<div align="center">

<img src="assets/banner.svg" alt="3 Q's — Meta Campaign Analyzer" width="100%"/>

<br/>

<h1>3 Q's — Meta Campaign Analyzer</h1>

<p><strong>Plugin para Claude Code que diagnostica campañas de Meta (Facebook &amp; Instagram Ads) aplicando la metodología de las 3 Q's y un sistema de benchmarks semáforo 🔴 🟡 🟢.</strong></p>

<p>
  <img alt="Version" src="https://img.shields.io/badge/version-1.4.0-74fbfb?style=for-the-badge&labelColor=2e3848"/>
  <img alt="Claude Code" src="https://img.shields.io/badge/Claude%20Code-Plugin-8dd0df?style=for-the-badge&labelColor=2e3848"/>
  <img alt="Meta Marketing API" src="https://img.shields.io/badge/Meta%20Marketing%20API-v23.0-376290?style=for-the-badge&labelColor=2e3848"/>
  <img alt="License" src="https://img.shields.io/badge/license-MIT-F5F6F7?style=for-the-badge&labelColor=2e3848"/>
</p>

<p>
  <a href="#-instalación">Instalar</a> ·
  <a href="#-cómo-funciona">Cómo funciona</a> ·
  <a href="#-metodología-3-qs">Metodología</a> ·
  <a href="#-tipos-de-campaña-soportados">Tipos soportados</a> ·
  <a href="#-seguridad--anti-ban">Seguridad</a>
</p>

</div>

---

## ✨ ¿Qué hace?

**3 Q's** conecta Claude Code con la **Meta Marketing API** y convierte los datos brutos de tus campañas en un diagnóstico accionable en 3 pasos:

> 1️⃣ **¿Qué pasó?** → Resultados principales vs tu objetivo de negocio
> 2️⃣ **¿Por qué pasó?** → Diagnóstico del embudo y calidad creativa
> 3️⃣ **¿Qué haremos?** → Optimizaciones concretas priorizadas

No tienes que editar archivos, exportar variables ni pegar JSON. Pegas tu Access Token una vez y Claude conduce la conversación:

```text
Access Token → Negocios → Campañas → Tipo → Análisis → [Conjuntos → Anuncios]
```

---

## 🚦 Sistema de benchmarks semáforo

Cada métrica se evalúa contra umbrales verde / amarillo / rojo:

| 🔴 Deficiente | 🟡 Aceptable | 🟢 Óptimo |
|:---:|:---:|:---:|
| Acción urgente | Revisar y optimizar | Mantener / escalar |

Los benchmarks se adaptan automáticamente al **tipo de campaña** y al **objetivo de negocio** que declaras (ROAS, CPL o costo por conversación).

---

## 🎯 Tipos de campaña soportados

| Tipo | Métrica clave | Benchmarks principales |
|---|---|---|
| 🛒 **Ventas** | ROAS | Embudo completo: Impresiones → Clics → Landing → Checkout → Compra |
| 💬 **Interacción / WhatsApp** | Costo por conversación | Tasa conversión a mensajes, CTR único |
| 📋 **Clientes Potenciales — Formularios** | CPL | Tasa conversión del formulario instantáneo |
| 🌐 **Clientes Potenciales — Sitio web** | CPL | Tasa conversión landing + velocidad |
| 🏪 **Reconocimiento / Tiendas físicas** | Alcance / CPM | Frecuencia, calidad del creativo |

Todas las tablas incluyen además: % video 3s, tiempo promedio de reproducción, frecuencia, CPM y métricas de calidad de Meta.

---

## 🧠 Metodología 3 Q's

### 1️⃣ ¿Qué pasó?
Métricas principales comparadas contra **tu** objetivo (no benchmarks genéricos). Ejemplo:
> *"ROAS 2.1x vs objetivo 4x → 47% por debajo 🔴"*

### 2️⃣ ¿Por qué pasó?
Se recorre el embudo paso por paso para encontrar el **eslabón débil**:

```
Impresiones → Clics salientes → Visitas p.d. → Ver contenido → Carrito → Checkout → Compra
                   ▲                                                      
                   └── El % más bajo revela dónde se pierde la audiencia
```

### 3️⃣ ¿Qué haremos?
Recomendaciones priorizadas por impacto, siempre aplicando las reglas del **Efecto Desglose** antes de pausar o escalar (nunca matar anuncios que Meta está preservando por aprendizaje).

---

## ⚡ Inicio rápido

### Requisitos

- [Claude Code](https://claude.ai/code) instalado
- Python 3.7+
- Token de Meta con permisos **de solo lectura**: `ads_read` + `business_management`

### 🔌 Instalación

<details open>
<summary><strong>Opción A — Plugin (recomendado, funciona en CLI y VS Code)</strong></summary>

Dentro de Claude Code:

```bash
/plugin marketplace add felipeverce/3Qs
/plugin install 3qs@3qs
```

O vía UI: `/plugin` → **Discover** → **3qs** → Install.

> La extensión de VS Code **solo** admite instalación vía plugin.

</details>

<details>
<summary><strong>Opción B — Skill personal (solo CLI)</strong></summary>

```bash
cp -r skills/3qs ~/.claude/skills/
```

</details>

### ▶️ Uso

1. Abre Claude Code con el plugin activo.
2. Escribe algo como *"Analiza mis campañas de Meta del último mes"*.
3. Pega tu **Access Token** una sola vez.
4. Claude hace el resto: escribe `.env`, ejecuta los scripts, lee los JSON y te presenta el diagnóstico.

---

## 🛠️ Ejecución manual (opcional)

Si prefieres usar los scripts por fuera de Claude:

```bash
pip install requests
export META_ACCESS_TOKEN=EAA...

python scripts/fetch_businesses.py               # → businesses.json
export AD_ACCOUNT_ID=act_123456789

python scripts/fetch_campaigns.py                # → campaigns.json
export CAMPAIGN_ID=123456789

python scripts/fetch_insights.py                 # → insights_*.json
python scripts/fetch_adsets.py                   # → adsets_<CAMPAIGN_ID>.json

export ADSET_ID=123456789
python scripts/fetch_ads.py                      # → ads_<ADSET_ID>.json
```

### Archivo `.env` (gestionado por Claude)

```env
META_ACCESS_TOKEN=EAA...
AD_ACCOUNT_ID=act_123456789
CAMPAIGN_ID=123456789
ADSET_ID=123456789
DATE_PRESET=last_30d
```

> `.env` está en `.gitignore` — nunca se commitea.

---

## 📁 Estructura del proyecto

```
3Qs/
├── .claude-plugin/
│   ├── plugin.json              → Manifiesto del plugin
│   └── marketplace.json         → Manifiesto del marketplace
├── skills/
│   └── 3qs/
│       └── SKILL.md             → Lógica y metodología
├── scripts/
│   ├── _common.py               → Config, helpers, paginación, retry
│   ├── fetch_businesses.py      → Paso 1: negocios y cuentas
│   ├── fetch_campaigns.py       → Paso 2: campañas
│   ├── fetch_insights.py        → Paso 3: métricas
│   ├── fetch_adsets.py          → Conjuntos de anuncios
│   └── fetch_ads.py             → Anuncios individuales
└── assets/
    └── banner.svg
```

---

## 🛡️ Seguridad / Anti-ban

Meta ha baneado cuentas legítimas (algunas con 16+ años) desde finales de 2025 al detectar patrones automatizados "no humanos" — aunque la API sea solo lectura. Este skill sigue prácticas seguras, pero hay decisiones que dependen de ti:

- ✅ **System User Token**, no token personal (los personales expiran y su uso continuo es señal de riesgo).
- ✅ **Developer App en una Business Manager SEPARADA** de tus cuentas de producción.
- ✅ **Scopes mínimos:** `ads_read` + `business_management`. Nunca `ads_management` — este skill no modifica campañas.
- 🚫 **Nada de MCPs no oficiales** ni scraping del Business Manager — el sistema *Andromeda* de Meta banea esa actividad al instante.

Si operas este skill desde Claude Code, asegúrate de cargar las reglas anti-ban (template reutilizable: `templates/CLAUDE-meta-readonly.md` en el directorio padre).

---

## 🔑 Cómo obtener tu Access Token

1. Entra a https://developers.facebook.com/apps/
2. **Crear app** → nombre → caso de uso: *Crear y administrar anuncios* + *Medir rendimiento con la API de Marketing*.
3. Selecciona tu **portafolio comercial** y crea la app.
4. **Herramientas → Explorador de API Graph** → selecciona tu app.
5. **Generar token de acceso** con SOLO: `ads_read` + `business_management`.

> Para uso continuo, crea un **System User Token** en Business Manager → Configuración → Usuarios del sistema. No expiran.

---

## 👤 Créditos

La metodología de las **3 Q's** (*¿Qué pasó? / ¿Por qué pasó? / ¿Qué haremos?*) está basada en el trabajo de **Felipe Vergara**.

<p>
  <a href="https://www.youtube.com/@FelipeVergara">
    <img alt="YouTube" src="https://img.shields.io/badge/YouTube-@FelipeVergara-74fbfb?style=for-the-badge&logo=youtube&logoColor=white&labelColor=2e3848"/>
  </a>
  <a href="https://github.com/felipeverce/3Qs">
    <img alt="GitHub" src="https://img.shields.io/badge/GitHub-felipeverce/3Qs-8dd0df?style=for-the-badge&logo=github&logoColor=white&labelColor=2e3848"/>
  </a>
</p>

---

## 📄 Licencia

MIT © [Felipe Vergara](https://github.com/felipeverce)

<div align="center">

<sub>Hecho con 💙 para la comunidad hispana de performance marketing.</sub>

</div>
