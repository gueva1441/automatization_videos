# REARMADO_F51f — Wittenoom re-armado sin LLM con la frase del cartel nueva

Salida de `python lab/hyperframes/f51f/rearmar_f51f.py`: casilleros (`raw_llm_prompt`) + `anio` del 03_visual.json de F51d-A → `f50g/rearmar.rearmar_una` con el código de F51f, `grupos` = `people_groups` del topic vivo. Cero llamadas a modelos, cero fal.

- Fotos: 96 · con cartel: 8 · cambian: 8
- Cambian solo fotos con cartel y solo en la oración del cartel: **sí**

## Las fotos con cartel

| foto | rol | antes | después |
|---|---|---|---|
| 3/3 | flux | The words "Australian Blue Asbestos" are written on the truck's door panel in painted block lettering, in clear crisp lettering. | The words "Australian Blue Asbestos" are written on the truck's door panel in clear crisp painted block lettering. |
| 3/5 | flux | The typed line on the letter in the platen reads "Extremely dangerous" in typewriter, in clear crisp lettering. | The typed line on the letter in the platen reads "Extremely dangerous" in clear crisp typewriter lettering. |
| 4/12 | flux | The words "7 July 1963" are written along the white border of the photograph in handwritten ink, in clear crisp lettering. | The words "7 July 1963" are written along the white border of the photograph in clear crisp handwritten ink lettering. |
| 5/1 | flux | The front page of the folded newspaper reads "WITTENOOM MINE CLOSES" in bold serif newsprint headline, in clear crisp lettering. | The front page of the folded newspaper reads "WITTENOOM MINE CLOSES" in clear crisp bold serif newsprint headline lettering. |
| 6/10 | flux | The words "WITTENOOM" are written on the fallen sign panel in the dust in highway sign sans-serif, in clear crisp lettering. | The word "WITTENOOM" is written on the fallen sign panel in the dust in clear crisp highway sign sans-serif lettering. |
| 6/16 | flux | The words "ROAD CLOSED" are written on the sign fixed to the barricade in block stencil, in clear crisp lettering. | The words "ROAD CLOSED" are written on the sign fixed to the barricade in clear crisp block stencil lettering. |
| 7/10 | supp | The words "Federal Court" are written over the entrance in carved, in clear crisp lettering. | The words "Federal Court" are written over the entrance in clear crisp carved lettering. |
| 7/13 | supp | The words "DANGER ASBESTOS" are written on the warning sign in block, in clear crisp lettering. | The words "DANGER ASBESTOS" are written on the warning sign in clear crisp block lettering. |

## Los prompts enteros (después)

### 3/3 (flux)

```
An early motor truck of the new operating company arriving at the small mine workings and corrugated-iron camp huts. Rolling up the unsealed gorge track as the new owners take over the workings. Wittenoom gorge in 1943, small mine workings cut into red cliffs, a scatter of corrugated-iron huts, wartime austerity. The words "Australian Blue Asbestos" are written on the truck's door panel in clear crisp painted block lettering. Harsh late-morning desert sun, long dust trail behind the truck. Extreme wide shot, high angle from the gorge rim, deep depth of field, 28mm. A grainy 35mm documentary photograph taken in 1943, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio.
```

### 3/5 (flux)

```
A manual typewriter holding a half-typed letter on a spartan desk. The warning letter sits mid-sentence in the platen, a chest X-ray film clipped to the window behind. A bare company-town medical room in 1948, fibro-cement walls, paper files, louvred window. The typed line on the letter in the platen reads "Extremely dangerous" in clear crisp typewriter lettering. Hard window light raking across the page, deep shadow in the room. Detail shot, eye-level across the desk, shallow depth of field, 85mm, X-ray softly blurred. A grainy 35mm documentary photograph taken in 1948, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio.
```

### 4/12 (flux)

```
A black-and-white baptism photograph of a Spanish migrant family, infant in a white baptismal gown. The photograph lying on a table, the family posed outside a small corrugated-iron church. Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes. Kitchen table of a fibro-cement company house, July 1963. The words "7 July 1963" are written along the white border of the photograph in clear crisp handwritten ink lettering. Harsh window daylight raking across the print. Detail shot, top-down, shallow depth of field, macro. A grainy 35mm documentary photograph taken in 1963, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio.
```

### 5/1 (flux)

```
A 1966 Australian newspaper front page announcing the closure of the Wittenoom asbestos operation, left folded on a bench in the silent mill canteen. Fine fibrous dust drifts down and settles on the newsprint as the closure news lies unread. Dust-choked mill canteen of corrugated iron and pale fibro-cement sheeting, Wittenoom, December 1966, empty tin mugs on a long timber table. The front page of the folded newspaper reads "WITTENOOM MINE CLOSES" in clear crisp bold serif newsprint headline lettering. Harsh white December midday sun knifing through a doorway, hard black shadows. Close shot, high angle looking down onto the bench, shallow depth of field, 50mm lens. A grainy 35mm documentary photograph taken in 1966, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio.
```

### 6/10 (flux)

```
A green highway road sign on a red-earth roadside with its town name panel removed. The unbolted name panel lies face up in the red dust at the foot of the empty sign post. Remote Pilbara highway turn-off, June 2007, spinifex and red rock ranges. The word "WITTENOOM" is written on the fallen sign panel in the dust in clear crisp highway sign sans-serif lettering. Soft golden-hour light. Wide shot, low angle, deep depth of field, 24mm. A grainy 35mm documentary photograph taken in 2007, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio.
```

### 6/16 (flux)

```
A permanent steel barricade across the red dirt road into the gorge, tailings dumps untouched beyond. The closed barrier holding the road shut while grey tailings sit undisturbed on the slopes. Wittenoom Gorge entrance, 2016, red earth road, spinifex, rocky ranges. The words "ROAD CLOSED" are written on the sign fixed to the barricade in clear crisp block stencil lettering. Soft dusk light, warm horizon glow. Wide shot, eye-level, deep depth of field, 28mm. A grainy 35mm documentary photograph taken in 2016, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio.
```

### 7/10 (supp)

```
Banjima traditional owners, Aboriginal Australians with dark brown skin, in smart contemporary attire, walking with Anglo-Australian lawyers in dark suits carrying document boxes. The group climbs the steps of the Federal Court building to lodge the case against Western Australia. Aboriginal Australian people with dark brown skin, dark wavy to curly hair (greying in elders) and brown eyes. Exterior of a modern Federal Court building in Perth, broad stone steps, glass and stone facade, 2026. The words "Federal Court" are written over the entrance in clear crisp carved lettering. Overcast soft morning daylight. Wide shot, low angle from the foot of the steps, deep depth of field, 28mm lens. A grainy 35mm documentary photograph taken in 2026, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio.
```

### 7/13 (supp)

```
A sun-faded government warning sign fixed to the barricade at the town entrance. Red dust gusts across the sign as the empty road beyond fades into haze. Barricaded entrance to the former Wittenoom townsite, red earth, scrub, distant ridges, 2026. The words "DANGER ASBESTOS" are written on the warning sign in clear crisp block lettering. Flat early-morning light with wind-blown dust haze. Close shot, eye-level, shallow depth of field, 85mm lens. A grainy 35mm documentary photograph taken in 2026, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio.
```

