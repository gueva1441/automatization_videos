# HANDOFF F57 — foto final en todos los clips + la voz entera del clip

Rama `f11-guion-v4` (main no se toca). Analista → CC. Decisiones de Omar: 2026-10-29 21:10 («todos»: foto final en todos los clips) y 21:17 (la foto final es un EDIT de la inicial). CC las anota en `DECISIONES.md` en el primer commit. Handoff auditado por subagente (13 correcciones aplicadas).

## Por qué
1. Hoy el clip arranca de una foto y el motor inventa a dónde va. Gemini Omni Flash 1.1 (G) y Kling 4.0 (K) aceptan `end_image_url` (`lab/hyperframes/f52/SCHEMAS_F52.md` l.18 K y l.72 G): el clip va de una foto a la otra.
2. Hoy el clip solo ve el `narration_anchor` (una frase que eligió el modelo). La voz de los 8 s es más (cap 1 de Wittenoom: el ancla es la oración 1; durante el clip la voz ya dice «Ese pie va a cerrar; lo que respira mientras…»). Foto final y movimiento salen de lo que de verdad se oye.
3. La foto final es un EDIT de la inicial (Seedream /edit con la inicial como referencia): dos fotos independientes cambian cara, ropa y luz y el motor «derrite» una en otra.

## Antes de escribir (método)
- ¿Construye sobre algo que ya decidimos reemplazar? No: G/K son el motor vigente (DECISIONES 14:43/15:00); m03 sigue. QA Studio (`_clipfix_core`) se rehace en la tanda (c); acá solo no se rompe.
- ¿Una decisión de hoy cambia el orden? No: orden de Omar 15:40, (a) primero.

## Constantes (todas existen; ninguna nueva)
| valor | origen | quién |
|---|---|---|
| 8 s de clip | `m03_visual.VEO_CLIP_DURATION_SEC` (l.840) | Omar (F53b) |
| ventana del clip en caracteres | `veo_zone_chars` que ya calcula `_process_one_cap` (m03 l.2181-2186: `int(VEO_CLIP_DURATION_SEC * chars_per_sec)`, recortado a `len−1`) | código existente |
| 2,4 palabras/s | `guion_v4.PALABRAS_POR_SEG` (l.1127, F27 medido) — SOLO en tests y en `clip_b.py`, porque la narración F56 todavía no tiene voz | existente |
| motores G → K, 1080p; G 0,15 US$/s, K 0,235 US$/s | DECISIONES 14:24 / 14:43 / 15:00; `engine_profiles.py` | Omar |
| parecido inicial/final (SSIM) | se mide y se informa; NO hay umbral ni freno | Omar 21:17 |

Seedream 5 Lite no acepta semilla (`engine_profiles.py:80` `accepts_seed=False`): no se pasa semilla a nada.

## Módulos que toca (6; los 2 últimos son solo paso de una clave)
1. `script_engine/m03_visual.py` (plan y prompts de fotos por cap): hoy guarda el `narration_anchor` del clip → además calcula y guarda `voz_clip`; el movimiento de m03 (`_seedream_video_prompt`) recibe `voz_clip` en lugar del ancla.
2. `script_engine/video_prompt.py` (Opus escribe el prompt del motor mirando la foto): hoy 1 foto → inicial + final; función nueva que escribe la instrucción de edit.
3. `asset_manager.py` (genera fotos y clips): hoy foto → clip → foto inicial → foto final (función nueva) → clip con las 2 fotos.
4. `engine_profiles.py` (perfiles de motor): `VideoProfile.campo_imagen_final`.
5. `script_engine/m06_assembler.py` (arma el guion que leen los assets; lista blanca de claves del cap Veo, l.99-110): suma `voz_clip`. `narration_anchor` se queda (lo usan QA Studio l.592 y m05).
6. `fase2a.py` (`_normalize_long`, l.131-145, lista blanca de claves): `narration_anchor` (l.144-145, entró en F53b solo para el clip) se REEMPLAZA por `voz_clip`.

## Parte A — código (US$ 0)
A0. Copia congelada para tests: `lab/hyperframes/f57/antes/01b_narration.json` = el `01b_narration.json` de `_steps/123bbb64-…` de hoy (md5 en el reporte). Ningún test nuevo lee `_steps`.

A1. **`voz_clip`** (m03, función pura `voz_del_clip(narracion, veo_position, ventana_chars) -> str`, sin LLM). `start` → las palabras (`\S+`) que EMPIEZAN antes del carácter `ventana_chars`; `end` → las que TERMINAN después de `len − ventana_chars`. Corte por palabra, sin agregar ni quitar nada. Ventana ≥ narración → la narración entera. `_process_one_cap` le pasa su `veo_zone_chars` ya recortado a `_render_prompts_seedream_veo`, que guarda `voz_clip` en el cap de `03_visual.json`. La zona de F51c (`_carve_veo_zones`) y el `veo_anchor` NO cambian: la foto inicial sigue saliendo del `veo_anchor` (regla del gancho de HANDOFF_142b).
   - Camino de la clave: m03 → `03_visual.json` → `m06_assembler` (l.99-110) → `fase2a._normalize_long` (l.131-145) → `chapter["voz_clip"]` en `_process_veo_chapter`. CC lista cada salto con archivo:línea.
   - Guion sin `voz_clip` (viejo): `_process_veo_chapter` PARA con mensaje claro («cap X sin voz_clip: correr m03 de nuevo»). No hay respaldo al ancla.
   - Simulación del analista, confirmada por el auditor (copia congelada, 2,4 palabras/s):
     | cap | pos | car. | palabras cap | ventana | palabras clip | voz_clip |
     |---|---|---|---|---|---|---|
     | 1 | start | 834 | 161 | 99 | 20 | «Un hombre joven posa para un retrato con el pie vendado. Ese pie va a cerrar; lo que respira mientras» |
     | 7 | end | 1266 | 216 | 112 | 21 | «respiró allí. Wittenoom ya no está en el mapa. ¿Qué respiró en diez meses que tardó casi treinta años en matarlo?» |

A2. **m03 movimiento**: `_seedream_video_prompt(image_prompt, voz_clip, label)`; el texto del usuario sigue con la etiqueta «NARRATOR OVER THIS CLIP», ahora con `voz_clip`. `_VEO_MOTION_SYSTEM` no se toca. (`test_module_f50b.py:161-164` sigue pasando.)

A3. **`engine_profiles.VideoProfile.campo_imagen_final`**: G = `end_image_url`, K = `end_image_url`. `_clip_payload` lo agrega solo si hay foto final (data-URI con el tipo leído de los bytes, como la inicial).

A4. **`video_prompt.py`** — tres textos:
   - `PEDIDO` (vigente, sin foto final): NO cambia, byte a byte; `test_module_f53b_video_prompt.py:56-58` sigue igual. Sin foto final recibe `voz_clip` bajo «NARRATION AT THIS MOMENT»: se acepta así (es la voz de ese momento).
   - **`PEDIDO_CON_FINAL`** (nuevo; con foto final), íntegro:
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
     `{segundos}` = `VEO_CLIP_DURATION_SEC` formateado con `:g` (el PEDIDO viejo trae el 8 escrito porque es copia de F52b; se deja así a propósito).
   - **`PEDIDO_FINAL`** (nuevo; instrucción de edit), íntegro:
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
   - `armar_body` y `escribir` reciben `foto_final=None`: con foto final → bloques `image` inicial, `image` final, texto de `PEDIDO_CON_FINAL`; sin → como hoy.
   - `escribir_final(foto, image_prompt, voz_clip, video_prompt)`: Opus `MODELO_CASILLEROS`, effort `ESFUERZO[MODELO_CASILLEROS]`, mismo bucle de reintentos que `escribir` (factorizado, no copiado).

A5. **`asset_manager.py`**:
   - Función nueva `foto_final_del_clip(foto_inicial, image_prompt, voz_clip, video_prompt, out_path) -> dict` (`path` o None, `ssim` o None, `instruccion`, `motivo`):
     1. si `out_path` ya existe → se reusa (no se paga de nuevo; solo se mide SSIM);
     2. `video_prompt.escribir_final(...)` → instrucción;
     3. `_generate_image_raw(instruccion, out_path, use_ultra, foto_madre_data_uris=[uri de la inicial con el tipo leído de los bytes])` → entra al `…/v5/lite/edit` (`asset_manager.py:335-341`; probado en `test_module_f8.py:129`);
     4. SSIM inicial vs final con el filtro `ssim` de ffmpeg (escalar la final al tamaño de la inicial si difiere);
     5. `ContentRejectedError` o error del edit → `path=None` y el motivo literal. No se suaviza nada.
   - `_process_veo_chapter`: foto inicial (como hoy) → `foto_final_del_clip(..., <cap>_img_<NN>_final.png)` → `_generate_clip(foto, vid_prompt, clip_path, image_prompt=..., ancla=chapter["voz_clip"], foto_final=<path o None>)`; si G rechaza, K con las mismas 2 fotos.
   - `clip_results` suma `foto_final`, `ssim`, `motivo_sin_final`; `path` y `status` no cambian (fase2b solo lee esos dos, `fase2b.py:1401-1415`).
   - El nombre `_final.png` no confunde a QA Studio: busca `{cap}_img_*.png` y toma el primero en orden (`qa_studio_server.py:595`); `ch01_img_01.png` va antes que `ch01_img_01_final.png`.
   - Se BORRA la lectura del ancla en `asset_manager.py:1157` (`chapter.get("narration_anchor")`).
   - `qa_studio_server._clipfix_core` (l.1111, 3 posicionales) sigue andando con `foto_final=None` por defecto; el falso de `test_qa_studio.py:479-492` no cambia.
   - Chascada 2: `_path_to_data_uri` con el tipo leído de los bytes (hoy fija `image/png`; Seedream entrega JPEG).

A6. Tests nuevos (`test_module_f57.py`, sin red, sobre la copia de A0 con la duración como parámetro): `voz_del_clip` start/end (los dos textos de la tabla) y borde (ventana ≥ narración); `PEDIDO` byte a byte igual; `PEDIDO_CON_FINAL` y `PEDIDO_FINAL` íntegros con `{segundos}`; `armar_body` con 2 imágenes en orden; payload con `end_image_url` en G y K y sin él cuando no hay final; `foto_final_del_clip` reusa un `_final.png` existente sin llamar a nada; edit rechazado → clip sin final y motivo; guion sin `voz_clip` → PARA; `_clipfix_core` sin final.
   - Se adapta: el falso `escribir` de `test_module_f53b_cadena.py:88` (firma cerrada) acepta `foto_final`.
   - Chascada 1: `test_module_f50c::test_f50c_a_fotos_testigo_de_wittenoom` pasa a una copia congelada: CC prueba `lab/hyperframes/f54/antes/` y `f55/antes/`, usa la que da «Eric Saint» en la foto 3 del cap 7 y lo informa; si ninguna, lo dice y no cambia el valor esperado.
   - Suite rápida + amplia + ch02 `f792f3d4…` + MAPA `--check` 0.
**Salida A (texto):** módulos antes → después; el camino de `voz_clip` con archivo:línea; los 3 PEDIDO enteros; los 2 `voz_clip` de la tabla calculados por el código nuevo; suites.

## Parte B — un clip real en lab (≈ US$ 1,5; +≈ US$ 1,9 si G rechaza y va K; no toca `_steps` ni `output/<topic>`)
`lab/hyperframes/f57/clip_b.py`, con `cost_tracker.start_video` / `end_video` como `lab/hyperframes/f53b/clip_real.py:46-53`, y las funciones de producción de la Parte A:
- Foto inicial: `lab/hyperframes/f52/fotos/cap01.png` (JPEG 2560×1440, hombre joven con el pie vendado: coincide con la oración 1 de la narración F56). `image_prompt`: `lab/hyperframes/f52/fotos/fotos_f52.json` → `cap01.prompt`.
- `voz_clip`: `voz_del_clip` sobre la copia de A0, cap 1, start, ventana con 2,4 palabras/s (solo acá).
- Movimiento: se REGENERA con `_seedream_video_prompt(image_prompt, voz_clip, …)` (prueba A2; el de `03_visual.json` se escribió con el ancla vieja). Se informan los dos, viejo y nuevo.
- Pasos: movimiento (Opus) → `foto_final_del_clip` (instrucción Opus → /edit → SSIM) → `_generate_clip` con las 2 fotos (Opus escribe el prompt del motor; G 1080p 8 s; si G rechaza, K).
- Cap 7 NO se corre: su foto de F52 es de la narración vieja.
**Salida B (texto + archivos en `lab/hyperframes/f57/`):** movimiento viejo y nuevo; instrucción de edit entera; prompt del motor entero; SSIM; motor que lo hizo y rechazos; gasto; las 2 fotos lado a lado; hoja de contactos del clip (cuadros 0, 2, 4, 6, 8 s).

## Reglas fijas
- Subagentes en paralelo donde se pueda (A1/A3/A4 independientes; A5 después; A6 al final).
- Cero cambios en los prompts de guion, escaleta, ficha y casilleros; los únicos textos de prompt nuevos son los de A4, tal cual están arriba.
- Nada de topes de dólares; el gasto se informa.
- Lo viejo se borra (ancla del clip en asset_manager y fase2a), no se apaga.
- Reporte `lab/hyperframes/f57/F57_REPORT.md` con «lo que queda abierto» entero y el veredicto de `revisor-handoff` íntegro.
- **PARADA** al terminar B. No se corre m03 de Wittenoom ni fotos de producción.

## Lo que el analista ya sabe que queda para después
- La narración F56 no tiene voz: el `sync_map` de Wittenoom es del 28-oct (cap 1: 32,96 s para 161 palabras = 4,9 palabras/s, imposible). m03 de producción (paso d) necesita la voz nueva primero. Se resuelve antes de (d).
- `_VEO_MOTION_SYSTEM` todavía nombra a «Google Veo» y un negative prompt que G/K no reciben: (c)/(d).
