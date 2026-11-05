# F78d chascada — los 3 tests de lab/hyperframes/f78c/a/suite.log, corridos en a6ff9a9

Corridos en el árbol de a6ff9a9 (`git archive`, `data/` y `output/` reales en solo lectura) y en el checkout: `3 failed, 1 passed`
igual en los dos (el que pasa es f51c [7-end]). **Los 3 ya fallaban en a6ff9a9, con el mismo error.** No se arregló nada.

| test | falla en a6ff9a9 | falla en HEAD | causa |
|---|---|---|---|
| `test_module_f51c.py::test_f51c_corte_veo_real_de_wittenoom[1-start-paredes de chapa.]` | sí | sí, mismo error | dato real: `output/audio/123bbb64…/sync_map.json` (fuera de git) se reescribió el 2026-10-31 23:08; ch01 pasó de 32,96 s a 65,68 s → la zona Veo baja de 109 a 55 caracteres y el final de oración más cercano es «venda blanca.» (75), no «paredes de chapa.» (115). `_carve_veo_zones` sin cambios desde 57f6aaf; el test, desde 3e1cc98 (los dos del 2026-10-29) |
| `test_module_m03_merge_timing.py::test_c_guarda_de_minimo` | sí | sí, mismo error (`4 == 3`) | código: f59d205 (2026-07-04, «fallback endurecido» de `anchor_timing.py`) solo busca un ancla de una palabra si tiene ≥ 4 letras; las anclas del test son «a» «b» «c» «d» → sin tiempo → no hay fusión. Primer commit que falla: f59d205 (f59d205~1 pasa) |
| `test_module_m03_merge_timing.py::test_c_veo_path_y_veo_anchor_intacto` | sí | sí, mismo error (`0 == 1`) | lo mismo desde f59d205 («uno», «dos»: 3 letras) |
