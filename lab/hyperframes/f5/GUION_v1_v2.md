# F5 §3 — Guion v1 vs v2 (evidencia para VALIDACION_F5)

Medido con `script_engine/m05_narrative.py` contra el MISMO evidence_pool para las dos versiones.

## 1. Datos nuevos por cap y Gusman

| cap | v1 datos nuevos | v2 datos nuevos | v2 asignados (skeleton) |
|---|---|---|---|
| 1 | 3 | 4 (D33, D59, T07, Q01) | 6 |
| 2 | 0 | 5 (D04, D09, D10, D54, T05) | 5 |
| 3 | 3 | 7 (D06, D65, T08, T09, T10, T11, T12) | 5 |
| 4 | 1 | 8 (D08, D17, D32, D38, D66, D67, T13, T17) | 5 |
| 5 | 1 | 8 (D19, D43, D60, D61, D68, T15, T23, Q02) | 4 |
| 6 | 2 | 6 (D21, D50, D72, T19, T26, T27) | 3 |
| 7 | 2 | 3 (D05, D57, D58) | 6 |

Gusman nombrado: v1 en caps ninguno · v2 en caps [1, 2, 3, 5, 6, 7]. Personajes de v2: Marlin N. Gusman (cap 1), William Hunter (cap 1), Carl Strock (cap 2), Ronnie L. Morgan, Jr. (cap 5), Cornel Hubert (cap 5), Robie Waganfeald (cap 6), Paul Kunkel Jr. (cap 6), Raphael Schwarz (cap 6)

## 2. Repetición

| dato | v1 caps | v2 caps |
|---|---|---|
| 6,500 | 4 [1, 2, 4, 7] | 2 [1, 3] |
| «pecho» | 4 [1, 3, 4, 7] | 2 [3, 4] |
| «29 de agosto» | 3 [1, 2, 3] | 3 [1, 2, 3] |
| 500 desaparecidos | 3 [5, 6, 7] | 2 [1, 3] |
| 517 | 0 [] | 1 [5] |

v1: datos duros del pool en más de 2 caps = 2 {'D33': [1, 2, 4, 7], 'D59': [5, 6, 7]}

v2: datos duros del pool en más de 2 caps = 0 

3-gramas repetidos entre caps: v1 3.4% · v2 4.1% (umbral < 5 %)

## 3. Adjetivos → hechos

| | v1 | v2 |
|---|---|---|
| adjetivos / 100 palabras (heurística, umbral calibrado 3.6) | 6.22 | 2.93 |
| densidad (datos duros / 100 palabras, umbral 2.0) | 1.36 | 3.29 |
| datos distintos del pool | 12 | 41 |
| palabras | 1398 | 1397 |

Pares de frases (mismo momento del relato):

- cap 2 · v1: «Ese día, el huracán Katrina desató su furia implacable sobre Nueva Orleans.»
  · v2: «Al día siguiente, el 29 de agosto de 2005, el huracán Katrina, de categoría 3, golpeó la costa de Luisiana con una fuerza devastadora.»
- cap 3 · v1: «El mismo 29 de agosto de 2005, el día del impacto del huracán, los generadores de respaldo, la última línea de defensa tecnológica, sucumbieron.»
  · v2: «La noche en que la red eléctrica falló, los generadores de respaldo de la Prisión de Orleans Parish no tardaron en seguirla.»
- cap 4 · v1: «Una eternidad de sufrimiento en la penumbra asfixiante.»
  · v2: «Dentro de algunos edificios de la prisión, como Templeman 1 y 2, el agua alcanzó el nivel del pecho.»

## 4. Cierres (cliffhanger del skeleton → últimas 2 oraciones de v2)

- **cap 1 → [T05]** El Sheriff Marlin N. Gusman anuncia en una conferencia de prensa que los prisioneros no serán evacuados de la Prisión de Orleans Parish.
  cierre: «Un horror olvidado, enterrado bajo las aguas y la negligencia. Lo que Gusman no dijo, es que no planeaba evacuarlos.» — ✔ (en el cierre: Gusman)
- **cap 2 → [T08]** La energía eléctrica se pierde y los generadores de respaldo fallan en la OPP.
  cierre: «La prisión, ya en tinieblas, quedaba completamente aislada, rodeada por un diluvio que lo cambiaría todo. Sin la luz para guiar ni el aire para respirar, la estructura aguardaba su destino: una noche en la que no solo la red eléctrica, sino también sus generadores de respaldo, perecerían por completo.» — ✔ (en el cierre: eléctrica, generadores, respaldo)
- **cap 3 → [T13]** Comienza la evacuación de algunos edificios de la prisión (Templeman 1 y 2) cuando el agua alcanza el nivel del pecho en el interior.
  cierre: «El diluvio contaminado seguía su ascenso imparable, prometiendo un horror aún mayor para los miles de prisioneros abandonados. Pronto, esta marea implacable alcanzaría cotas inimaginables, transformando sus celdas en trampas mortales con el agua llegando al nivel del pecho.» — ✘ 
- **cap 4 → [D19]** Inmediatamente después de la evacuación, 517 reclusos no estaban contabilizados
  cierre: «La prisión, ahora en silencio. Pero, ¿estaban todos los prisioneros fuera?» — ✔ (en el cierre: estaban)
- **cap 5 → [D72]** Un jurado federal otorga más de $650,000 a dos turistas de Ohio
  cierre: «La deshumanización y el abandono en la Prisión Parroquial de Orleans no pasarían desapercibidos para siempre. Algunos, en busca de reparación por el trato inhumano, llevarían su lucha a los tribunales, donde un jurado federal...» — ✔ (en el cierre: federal)
- **cap 6 → [D62]** No existen registros oficiales de lo que ocurrió en la Prisión de Orleans Parish inmediatamente después del huracán Katrina
  cierre: «Casos como el de Raphael Schwarz, Arrestado por intoxicación pública, y su experiencia en la prisión, resonaron en los testimonios. Sin embargo, a pesar de estas victorias legales y las investigaciones de alto nivel, una verdad inquietante persistía sobre el caos de esos días: la ausencia completa de documentación.» — ✔ (en el cierre: Prisión)

## Violaciones que el narrador aceptó tras 3 intentos (v2)

- cap 3: 4.55 adjetivos/100 palabras (máximo 3.6): sacá adjetivos — impenetrable, sofocante, atrapados, oscuro, insostenibles, ineludible, evidente, desesperada, imparab · más de 2 oraciones seguidas que califican sin dato: cambiá adjetivos por hechos · el cierre tiene que anticipar el dato concreto del cap 4: «Comienza la evacuación de algunos edificios de la prisión (Templeman 1 y 2) cuando el agua» (nombralo
- cap 5: nombrá a Ronnie L. Morgan, Jr. por nombre y apellido y con su cargo (Recluso, demandante) la primera vez · nombrá a Cornel Hubert por nombre y apellido y con su cargo (Alcaide del Elayn Hunt Correctional Center) la primera vez · 5.24 adjetivos/100 palabras (máximo 3.6): sacá adjetivos — escalofriante, minucioso, profunda, macabra, narrativa, atrapadas, vulnerable, motivos, hizo, cruda, 
- cap 7: densidad 1.88 datos/100 palabras (mínimo 2.0): más datos literales del pool, menos descripción

## Umbrales del juez

- v1: {'densidad': False, 'repeticion': False, 'adjetivacion': False, 'antagonista': False, 'cliffhanger': None}
- v2: {'densidad': True, 'repeticion': True, 'adjetivacion': True, 'antagonista': True, 'cliffhanger': False}
