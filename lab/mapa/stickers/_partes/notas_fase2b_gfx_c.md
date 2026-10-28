# Notas de auditoría — zona fase2b_gfx, parte fase2b_gfx_c

Los 11 archivos se leyeron enteros. Los md5 de los 11 coinciden con los de A al terminar. Todos los `imports_rotos` de A dan [] y lo verifiqué: los nombres que importa gfx_lab_server.py (`fase2b._build_plans`, `_load_script_lookup`, `_route_safe`, `_safe_scenes_for`, `gfx_layer.remapped_words/build_scenes/snap_cuts/assign_quiet_sides/_ffprobe_duration`, `gfx_director.load_chapter_context/question_keyword`, `gfx_project.write_project/cue_events/plan_transitions`, `gfx_literal_lock.lock`, `gfx_style._CROWD/_PERSON/_PLACE/suggest_movement`) existen.

## gfx_lab_server.py
- gfx_lab_server.py:273-276, 382-388: `question`, `summary` y `save_identity` son stubs que solo lanzan RuntimeError («borrado en F36 D»); siguen cableados en las rutas (`/question` GET:614 y POST:659, `/summary` GET:637 y POST:670, `/save_identity` POST:672), así que esas rutas devuelven siempre HTTP 500.
- gfx_lab_server.py:208, 367, 370: `lab_plan`, `_catalog` y `_sugerencias` sin ningún llamador (ni tests); `_sugerencias` apunta a `lab/identidad/sugerencias_<cap>.json` (existe sugerencias_ch02.json). Los tests de sugerencias (test_module_gfx_lab.py:199, 226) leen el archivo por su cuenta.
- gfx_lab_server.py:20-26: la docstring documenta como vigentes rutas ya borradas en F36 (`/question`, `/summary`, `/save_identity`) aunque las marca «borrados»; en cambio no documenta `/api/profile` ni `/objetos` con el mismo detalle.
- gfx_lab_server.py:128 `TAIL_SEC = 4.5` y 448 `pausa` clamp a TAIL_SEC; 407-409 `MOV_SAFE`/`SALIDA_KIND`: números y tablas del lab sin origen citado en DECISIONES (el comentario dice «pregunta 3 s + corte a negro 1 s + margen» pero `question_pause_sec` y `black_hold_sec` salen del perfil: 3.0 y 0.0 por defecto en gfx_config.py:266-267, no 1 s).
- gfx_lab_server.py:52 `DEFAULT_VIDEO` fijo en un id de video concreto (ba6c3cac-…) y 53 `_HF_DIST` ruta a node_modules de hyperframes: dependencia de datos y de paquete de una corrida específica.
- gfx_lab_server.py:686: mensaje «ch01 lleva pre-pad del hook» y 122 `time_offset = 0.0`: el lab ignora `title_pre_roll` (gfx_config.py:204, con --gfx el cap arranca con title_dur de title card sin voz, F30b B.3), así que el preview puede desalinearse en cualquier cap, no solo en ch01.
- gfx_lab_server.py:425-428: `transition_frames.get(...)` y `r.dip_frames` leídos de gfx_project.gfx_rules; la clave `"R3"` se usa como piso con `r.transition_frames["R3"]` (KeyError si un perfil trae transition_frames sin R3).
- gfx_lab_server.py:488-491: `rules_override` filtra HUERFANAS_TOKENS pero `save_lab_state` (línea 217) valida contra `_rule_fields()` sin filtrar huérfanas; un plan guardado con un token huérfano pasa al guardar y se ignora al previsualizar.
- gfx_lab_server.py:472: import a nivel módulo después de las clases (`# noqa: E402,F401`), con `_CROWD/_PERSON/_PLACE` importados y no usados en el archivo.
- gfx_lab_server.py:149 `import subprocess` dentro de la función, sin otra razón visible.
- Estado: coincide con `solo herramienta manual` de A. Ningún módulo de producción ni `run_pipeline` lo lanza.

## mixer_server.py
- mixer_server.py:54-55: `PROFILE_NAME = "MISTERIO_ABISAL"` y `TOPIC_ID = "8286b193-…"` cableados; `_set_topic` los re-apunta en main pero `PROFILE_NAME` no tiene argumento.
- mixer_server.py:60-67: `HEADROOM_DB = 10.0`, `BAND_LO_HZ/BAND_HI_HZ`, `MV_CLAMP = (0.05, 0.40)`, `MVF_CLAMP = (0.03, 0.30)`: números sin origen en DECISIONES (el comentario dice «editable, no es veredicto»).
- mixer_server.py:256-279 `_build_mix_filter`: espejo manual del filter_complex de fase2b `_mix_music_into_video` (la propia docstring admite la «DEUDA» de que queda stale si cambian los params de mixing); dos lógicas para lo mismo.
- mixer_server.py:99-109 `_find_ffmpeg_binary`: lookup de ffmpeg replicado de fase2b (comentario lo dice); mixer_server.py:133-148 resolución cap→track replicada de fase2b.
- mixer_server.py:359-363 `_rerun_command` lanza `fase2b.py <TOPIC_ID>` sin flags: reproduce el comando de FONDOS (sin gfx), no el render con --gfx --gfx-sparse; el botón «Re-armar» no regenera el video final con capa gráfica.
- mixer_server.py:74-75 y 296: carpeta de salida `_mixer_renders_chat40` con nombre de chat 40; el archivo es de 2026-06-02 (último commit 59435e9), anterior a toda la cadena F29+.
- mixer_server.py:3527 en fase2b.py referencia `python mixer_server.py` como camino para calibrar la pista antes de publicar: único vínculo vivo con el resto del pipeline.
- Estado: coincide con A (`solo herramienta manual`). Nota: `lanza {'fase2b.py': [363]}` de A es cierto pero solo ocurre con el botón Re-armar, no al arrancar.

## script_engine/transition_applier.py
- transition_applier.py:1: el docstring dice `modules/transition_applier.py` (ruta vieja); el módulo vive en `script_engine/`.
- transition_applier.py:445-552 `concat_with_transitions` (xfade encadenado con perfiles de arte) y 59-196 `resolve_position`/`build_transition_plan`/`_XFADE_MAP` son el camino «sin --gfx»; `concat_windowed` (340) es el camino con gfx. Con --gfx las transiciones de los perfiles de arte nunca se aplican (línea 364-367 las pisa por «corte_negro»), de modo que dos lógicas de unión conviven; `plans` en 361 se calcula igual aunque con `negro_frames` se descarta.
- transition_applier.py:365 `TransitionPlan(i, "corte_negro", 0.0)`: el nombre `corte_negro` no existe en `TRANSITION_INVENTORY` (transition_config.py:60-124) ni en `_XFADE_MAP` (137-145); solo se usa como etiqueta.
- transition_applier.py:144 `_XFADE_MAP["hard_cut"] = "fade"` con duración 0 se corrige a mínimo 0.04 s en 174; el comentario dice «≈ corte seco».
- transition_applier.py:134-136: comentario dice que whip_pan_flash se aproxima con fadewhite (no es un whip real); la descripción de transition_config.py:64 promete motion blur + flash + reentrada borrosa. Comentario y código no coinciden.
- transition_applier.py:279 `WINDOW_SEC = 1.0` («spec: ±1 s») y 203-216 `5× realtime`, pisos 300/600/900: números con origen solo en comentarios.
- transition_applier.py:428-429: audio final con `b:a 192k`, y 396-398 timeout `300` por ventana; sin origen en DECISIONES.
- transition_applier.py:30-35, 36-40: importa `is_valid` y `NARRATIVE_POSITIONS` y no los usa en el archivo (solo `get_effect`, `transition_render`, `DEFAULT_TRANSITION`, `get_default_transition`, `is_allowed`).
- Estado: `vivo` coincide con A. A marca etapas fondos/guion_pantalla/aprobar_guion/render por el import de fase2b arriba; leyendo el código solo se ejecuta en fondos (preview sin gfx) y render (con --gfx).

## gfx_config.py
- gfx_config.py:306-319: `zoom_min_scene`, `css_grade_variant`, `css_grade_opacity` sin llamador en producción (la primera ni en tests); la hermana `css_grade_intensity` (314) sí se usa (script_engine/gfx_layer.py:627, en un log).
- gfx_config.py:277-278: el comentario de `auto_icons` quedó cortado («categoría, nunca un adjetivo, sin game-icons automáticos)») con la frase de apertura borrada.
- gfx_config.py:44-46: comentario de `workers` cita «DECISIONES: 2026-10-25» y «lab v1» a la vez; el segundo texto («sin shaders (D5) → 5 workers») es de otro período.
- gfx_config.py:58 `stitch_nvenc` «= fase2b.NVENC_ARGS»: duplicado manual de una constante de fase2b.
- gfx_config.py:100-183 `_ENGINE_INVENTORY`: describe bloques que HUERFANAS_BLOQUES (380) y el catálogo F36/F37 dieron por borrados en parte (la regla de `chapter_question` habla de las «bullets del PRÓXIMO CAPÍTULO», pero el comentario 265 dice que la pregunta ahora es el `cierre` del último beat); `LLM_BLOCKS` (484) se calcula con `llm_decides` aunque el borrador del director se borró en F37 B.4.
- gfx_config.py:203 `forma_variante` (F31), 268 `peak_blocks` («gfx_peak»; el comentario de gfx_lab_server.py:182 dice que `plan_peak` se borró) y otras perillas de F3/F4: perillas cuya lectura no verifiqué una por una; las huérfanas declaradas están en 377-384.
- gfx_config.py:284-286: `theme_words` con vocabulario de un tema concreto (reclusos, prisioneros, cárcel…) como default del motor, no del perfil.
- gfx_config.py:362: `except Exception` genérico al leer nicho_config; import de `nicho_config` dentro de función.
- gfx_config.py:366-370: `active_profile_name` abre TODOS los *.json de gfx_profiles (también lexico_propuestas, critico_fewshot y golden, que no son perfiles) buscando `nichos`; los tres devuelven dict y `.get("nichos", [])` no falla, pero se leen como perfiles.
- gfx_config.py:480: `ACTIVE_PROFILE = load_profile()` al importar: cualquier clave desconocida en el perfil activo rompe el import de todos los módulos que dependen de gfx_config (efecto colateral global).
- gfx_config.py:44, 332-336: `_PROFILE_KEYS` incluye `costos` y `sellos_clima`, pero `channel_bug` figura en HUERFANAS_CLAVES (384) y misterio.json todavía la trae (se saca en memoria, `PERFIL_HUERFANAS` la anota).
- gfx_config.py:343-344: `ICON_KEYS` (14 claves) y gfx_lab_server.py:12 dice «los 12 íconos del set»; el comentario en gfx_config.py:342 dice que es igual a `gfx_icons.ICON_WHITELIST`. Número del texto (12) no coincide con el conjunto (14).
- Estado: `vivo` coincide. A marca research/guion/papel/voz/assets…; leyendo, se usa en guion (papel con m01e_pantalla/clima/pantalla_colocar), fondos, guion_pantalla, aprobar_guion y render; no encontré uso en voz, assets ni packaging.

## transition_profiles.py
- transition_profiles.py:332-340 `render_constraints_for_prompt` muerta («director futuro» que no existe); transition_profiles.py:19-20 dice que la aplicación vive en «parallax_animator_v2.py o en un futuro modules/transition_applier.py»: ninguno de los dos nombres existe así (el aplicador es script_engine/transition_applier.py).
- transition_profiles.py:36-44: `NARRATIVE_POSITIONS` incluye `intra_chapter`, que `resolve_position` (transition_applier.py:59-83) nunca devuelve.
- transition_profiles.py:58-280: 12 art_profiles; `whitelist` solo se usa en `render_constraints_for_prompt` (muerta); en producción solo pesan `blacklist` y `default_by_position`.
- Estado `vivo` coincide; etapas fondos/render (no corre en guion_pantalla ni aprobar_guion).

## transition_config.py
- transition_config.py:172 `clamp_duration_ms` muerta; transition_config.py:178 `render_inventory_for_prompt` también sin llamador en producción (el nombre existe igual en flow_config.py:115, que es el que importa script_engine/flow_director.py:31; A no la marcó por la coincidencia de nombre).
- transition_config.py:141-144 `transition_param_ranges` solo la usa `clamp_duration_ms` (muerta).
- transition_config.py:30-33 `fps: int = 30` («debe coincidir con flow_render.fps») sin lector en este archivo ni en transition_applier; `crf`, `preset`, `pix_fmt` y `video_codec` solo se usan en `concat_with_transitions` (camino sin gfx); con --gfx solo pesa `audio_codec` (transition_applier.py:431).
- transition_config.py:60-124 `ffmpeg_filter` de cada efecto (ej. «fade+boxblur+white_frame») es texto sin lector.
- transition_config.py:11-12: dice que la selección vive en «modules/transition_director.py cuando se implemente»; ese módulo no existe.
- Estado `vivo` coincide.

## gfx_profiles/*.json (solo claves de primer nivel)
- misterio_critico_fewshot.json: claves `fuente`, `ejemplos`; nadie lo lee desde que F36 §D borró el crítico viejo (script_engine/gfx_critic.py:11); lab/ESTADO_SESION.md:775 todavía lo cita como vigente. Estado que puse: huérfano. Tracked en git.
- misterio_golden_ch02.json: claves `profile`, `video_id`, `cap`, `saved_at`, `plan`, `rejected_by_lock`, `tokens`, `anotado`, `marks`; ningún código lo abre; es copia de referencia del lab F3 (saved_at 2026-10-20 01:20). Estado: huérfano.
- lexico_propuestas.json: no tiene claves de perfil (name/tokens…), es un diccionario palabra → datos con 78 entradas; vive en la carpeta de perfiles pero no es un perfil. Lo escribe gfx_intensity.record_proposals (llamado en gfx_layer.py:683) y lo lee el barrido de gfx_config.py:366.
- misterio.json: trae `channel_bug` (clave huérfana, gfx_config.py:384) e `identity` (gfx_config.py:333-334: «lo escribe el lab; el motor lo ignora»); además contiene tokens que gfx_config.py:377-379 declara huérfanos (se sacan en memoria; PERFIL_HUERFANAS los lista). No miré valores.
- finanzas.json: claves `name`, `description`, `nichos`, `fonts`, `tokens`, `blocks` (sin `moods`, `sfx` ni `sellos_clima`); `nichos = ['finanzas']`: solo se activaría con ese nicho o GFX_PROFILE=finanzas; no tiene `moods`, así que `active_moods()` daría vacío con él.
- Hay `gfx_profiles/misterio.json.bak_f3_20261020_012038` (respaldo viejo) en la misma carpeta; no es de mi parte pero el barrido de gfx_config.py:366 usa `glob("*.json")` y no lo recorre.

## Discrepancias con A
- `estado_a` de A coincide con mi estado en los 6 .py. Para los 5 json A dijo `vivo` en todos; yo puse `huérfano` para misterio_critico_fewshot.json y misterio_golden_ch02.json.
- Las `etapas` de A para los .json y gfx_config.py incluyen packaging, research y voz/assets por alcance de import; leyendo, no se aplican ahí.
- Candidatas de A confirmadas: las 8 (3 en gfx_lab_server.py, 3 en gfx_config.py, 1 en transition_profiles.py, 1 en transition_config.py). Descartadas por ser del framework http.server: `LabHandler.log_message`, `LabHandler.do_HEAD`, `LabHandler.do_POST`, `Handler.log_message`, `Handler.do_POST`.
