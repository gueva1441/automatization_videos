# F40 §6.4 — la tabla de §3 recalculada por código

`python lab/hyperframes/f40/a/sim_gancho.py` · hoy = código de HEAD 8669045 · F40 = árbol de trabajo. Voz = `entrada.caps` del raw de cada papel (la que vio m01e). Una fila por ficha del gancho que el autor propuso (Kyshtym: ch01 beat 1, intento N del raw de F39).

| tema | dato del gancho (intento, oración) | cifras que encuentra en la voz (con cap y oración) | hoy (HEAD) | con F40 |
|---|---|---|---|---|
| Kyshtym | D03 «ESCALA DE ACCIDENTES NUCLEARES · Nivel 6 de 7» (int. 1, [5]) | hoy (cifras del texto del ítem, `dice_voz`): «7» en ch04 [14] («A las siete y veinte de la tarde, el viento ya había decidido hacia dónde.»), «6» en ch05 [12] («Seis de octubre de mil novecientos cincuenta y siete.») · used_in<br>F40 (cifras del dato de la ficha, `no_dicho`): «6» en ch05 [12] («Seis de octubre de mil novecientos cincuenta y siete.»), «7» en ch04 [14] («A las siete y veinte de la tarde, el viento ya había decidido hacia dónde.») | cae: no_dicho («D03 es del pool del video y la narración lo dice en algún cap (gancho)») | pregunta al autor (4) → otro hecho → **queda** |
| Kyshtym | D50 «LA FUGA, COMPARADA · Chernóbil liberó 19 veces más» (int. 2, [5]) | hoy (cifras del texto del ítem, `dice_voz`): «19» en ch01 [7] («Tenían dieciocho, diecinueve, veinte años.») · used_in<br>F40 (cifras del dato de la ficha, `no_dicho`): «19» en ch01 [7] («Tenían dieciocho, diecinueve, veinte años.») | cae: no_dicho («D50 es del pool del video y la narración lo dice en algún cap (gancho)») | pregunta al autor (2) → otro hecho → **queda** |
| Kyshtym | D03 «NIVEL OFICIAL DEL ACCIDENTE · 6 en una escala de 7» (int. 3, [8]) | hoy (cifras del texto del ítem, `dice_voz`): «7» en ch04 [14] («A las siete y veinte de la tarde, el viento ya había decidido hacia dónde.»), «6» en ch05 [12] («Seis de octubre de mil novecientos cincuenta y siete.») · used_in<br>F40 (cifras del dato de la ficha, `no_dicho`): «6» en ch05 [12] («Seis de octubre de mil novecientos cincuenta y siete.»), «7» en ch04 [14] («A las siete y veinte de la tarde, el viento ya había decidido hacia dónde.») | cae: no_dicho («D03 es del pool del video y la narración lo dice en algún cap (gancho)») | cae: caben («etiqueta 27 + dato 20 = 47 caracteres y en la oración [8] caben 31; en este beat caben como máximo 90 (oración [1])») |
| Kyshtym | D201 «OTRA MUERTE EN LA PLANTA · Valia Dronova, 38 años: pulmones de piedra» (int. 4, [4]) | hoy (cifras del texto del ítem, `dice_voz`): «20» en ch01 [7] («Tenían dieciocho, diecinueve, veinte años.»)<br>F40 (cifras del dato de la ficha, `no_dicho`): ninguna | cae: no_dicho («D201 es del pool del video y la narración lo dice en algún cap (gancho)») | pasa |
| Kyshtym | D03 «NIVEL 6 DE 7 · Escala internacional de accidentes» (int. 5, [1]) | hoy (cifras del texto del ítem, `dice_voz`): «7» en ch04 [14] («A las siete y veinte de la tarde, el viento ya había decidido hacia dónde.»), «6» en ch05 [12] («Seis de octubre de mil novecientos cincuenta y siete.») · used_in<br>F40 (cifras del dato de la ficha, `no_dicho`): ninguna | cae: no_dicho («D03 es del pool del video y la narración lo dice en algún cap (gancho)») | pasa |
| Vajont v6 | D195 «LONGARONE · 1.269 de 1.328 habitantes murieron» (int. —, [2]) | hoy (cifras del texto del ítem, `dice_voz`): ninguna<br>F40 (cifras del dato de la ficha, `no_dicho`): ninguna | pasa | pasa (sin cambio) |

## Detalle por ficha

### Kyshtym · D03 «ESCALA DE ACCIDENTES NUCLEARES · Nivel 6 de 7» (int. 1, [5])
- hoy: cae: no_dicho («D03 es del pool del video y la narración lo dice en algún cap (gancho)»)
- F40 pregunta: D03 (ch01 beat 1, oración [5]) «ESCALA DE ACCIDENTES NUCLEARES · Nivel 6 de 7»: la voz dice «6» en ch05 [12] («Seis de octubre de mil novecientos cincuenta y siete.»); ¿es el mismo hecho? si no, mantenelo
- F40 pregunta: D03 (ch01 beat 1, oración [5]) «ESCALA DE ACCIDENTES NUCLEARES · Nivel 6 de 7»: la voz dice «7» en ch04 [14] («A las siete y veinte de la tarde, el viento ya había decidido hacia dónde.»); ¿es el mismo hecho? si no, mantenelo
- F40 pregunta: D03 (ch01 beat 1, oración [5]) «ESCALA DE ACCIDENTES NUCLEARES · Nivel 6 de 7»: la voz dice «6» en una oración posterior en ch05 [12] («Seis de octubre de mil novecientos cincuenta y siete.»); ¿es el mismo hecho? si no, mantenelo
- F40 pregunta: D03 (ch01 beat 1, oración [5]) «ESCALA DE ACCIDENTES NUCLEARES · Nivel 6 de 7»: la voz dice «7» en una oración posterior en ch04 [14] («A las siete y veinte de la tarde, el viento ya había decidido hacia dónde.»); ¿es el mismo hecho? si no, mantenelo
- F40 con «otro hecho»: queda=True · juicio_autor={"no_dicho": ["6", "7"], "spoiler": ["6", "7"]}

### Kyshtym · D50 «LA FUGA, COMPARADA · Chernóbil liberó 19 veces más» (int. 2, [5])
- hoy: cae: no_dicho («D50 es del pool del video y la narración lo dice en algún cap (gancho)»)
- F40 pregunta: D50 (ch01 beat 1, oración [5]) «LA FUGA, COMPARADA · Chernóbil liberó 19 veces más»: la voz dice «19» en ch01 [7] («Tenían dieciocho, diecinueve, veinte años.»); ¿es el mismo hecho? si no, mantenelo
- F40 pregunta: D50 (ch01 beat 1, oración [5]) «LA FUGA, COMPARADA · Chernóbil liberó 19 veces más»: la voz dice «19» en una oración posterior en ch01 [7] («Tenían dieciocho, diecinueve, veinte años.»); ¿es el mismo hecho? si no, mantenelo
- F40 con «otro hecho»: queda=True · juicio_autor={"no_dicho": ["19"], "spoiler": ["19"]}

### Kyshtym · D03 «NIVEL OFICIAL DEL ACCIDENTE · 6 en una escala de 7» (int. 3, [8])
- hoy: cae: no_dicho («D03 es del pool del video y la narración lo dice en algún cap (gancho)»)
- F40: cae caben: etiqueta 27 + dato 20 = 47 caracteres y en la oración [8] caben 31; en este beat caben como máximo 90 (oración [1])

### Kyshtym · D201 «OTRA MUERTE EN LA PLANTA · Valia Dronova, 38 años: pulmones de piedra» (int. 4, [4])
- hoy: cae: no_dicho («D201 es del pool del video y la narración lo dice en algún cap (gancho)»)

### Kyshtym · D03 «NIVEL 6 DE 7 · Escala internacional de accidentes» (int. 5, [1])
- hoy: cae: no_dicho («D03 es del pool del video y la narración lo dice en algún cap (gancho)»)

### Vajont v6 · D195 «LONGARONE · 1.269 de 1.328 habitantes murieron» (int. —, [2])
- hoy: pasa

