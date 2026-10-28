# Notas de auditoría — zona fase2a, parte fase2a_c

Material crudo para F43. Sin propuestas de cambio. Los 11 archivos se leyeron enteros; ninguno cambió (md5 de A copiados tal cual).

## Código muerto, duplicado y dos lógicas para lo mismo

- `audio_manager.py:149` `_transcribe_word_timestamps` y `audio_manager.py:208` `_force_align_to_script`: nadie las llama en el repo. Es el camino Whisper, reemplazado por el Forced Alignment de ElevenLabs (`audio_manager.py:543`).
- Muertas por arrastre (solo las usan las dos de arriba): `_get_whisper_model` (115), `_merge_punctuation_words` (133), `_normalize_token` (187), `_interp_spans` (195), `_enforce_monotonic_timestamps` (304). A no las marcó porque se nombran entre ellas.
- `audio_manager.py:133` `_merge_punctuation_words` está repetida en `fase2b.py:192`, y `audio_manager.py:71` `_find_ffmpeg_binary` en `fase2b.py:86` (y `mixer_server.py`, según A). El «llamador en fase2b» que A registró es la copia propia de fase2b, no un import de audio_manager.
- `audio_manager.py:462` `_normalize_loudness` llama a `ffmpeg` por nombre pelado, mientras `_get_ffprobe` (90) resuelve la ruta con Winget. Dos formas de ubicar el binario en el mismo archivo.
- `script_engine/m07_music_director.py:1218` `fijar_plan` solo la llama `plan_composicion` (1215), que está muerta en producción: muerta por arrastre. `m07:1202` `plan_composicion` y `m07:1249` `generar_con_plan` solo las usan `test_module_f28a.py` y `lab/hyperframes/f28/a/f28a_paleta.py`.
- `script_engine/m07_music_director.py:877` `_generate_new_track_with_gate` (con `_gate_approve_track` 780, `_play_audio_file` 699, `_edit_prompt_with_notepad` 736, `_persist_track_descriptor` 581, `_call_elevenlabs_music_api` 538) es el camino viejo «una pista nueva por video». Sigue conectado (m07:1134) y se activa si un intent no tiene pista de paleta en la biblioteca. Con F28 la idea declarada es «nunca se genera música por video» (m07:1103-1104).
- Dos lógicas para elegir pista: rama paleta (m07:1101-1109, sin umbral, cae a la pista «a») y rama vieja con `MATCH_SCORE_THRESHOLD` (m07:1110-1116 y 1446). El log de m07:449-451 imprime `MATCH_SCORE_THRESHOLD` aunque ahora el umbral efectivo puede ser el parámetro `umbral`.
- `audio_manager.py:456` `tts_v4_enabled` y `audio_profiles.py:105` `VOICE_SETTINGS_BY_INTENT` (v2 + Bill) siguen vivos; solo se usan si el capítulo no trae `narration_tts` o con `TTS_V2=1`. Tras F41 (cadena única v4) no hay otra fuente de capítulos sin `narration_tts` que el camino SHORT de `fase2a.py:324`.
- `audio_profiles.py:49` y `:68` perfiles `SABIDURIA_ESTOICA` y `TRUE_CRIME_TERROR`: nadie los activa (`audio_config.py:8` fija MISTERIO_ABISAL). Hay también `music_prompt` en los tres perfiles, escrito al sync_map (`audio_manager.py:847`) y no leído por ningún módulo de esta parte.
- `music_config.py:76` `MUSIC_PROMPTS` (7 prompts «curados a mano») es la fuente del camino viejo de generación; la paleta nueva usa `PALETA_INTENTS` (265) más `SONIDO_DEL_CANAL` (254). `SONIDO_DEL_CANAL` solo lo consume el lab de F28 (grep en lab/hyperframes/f28), no producción.

## Comentarios y docstrings que contradicen el código

- `audio_manager.py:7-9` dice que transcribe con faster-whisper y hace forced alignment contra Whisper; el código real usa el Forced Alignment de ElevenLabs (`audio_manager.py:686`). Los comentarios de 47-51 y 696-698 también arrastran la historia.
- `audio_manager.py:122` el log dice «Whisper (base, int8)» y la línea 125 carga `device="cuda", compute_type="float16"`.
- `audio_manager.py:808` `AUDIO_STYLE.get("elevenlabs_model_v4") or "eleven_v4"`: el valor literal aparece como respaldo, y `audio_profiles.py:18` ya lo trae. Duplicado de la constante.
- `fase2a.py:309-311`: fase2a habla de «timestamps Whisper en PR 3»; los timestamps ya no vienen de Whisper.
- `script_engine/m02_5_normalizer_gate.py:5-8` y `:113` anuncian «8 categorías» / «los 8 casos»; el prompt enumera 11 (hasta LARGE_NUMBER, 228) y `VALID_LLM_CATEGORIES` (54) tiene 13 valores. `:342` habla de «6 casos». `:84-90` el docstring de `_build_system_instruction` no menciona los cambios de F5.
- `script_engine/m02_5_normalizer_gate.py:97` y todo el prompt asumen «español neutro»; el docstring de `tts_normalizer.py:8-15` dice «Para SHORT… camino principal» y «LONG con gate», lenguaje de antes de F41.
- `script_engine/m07_music_director.py:20` «LLAMADAS GEMINI: 0-7 por video»; con paleta hay 1 por capítulo con 2+ pistas de paleta, y el flujo F28 puede tener más caps que 7 (no hay tope en el código).
- `music_config.py:41-44` el comentario dice «Duración fija… 60s» y «Camino A: 60s» (también en el encabezado, líneas 10-11), mientras `MUSIC_LENGTH_MS = 180000`. El comentario de la línea 44 sí explica el cambio; los dos de arriba no.
- `music_config.py:51-53` timeout «180s = 3 minutos» pero `m07_music_director.py:1255` usa `max(MUSIC_REQUEST_TIMEOUT_SEC, 400)`: dos números para lo mismo.
- `music_config.py:228` `stripped in ("", "...", "...")`: dos elementos iguales (probablemente un punto suspensivo Unicode y tres puntos que perdieron la diferencia).
- `music_config.py:29` y `:191-200` hablan de «las 7 entries»; `PALETA_INTENTS` (265-275) tiene 6: falta `resolution`.
- `script_engine/music_intensity.py:13-16` docstring define silencio «nunca más de 2 por cap; (a) va primero»; el código lo cumple, pero la regla (b) se evalúa solo contra citas que caen fuera de la ventana del golpe (línea 116) y eso no figura en el docstring.
- `patch_sync_map_mixing.py:6` «Descartable después de chat 28»: sigue en el repo y nada lo referencia.
- `subs_remap.py:12-15` cita `fase2b._build_chapter_segment ANTES de _build_ass_from_words`; `script_engine/gfx_layer.py:478` lo usa también y el docstring no lo dice.

## Números sin origen visible (para la regla «número que no esté en DECISIONES / F3 / estándar citado»)

- `script_engine/m07_music_director.py:917` `MAX_ATTEMPTS = 10`; `:266` y `:271` cortes de 400 y 300 caracteres del prompt/descripción; `:1076` `[:200]` del anchor; `:1062` `[:50]` del video_id; `:1255` 400 s de timeout; `PLAN_SECCIONES = (3, 5)` (1179), 3000 y 120000 ms por sección (1239-1241; el prompt de 1189 dice lo mismo), 50 y 48 estilos máximos (1231-1245).
- `script_engine/m07_music_director.py:313` y `music_config.py:49` umbral 80 («conservador inicial», sin medición citada); `:445` umbral 0 con paleta («F28: se elige entre las dos»).
- `audio_manager.py:410` timeout 120 s; `:566` 180 s; `:367` 15 s; `:690` loss > 0.15; `:462-464` `TP=-1.5`, `LRA=11`, 44100, 128k; `:470` respaldos `0.55` / `0.8`; `:809` `"es"`. `audio_profiles.py:23` `voice_lufs_v4 = -24.0` (justificado por una medición de F9 en el comentario); `audio_profiles.py:31-37` volúmenes y ducking del canal, con comentarios de «chat 32 tune».
- `audio_profiles.py:106-123` stability y style por intent: comentarios como «# subí / # igual / # subí mucho stability, bajé mucho style» describen cambios que ya no coinciden con los números (por ejemplo `shock` stability 0.45, el comentario dice «subí mucho»).
- `script_engine/music_intensity.py:27-35` `GANANCIA_DB`, `FADE_SILENCIO_S`, `SILENCIO_PREVIO_S`, `VUELTA_GOLPE_S`, `RAMPA_SUBE_S`, `MAX_SILENCIOS`, `SUBE_DESDE`, `ENV_HZ`: origen declarado «HANDOFF_F28 §B.2» en el docstring, no en DECISIONES.
- `anchor_timing.py:95` escalera 3 → 2 y `:105` mínimo 4 caracteres para el fallback de 1 token (origen: diag_235 / HANDOFF_135e en el docstring).
- `subs_remap.py:104` `0.05`, `:121` `0.01`: separaciones mínimas sin origen.
- `tts_normalizer.py:113-117` regex de horas AM/PM, dólares y porcentajes: F5 §1.4 en el comentario.

## Rutas de la cadena borrada (F41) que siguen vivas

- `audio_manager.py:54` `_NORMALIZED_NARRATION_FILENAME = "01b_narration_normalized.json"` y `:517` lectura de `data/scripts/_steps/<id>/01b_narration_normalized.json`; `script_engine/m02_5_normalizer_gate.py:639-642` lo escribe. Nombre y estructura (`narration_original`, `chapter_number`) son los del guion de antes de la cadena v4; hoy se alimentan de `01b_narration.json` que fase1_5 todavía produce para compatibilidad.
- `fase1_5.py:166-167` y `:570` leen `01a_skeleton.json` / `01b_narration.json` (los escribe `run_guion_v4`, `fase1_5.py:411`), y `audio_manager.process_script` toma `narrative_intent` de ese esqueleto (`audio_manager.py:799`). No es código de esta parte, pero es de donde cuelga.
- `fase2a.py:312-324` (camino SHORT: `audio_process(normalized, ...)`) es la única llamada a `process_script` fuera de fase1_5 y el form; con la cadena única «long» no está claro quién produce un topic SHORT.
- `audio_manager.py:456` comentario «guion v3 → v4», `audio_manager.py:805`: «guion v3» en comentarios; la cadena v3 (guionista v3) se borró en F41-A.
- `script_engine/m07_music_director.py:14` «INPUT: sync_map.json (post PR 2.A)», `:1063`: `topic_title = sync_map.get("video_id", topic_id)[:50]`: es el id, no el título (el comentario dice «fallback razonable»; se guarda en `topic_title` del descriptor).

## Imports dentro de funciones

- `audio_manager.py:120` import perezoso de `faster_whisper`: solo lo alcanza la rama muerta.
- `audio_manager.py:619` `from script_engine.tts_tags import transfer_tags` dentro de `generate_chapter_assets`: el módulo existe.
- `tts_normalizer.py:121, 136` `from script_engine.num_es import ...` dentro de `_num_text` y `normalize_pool_forms`: existe.
- `anchor_timing.py:48` `from tts_normalizer import normalize_for_tts` dentro de `_needle_normalized`, con `except Exception: pass` (`:50`): si el import fallara, el matcher seguiría con el anchor crudo sin avisar.
- `script_engine/music_intensity.py:157` `import wave` dentro de `aplicar_a_wav`.
- Ninguno de los imports de esta parte apunta a un módulo inexistente (`imports_rotos` de A confirmado vacío).

## Discrepancias con `estado_a` y otros hallazgos

- `patch_sync_map_mixing.py`: estoy de acuerdo con A (`huérfano`). Además corre código a nivel de módulo (lee/escribe `output/audio/7b52de57-.../sync_map.json` al ser importado, líneas 15-41): con solo importarlo reescribe el sync_map de Pripyat.
- `audio_profiles.py` y `audio_config.py`: A puso `etapas` hasta `render` (por import transitivo de fase2b). Leyendo el código, fase2b no las importa; el sync_map ya trae el bloque mixing (`fase2b.py:1957`). Las etapas reales son la voz y la planificación del guion por `voz_utils.narrador`; también las lee `mixer_server.py:41` (herramienta manual).
- `audio_manager.py` y `m07_music_director.py`: A los marcó alcanzados desde `research` y `assets`. En `research` no corren; en `assets` (fase2a) solo `process_script` del camino SHORT (`fase2a.py:324`), y solo si el topic no es «long».
- `music_config.py`: la función `validate_music_config` (191) exige exactamente los 7 intents de `MUSIC_PROMPTS` aunque la paleta de F28 defina 6; `generate_music_map` la llama siempre (`m07:1047`).
- Intent `resolution`: está en `MUSIC_PROMPTS` y en `VOICE_SETTINGS_BY_INTENT*`, no en `PALETA_INTENTS`; un capítulo `resolution` sin pista de paleta en la biblioteca cae al camino de generación con ElevenLabs (m07:1134), con gate interactivo si `music_gate_interactive` es True.
- `script_engine/m07_music_director.py:1101` lee `c.get("paleta")` de los descriptores de `audio_library/*.json`, campo que no figura en el esquema documentado en `_load_library` (m07:107-111) ni en `track_data` de `_generate_new_track_with_gate` (956-978).
- `script_engine/m07_music_director.py:352`, `:439`, `:1066` usan `error_handler.log_info(PipelineStage.AUDIO...)`; docstring de cabecera (26-28) anota deudas #167/#168 (sin cost_tracker para Music, `PipelineStage` sin MUSIC): el gasto de música no pasa por `cost_tracker` (`cost_usd: None`, m07:967). `generar_con_plan` tampoco registra costo.
- `script_engine/m02_5_normalizer_gate.py:699-709` en modo batch aplica TODOS los spans del LLM sin revisión y los recurrentes se escriben al diccionario global `data/normalizer_custom_dict.json` (persist_dict=True por defecto, no pasado por `fase1_5.py:541`).
- `audio_manager.py:630-639` la invalidación por `tts_hash` se evalúa solo si existe `meta_path`; con audio sin meta el código usa `prior_hash=None` y regenera. Funciona, pero depende del orden de dos `if` seguidos.
- `tts_normalizer.py:228` ejecuta `_load_custom_dict()` al importar y `m02_5_normalizer_gate.py:555` lo vuelve a ejecutar tras cada alta: las entradas ya cargadas se reasignan (idempotente para dicts, el `set` no duplica).
