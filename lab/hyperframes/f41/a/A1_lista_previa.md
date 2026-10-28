# F41 A.1 — Lista previa (antes de borrar nada)

Cómo se sacó: grafo de referencias por AST (calificado: dentro del módulo por nombre; desde otro archivo solo
`from M import X` o `alias.X` con `alias` = M), punto fijo «sin llamador en producción» después de quitar las semillas
de la cadena vieja. Producción = `.py` de la raíz (sin `test_*`, `_*`, `diag_*`) + `script_engine/` +
`researcher_steps/` + `tools/`. `lab/`, `_lab_*`, `_probe_*`, `diag_*` y los tests NO cuentan como llamadores vivos.
Lo que ya estaba sin llamador ANTES de F41 y no es de la cadena vieja **no se toca** (abajo, §4).

Semillas (la cadena vieja en `fase1_5`): `is_v3_topic`, `is_v4_guion`, `run_guion_v3`, la rama m01a vieja
(`generate_skeleton`), la rama m01b vieja (`generate_narration`), los flags `--v3` y `--guion` y los parámetros
`v3=`/`guion=` de `process_topic`. Más dos que ya estaban sin llamador y son la misma lógica de elegir/rehacer la
cadena vieja: `m01a_escaleta.is_v3` (el otro selector por `guion_version`/`GUION_V3`) y `m01b_narrator.regenerate_caps`
(el retoque del narrador v2), y `m01d_particion.regenerate_cap` (F10, «regenerate_caps v3» con el editor v3: sin
llamador desde F11 y su única dependencia, `m01c_editor.edit`, cae con el guionista v3).

## 1. Se borra (llamadores en producción = 0 después de quitar la cadena vieja)

| archivo:símbolo | llamadores en producción (hoy) | tests que lo usan | lab (no cuenta) |
|---|---|---|---|
| fase1_5.py:is_v3_topic | fase1_5.process_topic (rama vieja) | test_module_f10::test_cuando_corre_v3, test_module_f11::test_v3_sigue_por_su_camino_y_v4_por_el_suyo | — |
| fase1_5.py:is_v4_guion | fase1_5.process_topic | test_module_f11::test_v3_sigue_por_su_camino_y_v4_por_el_suyo | — |
| fase1_5.py:run_guion_v3 | fase1_5.process_topic | test_module_f11::test_v3_byte_identico (vía `_run_v3`), test_module_f22::test_dorado_v3_solo_cambian_los_mensajes_de_f22 y test_module_f23::test_dorado_v3_solo_cambian_las_bandas (vía `t11._run_v3`) | — |
| fase1_5.py: flags `--v3`, `--guion`; parámetros `v3`, `guion` de `process_topic`; imports `generate_skeleton`, `generate_narration`; las ramas m01a/m01b viejas y v3 | `main` → `process_topic` | test_module_f10::test_sin_flag_corre_el_camino_viejo; y de paso (se ajustan, §3): f11b, f26c, f27, f39_fase1 | lab f10 (docstrings) |
| fase1_5.py: `topic["guion_version"] = 3/4` en `_topic_v3`/`run_guion_v4` | nadie lo lee después de borrar `is_v3_topic`/`is_v4_guion`/`m01a_escaleta.is_v3` | — | — |
| script_engine/m01a_escaleta.py:is_v3 | 0 (ya antes de F41) | test_module_f6b::test_flag_v3_y_camino_v2 | — |
| script_engine/m01a_skeleton.py:generate_skeleton | fase1_5 (rama vieja) | test_module_01a.py (script manual, entero), test_module_01a_evidence::test_generate_skeleton_con_pool, test_module_f5c::test_skeleton_congelado_traduce_ids_y_saca_lo_que_no_esta | lab/hyperframes/f5/correr_f5_orleans.py |
| m01a_skeleton: frozen_skeleton, SkeletonValidationError, _build_prompt, _call_with_validation_retry, _enforce_structure, _fact_ids, _format_facts, _min_new, _persist, _pool_prompt_section, _skeleton_schema, _validate_distribution_plan, _validate_evidence_plan, _validate_skeleton | solo `generate_skeleton` (y entre ellos) | test_module_01a_evidence::test_plan_valido_y_cliffhangers, ::test_reparaciones_deterministas, ::test_errores_que_no_se_reparan, ::test_prompt_y_schema_con_y_sin_pool | _lab_chat66b_m01a_schema.py |
| m01a_skeleton: DEVELOPMENT_CAPS, EVIDENCE_KINDS, MAX_BRIDGE_EVIDENCE, MAX_BULLETS_PER_CHAPTER, MIN_BULLETS_PER_CHAPTER, MAX_RETRY_ATTEMPTS, MIN_NEW_EVIDENCE, VALID_NARRATIVE_INTENTS | solo las funciones de arriba | (test_generate_skeleton_con_pool) | _lab_chat66b_m01a_schema.py |
| script_engine/m01b_narrator.py:generate_narration | fase1_5 (rama vieja) | test_module_01b.py (script manual, entero) | lab f5 correr_f5_orleans |
| m01b_narrator:regenerate_caps | 0 (ya antes de F41) | test_module_f5_prod::test_retoque_solo_rehace_los_caps_pedidos | lab f5 correr_f5_orleans |
| m01b_narrator: _call_with_length_retry, _best_of_n, _call_narrator, _base_direction, _trim_to_sentence_boundary, _prompt_hook, _prompt_development, _prompt_outro, _prompt_humanizer, _evidence_block, _format_facts, _format_previous_narrations, _format_skeleton, _format_topic_block, _tone_block, _prose_rules, _narration_schema, _humanizer_schema, _validate_humanizer, _persist | solo `generate_narration`/`regenerate_caps` (y `m01b_guionista.build_prompt`, que también cae) | test_m01b_retry (los 5), test_chat51_outro_no_fatal.py (script manual, entero), test_module_f5_narrative::test_prompt_narrador_con_y_sin_pool, ::test_retry_por_pool_y_aceptacion_con_violaciones, ::test_ultimo_intento_largo_acepta_el_anterior, test_module_f5b::test_narrador_declara_ids_y_corrige_mayusculas, test_module_f5c::test_mejor_de_3_se_queda_con_el_mejor_no_con_el_ultimo, ::test_mejor_de_3_no_toma_el_ultimo_si_es_peor | _lab_chat66b_m01b_schema.py |
| m01b_narrator: F5_RULES, PROSE_RULES, PROSE_RULE_6_POOL, TONE_INSTRUCTIONS_BY_INTENT, HUMANIZER_COUNT, HUMANIZER_MAX_CHARS, OUTRO_RETRY_MARGIN, POOL_NARRATOR, POOL_BEST_OF, POOL_MIN_LEN_FACTOR, STEPS_DIR, _SENT_SPLIT | solo las funciones de arriba | test_chat33_pausas_conjy::test_tone_instructions_sin_pausas, ::test_tone_instructions_conservan_tono, ::test_prose_rules_sin_regla_pausas; test_module_01b_pauses::test_tone_blocks_tienen_pausas, ::test_hook_abre_con_pausa, ::test_prose_rules_regla_pausas; test_module_f5d::test_prompt_trae_las_reglas_nuevas; (de paso, se ajustan: f5c::test_prompt_prioridad_y_relleno_nuevo, f5d::test_largo_minimo_mas_15_para_pro) | _lab_chat66b_m01b_schema.py |
| script_engine/m01b_guionista.py:write | fase1_5.run_guion_v3 | test_module_f6c::test_write_best_of_2_reintenta_con_las_duras | lab f6, f7, f10, f11…f26 (corridas) |
| m01b_guionista: build_prompt, beats_section, extra_material, _item_line, SYSTEM, SCHEMA, PROMPT_VERSION, BEST_OF, EXTRA_PER_CAP, PARA_WORDS | solo `write` | test_module_f6c::test_prompt_y_particion | lab f11 convergencia, _gpt_probe_analista |
| script_engine/m01c_editor.py:edit, _cap_hard, PROMPT_VERSION | fase1_5.run_guion_v3; m01d_particion.regenerate_cap (sin llamador) | test_module_f6c::test_editor_guardia_y_rechazo_por_validadores | lab f6, f7, f10 |
| script_engine/m01d_particion.py:regenerate_cap | 0 (ya antes de F41) | — | — |

## 2. Queda (tiene otro llamador vivo)

| archivo:símbolo | quién lo usa |
|---|---|
| módulo `script_engine/m01a_skeleton` (queda: STEPS_DIR, CHAPTER_SCHEMA, DEFAULT_INTENT_BY_CAP, SCREEN_PER_CAP, SCREEN_MUST, canonize_figures, assign_screen_ids, finalize_pool_plan) | m01a_escaleta (CHAPTER_SCHEMA, DEFAULT_INTENT_BY_CAP, STEPS_DIR, finalize_pool_plan, SCREEN_PER_CAP), m01d_particion, m01e_pantalla, m01a_columna, researcher_steps/ficha_caso (STEPS_DIR), tts_tags (DEFAULT_INTENT_BY_CAP) |
| módulo `script_engine/m01b_narrator` (queda: LEN_*, _char_band, FORBIDDEN_OPENINGS/CLOSINGS, GENERIC_CONNECTORS, NarrationValidationError, _first_sentence, _word_count, _contains_any, _len_range, _validate_narration) | m01b_guionista.review (`_validate_narration`, `NarrationValidationError`), m01d_particion.len_range (`_len_range`) |
| módulo `script_engine/m01b_guionista` (queda: review, normalize, caps_text, sentences, wc, _surname, _verified_antagonist, _beat_cap, institution_re, INSTITUTION, …) | guion_v4 (normalize, wc, sentences, review, caps_text, _surname, _verified_antagonist), m01c_editor, m01d_particion |
| módulo `script_engine/m01c_editor` (queda: SYSTEM, SCHEMA, build_prompt, lexical_guard, GUARD_ALL, narration_tts, …) | guion_v4.editor_pass (el `--editor` de F27), m01d_particion |
| `m05_narrative.judge_narration` | fase1_5.run_guion_v4 |
| fase1_5: `run_escaleta_v3`, `run_guion_v4`, `_topic_v3`, `cargar_perfil`, `run_pantalla`, `asegurar_ficha`, papel, semilla, `_load_skeleton`, `_load_narration`, `_build_audio_script` | la única cadena (process_topic) y la reanudación `--from` |
| fase1_5 flags `--modelo` | **queda**: elige el modelo de la cadena v4 (guionista + reparación), que es la única cadena; no servía a la vieja |
| fase1_5 flags `--editor`, `--columna`, `--sin-columna`, `--modelo-escaleta`, `--temas`, `--only`, `--from`, `--semilla`, `--aprobar-papel`, `--batch`, `--no-gate`, `--no-music-gate`, `--csv` | la única cadena |

## 3. Tests que usan la cadena vieja de paso pero prueban otra cosa (se ajustan, no se borran)

| test | por qué se ajusta |
|---|---|
| test_module_f11b::test_fase1_5_pasa_el_modelo | prueba que `--modelo` llega a run_guion_v4: se le sacan `v3=True, guion="v4"` |
| test_module_f26c::test_temas_un_proceso_por_tema | prueba `temas_cmds`; usaba `--v3` como argumento cualquiera que pasa de largo: se cambia por `--columna` |
| test_module_f27::test_fase1_5_editor_solo_con_la_bandera | prueba `--editor`: se le sacan `v3=True, guion="v4"` |
| test_module_f39_fase1 (6 tests: a3, a1×2, a4×3) | prueban la cadena F39: se les sacan `v3=True, guion="v4"` (ahora es la única) |
| test_module_f5c::test_prompt_prioridad_y_relleno_nuevo | prueba también `m05_narrative.FORBIDDEN_FILLER` (vivo): quedan esas aserciones, salen las de F5_RULES/POOL_* |
| test_module_f5d::test_largo_minimo_mas_15_para_pro | prueba `_len_range` (vivo): sale la línea de `POOL_MIN_LEN_FACTOR` |
| test_module_01b_pauses.py (import) | el import de `TONE_INSTRUCTIONS_BY_INTENT, PROSE_RULES` sale; `_first_sentence` queda |
| test_chat33_pausas_conjy.py (import) | el import de `m01b_narrator` sale; los dos del normalizer quedan |
| test_module_f11.py (helpers) | `_fake_pro`, `_run_v3`, `V3_GOLDEN*`, `BANDAS_F23` solo servían al dorado v3: salen con él (los usan f22/f23 solo en los dorados que se borran) |

## 4. Ya sin llamador antes de F41 y fuera de la cadena vieja (NO se tocan; anotados)

m01a_escaleta: `to_markdown` (18 scripts de lab), los `PROMPT_VERSION_*`/`SYSTEM_V2_*` viejos (los fijan tests de
literalidad); m01d_particion: `cut_phrases` (lab f10); guion_v3_reglas: `DATE_MAX_PER_CAP`; m01b_guionista:
`INSTITUTION`; m01e_pantalla: `ESTILOS`, `TIPOS_DESCARTE`; m05_narrative: `_REPEAT_TIPOS`.

## 5. Módulos enteros

Ninguno queda sin llamador: `m01a_skeleton`, `m01b_narrator`, `m01b_guionista` y `m01c_editor` tienen llamadores vivos
(§2) → se borra lo de §1 dentro de cada uno, el archivo queda.
