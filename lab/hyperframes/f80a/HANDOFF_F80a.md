# HANDOFF F80a — reporte de SOLO LECTURA: qué amarra el pipeline al español, a los 13 minutos y al molde del guion

Fecha: 2026-11-10 · Analista → CC · Rama `f11-guion-v4` (no se crea rama) · Base: commit `c0cce6a`
Modelo sugerido: Opus medium.

## 0. Por qué
Omar abre un canal nuevo en inglés («Filed and Ignored»), con videos de 20 a 30 minutos, sobre este mismo repo. Español sigue siendo el modo por defecto y no se rompe. Antes de cambiar nada hace falta saber, con archivo y línea, qué está amarrado al español, a la duración actual y a la estructura del guion. Decisión de Omar: `DECISIONES.md`, línea `2026-11-10 21:44`.

Esta tanda no cambia nada: entrega un reporte. Las tandas que cambian código vienen después y salen de este reporte.

## 1. Reglas fijas
1. **Solo lectura.** No se edita código, prompts, config, datos ni tests. No se llama a ninguna API (US$ 0). No hay render, TTS ni corridas del pipeline.
2. Los únicos archivos que esta tanda crea o toca: `lab/hyperframes/f80a/F80a_REPORT.md` (nuevo) y una línea en `lab/ESTADO_SESION.md`. `DECISIONES.md` ya trae en el árbol de trabajo la línea del analista del 2026-11-10 21:44: se commitea tal cual.
3. Subagentes en paralelo, todos los que el trabajo permita (uno por sección como mínimo).
4. Búsquedas con `git grep` (con `timeout`); `grep -r` sobre el repo entero se cuelga por la carpeta `output/`.
5. Fuera del barrido: `lab/`, `_archived/`, `output/`, `data/`, los `test_*.py` (los tests se cuentan aparte, en la columna «tests que lo fijan»).
6. Lo que aparezca y no sea parte del contrato del §4 va a la sección «Fuera de alcance» del reporte. No se arregla ni abre trabajo nuevo.
7. Constantes de este handoff: ninguna. No hay números que decidir. Si el reporte necesita una cifra, sale de un archivo del repo y se cita la ruta.

## 2. Etapa 1 — inventario (un subagente por sección, en paralelo)

Cada fila de las secciones A a D lleva `archivo:línea` real y el texto corto de lo que hay ahí.

### A. Dónde está amarrado el español
Tabla: `archivo:línea` · qué es · tipo · tests que lo fijan · cómo se volvería dato.

Tipos (usar estos nombres):
- `prompt` — texto de sistema o de tarea para un modelo, escrito en español o que pide salida en español.
- `ejemplo` — ejemplos dentro de un prompt (el modelo copia lo que ve).
- `texto_pantalla` — texto fijo que termina en la imagen: sellos, relojes, meses, rótulos, title cards, plantillas gfx.
- `voz` — voz de ElevenLabs, perfil de audio, código de idioma, etiquetas TTS, normalizador (números a letras, abreviaturas).
- `karaoke` — subtítulos quemados: tokenización, `.ass`, fuentes, reglas de corte.
- `logica_idioma` — código que asume español: regex con palabras, detectores, conteo de años o cifras, palabras por segundo, anclas por trigrama, stopwords.
- `api_idioma` — parámetros de idioma o región a servicios externos (YouTube, Gemini, OpenAI, fal, ElevenLabs).
- `canal` — el literal «Misterios Sepultados», handle, playlist, descripción, firma.
- `rutas` — nombres de carpeta o archivo donde un segundo canal chocaría (`output/`, `data/scripts/_steps/`, `publish/`, docs).

«Cómo se volvería dato» es una de tres: `perfil` (un valor en un perfil por canal), `prompt_por_idioma` (hace falta un prompt hermano en inglés), `codigo` (hace falta lógica por idioma; decir cuál).

Mínimo a cubrir (no es la lista completa; es lo que el analista ya sabe que existe): `m01a_escaleta` (SYSTEM_V2, TAREA_V2, mensajes de `validate`), `guion_v4` (SYSTEM del guionista en producción y reparación), `m01b_guionista`, `m01c_editor`, `m01d_particion` (títulos), `m01e_pantalla`, `m01f` (crítico), `m05_narrative` (juez y `retencion`), verificador de narración, ficha (GPT), perfil y research v3 (R1–R3), `tts_tags`, `normalize_for_tts`, `audio_profiles`, `voz_utils`, m03 (prompts de foto y bloque PERSONAS), `foto_madre`, m09 y m09b (packaging y subida), director / rotulista / crítico de gfx, `gfx_templates/`, `pantalla_colocar`, `gfx_guion`, gate ES de `fase1` (`_measure_es`, `_verify_pick_es_saturation`, `already_es`), `niche_discoverer`, `estante`, QA Studio (textos del form y pestañas).

### B. Dónde está amarrada la duración
Tabla: `archivo:línea` · parámetro · valor de hoy · de dónde sale (config / default / literal) · qué lo consume.

Tiene que incluir: cada clave de `video_length.DEFAULTS` y de `config.long_video`; `CHAPTER_SCHEMA` (duraciones por rol); `palabras_objetivo` y cómo se escala; `min_beats`, `max_beats`, `MAX_BEATS_POR_CAP`; `max_images_per_video` y `_calculate_image_count`; los relojes de palabras por segundo que haya (el analista conoce tres valores distintos: listarlos todos con su uso); duraciones de clip del gancho y del cierre; tramos de música; cualquier tope de tiempo, tamaño o cantidad que un video del doble de largo pueda tocar.

Al final de B, una lista corta: «qué se rompe o se queda corto si el guion dobla su largo sin tocar nada» (con la fila que lo causa).

### C. Dónde vive la estructura del guion
C1. **El número 7.** Cada uso de `EXPECTED_CHAPTER_COUNT`, de `CHAPTER_SCHEMA`, de «siete capítulos» en prompts, de roles `hook` / `development` / `reveal_outro`, de `render_engine` por cap, de `DEFAULT_INTENT_BY_CAP` y de cualquier `range(1, 8)` o equivalente. Tabla: `archivo:línea` · qué asume · qué pasaría con otro número.

C2. **Las piezas del molde.** Omar aprobó quitar M1–M7 (línea de DECISIONES del 2026-11-10 21:44) y pidió, desde el 29-oct, análisis de impacto río abajo antes de quitar cualquier regla. Para cada pieza: dónde está el texto, qué test la fija byte a byte, y **quién lee río abajo lo que esa pieza produce** (campo de la escaleta o forma del guion → módulo que lo consume). Si nadie lo lee, se escribe «nadie» y se pega el `git grep` que lo demuestra.

| id | Pieza | Dónde |
|---|---|---|
| M1 | Regla 2 de la escaleta: «Sin contexto, sin año, sin cifras: lo que se ve.» y el flash-forward obligatorio | `m01a_escaleta.SYSTEM_V2` |
| M2 | Regla 3 de la escaleta entera (el cap 2 es la vida antes, el único cap tranquilo) | `m01a_escaleta.SYSTEM_V2` |
| M3 | Regla 5 de la escaleta: «después del pico, un respiro…» | `m01a_escaleta.SYSTEM_V2` |
| M4 | Regla 9 de la escaleta: «nunca "hoy"» | `m01a_escaleta.SYSTEM_V2` |
| M5 | `<ejemplo>` del faro (beat 1 sin nombre, cap 2 intensidad 1, cap 6 «respiro») | `m01a_escaleta.SYSTEM_V2` |
| M6 | `<errores>`: «la curva empieza alta, baja en el cap 2 y vuelve a subir» | `m01a_escaleta.SYSTEM_V2` |
| M7 | Guionista: `<estructura>` punto 1 («sin año, sin cifra, sin institución», «termina volviendo atrás»), punto 5 («nunca "hoy"») y el ejemplo de gancho de la vela | `guion_v4.py` |

Piezas atadas al molde que NO están aprobadas para quitar; solo se informa quién las lee: `BLOQUEANTES_V2` («loops… el principal en el cap 7 o en el pico», «recuerda_loop al cierre del cap 3»), `RECUERDA_LOOP_CAP`, `MIN_HUMAN_CAPS`, el campo `flash_forward`, `funcion` / `intensidad` / `pico` de cada beat.

Consumidores a rastrear como mínimo: `tts_tags`, música (matcher por intent y mapa de intensidad por beats), `m05`, `m01f`, `m01e_pantalla`, gfx (director, `gfx_layer`, `pantalla_colocar`), `m03`, QA Studio.

### D. Arreglos en espera
Fuentes: `lab/ESTADO_SESION.md`, `DECISIONES.md`, y la sección «abierto» de los `lab/hyperframes/f*/F*_REPORT.md` que ESTADO_SESION todavía dé por vigentes (F79 incluido).
Tabla: arreglo · fuente (archivo y sección) · grupo · por qué va en ese grupo.
Grupos: `también_inglés` (hace falta para sacar el primer video en inglés) · `solo_español` · `ya_no_aplica`.

### E. Tamaño del trabajo
Sin horas. Por bloque (perfil por canal · prompts en inglés · lógica por idioma · duración · carpetas por canal · estructura): cuántos archivos, cuántos prompts, cuántos tests byte-idénticos o de contrato se tocan, riesgo (bajo / medio / alto con el motivo) y de qué otro bloque depende. Cierra con un orden propuesto de tandas donde cada una deja el español igual que hoy (salida idéntica verificable) antes de sumar inglés.

### F. Costo real por etapa
De los archivos de costo que ya están en disco para Wittenoom y Colza (citar cada ruta). Tabla: etapa · US$ Wittenoom · US$ Colza · de qué depende (nº de fotos / caracteres de voz / nº de clips / fijo por video). Sin extrapolar a 25 minutos: eso lo hace el analista con Omar.

## 3. Etapa 2 — verificación entre agentes (antes de dar nada por hecho)
Dos verificadores en paralelo, cada uno un subagente con **contexto limpio**: no vieron hacerse el inventario.

- **V1 · filas.** Recibe solo el borrador del reporte. Abre cada `archivo:línea` de A, B, C y D y marca `sostiene` o `no sostiene` (y qué hay de verdad ahí). Revisa todas las filas, no una muestra.
- **V2 · cobertura.** No recibe el reporte al empezar. Hace su propio barrido del repo (mismas exclusiones del §1.5) buscando lo mismo que piden A, B y C1, por su cuenta. Después recibe el reporte y lista lo que él encontró y el reporte no trae.

Lo que V1 marque `no sostiene` se corrige o se quita. Lo que V2 encuentre de más se agrega, o se pone en «Descartados» con el motivo. Después se vuelve a correr el verificador que falló.

El lazo termina cuando una ronda sale sin fallas, o cuando una ronda no baja el número de fallas de la anterior: ahí PARADA con lo que queda listado.

## 4. CONTRATO (lo que el analista va a medir)
| # | Chequeo | Evidencia que debe traer el reporte |
|---|---|---|
| 1 | Cada fila de A–D tiene `archivo:línea` que existe y dice lo que la fila afirma | Tabla de V1: filas revisadas = filas que sostienen, por sección, y en qué ronda |
| 2 | A cubre todos los tipos del §2.A y todos los módulos del «mínimo a cubrir» | Lista módulo → nº de filas; un módulo con 0 filas lleva la frase «no tiene español» y el `git grep` que lo muestra |
| 3 | Nada del barrido independiente quedó sin clasificar | Tabla de V2: hallazgos propios · ya estaban · agregados · descartados con motivo |
| 4 | B trae todas las claves de `video_length.DEFAULTS` | nº de claves en el archivo = nº de filas de esas claves |
| 5 | C1 trae todos los usos del 7 | Salida de `git grep -n "EXPECTED_CHAPTER_COUNT"` (con las exclusiones) = filas de C1 de ese nombre |
| 6 | C2 trae M1–M7 con su «quién lo lee río abajo» | 7 filas; cada «nadie» con su `git grep` pegado |
| 7 | D clasifica todos los abiertos de F79 y de ESTADO_SESION vigentes | nº de abiertos en la fuente = nº de filas, por fuente |
| 8 | F sale de archivos reales | Ruta de cada archivo de costo usado |
| 9 | No se tocó nada más | `git show --stat HEAD` del commit de cierre: solo `F80a_REPORT.md`, `HANDOFF_F80a.md`, `ESTADO_SESION.md`, `DECISIONES.md` |

## 5. Etapa 3 — cierre
1. `revisor-handoff` lee handoff y reporte. Su veredicto va íntegro en el reporte. Sus observaciones que caigan dentro del contrato se corrigen antes de la PARADA; las de fuera van a «Fuera de alcance».
2. Un solo commit de documentos: `docs(F80a): reporte de solo lectura (español, duración, estructura, arreglos en espera, tamaño, costo)`.
3. Línea en `lab/ESTADO_SESION.md`.
4. **PARADA.** El analista lee el reporte y el diff; Omar decide el orden de las tandas.

## 6. Forma del reporte
`lab/hyperframes/f80a/F80a_REPORT.md`, en español llano, con tablas. Orden: resumen de 10 líneas (lo más amarrado, lo más barato de soltar, lo que más riesgo tiene) → A → B → C → D → E → F → Verificación (tablas de V1 y V2 por ronda) → Descartados → Fuera de alcance → veredicto del revisor.
