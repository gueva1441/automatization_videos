# F20 (parte 1) — el research se adapta al tema · REPORTE

2026-10-24 · rama `f11-guion-v4` (desde `d7ce148`) · solo research y compuerta: **no corrió ficha, columna, escaleta ni guion**. Runner `f20_corridas.py` (etapas `recalculo`, `research`, `vocab_kyshtym`).

## 0. En una línea
**Kyshtym pasa de ROJO a VERDE** (208 datos · 20 citas verificadas · **4 humanos elegibles** · 22 eventos con fecha). **Orleans e Ycuá siguen verde y verde, sin perder a ningún elegible** (12 → 32 y 15 → 32). Gasto: **US$ 1.012** (research de Kyshtym US$ 0.963, de un tope de 3.50). Los testigos de la explosión (Osetrov, Komarov, Serov) y las voces rusas (Ladeishchikova, la madre de Kutepova) tienen citas verificadas en el pool, pero **no son personajes**: `evidence_pool.is_person` rechaza los nombres con iniciales y los escritos en cirílico (§5). Eso queda fuera de §1 y no lo toqué.

## 1. Los tres perfiles (tal cual)

### Orleans (`ba6c3cac-f7r3`, `_perfil_f20.json`, sin research)
```json
{
 "roles_testigo": [
  "preso",
  "prisionero",
  "recluso",
  "testigo",
  "demandante",
  "superviviente",
  "periodista",
  "abogado"
 ],
 "roles_antagonista": [
  "sheriff",
  "administración penitenciaria",
  "autoridades locales",
  "departamento de justicia",
  "estado",
  "gobierno de la ciudad",
  "oficiales de la prisión",
  "condado de Orleans"
 ],
 "sustantivos_conteo": [
  "presos",
  "reclusos",
  "prisioneros",
  "víctimas",
  "testimonios",
  "demandantes",
  "supervivientes",
  "afectados",
  "evacuados"
 ],
 "_f20": "vocabulario del caso, sin research (F20 §2.1)"
}
```

### Ycuá (`f8s1-ycua-bolanos`, `_perfil_f20.json`, sin research)
```json
{
 "anio_evento": 2004,
 "lugar_principal": "Asunción",
 "idioma_local": "español (Asunción, Paraguay)",
 "nombres_lugar": [
  "Incendio del supermercado Ycuá Bolaños",
  "Tragedia de Ycuá Bolaños",
  "Ycuá Bolaños fire",
  "Ycuá Bolaños"
 ],
 "place_re": "\\bIncendio\\ del\\ supermercado\\ Ycuá\\ Bolaños\\b|\\bTragedia\\ de\\ Ycuá\\ Bolaños\\b|\\bYcuá\\ Bolaños\\ fire\\b|\\bYcuá\\ Bolaños\\b",
 "roles_testigo": [
  "sobreviviente",
  "sobrevivientes",
  "survivor",
  "oikovéva",
  "familiar",
  "relatives",
  "trabajador",
  "rescuer",
  "cliente",
  "witness"
 ],
 "roles_antagonista": [
  "dueño",
  "dueños",
  "owner",
  "jára",
  "gerente",
  "manager",
  "juez",
  "fiscal",
  "prosecutor",
  "Corte Suprema"
 ],
 "sustantivos_conteo": [
  "víctima",
  "víctimas",
  "victim",
  "ohasa'asýva",
  "muertos",
  "fallecidos",
  "dead",
  "omanóva",
  "heridos",
  "personas"
 ],
 "_f20": "vocabulario del caso, sin research (F20 §2.1)"
}
```

### Kyshtym (`f18-kyshtym-mayak`, `_perfil.json`)
```json
{
 "anio_evento": 1957,
 "lugar_principal": "Mayak Production Association",
 "idioma_local": "ruso (Ozyorsk, Unión Soviética)",
 "nombres_lugar": [
  "Kyshtym Disaster",
  "Mayak Disaster",
  "Kyshtym Accident",
  "Urals Nuclear Waste Accident",
  "Mayak Production Association",
  "PA Mayak"
 ],
 "nombres_locales": [
  "Кыштымская авария",
  "Маяк",
  "ПО «Маяк»",
  "Производственное объединение «Маяк»",
  "Озёрск",
  "Челябинск-40",
  "Катастрофа на ПО «Маяк»"
 ],
 "place_re": "\\bKyshtym\\ Disaster\\b|\\bMayak\\ Disaster\\b|\\bKyshtym\\ Accident\\b|\\bUrals\\ Nuclear\\ Waste\\ Accident\\b|\\bMayak\\ Production\\ Association\\b|\\bPA\\ Mayak\\b|(?<!\\w)Кыштымская\\ авария(?!\\w)|(?<!\\w)Маяк(?!\\w)|(?<!\\w)ПО\\ «Маяк»(?!\\w)|(?<!\\w)Производственное\\ объединение\\ «Маяк»(?!\\w)|(?<!\\w)Озёрск(?!\\w)|(?<!\\w)Челябинск\\-40(?!\\w)|(?<!\\w)Катастрофа\\ на\\ ПО\\ «Маяк»(?!\\w)",
 "roles_testigo": [
  "testigo ocular",
  "eyewitness",
  "eyewitnesses",
  "очевидец",
  "очевидцы",
  "residente",
  "resident",
  "residents",
  "житель",
  "жители",
  "trabajador",
  "worker",
  "workers",
  "работник",
  "работники",
  "informante",
  "informant",
  "informants",
  "информатор",
  "информаторы",
  "superviviente",
  "survivor",
  "survivors",
  "выживший",
  "выжившие",
  "persona local",
  "local person",
  "local people",
  "местный житель",
  "местные жители"
 ],
 "roles_antagonista": [
  "gobierno",
  "government",
  "governments",
  "правительство",
  "правительства",
  "complejo químico",
  "chemical combine",
  "chemical combines",
  "химический комбинат",
  "химические комбинаты",
  "administración de la planta",
  "plant management",
  "plant managements",
  "администрация завода",
  "администрации заводов",
  "ministerio",
  "ministry",
  "ministries",
  "министерство",
  "министерства",
  "autoridad estatal",
  "state authority",
  "state authorities",
  "государственная власть",
  "государственные власти",
  "servicio secreto",
  "secret service",
  "secret services",
  "секретная служба",
  "секретные службы"
 ],
 "sustantivos_conteo": [
  "víctima",
  "victim",
  "victims",
  "жертва",
  "жертвы",
  "afectado",
  "affected person",
  "affected people",
  "пострадавший",
  "пострадавшие",
  "irradiado",
  "irradiated person",
  "irradiated people",
  "облученный",
  "облученные",
  "evacuado",
  "evacuee",
  "evacuees",
  "эвакуированный",
  "эвакуированные",
  "enfermo",
  "sick person",
  "sick people",
  "больной",
  "больные",
  "fallecido",
  "fatality",
  "fatalities",
  "погибший",
  "погибшие",
  "herido",
  "injured person",
  "injured people",
  "раненый",
  "раненые"
 ]
}
```

Los de Orleans e Ycuá son del 2.º intento: el 1.º venía con las formas pegadas en un elemento («preso / presos (en) prisoner / prisoners»; respaldo `perfil_*_f20_intento1.json`). El de Kyshtym es el 2.º vocabulario: el que generó `run_seed` venía con las formas pegadas por espacios (`perfil_kyshtym_f20_intento1.json`). §4 explica la lectura de formato.

## 2. Antes → después

| | Orleans | Ycuá | Kyshtym (F19 → F20) |
|---|---|---|---|
| compuerta | verde → **verde** | verde → **verde** | rojo → **verde** |
| métricas antes | datos 558 · citas_verificadas 162 · elegibles_humano 12 · eventos_con_fecha 127 | datos 227 · citas_verificadas 52 · elegibles_humano 15 · eventos_con_fecha 62 | datos 174 · citas_verificadas 18 · elegibles_humano 0 · eventos_con_fecha 20 |
| métricas después | datos 558 · citas_verificadas 162 · elegibles_humano 32 · eventos_con_fecha 127 | datos 227 · citas_verificadas 52 · elegibles_humano 32 · eventos_con_fecha 62 | datos 208 · citas_verificadas 20 · elegibles_humano 4 · eventos_con_fecha 22 |
| conteos canónicos | 6,375 (variantes 5,919, 6,000, 6,000, 6,295, 6,375, 6,500, 7,000, 8,000) → 6,375 (variantes 5,919, 6,000, 6,000, 6,295, 6,375, 7,000, 8,000) | — → — | — → — |
| documentos por idioma (propuestos · bajados · nombran el evento · aportan · ítems*) | sin research: iguales | sin research: iguales | ?: 6 · 0 · 0 · 0 · 0<br>en: 5 · 5 · 2 · 2 · 88<br>ru: 9 · 8 · 8 · 8 · 239 → ?: 2 · 0 · 0 · 0 · 0<br>en: 7 · 7 · 4 · 4 · 169<br>ru: 11 · 8 · 8 · 8 · 217 |

\* Ítems por documento: un ítem que está en dos documentos cuenta en los dos.

**Elegibles Orleans:** 12 → 32. Siguen: Brady Richard, Dan Bright, Edward “Edgar” Burton, Iris Hardeman, Joyce Gilson, Pearl Cornelia Bland, Quantonio Williams, Raphael Schwarz, Renard Reed, Rhonda Ducre, Tyrone Lewis, William Short. **Entran:** Albert G. Couvillion, Andy Kopplin, Arnie Fielkow, Big Whappy, Capitán Jenkins, Christina Foster, David Fernandez, Denise Lewis Henry, Gedra Payne Robinson, Glyendale Stevenson, Kathleen Babineaux Blanco, Keanna Herbert, Luis Reyes, Mark Jones, Mary Gehman, Oliver Thomas, Phyllis Mann, Richard Stalder, Ronnie Lee Morgan, Jr., Shawn Duncan. **Salen:** ninguno.

**Elegibles Ycuá:** 15 → 32. Siguen: Angélica Roa, Benedicto Pérez, Blas Cristaldo, Cristian Sosa, Diana Benítez, Digna Felicia Cáceres, Juan Brizuela, Julia López, Liz Torres, Mario Eduardo Chamorro, María Angélica, Nelson Astigarraga, Rubén Urbieta, Tatiana Gabaglio, Ángela Pujol. **Entran:** Alejandro Maciel, Alejandro Nissen, Amada Correa, Antonio Morínigo, Beatriz González, Carlos Halke, Escobar Faella, José Luis Simón, Lili Cristaldo, Luis Escobar Faella, Nelson Jara, Rubén Valdez, Tania Campos, Verónica Becker, Víctor Galeano, Yessica Natalia, Yessica Vanessa. **Salen:** ninguno.

**Elegibles Kyshtym:** ninguno → Lyudmila Krestinina, Andrei Vazhenin, Zhores Medvedev, Lev Tumerman.

Lo que se ve en las tablas:
- En Orleans, la canónica 6,375 se mantiene, pero se pierde la variante 6,500: ese dato usa un sustantivo que el perfil no trae.
- Ycuá sigue sin canónica: el conteo exige ≥ 1000 y el mismo conteo en ≥ 2 documentos, y sus muertos son 327–400.
- En Kyshtym tampoco hay canónica: las cifras grandes son de dosis o de superficie, no del mismo sustantivo en dos documentos.
- Entre los que entran en Orleans hay funcionarios: Blanco (gobernadora), Stalder (secretario de Correcciones), Thomas y Fielkow (concejales). La regla nueva solo excluye al antagonista y a quien tiene como rol uno de `roles_antagonista`. Decide el analista.

## 3. Kyshtym: personajes del pool (lista completa) y citas

| id | nombre | rol | testigo | antagonista | citas | datos | presente en el evento | **elegible** | documentos |
|---|---|---|---|---|---|---|---|---|---|
| P01 | Lyudmila Krestinina | Jefa del laboratorio de epidemiología del Centro Científico y Práctico de Medicina de Radiación de los Urales | False | False | 2 | 1 | False | **True** | F04 |
| P02 | Andrei Vazhenin | Oncólogo jefe de la región de Chelyabinsk | False | False | 1 | 0 | False | **True** | F04 |
| P03 | Zhores Medvedev | Genetista soviético exiliado | False | False | 2 | 11 | True | **True** | F11, F13, F18 |
| P04 | Lev Tumerman | Científico soviético | True | False | 2 | 3 | False | **True** | F11 |
| P06 | Igor Vasil'evich Kurchatov | Padre de la ciencia atómica en la Unión Soviética | True | True | 0 | 3 | False | **False** | F11 |
| P07 | N. V. Timofeyev-Resovskiy | Científico que realizó investigaciones radioecológicas | True | False | 0 | 0 | False | **False** | F11 |
| P08 | Josef Stalin | Líder de la URSS | False | True | 0 | 1 | False | **False** | F18 |
| P09 | periódico Komsomolskaya Pravda | — | False | False | 1 | 0 | False | **False** | F13 |

Citas del pool: ✔ = verificada. Las de autor sin «personaje» son las que se pierden en §5.

| id | autor | ✔ | doc | texto (≤ 110) |
|---|---|---|---|---|
| Q01 | Lyudmila Krestinina | ✔ | F04 | el riesgo de desarrollar cáncer en el área donde se propaga la nube radiactiva y en las orillas del río Techa … |
| Q02 | Lyudmila Krestinina | ✔ | F04 | el 92% de la dosis fue recibida por las personas durante los dos primeros años, y ahora la mayoría de los terr… |
| Q03 | Andrei Vazhenin | ✔ | F04 | el cáncer es provocado no tanto por la radiación como por el tabaquismo y el alcohol, así como por la industri… |
| Q04 | Андрей Талевлин | — | F15 | La población de aquellos pueblos y aldeas donde el reasentamiento se llevó a cabo parcialmente no recibe ayuda… |
| Q05 | Толстиков, Бочкарева | ✔ | F03 | Como resultado de la liquidación de sus consecuencias, se adquirió por primera vez experiencia de tal magnitud… |
| Q06 | В.Д. Камынин | ✔ | F03 | incluso en nuestro tiempo, se mantiene el secreto de Estado sobre estos documentos, lo que dificulta su uso. |
| Q07 | El exjefe médico del hospital de Kyshtym | ✔ | F10 | consideraba que era un feto humano con una grave anomalía de desarrollo |
| Q08 | Zhores Medvedev | ✔ | F11 | la explosión arrojó polvo y materiales radiactivos a lo alto del cielo, ... Fuertes vientos soplaron las nubes… |
| Q09 | Lev Tumerman | — | F11 | A unos 100 kilómetros de Sverdlovsk, una señal de tráfico advertía a los conductores que no se detuvieran dura… |
| Q10 | Lev Tumerman | ✔ | F11 | Lo que me dijeron muchas personas en Sverdlovsk y Belpyarsk fue que la lluvia radioactiva fue consecuencia de … |
| Q11 | anuncios en la radio y periódicos | ✔ | F11 | acusando a EE.UU. de transmitir veneno por el aire que era transportado por la lluvia que caía sobre todo el Ó… |
| Q12 | Una antigua residente del Óblast de Chelyabinsk | ✔ | F11 | Podíamos ver cómo se les desprendía la piel de la cara, las manos y otras partes expuestas del cuerpo. Estas v… |
| Q13 | Guinness Book of World Records | ✔ | F13 | Accidente con residuos nucleares: escape de residuos de plutonio. Kyshtym, URSS, aproximadamente en diciembre … |
| Q14 | Zhores Medvedev | — | F13 | durante el accidente de 'Kyshtym' debió haber cientos de muertos |
| Q15 | periódico Komsomolskaya Pravda | — | F13 | El horror más global ocurrió en 1957, cuando cerca de Kyshtym explotó una planta secreta de producción de arma… |
| Q16 | V.M. Osetrov | ✔ | F13 | estando junto al panel de instrumentos y sintiendo una fuerte sacudida de la tierra, escuchó un estruendo, y f… |
| Q17 | V.I. Komarov | ✔ | F13 | después de la explosión fue lanzado por los aires y arrojado al suelo. Al levantarse y salir a la calle, vio q… |
| Q18 | I.F. Serov | ✔ | F13 | En ese momento, en la zona de la planta 25, donde se encontraba el almacén de residuos radiactivos, se levantó… |
| Q19 | Любовь Ладейщикова | ✔ | F16 | los niños estaban muy contentos con lo que le pasaba al río: peces muertos flotaban panza arriba. Los atrapaba… |
| Q20 | Мама de Надежда Кутепова | ✔ | F16 | el pescado que traían de la región de Chelyabinsk, cuando lo ponían sobre papel de rayos X, instantáneamente d… |
| Q21 | médicos | ✔ | F16 | Está todo claro, tu madre fue liquidadora |
| Q22 | abogados de Rosatom | ✔ | F16 | ¿cómo se puede separar a la madre y al feto si son un todo único, y el feto se ve más afectado por factores no… |
| Q23 | Jueza | ✔ | F16 | Nadia, no queremos ni un solo precedente para que en la región las viudas de los liquidadores de 'Mayak' recib… |
| Q24 | Greenpeace 2007a | ✔ | F19 | La planta nuclear de Mayak en los Urales del Sur fue uno de los secretos oscuros de la guerra fría. Era el pri… |
## 4. Cambios (solo `researcher_steps/research_v3.py`, §1) y lecturas declaradas
1. **Perfil con el vocabulario del caso.** `seed_vocabulario` (1 Flash) genera `roles_testigo`, `roles_antagonista` y `sustantivos_conteo` a partir del seed y de las fuentes de R1.
   - `run_seed` lo agrega a `_perfil.json` después de R1, cuando falta. **Diferencia con el handoff:** es otra llamada, no la misma que genera `nombres_locales`. Esa corre antes de R1, y el handoff también pide usar R1.
   - **Lectura de formato:** el modelo pegaba las formas en un solo elemento, con barras y marcas de idioma en Orleans e Ycuá, y con espacios en Kyshtym.
     - El esquema pide cada término como `{es, otras: [...]}`.
     - `_formas` corta en «/», «;», «,» y «(en)».
     - No hay chequeo nuevo: es leer la salida.
2. **El research lee el perfil** (`set_vocabulario`, llamada en `run_seed`):
   - **R3:** «testigo … ({roles_testigo})» y «antagonista … ({roles_antagonista})». Sin perfil: «según el caso». Se fue la lista «preso, guardia, familiar, rescatista, vecino», y también «funcionarios, abogados o expertos».
   - **`_TITLES`:** queda la base genérica (grados, tratamientos, sufijos) más los roles del perfil.
     - **Diferencia declarada:** «sheriff», «deputy» y «alguacil» siguen en la base, porque son cargos delante de un nombre, como «captain», y la lista del handoff no los incluye.
     - Sin «deputy», «Deputy Renard Reed» deja de ser Renard Reed: en el 2.º intento del recálculo, Reed perdía sus 3 citas y salía de los elegibles.
     - «warden» salió.
   - **`_NOT_PERSON`:** solo palabras gramaticales y de grupo («del», «en», «group», «officers», «oficiales»). Del perfil entran solo las formas de grupo (plurales o frases), como en la lista vieja («deputies», «guardias»). Un rol en singular es un cargo delante del nombre, va a `_TITLES` y deja «Deputy Foster» como persona.
   - **Fuera:** inmate, recluso, reclusa, preso, presa, warden, deputies, guardias, guards, abogado, abogada, attorney.
   - **Conteo:** la regex se arma con `sustantivos_conteo` del perfil más «personas» y «víctimas». Sin perfil, «presos» ya no es conteo.
   - **Descargas:** `MAX_DESCARGAS_OK` = 10 **por idioma**, con el mismo orden de prioridad dentro de cada idioma. El idioma sale de `fuente_idioma`: un título en otro alfabeto manda sobre el `idioma` de R1, que marcaba «en» o «?» a fuentes rusas.
3. **Humano elegible** (`person_stats`):
   - Regla: no antagonista, sin un rol de `roles_antagonista`, y con una cita propia verificada **o** ≥ 3 ítems.
   - **Lectura declarada de «≥ 3 ítems»:** citas + datos + eventos que lo nombran (antes: 3 citas o 3 datos).
   - **Lectura declarada de «un rol de `roles_antagonista`»:** el rol **empieza** con ese rol («Sheriff de Orleans» queda afuera; «Oficial del sheriff», no). Con «lo nombra en cualquier parte», Reed salía.
   - Ya no se exige testigo ni presencia en el año. `presente_en_evento` queda como dato informativo.
4. **La compuerta** no cambió: mismos umbrales; solo cambia quién cuenta como elegible.

**Lo que sigue a la medida de Orleans** (fuera de las líneas del handoff, sin tocar): `SUBJECT_RE_DEFAULT` (OPP / Orleans Parish Prison), `_OTHER_PLACE` (Hunt, Angola, Templeman…) y `_OFFICIAL_SAYS` («según el sheriff…»), en `population_canon`. Para otro tema, `population_canon` casi nunca encuentra nada.

## 5. Lo que el tema todavía rompe (anotado, sin tocar: fuera de §1)
- **Los testigos rusos no llegan a personajes.** `evidence_pool.is_person` rechaza los nombres con iniciales («V.M. Osetrov», «V.I. Komarov», «I.F. Serov») y los escritos en cirílico («Любовь Ладейщикова», «Андрей Талевлин»), y `person_key` lee solo letras latinas.
  - Sus citas están en el pool y están verificadas (Q16–Q19), pero `add_quote_authors` no los suma como personajes, así que la regla nueva de elegible nunca los ve.
  - La madre de Kutepova y la jueza entran como autores descriptivos, no con nombre.
  - Los 4 elegibles de hoy son voces de documento: Krestinina, Vazhenin, Medvedev, Tumerman.
- **R3 de Kyshtym corrió con los roles pegados** del 1.er vocabulario: el modelo los lee como texto. El 2.º vocabulario se aplicó a `person_stats`, a las canónicas y a la compuerta, sin rehacer R3 (etapa `vocab_kyshtym`).
- **R1 no reprodujo la lista de F19:** salieron 20 fuentes, en parte distintas (p. ej. biblioatom 1990). Hubo 4 HTTP 429 (F06, F07, F12, F14) y un video.

## 6. Costo (`costos_f20.json`)
| etapa | US$ |
|---|---|
| vocabulario Orleans (intento 1 + 2) | 0.0078 + 0.0051 |
| vocabulario Ycuá (intento 1 + 2) | 0.0144 + 0.0095 |
| research Kyshtym (perfil, R1, R2, R3, R4, R5, compuerta; tope 3.50) | 0.9632 |
| vocabulario Kyshtym (2.º) | 0.0125 |
| **total** | **1.0125** |

El freno corta antes de cada llamada que pasa por `gemini_helpers.call_pro_json`, `call_flash_json` o `research_v3.search_*`, si lo gastado más 0.12 pasaría el tope. Las de `verify_quotes` (grounding directo) no pasan por el freno: se miden al final.

## 7. Tests
- `test_module_f20.py` (8):
  - el perfil con los tres campos y `{es, otras}`;
  - `run_seed` completa el perfil después de R1;
  - `_formas`;
  - las listas sin términos de tema;
  - R3 con los roles del perfil;
  - el conteo con presos y con muertos;
  - las descargas por idioma (24 fuentes: 10 + 10, el resto sin intentar);
  - `elegible_humano` con Reed, Kutepova, Osetrov y Gusman, más Serov (cita sin verificar), una antagonista y «Oficial del sheriff».
- **Tests viejos adaptados** en `test_module_f7.py`: 4 tests de Orleans cargan el vocabulario de Orleans con un fixture, porque ahora viene del perfil. En `test_people_names_and_eligibility`, Duncan pasa a ser elegible (la presencia ya no excluye), con `presente_en_evento` en False.
- Suite amplia: **700 verdes + las 5 previas**.

## 8. Disco
- `_steps/ba6c3cac-f7r3/` y `_steps/f8s1-ycua-bolanos/`: **no se pisó nada**. Se agregaron `_perfil_f20.json`, `POOL_GATE_f20.md` y `00_pool_v3_f20_recalculo.json`. Copias en `lab/hyperframes/f20/`: `POOL_GATE_{orleans,ycua}_f20.md`, `perfil_*_f20.json` y `recalculo_f20.json`. Los intentos 1 y 2 quedan como `*_intento1`/`*_intento2`.
- `_steps/f18-kyshtym-mayak/`:
  - el pool, el perfil, `fuentes/` y POOL_GATE son los de F20;
  - lo de F19 quedó en `00_pool_v3_f19.json` y `_f19/` (POOL_GATE, perfil, manifiesto, fuentes.json);
  - el intento 1 de F20 quedó en `00_pool_v3_f20_intento1.json`, `_perfil_f20_intento1.json` y `POOL_GATE_f20_intento1.md`.
- **El topic de Kyshtym en `topics_db` tiene el pool de F20 (verde).** Respaldo: `topics_db.pre_f20.json`.
- `lab/hyperframes/f20/f20.b64`: es este mismo handoff, comprimido con gzip y en base64 (idéntico byte a byte). No se commitea.

## 9. Veredicto del revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

Corrí `pytest test_module_f20.py test_module_f7.py test_module_f19.py`: 64 verdes. La suite de 700 no la corrí, así que ese número es NO VERIFICABLE.

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Perfil con roles_testigo, roles_antagonista, sustantivos_conteo (4–10 palabras + otros idiomas) | PARCIAL | `research_v3.py` ~1952 (`VOCAB_SCHEMA`, `seed_vocabulario`). Los perfiles de Kyshtym tienen unos 30 términos por campo, porque cuentan cada forma de idioma como término. Eso se acerca a «4–10 palabras, más sus formas». |
| 2 | R3 lee roles del perfil en vez de la lista fija | OK | `research_v3.py` ~1009 y ~1013 (`_roles`), cableado en `run_seed` con `extract_document(s2…)`. |
| 3 | Sin términos de tema en `_TITLES` / `_NOT_PERSON` | PARCIAL | Salieron inmate, recluso, preso, warden, guardias, guards, abogado, etc. (~1226-1260). Quedan sheriff, deputy y alguacil en `_TITLES_BASE`. No son términos del handoff, pero son cargos carcelarios y el handoff pide que «las listas carcelarias ya no estén en el código». Está declarado en el reporte §4, pero es una reinterpretación. |
| 4 | roles → `_TITLES` y a `_NOT_PERSON` solo formas de grupo | OK | `set_vocabulario`, ~1244-1259. El handoff dice «se suman los roles_*»; lo de sumar solo los plurales a `_NOT_PERSON` es lectura del implementador, razonable. |
| 5 | Conteo con sustantivos del perfil (+ personas y víctimas) | OK | `_count_re`, `count_value`. Probado en `test_module_f20.py`: un caso de presos y uno de muertos. |
| 6 | Descargas por idioma, 10 por idioma | OK | `download_sources` con `n_ok` por idioma. `fuente_idioma` es un detector de alfabeto nuevo, pero no es una regla de filtrado. |
| 7 | `elegible_humano` = no antagonista y (cita propia verificada o ≥3 ítems), sin presencia en el año, con `presente_en_evento` | OK | `person_stats` ~1421-1446. «≥3 ítems» se lee como n_citas + n_datos (razonable). «Rol de roles_antagonista» se lee como «el rol empieza con» (razonable). Esa condición de rol es una comprobación nueva: la regla del handoff dice «no antagonista» y se la leyó como si incluyera el rol. Está declarada en el reporte §4. |
| 8 | Vocabulario generado en el mismo paso que `nombres_locales`, a partir de R1 | PARCIAL | Es una llamada aparte después de R1, y el reporte lo declara. El handoff es ambiguo (dice «mismo paso» y también «a partir de R1»), así que esta lectura es defendible. El esquema `{es, otras}` y `_formas` son lectura de formato, no un chequeo de contenido. |
| 9 | Orleans y Ycuá recalculados sin research, `POOL_GATE_f20.md`, sin pisar nada | OK | En `data/scripts/_steps/` están solo `00_pool_v3_f20_recalculo.json`, `POOL_GATE_f20.md` y `_perfil_f20.json`. Los originales `POOL_GATE.md`, `00_pool_v3.json` y `_perfil.json` de Ycuá están. `recalculo_f20.json` confirma verde→verde, Orleans 12→32 y la variante 6,500 perdida. |
| 10 | Kyshtym rehecho, tope 3.50, respaldo `00_pool_v3_f19.json` | OK | El respaldo existe. `costos_f20.json` marca research US$ 0.9632 (total 1.0125). `POOL_GATE_kyshtym_f20.md` da VERDE: 208 / 20 / 4 / 22. |
| 11 | Lectura de la etapa `vocab_kyshtym` | PARCIAL | Recalculó vocabulario, person_stats, canónicas y compuerta sin rehacer R3, y reescribió `00_pool_v3.json`. Esto se aparta de «research v3 completo»: R3 de Kyshtym corrió con el 1.er vocabulario, el de los roles pegados. Está declarado en el reporte §5. El intento 1 está respaldado. |
| 12 | Tests de §3 (cuatro casos de elegible + los demás) | OK | `test_module_f20.py` tiene Reed, Kutepova, Osetrov, Gusman y 4 casos más. Los 4 tests viejos de `test_module_f7.py` se adaptaron (fixture, Duncan elegible) y son coherentes con el cambio de regla. |
| 13 | Reporte: tres perfiles, tabla antes/después, lista completa de personajes de Kyshtym, costo, veredicto del revisor | PARCIAL | Todo está y coincide con `kyshtym_f20.json` y `recalculo_f20.json`. El §9 del veredicto dice «(se pega abajo)», así que falta pegarlo. |
| 14 | No se tocó ficha, columna, escaleta, guion, m05, evidence, config, m03, gfx_* | OK | Los únicos archivos tocados son `research_v3.py`, `test_module_f7.py`, `test_module_f20.py` y `lab/hyperframes/f20/`. `diag_234_cap4.py` y `gfx_profiles/*` ya figuraban modificados al arrancar la sesión (mtime de junio y del 21-oct), y `lab/ESTADO_SESION.md` los declara sin commitear a propósito. |
| 15 | Reporte sin afirmaciones sin sostén | OK | Verifiqué las métricas, los elegibles, el costo y los archivos de `_steps` contra los JSON y el disco. Coinciden. |

Fuera de alcance: ninguno.

Sobre los puntos que pediste juzgar:
- Punto 7 (testigos rusos): bien anotado en §0 y §5. Los 4 elegibles de Kyshtym son Krestinina, Vazhenin, Medvedev y Tumerman; los tres primeros tienen `testigo` false. Osetrov, Komarov y Serov están en el pool como citas verificadas, pero no como personajes. Es consecuencia directa de la regla del handoff, y el analista debe verlo antes de la parte 2.
- Orleans: pasa de 12 a 32 elegibles y entran funcionarios (Blanco, Stalder, Thomas, Fielkow). El reporte lo avisa y lo deja a decisión del analista.

Riesgos que el contrato no cubre:
- Quedan listas de Orleans en `SUBJECT_RE_DEFAULT`, `_OTHER_PLACE` y `_OFFICIAL_SAYS`. Por eso `population_canon` nunca da canónica en otros temas, y Ycuá y Kyshtym salen sin ella. El reporte lo anota.
- Elegible ya no exige ser testigo, así que entran investigadores y comentaristas como humanos de la historia. La parte 2 tendrá que decidir esto.
- Hay que pegar el §9 del reporte antes del commit. ESTADO_SESION y el commit quedan después del veredicto, como indicaste.

**Nota de CC después del veredicto:** la suite amplia (700 verdes + las 5 previas) la corrí en esta sesión después del último cambio de `research_v3.py` (el esquema `{es, otras}`).
