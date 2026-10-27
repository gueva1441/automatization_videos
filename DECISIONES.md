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
- 2026-10-26 16:49 · **Antes de cada handoff, volver a derivar el orden:** ¿construye sobre código que ya decidimos reemplazar? ¿alguna decisión de hoy cambia el orden? Si sí, se reordena y el handoff viejo se archiva con la razón. La prisa es por un sistema que funcione, no por un render · «¿tiene lógica?» de Omar · vigente.
- 2026-10-26 22:26 · **Regla vital: casi nada hardcode.** Ningún número, lista de palabras ni valor de un tema metido en el código; todo arreglo es una **solución general** que sirve para cualquier tema y no se rompe con poco, nunca un parche para un video. Lo que no se puede derivar del material va al perfil del canal o del narrador con su origen; lo de un video solo se toca como edición de contenido sobre el papel (`--plan-edit`), nunca en código · Omar · vigente.
- 2026-10-26 22:32 · **Regla de trabajo: ante cada falla, primero «¿por qué pasa?» y el arreglo es una regla automática y general en el sistema.** Las cosas chicas las resuelve el analista con una regla general; a Omar le llega solo el papel en la compuerta y corrige solo lo que es gusto. Un error que se repite se arregla en la causa, nunca pidiéndole una edición a mano. El pipeline es casi full automático · Omar · vigente.
- 2026-10-27 00:30 · **RAM, no Firefox:** la regla «Firefox cerrado en todo render» (F2) se reemplaza por «antes de un render completo (`--gfx` sin `--plan-only`) medir la RAM libre; si es < 14 GB (umbral de F2), avisar y PARADA». CC nunca cierra programas de Omar; en `--plan-only`, tests y md5 no se mide ni se cierra nada · Omar · vigente.
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

- 2026-10-26 14:28 · **El gancho (ch01) nunca queda vacío.** El gancho no es pico a efectos del texto: 0–1 texto, 1 reloj, 1 sello; para el gancho los candidatos son todo el pool (lo que la voz no dice en el video), no solo los ítems de su beat · Omar · aplicada F34 (el modelo eligió D195 y el candado lo cortó por el año; ver revisión F34).
- 2026-10-26 14:36 · Vajont ch03: la ficha es la **fisura** (D49), no L'Unità · Omar · vigente.
- 2026-10-26 14:36 · **Nivel de agua sí**, con etiqueta: Pontesei «OLA | 20 m» (ch03) y «COTA AUTORIZADA | 715 m» (ch04) · Omar · aplicada F34.
- 2026-10-26 14:36 · **Fecha-hora sobre negro en el segundo 0** del video: «9 OCT 1963 · 22:39» antes de la primera imagen (promesa del cold open) · Omar · aplicada F34 en el plan; falta decidir qué pasa con la intro de 2.5 s (ver revisión F34).
- 2026-10-26 14:32 · Criterio rector: el video en papel se construye para **retener**; el analista siempre critica y propone algo mejor, nunca acepta un resultado vacío o débil como «así queda» · Omar · vigente.

- 2026-10-26 16:30 · **Sellos de clima los elige Sonnet en la misma llamada del rotulista** (ya tiene el relato del cap); Gemini Flash sale de los sellos (inclina a AMENAZA, nunca devuelve MEMORIA) · Omar · pendiente de tanda.
- 2026-10-26 16:30 · **Partir `gfx_rotulista.py` (1.911 líneas) en 5 módulos:** `rotulista_llm` (prompt + llamada), `rotulista_filtros` (candado, no dicho, spoiler, lectura, cantidad, en orden visible), `rotulista_colocar` (escenas, tiempos, ediciones), `clima` (sellos), `voz_datos` (reloj, agua, tarjeta); con los tests de F34 como red · «hay que corregir estructuras o vamos a estar en la misma cosa» · Omar · después de v6 y de los bugs 1–8.
- 2026-10-26 16:30 · **Fuera las listas de Vajont del código:** `UNIDAD_CONTADOR` («personas», «liras») y `AGUA_ETIQUETAS` (COTA AUTORIZADA, OLA…; la puso el analista en F34 A.5) → la unidad y la etiqueta vienen del modelo / de la oración, no de una lista · Omar · con la partición.
- 2026-10-26 16:30 · Números sin origen en el rotulista: altura del agua 15–85 % de la pantalla, reloj de 12 s (y sin mirar el corte) → se clasifican con los 66 de `gfx_config` · Omar.

- 2026-10-26 16:33 · **El rotulista recibe todo el pool con cifra/fecha/cita del video** (no solo los ítems que la escaleta asignó al beat), con la marca «este beat lo cuenta»; él elige y los filtros cuidan spoiler y repetición. `a_pantalla` de la escaleta deja de ser la única llave · Omar · tanda de estructura.
- 2026-10-26 16:33 · **El rotulista sabe cuánto cabe:** la entrada trae por oración los segundos hasta el próximo corte de escena y el prompt dice «en esta oración caben N caracteres» (N = segundos × 15 cps) · Omar · tanda de estructura. Menor: pasarle los detalles de `gfx_vision` para la lupa; `voz_antes`/`voz_video` van duplicados.

- 2026-10-26 16:35 · **El crítico va antes del reparto:** mira todos los candidatos (sellos y textos) y después corre «uno por beat / una por escena»; un sello que el crítico tira no ocupa lugar. A los sellos de clima solo les pregunta «¿estorba?» (tapa algo), no «repite» · Omar · tanda de bugs (bug 2).

- 2026-10-26 16:38 · **Borrar el código muerto en la tanda de estructura**, con sus tests: lo muerto de `gfx_peak` (plan_peak, water_level, time_ticker, zoom_latido, clear_around; `sentences`/`lexicon_hits` pasan a utilería de voz, `peak_word` a `clima`), `gfx_fragments`, `gfx_question`, `gfx_identity` del pipeline, `data_callout.html.tmpl`, `grade_css.html.tmpl`, y los «se llama y se descarta» del mapa. Dos lógicas para lo mismo no conviven · Omar · tanda de estructura.

- 2026-10-26 16:41 · **Vajont v6, confirmado por Omar (5 de 5):** gancho = D195 «LONGARONE · 1.269 de 1.328 habitantes murieron» (0:18, sin año en la etiqueta); sellos PÁNICO · CALMA + AMENAZA · AVISO · AMENAZA · INMINENTE · COLAPSO + SILENCIO · MEMORIA (fuera los AMENAZA de ch03, ch05, ch07); ch03 fisura en vez de L'Unità; ch06 1.910 muertos como ficha (812.7); la tarjeta fecha-hora reemplaza la intro congelada (3 s de negro, luego la primera imagen). Detalle línea por línea en `lab/hyperframes/f34/REVISION_GUION.md` · Omar · F35.

## Orden de tandas (acordado 2026-10-26 16:41)
~~1. F35: 15 ediciones a mano + render v6~~ · **descartado 16:45** («¿tiene lógica corregir v6 sobre módulos rotos?» — no: parchar la salida en vez de arreglar lo que la produce). El handoff queda en `lab/hyperframes/f35/` como archivado.
1. **F36 — estructura + bugs, en 4 partes con PARADA** (A partir el rotulista sin cambiar comportamiento · B los 8 bugs + tarjeta que se dibuje · C entradas nuevas y Sonnet elige sellos · D borrar zombis); cada parte se mide regenerando el guion de Vajont contra la tabla DEBERÍA de la revisión F34 (el contrato). Al final: guion → revisión → «aprobado» → render v6. `--plan-edit` solo para lo excepcional que quede.
2. **Bugs (ahora dentro de F36 B):** contador borrado por el realizador; crítico antes del reparto; AMENAZA repetido / MEMORIA nunca; agua y reloj contra el corte; `contradicciones` falso positivo; desempate por valor; candado del gancho; tope de caracteres.
3. **Estructura (ahora F36 A, C, D):** partir el rotulista en 5; Sonnet elige sellos; pool completo + «cuánto cabe»; fuera listas de Vajont; borrar zombis. Forma (F31b) se prueba en paralelo con clips de ch06, sin esperar el render.
3b. **F37 — el papel elige más y mejor, Fase 2 mueve en vez de cortar** (handoff `lab/hyperframes/f37/HANDOFF_F37_papel_y_colocar.md`); después: papel → compuerta de Omar → `--plan-only` → «aprobado» → render v6.
4. **Sesión Omar + analista:** clasificar los 66 números sin origen → `gfx_config` lee DECISIONES.
5. Forma (F31b), subtítulos, sfx, Kyshtym en seco.

- 2026-10-26 17:58 · **«Una por escena» pasa a «nunca al mismo tiempo»:** dos bloques (texto, sello, reloj, agua) no se solapan ni se tocan; la escena deja de ser la unidad (nació con escenas de ~10 s; Veo trae escenas de 40–100 s). Sin número nuevo. Reemplaza a «nunca dos en la misma escena» (02:52) · Omar · F36 C.
- 2026-10-26 17:58 · **Pico: solo `a_pantalla`, salvo que el beat pico no tenga ningún `a_pantalla`**; entonces el rotulista puede poner un texto no marcado (el pico sin texto es peor). Precisa la decisión 14:22 · Omar · F36 C.


## Catálogo definitivo de la capa gfx (Omar, 2026-10-26 18:17) — «compactar el rompecabezas»
Se quedan **9 componentes**; todo lo demás se **borra del código** (no se apaga), con sus plantillas, reglas, tests y entradas del perfil:
1. Title card con el título del cap (Fase 1 lo escribe; gfx lo dibuja; 3 s sin voz).
2. **Ficha** = el único bloque de texto; tres estilos que salen del tipo de dato sin modelo: *normal* (D/T), *papel* (documento/carta: ex recorte), *cita* (Q, con autor), *nombre* (P). El rotulista decide «ficha o nada», no el tipo.
3. Sello de clima (pocos; palabra del vocabulario del perfil; nunca la de la voz).
4. Reloj (fecha que dice la voz; forma pendiente F31b).
5. Pregunta de cierre del último beat.
6. Tarjeta fecha-hora en el segundo 0 (medir en v6).
7. Transiciones con razón: corte, zoom punch en el pico, fundido por beat/fecha, dip al cierre, negro entre caps.
8. Movimiento de foto (bake ffmpeg) + grano y viñeta.
9. Sfx: solo el golpe del title card.
**Se borran:** contador (`count_up` y plantilla), nivel de agua (`water_level` y plantilla; queda como idea opcional por tema, sin código), lupa (`evidence_zoom`, `gfx_vision.pick_zoom`; vuelve cuando haya imágenes reales), ícono por tema (`category_icon`, `icon_callout`, `icon_array`, `gfx_fragments`), marca del canal en gfx (`gfx_bug`; la llama va al outro), sfx por bloque (todos menos title card), `data_callout`, `grade_css`, `source_tag`, y en `rotulista` los tipos `lupa`/`agua`/contador y `animacion_de_cifra`.
Motivo: retención + costo de sostener; 19 componentes con 7 tipos de texto producían bugs que nadie veía (el contador estuvo borrado 3 tandas). Efecto en F36: C.4 (agua desde el modelo) **se cancela**; D crece con esta lista. Las líneas 7 (agua ch04) y 11 (contador D128) del contrato pasan: 7 fuera, 11 como ficha.

- 2026-10-26 19:54 · **El autor de la pantalla va a Fase 1:** paso nuevo `m01e_pantalla` después de la partición y antes de la voz; una llamada a Sonnet por video (narración de los 7 caps + escaleta + pool completo + títulos + vocabulario de clima) → guion de pantalla **en papel** (por beat: ficha o nada, sello o nada, relojes, tarjeta; ancla por oración, sin tiempos). Omar lo revisa antes de pagar voz e imágenes. La capa gfx deja de tener autor: ancla, mide si cabe, filtra, crítico de foto, coloca, dibuja. `rotulista_llm` de gfx se borra. Motivo: el contenido se decide donde está toda la información; el 80 % del problema era elegir, no colocar · Omar · F36 C/D reescritos.

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
- Sellos: se quedan como clima (14:22) · resuelto.

## Pendientes de infraestructura (acordados 2026-10-26 12:52–13:16)
- Mapa de módulos con flujograma y «stickers» de descripción por módulo; cada handoff declara módulos tocados.
- Hook que bloquea `fase2b --gfx` sin `GUION_PANTALLA.json` aprobado por Omar.
- `/tanda` en CC con PARADA corta por módulo; subagente simulador (reglas en seco contra los planes antes de programar).
- Este archivo leído por el código (`gfx_config` carga constantes desde aquí).
