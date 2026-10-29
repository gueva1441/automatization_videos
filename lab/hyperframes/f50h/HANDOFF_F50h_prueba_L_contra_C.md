# HANDOFF F50h — prueba L contra C (armado del prompt de foto), en lab

Analista → CC · 2026-10-29 · rama `f11-guion-v4` · **no toca producción** · tope US$ 5,00 · dos tramos con PARADA en el medio.

## Por qué
La foto 1/2 de Wittenoom dio asiáticos con «Spanish migrant» y españoles con «Mediterranean features»: Seedream 5.0 Lite obedece rasgos visibles, no nacionalidades. Eso ya se arregló en F50g-A (el aspecto del grupo del canon va al prompt).

Queda la otra mitad: el prompt de hoy (L) mide entre 111 y 273 palabras. Pega 12 casilleros de Opus y repite cosas (pie vendado ×4, grano ×3, «cold» ×3). Además termina con una pila de palabras clave de estilo, y la guía de fal para 5.0 Lite dice que eso distrae al modelo: https://fal.ai/learn/tools/how-to-use-seedream-5-lite (2–4 oraciones, sujeto+acción → lugar → estilo al final, prosa natural).

La pregunta es si un armado más corto y en prosa (C), sacado de los mismos casilleros, cumple mejor. Lo que gane define el armado de F51 (regenerar Wittenoom antes del 2026-11-17).

## Orden re-derivado (skill handoff-analista §0)
- ¿Construye sobre código que se va a reemplazar? No. Solo lee `armar()` y sus helpers; no los cambia.
- ¿Alguna decisión de hoy cambia el orden? No: L/C → F50g-B → F51 (ENTRADA 2026-10-29c).

## Constantes
| valor | origen | quién |
|---|---|---|
| 20 fotos (lista de §Etapa 1) | cubren épocas 1943–2024, planos close/medium/wide/detail, 2 grupos, carteles, sin gente y las 3 de referencia de Omar; quedan fuera 6/3 y 7/11 (bug «Court», F50g-B) y 1/1 y 7/1 (cuadros Veo) | analista, aprobado por Omar 2026-10-29 02:03 |
| 3 variantes (L, C, C+ép) | diseño de la prueba | Omar 2026-10-29 02:01 |
| 2 fotos por prompt (`num_images` 2) | Seedream 5.0 Lite no acepta `seed` (`engine_profiles.py` l. 35 y 69) → con 1 foto el resultado es en parte suerte; mismo criterio que F46b | Omar 2026-10-29 02:03 |
| US$ 0,035 por foto | `engine_profiles.py` l. 79 (`cost_usd`) | proyecto |
| 120 fotos ≈ US$ 4,20 + visión ≈ US$ 0,30 → **tope US$ 5,00** | derivado + margen | Omar 2026-10-29 02:03 |
| «reason» de visión ≤ 12 palabras | formato de salida compacto para la tabla | analista (no afecta la medida) |
| Regla para elegir: gana la que Omar elige en más fotos; si hay empate, el puntaje de visión | — | Omar 2026-10-29 02:03 |

Ningún otro número entra. Los de fal («2–4 oraciones», «50+ palabras pierden atención al final») **no** son cortes: solo se reportan al lado.

## Módulos
- **Producción tocada:** ninguna.
- **Se leen sin cambiarlos:** `script_engine/m03_imagenes_v3.py` (`oracion`, `frase_cartel`, `_minuscula_media`, `_ANIO_O_DECADA`, `f8_backstop`, `armar` para L); `script_engine/m03_visual.py` (`_sacar_frases_con_texto`); `lab/hyperframes/f50g/rearmar.py` (`fotos`, `rearmar_una`); `lab/hyperframes/f49/f49_corridas.py` (`generar_1`, `hojas` como modelo); `script_engine/gfx_critic.py` (el cliente Gemini con `api.gemini_model` y `track_gemini_vision`).
- **Nuevos, todos en `lab/hyperframes/f50h/`:** `f50h.py` (una entrada por etapa: `--prompts`, `--fotos`, `--hojas`, `--vision`, `--tabla`), sus salidas y las fotos.

## Etapa 0 — anotar (US$ 0)
1. md5 de este handoff en el reporte.
2. `DECISIONES.md`, al final y tal cual:
   `- 2026-10-29 02:03 · **F50h:** prueba L contra C del prompt de foto en lab (20 fotos de Wittenoom × 3 armados × 2 fotos, Seedream 5.0 Lite, tope US$ 5): L = armar de hoy con aspecto; C = mismos casilleros sin mirada/objeto/paleta ni STYLE_TAIL, en el orden de la guía de fal con una oración de estilo en prosa de igual contenido; C+ép = C con estilo «como una foto real de ese año». Hoja ciega para Omar y puntaje por elemento con Gemini Flash; gana la que Omar elige en más fotos (empate → visión). Si gana C+ép, el estilo por época queda como decisión aparte (2026-10-28 10:34) · Omar · F50h`

## Etapa 1 — los 60 prompts en texto (US$ 0) → PARADA
Fotos (`cap/foto` del papel `lab/hyperframes/f50g/PAPEL_FOTOS_WITTENOOM.json`):
`1/2 1/3 1/4 2/9 2/11 2/15 3/3 3/6 3/10 4/1 4/11 4/12 5/1 5/8 5/13 5/16 6/5 6/15 7/7 7/9`

Casilleros: el `raw_llm_prompt` de cada foto en el `03_visual.json` vivo de Wittenoom (`123bbb64-…`), igual que `rearmar.py`; año = el `anio` guardado; `grupos` = los `people_groups` del topic, igual que `rearmar.py`.

- **L** = el `prompt` guardado en el papel f50g, tal cual (verificar que sea igual a `rearmar_una(..., grupos)`: 20/20).
- **C** = estas partes, en este orden, unidas con espacio y omitiendo las vacías:
  1. `oracion(subject)` + `oracion(action)`
  2. aspecto: `oracion(appearance)` de cada grupo de `people_group`, en el orden de Opus (igual que F50g-A)
  3. lugar + año: la misma regla que `armar` (si `setting` ya trae año o década, sin «, año»)
  4. cartel: `frase_cartel(text_in_image)` si `present` y hay `text`
  5. `oracion(lighting)` (**sin** `color_palette`)
  6. plano: `oracion(«<shot_scale> shot, <camera_angle>, <lens_technique>»)`, la misma construcción que `armar`
  7. estilo, una oración: `A grainy 35mm documentary photograph taken in {anio}, with muted colors and slight underexposure, in a dark-history realist style.`
  8. cierre: el mismo de `armar` (`aspect_ratio_text` del perfil + `NO_TEXT` si no hay cartel)

  No entran `gaze_interaction`, `props_detail`, `color_palette`, `style_head` ni `STYLE_TAIL`. Después, el **mismo** post-proceso que L: `_sin_negadas` sobre los casilleros de prosa antes de armar, `f8_backstop` y `_sacar_frases_con_texto` (como `rearmar_una`).
- **C+ép** = C con el estilo (parte 7) cambiado por: `A grainy documentary photograph taken in {anio}, with the film, color and tones a real photograph from {anio} would have, slightly underexposed, in a dark-history realist style.`

**Simulación del analista** (sin el post-proceso F8, sobre las 20): L mediana 167,5 palabras (máx. 273) → C mediana 131 (máx. 196), 8 a 10 oraciones. Ojo: C queda más corto pero **no** llega a lo de fal (2–4 oraciones). Se mide igual: el exceso viene de casilleros de Opus que se conservan (sujeto, acción, aspecto, lugar).

Ejemplo simulado (1/2, C, 159 palabras): «A Spanish migrant family posed for a portrait: a young olive-skinned miner in a pressed shirt with a bandaged foot, … The family stands squared to the camera for the portrait while the white-bandaged foot sticks out at the front of the group. Spanish Mediterranean people with olive to light skin, … Front of a corrugated sheet-metal house …, Wittenoom early 1960s. Hard cold overcast daylight, flat and shadowless. Wide shot, eye-level, like a 1960s box camera, deep depth of field, slight film softness at edges. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.»

**Salida de la etapa 1:** `PROMPTS_F50h.json` y `PROMPTS_F50h.md`. El `.md` lleva:
- una tabla por foto con palabras y oraciones de L / C / C+ép;
- los 3 prompts enteros de 1/2, 3/3 y 7/7;
- la verificación L = guardado (20/20).

Commit. **PARADA:** el analista revisa los 60 en texto y Omar da el OK antes de gastar.

## Etapa 2 — fotos (US$ ≤ 4,20), con el OK de Omar
- `generar_1` de F49 con `num_images` = 2: 60 llamadas, 120 png. Usar workers al máximo (llamadas independientes) y `cost_tracker` en cada una.
- Si el gasto acumulado llega a US$ 5,00, se corta y se reporta.
- **A ciegas:** cada foto se guarda como `fotos/<cap>_<foto>/<código>_<n>.png`. El `<código>` es una letra A/B/C asignada al azar **por foto**. La llave (`llave.json`, foto → {A: L|C|C+ép, …}) se escribe aparte, **no** se commitea hasta que Omar vote y no se nombra en el reporte.
- Un rechazo de contenido o un error se reintenta una vez; si vuelve a fallar, queda anotado en la tabla como hueco.

## Etapa 3 — hojas y visión (US$ ≤ 0,30) → PARADA
1. **Hojas** (`hojas/hoja_<cap>_<foto>.jpg`, una por foto): 6 celdas en 2 filas × 3 columnas (A, B, C; arriba la foto 1, abajo la 2). Rótulo de la celda = `A1`, `A2`…; arriba de la hoja, el ancla en español. Mismo estilo que `hojas()` de F49.
2. **Visión:** una llamada por png (120) con el cliente y el modelo de `gfx_critic.py`, en paralelo. El modelo no ve la variante, el prompt ni el nombre del archivo. Los elementos se arman por código desde los casilleros de esa foto (los mismos para las 3 variantes):
   - `subject` = el casillero `subject`
   - `action` = `action`
   - `appearance_<grupo>` = la `appearance` de cada grupo
   - `place` = `setting`
   - `era` = «Everything visible fits the year {anio}; none of these appear: {anachronism_blocklist del canon, unido con «; »}»
   - `lighting` = `lighting`
   - `shot` = «{shot_scale} shot, {camera_angle}»
   - `sign` = «A sign or label reads exactly "{text}" and is legible» (solo si hay cartel)
   - `no_text` = «No readable letters or words anywhere in the image» (solo si no hay cartel)

   El canon sale de `lab/hyperframes/f50f/canon_f50f.json` (`anachronism_blocklist`), el mismo del topic.

   Prompt exacto (no se cambia):
   ```
   You are checking one photograph against a list of elements it should show.
   For each element, answer "yes" if it is clearly shown, "no" if it is missing or contradicted, or "not_visible" if the framing makes it impossible to judge (for example, people seen only from behind for an appearance element).
   Judge only what you can see in the image. Do not guess.
   Elements:
   {una línea por elemento: "- <id>: <texto>"}
   Return only JSON, with no other text:
   {"elements":[{"id":"<id>","answer":"yes|no|not_visible","reason":"<at most 12 words>"}],"invented_text":true|false}
   "invented_text" is true if the image shows any letters or words other than the sign text listed above.
   ```
   Revisión del analista del prompt: la 7/7 de espaldas tiene que dar `appearance_banjima` = `not_visible`, no `no`; para eso está el ejemplo del «from behind». Un JSON que no parsea se pide una vez más; si falla de nuevo, queda como hueco.
3. **Puntaje** por png = sí / (sí + no); `not_visible` se cuenta aparte. `invented_text` en una foto con cartel solo cuenta si hay letras fuera del cartel.
4. **Salida:** `VISION_F50h.json` y `VISION_F50h.md`, con una tabla por foto y por letra (A/B/C, no por variante): puntaje medio de las 2 fotos, `not_visible` e `invented_text`, más el total por letra. La llave **no** se abre.

Commit (sin `llave.json`). **PARADA:** el analista revisa las hojas, Omar elige una letra por foto en el chat, y recién ahí CC abre la llave y escribe el resultado en una etapa 4 que se le pide aparte.

## Reglas fijas
- No tocar producción (`script_engine/`, `03_visual.json`, topics_db). No correr m03 con modelo ni F50g-B.
- Ni un número fuera de la tabla de constantes.
- Workers al máximo en fotos y visión.
- Commits por etapa; ESTADO_SESION y `F50h_REPORT.md` con la salida de cada etapa, lo abierto y el veredicto íntegro de `revisor-handoff`.
- Suite rápida y candado ch02 como siempre (no deberían moverse: no hay cambios de producción).
