# HANDOFF F11c — Prompt con la estructura oficial + Gemini 4 Argon vs GPT-6.1 Sol (Ycuá)

Analista · 2026-10-23 · Para CC. Base: `ae7b8dc` (rama `f11-guion-v4`; seguí en la misma). **Solo narración.** Nada de imágenes, voz, audio, m03, assemble, fase2a/2b, render, QA Studio ni producción.

## 0. Por qué
- **F11b** (Ycuá, todo leído del disco):
  - Los crudos de GPT tienen el largo justo y 0 bloqueantes, pero la voz suena a analista y cada «queda abierta» de la escaleta sale como pregunta literal (Sol mete 20 preguntas en 1,500 palabras).
  - Gemini se queda corto e inventa datos: «11:20», «600 °C» (en el pool, 600 es una cantidad de personas), «Murieron 327» (era de PANTALLA) y «el bombero Cristian Sosa».
  - El editor m01c les recortó 220–270 palabras buenas a los crudos que ya tenían 0 bloqueantes.
- **El modelo de Gemini es viejo.** El guionista usa `gemini_model_research` = `gemini-2.5-pro`, que es la misma variable del research.
- **El prompt no sigue la estructura que piden los dos fabricantes:**
  - **OpenAI**: el rol, el tono y las reglas van en el mensaje del desarrollador o sistema, y los datos de la tarea en el del usuario. El orden es Identidad → Instrucciones → Ejemplos → Contexto. A los modelos de razonamiento hay que darles metas, no pasos.
  - **Google**: el persona, las restricciones y el formato van en la instrucción de sistema. «Siempre incluir ejemplos.» Con contexto largo, primero todos los datos y la instrucción **al final**. Un solo formato de delimitadores. Gemini 3 o más nuevo responde directo: si querés estilo narrativo, hay que pedirlo explícitamente. No se tocan temperature, top_p ni top_k.
  - Lo que hacemos hoy: una sola línea de sistema; todo lo demás en el mensaje del usuario, con las instrucciones arriba; ningún ejemplo.

## 1. Cambios (es reordenar el prompt y cambiar el modelo; **ninguna regla nueva**)

**1.1 Prompt v4 reestructurado** (`guion_v4.py`, `PROMPT_VERSION = "f11c-1"`). Es el mismo para los dos modelos y usa delimitadores XML en los dos.

- **Sistema / desarrollador** (va en `system_instruction` en Gemini y en el mensaje `system` en GPT):
  ```
  <rol>Sos el guionista de Misterios Sepultados, un canal de documentales de historia oscura en YouTube, en español neutro.
  Escribís la narración en off que escucha el espectador. Tu meta: que no se vaya. Contás una historia real con un
  humano con nombre, escenas concretas y suspenso; no explicás ni analizás. No inventás: toda cifra, fecha, hora,
  nombre y cita sale de los datos que te dan.</rol>
  <voz>Narrativa y cinematográfica. Presente o pasado cercano. Frases cortas cuando algo golpea. Lo que se ve, se oye,
  se huele. El narrador no habla de sus fuentes ("los datos", "el testimonio señala", "la frase indica") ni del video.</voz>
  <oficio>
  1. Gancho: la imagen del beat 1; después, la promesa.
  2. Seguimos a un humano con nombre.
  3. Frases cortas antes del golpe.
  4. Cita literal, 25 palabras o menos, con quién la dijo (la marcada SIN VERIFICAR va sin el nombre).
  5. Hechos, citas y alguna pregunta; no juicios.
  6. La fecha completa, una vez; después, "ese día", "esa noche".
  7. Lo marcado PANTALLA no lo dice la voz.
  8. La última frase es una cita o una pregunta.
  </oficio>
  <ejemplos_de_voz> (solo la voz; los hechos son de otro caso y no se usan)
  El 30 de agosto, el agua sucia de la inundación irrumpió en las celdas. Olía a una mezcla de aguas residuales y
  combustible diésel. En varios pabellones, los presos quedaron atrapados en sus celdas cerradas. Vieron cómo el
  nivel subía sin poder hacer nada. Pronto, el agua les llegaría hasta el pecho.

  El oficial Renard Reed también fue testigo. «Parecía que estaban abatiendo a la gente», dijo Reed. Vio a alguien
  caer al agua. No sabía si la munición era real o de goma. Fue suficiente. Lo vio.
  </ejemplos_de_voz>
  ```
  (Los dos ejemplos son párrafos 10 y 14 de `lab/hyperframes/f7/NARRACION_orleans_v3r3.md`, F7c-3, nota 8.5. Copialos literal desde ese archivo.)

- **Usuario** (los datos primero, la tarea al final):
  ```
  <caso> tema, humano (nombre y rol), promesa del gancho, pico, cierre humano </caso>
  <escaleta> por cap: «CAP n · ≈ N palabras»; por beat: función, emoción, imagen, dato central, apoyos, cierre,
             y «el espectador se pregunta: …» (antes «queda abierta»: es un dato para vos, no una frase para decir) </escaleta>
  <tarea>Con lo de arriba, escribí la narración completa en párrafos, cada uno con su beat. Cada cap, cerca de sus
  palabras (es su largo, no un máximo); el video completo ≈ {total} palabras. Devolvé el JSON del esquema.</tarea>
  ```
- Las marcas de los datos quedan como en F11b (VERIFICADA, SIN VERIFICAR (sin nombre), PANTALLA, CIFRA OFICIAL), y también la excepción del humano para Q20.

**1.2 Modelo propio del guionista.**
- `--modelo gemini-4-argon` usa un `call` con ese modelo para toda la cadena v4: guionista, regeneración y edición de oración.
- Va como parámetro o config **del guion v4 solamente**. `gemini_model_research` y todo el research no cambian.
- No se pasan temperature, top_p ni top_k. Thinking queda por defecto.
- Primero, una llamada mínima de humo para confirmar que tu llave acepta `gemini-4-argon` (cuenta de pago). Si no lo acepta, PARADA y se reporta; no lo reemplaces por otro modelo.
- Costo: precio oficial vigente (`gemini-4-argon` US$ 2 / 10 por millón de tokens hasta el 30 de noviembre; fuente: ai.google.dev/gemini-api/docs/pricing).

**1.3 Sin el editor m01c en v4 cuando el crudo tiene 0 bloqueantes.**
- Si el crudo tiene bloqueantes, la ronda única de F11b se hace igual: regeneración del cap + edición de la oración. El m01c solo se saltea cuando no hay bloqueantes.
- No se agrega nada; se saca un paso.

## 2. Corridas (solo Ycuá `f8s1-ycua-bolanos`, `01a_escaleta_v1.json`, md5 `e1ba1a48…`, sin notas)
| corrida | modelo | esfuerzo |
|---|---|---|
| `_v4c_argon` | `gemini-4-argon` | por defecto |
| `_v4c_sol` | `gpt-6.1-sol` | `high` |
- **Mismo prompt exacto** para las dos: guardá el sistema y el usuario una sola vez en `prompt_ycua_v4c_{sistema,usuario}.txt`, con su md5.
- Salidas en `lab/hyperframes/f11c/`: `NARRACION_ycua_v4c_<modelo>.md` (crudo y final) y `guion_ycua_v4c_<modelo>.json`. No se pisa nada anterior y no se escribe en `topics_db`.
- **`compara_f11c.html`**, con la misma forma que `compara_f11b.html`. Filas: v3 (v1), F11b sol crudo, F11b astra crudo, v4c argon y v4c sol (crudo y final).
  - Agregá una columna **«preguntas»** con el conteo de signos «?» (es métrica; no rechaza nada).
  - Agregá una columna **«frases de analista»** que solo cuente las expresiones que el analista ya marcó en F11b: «los datos», «el testimonio», «la frase señala», «no permiten explicar». Es métrica para el reporte, no un bloqueante.
- **Tope: US$ 1.50.**

## 3. Frenos
- Igual que F11 §3 y F11b §3: solo narración, **cero reglas nuevas** (ningún bloqueante nuevo), los archivos prohibidos no se tocan, sin merge, no correr `f10_quirurgico_ycua.py`, no commitear `.env` ni `lab/_gpt_probe_analista/`.
- `gemini_model_research` y `config.py` no se tocan.
- Tests: el test dorado de v3 sigue verde. Tests nuevos (sin red): la estructura del prompt (el sistema trae rol, voz, oficio y ejemplos; el usuario termina en `<tarea>`), el modelo del guionista separado del de research, y que m01c se saltee cuando hay 0 bloqueantes. Suites verdes + las 5 fallas previas.
- Actualizar `lab/ESTADO_SESION.md`.

## 4. Reporte `lab/hyperframes/f11c/F11c_REPORT.md`
1. La tabla resumen.
2. Tokens del prompt (sistema y usuario) y costo por corrida.
3. Lo que hizo la ronda de reparación, si hubo.
4. Aparte, sin tocar nada: **Paiva hijo**. El pool tiene D20 «Emiliano Paiva, hijo del dueño, 10 años» y también la acusación contra «Víctor Daniel Paiva». Citá las fuentes de las dos (doc_id y offset) para que Omar decida antes de producir.
5. El veredicto íntegro del revisor-handoff.

## 5. PARADA
Commit + reporte → **PARADA**. El analista lee los dos crudos y los dos finales y le da a Omar la nota y la comparación antes de que Omar los lea.
