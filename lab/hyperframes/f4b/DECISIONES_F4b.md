# DECISIONES F4b — decisiones por defecto (modo nocturno)

## §0 Marca del canal
- **E1** Pipeline de los 12 íconos (Flux.2 Pro, semillas 1441–1443, potrace) en `script_engine/gfx_icons/make_bug.py`. La llama salió dibujada en blanco (no en color), y el criterio de «mancha más brillante» elegía la capucha: la llama se ubica con visión (`judge_zoom_box`, 1 llamada por candidato, cacheada en `bug_raw/*.flame.json`) y se toman los píxeles claros dentro de esa caja. La silueta se traza sin la llama; la llama va en `<g id="flame" fill="#e8a84a">`.
- **E2** La marca no lleva el acento rojo que el trazado de íconos agrega a un hueco: el único color es la llama.
- **E3** Candidato 3: el t2i dibujó además una vela en la mano; visión eligió esa llama (la más visible).
- **E4** Sin scipy/OpenCV en el venv: el etiquetado de manchas se hizo con numpy (no se instalan dependencias nuevas de noche).
- **E5** Tira: fondo nocturno de ch02 (96 s). Gasto: 3 imágenes fal ≈ US$ 0.09 (fuera del tope Gemini) + 4 llamadas de visión.

## §1 Director de intensidad
- **E6** `script_engine/gfx_intensity.py`, token `intensity_director` (misterio true). Las frases que ve el LLM son las mismas que usa el pico (cortadas sobre las palabras con tiempo de Whisper), así el índice de frase coincide.
- **E7** Las cargas de categorías de RESERVA (sin capa: silencio, caos, abandono…) se validan y se guardan como propuestas, pero no generan mood (no tienen capa que dibujar). Solo las de categorías activas se suman al léxico del cap.
- **E8** El LLM pone la intensidad más alta hacia el final de cada cap (cierre de suspenso). Para no perder el nivel de agua aprobado en ch02: si una frase con cifra de agua está a ≤ 0.1 de la intensidad máxima, el pico va ahí (`WATER_PEAK_TOL`).
- **E9** Pico garantizado: siempre se marca la frase; el bloque grande es (en orden) nivel de agua → zoom con latido (si visión da caja en esa escena) → recorte cercano → el mood + sello de esa frase. Si no hay ninguno, el pico queda marcado sin bloque (se anota en el log).
- **E10** La promoción al léxico del perfil edita `misterio.json` con una inserción mínima (sin re-formatear el archivo). Commit del JSON: lo hace CC en la sesión (no se commitea desde el pipeline durante un render).
- **E11** Prueba sobre Orleans (`intensidad_orleans.json`): 7 llamadas Flash; en ch04 el validador descartó «sin voz» (no es una palabra, son dos).
- **E12** «3–5 cargas»: el tope 5 se aplica; si solo 1–2 cargas son literales, se aceptan esas (descartar las válidas para forzar 3 sería peor).
- **E13** 5 de 7 picos caen en la última frase (el LLM sube la intensidad hacia el cierre). No se corrige con una regla nueva de noche: se ve en el render de §5.

## §2 Fragmento literal más impactante
- **E14** `script_engine/gfx_fragments.py`, token `fragment_director`. Corre después del plan (cuando ya se sabe en qué tramo cae cada recorte/dato) y antes del pico; después se vuelve a pasar el candado literal. Una llamada Flash por cap, cacheada por prompt.
- **E15** Recorte: opciones del fact + de la narración del tramo SOLO si comparten una palabra de contenido con el fact. Sin ese filtro, la narración cambiaba el sentido del documento («quinientas vidas» sobre un fact de 6,500 personas). Con el filtro entra «agua contaminada subió implacable».
- **E16** Dato: opciones del fact y de la narración ±4 s, como mucho 1 palabra más que hoy, con TODAS sus cifras y nombres propios (si no, «Templeman 1 y 2» quedaba «Templeman 1»). Años y fechas no se tocan (el sello ya es el dato justo).
- **E17** Bordes: sin palabras funcionales ni verbos conjugados/gerundios/infinitivos en los extremos (salían «inmundo alcanzando», «Human Rights Watch denunció»), y una fecha nunca se parte («tocó tierra el 29»).
- **E18** El sello rojo no pasa por §2: es una sola palabra y ya la eligen el léxico + §1. El mood de la categoría del fragmento no se agrega aparte (lo pone el énfasis si la palabra se dice): solo el ícono del recorte/dato.

## §3 Zoom foto-primero
- **E19** `script_engine/gfx_vision.py`, token `photo_first_zoom`. Imagen que mira visión: la foto original (PNG) en caps de fotos; el cuadro del base al empezar el zoom en caps Veo/híbridos. Cache por hash de la imagen en `output/<video>/assets/photo_details.json`.
- **E20** Con el pase de visión disponible, el zoom que propuso el director (o el zoom_judge) se descarta y decide la foto: pico (si visión da caja en esa escena: nunca textura) → nombrado → de editor. El zoom «fuera del pico» por palabra de peso 3 de F3 se apaga en este modo (elegía cualquier detalle aunque la voz no lo nombrara). Sin visión → todo como en F4.
- **E21** «Nombrado» = una palabra de la voz dentro del tramo comparte raíz con el label del detalle o es sinónimo de su tipo (mano/manos/dedos; rostro/cara/ojos; niño/preso/cuerpo…).
- **E22** Router: foto con rostro o manos → movimiento seguro sobre el PNG (riesgo alto) con el acercar centrado en la caja (`transformOrigin` = centro del detalle). El centro de la caja no se mueve al acercar, así el zoom de evidencia cae en el mismo lugar.

## §4 Íconos gratis
- **E23** game-icons se baja del repo oficial (`github.com/game-icons/icons`, 4.239 SVG, 22 MB) con `script_engine/gfx_icons/fetch_game_icons.sh` a `script_engine/gfx_runtime/icons/` (en `.gitignore`). El índice `gfx_profiles/icons/icons_index.json` sí se versiona.
- **E24** Restilizado: se saca el cuadrado negro de fondo, relleno hueso `#e8e0cc`, y el filtro de tinta + secado del set propio (`scoped_svg`). Sin rojo: game-icons no marca un «detalle semántico» y pintarlo a ojo sería inventar.
- **E25** Lucide: en el repo solo están los 12 SVG de respaldo del set (no el paquete entero), así que el paso «si no hay match → Lucide» casi nunca encuentra algo. No se bajó Lucide completo (no lo pide el handoff); queda anotado.
- **E26** Solo palabras de carga marcadas `concreta: true` por §1 buscan ícono automático (moods sin ícono propio y recortes/datos sin ícono). El tope de 3 bloques de ícono por cap sigue.
- **E27** Crédito «Íconos: game-icons.net (CC BY 3.0) · Lucide (MIT)» al final de la descripción que genera m09 (`_normalize_metadata`), una sola vez.

## §0.3 Marca (implementación, antes de la elección)
- **E28** La marca se compone en el COSIDO FFmpeg del render disperso (`gfx_sparse.stitch` + `gfx_bug.py`), no en HyperFrames: así está en todo el cap (también fuera de las ventanas) y se puede cambiar sin volver a renderizar HyperFrames. Sin `channel_bug.enabled` en el perfil no hay marca (finanzas no la tiene).
- **E29** Entrada «ink_bleed» de 0.8 s aproximada con aparición de opacidad (en FFmpeg no hay tinta); la llama se enciende 0.5 s después. Solo en ch01.
- **E30** Parpadeo «cada 90 s» medido por cap (el cosido no conoce el tiempo absoluto del video): a los 45 s de cada cap y cada 90 s desde ahí.
- **E31** Se esconde con fade de 0.3 s en: título, pregunta + negro, nivel de agua, cierre, y bloques del lado izquierdo de arriba (datos, recortes, contador, reloj, bloque de ícono).
- **E32** Cierre del video: el último cap (sin pregunta) se alarga 2.5 + 1 s con la misma pausa de F3 (fase2b rellena audio y música).
- **E33** Elegir el ícono con una regla mecánica sobre el índice salía mal: «agua» daba la molécula H2O y «cadáver» un pez muerto. Ahora Flash elige un número entre los candidatos del índice, mirando la frase, o 0 si ninguno dibuja la palabra (`choose_icons`, caché por palabra en `gfx_profiles/icons/auto_choice.json`). El «buscar en inglés» solo acepta un archivo con ese nombre EXACTO: las coincidencias parciales traían «shadow-grasp» para penumbra y un jabón líquido para «líquida».
- **E34** Validación a mano de 50 entradas del índice (semilla 50): ~45 bien traducidas; fallan los nombres compuestos que se parten en dos palabras («lightning-spanner» → «llave», «inglesa»; «card-5-diamonds» → «cinco», «diamantes»). Lo compensa la elección por Flash con la frase.
- **E35** La tira de Orleans suma los sustantivos dibujables más frecuentes de la narración (demo, con caché aparte `lab/hyperframes/f4b/auto_choice_demo.json`). En el pipeline solo entran las cargas `concreta: true` de §1: en Orleans fueron 3 («agua» ya tiene ícono propio; «penumbra» y «líquida» quedan sin ícono).
- **E36** (§3) «Nombrado» = la voz dice el sustantivo PRINCIPAL del detalle (1ra palabra del label) o un sinónimo de su tipo; para texturas vale cualquier palabra del label (el material). Con cualquier palabra, «insecto en agua» se elegía porque la voz decía «agua». Orden final: nombrado (no textura) → de editor (humano, frase más intensa) → textura nombrada.
- **E37** (§3) Verificación del recorte: antes de usar un zoom, visión mira la caja recortada (margen 5 %) y confirma que el detalle está en el centro y ocupa la mayor parte; si no, pasa al siguiente candidato (máx 3). Sin esto, 2 de 7 zooms de Orleans caían en barrotes al lado de las manos. Cache en `assets/zoom_verify.json`. Un fallo de visión queda anotado en la cache (esa escena sin detalles) para no reintentarlo en cada render.
