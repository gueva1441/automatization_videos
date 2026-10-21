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
