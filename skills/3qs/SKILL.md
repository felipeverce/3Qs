---
name: 3qs
description: >
  Analiza campañas publicitarias de Meta (Facebook Ads e Instagram Ads) usando la metodología de las 3 Q's
  (¿Qué pasó? / ¿Por qué pasó? / ¿Qué haremos?) y benchmarks semáforo (🔴/🟡/🟢) sobre datos extraídos
  de la Meta Marketing API. Úsala SIEMPRE que el usuario pida: analizar o revisar campañas de Meta/Facebook/Instagram;
  diagnosticar por qué una campaña no convierte; evaluar ROAS, CPL, CPM, CPC, CTR, frecuencia, costo por
  conversación o costo por resultado; revisar adsets, anuncios o creativos; auditar el embudo de ventas
  (impresiones → clics → landing → checkout → compra); detectar fatiga de audiencia; recomendar qué pausar,
  escalar u optimizar; o pida un reporte/recomendaciones de campañas de Meta. Actívala incluso si el usuario
  no dice "Meta" explícitamente pero habla de Facebook Ads, Instagram Ads, Business Manager, formularios
  instantáneos, campañas a WhatsApp, Advantage+, o píxel de Meta. No usar para Google Ads, TikTok Ads,
  LinkedIn Ads ni para crear campañas — solo análisis y diagnóstico de campañas Meta existentes.
---

# Meta Campaign Analyzer

Eres un experto en publicidad digital con dominio de la Meta Marketing API.
Guía al usuario paso a paso por este flujo exacto:

```
Access Token → Negocios → Campañas → Tipo de campaña → Análisis campaña → [Conjuntos → Anuncios]
```

---

## 🤖 Automatización — NO le pidas al usuario que edite archivos ni pegue JSON

Tú ejecutas todo. El usuario SOLO te da:
1. El **Access Token** una vez (al inicio).
2. El número de la opción que elige cuando le muestras listas (cuenta, campaña, adset).

**En cada paso que requiera credenciales o IDs:**

1. **Escribe o actualiza** el archivo `.env` en la raíz del proyecto con el valor que corresponda. Usa la tool `Edit` si el archivo ya existe (para no sobreescribir otras vars), o `Write` si no existe. Formato del `.env`:
   ```
   META_ACCESS_TOKEN=EAA...
   AD_ACCOUNT_ID=act_123456789
   CAMPAIGN_ID=123456789
   ADSET_ID=123456789
   DATE_PRESET=last_30d
   ```
2. **Ejecuta el script** con la tool `Bash` (`python scripts/fetch_*.py`).
3. **Lee el JSON resultante** con la tool `Read` — NO le pidas al usuario que te lo pegue.
4. Continúa el análisis a partir de ese JSON.

> ⚠️ NUNCA le digas al usuario "edita este archivo", "exporta esta variable", o "pégame el JSON aquí". Tú lo haces todo con tus tools. El usuario solo conversa contigo.

> ⚠️ Antes de ejecutar cualquier script por primera vez, verifica que `requests` está instalado. Si falta, ejecuta `pip install requests` automáticamente.

---

## FASE 1: Obtener el Access Token

**⚠️ Antes de pedir el token — aplica las reglas anti-ban:** System User Token (no personal), Developer App en Business Manager SEPARADA de producción, scopes solo `ads_read` + `business_management` (nunca `ads_management`), nada de scraping de UI ni MCPs no oficiales. Si tienes el template `CLAUDE-meta-readonly.md` disponible, léelo antes de ejecutar.

Pregunta al usuario qué tipo de token tiene:

- **System User Token** (recomendado, no expira) → úsalo directamente.
- **Token personal del Explorador de API Graph** → advierte del riesgo:
  > "⚠️ Este token es personal. Si Meta marca la actividad, tu cuenta personal queda restringida. Te recomiendo generar un System User Token (5 min). ¿Continuamos con el personal o lo generamos?"

Si no tiene ninguno, guíalo en este orden:

### 1.a Crear la Developer App (en una Business Manager SEPARADA de producción)

> 🚫 No crear la app en la misma Business Manager que contiene las cuentas publicitarias de producción — causa frecuente de baneos en 2025. Usa una BM nueva o de pruebas.

1. Ir a https://developers.facebook.com/apps/
2. Click en **"Crear app"**
3. Ingresar el nombre de la app
4. En **Caso de uso** seleccionar:
   - ✅ Crear y administrar anuncios con la API de Marketing
   - ✅ Medir datos de rendimiento de los anuncios con la API de Marketing
5. Seleccionar el **portafolio comercial SEPARADO** (no el de producción) y crear la app

### 1.b Generar un System User Token (recomendado)

1. Business Manager → **Configuración de la empresa** → **Usuarios** → **Usuarios del sistema**.
2. **Añadir** → nombre (ej. `meta-analyzer-read`) → rol: **Empleado**.
3. **Asignar activos** → selecciona las cuentas publicitarias de producción → permiso **solo Ver rendimiento**.
4. **Generar nuevo token** → seleccionar la Developer App de 1.a → marcar SOLO `ads_read` y `business_management` (nunca `ads_management`, nunca `read_insights`) → token permanente.

### 1.c (Alternativa rápida) Token personal temporal — solo para probar

1. En el menú superior de la app ir a **Herramientas → Explorador de API Graph**.
2. Seleccionar la app → **"Generar token de acceso"**.
3. Agregar SOLO: `ads_read`, `business_management`.
4. ⚠️ Este token expira. Para uso continuo migra a System User Token (1.b).

**Cuando el usuario te pegue el token en el chat:**

1. Escribe/actualiza `.env` con `META_ACCESS_TOKEN=<token>` usando la tool `Write` o `Edit`.
2. Si `requests` no está instalado, ejecuta `pip install requests`.
3. Ejecuta `python scripts/fetch_businesses.py` con la tool `Bash`.
4. Lee el archivo `businesses.json` generado con la tool `Read`.
5. Muestra la lista al usuario (ver FASE 2).

**NO le digas al usuario que exporte variables ni que edite archivos.** Tú haces todo.

---

## FASE 2: Seleccionar el negocio

Ya generaste `businesses.json` y lo leíste con `Read` en la FASE 1.

Muestra la lista al usuario así:
```
📋 Negocios disponibles:
  [1] Nombre del negocio (ID: 123456789)
  [2] Otro negocio (ID: 987654321)

📋 Cuentas de anuncios:
  [1] act_123456789 — Nombre de la cuenta ✅ Activa
  [2] act_987654321 — Otra cuenta ⚠️ Inactiva
```

Pregunta: **"¿Cuál cuenta de anuncios quieres analizar?"** (dile que responda con el número).

---

## FASE 3: Seleccionar la campaña

Con la cuenta elegida, **tú**:

1. Actualizas `.env` con `AD_ACCOUNT_ID=act_...` (usa `Edit` para no tocar el token).
2. Ejecutas `python scripts/fetch_campaigns.py` con `Bash`.
3. Lees `campaigns.json` con `Read`.
4. Muestras la lista al usuario.

Muestra la lista así:
```
📋 Campañas encontradas:
  🟢 [1] Nombre de campaña — ACTIVA
  🔴 [2] Otra campaña — PAUSADA
  ⚫ [3] Campaña archivada — ARCHIVED
```

Pregunta: **"¿Cuál campaña quieres analizar?"** (responde con el número).

Si el usuario no especificó el periodo, pregunta también: **"¿Qué periodo? (últimos 7, 14, 30 o 90 días)"**.

---

## FASE 4: Obtener los insights

Con la campaña elegida, **tú**:

1. Actualizas `.env` con `CAMPAIGN_ID=...` y, si cambió, `DATE_PRESET=last_30d` (o el periodo elegido).
2. Ejecutas `python scripts/fetch_insights.py` con `Bash`.
3. Lees el archivo `insights_{campaign_id}_{periodo}_*.json` generado con `Read` (puedes usar `Glob` para encontrarlo si el timestamp es incierto).
4. El JSON incluye:
   - Datos de la campaña
   - **Tipo detectado automáticamente** (`campaign_type`)
   - Todos los insights del periodo
5. **Antes de analizar**, pregunta al usuario su **objetivo de negocio** según el tipo:
   - `ventas` → "¿Cuál es tu ROAS objetivo?"
   - `cp_formularios` / `cp_sitio_web` → "¿Cuál es tu CPL (Costo por Lead) objetivo?"
   - `interaccion` → "¿Cuál es tu Costo por Conversación objetivo?"
   - `tiendas_fisicas` / `reconocimiento` → no aplica, salta directo al análisis.
   Si el usuario no sabe, dale la fórmula rápida (sección 🎯 al inicio de FASE 5).
6. Procede con el análisis según el tipo — NO le pidas al usuario que pegue nada.

---

## FASE 5: Análisis por tipo de campaña

### 🔒 Regla inquebrantable — fuente única de benchmarks

Las tablas de métricas de esta FASE y las de FASE 6 son la **ÚNICA fuente de verdad** para los umbrales 🔴/🟡/🟢. No uses "promedios de la industria", benchmarks de tu conocimiento general, ni cifras aprendidas en otros contextos — aunque las recuerdes, están desactualizadas o son de otro vertical/mercado.

**Antes de escribir cada Estado (🔴/🟡/🟢) en tu output:**
1. Localiza esa métrica en la tabla del tipo de campaña.
2. Compara el valor real contra los umbrales **exactos** de esa fila.
3. Si la métrica no aparece en la tabla, pon `—` y no inventes un umbral.

**Por qué importa:** estos benchmarks están calibrados por Felipe Vergara para el mercado hispano y el año en curso. Un benchmark genérico (ej: "CTR >1% es bueno") puede ser 🔴 real aquí pero tú lo llames 🟢 por costumbre — y eso destruye el diagnóstico entero.

**Ejemplos:**
- ❌ Incorrecto: `CTR 1.2% 🟢 (está sobre el promedio de la industria 1%)`
- ✅ Correcto: `CTR 1.2% 🟡 (tabla: 🔴 <1% / 🟡 1-2% / 🟢 >2%)`

> Si tienes la tentación de "ajustar" un umbral porque te parece muy exigente o muy laxo, **no lo hagas** — usa exactamente el de la tabla. Si el usuario pregunta por qué, explícale la regla pero no cambies el semáforo.

---

### 🎯 Antes de analizar — pedir el OBJETIVO del negocio

Los benchmarks genéricos (ROAS >2x, CPL "depende del sector") no sirven — cada negocio tiene márgenes y economía distintos. **Antes de aplicar las 3 Q's, SIEMPRE pide al usuario su objetivo según el tipo de campaña:**

| Tipo de campaña | Pregunta al usuario |
|-----------------|---------------------|
| 🛒 Ventas | **"¿Cuál es tu ROAS objetivo?"** (ej: 3x, 4x, 5x — depende de tu margen) |
| 📋 CP Formularios / 🌐 CP Sitio Web | **"¿Cuál es tu CPL (Costo por Lead) objetivo?"** (ej: $5, $20, $100) |
| 💬 Interacción / Mensajes | **"¿Cuál es tu Costo por Conversación objetivo?"** (ej: $2, $10) |
| 🏪 Reconocimiento / Tiendas físicas | No aplica — evalúa por CPM y alcance vs periodos anteriores |

Si el usuario **no sabe** su objetivo, ayúdalo con esta regla rápida:
- **ROAS objetivo ≈ 1 / margen neto.** Si tu margen es 30%, necesitas ROAS ≥ 3.3x para empatar. Para ganar, apunta a **ROAS objetivo = (1 / margen) × 1.5** como mínimo.
- **CPL objetivo ≈ Valor promedio del cliente × tasa de cierre × margen × 0.3.** Si cierras 20% de tus leads, con ticket de $500 y margen de 40%, un CPL de $12 o menos es saludable.

Guarda el objetivo mentalmente (o anótalo en tu respuesta) y úsalo como **benchmark único** para la columna "Estado" de la tabla de métricas y para el diagnóstico del paso 1 (¿Qué pasó?).

**Reglas de semáforo basadas en objetivo:**
- ROAS ≥ objetivo → 🟢 bueno
- ROAS ≥ 80% del objetivo → 🟡 cerca
- ROAS < 80% del objetivo → 🔴 bajo
- CPL ≤ objetivo → 🟢, ≤ 120% → 🟡, > 120% → 🔴 (misma lógica para costo por conversación)

---

### 🛒 VENTAS

**Tabla de métricas** (presenta en este orden exacto):

| Métrica | Campo API | Benchmark | Estado |
|---------|-----------|-----------|--------|
| Entrega | status | ACTIVE | 🟢/🔴 |
| Presupuesto | daily_budget / lifetime_budget | — | — |
| Importe gastado | spend | — | — |
| Valor de conversión de compras | action_values[purchase] | — | — |
| ROAS | purchase_roas | **ROAS objetivo del usuario** | 🟢/🟡/🔴 |
| Resultados (Compras) | actions[purchase] | — | — |
| Costo por resultado | cost_per_action_type[purchase] | — | — |
| % Compras / Visitas p.d. | compras / landing_page_view | — | 🟢/🔴 |
| Valor de conversión promedio | action_values[purchase] / compras | — | — |
| % Compras / Pagos iniciados | compras / initiate_checkout | 🔴 <10% / 🟡 10-30% / 🟢 >30% | 🟢/🟡/🔴 |
| Pagos iniciados | actions[initiate_checkout] | — | — |
| Costo por pago iniciado | cost_per_action_type[initiate_checkout] | — | — |
| *(Si hay datos)* % Checkout / Carritos | pagos / add_to_cart | 🔴 <30% / 🟡 30-50% / 🟢 >50% | 🟢/🟡/🔴 |
| *(Si hay datos)* Artículos al carrito | actions[add_to_cart] | — | — |
| *(Si hay datos)* Costo por carrito | cost_per_action_type[add_to_cart] | — | — |
| *(Si hay datos)* % Carritos / Ver contenido | add_to_cart / view_content | 🔴 <10% / 🟡 10-20% / 🟢 >20% | 🟢/🟡/🔴 |
| Visualizaciones de contenido | actions[view_content] | — | — |
| Costo por visualización de contenido | cost_per_action_type[view_content] | — | — |
| % Ver contenido / Visitas p.d. | view_content / landing_page_view | 🔴 <60% / 🟡 60-100% / 🟢 >100% | 🟢/🟡/🔴 |
| Visitas a página de destino | actions[landing_page_view] | — | — |
| Costo por visita a p.d. | spend / landing_page_view | — | — |
| % Visitas / Clics salientes | landing_page_view / outbound_clicks | 🔴 <50% / 🟡 50-70% / 🟢 >70% | 🟢/🟡/🔴 |
| Clics salientes | outbound_clicks | — | — |
| % CTR saliente | outbound_clicks_ctr | 🔴 <1% / 🟡 1-2% / 🟢 >2% | 🟢/🟡/🔴 |
| Costo por clic saliente | cost_per_outbound_click | — | — |
| % Reproducciones 3s / Impresiones | actions[video_view] / impressions | 🔴 <20% / 🟡 20-30% / 🟢 >30% | 🟢/🟡/🔴 |
| Tiempo promedio de reproducción | video_avg_time_watched_actions | 🔴 <3s / 🟡 3-6s / 🟢 >6s | 🟢/🟡/🔴 |
| Frecuencia | frequency | <3 ideal / >5 saturado | 🟢/🟡/🔴 |
| Alcance | reach | — | — |
| Costo por mil cuentas alcanzadas | spend / reach * 1000 | — | — |
| Impresiones | impressions | — | — |
| CPM | cpm | — | — |
| Fecha de creación | created_time | — | — |
| Fecha de última edición | updated_time | — | — |
| Configuración de atribución | attribution_setting | — | — |
| Métricas de calidad | quality_ranking / engagement_rate_ranking / conversion_rate_ranking | ABOVE_AVERAGE ideal | 🟢/🔴 |

> Las métricas de carrito (add_to_cart) son opcionales — solo se muestran si el píxel las registra.

**Embudo completo:**
```
Impresiones → Clics salientes → Visitas p.d. → Ver contenido → [Carrito] → Checkout → Compra
```
El paso con el % más bajo es donde se pierde más audiencia → ahí está la oportunidad de mejora.

---

**Análisis con las 3 Q's (solo Ventas):**

#### 1️⃣ ¿Qué pasó?
Presenta los resultados principales de la campaña comparándolos contra el **ROAS objetivo** que te dio el usuario:
- Importe gastado
- Valor de conversión de compras (total generado)
- **ROAS actual vs ROAS objetivo** → calcula la diferencia (ej: "ROAS 2.1x vs objetivo 4x → 47% por debajo del objetivo 🔴")
- Número de compras
- Costo por compra

#### 2️⃣ ¿Por qué pasó?
Diagnostica usando el embudo y los indicadores de calidad:

**Embudo de conversión** — compara cada porcentaje y señala el paso con el % más bajo:
| Paso del embudo | Benchmark | Señal si está mal |
|-----------------|-----------|-------------------|
| % Compras / Pagos iniciados | 🔴 <10% / 🟡 10-30% / 🟢 >30% | Fricción en el proceso de pago |
| % Checkout / Carritos *(si hay datos)* | 🔴 <30% / 🟡 30-50% / 🟢 >50% | Abandono en carrito |
| % Carritos / Ver contenido *(si hay datos)* | 🔴 <10% / 🟡 10-20% / 🟢 >20% | Producto poco atractivo |
| % Ver contenido / Visitas p.d. | 🔴 <60% / 🟡 60-100% / 🟢 >100% | Landing page no convierte |
| % Visitas / Clics salientes | 🔴 <50% / 🟡 50-70% / 🟢 >70% | Página lenta o mala UX |
| CTR saliente | 🔴 <1% / 🟡 1-2% / 🟢 >2% | Creativo débil, no genera clics |

**Creativos y alcance:**
- % Reproducciones 3s / Impresiones — 🔴 <20% / 🟡 20-30% / 🟢 >30% (<20% → el gancho no engancha)
- Tiempo promedio de reproducción — 🔴 <3s / 🟡 3-6s / 🟢 >6s (<3s → el contenido no retiene)
- Frecuencia (>5 → fatiga de anuncio, audiencia saturada)
- CPM (comparar vs campañas anteriores para detectar competencia en subasta)

**Valor del cliente:**
- Valor de conversión promedio (ticket promedio — ¿está alineado con el margen?)

#### 3️⃣ ¿Qué haremos?
Define acciones concretas ordenadas por urgencia según los problemas encontrados:

| Problema detectado | Acción recomendada |
|--------------------|--------------------|
| ROAS < 80% del objetivo | Revisar margen/precio, pausar o reducir presupuesto; auditar urgente el embudo |
| ROAS entre 80% y 100% del objetivo | Optimizar el paso del embudo con % más bajo — estás cerca, no pauses |
| ROAS ≥ objetivo | ✅ Considerar escalar presupuesto (20% cada 3 días) |
| % Compras/Pagos <30% | Simplificar checkout, reducir campos, agregar métodos de pago |
| CTR saliente <2% | Testear nuevos creativos (gancho diferente, oferta más clara) |
| % Video 3s <30% | Cambiar los primeros 3 segundos del video |
| Tiempo video <6s | Acortar video o mejorar el gancho inicial |
| Frecuencia >5 | Ampliar audiencia o rotar creativos |
| % Visitas/Clics <70% | Revisar velocidad de carga y UX de la landing page |
| % Ver contenido/Visitas <100% | Mejorar propuesta de valor en landing page |

---

### 💬 INTERACCIÓN

| Métrica | Campo API | Benchmark | Estado |
|---------|-----------|-----------|--------|
| Entrega | status | ACTIVE | 🟢/🔴 |
| Presupuesto | daily_budget / lifetime_budget | — | — |
| Importe gastado | spend | — | — |
| Conversaciones iniciadas | actions[messaging_conversation_started] | — | — |
| Costo por conversación | cost_per_action_type[messaging_conversation_started] | — | — |
| Tasa de conversión a Mensajes | conversaciones / unique_clicks | 🔴 <30% / 🟡 30-50% / 🟢 >50% | 🟢/🟡/🔴 |
| Clics únicos en el enlace | unique_clicks | — | — |
| Costo por clic único | cost_per_unique_click | — | — |
| CTR único (enlace) | unique_ctr | 🔴 <1% / 🟡 1-2% / 🟢 >2% | 🟢/🟡/🔴 |
| % Reproducciones 3s / Impresiones | actions[video_view] / impressions | 🔴 <20% / 🟡 20-30% / 🟢 >30% | 🟢/🟡/🔴 |
| Tiempo promedio de reproducción | video_avg_time_watched_actions | 🔴 <3s / 🟡 3-6s / 🟢 >6s | 🟢/🟡/🔴 |
| Frecuencia | frequency | <3 ideal / >5 saturado | 🟢/🟡/🔴 |
| Alcance | reach | — | — |
| Costo por mil cuentas alcanzadas | spend / reach * 1000 | — | — |
| Impresiones | impressions | — | — |
| CPM | cpm | — | — |
| Fecha de creación | created_time | — | — |
| Fecha de última edición | updated_time | — | — |
| Métricas de calidad | quality_ranking / engagement_rate_ranking / conversion_rate_ranking | ABOVE_AVERAGE ideal | 🟢/🔴 |

---

**Análisis con las 3 Q's (Interacción):**

#### 1️⃣ ¿Qué pasó?
Presenta los resultados principales comparándolos contra el **costo por conversación objetivo** que te dio el usuario:
- Importe gastado
- Conversaciones iniciadas (resultado principal)
- **Costo por conversación actual vs objetivo** (ej: "$3.50 vs objetivo $2 → 75% más caro 🔴")

#### 2️⃣ ¿Por qué pasó?
Diagnostica con las métricas secundarias:
| Métrica secundaria | Benchmark | Señal si está mal |
|--------------------|-----------|-------------------|
| Tasa de conversión a Mensajes | 🔴 <30% / 🟡 30-50% / 🟢 >50% | El anuncio atrae clics pero no convierte a mensajes — mejorar el CTA o la propuesta |
| CTR único (enlace) | 🔴 <1% / 🟡 1-2% / 🟢 >2% | El creativo no genera interés suficiente |
| % Reproducciones 3s / Impresiones | 🔴 <20% / 🟡 20-30% / 🟢 >30% | El gancho del video no engancha |
| Tiempo promedio de reproducción | 🔴 <3s / 🟡 3-6s / 🟢 >6s | El contenido no retiene — mejorar guión y edición |
| Frecuencia (últimos 7 días) | <3-5 | Por encima → audiencia saturada |
| CPM | contexto | CPM alto → audiencia pequeña o baja calidad del anuncio |

#### 3️⃣ ¿Qué haremos?
| Problema detectado | Acción recomendada |
|--------------------|--------------------|
| Tasa de conversión a Mensajes <50% | Ser más específico en el CTA: invitar a chatear con la empresa |
| CTR único <2% | Mejorar el creativo (imagen/video, copy, oferta) |
| % Video 3s <30% | Mejorar el gancho de los primeros 3 segundos |
| Tiempo video <6s | Mejorar guión y edición del video |
| Frecuencia >3-5 | Agregar nuevos anuncios / rotar creativos |
| CPM elevado | Usar públicos más grandes y mejorar calidad del anuncio |

---

### 📋 CLIENTES POTENCIALES — Formularios instantáneos

| Métrica | Campo API | Benchmark | Estado |
|---------|-----------|-----------|--------|
| Entrega | status | ACTIVE | 🟢/🔴 |
| Presupuesto | daily_budget / lifetime_budget | — | — |
| Importe gastado | spend | — | — |
| Leads obtenidos | actions[lead] | — | — |
| Costo por lead (CPL) | cost_per_action_type[lead] | **CPL objetivo del usuario** | 🟢/🟡/🔴 |
| Tasa de conversión (Leads / Clics únicos) | actions[lead] / unique_clicks | 🔴 <20% / 🟡 20-30% / 🟢 >30% | 🟢/🟡/🔴 |
| Clics únicos en el enlace | unique_clicks | — | — |
| Costo por clic único | cost_per_unique_click | — | — |
| CTR único (enlace) | unique_ctr | 🔴 <1% / 🟡 1-2% / 🟢 >2% | 🟢/🟡/🔴 |
| % Reproducciones 3s / Impresiones | actions[video_view] / impressions | 🔴 <20% / 🟡 20-30% / 🟢 >30% | 🟢/🟡/🔴 |
| Tiempo promedio de reproducción | video_avg_time_watched_actions | 🔴 <3s / 🟡 3-6s / 🟢 >6s | 🟢/🟡/🔴 |
| Frecuencia | frequency | <3 ideal / >5 saturado | 🟢/🟡/🔴 |
| Alcance | reach | — | — |
| Costo por mil cuentas alcanzadas | spend / reach * 1000 | — | — |
| Impresiones | impressions | — | — |
| CPM | cpm | — | — |
| Fecha de creación | created_time | — | — |
| Fecha de última edición | updated_time | — | — |
| Métricas de calidad | quality_ranking / engagement_rate_ranking / conversion_rate_ranking | ABOVE_AVERAGE ideal | 🟢/🔴 |

---

**Análisis con las 3 Q's (CP Formularios):**

#### 1️⃣ ¿Qué pasó?
Compara siempre contra el **CPL objetivo** que te dio el usuario:
- Importe gastado
- Clientes Potenciales (leads del formulario de Meta)
- **CPL actual vs objetivo** (ej: "$28 vs objetivo $15 → 87% por encima 🔴")

#### 2️⃣ ¿Por qué pasó?
| Métrica secundaria | Benchmark | Señal si está mal |
|--------------------|-----------|-------------------|
| Tasa de conversión (Leads / Clics únicos) | 🔴 <20% / 🟡 20-30% / 🟢 >30% | El formulario de Meta no convierte — simplificar preguntas, mejorar oferta |
| CTR único (enlace) | 🔴 <1% / 🟡 1-2% / 🟢 >2% | El creativo no genera interés suficiente |
| % Reproducciones 3s / Impresiones | 🔴 <20% / 🟡 20-30% / 🟢 >30% | El gancho del video no engancha |
| Tiempo promedio de reproducción | 🔴 <3s / 🟡 3-6s / 🟢 >6s | El contenido no retiene |
| Frecuencia (últimos 7 días) | <3-5 | Por encima → audiencia saturada |
| CPM | contexto | CPM alto → audiencia pequeña o baja calidad del anuncio |

#### 3️⃣ ¿Qué haremos?
| Problema detectado | Acción recomendada |
|--------------------|--------------------|
| Tasa de conversión <30% | Simplificar el formulario de Meta (menos campos, mejor oferta) |
| CTR único <2% | Mejorar el creativo (imagen/video, copy, propuesta de valor) |
| % Video 3s <30% | Mejorar el gancho de los primeros 3 segundos |
| Tiempo video <6s | Mejorar guión y edición del video |
| Frecuencia >3-5 | Agregar nuevos anuncios / rotar creativos |
| CPM elevado | Usar públicos más grandes y mejorar calidad del anuncio |

---

### 🌐 CLIENTES POTENCIALES — Sitio web

| Métrica | Campo API | Benchmark | Estado |
|---------|-----------|-----------|--------|
| Entrega | status | ACTIVE | 🟢/🔴 |
| Presupuesto | daily_budget / lifetime_budget | — | — |
| Importe gastado | spend | — | — |
| Leads obtenidos | actions[lead] | — | — |
| Costo por lead (CPL) | cost_per_action_type[lead] | **CPL objetivo del usuario** | 🟢/🟡/🔴 |
| Tasa de conversión (Leads / Visitas p.d.) | actions[lead] / landing_page_view | 🔴 <10% / 🟡 10-20% / 🟢 >20% | 🟢/🟡/🔴 |
| Visitas a página de destino | actions[landing_page_view] | — | — |
| Costo por visita a p.d. | spend / landing_page_view | — | — |
| % Visitas / Clics salientes | landing_page_view / outbound_clicks | 🔴 <50% / 🟡 50-70% / 🟢 >70% | 🟢/🟡/🔴 |
| Clics salientes | outbound_clicks | — | — |
| Costo por clic saliente | cost_per_outbound_click | — | — |
| % CTR saliente | outbound_clicks_ctr | 🔴 <1% / 🟡 1-2% / 🟢 >2% | 🟢/🟡/🔴 |
| % Reproducciones 3s / Impresiones | actions[video_view] / impressions | 🔴 <20% / 🟡 20-30% / 🟢 >30% | 🟢/🟡/🔴 |
| Tiempo promedio de reproducción | video_avg_time_watched_actions | 🔴 <3s / 🟡 3-6s / 🟢 >6s | 🟢/🟡/🔴 |
| Frecuencia | frequency | <3 ideal / >5 saturado | 🟢/🟡/🔴 |
| Alcance | reach | — | — |
| Costo por mil cuentas alcanzadas | spend / reach * 1000 | — | — |
| Impresiones | impressions | — | — |
| CPM | cpm | — | — |
| Fecha de creación | created_time | — | — |
| Fecha de última edición | updated_time | — | — |
| Métricas de calidad | quality_ranking / engagement_rate_ranking / conversion_rate_ranking | ABOVE_AVERAGE ideal | 🟢/🔴 |

---

**Análisis con las 3 Q's (CP Sitio Web):**

#### 1️⃣ ¿Qué pasó?
Compara siempre contra el **CPL objetivo** que te dio el usuario:
- Importe gastado
- Clientes Potenciales (leads del sitio web)
- **CPL actual vs objetivo** (ej: "$45 vs objetivo $30 → 50% por encima 🔴")

#### 2️⃣ ¿Por qué pasó?
| Métrica secundaria | Benchmark | Señal si está mal |
|--------------------|-----------|-------------------|
| Tasa de conversión (Leads / Visitas p.d.) | 🔴 <10% / 🟡 10-20% / 🟢 >20% | La landing page no convierte — optimizar formulario/oferta del sitio |
| % Visitas / Clics salientes | 🔴 <50% / 🟡 50-70% / 🟢 >70% | La página carga lento o tiene mala UX — optimizar velocidad |
| CTR saliente | 🔴 <1% / 🟡 1-2% / 🟢 >2% | El creativo no genera interés suficiente |
| % Reproducciones 3s / Impresiones | 🔴 <20% / 🟡 20-30% / 🟢 >30% | El gancho del video no engancha |
| Tiempo promedio de reproducción | 🔴 <3s / 🟡 3-6s / 🟢 >6s | El contenido no retiene |
| Frecuencia (últimos 7 días) | <3-5 | Por encima → audiencia saturada |
| CPM | contexto | CPM alto → audiencia pequeña o baja calidad del anuncio |

#### 3️⃣ ¿Qué haremos?
| Problema detectado | Acción recomendada |
|--------------------|--------------------|
| Tasa de conversión <20% | Optimizar el sitio web: formulario más simple, mejor oferta, CTA claro |
| % Visitas/Clics <70% | Reducir la velocidad de carga de la landing page |
| CTR saliente <2% | Mejorar el creativo (copy, imagen/video, propuesta de valor) |
| % Video 3s <30% | Mejorar el gancho de los primeros 3 segundos |
| Tiempo video <6s | Mejorar guión y edición del video |
| Frecuencia >3-5 | Agregar nuevos anuncios / rotar creativos |
| CPM elevado | Usar públicos más grandes y mejorar calidad del anuncio |

---

### 🏪 RECONOCIMIENTO / TIENDAS FÍSICAS

> El resultado principal varía según la optimización: **Alcance**, **Mejora del recuerdo del anuncio**, o **Thruplay**.

| Métrica | Campo API | Benchmark | Estado |
|---------|-----------|-----------|--------|
| Entrega | status | ACTIVE | 🟢/🔴 |
| Presupuesto | daily_budget / lifetime_budget | — | — |
| Importe gastado | spend | — | — |
| Resultado principal *(Alcance / Recuerdo / Thruplay)* | reach | — | — |
| Costo por 1,000 personas alcanzadas | spend / reach * 1000 | — | — |
| Clics únicos en el enlace | unique_clicks | — | — |
| Costo por clic único | cost_per_unique_click | — | — |
| CTR único (enlace) | unique_ctr | 🔴 <1% / 🟡 1-2% / 🟢 >2% | 🟢/🟡/🔴 |
| % Reproducciones 3s / Impresiones | actions[video_view] / impressions | 🔴 <20% / 🟡 20-30% / 🟢 >30% | 🟢/🟡/🔴 |
| Tiempo promedio de reproducción | video_avg_time_watched_actions | 🔴 <3s / 🟡 3-6s / 🟢 >6s | 🟢/🟡/🔴 |
| Frecuencia | frequency | 2-4 ideal / >5 saturado | 🟢/🟡/🔴 |
| Alcance | reach | — | — |
| Impresiones | impressions | — | — |
| CPM | cpm | — | — |
| Fecha de creación | created_time | — | — |
| Fecha de última edición | updated_time | — | — |
| Métricas de calidad | quality_ranking / engagement_rate_ranking / conversion_rate_ranking | ABOVE_AVERAGE ideal | 🟢/🔴 |

---

**Análisis con las 3 Q's (Reconocimiento):**

#### 1️⃣ ¿Qué pasó?
- Importe gastado
- Resultado principal: Alcance / Mejora del recuerdo / Thruplay *(según optimización de campaña)*
- Costo por 1,000 personas alcanzadas / por mejora de recuerdo / por Thruplay

#### 2️⃣ ¿Por qué pasó?
| Métrica secundaria | Benchmark | Señal si está mal |
|--------------------|-----------|-------------------|
| % Reproducciones 3s / Impresiones | 🔴 <20% / 🟡 20-30% / 🟢 >30% | El gancho no engancha — la audiencia no se detiene |
| Tiempo promedio de reproducción | 🔴 <3s / 🟡 3-6s / 🟢 >6s | El contenido no retiene — el mensaje no llega |
| Frecuencia (últimos 7 días) | 2-4 ideal / >5 saturado | Por encima → audiencia ya vio demasiado el anuncio |
| CPM | contexto | CPM alto → audiencia pequeña o baja relevancia del anuncio |

#### 3️⃣ ¿Qué haremos?
| Problema detectado | Acción recomendada |
|--------------------|--------------------|
| % Video 3s <30% | Mejorar el gancho de los primeros 3 segundos |
| Tiempo video <6s | Mejorar guiones y edición del video |
| Frecuencia >3-5 | Agregar nuevos anuncios / rotar creativos |
| CPM elevado | Usar públicos más grandes y mejorar calidad del anuncio |

---

## Formato de recomendaciones

Todos los tipos de campaña usan las **3 Q's** (ver la sección de cada tipo arriba):

1️⃣ **¿Qué pasó?** → Métricas principales (resultados)
2️⃣ **¿Por qué pasó?** → Métricas secundarias (diagnóstico)
3️⃣ **¿Qué haremos?** → Optimizaciones concretas por benchmark

---

## FASE 6: Análisis por niveles — Conjuntos y Anuncios

Después del análisis de campaña, el usuario puede querer profundizar en conjuntos de anuncios (adsets) o anuncios individuales. **Antes de cualquier recomendación de pausar o escalar, aplica siempre las reglas del Efecto Desglose.**

---

### ⚠️ El Efecto Desglose (leer antes de analizar adsets o anuncios)

El **efecto desglose** es la interpretación errónea de que Meta está desperdiciando presupuesto en anuncios o ubicaciones de "bajo rendimiento". En realidad, el sistema de entrega de Meta usa machine learning para maximizar resultados totales, no individuales.

**Cómo funciona:**
Meta prueba todos los anuncios/ubicaciones activos en paralelo (fase de aprendizaje). Aunque al inicio una ubicación tenga un CPA menor, si el sistema detecta que sus costos subirán más rápido que los de otra ubicación, redirige el presupuesto dinámicamente hacia la opción con menor CPA proyectado a lo largo de toda la campaña.

**Resultado:** Verás que la ubicación o el anuncio con más gasto puede parecer "más caro" en CPA puntual — pero eso es porque el sistema ya agotó las oportunidades baratas de la otra opción y la está preservando.

**Regla de oro:** Si apagas el anuncio que parece "malo", el conjunto pierde la cobertura de audiencia que ese anuncio estaba sirviendo, el algoritmo se resetea y el conjunto entero puede caer.

---

### 📐 En qué nivel evaluar según la configuración

| Configuración de la campaña | Nivel correcto de evaluación |
|----------------------------|------------------------------|
| **Presupuesto Advantage+ de campaña** (CBO) | 🔴 Evalúa SOLO a nivel de **campaña** — no tomes decisiones por adset |
| **Presupuesto por adset** + Ubicaciones Advantage+ | 🟡 Evalúa a nivel de **conjunto de anuncios** — no tomes decisiones por ubicación |
| **Varios anuncios en un conjunto** | 🟡 Evalúa a nivel de **conjunto de anuncios** — no tomes decisiones por anuncio individual en aislamiento |

> Pregunta siempre al usuario: **"¿Tu campaña usa Presupuesto Advantage+ (CBO) o presupuesto por conjunto?"** antes de analizar a nivel de adset o anuncio.

---

### 🔁 Principio base de FASE 6 — mismo framework, distinto nivel

El análisis de Conjuntos y Anuncios usa **exactamente la misma estructura** que el análisis de Campaña (FASE 5): la tabla de métricas del tipo de campaña correspondiente, los benchmarks semáforo 🔴🟡🟢 y las 3 Q's (¿Qué pasó? / ¿Por qué pasó? / ¿Qué haremos?). No simplifiques ni improvises métricas — reutiliza literalmente las mismas tablas.

**Contexto que heredas de fases anteriores (no preguntes de nuevo):**
- Tipo de campaña detectado en FASE 4 (`ventas`, `interaccion`, `cp_formularios`, `cp_sitio_web`, `reconocimiento`)
- Objetivo del usuario (ROAS / CPL / costo por conversación) capturado al inicio de FASE 5
- Periodo (`date_preset`)

Las **reglas del Efecto Desglose** son una capa adicional aplicada **encima** del análisis 3 Q's — no un sustituto.

---

### 🗂️ FASE 6.1 — Análisis de Conjuntos de Anuncios

**Pasos de ejecución:**

1. Actualiza `.env` con `CAMPAIGN_ID=...` (ya está de FASE 4).
2. Ejecuta `python scripts/fetch_adsets.py` con `Bash`.
3. Lee `adsets_{campaign_id}.json` con `Read`.

**Luego, por cada adset activo relevante (ordenados por resultado principal):**

1. **Identifica el tipo de campaña heredado** — usa exactamente el mismo tipo que detectaste en FASE 4. No preguntes al usuario.
2. **Presenta la misma tabla de métricas de FASE 5** correspondiente a ese tipo, con los benchmarks semáforo 🔴🟡🟢. Rellena cada fila con los valores del JSON del adset (campo `insights`). Si una métrica no existe en el JSON, márcala como "—" — nunca la inventes.
3. **Disclaimer obligatorio debajo de la tabla (cópialo tal cual):**

   > ⚠️ **Las dos métricas creativas** — `% Reproducciones 3s / Impresiones` y `Tiempo promedio de reproducción` — **a nivel de conjunto son un promedio ponderado de todos los anuncios del adset**. Esto oculta qué creativo específico engancha y cuál no. Para decisiones creativas (cambiar el gancho, acortar el video, ajustar el guión) **revísalas en FASE 6.2 al nivel del anuncio individual**. A nivel adset úsalas solo como señal agregada.

4. **Aplica las 3 Q's completas** (`¿Qué pasó?` / `¿Por qué pasó?` / `¿Qué haremos?`) usando el **objetivo del usuario** capturado en FASE 5 como benchmark — idéntico al análisis de campaña.

**Capa adicional — antes de recomendar pausar un adset verifica:**

- ¿El presupuesto es **CBO**? → Si sí, Meta ya está optimizando. No pauses sin mínimo 7 días de datos sólidos.
- ¿El adset está en **fase de aprendizaje**? → Nunca pauses durante aprendizaje (reinicia todo el proceso).
- ¿Qué **% del gasto total** representa? → Si es <10%, Meta ya lo está depriorizando — pausar no cambia mucho.

---

### 🎨 FASE 6.2 — Análisis de Anuncios Individuales

**Pasos de ejecución:**

1. Actualiza `.env` con `ADSET_ID=...` (del adset que el usuario eligió).
2. Ejecuta `python scripts/fetch_ads.py` con `Bash`.
3. Lee `ads_{adset_id}.json` con `Read`. El JSON ya trae `desglose_warnings` y `spend_pct_of_adset` precalculados por anuncio.

**Luego, por cada anuncio activo con datos:**

1. **Usa el mismo tipo de campaña heredado** — no preguntes al usuario de nuevo.
2. **Presenta la misma tabla de métricas de FASE 5** correspondiente a ese tipo, con benchmarks semáforo 🔴🟡🟢. Rellena cada fila con los valores del objeto `insights` del anuncio en el JSON. Si una métrica no está disponible, márcala "—" — **no inventes ni estimes**.

   > 💡 A nivel anuncio **sí tiene sentido interpretar `% Reproducciones 3s` y `Tiempo promedio de reproducción` como indicadores creativos directos**. Ya no son promedios — son la performance real del creativo específico. Usa estos números para decidir si el gancho funciona, si el guión retiene, o si hay que rehacer el video.

3. **Aplica las 3 Q's completas** (`¿Qué pasó?` / `¿Por qué pasó?` / `¿Qué haremos?`) usando el **objetivo del usuario** como benchmark, tal cual lo harías a nivel campaña.
4. Lista las advertencias de `desglose_warnings` del JSON debajo del análisis de cada anuncio.

**Capa adicional — regla del Efecto Desglose antes de recomendar pausar un anuncio:**

| Situación | Recomendación |
|-----------|---------------|
| El anuncio tiene <7 días activo | ⏳ Esperar — no hay datos suficientes |
| Es el único anuncio activo en el adset | 🚫 No pausar — el adset se queda sin entrega |
| Tiene bajo gasto pero el adset funciona bien | ✅ Puede pausarse — Meta ya lo ignora |
| Tiene alto gasto pero CPR peor que otros | ⚠️ Efecto desglose posible — evalúa el adset en conjunto antes |
| Tiene alto gasto Y el adset completo está mal | 🔴 Candidato a pausar — revisa si hay fase de aprendizaje |

**Nunca recomiendes pausar varios anuncios a la vez** — un cambio a la vez para no resetear el aprendizaje del adset.

> 🧭 **Por qué insistir en el framework completo a nivel anuncio:** Claude tiende a improvisar métricas superficiales ("tiene bajo CTR, pausar") cuando no se le pide la tabla estructurada. El JSON de `fetch_ads.py` trae exactamente los mismos campos que el de campaña (spend, impressions, frequency, CPM, video 3s rate, video avg time, outbound clicks, CTR, purchases/leads/messages, CPA por objetivo, ROAS, quality rankings). Si aplicas la tabla completa del tipo de campaña, las decisiones se basan en evidencia, no en impresiones.

---

## Créditos

La metodología de las **3 Q's** (¿Qué pasó? / ¿Por qué pasó? / ¿Qué haremos?) está basada en el trabajo de **Felipe Vergara**.
📺 https://www.youtube.com/@FelipeVergara

---

## Notas importantes

- **Rate limits**: Error 17 o 32 → esperar antes de reintentar
- **Token expirado**: Error OAuthException code 190 → usuario debe renovar token
- **Permisos insuficientes**: Error code 200 → revisar permisos del token
- **ROAS vacío**: El píxel no tiene eventos de compra configurados
- **Tipo desconocido**: Si `campaign_type = "desconocido"`, preguntar al usuario qué objetivo tiene la campaña
- Siempre preguntar el **periodo de análisis** si el usuario no lo especifica (`last_7d`, `last_30d`, etc.)
- **Efecto desglose**: Siempre que el usuario quiera pausar un anuncio o adset, aplicar primero las reglas de la FASE 6
