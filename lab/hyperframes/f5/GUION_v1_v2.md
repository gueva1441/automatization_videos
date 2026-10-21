# F5c — Guion v1 vs v2 (evidencia para la validación del analista)

Medido con `script_engine/m05_narrative.py` contra el MISMO evidence_pool (el de F5b, ya filtrado) para las dos versiones. v2 se cuenta por los ids que declaró el narrador (N2); v1 no declara, se cuenta por regex.

## 1. Datos nuevos por cap y Gusman

| cap | v1 datos nuevos | v2 datos nuevos | v2 asignados (skeleton) |
|---|---|---|---|
| 1 | 3 | 2 (D05, Q01) | 6 |
| 2 | 0 | 3 (T06, D09, D10) | 5 |
| 3 | 3 | 3 (T08, D33, T09) | 5 |
| 4 | 1 | 2 (D08, D17) | 5 |
| 5 | 1 | 7 (D19, D60, T15, D67, Q02, D61, D50) | 4 |
| 6 | 2 | 2 (T26, D69) | 3 |
| 7 | 2 | 2 (D59, D58) | 5 |

Gusman nombrado: v1 en caps ninguno · v2 en caps [1, 2, 3, 5]. Personajes de v2: Marlin N. Gusman (cap 1), William Hunter (cap 1), Carl Strock (cap 2), Ronnie L. Morgan, Jr. (cap 5), Robie Waganfeald (cap 6), Paul Kunkel Jr. (cap 6)

## 2. Repetición

| dato | v1 caps | v2 caps |
|---|---|---|
| 6,500 | 4 [1, 2, 4, 7] | 1 [3] |
| «pecho» | 4 [1, 3, 4, 7] | 2 [3, 4] |
| «29 de agosto» | 3 [1, 2, 3] | 3 [1, 2, 3] |
| 500 desaparecidos | 3 [5, 6, 7] | 2 [3, 7] |
| 517 | 0 [] | 1 [5] |

v1: datos duros del pool en más de 2 caps = 2 {'D33': [1, 2, 4, 7], 'D59': [5, 6, 7]}

v2: datos duros del pool en más de 2 caps = 0 

3-gramas repetidos entre caps: v1 3.4% · v2 8.6% (umbral < 5 %)

## 3. Adjetivos → hechos

| | v1 | v2 |
|---|---|---|
| adjetivos / 100 palabras (heurística, F5b: entre 2 y 4) | 6.22 | 1.87 |
| caps fuera de 2–4 adjetivos/100 | [1, 2, 3, 4, 5, 6, 7] | [1, 2, 6] |
| densidad por regex (medición de F5) | 1.36 | 4.23 |
| densidad (datos duros / 100 palabras, umbral 2.0) | 1.36 | 2.16 |
| datos distintos del pool | 12 | 21 |
| palabras | 1398 | 1017 |

Pares de frases (mismo momento del relato):

- cap 2 · v1: «Ese día, el huracán Katrina desató su furia implacable sobre Nueva Orleans.»
  · v2: «Esa misma noche, la electricidad en la prisión se cortó, sumiendo los pabellones en una oscuridad premonitoria.»
- cap 3 · v1: «El mismo 29 de agosto de 2005, el día del impacto del huracán, los generadores de respaldo, la última línea de defensa tecnológica, sucumbieron.»
  · v2: «El 29 de agosto de 2005, los generadores de respaldo de la prisión fallaron, sumiendo a las aproximadamente 6,500 personas atrapadas dentro en una oscuridad absoluta.»
- cap 4 · v1: «Una eternidad de sufrimiento en la penumbra asfixiante.»
  · v2: «Superó esa marca.»

## 4. Cierres (cliffhanger del skeleton → últimas 2 oraciones de v2)

- **cap 1 → [T05]** El sheriff Marlin N. Gusman anuncia en una conferencia de prensa que los prisioneros no serán evacuados de la Prisión de Orleans Parish.
  cierre: «Los prisioneros, sentenció Gusman, se quedarían 'donde pertenecen'. Pero la orden que estaba a punto de dar en una conferencia de prensa sellaría el destino de todos.» — ✔ (en el cierre: Gusman, conferencia, prisioneros)
- **cap 2 → [T08]** La energía eléctrica se pierde y los generadores de respaldo fallan en la OPP.
  cierre: «Dentro de la prisión, la única barrera contra la oscuridad total eran los generadores de respaldo. Pero su energía también estaba a punto de extinguirse.» — ✔ (en el cierre: energía, generadores, respaldo)
- **cap 3 → [T13]** Comienza la evacuación de algunos edificios de la prisión (Templeman 1 y 2) cuando el agua alcanza el nivel del pecho en el interior.
  cierre: «Pero la petición llegó demasiado tarde. Para muchos, el agua ya no estaba en los tobillos; en los edificios Templeman 1 y 2, la inundación estaba a punto de alcanzar el nivel del pecho.» — ✔ (en el cierre: Templeman, edificios)
- **cap 4 → [D19]** Inmediatamente después de la evacuación, 517 reclusos no estaban contabilizados
  cierre: «Pero cuando el último prisionero fue trasladado, el horror dio paso a una pregunta aún más inquietante: ¿estaban todos? El conteo oficial revelaría un vacío imposible de explicar.» — ✔ (en el cierre: estaban)
- **cap 5 → [D69]** Un jurado federal otorga más de $650,000 a dos turistas de Ohio
  cierre: «Sin embargo, más tarde se emitieron 14 órdenes de arresto para fugitivos. Mientras la palabra de los prisioneros era enterrada, la pesadilla vivida por dos turistas atrapados en el caos estaba a punto de costarle a la ciudad más de 650,000 dólares en un tribunal federal.» — ✔ (en el cierre: 650,000, federal, turistas)
- **cap 6 → [D62]** No existen registros oficiales de lo que ocurrió en la Prisión de Orleans Parish inmediatamente después del huracán Katrina
  cierre: «Apenas semanas después del desastre, el 17 de octubre de 2005, reabrieron el edificio 'House of Detention'. Estas investigaciones y demandas se basaron en testimonios, porque al buscar la versión oficial de los hechos, se toparon con un vacío documental absoluto: simplemente no existen registros oficiales de lo que ocurrió en la prisión durante esos días críticos.» — ✔ (en el cierre: existen, registros, oficiales, ocurrió)

## F5b — repetición dentro del cap (N3) y nombres (N5)

| cap | v1 repetidos en el cap | v2 repetidos en el cap |
|---|---|---|
| 1 | «6,500» ×2 | — |
| 2 | — | — |
| 3 | — | «29 de agosto» ×2 |
| 4 | — | — |
| 5 | «500» ×4 | — |
| 6 | — | — |
| 7 | — | — |

Nombres sin acción en la historia: v1 [] · v2 []


## Violaciones que el narrador aceptó tras 3 intentos (v2)

- cap 1: [dura] declaraste en datos_usados ids que no están LITERALES en la narración (decí la cifra/fecha tal cual o sacalos de la lista): D04 · [blanda] estos datos del pool suenan en tu narración pero no están en datos_usados (si los contaste, declaralos; si es un choque de cifras —«Interestatal 10» no · [blanda] la cita «donde pertenecen…» va entre comillas y con su autor (Sheriff Marlin N. Gusman) al lado · [blanda] 1.59 adjetivos/100 palabras (mínimo 2.0): se lee como un acta; sumá 2 o 3 calificativos concretos atados a los hechos (cómo era el agua, la celda, el c
- cap 2: [blanda] estos datos del pool suenan en tu narración pero no están en datos_usados (si los contaste, declaralos; si es un choque de cifras —«Interestatal 10» no · [blanda] 0.69 adjetivos/100 palabras (mínimo 2.0): se lee como un acta; sumá 2 o 3 calificativos concretos atados a los hechos (cómo era el agua, la celda, el c
- cap 3: [dura] declaraste en datos_usados ids que no están LITERALES en la narración (decí la cifra/fecha tal cual o sacalos de la lista): T12 · [dura] cada dato se dice UNA vez por cap; después parafraseá sin la cifra («ese lunes», «esa noche», «el agua»): «29 de agosto» ×2 · [blanda] estos datos del pool suenan en tu narración pero no están en datos_usados (si los contaste, declaralos; si es un choque de cifras —«Interestatal 10» no
- cap 4: [blanda] estos datos del pool suenan en tu narración pero no están en datos_usados (si los contaste, declaralos; si es un choque de cifras —«Interestatal 10» no · [blanda] densidad 1.34 datos/100 palabras (mínimo 2.0): más datos literales del pool, menos descripción
- cap 5: [blanda] estos datos del pool suenan en tu narración pero no están en datos_usados (si los contaste, declaralos; si es un choque de cifras —«Interestatal 10» no · [blanda] nombrá a Ronnie L. Morgan, Jr. por nombre y apellido y con su cargo (Recluso, demandante) la primera vez · [blanda] la cita «Están en la cárcel, hombre. Mienten... N…» va entre comillas y con su autor (Sheriff Gusman) al lado
- cap 6: [blanda] estos datos del pool suenan en tu narración pero no están en datos_usados (si los contaste, declaralos; si es un choque de cifras —«Interestatal 10» no · [blanda] densidad 1.06 datos/100 palabras (mínimo 2.0): más datos literales del pool, menos descripción · [blanda] 1.06 adjetivos/100 palabras (mínimo 2.0): se lee como un acta; sumá 2 o 3 calificativos concretos atados a los hechos (cómo era el agua, la celda, el c
- cap 7: [blanda] densidad 1.94 datos/100 palabras (mínimo 2.0): más datos literales del pool, menos descripción · [blanda] 21% de tus frases de 3 palabras ya se dijeron en caps anteriores (máximo 5%): no repitas fórmulas («sheriff Marlin N. Gusman» basta una vez; después «e

## Umbrales del juez

- v1: {'densidad': False, 'repeticion': False, 'adjetivacion': False, 'repeticion_en_cap': False, 'nombres': True, 'antagonista': False, 'cliffhanger': None}
- v2: {'densidad': True, 'repeticion': False, 'adjetivacion': False, 'repeticion_en_cap': False, 'nombres': True, 'antagonista': True, 'cliffhanger': True}
