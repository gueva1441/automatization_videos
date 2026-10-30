# F60_REPORT — foto madre por PERSONA + modo secuencia (Seedream v5 Lite /edit)

Handoff `lab/hyperframes/f60/HANDOFF_F60_madre_personas_secuencia.md` (md5 `a2e7e8cb4a6e62c52fdccc5b58c7b1ac`). Rama `f11-guion-v4`. Topic Wittenoom `123bbb64-9fca-4395-8bf4-57d60e219ef1` sobre la copia `lab/hyperframes/f60/base/`. Sin código de producción tocado.

## Etapa 0 — prueba de secuencia en lab — PARADA 0 (con PARÁ por timeout)

- Madre de Daniel Écija: OK (26,9 s, US$ 0,035).
- Lote 1 (6 fotos): **ReadTimeout a los 240 s** (timeout existente de `_generate_image_raw`); 0 devueltas; gasto probable US$ 0,21 sin confirmar.
- Lote 2 (3 fotos): 3/3 en 142,5 s, US$ 0,105; escena i = imagen i (1 parcial, 2 sí); cara de la madre 8/10 en la única foto con caras, con contagio a 2–3 mineros; la ropa de la madre se arrastra.
- Gasto confirmado **US$ 0,14** (+ 0,21 probable).
- PARÁ: el timeout para N = 6 es un número que no está en la tabla de constantes → lo decide el analista/Omar.

### T · Tabla de verdad verificada contra `03_visual.json` de la copia (las 15 referencias coinciden; aquí las 9 fotos flux de Daniel que entraron)

| ref | cap | archivo | año | people_group | plano | ancla (recorte) |
|---|---|---|---|---|---|---|
| chapters[1].img[0] | 2 | ch02_img_01.png | 1961 | spanish_migrant_families | wide | Dieciséis de septiembre de mil novecientos sesenta y uno. En el salón de baile del Círculo de Bellas Artes de  |
| chapters[1].img[1] | 2 | ch02_img_02.png | 1962 | spanish_migrant_families | wide | Un año después se casan: el jueves veinte de septiembre de mil novecientos sesenta y dos. Cuatro días más tard |
| chapters[1].img[3] | 2 | ch02_img_04.png | 1962 | spanish_migrant_families | medium | De Wittenoom no saben nada; saben que hay trabajo y que van juntos. «Iba pegadita a mi marido, como una niña», |
| chapters[1].img[4] | 2 | ch02_img_05.png | 1962 | spanish_migrant_families | wide | Con el tiempo se hicieron amigos íntimos de otra pareja, Milagros Barroso y Ramón de Juan. |
| chapters[2].img[15] | 3 | ch03_img_16.png | 1962 | spanish_migrant_families | wide | «porque estaban acostumbrados; lo esperaban», dijo McNulty. En mil novecientos sesenta y uno la producción sub |
| chapters[3].img[6] | 4 | ch04_img_07.png | 1963 | spanish_migrant_families | wide | Y en ese pueblo, en junio de mil novecientos sesenta y tres, nació un niño. |
| chapters[3].img[8] | 4 | ch04_img_09.png | 1962 | mine_and_mill_workers | wide | Uno de los hijos de Daniel cuenta que el primer día de trabajo de su padre hubo una explosión y murió gente. |
| chapters[3].img[13] | 4 | ch04_img_14.png | 1963 | spanish_migrant_families | wide | Se fueron antes de que nadie les dijera nada. Nadie les había dicho nada. |
| chapters[4].img[4] | 5 | ch05_img_05.png | 1966 | spanish_migrant_families | wide | Ese mismo año, los Écija entran a su casa en Madrid. |

Las otras 6 referencias de la tabla también coinciden: chapters[1].img[5] = «A Madrid migrant family … small boy around eight» (la otra familia); [4].img[12] y [13] = «lean Spanish man about fifty-five» (1991); [4].img[14] = «sepia family photograph … one foot bandaged» (2023); [0].supp[0] ancla «…menos el pie: está vendado…»; [0].image_prompt = «young adult Spanish migrant miner … one foot wrapped in a white bandage» y [0].supp[3] ancla «Para entender ese pie hay que volver a un baile en Madrid» (cap con clip, Etapa C).

## Salida 0 (íntegra) (prueba de secuencia en lab, SIN tocar producción) — PARADA 0

Handoff `lab/hyperframes/f60/HANDOFF_F60_madre_personas_secuencia.md` (md5 `a2e7e8cb4a6e62c52fdccc5b58c7b1ac`, verificado). Copia de lab `lab/hyperframes/f60/base/` hecha con `lab/hyperframes/f60/copia_lab.py` (copia del método de F59; producción intacta: guion vivo `f762dc48…` antes y después, `_steps` sin cambios; 230 archivos, 629,9 MB; log en `copia_lab.log`). Runner: `lab/hyperframes/f60/etapa0_secuencia.py` → `etapa0.json`, `etapa0.log`, imágenes en `e0/` (fuera de git).

**Resultado en una línea:** la madre salió bien; el lote de 6 fotos **no entró en el timeout existente de 240 s** (`_generate_image_raw`, asset_manager.py) y se perdió; el lote de 3 fotos tardó 142,5 s, devolvió 3/3, escena i = imagen i en las 3, y la cara de la madre aparece en la única foto que muestra caras (con contagio a un segundo minero). **PARÁ** por el punto «timeout de la llamada de secuencia … si alguno no alcanza para N fotos, PARÁ y mostrá la medición».

### 0.1 Schema de `fal-ai/bytedance/seedream/v5/lite/edit` (GET, método de f52; crudo en `schema_edit_v5_lite.json`)

| campo | req | tipo | default | rango | descripción (fal) |
|---|---|---|---|---|---|
| `prompt` | sí | string | — | — | The text prompt used to edit the image |
| `image_urls` | sí | array | — | — | List of URLs of input images for editing. When more than 10 references are provided, only the last 10 are used. |
| `num_images` | | integer | 1 | 1–6 | Number of separate model generations to be run with the prompt. |
| `max_images` | | integer | 1 | 1–15 | Maximum images per generation in sequential mode. Ignored when sequential generation is disabled. **Combined input references and outputs per generation cannot exceed 15.** |
| `sequential_image_generation` | | enum | — | `auto` / `disabled` | Generate related images with `auto`, or one image per generation with `disabled`. When omitted, values of `max_images` above one enable `auto`. |
| `enable_safety_checker` | | boolean | true | | |
| `sync_mode` | | boolean | false | | |
| `watermark` | | boolean | false | | |
| `image_size` | | enum/obj | `auto_2K` | | native 2560x1440 to 4096x4096, aspect 1/16–16 |
| `output_format` | | string | jpeg | | |

Salida: `images` (lista) + `seed`. Límite referencias+salidas = **15** por generación. Con 2 madres (tope `_norm_foto_madre_refs`) caben hasta 13 salidas; con 1 madre, 14. `num_images` queda en 1 (handoff).

**Precio real (GET `api.fal.ai/v1/models/pricing`):** `/edit` **0,035 US$ por imagen** (`unit: images`); t2i v5 Lite 0,035 US$/imagen. Mismo valor que `seedream_per_image` de `track_seedream`, pero leído de fal. Lo que fal cobra por una llamada de secuencia es `unit_price × imágenes devueltas`; no hay forma de leer el cobro real de una llamada desde la API (se asume la tarifa publicada).

### 0.2 Madre de Daniel Écija (Seedream v5 Lite t2i, `model_id` del perfil, `image_size` {2560×1440} del perfil)

Datos reales usados (a mano, Etapa B.1):
- `appearance_canon` (05_visual_canon): «a young adult Spanish migrant miner in work clothes, one foot visibly bandaged» → recortado sin ropa ni estado del cuerpo: «a young adult Spanish migrant miner».
- `people_group` más frecuente en las 9 fotos de Daniel de la tabla: `spanish_migrant_families` ×8, `mine_and_mill_workers` ×1 → appearance «Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes.»
- año = primer número de 4 dígitos de `era` «1962-1963» → **1962**. `ESTILO_C` y `NO_TEXT` reusados de `m03_imagenes_v3` (sin «faceless»).

Prompt (el que fue a fal):

    Head-and-shoulders portrait of a young adult Spanish migrant miner. Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes. Neutral expression, facing the camera, plain mid-grey background, soft even light. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight underexposure, in a dark-history realist style. No readable text, no signage, no labels.

Payload: `{"prompt", "image_size": {"width": 2560, "height": 1440}, "num_images": 1, "enable_safety_checker": true}` (espejo de `_seedream_payload_for`; v5 Lite no acepta seed). Resultado: **26,9 s**, seed devuelto 143986887, 2560×1440 (JPEG con extensión .png, como en producción), US$ 0,035. Foto: `e0/madre_daniel_ecija.png` (arriba en la hoja). Es un hombre joven de pelo oscuro corto, barba de pocos días, mirando a cámara, fondo gris, camisa de trabajo manchada (la ropa la puso el modelo aunque el prompt no la pide).

### 0.3 Lotes de secuencia (`/edit`, `image_urls=[madre]`, `max_images=len(lote)`, `sequential_image_generation="auto"`, `num_images=1`, `image_size` del perfil, timeout 240 s)

Fotos de Daniel de la tabla de verdad (caps flux, orden de guion): chapters[1].img[0,1,3,4], [2].img[15], [3].img[6,8,13], [4].img[4] = 9 fotos → lotes de 6: **lote 1 = 6, lote 2 = 3**. `chapters[4].img[4]` (1966, de espaldas, ~30; «Daniel Écija o ""») entra y se declara. Tabla de verdad verificada: las 15 referencias coinciden con lo que describe el analista (ver `etapa0.json → items` y el dump en F60_REPORT §T).

Prompt de secuencia: armado en código (sin LLM) como en el handoff; de cada `prompt` de 03_visual se quitan las frases «The image has a 16:9 aspect ratio.» (`aspect_ratio_text` del perfil) y «No readable text, no signage, no labels.» (`NO_TEXT`), y van una sola vez al final en «Every image: …». Prompts íntegros en `etapa0.json → lotes[n].prompt_secuencia`.

### Lote 1 — 6 fotos (ch02_img_01, ch02_img_02, ch02_img_04, ch02_img_05, ch03_img_16, ch04_img_07) · prompt 4608 chars
- Pedidas 6 · devueltas **0** · **`ReadTimeout: HTTPSConnectionPool(host='fal.run', port=443): Read timed out. (read timeout=240)`**.
- Medición: con 3 fotos la llamada tardó 142,5 s (≈ 47,5 s por foto); 6 fotos proyectan ≈ 285 s > 240 s. El timeout existente de `_generate_image_raw` (240 s, `fal.run` SYNC) **no alcanza para 6 fotos**. El de la cola (`FLUX_POLL_TIMEOUT` = 180 s) tampoco; el de clips (`CLIP_POLL_TIMEOUT` = 600 s) sí alcanzaría, pero es de otro camino.
- Costo: fal probablemente siguió generando después del corte y cobró las 6 (US$ 0,21); no se puede confirmar desde la API. Se cuenta como **gasto probable** aparte.
- No se reintentó: elegir otro timeout es un número que no está en la tabla → PARÁ.

### Lote 2 — 3 fotos (ch04_img_09, ch04_img_14, ch05_img_05) · prompt 2405 chars
- Pedidas 3 · devueltas **3** · **142,5 s** · seed 1339186958 · 2560×1440 las 3 · US$ **0,105** (0,035 × 3).
- ¿Imagen i = escena i? (mirada de CC; la segunda mirada independiente está en F60_REPORT):

| pos | foto | escena pedida | ¿es la escena? | cara de la madre |
|---|---|---|---|---|
| 1 | ch04_img_09 (cap 4, 1962) | mineros cubiertos de polvo, la mayoría de espaldas, y un joven minero español aparte; fuera de la bocamina tras la explosión, nube de polvo | **parcial**: bocamina, polvo y paredes rojas sí; pero 8 mineros en fila mirando a cámara, ninguno de espaldas, nadie «aparte» | **sí**: el 7.º de izquierda a derecha es la madre (cejas, nariz, boca, pelo); el 6.º también se le parece → **contagio: 2 caras** |
| 2 | ch04_img_14 (cap 4, 1963) | familia de espaldas cruzando la pista hacia el avión con valijas | **sí** (hombre, mujer con bebé, valijas, avión de hélice, pista oscura, cañón de fondo; luz dorada) | de espaldas: no se ve la cara |
| 3 | ch05_img_05 (cap 5, 1966) | familia de espaldas entrando por el portal de un bloque de Madrid, calle de ladrillo con balcones | **sí** (bloque de ladrillo rojo con balcones de hierro, familia pequeña en el portal, plano general) | de espaldas: no se ve la cara |

- Hoja: `lab/hyperframes/f60/hoja_madre_secuencia.jpg` (madre arriba; por fila: nueva | PNG t2i viejo del mismo slot en la copia). Caras: `hoja_caras_lote2.jpg` (madre recortada vs franja de rostros de la foto 1).
- **Advertencia sobre la columna «vieja»:** los PNG de `assets/` de la copia vienen del guion del 28-oct (hallazgo F59 §5.1): el manifest dice para ch04_img_09 «young Spanish woman in a hospital bed», para ch04_img_14 «empty cork notice board» y para ch05_img_05 «couple unlocking the front door». Solo la tercera es la misma escena. La comparación de cara con la t2i vieja solo vale ahí: en la vieja el hombre tiene otra cara (y está de frente); en la nueva está de espaldas.

### 0.4 Gasto

| servicio | qué | US$ |
|---|---|---|
| fal Seedream v5 Lite t2i | madre | 0,035 |
| fal Seedream v5 Lite /edit secuencia | lote 2, 3 imágenes | 0,105 |
| **total confirmado** | | **0,14** |
| fal /edit secuencia (probable, sin confirmar) | lote 1, 6 imágenes que fal pudo haber generado tras el timeout | 0,21 |

`cost_tracker` no se usó (el handoff pide el precio de fal, y `track_seedream` tiene tarifa fija); los valores son `unit_price × imágenes devueltas`.

### 0.5 DECISIONES.md
Las 4 líneas de «Decisiones» del handoff, tal cual, al final de `DECISIONES.md` (CRLF), con una línea de encabezado «F60 (handoff …, «Decisiones», tal cual)».

### Lo que queda abierto (Etapa 0)
1. **Timeout para 6 fotos** (PARÁ): 240 s no alcanza; 3 fotos = 142,5 s. Decisión del analista/Omar: un timeout para la llamada de secuencia (p. ej. proporcional a N) o pasar la secuencia por la cola de fal (`queue.fal.run`) con un poll largo. Sin ese número no se repite el lote 1.
2. El lote de 6 no se vio: no hay medida de contagio ni de «escena i = imagen i» con 6; con 3 dio 3/3 en escena y 2 caras-madre de 8 en la única foto con caras.
3. En la foto 1 el modelo ignoró «mostly seen from behind» y «standing apart» y puso a todos de frente; con una madre en `image_urls`, `/edit` tiende a mostrar la cara. Pendiente ver si pasa con más lotes.
4. La ropa de la madre (camisa de trabajo manchada) la puso el modelo; el prompt no la pide.
5. Precio real de la llamada cortada: no verificable desde la API.
6. Los PNG «viejos» de la copia no corresponden a los prompts de 03_visual en 2 de las 3 fotos del lote 2 (y en 6 de 9 del total): la comparación cara nueva vs t2i vieja casi no tiene par.


## Segunda mirada independiente (subagente, solo lectura, íntegra)

**Madre (referencia):** hombre joven, pelo negro corto y desordenado, cejas gruesas y oscuras, ojos marrones oscuros, nariz recta algo prominente, barba de pocos días, labios finos, cara alargada, camisa de trabajo oscura manchada de blanco. Retrato frontal de estudio, fondo gris.

| Imagen | (a) ¿Muestra la escena i del prompt? | (b) ¿Se ve la cara del hombre de la madre? Parecido 1-10 | (c) Contagio |
|---|---|---|---|
| 01_ch04_img_09 (Image 1: mineros tras la explosión, mayoría de espaldas, uno español apartado) | **Parcial.** Hay garganta roja, portal de madera, polvo flotando y 7 mineros con camisas sucias; pero los 7 están **de frente mirando a cámara**, ninguno de espaldas, y nadie está "apartado": es una foto de grupo posada, no un momento después del estallido. | **Sí.** El hombre grande del centro-derecha (2.º desde la derecha, primer plano) es la madre: **8/10**. Mismo pelo negro desordenado, mismas cejas gruesas, ojos oscuros, nariz, barba rala y boca fina; la cara es un poco más ancha y más sucia que en la madre. | **3 de 7** llevan la cara de la madre: el del centro-derecha (8/10), el del centro-fondo justo a su izquierda (7/10, casi un clon más chico) y el de la derecha del todo (6/10, misma estructura y pelo, algo más fornido). Los otros 4 (canoso, dos castaños claros, moreno del fondo) son caras distintas. |
| 02_ch04_img_14 (Image 2: familia cruzando la pista hacia la avioneta, de espaldas, golden hour) | **Sí.** Hombre en camisa oscura manchada con dos valijas, mujer de vestido claro con bebé en brazos y valija, todos de espaldas, pista oscura, avión con hélices al fondo, meseta roja, luz dorada con sombras largas. Único reparo: el avión parece bimotor turbohélice moderno, no "pequeña avioneta" de 1963. | **No se ve la cara porque está de espaldas.** Solo se ve nuca con pelo negro corto, cuerpo delgado y la camisa manchada de la madre: compatible, pero no se puede puntuar la cara. | No aplica (nadie muestra la cara; la mujer también de espaldas, el bebé de perfil borroso). |
| 03_ch05_img_05 (Image 3: familia entrando por el portal de un bloque de ladrillo en Madrid, 1966, nene de la mano) | **Sí.** Fachada de ladrillo con balcones de hierro y rejas, portal, hombre con chaqueta oscura, mujer con blusa y falda, nene de la mano, los tres de espaldas entrando, adoquines, luz suave. Reparo menor: la chaqueta del hombre tiene las mismas manchas blancas que la camisa de minero (arrastre de la madre en la ropa, no "late-1960s jacket" limpia). | **No se ve la cara porque está de espaldas** y además la figura es muy chica (plano muy abierto). Solo pelo negro y silueta delgada; imposible puntuar. | No aplica (ninguna cara visible). |

**¿Las tres parecen la misma persona?** Solo se puede afirmar por la cara en la 01 (y ahí la madre está bien transferida, 8/10). En 02 y 03 el hombre es coherente con la madre en lo que se ve (pelo negro corto, delgado, camisa/chaqueta oscura con las mismas manchas blancas), pero sin cara visible no hay forma de confirmar identidad: es consistencia de vestuario y silueta, no facial. El hallazgo fuerte es el **contagio en la 01**: Seedream en secuencia replicó la cara de la madre en 3 de 7 mineros en vez de usarla en uno solo, e ignoró el "mostly seen from behind".

Nota de CC: CC cuenta 8 mineros (el subagente 7) y ve la madre clara en 2 (el 7.º y el 6.º); el subagente suma un tercero (el de la derecha). Coinciden en lo que importa: la madre se transfiere (≈ 8/10) y se contagia a más de un minero; la ropa de la madre (manchas blancas) se arrastra a las 3 fotos.

## Veredicto de revisor-handoff — Etapa 0 (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES (la Etapa 0 queda incompleta por un PARÁ legítimo del handoff: el lote de 6 fotos no se obtuvo)

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Leer el schema de `/edit` v5 Lite (método f52) y pegar `max_images`, `num_images` y el límite referencias+salidas | OK | `schema_edit_v5_lite.json` existe (12 KB). SALIDA_0 §0.1: `max_images` 1–15, `num_images` 1–6, referencias+salidas ≤ 15. `num_images` quedó en 1 (etapa0.json, payload). |
| 2 | Madre de Daniel: v5 Lite t2i, prompt B.1 a mano, `ESTILO_C` y `NO_TEXT` reusados, sin «faceless» | OK | El prompt en `etapa0.log`/`etapa0.json` sigue el formato del handoff. El runner usa `v3img.ESTILO_C.format(anio=1962)` y `v3img.NO_TEXT` (etapa0_secuencia.py:132-134). Año 1962 sale de `era` «1962-1963». `e0/madre_daniel_ecija.png` existe y mide 2560×1440. |
| 3 | Fotos de Daniel de la tabla (caps flux, orden de guion) → lotes de 6 → una llamada `/edit` por lote con `image_urls=[madre]`, `max_images=len(lote)` y el prompt de secuencia | PARCIAL | 9 fotos, lotes 6+3. El prompt de secuencia coincide con el formato (encabezado «A series of N…», «Image i:», «Every image: aspecto NO_TEXT», sin LLM). El lote 1 dio ReadTimeout a los 240 s con 0 devueltas. El lote 2 salió 3/3 en 142,5 s. |
| 4 | Por lote: pedidas/devueltas, ¿imagen i = escena i?, segundos, precio real, hoja con madre + nuevas + t2i vieja | PARCIAL | Lote 2 completo en SALIDA_0 §0.3. Lote 1 solo tiene la medición del timeout, sin fotos. Las hojas existen (`hoja_madre_secuencia.jpg`, `hoja_caras_lote2.jpg`). Las 3 imágenes del lote 2 miden 2560×1440. SALIDA_0 admite que 2 de las 3 «viejas» no son la misma escena. |
| 5 | DECISIONES.md con las 4 líneas «Decisiones» tal cual | OK | `git diff DECISIONES.md` muestra 5 líneas añadidas: 1 de encabezado y las 4 del handoff, con el mismo texto (15:42, 15:45, 16:14, 16:14 «sigamos»). Terminan en CRLF (`$` tras `^M` en `cat -A`). |
| 6 | Número fuera de la tabla → PARÁ | OK | El timeout de 240 s es el existente (`TIMEOUT_S`, etapa0_secuencia.py:32). Al no alcanzar para 6 fotos, CC paró sin inventar otro valor, que es lo que pide la fila de la tabla («si alguno no alcanza para N fotos, PARÁ y mostrá la medición»). |
| 7 | Tabla de verdad: si una referencia no coincide, PARÁ | OK | Verifiqué con el 03_visual de la copia las refs [1][5], [3][6], [3][8], [3][13], [4][4], [4][12], [4][14], [2][15] y [0] supp[0]. Todas describen lo que dice la tabla. Hay una ambigüedad menor: [3][6] está declarada «dudosa» en la tabla. |
| 8 | Precio real de fal, no `track_seedream` | OK | Salió de GET `api.fal.ai/v1/models/pricing`: 0,035 US$/imagen para t2i y para `/edit` (runner l.57-58). El cálculo es 0,035 × imágenes devueltas. |
| 9 | Costos cierran | OK | 0,035 + 0,105 = 0,14 confirmado. Los 0,21 del lote 1 figuran aparte como probables y sin confirmar. etapa0.json `usd_total` = 0,14 coincide. |
| 10 | SALIDA_0 coincide con etapa0.json | OK | Coinciden los prompts, los tiempos (26,9 s y 142,5 s), las seeds, los conteos y el timeout 240 s. |
| 11 | Producción intacta | OK | `git status` y `git diff --stat` de asset_manager.py, m03_visual.py, foto_madre.py, m06_assembler.py y qa_studio_server.py salen vacíos. |
| 12 | Imágenes fuera de git | PARCIAL | No hay nada staged ni commiteado. Pero solo `base/` está ignorado (`git check-ignore`); `e0/*.png` y las hojas `.jpg` aparecen como untracked normales. |

Fuera de alcance:
- `lab/ESTADO_SESION.md` figura modificado (+13 líneas). CLAUDE.md lo exige en cada hito, así que lo considero aceptable.
- `diag_234_cap4.py` y `lab/hyperframes/f28/a/f28a.log` ya estaban modificados antes de la tanda.
- No encontré nada más fuera de `lab/hyperframes/f60/` y DECISIONES.md.

Observaciones:
1. El runner pasa `sequential_image_generation="auto"` (l.168), que el handoff no menciona. Equivale al default del schema cuando `max_images` > 1, pero es un parámetro agregado.
2. Tras el fallo del lote 1, el runner siguió solo con el lote 2 (0,105 US$). No viola nada, pero el PARÁ se aplicó recién después del gasto.
3. El lote de 6 no se vio, así que faltan datos de contagio y de «escena i = imagen i» con 6 fotos. En el lote 2, la foto 1 es «parcial»: el modelo ignoró «de espaldas» y «aparte», y hay contagio a 2 caras.
4. La comparación con la t2i vieja casi no tiene par: las «viejas» vienen del guion del 28-oct. Solo ch05_img_05 es la misma escena (SALIDA_0 lo advierte).
5. etapa0.log imprime «NonexNone» para el tamaño de la madre, pero el archivo real mide 2560×1440 (lo medí con PIL).

Riesgos que el contrato no cubre:
- Los 0,21 US$ del lote 1 no se pueden confirmar desde la API.
- Si `git add` toma `f60/` entero, entrarían los PNG y JPG de `e0/`, los de las hojas y quizá `base/`; conviene un patrón en .gitignore o un add selectivo.
- Queda sin decidir el timeout para 6 fotos; el analista u Omar tienen que fijar ese número (por ejemplo, proporcional a N o por la cola de fal) antes de la Etapa B.

### Adenda de CC
- **Obs. 1:** cierto; `"auto"` es el valor que el schema aplica solo cuando `max_images` > 1; se puso explícito para que el payload diga lo que hace. No es un número; si el analista prefiere omitirlo, es una línea.
- **Obs. 2:** cierto; el runner no se detiene al primer lote fallido. El lote 2 era el de 3 fotos y dio la medición (142,5 s) que el PARÁ pide mostrar; sin él no habría proyección para 6.
- **Obs. 5:** fal no devuelve `width`/`height` en la respuesta de v5 Lite; el tamaño real (2560×1440, medido con PIL) está en SALIDA_0 §0.2. El log queda tal cual.
- **Fila 12 / riesgo 2:** como en F58/F59, las imágenes quedan fuera por paths explícitos en el commit; no se tocó `.gitignore` sin pedido (`base/` sí está ignorada por las reglas de `data/` y `output/`).
- **Riesgo 3:** es el PARÁ de esta etapa; la pregunta va al analista con la medición (3 fotos = 142,5 s; 240 s no alcanza para 6).
