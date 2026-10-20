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

## §2 — El director aplica la identidad
- **D10** Todo lo de §2 cuelga de un token nuevo, `identity_rules` (motor: false = F3 tal cual; misterio: true). Así `finanzas` y los tests de F3 no cambian y el md5 sin `--gfx` no se toca (la capa solo corre con `--gfx`).
- **D11** Movimiento por foto (`gfx_style.movement_for`): quieta solo con texto en la imagen; alejar en la primera y la última foto del cap («apertura/cierre»); 3D en planos anchos de lugar (queda el clip DepthFlow); paneo en planos anchos con gente; acercar en todo lo demás. Las formas no 3D van como movimiento seguro sobre el PNG (igual que en el lab). Si el router de deformación ya marcó la foto (riesgo alto / Ken Burns), manda el router. Solo motor flux; Veo e híbrido no se tocan.
- **D12** Transiciones: fundido cruzado 20 f por default (`crossfade_frames`); corte si el plano entrante o saliente dura < 3.5 s («ritmo rápido», `fast_cut_sec`) o si la foto siguiente es del mismo lugar (setting del prompt con Jaccard ≥ 0.6); corte forzado si las 2 anteriores no fueron corte (≥ 1 cada 3; flash cuenta como corte); flash solo en R1 con el tope del perfil (2 y 20 s de separación), si no «corte + golpe»; 1 fundido a negro por cap en la primera escena R3 después de los 10 s; corte seco después del zoom (regla F2). Las transiciones quedan en `plan["transitions"]` y las usan el templater, el disperso y las cues.
- **D13** Golpes de zoom: candidatos = los del director + palabras del léxico con peso ≥ 2 + disparadores de datos; puntaje = peso (+2 dato, +1 propuesto por el director); máx 4, uno por frase, nunca a ±5 s del pico, nunca durante el título. `blocks.punch_in.max_per_cap` 2 → 4 para que el director pueda proponer 4.
- **D14** Reloj: `ticker_min_times: 2` en misterio (handoff §1.1: «solo si ≥ 2 horas verificadas»). En ch02 el reloj de fecha que Omar aprobó deja de salir; el handoff manda sobre el plan dorado.
- **D15** Sello dentro del bloque de ícono: token `icon_stamp_px` (112 = M) separado del sello suelto (`emphasis_stamp_px` 84 = S).
- **D16** El plan dorado va como few-shot en el prompt de sistema del director (`system_prompt()`), con la frase «las formas las pone el sistema». `DIRECTOR_VERSION` v1.5 → v1.6: los 7 caps re-llaman a Flash una vez (cache por versión).
- **D17** Bug encontrado: el render disperso no corría al timeline de ventanas el nivel de agua, el reloj, el corte a negro ni el latido (F3 solo se había probado sin disperso). Arreglado en `gfx_sparse` con test.
- **D18** `IDENTIDAD_misterio.md` pasa a `gfx_profiles/` (versionado, §4 del handoff, adelantado porque el pedido de Omar lo nombra ahí); el lab ahora lo escribe ahí. Se commitea también `misterio_golden_ch02.json` (lo lee el few-shot).
- **D19** `--hw-encode` no se usa en §4: NVENC midió 48.7 dB (< 50) en F2 y no hay medición nueva.

## §3 — Golpe de zoom / empuje / corte+golpe sobre clips de video
- **D20** Antes de cambiar código se midió (5 pruebas, `lab/hyperframes/f4/s3/README.md`): en el render y en el snapshot de HyperFrames 0.8.172 el contenedor `#vw` SÍ escala el clip de video (el frame inyectado es hermano del `<video>` dentro de `#vw`). Hasta el render de F3 anterior al arreglo C64 estaba acercado. Por eso el golpe de zoom, el empuje de muerte y el corte + golpe ya escalaban el video; no hacía falta tocarlos.
- **D21** Lo que sí se cambió: el zoom de evidencia deja de tapar el clip con un cuadro congelado en producción (token `zoom_freeze_frame`, motor false), así DepthFlow/Veo siguen moviéndose durante el zoom, como pide el handoff. El preview del lab lo conserva (true): ahí no se pudo verificar el player del navegador y es donde se vio el problema en F3.
- **D22** Verificación en ch01 (Veo) y ch04 (3D) con `--only-cap` (renders parciales permitidos); el render completo de §4 reusa esas capas.
