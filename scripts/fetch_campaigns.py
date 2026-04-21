"""
Meta Campaign Analyzer - Paso 2: Obtener campañas de una cuenta de anuncios.

Uso:
  export META_ACCESS_TOKEN=EAA...
  export AD_ACCOUNT_ID=act_123456789
  python scripts/fetch_campaigns.py
"""

import json

from _common import STATUS_ICON, api_get, fmt_budget, load_config


def main():
    cfg = load_config(required=("META_ACCESS_TOKEN", "AD_ACCOUNT_ID"))
    token      = cfg["access_token"]
    account_id = cfg["ad_account_id"]

    print(f"\n📋 Obteniendo campañas de {account_id}...\n")

    campaigns = api_get(
        f"/{account_id}/campaigns",
        {
            "access_token": token,
            "fields": (
                "id,name,status,objective,daily_budget,lifetime_budget,"
                "budget_remaining,start_time,stop_time,created_time,updated_time,"
                "destination_type"
            ),
            "limit": 100,
        },
        paginate=True,
    )["data"]

    if not campaigns:
        print("  No se encontraron campañas.")
        return

    print(f"  Campañas encontradas: {len(campaigns)}\n")
    for i, c in enumerate(campaigns, 1):
        icon = STATUS_ICON.get(c["status"], "❓")
        print(f"  {icon} [{i}] {c['name']}")
        print(
            f"       ID: {c['id']} | Objetivo: {c.get('objective', '—')} | "
            f"Presupuesto: {fmt_budget(c)}"
        )

    filename = "campaigns.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(campaigns, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Datos guardados en: {filename}")
    print("\nPega el contenido de ese archivo en Claude para continuar.\n")


if __name__ == "__main__":
    main()
