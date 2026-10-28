# F50 B — verificación del prompt de foto en producción (en seco, sin API)

Script: `lab/hyperframes/f50/verificar_b.py` (datos en `B_VERIFICACION_datos.json`).

## 1. Pedido (cap 2 de Wittenoom, canon S5 de F48, anclas y beats de `f50/antes/03_visual.json`)

| | lab (`f48/pedidos/pedido_S5_ch02.txt`, `slots_S5_ch02.json`) | producción |
|---|---|---|
| sistema + usuario | `278e1fe2eba1aa1dee0d3fe1c177875c` | `278e1fe2eba1aa1dee0d3fe1c177875c` |
| esquema | `fa1ebfd1a34c53b070f2879ebd1f4181` | `fa1ebfd1a34c53b070f2879ebd1f4181` |

**Iguales byte a byte.**

## 2. Armado (casilleros crudos de `f48/slots_S5_ch02.json` y `slots_S5_ch07.json` por `_render_prompts_seedream`)

28 prompts contra los S5 de `f49/PROMPTS_F49.json`: **26 iguales**, 2 distintos, los dos por la chascada del cartel; años distintos: 0. Ninguna foto de estos caps tocaba la chascada de la cifra en mayúscula.

| cap | foto | antes (F49) | después (F50) |
|---|---|---|---|
| 2 | 13 | On the wooden sign board beside the shed reads "WITTENOOM" in hand-painted block letters lettering, in clear crisp lettering. | The words "WITTENOOM" are written on the wooden sign board beside the shed in hand-painted block letters, in clear crisp lettering. |
| 7 | 11 | On the warning sign fixed to the barricade reads "DANGER ASBESTOS" in faded block stencil lettering, in clear crisp lettering. | The words "DANGER ASBESTOS" are written on the warning sign fixed to the barricade in faded block stencil, in clear crisp lettering. |

Cualquier otra diferencia habría sido PARADA: no hubo.

## 3. Lo borrado y sus tests

| dónde | qué | tests |
|---|---|---|
| `m03_visual.py` | `SEEDREAM_SLOTS_USE_PRO`, `_SEEDREAM_SLOTS_MODEL_LABEL`, `FLUIDIFY_MAX_WORKERS`, `call_pro_json` (import) | `test_module_134b_fluidificador_flash.py`: bloques 1 y 4 fuera (quedan 2 y 3, de gemini_helpers y el reporte de costos) |
| `m03_visual.py` | fluidificador: `FLUIDIFICADOR_SYSTEM`, `_FLUIDIFICADOR_SCHEMA`, `_build_fluidificador_user`, `_fluidify_item` | `test_module_f27.py`: 3 tests fuera (11 → 8); `test_module_cost_tracker_gemini.py` y f27: rótulo `m03:fluidificador`/`m03:slots` → `ficha_caso` |
| `m03_visual.py` | Guarda 1 / candado de cifras: `_UNIT_GROUPS`, `_GROUP_EN`, `_GROUP_ANY_RE`, `_MEASURE_UNITS*`, `_NAME_PREFIX_RE`, `_MEASURE_RE`, `_YEAR_RE`, `_unit_to_mtype`, `_has_name_prefix`, `_classify_locked_facts`, `MAX_MEASURES_PER_IMAGE`, `_enforce_measure_fit`, `_digit_variants`, `_SPANISH_UNIT_WORDS`, `_measure_unit_adjacent`, `_post_check_locked`, `_seedream_facts_verbatim` | `test_m03_guarda1_degrade.py` borrado (5 tests) |
| `m03_visual.py` | re-tejido: `LEAK_MAX_RETEJIDOS`, `_fluidify_with_leakage_guard`, `_find_text_leakage`, `_LEAK_ATTACH_WORDS`, `_LEAK_ATTACH_RE`, `_scrub_text_leakage` | `test_module_03_leakage_retry.py`: chequeos 1–4 fuera (queda el 5, de fase1_5) |
| `m03_visual.py` | `_f8_finish_item` (re-tejido F8) y el camino v2 sin escaleta | `test_module_f8.py`: fixture nuevo (Opus falso), `test_render_v2_sin_cambios` → `test_sin_escaleta_no_hay_casilleros`, +2 tests (17 → 19); `test_module_f8b.py` (17, una aserción ajustada) |
| `m03_visual.py` | `_VEO_VIDEO_PROMPT_STRUCT`, `_SEEDREAM_MOTION_SYSTEM` (C) | sin tests previos; `test_module_f50b.py` comprueba que no están |
| `m03_imagenes_v3.py` | `wrap_style` (quedó sin uso) | `test_module_f8.py`: `test_estilo_al_principio_y_al_final` → `test_estilo_en_el_medio_del_armado` |
| `topic_researcher.py` (A) | la llamada al 4e y su guardado | `test_module_f39_research.py`, `test_module_f7d.py` |

Se mantiene `_validate_no_text_leakage` (su pasada 1 es ahora el backstop `_sacar_frases_con_texto`) y su test `test_module_03_text_leakage_casing.py`.

Grep final (producción, sin `lab/` ni `_*.py`): ningún uso vivo de lo borrado. Quedan los nombres solo en `test_module_f50b.py`, que comprueba que no existen.
