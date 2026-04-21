"""
Meta Campaign Analyzer - Paso 4b: Anuncios de un conjunto.

Uso:
  export META_ACCESS_TOKEN=EAA...
  export ADSET_ID=123456789
  export DATE_PRESET=last_7d   # opcional
  python scripts/fetch_ads.py

IMPORTANTE - Efecto Desglose:
  Antes de pausar cualquier anuncio, lee las advertencias que imprime el script.
  Nunca pauses varios anuncios a la vez — un cambio a la vez.
"""

import json

from _common import (
    DELIVERY_ICONS,
    INSIGHTS_FIELDS,
    LEARNING_LABELS,
    api_get,
    fmt_money,
    fmt_num,
    get_action,
    load_config,
)


def get_adset_info(adset_id, token):
    return api_get(f"/{adset_id}", {
        "access_token": token,
        "fields": (
            "id,name,status,effective_status,campaign_id,learning_stage_info,"
            "optimization_goal,daily_budget,lifetime_budget"
        ),
    })


def get_ads(adset_id, token):
    return api_get(
        f"/{adset_id}/ads",
        {
            "access_token": token,
            "fields": "id,name,status,effective_status,creative{id,name,object_type}",
            "limit": 100,
        },
        paginate=True,
    )["data"]


def get_insights(ad_id, token, date_preset):
    data = api_get(
        f"/{ad_id}/insights",
        {
            "access_token": token,
            "fields": INSIGHTS_FIELDS,
            "date_preset": date_preset,
            "level": "ad",
        },
    ).get("data", [])
    return data[0] if data else {}


def desglose_warnings(ad_status, spend, total_spend, active_count, days_active=None):
    """Reglas del efecto desglose para este anuncio."""
    warnings = []

    if active_count == 1 and ad_status == "ACTIVE":
        warnings.append(
            "🚫 Es el ÚNICO anuncio activo — pausarlo detiene toda la entrega del conjunto"
        )

    if days_active is not None and days_active < 7:
        warnings.append(
            f"⏳ Lleva solo {days_active} día(s) activo — espera 7 días para tener datos"
        )

    if total_spend and total_spend > 0 and spend:
        pct = float(spend) / total_spend * 100
        if float(spend) > 0 and pct < 10:
            warnings.append(
                f"ℹ️  Gasto bajo ({pct:.1f}% del total) — Meta ya lo está depriorizando naturalmente"
            )
        elif pct > 80:
            warnings.append(
                f"📌 Concentra el {pct:.1f}% del gasto — es el anuncio dominante del conjunto"
            )

    return warnings


def main():
    cfg = load_config(required=("META_ACCESS_TOKEN", "ADSET_ID"))
    token       = cfg["access_token"]
    adset_id    = cfg["adset_id"]
    date_preset = cfg["date_preset"] if cfg["date_preset"] != "last_30d" else "last_7d"

    print(f"\n🔍 Obteniendo anuncios del conjunto {adset_id}...")
    print(f"📅 Periodo: {date_preset}\n")

    adset      = get_adset_info(adset_id, token)
    adset_name = adset.get("name", "—")
    learn_info = adset.get("learning_stage_info") or {}
    learn_st   = learn_info.get("status", "")
    learn_str  = LEARNING_LABELS.get(learn_st, "")

    print(f"📦 Conjunto: {adset_name}")
    print(f"🎯 Optimización: {adset.get('optimization_goal', '—')}")
    if learn_str:
        print(f"📚 Aprendizaje: {learn_str}")

    ads = get_ads(adset_id, token)
    if not ads:
        print("\n❌ No se encontraron anuncios en este conjunto.")
        return

    active_count = sum(1 for a in ads if a.get("effective_status") == "ACTIVE")
    print(f"\n🎨 {len(ads)} anuncio(s) — {active_count} activo(s)\n")

    # Recolectar insights para calcular % de gasto
    all_insights = {}
    total_spend = 0.0
    for ad in ads:
        ins = get_insights(ad["id"], token, date_preset)
        all_insights[ad["id"]] = ins
        sp = ins.get("spend")
        if sp:
            total_spend += float(sp)

    print("═" * 68)

    enriched = []

    for i, ad in enumerate(ads, 1):
        ad_id      = ad["id"]
        ad_name    = ad.get("name", "Sin nombre")
        eff_status = ad.get("effective_status", ad.get("status", "UNKNOWN"))
        status_str = DELIVERY_ICONS.get(eff_status, f"❓ {eff_status}")

        creative      = ad.get("creative") or {}
        creative_type = creative.get("object_type", "—")

        ins = all_insights.get(ad_id, {})

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

        ob_clicks = ins.get("outbound_clicks", [{}])
        ob_val    = ob_clicks[0].get("value") if ob_clicks else None
        ob_ctr    = ins.get("outbound_clicks_ctr", [{}])
        ob_ctr_v  = ob_ctr[0].get("value") if ob_ctr else None

        quality    = ins.get("quality_ranking", "")
        engagement = ins.get("engagement_rate_ranking", "")
        conversion = ins.get("conversion_rate_ranking", "")

        spend_pct = (
            float(spend) / total_spend * 100
            if spend and total_spend > 0
            else None
        )

        warnings = desglose_warnings(eff_status, spend, total_spend, active_count)

        ad_record = dict(ad)
        ad_record["insights"]            = ins
        ad_record["spend_pct_of_adset"]  = spend_pct
        ad_record["desglose_warnings"]   = warnings
        enriched.append(ad_record)

        print(f"\n  #{i}  {ad_name}")
        print(f"       ID: {ad_id}")
        print(f"       Estado:         {status_str}")
        print(f"       Tipo creativo:  {creative_type}")

        if not ins:
            print(f"\n       📊 Sin datos de insights para '{date_preset}'")
        else:
            print(f"\n       📊 Métricas ({date_preset}):")
            line = f"          Importe gastado:    {fmt_money(spend)}"
            if spend_pct is not None:
                line += f"  ({spend_pct:.1f}% del conjunto)"
            print(line)
            print(f"          Alcance:            {fmt_num(reach)}")
            print(f"          Impresiones:        {fmt_num(impressions)}")
            print(f"          Frecuencia:         {fmt_num(freq, 2)}")
            print(f"          CPM:                {fmt_money(cpm)}")

            if ob_val:
                print(f"          Clics salientes:    {fmt_num(ob_val)}")
            if ob_ctr_v:
                print(f"          CTR saliente:       {fmt_num(ob_ctr_v, 2)}%")

            if video_3s_rate is not None:
                print(f"          % Video 3s:         {video_3s_rate:.2f}%")
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

        if warnings:
            print(f"\n       ⚡ Efecto Desglose:")
            for w in warnings:
                print(f"          {w}")

    filename = f"ads_{adset_id}.json"
    payload = {
        "adset_id":      adset_id,
        "adset":         adset,
        "date_preset":   date_preset,
        "total_spend":   total_spend,
        "active_count":  active_count,
        "ads":           enriched,
    }
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)

    print(f"\n{'═' * 68}")
    print(f"\n✅ Análisis de anuncios completado.")
    print(f"💾 Datos guardados en: {filename}")
    print(f"📌 Regla: Un cambio a la vez — no pauses varios anuncios simultáneamente.")
    if learn_st == "LEARNING":
        print(f"⚠️  Conjunto en aprendizaje — espera antes de hacer cualquier cambio.")
    print("\nPega el contenido del JSON en Claude para el análisis detallado.\n")


if __name__ == "__main__":
    main()
