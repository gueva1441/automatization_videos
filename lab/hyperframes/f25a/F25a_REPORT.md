# F25a_REPORT — ¿qué modelo para la ficha y la escaleta? (Kyshtym, pool F23, en paralelo)

CC · 2026-10-25 · base `b27f54c`, rama `f11-guion-v4`, sin merge. Entrada: el pool de Kyshtym de F23 y su perfil (sin
research). Prompts y chequeos sin cambios: ficha v2.2 `070b75df…`, escaleta f24-1 `006a195f…`, guion v5.3 `8ca9aa49…`.
- **Runner:** `f25a_corridas.py`, ThreadPool de 4 workers por etapa. El costo de cada llamada sale de `usage`. El freno
  reserva el peor caso con lock y hay una sola facturación por llamada (un corte por `max_tokens` no se reintenta: se
  anota).
- **Gasto:** Claude **US$ 13.5704 de 15.00** · OpenAI **US$ 1.3708 de 4.00**.
- **Tiempo de pared:** **2,637 s (44 min)** sumando las cuatro corridas: 1,035 + 371 + 747 + 484 s.

**En corto: Sol para la ficha y para la escaleta.**
- **Ficha:** Fable no llegó a dar ninguna en cuatro llamadas (US$ 6.69 gastados).
  - 1.ª corrida: HTTP 400 por el esquema.
  - Sin esquema y con 32 000 de salida: las dos se cortaron por `max_tokens`.
  - Con tu regla (100 000, streaming, effort medium): fF1 terminó (46 119 tokens de salida), pero el JSON no se pudo
    leer y se perdió. fF2 no entró en el tope.
  - Las dos de Sol salieron a la primera, por US$ 0.38–0.40.
- **Escaleta:** cada modelo pasó 1 de 2.
  - Fable cuesta 7–10× más (US$ 2.1–2.8 contra 0.29), apila 4.8 apoyos por beat contra 2.3, y su guion se pasa del tope
    de palabras (2,047 > 1,700).
  - Sol reparte 1·1·2·2·1·3·3 y su guion da 1,499 palabras con 0 bloqueantes.

## 1. Etapa 1 — ficha v2.2

| | modelo | problemas del chequeo | hechos n1 / n2 | citas (verificadas) | escenas | humanos candidatos | personas | US$ | s |
|---|---|---|---|---|---|---|---|---|---|
| fS1 | gpt-6.1-sol high | 11 | 18 / 52 | 20 (17) | 12 | Dubrovsky, Kuleshov, Chanova | 43 | 0.3835 | 383 |
| **fS2** | gpt-6.1-sol high | **9** | 19 / 49 | 16 (13) | 11 | Dubrovsky, Kuleshov, Chanova | 47 | 0.4019 | 401 |
| fF1 | claude-fable-5-1 | — | — | — | — | — | — | 4.6944 | 371 + 483 |
| fF2 | claude-fable-5-1 | — | — | — | — | — | — | 1.9942 | 356 |

**Mejor ficha de Sol: fS2** (menos problemas: 9 contra 11). **Mejor de Fable: ninguna.**

Qué le pasó a Fable, en orden:
1. **HTTP 400 en las dos (1.ª corrida, US$ 0, 0.5 s):** «The compiled grammar is too large… Simplify your tool
   schemas». La API no acepta el esquema de la ficha como `output_config.format`. No es un corte.
2. **Sin esquema forzado, `max_tokens` 32 000, effort high:** las dos se cortaron por `max_tokens` (39 424 in /
   32 000 out, US$ 1.9942 cada una). No se reintentaron; queda anotado. Copias en `_fF1_32k/` y `_fF2_32k/`.
3. **Con la regla nueva (100 000 en streaming, effort medium, sin esquema), en serie por el tope:**
   - **fF1** terminó (`end_turn`, 46 119 tokens de salida, US$ 2.7002, 483 s), pero `json.loads` falló («Expecting
     value»). Sin esquema, el modelo seguramente envolvió el JSON en texto o en un bloque de código.
   - El runner no guardaba la respuesta cruda, así que **se perdió**. No se reintentó: la regla es una sola facturación.
   - Ya está arreglado: `claude_helpers.json_del_texto` (del primer «{» al último «}», con test), y el runner ahora
     guarda cada respuesta en `<tag>/respuesta_*.json`.
   - **fF2** no corrió: freno (13.57 + peor caso 3.37 > 15.00).

Citas verificadas = las citas de la ficha cuyo id del pool (Q##) tiene `verificacion.estado == "verificada"`. El campo
`verificacion` de la ficha es texto libre del modelo; mi primera versión lo leía como estado y daba 0.

## 2. Etapa 2 — escaleta f24-1 sin columna (las cuatro sobre fS2)

**Desvío:** sin ficha de Fable, eF1 y eF2 corrieron con Fable **sobre la ficha de Sol (fS2)**, igual que eS1 y eS2. Así
la escaleta se compara con la misma entrada. Las escaletas de Fable corrieron **antes** de la regla nueva (`max_tokens`
32 000, effort high); no se cortaron.

| | modelo | beats 1.ª pasada → final | bloqueantes 1.ª → 2.ª | ids | apoyos/beat | humano · antagonista | US$ | s |
|---|---|---|---|---|---|---|---|---|
| eS1 | Sol high | 1·1·3·2·1·3·3 → **1·1·2·2·1·3·3** (13) | 28 → **0** | 43 | 2.31 | Dubrovsky · Gobierno de la URSS (institución) | 0.2961 | 431 |
| eS2 | Sol high | 1·1·3·2·1·3·3 → rechazada | 21 → 1: «beat 9: D117 es otra cifra del conteo 12.763 [D45]» → PARADA | — | — | — | 0.2893 | 426 |
| eF1 | Fable high | 1·2·2·2·2·2·2 → rechazada | 15 → 2: «beat 2: dato_central «L09» no existe…», «antagonista … (comisión de Slavsky) no es una persona del pool ni una institución de la ficha» → PARADA | — | — | — | 2.1362 | 413 |
| eF2 | Fable high | 1·2·2·2·1·3·2 → **1·2·2·2·2·3·2** (14) | 9 → **0** | **81** | **4.79** | Dubrovsky · Ministerio soviético de Construcción de Maquinaria Mediana | 2.8047 | 551 |

- **Promesa:**
  - eS1: «¿Cómo se vuelve invisible el daño que un hombre puede sentir en el pecho?»
  - eF2: «Un hombre pide que apaguen una manguera de bomberos porque el agua fría le duele en el pecho. Lo que le estaban
    sacando del cuerpo, el mundo tardó casi veinte años en saber que existía.»
  - eF2 es una imagen más un adelanto. La segunda oración resume lo que viene, justo lo que la regla f22-2 saca.
- **Cierre:**
  - eS1: «Volver a Dubrovsky y al dispositivo que no recibió. Terminar con una pregunta, no con un balance inventado:
    «¿Cuál fue el costo sanitario completo del desastre, y cuántos afectados quedaron sin reconocimiento o reparación
    después de una exposición que ni siquiera pudieron registrar?»»
  - eF2: «Vuelve a Dubrovsky con el dato que cierra su arco: a los seis electricistas no les dieron fotocasetes y no los
    incorporaron de inmediato a la lista de liquidadores. Nadie midió lo que recibió junto a la fuente. La pregunta que
    nadie respondió es cuántos como él quedaron fuera de todas las cuentas, no de las que se discuten (Buldakov, los 66
    casos, los 200 muertos) sino de las que nunca se hicieron.»
- **Tokens de salida:** Sol, 10–13k por intento; Fable, 13–25k.
- **Reparto:** las cuatro primeras pasadas quedaron en 1–3 beats por cap (el bloqueante de F24 no saltó en ninguna).

## 3. Etapa 3 — guion v5.3 con Fable (solo las escaletas que pasaron)

gS2 y gF1 no corrieron: sus escaletas fueron rechazadas.

| | escaleta | palabras ≈ min | bloqueantes | citas | palabras por cap | personas con nombre por cap | US$ | s |
|---|---|---|---|---|---|---|---|---|
| gS1 | eS1 (Sol) | **1,499 ≈ 12.2** | **0** | 5 | 146 · 195 · 310 · 174 · 97 · 304 · 266 | 1 Dubrovsky · 2 Dubrovsky · 3 Dubrovsky, Slavsky · 4 Chelyabinsky Rabochy, Demyanovich, Slavsky · 5 Dubrovsky · 6 Dubrovsky, Otdelnov, Medvedev · 7 Dubrovsky, Chanova, Sociedad Civil | 0.9550 | 197 |
| gF2 | eF2 (Fable) | 2,047 ≈ 16.6 | **1** (2,047 palabras > tope 1,700) | **10** | 143 · 311 · 330 · 288 · 271 · 434 · 258 | 1 Dubrovsky · 2 Popova · 3 Dubrovsky, Slavsky · 4 Dubrovsky, Rabochy, Kuleshov, Slavsky · 5 Dubrovsky, Kuleshov · 6 Buldakov, L. Smirnova, Soviet Supremo, Medvedev · 7 Dubrovsky, Chanova, Sociedad Civil | 0.9859 | 189 |

El contador de personas cuenta instituciones y medios («Chelyabinsky Rabochy», «Sociedad Civil», «Soviet Supremo de la
URSS») como personas.

## 4. Decisión

- **Ficha: Sol.** Fable no produjo una ficha utilizable en cuatro llamadas, a 5–7× el costo. Le queda una prueba
  pendiente: ahora, con el JSON extraído del texto, fF1 habría pasado el parseo, porque terminó en 46k tokens.
- **Escaleta: Sol.** Los dos modelos pasan 1 de 2. Fable hace escaletas más densas (81 ids, 4.8 apoyos por beat), y eso
  se nota en el guion: +548 palabras y un bloqueante de largo, aunque tiene 10 citas contra 5. Su promesa trae un
  adelanto, y cuesta 7–10× más.
- **Guion:** sigue Fable.

## 5. La regla nueva para Claude (`claude_helpers.py`, tu pedido de esta tanda)

- **Streaming obligatorio y `max_tokens` 100 000:**
  - `MAX_TOKENS = 100_000`.
  - `_post` siempre manda `stream: true` y arma la respuesta con `leer_stream`, que convierte los eventos SSE en el mismo
    dict que la respuesta sin streaming.
  - Un error a mitad del stream (`overloaded_error`, `rate_limit_error`, `api_error`) se reintenta como un 529; cualquier
    otro → `ClaudeError`.
  - `TIMEOUT_S` pasa a ser por lectura del stream, no por la llamada entera.
- **Effort por etapa:** `ESFUERZO_POR_ETAPA = {"guion": "high", "ficha": "medium", "escaleta": "medium"}`.
  - El guion de producción ya usa high (`guion_v4.ESFUERZO`). Hoy ficha y escaleta usan Sol en producción, así que la
    tabla solo la lee quien arma un `call` de Claude para esas etapas (el runner de F25a).
- **Sin esquema en salidas grandes:** `SALIDA_GRANDE = ("ficha_caso",)` va sin `output_config.format`. Sin esquema, el
  JSON se extrae del texto con `json_del_texto`.
- **Tests:** `test_module_f25a.py` (5): stream armado, `_post` con stream y 100k, reintento por error en el stream,
  JSON envuelto, ficha sin esquema y effort. `test_module_f22d` pasa a `MAX_TOKENS == 100_000`.
- **Suite amplia: 860 verdes + las 5 previas** (3 `01b_pauses`, 2 `m03_merge_timing`).

## 6. Costo y tiempo

| etapa | llamadas | Claude US$ | OpenAI US$ | pared |
|---|---|---|---|---|
| 1 fichas (fS1, fS2 + los 400 de Fable) | 2 (+2 rechazadas en 0.5 s) | 0 | 0.7854 | 401 s (1.ª corrida) |
| 1 fichas Fable sin esquema, 32k | 2 | 3.9884 | — | 371 s |
| 1b fF1 con la regla nueva (fF2 frenada) | 1 | 2.7002 | — | 484 s |
| 2 escaletas (eS1, eS2, eF1, eF2) | 8 | 4.9409 | 0.5854 | 431 s (Sol, 1.ª corrida) / 551 s (Fable, 3.ª) |
| 3 guiones (gS1, gF2) | 2 | 1.9409 | — | 197 s / 196 s |
| **total** | **15 facturadas** | **13.5704** | **1.3708** | **2,637 s** |

## 7. Archivos

`lab/hyperframes/f25a/`:
- **Salidas:** `FICHA_fS1.md`, `FICHA_fS2.md` (Fable no dio ficha), `ESCALETA_eS1.md`, `ESCALETA_eF2.md` (eS2 y eF1
  rechazadas), `NARRACION_gS1.md`, `NARRACION_gF2.md`.
- **Por tag:** `<tag>/resultado.json` (métricas, log de llamadas, error), crudos de escaleta, fichas y escaletas en JSON.
- **Lo que falló:** `_fF1_400/`, `_fF2_400/` (HTTP 400) y `_fF1_32k/`, `_fF2_32k/` (cortadas en 32k).
- **Runner y costos:** `costos_f25a.json` (cada llamada con in/out/stop/US$/s), `f25a_corridas.py`, `run*.log`.

## 8. Veredicto del revisor-handoff

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Cifras del reporte = costos_f25a.json y resultado.json | OK | Recalculé: Claude 13.5704, OpenAI 1.3708, pared_total_s 2637.4 coinciden. Coinciden también métricas de fS1/fS2 (11 y 9 problemas, 17 y 13 citas verificadas), beats/ids/apoyos de eS1 y eF2, y palabras/bloqueantes de gS1 (1,499, 0) y gF2 (2,047, 1 por tope). |
| 2 | Topes (Claude 15, OpenAI 4) | OK | 13.57 y 1.37. El freno frenó fF2 (resultado.json de fF2: "13.570 + peor caso 3.368 > 15.00"). |
| 3 | Cero cambios de prompts y chequeos | OK | git status: solo claude_helpers.py y test_module_f22d.py tocados de esta tarea; researcher_steps y prompts no figuran. md5 de sistema (070b75df, 006a195f, 8ca9aa49) son los declarados. |
| 4 | Regla de claude_helpers | OK | MAX_TOKENS 100_000; _post siempre stream:true con leer_stream; ESFUERZO_POR_ETAPA guion high, ficha y escaleta medium; SALIDA_GRANDE=("ficha_caso",) sin output_config.format; json_del_texto; reintento de errores del stream. |
| 5 | Suite | OK | La corrí: 860 passed, 5 failed (3 01b_pauses + 2 m03_merge_timing, las previas). |
| 6 | Desvíos declarados | OK | HTTP 400 de Fable: existen _fF1_400/ y _fF2_400/. fF1/fF2 cortadas a 32k: en costos_f25a.json figuran con max_tokens y cortada True. eF1/eF2 sobre fS2: el campo "ficha" de sus resultado.json lo confirma. fF1 con la regla nueva terminó en end_turn con 46,119 tokens y se perdió por JSON (su resultado.json tiene error y no hay respuesta guardada). fF2 frenada. Hay 2 FICHA, 2 ESCALETA y 2 NARRACION de las 4 pedidas, y el reporte lo dice. |
| 7 | Entregables: tabla comparativa y tiempo de pared | PARCIAL | F25a_REPORT.md existe, con tablas y total 2,637 s. Faltan 2 FICHA, 2 ESCALETA y 2 NARRACION de los 12 archivos pedidos (por los fallos declarados). "Las cuatro a la vez" no se cumplió en la rehecha de fF1, que corrió sola. |
| 8 | Commit, revisor y PARADA | NO VERIFICABLE | Sin commitear a la fecha, como se anunció; §8 sigue en REVISOR_PENDIENTE. |

Observaciones:
- El freno reserva el peor caso por la salida acotada del runner, no por los 100,000 tokens (a US$ 50 por millón serían US$ 5.0). El tope duro de US$ 15 se cumplió, pero el freno no cubre el peor caso real de una llamada de Fable con la regla nueva.
- El tiempo de pared de 2,637 s es la suma de cuatro corridas (el reporte pone 1,035 + 371 + 747 + 484), no el reloj real de la tanda. No pude verificar los 1,035 y 747 s con resultado.json. eF1 y eF2 salieron en una corrida distinta de la de Sol.
- Comparación sesgada contra Fable: las escaletas de Fable corrieron con 32k y high, antes de la regla nueva, y las de Sol con high; ninguna usó la regla (medium). El guion gF2 se pasó del tope de 1,700 palabras. La decisión "Sol para ficha y escaleta" descansa en 1 ficha de Fable perdida por parseo (ya corregido en claude_helpers) y en 1 de 2 escaletas por modelo; el reporte lo admite parcialmente.
- gF2 figura con 196 s en §6 y 188.6 s en su resultado.json (196 es el máximo de la etapa 3, no un error).

Fuera de alcance: ninguno. diag_234_cap4.py y gfx_profiles/* aparecen modificados pero Omar ya los marcó como ajenos a esta tarea.

Riesgos que el contrato no cubre: la regla de 100k tokens con streaming deja el costo de una llamada de Fable casi sin cota (hasta US$ 5 cada una). SALIDA_GRANDE está fijada solo para ficha_caso, y cualquier otra salida grande va con esquema y puede repetir el HTTP 400. Sin esquema, el chequeo propio es la única defensa contra JSON mal formado, como pasó con fF1.
