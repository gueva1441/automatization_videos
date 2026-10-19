# HANDOFF F3 — Laboratorio interactivo de identidad (ch02)

**Fecha:** 2026-10-19 · **Analista:** chat proyecto · **Ejecutor:** CC · **Gate:** Omar (usa el lab, marca casillas)
**Base:** `f2-gfx-director` @ `31c671c`. Nueva rama `f3-lab-identidad` desde ahí. `main` intacta.
**Docs:** `DOC_MAESTRO_HyperFrames.md`, `F2b_REPORT.md`, `gfx_profiles/misterio.json`, `BACKLOG_gfx_ideas.md`.

---

## 0. Por qué

Omar vio el AB de F2b y el problema ya no es técnico: **los elementos salen en el momento equivocado de la historia, los íconos no convencen, no hay pregunta de cierre, y el conjunto no tiene identidad**. Más reglas a ciegas no lo arreglan. Lo arregla que Omar **vea cada opción en la foto real, elija, y lo que elija se vuelva la identidad del canal** que el director copia en los próximos videos.

Omar no es editor de video. El lab tiene que ser **tan fácil como un formulario**: cada elemento viene con una sugerencia de la IA ("probá esto aquí, por esto") y un botón para aplicarla. Él marca ✔ en lo que se queda.

**Capítulo de trabajo: ch02 de Orleans** (`ba6c3cac-…`). Ya calibrado, tiene fotos, Veo, contador, recorte, moods. ch05 como segundo (muerte/cruz).

---

## 1. Qué es el lab

Una página HTML local (`lab/identidad/index.html`) servida por un mini-servidor Python (`gfx_lab_server.py`, Flask o `http.server` + endpoints). Tres columnas:

| Izquierda: **Historia** | Centro: **Escena** | Derecha: **Catálogo** |
|---|---|---|
| Narración de ch02 palabra por palabra (de Whisper), con el audio. Clic en una palabra = "aquí va algo". Debajo, las fotos del cap en tira, con su rango de tiempo. | Preview real de HyperFrames (iframe 1280×720, misma plantilla que el render) con play/pausa sincronizado al audio. Se regenera en ~1 s al cambiar algo. | Pestañas: **Foto · Momento · Entre fotos · Cierre · Global**. Cada elemento tiene: nombre en español, qué hace (1 línea), **Hint IA**, botón **Probar sugerencia**, controles de atributos, y casilla ✔ **Se queda en el canal**. |

Abajo, barra fija: **▶ Preview · 🎬 Render ch02 (mp4) · 💾 Guardar identidad · 📄 Resumen para el analista**.

### 1.1 Cómo funciona una sesión de Omar
1. Abre el lab. Ya viene cargado el plan que hizo el director para ch02 **más las sugerencias de la IA** (marcadas "sugerido", en gris). Nada aprobado todavía.
2. Da play. Ve la escena. Donde algo le chirría, clic en la palabra o la foto → panel derecho muestra qué hay ahí y qué más podría ir.
3. Prueba variantes con **Probar sugerencia** o cambiando atributos. El preview se actualiza.
4. Marca ✔ en lo que se queda. Marca ✖ en lo que no quiere ver nunca (va a lista de rechazados).
5. **Render ch02** cuando quiera verlo como mp4 (usa `fase2b --only-cap ch02 --gfx --gfx-plan lab_plan.json`, ~5 min).
6. **Guardar identidad** cuando esté contento. Eso escribe:
   - `gfx_profiles/misterio.json` actualizado (tokens, defaults, inventario con `enabled` true/false, variantes aprobadas).
   - `gfx_profiles/misterio_golden_ch02.json`: el plan de ch02 tal como Omar lo dejó = **ejemplo dorado** que el director recibe en su prompt (few-shot).
   - `IDENTIDAD_misterio.md`: resumen humano (ver §4) para el analista.
7. El director, desde entonces, usa perfil + ejemplo dorado. El siguiente video sale "como ch02".

### 1.2 Reglas de UX (no negociables)
- Todo en español, sin jerga: "Sello rojo", no `keyword_stamp`. El nombre técnico va en gris pequeño.
- Cada elemento: **una frase de qué hace + Hint IA de 3 líneas** (cuándo · dónde · por qué) + botón "Probar sugerencia" que aplica el preset recomendado en el lugar recomendado.
- Atributos con controles simples: selector (S/M/L), paleta de 4 colores máximo, lista de animaciones con miniatura animada en CSS (hover = se mueve).
- Nunca un campo de texto libre salvo: pregunta de cierre, texto de un label manual.
- Deshacer (Ctrl+Z) y "volver al plan del director".
- El preview es el render real: misma plantilla, misma fuente, mismo tamaño. Si en el lab se ve bien, en el mp4 se ve igual.

---

## 2. Catálogo completo (con hints)

Formato de cada entrada: **Nombre** (`id`) — qué hace. Atributos. **Hint IA.** Default sugerido para Misterios Sepultados.

### A. Pestaña FOTO — movimiento de la imagen (uno por foto)

| Elemento | Atributos | Hint IA |
|---|---|---|
| **Acercamiento lento** (`ken_burns_in`) | intensidad 1–3 (1.03–1.10), duración = foto, easing suave/lineal, punto focal (clic en la foto) | Retratos y rostros. Acerca hacia los ojos. Es la base del 60 % de las fotos. |
| **Alejamiento** (`ken_burns_out`) | igual | Revelar un lugar: empieza en el detalle y muestra el conjunto. 1 por cap máximo. |
| **Paneo** (`pan`) | dirección ←→↑↓, intensidad | Fotos anchas (calles, filas de gente). Nunca en retratos. |
| **Profundidad 3D** (`depthflow`) | preset orbital/dolly/zoom, intensidad | Paisajes y edificios con cielo. Ya existe; el lab solo elige preset. |
| **Video generado** (`veo` / `wan`) | — | Ya ruteado por el pipeline; en el lab se marca "mantener" o "cambiar a foto fija". |
| **Golpe de zoom** (`punch_in`) | 1.025 en 400 ms, en palabra X | Cuando la voz dice la palabra que importa. Máx 3 por cap. |
| **Quieta** (`hold`) | — | Solo para fotos de documentos (el texto no debe moverse). |

### B. Pestaña FOTO — look (por foto o global)

| Elemento | Atributos | Hint IA |
|---|---|---|
| **Viñeta** (`vignette`) | 0 / 0.15 / 0.30 | 0.15 es el look aprobado. Subí a 0.30 solo en moods de encierro. |
| **Grano** (`grain`) | 0 / 0.08 / 0.15 | Aprobado en 0. Probá 0.08 solo en fotos de archivo para unificar. |
| **Desaturación** (`desat`) | 0–100 % | Identidad posible: 20 % global da "documental". Probalo en todo el cap y decidí. |
| **Tinte** (`tint`) | ninguno / frío azul / verde enfermo / sepia archivo | Sepia solo en fotos antiguas; frío en noche/agua. Nunca mezclar dos en el mismo cap. |
| **Letterbox** (`letterbox`) | off / 2.35:1 | Solo como entrada de mood muerte o en el cierre de cap. Si está siempre, deja de significar. |
| **Luz de linterna** (`spotlight`) | radio, deriva 2–3° | Mood oscuridad. Elegante si se usa 1 vez por cap. |

### C. Pestaña MOMENTO — moods (se disparan por palabra)

4 activos: **veneno/enfermedad · agua · muerte · oscuridad/encierro**. Reserva: fuego, caos, radiación, frío, silencio.

| Atributo | Opciones | Hint IA |
|---|---|---|
| Intensidad | baja / media | Baja. El mood es un momento, no un filtro. |
| Duración | 1.5 / 2.5 / 4 s | 2.5 s. Más largo cansa; menos no se nota. |
| Con sello rojo | sí / no | Sí cuando la palabra es rara (arsénico); no cuando es común (agua). |
| Con ícono | sí / no / solo si literal | "Solo si literal" (regla F2b). |
| SFX | tic sordo / golpe grave / nada | Tic sordo para veneno/encierro, golpe grave para muerte, nada para agua. |
| Letterbox en muerte | sí / no | Sí. Es lo que más se sintió en ch05. |

**Hint de ubicación:** el lab resalta en la narración todas las palabras del léxico y marca cuáles disparó el director. Omar puede activar/desactivar cada una con un clic. Lo que apague/encienda ajusta el peso de la palabra en el perfil (1–3).

### D. Pestaña MOMENTO — texto en pantalla

| Elemento | Atributos | Hint IA |
|---|---|---|
| **Título de capítulo** (`title_card`) | fuente Anton, tamaño L, entrada: persiana / sello / fade, con "CAPÍTULO N" sí/no, duración 2–3 s | Persiana (texto sale desde detrás de una línea). Con número de capítulo. Al inicio de cada cap. |
| **Dato** (`data_callout`) | cifra + fragmento ≤8 palabras, posición (9 zonas), tamaño S/M, entrada: cascada / persiana / sello, salida: fade / tinta seca, caja sí/no | Tercio superior del lado "tranquilo" de la foto. Cascada. 1–2 por cap. Solo cifras o nombres propios. |
| **Contador** (`count_up`) | cifra, rampa 1.2 s + hold 2.5 s, tamaño L, color hueso / rojo, con unidad ("muertos") sí/no | Para la cifra más dura del cap. **Una vez por cifra en todo el video.** Rojo solo si es muertos. |
| **Sello rojo** (`keyword_stamp`) | palabra literal, rotación −3°…3°, tamaño S/M, entrada: sello / golpe, con borde sí/no | La palabra exacta que dice la voz. Máx 1 por frase, 5 por cap. Rotación −2°. |
| **Fuente** (`source_tag`) | texto "INFORME X, 1987", posición esquina, tamaño S, opacidad 0.75 | Debajo de cada dato con fuente. Siempre que haya fuente. Nadie lo lee, todos lo sienten. |
| **Tercio inferior** (`lower_third`) — nuevo | nombre + cargo, 2 líneas, entrada deslizar desde borde, 3 s | Cuando aparece una persona por primera vez. 1–2 por video. |
| **Cita** (`quote_card`) — nuevo | texto ≤ 20 palabras entre comillas, autor, Playfair, fondo oscurecido 50 %, entrada máquina de escribir / persiana, 4 s | Cuando la narración cita a alguien literalmente. Máx 1 por cap. Solo con cita en `verified_facts`. |
| **Pregunta de cierre** (`chapter_question`) | ver §E Cierre | — |

**Atributos comunes de texto** (en pestaña Global): fuente de datos (Anton / Playfair SC), color hueso `#f2efe6`, rojo acento `#c2302f`, amarillo de subtítulos (fijo), sombra sí/no, tamaño base.

### E. Pestaña MOMENTO — recortes de archivo (`archive_clipping`)

| Atributo | Opciones | Hint IA |
|---|---|---|
| **Estilo** | periódico (papel viejo) / **post-it** (amarillo, cinta) / ficha forense (cartulina, sello) / telegrama / carpeta "CONFIDENCIAL" | Periódico para hechos públicos; ficha forense para datos de víctimas; carpeta para encubrimientos. Elegí **2 estilos máximo** para el canal. |
| Entrada | cascada (kicker → titular → fuente) / caer desde arriba / deslizar desde borde / desdoblar | Cascada. Caer solo para post-it. |
| Salida | fade / tinta seca / deslizar | Fade 0.4 s. |
| Rotación | −4°…4° | −2° periódico, +3° post-it. |
| Ancho | ≤ 30 % | 28 %. |
| Con foto miniatura | sí / no | No (regla literal). |
| Cinta / clip | cinta / clip / nada | Cinta en post-it, nada en periódico. |
| Duración | 3 / 4 / 5 s | 4 s. Titular de ≤ 8 palabras se lee en 2. |

**Hint de ubicación:** el primer fact con fuente de cada cap. Lab muestra todos los facts elegibles del cap con un botón "poner recorte aquí".

### F. Pestaña MOMENTO — íconos

12 propios (grabado) + respaldo Lucide. Regla: solo si la palabra es literalmente lo que el ícono dibuja.

| Atributo | Opciones | Hint IA |
|---|---|---|
| Entrada | **tinta que sangra** (`ink_bleed`) / **prensa** (`press_wipe`) / sello (`stamp`) / dibujar (solo Lucide) | Tinta para veneno/muerte, prensa para evidencia, sello para encierro. |
| Hold | respirar / deriva / pulso rojo / combinación / quieto | Respirar + pulso rojo. Nunca quieto. |
| Salida | tinta seca / fade / quemar | Tinta seca. |
| Tamaño | S (80 px) / M (120) / L (180) | M. L solo si está solo en pantalla. |
| Posición | 9 zonas | Lado contrario a la cara. |
| Con sello de palabra | sí / no | Sí. |
| Red acento | sí / no | Solo donde significa (ojos, cerradura, clavo). |
| **Matriz** (`icon_array`) | N figuras en filas de 10, víctimas en rojo | Solo cifras ≤ 500 con relación total/afectados. 1 por video. |

**Si ningún ícono convence tras probar entradas/tamaños → el problema es el dibujo.** El lab tiene botón "regenerar este ícono" que lanza Flux con un prompt alternativo (más grueso / más simple / más detalle) y potrace; muestra 3 nuevos; Omar elige.

### G. Pestaña ENTRE FOTOS — transiciones

| Elemento | Atributos | Hint IA |
|---|---|---|
| **Corte** (`cut`) | — | El 70 % de los cambios. El corte es el ritmo del documental. |
| **Fundido a negro** (`dip_to_black`) | 20 / 30 f | Entre capítulos y antes de un dato duro. |
| **Flash** (`flash`) | 30 % | Solo en impacto (muerte, explosión). Máx 2 por cap. |
| **Fundido cruzado** (`crossfade`) | 20 f | Entre dos fotos del mismo lugar o tiempo. |
| **Zoom a través** (`zoom_through`) — nuevo | empuja dentro de la foto y sale en la siguiente | De un plano general a un detalle. 1 por cap. |
| **Barrido de tinta** (`ink_wipe`) — nuevo | tinta negra cubre y revela, 0.6 s | Firma del canal si gusta: entre épocas (antes/después). 1–2 por video. |
| **Quemado** (`burn`) — nuevo | la foto se quema desde un borde | Solo con fuego/destrucción en la narración. |
| **Match cut** (`match_cut`) — F3 backlog | el contador se encoge y es el punto del mapa; la gota del ícono es la inundación | Máx 1–2 por video. Se construye después del lab, solo si Omar lo marca "quiero". |

### H. Pestaña MOMENTO — sonido (`sfx`)

Biblioteca existente: tic sordo, sello, papel, tinta, golpe grave, whoosh corto, latido, drone subida. Atributos: volumen (−18 / −12 / −6 dB), con/sin. **Hint:** sello → "sello"; recorte → "papel"; contador → "tic"; cierre → "drone subida"; mood muerte → "golpe grave". Nunca más de 1 SFX por segundo.

### I. Pestaña CIERRE — fin de capítulo

| Elemento | Atributos | Hint IA |
|---|---|---|
| **Pregunta de cierre** (`chapter_question`) | texto (Omar la escribe a mano en el lab), fondo oscurecido 50/70 %, fuente Anton hueso tamaño L, entrada máquina de escribir / persiana, **pausa 2.5–3.5 s con la voz en silencio**, SFX drone subida, salida fundido a negro | Una pregunta que no se responde hasta el siguiente cap. 70 %, persiana, 3 s, drone. Es el gancho de retención más barato que existe. |
| **Tarjeta "Capítulo N"** (`next_chapter_card`) | título del siguiente cap, 1.5 s | Después de la pregunta. Opcional. |
| **Silencio visual** (`black_hold`) | 0.5–1 s de negro | Entre pregunta y siguiente cap. |

Nota: la pausa de 3 s **alarga el cap**. fase2b tiene que insertar silencio en la narración ahí (no superponer). Es la única pieza del lab que cambia duración.

### J. Pestaña GLOBAL — identidad fija

Subtítulos karaoke (Anton 150, 3 palabras, amarillo; solo tamaño ajustable S/M/L), paleta (hueso / rojo / amarillo / negro), fuentes (Anton datos, Playfair SC recortes), intervalo máximo sin bloque (12 / 18 / 25 s), máximos por cap (sellos, datos, recortes, íconos), zona protegida de subtítulos.

---

## 3. Hints: cómo se escriben y de dónde salen

Cada elemento del catálogo lleva en `lab/identidad/catalogo.json`:
```json
{"id":"archive_clipping","nombre":"Recorte de archivo","que_hace":"Muestra un titular como recorte de periódico o post-it",
 "hint":{"cuando":"En el primer dato con fuente de cada capítulo","donde":"Tercio superior, lado opuesto a la cara","por_que":"Da sensación de prueba documental sin que el espectador lea mucho"},
 "preset_sugerido":{"estilo":"periodico","entrada":"cascade","rotacion":-2,"ancho":0.28,"duracion":4},
 "atributos":[...],"ejemplo_en_ch02":{"t":34.2,"fact_idx":3}}
```
- **Sugerencias concretas para ch02** (`lab/identidad/sugerencias_ch02.json`): el analista entrega una lista de 15–20 colocaciones sugeridas (palabra/tiempo + elemento + preset) que el lab muestra en gris como "sugerido". Omar las acepta o rechaza con un clic. **Esto es lo que lo hace fácil: no parte de cero.**
- Cada "Probar sugerencia" aplica el preset en el lugar del ejemplo y hace preview.

---

## 4. El resumen para el analista (`IDENTIDAD_misterio.md`)

Se genera en vivo a medida que Omar marca casillas. Secciones:
1. **Lo que se queda** — tabla: elemento · variante elegida · atributos · cuántas veces por cap · dónde (regla de ubicación en palabras de Omar, p. ej. "sello cuando la voz dice palabra de mood").
2. **Lo que nunca** — rechazados (✖) con una línea de por qué si Omar la escribió.
3. **Lo que falta** — cosas que Omar quiso y el catálogo no tiene (campo libre "quisiera que…").
4. **Plan dorado de ch02** — lista cronológica: t · palabra · elemento · variante.
5. **Preguntas abiertas** (que el lab detecta solo): elementos probados pero sin ✔ ni ✖; moods activados sin SFX; etc.

El analista lee esto y escribe el handoff F4 para que el director lo replique en todo el video y en los siguientes. **Omar no tiene que explicar nada por chat.**

---

## 5. Implementación (CC)

### 5.1 Arquitectura
- `gfx_lab_server.py` (Flask): sirve `lab/identidad/`, las fotos y el audio de ch02, `words.json` (Whisper), el plan actual del director, `catalogo.json`, `sugerencias_ch02.json`. Endpoints: `POST /preview` (plan → HTML HyperFrames vía `gfx_project.py` → ruta del iframe), `POST /render` (lanza `fase2b --only-cap ch02 --gfx --gfx-plan`), `POST /save_identity`, `POST /regen_icon`, `GET /summary`.
- `index.html` + `lab.js` (vanilla, sin build), `catalogo.json`, `plan_ch02_lab.json` (estado), miniaturas CSS de cada animación (`anim_previews.css`).
- Preview: reutiliza **las mismas plantillas `gfx_templates/`**; el iframe carga la composición y GSAP la anima; audio de narración sincronizado por `currentTime`. Sin render de video para preview.
- `gfx_director.py` gana `--golden-plan` + `--identity` (perfil): el ejemplo dorado entra al prompt como few-shot y el inventario `enabled` filtra lo que el LLM puede usar.
- Elementos **nuevos** del catálogo (lower_third, quote_card, zoom_through, ink_wipe, burn, next_chapter_card, black_hold, pausa de cierre): se implementan como plantillas simples. `match_cut` NO se implementa ahora (solo aparece en el catálogo como "futuro" con casilla "quiero").

### 5.2 Orden y paradas
| § | Trabajo | Est. |
|---|---|---|
| A | Servidor + historia (palabras + audio + fotos) + preview iframe con el plan del director | 4 h |
| B | Catálogo completo con atributos, miniaturas animadas y hints; sugerencias_ch02 cargadas | 3 h |
| C | Casillas ✔/✖, deshacer, resumen en vivo, Guardar identidad (perfil + golden + md) | 2 h |
| D | Elementos nuevos (7 plantillas) + pausa de cierre en fase2b + botón Render + regenerar ícono | 3 h |
| E | Director consume identidad + golden plan; test: ch05 con identidad guardada | 2 h |
| **PARADA ÚNICA** | tras §C: Omar abre el lab, juega 30 min, guarda. CC sigue con D y E mientras Omar marca. | |

Total ~14 h de CC. Revisor antes de cada commit. Commits `feat(gfx-f3-lab): <sección>`.

### 5.3 Sugerencias para ch02 (el analista las entrega en `sugerencias_ch02.json` antes de §B)
CC genera un borrador con `gfx_cues_ch02` actual + léxico; el analista lo revisa en chat y lo corrige. No bloquea §A.

---

## 6. Candados
Lock literal (todo texto en pantalla viene de narración o facts, salvo la pregunta de cierre escrita por Omar en el lab, que se guarda como `manual: true`) · sin shaders · `main` intacta · sin `--gfx` byte-idéntico en segmentos · el preview usa las plantillas reales, nunca una copia · tests verdes por commit.

## 7. Qué espera Omar al terminar
1. Abrir `http://localhost:8765` y ver ch02 corriendo con lo que el director hizo + sugerencias en gris.
2. Probar, marcar, guardar. 30 minutos.
3. Un mp4 de ch02 igual a lo que vio.
4. `IDENTIDAD_misterio.md` listo para que el analista escriba F4.
