# HANDOFF F49 — Fotos: la entrada nueva con Opus (S5 de F48) contra lo de hoy (C2 con Pro), caps 2 y 7 de Wittenoom (lab)

Analista, 2026-10-28 10:40. Pedido de Omar (10:34): «si dale» a fotos de la candidata contra lo de hoy, con el **estilo fijo de hoy** (opción a: `style_head(año)` + `STYLE_TAIL`, igual para todas las épocas; el estilo por época se prueba aparte).
Tema Wittenoom `123bbb64-9fca-4395-8bf4-57d60e219ef1`. Rama `f11-guion-v4`.
**Qué se compara:** candidata = S5 de F48 (Opus 5.5 + entrada nueva + armado por código) contra la de hoy = C2 (Pro + entrada vieja + armado por código). Son dos cambios juntos a propósito: es la prueba de pase o no pase de la candidata; cada cambio ya se midió por separado en texto (F47b modelo, F48 entrada).

## Constantes
| Valor | Origen | Quién |
|---|---|---|
| Prompts: **los ya escritos**, sin llamar a ningún LLM: S5 de `lab/hyperframes/f48/PROMPTS_F48.json` (caps 2 y 7) y C2 de `lab/hyperframes/f47/PROMPTS_F47.json` (cap 7) | existentes | — |
| Cap 2 de C2: **las fotos ya generadas** en `lab/hyperframes/f46/f46b/C2/` (`_a`), no se regeneran | existentes (F46b) | — |
| **1 foto por prompt** (`num_images` 1) | F46b: las 2 fotos de cada prompt salieron casi iguales (medido por el analista en las hojas) | analista |
| Fotos nuevas: 16 (S5 cap 2) + 12 (S5 cap 7) + 12 (C2 cap 7) = **40** | — | derivado |
| Motor, payload, grade y workers de producción (`seedream/v5/lite`, 2560×1440, `FLUX_MAX_WORKERS`) | existentes | — |
| Tope **US$ 2,50** | 40 × 0,035 = 1,40 (precio de F46b: 3,36 / 96) + margen | Omar confirma al pegar |

## Chascada (producción, F8)
`script_engine/m03_imagenes_v3.fix_counts_lr`: «The two men» → hoy «The a couple of men» (cap 7 foto 7 de S5, abierto l6 de F48). Arreglo general: si la cifra va precedida de un artículo («the/a/an»), el artículo se va junto con la cifra. Test nuevo con «The two men sit», «two men sit», «The three inmates». **Los prompts de esta tanda se re-pasan por `fix_counts_lr` arreglada antes de generar** (se reporta qué prompts cambiaron y cómo).

## Módulos
- `script_engine/m03_imagenes_v3.py` (producción): `fix_counts_lr` reemplaza «número → cantidad vaga» y hoy deja el artículo colgado → después se lleva el artículo. Nada más.
- Nuevo `lab/hyperframes/f49/f49_corridas.py` (lee los prompts, freno, genera en paralelo, grade, hojas) y `f49_hoja.py` (o reusa `f46b_hoja.py`).

## Paso 0
`DECISIONES.md`, dos líneas tal cual:
- «2026-10-28 10:34 · Estilo de las fotos en la prueba: fijo de hoy (`style_head` + `STYLE_TAIL`) para todas las épocas; el estilo por época se prueba aparte · Omar».
- «2026-10-28 10:34 · F49: fotos de la candidata (S5 de F48: Opus 5.5 + entrada nueva) contra C2 (Pro), caps 2 y 7 de Wittenoom, 1 foto por prompt · Omar · F49».

## Parte 1 — chascada
`fix_counts_lr` + test; suite rápida verde; commit.

## Parte 2 — fotos
1. Prompts: S5 caps 2 y 7, C2 cap 7, re-pasados por `fix_counts_lr`. Tabla de los que cambiaron (antes → después).
2. 40 fotos **en paralelo**; freno antes de cada llamada; `cost_tracker` con `f49-lab`; grade de producción; a `f49/S5/` y `f49/C2/` (`chNN_img_MM.png` + `_graded`). Rechazos del filtro: se reportan, no se reintenta con otro texto.
3. Hojas (≤ 3840 px de ancho, una cada 4 fotos): cap 2 → columnas **C2 (F46b `_a`) | S5**; cap 7 → **C2 | S5**. Rótulo: n.º, año de cada variante y las primeras 8 palabras del ancla.
4. Costos de `cost_history` (`f49-lab`) y rechazos.

## Reglas fijas
- Ninguna llamada a LLM. Nada en `data/` (salvo `cost_history`), `output/` ni `topics_db`. Las PNG no van a git.
- Paralelo al máximo (subagentes y workers).
- Prohibido `pytest --collect-only` y `pytest test_*.py` en bloque.
- `F49_REPORT.md` con «lo que queda abierto» y el veredicto íntegro de `revisor-handoff`; `lab/ESTADO_SESION.md`; commit.

## PARADA al terminar la parte 2. No se elige ni se pasa nada a producción (salvo la chascada).
