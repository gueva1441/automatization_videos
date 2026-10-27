# F39 · A.2 — Escaleta sin ficha = error (salida en texto)

Subagente 1 (m01a_escaleta + tests), 2026-10-27. Handoff `lab/hyperframes/f39/HANDOFF_F39_fase1_de_la_semilla.md` §3, §6 A.2, §8; DECISIONES 2026-10-27 15:23, 2026-10-26 22:26 (casi nada hardcode) y 16:38 (borrar, no apagar). Cero llamadas a modelos, nada en `data/`, sin `git add`/`commit`, mapa sin regenerar.

## Archivos tocados

| archivo | qué |
|---|---|
| `script_engine/m01a_escaleta.py` (CRLF, editado con Edit; `file`: «with CRLF line terminators», 0 LF sueltos) | + `class EscaletaSinFicha(Exception)`; `generate_escaleta` sin ficha v2 la lanza; rama vieja y lo que solo ella usaba, borrado. md5 9a6afd1b… (copia de trabajo antes; HEAD 27f3d45d… en LF) → `7a84f8c67a832ecdb6e93bb86734058d`. 2036 → 1715 líneas (+27 −348) |
| `test_module_f39_escaleta.py` (nuevo) | 8 tests |
| `test_module_f14.py`, `test_module_f15.py`, `test_module_f15b.py`, `test_module_f16.py`, `test_module_f6b.py` (CRLF, 0 LF sueltos) | tests borrados / ajustados (abajo) |
| `test_module_f22.py`, `test_module_f7.py`, `test_module_f7d.py`, `test_module_f8.py` (LF, como estaban) | tests borrados / ajustados (abajo) |
| `lab/hyperframes/f39/a/escaleta_grep_antes.txt`, `escaleta_grep_despues.txt`, este archivo | salida A.5 (c) |

No se tocaron `fase1_5.py`, `topic_researcher.py`, `research_v3.py`, `ficha_caso.py`, `lab/tools/mapa_modulos.py`.

## El cambio

```python
class EscaletaSinFicha(Exception):
    """F39 §A.2: el topic no tiene `ficha_caso.json` con `historia` (ficha v2); la escaleta no corre (PARADA)."""

# en generate_escaleta, después de frozen → pool → compuerta → ficha="auto":
    if not (ficha and "historia" in ficha):          # F39 §A.2: sin ficha v2 no hay escaleta (ni camino viejo)
        raise EscaletaSinFicha(f"{topic_id}: sin ficha_caso.json con historia")
```
`topic_id = topic.get("id") or topic.get("topic_id")`, como ya lo usaba la función. Antes de lanzarla no se arma ningún `call` (ni el que se pasa ni `call_escaleta`). Orden sin cambios: `escaleta_frozen` (no mira la ficha) → pool vacío = ValueError → compuerta (rojo = PoolGateRed) → ficha → v2. Firma: se quitó `attempts=` (solo lo usaba la rama vieja; la v2 decía «`attempts` no aplica»); la llamada de `fase1_5.py` (m01a, hoy ~línea 382) no lo pasa.

## Símbolos borrados (solo los usaba la rama vieja)

`grep -rn` en todo el repo (código, `fase1_5.py`, `guion_v4.py`, `script_engine/`, `researcher_steps/`, `lab/tools/`, tests; alias `me.`/`ma.` y `from … import`): fuera de los tests de la rama vieja y de scripts históricos de `lab/hyperframes/f7`, `f14`, `f15`, `f15b` (ver «lo que queda abierto»), ningún llamador.

| símbolo | qué era |
|---|---|
| `PROMPT_VERSION` ("f6b-4") | versión de la escaleta sin ficha |
| `MAX_ATTEMPTS` (3) y el parámetro `attempts` | intentos del camino viejo |
| `SYSTEM` | sistema del prompt viejo (Pro) |
| `FEWSHOT` | los dos ejemplos (Sago, Triangle) |
| `rules_text`, `RULES` | las 17 reglas del prompt viejo |
| `build_prompt` | usuario del prompt viejo |
| `pool_section` (+ el apagador `ESCALETA_DIGEST`) | pool / digest / ficha v1 para el prompt viejo |
| `ficha_section` | la ficha (v1 y v2) en el formato del prompt viejo (la v2 usa `ficha_section_v2`) |
| `_fmt_people`, `_fmt_quotes`, `_fmt_canonical`, `_fmt_counts`, `_verif` | formateadores de `pool_section` / `ficha_section` |
| `own_ids` | solo lo usaban `_fmt_people` y `ficha_section` |
| el bucle Pro (`from gemini_helpers import call_pro_json`, `validate(… final=k == attempts …)`, `01a_escaleta_rechazada.json` con `prompt_version` f6b-4) | el cuerpo de la rama |

Docstring del módulo: la línea «Una llamada a Gemini Pro (`call_pro_json`) … hasta MAX_ATTEMPTS» y la de `notas topic["escaleta_notas"]` (solo las leía `build_prompt`) se reemplazaron por lo de F39.

## Símbolos que quedan por otro llamador vivo

| símbolo | quién lo usa |
|---|---|
| `SCHEMA` | `SCHEMA_FICHA = copy.deepcopy(SCHEMA)` + 3 cambios (lo que manda la v2); también `test_module_f19.py:118`, `test_module_f22.py:261` (antagonista del esquema base). Comentario nuevo: «ya no se manda solo; queda como base de SCHEMA_FICHA» |
| `MAX_APOYOS` (3) | default de `validate(max_apoyos=…)`; lo usa `frozen_escaleta` (camino `escaleta_frozen`, no se toca) y `test_module_f14.py::test_validate_apoyos_hasta_6_solo_con_ficha`. Comentario actualizado |
| `MAX_APOYOS_FICHA` (6) | `bloqueantes` (v2) |
| `count_variants` | `validate`, `writer_instructions`; `guion_v4.py:587`, `m01b_guionista.py:94` y `:295`; `test_module_f23.py:279` |
| `validate`, `question_problems`, `_beat_known`, `_plain`, constantes `INTENSITY`, `MIN_HUMAN_CAPS`, `Q_MAX_WORDS`, `FUNCIONES`, `ADMIN_TERMS`, `Q_OPENERS`, `ABSTRACT`, `WORDS_TOL`, `CAP_WORDS`, `MIN_BEATS*`, `NUM_WORDS`, `has_figure` | `bloqueantes` (v2) y `frozen_escaleta`; `NUM_WORDS` también `m01c_editor`; `has_figure` `m01b_guionista` |
| `_profile` | `generate_escaleta_v2` (rango de beats) |
| `ficha_notes`, `pool_gate_profile`, `apply_pool_plan`, `writer_instructions`, `_persist`, `EscaletaValidationError`, `is_v3` | v2 / frozen / `fase1_5` |
| `os` (import) | `is_v3` |

## md5 de los prompts v2 (antes = después)

Script `scratchpad/md5_v2.py`, corrido antes de tocar nada y después; `diff` vacío («MD5 IGUALES»):

```
SYSTEM_V2          2e67791cedbfa7492f8b6de1268b7b30
SYSTEM_V2_F25_1    9325ad3890ebfe241953d86759e20296
SYSTEM_V2_F24_1    006a195f0ce4be014df34d71644aedb1
SYSTEM_V2_F22_2    22cfd68b7cee4734e95bb3ee27bb96b2
SYSTEM_V2_F22_1    7ea18a6aa1ca91c5ad0dfb7cc9b239a8
SYSTEM_V2_F16_1    49ed74d941def064cdda077212629ff1
TAREA_V2           5808b41eb57a0949f009213d52076521
TAREA_COLUMNA      b53c30be945ea2ababa857ff04e87c83
SCHEMA_FICHA       a389dea871254a2136ee1dfaf88b403b   (json.dumps sort_keys)
PROMPT_VERSION_V2  f26-1  COLUMNA f26-1
build_prompt_v2    5aea02448a1916912d53e9ab0e66db21   (TOPIC/FICHA de test_module_f16)
build_prompt_v2 fb 69c232d0918a02a35ae7408069a08fb6   (con feedback ['x'] y beats=(7, 14))
```

## Tests

### Borrados por nombre (9) — probaban la rama vieja
| archivo::test | por qué |
|---|---|
| `test_module_f14.py::test_escaleta_sin_ficha_byte_identica` | md5 de `build_prompt` sin ficha + `RULES` |
| `test_module_f14.py::test_escaleta_con_ficha_lee_la_ficha_y_apoyos_0_6` | `build_prompt` con ficha v1 (`ficha_section`, «0–6 `datos_apoyo`» de `rules_text`, digest sin ficha) |
| `test_module_f15.py::test_escaleta_sin_ficha_sigue_byte_identica` | md5 de `build_prompt` + `SCHEMA` sin `escena_idx` (el esquema del camino viejo) |
| `test_module_f15.py::test_escaleta_con_ficha_v2_historia_y_escenas_primero` | `build_prompt` (el viejo) con ficha v2: forma pre-F16, ya no existe |
| `test_module_f15b.py::test_escaleta_sin_ficha_intacta_y_con_ficha_pide_gancho_y_pico_desde_escenas` | md5 de `build_prompt` + texto de `ficha_section` |
| `test_module_f16.py::test_sin_ficha_byte_identico` | md5 de `build_prompt` sin ficha |
| `test_module_f16.py::test_sin_ficha_sigue_por_el_camino_viejo` | afirmaba exactamente lo que F39 prohíbe (sin ficha → `SYSTEM`/`SCHEMA`); lo reemplaza `test_module_f39_escaleta` |
| `test_module_f22.py::test_escaleta_v1_byte_identica` | md5 de `SYSTEM`, `FEWSHOT`, `RULES`, `build_prompt`, `SCHEMA` y `PROMPT_VERSION == "f6b-4"` |
| `test_module_f7.py::test_escaleta_reads_v3_pool` | `build_prompt` con el pool v3 («Dan Bright», «VERIFICADA») |

Con ellos se fueron fixtures que solo ellos usaban: `ESC_MD5` (f14, importado por f15/f15b/f16), los imports `hashlib` (f14, f15, f15b, f16) y `POOL11`/`TOPIC11` (f15b, f16). pyflakes limpio en los 10 archivos.

### Ajustados (6) — usaban la rama vieja de paso, prueban otra cosa
| archivo::test | qué prueba | cambio |
|---|---|---|
| `test_module_f14.py::test_generate_escaleta_auto_lee_la_ficha_del_disco` | `ficha="auto"` lee `ficha_caso.json` del disco | sin ficha en disco → `EscaletaSinFicha` (sin llamar); con `FICHA_ESC_V2` (la ficha sintética del archivo + `historia` mínima) en disco → una sola llamada, prompt v2 con `<ficha>` y el hecho de la ficha |
| `test_module_f6b.py::test_generate_con_reintento_pool_plan_y_frozen` | generate → pool plan → persistido → `escaleta_frozen` | ficha v2 mínima sintética; el «reintento» es la regeneración v2 con un bloqueante (`dato_central` D99 inexistente; antes una intensidad que baja, que en la v2 es métrica): `<rechazo>` + «D99» + «no existe en el pool» en el 2.º prompt. El resto de las aserciones (caps 1–7, evidence_ids, cliffhanger, pantalla_ids, `_pool_plan`, humano P08 persistido, frozen sin llamar) igual |
| `test_module_f7.py::test_digest_has_real_ids_and_escaleta_uses_it` → renombrado `test_digest_has_real_ids` | el digest del research con ids reales | quedan las 4 líneas del digest; salen las de `build_prompt`/`pool_section`/`ESCALETA_DIGEST` |
| `test_module_f7d.py::test_escaleta_gate_red_spends_nothing_yellow_shortens` | rojo no gasta; amarillo ya no acorta; pool viejo sin compuerta, tope 14 | «Entre 7 y N beats» en `build_prompt` → `me._profile(t)[1:3] == (7, me.MAX_BEATS)` (el rango que la v2 dice en el usuario) |
| `test_module_f8.py::test_minimo_dos_beats_por_cap_de_desarrollo` | `validate`: ≥ 2 beats por cap de desarrollo | sale la línea `"al menos 2 beats cada uno" in me.RULES` |
| `test_module_f8.py::test_amarillo_baja_el_minimo_a_uno` | `validate` con `largo` amarillo | sale la línea de `rules_text` |

Docstrings de f14, f15, f15b, f16, f22 actualizados (decían «sin ficha byte-idéntica»).

### Nuevos: `test_module_f39_escaleta.py` (8)
Fixtures sintéticos (`test_module_f6b.POOL/good`, `test_module_f16.FICHA`), `STEPS_DIR` en `tmp_path`, `call_escaleta` parcheado para que explote.
- (a) `test_sin_ficha_en_disco_para_sin_llamar`: sin ficha → `EscaletaSinFicha`, `str(e) == "t-f39: sin ficha_caso.json con historia"`; con `call` que explota, sin `call` (el por defecto explota) y con `ficha=None`; no queda `01a_escaleta*.json`.
- (a) `test_sin_ficha_tambien_con_columna_generar`: con `columna="generar"` para antes de la columna (que explota).
- `test_es_excepcion_publica_y_no_es_de_validacion`.
- (b) `test_ficha_sin_historia_para_igual`: la ficha sin `historia`, como dict y leída del disco.
- (b) `test_topic_id_como_lo_usa_la_funcion`: con `topic_id` (sin `id`), el mensaje usa ese id.
- (c) `test_con_ficha_v2_sigue_el_camino_v2`: ficha v2 en disco, `call` falso: 1 llamada, `SYSTEM_V2`, `SCHEMA_FICHA`, prompt == `build_prompt_v2`, `prompt_version` f26-1, `_metricas`, caps 1–7, persistida.
- (c) `test_con_ficha_v2_dict_sin_call_va_por_call_escaleta`: sin `call`, va por `call_escaleta(modelo)` (falso).
- `test_frozen_no_mira_la_ficha`: `escaleta_frozen` sin ficha no para ni llama.

### Resultados
- Antes de tocar: los 20 archivos que mencionan `m01a_escaleta`/`generate_escaleta` → **362 passed**.
- Después, sin los ajustes: 15 failed / 347 passed (los 9 borrados + 6 ajustados).
- Después: `grep -ln "m01a_escaleta\|generate_escaleta" test_module_*.py` (22 archivos: los 20 + `test_module_f39_escaleta.py` + `test_module_f39_fase1.py` de CC) → **372 passed, 0 failed** (= 362 − 9 + 8 + 11 de f39_fase1).
- `test_module_f39_escaleta.py` solo → **8 passed**.
- Suite rápida `test_module_f25c.py test_module_f24.py test_module_f21.py` → **58 passed**.
- Suite amplia y candado (md5 ch02): no corridos (los corre CC al final).

## Greps (A.5 c)

`lab/hyperframes/f39/a/escaleta_grep_antes.txt` (49 líneas) y `escaleta_grep_despues.txt` (12 líneas), patrón:
`\bPROMPT_VERSION\b|\bMAX_ATTEMPTS\b|\bSYSTEM\b|\bFEWSHOT\b|\brules_text\b|\bRULES\b|\bown_ids\b|\b_fmt_people\b|\b_verif\b|\b_fmt_quotes\b|\b_fmt_canonical\b|\b_fmt_counts\b|\bficha_section\b|\bpool_section\b|\bbuild_prompt\b|\battempts\b|ESCALETA_DIGEST|call_pro_json|\bMAX_APOYOS\b|\bSCHEMA\b|EscaletaSinFicha`

Después (entero):
```
8:ficha v2, `EscaletaSinFicha` (para, sin gastar); el camino viejo (Pro con el pool, sin ficha) se borró. La salida
11:    generate_escaleta(topic)   → escaleta (persistida en _steps/<id>/01a_escaleta.json); sin ficha v2, EscaletaSinFicha
112:class EscaletaSinFicha(Exception):
121:SCHEMA: dict[str, Any] = {
144:# F39 §A.2: SCHEMA ya no se manda solo (era el de la escaleta sin ficha, borrada); queda como base de SCHEMA_FICHA.
148:SCHEMA_FICHA: dict[str, Any] = copy.deepcopy(SCHEMA)
157:MAX_APOYOS = 3                      # datos_apoyo por beat sin ficha: hoy solo el default de `validate` (escaleta_frozen)
239:             solo_apoyo: list[str] | tuple[str, ...] = (), largo: dict | None = None, max_apoyos: int = MAX_APOYOS,
781:    F39 §A.2: sin ficha v2 (no hay ficha, o no tiene `historia`), EscaletaSinFicha: para sin llamar a ningún modelo. El
799:        raise EscaletaSinFicha(f"{topic_id}: sin ficha_caso.json con historia")
1457:    """F16 §1.1: <caso> (título, ángulo, misterio, revelación) · <ficha> · <tarea> literal. Sin notas, sin FEWSHOT,
```
(La 1457 es el docstring de `build_prompt_v2`, que dice que la v2 no lleva FEWSHOT: texto, no símbolo.)

## Sticker de `m01a_escaleta` (propuesto; el mapa no se regeneró)

Hoy en `lab/tools/mapa_modulos.py:161`: «Fase 1: arma la escaleta (los beats del video con función, intensidad, datos y cierre) desde la ficha del caso; es lo que el gfx lee para saber qué va dónde.» · recibe «ficha del caso + pool».

Nuevo:
- sticker: «Fase 1: arma la escaleta (los beats del video con función, intensidad, datos y cierre) desde la ficha del caso v2; es lo que el gfx lee para saber qué va dónde. F39 §A.2: sin ficha v2 (`ficha_caso.json` con `historia`) lanza `EscaletaSinFicha` y para sin gastar; el camino viejo sin ficha (prompt, reglas y ejemplos de Pro) se borró.»
- recibe: «ficha del caso v2 + pool» · entrega `01a_escaleta.json` · F6 · vivo (fase 1; el gfx lee su salida).

## Lo que queda abierto
1. **`escaleta_notas` sin lector**: `fase1_5.py:196–202` sigue cargando `_steps/<id>/escaleta_notas.md` en `topic["escaleta_notas"]`, que solo leía `build_prompt` (borrado; la v2 dice «sin notas» desde F16). Código muerto en `fase1_5` (archivo de CC): borrarlo o decidir si la v2 debe leer notas.
2. **`pool["digest"]` sin lector en producción**: `researcher_steps/research_v3.py:2067` (`build_digest`) lo arma «para lo que lee la escaleta»; el único lector era `pool_section` (borrado). No lo toqué (no es de esta tarea y cambia el contenido del pool / `pool_md5` de las fichas). Queda para decidir: borrar `build_digest` (y su test `test_module_f7.py::test_digest_has_real_ids`) o anotar otro uso.
3. **Scripts históricos de lab que ya no corren** contra el código de hoy (usan símbolos borrados): `lab/hyperframes/f7/f7c_orleans.py:99` (`attempts=`), `lab/hyperframes/f14/f14_orleans.py:172–174`, `lab/hyperframes/f15/f15_corridas.py:189–191`, `lab/hyperframes/f15b/f15b_corridas.py:167–169` (`ma.build_prompt`, `ma.SYSTEM`); además cualquier corrida f6–f10 que llame `generate_escaleta` sin ficha v2 ahora para con `EscaletaSinFicha`. Son registro de corridas ya hechas, no llamadores vivos; no se tocaron.
4. **`SCHEMA` y `MAX_APOYOS` quedan** (ver tabla): `SCHEMA` solo como base de `SCHEMA_FICHA`; plegarlo dentro de `SCHEMA_FICHA` es un cambio de forma posible (el md5 de `SCHEMA_FICHA` tendría que seguir en `a389dea8…`), no lo hice para no tocar lo que manda la v2. `MAX_APOYOS` = 3 vive solo por `escaleta_frozen` (`validate` sin `max_apoyos`).
5. **`validate(final=…)`**: la v2 y frozen pasan siempre `final=True`; el valor `False` solo lo usaba el bucle viejo. Se dejó el parámetro (no cambia el comportamiento); simplificarlo es otra tanda.
6. **`EscaletaSinFicha` sale después de la compuerta del pool** (orden de siempre: frozen → pool → compuerta → ficha). La compuerta es determinista (no gasta) pero con `persist=True` escribe `POOL_GATE.md/json` en `_steps/<id>/` antes de parar.
7. Suite amplia (898 + 5) y candado md5 ch02 `38e5ba14…`: pendientes, los corre CC en serie al final de A. Los tests borrados (9) bajan la cuenta de la amplia.
8. El sticker de arriba no está aplicado en `lab/tools/mapa_modulos.py` ni en `lab/MAPA_MODULOS.md` (no regenerar el mapa fue consigna).
