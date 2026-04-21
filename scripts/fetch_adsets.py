"""
Meta Campaign Analyzer - Paso 4a: Conjuntos de anuncios de una campaña.

Uso:
  export META_ACCESS_TOKEN=EAA...
  export CAMPAIGN_ID=123456789
  export DATE_PRESET=last_7d   # opcional
  python scripts/fetch_adsets.py

NOTA: Con presupuesto CBO (Advantage+), evalúa resultados a nivel de CAMPAÑA.
Con presupuesto por conjunto, evalúa a nivel de CONJUNTO.
"""

import json

from _common import (
    DELIVERY_ICONS,
    INSIGHTS_FIELDS,
    LEARNING_LABELS,
    api_get,
    fmt_budget,
    fmt_money,
    fmt_num,
    get_action,
    load_config,
)


def get_campaign_info(campaign_id, token):
    return api_get(f"/{campaign_id}", {
        "access_token": token,
        "fields": "id,name,objective,daily_budget,lifetime_budget",
    })


def get_adsets(campaign_id, token):
    return api_get(
        f"/{campaign_id}/adsets",
        {
            "access_token": token,
            "fields": (
                "id,name,status,effective_status,daily_budget,lifetime_budget,"
                "budget_remaining,learning_stage_info,optimization_goal,bid_strategy,"
                "destination_type"
            ),
            "limit": 100,
        },
        paginate=True,
    )["data"]


def get_insights(adset_id, token, date_preset):
    data = api_get(
        f"/{adset_id}/insights",
        {
            "access_token": token,
            "fields": INSIGHTS_FIELDS,
            "date_preset": date_preset,
            "level": "adset",
        },
    ).get("data", [])
    return data[0] if data else {}


def main():
    cfg = load_config(required=("META_ACCESS_TOKEN", "CAMPAIGN_ID"))
    token       = cfg["access_token"]
    campaign_id = cfg["campaign_id"]
    date_preset = cfg["date_preset"] or "last_7d"

    print(f"\n🔍 Obteniendo conjuntos de anuncios...")
    print(f"📅 Periodo: {date_preset}\n")

    campaign = get_campaign_info(campaign_id, token)
    camp_name = campaign.get("name", "—")

    # CBO: budget a nivel campaña
    is_cbo = bool(campaign.get("daily_budget") or campaign.get("lifetime_budget"))

    print(f"📣 Campaña: {camp_name}")
    print(f"🎯 Objetivo: {campaign.get('objective', '—')}")

    if is_cbo:
        print("\n⚠️  PRESUPUESTO CBO (Advantage+) DETECTADO")
        print("   → Evalúa el éxito a nivel de CAMPAÑA completa.")
        print("   → No tomes decisiones de pausa/escala basándote solo en métricas por conjunto.")
    else:
        print("\nℹ️  Presupuesto por conjunto — evalúa a nivel de CONJUNTO DE ANUNCIOS.")

    print()

    adsets = get_adsets(campaign_id, token)
    if not adsets:
        print("❌ No se encontraron conjuntos de anuncios.")
        return

    active = sum(1 for a in adsets if a.get("effective_status") == "ACTIVE")
    print(f"📦 {len(adsets)} conjunto(s) — {active} activo(s)\n")
    print("═" * 68)

    enriched = []

    for i, adset in enumerate(adsets, 1):
        adset_id   = adset["id"]
        name       = adset.get("name", "Sin nombre")
        eff_status = adset.get("effective_status", adset.get("status", "UNKNOWN"))
        status_str = DELIVERY_ICONS.get(eff_status, f"❓ {eff_status}")
        budget_str = fmt_budget(adset) if not is_cbo else "CBO (controlado por campaña)"

        learn_info = adset.get("learning_stage_info") or {}
        learn_st   = learn_info.get("status", "")
        learn_str  = LEARNING_LABELS.get(learn_st, "")

        print(f"\n  #{i}  {name}")
        print(f"       ID: {adset_id}")
        print(f"       Estado:      {status_str}")
        print(f"       Presupuesto: {budget_str}")
        if learn_str:
            print(f"       Aprendizaje: {learn_str}")

        ins = get_insights(adset_id, token, date_preset)
        adset_record = dict(adset)
        adset_record["insights"] = ins
        enriched.append(adset_record)

        if not ins:
            print(f"\n       📊 Sin datos de insights para '{date_preset}'")
            continue

        spend       = ins.get("spend")
        impressions = ins.get("impressions")
        reach       = ins.get("reach")
        freq        = ins.get("frequency")
        cpm         = ins.get("cpm")
        actions     = ins.get("actions", [])
        cpa_list    = ins.get("cost_per_action_type", [])
        roas_data   = ins.get("purchase_roas", [])

        purchases = get_action(actions, "purchase")
        leads     = get_action(actions, "lead")
        messages  = get_action(actions, "messaging_conversation_started_7d")

        cpa_purchase = get_action(cpa_list, "purchase")
        cpa_lead     = get_action(cpa_list, "lead")
        cpa_msg      = get_action(cpa_list, "messaging_conversation_started_7d")
        roas         = roas_data[0].get("value") if roas_data else None

        video_view_3s = get_action(actions, "video_view")
        video_avg_raw = ins.get("video_avg_time_watched_actions", [])
        video_avg_val = video_avg_raw[0].get("value") if video_avg_raw else None
        video_3s_rate = (
            float(video_view_3s) / float(impressions) * 100
            if video_view_3s and impressions and float(impressions) > 0
            else None
        )

        quality    = ins.get("quality_ranking", "")
        engagement = ins.get("engagement_rate_ranking", "")
        conversion = ins.get("conversion_rate_ranking", "")

        print(f"\n       📊 Métricas ({date_preset}):")
        print(f"          Importe gastado:   {fmt_money(spend)}")
        print(f"          Alcance:           {fmt_num(reach)}")
        print(f"          Impresiones:       {fmt_num(impressions)}")
        print(f"          Frecuencia:        {fmt_num(freq, 2)}")
        print(f"          CPM:               {fmt_money(cpm)}")

        if video_3s_rate is not None:
            print(f"          % Video 3s:        {video_3s_rate:.2f}%")
        if video_avg_val:
            print(f"          Tiempo prom. video: {fmt_num(video_avg_val, 1)}s")

        if purchases:
            print(f"\n          🛒 Compras:          {fmt_num(purchases)}")
            print(f"          Costo/compra:       {fmt_money(cpa_purchase)}")
            if roas:
                print(f"          ROAS:               {fmt_num(roas, 2)}x")

        if leads:
            print(f"\n          📋 Leads:            {fmt_num(leads)}")
            print(f"          Costo/lead:         {fmt_money(cpa_lead)}")

        if messages:
            print(f"\n          💬 Conversaciones:   {fmt_num(messages)}")
            print(f"          Costo/conv.:        {fmt_money(cpa_msg)}")

        if quality:
            print(f"\n          📈 Calidad:          {quality}")
            print(f"          Interacción:        {engagement}")
            print(f"          Conversión:         {conversion}")

    # Volcar JSON para pegar en Claude
    filename = f"adsets_{campaign_id}.json"
    payload = {
        "campaign_id":  campaign_id,
        "campaign":     campaign,
        "is_cbo":       is_cbo,
        "date_preset":  date_preset,
        "adsets":       enriched,
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"\n{'═' * 68}")
    print(f"\n✅ Análisis de conjuntos completado.")
    print(f"💾 Datos guardados en: {filename}")
    if is_cbo:
        print("⚠️  CBO activo: evalúa el éxito final a nivel de CAMPAÑA.")
    print("\nPega el contenido del JSON en Claude para profundizar el análisis.\n")


if __name__ == "__main__":
    main()
