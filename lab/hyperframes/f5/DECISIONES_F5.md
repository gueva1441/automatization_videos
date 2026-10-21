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
