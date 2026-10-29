# PROMPTS_F50h — L, C y C+ép de las 20 fotos (F50h etapa 1, en texto, US$ 0)

Salida de `python lab/hyperframes/f50h/f50h.py --prompts`. Casilleros: el `raw_llm_prompt` y el `anio` de cada foto del 03_visual.json vivo de Wittenoom; grupos: los `people_groups` del topic (igual que `f50g/rearmar.py`). Ninguna llamada a modelos ni a fal.

**Verificación L = guardado: 20/20**. L (el `prompt` del papel de F50g) es igual a `rearmar_una(..., grupos)` y al `prompt` del 03_visual.json vivo en 20 de 20 fotos.

| | L | C | C+ép |
|---|---:|---:|---:|
| palabras, mediana | 167.5 | 131.0 | 139.0 |
| palabras, mín · máx | 115 · 273 | 87 · 196 | 95 · 204 |
| oraciones, mediana | 13.0 | 9.0 | 9.0 |

Referencia de la guía de fal (no es un corte; el handoff lo pide solo como dato al lado): 2–4 oraciones.

## Por foto

| foto | año | plano | grupos | cartel | palabras L · C · C+ép | oraciones L · C · C+ép | L = guardado |
|---|---|---|---|---|---|---|---|
| 1/2 | 1962 | wide | spanish_migrant_families | — | 209 · 159 · 167 | 13 · 9 · 9 | sí |
| 1/3 | 1962 | medium | spanish_migrant_families, mine_and_mill_workers | — | 206 · 162 · 170 | 14 · 10 · 10 | sí |
| 1/4 | 1962 | extreme_wide | — | WITTENOOM | 161 · 115 · 123 | 12 · 8 · 8 | sí |
| 2/9 | 1962 | medium | spanish_migrant_families | — | 170 · 132 · 140 | 13 · 9 · 9 | sí |
| 2/11 | 1962 | extreme_wide | — | — | 130 · 93 · 101 | 12 · 8 · 8 | sí |
| 2/15 | 1962 | detail | mine_and_mill_workers | — | 157 · 127 · 135 | 13 · 9 · 9 | sí |
| 3/3 | 1943 | wide | company_managers, prospectors_mine_owners | AUSTRALIAN BLUE ASBESTOS | 205 · 160 · 168 | 14 · 10 · 10 | sí |
| 3/6 | 1948 | medium | mine_and_health_officials, company_managers | — | 192 · 149 · 157 | 14 · 10 · 10 | sí |
| 3/10 | 1957 | medium | mine_and_mill_workers | — | 200 · 152 · 160 | 13 · 9 · 9 | sí |
| 4/1 | 1963 | wide | town_children | — | 168 · 130 · 138 | 13 · 9 · 9 | sí |
| 4/11 | 1963 | close | spanish_migrant_families | — | 155 · 124 · 132 | 13 · 9 · 9 | sí |
| 4/12 | 1963 | detail | spanish_migrant_families | 7 July 1963 | 170 · 138 · 146 | 13 · 9 · 9 | sí |
| 5/1 | 1966 | detail | — | MINE TO CLOSE | 164 · 115 · 123 | 12 · 8 · 8 | sí |
| 5/8 | 1985 | medium | airport_police, spanish_migrant_families | — | 174 · 143 · 151 | 13 · 9 · 9 | sí |
| 5/13 | 1991 | wide | spanish_migrant_families | — | 167 · 136 · 144 | 13 · 9 · 9 | sí |
| 5/16 | 2023 | close | spanish_migrant_families | — | 273 · 196 · 204 | 13 · 9 · 9 | sí |
| 6/5 | 2024 | medium | spanish_migrant_families | — | 158 · 128 · 136 | 13 · 9 · 9 | sí |
| 6/15 | 2016 | detail | — | CABINET IN CONFIDENCE | 115 · 87 · 95 | 12 · 8 · 8 | sí |
| 7/7 | 2023 | wide | banjima_traditional_owners | — | 157 · 128 · 136 | 13 · 9 · 9 | sí |
| 7/9 | 2023 | medium | banjima_traditional_owners | — | 167 · 127 · 135 | 13 · 9 · 9 | sí |

## 1/2 entera

**L** (209 palabras, 13 oraciones)

```
A Spanish migrant family posed for a portrait: a young olive-skinned miner in a pressed shirt with a bandaged foot, a slim young dark-haired wife in a cotton dress, a few relatives behind them. The family stands squared to the camera for the portrait while the white-bandaged foot sticks out at the front of the group. Spanish Mediterranean people with olive to light skin, dark brown or black hair, dark eyes, slim to medium builds; women and children tanned and dusted red in Wittenoom. Everyone faces the camera; the miner's weight leans off the bandaged foot, wife's hand resting on his shoulder, faces sun-lined and dust-dulled. The bright white bandage on the foot at the front edge of the portrait. Front of a corrugated sheet-metal house with an asbestos-cement wall panel, packed red earth yard, Wittenoom early 1960s. Grainy 35mm documentary photograph, 1962, dark-history realism, muted colors, visible film grain, slightly underexposed. 35mm film grain, muted documentary colors. Hard cold overcast daylight, flat and shadowless. Faded sepia family-photo tones over rust-red earth, grey corrugated metal, cold blue-grey shadow. Wide shot, eye-level, like a 1960s box camera, deep depth of field, slight film softness at edges. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

**C** (159 palabras, 9 oraciones)

```
A Spanish migrant family posed for a portrait: a young olive-skinned miner in a pressed shirt with a bandaged foot, a slim young dark-haired wife in a cotton dress, a few relatives behind them. The family stands squared to the camera for the portrait while the white-bandaged foot sticks out at the front of the group. Spanish Mediterranean people with olive to light skin, dark brown or black hair, dark eyes, slim to medium builds; women and children tanned and dusted red in Wittenoom. Front of a corrugated sheet-metal house with an asbestos-cement wall panel, packed red earth yard, Wittenoom early 1960s. Hard cold overcast daylight, flat and shadowless. Wide shot, eye-level, like a 1960s box camera, deep depth of field, slight film softness at edges. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

**C+ép** (167 palabras, 9 oraciones)

```
A Spanish migrant family posed for a portrait: a young olive-skinned miner in a pressed shirt with a bandaged foot, a slim young dark-haired wife in a cotton dress, a few relatives behind them. The family stands squared to the camera for the portrait while the white-bandaged foot sticks out at the front of the group. Spanish Mediterranean people with olive to light skin, dark brown or black hair, dark eyes, slim to medium builds; women and children tanned and dusted red in Wittenoom. Front of a corrugated sheet-metal house with an asbestos-cement wall panel, packed red earth yard, Wittenoom early 1960s. Hard cold overcast daylight, flat and shadowless. Wide shot, eye-level, like a 1960s box camera, deep depth of field, slight film softness at edges. A grainy documentary photograph taken in 1962, with the film, color and tones a real photograph from 1962 would have, slightly underexposed, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```


## 3/3 entera

**L** (205 palabras, 14 oraciones)

```
Company managers of British descent in lightweight suits and felt hats meeting sun-weathered Australian prospectors in rolled-sleeve work shirts and wide-brimmed hats. A company truck pulling into the gorge camp as the newcomers walk toward the prospectors' huts to take over the workings. Australian men of British descent, fair complexions, neatly cut and combed hair, office-worker builds. Australian men of British or Irish descent, fair skin deeply sun-tanned and weathered, short hair, lean wiry build from bush prospecting. The prospectors stand back with arms folded, watching the suited men approach; faces read only at a distance. The dusty company truck with its freshly painted door lettering. Yampire gorge mining camp, 1943: tents, corrugated sheet-metal huts, a crude crushing shed, red scree slopes. Grainy 35mm documentary photograph, 1943, dark-history realism, muted colors, visible film grain, slightly underexposed. 35mm film grain, muted documentary colors. Harsh midday desert sun, short black shadows. Red earth and dust, blue-grey asbestos spoil heaps, sun-bleached canvas, dull khaki and pale suit linen. Wide shot, eye-level from beside the huts, deep depth of field, 35mm lens. The words "AUSTRALIAN BLUE ASBESTOS" are written on the truck's driver-side door in hand-painted block letters, in clear crisp lettering. The image has a 16:9 aspect ratio.
```

**C** (160 palabras, 10 oraciones)

```
Company managers of British descent in lightweight suits and felt hats meeting sun-weathered Australian prospectors in rolled-sleeve work shirts and wide-brimmed hats. A company truck pulling into the gorge camp as the newcomers walk toward the prospectors' huts to take over the workings. Australian men of British descent, fair complexions, neatly cut and combed hair, office-worker builds. Australian men of British or Irish descent, fair skin deeply sun-tanned and weathered, short hair, lean wiry build from bush prospecting. Yampire gorge mining camp, 1943: tents, corrugated sheet-metal huts, a crude crushing shed, red scree slopes. The words "AUSTRALIAN BLUE ASBESTOS" are written on the truck's driver-side door in hand-painted block letters, in clear crisp lettering. Harsh midday desert sun, short black shadows. Wide shot, eye-level from beside the huts, deep depth of field, 35mm lens. A grainy 35mm documentary photograph taken in 1943, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio.
```

**C+ép** (168 palabras, 10 oraciones)

```
Company managers of British descent in lightweight suits and felt hats meeting sun-weathered Australian prospectors in rolled-sleeve work shirts and wide-brimmed hats. A company truck pulling into the gorge camp as the newcomers walk toward the prospectors' huts to take over the workings. Australian men of British descent, fair complexions, neatly cut and combed hair, office-worker builds. Australian men of British or Irish descent, fair skin deeply sun-tanned and weathered, short hair, lean wiry build from bush prospecting. Yampire gorge mining camp, 1943: tents, corrugated sheet-metal huts, a crude crushing shed, red scree slopes. The words "AUSTRALIAN BLUE ASBESTOS" are written on the truck's driver-side door in hand-painted block letters, in clear crisp lettering. Harsh midday desert sun, short black shadows. Wide shot, eye-level from beside the huts, deep depth of field, 35mm lens. A grainy documentary photograph taken in 1943, with the film, color and tones a real photograph from 1943 would have, slightly underexposed, in a dark-history realist style. The image has a 16:9 aspect ratio.
```


## 7/7 entera

**L** (157 palabras, 13 oraciones)

```
An elderly Aboriginal Banjima man with grey hair and beard, slim weathered build, in a collared shirt and broad-brimmed hat, small against the land. He stands at the rim of a red gorge overlooking his country. Aboriginal Australian people with dark brown skin, dark curly or wavy hair, elders with grey hair and beards, builds shaped by outdoor life in the Pilbara. Seen from behind, looking out over the gorge and plains. A worn broad-brimmed hat silhouetted against the sky. Banjima country in the Hamersley Ranges near Wittenoom, contemporary era, red cliffs and spinifex, 2023. Grainy 35mm documentary photograph, 2023, dark-history realism, muted colors, visible film grain, slightly underexposed. 35mm film grain, muted documentary colors. Late afternoon golden light. Intense red rock, gold spinifex, blue-grey distance, warm late light. Wide shot, eye-level from behind on the rim, deep depth of field, 35mm lens. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

**C** (128 palabras, 9 oraciones)

```
An elderly Aboriginal Banjima man with grey hair and beard, slim weathered build, in a collared shirt and broad-brimmed hat, small against the land. He stands at the rim of a red gorge overlooking his country. Aboriginal Australian people with dark brown skin, dark curly or wavy hair, elders with grey hair and beards, builds shaped by outdoor life in the Pilbara. Banjima country in the Hamersley Ranges near Wittenoom, contemporary era, red cliffs and spinifex, 2023. Late afternoon golden light. Wide shot, eye-level from behind on the rim, deep depth of field, 35mm lens. A grainy 35mm documentary photograph taken in 2023, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

**C+ép** (136 palabras, 9 oraciones)

```
An elderly Aboriginal Banjima man with grey hair and beard, slim weathered build, in a collared shirt and broad-brimmed hat, small against the land. He stands at the rim of a red gorge overlooking his country. Aboriginal Australian people with dark brown skin, dark curly or wavy hair, elders with grey hair and beards, builds shaped by outdoor life in the Pilbara. Banjima country in the Hamersley Ranges near Wittenoom, contemporary era, red cliffs and spinifex, 2023. Late afternoon golden light. Wide shot, eye-level from behind on the rim, deep depth of field, 35mm lens. A grainy documentary photograph taken in 2023, with the film, color and tones a real photograph from 2023 would have, slightly underexposed, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```
