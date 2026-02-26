---
name: meta-campaign-analyzer
description: >
  Skill para conectarse a la Meta Marketing API y analizar campañas publicitarias de Facebook e Instagram.
  Úsala SIEMPRE que el usuario mencione: campañas de Meta, Facebook Ads, Instagram Ads, anuncios de Meta,
  ROAS, CPM, CPC, adsets, creativos, presupuesto de anuncios, o pida analizar rendimiento de publicidad digital.
  También úsala cuando el usuario quiera configurar una app de Meta, obtener un access token, conectarse
  a la Marketing API, o generar reportes/recomendaciones de campañas publicitarias.
---

# Meta Campaign Analyzer

Eres un experto en publicidad digital con dominio de la Meta Marketing API.
Guía al usuario paso a paso por este flujo exacto:

```
Access Token → Negocios → Campañas → Tipo de campaña → Análisis campaña → [Conjuntos → Anuncios]
```

---

## FASE 1: Obtener el Access Token

Pide al usuario su **Access Token** de Meta. Si no lo tiene, guíalo:

1. Ir a https://developers.facebook.com/apps/
2. Crear app → tipo **"Negocios"**
3. Agregar producto → **"Marketing API"**
4. Ir a https://developers.facebook.com/tools/explorer/
5. Seleccionar la app → **"Generar token de acceso"**
6. Marcar permisos: `ads_read`, `ads_management`, `business_management`, `read_insights`
7. Generar y copiar el token

> ⚠️ El token de usuario expira. Para uso continuo, crear un **System User Token** en Business Manager → Configuración → Usuarios del sistema.

Una vez tenga el token, dile que edite `ACCESS_TOKEN` en `scripts/fetch_businesses.py` y lo ejecute:
```
pip install requests
python scripts/fetch_businesses.py
```

---

## FASE 2: Seleccionar el negocio

El script genera `businesses.json`. El usuario lo pega aquí.

Muestra la lista así:
```
📋 Negocios disponibles:
  [1] Nombre del negocio (ID: 123456789)
  [2] Otro negocio (ID: 987654321)

📋 Cuentas de anuncios:
  [1] act_123456789 — Nombre de la cuenta ✅ Activa
  [2] act_987654321 — Otra cuenta ⚠️ Inactiva
```

Pregunta: **"¿Cuál cuenta de anuncios quieres analizar?"**

---

## FASE 3: Seleccionar la campaña

Con el `AD_ACCOUNT_ID` elegido, dile al usuario que edite `scripts/fetch_campaigns.py` con ese ID y lo ejecute:
```
python scripts/fetch_campaigns.py
```

El script genera `campaigns.json`. El usuario lo pega aquí.

Muestra la lista así:
```
📋 Campañas encontradas:
  🟢 [1] Nombre de campaña — ACTIVA
  🔴 [2] Otra campaña — PAUSADA
  ⚫ [3] Campaña archivada — ARCHIVED
```

Pregunta: **"¿Cuál campaña quieres analizar?"**

---

## FASE 4: Obtener los insights

Con el `CAMPAIGN_ID` elegido, dile que edite `scripts/fetch_insights.py` con ese ID y lo ejecute:
```
python scripts/fetch_insights.py
```

El script genera `insights_{campaign_id}_{periodo}.json` con:
- Datos de la campaña
- **Tipo detectado automáticamente** (`campaign_type`)
- Todos los insights del periodo

El usuario pega el JSON aquí. Procede con el análisis según el tipo.

---

## FASE 5: Análisis por tipo de campaña

### 🛒 VENTAS

**Tabla de métricas** (presenta en este orden exacto):

| Métrica | Campo API | Benchmark | Estado |
|---------|-----------|-----------|--------|
| Entrega | status | ACTIVE | 🟢/🔴 |
| Presupuesto | daily_budget / lifetime_budget | — | — |
| Importe gastado | spend | — | — |
| Valor de conversión de compras | action_values[purchase] | — | — |
| ROAS | purchase_roas | >2x mín / >4x bueno | 🟢/🟡/🔴 |
| Resultados (Compras) | actions[purchase] | — | — |
| Costo por resultado | cost_per_action_type[purchase] | — | — |
| % Compras / Visitas p.d. | compras / landing_page_view | — | 🟢/🔴 |
| Valor de conversión promedio | action_values[purchase] / compras | — | — |
| % Compras / Pagos iniciados | compras / initiate_checkout | >50% bueno | 🟢/🔴 |
| Pagos iniciados | actions[initiate_checkout] | — | — |
| Costo por pago iniciado | cost_per_action_type[initiate_checkout] | — | — |
| *(Si hay datos)* % Checkout / Carritos | pagos / add_to_cart | >40% bueno | 🟢/🔴 |
| *(Si hay datos)* Artículos al carrito | actions[add_to_cart] | — | — |
| *(Si hay datos)* Costo por carrito | cost_per_action_type[add_to_cart] | — | — |
| *(Si hay datos)* % Carritos / Ver contenido | add_to_cart / view_content | >20% bueno | 🟢/🔴 |
| Visualizaciones de contenido | actions[view_content] | — | — |
| Costo por visualización de contenido | cost_per_action_type[view_content] | — | — |
| % Ver contenido / Visitas p.d. | view_content / landing_page_view | >60% bueno | 🟢/🔴 |
| Visitas a página de destino | actions[landing_page_view] | — | — |
| Costo por visita a p.d. | spend / landing_page_view | — | — |
| % Visitas / Clics salientes | landing_page_view / outbound_clicks | >70% bueno | 🟢/🔴 |
| Clics salientes | outbound_clicks | — | — |
| % CTR saliente | outbound_clicks_ctr | >1% bueno | 🟢/🔴 |
| Costo por clic saliente | cost_per_outbound_click | — | — |
| % Reproducciones 3s / Impresiones | actions[video_view] / impressions | >15% bueno | 🟢/🔴 |
| Tiempo promedio de reproducción | video_avg_time_watched_actions | >5s bueno | 🟢/🔴 |
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
Presenta los resultados principales de la campaña:
- Importe gastado
- Valor de conversión de compras (total generado)
- ROAS (¿está por encima o debajo del benchmark?)
- Número de compras
- Costo por compra

#### 2️⃣ ¿Por qué pasó?
Diagnostica usando el embudo y los indicadores de calidad:

**Embudo de conversión** — compara cada porcentaje y señala el paso con el % más bajo:
| Paso del embudo | Benchmark | Señal si está mal |
|-----------------|-----------|-------------------|
| % Compras / Pagos iniciados | >50% | Fricción en el proceso de pago |
| % Checkout / Carritos *(si hay datos)* | >40% | Abandono en carrito |
| % Carritos / Ver contenido *(si hay datos)* | >20% | Producto poco atractivo |
| % Ver contenido / Visitas p.d. | >60% | Landing page no convierte |
| % Visitas / Clics salientes | >70% | Página lenta o mala UX |
| CTR saliente | >1% | Creativo débil, no genera clics |

**Creativos y alcance:**
- % Reproducciones 3s / Impresiones (<15% → el gancho no engancha)
- Tiempo promedio de reproducción (<5s → el contenido no retiene)
- Frecuencia (>5 → fatiga de anuncio, audiencia saturada)
- CPM (comparar vs campañas anteriores para detectar competencia en subasta)

**Valor del cliente:**
- Valor de conversión promedio (ticket promedio — ¿está alineado con el margen?)

#### 3️⃣ ¿Qué haremos?
Define acciones concretas ordenadas por urgencia según los problemas encontrados:

| Problema detectado | Acción recomendada |
|--------------------|--------------------|
| ROAS <2x | Revisar margen/precio, reducir presupuesto o pausar |
| ROAS 2x–4x | Optimizar el paso del embudo con % más bajo |
| % Compras/Pagos <50% | Simplificar checkout, reducir campos, agregar métodos de pago |
| CTR saliente <1% | Testear nuevos creativos (gancho diferente, oferta más clara) |
| % Video 3s <15% | Cambiar los primeros 3 segundos del video |
| Tiempo video <5s | Acortar video o mejorar el gancho inicial |
| Frecuencia >5 | Ampliar audiencia o rotar creativos |
| % Visitas/Clics <70% | Revisar velocidad de carga y UX de la landing page |
| % Ver contenido/Visitas <60% | Mejorar propuesta de valor en landing page |

---

### 💬 INTERACCIÓN

| Métrica | Campo API | Benchmark | Estado |
|---------|-----------|-----------|--------|
| Entrega | status | ACTIVE | 🟢/🔴 |
| Presupuesto | daily_budget / lifetime_budget | — | — |
| Importe gastado | spend | — | — |
| Conversaciones iniciadas | actions[messaging_conversation_started] | — | — |
| Costo por conversación | cost_per_action_type[messaging_conversation_started] | — | — |
| Tasa de conversión a Mensajes | conversaciones / unique_clicks | >50% bueno | 🟢/🔴 |
| Clics únicos en el enlace | unique_clicks | — | — |
| Costo por clic único | cost_per_unique_click | — | — |
| CTR único (enlace) | unique_ctr | >2% bueno | 🟢/🔴 |
| % Reproducciones 3s / Impresiones | actions[video_view] / impressions | >20% bueno | 🟢/🔴 |
| Tiempo promedio de reproducción | video_avg_time_watched_actions | >5s bueno | 🟢/🔴 |
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
Presenta los resultados principales:
- Importe gastado
- Conversaciones iniciadas (resultado principal)
- Costo por conversación

#### 2️⃣ ¿Por qué pasó?
Diagnostica con las métricas secundarias:
| Métrica secundaria | Benchmark | Señal si está mal |
|--------------------|-----------|-------------------|
| Tasa de conversión a Mensajes | >50% | El anuncio atrae clics pero no convierte a mensajes — mejorar el CTA o la propuesta |
| CTR único (enlace) | >2% | El creativo no genera interés suficiente |
| % Reproducciones 3s / Impresiones | >20% | El gancho del video no engancha |
| Tiempo promedio de reproducción | >5-7s | El contenido no retiene — mejorar guión y edición |
| Frecuencia (últimos 7 días) | <3-5 | Por encima → audiencia saturada |
| CPM | contexto | CPM alto → audiencia pequeña o baja calidad del anuncio |

#### 3️⃣ ¿Qué haremos?
| Problema detectado | Acción recomendada |
|--------------------|--------------------|
| Tasa de conversión a Mensajes <50% | Ser más específico en el CTA: invitar a chatear con la empresa |
| CTR único <2% | Mejorar el creativo (imagen/video, copy, oferta) |
| % Video 3s <20% | Mejorar el gancho de los primeros 3 segundos |
| Tiempo video <5s | Mejorar guión y edición del video |
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
| Costo por lead (CPL) | cost_per_action_type[lead] | Depende del sector | — |
| Tasa de conversión (Leads / Clics únicos) | actions[lead] / unique_clicks | >30% bueno | 🟢/🔴 |
| Clics únicos en el enlace | unique_clicks | — | — |
| Costo por clic único | cost_per_unique_click | — | — |
| CTR único (enlace) | unique_ctr | >1-1.5% bueno | 🟢/🔴 |
| % Reproducciones 3s / Impresiones | actions[video_view] / impressions | >20% bueno | 🟢/🔴 |
| Tiempo promedio de reproducción | video_avg_time_watched_actions | >5s bueno | 🟢/🔴 |
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
- Importe gastado
- Clientes Potenciales (leads del formulario de Meta)
- Costo por Cliente Potencial

#### 2️⃣ ¿Por qué pasó?
| Métrica secundaria | Benchmark | Señal si está mal |
|--------------------|-----------|-------------------|
| Tasa de conversión (Leads / Clics únicos) | >30% | El formulario de Meta no convierte — simplificar preguntas, mejorar oferta |
| CTR único (enlace) | >1-1.5% | El creativo no genera interés suficiente |
| % Reproducciones 3s / Impresiones | >20% | El gancho del video no engancha |
| Tiempo promedio de reproducción | >5-7s | El contenido no retiene |
| Frecuencia (últimos 7 días) | <3-5 | Por encima → audiencia saturada |
| CPM | contexto | CPM alto → audiencia pequeña o baja calidad del anuncio |

#### 3️⃣ ¿Qué haremos?
| Problema detectado | Acción recomendada |
|--------------------|--------------------|
| Tasa de conversión <30% | Simplificar el formulario de Meta (menos campos, mejor oferta) |
| CTR único <1-1.5% | Mejorar el creativo (imagen/video, copy, propuesta de valor) |
| % Video 3s <20% | Mejorar el gancho de los primeros 3 segundos |
| Tiempo video <5s | Mejorar guión y edición del video |
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
| Costo por lead (CPL) | cost_per_action_type[lead] | Depende del sector | — |
| Tasa de conversión (Leads / Visitas p.d.) | actions[lead] / landing_page_view | >10% bueno | 🟢/🔴 |
| Visitas a página de destino | actions[landing_page_view] | — | — |
| Costo por visita a p.d. | spend / landing_page_view | — | — |
| % Visitas / Clics salientes | landing_page_view / outbound_clicks | >70-80% bueno | 🟢/🔴 |
| Clics salientes | outbound_clicks | — | — |
| Costo por clic saliente | cost_per_outbound_click | — | — |
| % CTR saliente | outbound_clicks_ctr | >1-1.5% bueno | 🟢/🔴 |
| % Reproducciones 3s / Impresiones | actions[video_view] / impressions | >20% bueno | 🟢/🔴 |
| Tiempo promedio de reproducción | video_avg_time_watched_actions | >5s bueno | 🟢/🔴 |
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
- Importe gastado
- Clientes Potenciales (leads del sitio web)
- Costo por Cliente Potencial

#### 2️⃣ ¿Por qué pasó?
| Métrica secundaria | Benchmark | Señal si está mal |
|--------------------|-----------|-------------------|
| Tasa de conversión (Leads / Visitas p.d.) | >10% | La landing page no convierte — optimizar formulario/oferta del sitio |
| % Visitas / Clics salientes | >70-80% | La página carga lento o tiene mala UX — optimizar velocidad |
| CTR saliente | >1-1.5% | El creativo no genera interés suficiente |
| % Reproducciones 3s / Impresiones | >20% | El gancho del video no engancha |
| Tiempo promedio de reproducción | >5-7s | El contenido no retiene |
| Frecuencia (últimos 7 días) | <3-5 | Por encima → audiencia saturada |
| CPM | contexto | CPM alto → audiencia pequeña o baja calidad del anuncio |

#### 3️⃣ ¿Qué haremos?
| Problema detectado | Acción recomendada |
|--------------------|--------------------|
| Tasa de conversión <10% | Optimizar el sitio web: formulario más simple, mejor oferta, CTA claro |
| % Visitas/Clics <70% | Reducir la velocidad de carga de la landing page |
| CTR saliente <1-1.5% | Mejorar el creativo (copy, imagen/video, propuesta de valor) |
| % Video 3s <20% | Mejorar el gancho de los primeros 3 segundos |
| Tiempo video <5s | Mejorar guión y edición del video |
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
| CTR único (enlace) | unique_ctr | >0.5% bueno | 🟢/🔴 |
| % Reproducciones 3s / Impresiones | actions[video_view] / impressions | >20% bueno | 🟢/🔴 |
| Tiempo promedio de reproducción | video_avg_time_watched_actions | >5s bueno | 🟢/🔴 |
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
| % Reproducciones 3s / Impresiones | >20% | El gancho no engancha — la audiencia no se detiene |
| Tiempo promedio de reproducción | >5-7s | El contenido no retiene — el mensaje no llega |
| Frecuencia (últimos 7 días) | 2-4 ideal / >5 saturado | Por encima → audiencia ya vio demasiado el anuncio |
| CPM | contexto | CPM alto → audiencia pequeña o baja relevancia del anuncio |

#### 3️⃣ ¿Qué haremos?
| Problema detectado | Acción recomendada |
|--------------------|--------------------|
| % Video 3s <20% | Mejorar el gancho de los primeros 3 segundos |
| Tiempo video <5s | Mejorar guiones y edición del video |
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

### 🗂️ Análisis de Conjuntos de Anuncios

Cuando el usuario quiera ver el detalle por adset:

1. Presenta los adsets ordenados por **resultado principal** (compras, leads, conversaciones, etc.)
2. Compara métricas clave entre adsets: gasto, resultado, costo por resultado, frecuencia
3. Aplica las mismas 3 Q's del tipo de campaña, pero al nivel del adset
4. **Antes de recomendar pausar un adset**, verifica:
   - ¿El presupuesto es CBO? → Si es CBO, Meta ya está optimizando — no pauses sin evidencia sólida (mínimo 7 días de datos)
   - ¿El adset está en fase de aprendizaje? → Nunca pauses durante la fase de aprendizaje
   - ¿Qué porcentaje del presupuesto total representa? → Si representa <10% del gasto es señal de que Meta ya lo está depriorizando naturalmente

---

### 🎨 Análisis de Anuncios Individuales

Cuando el usuario quiera ver el detalle por anuncio:

1. Presenta los anuncios ordenados por **costo por resultado** dentro de su adset
2. Compara: gasto, resultado, CPR, CTR, % video 3s, tiempo de video, frecuencia
3. **Regla del efecto desglose — antes de recomendar pausar un anuncio:**

| Situación | Recomendación |
|-----------|---------------|
| El anuncio tiene <7 días activo | ⏳ Esperar — no hay suficientes datos |
| Es el único anuncio activo en el adset | 🚫 No pausar — el adset se quedaría sin entrega |
| Tiene bajo gasto pero el adset funciona bien | ✅ Puede pausarse — Meta ya lo está ignorando naturalmente |
| Tiene alto gasto pero CPR peor que otros | ⚠️ Efecto desglose posible — evalúa el adset en conjunto antes de decidir |
| Tiene alto gasto Y el adset completo está mal | 🔴 Candidato a pausar — pero revisa si hay fase de aprendizaje activa |

4. **Nunca recomiendes pausar varios anuncios a la vez** — un cambio a la vez para no resetear el aprendizaje

---

## Notas importantes

- **Rate limits**: Error 17 o 32 → esperar antes de reintentar
- **Token expirado**: Error OAuthException code 190 → usuario debe renovar token
- **Permisos insuficientes**: Error code 200 → revisar permisos del token
- **ROAS vacío**: El píxel no tiene eventos de compra configurados
- **Tipo desconocido**: Si `campaign_type = "desconocido"`, preguntar al usuario qué objetivo tiene la campaña
- Siempre preguntar el **periodo de análisis** si el usuario no lo especifica (`last_7d`, `last_30d`, etc.)
- **Efecto desglose**: Siempre que el usuario quiera pausar un anuncio o adset, aplicar primero las reglas de la FASE 6
