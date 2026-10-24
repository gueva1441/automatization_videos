# HANDOFF F16 — Escaleta v2: 13 bloqueantes, oficio, Sol · Ycuá y Orleans completos

Analista · 2026-10-23 · Para CC. Base: `fa1d02b` (rama `f11-guion-v4`; seguí en la misma). Ficha → escaleta → guion. Sin producción.

## 0. Por qué (del disco)
- El guionista quedó cerrado con v5.1 (F15b): párrafos con escena, 0 preguntas, 0 analista, 0 inventos, Ycuá 8 y Orleans 8.
- El cuello ahora es la escaleta: 42 chequeos duros + 6 de preguntas (`m01a_escaleta.validate`, `question_problems`), con reintento por feedback hasta 3 veces. Es el mismo cuadro que tenía el guion en v3. En F15b rechazó Ycuá 7 veces por «la intensidad baja antes del pico» (el modelo puso el gancho con la escena más fuerte sin marcarlo flash-forward) y por «Liz Torres en escena con una cita sin verificar» (la protagonista con su propia cita). Elige un humano distinto en cada corrida (Reed → Pearl → Richard → Burton) y usó 1 escena de 14.
- Sigue en Gemini 2.5 Pro con un prompt de reglas.

## 1. Cambios
**1.1 Prompt de la escaleta v2** — `lab/hyperframes/f16/PROMPT_ESCALETA_v2.md` (md5 en el reporte). El bloque SISTEMA va **literal** como `system_instruction` cuando hay ficha; el usuario con la forma del archivo (caso, ficha completa con historia y escenas primero, tarea al final). Sin `escaleta_notas`, sin FEWSHOT viejo, sin `rules_text`, sin feedback. `PROMPT_VERSION = "f16-1"`. Sin ficha: byte-idéntico a hoy (test).
**1.2 Modelo:** la escaleta con ficha usa `gpt-6.1-sol` high por el mismo `call_for` del guion. El esquema de salida es el contrato de hoy (los mismos campos); `escena_idx` y `flash_forward` incluidos. Sin ficha: Gemini como hoy.
**1.3 Bloqueantes de la escaleta:** `m01a_escaleta.bloqueantes(esc, pool, ficha)` con los **13** del archivo (7 de estructura, 6 de datos), en código existente (son chequeos que `validate` ya tiene; se extraen tal cual). Si falla, **una** regeneración con los bloqueantes como feedback; si vuelve a fallar, PARADA. Todo lo demás de `validate` y `question_problems` pasa a `metricas_escaleta(esc, pool, ficha)` y se muestra. El camino sin ficha sigue usando `validate` entero (byte-idéntico).
**1.4 `writer_instructions` ya no se genera con ficha** (el guion v5 no las lee). Sin ficha, igual que hoy.

## 2. Corridas (ficha v2 re-chequeada de F15b, sin rehacer)
| tema | escaleta v2 (Sol) | guion v5.1 (Sol) |
|---|---|---|
| Ycuá | sí | sí |
| Orleans | sí | sí |
- Las escaletas anteriores no se pisan (`_f15`, `_f15b`). Salidas en `lab/hyperframes/f16/`: escaletas (.json y .md), `NARRACION_<tema>_f16.md`, `guion_<tema>_f16.json`, prompts con md5.
- **`compara_f16.html`**: por tema, F15b | F16 por cap (guion), y arriba la escaleta: humano, pico, beats por cap, escenas usadas, giros con beat, curva de intensidad, bloqueantes y métricas. Embudo pool → ficha → escaleta → guion.
- **Tope: US$ 2.00.**

## 3. Frenos
- Cero reglas nuevas en guion ni escaleta: los 13 bloqueantes son chequeos que ya existían; no se agrega ninguno.
- No tocar el pool, `research_v3`, `m05`, `evidence.py`, `guion_v3_reglas.py`, `config.py`, `topics_db`, `m03*`, `gfx_*`.
- Sin merge; no commitear `.env` ni `lab/_gpt_probe_analista/`.
- Tests sin red: sistema v2 byte-idéntico al archivo; sin ficha byte-idéntico a HEAD (los md5 de los dos temas); los 13 bloqueantes (un caso cada uno); una sola regeneración; métricas no rechazan. Suites verdes + las 5 previas; dorado de v3 verde.
- Actualizar `lab/ESTADO_SESION.md`.

## 4. Reporte `lab/hyperframes/f16/F16_REPORT.md`
1. md5 del prompt contra el archivo.
2. Por tema: humano y pico elegidos vs. los de la ficha; escenas y giros usados; bloqueantes; métricas que antes rechazaban y ahora solo se ven.
3. Tabla del guion F15b | F16 (palabras, minutos, párrafos, frases por párrafo, bloqueantes).
4. Costo y tokens.
5. Veredicto íntegro del revisor-handoff.

## 5. PARADA
Commit + reporte → **PARADA**. El analista revisa el diff (prompt literal, los 13 extraídos sin cambios, sin ficha intacto) y lee escaletas y guiones. Si Ycuá da ≥ 8 con escaleta y guion de una sola pasada, lo que sigue es producción.
