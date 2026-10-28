# F40b — Kyshtym: iniciales fuera de la narración y papel regenerado — REPORTE

Pedido de Omar (2026-10-27, «F40b»): datos, sin código; en serie. Rama `f11-guion-v4`. Modelo: Opus 5.5 (medium).
Reglas fijas cumplidas: no se cerró ningún programa de Omar; cero cambios de código y de prompts; nada de voz, imágenes ni render; no se corrió `--aprobar-papel`; tope US$ 1,00 en `lab/TOPE_TANDA.json` (`{"usd": 1.00, "desde": "2026-10-27T20:05:45"}`).

## Paso 0
Línea 2026-10-27 20:05 agregada al final de `DECISIONES.md` (sección «2026-10-27»), tal cual. Commit **`56bf26f`**, solo `DECISIONES.md`, md5 `2067e63158b53016b540695251f18617` en el mensaje.

## 1. Iniciales fuera de la narración (`lab/hyperframes/f40/f40b/iniciales.py`)
Regex del pedido: una o más «Letra mayúscula + punto + espacio» seguidas de una palabra con mayúscula. **Antes de reemplazar**, cada coincidencia con su oración (`iniciales_lista.txt`):
```
== 01b_narracion_v3.json: 9 coincidencia(s)
  «V. A. Saprykin» → «Saprykin» · en: …Sobre la cubierta, una capa de tierra y césped verde recién puesto, como si ahí abajo no hubiera nada. V. A. Saprykin preguntó si todo eso no se iba a derrumbar bajo su propio peso.…
  «N. I. Ivanov» → «Ivanov» · en: …Era mil novecientos cincuenta y seis y la planta no podía esperar; N. I. Ivanov lo había dicho así: «No se puede esperar a que todo sea como uno quiere.…
  «L. A. Buldakov» → «Buldakov» · en: …En julio, en una sesión del Sóviet Supremo de la URSS, se habla por fin del tanque catorce, y el dieciocho de julio L. A. Buldakov afirma ahí, de pie, que en tres años de seguimiento no se registró ninguna forma de enfermedad por radiación.…
  «V. A. Saprykin» → «Saprykin» · en: …Sobre la cubierta, una capa de tierra y césped verde recién puesto, como si ahí abajo no hubiera nada. V. A. Saprykin preguntó si todo eso no se iba a derrumbar bajo su propio peso.…
  «V. A. Saprykin» → «Saprykin» · en: …Sobre la cubierta, una capa de tierra y césped verde recién puesto, como si ahí abajo no hubiera nada. V. A. Saprykin preguntó si todo eso no se iba a derrumbar bajo su propio peso.…
  «N. I. Ivanov» → «Ivanov» · en: …Era mil novecientos cincuenta y seis y la planta no podía esperar; N. I. Ivanov lo había dicho así: «No se puede esperar a que todo sea como uno quiere.…
  «N. I. Ivanov» → «Ivanov» · en: …Era mil novecientos cincuenta y seis y la planta no podía esperar; N. I. Ivanov lo había dicho así: «No se puede esperar a que todo sea como uno quiere.…
  «L. A. Buldakov» → «Buldakov» · en: …En julio, en una sesión del Sóviet Supremo de la URSS, se habla por fin del tanque catorce, y el dieciocho de julio L. A. Buldakov afirma ahí, de pie, que en tres años de seguimiento no se registró ninguna forma de enfermedad por radiación.…
  «L. A. Buldakov» → «Buldakov» · en: …En julio, en una sesión del Sóviet Supremo de la URSS, se habla por fin del tanque catorce, y el dieciocho de julio L. A. Buldakov afirma ahí, de pie, que en tres años de seguimiento no se registró ninguna forma de enfermedad por radiación.…
== 01b_narration.json: 6 coincidencia(s)
  «V. A. Saprykin» → «Saprykin» · en: …Sobre la cubierta, una capa de tierra y césped verde recién puesto, como si ahí abajo no hubiera nada. V. A. Saprykin preguntó si todo eso no se iba a derrumbar bajo su propio peso.…
  «V. A. Saprykin» → «Saprykin» · en: …Sobre la cubierta, una capa de tierra y césped verde recién puesto, como si ahí abajo no hubiera nada. V. A. Saprykin preguntó si todo eso no se iba a derrumbar bajo su propio peso.…
  «N. I. Ivanov» → «Ivanov» · en: …Era mil novecientos cincuenta y seis y la planta no podía esperar; N. I. Ivanov lo había dicho así: «No se puede esperar a que todo sea como uno quiere.…
  «N. I. Ivanov» → «Ivanov» · en: …Era mil novecientos cincuenta y seis y la planta no podía esperar; N. I. Ivanov lo había dicho así: «No se puede esperar a que todo sea como uno quiere.…
  «L. A. Buldakov» → «Buldakov» · en: …En julio, en una sesión del Sóviet Supremo de la URSS, se habla por fin del tanque catorce, y el dieciocho de julio L. A. Buldakov afirma ahí, de pie, que en tres años de seguimiento no se registró ninguna forma de enfermedad por radiación.…
  «L. A. Buldakov» → «Buldakov» · en: …En julio, en una sesión del Sóviet Supremo de la URSS, se habla por fin del tanque catorce, y el dieciocho de julio L. A. Buldakov afirma ahí, de pie, que en tres años de seguimiento no se registró ninguna forma de enfermedad por radiación.…
== 01b_guionista_v4.json: 8 coincidencia(s)
  «V. A. Saprykin» → «Saprykin» · en: …Sobre la cubierta, una capa de tierra y césped verde recién puesto, como si ahí abajo no hubiera nada. V. A. Saprykin preguntó si todo eso no se iba a derrumbar bajo su propio peso.…
  «N. I. Ivanov» → «Ivanov» · en: …Era mil novecientos cincuenta y seis y la planta no podía esperar; N. I. Ivanov lo había dicho así: «No se puede esperar a que todo sea como uno quiere.…
  «L. A. Buldakov» → «Buldakov» · en: …En julio, en una sesión del Sóviet Supremo de la URSS, se habla por fin del tanque catorce, y el dieciocho de julio L. A. Buldakov afirma ahí, de pie, que en tres años de seguimiento no se registró ninguna forma de enfermedad por radiación.…
  «V. A. Saprykin» → «Saprykin» · en: …Sobre la cubierta, una capa de tierra y césped verde recién puesto, como si ahí abajo no hubiera nada. V. A. Saprykin preguntó si todo eso no se iba a derrumbar bajo su propio peso.…
  «N. I. Ivanov» → «Ivanov» · en: …Era mil novecientos cincuenta y seis y la planta no podía esperar; N. I. Ivanov lo había dicho así: «No se puede esperar a que todo sea como uno quiere.…
  «L. A. Buldakov» → «Buldakov» · en: …En julio, en una sesión del Sóviet Supremo de la URSS, se habla por fin del tanque catorce, y el dieciocho de julio L. A. Buldakov afirma ahí, de pie, que en tres años de seguimiento no se registró ninguna forma de enfermedad por radiación.…
  «A. A. Kazutov)» → «Kazutov)» · en: …cap 2: la cita «¿Quién sabe qué fuerza se necesita para …» va entre comillas y con su autor (A. A. Kazutov) al lado…
  «A. A. Kazutov)» → «Kazutov)» · en: …la cita «¿Quién sabe qué fuerza se necesita para …» va entre comillas y con su autor (A. A. Kazutov) al lado…
```
Todas son iniciales de persona (Saprykin, Ivanov, Buldakov, y Kazutov en dos textos de bloqueantes que guarda `01b_guionista_v4.json`, no en la narración): no hubo PARADA. Reemplazo con respaldo `_pre_f40b` de cada archivo (`iniciales_aplicar.txt`):
```
- 01b_narracion_v3.json: 9 reemplazo(s) · md5 58a232f0c2c6c6a6ed29cc70fd132b6b → 5f44561c229f1c13a3ffc18104276cf3 · respaldo 01b_narracion_v3_pre_f40b.json
- 01b_narration.json: 6 reemplazo(s) · md5 1d2fc5530c84d65e3ad3414d6ae3a9bc → dccfcd96648c077a365689f5dbd7affe · respaldo 01b_narration_pre_f40b.json
- 01b_guionista_v4.json: 8 reemplazo(s) · md5 a9c666783cde6833ec0e301551c28f98 → cc2e7c500abdc5550ad5be71122c76a6 · respaldo 01b_guionista_v4_pre_f40b.json
grep final:
  01b_narracion_v3.json: iniciales 0 · cenás 0 · acá 0
  01b_narration.json: iniciales 0 · cenás 0 · acá 0
  01b_guionista_v4.json: iniciales 0 · cenás 0 · acá 0
```

## 2. Papel regenerado
Como F40 C.3: `fase1_5._topic_v3` + `fase1_5.run_pantalla("f39-kyshtym", pool, log)` → `m01e_pantalla.generar`, sin script nuevo. Respaldo previo `01e_pantalla_f40.json/.md/.raw.json` (md5 `f197b7d5…` / `0ba9c0ad…` / `3d25b3f0…`). Corrida 20:05:45 → 20:07:55 (`pantalla.log`):
```
  m01e intento 1: in 47865 · out 18145 · US$ 0.2772 · JSON
  m01e intento 1 validado: fichas fuera 0 · preguntas 7 · vuelven 5 · picos vacíos 0
  m01e intento 2: in 55780 · out 418 · US$ 0.1157 · JSON
  m01e vuelta 1 validada: fichas fuera 0 · preguntas nuevas 0 · picos vacíos 0
  m01e: 5 motivo(s) sin beat → sin otra vuelta (anotados)
  m01e: 12 fichas · 9 sellos · 6 relojes → C:\CLAUDE_PROJECTS\automatization_videos\data\scripts\_steps\f39-kyshtym\01e_pantalla.md
papel: sí
exit=0
```
**US$ 0,3929** (2 llamadas: 0,2772 + 0,1157), dentro del tope de 1,00. 1 vuelta; cierre «sin beat»; cortados al cierre: nada; gancho con ficha (D03); picos vacíos y `a_pantalla` vacíos: ninguno.

**«2000» volvió sin punto** en D83 (ch07 beat 11; en D90 los números de 4 cifras son años, «1957 y 1959»). Corregido con `m01e_pantalla.editar`, como en F40 C.4 (`edicion_2000.txt`); ninguna otra edición:
```
antes: ch07 11 · ENFERMOS POR RADIACIÓN · Más de 2000 diagnosticados, 1948-1958 · md5 papel 6071496b4cec68730154c0a0fcc099fb
después: ENFERMOS POR RADIACIÓN · Más de 2.000 diagnosticados, 1948-1958 · editado True · caracteres 60 · md5 papel 62e1da7c5b5df17d388db83d6b6a9a94
```
`editar` no volvió a guardar `01e_pantalla.antes_de_edicion.json` porque ya existía (es el de F40, 19:02): la copia previa de esta edición es `01e_pantalla_f40.*` más el papel recién generado (md5 `6071496b…` del .json antes de editar, en el log de arriba).

## 3. Salida en texto
## Diff ficha por ficha contra el papel de F40 (`01e_pantalla_f40.*`, .md `0ba9c0ad…`)

| cap · beat | ficha F40 | ficha F40b | sello F40 → F40b | |
|---|---|---|---|---|
| ch01 · 1 | D03 «GRAVEDAD EN LA ESCALA NUCLEAR · Nivel 6 de 7» [5] | D03 «QUÉ TAN GRAVE FUE · Nivel 6 de 7 en la escala internacional» [5] | MEMORIA → AMENAZA | misma ficha, otro texto |
| ch02 · 2 | D194 «LAS DOS PRIMERAS PROMOCIONES · Murieron casi todos» [6] | D194 «LAS DOS PRIMERAS PROMOCIONES · Murieron casi por completo» [6] | CALMA → AVISO | misma ficha, otro texto |
| ch02 · 3 | D31 «EL CÉSPED ERA CAMUFLAJE · Encima, 2 metros de tierra» [15] | D31 «ENCIMA DE TODO · 2 metros de tierra y césped» [15] | AMENAZA → CALMA | misma ficha, otro texto |
| ch03 · 4 | T21 «ESE MISMO AÑO · Se decide dejar de verter residuos en el río Techa» [2] | D79 «UN ANTECEDENTE EN LA PLANTA · En 1953, primera reacción en cadena sin control» [6] | INMINENTE → INMINENTE | cambia |
| ch04 · 5 | D47 «ESTIMACIÓN POSTERIOR · Entre 70 y 100 toneladas de TNT» [9] | D50 «LA FUGA, COMPARADA · Chernóbil: unas 19 veces más» [10] | COLAPSO → COLAPSO | cambia |
| ch04 · 6 | D17 «GENTE EN LA ZONA CONTAMINADA · 270.000 habitantes en 217 localidades» [19] | D17 «LA ZONA CONTAMINADA · 270.000 habitantes en 217 localidades» [19] | — → — | misma ficha, otro texto |
| ch05 · 7 | D93 «VECINOS SIN EVACUAR · 86.000 habitantes» [9] | D93 «CIUDAD SIN EVACUAR · 86.000 habitantes» [9] | RABIA → RABIA | misma ficha, otro texto |
| ch05 · 8 | P04 «SLAVSKY, MINISTRO · De Construcción de Maquinaria Mediana» [19] | D138 «LAS MÁS CONTAMINADAS · Calle Lenin y calle Shkolnaya» [16] | — → ALARMA | cambia |
| ch06 · 9 | D20 «TOTAL DE REUBICADOS · 12.763 personas» [6] | D40 «GENTE SIN SU PUEBLO · De 10.000 a 12.000 personas» [7] | SILENCIO → — | cambia |
| ch06 · 10 | D90 «DOSIS ENTRE 1957 Y 1959 · Unos 30.000 trabajadores y militares con más de 0,25 Sv» [18] | D90 «LOS QUE LIMPIARON · Unos 30.000, entre 1957 y 1959» [19] | — → SILENCIO | misma ficha, otro texto |
| ch07 · 11 | D83 «ENFERMOS ENTRE 1948 Y 1958 · Más de 2.000 obreros con enfermedad por radiación» [7] | D83 «ENFERMOS POR RADIACIÓN · Más de 2.000 diagnosticados, 1948-1958» [5] | — → — | misma ficha, otro texto |
| ch07 · 12 | D201 «OTRA MUERTE · Valia, 38 años: pulmones de piedra» [19] | D171 «LAS DOSIS RECIBIDAS · Más altas que en Chernóbil» [17] | — → MEMORIA | cambia |

Relojes F40 6 · F40b 6 · iguales: True
Fichas F40 12 · F40b 12; sellos F40 7 · F40b 9
Picos vacíos F40b [] · a_pantalla vacíos F40b []
Reintento F40b: vueltas 1 · cierre 'sin beat' · cortados al cierre [] · US$ 0.39292

## Oraciones de ch03 [0]–[8] como quedan (las que lee el papel, `caps[ch03].oraciones`)

- [0] Las tuberías de refrigeración de uno de los contenedores tenían fugas.
- [1] Y las desconectaron.
- [2] Era mil novecientos cincuenta y seis y la planta no podía esperar; Ivanov lo había dicho así: «No se puede esperar a que todo sea como uno quiere.
- [3] Hay que hacer lo necesario para que el trabajo avance», en las condiciones que existían, sin perder un solo día.
- [4] Entre el nueve de marzo y el diez de abril de mil novecientos cincuenta y siete, al tanque número catorce le entraron doscientos cincuenta y seis metros cúbicos de residuos de producción.
- [5] Adentro quedaron setenta u ochenta toneladas, sin el agua que las tuberías rotas ya no traían.
- [6] La investigación que vino después consideró probable lo que ocurrió ahí dentro durante esos meses: los residuos se calentaron solos, hasta trescientos treinta, trescientos cincuenta grados; el líquido se fue y quedaron sales secas de nitrato y acetato de sodio, cocinándose dentro del hormigón, bajo el césped.
- [7] ¿Quién miraba la temperatura?
- [8] El tanque catorce quedó lleno en abril.

ch03 tenía 12 oraciones en el papel de F40 y tiene 10 ahora.

Nota: **ch04 beat 5 ahora tiene D50** («LA FUGA, COMPARADA · Chernóbil: unas 19 veces más»), elegido por el autor sin edición (en F40 era D47). En ch03, [2]–[3] siguen partidas, pero en el punto de la propia cita de Ivanov («…como uno quiere.» / «Hay que hacer…»), no en iniciales: ch03 pasó de 12 a 10 oraciones.

### `01e_pantalla.md` nuevo, ENTERO (`data/scripts/_steps/f39-kyshtym/01e_pantalla.md`, después de la edición; copia en `lab/hyperframes/f40/f40b/01e_pantalla.md`)

````markdown
# Guion de pantalla en papel — f39-kyshtym

`m01e_pantalla` m01e-6 (md5 del prompt `3b98aef1d8595124967ac7a85b75bab7`) · claude-sonnet-5-5 medium · 2 intento(s) · US$ 0.3929 · tokens de entrada 47865

Segundos por palabra 0.3459 (mediana de 200 oraciones de 9 caps del narrador N9Z5MLTIaHFLflaLtbDi) · tope US$ 1.0 (respaldo (el perfil no trae costos.m01e_tope_usd)) · intento 1: in 47865 · out 18145 · US$ 0.2772 · intento 2: in 55780 · out 418 · US$ 0.1157

Totales: 12 fichas · 9 sellos · 6 relojes · 58 descartados

## ch01 — La luz que no era fuego

- beat 1 · gancho · PICO · ficha **D03** [normal] «QUÉ TAN GRAVE FUE · Nivel 6 de 7 en la escala internacional» en [5] sobre «cráter» (56/90 car.) · respaldo: «nivel 6 de 7 en la escala internacional de eventos radiológicos del OIEA» · año — / relato — · juzgado por el autor: otro hecho {'no_dicho': ['6', '7'], 'spoiler': ['6', '7']} · aporta: Pone una calificación oficial de gravedad al accidente, que la voz no dice en ningún momento del video. · sello **AMENAZA** en [5]
- relojes: —

## ch02 — La ciudad sin mapa

- beat 2 · planteo · ficha **D194** [normal] «LAS DOS PRIMERAS PROMOCIONES · Murieron casi por completo» en [6] sobre «mueren» (54/90 car.) · respaldo: «Las dos primeras promociones de trabajadores de la planta murieron casi por completo.» · año — / relato 1957 · aporta: Convierte el rumor de las aldeas en un dato: lo que le pasó a los primeros trabajadores de la planta. · sello **AVISO** en [6]
- beat 3 · planteo · PICO · ficha **D31** [normal] «ENCIMA DE TODO · 2 metros de tierra y césped» en [15] sobre «césped» (41/90 car.) · respaldo: «capa de tierra de 2 metros de espesor y césped para camuflaje» · año — / relato 1957 · juzgado por el autor: otro hecho {'spoiler': ['2']} · aporta: Dice cuánta tierra había sobre la tapa: la voz solo habla de una capa de tierra y césped. · sello **CALMA** en [15]
- relojes: —

## ch03 — El tanque catorce

- beat 4 · escalada · PICO · ficha **D79** [normal] «UN ANTECEDENTE EN LA PLANTA · En 1953, primera reacción en cadena sin control» en [6] sobre «residuos» (74/90 car.) · respaldo: «En 1953, ocurrió la primera reacción en cadena autointensificada en la planta química» · año 1953 / relato 1957 · aporta: Muestra que la planta ya había tenido un descontrol nuclear en 1953; la voz no lo cuenta. · sello **INMINENTE** en [8]
- relojes: 9 MAR 1957 en [4], 10 ABR 1957 en [4]

## ch04 — Un domingo de fútbol

- beat 5 · pico · PICO · ficha **D50** [normal] «LA FUGA, COMPARADA · Chernóbil: unas 19 veces más» en [10] sobre «curios» (46/46 car.) · respaldo: «fue aproximadamente 19 veces mayor que la de Kyshtym» · año — / relato 1957 · aporta: Pone la cifra de la fuga en escala con Chernóbil, algo que la voz no hace. · sello **COLAPSO** en [7]
- beat 6 · respiro · ficha **D17** [normal] «LA ZONA CONTAMINADA · 270.000 habitantes en 217 localidades» en [19] sobre «franja» (56/90 car.) · respaldo: «270.000 habitantes en 217 localidades» · año — / relato 1957 · aporta: Dice cuánta gente vivía bajo la franja radiactiva; la voz solo da su largo. · sello —
- relojes: 29 SEP 1957 en [0]

## ch05 — La aurora de Cheliábinsk

- beat 7 · giro · PICO · ficha **D93** [normal] «CIUDAD SIN EVACUAR · 86.000 habitantes» en [9] sobre «defensa» (35/90 car.) · respaldo: «con 86.000 habitantes» · año — / relato 1957 · aporta: Dice cuánta gente quedó en la ciudad sin evacuar; la voz no da la cifra. · sello **RABIA** en [5]
- beat 8 · escalada · ficha **D138** [normal] «LAS MÁS CONTAMINADAS · Calle Lenin y calle Shkolnaya» en [16] sobre «calles» (49/90 car.) · respaldo: «la calle Lenin y la calle Shkolnaya» · año — / relato 1957 · aporta: Nombra las calles donde la contaminación era peor, que es justo lo que las mujeres lavaban con baldes. · sello **ALARMA** en [20]
- relojes: 6 OCT 1957 en [12]

## ch06 — Los pueblos enterrados

- beat 9 · consecuencia · ficha **D40** [normal] «GENTE SIN SU PUEBLO · De 10.000 a 12.000 personas» en [7] sobre «pueblos» (46/57 car.) · respaldo: «con una población de 10.000 a 12.000 personas» · año — / relato 1960 · aporta: Pone en personas los veintitrés pueblos enterrados; la voz solo da el número de pueblos. · sello —
- beat 10 · revelacion · PICO · ficha **D90** [papel] «LOS QUE LIMPIARON · Unos 30.000, entre 1957 y 1959» en [19] sobre «trabajadores» (47/90 car.) · respaldo: «Entre 1957 y 1959, unos 30.000 trabajadores del combinado y militares» · año — / relato 1960 · juzgado por el autor: otro hecho {'no_dicho': ['1959'], 'spoiler': ['1959']} · aporta: Dice cuántos trabajadores y militares participaron en la limpieza; la voz no da la cifra. · sello **SILENCIO** en [21]
- relojes: —

## ch07 — Lo que calló el acta

- beat 11 · revelacion · PICO · ficha **D83** [normal] «ENFERMOS POR RADIACIÓN · Más de 2.000 diagnosticados, 1948-1958» en [5] sobre «ninguna» (60/90 car.) · respaldo: «Entre 1948 y 1958, más de 2000 trabajadores fueron diagnosticados con enfermedad profesional por radiación» · aporta: Contrasta en silencio la declaración de «ningún caso» con los diagnósticos de trabajadores en la misma planta. · sello —
- beat 12 · cierre · ficha **D171** [normal] «LAS DOSIS RECIBIDAS · Más altas que en Chernóbil» en [17] sobre «enfermedad» (45/51 car.) · respaldo: «fueron considerablemente más altas que en Chernóbil» · año — / relato 1998 · aporta: Compara las dosis de los trabajadores con las de Chernóbil, que la voz no menciona. · sello **MEMORIA** en [14]
- relojes: 13 ABR 1958 en [0], 16 JUN 1989 en [4]

## Lo que cayó

- (nada)

## Reintento: los motivos que se le mandaron al autor

- D03 (ch01 beat 1, oración [5]) «QUÉ TAN GRAVE FUE · Nivel 6 de 7 en la escala internacional»: la voz dice «6» en ch05 [12] («Seis de octubre de mil novecientos cincuenta y siete.»); ¿es el mismo hecho? si no, mantenelo
- D03 (ch01 beat 1, oración [5]) «QUÉ TAN GRAVE FUE · Nivel 6 de 7 en la escala internacional»: la voz dice «7» en ch04 [14] («A las siete y veinte de la tarde, el viento ya había decidido hacia dónde.»); ¿es el mismo hecho? si no, mantenelo
- D03 (ch01 beat 1, oración [5]) «QUÉ TAN GRAVE FUE · Nivel 6 de 7 en la escala internacional»: la voz dice «6» en una oración posterior en ch05 [12] («Seis de octubre de mil novecientos cincuenta y siete.»); ¿es el mismo hecho? si no, mantenelo
- D03 (ch01 beat 1, oración [5]) «QUÉ TAN GRAVE FUE · Nivel 6 de 7 en la escala internacional»: la voz dice «7» en una oración posterior en ch04 [14] («A las siete y veinte de la tarde, el viento ya había decidido hacia dónde.»); ¿es el mismo hecho? si no, mantenelo
- D31 (ch02 beat 3, oración [15]) «ENCIMA DE TODO · 2 metros de tierra y césped»: la voz dice «2» en una oración posterior en ch04 [2] («Dos equipos de la ciudad en la cancha, y en las gradas muchachos de la edad de Valevich y de los del comedor.»); ¿es el mismo hecho? si no, mantenelo
- D90 (ch06 beat 10, oración [19]) «LOS QUE LIMPIARON · Unos 30.000, entre 1957 y 1959»: la voz dice «1959» en la oración ancla o en una vecina en ch06 [20] («En mil novecientos cincuenta y nueve, Valevich se fue.»); ¿es el mismo hecho? si no, mantenelo
- D90 (ch06 beat 10, oración [19]) «LOS QUE LIMPIARON · Unos 30.000, entre 1957 y 1959»: la voz dice «1959» en una oración posterior en ch06 [20] («En mil novecientos cincuenta y nueve, Valevich se fue.»); ¿es el mismo hecho? si no, mantenelo
- D122: dijiste que la voz lo dice («La voz ya dice los ocho metros de profundidad.»); la voz de ch02 no dice «8,2» («El tanque que explotó era de acero inoxidable y estaba en un cañón de hormigón a 8,2 metros de profundidad.»): vuelve a ser candidato
- T27: dijiste que la voz lo dice («La voz cuenta el rumbo noreste.»); la voz de ch04 no dice «1» («Una nube radiactiva se eleva hasta 1 km y se desplaza en dirección noreste, formando la Traza Radiactiva del Ural Oriental (VURS). (fecha 1957-09-29)»): vuelve a ser candidato
- T40: dijiste que la voz lo dice («La voz cuenta la nota sobre la aurora.»); la voz de ch05 no dice «Chelyabinsk» («Un periódico de Chelyabinsk publicó una nota que atribuía el resplandor en el cielo a una aurora polar. (fecha 1957-10-06)»): vuelve a ser candidato
- T61: dijiste que la voz lo dice («La voz dice el reportaje del 16 de junio de 1989.»); la voz de ch07 no dice «Rabochi» ni «Mayak» («El periódico "Chelyabinski Rabochi" publica el primer informe de prensa sobre el accidente de 1957 en Mayak. (fecha 1989-06-16)»): vuelve a ser candidato
- D152: dijiste que la voz lo dice («La voz cuenta los dos litigios de Valevich.»); la voz de ch07 no dice «2» («A Anatoly Valevich le llevó dos procesos judiciales, primero contra el Fondo de Seguro Social y luego contra la Dirección de Protección Social, para que se le reconocieran sus derechos.»): vuelve a ser candidato

### Preguntas y respuesta del autor

- D03 {'no_dicho': ['6', '7'], 'spoiler': ['6', '7']}: la mantuvo en ch01 beat 1 [5]: otro hecho
- D31 {'spoiler': ['2']}: la mantuvo en ch02 beat 3 [15]: otro hecho
- D90 {'no_dicho': ['1959'], 'spoiler': ['1959']}: la mantuvo en ch06 beat 10 [19]: otro hecho

### Reintento parcial: 1 vuelta(s)

#### Vuelta 1 · US$ 0.1157

- beats que podía cambiar: ch01 beat 1, ch02 beat 3, ch06 beat 10
- motivos:
  - D03 (ch01 beat 1, oración [5]) «QUÉ TAN GRAVE FUE · Nivel 6 de 7 en la escala internacional»: la voz dice «6» en ch05 [12] («Seis de octubre de mil novecientos cincuenta y siete.»); ¿es el mismo hecho? si no, mantenelo
  - D03 (ch01 beat 1, oración [5]) «QUÉ TAN GRAVE FUE · Nivel 6 de 7 en la escala internacional»: la voz dice «7» en ch04 [14] («A las siete y veinte de la tarde, el viento ya había decidido hacia dónde.»); ¿es el mismo hecho? si no, mantenelo
  - D03 (ch01 beat 1, oración [5]) «QUÉ TAN GRAVE FUE · Nivel 6 de 7 en la escala internacional»: la voz dice «6» en una oración posterior en ch05 [12] («Seis de octubre de mil novecientos cincuenta y siete.»); ¿es el mismo hecho? si no, mantenelo
  - D03 (ch01 beat 1, oración [5]) «QUÉ TAN GRAVE FUE · Nivel 6 de 7 en la escala internacional»: la voz dice «7» en una oración posterior en ch04 [14] («A las siete y veinte de la tarde, el viento ya había decidido hacia dónde.»); ¿es el mismo hecho? si no, mantenelo
  - D31 (ch02 beat 3, oración [15]) «ENCIMA DE TODO · 2 metros de tierra y césped»: la voz dice «2» en una oración posterior en ch04 [2] («Dos equipos de la ciudad en la cancha, y en las gradas muchachos de la edad de Valevich y de los del comedor.»); ¿es el mismo hecho? si no, mantenelo
  - D90 (ch06 beat 10, oración [19]) «LOS QUE LIMPIARON · Unos 30.000, entre 1957 y 1959»: la voz dice «1959» en la oración ancla o en una vecina en ch06 [20] («En mil novecientos cincuenta y nueve, Valevich se fue.»); ¿es el mismo hecho? si no, mantenelo
  - D90 (ch06 beat 10, oración [19]) «LOS QUE LIMPIARON · Unos 30.000, entre 1957 y 1959»: la voz dice «1959» en una oración posterior en ch06 [20] («En mil novecientos cincuenta y nueve, Valevich se fue.»); ¿es el mismo hecho? si no, mantenelo
  - D122: dijiste que la voz lo dice («La voz ya dice los ocho metros de profundidad.»); la voz de ch02 no dice «8,2» («El tanque que explotó era de acero inoxidable y estaba en un cañón de hormigón a 8,2 metros de profundidad.»): vuelve a ser candidato
  - T27: dijiste que la voz lo dice («La voz cuenta el rumbo noreste.»); la voz de ch04 no dice «1» («Una nube radiactiva se eleva hasta 1 km y se desplaza en dirección noreste, formando la Traza Radiactiva del Ural Oriental (VURS). (fecha 1957-09-29)»): vuelve a ser candidato
  - T40: dijiste que la voz lo dice («La voz cuenta la nota sobre la aurora.»); la voz de ch05 no dice «Chelyabinsk» («Un periódico de Chelyabinsk publicó una nota que atribuía el resplandor en el cielo a una aurora polar. (fecha 1957-10-06)»): vuelve a ser candidato
  - T61: dijiste que la voz lo dice («La voz dice el reportaje del 16 de junio de 1989.»); la voz de ch07 no dice «Rabochi» ni «Mayak» («El periódico "Chelyabinski Rabochi" publica el primer informe de prensa sobre el accidente de 1957 en Mayak. (fecha 1989-06-16)»): vuelve a ser candidato
  - D152: dijiste que la voz lo dice («La voz cuenta los dos litigios de Valevich.»); la voz de ch07 no dice «2» («A Anatoly Valevich le llevó dos procesos judiciales, primero contra el Fondo de Seguro Social y luego contra la Dirección de Protección Social, para que se le reconocieran sus derechos.»): vuelve a ser candidato
- aplicados: —

### Motivos sin beat (no hubo reintento)

- D122: dijiste que la voz lo dice («La voz ya dice los ocho metros de profundidad.»); la voz de ch02 no dice «8,2» («El tanque que explotó era de acero inoxidable y estaba en un cañón de hormigón a 8,2 metros de profundidad.»): vuelve a ser candidato
- T27: dijiste que la voz lo dice («La voz cuenta el rumbo noreste.»); la voz de ch04 no dice «1» («Una nube radiactiva se eleva hasta 1 km y se desplaza en dirección noreste, formando la Traza Radiactiva del Ural Oriental (VURS). (fecha 1957-09-29)»): vuelve a ser candidato
- T40: dijiste que la voz lo dice («La voz cuenta la nota sobre la aurora.»); la voz de ch05 no dice «Chelyabinsk» («Un periódico de Chelyabinsk publicó una nota que atribuía el resplandor en el cielo a una aurora polar. (fecha 1957-10-06)»): vuelve a ser candidato
- T61: dijiste que la voz lo dice («La voz dice el reportaje del 16 de junio de 1989.»); la voz de ch07 no dice «Rabochi» ni «Mayak» («El periódico "Chelyabinski Rabochi" publica el primer informe de prensa sobre el accidente de 1957 en Mayak. (fecha 1989-06-16)»): vuelve a ser candidato
- D152: dijiste que la voz lo dice («La voz cuenta los dos litigios de Valevich.»); la voz de ch07 no dice «2» («A Anatoly Valevich le llevó dos procesos judiciales, primero contra el Fondo de Seguro Social y luego contra la Dirección de Protección Social, para que se le reconocieran sus derechos.»): vuelve a ser candidato

## Cierre del reintento

- cerró por: **sin beat** (después de 1 vuelta)
- cortado al cerrar, sin preguntarle al autor: (nada)

## Descartados por el modelo

- Q18 [voz_lo_dice]: La voz cita a Valevich casi literal en la oración 6 del capítulo 1.
- D153 [voz_lo_dice]: La voz dice los cincuenta estudiantes trasladados, incluido Valevich.
- Q19 [voz_lo_dice]: La voz cita la frase de Kurchatov y Tal.
- Q24 [voz_lo_dice]: La voz lee los chocolateros y la planta 25.
- Q01 [voz_lo_dice]: La voz cita la pregunta sobre qué fuerza haría falta para destruir el tanque.
- Q05 [voz_lo_dice]: La voz cuenta la pregunta de Saprykin.
- Q06 [voz_lo_dice]: La voz cita la locomotora con el ténder.
- D30 [voz_lo_dice]: La voz ya dice las ciento sesenta toneladas de la cubierta.
- D122 [voz_lo_dice]: La voz ya dice los ocho metros de profundidad. — **falso: la voz no dice ['8,2']**
- D07 [spoiler]: Las 70-80 toneladas las cuenta la voz en el capítulo 3.
- T20 [voz_lo_dice]: La voz dice que las tuberías perdían y se desconectaron.
- T23 [voz_lo_dice]: La voz dice el llenado entre el 9 de marzo y el 10 de abril.
- D101 [voz_lo_dice]: La voz dice setenta u ochenta toneladas.
- D46 [voz_lo_dice]: La voz dice el autocalentamiento hasta 330-350 grados.
- Q16 [voz_lo_dice]: La voz cita a Ivanov.
- T28 [voz_lo_dice]: La voz dice las cuatro y veintidós y la explosión.
- D09 [voz_lo_dice]: La voz dice las 25-29 toneladas de TNT.
- D10 [voz_lo_dice]: La voz dice el cráter de diez metros de hondo y veinte de ancho.
- D35 [voz_lo_dice]: La voz dice que la cubierta de ciento sesenta toneladas voló.
- D11 [voz_lo_dice]: La voz dice los veinte millones de curios.
- D12 [voz_lo_dice]: La voz dice que noventa de cada cien partes cayeron en el combinado.
- D91 [otro]: La voz ya dice las más de cinco mil personas; lo que suma es la dosis en sieverts, demasiado técnica para entenderse en 3 segundos.
- T32 [voz_lo_dice]: La voz dice el cielo rosado y azul claro.
- T27 [voz_lo_dice]: La voz cuenta el rumbo noreste. — **falso: la voz no dice ['1']**
- T30 [voz_lo_dice]: La voz dice las siete y veinte y Bagaryak.
- T31 [voz_lo_dice]: La voz dice que la nube llega a Tiumén.
- T36 [voz_lo_dice]: La voz dice las tres de la mañana y la franja completa.
- D37 [voz_lo_dice]: La voz da la franja de 300-350 km.
- T35 [voz_lo_dice]: La voz cuenta los vidrios rotos y que no les dicen el nivel.
- T34 [voz_lo_dice]: La voz dice que llevan al personal diurno al área contaminada.
- T37 [voz_lo_dice]: La voz dice la primera medición de las cuatro de la mañana.
- T33 [voz_lo_dice]: La voz dice que empieza el estudio radiológico.
- Q14 [voz_lo_dice]: La voz cita la respuesta del director.
- Q02 [voz_lo_dice]: La voz cita la nota de la aurora polar.
- Q07 [voz_lo_dice]: La voz cuenta que la nota decía que habría más auroras.
- T40 [voz_lo_dice]: La voz cuenta la nota sobre la aurora. — **falso: la voz no dice ['Chelyabinsk']**
- T38 [voz_lo_dice]: La voz dice la llegada de la comisión de Slavsky.
- T39 [voz_lo_dice]: La voz dice los 1100 evacuados y las tres aldeas.
- D104 [voz_lo_dice]: La voz dice los seiscientos evacuados.
- D136 [voz_lo_dice]: La voz cuenta el dosímetro sobre el chico que juega.
- T43 [voz_lo_dice]: La voz cuenta los destacamentos que tumbaron y enterraron todo.
- D19 [voz_lo_dice]: La voz dice las veintitrés localidades.
- D21 [voz_lo_dice]: La voz dice los setecientos kilómetros cuadrados.
- D159 [voz_lo_dice]: La voz cuenta los vehículos que no pudieron limpiarse.
- D158 [voz_lo_dice]: La voz cuenta los doscientos presos hospitalizados.
- Q11 [voz_lo_dice]: La voz cita el testimonio de la trabajadora.
- D145 [voz_lo_dice]: La voz cuenta al jefe de Belenkov que agonizó.
- Q21 [voz_lo_dice]: La voz cita la pregunta a Gutnikov.
- T50 [otro]: Suma contexto (el decreto que permitía irse), pero el beat 10 ya lleva una ficha, la del dato de los 30.000.
- D20 [otro]: Las fuentes dan tres totales de reasentados que no coinciden; mostrarlas juntas necesita más de una línea.
- Q03 [voz_lo_dice]: La voz cuenta la declaración de Buldakov casi literal.
- D44 [voz_lo_dice]: La voz dice el diario danés y su fecha.
- T57 [voz_lo_dice]: La voz dice el informe de Medvedev en New Scientist.
- T61 [voz_lo_dice]: La voz dice el reportaje del 16 de junio de 1989. — **falso: la voz no dice ['Rabochi', 'Mayak']**
- T62 [voz_lo_dice]: La voz cuenta la sesión del Sóviet Supremo de julio.
- D152 [voz_lo_dice]: La voz cuenta los dos litigios de Valevich. — **falso: la voz no dice ['2']**
- D156 [voz_lo_dice]: La voz dice el riñón perdido en 1998.
- T64 [voz_lo_dice]: La voz dice el estatus de liquidador en 1993.
````

## US$
| paso | llamadas | US$ |
|---|---|---|
| papel (Sonnet: intento 1 + 1 vuelta) | 2 | 0,3929 |
| **total** | | **0,3929** (tope 1,00) |

## Lo que queda abierto (entero)
- b1. **La cita de Ivanov sigue partida en dos oraciones** (ch03 [2] y [3]) por su propio punto interno: el cortador parte en cualquier «. » aunque esté dentro de «…». No es de iniciales; queda en la lista de DECISIONES 18:30/20:05 (el cortador).
- b2. **Las iniciales siguen en el pool, la ficha, la escaleta y los textos de bloqueantes** del guionista (Kazutov, en dos mensajes de `01b_guionista_v4.json`, sí se quitaron porque el regex corre sobre el archivo entero). La voz ya no las lee; el arreglo general (normalizer y cortador) está en la lista de 18:30.
- b3. **`01e_pantalla.antes_de_edicion.json` es el de F40** (19:02): `editar` lo escribe solo la primera vez. El respaldo previo a esta edición es `01e_pantalla_f40.*` + el log.
- b4. **El papel cambió bastante contra F40** (5 fichas distintas y 7 con otro texto, sellos 7 → 9) por haber regenerado: el autor vuelve a elegir con la voz nueva. Es lo esperado del pedido.
- b5. **El papel de Kyshtym sigue sin aprobar:** lo aprueba Omar con `python fase1_5.py --topic f39-kyshtym --aprobar-papel "Omar <fecha>"`.
- b6. Siguen los abiertos de F40 (o1–o20) que esta tanda no toca.

## Procesos
Sin subagentes de trabajo (en serie, como pidió Omar); solo el revisor. La regeneración del papel corrió en segundo plano y terminó (exit 0). Ningún proceso vivo. No se cerró ningún programa de Omar.

## Veredicto del revisor (`revisor-handoff`, íntegro)
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 0a | Línea 2026-10-27 20:05 al final de DECISIONES.md, tal cual | OK | DECISIONES.md:124. Coincide palabra por palabra con el pedido. |
| 0b | Commit solo de DECISIONES.md, con md5 en el mensaje | OK | `56bf26f` tiene 1 archivo (+1 línea). El md5 del mensaje, 2067e631…, coincide con `md5sum DECISIONES.md`. |
| 1a | Lista previa de cada coincidencia con su oración; solo iniciales de persona | OK | `iniciales_lista.txt`: Saprykin, Ivanov, Buldakov y Kazutov. Sin PARADA, y es correcto. |
| 1b | Respaldo `_pre_f40b` de los 3 archivos | OK | Existen `01b_narracion_v3_pre_f40b.json`, `01b_narration_pre_f40b.json` y `01b_guionista_v4_pre_f40b.json`. |
| 1c | grep final = 0 iniciales, 0 «cenás», 0 «acá» | OK | Lo corrí yo sobre los 3 archivos: 0 en todo. Con un regex más laxo (`\b[A-Z]\. `) también da 0 en narration y narracion_v3. |
| 1d | md5 antes → después | OK | Los md5 de `*_pre_f40b.json` y de los actuales coinciden con `iniciales_aplicar.txt` (58a232f0→5f44561c, 1d2fc553→dccfcd96, a9c66678→cc2e7c50). |
| 2a | Respaldo `01e_pantalla_f40.*`; su .md es 0ba9c0ad… | OK | `01e_pantalla_f40.md` md5 0ba9c0ade3e1…; también existen el .json y el .raw.json. |
| 2b | Papel regenerado con la llamada de producción | OK | `pantalla.log`: cost_tracker de f39-kyshtym, intento 1 más 1 vuelta, exit 0. El reporte dice `fase1_5.run_pantalla` → `m01e_pantalla.generar`. No hay código nuevo; no pude comprobar la llamada más allá del log. |
| 2c | Única edición «2000»→«2.000» (D83 ch07) | OK | `edicion_2000.txt`: editado True. Los md5 .json 6071496b→62e1da7c coinciden con el archivo actual. |
| 3a | `01e_pantalla.md` ENTERO en el reporte | OK | Comparé el archivo con `F40b_REPORT.md` y está completo (18478 caracteres). El md5 83e8622b es idéntico entre `data/` y `lab/`. |
| 3b | Diff ficha por ficha, log, US$ ≤ 1,00, ch03 [0]–[8] | OK | Tabla de 12 fichas, log, US$ 0,3929 (0,2772 + 0,1157) y las oraciones [0]–[8] están en el reporte. Tope en `lab/TOPE_TANDA.json`: 1.00. |
| 4 | Cero código/prompts | OK | `git diff 56bf26f -- '*.py'` solo muestra `diag_234_cap4.py` (ajeno, ya modificado antes de la tanda). `iniciales.py` es un script de lab nuevo y sin trackear. |
| 5 | No se corrió `--aprobar-papel`; ningún programa de Omar cerrado; sin voz/imágenes/render | OK (por declaración) | El reporte lo declara en "Procesos" y en b5. Nada en `pantalla.log` ni en los archivos contradice eso. No hay forma de comprobar lo que no deja rastro. |
| 6 | Veredicto del revisor al final del reporte, ESTADO, commit y push | NO VERIFICABLE | Es posterior a mi revisión. `lab/ESTADO_SESION.md` figura modificado y `lab/hyperframes/f40/f40b/` sin trackear; falta commit y push. |

Observaciones:
- Se editaron también dos textos de bloqueantes dentro de `01b_guionista_v4.json` ("A. A. Kazutov"). No son narración, pero el regex corre sobre el archivo entero, como pedía Omar. El reporte lo declara.
- Afirmación sin verificar: "ch03 pasó de 12 a 10 oraciones". No lo comprobé contra el .json (mi intento de leerlo falló por estructura). Las oraciones [0]–[8] sí coinciden con lo esperado: [2] y [3] ya no se parten en las iniciales.
- La cita de Ivanov sigue partida en ch03 [2]/[3] por su propio punto interno. El reporte lo anota como b1.
- El papel cambió bastante contra F40: 5 fichas distintas y 7 con otro texto. Es lo esperado al regenerar. D50 entró en ch04 sin edición.
- `01e_pantalla.antes_de_edicion.json` es el de F40; `editar` solo lo escribe la primera vez. El reporte lo declara (b3).

Fuera de alcance: ninguno. El único archivo modificado ajeno a la tanda es `diag_234_cap4.py`, que ya estaba modificado. `lab/hyperframes/f28/a/f28a.log` también aparece modificado y viene del estado previo. `lab/TOPE_TANDA.json` (1.50→1.00) y `lab/ESTADO_SESION.md` están dentro de lo pedido.

Riesgos que el contrato no cubre:
- Las iniciales siguen en el pool, la ficha y la escaleta. Si se regenera la narración o la voz desde ahí, vuelven a aparecer.
- El cortador sigue partiendo oraciones en puntos internos de una cita (ch03 [2]/[3]). Eso afecta pausas y sincronía de la voz.
- El papel regenerado cambió fichas que Omar ya había visto en F40, y sigue sin aprobar.

### Adenda de CC (después del veredicto; el texto de arriba queda tal cual)
- «ch03 pasó de 12 a 10 oraciones»: lo calculó el script de `diff_y_ch03.md` con `len(caps[ch03].oraciones)` de `01e_pantalla_f40.json` (12) y de `01e_pantalla.json` (10): las dos de más eran los cortes en «N.» e «I.» de las iniciales.
- Fila 6: este veredicto quedó pegado acá; `lab/hyperframes/f40/f40b/`, `lab/ESTADO_SESION.md` y `lab/TOPE_TANDA.json` entran en el commit siguiente, y después va el push.
