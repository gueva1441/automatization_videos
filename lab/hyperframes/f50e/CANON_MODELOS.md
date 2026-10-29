# CANON_MODELOS — el canon de Wittenoom con Flash, Sonnet 5.5 y Opus 5.5 (F50e-A, en texto)

Salida de `python -u lab/hyperframes/f50e/canon_modelos.py` (las llamadas) y `canon_modelos_md.py` (esta tabla). Mismo pedido que `step_4e.canon_desde_ficha`; nada se guardó en producción.

- md5 del pedido: `d2568e2a94c5db96f9836451b2f80cd7` en todos los intentos de las 7 corridas: sí
- Producción intacta (md5 antes = después): topics_db True · 05_visual_canon.json True
- Gasto (cost_tracker `f50e-canon-modelos`): US$ 0.8093 · tope US$ 1,00
- **PARADA por tope:** tope: gastado 0.8093 + 2 × opus 1 0.3464 = 1.5021 > 1.0: opus 2 y 3 no corren
- Fotos: 96, con año (anio_ancla o respaldo[0]): 96

**Aviso — el esquema no llegó a los modelos Claude.** El primer intento de cada corrida de Sonnet y Opus (con `VISUAL_CANON_SCHEMA_FICHA` como structured output) volvió HTTP 400: «Schemas contains too many optional parameters (46)… (limit: 24)». `extract_visual_canon` cayó entonces a su respaldo de producción: el MISMO texto, sin esquema. Esas respuestas son las que se miden. Flash sí corrió con el esquema. El pedido es el mismo; el formato forzado, no.

## Resumen por modelo

| modelo | corridas medidas | fotos cubiertas mín · máx | grupos (por corrida) | grupos con años sin ropa (por corrida) | years ilegibles | US$ promedio por corrida | fallas |
|---|---|---|---|---|---|---:|---|
| flash | 2 de 3 | 61 · 61 de 96 | 22 / 5 | 1 / 0 | ninguno | 0.0255 | flash_2: canon sin periods |
| sonnet | 3 de 3 | 96 · 96 de 96 | 7 / 10 / 8 | 1 / 0 / 1 | ninguno | 0.1287 | — |
| opus | 1 de 3 (2 no corrieron: tope) | 96 · 96 de 96 | 13 | 0 | ninguno | 0.3464 | — |

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

## 4c — fotos sin ningún period que las cruce (y el que les daría la regla del «más cercano»)

- flash_1: 35 fotos — cap 5: [1971, 1978, 1985, 1986, 1991, 1993] → 1937-1966; cap 6: [1988, 1989, 1991, 1992, 2007, 2016] → 1937-1966; cap 7: [2021, 2023, 2024] → 1937-1966
- flash_3: 35 fotos — cap 5: [1971, 1978, 1985, 1986, 1991, 1993] → 1958-1966; cap 6: [1988, 1989, 1991, 1992, 2007, 2016] → 1958-1966; cap 7: [2021, 2023, 2024] → 1958-1966
- sonnet_1: ninguna
- sonnet_2: ninguna
- sonnet_3: ninguna
- opus_1: ninguna

## 4d — grupos con años de su where_when sin ropa por tramo

- flash_1: `asbestos_diseases_society_ceo` años [1979] (ropa: 1980-2020s)
- flash_3: ninguno
- sonnet_1: `spanish_migrant_families` años [1966, 1971] (ropa: 1962-1964 · 1985-2020s)
- sonnet_2: ninguno
- sonnet_3: `spanish_migrant_families` años [1966, 1971] (ropa: 1962-1964 · 1985-1991)
- opus_1: ninguno

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

### sonnet_1 (96/96)

```json
[
 {
  "years": "1937-1949",
  "clothing": "Khaki or drill work shirts and trousers, felt slouch hats, heavy boots for prospectors and early miners. Plain suits for officials and managers.",
  "technology": "Hand tools, early mechanical crushing, paper reports and typewritten correspondence. NO digital devices.",
  "vehicles_machinery": "1930s-40s trucks, pack and prospecting gear, early small mill machinery, basic mine haulage.",
  "interiors": "Rough corrugated-iron and timber huts and offices, basic mine administration rooms, dusty mill sheds."
 },
 {
  "years": "1950-1966",
  "clothing": "Cotton work shirts, singlets, overalls and work boots for miners and mill workers, all dust-covered. Plain 1960s European civilian clothes for migrant families. Suits or shirt-and-tie for inspectors and managers.",
  "technology": "Analog photography, paper medical and inspection reports, radio and wall telephones, basic mechanical dust-reduction equipment.",
  "vehicles_machinery": "Small propeller aircraft, tipper trucks spreading tailings, working mill machinery with spills and leaks, ocean liners for migrants.",
  "interiors": "Houses of sheet metal, timber and uralita (asbestos cement), a dusty mill, a small hospital, a school with a tailings-covered yard, a church."
 },
 {
  "years": "1967-1992",
  "clothing": "Late-20th-century civilian clothes for remaining residents, officials, lawyers and campaigners. Plain office and court dress for hearings and inquiries.",
  "technology": "Typed legal and parliamentary documents, 1970s-90s film and early video, analog telephones and photocopied reports. NO smartphones.",
  "vehicles_machinery": "Demolition machinery, trucks, official government vehicles, shuttered mill and mine plant.",
  "interiors": "Emptying houses, closing school, nursing post and police station, courtrooms and parliamentary committee rooms."
 },
 {
  "years": "1993-2026",
  "clothing": "Contemporary civilian dress for officials, lawyers, Banjima representatives and researchers, kept strictly out of operating-town scenes.",
  "technology": "Modern environmental survey equipment, digital reports and maps appear only in official contexts, never inside the 1937-1966 town.",
  "vehicles_machinery": "Permanent barricades and blocked access roads, a closed airstrip, survey vehicles, eroding tailings in gorge and creek channels.",
  "interiors": "Largely empty. Last houses abandoned or demolished, with powers disconnected. Interiors appear only in legal and government settings."
 }
]
```

Grupo con más años:

```json
{
 "id": "mines_and_health_inspectors",
 "who": "Mines officials, public-health doctors, health inspectors, a public health commissioner and an industrial hygienist who reported on or warned about asbestos dust.",
 "where_when": "Wittenoom and government offices, 1944-1968, including 1948-1951, 1960, 1962, 1965, 1966 and 1968.",
 "appearance": "",
 "clothing_by_period": [
  {
   "years": "1944-1968",
   "clothing": "Plain suits or dust-marked shirts and trousers for field inspections, doctors in simple professional dress."
  }
 ]
}
```

### opus_1 (96/96)

```json
[
 {
  "years": "1937-1947",
  "clothing": "Prospectors and early miners in rough flannel or cotton shirts, heavy trousers with braces, felt hats and leather boots; officials and inspectors in three-piece suits and fedoras.",
  "technology": "Hand tools, early pneumatic drills, blasting explosives, valve radios, telegraph and manual typewriters; no plastics, no electronics.",
  "vehicles_machinery": "1930s-1940s utility trucks and small flatbed lorries on dirt tracks, rudimentary early mill machinery at Yampire and Wittenoom gorges.",
  "interiors": "Rough timber and corrugated-iron huts and camp buildings, kerosene lamps, packed-earth floors, bare work benches."
 },
 {
  "years": "1948-1966",
  "clothing": "Miners and mill hands in singlets or cotton work shirts, khaki shorts, work boots and felt hats with no respirators, dust-covered; migrant women in light cotton dresses and headscarves; children in shorts or simple dresses, often barefoot; company managers and health officials in lightweight suits.",
  "technology": "Full-scale mill with crushers, conveyors and fibre bagging, rudimentary dust-reduction equipment installed late, valve radios, rotary telephones, film cameras, typewritten reports and memos.",
  "vehicles_machinery": "Tipper trucks delivering blue tailings to yards and roads, rugged four-wheel-drive utilities, small twin-engine propeller aircraft on the tailings airstrip, passenger liners carrying European migrants.",
  "interiors": "Company houses of timber, corrugated iron and fibro-cement sheeting, the town hospital ward, school classrooms, dust-filled mill sheds."
 },
 {
  "years": "1967-1992",
  "clothing": "1970s-1980s civilian clothing for remaining residents; suits and ties for lawyers, judges' robes in court, suits for parliamentarians and officials; former workers shown older in ordinary casual clothes.",
  "technology": "CRT televisions, electric typewriters, photocopied legal documents, early office computers only from the late 1980s; airport passport desks with paper documents.",
  "vehicles_machinery": "1970s-1980s four-wheel drives and sedans, demolition machinery clearing town buildings in 1986-1992.",
  "interiors": "Courtrooms, law offices, parliamentary committee rooms, a shrinking town with closed school, nursing post and police station."
 },
 {
  "years": "1993-2026",
  "clothing": "Present-day scenes only: Banjima traditional owners and advocates in contemporary outdoor clothing; government and legal figures in modern business attire; no people inside the forbidden zone except as implied past.",
  "technology": "Contemporary technology permitted only in explicitly present-day segments (legal offices, interviews); the town itself shows no functioning infrastructure after the 2006 power disconnection.",
  "vehicles_machinery": "Modern four-wheel drives outside the zone, demolition equipment in 2022-2023, permanent barricades across access roads.",
  "interiors": "Interview settings with sepia family photographs, legal and government offices; the town has no surviving interiors after final demolition."
 }
]
```

Grupo con más años:

```json
{
 "id": "mine_and_mill_workers",
 "who": "Asbestos miners, mill hands, fitters and laborers at Wittenoom, a high-turnover mix of Australians and European migrants.",
 "where_when": "Wittenoom mines and mill from 1937 to 1966, documented especially in 1946-1959 dust disputes and the 1957 Board of Reference inspection; survivors appear as aging former workers in the 1980s.",
 "appearance": "Mixed Australian and European men, fair to olive skin with sun-darkened faces and arms, lean and muscular from heavy manual labor, skin, hair and clothes coated in fine pale fibrous dust.",
 "clothing_by_period": [
  {
   "years": "1937-1947",
   "clothing": "Rough cotton or flannel work shirts, heavy trousers with braces, leather boots and battered felt hats, no respiratory protection."
  },
  {
   "years": "1948-1966",
   "clothing": "Singlets or short-sleeved cotton work shirts, khaki shorts, work boots and felt or slouch hats, short practical haircuts, dust-caked clothing with at most a cloth rag over the mouth."
  },
  {
   "years": "1979-1992",
   "clothing": "Aging former workers in ordinary 1980s casual shirts and trousers, some visibly frail from illness."
  }
 ]
}
```
