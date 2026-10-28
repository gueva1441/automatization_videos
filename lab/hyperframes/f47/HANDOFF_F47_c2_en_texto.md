# HANDOFF F47 — ¿Sirve C2 para cualquier historia? Medido solo en texto, caps de otra época de Wittenoom + Claude llenando los casilleros (lab)

Analista, 2026-10-28 03:05. Pedido de Omar (02:49): antes de pasar C2 a producción, evaluar si su estructura cubre todo lo que debe tener un prompt de imagen y si sirve para cualquier historia. (02:55): «hacela solo en texto … si querés probate un modelo de Claude a ver si genera mucho mejor los prompts».
Tema Wittenoom `123bbb64-9fca-4395-8bf4-57d60e219ef1`. Rama `f11-guion-v4`. Base: `lab/hyperframes/f46/f46b/` (C2 = armado por código, sin oración de aspecto, sin cifras).

## Por qué (evaluación en papel del analista, a confirmar con esta tanda)
El canon es **uno por video** (`era_visual_canon` con `primary_decade` 1960s, `spans` 1937-2007, `forbidden_anachronisms` que prohíbe ropa post-2000, cámaras digitales y entornos limpios; `condition_evolution` con 2 estados) y los `people_groups` son 5, **ninguno Banjima** aunque «Banjima» sale 85 veces en el pool. El año ya se pone por foto; lugar, época visual, idioma del cartel y grupo, no. Ejemplo que lo junta todo: cap 7, foto 8 (suplementaria del cap Veo) «En dos mil veintitrés, Marcos Orellana … con Maitland Parker, un anciano Banjima».
Esta tanda **mide**; no arregla nada. Los arreglos (canon por tramos de época, lugar por código, idioma por foto, grupos desde el pool) van en otra tanda con la tabla de esta.

## Constantes
| Valor | Origen | Quién |
|---|---|---|
| Caps medidos con C2: **5, 6 y 7** | los de otra época (1966 → hoy) en ENTRADA 28c | analista |
| Variante D también en el **cap 2** | ahí C2 ya tiene fotos (F46b) → D se compara contra algo visto | analista |
| Modelo de D: **`claude-fable-5-1`**, effort **high** | Omar 02:55 pidió un Claude; Fable es `DEFAULT_MODELO_ESCALETA` / `DEFAULT_MODELO_GUION` y su effort `high` es el de `guion_v4.ESFUERZO` | analista (modelo) · existente (effort) |
| Llamadas de C2 (Pro): las de `f46b` (`SEEDREAM_SLOTS_USE_PRO`) | existente | — |
| Año de cada foto: la cadena 1→5 de F46b (`anios`) | existente (F46b) | analista |
| Fotos: **0** | Omar 02:55 «solo en texto» | Omar |
| Tope **US$ 6,00** | Pro 3 caps ≈ 0,36 (F46b: 0,1178 por cap) + Fable 4 caps ≈ 4 (pedido de ~17 k tokens de entrada = 0,17 + salida y razonamiento ~10–25 k = 0,5–1,25, con `PRICES` de `claude_helpers`) + margen | Omar confirma al pegar |

## Variantes (una variable cada una)
| Variante | Qué es | Contra qué |
|---|---|---|
| **C2** | `f46b` tal cual (expediente + Pro + armado por código + F8), caps 5, 6, 7 | la evaluación en papel |
| **D** | C2 con **un solo cambio**: los casilleros los llena `claude-fable-5-1` (`claude_helpers.call_json`) con el **mismo** system, el **mismo** user-prompt, el **mismo** esquema y la **misma** validación que Pro. Caps 2, 5, 6, 7 | C2 del mismo cap |

No hay textos nuevos para los LLM. Ningún cambio de prompt. Si Fable se niega (`stop_reason: refusal`) o rompe el JSON tras los reintentos de `claude_helpers`, se reporta tal cual; **no** se retoca el prompt.

## Caps Veo (cap 7)
El cap 7 no tiene `image_prompts`: se arma C2/D sobre sus `supplemental_image_prompts` (las fotos extra del clip). El `video_prompt` del clip queda **fuera** (se reporta cuántos hay y su texto entero, sin evaluar).

## Chequeos por código (por foto, en las dos variantes)
1. año y de dónde salió (regla 1–5);
2. ¿el año cae dentro de `era_visual_canon.spans`? (no → «año fuera del canon»);
3. ¿algún lugar del DÓNDE del expediente aparece en la prosa?;
4. gente sin grupo: la prosa matchea `m03_imagenes_v3.HUMAN` y `people_group` es `[]`;
5. nombres reales: nombres de `canon.documented_people` y `pool.personajes` que salen en el ancla (lista) y si alguno quedó en la prosa;
6. `text_in_image`: presente sí/no, texto, e idioma del lugar que usó `place_language`;
7. notas F8 (qué frase se sacó y por qué);
8. palabras.
Más, por cap: el `people_group` elegido por foto, y el estado de `condition_evolution` que la prosa describe (no se mide por código: se pega la frase del setting para que la lea el analista).

## Módulos
Producción: **ninguno se edita**. Se importan los mismos que en F46b y `claude_helpers.call_json`.
Nuevo en `lab/hyperframes/f47/`: `f47_corridas.py` — reusa `f46b_corridas` (`expedientes`, `bloque_expediente`, `slots`, `armar`, `f8`, `anios`) con el cap como parámetro (hoy `CAP` = 2 fijo y `cargar` solo lee `image_prompts`) y el canon `f46b/canon_C.json` sin regenerar.

## Paso 0
`DECISIONES.md`, dos líneas tal cual:
- «2026-10-28 02:49 · C2 no pasa a producción hasta evaluar si su estructura sirve para cualquier historia · Omar».
- «2026-10-28 02:55 · F47: C2 se mide solo en texto (sin fotos) en los caps 5, 6 y 7 de Wittenoom, más una variante D con Claude Fable 5.1 llenando los casilleros (caps 2, 5, 6, 7) · Omar · F47».

## Parte única — prompts en texto
1. Expedientes de los caps 5, 6, 7 (y 2 para D) → `expedientes_F47.md`.
2. C2 (Pro) caps 5–7 y D (Fable) caps 2, 5–7, **todas las llamadas en paralelo**; freno antes de cada una; costos con `cost_tracker` en `f47-lab`.
3. Armado por código + F8 igual que C2 de F46b.
4. Salida `PROMPTS_F47.md`: por cap y foto → ancla, año (fuente), DÓNDE, grupos C2 | D, prompt C2 entero, prompt D entero, palabras. Después la tabla de los 8 chequeos (filas = fotos, columnas = chequeo × variante) y una fila de totales por cap. Al final, el `video_prompt` del cap 7 entero.
5. Crudos de Pro y de Fable guardados (`slots_C2_chNN.json`, `slots_D_chNN.json`).
6. Costos reales de `cost_history` (`f47-lab`).

## Reglas fijas
- Nada en `data/` (salvo `cost_history`), `output/` ni `topics_db`. Ningún archivo de producción editado. Cero fotos, cero llamadas a fal.
- Paralelo al máximo (subagentes y workers).
- Prohibido `pytest --collect-only` y `pytest test_*.py` en bloque.
- Reporte `F47_REPORT.md` con «lo que queda abierto» y el veredicto íntegro de `revisor-handoff`; `lab/ESTADO_SESION.md`; commit.

## PARADA al terminar la parte única. No se elige variante ni se toca producción.
