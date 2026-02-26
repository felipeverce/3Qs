"""
Meta Campaign Analyzer - Paso 1: Obtener negocios y cuentas de anuncios

Edita ACCESS_TOKEN con tu token y ejecuta:
  pip install requests
  python scripts/fetch_businesses.py
"""

import sys
import requests
import json

sys.stdout.reconfigure(encoding="utf-8")

# ══════════════════════════════════════════
# CONFIGURACIÓN - Edita este valor
# ══════════════════════════════════════════
ACCESS_TOKEN = "TU_ACCESS_TOKEN_AQUI"
# ══════════════════════════════════════════

BASE_URL = "https://graph.facebook.com/v21.0"


def get_businesses():
    url = f"{BASE_URL}/me/businesses"
    params = {
        "access_token": ACCESS_TOKEN,
        "fields": "id,name",
        "limit": 100,
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json().get("data", [])


def get_ad_accounts():
    url = f"{BASE_URL}/me/adaccounts"
    params = {
        "access_token": ACCESS_TOKEN,
        "fields": "id,name,account_status,currency,business",
        "limit": 100,
    }
    r = requests.get(url, params=params)
    r.raise_for_status()
    return r.json().get("data", [])


def main():
    print("\n📋 Obteniendo perfiles de negocio...\n")

    result = {"businesses": [], "ad_accounts": []}

    # Negocios
    try:
        businesses = get_businesses()
        result["businesses"] = businesses
        if businesses:
            print(f"  Negocios encontrados: {len(businesses)}")
            for b in businesses:
                print(f"    → [{b['id']}] {b['name']}")
        else:
            print("  Sin negocios directos asociados al token.")
    except Exception as e:
        print(f"  No se pudieron obtener negocios: {e}")

    # Cuentas de anuncios — agrupa por negocio, excluye Read-Only
    print("\n📋 Obteniendo cuentas de anuncios...\n")
    try:
        all_accounts = get_ad_accounts()

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

        # Mostrar agrupadas
        for biz_name, accounts in by_business.items():
            # Separar propias (sin Read-Only) de accesos externos
            owned = [a for a in accounts if "(Read-Only)" not in a["name"]]
            readonly = [a for a in accounts if "(Read-Only)" in a["name"]]

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
    except Exception as e:
        print(f"  No se pudieron obtener cuentas: {e}")
        result["ad_accounts"] = []

    # Guardar
    filename = "businesses.json"
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"\n✅ Datos guardados en: {filename}")
    print("\nPega el contenido de ese archivo en Claude para continuar.\n")


if __name__ == "__main__":
    main()
