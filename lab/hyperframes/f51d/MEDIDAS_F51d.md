# MEDIDAS_F51d — Wittenoom en texto tras m03 (F51d-A etapa 2)

Salida de `python lab/hyperframes/f51d/medidas_f51d.py --visual C:\CLAUDE_PROJECTS\automatization_videos\data\scripts\_steps\123bbb64-9fca-4395-8bf4-57d60e219ef1\03_visual.json`.

- Archivo medido: `C:\CLAUDE_PROJECTS\automatization_videos\data\scripts\_steps\123bbb64-9fca-4395-8bf4-57d60e219ef1\03_visual.json`
- md5: `72fdd85ce03352aa3c734108be2a9f38`
- topic_id del archivo: `123bbb64-9fca-4395-8bf4-57d60e219ef1` · fotos: 96 · cap 1: 5 · cap 2: 16 · cap 3: 16 · cap 4: 14 · cap 5: 16 · cap 6: 16 · cap 7: 13
- Canon: `people_groups` del topic vivo (12 grupos): mine_and_mill_workers, spanish_migrant_families, wittenoom_town_residents, company_owners_and_managers, government_mines_and_health_officials, unions_and_labour_arbitration, australian_politicians, asbestos_victims_advocates_and_lawyers, banjima_traditional_owners, international_human_rights_observers, environmental_assessors, australian_airport_police
- Numeración «cap/i»: `f50g/rearmar.fotos(cap)`, i desde 1 (en los caps Veo la foto 1 es la del clip).
- Grupos de una foto: unión de `people_group` del ítem y del casillero (`raw_llm_prompt`).

## 1. Fotos con un `people_group` que no existe en el canon vivo

**Total: 0** (tiene que dar 0 tras m03)

- ninguna

## 2. Fotos cuyos grupos tienen todos `appearance` vacío

Grupos del canon con `appearance` vacío (5): wittenoom_town_residents, asbestos_victims_advocates_and_lawyers, international_human_rights_observers, environmental_assessors, australian_airport_police

**Total: 6**

| foto | rol | grupo(s) | subject (casillero) |
|---|---|---|---|
| 4/3 | flux | wittenoom_town_residents | small figures of children scattered across a town ground entirely surfaced with blue-grey tailings |
| 5/9 | flux | australian_airport_police | An open passport lying on a laminate checkpoint counter, a mid-1980s Australian police officer in light-blue shirt and peaked cap bent over it, out of focus behind |
| 5/12 | flux | wittenoom_town_residents | A late-1980s demolition excavator tearing down a fibro-cement company house, a lone sun-weathered Anglo-Australian resident in his sixties, T-shirt and broad-brimmed hat, watching from a distant veranda |
| 6/7 | flux | asbestos_victims_advocates_and_lawyers | A middle-aged Anglo-Australian woman advocate, medium build, shoulder-length hair, in contemporary professional attire, seen from behind |
| 6/8 | flux | wittenoom_town_residents | Middle-aged Anglo-Australian adults in their sixties, children of the town's police and teachers, in casual clothes, mostly seen from behind |
| 7/4 | supp | environmental_assessors | A few adult Anglo-Australian environmental assessors, lean builds, in white protective coveralls, respirators and wide-brimmed hats |

## 3. Fotos cuyo prompt contiene un texto de `condition_by_period`

Textos de condición buscados: 11. **Fotos con la subcadena exacta: 0** (tiene que dar 0). Aparte, sin mayúsculas y sin el punto final: 0 fotos más.

- ninguna

## 4. Prompts enteros de 2/9, 4/11, 4/12 y 5/8

### 2/9 (flux)

- Ancla: «Recuerda el canal de Suez y el calor que hacía ahí, un calor que todavía lo hace resoplar cuando lo cuenta.»
- Año: 1962 — 1) el casillero `year` del modelo · palabras: 125

```
Spanish migrant passengers on deck, olive-skinned men in sweat-soaked singlets and women in damp cotton dresses; a boy around eight in shorts sits at the rail. The liner glides through the Suez Canal under blazing sun, passengers crowding the scant shade. Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes. Suez Canal, 1962, flat desert sand banks close on both sides of the ship. Harsh overhead noon sun, heat haze. Wide shot, eye-level along the deck, 35mm lens, deep depth of field. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

### 4/11 (flux)

- Ancla: «Tres meses después le tocó a María. Llegó al hospital de Wittenoom debilitada por una infección renal. El bebé era muy grande. Lo sacaron con fórceps.»
- Año: 1963 — 1) el casillero `year` del modelo · palabras: 121

```
A young Spanish migrant mother, about 25, slender and weakened, dark hair damp with sweat, and an Anglo-Australian nurse in white holding a very large swaddled baby. Lying back exhausted after the forceps delivery as the nurse lifts the newborn. Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes. Wittenoom hospital delivery room, June 1963, mid-century iron bed, enamel fittings. Cool overhead light, shadows gathering in the corners. Medium shot, slightly high angle, shallow depth of field, 50mm. A grainy 35mm documentary photograph taken in 1963, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

### 4/12 (flux)

- Ancla: «Le pusieron Daniel, como el padre. Hay una foto del bautizo: siete de julio de mil novecientos sesenta y tres.»
- Año: 1963 — 1) el casillero `year` del modelo · palabras: 119

```
A black-and-white baptism photograph of a Spanish migrant family, infant in a white baptismal gown. The photograph lying on a table, the family posed outside a small corrugated-iron church. Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes. Kitchen table of a fibro-cement company house, July 1963. The words "7 July 1963" are written along the white border of the photograph in handwritten ink, in clear crisp lettering. Harsh window daylight raking across the print. Detail shot, top-down, shallow depth of field, macro. A grainy 35mm documentary photograph taken in 1963, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio.
```

### 5/8 (flux)

- Ancla: «Veinte años después, un policía iba a reconocer el nombre del pueblo en un pasaporte.»
- Año: 1966 — 1) el casillero `year` del modelo · palabras: 97

```
The tailings-surfaced Wittenoom airstrip with a small propeller passenger aircraft. The small aircraft taxis for departure, its propellers raising a long plume of grey-red dust behind it. Isolated Pilbara airstrip of compacted blue-grey tailings on red earth, December 1966. Harsh white December midday sun, heat shimmer over the strip. Wide shot, eye-level from the edge of the strip, deep depth of field, 50mm lens. A grainy 35mm documentary photograph taken in 1966, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

## 5. 6/3, 7/11 y 3/16

m03 re-planea las anclas: van por posición y, aparte, por el texto del ancla.

### 5a. Por posición

### posición: 6/3 (flux)

- Ancla: «En mil novecientos ochenta y ocho un juez leyó su veredicto: la compañía había mostrado un desprecio continuo, consciente y contumaz por la seguridad y la salud de sus trabajadores.»
- «Court» en el prompt: sí · año: **1988** — 1) el casillero `year` del modelo · casillero `year`: '1988'

```
An Anglo-Australian judge in his sixties, heavy build, in black robes and wig at a raised timber bench; ageing former workers in the public gallery seen from behind. The judge reading the verdict aloud from typed pages. Adult men of European origin (Anglo-Australian, Central and Eastern European, Southern European including Spanish), with fair to olive skin, dark to light hair and lean working builds. Western Australian Supreme Court courtroom, 1988, dark jarrah panelling, coat of arms above the bench. Soft daylight from tall windows mixed with warm bench lamp. Wide shot, eye-level from the rear of the gallery, deep depth of field, 35mm. A grainy 35mm documentary photograph taken in 1988, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

### posición: 7/11 (supp)

- Ancla: «Nadie ha empezado a limpiar.»
- «Court» en el prompt: no · año: **2026** — 1) el casillero `year` del modelo · casillero `year`: '2026'

```
The emptied former Wittenoom town site, all buildings demolished. Wind drags red dust across bare concrete footings and old roads still surfaced with blue-grey tailings. Former Wittenoom townsite in 2026: no houses left, scattered slab footings, faint street grid, scrub regrowth, red earth. Flat early-morning light with wind-blown dust haze. Extreme wide shot, high elevated angle, deep depth of field, wide-angle. A grainy 35mm documentary photograph taken in 2026, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

### posición: 3/16 (flux)

- Ancla: ««porque estaban acostumbrados; lo esperaban», dijo McNulty. En mil novecientos sesenta y uno la producción subió. Al año siguiente, los Écija bajaban de aquel avión.»
- «Court» en el prompt: no · año: **1962** — 1) el casillero `year` del modelo · casillero `year`: '1962'

```
A young Spanish migrant couple of Mediterranean origin: a lean dark-haired man in his twenties in work shirt and trousers, and a slim young woman in a modest knee-length cotton dress. Stepping down from a small propeller aircraft onto the airstrip. Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes. The Wittenoom airstrip in 1962, surfaced with crumbly blue-grey tailings, low tin and fibro houses beyond, a dust plume over the gorge. Harsh midday desert sun, heat shimmer and haze. Wide shot, low angle from the airstrip surface, 50mm, moderate depth of field. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

### 5b. Por texto del ancla

#### 6/3 · juez / veredicto / Tribunal Supremo — 1 foto(s): 6/3

### ancla: 6/3 (flux)

- Ancla: «En mil novecientos ochenta y ocho un juez leyó su veredicto: la compañía había mostrado un desprecio continuo, consciente y contumaz por la seguridad y la salud de sus trabajadores.»
- «Court» en el prompt: sí · año: **1988** — 1) el casillero `year` del modelo · casillero `year`: '1988'

```
An Anglo-Australian judge in his sixties, heavy build, in black robes and wig at a raised timber bench; ageing former workers in the public gallery seen from behind. The judge reading the verdict aloud from typed pages. Adult men of European origin (Anglo-Australian, Central and Eastern European, Southern European including Spanish), with fair to olive skin, dark to light hair and lean working builds. Western Australian Supreme Court courtroom, 1988, dark jarrah panelling, coat of arms above the bench. Soft daylight from tall windows mixed with warm bench lamp. Wide shot, eye-level from the rear of the gallery, deep depth of field, 35mm. A grainy 35mm documentary photograph taken in 1988, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

#### 7/11 · Tribunal Federal — 1 foto(s): 7/10

### ancla: 7/10 (supp)

- Ancla: «Dos años después, Gordon Legal presentó en nombre de BNTAC un proceso contra Australia Occidental en el Tribunal Federal.»
- «Court» en el prompt: sí · año: **2026** — 1) el casillero `year` del modelo · casillero `year`: '2026'

```
Banjima traditional owners, Aboriginal Australians with dark brown skin, in smart contemporary attire, walking with Anglo-Australian lawyers in dark suits carrying document boxes. The group climbs the steps of the Federal Court building to lodge the case against Western Australia. Aboriginal Australian people with dark brown skin, dark wavy to curly hair (greying in elders) and brown eyes. Exterior of a modern Federal Court building in Perth, broad stone steps, glass and stone facade, 2026. The words "Federal Court" are written over the entrance in carved, in clear crisp lettering. Overcast soft morning daylight. Wide shot, low angle from the foot of the steps, deep depth of field, 28mm lens. A grainy 35mm documentary photograph taken in 2026, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio.
```

#### 3/16 · «Al año siguiente, los Écija» — 1 foto(s): 3/16

### ancla: 3/16 (flux)

- Ancla: ««porque estaban acostumbrados; lo esperaban», dijo McNulty. En mil novecientos sesenta y uno la producción subió. Al año siguiente, los Écija bajaban de aquel avión.»
- «Court» en el prompt: no · año: **1962** — 1) el casillero `year` del modelo · casillero `year`: '1962'

```
A young Spanish migrant couple of Mediterranean origin: a lean dark-haired man in his twenties in work shirt and trousers, and a slim young woman in a modest knee-length cotton dress. Stepping down from a small propeller aircraft onto the airstrip. Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes. The Wittenoom airstrip in 1962, surfaced with crumbly blue-grey tailings, low tin and fibro houses beyond, a dust plume over the gorge. Harsh midday desert sun, heat shimmer and haze. Wide shot, low angle from the airstrip surface, 50mm, moderate depth of field. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

## 6. Caps 1 y 7: ancla Veo, anclas vecinas y `video_prompt`

Mitad de palabra = el carácter de la narración pegado al ancla es alfanumérico y el borde del ancla también. Se busca en `narration` del cap de 01b_narration.json.

### cap 1 (veo_position: start)

| foto | rol | ancla | posición | antes / después | mitad de palabra | mitad de oración (informativo) |
|---|---|---|---|---|---|---|
| 1/1 | Veo | «Un hombre joven posa para una foto con el pie envuelto en una venda blanca.» | 0–75 (exacta) | '' / ' ' | no | no |
| 1/2 | apoyo vecina | «En el retrato de familia todos miran a cámara menos el pie: está vendado, y la herida que le hizo un trozo de amianto no cierra.» | 116–244 (exacta) | ' ' / ' ' | no | no |
| 1/3 | apoyo vecina | «El hombre se llama Daniel Écija y es minero.» | 245–289 (exacta) | ' ' / ' ' | no | no |

`video_prompt` del cap 1, entero y tal cual:

```
A slow, somber documentary shot on grainy 35mm film from the early sixties, muted colors and slight underexposure. The camera makes a very slow push-in, starting on a medium shot of the young miner against the corrugated iron wall and ending slightly closer, the white bandaged foot still sharp in the lower frame. First, fine red dust drifts low across the ochre earth, then his short shirt sleeves stir faintly in a light breeze as he breathes slowly. Hard, cold midday light under a pale washed-out sky keeps short sharp shadows steady in the dusty yard. He stays in place, posed stiffly with his weight off the bandaged foot, face and body steady.
```

### cap 7 (veo_position: end)

| foto | rol | ancla | posición | antes / después | mitad de palabra | mitad de oración (informativo) |
|---|---|---|---|---|---|---|
| 7/1 | Veo | «No se ha retirado una sola palada de asbesto. ¿Quién va a sacar la primera palada de esa tierra?» | 1137–1233 (exacta) | ' ' / '' | no | no |
| 7/12 | apoyo vecina | «En los accesos al pueblo y desfiladero hay bloqueos.» | 989–1041 (exacta) | '\n' / ' ' | no | no |
| 7/13 | apoyo vecina | «El gobierno de Australia Occidental habla de un «grave problema de salud y seguridad pública».» | 1042–1136 (exacta) | ' ' / ' ' | no | no |

`video_prompt` del cap 7, entero y tal cual:

```
A slow, somber documentary shot on grainy 35mm film, muted colors and slight underexposure, in a quiet dark-history realist style. Low at creek-bed level, the camera makes a very slow push-in, starting on the wide view of the upright shovel in the blue-grey tailings and ending on a closer framing of the shovel and its sunken blade against the red-ochre bank. First the thin stream slides steadily past the shovel toward the floodplain, rippling softly over the shallow pools, then a faint breeze stirs the spinifex clumps and lifts a few wisps of pale dust from the tailings. Pale cold dawn light and long soft shadows hold steady over the dry Pilbara gorge throughout.
```

## 7. Fuentes del año (`anio_fuente`)

| anio_fuente | fotos |
|---|---:|
| 1) el casillero `year` del modelo | 96 |
| total | 96 |

## 8. Palabras por prompt

- Mediana: **115.0** · máximo: **155** (2/1) · mínimo: 80 (2/11) · fotos: 96

| cap | fotos | mediana | máximo |
|---|---:|---:|---:|
| 1 | 5 | 134 | 144 |
| 2 | 16 | 121.5 | 155 |
| 3 | 16 | 123.5 | 154 |
| 4 | 14 | 118.0 | 125 |
| 5 | 16 | 118.5 | 136 |
| 6 | 16 | 98.0 | 139 |
| 7 | 13 | 100 | 136 |

## 9. Gasto por paso

### 01_v3_costos.json (`_corridas`)

| # | paso | US$ | segundos |
|---:|---|---:|---:|
| 1 | ficha | 0.3533 | 382.1 |
| 2 | escaleta | 1.8637 | 338.9 |
| 3 | guionista_v4 | 1.2342 | 248.0 |
| 4 | reparacion_v4 | 0.0765 | 40.2 |
| 5 | particion | 0.0479 | 45.1 |
| 6 | pantalla | 0.6585 | 226.4 |
| 7 | canon | 0.0306 | 48.2 |
| 8 | m03 | 2.1205 | 168.9 |
| 9 | canon (F50d, 3 corridas en paralelo; la 1 queda) | 0.0989 | 62.0 |
| 10 | canon | 0.3415 | 132.1 |
| 11 | m03 | 2.332 | 156.8 |
| 12 | canon | 0.3919 | 151.1 |
| 13 | m03 | 2.2653 | 155.7 |

### cost_history.json: entradas del topic con `timestamp` ≥ 2026-10-29T12:37:02

**Total: US$ 2.26531** en 17 entradas de 1 registro(s).

| registro (created_at) | entradas | US$ |
|---|---:|---:|
| 2026-10-29T12:37:14.718046 | 17 | 2.26531 |

| stage | proveedor / modelo | descripción | llamadas | US$ | tokens in | out | thinking |
|---|---|---|---:|---:|---:|---:|---:|
| script_generator | Anthropic claude-opus-5-5 | m03:casilleros | 7 | 2.151716 | 218734 | 63839 | 0 |
| script_generator | Gemini 2.5 Flash | call_flash_json | 7 | 0.086066 | 4852 | 2692 | 31152 |
| script_generator | Anthropic claude-opus-5-5 | m03:motion | 3 | 0.027528 | 3232 | 730 | 0 |
