# DECISIONES F5 — Guion v2 (research completo → guion y pantalla)

Handoff: `lab/hyperframes/f5/HANDOFF_F5_guion_v2.md`. Rama `f5-guion-v2`.

## Base
- **J0** El handoff dice «base f3-lab-identidad tras F4f». F4f no existe en el repo: el último commit es F4e (`39e37ac`). Omar pidió «desde el último commit», así que la rama sale de `39e37ac`. El handoff estaba en `lab/hyperframes/f4c/` y lo moví a `lab/hyperframes/f5/`.
- **J0b** Tests previos rotos que no son de F5: `test_module_01b_pauses.py` (3 fallos). Piden «PAUSAS» y «...» en los tonos de `m01b`, y el `m01b` del commit no los tiene. Los tests `test_module_00/01a/01b.py` son scripts en vivo, no pytest.

## §1.1 evidence_pool (`researcher_steps/evidence_pool.py`)
- **J1** Es un módulo nuevo y lo llama `step_4a_facts.extract_facts_and_sources(with_pool=True)`. Los `verified_facts` no cambian. Hace una llamada Flash por bloque (técnico, humano, misterio); el bloque visual no tiene datos ni fuentes. Si un bloque falla, ese bloque queda sin pool; si falla todo, `evidence_pool: None` y el pipeline sigue con `verified_facts`.
- **J2 (literal)** Texto, evento, cita y nombre (de lugar y de personaje) tienen que estar literales en su bloque. La comparación es sin mayúsculas, tildes, tipo de comillas ni puntuación final; lo que no está literal se descarta y se anota. `valor` tiene que estar literal en `texto`; si no, es null. `rol` de lugares y personajes es una descripción corta del LLM y no va a pantalla.
- **J3 (fuente)** Sale solo de las `[FUENTES CONSULTADAS]` del mismo bloque, y solo si el ítem nombra a la organización o autor de esa fuente (nombre antes de la primera coma o sigla entre paréntesis). Se busca primero en el texto del ítem y después en su línea del bloque. Si no hay coincidencia, `null`. En Orleans: 10 de 72 datos con fuente; el research casi nunca ata un dato a una fuente.
- **J4 (limpieza)** Personajes: solo personas (≥ 2 palabras con mayúscula, sin organizaciones). Citas: el título de una fuente no es una cita. Datos: un texto contenido en otro del mismo bloque es un fragmento y se descarta. Merge entre bloques: cronología con el mismo día y el mismo hecho (≥ 50 % de palabras de contenido en común), personajes por nombre y apellido, lugares por inclusión. Los IDs los asigna el código y la cronología va ordenada por fecha.
- **J5 (geocodificación)** Nominatim, 1 pedido por segundo, caché en `data/geocode_cache.json`. Primera corrida: «Templeman 1» cayó en Londres, «Angola» en África, «17th Street» en Nueva York. Por eso ahora se ancla al lugar principal del video (la ciudad más nombrada): se consulta «nombre, ancla» y solo se aceptan resultados a ≤ 400 km del ancla. Los de rol país, estado o ciudad no tienen tope. Las siglas (OPP, HOD, CYC) no se geocodifican. Sin resultado confiable → null.
- **J6** `raw_cache` guarda la respuesta cruda de Flash por bloque, para re-correr el filtro sin volver a llamar.
- **J7** El topic consolidado (`topic_researcher`) y el guion final (`m06_assembler`) llevan `evidence_pool`.

## §1.2 skeleton (`script_engine/m01a_skeleton.py` + `script_engine/evidence.py`)
- **J8** `script_engine/evidence.py`: helpers del pool compartidos por m01a, m01b, las métricas y gfx (IDs, texto, «anchors» = lo que tiene que sonar literal para contar un dato como usado, formato para prompts).
- **J9** Con `evidence_pool`, el prompt suma el pool numerado y un paso 1b que pide `_evidence_plan` (cap_1..cap_7), `personajes` y `cliffhanger` por cap. Sin pool, el prompt y el schema quedan idénticos a los de antes (test). El `_distribution_plan` de los `verified_facts` sigue igual; los facts son para las imágenes.
- **J10 (reparaciones deterministas)** En la prueba en vivo, Flash nunca cumplió todas las reglas en 3 intentos (faltaba el antagonista, el cap 7 quedaba con 1 dato nuevo, la cronología retrocedía un día, cliffhangers del mismo cap, F## mezclados). Por eso lo mecánico se repara en código y queda en `_evidence_repairs` del skeleton, auditable:
  - eventos anteriores al primero del cap previo se mudan a ese cap;
  - los repetidos que pasan de 1 se quitan;
  - un cap con menos de 3 nuevos se completa con IDs sin usar (eventos en su rango de fechas, después datos; el cap 7 prefiere lo más reciente);
  - el antagonista ausente entra en el primer cap cuyos datos lo nombran;
  - un cliffhanger inválido pasa a ser el primer ID nuevo del cap siguiente;
  - los F##, P## y L## dentro del plan se ignoran.
  Solo un D/T/Q inexistente, o un pool que no alcanza, fuerzan error y reintento.
- **J11** «Seguir la cronología» se valida en los caps 2–6, por la primera fecha de cada cap. El hook puede abrir con el momento más fuerte y el cap 7 con lo último que se supo.
- **J12** Si el pool tiene menos de 21 datos, eventos y citas, el mínimo por cap baja a ⌊n/7⌋ (al menos 1).
- **J13** Instrucción agregada al prompt: «si dos datos se contradicen, van al mismo cap y la narración cuenta la contradicción». Responde al riesgo 6 del handoff (6,375 vs 6,500 elegidos sin criterio).

## §1.3 narrador (`m01b_narrator.py`) + §1.5 juez narrativo (`script_engine/m05_narrative.py`)
- **J14** El juez de §1.5 es un módulo nuevo y determinista, `m05_narrative.py`. `m05_judge` es el juez VISUAL (prompts de imagen contra narración) y sigue desconectado de la cadena desde Chat 119. El narrador lo usa para validar cada cap (`cap_problems`) y reintentar con feedback dirigido; `judge_narration()` escribe el reporte del video en `_steps/<id>/06_judge_narrative.json`.
- **J15 (qué cuenta como «dato usado»)** Un ítem cuenta si alguno de sus anchors suena literal (`evidence.anchors`):
  - fecha → «día de mes»;
  - cifra o magnitud → sus cifras, en dígitos o en palabras (`script_engine/num_es.py`), y «50» dentro de «seiscientos cincuenta mil» no vale;
  - evento o dato de fecha → la fecha más una palabra de su contenido en la MISMA oración. Sin esto, «29 de agosto» marcaba seis eventos.
  Densidad y repetición cuentan solo datos duros (`is_hard`: cifras, magnitudes, fechas con día, contradicciones, eventos con día, citas). Un nombre, un lugar o un año suelto no son «el dato».
- **J16 (calibración en v1)** Orleans v1 con este medidor da:
  - densidad 1.65 (el analista estimaba ≈ 0.7: mi conteo es un poco más generoso; v1 igual falla el umbral de 2.0);
  - «6,500» en 4 caps y «500» en 6 caps (falla repetición);
  - Gusman 0 veces (falla antagonista).
  El diagnóstico se reproduce.
- **J17 (adjetivos)** No hay etiquetador gramatical (spaCy, stanza y nltk no están instalados). La heurística es una lista del género más sufijos -oso/-ble/-ivo/-ante/-ente…, excluyendo adverbios en -mente y sustantivos conocidos. Mide la tendencia, no la gramática exacta.
- **J18 (umbral de adjetivos recalibrado)** El handoff pide ≤ 8 por 100 palabras con v1 ≈ 14 (medición del analista). Esta heurística mide v1 en 6.2, así que con 8 literal v1 ya «aprobaría». Se aplica el mismo recorte relativo, 8/14: `ADJ_MAX = 3.6`. Lo marco para que el analista valide la escala.
- **J19 (antagonista)** Se exige el principal: el más nombrado en el pool (Orleans: Marlin N. Gusman). El pool marca también a su adjunto William Hunter como antagonista; exigir a los dos daba un falso negativo.
- **J20 (reglas en el narrador)** Con pool, el prompt de cada cap suma:
  - sus datos asignados;
  - las personas que entran (nombre y cargo);
  - el cliffhanger;
  - los datos ya gastados en 2 caps;
  - las reglas A–G.
  Sin pool, el prompt es idéntico al de antes (test). La regla 6 (lista blanca numérica) pasa a ser «verified_facts o el EVIDENCE POOL».
- **J21 (validación)** `cap_problems` chequea:
  - ≥ 3 de los datos nuevos asignados, literales;
  - ningún dato que ya esté en 2 caps;
  - personas del cap por nombre, apellido y cargo;
  - eventos en orden de fecha;
  - citas entre comillas con su autor cerca;
  - relleno prohibido y más de 2 oraciones seguidas que califican sin dato;
  - densidad ≥ 2.0 y adjetivos ≤ 3.6;
  - cierre que contiene un término del cliffhanger.
- **J22 (reintento y aceptación)** Si falla, `kind="evidence"`: reintenta con la lista de problemas (3 intentos con pool; antes eran 2). Si el último intento todavía falla SOLO por reglas del pool, la narración se acepta y los problemas quedan en `_f5_violations` del 01b y en el reporte del juez. Largo, frases prohibidas y primera oración siguen como antes. Motivo: el handoff dice «falla → reintento», no «falla → matar el topic».
- **J23** Citas: en la prueba el narrador puso el autor como firma («— Sheriff Marlin N. Gusman»), que el TTS leería. La regla E ahora pide el autor DENTRO de la oración («dijo el sheriff Gusman»).

## §1.4 normalizer (`tts_normalizer.py`, `m02_5_normalizer_gate.py`)
- **J24** `normalize_pool_forms()` es determinista. Pasa a forma hablada las horas con AM/PM, los dólares («$223 millones» → «doscientos veintitrés millones de dólares»), los porcentajes con decimal y las comillas de citas (se sacan; la cita queda dicha). El gate la aplica a cada cap después de los spans del auditor LLM, en modo interactivo y en batch, y la deja anotada como span `f5_pool_forms`. `normalize_for_tts` (SHORT y respaldo) no la llama: el camino SHORT no cambia, salvo las siglas.
- **J25** Siglas: ACLU → «a ce ele u», HRW → «Human Rights Watch», DOJ → «Departamento de Justicia», FEMA se pronuncia como palabra.
- **J26** El gate acepta `persist_dict=False`, para correr sobre un topic de prueba sin escribir en el `normalizer_custom_dict.json` global.

## Herramientas
- **J27 (bug de proceso)** Los heredocs de Git Bash convierten `\\b` en el byte 0x08 dentro de strings de Python. Es el mismo daño que tenían `gfx_fragments._DATE_RE` (F4c G16) y `gfx_icons` (F4d H11). Pasó otra vez en `evidence.py` y lo corregí. Desde acá, todo parche con barras invertidas va por un script escrito con Write, y cada parche chequea que no queden bytes de control.

## §2 producción (`script_engine/gfx_pool.py` + cableado en gfx_director, gfx_layer, gfx_question)
- **J28 (compatibilidad)** Todo va detrás de `ctx["pool"]`, que solo existe si el guion (`data/scripts/<id>.json`) trae `evidence_pool`. Los guiones viejos no lo traen y salen igual que antes: suite gfx en 301 verdes, sin cambios. Sin `--gfx` no corre nada de esto.
- **J29 (candado)** `load_chapter_context` suma a las fuentes del candado los textos del pool: datos, eventos, citas con su autor, lugares, personajes y sus fuentes completas y cortas («Organización, año»).
- **J30 (recortes)** Con pool, los recortes de `verified_facts` se reemplazan por recortes del pool (`plan_pool_documents`). Proceso:
  1. Candidatos: los IDs del cap en el skeleton y después los de los caps ±1; datos duros y citas; sin los que ya salieron en pantalla en caps anteriores (dedupe por `pool_id`).
  2. Cada candidato se ubica en la oración de la voz que habla de lo mismo (≥ 2 palabras de contenido en común, o 1 si el dato es del propio cap).
  3. Opciones: cláusulas completas del dato que suman a la voz del tramo y pasan el candado. Flash elige entre las 3 mejores.
  4. Kicker = fuente corta del dato → fecha literal del dato → año del dato. Sin ninguno → sin recorte. Ya no se usa el año que dice la voz del cap (F4c G11), como pide el handoff.
  5. Se respeta el tope de recortes por cap y no se pisan otros bloques.
- **J31 (datos)** También salen del pool: la cifra del dato, en el instante en que la voz la nombra, con una cláusula de ≤ 5 palabras del pool. Máximo 2 por cap. R7 (F4c) los saca si la voz los dice literal en ese tramo. Los datos de `verified_facts` que había puesto el director se reemplazan.
- **J32 (ícono por contenido)** Decisión de Omar, escena 1: el ícono lo decide el tema del dato, nunca la palabra de la voz. Mapa:
  - demanda / jurado / indemnización / carta de hallazgos → balanza;
  - cadáveres / cuerpos / muertos → calavera;
  - aguas residuales / contaminación → biohazard;
  - registros / listas / desaparecidos → ojo tachado;
  - celdas / encerrados → candado;
  - agua / inundación / pies / metros → gota;
  - cifras de personas → sin ícono.
- **J33 (íconos que faltan)** Huracán → espiral y generadores → rayo tachado: esos íconos no existen todavía. El handoff pide generarlos «con el pipeline de los 12», pero F5 es sin imágenes (Omar). Quedan anotados en el bloque (`icon_missing`) y salen sin ícono. Son el primer pendiente de F6.
- **J34 (pregunta)** Sale del cliffhanger del skeleton: `gfx_question` recibe el texto del dato que revela el cap siguiente. Las 3 candidatas tienen que pasar la rúbrica de F4c y compartir un sustantivo con ese dato. Si ninguna pasa, se usa el generador de F4c. La pregunta manual de Omar nunca se pisa. El caché usa la versión `f5-cliff`.
- **J35 (reloj)** Sale de la cronología del cap, y solo si el cap avanza de fecha (≥ 2 fechas distintas) o trae hora. Muestra la primera fecha (o la hora) desde que la voz la nombra hasta que nombra la siguiente. La plantilla no cambia (no anima un cambio de fecha); el candado sigue validando el texto del evento y la hora.
- **J36 (mapa)** Los lugares con lat/lon quedan en el `evidence_pool` del guion para F6. No se renderiza nada.
- **J37 (`plan_only`)** `apply_gfx(plan_only=True)` hace director, candado, pico, identidad, pregunta, crítico, SFX y cues, y devuelve el clip base sin HyperFrames ni render. Es para la simulación de §3.
- **J38** Una cláusula de recorte puede arrancar con una cifra («517 prisioneros…»). Antes solo podía arrancar con letra.

## §3 prueba sobre Orleans
- **J39** Topic de prueba `ba6c3cac-f5v2`. Usa el research de v1 (`00_pool_etiquetado.json`, sin volver a investigar) y la misma respuesta cruda de Flash para el pool (mismo prompt, `00b_pool_raw.json`). Los `verified_facts` son los de v1, idénticos (diff vacío). No se escribe nada en `topics_db.json`: el runner le pasa el topic directo a skeleton y narrador.
- **J40** El normalizer corre en batch con `persist_dict=False`. El juez escribe `06_judge_narrative.json` (v2) y `06_judge_narrative_v1.json` (v1 medido con el mismo pool), los dos en el dir de v2. El dir de v1 no se toca.
- **J41 (proxy de fotos)** Las palabras de v2 se reparten uniformes en la duración del audio de v1, y las escenas se fijan en los tiempos de corte de v1 con anchors sintéticos de 4 palabras de v2. Los índices son crecientes, el trigrama es único desde el anchor anterior y no arrancan en cifras ni siglas con puntos, porque el needle se normaliza como el TTS. En los caps Veo, el primer suplementario va con un anchor real. Las 7 escenas proxy resuelven.
- **J42** La simulación de v1 corre con el MISMO código de F5 (sin pool, así que el camino de verified_facts de F4e) y con los cachés del director de v1. La de v2 corre en `output/ba6c3cac-f5v2/_fase2b_work`, con los cachés de visión de las mismas fotos copiados. `record_proposals` se desactiva en las simulaciones: la copia v2 no es un segundo video, y si no, promovería palabras al perfil.
- **J43 (arreglos en la prueba)** Tres arreglos que salieron de la prueba:
  - cap con muchos datos → narración de 2495 caracteres → el último intento caía por largo. El prompt ahora pide 3–6 datos y el skeleton ≤ 7 por cap, y un último intento que rompe largo o frases cede ante uno anterior que solo fallaba reglas del pool;
  - los paréntesis cortan siempre la cláusula;
  - una cláusula no arranca en infinitivo reflexivo («inundarse…»).
- **J44** §1.6 (`m03_visual`, opcional) no se hizo.


---

# F5b — arreglos de la validación del analista (`VALIDACION_F5.md`)

Pedido: N1–N5 (narración) y S1–S6 (pantalla), regenerar v2, actualizar `compara_orleans.html`, re-simular los 7 caps. Sin imágenes ni render. Misma rama `f5-guion-v2`, desde `1ca7194`. El handoff con §1.6 y sus FRENOS (`HANDOFF_F5_guion_v2.md`) ya estaba en el disco sin commitear; entra en el commit de F5b junto con `VALIDACION_F5.md` y la versión previa del handoff (`HANDOFF_F5_guion_v2.v1_sin_frenos.md`).

## Narración
- **K1 (N1, relevancia)** `researcher_steps/evidence_pool.unrelated_lines`. El propio bloque marca lo ajeno («aunque no directamente relacionado con los eventos de Katrina», «no prueban nada sobre…»). Se toma la nota (la oración del marcador y la siguiente) y las líneas del bloque que comparten ≥ 2 raíces RARAS con ella (palabras de ≥ 7 letras que aparecen en ≤ 2 líneas). Un ítem sale solo si su texto está en esa zona y en ninguna otra parte del bloque: «Nueva Orleans» aparece en la nota de la posada, pero también en todo el resto, y se queda. En Orleans salen 4: la cárcel de 1902, el capitán de la guardia, el médium y la «Inn at the Old Jail». Lo que sale queda en `pool["_descartados"]` con el motivo. `evidence.items` no lo lee.
- **K2 (N1, lo que no se tocó)** El bloque humano dice «El año 2005 fue también el año del atentado terrorista en Londres». No tiene marcador de «no relacionado», así que Londres sigue en el pool. No lo pidió el analista; queda anotado.
- **K3 (N5, nombres)** `person_acts`: un personaje entra si es autor de una cita, si es antagonista (el research le atribuye la decisión) o si tiene un verbo activo después de su nombre. La heurística salta «Jr.», un sujeto coordinado («y Paul Kunkel Jr.»), una aposición («, un recluso,») y un «del Cuerpo de…». La pasiva no cuenta. Resultado:
  - quedan Gusman, Hunter, Strock («testifica»), Waganfeald y Kunkel («recibieron») y Morgan («presentó»);
  - salen Schwarz («es arrestado») y **Hubert**, que solo aparece como demandado. El analista lo había listado entre los nombres que entran; con la regla de N5 no hace nada. Que lo confirme.

  También salen los datos que son solo el nombre de quien sale («Raphael Schwarz», «alcaide Cornel Hubert»). El juez marca `nombres_sin_accion` si la narración igual los nombra.
- **K4 (N5, mayúsculas)** Dos arreglos:
  - en el pool, `fix_caps`: minúscula después de un rótulo («…: aproximadamente 6,375»), salvo antes de un nombre propio, y en cargos comunes a mitad de oración («el sheriff Gusman», «huracán Katrina»). El rol va en minúscula. Las citas quedan como las dijo el autor;
  - en la narración, `evidence.fix_glued_caps` baja una lista cerrada de sustantivos y participios comunes («…Schwarz, Arrestado por» → «arrestado»). Nunca toca un nombre propio ni el arranque de una oración o de una cita.

  El candado compara sin mayúsculas, así que ningún texto deja de ser literal.
- **K5 (N2, por id)** Con pool, el narrador devuelve `datos_usados` (schema + regla K del prompt). Cuenta lo declarado que además suena literal. Un id declarado que no suena literal es un problema que vuelve en el reintento. Si usa un dato y no lo declara, no cuenta: el error es conservador. v1 no declara y se mide por regex como en F5; el reporte dice `conteo: por_id | regex` y, para v2, también `densidad_regex`. Sin pool, el schema y el prompt quedan como antes (test).
- **K6 (N3, una vez por cap)** `evidence.repeats_in_cap`: de cada dato declarado se cuentan sus anchors (cifra o fecha, en dígitos o en palabras) y sus «frases firma» (3-gramas del dato con ≥ 2 palabras de contenido en minúscula: «nivel del pecho»). Más de 1 vez en el cap es un problema y el feedback pide paráfrasis sin la cifra. Se informa la forma más larga («29 de agosto de 2005» cubre «29 de agosto»).
- **K7 (N4, adjetivos)** `ADJ_MIN = 2.0`, `ADJ_MAX = 4.0`, en la misma escala de la heurística que usó el analista. Reemplaza al 3.6 de J18. Por debajo del piso, el feedback pide 2 o 3 calificativos atados a hechos, sin relleno.

## Pantalla
- **K8 (S1, cláusula completa)** `gfx_pool.pool_clause_options` reemplaza a `clause_options` en los recortes del pool. Hay una heurística de verbo, sin etiquetador.
  - Una opción arranca donde arranca la cláusula: el comienzo de una parte entre comas, o una coordinada o subordinada («y», «que», «cuando»…) con verbo propio en su tramo. Un sujeto coordinado («Robie Waganfeald y Paul Kunkel Jr.») no corta.
  - Termina donde termina la cláusula, o en un borde de frase (preposición, «que», «y», «de» + artículo) DESPUÉS de verbo + objeto. Antes de una fecha («fallaron | el 29 de agosto») puede cortar justo después del verbo, porque la fecha va al kicker.
  - Nunca corta dentro de «más de 50».
  - Una parte sin verbo vale solo entera y con su cifra («un huracán de categoría 3»).
  - Una parte que arranca en verbo en minúscula («toca tierra en…») es un predicado sin sujeto y queda fuera.
  - «EE. UU.», «Jr.», «N.» y una sigla entre paréntesis («(OPP)») no cortan.
  - Si ninguna opción entra en ≤ 10 palabras, no hay recorte. Flash solo elige entre estas opciones.
- **K9 (S1, casos del analista)** Resultado sobre sus tres ejemplos:
  - «piso comienzan…» → «Las celdas del primer piso comienzan a inundarse» / «las aguas residuales refluyen»;
  - «federal otorga…» → «Un jurado federal otorga más de $650,000»;
  - «la prisión no finalizó…» → sin opción («La evacuación completa de la prisión no finalizó hasta el viernes 2 de septiembre» tiene 13 palabras, y cortarla deja el verbo sin su complemento).
- **K10 (S2, cronología)** `narrated_dates`: la fecha que la voz viene narrando en cada oración es la última fecha con día dicha hasta esa oración. Antes de la primera, vale la primera fecha que dice el cap (la voz todavía no avanzó). La fecha del dato es `evidence.item_date`: su `fecha` completa o la fecha escrita en su texto, con el año del cap si no lo dice. Un dato solo puede salir en oraciones donde su fecha es ≤ la narrada. Un dato sin día no tiene restricción.
- **K11 (S3, hecho)** `evidence.same_fact`. Dos ítems cuentan el mismo hecho si comparten:
  - una cifra grande (≥ 3 dígitos, o con $ o %);
  - una cifra chica más una palabra de contenido;
  - o, sin cifras, la misma fecha con día y ≥ 50 % de las palabras de contenido.

  Se aplica entre caps (contra lo ya mostrado) y dentro del cap (recortes y datos). Los candidatos salen del cap y del ANTERIOR, nunca del siguiente: con ±1, el cap 5 mostraba el jurado del cap 6.
- **K12 (S4, ícono literal)** Token nuevo `icon_literal_only`: apagado por default, prendido en `misterio`.
  - `category_icon` ya no cae al ícono más común de la categoría.
  - `emphasis_icon` no pone ícono a un adjetivo (heurística de m05).
  - Los íconos automáticos de game-icons (F4b §4) no corren.
  - `gfx_pool.content_icon` busca en el TITULAR la primera palabra del mapa `icon_words` del perfil. «Agua» sola nunca lleva gota (R4). Espiral y rayo siguen anotados como faltantes (J33).

  Al mapa del perfil se suman «inundación», «inundaciones» → gota y «residuales» → biohazard, que son los del analista. Los tests de F4c que fijaban el ícono por categoría corren ahora con el token apagado (el comportamiento sigue cubierto), y hay un test nuevo para el mapa literal.
- **K13 (S5, metros)**
  - Las opciones de recorte y de dato con pies, millas, libras, galones o °F quedan fuera.
  - El nivel de agua, si la voz dice «15 pies», muestra la cifra métrica LITERAL del mismo fact («(4.6 metros)»). Si el fact no la trae, no hay nivel de agua: convertir daría un texto que el candado no acepta.
  - Un contador con unidad imperial se descarta.

## §1.6 / S6 — `m03_visual` con FRENOS
- **K14** Un solo cambio en `_format_seedream_canon_block`: si `topic["evidence_pool"]`, se agrega `UBICACIONES DOCUMENTADAS (no mezclar en una misma escena):` antes del bloque `USO`. Lo arma `_format_documented_locations`:
  - grupos fijos con su regla de composición: menores → «separados de los adultos»; mujeres → «nunca en la misma celda que hombres»; evacuados;
  - el «dónde» sale literal del pool: lugares cuyo rol es del grupo («instalación juvenil») y lugares nombrados como destino en un dato o evento del grupo («al paso elevado de Broad Street sobre la Interestatal 10»). Un lugar de origen no cuenta. El escenario principal (nombrado en más de 4 textos) no distingue a nadie;
  - personajes por rol, nunca por nombre.

  No se tocó nada de la lista de FRENOS. Sin pool, el canon es byte-idéntico (comparado contra `1ca7194` sobre el topic de Orleans v1, y con un test). Las 5 fallas de `test_module_m03_merge_timing.py` y `test_module_03_plan_anchors.py` también fallan en `1ca7194` (corrido sobre un `git archive` del commit): no son de F5b.
- **K15 (prueba de §1.6)** `correr_f5_orleans.py --etapa visual` corre `assign_visual_prompts` tal cual sobre v2, con el `sync_map` de v1 (mismas duraciones, mismo número de imágenes) y `video_id` = v2. No hay timestamps de v2, así que la reconciliación temporal no corre. Es comportamiento existente sin audio, no un cambio. Solo texto; cero imágenes.

## Corrida
- **K16 (respaldo y caché)** El caché del director (`gfx_plan_chNN.json`) se valida por versión del director, no por narración. Por eso la simulación de v2 arranca en un work dir limpio y la de F5 queda en `output/ba6c3cac-f5v2/_bak_f5b_pre/_fase2b_work`. La de v1 se re-simula con el código de F5b (cambian íconos y unidades) y la anterior queda en `…/_fase2b_work_f5sim_v1_bak_f5b`. Los archivos de v2 de F5 quedan en `lab/hyperframes/f5/v2_f5/`.
- **K17 (N2, declaración tolerante)** En el 1.er intento el narrador declaró F## (verified_facts) y, en un cap, el texto del dato en vez del id. `evidence.resolve_declared` traduce lo DECLARADO a ids del pool, sin regex sobre el pool entero:
  - «[D07]» → D07;
  - «F05» → los ítems del pool que cuentan ese fact (≥ 50 % de palabras en común) y suenan literales;
  - un texto → el único ítem que lo contiene.

  Además, el feedback del reintento lista los datos que suenan y no se declararon («Interestatal 10 no son los niños»).
- **K18 (densidad: por qué baja)** El regex de F5 contaba una vez por id. Un «29 de agosto» dicho una vez prendía 5 eventos, y «517» dos ids. Por eso el juez suma `densidad_hechos`: anclas DISTINTAS que suenan.
  - **Por hecho:** v1 0.86 · v2 F5 2.01 · v2 F5b 1.12.
  - **Por id** (lo que pide N2): v2 F5b 1.26.

  La v2 de F5b tiene MENOS datos que la de F5. Las reglas nuevas tiran en contra de la densidad: cada dato una vez, piso de adjetivos, declarar ids. Flash no las cumple todas en 3 intentos y acepta con violaciones (J22). Hubo 3 corridas del guion: en la 2.ª se sumó K17; en la 3.ª, la meta explícita «2 datos distintos cada 100 palabras». Quedó la 3.ª (0 caps con repetidos dentro del cap, 0 nombres sin acción). Las otras dos están en `pruebas/01b_narration_f5b_intento{1,2}.json`.
- **K19 (P5 sigue)** Los caps 6 y 7 siguen sin recorte. Hay candidatos (D17, D37, D50, Q02, T17, T25…), pero ninguno tiene una cláusula completa de ≤ 10 palabras que sume a la voz con fuente o fecha:
  - D37 «El Sheriff Gusman negó públicamente las acusaciones» no tiene fecha ni fuente (kicker J30 → sin recorte);
  - T25 «El Departamento de Justicia de EE. UU. emite una carta de hallazgos» tiene 11 palabras.

  No se relajó ninguna regla.
- **K20 (§1.6, lo que muestran los prompts)** Con el canon nuevo, los 3 prompts del cap 4 con niños (el ancla «niños de hasta 10 años» y las dos siguientes) ubican al chico en el centro juvenil (CYC). Ninguno mezcla mujer y niño en una celda. Igual quedan dos niños solos en una celda de la prisión de adultos: ch01 supp 3 («algunos niños, quedaron atrapados…») y ch07 Veo. El canon es texto pasivo y el validador no se toca (FRENOS). **Propuesta, no hecha:** que `m03` exija el lugar del grupo cuando el ancla nombra al grupo.
