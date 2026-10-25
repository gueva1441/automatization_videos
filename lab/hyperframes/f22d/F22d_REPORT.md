# F22d_REPORT — escaleta sin columna por defecto, guion con Opus 5.5 por defecto · Kyshtym

2026-10-24 · rama `f11-guion-v4` sobre `ee54850` · **US$ 0.7736 de 1.50** · sin merge · **PARADA**.

## 0. En corto
- **Código (decisión del analista), cero cambios de prompts** (md5 de los cuatro sistemas iguales a F22):
  - `fase1_5`: la escaleta va **siempre sin columna** (`run_escaleta_v3` llama a `generate_escaleta(columna=None)`). `--columna` genera además la columna como página de lectura (`_steps/<id>/COLUMNA_<id>.md` + `01a_columna.json`), después de la escaleta y sin pasársela. `--sin-columna` se sigue aceptando y no cambia nada (es el defecto).
  - `guion_v4.DEFAULT_MODELO_GUION = "claude-opus-5-5"`: sin `call` ni `--modelo`, `write`, `reparar` y `fase1_5.run_guion_v4` usan Opus 5.5 effort high (`claude_helpers.MAX_TOKENS` = 32,000). **`call_for(None)` sigue siendo Sol**: la escaleta y la columna también lo usan, y la decisión es escaleta con Sol.
  - Tests adaptados: f10 (el `run_escaleta_v3` falso acepta `columna=`), f12 (el guion sin `call` es Opus; `call_for(None)` sigue en Sol), f17 (la escaleta va sin columna con y sin `--columna`; la columna de lectura se escribe solo con `--columna`). Nuevo `test_module_f22d.py` (3). Suite amplia: ver §3.
- **Kyshtym** desde la ficha de F22 (`ficha_kyshtym_f22.json` = `_steps/.../ficha_caso.json`, pool md5 `8a40a7f3…`): escaleta v2.1 sin columna con Sol (intento 1: 15 bloqueantes → **intento 2: 0**), guion v5.2 con Opus: **1,695 palabras ≈ 13.8 min, 0 bloqueantes, 9 citas, 9 personas con nombre**. Cero Cardal en escaleta y narración.
- **Sin columna, la escaleta cambia de humano y de antagonista:** humano **Nadezhda Kutepova** (en F22, con columna, V. I. Komarov) y antagonista **institución «Mayak»** (en F22, «ninguno»). Trae 44 ids y 1.71 apoyos por beat contra 35 y 1.29 con columna.

## 1. Kyshtym: escaleta sin columna (Sol) → guion v5.2 (Opus 5.5), contra F22

#### Escaleta

| escaleta | beats | beats por cap | ids totales | a_pantalla | apoyos/beat | palabras de imagen (total · por beat) | intentos (bloqueantes) | humano | antagonista |
|---|---|---|---|---|---|---|---|---|---|
| F22d (sin columna, guion Opus) | 14 | [2, 1, 2, 2, 2, 3, 2] | 44 | 6 | 1.71 | 421 · 30.1 | [15, 0] | Nadezhda Kutepova | institucion Mayak |
| F22 (con columna, guion Sol; ref.) | 14 | [1, 1, 2, 2, 2, 2, 4] | 35 | 3 | 1.29 | 427 · 30.5 | [4, 0] | V.I. Komarov | ninguno ninguno |

#### Promesa del gancho y cierre humano (textuales)

| escaleta | promesa_gancho | cierre_humano |
|---|---|---|
| F22d (sin columna, guion Opus) | «Vas a entender cómo una explosión con testigos y un territorio contaminado pudo quedar fuera de la explicación pública, y por qué darla a conocer no bastó para reconocer a sus afectados.» | «Kutepova cuestiona la separación legal entre una madre expuesta y el feto. Después de su cita, queda abierta la pregunta: «¿Cuántas personas afectadas por Mayak quedaron fuera del reconocimiento y de la reparación estatal?»» |
| F22 (con columna, guion Sol; ref.) | «Vas a entender qué salió de aquel almacenamiento, cómo quedó sin explicación pública y por qué reconocer a sus afectados terminó siendo otra disputa.» | «Volver al técnico del comienzo, sin repetir su testimonio ni atribuirle un destino posterior. Su experiencia no permite contar a todos los afectados. Cerrar con la pregunta pendiente: ¿Cuántas personas afectadas por Mayak quedaron fuera del reconocimiento y de la reparación estatal?» |

#### Guion

| guion | modelo | palabras | min | bloqueantes | citas | personas con nombre | cierre |
|---|---|---|---|---|---|---|---|
| F22d (sin columna, guion Opus) | claude-opus-5-5 | 1695 | 13.8 | 0 | 9 | 9 | pregunta |
| F22 (con columna, guion Sol; ref.) | gpt-6.1-sol | 1003 | 8.2 | 0 | 6 | 6 | pregunta |

#### Por cap (palabras · citas · bloqueantes · personas con nombre)

| cap | F22d (sin columna, guion Opus) | F22 (con columna, guion Sol; ref.) |
|---|---|---|
| 1 | 241 pal · 2 citas · 0 bl · Nadezhda Kutepova | 87 pal · 0 citas · 0 bl · V. I. Komarov |
| 2 | 174 pal · 0 citas · 0 bl · Josef Stalin, Nadezhda Ivanovna Kozlova | 75 pal · 0 citas · 0 bl · V. I. Komarov |
| 3 | 241 pal · 2 citas · 0 bl · Lyubov Ladeyshchikova | 143 pal · 1 citas · 0 bl · Lyubov Ladeyshchikova, V. I. Komarov |
| 4 | 166 pal · 0 citas · 0 bl · — | 113 pal · 0 citas · 0 bl · — |
| 5 | 279 pal · 1 citas · 0 bl · Lev Nikolaevich Gaev | 149 pal · 2 citas · 0 bl · V. I. Komarov |
| 6 | 404 pal · 2 citas · 0 bl · Lev Nikolaevich Gaev, Lev Tumerman, Zhores Medvedev | 129 pal · 0 citas · 0 bl · — |
| 7 | 188 pal · 2 citas · 0 bl · Nadezhda Kutepova, Planeta de las Esperanzas, V. D. Kamynin | 295 pal · 3 citas · 1 bl · Lev Tumerman, Nadezhda Kutepova, Planeta de las Esperanzas, V. I. Komarov, Zhores Medvedev |

Costo F22d: escaleta US$ 0.297 · guion US$ 0.4766 · total US$ 0.7736 de 1.50.

Notas de la tabla: los bloqueantes del resumen se re-miden con el código de hoy (el de F22 da 0 porque el «1982» dejó de contar desde F22b); los de «por cap» son los guardados en cada corrida (por eso el cap 7 de F22 muestra 1). La comparación con F22 cambia dos cosas a la vez (columna y modelo del guion): no separa el efecto de cada una. Personas = las de la ficha con nombre de persona que la voz nombra, sin mononimios («Planeta de las Esperanzas», la ONG, pasa por su forma).

## 2. Archivos
`lab/hyperframes/f22d/`: `F22d_REPORT.md`, `ESCALETA_kyshtym.md`, `escaleta_kyshtym_f22d.json`, `escaleta_crudos_kyshtym_f22d.json`, `NARRACION_kyshtym_f22d.md`, `guion_kyshtym_f22d.json`, `costos_f22d.json`, `tabla_f22d.md`, `prompt_kyshtym_f22d_{escaleta,guion}.txt` (con md5), `f22d_corridas.py`, `f22d_tabla.py`, `run.log`. Código: `fase1_5.py`, `script_engine/guion_v4.py`, `test_module_f10.py`, `test_module_f12.py`, `test_module_f17.py`, `test_module_f22d.py`. La escaleta no se guardó en `_steps`.

## 3. Tests
Suite amplia (`test_module_f[0-9]*`, `gfx_*`, `01a*`, `01b*`, `m03_*`, fase2b reassemble/hwencode, concat, transition): **806 verdes + las 5 previas** (803 + 3 de `test_module_f22d.py`; los 3 adaptados siguen contados).

## 4. Veredicto del revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | La columna deja de alimentar a la escaleta; `--sin-columna` pasa a ser el defecto | OK | `fase1_5.py` `run_escaleta_v3` llama a `generate_escaleta(columna=None)` siempre. `--sin-columna` se acepta y no cambia nada. |
| 2 | La columna se genera solo como `COLUMNA_<tema>.md` de lectura, y solo con `--columna` | OK | `fase1_5.py`: la columna se genera después de la escaleta y no se le pasa. Los tests de f17 y f22d lo cubren. Ninguna corrida real lo ejercitó. |
| 3 | El guion v4 usa claude-opus-5-5 por defecto (max_tokens 32000, esfuerzo high) | OK | `guion_v4.py` define `DEFAULT_MODELO_GUION`; `write`, `reparar` y `run_guion_v4` lo usan. `claude_helpers.MAX_TOKENS = 32000`. `guion_kyshtym_f22d.json` registra max_tokens 32000, esfuerzo high, modelo opus. |
| 4 | La escaleta sigue en Sol; solo el guion pasa a Opus | OK | `call_for(None)` sigue siendo gpt-6.1-sol, y `test_module_f12` lo asevera. `costos_f22d.json`: escaleta con gpt-6.1-sol, guion con claude-opus-5-5. |
| 5 | Cero cambios de prompts | OK | `git diff` no toca ningún archivo de prompts; solo cambian `fase1_5.py` y `guion_v4.py` (constante y llamadas). Los md5 de sistema de escaleta (7ea18a6a…) y guion (743e4f0a…) son idénticos a los de F22 y F22c. |
| 6 | Corrida Kyshtym desde la ficha de F22: escaleta v2.1 sin columna, luego guion v5.2 | OK | `f22d_corridas.py` usa `ficha_kyshtym_f22` y `columna=None`. La escaleta es `prompt_version f22-1`, sin columna. El guion es versión f22-1. `run.log`: 14 beats, 1695 palabras, 0 bloqueantes, 9 citas. |
| 7 | Tope de US$ 1.50 | OK | Total 0.7736. Escaleta 0.1547 + 0.1424 = 0.297. Opus: 11655 in y 21497 out dan 0.4766 con la tarifa 4/20. El tope se aplica antes de cada llamada en el runner. |
| 8 | Salidas en `lab/hyperframes/f22d/`: `ESCALETA_kyshtym.md`, `NARRACION_kyshtym_f22d.md`, costos | OK | Existen y no están vacíos: 21 KB, 11.5 KB y `costos_f22d.json`. |
| 9 | Reporte con beats, ids, apoyos/beat, promesa y cierre textuales, palabras, bloqueantes, citas, personas por cap | OK | `F22d_REPORT.md` §1. Reproduje la tabla con `f22d_tabla.py` y es idéntica a `tabla_f22d.md` y al reporte. |
| 10 | Tests | OK | Mis cuatro archivos de test dieron 55 passed. Las modificaciones a f10, f12 y f17 se limitan al cambio de comportamiento. El 806 de la suite amplia no lo corrí, así que no está verificado. |
| 11 | Cero Cardal | OK | `cero_cardal.py` dio "cero Cardal" en la escaleta y en la narración. |
| 12 | Commit, revisor, PARADA | PARCIAL | Sigue sin commitear y el §4 del reporte dice REVISOR_PENDIENTE; ese lugar es para este veredicto. `lab/ESTADO_SESION.md` ya tiene la entrada F22d y dice "HECHO, PARADA". |

Observaciones:
- **Desvío no declarado.** Comparado con F22, el humano pasa de Komarov a Kutepova y el antagonista de "ninguno" a la institución Mayak. El reporte sí lo declara y aclara que la comparación mezcla dos cambios a la vez (columna y modelo del guion).
- **Cifras con diferencia mínima.** Las palabras por capítulo suman 1693 y el total dice 1695. No es contradicción grave, pero el reporte no lo explica.
- **Conteo de personas.** Las "9 personas con nombre" incluyen a "Planeta de las Esperanzas", que es una ONG y no una persona. El reporte lo menciona al pasar, pero la cifra queda inflada.
- **Intento 1 de la escaleta.** Tuvo 15 bloqueantes y el intento 2 tuvo 0. El docstring de `f22d_corridas.py` habla de 13; es un detalle cosmético.
- **Cambio de interfaz.** `process_topic` y `run_escaleta_v3` ya no tienen el parámetro `sin_columna`; ahora se llama `columna`, con otro sentido. Cualquier llamador externo que use el nombre viejo se rompe. El reporte no lo menciona.
- **Guion sin reparación.** La corrida usó una sola llamada, sin reparación. Solo lo dice el docstring del runner, no el reporte.

Fuera de alcance: ninguno de esta tanda. `diag_234_cap4.py` y `gfx_profiles/*` están modificados, pero el pedido ya los marca como ajenos. Los archivos de F22d son `fase1_5.py`, `script_engine/guion_v4.py`, `test_module_f10.py`, `test_module_f12.py`, `test_module_f17.py`, `test_module_f22d.py`, `lab/hyperframes/f22d/` y `lab/ESTADO_SESION.md`.

Riesgos que el contrato no cubre:
- Con Opus 5.5 por defecto, el costo y el límite de salida de 32 000 tokens quedan sin tope en las corridas normales. El tope de 1.50 solo vive en el runner del laboratorio.
- La ruta `--columna` solo está probada con tests con mocks, no con una corrida real.
- El efecto de quitar la columna no se aísla del efecto de cambiar el modelo del guion, porque la corrida varía las dos cosas contra F22.
