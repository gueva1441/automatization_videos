# F7b — Pool de Orleans v3-research (R3 extracción · R4 merge · R5 verificación por texto)

Rama `f7-research-v3` · topic `ba6c3cac-f7r3` · código `researcher_steps/research_v3.py` · runner `lab/hyperframes/f7/f7b_pool_orleans.py` · pool `lab/hyperframes/f7/00_pool_v3.json` (copia de `data/scripts/_steps/ba6c3cac-f7r3/00_pool_v3.json`) · métricas `f7b_metricas.json` · log `f7b_run.log` · tests `test_module_f7.py` (23).

## 1. Métricas contra el pool f6v3 (criterio de éxito §1.1)

| métrica | f6v3 | **v3-research** | criterio |
|---|---|---|---|
| datos | 91 | **558** (6.1×) | ≥ 5× → ≥ 455 ✔ |
| cronología | 30 | **152** | — |
| cronología con hora | 2 | **28** | «con horas donde el documento las tenga» ✔ |
| lugares | 29 | 67 | — |
| citas | 11 | **188** (152 de testigos) | — |
| citas verificadas literal | 2 | **162** (+ 25 parciales, 1 sin verificar) | — |
| citas de testigos con nombre, verificadas con documento | 2 | **25** (de 20 personas) | ≥ 15 ✔ |
| personajes / testigos | 11 / 3 | 69 / 52 | — |
| testigos con ≥ 3 citas | 0 | 4 | — |
| elegibles como humano (testigo, no antagonista, ≥ 3 citas o ≥ 3 datos, presente en 2005) | 0 | **13** | — |
| ítems con `doc_id` + posición en el txt | 0 % | **100 %** | 100 % ✔ |
| ítems confirmados por ≥ 2 documentos | 0 | 35 | — |

Elegibles: Brady Richard, Corey Stevenson, Raphael Schwarz, Renard Reed (guardia), Iris Hardeman, Joyce Gilson, David Williams, Tyrone Lewis, Pearl Cornelia Bland, Quantonio Williams, Duane Lewis (guardia), Dan Bright, Edward «Edgar» Burton.

Citas de testigos con nombre verificadas (muestra): Brady Richard, Rhonda Ducre, Renard Reed («Once the power went out, deputies started quitting right and left»), Deputy Foster («Gusman totally disappointed me and let me down when we needed him the most»), Keanna Herbert, Pearl Cornelia Bland, Ronnie Lee Morgan Jr., Luis Reyes («There are dead inmates in there still»), Mary Gehman, David Fernandez, Dan Bright («They left us to die there», HRW 2005), Edward Burton y Big Whappy (The Lens).

## 2. Aporte por documento

| doc | documento | datos | crono | lugares | citas | personajes | descartados | costo R3 |
|---|---|---|---|---|---|---|---|---|
| F01 | ACLU *Abandoned & Abused* (2006) | 173 | 42 | 23 | 70 | 45 | 27 | 0.674 |
| F02 | HRW, *Prisoners Abandoned to Floodwaters* (2005) | 12 | 6 | 2 | 7 | 4 | 0 | 0.061 |
| F03 | ACLU, 400 testimonios resumidos (2006) | 290 | 67 | 27 | 82 | 13 | 87 | 0.883 |
| F04 | DOJ, resúmenes de casos (solo la ventana de OPP) | 6 | 7 | 1 | 0 | 0 | 1 | 0.034 |
| F05 | HRW, cartas de presos (2005) | 19 | 11 | 9 | 5 | 0 | 0 | 0.067 |
| F06 | ACLU, abusos después de Katrina (2006) | 6 | 6 | 0 | 11 | 0 | 0 | 0.049 |
| F08 | Vera Institute, *Justice in Katrina's Wake* (2015) | 17 | 4 | 1 | 4 | 2 | 4 | 0.073 |
| F09 | DOJ, carta de hallazgos (2009, OCR) | 7 | 0 | 0 | 0 | 0 | 1 | 0.058 |
| F10 | The Lens (2025) | 24 | 6 | 4 | 9 | 5 | 0 | 0.076 |
| F12 | *Voices from the Storm* (página del libro) | 4 | 3 | 0 | 0 | 0 | 1 | 0.028 |

Conteos por documento de origen (`doc_id`); un ítem repetido en otro documento cuenta una vez, en el primero por autoridad. Descartados en total: 129 (66 «no es una persona con nombre propio», 46 «cita_literal no está en el documento», 8 lugares cuyo nombre no está, 8 personajes sin acción —ninguno testigo—, 1 fecha que no coincide con el año de la cita literal). Contaminación: **0 ítems** fuera por fecha o lugar en esta corrida — ninguno de los 10 documentos es de otro tema ni de más de 2025, y la nota de la ACLU sobre Trinidad (Burnley / Chad Joseph) no salió en la búsqueda. La regla está probada con ese caso como fixture (`test_merge_dedupes_between_docs_and_drops_contamination`).

## 3. Lo que salió de leer los documentos reales (y quedó como regla en el código)

1. **PDF a dos columnas.** Con `pdfplumber` el informe de la ACLU salía con las líneas de las dos columnas intercaladas: el modelo leía bien, pero sus citas literales no aparecían en el txt (F01: 2 ítems válidos en la primera corrida). Ahora `pdftotext` (poppler) va primero; `pdfplumber` (con detección del canal entre columnas y sin las letras sueltas de los rótulos verticales) y `pypdf` quedan de respaldo. Las respuestas de Pro ya pagadas se **re-validaron** contra el txt nuevo sin volver a llamar (`--revalidar`).
2. **OCR sin espacios** (carta del DOJ: «andefficientlyevacuatingthe»): la búsqueda literal tiene un segundo intento que ignora los espacios, solo para citas de ≥ 8 palabras y ≥ 30 letras.
3. **Llamadas a nota pegadas** («prisoners.11This», «OPP,17$2.00»): se sacan al pasar el PDF a texto, con un patrón que no toca cifras («$24.39», «1,300», «2005.1» quedan).
4. **Fecha mal normalizada por el modelo:** «On August 10, 2001» fechado 2005-08-10 (ponía a Shawn Duncan, muerto en 2001, como presente durante el huracán). Un evento cuya cita literal trae un año distinto del de su fecha se descarta.
5. **Personas:** «Sgt. Bell» / «Sergeant Bell» y «Marlin N. Gusman» / «Sheriff Martin Gusman» (errata de un documento) son la misma persona; el nombre que queda es la variante con nombre y apellido más frecuente en los documentos (las otras en `variantes_nombre`). Los autores de cita que son cargos o grupos («Abogado del Sheriff», «Oficiales en Conchetta») no entran como personajes.
6. **Filtro de acción** (`evidence_pool.acting_filter`, heurística de verbos en español para los bloques resumidos): sacaba testigos reales de la ACLU (Keanna Herbert, Iris Hardeman). En v3 un testigo ya está probado por su `cita_literal` y no pasa por ese filtro; el resto sí.
7. **Elegible como humano:** además de lo que pide el handoff (≥ 3 citas o ≥ 3 datos), no antagonista (Gusman era elegible: el modelo lo marca testigo porque estuvo en la cárcel) y con alguna presencia en el año del evento.
8. **Documento largo de otro tema** (lista de casos del DOJ, 200 k caracteres con 6 menciones de OPP): se leen solo las ventanas de ±4 k alrededor de cada mención (1 llamada en vez de 4).

## 4. Costo

| tramo | costo de una corrida limpia (estimado) | gastado en esta sesión |
|---|---|---|
| R1 (Pro + búsqueda: 4 focos + 5 pistas, con reintentos «sin grounding») | ≈ 0.55–0.75 | ≈ 1.0–1.2 (5 corridas mientras se ajustaba R1; medidas: 0.07, 0.33 y 0.48; la 2.ª y la 3.ª no registraron su costo) |
| fichas (Flash) | 0.01 | 0.03 |
| R3 (Pro, 10 documentos, 21 trozos) | 2.00 | 2.21 (incluye el piloto de F05, la re-extracción de F05/F06 cuando cambió su ficha y Vice 2015, que quedó fuera del cupo) |
| R4/R5, geocodificación | 0 | 0 |
| **total** | **≈ 2.6–2.8** | **≈ 3.2–3.4** |

**El criterio de costo (≤ US$ 2.5 por tema) no se cumple:** ≈ US$ 2.6–2.8 en una corrida limpia (estimado: R3 está medido —2.00—; R1 sale de la última corrida más las búsquedas que estaban en caché; no se midió una corrida limpia de punta a punta). El 70 % es la lectura de los dos documentos de 300 k de la ACLU (F01 0.67 + F03 0.88: 12 trozos de 60 k, salida larga). Palancas, sin probar: `R3_THINKING` 2048 → 1024; Flash para documentos de testimonios resumidos (F03); menos reintentos en R1 (hoy hasta 3 llamadas por búsqueda que vuelve sin grounding).

## 5. Integración

- **Contrato:** el pool conserva todas las claves (`datos`, `cronologia`, `lugares`, `citas`, `personajes`, `_descartados`, `cifras_canonicas`). Nuevo y aditivo: `doc_id`, `docs`, `n_fuentes`, `evidencia` (cada documento con su posición y cita literal), `cita_literal`, `offset`, `idioma`, `fuente` (título y año del documento: ahora todo ítem tiene fuente); en citas `texto_original`, `texto_es` (= `texto`), `testigo`, `presente_en`; en personajes `n_citas`, `n_datos`, `elegible_humano`, `variantes_nombre`; `verificacion` en todos los ítems (en citas, con `verificada` / `verificada_parcial` / `sin_verificar`; la escaleta ya trata todo lo que no es `verificada` como «sin nombre»). Metadatos en `_research_v3` (documentos, versiones de prompt, costo).
- **Escaleta (m01a):** el prompt se arma con el pool nuevo sin error (test sin LLM y con el pool real), pero pasa de ≈ 8 k a **≈ 63 k tokens** (253 k caracteres). Es el riesgo 4 del handoff: entra en el contexto de Pro, pero cuesta ≈ US$ 0.08 de entrada por intento y no sé cómo se comporta la escaleta con 558 datos. **Propuesta para F7c** (no hecha: m01a es freno): que la escaleta reciba un resumen por documento + personajes y citas completos, como dice el handoff.
- **4b/4c/4d/4e:** no se corrieron. Hoy reciben los bloques angulares de texto, no el pool; para `ba6c3cac-f7r3` quedan los de f6v3 (`01_facts_sources.json` del topic nuevo = el de f6v3 con el pool reemplazado).
- **Topic nuevo** `ba6c3cac-f7r3`: `data/scripts/_steps/ba6c3cac-f7r3/01_facts_sources.json` y una entrada NUEVA en `data/topics_db.json` (copia de la de `ba6c3cac-f5v2` —f6v3 no está en la base— con el pool nuevo y `research_version: 3`). f5v2 y f6v3 no se tocaron. Respaldo de la base antes de escribir: `lab/hyperframes/f7/topics_db_pre_f7b.json` (sin commitear).
- **`RESEARCH_V3`:** existe la llave (`research_v3_enabled`: `RESEARCH_V3=1` o `topic["research_version"] == 3`), pero **no está cableada en `topic_researcher`**: el camino viejo queda byte-idéntico porque no se tocó. Cablear v3 como default de los seeds nuevos implica decidir qué reciben 4b–4e (los bloques angulares o el pool): queda para después de F7c.

## 6. Para que el analista mire

1. **Cifras canónicas: casi vacías.** Con cientos de datos, agrupar cifras «cercanas» juntaba capacidad (8,000 camas), población promedio (6,500) y el patio de Hunt (5,000). Ahora el grupo exige cifras a ≤ 1.25× y el mismo asunto (≥ 35 % de palabras en común), con el número pegado al sustantivo. Resultado: un solo grupo (6,295 del 30-jun-2005 contra el promedio de 5,919, Vera 2015). El 6,375 (dato del sheriff, en la ACLU y en The Lens) está como dato, pero no como canónica: el texto de la ACLU que lo atribuye a «las estadísticas del sheriff» trae dos conteos en la oración. Es heurística; si el analista quiere una cifra canónica fija, conviene decidirla a mano en el pool o con un paso de LLM.
2. **`presente_en` es ruidoso:** `evidence_pool.presence` agrega todos los eventos de las fechas en que el documento ubica a la persona; quien estuvo del 28-ago al 2-sep queda «presente» en decenas de eventos de otros edificios.
3. **Recorte a 300 k:** de los 400 testimonios de la ACLU (473 k caracteres) se leyeron 298 k; unos 150 testimonios quedaron sin leer. Subir el tope para colecciones de testimonios sube el costo (≈ US$ 0.4 más).
4. **Faltan** BBC 2006, prensa local de la semana del 29-ago-2005 (Times-Picayune, Toledo Blade) y el fallo Waganfeald: ninguna URL salió en el grounding (ver F7a). Norman («Simplemente abandonaron la cárcel») venía de la BBC: no está en este pool.
5. **Gusman** queda marcado testigo (estuvo en la cárcel) y antagonista; no es elegible como humano.

## 7. Veredicto del revisor-handoff (íntegro)

Después del veredicto se corrigió el total de descartados de §2 (decía 120; son 129, como suman los desgloses) y se actualizó `lab/ESTADO_SESION.md`. `topics_db_pre_f7b.json` (respaldo de `data/topics_db.json`) queda sin commitear, como el `topics_db_pre.json` de F5.

VEREDICTO: CUMPLE CON OBSERVACIONES

Los frenos están limpios y los números del pool real coinciden con F7b_pool.md. Quedan observaciones: el costo supera el techo, faltan pruebas que pide el handoff y ESTADO_SESION.md está desactualizado.

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Frenos: no tocar evidence.py, step_4b/4c/4d/4e, m01a/b/c, m03, fase*, gfx_*, topic_researcher | OK | `git diff c7da0ba..HEAD --stat` solo toca `lab/`, `researcher_steps/research_v3.py` (nuevo) y `test_module_f7.py`. |
| 2 | Ninguna URL fuera del grounding | OK | `fuentes_orleans.json`: las 20 fuentes aceptadas están en `_grounding` (35 chunks). Las 21 fuera quedan en `_descartadas` y F7a las lista. |
| 3 | §1.1 datos ≥ 5× | OK | `00_pool_v3.json`: 558 datos contra 91 en f6v3, o sea 6.1×. |
| 4 | §1.1 ≥ 15 citas de testigos con nombre y documento | OK | 25 citas `testigo` y `verificada` (20 autores). Sin las dos variantes de Gusman (el antagonista) quedan 22 citas de 18 autores con nombre propio. Como filtré los autores con una regex, el número exacto es aproximado. |
| 5 | §1.1 cronología con horas | OK | 28 de 152 entradas con `hora`. El pool viejo tenía 2 con hora (no lo recontrolé). |
| 6 | §1.1 100 % con doc_id + posición | OK | Los 1.205 ítems tienen `doc_id` y `offset`. Los reubiqué con `DocText.locate` sobre los txt de `fuentes/`: 0 no encontrados y 0 con offset distinto. Las 162 citas `verificada` también se encuentran en su documento. |
| 7 | Conteos de F7b_pool.md contra los datos | PARCIAL | Coinciden: 558, 152, 67, 188, 69 ítems, 162/25/1 en `verificacion`, 4 testigos con ≥3 citas, 13 elegibles y 35 con ≥2 documentos. Falla uno: §2 dice «Descartados en total: 120» pero `_descartados` tiene 129. Sus propios desgloses (66+46+8+8+1) suman 129. |
| 8 | F7a: ≥ 8 documentos bajados con tabla | OK | 10 con `ok`, y los txt están en `fuentes/` y en `manifest_orleans.json`. Los faltantes (BBC, Times-Picayune, Toledo Blade, fallo Waganfeald) están declarados como ✖. |
| 9 | Pruebas §5 | PARCIAL | Los 61 tests pasan (f6a, f6b, f6c y f7; f7 tiene 23). Hay pruebas de escaleta con el pool v3 y de llave apagada por defecto. Falta la integración «pool v3 → step_4b/4c/4d/4e»: F7b §5 admite que no se corrió. Tampoco hay test de `RESEARCH_V3=0` byte-idéntico; se sostiene solo porque `topic_researcher` no cambió. |
| 10 | Costo ≤ US$ 2.5 por tema (§1.3) | FALLA (declarada) | F7b §4: ≈ 2.6–2.8 en corrida limpia, y 3.2–3.4 gastados en la sesión. La corrida limpia es una estimación, no una medición de punta a punta. Dos corridas de R1 no registraron su costo. |
| 11 | topic `ba6c3cac-f7r3` nuevo; f5v2 y f6v3 intactos | NO VERIFICABLE | `data/` está en `.gitignore` (`.gitignore:11`), así que no hay diff. Existe el respaldo `topics_db_pre_f7b.json`, sin commitear. |
| 12 | Commit wip y ESTADO_SESION.md al día | PARCIAL | Hay 3 commits wip. Falta commitear `F7b_pool.md` y `topics_db_pre_f7b.json`. El ESTADO_SESION.md commiteado dice «F7b en marcha» y que HRW 2005 falta; ya no es cierto. El commit 153a84d no lo actualizó. |

Desvíos respecto del handoff, todos declarados en F7a o F7b:
- `pdftotext` va como primario, antes que `pdfplumber` (F7a decisión 6, F7b §3.1).
- Pro con temperatura 0.7 en R1 (F7a decisión 2).
- Los 4 focos de búsqueda más 5 pistas del analista, con reintentos.
- La llave `RESEARCH_V3` existe pero no está cableada en `topic_researcher` (F7b §5).
- Recorte a 300 k caracteres: se pierden unos 150 testimonios de la ACLU (F7b §6.3).
- La escaleta pasa de ≈ 8 k a ≈ 63 k tokens (F7b §5).
- Cifras canónicas casi vacías: solo un grupo (F7b §6.1).

Fuera de alcance: ninguno en los commits. Hay cambios sin commitear en `diag_234_cap4.py`, `gfx_profiles/lexico_propuestas.json` y `gfx_profiles/misterio.json`. Ya estaban en el git status inicial y no son de F7. `gfx_profiles` entra en la familia `gfx_*` de los frenos, así que conviene que no se cuelen en un commit de F7.

Riesgos que el contrato no cubre:
- Los autores verificados incluyen cargos y anónimos («Inmate #12», «un guardia»). El criterio de ≥ 15 testigos con nombre depende de cómo se filtre, y `presente_en` es ruidoso (lo admite F7b §6.2).
- Un pool de 63 k tokens puede degradar la escaleta en F7c; ahí hay que mirar el comportamiento.
- Los documentos y el topic nuevo viven en `data/`, que git ignora. Los datos y el topic no se pueden recuperar desde el repo.
