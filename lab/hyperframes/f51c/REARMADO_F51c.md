# REARMADO_F51c — Wittenoom re-armado en seco: antes (F51a) contra después (código F51c)

Salida de `PYTHONIOENCODING=utf-8 python lab/hyperframes/f51c/rearmar_todo.py`. Cero llamadas a modelos, cero fal; no se escribe `03_visual.json`, ni el canon, ni topics_db.

- **Antes** = el rearmado de F51a: casilleros (`raw_llm_prompt`) + el `anio` guardado de cada foto → `armar` → `scrub_documented_names` **viejo** (código de `a4a784e`, cargado con `git show` y ejecutado en memoria) con `topic["documented_people"]` → `f8_backstop` nuevo (el resto del backstop no cambió) → `_sacar_frases_con_texto`.
- **Después** = el código de `57f6aaf`: año = `anio_final(e, slots)` nuevo (sin el paso 1 «dicho en el ancla») → `armar` → `f8_backstop` (sin borrado) → `_sacar_frases_con_texto`.
- El expediente `e` se reconstruye como `m03_visual._render_prompts_seedream`: `mexp.expedientes(topic, mexp.fuentes(TID), cap_beats, anclas, assign, mexp.anio_previo(01b_narration.chapters, n), topic_year)`, con las anclas (`narration_anchor`; la de la foto Veo, la del capítulo) y el `beat` guardados en el 03_visual.json. Nada se recalcula con LLM.
- `grupos` = `people_groups` del topic **vivo** (canon F51b) en los dos lados, así la única diferencia entre antes y después son los arreglos a (borrado de nombres) y c (año). Por eso «antes» no es el texto literal de REARMADO_F51a.md (que usó el canon previo a F51b), sino el rearmado de F51a con el canon de hoy.

## Verificación del año (expediente reconstruido + `anio_final` viejo)

- Fotos: 96 · pasan por `armar`: 96 · sin `raw_llm_prompt`: 0
- `anio_final` viejo sobre el expediente reconstruido = `anio` guardado: **96/96**
- Además con la misma fuente (`anio_fuente`): 96/96

## Qué cambia (después ≠ antes)

- Cambian: **3/96**
- El borrado viejo cambiaba el prompt (arreglo a): 6/3, 7/11
- El año cambia (arreglo c): 3/16 (1961 → 1962)

| foto | rol | motivo |
|---|---|---|
| 3/16 | flux | c (año 1961 → 1962) |
| 6/3 | flux | a (el borrado de nombres cambiaba el prompt) |
| 7/11 | supp | a (el borrado de nombres cambiaba el prompt) |

- 6/3: cambia — a (el borrado de nombres cambiaba el prompt) · «Court» en antes: no, en después: sí
- 7/11: cambia — a (el borrado de nombres cambiaba el prompt) · «Court» en antes: no, en después: sí
- 3/16: cambia — c (año 1961 → 1962) · «Court» en antes: no, en después: no
- Otros cambios fuera de 6/3, 7/11 y 3/16: ninguno

## Prompts enteros

### 6/3 (flux)

- Ancla: «En mil novecientos ochenta y ocho un juez leyó su veredicto: la compañía había mostrado un desprecio continuo, consciente y contumaz por la seguridad y la salud de sus trabajadores.»
- Casillero `year` de Opus: '1988' · año dicho en el ancla (`anio_ancla`): '1988'
- Año antes: **1988** — 1) dicho en el ancla (guardado)
- Año después: **1988** — 1) el casillero `year` del modelo

**Antes**

```
An older Anglo-Australian judge in wig and robes on the bench; frail former workers and a lawyer in a broad-lapel 1980s suit in the gallery. The judge reads the verdict aloud from typed pages as the gallery sits motionless. A wood-panelled 1988 Perth Supreme a Head of the state government that rejected the parliamentary clean-up report of the 1992 era courtroom with tall windows. Soft overcast daylight from tall courtroom windows. Wide shot, low angle from the gallery toward the bench, deep depth of field, 35mm lens. A grainy 35mm documentary photograph taken in 1988, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

**Después**

```
An older Anglo-Australian judge in wig and robes on the bench; frail former workers and a lawyer in a broad-lapel 1980s suit in the gallery. The judge reads the verdict aloud from typed pages as the gallery sits motionless. A wood-panelled 1988 Perth Supreme Court courtroom with tall windows. Soft overcast daylight from tall courtroom windows. Wide shot, low angle from the gallery toward the bench, deep depth of field, 35mm lens. A grainy 35mm documentary photograph taken in 1988, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

### 7/11 (supp)

- Ancla: «Dos años después, Gordon Legal presentó en nombre de BNTAC un proceso contra Australia Occidental en el Tribunal Federal.»
- Casillero `year` de Opus: '2026' · año dicho en el ancla (`anio_ancla`): None
- Año antes: **2026** — 2) el casillero `year` del modelo (guardado)
- Año después: **2026** — 1) el casillero `year` del modelo

**Antes**

```
Members of the Banjima community, Aboriginal Australians of mixed ages with dark brown skin, in neat shirts and jackets, beside lawyers in contemporary suits. The group walks up the wide steps of the Federal a Head of the state government that rejected the parliamentary clean-up report of the 1992 era building to lodge the claim. Aboriginal Australian people with dark brown skin, dark wavy to curly hair (greying in elders) and brown eyes. Federal a Head of the state government that rejected the parliamentary clean-up report of the 1992 era building exterior in Perth, 2026, modern stone and glass facade. The words "FEDERAL a Head of the state government that rejected the parliamentary clean-up report of the 1992 era" are written over the main entrance in carved block capitals, in clear crisp lettering. Soft overcast morning light. Wide shot, low angle from the foot of the steps, deep depth of field, 28mm lens. A grainy 35mm documentary photograph taken in 2026, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio.
```

**Después**

```
Members of the Banjima community, Aboriginal Australians of mixed ages with dark brown skin, in neat shirts and jackets, beside lawyers in contemporary suits. The group walks up the wide steps of the Federal Court building to lodge the claim. Aboriginal Australian people with dark brown skin, dark wavy to curly hair (greying in elders) and brown eyes. Federal Court building exterior in Perth, 2026, modern stone and glass facade. The words "FEDERAL COURT" are written over the main entrance in carved block capitals, in clear crisp lettering. Soft overcast morning light. Wide shot, low angle from the foot of the steps, deep depth of field, 28mm lens. A grainy 35mm documentary photograph taken in 2026, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio.
```

### 3/16 (flux)

- Ancla: «En mil novecientos sesenta y uno la producción subió. Al año siguiente, los Écija bajaban de aquel avión.»
- Casillero `year` de Opus: '1962' · año dicho en el ancla (`anio_ancla`): '1961'
- Año antes: **1961** — 1) dicho en el ancla (guardado)
- Año después: **1962** — 1) el casillero `year` del modelo

**Antes**

```
A young Spanish migrant couple, olive skin, dark hair, slim builds, the man in a pressed shirt and trousers, the woman in a modest cotton dress and cardigan. Descending the steps of a small propeller aircraft onto the airstrip as the mill's dust plume rises on the horizon. Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes. Wittenoom airstrip, 1962, surfaced with compacted blue-grey tailings, tipper trucks and the mill in the distance. Harsh late-afternoon desert sun, long shadows over the tailings. Wide shot, low angle from the airstrip surface, deep depth of field, 35mm lens. A grainy 35mm documentary photograph taken in 1961, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

**Después**

```
A young Spanish migrant couple, olive skin, dark hair, slim builds, the man in a pressed shirt and trousers, the woman in a modest cotton dress and cardigan. Descending the steps of a small propeller aircraft onto the airstrip as the mill's dust plume rises on the horizon. Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes. Wittenoom airstrip, 1962, surfaced with compacted blue-grey tailings, tipper trucks and the mill in the distance. Harsh late-afternoon desert sun, long shadows over the tailings. Wide shot, low angle from the airstrip surface, deep depth of field, 35mm lens. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

## Cortes Veo (caps 1 y 7)

Narración = `01b_narration.json` capítulo `narration`.strip(); `veo_zone_chars = max(1, min(int(8.0 × len / duration_sec), len − 1))` con `duration_sec` de `output/audio/<TID>/sync_map.json`. Corte viejo = en el carácter; corte nuevo = `m03_visual._carve_veo_zones`. **Solo son los cortes:** las anclas que eligió Opus dentro de cada zona no se recalculan sin LLM.

### Cap 1 (posición start)

- len 453 · duración 32.96 s · 13.74 car/s · `veo_zone_chars` 109
- Corte viejo en el carácter 109 · nuevo en 115 · Δ +6 caracteres ≈ +0.44 s
- Zona Veo nueva [0, 115) · fotos de apoyo [115, 453)

| | últimos 40 de la zona Veo | primeros 40 de las fotos de apoyo |
|---|---|---|
| viejo | «lanca. Detrás, tierra roja y paredes de » | «chapa. En el retrato de familia todos mi» |
| nuevo | « Detrás, tierra roja y paredes de chapa.» | « En el retrato de familia todos miran a » |

### Cap 7 (posición end)

- len 1233 · duración 89.28 s · 13.81 car/s · `veo_zone_chars` 110
- Corte viejo en el carácter 1123 · nuevo en 1136 · Δ +13 caracteres ≈ +0.94 s
- Zona Veo nueva [1136, 1233) · fotos de apoyo [0, 1136)

| | últimos 40 de las fotos de apoyo | primeros 40 de la zona Veo |
|---|---|---|
| viejo | « de un «grave problema de salud y seguri» | «dad pública». No se ha retirado una sola» |
| nuevo | « problema de salud y seguridad pública».» | « No se ha retirado una sola palada de as» |

## Nota: ids de `people_group` fuera del canon vivo

- Fotos con algún id de `people_group` que no existe en el canon vivo: **20** (iguales en antes y después: los dos lados usan el mismo `grupos`). Ids: airport_police, company_managers, international_un_official, mine_and_health_officials, prospectors_mine_owners, town_children, union_and_arbitration, victims_advocates_and_lawyers.
- Fotos con `people_group` y sin aspecto pegado: antes 14, después 14; texto del aspecto igual antes/después en 96/96.
- Es lo esperado (F51b abierto 2): esos ids no pegan aspecto en este rearmado; se arregla en F51d al correr m03 de nuevo.

## Por foto

| foto | rol | año guardado | año después | fuente después | borrado viejo | cambia |
|---|---|---|---|---|---|---|
| 1/1 | veo0 | 1962 | 1962 | 1) el casillero `year` del modelo | no | no |
| 1/2 | supp | 1962 | 1962 | 1) el casillero `year` del modelo | no | no |
| 1/3 | supp | 1962 | 1962 | 1) el casillero `year` del modelo | no | no |
| 1/4 | supp | 1962 | 1962 | 1) el casillero `year` del modelo | no | no |
| 1/5 | supp | 1962 | 1962 | 1) el casillero `year` del modelo | no | no |
| 2/1 | flux | 1961 | 1961 | 1) el casillero `year` del modelo | no | no |
| 2/2 | flux | 1962 | 1962 | 1) el casillero `year` del modelo | no | no |
| 2/3 | flux | 1962 | 1962 | 1) el casillero `year` del modelo | no | no |
| 2/4 | flux | 1962 | 1962 | 1) el casillero `year` del modelo | no | no |
| 2/5 | flux | 1963 | 1963 | 1) el casillero `year` del modelo | no | no |
| 2/6 | flux | 1962 | 1962 | 1) el casillero `year` del modelo | no | no |
| 2/7 | flux | 1962 | 1962 | 1) el casillero `year` del modelo | no | no |
| 2/8 | flux | 1962 | 1962 | 1) el casillero `year` del modelo | no | no |
| 2/9 | flux | 1962 | 1962 | 1) el casillero `year` del modelo | no | no |
| 2/10 | flux | 1962 | 1962 | 1) el casillero `year` del modelo | no | no |
| 2/11 | flux | 1962 | 1962 | 1) el casillero `year` del modelo | no | no |
| 2/12 | flux | 1962 | 1962 | 1) el casillero `year` del modelo | no | no |
| 2/13 | flux | 1962 | 1962 | 1) el casillero `year` del modelo | no | no |
| 2/14 | flux | 1962 | 1962 | 1) el casillero `year` del modelo | no | no |
| 2/15 | flux | 1962 | 1962 | 1) el casillero `year` del modelo | no | no |
| 2/16 | flux | 1962 | 1962 | 1) el casillero `year` del modelo | no | no |
| 3/1 | flux | 1944 | 1944 | 1) el casillero `year` del modelo | no | no |
| 3/2 | flux | 1946 | 1946 | 1) el casillero `year` del modelo | no | no |
| 3/3 | flux | 1943 | 1943 | 1) el casillero `year` del modelo | no | no |
| 3/4 | flux | 1948 | 1948 | 1) el casillero `year` del modelo | no | no |
| 3/5 | flux | 1948 | 1948 | 1) el casillero `year` del modelo | no | no |
| 3/6 | flux | 1948 | 1948 | 1) el casillero `year` del modelo | no | no |
| 3/7 | flux | 1949 | 1949 | 1) el casillero `year` del modelo | no | no |
| 3/8 | flux | 1957 | 1957 | 1) el casillero `year` del modelo | no | no |
| 3/9 | flux | 1957 | 1957 | 1) el casillero `year` del modelo | no | no |
| 3/10 | flux | 1957 | 1957 | 1) el casillero `year` del modelo | no | no |
| 3/11 | flux | 1957 | 1957 | 1) el casillero `year` del modelo | no | no |
| 3/12 | flux | 1957 | 1957 | 1) el casillero `year` del modelo | no | no |
| 3/13 | flux | 1957 | 1957 | 1) el casillero `year` del modelo | no | no |
| 3/14 | flux | 1957 | 1957 | 1) el casillero `year` del modelo | no | no |
| 3/15 | flux | 1957 | 1957 | 1) el casillero `year` del modelo | no | no |
| 3/16 | flux | 1961 | 1962 | 1) el casillero `year` del modelo | no | sí |
| 4/1 | flux | 1963 | 1963 | 1) el casillero `year` del modelo | no | no |
| 4/2 | flux | 1963 | 1963 | 1) el casillero `year` del modelo | no | no |
| 4/3 | flux | 1963 | 1963 | 1) el casillero `year` del modelo | no | no |
| 4/4 | flux | 1963 | 1963 | 1) el casillero `year` del modelo | no | no |
| 4/5 | flux | 1963 | 1963 | 1) el casillero `year` del modelo | no | no |
| 4/6 | flux | 1963 | 1963 | 1) el casillero `year` del modelo | no | no |
| 4/7 | flux | 1963 | 1963 | 1) el casillero `year` del modelo | no | no |
| 4/8 | flux | 1963 | 1963 | 1) el casillero `year` del modelo | no | no |
| 4/9 | flux | 1962 | 1962 | 1) el casillero `year` del modelo | no | no |
| 4/10 | flux | 1963 | 1963 | 1) el casillero `year` del modelo | no | no |
| 4/11 | flux | 1963 | 1963 | 1) el casillero `year` del modelo | no | no |
| 4/12 | flux | 1963 | 1963 | 1) el casillero `year` del modelo | no | no |
| 4/13 | flux | 1963 | 1963 | 1) el casillero `year` del modelo | no | no |
| 4/14 | flux | 1963 | 1963 | 1) el casillero `year` del modelo | no | no |
| 5/1 | flux | 1966 | 1966 | 1) el casillero `year` del modelo | no | no |
| 5/2 | flux | 1966 | 1966 | 1) el casillero `year` del modelo | no | no |
| 5/3 | flux | 1966 | 1966 | 1) el casillero `year` del modelo | no | no |
| 5/4 | flux | 1966 | 1966 | 1) el casillero `year` del modelo | no | no |
| 5/5 | flux | 1966 | 1966 | 1) el casillero `year` del modelo | no | no |
| 5/6 | flux | 1971 | 1971 | 1) el casillero `year` del modelo | no | no |
| 5/7 | flux | 1966 | 1966 | 1) el casillero `year` del modelo | no | no |
| 5/8 | flux | 1985 | 1985 | 1) el casillero `year` del modelo | no | no |
| 5/9 | flux | 1985 | 1985 | 1) el casillero `year` del modelo | no | no |
| 5/10 | flux | 1978 | 1978 | 1) el casillero `year` del modelo | no | no |
| 5/11 | flux | 1986 | 1986 | 1) el casillero `year` del modelo | no | no |
| 5/12 | flux | 1993 | 1993 | 1) el casillero `year` del modelo | no | no |
| 5/13 | flux | 1991 | 1991 | 1) el casillero `year` del modelo | no | no |
| 5/14 | flux | 1992 | 1992 | 1) el casillero `year` del modelo | no | no |
| 5/15 | flux | 2023 | 2023 | 1) el casillero `year` del modelo | no | no |
| 5/16 | flux | 2023 | 2023 | 1) el casillero `year` del modelo | no | no |
| 6/1 | flux | 1989 | 1989 | 1) el casillero `year` del modelo | no | no |
| 6/2 | flux | 1979 | 1979 | 1) el casillero `year` del modelo | no | no |
| 6/3 | flux | 1988 | 1988 | 1) el casillero `year` del modelo | sí | sí |
| 6/4 | flux | 2024 | 2024 | 1) el casillero `year` del modelo | no | no |
| 6/5 | flux | 2024 | 2024 | 1) el casillero `year` del modelo | no | no |
| 6/6 | flux | 2024 | 2024 | 1) el casillero `year` del modelo | no | no |
| 6/7 | flux | 2024 | 2024 | 1) el casillero `year` del modelo | no | no |
| 6/8 | flux | 2006 | 2006 | 1) el casillero `year` del modelo | no | no |
| 6/9 | flux | 2007 | 2007 | 1) el casillero `year` del modelo | no | no |
| 6/10 | flux | 2007 | 2007 | 1) el casillero `year` del modelo | no | no |
| 6/11 | flux | 1992 | 1992 | 1) el casillero `year` del modelo | no | no |
| 6/12 | flux | 1994 | 1994 | 1) el casillero `year` del modelo | no | no |
| 6/13 | flux | 1994 | 1994 | 1) el casillero `year` del modelo | no | no |
| 6/14 | flux | 1992 | 1992 | 1) el casillero `year` del modelo | no | no |
| 6/15 | flux | 2016 | 2016 | 1) el casillero `year` del modelo | no | no |
| 6/16 | flux | 2023 | 2023 | 1) el casillero `year` del modelo | no | no |
| 7/1 | veo0 | 2026 | 2026 | 1) el casillero `year` del modelo | no | no |
| 7/2 | supp | 2026 | 2026 | 1) el casillero `year` del modelo | no | no |
| 7/3 | supp | 2026 | 2026 | 1) el casillero `year` del modelo | no | no |
| 7/4 | supp | 2026 | 2026 | 1) el casillero `year` del modelo | no | no |
| 7/5 | supp | 2021 | 2021 | 1) el casillero `year` del modelo | no | no |
| 7/6 | supp | 2026 | 2026 | 1) el casillero `year` del modelo | no | no |
| 7/7 | supp | 2023 | 2023 | 1) el casillero `year` del modelo | no | no |
| 7/8 | supp | 2023 | 2023 | 1) el casillero `year` del modelo | no | no |
| 7/9 | supp | 2023 | 2023 | 1) el casillero `year` del modelo | no | no |
| 7/10 | supp | 2024 | 2024 | 1) el casillero `year` del modelo | no | no |
| 7/11 | supp | 2026 | 2026 | 1) el casillero `year` del modelo | sí | sí |
| 7/12 | supp | 2026 | 2026 | 1) el casillero `year` del modelo | no | no |
| 7/13 | supp | 2026 | 2026 | 1) el casillero `year` del modelo | no | no |
