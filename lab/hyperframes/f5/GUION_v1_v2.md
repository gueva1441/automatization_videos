# F5d — Guion v1 vs v2 (evidencia para la validación del analista)

Medido con `script_engine/m05_narrative.py` contra el MISMO evidence_pool (el de F5b, ya filtrado) para las dos versiones. v2 se cuenta por los ids que declaró el narrador (N2); v1 no declara, se cuenta por regex.

## 1. Datos nuevos por cap y Gusman

| cap | v1 datos nuevos | v2 datos nuevos | v2 asignados (skeleton) |
|---|---|---|---|
| 1 | 3 | 3 (D04, D57, Q01) | 6 |
| 2 | 0 | 4 (T05, T06, D09, D10) | 5 |
| 3 | 3 | 3 (T08, T09, T12) | 4 |
| 4 | 1 | 3 (T13, D08, D17) | 5 |
| 5 | 1 | 4 (D19, D60, D61, Q02) | 4 |
| 6 | 2 | 2 (T26, D69) | 3 |
| 7 | 2 | 2 (D58, D59) | 6 |

Gusman nombrado: v1 en caps ninguno · v2 en caps [1, 2, 3, 5]. Personajes de v2: Marlin N. Gusman (cap 1), William Hunter (cap 1), Carl Strock (cap 2), Ronnie L. Morgan, Jr. (cap 5), Robie Waganfeald (cap 6), Paul Kunkel Jr. (cap 6)

## 2. Repetición

| dato | v1 caps | v2 caps |
|---|---|---|
| 6,500 | 4 [1, 2, 4, 7] | 0 [] |
| «pecho» | 4 [1, 3, 4, 7] | 1 [4] |
| «29 de agosto» | 3 [1, 2, 3] | 2 [1, 3] |
| 500 desaparecidos | 3 [5, 6, 7] | 2 [4, 7] |
| 517 | 0 [] | 1 [5] |

v1: datos duros del pool en más de 2 caps = 2 {'D33': [1, 2, 4, 7], 'D59': [5, 6, 7]}

v2: datos duros del pool en más de 2 caps = 0 

3-gramas repetidos entre caps: v1 3.4% · v2 8.7% (umbral < 5 %)

## 3. Adjetivos → hechos

| | v1 | v2 |
|---|---|---|
| adjetivos / 100 palabras (heurística, F5b: entre 2 y 4) | 6.22 | 2.58 |
| caps fuera de 2–4 adjetivos/100 | [1, 2, 3, 4, 5, 6, 7] | [7] |
| densidad por regex (medición de F5) | 1.36 | 3.35 |
| densidad (datos duros / 100 palabras, umbral 2.0) | 1.36 | 1.97 |
| datos distintos del pool | 12 | 21 |
| palabras | 1398 | 1165 |

Pares de frases (mismo momento del relato):

- cap 2 · v1: «Ese día, el huracán Katrina desató su furia implacable sobre Nueva Orleans.»
  · v2: «Al día siguiente, el huracán desató su fuerza.»
- cap 3 · v1: «El mismo 29 de agosto de 2005, el día del impacto del huracán, los generadores de respaldo, la última línea de defensa tecnológica, sucumbieron.»
  · v2: «La frágil esperanza de los generadores se extinguió el 29 de agosto de 2005.»
- cap 4 · v1: «Una eternidad de sufrimiento en la penumbra asfixiante.»
  · v2: «Subió sin piedad, metro a metro, en la oscuridad total.»

## 4. Cierres (cliffhanger del skeleton → últimas 2 oraciones de v2)

- **cap 1 → [T05]** El sheriff Marlin N. Gusman anuncia en una conferencia de prensa que los prisioneros no serán evacuados de la Prisión de Orleans Parish.
  cierre: «Gusman fue claro: se quedarían "donde pertenecen". Una sentencia dictada antes de que subiera el agua, que sería confirmada por la terrible decisión que el sheriff estaba a punto de anunciar.» — ✔ (en el cierre: Gusman, sheriff)
- **cap 2 → [T08]** La energía eléctrica se pierde y los generadores de respaldo fallan en la OPP.
  cierre: «Para los miles de prisioneros atrapados en la negrura, la única esperanza de luz y seguridad recaía en los generadores de respaldo. Pero estos también estaban a punto de fallar.» — ✔ (en el cierre: generadores, respaldo)
- **cap 3 → [T13]** Comienza la evacuación de algunos edificios de la prisión (Templeman 1 y 2) cuando el agua alcanza el nivel del pecho en el interior.
  cierre: «Pero mientras los papeles se movían lentamente en el exterior, en el interior, la inundación avanzaba implacable. Y en algunos edificios, el nivel del agua ya estaba subiendo mucho más allá de los tobillos.» — ✔ (en el cierre: algunos, edificios, interior)
- **cap 4 → [D19]** Inmediatamente después de la evacuación, 517 reclusos no estaban contabilizados
  cierre: «Al comparar las listas, un agujero negro apareció en los registros: faltaban más de 500 personas. ¿Dónde estaban?» — ✔ (en el cierre: estaban)
- **cap 5 → [D69]** Un jurado federal otorga más de $650,000 a dos turistas de Ohio
  cierre: «No confíen en drogadictos, cobardes y criminales para saber cuál es la historia". Pero mientras las voces de los reclusos eran silenciadas por el sistema, las de dos inesperados turistas estaban a punto de abrir una grieta legal que le costaría a la ciudad más de 650,000 dólares.» — ✔ (en el cierre: 650,000, turistas)
- **cap 6 → [D62]** No existen registros oficiales de lo que ocurrió en la Prisión de Orleans Parish inmediatamente después del huracán Katrina
  cierre: «y no encontraron nada. Porque, increíblemente, no existen registros oficiales de lo que ocurrió en la Prisión de Orleans Parish inmediatamente después del huracán Katrina.» — ✔ (en el cierre: Prisión de Orleans Parish, Orleans, Parish, Katrina)

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

- cap 1: [blanda] estos datos del pool suenan en tu narración pero no están en datos_usados (si los contaste, declaralos; si es un choque de cifras —«Interestatal 10» no · [blanda] nombrá a William Hunter por nombre y apellido y con su cargo (Adjunto del Sheriff Gusman) la primera vez
- cap 3: [blanda] estos datos del pool suenan en tu narración pero no están en datos_usados (si los contaste, declaralos; si es un choque de cifras —«Interestatal 10» no · [blanda] densidad 1.68 datos/100 palabras (mínimo 2.0): más datos literales del pool, menos descripción
- cap 4: [blanda] estos datos del pool suenan en tu narración pero no están en datos_usados (si los contaste, declaralos; si es un choque de cifras —«Interestatal 10» no · [blanda] densidad 1.52 datos/100 palabras (mínimo 2.0): más datos literales del pool, menos descripción
- cap 5: [blanda] estos datos del pool suenan en tu narración pero no están en datos_usados (si los contaste, declaralos; si es un choque de cifras —«Interestatal 10» no · [blanda] nombrá a Ronnie L. Morgan, Jr. por nombre y apellido y con su cargo (Recluso, demandante) la primera vez
- cap 6: [blanda] estos datos del pool suenan en tu narración pero no están en datos_usados (si los contaste, declaralos; si es un choque de cifras —«Interestatal 10» no · [blanda] densidad 0.9 datos/100 palabras (mínimo 2.0): más datos literales del pool, menos descripción
- cap 7: [blanda] estos datos del pool suenan en tu narración pero no están en datos_usados (si los contaste, declaralos; si es un choque de cifras —«Interestatal 10» no · [blanda] 1.9 adjetivos/100 palabras (mínimo 2.0): se lee como un acta; sumá 2 o 3 calificativos concretos atados a los hechos (cómo era el agua, la celda, el ca · [blanda] 27% de tus frases de 3 palabras ya se dijeron en caps anteriores (máximo 5%): no repitas fórmulas («sheriff Marlin N. Gusman» basta una vez; después «e

## Umbrales del juez

- v1: {'densidad': False, 'repeticion': False, 'adjetivacion': False, 'repeticion_en_cap': False, 'nombres': True, 'antagonista': False, 'cliffhanger': None}
- v2: {'densidad': False, 'repeticion': False, 'adjetivacion': True, 'repeticion_en_cap': True, 'nombres': True, 'antagonista': True, 'cliffhanger': True}
