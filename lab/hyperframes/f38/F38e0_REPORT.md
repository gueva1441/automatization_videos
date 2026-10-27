# F38e-0 — Dos pruebas en seco: rótulos parafraseados y títulos de cap — REPORTE

Handoff `lab/hyperframes/f38/HANDOFF_F38e0_pruebas_en_seco.md` (md5 `ef89918b22b8bc1babdf96199f18e360`). Rama `f11-guion-v4`.
Commits: paso 0 `2819c09` · scripts, raws, tablas, reporte y ESTADO (este). **PARADA.** No se decide nada sobre los
resultados: comparan Omar y el analista. Las columnas «¿se entiende solo?» y «¿promete sin contar el final?» están vacías.

## Paso 0 (md5 comprobados, tal cual)
- `DECISIONES.md` `184831d263cdf4777e73dc071a60c245` (11:21 y 11:44).
- `PRUEBA1_prompt_rotulos.md` `240e3e7bf13656cb62f68b598393f41f`.
- `PRUEBA2_prompt_titulos.md` `e644cb0e7adfdd607ecba33a07f67205`.
- El handoff.
- `F38_REPORT.md` no entró: no estaba modificado, ya estaba en `7d91445`.
- Los archivos ajenos sin commitear (`diag_234_cap4.py`, `gfx_profiles/*`, `f28a.log`, las `ENTRADA_ANALISTA_*` y
  `VER_RENDER_v6.md`) no entraron.

## Cómo se corrió
- **Paralelo** (DECISIONES 01:23): un subagente por prueba, a la vez.
- **Pipeline sin tocar:** solo se importa.
- **Nada escrito en `data/` ni `output/`:** se midieron mtime y md5 antes y después en los dos casos. En `logs/`
  quedaron 2 archivos vacíos que crea el import de `error_handler` (abierto e11);
  `data/cost_history.json` sigue en `1f5e5ded…`.
  - A: neutralizó `cost_tracker._track` y el `FileHandler` que `error_handler` abre en `logs/` al importarse.
  - B: desvió `gemini_helpers._dump_invalid_json`, que nunca llegó a dispararse.
  - Las dos cosas se hicieron por monkeypatch dentro de los scripts de lab; no se editó ningún helper.
- **Gasto:** A US$ 0,3391 (una llamada a Sonnet: 66 440 tokens de entrada y 20 623 de salida). B US$ 0,0152 (tres
  llamadas a Flash). **Total US$ 0,3543**, tope 1,00.

## A — Prueba 1: rótulos (Sonnet 5.5 medium, una llamada)
- SYSTEM: el bloque «Prompt nuevo (m01e-6-prueba), entero» del md, extraído por código (md5 `7d2ccdd28055d6e621d1d251a0fe8bb7`, 3098 caracteres).
- USER: `_para_modelo(entrada)` + `FORMATO_SALIDA` con `"respaldo": "…", ` insertado una vez.
- Entrada reconstruida desde `f38/b2/fase1`: **idéntica** al `entrada` de `f38/b4/01e_pantalla.raw.json`.
- Archivos: `prueba1/prueba1_rotulos.py`, `prueba1.raw.json`, `TABLA.md`, `prueba1.log`.

## Prueba 1 — rótulos parafraseados (F38e-0 §A)

SYSTEM md5 `7d2ccdd28055d6e621d1d251a0fe8bb7` · modelo claude-sonnet-5-5 (medium) · una llamada.

| cap·beat | v6 hoy (etiqueta · dato · autor) | intento 1 de m01e-5 | NUEVO (etiqueta · dato · autor) | respaldo ✓/✗ | cifras | nombres | validar | car./caben | ¿se entiende solo? |
|---|---|---|---|---|---|---|---|---|---|
| ch01·1 | D84: PRESIÓN DE LA OLA DE AIRE · dos bombas de Hiroshima | D84: PRESIÓN DE LA OLA DE AIRE · dos bombas de Hiroshima | D195: LOS QUE VIVÍAN EN LONGARONE · Murieron 1.269 de 1.328 | ✓ · respaldo: «1.269 de 1.328 habitantes fallecidos» | 1.269 literal; 1.328 literal | — | queda | 50/90 |  |
| ch02·2 | D117: ACTA DEL CONSEJO SUPERIOR · solo 13 de 34 representantes presentes | D117: ACTA DEL CONSEJO SUPERIOR · solo 13 de 34 representantes presentes | D240: SESIÓN DE APROBACIÓN · Asistieron solo 13 de los 34 representantes | ✓ · respaldo: «asistieron solo 13 de los 34 representantes del Consejo Superior de Obras Públicas» | 13 literal; 34 literal | — | queda | 63/90 |  |
| ch02·3 | D47: FRENTE DEL DESMORONAMIENTO · 2 km de frente y 600 m de desarrollo vertical | D47: FRENTE DEL DESMORONAMIENTO · 2 km de frente y 600 m de desarrollo vertical | D47: TAMAÑO DEL DESMORONAMIENTO · 2 km de frente y 600 m de desarrollo vertical | ✓ · respaldo: «de 2 km de frente y 600 m de desarrollo vertical» | 2 literal; 600 literal | — | pregunta (spoiler: «2») | 71/83 |  |
| ch03·4 | T15: VOLUMEN DE LA ROCA · 3 millones de metros cúbicos | T15: VOLUMEN DE LA ROCA · 3 millones de metros cúbicos | T16: EL TRABAJADOR MUERTO · Arcangelo Tiziani | ✓ · respaldo: «mata a Arcangelo Tiziani» | — | Tiziani ✓ | queda | 37/83 |  |
| ch03·5 | D49: ANCHO DE LA FISURA · Más de 1 metro | D49: ANCHO DE LA FISURA · Más de 1 metro | D49: ANCHO DE LA FISURA · Más de 1 metro | ✓ · respaldo: «fisura de más de 1 metro de ancho» | 1 literal | — | queda | 32/90 |  |
| ch04·6 | T39: ROCA QUE AMENAZABA ERTO · 50 millones de metros cúbicos | T39: ROCA QUE AMENAZABA ERTO · 50 millones de metros cúbicos | — | — | — | — | — | — |  |
| ch04·7 | T50: COTA ALCANZADA · 720 metros | T50: COTA ALCANZADA · 720 metros | D106: SOBRE LA COTA SEGURA · 15 metros de más | ✓ · respaldo: «15 metros por encima de la cota de seguridad recomendada» | 15 literal | — | pregunta (contradice: «715») | 36/36 |  |
| ch05·8 | Q50: DOCUMENTO OFICIAL · en continua aprensión · Administración del comune di Erto e Casso | Q50: DOCUMENTO OFICIAL · «en continua aprensión» — Administración del comune di Erto e Casso | Q50: LO QUE DECÍAN · «en continua aprensión y en continua alarma» — Municipio de Erto y Casso | ✓ · respaldo: «en continua aprensión y en continua alarma» · cita literal ✗ (el dato trae «— autor»; sin él: ✓) | — | Municipio ✗, Erto ✗, Casso ✗ | corta (candado: la cita no es literal del texto fuente) | 130/90 |  |
| ch05·9 | Q51: ÚLTIMA LÍNEA DE LA POSDATA · Que Dios nos ayude · Alberico Biadene | Q51: ÚLTIMA LÍNEA DE LA POSDATA · «Que Dios nos ayude» — Alberico Biadene | Q51: LA ÚLTIMA LÍNEA · «Que Dios nos ayude» — Alberico Biadene | ✓ · respaldo: «Que Dios nos ayude.» · cita literal ✗ (el dato trae «— autor»; sin él: ✓) | — | Dios ✓, Alberico ✗, Biadene ✗ | corta (candado: la cita no es literal del texto fuente) | 74/90 |  |
| ch06·10 | D86: ALTURA DEL MURO DE AGUA · 70 metros | D86: ALTURA DEL MURO DE AGUA · 70 metros | D86: EL MURO DE AGUA EN LONGARONE · 70 metros de altura | ✓ · respaldo: «tenía una altura de 70 metros» | 70 literal | — | queda | 47/90 |  |
| ch06·11 | D128: RECUENTO OFICIAL · 1.910 personas | D128: RECUENTO OFICIAL · 1.910 personas | D128: TOTAL DE MUERTOS · 1.910 personas | ✓ · respaldo: «murieron 1.910 personas» | 1.910 literal | — | queda | 30/57 |  |
| ch07·12 | Q14: RESPUESTA · Y justicia tendréis · Giovanni Leone | Q14: RESPUESTA · «Y justicia tendréis» — Giovanni Leone | Q14: LA RESPUESTA · «Y justicia tendréis» — Giovanni Leone, presidente del Consejo | ✓ · respaldo: «Y justicia tendréis» · cita literal ✗ (el dato trae «— autor»; sin él: ✓) | — | Giovanni ✗, Leone ✗, Consejo ✗ | corta (candado: la cita no es literal del texto fuente) | 92/90 |  |
| ch07·13 | D245: CONDENA A MONTEDISON · 55.645.758.500 liras | D245: CONDENA A MONTEDISON · 55.645.758.500 liras | D245: CONDENA A MONTEDISON, 1997 · 55.645.758.500 liras | ✓ · respaldo: «En 1997, el Tribunal de Belluno condenó a Montedison a pagar al municipio de Longarone 55.645.758.500 liras» | 1997 literal; 55.645.758.500 literal | — | queda | 46/62 |  |

### Sellos y relojes (no se evalúan: solo que no se hayan roto)

| | v6 hoy | NUEVO (respuesta) | NUEVO (quedan tras validar) |
|---|---|---|---|
| sellos | 9 | 9 | 9 |
| relojes | 4 | 4 | 4 (sin error) |
| fichas | 13 | 12 | 9 |

Relojes v6: ch01[13] 9 OCT 1963, ch04[0] 4 NOV 1960, ch07[11] 20 FEB 1968, ch07[14] 29 NOV 1968
Relojes NUEVO: ch01[13] 9 OCT 1963, ch04[0] 4 NOV 1960, ch07[11] 20 FEB 1968, ch07[14] 29 NOV 1968
Sellos v6: ch01·1 INMINENTE, ch02·2 CALMA, ch02·3 AMENAZA, ch03·4 AVISO, ch03·5 SILENCIO, ch04·7 ALARMA, ch06·10 PÁNICO, ch07·12 RABIA, ch07·13 MEMORIA
Sellos NUEVO: ch01·1 PÁNICO, ch02·2 CALMA, ch02·3 AMENAZA, ch03·5 AVISO, ch05·8 INMINENTE, ch05·9 SILENCIO, ch06·10 COLAPSO, ch07·12 RABIA, ch07·13 MEMORIA

### Gasto

- llamada 1: in 66440 · out 20623 · US$ 0.3391 · 134.9 s · stop end_turn · JSON
- total US$ 0.3391 (claude_helpers.cost_of) · peor caso estimado antes US$ 0.2803

Notas de lectura: «car./caben» con `pantalla_colocar.caracteres` (en una cita, autor del archivo + 5); «cifras» con `voz_utils.numeros` sobre etiqueta y dato (una cifra seguida de «mil/millones» se escala para comparar); «redondeo» = no literal y con «más de» (menor) o «casi» (mayor) en el mismo campo; «nombres» con `voz_utils.nombres` (no ve nombres en texto todo en mayúsculas ni el que abre el campo). «autor (archivo)» = el formato no tiene campo autor: es el del archivo; «(modelo)» = el modelo agregó `autor` a la ficha; si el dato ya trae «— autor» (lo metió el modelo), no se repite. En esas citas «car.» cuenta el autor dos veces (el del dato y el del archivo, como lo mide `caracteres`) y «nombres» mira también el autor metido en el dato. Ninguna ficha nueva trajo un campo `autor` propio.

## B — Prueba 2: títulos de cap (Gemini 2.5 Flash, tres llamadas)
- Pedido: el bloque «Pedido nuevo, entero» del md, extraído por código, con `TITLE_MAX_WORDS` = 5 y `lines` como B.2 (md5 del pedido `85e8b649…`, 5178 caracteres).
- Llamada como `titles()`: `call_flash_json(…, response_schema=TITLES_SCHEMA)`.
- El pedido entero está en `prueba2/TABLA.md` y en `prueba2.raw.json`.

## F38e-0 · Prueba 2 — títulos de cap (Flash, en seco)

Escaleta: `data/scripts/_steps/f8s3-vajont/01a_escaleta.json` (solo lectura). Modelo: `gemini-2.5-flash` vía
`call_flash_json(pedido, response_schema=m01d_particion.TITLES_SCHEMA, description="prueba2: títulos")`, 3 llamadas con el mismo pedido.
Validación = la de `m01d_particion.titles()` (≤ 5 palabras, sin dígito, sin «?», tras `strip().strip('".«»')`), por llamada (1/2/3).
Cantidad de títulos por llamada (titles() exige 7): llamada 1: 7 títulos · llamada 2: 7 títulos · llamada 3: 7 títulos. US$ total: 0.015247.

| cap | hoy (de 01a_skeleton.json) | nuevo 1 | nuevo 2 | nuevo 3 | validación | ¿promete sin contar el final? |
|---|---|---|---|---|---|---|
| ch01 | Cama en la oscuridad | La Fuerza Oculta | La cama se mueve | La cama se mueve | 1✓ · 2✓ · 3✓ |  |
| ch02 | El muro que tapa | La Montaña Advierte | La montaña se mueve | Vivir bajo la obra | 1✓ · 2✓ · 3✓ |  |
| ch03 | La costura abierta | Grietas Y Verdades | El agua responde | La montaña habla | 1✓ · 2✓ · 3✓ |  |
| ch04 | La ola de juguete | La Verdad Incomoda | Contra quien avisa | Culpar al mensajero | 1✓ · 2✓ · 3✓ |  |
| ch05 | Piedras rodando | La Última Advertencia | El último aviso | El riesgo inminente | 1✓ · 2✓ · 3✓ |  |
| ch06 | El gran rugido | La Noche Eterna | La noche del desastre | Cuatro minutos eternos | 1✓ · 2✓ · 3✓ |  |
| ch07 | Diarios y verdades | La Verdad Olvidada | Buscando la verdad | Buscar responsables | 1✓ · 2✓ · 3✓ |  |


## Lo que queda abierto (entero)
- e1. **Las tres citas de la prueba 1 caen por el candado** (Q50, Q51, Q14).
  - Causa: el modelo mete «— autor» dentro de `texto`, porque el formato no tiene campo `autor` y el prompt nuevo pide
    «el autor va en español».
  - Sin ese agregado, las tres frases son literales del archivo.
  - Por lo mismo, «car.» de las citas cuenta el autor dos veces y «nombres» sale ✗ por el autor del dato.
  - Pasó igual en el intento 1 de m01e-5 (F38d, d1).
- e2. **Lo que deja la validación de hoy en la prueba 1** (`final=False`):
  - quedan 9 fichas, cortan 3 y quedan 2 preguntas: D47 spoiler «2»; D106 contradice «715»;
  - picos vacíos ch05·8 y ch07·12;
  - `a_pantalla` faltantes ch02·2 (usó D240 en vez de D117, y descartó D117 como «repetido») y ch05·8;
  - «vuelven» T15, T21, T39, Q15 y T85;
  - ch04·6 sin ficha.
  - Es una sola llamada, sin vueltas, a propósito: se compara contra el intento 1 de m01e-5, no contra el papel final.
- e3. **Ninguna cifra salió «redondeo» ni «no está»:** todas son literales. El margen de redondeo de DECISIONES 11:44
  queda sin medir en esta corrida.
- e4. **`OUT_TOKENS_PEOR` (16 000) subestima la salida real:** 20 623 en la prueba 1; 17 239 en F38d b4. El peor caso fue
  US$ 0,28 y el real 0,34.
- e5. **El USER de la prueba 1 se armó con `ensure_ascii=False`,** como `m01e.pedido()`, para que el body sea igual al de
  `autor()`. El handoff escribe `json.dumps(...)` a secas, que mandaría los acentos escapados.
- e6. **Elecciones propias de la verificación A.5** (anotadas al pie de la tabla):
  - una cifra seguida de «mil/millones» se escala para comparar;
  - «más de» o «casi» se buscan en todo el campo;
  - `nombres()` no ve nombres en mayúsculas ni el que abre el campo.
  - En esta corrida ninguna cambió un resultado.
- e7. **Prueba 2, ningún beat de la escaleta tiene campo `pico`:** el pico está en `esc.pico.beat` = 10. Se siguió la
  letra del handoff y del md (`b.get("pico")`), así que « · pico» no aparece en ninguna línea. El beat 10 igual dice
  «beat 10 pico:» por su `funcion`.
- e8. **Prueba 2, lo que la validación de hoy no ve:**
  - la llamada 1 sale en Title Case y con «Incomoda» sin tilde;
  - la llamada 3 da «Cuatro minutos eternos» (cifra en letras: pasa el código);
  - hay variación alta entre las tres llamadas y títulos genéricos que se repiten («La Verdad…» ×3 en la 1).
  - Los 21 títulos pasan la validación de `titles()`, que está copiada en el script porque no se puede importar.
- e9. **`prueba1.log` acumula tres corridas:** la en seco, la llamada y un rehacer de la tabla sin gasto. El raw guarda la
  respuesta original sin tocar.
- e11. **Quedaron 2 logs vacíos en `logs/`** (`pipeline_20261027_114953.log` y `…115155.log`). Los crea el import de
  `error_handler` al cargar `cost_tracker`; la prueba 1 los creyó neutralizados y no lo estaban del todo. Están
  ignorados por git, tienen 0 bytes y no se borraron. Lo encontró el revisor (fila 6).
- e10. **Fuera de esta tanda, siguen:** la tarjeta del segundo 0 a quitar (DECISIONES 11:21); F38e (B1–B5, r1, R8); los
  abiertos de F38d y del render v6.

## Veredicto del revisor (`revisor-handoff`, íntegro)
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Paso 0: md5 y commit tal cual | OK | El commit 2819c09 existe. El handoff da md5 `ef89918b…`, que coincide con mi `md5sum`. Los md5 de DECISIONES y de los dos prompts no los recalculé; los tomé del mensaje del commit y del reporte. |
| 2 | SYSTEM de la prueba 1 igual al bloque del md | OK | Extraje las líneas 10-25 de `PRUEBA1_prompt_rotulos.md`. Son idénticas, byte a byte, al `system` guardado en `prueba1.raw.json`. El md5 es `7d2ccdd28055d6e621d1d251a0fe8bb7`. |
| 3 | Pedido de la prueba 2 igual al bloque del md, con `{TITLE_MAX_WORDS}`=5 y `{lines}` reemplazados | OK | El prefijo y el sufijo del bloque del md, con 5 sustituido, coinciden con el `pedido` del raw. El md5 es `85e8b649fcac2ba25d9fbf987e282025`. |
| 4 | Pipeline sin tocar | OK | `git status` y `git diff --stat 2819c09` sobre `script_engine`, `tests`, `gemini_helpers.py`, `claude_helpers.py` y `config.py` no muestran nada. Solo cambian `gfx_profiles/*` y `diag_234_cap4.py`, que ya estaban modificados antes de la tanda. |
| 5 | Nada en `data/` ni `output/` | OK | `find data output -newermt '2026-10-27 11:30'` no devuelve nada. `cost_history.json` mantiene su md5 `1f5e5ded…` antes y después, según los logs y `data_escrituras` del raw. |
| 6 | Nada en `logs/` (afirmado en el reporte) | PARCIAL | Aparecieron dos archivos de 0 bytes: `logs/pipeline_20261027_114953.log` y `…115155.log`. Los creó el import de `error_handler` durante las corridas. El reporte dice «nada escrito en logs/» y `prueba1.log` dice «cambiados/nuevos: ninguno», pero eso es falso para estos dos. Están ignorados por git y vacíos. Esto no está en el abierto. |
| 7 | Gasto | OK | A: 0,33911, una llamada. B: 0,015247, tres llamadas, y la suma de las tres da 0,015246. Total 0,3543 contra el tope de 1,00. El reporte coincide. |
| 8 | Columnas «¿se entiende solo?» y «¿promete…?» vacías | OK | Están vacías en las 13 filas de `prueba1/TABLA.md` y en las 7 de `prueba2/TABLA.md`, y también en el reporte. |
| 9 | Tablas del reporte iguales a los TABLA.md | OK | Las 13 filas de la prueba 1 y las 7 de la prueba 2 aparecen textuales en `F38e0_REPORT.md`. |
| 10 | El reporte no decide sobre los resultados | OK | Dice «No se decide nada». El abierto e1-e10 solo describe hechos. |
| 11 | Reporte con abierto entero, md5 del paso 0 y US$ total | OK | `F38e0_REPORT.md` existe (13701 bytes). |
| 12 | Veredicto del revisor dentro del reporte | PENDIENTE | El reporte termina en «(se pega abajo)». Falta pegar este veredicto. |
| 13 | Tres llamadas en la prueba 2, validación de hoy y pedido entero | OK | `llamadas` tiene 3 elementos. Los 21 títulos pasan la validación. El pedido completo está en `TABLA.md`. |
| 14 | Subagentes en paralelo, uno por prueba | NO VERIFICABLE | Solo se ve que el `.py` de la prueba 2 se escribió a las 11:51 y el de la prueba 1 a las 11:56. Para confirmar el paralelismo haría falta el registro de ejecución. |
| 15 | ESTADO y commit final | PENDIENTE | Ambos se hacen después de este veredicto, como dijiste. |

Fuera de alcance: ninguno atribuible a la tanda. Las escrituras son `prueba1/`, `prueba2/` y `F38e0_REPORT.md`, más los dos logs vacíos de la fila 6. Los `ENTRADA_ANALISTA_*` y `VER_RENDER_v6.md` son untracked ajenos y no deben entrar al commit.

Desviaciones declaradas en el reporte (e5, e7): `ensure_ascii=False` en el USER de la prueba 1, y ningún beat con `pico`. Ninguna cambia el cumplimiento.

Riesgos que el contrato no cubre:
- La corrida de la prueba 1 siempre deja logs vacíos en `logs/`. El candado «nada en logs» no está en el handoff, pero el reporte lo afirma. Conviene corregir esa frase o agregarla al abierto.
- El reporte no identifica los `.py` ajenos untracked de la raíz. El commit final debe agregar solo los archivos de la tanda.

### Adenda de CC (después del veredicto; el texto de arriba queda tal cual)
- Fila 6: la frase del reporte se corrigió («nada en `data/` ni `output/`; en `logs/` quedaron 2 archivos vacíos…») y el hecho pasó al abierto como e11. Los dos logs no se borraron: están ignorados por git y vacíos, y no son de la tanda borrarlos.
- Filas 12 y 15: el veredicto quedó pegado acá. ESTADO y el reporte van en el mismo commit, que agrega por ruta explícita solo `prueba1/`, `prueba2/`, `F38e0_REPORT.md` y `lab/ESTADO_SESION.md`; no entran los archivos ajenos.
