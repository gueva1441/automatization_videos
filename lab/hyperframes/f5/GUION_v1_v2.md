# F5b — Guion v1 vs v2 (evidencia para la validación del analista)

Medido con `script_engine/m05_narrative.py` contra el MISMO evidence_pool (el de F5b, ya filtrado) para las dos versiones. v2 se cuenta por los ids que declaró el narrador (N2); v1 no declara, se cuenta por regex.

## 1. Datos nuevos por cap y Gusman

| cap | v1 datos nuevos | v2 datos nuevos | v2 asignados (skeleton) |
|---|---|---|---|
| 1 | 3 | 2 (D04, D08) | 3 |
| 2 | 0 | 3 (T03, T05, D10) | 5 |
| 3 | 3 | 3 (T08, D33, T07) | 3 |
| 4 | 1 | 2 (D67, D32) | 5 |
| 5 | 1 | 3 (T13, T15, D43) | 5 |
| 6 | 2 | 5 (D17, T17, D37, Q02, D50) | 5 |
| 7 | 2 | 0 () | 6 |

Gusman nombrado: v1 en caps ninguno · v2 en caps [2, 3, 5, 6]. Personajes de v2: Marlin N. Gusman (cap 3), William Hunter (cap 3), Robie Waganfeald (cap 6), Paul Kunkel Jr. (cap 6)

## 2. Repetición

| dato | v1 caps | v2 caps |
|---|---|---|
| 6,500 | 4 [1, 2, 4, 7] | 2 [1, 3] |
| «pecho» | 4 [1, 3, 4, 7] | 4 [1, 3, 4, 5] |
| «29 de agosto» | 3 [1, 2, 3] | 4 [1, 2, 3, 5] |
| 500 desaparecidos | 3 [5, 6, 7] | 4 [1, 3, 5, 7] |
| 517 | 0 [] | 1 [5] |

v1: datos duros del pool en más de 2 caps = 2 {'D33': [1, 2, 4, 7], 'D59': [5, 6, 7]}

v2: datos duros del pool en más de 2 caps = 0 

3-gramas repetidos entre caps: v1 3.4% · v2 7.0% (umbral < 5 %)

## 3. Adjetivos → hechos

| | v1 | v2 |
|---|---|---|
| adjetivos / 100 palabras (heurística, F5b: entre 2 y 4) | 6.22 | 4.19 |
| caps fuera de 2–4 adjetivos/100 | [1, 2, 3, 4, 5, 6, 7] | [1, 2, 3, 4, 5] |
| densidad por regex (medición de F5) | 1.36 | 3.08 |
| densidad (datos duros / 100 palabras, umbral 2.0) | 1.36 | 1.26 |
| datos distintos del pool | 12 | 18 |
| palabras | 1398 | 1431 |

Pares de frases (mismo momento del relato):

- cap 2 · v1: «Ese día, el huracán Katrina desató su furia implacable sobre Nueva Orleans.»
  · v2: «Ese mismo día, los reclusos recibieron su última comida antes de que el huracán azote, un acto macabro previo a la inanición.»
- cap 3 · v1: «El mismo 29 de agosto de 2005, el día del impacto del huracán, los generadores de respaldo, la última línea de defensa tecnológica, sucumbieron.»
  · v2: «El 29 de agosto de 2005, la energía eléctrica se perdió y los generadores de respaldo fallaron en la Prisión Parroquial de Orleans (OPP).»
- cap 4 · v1: «Una eternidad de sufrimiento en la penumbra asfixiante.»
  · v2: «Los días se hicieron indistinguibles en la oscuridad total.»

## 4. Cierres (cliffhanger del skeleton → últimas 2 oraciones de v2)

- **cap 1 → [T05]** El sheriff Marlin N. Gusman anuncia en una conferencia de prensa que los prisioneros no serán evacuados de la Prisión de Orleans Parish.
  cierre: «La desesperación flotaba en el aire estancado. Pero lo peor estaba por venir: la decisión fría del sheriff sellaría un destino aún más cruel.» — ✔ (en el cierre: sheriff)
- **cap 2 → [T08]** La energía eléctrica se pierde y los generadores de respaldo fallan en la OPP.
  cierre: «Un devastador 80% de Nueva Orleans se hundió bajo hasta 15 pies de agua oscura y traicionera. Las calles se convirtieron en ríos caudalosos, las casas en precarias islas, y la prisión, ya aislada por la decisión humana, se vería pronto condenada a una oscuridad aún más profunda y terminal cuando, de forma inminente, su energía eléctrica se perdiera y sus generadores de respaldo fallaran.» — ✔ (en el cierre: energía, eléctrica, generadores, respaldo)
- **cap 3 → [D06]** Los generadores de respaldo de la prisión fallaron el 29 de agosto de 2005
  cierre: «Para ellos, los reclusos eran un problema, no víctimas, y la negativa a evacuar fue una sentencia. ¿Qué significaría ahora la ausencia de luz y aire para los miles atrapados en esas celdas inundadas?» — ✘ 
- **cap 4 → [T13]** Comienza la evacuación de algunos edificios de la prisión (Templeman 1 y 2) cuando el agua alcanza el nivel del pecho en el interior.
  cierre: «La agonía parecía interminable, pero un atisbo de movimiento se aproximaba. Algunos edificios comenzarían a ser evacuados, pero no sin antes enfrentar una prueba final en las aguas turbias.» — ✔ (en el cierre: algunos, edificios)
- **cap 5 → [T17]** Se completa la evacuación total de la Prisión Parroquial de Orleans.
  cierre: «A pesar de los avistamientos y estas alarmantes cifras de ausencias, la Prisión Parroquial de Orleans aún esperaba una acción final. Una evacuación total estaba a punto de completarse, pero la verdad sobre lo ocurrido en sus muros inundados seguiría siendo un secreto oscuro.» — ✔ (en el cierre: Parroquial, Orleans, evacuación, Prisión)
- **cap 6 → [T25]** El Departamento de Justicia de EE. UU. emite una carta de hallazgos sobre las condiciones en la OPP
  cierre: «A pesar de los intentos de barrer la verdad bajo la alfombra de la negación oficial, los ecos de Orleans persistían. Una investigación aún más profunda se avecinaba, proveniente de las más altas esferas del gobierno, que comenzaría a desvelar una narrativa institucional de fallas y abusos aún más sombría.» — ✘ 

## F5b — repetición dentro del cap (N3) y nombres (N5)

| cap | v1 repetidos en el cap | v2 repetidos en el cap |
|---|---|---|
| 1 | «6,500» ×2 | — |
| 2 | — | — |
| 3 | — | — |
| 4 | — | — |
| 5 | «500» ×4 | — |
| 6 | — | — |
| 7 | — | — |

Nombres sin acción en la historia: v1 [] · v2 []


## Violaciones que el narrador aceptó tras 3 intentos (v2)

- cap 1: estos datos del pool suenan en tu narración pero no están en datos_usados (si los contaste, declaralos; si es un choque de cifras —«Interestatal 10» no son los  · 10.59 adjetivos/100 palabras (máximo 4.0): sacá adjetivos — devastador, brutal, densa, imparable, atrapados, sofocante, estancado, fría, cruel
- cap 2: declaraste en datos_usados ids que no están LITERALES en la narración (decí la cifra/fecha tal cual o sacalos de la lista): T04 · estos datos del pool suenan en tu narración pero no están en datos_usados (si los contaste, declaralos; si es un choque de cifras —«Interestatal 10» no son los  · densidad 1.44 datos/100 palabras (mínimo 2.0): más datos literales del pool, menos descripción · 5.26 adjetivos/100 palabras (máximo 4.0): sacá adjetivos — devastador, macabro, siguiente, fría, tajante, vibrante, oscura, caudalosos, profunda, inminente
- cap 3: usaste 2 de los datos asignados (mínimo 3); faltan literales o sin declarar en datos_usados: [T09] «29 de agosto» · declaraste en datos_usados ids que no están LITERALES en la narración (decí la cifra/fecha tal cual o sacalos de la lista): T09 · estos datos del pool suenan en tu narración pero no están en datos_usados (si los contaste, declaralos; si es un choque de cifras —«Interestatal 10» no son los  · densidad 1.38 datos/100 palabras (mínimo 2.0): más datos literales del pool, menos descripción · 1.84 adjetivos/100 palabras (mínimo 2.0): se lee como un acta; sumá 2 o 3 calificativos concretos atados a los hechos (cómo era el agua, la celda, el calor), si · el cierre tiene que anticipar el dato concreto del cap 4: «Los generadores de respaldo de la prisión fallaron el 29 de agosto de 2005» (nombralo o dejalo incomp
- cap 4: usaste 2 de los datos asignados (mínimo 3); faltan literales o sin declarar en datos_usados: [D06] «29 de agosto»; [T10] «29 de agosto»; [T11] «29 de agosto» · declaraste en datos_usados ids que no están LITERALES en la narración (decí la cifra/fecha tal cual o sacalos de la lista): T11, T10 · estos datos del pool suenan en tu narración pero no están en datos_usados (si los contaste, declaralos; si es un choque de cifras —«Interestatal 10» no son los  · densidad 1.03 datos/100 palabras (mínimo 2.0): más datos literales del pool, menos descripción · 5.64 adjetivos/100 palabras (máximo 4.0): sacá adjetivos — sofocante, indistinguibles, atrapados, insoportable, constante, escalofriante, olvidados, flotante, i
- cap 5: estos datos del pool suenan en tu narración pero no están en datos_usados (si los contaste, declaralos; si es un choque de cifras —«Interestatal 10» no son los  · densidad 0.99 datos/100 palabras (mínimo 2.0): más datos literales del pool, menos descripción · 4.29 adjetivos/100 palabras (máximo 4.0): sacá adjetivos — eterna, cruel, siguiente, fangosa, desgarradora, turbias, sombría, inquietante, vigilante, aterrador,
- cap 6: estos datos del pool suenan en tu narración pero no están en datos_usados (si los contaste, declaralos; si es un choque de cifras —«Interestatal 10» no son los  · el cierre tiene que anticipar el dato concreto del cap 7: «El Departamento de Justicia de EE. UU. emite una carta de hallazgos sobre las condiciones » (nombralo

## Umbrales del juez

- v1: {'densidad': False, 'repeticion': False, 'adjetivacion': False, 'repeticion_en_cap': False, 'nombres': True, 'antagonista': False, 'cliffhanger': None}
- v2: {'densidad': False, 'repeticion': False, 'adjetivacion': False, 'repeticion_en_cap': True, 'nombres': True, 'antagonista': True, 'cliffhanger': False}
