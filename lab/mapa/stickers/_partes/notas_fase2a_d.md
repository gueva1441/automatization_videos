# Notas de auditoría — zona fase2a, parte fase2a_d

Solo lo que vi leyendo los 9 archivos enteros. Sin propuestas. Los md5 de los 9 archivos coinciden con los de A al terminar.

## Falsos positivos en los hechos de A
- `script_engine/voz_utils.py:70` (`nombres`): la lista `prod` de A (evidence_pool, ficha_caso, pool_gate, research_v3, verify_quotes, evidence, guion_v3_reglas, guion_v4, m01a_*, m01b_guionista, m01d_particion, m05_narrative…) sale de `from script_engine import nombres`, que es el módulo `script_engine/nombres.py`, no esta función. Los llamadores reales de `voz_utils.nombres` son `m01e_pantalla.py:62` y `pantalla_filtros.py:16`. Por eso A marca `research` como etapa de voz_utils y es falso: voz_utils corre solo en `guion`, `guion_pantalla` y `render`.
- `script_engine/voz_utils.py:112` (`palabras`): mismo problema por nombre genérico; A lista guion_v4.py y nombres.py como llamadores y ahí es la palabra común, no la función.
- `fase2a.py:370` (`main`): A le asigna ~18 archivos y ~90 tests como llamadores porque todos tienen una función llamada `main`. El único que lanza fase2a es `run_pipeline.py:342`.
- `engine_profiles.py`: A le pone `research`, `guion`, `papel` y `packaging` por el cierre de imports (fase3.py, fase1.py). Los usos reales son `asset_manager.py:257,278,329` (assets) y `m03_visual.py:965` (voz, vía fase1_5).
- `foto_madre.py`: A le pone `research`, `guion`, `papel`; en el código solo corre en `voz` (fase1_5.py:647, paso0 dentro del bloque que arranca en normalizer_gate) y en `assets` (fase2a.py:337).
- `art_profiles.py`: A dice `tests: test_module_02.py, test_module_05.py` y 0 importadores; es cierto en producción, pero `test_module_02.py:22` hace `from art_profiles import VALID_PROFILES` y `script_engine/_archived/m02_profiles.py:50` también lo importa. Mi `estado` es el mismo (huérfano).

## Código muerto
- `script_engine/parallax_animator_v2.py:573` `build_hook_clip`: nadie la llama en todo el repo; está en `__all__` (línea 45) y su comentario sigue en `flow_profiles.py:32`.
- `script_engine/parallax_animator_v2.py:238` `_build_options`: la escala de intensidad por duración corta (líneas 253-257) ya no se usa en el camino de `build_animated_clip` (el docstring de las líneas 485-493 lo dice: siempre recibe 7.0); queda viva solo por `build_hook_clip` (que nadie llama) y por tests (test_chat55_flow_zoom.py, test_module_parallax_intensity_scale.py).
- `script_engine/parallax_animator_v2.py:300-301,337-338` `tiling_mode` e `introspect_tiling` (y el bloque `introspect_tiling` del runner, líneas 102-139): `build_animated_clip` solo pasa `tiling_mode=None` y fase2b no pasa nada; ninguna llamada de producción los activa. El comentario de la línea 143 los llama «DEPRECADO en chat 21».
- `script_engine/voz_utils.py:120` `munon`: ni producción ni tests; sus datos (`_ARTPREP`) sí se usan en otros lados.
- `art_profiles.py:155,172,210,255,414`: las cinco funciones sin llamador; también son código sin uso `PROFILE_GUIDE` (línea 462), `VEO_MOTION`, `NEGATIVE_PROMPT_GLOBAL` y los dos tuples de leakage, solo alcanzados por `_archived/m02_profiles.py` (que copia su propio `PROFILE_GUIDE`, línea 65, duplicado del de art_profiles).
- `art_config.py:19` `LEONARDO_SETTINGS`: nadie lo importa (`QA_sweep_flux_stale.md` ya lo marcó). Al importarlo leería `api.leonardo_model_id`, que sigue en config.
- `engine_profiles.py:71` `SEEDREAM_45_MODEL_ID`: se define y no se lee en ningún lado del repo (el comentario de las líneas 69-70 lo deja como ruta de vuelta).

## Dos lógicas para lo mismo / duplicados
- `engine_profiles.py:63,79` `cost_usd` (0.028 Kling, 0.035 Seedream) y `cost_tracker.py:229,247` (`kling_per_image` 0.028, `seedream_per_image` 0.035 desde `pipeline.costs`): el precio por imagen vive en dos sitios; `asset_manager.py` no lee `render.cost_usd` (grep: no aparece).
- `script_engine/voz_utils.py:333` `frases` y `:322`/`:340` `oraciones`/`oraciones_de_texto`: tres cortes de oraciones distintos (regex propia vs. `gfx_peak.sentences`); el docstring de `frases` dice que se movió de `gfx_question.sentences`.
- `foto_madre.py:84` hardcodea `{"width": 2560, "height": 1440}` y `engine_profiles.py:78` usa `pipeline.image_width/height`; `art_config.py:21-22` también usa `pipeline`. El comentario de foto_madre dice que son iguales a propósito, pero son dos fuentes del mismo número.
- `fase2a.py:333-339` repite la generación de foto madre que ya hace `fase1_5.py:647`; el comentario de las líneas 329-332 lo reconoce como «red de seguridad».
- `fase2a.py:206` `normalize_script` y `fase1_5.py:120` (`_build_audio_script`, comentario «mismo formato que fase2a._chapter_id»): dos constructores del mismo formato de capítulo.

## Comentarios que contradicen el código
- `engine_profiles.py:13-16` y `:43`: la «mitad PROMPT» está «DEFINIDA pero NADIE la lee todavía / INERTE hasta 3b», pero `script_engine/m03_visual.py:649-682,748` lee `profile.formula` y `profile.aspect_ratio_text`. `negations_in_text`, `style_tail` y `text_recipe` sí no los lee nadie fuera de tests.
- `engine_profiles.py:11`: «Mientras api.image_engine siga "kling"…» y el docstring dice «Cada motor (Kling, Seedream)»; el código usa `select_profile("seedream")` fijo en `asset_manager.py:257,278` y `m03_visual.py:965`.
- `fase2a.py:2-8` y `:280`: el docstring lista como paso 1 `audio_manager.process_script()` que genera `sync_map.json`, pero para LONG (el único tipo que lanza el form) el audio ya viene de fase1_5 y fase2a solo lee el sync_map (líneas 312-321).
- `fase2a.py:342`: el log dice «Assets... (imágenes Leonardo + clips Veo)» y el comentario de 125 usa `"leonardo"` como default de `render_engine`; Leonardo ya no es el motor (ver `QA_sweep_flux_stale.md`).
- `fase2a.py:24-28`: la NOTA habla de imports `from modules.xxx (legacy)` y de `art_config`, pero el archivo no importa ninguno de los dos.
- `fase2a.py:319`: el mensaje de error manda a `--from m01b`, que en `fase1_5.VALID_FROM_STEPS` rehace el guion completo; para recuperar solo el audio el paso sería `normalizer_gate`/`audio` (no lo verifiqué corriendo nada).
- `art_profiles.py:1-15` y `:264-280`: el encabezado dice «Refactor v2.2» y el bloque del chat 14 todavía dice «AGREGAR AL FINAL de art_profiles.py» / «Después de pegar este bloque» (instrucciones de parche ya aplicadas). `:226` cita `script_generator.sanitize_metadata_leak()`; `script_generator.py` no existe en la raíz.
- `script_engine/voz_datos.py:119`: el encabezado de sección dice «reloj en la esquina y palabra del pico (de gfx_peak, F36 §D)», pero solo hay `ticker_corner`; la palabra del pico no está en el archivo.
- `script_engine/voz_datos.py:106` `pico_plan`: recibe `words, scenes, moods, intensity, time_offset, freq` y no usa ninguno (solo `plan`, `ent`, `log`); el docstring cuenta que el sello propio del pico se borró.
- `script_engine/voz_utils.py:2-7`: el docstring dice que la usan «pantalla_filtros, pantalla_colocar, clima, voz_datos y m01e_pantalla»; en el código `pantalla_colocar` y `clima` solo la nombran en strings/comentarios (pantalla_colocar.py:96), y la importan además `pantalla_entrada`, `gfx_layer` y `gfx_realizador`.
- `script_engine/voz_utils.py:392-399` `narrador`: el docstring dice «para guiones v3»; F41 borró la cadena v3 y la voz v4 es la única.

## Números sin origen citado en el código
- `parallax_animator_v2.py:235` `_INTENSITY_FLOOR_FACTOR = 0.45` y `:681` `MID_RISK_MAX_INTENSITY = 0.85`: sin fuente (el 7.0 de `_DURATION_REFERENCE_S` sí dice «velocidad dulce validada img_03»); `:299,583` timeout 300 s, `:413` 180 s, `:561`/`:560` 180 y 120 s de FFmpeg, `-crf 18` (:548, :638), `DEPTHMAP_CACHE_SIZE_MB = 500` (:363) con razón dada pero sin medida.
- `parallax_animator_v2.py:93,270,272` `state.height = 0.05`, `isometric = 0.6`, `depth = 0.9`: «validada empíricamente chat 20/21»; sin DECISIONES citada.
- `foto_madre.py:91,105,112` timeouts 120/300/60 s; `:36-37` `_STYLE`: copiado de m03_visual (el comentario dice línea 149, no la verifiqué).
- `voz_datos.py:36,131` y `voz_utils.py:445`: la tolerancia 0.3 s («la tolerancia de pico_cap») y el `+0.3` del reloj aparecen escritos tres veces; `voz_datos.py:125` el `2.5` s de duración por defecto de un callout; `voz_datos.py:68,74` márgenes `i-4`, `i+8` («derivado»).
- `voz_utils.py:32` `range(100_000)` para el conversor palabras→número: el docstring dice 0-99 999, sin origen del tope; `:86-89` raíz de 5 letras; `:149` palabras de ≥ 4 letras.
- `engine_profiles.py:63,79`: costos con comentario («probado por Omar… $0.035») pero repetidos (ver arriba).
- `promote_palette_to_library_chat36.py:104` `NOMINAL_DURATION_MS = 60000` y los BPM/tonalidades de los prompts (líneas 46-102): registro del chat 36, sin ruta a DECISIONES.

## Rutas viejas / estado raro
- `promote_palette_to_library_chat36.py:143-174`: `audio_library/` hoy contiene pistas `*_f28_*` y subcarpetas `_paleta_f28`, `_retiradas` (no hay `*_curated`), por lo que el guard de la línea 146 no frenaría una corrida: movería los archivos sueltos de la library actual a `audio_library_backup_nyos_chat36/` y copiaría los 7 curados del chat 36. No lo ejecuté; es observación del código contra el listado del directorio.
- `fase2a.py:437-449`: rama sin `--topic` (lista blanca en `data/fase1_review.csv`, `_read_approved_topic_ids_from_csv`, `_should_skip`, `SKIP_STATUSES`) y rama SHORT (`_normalize_short`, `audio_process`, `--variation`): el form siempre pasa `--topic` y solo lanza LONG (`run_pipeline.py:342`); quedan alcanzables solo corriendo fase2a a mano (`_normalize_short` también por default `video_type="short"` de la línea 208 si el script no trae `video_type`).
- `fase2a.py:56` y `foto_madre.py:28-34`: importan `ContentRejectedError`, `_fal_headers`, `_flux_poll` (nombre «flux») de `asset_manager`; `_flux_poll` se usa para GPT Image 2 (foto_madre.py:105).
- `foto_madre.py` no importa ni usa `cost_tracker`: el gasto de GPT Image 2 (2560x1440, quality high, líneas 84-87) no se registra desde este módulo (coincide con la nota de memoria «Foto madre: costo fuera del bus»).
- `foto_madre.py:293` y `asset_manager`: el fallback llama `_generate_image_raw(prompt, dest, use_ultra=False, seed=None)`; `use_ultra` es un parámetro del motor Flux viejo.
- `art_profiles.py:244,247` y `:228-252`: prefijos de leakage con `leonardo,` y `flux,` / `ken_burns_zoom,` (motores y estilos del pasado) en un módulo huérfano.
- `art_profiles.py:306-308`: el comentario dice «Aplica solo a caps 1 y 7 (render_engine="veo"); los caps 2-6 (Flux)… depthflow en fase2b» —sigue la lógica Veo+Flux de chat 14, hoy el motor es Seedream.

## `estado_a` de A que no coincide
- Ninguno. Coinciden los 9: parallax vivo, art_profiles huérfano, fase2a vivo, voz_utils vivo, foto_madre vivo, promote solo herramienta manual, voz_datos vivo, engine_profiles vivo, art_config huérfano. Lo que difiere es la etapa de cada uno (ver «Falsos positivos»).

## Lo que no pude comprobar
- No leí `config.py` más allá de nombres de claves (`image_engine`, `fal_kling_model`, `leonardo_model_id`, valores omitidos), ni el contenido de `gfx_profiles`.
- No verifiqué el modelo exacto de Veo ni de ElevenLabs que usan `asset_manager`/`audio_manager`; en los stickers los nombro por su clave de config.
