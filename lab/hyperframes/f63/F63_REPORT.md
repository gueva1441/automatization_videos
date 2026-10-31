# F63 — ¿El papel mejora si lo escribe Opus con toda la información? + verificador de narración (solo lab, solo texto)

Handoff: `lab/hyperframes/f63/HANDOFF_F63_papel_opus.md` (md5 `d684b0fb38a42ad36919a0e211832ad6`, verificado). Rama `f11-guion-v4`, base `b15e9ba`. Topic Wittenoom `123bbb64-9fca-4395-8bf4-57d60e219ef1`. Fecha: 2026-10-31.

Runners (lab, nuevos): `etapa_a_papel.py` (Parte A) y `etapa_b_verificador.py` (Parte B; importa de A la entrada y la llamada). De `m01e_pantalla` solo se importa (`cargar`, `entrada`, `entrada_md5`, `_para_modelo`, `PANTALLA_SYSTEM`, `FORMATO_SALIDA`, `validar`, `armar`, `a_markdown`, `estilo_de`, `primer_json`, `_int`); `llamar` y `generar` no se llaman. El modelo se llama con `hx._post(body)` directo, body como `m01e_pantalla.llamar.autor` (`model`, `max_tokens = hx.MAX_TOKENS`, `system`, `messages`, `output_config.effort`); costo `hx.cost_of`; registro `hx._track(model, usage, "lab_f63_<brazo>_<n>")` sin `cost_tracker.start_video` (va a `session_overhead`, no a `data/cost_history.json`). A y B corrieron a la vez: 8 + 14 = 22 llamadas en paralelo (dos procesos, un hilo por llamada).

## Chequeos que paran (todos OK)

| chequeo | esperado | medido |
|---|---|---|
| md5 del handoff | d684b0fb38a42ad36919a0e211832ad6 | d684b0fb38a42ad36919a0e211832ad6 |
| `entrada_md5` de hoy (= `01e_pantalla.raw.json`) | a2b19d01f425b58b959b455d2e691c89 | a2b19d01f425b58b959b455d2e691c89 |
| md5 de `PANTALLA_SYSTEM` (S, O1) | 7d2ccdd2… (el que mida CC) | 7d2ccdd28055d6e621d1d251a0fe8bb7 |
| md5 del SYSTEM O2/O3 (oración 2 reemplazada, A.2) | 85d094bed6090b14d1802ca97433d982 | 85d094bed6090b14d1802ca97433d982 |
| md5 del SYSTEM de B | ce31cc515a077d74da72479e9693296e | ce31cc515a077d74da72479e9693296e |
| md5 de `01b_narracion_v3.json` | c7badfbe260f5eb24a47e780b40406b5 | c7badfbe260f5eb24a47e780b40406b5 |

`prompt_md5()` de m01e (SYSTEM + formatos) sigue en `3b98aef1d8595124967ac7a85b75bab7`; el 7d2ccdd2… es el md5 del SYSTEM solo, como pide la tabla del handoff. Velocidad del narrador: 0.34 s/palabra (mediana de 347 oraciones de 16 caps del narrador N9Z5MLTIaHFLflaLtbDi).

## Parte A — cuatro brazos × 2 corridas

### Entradas

- Entrada de hoy (S, O1): archivo de 292 ítems de los 362 del pool; USER 105,922 caracteres (md5 `a2b19d01f425b58b959b455d2e691c89`).
- Entrada completa (O2, O3; A.1, por código en el runner): archivo de 362 ítems (todo el pool: `_tipo` reemplazado en el proceso por `_kind` → D/T/Q/P/L y `entrada(...)` llamada igual, así `beats_que_lo_cuentan`, `a_pantalla`, `autor`, `rol` y `testimonio` salen como hoy; L con `texto` «nombre — rol»; todo ítem con `contexto_fuente` = `cita_literal`, o la del primer elemento de `evidencia` —los 362 tienen `cita_literal`—), beats con `emocion`, `imagen_sensorial`, `pregunta_abierta`, `paga` de `01a_escaleta.json`, más `escaleta_video` (`promesa_gancho`, `loops`, `recuerda_loop`, `pico`, `humano`, `antagonista`, `cierre_humano`) y `disputas` (`versiones` ×2 y `contradicciones` ×5 de `ficha_caso.json`). USER 199,691 caracteres (md5 `018f9cc1b939e2afdcfad5eb5ebcc36f`). Los 7 ids que hoy faltan (D85, D03, D129, D20, D10, D70, D34) están en el archivo completo (verificado en seco). Muestra: `entrada_completa_muestra.json`.
- Validación «solo anotar» (A.3): `ent["_pool"] = carga["pool"]`; `validar(resp, ent, {}, final=True)` y `armar(ent, res)` con un `res` armado por el runner (un intento, sin tope, sin vueltas). Cada ficha que propuso el modelo queda en el `.md` debajo de su beat con «pasa» o «cortaría: <primera regla del código> — <motivo>».

### Tabla A (una fila por brazo y corrida)

| brazo · corrida | modelo · effort · entrada | JSON | fichas propuestas | pasan | cortadas (primera regla) | gancho con ficha | picos con ficha | a_pantalla cubiertos (de 6) | ids de la escaleta usados | sellos | relojes | tokens in / out | US$ | seg |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S · 1 | sonnet-5-5 · medium · hoy | sí | 12 | 6 | candado 1·fecha_relato 1·no_dicho 2·spoiler 2 | no | 3/7 | 0/6 (—) | 1 (D82); fuera de la escaleta: D102, D115, D122, D44, T86 | 7 | 3 | 51365 / 19676 | 0.2995 | 132.5 |
| S · 2 | sonnet-5-5 · medium · hoy | sí | 13 | 9 | candado 1·fecha_relato 1·no_dicho 1·spoiler 1 | no | 6/7 | 0/6 (—) | 6 (D82, D83, Q19, Q25, Q35, T80); fuera de la escaleta: D102, D135, T86 | 9 | 3 | 51365 / 19075 | 0.2935 | 135.2 |
| O1 · 1 | opus-5-5 · medium · hoy | sí | 13 | 8 | caben 2·contradice 1·fecha_relato 1·spoiler 1 | no | 4/7 | 0/6 (—) | 2 (D82, D83); fuera de la escaleta: D102, D115, D44, D58, D69, Q22 | 8 | 3 | 51365 / 16034 | 0.5261 | 138.6 |
| O1 · 2 | opus-5-5 · medium · hoy | sí | 13 | 8 | fecha_relato 3·spoiler 2 | D26 | 5/7 | 0/6 (—) | 3 (D82, Q19, T80); fuera de la escaleta: D102, D115, D26, D44, D68 | 9 | 3 | 51365 / 16637 | 0.5382 | 149.2 |
| O2 · 1 | opus-5-5 · medium · completa | sí | 13 | 10 | fecha_relato 1·no_dicho 2 | no | 5/7 | 1/6 (D23) | 5 (D02, D23, Q19, Q25, T80); fuera de la escaleta: D102, D115, D44, D68, Q22 | 8 | 3 | 88647 / 19220 | 0.7390 | 165.9 |
| O2 · 2 | opus-5-5 · medium · completa | sí | 13 | 8 | candado 1·fecha_relato 2·no_dicho 1·spoiler 1 | no | 4/7 | 0/6 (—) | 4 (D02, D83, Q19, T80); fuera de la escaleta: D102, D115, D44, Q22 | 8 | 3 | 88647 / 17292 | 0.7004 | 154.6 |
| O3 · 1 | opus-5-5 · high · completa | sí | 13 | 8 | fecha_relato 2·no_dicho 1·spoiler 2 | no | 5/7 | 0/6 (—) | 3 (D02, Q19, T80); fuera de la escaleta: D102, D115, D35, D44, D69 | 8 | 3 | 88647 / 28436 | 0.9233 | 246.9 |
| O3 · 2 | opus-5-5 · high · completa | sí | 13 | 9 | candado 2·fecha_relato 1·spoiler 1 | D80 | 7/7 | 0/6 (—) | 4 (D83, Q19, Q27, T80); fuera de la escaleta: D35, D44, D68, D80, Q22 | 8 | 3 | 88647 / 26121 | 0.8770 | 228.1 |

Coincidencia entre corrida 1 y 2 (beats de 13 con el mismo `pool_id` de ficha que pasa en las dos, ÷ 13):

| brazo | beats con el mismo id | valor | beats sin ficha en las dos |
|---|---|---|---|
| S | 3/13 (ch03 b4, ch04 b8, ch07 b13) | 0.231 | 3 |
| O1 | 4/13 (ch03 b4, ch03 b5, ch03 b6, ch04 b8) | 0.308 | 3 |
| O2 | 7/13 (ch03 b4, ch03 b5, ch03 b6, ch04 b7, ch04 b8, ch06 b11, ch06 b12) | 0.538 | 2 |
| O3 | 4/13 (ch03 b5, ch04 b7, ch05 b10, ch06 b12) | 0.308 | 2 |

Fichas que pasan, por beat:

| brazo · corrida | b1 | b2 | b3 | b4 | b5 | b6 | b7 | b8 | b9 | b10 | b11 | b12 | b13 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| S · 1 | — | — | D122 | D82 | D44 | D115 | — | D102 | — | — | — | — | T86 |
| S · 2 | — | Q25 | D83 | D82 | D135 | — | Q19 | D102 | — | Q35 | — | T80 | T86 |
| O1 · 1 | — | — | D83 | D82 | D44 | D115 | — | D102 | — | — | Q22 | D58 | D69 |
| O1 · 2 | D26 | — | — | D82 | D44 | D115 | Q19 | D102 | — | — | — | T80 | D68 |
| O2 · 1 | — | Q25 | — | D02 | D44 | D115 | Q19 | D102 | — | D23 | Q22 | T80 | D68 |
| O2 · 2 | — | — | D83 | D02 | D44 | D115 | Q19 | D102 | — | — | Q22 | T80 | — |
| O3 · 1 | — | — | — | D02 | D44 | D115 | Q19 | D102 | — | D35 | — | T80 | D69 |
| O3 · 2 | D80 | — | D83 | Q27 | D44 | — | Q19 | — | — | D35 | Q22 | T80 | D68 |

Costo A: US$ 4.8971 · 249.3 s de pared (las 8 a la vez).

Papeles: `a/<brazo>_<n>.md` (encabezado con el md5 del SYSTEM del brazo en lugar de `prompt_md5()`; bajo cada beat, las fichas propuestas con «pasa» / «cortaría»), `a/<brazo>_<n>.raw.json` (body enviado, intentos con texto y usage, respuesta, validación, tokens, US$, segundos). Copia a ciegas: `a/ciego/papel_01..08.md` (sin la línea del modelo/md5 ni la de tokens/tope; orden al azar, semilla 63); clave en `a/clave_ciego.json`.

Log de llamadas (`a/etapa_a.log`):

- lab_f63_S_1 intento 1: in 51365 · out 19676 · US$ 0.2995 · 132.5 s · JSON · stop end_turn
- lab_f63_S_2 intento 1: in 51365 · out 19075 · US$ 0.2935 · 135.2 s · JSON · stop end_turn
- lab_f63_O1_1 intento 1: in 51365 · out 16034 · US$ 0.5261 · 138.6 s · JSON · stop end_turn
- lab_f63_O1_2 intento 1: in 51365 · out 16637 · US$ 0.5382 · 149.2 s · JSON · stop end_turn
- lab_f63_O2_2 intento 1: in 88647 · out 17292 · US$ 0.7004 · 154.6 s · JSON · stop end_turn
- lab_f63_O2_1 intento 1: in 88647 · out 19220 · US$ 0.7390 · 165.9 s · JSON · stop end_turn
- lab_f63_O3_2 intento 1: in 88647 · out 26121 · US$ 0.8770 · 228.1 s · JSON · stop end_turn
- lab_f63_O3_1 intento 1: in 88647 · out 28436 · US$ 0.9233 · 246.9 s · JSON · stop end_turn

## Parte B — verificador de narración (Opus 5.5 medium, 7 caps × 2 corridas)

Archivo de B: 362 ítems con `id`, `texto`, `fecha`, `fuente`, `contexto_fuente`; `disputas` como en A.1.4; oraciones e `idx` los de `entrada(...)["caps"]`. SYSTEM literal del handoff (md5 arriba). Salida: `b/verificador_<cap>_<n>.json`.

### Tabla B

| cap · corrida | JSON | afirmaciones | respaldadas | contradice | sin_respaldo | otros estados | tokens in / out | US$ | seg |
|---|---|---|---|---|---|---|---|---|---|
| ch01 · 1 | sí | 18 | 13 | 2 | 3 | — | 65908 / 3400 | 0.3316 | 30.3 |
| ch01 · 2 | sí | 16 | 12 | 2 | 2 | — | 65908 / 2985 | 0.3233 | 27.2 |
| ch02 · 1 | sí | 26 | 24 | 0 | 2 | — | 66158 / 3694 | 0.3385 | 29.9 |
| ch02 · 2 | sí | 26 | 24 | 0 | 2 | — | 66158 / 3304 | 0.3307 | 26.3 |
| ch03 · 1 | sí | 35 | 30 | 1 | 4 | — | 67080 / 7069 | 0.4097 | 57.5 |
| ch03 · 2 | sí | 42 | 35 | 2 | 5 | — | 67080 / 7089 | 0.4101 | 57.8 |
| ch04 · 1 | sí | 27 | 19 | 1 | 7 | — | 66188 / 4329 | 0.3513 | 39.1 |
| ch04 · 2 | sí | 28 | 18 | 1 | 9 | — | 66188 / 4069 | 0.3461 | 33.7 |
| ch05 · 1 | sí | 31 | 30 | 0 | 1 | — | 66450 / 5995 | 0.3857 | 50.7 |
| ch05 · 2 | sí | 30 | 27 | 0 | 3 | — | 66450 / 4909 | 0.3640 | 40.4 |
| ch06 · 1 | sí | 24 | 19 | 1 | 4 | — | 66379 / 3858 | 0.3427 | 31.4 |
| ch06 · 2 | sí | 25 | 20 | 1 | 4 | — | 66379 / 4684 | 0.3592 | 38.2 |
| ch07 · 1 | sí | 21 | 19 | 1 | 1 | — | 66136 / 3394 | 0.3324 | 30.3 |
| ch07 · 2 | sí | 22 | 20 | 1 | 1 | — | 66136 / 3564 | 0.3358 | 31.1 |
| **total corrida 1** | | 182 | 154 | 6 | 22 | | | 2.4920 | |
| **total corrida 2** | | 189 | 156 | 7 | 26 | | | 2.4693 | |

Costo B: US$ 4.9612 · 60.0 s de pared (las 14 a la vez).

### B.1 Contrato, fila por fila

**ch01 [1]** (idx real 1) «Ese pie va a cerrar; lo que respira mientras espera que cierre va a tardar casi treinta años en matarlo, y lo va a alcanzar a miles de kilómetros de aquí.» — cuenta como encontrada: contradice D85 («no se cerraba»)

- corrida 1: **contradice** ['D85'] — «La herida del pie llegó a cerrar» · fragmento: «Se le cayó un trozo de amianto en el pie y, extrañamente, fue una herida que no se cerraba nunca.»
- corrida 1: **respaldada** ['T64', 'D89', 'D87'] — «Lo que respiró en Wittenoom lo mató casi treinta años después»
- corrida 1: **sin_respaldo** [] — «La enfermedad lo alcanzó a miles de kilómetros de Wittenoom»
- corrida 2: **contradice** ['D85'] — «La herida del pie llegó a cerrar» · fragmento: «Se le cayó un trozo de amianto en el pie y, extrañamente, fue una herida que no se cerraba nunca.»
- corrida 2: **respaldada** ['D87', 'T64', 'D89'] — «Lo que respiró en Wittenoom tardó casi treinta años en matarlo»
- corrida 2: **sin_respaldo** [] — «Murió a miles de kilómetros de Wittenoom»

**ch01 [2]** (idx real 2) «La foto es en blanco y negro.» — cuenta como encontrada: contradice Q25 (contexto_fuente «sepia family photos») o sin_respaldo

- corrida 1: **sin_respaldo** [] — «La foto es en blanco y negro»
- corrida 2: **sin_respaldo** [] — «La foto es en blanco y negro»

**ch06 [10]** (idx real 10) «Hacia junio de 2007, según otras referencias en 2006, Wittenoom fue abolido oficialmente.» — cuenta como encontrada: respaldada con D31 o D30 en ids

- corrida 1: **respaldada** ['T80', 'D31', 'T71', 'D30'] — «Wittenoom fue abolido oficialmente hacia junio de 2007; según otras referencias, en 2006.»
- corrida 2: **respaldada** ['D31', 'T80', 'D30', 'T71'] — «Wittenoom fue abolido oficialmente hacia junio de 2007; según otras referencias, en 2006.»

**ch06 [12]** (idx real 12) «El gobierno de Australia Occidental lo llamó «el fin de un período oscuro en la historia de nuestro Estado».» — cuenta como encontrada: contradice Q07 (fecha 2022)

- corrida 1: **contradice** ['Q07', 'T91'] — «El gobierno de Australia Occidental llamó a la abolición del pueblo «el fin de un período oscuro en la historia de nuestro Estado».» · fragmento: «Q07 (fecha 2022): "The W.A. Government declared this was “an end to a dark period in our State's history.”"; T91: "In 2022, the last remaining residents of Wittenoom town were evicted ahead of its demolition in 2023."»
- corrida 2: **contradice** ['Q07', 'T91'] — «El gobierno de Australia Occidental calificó la abolición del pueblo como «el fin de un período oscuro en la historia de nuestro Estado».» · fragmento: «Q07 (fecha 2022): "The W.A. Government declared this was “an end to a dark period in our State's history.”"; T91: "In 2022, the last remaining residents of Wittenoom town were evicted ahead of its demolition in 2023."»

### «contradice» que salen en las dos corridas (misma oración y mismos ids; o misma oración con ids distintos, anotado)

- ch01 [1] ids ['D85']: «La herida del pie llegó a cerrar» · «La herida del pie llegó a cerrar»
- ch01 [9] ids ['D149', 'D04']: «Los residuos siguen en el mismo lugar donde se depositaron» · «Los residuos de la mina siguen en el mismo lugar donde se dejaron»
- ch03 [14] ids ['T13', 'D91']: «En 1946 ya había diagnósticos (plural) de asbestosis» · «En 1946 ya había diagnósticos (varios) de asbestosis»
- ch04 [1] ids ['Q16']: «El hijo cuenta que en esa explosión murió alguien» · «El hijo cuenta que en esa explosión murió alguien (una persona)»
- ch06 [12] ids ['Q07', 'T91']: «El gobierno de Australia Occidental llamó a la abolición del pueblo «el fin de un período oscuro en la historia de nuestro Estado».» · «El gobierno de Australia Occidental calificó la abolición del pueblo como «el fin de un período oscuro en la historia de nuestro Estado».»
- ch07 [9] ids ['D19', 'T09'] / corrida 2 ['D19']: «En 1944 dos inspectores informaron sobre el problema del polvo.» · «En 1944 dos inspectores informaron sobre el problema del polvo» (misma oración, ids distintos)

### Lista entera de «contradice» y «sin_respaldo», por cap y corrida

**ch01 · corrida 1** (2 contradice · 3 sin_respaldo)

- [1] **contradice** ['D85'] — «La herida del pie llegó a cerrar» · fragmento: «Se le cayó un trozo de amianto en el pie y, extrañamente, fue una herida que no se cerraba nunca.»
- [1] **sin_respaldo** [] — «La enfermedad lo alcanzó a miles de kilómetros de Wittenoom»
- [2] **sin_respaldo** [] — «La foto es en blanco y negro»
- [8] **sin_respaldo** [] — «Arrancaron las señales de la carretera»
- [9] **contradice** ['D149', 'D04'] — «Los residuos siguen en el mismo lugar donde se depositaron» · fragmento: «asbestos from Wittenoom's tailings piles had spread out beyond the contamination zone and into the Fortescue River.»

**ch01 · corrida 2** (2 contradice · 2 sin_respaldo)

- [1] **contradice** ['D85'] — «La herida del pie llegó a cerrar» · fragmento: «Se le cayó un trozo de amianto en el pie y, extrañamente, fue una herida que no se cerraba nunca.»
- [1] **sin_respaldo** [] — «Murió a miles de kilómetros de Wittenoom»
- [2] **sin_respaldo** [] — «La foto es en blanco y negro»
- [9] **contradice** ['D04', 'D149'] — «Los residuos de la mina siguen en el mismo lugar donde se dejaron» · fragmento: «The natural forces of wind and water have also spread the asbestos wastes, such that they now cover an area of approximately 10 square kilometres. / asbestos from Wittenoom's tailings piles had spread out beyond the contamination zone and into the Fortescue River.»

**ch02 · corrida 1** (0 contradice · 2 sin_respaldo)

- [5] **sin_respaldo** [] — «Hicieron ese viaje en barco»
- [17] **sin_respaldo** [] — «Era la tierra más roja que Víctor había visto en su vida»

**ch02 · corrida 2** (0 contradice · 2 sin_respaldo)

- [5] **sin_respaldo** [] — «El matrimonio Écija-Bernal viajó en barco»
- [17] **sin_respaldo** [] — «Era la tierra más roja que Víctor había visto en su vida»

**ch03 · corrida 1** (1 contradice · 4 sin_respaldo)

- [4] **sin_respaldo** [] — «Quien lo recuerda es uno de los chicos que bajaron de ese avión»
- [8] **sin_respaldo** [] — «La cita es de un antiguo trabajador de la mina»
- [14] **contradice** ['T13', 'D91'] — «En 1946 ya había diagnósticos (plural) de asbestosis» · fragmento: «cómo en 1946 ya se había diagnosticado un caso de asbestosis»
- [22] **sin_respaldo** [] — «La Junta de Referencia entró al molino y escribió lo que vio con sus propios ojos»
- [30] **sin_respaldo** [] — «La cita es de McNulty»

**ch03 · corrida 2** (2 contradice · 5 sin_respaldo)

- [4] **sin_respaldo** [] — «Quien da el testimonio es uno de los chicos que bajaron de ese avión»
- [8] **sin_respaldo** [] — «Quien lo dijo fue un antiguo trabajador de la mina»
- [14] **contradice** ['T13', 'D91'] — «En 1946 ya había diagnósticos (varios) de asbestosis» · fragmento: «en 1946 ya se había diagnosticado un caso de asbestosis»
- [21] **sin_respaldo** [] — «Ese tribunal fue en persona a ver el molino»
- [22] **sin_respaldo** [] — «La Junta de Referencia entró al molino»
- [30] **sin_respaldo** [] — «La cita es de McNulty»
- [31] **contradice** ['D50', 'T32', 'D130', 'T35'] — «El caso que McNulty escribió en 1962 fue el primer caso de mesotelioma» · fragmento: «Dr J McNulty of the Public Health Department diagnosed the first mesothelioma case arising from Wittenoom. / The first case of mesothelioma outside South Africa—in an ex-Wittenoom mill worker—was reported by McNulty in 1962.»

**ch04 · corrida 1** (1 contradice · 7 sin_respaldo)

- [0] **sin_respaldo** [] — «Llegó semanas después de su boda»
- [1] **contradice** ['Q16'] — «El hijo cuenta que en esa explosión murió alguien» · fragmento: «“El primer día de trabajo de nuestro padre hubo una explosión y murieron varias personas”, relata Daniel hijo.»
- [3] **sin_respaldo** [] — «Los hombres volvían de la mina a las casas con el polvo encima»
- [3] **sin_respaldo** [] — «Los chicos jugaban en esos patios»
- [11] **sin_respaldo** [] — «El parto fue con fórceps»
- [12] **sin_respaldo** [] — «El bebé era muy grande»
- [12] **sin_respaldo** [] — «María venía debilitada por una infección renal»
- [15] **sin_respaldo** [] — «La familia conserva una fotografía del día del bautizo»

**ch04 · corrida 2** (1 contradice · 9 sin_respaldo)

- [0] **sin_respaldo** [] — «Daniel Écija llegó a la pista de Wittenoom semanas después de su boda»
- [1] **contradice** ['Q16'] — «El hijo cuenta que en esa explosión murió alguien (una persona)» · fragmento: «El primer día de trabajo de nuestro padre hubo una explosión y murieron varias personas»
- [1] **sin_respaldo** [] — «Ningún otro documento confirma la explosión»
- [3] **sin_respaldo** [] — «Los hombres volvían a las casas con el polvo encima»
- [3] **sin_respaldo** [] — «Los chicos jugaban en esos patios de relaves»
- [11] **sin_respaldo** [] — «El parto fue con fórceps»
- [12] **sin_respaldo** [] — «El bebé era muy grande»
- [12] **sin_respaldo** [] — «María venía debilitada por una infección renal»
- [15] **sin_respaldo** [] — «La familia conserva una fotografía del día del bautizo»
- [18] **sin_respaldo** [] — «Los Écija creyeron que de Wittenoom se llevaban solo un hijo»

**ch05 · corrida 1** (0 contradice · 1 sin_respaldo)

- [11] **sin_respaldo** [] — «Entre las fotografías hay imágenes del baile, del barco y del bautizo»

**ch05 · corrida 2** (0 contradice · 3 sin_respaldo)

- [11] **sin_respaldo** [] — «Entre las fotografías hay imágenes del baile, del barco y del bautizo»
- [12] **sin_respaldo** [] — «El diagnóstico tuvo lugar en Madrid»
- [18] **sin_respaldo** [] — «Daniel Écija murió en Madrid»

**ch06 · corrida 1** (1 contradice · 4 sin_respaldo)

- [1] **sin_respaldo** [] — «Los nacidos en Wittenoom llevan el nombre del pueblo escrito en el pasaporte.»
- [5] **sin_respaldo** [] — «Mercedes de Juan se somete a una revisión médica que se repite periódicamente.»
- [7] **sin_respaldo** [] — «Melita Markey sigue contando las muertes por su cuenta.»
- [12] **contradice** ['Q07', 'T91'] — «El gobierno de Australia Occidental llamó a la abolición del pueblo «el fin de un período oscuro en la historia de nuestro Estado».» · fragmento: «Q07 (fecha 2022): "The W.A. Government declared this was “an end to a dark period in our State's history.”"; T91: "In 2022, the last remaining residents of Wittenoom town were evicted ahead of its demolition in 2023."»
- [20] **sin_respaldo** [] — «En esa tierra vivía un hombre que no podía irse.»

**ch06 · corrida 2** (1 contradice · 4 sin_respaldo)

- [1] **sin_respaldo** [] — «Quienes nacieron en Wittenoom llevan el nombre del lugar escrito en el pasaporte.»
- [5] **sin_respaldo** [] — «Mercedes de Juan se somete a un control médico que se repite periódicamente.»
- [7] **sin_respaldo** [] — «Melita Markey sigue haciendo el recuento de víctimas.»
- [12] **contradice** ['Q07', 'T91'] — «El gobierno de Australia Occidental calificó la abolición del pueblo como «el fin de un período oscuro en la historia de nuestro Estado».» · fragmento: «Q07 (fecha 2022): "The W.A. Government declared this was “an end to a dark period in our State's history.”"; T91: "In 2022, the last remaining residents of Wittenoom town were evicted ahead of its demolition in 2023."»
- [20] **sin_respaldo** [] — «En esa tierra vivía un hombre que no podía irse.»

**ch07 · corrida 1** (1 contradice · 1 sin_respaldo)

- [9] **contradice** ['D19', 'T09'] — «En 1944 dos inspectores informaron sobre el problema del polvo.» · fragmento: «the Mines Inspector and the Assistant State Mining Engineer reported on the dust issue as early as 1944»
- [13] **sin_respaldo** [] — «Nadie en la familia de Daniel Écija sabe decir qué respiró en Wittenoom.»

**ch07 · corrida 2** (1 contradice · 1 sin_respaldo)

- [9] **contradice** ['D19'] — «En 1944 dos inspectores informaron sobre el problema del polvo» · fragmento: «the Mines Inspector and the Assistant State Mining Engineer reported on the dust issue as early as 1944»
- [13] **sin_respaldo** [] — «Nadie en la familia Écija sabe decir qué respiró él en Wittenoom»

## Costo total

US$ 9.8583 (A 4.8971 + B 4.9612); estimado del auditor en el handoff: ≈ US$ 8–9. Registrado con `hx._track` bajo `lab_f63_*` en `session_overhead` del proceso; `data/cost_history.json` no cambió (mtimes).

## Producción intacta (mtimes antes / después)

25296 archivos bajo `script_engine/`, `data/scripts/_steps/123bbb64-…/`, `data/cost_history.json`, `output/` y `logs/` antes; 25296 después; diferencias: 0 (ninguna).

Declarado: al importar `claude_helpers`/`m01e_pantalla`, `error_handler.py` (l. 68) crea al arrancar cada proceso un `logs/pipeline_<fecha>.log` vacío (0 bytes). Aparecieron tres (prueba en seco, A y B: `pipeline_20261031_131452/131513/131514.log`), ninguno escrito por el runner; CC los borró después de medirlos (vacíos) y la comparación final de mtimes se hizo sin ellos. Ningún otro archivo de producción cambió.

## Lectura de CC (hechos medidos; la calificación con DEBERÍA es del analista, a ciegas)

- Las 22 llamadas devolvieron JSON al primer intento (`stop end_turn`); ningún reintento. Solo intento 1 en los 4 brazos: ninguno de estos papeles pasó por vueltas de corrección, así que no se comparan con el papel de producción (que tuvo una vuelta) sino entre sí.
- Fichas que pasan la validación en papel: S 6 y 9 · O1 8 y 8 · O2 10 y 8 · O3 8 y 9 (de 13 beats). Las que caen lo hacen por `fecha_relato`, `spoiler`, `no_dicho`, `candado`, `caben`, `contradice`; ninguna por `anclaje`, `formato`, `respaldo`, `cita_sin_fecha`, `una_vez` ni `sello`. Ningún reloj con error.
- Gancho (ch01 beat 1): 6 de 8 corridas quedan sin ficha en el gancho. En todas el modelo propuso una: S ×2 D79 (cae por `no_dicho`: la voz dice «2000» en otra oración del video), O1_1 D26 (`caben`), O2 ×2 y O3_1 D108 (`no_dicho`: «Australia» en la oración ancla o vecina); pasan O1_2 (D26) y O3_2 (D80). Ningún brazo usó D85 (el dato central del beat 1 según la escaleta) ni en el gancho ni en otro beat, tampoco O2/O3 que lo tenían en el archivo.
- Los 7 ids que hoy faltan en el archivo (D85, D03, D129, D20, D10, D70, D34) no aparecen en ninguna ficha que pasa de O2/O3 (que los tenían). Ningún brazo propuso un ítem L. `a_pantalla` de la escaleta: 0/6 en 7 corridas; O2_1 cubre D23 (1/6). Los `a_pantalla_vacios` por corrida están en cada `.raw.json` y en el `.md` (⚠).
- Ids de la escaleta usados (de 68): S 1 y 6 · O1 2 y 3 · O2 5 y 4 · O3 3 y 4; D102, D115 y D44 (fuera de la escaleta) se repiten en casi todas las corridas.
- Coincidencia entre corridas (mismo id en el mismo beat): S 3/13 · O1 4/13 · O2 7/13 · O3 4/13. Una sola pareja por brazo: no alcanza para decir que O2 sea más estable; sí que ningún brazo repite más de la mitad de sus fichas.
- Costo y tiempo por papel: S ≈ US$ 0,30 / 134 s · O1 ≈ 0,53 / 144 s · O2 ≈ 0,72 / 160 s · O3 ≈ 0,90 / 237 s. El `high` de O3 salió con 26–28 k tokens (contra 16–19 k de los demás) y no cambió el conteo de fichas que pasan.
- Parte B: las 4 filas del contrato salen como el handoff espera en las dos corridas (ch01 [1] contradice D85; ch01 [2] sin_respaldo las dos veces, no contradice Q25; ch06 [10] respaldada con D31 y D30; ch06 [12] contradice Q07 con T91). Por corrida: 182 y 189 afirmaciones, 154 y 156 respaldadas, 6 y 7 contradice, 22 y 26 sin_respaldo. Seis «contradice» salen en las dos corridas (lista arriba; ch07 [9] con ids distintos). El resto de «contradice» y «sin_respaldo» queda para el analista: parte son matices de redacción («dos inspectores» vs los dos cargos de D19; «diagnósticos» en plural), no errores de hecho.

## Veredicto de revisor-handoff (íntegro)

**VEREDICTO: CUMPLE CON OBSERVACIONES**

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | md5 del handoff | OK | `md5sum` da d684b0fb38a42ad36919a0e211832ad6 |
| 2 | Solo se importa de `m01e_pantalla`; nunca `llamar` ni `generar`; `hx._post` directo; body como `llamar.autor`; `hx.cost_of` y `hx._track("lab_f63_…")` sin `start_video` ni `end_video` | OK | `etapa_a_papel.py` l.36-38 y l.152-184: body con model, `max_tokens=hx.MAX_TOKENS` (100000), system, messages user y `output_config.effort`. `grep start_video\|end_video\|.llamar(\|generar(` solo encuentra una mención en un docstring (l.12). Los 4 `raw.json` revisados traen ese body. |
| 3 | Chequeos que paran | OK | Recalculé: `entrada_md5` a2b19d01…; SYSTEM S/O1 7d2ccdd2…; O2/O3 85d094be…; SYSTEM B ce31cc51…; `01b_narracion_v3.json` c7badfbe…. El SYSTEM B del runner es idéntico al bloque literal del handoff, y el formato también. La oración 2 ANTES y DESPUÉS es idéntica byte a byte a la del handoff. |
| 4 | A.1 entrada completa | OK | Archivo de 362 ítems (D155 · T98 · Q50 · P35 · L24). Los 362 tienen `contexto_fuente`. Los beats traen `emocion`, `imagen_sensorial`, `pregunta_abierta` y `paga`. `escaleta_video` tiene los 7 campos. `disputas` tiene `versiones` y `contradicciones`. El USER de O2 tiene las claves caps, beats, archivo, clima, `escaleta_video` y disputas. El md5 del USER, 018f9cc1…, coincide con el reporte. En `entrada_completa_muestra.json`, D34, D85, Q25 y L01 vienen con su `contexto_fuente`. El texto de L01 lo vi con la codificación rota en la terminal, así que no pude confirmar visualmente el formato «nombre — rol». |
| 5 | A.3 y A.4: validación solo anotar, `.md`, `.raw.json`, tabla A, copia a ciegas | OK | `validar(..., final=True)` con `_pool` en l.189-207. Cada `.md` lista las fichas propuestas con «pasa» o «cortaría», y hay 0 «sin veredicto» en los 8. El encabezado lleva el md5 del SYSTEM del brazo (O2_1 → 85d094be…). Los `raw.json` traen body, respuesta, validación, tokens, US$ y segundos. La tabla A tiene las columnas pedidas. La coincidencia usa la definición de Constantes (÷13, `len(beats)=13`). `grep -il opus\|sonnet\|md5\|medium\|high\|m01e` sobre `ciego/*.md` no encuentra nada. Los 8 papeles cambian el encabezado por «(encabezado quitado)». La clave está en `clave_ciego.json`. |
| 6 | Parte B | OK | Opus 5.5 medium, 14 llamadas. `tabla_b.json` y los 14 `verificador_chNN_n.json` existen. `archivo_items`=362. Las 4 filas del contrato salen en las dos corridas: ch01[1] contradice D85; ch01[2] sin_respaldo; ch06[10] respaldada con D31 y D30; ch06[12] contradice Q07 con T91. Hay «contradice» en ambas corridas (6 pares). El orden del USER (cap, oraciones, archivo, disputas) y los 5 campos del archivo coinciden con `user_b` (l.61-64). |
| 7 | Producción intacta | OK | `mtimes_antes.json` y `mtimes_despues.json` tienen 25296 entradas cada uno y 0 diferencias. Los mtimes actuales de los archivos listados coinciden con `mtimes_despues.json`. `git status`: lo tocado antes de F63 sigue igual (DECISIONES.md, `diag_234_cap4.py`, `f28a.log`), y lo nuevo está solo en `lab/hyperframes/f63/`. `lab/ESTADO_SESION.md` no figura modificado. |
| 8 | Reporte completo | OK | `F63_REPORT.md` trae las tablas A y B, el contrato fila por fila, los md5, los costos (4.8971 + 4.9612 = 9.8583), la coincidencia y la lista entera de contradice y sin_respaldo. El costo de A cuadra con `tabla_a.json` y el de B con `tabla_b.json`. La sección del veredicto sigue «(pendiente)», como corresponde. |
| 9 | Interpretaciones de CC | OK | Las cinco son defendibles, ver observaciones 1 a 4. |

Fuera de alcance: ninguno. Los archivos nuevos están solo en `lab/hyperframes/f63/`. Los archivos de alcance extra (`entrada_completa_muestra.json` y `mtimes_*.json`) también están ahí.

Observaciones:
1. Interpretación (a) aceptable. «Solo intento 1» se aplicó a la corrección. El reintento por falta de JSON quedó en el código (l.159-183) como pide §Cómo se llama al modelo, y no se usó: el log muestra 22 de 22 con un solo intento.
2. Interpretaciones (b) y (c) aceptables. Ambas son lecturas razonables de «coincidencia» y de «cubiertos», y están declaradas en el reporte. Ambas se calculan sobre fichas que pasan la validación, no sobre las propuestas.
3. Interpretación (d) es un desvío menor: `etapa_b_verificador` importa de `etapa_a_papel`, que el handoff no previó. Es solo lab y no cambia ninguna medición.
4. Interpretación (e) es un exceso menor: `entrada_completa_muestra.json` y `mtimes_*.json` quedaron en `f63/`, dentro del alcance permitido.
5. Declaración sobre los `logs/pipeline_*.log`. Es coherente con el repo: el reporte dice que `error_handler.py` crea un log vacío al importar. Pero mi revisión importó `m01e_pantalla` y creó `logs/pipeline_20261031_132315.log` (0 bytes), que sigue ahí. No es de CC y no lo borré por ser de solo lectura. Hay que sacarlo antes de cualquier comparación de mtimes posterior.
6. Lo que dice el reporte sobre qué ids usó cada brazo (por ejemplo «ningún brazo usó D85») y sobre los motivos de caída del gancho no lo recalculé: solo cuadré totales, md5 y estructura. Es el trabajo del analista a ciegas.
7. Pendiente de proceso, no es falla: el commit de `f63/` y la actualización de `lab/ESTADO_SESION.md` tienen que hacerse después de este veredicto. El veredicto va íntegro en la sección «(pendiente)».

Riesgos que el contrato no cubre:
- Cada brazo tiene una sola pareja de corridas (coincidencia entre 4/13 y 7/13), así que la diferencia entre brazos puede ser ruido de corrida.
- El juicio de calidad depende del analista a ciegas. Las métricas del código (fichas que pasan) no equivalen a la nota con DEBERÍA.
- Los logs vacíos de `logs/` que crea cualquier import de `claude_helpers` o `m01e` ensucian los mtimes de producción: ya apareció uno más durante esta revisión.

### Adenda de CC
- **Obs. 4 (L01 «nombre — rol»):** verificado por código en la prueba en seco: `L01` → «Yampire Mine — Una de las tres minas de donde se extrajo asbesto comercialmente.» (el runner lo arma en `entrada_completa`, l.117-118).
- **Obs. 5:** el `logs/pipeline_20261031_132315.log` (0 bytes) de la revisión se borró después del veredicto y la comparación de mtimes se repitió: 0 diferencias. Queda anotado como riesgo del proceso: todo import de `claude_helpers`/`m01e_pantalla` (también `pytest`) crea uno; la comparación de mtimes de una tanda tiene que mirar `logs/` sabiendo eso.
- **Obs. 6:** los ids usados por brazo salen de `tabla_a.json` (`ids_pasan_por_beat`) y los motivos del gancho de los `descartados` con `beat == 1` de cada `.raw.json`; están en «Lectura de CC» como hechos medidos, no como calificación.
- **Riesgo 1:** compartido; el handoff fijó 2 corridas por brazo (Omar) y el reporte lo dice. Si Omar quiere separar brazo de ruido, hacen falta más corridas del brazo que elija (≈ US$ 0,30–0,90 cada una).
