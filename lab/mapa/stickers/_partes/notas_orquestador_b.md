# Notas de auditoría — zona orquestador, parte orquestador_b

Materia prima para F43. Sin propuestas de cambio. Archivos leídos enteros: asset_manager.py (1406 líneas), m09_packaging.py (844), m09_review_server.py (509), csv_exporter.py (384), report_foto_madre_edits.py (116), config.py (342). Los md5 de A no cambiaron durante la lectura.

## config.py
- config.py:330 `get_video_config` solo aparece en el docstring (config.py:9); ningún .py del repo la llama.
- config.py (clase APIConfig, bloque de claves de servicios): hay credenciales escritas en claro en el archivo versionado (Gemini, YouTube, Leonardo, fal, ElevenLabs, proxy, Pixabay). No copio ningún valor. Un comentario en asset_manager.py:595 dice que `api.*` está "gitignored", lo que contradice que el archivo esté en el repo.
- config.py:56-60 y 63: `gemini_api_key`, `leonardo_*` siguen en `APIConfig` aunque el docstring (config.py:67) los marca DEPRECATED; `leonardo_chapters` (config.py:194) y `leonardo_images_per_long_video` (config.py:217) siguen con nombre Leonardo y alimentan `estimated_cost_per_long_video` con tarifa Flux.
- config.py:148-174 costos: `flux_pro_per_image`, `kling_per_image`, `seedream_per_image`, `fal_per_clip`, `elevenlabs_per_char` y las tarifas de Gemini por 1M tokens son números sin cita de origen más allá de comentarios sueltos (fecha "2026-07-04" para Gemini). `estimated_cost_for` usa la tarifa de Flux para el video largo aunque `image_engine` es Seedream.
- config.py:12 y 5-19 (docstring de arranque) habla de Leonardo → Flux 1.1 Pro; el motor por defecto hoy es otro (`image_engine`, config.py:96). Comentario desactualizado.
- config.py:192-194 `total_chapters = 7`, `veo_chapters = (1, 7)`; el comentario de la clase (config.py:186) dice "Cap 8" y la cadena v4 puede variar el número de capítulos.
- config.py:198-218: varios largos (`target_duration_seconds`, `target_word_count`, `min/max_word_count`, `target_words`, `max_words`, `hook_words`, `dev_words`, `outro_words`, `*_cap_seconds`, `max_images_per_video`) conviven; los comentarios mencionan "hipótesis de arranque" de F7c-2 y F25c. No verifiqué cuáles consume hoy la cadena v4 (fuera de mi parte).

## asset_manager.py
- asset_manager.py:2-14, 23, 1332: docstring y manifiesto hablan de "Flux 1.1 Pro / Ultra" y `"image_engine": "fal.ai Flux 1.1 Pro"` fijo (asset_manager.py:1332), pero el motor real sale de `api.image_engine` (por defecto seedream) y el modelo Flux del config es Flux.2 Pro.
- asset_manager.py:1282: el log dice "Vision Guardrail ACTIVO" siempre, mientras `ENABLE_VISION_VALIDATOR = False` (asset_manager.py:68). El manifiesto sí graba el valor real (asset_manager.py:1334). Además `"model": "gemini-2.5-flash"` está escrito como string fijo (asset_manager.py:1335) en vez de leer `api.gemini_model`.
- asset_manager.py:255 y 273: los docstrings de `_seedream_payload_for` / `_seedream_edit_payload_for` dicen "Seedream 4.5", pero `config.py:156` y `engine_profiles.py:68` hablan de Seedream 5.0 Lite (sin `seed` de entrada). Comentario contradice el código.
- asset_manager.py:184-210 `_flux_payload_for` recibe `model_endpoint` y no lo usa.
- asset_manager.py:319 y 394: `use_ultra` queda inerte en los motores de perfil (lo dice el docstring, asset_manager.py:325); en la rama flux ambos endpoints son el mismo modelo (config.py:90-91). `HOOK_CHAPTER_ID`, `_is_hook_chapter` y los logs "ULTRA/PRO" siguen vivos sin efecto de calidad.
- asset_manager.py:393-442: la rama "flux" (queue) solo corre si `select_profile(api.image_engine)` devuelve None, o sea con `image_engine="flux"`; el valor por defecto de config no la usa.
- asset_manager.py:445-446: alias `_flux_generate_raw` "para scripts externos"; el único llamador que encontré es la raíz `_gen_cap5_missing.py:29` (script suelto, no del form).
- asset_manager.py:1292-1298: remapeo de `render_engine == "leonardo"` a flux, para guiones viejos; Leonardo ya no existe como motor.
- asset_manager.py:130-137 `_extract_art_profile` y los campos `art_profile` / `profiles_used` / `art_profiles_used: []` (asset_manager.py:1354) son restos del catálogo desconectado en el chat 19 (el propio código lo dice).
- asset_manager.py:1047-1056 y 1094-1117: el camino Veo (`_process_veo_chapter`, `_call_veo_once`, `_generate_veo_clip`) sigue completo; usa `chapter["video_prompts"]` obligatorio. No verifiqué si algún guion v4 actual emite `render_engine == "veo"`.
- Números sin origen en el archivo: `FLUX_POLL_TIMEOUT` 180 (asset_manager.py:64), `VEO_POLL_TIMEOUT` 600, `RATE_LIMIT_BACKOFF_SECONDS` 20, `15 * attempt` (asset_manager.py:657), timeouts de requests 15/30/60/120/240 (varias líneas), tope `prompt[:2500]` de Kling (asset_manager.py:240).
- asset_manager.py:63: `FLUX_MAX_WORKERS` se lee de `pipeline.fal_concurrency` con `getattr(..., 20) or 20`; el comentario (asset_manager.py:62) menciona bajar a 10 "si no se compran $100 en 4 semanas", una condición de negocio escrita en el código.
- asset_manager.py:1263-1264: `process_script` no usa `sync_map` salvo para avisar de capítulos sin entrada (asset_manager.py:1268-1277); el parámetro casi no influye.
- asset_manager.py:1215: import dentro de función `from script_engine import image_grade` (existe; no está roto).
- foto_madre.py:28 importa de asset_manager cinco nombres privados (`_generate_image_raw`, `_fal_headers`, `_flux_poll`, `_is_content_rejection`, `ContentRejectedError`); por eso A marca asset_manager como alcanzado desde fase1_5 (papel/guion) y no solo desde `assets`. En el código, la generación de la foto madre corre en `fase1_5.process_topic` (fase1_5.py:647) y en `fase2a.py:337`.

## script_engine/m09_packaging.py
- m09_packaging.py:20 docstring dice "NO toca ningún módulo existente" / "Greenfield", pero importa m03_visual (m09_packaging.py:40) y asset_manager (m09_packaging.py:489).
- m09_packaging.py:8-14, 620, 807: la ayuda y el md hablan de "elegí 1 de 3 títulos" / `--title N (1-3)`; el esquema de Gemini pide 6 títulos y 6 overlays (m09_packaging.py:120-121, `minItems: 6`).
- m09_packaging.py:286 el prompt del hero dice "SEEDREAM 4.5"; el motor por defecto hoy es Seedream 5.0 Lite (engine_profiles.py:68). Además el render real va por `api.image_engine`, que puede ser otro.
- m09_packaging.py:96 `_load_canonical` usa `Path("data")` relativo al directorio de trabajo, no `DATA_DIR`; igual `Path("_lab_out/...")` en m09_packaging.py:627. Depende del cwd.
- m09_packaging.py:627: las miniaturas "existentes" dependen de `_lab_out/lab_fidelity_punch_chat56/audit_map.csv`, un producto de laboratorio del chat 56; si falta, se omite sin error (m09_packaging.py:638).
- m09_packaging.py:110: `cost_tracker.track_gemini(..., calls=1)` cuenta un costo plano por llamada, mientras config.py:163-173 y `cost_tracker.track_gemini_tokens` (cost_tracker.py:133) existen para costo por token (HANDOFF_133). Dos lógicas de costo de Gemini.
- m09_packaging.py: no llama `cost_tracker.start_video`; los costos de imagen que registra `asset_manager._generate_image_raw` caen en el video activo del proceso (en fase3/--review no lo inicia nadie en este archivo). No verifiqué qué hace `_add_entry` sin video activo (cost_tracker.py:304-334).
- m09_packaging.py:31 `Any` importado y no usado.
- m09_packaging.py:684 el CHECKLIST trae un pendiente fijo "Verificar cap3 sin texto fantasma (pendiente de backlog)", viejo, impreso en todos los videos.
- m09_packaging.py:92 `_final_mp4` apunta a `{id}_final_v3_ZOOM.mp4`; el comentario avisa que es el nombre histórico y el CHECKLIST cae a él si no llega `--video-path`.
- Números sin origen citado: `THUMB_TEXT_SCALE` 0.15, `THUMB_STROKE_PX` 8, `THUMB_MARGIN` 56, `THUMB_MAX_LINES` 2, `MAX_TITLE_CHARS` 90 (el prompt dice 70, m09_packaging.py:133), `MAX_TAGS_CHARS` 450, `FRESH_THUMBS` 3, `META_TEMP` 0.35, temperatura 0.4 escrita en línea (m09_packaging.py:375 y 550), `HERO_NARRATION_PER_CAP` 1400, `THUMB_MAX_BYTES` 2 MB (esa sí es regla de YouTube pero sin cita), colores del texto (231, 29, 29) etc.
- m09_packaging.py:40-43 importa `DOCTRINE_*` desde m03_visual; hace que este módulo arrastre config, Gemini y cost_tracker (qa_studio_server.py:1436 lo comenta como razón para lanzarlo por subprocess).

## script_engine/m09_review_server.py
- m09_review_server.py:405 `Handler.log_message` y :444 `Handler.do_POST` figuran sin llamador en A; los llama el framework (`http.server`). No son muertas.
- m09_review_server.py:335-341 `fillDatalist` (JavaScript dentro de `_PAGE`) no se llama en ninguna parte de la página; los comentarios (m09_review_server.py:318, 335) todavía hablan de `datalist` aunque se reemplazó por el menú propio (m09_review_server.py:343-361).
- m09_review_server.py:372 el contador muestra "x" (`toFixed(2)+'x'`) mientras el HTML inicial dice "1.00×" (m09_review_server.py:284). Cosmético.
- m09_review_server.py:150 `import shutil as _sh` dentro de `delete_candidate`; m09_review_server.py:432 `from urllib.parse import unquote` dentro de `do_GET` (el módulo ya importa `urlparse` arriba).
- m09_review_server.py:10-13 dice que "las llamadas Gemini/Flux son del lado de Omar (sus keys)"; en realidad `_run_generate` y `_run_first_batch` gastan Gemini y el motor de imagen desde este mismo proceso (m09_review_server.py:121-127, 173).
- m09_review_server.py:49-65 conserva compatibilidad con records viejos de `hero_iterations.json` (`subject`/`hero_prompt` únicos).
- Servidor sin autenticación en 127.0.0.1 con rutas POST que gastan API (`/generate`) y mueven archivos (`/delete_candidate`); `resolve_image` y `delete_candidate` validan el nombre base.

## csv_exporter.py
- csv_exporter.py:298 `parse_decisions_csv` (con `_parse_index` :263 y `_parse_format` :283, que solo ella usa) está importada por fase1.py:45 y fase1_5.py:59 pero ningún código de producción la llama; solo test_module_35_menu_csv.py:54. Lo mismo con `OUTPUT_CSV` importado en fase1.py:43 y fase1_5.py:59 sin uso en esos archivos. A no la marcó como candidata porque aparece en esos imports.
- csv_exporter.py:176-179 el docstring dice que "el motor (fase1_5) ya no consume hook_index / outro_index / format_override" y que `export_single_topic_csv` pre-llena "1" dummy para que `parse_decisions_csv` lo apruebe, pero nadie en producción lee ese resultado; el CSV sirve hoy solo para la lista de topic_ids de fase2a (fase2a.py:72) cuando se corre sin `--topic`.
- csv_exporter.py:1 el docstring dice `modules/csv_exporter.py` (ruta que no existe; el archivo está en la raíz). csv_exporter.py:222-256 imprime "Dashboard 3.0" y fase1.py habla de "Dashboard 2.0" (fase1.py:9, 575, 586).
- csv_exporter.py:121-124 `estimated_cost_for(video_type)` usa tarifas Flux (ver config.py), no el motor real.
- La etapa `research` es la que corre `export_fase1_csv` (fase1.py Paso 4); `export_single_topic_csv` solo en el menú interactivo de fase1_5 (fase1_5.py:750), que el form no usa (usa `--topic`).

## report_foto_madre_edits.py
- Sin importadores, sin lanzadores y sin tests (A: `tests: []`). Único origen: commit 7ecb047 del 2026-07-03. `estado_a` = solo herramienta manual; coincido.
- report_foto_madre_edits.py:1 dice "HANDOFF_133 + pedido de Omar"; el campo `stale_telemetry` (report_foto_madre_edits.py:60) existe por manifests anteriores al fix del endpoint; ya no debería aparecer en corridas nuevas (asset_manager.py:385 graba el endpoint real).
- Escribe en `output/` (sidecars por corrida e índice global); no se corrió.

## Discrepancias con A
- Ninguna en `estado_a` (los seis quedan como A: cinco vivos y uno solo herramienta manual).
- A marcó `etapas` de asset_manager con research/guion/papel/voz porque otros scripts lo alcanzan por import (foto_madre, fase1_5); en el código el motor de imágenes corre en `assets` (fase2a) y, para las miniaturas, en `packaging`.
- A marcó `etapas` de csv_exporter con guion/papel/voz/assets; en el código solo escribe en `research` (fase1) y en el menú interactivo de fase1_5; fase2a solo lee el CSV.
- csv_exporter.py: A no marcó `parse_decisions_csv` ni `OUTPUT_CSV` (csv_exporter) como candidatas; las dejo en notas arriba.
