# F22_REPORT — familias C + E: ejemplos de un caso inventado, antagonista persona / institución / ninguno, nombre como lo escribe el documento

2026-10-24 · rama `f11-guion-v4` (base `8be0ea9`) · handoff `HANDOFF_F22_ejemplos_y_antagonista.md` (md5 `2685deecf8e8516d6cc8ee2c61b47384`, verificado) · **US$ 1.4672 de 3.00** · sin merge · **PARADA**.

## 0. En corto
- Los cuatro prompts quedaron **literales** (md5 del bloque `## SISTEMA` = md5 en código, los cuatro); los viejos siguen en código con su versión, byte-idénticos. La escaleta v1 (sin ficha) y las tareas de escaleta y guion: byte-idénticas a `8be0ea9`.
- **Ycuá** (columna v1.1 → escaleta v2.1 → guion v5.2): **0 bloqueantes**, humano Liz Torres, antagonista Juan Pío Paiva (persona) en columna y escaleta. Pero el guion sale **más corto: 838 palabras ≈ 6.8 min** contra 1,384 ≈ 11.3 min del guion de F16 (13 personas con nombre contra 24). No se corrige nada.
- **Kyshtym** llega por primera vez al guion (ficha nueva → columna → escaleta → guion): ficha con 9 instituciones en `personas` (Средмаш / Ministerio de Construcción de Maquinaria Mediana, la comisión, «autoridades soviéticas»…), columna en 1 intento, escaleta en la regeneración. El antagonista elegido **no es institución sino «ninguno»** (columna y escaleta coinciden: la ficha no dice quién decidió ignorar las fallas de refrigeración). Guion 1,003 palabras ≈ 8.2 min con **1 bloqueante → PARADA** (crudo guardado, sin parche): (a) «1982», el año del estudio *An Analysis of the Alleged Kyshtym Disaster*, que está en el campo `fuente` de D96/Q08 (lo ve el guionista) pero no en el texto que lee el juez de cifras.
- **Cero Cardal** en las 7 salidas (ficha, columnas, escaletas, narraciones) y ningún id «##» copiado.
- Suite amplia **795 verdes + las 5 previas** (743 + 52 de `test_module_f22.py`). Dorado v3: cambia solo por los cinco mensajes de feedback que pide el handoff (probado: con esos textos vueltos atrás da el hash de F21).
- Desvíos y hallazgos, en §6.

## 1. md5 y diff de los prompts
Los md5 de los seis archivos de `lab/hyperframes/f22/` coinciden con el §6 del handoff (verificados antes de empezar y en el test `test_md5_de_los_archivos_del_handoff`). El diff completo, línea a línea (cada línea de un prompt es un párrafo), está abajo en el anexo A (= `PROMPTS_f22_diff.md`, generado por `f22_diffs.py`).

| prompt | md5 del bloque `## SISTEMA` del archivo | md5 en código | viejo (sigue en código, con su versión) |
|---|---|---|---|
| ficha v2.1 | `7d3599dc6e4123a3bb883fc15a541e71` | `7d3599dc6e4123a3bb883fc15a541e71` | `2e151732…` = `system("f15-1")` |
| columna v1.1 | `f294cf6b1220983903ce339f5b21cb27` | `f294cf6b1220983903ce339f5b21cb27` | `1408569c…` = `SYSTEM_F17_1` |
| escaleta v2.1 | `7ea18a6aa1ca91c5ad0dfb7cc9b239a8` | `7ea18a6aa1ca91c5ad0dfb7cc9b239a8` | `49ed74d9…` = `SYSTEM_V2_F16_1` |
| guion v5.2 | `743e4f0a7ff9e58d86762bbd43679952` | `743e4f0a7ff9e58d86762bbd43679952` | `cdce609a…` = `system("f15b-1")` |

**Lo que el diff muestra fuera de lo que cada archivo declara en «Qué cambia»** (pegado literal igual; lo marco para que el analista confirme):
1. **Ficha:** entra «Si «texto» no está en español, «traduccion» lleva la cita en español.» al final del ítem `citas`. El archivo declara tres cambios (ejemplos, paréntesis, instituciones); esta frase no está entre ellos (en código, desde F19, `traduccion` estaba solo en la descripción del esquema).
2. **Guion:** el archivo dice «dos ítems de `<errores>`»; cambian **cuatro** (explicar lo obvio: sale «presos»; juicio disfrazado de pregunta; telegrama; gancho abstracto).
3. **Guion:** la regla 6 de `<estructura>` no solo cambia el ejemplo: suma «se dice por su rol» («…va sin el nombre de quien lo dijo: se dice por su rol («un mecánico contó»…»).
4. Los md5 «viejos» que citan los archivos (ficha 1fdbd0b9…, columna 0e649094…, escaleta 8d573288…, guion 6dcc4294…) no son los de los bloques en código (2e151732 / 1408569c / 49ed74d9 / cdce609a); parecen ser md5 de los archivos `.md` enteros. El diff se hizo contra lo que estaba en código.
El resto del diff es lo declarado: ejemplos de Orleans/Ycuá → Puerto Cardal con `D##/Q##/T##/E#`, paréntesis de Orleans/Ycuá → genéricos, instituciones en `personas` (ficha), QUIÉN DECIDE (columna: `<que_es>`, `<oficio>` 3 nuevo y renumerado, ejemplo, `<errores>` sin «90 personas» y con «inventar un culpable»), la línea del antagonista en `<que_es_una_escaleta>` (escaleta) y la tarea de la columna (QUIÉN DECIDE + `antagonista` en el JSON).

## 2. Código (qué cambió y dónde)

### 2.1 Los cuatro prompts (C) — literales desde «## SISTEMA»
- Extracción: desde «\n## SISTEMA\n\n» hasta el primer «\n\n---\n» (el mismo anclaje de F15–F17; con los archivos viejos da los md5 que ya estaban en código). Los cuatro bloques en código = los del handoff (tabla en `PROMPTS_f22_diff.md`, test `test_los_cuatro_sistemas_byte_identicos_al_handoff`).
- **Cómo quedaron los viejos** (para no romper los tests de byte-identidad sin motivo): como constantes con nombre de versión, en el mismo módulo, byte-idénticas y fuera del camino por defecto:
  - `ficha_caso.SYSTEM_F15_1` (`system("f15-1")`) · nuevo `SYSTEM_F22_1` = `system()`; `PROMPT_VERSION = "f22-1"`, `PROMPT_VERSION_F15 = "f15-1"`.
  - `m01a_columna.SYSTEM_F17_1` / `TAREA_F17_1` (`PROMPT_VERSION_F17`) · nuevos `SYSTEM` / `TAREA` (la tarea del bloque USUARIO del archivo, literal: trae QUIÉN DECIDE y `antagonista`); `PROMPT_VERSION = "f22-1"`.
  - `m01a_escaleta.SYSTEM_V2_F16_1` (`PROMPT_VERSION_V2_F16`) · nuevo `SYSTEM_V2`; `PROMPT_VERSION_V2 = "f22-1"` y también `PROMPT_VERSION_COLUMNA = "f22-1"` (con ficha, con o sin columna, es la v2.1; `PROMPT_VERSION_COLUMNA_F17` queda). `TAREA_V2` y `TAREA_COLUMNA` sin cambios (md5 = 8be0ea9). **La v1 (sin ficha) byte-idéntica**: SYSTEM, FEWSHOT, RULES, SCHEMA y el usuario con y sin feedback dan los mismos md5 que el módulo de 8be0ea9 (`test_escaleta_v1_byte_identica`).
  - `guion_v4.SYSTEM_V5_2` = `system()` (`PROMPT_VERSION = "f22-1"`); el v5.1 sigue con `system("f15b-1")` (`PROMPT_VERSION_V5_1`), el v5 con `"f15-1"`; `VERSIONES_V5` = las tres (mismo usuario v5; `TAREA_V5` sin cambios).
  - Los tests viejos (f14, f15, f15b, f16, f17, f21) apuntan a esas constantes (mismo md5 que antes); los que miden la versión del camino por defecto usan la constante nueva.
- **Research** (`research_v3.py`): R3 regla 6 «un preso de Templeman III» → «la descripción que da el texto (por ejemplo, el rol: «una vecina», «un operario»)»; los tres ejemplos JSON `"anio":2006,"idioma":"en"|"it"` → `"anio":0,"idioma":"xx"`; `seed_vocabulario` con los ejemplos de tres tipos de caso en una línea; `seed_profile` «inglés (Nueva Orleans, EE. UU.)» → «el idioma del lugar del caso».
- **Mensajes de feedback al modelo**:
  - `m05_narrative`: «Interestatal 10» → «una ruta 10»; «(cómo era el agua, la celda, el calor)» → «(cómo era el lugar, la luz, el frío o el calor)»; ««sheriff Marlin N. Gusman» basta una vez; después «el sheriff», «Gusman»» → «el nombre completo con el cargo basta una vez; después, el cargo o el apellido solo».
  - `guion_v3_reglas`: fechas «ese domingo» → «ese día»; el ancla modelo del gancho se arma con el lugar y el año del seed actual (`research_v3.caso()`, que guarda `lugar_principal`/`anio_evento` del perfil en `set_vocabulario`): con perfil, ««Asunción, 2004.»»; sin perfil, sin ejemplo. «ciudad» → «lugar» en ese mensaje (Mayak no es una ciudad).
  - Los prompts v1 de la escaleta y el v3 del guionista (`m01b_guionista`, dorado v3) no se tocan. Los docstrings/comentarios con Orleans (familia J) tampoco.

### 2.2 Antagonista persona / institución / ninguno (E)
- Contrato: `{"tipo": persona|institucion|ninguno, "id" (persona), "nombre", "por_que"}` (+ `ids` en la columna).
- **Columna**: esquema con `antagonista` (requerido). `chequeo` suma `antagonista_problemas`: persona → `persona_de` en la ficha; institución → `institucion_de_la_ficha`; ninguno → `por_que` no vacío. Una regeneración si falla, como hoy. `to_markdown` y `section` (lo que lee la escaleta) con la línea `QUIÉN DECIDE: …` entre HUMANO y PICO (forma del ejemplo); una columna de F17 sin antagonista se lee igual.
- **`institucion_de_la_ficha`** (una sola, en `m01a_columna`; la escaleta la usa): nombre = nombre o variante de una entrada de `personas` de la ficha (sin el artículo en los dos lados), o literal en ≥ 2 hechos. 
- **Escaleta v2.1**: `SCHEMA_FICHA.antagonista.tipo` con `ninguno` y `por_que` requerido; `validate` (solo con ficha): `ninguno` sin `por_que` → bloqueante (mismo bloqueante «antagonista»; el patrón suma ese mensaje); `ids_v2` no lee P## de institución ni de ninguno. Con institución, al pasar, la escaleta copia las `variantes` de la ficha a `antagonista.variantes` (lectura, no chequeo) para que partición y guion la busquen con todas sus formas. Métricas nuevas (informativas): `antagonista_tipo`, `antagonista_caps` y, con columna, `antagonista_es_el_de_la_columna`.
- **`m01d_particion`**: la institución queda en `personajes` con `tipo: "institucion"`, su nombre, variantes y `entra_en_cap`; la persona como siempre (sin campo `tipo` = persona: agregarlo cambiaba el dorado v3 sin motivo). `entra_en_cap` con `nombres.nombra` (persona) / `nombres.menciona` (institución). Ninguno → no hay entrada.
- **`guion_v3_reglas.antagonist_problems`** (que contiene `_ANON_VOICE`): solo con `tipo == "persona"` (sin `tipo` = persona: Orleans/Gusman como antes). `antagonista_caps` (métrica): caps donde la voz lo nombra. `guion_v4.metricas` suma `antagonista_tipo` y `antagonista_caps`. `mark()`/`data_line`/`_is_human` sin cambios.
- **`m05_narrative`**: el aviso «nombrá a X por nombre y apellido» saltea la entrada `tipo: institucion` de `personajes` (consecuencia de que m01d ya no la borra; sin esto le pediría nombre y apellido a un ministerio).
- **Ficha**: el chequeo de hoy **no** aplica `es_persona` ni «nombrada en sus ids» a `personas` (lo de «nombrada» existe solo para `personas_descartadas`). No hay nada que eximir; agregar «nombrada en sus ids» a `personas` sería un chequeo nuevo, y no lo agregué. Test: una institución en `personas` pasa el chequeo.

### 2.3 El nombre como lo escribe el documento
- R3: `citas[].autor_en_documento` y `personajes[].nombre_en_documento` en el esquema y una línea en las reglas 6 y 7 (texto del handoff). `validate_doc_items` los guarda; «el apellido está en el documento» acepta `nombre_en_documento`. El merge acumula las formas de cada documento (`nombre_en_documentos`, `autor_en_documentos`); `research_v3.en_documento(it, campo)` las lee (un pool viejo: []).
- `verify_pool`: el autor cerca de la cita por su apellido **o** cualquier parte de `autor_en_documento`, con `nombres.menciona`.
- `presence_v3` / `person_stats` / `_names_in`: `name_terms` suma «nombre apellido» y el apellido del nombre en el documento (no el nombre de pila solo, que matchearía de más).
- El pool de Kyshtym no tiene el campo (no se rehace el research).

## 3. Corridas (§2)
Runner `f22_corridas.py` (freno antes de cada llamada de Sol por paso, por tema y total; una sola facturación por llamada; perfil del seed cargado con `fase1_5.cargar_perfil`). Página `compara_f22.html` (`f22_compara.py`, sin API; probada a 375 px sin scroll horizontal) y `resumen_f22.json`. `topics_db` no se tocó: el topic se arma en memoria con el pool de `_steps`.

### 3.1 Ycuá (`f8s1-ycua-bolanos`) — desde la ficha v2 de F15b (no se rehízo)
Control: con el topic que arma el runner, el usuario de la escaleta v2 sin columna da el md5 de F16 (`2d77969a…`), así que el pool es el mismo.
- **Columna v1.1** (1 intento, 0 problemas, US$ 0.092): humano **Liz Torres**; **QUIÉN DECIDE: Juan Pío Paiva (persona)** — «Digna Cáceres le atribuye la orden de cerrar; el dueño fue condenado a doce años… no reconstruimos como comprobada una orden que la defensa niega»; pico cap 5; 7 personas con nombre (F17 con las notas de Omar: 6). Corrí **sin** las notas de Omar de F17 (`columna_notas.md`): el handoff pide columna v1.1 a secas.
- **Escaleta v2.1**: pase 1 cortado por mi freno (§6.1); pase 2 = intento 1 con 8 bloqueantes (un `P13, P80` como dato central; 7 ids de `a_pantalla` también en beats) → **intento 2: 0**. 14 beats, humano = columna, antagonista = columna (persona, Paiva), pico beat 9, escenas 6, 7, 8, 9, 10, 12.
- **Guion v5.2**: **0 bloqueantes**, 21 párrafos, cierre en pregunta, citas 7 (F16: 9). `nota_b` = None (perfil cargado).

Tabla F16 → F22 (antes = la última cadena completa de Ycuá: escaleta v2 y guion v5.1 de F16; F17 solo llegó a la columna. Personas = las de la ficha con nombre de persona que la voz nombra, sin mononimios):

| | antes | F22 |
|---|---|---|
| humano (columna · escaleta) | Liz Torres · Liz Torres | Liz Torres · Liz Torres |
| antagonista | P06 (persona; F16 no tenía `tipo`) | Juan Pío Paiva (persona) |
| caps donde la voz nombra al antagonista | 7 | 7 |
| palabras · minutos | 1,384 · 11.3 | **838 · 6.8** |
| bloqueantes del guion | 0 | 0 |
| personas con nombre en el guion | 24 | 13 |
| citas | 9 | 7 |
| escenas de la ficha usadas | 2, 3, 5, 7, 8, 9, 10, 12 | 6, 7, 8, 9, 10, 12 |

Por cap (F16 → F22):

| cap | palabras F16→F22 | personas con nombre F16 → F22 | citas | bloqueantes | escenas |
|---|---|---|---|---|---|
| 1 | 94 → 82 | 1 (Liz Torres) → 1 (Liz Torres) | 1 → 1 | 0 → 0 | [8] → [8] |
| 2 | 129 → 88 | 4 (Alfredo Vallovera, Blas Cristaldo, Teresa Urbieta, Ángela Pujol) → 2 (Alfredo Vallovera, Benedicto Pérez) | 1 → 0 | 0 → 0 | [2, 3] → — |
| 3 | 295 → 112 | 7 (Beatriz González, Benedicto Pérez, Carlos Halke, Cristian Sosa, Enrique Riera, Martín Burt, Víctor Galeano) → 1 (Beatriz González) | 2 → 1 | 0 → 0 | [5] → [6] |
| 4 | 177 → 102 | 4 (Alejandro Nissen, Digna Felicia Cáceres, Tatiana Gabaglio, Víctor Galeano) → 2 (Digna Felicia Cáceres, Víctor Galeano) | 1 → 1 | 0 → 0 | [7, 9] → [7] |
| 5 | 46 → 107 | 0 (—) → 1 (Tatiana Gabaglio) | 1 → 2 | 0 → 0 | [8] → [8, 9] |
| 6 | 340 → 143 | 6 (Cristian Sosa, Juan Pío Helvidio Paiva Escobar, Luis Escobar Faella, Nelson Astigarraga, Rubén Urbieta, Víctor Galeano) → 1 (Nelson Astigarraga) | 0 → 0 | 0 → 0 | [10, 12] → [9, 10, 12] |
| 7 | 303 → 204 | 8 (Daniel Areco, Digna Felicia Cáceres, Edgar Sánchez, Ismael Alcaraz, Juan Pío Helvidio Paiva Escobar, Luis Escobar Faella, María Estela Morínigo Giménez de Palacios, Teresa Sosa) → 5 (Antonio Morínigo, Daniel Areco, Juan Pío Helvidio Paiva Escobar, Luis Escobar Faella, Víctor Daniel Paiva) | 3 → 2 | 0 → 0 | — → — |

Lectura: la cadena nueva no rompe nada (0 bloqueantes, mismo humano y mismo pico de la ficha, Cardal en cero), pero el guion pierde casi el 40 % del largo: todos los caps salvo el 5 son más cortos (el 3 baja de 295 a 112 y el 6 de 340 a 143) y entran la mitad de las personas. No sé si viene del guion v5.2 o de la escaleta nueva (14 beats contra los de F16): no lo separé, porque separarlo es otra llamada fuera del pedido. Va para el analista.

### 3.2 Kyshtym (`f18-kyshtym-mayak`) — ficha nueva
- **Pool** (etapa `pool`, sin API): los pasos deterministas de `recheck.paso_pool` de F21 sobre el pool de F20 en disco, con el código de hoy → compuerta **verde** (208 datos / 18 citas verificadas / **7 elegibles** / 22 eventos), Osetrov, Komarov, Serov y Ladeyshchikova como personas (los tres primeros con citas parciales: el pool no tiene `autor_en_documento`). Guardado como `00_pool_v3.json` (el de F20 en `00_pool_v3_f20.json`); resumen en `pool_kyshtym_f22.json`. **Hallazgo:** quedan **dos `P09`** (§6.4).
- **Ficha v2.1** (US$ 0.413, 486 s): crudo → final: 36 personas, 4 candidatos (Kutepova 1 cita verificada, **Komarov 0**, Medvedev 1, Tumerman 1), 6 giros, 11 escenas (13 en el crudo), 74 hechos, 33 cifras, 20 citas, 15 decisiones, 8 versiones, 3 contradicciones; 23 ítems sacados por el chequeo (15 de ellos `personas_descartadas` que no están entre los descartados del pool: varios ya son personajes del pool de F21c, como Kamynin y Talevlin). **Instituciones en `personas`**: Ministerio de Construcción de Maquinaria Mediana de la URSS (Средмаш, МСМ), Comisión presidida por Slavski, autoridades soviéticas, Tribunal Supremo, Ministerio de Desarrollo Social, más dos colectivos y una jueza sin nombre. (Mayak no aparece como entrada propia.)
- **Columna v1.1** (1 intento, 0 problemas, US$ 0.089): humano **V. I. Komarov** (su cita es parcial; la columna lo dice); **QUIÉN DECIDE: ninguno** — «La ficha describe deficiencias desatendidas y una refrigeración sin reparar, pero no identifica quién decidió ignorarlas. Sí atribuye el silencio público inicial a las autoridades soviéticas: esa responsabilidad se cuenta por separado.» Pico cap 5 (la explosión). 6 personas con nombre. La columna, tal cual, está en `COLUMNA_kyshtym.md` y arriba de la sección de Kyshtym en `compara_f22.html`.
- **Escaleta v2.1** (US$ 0.247): intento 1, 4 bloqueantes (Q17 en dos beats; 3 ids de `a_pantalla` en beats) → **intento 2: 0**. 14 beats, humano = columna, antagonista **ninguno** = columna, pico beat 7, 8 escenas.
- **Guion v5.2** (US$ 0.118): 1,003 palabras ≈ 8.2 min, 20 párrafos, cierre en pregunta, 6 citas, humano en caps 1, 2, 3, 5, 7. **1 bloqueante → PARADA** (crudo en `guion_kyshtym_f22.json`, `NARRACION_kyshtym_f22.md`; no se parcheó):
  - (a) cap 7, beat 13: «En 1982, los autores de An Analysis of the Alleged Kyshtym Disaster expresan su completo desacuerdo…» → «cifra que no está en el research: 1982». El 1982 está en `fuente` de D96 y Q08 («An Analysis of the Alleged Kyshtym Disaster, 1982»), que el guionista recibe; `invented_numbers` no lee `fuente`. Es un choque entre lo que se le muestra al modelo y lo que mira el juez, no un dato inventado. Decide el analista.

| cap | palabras | personas con nombre | citas | bloqueantes | escenas |
|---|---|---|---|---|---|
| 1 | 87 | V. I. Komarov | 0 | 0 | [4] |
| 2 | 75 | V. I. Komarov | 0 | 0 | — |
| 3 | 143 | Lyubov Ladeyshchikova, V. I. Komarov | 1 | 0 | [1] |
| 4 | 113 | — | 0 | 0 | [2] |
| 5 | 149 | V. I. Komarov | 2 | 0 | [3, 5] |
| 6 | 129 | — | 0 | 0 | [7, 9] |
| 7 | 295 | Lev Tumerman, Nadezhda Kutepova, Planeta de las Esperanzas, V. I. Komarov, Zhores Medvedev | 3 | 1 | [10] |

(«Planeta de las Esperanzas», la ONG de Kutepova, pasa `es_persona` por su forma: es un falso positivo de la métrica.)

## 4. «Cero Cardal» (§3)
`cero_cardal.py`: palabras enteras Cardal, Soto, Bascuñán, Quiroga, Marín, Alborada, «Faros y Balizas»; «querosén» y «telegrama» con cualquier terminación. Control: 0 en Orleans F7c-3 (escaleta y narración v3r3) y en Ycuá (columna F17, escaleta y narración F16); el caso ejemplo da 8 de las 9.

| salida | coincidencias |
|---|---|
| FICHA_kyshtym.md | 0 |
| COLUMNA_ycua.md · COLUMNA_kyshtym.md | 0 · 0 |
| ESCALETA_ycua.md · ESCALETA_kyshtym.md | 0 · 0 |
| NARRACION_ycua_f22.md · NARRACION_kyshtym_f22.md | 0 · 0 |

Ningún id del ejemplo («D##», «Q##», «T##», «E#») en salidas ni crudos (solo en los `prompt_*.txt`, que llevan el sistema).

## 5. Costo por paso
| tema | paso | llamadas | US$ |
|---|---|---|---|
| Ycuá | columna | 1 | 0.0916 |
| Ycuá | escaleta, pase 1 (cortado por el freno) | 1 | 0.1340 |
| Ycuá | escaleta, pase 2 | 2 | 0.2690 |
| Ycuá | guion | 1 | 0.1057 |
| **Ycuá** | | | **0.6003** de 1.00 |
| Kyshtym | ficha | 1 | 0.4132 |
| Kyshtym | columna | 1 | 0.0891 |
| Kyshtym | escaleta | 2 | 0.2467 |
| Kyshtym | guion | 1 | 0.1179 |
| **Kyshtym** | | | **0.8669** de 2.00 |
| **total** | | | **1.4672** de 3.00 |

## 6. Desvíos, decisiones mías y hallazgos
1. **Freno de paso mal dimensionado (mío).** El pase 1 de la escaleta de Ycuá se cortó antes de la regeneración porque puse 0.45 al paso con `max_completion_tokens` 30 000 (peor caso 0.34 por llamada). No fue un límite del handoff. Bajé la salida a la de F18 (escaleta 20 000, guion 24 000), subí el paso a 0.65 (contando lo gastado) y rehice la escaleta entera: el pase 1 (US$ 0.134) queda gastado y guardado (`escaleta_crudos_ycua_pase1.json`, `run_ycua_pase1.log`).
2. **Test literal de §1.3 («Осетров» → verificada) no pasa con `nombres.menciona`.** Junto a la cita Q16 el documento F13 dice «В.М. Осетрова» (genitivo); «Осетров» está a 658 caracteres, fuera de la ventana de 400. Con `autor_en_documento: "В.М. Осетрова"` (como lo escribe el texto junto a la cita) → verificada; con «Осетров» → parcial. Komarov igual («В.И. Комарова»); Serov («Серов») verificada con las dos formas. No agregué tolerancia a la declinación (sería una regla nueva de nombres); los tests documentan los dos casos. Para F23: o el modelo devuelve la forma de junto a la cita, o `nombres` aprende flexión.
3. **Ficha: «sin `es_persona` pero nombrada en sus ids».** El chequeo de hoy no aplica `es_persona` ni «nombrada en sus ids» a `personas` (solo a `personas_descartadas`). No había nada que eximir, y agregar «nombrada» sería un chequeo nuevo: no lo agregué. Test: una institución en `personas` pasa.
4. **Dos `P09` en el pool de Kyshtym (bug previo, no tocado).** `add_quote_authors` numera con `len(personajes) + 1`; como en el pool de F20 falta P05, el nuevo autor (Андрей Талевлин) toma P09, que ya era Komsomolskaya Pravda. `ev.items` se queda con el último. Pasa igual en el recheck de F21c. Va como seguimiento.
5. **El antagonista de Kyshtym salió «ninguno»**, no institución. Lo decidió el modelo en columna y escaleta, con la razón citada arriba. El contrato lo permite; el esperado del handoff era institución.
6. **Ycuá sin las notas de Omar** en la columna (§3.1).
7. **`m05`:** el aviso «nombrá a X por nombre y apellido» saltea la institución que ahora queda en `personajes` (consecuencia directa de §1.2 en m01d; el handoff no lo listaba).
8. **Persona en `personajes` de m01d sin campo `tipo`** (sin `tipo` = persona): agregarlo cambiaba el dorado v3 sin necesidad.
9. **Dorado v3** (`test_module_f11.V3_GOLDEN`): pasa de `76101fbe…` a `cf2181e4…` porque el dorado guarda los mensajes de feedback; cambian exactamente los cinco textos del handoff. `test_dorado_v3_solo_cambian_los_mensajes_de_f22` vuelve esos textos atrás y obtiene `76101fbe…`.
10. **Métricas informativas guardadas en los JSON de la corrida**: el `antagonista_caps` de `guion_ycua_f22.json` y de la escaleta dicen [] porque se calcularon antes de un arreglo de la métrica (sumé el nombre completo de la persona: `nombres.terminos` arma «juan paiva» y no encontraba «Juan Pío Paiva»). La página y este reporte usan el valor recalculado (7). No cambia ningún bloqueante.
11. **Respaldos:** Ycuá `01a_columna`, `01a_escaleta`, `01b_editor_v3`, `01b_guionista_v3`, `01b_narracion_v3`, `01b_narration` → `*_f17.json` (solo `01a_columna.json` se pisó; la escaleta nueva es `01a_escaleta_f22.json`). Kyshtym: `00_pool_v3_f20.json`, `ficha_caso_f18.json`.
12. **`topics_db` sin tocar**: el topic de Kyshtym en `topics_db` sigue con el pool de F20 (mismos ids de datos/citas/cronología; el de F21c suma personajes). Si la cadena de producción va a correr Kyshtym, hay que alinearlo.
13. **`_transfer_tmp/` borrado.**

## 7. Tests
- `test_module_f22.py` (52): md5 de los 6 archivos; los 4 SISTEMA y la tarea de la columna literales; viejos con su versión; escaleta v1 y tareas byte-idénticas a 8be0ea9; prompts y mensajes sin Orleans/Ycuá; ancla con el lugar y año del seed; «ese día»; dorado v3 con solo los mensajes cambiados; esquemas y chequeo del antagonista en columna y escaleta (los tres tipos, variante de la ficha, institución fuera de la ficha, ninguno sin `por_que`); m01d con la institución; `antagonist_problems`/`_ANON_VOICE` solo con persona (Orleans/Gusman como antes); métricas; ficha con institución; `verify_pool` con el documento ruso F13 (con y sin el campo); `validate_doc_items` con `nombre_en_documento`; merge/presencia; «cero Cardal» con los controles.
- Adaptados (apuntan a las constantes con versión, mismos md5): f11 (dorado), f14, f15, f15b, f16, f17 (+ `col_buena` con antagonista), f21.
- Suite amplia (`test_module_f[0-9]*`, `gfx_*`, `01a*`, `01b*`, `m03_*`, fase2b reassemble/hwencode, concat, transition): **795 verdes + las 5 previas** (3 `01b_pauses`, 2 `m03_merge_timing`).

## 8. Archivos
`lab/hyperframes/f22/`: `F22_REPORT.md`, `PROMPTS_f22_diff.md`, `compara_f22.html`, `resumen_f22.json`, `costos_f22.json`, `f22_corridas.py`, `f22_compara.py`, `f22_diffs.py`, `cero_cardal.py`, `FICHA_kyshtym.md`, `ficha_kyshtym_f22.json`, `ficha_crudo_kyshtym.json`, `pool_kyshtym_f22.json`, `COLUMNA_{ycua,kyshtym}.md`, `columna_{ycua,kyshtym}_f22.json`, `columna_crudos_*.json`, `ESCALETA_{ycua,kyshtym}.md`, `escaleta_{ycua,kyshtym}_f22.json`, `escaleta_crudos_*.json`, `NARRACION_{ycua,kyshtym}_f22.md`, `guion_{ycua,kyshtym}_f22.json`, `prompt_{tema}_f22_{paso}.txt` (con md5), `run_*.log`. Código: `researcher_steps/{ficha_caso,research_v3}.py`, `script_engine/{m01a_columna,m01a_escaleta,guion_v4,guion_v3_reglas,m01d_particion,m05_narrative}.py`, `test_module_f22.py` y los 7 tests adaptados.

## 9. Veredicto del revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

Corrí por mi cuenta: pytest test_module_f22.py (52 verdes), f22_diffs.py, cero_cardal.py sobre las 7 salidas, md5 de los 4 bloques SISTEMA contra el código, suma de costos y la lista de archivos tocados. No corrí f22_corridas.py ni la suite amplia (795), que quedan solo por dicho del reporte.

| # | requisito | estado | evidencia |
|---|---|---|---|
| 0 | md5 del handoff y de los 5 archivos | OK | `md5sum` da 2685deec…, 7068cef5…, 168358d1…, af1d5f41…, 601aa76a…, 9d80720a… (todos iguales a §6) |
| 1.1a | 4 prompts literales desde «## SISTEMA» | OK | Extraje cada bloque y lo comparé con `ficha_caso.system()`, `m01a_columna.SYSTEM`, `m01a_escaleta.SYSTEM_V2` y `guion_v4.system()`. Los 4 md5 son idénticos (7d3599dc, f294cf6b, 7ea18a6a, 743e4f0a) y `b==s` es True |
| 1.1b | versiones `f22-1` / `v5.2`; viejos conservados | OK | Las 4 `PROMPT_VERSION` son f22-1. Los viejos siguen como `SYSTEM_F15_1`, `SYSTEM_F17_1`, `SYSTEM_V2_F16_1` y `system("f15b-1")` (declarado). La v1 de la escaleta es byte-idéntica según `test_escaleta_v1_byte_identica` (verde) |
| 1.1c | R3, `seed_vocabulario`, `seed_profile`, mensajes de feedback sin nombres propios | OK | `git diff` de `research_v3`, `m05_narrative` y `guion_v3_reglas`. «ese domingo» pasó a «ese día» y el ancla se arma con el lugar y el año del seed |
| 1.2 | antagonista persona / institución / ninguno de punta a punta | OK en lo implementado, con un hueco (ver obs. 3) | Cambios en columna, escaleta, `m01d`, `antagonist_problems`, métricas `antagonista_tipo` y `antagonista_caps`. Hay tests de los tres tipos, de la variante de la ficha, de la institución fuera de la ficha y de ninguno sin `por_que` (52 verdes) |
| 1.3 | `nombre_en_documento` y `autor_en_documento` | PARCIAL, declarado | Implementado en el esquema R3, `verify_pool`, `presence_v3` y `_names_in`. El test literal «Осетров» → verificada NO pasa: el texto trae «В.М. Осетрова» (genitivo) a 658 caracteres, fuera de la ventana de 400. Con «В.М. Осетрова» sí se verifica. Está en F22_REPORT §6.2 y los tests documentan los dos casos |
| 1.4 / 4 | cero reglas de estilo nuevas, cero cambios de umbrales | OK | `git diff -U0` no muestra cambios en constantes numéricas. Los cambios son prompts, esquemas y mensajes. `institucion_de_la_ficha` pasó de `ev.norm` a `nombres.norm` (lectura de nombres, no un umbral) |
| 2 | corridas Ycuá y Kyshtym, respaldos | OK | `costos_f22.json` tiene 8 etapas. Los respaldos `*_f17.json` y `ficha_caso_f18.json` están declarados en §6.11 (esos archivos son datos fuera del git status y no los vi) |
| 2 | Ycuá: no empeora | PARCIAL, declarado | 0 bloqueantes, pero 838 palabras (≈6.8 min) contra 1,384 (≈11.3 min) de F16, y 13 personas con nombre contra 24 (el reporte las llama F16, no F17). Tiene que decidirlo el analista; el reporte no separa si la causa es la escaleta nueva o el guion v5.2 |
| 2 | Kyshtym: llega a guion; antagonista esperado = institución | PARCIAL, declarado | Llegó al guion. El antagonista salió «ninguno» en vez de institución (§6.5). El guion queda con 1 bloqueante (a) «1982»: el año está en `fuente` de D96/Q08, y `invented_numbers` no lo lee. PARADA con el crudo guardado, sin parche, como pide el handoff |
| 2 | tope US$ 3.00 | OK | La suma de `costos_f22.json` es 1.4672, igual a `usd_total` y al reporte (Ycuá 0.6003, Kyshtym 0.8669) |
| 3 | tests | OK | 52 verdes en `test_module_f22.py`. Incluye md5, esquemas, `m01d`, `antagonist_problems`, `verify_pool` y cero Cardal con controles |
| 3 | cero Cardal | OK | Mi corrida de `cero_cardal.py` da «cero Cardal» en FICHA_kyshtym, COLUMNA y ESCALETA de ambos temas, y NARRACION de ambos |
| 5 | reporte: md5, diff línea a línea, tablas, costos | OK | F22_REPORT §1, §3, §4, §5 y Anexo A (`PROMPTS_f22_diff.md`, 266 líneas, reproducible con `f22_diffs.py`) |
| 5 | veredicto íntegro del revisor | PENDIENTE | La §9 todavía dice REVISOR_PENDIENTE: ahí va este veredicto |
| Pedido | `_transfer_tmp/` borrado; no commitear `.env`, `config.py` ni `lab/_gpt_probe_analista/` | OK | `_transfer_tmp` no existe. Ningún `.env` ni `config.py` aparece en el diff. `_gpt_probe_analista` es untracked y hay que excluirlo al hacer `git add` |
| Pedido | `compara_f22.html`, ESTADO_SESION | OK | `compara_f22.html` existe (35 KB) y ESTADO_SESION tiene la entrada F22 (línea 15) |

Observaciones:
1. El reporte señala tres desvíos de pegado literal que no están en el «Qué cambia» de los archivos (§1 puntos 1 a 3). La frase de `traduccion` en la ficha, los cuatro ítems de `<errores>` del guion (el archivo dice dos) y «se dice por su rol» en la regla 6 del guion salieron del archivo literal. Las tres líneas están en el diff y quedan a confirmar por el analista. También avisa que los md5 «viejos» que citan los archivos no son los de los bloques en código, y lo declara.
2. Se cambió una constante de test, el dorado v3 (`V3_GOLDEN`, de 76101fbe a cf2181e4). El reporte lo declara (§6.9) y un test devuelve los 5 textos al estado anterior y recupera 76101fbe. Es consecuencia del mandato de §1.1 sobre los mensajes.
3. Hueco en §1.2: «una persona con rol institucional tiene que estar nombrada en el texto de sus ids» NO se implementó. CC lo declaró como chequeo nuevo que no agregó (§6.3). Es un desvío del handoff con motivo declarado.
4. Hubo gasto no planeado por un freno mío mal dimensionado: el pase 1 de la escaleta de Ycuá (US$ 0.134) se cortó y hubo que rehacerlo (§6.1). Está dentro del tope y declarado.
5. Los JSON de la corrida guardan `antagonista_caps` = [] y el reporte usa el valor recalculado (7). Está declarado (§6.10).
6. Cambios no pedidos en `m05_narrative` (saltea instituciones en el aviso de nombre y apellido) y en `m01d` (el campo `tipo` solo para instituciones). Ambos declarados (§6.7 y §6.8).
7. Ycuá se corrió sin las notas de Omar de F17 (§6.6). Es defendible: el handoff pide columna v1.1 a secas.

Fuera de alcance: ninguno. Los 7 `test_module_f*.py` adaptados (f11, f14, f15, f15b, f16, f17, f21) están declarados y son necesarios para apuntar a las constantes con versión. `diag_234_cap4.py` y `gfx_profiles/*` no son de esta tanda y no aparecen en lo que revisé.

Riesgos que el contrato no cubre:
- La caída de Ycuá a 838 palabras no está explicada: no se separó guion v5.2 de escaleta v2.1, y 838 palabras es un largo que puede no alcanzar para el video.
- El pool de Kyshtym tiene dos `P09` (§6.4) y `topics_db` sigue con el pool de F20 (§6.12). Ninguno de los dos está resuelto y ambos afectan a una futura producción de Kyshtym.

---

## Anexo A — md5 y diff de los prompts (= PROMPTS_f22_diff.md)

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
