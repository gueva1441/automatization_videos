# HANDOFF F4b — Marca del canal + director inteligente (intensidad, fragmento, zoom, íconos gratis)

> Pegado por Omar en el chat (2026-10-20 12:00), guardado por CC.

**Fecha:** 2026-10-20 12:00 · **Analista:** chat proyecto · **Ejecutor:** CC (misma sesión F4) · **Gate:** Omar (una parada al inicio: elegir la marca; el resto autónomo) **Base:** `f3-lab-identidad` @ `56085d1` (F4 §1–§4 cerrados, video completo listo). El merge de F4 (§5) sigue esperando el OK de Omar; F4b se construye encima, en la misma rama, y se mergea junto. **Leer:** `lab/ESTADO_SESION.md`, `F4_REPORT.md`, `RESUMEN_NOCHE_F4.md`, `HANDOFF_F4_produccion_identidad.md`, `gfx_profiles/IDENTIDAD_misterio.md`, `script_engine/gfx_director.py`, `gfx_style.py`, `gfx_icons.py`, `zoom_judge`.

## 0. Por qué
Omar vio el video completo con identidad. Las formas están bien; lo que falla es **quién decide qué va dónde**: el titular del recorte lo corta una regla mecánica (sale "agua hasta el pecho" cuando lo fuerte era "agua putrefacta"), el zoom busca lo que dice la palabra y no lo que hay en la foto (zoomea aceite habiendo una herida en una mano), el pico solo existe en 2 de 7 caps porque el léxico es una lista corta, y los íconos solo salen para 12 palabras. F4b pone un LLM a **leer y elegir entre opciones literales** (nunca a escribir), un pase de visión a **mirar las fotos antes**, y una fuente gratis de íconos. Además, la marca del canal.

## §0 PRIMERO — Marca del canal (`channel_bug`) · PARADA ÚNICA de Omar
1. Generar 3 candidatos de la marca con el mismo pipeline de los 12 íconos (Flux.2 Pro, 1024², potrace): *"1890 woodcut engraving, hooded figure holding a lantern, three-quarter view, white ink on pure black, thick irregular engraved strokes, the lantern flame as the only lit detail, no text, centered, isolated"*. 3 semillas. La llama se separa en un `<g id="flame">` propio (para animarla y colorearla cálida `#e8a84a`).
2. Tira `tira_marca_canal.jpg`: los 3 candidatos a tamaño real de esquina (4 % de alto sobre un frame oscuro de ch02) y grandes (cierre de video). **Omar elige 1** (o pide otra tanda). CC espera esa respuesta y nada más; mientras tanto arranca §1 (no depende de la marca).
3. Implementación (tras la elección):
   - Esquina superior izquierda, 4 % de alto, opacidad 0.55, hueso; llama cálida.
   - Entrada: al inicio del video, la silueta aparece con `ink_bleed` 0.8 s y la llama se enciende 0.5 s después. Luego quieta. Cada 90 s, parpadeo leve de la llama (0.4 s). Nada más.
   - Se oculta durante: título de capítulo, pregunta de cierre, negro, nivel de agua, y cuando un bloque cae en esa esquina (ya existe el router de zonas: la esquina de la marca pasa a ser zona no disponible para los demás bloques; si un bloque la necesita, la marca hace fade 0.3 s).
   - Cierre de video (`outro_bug`): tras el último cap, 2.5 s: el encapuchado al centro a 25 % de alto, la llama parpadea y se apaga → negro 1 s. Sin texto. (El texto de cierre, si Omar lo quiere, se agrega después desde el banner: serif con espaciado.)
   - Todo sale del perfil del canal (`channel_bug` en `misterio.json`; `finanzas.json` sin marca hasta que tenga la suya). Token `channel_bug.enabled`.

## §1 Director de intensidad (reemplaza "pico solo con peso 3")
- Una llamada Flash por cap con la narración del cap (y la del anterior/siguiente como contexto corto). Devuelve JSON: `pico: {sentence_idx}`, `cargas: [{word, sentence_idx, categoria, peso 1–3}]` (3–5 palabras), `intensidad_por_frase: [0–1]`.
- Validador: `word` debe estar literalmente en la narración (misma flexión); `categoria` debe existir en el perfil (activas o reserva); peso 1–3. Lo que no pasa, se descarta. Si el LLM falla 2 veces → fallback al léxico actual (comportamiento de hoy).
- El léxico fijo queda como piso (siempre se aplica) y como mapa de íconos. Palabras nuevas que pasan el validador se guardan en `gfx_profiles/lexico_propuestas.json` con `{word, categoria, peso, video_id}`; cuando una palabra aparece en 2 videos distintos, entra sola al léxico del perfil (commit automático del JSON, anotado en el reporte).
- **Pico garantizado: 1 por cap**, en la frase de mayor `intensidad`. Si empata, la que tenga más cargas de peso 3. Regla de pico de F3 sin cambios (un bloque grande, nada ±5 s).
- Límites por cap sin cambios (máx 5 moods, 20 s entre moods de la misma categoría, etc.).
- Costo: cachear la respuesta cruda por `(video, cap, hash narración)`.

## §2 Fragmento literal más impactante (recorte, sello, dato)
- Para cada candidato a recorte / dato / sello en un tramo, el validador extrae **todos los fragmentos literales** de ≤ 8 palabras (ventanas por cláusula, cortadas en comas/puntos) del fact y de la narración del tramo. Lista numerada.
- Flash **elige un número** (y nada más) según: impacto emocional > concreción > brevedad. Si responde fuera de la lista → el primero (comportamiento de hoy). Prompt incluye 5 ejemplos: "agua putrefacta" > "agua hasta el pecho"; "6,500 almas" > "aproximadamente 6,500 personas".
- El fragmento elegido fija la **categoría** del bloque (vía léxico + cargas de §1): "putrefacta" → veneno/enfermedad → el recorte sale "con ícono" (calavera/biohazard del set, o game-icons §4) y el mood de esa categoría acompaña si no choca con límites.
- Candado literal intacto: todo texto en pantalla sigue siendo un fragmento exacto del fact o de la narración. Dedupe de titulares entre caps se mantiene.
- Tope: 1 llamada por tramo con candidatos (batch de todos los tramos de un cap en una sola llamada).

## §3 Zoom foto-primero
- Pase de visión por cap, **antes** del director: para cada imagen del cap, Gemini visión lista hasta 3 detalles zoomeables con recuadro y confianza: `{label, box, conf, tipo}` donde `tipo ∈ {rostro, manos, persona, objeto, texto, textura}`. Prioridad fija: rostro/manos > persona > objeto > texto > **textura (agua, aceite, humo, nubes) último y solo si no hay nada más**. Cache por `(image_hash)`.
- El director cruza detalles con narración:
  - Si la voz nombra el detalle (herida, mano, niño, rostro, puerta…) dentro del tramo → zoom ahí, anclado a la palabra (comportamiento de F2b, pero ahora con el box ya calculado).
  - Si no lo nombra pero hay un detalle `rostro|manos|persona` con conf ≥ 0.8 → **1 zoom por cap igual**, en la frase de mayor intensidad (§1) que caiga sobre esa foto. Es el "zoom de editor".
  - Prohibido zoom a `textura` salvo mención literal y sin detalle humano en la foto.
- El resultado alimenta el router: foto con `rostro|manos` → `deform_risk=high` y el movimiento base (acercar) apunta al box.
- Máx 1 zoom de evidencia por cap (sin cambios). El `zoom_judge` viejo queda como fallback si el pase de visión falla.

## §4 Íconos gratis automáticos (sin aprobación de Omar)
- Descargar una vez el paquete SVG de **game-icons.net** (CC BY 3.0, ~4,000 íconos) a `gfx_runtime/icons/game-icons/` (fuera del repo si pesa; registrar en `.gitignore` + script de descarga). Lucide ya está (MIT).
- Índice local `icons_index.json`: nombre del ícono → palabras en español (traducción + sinónimos; generarlo una vez con Flash a partir de los nombres en inglés, validar a mano una muestra de 50).
- Flujo: palabra de carga **concreta** (sustantivo dibujable; Flash marca `concreta: true/false` en §1) sin ícono en el set → buscar en el índice (palabra, lema, sinónimos) → **restilizar** al look del canal con el mismo pipeline que hoy restiliza Lucide (trazo irregular, hueso `#f2efe6`, rojo solo en el detalle semántico si lo hay, grano de tinta) → si no hay match, Lucide → si no, sin ícono.
- Los 12 propios tienen prioridad siempre. Flux solo por pedido manual de Omar.
- Crédito: línea fija en la descripción del video generada por el pipeline: *"Íconos: game-icons.net (CC BY 3.0) · Lucide (MIT)"*. Verificar dónde se arma la descripción (fase3) y agregarla.
- Prueba: correr sobre las palabras de carga de los 7 caps de Orleans y dejar `tira_iconos_auto_orleans.jpg` en el reporte (solo para que Omar vea; no bloquea).

## §5 Prueba completa y reporte
1. Re-correr el director sobre los 7 caps de Orleans (caché de Flash limpia para §1–§3) y re-ensamblar **incremental** (no render completo nuevo salvo que cambie > 4 caps; si cambia todo, un render completo, el único de F4b).
2. `AB_{id}_f4b.mp4` + cues + páginas de revisión.
3. `F4b_REPORT.md`: por cap: pico elegido (frase), cargas nuevas vs léxico, fragmentos elegidos vs el que salía antes (tabla antes/después), zooms (detalle, tipo, nombrado o "de editor"), íconos usados (propio / game-icons / Lucide / ninguno), marca del canal (dónde se ocultó), tiempos, Gemini (tope **$3** para toda F4b), veredictos íntegros.
4. `lexico_propuestas.json` con lo que salió de Orleans.

## §6 Candados
Lock literal (el LLM elige entre literales, nunca escribe; excepción `generated:true` solo para la pregunta) · sin shaders · sin rembg · `main` intacta (F4 §5 y F4b se mergean juntos con el OK de Omar) · tests verdes y revisor por sección · sin `--gfx` byte-idéntico en segmentos · un render completo máximo · marca del canal solo desde el perfil.

## §7 Orden
§0 (generar tira de marca → avisar a Omar) → §1 → §2 → §3 → §4 → (cuando Omar eligió: implementar §0.3) → §5 → `RESUMEN_F4b.md` (≤ 40 líneas, ≤ 3 preguntas con la opción ya aplicada). Modo nocturno: sin preguntar; decisiones conservadoras anotadas en `DECISIONES_F4b.md`. Estimación ~10 h de CC.
