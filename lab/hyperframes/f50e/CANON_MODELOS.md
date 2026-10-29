# CANON_MODELOS — el canon de Wittenoom con Flash, Sonnet 5.5 y Opus 5.5 (F50e-A y F50e-B, en texto)

Salida de `python -u lab/hyperframes/f50e/canon_modelos.py` (las llamadas) y `canon_modelos_md.py` (esta tabla). Mismo pedido que `step_4e.canon_desde_ficha`; nada se guardó en producción.

- md5 del pedido: `d2568e2a94c5db96f9836451b2f80cd7` en todos los intentos de las 9 corridas: sí
- Producción intacta (md5 antes = después): topics_db True · 05_visual_canon.json True
- Gasto F50e-A (cost_tracker `f50e-canon-modelos`): US$ 0.8093 · tope US$ 1,00
- F50e-A, parada por tope: tope: gastado 0.8093 + 2 × opus 1 0.3464 = 1.5021 > 1.0: opus 2 y 3 no corren
- **F50e-B** (opus_2 y opus_3, directo sin esquema; cost_tracker `f50e-b-canon-opus`): US$ 0.7244 · tope US$ 1,00 · md5 del pedido `d2568e2a94c5db96f9836451b2f80cd7` · producción intacta: topics_db True · 05_visual_canon.json True
- Fotos: 96, con año (anio_ancla o respaldo[0]): 96

**Aviso — el esquema no llegó a los modelos Claude.** El primer intento de cada corrida de Sonnet y Opus (con `VISUAL_CANON_SCHEMA_FICHA` como structured output) volvió HTTP 400: «Schemas contains too many optional parameters (46)… (limit: 24)». `extract_visual_canon` cayó entonces a su respaldo de producción: el MISMO texto, sin esquema. Esas respuestas son las que se miden. Flash sí corrió con el esquema. El pedido es el mismo; el formato forzado, no.

## Resumen por modelo

| modelo | corridas medidas | fotos cubiertas mín · máx | grupos (por corrida) | grupos con años sin ropa (por corrida) | grupos sin appearance (por corrida) | years ilegibles | US$ promedio por corrida | fallas |
|---|---|---|---|---|---|---|---:|---|
| flash | 2 de 3 | 61 · 61 de 96 | 22 / 5 | 1 / 0 | 0/22 / 0/5 | ninguno | 0.0255 | flash_2: canon sin periods |
| sonnet | 3 de 3 | 96 · 96 de 96 | 7 / 10 / 8 | 1 / 0 / 1 | 4/7 / 7/10 / 5/8 | ninguno | 0.1287 | — |
| opus | 3 de 3 | 96 · 96 de 96 | 13 / 13 / 11 | 0 / 0 / 0 | 2/13 / 3/13 / 3/11 | ninguno | 0.3569 | — |

## Por corrida

| corrida | periods (4a) | fotos cubiertas (4b) | por cap 1–7 (cubiertas/con año) | grupos (4d) | con años sin ropa | ilegibles (4e) | tokens in / out / thinking (4f) | US$ | s | intentos |
|---|---|---:|---|---:|---:|---|---|---:|---:|---:|
| flash_1 | 1937-1966 | 61/96 | 5/5 · 16/16 · 16/16 · 14/14 · 10/16 · 0/16 · 0/13 | 22 | 1 | — | 10122 / 5665 / 9020 | 0.0397 | 69.0 | 1 |
| flash_2 | **FALLA: canon sin periods** | — | — | — | — | — | 10122 / 2449 / 1085 | 0.0119 | 18.9 | 1 |
| flash_3 | 1937-1957 · 1958-1966 | 61/96 | 5/5 · 16/16 · 16/16 · 14/14 · 10/16 · 0/16 · 0/13 | 5 | 0 | — | 10122 / 4030 / 4756 | 0.025 | 43.8 | 1 |
| sonnet_1 | 1937-1949 · 1950-1966 · 1967-1992 · 1993-2026 | 96/96 | 5/5 · 16/16 · 16/16 · 14/14 · 16/16 · 16/16 · 13/13 | 7 | 1 | — | 14952 / 9421 / 0 | 0.1241 | 65.8 | 2 |
| sonnet_2 | 1937-1949 · 1950-1966 · 1967-1992 · 1993-2026 | 96/96 | 5/5 · 16/16 · 16/16 · 14/14 · 16/16 · 16/16 · 13/13 | 10 | 0 | — | 14952 / 11291 / 0 | 0.1428 | 77.7 | 2 |
| sonnet_3 | 1937-1946 · 1947-1966 · 1967-1992 · 1993-2026 | 96/96 | 5/5 · 16/16 · 16/16 · 14/14 · 16/16 · 16/16 · 13/13 | 8 | 1 | — | 14952 / 8939 / 0 | 0.1193 | 65.3 | 2 |
| opus_1 | 1937-1947 · 1948-1966 · 1967-1992 · 1993-2026 | 96/96 | 5/5 · 16/16 · 16/16 · 14/14 · 16/16 · 16/16 · 13/13 | 13 | 0 | — | 14952 / 14330 / 0 | 0.3464 | 130.8 | 2 |
| opus_2 | 1937-1946 · 1947-1966 · 1967-1993 · 1994-2026 | 96/96 | 5/5 · 16/16 · 16/16 · 14/14 · 16/16 · 16/16 · 13/13 | 13 | 0 | — | 14952 / 16394 / 0 | 0.3877 | 153.2 | 1 |
| opus_3 | 1937-1947 · 1948-1966 · 1967-1992 · 1993-2026 | 96/96 | 5/5 · 16/16 · 16/16 · 14/14 · 16/16 · 16/16 · 13/13 | 11 | 0 | — | 14952 / 13843 / 0 | 0.3367 | 125.9 | 1 |

## 4c — fotos sin ningún period que las cruce (y el que les daría la regla del «más cercano»)

- flash_1: 35 fotos — cap 5: [1971, 1978, 1985, 1986, 1991, 1993] → 1937-1966; cap 6: [1988, 1989, 1991, 1992, 2007, 2016] → 1937-1966; cap 7: [2021, 2023, 2024] → 1937-1966
- flash_3: 35 fotos — cap 5: [1971, 1978, 1985, 1986, 1991, 1993] → 1958-1966; cap 6: [1988, 1989, 1991, 1992, 2007, 2016] → 1958-1966; cap 7: [2021, 2023, 2024] → 1958-1966
- sonnet_1: ninguna
- sonnet_2: ninguna
- sonnet_3: ninguna
- opus_1: ninguna
- opus_2: ninguna
- opus_3: ninguna

## 4d — grupos con años de su where_when sin ropa por tramo

- flash_1: `asbestos_diseases_society_ceo` años [1979] (ropa: 1980-2020s)
- flash_3: ninguno
- sonnet_1: `spanish_migrant_families` años [1966, 1971] (ropa: 1962-1964 · 1985-2020s)
- sonnet_2: ninguno
- sonnet_3: `spanish_migrant_families` años [1966, 1971] (ropa: 1962-1964 · 1985-1991)
- opus_1: ninguno
- opus_2: ninguno
- opus_3: ninguno

## 4g — grupos con appearance vacío

- flash_1: 0/22 — ninguno
- flash_3: 0/5 — ninguno
- sonnet_1: 4/7 — `mine_owners_prospectors_and_company_executives`, `mines_and_health_inspectors`, `government_officials_and_inquiry_leaders`, `asbestos_disease_advocates`
- sonnet_2: 7/10 — `mines_and_health_officials`, `prospectors_and_mine_owners`, `company_management`, `government_and_political_figures`, `labour_unions_and_arbitration`, `asbestos_disease_advocates`, `legal_professionals`
- sonnet_3: 5/8 — `prospectors_and_mine_owners`, `company_executives`, `government_and_health_officials`, `politicians_and_inquiry_leaders`, `asbestos_disease_advocates`
- opus_1: 2/13 — `airport_police`, `last_residents`
- opus_2: 3/13 — `late_residents`, `airport_police`, `un_rapporteur`
- opus_3: 3/11 — `victims_advocates_and_lawyers`, `late_wittenoom_residents`, `airport_police`

## Ejemplo — la corrida de peor cobertura de cada modelo

### flash_1 (61/96)

```json
[
 {
  "years": "1937-1966",
  "clothing": "Miners in heavy-duty work clothes, hard hats, basic dust masks. Civilians in light cotton casual wear, wide-brimmed hats. Children in simple play clothes.",
  "technology": "Early industrial mining equipment, analog gauges, rudimentary safety gear. Landline phones, basic radios, manual typewriters.",
  "vehicles_machinery": "1940s-1960s heavy mining trucks, bulldozers. Civilian sedans and utes of the era. Small propeller planes.",
  "interiors": "Basic, functional homes often built with asbestos materials. Wooden desks, filing cabinets in offices. Dusty conditions throughout."
 }
]
```

Grupo con más años:

```json
{
 "id": "public_health_doctors",
 "who": "Doctors from the Department of Public Health monitoring health issues",
 "where_when": "Unspecified locations, 1960, 1962, 1968",
 "appearance": "Caucasian, professional, likely middle-aged, conveying an air of medical authority.",
 "clothing_by_period": [
  {
   "years": "1960-1969",
   "clothing": "Professional medical attire or business suits of the 1960s, clean and functional."
  }
 ]
}
```

### sonnet_2 (96/96)

```json
[
 {
  "years": "1937-1949",
  "clothing": "Prospectors and early miners in rugged khaki work shirts, trousers, boots and wide-brimmed felt hats; officials in suits or shirts with ties and hats.",
  "technology": "Hand tools, manual sampling, typed reports, paper correspondence, radio and wired telephone. NO digital technology, NO modern respirators.",
  "vehicles_machinery": "1930s-1940s trucks, early crushing and milling plant, rough gorge tracks, small aircraft for access.",
  "interiors": "Basic bush huts, tin and timber sheds, simple mine offices with timber desks and paper files."
 },
 {
  "years": "1950-1966",
  "clothing": "Dusty work shirts, overalls and boots for male workers; migrant families in modest 1950s-60s cotton dresses, shirts, knitwear and plain shoes; officials in shirts and ties.",
  "technology": "Film photography, typewriters, reel-to-reel and early radio equipment, dust-extraction hoods, mechanical industrial machinery. NO LED screens, NO digital devices.",
  "vehicles_machinery": "Small propeller aircraft, tipper trucks dumping tailings, utility vehicles, working mill machinery, ocean liner voyages for migrants.",
  "interiors": "Company houses of corrugated metal, timber and uralita; a dusty mill with a thick suspended dust cloud; a small hospital, a school and a church."
 },
 {
  "years": "1967-1992",
  "clothing": "Plain 1970s-80s casual clothing for the remaining residents; suits and ties for lawyers, judges and officials; work clothes and hard hats for demolition crews.",
  "technology": "Photocopied reports, television and film cameras, wired phones, early office computers by the late 1980s. NO smartphones, NO tablets.",
  "vehicles_machinery": "1970s-80s sedans and utility vehicles, bulldozers and demolition equipment, trucks.",
  "interiors": "Shrinking town with emptied houses, closing school, clinic and police station, and court and parliamentary hearing rooms with 1980s institutional decor."
 },
 {
  "years": "1993-2026",
  "clothing": "Contemporary but plain dress for officials, legal figures and elders in documentary settings; protective white suits, if shown, only for official modern site visits.",
  "technology": "Contemporary reports, video interviews, environmental sampling, legal filings. Modern devices appear only in present-day framing and never inside 1937-1966 scenes.",
  "vehicles_machinery": "Modern four-wheel-drive vehicles and permanent road barricades at the town and gorge entrances.",
  "interiors": "Emptied, demolished or overgrown townsite, with barricaded entrances and no inhabited interiors; offices and courts appear only in a modern legal or political context."
 }
]
```

Grupo con más años:

```json
{
 "id": "mine_and_mill_workers",
 "who": "Miners, mill workers, a mill fitter and laborers at Wittenoom, including post-war displaced persons assigned by the federal government and European recruits.",
 "where_when": "Mines and mill at Wittenoom, 1947-1966, including 1948-1951 displaced-person assignments and workers observed in 1953-1957.",
 "appearance": "Physically worked, lean to sturdy laboring builds, often coated in fine pale dust.",
 "clothing_by_period": [
  {
   "years": "1947-1957",
   "clothing": "Dusty khaki or grey work shirts, trousers or overalls, heavy boots and soft caps or hats, with little or no respiratory protection in a hot dry climate."
  },
  {
   "years": "1958-1966",
   "clothing": "Dust-covered overalls and work shirts, boots and caps, sometimes with a simple cloth mask, in a hot dry climate."
  }
 ]
}
```

### opus_2 (96/96)

```json
[
 {
  "years": "1937-1946",
  "clothing": "Prospectors and early miners in khaki shirts, moleskin or denim trousers, felt bush hats and leather boots. Wartime officials in wool suits and ties.",
  "technology": "Hand tools, rock drills, explosives, rudimentary crushing plant, kerosene lamps, valve radios, typewritten mines reports, telegrams.",
  "vehicles_machinery": "1930s round-fendered trucks and utes on unsealed red tracks, pack loads and small early crushing machinery at the gorges.",
  "interiors": "Rough camp huts and corrugated-iron shelters, canvas tents, bare timber tables, kerosene lighting."
 },
 {
  "years": "1947-1966",
  "clothing": "Male workers, including post-war European and Spanish migrants, in dust-coated cotton work shirts, singlets, work trousers and boots. Migrant women in cotton print dresses and headscarves. Children in shorts and simple dresses, often barefoot. Managers and doctors in light suits.",
  "technology": "Expanded fibre mill with belts, screens and later dust-reduction ducting; pneumatic drills; landline telephones; manual typewriters; film cameras; valve radios. No digital technology.",
  "vehicles_machinery": "Late-1940s to early-1960s trucks and tip trucks spreading tailings, company utes, small twin-engine propeller aircraft at a dusty airstrip.",
  "interiors": "Corrugated-iron and fibro company houses with linoleum floors, enamel kitchenware and early refrigerators. Small town hospital ward. School classrooms with timber desks."
 },
 {
  "years": "1967-1993",
  "clothing": "Remaining residents and former workers in late-1960s to 1980s casual wear. Lawyers, judges and politicians in 1980s suits. Ageing ex-workers and widows in plain clothes at courts and meetings.",
  "technology": "Landline phones, typewriters giving way to early office computers in city offices only, analogue television news cameras, film photography.",
  "vehicles_machinery": "1970s-1980s sedans and 4WDs on degraded roads, demolition equipment removing town buildings, airstrip closing.",
  "interiors": "Shrinking town with closing school, nursing post and police station. City courtrooms and parliamentary hearing rooms with timber panelling."
 },
 {
  "years": "1994-2026",
  "clothing": "Contemporary outdoor workwear, business suits for officials and lawyers, casual clothing for Banjima community members and activists.",
  "technology": "Contemporary devices permitted only in these scenes: digital cameras, laptops at press conferences, printed warning signage.",
  "vehicles_machinery": "Modern 4WD vehicles halted at permanent barricades, earthmoving equipment for final demolitions.",
  "interiors": "Government offices, law firm meeting rooms, interview rooms with family photographs."
 }
]
```

Grupo con más años:

```json
{
 "id": "public_health_physicians",
 "who": "Australian public health doctors, the Public Health Commissioner and an industrial hygienist who warned about asbestos dust and diagnosed disease.",
 "where_when": "Wittenoom and state health offices, 1948-1951, 1960-1968, including a 1965 schoolyard reprimand and a 1966 machinery inspection.",
 "appearance": "White Anglo-Australian men with professional builds and short neatly combed hair.",
 "clothing_by_period": [
  {
   "years": "1948-1968",
   "clothing": "White shirts, ties and light suits or white coats, felt hats outdoors, and leather shoes dusted red on site visits."
  }
 ]
}
```
