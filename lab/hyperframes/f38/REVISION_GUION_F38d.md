# REVISIÓN DEL GUION DE PANTALLA — Vajont F38d (analista, 2026-10-27)

Base: `lab/hyperframes/f38/b4/GUION_PANTALLA.md` (md5 `0af5b1dc…`, igual a `output/f8s3-vajont-f30/`) y papel `b4/01e_pantalla.md` (md5 `82c04a3a…`).

Data bruta cruzada:
- pool `00_pool_v3.json`;
- voz `01b_narration.json` (7 caps);
- escaleta `01a_escaleta.json`;
- planes `gfx_plan_chNN.resolved.json`;
- código `pantalla_colocar.instantes`/`repartir`;
- contrato F34 (`f34/REVISION_GUION.md`) y DECISIONES 16:41.

## 1. Semáforo y conteos
| cap | | qué falla |
|---|---|---|
| ch01 | 🟡 | gancho D84 ≠ D195 (decisión de Omar 16:41); la pregunta de cierre va desfasada de la voz |
| ch02 | 🔴 | D47 sale sobre la oración de Edoardo Semenza, no sobre la de Müller (rompe (b)); CALMA sin colocar (forma, F31b) |
| ch03 | 🟢 | — |
| ch04 | 🔴 | T50 «COTA ALCANZADA 720 m» contradice la voz de ch05 (junio: 700 m) y al propio pool (D160/T51: 700 m; D161: 710 m) |
| ch05 | 🟡 | reloj 9 OCT perdido (bug del reloj); Q51 movida de [17] a [18] sin motivo declarado; Q50 con autor en dos idiomas |
| ch06 | 🟡 | D192 fuera: ninguna oración la cuenta (ver §3, B5) |
| ch07 | 🔴 | la pregunta de cierre (último texto del video) es una frase que la voz no dice: 190 caracteres, 12,9 s |

Conteos:
- 13 fichas, una por beat (1 recorte + 3 citas + 9 normales);
- 8 sellos, más 1 cortado (CALMA);
- 3 relojes, más 1 cortado (9 OCT ch05);
- 6 punches (ch01 es Veo, una sola escena, sin corte donde ponerlo);
- 7 preguntas de cierre;
- 1 tarjeta;
- `a_pantalla` 4/5.

## 2. DEBERÍA por línea
| # | mm:ss · cap | hoy | ✗ regla | DEBERÍA | fuente |
|---|---|---|---|---|---|
| 1 | 01:04.2 · ch01 b1 | ficha D84 «PRESIÓN DE LA OLA DE AIRE · dos bombas de Hiroshima» | contra la decisión de Omar 16:41 (gancho = D195) | ficha **«LONGARONE · 1.269 de 1.328 habitantes murieron»**, ancla [2] «Longarone» (≈00:19), escena 0 (Veo), 3,3 s; D84 sale. Pasa (c): la voz nunca dice cuántos murieron en Longarone | D195 (F20, literal «1,269 of 1,328»). **Omar confirma o cambia** |
| 2 | 03:11.2 · ch02 b3 | ficha D47 en [12], sobre «…Edoardo Semenza…» | (b): el dato es de Müller ([11]) y Fase 2 lo pasó a la oración siguiente | misma ficha a las **03:04.2** (inicio de la escena 8, cap 79,6 s, **dentro de [11]**), 4,7 s → termina en 84,3, antes del corte de 86,6. Coincide con el punch del pico (transición, no bloque) | D47; bug B1 |
| 3 | 07:59.4 · ch04 b7 | ficha T50 «COTA ALCANZADA · 720 metros» | fiel a la fuente, pero contradice el video: la voz de ch05 dice «junio de 1963, setecientos metros» y la de ch04 dice «autorizada setecientos quince»; el pool tiene D160/T51 (700 m en junio) y D161 (710 m). 720 no se alcanzó | ficha **«ENEL, LA COMPRADORA · creada por ley en diciembre de 1962»** (54 car., 3,6 s), misma ancla [15] «ENEL», escena 9. El pico no queda vacío (17:58) | D105 (F15, literal). T50 → research (§4) |
| 4 | 08:51.3 · ch05 b8 | cita Q50, kicker «DOCUMENTO OFICIAL», autor «Administración del comune di Erto e Casso» | kicker genérico; autor en dos idiomas | kicker **«CARTA DEL MUNICIPIO»**, autor **«Municipio de Erto y Casso»**: 19 + 21 + 25 + 5 = 70 ≤ 90 | Q50 (`autor_en_documento`: «l'amministrazione del comune di Erto e Casso»); F34 #8 |
| 5 | 09:57.0 · ch05 b8 | ✂ reloj «9 OCT» («quedaría menos de 2 s») | información > clima: es la fecha del desastre y la voz la dice | reloj **«9 OCT · 1963»** a las **09:58.9** (inicio de la escena 10, cap 89,4 s, dentro de la oración «El nueve de octubre a la mañana…»), con su duración normal | voz ch05; bug B2 |
| 6 | 10:37.7 · ch05 b9 | cita Q51 movida de 115,46 s ([17] «posdata») a 128,2 s ([18] «De veinte a treinta centímetros»), sin falla declarada | los intentos 1 (115,46 y 121,86 s) tenían lectura y no hay motivo escrito | Q51 en **[17]** a las **10:24.9** (cap 115,46 s, escena 12: 113,3–128,2), 4,3 s, donde la puso el papel | Q51; bug B3 |
| 7 | 13:32.5 · ch06 b11 | D192 no está | — | **nada** en Vajont: ninguna oración de ch06 habla de la presa ni de sus técnicos (b), y [24] «Entre los muertos» ya tiene D128. Pantalla vacía = correcta. Omar puede pedirla por `--plan-edit` (gusto) | D192; B5 para otros temas |
| 8 | 17:22.4 · ch07 b13 | pregunta de cierre «La sentencia dice… decidió que Micaela siguiera durmiendo.» (190 car., 12,9 s) | es el `cierre` de la escaleta, que el guionista reescribió. La voz dice «…decidió que Longarone no debía saber.» + «¿Quién decidió que Micaela siguiera durmiendo?» | **«¿Quién decidió que Micaela siguiera durmiendo?»** (45 car., 3,0 s), misma ancla | voz ch07; bug B4 |
| 9 | 01:37.9 · ch01 b1 | pregunta de cierre «El dique no cedió… vino por encima de él.» mientras la voz dice [16] «Y para entender…» | va desfasada: muestra [14]+[15] cuando la voz ya pasó a [16] | ancla en el inicio de **[14]** «Pero el dique no cedió esa noche.» | voz ch01; bug B4 |

Pasan las tres reglas (sin cambios):
- tarjeta 00:00;
- reloj 01:16;
- recorte D117;
- AMENAZA, T15, AVISO, SILENCIO, D49;
- reloj 4 NOV, T39, ALARMA;
- D86, PÁNICO, D128;
- Q14, RABIA, reloj 20 FEB, D245, MEMORIA.

Además:
- música ✓, costuras ✓, lectura ✓;
- inicio de voz ✗ en ch07 (−32,6 contra −30,5 dB, previo F32, no frena).

## 3. Bugs de reglas (código, generales, papel intacto)
- **B1 — `instantes` no prueba un corte que cae antes de la palabra ancla.** Solo prueba el inicio de la escena siguiente después del ancla. Ejemplo: D47 en ch02. El inicio de la oración [11] queda a 0,1 s del corte, el ancla a 1,9 s del corte, y la escena 8 (79,6 s), que está dentro de [11], nunca se prueba. Entonces salta a [12], que cuenta otra cosa.
  - Arreglo: el intento 2 prueba **todo inicio de escena dentro de la oración ancla**, antes o después del ancla, antes de pasar a la oración siguiente.
  - Simulado: D47 entra a 79,6–84,3 ✓.
- **B2 — El reloj no mueve su fin con el intento.** `end` sale del instante original, así que todo intento más tarde tiene menos de 2 s.
  - Ejemplo: 9 OCT en ch05. El intento «inicio de la escena 10» (89,43 s) falla, con 20 s de escena libres.
  - Arreglo: el fin se mueve con el intento (misma duración, cortada en su nuevo corte).
  - Simulado: 89,4 s en adelante ✓, sin choques hasta Q51.
- **B3 — Un movido sin motivo.** Q51 tenía dos intentos de su oración con lectura y quedó en el 3, con `fallas` vacío.
  - CC encuentra por qué. Si es bug, Q51 vuelve a [17]. En cualquier caso, todo movido declara qué falló en cada intento anterior.
- **B4 — La pregunta de cierre sale de la escaleta, no de la voz.** Si el guionista reescribe el cierre, la pantalla muestra una frase que nadie dice (ch07), o la ancla en una oración que no es la suya (ch01).
  - Arreglo: el texto = las oraciones de la voz que alinean con el `cierre`. Si difieren, gana la voz. El ancla es la primera de ellas.
- **B5 — Contrato de m01e contra DECISIONES 14:22** («2 `a_pantalla` en el mismo beat si van en escenas distintas»; desde 17:58, «nunca al mismo tiempo»). El prompt y el código dicen «como máximo una ficha por beat» sin la excepción. En Vajont no cambia nada (#7), pero en otro tema corta un `a_pantalla` con ancla.
  - **Toca el prompt → regenera el papel.** Va con d1, antes de Kyshtym, no antes de la compuerta de Vajont.

## 4. Research de Fase 1 (junto con c9, formato de cifras)
- **Cifras del pool que se contradicen y nadie marca:** T50 (720 m, mayo de 1963) contra D160/T51 (700 m, junio) y D161 (710 m). El autor no tiene forma de saberlo.
- **Autor de cita a medio traducir:** Q50.

## 5. Veredicto
**Render: no.**
1. **Arreglos de código** (tanda chica de CC, solo Fase 2, sin tocar el prompt ni el papel): B1, B2, B3, B4 → `--plan-only` → esta tabla se vuelve a medir. Se esperan #2, #5, #6, #8 y #9 resueltos solos.
2. **Ediciones de contenido** (`--plan-edit`, en la compuerta): #3 (T50 → D105) y #4 (kicker y autor de Q50).
3. **Decide Omar:**
   - #1 gancho: D195 (su decisión de las 16:41) o D84;
   - #7 D192: fuera (voto del analista) o a mano;
   - sellos: el autor puso INMINENTE en ch01 y nada en ch05; ALARMA en ch04; PÁNICO en ch06, sobre «una fuerza la agarra»; RABIA de más en ch07; CALMA se cae por la forma. Contra lo del 16:41 (PÁNICO, AMENAZA, INMINENTE, COLAPSO + SILENCIO), el analista vota quedarse con los del autor: cumplen la regla del sello;
   - d1 + B5 antes de Kyshtym (cambian el prompt).

## 6. De quién es cada falla
- B1 y B2: la escalera de F37 §B.1, especificada por el analista sin el caso «corte antes del ancla» ni el fin del reloj. **Analista.**
- B3: sin causa conocida. **CC la declara.**
- B4: viene de F32. Ningún chequeo compara la pregunta de cierre con la voz final. **Analista.**
- B5: el handoff F36 C no pasó la excepción del 14:22 a m01e. **Analista.**
- T50: research (pool contradictorio) más la elección del autor. Ningún chequeo lo puede ver.
