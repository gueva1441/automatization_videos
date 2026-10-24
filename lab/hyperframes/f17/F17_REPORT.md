# F17 — Columna vertebral · reporte corto (cerrado en PARADA 1)

2026-10-24 · rama `f11-guion-v4` (base `fceeee3`). **Cerrado por cambio de plan:** Omar pasó a Kyshtym/Mayak (F18). Ycuá queda en PARADA 1 para siempre: no se corrió escaleta ni guion de Ycuá ni nada de Orleans, y no se regenera más su columna. No hay `compara_f17.html` (no hubo escaleta ni guion que comparar).

## 1. Prompt
- `PROMPT_COLUMNA_v1.md`: md5 del archivo (en LF) `0e6490946a9cda10be16b308bd0eb51a`. SISTEMA extraído anclando en «\n## SISTEMA\n\n»: md5 `1408569c5c9de22ec406a10ba0cd9b13` (test byte-idéntico `test_module_f17.py::test_sistema_columna_byte_identico_al_archivo`; la tarea y el texto de «CÓMO SE USA LA COLUMNA» también, literales).
- Usuario de las corridas: v1 `2a3576acca599716b181e7a0136fd1b4`; con notas `0e6b212465a9080af166e8e813e58f98` (`prompt_ycua_f17_columna*.txt`).

## 2. Código
- `script_engine/m01a_columna.py` (nuevo, `f17-1`): Sol high, usuario = caso + ficha (la misma sección que la escaleta v2) + tarea literal. Chequeo determinista: 7 caps, humano y personas de cada cap existen en la ficha, ids existen. Si falla, UNA regeneración; después `ColumnaError` (PARADA). Métrica: personas con nombre. `notas=` (UNA regeneración con las notas de Omar dentro de la tarea).
- `m01a_escaleta`: `build_prompt_v2(columna=)` (columna antes de la ficha; `TAREA_COLUMNA` literal), `generate_escaleta(columna=None | dict | "generar")`, `prompt_version` `f17-1` solo con columna, los mismos 13 bloqueantes, `metricas_columna` (humano = columna, personas por cap ⊆ columna, cierre = «termina»). **Sin columna, byte-idéntica a F16**: test contra los md5 de los fixtures y de los prompts reales de Ycuá (`2d77969a…`) y Orleans (`d748efd2…`).
- `fase1_5`: con ficha v2, m01a = columna → escaleta; `--sin-columna` reproduce F16.
- `cost_tracker`: bajo pytest no escribe `data/cost_history.json`.
- Runner `lab/hyperframes/f17/f17_corridas.py` (freno de costo antes de cada llamada, `max_completion_tokens` 16 000 para la columna, una sola llamada que factura).

## 3. Tests
`test_module_f17.py` 27 verdes. Suite amplia 677 verdes + las 5 previas (3 `01b_pauses`, 2 `m03_merge_timing`). `test_v3_byte_identico` verde. (Un monkeypatch de `test_module_f10` se rompió por el kwarg nuevo; se arregló en `fase1_5` pasando `sin_columna` solo cuando es True.)

## 4. Corridas (Ycuá) y costo
| etapa | humano | personas con nombre | intentos | in / out / razonamiento | US$ |
|---|---|---|---|---|---|
| columna v1 (`COLUMNA_ycua_v1.md`) | Tatiana Gabaglio | 7 | 1 | 15 747 / 1 631 / 4 096 | 0.0888 |
| columna con las 3 notas de Omar (`COLUMNA_ycua.md`) | Liz Torres | 6 | 1 | 15 989 / 1 770 / 3 072 | 0.0804 |
| **tanda** | | | | | **0.1692** de 2.00 |

Notas de Omar en `data/scripts/_steps/f8s1-ycua-bolanos/columna_notas.md`. La regeneración con notas cumplió la nota 1 y en parte la 2 y la 3: falta la cita literal de Digna, y la «bola de fuego» no figura en la ficha.

## 5. Limpieza de `cost_history`
`data/cost_history.json` (ignorado por git): se sacaron los registros `t-f11b`. **Eran 33, por US$ 99.0** (el handoff decía 59 / US$ 100). 505 → 472; respaldo `data/cost_history.pre_f17.json`. Después de las dos columnas reales tiene 474. El tracker ya no registra cuando corre pytest (test `test_cost_tracker_no_escribe_el_historial_bajo_pytest`).

## 6. Veredictos del revisor-handoff (íntegros)

### 6.1 Hasta la PARADA 1 (código, tests, limpieza, columna v1)

VEREDICTO: CUMPLE CON OBSERVACIONES (alcance: hasta la Parada 1)

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | §1.1 paso `m01a_columna`: SISTEMA literal, usuario = caso + ficha completa + tarea literal, Sol high, `PROMPT_VERSION="f17-1"` | OK | `script_engine/m01a_columna.py:25,36-84,108-132`. Corrí el extractor anclado en «\n## SISTEMA\n\n» sobre `PROMPT_COLUMNA_v1.md` en LF: md5 `1408569c…`. Coincide con `costos_f17.json` y con el test byte-idéntico. `call_for(None)` es la ruta de Sol. |
| 2 | §1.1 chequeo determinista sin LLM: 7 caps, humano de la ficha, ids existen, personas de cada cap existen. Una regeneración y luego PARADA. Métrica de personas con nombre | OK | `m01a_columna.py:198-224` (`chequeo`), `:255-277` (regeneración y `ColumnaError`), `:227-236` (métrica). No hay reglas de estilo. |
| 3 | §1.1 se guardan `01a_columna.json` y `COLUMNA_<tema>.md` con la forma del ejemplo | OK | `_steps/f8s1-ycua-bolanos/01a_columna.json` (6990 B). `lab/hyperframes/f17/COLUMNA_ycua.md` (5198 B), con HUMANO / PICO / 7 filas QUÉ PASA·TERMINA / AFUERA. |
| 4 | §1.2 escaleta con columna: columna antes de la ficha, `TAREA_COLUMNA` literal, `f17-1` solo con columna, 13 bloqueantes sin cambios, 3 métricas informativas | OK | `m01a_escaleta.py` `build_prompt_v2(columna=)`, `TAREA_COLUMNA`, `metricas_columna`, `generate_escaleta_v2`. El texto de `TAREA_COLUMNA` es el de «CÓMO SE USA LA COLUMNA» (hay test contra el .md). `SYSTEM_V2` no se tocó. |
| 5 | §1.2 sin columna la escaleta es byte-idéntica a F16 (pedido extra: test contra md5) | OK | `test_module_f17.py:199-217`: md5 de fixtures y de los prompts reales de Ycuá y Orleans, más md5 de `SYSTEM_V2`. Los tests de los prompts reales hacen skip si faltan los datos de `_steps`; en esta corrida pasaron los 27. |
| 6 | §1.4 `fase1_5`: con ficha, m01a = columna → escaleta; flag `--sin-columna` | OK | `fase1_5.py` (`run_escaleta_v3(sin_columna)`, `columna="generar"`, argparse `--sin-columna`). Tests en `test_module_f17.py:258-286`. |
| 7 | §3 cost_history: sacar las entradas `t-f11b`; el tracker no registra bajo pytest (Chascada) | OK | `cost_tracker.py` sale si hay `PYTEST_CURRENT_TEST`. El respaldo `data/cost_history.pre_f17.json` tiene 505 registros, 33 de ellos `t-f11b`. El archivo actual no tiene ninguno. Hay test (`:288`). |
| 8 | §3 tests sin red; 27 de F17 verdes; dorado de v3 verde | OK | Corrí `pytest test_module_f17.py`: 27 passed. `test_module_f11.py -k v3_byte`: 1 passed. |
| 9 | §3 suite amplia 677 + 5 previas | NO VERIFICABLE | No la corrí entera. Dato declarado por la sesión madre. |
| 10 | §2 Parada 1: solo la columna de Ycuá, con `COLUMNA_ycua.md`, tope US$ 2.00, sin pisar `_f16` | OK | `costos_f17.json`: una sola etapa, US$ 0.0888, 1 intento, error null. `prompt_ycua_f17_columna.txt` guardado con md5. No hay archivos `_f17` de escaleta ni de guion. `f17_corridas.py` trae el freno de tope y el manejo de `columna_notas.md` (una sola regeneración). |
| 11 | §3 frenos: no tocar pool, `research_v3`, `ficha_caso`, m05, evidence, `guion_v3_reglas`, config, `topics_db`, m03*, `gfx_*`; cero reglas nuevas | OK | Los archivos tocados por F17 son `m01a_columna.py`, `m01a_escaleta.py`, `fase1_5.py`, `cost_tracker.py`, el test y `lab/`. Ver la nota sobre `gfx_profiles` abajo. |
| 12 | `lab/ESTADO_SESION.md` actualizado | OK | Sección «F17 … PARADA 1», con md5, costos y la limpieza de cost_history. |

Fuera de alcance: `diag_234_cap4.py`, `gfx_profiles/lexico_propuestas.json` y `gfx_profiles/misterio.json` figuran modificados. Ya estaban modificados en el git status inicial de la sesión (previos a F17). Nada de F17 los toca, pero entrarán al commit si se hace `git add -A`. `.env` y `lab/_gpt_probe_analista/` siguen sin commitear.

Observaciones:
- Cifras de cost_history: el archivo tiene hoy 473 registros, no 472. El +1 es la corrida real de la columna de Ycuá (`…-f17-columna`), así que es coherente. Conviene aclararlo en el reporte.
- Cada afirmación de contenido de la columna (por ejemplo «los Paiva negaron ordenar el cierre») depende de la ficha. No la contrasté contra la ficha ni contra el pool.
- Lo que Omar tiene que leer: 7 personas con nombre en total, incluido el humano. El prompt pide cinco o seis además del humano, así que está dentro de lo pedido. El cap 3 es el más flojo: no tiene giro propio claro y se apoya en Beatriz.

Riesgos que el contrato no cubre: (1) Los tests de md5 de los prompts reales de F16 hacen skip si faltan los `_steps`, que están en `data/` (ignorado por git). En un checkout nuevo esa garantía queda sin cubrir. (2) El freno de `cost_tracker` depende de `PYTEST_CURRENT_TEST`; un script de laboratorio sin pytest sigue escribiendo el historial. (3) El tope de US$ 2.00 se controla solo dentro de `f17_corridas.py`, que no revisé corriendo.

### 6.2 Regeneración con las notas de Omar

VEREDICTO: CUMPLE CON OBSERVACIONES

Las notas son las de Omar y se regeneró una sola vez, dentro del tope. La columna nueva cumple la nota 1, cumple en parte la 2 y la 3, y deja fuera dos elementos concretos que Omar pidió.

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | `columna_notas.md` con las 3 notas de Omar | OK | `data/scripts/_steps/f8s1-ycua-bolanos/columna_notas.md`: las tres notas coinciden con el pedido y están en el prompt guardado, literal (comprobado por código) |
| 2 | Las notas van en la tarea | OK | `prompt_ycua_f17_columna_notas.txt:426-430` («Notas del editor…» dentro de `<tarea>`); `m01a_columna.py:119-120` |
| 3 | Una sola regeneración | OK | `costos_f17.json`: etapas `columna` y `columna_notas`, un intento cada una, error null. El runner (`f17_corridas.py:92-97`) regenera solo si la columna guardada no tiene notas |
| 4 | Archivos nuevo y v1 guardados | OK | Existen y no están vacíos: `COLUMNA_ycua.md` (5688 B), `COLUMNA_ycua_v1.md`, `columna_ycua_f17(.json/_v1.json)`, `01a_columna(.json/_v1.json)`. La columna nueva guarda `notas`, y el prompt de notas está en disco |
| 5 | Costo y tope | OK | US$ 0.0804 la regeneración, US$ 0.1692 la tanda, contra un tope de US$ 2.00 (`f17_corridas.py:33`) |
| 6 | Nota 1: Liz Torres como humano, Tatiana como segunda historia | OK | Humano y pico (cap 5) son Liz. Hay citas verificadas en gancho (cap 1 «acá nos morimos todos»), pico (cap 5) y cierre (cap 7). Tatiana entra en el cap 4 (niña bajo el panel) y vuelve en el cap 6 (bomberos, amputación). No es el hilo |
| 7 | Nota 2, cap 4: entra la orden con Digna y «el jefe mandó cerrar las puertas» | PARCIAL | Están Digna y la orden atribuida a Paiva, bien marcada como interpretación de ella. Falta la cita literal «el jefe mandó cerrar las puertas». Sí la sostiene la ficha: `ficha_caso.json:3958`, de Digna, verificada_parcial |
| 8 | Nota 2, cap 7: pericia, testigos, Paiva, guardia | PARCIAL | Pericia con tres puertas cerradas: sí. Los Paiva niegan la orden: sí. El guardia reconoce la radio: sí, pero atenuado («un participante contó que los fiscales comunicaron…»), lo que coincide con la ficha (`ficha_caso.json:1035`). «Los testigos dicen todas» quedó en una sola madre, no en testigos en plural |
| 9 | Nota 3, cap 3: ruido, bola de fuego, llamas (Sosa); Beatriz y pericia como apoyo | PARCIAL | Víctor «aceite hirviendo» y Sosa con las llamas sobre quienes almuerzan: sí. Beatriz queda en AFUERA. Falta la «bola de fuego por el techo». La ficha no la sostiene: no hay ninguna «bola» (`ficha_caso.json`, búsqueda sin resultados). Solo registra el aislante del techo como vía de propagación (línea 3258) y la «explosión» de Beatriz. La columna no la inventó, pero tampoco avisa de la omisión. La pericia (origen en la chimenea y propagación por el techo) abre el desarrollo del cap 3 junto a los testigos, más que como simple apoyo |
| 10 | Documentación | OK | `lab/ESTADO_SESION.md` tiene la sección F17 con la decisión de Omar y la PARADA |

Fuera de alcance: ninguno detectado. Los cambios están en `lab/hyperframes/f17/` (sin seguimiento), `script_engine/m01a_columna.py`, `test_module_f17.py` y `lab/ESTADO_SESION.md`. `m01a_escaleta.py`, `fase1_5.py` y `cost_tracker.py` salen modificados por la entrega F17 anterior, no por esta regeneración. No ejecuté `f17_corridas.py`.

Riesgos que el contrato no cubre: la escaleta que siga hereda la omisión de la cita de Digna y de la «bola de fuego». Si Omar quiere esa cita, hay que pedirla de forma explícita, y la bola de fuego no tiene sostén en la ficha. Que «testigos» sea una sola madre, y que el guardia llegue por un tercero, son decisiones editoriales que Omar debería ver antes del «dale».
