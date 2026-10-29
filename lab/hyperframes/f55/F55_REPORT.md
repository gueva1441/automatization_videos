# F55 — el detector deja de frenar guiones buenos; citas repetidas fuera del pool; promesa de una oración · REPORTE

Handoff: `lab/hyperframes/f55/HANDOFF_F55_detector_y_dedupe.md` (md5 `404a899dbc529c0796d4656747e4f92d`, verificado antes de tocar nada). Rama `f11-guion-v4`. Sin tope de dólares (DECISIONES 16:08): el gasto se mide y se informa. Correcciones de Omar al pegar el prompt: las 4 líneas de DECISIONES van solo en la raíz (`claude/DECISIONES.md` vive fuera del repo); el 0,7 + mismo autor y C.0 opción (ii) ya están confirmados en `527040a`.

## Para Omar, en corto (etapa 0)
- Guardé tal cual lo que Wittenoom tiene hoy (lo de F54 B.5) en `lab/hyperframes/f55/antes/`.
- Las 4 decisiones nuevas están en DECISIONES.md.
- Se fue el tope por tanda (el candado que paraba `fase1_5`/`fase2a` al llegar a los dólares): hook, su línea en `settings.json`, `lab/TOPE_TANDA.json`, su fila en el README y su sticker del mapa.
- Se fue la constante v5.5 del guionista con su test; el guionista sigue en v5.6 (`f54-2`).
- Gasto: US$ 0. **PARADA 0.**

# Etapa 0 — snapshots, borrados, DECISIONES · PARADA 0

## Commits
| commit | qué |
|---|---|
| `527040a` (antes de este arranque) | DECISIONES 19:30: dedupe 0,7 + mismo autor; C.0 opción (ii) |
| `0c4eaa4` | snapshots en `f55/antes/`, DECISIONES 16:08 / 19:07 / 19:16 / 19:15, fuera el tope por tanda, fuera `SYSTEM_V5_5`, stickers, MAPA |
| (este) | reporte, ESTADO |

## Qué se hizo, punto por punto
1. **Snapshots** → `lab/hyperframes/f55/antes/`: `00_pool_v3.json`, `00_pool_etiquetado.json`, `01_facts_sources.json` (el pool como lo lee `fase1_5`), `01a_escaleta.json`, `01a_skeleton.json`, `01b_guionista_v4.json`, `01b_narration.json`, `01b_narracion_v3.json`, `01e_pantalla.json/.md/.raw.json`, `01_v3_costos.json`. Son los de F54 B.5 (18:40–18:50).
2. **DECISIONES.md (raíz):** 4 líneas, texto literal del handoff (16:08, 19:07, 19:16, 19:15). No se creó `claude/DECISIONES.md` (corrección de Omar). Las de 0,7 y C.0 ya estaban desde `527040a` con la hora 19:30 que puso Omar.
3. **Tope por tanda, borrado:** `.claude/hooks/tope_tanda.py` (`git rm`); su entrada en el array `hooks` de `.claude/settings.json` (quedan 4 hooks PreToolUse; `json.load` válido; el resto del archivo byte-idéntico); `lab/TOPE_TANDA.json` (`git rm -f`: estaba modificado sin commitear, por diseño); README de hooks: la fila de `tope_tanda.py` y las dos frases de «Límites conocidos» que hablaban del tope («no pasa por `tope_tanda`» → «no pasa por los hooks»; «Por eso el tope es por tanda, no por llamada» fuera); el sticker del hook en `lab/mapa/stickers/orquestador.json` y la mención en el `estado_prueba` de `_comun.py`. **Tests:** `grep -n "tope_tanda\|TOPE_TANDA" test_module_f26*.py` → **vacío**: ningún test lo nombra, nada que borrar.
4. **`SYSTEM_V5_5` borrado** de `guion_v4.py` con `PROMPT_VERSION_V5_5`, su posición en `VERSIONES_V5` y la rama de `system()`; `test_guion_v5_5_literal_y_dos_cambios` borrado; `test_guion_v5_6_literal_y_solo_cambia_ejemplos` compara contra `lab/hyperframes/f54/PROMPT_GUIONISTA_v5_5.md`; `VERSIONES_V5[:3]` → `[:2]`; `test_module_f22` (tupla de versiones). `system()` sigue devolviendo `f54-2`.

## Salida 0 (texto)

### `git diff --stat` (= `git show --stat 0c4eaa4`, sin los 12 archivos de `antes/`)
```
 .claude/hooks/README.md            |  5 +-
 .claude/hooks/tope_tanda.py        | 76 ------
 .claude/settings.json              |  1 -
 DECISIONES.md                      |  4 +
 lab/MAPA_PROYECTO.json             | 45 ++-----
 lab/MAPA_PROYECTO.md               | 13 ++-
 lab/TOPE_TANDA.json                |  1 -
 lab/mapa/stickers/guion.json       |  2 +-
 lab/mapa/stickers/orquestador.json | 20 +-
 script_engine/guion_v4.py          | 97 +------
 test_module_f22.py                 |  2 +-
 test_module_f54.py                 | 19 +--
 + lab/hyperframes/f55/antes/ (12 archivos)
```

### `grep -rn "tope_tanda\|TOPE_TANDA"` (fuera de `lab/hyperframes/f5[45]/`, ESTADO y DECISIONES) — listado, no tocado
- Producción y hooks: **0** restantes (README, settings, sticker y hook ya sin él).
- `lab/mapa/hechos.json` (digest del auditor de estructura, se regenera con el auditor, no con `mapa_modulos.py`): 1 entrada del hook borrado.
- `lab/ENTRADA_ANALISTA_2026-10-25.md`, `lab/mapa/notas_auditoria_orquestador.md`, `lab/mapa/stickers/_partes/*` (notas históricas): menciones.
- Scripts de tandas cerradas en `lab/` que leen `TOPE_TANDA.json` (no se tocan; si se corren, no encuentran el archivo): `f26/d/prueba_hooks.py`, `f47/f47_corridas.py`, `f47/f47b_corridas.py`, `f48/f48_corridas.py`, `f50e/canon_modelos.py`, `f52/prueba_video.py`, `f53a/moderacion.py`, `f53a/K/moderacion_k.py`; más los reportes y handoffs de F26–F54 que lo nombran como historia.

### `grep -rn "SYSTEM_V5_5\|PROMPT_VERSION_V5_5\|f54-1" .` — listado
- `script_engine/`: solo `m01a_escaleta.PROMPT_VERSION_V2 = "f54-1"` y `PROMPT_VERSION_COLUMNA = "f54-1"` (la **escaleta** sigue en f54-1 hasta la Parte C → `f55-1`); `guion_v4.py` sin ninguna.
- Tests: `test_module_f17.py:180` y `test_module_f54.py:54-55` (`f54-1` de la escaleta: correcto); `test_module_f54.py:69,72` (el v5.5 ahora desde el `.md`; `not hasattr(g4, "SYSTEM_V5_5")`).
- Lab: `lab/hyperframes/f54/salida_a.py:74` usa `g4.SYSTEM_V5_5` → **ese script de la tanda cerrada F54 queda roto** (lista, no se toca); `f54/EJEMPLOS_v5_6_propuesta.md`, `f54/MEDIDA_RETENCION.md`, `f54/F54_REPORT.md`: historia.

### Suite rápida
`pytest -q -x test_module_f25c.py test_module_f24.py test_module_f21.py`: **55 passed**, 3 skipped. Además `test_module_f54.py` + `test_module_f22.py`: 86 passed, 8 skipped. `mapa_modulos.py --check`: 157 archivos, 0 fallas (158 → 157: el hook).

## Decisiones de CC (etapa 0)
1. `settings.json`: quité la línea del hook por texto (no reescribí el JSON con `json.dumps`, que cambiaba el formato de todo el archivo); validado con `json.load`.
2. README de hooks: además de la fila, dos frases de «Límites conocidos» que solo existían por el tope; «lo viejo se borra».
3. El `.md` del v5.5 (`lab/hyperframes/f54/PROMPT_GUIONISTA_v5_5.md`) se queda: es el registro de la tanda y el test del v5.6 lo usa como «antes».
4. `lab/mapa/hechos.json` no se regenera acá (es del `structure-auditor`, no de `mapa_modulos.py`); queda listado.

## Lo que queda abierto (etapa 0)
- `lab/hyperframes/f54/salida_a.py` roto por el borrado de `SYSTEM_V5_5` (script de lab de tanda cerrada).
- Los 8 scripts de lab que leían `TOPE_TANDA.json` (tandas cerradas).
- `lab/mapa/hechos.json` con la entrada del hook borrado hasta la próxima corrida del auditor.

**PARADA 0.**

## Veredicto de revisor-handoff (etapa 0, íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

Handoff md5 404a899dbc529c0796d4656747e4f92d: coincide. Corrí `python -m pytest -q test_module_f54.py test_module_f22.py test_module_f25c.py`: 91 passed, 8 skipped. `lab/tools/mapa_modulos.py --check`: 157 archivos, 0 fallas. No corrí la suite rápida de 3 archivos (f25c, f24, f21) que cita el reporte, así que su «55 passed» queda NO VERIFICADO. No llamé a ningún modelo.

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Snapshots completos e idénticos a `_steps` | OK | Los 12 archivos de `lab/hyperframes/f55/antes/` dan md5 IGUAL a `data/scripts/_steps/123bbb64-.../`. Incluyen pool, `01_facts_sources`, escaleta, skeleton, `01b_guionista_v4`, `01b_narration`, `01b_narracion_v3`, `01e_*` y costos. |
| 2 | 4 líneas de DECISIONES literales (16:08, 19:07, 19:16, 19:15), solo en la raíz | OK | `git show 0c4eaa4 -- DECISIONES.md` suma exactamente 4 líneas con el texto del handoff, en ese orden. `claude/` no existe ni hay nada en `git ls-files`. Las líneas 19:30 de `527040a` (0,7 y C.0 ii) están intactas. |
| 3a | Borrado de `tope_tanda.py` y `lab/TOPE_TANDA.json` | OK | Los dos archivos ya no existen; el commit los marca borrados. |
| 3b | `settings.json` válido y resto intacto | OK | El diff borra una sola línea (la del hook). `json.load` da 4 hooks PreToolUse y 1 PostToolUse. |
| 3c | Fila del README | OK | Fila borrada. Además se editaron dos frases de «Límites conocidos» y el texto pasa de «seis» a «cinco candados». El handoff pedía solo la fila; CC lo declara como su decisión 2. |
| 3d | Tests de `test_module_f26*.py` que nombren el tope | OK | `grep -n "tope_tanda\|TOPE_TANDA" test_module_f26*.py` da vacío. Confirmado. |
| 3e | `grep -rn TOPE_TANDA lab/` listado sin tocar | OK | Quedan menciones en scripts de tandas cerradas (`f26/d/prueba_hooks.py`, `f47/*_corridas.py`, etc.). El reporte los lista y ninguno aparece en el diff. |
| 4a | Borrado de `SYSTEM_V5_5`, `PROMPT_VERSION_V5_5`, `VERSIONES_V5` y la rama de `system()` | OK | El diff de `script_engine/guion_v4.py` quita la constante, su versión, su posición en la tupla y la rama (`if version == PROMPT_VERSION_V5_5`). Solo se borra el v5.5 y se cambia un docstring. |
| 4b | Tests del v5.5 y v5.6 | OK | `test_guion_v5_5_literal_y_dos_cambios` borrado. El del v5.6 lee `f54/PROMPT_GUIONISTA_v5_5.md` (`test_module_f54.py:69`). `VERSIONES_V5[:2]` en `test_module_f54.py:72` y la tupla en `test_module_f22.py:112`. |
| 4c | `system()` sigue en `f54-2` | OK | `PROMPT_VERSION` no se tocó; el test pasa. |
| 4d | `grep` de `SYSTEM_V5_5` / `f54-1` listado | OK | Los `f54-1` restantes en `script_engine/` y tests son los de la escaleta (`m01a_escaleta.py:860,1615`), no del guionista. El reporte lo explica. |
| 5 | Salida 0 del reporte y «lo que queda abierto» | PARCIAL | `lab/hyperframes/f55/F55_REPORT.md` tiene los greps listados y los 3 abiertos, incluido `f54/salida_a.py:74` roto. Pero el `--stat` pegado dice `MAPA_PROYECTO.md | 11` y el commit da 13: se armó a mano. El veredicto del revisor está pendiente («se pega abajo»), lo esperado ahora. |
| 6 | Nada fuera de alcance | OK | Los archivos del commit `0c4eaa4` son: los 12 de `antes/`, DECISIONES, el tope, los stickers, el MAPA, `guion_v4.py` y 2 tests. No se tocó ningún archivo de la Parte A/B/C (`evidence`, `dicho_verificador`, `research_v3`, `m01a_escaleta`). Sin commitear solo hay `F55_REPORT.md` y `ESTADO_SESION.md`, además de `diag_234_cap4.py` y `f28a.log`, que ya estaban modificados antes de la tanda. |

Fuera de alcance: ninguno. Los cambios en `lab/MAPA_PROYECTO.*`, `lab/mapa/stickers/{guion,orquestador}.json` y `test_module_f22.py` son consecuencia directa de los borrados (`guard_mapa` los exige).

Observaciones:
- `lab/mapa/hechos.json:33477` conserva la entrada del hook borrado. El reporte lo declara abierto.
- Los números del `--stat` del reporte difieren del real (MAPA_PROYECTO.md 11 contra 13).
- `f54/salida_a.py` queda roto. Es lo previsto por «lo viejo se borra» y está declarado.

Riesgos que el contrato no cubre:
- El hook `suite_rapida` corre f25c, f24 y f21, que no cubren los tests tocados (f54 y f22). Un rojo en esos dos no frena commits.
- Los 8 scripts de lab que leen `TOPE_TANDA.json` ya no encuentran el archivo. Si se vuelven a correr, fallan o ignoran el tope sin avisar.

## Adenda de CC (etapa 0)
- **Fila 5:** el `--stat` del reporte tenía el número de una corrida anterior (`MAPA_PROYECTO.md | 11`, antes del sticker del README); corregido a 13, el del commit. La suite rápida de 3 archivos la corrí yo dos veces (55 passed): el hook `suite_rapida` la vuelve a correr en cada commit.
- **Fila 3c:** las dos frases y el «seis → cinco» del README describían al hook borrado; «lo viejo se borra».
