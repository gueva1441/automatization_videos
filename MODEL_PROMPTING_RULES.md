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

## §1bis KLING o3 (image generation — motor base del canal)

**Modelo activo:** `fal-ai/kling-image/o3/text-to-image` (SYNC, `fal.run`). Ganó el gate B73-1
(probe cap4 Charleston, lab v6) como motor de imagen base: pasa en ejecución/horca donde Flux
devolvía 422, con framing implícito + filtro CAC interno. **Flux 2 Pro (§1) queda como fallback**
(`api.image_engine="flux"`); el dispatch vive en `m03_visual._render_prompts_flux` y en el append
de `assign_visual_prompts` (bake chat 80, path flux caps 2-6).

**Diferencias estructurales vs Flux:**
- Prompt **generativo** (el LLM escribe la escena de cero, NO "rewrite"), PROSA densa, **80-300
  palabras** (no el 30-80 de Flux). El aspecto NUNCA va en el texto ("wide horizontal composition",
  nunca "16:9").
- El LLM emite además `shot_scale` ∈ {extreme_wide, wide, medium, close, detail} y `light_mode` ∈
  {night, day, golden}.
- **Camino B (grano determinístico):** el LLM termina la escena SIN tail de estilo/grano; el harness
  **apendiza** un tail dialed por `(light_mode, shot_scale)` (`anti_plastic_dial` → `pick_tail`). En el
  path Kling ese tail **reemplaza** al `ancla_global` del nicho (apendizar ambos = doble textura).

**Las 12 reglas (`SYSTEM_INSTRUCTION_VISUAL_KLING`, misma numeración que el código):**
1. **Etnia por defecto** = la local del GEO, integrada al sujeto al inicio, period-correct; otra solo si
   la narración nombra al sujeto como extranjero. Cara al frente en R1.
2. **Solo descripciones positivas** (Kling no tiene negative prompt): describir lo que se quiere ver;
   superficies sin texto = lisas/gastadas.
3. **Sin nombres propios, sin texto legible:** describir por apariencia física (etnia+edad+ropa+era),
   nunca por rol pelado ni nombre (ni el del protagonista). Fechas → descriptores de era. Kling
   alucina texto: superficies planas/desgastadas.
4. **Era dura, anti-medieval:** marcador temporal explícito en CADA prompt (ropa/materiales/herrería/
   arquitectura de la década); no derivar a castillo/mazmorra genérico; afirmar el período, no nombrar
   los estilos prohibidos.
5. **Techo de monetización + aparato de matar:** mostrar literal lo que dice el anchor (cadalso / fila
   de sogas VACÍAS a la escala que implica; muro de sangre seca) PERO nunca cuerpos sin vida, ahorcados
   visibles, sangre fresca, mutilación, ni el momento del daño. Terror = escala+luz+sogas vacías+caras
   vivas cargadas. Si el sujeto sería el mecanismo y no hay beat de ejecución → espacio cargado vacío.
6. **Traducción física de metáforas:** lo indibujable ("sensación de pavor") → la materia física
   subyacente (un resplandor rojizo, ojos hundidos), nunca la palabra abstracta.
7. **Shot scale — el WIDE domina (16:9):** abrir cada prompt enunciando la escala. DEFAULT wide/extreme
   wide para lugar/arquitectura/evento masivo/aftermath/paisaje; medium/close SOLO para una emoción
   humana o un detalle de textura. PROHIBIDO que un cap entero sea medium/close.
8. **Retención por rank:** R1 = pico/héroe (acción específica, ojos/emoción). R2 = momento de ACCIÓN
   (dinámico). R3 = atmósfera/arquitectura con UN punto focal cargado (nunca placa vacía). Textura densa.
9. **Un dueño por motivo-firma (cero repetición):** se escribe el cap junto → coordinar ángulo/escala/
   sujeto; cualquier imagen-firma (aparato de ejecución, muro de sangre) la lleva EXACTAMENTE UN beat
   (el que narra el acto). Si un anchor solo REFERENCIA la ejecución por su consecuencia → CERO
   cadalso/soga en ninguna parte; elegir otro sujeto concreto.
10. **Vestir/ubicar por la narración, no por cliché:** mostrar al sujeto en el estado que narra ESTE
    beat (libre y digno en su oficio de día; acusado en interior tenso; preso con ropa tosca de época).
    ANTI-ANACRONISMO duro: uniformes a rayas PROHIBIDOS; solo ropa lisa de la década.
11. **El momento exacto del anchor, no el aftermath:** dibujar el instante que narra; calma-antes =
    la calma viva justo antes (golden-hour, con UN indicio mínimo de fondo); desastre-en-curso = el
    evento con profundidad; nunca el aftermath frío. `light_mode` casa con el momento.
12. **Luz/hora por coherencia de evento:** beats del MISMO evento comparten una luz. `light_mode`:
    night = penumbra murky; day = luz natural de época (vida libre, digna); golden = golden-hour viva
    de un beat calma-antes.

> **Etiquetas (decisión chat 79 D1):** m03 escribe el cap entero junto → NO hay clasificador/pasito
> previo de flags. `compute_flags` del lab NO se porta. 3 etiquetas se vuelven reglas escritas
> (no-repetir-motivo / vestir-según-narración / momento-exacto); la 4ª (ejecución) se le confía a la
> IA, con la revisión humana antes de publicar como red de seguridad.

> **Matiz chat-19 (anti-pánico para futuros chats):** chat 19 dijo "Python ya no concatena nada
> post-LLM", pero el `ancla_global` SIEMPRE se concatenó en el append del flux branch de
> `assign_visual_prompts`. El Camino B **extiende ESE mecanismo existente** (el tail dialed reemplaza al
> ancla en el path Kling); NO reabre el catálogo `art_profiles`, NO re-enciende `_stitch_zone2`
> (sigue no-op).

**§Veo-i2v (path veo bajo Kling, caps 1,7 — bake chat 81):** la doctrina Kling también aplica a los
caps veo, con esta forma:
- **`image_prompt`** (el first-frame que Veo anima i2v) → prosa densa Kling **SIN tail de grano**: Veo
  re-encodea/regenera temporalmente el frame y el grano analógico pesado dispara boil/crawl. Si un MP4
  real saliera plástico en gancho/outro, se evalúa ahí un tail liviano solo-paleta, con evidencia (B71-3).
- **`supplemental_image_prompts[]`** (stills puros DepthFlow = **caso flux**) → **tail dialed completo**
  (emiten `shot_scale`+`light_mode`, el harness apendiza el tail).
- **`video_prompt`** = §2 Veo, **intacto** (motion, no imagen Kling; no recibe `shot_scale`/`light_mode`).

La doctrina de imagen viene del **system** (`SYSTEM_INSTRUCTION_VISUAL_KLING`); el **user-prompt** veo
dropea `_build_rules_block` + `_VEO_EXAMPLES` + `_VEO_IMG_VIDEO_SUBJECT_SPEC` (conflicto de longitud:
Kling words vs Flux chars + AP3) y conserva `topic_block` + `visual_canon_block` +
`_VEO_VIDEO_PROMPT_STRUCT` (motion) + anchors. El swap del system es lo que mata la **fuga vertical** del
`SYSTEM_INSTRUCTION_VISUAL`. Dispatch global por `api.image_engine` (all-or-nothing: nunca mezcla motores
en un video); Flux fallback byte-idéntico. `_validate_veo_kling_cap` es hermano de `_validate_veo_cap`
(este queda intacto).

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
| 2026-06-17 | 66 | **R4 aplicada a los 6 módulos del motor que llamaban Gemini SIN `response_schema`** (m01a, m01b ×2, m02_5, m05, m06, m07) — cada uno define su schema (dict, patrón m03 `_xxx_schema()`) derivado de su validador existente y lo pasa a `call_flash_json`. + **resiliencia centralizada en `gemini_helpers`**: `_parse_with_retry` re-llama (generación fresca) hasta 3× si el parseo falla, dumpea+propaga solo en el fallo final (mismo mensaje de error). | Crash en vivo (chat 66): m01a recibió de Gemini comillas dobles SIN escapar en un bullet (`"Estancia "aterradora""`) → `json.loads` reventó y tumbó la corrida. Dos raíces: (1) sin schema, el mime-type JSON no garantiza el escape (R4 incumplido en 6 módulos); (2) ningún punto reintentaba un fallo de parseo. Schema mata la clase "comillas sin escapar" en la fuente; el retry centralizado es el piso de seguridad para los 6 de una. Labs read-only por módulo (assert estructural schema↔validador) + lab de resiliencia del helper; suite 49/49 verde, 0 regresiones (m03/m09 que ya usaban schema, estrictamente más robustos). |
| 2026-06-(67→78) | 67-78 | **Línea de probes Kling o3** (labs gitignored, `_lab_kling_cap4_probe.py`): Kling elegido como motor de imagen base (gate B73-1 PASS, probe cap4 Charleston) sobre Flux; tails anti-plástico dialed por `shot_scale`+`light_mode` (v6 FIX1-4: cara expuesta de noche, día digno, golden calma-antes), grano como Camino B (apendizado por el harness, no por el LLM). **EJE 1 (chats 77-78):** canal a 16:9 1440p (2560×1440) + dispatch Flux↔Kling en `asset_manager` (`api.image_engine`, default `kling`, SYNC `fal.run`). | Flux devolvía 422 en ejecución/horca; Kling pasa con framing implícito + filtro CAC interno. Resumen de la línea de probes que precede al bake. |
| 2026-06-19 | 80 | **Bake §Kling flux-only en m03** (path flux, caps 2-6): doctrina generativa Kling (`SYSTEM_INSTRUCTION_VISUAL_KLING`, dispatch por `api.image_engine`), schema +`shot_scale`/`light_mode`, `_validate_kling_cap` (carga ambos campos, budget 2500−tail), tail de grano dialed apendizado en el append branch de `assign_visual_prompts` (**reemplaza** `ancla_global` en el path Kling, Camino B). `compute_flags` NO portado (D1: m03 escribe el cap junto; la ejecución se le confía a la IA + revisión humana). **Flux fallback byte-idéntico** (`SYSTEM_INSTRUCTION_VISUAL`/`_validate_flux_cap`/append flux intactos; test byte-idéntico vs db2bae3 verde). | Flux 422 en ejecución; Kling pasa con framing implícito. Caps veo (1,7) = bake dedicado pendiente. |
| 2026-06-19 | 81 | **Bake §Kling path VEO en m03** (caps 1,7 — B80-1): espeja el bake flux sobre el bloque veo. `_veo_kling_step2_schema` (`shot_scale`/`light_mode` SOLO en supplementals, NO en `image_prompt`), `_build_veo_prompt_step2(is_kling)` (dropea `_build_rules_block`+`_VEO_EXAMPLES`+`_VEO_IMG_VIDEO_SUBJECT_SPEC`, conserva canon+`_VEO_VIDEO_PROMPT_STRUCT`+anchors), `_validate_veo_kling_cap` (hermano; `image_prompt` budget=2500 SIN tail, supp budget=2500−tail + carga campos, `video_prompt` longitud Veo), dispatch en `_render_prompts_veo`, append solo-supplementals. **(b) conservador:** `image_prompt` first-frame i2v SIN tail (Veo re-encodea→boil/crawl), supps con tail dialed. Ver §Veo-i2v. **Flux fallback byte-idéntico** (`_validate_veo_cap`/`_veo_step2_schema`/funciones flux intactas; test byte-idéntico vs 085d05c verde). | Cierra B70-1: el path veo queda bajo doctrina Kling; el swap del system mata la fuga vertical. Grano sobre el first-frame se valida en B71-3 (full-run), sin probe dedicado. |
| 2026-07-02 | 129 | m03 SEEDREAM slot NUEVO `foto_madre_ref` (routing, no-prosa): marca el objeto documentado que ESTE beat depicta como foco → asset_manager rutea /edit contra la foto madre en vez de t2i. Valores "__subject__" / nombre exacto de OBJETOS DOCUMENTADOS / "" (default cerrado, AP4). +key en response_schema (R4), definición-de-slot en la system-instruction (R1 atributo, R3 conceptual). El marcador es pedido-no-orden: el registry {ref→path} (emitido por m06 al contrato) + .exists() gatea; ref sin foto madre degrada a t2i. | Cierra la mitad USAR del object-lock (CONSUMO-B). La mitad GENERAR quedó cerrada en el 128 (foto madre en disco) pero ningún consumidor la usaba: todas las imágenes seguían saliendo t2i puro. El sujeto-objeto (submarino K-19) tenía referencia fuerte generada pero drift entre frames igual, porque el lock por IMAGEN-REF (/edit) no estaba cableado. |
| 2026-07-02 | 131 | object-lock a N objetos + CUTAWAY. **(A) 4e BLOQUE 4** (R1): criterio `anclado` FORMA→RECURRENCIA-por-centralidad ("el tema vuelve a este objeto foto tras foto → 'si', SIN importar silueta-vs-partes"; default "no" = aparece una vez / fondo / evidencia) + regla CONJUNTO-vs-PIEZA (varias partes de un objeto central → UNA entrada del objeto entero, no una por parte). Few-shot conceptual (R3, recurrencia vs aparición-única, sin nombres de temas). **(B) m03 slot `foto_madre_ref` STRING→ARRAY** (R4): hasta 2 refs por beat (default `[]`), para co-anclar 2 objetos en un cutaway. Regla del slot reescrita (R1). Cañería `asset_manager` 1→N: `image_urls` = lista de data-URIs; resolución pedido-no-orden (se queda con los refs cuyo path `.exists()`; ≥1 → /edit con esa lista, 0 → t2i; nunca crashea). | Extiende el object-lock del 129 (1 objeto/tema, 1 foto/imagen) a N objetos recurrentes + al cutaway (submarino+reactor en la MISMA imagen). El reactor driftea porque el criterio viejo lo juzgaba por FORMA (partes→"no"); ahora pasa a lockeable por RECURRENCIA (probe 130 verde). |
| 2026-07-03 | 131_fix_B | m03 REGLA NUEVA "ANCHOR HOLDS THE FORM" (R1): cuando un objeto está en `foto_madre_ref`, su forma la fija la referencia-imagen → los otros slots narran solo QUÉ hace y DÓNDE está, NUNCA su forma/pose/orientación/estructura (prohibido "suspended vertically", "encased in a frame", etc.). Recordatorio corto al final de `subject`/`action`/`props_detail`. Few-shot conceptual genérico (R3, sin nouns del topic). Aplica SOLO a objetos anclados; los no-anclados siguen descritos en full. | El cutaway del 131 ancló bien (4/4 /edit 2 refs) pero el reactor drifteaba en orientación+identidad (cilindro libre→encapsulado): la prosa (`action` narrando "colgar de la grúa") le ganaba al ancla. Espejo del lab 119: la forma la manda el ancla, no la prosa. |
| 2026-07-03 | 133 | **m03 (path seedream) — el canon deja de ser decoración y pasa a ser CONTRATO: 4 reglas nuevas de plantilla (cero lógica/schema).** (1) ESTADO POR BEAT + ancla respeta el estado: el slot `foto_madre_ref` gana la cláusula "STATE MUST MATCH THE BEAT" (si el beat narra al sujeto en una configuración física materialmente distinta — pre-reforma, en construcción, mutilado — la ref queda VACÍA y la prosa dibuja el estado desde `condition_evolution` at_event/later); + regla general "STATE BY BEAT" (todo prompt declara el estado del momento, sin mezclar dos en una imagen). (2) PERSONAS (paquete de 3): DEMOGRAFÍA OBLIGATORIA (etnia+edad+contextura de `demographics`/`appearance_canon`, explícita cuando el canon la tiene; "diverse group" no cumple) · GRUPOS (componer primero: mayoría de espaldas/plano amplio/silueta a contraluz con luz de borde — cara frontal en sombra negra NO es técnica; las 2-3 caras visibles CADA UNA distinta, nunca una receta para N) · ANTI-PARECIDOS (rasgos ordinarios de época; nunca nombre propio NI actores/celebridades/personajes de película). (3) CAMPOS DE ÉPOCA CONDICIONALES: cuando el beat toca el terreno de un campo, su material sale del canon (personas→`clothing`, interior→`interiors`, transporte/herramientas/luz→`vehicles_machinery`/`technology`); si no lo toca, no se fuerza. (4) `visual_reference_availability` ECHADO del bloque de contexto (meta-info de research, inútil para pintar). Framing POSITIVO, few-shots CONCEPTUALES, un término por concepto (MPR). **Alcance:** m03 solo soporta `image_engine='seedream'` (guard duro; flux/kling/veo-old removidos chat 117) → el "builder viejo" `_format_visual_canon_block` es dead code sin callers, NO se toca. Lint offline: `test_module_m03_reglas_133.py`. | Evidencia corrida 7dbf5ab2 (Old City Jail, 81 prompts): el canon viaja completo pero sin regla el LLM lo ignora — demographics "54th Massachusetts"/"slaves awaiting auction" → 0 y 3 huellas, salió "ethnically diverse prisoners" genérico; `condition_evolution` viajaba sin regla → beats de 1822 sin gobierno de estado; grupos con caras clonadas y caras frontales ahogadas en sombra negra (ilegibles). Patrón de la casa: donde sangró, regla dura. |
| 2026-07-03 | 132 | **`foto_madre.py` — motor GPT Image 2 (fal `openai/gpt-image-2`) para las fotos madre + prompt del SUJETO con el canon COMPLETO.** (a) La madre pasa de Seedream a GPT Image 2 (`MADRE_IMAGE_MODEL`, misma FAL_KEY/queue/poll; JPEG→PNG real vía `_ensure_real_png`; fallback al motor activo si GPT falla — la madre NUNCA bloquea el topic). Seedream/Kling **NO se tocan** para el resto del pipeline. (b) `_prompt_subject` pasa de 3 campos ("Isolated technical study …, seamless background") a TODAS las ramas del canon: `"Archival {década} documentary photograph"` (mata el look juguete/maqueta, medido en 3 tiradas) + materials/color/scale + `strictly avoid: {forbidden_anachronisms}` + el sujeto en su **medio natural** (a un objeto gigante su entorno es parte de la forma) a **3/4 a nivel de piso/mar** (el ángulo en que los caps lo consumen). `_prompt_prop` se queda AISLADO en fondo neutro (objeto chico) y solo suma época + prohibidos. `_clean()` corta el punto colgante de cada campo → sin `..` dobles. **Gate humano nuevo:** ADOPCIÓN de madre manual — si Omar deja un PNG en el destino (`foto_madre/<slug>.png`), paso0 lo adopta en vez de generar (sin UI nueva). | La calidad de la madre manda la del video entero (validado: costura GPT→Seedream 3/3, HANDOFF_132). Con Seedream + 3 campos la madre salía genérica/fuera de época. GPT Image 2 rinde el canon completo (live N=1 ec3d7c7f: semisumergible archival correcto, pontones vermellón, 3/4 a nivel de mar). Validación: `test_module_foto_madre_prompts.py` (offline, asserts de tokens + sin `..`) + live N=1 + test de adopción (motor no llamado, path persistido). |

---

**Mantenimiento:** cuando descubras algo nuevo, agregalo a la sección del modelo correspondiente o a §4 si es transversal. Registrá el cambio en §5. Nunca rehacer el archivo — siempre crecer.
