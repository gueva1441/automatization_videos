# Notas de auditoría — zona fase2b_gfx (F42 §B)

Materia prima para F43: lo raro que vio cada worker leyendo su parte entera, con archivo:línea. Sin propuestas.

<!-- parte fase2b_gfx_a -->
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

<!-- parte fase2b_gfx_b -->
# Notas de auditoría — zona fase2b_gfx, parte fase2b_gfx_b

Solo lectura. Archivos leídos enteros: los 14 de la parte (gfx_layer 854 líneas, gfx_project 853, gfx_guion 715, gfx_sparse 437, gfx_safe_bake 163, gfx_review 111, gfx_style 174, 6 plantillas/CSS y gfx_grade.json). Los md5 de los 14 archivos coinciden con los de A al terminar. Cada línea es un hallazgo con `archivo:línea`; no hay propuestas.

## Código muerto o sin productor

- `script_engine/gfx_guion.py:431` `_ocupa` no la nombra nadie (ni producción, ni tests, ni strings). Con ella, el parámetro `title_dur` de `chequeos` (`gfx_guion.py:440`) quedó sin uso dentro de la función (fase2b lo sigue pasando en `gfx_guion.py:643`).
- `script_engine/gfx_guion.py:342` `cortes_cap(plan, rejected, sents)`: el parámetro `sents` no se usa en el cuerpo.
- `script_engine/gfx_sparse.py:61-63, 71-72, 73, 81-84` `event_windows` y `gfx_sparse.py:189-221` `compose_sparse` manejan `count_up`, `icon_array`, `water_level` y `evidence_zoom` (con `latido_t`). Ningún módulo de producción escribe esas claves en el plan (grep en `script_engine/`, `fase2b.py`, `gfx_lab_server.py`: solo aparecen en `gfx_project`, `gfx_sparse`, `gfx_guion` y como nombres en `gfx_config`; `plan_base` en `gfx_layer.py:493-496` no las trae). Son ramas que nunca se ejecutan con un plan real.
- `script_engine/gfx_project.py:182` `quote_card_html` y su uso en `gfx_project.py:802-807`: el único productor del plan es `plan["quote_card"] = None` (`script_engine/pantalla_colocar.py:175`, `gfx_layer.py:495`); nadie lo llena con una cita. Solo se alcanza con un plan armado a mano (lab server, tests).
- `script_engine/gfx_project.py:81-84` y `gfx_project.py:85-86` en `_anim_in_js`: las ramas `number_pop` y `slide` no tienen llamador; solo se llama con `"stamp"` (`gfx_project.py:741`) y `"cascade"` (`gfx_project.py:796`). Los tokens `pop_from_scale` y `pop_sec` de `gfx_config.py:254-255` quedan colgados de esas ramas.
- `script_engine/gfx_templates/gfx_common.css:18-33` (`.callout`, `.co-mask`, `.co-text`, `.co-rule`), `gfx_common.css:41-48` (`.co-ico`, `.ar-ico`, `.count`, `.count-unit`) y `gfx_common.css:59-62` (`.zlabel`, `.zrect`): ningún HTML que genere el código usa esas clases (el dato con lupa, el contador y el ícono se borraron; la ficha usa `.tc-box`). Los tokens `callout_font`, `callout_anton_px`, `stamp_px`, `ar_ico_pad` que `gfx_project.py:619-635` (`render_css`) sigue sustituyendo solo alimentan esas reglas. `gfx_project.py:784` pasa `icon_html=""` fijo a `archive_clipping.html.tmpl`.
- `script_engine/gfx_templates/gfx_grade.json` (todo): nadie lo lee. Solo lo recuerda `gfx_layer.py:7-8` («el preset nativo queda versionado»). El grade real sale de `GRADE_VARIANTS` (CSS) y de `gfx_sparse.vignette_png/grain_png`.
- `script_engine/gfx_style.py:31` `_STOP` (conjunto de palabras vacías): definido y no usado.
- `script_engine/gfx_style.py:7-16` el docstring promete `identity_transitions()` y `select_punches()`; ninguna de las dos existe en el archivo (las reemplazó `transiciones_por_relato`, `gfx_style.py:107`).
- `script_engine/gfx_layer.py:631` y `gfx_layer.py:291` siguen importando de `script_engine/gfx_director.py` (`load_chapter_context`, `question_keyword`) aunque el director (el que armaba el borrador del plan) se borró en F37 B.4: queda el módulo como proveedor de contexto, con el nombre viejo.
- `script_engine/gfx_review.py:39` y `gfx_layer.py:496`: `gap_warnings` siempre vale `[]` (`plan_base` lo fija vacío y no hay otro productor), así que la sección «gap_warning» de `gfx_cues_chNN.md` sale siempre «(ninguno)». `gfx_config.py:196` `interrupt_max_sec` solo se usa para ese título.
- `script_engine/gfx_style.py:153-174` `identity_violations` cuenta transiciones `flash` y `cut_punch` y `flash_max_per_cap`; `transiciones_por_relato` (`gfx_style.py:107-150`) solo produce `zoom_punch`, `dissolve`, `dip` y `cut`. Esas dos comprobaciones no pueden dispararse con las transiciones de hoy.
- `script_engine/gfx_style.py:34-50` `suggest_movement` con `already_out=False` (rama «alejar», `gfx_style.py:49`): `movement_for` solo la llama con `already_out=True` (`gfx_style.py:59`); la otra rama solo la alcanza el lab server.
- `script_engine/gfx_guion.py:36-38, 42` y `gfx_guion.py:370-399` (`TIPO_ROT`, `TEXTOS`, `ANIMACIONES`, tablas de `cortes_cap`): siguen listando tipos de bloques borrados en F36 D: «lupa», «nivel de agua», «contador», «icono», `water_level`, `count_up`; y `gfx_guion.py:270` `cb.get("kind") == "name"`. Ningún productor actual los emite.

## Dos lógicas para lo mismo

- Transiciones: `script_engine/gfx_project.py:337` `plan_transitions` decide por `emotional_rank` (R1 flash, R3 dip/disolvencia) y es el respaldo de `transitions_of` (`gfx_project.py:329-334`); `script_engine/gfx_style.py:107` `transiciones_por_relato` decide por el relato y el docstring de F30b dice «el emotional_rank no decide nada». Las dos conviven: la segunda solo corre con `real` y `identity_rules` (`gfx_layer.py:784`), si no, vale la primera.
- Grade: el CSS (`gfx_common.css:66-74`, viñeta y grano con saltos) y el ffmpeg del disperso (`gfx_sparse.py:238-265` y `gfx_sparse.py:409-421`) son dos implementaciones del mismo look; el comentario de `gfx_sparse.py:239-243` copia a mano los números del CSS (`0.85`, `0.42`, `0.62`, `0.6`). `gfx_layer.py:627` escribe «grade: CSS intensidad …» en el log también cuando va el camino disperso, que no usa el CSS.
- Movimiento seguro: el mismo acercar/alejar/paneo vive en `gfx_project.py:446-468` (gsap, para la ruta sin bake) y en `gfx_safe_bake.py:36-56` (ffmpeg, la ruta con `safe_bake`), más el estado final del freeze en `gfx_project.py:370-375`.
- Valores del re-encode duplicados: `gfx_sparse.py:231-232` fija `-preset ultrafast`, `-crf 14` y `-g 30` en el código; `gfx_config.py:42-60` ya los tiene como `reencode_preset`, `reencode_crf`, `reencode_gop` (que sí usan `gfx_layer.py:97-100`, `gfx_layer.py:242-244` y `gfx_safe_bake.py:70-73`).
- Medidas del title card en dos lugares: `gfx_project.py:577` (`TC_LEFT, TC_RIGHT = 180, 180`) dice ser «los del CSS», y el CSS los tiene literales en `gfx_common.css:11-14`.
- `LECTURA_CPS = 15.0` definido dos veces: `script_engine/gfx_guion.py:31` y `script_engine/pantalla_colocar.py:19` (esta última es la que importa `gfx_layer.py:278`).
- `from gfx_config import gfx_rules as r` dentro de `archive_head_px` (`gfx_project.py:646`) repite el import de arriba (`gfx_project.py:36`); `import re` dentro de `_gray_frames` (`gfx_layer.py:177`) repite `gfx_layer.py:23`.

## Comentarios o docstrings que contradicen el código

- `script_engine/gfx_layer.py:576` «gfx_plan_override: … None → director + lock»: hoy None arma `plan_base` + papel + candado (el director se borró, F37 B.4; el propio docstring del módulo, `gfx_layer.py:9-10`, lo dice).
- `script_engine/gfx_layer.py:580` «plan_only: director + candado + crítico + cues» (mismo caso).
- `script_engine/gfx_layer.py:288` el docstring de `closing_question` cita `pantalla_entrada.LECTURA_CPS`; el código importa `pantalla_colocar.LECTURA_CPS` (`gfx_layer.py:278`).
- `script_engine/gfx_project.py:1-22` el docstring describe un plan con `callouts [{text,start,kind}]`, `count_up`, `archive_clipping` (singular) y `evidence_zoom`, y `public/fonts/Anton-Regular.ttf`; el código copia tres fuentes (`gfx_project.py:687`) y ya no dibuja contador ni lupa.
- `script_engine/gfx_project.py:235` y `gfx_project.py:607` citan `.co-text.stamp` como molde de la placa de la ficha; esa regla es CSS sin uso (`gfx_common.css:27-28`) y la placa real es `.tc-box.ficha .tc-kicker` (`gfx_common.css:17`).
- `script_engine/gfx_review.py:5` y `gfx_review.py:36` hablan de «omisiones/descartes del director» y «Notas del director»; el director ya no existe. `_NOTE_RE` (`gfx_review.py:19`) pesca hoy líneas como «sfx descartado» de `gfx_layer.py:451`.
- `script_engine/gfx_guion.py:3-4` «corre director, rotulista, reglas y crítico»; `gfx_guion.py:30` `VERSION = "f36-c"` con el último cambio del archivo en F38e (commit 68e6c41); `gfx_guion.py:410-412` y `gfx_guion.py:692` siguen rotulando «director · rotulista».
- `script_engine/gfx_sparse.py:3-5` lista «count_up, zoom» entre los eventos que abren ventana (no existen, ver arriba).
- `script_engine/gfx_layer.py:626` y `gfx_layer.py:627`: el paso «2 grade» se loguea siempre, aunque en el disperso (`gfx_layer.py:379-380`, `grade=False`) no hace nada.

## Números sin origen (ni DECISIONES ni estándar citado en el código)

- `script_engine/gfx_layer.py:208` umbral `6.0` de cambio entre cuadros para anclar el corte; `gfx_layer.py:167` y `gfx_layer.py:211` margen `0.3` s; `gfx_layer.py:226-233` tercios `0.4/0.6`, franja `0.7` y escala `160×90`; `gfx_layer.py:439` instante `0.05` s y `0.03` s del golpe del title card; `gfx_layer.py:449` «≥ 7 letras» de palabra acentuada.
- `script_engine/gfx_sparse.py:252-254` `GRAIN_SIGMA 0.14` (dice «calibrado»), `GRAIN_PAD 360`, `XFADE_FRAMES 4` (cita «nocturno §3», un handoff, no DECISIONES); `gfx_sparse.py:145` `FULL_COVER_FRAC 0.95` (F10 B1); `gfx_sparse.py:49-50` `margin 0.5` y `merge_gap 2.0`; `gfx_sparse.py:45` y `gfx_sparse.py:305` duración `0.35` s del `cut_punch`; `gfx_sparse.py:403` `crf=16`.
- `script_engine/gfx_project.py:113-171` capas de mood (14 partículas, semilla `1441`, opacidades `0.38/0.35/0.85/0.5`, letterbox `0.10`); `gfx_project.py:261` kicker del reloj `64` px y `gfx_project.py:264` `left/right:150px; top:64px`; `gfx_project.py:638-639` `HEAD_CHAR_W 0.58` y `HEAD_STEPS (1.0, 0.85, 0.72)` (G2 de F5e); `gfx_project.py:583` `kick_top = 380` y las constantes `190`, `900` de `tc_metrics`.
- `script_engine/gfx_style.py:26` `PEAK_CLEAR_SEC = 5.0`; `gfx_style.py:103-104` `ZOOM_PUNCH_SCALE 1.4` y `ZOOM_PUNCH_MS 400` (cita «transition_config», no DECISIONES).
- `script_engine/gfx_guion.py:33-35` `PICO_DB -18`, rampa `0.10` s, ventana `0.01` s (declarados en el docstring como lectura de F32_REPORT); `gfx_guion.py:122` `buscar_s 0.5`, `gfx_guion.py:131-132` `sr = 16000` y `seg = 1.5`; `gfx_guion.py:60` y `gfx_guion.py:68` tolerancia `0.3` s de `_beat_at`/`_oracion_en`.

## Otros

- `estado_a` coincide con lo que leí en los 14 archivos (13 vivos, `gfx_grade.json` huérfano). Discrepo de las etapas de A en cuatro casos: A pone `research…render` a `gfx_project.py`, `gfx_style.py` y a las plantillas/CSS porque los scripts de etapa los alcanzan por import; leyendo, `gfx_style` corre en `guion_pantalla` y `render`, las plantillas y el CSS solo en `render`, y `gfx_project` corre en `guion` (por `m01e_pantalla.validar`, `script_engine/m01e_pantalla.py:406`, que ejecuta `fase1_5.run_pantalla`), `guion_pantalla` y `render`. `gfx_layer`, `gfx_guion`, `gfx_sparse`, `gfx_safe_bake` y `gfx_review` coinciden con A (con `gfx_guion` solo en `guion_pantalla` y `gfx_review` en `guion_pantalla` y `render`; el `fondos` y `aprobar_guion` que A les suma no ejecutan estos módulos: `run_pipeline.py:365` lanza `fase2b.py <id>` sin `--gfx` y `--aprobar-guion` no ensambla, `fase2b.py:3719`).
- `lanza` de A está vacío en los 6 módulos .py, pero todos arman comandos de `ffmpeg`/`ffprobe` (y `gfx_layer` además `node …/hyperframes.mjs`) con `subprocess.run`: `gfx_layer.py:55, 71, 101, 245, 406`, `gfx_sparse.py:230, 247, 262, 431`, `gfx_safe_bake.py:70, 82, 150`, `gfx_project.py:320`, `gfx_guion.py:85`.
- A marcó `gfx_guion._pcm`, `armar` y `a_markdown` con llamadores en `script_engine/m01e_pantalla.py` y `chequeos` con `fase2b.py` como «string»: son coincidencias de nombre (m01e_pantalla no importa `gfx_guion`; `armar` y `a_markdown` son sus propias funciones). Lo mismo con `gfx_sparse.stitch_transitions` en `gfx_config.py` (es el token `stitch_transitions` de las reglas, no la función).
- `script_engine/gfx_layer.py:637` `pe, pc, clima, vd` solo se enlazan dentro de `if rot_on:`; más abajo (`gfx_layer.py:699, 709, 717, 767-779`) se usan guardados por la misma condición, pero dependen de ella para no fallar.
- `script_engine/gfx_layer.py:810` `if sparse and not debug`: con `--gfx-debug` el cap va por el camino completo aunque se pida disperso.
- `script_engine/gfx_project.py:675` el parámetro `grade_variant` de `write_project` no lo pasa ningún llamador de producción; el único que toca las variantes es el lab server (`gfx_lab_server.py:503`, que reemplaza `GRADE_VARIANTS`).
- `script_engine/gfx_safe_bake.py:155` si `bake` falla antes de llegar a `tmp.rmdir()`, la carpeta `_base_cocido` y sus clips quedan en `public/` (la limpieza solo está en el camino feliz).
- Modelos: ninguno de los 14 archivos llama a un LLM directamente. `gfx_layer` invoca, desde otros módulos, a gfx_intensity (Flash), gfx_vision y gfx_critic (visión/crítico) solo cuando el plan no es el congelado (`gfx_layer.py:651, 670, 758-765`), o sea en `guion_pantalla`, no en `render`.

<!-- parte fase2b_gfx_c -->
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

<!-- parte fase2b_gfx_d -->
# Notas de auditoría — zona fase2b_gfx, parte fase2b_gfx_d

Los 12 archivos se leyeron enteros. Ninguno cambió de md5 durante el trabajo (no se tocó ninguno). Todas las rutas son de `script_engine/` salvo que se diga otra cosa.

## Código muerto o sin uso (más allá de las 4 funciones confirmadas)
- `gfx_pool.py:79` `literal_icon_map`: solo la llama `content_icon` (muerta); en producción tampoco la nombra nadie. Con ella quedan sin uso `MISSING_ICONS` (45), `_PEOPLE` (49) y `_NEVER_ICON_ALONE` (53).
- `gfx_pool.py:404` `FORMA_CALL`: constante que nadie lee (el «paso de forma de los recortes» se borró).
- `gfx_pool.py:407` `_hits`: nadie la usa; `evidence.py:122` tiene su propia `_hits` con otra firma.
- `gfx_pool.py:411` `_NUM`: regex sin ningún uso en el archivo ni fuera.
- `gfx_pool.py:361-363`: cabecera «S2 — cronología» sin código debajo.
- `gfx_pool.py:376-377` y `clima.py:61`: leen/cuentan `quote_card`, bloque que `pantalla_colocar.py:175` deja siempre en `None` (F36 D lo borró). Ojo: `gfx_project.py:530,802` y `gfx_guion.py:286` también lo leen, o sea que el bloque sigue en el render aunque ya nadie lo llena.
- `gfx_intensity.py:30` `MIN_CARGAS`: no se usa (solo `MAX_CARGAS`). `gfx_intensity.py:56` `_plain`: no se usa.
- `gfx_vision.py:37` `HUMAN`, `:50` `_plain`, `:54` `_tok`: no se usan en el archivo y nadie los importa.
- `gfx_realizador.py:175` `FUENTES_CIERRE`: tupla que nadie lee (las fuentes se devuelven como strings sueltos).
- `gfx_realizador.py:226` `finalizar(plan, real, log)`: el parámetro `real` no se usa. `gfx_realizador.py:250` `cerrar(...)`: `pool` y `side` no se usan (gfx_layer.py:781-783 igual los pasa).
- `gfx_literal_lock.py:44-45` `lock(..., question_sources=…)`: el parámetro no se usa («queda por compatibilidad del lab»); gfx_layer.py:704/725 igual lo pasa.
- `gfx_realizador.py:128` `candidatos` (con `ya_dicho`, `_voz_en`, `ya_mostrados`): lo que calcula solo termina en un log (gfx_layer.py:272) y en `gfx_beats_<cap>.json`; ningún consumidor lee `real["candidatos"]` para decidir nada. Los `ya_mostrados` además los fabrica `gfx_pool.used_ids_before` en gfx_layer.py:267 solo para esto.
- `pantalla_entrada.py:155` `"ya_mostrado": []`: la clave de la entrada siempre va vacía y nadie la lee (el filtro «ya mostrado» está en `pantalla_colocar.py:201` con `used_before`).

## Comentarios y docstrings que contradicen el código
- `pantalla_filtros.py:227`: dice «pantalla_entrada.del_papel»; esa función no existe (la que hace eso es `pantalla_entrada.preparar_cap`).
- `pantalla_filtros.py:251` (comentario sobre `ORDEN`): menciona `escena_final`, que `pantalla_colocar.py:296` dice que `repartir` reemplazó.
- `pantalla_filtros.py:2-3` y `pantalla_colocar.py:3`: «antes pantalla_filtros» / «antes pantalla_colocar» (el nombre nuevo igual al viejo; parece un reemplazo masivo que pisó el nombre anterior).
- `gfx_realizador.py:17` y `gfx_layer.py:254-255,262`: dicen que sin escaleta gfx_layer «sigue por el camino de siempre»; desde F37 el papel es el único camino y sin escaleta (`rot_on` falso, gfx_layer.py:634) el cap sale sin fichas ni sellos.
- `gfx_realizador.py:6-14`: el docstring de módulo sigue describiendo candidatos obligatorios/opcionales y topes como si decidieran algo; hoy solo sirven de log.
- `gfx_pool.py:2` («Todo detrás de `if pool`: un guion sin pool sigue con verified_facts exactamente como antes») y `gfx_pool.py:4-9`: describen funciones que ya no existen (`pool_clause_options` se presenta como de gfx_pool, pero la usa solo `m01a_skeleton` vía `finalize_pool_plan`).
- `gfx_pool.py:120`: «piezas de gfx_fragments (borrado)»; el módulo `gfx_fragments` ya no existe y las piezas viven acá.
- `gfx_critic.py:87-88` (`build_prompt_rot`): el prompt promete «IMAGEN 2: el mismo instante con el bloque ya dibujado», pero `estorba` (gfx_critic.py:159) llama con una sola imagen (`call(Path(img), prompt)`); el prompt dice que hay dos y se manda una (el docstring de estorba dice «foto sola»).
- `gfx_critic.py:83`: el prompt siempre incluye «EL ROTULISTA DICE QUE APORTA: «»» con texto vacío, y pide tres respuestas (`SCHEMA_ROT` las exige todas, :73-77) aunque solo cuenta `estorba`.
- `gfx_critic.py:23` / `pantalla_colocar.py:225-226`, `:189`, `:339`: siguen los nombres `rotulista`, `tipo_rotulista`, `critico_rotulista` de un módulo que se llama ahora `pantalla_*` (`gfx_literal_lock.py:70,74` filtra por `c.get("rotulista")`, o sea que ese nombre viejo es el que decide qué pasa por el candado).
- `gfx_pool.py:137`: línea con un bloque largo de espacios en medio (`and bool(...)` pegado tras 9 espacios), resto de una continuación de línea; funciona pero no se lee.
- `pantalla_colocar.py:173`: comentario «filtros importa este módulo arriba» (import circular: `pantalla_filtros.py:15` importa pantalla_colocar al tope y pantalla_colocar importa pantalla_filtros dentro de `colocar`).

## Números sin origen claro (no figuran en DECISIONES, identidad F3 ni estándar citado en el mismo archivo)
- `pantalla_colocar.py:221` `era_decade: 2000` fijo para todo recorte tipo documento, sea de la época que sea.
- `pantalla_colocar.py:208-210,214-216`: `side: "left"` fijo en fichas/citas (comentado solo como «la del title card»).
- `gfx_pool.py:455` `t < last + 2.0` y `:461` `start + 12.0`, `:458` tope de 2 cambios: constantes sueltas sin nombre (solo `TICKER_HOLD` 4.0 y `TICKER_MIN` 2.0 tienen nombre y comentario F5f).
- `gfx_pool.py:145` `DOC_MAX_WORDS = 10`, `:481` `COUNT_SAME_TOL = 0.15` (comentado «±15 %»), `:494` umbral `n < 100`: origen F5b/F5e, no una decisión citada.
- `gfx_critic.py:147` `dur` por defecto 2.5 s, `:61` «1 s después de que entra / a mitad si dura menos de 2 s», `:45` ancho 1280, `:188-211` medidas de la hoja de contactos (640, 62, 19, 15, 88): sin origen.
- `gfx_vision.py:38` `MIN_CONF = 0.6`, `:63` lados de caja 0.06–0.3 (repetidos también dentro del texto de `SYSTEM`, :41-42), `:85` tope de 3 detalles: sin origen citado.
- `gfx_intensity.py:29-31` `ATTEMPTS = 2`, `MAX_CARGAS = 5`, `ASK_CARGAS = 10`: citados a «F4c R1», no a una decisión de Omar.
- `pantalla_colocar.py:19` `LECTURA_CPS = 15.0` sí cita su origen (§0 estándar de subtitulado); `pantalla_filtros.py` usa `LECTURA_CPS` importado.

## Rutas o nombres de la cadena vieja que siguen
- `gfx_realizador.py:39` lee `01b_narracion_v3.json` (nombre «v3» con el guion v4 vigente); también `fase2b.py:1559`. La partición lo sigue escribiendo con ese nombre (`m01d_particion.py:243`), así que es consistente pero el nombre quedó de F10.
- `gfx_pool.py:12-34`: el docstring conserva la historia de F5b–F5f (recortes, contador, cita) de bloques borrados; el propio texto dice «quedan como referencia».
- `gfx_director.py:47` cita «DOC_MAESTRO §6» para una deuda de `verified_facts` sin id; no se verificó que siga vigente.

## Otras cosas raras
- `estado_a` de A coincide en los 12 archivos (todos «vivo»); la diferencia está en las etapas: A marca casi todos con `research`…`render` porque `fase1.py`, `fase2a.py`, etc. alcanzan estos módulos por import. Leyendo el código: `aprobar_guion` no corre ninguno (fase2b.py:3719-3732 solo llama `script_engine.aprobacion.aprobar`); `fondos` (fase2b sin `--gfx`) no los corre (el import de gfx_layer es perezoso, fase2b.py:1213); `research`, `papel` y `voz` tampoco. En `guion` corren los que importa `m01e_pantalla`/`m01a_escaleta`/`m01a_skeleton` (fase1_5.py:434 `run_pantalla`; gfx_pool, pantalla_filtros, pantalla_colocar, gfx_realizador.beat_de_pantalla, clima.vocabulario_clima, gfx_peak vía voz_utils).
- Cuatro de las capas que usan modelo o crítico están detrás de tokens del perfil con default `False` en el dataclass (`gfx_config.py:268-279`: `peak_blocks`, `intensity_director`, `photo_first_zoom`, `visual_critic`); `gfx_profiles/misterio.json` trae esas claves, pero el valor que realmente rige no se leyó (regla de la tanda). Por eso `gfx_intensity`, `gfx_vision` y `gfx_critic` están marcados «vivo» pero su ejecución real depende de esos valores. `realizador` (default `True`, gfx_config.py:195) no está en el perfil.
- `voz_datos.py:22` importa `gfx_realizador._raices` (función privada) desde otro módulo; `gfx_realizador.py:91` a su vez usa `evidence._FUNC` y `evidence._content` (privados de otro módulo).
- `gfx_pool.py` es importado por `m01a_skeleton.py`/`m01a_escaleta.py` (Fase 1) y por la capa gráfica (Fase 2): sirve a dos etapas distintas; cualquier cambio de este archivo afecta `guion` y `render`.
- `gfx_intensity.py:129,139`: la regla `_stamp_rule()` (token `stamp_nouns_only`, default `False`, gfx_config.py:280) condiciona dos validaciones; si el perfil lo deja en `False`, las cargas verbales y las palabras del tema no se filtran.
- `pantalla_filtros.py:195-222` `lectura`: la variable `antes` se incrementa con `antes += 0 if entran else 1` (cuenta solo los fallos previos al primer éxito); funciona, pero la lógica de `movido_corte` depende de ese contador y no está probada en ningún test que nombre `lectura` (A: `tests` de `lectura` = 0 en la lista de funciones).
