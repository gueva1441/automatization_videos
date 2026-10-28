# Notas de auditoría — zona research, parte research_c

Solo materia prima, sin propuestas. Los md5 de los 11 archivos coinciden con los de A al terminar de leer.

## Código muerto o casi muerto
- `researcher_steps/verify_quotes.py:166` `verify_literal` y `:241` `verify_testimonios`: ningún llamador en producción (el segundo solo lo toca `test_module_f6b.py`). Arrastran sin uso real a `judge` (81), `_parse` (71), `_domain` (50), `build_prompt` (34), `find_literal` (147), `doc_ok` (156) y `_search` (223); de todo el archivo solo se usan `_grounding`, `resolve_redirect`, `FFFD`, `_nz`, `_pattern` (research_v3.py:165,191,372,1179,1218,1227,1246) y `_named` (m01b_guionista.py:212).
- `researcher_steps/evidence_pool.py:697` `add_block`: solo `test_module_f6a.py` la llama.
- `script_engine/evidence.py:177` `format_pool`: nadie la nombra, ni tests; solo el docstring (línea 8).
- `researcher_steps/step_4d_summary.py:148-150`: `if len(summary) < 500: pass` no hace nada (el comentario dice que el orquestador loguea el tamaño; no lo hace esta función).

## Dos lógicas para lo mismo
- Verificación de citas literal: `verify_quotes.py:127-220` (`_nz`, `_pattern`, `find_literal`, `verify_literal`) y la verificación de `research_v3.py` (`DocText`, líneas 1177-1250, cuyo docstring dice que normaliza «como `verify_quotes._nz`») conviven; research_v3 solo importa de verify_quotes las piezas chicas.
- Armado del pool: con RESEARCH_V3 por defecto (`research_v3.py:57-61`) solo se usan de evidence_pool `fix_caps`, `_content_set`, `norm`, `acting_filter`, `anchor_place` y `geocode` (research_v3.py:1399,1718,1925,2042). `extract_evidence_pool` (758), `validate_block` (349), `merge` (444), `canonical_figures` (614), `presence` (678), `unrelated_lines` (191), `build_prompt` (319) y `SCHEMA` (65) corren solo con `RESEARCH_V3=0` (`topic_researcher.py:575`, `step_4a_facts.py:128`). research_v3 tiene su propio `canonical_v3`, `validate_doc_items` y `merge_docs` para lo mismo.
- `norm`: `evidence_pool.py:96` es un alias de `nombres.norm`; `script_engine/evidence.py:25` tiene su propia implementación (NFD sin marcas, no respeta la regla «solo letras latinas: й, ё intactas» que dice el docstring de la otra). Dos normalizaciones con el mismo nombre en dos módulos que se importan entre sí por el pool.
- `literal_in`: `evidence_pool.py:103` (subcadena normalizada) y `evidence.py:142` (con formas en palabras y números): mismo nombre, semántica distinta.
- `_content_set` (`evidence_pool.py:163`, raíces de 5, palabras ≥ 4, solo latino) vs `_content` (`evidence.py:157`, raíces de 6, palabras ≥ 5, cualquier alfabeto, con stopwords); `_sents` (`evidence_pool.py:182`) vs `_sentences` (`evidence.py:161`); `fix_caps` (`evidence_pool.py:292`, con lista fija `_COMMON_HEADS`) vs `fix_glued_caps` (`evidence.py:333`, con roles del pool + `nombres.tratamientos`). El comentario F21 de evidence.py dice que nombres.py es «única fuente», pero ambas versiones siguen vivas.
- `_num_forms`: `ficha_caso.py:360` devuelve `set[str]` y `evidence.py:106` devuelve `list[str]` (dígitos a palabras con `num_es.variants`); mismo nombre, tipo y fin distintos. `ficha_caso.py:412-448` (`word_numbers`: palabras a dígitos) es otra tabla de números en español aparte de `script_engine/num_es.py`.
- `step_4b/4c/4d/4e`: cuatro `_format_facts` casi iguales (`step_4b_canonical.py:17`, `step_4c_meta.py:25` con etiqueta de bloque, `step_4d_summary.py:17`, `step_4e_visual_canon.py:83`) y tres formateadores de bloques que truncan distinto (1500 en 4b, 800 en 4c, completo en 4d, 1500/6000 en 4e).
- `step_4a_facts.py:81` `with_pool=True` por defecto (llama a evidence_pool) y `topic_researcher.py:577` lo pisa con `with_pool=False` en la ruta v3: el parámetro existe para que la ruta v3 lo apague.

## Rutas de la cadena borrada (F41) o restos
- `ficha_caso.py:744` y `:844` importan `STEPS_DIR` de `script_engine/m01a_skeleton.py` (módulo que F41 recortó pero que sigue siendo dueño de `STEPS_DIR`, `finalize_pool_plan` y `SCREEN_PER_CAP`; m01a_escaleta.py:58 lo reimporta). No hay import roto.
- `ficha_caso.py:138-266`: tres SYSTEM de ~45 líneas cada uno (f23-1, f22-1, f15-1). F22 y F15 solo se piden con `system("f22-1")` / `system("f15-1")` explícito; no vi en producción ningún llamador con esa versión (el grep de `system(` fuera de tests solo muestra la del propio guion_v4.py:528 y el default). Sirven para tests byte-idénticos y reproducir fichas viejas, según sus comentarios (líneas 46-47, 136, 181, 226).
- `evidence.py:346` `resolve_declared` depende de `datos_usados`, que arma `m01b_guionista.py:84` desde `ids_usados`; su único llamador es `m01b_guionista.py:152` (dentro de `review`, que guion_v4.py:1216 sí usa).
- `step_4a_facts.py` y `step_4e` conservan la ruta `RESEARCH_V3=0` (4 ángulos resumidos) que research_v3.py:22 describe «sin cambios».

## Comentarios o docstrings que no coinciden con el código
- `step_4e_visual_canon.py:8-18` y `topic_researcher.py:11` dicen que el 4e produce 4 bloques; el código produce 5 (`central_subject`, líneas 412-415, 527-536, 597, 827) y el prompt dice «CINCO bloques» (línea 152). `extract_visual_canon` docstring (763-765) también lista 4.
- `step_4e_visual_canon.py:458` comenta «gemini_helpers L127-129» (referencia a línea ya vieja, no verificada).
- `step_4b_canonical.py:128` el comentario dice «Truncar si Gemini se pasó de palabras» pero el corte es por 500 caracteres (línea 129).
- `ficha_caso.py:335` el prompt de usuario fija «escenas (6–15), hechos (40–80), citas (10–25)» mientras SYSTEM_F22_1 y SYSTEM_F15_1 piden 8–15, 60–80 y 15–25: con `system("f22-1")` el sistema y la tarea final se contradicen.
- `ficha_caso.py:5-6 y :46 citan casos concretos (los 509 ítems de Ycuá, Orleans, Puerto Cardal) en docstrings de un módulo genérico.
- `pool_gate.py:6-12` y `:106-112`: el docstring y el texto del reporte repiten números (datos 150, citas verificadas 8, elegibles 2, eventos con fecha 10; pisos 40/2/3; «12 min», «≈ 1,500 palabras», «7–14 beats») que viven en `script_engine/video_length.py`; si cambian allá, el reporte seguiría diciendo lo viejo.
- `step_4d_summary.py:61` pide 1.800 palabras de guion y `step_4c_meta.py:61` «español neutro»; la ruta de guion actual es la v4, no verifiqué si esos números siguen vigentes.

## Números y reglas sin origen que encontré en DECISIONES.md
Busqué por grep en `DECISIONES.md` y no aparecen (el origen es solo un comentario de handoff F5/F14/F15b/F23 en el código):
- `evidence_pool.py:491` `GEO_MAX_KM = 400.0`, `:577` `CANON_RATIO = 1.5`, `:175` `UNRELATED_MIN_SHARED = 2`, `:624-625` piso de cifras ≥ 1000.
- `verify_quotes.py:124` `AUTHOR_WINDOW = 400` y `:160` «evento + 20 años».
- `ficha_caso.py:48` `MAX_LEV = 3` (el docstring lo cita de F12).
- `step_4e_visual_canon.py:110,113` truncados 1500 y 6000; `step_4c_meta.py:46` truncado 800; `step_4b_canonical.py:129` 500/497.

## Reglas hechas a medida de un caso
- `evidence_pool.py:289` `_COMMON_HEADS = ("Sheriff", "Huracán", "Teniente General", …, "Recluso")`, `:576` `_COUNT_NOUN` (reclusos|presos|prisioneros|evacuados…) y `:571-575` `_OFICIAL`/`_MEDIOS` (sheriff, departamento, estadísticas del…) están escritas para el caso de la prisión de Orleans, en un módulo genérico.
- `evidence_pool.py:59` `USER_AGENT` dice «contact: repo owner»; `geocode` pega contra Nominatim real con `time.sleep(1.1)` (red, no gasto en US$) cuando no hay caché.

## Cosas raras de comportamiento
- `ficha_caso.py:825-830` `save` toma el gasto de `cost_tracker.current_video`; corrida desde `main()` (`python -m researcher_steps.ficha_caso`, líneas 840-858) no abre video, así que `usd` queda en 0.0 aunque haya llamada paga. Con `usd=None` y sin video activo, igual.
- `ficha_caso.py:826` mismo módulo en `fase1_5.asegurar_ficha` (fase1_5.py:265): ahí sí hay video abierto o no según quién llame; no lo verifiqué.
- `step_4c_meta.py:158` `virality_score` solo lo nombra `topic_researcher.py` entre los archivos de producción (grep): no encontré otro consumidor.
- `research_summary` (4d) lo leen `m03_visual.py`, `m06_assembler.py` y `topic_validator.py` según grep; `m06_assembler` y `m03_visual` son de otra parte, no verifiqué si todavía están vivos en el form.
- `verify_quotes.py:223-238` `_search` usa `gemini_client` y `cost_tracker` con la etiqueta «verify_quote»; sin llamador real, así que esa etiqueta de costo no puede aparecer en una corrida actual.
- `pool_gate.py:43-44` `_tipo_evento` importa `caso()` de `research_v3` dentro de una función cuando el pool no trae `_tiempo`: dependencia de pool_gate hacia research_v3 y de research_v3 (línea 2609) hacia pool_gate.

## Discrepancias con `estado_a`
Ninguna: leí los 11 archivos y los 11 son `vivo`. Matices: `verify_quotes.py` está vivo solo por sus piezas chicas (ver arriba); la mayor parte de `evidence_pool.py` está viva solo con `RESEARCH_V3=0`. `evidence_pool.py` en A figura alcanzando fondos a render (por alias de nombres como `norm`); leyendo el código solo corre en `research`.
