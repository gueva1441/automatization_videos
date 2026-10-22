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

## 6. Diferencias con el handoff §8 (no hechas, a confirmar)

Durante la corrida apareció un §8 nuevo en `HANDOFF_F7_research_v3.md` (decisiones de Omar, 22:30). Ese texto entró en el commit wip `8291ff5` junto con mis archivos: no lo escribí yo. Su prompt (§8.4) agrega cosas que el pedido que recibí no tiene:
- **§8.4.4 / §8.2: parámetros de largo** en config (`target_words=1500`, `max_words=1700`, `dev_cap_seconds=105`, `max_images_per_video=90`, y en `m03_visual` solo el tope de `_calculate_image_count`) y **correr F7c con esos parámetros**. No hecho: la corrida usó los objetivos de palabras actuales de la escaleta (≈ 1,100–1,300). Toca `m03` (freno) y cambia el largo de los tres guiones comparados; necesita el OK.
- **§8.1.3: lugares con lat/lon en el digest.** El digest lista los lugares sin coordenadas.
- **§8.1.4: geocoder** (Jena en Nueva Orleans, I-10 en Baton Rouge, Angola con 4 nombres). Marcado «no bloquea F7c»: no hecho.

**Nota sobre elegibles (observación 1b del revisor):** Renard Reed (el humano de la escaleta) y Edward Burton son elegibles por su propio testimonio verificado, no por eventos vinculados: los dos tienen `presente_en` vacío (ningún evento de la cronología los nombra ni está a ±500 caracteres de una mención suya). Si «presencia real» tiene que ser un evento, quedan afuera y los elegibles bajan a 10; es una decisión del analista.

## 7. Veredicto del revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | `presente_en` por cita o párrafo ±500, sin rangos, con test | OK | `00_pool_v3.json`: 89 vínculos (el reporte dice 89). `test_presence_by_paragraph_never_by_date_range` pasa. |
| 1b | Elegibles re-armados (≥3 citas o ≥3 datos propios con presencia real) | PARCIAL | Hay 12 elegibles, coincide con el reporte. Renard Reed tiene 0 vínculos `presente_en`, 3 citas y 0 datos. Edward Burton tiene 0 vínculos, 3 citas y 1 dato. Iris Hardeman y William Short tienen 0 citas. Reed es el "humano" de la escaleta. El reporte reconoce la regla "o su propio testimonio verificado", pero eso no es literalmente "presencia real" del pedido. |
| 2 | Población: todas las variantes con fuente; oficial = informe/fallo; si no hay, "sin oficial" | OK | `cifras_canonicas[0]`: oficial 6,375 (ACLU 2006, dato D51 "conteo oficial del sheriff"). Variantes: 5,919, 6,000 (dos fuentes), 6,295, 6,375 (The Lens, "mismo valor"), 6,500, 7,000 y 8,000 (DOJ). Cada variante lleva `estatus` "según <fuente>". El test pasa. |
| 3 | `pool["digest"]` aditivo, con elegibles y citas, cifras, cronología con hora, lugares y datos por doc | OK | `pool["digest"]` tiene `texto`, `ids` y `caracteres` (50,065 caracteres). El reporte dice hasta 25 datos por doc, dentro del tope de 40. |
| 3b | `m01a` usa el digest con flag, cambio mínimo | OK | `git diff 5929eda..HEAD -- script_engine/` muestra solo +4 líneas en `pool_section` de `m01a_escaleta.py`, con flag `ESCALETA_DIGEST=0`. |
| 3c | Tokens ≤20k | NO VERIFICABLE | El reporte dice 18,665, medido con Gemini `count_tokens`. No pude medirlo sin LLM. 50k caracteres es plausible para ese rango. Falta correr `count_tokens` sobre `pool_section(pool)`. |
| 4 | Corrida Orleans `ba6c3cac-f7r3` por escaleta → guionista → editor → validadores; sin otros cambios en F6 | OK | `f7c_orleans.py` y `01b_narracion_v3.json` existen. `git diff --stat` en `script_engine/` toca solo `m01a_escaleta.py`. |
| 4b | `compara_orleans_v3r.html` con 3 columnas, métricas del juez y escaleta | OK | Existe, 32 KB. Los números del §4 del reporte coinciden con `f7c_metricas_compara.json`: 940 palabras, densidad 1.70, 9 citas, 558/187. Las 16 duras y 25 blandas coinciden con `revision` en `01b_narracion_v3.json`. |
| 4c | Costos del reporte | OK | `f7c_costos.json`: 0.1976 + 0.1461 + 0.1558 = 0.4995 (0.500). La corrida 3 da 0.517 y la 4 da 0.564. |
| 5 | Tests F6a/b/c + F7 | OK | `pytest` de los 4 archivos: 66 passed. |
| 6 | §8 del handoff (largo, m03, lat/lon, geocoder) no hecho y declarado | OK | `F7c_REPORT.md` §6 lo declara y lo justifica: toca `m03`, que es un freno, y cambia el largo de los tres guiones comparados. Está bien declarado frente al pedido de chat, que no incluye esos puntos. |

Observaciones:
- **Elegibilidad:** ver 1b arriba. Es el hallazgo principal. Conviene decirle a Omar que Reed y Burton son elegibles por testimonio y no por vínculos de presencia.
- **Alcance de F6:** solo `m01a` cambió en `script_engine/`. Los arreglos de `m05` (descartes `personajes_r3`, cifras "6.000" con punto, `CITA_MIN_WORDS`) se hicieron del lado del pool, en `research_v3.py`. Eso cumple el freno, aunque el reporte los presenta como "lo que la corrida encontró".
- **Sin commitear:** `F7c_REPORT.md` (+7 líneas, el §6) y `lab/ESTADO_SESION.md` están modificados y sin commitear.
- **Proceso:** hubo 5 corridas. Las corridas 1 y 2 no registraron costo, y el reporte lo declara.
- **Resultado de calidad:** la narración nueva es más corta y tiene más duras (16 contra 4), y el reporte lo dice sin maquillarlo.

Fuera de alcance: ninguno. Los archivos modificados sin commitear (`diag_234_cap4.py`, `gfx_profiles/*`) son preexistentes y no pertenecen a esta etapa. El `§8` de `HANDOFF_F7_research_v3.md` entró en el commit `8291ff5` pero lo escribió el analista, no CC, y el reporte lo aclara.

Riesgos que el contrato no cubre: el pedido no dice cómo tratar a un testigo con citas verificadas pero sin evento vinculado, como Reed. Las duras de la narración nueva siguen sin resolver: son 16, y 9 son de ids o citas no literales. Las notas del analista no se reinyectaron, así que la comparación contra F6c no es en igualdad de condiciones. El reporte lo declara.
