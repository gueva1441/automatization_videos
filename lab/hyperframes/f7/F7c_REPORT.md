# F7c — Orleans con el pool de research v3 por la tubería v3 (+ los 3 arreglos de la validación del pool)

Rama `f7-research-v3` · topic `ba6c3cac-f7r3` · pedido: validación del analista sobre F7b («aprobado, materia prima de 9»), puntos 1–4.

**Leer:** [compara_orleans_v3r.html](compara_orleans_v3r.html) (3 columnas por cap + métricas del juez + escaleta debajo de cada v3) · [NARRACION_orleans_v3r.md](NARRACION_orleans_v3r.md) · [ESCALETA_orleans_v3r.md](ESCALETA_orleans_v3r.md).

## 1. Los tres arreglos del pool (código en `researcher_steps/research_v3.py`, tests en `test_module_f7.py`)

1. **`presente_en` por párrafo** (`presence_v3`): un evento entra si su cita literal (o su texto) nombra a la persona, o si está a ±500 caracteres de una mención suya en el mismo documento. Nunca por fechas ni rangos (`fechas_presente` queda sin usar). La persona se busca por nombre completo; el apellido solo, si nadie más lo comparte (Tyrone y Duane Lewis no se cuentan uno al otro). Elegibles re-armados: testigo, no antagonista, ≥ 3 citas o ≥ 3 datos propios, y presencia real en el año del evento (un evento que la nombra, o su propio testimonio verificado). Resultado: 89 vínculos persona-evento (antes cientos por rangos); **12 elegibles**: Brady Richard, Rhonda Ducre, Raphael Schwarz, Renard Reed, Iris Hardeman, Joyce Gilson, Tyrone Lewis, Pearl Cornelia Bland, William Short, Quantonio Williams, Dan Bright, Edward Burton. Tests: `test_presence_by_paragraph_never_by_date_range`, `test_people_names_and_eligibility`.
2. **Población con todas sus variantes** (`population_canon`, primera en `cifras_canonicas`, `tipo: "poblacion"`): **oficial 6,375** («el conteo oficial de 6375 presos del sheriff», ACLU 2006, informe). Variantes con fuente: 5,919 y 6,295 y 6,000 (Vera 2015), 6,000, 6,500 y 7,000 (ACLU), 6,375 (The Lens 2025, mismo valor que la oficial), 8,000 (DOJ 2009). Oficial = documento informe_oficial/fallo/foia y, entre esos, la cifra ATRIBUIDA a la fuente oficial («según el sheriff», «conteo oficial»); sin ninguna → `oficial: None`, `sin_oficial: true` y cada variante «según <fuente>». Fuera del grupo: otros lugares (Hunt, el paso elevado, un edificio) y subconjuntos (fuera de 0.6–1.4 × la mediana: los 2,000 presos del DOC, los 1,300 evacuados que escribieron). Test: `test_population_canon_lists_all_variants_with_source`.
3. **Digest para la escaleta** (`pool["digest"]`, aditivo): personas elegibles completas + antagonistas con ≥ 3 citas o datos, todas sus citas, 12 citas verificadas de otros testigos con nombre y 10 sin nombre, cifras canónicas, la cronología con hora + 20 eventos del año del evento, los 30 lugares más nombrados y hasta 25 datos por documento. Ids reales del pool (la escaleta y sus validadores siguen con el pool entero). **`m01a_escaleta.pool_section` usa el digest si existe** (cambio de 4 líneas; `ESCALETA_DIGEST=0` lo apaga; sin digest, igual que antes). **Prompt de la escaleta: 18,665 tokens** (medido con `count_tokens` de Gemini; digest solo 16,194; antes 63 k). Test: `test_digest_has_real_ids_and_escaleta_uses_it`.

## 2. Lo que la corrida encontró en el pool (arreglado; no son cambios de F6)

La tubería de F6 lee el pool con validadores pensados para el pool v2. Tres cosas del pool nuevo los hacían fallar en falso:

- **Una «cita» de una palabra** («no», de *an officer*): el chequeo de cierre de la escaleta la encontraba dentro de cualquier frase («años») y rechazó 8 intentos de escaleta en dos corridas. Ahora una cita de menos de 3 palabras no entra (`CITA_MIN_WORDS`).
- **Descartes de lectura como «personas que no hacen nada»**: `m05.silent_names` lee los `_descartados` de tipo personaje; R3 guardaba ahí «Preso #13», «Guardias», «Gusman» (descartados por no ser un nombre propio) y el validador vetaba «preso» y «Gusman» en la narración (9 duras falsas). Ahora esos descartes van como `personajes_r3`.
- **Cifras con punto de miles** («6.000»): `m05.non_canonical` busca `\d[\d,]*\d` y leía «000». Ahora las canónicas se escriben «6,000».

Tests: `test_one_word_quote_is_not_a_quote`, `test_pool_does_not_trip_f6_validators`. Suites F6 + F7: **66 verdes**.

## 3. La corrida (F7c)

`lab/hyperframes/f7/f7c_orleans.py`: escaleta (m01a, lee el digest) → guionista (m01b, best_of_2) → editor (m01c) → revisión v3 (m01b.review), sin otros cambios en F6. Dos diferencias con la corrida de F6c, a propósito: **sin `escaleta_notas`** (las notas del analista de F6c citan ids del pool viejo; la prueba es si la narración sube sola) y **5 intentos de escaleta** (parámetro de `generate_escaleta`; el default es 3).

| corrida | resultado | costo |
|---|---|---|
| 1 | escaleta rechazada (3 intentos) | no registrado (el runner perdía el costo si fallaba; ya lo guarda) |
| 2 | escaleta rechazada (5 intentos; el último, por la cita «no») | no registrado |
| 3 | escaleta rechazada (5 intentos; ídem) | 0.517 |
| 4 | completa, con las duras falsas de §2 (guardada en `corrida4/`) | 0.564 |
| **5** | **la que vale**: escaleta al 2.º intento, guionista elige el intento 2, editor acepta 16 de 19 | **0.500** (escaleta 0.198 + guionista 0.146 + editor 0.156) |

Costo de F7c en esta sesión ≈ US$ 1.6 medido + las corridas 1–2 (≈ 8 llamadas de escaleta, ≈ US$ 0.5–0.8). La corrida limpia cuesta lo mismo que la de F6c (US$ 0.50 contra 0.61).

## 4. Comparación (juez m05, cada versión con su pool y su skeleton/escaleta)

| métrica | v2 F5d | v3 pool viejo (F6c) | **v3 pool nuevo (F7c)** |
|---|---|---|---|
| palabras | 1,165 | 1,070 | **940** |
| densidad (ids / 100 palabras) | 1.97 | 2.15 | **1.70** |
| datos distintos | 21 | 23 | 16 |
| adjetivos / 100 | 2.58 | 2.43 | 1.81 |
| trigramas repetidos | 0.087 | 0.007 | 0.020 |
| cliffhangers | 6/6 | 6/6 | 6/6 |
| problemas de fechas | 0 | 0 | 1 |
| citas usadas | 2 | 4 | **9** |
| testigos con nombre citados | — | Burton, Norman | **Brady Richard, Luis Reyes, Renard Reed, Edward Burton** (+ Gusman) |
| revisión v3: duras / blandas | — | 4 / 14 | **16 / 25** |
| pool: datos / citas | 67 / 2 | 91 / 11 | 558 / 187 |

**Lectura (mía, sin juicio de calidad del analista):**
- **Sube** la voz de los testigos: el humano es Renard Reed, un guardia que se quedó (escaleta: «testigo presencial del abandono y la violencia desde dentro del sistema»), con sus citas en los caps 2, 5 y 6 y en la última frase del video; Brady Richard ve los francotiradores desde la terraza del CCC; Luis Reyes cierra con «Todavía hay presos muertos ahí dentro»; Burton bebe agua del inodoro. Son citas literales de la ACLU, HRW y The Lens, todas con documento.
- **No sube sola** por las métricas: la narración es más corta (caps 4, 5 y 6 bajo el mínimo de 162 palabras), menos densa y con 16 duras. Las duras que quedan son de escritura, no del pool: 9 de 16 son «declaraste ids que no están literales / usaste menos datos de los asignados». El guionista resume o parafrasea las citas largas del pool nuevo (`texto_es` de hasta ~300 caracteres: Q14, Q69, Q183) y los datos traducidos de oraciones largas, y el candado literal (cita «entera, palabra por palabra, o no se usa») las rechaza. Otra: Q183 (Burton) está verificada solo en parte y va con su nombre.
- Lo flojo a la lectura: el cap 1 (gancho sin pico; «todo comenzó cuando los oficiales empezaron a renunciar» adelanta la cita de Reed del cap 2) y el cap 3, que repite la oscuridad tres veces.

**Propuestas (sin hacer, para el analista):** (a) en el pool, un `fragmento` corto por cita (≤ 25 palabras, literal) para que el guionista pueda citar entero; (b) en la escaleta, ≤ 1 cita larga por beat; (c) volver a darle a la escaleta las notas del analista con los ids nuevos, como en F6c, si se quiere comparar en igualdad de condiciones.

## 5. Archivos

- Código: `researcher_steps/research_v3.py` (presence_v3, population_canon, build_digest, CITA_MIN_WORDS, kind `*_r3`, fmt_count), `script_engine/m01a_escaleta.py` (`pool_section`: digest con flag), `test_module_f7.py` (28 tests).
- Runners: `lab/hyperframes/f7/f7c_orleans.py`, `lab/hyperframes/f7/build_compara_v3r.py`.
- Salidas: `compara_orleans_v3r.html`, `f7c_metricas_compara.json`, `escaleta_orleans_v3r.json`, `ESCALETA_orleans_v3r.md`, `NARRACION_orleans_v3r.md`, `f7c_costos.json`, `f7c_run*.out`, `escaleta_v3r_rechazada_corrida{1,2,3}.json`, `corrida4/`; pool `00_pool_v3.json` re-armado (sin llamadas). En `data/scripts/_steps/ba6c3cac-f7r3/` (fuera de git): `01a_escaleta.json`, `01b_guionista_v3.json`, `01b_editor_v3.json`, `01b_narracion_v3.json`.
