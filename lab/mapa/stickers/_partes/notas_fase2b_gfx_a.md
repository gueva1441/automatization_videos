# Notas de auditoría — zona fase2b_gfx, parte fase2b_gfx_a

Archivos leídos enteros: fase2b.py (3841 líneas), script_engine/aprobacion.py (74), script_engine/freeze_check.py (44). md5 al terminar iguales a los de A (c81d7e20…, b5fed4ae…, edbec655…).

## fase2b.py

### Código muerto o inalcanzable
- fase2b.py:553 `_chars_to_syllables` y fase2b.py:593 `_build_ass_from_syllables`: sin llamador en producción; solo tests de chat 38 y dos scripts sueltos de la raíz (`_regen_alignments_chat38.py:22`, `_smoke_chat38_ch01.py:15`).
- fase2b.py:44 y :550 `import pyphen` / `_DIC_ES`: se carga al importar el módulo y solo lo usa la rama de sílabas muerta; `mixer_server.py:15` y `qa_studio_server.py:10` lo citan como la razón para no importar fase2b.
- fase2b.py:2647 `GFX_PARALELO = 1` («DESCARTADO»): deja inalcanzables `_segmentos_en_paralelo` (:2781) y el bloque `if paralelo` (:3391-3402); solo `test_module_f28c.py` los ejerce forzando la constante a 2.
- fase2b.py:3665 `--hw-encode`: bandera aceptada que no hace nada (el propio comentario de :3707 lo dice); `_HW_ENCODE` ya vale True por defecto.
- fase2b.py:839 `_build_flux_visual(..., art_profile)`: el parámetro no se usa en el cuerpo; fase2b.py:970 `_concat_visual_clips(..., work_dir)` tampoco (el docstring de :993 lo admite).

### Dos lógicas para lo mismo
- fase2b.py:1946 `_mix_music_into_video` (ruta chat 32 y ruta chat 39) y fase2b.py:2098 `_grafo_musica` arman el mismo grafo de sidechain/amix con cadenas copiadas; la primera solo corre si falla la mezcla «audio solo» (:3595-3603).
- Los defaults de mezcla (0.25, 0.0, 0.03, 8, 80, 200) están repetidos en fase2b.py:1879-1880, :1988-1994, :2102-2107 y :2145-2150, sin una constante común ni origen citado.
- fase2b.py:593-655 `_build_ass_from_syllables` repite la cabecera (:621-632) y el evento de Hook (:639-655) que ya existen como `_ass_header` (:255) y `_ass_hook_event` (:274).
- fase2b.py:86 `_find_ffmpeg_binary`, fase2b.py:161 `_get_duration` y fase2b.py:192 `_merge_punctuation_words` tienen copias en `audio_manager.py:71`, `audio_manager.py:133`, `mixer_server.py:99`, y `_get_duration` también aparece en `mixer_server.py` y `script_engine/transition_applier.py` según el mapa de A.
- fase2b.py:1424 `_load_script_lookup` soporta short y long; fase2b.py:2600 `_route_safe` lee otra vez el mismo data/scripts/<id>.json, solo mira `chapters` (long) y arma `prompts_by_cap` a mano.
- fase2b.py:1433 `_load_script_lookup` arma la ruta con `Path("data")` relativo al directorio de trabajo, mientras :1555 y :2597 usan `DATA_DIR`; depende de desde dónde se lance.

### Números sin origen declarado
- fase2b.py:347 y :684 el `+ 0.3` s de cola del último subtítulo; fase2b.py:326 `max_chars=26` y `words_per_chunk=3` del karaoke de Shorts.
- fase2b.py:224-246 `_calc_hook_layout`: 1800 px, 0.55, topes 180/140/80 de fuente; fase2b.py:249-252 los estilos Viral (Anton 150, Outline 10, Shadow 5, MarginV 108) y Hook (Anton 128, Outline 8): solo el de F40 documenta «derivado/estándar».
- fase2b.py:136 `MUSIC_CROSSFADE_SEC = 2.0` («estándar documental», sin cita); fase2b.py:150 `INITIAL_SILENCE_SEC = 2.5` y fase2b.py:107 `HOOK_DURATION = 1.8` con origen «chat 32» pero sin decisión citada.
- fase2b.py:2646 `CLIP_WORKERS = 6` (origen F28 §C.3 en comentario, sin medición adjunta); fase2b.py:2651 `NVENC_ARGS` preset p5 y cq 23 (origen F29, comentario de peso).
- fase2b.py:3078 `VENTANA_S, BUSCA_S = 4.0, 20.0` y :3076 `sr = 11025`: rotulados «derivado» con razonamiento corto.

### Comentarios o textos que contradicen el código
- fase2b.py:12 y :26 (docstring del módulo): «1 call a Gemini Flash por art_profile distinto» y «~$0.0001 por art_profile»; hoy `_dispatch_flow_specs` (:2211) hace una sola tanda por todas las imágenes del video, y el zoom_judge y el router también llaman a Gemini.
- fase2b.py:14 (docstring): «karaoke 3-words» como si fuera el único registro; desde F40 el long-form va con subtítulos documentales (`_build_ass_documental`).
- fase2b.py:3666 `--hw-encode` dice «h264_nvenc p5 cq19»; `NVENC_ARGS` (:2651) usa cq 23 (el comentario de :2651 documenta el cambio, el texto de ayuda quedó viejo).
- fase2b.py:1232-1238 el bloque de comentario habla solo del karaoke por palabra («INTENCIONAL»); la rama real ahora bifurca en :1258 por `video_type`.
- fase2b.py:3280 y :1553 hablan del «flow_director» como único consumidor de Gemini en este módulo; en `_solo_plan` (:3192-3197) se suman los costos de Gemini (crítico, visión) y Claude que vienen de otros módulos.
- fase2b.py:3379-3380 comentario F37 sobre «sin el borrador del director» queda suelto sobre el `if plan_only`, sin código que lo explique.

### Rutas o nombres de la cadena v3 (F41) que siguen vivos
- fase2b.py:1559 y :3178: leen `01a_escaleta.json`, `01b_narracion_v3.json` y `00_pool_v3.json` de `data/scripts/_steps/<id>/`. Los tres siguen produciéndose (m01d_particion, research_v3), así que no están rotos; el sufijo `_v3` quedó en nombres de archivo de la cadena nueva.
- fase2b.py:1559 `_mapa_intensidad` devuelve None sin avisar si falta cualquiera de los tres archivos (la música sale plana sin envolvente).

### Comportamientos raros
- fase2b.py:3799 `plan_only=args.plan_only and mode == "single"`: en modo batch (sin video_id) `--plan-only` fuerza `--gfx` y `--reuse-visuals` (:3744-3746) pero no corta en el plan, y renderiza el batch completo con gfx.
- fase2b.py:3640-3643 el modo batch (sin video_id, lee topics_db por `assets_rendered`) no es lo que usa run_pipeline (siempre pasa el id); queda como entrada manual.
- fase2b.py:3719-3732 `--aprobar-guion` parte el argumento por espacios y toma la última palabra como fecha; si el texto viene «Omar» solo, `fecha` queda None y aprobacion.py:51 pone la hora de la máquina.
- fase2b.py:1564, :2426 y :2618 varios `except Exception` anchos (router de retratos, mapa de intensidad, depth_probe) que degradan en silencio a «sin visión / sin envolvente / gate OFF» con un print; el render sigue sin que quede registro fuera del log.
- fase2b.py:3282-3284 `cost_tracker.start_video` solo si no hay video en curso; con `--plan-only` el costo del crítico se atribuye al video activo (el de la corrida viva del form), no a uno propio.
- fase2b.py:3316 `--only-cap` no escribe flow_plan.json pero sí escribe flow_specs.json (:3312), así que tiene un efecto lateral fuera del cap.

### estado_a de A
- fase2b.py: coincide (vivo).

## script_engine/aprobacion.py
- aprobacion.py:8 «El hook … usa `estado()`»; coincide con guard_render.py:89. Además `estado()` lo llaman run_pipeline.py:127 y gfx_layer.py:507, no solo el hook.
- aprobacion.py:47 compara mtime de planes contra mtime del guion: depende del reloj del disco, sin tolerancia.
- aprobacion.py:23 `planes` solo la usan las funciones del propio archivo (A la marca viva por eso; no es muerta).
- gfx_layer.py:507 asume que el `work_dir` es `output/<id>/_fase2b_work` (usa `Path(work_dir).parent` como topic_dir); si cambia la estructura, `estado` da «no existe el guion» sin error visible.
- estado_a de A: coincide (vivo). La etapa de A es la de fase2b porque lo importa fase2b.py; leyendo, aprobacion también corre en el orquestador (run_pipeline) y en el hook de Claude Code.

## script_engine/freeze_check.py
- freeze_check.py:2-7 dice «Uso: después del render de fase2b, sobre cada `_fase2b_work/chNN_gfx.mp4`», pero ningún script de producción ni etapa del form lo invoca; solo `test_module_f10.py:161` y la línea de comandos.
- freeze_check.py:23 llama a `ffmpeg` por nombre (PATH), a diferencia de fase2b.py:86-100 que busca el binario de winget como respaldo.
- freeze_check.py:17 `NOISE = 0.002` sin origen citado (MIN_SEC sí lo razona en comentario).
- freeze_check.py:34 `check(..., allow=…)` nunca recibe `allow` desde la línea de comandos (freeze_check.py:44), así que por CLI las pausas y el negro de la pregunta de cierre cuentan como congelados.
- A marca `check` con muchos llamadores (ficha_caso, research_v3, m01a_escaleta): son otras funciones con el mismo nombre, no este módulo (nadie lo importa); la cuenta de A para `check` no es de este archivo.
- estado_a de A: coincide (solo herramienta manual).
