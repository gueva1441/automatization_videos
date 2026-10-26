# F34 B.2 — comparación línea por línea contra §1 (agente `simulador`, íntegra)

Solo lectura, sobre `lab/hyperframes/f34/GUION_PANTALLA.json`, los `rotulista_chNN.raw.json` y los `sellos_clima_chNN.json` de `output/f8s3-vajont-f30/_fase2b_work/`. Los segundos son t_mp4.

**Totales reales contra los esperados**

| | esperado §1 | salió | veredicto |
|---|---|---|---|
| textos | 9 | **5**: D117, D71, T39, D192, D245 | no |
| relojes + tarjeta | 4 + tarjeta | 4 (ch01 76.04, ch04 390.63, ch05 596.49, ch07 943.57) + tarjeta 0.0 | sí |
| aguas | 2 | 2 (ch03 250.73 OLA 20 m, ch04 464.06 COTA 715 m) | sí |
| sellos | 8 | **7**: PÁNICO, AMENAZA ×4, INMINENTE, SILENCIO | no |
| punches | 6 | 6 (ch02 183.67, ch03 250.73, ch04 458.27, ch05 527.13, ch06 707.5, ch07 877.07) | sí |

- El F34_REPORT de CC dice «6 textos» y «8 sellos». Ambas cuentas son erróneas.
- El chequeo «texto sin lectura» del propio guion dice «5 con su lectura».
- Cuento solo los eventos con `queda: true` de tipo ficha, recorte, lupa o persona.
- Los de lista de §1 que sí salieron: D117, T39, D192, D245. D71 salió en lugar de D49.

**ch01** (una sola escena, gancho)

| esperado §1 | salió | coincide | por qué |
|---|---|---|---|
| texto D118 «LA PRESA DEL VAJONT · 266 m de alto», ancla «la presa que todos creyeron caída sigue en pie» (0:10) | sin texto | no | El modelo propuso D195 (idx 2, rank 1) y no D118. Ver caso 1. |
| tarjeta «9 OCT 1963 · 22:39» en 0:00 | 0.0, dur 3.0, fuente escaleta.pico T57+T66 | sí | |
| sello PÁNICO | PÁNICO 39.94 (crítico: suma) | sí | |
| reloj 9 OCT 1963 en «Longarone, Italia, nueve de octubre…» | reloj `9 OCT · 1963` 76.04, dur 8.32 | sí | |
| punches | cuatro punch_in del director cortados por `duplica` (el zoom_punch del pico los reemplaza) | n/a | |

**ch02**

| esperado §1 | salió | coincide | por qué |
|---|---|---|---|
| D117 «ACTA DEL CONSEJO SUPERIOR · 13 de 34 representantes presentes» | recorte D117 128.7, dur 6.52, lectura 6.2: «CONSEJO SUPERIOR DE OBRAS PÚBLICAS, 1943 · Aprobó la presa con 13 de 34…» | sí (dato y ancla) | La etiqueta no es la esperada, pero el dato es el mismo y el crítico dio sí/sí/no estorba. «1943» queda en la etiqueta, aunque A.1 pedía no poner el año. |
| sellos CALMA, AMENAZA | ninguno | no | CALMA 162.28 cortado por crítico («tinte de muerte contradice la escena de vida»). AVISO 175.84 (beat 3) cortado por crítico («tinte de agua sobre montaña sin relación»). Los candidatos AMENAZA y los demás cayeron por el filtro «un sello por beat» (el beat ya tenía CALMA o AVISO). Ver caso 5. |
| punch | zoom_punch 183.67 | sí | |

**ch03**

| esperado §1 | salió | coincide | por qué |
|---|---|---|---|
| D49 «ANCHO DE LA FISURA · Más de 1 metro» | ficha D71 «L'UNITÀ · Diario del Partido Comunista Italiano» 316.2 (dur 4.94, lectura 2.93) | no | D49 se propuso, pero se cortó. Ver caso 2. |
| agua `OLA · 20 m` (Pontesei) | nivel de agua OLA 20 m 250.73, dur 4.81, más zoom_punch en el mismo instante | sí | |
| sello AVISO | AMENAZA 266.66 (crítico: suma) | no | Gemini devolvió AMENAZA (`sellos_clima_ch03.json`); AVISO no apareció. |
| (no esperado) | T21 «VOLUMEN DEL DESLIZAMIENTO» cortado por «beat pico (4): solo a_pantalla» (250.56). T16 persona cortado por candado (256.32). | n/a | El pico del cap es el beat 4, donde A.1 solo deja pasar a_pantalla. |

**ch04**

| esperado §1 | salió | coincide | por qué |
|---|---|---|---|
| T39 «ALERTA DE MERLIN, 1961 · 50 millones de m³» | ficha T39 423.52 «ROCA EN RIESGO DE DERRUMBE SOBRE ERTO · 50 millones de m³» (dur 3.78, lectura 3.6) | sí | |
| reloj 4 NOV 1960 | reloj 390.63, fuente T36, dur 4.43 | sí | |
| agua `COTA AUTORIZADA · 715 m` | 464.06, dur 4.5 | parcial | El bloque cruza el corte de escena 7 (468.03) por 0.5 s. Ver caso 6. |
| (no esperado) | sello AMENAZA 447.24; T33 cortado por lectura (103 caracteres piden 6.9 s y hay 5.0 s); D103, D104 y D68 cortados por «beat pico (7): solo a_pantalla». | n/a | |

**ch05**

| esperado §1 | salió | coincide | por qué |
|---|---|---|---|
| Q50 recorte «Carta del municipio… continua aprensión y alarma» | ninguno | no | Se propuso y se cortó por lectura. Ver caso 3. |
| reloj 9 OCT 1963 | reloj 596.49, fuente T61, dur 12.0 | sí | |
| sello INMINENTE | INMINENTE 660.15 (crítico: suma); además AMENAZA 531.95 | parcial | El INMINENTE salió; el AMENAZA extra es de otro beat. |

**ch06**

| esperado §1 | salió | coincide | por qué |
|---|---|---|---|
| D128 «MUERTOS, RECUENTO OFICIAL · 1.910 personas» | ninguno | no | Ver caso 4. |
| D192 «CENTRO DE CONTROL, ESTRIBO IZQ. · 20 técnicos muertos» | ficha D192 822.23 «TÉCNICOS MUERTOS EN EL CENTRO DE CONTROL · 20 técnicos en el estribo izquierdo» (dur 5.87, lectura 5.0) | sí | |
| sello COLAPSO | ninguno | no | Gemini sí devolvió COLAPSO 4 veces (`sellos_clima_ch06.json`). Cayeron por «un sello por beat: el beat 10 ya tiene INMINENTE», pero ese INMINENTE (710.09) fue cortado después por el crítico. Ver caso 5. |
| sello SILENCIO | SILENCIO 799.03 (crítico: suma) | sí | |

**ch07**

| esperado §1 | salió | coincide | por qué |
|---|---|---|---|
| T85 «REMISIÓN A JUICIO, 1968 · 11 imputados» | ninguno | no | Ver caso 7. |
| D245 «TRIBUNAL DE BELLUNO, 1997 · 55.645.758.500 liras» | ficha D245 994.17 «CONDENA A MONTEDISON, 1997 · 55.645.758.500 liras al municipio de Longarone» (dur 11.76, lectura 4.8) | sí | |
| reloj 20 FEB 1968 | reloj 943.57, fuente T85, dur 12.0 | sí | |
| sello MEMORIA | AMENAZA 897.65 | no | `sellos_clima_ch07.json` trae NINGUNA, AMENAZA, ALARMA, RABIA y SILENCIO. MEMORIA nunca lo devolvió Gemini. |
| (no esperado) | D32 y T102 cortados por «un texto por beat: el beat 13 ya tiene D245» | n/a | |

**Casos a investigar**

1. **ch01 sin texto (D118).**
   - D118 estaba en el pool del gancho (`gancho:true`, `dice_voz:false`, beat 1). Era elegible: la voz no dice 266 m.
   - El modelo no lo propuso ni lo descartó. Descartó P49, P32, D132 y D195, y su único bloque fue D195 (idx 2, palabra 11, 18.82): «LONGARONE, 1963 · 1.269 de 1.328 habitantes murieron».
   - Ese bloque lo cortó el candado (`filtro: candado`): «no están en el texto fuente de D195: ['1963']». El 1963 es del propio rótulo que escribió el modelo.
   - No hubo segundo intento con otro dato. `rotulista_ch01.raw.json` tiene 2 intentos de llamada, y el `final` es el de D195.
   - Hay un dato que sí cabía en el gancho. Coincide con el 1.269 del pool (D195), pero la fecha la inventó el modelo.
   - El gancho tiene `a_pantalla` vacío: ningún ítem de ch01 está marcado a_pantalla. D118 depende solo de la elección del modelo, y esa regla no obliga a ninguno.
2. **ch03 D71 en vez de D49.**
   - El modelo propuso los dos con `rank 1` y `beat 5`: D71 en la oración 13 (palabra 6, 316.2) y D49 en la oración 17 (palabra 22, 348.92).
   - La regla «un texto por beat» cortó el segundo en orden de oración: «un texto por beat: el beat 5 ya tiene D71» (filtro `cantidad`). Ganó el que viene primero, no el de más valor.
   - D49 no es a_pantalla, y el handoff esperaba D49. Con la nueva regla de «dos si son dos datos marcados a_pantalla» tampoco aplica, porque ninguno de los dos está marcado.
   - D71 es un dato débil: solo aclara qué es L'Unità.
   - D49 tenía lectura 2.73 s. Habría cabido, en la escena 11 con corte en 360.44.
3. **Q50 (ch05).**
   - Se propuso en la oración 2, palabra 18 (527.2). `a_pantalla` lo marca como pedido.
   - Lo cortó la lectura: «147 caracteres piden 9.8 s y hay 5.0 s hasta el corte de escena (30.8 s)». El texto es de 147 caracteres porque el modelo reescribió la cita como «El municipio advierte que la población vive en continua alarma y reitera su preocupación por la seguridad».
   - Un recorte más corto de la carta habría cabido. A.1 pide «UNA línea corta», y esta salió de cuatro líneas.
   - La oración ancla (idx 2, «Desde el dos de octubre…», t0 15.24 del cap, 527.2 en mp4) está a 5.0 s del corte de la escena. No es un problema de reparto: la escena de esa oración es corta.
   - El ancla fue la oración equivocada: la carta se lee más adelante, en las oraciones 13 a 15 (T61).
4. **D128 (ch06).**
   - Salió del modelo bien: oración 24, palabra 4, `unidad: personas`, `valor: 1910`, rank 1, más D192 en la misma oración 24 y palabra 4.
   - En el guion se ve con `tipo: contador` y texto «Guglielmo» (812.71, escena 13). Lo cortó `gfx_realizador.finalizar`, no el rotulista: «contador de una cifra que dice la voz (repite el subtítulo)».
   - Confirma el bug de CC: el realizador quita todo `count_up`, también el del rotulista. La cifra 1.910 no la dice la voz en ese cap: el modelo lo anota en el `aporta` («que la narración nunca dice»).
   - El texto «Guglielmo» del evento es sospechoso. El campo `texto` del contador toma la palabra de la oración que ancla y no el valor.
5. **Sellos AMENAZA repetidos entre caps y sellos faltantes.**
   - AMENAZA sale en ch03 (266.66), ch04 (447.24), ch05 (531.95) y ch07 (897.65). La regla A.4 solo impide repetir dentro del mismo cap (`ya salió en el cap`), así que no hay filtro que lo corte.
   - Gemini inclina a AMENAZA. Cuento 1 en ch01, 5 en ch02, 2 en ch03, 3 en ch04, 3 en ch05, 3 en ch06 y 1 en ch07 sobre sus listas. Devolvió AVISO una sola vez y MEMORIA nunca. Con el modelo y el prompt tal cual, cada cap cae a AMENAZA, INMINENTE o ALARMA.
   - Fallan los esperados: ch02 CALMA y AMENAZA, ch03 AVISO, ch06 COLAPSO, ch07 MEMORIA.
   - El filtro «un sello por beat» corre antes que el crítico. Un sello que el crítico después corta igual ocupó el beat: ch02 CALMA (162.28), ch02 AVISO (175.84) y ch06 INMINENTE (710.09). Por eso los demás candidatos del beat quedan cortados y el cap pierde el sello. En ch06, COLAPSO (devuelto 4 veces) cayó por esto.
6. **Agua de ch04 que cruza el corte.**
   - 464.06 + 4.5 s = 468.56. La escena 7 corta en 468.03 (88.03 s del cap contra 88.56 s del bloque). El chequeo del guion lo marca ✗: «termina en 88.56 s y la escena 7 corta en 88.03 s». Son 0.53 s.
   - El mismo agua tiene además un chequeo ✗ «cifra que contradice la voz»: «715 m vs 650 m» y «715 m vs 700 m». La cota 715 m es la que dice la voz, y el chequeo la compara con otras alturas del relato. Es falso positivo, porque 650 y 700 son niveles anteriores del embalse; 715 es la cota autorizada.
   - El agua de A.5 no pasa por «lectura»: su duración 4.5 se fija sin mirar el siguiente corte.
7. **T85 en ch07.**
   - El modelo sí lo propuso: oración 11, palabra 20, beat 12, rank 1, «REMISIÓN A JUICIO · Contra 11 personas por el desastre del Vajont» (943.57, lectura 4.13).
   - Lo cortó «beat pico (12): solo `a_pantalla`». T85 no está marcado a_pantalla (solo D245 lo está en ch07). El spoiler no fue la causa, así que A.2 punto 3 se arregló pero el pico lo cortó por otro lado.
   - En el mismo instante, 943.57, salió el reloj `20 FEB · 1968` (fuente T85, dur 12.0). La fecha está pero el hecho (11 imputados) no. §1 esperaba ambos.

**Lectura**

- Salen bien los relojes, las dos aguas, los seis punches, la tarjeta, D117, T39, D192 y D245.
- Faltan 4 textos de los 9, y los 5 que salen no son idénticos a los esperados (D71 en lugar de D49).
- De los 4 faltantes, tres son decisiones de filtro (D49, T85 y D128) y uno es del modelo (D118). Ninguno es de reparto, salvo que D49 perdió contra D71 por orden de oración. Q50 es de lectura.
- Faltan sellos en ch02, ch03, ch06 y ch07 porque Gemini devolvió otra palabra o el sello cayó por el orden de filtros, no porque la regla no se cumpla.
- El «un sello por beat» antes del crítico cuesta sellos en ch02 y ch06.
