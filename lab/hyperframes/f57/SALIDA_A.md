# F57 — Salida A (texto)

Handoff `lab/hyperframes/f57/HANDOFF_F57_foto_final_clips.md` (md5 `60ae081ae8b17197cc002e8ce6b3a169`, verificado). US$ 0. Copia congelada A0: `lab/hyperframes/f57/antes/01b_narration.json` (md5 `31efee2de1549b3cf7bc2afbb7715deb`, el `01b_narration.json` de `_steps/123bbb64-…` de hoy, la narración F56). Ningún test nuevo lee `_steps`.

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

## 2. El camino de `voz_clip`

1. `script_engine/m03_visual.py:2203-2207` — `_process_one_cap` calcula `veo_zone_chars = int(VEO_CLIP_DURATION_SEC * chars_per_sec)`, recortado a `[1, len−1]` (código existente).
2. `script_engine/m03_visual.py:2231` — se lo pasa a `_render_prompts_seedream_veo(…, veo_zone_chars)`.
3. `script_engine/m03_visual.py:1995` — `voz_clip = voz_del_clip(narration, veo_position, veo_zone_chars)`; `:2010` el movimiento la recibe; `:2024` `"voz_clip": voz_clip` en el cap.
4. `script_engine/m03_visual.py:2049` — `_persist` escribe `03_visual.json`.
5. `script_engine/m06_assembler.py:109` — `cap_out["voz_clip"] = vis.get("voz_clip", "")` (lista blanca del cap Veo).
6. `fase2a.py:146` — `_normalize_long`: `norm_ch["voz_clip"] = ch.get("voz_clip", "")`.
7. `asset_manager.py:1146-1148` — `_process_veo_chapter`: `voz_clip = chapter["voz_clip"]`; vacía → PARA.
8. `asset_manager.py:1209` y `:1215` — `foto_final_del_clip(…, voz_clip, …)` y `_generate_clip(…, ancla=voz_clip, foto_final=…)` → `video_prompt.escribir_final` / `escribir` (PEDIDO_FINAL / PEDIDO_CON_FINAL).

## 3. Los 3 PEDIDO enteros

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

## 4. Los 2 `voz_clip` de la tabla, calculados por el código nuevo

Copia A0, ventana como `_process_one_cap` con duración = palabras / 2,4 (`guion_v4.PALABRAS_POR_SEG`, solo en tests y `clip_b.py`):

| cap | pos | car. | palabras cap | ventana | palabras clip | voz_clip (código) |
|---|---|---|---|---|---|---|
| 1 | start | 834 | 161 | 99 | 20 | «Un hombre joven posa para un retrato con el pie vendado. Ese pie va a cerrar; lo que respira mientras» |
| 7 | end | 1266 | 216 | 112 | 21 | «respiró allí. Wittenoom ya no está en el mapa. ¿Qué respiró en diez meses que tardó casi treinta años en matarlo?» |

Coinciden con la simulación del analista, palabra por palabra. (`test_module_f57.py::test_voz_del_clip_los_dos_de_la_tabla`.)

## 5. Tests nuevos (`test_module_f57.py`, 20, sin red)

`voz_del_clip` start/end (los 2 de la tabla) y bordes (ventana ≥ narración, ventana 1, narración vacía); `_render_prompts_seedream_veo` guarda `voz_clip` y se la pasa al movimiento; el camino m06 → fase2a (`voz_clip` sí, `narration_anchor` no en fase2a); `PEDIDO` byte a byte; `PEDIDO_CON_FINAL` y `PEDIDO_FINAL` íntegros con `{segundos}`; `armar_body` con 2 imágenes en orden (y sin final, como hoy); `escribir_final` por el mismo `_llamar` (una sola copia del bucle); `campo_imagen_final` G y K; payload con `end_image_url` en G y K con las mismas 2 fotos si G rechaza, y sin él cuando no hay final; `_path_to_data_uri` por bytes; `foto_final_del_clip` reusa la existente sin llamar a nada / edit con la inicial de referencia / rechazo → sin final y motivo literal; `_process_veo_chapter` sin `voz_clip` PARA y ya no lee el ancla / foto final antes del clip y `clip_results` / sin final el clip sale con la inicial / `ch01_img_01.png` ordena antes que `_final`; `_clipfix_core` sigue con 3 posicionales y `foto_final=None`.

## 6. Chascada 1 (`test_module_f50c::test_f50c_a_fotos_testigo_de_wittenoom`)

Probadas las dos copias (sonda en seco, los 8 testigos de `TESTIGOS`). Con solo skeleton + narración congelados, **ninguna** arregla la foto 3/7 (`([], None)`): el arrastre de `m03_expediente.expedientes` no mira la narración sino `fuentes["parrafos"]`, que `mexp.fuentes` lee del `01b_narracion_v3.json` **vivo** (F55 D / F56 C); «Se llama Eric Saint» ya no está en ningún párrafo vivo. Congelando también los párrafos v3 de la copia:

| copia | 3/7 | 8 testigos |
|---|---|---|
| `f54/antes` (skeleton + narración + párrafos v3) | `(['Eric Saint'], 'arrastre')` | **8/8** |
| `f55/antes` (ídem) | `(['Eric Saint'], 'arrastre')` | 8/8 **de casualidad**: su narración ya es la reescrita de F55 D y ninguna ancla de F50c cae en sus párrafos; los testigos salen por el respaldo «párrafo del beat» |

Queda **`lab/hyperframes/f54/antes/`** (la narración anterior a F55 D, cuyas frases son las de las anclas congeladas de `f50f/antes/03_visual.json`). `expedientes_f50c.preparar(antes=None)`: con `antes`, lee skeleton, narración y párrafos v3 de la copia; sin `antes`, igual que hoy. El valor esperado de `TESTIGOS` no cambia. Ruido residual (no se tocó, hoy no cambia el resultado): escaleta, beats, ficha y `_perfil.json` siguen saliendo de `_steps` vivos; `f54/antes` no tiene ficha ni `_perfil.json`.

## 7. Suites

`bash lab/hyperframes/f41/verificar.sh f57` (logs en `lab/hyperframes/f41/f57/`): ch02 md5 **`f792f3d483a1fa42daed5f7f0e054f46`** (candado); rápida **53 passed**; amplia **1153 passed** + 4 fallas, las 4 previas (`m03_merge_timing` ×2, `gfx_lab` ×2); `test_module_f50c` vuelve a verde (15). `python lab/tools/mapa_modulos.py --check`: 158 archivos · **0 fallas**. Stickers de los 6 módulos actualizados.
