# F60 — Salida A (casillero `persona` en m03) — PARADA A

Handoff `lab/hyperframes/f60/HANDOFF_F60_madre_personas_secuencia.md` (md5 `a2e7e8cb4a6e62c52fdccc5b58c7b1ac`, verificado), Etapa A con los dos cambios del analista (input del canon con el nombre + texto del casillero byte a byte; borrado de `_format_visual_canon_block`). Sobre la copia de lab `lab/hyperframes/f60/base/`. Cero fotos. Runner `lab/hyperframes/f60/etapa_a_m03.py` → `a/etapa_a.json`, `a/etapa_a.log`, `a/03_visual_antes.json`, `a/03_visual_despues.json` (y la corrida 1 aparte, §A.4).

**Resultado en una línea:** el casillero `persona` llega a las 96 fotos (caps flux, supps e `image_f8` de los caps con clip), con nombres exactos del canon y sin nombres en la prosa; pero Opus **deja a Daniel Écija fuera** en la mayoría de sus escenas (4 de 96 fotos lo nombran; la tabla de verdad esperaba ≈ 9): cuando la voz dice «se casan», «van juntos», «mi marido», «los Écija» o nombra a otro en la misma oración, `persona` trae solo al nombrado o `[]`. Dos PARÁ: (1) el grep de nombres da 2 coincidencias, las dos con el apellido «Court» como sustantivo (`Supreme Court room`, `Federal Court courtroom`); (2) m03 vuelve a elegir anclas y el `_steps` de producción tiene un guion nuevo del 29-oct 20:55 que no es el del 03_visual ni el del audio (§A.4), así que la tabla de verdad se comparó por ancla, no solo por índice.

## A.1 Código (producción: solo lo que dice la Etapa A + la chascada)

| archivo | cambio |
|---|---|
| `script_engine/m03_visual.py` | **Input** (`_format_seedream_canon_block`): encabezado «PERSONAS DOCUMENTADAS (el nombre es solo para el casillero persona; en la prosa usar appearance_canon, NUNCA el nombre):» y cada persona empieza con su `name` (`• {name} ¦ role: … ¦ age … ¦ era: …`). **Salida**: `TEXTO_PERSONA` (byte a byte el bloque del handoff; verificado en código contra la cadena del handoff) concatenado tras `TEXTO_S4_YEAR` en `_si_casilleros`. **Esquema** (`_casilleros_schema`): `persona` ARRAY de STRING, `required` = […, "year", "people_group", "persona"]. `CLAVES_F8_PAPEL` += `"persona"` (llega a las supps y a `image_f8` de los caps con clip). **Chascada:** `_format_visual_canon_block` borrado entero (grep antes de borrar: 0 llamadores; solo la nombraban su docstring vecino y el test 133); el docstring de `_format_seedream_canon_block` lo dice. CRLF intacto. |
| `asset_manager.py` | `_iter_image_items` devuelve `"persona"` (lista de str; `[]` en guion legacy). Nadie la consume (Etapa B). CRLF intacto. |
| `script_engine/m03_imagenes_v3.py` | sin cambios: `persona` NO entra en `CASILLEROS_EDITABLES`. |
| `test_module_f50b.py` | el SI termina en `TEXTO_2_PEOPLE_GROUP + TEXTO_S4_YEAR + TEXTO_PERSONA`; `required[-3:] == ["year", "people_group", "persona"]`; esquema de `persona`. |
| `test_module_m03_reglas_133.py` | sin la verificación de que `_format_visual_canon_block` exista (y su nota de alcance). Su otra falla (`fixture topic ec3d7c7f… no está en topics_db`) es previa: la versión de HEAD falla igual. |
| `test_module_f59_a1.py`, `test_module_f58_a3.py` | 5 tests byte-idénticos comparan el prompt de Opus de HOY con la versión de `git show` de antes; fallaban solo por el bloque del canon (el nombre y el encabezado, cambio declarado). Adaptación mínima: el módulo viejo toma `_format_seedream_canon_block` del nuevo (`monkeypatch`), el resto sigue byte a byte. |
| stickers `fase2a.json` (m03_visual: `entrega` + `funciones_muertas` sin el builder borrado), `orquestador.json` (asset_manager: `recibe`) · `lab/tools/mapa_modulos.py` regenerado, `--check` 0 fallas | |

Suites (`lab/hyperframes/f41/f60a/`): ch02 md5 `f792f3d483a1fa42daed5f7f0e054f46` (candado), rápida 53 verdes + 3 skipped, amplia **1294 verdes + 31 skipped + 3 xfail + 5 fallas** = las 4 previas (`m03_merge_timing` ×2, `gfx_lab` ×2: `test_cues_sin_escribir_el_proyecto`, `test_preview_usa_las_plantillas_reales`) + `test_module_gfx_lab.py::test_candado_en_el_preview`, que pasa sola y ya falló en las corridas f50c, f50f, f51c y f55a (flaky, no de esta tanda). La primera pasada (`suite_amplia.log`, antes de adaptar los 5 byte-idénticos) dio 10 fallas; `suite_amplia_2.log` es la definitiva.

## A.2 Prueba: m03 sobre la copia (corrida 2, la que vale) · 134,8 s · US$ 2,2494 (cost_tracker, Opus + Flash)

Entradas: las del guion ANTERIOR, que son las del 03_visual de la copia (ver §A.4): `01a_escaleta`, `01a_skeleton`, `01b_narracion_v3`, `01b_narration` de `lab/hyperframes/f54/antes/` (respaldo del 29-oct 18:34; 96/96 anclas del 03_visual anterior están en esa narración), `00_pool_v3` de `lab/hyperframes/f44/B/_steps/<tid>/` (27-oct), `ficha_caso`, `_perfil`, `05_visual_canon` de producción; topic de `topics_db` (sin `asegurar_canon`, que escribe); `sync_map` del audio de producción. `m03_visual.STEPS_DIR` → la copia. 96 fotos (0+4 / 16 / 16 / 14 / 16 / 16 / 0+12, igual que antes), las 96 con clave `persona`, 23 no vacías; `image_f8.persona` en los caps 1 y 7 (`[]` los dos). Daniel Écija: **4 fotos**.

### Tabla foto → `persona` contra la tabla de verdad (por índice y por ancla; m03 vuelve a elegir anclas en el paso 1, así que 8 de las 16 referencias cambiaron de índice)

| referencia (del 03_visual anterior) | esperado (analista) | `persona` en ese índice ahora | resultado | dónde está la escena ahora | lectura de CC |
|---|---|---|---|---|---|
| `chapters[1].img[0]` | Daniel Écija | `[]` | **DESACUERDO** | misma ancla, mismo índice; escena: la pareja se conoce en el baile | Opus dejó `[]`: el párrafo no nombra a Daniel hasta «Allí María Bernal conoció a Daniel» (siguiente oración); la foto es la pareja, Daniel tendría que estar. |
| `chapters[1].img[1]` | Daniel Écija | `['María Bernal']` | **PARCIAL** | misma ancla, mismo índice; escena: la boda | `['María Bernal']`: «se casan» son los dos; Daniel falta. |
| `chapters[1].img[3]` | Daniel Écija (+ María Bernal) | `['María Bernal']` | **PARCIAL** | misma ancla, mismo índice; escena: la pareja en el barco | `['María Bernal']`: «van juntos» + «mi marido» en el párrafo; Daniel falta (la tabla lo esperaba primero, con María). |
| `chapters[1].img[4]` | Daniel Écija (+ quizá Ramón de Juan) | `['María Bernal']` | **DESACUERDO** | la ancla vieja («otra pareja, Milagros Barroso y Ramón de Juan») está ahora en img[5]; img[4] pasó a «Iba pegadita a mi marido» | img[5] (dos parejas) → `['Milagros Barroso', 'Ramón de Juan']`: Ramón sí, pero Daniel y María (la pareja protagonista, «se hicieron amigos») faltan. img[4] → `['María Bernal']` sin Daniel («mi marido»). |
| `chapters[1].img[5]` | NO Daniel | `['Milagros Barroso', 'Ramón de Juan']` | ACUERDO | la ancla vieja («Esa familia madrileña…») está ahora en img[6] | img[6] → `['Milagros Barroso', 'Víctor Calvo']`: sin Daniel, como pide la tabla. |
| `chapters[2].img[15]` | Daniel Écija | `[]` | **DESACUERDO** | ancla nueva: «En 1961 la producción subió. Al año siguiente, los Écija bajaban a esa pista»; la pareja bajando del avión | `[]` con «los Écija» en la ancla y la pareja como sujeto: Daniel (y María) tendrían que estar. Opus no leyó el apellido como la persona. |
| `chapters[3].img[6]` | Daniel Écija (dudoso: podría ser Ramón) | `[]` | n/a (escena cambió) | la ancla vieja («…nació un niño») está en img[7] y la foto es el hospital sin gente; img[6] es el suelo del pueblo | `[]` en las dos: correcto para esas escenas (no hay persona). La escena «Daniel espera fuera del hospital» no se volvió a elegir. |
| `chapters[3].img[8]` | Daniel Écija | `['Ramón de Juan']` | **DESACUERDO** | img[8] ancla «Daniel trabajaba en la mina. Ramón de Juan, el amigo, hacía jornadas de 16 h» (mineros saliendo); la ancla vieja (explosión del primer día) está en img[9] | img[8] → `['Ramón de Juan']`: la voz nombra a los dos y Opus eligió al nombrado con oración propia; Daniel falta. img[9] (mineros tras la explosión, «el primer día de trabajo de su padre») → `[]`: Daniel falta. |
| `chapters[3].img[13]` | Daniel Écija | `['María Bernal', 'Daniel Écija']` | ACUERDO | ancla ampliada («Después de esa foto, las maletas… Se fueron antes de que nadie les dijera nada»); familia de espaldas | `['María Bernal', 'Daniel Écija']`: Daniel está (de espaldas, con cojera); el orden pone a María primero (la tabla espera a Daniel como principal). |
| `chapters[4].img[4]` | Daniel Écija o "" | `[]` | ACUERDO | misma ancla, mismo índice; familia entrando a su casa en Madrid, 1966 | `[]`: aceptable según la tabla («Daniel Écija o ""»). |
| `chapters[4].img[12]` | "" | `[]` | ACUERDO | img[12] ancla «Madrid, 1991. Daniel Écija va al médico» (hombre de 55 de espaldas ante el médico) | `[]`: 1991, 55 años → no es la edad del canon (1962-1963), como pide la regla y la tabla. |
| `chapters[4].img[13]` | "" | `[]` | ACUERDO | img[13] ancla «Nueve meses. Daniel muere…» (cama vacía) | `[]`. |
| `chapters[4].img[14]` | "" | `[]` | ACUERDO | img[14] ancla «María… rodeada de fotografías en sepia» (foto enmarcada del minero con el pie vendado) | `[]`: foto dentro de la foto, como pide la regla. |
| `chapters[0].supp[0]` | "" | `['Daniel Écija']` | n/a (escena cambió) | misma ancla; la escena pasó de «solo el pie» a «la familia posa para el retrato, el minero con el pie vendado» | `['Daniel Écija']`: correcto para la escena nueva (Daniel entero, de frente). La tabla esperaba `""` porque la foto vieja era solo el pie. |
| `chapters[0].image_prompt` | Daniel Écija | `[]` | n/a (escena cambió) | la foto del clip pasó a «con el pie envuelto en una venda blanca» (detalle del pie) | `[]` en `image_f8.persona`: correcto para un plano de solo una parte del cuerpo. La escena vieja (el joven posa con el pie vendado) quedó en supp[1] («El hombre se llama Daniel Écija y es minero») → `['Daniel Écija']`, de acuerdo con la tabla. |
| `chapters[0].supp[3]` | Daniel Écija | `[]` | n/a (escena cambió) | misma ancla; la escena pasó de «familia posa ante la pared» a «copia vieja en blanco y negro de la foto de familia» | `[]`: foto dentro de la foto → correcto según la regla; la tabla esperaba Daniel para la escena vieja. |

Cuenta: **6 desacuerdos/parciales en los que falta Daniel** (baile, boda, barco, dos parejas, «los Écija» en la pista, mineros), **7 acuerdos**, 3 filas en las que m03 cambió la escena (y el valor es correcto para la escena nueva). Patrón: Opus pone en `persona` a quien la voz nombra en la ancla o muy cerca («María Bernal», «Ramón de Juan», «Víctor Calvo»); «él», «mi marido», «se casan», «la pareja», «los Écija» no le alcanzan para poner a Daniel, aunque el párrafo entero sea sobre los Écija. Es exactamente la minoría de menciones que el analista simuló; el texto del casillero («recognisably shown… if unsure, []») empuja al `[]`.

Anclas y párrafos de cada fila:
- `chapters[1].img[0]` · ancla anterior: «Dieciséis de septiembre de mil novecientos sesenta y uno. En el salón de baile del Círculo de Bellas Artes de Madrid, Daniel Écija conoce a …» · ancla ahora en ese índice: «Dieciséis de septiembre de mil novecientos sesenta y uno. En el salón de baile del Círculo de Bellas Artes de Madrid, Daniel Écija conoce a …» · párrafo: «Dieciséis de septiembre de mil novecientos sesenta y uno. En el salón de baile del Círculo de Bellas Artes de Madrid, Daniel Écija conoce a María Bernal. Un año después se casan: el jueves veinte de septiembre de mil novecientos sesenta y dos. Cuatro días más tarde ya están en el barco. Van a Australia con el acuerdo migratorio por el que pasaron cerca de ocho mil españoles. De Wittenoom no saben nada; saben que hay …»
- `chapters[1].img[1]` · ancla anterior: «Un año después se casan: el jueves veinte de septiembre de mil novecientos sesenta y dos. Cuatro días más tarde ya están en el barco.» · ancla ahora en ese índice: «Un año después se casan: el jueves veinte de septiembre de mil novecientos sesenta y dos.» · párrafo: «Dieciséis de septiembre de mil novecientos sesenta y uno. En el salón de baile del Círculo de Bellas Artes de Madrid, Daniel Écija conoce a María Bernal. Un año después se casan: el jueves veinte de septiembre de mil novecientos sesenta y dos. Cuatro días más tarde ya están en el barco. Van a Australia con el acuerdo migratorio por el que pasaron cerca de ocho mil españoles. De Wittenoom no saben nada; saben que hay …»
- `chapters[1].img[3]` · ancla anterior: «De Wittenoom no saben nada; saben que hay trabajo y que van juntos. «Iba pegadita a mi marido, como una niña», recuerda su mujer.» · ancla ahora en ese índice: «De Wittenoom no saben nada; saben que hay trabajo y que van juntos.» · párrafo: «Dieciséis de septiembre de mil novecientos sesenta y uno. En el salón de baile del Círculo de Bellas Artes de Madrid, Daniel Écija conoce a María Bernal. Un año después se casan: el jueves veinte de septiembre de mil novecientos sesenta y dos. Cuatro días más tarde ya están en el barco. Van a Australia con el acuerdo migratorio por el que pasaron cerca de ocho mil españoles. De Wittenoom no saben nada; saben que hay …»
- `chapters[1].img[4]` · ancla anterior: «Con el tiempo se hicieron amigos íntimos de otra pareja, Milagros Barroso y Ramón de Juan.» · ancla ahora en ese índice: ««Iba pegadita a mi marido, como una niña», recuerda su mujer.» · párrafo: «Dieciséis de septiembre de mil novecientos sesenta y uno. En el salón de baile del Círculo de Bellas Artes de Madrid, Daniel Écija conoce a María Bernal. Un año después se casan: el jueves veinte de septiembre de mil novecientos sesenta y dos. Cuatro días más tarde ya están en el barco. Van a Australia con el acuerdo migratorio por el que pasaron cerca de ocho mil españoles. De Wittenoom no saben nada; saben que hay …»
- `chapters[1].img[5]` · ancla anterior: «Esa familia madrileña había hecho el mismo viaje un mes antes. Un niño que hizo ese viaje todavía recuerda el calor.» · ancla ahora en ese índice: «Con el tiempo se hicieron amigos íntimos de otra pareja, Milagros Barroso y Ramón de Juan.» · párrafo: «Dieciséis de septiembre de mil novecientos sesenta y uno. En el salón de baile del Círculo de Bellas Artes de Madrid, Daniel Écija conoce a María Bernal. Un año después se casan: el jueves veinte de septiembre de mil novecientos sesenta y dos. Cuatro días más tarde ya están en el barco. Van a Australia con el acuerdo migratorio por el que pasaron cerca de ocho mil españoles. De Wittenoom no saben nada; saben que hay …»
- `chapters[2].img[15]` · ancla anterior: ««porque estaban acostumbrados; lo esperaban», dijo McNulty. En mil novecientos sesenta y uno la producción subió. Al año siguiente, los Écij…» · ancla ahora en ese índice: «En mil novecientos sesenta y uno la producción subió. Al año siguiente, los Écija bajaban de aquel avión.» · párrafo: «CSR venía de la industria azucarera y tenía muy poca experiencia en minas. Los reguladores del Estado hicieron poco más que emitir advertencias y pedir equipos para el polvo. Jim McNulty lo explicó así: cuando las Casandras advirtieron que el polvo era un problema y predijeron la enfermedad, en la industria minera no se encendieron las alarmas, «porque estaban acostumbrados; lo esperaban», dijo McNulty.»
- `chapters[3].img[6]` · ancla anterior: «Y en ese pueblo, en junio de mil novecientos sesenta y tres, nació un niño.» · ancla ahora en ese índice: «El pueblo entero estaba hecho de eso.» · párrafo: «Los chicos del pueblo juegan con el mineral. Víctor Calvo lo cuenta: «Nosotros jugábamos con él y lo íbamos deshilachando. Nos lo metíamos en la boca. Cuando lo tocábamos salía un polvillo que lo impregnaba todo». Estaban rodeados de amianto azul y no les daba miedo. Tampoco había dónde no estar rodeados. Los relaves del molino se usaron para construir el pueblo y la pista de aterrizaje. Se extendieron como suelo en …»
- `chapters[3].img[8]` · ancla anterior: «Uno de los hijos de Daniel cuenta que el primer día de trabajo de su padre hubo una explosión y murió gente.» · ancla ahora en ese índice: «Daniel trabajaba en la mina. Ramón de Juan, el amigo, hacía jornadas de dieciséis horas.» · párrafo: «Daniel trabajaba en la mina. Ramón de Juan, el amigo, hacía jornadas de dieciséis horas. Uno de los hijos de Daniel cuenta que el primer día de trabajo de su padre hubo una explosión y murió gente. En marzo de mil novecientos sesenta y tres, Milagros Barroso dio a luz en Wittenoom a John Patrick. Tres meses después le tocó a María. Llegó al hospital de Wittenoom debilitada por una infección renal. El bebé era muy gra…»
- `chapters[3].img[13]` · ancla anterior: «Se fueron antes de que nadie les dijera nada. Nadie les había dicho nada.» · ancla ahora en ese índice: «Después de esa foto, las maletas. Diez meses en Wittenoom. Se fueron antes de que nadie les dijera nada. Nadie les había dicho nada.» · párrafo: «Daniel trabajaba en la mina. Ramón de Juan, el amigo, hacía jornadas de dieciséis horas. Uno de los hijos de Daniel cuenta que el primer día de trabajo de su padre hubo una explosión y murió gente. En marzo de mil novecientos sesenta y tres, Milagros Barroso dio a luz en Wittenoom a John Patrick. Tres meses después le tocó a María. Llegó al hospital de Wittenoom debilitada por una infección renal. El bebé era muy gra…»
- `chapters[4].img[4]` · ancla anterior: «Ese mismo año, los Écija entran a su casa en Madrid.» · ancla ahora en ese índice: «Ese mismo año, los Écija entran a su casa en Madrid.» · párrafo: «Diciembre de mil novecientos sesenta y seis. James Vernon anuncia que CSR cierra Wittenoom. No lo cierra el polvo: lo cierra el dinero. El molino se apaga y el polvo se asienta sobre las cintas. Afuera, en los desfiladeros, quedan más de tres millones de toneladas de relaves. Nadie los mueve. De los hombres que habían pasado por la mina, cincuenta y nueve de cada cien se habían ido antes de cumplir seis meses. Ese mi…»
- `chapters[4].img[12]` · ancla anterior: «Seis años después de aquel control, su padre fue al médico.» · ancla ahora en ese índice: «Madrid, mil novecientos noventa y uno. Daniel Écija va al médico. Le hacen pruebas. La palabra es mesotelioma.» · párrafo: «Mil novecientos ochenta y cinco. Un aeropuerto australiano, un puesto de control. El agente abre el documento de Daniel Écija hijo, lee el lugar de nacimiento, baja la cabeza hacia el papel, vuelve a mirarlo. «Así que de Wittenoom, ¿eh? Un sitio terrorífico», dijo el policía. Para entonces, desde mil novecientos setenta y ocho, el gobierno del Estado venía reduciendo el pueblo y empujando a la gente a irse, por las f…»
- `chapters[4].img[13]` · ancla anterior: «Madrid, mil novecientos noventa y uno. Daniel Écija va al médico. Le hacen pruebas. La palabra es mesotelioma. Nueve meses.» · ancla ahora en ese índice: «Nueve meses. Daniel muere a los cincuenta y cinco años, veintiocho años después de la foto del bautizo.» · párrafo: «Madrid, mil novecientos noventa y uno. Daniel Écija va al médico. Le hacen pruebas. La palabra es mesotelioma. Nueve meses. Daniel muere a los cincuenta y cinco años, veintiocho años después de la foto del bautizo. Décadas más tarde, María está en una habitación rodeada de fotografías en sepia. Entre ellas, la del pie vendado. «Me pegué a mi marido, como una niña pequeña», dice la viuda.»
- `chapters[4].img[14]` · ancla anterior: «Daniel muere a los cincuenta y cinco años, veintiocho años después de la foto del bautizo. Décadas más tarde, María está en una habitación r…» · ancla ahora en ese índice: «Décadas más tarde, María está en una habitación rodeada de fotografías en sepia. Entre ellas, la del pie vendado. «Me pegué a mi marido, com…» · párrafo: «Madrid, mil novecientos noventa y uno. Daniel Écija va al médico. Le hacen pruebas. La palabra es mesotelioma. Nueve meses. Daniel muere a los cincuenta y cinco años, veintiocho años después de la foto del bautizo. Décadas más tarde, María está en una habitación rodeada de fotografías en sepia. Entre ellas, la del pie vendado. «Me pegué a mi marido, como una niña pequeña», dice la viuda.»
- `chapters[0].supp[0]` · ancla anterior: «En el retrato de familia todos miran a cámara menos el pie: está vendado, y la herida que le hizo un trozo de amianto no cierra.» · ancla ahora en ese índice: «En el retrato de familia todos miran a cámara menos el pie: está vendado, y la herida que le hizo un trozo de amianto no cierra.» · párrafo: «Un hombre joven posa para una foto con el pie envuelto en una venda blanca. Detrás, tierra roja y paredes de chapa. En el retrato de familia todos miran a cámara menos el pie: está vendado, y la herida que le hizo un trozo de amianto no cierra. El hombre se llama Daniel Écija y es minero. Vino de Madrid. Wittenoom, Australia Occidental, mil novecientos sesenta y dos. Para entender ese pie hay que volver a un baile en…»
- `chapters[0].image_prompt` · ancla anterior: «Un hombre joven posa para una foto con el pie envuelto en una venda blanca.» · ancla ahora en ese índice: «con el pie envuelto en una venda blanca» · párrafo: «Un hombre joven posa para una foto con el pie envuelto en una venda blanca. Detrás, tierra roja y paredes de chapa. En el retrato de familia todos miran a cámara menos el pie: está vendado, y la herida que le hizo un trozo de amianto no cierra. El hombre se llama Daniel Écija y es minero. Vino de Madrid. Wittenoom, Australia Occidental, mil novecientos sesenta y dos. Para entender ese pie hay que volver a un baile en…»
- `chapters[0].supp[3]` · ancla anterior: «Para entender ese pie hay que volver a un baile en Madrid, un año antes de la foto.» · ancla ahora en ese índice: «Para entender ese pie hay que volver a un baile en Madrid, un año antes de la foto.» · párrafo: «Un hombre joven posa para una foto con el pie envuelto en una venda blanca. Detrás, tierra roja y paredes de chapa. En el retrato de familia todos miran a cámara menos el pie: está vendado, y la herida que le hizo un trozo de amianto no cierra. El hombre se llama Daniel Écija y es minero. Vino de Madrid. Wittenoom, Australia Occidental, mil novecientos sesenta y dos. Para entender ese pie hay que volver a un baile en…»

### Todas las fotos con `persona` no vacía (corrida 2)

| foto | `persona` | año | ancla |
|---|---|---|---|
| `chapters[0].supp[0]` | `['Daniel Écija']` | 1962 | En el retrato de familia todos miran a cámara menos el pie: está vendado, y la herida que … |
| `chapters[0].supp[1]` | `['Daniel Écija']` | 1962 | El hombre se llama Daniel Écija y es minero. |
| `chapters[1].img[1]` | `['María Bernal']` | 1962 | Un año después se casan: el jueves veinte de septiembre de mil novecientos sesenta y dos. |
| `chapters[1].img[3]` | `['María Bernal']` | 1962 | De Wittenoom no saben nada; saben que hay trabajo y que van juntos. |
| `chapters[1].img[4]` | `['María Bernal']` | 1962 | «Iba pegadita a mi marido, como una niña», recuerda su mujer. |
| `chapters[1].img[5]` | `['Milagros Barroso', 'Ramón de Juan']` | 1963 | Con el tiempo se hicieron amigos íntimos de otra pareja, Milagros Barroso y Ramón de Juan. |
| `chapters[1].img[6]` | `['Milagros Barroso', 'Víctor Calvo']` | 1962 | Esa familia madrileña había hecho el mismo viaje un mes antes. |
| `chapters[1].img[7]` | `['Víctor Calvo']` | 1962 | Un niño que hizo ese viaje todavía recuerda el calor. Víctor Calvo era un niño cuando subi… |
| `chapters[1].img[10]` | `['Víctor Calvo', 'Milagros Barroso']` | 1962 | Recuerda los mareos. Y la incertidumbre: no saber muy bien adónde iban ni cómo iban a vivi… |
| `chapters[1].img[13]` | `['Víctor Calvo']` | 1962 | Hay polvo por todas partes. Ese niño cuenta que nunca había visto tanto polvo. |
| `chapters[2].img[3]` | `['Eric Saint']` | 1948 | Mil novecientos cuarenta y ocho. Un médico llega en avión y escribe una carta a máquina: l… |
| `chapters[2].img[5]` | `['Eric Saint']` | 1948 | Se llama Eric Saint. Lo que pasó con la carta lo contó él mismo: «Me desestimaron y, de he… |
| `chapters[3].img[1]` | `['Víctor Calvo']` | 1963 | Víctor Calvo lo cuenta: «Nosotros jugábamos con él y lo íbamos deshilachando. Nos lo metía… |
| `chapters[3].img[8]` | `['Ramón de Juan']` | 1962 | Daniel trabajaba en la mina. Ramón de Juan, el amigo, hacía jornadas de dieciséis horas. |
| `chapters[3].img[10]` | `['Milagros Barroso', 'John Patrick']` | 1963 | En marzo de mil novecientos sesenta y tres, Milagros Barroso dio a luz en Wittenoom a John… |
| `chapters[3].img[11]` | `['María Bernal']` | 1963 | Tres meses después le tocó a María. Llegó al hospital de Wittenoom debilitada por una infe… |
| `chapters[3].img[12]` | `['María Bernal', 'Daniel Écija']` | 1963 | El bebé era muy grande. Lo sacaron con fórceps. Le pusieron Daniel, como el padre. Hay una… |
| `chapters[3].img[13]` | `['María Bernal', 'Daniel Écija']` | 1963 | Después de esa foto, las maletas. Diez meses en Wittenoom. Se fueron antes de que nadie le… |
| `chapters[4].img[0]` | `['James Vernon']` | 1966 | Diciembre de mil novecientos sesenta y seis. James Vernon anuncia que CSR cierra Wittenoom… |
| `chapters[4].img[7]` | `['Daniel Écija hijo']` | 1985 | Mil novecientos ochenta y cinco. Un aeropuerto australiano, un puesto de control. El agent… |
| `chapters[5].img[4]` | `['Melita Markey']` | 2024 | La cuenta oficial se detuvo. «El gobierno dejó de contar en 2.000, pero ahora se calcula q… |
| `chapters[6].supp[6]` | `['Maitland Parker', 'Marcos Orellana']` | 2023 | Es tierra Banjima. En dos mil veintitrés, Marcos Orellana visitó Australia y se sentó con … |
| `chapters[6].supp[7]` | `['Maitland Parker']` | 2023 | «Todavía lloro por mi territorio, pero eso está arraigado en mí; simplemente no puedo alej… |

## A.3 Grep de nombres del canon en `prompt` (todas las fotos: caps flux, supps, foto del clip; miniaturas no se rearman en m03)

Nombre completo y nombre de pila de las 22 personas de `documented_people`, sin mayúsculas ni acentos, con borde de palabra. **Coincidencias: 2 → PARÁ según la regla**, las dos con «Court» (persona del canon «Court», jefe del gobierno del Estado) usado como sustantivo común:

- `chapters[5].img[1]` · token «Court» (persona del canon: Court) · prompt completo:

      A late-1980s Australian courtroom with a robed judge at the elevated bench and former asbestos workers in plain civilian clothes seen from behind. The judge reads the verdict aloud from typed pages. Wood-panelled Western Australian Supreme Court room, 1988, lawyers in dark suits at the bar table. Soft diffused light from tall windows. Wide shot, eye-level from the public gallery, deep depth of field, 28mm. A grainy 35mm documentary photograph taken in 1988, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.

- `chapters[6].supp[9]` · token «Court» (persona del canon: Court) · prompt completo:

      Lawyers in dark contemporary suits seen from behind, beside Banjima representatives with dark brown skin and greying hair in smart contemporary attire. Filing the claim before the bench, papers set down on the bar table. Aboriginal Australian people with dark brown skin, dark wavy to curly hair (greying in elders) and brown eyes. A modern Australian Federal Court courtroom, pale timber panelling, raised bench, 2026. Cool even daylight through high windows. Wide shot, high angle from the rear gallery, deep depth of field, wide lens. A grainy 35mm documentary photograph taken in 2026, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.


Ningún otro nombre (ni «Daniel», «María», «Ramón», «Milagros», «Víctor», «Mercedes», «Hancock», «Wright», «Major»…) aparece en la prosa de las 96 fotos. CC lo lee como colisión de un apellido que es palabra inglesa, no como fuga del nombre a la foto; lo decide el analista (p. ej. excluir del grep los nombres del canon que son sustantivos comunes, o quitar «Court»/«Major» de `documented_people`).

## A.4 Hallazgo: `_steps` de producción tiene un guion nuevo; corrida 1 (US$ 2,5815) con esas entradas

- `data/scripts/_steps/<tid>/01b_narration.json`, `01b_narracion_v3.json`, `01b_guionista_v4.json`, `01a_skeleton.json` son del **29-oct 20:55** (F54 B.5), `01a_escaleta.json` 20:26, `00_pool_v3.json` 20:38. El `03_visual.json` de producción (y de la copia) es del 29-oct 13:00, hecho con la narración ANTERIOR (normalizada el 28-oct: «Dieciséis de septiembre de mil novecientos sesenta y uno…»), que es también la del audio (`output/audio/<tid>/`, 28-oct) y la del guion vivo. De las 96 anclas del 03_visual, 96/96 están en `lab/hyperframes/f54/antes/01b_narration.json` y **3/96** en el `01b_narration.json` actual.
- Corrida 1 (`a/corrida1_narracion_29oct.json`, `.log`, `a/03_visual_corrida1_narracion_29oct.json`): m03 con las entradas actuales → 96 fotos, 23 con `persona`, Daniel en 4; ninguna ancla coincide con la tabla de verdad → se guardó como registro y se repitió con las entradas del guion anterior. Mismo patrón de ruteo (María sin Daniel en el baile; Daniel solo donde la voz lo nombra). Grep: 1 coincidencia, también «Court» (`chapters[6].supp[5]`, «court steps», con cartel «FEDERAL COURT» pedido por `text_in_image`).
- Consecuencia fuera de F60: si se corre `--from m03` en producción hoy, los prompts salen de la narración nueva y no cuadran con el audio ni con el guion vivo. No se tocó nada de producción; queda para el analista/Omar (nota en la carpeta compartida de sesiones).

Corrida 1, fotos con `persona` (para comparar el patrón):

| foto | `persona` | año | ancla |
|---|---|---|---|
| `chapters[0].supp[1]` | `['Daniel Écija']` | 1963 | El hombre se llama Daniel Écija, es minero, y llegó de Madrid hace unos meses. Wittenoom, … |
| `chapters[0].image_prompt` | `['Daniel Écija']` | 1963 | Un hombre joven posa para un retrato con el pie vendado. |
| `chapters[1].img[1]` | `['María Bernal']` | 1961 | Allí María Bernal conoció a Daniel. De esa noche y de lo que vino después, |
| `chapters[1].img[2]` | `['María Bernal']` | 1961 | ella no cuenta la música ni el vestido; cuenta que iba muy cerca de él y que confiaba en l… |
| `chapters[1].img[9]` | `['Milagros Barroso']` | 1962 | Allá los esperaban ya Ramón de Juan y Milagros Barroso, otro matrimonio que había llegado … |
| `chapters[1].img[11]` | `['Víctor Calvo']` | 1962 | Víctor Calvo hizo esa travesía de niño. Salieron de Málaga y tardaron más de veinte días e… |
| `chapters[1].img[13]` | `['Víctor Calvo', 'Milagros Barroso']` | 1962 | Recuerdo los mareos. La incertidumbre», dice Calvo. |
| `chapters[1].img[15]` | `['Víctor Calvo', 'Milagros Barroso']` | 1962 | Del avión, a la tierra más roja que Víctor había visto en su vida. |
| `chapters[2].img[1]` | `['Víctor Calvo', 'Milagros Barroso']` | 1962 | «Aterrizamos en una pista en medio de una tierra muy muy roja. Había polvo por todas parte… |
| `chapters[2].img[10]` | `['Eric Saint']` | 1948 | Pedía, naturalmente, examinar algunos de esos tórax. Eric Saint, médico, fue quien advirti… |
| `chapters[3].img[2]` | `['Ramón de Juan']` | 1962 | Ramón de Juan, el amigo, hacía con frecuencia jornadas de dieciséis horas. |
| `chapters[3].img[5]` | `['Víctor Calvo']` | 1963 | Nosotros jugábamos con él y lo íbamos deshilachando. Nos lo metíamos en la boca. Cuando lo… |
| `chapters[3].img[7]` | `['María Bernal']` | 1963 | En ese pueblo, en junio de 1963, María entró al hospital a dar a luz. |
| `chapters[3].img[10]` | `['Milagros Barroso', 'John Patrick']` | 1963 | Tres meses antes, en marzo, Milagros Barroso había dado a luz en el mismo pueblo a John Pa… |
| `chapters[3].img[11]` | `['María Bernal']` | 1963 | El 7 de julio de 1963 bautizaron al niño; la familia conserva una fotografía de ese día. |
| `chapters[4].img[2]` | `['Mercedes']` | 1971 | Los de Juan estuvieron en Wittenoom unos dos años y medio y regresaron a Madrid en 1971; M… |
| `chapters[4].img[11]` | `['Daniel Écija']` | 1962 | Eso había en el polvo. Eso respiraba mientras esperaba que le cerrara el pie. |
| `chapters[5].img[1]` | `['Daniel Écija hijo']` | 1985 | En un control de aeropuerto, el policía lee la página, baja la cabeza, vuelve a mirar. «As… |
| `chapters[5].img[4]` | `['Melita Markey']` | 2023 | Melita Markey sigue contando lo que el gobierno dejó de contar en dos mil; otras estimacio… |
| `chapters[6].supp[0]` | `['Maitland Parker']` | 2023 | Maitland Parker era Banjima, y esa tierra era la suya. |
| `chapters[6].supp[1]` | `['Maitland Parker', 'Marcos Orellana']` | 2023 | En 2023, Marcos Orellana visitó Australia y lo entrevistó sobre la contaminación y el daño… |
| `chapters[6].supp[2]` | `['Maitland Parker']` | 2023 | «Todavía lloro por mi territorio, pero eso está arraigado en mí; simplemente no puedo alej… |
| `chapters[6].supp[11]` | `['Daniel Écija']` | 1963 | Daniel Écija vivió diez meses en Wittenoom. Nadie en su familia sabe decir qué respiró all… |

## A.5 Diff de 5 ítems contra el 03_visual anterior (corrida 2)

Los 5 traen la clave nueva `persona`; la prosa cambia en los 5 (Opus no es determinista y el bloque del canon cambió: nombres como dato de ruteo), sin nombres propios (§A.3). Donde el índice cambió de ancla, el diff compara escenas distintas (se dice).

### `chapters[1].img[0]` · ancla igual: sí · `persona` después: `[]` · claves nuevas ['persona'], claves idas []

ANTES: A young Spanish couple in their mid-twenties, olive skin, dark hair; he lean in a dark narrow-lapel suit, she slim in a knee-length 1961 cotton-satin dress with neatly set hair. The pair meet at the edge of the dance floor amid swirling couples, his head inclined toward her as the music starts. Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes. Ballroom of the Círculo de Bellas Artes, Madrid, 1961: ornate high ceiling, crystal chandeliers, gilded mouldings, polished parquet crowded with dancing couples. Warm tungsten chandelier light, soft glow on faces. Wide shot, eye-level from the edge of the dance floor, 35mm lens, moderate depth of field, dancers softly blurred in motion. A grainy 35mm documentary photograph taken in 1961, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.

DESPUÉS: A young Spanish couple in their twenties, olive skin and dark hair, he slim in a dark suit and narrow tie, she slender in a tea-length cotton party dress, among other dancing Madrid couples. The couple meet at the edge of the dance floor, his hand extended toward her as the band plays. Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes. Ornate early-1960s ballroom of a Madrid fine-arts society, high coffered ceiling, tall arched windows, polished parquet floor. Warm tungsten chandelier light, soft evening glow. Wide shot, eye-level from the ballroom edge, deep depth of field, 35mm lens. A grainy 35mm documentary photograph taken in 1961, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.

diff por oración:

      @@ -1,2 +1,2 @@
      -A young Spanish couple in their mid-twenties, olive skin, dark hair; he lean in a dark narrow-lapel suit, she slim in a knee-length 1961 cotton-satin dress with neatly set hair
      -The pair meet at the edge of the dance floor amid swirling couples, his head inclined toward her as the music starts
      +A young Spanish couple in their twenties, olive skin and dark hair, he slim in a dark suit and narrow tie, she slender in a tea-length cotton party dress, among other dancing Madrid couples
      +The couple meet at the edge of the dance floor, his hand extended toward her as the band plays
      @@ -4,3 +4,3 @@
      -Ballroom of the Círculo de Bellas Artes, Madrid, 1961: ornate high ceiling, crystal chandeliers, gilded mouldings, polished parquet crowded with dancing couples
      -Warm tungsten chandelier light, soft glow on faces
      -Wide shot, eye-level from the edge of the dance floor, 35mm lens, moderate depth of field, dancers softly blurred in motion
      +Ornate early-1960s ballroom of a Madrid fine-arts society, high coffered ceiling, tall arched windows, polished parquet floor
      +Warm tungsten chandelier light, soft evening glow
      +Wide shot, eye-level from the ballroom edge, deep depth of field, 35mm lens

### `chapters[1].img[3]` · ancla igual: sí · `persona` después: `['María Bernal']` · claves nuevas ['persona'], claves idas []

ANTES: A young Spanish wife, mid-twenties, slight build, olive skin, dark set hair, in a modest cotton dress, pressed against her lean dark-haired husband in shirtsleeves. She walks the deck glued to his side, her shoulder tucked under his arm. Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes. Promenade deck of a migrant liner, 1962, other passengers soft in the background. Soft afternoon sea light. Medium shot, eye-level, three-quarter front, 85mm lens, shallow depth of field. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.

DESPUÉS: A young Spanish couple in their twenties, olive skin, dark hair, slim builds, he in a work shirt and trousers, she in a modest knee-length cotton dress. The couple stand side by side at the stern rail as the liner moves into open sea. Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes. Stern deck of a 1960s migrant ocean liner on open water. Soft neutral daylight at sea. Wide shot, eye-level from behind, deep depth of field, 35mm lens. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.

diff por oración:

      @@ -1,2 +1,2 @@
      -A young Spanish wife, mid-twenties, slight build, olive skin, dark set hair, in a modest cotton dress, pressed against her lean dark-haired husband in shirtsleeves
      -She walks the deck glued to his side, her shoulder tucked under his arm
      +A young Spanish couple in their twenties, olive skin, dark hair, slim builds, he in a work shirt and trousers, she in a modest knee-length cotton dress
      +The couple stand side by side at the stern rail as the liner moves into open sea
      @@ -4,3 +4,3 @@
      -Promenade deck of a migrant liner, 1962, other passengers soft in the background
      -Soft afternoon sea light
      -Medium shot, eye-level, three-quarter front, 85mm lens, shallow depth of field
      +Stern deck of a 1960s migrant ocean liner on open water
      +Soft neutral daylight at sea
      +Wide shot, eye-level from behind, deep depth of field, 35mm lens

### `chapters[3].img[8]` · ancla igual: NO · `persona` después: `['Ramón de Juan']` · claves nuevas ['persona'], claves idas []

ANTES: Dust-covered miners of European origin, mostly seen from behind, and one young Spanish miner, mid-20s, standing apart. Gathered outside the mine adit after the blast, a thick dust cloud still hanging over the entrance. Adult men of European origin (Anglo-Australian, Central and Eastern European, Southern European including Spanish), with fair to olive skin, dark to light hair and lean working builds. Wittenoom Gorge mine entrance, 1962, red rock walls, timber portal, tailings below. Harsh daylight dimmed by suspended dust. Wide shot, eye-level from the gorge floor, deep depth of field, 35mm. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.

DESPUÉS: Spanish and European miners, young adult, lean builds, olive to fair skin, in dust-coated singlets and drill trousers, mostly rim-lit silhouettes. Filing out of the mine at the gorge mouth at the end of a double shift. Adult men of European origin (Anglo-Australian, Central and Eastern European, Southern European including Spanish), with fair to olive skin, dark to light hair and lean working builds. Wittenoom Gorge mine entrance, 1962, red rock walls and tailings dumps, timber props. Low-key night, a single work lamp behind the men. Wide shot, low angle against the gorge wall, deep depth of field, 28mm lens. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.

diff por oración:

      @@ -1,2 +1,2 @@
      -Dust-covered miners of European origin, mostly seen from behind, and one young Spanish miner, mid-20s, standing apart
      -Gathered outside the mine adit after the blast, a thick dust cloud still hanging over the entrance
      +Spanish and European miners, young adult, lean builds, olive to fair skin, in dust-coated singlets and drill trousers, mostly rim-lit silhouettes
      +Filing out of the mine at the gorge mouth at the end of a double shift
      @@ -4,3 +4,3 @@
      -Wittenoom Gorge mine entrance, 1962, red rock walls, timber portal, tailings below
      -Harsh daylight dimmed by suspended dust
      -Wide shot, eye-level from the gorge floor, deep depth of field, 35mm
      +Wittenoom Gorge mine entrance, 1962, red rock walls and tailings dumps, timber props
      +Low-key night, a single work lamp behind the men
      +Wide shot, low angle against the gorge wall, deep depth of field, 28mm lens

### `chapters[4].img[12]` · ancla igual: NO · `persona` después: `[]` · claves nuevas ['persona'], claves idas []

ANTES: A lean Spanish man about fifty-five, olive skin, greying dark hair, slightly hollowed cheeks, early-1990s plain jacket and trousers. Sits alone waiting to see the doctor, shoulders rounded, chest sunk forward. Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes. Large tiled Madrid hospital waiting hall with rows of empty seats, 1991. Cold fluorescent overhead light, hard and flat. Wide shot, high angle from the far end of the hall, deep depth of field, 28mm lens. A grainy 35mm documentary photograph taken in 1991, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.

DESPUÉS: Spanish man in his mid-fifties, olive skin, greying dark hair, lean worn build, in a plain shirt and cardigan, seen from behind; a Spanish doctor in a white coat beyond. Sitting before the doctor as the chest X-ray is clipped to the lightbox and the diagnosis is spoken. Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes. Madrid hospital consulting room, 1991, metal desk, examination couch, tiled walls. Hard cold light from the lightbox, the rest of the room in shadow. Wide shot, eye-level from behind the patient, deep depth of field, 35mm. A grainy 35mm documentary photograph taken in 1991, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.

diff por oración:

      @@ -1,2 +1,2 @@
      -A lean Spanish man about fifty-five, olive skin, greying dark hair, slightly hollowed cheeks, early-1990s plain jacket and trousers
      -Sits alone waiting to see the doctor, shoulders rounded, chest sunk forward
      +Spanish man in his mid-fifties, olive skin, greying dark hair, lean worn build, in a plain shirt and cardigan, seen from behind; a Spanish doctor in a white coat beyond
      +Sitting before the doctor as the chest X-ray is clipped to the lightbox and the diagnosis is spoken
      @@ -4,3 +4,3 @@
      -Large tiled Madrid hospital waiting hall with rows of empty seats, 1991
      -Cold fluorescent overhead light, hard and flat
      -Wide shot, high angle from the far end of the hall, deep depth of field, 28mm lens
      +Madrid hospital consulting room, 1991, metal desk, examination couch, tiled walls
      +Hard cold light from the lightbox, the rest of the room in shadow
      +Wide shot, eye-level from behind the patient, deep depth of field, 35mm

### `chapters[0].supp[0]` · ancla igual: sí · `persona` después: `['Daniel Écija']` · claves nuevas ['persona'], claves idas ['_f8_slots_scrub']

ANTES: The bandaged foot of a young adult Spanish miner beside the sandalled feet of his wife and a child. The bandaged foot rests lightly on the ground, the dressing seeping a faint dull stain that will not dry. Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes. Compacted red earth mixed with crumbly blue-grey tailings in a Wittenoom house yard, 1962. Hard cold midday light under a pale washed-out sky, short sharp shadows. Detail shot, low angle near ground level, macro-leaning 85mm lens, shallow depth of field, family feet soft behind. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.

DESPUÉS: A Spanish migrant family posed together for a portrait. At the centre is a young olive-skinned miner, mid-twenties, lean, in a short-sleeved work shirt and drill trousers, one foot bandaged white. Beside him stands a slight young dark-haired Spanish woman in a modest knee-length cotton dress with neatly set early-1960s hair. A few relatives in plain cotton clothes stand beside the couple. The family stands stiffly in a line facing the camera for the portrait. The miner plants his weight on his good leg while his bandaged foot rests forward on the red ground. Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes. In front of a single-storey company house of corrugated iron and pale fibro-cement sheeting. The yard is surfaced with red earth and loose blue-grey tailings, 1962. Hard cold midday desert light, bleached and flat, sharp short shadows. Wide shot, eye-level, frontal like a period box camera, deep depth of field, 35mm lens, centred formal framing. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.

diff por oración:

      @@ -1,2 +1,6 @@
      -The bandaged foot of a young adult Spanish miner beside the sandalled feet of his wife and a child
      -The bandaged foot rests lightly on the ground, the dressing seeping a faint dull stain that will not dry
      +A Spanish migrant family posed together for a portrait
      +At the centre is a young olive-skinned miner, mid-twenties, lean, in a short-sleeved work shirt and drill trousers, one foot bandaged white
      +Beside him stands a slight young dark-haired Spanish woman in a modest knee-length cotton dress with neatly set early-1960s hair
      +A few relatives in plain cotton clothes stand beside the couple
      +The family stands stiffly in a line facing the camera for the portrait
      +The miner plants his weight on his good leg while his bandaged foot rests forward on the red ground
      @@ -4,3 +8,4 @@
      -Compacted red earth mixed with crumbly blue-grey tailings in a Wittenoom house yard, 1962
      -Hard cold midday light under a pale washed-out sky, short sharp shadows
      -Detail shot, low angle near ground level, macro-leaning 85mm lens, shallow depth of field, family feet soft behind
      +In front of a single-storey company house of corrugated iron and pale fibro-cement sheeting
      +The yard is surfaced with red earth and loose blue-grey tailings, 1962
      +Hard cold midday desert light, bleached and flat, sharp short shadows
      +Wide shot, eye-level, frontal like a period box camera, deep depth of field, 35mm lens, centred formal framing


## A.6 Gasto

| corrida | qué | US$ |
|---|---|---|
| 1 | m03 7 caps con las entradas actuales de `_steps` (narración del 29-oct 20:55) | 2,5815 |
| 2 | m03 7 caps con las entradas del guion anterior (f54/antes + pool f44/B) | 2,2494 |
| **total Etapa A** | | **4,83** |

## Lo que queda abierto (Etapa A)

1. **PARÁ (regla del grep):** 2 coincidencias, las dos «Court» como sustantivo. Decidir si el apellido «Court» (y «Major», «Wright») cuentan como nombre en el grep.
2. **Daniel sub-ruteado:** 4 fotos con Daniel en la corrida 2 (4 en la 1) contra ≈ 9 esperadas; «él», «mi marido», «se casan», «los Écija» no disparan el casillero. Antes de la Etapa B hay que decidir si el texto del casillero cambia (p. ej. «the couple / the family of a documented person counts as that person») o si la foto madre de Daniel se usa con menos fotos. Con 2 fotos ya alcanza para la madre (regla ≥ 2), pero las escenas de 1961-1962 quedarían sin ancla de cara.
3. **Orden:** en `chapters[3].img[13]` `persona` = `['María Bernal', 'Daniel Écija']` (la tabla esperaba a Daniel principal). Sin consecuencia hasta que el pre-paso de secuencia use `persona[0]`.
4. **m03 vuelve a elegir anclas** (Gemini, paso 1): 8/16 referencias cambiaron de índice entre corridas; la tabla de verdad por índice no es estable; en la Etapa B la prueba tiene que comparar por ancla o fijar anclas.
5. **Guion nuevo en `_steps`** (§A.4): producción desalineada entre narración, audio y 03_visual; decisión del analista/Omar.
6. **Ramón vs Daniel** en «Daniel trabajaba en la mina. Ramón de Juan, el amigo…»: Opus eligió al que tiene oración propia; con dos nombres en una ancla, el «main one first» no se cumple.
7. **`test_module_gfx_lab.py::test_candado_en_el_preview`** flaky (pasa sola, falla en 5 corridas de la suite): no es de esta tanda, pero ensucia el conteo.
8. 5 tests byte-idénticos (f59_a1, f58_a3) ahora toman el bloque del canon del módulo nuevo: si el canon vuelve a cambiar no lo van a ver; la identidad del resto del prompt sigue cubierta.
