# F60 — Salida 0 (prueba de secuencia en lab, SIN tocar producción) — PARADA 0

Handoff `lab/hyperframes/f60/HANDOFF_F60_madre_personas_secuencia.md` (md5 `a2e7e8cb4a6e62c52fdccc5b58c7b1ac`, verificado). Copia de lab `lab/hyperframes/f60/base/` hecha con `lab/hyperframes/f60/copia_lab.py` (copia del método de F59; producción intacta: guion vivo `f762dc48…` antes y después, `_steps` sin cambios; 230 archivos, 629,9 MB; log en `copia_lab.log`). Runner: `lab/hyperframes/f60/etapa0_secuencia.py` → `etapa0.json`, `etapa0.log`, imágenes en `e0/` (fuera de git).

**Resultado en una línea:** la madre salió bien; el lote de 6 fotos **no entró en el timeout existente de 240 s** (`_generate_image_raw`, asset_manager.py) y se perdió; el lote de 3 fotos tardó 142,5 s, devolvió 3/3, escena i = imagen i en las 3, y la cara de la madre aparece en la única foto que muestra caras (con contagio a un segundo minero). **PARÁ** por el punto «timeout de la llamada de secuencia … si alguno no alcanza para N fotos, PARÁ y mostrá la medición».

## 0.1 Schema de `fal-ai/bytedance/seedream/v5/lite/edit` (GET, método de f52; crudo en `schema_edit_v5_lite.json`)

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

## 0.2 Madre de Daniel Écija (Seedream v5 Lite t2i, `model_id` del perfil, `image_size` {2560×1440} del perfil)

Datos reales usados (a mano, Etapa B.1):
- `appearance_canon` (05_visual_canon): «a young adult Spanish migrant miner in work clothes, one foot visibly bandaged» → recortado sin ropa ni estado del cuerpo: «a young adult Spanish migrant miner».
- `people_group` más frecuente en las 9 fotos de Daniel de la tabla: `spanish_migrant_families` ×8, `mine_and_mill_workers` ×1 → appearance «Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes.»
- año = primer número de 4 dígitos de `era` «1962-1963» → **1962**. `ESTILO_C` y `NO_TEXT` reusados de `m03_imagenes_v3` (sin «faceless»).

Prompt (el que fue a fal):

    Head-and-shoulders portrait of a young adult Spanish migrant miner. Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes. Neutral expression, facing the camera, plain mid-grey background, soft even light. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight underexposure, in a dark-history realist style. No readable text, no signage, no labels.

Payload: `{"prompt", "image_size": {"width": 2560, "height": 1440}, "num_images": 1, "enable_safety_checker": true}` (espejo de `_seedream_payload_for`; v5 Lite no acepta seed). Resultado: **26,9 s**, seed devuelto 143986887, 2560×1440 (JPEG con extensión .png, como en producción), US$ 0,035. Foto: `e0/madre_daniel_ecija.png` (arriba en la hoja). Es un hombre joven de pelo oscuro corto, barba de pocos días, mirando a cámara, fondo gris, camisa de trabajo manchada (la ropa la puso el modelo aunque el prompt no la pide).

## 0.3 Lotes de secuencia (`/edit`, `image_urls=[madre]`, `max_images=len(lote)`, `sequential_image_generation="auto"`, `num_images=1`, `image_size` del perfil, timeout 240 s)

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

## 0.4 Gasto

| servicio | qué | US$ |
|---|---|---|
| fal Seedream v5 Lite t2i | madre | 0,035 |
| fal Seedream v5 Lite /edit secuencia | lote 2, 3 imágenes | 0,105 |
| **total confirmado** | | **0,14** |
| fal /edit secuencia (probable, sin confirmar) | lote 1, 6 imágenes que fal pudo haber generado tras el timeout | 0,21 |

`cost_tracker` no se usó (el handoff pide el precio de fal, y `track_seedream` tiene tarifa fija); los valores son `unit_price × imágenes devueltas`.

## 0.5 DECISIONES.md
Las 4 líneas de «Decisiones» del handoff, tal cual, al final de `DECISIONES.md` (CRLF), con una línea de encabezado «F60 (handoff …, «Decisiones», tal cual)».

## Lo que queda abierto (Etapa 0)
1. **Timeout para 6 fotos** (PARÁ): 240 s no alcanza; 3 fotos = 142,5 s. Decisión del analista/Omar: un timeout para la llamada de secuencia (p. ej. proporcional a N) o pasar la secuencia por la cola de fal (`queue.fal.run`) con un poll largo. Sin ese número no se repite el lote 1.
2. El lote de 6 no se vio: no hay medida de contagio ni de «escena i = imagen i» con 6; con 3 dio 3/3 en escena y 2 caras-madre de 8 en la única foto con caras.
3. En la foto 1 el modelo ignoró «mostly seen from behind» y «standing apart» y puso a todos de frente; con una madre en `image_urls`, `/edit` tiende a mostrar la cara. Pendiente ver si pasa con más lotes.
4. La ropa de la madre (camisa de trabajo manchada) la puso el modelo; el prompt no la pide.
5. Precio real de la llamada cortada: no verificable desde la API.
6. Los PNG «viejos» de la copia no corresponden a los prompts de 03_visual en 2 de las 3 fotos del lote 2 (y en 6 de 9 del total): la comparación cara nueva vs t2i vieja casi no tiene par.
