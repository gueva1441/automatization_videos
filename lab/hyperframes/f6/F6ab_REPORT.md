# F6a + F6b — Testimonios en el research y escaleta v3 · PARADA para el analista

Rama `f6-guion-v3`, sale de `45c052c`. `main` no se tocó. Handoff: `HANDOFF_F6_guion_v3.md`. Topic de laboratorio: `ba6c3cac-f6v3`. Copia los pasos de investigación de `ba6c3cac-f5v2`, que no se toca porque es el video producido; `topics_db.json` tampoco cambia.

**Para validar desde disco:**
- `lab/hyperframes/f6/ESCALETA_orleans.md` (legible);
- `lab/hyperframes/f6/escaleta_orleans.json` (= `data/scripts/_steps/ba6c3cac-f6v3/01a_escaleta.json`);
- `lab/hyperframes/f6/F6a_testimonios.md`.

## Lo que se hizo

### F6a — testimonios
- **Research:** `topic_researcher.TESTIMONIOS_SECTION` agrega `[TESTIMONIOS]` a los ángulos humano y misterio. Pide citas textuales de quienes estuvieron ahí, con nombre, rol, fecha y fuente; si no hay, «SIN TESTIMONIOS CON NOMBRE» más los anónimos. El ángulo técnico queda igual (sigue con `[DATOS DE MAGNITUD]`). `research_testimonios(seed)` es una query solo de esa sección.
- **Pool** (`researcher_steps/evidence_pool.py`):
  - las citas llevan `rol` y `testimonio` (true si quien habla estuvo ahí);
  - los personajes llevan `testigo`, `fechas_presente` (lo que dice el LLM) y `presente_en` (`presence`: ids de la cronología que lo nombran, más los de las fechas en que el research lo ubica);
  - `add_block` suma un bloque nuevo a un pool existente sin tocar los ids viejos;
  - la fuente de una cita se resuelve también por su línea («"…" — Nombre, rol — ACLU, 2006»).
- **Orleans** (`f6a_testimonios_orleans.py`): 1 Pro + Google Search, 42 s, **US$ 0.03**.
  - **9 citas testimonio** (antes: 0; las 2 que había eran del sheriff), 8 con fuente resuelta (solo Q04 no tiene).
  - **4 testigos con nombre:** P08 Edward «Edgar» Burton (preso), P09 Vincent Norman (preso), P10 Rhonda Ducre (guardia) y P12 Lenore Burnley (madre de Chad Joseph). Más dos anónimos, «un preso de 19 años del TCI» y «una presa del TCI».
  - También entraron 25 datos, 3 eventos y 4 lugares nuevos. Los ids viejos (D57, D19, T05…) no cambiaron.

### F6b — `script_engine/m01a_escaleta.py`
- **Una llamada a Pro** (`call_pro_json`, schema JSON) con el pool completo, citas y personas con sus marcas (TESTIMONIO, TESTIGO, ANTAGONISTA, «estuvo en»), las cifras canónicas, 2 escaletas de ejemplo de otros temas (Sago 2006, Triangle 1911; solo la forma) y las reglas del handoff §2.2, §3 y §4. Hasta 3 intentos con las correcciones del validador. `PROMPT_VERSION f6b-2`.
- **Validador determinista:**
  - **Rechaza y reintenta:**
    - 7–12 beats; los 7 caps cubiertos en orden; el beat 1 es el gancho del cap 1;
    - un dato central por beat, existente, y cada id en un solo beat;
    - intensidad 1–5 sin bajar hasta el pico; el pico no es el último beat y después hay un respiro de intensidad 1;
    - humano del pool (o colectivo con fuente y sin nombre inventado), en escena en ≥ 3 caps y antes del cap 3, **siempre con un dato suyo en el beat**;
    - antagonista del pool;
    - promesa y la imagen del gancho sin cifras;
    - imagen sensorial concreta, no una idea.
  - **Repara y lo anota:** palabras por cap (110 / 190×5 / 110, ±15 %); ids de apoyo inexistentes o repetidos; `pico.id`; el nombre exacto del humano.
  - **Rúbrica de la pregunta de pantalla** (último beat de cada cap): ≤ 8 palabras, ¿…?, culpa / consecuencia / destino, nada administrativo, sin nombres nuevos, nombra algo ya visto. Si en el último intento no pasa, queda `pregunta_valida: false` (el respaldo es `gfx_question`) y la escaleta no se rechaza.
- **Hereda de m01a_skeleton**, sobre una vista de caps: `finalize_pool_plan` (`canonize_figures` + `assign_screen_ids`, con los reservados para pantalla por cap) y el cliffhanger = el dato central del primer beat del cap siguiente.
- **`frozen_escaleta`:** token `escaleta_frozen`, o `skeleton_frozen` apuntando a una escaleta. Traduce ids por texto, como `frozen_skeleton`.
- **`is_v3`:** pool más `GUION_V3=1` o `guion_version: 3`.
- **`to_markdown`:** la escaleta legible.
- **Frenos (§5):** el diff de la rama no toca `m01a_skeleton`, `m01b_narrator`, `evidence.py`, m03, fase2a/2b ni `gfx_*`. `generate_skeleton` sigue igual (camino v2).
- **Tests:** `test_module_f6a.py` (3) y `test_module_f6b.py` (19). Suites: 432 verdes + las 3 fallas viejas de `01b_pauses`.

## La escaleta de Orleans (f6b-2)
- **Humano:** Vincent Norman (P09), preso; en escena en los caps 2, 3 y 4, cada uno con una cita suya (Q04, Q05 y Q06).
- **Antagonista:** Gusman.
- **Gancho:** imagen «Oscuridad total, el sonido del agua de la tormenta golpeando las paredes de la prisión.». Promesa: «Abandonaron a miles de personas en celdas inundadas. Esta es la historia de los cuerpos que vieron y los cientos que nunca aparecieron.».
- **Curva:** 2 → 2 → 3 → 4 → **5** (pico, beat 5: los cadáveres flotando, D60) → **1** (respiro: Lenore Burnley y la foto de Chad Joseph) → 3 (517 sin contabilizar y el sheriff que niega) → 2 (los US$ 650,000 a dos turistas).
- **Preguntas de pantalla:**
  - cap 1: «¿Por qué se apagaron las luces?» ⚠ (marcada por la heurística; ver dudas);
  - cap 2: «¿Quién decidió dejarlos allí dentro?»;
  - cap 3: «¿Cuánto tiempo los dejarían en el agua?»;
  - cap 4: «¿Por qué los guardias abandonaron sus puestos?»;
  - cap 5: «¿Cuántos cuerpos más había en el agua?»;
  - cap 6: «¿Dónde están los 517 desaparecidos?»;
  - cap 7: «¿Cuántas historias siguen sin contarse?».
- **Reservados para pantalla** (no se narran): cap 1 T09, T10 · cap 5 T04, T16 · cap 6 T23 · cap 7 D65, T12.
- **Costo de F6b:** US$ 0.48 (dos corridas de 3 intentos: f6b-1 y f6b-2; ver D7). La f6b-1 quedó guardada para comparar: `escaleta_orleans_f6b1.json` y `ESCALETA_orleans_f6b1.md`.

## Decisiones
- **D1 (topic)** Orleans v3 va en su propio topic (`ba6c3cac-f6v3`, solo en `data/scripts/_steps/`). El topic se arma en memoria desde el de f5v2 en `topics_db` (hook, misterio, ángulo) con el pool nuevo; `topics_db.json` no se toca hasta F6c/d.
- **D2 (re-research)** «Solo para esa sección»: una query propia (`TESTIMONIOS_ANGLE`) con la misma maquinaria del deep research (Pro + Google Search + backoff), y `add_block` para no renumerar el pool. Los ángulos humano y misterio llevan `[TESTIMONIOS]` en topics nuevos, sin re-investigar el resto de Orleans.
- **D3 (presencia)** `presente_en` combina dos señales deterministas: la cronología que nombra al personaje (apellido) y las fechas en que el research lo ubica (`fechas_presente` del LLM). Sin fechas ni menciones queda vacío. Burton, Norman y Burnley quedan vacíos: sus testimonios no tienen fecha.
- **D4 (bug encontrado)** La primera corrida de `add_block` pasaba el filtro de acción solo sobre el bloque nuevo, y sacó a Strock, Waganfeald, Kunkel y Morgan del pool. Ahora usa todos los bloques del research más el nuevo; el único que sale es Chad Joseph, que no hace nada en el research (murió).
- **D5 (escala y preguntas)** La intensidad va de 1 a 5 (el handoff no fija la escala; el respiro es 1). La pregunta de pantalla va solo en el último beat de cada cap: en los otros beats se vacía, porque es la pregunta de cierre del cap.
- **D6 (heurísticas)** Para «imagen sensorial» se rechaza solo lo abstracto (todas las palabras de contenido son ideas: desesperación, injusticia, sistema…). Una lista de palabras sensoriales rechazaba imágenes buenas (asfalto, sol, pies). Para «nombra algo ya conocido» cuenta el título del video, la promesa, el humano y los textos de los datos y las imágenes vistas hasta ese cap (por raíz de 5 letras). El cap 7 no lo exige: su pregunta es la que se queda, como «¿Cuántos siguen sin nombre?» del handoff.
- **D7 (humano respaldado; f6b-1 → f6b-2)**
  - En la f6b-1, Norman estaba «en escena» en beats donde no había nada suyo (la conferencia del sheriff, el paso elevado, el tribunal). Eso empuja al guionista de F6c a inventarle presencia.
  - Regla nueva (prompt y validador): en escena solo con un dato suyo en el beat (su cita o una mención), en ≥ 3 caps, o en tantos como datos suyos tenga el pool.
  - Con eso se regeneró. La f6b-1 queda como comparación.
- **D8 (reintentos)** Las dos corridas usaron los 3 intentos. En la f6b-1, los rechazos 1 y 2 fueron sobre todo mis heurísticas viejas (D6). En la f6b-2, preguntas que no pasaban la rúbrica y el humano en 2 caps; la tercera pasó.

## Dudas para el analista
1. **El humano no llega al final.** Norman tiene 3 citas en el pool, y la escaleta lo sigue en los caps 2–4. Después lo reemplazan Lenore Burnley (respiro) y el cierre humano, que cita al abogado Eric Balaban (Q10, que no es testigo). ¿Se acepta, se busca más de Norman (otra query de ~US$ 0.03), se suma un colectivo para los caps 5–7 o el final humano se le pide a Burnley?
2. **Los testimonios no están verificados.** Las atribuciones salen de Gemini con búsqueda: Burton → The Lens, 2025; Norman → ACLU 2006 y el documental «Prisoners of Katrina»; Q04 (Norman) quedó sin fuente. El candado literal garantiza que el texto está en el research, no que el research acierte. Antes de un video público, conviene cotejar Norman y Burton contra el informe de la ACLU.
3. **Pregunta del cap 1:** «¿Por qué se apagaron las luces?» está marcada porque «luces» no aparece en lo visto (se dijo «energía eléctrica»). Es un falso positivo de la heurística por raíz. ¿Se afina con sinónimos o se acepta el respaldo de `gfx_question`?
4. **Reservados para pantalla** (algoritmo heredado de F5d, por palabras en común): T04 («los reclusos reciben su última comida», del 28/29 de agosto) cae en el cap 5 y T12 (el pedido de ayuda del sheriff, 29 de agosto) en el cap 7. Los caps 2–4 no tienen reservados. Con la escaleta podrían ir al beat cuyo tiempo de relato coincide. ¿Se cambia en F6d o se deja?
5. **517 y «más de 500»** (D19 y D59) están en el mismo beat. La regla de un contador por hecho vive en gfx; el guionista (F6c) tendría que recibir «usá 517».
6. **El gancho abre con T08** (29 de agosto: se corta la luz) y el cap 2 vuelve al 28 (el anuncio del sheriff): es un salto adelante a propósito, solo un aviso. El apoyo D03 («Evento principal: huracán Katrina.») es un rótulo, no un dato.
7. **«El mismo token» de `frozen_escaleta`:** lo interpreté como que sirve `skeleton_frozen` (si apunta a una escaleta) además de `escaleta_frozen`.

## Veredicto del revisor
(íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

Las observaciones son de forma, no de fondo. No encontré datos inventados ni frenos violados.

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Rama f6-guion-v3 desde 45c052c, sin merge a main | OK | `git log 45c052c..HEAD`: solo 97c10ec (f6a) y 4b41280 (f6b) |
| 2 | §5 FRENOS intactos (m01a_skeleton, m01b_narrator, evidence.py, m03, fase2a/2b, gfx_*, normalizer, TTS) | OK | `git diff 45c052c --stat` solo toca evidence_pool.py, topic_researcher.py, `script_engine/m01a_escaleta.py` (nuevo), tests y lab. Los cambios en `diag_234_cap4.py`, `gfx_profiles/lexico_propuestas.json` y `gfx_profiles/misterio.json` son ajenos y estaban sin commitear. |
| 3 | Camino v2 sin pool intacto (`generate_skeleton`) | OK | m01a_skeleton y m01b_narrator sin diff. m01a_escaleta solo importa de m01a_skeleton. Las suites f5* y 03_anchor pasan. |
| 4 | F6a: `[TESTIMONIOS]`, `testigo`/`presente_en`, Orleans con testimonios | OK | El pool v3 tiene 9 citas con `testimonio: true` y 4 testigos (P08, P09, P10, P12). Los ids viejos (D57, D19, T05) no cambiaron. |
| 5 | F6b: escaleta de Orleans, reglas §2.2/§3/§4 | OK | `data/scripts/_steps/ba6c3cac-f6v3/01a_escaleta.json` es idéntico a `lab/hyperframes/f6/escaleta_orleans.json`. Detalle en las observaciones. |
| 6 | Ningún nombre ni cita inventados | OK | Cotejé los 21 ids de los beats contra `01_facts_sources.json` y todos existen. Q04, Q05, Q06 son de Norman, Q08 de Burnley y Q10 de Balaban, y el texto de `cierre_humano` coincide con Q10 literal. "Dos turistas" sale de D69. Ningún id se repite entre beats. |
| 7 | Reglas de la curva | OK | Intensidad 2-2-3-4-**5**-1-3-2. El pico (beat 5) no es el último. El respiro de intensidad 1 es el beat 6. El humano Norman está en los caps 2, 3 y 4, cada uno con una cita suya. |
| 8 | Palabras por cap y reservados para pantalla | OK | Caps: 110 / 190 / 190 / 190 / 95+95 / 190 / 110. Reservados: cap 1 T09, T10; cap 5 T04, T16; cap 6 T23; cap 7 D65, T12. Coincide con el reporte. |
| 9 | Preguntas de pantalla (rúbrica) | PARCIAL | Seis de las siete pasan. La del cap 1 («¿Por qué se apagaron las luces?») queda con `pregunta_valida: false`. El reporte lo declara y es el caso previsto: queda el respaldo `gfx_question`. |
| 10 | Gancho sin cifras | OK | La promesa y la imagen del beat 1 no llevan cifras. La promesa dice "miles", sin dígitos. |
| 11 | Reporte: costos, conteo de tests, decisiones | OK | f6a: US$ 0.0274 (≈0.03). f6b: 0.2416 + 0.2427 = 0.4843 (≈0.48), 3 intentos cada una. Tests: 432 passed y 3 failed, y las 3 son las viejas de 01b_pauses. |
| 12 | Bytes 0x08 en .py | OK | Ninguno en m01a_escaleta, evidence_pool, topic_researcher, los tests ni los .py de lab/f6. |
| 13 | Cierre del flujo: ESTADO_SESION, revisor, commit | PARCIAL | Ver observación 1. |

Observaciones:
1. `lab/ESTADO_SESION.md` quedó viejo. Dice "F6b en curso" y "Falta: F6b…", pero la escaleta ya existe. Hay que actualizarlo antes del commit final.
2. Tampoco hay commit final. Los archivos de `lab/hyperframes/f6/` están sin commitear: F6ab_REPORT.md, ESCALETA_*.md, escaleta_orleans*.json, f6b_run.out, f6b_frozen.out. La sección "Veredicto del revisor" del reporte está vacía, a la espera de este veredicto.
3. El reporte dice "9 citas testimonio, 7 con fuente", pero el pool tiene 8 con fuente. Solo Q04 no tiene. El error es menor y va en contra de lo que logró el trabajo.
4. La escaleta tiene debilidades de contenido que el reporte ya declara, y las confirmé:
   - El humano (Norman) desaparece desde el cap 5. El cierre usa a Balaban (Q10), que no es testigo.
   - Q04 de Norman no tiene fuente.
   - D03 es un rótulo, no un dato.
   - Beat 2 retrocede en el tiempo, del 28 al 29 de agosto.
   - D19 (517) y D59 (más de 500) están en el mismo beat.
   - T04 y T12 caen como reservados en caps 5 y 7, aunque pertenecen a los caps 2-4.

Fuera de alcance: ninguno atribuible a este trabajo. Los tres archivos ajenos sin commitear son los que Omar indicó.

Riesgos que el contrato no cubre:
- Los testimonios (Burton y Norman) vienen de Gemini con búsqueda y no están cotejados contra el informe de la ACLU. El candado literal solo asegura que el texto está en el research, no que sea cierto.
- El validador de gancho "primera frase sin año, cifra ni institución" (§3) todavía no corre sobre prosa. Solo se validan la promesa y la imagen. Queda para F6c.
- El tema f6v3 solo existe en `data/scripts/_steps/`. Si `topics_db.json` no se actualiza en F6c/d, nada lo apunta.

**Qué se hizo con las observaciones (CC):**
- 1 y 2: ESTADO_SESION actualizado; commit final con todo lo de `lab/hyperframes/f6/`.
- 3: corregido a 8 con fuente.
- 4 y riesgos: quedan como dudas 1–6 de este reporte, para F6c/d.
