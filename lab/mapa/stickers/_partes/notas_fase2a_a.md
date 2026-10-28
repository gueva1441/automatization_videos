# Notas de auditoría — zona fase2a, parte fase2a_a

Los 6 archivos se leyeron enteros (m03_visual.py 2747 líneas en 4 tramos). Los md5 de los 6 coinciden con los de A al terminar.

## Estado y etapas distintas de lo que marca A

- `script_engine/vision_validator.py` (todo el archivo): A lo marca vivo en 6 etapas por la cadena de imports. En realidad `validate_image` y `build_corrected_prompt` solo se llaman si `ENABLE_VISION_VALIDATOR` (asset_manager.py:68) es True, y la constante está fija en False; el módulo se importa (asset_manager.py:52) pero nunca ejecuta. Lo dejé como `vivo` por el import y lo expliqué en `estado_prueba`; el estado real es dormido por constante.
- `script_engine/m03_visual.py`: A le da research, guion, papel, voz, assets, packaging. Lo que corre de verdad es `assign_visual_prompts` en el tramo audio -> m07 -> m03 de `fase1_5.py` (línea 632), o sea etapa `voz` (el `--from normalizer_gate`). Las otras etapas solo lo alcanzan por import. packaging lo carga porque `m09_packaging.py:40` importa sus constantes DOCTRINE_*; ahí no corre ninguna función de m03.
- `script_engine/m03_imagenes_v3.py`: ídem, solo `voz`.
- `script_engine/image_grade.py`: A lo marca en 6 etapas; corre solo en `assets` (asset_manager.py:1321 -> `_apply_grade`).
- `depth_probe.py` y `zoom_judge.py`: A dice fondos, guion_pantalla, aprobar_guion, render. `aprobar_guion` no los toca (fase2b.py:3719 sale antes de procesar el video). `fondos`: puerta de zoom (fase2b.py:3300, solo sin `--reuse-visuals`). `guion_pantalla` y `render`: `_route_safe` (fase2b.py:3376) corre con `--gfx` (el plan-only lo activa) y vuelve a llamar a `judge_candidates` sobre imágenes con persona (fase2b.py:2617), o sea llamadas de visión en esas dos etapas también.

## Código muerto o sin uso

- `m03_visual.py:1368` `_format_bullets`: sin ningún llamador en el repo.
- `m03_visual.py:1374` `_format_visual_canon_block`: sin llamadores; el docstring de `_format_seedream_canon_block` (línea 367) lo llama "espejo"; `test_module_m03_reglas_133.py:10` lo declara "dead code" y cuenta su texto en el fuente.
- `m03_visual.py:1895` `_validate_no_text_leakage`: solo la usa `test_module_03_text_leakage_casing.py` (que además hace `import m03_visual` sin el prefijo `script_engine`). El camino real usa `_find_text_leakage` (línea 1972), que duplica sus patrones y pasadas a propósito (comentario en 1969).
- `m03_visual.py:112` `VALID_LIGHT_MODES`, `:1237` `VALID_RANKS`, `:1190` `FLUX_CHAPTERS`: constantes definidas y nunca leídas en producción. `MAX_RETRY_ATTEMPTS` (1239) solo se usa como default de `_call_with_validation_retry`.
- `m03_visual.py:103` `from nicho_config import get_active_nicho`: importado, nunca usado en el archivo.
- `m03_visual.py:2489-2498` `_stitch_zone2_into_cap_veo/flux`: no-ops explícitos desde el chat 19, se siguen llamando (2649 y 2702); no los conté como muertas porque tienen llamador.
- `image_grade.py:77` `stats`: solo tests.
- `depth_probe.py:182` `DEFORM_RISK_LEVELS`: constante sin uso; `deform_risk` (186) recibe `metrics` y no lo usa; el nivel `mid` "existe en el contrato, sin regla" (comentario 177-180).

## Dos lógicas para lo mismo / duplicación

- `m03_visual.py` tiene dos detectores de fuga de texto (`_validate_no_text_leakage` que levanta error y `_find_text_leakage` que devuelve el span) con los mismos patrones copiados en dos cuerpos (1923-1951 y 1978-1995).
- `m03_visual.py:1374` y `:364`: dos bloques de canon visual (el viejo sin uso y el de 2 capas).
- `m03_visual.py:1881` `_validate_prompt_length` (rango 120-700) y `:814` (rango 120-2500 con `KLING_PROMPT_MAX_CHARS`): dos topes de largo distintos para prompts de imagen; el de 700 solo se usa hoy en el motion del clip Veo (`_seedream_video_prompt`, 2401).
- `m03_visual.py` `_build_plan_anchors_prompt_veo/flux` y `_validate_plan_veo/flux`: dos ramas casi idénticas para "veo" y "flux", aunque el motor es único (seedream).
- `depth_probe.py:48-50` y `:144-146`: las mismas tres variables de entorno (DEPTHMAP_CACHE_SIZE_MB, TORCH_DEVICE, CUDA_VISIBLE_DEVICES) se fijan dos veces, en el runner y en `probe_images`.
- `vision_validator.py:42` fija `VISION_MODEL = "gemini-2.5-flash"` en el archivo, mientras `zoom_judge.py:77` usa `api.gemini_model` de config: dos maneras de elegir el modelo de visión.

## Comentarios y docstrings que contradicen el código

- `m03_visual.py:73`: "LLAMADAS GEMINI: 7 (Flash, 1 por cap, secuencial). ~$0.010/video". Hoy son Pro para slots (`SEEDREAM_SLOTS_USE_PRO = True`, 139), Flash para anclas y para el fluidificador por imagen, y un Pro para el motion; paralelo por cap (`CAP_MAX_WORKERS`). Costo sin origen en el código.
- `m03_visual.py:53` y `:79-81`: el docstring habla de prompts de 120-400 caracteres y de N = clamp(.., 6, 18); el código usa `PROMPT_MAX_CHARS = 700` y `KLING_PROMPT_MAX_CHARS = 2500`; y la fórmula tiene además tope por video (línea 1326-1331).
- `m03_visual.py:1227-1232`: el comentario describe un "ANCLA_GLOBAL + 3 slots del Traductor" (refactor v6 chat 27), que ya no existe.
- `m03_visual.py:1235`: la constante se llama KLING_ pero la usa el camino seedream; el comentario habla de "endpoint Kling".
- `m03_visual.py:2544-2549`: "los paths flux/kling/veo-old fueron removidos", pero el módulo conserva `render_engine == "flux"/"veo"` como nombres de rama, `_calculate_image_count` hablando de "Flux" y comentarios de "Flux/Kling" por todo el archivo.
- `m03_visual.py:1115`: `F8_NOTE_BODY_HOOK ="NO ..."` (falta un espacio; cosmético).
- `foto_madre.py:36` y `lab/probe_orphan_mothers.py:71` citan `m03_visual.py:149` / `L149` como lugar del slot `style`; hoy ese slot está unas ~55 líneas más abajo (el comentario de otro archivo quedó viejo).
- `image_grade.py:6-9` (docstring) dice saturación 0.72 y frío 0.03; `DEFAULTS` (24-30) trae `saturation` 0.70 y `cool` 0.02. `gfx_profiles/misterio.json` no tiene clave `image_grade`, así que valen los DEFAULTS.
- `vision_validator.py:5-6`: habla de "Flux" y de "Veo (caro: $0.24/clip)": precio sin origen y motor que el código ya no usa como único. El decorador `@error_handler.retry` de `validate_image` (130) casi no actúa: la función atrapa sus propias excepciones y devuelve fail-open.
- `depth_probe.py:177`: comentario "Nocturno §3 (default)" sin referencia a un documento.
- `m03_imagenes_v3.py:3-4`, `asset_manager.py:1199-1200`: hablan de guion v2 "sin escaleta" que sale byte-idéntico; tras F41 la cadena v2 está borrada y un tema sin escaleta ya no llega a m03 (`fase1_5.py` para antes). La rama `f8_beats is None` de `assign_visual_prompts` (2571) queda alcanzable solo desde tests y desde labs.

## Rutas de la cadena borrada (F41) que siguen vivas

- `m03_visual.py:2570-2574` y todas las condiciones `if f8:` / `if f8_beats:` (1008, 1049, 1063, 2696, 2727): la rama "sin escaleta / guion v2" se mantiene; sin escaleta se usa `SYSTEM_INSTRUCTION_VISUAL_SEEDREAM` (no el V3, línea 1003).
- `m03_visual.py` conserva el contrato de 7 capítulos con caps `veo` 1 y 7 (`VEO_CHAPTERS`, `EXPECTED_CHAPTER_COUNT = 7`) que viene del guion viejo; el guion v4 produce 7 caps pero la lógica de `render_engine` por cap sale del esqueleto (`01a_*.json`).
- `m03_visual.py:1352-1365` `_format_facts`: también lo importan los pasos de researcher_steps (step_4b/4c/4d/4e); es un helper compartido, no exclusivo de m03.

## Números sin origen citado en el archivo

- `m03_visual.py:146` `FLUIDIFY_MAX_WORKERS = 16` (origen: comentario "conservador", pico ~16 RPM; sin cita), `:152` `CAP_MAX_WORKERS = 7`, `:764` `LEAK_MAX_RETEJIDOS = 2`, `:1114` `F8_FIX_PASSES = 2`, `:1196-1197` `MIN_IMAGES_FLUX = 6`, `MAX_IMAGES_FLUX = 18`, `:1216-1217` `MIN_FLUX_EXTRAS = 4` / `MAX_FLUX_EXTRAS = 14`, `:547` `MAX_MEASURES_PER_IMAGE = 1`, `:717` y `:714` `thinking_budget=0` (cita HANDOFF_134b), `:1206` `MIN_ANCHOR_GAP_SEC = 1.0` (cita calibración chat 54), `:1195` `SECONDS_PER_IMAGE_TARGET = 7.0` (cita test_movements_v12).
- `m03_imagenes_v3.py:232` `MOTIF_MAX = 2`, `:423` `TEXT_MAX_WORDS = 3`, `:405` umbral de 100 en `beat_scale`, `:539` 25 % de planos medios, `:555` zoom 1.3-1.6 en `reencuadres`: origen en el docstring del handoff F8/F8b, sin valor en DECISIONES citado en el archivo.
- `image_grade.py:24-30` (saturación, lift, viñeta, grano, frío) y `:85` (luma > 24): citan "F8b §2.6" y una medición ("baja ~18 %"), no un estándar.
- `depth_probe.py:32-33` (`DEPTH_ZOOM_CB_MIN = 0.15`, `MAX_ZOOMS_PER_CHAPTER = 7`): citan lab chat 55 y HANDOFF_140b (C4).
- `zoom_judge.py:92` recorte de `razon` a 160 caracteres y `vision_validator.py:191-195` recortes a 200: sin origen.

## Otros

- `m03_visual.py:747-753` (`_fluidify_item`): con `sin_respuesta == max_attempts` devuelve los slots crudos sin tejer (F27 §A.1) y los cuenta como prosa válida para el resto de la cadena.
- `m03_visual.py:1039`: `raw_llm_prompt` se arma a partir de los slots y se guarda en `03_visual.json`; el nombre quedó del camino viejo "prompt crudo del LLM" (el prompt final lo teje otro modelo).
- `m03_visual.py:2744` `_sync_map_ref` se persiste como ref (comentario PR 1 chat 24).
- `image_grade.py:79` importa PIL dentro de la función (`stats`), la única que lo necesita; si PIL no está, solo falla esa función muerta en producción.
