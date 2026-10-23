# HANDOFF F12 — Ficha del caso (depurar los datos antes del guion) · Ycuá

Analista · 2026-10-23 · Para CC. Base: `967859f` (rama `f11-guion-v4`; seguí en la misma). **Solo datos.** En esta tanda no se corre ni la escaleta ni el guion, ni imágenes, voz o producción.

## 0. Decisión de Omar
- **Guionista: GPT-6.1 Sol (high), con el prompt de F11c, y nada más.** Se terminaron las pruebas de modelos.
- **Los datos se depuran antes del guion.** Hoy el guionista recibe un pool crudo de 509 ítems con contradicciones, errores de transcripción y cifras ambiguas. Casos reales de Ycuá:
  - el hijo de Paiva se llama «Emiliano» en F05 y «Víctor Daniel» en F09, F10, F15 y F16;
  - la cita Q34 dice «portó» (por «portón»);
  - el «600» aparece como temperatura y también como capacidad de personas.
- La ficha es la **única fuente** de la escaleta y del guionista: lo que no está en la ficha no existe.

## 1. Qué construir — `researcher_steps/ficha_caso.py`
**Entrada:** `data/scripts/_steps/<topic>/00_pool_v3.json`.
**Salida:** `ficha_caso.json` + `FICHA_<topic>.md` (para leer en el teléfono), en `_steps/<topic>/` y en `lab/hyperframes/f12/`.

**Una llamada a GPT-6.1 Sol (high)** con el pool completo (ids incluidos). Usá la estructura de F11c: rol y tarea en el sistema, los datos en el usuario y la tarea al final. Le pide:

| sección | contenido |
|---|---|
| `personas` | Un nombre canónico por persona, su rol, las variantes encontradas y los ids. Si dos fuentes dan nombres distintos, la persona va a `contradicciones`, **no se elige**. |
| `cronologia` | Los eventos del día en orden, con fecha y hora tal como están en el pool, y sus ids. |
| `hechos` | Entre 60 y 80 hechos útiles para contar la historia. Cada uno en una oración limpia, con sus ids de origen. Sin interpretación. |
| `cifras` | Una cifra por conteo (muertos, heridos, huérfanos, personas adentro…), con la fuente y las otras versiones. Cada cifra con su **unidad** (personas, °C, años): nunca un número sin qué cuenta. |
| `citas` | Las mejores 15–25 citas: autor, rol, estado de verificación y el texto. Un error evidente de transcripción se corrige y se guarda el original («portó» → «portón», con `original`). |
| `contradicciones` | Cada conflicto entre fuentes, con las versiones lado a lado, `doc_id` y `offset`. **No se resuelve:** decide Omar. |
| `descartados` | Lo que se dejó afuera por dudoso o fuera del caso, con el motivo, en una línea. |

**Chequeo determinista después de la llamada** (es control de la ficha, no una regla del guion):
- todo ítem de la ficha cita ids que existen en el pool;
- toda cifra, hora y fecha de la ficha aparece en el texto de esos ids;
- toda cita corregida está a ≤ 3 caracteres de distancia de su original (Levenshtein);
- si algo falla, sale de la ficha y va a `descartados` con el motivo «no respaldado». No hay reintento.

**Chascada:** el modelo por defecto del guion v4 pasa a ser `gpt-6.1-sol` en esfuerzo high (en el código de v4, no en `config.py`).

## 2. Corrida
- Solo Ycuá (`f8s1-ycua-bolanos`). **Tope US$ 0.50.**
- `FICHA_ycua.md`, en este orden:
  1. contradicciones (arriba, porque es lo que hay que decidir);
  2. personas;
  3. cifras;
  4. cronología;
  5. hechos;
  6. citas;
  7. descartados.

  Cada ítem lleva sus ids en letra chica, y arriba van los conteos de cada sección.
- Los nombres de las contradicciones de Ycuá que ya conocemos (Paiva hijo) tienen que salir ahí. Si no salen, decilo en el reporte.

## 3. Frenos
- No se tocan `00_pool_v3.json`, la escaleta, `guion_v4.py` (salvo el modelo por defecto), `m01a`, `m05`, `evidence.py`, `config.py` ni `topics_db`.
- **Cero reglas nuevas** para el guion.
- Sin merge; no commitear `.env` ni `lab/_gpt_probe_analista/`.
- Tests sin red: el esquema de la ficha, el chequeo determinista (id inexistente, cifra no respaldada, cita corregida de más) y el modelo por defecto del v4. El test dorado de v3 queda verde y las suites, verdes + las 5 fallas previas.
- Actualizar `lab/ESTADO_SESION.md`.

## 4. Reporte `lab/hyperframes/f12/F12_REPORT.md`
1. Conteos por sección y lo que sacó el chequeo determinista.
2. Costo y tokens.
3. Veredicto íntegro del revisor-handoff.

## 5. PARADA
Commit + reporte → **PARADA**. El analista lee la ficha del disco y se la pasa a Omar con las contradicciones para que decida. Recién después se cablea la ficha a la escaleta y al guionista, en otra tanda.
