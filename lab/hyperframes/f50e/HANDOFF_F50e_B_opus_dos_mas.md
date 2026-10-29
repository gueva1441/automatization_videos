# HANDOFF F50e-B — Las 2 corridas de Opus que faltan en el canon (lab, en texto)

Analista · 2026-10-28 23:20 · rama `f11-guion-v4` · Wittenoom `123bbb64-9fca-4395-8bf4-57d60e219ef1`.

## Por qué
F50e-A: Flash queda fuera (4 de 6 corridas sin cubrir las fotos de 1971–2024). Sonnet cubre 96/96 en 3 de 3 pero deja sin `appearance` 4/7, 7/10 y 5/8 grupos. Opus cubrió 96/96 con 2/13 grupos sin `appearance`, pero en **una sola corrida**: las otras 2 las frenó el tope (estimación de costo del analista, baja). Esta tanda completa las 3 de Opus para ver su varianza. Nada más cambia.

## Constantes
| valor | origen | quién |
|---|---|---|
| 2 corridas de `claude-opus-5-5` (opus_2, opus_3) | F50e-A, Omar 23:19 | Omar |
| effort `high` | `guion_v4.ESFUERZO["claude-opus-5-5"]` (existente) | existente |
| camino **sin esquema** (el mismo de opus_1: la API rechaza 46 opcionales > 24) | F50e-A, medido | existente |
| tope US$ 1,00 (opus_1 costó 0,3464 → 2 × ≈ 0,70) | Omar 23:19 | Omar |
| 2 en paralelo | preferencia de Omar | Omar |

## Módulos
Producción: ninguno. Lab: `lab/hyperframes/f50e/canon_modelos.py` (correr solo opus 2 y 3; las corridas de F50e-A no se repiten ni se pisan) y `canon_modelos_md.py` (tabla con la medida nueva).

## Paso 0
1. md5 de este handoff contra el del prompt.
2. `DECISIONES.md`, tal cual: `- 2026-10-28 23:19 · **F50e-B:** Flash queda fuera del canon (4 de 6 corridas sin cubrir 1971–2024); se completan las 3 corridas de Opus 5.5 (mismo pedido, sin esquema, effort high), tope US$ 1; después Omar elige entre Opus y Sonnet con la tabla · Omar · F50e-B`
3. `lab/TOPE_TANDA.json` = `{"usd": 1.0, "desde": <ahora>}`.

## Parte única
1. Llamá directo al camino sin esquema (no gastes el intento que da 400). Comprobá que el md5 del pedido es `d2568e2a94c5db96f9836451b2f80cd7`, el de F50e-A.
2. Misma medida 4a–4f de F50e-A, más **4g: grupos con `appearance` vacío** (lista de ids) para **las 9 corridas** (las 7 de F50e-A se miden de sus `canon_*.json`, sin llamar).
3. `CANON_MODELOS.md` regenerado con las 9 + opus_2 y opus_3: resumen por modelo con fotos cubiertas mín · máx, grupos por corrida, grupos con años sin ropa, **grupos sin appearance por corrida**, costo promedio.
4. Ejemplo pegado: `periods` y el grupo con más años de la peor corrida de Opus.

## PARADA
Con la tabla. Sin elegir modelo, sin tocar producción, sin correr D de F50d.

## Reporte
`F50e_B_REPORT.md`: qué pasó en llano, la tabla, lo que queda abierto (entero), veredicto íntegro de `revisor-handoff`. ESTADO, suite rápida, candado de ch02, commit.
