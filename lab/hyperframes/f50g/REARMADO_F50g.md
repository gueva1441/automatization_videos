# REARMADO_F50g — Wittenoom re-armado en seco con el aspecto del canon (F50g-A)

Salida de `python lab/hyperframes/f50g/rearmar.py`: los casilleros guardados en el `03_visual.json` de producción → `armar(slots, anio, grupos)` → F8 → backstop de texto, con `grupos` = `people_groups` del topic. Cero llamadas a modelos, cero fal. Palabras = `len(prompt.split())`; antes = el prompt guardado, después = el re-armado con grupos.

## Tabla

| cap | fotos | con aspecto | sin aspecto | palabras antes med | antes máx | después med | después máx | 0 grupos | 1 grupo | 2+ grupos |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 3 | 2 | 161 | 181 | 191 | 209 | 2 | 2 | 1 |
| 2 | 16 | 13 | 3 | 141.5 | 174 | 169.5 | 209 | 3 | 12 | 1 |
| 3 | 16 | 13 | 3 | 155 | 195 | 178.5 | 208 | 3 | 10 | 3 |
| 4 | 14 | 9 | 5 | 125.5 | 147 | 149.5 | 170 | 5 | 9 | 0 |
| 5 | 16 | 8 | 8 | 135 | 245 | 157.5 | 273 | 8 | 6 | 2 |
| 6 | 16 | 9 | 7 | 121.5 | 157 | 130 | 172 | 7 | 9 | 0 |
| 7 | 13 | 4 | 9 | 135 | 183 | 139 | 224 | 9 | 2 | 2 |
| **total** | 96 | 59 | 37 | 137.5 | 245 | 157.5 | 273 | 37 | 50 | 9 |
| total sin 1/1, 7/1 | 94 | 58 | 36 | 136 | 245 | 157.5 | 273 | 36 | 49 | 9 |

Primeros cuadros Veo (rol `image_f8`): 1/1, 7/1 — la última fila los excluye.

## Verificación automática

- Re-armado con grupos = {} contra el guardado: 96/96 iguales
- Con grupos menos el texto del aspecto = sin grupos (salvo espacios): 96/96
- Fotos que cambian con grupos: 59
- Ids de `people_group` que no están en el canon: ninguno
- Ids presentes en fotos pero sin `appearance` en el canon: ['airport_police', 'international_un_official']
- **Resultado: PASA**


## Fotos con aspecto

- 1/1 · spanish_migrant_families · 163 → 191 palabras
- 1/2 · spanish_migrant_families · 181 → 209 palabras
- 1/3 · spanish_migrant_families, mine_and_mill_workers · 147 → 206 palabras
- 2/1 · spanish_migrant_families · 174 → 202 palabras
- 2/2 · spanish_migrant_families · 158 → 186 palabras
- 2/3 · spanish_migrant_families · 141 → 169 palabras
- 2/4 · spanish_migrant_families · 144 → 172 palabras
- 2/5 · spanish_migrant_families · 143 → 171 palabras
- 2/6 · spanish_migrant_families · 148 → 176 palabras
- 2/7 · spanish_migrant_families · 139 → 167 palabras
- 2/8 · spanish_migrant_families · 129 → 157 palabras
- 2/9 · spanish_migrant_families · 142 → 170 palabras
- 2/12 · spanish_migrant_families · 151 → 179 palabras
- 2/13 · spanish_migrant_families · 134 → 162 palabras
- 2/15 · mine_and_mill_workers · 126 → 157 palabras
- 2/16 · spanish_migrant_families, town_children · 160 → 209 palabras
- 3/1 · mine_and_health_officials · 195 → 208 palabras
- 3/3 · company_managers, prospectors_mine_owners · 170 → 205 palabras
- 3/4 · mine_and_health_officials · 151 → 164 palabras
- 3/6 · mine_and_health_officials, company_managers · 165 → 192 palabras
- 3/7 · union_and_arbitration · 164 → 180 palabras
- 3/8 · union_and_arbitration · 161 → 177 palabras
- 3/9 · union_and_arbitration, mine_and_mill_workers · 158 → 205 palabras
- 3/10 · mine_and_mill_workers · 169 → 200 palabras
- 3/11 · mine_and_mill_workers · 152 → 183 palabras
- 3/12 · company_managers · 140 → 154 palabras
- 3/14 · mine_and_mill_workers · 135 → 166 palabras
- 3/15 · mine_and_mill_workers · 146 → 177 palabras
- 3/16 · spanish_migrant_families · 161 → 189 palabras
- 4/1 · town_children · 147 → 168 palabras
- 4/3 · town_children · 124 → 145 palabras
- 4/8 · mine_and_mill_workers · 138 → 169 palabras
- 4/9 · mine_and_mill_workers · 121 → 152 palabras
- 4/10 · spanish_migrant_families · 131 → 159 palabras
- 4/11 · spanish_migrant_families · 127 → 155 palabras
- 4/12 · spanish_migrant_families · 142 → 170 palabras
- 4/13 · spanish_migrant_families · 131 → 159 palabras
- 4/14 · spanish_migrant_families · 119 → 147 palabras
- 5/4 · mine_and_mill_workers · 132 → 163 palabras
- 5/5 · spanish_migrant_families · 149 → 177 palabras
- 5/6 · spanish_migrant_families · 131 → 159 palabras
- 5/8 · airport_police, spanish_migrant_families · 146 → 174 palabras
- 5/9 · airport_police, spanish_migrant_families · 128 → 156 palabras
- 5/13 · spanish_migrant_families · 139 → 167 palabras
- 5/15 · spanish_migrant_families · 138 → 166 palabras
- 5/16 · spanish_migrant_families · 245 → 273 palabras
- 6/1 · victims_advocates_and_lawyers · 144 → 159 palabras
- 6/2 · victims_advocates_and_lawyers · 151 → 166 palabras
- 6/3 · victims_advocates_and_lawyers · 157 → 172 palabras
- 6/4 · spanish_migrant_families · 131 → 159 palabras
- 6/5 · spanish_migrant_families · 130 → 158 palabras
- 6/6 · victims_advocates_and_lawyers · 118 → 133 palabras
- 6/7 · victims_advocates_and_lawyers · 121 → 136 palabras
- 6/11 · australian_politicians · 111 → 125 palabras
- 6/13 · australian_politicians · 122 → 136 palabras
- 7/7 · banjima_traditional_owners · 131 → 157 palabras
- 7/8 · banjima_traditional_owners, international_un_official · 146 → 172 palabras
- 7/9 · banjima_traditional_owners · 141 → 167 palabras
- 7/11 · banjima_traditional_owners, victims_advocates_and_lawyers · 183 → 224 palabras
