# DECISIONES — registro único (Omar decide; fecha; motivo). Si no está aquí, no existe.

Formato: `fecha · decisión · motivo/contexto · estado (vigente / aplicada en FNN / pendiente de confirmar)`. Los números del pipeline tienen que apuntar a una línea de aquí, a un estándar citado o a un valor de la identidad (F3). El analista anota el mismo día; CC lee de aquí.

## Reglas de trabajo (vigentes)
- 2026-10 · Una variable por corrida; cada parte termina con la salida de su módulo en texto · aprender una cosa por vez · vigente.
- 2026-10 · Cero reglas de estilo nuevas en prompts de guion/escaleta/ficha («menos, no más») · las pilas de reglas no convergen · vigente.
- 2026-10 · Workers al máximo donde haya paralelo; render gfx en fila · vigente.
- 2026-10 · El validador de visión de imágenes queda apagado; QA manual en la galería · vigente.
- 2026-10 · Motor de imágenes Seedream por permisividad con contenido oscuro; cualquier cambio debe mantenerla · vigente.
- 2026-10 · No se publica nada hasta que fase 1 (semilla → guion) funcione desatendida · vigente.
- 2026-10-26 02:50 · **Ningún número hardcode en handoffs sin declararlo**: tabla de constantes con origen (Omar / estándar / valor existente / derivado) · «una burrada» · vigente.
- 2026-10-26 11:13 · **Texto antes que render, siempre**: guion de pantalla por `--plan-only`, revisión del analista con DEBERÍA por línea, OK de Omar, y recién ahí render · 4 h de render para ver 2 textos es inaceptable · vigente.
- 2026-10-26 11:16 · En la revisión, cada línea que no pasa lleva su DEBERÍA (texto, minuto, escena, fuente) sacado de la data bruta · vigente.
- 2026-10-26 12:43 · Después de cada tanda de CC, el analista dice primero qué pasó y de quién es cada falla; no escribe el siguiente handoff antes · vigente.
- 2026-10-26 13:20 · Comunicación: Omar avisa «CC terminó»; el analista lee ESTADO, reporte, diff y hojas del disco; los prompts para CC van en bloque de código · vigente.
- 2026-10-26 · Omar entiende mejor con flujogramas · vigente.
- 2026-10-26 · Sesión nueva de CC solo cuando Omar lo pide; la orden va primera y explícita («como en F25c») · vigente.
- 2026-10 · Todo reporte de CC pasa por el subagente `revisor-handoff` y su veredicto va íntegro; el analista además lee el diff, no solo el reporte · vigente.
- 2026-10 · Fase 1 (semilla → guion) se califica con una sola nota 1–10 y cada falla etiquetada «se queda / se arregla a mano / frena»; de ahí se decide si se pasa a imágenes/voz · vigente.

## Contenido en pantalla (gfx)
- 2026-10-25 · Regla de todo texto: (a) dice lo que la voz no dice, (b) sobre lo que la voz cuenta en esa oración, (c) sin adelantar · acordada · vigente.
- 2026-10-25 · El texto de pantalla lo escribe un paso nuevo dentro del gfx (rotulista, opción b), no la escaleta · no tocar fase 1 · aplicada F29b.
- 2026-10-25 · Catálogo de compuertas por tipo: cifra (con etiqueta), recorte/documento, cita literal, persona, lupa (detalle chico en la imagen), reloj (fecha), mapa (lugar; bloque futuro); ícono por **tema**; **sello = clima, la excepción**: no repite la voz ni el subtítulo · «punto crítico» de Omar · vigente.
- 2026-10-26 02:52 · **1 texto por beat** máximo; gancho 0–1; respiro y cierre pueden ir en 0; animaciones sin texto 1 por beat, nunca sobre un texto, nunca dos en la misma escena · «muchas animaciones aburren» · aplicada F29c.
- 2026-10-26 02:54 · Arranque del bloque en la **palabra clave** del dato · aplicada F29c.
- 2026-10-26 02:54 · **El data_callout (letras grandes sueltas) desaparece; todo texto adopta la forma del title card (ficha)**; recortes de prensa y citas se quedan como están · «solo me gusta el title card» · aplicada F29c.
- 2026-10-26 · Ficha un escalón más chica que el title card (dato al tamaño de la pregunta de cierre, etiqueta al del kicker con placa) · «los rótulos siguen grandes»; etiqueta roja medida 1.2:1 · aplicada F32 (pendiente de ver en render).
- 2026-10-26 14:22 · **Confirmado por Omar:** 2 `a_pantalla` en el mismo beat si van en escenas distintas; en el beat pico solo `a_pantalla`; ch01 sin pre-roll; la música del cap arranca con su title card · aplicado en F32 · vigente.
- 2026-10-26 14:22 · **Sellos se quedan, pocos, como clima.** Palabra de clima distinta de la palabra de la voz; vocabulario aprobado para Vajont: PÁNICO, CALMA, AMENAZA, AVISO, ALARMA, INMINENTE, COLAPSO, SILENCIO, RABIA, MEMORIA · Omar · vigente.
- 2026-10-26 14:22 · Reloj gana siempre al sello (información > clima) · Omar · vigente. **Forma del reloj:** a Omar no le gusta cómo se ven las fechas arriba («se ven pobres») → pendiente de forma (F31b).
- 2026-10-26 · Los `punch_in` (acercamientos) del director sobran: el único golpe es el `zoom_punch` del pico · aplicada F32.
- 2026-10-26 · En caps de una sola escena (Veo), la unidad es la oración, no la escena · propuesta del analista · pendiente de confirmar.

## Transiciones y costura
- 2026-10-25 21:48 · **Cada transición con razón nombrable; si no hay razón, corte.** Lupa → corte; pico → `zoom_punch` (reemplaza al flash); cambio de beat o salto de fecha → fundido 20 f (identidad F3); cierre de cap → dip 10 f (identidad); entre caps negro → title card → voz; `whip_pan_flash` fuera · aplicada F30b.
- 2026-10-26 11:02 · A Omar le gustó el zoom-punch (4:05 de v5) · las demás se notan poco (esperado) · vigente.
- 2026-10-26 11:02 · Las preguntas de cierre tienen que poder leerse → duración por 15 cps (estándar de subtitulado) · aplicada F32.
- 2026-10-26 · Title card con aire = `title_dur` (3 s, identidad) sin voz · aplicada F30b.

## Velocidad
- 2026-10-26 · F30 aceptado como está (desvíos de SSIM = cuadros de corte, dos escenas donde v3 estaba mal, encoder); metas de tiempo para después · aplicada.
- 2026-10-25 · 8 workers no mejoran (medido); se queda en 5 · aplicada F30 C.

## Subtítulos y forma (pendientes de Omar)
- Registro: karaoke (retención) vs documental (subs en la familia del title card, sin amarillo) · voto del analista: documental · **pendiente**.
- `«»…` fuera del `.ass` (Anton dibuja `»` como `>>`) · aplicada F30b C.
- Variante de forma de F31 (entradas/salidas V1–V3, sello S1–S3 con/sin placa, reloj R1–R2) · voto del analista: V2 + S2 con placa · **pendiente**.
- Sellos: ¿se quedan como clima o se van? · **pendiente**.

## Pendientes de infraestructura (acordados 2026-10-26 12:52–13:16)
- Mapa de módulos con flujograma y «stickers» de descripción por módulo; cada handoff declara módulos tocados.
- Hook que bloquea `fase2b --gfx` sin `GUION_PANTALLA.json` aprobado por Omar.
- `/tanda` en CC con PARADA corta por módulo; subagente simulador (reglas en seco contra los planes antes de programar).
- Este archivo leído por el código (`gfx_config` carga constantes desde aquí).
