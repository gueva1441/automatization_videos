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
