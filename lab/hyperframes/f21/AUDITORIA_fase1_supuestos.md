# AUDITORÍA FASE 1 — supuestos de tema en la cadena semilla → guion

Analista · 2026-10-24 · Base `08d63d9` (rama `f11-guion-v4`). Solo lectura, sin gasto de API. Tres auditores en paralelo (research / jueces y ficha / columna-escaleta-guion-partición); los casos marcados ✔ fueron **ejecutados**, no leídos. Las tres tablas completas están en los anexos; esta primera parte las agrupa por **causa raíz**, que es como se arreglan.

## 0. El resumen en una línea
El pipeline no tiene 230 bugs. Tiene **9 supuestos** repetidos en 230 lugares. Siete de los nueve nacieron en Orleans y nadie los sacó cuando llegó un tema nuevo.

## 1. Las nueve familias

| # | supuesto | dónde vive (resumen) | qué rompe | arreglo | sev. |
|---|---|---|---|---|---|
| **A** | **Alfabeto latino, nombre = 2 palabras Title Case, apellido = última palabra.** Regex `[A-Za-zÁÉÍÓÚÑ…]`, `[a-zñ]+`, `\b`, `norm` NFD que destruye й/ё. Hay **4 funciones distintas de apellido** (`evidence._surname`, `guion_v4._surname`, `m01b_guionista._surname`, escaleta inline) y 3 de «es persona» (`evidence_pool.is_person`, `research_v3.person_key`, `verify_quotes._named`). | research_v3 1265/1132/1283/1304/1557/1678/1697/437(slugify)/218; evidence_pool 158-168; evidence 58/133/159/225/323; m05 84/149/211/453; guion_v3_reglas 115/143/272/337/435; guion_v4 289/583/595; m01a_columna 162-191; m01a_escaleta 263/500/627/642/1265/1410; ficha_caso 425/455/479; m01d 178/117; verify_quotes 102 | ✔ `is_person("V.M. Osetrov") → False`; ✔ `person_key("Jürgen Müller") → ("","")`; ✔ `is_named_person("Juan de la Cruz") → False` (partícula «de» en `_NOT_PERSON`); ✔ «Rasputin» → False; cirílico → **cero testigos con nombre → compuerta roja**, columna PARADA («humano no es persona de la ficha»), gancho sin ancla de lugar (hard fail permanente), antagonista nunca «nombrado». ✔ `slugify` de dos títulos rusos → mismo slug → **un documento pisa a otro en disco**. | **Un módulo `nombres.py`** (Unicode `\w`, iniciales, partículas de/del/van/von, mononimios, variantes/transliteración del pool) que reemplace a las 7 funciones. Sacar `del?/en/at/of/the` de `_NOT_PERSON`. `slugify` con `f["id"]`. | **alta** |
| **B** | **Vocabulario de cárcel/Orleans dentro del código.** | guion_v3_reglas 281-345 `_ROLE_PRESO`/`_ROLE_GUARDIA`/`role_class` (**es el bloqueante (b) de guion_v4:633**); 73-93 `JUDGMENTS`; 400-411 `photo_problems` (prohíbe «cámara», «imagen»); 369 `_ANON_VOICE`; evidence 312 `_COMMON_CAPS` (sheriff, alcaide, huracán, recluso); evidence 59 excluye «sheriff»; m05 40-80 `FORBIDDEN_FILLER` («infierno flotante», «manto de», «ecos de»), `_ADJ_LIST` (húmedo, pútrido, cautivo), `_NOT_ADJ`; m01b_guionista 40 `INSTITUTION` (parish, opp, aclu, fema, sheriff); m01a_escaleta 85 `ADMIN_TERMS` (evacuación, informe, tribunal prohibidos en pantalla); research_v3 1718-1726 **`SUBJECT_RE_DEFAULT` = «Orleans Parish Prison»** (`run_seed` nunca pasa otro → la cifra de población SIEMPRE se busca como Orleans), `_OTHER_PLACE` (Hunt, Angola, Jena, Templeman…), `_OFFICIAL_SAYS` (sheriff); 335 stopwords orleans/katrina; evidence_pool 154 `_ORG_WORDS`, 584 `_COUNT_NOUN`, 297 `_COMMON_HEADS`; verify_quotes 40 «TEMA: la Prisión Parroquial de Orleans» hardcodeado | «el teniente Ivanov» + «el sobreviviente Ivanov» → clases opuestas → **PARADA falsa de guion entero**; manicomio: «interno» = preso; «¿Por qué tardaron la evacuación?» prohibida en pantalla; «manto de nieve» y «la imagen satelital de la CIA» bloqueados; un caso en Jena (Alemania) o Angola pierde su cifra de población. | **Borrar.** `role_problems`: comparar la palabra de rol del pool con la de la narración, sin clases. Listas de estilo (filler, adjetivos, juicios, admin, institution): borrar lo de caso, dejar lo gramatical, y todo a métrica. `SUBJECT_RE`/`_OTHER_PLACE`/`_OFFICIAL_SAYS`: del perfil o fuera. | **alta** |
| **C** | **Ejemplos de prompts con hechos reales de Orleans/Ycuá** que el modelo copia. | m01a_columna 56-70 (Reed, Templeman III, 517, Pearl Bland/398, Nagin, Reyes); m01a_escaleta 1115-1145 (**ids reales** Q184, D192, D30… «517 ausentes») y 208-240 («un preso de Templeman III», «¿Dónde están los 517?»); guion_v4 119-145/204-244 («398 dólares», **«Trescientos veintisiete muertos»**, Renard Reed ×3, «Nueva Orleans, agosto de 2005», «Aunque estén en la cárcel…»), 90/103/114/116 («en la cárcel», «un preso contó», «las puertas», «Templeman III»); ficha_caso 143-152 (Pearl Bland, sheriff rechaza ayuda, Templeman III, 517 reclusos), 154-161 (huérfanos, guaraníes, puertas); research_v3 1011 («un preso de Templeman III» en R3 para CADA documento), 1972-1983 `seed_vocabulario` («en una cárcel: preso, guardia… sheriff, el ministerio, el dueño»), 123/198/331 (`"anio":2006`), 2020; m05 555/559/627/633 (feedback al modelo con «celda», «sheriff Marlin N. Gusman»); guion_v3_reglas 449 («Nueva Orleans, agosto de 2005.» como ancla modelo), 257 («ese domingo») | Sol copia un id del ejemplo → «dato_central no existe» → regeneración gastada; copia «327» → bloqueante (a) → PARADA; léxico de celdas/agua en Kyshtym. | Ejemplos de **un caso inventado** (sin cifras, ids ni nombres reales) o ids «Q##». Mensajes de feedback sin nombres propios. | **alta** |
| **D** | **El evento es un día (y un año).** | research_v3 1945 `anio_evento` INTEGER único, 1309 `ITEM_YEARS=20` + `LATE_OK/EARLY_OK` solo es/en/it, 2087 fallback año actual, 1008/1138 `fechas_presente` solo AAAA-MM-DD, 1439/1875 `presente_en_evento`; pool_gate 44 `fullmatch(\d{4}-\d{2}-\d{2})`; video_length 29 `gate_eventos_fecha=10` con día; evidence 168-175/208-210 `is_hard` exige día; 266 + m05 469 año por defecto único («2000»); guion_v3_reglas 214-265 `DATE_MAX_PER_CAP=1`, `DATE_PARAPHRASE` «ese domingo», **221 `replace_repeated_dates(day="1 de agosto")` con «domingo» fijo** (texto falso si se llama sin parámetro; v4 ya tiene la buena en 725); guion_v4 98/112/183/197 «fecha completa una vez, en el cap 2», 714-722 `event_date` = la más repetida; m05 125 «ese domingo» acepta como fecha; ficha_caso 133 «los eventos **del día**»; evidence 72/245 y guion_v3 47 año = `(19|20)\d\d` (siglo XIX fuera) | Mayak 1949–1989, asilo 1908–1987, Vajont 1959–63: la mitad de los ítems «contaminación»; 10 eventos con día exacto inalcanzables → rojo; cap de consecuencias con 2 fechas rechazado; «29 de septiembre» de otro año → «ese domingo». | Perfil con `tipo_evento` (puntual/prolongado) y **rango** `anio_inicio`/`anio_fin`; granularidad de fecha (día/mes/año) decide `is_hard`, la compuerta y la paráfrasis válida; borrar `guion_v3_reglas.replace_repeated_dates`; `DATE_MAX_PER_CAP` según nº de días distintos de la cronología. | **alta** |
| **E** | **Antagonista = una persona con apellido.** | research_v3 1014 (R3: «persona con nombre propio»), 1836 digest; evidence 368-378; m05 268/308; guion_v3_reglas 369-395 `antagonist_problems`/`_ANON_VOICE` («una fuente oficial soviética» prohibida); m01a_escaleta 668-674/1178 **obligatorio** (bloqueante v2), 1189 `institucion_de_la_ficha` solo nombre literal (sin variantes: Mayak / Combinado 817 / Minsredmash); m01d 178-188 la institución **desaparece** de `personajes` sin aviso | Kyshtym (Estado/Mayak), Vajont (SADE), manicomio (institución), represa (sin culpable) → PARADA o antagonista perdido. | `antagonista.tipo ∈ {persona, institucion, ninguno}` en toda la cadena; variantes de la ficha; m01d lo conserva con tipo. | **alta** |
| **F** | **Los jueces leen la cita en idioma original; la voz dice la traducción.** | ficha_caso 94-97/657 guarda `texto` original + `traduccion`; pero m05 494-510 `false_quotes`, 609-616 cita válida, guion_v3_reglas 51-66 `hook_problems`, 329-345 `role_problems` comparan contra `pool.citas[].texto` | En Kyshtym **toda cita dicha en español es «cita falsa»** (bloqueante). Autores institucionales («Informe TASS», «testigo anónimo») exigen que «suene» un apellido. | Jueces leen `id_texts(ficha)`/`traduccion`; autor puede ser organización/anónimo. | **alta** |
| **G** | **Umbrales calibrados con el pool de Orleans** (ACLU/DOJ: cientos de testimonios con nombre y día). | video_length 26-29 / pool_gate 21 (150 datos / 8 citas verif. / 2 elegibles / 10 eventos-día); m05 31-37 `DENSITY_MIN 2.0`, `MAX_DATO_CAPS 2`, `TRIGRAM_MAX`, `ADJ_MIN/MAX`; research_v3 40-46 `MIN_FUENTES 8`, `MIN_DOC_CHARS 3000`, `EVENT_CHECK_CHARS 5000` (decretos/recortes cortos se tiran), 1235/1499/1743 conteo ≥ **1000** (Ycuá ~400 muertos → sin cifra canónica), 1467/1727 bandas, 1042 `FOCUS_DENSITY`, 1213 `OFFICIAL_TIPOS` (académico nunca oficial); ficha_caso 232 (60–80 hechos, 15–25 citas fijos aunque el pool tenga 120 ítems); m01b_narrator 58-60 chars por rol **desacoplados** de `video_length`; m01a_skeleton 839 `SCREEN_PER_CAP`, 936 caps 6-7 con dato obligado | URSS 1957, asilo 1900, dictaduras: rojo/amarillo **por tipo de fuentes, no por calidad**; `DENSITY_MIN` obliga a meter adjetivos en un tema técnico; ficha inventa para llegar a 60 hechos. | Mover a **métrica** lo que no sea estructura; lo que quede, derivado del pool (hechos = % de ítems) o del `tipo_evento` del perfil; chars por rol ← palabras. | media-alta |
| **H** | **Una sola forma de contar la historia hecha regla.** | m01a_columna 45-52 (un humano persona con arco cap 1→7; cap 2 «vida antes»; cap 6 «los cuerpos, la búsqueda, cifras oficiales»; cap 7 «lo que la justicia dijo»); m01a_escaleta 1092-1113 SYSTEM_V2 §5 «la morgue», §8 «quién dio la orden, cómo estaban las puertas… la pericia vs los testigos es casi siempre el mejor cap 6», 1102 gancho siempre flash-forward; 812/849 + m01a_skeleton 99 `DEFAULT_INTENT_BY_CAP` fijo (cap 2 siempre «setup» → tts_tags 64 nunca pone golpes ahí; m03 hereda intents falsos); 316 «un hecho, una cifra» expulsa el rango («entre 200 y 10.000») aunque sea el único honesto | Kyshtym (sin juicio, sin cuerpos, pico técnico al inicio y pico humano décadas después), manicomio (crónica sin pico único), colectivo sin arco individual. | Oficio escrito por **función**, no por contenido («cierre: lo que quedó sin resolver»); humano colectivo o relevo permitido; `narrative_intent` desde la escaleta; «rango» como valor válido. | media |
| **I** | **Fuentes: inglés siempre, EE. UU. como norma.** | research_v3 112 «Buscá en INGLÉS y en {lugar}» (mitad del cupo en inglés para Paraguay/Italia), 1350 `.gov` (no .gob/.gov.it/.gouv), 601 `Accept-Language: en`, 450-459 `detect_lang` solo en/es/fr/it (✔ ruso/alemán → «?»), 586 `fuente_idioma`, 557 `_TAIL_HEAD` solo inglés, 38/112-131 «FOIA», «prensa de la primera semana» (URSS sin prensa libre), 619 `2006 0901` (Katrina), 2072 `idioma_local` letra muerta; evidence_pool 499 `GEO_MAX_KM` | Fuentes locales desplazadas; sitios .ru/.it sirven versión EN; idioma «?» en todos los ítems. | `idiomas_research` del perfil (inglés opcional); dominios oficiales genéricos; detección por alfabeto + stopwords del perfil. | media |
| **J** | Cosmético: docstrings/comentarios con Gusman, Tyrone y Duane Lewis, «509 ítems de Ycuá», «F10 Omar: 1 de agosto», «Orleans v1 ≈ 0.7»… | ~30 filas en los anexos | Nada; ruido y sesgo mental de quien lee. | Borrar en la misma pasada que toque cada archivo. | baja |

## 2. Qué NO tocar
Imágenes, voz, gfx, producción (`m03*`, `gfx_*`, `tts` salvo tags), `config.py` fuera de `long_video`. El contrato de 7 caps se queda (es el contrato de río abajo).

## 3. Orden propuesto (una tanda por fila; PARADA del analista entre cada una; cero API hasta la 3)
| tanda | familias | por qué juntas | cómo se valida sin gastar |
|---|---|---|---|
| **F21** | **A + B + F** | Son borrados y una generalización; no cambian ningún prompt. `nombres.py` único; fuera la dicotomía preso/guardia y las listas de Orleans; jueces leen la traducción. | Re-correr **solo los chequeos** (compuerta, `person_stats`, bloqueantes del guion F19/F20) sobre los pools y guiones que ya están en disco: Orleans, Ycuá, Kyshtym. Orleans/Ycuá no deben empeorar; Kyshtym debe ganar testigos (Osetrov, Komarov, Serov, Ladeyshchikova) sin tocar el research. |
| **F22** | **C + E** | Prompts: ejemplos de caso inventado; antagonista persona/institución/ninguno de punta a punta. | md5 de los prompts; tests de esquema; sin corrida. |
| **F23** | **D + G + H + I** | Perfil del seed con `tipo_evento`, rango de años, `idiomas_research`; umbrales a métrica o derivados; oficio por función. Es la tanda que cambia resultados, por eso va última y con todo lo anterior limpio. | Corrida Kyshtym completa (research → guion), tope US$ 5. |

## 4. Lo que yo hice mal y cambio
Cada handoff (F11–F20) auditó solo los archivos que nombraba. Esta tabla se podía hacer el 21 de octubre sin gastar un centavo. De aquí en adelante: **antes de proponer un arreglo, se revisa el camino entero por el que pasa ese dato**, no el archivo que falló.

---
## ANEXO 1 — Research, pool, verificación, compuerta (auditor 1)
Nota de alcance: `verify_quotes.verify_testimonios/verify_literal` y `evidence_pool.canonical_figures/extract_evidence_pool/build_prompt` NO corren en el camino v3 de producción (solo lab/tests y `RESEARCH_V3=0`); severidad bajada por eso.

| archivo:línea | qué asume | cat. | qué tema lo rompería | arreglo propuesto | severidad |
|---|---|---|---|---|---|
| research_v3.py:1718-1719 `SUBJECT_RE_DEFAULT` | El «sujeto» de la población es OPP / Orleans Parish Prison / «complejo carcelario»; `build_pool` (1618) se llama desde `run_seed` SIN `subject_re`, así que SIEMPRE usa este default | 6 | Todo tema que no sea Orleans: `population_canon` solo dispara si el dato dice «según el sheriff» | parametrizar desde `prof["place_re"]`/`nombres_lugar` del perfil; borrar el default | alta |
| research_v3.py:1720-1721 `_OTHER_PLACE` | Hunt, Angola, Jena, Elayn, Rapides, Templeman, Conchetta, «paso elevado/overpass» son «otro lugar» | 6 | Cualquier caso en Jena (Alemania), Angola (país), un apellido Hunt → el dato de población se descarta | borrar; si hace falta, parametrizar `lugares_excluidos` desde el perfil | alta |
| research_v3.py:1724-1726 `_OFFICIAL_SAYS` | La cifra oficial se atribuye al sheriff/alguacil | 1/6 | Kyshtym (comisión estatal), Vajont (SADE/ENEL, tribunal), asilo (departamento de salud) | parametrizar con `roles_antagonista`/«institución oficial» del perfil; o quedarse solo con «oficial/registros oficiales» | media |
| research_v3.py:335-336 `_words` | Stopwords fijas «orleans, parish, prison, katrina, hurricane» para `pista_covered` | 6 | Cosmético fuera de Orleans; además `[a-z0-9]+` deja vacía una pista en cirílico → nunca «cubierta» | borrar la resta; usar `\w+` | baja |
| research_v3.py:1429, 1433, 1666 comentarios | «Tyrone y Duane Lewis», «presencia real» | 6 | Ruido | borrar nombres | baja |
| research_v3.py:1451, 1456, 1787-1788 docstrings | «Sheriff Martin Gusman», «Marlin N. Gusman», «Abandoned & Abused: Orleans…» | 6 | Nada | neutralizar | baja |
| research_v3.py:1265 `person_key` regex `[A-Za-zÁÉÍÓÚÑáéíóúñ]+` + `w[:1].isupper()` | Nombres solo en alfabeto latino sin ü/ö/ß/ç/ã/ø/ł; cirílico, griego, árabe → `("","")` ✔ | 2 | Kyshtym (Осетров), Alemania (Müller), Portugal/Brasil (Gonçalves → apellido «gon» ✔), Polonia, Turquía | generalizar a `\w+` con `str.isalpha()` + `istitle()/isupper()` Unicode | alta |
| research_v3.py:1272-1276 `is_named_person` → `evidence_pool.is_person` + `_NOT_PERSON` | `\b(del?\|en\|at\|of\|the)\b` con re.I descarta cualquier nombre con partícula «de/del» ✔ («Juan de la Cruz», «Vittorio De Biasi», «Francisco de Paula Santander» → False) | 2 | Paraguay, España, Italia, Portugal, Francia, Países Bajos: se pierden personajes y autores de cita | sacar «del?/en/at/of/the» de `_NOT_PERSON`; dejar solo palabras de grupo | alta |
| research_v3.py:1132-1137 validate personajes | `is_named_person` + «el apellido es el ÚLTIMO token» | 2 | Cirílico (todo descartado), orden apellido-nombre (Hungría, Japón, China), mononimios («Rasputin» ✔ False) | aceptar ≥1 token capitalizado Unicode; cualquier token del nombre en el doc | alta |
| research_v3.py:1135 | El apellido transliterado está literal en el documento | 2 | Doc ruso + nombre en latín (o viceversa) → «el apellido no está en el documento» | comparar con `_nz`/alfabeto del doc, o exigir solo `cita_literal` (ya en 1090) | media |
| research_v3.py:1283 `same_person` | Mismo apellido y 3 primeras letras del nombre | 2 | `person_key` vacío (cirílico) → nunca dos personas son la misma; «gon» (Gonçalves) choca con «González» | depende del fix de `person_key` | media |
| research_v3.py:1304 `same_fact` citas | `person_key(autor)[1]` para dedupe | 2 | Autores en cirílico → «» == «» → citas de distintas personas se fusionan | ídem | media |
| research_v3.py:1557-1577 `verify_pool` | `sur` vacío → `autor_cerca` True trivial; «verificada» pero `is_named_person`=False | 2 | Cirílico: ningún testigo «con nombre»; `own_verified` nunca aplica → 0 elegibles → gate ROJO | ídem | alta |
| research_v3.py:1639, 1647 `metrics` | `is_named_person` decide «testigo con nombre» | 2 | Ídem | métrica informativa; no filtrar por alfabeto | media |
| research_v3.py:1678-1680 `_names_in` regex `[^a-z0-9ñ]+` | Texto y nombres en latín ASCII | 2 | Cirílico/griego: `n_datos` siempre 0 → `elegible_humano` imposible sin cita verificada | `[^\w]+` | alta |
| research_v3.py:1697 `presence_v3` `\b…\b` sobre `_ascii(text)` | Límites latinos; `_ascii` no translitera | 2 | Cirílico → `presente_en` vacío para todos | lookaround `(?<!\w)…(?!\w)` como `place_regex` | media |
| research_v3.py:1227-1229 `_TITLES_BASE` | Grados EN/ES de policía/cárcel (sheriff, deputy, alguacil, sgt) | 1 | Rusia (товарищ, академик), Italia (ing., dott., on.), Alemania (Herr, Frau), Francia (M., Mme) → tratamiento como nombre de pila | parametrizar `tratamientos` desde el perfil; base mínima mr/mrs/dr/jr/sr | media |
| research_v3.py:1233 `_NOT_PERSON_BASE` «officers\|oficiales» | Resto de Orleans | 1 | Redundante con perfil | borrar | baja |
| research_v3.py:1254 `set_vocabulario` | Cada palabra ≥3 letras de `roles_*` se vuelve «título» que `person_key` borra | 1 | Roles en cirílico nunca matchean | solo formas singulares | baja |
| research_v3.py:1257 `grupo = r"(s\|es)$"` | Plural = -s/-es (ES/EN) | 2 | Italiano (-i/-e), ruso (-ы/-и), alemán (-en/-er) | pedir `singular`/`plural` en `VOCAB_SCHEMA` | baja |
| research_v3.py:1235, 1241 `_COUNT_BASE`/`_count_re` | Conteo = número ≥1,000 o con separador de miles, pegado a sustantivo | 3/4 | Ycuá (~400 muertos), asilos (cientos) → sin cifra canónica | piso del perfil o métrica | media |
| research_v3.py:1499, 1743 `>= 1000` | Conteo relevante ≥ 1000 | 3 | Ídem | parametrizar `conteo_minimo` o borrar | media |
| research_v3.py:1467 `CANON_RATIO=1.25`, 1727 `POP_BAND=(0.6,1.4)` | Bandas calibradas sobre 6,295/6,375/6,500/8,000 presos | 3 | Kyshtym: 10,000 vs 270,000 expuestos | métrica / documentar | baja |
| research_v3.py:1213 `OFFICIAL_TIPOS` + 1513, 1755 | Solo fallo/informe_oficial/foia son «oficial» | 5 | URSS 1957 (lo autoritativo es IAEA/académico), asilo 1900 (libros) → nunca cifra oficial | `tipos_oficiales` del perfil o académico como oficial si no hay otro | media |
| research_v3.py:1350 `_doc_rank` `.endswith(".gov")` | Gobierno = `.gov` (EE. UU.) | 5 | `.gov.it`, `.gov.py`, `.gob.es`, `.gouv.fr`, `.ru` no se priorizan | `(\.\|^)(gov\|gob\|gouv\|gc)\.` o perfil | media |
| research_v3.py:38-39 `TIPOS_FUENTE` `foia` | Concepto legal de EE. UU. | 5 | El prompt pide «FOIA» para Rusia/Italia | borrar «FOIA» del prompt | baja |
| research_v3.py:112 prompt R1 «Buscá en INGLÉS y en {lugar}» | Inglés siempre | 5 | Paraguay/España/Italia: mitad del cupo en inglés | `idiomas_research` en el perfil | media |
| research_v3.py:113-115, 127-131 focos | «prensa local de la primera semana», «fallos, demandas, FOIA» | 4/5 | Evento prolongado; régimen sin prensa libre (URSS 1957) | focos por `tipo_evento` | media |
| research_v3.py:123, 198, 331 ejemplos JSON `"anio":2006,"idioma":"en"` | Valores de Orleans que el modelo copia | 6 | Temperatura 0.7 pega 2006/en | `"anio":0,"idioma":"xx"` | baja |
| research_v3.py:601 `Accept-Language: en,es;q=0.8` | Páginas multilingües sirven inglés | 5 | .ru/.it/.de devuelven EN | del perfil | media |
| research_v3.py:619 `{year or 2006}0901` | Fallback Katrina | 6 | Cosmético | año del evento | baja |
| research_v3.py:450-459 `_STOP` + `detect_lang` | Idiomas: en/es/fr/it | 2/5 | Ruso, alemán, portugués, polaco → `idioma:"?"` ✔ en cada ítem | detección por script + stopwords del perfil, o `langdetect` | media |
| research_v3.py:586-590 `fuente_idioma` | Alfabeto → ru/el/ar/he | 2 | Título transliterado → «en»; ucraniano/búlgaro → «ru» | `idioma_local` como mapeo | baja |
| research_v3.py:557 `_TAIL_HEAD` | Títulos de cola en inglés | 2/5 | «Notas», «Bibliografía», «Примечания» → recorta cuerpo | formas por idioma del perfil | baja |
| research_v3.py:554 `dehyphenate` `[A-Za-z]` | Notas pegadas solo tras latín | 2 | Cirílico: `cita_literal` no coincide | `(?<=[^\W\d_][.,;:])` | baja |
| research_v3.py:437 `slugify` `[a-z0-9]+` sobre `_ascii(titulo)` | Título latino | 2 | Dos fuentes rusas del mismo sitio y año → MISMO slug ✔ → el segundo pisa el archivo y el txt del primero; `same_document` lo marca duplicado | `f["id"]` en el slug o `unidecode` | alta |
| research_v3.py:218 `_path_tokens` `[a-z0-9]+` | URL ASCII | 2 | URL cirílica → `url_similarity` 0 → ficha descartada | `\w+` | baja |
| research_v3.py:40-46 `MIN_FUENTES=8, MAX_FUENTES=20, MAX_DESCARGAS_OK=10, MIN_DOC_CHARS=3000, EVENT_CHECK_CHARS=5000` | Documentos largos tipo ACLU/DOJ | 3 | Decretos/recortes <3,000 chars se tiran; libro con 5,000 chars de portada → «no nombra el evento» → fuera (1342) | perfil o métrica (anotar, no descartar) | media |
| research_v3.py:830-836 PDF enlazado | El PDF nombra el evento en 5,000 chars | 4 | Informe con 10 páginas de portada | ídem | baja |
| research_v3.py:1042-1044 `FOCUS_DENSITY = 1/20000` | ≥1 mención/20k chars | 3 | Libro donde el lugar se nombra poco | métrica | baja |
| research_v3.py:1008, 1015, 1104, 1138 | Cronología AAAA-MM-DD/AAAA-MM; `fechas_presente` solo días | 4 | «otoño de 1908», «finales de los 50» no entran; año solo no cuenta en el gate | aceptar `AAAA` y rangos; completitud a métrica | alta |
| research_v3.py:1107-1110 | Año de `cita_literal` = año de `fecha` | 4 | «57-го года», calendario juliano, «el año pasado» | descartar solo si difiere en >1 | baja |
| research_v3.py:1011 ejemplo «un preso de Templeman III» | Vocabulario Orleans en R3 para CADA documento | 1/6 | El modelo copia «preso de…» en un asilo o en Mayak | ejemplo con `roles_testigo[0]` | media |
| research_v3.py:1012, 1016 `_roles` fallback | Si no hay roles, prompt vago | 1 | Perfil fallido | que `seed_vocabulario` no falle en silencio | baja |
| research_v3.py:1014-1016 `antagonista` = «persona con nombre propio» | Antagonista persona | 4 | Kyshtym, Vajont, asilo, Ycuá (empresa) → nunca true; digest no lista antagonistas | antagonista institucional | media |
| research_v3.py:1945-1949 `PROFILE_SCHEMA` `anio_evento` INTEGER | Un solo año | 4 | Pennhurst 1908-1987, Gulag, Vajont 1959-1963 → fuera de ±20 años = «contaminación» | `anio_inicio`/`anio_fin` | alta |
| research_v3.py:2087 `year = prof.get("anio_evento") or date.today().year` | Fallback año actual | 4 | `anio_evento` 0 → todo anterior a 2006 es contaminación | fallar explícito | media |
| research_v3.py:1309-1319 `ITEM_YEARS=20`, `LATE_OK`, `EARLY_OK` | ±20 años; excepciones solo es/en/it | 2/3/4 | Ruso, alemán, francés: el juicio (`суд`, `Prozess`, `procès`) se descarta | perfil o métrica (`lejano`) | alta |
| research_v3.py:1439-1440, 1875 | «El evento» es un año | 4 | Multi-año: cronología del digest vacía | rango del perfil | media |
| research_v3.py:1121, 910, 895; verify_quotes.py:138 | Palabras por espacios | 2 | Chino/japonés: cita = 1 «palabra» → descartadas | contar caracteres | media |
| research_v3.py:1972-1983 `seed_vocabulario` | «en una cárcel: preso, guardia, oficial», «sheriff, el ministerio, el dueño»; inglés siempre | 1/5/6 | Ancla en cárcel | ejemplos neutros; inglés opcional | media |
| research_v3.py:2020 `seed_profile` | «inglés (Nueva Orleans, EE. UU.)» | 6 | Sesgo menor | neutro | baja |
| research_v3.py:2072 `lugar_idioma = seed.get("idioma_local")` | Seeds traen `idioma_local` (no lo traen) | 5 | Letra muerta | borrar o documentar | baja |
| research_v3.py:2074 `discover_sources` sin `pistas` | Pistas nunca se pasan en producción | — | Escrito para Orleans (F7) | borrar o conectar | baja |
| evidence_pool.py:158-162 `is_person` | Nombre = 2 palabras latinas Title Case | 2 | «V.M. Osetrov» → False ✔, «MARLIN GUSMAN» → False ✔, «Rasputin» → False ✔, cirílico → False ✔ | iniciales, all-caps, 1 palabra con `rol`; Unicode | alta |
| evidence_pool.py:154-155 `_ORG_WORDS` | Organizaciones de EE. UU. | 1/6 | Faltan Minatom, SADE, ENEL, comisión | `instituciones` del perfil | baja |
| evidence_pool.py:166-168 `_person_key` {jr, sr, sheriff, teniente, general, alcaide, capitan} | Cargos de cárcel; latino | 1/2 | `acting_filter` (sí corre en v3): cirílico → `person_acts` False → descartado | unificar con `research_v3.person_key` | media |
| evidence_pool.py:233 `_NOT_VERB` «sheriff»; 297 `_COMMON_HEADS` | Orleans | 1/6 | «Director Smith», «Ingeniero Biadene» | perfil o borrar | baja |
| evidence_pool.py:234-245 `_verb_like` | Verbo español tras apellido | 2 | Apellido cirílico (`\b`) | depende de `_person_key` | baja |
| evidence_pool.py:337-347 `build_prompt` | «un preso de Templeman III», «preso, guardia…» | 1/6 | Solo v2 | perfil | baja (v2) |
| evidence_pool.py:584 `_COUNT_NOUN`; 579 `_OFICIAL` | Conteo de cárcel | 1 | Solo v2 | borrar o perfil | baja (v2) |
| evidence_pool.py:37, 170 docstrings | Orleans | 6 | Nada | neutralizar | baja |
| evidence_pool.py:499 `GEO_MAX_KM=400`; 559 siglas `[A-Z]{2,5}` | ≤400 km; sigla latina | 2/3 | «ПО Маяк» no es sigla | métrica; Unicode | baja |
| verify_quotes.py:40 `TEMA: la Prisión Parroquial de Orleans…` | Tema hardcodeado | 6 | Cualquier tema si se reusa | `seed_title` o borrar | media (dormida) |
| verify_quotes.py:35-36 «original probablemente en inglés» | Inglés | 5 | Paraguay, Italia, Rusia | perfil | baja (dormida) |
| verify_quotes.py:102-104 `_named` | Mayúscula latina, dos palabras | 2 | Cirílico → False ✔ | `istitle()` Unicode | baja (dormida) |
| verify_quotes.py:155-162 `doc_ok` «≤ evento + 20 años»; fecha obligatoria | 20 años; sin año = inválido | 3/4 | Libro 2010 sobre 1957 | borrar (reemplazado en v3) | baja (dormida) |
| pool_gate.py:21-26 + video_length.py:26-29 | 150 / 8 / 2 / 10 | 3 | URSS 1957, asilo 1900, represa → ROJO sistemático | métrica por `tipo_evento`; perfil fija `gate_*` | alta |
| pool_gate.py:44 `fullmatch(\d{4}-\d{2}-\d{2})` | Solo día completo | 4 | AAAA-MM no suma | contar AAAA-MM (y AAAA si prolongado) | alta |
| pool_gate.py:22-25 motivos | Pocos datos = pocas descargas | — | Engaña al analista cuando la causa es alfabeto | mensajes neutros | baja |

## ANEXO 2 — Jueces (evidence, m05, guion_v3_reglas), video_length, ficha (auditor 2)

| archivo:línea | qué asume | cat | qué tema lo rompería | arreglo propuesto | severidad |
|---|---|---|---|---|---|
| evidence.py:58 | `_surname`: apellido = última palabra con mayúscula de `[A-Za-zÁÉÍÓÚÑáéíóúñ]+`; descarta "sheriff" | 1,2 | Cirílico → devuelve el nombre entero; «van der Berg», «De Michele»; apellido primero; ü/ö/ß | `\w+` Unicode + `person_key`/variantes del pool; sacar "sheriff" | alta |
| evidence.py:59 | títulos a excluir = {"jr","sr","sheriff"} | 1 | "Dr.", "Coronel", "General", "Ing.", "Dottore" → título como apellido | reutilizar `_TITLES` de research_v3 | media |
| evidence.py:63 | `_NUM_UNIT`: `$` opcional, separador `.`/`,` | 5 | "G. 4.500", "€", "руб.", "4 500" | canonizar como `ficha_caso._canon`; unificar con `_num_key` | media |
| evidence.py:72, 245, 288 | año = `(19\|20)\d\d` | 4 | Siglo XVIII/XIX: el año cuenta como cifra, infla densidad | `1[0-9]{3}\|20\d\d` o rango del seed | media |
| evidence.py:74-76 | unidades: pies, metros, millones, dólares, años, días, pisos, horas | 5 | curies, Sv, röntgen, toneladas, km², m³, guaraníes, camas, °C | lista del perfil o aceptar cualquier palabra corta | media |
| evidence.py:118-120 | `_NUMWORD` solo español | 2 | Cita literal en otro idioma | limitación aceptada | baja |
| evidence.py:133 | `norm` NFD destruye "й" → "и" | 2 | «Майяк», «Озёрск» cambian al normalizar; rompe `_surname` y `_content` | quitar diacríticos solo latinos o NFC | media |
| evidence.py:159, 171 | `_content` = `[a-zñ]{5,}` | 2 | Cirílico → vacío → `used_in` acepta cualquier oración con la fecha o falla | `[^\W\d_]{5,}` | alta |
| evidence.py:168-175 | evento «usado» solo si suena la fecha con día en la oración | 4 | Procesos sin día exacto: nunca `is_hard` → densidad baja → bloquea | granularidad mínima del perfil | alta |
| evidence.py:208, 210 | `is_hard`: cronología solo `AAAA-MM-DD` | 4 | Ídem | ídem | alta |
| evidence.py:218-219 | `_VAGUE_W` español; `[A-Za-zÁÉÍÓÚÑÜáéíóúñü]+` | 2 | Cirílico no tokeniza; alemán todo mayúscula = propio | `\w+` Unicode | baja |
| evidence.py:224 | docstring "Prisión de Orleans", "nivel del pecho" | 6 | — | borrar | baja |
| evidence.py:251 | comentario «29 de agosto de 2005» | 6 | — | borrar | baja |
| evidence.py:256, 272-279 | fecha hablada = `\d{1,2} de MES`; sin "primero de" | 2,4 | «primero de agosto» no se detecta; guion_v3_reglas sí → jueces inconsistentes | una sola `DATE_RE` compartida | media |
| evidence.py:266, m05:468-469 | año por defecto único | 4 | Casos que cruzan Año Nuevo (Kyshtym sep 1957 → 1958) → «fundiste fechas» | inferir por cercanía o rango del seed | media |
| evidence.py:296-297 | docstring "650,000 … D50 y D72" | 6 | — | borrar | baja |
| evidence.py:302 | cifra "grande" ≥ 3 dígitos | 3 | Horas 100-999, números de celda → falsos «mismo hecho» | métrica | baja |
| evidence.py:309 | solapamiento ≥ 50 % | 3 | Cirílico → `_content` vacío → False siempre | métrica | baja |
| evidence.py:312-313 | `_COMMON_CAPS` = arrestado, turista, recluso, demandante, sheriff, alcaide, huracán, adjunto, teniente | 1 | "Director", "Médico", "Ingeniero", "Enfermera" no se corrigen; «Huracán Katrina» se baja mal | borrar; derivar de `rol` del pool | media |
| evidence.py:318 | docstring "Raphael Schwarz", "Sheriff Gusman" | 6 | — | borrar | baja |
| evidence.py:323 | `[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+` | 2 | Cirílico/alemán no se procesan | `str.isupper()` | baja |
| evidence.py:340 | ids `[DTQPL]` vs ficha `[DTQPLF]` | 4 | Inconsistencia | constante compartida | baja |
| evidence.py:368-378 | antagonista = persona con flag; «principal» = apellido más repetido | 4 | Estado/Mayak, SADE, institución; cirílico → `blob.count` 0 | lugar/organización; `name_terms` | alta |
| m05_narrative.py:7 | "(Orleans v1 ≈ 0.7)" | 6 | — | borrar | baja |
| m05_narrative.py:17, 555 | «Interestatal 10» en feedback al modelo | 6 | Texto de Orleans al modelo | genérico | baja |
| m05_narrative.py:31 | `DENSITY_MIN = 2.0` | 3 | Pool chico o lento no alcanza aunque el guion sea bueno; calibrado Orleans | derivar del pool o métrica | alta |
| m05_narrative.py:32 | `MAX_DATO_CAPS = 2` | 3 | Un dato central legítimo en 3 caps (1.917 muertos Vajont) | métrica blanda / excepción canónicas | media |
| m05_narrative.py:33 | `TRIGRAM_MAX = 0.05` | 3 | «planta química Mayak» dispara 3-gramas | excluir entidades | media |
| m05_narrative.py:34-37 | `ADJ_MIN=2.0 / ADJ_MAX=4.0` calibrados Orleans | 3 | Temas técnicos con pocos calificativos → piso obliga adjetivos | métrica blanda; quitar piso | media |
| m05_narrative.py:40-44 | `FORBIDDEN_FILLER`: "infierno flotante", "el monstruo", "manto de", "ecos de" | 1 | «manto de nieve», «ecos de la explosión» bloqueados | borrar entradas de caso | media |
| m05_narrative.py:51-70 | `_ADJ_LIST` húmedo, pútrido, estancado, turbio, cautivo, atrapado | 1,3 | Lista de inundación/encierro; en Kyshtym mide otra cosa | métrica; sufijos + lexicón general | media |
| m05_narrative.py:72-80 | `_NOT_ADJ` teniente, sargento, comandante, paciente, residente | 1 | "combatiente", "disidente", "docente" contados como adjetivos | lista cerrada; métrica | baja |
| m05_narrative.py:84, 180, 198, 213, 453 | nombre propio = `[A-Za-zÁÉÍÓÚÑÜáéíóúñü]`, `[A-ZÁÉÍÓÚÑ][a-záéíóúñ]` | 2 | Cirílico, ß, polaco → `filler_run` cuenta relleno; `date_problems` falsos | Unicode en todos | alta |
| m05_narrative.py:125-133 | `_date_paraphrased` acepta "ese domingo/esa noche"; comentario "F10 (Omar: una fecha literal por cap…)" | 4,6 | Eventos de varios días: «ese domingo» no identifica nada; asume mismo día sin verificar | paráfrasis válida solo si hay un solo día-evento | media |
| m05_narrative.py:149-157 | `silent_names` con `_surname` + `\b` | 2 | Cirílico | `name_terms` | media |
| m05_narrative.py:211-225 | `names_with_role`: primera y última palabra en mayúscula; rol = 3 palabras ≥4 letras | 2,4 | Patronímicos; mononimios → falla siempre; partículas | `name_terms`/`person_key` + variantes; nombre único | alta |
| m05_narrative.py:268-269, 308 | antagonista = persona con apellido | 4 | Sin antagonista humano | generalizar | media |
| m05_narrative.py:366-370 | `_num_key`: "4.6" decimal; coma = miles | 5 | Europa: "4,6" → "46" (falso «inventado») | decidir por longitud del grupo como `ficha_caso._num_forms` | media |
| m05_narrative.py:380-393 | `invented_numbers`: cifra válida si está en pool/facts | 5 | «20 millones de curies» vs "20,000,000"; "16:22" → 16 y 22; «Chelyabinsk-40» → 40 | reutilizar `ficha_caso.numbers()` | media |
| m05_narrative.py:422-433 | `non_canonical`: `\d[\d,]*\d` solo coma | 4,5 | Kyshtym: canónica es MCi/km²; "1.917" con punto no captura | separador; skeleton marca qué es «conteo» | media |
| m05_narrative.py:457-458 | `DATE_MATCH_MIN=0.5`, `DATE_MATCH_WORDS=2` | 3 | Eventos cortos → «fundiste fechas» | métrica | baja |
| m05_narrative.py:469 | año por defecto "2000" | 4 | Siglo XIX | del seed | baja |
| m05_narrative.py:494-510 | `false_quotes`: comillas = cita del pool; ≤3 palabras ok; ejemplo "Templeman III" | 1,6 | Términos de 4+ palabras entre comillas; **citas traducidas no coinciden con `cits` → TODA cita traducida es «falsa»** | comparar contra `traduccion` de la ficha | alta |
| m05_narrative.py:498 | docstring «El sheriff de la cárcel declaró…» | 6 | — | borrar | baja |
| m05_narrative.py:559-560, 627, 633-634 | feedback: «ese lunes», «la celda», «sheriff Marlin N. Gusman basta una vez» | 6,1 | Guionista de Kyshtym recibe celdas y sheriff | sin nombres propios de Orleans | media |
| m05_narrative.py:602-608 | orden por `fecha` string; `None` rompe `sorted` | 4 | Fechas mixtas/None | ignorar sin fecha | baja |
| m05_narrative.py:609-616 | cita válida = comillas + `_surname(autor)` a ±150 chars | 4,2 | «Informe TASS», «Comisión», «testigo anónimo»; autor cirílico | `tipo_autor` organización/anónimo | media |
| guion_v3_reglas.py:6-9, 374 | "la decisión del sheriff", "rol preso/guardia" | 1,6 | — | borrar | baja |
| guion_v3_reglas.py:47-48 | `_DATE` año `(19\|20)\d\d`; sin "primero" | 2,4 | Siglos XVIII-XIX; inconsistente con DATE_RE (214) | unificar con evidence | media |
| guion_v3_reglas.py:73-93 | `JUDGMENTS`: "no eran considerados humanos", "como animales", "el sistema los abandonó", "fue una masacre", "esperar un milagro" | 1 | Orleans/Ycuá; Kyshtym («encubrimiento», «sacrificados») no detecta; "castig\w*" bloquea hecho documentado | solo patrones estructurales; blanda | media |
| guion_v3_reglas.py:89-92 | "F10 (notas del analista sobre Ycuá)" | 6,1 | — | borrar | baja |
| guion_v3_reglas.py:115-130 | `full_name_problems`: primera + última palabra latina | 2 | Cirílico → silencio; apellido doble; una palabra | Unicode; `variantes` | media |
| guion_v3_reglas.py:143, 153 | `_tokens` `[a-z0-9ñ]+`; entidad latina | 2 | Cirílico/alemán | Unicode | media |
| guion_v3_reglas.py:135-139 | `_STOP` solo español | 2 | Citas en otro idioma inflan 3-gramas | aceptar | baja |
| guion_v3_reglas.py:214-218 | `DATE_RE` + `DATE_PARAPHRASE` "ese domingo/…/esa noche" | 4 | Un día-evento asumido; «ese invierno», «ese año» no se aceptan | paráfrasis derivada de granularidad del seed | alta |
| guion_v3_reglas.py:215, 249-265 | `DATE_MAX_PER_CAP = 1`; fecha con año una sola vez | 3,4 | Kyshtym: cap de consecuencias necesita 2-3 fechas | `fechas_por_cap` del seed o blanda | alta |
| guion_v3_reglas.py:221 | `replace_repeated_dates(day="1 de agosto")` + "ese domingo" fijo | 4,6 | Default Ycuá; Vajont fue miércoles → **texto FALSO** sin parámetro (guion_v4 ya tiene la buena) | borrar | alta |
| guion_v3_reglas.py:222-246 | docstring «el 1 de agosto» → «ese domingo», «2004» | 6 | — | borrar con la función | baja |
| guion_v3_reglas.py:257 | feedback: «ese domingo» | 4,6 | Inyecta «domingo» a cualquier caso | «ese día» | media |
| guion_v3_reglas.py:272 | `_SENT` corta solo ante mayúscula latina | 2 | Oración con cirílico o cifra inicial no corta → métricas mal | `\S` o `\p{Lu}\|\d` | media |
| guion_v3_reglas.py:281-284 | `_ROLE_PRESO` / `_ROLE_GUARDIA` (recluso, preso, interno, detenido, sobreviviente, inmate / guardia, oficial, alguacil, carcelero, celador, sargento, capitán, teniente, deputy, vigilante, custodio) | 1 | Totalmente Orleans; manicomio «interno» = preso; barco/base «capitán» = guardia; falsos «en el pool es preso» | borrar la dicotomía; comparar rol del pool con rol de la narración sin clases | alta |
| guion_v3_reglas.py:287-293 | `role_class` solo "guardia"/"preso"/None | 1,4 | `role_problems` exige esta clase para TODAS las personas y citas | borrar / generalizar | alta |
| guion_v3_reglas.py:296-301 | `_ROLE_BEFORE`/`_ROLE_AFTER` desde las listas | 1 | Ídem | borrar con la regla | alta |
| guion_v3_reglas.py:306, 323 | «la reclusa Rhonda Ducre», «Brady Richard, un preso» | 6 | — | borrar | baja |
| guion_v3_reglas.py:337-338 | autor ↔ persona por última palabra | 2,4 | Cirílico; hermanos | `name_terms` | media |
| guion_v3_reglas.py:369-370 | `_ANON_VOICE`: "según alguien", "una voz oficial" | 4 | «una fuente oficial soviética» ES correcto | solo si antagonista es persona | media |
| guion_v3_reglas.py:374-395 | antagonista persona; `nombre.split()[-1]`; exige apellido en el cap | 4,2 | Institucional; «Славский» vs «Slavski» → hard fail en cada cap | organización; variantes + transliteración | alta |
| guion_v3_reglas.py:400-411 | `photo_problems` prohíbe foto, fotografía, imagen, cámara, retrato | 1 | «cámaras de los dosímetros», «imagen satelital de la CIA», «cámara de gas» son hechos | solo "foto\|fotografía\|fotógrafo" | media |
| guion_v3_reglas.py:430-442 | ancla del gancho: ≤10 palabras, año `(19\|20)\d\d`, lugar ≥5 letras de `lugares` | 2,4 | Siglo XIX; lugar cirílico → nunca ancla → **hard fail SIEMPRE**; «Oslo» | año `1\d{3}\|20\d\d`; Unicode; ≥4 o variantes | alta |
| guion_v3_reglas.py:449-450 | «Nueva Orleans, agosto de 2005.» como modelo | 6 | Copia literal | lugar/año del seed | media |
| guion_v3_reglas.py:464 | docstring «Cientos de familias…» | 6 | — | borrar | baja |
| video_length.py:5 | 2.05 palabras/s medido en una voz/caso | 3 | Otra voz, cifras técnicas | medir y retroalimentar | baja |
| video_length.py:26-29 | `gate_datos=150, gate_citas_verificadas=8, gate_elegibles=2, gate_eventos_fecha=10` | 3,4 | Poca documentación o fechas vagas → rojo | perfil (`tipo_evento`) o relajar eventos a cualquier granularidad | alta |
| ficha_caso.py:5-6 | "los 509 ítems de Ycuá" | 6 | — | borrar | baja |
| ficha_caso.py:39 | "(Ycuá F12)", "(Orleans F14)" | 6 | — | historial | baja |
| ficha_caso.py:133 | «cronologia: los eventos **del día**» | 4 | Kyshtym, manicomio, Vajont → el modelo descarta la cronología larga | «con la granularidad que el pool tenga» | alta |
| ficha_caso.py:136 | giros: «una puerta que no abre» | 1 | Sesga | generalizar | baja |
| ficha_caso.py:143 | ejemplo humano: Pearl Cornelia Bland, 398 dólares, huracán, oficiales, ids D301/Q88/D512 | 6,1 | Sesgo a presos/huracán | ejemplo abstracto o del pool | media |
| ficha_caso.py:146 | «El sheriff rechaza la ayuda…» | 6,1 | Ídem | reemplazar | media |
| ficha_caso.py:149 | «Celdas de Templeman III, 30 de agosto», «aguas residuales…»; fija `donde` = «lugar, DD de MES» | 6,1 | Incompatible con eventos sin día | reemplazar; `donde` sin fecha | media |
| ficha_caso.py:152 | «La lista de evacuados no incluye a 517 reclusos.» | 6,1 | Ídem | reemplazar | baja |
| ficha_caso.py:154 | cifras «(muertos, heridos, huérfanos…)», unidades «(°C, guaraníes…)» | 1,5 | Ycuá; faltan curies, km², rublos | del seed | baja |
| ficha_caso.py:160-161 | criterios 3-4: «cómo estaban las puertas» | 1 | Nuclear: lo disputado es una cifra | generalizar | baja |
| ficha_caso.py:240 | `_HORA` HH[:.h]MM | 5 | Horas en letras | aceptar | baja |
| ficha_caso.py:242 | `_ID` `[DTQPLF]\d{2,3}` excluido de cifras | 4 | «T34», «F15» reales se ignoran | solo ids del pool | baja |
| ficha_caso.py:265-269 | `_canon` quita "US$", "G." | 5,6 | Faltan €, £, ₽, руб, Lit.; «º» | `\p{Sc}` + «º» | media |
| ficha_caso.py:270, 304 | `_SCALE` mil/millones | 5 | billones, millardos, centenares | generalizar | baja |
| ficha_caso.py:271-280 | números en letras solo español | 2 | Citas en ruso/inglés con cifras en letras → descartadas | comparar `traduccion` | media |
| ficha_caso.py:312-313 | `word_numbers` `[a-z]+` | 2 | Cirílico vacío | aceptar | baja |
| ficha_caso.py:425-427 | `sentidos_problems`: raíz `[a-zñ]+` de 5 letras debe estar en los ids | 2,3 | Pool en ruso + `sentidos` en español → NUNCA coincide → **todas las escenas descartadas** | comparar contra traducción; o solo ids si idioma ≠ es | alta |
| ficha_caso.py:455-456 | `personas_descartadas`: `nom.split()[-1]` en texto de ids | 2 | Cirílico vs transliteración; «Jr.», «III» | `person_key`/variantes | media |
| ficha_caso.py:479 | `norm(base)` literal en `norm(src)` | 2 | Comillas rusas «» / „", guiones distintos | unificar comillas/guiones | media |
| ficha_caso.py:94-97, 657-658 | `texto` original + `traduccion`; `id_texts` usa traducción, pero m05.false_quotes y guion_v3.role_problems/hook_problems comparan contra `pool.citas[].texto` | 2,4 | Kyshtym: `false_quotes` marca TODAS las citas; `role_problems` no encuentra la cita | jueces leen `id_texts(ficha)`/`traduccion` | alta |
| ficha_caso.py:232, 154-155 | escenas 8–15, hechos 60–80 (nivel 1: 12–20), citas 15–25, humanos 2–4, giros 3–6 fijos | 3 | Pool chico (120 ítems) → el modelo inventa o repite | % de ítems, acotado | media |
| ficha_caso.py:133, 156 | `aproximada` solo si no coincide en ≥2 fuentes | 4 | Una sola fuente primaria → toda la cronología «aproximada» | según nº de fuentes | baja |

## ANEXO 3 — Columna, escaleta, skeleton, guion v4, editor, partición, tts, runner, config (auditor 3)

| archivo:línea | qué asume | cat. | qué tema lo rompería | arreglo propuesto | severidad |
|---|---|---|---|---|---|
| m01a_columna.py:56-70 | `<ejemplo>` del SYSTEM es Orleans entero: Reed, Templeman III, HOD, Broad Street, 517, Pearl Bland/398, Iris Hardeman, Nagin, Reyes, «donde pertenecen» | 1,5 | Contamina «qué pasa» con cárcel/huracán; cifras ajenas → bloqueante (a) | ejemplo sintético sin cifras ni nombres reales, o por tipo de caso | media |
| m01a_columna.py:45 | «Un humano… del cap 1 al 7» — una persona con arco | 4 | Kyshtym (sin testigo con arco), represa (anónimos), base (colectivo) | humano colectivo o relevo (escaleta v1 ya tiene `colectivo`) | alta |
| m01a_columna.py:47-52 | Caps fijos: 2 «vida antes», 6 «los cuerpos, la búsqueda, cifras oficiales», 7 «lo que la justicia dijo» | 4 | Manicomio (sin pico ni juicio), Kyshtym (sin búsqueda ni justicia) | oficio por función, no contenido | alta |
| m01a_columna.py:46,74 | «cinco o seis personas»; «La ficha tiene 90 personas» | 3 | 3 personas (Kyshtym) o 15 imprescindibles (juicio) | métrica; borrar cifra | baja |
| m01a_columna.py:51 | «las cifras oficiales (que van a pantalla)» | 4 | Cifras clasificadas | «si hay» | baja |
| m01a_columna.py:52 | Cap 7 termina con cita del humano o pregunta de la ficha | 4 | Humano sin cita | que la pregunta no dependa de la ficha | baja |
| m01a_columna.py:27,210 | `CAPS = 7` (también escaleta 553, skeleton, m01d) | 3,4 | Contrato de río abajo | dejar | baja |
| m01a_columna.py:162-191 | `_tokens` = `[a-z0-9ñ]+` sobre `ev.norm` | 2 | Cirílico («Курчатов»), ł/ø/ß → tokens vacíos → «humano no es una persona de la ficha» → **ColumnaError (PARADA)** | `\w` Unicode | alta |
| m01a_columna.py:189 | `set(t) <= set(tn)`: «Paiva» matchea la primera persona | 2 | Juan Pío Paiva / Daniel Paiva; padre/hijo | ≥2 tokens o id | media |
| m01a_columna.py:139 | Ids `[PDTQ]\d{1,4}` | 5 | Otros prefijos | dejar | baja |
| m01a_columna.py:315 | `to_markdown` escribe «gpt-6.1-sol high» fijo | 5 | Otro modelo | leer el real | baja |
| m01a_escaleta.py:85-87 | `ADMIN_TERMS` (indemnización, generador, registro, demanda, informe, autoridades, evacuación, tribunal) prohibidos en pregunta de pantalla | 1,6 | «¿Por qué tardaron la evacuación?» es LA pregunta de Kyshtym | borrar o métrica también en v1 | media |
| m01a_escaleta.py:91-96 | `ABSTRACT` incluye «muerte», «vida», «silencio», «poder», «memoria» | 6 | «El silencio total de la sala» rechazada | métrica; recortar | baja |
| m01a_escaleta.py:100-107 | `NUM_WORDS`/`has_figure` con «mil», «cien», «once» | 2,3 | «Once» (barrio), «Mil» (apellido) | marginal | baja |
| m01a_escaleta.py:148-151 | SYSTEM v1 «misterio» vs v2 «historia oscura» | 6 | — | unificar | baja |
| m01a_escaleta.py:153-177 | FEWSHOT Sago/Triangle con cifras («6:26», «trece hombres», «noveno piso») | 1 | Copia «sexto piso» → cifra inventada | quitar cifras del ejemplo | baja |
| m01a_escaleta.py:208-211 | Regla 5: «un preso de Templeman III, 19 años, según la ACLU» | 1,5 | Cárcel en prompt v1 | «una persona del lugar, edad, según la fuente» | baja |
| m01a_escaleta.py:217-218 | Regla 7: «agua negra… celda» | 1 | Ídem | generalizar | baja |
| m01a_escaleta.py:226-228 | Regla 9: «¿Por qué nadie abrió las celdas?», «¿Dónde están los 517?» | 1,5 | Copia «517» | borrar cifra | media |
| m01a_escaleta.py:239-240, 948-949 | «(«un preso», «una guardia»)» para anonimizar (también `writer_instructions`) | 1 | Kyshtym «un operario», manicomio «una enfermera» | «una persona que estuvo ahí, por su rol» | media |
| m01a_escaleta.py:69-70,80-83,189-190 | beats 7–14, ≥2 por cap 2–6, `WORDS_TOL` 15 %, intensidad 1–5, `MIN_HUMAN_CAPS` 3, `Q_MAX_WORDS` 8, `MAX_APOYOS_FICHA` 6 | 3 | Amarilla a 8 beats pero 7 caps × 2 = 12 | todo a `video_length`/perfil | baja |
| m01a_escaleta.py:202-205, 594-616 | Curva: no baja hasta el pico, respiro 1 después, flash-forward solo beat 1 | 4,6 | Crónica con varios picos | ya métrica v2 | baja |
| m01a_escaleta.py:214-215, 657-668 | Humano en ≥3 caps y «antes del cap 3» | 4 | Testigo que aparece al final | ya métrica v2 | baja |
| m01a_escaleta.py:216, 668-674, 1178 | **Antagonista obligatorio**: persona (v1) o institución literal (v2); bloqueante | 4 | Sin culpable; variantes («Mayak» / «Combinado 817» / «Minsredmash») → PARADA | opcional (`ninguno`) + variantes | alta |
| m01a_escaleta.py:1189-1199 | `institucion_de_la_ficha`: solo artículos castellanos; nombre literal | 2 | Sin abreviatura | variantes de la ficha | media |
| m01a_escaleta.py:263, 642-651, 1265 | Apellido = `split()[-1]`; **substring sin `\b`** | 2 | «Gusman Jr.» → «jr.»; «de la Cruz» → «cruz»; «Li» matchea «lista» | una sola función de apellido (hay 4) + `\b` | media |
| m01a_escaleta.py:627-629 | Colectivo: «nombre inventado» solo latín | 2 | Cirílico nunca; «Templeman III» tampoco | Unicode | baja |
| m01a_escaleta.py:736-738 | Cierre nombra al humano (substring) | 4 | Pregunta sin nombre | ya métrica v2 | baja |
| m01a_escaleta.py:500-501 | Nombre nuevo = `[A-ZÁÉÍÓÚÑ][\wáéíóúñ]+` | 2 | Cirílico/Ł | `str.isupper()` | baja |
| m01a_escaleta.py:1092-1113 | SYSTEM_V2 §5 «la morgue», §8 «quién dio la orden, cómo estaban las puertas… la pericia vs los testigos es casi siempre el mejor cap 6» | 1,4 | Ycuá hecho regla | función, no contenido | media |
| m01a_escaleta.py:1115-1145 | `<ejemplo>` SYSTEM_V2 Orleans con **ids reales** (Q184, T55, D30, Q08, Q24, Q14, Q47, Q146, D185, Q60, Q50, D192, D189, E3, E9), «517 ausentes» | 5 | Copia un id → «dato_central no existe» → regeneración gastada | ids «Q##», sin nombres | alta |
| m01a_escaleta.py:1102 | Gancho siempre flash-forward | 4 | Peor momento al inicio (16:22) | «si no es el primero…» | baja |
| m01a_escaleta.py:1168-1181 | `BLOQUEANTES_V2` casa mensajes por regex | 6 | Fragilidad | por código | baja |
| m01a_escaleta.py:1410-1428 | `_personas_beat` ≥2 tokens | 2 | Mononimos («Beria») | generalizar | baja |
| m01a_escaleta.py:812-822, 849-854 | `narrative_intent = DEFAULT_INTENT_BY_CAP[n]` fijo; `render_engine` por cap | 4 | Pico en cap 5 etiquetado «consequences»; tts silencia cap 2; m03 hereda intents falsos | desde la escaleta | media |
| m01a_escaleta.py:1475 | beats en prompt solo con compuerta | 3 | — | dejar | baja |
| m01a_skeleton.py:66-71, 99-107 | CHAPTER_SCHEMA 7 caps (veo/flux/veo; 45/105/45 s), `DEFAULT_INTENT_BY_CAP` | 3,4 | Ídem | contrato; intents desde escaleta | media |
| m01a_skeleton.py:839-840, 936-950 | `SCREEN_PER_CAP = 2`; caps 6-7 con ≥1 dato (roba) | 3,4 | Pocos datos duros | métrica | baja |
| m01a_skeleton.py:890-895 | `_worthy` ≤12 palabras | 3 | Citas traducidas largas | dejar | baja |
| evidence.py:57-60 (skeleton:626) | `ev._surname` latino, excluye «sheriff» | 2,5 | «Dürrenmatt» → «rrenmatt» | generalizar + borrar excepción | media |
| evidence.py:312-323 (`fix_glued_caps`) | `_COMMON_CAPS` sheriff, alcaide, huracán… | 1,5 | «Enfermera», «Operario» no se corrigen | perfil o diccionario | baja |
| guion_v4.py:53, 725-750 | `replace_repeated_dates`: fecha del pico o la más repetida → «ese <día>»; año opcional | 4 | Multi-año: «29 de septiembre» de otro año → «ese domingo» | exigir año o mismo cap; `fecha_central` de la ficha | media |
| guion_v4.py:98,112,183,197 | «frase corta con lugar y año»; «fecha completa una vez, en el cap 2» | 4 | Multi-fecha: pierde hechos | «cada fecha nueva, completa una vez» | media |
| guion_v4.py:90,175 | «en la cárcel, en el supermercado, en el valle» | 1 | Orleans/Ycuá/Vajont | «en el lugar del caso» | baja |
| guion_v4.py:103,188 | «un preso contó», «una sobreviviente recuerda» | 1 | Ídem | generalizar | baja |
| guion_v4.py:114,199 | «si las puertas estaban cerradas… Los dueños lo negaron» | 1 | Ycuá | generalizar | baja |
| guion_v4.py:116,201 | «sin «el edificio» cuando el dato dice «Templeman III»» | 1,5 | Orleans | generalizar | baja |
| guion_v4.py:119-145, 204-230 | `<ejemplos>` v5/v5.1 TODOS Orleans/Ycuá: inodoro, «Nueva Orleans, agosto de 2005», «30 de agosto», Renard Reed ×3, «Pearl debe 398 dólares», CCC, «Los Paiva», puertas de vidrio, «Aunque estén en la cárcel…» | 1,5 | Copia cadencia/léxico; «398» → bloqueante (a) | ejemplos sin cifras ni nombres reales | alta |
| guion_v4.py:156,241 | Error-ejemplo «Doce años. Trescientos veintisiete muertos.» | 5 | «trescientos veintisiete» → `invented_numbers` → PARADA | borrar cifras | media |
| guion_v4.py:243-244 | «Víctor… blíndex… Artigas», «cenizas… calor de horno» | 1,5 | Ycuá | generalizar | baja |
| guion_v4.py:55-73 | `OFICIO` + `EJEMPLOS_VOZ` (f11c) Orleans literal | 1,5 | Solo `version="f11c-1"` | borrar | baja |
| guion_v4.py:59,108,193 | Cita ≤ 25 palabras | 3 | Traducciones del ruso se alargan | perfil | baja |
| guion_v4.py:47, 653-661 | `CAP_TOL` ±25 %; `max_words` 1700 duro | 3 | Caso denso → PARADA por largo | dejar tope | baja |
| guion_v4.py:289-295, 320 | `_is_human` compara apellidos | 2 | Dos Paiva; Ivanov | por id de persona (`autor` → P##) | media |
| guion_v4.py:583, 595 (verify_quotes:102-104) | `_named(autor)` = `^[A-ZÁÉÍÓÚÑ]\S+\s+[A-ZÁÉÍÓÚÑ]`; `sur` ignorado si ≤3 | 2 | Cirílico o «Carlos de la Torre» → «anónimo» → **cita sin verificar pasa con nombre (bloqueante e nunca salta)**; «Li», «Wu», «Roy» | `str.isupper()`, partículas | media |
| guion_v4.py:620, 633-635 → guion_v3_reglas.py:281-345 | Bloqueante (b) `role_problems`: `_ROLE_PRESO` (…sobreviviente…) y `_ROLE_GUARDIA` (…oficial, capitán, teniente, sargento, deputy…) | 1,2 | «el teniente Ivanov» + «el sobreviviente Ivanov» → **PARADA**; manicomio «interno» vs «celador»; Ycuá «guardia de seguridad… sobreviviente» | borrar (b) o clases desde el perfil; mínimo sacar «sobreviviente» y grados militares | alta |
| guion_v3_reglas.py:337-339 (vía role_problems) | Cita ↔ persona por última palabra | 2 | Homónimos; partículas | por id | baja |
| guion_v4.py:574-598 | (e) apellido con `\b` ±200 chars en `ev.norm` | 2 | «Chelyabinsk»/«Cheliábinsk», «Kurchátov»/«Kurchatov» | `variantes` de ficha/pool | media |
| guion_v4.py:714-722 | `event_date` = pico o la más repetida | 4 | Casos largos | `historia.pico` con fecha | baja |
| m01b_guionista.py:40-41 | `INSTITUTION` = prisión, cárcel de, parish, opp, aclu, fema, sheriff, cuerpo de ingenieros… | 1,5 | «Mayak», «NKVD» no están; «gobierno» falsa alarma | instituciones de la ficha o borrar | baja |
| m01b_guionista.py:32-39, 347-362 | Métricas de estilo (≤6, >30, ±15 %, ≥85 %, humano ≥3 caps) | 6 | Solo métricas en v4 | dejar | baja |
| m01b_guionista.py:366-369 | «aparece por nombre» = apellido `\b` | 2 | Transliteración | variantes | baja |
| m01b_narrator.py:58-60, 718-720 | Largos en **caracteres** por rol (hook 300–800, dev 800–2000, outro 400–1100) desacoplados de `video_length`; m01d ±15 % | 3 | Amarilla (1200 palabras): avisos y párrafos movidos sin motivo | derivar de `*_words` (≈6 chars/palabra) | media |
| m01b_narrator.py:67, 742-750 | Hook primera oración ≤12 | 6 | — | métrica | baja |
| m01b_narrator.py:74-103, 752-777 | `FORBIDDEN_OPENINGS/CLOSINGS`, `GENERIC_CONNECTORS` («por otro lado») | 6 | Cita legítima marcada | métrica; «por otro lado» no es cliché | baja |
| m01b_narrator.py:197-214, 220-260 | `PROSE_RULES`/`F5_RULES`: «el sheriff Marlin Gusman», «28 de agosto… 29» | 1,5 | No los lee v4 | borrar con narrador v2 | baja |
| m01c_editor.py:60-70 | Prompt del editor: partir >30, ≤6 antes del golpe | 6 | No rechaza | dejar | baja |
| m01c_editor.py:92-97, 108-124 | `lexical_guard`: mayúscula no inicial = nombre | 2,6 | «Mayak» en minúscula pasa | dejar | baja |
| m01c_editor.py:84, tts_tags.py:70-74 | Citas por `«`/`“`; tts `[long pause]` solo con `«`/`“` | 6 | Comillas rectas → sin pausas | incluir `"` | baja |
| m01d_particion.py:31-39, 83-86 | Chars por rol ±15 %; cap largo → mover párrafo | 3,4 | Mueve un beat que la columna fijó (imágenes m03) | desde `video_length`; «corto» a métrica | baja |
| m01d_particion.py:178-188 | `personajes`: solo humano y antagonista `P##`; `entra_en_cap` por `split()[-1]` | 2,4 | **Antagonista institución desaparece sin aviso**; apellido = última palabra | `persona_de`/variantes; institución con `tipo` | media |
| m01d_particion.py:117-120 | `_title_fallback` `.capitalize()` | 2 | «Templeman iii», «Nkvd» | `[0].upper()+[1:]` | baja |
| m01d_particion.py:132-134, 143 | Títulos sin cifras/fechas/nombres, 2–5 palabras | 3,6 | «1957», «Mayak» prohibidos | dejar / perfil | baja |
| m01d_particion.py:304-306 | Regen: «fue una masacre», «un infierno», «una bofetada» | 6 | Juicios de Orleans | generalizar ejemplo | baja |
| tts_tags.py:23-26, 54-55, 64 | Golpe = ≤6 palabras en beat ≥4; máx 2; **ninguno en cap `setup`** (siempre cap 2) | 4 | Kyshtym: explosión en cap 2 → sin golpes donde más hacen falta | intent real por cap | baja |
| tts_tags.py:27, m01b_guionista.py:261 | Oraciones en `[.!?…]` | 2 | «Dr.», «I. V. Kurchátov» partidos | lista de abreviaturas | baja |
| fase1_5.py:168-176, 243-272 | `--modelo` duplica `MODELOS`; tras «PARADA» sigue a partición y juez | 3 | — | dejar | baja |
| config.py:192-194, 205-212 / video_length.py:11-33 | 7 caps, 1500/1700, 110/250/140, 45/105/45 s, beats 7–14; `gate_*` 150/8/10 | 3 | Kyshtym, manicomio 1900 → amarilla/roja por diseño | perfil del seed (tipo de caso → umbrales) | alta |
| config.py:168-173, cost_tracker.py:25-31 | Tarifas Gemini; GPT en `gpt_helpers.PRICES` | 3 | Modelo sin precio → Pro | dejar | baja |
| m01a_escaleta.py:316-334, m01a_skeleton.py:843-875 | «Un hecho, una cifra»; `cifras_canonicas` `estatus == "medios"` | 4 | «entre 200 y 10.000» (Kyshtym): la aproximada expulsada aunque sea la única honesta | «rango» como valor válido | media |
| m01a_escaleta.py:802-803, 858-868, 890-897 | Cronología/pantalla por ISO completa (`len(d) >= 10`) | 4 | Fechas de año/mes: nada se mueve | degrada suave | baja |
