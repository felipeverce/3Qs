"""
Meta Campaign Analyzer - Paso 3: Obtener insights de una campaña.

Uso:
  export META_ACCESS_TOKEN=EAA...
  export CAMPAIGN_ID=123456789
  export DATE_PRESET=last_30d   # opcional
  python scripts/fetch_insights.py
"""

import json
from datetime import datetime

from _common import INSIGHTS_FIELDS, api_get, load_config

# Mapeo de objetivo Meta → tipo interno
OBJECTIVE_MAP = {
    # Ventas
    "OUTCOME_SALES":           "ventas",
    "CONVERSIONS":             "ventas",
    "PRODUCT_CATALOG_SALES":   "ventas",
    # Interacción / Mensajes / Tráfico
    "OUTCOME_ENGAGEMENT":      "interaccion",
    "OUTCOME_TRAFFIC":         "interaccion",
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

# Solo "WEBSITE" califica como destino de sitio web para leads.
# MESSENGER / INSTAGRAM_DIRECT son destinos de chat, no sitio web.
WEBSITE_DESTINATION_TYPES = {"WEBSITE"}


def get_campaign_info(campaign_id, token):
    return api_get(
        f"/{campaign_id}",
        {
            "access_token": token,
            "fields": (
                "id,name,status,objective,daily_budget,lifetime_budget,"
                "budget_remaining,created_time,updated_time"
            ),
        },
    )


def get_first_adset_destination(campaign_id, token):
    """Fallback: destination_type suele ser más confiable a nivel adset."""
    try:
        data = api_get(
            f"/{campaign_id}/adsets",
            {
                "access_token": token,
                "fields": "destination_type",
                "limit": 1,
            },
        ).get("data", [])
        if data:
            return (data[0].get("destination_type") or "").upper()
    except SystemExit:
        raise
    except Exception:
        pass
    return ""


def get_insights(campaign_id, token, date_preset):
    data = api_get(
        f"/{campaign_id}/insights",
        {
            "access_token": token,
            "fields": INSIGHTS_FIELDS,
            "date_preset": date_preset,
            "level": "campaign",
        },
    ).get("data", [])
    return data[0] if data else {}


def detect_campaign_type(campaign, fallback_destination=""):
    objective        = (campaign.get("objective") or "").upper()
    destination_type = (campaign.get("destination_type") or fallback_destination or "").upper()

    campaign_type = OBJECTIVE_MAP.get(objective, "desconocido")

    # Distinguir leads por formulario vs sitio web
    if campaign_type == "cp_formularios" and destination_type in WEBSITE_DESTINATION_TYPES:
        campaign_type = "cp_sitio_web"

    return campaign_type, destination_type


def main():
    cfg = load_config(required=("META_ACCESS_TOKEN", "CAMPAIGN_ID"))
    token       = cfg["access_token"]
    campaign_id = cfg["campaign_id"]
    date_preset = cfg["date_preset"] or "last_30d"

    print(f"\n🔍 Obteniendo datos de campaña {campaign_id} ({date_preset})...\n")

    campaign = get_campaign_info(campaign_id, token)

    # destination_type no es un campo válido a nivel campaña en Graph API v21.0 (error 100).
    # Solo existe a nivel adset. Consultarlo únicamente si el objetivo sugiere leads,
    # donde hace falta distinguir formulario instantáneo vs sitio web externo.
    base_type = OBJECTIVE_MAP.get((campaign.get("objective") or "").upper(), "desconocido")
    fallback_dest = ""
    if base_type == "cp_formularios":
        fallback_dest = get_first_adset_destination(campaign_id, token)

    campaign_type, destination_type = detect_campaign_type(campaign, fallback_dest)

    print(f"  Campaña         : {campaign.get('name')}")
    print(f"  Objetivo        : {campaign.get('objective')}")
    print(f"  Destino         : {destination_type or '—'}")
    print(f"  Estado          : {campaign.get('status')}")
    print(f"  Tipo detectado  : {campaign_type}")

    print(f"\n  Obteniendo insights...")
    insights = get_insights(campaign_id, token, date_preset)

    if not insights:
        print(f"  ⚠️  Sin datos de insights para este periodo ({date_preset}).")

    result = {
        "campaign":         campaign,
        "campaign_type":    campaign_type,
        "destination_type": destination_type,
        "date_preset":      date_preset,
        "insights":         insights,
    }

    filename = f"insights_{campaign_id}_{date_preset}_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Datos guardados en: {filename}")
    print("\nPega el contenido de ese archivo en Claude para el análisis.\n")


if __name__ == "__main__":
    main()
