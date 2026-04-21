# CLAUDE.md — Reglas anti-ban para Meta Marketing API

> Este archivo instruye a cualquier agente de Claude Code que trabaje con este repo sobre cómo operar el skill `meta-campaign-analyzer` sin poner en riesgo la cuenta de Business Manager, la cuenta publicitaria ni el token del usuario.

---

## Por qué existe este archivo

Desde finales de 2025 Meta lleva adelante una ola de baneos contra cuentas que usan automatización/integraciones con la Marketing API. Se han reportado **cuentas legítimas con 16+ años de antigüedad** desactivadas por patrones de uso que el sistema de detección (**"Andromeda"**) clasifica como abuso.

Este skill es **solo lectura** — pero eso no es garantía. La mayoría de baneos ocurren por problemas en **arquitectura**, **autenticación** y **configuración**, no por lo que el código haga o deje de hacer. Este archivo es el mínimo que Claude debe cumplir para no escalar el riesgo.

---

## 1. Arquitectura obligatoria — Fetch → Local → Analyze

**Única arquitectura permitida:**

```
Claude (prompt)  →  Bash("python scripts/fetch_*.py")  →  Meta Graph API
                                    ↓
                           JSON local en disco
                                    ↓
                    Claude (Read tool)  →  Análisis conversacional
```

**Reglas:**

- ✅ Claude SOLO toca la Meta API **ejecutando los scripts Python de este repo** (`scripts/fetch_*.py`) vía la tool `Bash`.
- ✅ Claude SOLO consume datos de Meta **leyendo los JSON locales** con la tool `Read`.
- 🚫 **PROHIBIDO** usar `WebFetch` contra `graph.facebook.com` o cualquier subdominio de `facebook.com`/`fb.com`.
- 🚫 **PROHIBIDO** usar cualquier MCP server de Meta/Facebook no oficial (`mcp__*facebook*`, `mcp__*meta-ads*`, etc.). Estos no pasan por App Review y usan tokens personales — ban automático reportado.
- 🚫 **PROHIBIDO** lanzar navegadores (Playwright/Selenium/etc.) contra `business.facebook.com` o `adsmanager.facebook.com`. Andromeda detecta esto al instante — es la causa #1 de baneos reportados en 2025.

Si un Claude sucesor encuentra una forma "más directa" de hacer esto (MCP, WebFetch, scraping): **NO la uses**. Fue intencional que todo pase por el script.

---

## 2. Autenticación — System User Token (requisito duro)

Meta distingue dos tipos de token:

| Tipo | Expiración | Riesgo de ban | Uso recomendado |
|---|---|---|---|
| **User Access Token** (personal) | ~60 días | 🔴 Alto — si Meta marca la actividad, banea la cuenta personal | Solo pruebas puntuales |
| **System User Token** (no personal) | Nunca (hasta revocar) | 🟢 Bajo — diseñado para automatización | **Único recomendado** |

**Cuando el usuario te pida operar el skill:**

1. Pregunta explícitamente: **"¿Tu token es de Usuario del Sistema (System User) o es un token personal del Explorador de API Graph?"**
2. Si el usuario tiene **token personal** → advierte del riesgo antes de proceder:
   > "⚠️ Estás a punto de usar un token personal. Si Meta marca la actividad, tu cuenta personal puede quedar restringida. ¿Quieres continuar, o prefieres generar un System User Token primero? (Te puedo guiar en 2 min)."
3. Si el usuario tiene **System User Token** → procede normalmente.

**Guía rápida para generar un System User Token:**

1. Business Manager → **Configuración de la empresa** → **Usuarios** → **Usuarios del sistema**.
2. **Añadir** → nombre (ej. `meta-analyzer-read`) → rol: **Empleado**.
3. **Asignar activos** → selecciona las cuentas publicitarias → permiso **solo Ver rendimiento**.
4. **Generar nuevo token** → app: la Developer App (ver §3) → permisos: `ads_read`, `business_management` → **no expira**.

Guarda el token en `.env` (nunca en el código, nunca en git).

---

## 3. Developer App en Business Manager SEPARADA

**Causa muy frecuente de baneos recientes:** crear la Developer App (que emite el token) en la **misma** Business Manager que opera las cuentas publicitarias de producción.

**Regla:**

- La Developer App debe vivir en una **Business Manager separada** de la que contiene los activos de negocio del cliente.
- Esa BM separada puede ser nueva (creada solo para la app) o una BM de pruebas.
- Desde ahí se pide el System User Token, y a ese System User se le asignan los activos de la BM de producción (acceso cruzado solo-lectura).

**Si el usuario no sabe hacerlo, guíalo.** Si insiste en usar la misma BM para todo: adviértelo explícitamente del riesgo y deja constancia en el chat de que se le informó.

---

## 4. Permisos (scopes) — nunca escalar

Este skill es **estrictamente solo-lectura**. Los únicos permisos necesarios son:

- `ads_read` → leer campañas, adsets, ads, insights.
- `business_management` → listar negocios en `/me/businesses`.

**Reglas duras:**

- 🚫 NUNCA pidas ni aceptes tokens con `ads_management` (escritura). Si el usuario pegó un token con `ads_management`, recomienda regenerar uno con scope reducido — no es requerido y amplía la superficie de ataque.
- 🚫 NUNCA uses `read_insights` (legacy de Page Insights, obsoleto para Ads).
- 🚫 Si el usuario te pide **modificar** una campaña (pausar, cambiar presupuesto, editar creativo, etc.) → **redirigir a Ads Manager**:
  > "Este skill no modifica campañas por diseño. Haz el cambio desde Ads Manager (adsmanager.facebook.com) y vuelve aquí para medir el impacto."
- 🚫 NUNCA instales ni uses MCPs que prometan modificar campañas — ver §1.

---

## 5. Rate limits

Meta usa un sistema de puntos (BUC, "Business Use Case Usage"):

| Tier | Presupuesto | Ventana | 1 GET cuesta | 1 WRITE cuesta |
|---|---|---|---|---|
| Development | 60 puntos | 5 min | 1 pt | 3 pts |
| Standard | 9,000 puntos | 5 min | 1 pt | 3 pts |

**Una sesión típica de análisis con este skill consume < 50 GETs** — muy por debajo del límite en cualquier tier. No hay motivo para saturar.

**Reglas:**

- ✅ El módulo `scripts/_common.py` ya implementa backoff exponencial (2s→4s→8s) ante códigos `4`, `17`, `32`, `613` (rate limit) y `429`. Confía en él.
- ✅ Si un script falla por rate limit tras reintentos → **espera al menos 5 minutos** antes de reejecutarlo. No lo reejecutes en loop.
- ✅ Si el usuario pide analizar varias cuentas en la misma sesión → hazlo **de una en una**, esperando a que cada script termine.
- 🚫 NUNCA ejecutes múltiples `fetch_*.py` **en paralelo** (ej. no pongas `run_in_background: true` en el Bash tool para este repo). Las ráfagas paralelas son uno de los patrones que Andromeda marca.

---

## 6. Antipatrones prohibidos (todo esto puede causar ban)

Lista explícita para que no haya dudas:

| Antipatrón | Por qué banea |
|---|---|
| Scraping del DOM de `business.facebook.com` / `adsmanager.facebook.com` | Andromeda detecta patrones de navegador automatizado al instante. Causa #1 de baneos reportados. |
| Automatizar clicks con Playwright/Selenium en UI de Meta | Igual que arriba — Andromeda no distingue "uso personal" de "bot". |
| Usar tokens personales en scripts que corren 24/7 o en cron | Los tokens personales expiran; renovarlos programáticamente con `fb_exchange_token` en volumen es bandera roja. |
| Hacer POST/DELETE a `/campaigns`, `/adsets`, `/ads`, `/adcreatives` | Este skill NO lo hace; si un Claude sucesor lo intenta → abortar. |
| Usar endpoints no documentados (ej. los internos que usa Ads Manager) | Garantía de ban — solo la API pública es legítima. |
| Usar versiones de API viejas (< v18) | Meta penaliza versiones deprecadas. El skill usa `v21.0`. |
| Instalar MCPs de Meta/Facebook sin App Review oficial | La mayoría son proyectos de terceros con tokens personales — misma categoría que scraping. |
| Tokens hardcodeados en el repo o commiteados a git | No es ban directo, pero si el token se filtra y alguien lo usa abusivamente, la cuenta paga. |
| Ejecutar fetches en paralelo o en ráfagas | Meta espera tráfico "humano" — ráfagas disparan heurísticas. |

---

## 7. Protocolo si el usuario reporta un ban

Si el usuario dice que Meta le desactivó la cuenta, la BM, la app, o el token:

1. **Detener toda ejecución** inmediatamente. No ejecutes más scripts.
2. Pedir el **correo/notificación exacta de Meta** con el motivo del ban (o el texto del aviso en Business Manager).
3. **NO** generar un token nuevo ni reautenticar con otra cuenta en la misma sesión — eso puede interpretarse como evasión y amplificar el problema.
4. **NO** intentar "probar si todavía funciona" ejecutando otra request — si hay una restricción activa, cada request extra cuenta.
5. Guiar al usuario al **flujo de apelación oficial**:
   - Business Manager: https://business.facebook.com/business/info → ver avisos.
   - Apelación: https://www.facebook.com/help/contact/2166173276743732 (o el enlace que aparezca en el aviso).
6. Revisar este archivo con el usuario para identificar qué regla se saltó (si es que se saltó alguna) y documentar para el futuro.

---

## 8. Checklist antes de ejecutar `fetch_*.py`

Antes de lanzar cualquier `python scripts/fetch_*.py` con la tool `Bash`, verifica mentalmente:

- [ ] ¿El `.env` existe y tiene `META_ACCESS_TOKEN`? (si no, escríbelo con el token que dio el usuario).
- [ ] ¿El token es de System User o ya advertí del riesgo si es personal?
- [ ] ¿El scope solicitado es solo `ads_read` + `business_management` (no `ads_management`)?
- [ ] ¿Es el primer fetch de la sesión, o el anterior ya terminó? (nada en paralelo).
- [ ] ¿Hubo un error de rate limit hace menos de 5 minutos? Si sí → esperar.

Si cualquier respuesta es ambigua: pregunta al usuario antes de ejecutar.

---

## Referencias

- Fuente principal de estas reglas: `/Users/alonso/Dev/Anti-Bloqueo/Papers/meta-api-ai-safety-guide (1).md`.
- Documentación oficial de Meta Marketing API: https://developers.facebook.com/docs/marketing-apis/
- System User Tokens: https://developers.facebook.com/docs/marketing-api/system-users/

> Este archivo es la versión **básica** de reglas anti-ban. Para el curso se construirá una versión exhaustiva con ejemplos de código, logging estructurado, cache con TTL, y tabla completa de códigos de error Meta.
