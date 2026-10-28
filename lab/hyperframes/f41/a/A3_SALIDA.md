# F41 A.3 — Salida en texto de la Parte A (una sola cadena)

Tope US$ 0,00: no se corrió `fase1_5`/`fase2a`/`fase2b` reales ni ninguna API; no se aprobó papel ni guion; nada
escrito en `data/` (la tabla de topics es de solo lectura). Lista previa: `lab/hyperframes/f41/a/A1_lista_previa.md`.

## 1. Lo borrado (llamadores en producción = 0)

| archivo:función / símbolo | llamadores en producción | tests borrados (por nombre) |
|---|---|---|
| fase1_5.py:is_v3_topic | 0 (era `process_topic`) | test_module_f10::test_cuando_corre_v3; test_module_f11::test_v3_sigue_por_su_camino_y_v4_por_el_suyo |
| fase1_5.py:is_v4_guion | 0 | (el mismo de f11) |
| fase1_5.py:run_guion_v3 | 0 | test_module_f11::test_v3_byte_identico (+ helpers `_fake_pro`, `_run_v3`, `V3_GOLDEN`, `V3_GOLDEN_F22`, `V3_GOLDEN_F21`, `BANDAS_F23`); test_module_f22::test_dorado_v3_solo_cambian_los_mensajes_de_f22; test_module_f23::test_dorado_v3_solo_cambian_las_bandas |
| fase1_5.py: flags `--v3`, `--guion`; parámetros `v3`, `guion` de `process_topic`; ramas m01a vieja (`generate_skeleton`), m01b vieja (`generate_narration`) y m01b v3; imports de `generate_skeleton`/`generate_narration`; `topic["guion_version"] = 3/4` | 0 | test_module_f10::test_sin_flag_corre_el_camino_viejo |
| script_engine/m01a_escaleta.py:is_v3 (y el `import os` que solo usaba él) | 0 (ya antes) | test_module_f6b::test_flag_v3_y_camino_v2 |
| script_engine/m01a_skeleton.py: generate_skeleton, frozen_skeleton, SkeletonValidationError, _build_prompt, _call_with_validation_retry, _enforce_structure, _fact_ids, _format_facts, _min_new, _persist, _pool_prompt_section, _skeleton_schema, _validate_distribution_plan, _validate_evidence_plan, _validate_skeleton, DEVELOPMENT_CAPS, EVIDENCE_KINDS, MAX_BRIDGE_EVIDENCE, MAX_BULLETS_PER_CHAPTER, MIN_BULLETS_PER_CHAPTER, MAX_RETRY_ATTEMPTS, MIN_NEW_EVIDENCE, VALID_NARRATIVE_INTENTS (+ imports `json`, `call_flash_json`) | 0 | archivo entero **test_module_01a.py** (script manual `main`, sin tests pytest); archivo entero **test_module_01a_evidence.py**: ::test_plan_valido_y_cliffhangers, ::test_reparaciones_deterministas, ::test_errores_que_no_se_reparan, ::test_prompt_y_schema_con_y_sin_pool, ::test_generate_skeleton_con_pool; test_module_f5c::test_skeleton_congelado_traduce_ids_y_saca_lo_que_no_esta |
| script_engine/m01b_narrator.py: generate_narration, regenerate_caps (ya sin llamador antes), _call_with_length_retry, _best_of_n, _call_narrator, _base_direction, _trim_to_sentence_boundary, _prompt_hook, _prompt_development, _prompt_outro, _prompt_humanizer, _evidence_block, _format_facts, _format_previous_narrations, _format_skeleton, _format_topic_block, _tone_block, _prose_rules, _narration_schema, _humanizer_schema, _validate_humanizer, _persist, F5_RULES, PROSE_RULES, PROSE_RULE_6_POOL, TONE_INSTRUCTIONS_BY_INTENT, HUMANIZER_COUNT, HUMANIZER_MAX_CHARS, OUTRO_RETRY_MARGIN, POOL_NARRATOR, POOL_BEST_OF, POOL_MIN_LEN_FACTOR, STEPS_DIR, _SENT_SPLIT (+ imports `json`, `Path`, `DATA_DIR`, `call_flash_json`, `call_pro_json`, `evidence`) | 0 | archivo entero **test_module_01b.py** (script manual); archivo entero **test_chat51_outro_no_fatal.py** (script manual `run`); archivo entero **test_m01b_retry.py**: ::test_retry_phrase_connector, ::test_retry_phrase_open_and_close, ::test_phrase_exhausted_raises, ::test_length_retry_regression, ::test_outro_salvage_intact; test_module_f5_narrative::test_prompt_narrador_con_y_sin_pool, ::test_retry_por_pool_y_aceptacion_con_violaciones, ::test_ultimo_intento_largo_acepta_el_anterior; test_module_f5_prod::test_retoque_solo_rehace_los_caps_pedidos; test_module_f5b::test_narrador_declara_ids_y_corrige_mayusculas; test_module_f5c::test_mejor_de_3_se_queda_con_el_mejor_no_con_el_ultimo, ::test_mejor_de_3_no_toma_el_ultimo_si_es_peor; test_module_f5d::test_prompt_trae_las_reglas_nuevas; test_chat33_pausas_conjy::test_tone_instructions_sin_pausas, ::test_tone_instructions_conservan_tono, ::test_prose_rules_sin_regla_pausas; test_module_01b_pauses::test_tone_blocks_tienen_pausas, ::test_hook_abre_con_pausa, ::test_prose_rules_regla_pausas |
| script_engine/m01b_guionista.py: write, build_prompt, beats_section, extra_material, _item_line, SYSTEM, SCHEMA, PROMPT_VERSION, BEST_OF, EXTRA_PER_CAP, PARA_WORDS (+ `Callable`) | 0 | test_module_f6c::test_write_best_of_2_reintenta_con_las_duras |
| script_engine/m01c_editor.py: edit, _cap_hard, PROMPT_VERSION (+ `Callable`) | 0 | test_module_f6c::test_editor_guardia_y_rechazo_por_validadores |
| script_engine/m01d_particion.py: regenerate_cap (ya sin llamador antes; usaba `m01c_editor.edit`) | 0 | — |

Docstrings al día: `fase1_5` (cabecera, uso, `process_topic`, `run_one_topic_from_menu`, ayuda de `--modelo`/`--editor`),
`m01a_skeleton`, `m01b_narrator`, `m01b_guionista`, `m01c_editor`, `m01a_escaleta`, `m01e_pantalla` (`run_guion_v3/v4` →
`run_guion_v4`).

## 2. Lo que quedó por otro llamador

| archivo:símbolo | quién lo usa |
|---|---|
| módulo m01a_skeleton: STEPS_DIR, CHAPTER_SCHEMA, DEFAULT_INTENT_BY_CAP, SCREEN_PER_CAP, SCREEN_MUST, canonize_figures, assign_screen_ids, finalize_pool_plan | m01a_escaleta, m01d_particion, m01e_pantalla, m01a_columna, researcher_steps/ficha_caso, tts_tags |
| módulo m01b_narrator: _validate_narration, NarrationValidationError, _len_range, LEN_*, FORBIDDEN_OPENINGS/CLOSINGS, GENERIC_CONNECTORS, HOOK_FIRST_SENTENCE_MAX_WORDS, _first_sentence, _word_count, _contains_any | m01b_guionista.review, m01d_particion.len_range |
| módulo m01b_guionista: review, normalize, caps_text, sentences, wc, _surname, _verified_antagonist, institution_re, … | guion_v4, m01c_editor, m01d_particion |
| módulo m01c_editor: SYSTEM, SCHEMA, build_prompt, lexical_guard, GUARD_ALL, narration_tts | guion_v4.editor_pass (`--editor`, F27), m01d_particion |
| m05_narrative.judge_narration | fase1_5.run_guion_v4 |
| fase1_5: run_escaleta_v3, run_guion_v4, _topic_v3, cargar_perfil, run_pantalla, asegurar_ficha, papel, semilla, _load_skeleton, _load_narration, _build_audio_script | la cadena única y la reanudación `--from` |
| fase1_5 `--modelo` | **queda**: elige el modelo del guion v4, que es la única cadena (no servía solo a la vieja) |
| fase1_5 `--editor`, `--columna`, `--sin-columna`, `--modelo-escaleta`, `--temas`, `--only`, `--from`, `--semilla`, `--aprobar-papel`, `--batch`, `--no-gate`, `--no-music-gate`, `--csv` | la cadena única |

Ningún módulo entero quedó sin llamador. Ya muertos antes de F41 y fuera de la cadena (no se tocaron):
m01a_escaleta `to_markdown`, `PROMPT_VERSION_*`/`SYSTEM_V2_*` viejos; m01d_particion `cut_phrases`; guion_v3_reglas
`DATE_MAX_PER_CAP`; m01b_guionista `INSTITUTION`; m01e_pantalla `ESTILOS`, `TIPOS_DESCARTE`; m05_narrative
`_REPEAT_TIPOS`; topic_researcher `research_testimonios`, `_build_testimonios_prompt`, `TESTIMONIOS_ANGLE`.

## 3. `grep` 0 en código de producción

```
$ grep -rnE -e "is_v3_topic|is_v4_guion|--v3|--guion" --include=*.py --include=*.html --include=*.sh --include=*.ps1 . | grep -v "^./lab/\|^./_\|^./test_\|^./diag_\|^./data/"
(exit 1; líneas: 0)
```

Fuera de producción aparece en: `test_module_f41_cadena.py` (afirma que NO existen), un comentario de
`test_module_f26c.py` («F41: sin --v3»), docs (`DECISIONES.md`, `lab/ESTADO_SESION.md`, handoffs y reportes de
f10/f11/f11b/f11c/f14/f39/f41) y tres scripts de lab de F10 (`lab/hyperframes/f10/f10_ajuste_ycua.py`,
`f10_seco_orleans.py`, `f10_ycua_docs.py`, en docstrings).

## 4. Qué haría hoy `fase1_5 --topic <id> --batch` (solo lectura)

Script: `lab/hyperframes/f41/a/tabla_topics.py` (lee topics_db, `_steps/<id>/`, seeds_archive y `estado_papel`; la
compuerta del pool se evalúa en memoria con `pool_gate.evaluate`, sin escribir POOL_GATE.md).

| topic | video_type | guion_version | pool v3 | qué haría `fase1_5 --topic <id> --batch` | notas |
|---|---|---|---|---|---|
| ba6c3cac-a091-41c0-8dad-afd2f4364747 | long | None | no | PARADA antes de gastar: sin evidence_pool (falta `_research_v3`): la cadena no corre sin el pool del research v3 | papel hoy: no (no hay papel) · data/scripts/ba6c3cac-a091-41c0-8dad-afd2f4364747.json existe |
| eca6d3e2-fc1d-4341-82de-07c6d159e801 | long | None | no | PARADA antes de gastar: sin evidence_pool (falta `_research_v3`): la cadena no corre sin el pool del research v3 | papel hoy: no (no hay papel) · data/scripts/eca6d3e2-fc1d-4341-82de-07c6d159e801.json existe |
| 92146ab7-6c85-4bbc-b813-d7e31afc9876 | long | None | no | PARADA antes de gastar: sin evidence_pool (falta `_research_v3`): la cadena no corre sin el pool del research v3 | papel hoy: no (no hay papel) · data/scripts/92146ab7-6c85-4bbc-b813-d7e31afc9876.json existe |
| ba6c3cac-f5v2 | long | None | no | PARADA antes de gastar: el evidence_pool no es del research v3 (falta `_research_v3`): la cadena no corre sin el pool del research v3 | papel hoy: no (no hay papel) · data/scripts/ba6c3cac-f5v2.json existe |
| ba6c3cac-f7r3 | long | None | sí | cadena única desde m01a: compuerta verde → ficha v2 existente (f15-1, no se paga) → escaleta (se paga) → guion v4 → partición → papel (se paga) → PARADA del papel (el papel nuevo queda sin aprobar) | papel hoy: no (no hay papel) |
| f8s1-ycua-bolanos | None | None | sí | cadena única desde m01a: compuerta verde → ficha v2 existente (f15-1, no se paga) → escaleta (se paga) → guion v4 → partición → papel (se paga) → PARADA del papel (el papel nuevo queda sin aprobar) | papel hoy: no (no hay papel) |
| f18-kyshtym-mayak | None | None | sí | cadena única desde m01a: compuerta verde → ficha v2 existente (f23-1, no se paga) → escaleta (se paga) → guion v4 → partición → papel (se paga) → PARADA del papel (el papel nuevo queda sin aprobar) | papel hoy: no (no hay papel) |
| f8s3-vajont | None | 4 | sí | cadena única desde m01a: compuerta verde → ficha v2 existente (f23-1, no se paga) → escaleta (se paga) → guion v4 → partición → papel (se paga) → PARADA del papel (el papel nuevo queda sin aprobar) | papel hoy: no (el papel no está aprobado) · data/scripts/f8s3-vajont.json existe |
| f39-kyshtym | None | None | sí | cadena única desde m01a: compuerta verde → ficha v2 existente (f23-1, no se paga) → escaleta (se paga) → guion v4 → partición → papel (se paga) → PARADA del papel (el papel nuevo queda sin aprobar) | papel hoy: APROBADO (papel aprobado por Omar (2026-10-27), md5 7db98e46…) · OJO: desde m01a se rehace y se paga el papel aprobado; retomar sin pagar = `--from normalizer_gate --batch` |

(`guion_version` ya no lo lee nadie: el 4 de Vajont no cambia nada. Los `video_type` en None son de topics viejos: A.2
vale para lo que salga del research desde ahora; no se migró `data/`.)

## 5. Tests

Ajustados (usaban la cadena vieja de paso; prueban otra cosa): test_module_f11b::test_fase1_5_pasa_el_modelo y
test_module_f27::test_fase1_5_editor_solo_con_la_bandera (sin `v3=`/`guion=`, pool con `_research_v3`);
test_module_f26c::test_temas_un_proceso_por_tema (`--v3` → `--columna` como argumento que pasa de largo);
test_module_f39_fase1 (6: a3_de_la_semilla…, a1_compuerta_roja…, a1_ficha_v2_existente…, a4_aprobar_papel…,
a4_reanudar…, a4_papel_aprobado…: sin `v3=True, guion="v4"`); test_module_f5c::test_prompt_prioridad_y_relleno_nuevo
(quedan las aserciones de `m05_narrative.FORBIDDEN_FILLER`); test_module_f5d::test_largo_minimo_mas_15_para_pro (queda
`_len_range`); test_module_f6c::test_prompt_y_particion (quedan `normalize` y `caps_text`); imports de
test_module_01b_pauses, test_chat33_pausas_conjy, test_module_f5_narrative, test_module_f5_prod, test_module_f5b,
test_module_f5c, test_module_f6c y test_module_f11.

Nuevo: `test_module_f41_cadena.py` (20, sintéticos): sin pool v3 → PARADA sin gastar desde m01a/m01b/normalizer_gate/
audio/m03, sin pool y con pool no-v3 (10); por CLI sale con 2; pool v3 sin `guion_version` corre compuerta → ficha →
escaleta → guion v4 → PARADA del papel; desde m01b va al guion v4; `--v3`/`--guion` no están en `--help` y argparse
los rechaza; la cadena vieja no existe en fase1_5 ni en los módulos; research_topics guarda `long`/`short`;
investigar_semilla guarda `long`; `_enrich_with_seed_metadata` sin tipo no lo inventa; título de la ficha desde
`seeds_archive.json → archived`.

Resultados: test_module_f41_cadena.py 20/20 · los que tocan fase1_5/topic_researcher/fase1 + los editados (37
archivos, sin test_run_pipeline.py) 378 verdes, 0 rojos · suite rápida (f25c, f24, f21) 58/58 · además los que
importan los módulos tocados (m01*, guion_v4, m01e, tts_tags, ficha_caso, m05…: 28 archivos) 277 verdes, 0 rojos.
