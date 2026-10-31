# F66b_REPORT — narración restaurada y papel re-escrito; el verificador solo avisa

Pedido de Omar 2026-10-31 17:25 · rama `f11-guion-v4` · base `00a4e23` · CC Opus 5.5 medium · commits `c98617d` (Etapa 1), `ac5ceb8` (Etapa 2) + cierre. **Una sola llamada real, la corrida del papel: US$ 0,98.** El papel NO está aprobado; voz y fotos NO corrieron.

## Etapa 1 (0 llamadas)

- **Código:** `run_verificacion(topic_id, pool, *, log, post=None)` solo verifica, escribe `01b_verificacion.json/.md` y deja cada «contradice» en `quedan` (aviso en el `.md` del papel y en la PARADA). No edita ni re-particiona. Sin flag: borrados el camino «v», `_parrafo_de`, `guard`/`cifras_ok` de `edit_sentences` y `title_list` de `particionar`. `script_engine/guion_v4.py` y `m01d_particion.py` quedan **idénticos a `a9aa200`**. `run_guion_v4` conserva su partición; `verificar_narracion` ya no arma `call`. Los prompts no cambian: `PANTALLA_SYSTEM` 85d094be…, `SYSTEM_B` ce31cc51…, `prompt_md5()` f2bfdf20…, m01e-7 (test).
- **Restauración** (`etapa1_restaurar.py`): los 6 archivos del pedido, de `f66/antes/` a `_steps`; lo de F66 en `f66/despues_descartado/`. Narración `c7badfbe260f5eb24a47e780b40406b5` ✓. USER del autor `018f9cc1b939e2afdcfad5eb5ebcc36f` ✓. No se restauró el raw viejo: habría sido un hit de caché con el papel de las fichas forzadas. `01_v3_costos.json` tampoco: registra lo gastado.
- **`01b_verificacion`:** rehecho desde la 1.ª pasada de F66, sin llamar al modelo: 7 «contradice» como aviso, sin «corregida ✔» ni columnas de ediciones; siguen los 24 «sin respaldo».
- **Decisión de CC sobre ch03 [15]** (Q53): `quedan` lleva los 7 del pedido. Esa octava marca salió solo en la re-verificación descartada, así que no entra al aviso. Se conserva en el JSON (`re_verificacion_descartada`) y en una sección aparte del `.md`. La oración sigue en la narración restaurada: ver abierto 3.
- **Tests:** `test_module_f66` reescrita en su Etapa B (16 en total), con post falso y el POST real explotando: contradice → aviso sin editar ni re-particionar (narración y skeleton byte a byte), firmas restauradas, sin guionista, orden de `run_guion_v4`. Tests del camino «v» borrados. Suites vecinas: 204 verdes + 7 saltados (sin Vajont, previos). Stickers ×4, MAPA 0.

## Etapa 2

Respaldo del papel de F66 en `despues_descartado/`; `python -m script_engine.m01e_pantalla 123bbb64-…` (`etapa2_run.log`). El intento 1 dejó 1 ficha fuera, por el código (no por el verificador). La vuelta la cambió:

- D115 (ch03 beat 6) «ESE MISMO 1962 · Récord de asbesto en Australia: 95% venía de Wittenoom»: candado: no están en el texto fuente de D115: ['Australia']

`PAPEL_RESTAURADO.md`, entero:

#### F66b Etapa 2 — el papel sobre la narración restaurada

`m01e-7` · claude-opus-5-5 medium · narración `c7badfbe260f5eb24a47e780b40406b5` · entrada `018f9cc1b939e2afdcfad5eb5ebcc36f` · 13 de 13 fichas · 8 sellos · 3 relojes · cierre **sin motivos** tras 1 vuelta(s) · **sin aprobar**: el papel no está aprobado

| beat | cap | función | ficha | texto | oración ancla |
|---|---|---|---|---|---|
| 1 | ch01 | gancho ⚡ | D26 | LO QUE QUEDÓ · El mayor sitio contaminado del hemisferio sur | [9] Lo que sobró de la mina, en cambio, sigue donde lo dejaron. |
| 2 | ch02 | planteo | Q25 | POR QUÉ SE FUERON · En España no teníamos nada, ninguno de los dos. — María Bernal | [2] De esa noche y de lo que vino después, ella no cuenta la música ni el vestido; cuenta que iba muy cerca de él y que confiaba en lo que venía. |
| 3 | ch02 | planteo ⚡ | D83 | ASÍ SE LLAMÓ EL ACUERDO · Operación Canguro, con el franquismo, desde 1958 | [7] No iban solos: cerca de ocho mil españoles cruzaron por un acuerdo entre los dos gobiernos, y CSR, la compañía dueña de la mina, venía haciendo viajes privados a Europa para reclutar gente desde 1950. |
| 4 | ch03 | planteo | D02 | LO QUE PISABAN · Relaves con alrededor de un 5% de asbesto | [9] El pueblo entero, la pista, los patios, la escuela: todo estaba hecho con lo que sobraba de la mina. |
| 5 | ch03 | escalada ⚡ | D44 | YA SE SABÍA · En 1930 un informe ligó asbesto y asbestosis | [11] Los informes eran anteriores a la boda, al barco y al avión. |
| 6 | ch03 | giro | D115 | ESE MISMO 1962 · Récord de asbesto del país: el 95% salió de Wittenoom | [31] El año en que McNulty escribió ese primer caso, un recién casado de Madrid se bajaba de un avión en esa misma pista de polvo. |
| 7 | ch04 | escalada ⚡ | Q19 | SIN ALERTA · Nadie nos avisó de nada. — Víctor Calvo | [9] Estaban rodeados de amianto azul y no les daba miedo. |
| 8 | ch04 | giro | D102 | ESE BEBÉ, HOY · Productor de televisión en España | [13] Nació un varón y le pusieron Daniel, como el padre. |
| 9 | ch05 | escalada | D94 | LO QUE PAGÓ CSR EN 1989 · 18,3 millones de dólares australianos a 200 afectados | [8] Y en 1988 un juez determinó que la compañía había mostrado un desprecio continuo, consciente y contumaz por la seguridad y la salud de sus trabajadores. |
| 10 | ch05 | pico ⚡ | D23 | NO ERA EL PRIMERO · En 1989 ya eran más de 500 los muertos de Wittenoom | [12] En 1991, en Madrid, un diagnóstico puso nombre a lo que Daniel llevaba adentro: mesotelioma. |
| 11 | ch06 | respiro | Q22 | MUERTOS QUE NO VIVÍAN ALLÍ · solo fueron en una excursión del colegio — John de Juan | [8] Markey dice que hay hijos de funcionarios que trabajaban en el pueblo, como policías o maestros, que están ahora enfermando. |
| 12 | ch06 | revelacion ⚡ | T80 | QUIÉN LO ANUNCIÓ · Jon Ford, ministro de Desarrollo Regional | [10] Hacia junio de 2007, según otras referencias en 2006, Wittenoom fue abolido oficialmente. |
| 13 | ch07 | cierre ⚡ | D69 | LO QUE SÍ COBRÓ EL ESTADO · Más de 70.000 millones de dólares en regalías del Pilbara | [7] Los abogados sostienen que el Estado no ha gastado dinero en remediar el sitio y que no se ha retirado una sola palada de asbesto de la tierra Banjima. |

##### Descartes del verificador

- En el papel final: ninguno.

Por llamada (incluye lo que se cortó en el intento 1 y la vuelta reemplazó):

| llamada | marcas | pasa | corta | dicho | no_dicho | US$ |
|---|---|---|---|---|---|---|
| 1 | 8 | 2 | 0 | 6 | 0 | 0.0605 |
| 2 | 8 | 2 | 0 | 6 | 0 | 0.0611 |

`a_pantalla` como aviso (⚠, no obligan): D01 (b5), D51 (b9), D34 (b11), D40 (b12), D61 (b13)

##### Costo por llamada

| llamada | in | escritos al caché | leídos | out | US$ | s |
|---|---|---|---|---|---|---|
| autor intento 1 | 4 | 88643 | 0 | 17045 | 0.7841 | 146.6 |
| autor vuelta 1 | 7115 | 0 | 88643 | 499 | 0.0739 | 8.3 |
| verificador 1 | 9536 | — | — | 1118 | 0.0605 | 9.6 |
| verificador 2 | 9536 | — | — | 1150 | 0.0611 | 10.1 |
| **total** | | | | | **0.9797** (autor 0.8580 + verificador 0.1216) | |

##### Confirmación del QA Studio y del aviso

- QA Studio → 📄 PAPEL en Chrome headless, con el papel de producción y sin tocar botones: 13 beats · estado «Sin aprobar» · 0 errores de página · captura `papel_restaurado_qa.png`.
- Cabecera de la vista: 7 «contradice» en el aviso.
- Final del `01e_pantalla.md`: sección de aviso presente y última, 7 «contradice».
- PARADA: lleva el aviso: «⚠ la narración sigue contradiciendo el archivo en 7 punto(s): ch01 «Ese pie va a cerrar; lo que respira mientr…»
- md5 del papel antes y después de mirar: `cc6ceca97aaebcbe2b8fbe8321dc4a02` / `cc6ceca97aaebcbe2b8fbe8321dc4a02` (iguales).

En la cabecera:

- ch01 [1] «Ese pie va a cerrar; lo que respira mientras espera que cierre va a tardar casi treinta años en matarlo, y lo va a alcanzar a miles de kilómetros de aquí.»: La herida del pie va a cerrar. (D85)
- ch01 [9] «Lo que sobró de la mina, en cambio, sigue donde lo dejaron.»: Los residuos de la mina siguen donde los dejaron. (D04, D149)
- ch03 [14] «En 1946 ya había diagnósticos de asbestosis, y un inspector describió las condiciones de trabajo como terroríficas.»: En 1946 ya había diagnósticos (en plural) de asbestosis (T13, D91)
- ch03 [31] «El año en que McNulty escribió ese primer caso, un recién casado de Madrid se bajaba de un avión en esa misma pista de polvo.»: McNulty escribió el primer caso de mesotelioma en 1962 (D50, T32, D130)
- ch04 [1] «El hijo cuenta que el primer día de trabajo de su padre hubo una explosión y que alguien murió; no hay otro documento que lo confirme.»: Según el hijo, en esa explosión murió alguien (Q16)
- ch06 [12] «El gobierno de Australia Occidental lo llamó «el fin de un período oscuro en la historia de nuestro Estado».»: El gobierno de Australia Occidental llamó a la abolición del pueblo «el fin de un período oscuro en la historia de nuestro Estado». (Q07, T91)
- ch07 [9] «Quién sabía está escrito: dos inspectores en 1944, un médico al que llamaron alborotador en 1948, un tribunal que entró al molino en 1957.»: Dos inspectores advirtieron sobre el polvo en 1944 (D19)


Medido por primera vez con caché en el autor (F65b lo había derivado): el intento 1 cuesta 0,7841 (F66, sin caché: 0,7064) y la vuelta 0,0739 (F66: 0,4013). La captura `papel_restaurado_qa.png` muestra la vista con el aviso.

## Lo que queda abierto

1. **Decisión de Omar al revisar:** este papel se aprueba sobre una narración con 7 contradicciones conocidas, entre ellas la promesa del gancho («Ese pie va a cerrar», D85: no cerraba nunca). El aviso las muestra y la cadena no las corrige. Corregirlas a mano o aprobar con ellas es decisión suya. Tocar la narración cambia el USER: hay que re-escribir el papel (≈ US$ 1) y «sugerir» se niega hasta entonces (candado de entrada).
2. **Fichas ancladas en oraciones marcadas:** beat 1 (D26) ancla en ch01 [9] y beat 6 (D115) en ch03 [31], dos de las 7. Si se corrigen, esas anclas pueden moverse.
3. **ch03 [15] (Q53) queda fuera del aviso** aunque la oración sigue en la narración: la 1.ª pasada no la marcó y la re-verificación sí (varianza de 1 corrida por cap). Omar la ve solo en `01b_verificacion.md`. Si la quiere en el aviso, es agregarla a `quedan` y re-escribir el `.md` del papel.
4. **El rediseño está pendiente, antes del tema 2** (DECISIONES 17:25): corregir con el dato, nunca sacar, proteger promesa y re-gancho. Hasta entonces cada video paga el verificador (≈ US$ 2,44, medido en esta narración) y solo recibe un aviso. El análisis de por qué borraba sigue en `F66_REPORT.md`.
5. **`leer_quedan` no compara contra el md5 de la narración:** si la narración cambia y se corre `m01e_pantalla` sin pasar por la verificación, el aviso sale viejo. `01b_verificacion.json` trae `narracion_md5`: alcanza con compararlo. No se tocó: no estaba pedido.
6. **`--verificar-narracion` re-pagaría ≈ US$ 2,44 y pisaría `01b_verificacion`** (se pierde la sección de ch03 [15]; queda en `despues_descartado/`). Ya no toca la narración.
7. **`F66_REPORT.md` y `F65b_REPORT.md` quedan como historia:** describen la narración descartada. `01e_sugerir.log.jsonl` trae las 2 corridas de F65b sobre el papel de F66; las capturas de `f65/ui/` también son de ese papel.
8. **PARADA:** el papel no está aprobado; voz y fotos sin correr. Cuando se apruebe, la voz va con `--from normalizer_gate`, nunca `--from audio`: el `01b_narration_normalized.json` restaurado sigue siendo del 28-oct.

## Veredicto de revisor-handoff (íntegro)

**VEREDICTO: CUMPLE CON OBSERVACIONES**

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | guion_v4.py y m01d_particion.py idénticos a a9aa200 | OK | `git diff a9aa200 HEAD --ignore-space-at-eol -- ...` vacío |
| 2 | run_verificacion solo verifica: sin edición, sin partición, sin flag | OK | fase1_5.py:481-504 escribe 01b_verificacion.json/.md y devuelve `quedan`; no llama al guionista, a edit_sentences ni a particionar |
| 3 | Sin rastro de guard/cifras_ok/title_list/_parrafo_de/edit_sentences en script_engine ni fase1_5 | OK | grep: solo coincidencias ajenas (guardia, guard_render, etc.) |
| 4 | md5 de los 6 archivos en _steps = f66/antes | OK | md5sum igual en los 6; narración c7badfbe260f5eb24a47e780b40406b5 |
| 5 | despues_descartado tiene lo de F66 | OK | 01b_narracion_v3 b079e130… igual a f66/despues; 01e_pantalla.json y 01b_verificacion.json idénticos (cmp) a f66/despues |
| 6 | USER md5 018f9cc1b939e2afdcfad5eb5ebcc36f | OK | mp.entrada_md5(mp.entrada(mp.cargar(...), vocabulario_clima())) = 018f9cc1…; no gastó |
| 7 | 01b_verificacion.md: 7 filas, sin columnas de ediciones | OK | tabla con columnas cap/oración/afirmación/ids/fragmento, 7 filas, sin «corregida ✔» |
| 8 | `quedan` = los 7 de primera.contradice de despues_descartado | OK | comparación por (cap, oración): igual; primera.contradice idéntico al descartado |
| 9 | 01e_pantalla.json: clave de entrada 018f9cc1…, aviso de 7, sin `aprobado` | OK | entrada_md5 018f9cc1…, aviso_narracion len 7, no hay clave `aprobado` |
| 10 | Tabla de PAPEL_RESTAURADO contra el JSON | OK | 13 beats, fichas y anclas consistentes con la vista y con el .md; 13/13, 8 sellos |
| 11 | Costo 0,9797 contra raw y 01_v3_costos.json | OK | raw: 0,78413 + 0,0739 + 0,0605 + 0,06114 = 0,97967; costos.json última «pantalla» 0,9797; el JSON dice autor 0,858 + verificador 0,1216 |
| 12 | Captura papel_restaurado_qa.png (Read) | OK | cabecera «Sin aprobar», US$ 0,9797, m01e-7, bloque ⚠ con los 7 contradice, beat 1 con ficha D26 |
| 13 | Aviso al final del .md y en la cabecera | OK | 01e_pantalla.md termina con «⚠ Aviso de la verificación» y 7 ítems; la PARADA lo lleva (según el reporte, ver obs. 4) |
| 14 | Prompts intactos | OK | prompt_md5 f2bfdf2044a4c77a59fc62ebe93966c2, PROMPT_VERSION m01e-7; m01e_pantalla.py sin diff vs 00a4e23; narracion_verificador.py solo cambió el docstring |
| 15 | Tests | OK | pytest sobre los 4 archivos: f66 16, f10 11, f27 8, f65b 22, todos pasan |
| 16 | Nada de Wittenoom en el código nuevo | OK | los únicos hits en script_engine/fase1_5 son docstrings viejos (m01e_pantalla.py:182, name_matching.py:8) |
| 17 | Línea en DECISIONES.md 17:25 | OK | presente, con el texto pedido |
| 18 | Papel NO aprobado; voz y fotos no corrieron | OK | sin `aprobado`; captura «Sin aprobar» |
| 19 | ESTADO actualizado | NO VERIFICABLE | el pedido dice que se hace después del veredicto; `lab/ESTADO_SESION.md` no tiene cambios |
| 20 | F66b_REPORT.md con «lo que queda abierto» y veredicto | PARCIAL | existe, con 8 abiertos; el veredicto dice «(pendiente)» hasta pegar este |

Fuera de alcance: ninguno en los commits. El árbol sigue sucio con archivos previos a la tanda (diag_234_cap4.py, f28a.log y los `??`), que no son de F66b.

Observaciones:
1. DECISIONES.md sin commitear trae 11 líneas nuevas, no solo la de 17:25: también 13:07, 14:16, 14:20, 15:49 (x3), 16:13 (x2), 17:30 (x2) de F65/F66. Son decisiones previas que nunca se habían commiteado, y el reporte no lo dice. El commit de cierre las va a incluir; Omar tiene que saberlo. La línea 17:30 sobre «aviso si quedan contradice» la atribuye al analista.
2. Decisiones de CC, mi juicio. (a) ch03 [15] fuera de `quedan` pero guardado aparte: razonable, el pedido decía «los 7 de primera». Pero esa oración sigue en la narración y la marcó la re-verificación; el reporte lo declara en el abierto 3. (b) No restaurar raw ni costos: correcto, el raw viejo daría un hit de caché con el papel de las fichas forzadas y los costos son gasto real. (c) Simplificar la firma de run_verificacion: coherente con «no lo dejés apagado», y nadie más usaba los parámetros. (d) Etapa 1 con código y restauración en un solo commit: no hay perjuicio, aunque mezcla dos tipos de cambio.
3. El pedido decía solo «los 7 contradice» y el aviso del papel los cubre. La varianza del verificador es real: una corrida por cap omitió una oración que otra marcó. El verificador no es una red completa. El reporte lo menciona.
4. No pude confirmar por mi cuenta la parte «PARADA lleva el aviso» (hay que correr fase1_5, que me prohibieron). Me baso en el reporte y en el aviso dentro del .md.
5. «Lo que queda abierto» es honesto. Cubre la decisión de Omar sobre aprobar con 7 contradicciones (incluye la promesa D85 «Ese pie va a cerrar»), las anclas en oraciones marcadas, `leer_quedan` sin md5, el costo de re-correr, los reportes viejos que describen la narración descartada y `--from normalizer_gate`. No encontré nada grave que falte.

Riesgos que el contrato no cubre:
- Aprobar el papel con la promesa del gancho aún contradiciendo el archivo: cada video paga ≈ US$ 2,44 de verificador (0,12 en esta corrida por ficha; 2,44 en la narración) y solo recibe un aviso, sin corrección hasta el rediseño.
- `leer_quedan` no compara el md5 de la narración: si la narración cambia sin re-verificar, el aviso sale viejo.
- Si Omar edita la narración a mano, cambia el USER y el papel hay que re-escribirlo (≈ US$ 1).

### Adenda de CC
- **Obs. 1:** cierto. El pedido manda commitear `DECISIONES.md`, así que el commit de cierre lleva las 11 líneas: la de 17:25 y las 10 del 31-oct que estaban sin commitear (9 de Omar o del analista; las 2 de 17:30 son de F66, «voto del analista»). No toqué ninguna.
- **Obs. 4:** verificado en la corrida: `papel_restaurado.py` llama a `fase1_5.parada_del_papel` y hace `assert "7 punto(s)" in parada`; pasó. `PAPEL_RESTAURADO.md` lo pega.
- **Fila 19:** hecho en el commit de cierre.
- **Riesgo 1:** es el abierto 4. «0,12» es el verificador de fichas del papel; «2,44» es el de narración, otro módulo.
