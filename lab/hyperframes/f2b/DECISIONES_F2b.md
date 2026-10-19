# DECISIONES_F2b — decisiones conservadoras (modo autónomo)

Handoff: `lab/hyperframes/_handoff_adjuntos/HANDOFF_F2b_director_v2.md` · rama `f2-gfx-director` (base `0cc1997`).
Formato: # · sección · decisión · por qué.

| # | § | Decisión | Por qué |
|---|---|---|---|
| B1 | 1.1 | "Cifra" para el titular = número de ≥ 2 dígitos, o con decimales o %, que **no** sea año ni día de fecha ("29 de agosto"). | Con "cualquier número", el fact 0 elegía "como Templeman 1 y 2" y el fact 2 cortaba en "el 29". El año va al kicker. |
| B2 | 1.1 | Ventana de ≤ 8 palabras: si hay cifra, incluye la cifra **y la palabra siguiente** (unidad). Si para eso hay que correr el inicio, el titular puede arrancar a mitad de cláusula (p. ej. «partes de Nueva Orleans quedaron bajo 15 pies»). | El handoff pide la cláusula con la cifra; perder la unidad ("bajo 15") es peor que perder la primera palabra. |
| B3 | 1.1 | Bordes del titular: se quitan palabras funcionales al final (de, el, en, y…) y los paréntesis sin cerrar; una fecha nunca se parte (se corta antes). Nunca se agrega nada. | Sigue siendo substring literal del fact (pasa el candado por construcción; además se re-chequea). |
| B4 | 1.1 | Kicker = etiqueta de fuente del fact ("Organización, año", ya existente de §0d) si la hay; si no, el año del fact si no está ya en el titular; si no, vacío. | Spec "fuente del fact o año". La etiqueta es prefijo literal de `sources[]` (el candado la acepta). |
| B5 | 1.1 | Lo que el LLM mande como `headline`/`kicker` se **ignora** (el schema ya no los pide). Se mantiene la regla titular ≠ cuerpo. | Recorte determinista; el LLM solo elige fact y escena. |
| B6 | 1.2 | Ancla del zoom = `anchor_word_idx` + `anchor_len` (1–6 palabras de WORDS), dichas dentro de la escena del zoom (± 1 s antes, + 0.5 s después). Sin ancla válida → sin zoom (y sin llamada de visión). | "Zoom fuera del detalle narrado" era el problema; si la voz no nombra nada en esa escena, no hay qué acercar. |
| B7 | 1.2 | Umbral de confianza de visión `zoom_conf_min = 0.7` (token del perfil). Se aplica al leer el cache: cambiarlo no re-llama a Gemini. Cache por `escena|ancla`. | "Umbral de confianza explícito". 0.7 = conservador (ante duda, sin zoom). |
| B8 | 1.3 | `chapter_question` OFF en `misterio.json` (enabled=false). La regla sale del system prompt; el código y sus tests siguen (test con monkeypatch). | Spec 1.3. Deuda de guion: reactivar cuando m01b emita `cliffhanger` por cap. |
| B9 | 1.4 | `interrupt_max_sec` 35 → **18** y `interrupt_min_sec` 25 → **12** en el perfil (no en el motor). El orden del relleno queda callout → punch_in hasta que §2 agregue el énfasis de palabra adelante. | El perfil finanzas no cambia; el motor tampoco. |
| B10 | 1.5 | Filtro de visión del router = regex sobre `subject/action/gaze_interaction/prompt` del image_prompt (los prompts están en **inglés**; se aceptan términos EN y ES). En Orleans: 40/81 imágenes, 29 sin veredicto previo → 29 llamadas Flash vision (una vez; quedan en `zoom_verdicts.json`). Alto = `cara_closeup` (regla de §4 F2 sin cambios). | Spec "solo sobre imágenes cuyo prompt menciona persona/rostro/retrato/manos/cuerpo". No se agregó "sujeto_con_fondo + close" como high: no hay evidencia de que deforme. |
| B11 | 1.6 | `grain_opacity` 0.15 → **0.0** y `vignette_opacity` 0.20 → **0.15** en el perfil. Con grano 0 el disperso ya no genera ni aplica la textura (la rama existe pero no corre). **Revierte D21** en lo que hace al grano. | Look aprobado por Omar: grano 0, viñeta 0.15. |
