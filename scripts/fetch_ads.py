"""
Meta Campaign Analyzer - Paso 4b: Obtener anuncios de un conjunto

Edita ACCESS_TOKEN y ADSET_ID, luego ejecuta:
  python scripts/fetch_ads.py

IMPORTANTE - Efecto Desglose:
  Antes de pausar cualquier anuncio, lee la tabla de advertencias al final.
  Nunca pauses varios anuncios a la vez — un cambio a la vez.
"""

import sys
import requests

sys.stdout.reconfigure(encoding="utf-8")

# ══════════════════════════════════════════
# CONFIGURACIÓN - Edita estos valores
# ══════════════════════════════════════════
ACCESS_TOKEN = "TU_ACCESS_TOKEN_AQUI"
ADSET_ID     = "TU_ADSET_ID_AQUI"
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
    "ADSET_PAUSED":     "⏸️  Pausa (conjunto)",
    "DELETED":          "🗑️  Eliminado",
    "ARCHIVED":         "📦 Archivado",
    "DISAPPROVED":      "🚫 Desaprobado",
    "PENDING_REVIEW":   "🔍 En revisión",
    "WITH_ISSUES":      "⚠️  Con problemas",
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


# ── API calls ──────────────────────────────────────────────────────

def get_adset_info():
    r = requests.get(f"{BASE_URL}/{ADSET_ID}", params={
        "access_token": ACCESS_TOKEN,
        "fields": "id,name,status,effective_status,campaign_id,learning_stage_info,"
                  "optimization_goal,daily_budget,lifetime_budget",
    })
    r.raise_for_status()
    return r.json()

def get_ads():
    r = requests.get(f"{BASE_URL}/{ADSET_ID}/ads", params={
        "access_token": ACCESS_TOKEN,
        "fields": "id,name,status,effective_status,creative{id,name,object_type}",
        "limit": 100,
    })
    r.raise_for_status()
    return r.json().get("data", [])

def get_insights(ad_id):
    r = requests.get(f"{BASE_URL}/{ad_id}/insights", params={
        "access_token": ACCESS_TOKEN,
        "fields": INSIGHTS_FIELDS,
        "date_preset": DATE_PRESET,
        "level": "ad",
    })
    r.raise_for_status()
    data = r.json().get("data", [])
    return data[0] if data else {}


# ── Efecto desglose ────────────────────────────────────────────────

def desglose_warnings(ad, ad_status, spend, total_spend, active_count, days_active=None):
    """Evalúa si aplica advertencia de efecto desglose para este anuncio."""
    warnings = []

    # Regla 1: único anuncio activo
    if active_count == 1 and ad_status == "ACTIVE":
        warnings.append("🚫 Es el ÚNICO anuncio activo — pausarlo detiene toda la entrega del conjunto")

    # Regla 2: pocos días activo
    if days_active is not None and days_active < 7:
        warnings.append(f"⏳ Lleva solo {days_active} día(s) activo — espera 7 días para tener datos suficientes")

    # Regla 3: bajo gasto (Meta ya lo está depriorizando)
    if total_spend and total_spend > 0 and spend:
        pct = float(spend) / total_spend * 100
        if float(spend) > 0 and pct < 10:
            warnings.append(f"ℹ️  Gasto bajo ({pct:.1f}% del total) — Meta ya lo está depriorizando naturalmente")
        elif pct > 80:
            warnings.append(f"📌 Concentra el {pct:.1f}% del gasto — es el anuncio dominante del conjunto")

    return warnings


# ── Main ───────────────────────────────────────────────────────────

def main():
    print(f"\n🔍 Obteniendo anuncios del conjunto {ADSET_ID}...")
    print(f"📅 Periodo: {DATE_PRESET}\n")

    # Info del conjunto
    adset      = get_adset_info()
    adset_name = adset.get("name", "—")
    learn_info = adset.get("learning_stage_info") or {}
    learn_st   = learn_info.get("status", "")
    learn_str  = LEARNING_LABELS.get(learn_st, "")

    print(f"📦 Conjunto: {adset_name}")
    print(f"🎯 Optimización: {adset.get('optimization_goal', '—')}")
    if learn_str:
        print(f"📚 Aprendizaje: {learn_str}")

    # Obtener anuncios
    ads = get_ads()
    if not ads:
        print("\n❌ No se encontraron anuncios en este conjunto.")
        return

    active_count = sum(1 for a in ads if a.get("effective_status") == "ACTIVE")
    print(f"\n🎨 {len(ads)} anuncio(s) — {active_count} activo(s)\n")

    # Recolectar todos los insights primero (para calcular % de gasto)
    all_insights = {}
    total_spend  = 0.0
    for ad in ads:
        ins = get_insights(ad["id"])
        all_insights[ad["id"]] = ins
        sp = ins.get("spend")
        if sp:
            total_spend += float(sp)

    print("═" * 68)

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

        # Resultados
        purchases = get_action(actions, "purchase")
        leads     = get_action(actions, "lead")
        messages  = get_action(actions, "messaging_conversation_started_7d")

        cpa_purchase = get_action(cpa_list, "purchase")
        cpa_lead     = get_action(cpa_list, "lead")
        cpa_msg      = get_action(cpa_list, "messaging_conversation_started_7d")
        roas         = roas_data[0].get("value") if roas_data else None

        # Video
        video_view_3s = get_action(actions, "video_view")
        video_avg_raw = ins.get("video_avg_time_watched_actions", [])
        video_avg_val = video_avg_raw[0].get("value") if video_avg_raw else None
        video_3s_rate = (float(video_view_3s) / float(impressions) * 100
                         if video_view_3s and impressions and float(impressions) > 0 else None)

        # Clics salientes
        ob_clicks = ins.get("outbound_clicks", [{}])
        ob_val    = ob_clicks[0].get("value") if ob_clicks else None
        ob_ctr    = ins.get("outbound_clicks_ctr", [{}])
        ob_ctr_v  = ob_ctr[0].get("value") if ob_ctr else None

        # Calidad
        quality    = ins.get("quality_ranking", "")
        engagement = ins.get("engagement_rate_ranking", "")
        conversion = ins.get("conversion_rate_ranking", "")

        # % de gasto en el conjunto
        spend_pct = (float(spend) / total_spend * 100
                     if spend and total_spend > 0 else None)

        print(f"\n  #{i}  {ad_name}")
        print(f"       ID: {ad_id}")
        print(f"       Estado:         {status_str}")
        print(f"       Tipo creativo:  {creative_type}")

        if not ins:
            print(f"\n       📊 Sin datos de insights para '{DATE_PRESET}'")
        else:
            print(f"\n       📊 Métricas ({DATE_PRESET}):")
            print(f"          Importe gastado:    {fmt_money(spend)}", end="")
            if spend_pct is not None:
                print(f"  ({spend_pct:.1f}% del conjunto)", end="")
            print()
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

        # Advertencias de efecto desglose
        warnings = desglose_warnings(
            ad, eff_status, spend, total_spend, active_count
        )
        if warnings:
            print(f"\n       ⚡ Efecto Desglose:")
            for w in warnings:
                print(f"          {w}")

    print(f"\n{'═' * 68}")
    print(f"\n✅ Análisis de anuncios completado.")
    print(f"📌 Regla: Un cambio a la vez — no pauses varios anuncios simultáneamente.")
    if learn_st == "LEARNING":
        print(f"⚠️  Conjunto en aprendizaje — espera antes de hacer cualquier cambio.")
    print()


if __name__ == "__main__":
    main()
