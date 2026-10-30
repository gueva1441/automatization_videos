# F57 — foto final en todos los clips + la voz entera del clip · REPORTE

Handoff: `lab/hyperframes/f57/HANDOFF_F57_foto_final_clips.md` (md5 `60ae081ae8b17197cc002e8ce6b3a169`, verificado antes de tocar nada). Rama `f11-guion-v4`. Decisiones de Omar 21:10 y 21:17 en `DECISIONES.md` (primer commit). Sin tope de dólares (el gasto se informa). Cero cambios en prompts de guion/escaleta/ficha/casilleros: los únicos textos nuevos son los 3 de A4, copiados tal cual. Sin constantes nuevas. Lo viejo se borró (la lectura del ancla en `asset_manager` y en `fase2a`). No se corrió m03 de Wittenoom ni fotos de producción; `_steps` y `output/<topic>` sin tocar.

## Para Omar, en corto
- Cada clip va a tener ahora **dos fotos**: la inicial (como hoy) y una **final que es un edit de la inicial** (Seedream /edit con la inicial de referencia; la instrucción la escribe Opus a partir de la voz entera del clip y el movimiento aprobado). El motor (Gemini Omni Flash → Kling 4.0) recibe las dos y el clip va de una a la otra.
- El clip ya no mira solo el ancla (una frase): mira **las palabras que la voz dice en los 8 s** (`voz_clip`, calculado por código con la ventana que m03 ya usaba). Los dos ejemplos del handoff salen palabra por palabra.
- **Prueba real (Parte B):** cap 1 de Wittenoom, Gemini lo hizo sin rechazo, 8,00 s 1080p, SSIM inicial/final **0,78**. En la foto final el hombre es el mismo (cara, ropa, pose, luz) y se suma una bruma de polvo rojo bajo, como pide la voz; el clip termina en esa foto. **Gasto Parte B: US$ 1,34** (Parte A: US$ 0). Las fotos lado a lado y la hoja de contactos están en `lab/hyperframes/f57/clip/` (no se commitean mp4/png/jpg).
- **PARADA B.**

## Commits
| commit | qué |
|---|---|
| `f7aa5a8` | Etapa 0: DECISIONES 21:10 y 21:17, handoff, A0 (`antes/01b_narration.json`, md5 `31efee2d…`) |
| `bdbc6a5` | Parte A: 6 módulos, `test_module_f57.py` (20), chascada 1 (f50c → `f54/antes`), chascada 2 (`_path_to_data_uri`), `clip_b.py`, stickers, MAPA, suite, `SALIDA_A.md` |
| (este) | Parte B: `SALIDA_B.md`, `clip_b.json`, `clip_b.log`, reporte, ESTADO |

## Decisiones de CC
1. **Subagentes:** A4 (`video_prompt.py`) lo hizo un subagente en paralelo con A1/A3 (míos); la chascada 1 (f50c) otro subagente en paralelo con A6. Revisé los dos diffs antes de commitear.
2. **`voz_del_clip` devuelve el substring original** (`narracion[primera.start():última.end()]`), no las palabras unidas con espacio: así «sin agregar ni quitar nada» vale también para espacios dobles o saltos.
3. **`_path_to_data_uri` lee el tipo de los bytes** (chascada 2) y lo usan tanto `_clip_payload` (antes tenía su propia copia del data URI) como el `/edit` de la foto final. Consecuencia: una foto madre que no sea JPEG ni PNG ahora levanta `ValueError` (antes salía como `image/png` falso). No había ninguna en el código ni en los tests.
4. **`foto_final_del_clip` atrapa `ContentRejectedError` y cualquier otra excepción del edit** (red, 5xx agotados, ffmpeg): el handoff dice «ContentRejectedError o error del edit → path=None y el motivo literal»; el clip sale con la inicial y el motivo queda en `clip_results.motivo_sin_final`. `use_ultra` va como kwarg (inerte en Seedream, como en `_generate_image_raw`).
5. **SSIM con `scale2ref`** de ffmpeg (escala la final al tamaño de la inicial si difiere) y se lee `All:` de la salida; si ffmpeg no lo imprime, `ssim=None` (se informa, no frena).
6. **`escribir_final` y `escribir` comparten `_llamar`** (bucle de reintentos movido, no copiado); el subagente sumó `_body(contenido)` para que las dos armen el mismo dict de la API. Un test cuenta que el bucle está una sola vez.
7. **Chascada 1:** queda `lab/hyperframes/f54/antes/` y hubo que congelar también los párrafos v3 (`01b_narracion_v3.json`), no solo skeleton + narración, porque el arrastre del expediente busca el ancla en los párrafos que `mexp.fuentes` lee de `_steps`. `f55/antes` pasa pero de casualidad (ya es la narración reescrita). Valor esperado sin tocar.
8. **Parte B:** el movimiento se regeneró con Opus y la foto inicial es la de F52 (no se generó ninguna). `cost_tracker` muestra **2 llamadas `m03:motion`**: la primera cayó fuera de 120–700 caracteres y el bucle de `_seedream_video_prompt` reintentó (el que quedó tiene 636); es el comportamiento vigente, no F57.

## Salida A (texto; entera en `lab/hyperframes/f57/SALIDA_A.md`)

## 1. Módulos: antes → después

| módulo | antes | después |
|---|---|---|
| `script_engine/m03_visual.py` | guardaba el `narration_anchor` del clip; `_seedream_video_prompt(image_prompt, anchor, label)` recibía el ancla | **`voz_del_clip(narracion, veo_position, ventana_chars)`** (l.1936, pura, sin LLM): `start` → las palabras (`\S+`) que empiezan antes del carácter `ventana_chars`; `end` → las que terminan después de `len − ventana_chars`; corte por palabra, texto original tal cual; ventana ≥ narración → entera. `_render_prompts_seedream_veo` recibe `veo_zone_chars` (el que ya calcula `_process_one_cap`, recortado) y guarda **`voz_clip`** en el cap (l.2024); `_seedream_video_prompt(image_prompt, voz_clip, label)` recibe la voz del clip (misma etiqueta «NARRATOR OVER THIS CLIP»; `_VEO_MOTION_SYSTEM` sin tocar). `_carve_veo_zones` y `veo_anchor` NO cambian: la foto inicial sigue saliendo del ancla |
| `script_engine/video_prompt.py` | `PEDIDO` (1 foto); `escribir` con el bucle de reintentos adentro | `PEDIDO` byte a byte igual. **`PEDIDO_CON_FINAL`** (l.45) y **`PEDIDO_FINAL`** (l.60) íntegros; `{segundos}` = `VEO_CLIP_DURATION_SEC` con `:g`. `armar_pedido`/`armar_body`/`escribir` reciben `foto_final=None` (con foto final: bloques `image` inicial, `image` final, texto de PEDIDO_CON_FINAL; sin: como hoy). **`armar_body_final`** y **`escribir_final(foto, image_prompt, voz_clip, video_prompt)`** (l.183; Opus `MODELO_CASILLEROS`, effort `ESFUERZO[MODELO_CASILLEROS]`). El bucle de reintentos está una sola vez en **`_llamar(body, desc, post)`** (l.135), lo usan las dos |
| `asset_manager.py` | foto → clip; leía `chapter.get("narration_anchor")` (l.1157); `_path_to_data_uri` fijaba `image/png` | **`foto_final_del_clip(foto_inicial, image_prompt, voz_clip, video_prompt, out_path, *, use_ultra=False)`** (l.675): reusa `out_path` si existe (solo mide SSIM) → `escribir_final` → `_generate_image_raw(instruccion, out_path, use_ultra, foto_madre_data_uris=[uri de la inicial])` (entra al `/edit`) → **`_ssim`** (l.664, filtro `ssim` de ffmpeg, `scale2ref` si difieren) → `{path, ssim, instruccion, motivo}`; `ContentRejectedError`/error → `path None` y motivo literal. `_generate_clip(..., foto_final=None)` (l.702) pasa la foto final a `escribir` y al motor; `_call_clip_once`/`_clip_payload` (l.592) agregan `perfil.campo_imagen_final` solo si hay foto final. `_process_veo_chapter`: **PARA sin `voz_clip`** («cap X sin voz_clip: correr m03 de nuevo», l.1148; sin respaldo al ancla), foto inicial → `foto_final_del_clip(..., <cap>_img_<NN>_final.png)` → `_generate_clip(..., ancla=voz_clip, foto_final=…)`; `clip_results` suma `foto_final`, `ssim`, `motivo_sin_final` (`path`/`status` iguales). La lectura del ancla se BORRÓ. Chascada 2: `_path_to_data_uri` lee el tipo de los bytes (l.293) |
| `engine_profiles.py` | `VideoProfile` sin campo de foto final | **`VideoProfile.campo_imagen_final`** (l.124): G = `end_image_url` (l.145), K = `end_image_url` (l.161) |
| `script_engine/m06_assembler.py` | lista blanca del cap Veo sin `voz_clip` | suma `cap_out["voz_clip"]` (l.109); `narration_anchor` se queda (QA Studio l.592, m05) |
| `fase2a.py` | `norm_ch["narration_anchor"]` (F53b) | **reemplazado** por `norm_ch["voz_clip"]` (l.146) |

Fuera de los 6 módulos: `test_module_f53b_cadena.py:88` (el falso `escribir` acepta `foto_final`); `test_module_f50c.py` + `lab/hyperframes/f50c/expedientes_f50c.py` (chascada 1, ver §6); stickers de los 6 módulos y MAPA.

### 2. El camino de `voz_clip`

1. `script_engine/m03_visual.py:2203-2207` — `_process_one_cap` calcula `veo_zone_chars = int(VEO_CLIP_DURATION_SEC * chars_per_sec)`, recortado a `[1, len−1]` (código existente).
2. `script_engine/m03_visual.py:2231` — se lo pasa a `_render_prompts_seedream_veo(…, veo_zone_chars)`.
3. `script_engine/m03_visual.py:1995` — `voz_clip = voz_del_clip(narration, veo_position, veo_zone_chars)`; `:2010` el movimiento la recibe; `:2024` `"voz_clip": voz_clip` en el cap.
4. `script_engine/m03_visual.py:2049` — `_persist` escribe `03_visual.json`.
5. `script_engine/m06_assembler.py:109` — `cap_out["voz_clip"] = vis.get("voz_clip", "")` (lista blanca del cap Veo).
6. `fase2a.py:146` — `_normalize_long`: `norm_ch["voz_clip"] = ch.get("voz_clip", "")`.
7. `asset_manager.py:1146-1148` — `_process_veo_chapter`: `voz_clip = chapter["voz_clip"]`; vacía → PARA.
8. `asset_manager.py:1209` y `:1215` — `foto_final_del_clip(…, voz_clip, …)` y `_generate_clip(…, ancla=voz_clip, foto_final=…)` → `video_prompt.escribir_final` / `escribir` (PEDIDO_FINAL / PEDIDO_CON_FINAL).

### 3. Los 3 PEDIDO enteros

**`PEDIDO`** (vigente, sin foto final; sin cambios, byte a byte con `lab/hyperframes/f52/prompts_video.py`; sin foto final recibe `voz_clip` bajo «NARRATION AT THIS MOMENT», aceptado así):
```
You write the motion prompt for an image-to-video model. The still image is the first frame. Follow the model guide below exactly; it decides structure, length and closing lines.
MODEL GUIDE:
{ficha}
FIRST FRAME: the attached image. Where it differs from the still image prompt (framing, pose, what is visible), describe the motion from the image as it is.
STILL IMAGE PROMPT (what the first frame was asked to show):
{prompt_foto}
NARRATION AT THIS MOMENT:
{ancla}
APPROVED MOTION (keep its intent, rewrite it for this model):
{video_prompt_vivo}
Clip length: 8 seconds, one continuous shot, no cuts, no dialogue, no music, no on-screen text.
Return only the prompt text.
```

**`PEDIDO_CON_FINAL`** (nuevo; con foto final):
```
You write the motion prompt for an image-to-video model. The first attached image is the first frame and the second attached image is the last frame: the shot goes from one to the other. Follow the model guide below exactly; it decides structure, length and closing lines.
MODEL GUIDE:
{ficha}
FIRST FRAME: the first attached image. Where it differs from the still image prompt (framing, pose, what is visible), describe the motion from the image as it is.
LAST FRAME: the second attached image. Describe the motion that ends exactly on it.
STILL IMAGE PROMPT (what the first frame was asked to show):
{prompt_foto}
NARRATION DURING THE CLIP (Spanish):
{ancla}
APPROVED MOTION (keep its intent, rewrite it for this model):
{video_prompt_vivo}
Clip length: {segundos} seconds, one continuous shot, no cuts, no dialogue, no music, no on-screen text.
Return only the prompt text.
```

**`PEDIDO_FINAL`** (nuevo; instrucción de edit):
```
You write an edit instruction for an image-editing model. The attached image is the first frame of a {segundos}-second continuous documentary shot. Write the instruction that turns it into the last frame of that same shot.
The last frame keeps the same place, the same people with the same faces, bodies and clothes, the same light and the same photographic style; it changes only what changes during those seconds, following the narration and the approved motion.
STILL IMAGE PROMPT (what the first frame was asked to show):
{prompt_foto}
NARRATION DURING THE SHOT (Spanish; the last frame shows the moment at its end):
{voz_clip}
APPROVED MOTION (where the camera ends up):
{video_prompt_vivo}
Return only the edit instruction: one paragraph of plain English prose describing the last frame.
```
`{segundos}` → `8` (`VEO_CLIP_DURATION_SEC = 8.0`, `:g`).

### 4. Los 2 `voz_clip` de la tabla, calculados por el código nuevo

Copia A0, ventana como `_process_one_cap` con duración = palabras / 2,4 (`guion_v4.PALABRAS_POR_SEG`, solo en tests y `clip_b.py`):

| cap | pos | car. | palabras cap | ventana | palabras clip | voz_clip (código) |
|---|---|---|---|---|---|---|
| 1 | start | 834 | 161 | 99 | 20 | «Un hombre joven posa para un retrato con el pie vendado. Ese pie va a cerrar; lo que respira mientras» |
| 7 | end | 1266 | 216 | 112 | 21 | «respiró allí. Wittenoom ya no está en el mapa. ¿Qué respiró en diez meses que tardó casi treinta años en matarlo?» |

Coinciden con la simulación del analista, palabra por palabra. (`test_module_f57.py::test_voz_del_clip_los_dos_de_la_tabla`.)

### 5. Tests nuevos (`test_module_f57.py`, 20, sin red)

`voz_del_clip` start/end (los 2 de la tabla) y bordes (ventana ≥ narración, ventana 1, narración vacía); `_render_prompts_seedream_veo` guarda `voz_clip` y se la pasa al movimiento; el camino m06 → fase2a (`voz_clip` sí, `narration_anchor` no en fase2a); `PEDIDO` byte a byte; `PEDIDO_CON_FINAL` y `PEDIDO_FINAL` íntegros con `{segundos}`; `armar_body` con 2 imágenes en orden (y sin final, como hoy); `escribir_final` por el mismo `_llamar` (una sola copia del bucle); `campo_imagen_final` G y K; payload con `end_image_url` en G y K con las mismas 2 fotos si G rechaza, y sin él cuando no hay final; `_path_to_data_uri` por bytes; `foto_final_del_clip` reusa la existente sin llamar a nada / edit con la inicial de referencia / rechazo → sin final y motivo literal; `_process_veo_chapter` sin `voz_clip` PARA y ya no lee el ancla / foto final antes del clip y `clip_results` / sin final el clip sale con la inicial / `ch01_img_01.png` ordena antes que `_final`; `_clipfix_core` sigue con 3 posicionales y `foto_final=None`.

### 6. Chascada 1 (`test_module_f50c::test_f50c_a_fotos_testigo_de_wittenoom`)

Probadas las dos copias (sonda en seco, los 8 testigos de `TESTIGOS`). Con solo skeleton + narración congelados, **ninguna** arregla la foto 3/7 (`([], None)`): el arrastre de `m03_expediente.expedientes` no mira la narración sino `fuentes["parrafos"]`, que `mexp.fuentes` lee del `01b_narracion_v3.json` **vivo** (F55 D / F56 C); «Se llama Eric Saint» ya no está en ningún párrafo vivo. Congelando también los párrafos v3 de la copia:

| copia | 3/7 | 8 testigos |
|---|---|---|
| `f54/antes` (skeleton + narración + párrafos v3) | `(['Eric Saint'], 'arrastre')` | **8/8** |
| `f55/antes` (ídem) | `(['Eric Saint'], 'arrastre')` | 8/8 **de casualidad**: su narración ya es la reescrita de F55 D y ninguna ancla de F50c cae en sus párrafos; los testigos salen por el respaldo «párrafo del beat» |

Queda **`lab/hyperframes/f54/antes/`** (la narración anterior a F55 D, cuyas frases son las de las anclas congeladas de `f50f/antes/03_visual.json`). `expedientes_f50c.preparar(antes=None)`: con `antes`, lee skeleton, narración y párrafos v3 de la copia; sin `antes`, igual que hoy. El valor esperado de `TESTIGOS` no cambia. Ruido residual (no se tocó, hoy no cambia el resultado): escaleta, beats, ficha y `_perfil.json` siguen saliendo de `_steps` vivos; `f54/antes` no tiene ficha ni `_perfil.json`.

### 7. Suites

`bash lab/hyperframes/f41/verificar.sh f57` (logs en `lab/hyperframes/f41/f57/`): ch02 md5 **`f792f3d483a1fa42daed5f7f0e054f46`** (candado); rápida **53 passed**; amplia **1153 passed** + 4 fallas, las 4 previas (`m03_merge_timing` ×2, `gfx_lab` ×2); `test_module_f50c` vuelve a verde (15). `python lab/tools/mapa_modulos.py --check`: 158 archivos · **0 fallas**. Stickers de los 6 módulos actualizados.


## Salida B (texto; entera en `lab/hyperframes/f57/SALIDA_B.md`; archivos en `lab/hyperframes/f57/clip/`)

Foto inicial: `lab\hyperframes\f52\fotos\cap01.png` (JPEG 2560×1440, F52). Narración: copia A0 (`lab/hyperframes/f57/antes/01b_narration.json`), cap 1, 834 caracteres, 161 palabras; ventana 99 caracteres (2,4 palabras/s, solo acá).

**voz_clip** (20 palabras): «Un hombre joven posa para un retrato con el pie vendado. Ese pie va a cerrar; lo que respira mientras»

Ancla vieja (03_visual.json vivo): «Un hombre joven posa para una foto con el pie envuelto en una venda blanca.»

### 1. Movimiento viejo y nuevo

**Viejo (03_visual.json, con el ancla):**

    A slow, somber documentary shot on grainy 35mm film from the early sixties, muted colors and slight underexposure. The camera makes a very slow push-in, starting on a medium shot of the young miner against the corrugated iron wall and ending slightly closer, the white bandaged foot still sharp in the lower frame. First, fine red dust drifts low across the ochre earth, then his short shirt sleeves stir faintly in a light breeze as he breathes slowly. Hard, cold midday light under a pale washed-out sky keeps short sharp shadows steady in the dusty yard. He stays in place, posed stiffly with his weight off the bandaged foot, face and body steady.

**Nuevo (`_seedream_video_prompt` con voz_clip):**

    A slow, somber documentary shot on grainy 35mm film, muted colors and slight underexposure. The camera holds a locked-off medium shot at eye level with a subtle drift, easing in slightly so the framing ends a touch tighter on the man and his bandaged foot. First, fine red dust lifts from the ochre earth and drifts across the yard, then the loose cloth of his shirt stirs faintly as he breathes slowly, chest rising and falling. Hard cold midday light under a pale washed-out sky keeps short sharp shadows against the grey corrugated iron wall. He stays in place, posed stiffly, face and body steady, weight held off the bandaged foot.

### 2. Instrucción de edit (foto final)

    Push the framing in slightly so it ends a touch tighter on the same young man, centered at eye level, with a little less of the corrugated wall and red yard visible at the edges. Keep his head near the top of the frame and his bandaged foot and boot still fully in view in the lower frame, with the white bandage sharp. Keep him exactly the same: same face and steady, unsmiling stare into the lens, same short dark hair, same lean build, and the same dust-stained tan shirt with rolled sleeves, open collar and two chest pockets. Keep the same dark, red-dusted trousers and worn boot. He holds the same stiff pose, arms hanging at his sides, weight kept off the bandaged foot, which rests lightly on its toes. Show his chest slightly risen mid-breath, with the loose shirt cloth gently shifted and a few soft folds moved across the front and pockets. Add a thin, low haze of fine red-ochre dust lifting from the ground and drifting sideways across the yard behind and around his legs and feet. The haze should slightly soften the base of the grey corrugated iron wall without hiding him. Keep the hard, cold midday light, the pale washed-out sky, the short sharp shadows on the red earth, and the grainy, muted, slightly underexposed 1962 35mm documentary look. Add no text, signage or labels.

Resultado: foto final lab\hyperframes\f57\clip\cap01_img_01_final.png · **SSIM inicial/final: 0.784829** (se informa; sin umbral) · motivo: None

### 3. Prompt del motor y motor que lo hizo

Motor: **gemini_omni_flash** · rechazos: ninguno

    Grainy 35mm documentary footage from 1962, muted colors, slight underexposure, somber and still. A young Spanish miner stands stiffly in the red-ochre yard of a company house, posed for a family photograph, weight held off his white-bandaged foot, staring into the lens. Keep his face, short dark hair, dust-stained short-sleeved shirt with rolled sleeves, dark dusty trousers, worn boot, bright white bandage, grey corrugated iron wall and pale washed-out sky exactly as in the image.

Locked-off medium shot at eye level with a very slow push-in, ending a touch tighter on the man and his bandaged foot. Fine red dust lifts from the ground and drifts across the yard behind him, building into a soft haze along the base of the wall. His shirt stirs faintly as he breathes slowly, chest rising and falling. He does not move from his pose. Hard cold midday light holds short sharp shadows.

Sound: dry wind across the yard, the faint hiss of blowing dust, a distant tick of corrugated iron in the heat. No dialogue, no music.

One continuous 8-second shot, no cuts, no on-screen text, no captions.

Clip: lab\hyperframes\f57\clip\cap01_clip_01.mp4 · {"segundos": 8.0, "ancho": 1920, "alto": 1080, "audio": false, "usd": 1.2, "foto_final": "cap01_img_01_final.png"}

### 4. Gasto

| servicio | descripción | US$ |
|---|---|---|
| Anthropic claude-opus-5-5 | m03:motion | 0.00981 |
| Anthropic claude-opus-5-5 | m03:motion | 0.00924 |
| Anthropic claude-opus-5-5 | cap01_img_01_final: instruccion | 0.03354 |
| fal.ai Seedream 5.0 Lite (edit) | cap01_img_01_final: Push the framing in slightly so it ends a touch tighter on t... | 0.035 |
| Anthropic claude-opus-5-5 | cap01_clip_01: prompt gemini_omni_flash | 0.05327 |
| fal google/gemini-omni-flash/v1.1/image-to-video | cap01_clip_01: gemini_omni_flash | 1.2 |

**Total US$ 1.3409** · 156.5 s de reloj.

### 5. Archivos

- `clip/cap01_img_01.png` (inicial, copia de F52) · `clip/cap01_img_01_final.png` (final)
- `clip/lado_a_lado.jpg` (las 2 fotos lado a lado) · `clip/hoja_contactos.jpg` (cuadros 0, 2, 4, 6, 8 s)
- `clip/cap01_clip_01.mp4` · `clip_b.json` (todo, con el log del clip y ffprobe)

Sin errores.

Lo que se ve (CC, mirando `lado_a_lado.jpg` y `hoja_contactos.jpg`): la foto final es el mismo hombre con la misma cara, pelo, camisa manchada, pantalón, bota y venda, misma pared y luz; cambia una bruma baja de polvo rojo que cruza el patio detrás de las piernas y el encuadre apenas más cerrado. En el clip el polvo se levanta a partir de los 4 s y el último cuadro coincide con la foto final; el hombre no se mueve de la pose. Duración 8,000 s, 1920×1080, sin audio.

## Suites
Parte A (`bash lab/hyperframes/f41/verificar.sh f57`, sobre el árbol de `bdbc6a5`): ch02 md5 **`f792f3d483a1fa42daed5f7f0e054f46`**; rápida **53 passed**; amplia **1153 passed** + 4 fallas previas (`m03_merge_timing` ×2, `gfx_lab` ×2); `test_module_f50c` vuelve a verde. `mapa_modulos.py --check`: 158 · 0 fallas. La Parte B no toca código.

## Lo que queda abierto
1. **La narración F56 no tiene voz** (lo sabe el analista): en producción la ventana sale del `sync_map` real; el de Wittenoom es del 28-oct (cap 1: 4,9 palabras/s, imposible). m03 de producción (paso d) necesita la voz nueva primero. `clip_b.py` y los tests usan 2,4 palabras/s solo por eso.
2. **`_VEO_MOTION_SYSTEM`** sigue nombrando «Google Veo» y un negative prompt que G/K no reciben: tandas (c)/(d).
3. **QA Studio `_clipfix_core`** regenera el clip sin foto final (`generate_veo_fn(first_frame, video_prompt, out_clip)` → `foto_final=None`): se rehace en la tanda (c). Sigue leyendo `narration_anchor` del guion canónico (m06 lo conserva).
4. **SSIM 0,78 sin umbral** (Omar 21:17). Decide Omar si el nivel de cambio de esta foto final (bruma de polvo, encuadre apenas más cerrado) es lo que quiere o si la instrucción debe pedir más/menos.
5. **Dos llamadas de movimiento** en B (reintento por largo del bucle vigente de `_seedream_video_prompt`): US$ 0,01 de más por clip cuando pasa; no es de F57.
6. **`_path_to_data_uri` con un formato que no sea JPEG/PNG levanta `ValueError`** (decisión 3): antes mentía `image/png`.
7. **f50c** sigue leyendo escaleta, beats, ficha y `_perfil.json` de `_steps` vivos (hoy no cambia el resultado; `f54/antes` no tiene ficha ni perfil).
8. **`clip/` no va a git** (mp4/png/jpg, como f53b/clip): quedan en disco en `lab/hyperframes/f57/clip/`.
9. **PARADA B.** Nada de Wittenoom pasa a fotos ni a m03 sin Omar.

## Veredicto de revisor-handoff (íntegro)

(se pega abajo)
