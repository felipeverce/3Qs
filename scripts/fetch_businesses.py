"""
Meta Campaign Analyzer - Paso 1: Obtener negocios y cuentas de anuncios.

Uso:
  export META_ACCESS_TOKEN=EAA...
  python scripts/fetch_businesses.py

(o crea un archivo .env en la raíz del proyecto con META_ACCESS_TOKEN=...)
"""

import json

from _common import api_get, load_config


def main():
    cfg = load_config()
    token = cfg["access_token"]

    print("\n📋 Obteniendo perfiles de negocio...\n")

    result = {"businesses": [], "ad_accounts": []}

    # Negocios
    try:
        businesses = api_get(
            "/me/businesses",
            {"access_token": token, "fields": "id,name", "limit": 100},
            paginate=True,
        )["data"]
        result["businesses"] = businesses
        if businesses:
            print(f"  Negocios encontrados: {len(businesses)}")
            for b in businesses:
                print(f"    → [{b['id']}] {b['name']}")
        else:
            print("  Sin negocios directos asociados al token.")
    except SystemExit:
        raise
    except Exception as e:
        print(f"  No se pudieron obtener negocios: {e}")

    # Cuentas de anuncios
    print("\n📋 Obteniendo cuentas de anuncios...\n")
    try:
        all_accounts = api_get(
            "/me/adaccounts",
            {
                "access_token": token,
                "fields": "id,name,account_status,currency,business",
                "limit": 100,
            },
            paginate=True,
        )["data"]

        # Agrupar por negocio
        by_business = {}
        standalone = []
        for a in all_accounts:
            biz = a.get("business")
            if biz:
                biz_name = biz.get("name", "—")
                by_business.setdefault(biz_name, []).append(a)
            else:
                standalone.append(a)

        for biz_name, accounts in by_business.items():
            owned    = [a for a in accounts if "(Read-Only)" not in a["name"]]
            readonly = [a for a in accounts if "(Read-Only)"     in a["name"]]

            print(f"  [{biz_name}]")
            for a in owned:
                status = "✅ Activa" if a.get("account_status") == 1 else "⚠️ Inactiva"
                print(f"    → [{a['id']}] {a['name']} | {status}  ← PROPIA")
            for a in readonly:
                status = "✅ Activa" if a.get("account_status") == 1 else "⚠️ Inactiva"
                print(f"    → [{a['id']}] {a['name']} | {status}")

        if standalone:
            print("\n  [Sin negocio asignado]")
            for a in standalone:
                status = "✅ Activa" if a.get("account_status") == 1 else "⚠️ Inactiva"
                print(f"    → [{a['id']}] {a['name']} | {status}")

        result["ad_accounts"] = all_accounts
    except SystemExit:
        raise
    except Exception as e:
        print(f"  No se pudieron obtener cuentas: {e}")
        result["ad_accounts"] = []

    filename = "businesses.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Datos guardados en: {filename}")
    print("\nPega el contenido de ese archivo en Claude para continuar.\n")


if __name__ == "__main__":
    main()
