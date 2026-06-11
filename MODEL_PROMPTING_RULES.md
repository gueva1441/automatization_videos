# MODEL_PROMPTING_RULES.md

**Versión:** 1.0 (2026-05-25)
**Última actualización:** 2026-05-25 — Chat 30
**Propósito:** Fuente única de verdad sobre cómo prompar a los modelos externos del pipeline (Flux, Veo, Gemini). Consultar **antes** de modificar cualquier prompt en cualquier módulo. Cada regla viene de doc oficial citada o de aprendizaje empírico del proyecto.

---

## Cuándo consultar este archivo

**Obligatorio leer:**

- Antes de modificar `m03_visual.py` (afecta prompts Flux + Veo)
- Antes de modificar cualquier `system_instruction` o prompt template de los módulos `m00`–`m05`
- Antes de modificar `art_profiles.py`, `flow_profiles.py`, o cualquier archivo que concatene texto en prompts
- Antes de tocar `_build_rules_block()`, `_build_veo_prompt()`, `_build_traduc_prompt()` o equivalentes
- Cuando Claude Code recibe un handoff que toca prompts → debe leer este archivo antes de aplicar cambios

**Cómo se actualiza:**

- Cada vez que descubrimos un comportamiento del modelo, agregar entrada a `§4 Anti-patrones` o a la sección del modelo correspondiente
- Cada cambio se registra en `§5 Bitácora`
- El archivo **crece, nunca se rehace**

---

## §1 FLUX 2 Pro (image generation)

**Modelo activo:** `fal-ai/flux-2-pro` (32B params, Mistral-3 24B VLM + rectified flow transformer)
**Fuente oficial:** https://docs.bfl.ml/guides/prompting_guide_flux2

### 1.1 Framework

```
Subject + Action + Style + Context
```

- **Subject:** el foco principal (persona, objeto, personaje) con descriptores físicos integrados
- **Action:** lo que hace o su pose
- **Style:** enfoque artístico, medio, estética
- **Context:** setting, lighting, time, mood, condiciones atmosféricas

### 1.2 REGLAS INVIOLABLES

**R1. Word order matters — subject-first.**
Flux 2 Pro pone más atención a lo que viene primero. El sujeto principal va al inicio, NUNCA después de un prefijo técnico largo.

- ✗ MAL: `"High dynamic range digital sensor, gritty digital film emulation, low-key dramatic lighting -- a mid-age woman sleeping in a hut"`
- ✓ BIEN: `"A mid-age Cameroonian woman sleeping in a hut, low-key dramatic lighting, gritty digital film emulation"`

**R2. NO negative prompts.**
Flux 2 **no soporta** prompts negativos. Frases como `"No readable text, no visible letters, no inscriptions, no signage, no labels"` son ignoradas y sólo suman tokens que diluyen al sujeto.

- Para excluir texto: omitir la mención de texto del prompt (o decir `"clean surfaces"`)
- Para excluir personas: describir `"an empty scene"`, no `"no people"`
- Para excluir blur: decir `"sharp focus throughout"`, no `"no blur"`

**R3. Descriptores físicos integrados al sujeto.**
La etnia, edad, rasgos, ropa van **dentro del bloque del sujeto al inicio**, no esparcidos al final del prompt. Lo que llega tarde, llega diluido.

- ✗ MAL: `"A woman in a hut, ..., 1980s rural clothing, woven basket"` (etnia + ropa al final)
- ✓ BIEN: `"A Cameroonian woman in her 40s, dark skin, wearing 1980s rural cotton wrap, resting inside a hut"`

Ejemplo oficial de la doc (personaje consistente cross-panel):
> *"(30 years old, brown skin tone, short natural fade haircut with black hair, black-framed glasses, light blue button-up shirt, athletic build, strong jawline)"*

**R4. Lenguaje natural en prosa, NO keyword soup ni CSV.**
Flux 2 entiende prosa descriptiva mejor que listas separadas por comas estilo SDXL.

- ✗ MAL: `"...mud brick interior, woven basket, simple cloth wrap, silent, struggling breath"` (CSV redundante al final)
- ✓ BIEN: `"...inside a hut with mud brick walls, a woven basket beside her, an air of silent struggle"`

**R5. Longitud objetivo: 30–80 palabras (medium).**
- Short (10–30 words): conceptos rápidos
- **Medium (30–80 words): óptimo para producción**
- Long (80+ words): sólo escenas complejas que lo justifiquen

**R6. Native language para context cultural.**
Promptear en el idioma del context cultural produce resultados más auténticos. Para topics en Camerún francés: considerar prompt en francés. Para Japón: japonés. Esto es **opcional pero recomendado** para escenas con fuerte componente cultural.

### 1.3 Referencias de cámara y film

Para fotorealismo, citar cámara/lente/película específicas funciona mejor que descriptores genéricos.

| Estilo | Descriptor |
|---|---|
| Modern Digital | `"shot on Sony A7IV, clean sharp, high dynamic range"` |
| 80s Vintage | `"film grain, warm color cast, soft focus, 80s vintage photo"` |
| Analog Film | `"shot on Kodak Portra 400, natural grain, organic colors"` |
| 2000s Digicam | `"early digital camera, slight noise, flash photography, 2000s digicam style"` |

Específico > genérico:
- ✗ `"professional photo"`
- ✓ `"shot on Fujifilm X-T5, 35mm f/1.4"`

### 1.4 Hex codes para colores precisos

Asociar SIEMPRE el código hex a un objeto específico:

- ✗ `"use red #FF0000 in the image"`
- ✓ `"the car is #FF0000"`

### 1.5 JSON structured prompts (opcional, para casos complejos)

Flux 2 entiende JSON estructurado. Útil cuando se necesita control preciso sobre múltiples elementos. **Para nuestro pipeline NO es necesario** — la prosa estructurada según R1–R5 alcanza.

Si en el futuro se quiere usar, schema base:
```json
{
  "scene": "...",
  "subjects": [{"description": "...", "position": "..."}],
  "style": "...",
  "lighting": "...",
  "mood": "...",
  "camera": {"angle": "...", "lens": "..."}
}
```

### 1.6 Anti-patrones específicos de Flux 2 detectados en el proyecto

- **Prefijo técnico mega-largo al inicio** (chat 30): el patrón `"High dynamic range digital sensor, gritty digital film emulation, low-key dramatic lighting, cold desaturated palette, coarse analog noise texture -- "` antes del sujeto sepulta el sujeto principal. **Si se quiere style, debe ir al final o integrado, NO al inicio.**

- **CSV redundante al final** (chat 30): props/mood en CSV después del prompt principal son keyword soup. Mover esa info dentro del prosa o eliminar.

- **Default étnico India/Bangladesh** (chat 30): cuando el prompt menciona `"rural clothing + mud wall + 1980s"` sin etnia explícita, Flux defaultea a rasgos del subcontinente indio (probablemente por densidad de training data para esa combinación). **Mitigación: R3 — etnia siempre integrada al sujeto al inicio.**

### 1.7 Plantilla de referencia para humanos en escena documental

```
A [etnia] [género] in [his/her] [edad], [rasgos físicos opcionales],
wearing [ropa con periodo], [acción o pose], in [setting brief],
[lighting], [style descriptor].
```

Ejemplo aplicado:
```
A Cameroonian woman in her 40s, dark skin and weathered features,
wearing a 1980s rural cotton wrap, resting her head against a mud
wall inside a dimly lit hut, low-key dramatic lighting, gritty
digital film emulation.
```

Conteo: ~38 palabras. Dentro del rango medium. Subject-first. Etnia integrada. Sin negativos. Sin CSV final.

### 1.8 Content safety (espejo de §2.3 Veo)

Flux 2 Pro también tiene content filter. Devuelve **HTTP 422** ante imágenes de
muerte/cuerpos. Detectado chat 31: prompt de ganado "inert/motionless" → 422,
mismo patrón AP9 que Veo.

**Mitigación (igual que Veo, AP9):** pivote "muerte implícita → calma previa".
Aplica a personas Y animales Y víctimas masivas. La narración hace el horror,
la imagen muestra la calma anterior (seres vivos en paz, escena ambiental).

- ✗ CONCEPTO a evitar: cuerpos/figuras inmóviles, aftermath de muerte (aunque
  sea "quieto" dispara el filtro).
- ✓ CONCEPTO correcto: la escena viva y tranquila previa (aldea al atardecer,
  ganado pastando al amanecer, luz de lámpara).

**APARATO de ejecución (chat 54):** el filtro también dispara con el OBJETO o
ESTRUCTURA construido para matar (horca, dispositivo de ejecución), aunque NO
haya ninguna persona en cuadro. Reemplazo = el espacio cargado y vacío (luz
dramática + escala opresiva + UN objeto cargado que implica lo que pasó: una soga
sola, un banco volcado), NUNCA el mecanismo entero. Trigger estrecho al objeto:
las demás escenas (gente, cuartos, vida diaria) NO se vacían. Detectado:
Charleston cap5 (horca) — chat 53/54.

Vive en `SYSTEM_INSTRUCTION_VISUAL` regla 5 (chat 32, sub-cláusula APPARATUS OF
KILLING chat 54). Topics conocidos que disparan filter en Flux: Lake Nyos
(ganado, cap5) — chat 31; Charleston (horca, cap5) — chat 53.

---

## §2 Veo 3.1 (video generation)

**Modelo activo:** `fal-ai/veo-3.1-lite` (con `flux-2-pro` como image input para hooks/outros)
**Fuente oficial:** https://cloud.google.com/blog/products/ai-machine-learning/ultimate-prompting-guide-for-veo-3-1

### 2.1 Framework oficial

```
Cinematography + Subject + Action + Context + Style & Ambiance
```

- **Cinematography:** trabajo de cámara y composición del shot (PRIMERO — clave para tono)
- **Subject:** el foco/personaje principal
- **Action:** qué hace el sujeto
- **Context:** entorno y elementos de fondo
- **Style & ambiance:** estética general, mood, lighting

**Diferencia clave vs Flux:** Veo prioriza la **cinematografía al inicio**, no el sujeto. Esto es porque Veo genera **movimiento**, y el movimiento empieza por la cámara.

### 2.2 REGLAS INVIOLABLES

**R1. Cinematografía al inicio.**
Empezar con shot type + camera movement.

Ejemplo oficial:
> *"Medium shot, a tired corporate worker, rubbing his temples in exhaustion, in front of a bulky 1980s computer..."*

**R2. Vocabulario cinematográfico específico.**
- Movimiento: `dolly shot`, `tracking shot`, `crane shot`, `aerial view`, `slow pan`, `POV shot`
- Composición: `wide shot`, `close-up`, `extreme close-up`, `low angle`, `two-shot`
- Lente/foco: `shallow depth of field`, `wide-angle lens`, `soft focus`, `macro lens`, `deep focus`

**R3. Longitud objetivo: 100–200 palabras** (más larga que Flux porque incluye temporal + audio).
Context window: 5000 tokens.

**R4. Audio en el prompt.**
Veo 3.1 genera audio sincrónico. Se controla con sintaxis explícita:
- **Diálogo:** comillas → `A woman says, "We have to leave now."`
- **SFX:** prefijo SFX → `SFX: thunder cracks in the distance`
- **Ambiente:** prefijo Ambient noise → `Ambient noise: the quiet hum of a starship bridge`

**EN NUESTRO PIPELINE:** NO usamos audio de Veo (lo aportan ElevenLabs + library tracks). Por lo tanto, **NO incluir diálogo ni SFX en `video_prompt`** — eso aumenta riesgo de filter y desperdicia tokens.

**R5. Negative prompts — describir lo positivo.**
Mismo principio que Flux:
- ✗ `"no man-made structures"`
- ✓ `"a desolate landscape with no buildings or roads"` (sigue siendo descriptivo positivo)

**R6. Clip length: 4, 6, u 8 segundos.**
En este proyecto: **8 segundos fijos** (`VEO_CLIP_DURATION_SEC=8.0` en `m03_visual.py`). Si en el futuro se quiere variar, parametrizar — no harcodear en el prompt.

### 2.3 Content safety filter

Veo es **muy estricto** con muerte humana masiva, gore, conflict imagery. El filter devuelve **HTTP 422 Unprocessable Entity** al rechazar.

**Patrón confirmado (chat 29, fix #210):** hooks de desastre humano fallan en Veo cuando los prompts mencionan:
- `"motionless"`, `"abandoned"`, `"eerie"`, `"deep night"`, `"no human figures"`
- Cualquier referencia implícita a muerte o destrucción humana

**Mitigación (fix #210):** pivote semántico **"muerte implícita → calma previa"**. La narración del cap se encarga del horror, la imagen NO.

Ejemplo:
- ✗ MAL: `"motionless village at deep night, abandoned huts, eerie silence"` → 422
- ✓ BIEN: `"peaceful village at dusk, kerosene lamp glow, fireflies drifting, gentle breeze through leaves"`

**Topics conocidos que disparan filter** (registrar acá cuando aparezcan):
- Lake Nyos 1986 (cap 1, hook) — chat 29
- Bhopal — probable (no testeado todavía)
- Jonestown — probable

### 2.4 Image-to-video en este pipeline

El pipeline genera un `image_prompt` (con Flux) que sirve de **primer frame**, y un `video_prompt` que describe la animación. Reglas:

- El `image_prompt` debe respetar las reglas de §1 (Flux)
- El `video_prompt` debe describir **movimiento + cinematografía**, NO repetir descripción visual del frame (eso ya está en el image)
- **NO mezclar:** Veo lee ambos. Redundancia = ruido.

Ejemplo correcto (cap 1 Nyos post-fix #210):
```
image_prompt: "rural Cameroonian village at dusk, mud-brick huts under
dense jungle vegetation, kerosene lamp glow inside one hut, peaceful
evening scene, period-correct 1986 details"

video_prompt: "slow pan across the village, gentle breeze through
leaves, fireflies drifting in the air, soft kerosene lamp flicker,
ambient nighttime atmosphere"
```

El `image_prompt` describe **qué se ve**. El `video_prompt` describe **cómo se mueve la cámara y qué cambia en el tiempo**.

### 2.5 Fallback strategy (backlog #210)

Hoy: 422 = error fatal → cap queda sin clip.
Futuro: capturar 422 → marcar `status="content_policy_fallback"` → regresar a Flux base con DepthFlow (perdemos el clip Veo pero no rompemos el cap).

Pendiente implementar.

---

## §3 Gemini 2.5 Flash (LLM scripter)

**Modelo activo:** `gemini-2.5-flash` (GA, ganó A/B test vs 2.0 Flash y vs 2.5 Flash Preview)
**Fuente oficial:** https://ai.google.dev/gemini-api/docs/prompting-strategies
**Uso en el pipeline:** todos los módulos `m00`–`m05` (sintetizador, skeleton, narrador, visual, juez)

### 3.1 Arquitectura de prompts en este pipeline

Cada llamada Gemini tiene tres capas:

1. **System instruction:** preamble fijo — define rol, tono, constraints inviolables del módulo.
2. **User prompt:** input variable de esa llamada (datos del topic, output del módulo anterior, etc).
3. **Response schema (opcional):** JSON schema para structured output.

### 3.2 REGLAS INVIOLABLES

**R1. Una destilación por llamada.**
Cada módulo del motor (m00, m01a, m01b, m03, m04, m05) hace **una** tarea. No pedir N tareas en una llamada con reglas cruzadas. (Ver `ARCHITECTURE.md` §2 — anti-patrón #1.)

**R2. Validación tardía como parche está PROHIBIDA.**
El validador (m05) audita, **NO reescribe**. Si encuentra problema, emite `FAIL` con `retry_step` para que el módulo correspondiente regenere. (Ver `ARCHITECTURE.md` §2 — anti-patrón #3.)

**R3. Few-shot conceptual, NO literal.**
- Los ejemplos `✗ MAL` no deben contener texto copiable por el modelo
- Si el ejemplo MAL incluye términos prohibidos textualmente, el LLM puede reforzar ese patrón (es lo opuesto de lo que se quiere)
- Anti-patrón confirmado por docs oficiales de Google: *"mencionar términos prohibidos como ejemplos negativos refuerza esos patrones"*

**R4. JSON structured output con response schema.**
Para módulos que devuelven JSON (todos los del motor), usar el parámetro `response_schema` en la llamada API, no pedir el JSON sólo con instrucciones de texto.

Ventajas:
- Garantiza JSON sintácticamente correcto (no más parsing fallido)
- El schema actúa como reglas implícitas para el modelo
- **No garantiza validez semántica** — eso lo valida m05

**R5. Sin demasiados few-shot examples.**
Demasiados ejemplos → el modelo overfittea al formato exacto. 1–3 ejemplos bien elegidos > 10 ejemplos.

**R6. Consistencia de formato entre few-shot examples.**
Si vas a poner ejemplos, deben tener exactamente el mismo formato (mismos XML tags, mismos splitters, mismo whitespace). Inconsistencia → output inconsistente.

### 3.3 Voting para validación (m05)

Aprendizaje empírico del proyecto:

- **~50% del output single-shot de m05 es ruido.** Voting N=3 es el modo recomendado para validación.
- Dedup por `(cap, img, category)`.
- Cohortes:
  - **3/3** = alta confianza, atender prioritario
  - **2/3** = mayoría, atender
  - **1/3** = ruido, ignorar (cohort threshold pasa)
- Wittenoom benchmark: 4 bugs 3/3 + 3 bugs 2/3 + 9 ruido 1/3.

**Side effect documentado (chat 29, #207):** issues reales cohort 1/3 pasan inadvertidos (ej: anachronism modern tablet en Nyos cap 6). Trade-off aceptado para evitar ruido.

### 3.4 Flakiness estocástica

- Cuando se aumenta la cantidad de outputs que un LLM debe emitir en una sola llamada, la calidad cae **estocásticamente, no linealmente**.
- **Anti-patrón:** "bajar el techo" (pedir menos items) NO resuelve. Lo que resuelve es **refactorizar el prompt** para que el LLM tenga menos carga cognitiva por item.

### 3.5 Default art_profile decisión arquitectónica (FASE 5)

`art_profiles.py` fue reemplazado por `system_instruction` único:

> *"Documentary photography style. Period-correct natural lighting per scene. Slightly desaturated palette."*

Razones:
- Catálogo de profiles + assignment ciego = anti-patrón #4 de ARCHITECTURE.md
- La industria de canales faceless documentales NO usa catálogos de profiles
- Gemini 2.5 Flash GA gana A/B test vs 3 Flash Preview (todas las métricas, 3× más barato)

**No reintroducir art_profiles sin razón fuerte.**

### 3.6 Reglas en `_build_rules_block()` (m03)

Cuando se agregan reglas al system instruction de m03:

- Numerar las reglas
- Una regla por concepto (no compound rules con AND/OR cruzados)
- Ejemplos ✓ BIEN al final de cada regla, NO ✗ MAL si el MAL contiene patrón copiable
- Si el LLM ignora una regla, **NO es problema de fuerza de palabra** ("OBLIGATORIO" no fixea nada) — es problema de **dónde queda el default**. Invertir el default antes que agregar imperativos.

**Ejemplo aplicado (chat 30, regla 4 etnia):**
- ✗ Versión vieja: *"La etnia es OBLIGATORIA si hay humanos visibles, salvo que el sujeto sea explícitamente extranjero al GEO"* → escapatoria amplia, LLM la usaba para 17/26 humanos
- ✓ Versión nueva (pendiente aplicar): *"El DEFAULT es la etnia local del GEO. Solo usá otra etnia si la narración nombra explícitamente al sujeto como extranjero"* → invierte el burden of proof

---

## §4 Anti-patrones documentados (aplica a TODOS los modelos)

Estos son patrones que ya nos rompieron al menos una vez. Cuando un fix proponga algo similar, **rechazar sin discusión** (patrón #91 — eliminar la abstracción, no agregar el item N).

### AP1. Prefijo técnico/estilo ANTES del sujeto (Flux)
Síntoma: el sujeto sale mal o se ignora. Causa raíz: word order. Fix: subject-first.
*Detectado: chat 30. Aplica a: Flux 2 Pro.*

### AP2. Negative prompts en modelos que no los soportan
Síntoma: el contenido no excluido aparece igual. Tokens desperdiciados. Causa raíz: Flux 2 y Veo no soportan. Fix: describir lo positivo.
*Detectado: chat 30. Aplica a: Flux 2 Pro, Veo 3.1.*

### AP3. Ejemplos `✗ MAL` con texto copiable
Síntoma: el LLM reproduce el patrón "malo" porque lo vio en el prompt. Fix: few-shot conceptual, no literal.
*Aplica a: Gemini 2.5 Flash (y todos los LLMs).*

### AP4. Reglas con escapatorias amplias
Síntoma: la regla se cumple en pocos casos porque la excepción aplica frecuente. Fix: invertir el default, no agregar imperativos.
*Detectado: chat 29 fix #209 v1. Aplica a: Gemini 2.5 Flash.*

### AP5. Profile/category assignment ciego
Síntoma: outputs mal categorizados porque el assignment se hace con poco contexto. Fix: dar al módulo el contexto completo (bullets/canonical/facts), no solo el title.
*Documentado en: ARCHITECTURE.md §2 anti-patrón #4.*

### AP6. Múltiples tareas en una llamada con reglas cruzadas
Síntoma: el LLM optimiza una en detrimento de la otra. Fix: una destilación por llamada (motor de guion).
*Documentado en: ARCHITECTURE.md §2 anti-patrón #1.*

### AP7. Validador que reescribe
Síntoma: pérdida de trazabilidad, errores propagados sin detectar. Fix: el validador audita, emite FAIL con `retry_step`, el módulo correspondiente regenera.
*Documentado en: ARCHITECTURE.md §2 anti-patrón #3.*

### AP8. Default étnico por contexto en Flux
Síntoma: humanos sin etnia explícita salen con rasgos no coincidentes con el GEO. Específicamente Flux 2 con `"rural + mud wall + 1980s"` → rasgos del subcontinente indio. Fix: §1 R3 — etnia integrada al sujeto al inicio.
*Detectado: chat 30. Aplica a: Flux 2 Pro.*

### AP9. Content filter en desastre/muerte (Veo Y Flux)
Síntoma: HTTP 422 en prompts con figuras inmóviles, cuerpos, aftermath de
muerte (incluso "quieto"), Y TAMBIÉN con la estructura/dispositivo construido
para matar (horca, aparato de ejecución) aunque NO haya persona en cuadro. Fix:
pivote semántico "muerte implícita → calma previa". La narración hace el horror,
no la imagen. Aplica a personas, animales y víctimas masivas. Para el APARATO de
matar: redirigir al espacio cargado vacío (luz + escala + un objeto cargado), no
el mecanismo (sub-cláusula APPARATUS OF KILLING en regla 5, chat 54).
*Detectado: chat 29 fix #210 (Veo) + chat 31 ganado cap5 (Flux) + chat 53/54 horca cap5 (Flux). Aplica a: Veo 3.1 + Flux 2 Pro.*

---

## §5 Bitácora de cambios

| Fecha | Chat | Cambio | Razón |
|---|---|---|---|
| 2026-05-25 | 30 | Creación del archivo con §1 (Flux 2), §2 (Veo 3.1), §3 (Gemini 2.5 Flash), §4 (anti-patrones AP1–AP9) | Patrón #91: dejamos de parchear regla 4 de m03 (3 veces ya) y consolidamos las reglas de prompting de los 3 modelos en una sola fuente de verdad. Iniciativa de Omar tras descubrir en chat 30 que el problema "humanos con cara india en escenas camerunesas" no era falta de la regla "etnia obligatoria" sino estructura del prompt (subject-first, sin negativos, sin CSV final) — info que ya teníamos validada en el pasado pero se perdió en transitions Claude Code ↔ Claude web. |
| 2026-05-28 | 32 | §1.8 content-safety Flux + AP9 ampliado a Flux. m03: afilada regla 5 (muerte→calma cubre animales/masivo), regla 7 (pantallas/proyecciones→abstracto), regla 4 (presente=tangible, no sci-fi), regla 3 path Veo (negativo "no readable text"→positivo). | #232 (ganado 422) + #235 (cap6 holograms+texto "Lake Kivu"). Las reglas existían pero tenían huecos; se afilaron en vez de agregar bloque nuevo. |
| 2026-06-10 | 54 | regla 5 — sub-cláusula APPARATUS OF KILLING (calma tensa): cuando el sujeto sería el mecanismo de matar, el default se invierte al espacio cargado vacío (luz + escala + UN objeto cargado), nunca el aparato. §1.8 + AP9 extendidos al aparato (no solo cuerpos). | cap5 Charleston 422 con la horca; AP9 cubría cuerpos pero no el dispositivo de ejecución. Trigger estrecho al objeto (las demás escenas no se vacían), default invertido, validado en lab de regresión: control Nyos sin flip, ejecución redirige sola (horca→soga/banco volcado), caps normales intactos. |
| 2026-06-11 | 55 | Clasificador visual CIEGO de 5 categorías (`zoom_judge.py`): Gemini Flash vision, temp 0, `response_schema` enum `sujeto_con_fondo\|cara_closeup\|superficie_plana\|corredor_tunel\|otro` + confianza + razón. Test ciego (sin filename/expectativa/mención de zoom). Es el sensor semántico del gate de zoom v3 (geometría depth_probe pre-filtra, el juez decide). Solo `sujeto_con_fondo` promueve a zoom_in. | El depth map geométrico no distingue sujeto-digno-de-zoom de cara close-up o muro con relieve fantasma (labs 1.5). El juez de visión sí: validado lab 1.6 sobre 12 imágenes reales de Charleston, **12/12 estable** entre 2 corridas a temp 0, atrapó la cara (ch04_img_06) y la fachada plana (ch05_img_05) que la geometría dejaba pasar. Veredictos cacheados en `zoom_verdicts.json` (determinismo entre re-animaciones por construcción). |

---

**Mantenimiento:** cuando descubras algo nuevo, agregalo a la sección del modelo correspondiente o a §4 si es transversal. Registrá el cambio en §5. Nunca rehacer el archivo — siempre crecer.
