# F41 — Una sola cadena y el form de punta a punta — REPORTE

Handoff `lab/hyperframes/f41/HANDOFF_F41_una_cadena_y_el_form.md` (md5 `bd6361b318b107c6428a9d549f10d70a`). Rama `f11-guion-v4`, base `5c6d9cb`. Modelo: Opus 5.5 (medium). Sesión abierta por pedido de Omar desde la de F38e–F40b («abrí sesión nueva sin perder el hilo»).

Pedido literal de Omar (palabra por palabra):

> /tanda F41 — Una sola cadena y el form de punta a punta. Omar confirma: ritmo de imágenes el de producción (7,0 s, sin cambio) y fondos del --plan-only con el fase2b sin gfx existente.
>
> LECTURAS (antes de tocar nada): CLAUDE.md; DECISIONES.md; el handoff ENTERO lab/hyperframes/f41/HANDOFF_F41_una_cadena_y_el_form.md (verificá md5 bd6361b318b107c6428a9d549f10d70a); .claude/commands/tanda.md; lab/MAPA_MODULOS.md; run_pipeline.py, fase1_5.py, fase1.py enteros; topic_researcher.py (research_topics, investigar_semilla, _enrich_with_seed_metadata); qa_studio_server.py (sección FORM ASISTIDO y rutas /form*); qa_form.html; qa_form_markers.py; test_run_pipeline.py.
>
> PASO 0 (en serie):
> 1. lab/TOPE_TANDA.json → {"usd": 0.00, "desde": "<ahora>"}.
> 2. Agregá AL FINAL de DECISIONES.md esta línea tal cual: [línea 2026-10-27 20:59, ver DECISIONES.md]
> 3. Commit SOLO de DECISIONES.md + el handoff, con los dos md5 en el mensaje.
>
> TRABAJO (usá todos los subagentes en paralelo que el trabajo permita):
> - Subagente A = Parte A del handoff (fase1_5, topic_researcher, fase1). Interfaz que NO cambia: `fase1_5 --topic <id> --batch`, `--from normalizer_gate`, `--aprobar-papel "QUIÉN FECHA"`, `--semilla … --topic …`, `estado_papel(id)`.
> - Subagente B = Parte B del handoff (run_pipeline, qa_studio_server, qa_form.html; qa_form_markers solo si hace falta), contra esa interfaz.
> - A y B corren a la vez; un commit por parte. Cada parte termina con SU SALIDA EN TEXTO (A.3 y B.8 del handoff) en lab/hyperframes/f41/a/ y f41/b/.
> - Borrar, no apagar: lo que queda sin llamador se borra con sus tests (por nombre); lo que tenga otro llamador vivo se anota y no se borra.
> - Mapa de módulos regenerado al final.
>
> REGLAS FIJAS:
> - US$ 0: PROHIBIDO correr fase1_5/fase2a/fase2b reales, llamar APIs, aprobar papel o guion de ningún topic, tocar main.
> - No cierres ningún programa de Omar (DECISIONES 00:30), tampoco desde subagentes.
> - Ningún número nuevo: si hace falta uno → PARADA y preguntá.
> - Ningún `cat` suelto antes de un heredoc.
>
> VALIDACIÓN (en serie, al final): tests nuevos de B.1–B.6 con stubs; suite rápida; suite amplia; candado de ch02 de Orleans con lab/hyperframes/f40/verificar.sh (debe dar f792f3d4… con subs y 98386f86… con --no-subs). Después, subagente revisor-handoff contra el handoff; su veredicto va ÍNTEGRO.
>
> CIERRE: lab/hyperframes/f41/F41_REPORT.md con: módulos tocados (hoy → después), salidas A.3 y B.8 (tablas, no archivos enteros), lista de lo borrado, suites, «lo que queda abierto» entero y el veredicto íntegro del revisor. NO pegues documentos enteros en el reporte (papel, guion de pantalla): están en disco con md5. Actualizá lab/ESTADO_SESION.md, commit, push a origin/f11-guion-v4. PARADA.

## Lecturas declaradas
`CLAUDE.md`; `DECISIONES.md` (con 20:59); el handoff entero (md5 ✓); `.claude/commands/tanda.md`; `lab/MAPA_MODULOS.md`; `run_pipeline.py` entero; `fase1_5.py` (conocido de F39–F40b, y los subagentes lo leen entero); `fase1.py` (estructura, auto-chain a `fase1_5.run_one_topic_from_menu`); `topic_researcher.py` (`research_topics`, `investigar_semilla`, `_enrich_with_seed_metadata`, de F39); `qa_studio_server.py` (sección FORM ASISTIDO, `_form_command`, rutas `/form*`); `qa_form_markers.py`. `qa_form.html` y `test_run_pipeline.py` los lee entero el subagente B (dueño de esos archivos).

## Paso 0
1. `lab/TOPE_TANDA.json` = `{"usd": 0.00, "desde": "2026-10-27T21:03:52"}`.
2. Línea 2026-10-27 20:59 agregada al final de `DECISIONES.md`, tal cual.
3. Commit (solo `DECISIONES.md` + el handoff): `DECISIONES.md` md5 `f2bbbdfe7cb753a6ce324909945fba9c`, handoff `bd6361b318b107c6428a9d549f10d70a`.

## Constantes
Ninguna nueva. Las del handoff son todas existentes o derivadas: tope US$ 0,00 (la tanda no llama a ninguna API); ritmo de imágenes 7,0 s (`m03_visual.SECONDS_PER_IMAGE_TARGET`, sin cambio; confirmado por Omar); fondos del `--plan-only` = `fase2b <id>` sin gfx (código cero; confirmado por Omar); flags del render final `--reuse-visuals --keep-segments --gfx --gfx-sparse` (ESTADO, «Video completo»).

## Cómo se corrió
- Paso 0 en serie. **A y B en paralelo**, un subagente cada uno, con archivos separados (A: `fase1_5.py`, `topic_researcher.py`, `fase1.py` y sus tests; B: `run_pipeline.py`, `qa_studio_server.py`, `qa_form.html`, `qa_form_markers.py`, `test_run_pipeline.py`) y la interfaz fija del pedido. En cada brief: «no cierres ningún programa de Omar (DECISIONES 00:30)» y «US$ 0: no corras fase1_5/fase2a/fase2b reales ni llames APIs». Un commit por parte. Validación en serie al final; revisor al final.

## Módulos tocados (hoy → después)
| módulo | hoy | después |
|---|---|---|
| `fase1_5` (A) | dos cadenas (vieja y v3) elegidas por `guion_version` o `--v3 --guion`; guionista v3 junto al v4 | una sola cadena (F39 + guion v4); `is_v3_topic`, `is_v4_guion`, `--v3`, `--guion`, `run_guion_v3` y las ramas viejas borrados; sin pool v3 → PARADA antes de gastar desde cualquier paso; compuerta del papel siempre |
| `topic_researcher` (A) | no guarda `video_type` | `research_topics` guarda el pedido; `investigar_semilla` guarda `long` |
| `fase1` (A) | auto-chain a `fase1_5.run_one_topic_from_menu` | sin cambios: llega a la única cadena sola |
| `m01a_skeleton`, `m01b_narrator`, `m01b_guionista`, `m01c_editor`, `m01d_particion`, `m01a_escaleta` (A) | traen la cadena vieja (`generate_skeleton`, `generate_narration`, `write`, `edit`, `regenerate_cap`, `is_v3`) | solo queda lo que tiene llamador vivo (tabla de A abajo); `m01a_escaleta` y `m01d_particion` con sticker nuevo en el mapa |
| `run_pipeline` (B) | GUION → ASSETS → VISOR → `fase2b` sin gfx → fase3; la PARADA del papel se leía como «m06» | GUION → PAPEL → VOZ → ASSETS → VISOR → FONDOS → GUION DE PANTALLA → RENDER gfx → fase3; `etapa_de` de solo lectura y retomar sin re-pagar; RAM medida antes del render (B2) |
| `qa_studio_server` (B) | lanza solo `--research` | además `/form_topics` y `/form_resume` (retomar con `run_pipeline --topic <id> --batch`) |
| `qa_form.html` (B) | gates seed_pick, judge_action, visor_gate, remeasure_pick | más `papel_gate` y `guion_gate` con el documento entero (bloque monoespaciado con scroll) y lista «Retomar» |
| `qa_form_markers` | — | sin cambios (no hizo falta) |
`run_pipeline`, `qa_studio_server`, `qa_form`, `fase1_5`, `topic_researcher`, `fase1` y los m01* viejos no están en el mapa (que es de la capa gráfica y lo que la alimenta). Mapa regenerado: 35 módulos · 116 aristas · 0 muertos.

## A — Una sola cadena (`fc59a76`, subagente A)
**A.1 Lista previa** antes de borrar: `lab/hyperframes/f41/a/A1_lista_previa.md` (grafo AST con llamadores calificados; producción = raíz + `script_engine/` + `researcher_steps/` + `tools/`; `lab/`, `_lab_*`, `diag_*` y tests no cuentan).

**Lo borrado (llamadores en producción = 0):**
| archivo: símbolos | tests borrados por nombre |
|---|---|
| `fase1_5.py`: `is_v3_topic`, `is_v4_guion`, `run_guion_v3`; flags `--v3`, `--guion`; parámetros `v3`/`guion` de `process_topic`; ramas m01a vieja (`generate_skeleton`), m01b vieja (`generate_narration`) y m01b v3; `topic["guion_version"] = 3/4` | `test_module_f10::test_cuando_corre_v3`, `::test_sin_flag_corre_el_camino_viejo`; `test_module_f11::test_v3_byte_identico`, `::test_v3_sigue_por_su_camino_y_v4_por_el_suyo` (+ auxiliares `_fake_pro`, `_run_v3`, `V3_GOLDEN*`, `BANDAS_F23`); `test_module_f22::test_dorado_v3_solo_cambian_los_mensajes_de_f22`; `test_module_f23::test_dorado_v3_solo_cambian_las_bandas` |
| `script_engine/m01a_escaleta.py`: `is_v3` | `test_module_f6b::test_flag_v3_y_camino_v2` |
| `script_engine/m01a_skeleton.py`: `generate_skeleton`, `frozen_skeleton`, `SkeletonValidationError` y 12 auxiliares, 8 constantes que solo usaban ellos | archivos enteros `test_module_01a.py` (script manual) y `test_module_01a_evidence.py` (5 tests); `test_module_f5c::test_skeleton_congelado_traduce_ids_y_saca_lo_que_no_esta` |
| `script_engine/m01b_narrator.py`: `generate_narration`, `regenerate_caps` y 20 auxiliares de prompts/reintentos/esquemas, 12 constantes (`F5_RULES`, `PROSE_RULES`, `TONE_INSTRUCTIONS_BY_INTENT`, `POOL_*`, …) | archivos enteros `test_module_01b.py`, `test_chat51_outro_no_fatal.py` (scripts manuales) y `test_m01b_retry.py` (5 tests); `test_module_f5_narrative` (3), `test_module_f5_prod::test_retoque_solo_rehace_los_caps_pedidos`, `test_module_f5b::test_narrador_declara_ids_y_corrige_mayusculas`, `test_module_f5c` (2 de «mejor de 3»), `test_module_f5d::test_prompt_trae_las_reglas_nuevas`, `test_chat33_pausas_conjy` (3), `test_module_01b_pauses` (3: las 3 fallas previas conocidas de la suite amplia) |
| `script_engine/m01b_guionista.py`: `write`, `build_prompt`, `beats_section`, `extra_material`, `_item_line`, `SYSTEM`, `SCHEMA`, `PROMPT_VERSION`, `BEST_OF`, `EXTRA_PER_CAP`, `PARA_WORDS` | `test_module_f6c::test_write_best_of_2_reintenta_con_las_duras` |
| `script_engine/m01c_editor.py`: `edit`, `_cap_hard`, `PROMPT_VERSION` | `test_module_f6c::test_editor_guardia_y_rechazo_por_validadores` |
| `script_engine/m01d_particion.py`: `regenerate_cap` (ya sin llamador; usaba `m01c_editor.edit`) | — |

**Lo que quedó por otro llamador vivo:** `m01a_skeleton` (`STEPS_DIR`, `CHAPTER_SCHEMA`, `DEFAULT_INTENT_BY_CAP`, `SCREEN_*`, `canonize_figures`, `assign_screen_ids`, `finalize_pool_plan` → escaleta, partición, papel, columna, ficha, tts_tags); `m01b_narrator` (`_validate_narration`, `NarrationValidationError`, `_len_range` y sus constantes → `m01b_guionista.review`, `m01d_particion.len_range`); `m01b_guionista` (`review`, `normalize`, `caps_text`, `sentences`, `wc`, … → `guion_v4`, `m01c_editor`, `m01d_particion`); `m01c_editor` (`SYSTEM`, `SCHEMA`, `build_prompt`, `lexical_guard`, `GUARD_ALL`, `narration_tts` → `guion_v4.editor_pass` con `--editor`, `m01d_particion`); `m05_narrative.judge_narration` (→ `run_guion_v4`); el flag `--modelo` (elige el modelo del guion v4, la única cadena) y los demás flags de la cadena única. Ningún módulo entero quedó sin llamador.

**Ajustados** (usaban la cadena vieja de paso): `test_module_f11b::test_fase1_5_pasa_el_modelo`, `test_module_f27::test_fase1_5_editor_solo_con_la_bandera` (sin `v3`/`guion`, pool con `_research_v3`); `test_module_f26c::test_temas_un_proceso_por_tema` (`--v3` → `--columna`); `test_module_f39_fase1` (6, sin `v3=True, guion="v4"`); `test_module_f5c::test_prompt_prioridad_y_relleno_nuevo`, `test_module_f5d::test_largo_minimo_mas_15_para_pro`, `test_module_f6c::test_prompt_y_particion` (quedan sobre lo vivo). **Nuevo** `test_module_f41_cadena.py` (20): sin pool v3 = PARADA sin gastar desde 5 pasos y por CLI exit 2; topic con pool v3 y sin `guion_version` corre la cadena nueva hasta la PARADA del papel; desde m01b va al guion v4; `--v3`/`--guion` fuera de `--help` y rechazados; la cadena vieja no existe; `research_topics` guarda `long`/`short`, `investigar_semilla` `long`; sin tipo no se inventa; el título de la ficha sale de `archived`.

**Arreglo extra de A (declarado):** `fase1_5._titulo_de_semilla` buscaba el título de la ficha solo en `seeds_archive.json → seeds`; un topic que sale de `research_topics` (el camino del form) no guarda `seed_title` y su semilla queda en `→ archived`. Ahora busca en los dos; sin eso, un tema nuevo desde el form pararía en la ficha con «sin seed_title». Tiene test.

**A.3 — `grep` 0 en código de producción:**
```
$ grep -rnE -e "is_v3_topic|is_v4_guion|--v3|--guion" --include=*.py --include=*.html --include=*.sh --include=*.ps1 . | grep -v "^./lab/\|^./_\|^./test_\|^./diag_\|^./data/"
(exit 1; líneas: 0)
```
(Fuera de producción: `test_module_f41_cadena.py`, que afirma que no existen; un comentario de `test_module_f26c.py`; docs e handoffs viejos; docstrings de 3 scripts de lab de F10.)

**A.3 — Qué haría hoy `fase1_5 --topic <id> --batch`** (solo lectura, `lab/hyperframes/f41/a/tabla_topics.py`):
| topic | video_type | pool v3 | qué haría | notas |
|---|---|---|---|---|
| ba6c3cac-a091… (Orleans, publicado) | long | no | PARADA antes de gastar: sin evidence_pool v3 | sin papel · tiene `data/scripts/…json` |
| eca6d3e2-fc1d… | long | no | PARADA antes de gastar: sin evidence_pool v3 | tiene script |
| 92146ab7-6c85… | long | no | PARADA antes de gastar: sin evidence_pool v3 | tiene script |
| ba6c3cac-f5v2 | long | no | PARADA antes de gastar: el pool no es del research v3 | tiene script |
| ba6c3cac-f7r3 | long | sí | cadena única desde m01a: ficha v2 existente (f15-1, no se paga) → escaleta, guion v4, partición, papel (se pagan) → PARADA del papel | sin papel |
| f8s1-ycua-bolanos | None | sí | igual (ficha f15-1) | sin papel |
| f18-kyshtym-mayak | None | sí | igual (ficha f23-1) | sin papel |
| f8s3-vajont | None | sí | igual (ficha f23-1; el `guion_version` 4 ya no cambia nada) | papel sin aprobar · tiene script |
| f39-kyshtym | None | sí | igual (ficha f23-1) | **papel APROBADO**: correr `fase1_5 --topic … --batch` a mano lo rehace y lo paga; el retomar de B no lo hace (va a la voz con `--from normalizer_gate`) |

Resultados de A: `test_module_f41_cadena.py` 20/20; los 37 archivos que tocan `fase1_5`/`topic_researcher`/`fase1` + editados 378 verdes; los 28 que importan los módulos tocados 277 verdes; rápida 58. CC repitió antes del commit (`f41_cadena + f39_fase1 + run_pipeline + rápida`): 147 passed.

## B — El orquestador y el form (`0354cbc`, subagente B) + B2 RAM (`8a0ed90`, CC)
**Secuencia nueva** (`run_pipeline.sequence`): arranca en `etapa_de(tid)`, corre la etapa, vuelve a mirar el disco; si la etapa no avanzó, frena con exit 1 (nunca corre dos veces lo mismo). Exit 0 = cadena completa o parada normal en una compuerta; 1 = falla o artefacto faltante.

| etapa | qué corre | cómo la detecta `etapa_de` (solo lectura) |
|---|---|---|
| `guion` | `fase1_5 --topic X --batch` | no hay `_steps/<id>/01e_pantalla.md` ni nada de después |
| `papel` | `papel_gate` | hay papel y `fase1_5.estado_papel` da False (también si cambió después de aprobado) |
| `voz` | `fase1_5 --topic X --from normalizer_gate --batch` | papel aprobado y falta `data/scripts/<id>.json` |
| `assets` | `fase2a --topic X` | falta `output/<id>/assets/assets_manifest.json` |
| `fondos` | `visor_gate` (solo con el form, sin cambio) y después `fase2b X` sin gfx | falta `output/<id>/<id>_final.mp4` y a algún cap le falta su visual base en `_fase2b_work/` (espejo de `fase2b._visual_base_existente`) |
| `guion_pantalla` | `fase2b X --plan-only` | falta `output/<id>/GUION_PANTALLA.json` |
| `aprobar_guion` | `guion_gate` | `aprobacion.estado(output/<id>)` da False (también si los planes cambiaron) |
| `render` | medida de RAM (B2) y `fase2b X --reuse-visuals --keep-segments --gfx --gfx-sparse` | falta `output/<id>/<id>_final_gfx.mp4` o es más viejo que `GUION_PANTALLA.json` |
| `packaging` | `fase3 X`; con `--batch`, solo el comando | falta `packaged` en topics_db |
| `listo` | nada | — |
| `cadena_vieja` | nada (exit 1) | sin papel pero con script, manifest, `_final*.mp4` o `video_generated`: protege lo ya pagado de los topics viejos |

**Compuertas (B.2, B.5):** sin `QA_FORM` paran siempre (exit 0) e imprimen leer / aprobar / `retomar: python run_pipeline.py --topic X` (el guion de pantalla suma `editar: … --plan-edit ARCHIVO.json`). Con el form emiten el marcador con el `.md` entero en `body` y esperan `input()`: **solo «A» aprueba**; cualquier otra respuesta o stdin cerrado es P. A en el papel → `--aprobar-papel "Omar <hoy>"` y sigue a la voz; A en el guion → `--aprobar-guion "Omar <hoy>"`, render y fase3 (en batch, el comando). La fecha sale de `datetime.date.today()`. **Nunca se aprueban solas.**

**B.7 + B2 (RAM):** el orquestador no cierra ningún programa (un test verifica que no haya `taskkill`, `kill(`, `terminate(` ni `psutil` en el código). B paró la medida de RAM porque el 14 no estaba en la tabla del handoff; CC la cableó después con origen en **DECISIONES 2026-10-27 00:30** (`RAM_MIN_GB = 14.0`): antes del render completo mide la RAM física libre (`GlobalMemoryStatusEx`, solo lectura); < 14 GB → PARADA con el comando de retomar, sin correr el render y sin cerrar nada; sin medida → avisa y sigue. Hoy la máquina tiene 13,3 GB libres: un render desde el form pararía ahí.

**Server y form:** `_FORM_PHASES` = RESEARCH, GUION, PAPEL, VOZ, ASSETS, FONDOS, PANTALLA, RENDER, PACKAGING; rutas GET `/form_topics` y POST `/form_resume?topic=<id>` (400 si no está en topics_db, 409 si ya hay una corrida); `/form?topic=<id>` abre retomando ese topic; `papel_gate` y `guion_gate` muestran el documento entero en un `<pre>` con scroll. El JS pasa `node --check`.

**Lo borrado en B:** el mensaje «m06 quedó en [R]/[E]» y su `--from m06`; `VIDEO_DONE_STATUS` y `_video_status` (el video se decide por artefactos en disco); el `_phase_header` anidado (pasó a nivel de módulo); la elección de `--batch` según el modo (`fase1_5` va siempre con `--batch`, la interfaz fija).

**Tests de B:** `test_run_pipeline.py` reescrito al estilo pytest: los 7 viejos **devolvían un bool en vez de `assert` y pasaban siempre**; ahora prueban la secuencia nueva (`test_order_and_tid`, `test_stop_on_nonzero`, `test_stop_missing_script`, `test_assisted_calls_fase3`, `test_batch_skips_fase3`, `test_research_runs_fase1_then_sequences`, `test_research_fase1_fails_no_sequence`). Nuevos para B.1–B.6: compuerta del papel (terminal, A, P, nunca sola ×4, PARADA de fase1_5), fondos y `--plan-only`, visor antes de fondos, compuerta del guion (A, A batch, P, terminal), render que falla avisa RAM y no cierra nada, `etapa_de` por etapa (×10), papel o planes cambiados vuelven a la compuerta, fondos por visuales base, render más viejo que el guion, cadena vieja (×4 + status), cadena vieja y listo no corren nada, `etapa_de` de solo lectura, retomar nunca re-corre una etapa hecha (×9), etapa que no avanza para, sin mensaje m06, headers → fases del form, `/form_resume` con `Popen` stub, `/form_topics`; y de B2: render con poca RAM para antes, sin medida sigue y avisa, la medida real da un número o None. `test_run_pipeline.py` 63 passed; con los del form (`test_module_f40_subs`, `test_module_qa_form_cost`, `test_qa_studio`) 90 passed.

**B.8 — Tabla `etapa_de`** (`lab/hyperframes/f41/b/tabla_etapas.py`, solo lectura):
| topic | status | etapa_de | qué correría `run_pipeline --topic X` |
|---|---|---|---|
| ba6c3cac-a091… (Orleans) | video_generated | cadena_vieja | nada (tiene script, manifest, `_final` y `_final_gfx`) |
| eca6d3e2-fc1d… | video_generated | cadena_vieja | nada |
| 92146ab7-6c85… | video_generated | cadena_vieja | nada |
| ba6c3cac-f5v2 | video_generated | cadena_vieja | nada |
| ba6c3cac-f7r3 | video_generated | cadena_vieja | nada (por el status; su video está bajo el id f5v2) |
| f8s1-ycua-bolanos | researched | guion | `fase1_5 --topic X --batch` |
| f18-kyshtym-mayak | researched | guion | `fase1_5 --topic X --batch` |
| f8s3-vajont | video_generated | papel | compuerta del papel (si se aprobara, saltaría a `guion_pantalla`: tiene los 7 visuales base; no re-paga nada) |
| f39-kyshtym | researched | voz | `fase1_5 --topic X --from normalizer_gate --batch` (papel aprobado por Omar, md5 7db98e46…; falta `data/scripts/f39-kyshtym.json`) |

**B.8 — Recorridos en seco del form** (`lab/hyperframes/f41/b/recorrido_form.py`, `run_pipeline.main()` en proceso con stubs, salida como la lee `qa_studio_server._form_reader`; detalle en `lab/hyperframes/f41/b/B8_SALIDA.md`, regenerado con el stub de RAM):
| recorrido | fases y marcadores en orden | final |
|---|---|---|
| 1 · `--research --video-type long --batch`, respuestas A / C / A | RESEARCH (fase1 stub) → GUION `fase1_5 --batch` → PAPEL **papel_gate** [A, P] → A: `--aprobar-papel "Omar <hoy>"` → VOZ `--from normalizer_gate --batch` → ASSETS fase2a → FONDOS **visor_gate** [C] → C: `fase2b X` → PANTALLA `--plan-only` → **guion_gate** [A, P] → A: `--aprobar-guion "Omar <hoy>"` → RENDER `--reuse-visuals --keep-segments --gfx --gfx-sparse` | «Cadena completa» + «LISTO PARA PACKAGING → python fase3.py …»; exit 0 |
| 2a · research con **P** en el papel | RESEARCH → GUION → **papel_gate** → P | frena en PAPEL con leer / aprobar / retomar; exit 0; `etapa_de` = papel |
| 2b · «Retomar» (`--topic … --batch`), A / C / A | arranca directo en PAPEL (no re-corre GUION) y sigue como el 1 | «Cadena completa»; exit 0; `etapa_de` = packaging; ninguna fase corrió dos veces |

## Validación (en serie, al final; US$ 0)
| verificación | resultado |
|---|---|
| tests nuevos B.1–B.6 + B2 (`test_run_pipeline.py`, stubs) | 63 passed |
| candado ch02 de Orleans **con** subtítulos (`lab/hyperframes/f41/verificar.sh final`) | `f792f3d483a1fa42daed5f7f0e054f46` ✓ |
| candado ch02 de Orleans **sin** subtítulos (`--only-cap ch02 --reuse-visuals --sw-encode --no-subs`) | `98386f8608e86f8099bbfb2d61cf2950` ✓ |
| suite rápida (`f25c f24 f21`) | 58 passed |
| suite amplia (`-n auto`) | **936 passed, 2 failed** = las 2 previas de `m03_merge_timing` |

- **Las 5 fallas previas pasaron a 2:** las 3 de `test_module_01b_pauses.py` (`test_tone_blocks_tienen_pausas`, `test_hook_abre_con_pausa`, `test_prose_rules_regla_pausas`) probaban el narrador viejo y A las borró por nombre con la cadena vieja.
- **La primera corrida de la amplia dio «no tests ran»:** el patrón `test_module_01a*.py` del `verificar.sh` ya no tiene archivos (A borró `test_module_01a.py` y `test_module_01a_evidence.py`) y pytest abortaba todo. En `lab/hyperframes/f41/verificar.sh` se agregó `shopt -s nullglob` (un patrón vacío deja de contar) y se volvió a correr. Logs en `lab/hyperframes/f41/final/`.
- Los md5 de ch02 los pisan las corridas del candado en `output/ba6c3cac-…/_fase2b_work/`, como siempre. Nada más se corrió de `fase2b`, y nunca `fase1_5` ni `fase2a`.

## US$
0,00 (ninguna llamada a modelos; tope `lab/TOPE_TANDA.json` = 0,00).

## Frenos
- No se corrió `fase1_5`, `fase2a` ni `fase2b` reales (solo el candado de Orleans sin gfx, que no llama a nada), no se llamó a ninguna API, no se aprobó papel ni guion de ningún topic, no se tocó `main`.
- No se cerró ni se lanzó ningún programa de Omar (los dos briefs lo decían; ningún subagente cerró nada).
- Ningún número nuevo: el único número de código nuevo, `RAM_MIN_GB = 14.0`, tiene origen en DECISIONES 2026-10-27 00:30.
- Ningún `cat` suelto antes de un heredoc.
- Nada escrito en `data/` ni en `output/` salvo el candado (y un `logs/pipeline_*.log` vacío que deja importar `fase1_5`).

## Commits (rama `f11-guion-v4`, base `5c6d9cb`, todos por rutas explícitas)
| commit | parte |
|---|---|
| `72d9eb2` | DECISIONES.md (`f2bbbdfe…`, línea 20:59) + handoff (`bd6361b3…`) |
| `0354cbc` | B: orquestador, form, retomar, tests |
| `fc59a76` | A: una sola cadena, video_type, tests, mapa |
| `8a0ed90` | B2: RAM antes del render completo (DECISIONES 00:30) + recorrido de B8 regenerado |
| (último) | reporte, ESTADO, `verificar.sh` de F41, logs del candado |

## Lo que queda abierto (entero)
**De A:**
- a1. **Correr a mano `fase1_5 --topic X --batch` siempre empieza en m01a** y rehace y paga escaleta, guion v4 y papel, aunque ya haya papel (y el papel nuevo queda sin aprobar). El retomar de B no lo hace (`etapa_de` va a la compuerta o a la voz), pero un `fase1_5 --topic f39-kyshtym --batch` tipeado en terminal sí re-pagaría el papel aprobado de Kyshtym. Lo seguro es `run_pipeline --topic X` o `fase1_5 --topic X --from normalizer_gate --batch`.
- a2. La PARADA de un topic sin pool v3 sale con exit 2; su `parada` es el paso desde el que arrancó (p. ej. `m01a`), no `"papel"`. La interfaz y sus códigos de salida no cambiaron.
- a3. **Lab roto a sabiendas:** los scripts de lab que importaban lo borrado ya no corren (`lab/hyperframes/f5/correr_f5_orleans.py`, los de f6, f7, f10, f11 y f13–f26 con `mg.write`/`mc.edit`, `_lab_chat66b_m01a_schema.py`, `_lab_chat66b_m01b_schema.py`, `lab/_gpt_probe_analista/*`). Son evidencia histórica, no producción.
- a4. Muertos de antes de F41 y fuera de la cadena, sin tocar: `m01a_escaleta.to_markdown` y los `PROMPT_VERSION_*`/`SYSTEM_V2_*` viejos (los fijan tests de literalidad), `m01d_particion.cut_phrases`, `guion_v3_reglas.DATE_MAX_PER_CAP`, `m01b_guionista.INSTITUTION`, `m01e_pantalla.ESTILOS`/`TIPOS_DESCARTE`, `m05_narrative._REPEAT_TIPOS`, `topic_researcher.research_testimonios`/`_build_testimonios_prompt`/`TESTIMONIOS_ANGLE`.
- a5. El arreglo de `_titulo_de_semilla` (busca también en `archived`) va más allá de la letra de A.2; sin él, el form no llega a la ficha en un tema nuevo. Se dejó; se revierte si Omar no lo quiere.
- a6. `video_type` de topics viejos: no se migró `data/` (Ycuá, los dos Kyshtym y Vajont siguen en `None`). El menú de `fase1_5` (sin `--topic`) solo lista topics `validated`; los de `--semilla` quedan `researched`, como antes.
- a7. Importar `fase1_5` (p. ej. `tabla_topics.py`) deja un `logs/pipeline_<fecha>.log`.
- a8. `run_guion_v4` y `_topic_v3` conservan esos nombres (tests y lab los usan); ya no fuerzan `guion_version`.
- a9. Las menciones a `--v3 --guion v4` en `DECISIONES.md`, `ESTADO_SESION.md` y handoffs viejos quedan como historia.
- a10. `escaleta_notas` (lo carga `fase1_5._topic_v3`) y `pool["digest"]` siguen sin lector desde F39 (f5 de F39); no se tocaron.

**De B:**
- b1. ~~RAM antes del render~~ → cableado en B2 con DECISIONES 00:30 (14 GB). Con la RAM de hoy (13,3 GB libres) un render desde el form pararía antes de correr y pediría liberar RAM.
- b2. `fase1_5` va siempre con `--batch` desde el orquestador: las compuertas intermedias en terminal (normalizer, music) ya no preguntan.
- b3. **Papel aprobado después de que ya existe el script:** si el papel se aprueba (o se re-aprueba tras cambiar) y `data/scripts/<id>.json` ya existe, `etapa_de` saltea la voz aunque el papel sea más nuevo que el script. Le pasaría a Vajont si se aprueba su papel. No se comparan mtimes papel↔script porque no hay regla para eso.
- b4. Retomar `f8s1-ycua-bolanos` o `f18-kyshtym-mayak` corre la cadena nueva desde m01a (paga escaleta, guion y papel). Lo decide quien lo lance.
- b5. El form auto-lanza un research al abrirse; para retomar sin pasar por eso: `/form?topic=<id>` o «Retomar» sin una corrida viva (con una corrida en curso, `/form_resume` devuelve 409; no se mata nada).
- b6. El marcador lleva el documento entero en `body` y `/form_state` lo reenvía en cada poll de 1 s mientras la compuerta está abierta; no se midió con un papel real (decenas de KB).
- b7. **La UI del form no se probó en un navegador** (no se lanzó qa_studio, por la regla): solo `node --check` del JS y los tests del server con stub.
- b8. La etiqueta `\bm06\b` → «Classifying issues…» de `activityLabel` en `qa_form.html` sigue; si m06 ya no imprime nada es código muerto.
- b9. Los topics viejos (Orleans y otros 4) quedan en `cadena_vieja`: el orquestador no los retoma. Orleans sigue publicable con lo que tiene en disco.

**Lo de la lista de 18:30 que el handoff deja fuera:** o14 (`video_type` por cap → short), foto madre fuera de `cost_tracker`, costo de Claude que el form no muestra (solo Gemini), iniciales en el normalizer y el cortador, el cortador parte las citas.

## Procesos (paso 12 de `/tanda`)
Subagentes A, B y el revisor: terminados, ninguno vivo. Shells en segundo plano: el candado y la suite amplia (terminados). No se lanzó qa_studio y no se cerró ningún programa de Omar.

## Veredicto del revisor (`revisor-handoff`, íntegro)
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Handoff entero, md5 bd6361b3… | OK | md5sum coincide. |
| 2 | Línea 2026-10-27 20:59 en DECISIONES | OK | DECISIONES.md:125; diff 72d9eb2~1..HEAD = +1 línea. |
| 3 | Cadena vieja borrada, no apagada | OK | generate_skeleton / generate_narration solo en docstrings y en el test que prueba su ausencia (test_module_f41_cadena.py:137,155). Sin ramas comentadas ni flags muertos. m01d_particion.regenerate_cap_v3 es otra función, viva. |
| 4 | grep 0 de is_v3_topic\|is_v4_guion\|--v3\|--guion\|run_guion_v3 en producción | OK | Mi grep sobre .py/.html/.sh (excluyendo lab, _*, test_*, diag*) = 0. |
| 5 | Lo que quedó tiene llamador vivo | OK | finalize_pool_plan lo importa m01a_escaleta.py:58; lexical_guard lo usa guion_v4.py:1024,1115; el resto en A1_lista_previa.md §2. |
| 6 | Interfaz fija intacta | OK | fase1_5.py conserva --topic, --from, --batch, --semilla, --aprobar-papel; estado_papel en fase1_5.py:298; run_pipeline llama fase1_5 --topic X --batch. |
| 7 | B.1–B.7 contra la letra | OK | test_run_pipeline.py + test_module_f41_cadena.py: 81 passed (corrido por mí). recorrido_form.py con stubs: orden aprobar-papel, voz, assets, fondos, plan-only, aprobar-guion, render; "¿Se corrió dos veces alguna fase? False". Sin QA_FORM las compuertas paran (run_pipeline.py:336,411). Existen test_retomar_nunca_recorre_una_etapa_hecha y test_sin_mensaje_m06. Los diffs de run_pipeline y qa_studio_server no agregan taskkill/kill/terminate/Firefox. |
| 8 | RAM_MIN_GB con origen y permitido | OK | run_pipeline.py:247 = 14.0, origen DECISIONES.md:22 (00:30, "< 14 GB, umbral de F2"). El handoff B.7 pide medir y avisar sin cerrar nada; la función solo mide y para. |
| 9 | Tests borrados listados por nombre | OK | F41_REPORT.md:63-69 y A1_lista_previa.md §1; el diff confirma los 3 de 01b_pauses y los archivos enteros. |
| 10 | Suite amplia 5 → 2 fallas previas | OK | final/suite_amplia.log: 2 failed, 936 passed; las 2 son test_module_m03_merge_timing (previas). Las 3 que desaparecen son las de 01b_pauses, borradas con el narrador viejo. |
| 11 | shopt -s nullglob legítimo | OK | verificar.sh:4; el patrón test_module_01a*.py ya no tiene archivos; no debilita ningún test. |
| 12 | Candado ch02 | OK | final/onlycap_ch02_nogfx.log:39 = f792f3d4…; final/onlycap_ch02_nosubs.log:39 = 98386f86… (leído del log, no corrido por mí). |
| 13 | Suite rápida | OK | final/suite_rapida.log: 58 passed. |
| 14 | Arreglo extra _titulo_de_semilla | OK con observación | fase1_5.py:249; topic_researcher guarda video_type. Declarado en el reporte (a5), con test; excede la letra de A.2. |
| 15 | US$ 0 / tope | OK | TOPE_TANDA.json = {"usd": 0.00, ...}. No puedo verificar que no hubo llamadas a APIs, solo que no hay logs de gasto. |
| 16 | Reporte con tablas y abierto entero | OK | F41_REPORT.md existe, con "Lo borrado" y "Lo que queda abierto (entero)" (a3, a5…). Falta este veredicto, que se pega ahora. |
| 17 | Commits por parte, ESTADO, push | NO VERIFICABLE | lab/ESTADO_SESION.md figura modificado sin commitear; no vi el commit final ni el push. |

Fuera de alcance: ninguno atribuible a F41. diag_234_cap4.py y lab/hyperframes/f28/a/f28a.log ya estaban sucios al empezar y no están en los commits F41. TOPE_TANDA.json y ESTADO_SESION.md son del flujo de la tanda.

Riesgos que el contrato no cubre:
- Lab roto a sabiendas (a3): decenas de scripts de lab/ y _lab_* importan símbolos borrados.
- No corrí el candado de ch02 ni la suite amplia: solo leí los logs de final/. El e2e real desde el form (tema nuevo de 0) tampoco está probado, solo con stubs.
- Con la RAM de hoy (13,3 GB, bajo el umbral de 14) el primer render completo desde el form se va a parar; Omar debe saberlo antes de lanzar.

### Adenda de CC (después del veredicto; el texto de arriba queda tal cual)
- Fila 17: este veredicto quedó pegado acá; el reporte, `lab/ESTADO_SESION.md` (cabecera, «Para Omar (F41)», bloque F41 y candados vigentes), `lab/hyperframes/f41/verificar.sh`, los logs de `final/` y `lab/TOPE_TANDA.json` entran en el commit final, y después va el push a `origin/f11-guion-v4`.
- Fila 14: el arreglo de `_titulo_de_semilla` queda como abierto a5 (se revierte si Omar no lo quiere).
- Riesgo de la RAM: está en el «Para Omar» de ESTADO y en b1 del abierto.
