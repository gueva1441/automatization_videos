# DECISIONES F4 — decisiones por defecto (modo nocturno)

Regla del modo nocturno: ante una decisión sin regla escrita, lo más conservador, anotado acá. Numeración D1…

## §0 — Adoptar la identidad guardada por Omar (01:20)
- **D1** `blocks.chapter_question.enabled` queda en `false` aunque el lab lo guardó `true`. La pregunta la genera `gfx_question` (C56); si el director la volviera a elegir habría dos preguntas. En `gfx_identity.apply_identity`, el ✔/✖ de «Pregunta de cierre» ahora prende/apaga `question_auto` en vez de `enabled` (así el próximo Guardar no la reprende).
- **D2** El perfil se reescribe en el formato compacto versionado (el lab lo había guardado con indent 1: diff de 700 líneas). Contenido = el de Omar salvo D1. `title_dur` 3 → 3.0: el lab manda enteros; `apply_identity` ahora convierte int → float cuando el token del motor es float.
- **D3** `black_hold_sec` queda en 1.0 s (el resumen dice 0.75 «anotado» = valor del catálogo, no elegido; el handoff acepta 0.75–1; Omar vio 1.0 en el render de ch02).
- **D4** Los 8 tests que fijaban la calibración F2 (acento `#c8102e`, golpe 1.025, cifras number_pop) pasan a los valores de la identidad. Respaldo del perfil anterior: `gfx_profiles/misterio.json.bak_f3_20261020_012038` (sin trackear).

## §1 — Pendientes de F3
- **D5** §1.1 (mood agua sin cáusticas, otros 3 moods sin patrón repetido) ya está en `d4ed4e5` con test que impide `repeating-*gradient`; no se toca. Falta la mirada de Omar (queda en el resumen).
- **D6** §1.2 pregunta: tope 8 palabras como token del perfil (`question_max_words_auto: 8` en misterio; el motor sigue en 12 para otros canales), validador rechaza abstractas por raíz (moral, destino, transformó, significado…), few-shot con las 3 de Omar en el prompt.
- **D7** ch02: la pregunta activa sigue siendo la de Omar («¿Quién fue el culpable?», plan dorado); la generada con el contrato nuevo queda en el reporte. ch05 usa la generada.
- **D8** §1.3 (video completo con pausas) se verifica en el ÚNICO render completo de §4 (regla nocturna: un render completo máximo).
- **D9** (revisor §1) «justicia»/«libertad» se suman a las abstractas; ch05 regenerada: «¿Cómo obtuvieron Waganfeald y Kunkel su indemnización?». Gasto Gemini §1: 3 llamadas Flash sin thinking (~1.5 k tokens c/u) ≈ US$ 0.002 (el cost_tracker no estaba abierto en el script suelto; se estima por tokens).
