# F25b_REPORT — ficha_caso con --modelo: Opus 5.5 ×2 contra Sol ×2 (Kyshtym, pool F23, en paralelo)

CC · 2026-10-25 · base `b2db299`, rama `f11-guion-v4`, sin merge. Prompt de la ficha v2.2 sin tocar (sistema
`070b75df…`). Las cuatro corrieron a la vez (ThreadPool de 4, `f25b_corridas.py`). **Claude US$ 2.5687 de 6.00 ·
OpenAI US$ 0.6491 de 1.00 · tiempo de pared 473.5 s.**

**En corto.** Opus terminó las dos fichas: `end_turn`, 53–60k tokens de salida, US$ 1.21–1.36. Leen bien: arcos
concretos, con fechas y montos. Pero **el chequeo les saca 58 y 71 ítems**, contra 8 y 18 de Sol, y **les deja 0 cifras**.
El motivo de los descartes es de forma (no contrasté el contenido descartado contra el pool). Sin el esquema forzado, Opus le pone otros nombres a los campos:
- `fuente: {ids: [...]}` o `fuente: {id: "D72"}` en vez de `ids`;
- `conteo` o `que_cuenta` en vez de `que`;
- dentro de `otras_versiones`, `id` (fO2) o solo `doc_id` + `offset` (fO1) en vez de `ids`.

El chequeo ve esos ítems «sin ids» y los descarta. **Así como está, la ficha de Opus no sirve: se queda sin cifras ni
decisiones.** Sigue Sol, a menos que se le dé a Claude la forma de los campos (ver §3).

## 1. Producción (`researcher_steps/ficha_caso.py`)

- **`call_for(modelo=None, *, crudo=None, post=None)`:**
  - Sin modelo: gpt-6.1-sol high, como siempre.
  - Un `claude-*`: va por `claude_helpers.make_call` con su regla (streaming, `max_tokens` 100 000, effort medium de
    `ESFUERZO_POR_ETAPA["ficha"]`, sin `output_config.format`, porque `ficha_caso` está en `SALIDA_GRANDE`, y el JSON
    se saca del texto).
  - `crudo`: cada respuesta de la API se guarda tal cual.
- **`run(…, modelo=None)`:** sin `call`, usa `call_for(modelo)` con la respuesta cruda en
  `_steps/<topic>/ficha_respuesta_cruda.json`.
- **`save(…, modelo=None)`:** registra el modelo y el effort reales (antes siempre decía Sol). `esfuerzo_de(modelo)`.
- **CLI:** `python -m researcher_steps.ficha_caso <topic> --modelo claude-opus-5-5 [--title …] [--tag …]`.
- **Sin cambios:** prompt (`system()`, `prompt()`) y chequeo (`check`).
- **Tests:** `test_module_f25b.py` (3): Claude por claude_helpers, con 100k, medium, sin esquema, JSON envuelto y
  crudo guardado; Sol high sin modelo; `save` con el modelo. Suite amplia: **863 verdes + las 5 previas**.

## 2. Las cuatro fichas

| | modelo · effort | salida (tokens) · stop | problemas del chequeo | hechos n1 / n2 | citas (verificadas) | escenas | personas | cifras | decisiones · versiones · contradicciones | US$ | s |
|---|---|---|---|---|---|---|---|---|---|---|---|
| fO1 | Opus 5.5 · medium | 59 909 · end_turn | **58** | 20 / 50 | 14 (14) | 11 | 43 | **0** (34 sacadas) | 7 · 4 · 7 | 1.3559 | 474 |
| fO2 | Opus 5.5 · medium | 52 753 · end_turn | **71** | 20 / 36 | 18 (17) | 10 | 38 | **0** (24 sacadas) | 0 · 0 · 0 | 1.2128 | 422 |
| fS1 | Sol · high | 26 639 · stop | **8** | 19 / 50 | 18 (15) | 10 | 39 | 34 | 12 · 4 · 7 | 0.3212 | 366 |
| fS2 | Sol · high | 27 312 · stop | 18 | 16 / 54 | 18 (16) | 11 | 45 | 47 | 17 · 8 · 7 | 0.3279 | 361 |

- **Entrada:** 39 424 tokens para Opus y 27 398 para Sol (el mismo prompt, otro tokenizador).
- **Ningún corte.** Tampoco hubo reintentos: una sola facturación por ficha.
- **Citas verificadas** = las citas de la ficha cuyo id del pool tiene `verificacion.estado == "verificada"`.

**Por qué el chequeo vacía a Opus** (motivos más frecuentes):

| | lo que sacó | motivos |
|---|---|---|
| fO1 | cifras 34 · decisiones 12 · citas 7 · cronología 3 | «no respaldado: sin ids» ×34 (las cifras traen `fuente.ids`) · «versión sin ids («None»)» en 11 ítems (17 versiones: `otras_versiones` con `doc_id` + `offset` y sin `ids`) · «el texto de la cita no está en sus ids» ×3 |
| fO2 | cifras 24 · decisiones 16 · descartados 11 · contradicciones 7 · versiones 4 · citas 4 | «sin ids» ×35: 24 cifras con `fuente.id` y 11 descartados que traen solo `{que, motivo}`, sin ningún campo de ids (ahí falta el campo; no tiene otro nombre) · «versión sin ids» en 27 ítems (`otras_versiones` con `id`) |
| fS1 | cifras 5 · citas 2 · personas_descartadas 1 | cifras pegadas («1997167», «2007287»), 2 citas fuera de sus ids, un descartado que no está en el pool |

Ejemplo, la misma cifra en las tres formas:
- **fO1:** `{'conteo': 'muertos tras el accidente', 'valor': 'alrededor de 200', 'fuente': {'ids': ['D72'], …}, 'otras_versiones': [{'version': …, 'doc_id': 'F10', 'offset': 5438}]}`.
- **fO2:** lo mismo con `que_cuenta` y `fuente: {'id': 'D72'}`.
- **Sol:** `{'que': …, 'valor': …, 'unidad': …, 'ids': ['D20', 'D74', 'D137'], …}`, tal como lo espera el esquema.

**Candidatos a humano y su arco:**

| | candidatos (citas verificadas) | arco del primero (Dubrovsky), textual |
|---|---|---|
| fO1 | Dubrovsky (2), Kuleshov (1), Chanova (1), **Lyudmila Smirnova** (1) | «entra mirando una película en el club la tarde en que tiembla el edificio; al día siguiente va a trabajar como siempre y lo mandan sin instrucciones, con un mono de goma y sin su «pétalo», a arrancar arbustos junto a la fuente, donde recibe cinco normas diarias; sale lavado a manguerazos, con dolor en el pecho, y sin fotocasete, por lo que no entra enseguida en la lista de liquidadores» |
| fO2 | Dubrovsky (2), Kuleshov (1), Chanova (1), Lyudmila Smirnova (1) | «entra mirando una película en el club «Derevyashka» cuando el edificio tiembla; al día siguiente lo mandan sin instrucciones a arrancar arbustos junto a la fuente, trabaja sin «pétalo» y recibe cinco normas diarias de radiación y un chorro de manguera que le duele en el pecho; sale sin fotocasete y por eso no entra de inmediato en la lista de liquidadores» |
| fS1 | Dubrovsky (2), Kuleshov (1), Galina Prokópyevna Chanova (1), **Anna Ilyina** (2) | «Entra como un espectador de cine que oye la explosión, pasa a arrancar arbustos sin instrucciones y relata un lavado doloroso con agua fría, y sale de esos trabajos con una exposición que no quedó registrada mediante los dispositivos que no les entregaron y con un reconocimiento como liquidador demorado.» |
| fS2 | Dubrovsky (2), Kuleshov (1), Chanova (1), **N.N.D.** (0) | «Entra como trabajador que oye la explosión mientras mira una película, es enviado a arrancar arbustos sin instrucciones suficientes y termina sometido a un lavado doloroso y con un reconocimiento demorado como liquidador por no haber recibido un dispositivo de registro.» |

Los arcos de Opus son más concretos: el club Derevyashka, «cinco normas diarias», el fotocasete, los 167 rublos de
Chanova en 1997 y los 287 de 2007, los ~60.000 de ~150.000. Los de Sol son más abstractos («un dispositivo de registro»).
Arcos completos de los cuatro candidatos en cada `FICHA_*.md` y en `<tag>/resultado.json`.

## 3. Lectura

- **El contenido de Opus está bien:** más concreto en los arcos, con casi todas las citas verificadas (14 de 14, 17 de
  18) y el mismo nivel 1 que Sol (20).
- **Lo que lo hunde es la forma de los campos** (la comparación en bruto de «problemas» es contra un chequeo hecho para la forma del esquema, la que Sol respeta; y es un solo pool con 2 muestras por modelo). Sin esquema forzado, Opus elige sus propios nombres, y el chequeo, que
  es estricto con `ids`, descarta todo lo que no los trae donde los espera.
- **El esquema entero no se puede volver a forzar:** la API lo rechaza por demasiado grande (HTTP 400, F25a).
- **Dos salidas posibles; no hice ninguna (prompts y chequeo quedan sin tocar):**
  1. Darle a Claude la forma de los campos como texto en el pedido. Toca el prompt.
  2. Normalizar en código lo que llega (`fuente.ids` → `ids`, `que_cuenta` / `conteo` → `que`, `id` → `ids`) antes del
     chequeo.
- **Mientras tanto, la ficha queda en Sol:** 8–18 problemas a US$ 0.32–0.33, contra US$ 1.21–1.36 de Opus.

## 4. Archivos

`lab/hyperframes/f25b/`:
- **Fichas:** `FICHA_fO1.md`, `FICHA_fO2.md`, `FICHA_fS1.md`, `FICHA_fS2.md`.
- **Por tag:** `<tag>/ficha_caso.json`, `ficha_crudo.json`, **`ficha_respuesta_cruda.json`** (la respuesta de la API
  tal cual) y `resultado.json` (métricas, arcos, llamada).
- **Costos y runner:** `costos_f25b.json` (cada llamada con max_tokens, effort, esquema, in/out, stop, US$, s),
  `f25b_corridas.py`, `run.log`.

## 5. Veredicto del revisor-handoff

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | `--modelo` en ficha_caso | OK | `git diff -- researcher_steps/ficha_caso.py`: `main()` con argparse y `run(modelo=…)`. |
| 2 | Camino Claude con la regla (stream, 100k, medium, sin esquema, crudo guardado) | OK | `call_for` usa `claude_helpers.make_call`. `claude_helpers.py:34-38` define MAX_TOKENS 100000, medium para la ficha y SALIDA_GRANDE con `ficha_caso`. `costos_f25b.json` muestra max_tokens 100000, effort medium, esquema false. `fO*/ficha_respuesta_cruda.json` existe y trae la respuesta de la API tal cual. |
| 3 | Cero prompts y chequeo tocados | OK | El diff solo añade docstring, `esfuerzo_de`, `call_for` y `main`, y pasa `modelo` en `run` y `save`. `system()`, `prompt()` y `check()` no cambian. `prompt_md5` sistema `070b75df…`, igual al de la ficha v2.2. `claude_helpers.py` y `gpt_helpers.py` no figuran en `git diff --stat`. |
| 4 | Cuatro fichas en paralelo (Opus ×2, Sol ×2); `FICHA_*.md` y reporte | OK | `FICHA_fO1/fO2/fS1/fS2.md` y `F25b_REPORT.md` existen en `lab/hyperframes/f25b/`. Las 4 corrieron en un ThreadPool y `pared_s` es 473.5. |
| 5 | Tope US$ 6 Claude y US$ 1 OpenAI | OK | `costos_f25b.json`: Claude 1.3559 + 1.2128 = 2.5687, OpenAI 0.3212 + 0.3279 = 0.6491. El runner reserva el peor caso antes de cada llamada (`f25b_corridas.py:28-60`). |
| 6 | Cifras del reporte (problemas, hechos n1/n2, citas, escenas, personas, US$, segundos) | OK | Coinciden con `resultado.json`, `ficha_caso.json` y `run.log`. Problemas: 58, 71, 8, 18. Hechos n1/n2: 20/50, 20/36, 19/50, 16/54. Citas: 14, 18, 18, 18; verificadas 14, 17, 15, 16 según `run.log`. Escenas: 11, 10, 10, 11. Personas: 43, 38, 39, 45. Cifras: 0, 0, 34, 47. Decisiones·versiones·contradicciones: 7·4·7, 0·0·0, 12·4·7, 17·8·7. US$ y segundos coinciden. |
| 7 | Descartes de Opus por campos con otros nombres | OK, con matices | Confirmado en `ficha_crudo.json` y `chequeo.sacados`. fO1 usa `conteo` y `fuente.ids`: 34 cifras sacadas por «sin ids», 0 quedan. fO2 usa `que_cuenta` y `fuente.id`: 24 cifras sacadas. En `otras_versiones`, fO1 trae `doc_id` + `offset` sin ids y fO2 trae `id`. Los sacados por sección coinciden: fO1 34 cifras, 12 decisiones, 7 citas, 3 cronología; fO2 24 cifras, 16 decisiones, 7 contradicciones, 4 versiones, 11 descartados, 4 citas. |
| 8 | Candidatos a humano con arco | OK | Cuatro candidatos por ficha, con arco en `resultado.json` y en el reporte §2. No verifiqué cada arco palabra por palabra. |
| 9 | Suite | OK | Corrida propia: 863 passed, 5 failed (las 5 previas, `test_module_01b_pauses` ×3 y `test_module_m03_merge_timing` ×2). |
| 10 | Commit, revisor, PARADA | NO VERIFICABLE | Está sin commitear y §5 dice REVISOR_PENDIENTE, como corresponde en este punto. |

Observaciones (imprecisiones del reporte, no cambian la conclusión):
- **Descartados de fO2:** el reporte atribuye el «sin ids ×35» a `fuente.id`. En realidad son 24 cifras por `fuente.id` más 11 descartados cuyo crudo trae `{que, motivo}` sin ningún campo de ids. Ahí el campo falta, no tiene otro nombre. La explicación «solo otros nombres» es cierta para las cifras y las versiones, pero no para esos 11.
- **fO1, versiones:** el «×11» del reporte cuenta ítems. Hay 17 ocurrencias de «versión sin ids». El reporte dice que fO1 usa `id` en `otras_versiones`, pero eso solo es cierto en fO2. fO1 usa `doc_id` + `offset`.
- **Contenido:** la frase «no es contenido inventado, es forma» no está probada. No se contrastó el contenido de lo descartado contra el pool; solo se comprobó que el motivo del descarte es de forma.
- **Opus vs Sol:** el reporte compara en bruto el número de problemas del chequeo entre Opus y Sol, y el chequeo usa la forma de campos de Sol.

Fuera de alcance: ninguno de esta tarea. `diag_234_cap4.py` y `gfx_profiles/*` aparecen modificados, pero Omar ya los declaró ajenos.

Riesgos que el contrato no cubre:
- La ficha de Opus queda inutilizable (0 cifras, 0 decisiones en fO2) hasta que se normalice la forma de los campos o se la dé en el pedido. Cualquiera de las dos toca el chequeo o el prompt, y eso queda fuera de F25b.
- Se probó un solo pool (Kyshtym) y 2 muestras por modelo, así que la conclusión «sigue Sol» es débil.

*(Después del veredicto, CC corrigió en el reporte las cuatro imprecisiones de arriba: los 11 descartados de fO2 sin campo de ids, las 17 versiones de fO1 con `doc_id` + `offset`, «el motivo es de forma» en lugar de «no es contenido inventado», y la advertencia sobre la comparación en bruto, con un solo pool y 2 muestras. Los números no cambiaron.)*
