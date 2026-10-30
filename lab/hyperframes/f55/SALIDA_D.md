# F55 — Salida D (texto)

F54 = `lab/hyperframes/f55/antes/` (escaleta `f54-1`, guion `f54-2`, pool de 58 citas) · F55 = `_steps/123bbb64-9fca-4395-8bf4-57d60e219ef1/` regenerado (escaleta `f55-1`, guion `f54-2`, pool de 50). Corrida combinada a propósito (detector + dedupe + promesa): la tabla no atribuye diferencias a una sola variable.

## 1. Tabla A/B cap por cap

| cap | palabras F54 | F55 | años F54 | F55 | datos/min F54 | F55 | bloqueantes F54 (tras la ronda) | bloqueantes F55 (tras la ronda) |
|---|---|---|---|---|---|---|---|---|
| 1 | 168 | 161 | 2 | 1 | 0.9 | 0.9 | — | — |
| 2 | 263 | 220 | 3 | 4 | 3.3 | 3.9 | — | — |
| 3 | 368 | 433 | 11 | 5 | 2.0 | 2.0 | (d) fuera del caso (descartado en el pool): Defensor del emplead; (h) pago no dicho: el beat 5 paga la pregunta del beat 3 con D21; (h) pago no dicho: el beat 5 paga el loop L2 con D21, que no est | (a) entre comillas, pero no es una cita del pool: «Aterrizamos e; (d) fuera del caso (descartado en el pool): El avión era pequeño; (d) fuera del caso (descartado en el pool): Defensor del emplead |
| 4 | 335 | 322 | 2 | 4 | 1.7 | 2.7 | — | — |
| 5 | 252 | 292 | 5 | 7 | 4.0 | 3.9 | — | — |
| 6 | 278 | 297 | 7 | 4 | 1.6 | 3.4 | (h) pago no dicho: el beat 11 paga la pregunta del beat 10 con D | — |
| 7 | 249 | 210 | 5 | 6 | 3.5 | 2.7 | — | — |
| **total** | 1913 | 1935 | 35 | 31 | | | 4 | 3 |

Quién vio los bloqueantes del nuevo: código (f/h con `regla_dicho`) → lo que quedó arriba; Sonnet confirmó 0:  · verificador: 0 llamada(s), 0 caché, US$ 0.0.
Bloqueantes del crudo nuevo antes de la ronda única: 4 → después 3; PARADA del guion: True.

- (crudo) cap 3 beat 4 (a): entre comillas, pero no es una cita del pool: «Aterrizamos en una pista en medio de una tierra muy muy roja…»
- (crudo) cap 3 beat 4 (d): fuera del caso (descartado en el pool): El avión era pequeño, de hélices, y se movía muchísimo. Aterrizamos en una pista
- (crudo) cap 3 beat 5 (d): fuera del caso (descartado en el pool): Defensor del empleador no identificado
- (crudo) cap 6 beat 11 (a): entre comillas, pero no es una cita del pool: «Hay hijos de funcionarios que trabajaban en el pueblo, como …»

## 2. La promesa (escaleta) y la oración 2 del cap 1 (guion)

| | F54 | F55 |
|---|---|---|
| promesa_gancho | Daniel Écija vivió diez meses en Wittenoom. Murió de eso casi treinta años después, en Madrid. Esta es la historia de quién sabía, desde mil novecientos cuarenta y ocho, lo que hacía ese polvo, y de por qué tres millones de toneladas siguen donde las dejaron. | Un minero español vivió diez meses en un pueblo construido con polvo de asbesto azul y tardó casi treinta años en morir de eso; el pueblo ya no existe en los mapas, pero tres millones de toneladas de relaves siguen donde las dejaron. |
| oraciones de la promesa | 3 | 1 (métrica `promesa_oraciones`: 1) |
| oración 2 del cap 1 | Vivió diez meses en el pueblo donde le tomaron esa foto y murió de esos diez meses casi treinta años después, en Madrid; había gente con cargo y con firma que sabía desde mil novecientos cuarenta y ocho lo que hacía ese polvo, y más de tres millones de toneladas siguen donde las dejaron. | Ese pie va a cerrar; lo que respira mientras espera que cierre va a tardar casi treinta años en matarlo, y lo va a alcanzar a miles de kilómetros de aquí. |

### Los dos cap 1 enteros

| F54 | F55 |
|---|---|
| Un hombre joven posa de pie para un retrato, con un pie envuelto en vendas. Vivió diez meses en el pueblo donde le tomaron esa foto y murió de esos diez meses casi treinta años después, en Madrid; había gente con cargo y con firma que sabía desde mil novecientos cuarenta y ocho lo que hacía ese polvo, y más de tres millones de toneladas siguen donde las dejaron. La foto es sepia, como las demás que hay sobre la mesa. Una mujer mayor las ordena, una por una. Cuenta que a su marido le cayó un trozo de amianto en el pie y que la herida no cerraba; por eso la venda. «Me pegué a mi marido, como una niña pequeña», dice la mujer que ordena las fotos. El hombre del pie vendado se llamaba Daniel Écija, minero emigrante español. Wittenoom, Australia Occidental, mil novecientos sesenta y dos. Para entender ese retrato hay que volver a Madrid, a un baile, un año antes de que lo tomaran. | Un hombre joven posa para un retrato con el pie vendado. Ese pie va a cerrar; lo que respira mientras espera que cierre va a tardar casi treinta años en matarlo, y lo va a alcanzar a miles de kilómetros de aquí. La foto es en blanco y negro. La familia que la guarda cuenta que le cayó encima un trozo de amianto y que la herida no cerraba. Una herida hecha por un pedazo de mineral que no cierra. El hombre se llama Daniel Écija, es minero, y llegó de Madrid hace unos meses. Wittenoom, Australia Occidental, 1963.  Esa foto se tomó en un pueblo que hoy no figura en ningún mapa. Arrancaron las señales de la carretera y borraron el nombre. Lo que sobró de la mina, en cambio, sigue donde lo dejaron. Pero antes de que lo borraran, alguien tuvo que llevar a ese hombre hasta allí. Dos años antes de la foto, en Madrid, hubo un baile. |

## 3. Loops declarados con sus pagos (escaleta F55), leídos con `evidence.regla_dicho`

- **Loop 1** (L1): «¿Qué le hizo Wittenoom a Daniel en diez meses, si el pueblo ya estaba a miles de kilómetros cuando lo alcanzó?» — se abre en el beat 1 (cap 1, D85: A2) · se paga en el beat 10 (cap 5, T64: ancla)
- **Loop 2** (L2): «¿Quién sabía que el polvo mataba, desde cuándo, y quién va a limpiar lo que quedó?» — se abre en el beat 5 (cap 3, D92: A1) · se paga en el beat 13 (cap 7, T98: ancla)

Beats con `paga` (2):
- beat 10 (cap 5, T64: ancla) paga la pregunta del beat 1: «¿Por qué una herida hecha por un pedazo de mineral no cierra? ¿Qué hay en ese polvo?»
- beat 13 (cap 7, T98: ancla) paga la pregunta del beat 5: «Si en 1944 y 1948 ya estaba escrito, ¿quién decidió seguir?»

`recuerda_loop`: beat 6 · «Un año después de que McNulty escribiera ese primer caso, un recién casado de Madrid se bajaba de un avión en esa misma pista de polvo.»

## 4. Los 7 títulos

| cap | F54 | F55 |
|---|---|---|
| 1 | La herida que no cerró | Herida que no cierra |
| 2 | Promesas y polvo | Un viaje incierto |
| 3 | Peligro silenciado | El aire que respiran |
| 4 | El polvo lo cubría todo | Infancia entre fibras |
| 5 | La factura del tiempo | Un mal oculto |
| 6 | Un pueblo, polvo eterno | El rastro persiste |
| 7 | El costo sin fin | La herida abierta |

## 5. Medida de retención por código (`lab/hyperframes/f54/medida_retencion.py`): F54 | F55

| ingrediente | viejo | nuevo |
|---|---|---|
| segundos hasta la primera apuesta | 550.0 s (cap 5, loop principal (D89)) | 545.4 s (cap 5, loop principal (T64)) |
| loops abiertos / pagados | 2 declarado(s) · loop L1 (D89): pagado; loop L2 (D21): pagado, en la primera oración del cap; beat 5 paga (D21): pagado, en la primera oración del cap; beat 9 paga (D89): pagado; beat 11 paga (D10): NO pagado; beat 12 paga (T92): pagado | 2 declarado(s) · loop L1 (T64): pagado; loop L2 (T98): pagado; beat 10 paga (T64): pagado; beat 13 paga (T98): pagado |
| re-gancho | sí (cap 3, min 5.33, parecido 1.0) | declarado pero no dicho (cap 3, min 3.97, parecido 0.36) |
| el cierre vuelve a la imagen del gancho | sí (Q24 en el cap 7) | sí (T98 en el cap 7) |

| cap | palabras v | n | años v | n | datos/min v | n |
|---|---|---|---|---|---|---|
| 1 | 168 | 161 | 2 | 1 | 0.9 | 0.9 |
| 2 | 263 | 220 | 3 | 4 | 3.3 | 3.9 |
| 3 | 368 | 433 | 11 | 5 | 2.0 | 2.0 |
| 4 | 335 | 322 | 2 | 4 | 1.7 | 2.7 |
| 5 | 252 | 292 | 5 | 7 | 4.0 | 3.9 |
| 6 | 278 | 297 | 7 | 4 | 1.6 | 3.4 |
| 7 | 249 | 210 | 5 | 6 | 3.5 | 2.7 |


## 6. `grep` de los 8 ids descartados en `_steps/<topic>/` regenerado

| archivo | apariciones fuera de `_descartados` | dónde |
|---|---|---|
| (ninguno) | 0 | — |

**Total fuera de `_descartados` y de `ficha_caso.json`: 0** (debe dar 0). `ficha_caso.json` en disco sigue con sus 36 apariciones (no se reescribe; `load` las remapea en memoria).

## 7. El papel (01e_pantalla.md, F55)

# Guion de pantalla en papel — 123bbb64-9fca-4395-8bf4-57d60e219ef1

`m01e_pantalla` m01e-6 (md5 del prompt `3b98aef1d8595124967ac7a85b75bab7`) · claude-sonnet-5-5 medium · 3 intento(s) · US$ 0.6279 · tokens de entrada 51320

Segundos por palabra 0.34 (mediana de 347 oraciones de 16 caps del narrador N9Z5MLTIaHFLflaLtbDi) · tope US$ 1.0 (respaldo (el perfil no trae costos.m01e_tope_usd)) · intento 1: in 51320 · out 23746 · US$ 0.3401 · intento 2: in 59781 · out 4826 · US$ 0.1678 · intento 3: in 58827 · out 232 · US$ 0.1200

Totales: 13 fichas · 6 sellos · 3 relojes · 64 descartados

## ch01 — Herida que no cierra

- beat 1 · gancho · PICO · ficha **D79** [normal] «LOS MUERTOS DE WITTENOOM · Más de 2000 mineros y vecinos murieron» en [7] sobre «pueblo» (62/71 car.) · respaldo: «Más de 2000 antiguos trabajadores de la mina y residentes de Wittenoom han muerto por enfermedades relacionadas con el asbesto.» · año — / relato 1963 · juzgado por el autor: otro hecho {'no_dicho': ['2000'], 'spoiler': ['2000']} · aporta: Pone la escala de muertes del pueblo, que la voz no dice en ningún momento del video. · sello **SILENCIO** en [8]
- relojes: —

## ch02 — Un viaje incierto

- beat 2 · planteo · ficha **Q25** [cita] «LO QUE DEJABAN · En España no teníamos nada» — María Bernal (autor: modelo) en [2] sobre «confiaba» (57/90 car.) · respaldo: «En España no teníamos nada, ninguno de los dos.» · año — / relato 1961 · aporta: Explica por qué se fueron: la pareja no tenía nada en España. La voz solo cita la otra parte de lo que dice ella. · sello —
- beat 3 · planteo · PICO · ficha **D105** [normal] «SU ÚNICO SUPERMERCADO · Un camión con víveres cada 15 días» en [17] sobre «tierra» (55/71 car.) · respaldo: «Un camión traía suministros al único supermercado de Wittenoom cada 15 días.» · año — / relato 1962 · aporta: Muestra el aislamiento del destino con un detalle cotidiano que la voz no cuenta. · sello —
- relojes: 16 SEP 1961 en [0], 20 SEP 1962 en [4]

## ch03 — El aire que respiran

- beat 4 · planteo · ficha **D82** [normal] «AISLADO · A unos 1.400 kilómetros de Perth» en [1] sobre «Pilbara» (39/40 car.) · respaldo: «a unos 1.400 kilómetros de Perth» · año — / relato 1962 · aporta: Da la distancia a la ciudad más cercana. La voz solo nombra el desierto. · sello —
- beat 5 · escalada · PICO · ficha **D01** [normal] «LO QUE SE SACÓ DE LA TIERRA · Más de 150.000 toneladas de asbesto» en [12] sobre «mina» (62/90 car.) · respaldo: «Se extrajeron comercialmente aproximadamente 150.000 toneladas de asbesto de tres minas entre 1937 y 1966.» · año 1937 / relato 1943 · aporta: Pone en cifra cuánto asbesto salió de las minas; la voz no da ninguna cantidad de producción en este capítulo. · sello **AVISO** en [16]
- beat 6 · giro · ficha **T25** [normal] «LA CIENCIA YA LO SABÍA · En 1955 ya se sabía que daba cáncer» en [26] sobre «polvo» (57/90 car.) · respaldo: «Investigadores descubrieron los peligros cancerígenos del asbesto. (fecha 1955)» · año 1955 / relato 1957 · aporta: Pone fecha a cuándo la ciencia advirtió del cáncer, antes de recortar el pago por el polvo. La voz no lo dice. · sello —
- relojes: —

## ch04 — Infancia entre fibras

- beat 7 · escalada · PICO · ficha **Q19** [cita] «SIN AVISO · Nadie nos avisó de nada» — Víctor Calvo (autor: modelo) en [13] sobre «miedo» (49/51 car.) · respaldo: «Nadie nos avisó de nada.» · año — / relato 1962 · aporta: La frase final del testimonio de Calvo, que la voz omite: a los chicos nadie les advirtió. · sello —
- beat 8 · giro · ficha **D102** [normal] «AQUEL BEBÉ, HOY · 63 años y productor de televisión» en [17] sobre «Daniel» (48/51 car.) · respaldo: «tiene 63 años y es un conocido productor de televisión en España.» · año — / relato 1963 · aporta: Cuenta qué fue del bebé que nació en el pueblo. La voz no lo dice. · sello **CALMA** en [22]
- relojes: 7 JUL 1963 en [19]

## ch05 — Un mal oculto

- beat 9 · escalada · ficha **D51** [normal] «LO QUE SACÓ LA MINA · 131.000 toneladas de amianto azul» en [1] sobre «cierre» (52/71 car.) · respaldo: «La mina de Wittenoom produjo 131.000 toneladas de crocidolita, de las cuales más de 100.000 toneladas fueron exportadas.» · año 1966 / relato 1966 · aporta: Pone en cifra lo que produjo la mina hasta el cierre. La voz solo habla de las razones del anuncio. · sello —
- beat 10 · pico · PICO · ficha **D23** [papel] «YA HABÍAN MUERTO, 1989 · Más de 500 mineros y vecinos» en [12] sobre «mesotelioma» (50/76 car.) · respaldo: «Para 1989, más de 500 antiguos trabajadores y residentes de Wittenoom habían muerto por infecciones relacionadas con el asbesto.» · año 1989 / relato 1991 · aporta: Muestra que Daniel no fue el primero: ya había cientos de muertos antes de su diagnóstico. · sello **MEMORIA** en [11]
- relojes: —

## ch06 — El rastro persiste

- beat 11 · respiro · ficha **D121** [normal] «LOS QUE PASARON · Unas 7000 trabajaron para ABA» en [0] sobre «pasaron» (44/51 car.) · respaldo: «Aproximadamente 7000 personas trabajaron para ABA en los 23 años que la compañía extrajo y molió asbesto.» · año — / relato 1962 · aporta: Da la cifra de personas que pasaron por la mina, sin contar a sus familias. · sello —
- beat 12 · revelacion · PICO · ficha **D40** [normal] «TAMAÑO DE LA ZONA · 46.840 hectáreas» en [13] sobre «zona» (33/90 car.) · respaldo: «El Área de Gestión del Asbesto de Wittenoom (WAMA) cubre una superficie de 46.840 hectáreas.» · año — / relato 2006 · aporta: Da la superficie oficial de la zona declarada no apta. La voz no la dice. · sello **AMENAZA** en [15]
- relojes: —

## ch07 — La herida abierta

- beat 13 · cierre · PICO · ficha **D61** [papel] «RECONOCIDO POR EL GOBIERNO · 2023: la contaminación se extendió» en [8] sobre «problema» (60/76 car.) · respaldo: «Un Subcomité de Wittenoom determinó en 2023 que todos los informes sobre el alcance de la contaminación ya no son aplicables y que la contaminación se ha extendido.» · año 2023 / relato 2026 · aporta: Un organismo oficial admitió en 2023 que la contaminación creció y que los estudios quedaron viejos. La voz no lo dice. · sello **RABIA** en [11]
- relojes: —

## Lo que cayó

- (nada)

## Reintento: los motivos que se le mandaron al autor

- D131 (ch03 beat 6) «LA OFICINA DE SALUD LABORAL · Se creó en 1959 con una sola persona»: fecha_relato: D131 es de 1959 y en la oración [27] el relato va por 1957 (el último año que dijo la voz); ni la oración ni sus vecinas lo sitúan después
- D94 (ch05 beat 9) «LO QUE PAGÓ LA EMPRESA · 18,3 millones de dólares australianos a 200 afectados»: fecha_relato: D94 es de 1989 y en la oración [8] el relato va por 1988 (el último año que dijo la voz); ni la oración ni sus vecinas lo sitúan después
- D79 (ch01 beat 1, oración [7]) «LOS MUERTOS DE WITTENOOM · Más de 2000 mineros y vecinos murieron»: la voz dice «2000» en ch06 [7] («Melita Markey sigue contando lo que el gobierno dejó de contar en dos mil; otras estimaciones, dice, hablan de más de cuatro mil, y la cifra sube.»); ¿es el mismo hecho? si no, mantenelo
- D79 (ch01 beat 1, oración [7]) «LOS MUERTOS DE WITTENOOM · Más de 2000 mineros y vecinos murieron»: la voz dice «2000» en una oración posterior en ch06 [7] («Melita Markey sigue contando lo que el gobierno dejó de contar en dos mil; otras estimaciones, dice, hablan de más de cuatro mil, y la cifra sube.»); ¿es el mismo hecho? si no, mantenelo
- D135 (ch03 beat 5, oración [13]) «QUIÉN DIRIGÍA LA MINA · El Estado los llamó «aficionados»»: la voz dice «Estado» en la oración ancla o en una vecina en ch03 [13] («En 1944, el inspector de minas y el ingeniero de minas Adjunto del Estado informaron sobre el problema del polvo.»); ¿es el mismo hecho? si no, mantenelo
- T13: dijiste que la voz lo dice («La voz dice los diagnósticos de 1946.»); la voz de ch03 no dice «Wittenoom» («Se diagnosticó un primer caso de asbestosis en Wittenoom. (fecha 1946)»): vuelve a ser candidato
- D21: dijiste que la voz lo dice («La voz dice que la producción subió en 1961.»); la voz de ch03 no dice «Wittenoom» («La producción minera en Wittenoom se incrementó en 1961 a pesar de la evidencia de los riesgos.»): vuelve a ser candidato
- T27: dijiste que la voz lo dice («La voz cuenta el recorte del suplemento.»); la voz de ch03 no dice «3» ni «4» («El subsidio por polvo se redujo a 3 o 4 peniques y se restringió a ciertas áreas, tras la instalación de equipo para reducir el polvo. (fecha 1957)»): vuelve a ser candidato
- T35: dijiste que la voz lo dice («La voz cuenta el caso de mesotelioma de McNulty en 1962.»); la voz de ch03 no dice «Sudáfrica» ni «Wittenoom» («Se reporta el primer caso de mesotelioma fuera de Sudáfrica, en un ex-trabajador de la planta de molienda de Wittenoom. (fecha 1962)»): vuelve a ser candidato
- D95: dijiste que la voz lo dice («La voz dice los mil quinientos millones.»); la voz de ch07 no dice «1.500» («El pueblo aborigen banjima reclama 1.500 millones de dólares australianos al Ejecutivo por la contaminación.»): vuelve a ser candidato
- el beat 5 de ch03 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D01 («150.000 toneladas de asbesto comercial entre 1937 y 1966: cifra técnica de contexto.»)
- el beat 9 de ch05 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D51 («Producción atribuida por Vernon a la mina de Wittenoom, 131.000 toneladas, en el anuncio del cierre.»)
- el beat 12 de ch06 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D40 («Superficie oficial de WAMA: 46.840 hectáreas; cifra administrativa con versiones en disputa, mejor leída que dicha.»)
- el beat 13 de ch07 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D61 («Reconocimiento oficial de 2023 de que los estudios sobre la extensión quedaron desactualizados; va como documento fechado.»)

### Preguntas y respuesta del autor

- D79 {'no_dicho': ['2000'], 'spoiler': ['2000']}: la mantuvo en ch01 beat 1 [7]: otro hecho
- D135 {'no_dicho': ['Estado', 'Minas']}: la sacó o la cambió (el mismo hecho, o eligió otra)

### Reintento parcial: 2 vuelta(s)

#### Vuelta 1 · US$ 0.1678

- beats que podía cambiar: ch01 beat 1, ch03 beat 5, ch03 beat 6, ch05 beat 9, ch06 beat 12, ch07 beat 13
- motivos:
  - D131 (ch03 beat 6) «LA OFICINA DE SALUD LABORAL · Se creó en 1959 con una sola persona»: fecha_relato: D131 es de 1959 y en la oración [27] el relato va por 1957 (el último año que dijo la voz); ni la oración ni sus vecinas lo sitúan después
  - D94 (ch05 beat 9) «LO QUE PAGÓ LA EMPRESA · 18,3 millones de dólares australianos a 200 afectados»: fecha_relato: D94 es de 1989 y en la oración [8] el relato va por 1988 (el último año que dijo la voz); ni la oración ni sus vecinas lo sitúan después
  - D79 (ch01 beat 1, oración [7]) «LOS MUERTOS DE WITTENOOM · Más de 2000 mineros y vecinos murieron»: la voz dice «2000» en ch06 [7] («Melita Markey sigue contando lo que el gobierno dejó de contar en dos mil; otras estimaciones, dice, hablan de más de cuatro mil, y la cifra sube.»); ¿es el mismo hecho? si no, mantenelo
  - D79 (ch01 beat 1, oración [7]) «LOS MUERTOS DE WITTENOOM · Más de 2000 mineros y vecinos murieron»: la voz dice «2000» en una oración posterior en ch06 [7] («Melita Markey sigue contando lo que el gobierno dejó de contar en dos mil; otras estimaciones, dice, hablan de más de cuatro mil, y la cifra sube.»); ¿es el mismo hecho? si no, mantenelo
  - D135 (ch03 beat 5, oración [13]) «QUIÉN DIRIGÍA LA MINA · El Estado los llamó «aficionados»»: la voz dice «Estado» en la oración ancla o en una vecina en ch03 [13] («En 1944, el inspector de minas y el ingeniero de minas Adjunto del Estado informaron sobre el problema del polvo.»); ¿es el mismo hecho? si no, mantenelo
  - T13: dijiste que la voz lo dice («La voz dice los diagnósticos de 1946.»); la voz de ch03 no dice «Wittenoom» («Se diagnosticó un primer caso de asbestosis en Wittenoom. (fecha 1946)»): vuelve a ser candidato
  - D21: dijiste que la voz lo dice («La voz dice que la producción subió en 1961.»); la voz de ch03 no dice «Wittenoom» («La producción minera en Wittenoom se incrementó en 1961 a pesar de la evidencia de los riesgos.»): vuelve a ser candidato
  - T27: dijiste que la voz lo dice («La voz cuenta el recorte del suplemento.»); la voz de ch03 no dice «3» ni «4» («El subsidio por polvo se redujo a 3 o 4 peniques y se restringió a ciertas áreas, tras la instalación de equipo para reducir el polvo. (fecha 1957)»): vuelve a ser candidato
  - T35: dijiste que la voz lo dice («La voz cuenta el caso de mesotelioma de McNulty en 1962.»); la voz de ch03 no dice «Sudáfrica» ni «Wittenoom» («Se reporta el primer caso de mesotelioma fuera de Sudáfrica, en un ex-trabajador de la planta de molienda de Wittenoom. (fecha 1962)»): vuelve a ser candidato
  - D95: dijiste que la voz lo dice («La voz dice los mil quinientos millones.»); la voz de ch07 no dice «1.500» («El pueblo aborigen banjima reclama 1.500 millones de dólares australianos al Ejecutivo por la contaminación.»): vuelve a ser candidato
  - el beat 5 de ch03 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D01 («150.000 toneladas de asbesto comercial entre 1937 y 1966: cifra técnica de contexto.»)
  - el beat 9 de ch05 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D51 («Producción atribuida por Vernon a la mina de Wittenoom, 131.000 toneladas, en el anuncio del cierre.»)
  - el beat 12 de ch06 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D40 («Superficie oficial de WAMA: 46.840 hectáreas; cifra administrativa con versiones en disputa, mejor leída que dicha.»)
  - el beat 13 de ch07 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D61 («Reconocimiento oficial de 2023 de que los estudios sobre la extensión quedaron desactualizados; va como documento fechado.»)
- aplicados: ch03 beat 5 (ficha), ch03 beat 6 (ficha), ch05 beat 9 (ficha), ch06 beat 12 (ficha), ch07 beat 13 (ficha)

#### Vuelta 2 · US$ 0.1200

- beats que podía cambiar: ch03 beat 5
- motivos:
  - D135 (ch03 beat 5, oración [13]) «QUIÉN DIRIGÍA LA MINA · El Departamento de Minas los llamó «aficionados»»: la voz dice «Minas» en la oración ancla o en una vecina en ch03 [13] («En 1944, el inspector de minas y el ingeniero de minas Adjunto del Estado informaron sobre el problema del polvo.»); ¿es el mismo hecho? si no, mantenelo
  - T13: dijiste que la voz lo dice («La voz dice los diagnósticos de 1946.»); la voz de ch03 no dice «Wittenoom» («Se diagnosticó un primer caso de asbestosis en Wittenoom. (fecha 1946)»): vuelve a ser candidato
  - D21: dijiste que la voz lo dice («La voz dice que la producción subió en 1961.»); la voz de ch03 no dice «Wittenoom» («La producción minera en Wittenoom se incrementó en 1961 a pesar de la evidencia de los riesgos.»): vuelve a ser candidato
  - T27: dijiste que la voz lo dice («La voz cuenta el recorte del suplemento.»); la voz de ch03 no dice «3» ni «4» («El subsidio por polvo se redujo a 3 o 4 peniques y se restringió a ciertas áreas, tras la instalación de equipo para reducir el polvo. (fecha 1957)»): vuelve a ser candidato
  - T35: dijiste que la voz lo dice («La voz cuenta el caso de mesotelioma de McNulty en 1962.»); la voz de ch03 no dice «Sudáfrica» ni «Wittenoom» («Se reporta el primer caso de mesotelioma fuera de Sudáfrica, en un ex-trabajador de la planta de molienda de Wittenoom. (fecha 1962)»): vuelve a ser candidato
  - D95: dijiste que la voz lo dice («La voz dice los mil quinientos millones.»); la voz de ch07 no dice «1.500» («El pueblo aborigen banjima reclama 1.500 millones de dólares australianos al Ejecutivo por la contaminación.»): vuelve a ser candidato
  - el beat 5 de ch03 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D01 («150.000 toneladas de asbesto comercial entre 1937 y 1966: cifra técnica de contexto.»)
- aplicados: ch03 beat 5 (ficha)

### Motivos sin beat (no hubo reintento)

- T13: dijiste que la voz lo dice («La voz dice los diagnósticos de 1946.»); la voz de ch03 no dice «Wittenoom» («Se diagnosticó un primer caso de asbestosis en Wittenoom. (fecha 1946)»): vuelve a ser candidato
- D21: dijiste que la voz lo dice («La voz dice que la producción subió en 1961.»); la voz de ch03 no dice «Wittenoom» («La producción minera en Wittenoom se incrementó en 1961 a pesar de la evidencia de los riesgos.»): vuelve a ser candidato
- T27: dijiste que la voz lo dice («La voz cuenta el recorte del suplemento.»); la voz de ch03 no dice «3» ni «4» («El subsidio por polvo se redujo a 3 o 4 peniques y se restringió a ciertas áreas, tras la instalación de equipo para reducir el polvo. (fecha 1957)»): vuelve a ser candidato
- T35: dijiste que la voz lo dice («La voz cuenta el caso de mesotelioma de McNulty en 1962.»); la voz de ch03 no dice «Sudáfrica» ni «Wittenoom» («Se reporta el primer caso de mesotelioma fuera de Sudáfrica, en un ex-trabajador de la planta de molienda de Wittenoom. (fecha 1962)»): vuelve a ser candidato
- D95: dijiste que la voz lo dice («La voz dice los mil quinientos millones.»); la voz de ch07 no dice «1.500» («El pueblo aborigen banjima reclama 1.500 millones de dólares australianos al Ejecutivo por la contaminación.»): vuelve a ser candidato

## Cierre del reintento

- cerró por: **sin beat** (después de 2 vueltas)
- cortado al cerrar, sin preguntarle al autor: (nada)

## Descartados por el modelo

- D85 [otro]: Es el dato central del gancho según la escaleta, pero no está en el archivo. Lo reemplacé por D79.
- T34 [voz_lo_dice]: La voz cuenta el baile y su fecha en la oración 0 del capítulo 2.
- T38 [voz_lo_dice]: La fecha de partida (24 de septiembre de 1962) se deduce de «cuatro días después» de la boda. Además el respaldo está en formato ISO.
- Q14 [voz_lo_dice]: La voz cita el viaje de Calvo casi completo.
- D83 [voz_lo_dice]: La voz dice «cerca de ocho mil españoles».
- T36 [voz_lo_dice]: La voz dice la llegada de los De Juan en agosto de 1962.
- T24 [voz_lo_dice]: La voz dice los viajes de reclutamiento desde 1950.
- Q13 [voz_lo_dice]: La voz resume que se hicieron íntimos amigos.
- Q27 [voz_lo_dice]: La voz reproduce la cita de Calvo sobre el avión y la pista.
- Q44 [voz_lo_dice]: La voz cita a un antiguo trabajador sobre los relaves.
- D92 [voz_lo_dice]: La voz dice que Saint advirtió por escrito en 1948.
- Q45 [voz_lo_dice]: La voz cita la carta de Saint.
- Q53 [voz_lo_dice]: La voz cita al defensor del empleador.
- Q46 [voz_lo_dice]: La voz cita el «alborotador».
- D19 [voz_lo_dice]: La voz dice el informe de 1944.
- T13 [voz_lo_dice]: La voz dice los diagnósticos de 1946. — **falso: la voz no dice ['Wittenoom']**
- T06 [voz_lo_dice]: La voz dice el traspaso de 1943.
- D21 [voz_lo_dice]: La voz dice que la producción subió en 1961. — **falso: la voz no dice ['Wittenoom']**
- Q54 [voz_lo_dice]: La voz cita el acta de la Junta de Referencia.
- T27 [voz_lo_dice]: La voz cuenta el recorte del suplemento. — **falso: la voz no dice ['3', '4']**
- T35 [voz_lo_dice]: La voz cuenta el caso de mesotelioma de McNulty en 1962. — **falso: la voz no dice ['Sudáfrica', 'Wittenoom']**
- Q49 [voz_lo_dice]: La voz cita a McNulty.
- D130 [voz_lo_dice]: Es el mismo hecho que cuenta la voz sobre McNulty en 1962.
- D115 [otro]: Encaja con la oración de McNulty en 1962, que está en el capítulo 4. Elegí un ancla dentro del capítulo 3 para el beat 6, así que no lo usé.
- Q16 [voz_lo_dice]: La voz cuenta la explosión del primer día.
- D104 [voz_lo_dice]: La voz dice las jornadas de dieciséis horas.
- T41 [voz_lo_dice]: La voz dice el bautizo y la partida.
- T40 [voz_lo_dice]: La voz cuenta el nacimiento.
- T39 [voz_lo_dice]: La voz cuenta el nacimiento de John Patrick.
- D87 [voz_lo_dice]: La voz dice «unos diez meses».
- T49 [voz_lo_dice]: La voz cuenta el cierre por costos.
- T47 [voz_lo_dice]: La voz cuenta el regreso a Madrid.
- D88 [voz_lo_dice]: La voz cuenta los dos años y medio de los De Juan.
- T51 [voz_lo_dice]: La voz cuenta el regreso de los De Juan en 1971.
- D27 [voz_lo_dice]: La voz cuenta la reducción del pueblo en 1978.
- D93 [voz_lo_dice]: La voz cita el fallo del juez de 1988.
- T56 [voz_lo_dice]: La voz cuenta la sociedad de 1979.
- D51 [otro]: Válido para el beat 9, pero D94 (la indemnización) suma más.
- T64 [voz_lo_dice]: La voz cuenta el diagnóstico de 1991.
- D89 [voz_lo_dice]: La voz cuenta la muerte nueve meses después.
- Q35 [voz_lo_dice]: La voz cita al hijo.
- D110 [otro]: Es una proyección técnica difícil de leer en 3 segundos. D23 se entiende solo.
- Q24 [voz_lo_dice]: La voz cita al policía.
- Q21 [voz_lo_dice]: La voz cita a Mercedes de Juan.
- Q33 [voz_lo_dice]: La voz cuenta lo de Markey.
- D90 [spoiler]: La cifra de más de 4000 muertes la cuenta la voz después, en el capítulo 6.
- D64 [otro]: Buena comparación con el estadio, pero en el beat pico 12 priorizé el dato central T80.
- D02 [voz_lo_dice]: La voz dice los más de tres millones de toneladas de relaves.
- Q07 [voz_lo_dice]: La voz cita al gobierno sobre el «período oscuro».
- Q03 [voz_lo_dice]: La voz cita la declaración de «no apta».
- D10 [otro]: No existe en el archivo.
- T90 [voz_lo_dice]: La voz dice las fibras en canales de arroyos.
- D59 [voz_lo_dice]: La voz cuenta el documento de 2016.
- T98 [voz_lo_dice]: La voz cuenta el proceso de Gordon Legal en 2026.
- Q10 [voz_lo_dice]: La voz cita a Parker.
- T92 [voz_lo_dice]: La voz cuenta la visita de Orellana.
- T96 [voz_lo_dice]: La voz dice la muerte de Parker.
- D95 [voz_lo_dice]: La voz dice los mil quinientos millones. — **falso: la voz no dice ['1.500']**
- Q34 [voz_lo_dice]: La voz cita al gobierno sobre el «grave problema».
- D70 [otro]: No existe en el archivo.
- D03 [otro]: No existe en el archivo.
- D129 [otro]: No existe en el archivo.
- D20 [otro]: No existe en el archivo.
- D86 [repetido]: Se parece a D121, que ya usé en el beat 11.
