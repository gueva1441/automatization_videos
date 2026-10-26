# F34 — simulación en seco de las reglas, ANTES del código (/tanda paso 5)

Agente `simulador` (solo lectura, sin API) contra `lab/hyperframes/f32/GUION_PANTALLA.json`, las crudas
`rotulista_chNN.raw.json` y los planes `gfx_plan_chNN.resolved.json` de `output/f8s3-vajont-f30/_fase2b_work/`. Su
respuesta, íntegra:

---

**Base de F32.** El modelo propuso 12 bloques (ch01 no propuso ninguno). Los que cortó el rotulista:

| pool_id | cap | regla | motivo |
|---|---|---|---|
| D117 | ch02 | candado | `1943` |
| D237 | ch02 | lectura | 116 caracteres piden 7.7 s y hay 6.5 s |
| D49 | ch03 | candado | `2005` y `Vajont` |
| T39 | ch04 | forma | no cabe en la ficha |
| D68 | ch04 | cantidad | beat pico |
| Q50 | ch05 | lectura | 179 caracteres piden 11.9 s y hay 10.9 s |
| D192 | ch06 | lectura | 143 caracteres piden 9.5 s y hay 9.5 s |
| T85 | ch07 | spoiler | `Vajont` |

Quedaron en pantalla 2 textos: D128 en ch06 y D245 en ch07.

Para el handoff: el candado y el spoiler que corrió la cadena en F32 son los del guion, no los de las crudas. En las crudas el orden de las reglas cambia porque no pasan las escenas. Por eso T85 figura como `lectura` en la cruda y como `spoiler` en el guion.

## 1. A.2.1 Candado: un número o nombre de la oración ancla cuenta como presente

| propuestos (candado) | cortados hoy | dejan de caer | quedan cortados por candado |
|---|---|---|---|
| 12 | 2 | 1 (D117) | 1 (D49) |

Ejemplos reales:
- **D117, ch02 s2, 0:19.2.** Texto de F32: «Acta de aprobación, 1943 · Solo 13 de 34…». `1943` está dicho en la ancla («mil novecientos cuarenta y tres»), así que deja de caer por candado. Pero con ese texto largo cae igual por lectura: 119 caracteres piden 7.9 s y hay 3.4 s hasta el corte en 24.6 s. Solo pasa con el texto corto de §1 («ACTA DEL CONSEJO SUPERIOR · 13 de 34 representantes presentes», 58 caracteres, 3.9 s). Y pasa porque arranca en la escena siguiente (24.6 s).
- **D49, ch03 s17.** Sigue cayendo con `['2005','Vajont']`, porque ninguno está en la ancla. Lo salva el reemplazo A.1 #2 («no pongas la fuente»), no A.2.1. Con «ANCHO DE LA FISURA · Más de 1 metro» pasa limpio.
- **A.2.1 hace falta para dos textos de §1 que hoy caerían por candado:**
  - T39 «ALERTA DE MERLIN, **1961**»: el año está solo en la voz («mil novecientos sesenta y uno», ch04 s6).
  - T85 «REMISIÓN A JUICIO, **1968**»: el año está solo en la voz (ch07 s11).
  - Sin A.2.1 caen con `['1961']` y `['1968']`. Con A.2.1 pasan.
- **Riesgo en Q50.** Si el modelo escribe la etiqueta «Carta del municipio de Erto y Casso **a SADE**» (como en §1), cae por candado con `['SADE']`. SADE no está en el texto fuente de Q50 ni en la ancla (ch05 s2). El `por_que` sí dice «a SADE», pero el candado no mira el `por_que`. La etiqueta de F32 («…, 2023», de `short_source`) sí pasa.

## 2. A.2.2 No dicho: números en letras a dígitos antes de comparar

| propuestos | caerían como «nuevo» → ahora «dicho» | notas |
|---|---|---|
| 12 | **0** | ya está hecho en el código |

`numeros()` y `numero_en()` de `gfx_rotulista.py` ya convierten letras a dígitos con `num_es` (`_w2n`). Medido hoy sobre el texto de D237 (ch02 s5):
- `numeros()` da `['400']`.
- El `no_dicho` lo corta contra la vecina («cuatrocientos»).
- La cruda guarda exactamente eso: `regla: no_dicho ['400']`.
- En el guion de F32 D237 figura como `lectura` porque esa regla corre antes y lo corta por lectura. Nunca llega a `no_dicho`.

**Pregunta para el analista:** la premisa «D237 pasó como nuevo» no se reproduce. Antes de programar A.2.2 conviene confirmar si ya está. Un comparador solo de dígitos sí dejaría pasar a D237, pero no es el código actual.

Dato lateral: la hora «diez y treinta y nueve» se parsea como `39`, no como 22:39. Una cifra de pool «22:39» marca `39` como dicho en el video.

## 3. A.2.3 Spoiler: un nombre dicho antes en el cap o en un cap anterior no es spoiler

| propuestos | spoiler hoy | dejan de caer |
|---|---|---|
| 12 | 1 (T85) | 1 (T85) |

- **T85, ch07 s11, 1:24.7.** Texto de F32: «La sentencia se presentó contra 11 personas por el desastre del Vajont». Hoy cae con `['Vajont']`, porque la voz lo dice en una oración posterior del cap y no antes dentro de ch07.
- **Con A.2.3.** `Vajont` ya está dicho en ch02 s1, así que pasa (88 caracteres, 5.9 s, arranca en la escena siguiente).
- **No hay otros spoilers en F32.**

## 4. A.3.1 Reloj, agua y textos ganan al sello

Hay 10 sellos en pantalla hoy. Relojes cortados por sello: 2. Para los otros solapes uso el conjunto propuesto: textos de §1, relojes (director + A.3.3) y aguas (A.5).

| sello hoy | quita un reloj (comparte beat) | comparte escena con texto/agua/reloj | comparte beat con reloj/agua |
|---|---|---|---|
| ch05 «estruendos» 0:22.9, beat 8, esc 2 | **sí**, `9 OCT` a 1:27.5 (cortó `zona`) | texto Q50 (esc 2) | reloj 9 OCT |
| ch07 «grito» 0:10.9, beat 12, esc 0 | **sí**, `20 FEB` a 1:24.7 (cortó `zona`) | — | reloj 20 FEB |
| ch01 «fuerza» 0:37.4 | no | D118 y reloj (esc 0, cap de una sola escena) | reloj 9 OCT |
| ch03 «desmoronamiento» 1:45.8 | no | texto D49 (esc 11) | — |
| ch07 «ola» 2:34.3 | no | — | reloj 29 NOV 1968 (extra de A.3.3, ver punto 6) |
| ch02 vida, montaña; ch05 deslizamiento; ch06 fisura, fango | no | — | — |

- **Resumen.** Sellos que cederían: 2 por quitar un reloj, hasta 4 más según la lectura de «escena» o «beat».
- **Las dos pérdidas reales del handoff** («9 OCT» y «20 FEB») las explican exactamente esos 2 sellos.
- **Choque con lo esperado en §1.** Esa tabla pone ch01 sello + reloj + tarjeta, ch05 INMINENTE + reloj 9 OCT, ch07 MEMORIA + reloj 20 FEB. Si la regla «una animación por beat» (reloj/agua/sello) sigue vigente, el sello de esos beats cede y §1 no se cumple. Para que coincida, la unidad tiene que pasar de beat a escena u oración.

## 5. A.3.2 ch01, una cosa por oración

ch01 tiene una sola escena (esc 0, 0–101.6 s). Bloques candidatos:

| bloque | oración | tiempo | conflicto |
|---|---|---|---|
| title card «Cama en la oscuridad» | s0 (0.12–6.34) | 0.0–3.0 | **choca con la tarjeta fecha-hora**: «en 0:00», `title_dur` 3.0, mismo estilo, misma oración s0 |
| texto D118 | s1 | arranca 7.4, dura hasta 15.3 | — |
| reloj 9 OCT 1963 | s13 (73.5–77.9) | 73.5, dura ~4.4 | — |
| sello (4 candidatos hoy) | s1 «oscuridad» 9.8, s6 «fuerza» 37.4, s10 «ruido» 63.5, s16 «ola» 86.0 | 2.5 s | «oscuridad» está en s1 junto a D118: choca. PÁNICO tendría que ir en s6, s10 o s16. «Coletti» no es un candidato de hoy |
| pregunta de cierre | tras s16 | 94.9–100.6 | — |

- **Resultado.** Hay 1 conflicto seguro: title card y tarjeta en s0, y las dos duran 3.0 s sobre el 0:00. Hay otro condicional: el sello «oscuridad» de s1 contra D118.
- **No se resuelve con el guion.** O la tarjeta va antes de la primera imagen y desplaza todo 3 s (afecta mezcla y música), o no puede convivir con el title card en 0–3.0.

## 6. A.3.3 Reloj cuando la voz dice día + mes + año

Detecté 4 oraciones con fecha completa en 7 caps:

| cap | oración | segundo | fecha | beat |
|---|---|---|---|---|
| ch01 | s13 «Longarone, Italia, nueve de octubre…» | 1:13.5 | 9 OCT 1963 | 1 |
| ch04 | s0 «El cuatro de noviembre de mil novecientos sesenta…» | 0:00.1 | 4 NOV 1960 | 6 |
| ch07 | s11 «el veinte de febrero de mil novecientos sesenta y ocho» | 1:24.7 | 20 FEB 1968 | 12 |
| ch07 | s14 «El juicio empezó el veintinueve de noviembre de mil novecientos sesenta y ocho» | 1:41.6 | 29 NOV 1968 | 13 |

Fechas con día y mes pero sin año (no cuentan): ch03 s19 «cuatro de noviembre», ch05 s1 «veintiséis de septiembre», ch05 s2 «dos de octubre», ch05 s13 «El nueve de octubre a la mañana» (1:27.5).

| propuestos | quedan |
|---|---|
| 4 por voz + 1 del director (ch05 9 OCT) | 5, contra 4 esperados en §1 |

No va a coincidir en:
- **ch05 «9 OCT».** La voz no dice el año, así que A.3.3 no lo propone. Depende de que el director lo pida (hoy lo cortó el sello, ver punto 4). Y el reloj de F32 dice «9 OCT» sin año.
- **ch07 29 NOV 1968.** Es un reloj extra que §1 no espera. Va en el beat 13, distinto del beat 12 de 20 FEB, así que la regla de beat no lo frena.
- **ch04 4 NOV 1960.** A.3.3 lo ancla en s0 (0:00.1), dentro de la escena del title card (0–10.6). El del director de F32 está en 10.6 s (esc 1) y es el que pasó.

## 7. A.4 Sellos de clima: las 10 palabras en la voz

El filtro es determinista, sin Gemini. Candidatos a sello de hoy: 52 momentos (10 en pantalla, 42 cortados).

| criterio | momentos con alguna de las 10 en voz anterior, ancla o siguiente |
|---|---|
| palabra exacta | **3 de 52** (0 de los 10 en pantalla) |
| por raíz de 5 letras | 5 de 52 (1 de los 10 en pantalla) |

- ch04 0:45.3 «amenaza»: AMENAZA (cortado hoy).
- ch05 2:31.2 «alarma»: ALARMA (cortado hoy).
- ch06 1:37.8 «fuerza»: AVISO (cortado hoy).
- Por raíz, además: ch05 «sacudidas» 0:21.8 y «estruendos» 0:23.0 (esta sí en pantalla): AVISO por «avisos». Con A.4 ese sello no podría ser AVISO.
- **Efecto del filtro: casi nulo.** La voz de Vajont casi nunca usa las 10 palabras. El filtro corta como mucho 3 de 52 candidatos, y ninguno de los que están en pantalla.

El tope de sellos no lo pone esto. Lo pone «una animación por beat». Hay 13 beats, y en 7 hay reloj o agua propuestos (b1, b4, b6, b7, b8, b12 y b13 por 29 NOV). Quedan libres b2, b3, b5, b9, b10 y b11. Eso da 6, hasta 7 si no se acepta 29 NOV, contra 8 de §1.

## 8. A.5 Agua desde la voz

Lectura literal: «<n> metros» (n en dígitos o letras), o `cota`/`nivel`/`ola` con número en la oración o la anterior.

| cap | oración | segundo | etiqueta propuesta | valor | beat |
|---|---|---|---|---|---|
| ch03 | s1 «levantó una ola de veinte metros» | 0:02.9 | OLA | 20 m | 4 |
| ch03 | s7 «Una ola de veinte metros» | 0:47.9 | OLA | 20 m | 4 |
| ch04 | s0 «seiscientos cincuenta metros sobre el nivel del mar» | 0:00.1 | NIVEL DEL EMBALSE | 650 m | 6 |
| ch04 | s12 «setecientos metros sobre el nivel del mar» | 1:15.2 | NIVEL DEL EMBALSE | 700 m | 7 |
| ch04 | s13 «La cota autorizada fue de setecientos quince» | 1:21.1 | COTA AUTORIZADA | 715 | 7 |
| ch05 | s0 «el agua llegó a los setecientos metros» | 0:03.1 | NIVEL DEL EMBALSE | 700 m | 8 |

Falsos positivos de la regla literal (5):
- ch01 s16: «ola» más «veinte años».
- ch04 s2: «setecientos mil metros cúbicos» (volumen, no altura).
- ch04 s15: «nivel» más año.
- ch05 s1: «nivel de seguridad» más fechas.
- ch06 s16: «La ola la arrastra cuatrocientos metros» (distancia, no nivel).

Total literal: 11 oraciones, 6 válidas.

| propuestos válidos | por beat | contra §1 |
|---|---|---|
| 6 oraciones | 4 beats: ch03 b4, ch04 b6, ch04 b7, ch05 b8 | §1 espera 2 |

No va a coincidir en:
- **ch03.** La primera oración candidata (0:02.9) cae dentro del title card (0–3.0).
- **ch04.** En el beat 7 la regla elige s12 (700 m) antes que s13 (715), y §1 espera 715 «COTA AUTORIZADA». Además el beat 6 compite con el reloj 4 NOV (s0 trae los dos).
- **ch05 s0.** 700 m es un agua que §1 no espera. Compite con el reloj 9 OCT (beat 8).

## 9. A.6 Tarjeta «9 OCT 1963 · 22:39»

Sí se puede derivar, pero la hora no sale del ítem pico.
- **Fecha.** El pico de la escaleta (`data/scripts/_steps/f8s3-vajont/01a_escaleta.json`) es el beat 10, `dato_central` T57. T57 en `00_pool_v3.json` tiene `fecha: 1963-10-09` y `hora: null`.
- **Hora.** Sale de otros ítems del mismo pool:
  - `hora: "22:39"` en T66, T67, T68, T69, T70 y T71.
  - El texto «22:39» en D02, D14, D143 y Q12.
  - La explicación del pico en la escaleta (`pico.por_que`), que dice «el Toc entra al embalse a las 22:39».
- **Conflicto.** T65 (Vajont. Storia di una diga) trae `hora: "22:30"`. Es 1 contra 6, pero habría que escribirlo en la regla de certeza.
- **Voz.** La voz dice la hora en letras en ch07 s26 («diez y treinta y nueve de la noche») y «diez y media» en ch05.
- **Sin ancla única.** La regla de A.6 («beat pico + el ítem que da la hora») no tiene un ítem único. Hay que fijar el criterio: coincidencia de al menos N fuentes, o el primer ítem del pool con `hora`.

## Totales contra la tabla §1

| | esperado §1 | simulado | comentario |
|---|---|---|---|
| textos | 9 | 8 a 9 | ver abajo |
| relojes | 4 + tarjeta | 5 (sin tarjeta resuelta) | ver puntos 6 y 5 |
| aguas | 2 | 4 beats válidos | ver punto 8 |
| sellos | 8 | 6 a 7 | ver punto 7 |

Qué no va a coincidir:

1. **Textos (9).** Posibles y deterministas: D117, D49, T39, T85, D245, D128, D192. T39 y T85 dependen de A.2.1. D118 en el gancho depende solo del prompt: no está en `items` de ningún cap, y 266 no está dicho en el video. Q50 depende de que la etiqueta no lleve «SADE». ch06 tiene un problema fuerte: D128 y D192 se anclan en la misma oración (s24, «Entre los muertos está Guglielmo Celso») y caen en la misma escena 13 (126.9 s). A.1 pide «oraciones distintas» y el guion exige una cosa por escena, así que probablemente salga 1 y no 2. Eso baja el total a 8.
2. **Relojes (4 + tarjeta).** El conteo sale 5 por 29 NOV 1968 (ch07), que §1 no lista. ch05 depende del director. La tarjeta choca con el title card de ch01 en 0:00 (ver punto 5).
3. **Aguas (2).** La regla da hasta 4 beats válidos (ch03 b4, ch04 b6, ch04 b7, ch05 b8) más falsos positivos. Para quedarse en 2 hace falta «una por cap», una prioridad de `cota` sobre `nivel`, y un filtro de unidad («metros cúbicos» no es altura; «ola» no es siempre agua).
4. **Sellos (8).** El tope por beat da 6 a 7 si se mantiene «una animación por beat». Para llegar a 8 hay que pasar a una por escena u oración, porque §1 pone sello y reloj o agua en los beats de ch01, ch03, ch05 y ch07.
5. **Premisa de A.2.2.** No se reproduce, porque el código ya hace esa conversión (ver punto 2).

---

## Qué cambió en el código por esta simulación (decisiones de CC, declaradas)

- **A.2.2:** el conversor ya estaba; el arreglo es el orden (no dicho y spoiler corren antes que la lectura), así D237 cae por repetir la voz.
- **A.3.1:** el sello ya no cuenta para «una animación por beat» frente al reloj, el agua o la lupa (§A.3.1: «se mueve a otra oración del beat»); sigue siendo un sello por beat y nunca en la escena (u oración) de otra cosa. Así ch01/ch05/ch07 pueden tener reloj y sello en el mismo beat, como §1.
- **A.5:** el agua necesita palabra clave (ola de N metros · cota con número · N metros sobre el nivel / nivel … N metros), una por cap, en el orden COTA AUTORIZADA > COTA > OLA > NIVEL DEL EMBALSE > NIVEL; nunca metros cúbicos, nunca «ola … años», nunca «la ola la arrastra N metros».
- **A.6:** la hora = la de un ítem de la cronología de la fecha del pico que el `por_que` del pico dice literal (22:39 → T66); T65 «22:30» no la dice. Si nada calza, `⚠ falta fecha-hora`.
- **A.3.3:** el reloj de la voz solo cuando la cronología no da reloj en el cap (uno por cap); así ch07 queda con el de la cronología y no suma 29 NOV.
- **Tarjeta vs. title card de ch01:** queda abierto (ver F34_REPORT).
