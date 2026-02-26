"""
Meta Campaign Analyzer - Paso 3: Obtener insights de una campaña

Edita ACCESS_TOKEN y CAMPAIGN_ID, luego ejecuta:
  python scripts/fetch_insights.py
"""

import sys
import requests
import json
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8")

# ══════════════════════════════════════════
# CONFIGURACIÓN - Edita estos valores
# ══════════════════════════════════════════
ACCESS_TOKEN = "TU_ACCESS_TOKEN_AQUI"
CAMPAIGN_ID  = "TU_CAMPAIGN_ID_AQUI"
DATE_PRESET  = "last_30d"  # Opciones: last_7d, last_14d, last_30d, last_90d, this_month, last_month
# ══════════════════════════════════════════

BASE_URL = "https://graph.facebook.com/v21.0"

INSIGHTS_FIELDS = ",".join([
    # Entrega y alcance
    "impressions",
    "reach",
    "frequency",
    "spend",
    "cpm",
    # Clics únicos
    "unique_clicks",
    "unique_ctr",
    "cost_per_unique_click",
    # Clics salientes
    "outbound_clicks",
    "outbound_clicks_ctr",
    "cost_per_outbound_click",
    # Acciones y conversiones
    "actions",
    "action_values",
    "cost_per_action_type",
    # ROAS
    "purchase_roas",
    # Video (video_view en actions = reproducciones 3 segundos)
    "video_avg_time_watched_actions",
    # Calidad
    "quality_ranking",
    "engagement_rate_ranking",
    "conversion_rate_ranking",
])

# Mapeo de objetivo Meta → tipo interno
OBJECTIVE_MAP = {
    # Ventas
    "OUTCOME_SALES":           "ventas",
    "CONVERSIONS":             "ventas",
    "PRODUCT_CATALOG_SALES":   "ventas",
    # Interacción / Mensajes
    "OUTCOME_ENGAGEMENT":      "interaccion",
    "MESSAGES":                "interaccion",
    "POST_ENGAGEMENT":         "interaccion",
    "PAGE_LIKES":              "interaccion",
    "EVENT_RESPONSES":         "interaccion",
    # Leads (se distinguen más abajo por destination_type)
    "OUTCOME_LEADS":           "cp_formularios",
    "LEAD_GENERATION":         "cp_formularios",
    # Tiendas / Reconocimiento
    "OUTCOME_STORE_TRAFFIC":   "tiendas_fisicas",
    "LOCAL_AWARENESS":         "tiendas_fisicas",
    "OUTCOME_AWARENESS":       "tiendas_fisicas",
    "REACH":                   "tiendas_fisicas",
    "BRAND_AWARENESS":         "tiendas_fisicas",
}

# Destination types que indican sitio web (para campañas de leads)
WEBSITE_DESTINATION_TYPES = {"WEBSITE", "ON_POST", "MESSENGER", "INSTAGRAM_DIRECT"}


def get_campaign_info():
    url = f"{BASE_URL}/{CAMPAIGN_ID}"
    params = {
        "access_token": ACCESS_TOKEN,
        "fields": "id,name,status,objective,daily_budget,lifetime_budget,budget_remaining,created_time,updated_time",
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json()


def get_insights():
    url = f"{BASE_URL}/{CAMPAIGN_ID}/insights"
    params = {
        "access_token": ACCESS_TOKEN,
        "fields": INSIGHTS_FIELDS,
        "date_preset": DATE_PRESET,
        "level": "campaign",
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    data = r.json().get("data", [])
    return data[0] if data else {}


def detect_campaign_type(campaign):
    objective        = campaign.get("objective", "").upper()
    destination_type = campaign.get("destination_type", "").upper()

    campaign_type = OBJECTIVE_MAP.get(objective, "desconocido")

    # Distinguir leads por formulario vs sitio web
    if campaign_type == "cp_formularios" and destination_type in WEBSITE_DESTINATION_TYPES:
        campaign_type = "cp_sitio_web"

    return campaign_type


def main():
    print(f"\n🔍 Obteniendo datos de campaña {CAMPAIGN_ID} ({DATE_PRESET})...\n")

    campaign = get_campaign_info()
    campaign_type = detect_campaign_type(campaign)

    print(f"  Campaña   : {campaign.get('name')}")
    print(f"  Objetivo  : {campaign.get('objective')}")
    print(f"  Estado    : {campaign.get('status')}")
    print(f"  Tipo      : {campaign_type}")

    print(f"\n  Obteniendo insights...")
    insights = get_insights()

    if not insights:
        print("  ⚠️  Sin datos de insights para este periodo.")

    result = {
        "campaign":      campaign,
        "campaign_type": campaign_type,
        "date_preset":   DATE_PRESET,
        "insights":      insights,
    }

    filename = f"insights_{CAMPAIGN_ID}_{DATE_PRESET}_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Datos guardados en: {filename}")
    print("\nPega el contenido de ese archivo en Claude para el análisis.\n")


if __name__ == "__main__":
    main()
