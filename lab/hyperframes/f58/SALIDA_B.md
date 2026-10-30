# F58 — Salida B (Wittenoom real)

Comando: `python -m script_engine.m09_packaging 123bbb64-9fca-4395-8bf4-57d60e219ef1 --candidates` (vía `main()` con ese argv, dentro de `cost_tracker.start_video('f58_parte_b')`). 199.9 s de reloj. Topic `123bbb64-9fca-4395-8bf4-57d60e219ef1`.

## 1. Los 3 paquetes

### Paquete 01 — 1

- **Título** (64 caracteres): Vivió 10 meses junto a una mina de amianto azul y murió a los 55
- **Texto**: «¿QUÉ RESPIRÓ ALLÍ?»
- **Ancla** (oración literal del gancho): «Ese pie va a cerrar; lo que respira mientras espera que cierre va a tardar casi treinta años en matarlo, y lo va a alcanzar a miles de kilómetros de aquí.»
- **cap_que_paga**: 5
- **dato_ids**:
  - `D87`: La familia Écija-Bernal vivió en Wittenoom unos 10 meses, entre 1962 y 1963.
  - `D89`: Daniel Écija padre murió de mesotelioma a los 55 años, nueve meses después de su diagnóstico.
  - `D35`: El asbesto azul (crocidolita), el tipo que se extraía en Wittenoom, es el más mortal de todos los tipos de asbesto.
  - `D85`: Daniel Écija padre se hirió el pie con un trozo de amianto y la herida no se cerraba.
- **Avisos**: ninguno
- **Foto**: paquete_01_base.png · año 1963 (1) el casillero `year` del modelo)
- **Compuesta**: paquete_01.png · base paquete_01_base.png

### Paquete 02 — 3

- **Título** (60 caracteres): Sabían del polvo desde 1944: la mina que mató a Daniel Écija
- **Texto**: «LO LLAMARON ALBOROTADOR»
- **Ancla** (oración literal del gancho): «La familia que la guarda cuenta que le cayó encima un trozo de amianto y que la herida no cerraba.»
- **cap_que_paga**: 3
- **dato_ids**:
  - `D19`: El Inspector de Minas y el Ingeniero de Minas Adjunto del Estado informaron sobre el problema del polvo ya en 1944.
  - `D89`: Daniel Écija padre murió de mesotelioma a los 55 años, nueve meses después de su diagnóstico.
  - `D92`: En 1948, el doctor Eric Saint advirtió por escrito que los niveles de polvo en Wittenoom eran extremadamente peligrosos.
  - `T19`: 1948 · El doctor Eric Saint advirtió por escrito sobre los peligrosos niveles de polvo en la mina.
- **Avisos**: ninguno
- **Foto**: paquete_02_base.png · año 1963 (1) el casillero `year` del modelo)
- **Compuesta**: paquete_02.png · base paquete_02_base.png

### Paquete 03 — 4

- **Título** (63 caracteres): Wittenoom, 1963: el pueblo de amianto que borraron de los mapas
- **Texto**: «NADIE SACÓ UNA PALADA»
- **Ancla** (oración literal del gancho): «Lo que sobró de la mina, en cambio, sigue donde lo dejaron.»
- **cap_que_paga**: 7
- **dato_ids**:
  - `T40`: 1963-06 · Nació Daniel Écija Bernal en el hospital de Wittenoom.
  - `T41`: 1963-07-07 · La familia Écija-Bernal bautizó a su hijo Daniel y poco después abandonó Wittenoom.
  - `D31`: En junio de 2007, el sitio del pueblo de Wittenoom fue oficialmente desclasificado y su nombre eliminado de los mapas y señales de tráfico oficiales.
  - `D71`: No se ha retirado ni una sola palada de asbesto de la tierra Banjima.
  - `D02`: Se estima que los relaves de la minería, que contienen alrededor de un 5% de asbesto, superan los 3 millones de toneladas.
- **Avisos**: ninguno
- **Foto**: paquete_03_base.png · año 2026 (1) el casillero `year` del modelo)
- **Compuesta**: paquete_03.png · base paquete_03_base.png

## 2. Los 3 prompts de foto (enteros)

### Paquete 01

**prompt (el que fue a Seedream):**

    A young adult Spanish migrant miner, olive skin, short dark early-1960s hair, lean work-hardened build, sun-weathered face, in a dust-coated short-sleeved work shirt and drill trousers, one foot wrapped in a pale bandage and the other in a heavy work boot. Stands posing stiffly for a family portrait, weight shifted onto his good leg, the bandaged foot set forward on the ground. Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes. Wittenoom company town, 1963: in front of a low corrugated-iron and fibro-cement company house, its yard surfaced with crumbly blue-grey crocidolite tailings. Hard cold overcast desert light, flat and shadowless, isolating the figure against the pale wall. Medium shot, eye-level, frontal like a period box camera, 50mm lens, moderate depth of field, slightly soft period film grain. The person fills the right half of the frame, face and torso large; the left half is dark, uncluttered negative space. A grainy 35mm documentary photograph taken in 1963, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.

**raw_llm_prompt (casillero de Opus):**

    {"subject": "A young adult Spanish migrant miner, olive skin, short dark early-1960s hair, lean work-hardened build, sun-weathered face, in a dust-coated short-sleeved work shirt and drill trousers, one foot wrapped in a pale bandage and the other in a heavy work boot", "action": "Stands posing stiffly for a family portrait, weight shifted onto his good leg, the bandaged foot set forward on the ground", "gaze_interaction": "Face and eyes square to the camera, shoulders slightly drawn up, a guarded half-smile, arms hanging straight at his sides", "setting": "Wittenoom company town, 1963: in front of a low corrugated-iron and fibro-cement company house, its yard surfaced with crumbly blue-grey crocidolite tailings", "color_palette": "Desaturated black-and-white tonality with a cold blue-grey cast; pale grey fibro walls, dull grey corrugated iron, washed-out red-ochre earth", "props_detail": "The pale bandage around his foot, its edges greyed by a fine fibrous dust", "shot_scale": "medium", "camera_angle": "eye-level, frontal like a period box camera", "lens_technique": "50mm lens, moderate depth of field, slightly soft period film grain", "lighting": "Hard cold overcast desert light, flat and shadowless, isolating the figure against the pale wall", "mood": "A lone figure pinned under flat white sky, fine dust hanging in the air, a stiff pose held a beat too long", "style": "Documentary photographic realism, dark-history, faceless channel look, aged 1960s family snapshot", "text_in_image": {"present": false, "text": "", "font": "", "location": ""}, "hard_fact_ids": [], "people_group": ["spanish_migrant_families"], "year": "1963"}

### Paquete 02

**prompt (el que fue a Seedream):**

    The bandaged foot of a young Spanish migrant miner resting on tailings-surfaced ground, a dusty trouser cuff above it, a jagged fragment of blue crocidolite asbestos lying beside it. The foot rests motionless while the loose fibrous fragment sheds fine threads and powder onto the bandage. Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes. A Wittenoom house yard, 1963, the ground compacted with loose blue-grey crocidolite tailings and red-ochre dust. Hard cold directional overcast light raking across the fibres. Detail shot, high angle looking down, macro-leaning 100mm lens, shallow depth of field, fibres sharp, background soft. The person fills the right half of the frame, face and torso large; the left half is dark, uncluttered negative space. A grainy 35mm documentary photograph taken in 1963, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.

**raw_llm_prompt (casillero de Opus):**

    {"subject": "The bandaged foot of a young Spanish migrant miner resting on tailings-surfaced ground, a dusty trouser cuff above it, a jagged fragment of blue crocidolite asbestos lying beside it", "action": "The foot rests motionless while the loose fibrous fragment sheds fine threads and powder onto the bandage", "gaze_interaction": "Focal direction drawn down to the pale bandage and the frayed blue-grey mineral fragment beside it", "setting": "A Wittenoom house yard, 1963, the ground compacted with loose blue-grey crocidolite tailings and red-ochre dust", "color_palette": "Cold blue-grey crocidolite tones, off-white greyed bandage, muted red-ochre dust, desaturated documentary grade", "props_detail": "A frayed chunk of raw blue asbestos unravelling into fine fibrous threads", "shot_scale": "detail", "camera_angle": "high angle looking down", "lens_technique": "macro-leaning 100mm lens, shallow depth of field, fibres sharp, background soft", "lighting": "Hard cold directional overcast light raking across the fibres", "mood": "Fine fibrous powder settling on the cloth, a dull stain spreading through the bandage weave, utter stillness", "style": "Documentary photographic realism, dark-history, faceless channel look", "text_in_image": {"present": false, "text": "", "font": "", "location": ""}, "hard_fact_ids": [], "people_group": ["spanish_migrant_families"], "year": "1963"}

### Paquete 03

**prompt (el que fue a Seedream):**

    Vast abandoned blue-grey asbestos tailings dumps spilling down the rocky red walls of a Pilbara gorge where the erased mining town once stood. The tailings lie exactly where they were dumped, eroding in slow streaks toward a dry creek bed, the empty town site beyond reduced to bare cleared ground. Wittenoom gorge in the present day: demolished, emptied town site, a permanent barricade across the old road entrance, sparse spinifex, 2026. Cold overcast daylight, flat and colourless over the gorge. Extreme wide shot, high angle aerial view, wide-angle lens, deep depth of field. The person fills the right half of the frame, face and torso large; the left half is dark, uncluttered negative space. A grainy 35mm documentary photograph taken in 2026, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.

**raw_llm_prompt (casillero de Opus):**

    {"subject": "Vast abandoned blue-grey asbestos tailings dumps spilling down the rocky red walls of a Pilbara gorge where the erased mining town once stood", "action": "The tailings lie exactly where they were dumped, eroding in slow streaks toward a dry creek bed, the empty town site beyond reduced to bare cleared ground", "gaze_interaction": "Focal direction pulls from the pale tailings slopes down the gorge toward the empty flat where the town stood", "setting": "Wittenoom gorge in the present day: demolished, emptied town site, no buildings, a permanent barricade across the old road entrance, sparse spinifex", "color_palette": "Desaturated red-ochre rock and earth, blue-grey crocidolite tailings, bleached grey sky, cold documentary grade", "props_detail": "A long scar of loose blue-grey tailings washing into a dry creek bed", "shot_scale": "extreme_wide", "camera_angle": "high angle aerial view", "lens_technique": "wide-angle lens, deep depth of field", "lighting": "Cold overcast daylight, flat and colourless over the gorge", "mood": "An immense silent landscape, wind lifting faint dust off the dumps, no living figure anywhere", "style": "Documentary photographic realism, dark-history, faceless channel look", "text_in_image": {"present": false, "text": "", "font": "", "location": ""}, "hard_fact_ids": ["F02"], "people_group": [], "year": "2026"}

## 3. Nombres de `documented_people` / `ficha.personas` en los prompts (medida, no freno)

Formas buscadas: 126 (nombre y variantes de las 56 personas de la ficha, sin paréntesis; `name` de los 22 `documented_people` del canon), palabra entera, sin distinguir mayúsculas.

Ningún prompt nombra a nadie.

## 4. Hoja

`lab\hyperframes\f58\hoja_paquetes.jpg` — las 3 miniaturas compuestas lado a lado (compuestas en `output/123bbb64-9fca-4395-8bf4-57d60e219ef1/publish/thumb_candidates/`; no van a git).

## 5. Descripción y tags

**Descripción** (1502 caracteres):

    Daniel Écija vivió unos 10 meses en Wittenoom y el amianto que respiró allí lo alcanzó décadas después en Madrid. En 1961, en el Círculo de Bellas Artes de Madrid, conoció a María Bernal en un baile; se casaron el 20 de septiembre de 1962 y cuatro días después emigraron a Australia, parte de los cerca de 8.000 españoles que llegaron con la Operación Canguro. Su destino fue Wittenoom, en la región de Pilbara, un pueblo minero de asbesto azul (crocidolita), el tipo más mortal de todos, explotado por Australian Blue Asbestos, filial de CSR. Con los relaves de la mina se hicieron la pista de aterrizaje, las carreteras y los patios donde jugaban los chicos. Las advertencias existían desde mucho antes: en 1944 el Inspector de Minas informó sobre el problema del polvo, en 1946 otro inspector llamó 'terroríficas' a las condiciones y en 1948 el doctor Eric Saint advirtió por escrito que los niveles de polvo eran extremadamente peligrosos. Aun así, la producción se incrementó en 1961. La mina cerró en 1966 por razones económicas. En 1991, Daniel fue diagnosticado con mesotelioma y murió nueve meses después, a los 55 años. Hoy Wittenoom no figura en los mapas oficiales, más de 3 millones de toneladas de relaves siguen en tierra Banjima y no se ha retirado ni una sola palada de asbesto. Esta es la historia de un hombre, de un pueblo borrado y de todos los que sabían. Suscribite para más historias que la historia oficial prefirió no contar.
    
    Íconos: game-icons.net (CC BY 3.0) · Lucide (MIT)

**Tags** (23): Wittenoom, amianto azul, asbesto, crocidolita, mesotelioma, Daniel Écija, María Bernal, Operación Canguro, emigrantes españoles, Australia Occidental, Pilbara, CSR, pueblo fantasma, pueblo borrado del mapa, historia oscura, documental, desastre industrial, Banjima, Eric Saint, blue asbestos, asbestos mining disaster, ghost town Australia, Wittenoom documentary

## 6. Gasto (cost_tracker, video `f58_parte_b`)

| servicio | descripción | US$ |
|---|---|---|
| Anthropic claude-opus-5-5 | m09:paquetes | 0.16794 |
| Anthropic claude-opus-5-5 | m03:casilleros | 0.12233 |
| fal.ai Seedream 5.0 Lite (t2i) | paquete_01_base: A young adult Spanish migrant miner, olive skin, short dark ... | 0.035 |
| fal.ai Seedream 5.0 Lite (t2i) | paquete_02_base: The bandaged foot of a young Spanish migrant miner resting o... | 0.035 |
| fal.ai Seedream 5.0 Lite (t2i) | paquete_03_base: Vast abandoned blue-grey asbestos tailings dumps spilling do... | 0.035 |

Por rubro: **m09:paquetes** US$ 0.16794 · **casilleros** US$ 0.12233 · **fotos** US$ 0.105

**Total US$ 0.3953**.

`asegurar_canon`: no llamó a Flash (la marca `canon_ficha_md5` del topic coincidía con la ficha).

## 7. Archivos

- `output/123bbb64-9fca-4395-8bf4-57d60e219ef1/publish/metadata.json` (paquetes, descripción, tags) y `thumb_candidates/paquete_NN*.png` (no van a git)
- `lab/hyperframes/f58/hoja_paquetes.jpg`, `parte_b.json` (todo), `parte_b.log` (stdout de la corrida)