# F22b_REPORT — corrector de cifras «recibidas», Claude Opus 5.5 en la cadena del guion v4, cinco guiones de Ycuá

2026-10-24 · rama `f11-guion-v4` sobre `ed55399` · **US$ 0.9897 de 4.00** (Sol + Anthropic, con la llamada de prueba) · sin merge · **PARADA**.

## 0. En corto
- **Corrector (1):** `invented_numbers` acepta las cifras de las líneas de datos que recibió el guionista en el bloque `<escaleta>` (texto de la ficha o del pool, marcas VERSIÓN DE / PANTALLA, fuente). El «1982» de Kyshtym F22 deja de ser bloqueante: con el mismo guion de F22, `guion_v4.bloqueantes` da **0** (antes 1). No es una regla nueva: el juez lee una fuente más.
- **Claude (2):** `claude_helpers.py` (copia de `gpt_helpers.py` contra la Messages API, `anthropic-version: 2026-10-21`, salida JSON con `output_config.format`, PRICES Opus 5.5 4 / 20 y Sonnet 5.5 2 / 10 US$ por millón). Llamada de prueba de 10 tokens: **HTTP 200**, `claude-opus-5-5`, «ok», US$ 0.000148. No hizo falta habilitar nada para `api.anthropic.com`. `--modelo claude-opus-5-5` en `fase1_5` y `guion_v4.call_for` (effort `high`, como Sol).
- **Cinco guiones sobre la misma escaleta de F22: los cinco con 0 bloqueantes y cero Cardal.** Sol v5.2: 939 y 846 palabras; **Sol v5.1: 803**; **Opus 5.5 v5.2: 1,144 y 1,159** (≈ 9.3 min, 13 personas, 8–9 citas). F16 (otra escaleta): 1,384.
- **Lo que esto responde de F22:** con la misma escaleta, el v5.1 de Sol sale tan corto como el v5.2 (803 contra 846–939). La caída de largo de F22 (838 contra 1,384 de F16) no viene del prompt v5.2: viene de la escaleta nueva (o de Sol con esa escaleta). Opus, con el mismo prompt y la misma escaleta, escribe un 30 % más que Sol y reparte más personas en los caps 6 y 7.
- Tests: `test_module_f22b.py` (8); suite amplia **803 verdes + las 5 previas**.

## 1. Corrector: cifras de lo que recibió el guionista
- `m05_narrative.invented_numbers(text, pool, facts, recibido=None)`: con `recibido`, sus números se suman a las fuentes.
- `guion_v4.datos_recibidos(esc, pool, ficha, largo, version)`: el bloque `<escaleta>` que armó el usuario de esa versión (`escaleta_section_v5` para v5/v5.1/v5.2; `escaleta_section` para f11c/f13), **solo las líneas con un «[id]»** (las de datos: texto, marcas, fuente) y **sin los ids** (el 96 de «[D96]» no cuenta). Los números de estructura («BEAT 5», «intensidad 4», «CAP 3») no entran.
- `guion_v4.bloqueantes(..., version=PROMPT_VERSION)` pasa `datos_recibidos` a (a). Las llamadas internas (`reparar`, `editor_pass`) usan la versión por defecto.
- Test con Kyshtym F22: el guion guardado tenía 1 bloqueante («cifra que no está en el research: 1982»); sin `recibido` sigue saliendo 1982, con `recibido` no, y `bloqueantes` da `[]`. El «1982» viene de «VERSIÓN DE: An Analysis of the Alleged Kyshtym Disaster, 1982». Kyshtym no se volvió a correr (no estaba pedido): con el corrector, su guion de F22 pasa.
- El dorado v3 sigue verde (`test_module_f11.py`).

## 2. claude_helpers.py y `--modelo claude-opus-5-5`
- Misma firma y forma que `gpt_helpers`: `call_json` / `make_call(model, effort, post=)`, HTTP directo con `urllib` (el SDK `anthropic` no está instalado en el venv, y el pedido era una copia de `gpt_helpers`). Headers `x-api-key`, `anthropic-version: 2026-10-21`, `content-type`.
- La llave sale de `ANTHROPIC_API_KEY` (entorno) o de `.env`; nunca se imprime ni se escribe: los errores muestran el código HTTP y el cuerpo de la respuesta. Verifiqué que `sk-ant-` no aparece en ningún archivo del repo fuera de `.env`.
- Cuerpo: `model`, `max_tokens`, `system`, `messages`, `output_config: {effort, format: {type: json_schema, schema}}` (el esquema estilo Gemini pasa a JSON Schema con `additionalProperties: false` en cada objeto). Sin `thinking` (Opus 5.5 piensa siempre, adaptativo; su effort por defecto es `medium`, por eso va `high` explícito, como Sol).
- Reintenta 408/429/529/5xx, timeout y JSON roto; otro 4xx o `stop_reason: refusal` → `ClaudeError`. Costo: `usage.input_tokens × in + usage.output_tokens × out` (el razonamiento de Claude viene dentro de `output_tokens`; por eso en `costos_f22b.json` Opus no separa thinking y Sol sí).
- **Sin `fallbacks` del lado del servidor** (la skill de la API lo recomienda por defecto para Opus 5.5): en una comparación de modelos, que una negativa re-corra en otro modelo mezclaría resultados. Una negativa sale como error. Ninguna corrida se negó.
- `guion_v4`: `MODELOS` + `claude-opus-5-5`, `CLAUDE = ("claude-opus-5-5",)`, `ESFUERZO["claude-opus-5-5"] = "high"`, `call_for` → `claude_helpers.make_call`. `fase1_5 --modelo` acepta `claude-opus-5-5`. El modelo por defecto sigue siendo Sol.

## 3. Corridas (solo el paso del guion)
Runner `f22b_corridas.py`: misma escaleta (`lab/hyperframes/f22/escaleta_ycua_f22.json`, idéntica a `_steps/.../01a_escaleta_f22.json`), misma ficha v2 de F15b, perfil del seed cargado; `max_tokens` / `max_completion_tokens` 24,000; freno antes de cada llamada contra el tope de US$ 4.00 (lo gastado + el peor caso); una sola facturación por llamada; sin reparación (como F16–F22). Bloqueantes re-medidos con el corrector nuevo y la versión de cada corrida.
- **Desvío de nombre:** el pedido dice «Sol v5.1 ×1 (system("f15-1"))». En `guion_v4`, `"f15-1"` es el **v5** (F15); el v5.1 es `"f15b-1"`. Corrí el **v5.1** (`f15b-1`), que es lo que dicen la etiqueta «v5.1» y el nombre `sol51`. Si se quería el v5, es una corrida más (≈ US$ 0.12).

#### Resumen

| corrida | modelo · guion | palabras | min | bloqueantes | citas | personas con nombre | cierre | US$ |
|---|---|---|---|---|---|---|---|---|
| sol52a | gpt-6.1-sol · v5.2 | 939 | 7.6 | 0 | 7 | 13 | pregunta | 0.0968 |
| sol52b | gpt-6.1-sol · v5.2 | 846 | 6.9 | 0 | 7 | 11 | pregunta | 0.1372 |
| sol51 | gpt-6.1-sol · v5.1 | 803 | 6.5 | 0 | 7 | 13 | pregunta | 0.1209 |
| opus52a | claude-opus-5-5 · v5.2 | 1144 | 9.3 | 0 | 9 | 13 | pregunta | 0.3261 |
| opus52b | claude-opus-5-5 · v5.2 | 1159 | 9.4 | 0 | 8 | 13 | pregunta | 0.3086 |
| F22 (ref.) | gpt-6.1-sol · v5.2 | 838 | 6.8 | 0 | 7 | 13 | pregunta | — |
| F16 (ref.) | gpt-6.1-sol · v5.1 · escaleta F16 | 1384 | 11.3 | 0 | 9 | 24 | cita | — |

#### Por cap (palabras · personas con nombre · citas · bloqueantes)

| cap | sol52a | sol52b | sol51 | opus52a | opus52b | F22 (ref.) | F16 (ref.) |
|---|---|---|---|---|---|---|---|
| 1 | 90 · 1p · 1c · 0b | 84 · 1p · 1c · 0b | 79 · 1p · 1c · 0b | 130 · 1p · 1c · 0b | 136 · 1p · 1c · 0b | 82 · 1p · 1c · 0b | 94 · 1p · 1c · 0b |
| 2 | 99 · 2p · 0c · 0b | 92 · 2p · 0c · 0b | 91 · 2p · 0c · 0b | 126 · 3p · 0c · 0b | 131 · 3p · 0c · 0b | 88 · 2p · 0c · 0b | 129 · 4p · 1c · 0b |
| 3 | 119 · 1p · 1c · 0b | 119 · 1p · 1c · 0b | 108 · 1p · 1c · 0b | 145 · 1p · 1c · 0b | 145 · 1p · 1c · 0b | 112 · 1p · 1c · 0b | 295 · 7p · 2c · 0b |
| 4 | 109 · 2p · 1c · 0b | 106 · 2p · 1c · 0b | 102 · 2p · 1c · 0b | 146 · 2p · 1c · 0b | 136 · 2p · 1c · 0b | 102 · 2p · 1c · 0b | 177 · 4p · 1c · 0b |
| 5 | 109 · 1p · 2c · 0b | 107 · 1p · 2c · 0b | 85 · 1p · 2c · 0b | 106 · 2p · 1c · 0b | 171 · 1p · 2c · 0b | 107 · 1p · 2c · 0b | 46 · 0p · 1c · 0b |
| 6 | 158 · 1p · 0c · 0b | 143 · 1p · 0c · 0b | 130 · 1p · 0c · 0b | 215 · 5p · 1c · 0b | 164 · 3p · 0c · 0b | 143 · 1p · 0c · 0b | 340 · 6p · 0c · 0b |
| 7 | 255 · 6p · 2c · 0b | 195 · 3p · 2c · 0b | 208 · 5p · 2c · 0b | 276 · 9p · 4c · 0b | 276 · 9p · 3c · 0b | 204 · 5p · 2c · 0b | 303 · 8p · 3c · 0b |

#### Personas con nombre por cap

| corrida | personas con nombre por cap |
|---|---|
| sol52a | 1: Liz Torres · 2: Alfredo Vallovera, Benedicto Pérez · 3: Beatriz González · 4: Digna Felicia Cáceres, Víctor Galeano · 5: Tatiana Gabaglio · 6: Nelson Astigarraga · 7: Antonio Morínigo, Daniel Areco, Juan Pío Helvidio Paiva Escobar, Luis Escobar Faella, Víctor Daniel Paiva, Víctor Galeano |
| sol52b | 1: Liz Torres · 2: Alfredo Vallovera, Benedicto Pérez · 3: Beatriz González · 4: Digna Felicia Cáceres, Víctor Galeano · 5: Tatiana Gabaglio · 6: Nelson Astigarraga · 7: Antonio Morínigo, Juan Pío Helvidio Paiva Escobar, Luis Escobar Faella |
| sol51 | 1: Liz Torres · 2: Alfredo Vallovera, Benedicto Pérez · 3: Beatriz González · 4: Digna Felicia Cáceres, Víctor Galeano · 5: Tatiana Gabaglio · 6: Nelson Astigarraga · 7: Antonio Morínigo, Daniel Areco, Juan Pío Helvidio Paiva Escobar, Luis Escobar Faella, Víctor Daniel Paiva |
| opus52a | 1: Liz Torres · 2: Alfredo Vallovera, Benedicto Pérez, Liz Torres · 3: Beatriz González · 4: Digna Felicia Cáceres, Víctor Galeano · 5: Liz Torres, Tatiana Gabaglio · 6: Alfredo Vallovera, Digna Felicia Cáceres, Liz Torres, Nelson Astigarraga, Tatiana Gabaglio · 7: Antonio Morínigo, Daniel Areco, Digna Felicia Cáceres, Juan Pío Helvidio Paiva Escobar, Liz Torres, Luis Escobar Faella, Tatiana Gabaglio, Víctor Daniel Paiva, Víctor Galeano |
| opus52b | 1: Liz Torres · 2: Alfredo Vallovera, Benedicto Pérez, Liz Torres · 3: Beatriz González · 4: Digna Felicia Cáceres, Víctor Galeano · 5: Tatiana Gabaglio · 6: Digna Felicia Cáceres, Nelson Astigarraga, Tatiana Gabaglio · 7: Antonio Morínigo, Daniel Areco, Digna Felicia Cáceres, Juan Pío Helvidio Paiva Escobar, Liz Torres, Luis Escobar Faella, Tatiana Gabaglio, Víctor Daniel Paiva, Víctor Galeano |
| F22 (ref.) | 1: Liz Torres · 2: Alfredo Vallovera, Benedicto Pérez · 3: Beatriz González · 4: Digna Felicia Cáceres, Víctor Galeano · 5: Tatiana Gabaglio · 6: Nelson Astigarraga · 7: Antonio Morínigo, Daniel Areco, Juan Pío Helvidio Paiva Escobar, Luis Escobar Faella, Víctor Daniel Paiva |
| F16 (ref.) | 1: Liz Torres · 2: Alfredo Vallovera, Blas Cristaldo, Teresa Urbieta, Ángela Pujol · 3: Beatriz González, Benedicto Pérez, Carlos Halke, Cristian Sosa, Enrique Riera, Martín Burt, Víctor Galeano · 4: Alejandro Nissen, Digna Felicia Cáceres, Tatiana Gabaglio, Víctor Galeano · 5: — · 6: Cristian Sosa, Juan Pío Helvidio Paiva Escobar, Luis Escobar Faella, Nelson Astigarraga, Rubén Urbieta, Víctor Galeano · 7: Daniel Areco, Digna Felicia Cáceres, Edgar Sánchez, Ismael Alcaraz, Juan Pío Helvidio Paiva Escobar, Luis Escobar Faella, María Estela Morínigo Giménez de Palacios, Teresa Sosa |

Tanda F22b: US$ 0.9897 de 4.00 (incluye la llamada de prueba de la llave).

Narraciones: `NARRACION_ycua_f22b_{sol52a,sol52b,sol51,opus52a,opus52b}.md` (cada una con palabras, bloqueantes, citas y personas con nombre por cap, y el texto por cap). Crudos: `guion_ycua_f22b_<tag>.json`; prompts con md5: `prompt_ycua_f22b_<tag>.txt` (los dos v5.2 de Sol y los dos de Opus tienen el mismo sistema y el mismo usuario). Personas = las de la ficha con nombre de persona que la voz nombra, sin mononimios (la misma medida de F22).

### Lectura
- **Ruido de Sol con el mismo prompt:** 939 contra 846 palabras, 13 contra 11 personas. Sol v5.1 (803) queda dentro de ese rango por abajo.
- **Opus 5.5:** +25–35 % de palabras sobre Sol con el mismo prompt (1,144 / 1,159), caps 1 y 2 más largos (130 contra 90), y en los caps 6 y 7 vuelve a nombrar a Liz, Tatiana y Digna (Sol nombra solo a Nelson Astigarraga en el 6). Las dos corridas de Opus son muy parecidas entre sí (salvo el cap 5: 106 contra 171).
- **Ninguno llega al largo de F16** (1,384, otra escaleta).
- Costo por guion: Sol US$ 0.10–0.14; Opus US$ 0.31–0.33 (≈ 13–14 k tokens de salida con el razonamiento, 132–140 s).

## 4. Costo
| paso | US$ |
|---|---|
| prueba de la llave (10 tokens) | 0.0001 |
| sol52a · sol52b · sol51 | 0.0968 · 0.1372 · 0.1209 |
| opus52a · opus52b | 0.3261 · 0.3086 |
| **total** | **0.9897** de 4.00 |

## 5. Tests
- `test_module_f22b.py` (8): el 1982 de Kyshtym (antes 1 bloqueante, ahora 0; sin `recibido` se sigue marcando); ids y números de estructura no cuentan; `datos_recibidos` sigue la versión del usuario; esquema → structured outputs; cuerpo, respuesta y costo de `call_json` con un `post` falso; negativa y JSON roto; la llave de `.env` sin aparecer en el error; `--modelo claude-opus-5-5` en la cadena v4.
- Suite amplia (`test_module_f[0-9]*`, `gfx_*`, `01a*`, `01b*`, `m03_*`, fase2b reassemble/hwencode, concat, transition): **803 verdes + las 5 previas**.

## 6. Archivos
Código: `claude_helpers.py` (nuevo), `script_engine/guion_v4.py`, `script_engine/m05_narrative.py`, `fase1_5.py`, `test_module_f22b.py`. Lab: `lab/hyperframes/f22b/` (`F22b_REPORT.md`, `f22b_corridas.py`, `f22b_tabla.py`, `prueba_llave.py` y `.json`, `tabla_f22b.md`, `resumen_f22b.json`, `costos_f22b.json`, las 5 narraciones, los 5 crudos, los 5 prompts, logs). No se commitean `.env`, `config.py` ni `lab/_gpt_probe_analista/`.

## 7. Veredicto del revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

Corrí los 18 tests (`test_module_f22b.py` y `test_module_f11.py`): pasan. `f22b_tabla.py` corre sin error. `cero_cardal.py` da «cero Cardal» en las 5 narraciones y en los 5 `guion_*.json`. No corrí nada que gaste API.

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Corrector: `invented_numbers` recibe además los números de las líneas del bloque `<escaleta>` | OK | `m05_narrative.py` agrega `recibido` como parámetro opcional que se suma a las fuentes. `guion_v4.datos_recibidos` toma las líneas con `[id]` del bloque que recibió el guionista y les quita los ids. |
| 1b | Test con el «1982» de Kyshtym F22 | OK | `test_kyshtym_1982_ya_no_es_inventada` pasa. Hay además tests de ids y números de estructura, y de que se sigue la versión del prompt. |
| 1c | «Cero reglas nuevas» | OK | El diff solo amplía el texto fuente de la regla (a) existente. No hay código de decisión nuevo, y el reporte lo declara así. |
| 2 | `claude_helpers.py` copia de `gpt_helpers.py` contra la Messages API | OK | Misma firma. `URL=https://api.anthropic.com/v1/messages`, header `anthropic-version: 2026-10-21`, llave de `ANTHROPIC_API_KEY`, JSON vía `output_config.format`. |
| 2b | PRICES según la tabla pública | OK | `claude_helpers.py:25`: Opus 5.5 (4, 20) y Sonnet 5.5 (2, 10). Es lo que pidió Omar. Contra la tabla pública real no lo pude verificar yo. |
| 2c | `--modelo claude-opus-5-5` en la cadena v4 | OK | Cambios en `fase1_5.py` y en `guion_v4.py` (`MODELOS`, `CLAUDE`, `call_for`). El test de la cadena pasa. |
| 2d | Llamada de prueba de 10 tokens antes de las corridas | OK | `prueba_llave.json`: HTTP 200, `claude-opus-5-5`, «ok», US$ 0.000148. |
| 3 | Llave nunca impresa ni copiada | OK | `grep -rl "sk-ant-"` fuera de `.env` solo da `F22b_REPORT.md`. Es la cadena literal en una frase del texto, sin llave. |
| 4 | Corridas: Sol v5.2 ×2, Sol v5.1 ×1, Opus v5.2 ×2, misma escaleta, solo el guion | PARCIAL | Las 5 existen, con prompts y md5. Los dos Sol v5.2 y los dos Opus comparten sistema `743e4f0a`. La corrida «Sol v5.1» no es lo que pidió Omar al pie de la letra (ver observación 1). |
| 5 | Tope US$ 4.00 entre las dos APIs | OK | La suma de `costos_f22b.json` da 0.989748, igual al reporte. Recalculé a mano Opus 5.5 y Sol 5.2a con los tokens y los precios del archivo, y coinciden. |
| 6 | 5 archivos `NARRACION_ycua_f22b_*.md` con palabras, bloqueantes, citas y personas por cap | OK | Existen con los nombres exactos. Las cabeceras coinciden con la tabla del reporte (939, 846, 803, 1144, 1159 palabras; 0 bloqueantes). |
| 7 | Tabla comparativa en `F22b_REPORT.md` | OK | Tabla resumen, tabla por cap y personas por cap, con F22 y F16 como referencia. |
| 8 | Commit, revisor-handoff, PARADA | NO VERIFICABLE | Los cambios siguen sin commitear (esperado en esta etapa). El §7 del reporte dice `REVISOR_PENDIENTE`; este veredicto va ahí. |

Observaciones:
1. **Desvío en Sol «v5.1 (system("f15-1"))».** En el código `"f15-1"` es el v5 y `"f15b-1"` es el v5.1 (`guion_v4.py:42-43`). La corrida usó `f15b-1`, el v5.1, y el reporte lo declara con el costo de la alternativa (≈ US$ 0.12). Si Omar quería el v5, falta esa corrida. Es una ambigüedad del pedido, resuelta por la etiqueta «v5.1».
2. **Extra no pedido: `effort: high` en Opus.** Se fijó en `ESFUERZO` para igualar a Sol, porque el defecto de Opus es `medium`. Está declarado. Sube el costo de Opus y condiciona la comparación.
3. **Otra decisión propia declarada:** sin `fallbacks` del servidor, para no mezclar modelos en una comparación.
4. **Pendiente que no contradice el pedido:** `bloqueantes(...)` usa `PROMPT_VERSION` por defecto en `reparar` y `editor_pass`. El corrector toma las líneas del prompt v5.2 aunque la cadena corra una versión vieja. Solo las corridas de F22b pasan `version` explícita.
5. **Cifras coherentes.** El costo total, las palabras por corrida y los md5 de prompt coinciden entre reporte, narraciones y `costos_f22b.json`. No verifiqué las cifras por cap una a una.

Fuera de alcance: ninguno entre los archivos tocados por esta tanda. Son `claude_helpers.py` y `test_module_f22b.py` (nuevos), `lab/hyperframes/f22b/`, `fase1_5.py`, `script_engine/guion_v4.py`, `script_engine/m05_narrative.py` y `lab/ESTADO_SESION.md`. `diag_234_cap4.py` y `gfx_profiles/*` aparecen modificados, pero Omar ya dijo que no son de esta tanda.

Riesgos que el contrato no cubre: el corrector acepta cualquier cifra presente en el texto de datos, incluidas las que el modelo podría haber citado mal pero que figuran ahí. La conclusión «la caída de largo viene de la escaleta» sale de 1 corrida de Sol v5.1 contra 2 de Sol v5.2; la muestra es chica.
