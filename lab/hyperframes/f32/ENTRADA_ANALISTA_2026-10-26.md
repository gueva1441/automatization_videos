# ENTRADA PARA EL ANALISTA — 2026-10-26 13:30 (reemplaza a la del 25)

Leé primero `DECISIONES.md` (raíz del repo / `claude/DECISIONES.md`), después esto, después `lab/ESTADO_SESION.md` (cabecera + F32) y `lab/hyperframes/f32/F32_REPORT.md` («lo que queda abierto» entero). Los skills `arranque-analista-pipeline`, `handoff-analista`, `revision-guion-pantalla` y `ver-render` traen el método; aquí va solo el estado.

## 1. Qué pasó del 25 al 26 (seis tandas de CC, todas CUMPLE CON OBSERVACIONES)
- **F29b/F29c — rotulista:** el texto de pantalla lo escribe Sonnet por beat, anclado a palabra, con candados; la ficha reemplaza al data_callout (forma del title card). Resultado en Vajont: **2 textos en 17 min**, por reglas del analista que se cancelan con el material (lectura 15 cps contra cortes de escena de ~10 s; una por beat; una por escena). El rotulista propone bien (16); los filtros matan 14.
- **F30 — render rápido:** bake de fotos con ffmpeg (`perspective`), transiciones en el stitch, NVENC. 64 → 37 min (ahora ~31–35). Metas (≤ 20 gfx) no alcanzadas; queda el bake (~80 s/cap).
- **F30b — transiciones por relato y costura:** corte por defecto, punch en el pico, fundido por beat/fecha, dip al cierre; entre caps negro → title card 3 s sin voz → voz; `«»` fuera del `.ass`. **Funciona y a Omar le gustó el punch.**
- **F31 — variantes de forma** (V1–V3 entradas, S1–S3 sello con/sin placa, R1–R2 reloj) detrás de `--forma-variante`; nada es default. Medido: el kicker rojo de la ficha da **1.2:1** de contraste (inaceptable).
- **F32 — guion de pantalla:** `fase2b --plan-only` escribe `output/<topic>/GUION_PANTALLA.md/.json` (200 eventos con quién cortó qué) + `mezcla_preview.wav`; `--plan-edit` aplica cambios sin re-llamar al modelo. **Desde ahora nada se renderiza sin guion revisado y OK de Omar.** También: preguntas de cierre por cps, pre-roll (la voz nunca perdió el ataque: era el golpe del title card encima), coherencia de cifras.

## 2. Estado del guion de Vajont (revisado el 26, 12:38–12:42; render NO autorizado)
- Semáforo: ch01 🔴 ch02 🔴 ch03 🟡 ch04 🟡 ch05 🟡 ch06 🟢 ch07 🟢. En pantalla: 2 fichas, 10 sellos, 1 reloj, 6 punches, 0 recortes, 0 agua, 0 lupa.
- **Causa principal:** el modelo escribe oraciones de 100–180 caracteres; la ficha es etiqueta + dato corto. Con eso vuelven ~6 de los 9 cortados. DEBERÍA por línea en la conversación del 26 (pasar a `lab/hyperframes/f32/REVISION_GUION.md`).
- **Bugs de reglas:** candado rechaza «1943» que la voz dice; «cuatrocientos» no se convierte a 400 (D237 debió caer por repetir, no por lectura); «Vajont» contado como spoiler; sello corta al reloj (9 OCT, 20 FEB); ch01 es **una sola escena** de 101 s (Veo) → «una por escena» mata todo; agua/lupa/contador **sin quién los proponga** desde F29b.
- **Sellos:** los 10 repiten la palabra de la voz (fuerza, vida, montaña…): cero clima. Vocabulario propuesto (PÁNICO, CALMA, AMENAZA, AVISO, ALARMA, INMINENTE, COLAPSO, SILENCIO, RABIA, MEMORIA) pendiente de Omar.
- **Música corrida** respecto del cap (ch02 4.6 s antes, ch07 14.8 s antes): previo a F32; hay que alinearla con el title card antes de renderizar.
- El render debe usar los planes aprobados (lock); el crítico de sellos en plan-only mira solo la foto.

## 3. Lo que sigue, en orden (acordado con Omar el 26)
1. **Infraestructura** (handoff por escribir): mapa de módulos con flujograma y «stickers» (descripción por módulo, nombres raros explicados); hook que bloquea `fase2b --gfx` sin `GUION_PANTALLA.json` aprobado; `/tanda` en CC con PARADA corta por módulo; subagente simulador (reglas en seco contra los planes antes de programar); `gfx_config` lee constantes de `DECISIONES.md`.
2. **Correcciones de reglas + ediciones del guion de Vajont** (sin render): ficha = etiqueta + dato 1 línea; arranque en escena siguiente si no cabe; candado/spoiler/números en letras; oración como unidad en caps sin cortes; reloj > sello; agua/lupa/contador con quién los proponga; música alineada; lock de planes. Regenerar guion → revisión → OK → render v6.
3. Forma (F31b con la variante que elija Omar; kicker legible), subtítulos (registro), sfx (oído de Omar), mapa (bloque nuevo), Kyshtym en seco, fase3.

## 4. Decisiones que esperan a Omar (ver `DECISIONES.md`)
Confirmar lo aplicado por voto del analista (2 `a_pantalla` por beat en escenas distintas; `a_pantalla` en el pico; ch01 sin pre-roll; música con el title card) · vocabulario de sellos · reloj > sello · registro de subtítulos · variante de forma F31 · ¿sellos se quedan?

## 5. Dónde está lo nuevo
- Guion: `output/f8s3-vajont-f30/GUION_PANTALLA.md/.json`, mezcla `_fase2b_work/mezcla_preview.wav`. Videos: `output/f8s3-vajont-f30/f8s3-vajont_final_gfx_v4.mp4` (rotulista) y `_v5.mp4` (+ transiciones y costura); `output/f8s3-vajont-f29/f8s3-vajont_final_gfx_v3b.mp4` (F30, mismos bloques que v3).
- Hojas: `lab/hyperframes/f29c/BLOQUES_v4.jpg`, `f30b/COSTURAS_v5.jpg`, `f31/VARIANTES_ch06.jpg` + clips `f31/ch06_<variante>.mp4`.
- Reportes: `lab/hyperframes/f29b|f29c|f30|f30b|f31|f32/F*_REPORT.md`. Handoffs también en `claude/`.
- Commits (rama `f11-guion-v4`): F29b `5ae6177`…`d7fac3c` · F30 `94d9496`,`537416f`,`7ac4ef8` · F29c `cc3f079`,`e852788` · F30b `7d0d0e5`,`6c5092c`,`a19dbbc` · F31 `0253672` · F32 `308032a`,`2fde994`,`cd60c74`. `DECISIONES.md` y esta ENTRADA están en disco sin commitear (van en la tanda de infraestructura).
- Análisis del 25 (`claude/ANALISIS_render_tiempo`, `ANALISIS_gfx_contenido_y_forma`): válidos como diagnóstico; su §5b (cifras de forma) quedó superado por F31.

## 6. Lo que ya aprendimos esta semana (resumen; detalle en el skill de arranque)
Simular las reglas contra los planes antes de mandarlas · quitar reglas, no apilar · informa > clima · un cap puede ser una sola escena · los filtros tienen falsos positivos conocidos · los caminos viejos no se borran solos · leer entera la sección «abierto» de CC · texto antes que render.
