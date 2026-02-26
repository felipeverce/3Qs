"""
Meta Campaign Analyzer - Paso 2: Obtener campañas de una cuenta de anuncios

Edita ACCESS_TOKEN y AD_ACCOUNT_ID, luego ejecuta:
  python scripts/fetch_campaigns.py
"""

import sys
import requests
import json

sys.stdout.reconfigure(encoding="utf-8")

# ══════════════════════════════════════════
# CONFIGURACIÓN - Edita estos valores
# ══════════════════════════════════════════
ACCESS_TOKEN  = "TU_ACCESS_TOKEN_AQUI"
AD_ACCOUNT_ID = "TU_AD_ACCOUNT_ID_AQUI"
# ══════════════════════════════════════════

BASE_URL = "https://graph.facebook.com/v21.0"

STATUS_ICON = {
    "ACTIVE":   "🟢",
    "PAUSED":   "🔴",
    "ARCHIVED": "⚫",
    "DELETED":  "⚫",
}


def get_campaigns():
    url = f"{BASE_URL}/{AD_ACCOUNT_ID}/campaigns"
    params = {
        "access_token": ACCESS_TOKEN,
        "fields": "id,name,status,objective,daily_budget,lifetime_budget,budget_remaining,start_time,stop_time,created_time,updated_time,destination_type",
        "limit": 100,
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json().get("data", [])


def main():
    print(f"\n📋 Obteniendo campañas de {AD_ACCOUNT_ID}...\n")

    campaigns = get_campaigns()

    if not campaigns:
        print("  No se encontraron campañas.")
        return

    print(f"  Campañas encontradas: {len(campaigns)}\n")
    for i, c in enumerate(campaigns, 1):
        icon = STATUS_ICON.get(c["status"], "❓")
        budget = c.get("daily_budget") or c.get("lifetime_budget") or "—"
        print(f"  {icon} [{i}] {c['name']}")
        print(f"       ID: {c['id']} | Objetivo: {c.get('objective', '—')} | Presupuesto: {budget}")

    filename = "campaigns.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(campaigns, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Datos guardados en: {filename}")
    print("\nPega el contenido de ese archivo en Claude para continuar.\n")


if __name__ == "__main__":
    main()
