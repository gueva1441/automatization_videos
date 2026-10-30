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


---

# Parte A — detector · PARADA A

**Gasto Parte A: US$ 0,012** (Salida A: 3 llamadas a Sonnet, US$ 0,0091 por `cost_of`; test real `F55_REAL=1`: 1 llamada ≈ US$ 0,003). Acumulado F55: ≈ US$ 0,012.

## Para Omar, en corto
- El detector de «lo que la voz dice» ahora reconoce un dato sin cifra ni fecha si la oración trae su año y una palabra del hecho (A1) o la mitad de sus palabras (A2). Sobre Wittenoom marca exactamente los 13 (A1) y los 6 (A2) de la simulación del analista.
- Para el dato del cierre y de los pagos, cuando no hay cifra que buscar, la segunda opinión la da Sonnet: le muestra el hecho y las oraciones del cap y acepta el «sí» solo si copia un fragmento real.
- Resultado sobre los dos guiones de Wittenoom: **0 bloqueantes (f)/(h)** (antes: 1 en el viejo, 3 en el nuevo, todos falsos). Sonnet confirmó D42 en el cap 7 viejo, D21 en el cap 3 y D10 en el cap 6 nuevos. Costó US$ 0,009.

## Commits
| commit | qué |
|---|---|
| `090b1eb` | `evidence.regla_dicho`/`oracion_dicha`, `dicho_verificador.py`, `guion_v4` (f)/(h) con verificador, `test_module_f55.py`, stickers, MAPA |
| (este) | `salida_a.py` → `SALIDA_A.md` + `salida_a.json`, reporte, ESTADO, logs |

## Módulos: antes → después
| módulo | antes | después |
|---|---|---|
| `script_engine/evidence.py` | `used_in` solo con anclas (un `datos` sin cifra ni fecha con guion → nunca dicho) | `regla_dicho(text, it) -> "ancla" \| "A1" \| "A2" \| None`; con ancla, el código de siempre (`_oracion_ancla`, mismo criterio, byte a byte en la lógica); sin ancla y `_kind == "datos"`: A1 si `fecha` es un año de 4 dígitos (el año en cifras con límite de palabra o en letras vía `num_es.variants`, normalizado con `norm`, + ≥ 1 palabra de `_content(texto)` **descontando** las palabras del año en letras, en la misma oración); si no o si A1 falla → A2 (`|C∩S|/|C| ≥ UMBRAL_A2 = 0.5` y `|C∩S| ≥ A2_MIN_COINCIDENCIAS = 2`, constantes propias, no las de `same_fact`); citas, lugares, personajes y cronología siguen como hoy. `oracion_dicha(text, it) -> int \| None` (índice en `_sentences`). `used_in = regla_dicho(...) is not None` |
| `script_engine/dicho_verificador.py` (nuevo) | — | `pedido(hecho, oraciones)` puro (hecho, oraciones numeradas desde 1, la pregunta literal del handoff, formato JSON); `verificar(hecho, oraciones, *, log, id, cap_md5_, post)` → Sonnet 5.5 `medium` (`claude_helpers._post`, `cost_of`, `_track(..., "dicho_verificador")`), salida `{"oracion": n\|null, "fragmento": str\|null}` con esquema; `None` si `n` fuera de rango o el fragmento normalizado no es subcadena de la oración `n`; error/timeout/JSON roto → `None` + log, 1 reintento; caché en memoria por `(id, md5 del cap)`; `estado()` = llamadas, caché, usd; `reset()` |
| `script_engine/guion_v4.py` | (f)/(h) devolvían bloqueantes puros mirando solo `ids_usados` | `cierre_no_dicho(esc, parrafos, pool, verificar)` y `pago_no_dicho(...)` → `(bloqueantes, altas)`; `_dicho_o_verificado`: con ancla decide el código (en `ids_usados` o no); **sin ancla pregunta a `verificar` aunque A1/A2 digan sí** (§1 del handoff); `bloqueantes(..., verificar=None)` usa `dicho_verificador.verificar` por defecto, suma cada alta a `ids_usados` del párrafo indicado (opción a, en el lugar; m03/gfx los ven) y la deja en `ULTIMAS_ALTAS`; `metricas` agrega `confirmados_sonnet` (las altas) y `verificador` (llamadas, caché, usd) |

Tests: `test_module_f55.py` (17): constantes; A1/A2 sobre el guion nuevo = la simulación §3 (68 sin ancla; A1 = los 13; A2 = D42, D71, D85, D150, y D19/D92 por A1 antes que A2; D21 A1 cap 3; D10 None; D42 A2 cap 6; D85 A2 cap 1; D92 cap 1 True); `oracion_dicha`; A1 no cuenta el año en letras como palabra; A2 exige 2 y la mitad; con ancla nada cambia (A2 no aplica); `pedido` literal; lectura de la respuesta (rango, fragmento); `verificar` con `post` simulado (caché, costo, error → 1 reintento); (f)/(h) con `verificar` sí / no / None y las altas en `ids_usados` y en `metricas`; sin ancla Sonnet decide aunque A2 diga sí; con ancla no se llama; `ids_usados` de los 7 caps viejos y nuevos: antes ⊆ después con la diferencia escrita; **Sonnet real** sobre D10 del cap 6 nuevo con `skipif` por `F55_REAL=1` (corrido una vez: pasa, oración con «Colonial», 1 llamada).

## Decisiones de CC (Parte A)
1. **`_oracion_ancla`** reproduce el `used_in` viejo y además dice la oración: para eventos con fecha, la que trae ancla y palabra del hecho; para el resto, la primera con el ancla. El criterio de «dicho» con ancla no cambió (test `con_ancla_nada_cambia`; los `ids_usados` «antes» de las 2×7 tablas son subconjunto de «después»).
2. **A1 antes que A2** cuando hay año: por eso D19 y D92 salen «A1» aunque también cumplan A2 (la simulación del analista los contaba en los dos).
3. **Esquema del verificador en JSON Schema minúsculas**: `claude_helpers.json_schema` solo baja los `type` que son `str`; con `["INTEGER","NULL"]` la API devolvía 400 (primera corrida de la Salida A, 6 llamadas fallidas sin costo). Corregido antes de la corrida que cuenta.
4. **`verificar` por defecto = Sonnet real** en `bloqueantes`, como pide el handoff; los tests inyectan uno simulado. Riesgo: un test futuro con un `dato_central` sin ancla y sin `verificar` llamaría a la API (los fixtures de hoy tienen ancla).
5. **Las altas se aplican en el lugar** sobre `parrafos`; `with_ids` recalcula `ids_usados` desde el texto en cada paso de `reparar`, así que una alta puede «perderse» entre pasos y volver en el siguiente `bloqueantes` (caché: sin llamada). El último `bloqueantes` de `reparar` la deja en los párrafos finales.
6. **`git stash` una vez**, para separar el commit del reporte de la etapa 0 del `evidence.py` ya editado (push/pop de un archivo, inmediato). La convención pide no usarlo; lo digo.

## Salida A (texto; entera en `lab/hyperframes/f55/SALIDA_A.md`, crudo en `salida_a.json`)

## viejo

##### 1. D21, D10, D42, D85: regla · cap · oración

| id | hecho | regla por código | cap | oración | Sonnet (f/h) |
|---|---|---|---|---|---|
| D21 | La producción minera en Wittenoom se incrementó en 1961 a pesar de la  | A1 | 3 | En mil novecientos sesenta y uno la producción subió. | — |
| D10 | El material de asbesto del vertedero de Colonial alimenta el área de c | ninguna | — | — | — |
| D42 | Se han instalado barricadas permanentes en las entradas del antiguo pu | A2 | 7 | En los accesos al antiguo pueblo y al desfiladero hay bloqueos permanentes. | sí: cap 7, oración 12 (cierre) |
| D85 | Daniel Écija padre se hirió el pie con un trozo de amianto y la herida | ninguna | — | — | — |

##### 2. Bloqueantes (f)/(h) con el detector nuevo + Sonnet: 0


Altas de Sonnet (entran a `ids_usados`):

- D42 → cap 7, párrafo 23, oración 12 (cierre)

##### 3. `ids_usados` antes (solo anclas) → después (regla_dicho + Sonnet), por párrafo

| cap | párrafo (beat) | antes | + después |
|---|---|---|---|
| 1 | 0 (1) | — | — |
| 2 | 1 (2) | D82, D83, Q12 | — |
| 2 | 2 (3) | Q14 | — |
| 2 | 3 (3) | T36 | — |
| 3 | 4 (4) | T06, T13 | D19 |
| 3 | 5 (4) | — | — |
| 3 | 6 (4) | — | — |
| 3 | 7 (5) | — | — |
| 3 | 8 (5) | Q49 | — |
| 3 | 9 (5) | — | D21 |
| 4 | 10 (6) | T40 | — |
| 4 | 11 (7) | D87, D104, D129, T39, T41 | — |
| 5 | 12 (8) | D02, T51 | — |
| 5 | 13 (9) | T67, Q24 | D27 |
| 5 | 14 (10) | D89, Q25 | — |
| 5 | 15 (10) | — | — |
| 6 | 16 (11) | D23, Q21 | D36, D93 |
| 6 | 17 (11) | — | — |
| 6 | 18 (12) | — | D54 |
| 6 | 19 (12) | — | — |
| 6 | 20 (12) | — | D59, D61 |
| 7 | 21 (13) | T90 | — |
| 7 | 22 (13) | T92, T96 | — |
| 7 | 23 (14) | — | D42, D71 |

Log del verificador:

    [verificador] D42: oración 12

#### nuevo

##### 1. D21, D10, D42, D85: regla · cap · oración

| id | hecho | regla por código | cap | oración | Sonnet (f/h) |
|---|---|---|---|---|---|
| D21 | La producción minera en Wittenoom se incrementó en 1961 a pesar de la  | A1 | 3 | En mil novecientos sesenta y uno, la producción aumentó. | sí: cap 3, oración 15 (la pregunta del beat 3); sí: cap 3, oración 15 (el loop L2) |
| D10 | El material de asbesto del vertedero de Colonial alimenta el área de c | ninguna | — | — | sí: cap 6, oración 11 (la pregunta del beat 10) |
| D42 | Se han instalado barricadas permanentes en las entradas del antiguo pu | A2 | 6 | En las entradas al pueblo y al desfiladero pusieron barricadas permanentes, porque el área no es segura. | — |
| D85 | Daniel Écija padre se hirió el pie con un trozo de amianto y la herida | A2 | 1 | Cuenta que a su marido le cayó un trozo de amianto en el pie y que la herida no cerraba; por eso la venda. | — |

##### 2. Bloqueantes (f)/(h) con el detector nuevo + Sonnet: 0


Altas de Sonnet (entran a `ids_usados`):

- D21 → cap 3, párrafo 6, oración 15 (la pregunta del beat 3)
- D10 → cap 6, párrafo 14, oración 11 (la pregunta del beat 10)
- D21 → cap 3, párrafo 6, oración 15 (el loop L2)

##### 3. `ids_usados` antes (solo anclas) → después (regla_dicho + Sonnet), por párrafo

| cap | párrafo (beat) | antes | + después |
|---|---|---|---|
| 1 | 0 (1) | Q25 | D85 |
| 2 | 1 (2) | D82, D83, T24, T34, T37, Q12 | — |
| 2 | 2 (3) | — | — |
| 2 | 3 (3) | — | — |
| 3 | 4 (4) | T06, T13 | D19 |
| 3 | 5 (4) | — | D92 |
| 3 | 6 (5) | T27, T29, T35 | D21 |
| 4 | 7 (6) | Q44 | — |
| 4 | 8 (6) | — | — |
| 4 | 9 (7) | D87, D104, T41 | — |
| 5 | 10 (8) | D121, T21, T47, T48, T64 | D27 |
| 5 | 11 (9) | D89 | — |
| 5 | 12 (9) | Q23 | — |
| 6 | 13 (10) | D06, T67 | D42 |
| 6 | 14 (11) | T90 | D59, D150, D10 |
| 7 | 15 (12) | D95, T92, T96 | D61 |
| 7 | 16 (13) | Q21 | — |
| 7 | 17 (13) | — | — |
| 7 | 18 (13) | T57, Q24 | — |

Log del verificador:

    [verificador] D21: oración 15
    [verificador] D10: oración 11

#### Verificador (las dos corridas)

llamadas 3 · caché 1 · US$ 0.0091


### Resumen de la Salida A
| | viejo | nuevo |
|---|---|---|
| D21 | A1, cap 3 («En mil novecientos sesenta y uno la producción subió.») | A1, cap 3 + Sonnet sí (oración 15) para (h) ×2 |
| D10 | ninguna | ninguna por código → **Sonnet sí** (cap 6, oración 11) |
| D42 | A2, cap 7 («En los accesos al antiguo pueblo y al desfiladero hay bloqueos permanentes.») + Sonnet sí (oración 12) para (f) | A2, cap 6 |
| D85 | ninguna | A2, cap 1 |
| bloqueantes (f)/(h) | 1 → **0** | 3 → **0** |
| `ids_usados` que cambian | 7 párrafos (+D19, D21, D27, D36, D93, D54, D59, D61, D42, D71) | 8 párrafos (+D85, D19, D92, D21, D27, D42, D59, D150, D10, D61) |
| verificador | 1 llamada | 2 llamadas + 1 caché (D21 ×2) · total US$ 0,0091 |

Nota: en el viejo, D42 no llega a A2 en el cap 7 por código (`regla_dicho` lo da A2 porque la oración «hay bloqueos permanentes» comparte «perman», «entrad», «pueblo», «desfil» = 4 de 7 ≥ 0,5: sí llega; la simulación del analista lo decía); en cualquier caso, al ser `dato_central` del cierre, lo decide Sonnet, que confirmó.

## Suite
`bash lab/hyperframes/f41/verificar.sh f55a` (logs en `lab/hyperframes/f41/f55a/`): ch02 md5 `f792f3d483a1fa42daed5f7f0e054f46`; rápida **55 passed**; amplia **1107 passed** + 8 fallas: las 4 previas (`m03_merge_timing` ×2, `gfx_lab` ×2), `gfx_lab::test_candado_en_el_preview` (intermitente conocido desde F51c) y **3 nuevas que no son de F55**: `test_module_f51c.py::test_f51c_corte_veo_real_de_wittenoom` ×2 y `test_module_f48.py::test_geo_era_de_wittenoom` leen `data/scripts/_steps/<Wittenoom>/01b_narration.json`, que **F54 B.5 regeneró** (18:46): esperan «paredes de chapa.», «seguridad pública».» y «1943–2024» del guion viejo. Es la primera suite amplia desde esa regeneración (la de F54 B arrancó antes de que B.5 escribiera). Van a «lo abierto»: tests de tandas cerradas clavados a un dato de producción que cambia.

## Lo que queda abierto (Parte A)
1. Los 3 tests de F51c/F48 clavados a la narración vieja de Wittenoom (y volverán a romperse en la Parte D): decidir si se apuntan a `lab/hyperframes/f54/antes/` o se borran.
2. `verificar` real por defecto en `bloqueantes` (decisión 4): un fixture sin ancla y sin `verificar` gasta.
3. Alcance declarado del handoff: «el 48», «el cuarenta y ocho», décadas; citas parafraseadas no cuentan (por decisión).
4. `with_ids` recalcula y descarta las altas entre pasos de `reparar` (decisión 5): funciona por la caché, pero no es prolijo.

**PARADA A.**

## Veredicto de revisor-handoff (Parte A, íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

Handoff md5 404a899d... verificado. Corrí `pytest -q test_module_f55.py test_module_f54.py test_module_f11.py`: 67 passed, 2 skipped (el test real de Sonnet y otro skip). No llamé a ningún modelo ni puse F55_REAL.

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | regla_dicho: ancla → A1 → A2 → None; alcance solo `datos`; con ancla, código viejo; oracion_dicha devuelve índice en `_sentences`; used_in envoltorio | OK | script_engine/evidence.py: `_oracion_ancla` es idéntica a `used_in` de 3a45c75 (rama dated y no dated). `regla_dicho` devuelve None si `_kind != "datos"`. A1 solo con `\d{4}` (`_anio_sin_guion`), con límite de palabra, formas de `num_es.variants` normalizadas con `norm`, y descuenta las palabras del año en letras. A2 usa `UMBRAL_A2=0.5` y `A2_MIN_COINCIDENCIAS=2`, constantes propias. `used_in = regla_dicho(...) is not None`. |
| 2 | dicho_verificador | OK | dicho_verificador.py: MODELO `claude-sonnet-5-5` y EFFORT `medium`, iguales a m01e_pantalla l.67-68. Usa `hx._post`, `hx.cost_of` y `hx._track(..., "dicho_verificador")`. `PREGUNTA` es literal. Oraciones numeradas desde 1. `_leer` da None si el número está fuera de rango o el fragmento normalizado no es subcadena. 1 reintento con log. Caché por (id, md5 del cap). `estado()` devuelve llamadas, cache y usd. |
| 3 | guion_v4 (f)/(h) y llamador | OK con observación | `cierre_no_dicho` y `pago_no_dicho` devuelven (bloqueantes, altas). Las oraciones del cap son `[(k, s)...]` con `ev._sentences`. Un dato sin ancla va a `verificar` aunque A1/A2 digan sí (`_dicho_o_verificado`; lo cubre `test_sin_ancla_sonnet_decide_aunque_a2_diga_si`). `bloqueantes` suma las altas a `ids_usados` del párrafo, las deja en `ULTIMAS_ALTAS` y `metricas` las guarda en `confirmados_sonnet` y `verificador`. El párrafo no recibe claves nuevas. |
| 4 | Tests A.4 | OK | test_module_f55.py (17 tests). Casos de §3: D21 A1, D10 None, D42 A2, D85 A2, D92 cap 1 A1. También el conjunto A1 de 13 y el A2 de 4, pedido puro, (f)/(h) con verificar sí/no/None y `ids_usados` de los 7 caps viejos y nuevos (antes ⊆ después, diferencia escrita). Test real de Sonnet con skipif `F55_REAL`. |
| 5 | Salida A | OK | SALIDA_A.md: tabla de D21/D10/D42/D85 en viejo y nuevo, `ids_usados` antes→después por párrafo, 3 llamadas, 1 caché, US$ 0,0091. Bloqueantes (f)/(h) en 0 en ambos. |
| 6 | Nota de las 3 fallas nuevas | OK | Confirmado. test_module_f48.py:16-18 lee `01b_narration.json` de producción y espera «1943–2024». test_module_f51c.py:42 espera «paredes de chapa.» y «seguridad pública».» (f51c ×2). Las 3 fallas reproducen sin red. El diff 3a45c75..HEAD no toca datos de producción, solo código, tests y lab. Es la narración que F54 B.5 regeneró, no F55. |
| 7 | Fuera de alcance | OK | `git diff --name-only 3a45c75 HEAD` no contiene research_v3 ni m01a_escaleta. |

Observaciones (no bloqueantes):
- guion_v4.py, `_dicho_o_verificado`: cada alta lleva una clave extra `"que"` además de las 5 del handoff {id, cap, parrafo, oracion, regla}. Es inofensiva y `test_f_y_h_devuelven_bloqueantes_y_altas` la fija en el test, pero no está en el contrato.
- La Salida A muestra D21 con Sonnet «sí» en el nuevo y D42 «sí» en el viejo, y D10 confirmado por Sonnet (cap 6, oración 11). Eso hace creíble el diseño, pero el resultado de Sonnet es un solo run; el test real no lo corrí.
- Los datos que A1/A2 dan por dichos y no son `dato_central` de cierre ni de pago entran a `ids_usados` sin segunda opinión. El handoff lo acepta (D92 cap 1, D135, D144).

Fuera de alcance: ninguno. Aparte quedan sin commitear `diag_234_cap4.py` y `lab/hyperframes/f28/a/f28a.log`; ya estaban modificados antes de F55, no vienen de estos commits. El sticker `research.json` y MAPA son regeneración legítima por el cambio de md5 de evidence.py.

Riesgos que el contrato no cubre: `bloqueantes` modifica `parrafos` en el lugar y la alta usa un índice de párrafo calculado sobre `ps_ids`. Eso depende de que `with_ids` conserve el orden. Los 3 tests de producción (f48, f51c ×2) quedan rojos hasta que alguien los actualice, y la suite amplia seguirá mostrando 8 fallas.

## Adenda de CC (Parte A)
- **Clave `"que"` en las altas:** dice qué pago o cierre confirmó Sonnet (para la Salida A y el reporte); no la lee ningún otro módulo. Si el analista la quiere fuera, es una línea.
- **Test real:** lo corrí yo una vez con `F55_REAL=1` (pasa: D10 confirmado en la oración con «Colonial», 1 llamada); el revisor no lo repitió a propósito.
- **`with_ids` conserva el orden** (recorre `parrafos` en orden y devuelve una lista nueva del mismo largo): el índice de párrafo de la alta es el mismo en `ps_ids` y en `parrafos`.


---

# Parte B — dedupe de citas del pool · PARADA B

**Gasto Parte B: US$ 0** (sin API). Acumulado F55: ≈ US$ 0,012. Confirmación de Omar: `527040a` (0,7 + mismo autor, 19:30).

## Para Omar, en corto
- Dos citas del mismo autor que dicen lo mismo con palabras casi iguales ahora son una sola en el pool: queda la que tiene más fuentes (o la más larga) y la otra queda anotada como descartada apuntando a la que queda.
- En Wittenoom: 58 citas → 50, los 8 pares que había encontrado el analista (Q12/Q25 incluido, el que el guionista dijo dos veces), ninguno de más.
- El pool de Wittenoom ya está deduplicado en disco; la escaleta, el guion y el papel viejos siguen apuntando a 8 ids que ya no existen (22 referencias): la Parte D los regenera.

## Commits
| commit | qué |
|---|---|
| `551ab8f` | `research_v3._similitud_citas` / `_dedupe_citas` / `remapear_ids` + llamada en `build_pool`; `dedupe_pool.py` aplicado; `SALIDA_B.md`; tests; sticker; MAPA |
| (este) | reporte (esta sección), ESTADO, logs |

## Módulos: antes → después
| módulo | antes | después |
|---|---|---|
| `researcher_steps/research_v3.py` | las citas iban al pool tal cual | `UMBRAL_DEDUPE_CITAS = 0.7` (DECISIONES 19:30); `_similitud_citas(a, b)` = `|Ca∩Cb| / min(|Ca|,|Cb|)` con `C = evidence._content(texto)`, solo si los dos autores existen y son iguales tras `evidence.norm` (igualdad exacta, sin parcial; sin autor → None); `_dedupe_citas(pool, log)`: queda la de más `n_fuentes` (empate: la más larga; empate total: la primera), los ids no se renumeran, los `docs` de la que sale se suman a la que queda y `n_fuentes` se recalcula, la descartada va a `pool["_descartados"]` como `{"kind": "citas", "id", "duplicado_de", "similitud", "motivo": "cita duplicada", "autor", "texto"}`; se llama en `build_pool` después de `verify_pool` y antes del segundo `person_stats` (así `n_citas` de los personajes ya cuenta sin duplicados) y antes de `add_fragments` y del digest; `remapear_ids(obj, pool)`: copia de `obj` con cada id descartado → su `duplicado_de` en listas de ids e ids sueltos (dos ids iguales en una lista quedan uno) |
| `lab/hyperframes/f55/dedupe_pool.py` (nuevo, lab) | — | aplica `_dedupe_citas` al pool de Wittenoom sin volver a investigar: lee `data/topics_db.json`, respalda `data/topics_db.pre_f55_dedupe.json`, escribe el pool en `topics_db.json` y en `_steps/<id>/01_facts_sources.json` (los dos tenían el mismo pool, byte a byte); lista las referencias a ids descartados en escaleta, skeleton, `ids_usados` y papel de F54 (de `f55/antes/`, idénticos a `_steps`) → `SALIDA_B.md`. `--seco` no escribe |

Tests (`test_module_f55.py`, +5 → 22): el umbral; los 8 pares de Wittenoom con la función de producción dan exactamente 0,94 · 0,92 · 0,90 · 0,89 · 0,88 · 0,88 · 0,73 · 0,71, Q19/Q32 = 0,50 (no se deduplica), Q30/Q36 y Q18/Q36 no se comparan (autores distintos), 58 → 50 sin renumerar; más fuentes gana a más larga y los `docs` se suman (`n_fuentes` 2 → 3); empate en fuentes → la más larga; sin autor y otro autor no se comparan; `remapear_ids` (listas, ids sueltos, strings que no son id, copia, sin descartados devuelve igual).

## Decisiones de CC (Parte B)
1. **Dónde se llama en `build_pool`:** después de `verify_pool` (así el `n_fuentes`/`verificacion` de cada cita ya está) y antes del segundo `person_stats`, de `add_fragments` y del digest, para que nada río abajo vea las descartadas. El handoff decía «al cerrar el pool»; este es el último punto antes de que el pool se use.
2. **Empate total** (mismas fuentes, mismo largo): queda la primera del pool (id menor). No pasó en Wittenoom.
3. **La descartada guarda también `autor` y `texto`** además de los 4 campos del handoff, para que la lista de descartados se lea sola (como las demás entradas de `_descartados`, que llevan `texto`).
4. **El script escribe en los dos lugares** donde vive el pool de Wittenoom (`topics_db.json`, que lee `fase1_5`, y `01_facts_sources.json`), con respaldo del primero; `data/` está fuera de git. No recalculé `person_stats` (`n_citas` por persona) sobre el pool deduplicado: se recalcula solo en un research nuevo; anotado.
5. **Qué pasa con `01e_pantalla.json`:** las 2 referencias están en `descartados[].pool_id` (citas que el papel ya había descartado), no en fichas vivas.
6. **(g) «cita repetida»** sigue mirando ids: queda en «lo abierto» («con el dedupe ya no debería hacer falta»), como pide el handoff.

## Salida B (texto; entera en `lab/hyperframes/f55/SALIDA_B.md`)

## 1. Los pares: cuál quedó y por qué

| sale | queda | similitud | autor | n_fuentes (sale → queda) | por qué queda | texto que sale | texto que queda |
|---|---|---|---|---|---|---|---|
| Q12 | Q25 | 0.88 | María Bernal | 1 → 2 (docs ['F08', 'F07']) | más larga (empate en fuentes) | Iba pegadita a mi marido, como una niña. Pero estaba orgullosa. Me había enamorado de aque | Me pegué a mi marido, como una niña pequeña. Pero estaba orgullosa. Me había enamorado de  |
| Q26 | Q14 | 0.88 | Víctor Calvo | 1 → 2 (docs ['F07', 'F08']) | más larga (empate en fuentes) | Salimos de Málaga y tardamos más de 20 días en barco en llegar a Australia. Pasamos por el | Salimos de Málaga y tardamos más de 20 días en llegar en barco a Australia. Pasamos por el |
| Q15 | Q27 | 0.9 | Víctor Calvo | 1 → 2 (docs ['F08', 'F07']) | más larga (empate en fuentes) | El avión era pequeño, de hélices, y se movía muchísimo. Aterrizamos en una pista en medio  | El avión era pequeño, de hélice, y se movía mucho. Aterrizamos en una pista en medio de un |
| Q28 | Q16 | 0.89 | Daniel Écija (hijo) | 1 → 2 (docs ['F07', 'F08']) | más larga (empate en fuentes) | El primer día de trabajo de nuestro padre hubo una explosión y murieron varias personas. C | El primer día de trabajo de nuestro padre hubo una explosión y murieron varias personas. Y |
| Q29 | Q17 | 0.73 | Víctor Calvo | 1 → 2 (docs ['F07', 'F08']) | más larga (empate en fuentes) | Apenas había medidas de seguridad. Había muchos accidentes y las ambulancias venían todo e | No tenían apenas medidas de seguridad. Había muchos accidentes y cada dos por tres aparecí |
| Q30 | Q18 | 0.92 | Daniel Écija (hijo) | 1 → 2 (docs ['F07', 'F08']) | más larga (empate en fuentes) | Mi padre describía Wittenoom como un lugar sin ley. Un pueblo con una vida bastante primit | Mi padre nos habló de Wittenoom como un lugar sin ley. Un pueblo con una vida bastante pri |
| Q20 | Q33 | 0.94 | Melita Markey | 1 → 2 (docs ['F08', 'F07']) | más larga (empate en fuentes) | El Gobierno dejó de contar en 2.000, pero ahora se calcula que la cifra puede ser superior | El gobierno dejó de contar en 2000, pero ahora se estima que la cifra puede ser superior a |
| Q23 | Q35 | 0.71 | Daniel Écija (hijo) | 1 → 2 (docs ['F08', 'F07']) | más larga (empate en fuentes) | Ese sitio nos cambió la vida para siempre. Nosotros nos quedamos sin padre, y mi madre sin | Ese lugar cambió nuestras vidas para siempre. Perdimos a nuestro padre, y mi madre perdió  |

Pares que NO se deduplican (control del handoff §4):

- Q30/Q36: similitud no se compara (autores distintos o sin autor) · autores «Daniel Écija (hijo)» / «Un oficial de policía»
- Q18/Q36: similitud no se compara (autores distintos o sin autor) · autores «Daniel Écija (hijo)» / «Un oficial de policía»
- Q19/Q32: similitud 0.50 · autores «Víctor Calvo» / «Víctor Calvo»

### 2. Qué apunta hoy a ids descartados (solo listar; la Parte D regenera todo desde la escaleta)

| archivo | dónde | id | debería ser |
|---|---|---|---|
| 01a_escaleta.json | beats[1].datos_apoyo[2] | Q12 | Q25 |
| 01a_escaleta.json | beats[2].datos_apoyo[0] | Q15 | Q27 |
| 01a_escaleta.json | beats[8].datos_apoyo[1] | Q23 | Q35 |
| 01a_escaleta.json | beats[12].datos_apoyo[2] | Q20 | Q33 |
| 01a_escaleta.json | caps[1].evidence_ids[3] | Q12 | Q25 |
| 01a_escaleta.json | caps[1].evidence_ids[8] | Q15 | Q27 |
| 01a_escaleta.json | caps[4].evidence_ids[9] | Q23 | Q35 |
| 01a_escaleta.json | caps[6].evidence_ids[10] | Q20 | Q33 |
| 01a_skeleton.json | chapters[1].evidence_ids[3] | Q12 | Q25 |
| 01a_skeleton.json | chapters[1].evidence_ids[8] | Q15 | Q27 |
| 01a_skeleton.json | chapters[4].evidence_ids[9] | Q23 | Q35 |
| 01a_skeleton.json | chapters[6].evidence_ids[10] | Q20 | Q33 |
| 01b_guionista_v4.json | parrafos[1].ids_usados[5] | Q12 | Q25 |
| 01b_guionista_v4.json | parrafos[12].ids_usados[0] | Q23 | Q35 |
| 01b_guionista_v4.json | reparacion.parrafos[1].ids_usados[5] | Q12 | Q25 |
| 01b_guionista_v4.json | reparacion.parrafos[12].ids_usados[0] | Q23 | Q35 |
| 01b_narration.json | chapters[1].datos_usados[5] | Q12 | Q25 |
| 01b_narration.json | chapters[1].ids_usados[5] | Q12 | Q25 |
| 01b_narration.json | chapters[4].datos_usados[6] | Q23 | Q35 |
| 01b_narration.json | chapters[4].ids_usados[6] | Q23 | Q35 |
| 01e_pantalla.json | descartados[5].pool_id | Q15 | Q27 |
| 01e_pantalla.json | descartados[12].pool_id | Q23 | Q35 |

Total de referencias a ids descartados: 22.

Log:

    [dedupe citas] Q12 → Q25 (0.88); Q26 → Q14 (0.88); Q15 → Q27 (0.9); Q28 → Q16 (0.89); Q29 → Q17 (0.73); Q30 → Q18 (0.92); Q20 → Q33 (0.94); Q23 → Q35 (0.71)

Escrito: `C:\CLAUDE_PROJECTS\automatization_videos\data\topics_db.json` (respaldo `topics_db.pre_f55_dedupe.json`) y `C:\CLAUDE_PROJECTS\automatization_videos\data\scripts\_steps\123bbb64-9fca-4395-8bf4-57d60e219ef1\01_facts_sources.json`.

## Suite
`bash lab/hyperframes/f41/verificar.sh f55b` (logs en `lab/hyperframes/f41/f55b/`, corrida sobre el commit `551ab8f`): ch02 md5 `f792f3d483a1fa42daed5f7f0e054f46`; rápida **55 passed**; amplia **1113 passed** + 7 fallas: las 4 previas (`m03_merge_timing` ×2, `gfx_lab` ×2) y las 3 de `f51c`/`f48` clavadas a la narración vieja de Wittenoom (ver Parte A); `mapa_modulos.py --check`: 0 fallas (158).

## Lo que queda abierto (Parte B)
1. (g) «cita repetida» mira ids: con el dedupe ya no debería hacer falta; se decide después de la Parte D.
2. `person_stats` (`n_citas` por persona) del pool de Wittenoom no se recalculó tras el dedupe (solo lo hace un research nuevo).
3. Las 22 referencias a ids descartados en la escaleta/guion/papel de F54: las regenera la Parte D; hasta entonces `01a_escaleta.json` de `_steps` apunta a Q12, Q15, Q20 y Q23.
4. Pools de otros temas (Vajont, Kyshtym, Orleans) no se deduplicaron: solo con un research nuevo o corriendo `dedupe_pool.py` adaptado.
5. `remapear_ids` no tiene llamador en producción (el handoff la pide con test; la Parte D regenera desde la escaleta). Si alguna vez se reanuda desde `--from m01b` con una escaleta vieja, habría que llamarla ahí.

**PARADA B.**

## Veredicto de revisor-handoff (Parte B, íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | `_similitud_citas` = |Ca∩Cb|/min, C = `ev._content`; autor igual tras `ev.norm` (exacto); sin autor → no se compara | OK | researcher_steps/research_v3.py (551ab8f), `_similitud_citas`. Devuelve None si falta autor o difieren, y también si alguna cita no tiene palabras de contenido (guarda extra, sin número nuevo). |
| 2a | `_dedupe_citas`: umbral 0,7 como constante propia | OK | `UMBRAL_DEDUPE_CITAS = 0.7`, con comentario a DECISIONES 19:30. La línea existe en DECISIONES.md:163. |
| 2b | Queda la de más n_fuentes (empate: la más larga); ids sin renumerar; docs sumados; n_fuentes recalculado | OK | Compara la tupla (n_fuentes, len(texto)). Une docs sin duplicados e incluye el doc_id de la descartada. |
| 2c | Descartada a pool["_descartados"] con kind, id, duplicado_de, similitud, motivo | OK | Agrega autor y texto, como se declaró. |
| 2d | Llamada en build_pool | OK | Va tras verify_pool y antes del segundo person_stats, add_fragments y build_digest. Es razonable: digest y fragmentos se arman sobre el pool deduplicado. |
| 3 | `remapear_ids(obj, pool)` con test | OK | Devuelve copia, reemplaza en listas y strings sueltos, no repite ids en una lista. Corrí `python -m pytest -q test_module_f55.py -k "dedupe or pares or remapear or fuentes or empate"`: 5 passed. |
| 4a | dedupe_pool.py sin API ni tocar fase1_5 | OK | Solo importa fase1_5 para leer la constante TOPICS_DB; imports sin SDK de modelos. fase1_5.py no está en el diff de 551ab8f. |
| 4b | 58 → 50 y similitudes de los 8 pares | OK | Recalculé con la función de producción sobre f55/antes/01_facts_sources.json (58 citas): Q12/Q25 0,875; Q26/Q14 0,88; Q20/Q33 0,94; Q23/Q35 0,706; Q17/Q29 0,727; Q19/Q32 0,50. Coinciden con §4 del handoff. |
| 4c | Escritura con respaldo | OK | data/topics_db.json: 50 citas y 8 descartadas kind=citas. _steps/123bbb64.../01_facts_sources.json: 50 citas. data/topics_db.pre_f55_dedupe.json existe. |
| 5 | B.3: referencias solo listadas; (g) a «lo abierto» | OK | SALIDA_B.md lista 22 referencias (escaleta, skeleton, ids_usados, papel) sin tocarlas. F55_REPORT.md:338 y :400 dejan (g) en lo abierto con la nota «con el dedupe ya no debería hacer falta». |
| 6 | Salida B en el reporte | OK | Tiene los 8 pares con cuál quedó y por qué, los controles Q30/Q36, Q18/Q36 y Q19/Q32, y la lista de 22 referencias. |
| 7 | Nada fuera de alcance en 551ab8f | OK | Archivos: research_v3, test_module_f55, dedupe_pool.py, SALIDA_B.md, sticker research.json, MAPA json y md. Todo es de B o su documentación obligatoria. |

Fuera de alcance: ninguno (no revisé los cambios sin commitear de la Parte C, como se pidió).

Observaciones:
- En los 8 pares la razón de «queda» es «más larga (empate en fuentes)»: todas tenían 1 fuente, así que el criterio de más n_fuentes nunca decide en Wittenoom. Es correcto según el contrato, pero ese criterio solo está probado con test sintético, no con datos reales.
- Los 22 ids colgantes siguen en escaleta, ids_usados y papel. El handoff lo acepta hasta la Parte D; mientras tanto la escaleta apunta a ids que ya no están en el pool.
- data/topics_db.json no figura como modificado en git (probablemente ignorado), así que el pool dedupeado se verifica solo por estado en disco, no por commit.

Riesgos que el contrato no cubre:
- `_content` compara conjuntos de palabras: dos citas del mismo autor con vocabulario parecido pero distinto sentido podrían fusionarse. Con 58 citas dio 0 falsos; con pools nuevos no hay garantía.
- Nada llama a `remapear_ids` en el flujo de producción; solo existe y está testeada. La Parte D depende de que la escaleta se regenere sobre el pool nuevo.

## Adenda de CC (Parte B)
- **`remapear_ids` sin llamador:** el handoff la pide como función con test («reemplaza ids descartados por su duplicado_de en listas de ids (con test)») y deja la regeneración a la Parte D; si la Parte D arranca desde una escaleta vieja (`--from m01b`), ahí es donde debería llamarse. Anotado en «lo abierto».
- **`data/` fuera de git:** el pool deduplicado se prueba por disco (50 citas, 8 descartadas) y por el respaldo `topics_db.pre_f55_dedupe.json`; el pool de antes (58) está versionado en `lab/hyperframes/f55/antes/01_facts_sources.json`.


---

# Parte C — promesa de una oración · C.0 opción (ii) · PARADA C

**Gasto Parte C: US$ 0.** Acumulado F55: ≈ US$ 0,012. Decisiones de Omar: 19:15 (promesa = una oración) y 19:30 (C.0 opción ii).

## Para Omar, en corto
- La promesa del gancho es una sola oración: el esquema se lo dice al modelo, el ejemplo del prompt ahora tiene una, y si igual vienen dos, el código se queda con la primera y lo anota (sin gastar).
- Como pediste, las 6 versiones viejas del prompt de la escaleta se fueron del código con sus tests (quedan sus `.md` en `lab/` como historia); el prompt vigente pasa a `f55-1`.

## Commits
| commit | qué |
|---|---|
| `c7dfb7f` | `m01a_escaleta` (esquema, ejemplo, validate, métrica, fuera las 6 versiones viejas), tests, `PROMPT_ESCALETA_f55_1.md`, sticker, MAPA |
| (este) | reporte (esta sección), ESTADO, logs |

## Módulos: antes → después
| módulo | antes | después |
|---|---|---|
| `script_engine/m01a_escaleta.py` | `promesa_gancho: _S` en el esquema; `<ejemplo>` con la promesa en dos oraciones; `SYSTEM_V2` + 6 constantes viejas (`SYSTEM_V2_F26_1`, `F25_1`, `F24_1`, `F22_2`, `F22_1`, `F16_1`) con sus `PROMPT_VERSION_V2_*`; prompt `f54-1` | `promesa_gancho: {"type": "STRING", "description": "Una sola oración: lo que está en juego."}` en `SCHEMA` y `SCHEMA_FICHA` (**confirmado:** el esquema viaja por la API como `output_config.format` / `response_schema`, no dentro del texto del prompt: `claude_helpers.call_json` l. 174–175); `<ejemplo>`: una sola línea cambia (abajo); `validate`: `len(evidence._sentences(promesa)) > 1` → reparación por código (se queda la primera) + aviso en `rep`, `esc["_promesa_oraciones"]` y métrica `promesa_oraciones`; **fuera las 6 constantes viejas y sus 6 `PROMPT_VERSION_V2_*`** (1708 → 1448 líneas); `PROMPT_VERSION_V2 = PROMPT_VERSION_COLUMNA = "f55-1"` |

Tests: borrados los que solo comparaban constantes viejas: `test_module_f26.py` entero (3 tests: f26-1 contra su .md, f25-1 con su versión, los tres agregados), `test_module_f24.py::test_prompt_escaleta_f24_literal_y_una_sola_linea`, `test_module_f25c.py::test_escaleta_f25_1_literal_y_un_solo_cambio`; ajustados: `f16` (solo `TAREA_V2`), `f17` (fuera la línea del md5 de F16_1; columna `f55-1`), `f21`/`f22`/`f22d`/`f23` (el md5 de la escaleta f22-2 se lee del `.md` o sale de la lista), `f54` (f26-1 → f54-1 comparados por sus `.md`); nuevos en `test_module_f55.py` (+4 → 26): f55-1 literal contra su `.md` y una sola línea distinta de f54-1; las 12 constantes ya no existen y `SYSTEM_V2` tiene un solo `<rol>`; esquema con la descripción; promesa de dos oraciones → se queda la primera, aviso, métrica.

## Decisiones de CC (Parte C)
1. **Se borraron 6 constantes, no 5.** La línea de DECISIONES nombra 5 (`F26_1, F25_1, F24_1, F22_2, F22_1`) y dice «queda solo la vigente»; el handoff C.0 (ii) dice `SYSTEM_V2_F26_1…F16_1`. Borré también `SYSTEM_V2_F16_1`/`PROMPT_VERSION_V2_F16`: era la única forma de que quede solo la vigente. Si Omar quería conservar la de F16, es un `git revert` parcial.
2. **Los tests de tandas cerradas que comparaban constantes viejas se borran** (f26 entero, una función en f24 y otra en f25c): «lo viejo se borra». Los que además chequeaban otra cosa se ajustaron para leer el `.md` histórico (los `.md` de F16, F22, F24, F25c, F26 y F54 siguen en `lab/`).
3. **La reparación por código de la promesa** va en `rep` (reparaciones), no en `hard`: el handoff pide «aviso + reparación por código». La métrica `promesa_oraciones` cuenta las oraciones que vinieron.
4. **La versión sube a `f55-1`** (handoff C.0 ii: «la vigente, que pasa a f55-1»); `PROMPT_VERSION_COLUMNA` acompaña como siempre.
5. `lab/mapa/tests_collect.json` / `tests_lab.json` (digests de tests, los regenera otro proceso) siguen nombrando `test_module_f26.py`; `MAPA --check` da 0. Anotado.

## Salida C (texto): diff completo del prompt de la escaleta antes (f54-1) → después (f55-1)
65 líneas en los dos; 64 iguales; 1 distinta(s):

```diff
- promesa_gancho: «Once personas esperaron veintitrés días un barco que no llegó. Esta es la historia de quién decidió que no llegara.»
+ promesa_gancho: «Once personas esperaron veintitrés días un barco que alguien había decidido que no llegara.»
```

Y lo que no es texto del prompt pero el modelo recibe: el esquema de salida (`SCHEMA_FICHA`), donde `promesa_gancho` pasa de `{"type": "STRING"}` a `{"type": "STRING", "description": "Una sola oración: lo que está en juego."}`.

## Suite
`bash lab/hyperframes/f41/verificar.sh f55c` (logs en `lab/hyperframes/f41/f55c/`, sobre `c7dfb7f`): ch02 md5 `f792f3d483a1fa42daed5f7f0e054f46`; rápida **53 passed** (55 − 2: los tests de f24 y f25c que solo comparaban constantes viejas), 3 skipped; amplia **1112 passed** + 7 fallas: las 4 previas (`m03_merge_timing` ×2, `gfx_lab` ×2) y las 3 de `f51c`/`f48` clavadas a la narración vieja de Wittenoom (ver Parte A); `mapa_modulos.py --check`: 0 fallas (158).

## Lo que queda abierto (Parte C)
1. Decisión 1 (6 constantes y no 5): confirmar.
2. Los digests de tests del mapa (`tests_collect.json`, `tests_lab.json`) listan `test_module_f26.py` hasta que se regeneren.
3. `lab/hyperframes/f54/salida_a.py` (ya roto por v5.5) ahora también por `SYSTEM_V2_F26_1`.
4. `evidence._sentences` corta en abreviaturas («Dr.», «Mt.»): una promesa de una oración con abreviatura se recortaría mal (aviso visible en `rep`). Sin caso real todavía.

**PARADA C.** La Parte D (Wittenoom en texto, combinada) solo con el OK del analista.

## Veredicto de revisor-handoff (Parte C, íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | C.1 promesa_gancho con description exacta en SCHEMA y SCHEMA_FICHA | OK | m01a_escaleta.py:133 tiene el texto exacto. SCHEMA_FICHA es deepcopy de SCHEMA (:160), así que lo hereda. `SCHEMA['properties']['promesa_gancho']` lo confirma. SCHEMA_FICHA se pasa como `response_schema` en :1310. |
| 1b | El reporte confirma que el esquema viaja por API y no dentro del texto del prompt | PARCIAL | F55_REPORT.md:481 dice «lo que no es texto del prompt pero el modelo recibe: el esquema de salida (SCHEMA_FICHA)». Lo dice, pero sin las palabras «por API». El mensaje del commit sí dice «va por API en el esquema». Es una observación menor. |
| 2 | C.2: cambia una sola línea del ejemplo; nada más | OK | Diff de los .md de f54-1 y f55-1: solo cambian el título, la nota de cabecera (línea 3) y la línea 39 de `promesa_gancho`. La línea 39 pasa exactamente de «…un barco que no llegó. Esta es la historia de quién decidió que no llegara.» a «…un barco que alguien había decidido que no llegara.». `SYSTEM_V2` está contenida en el .md f55-1. PROMPT_VERSION_V2 y PROMPT_VERSION_COLUMNA son "f55-1". |
| 3 | C.3: más de una oración → aviso y reparación por código, métrica, sin número nuevo | OK | :411-415 usa `ev._sentences`, deja la primera oración y agrega el aviso a `rep`. :1109 agrega la métrica `promesa_oraciones`. El único umbral es `> 1`, tomado del handoff. Hay un test nuevo en test_module_f55. |
| 4 | C.0 (ii): constantes viejas borradas | OK | `dir(m)` no tiene ninguna `SYSTEM_V2_*` ni `PROMPT_VERSION_V2_*` con sufijo. Solo quedan SYSTEM_V2 y PROMPT_VERSION_V2. |
| 5 | Tests: borrados y ajustados | OK | Se borraron f24::test_prompt_escaleta_f24_literal_y_una_sola_linea, f25c::test_escaleta_f25_1_literal_y_un_solo_cambio y test_module_f26.py. Los tres comparaban solo constantes viejas. Los ajustes en f16, f17, f21, f22, f22d, f23 y f54 quitan asserts de constantes o comparan contra los .md. Los md5 y los diffs de una sola línea siguen igual (por ejemplo f54 compara f26-1 y f54-1 por .md). test_module_f55 agrega 4 tests: f55-1 literal, constantes borradas, esquema y promesa de dos oraciones. Corrí el pytest que pediste: 244 passed, 15 skipped. |
| 6 | Salida C: diff completo antes/después | OK | F55_REPORT.md:473-481 muestra 65 líneas, 64 iguales y 1 distinta, con el diff exacto. Agrega el cambio del esquema. |
| 7 | Alcance | OK | c7dfb7f no toca research_v3, guion_v4 ni evidence. Solo toca m01a_escaleta, tests, el .md nuevo, el sticker y el MAPA. El commit de docs posterior solo toca ESTADO, F55_REPORT y logs f55c. |
| 8 | `grep SYSTEM_V2_F\|PROMPT_VERSION_V2_F` fuera de lab/ y _* | OK | Quedan solo 4 coincidencias, todas en strings o comentarios de tests: test_module_f16.py:54 (un comentario) y test_module_f55.py:351-353 (los nombres que el test verifica como ausentes). No hay código vivo. |

Decisión 1 (6 constantes en vez de 5): está bien, no es un apartamiento. DECISIONES 19:30 enumera 5 pero dice «queda solo la vigente». El handoff C.0 (ii) dice «F26_1…F16_1». Dejar F16_1 habría roto «queda solo la vigente». Quedó declarada en F55_REPORT.md:467 y abierta para confirmar en :487. Lo que falta es la confirmación explícita de Omar.

Fuera de alcance: ninguno.

Observaciones, riesgos y pendientes que el contrato no cubre:
- `ev._sentences` parte en abreviaturas. «El Dr. Smith llegó… Mt. Wittenoom» se divide en 3 «oraciones». Con la reparación por código, una promesa legítima de una sola oración con «Dr.», «Mt.» o similar quedaría truncada en «El Dr.» y se avisaría un falso positivo. No hay test de ese caso.
- El reporte deja abiertos: los digests tests_collect.json y tests_lab.json listan test_module_f26.py hasta regenerarse, y f54/salida_a.py ya estaba roto y ahora también por `SYSTEM_V2_F26_1`. Ambos están fuera del código de producción.

## Adenda de CC (Parte C)
- **Fila 1b:** confirmado y dicho con todas las letras acá: el esquema (`SCHEMA_FICHA`, con la `description`) viaja **por la API** como `response_schema` → `output_config.format` (`claude_helpers.call_json` l. 174–175) / `response_schema` de Gemini; no es texto del prompt.
- **Abreviaturas en `_sentences`:** cierto; es el mismo cortador que usa todo el pipeline (guion, medida, (f)/(h)). Una promesa con «Dr.» quedaría cortada; el aviso queda en `rep` y se ve en el reporte de la escaleta. A la lista, sin número nuevo.


---

# Adenda D.0 — el pool deduplicado llega a todos los que lo leen · PASÓ (sin PARADA)

Adenda: `lab/hyperframes/f55/ADENDA_F55_D0.md` (md5 `86eb19a7729dd6aa34b63b12eacf3c9e`, verificado). **Gasto: US$ 0.** DECISIONES 20:25 escrita (`00838c2`): las 6 constantes de la escaleta se quedan borradas, incluida la de F16.

## Para Omar, en corto
- El analista encontró que el pool de Wittenoom vive en tres copias y el dedupe había escrito dos; y que la ficha del caso (que la Parte D no regenera) apuntaba 36 veces a citas que ya no existen.
- Ahora las tres copias son iguales (50 citas, los mismos 8 descartados) y la ficha se corrige **al cargarla**, en memoria, para cualquier tema que tenga citas descartadas: 36 → 0 ids colgantes. El archivo de la ficha no se toca.
- Los 3 tests viejos que fallaban desde F54 B.5 vuelven a verde leyendo la narración congelada para la que se escribieron.

## Commits
| commit | qué |
|---|---|
| `00838c2` | DECISIONES 20:25 |
| `3e1cc98` | `dedupe_pool.py` (3 copias), `ficha_caso.load` + `ids_remapeados`, `remapear_ids` con claves, tests f48/f51c a la copia congelada, tests D.0, `SALIDA_D0.md`, `SALIDA_B.md` §3, stickers, MAPA |
| (este) | reporte (esta sección), ESTADO, logs |

## Módulos: antes → después
| módulo | antes | después |
|---|---|---|
| `lab/hyperframes/f55/dedupe_pool.py` | escribía `topics_db.json` y `01_facts_sources.json` | también `_steps/<id>/00_pool_v3.json` (lo leen `ficha_caso` y `m01e_pantalla`); el dedupe es idempotente (sobre un pool ya deduplicado da 0 pares), así que se corre sobre las 3 copias y se comparan ids de citas y descartados (§3 de `SALIDA_B.md`); las tablas de pares se arman desde el pool de antes (`f55/antes/01_facts_sources.json`, 58) |
| `researcher_steps/ficha_caso.py` → `load(topic_id, steps_dir=None, log=None)` | leía el JSON tal cual | si `_steps/<id>/00_pool_v3.json` trae citas descartadas (`kind == "citas"` con `duplicado_de`), devuelve la ficha pasada por `research_v3.remapear_ids`, en memoria; `log` dice cuántos ids cambiaron (`ids_remapeados`, función nueva que cuenta ids sueltos, en listas y como claves); sin descartados, sin pool o con pool ilegible, la ficha tal cual. Lo usan `fase1_5` (ficha, escaleta, guion, columna) y `m01a_escaleta`: todos pasan por `load` |
| `researcher_steps/research_v3.py` → `remapear_ids` | listas e ids sueltos | también claves de dict que son ids; si la clave nueva ya existe, queda la existente |
| `test_module_f48.py`, `test_module_f51c.py` | leían `_steps/<Wittenoom>/01b_narration.json` (regenerado en F54 B.5 → 3 rojos) | leen `lab/hyperframes/f54/antes/01b_narration.json`, la copia congelada para la que se escribieron; no se borran |

Tests (`test_module_f55.py`, +3 → 29): `remapear_ids` con claves (y la clave nueva que ya existe); `ficha_caso.load` con pool con descartados (2 ids remapeados, log, el archivo no cambia), sin descartados (tal cual, sin log), sin pool y sin ficha; la ficha de Wittenoom cargada no contiene ninguno de los 8 ids descartados del pool de `_steps`.

## Decisiones de CC (D.0)
1. **La ficha en disco no tenía ids como claves de dict** (0); la extensión de `remapear_ids` a claves es general y queda probada con un caso sintético.
2. **`load` cuenta antes de remapear** (`ids_remapeados`) y solo remapea si hay algo que cambiar: una ficha sin ids colgantes vuelve el mismo objeto, sin copia ni log.
3. **El `log` de `load` es opcional** (firma compatible con todos los llamadores de hoy, que no lo pasan): el conteo aparece en el reporte por `SALIDA_D0.md`; en producción, `fase1_5` no lo imprime todavía (una línea cuando el analista la quiera).
4. **Los tests de f48/f51c no se borran**, como pide la adenda; apuntan a la narración congelada. La Parte D volverá a regenerar `_steps` sin tocarlos.

## Salida D.0 (texto)

## 1. Ids de citas en las tres copias del pool

Ver `SALIDA_B.md` §3 (corrida de `dedupe_pool.py` de D.0): `topics_db.json`, `01_facts_sources.json` y `00_pool_v3.json` tienen las mismas 50 citas y los mismos 8 descartados (Q12, Q15, Q20, Q23, Q26, Q28, Q29, Q30).

### 2. La ficha cargada (`ficha_caso.load`)

- ids descartados en `ficha_caso.json` **en disco**: 36 apariciones ({'Q15': 5, 'Q12': 7, 'Q20': 7, 'Q23': 11, 'Q26': 4, 'Q28': 2}); `ids_remapeados` = 36.
- log de `load`: ['  [ficha] 36 id(s) de citas duplicadas remapeados al cargar (el archivo no cambia)']
- `grep` de `Q12|Q15|Q20|Q23|Q26|Q28|Q29|Q30` sobre el JSON de la ficha **cargada**: **0**.
- el archivo en disco no cambia (md5 igual antes y después de `load`).

### 3. Las tres copias del pool (D.0)

| copia | citas | ids de citas | descartados (citas) |
|---|---|---|---|
| topics_db.json | 50 | Q01, Q02, Q03, Q04, Q05, Q06, Q07, Q08, Q09, Q10, Q11, Q13, Q14, Q16, Q17, Q18, Q19, Q21, Q22, Q24, Q25, Q27, Q31, Q32, Q33, Q34, Q35, Q36, Q37, Q38, Q39, Q40, Q41, Q42, Q43, Q44, Q45, Q46, Q47, Q48, Q49, Q50, Q51, Q52, Q53, Q54, Q55, Q56, Q57, Q58 | Q12, Q15, Q20, Q23, Q26, Q28, Q29, Q30 |
| 01_facts_sources.json | 50 | Q01, Q02, Q03, Q04, Q05, Q06, Q07, Q08, Q09, Q10, Q11, Q13, Q14, Q16, Q17, Q18, Q19, Q21, Q22, Q24, Q25, Q27, Q31, Q32, Q33, Q34, Q35, Q36, Q37, Q38, Q39, Q40, Q41, Q42, Q43, Q44, Q45, Q46, Q47, Q48, Q49, Q50, Q51, Q52, Q53, Q54, Q55, Q56, Q57, Q58 | Q12, Q15, Q20, Q23, Q26, Q28, Q29, Q30 |
| 00_pool_v3.json | 50 | Q01, Q02, Q03, Q04, Q05, Q06, Q07, Q08, Q09, Q10, Q11, Q13, Q14, Q16, Q17, Q18, Q19, Q21, Q22, Q24, Q25, Q27, Q31, Q32, Q33, Q34, Q35, Q36, Q37, Q38, Q39, Q40, Q41, Q42, Q43, Q44, Q45, Q46, Q47, Q48, Q49, Q50, Q51, Q52, Q53, Q54, Q55, Q56, Q57, Q58 | Q12, Q15, Q20, Q23, Q26, Q28, Q29, Q30 |

Las tres copias tienen los MISMOS ids de citas y los mismos descartados.


## Suite
`bash lab/hyperframes/f41/verificar.sh f55d0` (logs en `lab/hyperframes/f41/f55d0/`, sobre `3e1cc98`): ch02 md5 `f792f3d483a1fa42daed5f7f0e054f46`; rápida **53 passed**, 3 skipped; amplia **1118 passed** + **solo las 4 fallas previas** (`m03_merge_timing` ×2, `gfx_lab` ×2): los 3 de f51c/f48 volvieron a verde; `mapa_modulos.py --check`: 0 fallas (158).

## Lo que queda abierto (D.0)
1. `fase1_5` no imprime el log del remapeo de la ficha (la firma lo admite).
3. Dos menciones de ids descartados dentro de prosa de la ficha (`dice`: «El pasaje de Q23…», «Q26 añade…») no se remapean: son texto, no ids.
2. `person_stats` del pool de Wittenoom sigue sin recalcular tras el dedupe (de la Parte B).

**D.0 pasó entera → sigue la Parte D sin esperar** (pedido de Omar).

## Veredicto de revisor-handoff (D.0, íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | 3 copias del pool: mismos 50 ids de citas y mismos 8 descartados | OK | Lo recalculé por código. topics_db, 01_facts_sources y 00_pool_v3 dan 50 ids únicos, secuencia idéntica y descartados Q12, Q15, Q20, Q23, Q26, Q28, Q29, Q30. `lab/hyperframes/f55/dedupe_pool.py:47-62` escribe la tercera copia y compara las tres. |
| 2a | `load` remapea en memoria, el archivo no cambia, log con el conteo | OK | `researcher_steps/ficha_caso.py:751-775`. `fc.load(tid, log=lg)` devolvió el log "36 id(s) ... remapeados". Ninguna ruta de `load` escribe el archivo. |
| 2b | Sin descartados o sin pool devuelve tal cual; firma compatible | OK | `ficha_caso.py:767-773`: `log` es opcional. `test_module_f55.py` `test_ficha_load_remapea_en_memoria` cubre sin descartados, sin pool y sin ficha (None). Pasa. |
| 2c | Todos los que leen la ficha pasan por `load` | PARCIAL | Pasan por `load`: `fase1_5.py:270`, `fase1_5.py:300` y `script_engine/m01a_escaleta.py:850`. NO pasa: `script_engine/m03_expediente.py:29` lee `ficha_caso.json` directo con `_j(...)` y lo usa para las escenas del expediente. Ahí la ficha sigue con ids colgantes. |
| 3 | `remapear_ids` con claves de dict y su test | OK | `researcher_steps/research_v3.py:2148-2155`. Test `test_remapear_ids_tambien_claves_de_dict`, que cubre también el caso de clave ya existente. Pasa. |
| 4 | f48 y f51c leen `f54/antes/01b_narration.json`, pasan, no se borraron | OK | `test_module_f48.py:14-21`, `test_module_f51c.py:15`. Corrí `pytest test_module_f55 f48 f51c`: 37 passed, 1 skipped. |
| 5 | Sin constantes nuevas; US$ 0 | OK | El diff de 3e1cc98 no agrega constantes, ni red, ni llamadas a modelos. `UMBRAL_DEDUPE_CITAS` ya existía. |
| 6 | Salida D.0 con los 3 datos | PARCIAL | Los 3 datos están en `lab/hyperframes/f55/SALIDA_D0.md` y en la sección del reporte. El tercero dice «grep literal = 0», pero el grep literal de Omar no da 0. Detalle abajo. |
| 7 | DECISIONES 20:25 literal | OK | `DECISIONES.md:169`, texto idéntico al pedido. Commit 00838c2. |
| 8 | Nada fuera de alcance | OK | Los 17 archivos de `HEAD~3..HEAD` son el código, los tests y las salidas del pedido, más ESTADO, MAPA, stickers, F55_REPORT y los logs de f55d0. Los dos modificados sin commit (`diag_234_cap4.py` y `f28a.log`) ya estaban así antes de esta tanda. |

Hallazgos:
- **El «grep = 0» solo vale para ids como token.** Sobre el JSON de la ficha cargada, `Q12|Q15|Q20|Q23|Q26|Q28|Q29|Q30` da 2 coincidencias en texto libre de `dice`: «El pasaje de Q23 termina cortado...» y «Q26 añade en su rótulo...». Con el id entre comillas da 0. En disco el grep literal da 38, no 36. El reporte mide ids exactos y no lo aclara. Esos 2 textos nombran ids viejos dentro de prosa y `load` no los toca. Omar pidió el grep literal.
- **`m03_expediente.py:29`** (ver 2c). El reporte afirma que la ficha «se corrige al cargarla para cualquier tema» y no menciona este lector.
- Menor: `fase1_5` no imprime el log de `load`, y el reporte lo admite.

Fuera de alcance: ninguno.

Riesgos que el contrato no cubre: la Parte D en curso lee la ficha con `load` en `fase1_5` y en la escaleta, así que está cubierta. Todo lo que pase por `m03_expediente` (o cualquier lector directo) arrastrará ids viejos hasta que se arregle. Las menciones de ids en prosa de la ficha (Q23, Q26) quedan apuntando a citas descartadas.

## Adenda de CC (D.0) — con los dos hallazgos arreglados en el commit siguiente
- **2c, `m03_expediente.fuentes`:** arreglado: lee la ficha por `ficha_caso.load` (una línea; test `test_m03_expediente_lee_la_ficha_por_load`; f50b/f50c/f50d siguen verdes). Con eso **todos** los lectores de `ficha_caso.json` pasan por `load` (`grep "ficha_caso.json"` sobre producción: fase1_5 l. 297 solo mira si existe para el canon). Es la regla general de la adenda («para cualquier topic»), no un parche.
- **6, grep literal:** `SALIDA_D0.md` ahora trae los dos números: con el id como valor entero (`"Q12"`), disco 36 → cargada **0**; grep literal sin comillas, disco 38 → cargada **2**, y las 2 son menciones dentro de un texto libre (`dice`: «El pasaje de Q23 termina cortado…», «Q26 añade en su rótulo…»), no ids. `remapear_ids` cambia ids (strings enteros, listas, claves), no prosa; reescribir prosa de la ficha sería inventar texto. Queda anotado en «lo abierto».
- La Parte D, que ya corría cuando llegó este veredicto, lee la ficha por `fase1_5` y `m01a_escaleta` (los dos por `load`): no la afecta.


---

# Parte D — Wittenoom en texto, corrida combinada (detector + dedupe + promesa) · PARADA D

**Gasto Parte D: US$ 3,93** (`cost_history` 20:21–20:33: escaleta 1,64 (2 intentos: el 1.º frenó por «humano colectivo sin fuente del pool», el 2.º pasó), guionista 1,55, editar frase 0,08, partición 0,02, papel 0,63). **Acumulado F55: ≈ US$ 3,94.** Cero fotos, cero voz (`--batch` para en la PARADA del papel, como en F54 B.5: no hubo que inventar flags).

## Para Omar, en corto
- Wittenoom tiene escaleta, guion y papel nuevos en texto. La promesa del gancho salió en **una oración** (antes 3); los dos loops se declaran y, leídos con el detector nuevo, **se abren y se pagan** (uno con ancla, uno por A1/A2); el cierre vuelve a la imagen del gancho.
- El guion nuevo frena con **3 bloqueantes, los 3 falsos por otra causa**: la voz citó dos frases de citas que el dedupe sacó del pool (Q15 y una más), con las palabras de la cita descartada; el juez de citas no la encuentra (a) y el de contaminación la ve en «descartados» y la trata como de otro caso (d). Y sigue la (d) vieja del cap 3. El detector de F55 no frenó nada (0 llamadas a Sonnet: los datos del cierre y los pagos tenían ancla).
- El re-gancho se declaró en la escaleta pero el guionista no lo dijo (parecido 0,36).
- Ningún id descartado quedó en la escaleta, el skeleton, el guion ni el papel regenerados (grep 0). El `digest` del pool todavía los traía: corregido en las 3 copias.
- Decidís con el analista: nota 1–10 y si esta versión pasa a fotos.

## Commits
| commit | qué |
|---|---|
| `ea8ae11` | `salida_d.py` → `SALIDA_D.md`, `MEDIDA_RETENCION_D.md`, `d_run.log`; `dedupe_pool.py` remapea el `digest` del pool (3 copias) |
| (este) | reporte (esta sección), ESTADO |

## Corrida (texto, `lab/hyperframes/f55/d_run.log`)
`python fase1_5.py --topic 123bbb64-… --from m01a --batch`: compuerta verde (40 citas verificadas, antes 42: dos duplicadas se fueron) · ficha existente, cargada con 36 ids remapeados · **escaleta f55-1:** intento 1 con 1 bloqueante («humano colectivo sin fuente del pool»: el modelo puso un rótulo de la ficha como fuente), intento 2 limpio (24 reparaciones, 8 a métricas); 2 loops, 2 beats con `paga`, `recuerda_loop` en el beat 6 (último del cap 3), promesa de 1 oración · **guion f54-2:** 1935 palabras; bloqueantes **4 → 3** (3 ediciones por oración, 1 aceptada); PARADA del guion reportada y la cadena siguió · partición: cap 3 largo → un párrafo pasa al cap 4; cap 7 acortado · **papel m01e:** 3 intentos, 13 fichas · 6 sellos · 3 relojes → `01e_pantalla.md` · PARADA del papel.

### Los 3 bloqueantes del guion nuevo y qué son
| # | código | cap | qué dice | qué pasa de verdad |
|---|---|---|---|---|
| 1 | (a) | 3 | entre comillas, pero no es una cita del pool: «Aterrizamos en una pista en medio de una tierra muy muy roja…» | es el texto de **Q15**, descartada por duplicada de Q27 (0,90). La ficha trae esa frase con las palabras de Q15 (la ficha se escribió antes del dedupe; `load` remapea los ids, no los textos); el guionista la citó tal cual; el pool ya no tiene a Q15 → **falso positivo del dedupe** |
| 2 | (d) | 3 | fuera del caso (descartado en el pool): «El avión era pequeño, de hélices…» | la misma Q15: `m05.contamination` lee todo `_descartados` y trata la cita duplicada como un dato de otro caso → **falso positivo del dedupe** |
| 3 | (d) | 3 | fuera del caso: «Defensor del empleador no identificado» | el previo de F54 (no se toca, pedido de Omar) |

El crudo traía además una (a) en el cap 6 («Hay hijos de funcionarios que trabajaban en el pueblo, como …», texto de otra cita descartada) que la edición por oración sacó.

**Hallazgo (a la lista; arreglo general en un handoff aparte):** el dedupe deja en `_descartados` el texto de la cita que sale, y dos jueces lo leen mal: `contamination` (d) lo cuenta como «de otro caso» (una duplicada es el mismo hecho, no contaminación: debería saltar `kind == "citas"` con `duplicado_de`), y `false_quotes` (a) no acepta las palabras de la duplicada como la cita que quedó. Mientras la ficha conserve las palabras de la duplicada (sus textos no se remapean, solo sus ids), el guionista va a citar esa versión. Opciones: que `ficha_caso.load` también reemplace el texto de la cita por el de la que quedó, o que los jueces miren `duplicado_de`. Sin eso, el guion nuevo queda en PARADA por 2 frenos falsos más la (d) vieja.

## Decisiones de CC (Parte D)
1. **Corrida tal cual el handoff** (`--from m01a --batch`), misma invocación que F54 B.5; no se tocó `fase1_5` ni se agregaron flags.
2. **`digest` del pool:** la Salida D §6 encontró 8 ids descartados en `pool.digest.ids` de las 3 copias (el digest se armó antes del dedupe; en un research nuevo `build_pool` lo arma después). `dedupe_pool.py` remapea ahora todo lo del pool que no sea `citas` ni `_descartados` con `remapear_ids`, en las 3 copias; recorrido: 0 fuera de `_descartados`/ficha. La escaleta de la Parte D ya había corrido con el digest viejo: no leyó esos ids (0 en lo regenerado), porque la escaleta v2 lee la ficha, no el digest.
3. **No se tocaron los jueces (a)/(d)** ni la ficha: la Parte D es la medición; el arreglo del hallazgo va aparte.
4. **Medida de retención:** la de F54 (`medida_retencion.py`) sobre F54 = `f55/antes/` y F55 = `_steps`, sin panel ciego (la adenda de F55 no lo pide).

## Salida D (texto; entera en `lab/hyperframes/f55/SALIDA_D.md`)

## 1. Tabla A/B cap por cap

| cap | palabras F54 | F55 | años F54 | F55 | datos/min F54 | F55 | bloqueantes F54 (tras la ronda) | bloqueantes F55 (tras la ronda) |
|---|---|---|---|---|---|---|---|---|
| 1 | 168 | 161 | 2 | 1 | 0.9 | 0.9 | — | — |
| 2 | 263 | 220 | 3 | 4 | 3.3 | 3.9 | — | — |
| 3 | 368 | 433 | 11 | 5 | 2.0 | 2.0 | (d) fuera del caso (descartado en el pool): Defensor del emplead; (h) pago no dicho: el beat 5 paga la pregunta del beat 3 con D21; (h) pago no dicho: el beat 5 paga el loop L2 con D21, que no est | (a) entre comillas, pero no es una cita del pool: «Aterrizamos e; (d) fuera del caso (descartado en el pool): El avión era pequeño; (d) fuera del caso (descartado en el pool): Defensor del emplead |
| 4 | 335 | 322 | 2 | 4 | 1.7 | 2.7 | — | — |
| 5 | 252 | 292 | 5 | 7 | 4.0 | 3.9 | — | — |
| 6 | 278 | 297 | 7 | 4 | 1.6 | 3.4 | (h) pago no dicho: el beat 11 paga la pregunta del beat 10 con D | — |
| 7 | 249 | 210 | 5 | 6 | 3.5 | 2.7 | — | — |
| **total** | 1913 | 1935 | 35 | 31 | | | 4 | 3 |

Quién vio los bloqueantes del nuevo: código (f/h con `regla_dicho`) → lo que quedó arriba; Sonnet confirmó 0:  · verificador: 0 llamada(s), 0 caché, US$ 0.0.
Bloqueantes del crudo nuevo antes de la ronda única: 4 → después 3; PARADA del guion: True.

- (crudo) cap 3 beat 4 (a): entre comillas, pero no es una cita del pool: «Aterrizamos en una pista en medio de una tierra muy muy roja…»
- (crudo) cap 3 beat 4 (d): fuera del caso (descartado en el pool): El avión era pequeño, de hélices, y se movía muchísimo. Aterrizamos en una pista
- (crudo) cap 3 beat 5 (d): fuera del caso (descartado en el pool): Defensor del empleador no identificado
- (crudo) cap 6 beat 11 (a): entre comillas, pero no es una cita del pool: «Hay hijos de funcionarios que trabajaban en el pueblo, como …»

### 2. La promesa (escaleta) y la oración 2 del cap 1 (guion)

| | F54 | F55 |
|---|---|---|
| promesa_gancho | Daniel Écija vivió diez meses en Wittenoom. Murió de eso casi treinta años después, en Madrid. Esta es la historia de quién sabía, desde mil novecientos cuarenta y ocho, lo que hacía ese polvo, y de por qué tres millones de toneladas siguen donde las dejaron. | Un minero español vivió diez meses en un pueblo construido con polvo de asbesto azul y tardó casi treinta años en morir de eso; el pueblo ya no existe en los mapas, pero tres millones de toneladas de relaves siguen donde las dejaron. |
| oraciones de la promesa | 3 | 1 (métrica `promesa_oraciones`: 1) |
| oración 2 del cap 1 | Vivió diez meses en el pueblo donde le tomaron esa foto y murió de esos diez meses casi treinta años después, en Madrid; había gente con cargo y con firma que sabía desde mil novecientos cuarenta y ocho lo que hacía ese polvo, y más de tres millones de toneladas siguen donde las dejaron. | Ese pie va a cerrar; lo que respira mientras espera que cierre va a tardar casi treinta años en matarlo, y lo va a alcanzar a miles de kilómetros de aquí. |

### Los dos cap 1 enteros

| F54 | F55 |
|---|---|
| Un hombre joven posa de pie para un retrato, con un pie envuelto en vendas. Vivió diez meses en el pueblo donde le tomaron esa foto y murió de esos diez meses casi treinta años después, en Madrid; había gente con cargo y con firma que sabía desde mil novecientos cuarenta y ocho lo que hacía ese polvo, y más de tres millones de toneladas siguen donde las dejaron. La foto es sepia, como las demás que hay sobre la mesa. Una mujer mayor las ordena, una por una. Cuenta que a su marido le cayó un trozo de amianto en el pie y que la herida no cerraba; por eso la venda. «Me pegué a mi marido, como una niña pequeña», dice la mujer que ordena las fotos. El hombre del pie vendado se llamaba Daniel Écija, minero emigrante español. Wittenoom, Australia Occidental, mil novecientos sesenta y dos. Para entender ese retrato hay que volver a Madrid, a un baile, un año antes de que lo tomaran. | Un hombre joven posa para un retrato con el pie vendado. Ese pie va a cerrar; lo que respira mientras espera que cierre va a tardar casi treinta años en matarlo, y lo va a alcanzar a miles de kilómetros de aquí. La foto es en blanco y negro. La familia que la guarda cuenta que le cayó encima un trozo de amianto y que la herida no cerraba. Una herida hecha por un pedazo de mineral que no cierra. El hombre se llama Daniel Écija, es minero, y llegó de Madrid hace unos meses. Wittenoom, Australia Occidental, 1963.  Esa foto se tomó en un pueblo que hoy no figura en ningún mapa. Arrancaron las señales de la carretera y borraron el nombre. Lo que sobró de la mina, en cambio, sigue donde lo dejaron. Pero antes de que lo borraran, alguien tuvo que llevar a ese hombre hasta allí. Dos años antes de la foto, en Madrid, hubo un baile. |

### 3. Loops declarados con sus pagos (escaleta F55), leídos con `evidence.regla_dicho`

- **Loop 1** (L1): «¿Qué le hizo Wittenoom a Daniel en diez meses, si el pueblo ya estaba a miles de kilómetros cuando lo alcanzó?» — se abre en el beat 1 (cap 1, D85: A2) · se paga en el beat 10 (cap 5, T64: ancla)
- **Loop 2** (L2): «¿Quién sabía que el polvo mataba, desde cuándo, y quién va a limpiar lo que quedó?» — se abre en el beat 5 (cap 3, D92: A1) · se paga en el beat 13 (cap 7, T98: ancla)

Beats con `paga` (2):
- beat 10 (cap 5, T64: ancla) paga la pregunta del beat 1: «¿Por qué una herida hecha por un pedazo de mineral no cierra? ¿Qué hay en ese polvo?»
- beat 13 (cap 7, T98: ancla) paga la pregunta del beat 5: «Si en 1944 y 1948 ya estaba escrito, ¿quién decidió seguir?»

`recuerda_loop`: beat 6 · «Un año después de que McNulty escribiera ese primer caso, un recién casado de Madrid se bajaba de un avión en esa misma pista de polvo.»

### 4. Los 7 títulos

| cap | F54 | F55 |
|---|---|---|
| 1 | La herida que no cerró | Herida que no cierra |
| 2 | Promesas y polvo | Un viaje incierto |
| 3 | Peligro silenciado | El aire que respiran |
| 4 | El polvo lo cubría todo | Infancia entre fibras |
| 5 | La factura del tiempo | Un mal oculto |
| 6 | Un pueblo, polvo eterno | El rastro persiste |
| 7 | El costo sin fin | La herida abierta |

### 5. Medida de retención por código (`lab/hyperframes/f54/medida_retencion.py`): F54 | F55

| ingrediente | viejo | nuevo |
|---|---|---|
| segundos hasta la primera apuesta | 550.0 s (cap 5, loop principal (D89)) | 545.4 s (cap 5, loop principal (T64)) |
| loops abiertos / pagados | 2 declarado(s) · loop L1 (D89): pagado; loop L2 (D21): pagado, en la primera oración del cap; beat 5 paga (D21): pagado, en la primera oración del cap; beat 9 paga (D89): pagado; beat 11 paga (D10): NO pagado; beat 12 paga (T92): pagado | 2 declarado(s) · loop L1 (T64): pagado; loop L2 (T98): pagado; beat 10 paga (T64): pagado; beat 13 paga (T98): pagado |
| re-gancho | sí (cap 3, min 5.33, parecido 1.0) | declarado pero no dicho (cap 3, min 3.97, parecido 0.36) |
| el cierre vuelve a la imagen del gancho | sí (Q24 en el cap 7) | sí (T98 en el cap 7) |

| cap | palabras v | n | años v | n | datos/min v | n |
|---|---|---|---|---|---|---|
| 1 | 168 | 161 | 2 | 1 | 0.9 | 0.9 |
| 2 | 263 | 220 | 3 | 4 | 3.3 | 3.9 |
| 3 | 368 | 433 | 11 | 5 | 2.0 | 2.0 |
| 4 | 335 | 322 | 2 | 4 | 1.7 | 2.7 |
| 5 | 252 | 292 | 5 | 7 | 4.0 | 3.9 |
| 6 | 278 | 297 | 7 | 4 | 1.6 | 3.4 |
| 7 | 249 | 210 | 5 | 6 | 3.5 | 2.7 |


### 6. `grep` de los 8 ids descartados en `_steps/<topic>/` regenerado

| archivo | apariciones fuera de `_descartados` | dónde |
|---|---|---|
| (ninguno) | 0 | — |

**Total fuera de `_descartados` y de `ficha_caso.json`: 0** (debe dar 0). `ficha_caso.json` en disco sigue con sus 36 apariciones (no se reescribe; `load` las remapea en memoria).


### 7. El papel (01e_pantalla.md, F55)

# Guion de pantalla en papel — 123bbb64-9fca-4395-8bf4-57d60e219ef1

`m01e_pantalla` m01e-6 (md5 del prompt `3b98aef1d8595124967ac7a85b75bab7`) · claude-sonnet-5-5 medium · 3 intento(s) · US$ 0.6279 · tokens de entrada 51320

Segundos por palabra 0.34 (mediana de 347 oraciones de 16 caps del narrador N9Z5MLTIaHFLflaLtbDi) · tope US$ 1.0 (respaldo (el perfil no trae costos.m01e_tope_usd)) · intento 1: in 51320 · out 23746 · US$ 0.3401 · intento 2: in 59781 · out 4826 · US$ 0.1678 · intento 3: in 58827 · out 232 · US$ 0.1200

Totales: 13 fichas · 6 sellos · 3 relojes · 64 descartados

## ch01 — Herida que no cierra

- beat 1 · gancho · PICO · ficha **D79** [normal] «LOS MUERTOS DE WITTENOOM · Más de 2000 mineros y vecinos murieron» en [7] sobre «pueblo» (62/71 car.) · respaldo: «Más de 2000 antiguos trabajadores de la mina y residentes de Wittenoom han muerto por enfermedades relacionadas con el asbesto.» · año — / relato 1963 · juzgado por el autor: otro hecho {'no_dicho': ['2000'], 'spoiler': ['2000']} · aporta: Pone la escala de muertes del pueblo, que la voz no dice en ningún momento del video. · sello **SILENCIO** en [8]
- relojes: —

## ch02 — Un viaje incierto

- beat 2 · planteo · ficha **Q25** [cita] «LO QUE DEJABAN · En España no teníamos nada» — María Bernal (autor: modelo) en [2] sobre «confiaba» (57/90 car.) · respaldo: «En España no teníamos nada, ninguno de los dos.» · año — / relato 1961 · aporta: Explica por qué se fueron: la pareja no tenía nada en España. La voz solo cita la otra parte de lo que dice ella. · sello —
- beat 3 · planteo · PICO · ficha **D105** [normal] «SU ÚNICO SUPERMERCADO · Un camión con víveres cada 15 días» en [17] sobre «tierra» (55/71 car.) · respaldo: «Un camión traía suministros al único supermercado de Wittenoom cada 15 días.» · año — / relato 1962 · aporta: Muestra el aislamiento del destino con un detalle cotidiano que la voz no cuenta. · sello —
- relojes: 16 SEP 1961 en [0], 20 SEP 1962 en [4]

## ch03 — El aire que respiran

- beat 4 · planteo · ficha **D82** [normal] «AISLADO · A unos 1.400 kilómetros de Perth» en [1] sobre «Pilbara» (39/40 car.) · respaldo: «a unos 1.400 kilómetros de Perth» · año — / relato 1962 · aporta: Da la distancia a la ciudad más cercana. La voz solo nombra el desierto. · sello —
- beat 5 · escalada · PICO · ficha **D01** [normal] «LO QUE SE SACÓ DE LA TIERRA · Más de 150.000 toneladas de asbesto» en [12] sobre «mina» (62/90 car.) · respaldo: «Se extrajeron comercialmente aproximadamente 150.000 toneladas de asbesto de tres minas entre 1937 y 1966.» · año 1937 / relato 1943 · aporta: Pone en cifra cuánto asbesto salió de las minas; la voz no da ninguna cantidad de producción en este capítulo. · sello **AVISO** en [16]
- beat 6 · giro · ficha **T25** [normal] «LA CIENCIA YA LO SABÍA · En 1955 ya se sabía que daba cáncer» en [26] sobre «polvo» (57/90 car.) · respaldo: «Investigadores descubrieron los peligros cancerígenos del asbesto. (fecha 1955)» · año 1955 / relato 1957 · aporta: Pone fecha a cuándo la ciencia advirtió del cáncer, antes de recortar el pago por el polvo. La voz no lo dice. · sello —
- relojes: —

## ch04 — Infancia entre fibras

- beat 7 · escalada · PICO · ficha **Q19** [cita] «SIN AVISO · Nadie nos avisó de nada» — Víctor Calvo (autor: modelo) en [13] sobre «miedo» (49/51 car.) · respaldo: «Nadie nos avisó de nada.» · año — / relato 1962 · aporta: La frase final del testimonio de Calvo, que la voz omite: a los chicos nadie les advirtió. · sello —
- beat 8 · giro · ficha **D102** [normal] «AQUEL BEBÉ, HOY · 63 años y productor de televisión» en [17] sobre «Daniel» (48/51 car.) · respaldo: «tiene 63 años y es un conocido productor de televisión en España.» · año — / relato 1963 · aporta: Cuenta qué fue del bebé que nació en el pueblo. La voz no lo dice. · sello **CALMA** en [22]
- relojes: 7 JUL 1963 en [19]

## ch05 — Un mal oculto

- beat 9 · escalada · ficha **D51** [normal] «LO QUE SACÓ LA MINA · 131.000 toneladas de amianto azul» en [1] sobre «cierre» (52/71 car.) · respaldo: «La mina de Wittenoom produjo 131.000 toneladas de crocidolita, de las cuales más de 100.000 toneladas fueron exportadas.» · año 1966 / relato 1966 · aporta: Pone en cifra lo que produjo la mina hasta el cierre. La voz solo habla de las razones del anuncio. · sello —
- beat 10 · pico · PICO · ficha **D23** [papel] «YA HABÍAN MUERTO, 1989 · Más de 500 mineros y vecinos» en [12] sobre «mesotelioma» (50/76 car.) · respaldo: «Para 1989, más de 500 antiguos trabajadores y residentes de Wittenoom habían muerto por infecciones relacionadas con el asbesto.» · año 1989 / relato 1991 · aporta: Muestra que Daniel no fue el primero: ya había cientos de muertos antes de su diagnóstico. · sello **MEMORIA** en [11]
- relojes: —

## ch06 — El rastro persiste

- beat 11 · respiro · ficha **D121** [normal] «LOS QUE PASARON · Unas 7000 trabajaron para ABA» en [0] sobre «pasaron» (44/51 car.) · respaldo: «Aproximadamente 7000 personas trabajaron para ABA en los 23 años que la compañía extrajo y molió asbesto.» · año — / relato 1962 · aporta: Da la cifra de personas que pasaron por la mina, sin contar a sus familias. · sello —
- beat 12 · revelacion · PICO · ficha **D40** [normal] «TAMAÑO DE LA ZONA · 46.840 hectáreas» en [13] sobre «zona» (33/90 car.) · respaldo: «El Área de Gestión del Asbesto de Wittenoom (WAMA) cubre una superficie de 46.840 hectáreas.» · año — / relato 2006 · aporta: Da la superficie oficial de la zona declarada no apta. La voz no la dice. · sello **AMENAZA** en [15]
- relojes: —

## ch07 — La herida abierta

- beat 13 · cierre · PICO · ficha **D61** [papel] «RECONOCIDO POR EL GOBIERNO · 2023: la contaminación se extendió» en [8] sobre «problema» (60/76 car.) · respaldo: «Un Subcomité de Wittenoom determinó en 2023 que todos los informes sobre el alcance de la contaminación ya no son aplicables y que la contaminación se ha extendido.» · año 2023 / relato 2026 · aporta: Un organismo oficial admitió en 2023 que la contaminación creció y que los estudios quedaron viejos. La voz no lo dice. · sello **RABIA** en [11]
- relojes: —

## Lo que cayó

- (nada)

## Reintento: los motivos que se le mandaron al autor

- D131 (ch03 beat 6) «LA OFICINA DE SALUD LABORAL · Se creó en 1959 con una sola persona»: fecha_relato: D131 es de 1959 y en la oración [27] el relato va por 1957 (el último año que dijo la voz); ni la oración ni sus vecinas lo sitúan después
- D94 (ch05 beat 9) «LO QUE PAGÓ LA EMPRESA · 18,3 millones de dólares australianos a 200 afectados»: fecha_relato: D94 es de 1989 y en la oración [8] el relato va por 1988 (el último año que dijo la voz); ni la oración ni sus vecinas lo sitúan después
- D79 (ch01 beat 1, oración [7]) «LOS MUERTOS DE WITTENOOM · Más de 2000 mineros y vecinos murieron»: la voz dice «2000» en ch06 [7] («Melita Markey sigue contando lo que el gobierno dejó de contar en dos mil; otras estimaciones, dice, hablan de más de cuatro mil, y la cifra sube.»); ¿es el mismo hecho? si no, mantenelo
- D79 (ch01 beat 1, oración [7]) «LOS MUERTOS DE WITTENOOM · Más de 2000 mineros y vecinos murieron»: la voz dice «2000» en una oración posterior en ch06 [7] («Melita Markey sigue contando lo que el gobierno dejó de contar en dos mil; otras estimaciones, dice, hablan de más de cuatro mil, y la cifra sube.»); ¿es el mismo hecho? si no, mantenelo
- D135 (ch03 beat 5, oración [13]) «QUIÉN DIRIGÍA LA MINA · El Estado los llamó «aficionados»»: la voz dice «Estado» en la oración ancla o en una vecina en ch03 [13] («En 1944, el inspector de minas y el ingeniero de minas Adjunto del Estado informaron sobre el problema del polvo.»); ¿es el mismo hecho? si no, mantenelo
- T13: dijiste que la voz lo dice («La voz dice los diagnósticos de 1946.»); la voz de ch03 no dice «Wittenoom» («Se diagnosticó un primer caso de asbestosis en Wittenoom. (fecha 1946)»): vuelve a ser candidato
- D21: dijiste que la voz lo dice («La voz dice que la producción subió en 1961.»); la voz de ch03 no dice «Wittenoom» («La producción minera en Wittenoom se incrementó en 1961 a pesar de la evidencia de los riesgos.»): vuelve a ser candidato
- T27: dijiste que la voz lo dice («La voz cuenta el recorte del suplemento.»); la voz de ch03 no dice «3» ni «4» («El subsidio por polvo se redujo a 3 o 4 peniques y se restringió a ciertas áreas, tras la instalación de equipo para reducir el polvo. (fecha 1957)»): vuelve a ser candidato
- T35: dijiste que la voz lo dice («La voz cuenta el caso de mesotelioma de McNulty en 1962.»); la voz de ch03 no dice «Sudáfrica» ni «Wittenoom» («Se reporta el primer caso de mesotelioma fuera de Sudáfrica, en un ex-trabajador de la planta de molienda de Wittenoom. (fecha 1962)»): vuelve a ser candidato
- D95: dijiste que la voz lo dice («La voz dice los mil quinientos millones.»); la voz de ch07 no dice «1.500» («El pueblo aborigen banjima reclama 1.500 millones de dólares australianos al Ejecutivo por la contaminación.»): vuelve a ser candidato
- el beat 5 de ch03 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D01 («150.000 toneladas de asbesto comercial entre 1937 y 1966: cifra técnica de contexto.»)
- el beat 9 de ch05 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D51 («Producción atribuida por Vernon a la mina de Wittenoom, 131.000 toneladas, en el anuncio del cierre.»)
- el beat 12 de ch06 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D40 («Superficie oficial de WAMA: 46.840 hectáreas; cifra administrativa con versiones en disputa, mejor leída que dicha.»)
- el beat 13 de ch07 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D61 («Reconocimiento oficial de 2023 de que los estudios sobre la extensión quedaron desactualizados; va como documento fechado.»)

### Preguntas y respuesta del autor

- D79 {'no_dicho': ['2000'], 'spoiler': ['2000']}: la mantuvo en ch01 beat 1 [7]: otro hecho
- D135 {'no_dicho': ['Estado', 'Minas']}: la sacó o la cambió (el mismo hecho, o eligió otra)

### Reintento parcial: 2 vuelta(s)

#### Vuelta 1 · US$ 0.1678

- beats que podía cambiar: ch01 beat 1, ch03 beat 5, ch03 beat 6, ch05 beat 9, ch06 beat 12, ch07 beat 13
- motivos:
  - D131 (ch03 beat 6) «LA OFICINA DE SALUD LABORAL · Se creó en 1959 con una sola persona»: fecha_relato: D131 es de 1959 y en la oración [27] el relato va por 1957 (el último año que dijo la voz); ni la oración ni sus vecinas lo sitúan después
  - D94 (ch05 beat 9) «LO QUE PAGÓ LA EMPRESA · 18,3 millones de dólares australianos a 200 afectados»: fecha_relato: D94 es de 1989 y en la oración [8] el relato va por 1988 (el último año que dijo la voz); ni la oración ni sus vecinas lo sitúan después
  - D79 (ch01 beat 1, oración [7]) «LOS MUERTOS DE WITTENOOM · Más de 2000 mineros y vecinos murieron»: la voz dice «2000» en ch06 [7] («Melita Markey sigue contando lo que el gobierno dejó de contar en dos mil; otras estimaciones, dice, hablan de más de cuatro mil, y la cifra sube.»); ¿es el mismo hecho? si no, mantenelo
  - D79 (ch01 beat 1, oración [7]) «LOS MUERTOS DE WITTENOOM · Más de 2000 mineros y vecinos murieron»: la voz dice «2000» en una oración posterior en ch06 [7] («Melita Markey sigue contando lo que el gobierno dejó de contar en dos mil; otras estimaciones, dice, hablan de más de cuatro mil, y la cifra sube.»); ¿es el mismo hecho? si no, mantenelo
  - D135 (ch03 beat 5, oración [13]) «QUIÉN DIRIGÍA LA MINA · El Estado los llamó «aficionados»»: la voz dice «Estado» en la oración ancla o en una vecina en ch03 [13] («En 1944, el inspector de minas y el ingeniero de minas Adjunto del Estado informaron sobre el problema del polvo.»); ¿es el mismo hecho? si no, mantenelo
  - T13: dijiste que la voz lo dice («La voz dice los diagnósticos de 1946.»); la voz de ch03 no dice «Wittenoom» («Se diagnosticó un primer caso de asbestosis en Wittenoom. (fecha 1946)»): vuelve a ser candidato
  - D21: dijiste que la voz lo dice («La voz dice que la producción subió en 1961.»); la voz de ch03 no dice «Wittenoom» («La producción minera en Wittenoom se incrementó en 1961 a pesar de la evidencia de los riesgos.»): vuelve a ser candidato
  - T27: dijiste que la voz lo dice («La voz cuenta el recorte del suplemento.»); la voz de ch03 no dice «3» ni «4» («El subsidio por polvo se redujo a 3 o 4 peniques y se restringió a ciertas áreas, tras la instalación de equipo para reducir el polvo. (fecha 1957)»): vuelve a ser candidato
  - T35: dijiste que la voz lo dice («La voz cuenta el caso de mesotelioma de McNulty en 1962.»); la voz de ch03 no dice «Sudáfrica» ni «Wittenoom» («Se reporta el primer caso de mesotelioma fuera de Sudáfrica, en un ex-trabajador de la planta de molienda de Wittenoom. (fecha 1962)»): vuelve a ser candidato
  - D95: dijiste que la voz lo dice («La voz dice los mil quinientos millones.»); la voz de ch07 no dice «1.500» («El pueblo aborigen banjima reclama 1.500 millones de dólares australianos al Ejecutivo por la contaminación.»): vuelve a ser candidato
  - el beat 5 de ch03 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D01 («150.000 toneladas de asbesto comercial entre 1937 y 1966: cifra técnica de contexto.»)
  - el beat 9 de ch05 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D51 («Producción atribuida por Vernon a la mina de Wittenoom, 131.000 toneladas, en el anuncio del cierre.»)
  - el beat 12 de ch06 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D40 («Superficie oficial de WAMA: 46.840 hectáreas; cifra administrativa con versiones en disputa, mejor leída que dicha.»)
  - el beat 13 de ch07 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D61 («Reconocimiento oficial de 2023 de que los estudios sobre la extensión quedaron desactualizados; va como documento fechado.»)
- aplicados: ch03 beat 5 (ficha), ch03 beat 6 (ficha), ch05 beat 9 (ficha), ch06 beat 12 (ficha), ch07 beat 13 (ficha)

#### Vuelta 2 · US$ 0.1200

- beats que podía cambiar: ch03 beat 5
- motivos:
  - D135 (ch03 beat 5, oración [13]) «QUIÉN DIRIGÍA LA MINA · El Departamento de Minas los llamó «aficionados»»: la voz dice «Minas» en la oración ancla o en una vecina en ch03 [13] («En 1944, el inspector de minas y el ingeniero de minas Adjunto del Estado informaron sobre el problema del polvo.»); ¿es el mismo hecho? si no, mantenelo
  - T13: dijiste que la voz lo dice («La voz dice los diagnósticos de 1946.»); la voz de ch03 no dice «Wittenoom» («Se diagnosticó un primer caso de asbestosis en Wittenoom. (fecha 1946)»): vuelve a ser candidato
  - D21: dijiste que la voz lo dice («La voz dice que la producción subió en 1961.»); la voz de ch03 no dice «Wittenoom» («La producción minera en Wittenoom se incrementó en 1961 a pesar de la evidencia de los riesgos.»): vuelve a ser candidato
  - T27: dijiste que la voz lo dice («La voz cuenta el recorte del suplemento.»); la voz de ch03 no dice «3» ni «4» («El subsidio por polvo se redujo a 3 o 4 peniques y se restringió a ciertas áreas, tras la instalación de equipo para reducir el polvo. (fecha 1957)»): vuelve a ser candidato
  - T35: dijiste que la voz lo dice («La voz cuenta el caso de mesotelioma de McNulty en 1962.»); la voz de ch03 no dice «Sudáfrica» ni «Wittenoom» («Se reporta el primer caso de mesotelioma fuera de Sudáfrica, en un ex-trabajador de la planta de molienda de Wittenoom. (fecha 1962)»): vuelve a ser candidato
  - D95: dijiste que la voz lo dice («La voz dice los mil quinientos millones.»); la voz de ch07 no dice «1.500» («El pueblo aborigen banjima reclama 1.500 millones de dólares australianos al Ejecutivo por la contaminación.»): vuelve a ser candidato
  - el beat 5 de ch03 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D01 («150.000 toneladas de asbesto comercial entre 1937 y 1966: cifra técnica de contexto.»)
- aplicados: ch03 beat 5 (ficha)

### Motivos sin beat (no hubo reintento)

- T13: dijiste que la voz lo dice («La voz dice los diagnósticos de 1946.»); la voz de ch03 no dice «Wittenoom» («Se diagnosticó un primer caso de asbestosis en Wittenoom. (fecha 1946)»): vuelve a ser candidato
- D21: dijiste que la voz lo dice («La voz dice que la producción subió en 1961.»); la voz de ch03 no dice «Wittenoom» («La producción minera en Wittenoom se incrementó en 1961 a pesar de la evidencia de los riesgos.»): vuelve a ser candidato
- T27: dijiste que la voz lo dice («La voz cuenta el recorte del suplemento.»); la voz de ch03 no dice «3» ni «4» («El subsidio por polvo se redujo a 3 o 4 peniques y se restringió a ciertas áreas, tras la instalación de equipo para reducir el polvo. (fecha 1957)»): vuelve a ser candidato
- T35: dijiste que la voz lo dice («La voz cuenta el caso de mesotelioma de McNulty en 1962.»); la voz de ch03 no dice «Sudáfrica» ni «Wittenoom» («Se reporta el primer caso de mesotelioma fuera de Sudáfrica, en un ex-trabajador de la planta de molienda de Wittenoom. (fecha 1962)»): vuelve a ser candidato
- D95: dijiste que la voz lo dice («La voz dice los mil quinientos millones.»); la voz de ch07 no dice «1.500» («El pueblo aborigen banjima reclama 1.500 millones de dólares australianos al Ejecutivo por la contaminación.»): vuelve a ser candidato

## Cierre del reintento

- cerró por: **sin beat** (después de 2 vueltas)
- cortado al cerrar, sin preguntarle al autor: (nada)

## Descartados por el modelo

- D85 [otro]: Es el dato central del gancho según la escaleta, pero no está en el archivo. Lo reemplacé por D79.
- T34 [voz_lo_dice]: La voz cuenta el baile y su fecha en la oración 0 del capítulo 2.
- T38 [voz_lo_dice]: La fecha de partida (24 de septiembre de 1962) se deduce de «cuatro días después» de la boda. Además el respaldo está en formato ISO.
- Q14 [voz_lo_dice]: La voz cita el viaje de Calvo casi completo.
- D83 [voz_lo_dice]: La voz dice «cerca de ocho mil españoles».
- T36 [voz_lo_dice]: La voz dice la llegada de los De Juan en agosto de 1962.
- T24 [voz_lo_dice]: La voz dice los viajes de reclutamiento desde 1950.
- Q13 [voz_lo_dice]: La voz resume que se hicieron íntimos amigos.
- Q27 [voz_lo_dice]: La voz reproduce la cita de Calvo sobre el avión y la pista.
- Q44 [voz_lo_dice]: La voz cita a un antiguo trabajador sobre los relaves.
- D92 [voz_lo_dice]: La voz dice que Saint advirtió por escrito en 1948.
- Q45 [voz_lo_dice]: La voz cita la carta de Saint.
- Q53 [voz_lo_dice]: La voz cita al defensor del empleador.
- Q46 [voz_lo_dice]: La voz cita el «alborotador».
- D19 [voz_lo_dice]: La voz dice el informe de 1944.
- T13 [voz_lo_dice]: La voz dice los diagnósticos de 1946. — **falso: la voz no dice ['Wittenoom']**
- T06 [voz_lo_dice]: La voz dice el traspaso de 1943.
- D21 [voz_lo_dice]: La voz dice que la producción subió en 1961. — **falso: la voz no dice ['Wittenoom']**
- Q54 [voz_lo_dice]: La voz cita el acta de la Junta de Referencia.
- T27 [voz_lo_dice]: La voz cuenta el recorte del suplemento. — **falso: la voz no dice ['3', '4']**
- T35 [voz_lo_dice]: La voz cuenta el caso de mesotelioma de McNulty en 1962. — **falso: la voz no dice ['Sudáfrica', 'Wittenoom']**
- Q49 [voz_lo_dice]: La voz cita a McNulty.
- D130 [voz_lo_dice]: Es el mismo hecho que cuenta la voz sobre McNulty en 1962.
- D115 [otro]: Encaja con la oración de McNulty en 1962, que está en el capítulo 4. Elegí un ancla dentro del capítulo 3 para el beat 6, así que no lo usé.
- Q16 [voz_lo_dice]: La voz cuenta la explosión del primer día.
- D104 [voz_lo_dice]: La voz dice las jornadas de dieciséis horas.
- T41 [voz_lo_dice]: La voz dice el bautizo y la partida.
- T40 [voz_lo_dice]: La voz cuenta el nacimiento.
- T39 [voz_lo_dice]: La voz cuenta el nacimiento de John Patrick.
- D87 [voz_lo_dice]: La voz dice «unos diez meses».
- T49 [voz_lo_dice]: La voz cuenta el cierre por costos.
- T47 [voz_lo_dice]: La voz cuenta el regreso a Madrid.
- D88 [voz_lo_dice]: La voz cuenta los dos años y medio de los De Juan.
- T51 [voz_lo_dice]: La voz cuenta el regreso de los De Juan en 1971.
- D27 [voz_lo_dice]: La voz cuenta la reducción del pueblo en 1978.
- D93 [voz_lo_dice]: La voz cita el fallo del juez de 1988.
- T56 [voz_lo_dice]: La voz cuenta la sociedad de 1979.
- D51 [otro]: Válido para el beat 9, pero D94 (la indemnización) suma más.
- T64 [voz_lo_dice]: La voz cuenta el diagnóstico de 1991.
- D89 [voz_lo_dice]: La voz cuenta la muerte nueve meses después.
- Q35 [voz_lo_dice]: La voz cita al hijo.
- D110 [otro]: Es una proyección técnica difícil de leer en 3 segundos. D23 se entiende solo.
- Q24 [voz_lo_dice]: La voz cita al policía.
- Q21 [voz_lo_dice]: La voz cita a Mercedes de Juan.
- Q33 [voz_lo_dice]: La voz cuenta lo de Markey.
- D90 [spoiler]: La cifra de más de 4000 muertes la cuenta la voz después, en el capítulo 6.
- D64 [otro]: Buena comparación con el estadio, pero en el beat pico 12 priorizé el dato central T80.
- D02 [voz_lo_dice]: La voz dice los más de tres millones de toneladas de relaves.
- Q07 [voz_lo_dice]: La voz cita al gobierno sobre el «período oscuro».
- Q03 [voz_lo_dice]: La voz cita la declaración de «no apta».
- D10 [otro]: No existe en el archivo.
- T90 [voz_lo_dice]: La voz dice las fibras en canales de arroyos.
- D59 [voz_lo_dice]: La voz cuenta el documento de 2016.
- T98 [voz_lo_dice]: La voz cuenta el proceso de Gordon Legal en 2026.
- Q10 [voz_lo_dice]: La voz cita a Parker.
- T92 [voz_lo_dice]: La voz cuenta la visita de Orellana.
- T96 [voz_lo_dice]: La voz dice la muerte de Parker.
- D95 [voz_lo_dice]: La voz dice los mil quinientos millones. — **falso: la voz no dice ['1.500']**
- Q34 [voz_lo_dice]: La voz cita al gobierno sobre el «grave problema».
- D70 [otro]: No existe en el archivo.
- D03 [otro]: No existe en el archivo.
- D129 [otro]: No existe en el archivo.
- D20 [otro]: No existe en el archivo.
- D86 [repetido]: Se parece a D121, que ya usé en el beat 11.


## Lo que queda abierto (Parte D)
1. **Dedupe vs. jueces (a)/(d):** 2 frenos falsos sobre el texto de una cita duplicada (Q15); arreglo general en handoff aparte (saltar duplicadas en `contamination`; `false_quotes`/`ficha_caso.load` con el texto de la cita que quedó).
2. La (d) previa del cap 3 («Defensor del empleador no identificado») sigue (pedido de Omar: no tocar).
3. Re-gancho declarado y no dicho por el guionista (parecido 0,36); nada lo chequea.
4. Ningún pago en la primera oración del cap salvo el de L2 (cap 3): `<estructura>` §2 se cumple a medias.
5. El re-gancho y el `recuerda_loop` quedan en el beat 6 (último del cap 3) como manda el validador; la oración no apareció en la voz.
6. `person_stats` del pool sin recalcular tras el dedupe; `fase1_5` sin el log del remapeo de la ficha.
7. El guion queda en **PARADA del guion** (3 bloqueantes) y PARADA del papel: nada pasa a voz ni fotos sin Omar.

**PARADA D.** Omar y el analista califican.

## Veredicto de revisor-handoff (Parte D, íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Invocación del handoff, llegó a 01e, sin fotos ni voz | OK | d_run.log: "Modo: 1 topic… desde m01a", pasos 01a/01b/01d/m01e, exit 0. 0 menciones a fotos, voz, m02 o m03. 01e_pantalla.md existe. `fase1_5.py` no fue tocado. |
| 2 | Gasto US$ 3,93 | OK | d_run.log: TOTAL US$ 3.9277. Sumé las entradas de data/cost_history.json de 20:21 a 20:40 del topic y dio 3.9277, igual al log. |
| 3 | SALIDA_D.md completa | OK | §1 tabla A/B por cap (F54 y F55, con bloqueantes de ambos). §2 promesa y oración 2. §3 loops con regla_dicho. §4 los 7 títulos. §5 medida de retención. §6 grep. §7 papel. Recalculé el grep de los 8 ids (Q12, Q15, Q20, Q23, Q26, Q28, Q29, Q30) en 01a_escaleta, 01a_skeleton, 01b_guionista_v4, 01b_narration, 01b_narracion_v3, 01e_pantalla (md, json y raw): 0 en todos. Fuera de `_descartados` hay 0 en las copias del pool: `00_pool_v3.json`, `01_facts_sources.json` y `topics_db.json`. Los ids siguen solo en ficha_caso.json, FICHA md, `ficha_respuesta_cruda`, los PDF y `_descartados`, que es lo permitido. |
| 4 | Diagnóstico de los 3 bloqueantes | OK | `01b_guionista_v4.json` `reparacion.bloqueantes_despues` trae (a) «Aterrizamos en una pista…», (d) «El avión era pequeño…» y (d) «Defensor del empleador». En `00_pool_v3.json` `_descartados`, Q15 figura como duplicada de Q27 (0,90) y el texto de Q27 coincide con la frase. La (d) del defensor es la previa de F54. `metricas.verificador` = {llamadas 0, cache 0, usd 0.0}. F55_REPORT.md (~l.677) dice que Sonnet confirmó 0. |
| 5 | Promesa de 1 oración y loops pagados | OK | SALIDA_D §2: `promesa_oraciones` 1, y el texto de la promesa es una sola oración. §3: L1 (T64) y L2 (T98) pagados, y también los pagos de los beats 10 y 13. |
| 6 | Remapeo del digest declarado, 3 copias limpias | OK | `dedupe_pool.py:63-70` remapea todo lo del pool que no sea `citas` ni `_descartados`, en las 3 copias. Está declarado en el reporte (Decisión 2). Recalculado: 0 fuera de `_descartados` en las 3 copias. |
| 7 | Nada fuera de alcance | OK | `git diff --name-only HEAD~2 HEAD` toca solo lab/hyperframes/f55/*, ESTADO_SESION.md y F55_REPORT. No toca script_engine/, researcher_steps/ ni `fase1_5.py`. |
| 8 | "Lo que queda abierto" incluye el hallazgo dedupe vs. jueces (a)/(d) | OK | F55_REPORT.md:945, ítem 1 de "Lo que queda abierto (Parte D)". El hallazgo está además desarrollado en el reporte, con opciones y sin tocar los jueces (Decisión 3). |

`python -m pytest -q test_module_f55.py`: 29 passed, 1 skipped.

Observaciones, ninguna bloqueante:
- El guion nuevo queda en PARADA (3 bloqueantes). Dos son falsos del dedupe y uno es la (d) previa. Está declarado, pero la Parte D no entrega un guion limpio.
- El commit "lab" modificó también SALIDA_B.md, que es de una parte ya revisada: borró una línea de log duplicada. Es trivial, pero no figura entre los cambios que el mensaje de commit anuncia.
- La corrida usó el digest viejo del pool, antes de corregirlo en `dedupe_pool.py`. El reporte lo declara y el grep da 0 en lo regenerado, pero la escaleta se corrió con un pool que después se corrigió.
- Los datos regenerados (`data/scripts/_steps/…`, `topics_db.json`) no van en los commits. Las pruebas viven en `lab/.../f55/antes` y en los .md.

Fuera de alcance: ninguno.

Riesgos que el contrato no cubre: el guion que cita la versión de Q15 depende de que la ficha conserve los textos de las duplicadas, así que cualquier regeneración futura repite los dos frenos falsos hasta que se arregle el hallazgo. El verificador de Sonnet no se ejercitó en esta corrida (0 llamadas), de modo que su comportamiento con las duplicadas no está medido.

## Adenda de CC (Parte D)
- **SALIDA_B.md en el commit lab:** `dedupe_pool.py` regenera ese archivo cada vez que corre (D.0 y D lo corrieron); el cambio es una línea de log duplicada menos. Lo digo acá, ya que el mensaje del commit no lo nombra.
- **Digest viejo durante la corrida:** la escaleta v2 arma su prompt con la ficha, no con `pool["digest"]` (F16/F39), y lo regenerado dio 0 ids descartados; igual queda dicho que la corrección del digest llegó después de la corrida.
- **Verificador sin ejercitar en D:** en la Salida A sí se ejercitó (3 llamadas reales: D42, D21, D10) y en el test real; acá no hizo falta porque el cierre y los pagos tenían ancla.
- **El guion no queda limpio:** 2 frenos son del hallazgo dedupe vs. jueces (handoff aparte) y 1 es la (d) previa que Omar pidió no tocar.
