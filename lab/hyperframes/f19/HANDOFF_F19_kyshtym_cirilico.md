# HANDOFF F19 — Kyshtym otra vez: cirílico en el research, antagonista institucional, beats según la compuerta

Analista · 2026-10-24 · Para CC (misma sesión). Base: `29da90c` (rama `f11-guion-v4`). Research → ficha → columna → escaleta → guion, **sin paradas** (Omar dio el OK a los tres arreglos). Sin producción.

## 0. Por qué (del reporte F18 y del disco)
- La cadena nueva funcionó hasta la columna (Tumerman, pico en la explosión, 3 personas). La escaleta paró.
- Tres causas, ninguna del tema:
  1. **El research no lee cirílico.** `place_re` del seed se arma solo con nombres latinos; `names_event` (research_v3.py:581) descarta los 5 documentos rusos (113 k chars) y el pool sale de 5 fuentes en inglés. Es la raíz del pool flojo.
  2. **Antagonista = persona.** `validate` exige un P## del pool (m01a_escaleta.py:665). En Kyshtym decide una institución. En Orleans F15 el modelo también lo dejó vacío.
  3. **Rango de beats:** con compuerta amarilla, `validate` exige 7–8 (`gate_yellow_max_beats`) pero el sistema v2 dice «de 7 a 14». El modelo recién se entera en la regeneración.

## 1. Arreglos (son correcciones de forma; no agregan ningún chequeo)
**1.1 Cirílico en el research** (`research_v3.py` y el perfil del seed; es la única vez que se toca research en esta serie, y solo esto):
- El perfil del seed lleva `nombres_locales`: las formas del lugar y del evento en el idioma local (para Kyshtym: «Кыштым», «Маяк», «Озёрск», «Челябинск-40», «Кыштымская авария», «ВУРС»). Las genera el mismo paso que hoy genera el perfil (Pro), pidiéndole explícitamente las formas en el alfabeto del `idioma_local`.
- `place_re` se arma con los nombres latinos **y** los locales, con `re.I` y sin depender de `\b` (en cirílico `\b` falla con Python para algunos límites; usar lookarounds de letra `(?<![\w])…(?![\w])` con `re.UNICODE`).
- `names_event` no cambia; solo recibe el `place_re` nuevo. `focus_text` igual.
- Test: un texto en ruso con «Кыштым» pasa `names_event`; el mismo texto sin ninguna forma no pasa; Orleans y Ycuá dan el mismo `place_re` que antes para los nombres latinos (los locales son adicionales).
- **Rehacer el research de Kyshtym** con el mismo seed, mismo topic id (`f18-kyshtym-mayak`, respaldando el pool de F18 como `00_pool_v3_f18.json`). Tope US$ 3.00. Reportar cuántos ítems aportan las fuentes rusas.

**1.2 Antagonista persona o institución:**
- `antagonista` acepta `tipo: "persona" | "institucion"`. Persona: P## del pool, como hoy. Institución: `nombre` tiene que ser una organización que aparece **literal** en la ficha (sección `personas` con rol institucional, o en el texto de ≥ 2 hechos). El chequeo es el mismo de siempre («existe en la ficha»), con dos fuentes posibles.
- Sin ficha (camino v3), nada cambia.
- Test: Orleans con Gusman (persona) pasa; Kyshtym con «el Ministerio de Construcción de Maquinaria Media» pasa si está en ≥ 2 hechos; «la KGB» sin aparecer en la ficha no pasa.

**1.3 Beats según la compuerta:** el sistema v2 de la escaleta no cambia (sigue literal). El **usuario** lleva, antes de `<tarea>`, una línea que ya existe en el camino v3 (`rules_text` la tiene): «Esta escaleta lleva entre {min} y {max} beats» con los valores del perfil de la compuerta (verde 7–14, amarillo 7–8). No es una regla nueva: es decirle el rango que `validate` ya exigía.

## 2. La cadena (sin paradas; decisiones como en F18 §2)
| paso | tope |
|---|---|
| research v3 con cirílico + compuerta | 3.00 |
| ficha v2 | 0.60 |
| columna | 0.30 |
| escaleta v2 (una regeneración; si falla, PARADA con el crudo guardado) | 0.60 |
| guion v5.1 | 0.30 |
| **total** | **5.00** |
- Compuerta roja: PARADA. Amarilla o verde: seguir.
- Las citas que el modelo tradujo (F18 §lo que rompió): la ficha guarda la cita en el idioma original en `texto` y una traducción en `traduccion`; el chequeo compara `texto` con el pool, como siempre. El guion usa `traduccion` cuando existe (una línea en `data_line`). Es formato, no regla.

## 3. Salidas
- `lab/hyperframes/f19/`: `POOL_GATE.md`, `FICHA_kyshtym.md`, `COLUMNA_kyshtym.md`, `ESCALETA_kyshtym.md`, **`NARRACION_kyshtym_f19.md`**, prompts con md5, `costos_f19.json`.
- `compara_f19.html`: embudo F18 | F19 (documentos → ítems, por idioma de fuente), columna, y el guion por cap (bloqueantes, personas, escenas, frases marcadas).
- `F19_REPORT.md`: cuánto aportó el cirílico; antagonista elegido; beats; costo; veredicto íntegro del revisor-handoff.

## 4. Frenos
- Los tres cambios de §1 y nada más. Cero chequeos nuevos.
- No tocar `config.py`, `topics_db` salvo el topic, `m03*`, `gfx_*`, voz, producción.
- Sin merge; no commitear `.env` ni `lab/_gpt_probe_analista/`.
- Tests: los tres de §1 más la suite verde + las 5 previas; dorado de v3 verde; sin ficha, escaleta byte-idéntica.
- Actualizar `lab/ESTADO_SESION.md`.

## 5. PARADA (única, al final)
Commit + reporte → PARADA. El analista revisa el diff y lee ficha, columna, escaleta y guion. Si Kyshtym da ≥ 8, producción.
