# HANDOFF F14 — La ficha reemplaza al digest (una prueba, Orleans)

Analista · 2026-10-23 · Para CC. Base: `2e13616` (rama `f11-guion-v4`; seguí en la misma). **Solo datos → escaleta → guion.** Sin imágenes, voz ni producción.

## 0. Por qué (medido del disco)
- El research de Orleans deja **1,033 ítems** (558 datos, 152 eventos, 187 citas, 162 verificadas, 43 documentos). La escaleta usa **32** (3 %). Ycuá: 509 → 40 (7 %).
- Se pierde en dos pasos: el **digest** (F7c: un resumen de Gemini de ~50 k caracteres hecho para bajar tokens; lo que omite no existe para la escaleta) y la **escaleta** (1 dato central + 0–3 apoyos por beat).
- Con largo abierto (F13), el guion dura lo que la escaleta da: Orleans queda en 6.3 min por este embudo, no por falta de research.
- La ficha de F12 ya hace lo que el digest debía hacer, pero con criterio y con rastro: selecciona, junta repetidos, separa contradicciones y descarta con motivo. Solo que hoy nadie la lee.

## 1. Cambios
**1.1 La ficha resuelve las contradicciones sola** (`researcher_steps/ficha_caso.py`), con 5 criterios generales que valen para cualquier tema. Van en el prompt de la ficha y cada decisión sale con su criterio al lado (`decision`, `criterio`, `otras_versiones`):
1. **Error de extracción** (lo que extrajo el pool no coincide con lo que dice el pasaje): gana el pasaje.
2. **Variantes de un nombre**: gana la forma del documento oficial o judicial; si no hay, la que más fuentes repiten.
3. **Conteos** (muertos, heridos, personas): gana la cifra oficial; si no hay, la que más fuentes repiten. Las otras quedan como `otras_versiones`, para que el guion pueda decir «otras fuentes hablan de…».
4. **Hechos disputados** (quién dio una orden, cómo estaban las puertas): **no se resuelven**. Pasan a la ficha como `versiones`, cada una con su fuente, para que el guion las cuente como versiones.
5. **Horas y fechas**: gana la que coincide en 2 o más fuentes; si ninguna, se marca `aproximada`.
Lo que no cae en ningún criterio queda en `contradicciones` como hoy (sin resolver), y se reporta.
Chequeo determinista igual que F12. **Un segundo campo: `personas_descartadas`** — las que el pool marca en `_descartados` pero que la ficha considera necesarias para la historia (caso Nagin: el alcalde que ordena la evacuación), con el motivo. La escaleta puede usarlas.

**1.2 La escaleta lee la ficha, no el digest** (`m01a_escaleta.pool_section`): si existe `ficha_caso.json`, el prompt de la escaleta lleva la ficha completa (hechos, cronología, cifras con unidad, citas, personas, versiones) con sus ids, y **no** el digest. Sin ficha, todo igual que hoy (test byte-idéntico).
- `datos_apoyo` por beat: de 0–3 pasa a **0–6**. Es el único número que cambia en la escaleta, y es para dejar pasar material, no una regla.
- Los ids de la ficha son los mismos del pool, así que el guion, m03 y gfx no cambian nada.

**1.3 El guion v4 recibe los datos de la ficha** (`guion_v4.data_line`): el texto de cada id sale de la ficha (hecho limpio, cifra con unidad, cita corregida) cuando existe; si no, del pool. Largo **abierto** (F13). Sol high.

## 2. Prueba (solo Orleans `ba6c3cac-f7r3`)
1. `ficha_caso` de Orleans con los criterios → `FICHA_orleans.md` + `ficha_caso.json`.
2. **Escaleta nueva** con la ficha (`fase1_5 --v3 --only m01a` o el runner equivalente), sin notas. Guardá la escaleta de F7c-3 aparte (`01a_escaleta_f7c3.json`): no se pisa.
3. Guion v4 abierto con Sol sobre esa escaleta.
- Salidas en `lab/hyperframes/f14/`: ficha, escaleta, `NARRACION_orleans_f14.md`, `guion_orleans_f14.json`, prompts con md5.
- **`compara_f14.html`**: Orleans **F13 abierto (digest + escaleta F7c-3)** | **F14 (ficha + escaleta nueva)**, por cap, con palabras, minutos, bloqueantes, ids distintos usados, citas y las frases marcadas. Arriba: ítems del pool → ítems en la ficha → ítems en la escaleta → ítems en el guion, en las dos versiones.
- **Tope: US$ 1.50.**

## 3. Frenos
- No se toca `00_pool_v3.json`, `research_v3.py`, `m05`, `evidence.py`, `guion_v3_reglas.py`, `config.py` ni `topics_db`.
- **Cero reglas nuevas** para el guion; los 5 criterios son de la ficha.
- Sin merge; no commitear `.env` ni `lab/_gpt_probe_analista/`.
- Tests sin red: criterios (un caso por criterio), escaleta sin ficha byte-idéntica, `data_line` con y sin ficha, apoyos 0–6. Suites verdes + las 5 fallas previas. Test dorado de v3 verde.
- Actualizar `lab/ESTADO_SESION.md`.

## 4. Reporte `lab/hyperframes/f14/F14_REPORT.md`
1. Embudo en números: pool → ficha → escaleta → guion (F13 vs F14).
2. Contradicciones de Orleans: cuántas resolvió cada criterio y cuántas quedaron.
3. Qué pasó con Nagin.
4. Costo y tokens.
5. Veredicto íntegro del revisor-handoff.

## 5. PARADA
Commit + reporte → **PARADA**. El analista lee la ficha, la escaleta y el guion y le dice a Omar si el video ganó material y filo, o no.
