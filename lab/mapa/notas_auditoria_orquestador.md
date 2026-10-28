# Notas de auditoría — zona orquestador (F42 §B)

Materia prima para F43: lo raro que vio cada worker leyendo su parte entera, con archivo:línea. Sin propuestas.

<!-- parte orquestador_a -->
# Notas de auditoría — zona orquestador, parte orquestador_a

Materia prima para F43. Sin propuestas de cambio. Todo leído de la primera a la última línea (los 8 archivos), solo lectura.

## Discrepancias con `estado_a`
- `version_stamp.py`: A lo marca `huérfano`; yo puse `solo herramienta manual`. Nadie lo importa ni lo lanza (grep en .py, .claude/ y hooks), pero `REPO_MAP.md:13` dice que lo corre CC a mano y `VERSION.json` (raíz) está versionado y con push_id de 2026-07-13. Es la única diferencia con A.
- `_reseed_core` (qa_studio_server.py:819): A la marca `sin_llamador`. La confirmo como muerta en el servidor y el form, pero tiene un llamador real en una herramienta manual de lab (`lab/hyperframes/f5/regen_marcadas.py:37`) además del test. Dejo la decisión a la auditoría.
- `Handler.log_message` (L1724) y `Handler.do_POST` (L1865): no las cuento como muertas; las llama el framework `http.server`.

## Código muerto o dormido
- qa_studio_server.py:975-1011 `_FIX_CLIP_REWRITE_INSTRUCTION` y :1014 `_build_clipfix_user_prompt`: el comentario de L968-971 las declara dormidas (chat 113, "NO borrar sin decisión de Omar"); ningún call-site.
- qa_studio_server.py:247-251 `_is_single` devuelve siempre `False` ("Option A retirada"); se sigue llamando en `caps()` y el campo `single` viaja al front.
- qa_studio.html:168-179 (CSS `.single-wrap`, `.single-card`, `.galtitle`, `.gal`, `.galitem`) y :768 (selector `.galitem img`): estilos y selector de la "Option A / galería" que el servidor ya no emite (`single` siempre falso). También :345 `c.single?' · clip':''`.
- qa_studio.html:718-722 `fixbar()`: sigue mostrando "corregir narración/audio (Zona 2) → v2" aunque la Zona 2 ya existe (botón `narrFixBtn`, L428).
- qa_form.html:267 y :338-360 menús `judge_action` y `remeasure_pick`, y qa_studio_server.py:1426 `__judge__ → qa_judge.html`: el juez m05 está DESCONECTADO del chain (fase1_5.py:15 y :65, chat 119); `m05_judge.py:1617-1618` todavía emite `judge_action` pero nada de la cadena lo llama. `remeasure_pick` sale de fase1.py:438.
- qa_form_markers.py:10-13: el docstring dice que m05_judge.py es "código nuevo" que usa este módulo; m05_judge hoy está fuera de la cadena.

## Restos de la cadena borrada (F41) que siguen vivos
- qa_form.html:219-232 `activityLabel`: reconoce `m01a|m01b` ("Writing narration"), `m05|judge|juez` ("Auditing script"), `m06` ("Classifying issues") y el encabezado `VIDEO (`; ni la cadena única de F41 ni `_phase_header` de run_pipeline emiten ya `VIDEO (` (hoy: FONDOS, PANTALLA, RENDER).
- run_pipeline.py:149 y :173-180 `CADENA_VIEJA`: manejo explícito de topics de la cadena borrada (sin papel pero con guion/assets/video): es intencional de F41, pero es una rama que solo existe por los datos viejos.
- script_engine/__init__.py:3-9: el docstring lista `m01a_skeleton`, `m01b_narrator`, `m02_profiles`, `m04_sanitizer` y `m05_judge` como "pendiente"; `m02_profiles` y `m04_sanitizer` no existen en `script_engine/`, y los otros ya no son el motor actual (m01a_escaleta, m01b_guionista, m01e_pantalla).
- qa_studio_server.py:1417 `_FORM_PHASES` y :1530 `_form_topics` están ajustados a F41. La lista de fases (`RESEARCH, GUION, PAPEL, VOZ, ASSETS, FONDOS, PANTALLA, RENDER, PACKAGING`) está escrita tres veces: qa_studio_server.py:1417, qa_form.html:213-215 (`PHASE_LABEL`) y :436-437 (`PHASE_ES`), más los encabezados de run_pipeline.py.

## Dos lógicas para lo mismo
- run_pipeline.py:85-106 `_visuales_base_faltan` copia a mano la regla de `fase2b._visual_base_existente` (fase2b.py:2869) "porque fase2b arrastra DepthFlow y Gemini": dos copias de la regla de qué visual base existe por cap; si fase2b la cambia, run_pipeline no se entera.
- El estado "terminado" de un topic aparece como literal tres veces: fase3.py:27 `DONE_STATUS = "video_generated"` (comentario "mismo contrato que fase2b"), run_pipeline.py:137 (literal suelto) y el marcador `packaged` en run_pipeline.py:132.
- qa_studio_server.py:633-638 `_assemble_command` corre `fase2b.py <tid>` sin flags (preview sin gfx), mientras run_pipeline.py:246 y :412 corre el render con `--reuse-visuals --keep-segments --gfx --gfx-sparse`. Dos "ensamblar" distintos; el botón ENSAMBLAR del visor no hace el render final.
- qa_studio_server.py:773-784 `_invalidate_baked` borra `_fase2b_work/chNN_flux_visual.mp4` y `chNN_hybrid_visual.mp4`, los mismos archivos que `run_pipeline._visuales_base_faltan` (L98-102) usa para decidir si falta la etapa `fondos`. Acoplamiento por nombre de archivo entre el visor y el orquestador.
- qa_studio_server.py:1202-1204 arma `data/normalizer_custom_dict.json` con `state.base/"data"` (comentario: "base/data == DATA_DIR en producción") en vez de usar DATA_DIR de config: otra convención de ruta paralela a la de run_pipeline.py:48.
- qa_studio_server.py:2002-2009 `_free_port` y :1444-1451 `_free_port_local`: dos funciones de puerto libre en el mismo archivo (una con `connect_ex` desde 8000, otra con bind a 0).

## Comentarios que contradicen el código
- qa_studio_server.py:28-33 (docstring): dice que el wiring de fase3 queda DEFERIDO y que ENSAMBLAR solo corre fase2b; hoy `run_pipeline` lanza fase3 (run_pipeline.py:430) y el server lanza el review de m09 (L1490).
- qa_studio_server.py:1436-1437: dice que se usa subprocess porque "m09_packaging arrastra config/gemini/cost_tracker que este server evita a propósito", pero el mismo archivo importa `asset_manager`, `gemini_helpers` y `audio_manager` (pesados) en los núcleos de fix (L824, L870, L1046, L1255-1256), solo que de forma diferida.
- qa_studio.html:13: "Botones de fix VISIBLES pero DESHABILITADOS (tooltip v2)"; hoy están habilitados y cableados (L500-540).
- qa_studio.html:507, :510 y :803: el panel del clip dice "mismo primer frame, cambia el MOVIMIENTO/cámara" y "reescribe el video_prompt"; el servidor hace lo contrario (qa_studio_server.py:962-971 y :1072-1111: regenera la FOTO del primer frame con el video_prompt intacto).
- run_pipeline.py:37: cita "DECISIONES 2026-10-27 00:30" para "no cierra ningún programa"; esa entrada es la regla de RAM que la de 21:50 (DECISIONES.md:126) dejó sin efecto.
- qa_studio_server.py:1375-1378 (cabecera del bloque) y qa_form.html:3: dicen que el form lanza `run_pipeline --research`; cierto para el botón, pero el form también retoma con `--topic` (L1525-1527, qa_form.html:473).
- run_pipeline.py:21-26 y L33: el docstring habla de PACKAGING "solo con form"; el form (qa_studio_server.py:1522 y :1527) siempre pasa `--batch`, así que desde el form fase3 nunca corre: solo se imprime `python fase3.py <id>`.

## Números sin origen visible
- qa_studio_server.py:630 `_ASM_LOG_MAX = 600`, :1418 `_FORM_CONSOLE_MAX = 600`, :1640 límite de 500 caracteres de `_sanitize_form_line`, :2005 rango de 50 puertos en `_free_port`, :1482 `timeout=3` al matar el review de miniaturas, :1698 `tail=200`: ninguno cita DECISIONES ni un estándar.
- qa_studio_server.py:792 `RESEED_STEP = 104729` ("primo", F5e): el origen es el comentario, no un DECISIONES.
- qa_studio_server.py:69 `TOPIC_ID` por defecto cableado a un uuid concreto (985a942f-…): un dato de un video puntual como default.
- qa_studio.html:26-27 `--heat-good-max:8` y `--heat-long-max:13` (segundos): el comentario dice "perilla; afinar con videos reales"; sin origen en DECISIONES.
- qa_form.html:41 y :45 (CSS): animación de 26 s que llena la barra hasta 88%: heurística visual sin origen.

## Otros
- run_pipeline.py:363 y :290: `input()` sin timeout en el visor y en las compuertas; con el form las responde el navegador, sin form la corrida queda esperando stdin.
- run_pipeline.py:121-122 y :543: import diferido de `fase1_5` "porque es pesado", pero `etapa_de` llama a `_estado_papel` al arrancar cualquier corrida, así que siempre se importa.
- run_pipeline.py: el parámetro `batch` lo usa solo `_paso_packaging`; todos los `_paso_*` lo reciben por uniformidad (L296-407).
- run_pipeline.py:147 `ETAPAS` no incluye `research`; el research vive solo en `main()` (L523-539) y se secuencia aparte.
- fase3.py:54 `_volatile_warning` busca `*_final_*ZOOM*.mp4`, un nombre de artefactos viejos; el render actual deja `<id>_final_gfx.mp4` (run_pipeline.py:116). No encontré en fase2b.py ningún nombre `*_ZOOM.mp4` que lo produzca.
- fase3.py:127-131: exige `topic.status == "video_generated"` y `video_path` existente; si el render de run_pipeline escribe `_final_gfx.mp4`, depende de que fase2b lo registre en topics_db (no verificado, no leí fase2b entero).
- qa_form_markers.py:19: `QA_FORM` se lee una sola vez al importar; run_pipeline.py:53 lo importa en el nivel de módulo, así que un `QA_FORM` seteado después del import no tiene efecto (diseño intencional según el docstring).
- version_stamp.py:1-11: sin docstring ni `__main__`; ejecuta y escribe al importarse (efecto de módulo).

<!-- parte orquestador_b -->
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

<!-- parte orquestador_c -->
# Notas de auditoría — zona orquestador, parte orquestador_c

Materia prima para F43; no propone cambios. Leídos enteros los 24 archivos. Hechos de A contrastados con grep sobre producción (sin `lab/hyperframes`, sin `_lab_*`/`_probe_*`).

## Diferencias con `estado_a` de A
- `qa_seed_pick.html`: A dice `vivo` (etapa `orquestador/form`); pongo `huérfano`. `qa_studio_server.py:1420-1421` dice «qa_seed_pick.html jubilado (ya no se sirve)» y `_FORM_MENU_HTML` (`qa_studio_server.py:1422-1427`) no la incluye; ninguna ruta ni `.py` la abre. Su propio comentario de cabecera (`qa_seed_pick.html:4`) todavía dice «Servido por qa_studio_server (/form_menu/seed_pick)», lo cual ya no es cierto.
- `.claude/hooks/*.py` (los 6 hooks y `_comun.py`), `.claude/commands/tanda.md`, `.claude/agents/simulador.md`: A pone `solo herramienta manual`; pongo `vivo` porque `.claude/settings.json:8-12` y `:20` cablean los hooks, `_comun` lo importan todos, `tanda.md:17` invoca al simulador y `/tanda` es un comando activo. `structure-auditor.md` y `hooks/README.md` quedan `solo herramienta manual` (nadie los invoca / es documentación).

## Archivos que cambiaron mientras los leía (md5 distinto al de A)
Alguien editó estos tres durante mi lectura (trabajo F42 §C.4 en curso, ajeno a mi parte). Copié en el JSON el md5 de A, como pide el brief; los md5 actuales son:
- `.claude/commands/tanda.md`: A `71d49a2f…`, ahora `773354d0cb27d69b7bccac08d0979cd6` (pasos 2, 8 y 9 reescritos: ahora citan `lab/MAPA_PROYECTO.md`, md5 `f792f3d4…` y `verificar.sh`). Mi primera lectura fue de la versión vieja (citaba `lab/MAPA_MODULOS.md` y «5 fallas previas conocidas»); el sticker describe la nueva (los 12 pasos).
- `.claude/hooks/README.md`: A `5e4e093c…`, ahora `582575453abb1793b0c30ce05ff0d8b4`.
- `.claude/hooks/guard_mapa.py`: A `d91cd130…`, ahora `facfa9268459e87323a23d355addb5f8` (el docstring ya dice F42 §C.4; el sticker describe esa versión).
- `lab/mapa/stickers/_partes/orquestador_c.json` quedará con md5 de A para estos tres, que no coincide con el archivo de hoy.

## Código muerto o duplicado
- `cost_tracker.py:257` `track_leonardo`: marcada DEPRECATED en su propio docstring, sin llamadores; solo `REPO_MAP.md:196` la nombra. Lee la clave `leonardo_per_image` de config.
- `cost_tracker.py:297` `track_custom`: solo la llama `test_module_f26c.py:138`.
- `error_handler.py:228` `save_error_report` y `:242` `has_critical_errors`: sin ningún llamador (ni tests). `get_summary` (`:216`) solo se usa desde `save_error_report`, así que en producción también queda sin uso real aunque A no la marcó.
- `error_handler.py:34-37` miembros de `PipelineStage` sin uso en producción: `CHANNEL_MEMORY` y `ORCHESTRATOR` (grep `PipelineStage.<X>` = 0 fuera de tests/lab).
- `cost_tracker.py:195` `track_flux_pro` y `:207` `track_flux_ultra`: dos métodos para el mismo modelo; el docstring (`:210-212`) admite que existe «por compatibilidad». Ambos tienen llamador vivo en `asset_manager.py`.
- `gemini_helpers.py:179-195`, `:217-233` y `:241-255`: `call_flash_json`, `call_pro_json` y `call_model_json` repiten el mismo bloque `config_kwargs` línea por línea; solo cambia el modelo.
- `claude_helpers.py` y `gpt_helpers.py`: `_api_key`, `json_schema`, `_post`, `_track`, `cost_of`, `call_json` y `make_call` son copias (el propio encabezado de `claude_helpers.py:2` dice «Copia de gpt_helpers.py»). Se divergen en detalle (HTTP 408/529, streaming, `additionalProperties`).
- `qa_choice.html:99-114,126-129` `renderSeeds` + rama `payload.seeds`: panel de tarjetas de seeds para `reuse_seeds`, pero `qa_form.html:278` manda `reuse_seeds` y `seed_pick` a `qa_gallery.html`; la rama ya no se alcanza desde el form.
- `qa_gallery.html`, `qa_seed_pick.html`, `qa_judge.html`, `qa_choice.html`: cada archivo repite `esc`, `fmtViews`, `fmtRatio`, `MODE_BADGES`, `STATES`, `riskOf` y el `qaAnswer`; la paleta se «copia» entre archivos por comentario («paleta EXACTA copiada de …»).
- `.claude/agents/structure-auditor.md:15-28`: su lista de 55 módulos incluye `m01a_skeleton`, `m01b_narrator` (que F41 vació de sus funciones; los archivos siguen en `script_engine/`) y `subtopic_measurer` (no existe en el repo). `_repo_audit/` existe vacío.

## Números o constantes sin origen en el archivo
- `cost_tracker.py:27-32` `_DEFAULT_GEMINI_RATES_PER_1M` (tarifas Gemini): tienen fecha y fuente en los comentarios (`:22-24`, `:30`), pero `gemini-3-flash-preview` no tiene fuente propia y `_default` (`:32`) es «fallback conservador» sin origen. El precio de `gemini-4-argon` vale «hasta el 2026-11-30» (`:30`): tiene vencimiento.
- `cost_tracker.py:185` `0.0001` (default de `gemini_vision_per_call`), `:229` `0.028` (kling), `:247` `0.035` (seedream): defaults literales por si falta la clave en config; los comentarios dicen «aprox» o «confirmar por delta de dashboard» (`:226-227`).
- `claude_helpers.py:144-145` multiplicadores de caché `1.25` (escritura) y `0.1` (lectura): sin cita de fuente. `:31` PRICES cita «tabla pública de precios de Anthropic» pero sin fecha.
- `claude_helpers.py:32,33,34` `MAX_ATTEMPTS=3`, `TIMEOUT_S=600`, `MAX_TOKENS=100_000`: `MAX_TOKENS` tiene origen en el comentario F25a; los otros dos no.
- `gpt_helpers.py:23-26` `MAX_ATTEMPTS=3`, `TIMEOUT_S=600`, `MAX_COMPLETION_TOKENS=32000`: sin origen (PRICES sí cita HANDOFF_F11b §1.3).
- `error_handler.py:146` `max_server_retries` por defecto `5` y `:159` base mínima `10` s × `1.5`: sin origen. `:132` el docstring dice «esperas aprox ~15s, ~23s, ~45s, ~90s, ~180s», pero con la fórmula de `:157-161` (base `5·2^(n-1)`, mínimo 10 × 1.5, más hasta 50 % de jitter) los valores base son 15, 15, 30, 60 s (+ jitter).
- `gemini_helpers.py:36` `PARSE_MAX_ATTEMPTS=3` y `:19` `max_attempts=3`, sin origen; `:27` comenta «2s, 4s, 8s» pero con 3 intentos solo ocurren las esperas de 2 s y 4 s (`2 ** (attempt + 1)` con attempt 0 y 1).
- `mixer.html:90,96,153` valores por defecto de sliders (`0.26`, `0.16`) y del perfil de ducking (`0.03`, `5`, `80`, `200`) escritos a mano como respaldo hasta que `/defaults` responda.
- `tools/dump_topic_evidence.py:27-37` `VERDICT_PRIORITY` (orden de los veredictos) y `tools/build_gemini_validation_prompt.py:21-65` el prompt dice «8 temas» fijo, mientras el dump puede tener cualquier cantidad.
- `.claude/hooks/suite_rapida.py:16` `TIMEOUT_S=170`: sin origen (el `timeout` de `settings.json:9` es 180).

## Comentarios o textos que contradicen el código
- `cost_tracker.py:243-246` el docstring de `track_seedream` dice «La TARIFA queda 0.04 para ambos modos», pero el código (`:247`) usa el default `0.035` con comentario «F8: Seedream 5.0 Lite»; el `service` también dice 5.0 Lite, no 4.5 como el docstring (`:240`).
- `cost_tracker.py:339-340` y `:105-117`: el gasto sin video activo (research en `fase1.py`, que no abre `start_video`) cae en `session_overhead`; `end_video` (`fase1.py:555`) devuelve None sin guardar nada y ese overhead solo sale en `data/session_report_<fecha>.json` (`save_session_report`, `fase1.py:559`), no en `data/cost_history.json`, que es lo que lee el hook `tope_tanda`.
- `cost_tracker.py:354` `_load_history` y `:348` `_save_to_history` usan `read_text`/`write_text` sin `encoding` (cp1252 en Windows); `.claude/hooks/README.md:21-22` ya lo registra («cost_history.json hoy no es UTF-8 válido»); `tope_tanda.py:34-35` lo rodea con cp1252.
- `cost_tracker.py:158-164` solo `track_gemini_tokens` emite el marcador de costo en vivo al form; `claude_helpers._track` (`:152`) y `gpt_helpers._track` (`:77`) escriben con `_add_entry` privado y no emiten marcador, así que el gasto de Claude/GPT no llega al contador en vivo del form.
- `cost_tracker.py:121-131` `track_gemini` etiqueta el stage `SCRIPT` y llama la clave `gemini_per_call` aunque el servicio es solo «Gemini»; `track_gemini_tokens` (`:133-157`) usa el mismo stage `SCRIPT` también para Claude/GPT (en `claude_helpers.py:152`, `gpt_helpers.py:77`), aunque la imagen Gemini Vision va a `IMAGE`.
- `claude_helpers.py:11-14` el comentario cita «tope 128k» y max_tokens 100 000; `script_engine/guion_v4.py:62` dice «max_tokens 32 000, claude_helpers.MAX_TOKENS», pero `claude_helpers.MAX_TOKENS` vale 100 000 (`claude_helpers.py:34`).
- `claude_helpers.py:36` el comentario habla de «la ficha» pero `SALIDA_GRANDE = ("ficha_caso",)` se compara con `description` literal; depende de que `ficha_caso.py` pase exactamente ese string.
- `error_handler.py:144` `max_retries or pipeline.max_retries` trata `max_retries=0` como «no pasado» (cae al valor de config).
- `gemini_helpers.py:20` el docstring de `_with_retry` dice «si Gemini devuelve 503» pero captura cualquier `ServerError` (5xx) y no reintenta 429.
- `qa_seed_pick.html:4-5` ver arriba (dice «Servido por qa_studio_server»).
- `qa_gallery.html:1-17`, `qa_judge.html:3-6`: cabeceras citan «contrato chat 61»/«HANDOFF 63a/65a/65b» sin ruta; el nombre `qa_form.html` es correcto.
- `.claude/hooks/README.md:7-14` tabla: `md5_prompt` dice «Edit/Write/MultiEdit» (coincide con `settings.json:18`) pero su docstring (`md5_prompt.py:1`) dice «Edit|Write»; `suite_rapida.py:1` y `tope_tanda.py:1` dicen «PreToolUse Bash» pero `settings.json:6` los dispara en `Bash|PowerShell`.
- `.claude/agents/simulador.md:10` cita como default el topic `f8s3-vajont-f30`; no verifiqué si todavía existe en `output/` (no se lee `output/`).
- `.claude/commands/tanda.md:20` cita `lab/hyperframes/f41/verificar.sh`; el resto de pasos citan `lab/MAPA_PROYECTO.md`, que hoy no existe en disco (`lab/MAPA_MODULOS.md` sí): el comando apunta a un archivo que todavía hay que generar.

## Rutas de la cadena borrada (F41) o datos que ya no existen
- `tools/dump_topic_evidence.py:21` lee `data/topics_db.json` y `tools/build_gemini_validation_prompt.py:17` lee `data/topic_evidence_dump.md`; según `lab/ESTADO_SESION.md:26` ambos archivos de datos se enviaron a la Papelera, así que las dos herramientas hoy imprimirían «[ERROR] no existe».
- `.claude/agents/structure-auditor.md`: ver arriba, módulos `m01a_skeleton`/`m01b_narrator` cuyas funciones F41 borró y `subtopic_measurer` que no existe.
- `error_handler.py`, `cost_tracker.py`, `gemini_helpers.py`, `claude_helpers.py`, `gpt_helpers.py`: sin referencias a la cadena vieja (`is_v3_topic`, `--v3`, `--guion`); limpios.

## Efectos al importar (raro)
- `error_handler.py:257` crea la instancia global al importar y `_setup_logger` (`:68`) abre un `logs/pipeline_<fecha>.log` nuevo por cada proceso que importe el módulo (incluidos subprocess, hooks no, tests sí); `cost_tracker.py:532` y `gemini_helpers.py:15-16` también construyen objetos globales al importar (`APIConfig()` y `genai.Client(...)`).
- `gemini_helpers.py:16` crea el cliente de Gemini con la llave de config al importar: cualquier módulo que importe `gemini_helpers` (también arriba, como `step_4a_facts.py:19`) paga ese costo aunque no llame a la API.
- `.claude/hooks/guard_mapa.py:23-24` importa y ejecuta `lab/tools/mapa_modulos.check()` dentro del hook en cada `git commit` (versión nueva F42 §C.4); un fallo se traga y se convierte en aviso.
- `.claude/hooks/guard_render.py:24-28` carga `script_engine/aprobacion.py` por ruta con `importlib.util` (no por `import`), por eso A no ve la arista; `_aprobacion()` se llama en cada comando con `--gfx`.

## Otras rarezas
- `cost_tracker.py:94-98` `start_video` no cierra un `current_video` anterior; si se llama dos veces seguidas el primer reporte se pierde sin pasar por `end_video`.
- `cost_tracker.py:183-193` `track_gemini_vision` estampa `unit_label="calls"` y las entradas Gemini por tokens `unit_label="tokens"`; `get_gemini_summary` (`:446`) filtra por `unit_label == "tokens"`, así que también cuenta las entradas de Anthropic y OpenAI como «Gemini» (por modelo salen con su propio `service`, pero los totales de `print_gemini_report` suman todo).
- `researcher_steps/research_v3.py:1561` usa el método privado `cost_tracker._all_entries()` (y `claude_helpers._track`/`gpt_helpers._track` usan `_add_entry` privado): no hay API pública para esos usos.
- `mixer.html:132` dice «revertí con `revert_generation`» (existe en `script_engine/topics_db.py`); el re-armado corre `fase2b` sin `--gfx` (`mixer_server.py:351` «$0, sin gate»), por eso `guard_render` no lo toca.
- `qa_*.html` cargan las tipografías de Google Fonts por red (`<link href="https://fonts.googleapis.com/…">`); en un equipo sin internet cae a la tipografía por defecto.
- `.claude/hooks/guard_git.py:91-93` mira solo los refspecs escritos: `git push origin HEAD` estando en `main` pasa (el refspec `HEAD` no es `main` y `refs` no está vacío); solo bloquea `main`, `x:main` o `refs/heads/main` literales, o un push sin refspec estando en main.
- `.claude/hooks/suite_rapida.py:15` y `.claude/commands/tanda.md:20` repiten la lista de tests `f25c, f24, f21` en dos lugares sin referencia cruzada (README la repite una tercera vez, `README.md:10`).
