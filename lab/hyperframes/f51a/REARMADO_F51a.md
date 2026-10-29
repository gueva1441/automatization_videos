# REARMADO_F51a — Wittenoom re-armado en seco con el `armar` nuevo (C)

Salida de `PYTHONIOENCODING=utf-8 python lab/hyperframes/f51a/rearmar_todo.py`. Casilleros: el `raw_llm_prompt` y el `anio` de cada foto del `03_visual.json` de producción de Wittenoom → `f50g/rearmar.rearmar_una` (armar → f8_backstop → _sacar_frases_con_texto), con `grupos` = `people_groups` del topic. Antes = el `prompt` guardado (armado viejo); después = el re-armado. Palabras = `len(prompt.split())`. Cero llamadas a modelos, cero fal; no se escribe producción.

## Resumen

- Fotos: 96 · pasan por `armar`: 96 · no pasan (sin `raw_llm_prompt`): 0
- Palabras antes, mediana · máx: 157.5 · 273
- Palabras después, mediana · máx: 122.5 · 196
- Cambian (después ≠ antes): 96/96
- Prompt nuevo vacío o sin `sujeto`: ninguna

## Prompts enteros

### Cap 1, foto 2: 1/2

**Antes** (209 palabras)

```
A Spanish migrant family posed for a portrait: a young olive-skinned miner in a pressed shirt with a bandaged foot, a slim young dark-haired wife in a cotton dress, a few relatives behind them. The family stands squared to the camera for the portrait while the white-bandaged foot sticks out at the front of the group. Spanish Mediterranean people with olive to light skin, dark brown or black hair, dark eyes, slim to medium builds; women and children tanned and dusted red in Wittenoom. Everyone faces the camera; the miner's weight leans off the bandaged foot, wife's hand resting on his shoulder, faces sun-lined and dust-dulled. The bright white bandage on the foot at the front edge of the portrait. Front of a corrugated sheet-metal house with an asbestos-cement wall panel, packed red earth yard, Wittenoom early 1960s. Grainy 35mm documentary photograph, 1962, dark-history realism, muted colors, visible film grain, slightly underexposed. 35mm film grain, muted documentary colors. Hard cold overcast daylight, flat and shadowless. Faded sepia family-photo tones over rust-red earth, grey corrugated metal, cold blue-grey shadow. Wide shot, eye-level, like a 1960s box camera, deep depth of field, slight film softness at edges. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

**Después** (159 palabras)

```
A Spanish migrant family posed for a portrait: a young olive-skinned miner in a pressed shirt with a bandaged foot, a slim young dark-haired wife in a cotton dress, a few relatives behind them. The family stands squared to the camera for the portrait while the white-bandaged foot sticks out at the front of the group. Spanish Mediterranean people with olive to light skin, dark brown or black hair, dark eyes, slim to medium builds; women and children tanned and dusted red in Wittenoom. Front of a corrugated sheet-metal house with an asbestos-cement wall panel, packed red earth yard, Wittenoom early 1960s. Hard cold overcast daylight, flat and shadowless. Wide shot, eye-level, like a 1960s box camera, deep depth of field, slight film softness at edges. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

### Con 2 grupos (spanish_migrant_families, mine_and_mill_workers): 1/3

**Antes** (206 palabras)

```
A young Spanish migrant miner, olive skin sun-darkened, lean muscular build, dark slicked hair, in a dust-caked work shirt and trousers, one foot bandaged. Standing against a sheet-metal wall after a shift, shifting his weight onto the good foot. Spanish Mediterranean people with olive to light skin, dark brown or black hair, dark eyes, slim to medium builds; women and children tanned and dusted red in Wittenoom. Mixed Australian (British-descended) and Southern, Central and Eastern European men, light to olive skin darkened by sun, short hair, lean muscular builds from heavy manual labour, often coated in fine dust. Face turned toward the camera, eyes shadowed by fatigue, shoulders slumped, fine grey dust in the creases of his shirt and skin. A dust-whitened cloth cap held loosely at his side. Beside a corrugated sheet-metal worker house, red Pilbara earth and blue-grey tailings yard, Wittenoom 1962. Grainy 35mm documentary photograph, 1962, dark-history realism, muted colors, visible film grain, slightly underexposed. 35mm film grain, muted documentary colors. Hard cold overcast daylight from one side. Muted rust-red earth, blue-grey tailings, pale grey dust film, desaturated cold tones. Medium shot, eye-level, 85mm lens, shallow depth of field. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

**Después** (162 palabras)

```
A young Spanish migrant miner, olive skin sun-darkened, lean muscular build, dark slicked hair, in a dust-caked work shirt and trousers, one foot bandaged. Standing against a sheet-metal wall after a shift, shifting his weight onto the good foot. Spanish Mediterranean people with olive to light skin, dark brown or black hair, dark eyes, slim to medium builds; women and children tanned and dusted red in Wittenoom. Mixed Australian (British-descended) and Southern, Central and Eastern European men, light to olive skin darkened by sun, short hair, lean muscular builds from heavy manual labour, often coated in fine dust. Beside a corrugated sheet-metal worker house, red Pilbara earth and blue-grey tailings yard, Wittenoom 1962. Hard cold overcast daylight from one side. Medium shot, eye-level, 85mm lens, shallow depth of field. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

### Veo (rol veo0): 1/1

**Antes** (191 palabras)

```
A young Spanish migrant miner, olive-skinned, slim and wiry, mid-twenties, seated for a family photograph, his foot wrapped in a white bandage. Holding still for the camera while the bandaged foot rests on the red dirt, the asbestos cut beneath it still not closing. Spanish Mediterranean people with olive to light skin, dark brown or black hair, dark eyes, slim to medium builds; women and children tanned and dusted red in Wittenoom. Focus on the bandaged foot; his body sits stiffly upright above it, shoulders drawn in, dust on his trouser cuffs. Faint grey dust and seepage stains on the fabric. Yard of a corrugated sheet-metal worker house in Wittenoom, early 1960s, red earth underfoot. Grainy 35mm documentary photograph, 1962, dark-history realism, muted colors, visible film grain, slightly underexposed. 35mm film grain, muted documentary colors. Hard cold overcast daylight from one side, flat desert glare without warmth. Desaturated sepia-grey with muted rust-red earth, pale grey dust film, cold blue-grey shadows. Close shot, low angle at ground level, shallow depth of field, 85mm lens, background corrugated wall soft. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

**Después** (148 palabras)

```
A young Spanish migrant miner, olive-skinned, slim and wiry, mid-twenties, seated for a family photograph, his foot wrapped in a white bandage. Holding still for the camera while the bandaged foot rests on the red dirt, the asbestos cut beneath it still not closing. Spanish Mediterranean people with olive to light skin, dark brown or black hair, dark eyes, slim to medium builds; women and children tanned and dusted red in Wittenoom. Yard of a corrugated sheet-metal worker house in Wittenoom, early 1960s, red earth underfoot. Hard cold overcast daylight from one side, flat desert glare without warmth. Close shot, low angle at ground level, shallow depth of field, 85mm lens, background corrugated wall soft. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

## Por foto

| foto | rol | palabras antes | después | cambia |
|---|---|---:|---:|---|
| 1/1 | veo0 | 191 | 148 | sí |
| 1/2 | supp | 209 | 159 | sí |
| 1/3 | supp | 206 | 162 | sí |
| 1/4 | supp | 161 | 115 | sí |
| 1/5 | supp | 145 | 106 | sí |
| 2/1 | flux | 202 | 160 | sí |
| 2/2 | flux | 186 | 149 | sí |
| 2/3 | flux | 169 | 130 | sí |
| 2/4 | flux | 172 | 138 | sí |
| 2/5 | flux | 171 | 136 | sí |
| 2/6 | flux | 176 | 139 | sí |
| 2/7 | flux | 167 | 134 | sí |
| 2/8 | flux | 157 | 126 | sí |
| 2/9 | flux | 170 | 132 | sí |
| 2/10 | flux | 124 | 94 | sí |
| 2/11 | flux | 130 | 93 | sí |
| 2/12 | flux | 179 | 143 | sí |
| 2/13 | flux | 162 | 131 | sí |
| 2/14 | flux | 130 | 99 | sí |
| 2/15 | flux | 157 | 127 | sí |
| 2/16 | flux | 209 | 167 | sí |
| 3/1 | flux | 208 | 154 | sí |
| 3/2 | flux | 144 | 105 | sí |
| 3/3 | flux | 205 | 160 | sí |
| 3/4 | flux | 164 | 121 | sí |
| 3/5 | flux | 137 | 98 | sí |
| 3/6 | flux | 192 | 149 | sí |
| 3/7 | flux | 180 | 133 | sí |
| 3/8 | flux | 177 | 140 | sí |
| 3/9 | flux | 205 | 167 | sí |
| 3/10 | flux | 200 | 152 | sí |
| 3/11 | flux | 183 | 152 | sí |
| 3/12 | flux | 154 | 118 | sí |
| 3/13 | flux | 125 | 99 | sí |
| 3/14 | flux | 166 | 139 | sí |
| 3/15 | flux | 177 | 138 | sí |
| 3/16 | flux | 189 | 148 | sí |
| 4/1 | flux | 168 | 130 | sí |
| 4/2 | flux | 121 | 84 | sí |
| 4/3 | flux | 145 | 110 | sí |
| 4/4 | flux | 119 | 83 | sí |
| 4/5 | flux | 117 | 84 | sí |
| 4/6 | flux | 134 | 95 | sí |
| 4/7 | flux | 111 | 78 | sí |
| 4/8 | flux | 169 | 134 | sí |
| 4/9 | flux | 152 | 122 | sí |
| 4/10 | flux | 159 | 125 | sí |
| 4/11 | flux | 155 | 124 | sí |
| 4/12 | flux | 170 | 138 | sí |
| 4/13 | flux | 159 | 122 | sí |
| 4/14 | flux | 147 | 121 | sí |
| 5/1 | flux | 164 | 115 | sí |
| 5/2 | flux | 140 | 102 | sí |
| 5/3 | flux | 143 | 101 | sí |
| 5/4 | flux | 163 | 124 | sí |
| 5/5 | flux | 177 | 142 | sí |
| 5/6 | flux | 159 | 129 | sí |
| 5/7 | flux | 122 | 87 | sí |
| 5/8 | flux | 174 | 143 | sí |
| 5/9 | flux | 156 | 124 | sí |
| 5/10 | flux | 119 | 85 | sí |
| 5/11 | flux | 123 | 92 | sí |
| 5/12 | flux | 122 | 91 | sí |
| 5/13 | flux | 167 | 136 | sí |
| 5/14 | flux | 125 | 93 | sí |
| 5/15 | flux | 166 | 132 | sí |
| 5/16 | flux | 273 | 196 | sí |
| 6/1 | flux | 159 | 122 | sí |
| 6/2 | flux | 166 | 123 | sí |
| 6/3 | flux | 172 | 133 | sí |
| 6/4 | flux | 159 | 126 | sí |
| 6/5 | flux | 158 | 128 | sí |
| 6/6 | flux | 133 | 99 | sí |
| 6/7 | flux | 136 | 102 | sí |
| 6/8 | flux | 127 | 93 | sí |
| 6/9 | flux | 118 | 85 | sí |
| 6/10 | flux | 122 | 87 | sí |
| 6/11 | flux | 125 | 93 | sí |
| 6/12 | flux | 118 | 84 | sí |
| 6/13 | flux | 136 | 107 | sí |
| 6/14 | flux | 113 | 85 | sí |
| 6/15 | flux | 115 | 87 | sí |
| 6/16 | flux | 120 | 91 | sí |
| 7/1 | veo0 | 151 | 109 | sí |
| 7/2 | supp | 135 | 103 | sí |
| 7/3 | supp | 139 | 102 | sí |
| 7/4 | supp | 122 | 91 | sí |
| 7/5 | supp | 133 | 94 | sí |
| 7/6 | supp | 116 | 86 | sí |
| 7/7 | supp | 157 | 128 | sí |
| 7/8 | supp | 172 | 133 | sí |
| 7/9 | supp | 167 | 127 | sí |
| 7/10 | supp | 112 | 83 | sí |
| 7/11 | supp | 224 | 196 | sí |
| 7/12 | supp | 121 | 92 | sí |
| 7/13 | supp | 142 | 110 | sí |
