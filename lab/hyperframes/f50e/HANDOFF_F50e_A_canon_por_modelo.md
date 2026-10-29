# HANDOFF F50e-A — ¿Qué modelo arma mejor el canon? Flash vs Sonnet 5.5 vs Opus 5.5, en texto (lab)

Analista · 2026-10-28 23:10 · rama `f11-guion-v4` · tema Wittenoom `123bbb64-9fca-4395-8bf4-57d60e219ef1`.
Reemplaza la parte D pendiente de F50d **solo en el orden**: D (m03 con Opus + papel) corre después, con el canon que gane acá.

## Por qué
F50d: el canon (ficha visual del tema: época por tramos de años + grupos de gente con su ropa por tramo) lo arma **una llamada a Gemini Flash**. En 3 corridas con el mismo pedido salieron 3 canons distintos (11 / 6 / 6 grupos; tramos hasta 1966 / hasta 2026 / hasta 2026). La corrida que quedó en producción no tiene ningún tramo después de 1966 → las fotos de 1971–2024 (caps 5–7) reciben ropa y tecnología de los 60. La pregunta de esta tanda: **¿un modelo más fuerte cubre todo el material sin cambiar el pedido?** Una sola variable: el modelo. El pedido, el esquema y la ficha no se tocan.

## Simulación del analista (datos de F50d, solo fotos con año en el ancla)
Medida: fotos cuyo año cae dentro de algún `era_visual_canon.periods` (años leídos con la regla de `m03_visual._tramo`).

| corrida Flash (F50d) | periods | fotos con año en el ancla cubiertas |
|---|---|---|
| 1 (la de producción) | 1937-1957 · 1958-1966 | 14/28 |
| 2 | 1937-1966 · 1966-2026 | 28/28 |
| 3 | 1937-1966 · 1978-2026 | 27/28 |

Hallazgo de la simulación (no es parte de la tanda, va a «abierto»): sacar «los años de la ficha» con una regex da falsos años (1040, 1160, 1190, 1210, 1230, 1250, 1400, 1450, 1510, 1850 en la ficha de Wittenoom: cantidades y códigos, no años). Si después hace falta pasarle a Flash la lista de años, tiene que salir de un campo de fecha, no de una regex sobre el texto.

## Constantes
| valor | origen | quién |
|---|---|---|
| modelos: Flash (el de `gemini_helpers.call_flash_json`, como hoy), `claude-sonnet-5-5`, `claude-opus-5-5` | Omar 2026-10-28 23:04 | Omar |
| 3 corridas por modelo (9 en total) | voto del analista, Omar 23:04 («si dale») | Omar |
| effort Opus `high` | `guion_v4.ESFUERZO["claude-opus-5-5"]` (existente, el mismo de m03) | existente |
| effort Sonnet `high` | el mismo de F47b (k7), para que cambie solo el modelo | F47b, Omar 03:19 |
| tope US$ 1,00 | Omar 23:04 | Omar |
| 9 llamadas en paralelo | preferencia de Omar: workers al máximo | Omar |
| año de cada foto = `anio_ancla` o `respaldo[0]` del expediente | `m03_visual._render_prompts_seedream` (F50d B, existente) | existente |

Ningún otro número entra. Si hace falta uno: PARADA y se pregunta.

## Módulos
Producción: **ninguno**. No se toca `step_4e_visual_canon.py`, `fase1_5.py`, `m03_*`, topics_db ni `05_visual_canon.json`.
Lab, nuevos en `lab/hyperframes/f50e/`:
- `canon_modelos.py`: las 9 llamadas en paralelo y la medida.
- `canon_<modelo>_<n>.json` (9), `CANON_MODELOS.md` (la tabla), `F50e_A_REPORT.md`.

## Paso 0
1. md5 de este handoff contra el del prompt.
2. `DECISIONES.md`, tal cual: `- 2026-10-28 23:04 · **F50e-A:** el canon de Wittenoom se mide en texto con Flash, Sonnet 5.5 y Opus 5.5 (3 corridas cada uno, mismo pedido, effort high en los Claude); la medida es por código (fotos cuyo año cae en un tramo, grupos y su ropa por tramo, varianza entre corridas); tope US$ 1; no toca producción; después decide Omar el modelo y recién ahí corre D de F50d · Omar · F50e-A`
3. `lab/TOPE_TANDA.json` = `{"usd": 1.0, "desde": <ahora>}` (fuera de git).

## Parte única — las 9 corridas
1. Mismo armado que `step_4e.canon_desde_ficha(topic, ficha)` (el pedido de `pedido_canon` y `VISUAL_CANON_SCHEMA_FICHA`). Para Sonnet y Opus, la llamada a Flash se reemplaza en el proceso de lab por un ruteador por hilo hacia `claude_helpers.call_json(prompt, model=…, response_schema=<el mismo esquema>, effort="high")`, como el ruteador de F47 (ajuste de transporte, no de texto). El texto del pedido no cambia: comprobá que el md5 del pedido es el mismo en las 9 y pegalo.
2. **Cuidado con el respaldo callado:** `extract_visual_canon` devuelve un canon vacío si la llamada falla. En el lab, un canon vacío o sin `periods` cuenta como **falla** y se reporta con el error; no se mide como si fuera un canon.
3. Nada se guarda en topics_db ni en `05_visual_canon.json`. Costos con `cost_tracker` en una sesión `f50e-canon-modelos`; el costo por modelo sale de las entradas de `cost_history` (descripción con modelo y n.º de corrida).
4. Medida por corrida, toda por código:
   - a. `periods` tal cual (years);
   - b. **fotos cubiertas:** de las 96 fotos de `03_visual.json`, cuántas tienen año (`anio_ancla` o `respaldo[0]`, el mismo cálculo que m03) y cuántas de esas caen dentro de algún period según `m03_visual._tramo`; por cap (1–7) y total;
   - c. fotos sin ningún period que las cruce → qué period les daría la regla del «más cercano» de F50d (para ver el daño);
   - d. n.º de grupos; por grupo: años que nombra su `where_when` y si cada uno cae en algún tramo de su `clothing_by_period`;
   - e. `years` que `_tramo` no puede leer (lista);
   - f. tokens, costo y segundos.
5. Tabla resumen por modelo (3 corridas): fotos cubiertas **mínimo · máximo** de las 3, grupos (lista de las 3), grupos con años sin ropa, `years` ilegibles, costo promedio por corrida.
6. Ejemplo pegado: `era_visual_canon.periods` y el grupo con más años de la corrida de **peor** cobertura de cada modelo.

## Criterio (lo aplica Omar con la tabla; CC no elige)
Primero: el **mínimo** de fotos cubiertas en las 3 corridas (lo que importa es que no dependa de la suerte). Desempate: grupos con años sin ropa (menos es mejor), después estabilidad del n.º de grupos, después costo.

## PARADA
Al final de la parte única, con `CANON_MODELOS.md` y el reporte. Sin elegir modelo, sin tocar producción, sin correr D.

## Reporte
`F50e_A_REPORT.md`: qué pasó en llano, la tabla, lo que queda abierto (entero) y el veredicto íntegro de `revisor-handoff`. ESTADO actualizado. Suite rápida y candado de ch02 como siempre (no debería cambiar nada: no se toca producción).
