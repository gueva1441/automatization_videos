# F66_REPORT — Verificador de narración a producción: F63 B cableado tras el guion, con corrección automática

Handoff `lab/hyperframes/f66/HANDOFF_F66_verificador_narracion.md` (md5 397a273ad89ee55face3fbf6ac4ea824) · rama `f11-guion-v4` · base `a9aa200` · 2026-10-31 · CC Opus 5.5 high · commits `3a1dc2f` (A), `504602b` (B), `17f830e` (C). Corrió antes que F65b por pedido del analista (DECISIONES 16:13 decía al revés; el pedido de esta tanda manda).

## Lo primero: el código cumple el handoff, pero la corrección degradó el guion en todo lo que tocó

Hay que leer esto como una falla de diseño de la corrección, no como un éxito con un efecto lateral. Se encontraron 7 «contradice» (las 5 estables de F63 + 2), las 7 ediciones pasaron la guardia y la re-verificación ya no las marca. Pero la edición usa el pedido de la reparación («Sacá esas frases o corregilas…»), y en **4 de 7 el modelo sacó la oración entera**; en 2 sacó solo un pedazo y en 1 corrigió (y además sacó otro hecho que nadie marcó). Ninguna puso el dato correcto del archivo salvo «un diagnóstico». La guardia léxica mide lo que se agrega, no lo que se pierde, y la re-verificación no puede marcar lo que ya no está. Costo narrativo medido en `MEDIR_C.md` (entero abajo):

- **El gancho perdió su promesa.** Cap 1 baja de 161 a 118 palabras. Sale «Ese pie va a cerrar; lo que respira mientras espera que cierre va a tardar casi treinta años en matarlo, y lo va a alcanzar a miles de kilómetros de aquí» (lo que abre el loop L1, y solo «va a cerrar» era falso) y sale «Lo que sobró de la mina, en cambio, sigue donde lo dejaron» (la segunda mitad de `promesa_gancho`).
- **El cap 3 perdió el re-gancho.** Sale «El año en que McNulty escribió ese primer caso, un recién casado de Madrid se bajaba de un avión en esa misma pista de polvo», la última oración del beat 6, el de `recuerda_loop` (F56 B: `rebalance` protege esa oración, `edit_sentences` no; es una paráfrasis de la literal de la escaleta, por eso `MEDIR_C` no la encuentra ni antes: la pérdida sale de leer el texto). El «contradice» era además discutible: la objeción era sobre el año del caso, no sobre el recién casado.
- **Se fue texto de más:** «un inspector describió las condiciones de trabajo como terroríficas» (ch03 [14]; nadie lo marcó) y «dos inspectores en 1944» (ch07 [9], que paga el loop L2 «quién sabía»; lo marcado era «inspector + ingeniero», y el hecho de 1944 era cierto).
- **La cita del gobierno salió** (ch06 [12]) en vez de fecharse en 2022; el riesgo declarado de la cifra no se llegó a medir porque el modelo no intentó poner la fecha. Lo mismo «varios» en ch04 [1]: sacó «y que alguien murió» en vez de corregir. **La guardia no rechazó ninguna.**

Son 104 palabras menos en total (≈ 35 s de voz, a 0,34 s por palabra). `g4.bloqueantes` da 0 → 0: nada en la cadena lo detecta. No lo revertí ni volví a llamar: el handoff dice una ronda y que la cadena sigue, y restaurar es decisión de Omar (narración previa en `lab/hyperframes/f66/antes/`). Ver «Lo que queda abierto» 1.

## Etapa A — módulo `narracion_verificador` (`3a1dc2f`)

`script_engine/narracion_verificador.py` nuevo: `SYSTEM_B`, `FORMATO_B`, `archivo_b`, `user_b` copiados literales del lab (leídos del archivo, no retipeados); `verificar_caps` en paralelo (ThreadPool, uno por cap), 2 intentos totales por cap por excepción de API o sin JSON, `hx._post` + `hx.cost_of` + `hx._track(…, "m01b_verificador")`. Un cap que falla dos veces queda con `error` y no frena. El lab no se tocó.

**Salida:** `user_b` de ch01 de Wittenoom = 156.148 caracteres; md5 del SYSTEM `ce31cc515a077d74da72479e9693296e`; md5 del USER `9f2dfc976d9b3e8e71f0e14a77bd55aa`, **idéntico** al de `f63/b/verificador_ch01_1.json`. Tests: 7 (md5, literal del lab, user_b, parseo, reintento por JSON y por excepción, cap caído no frena, 7 caps en paralelo con una barrera real).

## Etapa B — cableado (`504602b`)

```
antes:   guionista → reparar → particionar → pantalla (m01e) → juez
después: guionista → reparar → particionar → VERIFICACIÓN → pantalla (m01e) → juez (con la partición final)
                                           │
                                           ├ verificar_caps sobre 01b_narracion_v3 (7 a la vez)
                                           ├ por «contradice»: párrafo por texto (el beat desempata) → problema «v»
                                           ├ edit_sentences (REGEN_GUARD, cifras de los ids) → una ronda
                                           ├ si cambió algo: particionar con los mismos títulos, sin acortar
                                           ├ re-verificar_caps solo de los caps cuyo texto cambió
                                           └ 01b_verificacion.json/.md · verificacion en 01b_guionista_v4.json · aviso si quedan
--verificar-narracion: run_verificacion + run_pantalla sobre la narración escrita; sin guionista; sin juez
```

- `fase1_5.py`: `run_verificacion`, `_parrafo_de`, `_verificacion_md`, `verificar_narracion`, CLI, paso de costo «verificacion»; `parada_del_papel` lleva el aviso.
- `guion_v4.edit_sentences(…, guard=None, cifras_ok=None)`; `m01d.particionar(…, title_list=None)`; `m01e_pantalla`: `generar` pone `aviso_narracion` y `a_markdown` lo imprime al final (`PANTALLA_SYSTEM`, `prompt_md5()` f2bfdf20… y `m01e-7` sin cambios, test).

**Interpretaciones de CC (declaradas):**
1. **`cifras_ok` lee `texto` y `fecha` de los ids**, no solo `texto`: la tabla dice `texto`, pero Q07 trae 2022 en `fecha` y el handoff pide justo que «En 2022…» no caiga. Los nombres no se aceptan por ahí.
2. **Re-partición con `shorten=None`:** con el acortador real, `rebalance` volvería a llamar a Gemini por el cap 3 (largo conocido) y recortaría de nuevo el cap 7, texto que nadie marcó; además el pedido de la tanda no lista esa llamada. Efecto: se pierde del skeleton la nota vieja de partición (queda en `antes/`).
3. **`parrafos` de `run_verificacion`** (los de la reparación) solo sirven para anotar qué acortó la partición (`acortados_por_la_particion`): se edita sobre `01b_narracion_v3`, como pide el handoff; partir desde la reparación desharía el acortado.
4. **`--verificar-narracion` no corre el juez m05** (el handoff lo define como verificación + pantalla): `06_judge_narrative.json` queda de la narración anterior.

**Tests:** `test_module_f66` 23 (16 nuevos), con `claude_helpers._post` explotando si alguien lo alcanza. Suites vecinas (f10, f11b, f17, f22d, f27, f36c, f37a/b, f38*, f39, f40, f41, f64, f66): 211 verdes + 8 saltados. Ningún test viejo llega a la verificación real: los que tocan `run_guion_v4` lo reemplazan o cortan antes. Stickers ×5, MAPA 0.

## Etapa C — corrida real (`17f830e`)

Respaldos en `lab/hyperframes/f66/antes/` (10 archivos, md5 iguales al copiar); narración de partida `c7badfbe…` = la del lab. Comando: `python fase1_5.py --topic 123bbb64-9fca-4395-8bf4-57d60e219ef1 --verificar-narracion` (`etapa_c_run.log`).

Las 5 estables de §0 aparecieron todas (ch01 [1], ch01 [9], ch03 [14], ch04 [1], ch06 [12]); más ch07 [9] (ya salió en F63) y ch03 [31] (nueva). Una «nueva en la re-verificación» queda como aviso: ch03 [15] (Q53, el arbitraje es de 1949 y por el orden del relato parece anterior a 1948). Narración final `b079e130deb67d92ec6eeae11ad2c700`. Caps re-verificados: ch01, ch03, ch04, ch06, ch07.

### 01b_verificacion.md, entera

#### Verificación de la narración

Narración antes `c7badfbe260f5eb24a47e780b40406b5` · después `b079e130deb67d92ec6eeae11ad2c700` · caps re-verificados: ['ch01', 'ch03', 'ch04', 'ch06', 'ch07'] · US$ 4.1663 del verificador · 1 sin resolver

| cap | oración | afirmación | ids | fragmento | qué se hizo | después |
|---|---|---|---|---|---|---|
| ch01 | [1] Ese pie va a cerrar; lo que respira mientras espera que cierre va a tardar casi treinta años en matarlo, y lo va a alcanzar a miles de kilómetros de aquí. | La herida del pie va a cerrar. | D85 | Se le cayó un trozo de amianto en el pie y, extrañamente, fue una herida que no se cerraba nunca. | corregida ✔ | (oración sacada) |
| ch01 | [9] Lo que sobró de la mina, en cambio, sigue donde lo dejaron. | Los residuos de la mina siguen donde los dejaron. | D04, D149 | The natural forces of wind and water have also spread the asbestos wastes, such that they now cover an area of approximately 10 square kilometres. / asbestos from Wittenoom's tailings piles had spread out beyond the contamination zone and into the Fortescue River. | corregida ✔ | (oración sacada) |
| ch03 | [14] En 1946 ya había diagnósticos de asbestosis, y un inspector describió las condiciones de trabajo como terroríficas. | En 1946 ya había diagnósticos (en plural) de asbestosis | T13, D91 | cómo en 1946 ya se había diagnosticado un caso de asbestosis | corregida ✔ | En 1946 ya había un diagnóstico de asbestosis. |
| ch03 | [31] El año en que McNulty escribió ese primer caso, un recién casado de Madrid se bajaba de un avión en esa misma pista de polvo. | McNulty escribió el primer caso de mesotelioma en 1962 | D50, T32, D130 | Dr J McNulty of the Public Health Department diagnosed the first mesothelioma case arising from Wittenoom. / The first case of mesothelioma outside South Africa—in an ex-Wittenoom mill worker—was reported by McNulty in 1962. | corregida ✔ | (oración sacada) |
| ch04 | [1] El hijo cuenta que el primer día de trabajo de su padre hubo una explosión y que alguien murió; no hay otro documento que lo confirme. | Según el hijo, en esa explosión murió alguien | Q16 | El primer día de trabajo de nuestro padre hubo una explosión y murieron varias personas | corregida ✔ | El hijo cuenta que el primer día de trabajo de su padre hubo una explosión; no hay otro documento que lo confirme. |
| ch06 | [12] El gobierno de Australia Occidental lo llamó «el fin de un período oscuro en la historia de nuestro Estado». | El gobierno de Australia Occidental llamó a la abolición del pueblo «el fin de un período oscuro en la historia de nuestro Estado». | Q07, T91 | Q07 (fecha 2022): "The W.A. Government declared this was “an end to a dark period in our State's history.”" — la cita está fechada en 2022, ligada al desalojo de los últimos residentes antes de la demolición ("In 2022, the last remaining residents of Wittenoom town were evicted ahead of its demolition in 2023"), no a la abolición de 2006-2007. | corregida ✔ | (oración sacada) |
| ch07 | [9] Quién sabía está escrito: dos inspectores en 1944, un médico al que llamaron alborotador en 1948, un tribunal que entró al molino en 1957. | Dos inspectores advirtieron sobre el polvo en 1944 | D19 | the Mines Inspector and the Assistant State Mining Engineer reported on the dust issue as early as 1944 | corregida ✔ | Quién sabía está escrito: un médico al que llamaron alborotador en 1948, un tribunal que entró al molino en 1957. |
| ch03 | [15] El defensor del empleador tenía otra lectura: «El mero hecho de que haya nubes de polvo no significa que ese polvo sea peligroso». | Esa postura se presenta, por el orden del relato, como respuesta al diagnóstico de 1946 y anterior a 1948. | Q53 | En el arbitraje de 1949, el defensor empresarial sostuvo que la compañía no admitía que el polvo fuera peligroso | nueva en la re-verificación ⚠ (una ronda: queda como aviso) | — |

#### Sin respaldo en el archivo (24; no se corrige)

- ch01 [1] La muerte lo alcanzó a miles de kilómetros de Wittenoom.
- ch01 [2] La foto es en blanco y negro.
- ch01 [6] La foto es de 1963.
- ch02 [5] El matrimonio Écija-Bernal viajó en barco
- ch02 [17] Era la tierra más roja que Víctor había visto en su vida
- ch03 [4] El testimonio es de uno de los chicos que bajaron de ese avión
- ch03 [8] La cita es de un antiguo trabajador de la mina
- ch03 [21] El tribunal fue a ver el molino en persona
- ch03 [30] La cita es de McNulty
- ch03 [31] Ese recién casado llegó en avión a la pista de Wittenoom
- ch04 [0] Daniel Écija llegó a Wittenoom semanas después de su boda
- ch04 [1] No hay otro documento que confirme la explosión
- ch04 [3] Los hombres volvían a casa con el polvo encima
- ch04 [3] Los chicos jugaban en esos patios
- ch04 [11] El parto fue con fórceps
- ch04 [12] El bebé era muy grande
- ch04 [12] María venía debilitada por una infección renal
- ch04 [15] La familia conserva una fotografía del día del bautizo
- ch04 [18] Los Écija creyeron que de Wittenoom se llevaban solo un hijo
- ch05 [11] Entre las fotos hay una del baile, una del barco y una del bautizo
- ch06 [1] Quienes nacieron en Wittenoom tienen el nombre del lugar escrito en el pasaporte.
- ch06 [5] Mercedes de Juan tiene controles médicos que se repiten.
- ch06 [20] En esa tierra vivía un hombre que no podía irse.
- ch07 [13] Nadie en la familia de Daniel Écija sabe decir qué respiró en Wittenoom


### MEDIR_C.md, entero (antes → después, 0 llamadas)

#### F66 Etapa C — qué le hizo la corrección a la narración (0 llamadas)

| cap | palabras antes | palabras después | oraciones antes | oraciones después |
|---|---|---|---|---|
| 1 | 161 | 118 | 12 | 10 |
| 2 | 220 | 220 | 18 | 18 |
| 3 | 523 | 489 | 32 | 31 |
| 4 | 232 | 228 | 19 | 19 |
| 5 | 292 | 292 | 24 | 24 |
| 6 | 297 | 278 | 21 | 20 |
| 7 | 216 | 212 | 16 | 16 |

#### Párrafo antes → después, por edición

##### cap 1 beat 1 · aceptada

- problema: «Ese pie va a cerrar; lo que respira mientras espera que cierre va a tardar casi treinta años en matarlo, y lo va a alcanzar a miles de kilómetros de aquí.» → el archivo dice otra cosa (D85): «Se le cayó un trozo de amianto en el pie y, extrañamente, fue una herida que no se cerraba nunca.»
- SALE: «Ese pie va a cerrar; lo que respira mientras espera que cierre va a tardar casi treinta años en matarlo, y lo va a alcanzar a miles de kilómetros de aquí.»

##### cap 1 beat 1 · aceptada

- problema: «Lo que sobró de la mina, en cambio, sigue donde lo dejaron.» → el archivo dice otra cosa (D04, D149): «The natural forces of wind and water have also spread the asbestos wastes, such that they now cover an area of approximately 10 square kilometres. / asbestos from Wittenoom's tailings piles had spread out beyond the contamination zone and into the Fortescue Ri
- SALE: «Lo que sobró de la mina, en cambio, sigue donde lo dejaron.»

##### cap 3 beat 5 · aceptada

- problema: «En 1946 ya había diagnósticos de asbestosis, y un inspector describió las condiciones de trabajo como terroríficas.» → el archivo dice otra cosa (T13, D91): «cómo en 1946 ya se había diagnosticado un caso de asbestosis»
- SALE: «En 1946 ya había diagnósticos de asbestosis, y un inspector describió las condiciones de trabajo como terroríficas.»
- ENTRA: «En 1946 ya había un diagnóstico de asbestosis.»

##### cap 3 beat 6 · aceptada

- problema: «El año en que McNulty escribió ese primer caso, un recién casado de Madrid se bajaba de un avión en esa misma pista de polvo.» → el archivo dice otra cosa (D50, T32, D130): «Dr J McNulty of the Public Health Department diagnosed the first mesothelioma case arising from Wittenoom. / The first case of mesothelioma outside South Africa—in an ex-Wittenoom mill worker—was reported by McNulty in 1962.»
- SALE: «El año en que McNulty escribió ese primer caso, un recién casado de Madrid se bajaba de un avión en esa misma pista de polvo.»

##### cap 4 beat 7 · aceptada

- problema: «El hijo cuenta que el primer día de trabajo de su padre hubo una explosión y que alguien murió; no hay otro documento que lo confirme.» → el archivo dice otra cosa (Q16): «El primer día de trabajo de nuestro padre hubo una explosión y murieron varias personas»
- SALE: «El hijo cuenta que el primer día de trabajo de su padre hubo una explosión y que alguien murió; no hay otro documento que lo confirme.»
- ENTRA: «El hijo cuenta que el primer día de trabajo de su padre hubo una explosión; no hay otro documento que lo confirme.»

##### cap 6 beat 12 · aceptada

- problema: «El gobierno de Australia Occidental lo llamó «el fin de un período oscuro en la historia de nuestro Estado».» → el archivo dice otra cosa (Q07, T91): «Q07 (fecha 2022): "The W.A. Government declared this was “an end to a dark period in our State's history.”" — la cita está fechada en 2022, ligada al desalojo de los últimos residentes antes de la demolición ("In 2022, the last remaining residents of Wittenoom 
- SALE: «El gobierno de Australia Occidental lo llamó «el fin de un período oscuro en la historia de nuestro Estado».»

##### cap 7 beat 13 · aceptada

- problema: «Quién sabía está escrito: dos inspectores en 1944, un médico al que llamaron alborotador en 1948, un tribunal que entró al molino en 1957.» → el archivo dice otra cosa (D19): «the Mines Inspector and the Assistant State Mining Engineer reported on the dust issue as early as 1944»
- SALE: «Quién sabía está escrito: dos inspectores en 1944, un médico al que llamaron alborotador en 1948, un tribunal que entró al molino en 1957.»
- ENTRA: «Quién sabía está escrito: un médico al que llamaron alborotador en 1948, un tribunal que entró al molino en 1957.»

#### Lo que la escaleta espera de la voz

- `recuerda_loop` (beat 6): «Un año después de que McNulty escribiera ese primer caso, un recién casado de Madrid se bajaba de un avión en esa misma pista de polvo.» → antes NO está · después **NO está**
- `promesa_gancho`: «Un minero español vivió diez meses en un pueblo construido con polvo de asbesto azul y tardó casi treinta años en morir de eso; el pueblo ya no existe en los mapas, pero tres millones de toneladas de relaves siguen donde las dejaron.»
- `loops`: [{"id": "L1", "pregunta": "¿Qué le hizo Wittenoom a Daniel en diez meses, si el pueblo ya estaba a miles de kilómetros cuando lo alcanzó?", "abre_beat": 1, "paga_beat": 10}, {"id": "L2", "pregunta": "¿Quién sabía que el polvo mataba, desde cuándo, y quién va a limpiar lo que quedó?", "abre_beat": 5, "paga_beat": 13}]

#### Bloqueantes del guion con el verificador de Sonnet apagado: antes 0 → después 0

- ningún bloqueante nuevo

#### Skeleton

- títulos iguales: True
- particion antes: {'notas': ['cap 3: el acortado del último párrafo (beat 6) perdía la oración del re-gancho → se deja el original', 'cap 3: 3056 caracteres > 2242 y no se pudo mover ni acortar (aviso)', 'cap 7: 1378 caracteres > 1255 → el editor acortó el último párrafo (304 → 192)'], 'titulos': 'flash'}
- particion después: {'notas': ['cap 3: 2861 caracteres > 2242 y no se pudo mover ni acortar (aviso)'], 'titulos': 'los de la partición anterior'}
- claves que cambian en chapters: []
- otras claves del skeleton que cambian: []


### El papel nuevo

m01e-7 · claude-opus-5-5 medium · 2 intentos · cierre **sin motivos** · 13/13 fichas · US$ 1.2309 (autor 1.1077 + verificador 0.1232) · sin aprobar. Con F65a ya no se forzaron las fichas técnicas: los `a_pantalla` D01, D51, D23, D40, D61 quedan como aviso ⚠ (el autor puso D34). El verificador cortó 1 en el intento 1 (T38 «SALIDA · 24 de septiembre, 1962» en ch02 beat 3: la vecina ya lo dice); la vuelta puso D83.

| beat | cap | función | ficha | texto |
|---|---|---|---|---|
| 1 | ch01 | gancho | D108 | ESE PUEBLO · Escenario del peor desastre industrial de Australia |
| 2 | ch02 | planteo | Q25 | POR QUÉ SE FUERON · En España no teníamos nada, ninguno de los dos. |
| 3 | ch02 | planteo | D83 | EL PACTO DEL FRANQUISMO · Operación Canguro, desde 1958 |
| 4 | ch03 | planteo | D02 | LO QUE HABÍA EN LA PISTA · Relaves con alrededor de un 5% de asbesto |
| 5 | ch03 | escalada | D44 | ASBESTOSIS · Ligada al asbesto desde 1930 |
| 6 | ch03 | giro | D138 | ANTES DE CADA INSPECCIÓN · La empresa limpiaba para ocultar el peligro |
| 7 | ch04 | escalada | Q19 | LOS CHICOS · Nadie nos avisó de nada. |
| 8 | ch04 | giro | D102 | ESE BEBÉ, HOY · Productor de televisión en España |
| 9 | ch05 | escalada | D94 | EN 1989, CSR PAGÓ · 18,3 millones de dólares australianos a 200 afectados |
| 10 | ch05 | pico | Q35 | A QUIÉN CULPA · Por culpa de una empresa que no tuvo reparos |
| 11 | ch06 | respiro | D34 | EL GOBIERNO RECONOCE · Miles de muertos: mineros, vecinos y visitantes |
| 12 | ch06 | revelacion | T80 | QUIÉN LO ANUNCIÓ · Jon Ford, ministro de Desarrollo Regional |
| 13 | ch07 | cierre | D69 | LO QUE EL ESTADO SÍ COBRÓ · Más de 70.000 millones de dólares en regalías de Pilbara |

`01e_pantalla.md` entero:

#### Guion de pantalla en papel — 123bbb64-9fca-4395-8bf4-57d60e219ef1

`m01e_pantalla` m01e-7 (md5 del prompt `f2bfdf2044a4c77a59fc62ebe93966c2`) · claude-opus-5-5 medium · 2 intento(s) · US$ 1.2309 (autor 1.1077 + verificador 0.1232) · tokens de entrada 88303

Segundos por palabra 0.34 (mediana de 347 oraciones de 16 caps del narrador N9Z5MLTIaHFLflaLtbDi) · intento 1: in 88303 · out 17659 · US$ 0.7064 · intento 2: in 94705 · out 1125 · US$ 0.4013

Totales: 13 fichas · 8 sellos · 3 relojes · 57 descartados

#### ch01 — La herida que no cerraba

- beat 1 · gancho · PICO · ficha **D108** [normal] «ESE PUEBLO · Escenario del peor desastre industrial de Australia» en [6] sobre «pueblo» (61/71 car.) · respaldo: «La industria de la crocidolita de Wittenoom es considerada el peor desastre industrial en la historia de Australia.» · año — / relato — · verificador: pasa (no_dicho {'no_dicho': ['Australia']}) — La voz nunca califica a Wittenoom como el peor desastre industrial de Australia; solo coincide la palabra 'Australia'. · aporta: Dice la escala de lo que pasó en el pueblo de la foto, algo que la voz nunca dice. · sello **AMENAZA** en [3]
- relojes: —

#### ch02 — A la tierra roja

- beat 2 · planteo · ficha **Q25** [cita] «POR QUÉ SE FUERON · En España no teníamos nada, ninguno de los dos.» — María Bernal (autor: modelo) en [2] sobre «confiaba» (81/90 car.) · respaldo: «En España no teníamos nada, ninguno de los dos.» · año — / relato 1961 · verificador: pasa (spoiler {'spoiler': ['2']}) — La voz cita otra frase de María ('Me pegué a mi marido…') y dice que confiaba en lo que venía, pero nunca dice que en España no tenían nada. · aporta: Muestra la pobreza que los empujó a irse, que la voz no cuenta. · sello **MEMORIA** en [3]
- beat 3 · planteo · PICO · ficha **D83** [normal] «EL PACTO DEL FRANQUISMO · Operación Canguro, desde 1958» en [7] sobre «acuerdo» (52/90 car.) · respaldo: «Un acuerdo migratorio entre el franquismo y Australia iniciado en 1958, llamado Operación Canguro» · año 1958 / relato 1962 · aporta: Da el nombre del acuerdo entre gobiernos, dice que lo firmó el franquismo y desde qué año funcionaba. La voz no dice nada de eso. · sello —
- relojes: 16 SEP 1961 en [0], 20 SEP 1962 en [4]

#### ch03 — Ignorar el veneno

- beat 4 · planteo · ficha **D02** [normal] «LO QUE HABÍA EN LA PISTA · Relaves con alrededor de un 5% de asbesto» en [6] sobre «relaves» (65/90 car.) · respaldo: «Se estima que los relaves de la minería, que contienen alrededor de un 5% de asbesto» · año — / relato 1962 · aporta: Cuantifica cuánto asbesto quedaba en los relaves con que se hizo la pista. · sello —
- beat 5 · escalada · PICO · ficha **D44** [normal] «ASBESTOSIS · Ligada al asbesto desde 1930» en [14] sobre «asbestosis» (38/40 car.) · respaldo: «El informe de Merryweather y Price de 1930 estableció que la asbestosis era una enfermedad consecuente a la exposición al asbesto.» · año 1930 / relato 1946 · aporta: La enfermedad ya estaba ligada al asbesto más de una década antes de las advertencias que cuenta la voz. · sello **AVISO** en [17] · ⚠ sin su a_pantalla: D01 (el autor no lo puso)
- beat 6 · giro · ficha **D138** [normal] «ANTES DE CADA INSPECCIÓN · La empresa limpiaba para ocultar el peligro» en [22] sobre «molino» (67/71 car.) · respaldo: «ABA lograba ocultar el alcance de los peligros para la salud, especialmente en el molino, limpiando específicamente para las inspecciones oficiales.» · año — / relato 1957 · aporta: Lo que vieron los inspectores podía ser una versión limpiada a propósito. · sello **SILENCIO** en [30]
- relojes: —

#### ch04 — El juego peligroso

- beat 7 · escalada · PICO · ficha **Q19** [cita] «LOS CHICOS · Nadie nos avisó de nada.» — Víctor Calvo (autor: modelo) en [9] sobre «miedo» (51/51 car.) · respaldo: «Nadie nos avisó de nada.» · año — / relato 1962 · aporta: Los chicos jugaban con el amianto porque nadie les advirtió del peligro. · sello **CALMA** en [7]
- beat 8 · giro · ficha **D102** [normal] «ESE BEBÉ, HOY · Productor de televisión en España» en [13] sobre «Daniel» (46/51 car.) · respaldo: «Daniel Écija (hijo), nacido en Wittenoom, tiene 63 años y es un conocido productor de televisión en España.» · año — / relato 1963 · aporta: Muestra quién es hoy el bebé nacido en Wittenoom. · sello —
- relojes: 7 JUL 1963 en [15]

#### ch05 — Wittenoom por dentro

- beat 9 · escalada · ficha **D94** [normal] «EN 1989, CSR PAGÓ · 18,3 millones de dólares australianos a 200 afectados» en [8] sobre «juez» (70/90 car.) · respaldo: «En 1989, la empresa CSR pagó 18,3 millones de dólares australianos en indemnizaciones a 200 afectados.» · año 1989 / relato 1988 · verificador: pasa (fecha_relato {'fecha_relato': ['1989']}) — La voz menciona el fallo de 1988, pero no el pago de 18,3 millones a 200 afectados en 1989; la ficha suma un hecho nuevo. · aporta: Muestra la consecuencia económica del fallo: lo que la empresa terminó pagando y a cuántos. · sello **INMINENTE** en [10] · ⚠ sin su a_pantalla: D51 (el autor lo descartó [otro]: Una sola ficha por beat; la indemnización de CSR muestra más la consecuencia.)
- beat 10 · pico · PICO · ficha **Q35** [cita] «A QUIÉN CULPA · Por culpa de una empresa que no tuvo reparos» — Su hijo (autor: modelo) en [20] sobre «hijo» (69/71 car.) · respaldo: «Perdimos a nuestro padre, y mi madre perdió a su marido, por culpa de una empresa que no tuvo reparos en arriesgar la vida de sus trabajadores para ganar dinero» · año — / relato 1991 · aporta: El hijo señala a la empresa como responsable, cosa que la voz no le hace decir. · sello — · ⚠ sin su a_pantalla: D23 (el autor lo descartó [spoiler]: Adelanta el recuento de muertos que la voz aborda en ch06.)
- relojes: —

#### ch06 — El polvo viaja

- beat 11 · respiro · ficha **D34** [normal] «EL GOBIERNO RECONOCE · Miles de muertos: mineros, vecinos y visitantes» en [7] sobre «cifra» (67/90 car.) · respaldo: «Los restos de amianto de las operaciones mineras en Wittenoom han provocado miles de muertes entre mineros, residentes y visitantes.» · año — / relato 2000 · aporta: Las muertes alcanzaron también a vecinos y a gente que solo estuvo de visita. · sello **ALARMA** en [8]
- beat 12 · revelacion · PICO · ficha **T80** [normal] «QUIÉN LO ANUNCIÓ · Jon Ford, ministro de Desarrollo Regional» en [10] sobre «abolido» (57/66 car.) · respaldo: «El Ministro de Desarrollo Regional, Hon Jon Ford MLC, anunció que el pueblo había sido oficialmente abolido.» · año 2007 / relato 2007 · aporta: Pone nombre y cargo a quien anunció que el pueblo dejaba de existir. · sello **RABIA** en [18] · ⚠ sin su a_pantalla: D40 (el autor lo descartó [otro]: La superficie oficial varía entre las fuentes y suma menos que el dato central.)
- relojes: —

#### ch07 — La herida ancestral

- beat 13 · cierre · PICO · ficha **D69** [normal] «LO QUE EL ESTADO SÍ COBRÓ · Más de 70.000 millones de dólares en regalías de Pilbara» en [7] sobre «dinero» (81/90 car.) · respaldo: «El gobierno de Australia Occidental ha extraído más de 70.000 millones de dólares en regalías de la minería en Pilbara.» · año — / relato 2026 · aporta: Contrasta lo que el Estado cobró de la minería con que no gastó nada en limpiar. · sello — · ⚠ sin su a_pantalla: D61 (el autor lo descartó [otro]: Una sola ficha por beat; D69 suma más al cierre.)
- relojes: —

#### Lo que cayó

- (nada)

#### Verificador

- 2 llamada(s) · US$ 0.1232 · marcas de la última validación: 8
- llamada 1: 9 marca(s) → fichas pasa 3 · corta 1 · descartes dicho 5 · no_dicho 0 · US$ 0.0633 · 10.7 s · pedido 371e2827…
- llamada 2: 8 marca(s) → fichas pasa 3 · corta 0 · descartes dicho 5 · no_dicho 0 · US$ 0.0599 · 8.9 s · pedido 840448c8…
  - D108 (ch01 beat 1, [6]) «ESE PUEBLO · Escenario del peor desastre industrial de Australia»: no_dicho «Australia» en ch01 [5] («Wittenoom, Australia Occidental, 1963.»)
  - Q25 (ch02 beat 2, [2]) «POR QUÉ SE FUERON · En España no teníamos nada, ninguno de los dos.»: spoiler «2» en ch02 [7] («No iban solos: cerca de ocho mil españoles cruzaron por un acuerdo entre los dos»)
  - D94 (ch05 beat 9, [8]) «EN 1989, CSR PAGÓ · 18,3 millones de dólares australianos a 200 afectados»: fecha_relato «1989» en ch05 [8] («Y en 1988 un juez determinó que la compañía había mostrado un desprecio continuo») (relato 1988)
  - descarte D03 («Los desechos de asbesto se utilizaron en la construcción de la ciudad de Wittenoom, la pista de aterrizaje y otras instalaciones.»; el autor: «La voz dice que el pueblo y la pista se hicieron con relaves.»; la voz de ch03 no dice ['Wittenoom'])
  - descarte D129 («En Wittenoom se usaban los relaves, residuos del procesamiento del asbesto, como superficie para carreteras y para cubrir patios y lugares públicos.»; el autor: «La voz dice que los relaves cubrían carreteras y patios.»; la voz de ch03 no dice ['Wittenoom'])
  - descarte T13 («Se diagnosticó un primer caso de asbestosis en Wittenoom. (fecha 1946)»; el autor: «La voz dice el diagnóstico de 1946.»; la voz de ch03 no dice ['Wittenoom'])
  - descarte D21 («La producción minera en Wittenoom se incrementó en 1961 a pesar de la evidencia de los riesgos.»; el autor: «La voz dice que la producción subió en 1961.»; la voz de ch03 no dice ['Wittenoom'])
  - descarte D95 («El pueblo aborigen banjima reclama 1.500 millones de dólares australianos al Ejecutivo por la contaminación.»; el autor: «La voz dice los mil quinientos millones.»; la voz de ch07 no dice ['1.500'])

#### Reintento: los motivos que se le mandaron al autor

- T38 (ch02 beat 3) «SALIDA · 24 de septiembre, 1962»: spoiler: La vecina anterior dice que cuatro días después de la boda (20 de septiembre de 1962) ya estaban en el barco: es la misma fecha de salida. (ch02 [5])
- el beat 3 de ch02 es pico y quedó sin ficha

##### Reintento parcial: 1 vuelta(s)

#### Vuelta 1 · US$ 0.4013

- beats que podía cambiar: ch02 beat 3
- motivos:
  - T38 (ch02 beat 3) «SALIDA · 24 de septiembre, 1962»: spoiler: La vecina anterior dice que cuatro días después de la boda (20 de septiembre de 1962) ya estaban en el barco: es la misma fecha de salida. (ch02 [5])
  - el beat 3 de ch02 es pico y quedó sin ficha
- claves: (pico, ch02, 3); (spoiler, T38, ch02, 3, 1962)
- aplicados: ch02 beat 3 (ficha)

#### Cierre del reintento

- cerró por: **sin motivos** (después de 1 vuelta)

#### Descartados por el modelo

- D85 [voz_lo_dice]: La herida que no cerraba la cuenta la voz en ch01.
- T34 [voz_lo_dice]: El baile y su fecha los dice la voz.
- T37 [voz_lo_dice]: La fecha de la boda la dice la voz; va en el reloj.
- Q13 [voz_lo_dice]: La voz cuenta la amistad con Ramón y Milagros.
- D83 [otro]: Se priorizó el dato central del beat pico (T38); además la voz ya dice los ocho mil.
- Q14 [voz_lo_dice]: La voz cita la travesía de Calvo casi entera.
- T36 [voz_lo_dice]: La voz dice la llegada en agosto de 1962.
- T24 [voz_lo_dice]: La voz dice que CSR reclutaba en Europa desde 1950.
- Q27 [otro]: La voz cita casi todo; D02 suma más en ese beat.
- D03 [voz_lo_dice]: La voz dice que el pueblo y la pista se hicieron con relaves. — verificador: dicho: La voz dice que la pista y el pueblo entero se hicieron con lo que sobraba de la mina.
- D129 [voz_lo_dice]: La voz dice que los relaves cubrían carreteras y patios. — verificador: dicho: La voz dice que con los relaves se hicieron las carreteras, los patios y los espacios públicos.
- Q44 [voz_lo_dice]: La voz cita al antiguo trabajador.
- D82 [otro]: La distancia a Perth está en disputa entre las fuentes.
- D92 [voz_lo_dice]: La voz dice el dato central entero en ch03 idx19.
- Q45 [voz_lo_dice]: La voz cita la carta de Saint.
- Q46 [voz_lo_dice]: La voz cita que a Saint lo tildaron de alborotador.
- Q53 [voz_lo_dice]: La voz cita al defensor del empleador.
- T06 [voz_lo_dice]: La voz cuenta la compra de ABA en 1943.
- D19 [voz_lo_dice]: La voz cuenta los informes de 1944.
- T13 [voz_lo_dice]: La voz dice el diagnóstico de 1946. — verificador: dicho: La voz dice que en 1946 ya había un diagnóstico de asbestosis.
- D21 [voz_lo_dice]: La voz dice que la producción subió en 1961. — verificador: dicho: La voz dice que la producción subió en 1961, después de las advertencias.
- Q54 [voz_lo_dice]: La voz cita el acta de la Junta.
- T27 [otro]: La voz cuenta el recorte; D138 suma más en ese beat.
- D20 [voz_lo_dice]: La voz resume el documento oficial.
- T35 [voz_lo_dice]: La voz cuenta el caso de McNulty en 1962.
- Q49 [voz_lo_dice]: La voz cita a McNulty.
- Q16 [voz_lo_dice]: La voz cuenta la explosión del primer día.
- D104 [voz_lo_dice]: La voz dice las jornadas de dieciséis horas.
- T41 [voz_lo_dice]: El bautizo y la partida los dice la voz; la fecha va en el reloj.
- T40 [voz_lo_dice]: La voz cuenta el nacimiento en junio.
- T39 [voz_lo_dice]: La voz cuenta el nacimiento de John Patrick.
- D87 [voz_lo_dice]: La voz dice los diez meses.
- T49 [voz_lo_dice]: La voz cuenta el cierre por costos.
- D51 [otro]: Una sola ficha por beat; la indemnización de CSR muestra más la consecuencia.
- D93 [voz_lo_dice]: La voz dice el fallo del juez de 1988.
- T56 [voz_lo_dice]: La voz dice la fundación de la sociedad en 1979.
- T64 [voz_lo_dice]: La voz dice el diagnóstico y la muerte nueve meses después.
- D89 [voz_lo_dice]: La voz dice la edad y los nueve meses.
- D23 [spoiler]: Adelanta el recuento de muertos que la voz aborda en ch06.
- Q24 [voz_lo_dice]: La voz cita al policía.
- Q21 [voz_lo_dice]: La voz cita a Mercedes.
- Q33 [voz_lo_dice]: La voz cuenta lo que dice Markey.
- Q22 [otro]: Recortada, la cita no cabe en la oración ancla.
- Q03 [voz_lo_dice]: La voz cita la declaración de zona no apta.
- D10 [voz_lo_dice]: La voz cuenta el asbesto que baja hasta el Fortescue.
- T90 [voz_lo_dice]: La voz cuenta la nota de 2021.
- D59 [voz_lo_dice]: La voz cuenta el documento de 2016.
- Q07 [otro]: Una sola ficha por beat; se priorizó el dato central T80.
- D40 [otro]: La superficie oficial varía entre las fuentes y suma menos que el dato central.
- T98 [voz_lo_dice]: La voz cuenta el proceso de Gordon Legal.
- D95 [voz_lo_dice]: La voz dice los mil quinientos millones. — verificador: dicho: La voz menciona la reclamación de mil quinientos millones de dólares australianos por la tierra Banjima.
- D70 [voz_lo_dice]: La voz dice que el Estado no gastó en remediar.
- Q10 [voz_lo_dice]: La voz cita a Parker.
- T92 [voz_lo_dice]: La voz cuenta la visita de Orellana.
- T96 [voz_lo_dice]: La voz cuenta la muerte de Parker.
- Q34 [voz_lo_dice]: La voz cita al gobierno.
- D61 [otro]: Una sola ficha por beat; D69 suma más al cierre.

#### ⚠ Aviso de la verificación de la narración

⚠ la narración sigue contradiciendo el archivo en 1 punto(s): ch03 «El defensor del empleador tenía otra lectura: «El mero hecho» (Q53). Detalle en 01b_verificacion.md

- ch03 [15] «El defensor del empleador tenía otra lectura: «El mero hecho de que haya nubes de polvo no significa que ese polvo sea peligroso».»: Esa postura se presenta, por el orden del relato, como respuesta al diagnóstico de 1946 y anterior a 1948. · Q53 · «En el arbitraje de 1949, el defensor empresarial sostuvo que la compañía no admitía que el polvo fuera peligroso»


## Costo real por llamada

| llamada | tokens in | tokens out | US$ | s | intentos |
|---|---|---|---|---|---|
| verificador (1.ª pasada) ch01 | 65908 | 3500 | 0.3336 | 32.0 | 1 |
| verificador (1.ª pasada) ch02 | 66158 | 3895 | 0.3425 | 31.0 | 1 |
| verificador (1.ª pasada) ch03 | 67080 | 7100 | 0.4103 | 57.3 | 1 |
| verificador (1.ª pasada) ch04 | 66188 | 3853 | 0.3418 | 32.7 | 1 |
| verificador (1.ª pasada) ch05 | 66450 | 3995 | 0.3457 | 33.3 | 1 |
| verificador (1.ª pasada) ch06 | 66379 | 3514 | 0.3358 | 28.4 | 1 |
| verificador (1.ª pasada) ch07 | 66136 | 3324 | 0.3310 | 28.6 | 1 |
| re-verificación ch01 | 65782 | 2556 | 0.3142 | 23.9 | 1 |
| re-verificación ch03 | 66993 | 7340 | 0.4148 | 60.3 | 1 |
| re-verificación ch04 | 66181 | 3794 | 0.3406 | 32.7 | 1 |
| re-verificación ch06 | 66321 | 3090 | 0.3271 | 24.3 | 1 |
| re-verificación ch07 | 66125 | 3216 | 0.3288 | 27.2 | 1 |
| papel autor intento 1 | 88303 | 17659 | 0.7064 | 152.5 | — |
| papel autor vuelta 1 | 94705 | 1125 | 0.4013 | 13.6 | — |
| papel verificador 1 | 9685 | 1229 | 0.0633 | 10.7 | 1 |
| papel verificador 2 | 9384 | 1117 | 0.0599 | 8.9 | 1 |

| paso (`01_v3_costos.json`) | US$ | segundos |
|---|---|---|
| verificacion (verificador ×7 + re-verificación ×5 = 4.1663; 7 ediciones de oración en Fable 5.1 high = 0.2049) | 4.3712 | 165,2 |
| pantalla (papel) | 1.2309 | 187,8 |
| **total Etapa C** (alarma del handoff: 10) | **5.6021** | |

## Lo que queda abierto

1. **Decisión de Omar, antes de aprobar: la corrección borró la promesa del gancho y el re-gancho** (arriba). Opciones: (a) aceptar la narración así; (b) restaurar y reparar a mano solo «va a cerrar», «dos inspectores», etc. (copiar de `lab/hyperframes/f66/antes/` a `_steps/<topic>/` estos archivos: `01b_narracion_v3.json`, `01a_skeleton.json`, `01b_narration.json`, `01e_pantalla.json`, `.md`, `.raw.json`, y borrar `01b_verificacion.json`/`.md`; la narración vuelve a `c7badfbe…`); (c) otra tanda chica: para el código «v» un pedido que corrija y no saque, y rechazar la edición si sale una oración protegida (`recuerda_loop`, `promesa`) o si el párrafo pierde más que la oración marcada, y re-correr (≈ US$ 5,5). Mi recomendación: (c), porque el mismo borrado le va a pasar a cada video. El papel se re-escribe en cualquier caso que cambie la narración.
2. **«corregida ✔» engaña:** dice que la re-verificación no la marca, no que el texto siga bien; sacar la oración siempre da ✔ (la columna «después» dice «(oración sacada)»). **La PARADA y el `.md` del papel solo muestran el aviso de ch03 [15], no las 4 oraciones borradas:** quien apruebe desde la compuerta sin leer este reporte no las ve.
2b. Casos borde sin ejercer: si la re-verificación de un cap falla, `quedan` lleva el texto viejo de esa fila; `leer_quedan` no compara `01b_verificacion.json` contra el md5 de la narración, así que una narración regenerada sin verificar arrastraría un aviso viejo.
3. **La voz puede leer texto viejo:** `audio_manager._resolve_text_for_tts` usa `01b_narration_normalized.json` sin mirar su fecha, y el de Wittenoom es del 28-oct (anterior incluso al guion del 29). Después de aprobar hay que correr **`--from normalizer_gate`**, nunca `--from audio` (F62_REPORT Parte 2 decía `--from audio`, hoy está mal). `run_verificacion` no lo borra: no estaba pedido; ya era un problema antes de F66.
4. **24 «sin respaldo»** no se tratan (lista en la tabla): varios son escenas del guionista sin fuente («la foto es en blanco y negro», «el parto fue con fórceps»). Es credibilidad igual que los «contradice», sin dueño.
5. **1 corrida por cap:** F63 mostró 6 estables de 7; ch03 [31] y ch03 [15] salieron en esta sola corrida, así que una parte de lo que se edita o se avisa es varianza del modelo.
6. **`06_judge_narrative.json` quedó de la narración anterior** (`--verificar-narracion` no corre el juez). `run_guion_v4` sí se lo pasa final.
7. **El aviso del cap sin verificar** (si un cap falla dos veces) está solo en `01b_verificacion.md`, no en el papel: no pasó en esta corrida.
8. **PARADA:** el papel no está aprobado; voz y fotos no corrieron.

## Veredicto de revisor-handoff (íntegro)

**VEREDICTO: CUMPLE CON OBSERVACIONES.** El código y la corrida cumplen el handoff. El resultado sobre Wittenoom es malo, y el reporte lo cuenta casi con la gravedad correcta. Faltan DECISIONES y ESTADO_SESION.

Contrato: handoff md5 397a273a… (coincide). Revisé los commits con `git show`, sin tocar el working tree. Corrí test_module_f66 (23 verdes) y f64+f10+f27 (37 verdes), sin API.

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | SYSTEM_B md5 ce31cc51…; user_b reproduce el md5 del lab | OK | Armé el user_b de ch01 con la narración de f66/antes: 156.148 car., md5 9f2dfc97…, igual a `f63/b/verificador_ch01_1.json` (`user_md5`) |
| 2 | edit_sentences por defecto idéntico; `guard`/`cifras_ok` solo en verificación | OK | guion_v4.py:1232-1259: sin parámetros usa GUARD_ALL y los mismos mensajes. Los únicos llamadores son `reparar` (l.1382, sin parámetros) y fase1_5:544 (con ellos). test_b1 compara contra lexical_guard |
| 3 | Orden en run_guion_v4: particionar → verificación → pantalla → juez con la partición final | OK | fase1_5.py:656-662; test_b16 |
| 4 | Trabaja sobre 01b_narracion_v3 y ubica por texto | OK | `mp.cargar` lee 01b_narracion_v3; `_parrafo_de` usa ev.norm y el beat desempata. En producción `reparacion.parrafos` sigue intacto, salvo el párrafo 27 que ya difería por el acortado previo |
| 5 | Re-partición con los títulos del skeleton | OK | Títulos antes y después idénticos (verificado); `particion.titulos` pasó de «flash» a «los de la partición anterior» |
| 6 | Re-verifica solo los caps con texto cambiado | OK | Comparé f66/antes y despues: cambian ch01 (161→118), ch03 (523→489), ch04, ch06, ch07. ch02 y ch05 iguales, y el JSON dice `caps_cambiados` = [ch01, ch03, ch04, ch06, ch07] |
| 7 | Costos del reporte | OK | `01_v3_costos.json`: verificacion 4,3712 (165,2 s), pantalla 1,2309, total 5,6021. El raw da 7 llamadas de 1.ª pasada (2,4408) y 5 de re-verificación (1,7255), total 4,1663; cada tokens/US$/s coincide con la tabla. Las ediciones salen por resta: 0,2049 |
| 8 | Las 5 estables aparecen | OK | ch01[1], ch01[9], ch03[14], ch04[1], ch06[12], más ch07[9] y ch03[31]: 7 contradice |
| 9 | Aviso de ch03[15] al final del .md y en parada_del_papel | OK | Está en el `.md` de producción y en `etapa_c_run.log` (PARADA); `aviso_narracion` en el JSON del papel |
| 10 | Papel sin aprobar; prompts y versión sin cambios | OK | `01e_pantalla.json` sin clave de aprobación; prompt_md5 f2bfdf20…, m01e-7. El diff de m01e_pantalla solo agrega el aviso (9 líneas) y no toca PANTALLA_SYSTEM ni SYSTEM_V |
| 11 | Respaldos con el md5 de partida | OK | `antes/01b_narracion_v3.json` = c7badfbe…, igual a NARRACION_MD5 del lab. Los 10 archivos del handoff están en `antes/` |
| 12 | Nada de Wittenoom en el código; un commit por etapa; main intacta | OK | El grep de `+Wittenoom` en los `.py` fuera de lab/ dio vacío; 3 commits (A, B, C) |
| 13 | DECISIONES (línea «si quedan contradice, sigue con aviso» y la constante «1 corrida por cap») y `lab/ESTADO_SESION.md` | FALLA (pendiente) | DECISIONES.md no tiene línea F66 y ESTADO_SESION.md no cambió desde a9aa200. El handoff §1 y §4 y el CLAUDE.md los exigen |
| 14 | F66_REPORT con veredicto íntegro | PARCIAL | Existe (untracked); la sección del veredicto dice «(pendiente)», que es este paso |

**Las 4 interpretaciones declaradas**
- **`cifras_ok` con `fecha` (1):** razonable, pero va más allá de la tabla del handoff, que dice «texto de los ids». Lo cubre test_b7, y la corrida real nunca lo ejerció: ninguna edición puso 2022. Los nombres no se aceptan por ahí, y eso está testeado.
- **`shorten=None` en la re-partición (2):** aceptable. El texto ya viene acortado, y evita una llamada Gemini y un recorte no pedido. Cuesta la nota de partición vieja del skeleton, que está en `antes/`.
- **`parrafos` (3):** correcta. Solo alimenta `acortados_por_la_particion`; partir desde la reparación deshacería el acortado.
- **Juez no corre en `--verificar-narracion` (4):** coherente con el handoff. Pero `06_judge_narrative.json` queda de la narración anterior; el reporte lo declara en «abierto» 6.

**«Lo primero»: cotejado contra f66/antes y despues**
- Confirmado: 4 de 7 ediciones sacaron la oración entera (ch01[1], ch01[9], ch03[31], ch06[12]).
- Confirmado: ch04[1] pierde «y que alguien murió» y ch07[9] pierde «dos inspectores en 1944».
- Confirmado: ch03[14] queda en «un diagnóstico» y pierde «terroríficas».
- Confirmado: −104 palabras. Cap 1 161→118; cap 3 523→489; cap 6 297→278.
- Confirmado: «Lo que sobró de la mina… sigue donde lo dejaron» era la segunda mitad de `promesa_gancho`.
- Confirmado: la oración que abre L1 (ch01[1]) está borrada.
- Confirmado: la oración final del beat 6 (el re-gancho) está borrada, y el beat 6 es el de `recuerda_loop`.
- Confirmado: ninguna edición fue rechazada por la guardia.

**Observaciones**
1. Gravedad: el reporte la expone bien. Va primero, con cifras, lista lo perdido, no revierte, deja la decisión a Omar y recomienda (c). El titular («funcionó según el contrato») y el commit («7 ediciones aceptadas, 0 rechazadas») suenan a éxito. El resultado es que la tanda degradó el guion en el 100% de lo que tocó. Omar debería leerlo como falla de diseño de la corrección, no como éxito con un efecto lateral.
2. La narración dañada es la vigente en `data/` y el papel nuevo se generó sobre ella. Restaurar exige copiar los respaldos de `antes/` (`01b_narracion_v3`, `01a_skeleton`, `01b_narration`, `01e_pantalla.*`). El reporte lo sugiere pero no da el procedimiento.
3. Los artefactos que Omar lee solo muestran 1 aviso (ch03[15]). La PARADA y el `.md` del papel no mencionan las 4 oraciones borradas. `01b_verificacion.md` las marca «corregida ✔» con «después: (oración sacada)»; el reporte lo admite en «abierto» 2. Quien apruebe desde la compuerta sin leer F66_REPORT no ve el borrado.
4. Imprecisión menor: «el párrafo que `recuerda_loop` protege» se borró. En realidad se borró la última oración del párrafo, no el párrafo. Además `MEDIR_C.md` dice que la oración literal del `recuerda_loop` «antes NO está», porque el guionista la parafraseó («El año en que…» frente a «Un año después de que…»). La medición automática no respalda la pérdida del re-gancho. Se sostiene por lectura del texto, que verifiqué.
5. El caso ch03[31] el reporte lo llama «discutible», y estoy de acuerdo. La objeción del verificador era el año del caso, no el recién casado.
6. Si la re-verificación de un cap falla, la fila queda «corregida; la re-verificación falló ⚠» y pasa a `quedan` con el texto ya corregido, que no existe en la narración. Es un caso borde sin ejercer en la corrida real.
7. `leer_quedan` lee `01b_verificacion.json` sin comprobar su fecha ni el md5 de la narración. Si el archivo queda viejo respecto de una narración regenerada sin verificación, el aviso sería de texto desactualizado.

**Fuera de alcance:** `lab/hyperframes/f65/HANDOFF_F65b_qa_del_papel.md` entra en el commit A; es el handoff de F65b, lo anuncia el mensaje del commit y es inocuo. Stickers `lab/mapa/stickers/{guion,orquestador}.json` y los tests, esperados. No toqué nada (solo lectura; escribí copias temporales en el scratchpad).

**Riesgos que el contrato no cubre**
- Nada protege oraciones del `recuerda_loop` ni de la promesa del gancho frente a `edit_sentences`. La guardia mide lo que se agrega, no lo que se pierde, y `g4.bloqueantes` da 0→0. Esto se repite en cada video.
- La re-verificación no puede marcar lo que ya no está, así que borrar siempre da ✔. El verificador no mide la integridad narrativa (loops, promesa, duración: −35 s de voz).
- Con 1 corrida por cap hay varianza del verificador (ch03[31] y [15] salieron solo esta vez). Una parte de lo que se edita o avisa es ruido del modelo.

### Adenda de CC
- **Req. 13:** las dos líneas se agregaron a `DECISIONES.md` después de este veredicto, sin commitear: el archivo ya tenía líneas del analista sin commitear y no le mezclo las mías en un commit (quedan en el working tree). `lab/ESTADO_SESION.md` se actualizó en el commit de cierre.
- **Obs. 1, 2 y 4:** corregidos en el reporte después de este veredicto: el título ya dice que la corrección degradó el guion y que es una falla de diseño, «abierto» 1 trae el procedimiento de restauración, y «párrafo» pasó a «última oración del beat 6», con la nota de que la pérdida sale de leer el texto y no de `MEDIR_C`. El mensaje del commit `17f830e` ya no se puede cambiar; sí dice el daño.
- **Obs. 3:** es el punto que más me preocupa y no lo arreglé (no está en el handoff). El bloque «Para Omar» de ESTADO y `F65b_REPORT` dicen que no se apruebe antes de decidirlo. Queda dentro de la opción (c).
- **Obs. 6 y 7:** en «abierto» 2b.
