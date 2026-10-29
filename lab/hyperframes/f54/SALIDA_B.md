# F54 — Salida B (texto)

viejo = `lab/hyperframes/f54/antes/` (escaleta `f26-1`, guion `f25-1`) · nuevo = `data/scripts/_steps/123bbb64-9fca-4395-8bf4-57d60e219ef1/` (escaleta `f54-1`, guion `f54-2`).

## 1. Tabla A/B cap por cap

| cap | palabras v | n | años v | n | datos/min v | n | bloqueantes viejo | bloqueantes nuevo (tras la ronda única) |
|---|---|---|---|---|---|---|---|---|
| 1 | 86 | 168 | 1 | 2 | 0.0 | 0.9 | — | — |
| 2 | 302 | 263 | 3 | 3 | 2.4 | 3.3 | — | — |
| 3 | 350 | 368 | 6 | 11 | 1.2 | 2.0 | (d) fuera del caso (descartado en el pool): Defensor del empleador no iden | (d) fuera del caso (descartado en el pool): Defensor del empleador no iden; (h) pago no dicho: el beat 5 paga la pregunta del beat 3 con D21, que no e; (h) pago no dicho: el beat 5 paga el loop L2 con D21, que no está en el ca |
| 4 | 239 | 335 | 3 | 2 | 3.6 | 1.7 | — | — |
| 5 | 344 | 252 | 8 | 5 | 2.5 | 4.0 | — | — |
| 6 | 359 | 278 | 7 | 7 | 0.8 | 1.6 | — | (h) pago no dicho: el beat 11 paga la pregunta del beat 10 con D10, que no |
| 7 | 207 | 249 | 3 | 5 | 2.1 | 3.5 | (f) cierre no dicho: el dato central D42 del beat 14 (cierre) no está en e | — |
| **total** | 1887 | 1913 | 31 | 35 | | | 2 | 4 |

Guion nuevo: bloqueantes antes de la ronda única 4 → después 4 · PARADA del guion: True.

Bloqueantes del crudo nuevo (antes de reparar):

- cap 3 beat 5 (d): fuera del caso (descartado en el pool): Defensor del empleador no identificado — ««El mero hecho de que haya nubes de polvo no significa que ese polvo sea peligroso», dijo el defensor del empleador en m»
- cap 3 beat 5 (h): pago no dicho: el beat 5 paga la pregunta del beat 3 con D21, que no está en el cap 3
- cap 6 beat 11 (h): pago no dicho: el beat 11 paga la pregunta del beat 10 con D10, que no está en el cap 6
- cap 3 beat 5 (h): pago no dicho: el beat 5 paga el loop L2 con D21, que no está en el cap 3

## 2. Los dos cap 1, lado a lado

| viejo (f26-1 / f25-1) | nuevo (f54-1 / f54-2) |
|---|---|
| Un hombre joven posa para una foto con el pie envuelto en una venda blanca. Detrás, tierra roja y paredes de chapa. En el retrato de familia todos miran a cámara menos el pie: está vendado, y la herida que le hizo un trozo de amianto no cierra. El hombre se llama Daniel Écija y es minero. Vino de Madrid. Wittenoom, Australia Occidental, mil novecientos sesenta y dos. Para entender ese pie hay que volver a un baile en Madrid, un año antes de la foto. | Un hombre joven posa de pie para un retrato, con un pie envuelto en vendas. Vivió diez meses en el pueblo donde le tomaron esa foto y murió de esos diez meses casi treinta años después, en Madrid; había gente con cargo y con firma que sabía desde mil novecientos cuarenta y ocho lo que hacía ese polvo, y más de tres millones de toneladas siguen donde las dejaron. La foto es sepia, como las demás que hay sobre la mesa. Una mujer mayor las ordena, una por una. Cuenta que a su marido le cayó un trozo de amianto en el pie y que la herida no cerraba; por eso la venda. «Me pegué a mi marido, como una niña pequeña», dice la mujer que ordena las fotos. El hombre del pie vendado se llamaba Daniel Écija, minero emigrante español. Wittenoom, Australia Occidental, mil novecientos sesenta y dos. Para entender ese retrato hay que volver a Madrid, a un baile, un año antes de que lo tomaran. |

Promesa del gancho — viejo: «En el retrato de familia todos miran a cámara menos el pie: está vendado, y la herida que le hizo un trozo de amianto no cierra.» · nuevo: «Daniel Écija vivió diez meses en Wittenoom. Murió de eso casi treinta años después, en Madrid. Esta es la historia de quién sabía, desde mil novecientos cuarenta y ocho, lo que hacía ese polvo, y de por qué tres millones de toneladas siguen donde las dejaron.»

## 3. Loops declarados con sus pagos (escaleta nueva)

- **Loop 1** (L1): «¿Por qué un hombre que vivió diez meses en un pueblo del desierto muere de ese pueblo casi treinta años después y a medio mundo de distancia?» — se abre en el beat 1 (cap 1, D85) · se paga en el beat 9 (cap 5, D89: Si diez meses bastaron para él, ¿qué pasa con los que se quedaron años, y con los niños que se lo metían en la boca?)
- **Loop 2** (L2): «¿Qué sabía la empresa del polvo cuando fue a Europa a reclutar a estas familias?» — se abre en el beat 3 (cap 2, Q14) · se paga en el beat 5 (cap 3, D21: ¿Cómo se recluta gente en Europa para un lugar así, y qué se les cuenta?)

Beats con `paga` (4):
- beat 5 (cap 3, D21) paga la pregunta del beat 3: «¿De qué está hecho ese polvo que nadie había visto en esa cantidad?»
- beat 9 (cap 5, D89) paga la pregunta del beat 1: «¿Qué le pasó al hombre del pie vendado, y por qué una herida que no cierra importa en una historia sobre un pueblo borrado del mapa?»
- beat 11 (cap 6, D10) paga la pregunta del beat 10: «Si borrar el nombre es el fin del episodio, ¿qué pasa con el polvo que sigue ahí?»
- beat 12 (cap 7, T92) paga la pregunta del beat 11: «Si se sabe cómo encapsularlo y cuánto cuesta, ¿por qué no se ha hecho nunca?»

`recuerda_loop`: beat 5 · «A ese molino cubierto de polvo, a fines de mil novecientos sesenta y dos, iba a entrar un recién casado de Madrid que llevaba cuatro días de matrimonio cuando subió al barco.»

## 4. Los 7 títulos

| cap | viejo | nuevo |
|---|---|---|
| 1 | El pie que no cura | La herida que no cerró |
| 2 | El polvo de la tierra | Promesas y polvo |
| 3 | La verdad silenciada | Peligro silenciado |
| 4 | Jugar con veneno | El polvo lo cubría todo |
| 5 | El tiempo de matar | La factura del tiempo |
| 6 | Borrar el problema | Un pueblo, polvo eterno |
| 7 | Una herida abierta | El costo sin fin |

## 5. El papel (01e_pantalla.md, nuevo)

# Guion de pantalla en papel — 123bbb64-9fca-4395-8bf4-57d60e219ef1

`m01e_pantalla` m01e-6 (md5 del prompt `3b98aef1d8595124967ac7a85b75bab7`) · claude-sonnet-5-5 medium · 2 intento(s) · US$ 0.5103 · tokens de entrada 52702

Segundos por palabra 0.34 (mediana de 347 oraciones de 16 caps del narrador N9Z5MLTIaHFLflaLtbDi) · tope US$ 1.0 (respaldo (el perfil no trae costos.m01e_tope_usd)) · intento 1: in 52702 · out 25700 · US$ 0.3624 · intento 2: in 58538 · out 3082 · US$ 0.1479

Totales: 13 fichas · 9 sellos · 3 relojes · 23 descartados

## ch01 — La herida que no cerró

- beat 1 · gancho · PICO · ficha **D90** [normal] «MUERTOS POR WITTENOOM · Se calcula que superan los 4.000» en [1] sobre «polvo» (53/90 car.) · respaldo: «puede ser superior a 4.000» · año — / relato 1948 · aporta: La voz habla de un hombre y de las toneladas que quedan, pero nunca dice cuánta gente murió por el pueblo. · sello **MEMORIA** en [3]
- relojes: —

## ch02 — Promesas y polvo

- beat 2 · planteo · ficha **D83** [normal] «EL PLAN MIGRATORIO · Se llamó Operación Canguro, desde 1958» en [3] sobre «acuerdo» (56/90 car.) · respaldo: «iniciado en 1958, llamado Operación Canguro» · año 1958 / relato 1950 · juzgado por el autor: otro hecho {'spoiler': ['1958']} · aporta: La voz dice que cruzaron ocho mil españoles, pero no cómo se llamaba el acuerdo ni cuándo empezó. · sello **SILENCIO** en [8]
- beat 3 · planteo · PICO · ficha **D82** [normal] «AISLADO DEL MUNDO · A unos 1.400 kilómetros de Perth» en [15] sobre «desierto» (49/90 car.) · respaldo: «a unos 1.400 kilómetros de Perth» · año — / relato 1950 · aporta: Pone una distancia al aislamiento: la voz solo dice 'en medio del desierto'. · sello **AMENAZA** en [20]
- relojes: 16 SEP 1961 en [0], 20 SEP 1962 en [2]

## ch03 — Peligro silenciado

- beat 4 · escalada · PICO · ficha **Q45** [cita] «SU PRONÓSTICO · la cosecha más rica y letal de casos de asbestosis» — Eric Saint (autor: modelo) en [5] sobre «carta» (no está en la oración) (78/90 car.) · respaldo: «la cosecha más rica y letal de casos de asbestosis en la literatura mundial» · año 1948 / relato 1948 · aporta: Lo que Saint predijo en su advertencia. La voz solo cita cómo lo trataron después. · sello **ALARMA** en [3]
- beat 5 · giro · ficha **D78** [normal] «YA SE SABÍA · A mediados de la década de 1950 se descubrió que el asbesto da cáncer» en [14] sobre «mesotelioma» (80/90 car.) · respaldo: «A mediados de la década de 1950, los investigadores descubrieron los peligros cancerígenos del mineral de asbesto.» · año 1955 / relato 1962 · aporta: La voz cuenta el primer mesotelioma de 1962, pero no que el riesgo de cáncer se conocía desde los años 50. · sello **INMINENTE** en [16]
- relojes: —

## ch04 — El polvo lo cubría todo

- beat 6 · escalada · PICO · ficha **Q19** [cita] «LO QUE NO SABÍAN · Nadie nos avisó de nada» — Víctor Calvo (autor: modelo) en [5] sobre «deshilachaban» (56/90 car.) · respaldo: «Nadie nos avisó de nada.» · año — / relato 1962 · aporta: Cierra el testimonio de Calvo con la frase que la voz no dice: a los niños nadie les advirtió. · sello **CALMA** en [8]
- beat 7 · escalada · ficha **D88** [normal] «SE QUEDARON MÁS · La familia de Ramón vivió allí unos dos años y medio» en [14] sobre «Ramón» (67/90 car.) · respaldo: «vivió en Wittenoom unos dos años y medio» · año — / relato 1965 · juzgado por el autor: otro hecho {'no_dicho': ['Ramón']} · aporta: Cuánto se quedaron los amigos de los Écija, para contrastar con los diez meses que la voz cuenta después. · sello —
- relojes: 7 JUL 1963 en [18]

## ch05 — La factura del tiempo

- beat 8 · giro · ficha **D51** [normal] «LO QUE SACÓ LA MINA · 131.000 toneladas de amianto azul» en [1] sobre «anunció» (52/86 car.) · respaldo: «La mina de Wittenoom produjo 131.000 toneladas de crocidolita» · año 1966 / relato 1966 · aporta: Pone cifra a lo que produjo la mina que se cerraba; la voz solo dice el motivo y el número de personas. · sello —
- beat 9 · pico · PICO · ficha **D23** [papel] «ANTES QUE DANIEL · Para 1989, más de 500 antiguos trabajadores y residentes habían muerto» en [15] sobre «cuenta» (86/90 car.) · respaldo: «Para 1989, más de 500 antiguos trabajadores y residentes de Wittenoom habían muerto» · año 1989 / relato 1991 · aporta: Muestra que Daniel no fue el primero: cuando murió ya había más de 500 muertos documentados. La voz no lo dice. · sello **COLAPSO** en [19]
- relojes: —

## ch06 — Un pueblo, polvo eterno

- beat 10 · respiro · ficha **D26** [normal] «EL ÁREA CERRADA · El sitio contaminado más grande del hemisferio sur» en [6] sobre «área» (65/86 car.) · respaldo: «sitio contaminado más grande del hemisferio sur» · año — / relato 2006 · aporta: Pone tamaño a lo que las barricadas encierran: la voz solo dice que el área no es segura. · sello **AVISO** en [8]
- beat 11 · revelacion · PICO · ficha **D94** [normal] «LO QUE PAGÓ CSR · 18,3 millones de dólares a 200 afectados» en [13] sobre «propiedad» (55/90 car.) · respaldo: «la empresa CSR pagó 18,3 millones de dólares australianos en indemnizaciones a 200 afectados» · año 1989 / relato 2006 · aporta: La voz habla de quién quedó con los relaves, pero no de lo que pagó la empresa por los enfermos. · sello **RABIA** en [16]
- relojes: —

## ch07 — El costo sin fin

- beat 12 · consecuencia · PICO · ficha **T86** [normal] «LOS MÁS AFECTADOS · Banjima: la mayor incidencia de cáncer por asbesto per cápita del mundo» en [6] sobre «Banjima» (88/90 car.) · respaldo: «el pueblo Banjima sufre la mayor incidencia per cápita de cáncer por asbesto del mundo» · año 2016 / relato 2026 · aporta: Dice cuánto ha golpeado la enfermedad a los Banjima, algo que la voz no cuenta. · sello —
- beat 13 · cierre · ficha **D109** [normal] «CONTADOS EN 1986 · 94 mesoteliomas en 6912 extrabajadores» en [10] sobre «escáner» (54/71 car.) · respaldo: «Para finales de 1986, se habían registrado 94 casos de mesotelioma, 141 de cáncer de pulmón y 356 reclamos por asbestosis en una cohorte de 6912 antiguos trabajadores de Wittenoom» · año 1986 / relato 2026 · aporta: Pone cifra a los casos ya registrados entre los trabajadores, algo que la voz no dice al hablar de los controles médicos. · sello —
- relojes: —

## Lo que cayó

- (nada)

## Reintento: los motivos que se le mandaron al autor

- Q02 (ch06 beat 10) «LA ADVERTENCIA · desaconseja firmemente TODOS los viajes»: cita_sin_fecha: cita sin fecha: su autor («State Government», Gobierno estatal) no aparece en la oración [6] ni en sus vecinas
- D83 (ch02 beat 2, oración [3]) «EL PLAN MIGRATORIO · Se llamó Operación Canguro, desde 1958»: la voz dice «1958» en una oración posterior en ch03 [12] («En mil novecientos cincuenta y ocho, otro inspector resumió la mina en una palabra: una tragedia.»); ¿es el mismo hecho? si no, mantenelo
- D88 (ch04 beat 7, oración [14]) «SE QUEDARON MÁS · La familia de Ramón vivió allí unos dos años y medio»: la voz dice «Ramón» en la oración ancla o en una vecina en ch04 [14] («Tres meses antes, en marzo, Milagros Barroso había dado a luz en ese mismo pueblo a John Patrick; María recuerda que ella y Daniel se hicieron íntimos amigos de Milagros y de Ramón de Juan, que hacía jornadas de dieciséis horas.»); ¿es el mismo hecho? si no, mantenelo
- Q25: dijiste que la voz lo dice («La voz cita esa frase de María en la oración 5 del capítulo 1.»); la voz de ch01 no dice «2» («Me pegué a mi marido, como una niña pequeña. Pero estaba orgullosa. Me había enamorado de ese hombre y confiaba en el futuro… aunque estuviera tan lejos. En España no teníamos nada, ninguno de los dos.»): vuelve a ser candidato
- D28: dijiste que la voz lo dice («La voz cuenta las demoliciones y los cierres entre 1986 y 1992.»); la voz de ch06 no dice «Wittenoom» («Entre 1986 y 1992 se demolieron casas y edificios y se cerraron la escuela, el puesto de enfermería y la comisaría en Wittenoom.»): vuelve a ser candidato
- D95: dijiste que la voz lo dice («La voz dice los 1.500 millones del reclamo.»); la voz de ch07 no dice «1.500» («El pueblo aborigen banjima reclama 1.500 millones de dólares australianos al Ejecutivo por la contaminación.»): vuelve a ser candidato
- el beat 11 de ch06 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D23 («Recuento oficial de muertes hasta 1989 (más de 500): documento, no voz.»), D94 («Acuerdo de indemnización de CSR de 1989, 18,3 millones a 200 afectados: cifra de archivo.»)
- el beat 13 de ch07 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D109 («Cohorte de 6.912 trabajadores y 94 mesoteliomas hasta 1986: dato de estudio, va a pantalla sobre los controles médicos.»)

### Preguntas y respuesta del autor

- D83 {'spoiler': ['1958']}: la mantuvo en ch02 beat 2 [3]: otro hecho
- D88 {'no_dicho': ['Ramón']}: la mantuvo en ch04 beat 7 [14]: otro hecho

### Reintento parcial: 1 vuelta(s)

#### Vuelta 1 · US$ 0.1479

- beats que podía cambiar: ch02 beat 2, ch04 beat 7, ch06 beat 10, ch06 beat 11, ch07 beat 13
- motivos:
  - Q02 (ch06 beat 10) «LA ADVERTENCIA · desaconseja firmemente TODOS los viajes»: cita_sin_fecha: cita sin fecha: su autor («State Government», Gobierno estatal) no aparece en la oración [6] ni en sus vecinas
  - D83 (ch02 beat 2, oración [3]) «EL PLAN MIGRATORIO · Se llamó Operación Canguro, desde 1958»: la voz dice «1958» en una oración posterior en ch03 [12] («En mil novecientos cincuenta y ocho, otro inspector resumió la mina en una palabra: una tragedia.»); ¿es el mismo hecho? si no, mantenelo
  - D88 (ch04 beat 7, oración [14]) «SE QUEDARON MÁS · La familia de Ramón vivió allí unos dos años y medio»: la voz dice «Ramón» en la oración ancla o en una vecina en ch04 [14] («Tres meses antes, en marzo, Milagros Barroso había dado a luz en ese mismo pueblo a John Patrick; María recuerda que ella y Daniel se hicieron íntimos amigos de Milagros y de Ramón de Juan, que hacía jornadas de dieciséis horas.»); ¿es el mismo hecho? si no, mantenelo
  - Q25: dijiste que la voz lo dice («La voz cita esa frase de María en la oración 5 del capítulo 1.»); la voz de ch01 no dice «2» («Me pegué a mi marido, como una niña pequeña. Pero estaba orgullosa. Me había enamorado de ese hombre y confiaba en el futuro… aunque estuviera tan lejos. En España no teníamos nada, ninguno de los dos.»): vuelve a ser candidato
  - D28: dijiste que la voz lo dice («La voz cuenta las demoliciones y los cierres entre 1986 y 1992.»); la voz de ch06 no dice «Wittenoom» («Entre 1986 y 1992 se demolieron casas y edificios y se cerraron la escuela, el puesto de enfermería y la comisaría en Wittenoom.»): vuelve a ser candidato
  - D95: dijiste que la voz lo dice («La voz dice los 1.500 millones del reclamo.»); la voz de ch07 no dice «1.500» («El pueblo aborigen banjima reclama 1.500 millones de dólares australianos al Ejecutivo por la contaminación.»): vuelve a ser candidato
  - el beat 11 de ch06 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D23 («Recuento oficial de muertes hasta 1989 (más de 500): documento, no voz.»), D94 («Acuerdo de indemnización de CSR de 1989, 18,3 millones a 200 afectados: cifra de archivo.»)
  - el beat 13 de ch07 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D109 («Cohorte de 6.912 trabajadores y 94 mesoteliomas hasta 1986: dato de estudio, va a pantalla sobre los controles médicos.»)
- aplicados: ch06 beat 10 (ficha), ch06 beat 11 (ficha), ch07 beat 13 (ficha)

### Motivos sin beat (no hubo reintento)

- Q25: dijiste que la voz lo dice («La voz cita esa frase de María en la oración 5 del capítulo 1.»); la voz de ch01 no dice «2» («Me pegué a mi marido, como una niña pequeña. Pero estaba orgullosa. Me había enamorado de ese hombre y confiaba en el futuro… aunque estuviera tan lejos. En España no teníamos nada, ninguno de los dos.»): vuelve a ser candidato
- D28: dijiste que la voz lo dice («La voz cuenta las demoliciones y los cierres entre 1986 y 1992.»); la voz de ch06 no dice «Wittenoom» («Entre 1986 y 1992 se demolieron casas y edificios y se cerraron la escuela, el puesto de enfermería y la comisaría en Wittenoom.»): vuelve a ser candidato
- D95: dijiste que la voz lo dice («La voz dice los 1.500 millones del reclamo.»); la voz de ch07 no dice «1.500» («El pueblo aborigen banjima reclama 1.500 millones de dólares australianos al Ejecutivo por la contaminación.»): vuelve a ser candidato

## Cierre del reintento

- cerró por: **sin beat** (después de 1 vuelta)
- cortado al cerrar, sin preguntarle al autor: (nada)

## Descartados por el modelo

- D85 [otro]: Dato central del gancho que no figura en el archivo; se usó D90, que la voz no dice.
- Q25 [voz_lo_dice]: La voz cita esa frase de María en la oración 5 del capítulo 1. — **falso: la voz no dice ['2']**
- T34 [voz_lo_dice]: La voz cuenta el baile del 16 de septiembre de 1961.
- Q13 [spoiler]: Adelanta la amistad con Milagros y Ramón, que la voz cuenta en el capítulo 4.
- Q14 [voz_lo_dice]: La voz cita la travesía de Calvo casi completa.
- Q15 [voz_lo_dice]: La voz cuenta el avión, la tierra roja y el polvo.
- D92 [voz_lo_dice]: La voz dice que Saint advirtió por escrito en 1948.
- D21 [voz_lo_dice]: La voz dice que en 1961 la producción aumentó; la ficha solo repetiría eso.
- Q44 [voz_lo_dice]: La voz cita la frase de los relaves en la escuela.
- T41 [voz_lo_dice]: La voz cuenta el bautizo del 7 de julio de 1963 y la partida.
- T49 [voz_lo_dice]: La voz ya dice que la razón fue económica; se prefirió el dato de producción.
- D89 [voz_lo_dice]: La voz dice nueve meses, cincuenta y cinco años y la muerte en Madrid.
- Q23 [otro]: La voz cita su primera frase y no cabía una ficha de cita en la oración libre.
- D28 [voz_lo_dice]: La voz cuenta las demoliciones y los cierres entre 1986 y 1992. — **falso: la voz no dice ['Wittenoom']**
- Q07 [voz_lo_dice]: La voz cita 'el fin de un período oscuro'.
- D58 [otro]: Cifra de costo válida, pero en el beat 11 se prefirió D146.
- D10 [otro]: Dato central del beat 11 que no figura en el archivo.
- T92 [voz_lo_dice]: La voz cuenta la visita de Orellana en 2023.
- D95 [voz_lo_dice]: La voz dice los 1.500 millones del reclamo. — **falso: la voz no dice ['1.500']**
- Q24 [voz_lo_dice]: La voz cita la frase del policía.
- D109 [otro]: Se prefirió D110, que sugiere mejor la escala.
- D87 [voz_lo_dice]: La voz dice 'diez meses en total'.
- D56 [spoiler]: Introduce a los aborígenes que usan las gargantas antes de que la voz presente a los Banjima.
