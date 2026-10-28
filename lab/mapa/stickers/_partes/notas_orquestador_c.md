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
