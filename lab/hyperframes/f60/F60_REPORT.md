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

---

## Etapa 0b — secuencia por la cola de fal + madre con ropa limpia (PARADA 0b)

Handoff `HANDOFF_F60_0b_cola_y_madre_limpia.md` (md5 `30a632c578d98fa832bbc02bd90f1a34`). Runner `etapa0b_secuencia.py`; registros en `e0b/`. Salida 0b íntegra (también en `SALIDA_0b.md`):

Handoff `lab/hyperframes/f60/HANDOFF_F60_0b_cola_y_madre_limpia.md` (md5 `30a632c578d98fa832bbc02bd90f1a34`, verificado). Sobre la copia de lab `lab/hyperframes/f60/base/` ya existente (no se rehizo). Runner `lab/hyperframes/f60/etapa0b_secuencia.py` (copia de `etapa0_secuencia.py` con los 4 cambios del handoff) → `e0b/etapa0b_pedidos.json`, `e0b/etapa0b.json`, `e0b/etapa0b.log`, imágenes en `e0b/` (fuera de git). `e0/` y `etapa0_secuencia.py` intactos. Producción intacta: de `asset_manager` solo se importan `_clip_poll`, `_fal_headers`, `FLUX_MAX_WORKERS`, `CLIP_POLL_TIMEOUT`; de `config`, `api` (`fal_base_url` = `https://queue.fal.run`).

**Resultado en una línea:** por la cola de fal los dos lotes volvieron completos (6/6 y 3/3) en paralelo, 286,1 s de pared; la madre con ropa limpia salió con camisa clara sin manchas; las manchas de la Etapa 0 ya no se arrastran, pero la camisa clara de la madre sigue siendo la base en las escenas que no imponen otra prenda (cubierta, veranda, pista, hospital, bajo el mameluco); en la foto de los mineros esta vez sí están de espaldas y Daniel aparte, sin contagio. Sin errores de fal, sin reintentos. Gasto US$ 0,35.

### 0b.1 Madre (Seedream v5 Lite t2i por la cola, `model_id` del perfil, `image_size` 2560×1440)

Prompt que fue a fal — **byte a byte igual** al del handoff (`prompt_madre_igual_al_handoff: true` en `etapa0b.json`):

    Head-and-shoulders portrait of a young adult Spanish migrant miner, wearing a plain, clean, light-coloured shirt. Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes. Neutral expression, facing the camera, plain mid-grey background, soft even light. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight underexposure, in a dark-history realist style. No readable text, no signage, no labels.

- `request_id` `01a18ed4-d49e-7fb2-a5df-3b83d8972901` · submit 18:01:15 → vuelta 18:01:52 · **37,8 s** (submit → vuelta de `_clip_poll`, con cola) · seed 460661449 · 2560×1440 (JPEG con extensión .png) · `has_nsfw_concepts`: **no viene en la respuesta** (`None`; v5 Lite no lo devuelve, igual que `width`/`height`) · US$ 0,035.
- Foto `e0b/madre_daniel_ecija.png`: hombre joven, pelo oscuro corto, afeitado (sombra de barba leve), expresión neutra, fondo gris liso. **Ropa: camisa clara (crema), lisa, limpia, sin manchas ni polvo.** La frase de ropa funcionó; en la Etapa 0 la misma madre salió con camisa de trabajo manchada.

### 0b.2 Lotes (`/edit` secuencia por la cola, `image_urls=[data-uri de e0b/madre_daniel_ecija.png]`, `max_images=len(lote)`, `sequential_image_generation="auto"`, `num_images=1`, mismo prompt de secuencia que la Etapa 0)

Los 2 lotes se pidieron a la vez (`ThreadPoolExecutor(max_workers=min(2, FLUX_MAX_WORKERS=20))`) con la madre ya en disco; `request_id` escrito en `etapa0b_pedidos.json` antes de esperar; espera con `asset_manager._clip_poll` (600 s, poll 5 s, HTTP 15/30 s, tal cual).

| lote | fotos | pedidas / devueltas | `request_id` | submit → vuelta | s/foto | seed | `has_nsfw_concepts` | US$ (0,035 × devueltas) |
|---|---|---|---|---|---|---|---|---|
| 1 | ch02_img_01, ch02_img_02, ch02_img_04, ch02_img_05, ch03_img_16, ch04_img_07 (prompt 4608 chars) | 6 / **6** | `01a18ed5-6dfa-7ee0-ade6-d38eed7886dd` | 18:01:54 → 18:06:36 · **283,0 s** | 47,2 | 1780408611 | no viene (`None`) | 0,21 |
| 2 | ch04_img_09, ch04_img_14, ch05_img_05 (prompt 2405 chars) | 3 / **3** | `01a18ed5-6dff-7282-addd-f57d7bd862db` | 18:01:54 → 18:04:19 · **145,7 s** | 48,6 | 1200455859 | no viene (`None`) | 0,105 |

- **Tiempo de pared de los 2 lotes en paralelo: 286,1 s** (= el lote de 6; el de 3 corrió adentro). Las 9 fotos miden 2560×1440.
- El lote de 6 (283 s) confirma la proyección de la Etapa 0 (≈ 47,5 s/foto → 285 s): con `fal.run` síncrono a 240 s no entraba; con la cola y `CLIP_POLL_TIMEOUT` 600 s sobra. El submit nunca trajo `images` (siempre hubo que esperar).
- Ningún `TimeoutError`, `ContentRejectedError`, `RuntimeError` ni submit no-2xx. Sin reintentos.

### 0b.3 Tabla por foto — dos miradas

#### Mirada de CC

| foto | ¿es la escena pedida? | cara de la madre (1–10 o «de espaldas») | contagio (caras-madre de más) | ropa del protagonista: ¿escena o madre? | anacronismos a la vista |
|---|---|---|---|---|---|
| L1 #1 ch02_img_01 (1961, baile) | **sí**: salón con arañas, dorados, parquet, parejas bailando desenfocadas; él y ella en el borde de la pista, cabeza inclinada hacia ella | 8 (perfil: cejas, nariz, pelo, mentón) | 0 | **escena**: traje oscuro, camisa blanca, corbata | ninguno; el vestido de ella es liso crema (el prompt pedía cotton-satin), menor |
| L1 #2 ch02_img_02 (1962, muelle) | **sí**: muelle, transatlántico, pasarela, grúas, multitud, carrito de equipaje, valijas de cartón; de espaldas/perfil hacia el barco; ángulo bajo | 6 (perfil parcial bajo el sombrero; pelo y nariz compatibles) | 0 | **escena**: traje oscuro y sombrero | ninguno |
| L1 #3 ch02_img_04 (1962, cubierta) | **sí**: cubierta, mar, baranda, ella pegada bajo su brazo, pasajeros desenfocados, plano medio tres cuartos | **9** (misma cara que la madre, de frente) | 0 | **escena = madre**: camisa clara en mangas de camisa; el prompt pide «shirtsleeves», así que coincide con la escena, y de paso es la camisa de la madre (limpia) | ninguno |
| L1 #4 ch02_img_05 (1962, veranda) | **sí**: veranda de chapa y fibro, tierra roja, dos parejas sentadas, lámpara, atardecer | 8 (el hombre de la izquierda) | **1 débil**: el hombre de la derecha se le parece (pelo, cejas) pero es otra cara | **escena**: camisa blanca **con polvo/manchas** (el prompt pide dust-coated); la ropa de la escena pisa a la de la madre | reloj de pulsera en el hombre de la derecha (posible, no claro); menor |
| L1 #5 ch03_img_16 (1962, pista) | **parcial**: pareja bajando por la escalerilla, casas de chapa, polvareda sobre la garganta, sol duro; **pero el avión es un jet ejecutivo moderno (estilo Gulfstream) con una hélice pegada en la nariz y turbinas en la cola**, y la pista es asfalto negro, no tailings gris-azulado | 7 (chico en el cuadro; pelo, cejas, cara compatible) | 0 | **escena**: camisa clara con manchas y pantalón oscuro (el prompt pide work shirt) | **sí**: el avión (jet de los 80–2000 con hélice) |
| L1 #6 ch04_img_07 (1963, hospital) | **sí** (solo, anochecer, ventana iluminada, calle de tailings, cerros); el edificio es de 2 plantas de revoque, no «low fibro-cement», menor | **8–9** (de frente, misma cara; pelo algo más abundante) | 0 | **escena**: camisa clara **muy sucia de polvo** (el prompt pide dust in his work shirt) | ninguno |
| L2 #1 ch04_img_09 (1962, bocamina) | **sí**: bocamina con portal de madera, paredes rojas, polvo en suspensión, tailings; **los mineros de espaldas y él aparte, mirando a cámara** (en la Etapa 0 estaban todos de frente) | **9** (de frente) | **0** (los demás de espaldas o de perfil lejano) | **mixta**: mameluco de trabajo sucio (escena) sobre **la camisa clara de la madre** asomando en el cuello | cascos (válidos en 1962); ninguno |
| L2 #2 ch04_img_14 (1963, pista con bebé) | **sí**: familia de espaldas, bebé envuelto, valijas junto a la avioneta de ala alta, pista de tailings gris-azulada, cañón rojo, hora dorada, sombras largas | de espaldas | 0 | **escena**: mameluco/camisa gris de trabajo | ninguno (avioneta tipo Cessna de ala alta, plausible en 1963) |
| L2 #3 ch05_img_05 (1966, Madrid) | **sí**: familia de espaldas entrando por el portal de un bloque de ladrillo con balcones de hierro, calle estrecha, luz nublada | de espaldas | 0 | **escena**: chaqueta oscura y pantalón | leves: aparato cuadrado en la fachada (¿portero eléctrico/caja?) y buzón metálico modernos; el nene con una especie de buzo con capucha; calle sin un solo coche ni cartel (demasiado limpia) |

#### Segunda mirada independiente (subagente: recibió solo la madre nueva, las 9 fotos de `e0b/` y el prompt de cada escena; ni la hoja ni nada de `e0/`) — íntegra

#### 1) Foto madre `madre_daniel_ecija.png`
Hombre de ~22–26 años, retrato frontal tipo carnet, fondo gris-azulado liso con grano/rayas de foto vieja. Pelo castaño oscuro casi negro, corto, peinado hacia atrás/costado con flequillo apenas levantado. Cejas gruesas y oscuras, ojos marrones grandes, nariz recta, boca cerrada y seria, orejas algo salidas. **Sin barba**: solo sombra de afeitado leve en mentón y bigote. Expresión neutra/seria, mirada a cámara. **Ropa: camisa blanca-crema (blanco roto) de cuello abierto, sin corbata, limpia, sin manchas ni polvo.** Nada más visible (busto solo).

#### 2) Tabla

| foto | ¿es la escena pedida? | cara de la madre (1–10) | contagio (caras-madre de más) | ropa del protagonista | anacronismos |
|---|---|---|---|---|---|
| lote1/01_ch02_img_01 (baile 1961) | **Parcial**. Salón ornamentado con arañas, molduras doradas, parquet, parejas bailando, luz cálida: todo OK. Pero NO es plano abierto a altura de ojos: es plano medio-cerrado de la pareja en perfil (los bustos ocupan el cuadro). Ella trae un vestido/blusa crema lisa sin forma 1961, no «cotton-satin dress» hasta la rodilla. | **8** (de perfil: ceja gruesa, nariz recta, pelo oscuro peinado atrás, mentón; afeitado igual). Perfil dificulta la certeza plena. | 0 (los demás están desenfocados; ninguno con cara madre). | **La de la escena**: traje oscuro de solapa estrecha, camisa blanca, corbata negra. Correcto. | Ninguno visible. |
| lote1/02_ch02_img_02 (puerto 1962) | **Sí**. Transatlántico, grúas, muelle, multitud de emigrantes, carros de equipaje, maletas de cartón, mañana clara, ángulo bajo que enfatiza el barco. Él con traje y sombrero, ella con vestido claro y abrigo claro. | **De espaldas / 3/4 trasero**: solo se ve mejilla y oreja; rasgos insuficientes para juzgar. Pelo oscuro bajo el sombrero coincide. | 0 (multitud de fondo sin cara madre reconocible). | **La de la escena**: traje oscuro planchado + sombrero fedora. Correcto. | Ninguno; sombreros/maletas coherentes con los 60. |
| lote1/03_ch02_img_04 (cubierta 1962) | **Parcial**. Cubierta de paseo, mar, pasajeros desenfocados, luz suave de tarde, profundidad corta, ella bajo su brazo: OK. Pero es plano frontal (no 3/4) y el matrimonio mira a cámara en pose de retrato, no «caminando». | **10** – es la madre sin ninguna duda (misma ceja, ojos, nariz, boca, afeitado, peinado, mirada). | 0. | **Se parece a la madre**: camisa blanco-crema de cuello abierto, limpia. El prompt pide «shirtsleeves» así que es compatible con la escena, pero coincide exactamente con la camisa de la madre (mismo color, mismo cuello). | Ninguno. |
| lote1/04_ch02_img_05 (veranda Wittenoom) | **Sí** (con matiz). Casa de chapa acanalada + fibro, tierra roja, lámpara cálida, atardecer, plano desde el patio, dos parejas, hombres con camisas sucias, mujeres con vestidos de algodón. Matiz: las 4 personas posan sentadas mirando a cámara, no «comparten una velada». | **Dos candidatos**: hombre izquierdo **7** (ceja, nariz, boca, pelo muy parecidos; cara algo más redonda). Hombre derecho **5** (mismo pelo y cejas, nariz más ancha y piel más oscura). Sin zoom al original no puedo cerrar cuál es «el» protagonista. | **1** cara-madre de más: el segundo hombre es una variante clara del mismo rostro (contagio al «otro» marido). | **La de la escena**: camisa clara manchada de polvo/tierra marrón (ambos hombres). Correcto — pero la base es otra vez la camisa crema de la madre, ahora ensuciada. | Hombre derecho lleva **reloj de pulsera moderno (correa negra tipo deportiva)** en la muñeca izquierda. Lámpara de mesa eléctrica de pantalla: plausible pero el modelo luce contemporáneo. |
| lote1/05_ch03_img_16 (pista Wittenoom) | **Parcial / no**. Hay avión con hélice, pista oscura de relaves, casas de chapa, cañón y pluma de polvo, sol duro: OK. PERO el avión es **un jet ejecutivo bimotor tipo Gulfstream** (turbinas en cola, ventanillas ovales, escalera integrada) con una hélice pegada en el morro: híbrido absurdo, no «small propeller aircraft» de 1962. La pareja no está en primer plano desde ángulo bajo sino lejos y chica. | **5**: cara muy pequeña; pelo oscuro, cejas marcadas y complexión delgada compatibles, pero el rostro casi no tiene resolución; **parece tener gafas de sol** (sombra oscura en los ojos) lo que impide comparar. | 0. | **Mixta**: camisa clara (crema) con manchas marrones + pantalón oscuro. Compatible con «work shirt and trousers», pero otra vez la camisa de la madre. | **Jet ejecutivo** (anacronismo mayor, modelo ~1970s–2000s); posibles **gafas de sol**; las casas de chapa pintadas de azul claro con ventanas modernas en el borde derecho. |
| lote1/06_ch04_img_07 (hospital de noche) | **Parcial**. Hombre solo, noche, edificio bajo con una ventana iluminada, calle de relaves, cerros: OK. Pero es plano medio-cerrado frontal, no «wide shot from across the street»; el edificio es de dos plantas y cemento, no «low fibro-cement». | **9**: misma ceja, ojos, nariz, boca, afeitado, pelo; mirada hacia un lado, muy reconocible. | 0. | **La de la escena**: camisa clara MUY manchada de polvo/grasa (base crema igual a la madre, pero ensuciada). Correcto. | Lámpara fluorescente en la ventana superior (tubo blanco), plausible pero dudoso en Wittenoom 1963. Nada grave. |
| lote2/01_ch04_img_09 (bocamina tras la voladura) | **Sí**. Mineros de espaldas con cascos, portal de madera, paredes rojas, relaves, polvo que vela la luz, uno apartado en primer plano a la derecha. | **9–10**: es la madre de frente, sin duda (cejas, ojos, nariz, boca, afeitado, peinado). | 0 (todos los demás de espaldas o de perfil sin rasgos). | **Mixta**: camisa crema de cuello abierto (= madre, limpia bajo el mono) + **mono/overol de trabajo con tirantes** color tierra polvoriento encima. El mono es coherente con la escena; la camisa de abajo es la de la madre. | Los cascos son redondos tipo «salacot/casco de bombero» uniformes, aceptables. Ninguno moderno visible. |
| lote2/02_ch04_img_14 (familia a la pista, de espaldas) | **Parcial**. Familia de espaldas, pista de relaves oscura, avioneta de hélice (Cessna de ala alta, correcto para «small propeller aircraft»), maletas, cañón al fondo, sombras largas: OK. Pero NO es ángulo bajo (es a altura de ojos) y la mujer tiene **pelo negro largo suelto** (no coincide con la esposa de las otras fotos, recogida), vestido sin mangas con infante en brazos: bien. | **De espaldas**: imposible juzgar; pelo oscuro compatible. | 0. | **No la de la madre**: mono/overol gris-verdoso de una pieza (coherente con «work shirt» laxamente; más mono que camisa). | Avioneta Cessna de ala alta con ruedas carenadas: modelo ~1970s+ pero tolerable. Zapatillas/calzado claro de él poco definido. Mujer con pelo largo suelto estilo contemporáneo. |
| lote2/03_ch05_img_05 (Madrid 1966, de espaldas) | **Sí**. Familia de espaldas entrando por el portal de un bloque de ladrillo con balcones de hierro, calle estrecha, cielo nublado, visto desde enfrente. Él con chaqueta oscura y pantalón, ella con blusa clara y falda negra, niño de la mano. | **De espaldas**: no juzgable. | 0. | **La de la escena**: chaqueta oscura tipo cazadora + pantalón oscuro (no se ve camisa). Correcto. | **Caja/aparato gris en la fachada (parece timbre/portero o cámara/alarma moderna)** sobre la puerta; **buzón metálico moderno** a la izquierda del portal; rejas y ventanas lucen contemporáneas; calle asfaltada muy limpia con cordones modernos. El niño con **sudadera gris de capucha/cuello redondo y zapatillas** (anacrónico para 1966). |

#### 3) Conclusiones
**(a) Consistencia de identidad**: muy alta en las fotos donde la cara se ve de frente (03, 06, lote2/01 = 9–10; 01 de perfil 8). Donde la cara es pequeña (05) o de espaldas (02, lote2/02, lote2/03) no se puede verificar; en 04 la identidad se duplica en los dos hombres, con el izquierdo como mejor candidato. La «esposa» no es consistente entre fotos (recogido castaño en 01–04, pelo negro largo suelto en lote2/02).

**(b) Arrastre de la ropa de la madre**: sí, claro. La camisa crema de cuello abierto de la madre aparece como base en 03 (idéntica, limpia), 04, 05, 06 (ensuciada con polvo) y lote2/01 (debajo del mono). Solo se rompe cuando el prompt impone prenda fuerte y distinta: traje (01, 02), mono (lote2/02), chaqueta (lote2/03). Como para las escenas de mina «work shirt» ≈ camisa clara sucia, el arrastre es tolerable ahí; en 03 (cubierta) el modelo directamente copió la camisa de la madre.

**(c) Rarezas**: 05 es el problema serio: **jet ejecutivo con hélice pegada**, pareja chiquita y con gafas de sol aparentes. 04: **reloj moderno** en el segundo hombre + duplicación de la cara. lote2/03: fachada con **caja/cámara y buzón modernos**, niño con **sudadera y zapatillas**. No vi texto legible, carteles ni miembros extra en ninguna de las 9. Varias fotos (03, 04, 06) tienen pose «retrato mirando a cámara» en vez de la acción pedida, y los planos «wide» salen como plano medio (01, 03, 06).

**Nota de CC sobre la segunda mirada:** coincide con la mía en identidad (9–10 de frente), contagio (solo ch02_img_05, 1 cara) y en que la camisa clara de la madre sigue de base cuando la escena no impone otra prenda; difiere en que el subagente marca como «parcial» los planos que salieron más cerrados que el «wide» pedido (ch02_img_01, ch02_img_04, ch04_img_07) y las poses de retrato; yo lo di por escena cumplida con matiz. Lo del avión (ch03_img_16) lo vimos los dos.

### 0b.4 Comparación con la Etapa 0 en las 3 fotos repetidas (lote 2)

| foto | Etapa 0 (madre con camisa manchada) | Etapa 0b (madre con camisa limpia) | ¿desapareció el arrastre de las manchas? |
|---|---|---|---|
| ch04_img_09 | 8 mineros en fila **todos de frente**, nadie aparte; madre en el 7.º y parecido en el 6.º (contagio 2); camisa manchada de la madre | mineros **de espaldas**, Daniel **aparte** de frente; contagio 0; mameluco de trabajo sucio con la camisa clara limpia abajo | **sí** (la suciedad que hay es la del mameluco que pide la escena, no la mancha de la madre) |
| ch04_img_14 | familia de espaldas; el hombre con la camisa manchada de la madre | familia de espaldas; mameluco gris de trabajo sin manchas marcadas | **sí** |
| ch05_img_05 | familia de espaldas; el hombre con la camisa manchada en Madrid 1966 | el hombre con chaqueta oscura y pantalón (lo que pide la escena) | **sí** |

Lectura: con la madre limpia el modelo pone la ropa que dice cada escena (traje, sombrero, mameluco, chaqueta) y solo deja la camisa de la madre cuando la escena pide «shirtsleeves» o la deja asomar bajo el mameluco. El cambio de composición en ch04_img_09 (de espaldas / aparte) puede ser también efecto de la seed; no se puede atribuir solo a la ropa.

### 0b.5 Hoja

`e0b/hoja_madre_0b.jpg` (fuera de git): madre 0b arriba a la izquierda y la madre de la Etapa 0 al lado; por fila foto 0b | foto de la Etapa 0 del mismo slot. Solo tienen par las 3 de `e0/lote2/`; las 6 del lote 1 llevan la celda derecha vacía con la leyenda «sin foto de la Etapa 0: el lote 1 se cortó».

### 0b.6 Gasto total (precio real de fal, GET `api.fal.ai/v1/models/pricing`, 0,035 US$/imagen en los dos endpoints × devueltas)

| endpoint | qué | imágenes | US$ |
|---|---|---|---|
| `fal-ai/bytedance/seedream/v5/lite/text-to-image` | madre | 1 | 0,035 |
| `fal-ai/bytedance/seedream/v5/lite/edit` | lote 1 | 6 | 0,21 |
| `fal-ai/bytedance/seedream/v5/lite/edit` | lote 2 | 3 | 0,105 |
| **total Etapa 0b** | | 10 | **0,35** |

(Etapa 0: 0,14 confirmado + 0,21 probable del lote cortado; queda como está, no se intentó recuperar.)

### Lo que queda abierto (Etapa 0b)

1. **`has_nsfw_concepts` no viene** en la respuesta de v5 Lite (ni en t2i ni en `/edit`): se reporta `None`. Si hace falta ese dato, hay que mirar qué devuelve el schema de salida (en la Etapa 0 tampoco vino).
2. **Anacronismo del avión en ch03_img_16** (jet ejecutivo con hélice en la nariz): error del modelo frente a «small propeller aircraft»; en ch04_img_14 la avioneta sí salió bien. Es tema del prompt/escena, no de la madre.
3. **Contagio débil en ch02_img_05** (el segundo hombre se parece a la madre): con dos parejas en escena el modelo tiende a reutilizar la cara. En la Etapa 0 el contagio fue más fuerte (2–3 caras de 8).
4. **La camisa de la madre asoma** bajo el mameluco en ch04_img_09 y es la camisa de ch02_img_04 («shirtsleeves»): es compatible con las escenas, pero muestra que la ropa de la madre sigue entrando cuando la escena no la pisa.
5. **Composición de ch04_img_09:** esta vez el modelo respetó «mostly seen from behind» y «standing apart»; no se sabe si fue la ropa limpia, la seed o azar (una corrida).
6. **Detalles modernos en ch05_img_05** (aparato en la fachada, buzón, buzo con capucha del nene): leves, pero son del tipo que Omar marca.
7. **ch04_img_07:** el hospital salió de 2 plantas de revoque en vez de «low fibro-cement building»; la escena se entiende igual.
8. El gasto probable de US$ 0,21 del lote cortado de la Etapa 0 sigue sin confirmar (no se intentó recuperar: fue síncrono, sin `request_id`).
9. Sigue pendiente de la Etapa B.1 sacar «miner» del canon sin lista de palabras (PARÁ previo).

### Veredicto de revisor-handoff — Etapa 0b (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Handoff íntegro, md5 30a632c5… | OK | `md5sum` coincide. |
| 2 | 2 líneas de Decisiones en DECISIONES.md, texto tal cual | OK | `git diff DECISIONES.md`: 2 líneas nuevas al final, texto idéntico al handoff (17:48, «F60 0b», Omar · F60). |
| 3 | Terminaciones CRLF en esas líneas | PARCIAL | El archivo no tiene ningún CR (`grep -c $'\r'` = 0): todo el archivo es LF, líneas viejas incluidas. Las nuevas son consistentes con «el resto», pero el handoff decía CRLF. |
| 4 | Runner = copia de etapa0 con solo los 4 cambios | OK | Diff `etapa0_secuencia.py` → `etapa0b_secuencia.py`: cola, orden y paralelo, `ROPA_MADRE` y carpeta `e0b`. Las otras diferencias son andamiaje de esos cambios (Lock, `_volcar`, aborto si hay lotes sin madre, manejo de errores, `PROMPT_MADRE_ESPERADO`). |
| 5 | Usa `_clip_poll`, `_fal_headers`, `FLUX_MAX_WORKERS` y `api.fal_base_url` importados, submit timeout 60 | OK | `etapa0b_secuencia.py` líneas ~97-117 y ~265 (`ThreadPoolExecutor(min(len, am.FLUX_MAX_WORKERS))`); `SUBMIT_TIMEOUT_S = 60`. |
| 6 | request_id guardado antes de esperar; `status_url` y `response_url` tal como los devuelve el submit; sin duplicados | OK | `_guardar_pedido` va antes del poll. `pedir_o_reanudar` retoma el request_id guardado sin volver a pedir. Las URLs en `etapa0b_pedidos.json` traen `/requests/<id>/status`, sin `/edit`. |
| 7 | Prompt de la madre byte a byte | OK | `prompt_madre` en `etapa0b.json` es idéntico al del handoff (`prompt_madre_igual_al_handoff: true`). Comparé a ojo el repr con el handoff y coincide. |
| 8 | Madre sola y antes; los 2 lotes a la vez | OK | Madre 18:01:15 → 18:01:52. Lote 1 y lote 2 enviados ambos a las 18:01:54, con la madre ya en disco. |
| 9 | Números de SALIDA_0b = etapa0b.json / .log | OK | 37,8 s; 283,0 s (47,2 s/foto); 145,7 s (48,6 s/foto); pared 286,1 s; seeds 460661449 / 1780408611 / 1200455859; los 3 request_id; US$ 0,035 + 0,21 + 0,105 = 0,35. Todo coincide. |
| 10 | Precios del GET de pricing | OK | `precio_t2i` y `precio_edit` en el json: 0,035 US$/imagen, endpoint y unidad devueltos por `api.fal.ai/v1/models/pricing`. |
| 11 | Sin números nuevos fuera de la tabla de constantes | OK | Solo 6, 60, 2560×1440, 1962 y la frase de ropa. Los 600 s, el 20 y el poll de 5 s vienen de `asset_manager`. |
| 12 | Sin reintentos; errores sin tapar | OK | Log sin errores; ningún pedido con `reanudado`; 1 submit por llamada (3 request_id distintos). |
| 13 | `has_nsfw_concepts` tal como viene | OK | Se reporta `None` / «no viene» en la madre y los lotes. En el json `madre.width` y `height` salen `None`; la SALIDA dice 2560×1440 (las dimensiones de las 9 fotos no las medí). |
| 14 | Producción intacta; `e0/` y `etapa0_secuencia.py` intactos | OK | `git status`/`git diff` no muestran `asset_manager`, `foto_madre`, m03, m06 ni `qa_studio_server` tocados. `etapa0_secuencia.py` sin cambios. `e0/` figura como `??` entero (nunca se commiteó) y no puedo probar que no se editó. |
| 15 | Imágenes y hojas fuera de git | OK | `git diff --cached` vacío. Las imágenes de `e0b/` están sin trackear, ninguna staged. |
| 16 | Hoja `hoja_madre_0b.jpg` | OK | Vista con Read: madre 0b arriba y madre Etapa 0 al lado; 3 filas con par 0b / Etapa 0; las 6 del lote 1 con celda vacía rotulada. |
| 17 | Contraste visual con la tabla de CC | OK | La madre 0b trae camisa crema limpia y la de la Etapa 0, camisa oscura manchada. ch04_img_09: mineros de espaldas con cascos y Daniel aparte, de frente. Se ve el jet con hélice en ch03_img_16 y la camisa de la madre en ch02_img_04. En ch04_img_14 y ch05_img_05 las familias van de espaldas. |
| 18 | SALIDA_0b con los 7 puntos, tabla de 9 fotos con 2 miradas, «Lo que queda abierto» | OK | Existen 0b.1–0b.6 y la lista de abiertos. La segunda mirada se pega íntegra. |
| 19 | Independencia del subagente (sin ver `e0/` ni la hoja) | NO VERIFICABLE | Solo consta la declaración de CC. Falta el prompt o el registro del subagente. |
| 20 | Sección «Etapa 0b» en F60_REPORT.md | PARCIAL | Existe (línea 174, con tabla y abiertos). Todavía no trae el veredicto del revisor: el único «VEREDICTO» del archivo es el de la Etapa 0 (línea 131). Este veredicto es el que falta pegar. |
| 21 | `lab/ESTADO_SESION.md` actualizado y commit con paths explícitos | NO VERIFICABLE / PENDIENTE | `ESTADO_SESION.md` no figura modificado. No hay commit nuevo: HEAD sigue en 2eadb52. El pedido del analista no mencionaba el commit, pero el handoff lista `ESTADO_SESION.md` entre los paths. |
| 22 | PARADA 0b, sin pasar a la Etapa A | OK | Nada de la Etapa A en el diff. |

Fuera de alcance: ninguno. Las `??` de `hoja_caras_lote2.jpg` y `hoja_madre_secuencia.jpg` son restos de la Etapa 0, sin trackear. `diag_234_cap4.py` y `f28a.log` ya figuraban modificados en el git status inicial, no son de esta tanda.

Observaciones:
1. CRLF: ver fila 3. Ninguna línea de DECISIONES.md lleva CR, y el handoff pedía CRLF.
2. Afirmación incorrecta en SALIDA_0b: dice que «la mancha ya no se arrastra a las escenas». Lo que se ve es que la camisa limpia de la madre es la base en ch02_img_04, en ch02_img_05 (ensuciada), ch03_img_16, ch04_img_07 y debajo del mono en ch04_img_09. El propio texto lo reconoce más abajo (abiertos 4). La línea de resumen es más optimista que su propia tabla.
3. Las dos miradas discrepan en 3 de las 9 fotos. CC dice «sí» en ch02_img_01, ch02_img_04 y ch04_img_07, y el subagente «parcial» (planos más cerrados que el pedido, pose de retrato). CC lo anota, pero la tabla de CC queda más favorable. ch04_img_14 también es «parcial» para el subagente (ángulo, pelo de la esposa) y «sí» para CC, sin que la nota de CC lo mencione.
4. El anacronismo del jet con hélice en ch03_img_16 está reportado, y también el reloj de pulsera y la sudadera con capucha. Es lo que pide el handoff.
5. En ch04_img_09 el cambio de composición no se puede atribuir a la ropa: es una sola corrida. CC lo dice, y lo confirmo.
6. `etapa0b.json` no guarda `width` ni `height` de la madre. Quedan solo en el texto de SALIDA.

Riesgos que el contrato no cubre: una sola semilla por lote, sin réplica, así que «madre limpia → arrastre resuelto» es anecdótico con n=1. La frase de ropa clara hace que la camisa crema sea la base por defecto de cualquier escena de «work shirt». Con 2 pedidos en paralelo y 283 s en el lote de 6, un lote más grande (12 fotos, límite de 600 s) queda sin medir.

#### Adenda de CC
- **Fila 3 / obs. 1 (CRLF):** no se reproduce. `DECISIONES.md` leído en bytes tiene 190 terminaciones `\r\n` y 0 `\n` sueltos, y las 2 líneas nuevas terminan en `\r\n` (`git diff | cat -A` muestra `^M$`). El `grep -c $'\r'` del revisor corrió en Git Bash, que puede convertir el CR al leer; el archivo está en CRLF como el resto.
- **Obs. 2:** cierto; la línea de resumen de SALIDA_0b y de la sección 0b del reporte quedó corregida: «las manchas de la Etapa 0 ya no se arrastran, pero la camisa clara de la madre sigue siendo la base en las escenas que no imponen otra prenda».
- **Obs. 3:** la nota de CC al pie de la segunda mirada ya decía que el subagente marca «parcial» los planos cerrados; se agrega aquí que también difiere en ch04_img_14 (ángulo a altura de ojos y pelo suelto de la esposa). Las dos tablas van íntegras; el analista decide con las dos.
- **Obs. 6:** se agregó `medido_pil` (ancho, alto medidos con PIL) a la madre y a las 9 fotos en `etapa0b.json`, en un campo aparte; `width`/`height` siguen `None` tal como los devuelve fal.
- **Fila 19:** el brief del subagente nombraba solo `e0b/madre_daniel_ecija.png`, las 9 fotos de `e0b/lote1|lote2` y los prompts, y le prohibía `e0/` y las hojas; el registro del subagente queda en el transcript de la sesión, no en el repo.
- **Filas 20 y 21:** este veredicto se pega ahora; ESTADO y el commit con los paths del handoff van después del veredicto, como en las tandas anteriores.
