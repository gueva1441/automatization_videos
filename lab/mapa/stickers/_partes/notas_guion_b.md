# Notas de auditoría — zona guion, parte guion_b

Materia prima para F43. Todo leído de la primera a la última línea (12 archivos, 3 936 líneas). Sin proponer cambios. Los md5 de los 12 archivos al terminar coinciden con los de A.

Los `estado_a` de A (los 12 `vivo`) coinciden con lo que leí: ningún import roto (nombres y funciones importadas existen; verificado por AST).

## Código muerto o inalcanzable

- `script_engine/m01d_particion.py:372` `cut_phrases`: nadie la llama. `guion_v4.py:16` y `:1022` la nombran solo en comentarios («patrón de m01d.cut_phrases»); un script de lab (`f10_quirurgico_ycua.py`) la menciona.
- `script_engine/tts_tags.py:30` `strip_tags`: sin llamador de producción; solo `test_module_f9.py`, `test_module_f10.py` y `lab/hyperframes/f10/f10_seco_orleans.py`.
- `script_engine/tts_tags.py:26` `SLOWLY_WPS = 2.4`: ninguna línea de código lo lee; solo aparece en el docstring (`:12`).
- `script_engine/tts_tags.py:62` `slowly_dev`: `m01d_particion.py:236` llama `build_contract` sin pasarlo, así que en producción es siempre `False`; la rama `[slowly]` en párrafos de desarrollo solo se alcanza desde tests (`test_module_f9.py:42`) y lab (`f9_voz.py`).
- `script_engine/tts_tags.py:22` `TAG_RE` acepta `[pause]`; nada del módulo emite esa etiqueta.
- `script_engine/m01b_narrator.py:120-121` y `:176-184`: los parámetros `f5` y `min_factor` de `_validate_narration` no los pasa el único llamador de producción (`m01b_guionista.py:141`); la rama «reglas del evidence_pool» (`kind="evidence"`) solo corre en tests. `_len_range(min_factor)` (`:115`) igual.
- `script_engine/m01b_guionista.py:47` `INSTITUTION = institution_re()`: constante sin ningún lector; el código llama `institution_re(ficha)` directamente (`:168`).
- `script_engine/m01b_guionista.py:26` `import json`: no se usa en el archivo.
- `fase1_5.py:59` `parse_decisions_csv` y `OUTPUT_CSV`: importados y nunca usados (solo se usa `export_single_topic_csv`).
- `fase1_5.py:858` `--sin-columna`: se acepta y «no cambia nada» (lo dice su propio help); `--editor` (`:868`) es «solo para leer».
- `fase1_5.py:632` `visual = assign_visual_prompts(...)`: la variable no se usa después.
- `script_engine/video_length.py:30-33` `gate_yellow_pct`, `gate_yellow_target_words`, `gate_yellow_max_beats`, `gate_yellow_min_beats_dev_cap`: ningún código de producción los lee (solo el docstring de `m01a_escaleta.py:711` y tests `test_module_f8.py:43`), aunque los comentarios dicen «informativo» / «queda para el reporte».
- `script_engine/m01b_narrator.py` `NarrationValidationError.__init__` (`:78`) y los campos `kind/detail`: el docstring (`:72-75`) los justifica por «el retry», que se borró en F41.

## Dos lógicas para lo mismo / duplicado

- `fase1_5.py:212-227` `_step_cost` y `script_engine/m01e_pantalla.py:1192-1218` `main` repiten la misma lógica (leer/escribir `01_v3_costos.json`, `start_video`/`end_video`, `_corridas`).
- `fase1_5.py:139-152` `_load_topic_by_id` relee `topics_db.json` a mano mientras el mismo archivo importa `load_db`/`save_db` de `topics_db` (`:73`) y los usa en el paso 0 (`:644`).
- `fase1_5.py:58` y `:215`: `cost_tracker` importado arriba y otra vez dentro de `_step_cost`.
- `fase1_5.py:76` `VALID_FROM_STEPS` y `:81` `_PIPELINE_ORDER`: dos listas de los mismos pasos.
- `script_engine/nombres.py:34` `norm` y `:167` `plegar`, y la `norm` de `evidence`: tres normalizadores de texto con reglas parecidas (la docstring de `nombres.norm` dice que da «lo mismo que el evidence_pool.norm de antes»).

## Rutas de la cadena borrada (F41) que siguen vivas o con rastro

- `script_engine/m01d_particion.py:5-11`: el docstring dice que escribe «los mismos archivos que dejaban m01a_skeleton + m01b_narrator» y habla de «escaleta → guionista → editor»; esos módulos ya no escriben esos archivos.
- `script_engine/m01d_particion.py:256-264` / `:276` `regenerate_cap_v3` sigue viva (la llama `guion_v4.py:1151`); el sticker semilla dice que se borró `regenerate_cap` (otra función, la de F10): fácil de confundir.
- `script_engine/m01b_guionista.py:50-52` y `:240-243`: los carteles «Prompt» y «Escritura (best_of_2)» quedaron sin código debajo (era el guionista v3 borrado).
- `script_engine/m01c_editor.py:121-123`: cartel «Edición con validación» sin ninguna función de edición debajo (`edit` se borró).
- `script_engine/m01a_skeleton.py:27-28`: el comentario «NO se le pide a Flash que la decida» habla de un estructurador que ya no existe. El archivo ya no genera ningún skeleton; el `01a_skeleton.json` lo escribe `m01d_particion.py:243`.
- `fase1_5.py:111`, `:131` y `m01d_particion.py:223`: `humanizer_phrases` viaja siempre vacío; el propio docstring lo llama «deuda técnica heredada».
- `fase1_5.py:14-16` y `:65-67`: el juez m05/m06 «sigue vivo en el repo», pero `m05_judge` no tiene ningún importador de producción (solo tests y lab).
- `script_engine/name_matching.py:3-11`: se describe a `m05_judge` como consumidor; en producción el único consumidor real es `m03_visual.py:105`.

## Comentarios que contradicen el código

- `fase1_5.py:34` y `:835` (help de `--topic`): «default: todos los aprobados del CSV»; el código en `:921-930` dice lo contrario (sin `--topic` abre el menú de un tema, ya no corre batch del CSV).
- `script_engine/m01e_pantalla.py:17-19`: «UNA a Sonnet 5.5» y «contando las dos llamadas»; desde F38d (`:25-27`, `llamar`) hay vueltas de reintento hasta agotar motivos o tope.
- `script_engine/m01b_guionista.py:11-13` (docstring): gancho «sin año, cifra ni institución»; el código (`:168-169`) trata la institución como blanda y solo año/cifra como dura.
- `script_engine/m01b_guionista.py:227-228` marca como dura «el video tiene N palabras: el tope es …», mientras `video_length.py:12` dice que `max_words` «ya no frena el guion v4» y `guion_v4.py:949` que el tope ya no frena (va a métrica; la dura solo queda informada en `duras_v3`, `guion_v4.py:1222`).
- `script_engine/m01b_narrator.py:72-75`: el docstring lista los `kind` «empty | length | first_sentence | phrase | other»; el código también levanta `kind="evidence"` (`:182`).
- `script_engine/video_length.py:20-23`: el comentario dice que el tope de 12 beats «deja exactamente 12»; la línea siguiente fija `max_beats: 14` (F8b).
- `script_engine/tts_tags.py:12`: «medido: ver `voz_v4.wps`»; no existe ningún módulo `voz_v4` en el repo (solo `lab/hyperframes/f9/f9_voz.py`).

## Números sin origen a la vista (no están en DECISIONES, la identidad F3 ni un estándar citado en el mismo archivo)

- `script_engine/m01d_particion.py:74` `max(200, len(último) - over - 40)` (el 200 y el 40 del objetivo de acortado); `:31` `LEN_TOL = 0.15` (dice «±15 %» de F10 §2, sin cita de decisión).
- `script_engine/m01e_pantalla.py:722` `chars / 2.5` (caracteres a tokens): «la de siempre de §C.2», sin dato medido a la vista.
- `script_engine/m01b_guionista.py:32-36` `MIN_WORDS_FACTOR 0.85`, `SHORT_WORDS 6`, `LONG_WORDS 30`, `WORDS_TOL 0.15`, `MIN_HUMAN_CAPS 3`; `:218` `len(sur) > 3` y la ventana de ±200 caracteres; `:207` `[:40]`.
- `script_engine/m01b_narrator.py:29` `HOOK_FIRST_SENTENCE_MAX_WORDS = 12`; `:150` y `:159` ventanas de 200 caracteres para aperturas y cierres.
- `script_engine/m01a_skeleton.py:58-59` `SCREEN_PER_CAP = 2`, `SCREEN_MUST = (6, 7)` (F5d); `:146` bono `+2` si la fecha cae en el rango; `:156` umbral `>= 2`; `:126` `>= 2` palabras en común.
- `script_engine/tts_tags.py:23-26` `GOLPE_MAX_WORDS 6`, `GOLPE_MAX_PER_CAP 2`, `GOLPE_MIN_INTENSITY 4`, `SLOWLY_WPS 2.4`: el docstring los da como reglas sin cita de medición (el 2.4 ni se usa).
- `script_engine/name_matching.py:29` `_MIN_LAST_NAME_LEN = 5` y la lista `COMMON_LAST_NAME_BLACKLIST` (`:16-21`).
- `script_engine/num_es.py:74` rango de años 1900–2099 y `:87` corte `hh < 8` para «de la tarde»/«de la noche».

## Dependencias raras entre fases / estado global

- `script_engine/m01e_pantalla.py:199-200`: la Fase 1 importa código de Fase 2 (`gfx_realizador.beat_de_pantalla`, `music_intensity.beat_pico_de_cap`); `:62-64` importa nombres privados de `voz_utils` (`_analiza`, `_PARTICULAS`, `_palabra_en`, `_raiz_en`); `:816-856` usa privados de `claude_helpers` (`_post`, `_base`, `_track`, `PRICES`).
- `script_engine/m01a_skeleton.py:107`: `assign_screen_ids` (Fase 1) importa `gfx_pool._kicker` y `pool_clause_options` (Fase 2, privado el primero).
- `script_engine/m01b_guionista.py:43` usa `nombres._ORG` (privado); `m01d_particion.py:37` usa `m01b_narrator._len_range` (privado).
- `script_engine/nombres.py:28`/`:105`: `_tratamientos` y `_grupos` son estado global de proceso que cambian `set_tratamientos`/`set_grupos`; `fase1_5.py:872` ya lo reconoce («el perfil del caso es un global de proceso») y por eso `--temas` lanza un proceso por tema; `_topic_v3` (`fase1_5.py:205`) recarga el perfil en cada llamada.
- `script_engine/m01b_narrator.py:22-25`: `LEN_HOOK/LEN_DEVELOPMENT/LEN_OUTRO` se calculan al importar el módulo leyendo `config.long_video`; un cambio de config después del import no se ve.
- `script_engine/m01d_particion.py:93-110` y `:360`: `editor_shorten` y la regeneración usan `call_pro_json` (clave `gemini_model_research`) aunque el guion corra con `--modelo` de otro proveedor; el título usa `call_flash_json` (`gemini_model`). Es coherente con el help de `--modelo`, pero son tres modelos distintos dentro de «guion».

## Fuera de la cadena de costos

- `fase1_5.py:643-649` (paso 0, foto madre) corre fuera de `_step_cost`: su gasto (`openai/gpt-image-2`) no queda en `01_v3_costos.json`. Es el seam que ya registra la memoria del proyecto; acá solo anoto el renglón.
- `fase1_5.py:574` la voz (ElevenLabs) y `:599` la música (m07) tampoco pasan por `_step_cost`.

## Etapas (para el mapa)

- `fase1_5.py` corre en tres etapas: `guion` (`--batch`: m01a + m01b + papel de m01e), `papel` (`--aprobar-papel`: solo `aprobar_papel`/`md5_papel`) y `voz` (`--from normalizer_gate --batch`: normalizer gate → voz → m07 → m03 → foto madre → assemble). `m01d_particion`, `m01b_guionista`, `m01b_narrator`, `m01c_editor` y `m01e_pantalla` (la escritura) corren solo en `guion`; la normalización de las etiquetas de voz (`tts_tags.transfer_tags`) y `name_matching` (m03) corren en `voz`.
- `m01e_pantalla` además se lee en `guion_pantalla` y `render` (por `pantalla_entrada`, que importa `_texto_item`, `TIPO_DE_ESTILO` y `cargar_papel`), y `fase2b --plan-edit` (`fase2b.py:3738`, a mano) escribe con `editar`.
- `nombres`, `num_es`, `m01a_skeleton` y `video_length` son compartidos: A los marca en las 10 etapas por alcance transitivo; por lectura, los puse en las etapas donde de verdad se importan y se llaman (ver `etapa` en el JSON).

## Otros

- `_lab_name_scrub.py:7` (raíz del repo, sin versionar): `from name_matching import ...` y `import m05_judge`, sin el prefijo `script_engine.`; no corre tal cual. Fuera de mi parte; solo lo anoto.
- `script_engine/m01d_particion.py:252` `ParticionError` se define después de la función que la levanta (`particionar`, `:247`); funciona en tiempo de ejecución.
- `script_engine/m01b_guionista.py:96-98` y `script_engine/nombres.py:49-56`: aliases de una línea («F21: alias») que dejan dos nombres para lo mismo (`_surname` y `nombres.apellido`).
- `script_engine/name_matching.py`: ningún archivo de test lo importa (`tests` vacío en A); lo cubren de rebote los tests de `m05_judge`.
