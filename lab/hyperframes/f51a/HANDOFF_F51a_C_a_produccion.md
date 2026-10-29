# HANDOFF F51a — el armado C del prompt de foto pasa a producción (y se borra el viejo)

Analista → CC · 2026-10-29 · rama `f11-guion-v4` · **US$ 0** (sin fal, sin LLM) · 3 etapas y PARADA.

## Por qué
En F50h, C (el armado corto en prosa, en el orden de la guía de fal) le ganó a L (el `armar` de hoy) en 10 de 20 fotos contra 6, con 26 puntos de «la usarías» contra 23. Omar, 2026-10-29 03:23: «sí a las 3». Esta tanda hace solo la (a): C a producción. La (c), el canon con el aspecto separado del estado, va en F51b. Así cada cosa se mide por separado.

## Orden re-derivado
- ¿Construye sobre código que ya se decidió reemplazar? No. Reemplaza `armar` de `m03_imagenes_v3.py` y borra lo viejo.
- ¿Alguna decisión de hoy cambia el orden? Sí, la de las 03:23. Por eso F51a va primero: F51b (canon) y F51d (regenerar Wittenoom) usan el armado nuevo.

## Módulos que toca
| módulo | hoy | después |
|---|---|---|
| `script_engine/m03_imagenes_v3.py` | `armar` pega 10 partes: sujeto, aspecto, mirada, objeto, lugar+año, `style_head`+`STYLE_TAIL`, luz+paleta, técnica, cartel, cierre | `armar` arma C: sujeto, aspecto, lugar+año, cartel, luz (solo `lighting`), técnica, estilo C, cierre. Se borran `style_head`, `STYLE_TAIL` y las partes mirada, objeto y paleta. Se sacan de `_PROSA` `gaze_interaction`, `props_detail` y `color_palette` |
| `test_module_f8.py`, `test_module_f50b.py`, `test_module_f50g.py` | afirman el orden viejo, `style_head` y `STYLE_TAIL` | los asserts del orden viejo se reescriben al orden C; los que solo prueban `style_head`/`STYLE_TAIL` se borran |
| `DECISIONES.md` | — | 2 líneas (etapa 0) |

**No se toca:** `m03_visual.py`, que llama a `armar` y aplica el post-proceso igual que antes. Tampoco el esquema ni el prompt de casilleros: Opus sigue llenando `gaze_interaction`, `props_detail` y `color_palette`, porque los usan otros módulos (`depth_probe.py` l. 200, `m03_imagenes_v3.py` l. 385). Si dejan de pedirse, cambia lo que escribe Opus en los demás casilleros: es otra variable y queda en la lista.

## Constantes
| valor | origen | quién |
|---|---|---|
| Estilo C: `A grainy 35mm documentary photograph taken in {anio}, with muted colors and slight underexposure, in a dark-history realist style.` | `ESTILO_C`, `lab/hyperframes/f50h/f50h.py` l. 40 (handoff F50h, parte 7 de C) | Omar, 2026-10-29 02:03 (prueba) y 03:23 (producción) |
| Orden de C: sujeto · aspecto · lugar+año · cartel · luz · técnica · estilo · cierre | `armar_c`, `f50h.py` l. 59 | igual |
| 20 fotos del contrato | las de F50h (`PROMPTS_F50h.json`) | Omar, 02:03 |

No hay otros números.

## Etapa 0 — DECISIONES (sin código)
md5 de este handoff en el reporte. Al final de `DECISIONES.md`, tal cual:
```
- 2026-10-29 00:07 · **Court:** el borrado de nombres de `name_matching.scrub_documented_names` que rompe 6/3 y 7/11 se QUITA, no se le agregan reglas (se hace en F51c) · Omar · F50g-B
- 2026-10-29 03:23 · **F51:** a) el armado C de F50h va a producción y se borran del armado la mirada, el objeto, la paleta, style_head y STYLE_TAIL con sus tests; b) el estilo por época (C+ép) no, por ahora; c) el canon separa el aspecto fijo (piel, pelo, ojos, complexión) del estado (polvo, enfermedad) y el código pega solo el fijo · Omar · F51
```
Commit. Salida: las 2 líneas leídas del disco con `tail -2`.

## Etapa 1 — `armar` = C
1. En `armar`, las partes en este orden y con estas claves: `sujeto`, `aspecto`, `lugar_anio`, `texto`, `luz` (= `oracion(lighting)`, ya sin cláusulas negadas), `tecnica`, `estilo` (= el estilo C con `{anio}`), `cierre`. Las 5 claves que se repiten quedan con el mismo código de hoy. Se actualiza el docstring.
2. Se borran `style_head`, `STYLE_TAIL`, las partes `mirada` y `objeto`, y `color_palette` en `luz`. Antes de borrar, `grep` en todo el repo, `lab/` incluido. Si algo de producción los usa, PARADA y avisar. Lo de `lab/` se deja como está y se lista.
3. Tests: reescribirlos al orden C, borrar los de `style_head`/`STYLE_TAIL` y agregar uno que fije el orden C con un caso con cartel y un grupo.

**Contrato (sin esto no se commitea):** con el `armar` nuevo, y con el post-proceso de producción (`f8_backstop` + `_sacar_frases_con_texto`, igual que `m03_visual` l. 692–696) aplicado a los casilleros crudos (`raw_llm_prompt`) de las 20 fotos de F50h en `data/scripts/_steps/123bbb64-9fca-4395-8bf4-57d60e219ef1/03_visual.json`, el resultado tiene que ser **byte a byte igual** a `PROMPTS_F50h.json → fotos[i]["C"]` en las 20. Cualquier diferencia → PARADA, con el diff palabra por palabra.

Salida en el reporte:
- la tabla de las 20 (foto · igual sí/no);
- 2 prompts enteros, 1/2 y una con cartel, armados con el código de producción.

## Etapa 2 — en seco sobre todo Wittenoom (sin escribir)
Script de lab, `lab/hyperframes/f51a/rearmar_todo.py`: rearma con el `armar` nuevo **todas** las fotos de `03_visual.json` de Wittenoom, en memoria. **No escribe `03_visual.json`**: eso es F51d, con el canon nuevo. Salida en `lab/hyperframes/f51a/REARMADO_F51a.md`:
- cuántas fotos;
- palabras, mediana y máximo, antes y después;
- cuántas cambian;
- 3 prompts enteros, antes y después: 1/2, una con 2 grupos y una Veo, si hay una que pase por `armar`;
- cualquier foto donde el prompt nuevo quede vacío o sin `sujeto` → listar.

## Al cerrar
- Suite rápida, suite amplia (`lab/hyperframes/f41/verificar.sh`) y candado ch02 (`f792f3d4…`, no tiene que cambiar).
- Commit por etapa, con F51a en el mensaje.
- `ESTADO_SESION` y `lab/hyperframes/f51a/F51a_REPORT.md`, con lo abierto entero y el veredicto íntegro de `revisor-handoff`.
- **PARADA.**

## Reglas fijas
- Sin fal y sin LLM. No escribir `03_visual.json`, el canon ni topics_db.
- No tocar `name_matching` («Court»), el corte Veo, `anio_final`, el canon ni `cost_tracker`: son F51b–F51e.
- Subagentes en paralelo donde se pueda: los tests y el `grep` de etapa 1, y el rearmado de etapa 2.

## Lista (no se hace aquí)
- Dejar de pedirle a Opus `gaze_interaction`, `props_detail` y `color_palette` si nadie más los usa (otra variable).
- `track_gemini_vision` registra una tarifa fija: F51e.
