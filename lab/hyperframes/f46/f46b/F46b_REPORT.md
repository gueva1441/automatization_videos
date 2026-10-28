# F46b — El prompt de imagen «como cuchillo», armado por código (cap 2 de Wittenoom) — REPORTE

CC · 2026-10-28 · rama `f11-guion-v4` · handoff `lab/hyperframes/f46/HANDOFF_F46b_prompt_cuchillo.md` (md5 `8e3dd5908acb07c89450a2e6296cf95c` ✓). Paso 0 → Parte 1 → Parte 2 sin parada entre partes. Tope US$ 6,00; **gasto real US$ 3,5668**, leído de `cost_history` (`f46b-lab`). **PARADA:** no se elige variante ni se toca producción.

## Qué se corrió
- **Paso 0** (`878405d`): la línea del 2026-10-28 02:24 en `DECISIONES.md`, tal cual. `lab/TOPE_TANDA.json` = 6,00 (no commiteado).
- **Parte 1** (`python lab/hyperframes/f46/f46b/f46b_corridas.py prompts`, 02:33:07 → 02:35:29, US$ 0,2068):
  1. **Canon C:** el de B1 (`step_4e` con los 147 «facts» de la ficha) regenerado con el **texto 1** al final del prompt de step_4e. El esquema de respuesta se amplía solo en el proceso para recibir `people_groups`, que `extract_visual_canon` no devuelve: lo saco de la respuesta cruda. → `canon_C.json`.
  2. **Expediente por foto, por código** → `expedientes.md`:
     - ancla y párrafo;
     - beat (SEEN, emoción, intensidad);
     - AÑO (regla de la tabla, con de dónde salió);
     - DÓNDE (cronología + lugares + `donde` de las escenas);
     - escenas de la ficha;
     - citas enteras de los ids del beat;
     - personas (rol, sin nombre: el cap 2 no tiene ids `P..` en sus beats, así que queda vacío);
     - PEOPLE GROUPS.
  3. **Una llamada a Pro:**
     - SI v3 de producción con el **texto 2** (`people_group`) agregado como línea después de `foto_madre_ref`, y la propiedad en el esquema;
     - user-prompt `_build_seedream_prompt_step2` con el bloque de beats de producción + el expediente con el **texto 3** de encabezado;
     - anclas y beats de `03_visual.json` (`force_assign`).
     El pedido entero quedó en `prompt_slots_pro.txt`.
  4. **C0 armado por código** en el orden de la tabla: sujeto/acción → «The people are {appearance}, wearing {clothing}.» por grupo → mirada → objeto → «{setting}, {año}.» → `style_head(año)` + `STYLE_TAIL` → luz + paleta → plano/ángulo/lente → 16:9 + `NO_TEXT`.
     - Sin tejido de Flash, sin `mood`, sin el slot `style` (0 «faceless») y sin cifras: `hard_fact_ids` quedó fuera en las fotos 13 y 15 (`F08`).
     - Después, las reglas F8 de producción sobre los slots (`scrub_slots`, `fix_text_slot`) y sobre la prosa (nombres documentados, conteos, izquierda/derecha, escala, manos/cara/prohibidas/menores, sensible, motivos).
     - **Donde producción re-teje con Flash por una regla F8, acá va directo su backstop** (saca la frase), porque en C no hay tejido. Pasó una vez: foto 5, «manos en plano close».
  5. **C1** = C0 traducido por Flash con el **texto 4** como instrucción de sistema (texto plano, sin JSON). **C2** = C0 sin la oración de aspecto.
- **Parte 2** (`… fotos`, 02:35:42 → 02:40:26, US$ 3,36):
  - 48 prompts × `num_images` 2 = **96 fotos** con el payload de producción (Seedream 5 Lite t2i, 2560×1440) en paralelo (`FLUX_MAX_WORKERS` = 20), freno antes de cada llamada;
  - grade de producción, en `C0/`, `C1/`, `C2/` (`ch02_img_NN_a/_b` + `_graded`). **0 rechazadas.**
  - Hojas de 8 columnas: `f46b_hoja.py`, escrito por un subagente Sonnet en paralelo.
- **Producción no se editó:** las funciones se importan y los cambios (prompt y esquema de step_4e, SI y esquema de slots) viven solo en el proceso del lab. **Nada en `data/` salvo `cost_history.json`**, nada en `output/` (A se lee) ni en `topics_db`.

## Salida de la parte 1
### `people_groups` entero (canon C)
| id | who | where_when | appearance | clothing |
|---|---|---|---|---|
| `mining_workers` | Workers employed in the crocidolite asbestos mines and mill, including both local and migrant laborers. | Wittenoom mines and mill, predominantly 1937-1966, but especially in the 1950s-1960s. | Men of various ethnicities (Australian, European), typically robust builds for manual labor, often covered in asbestos dust. | Basic, durable workwear: sturdy shirts, trousers, boots, sometimes with simple protective gear, all heavily soiled with dust. |
| `european_migrant_families` | Families from European countries, particularly Spain, recruited to work and live in Wittenoom. | Arriving in Wittenoom, living in the town from the late 1940s through the mid-1960s. | People of European descent, including young adults, women, and children, adjusting to an arid environment. | Everyday civilian clothing typical of mid-20th century European styles, adapted for hot weather, often showing signs of wear and dust. |
| `wittenoom_children` | Children born or raised in Wittenoom, exposed to asbestos through play and daily life. | Playing in the town's patios, roads, and public spaces, 1950s-1960s. | Young children, often seen playing outdoors, with faces and clothes dusty from the environment. | Simple, functional play clothes typical of mid-20th century children's wear, suited for a hot climate, often dirty. |
| `officials_regulators` | Mine inspectors, state engineers, company representatives (e.g., CSR), and government officials. | Visiting the mine and town in various capacities from the 1940s to the 1960s. | Typically men, appearing professional and authoritative, often in contrast to the dusty environment of the workers. | Formal or semi-formal business attire (shirts, trousers, jackets) of the mid-20th century, possibly adapted for fieldwork. |
| `asbestos_advocates_victims` | Former workers and residents suffering from asbestos-related diseases, and their legal/health advocates. | From the 1970s onwards, in Australia and elsewhere, involved in lawsuits and advocacy. | People of various ages, often elderly and showing signs of illness, or legal professionals. | Contemporary civilian clothing for the period they are depicted, reflecting the late 20th and early 21st centuries. |

### Tabla de chequeos por código (`PROMPTS_C.md`; los 48 prompts enteros están en el archivo)
| foto | año (de dónde) | grupos | palabras C0 / C1 / C2 | año C0 / C1 / C2 | lugar de DÓNDE C0 / C1 / C2 | aspecto C0 / C1 / C2 |
|---|---|---|---|---|---|---|
| 1 | 1961 (1) dicho en el ancla) | european_migrant_families | 173 / 195 / 134 | sí / sí / sí | sí / sí / sí | sí / sí (traducción) / no |
| 2 | 1962 (1) dicho en el ancla) | european_migrant_families | 162 / 194 / 123 | sí / sí / sí | sí / sí / sí | sí / sí (traducción) / no |
| 3 | 1962 (2) el de la foto anterior del cap) | european_migrant_families | 183 / 201 / 144 | sí / sí / sí | no / no / no | sí / sí (traducción) / no |
| 4 | 1962 (2) el de la foto anterior del cap) | european_migrant_families | 172 / 208 / 133 | sí / sí / sí | no / no / no | sí / sí (traducción) / no |
| 5 | 1962 (2) el de la foto anterior del cap) | european_migrant_families | 150 / 175 / 111 | sí / sí / sí | no / no / no | sí / sí (traducción) / no |
| 6 | 1962 (2) el de la foto anterior del cap) | european_migrant_families | 169 / 206 / 130 | sí / sí / sí | no / no / no | sí / sí (traducción) / no |
| 7 | 1962 (2) el de la foto anterior del cap) | european_migrant_families, wittenoom_children | 201 / 240 / 127 | sí / sí / sí | no / no / no | sí / sí (traducción) / no |
| 8 | 1962 (2) el de la foto anterior del cap) | european_migrant_families, wittenoom_children | 209 / 244 / 135 | sí / sí / sí | no / no / no | sí / sí (traducción) / no |
| 9 | 1962 (2) el de la foto anterior del cap) | — | 135 / 155 / 135 | sí / sí / sí | no / no / no | no / no (traducción) / no |
| 10 | 1962 (2) el de la foto anterior del cap) | european_migrant_families, wittenoom_children | 219 / 267 / 145 | sí / sí / sí | no / no / no | sí / sí (traducción) / no |
| 11 | 1962 (2) el de la foto anterior del cap) | wittenoom_children | 174 / 212 / 139 | sí / sí / sí | no / no / no | sí / sí (traducción) / no |
| 12 | 1962 (2) el de la foto anterior del cap) | european_migrant_families | 172 / 203 / 133 | sí / sí / sí | no / no / no | sí / sí (traducción) / no |
| 13 | 1962 (2) el de la foto anterior del cap) | — | 127 / 146 / 127 | sí / sí / sí | no / no / no | no / no (traducción) / no |
| 14 | 1962 (2) el de la foto anterior del cap) | european_migrant_families, wittenoom_children | 214 / 261 / 140 | sí / sí / sí | sí / sí / sí | sí / sí (traducción) / no |
| 15 | 1962 (2) el de la foto anterior del cap) | — | 128 / 161 / 128 | sí / sí / sí | sí / sí / sí | no / no (traducción) / no |
| 16 | 1962 (2) el de la foto anterior del cap) | — | 144 / 171 / 144 | sí / sí / sí | no / no / no | no / no (traducción) / no |

### Ejemplo, foto 10 (Suez), los tres prompts
**C0** (219 palabras): Passengers of various ages, including an 8-year-old boy, on the deck of a ship. Slumped in deck chairs or leaning against railings, bodies limp from the heat, clothes visibly damp with sweat. The people are People of European descent, including young adults, women, and children, adjusting to an arid environment, wearing Everyday civilian clothing typical of mid-20th century European styles, adapted for hot weather, often showing signs of wear and dust. The people are Young children, often seen playing outdoors, with faces and clothes dusty from the environment, wearing Simple, functional play clothes typical of mid-20th century children's wear, suited for a hot climate, often dirty. Eyes are closed or gazing listlessly at the passing shoreline. A man mops his neck with a handkerchief. A metal cup of water, condensation dripping down its side, held loosely in a passenger's hand. The ship navigating the narrow Suez Canal, with flat, sun-scorched sandy banks visible close by, 1962. Grainy 35mm documentary photograph, 1962, dark-history realism, muted colors, visible film grain, slightly underexposed. 35mm film grain, muted documentary colors. Intense, glaring, high-noon sunlight. Pale yellows and beiges of the desert sand, washed-out blue of the sky, shimmering heat haze. Wide shot, eye-level, telephoto lens, compressing the heat haze. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.

**C1** (267 palabras): Pasajeros de varias edades, incluyendo un niño de 8 años, en la cubierta de un barco. Acomodados en sillas de cubierta o apoyados en barandillas, cuerpos flácidos por el calor, la ropa visiblemente húmeda por el sudor. Las personas son de ascendencia europea, incluyendo adultos jóvenes, mujeres y niños, adaptándose a un ambiente árido, vistiendo ropa civil cotidiana típica de los estilos europeos de mediados del siglo XX, adaptada para clima cálido, a menudo mostrando signos de desgaste y polvo. Las personas son niños pequeños, a menudo vistos jugando al aire libre, con caras y ropa polvorientas por el ambiente, vistiendo ropa de juego sencilla y funcional típica de la indumentaria infantil de mediados del siglo XX, adecuada para un clima cálido, a menudo sucia. Los ojos están cerrados o mirando sin entusiasmo la orilla que pasa. Un hombre se seca el cuello con un pañuelo. Una taza de metal con agua, con condensación goteando por sus lados, sostenida holgadamente en la mano de un pasajero. El barco navegando el estrecho Suez Canal, con orillas arenosas planas y quemadas por el sol visibles muy cerca, 1962. Fotografía documental granulada de 35mm, 1962, realismo de historia oscura, colores apagados, grano de película visible, ligeramente subexpuesta. Grano de película de 35mm, colores documentales apagados. Luz solar intensa, deslumbrante, de mediodía. Amarillos pálidos y beiges de la arena del desierto, azul descolorido del cielo, neblina de calor resplandeciente. Plano general, a la altura de los ojos, lente de teleobjetivo, comprimiendo la neblina de calor. La imagen tiene una relación de aspecto de 16:9. Sin texto legible, sin señalización, sin etiquetas.

**C2** (145 palabras): Passengers of various ages, including an 8-year-old boy, on the deck of a ship. Slumped in deck chairs or leaning against railings, bodies limp from the heat, clothes visibly damp with sweat. Eyes are closed or gazing listlessly at the passing shoreline. A man mops his neck with a handkerchief. A metal cup of water, condensation dripping down its side, held loosely in a passenger's hand. The ship navigating the narrow Suez Canal, with flat, sun-scorched sandy banks visible close by, 1962. Grainy 35mm documentary photograph, 1962, dark-history realism, muted colors, visible film grain, slightly underexposed. 35mm film grain, muted documentary colors. Intense, glaring, high-noon sunlight. Pale yellows and beiges of the desert sand, washed-out blue of the sky, shimmering heat haze. Wide shot, eye-level, telephoto lens, compressing the heat haze. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.

## Salida de la parte 2
- Hojas A | B1 | C0a | C0b | C1a | C1b | C2a | C2b (las `_graded`), 3836 px de ancho, con n.º, año y las primeras 8 palabras del ancla: `lab/hyperframes/f46/f46b/hoja_01-04.jpg`, `hoja_05-08.jpg`, `hoja_09-12.jpg`, `hoja_13-16.jpg`.
- Fotos: `lab/hyperframes/f46/f46b/C0/`, `C1/`, `C2/`. **No están en git** (unos 580 MB).
- Rechazadas por el filtro de seguridad: **ninguna** (`fotos_resultado.json`).

### Costos reales (`data/cost_history.json`, `video_id = f46b-lab`; detalle en `COSTOS.md`)
| servicio | llamadas | US$ |
|---|---|---|
| Gemini 2.5 Flash (canon 1 + 16 traducciones) | 17 | 0,0890 |
| Gemini 2.5 Pro (slots, una vez) | 1 | 0,1178 |
| fal.ai Seedream 5.0 Lite t2i (48 llamadas × 2 fotos) | 48 | 3,3600 |
| **Total** (2 reportes) | | **3,5668** (tope 6,00) |

## Lo que queda abierto (entero)
- i1. **Elegir variante:** lo deciden Omar y el analista mirando las hojas.
- i2. **El `appearance` de `people_groups` no trae tono de piel ni pelo:** por ejemplo, «People of European descent, including young adults, women, and children…», aunque el texto 1 los pide. La oración de aspecto de C0 dice el origen pero no el aspecto concreto; si eso alcanza para corregir los rostros de otro origen (lo que motivó F46b), se ve en las hojas.
- i3. **C1 no conservó todas las cifras:**
  - en 11 de 16 fotos (1–8, 10, 12 y 14) el número «20» de C0 no aparece en C1, porque «20th century» (en sus formas: «mid-20th century»…) pasó a «siglo XX»;
  - en la foto 6, «late twenties» pasó a «entre 25 y 29».
  Los años (1961/1962) y el 16:9 quedaron en las 16. Es el texto 4 tal cual; no lo toqué.
- i4. **El lugar del DÓNDE llega a la prosa en 4 de 16 fotos** (1, 2, 14 y 15): el setting de Pro casi nunca nombra Australia, Wittenoom ni Málaga, aunque están en el expediente. El año sí llega en las 16 (lo pone el código).
- i5. **La foto 1 tiene año 1961 y el resto 1962**, como en la simulación del analista. «Primer año del ancla» se toma por cláusula, porque `voz_utils.numeros` no da el orden de aparición.
- i6. **F8 sin re-tejido:** donde producción re-teje con Flash, en C se saca la frase directo (foto 5, «manos en plano close»). Hay que ver en la hoja si a la foto 5 le falta algo.
- i7. **Cifras (`hard_fact_ids`) fuera de C:** fotos 13 y 15 (`F08`). Se decide aparte si C gana.
- i8. **Personas (rol) vacío en el cap 2:** los beats 2 y 3 no tienen ids de `personajes`.
- i9. **El grupo `asbestos_advocates_victims` (desde los 70)** está en el canon pero no lo eligió ninguna foto del cap 2. Para los caps de hoy (5 a 7) es el que trae ropa contemporánea.
- i10. **Hay 2 fotos por prompt:** la varianza se ve en cada par a/b, y sigue siendo una sola llamada a Pro por variante.
- i11. **Las PNG (~580 MB) no van a git**; tampoco `lab/TOPE_TANDA.json`.
- i13. **La oración de aspecto queda mal armada con lo que devolvió el canon:** «The people are People of European descent…, wearing Everyday civilian clothing…». La plantilla del handoff espera un aspecto en minúscula y concreto (piel, pelo), y el canon dio un origen.
- i14. **Repetición en el estilo:** `style_head` («…muted colors, visible film grain…») y `STYLE_TAIL` («35mm film grain, muted documentary colors.») van juntos, como pide la tabla, y repiten grano y tono.
- i12. **El form de Omar sigue vivo** (Wittenoom en `m09_packaging --review`). No se tocó.

## Procesos y subagentes
- Subagentes: el de `f46b_hoja.py` y el revisor, terminados.
- Shells en segundo plano: los de la parte 1 y la parte 2, terminados.
- No cerré ningún proceso de Omar.

## Veredicto de revisor-handoff (íntegro)
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | md5 del handoff 8e3dd590… | OK | md5sum coincide; el reporte lo declara |
| 2 | Los 4 textos tal cual | OK | Los extraje del handoff y los comparé con las constantes TEXTO_1..4 de f46b_corridas.py:42-55: idénticos. Los textos 2 y 3 están en prompt_slots_pro.txt (líneas 22 y 266). |
| 3 | Ninguna otra regla nueva para los LLM | OK | Texto 1 se anexa al prompt de step_4e. Texto 2 se inserta como una línea después de foto_madre_ref del SI de producción. El bloque de expediente (YEAR/WHERE/PARAGRAPH/SCENES/QUOTES/PEOPLE) es dato, no regla. La traducción de C1 usa solo el texto 4. |
| 4 | Orden de armado = tabla del handoff | OK | armar(), f46b_corridas.py:305-317: sujeto/acción, aspecto, mirada, objeto, lugar+año, estilo (style_head + STYLE_TAIL), luz+paleta, plano, 16:9 + NO_TEXT. |
| 5 | Sin mood ni «faceless» | OK | 0 ocurrencias de "faceless" y de "mood" en los 48 prompts (C0/C1/C2.json). |
| 6 | F8 como producción; backstop donde producción re-teje | OK | f8() en :320-336 aplica scrub de nombres, fix_counts_lr, fix_scale, problems y scrub_sentence_problems. Solo la foto 5 disparó ("manos/cara: manos en plano close"). El reporte lo declara (i6). |
| 7 | Regla del año | OK | anios() en :151-180 sigue la cadena 1→5. Resultado: foto 1 = 1961 y fotos 2–16 = 1962, igual que la simulación del analista. El año aparece en los 16 prompts de las 3 variantes. |
| 8 | num_images 2 | OK | NUM_IMAGES = 2 en :39 y payload["num_images"] en :462. Hay 192 PNG y 96 `_graded`. |
| 9 | Freno y costos vs tope 6,00 | OK | freno() antes de cada llamada, con reserva en el paralelo (:503). Costo real 3,5668 (COSTOS.md y parte2.log), igual al del reporte. 0 rechazadas. |
| 10 | C1 y C2 difieren de C0 en una sola cosa | OK | C2 = C0 sin la oración de aspecto: lo verifiqué sobre los 16 prompts, sin diferencias. C1 es solo la traducción (texto 4). |
| 11 | Workers y paralelo | OK | ThreadPoolExecutor(am.FLUX_MAX_WORKERS), 20 workers; el log muestra las 48 llamadas intercaladas. |
| 12 | Parte 1: canon_C.json, expedientes.md, PROMPTS_C.md con tabla de chequeos | OK | Los tres existen y no están vacíos. people_groups está entero en el reporte (5 grupos). La tabla año/lugar/aspecto está en el reporte y en PROMPTS_C.md. |
| 13 | Parte 2: 4 hojas de 8 columnas | OK | hoja_01-04, 05-08, 09-12 y 13-16, todas de 3836×1090 (≤3840). Miré la hoja 09-12: tiene las 8 columnas A, B1, C0a, C0b, C1a, C1b, C2a y C2b, con rótulo de n.º, año y ancla. |
| 14 | Tabla de costos reales | OK | COSTOS.md, y la del reporte coincide: 0,0890 + 0,1178 + 3,3600. |
| 15 | Nada de producción, data/, output/ ni topics_db | OK | git status solo muestra M diag_234_cap4.py, M lab/TOPE_TANDA.json y M f28a.log, que ya estaban en el status inicial, más lab/ESTADO_SESION.md. Lo nuevo está en f46b/, y f46/B1/ y f46/B2/ siguen sin commitear. No pude verificar data/ ni output/ con certeza (solo git de lectura). |
| 16 | "Lo que queda abierto" entero | OK | i1–i12, con lo relevante: i2 (appearance sin piel ni pelo), i3 (cifras en C1), i4 (lugar), i6 (foto 5) e i7 (cifras fuera). |
| 17 | Números del reporte vs archivos | PARCIAL | Todo coincide con los archivos salvo i3: el reporte dice que "mid-20th century" perdió el "20" en 11 de 16 fotos, y yo cuento 10 de 12 prompts C0 que lo traen. Es un error menor de conteo. La foto 6 con «entre 25 y 29» no la verifiqué. |
| 18 | Veredicto, ESTADO_SESION y commit | NO VERIFICABLE | El reporte tiene el marcador {{VEREDICTO}} pendiente (este veredicto). ESTADO_SESION está modificado pero sin commitear. Falta el commit de la tanda. |

Observaciones de contenido (no violan el contrato):
- Los prompts finales traen frases mal formadas: "The people are People of European descent…, wearing Everyday civilian clothing…". Sale de la plantilla del handoff más el appearance del canon.
- La cola de estilo se duplica ("35mm film grain, muted documentary colors" aparece dos veces).
- El canon dio appearance sin tono de piel ni pelo, que era el motivo de F46b. El reporte lo declara (i2).
- La foto 10 (barco) recibe también el grupo wittenoom_children.

Fuera de alcance: ninguno.

Riesgos que el contrato no cubre: el aspecto es genérico ("European descent"), así que C0 y C2 podrían verse casi iguales en cuanto a origen; esto lo juzga Omar mirando las hojas. Las PNG (~580 MB) y TOPE_TANDA.json quedan fuera de git. Antes de cerrar hay que pegar este veredicto en el marcador del reporte y commitear.

### Adenda de CC (después del veredicto)
- **#17 / i3:** las dos cuentas miden cosas distintas. La mía cuenta las fotos donde el número «20» de C0 no aparece en C1, venga de «mid-20th century» o de otra forma de «20th century»: son 11 (fotos 1–8, 10, 12 y 14, sacado por código comparando las cifras de C0 y C1). i3 ahora lo dice así.
- **Observaciones de contenido:** van a «abierto» como i13 (la oración de aspecto mal armada con lo que devuelve el canon) e i14 (la repetición de grano/tono entre `style_head` y `STYLE_TAIL`, que el handoff pide juntos). La foto 10 con `wittenoom_children` es elección de Pro (ruteo), y queda a la vista en la tabla de chequeos.
- **#18:** el veredicto ya está pegado; el commit va con este reporte.

