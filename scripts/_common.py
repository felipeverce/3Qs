"""
Módulo compartido para los scripts de Meta Campaign Analyzer.

Carga credenciales desde variables de entorno o un archivo .env en la raíz
del proyecto (o en el directorio actual). Expone los helpers, constantes y
un `api_get()` con paginación y reintentos ante rate limits.

Variables de entorno soportadas:
  META_ACCESS_TOKEN   (requerida)
  AD_ACCOUNT_ID       (opcional — fetch_campaigns)
  CAMPAIGN_ID         (opcional — fetch_insights, fetch_adsets)
  ADSET_ID            (opcional — fetch_ads)
  DATE_PRESET         (opcional — por defecto last_30d)
"""

import os
import sys
import time
from pathlib import Path

try:
    import requests
except ImportError:
    print("\n❌ Falta la librería `requests`.")
    print("   → Instálala con:  pip install requests\n")
    sys.exit(1)

# Asegura salida UTF-8 en Windows
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass


# ── Constantes ─────────────────────────────────────────────────────
BASE_URL = "https://graph.facebook.com/v21.0"

INSIGHTS_FIELDS = ",".join([
    # Entrega y alcance
    "impressions", "reach", "frequency", "spend", "cpm",
    # Clics únicos
    "unique_clicks", "unique_ctr", "cost_per_unique_click",
    # Clics salientes
    "outbound_clicks", "outbound_clicks_ctr", "cost_per_outbound_click",
    # Acciones y conversiones
    "actions", "action_values", "cost_per_action_type",
    # ROAS
    "purchase_roas",
    # Video (video_view en actions = reproducciones 3 segundos)
    "video_avg_time_watched_actions",
    # Calidad
    "quality_ranking", "engagement_rate_ranking", "conversion_rate_ranking",
])

STATUS_ICON = {
    "ACTIVE":   "🟢",
    "PAUSED":   "🔴",
    "ARCHIVED": "⚫",
    "DELETED":  "⚫",
}

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
    "IN_PROCESS":       "⚙️  En proceso",
}

LEARNING_LABELS = {
    "LEARNING":          "📚 En aprendizaje  ← NO pausar (efecto desglose)",
    "LEARNING_LIMITED":  "⚠️  Aprendizaje limitado — necesita más conversiones",
    "LEARNING_COMPLETE": "✅ Aprendizaje completo",
    "DATA_COLLECTION":   "📊 Recolectando datos",
    "NOT_DELIVERING":    "🔴 Sin entrega",
}

# Rate limit / permisos / token — códigos Meta
RATE_LIMIT_CODES  = {4, 17, 32, 613}
TOKEN_EXPIRED     = 190
PERMISSIONS_ERROR = 200


# ── Configuración ──────────────────────────────────────────────────
def _load_dotenv():
    """Parser mínimo de .env (sin dependencias). Busca en CWD y raíz del repo."""
    candidates = [
        Path.cwd() / ".env",
        Path(__file__).resolve().parent.parent / ".env",
    ]
    for path in candidates:
        if not path.exists():
            continue
        for raw in path.read_text(encoding="utf-8").splitlines():
            line = raw.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, val = line.split("=", 1)
            key = key.strip()
            val = val.strip().strip('"').strip("'")
            os.environ.setdefault(key, val)
        return


def load_config(required=("META_ACCESS_TOKEN",)):
    """Carga credenciales desde env (o .env). Aborta si falta algún requerido."""
    _load_dotenv()
    missing = [k for k in required if not os.environ.get(k)]
    if missing:
        print(f"\n❌ Falta(n) variable(s) de entorno: {', '.join(missing)}")
        print("   → Expórtalas (`export META_ACCESS_TOKEN=...`) o crea un archivo .env con:")
        for k in missing:
            print(f"       {k}=tu_valor")
        print()
        sys.exit(1)
    return {
        "access_token": os.environ.get("META_ACCESS_TOKEN", ""),
        "ad_account_id": os.environ.get("AD_ACCOUNT_ID", ""),
        "campaign_id":   os.environ.get("CAMPAIGN_ID", ""),
        "adset_id":      os.environ.get("ADSET_ID", ""),
        "date_preset":   os.environ.get("DATE_PRESET", "last_30d"),
    }


# ── Formateo ───────────────────────────────────────────────────────
def fmt_money(val):
    try:    return f"${float(val):,.2f}"
    except: return "—"


def fmt_num(val, dec=0):
    try:
        return f"{float(val):,.{dec}f}" if dec else f"{int(float(val)):,}"
    except:
        return "—"


def fmt_budget(obj):
    """Formatea daily_budget / lifetime_budget de Meta (valores en subunidades)."""
    daily    = obj.get("daily_budget")
    lifetime = obj.get("lifetime_budget")
    try:
        if daily and float(daily) > 0:
            return f"${float(daily)/100:,.2f}/día"
        if lifetime and float(lifetime) > 0:
            return f"${float(lifetime)/100:,.2f} total"
    except (TypeError, ValueError):
        pass
    return "—"


def get_action(lst, key):
    """Busca un action_type en una lista de acciones de Meta."""
    for item in (lst or []):
        if item.get("action_type") == key:
            return item.get("value")
    return None


# ── API ────────────────────────────────────────────────────────────
def _error_code(response):
    try:
        return response.json().get("error", {}).get("code")
    except Exception:
        return None


def _handle_api_error(response):
    code = _error_code(response)
    if code == TOKEN_EXPIRED:
        print("\n❌ El Access Token expiró o es inválido (code 190).")
        print("   → Genera uno nuevo en https://developers.facebook.com/tools/explorer/")
        sys.exit(1)
    if code == PERMISSIONS_ERROR:
        print("\n❌ Permisos insuficientes (code 200).")
        print("   → El token necesita (solo-lectura): ads_read, business_management")
        sys.exit(1)
    try:
        response.raise_for_status()
    except requests.HTTPError as e:
        err = {}
        try:    err = response.json().get("error", {})
        except: pass
        msg = err.get("message") or str(e)
        print(f"\n❌ Error Meta API ({response.status_code}, code={code}): {msg}")
        sys.exit(1)


def api_get(path, params, paginate=False, max_retries=3):
    """
    GET a Graph API con:
      - Reintentos con backoff ante rate limits (códigos 4/17/32/613).
      - Paginación opcional siguiendo `paging.next`.
      - Manejo claro de token expirado (190) y permisos (200).

    `path` puede ser absoluto ("https://...") o relativo ("/me/businesses").
    """
    url = path if path.startswith("http") else f"{BASE_URL}/{path.lstrip('/')}"
    results = []

    while url:
        delay = 2
        for attempt in range(max_retries):
            try:
                r = requests.get(url, params=params, timeout=30)
            except requests.RequestException as e:
                if attempt == max_retries - 1:
                    print(f"\n❌ Error de red: {e}")
                    sys.exit(1)
                time.sleep(delay); delay *= 2
                continue

            if r.status_code == 200:
                break

            code = _error_code(r)
            if code in RATE_LIMIT_CODES and attempt < max_retries - 1:
                print(f"  ⏳ Rate limit (code {code}) — esperando {delay}s...")
                time.sleep(delay); delay *= 2
                continue

            _handle_api_error(r)

        body = r.json()
        data = body.get("data")

        if not paginate:
            return body

        if isinstance(data, list):
            results.extend(data)
        url = body.get("paging", {}).get("next")
        params = None  # la URL de `next` ya incluye todos los parámetros

    return {"data": results}
