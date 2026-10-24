# F22 — md5 y diff de los prompts

## md5 de los archivos del handoff

| archivo | md5 |
|---|---|
| HANDOFF_F22_ejemplos_y_antagonista.md | `2685deecf8e8516d6cc8ee2c61b47384` |
| CASO_EJEMPLO_cardal.md | `7068cef5063db1de5a015c50891204e4` |
| PROMPT_FICHA_v2_1.md | `168358d182f9831dedc1bd21ba910540` |
| PROMPT_COLUMNA_v1_1.md | `af1d5f4150b4f4fc54a0c603e7f65cbb` |
| PROMPT_ESCALETA_v2_1.md | `601aa76a77ce2c1dd9bd861a3bba6a02` |
| PROMPT_GUIONISTA_v5_2.md | `9d80720a0d6770c7cb4220f2ba0f4217` |

## Bloque SISTEMA del archivo vs código

| prompt | md5 del bloque `## SISTEMA` del archivo | md5 en código | igual | md5 del viejo (sigue en código) |
|---|---|---|---|---|
| ficha | `7d3599dc6e4123a3bb883fc15a541e71` | `7d3599dc6e4123a3bb883fc15a541e71` | sí | `2e151732da47e09acf0cb48eb7089fcb` |
| columna | `f294cf6b1220983903ce339f5b21cb27` | `f294cf6b1220983903ce339f5b21cb27` | sí | `1408569c5c9de22ec406a10ba0cd9b13` |
| escaleta | `7ea18a6aa1ca91c5ad0dfb7cc9b239a8` | `7ea18a6aa1ca91c5ad0dfb7cc9b239a8` | sí | `49ed74d941def064cdda077212629ff1` |
| guion | `743e4f0a7ff9e58d86762bbd43679952` | `743e4f0a7ff9e58d86762bbd43679952` | sí | `cdce609abea95ee36d0eb4f44d74dda8` |

## Diff ficha: ficha_caso.system("f15-1") (f15-1) → ficha_caso.system() (f22-1)

10 líneas salen, 12 entran (de 40 → 42 líneas). Cada línea del prompt es un párrafo entero.

```diff
--- ficha_caso.system("f15-1") (f15-1)
+++ ficha_caso.system() (f22-1)
@@ -4 +4 @@
-- personas: un nombre canónico por persona, su rol, las variantes del nombre que encontraste y sus ids. Si dos fuentes dan nombres distintos para la misma persona, no elegís: la persona va también a contradicciones.
+- personas: un nombre canónico por persona, su rol, las variantes del nombre que encontraste y sus ids. Si dos fuentes dan nombres distintos para la misma persona, no elegís: la persona va también a contradicciones. Las instituciones que deciden en el caso (un ministerio, una empresa, una dirección) van también en personas, con su rol institucional, para que la escaleta pueda nombrarlas.
@@ -8 +8 @@
-  - giros (3 a 6): los momentos en que la historia cambia de dirección (una orden, una puerta que no abre, una cifra que aparece, una negación oficial). Cada uno con sus ids y en qué orden pasan.
+  - giros (3 a 6): los momentos en que la historia cambia de dirección (una orden, un aviso que no llega, una cifra que aparece, una negación oficial). Cada uno con sus ids y en qué orden pasan.
@@ -14,2 +14,4 @@
-Ejemplo de humano candidato (de otro caso; copiá la forma, no el contenido):
-{"nombre": "Pearl Cornelia Bland", "rol": "detenida por una deuda de 398 dólares", "arco": "entra presa por multas, queda encerrada cuando llega el huracán, es agredida en Conchetta sin que los oficiales intervengan, y sale en junio del año siguiente por una orden de liberación", "ids": ["D301", "Q88", "D512"], "citas_verificadas": 1}
+Los ejemplos que siguen son de un caso que no es este (una estación de radio y faro en una isla, en los años sesenta). Copiá la forma, no el contenido: los ids van como D##, Q##, T## y ## es el número que tenga el id en ESTE pool.
+
+Ejemplo de humano candidato:
+{"nombre": "Elvira Soto", "rol": "telegrafista de la estación", "arco": "entra como empleada nueva el invierno del temporal, manda los telegramas pidiendo el barco y recibe las respuestas sin firma, sostiene la radio con las baterías del faro la noche en que se apaga el generador, y sale siendo la única que guardó el libro de telegramas", "ids": ["D##", "Q##", "T##"], "citas_verificadas": 3}
@@ -18 +20 @@
-{"orden": 2, "que_cambia": "El sheriff rechaza la ayuda del Departamento de Correcciones para evacuar: la prisión no se vacía", "ids": ["D35", "Q08"]}
+{"orden": 2, "que_cambia": "La Dirección responde al primer pedido de barco con «mantener servicio»: la estación no se evacúa", "ids": ["T##", "Q##"]}
@@ -21 +23 @@
-{"donde": "Celdas de Templeman III, 30 de agosto", "quien": "presos encerrados", "que_pasa": "el agua de la inundación entra y sube hasta el pecho", "sentidos": "olor a aguas residuales y combustible diésel; oscuridad total; gritos entre pabellones", "ids": ["T93", "D414", "D09", "D545"]}
+{"donde": "Sala de radio de la estación, la noche en que se apaga el generador", "quien": "Elvira Soto, Raúl Bascuñán, las tres familias", "que_pasa": "el generador se apaga y Elvira sigue transmitiendo con las baterías del faro", "sentidos": "olor a querosén; ventanas tapadas con mantas; el ruido del generador que tose dos veces y el silencio después; una vela", "ids": ["T##", "D##", "Q##"]}
@@ -24 +26 @@
-{"texto": "La lista de evacuados no incluye a 517 reclusos.", "nivel": 1, "sirve_para": "consecuencia", "ids": ["D185"]}
+{"texto": "El recuento de la comisión da dos muertos; las familias declaran tres.", "nivel": 1, "sirve_para": "consecuencia", "ids": ["D##", "D##"]}
@@ -26,2 +28,2 @@
-- cifras: una cifra por conteo (muertos, heridos, huérfanos, personas adentro…), con su fuente y las otras versiones. Cada cifra con su unidad (personas, °C, años, guaraníes…): nunca un número sin qué cuenta.
-- citas: las mejores 15 a 25, con autor, rol, estado de verificación y el texto. Si hay un error evidente de transcripción, lo corregís en «texto» y dejás el texto del pool en «original»; si no corregís nada, «original» va vacío.
+- cifras: una cifra por conteo (muertos, heridos, evacuados, personas adentro…), con su fuente y las otras versiones. Cada cifra con su unidad (personas, metros, grados, años, la moneda del caso…): nunca un número sin qué cuenta.
+- citas: las mejores 15 a 25, con autor, rol, estado de verificación y el texto. Si hay un error evidente de transcripción, lo corregís en «texto» y dejás el texto del pool en «original»; si no corregís nada, «original» va vacío. Si «texto» no está en español, «traduccion» lleva la cita en español.
@@ -33 +35 @@
-  4. Hechos disputados (quién dio una orden, cómo estaban las puertas): no se resuelven. Van a «versiones», cada versión con su fuente, para que el guion las cuente como versiones.
+  4. Hechos disputados (quién dio una orden, si un aviso llegó a tiempo): no se resuelven. Van a «versiones», cada versión con su fuente, para que el guion las cuente como versiones.
```

## Diff columna: m01a_columna.SYSTEM_F17_1 (f17-1) → m01a_columna.SYSTEM (f22-1)

21 líneas salen, 24 entran (de 44 → 47 líneas). Cada línea del prompt es un párrafo entero.

```diff
--- m01a_columna.SYSTEM_F17_1 (f17-1)
+++ m01a_columna.SYSTEM (f22-1)
@@ -6 +6 @@
-La columna es una página. Siete filas, una por capítulo, con dos cosas en cada una: qué pasa (los hechos y las personas que entran, en tres o cuatro frases) y con qué termina (la frase que deja la puerta abierta al siguiente). Arriba, el humano y el pico. Abajo, qué dejaste afuera y por qué. No es el guion ni la escaleta: es la decisión. Alguien que no sabe nada del caso tiene que leerla en un minuto y entender qué video va a ver.
+La columna es una página. Siete filas, una por capítulo, con dos cosas en cada una: qué pasa (los hechos y las personas que entran, en tres o cuatro frases) y con qué termina (la frase que deja la puerta abierta al siguiente). Arriba, el humano, quién decide y el pico. Abajo, qué dejaste afuera y por qué. No es el guion ni la escaleta: es la decisión. Alguien que no sabe nada del caso tiene que leerla en un minuto y entender qué video va a ver.
@@ -12,7 +12,8 @@
-3. Cap 1: el peor momento, ya en curso. Una imagen física (lo que se ve, se oye, se huele) con el humano adentro. Sin año, sin cifras, sin juicio. Termina volviendo atrás.
-4. Cap 2: la vida antes. Quién era esta gente y qué hacía ahí. Es el único cap tranquilo; termina con la primera señal del peligro.
-5. Caps 3 y 4: la escalada. Cada uno agrega un giro de la ficha y termina peor que el anterior.
-6. Cap 5: el pico. El de la ficha, salvo razón mejor. Es el cap con más hechos, no el de menos: todo lo anterior lo prepara. Termina con la frase más corta del video.
-7. Cap 6: el respiro y las consecuencias inmediatas: los que salen, los cuerpos, la búsqueda, las cifras oficiales (que van a pantalla).
-8. Cap 7: las versiones en disputa, lo que la justicia dijo, y el humano otra vez. Termina con una cita del humano o la pregunta final de la ficha.
-9. Lo que queda afuera se dice: nombres, hechos y escenas que no entraron, con una razón de una línea.
+3. Quién decide: la persona o la institución a la que la ficha atribuye la decisión que causó el daño. Si la ficha no se lo atribuye a nadie, decís «ninguno» y por qué; no inventás un culpable.
+4. Cap 1: el peor momento, ya en curso. Una imagen física (lo que se ve, se oye, se huele) con el humano adentro. Sin año, sin cifras, sin juicio. Termina volviendo atrás.
+5. Cap 2: la vida antes. Quién era esta gente y qué hacía ahí. Es el único cap tranquilo; termina con la primera señal del peligro.
+6. Caps 3 y 4: la escalada. Cada uno agrega un giro de la ficha y termina peor que el anterior.
+7. Cap 5: el pico. El de la ficha, salvo razón mejor. Es el cap con más hechos, no el de menos: todo lo anterior lo prepara. Termina con la frase más corta del video.
+8. Cap 6: el respiro y las consecuencias inmediatas: los que salen, los cuerpos, la búsqueda, las cifras oficiales (que van a pantalla).
+9. Cap 7: las versiones en disputa, lo que la justicia dijo, y el humano otra vez. Termina con una cita del humano o la pregunta final de la ficha.
+10. Lo que queda afuera se dice: nombres, hechos y escenas que no entraron, con una razón de una línea.
@@ -22 +23 @@
-De otro caso (una cárcel durante un huracán). Copiá la forma, no el contenido.
+De un caso que no es el tuyo (una estación de radio y faro en una isla, mil novecientos sesenta y ocho). Copiá la forma, no el contenido: ninguno de estos nombres ni cifras está en tu ficha.
@@ -24,2 +25,3 @@
-HUMANO: Renard Reed, oficial del sheriff: entra de servicio la noche de la tormenta, ve irse a sus compañeros, ve los disparos desde el techo, y años después es el único que lo dice en voz alta.
-PICO: cap 5, los francotiradores disparan a los presos que intentan salir del agua.
+HUMANO: Elvira Soto, telegrafista de la estación: manda los telegramas pidiendo el barco, recibe las respuestas sin firma, sostiene la radio con las baterías del faro la noche del pico, y años después es la única que guardó el registro.
+QUIÉN DECIDE: la Dirección de Faros y Balizas (institución): los telegramas de «mantener servicio» salen de ahí y nadie los firma.
+PICO: cap 5, la noche en que el generador se apaga y muere el niño.
@@ -27,7 +29,7 @@
-CAP 1 · QUÉ PASA: un hombre bebe agua del inodoro en una celda a oscuras; miles de presos encerrados en una cárcel inundada; Reed está de servicio adentro. TERMINA: Días antes de la sed, llegó la tormenta. Y con ella, una decisión.
-CAP 2 · QUÉ PASA: 28 de agosto, evacuación obligatoria de la ciudad; la excepción son los presos; el sheriff rechaza la ayuda para evacuar («donde pertenecen»); Reed ve a los oficiales renunciar cuando se va la luz. TERMINA: Cuando la luz se fue, los guardias también empezaron a irse.
-CAP 3 · QUÉ PASA: fallan los generadores; Templeman III sin luz ni aire; gritos entre pabellones; el agua empieza a entrar. TERMINA: En la oscuridad total, el agua empieza a subir.
-CAP 4 · QUÉ PASA: agua negra hasta el pecho, basura y heces; dos cadáveres flotando en el pabellón médico; presos de pie durante días; empiezan a romper ventanas y a quemar sábanas para que los vean. TERMINA: La respuesta no fue un rescate.
-CAP 5 · QUÉ PASA: Richard ve francotiradores en el techo del HOD disparando a los reclusos; Reed: «parecía que estaban abatiendo a la gente»; alguien grita «están tratando de escapar»; los presos entre el agua y los disparos. TERMINA: ¿Escapar o sobrevivir?
-CAP 6 · QUÉ PASA: el paso elevado de Broad Street, monos naranjas al sol; jaulas detrás de la estación; sándwiches por encima de la cerca; los trasladan por todo el estado. TERMINA: Cuando se armó la lista de evacuados, faltaban cientos de nombres.
-CAP 7 · QUÉ PASA: 517 ausentes de la lista; la portavoz: «nadie se ahogó, nadie se quedó atrás»; Reyes: «todavía hay presos muertos ahí dentro»; Reed. TERMINA: «Aunque estén en la cárcel, son seres humanos.»
+CAP 1 · QUÉ PASA: una mujer transmite en morse a la luz de una vela; la sala huele a querosén; afuera el faro sigue encendido; once personas esperan un barco. TERMINA: Tres semanas antes de la vela, llegó un telegrama. Y con él, una orden.
+CAP 2 · QUÉ PASA: la estación en invierno: once personas, tres familias, el Alborada que viene cada quince días; Elvira recién llegada; el primer telegrama de la Dirección cuando el temporal cierra el paso: mantener servicio. TERMINA: El Alborada tenía que llegar el lunes. No llegó el lunes.
+CAP 3 · QUÉ PASA: Elvira pide el barco; la respuesta es la misma; el combustible del generador se raciona; Bascuñán apaga la calefacción de las casas para que el faro siga. TERMINA: Cuando se apagó la última estufa, empezaron a mirar los muebles.
+CAP 4 · QUÉ PASA: el niño enferma; el mecánico Ismael Rojo sale a revisar el generador bajo la tormenta y no vuelve; el séptimo telegrama; la misma respuesta. TERMINA: El séptimo telegrama tampoco tuvo firma.
+CAP 5 · QUÉ PASA: el generador tose y se apaga; Elvira transmite con las baterías del faro; Bascuñán rompe la primera silla y la mete en la estufa; esa noche el niño deja de toser. TERMINA: Uno menos.
+CAP 6 · QUÉ PASA: el Alborada entra a la bahía; el padre Quiroga cuenta a los que bajan; dos muertos para la comisión, tres para las familias; Teo Marín, marinero: «el capitán leyó el papel y dio la vuelta». TERMINA: El papel que leyó el capitán nunca apareció.
+CAP 7 · QUÉ PASA: la comisión; el capitán: nunca zarpó por el temporal; los telegramas de Elvira: zarpó y recibió orden de volver; nadie de la Dirección firma nada; Elvira, años después, lee su libro en la radio. TERMINA: «Yo mandaba los telegramas. Nadie me dijo que los leyeran.»
@@ -35 +37 @@
-AFUERA: Pearl Bland y su deuda de 398 dólares (buen arco, pero compite con Reed por el hilo); Iris Hardeman en Central Lock-Up (entra solo si el cap 6 queda corto); Nagin (el contexto de la evacuación alcanza sin su nombre); las cifras legales de las condenas (van a pantalla).
+AFUERA: la historia del farero anterior (buen arco, pero es otro invierno); la discusión técnica sobre el alcance del faro (va a pantalla si hace falta); el nombre del capitán del Alborada (la versión alcanza con «el capitán»); los nombres de las tres familias (entran solo el niño y su madre, sin nombre, en el cap 5).
@@ -39,2 +41,2 @@
-- Repartir todas las personas de la ficha entre los caps para «aprovechar el material». La ficha tiene 90 personas; el video tiene lugar para seis.
-- Un cap 1 que explica lo que va a pasar («esto terminará en un juicio») en vez de mostrar el peor momento.
+- Repartir todas las personas de la ficha entre los caps para «aprovechar el material». La ficha puede tener decenas de personas; el video tiene lugar para seis.
+- Un cap 1 que explica lo que va a pasar («esto terminará en una comisión») en vez de mostrar el peor momento.
@@ -43,0 +46 @@
+- Inventar un culpable para que haya antagonista. Si la ficha no se lo atribuye a nadie, «ninguno».
```

## Diff columna (tarea): m01a_columna.TAREA_F17_1 → m01a_columna.TAREA

1 líneas salen, 1 entran (de 3 → 3 líneas). Cada línea del prompt es un párrafo entero.

```diff
--- m01a_columna.TAREA_F17_1
+++ m01a_columna.TAREA
@@ -2 +2 @@
-Con la ficha de arriba, escribí la columna vertebral de este caso: HUMANO, PICO, siete filas CAP n · QUÉ PASA / TERMINA, y AFUERA. Devolvé el JSON del esquema: {"humano": {"nombre", "por_que", "ids"}, "pico": {"cap", "que", "ids"}, "caps": [{"cap", "que_pasa", "termina", "personas", "ids"}], "afuera": [{"que", "por_que"}]}. En `ids`, los ids de la ficha que sostienen cada fila; en `personas`, los nombres que entran en ese cap.
+Con la ficha de arriba, escribí la columna vertebral de este caso: HUMANO, QUIÉN DECIDE, PICO, siete filas CAP n · QUÉ PASA / TERMINA, y AFUERA. Devolvé el JSON del esquema: {"humano": {"nombre", "por_que", "ids"}, "antagonista": {"tipo": "persona"|"institucion"|"ninguno", "nombre", "por_que", "ids"}, "pico": {"cap", "que", "ids"}, "caps": [{"cap", "que_pasa", "termina", "personas", "ids"}], "afuera": [{"que", "por_que"}]}. En `ids`, los ids de la ficha que sostienen cada fila; en `personas`, los nombres que entran en ese cap.
```

## Diff escaleta: m01a_escaleta.SYSTEM_V2_F16_1 (f16-1) → m01a_escaleta.SYSTEM_V2 (f22-1)

23 líneas salen, 26 entran (de 62 → 65 líneas). Cada línea del prompt es un párrafo entero.

```diff
--- m01a_escaleta.SYSTEM_V2_F16_1 (f16-1)
+++ m01a_escaleta.SYSTEM_V2 (f22-1)
@@ -6,0 +7,2 @@
+
+El antagonista es quien decide: una persona de la ficha, o una institución que la ficha nombra (un ministerio, una empresa, una dirección). Si en este caso no hay a quién atribuirle la decisión, lo decís («ninguno») y por qué.
@@ -14 +16 @@
-5. El pico es uno solo, y es el que la ficha marcó salvo que tengas una razón mejor (decila). Antes del pico, un cap que aprieta; después del pico, un respiro: los cuerpos, la morgue, el silencio.
+5. El pico es uno solo, y es el que la ficha marcó salvo que tengas una razón mejor (decila). Antes del pico, un cap que aprieta; después del pico, un respiro: lo que queda cuando pasa lo peor, el recuento, el silencio.
@@ -17 +19 @@
-8. Las versiones en disputa (quién dio la orden, cómo estaban las puertas) son material, no problema: dales su beat. El contraste entre la pericia y los testigos es casi siempre el mejor cap 6.
+8. Las versiones en disputa (quién dio la orden, si un aviso llegó a tiempo) son material, no problema: dales su beat. El contraste entre la versión oficial y lo que cuentan los testigos suele ser el mejor cap 6.
@@ -25 +27 @@
-De otro caso (una cárcel durante un huracán). Copiá la forma, no el contenido.
+De un caso que no es el tuyo (una estación de radio y faro en una isla, mil novecientos sesenta y ocho). Copiá la forma, no el contenido. Los ids van como Q##, D##, T##, E#: ## es el número que tenga el id en TU ficha; ninguno de estos existe en tus datos.
@@ -27,3 +29,4 @@
-humano: Renard Reed, oficial del sheriff. Por qué: entra de servicio la noche de la tormenta, ve a sus compañeros irse, ve los disparos desde el techo, y es el único que años después dice en voz alta lo que vio. 3 citas verificadas.
-promesa_gancho: «Miles de hombres quedaron encerrados cuando la ciudad se vació. Esta es la historia de quién decidió dejarlos.»
-pico: beat 5 (los francotiradores). Por qué: es el momento en que el encierro se vuelve cacería; todo lo anterior lo prepara.
+humano: Elvira Soto, telegrafista de la estación. Por qué: manda los telegramas pidiendo el barco, recibe las respuestas sin firma, sostiene la radio con las baterías del faro la noche del pico, y años después es la única que guardó el registro. 3 citas verificadas.
+antagonista: institución · la Dirección de Faros y Balizas. Por qué: los telegramas de «mantener servicio» salen de ahí y nadie los firma.
+promesa_gancho: «Once personas esperaron veintitrés días un barco que no llegó. Esta es la historia de quién decidió que no llegara.»
+pico: beat 5 (la noche del generador). Por qué: es el momento en que esperar deja de ser una decisión de la Dirección y pasa a ser una de ellos; todo lo anterior lo prepara.
@@ -31,5 +34,5 @@
-beat 1 · cap 1 · gancho · flash-forward · intensidad 4 · escena E3
-  imagen: el sabor del agua del inodoro en la boca, una celda a oscuras
-  dato central: Q184 (Burton: «tuvimos que beber agua del inodoro»)
-  el espectador se pregunta: ¿cómo se llega a eso?
-  cierre: Días antes de la sed, llegó la tormenta. Y con ella, una decisión.
+beat 1 · cap 1 · gancho · flash-forward · intensidad 4 · escena E#
+  imagen: una mujer transmite en morse a la luz de una vela; olor a querosén
+  dato central: Q## (Soto: «transmitía con las baterías del faro»)
+  el espectador se pregunta: ¿por qué sigue transmitiendo?
+  cierre: Tres semanas antes de la vela, llegó un telegrama. Y con él, una orden.
@@ -37,2 +40,2 @@
-  imagen: un televisor con el mapa del huracán, todavía con señal
-  dato central: T55 (28 de agosto, evacuación obligatoria) · apoyos: D30 (la excepción: los presos), Q08 (Gusman: «donde pertenecen»), Q24 (Reed: los oficiales renuncian)
+  imagen: el libro de telegramas abierto, la letra de Elvira
+  dato central: T## (el primer telegrama de la Dirección: mantener servicio) · apoyos: D## (once personas en la estación, tres familias), Q## (Bascuñán: «el faro no se apaga»), D## (la fecha prevista del Alborada)
@@ -40,2 +43,2 @@
-  el espectador se pregunta: ¿quién abre las puertas si los guardias se van?
-  cierre: Cuando la luz se fue, los guardias también empezaron a irse.
+  el espectador se pregunta: ¿quién manda cuando el que manda está a tres días de barco?
+  cierre: El Alborada tenía que llegar el lunes. No llegó el lunes.
@@ -43,3 +46,3 @@
-beat 5 · cap 5 · pico · intensidad 5 · escena E9
-  imagen: un fogonazo en el techo del edificio HOD, visto desde una ventana rota
-  dato central: Q14 (Richard: francotiradores) · apoyos: Q47 (Reed: «parecía que estaban abatiendo a la gente»), Q146 («están tratando de escapar»)
+beat 5 · cap 5 · pico · intensidad 5 · escena E#
+  imagen: el generador que tose dos veces y se apaga; una silla rota contra el piso
+  dato central: Q## (Soto: la noche que se apagó el generador) · apoyos: D## (Bascuñán ordena quemar los muebles), T## (la muerte del niño esa noche)
@@ -47,2 +50,2 @@
-  el espectador se pregunta: ¿escapar o sobrevivir?
-  cierre: Después de los disparos, quedaba la espera. Sobre un puente.
+  el espectador se pregunta: ¿cuánto dura una batería?
+  cierre: A la mañana, el faro seguía encendido. Adentro, eran uno menos.
@@ -51,3 +54,3 @@
-  dato central: D185 (517 ausentes de la lista) · apoyos: Q60 (Reyes: «todavía hay presos muertos ahí dentro»), Q50 (Reed: «son seres humanos»)
-  cierre: la cita de Reed.
-a_pantalla: D192 (la cifra oficial), D189 (la condena económica).
+  dato central: D## (la comisión: dos muertos; las familias: tres) · apoyos: Q## (Marín: «el capitán leyó el papel y dio la vuelta»), Q## (Soto: «nadie me dijo que los leyeran»)
+  cierre: la cita de Soto.
+a_pantalla: D## (el recuento oficial), D## (el informe de la comisión, fecha y folio).
```

## Diff guion: guion_v4.system("f15b-1") (v5.1) → guion_v4.system() (v5.2, f22-1)

19 líneas salen, 19 entran (de 85 → 85 líneas). Cada línea del prompt es un párrafo entero.

```diff
--- guion_v4.system("f15b-1") (v5.1)
+++ guion_v4.system() (v5.2, f22-1)
@@ -15 +15 @@
-- Nunca hablás del video, del canal ni de vos («esta es la historia de», «lo que vas a ver», «en este episodio»). El espectador no está viendo un video: está en la cárcel, en el supermercado, en el valle.
+- Nunca hablás del video, del canal ni de vos («esta es la historia de», «lo que vas a ver», «en este episodio»). El espectador no está viendo un video: está en el lugar donde pasó.
@@ -28 +28 @@
-6. Lo marcado PANTALLA no lo dice la voz: aparece en la imagen. Lo marcado SIN VERIFICAR va sin el nombre de quien lo dijo («un preso contó», «una sobreviviente recuerda»).
+6. Lo marcado PANTALLA no lo dice la voz: aparece en la imagen. Lo marcado SIN VERIFICAR va sin el nombre de quien lo dijo: se dice por su rol («un mecánico contó», «una de las mujeres recuerda»).
@@ -39 +39 @@
-Las versiones en disputa (quién dio una orden, si las puertas estaban cerradas): se cuentan como versiones, cada una con su dueño: «Según los testigos… Los dueños lo negaron». No elegís vos.
+Las versiones en disputa (quién dio una orden, si un aviso llegó a tiempo): se cuentan como versiones, cada una con su dueño: «Según los telegramas… El capitán lo negó ante la comisión». No elegís vos.
@@ -41 +41 @@
-El nombre de los lugares y las personas, como vienen en los datos. Sin traducir, sin acortar, sin «el edificio» cuando el dato dice «Templeman III».
+El nombre de los lugares y las personas, como vienen en los datos. Sin traducir, sin acortar, sin «el edificio» cuando el dato dice el nombre del edificio.
@@ -45 +45 @@
-Los ejemplos son de otros casos. Copiá la técnica, no el contenido.
+Los ejemplos son de un caso que no es el tuyo (una estación de radio y faro en una isla, mil novecientos sesenta y ocho). Copiá la técnica, no el contenido: ninguno de estos nombres, lugares ni cifras está en tus datos.
@@ -48 +48 @@
-«El agua sucia de un inodoro entra en la boca de un hombre. La celda está a oscuras. Bebe para seguir vivo. Miles de hombres han sido abandonados en celdas inundadas por una orden. Nueva Orleans, agosto de 2005. Pero días antes de la sed, llegó la tormenta. Y con ella, una decisión.»
+«Una mujer transmite en clave morse a la luz de una vela. La sala huele a querosén quemado. Afuera, el faro sigue encendido. Once personas esperan un barco que no va a llegar, porque alguien decidió que no llegara. Puerto Cardal, invierno de mil novecientos sesenta y ocho. Pero tres semanas antes de la vela, llegó un telegrama. Y con él, una orden.»
@@ -50,2 +50,2 @@
-Escena con los sentidos, sin inventar hechos (todo sale de "agua contaminada hasta el pecho, olor a aguas residuales y diésel, celdas cerradas"):
-«El 30 de agosto, el agua sucia de la inundación irrumpió en las celdas. Olía a una mezcla de aguas residuales y combustible diésel. En varios pabellones, los presos quedaron atrapados en sus celdas cerradas. Vieron cómo el nivel subía sin poder hacer nada. Pronto, el agua les llegaría hasta el pecho.»
+Escena con los sentidos, sin inventar hechos (todo sale de «olor a querosén, ventanas tapadas con mantas, el ruido del generador que se apaga, el silencio después»):
+«La noche del catorce, el generador tosió dos veces y se apagó. Por primera vez en tres semanas la estación quedó en silencio. Las ventanas estaban tapadas con mantas para guardar el calor. Olía a querosén. Alguien encendió una vela y la sala apareció, chica, llena de gente que no hablaba.»
@@ -54 +54 @@
-«El oficial Renard Reed también fue testigo. "Parecía que estaban abatiendo a la gente", dijo Reed. Vio a alguien caer al agua. No sabía si la munición era real o de goma. Fue suficiente. Lo vio.»
+«Teo Marín iba en el Alborada esa mañana. "El capitán leyó el papel y dio la vuelta", dijo Marín. No supo qué decía el papel. Vio la isla a lo lejos. Vio que se alejaba.»
@@ -56,2 +56,2 @@
-El hecho concreto en vez del juicio (no dice "cruel", "abandono", "inhumano"):
-«Pearl debe 398 dólares en multas. Por esa deuda sigue encerrada cuando llega el huracán. Meses después, en junio, una abogada consigue la orden que la libera.»
+El hecho concreto en vez del juicio (no dice «cruel», «abandono», «inhumano»):
+«Elvira pidió el barco siete veces. Las siete respuestas dicen lo mismo: mantener servicio. Ninguna tiene firma.»
@@ -60 +60 @@
-«Los internos encuentran una barra metálica en el techo. La arrancan. La llevan contra la pared. El miércoles por la mañana, en CCC, la barra golpea los bloques de hormigón. Una vez. Otra. Hasta que la pared cede.»
+«Bascuñán mira la silla. La levanta. La rompe contra el piso de la sala de radio y mete las patas en la estufa. Esa noche, mientras la madera arde, Elvira transmite con las baterías del faro. En el cuarto de al lado, el niño deja de toser. Nadie lo dice. Lo saben.»
@@ -63 +63 @@
-«Una empleada declaró que la orden de cerrar las puertas vino del dueño. Los Paiva lo negaron ante el tribunal. El guardia reconoció que recibió una orden por radio. Las puertas de vidrio, esa mañana, no se abrieron.»
+«Según los telegramas que Elvira guardó, el Alborada zarpó y recibió orden de volver. El capitán declaró ante la comisión que nunca salió del puerto por el temporal. El barco, esa semana, no llegó.»
@@ -66 +66 @@
-«Los sobrevivientes fueron repartidos por prisiones de todo el estado. Cuando se armó la lista de los evacuados, faltaban cientos de nombres.»
+«Cuando el Alborada entró por fin a la bahía, el padre Quiroga contó a los que bajaron a recibirlo. Faltaban dos. Las familias decían que tres.»
@@ -69 +69 @@
-«Renard Reed no habla de una lista. Habla de los hombres que estaban encerrados: "Aunque estén en la cárcel, son seres humanos".»
+«Elvira Soto no habla de la comisión. Habla de su libro de telegramas: "Yo mandaba los telegramas. Nadie me dijo que los leyeran".»
@@ -76 +76 @@
-- Explicar lo obvio: «Los hombres a los que se refiere son los presos que intentan salir.» → Se corta. El oyente ya lo sabe.
+- Explicar lo obvio: «Los hombres a los que se refiere son los que intentan salir.» → Se corta. El oyente ya lo sabe.
@@ -81 +81 @@
-- Juicio disfrazado de pregunta: «¿Doce años son suficientes por cientos de vidas?» → Se da el dato: «Doce años. Trescientos veintisiete muertos.»
+- Juicio disfrazado de pregunta: «¿Veintitrés días son suficientes para que alguien conteste un telegrama?» → Se da el dato: «Veintitrés días. Siete telegramas. Ninguna firma.»
@@ -83,2 +83,2 @@
-- Telegrama: «Víctor busca la puerta de blíndex.» como párrafo entero, y el siguiente «Otros corren hacia el acceso de Artigas.» → Es la misma escena: Víctor con el niño en brazos, la puerta de vidrio que no abre, la gente que vuelve del portón de Artigas y choca con los que vienen detrás. Un párrafo, con lo que se ve.
-- Gancho abstracto: «Una avalancha de cuerpos empuja hacia adentro. Según una sobreviviente, cuando empezó el fuego alguien dio la orden…» → El gancho es una imagen concreta en curso (las cenizas cayendo del cielorraso, el calor de horno), no una explicación de lo que pasó.
+- Telegrama: «Elvira busca las baterías del faro.» como párrafo entero, y el siguiente «Bascuñán rompe una silla.» → Es la misma escena: el generador apagado, la vela, Elvira con las baterías, Bascuñán con la silla, el niño en el cuarto de al lado. Un párrafo, con lo que se ve.
+- Gancho abstracto: «Una orden sin firma condenó a una isla. Según una sobreviviente, cuando llegó el telegrama alguien decidió…» → El gancho es una imagen concreta en curso (la mujer transmitiendo a la luz de una vela, el olor a querosén), no una explicación de lo que pasó.
```
