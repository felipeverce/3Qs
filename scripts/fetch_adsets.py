"""
Meta Campaign Analyzer - Paso 4a: Obtener conjuntos de anuncios de una campaña

Edita ACCESS_TOKEN y CAMPAIGN_ID, luego ejecuta:
  python scripts/fetch_adsets.py

NOTA: Con presupuesto CBO (Advantage+), evalúa resultados a nivel de CAMPAÑA.
Con presupuesto por conjunto, evalúa a nivel de CONJUNTO.
"""

import sys
import requests

sys.stdout.reconfigure(encoding="utf-8")

# ══════════════════════════════════════════
# CONFIGURACIÓN - Edita estos valores
# ══════════════════════════════════════════
ACCESS_TOKEN = "TU_ACCESS_TOKEN_AQUI"
CAMPAIGN_ID  = "TU_CAMPAIGN_ID_AQUI"
DATE_PRESET  = "last_7d"  # Opciones: last_7d, last_14d, last_30d, last_90d, this_month, last_month
# ══════════════════════════════════════════

BASE_URL = "https://graph.facebook.com/v21.0"

INSIGHTS_FIELDS = ",".join([
    "impressions", "reach", "frequency", "spend", "cpm",
    "unique_clicks", "unique_ctr", "cost_per_unique_click",
    "outbound_clicks", "outbound_clicks_ctr", "cost_per_outbound_click",
    "actions", "action_values", "cost_per_action_type",
    "purchase_roas", "video_avg_time_watched_actions",
    "quality_ranking", "engagement_rate_ranking", "conversion_rate_ranking",
])

DELIVERY_ICONS = {
    "ACTIVE":           "🟢 Activo",
    "PAUSED":           "⏸️  Pausado",
    "CAMPAIGN_PAUSED":  "⏸️  Pausa (campaña)",
    "DELETED":          "🗑️  Eliminado",
    "ARCHIVED":         "📦 Archivado",
    "WITH_ISSUES":      "⚠️  Con problemas",
    "IN_PROCESS":       "⚙️  En proceso",
}

LEARNING_LABELS = {
    "LEARNING":          "📚 En aprendizaje  ← NO pausar (efecto desglose)",
    "LEARNING_LIMITED":  "⚠️  Aprendizaje limitado — necesita más conversiones",
    "LEARNING_COMPLETE": "✅ Aprendizaje completo",
    "DATA_COLLECTION":   "📊 Recolectando datos",
    "NOT_DELIVERING":    "🔴 Sin entrega",
}


# ── Helpers ────────────────────────────────────────────────────────

def fmt_money(val):
    try:    return f"${float(val):,.2f}"
    except: return "—"

def fmt_num(val, dec=0):
    try:
        return f"{float(val):,.{dec}f}" if dec else f"{int(float(val)):,}"
    except: return "—"

def get_action(lst, key):
    for item in (lst or []):
        if item.get("action_type") == key:
            return item.get("value")
    return None

def fmt_budget(adset):
    daily    = adset.get("daily_budget")
    lifetime = adset.get("lifetime_budget")
    if daily    and float(daily) > 0:    return f"${float(daily)/100:,.2f}/día"
    if lifetime and float(lifetime) > 0: return f"${float(lifetime)/100:,.2f} total"
    return "CBO (controlado por campaña)"


# ── API calls ──────────────────────────────────────────────────────

def get_campaign_info():
    r = requests.get(f"{BASE_URL}/{CAMPAIGN_ID}", params={
        "access_token": ACCESS_TOKEN,
        "fields": "id,name,objective,daily_budget,lifetime_budget",
    })
    r.raise_for_status()
    return r.json()

def get_adsets():
    r = requests.get(f"{BASE_URL}/{CAMPAIGN_ID}/adsets", params={
        "access_token": ACCESS_TOKEN,
        "fields": "id,name,status,effective_status,daily_budget,lifetime_budget,"
                  "budget_remaining,learning_stage_info,optimization_goal,bid_strategy",
        "limit": 100,
    })
    r.raise_for_status()
    return r.json().get("data", [])

def get_insights(adset_id):
    r = requests.get(f"{BASE_URL}/{adset_id}/insights", params={
        "access_token": ACCESS_TOKEN,
        "fields": INSIGHTS_FIELDS,
        "date_preset": DATE_PRESET,
        "level": "adset",
    })
    r.raise_for_status()
    data = r.json().get("data", [])
    return data[0] if data else {}


# ── Main ───────────────────────────────────────────────────────────

def main():
    print(f"\n🔍 Obteniendo conjuntos de anuncios...")
    print(f"📅 Periodo: {DATE_PRESET}\n")

    campaign = get_campaign_info()
    camp_name = campaign.get("name", "—")

    # Detectar si es CBO: tiene daily_budget o lifetime_budget a nivel campaña
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

    adsets = get_adsets()
    if not adsets:
        print("❌ No se encontraron conjuntos de anuncios.")
        return

    active = sum(1 for a in adsets if a.get("effective_status") == "ACTIVE")
    print(f"📦 {len(adsets)} conjunto(s) — {active} activo(s)\n")
    print("═" * 68)

    for i, adset in enumerate(adsets, 1):
        adset_id   = adset["id"]
        name       = adset.get("name", "Sin nombre")
        eff_status = adset.get("effective_status", adset.get("status", "UNKNOWN"))
        status_str = DELIVERY_ICONS.get(eff_status, f"❓ {eff_status}")
        budget_str = fmt_budget(adset)

        # Fase de aprendizaje
        learn_info = adset.get("learning_stage_info") or {}
        learn_st   = learn_info.get("status", "")
        learn_str  = LEARNING_LABELS.get(learn_st, "")

        print(f"\n  #{i}  {name}")
        print(f"       ID: {adset_id}")
        print(f"       Estado:      {status_str}")
        print(f"       Presupuesto: {budget_str}")
        if learn_str:
            print(f"       Aprendizaje: {learn_str}")

        # Insights
        ins = get_insights(adset_id)
        if not ins:
            print(f"\n       📊 Sin datos de insights para '{DATE_PRESET}'")
            continue

        spend       = ins.get("spend")
        impressions = ins.get("impressions")
        reach       = ins.get("reach")
        freq        = ins.get("frequency")
        cpm         = ins.get("cpm")
        actions     = ins.get("actions", [])
        cpa_list    = ins.get("cost_per_action_type", [])
        roas_data   = ins.get("purchase_roas", [])

        # Resultados según tipo
        purchases = get_action(actions, "purchase")
        leads     = get_action(actions, "lead")
        messages  = get_action(actions, "messaging_conversation_started_7d")

        cpa_purchase = get_action(cpa_list, "purchase")
        cpa_lead     = get_action(cpa_list, "lead")
        cpa_msg      = get_action(cpa_list, "messaging_conversation_started_7d")
        roas         = roas_data[0].get("value") if roas_data else None

        # Video
        video_view_3s  = get_action(actions, "video_view")
        video_avg_raw  = ins.get("video_avg_time_watched_actions", [])
        video_avg_val  = video_avg_raw[0].get("value") if video_avg_raw else None
        video_3s_rate  = (float(video_view_3s) / float(impressions) * 100
                          if video_view_3s and impressions and float(impressions) > 0 else None)

        # Calidad
        quality    = ins.get("quality_ranking", "")
        engagement = ins.get("engagement_rate_ranking", "")
        conversion = ins.get("conversion_rate_ranking", "")

        print(f"\n       📊 Métricas ({DATE_PRESET}):")
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
            if roas: print(f"          ROAS:               {fmt_num(roas, 2)}x")

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

    print(f"\n{'═' * 68}")
    print(f"\n✅ Análisis de conjuntos completado.")
    if is_cbo:
        print("⚠️  CBO activo: evalúa el éxito final a nivel de CAMPAÑA.")
    print()


if __name__ == "__main__":
    main()
