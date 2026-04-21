# Meta Campaign Analyzer

Plugin para Claude Code que conecta con la **Meta Marketing API** y analiza campañas de Facebook e Instagram usando la metodología de las **3 Q's**: ¿Qué pasó? / ¿Por qué pasó? / ¿Qué haremos?

---

## ¿Qué hace?

Guía al usuario por un flujo completo de análisis:

```
Access Token → Negocios → Campañas → Tipo de campaña → Análisis → [Conjuntos → Anuncios]
```

Soporta 5 tipos de campaña con métricas y benchmarks específicos para cada uno:

| Tipo | Métricas |
|------|---------|
| 🛒 Ventas | ROAS, embudo completo, valor de conversión |
| 💬 Interacción | Conversaciones, tasa de conversión a mensajes |
| 📋 Clientes Potenciales — Formularios | CPL, tasa de conversión de formulario |
| 🌐 Clientes Potenciales — Sitio web | CPL, tasa de conversión de landing page |
| 🏪 Reconocimiento / Tiendas físicas | Alcance, frecuencia, CPM |

Incluye análisis de **Efecto Desglose** para decisiones correctas a nivel de adset y anuncio individual.

---

## Requisitos

- [Claude Code](https://claude.ai/code)
- Python 3.7+
- Librería `requests`:
  ```bash
  pip install requests
  ```
- Token de acceso de Meta con permisos: `ads_read`, `ads_management`, `business_management`, `read_insights`

---

## Instalación

### Como skill personal

Copia la carpeta `skills/meta-campaign-analyzer/` a tu directorio de skills:

```bash
cp -r skills/meta-campaign-analyzer ~/.claude/skills/
```

### Como plugin de Claude Code

Usa el comando `/plugin` dentro de Claude Code para añadir este repo como plugin. El manifiesto está en `.claude-plugin/plugin.json`.

---

## Uso

1. Abre Claude Code con el plugin/skill activo.
2. Habla sobre cualquier campaña de Meta — Claude activará el skill automáticamente.
3. **Pega tu Access Token** en el chat una sola vez. Claude:
   - Lo guarda en `.env` automáticamente.
   - Ejecuta los scripts por ti.
   - Lee los JSON generados y te muestra los resultados.
   - Te pide solo lo estrictamente necesario (qué cuenta, qué campaña, qué periodo).

No tienes que editar archivos, exportar variables, ni copiar/pegar JSON. Todo es conversacional.

### Archivo `.env`

Claude gestiona este archivo solo, pero si quieres crearlo manualmente:

```env
META_ACCESS_TOKEN=EAA...tu_token_aqui
# opcionales:
AD_ACCOUNT_ID=act_123456789
CAMPAIGN_ID=123456789
ADSET_ID=123456789
DATE_PRESET=last_30d
```

> `.env` está en `.gitignore` — no se commitea.

### Ejecución manual (si prefieres usar los scripts por tu cuenta)

```bash
pip install requests
export META_ACCESS_TOKEN=EAA...
python scripts/fetch_businesses.py              # → businesses.json
export AD_ACCOUNT_ID=act_123456789
python scripts/fetch_campaigns.py               # → campaigns.json
export CAMPAIGN_ID=123456789
python scripts/fetch_insights.py                # → insights_*.json
python scripts/fetch_adsets.py                  # → adsets_<CAMPAIGN_ID>.json
export ADSET_ID=123456789
python scripts/fetch_ads.py                     # → ads_<ADSET_ID>.json
```

---

## Estructura del proyecto

```
meta-campaign-analyzer/
├── .claude-plugin/
│   └── plugin.json              # Manifiesto del plugin
├── skills/
│   └── meta-campaign-analyzer/
│       └── SKILL.md             # Lógica y metodología de análisis
└── scripts/
    ├── _common.py               # Config, API helpers, paginación, retry
    ├── fetch_businesses.py      # Paso 1: negocios y cuentas
    ├── fetch_campaigns.py       # Paso 2: campañas de una cuenta
    ├── fetch_insights.py        # Paso 3: métricas de una campaña
    ├── fetch_adsets.py          # Conjuntos de anuncios
    └── fetch_ads.py             # Anuncios individuales
```

---

## Cómo obtener tu Access Token

1. Ve a https://developers.facebook.com/apps/
2. Click en **"Crear app"** e ingresa el nombre
3. En **Caso de uso** selecciona:
   - ✅ Crear y administrar anuncios con la API de Marketing
   - ✅ Medir datos de rendimiento de los anuncios con la API de Marketing
4. Selecciona el **portafolio comercial** y crea la app
5. En el menú superior ve a **Herramientas → Explorador de API Graph**
6. Selecciona tu app → **"Generar token de acceso"**
7. Agrega los permisos: `ads_read`, `ads_management`, `business_management`, `read_insights`

> **Para uso continuo:** crea un **System User Token** en Business Manager → Configuración → Usuarios del sistema. Los tokens de usuario expiran.

---

## Créditos

La metodología de análisis de campañas (las **3 Q's**: ¿Qué pasó? / ¿Por qué pasó? / ¿Qué haremos?) está basada en el trabajo de **Felipe Vergara**.

📺 [YouTube: @FelipeVergara](https://www.youtube.com/@FelipeVergara)

---

## Licencia

MIT
