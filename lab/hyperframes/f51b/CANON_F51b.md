# CANON_F51b — canon de Wittenoom viejo → nuevo, y 4 fotos armadas con el nuevo

Salida de `python lab/hyperframes/f51b/tabla_f51b.py`. Viejo = `lab/hyperframes/f51b/antes/05_visual_canon.json`, nuevo = `lab/hyperframes/f51b/canon_f51b.json`. Sin modelos, sin fal; nada de producción se escribe. Solo los textos y el diff, sin juicio.

- `canon_ficha_md5` viejo: `a08c790ceac3a982d0cdca904424371f`
- `canon_ficha_md5` nuevo: `4828d0e69b6edf3d58954849767ec1fd`

## 1. people_groups por id

| id | estado | appearance viejo | appearance nuevo | condition_by_period nuevo |
|---|---|---|---|---|
| prospectors_mine_owners | desaparece | Australian men of British or Irish descent, fair skin deeply sun-tanned and weathered, short hair, lean wiry build from bush prospecting. | — | — |
| company_managers | desaparece | Australian men of British descent, fair complexions, neatly cut and combed hair, office-worker builds. | — | — |
| mine_and_health_officials | desaparece | Australian men of British descent, fair skin, short neat hair, professional office builds. | — | — |
| mine_and_mill_workers | cambia | Mixed Australian (British-descended) and Southern, Central and Eastern European men, light to olive skin darkened by sun, short hair, lean muscular builds from heavy manual labour, often coated in fine dust. | Adult men of European origin (Anglo-Australian, Central and Eastern European, Southern European including Spanish), with fair to olive skin, dark to light hair and lean working builds. | 1937-1966: Covered head to toe in fine fibrous asbestos dust, sunburnt and exhausted from long shifts of up to 16 hours, with occasional untreated injuries such as a bandaged foot wound.; 1979-1992: Ageing former workers visibly ill with asbestosis, lung cancer and mesothelioma: breathless, gaunt and frail. |
| spanish_migrant_families | cambia | Spanish Mediterranean people with olive to light skin, dark brown or black hair, dark eyes, slim to medium builds; women and children tanned and dusted red in Wittenoom. | Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes. | 1962-1962: Seasick and drained by intense heat during the long sea voyage.; 1962-1964: Coated in red earth and fine asbestos dust; children's hands and mouths dusty from fraying raw asbestos; a mother weakened after a kidney infection and a complicated forceps birth.; 1991-1992: A former miner rapidly declining with mesothelioma in the months after diagnosis. |
| town_children | desaparece | Australian, European and Spanish children with light to olive skin, tanned, tousled hair, dusted with red earth and fine asbestos powder. | — | — |
| union_and_arbitration | desaparece | Australian men of British descent, fair skin, short neat hair, mixed office and former manual-labour builds. | — | — |
| australian_politicians | cambia | Predominantly Australian men of British descent, fair skin, short groomed hair, middle-aged office builds. | Adult Australian men of European descent with fair skin and short hair. | — |
| victims_advocates_and_lawyers | desaparece | Mixed Australian and European-born adults; ill former workers aged, thin and frail from lung disease. | — | — |
| banjima_traditional_owners | cambia | Aboriginal Australian people with dark brown skin, dark curly or wavy hair, elders with grey hair and beards, builds shaped by outdoor life in the Pilbara. | Aboriginal Australian people with dark brown skin, dark wavy to curly hair (greying in elders) and brown eyes. | 2023-2024: An elder visibly ill and declining from mesothelioma. |
| international_un_official | desaparece | — | — | — |
| airport_police | desaparece | — | — | — |
| wittenoom_town_residents | nuevo | — | — | 1940-1966: Living and playing on tailings-surfaced yards and roads, with fine asbestos and red dust settling on skin, hair and clothing.; 1978-2023: A dwindling, isolated population living among demolished lots without services. |
| company_owners_and_managers | nuevo | — | Adult Anglo-Australian men of European descent with fair to sun-weathered skin and short hair. | — |
| government_mines_and_health_officials | nuevo | — | Adult Australian men of European descent with fair to sun-weathered skin and short hair. | 1944-1966: Dusted by mill and site dust during inspections. |
| unions_and_labour_arbitration | nuevo | — | Adult Australian men of European descent with fair to tanned skin. | 1957-1957: Board members observing workers and surroundings blanketed in thick dust at the mill. |
| asbestos_victims_advocates_and_lawyers | nuevo | — | — | 1979-1992: Many victims visibly ill with asbestos-related disease: breathless and emaciated. |
| international_human_rights_observers | nuevo | — | — | — |
| environmental_assessors | nuevo | — | — | — |
| australian_airport_police | nuevo | — | — | — |

## 2. Lo demás del canon (viejo → nuevo)

### era_visual_canon (claves sueltas, sin periods)

- `clothing` (cambia): Mining era (1937-1966): miners and mill workers in sweat-stained cotton work shirts, khaki or navy shorts or trousers, leather work boots, felt slouch hats or cloth caps, often coated in fine dust, with little or no respiratory protection. Australian officials, inspectors and company managers in lightweight suits, ties and felt hats, or short-sleeved shirts in the heat. Migrant European and Spanish wives in simple cotton dresses, cardigans and headscarves. Children in shorts and cotton frocks, often barefoot or in sandals. Decline era (1970s-1990s): open-collar shirts, wide-lapel suits for lawyers and politicians, casual knitwear for retired former residents. Contemporary era (2000s-2020s): officials and lawyers in modern business attire; Aboriginal traditional owners and activists in casual shirts, jeans and broad-brimmed hats; any personnel inside the contaminated zone in modern disposable protective coveralls and respirators. → Mining-era workforce (1937-1966): miners and mill hands in sweat-stained cotton work shirts or sleeveless singlets, khaki or drill work trousers and shorts, heavy leather work boots and wide-brimmed felt or cloth hats, at most a simple cloth dust mask, with clothing and skin coated in fine fibrous dust. Company managers, mines inspectors and public health doctors wear lightweight suits or shirtsleeves with ties, trousers and leather shoes. Migrant wives wear modest knee-length cotton dresses and cardigans, and children wear shorts, simple frocks and sandals or go barefoot. Later decades: 1970s-1990s casual Australian rural clothing and plain business suits for officials, lawyers and politicians. From 2008, environmental officers wear modern protective gear behind barricades, and Banjima traditional owners and advocates wear contemporary casual or formal clothing at hearings and press events.
- `technology` (cambia): Mining era: mechanical crushing and fibre-separation mills, belt conveyors, mill fans and early dust-extraction ducting, valve radios, wall-mounted telephones, manual typewriters, carbon copies, paper files, box and folding film cameras producing black-and-white or sepia prints, ceiling fans, basic hospital instruments including obstetric forceps. NO computers, NO digital displays, NO mobile phones, NO plastic signage, NO modern air-monitoring instruments. Decline era: 1980s office equipment, CRT televisions, landline phones. Contemporary era: modern legal and government offices, digital cameras, laptops, warning signage and permanent road barricades. → 1937-1966: crushers, ore mills, belt conveyors and bagging plants with rudimentary dust-extraction equipment added late; manual typewriters, carbon-copy paper reports and handwritten letters; wall-mounted crank or rotary telephones; valve radios; film cameras and black-and-white or sepia prints; hospital forceps and basic mid-century medical instruments. NO plastic-cased electronics, NO digital displays, NO powered respirators, NO air-monitoring electronics. 1980s-1990s: fax machines, early desktop computers, CRT televisions. From 2008: digital mapping, laptops and modern sampling gear in remediation contexts only.
- `vehicles_machinery` (cambia): Mining era: mid-century flatbed trucks and tipper trucks carrying ore and tailings, utility vehicles and four-wheel-drive bush vehicles, mid-century sedans, small propeller passenger aircraft landing on a dirt airstrip, ore crushers and conveyors at the mill, tailings dumped down gorge walls. Ocean liners from Málaga to Australia via the Suez Canal. Decline era: 1970s-1980s Australian sedans and four-wheel drives, demolition machinery. Contemporary era: modern four-wheel drives stopped at permanent barricades; no operating mine machinery. → 1937-1966: dusty flatbed and tipper trucks hauling tailings, early utility vehicles and four-wheel-drive field vehicles on unsealed red-earth tracks, ore-processing mill plant beside the gorge, and small propeller-driven passenger aircraft on a bare tailings-surfaced airstrip. Migrant arrival by ocean passenger liner from Málaga through the Suez Canal. Later decades: 1970s-1990s sedans and 4WDs, and demolition excavators of 1986-1992. From 2008: modern 4WD government vehicles stopped at permanent barricades.
- `interiors` (cambia): Mining era: small worker houses and family homes of sheet metal, timber and asbestos-cement sheeting with plain furniture, enamel cookware, iron bedsteads and oscillating fans; a dust-choked mill interior with crushing machinery and thick suspended dust; a small town hospital ward with iron beds and basic obstetric equipment; government and company offices with typewriters, filing cabinets and paper reports. Later eras: family living rooms in Madrid with framed sepia photographs; courtrooms and parliamentary committee rooms; modern government offices. → 1937-1966: sparse company houses of corrugated iron, timber and fibro-cement sheeting with simple furniture, louvred windows, ceiling fans and dust on every surface; a basic single-room-style school; a small town hospital with iron beds and white-enamel fittings; a noisy mill interior thick with suspended fibre dust; plain government offices with filing cabinets and typewriters. Later: courtrooms and parliamentary hearing rooms in timber panelling (1988-1994); family living rooms in Madrid with sepia family photographs on display (interview setting).
- `forbidden_anachronisms` (cambia): In mining-era scenes: no modern respirators, hazmat suits, hi-visibility vests or hard hats with modern logos; no sealed bitumen roads with painted lines; no modern four-wheel drives, SUVs or pickup trucks; no jet aircraft at the airstrip; no plastic warning signs or asbestos-hazard pictograms; no mobile phones, digital cameras, computers or LED lighting; no solar panels, satellite dishes or wind turbines; no contemporary clothing, sneakers or synthetic sportswear. → In 1937-1966 scenes: no hi-vis vests, no hard hats with modern logos, no modern P2/P3 respirators or hazmat suits, no sealed asphalt with painted road lines, no plastic water bottles, no smartphones or digital screens, no modern 4WD SUVs, no jet aircraft at the airstrip, no warning signs or barricades (these belong only to the post-2006 forbidden zone). In demolished-era scenes, do not show the town as intact or populated.
- `materials_textures` (cambia): Worker houses built from corrugated sheet metal, timber and asbestos-cement sheeting; loose, crumbling fibrous asbestos that shreds into fine powder when handled; compacted asbestos tailings laid as the surface of roads, yards, driveways, the schoolyard, public spaces and the airstrip; fine powdery dust coating people, buildings and the mill; loose tailings dumps tipped into the gorges and washed by water into creek beds, pools and floodplains. → Company dwellings of corrugated iron, timber and fibro-cement (asbestos-cement) sheeting; loose, crumbly, fibrous crocidolite mine tailings spread and compacted as the surface of roads, the airstrip, house yards, the school playground and public spaces; raw fibrous asbestos that frays into threads and sheds a fine powder when handled; a fine fibrous dust coating people, buildings and machinery; tailings dumps in rocky gorge walls; asbestos deposits settled in creek beds, pools and alluvial floodplains.
- `color_palette` (cambia): Exterior dominated by intense red earth and red dust under harsh desert light, with blue-grey asbestos tailings surfaces and pale grey dust films over buildings and workers; interiors not documented; surviving family imagery described as sepia-toned. → Exterior: intense red-ochre earth and red dust everywhere, blue-grey crocidolite tailings on roads, yards and dumps (INFERENCE from 'blue asbestos'), dull grey corrugated iron and pale grey fibro walls under a harsh bright desert sky; interior colours not documented.
- `scale_dimensions` (cambia): A small, isolated outback mining town with a dirt airstrip sized for small propeller aircraft, three mines in the surrounding gorges, more than three million tonnes of tailings left behind, and an official asbestos management area of 46,840 hectares extending down drainage lines toward the Fortescue River. → The official Wittenoom Asbestos Management Area covers 46,840 hectares. More than three million tonnes of tailings were left behind after three mines produced about 150,000 tonnes of commercial asbestos (1937-1966). Contamination extends downstream through creeks, pools and floodplains toward the Fortescue River catchment. The town is small and isolated, with a small-aircraft airstrip; building heights and footprints are not documented (INFERENCE: low single-storey structures).
- `distinctive_features` (cambia): A small mining town in the red Pilbara desert whose own roads, yards, schoolyard and airstrip were paved with blue asbestos tailings, so the poison literally formed the ground people walked and played on; today it is an emptied, demolished, unmapped zone sealed by permanent barricades. → An isolated red-earth Pilbara mining town whose roads, yards, school playground and airstrip were literally paved with crumbling blue crocidolite tailings, set beside gorges choked with tailings dumps. Today it is emptied, demolished and sealed off by permanent barricades as a 46,840-hectare forbidden contamination zone.
- `demographics` (cambia): Documented workforce of Australian miners and mill workers, post-war European displaced persons assigned under federal work contracts (1948-1951), European recruits from private CSR recruitment trips (from 1950), and Spanish migrant families under the Spain-Australia migration agreement (early 1960s), with wives and young children living in town; mill workers dressed in dust-coated work clothes; Banjima Aboriginal traditional owners documented on their country in the contemporary era. Ethnicity and origin come from written records and testimony, not photographs. → Mining-era population (1937-1966): a predominantly male, high-turnover workforce of miners, mill hands and fitters, with 59% leaving within six months. It combined Australian workers, post-war European displaced persons assigned 1948-1951, CSR-recruited Europeans from 1950, and Spanish migrants arriving under the 1958 Spain-Australia agreement, accompanied by wives and young children; workers appear in dust-coated work clothes. Australian company managers, government mines and health officials and union representatives appear as visitors and authorities. Banjima Aboriginal traditional owners hold the land, documented as claimants and activists in 2023-2026. Composition comes from written and oral records, not photographs.
- `visual_reference_availability` (cambia): No sourced visual block was supplied; every place/object statement above derives from TEXT sources: oral testimony (red earth, dust everywhere, sheet-metal, timber and asbestos-cement houses, small propeller plane, children shredding asbestos), official and historical documents (tailings used for town, airstrip, roads, yards, schoolyard; mill dust clouds recorded by the Board of Reference in 1957; permanent barricades; water-borne deposits in creeks and floodplains), and technical reports (tonnages, 46,840 ha area). Family photographs are mentioned in text (portrait with bandaged foot, baptism photo dated 1963-07-07, sepia family photos in an interview) but were not provided. The blue-grey colour of tailings is INFERENCE from the documented blue asbestos (crocidolite); interior colours are undocumented. → No [VISUAL] source block was supplied; every place detail is TEXT-sourced. Oral testimony: a former child resident's memories supply the small propeller plane, red earth, dust everywhere, tin/timber/fibro-cement houses and children fraying asbestos. A former worker's testimony supplies the tailings spread on yards, accesses, schools, kindergarten and churches. Official written records supply the 1957 Board of Reference dust cloud at the mill and the 1965 playground tailings reprimand. Technical and environmental reports supply the tailings tonnage, 46,840 ha area, and deposits in creeks, pools and floodplains. An official government notice supplies the permanent barricades. The only photographic sources mentioned are private family albums: a portrait showing a bandaged foot, a photo dated 1963-07-07 linked to a baptism, and sepia family photographs seen in an interview. None are reproduced in the pool. Tailings colour is inferred from 'blue asbestos'; interior colours and building dimensions are undocumented.
- `condition_evolution` (cambia): {"at_event": "An operating mining town in the early 1960s: inhabited sheet-metal and asbestos-cement houses, a working mill wrapped in thick dust clouds, trucks dumping tailings to surface roads, yards and the schoolyard, children playing on the ground, and small propeller planes landing on the tailings airstrip.", "later": "After mining ended in December 1966 the town was progressively reduced from 1978, its school, nursing post and police station closed and buildings demolished from 1986 to 1992, the airport closed in 1993, power cut in 2006, the town formally abolished and erased from maps and signs in 2007, the last residents gone by 2022-2023 and remaining structures demolished, leaving tailings eroding into creeks and the Fortescue catchment behind permanent barricades on every access road."} → {"at_event": "During the mining era (1937-1966) the town is inhabited and operating. The mill stands under a thick suspended dust cloud with dust-covered workers, trucks dump fresh tailings onto yards and roads, children play on tailings-surfaced ground, and houses of tin, timber and fibro-cement sit on red earth with fine dust coating everything.", "later": "From 1978 the town is deliberately run down. Buildings are demolished and the school, nursing post and police station close (1986-1992); the airport closes (1993); power is cut (2006); the town is abolished and erased from maps and signs (2007, some sources 2006); the last residents leave and final structures are demolished (2022-2023). Wind and water erode the tailings into creeks and floodplains, and permanent barricades block the town and gorge entrances."}

### era_visual_canon.periods (por years: years y clothing)

- **1937-1945** (quitado): {"years": "1937-1945", "clothing": "Rough bush work clothes for prospectors and early miners: cotton shirts, braces, wide-brimmed felt hats, heavy boots; officials in wartime-austere suits and hats."}
- **1946-1966** (quitado): {"years": "1946-1966", "clothing": "Dust-covered miners and mill hands in work shirts, shorts or trousers and boots; migrant families in modest European clothing adapted to heat; officials and doctors in lightweight suits or short sleeves with ties."}
- **1967-1992** (quitado): {"years": "1967-1992", "clothing": "Remaining residents and visitors in 1970s-1980s casual wear; lawyers, judges and politicians in period suits; ill former workers in hospital gowns or casual clothes."}
- **1993-2026** (quitado): {"years": "1993-2026", "clothing": "Contemporary casual wear for Banjima traditional owners and activists; modern business attire for lawyers, officials and a UN rapporteur; modern protective coveralls and respirators for anyone inside the zone."}
- **1937-1949** (agregado): {"years": "1937-1949", "clothing": "Prospectors and early miners in rough cotton shirts, singlets, khaki trousers, felt slouch hats and leather boots; inspectors and managers in suits or shirtsleeves with ties; wartime and post-war austerity civilian dress."}
- **1950-1966** (agregado): {"years": "1950-1966", "clothing": "Multinational workforce in singlets, work shirts, shorts or drill trousers, wide-brim hats and work boots, all coated in dust; Spanish and other European migrant wives in modest cotton dresses; children in shorts and simple frocks; officials in lightweight suits."}
- **1967-2007** (agregado): {"years": "1967-2007", "clothing": "1970s-1990s casual Australian clothing for remaining residents; business suits for lawyers, judges' robes in court, suits for parliamentarians; ageing former workers in plain civilian clothes."}
- **2008-2026** (agregado): {"years": "2008-2026", "clothing": "Contemporary casual and formal clothing for Banjima traditional owners, advocates and lawyers; modern protective suits and respirators only for officials inside the contaminated zone."}

### anachronism_blocklist

- quitado: contemporary clothing
- quitado: modern industrial safety equipment in mining-era scenes
- quitado: hazmat suits and modern respirators before the 1980s
- quitado: hi-visibility vests
- quitado: sealed bitumen roads with painted lines
- quitado: modern SUVs and pickup trucks in mining-era scenes
- quitado: jet aircraft at the town airstrip
- quitado: plastic asbestos-hazard warning signs before closure
- quitado: solar panels and satellite dishes
- agregado: contemporary clothing (post-2000s) in mining-era scenes
- agregado: high-visibility safety vests in 1937-1966 scenes
- agregado: modern P2 respirators or hazmat suits in mining-era scenes
- agregado: modern industrial safety equipment and branded hard hats
- agregado: sealed asphalt roads with painted line markings
- agregado: modern 4WD SUVs in mining-era scenes
- agregado: jet aircraft at the Wittenoom airstrip
- agregado: drones
- agregado: asbestos warning signs and barricades in pre-1978 scenes

### documented_people (por name: appearance_canon)

- **Hancock**:
  - `appearance_canon` (cambia): an adult Australian prospector in rugged bush work clothes and wide-brimmed hat, weathered by outdoor work → a young adult Australian prospector and mine owner in rugged outback work clothes and a wide-brimmed hat
- **Wright**:
  - `appearance_canon` (cambia): an adult Australian prospector and mine manager in practical bush work clothes, sun-weathered → a young adult Australian prospector in practical outback work clothes
- **Eric Saint**:
  - `appearance_canon` (cambia): an adult Australian government medical officer in a lightweight suit and tie with a serious, concerned demeanor → a young adult Australian medical officer in shirtsleeves and tie with an earnest, concerned demeanor
- **Chifley**:
  - `appearance_canon` (cambia): a senior Australian statesman in a formal dark suit with a composed public demeanor → a middle-aged to elderly Australian national politician in a dark suit with a confident public manner
- **McNulty**:
  - `appearance_canon` (cambia): a middle-aged Australian public health physician in a shirt and tie with a clinical, attentive demeanor → a middle-aged Australian public health physician in a plain suit
- **Davidson**:
  - `appearance_canon` (cambia): a middle-aged Australian senior health official in a suit with a stern, authoritative demeanor → a middle-aged Australian senior health official in a lightweight suit with a stern demeanor
- **Major**:
  - `appearance_canon` (cambia): a middle-aged Australian industrial hygienist in shirt sleeves and tie, inspecting machinery with a critical eye → a middle-aged Australian industrial hygienist in shirtsleeves, inspecting machinery with a notebook
- **James Vernon**:
  - `appearance_canon` (cambia): a middle-aged Australian corporate executive in a dark tailored suit with a formal boardroom demeanor → a middle-aged Australian corporate executive in a dark business suit
- **Court**:
  - `appearance_canon` (cambia): a middle-aged Australian state politician in a dark business suit with a guarded official demeanor → a middle-aged Australian state politician in a business suit
- **Peter Gordon**:
  - `appearance_canon` (cambia): an adult Australian litigation lawyer in a business suit with a determined courtroom demeanor → a young adult to middle-aged Australian lawyer in a dark business suit
- **Ben Wyatt**:
  - `appearance_canon` (cambia): a middle-aged Australian state government minister in a modern business suit → a middle-aged Australian state government minister in a contemporary business suit
- **Marcos Orellana**:
  - `appearance_canon` (cambia): a middle-aged international UN human rights expert in modern business attire with an attentive, listening demeanor → a middle-aged international human rights official in smart contemporary attire
- **Maitland Parker**:
  - `appearance_canon` (cambia): an elderly Aboriginal Australian Banjima elder in casual outback clothing with a dignified, weary bearing → an elderly Aboriginal Australian Banjima man with a dignified, resolute demeanor
- **Melita Markey**:
  - `appearance_canon` (cambia): a middle-aged Australian woman advocate in modern professional attire with an earnest demeanor → a middle-aged Australian woman advocate in contemporary professional attire
- **Daniel Écija**:
  - `appearance_canon` (cambia): a young adult Spanish migrant miner in dusty work clothes, in one portrait with a bandaged foot → a young adult Spanish migrant miner in work clothes, one foot visibly bandaged
- **María Bernal**:
  - `appearance_canon` (cambia): a young adult Spanish woman in a simple cotton dress, physically weakened after a difficult birth, hopeful but strained → a young adult Spanish newlywed migrant woman in a modest cotton dress, hopeful yet physically weakened
- **Daniel Écija hijo**:
  - `appearance_canon` (cambia): a young adult man of Spanish descent born in Australia, in casual travel clothes at an airport checkpoint → a young adult Spanish man presenting travel documents at an airport checkpoint
- **Milagros Barroso**:
  - `appearance_canon` (cambia): a young adult Spanish mother in a modest cotton dress, caring for small children in the heat and dust → a young adult Spanish migrant mother in a modest cotton dress
- **Ramón de Juan**:
  - `appearance_canon` (cambia): an adult Spanish migrant miner in dust-covered work shirt and trousers, visibly exhausted from long shifts → a young adult Spanish miner in dust-coated work clothes with a fatigued expression
- **Víctor Calvo**:
  - `appearance_canon` (cambia): a young Spanish boy in shorts and a cotton shirt, red dust on skin and clothes → a young Spanish boy in simple shorts and shirt, curious and dust-covered
- **John Patrick**:
  - `appearance_canon` (cambia): a newborn infant of Spanish parents wrapped in a light cotton blanket → a newborn infant wrapped in a plain cotton blanket
- **Mercedes**:
  - `appearance_canon` (cambia): a young Spanish girl in a simple cotton frock with dust on her sandals → a young Spanish girl in a simple cotton frock

### documented_props (por nombre: nombre · forma · anclado · foto_madre)

igual

### central_subject (campo por campo)

igual

## 3. Prompts armados con el canon nuevo (en memoria) al lado del C′ de F50i

Código de producción como `f51a/contrato.py`: `rg.fotos(cap)` sobre el 03_visual.json vivo (solo lectura), `escala` del beat, `rg.rearmar_una(it, escala, topic['documented_people'], grupos)` con `grupos` = `people_groups` del canon nuevo; `topic` = `get_topic_by_id` (topics_db vivo).

### 2/9 · spanish_migrant_families · palabras C′ 123 → nuevo 123

Byte a byte igual a C′ de F50i: **no**

Diff palabra por palabra (- C′ de F50i, + nuevo): + people + of - people + European + origin - or + to - hair, + hair + and - eyes, + eyes. - slim - to - medium - builds.

**C′ (F50i)**

```
A young Spanish boy about seven, pale under his tan, slim, dark hair damp, cotton shirt, beside his mother in a cotton dress. The seasick boy sits slumped on a deck bench, head resting against his mother's side as the ship rolls. Spanish Mediterranean people with olive to light skin, dark brown or black hair, dark eyes, slim to medium builds. Lower open deck of the liner on the Indian Ocean, 1962, wet railings and rolling swell. Flat overcast sea light. Medium shot, eye-level, shallow depth of field, 50mm lens. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

**Nuevo (canon nuevo)**

```
A young Spanish boy about seven, pale under his tan, slim, dark hair damp, cotton shirt, beside his mother in a cotton dress. The seasick boy sits slumped on a deck bench, head resting against his mother's side as the ship rolls. Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes. Lower open deck of the liner on the Indian Ocean, 1962, wet railings and rolling swell. Flat overcast sea light. Medium shot, eye-level, shallow depth of field, 50mm lens. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

### 4/11 · spanish_migrant_families · palabras C′ 115 → nuevo 115

Byte a byte igual a C′ de F50i: **no**

Diff palabra por palabra (- C′ de F50i, + nuevo): + people + of - people + European + origin - or + to - hair, + hair + and - eyes, + eyes. - slim - to - medium - builds.

**C′ (F50i)**

```
Steel obstetric forceps on an enamel instrument tray, a weakened Spanish woman out of focus in the bed beyond. The instruments laid ready beside the delivery bed during a difficult birth. Spanish Mediterranean people with olive to light skin, dark brown or black hair, dark eyes, slim to medium builds. Delivery room of the Wittenoom hospital, June 1963, enamel basins, iron bed frame. Single overhead bulb, deep shadows at the room's edges. Close shot, slightly high angle, shallow depth of field, 50mm. A grainy 35mm documentary photograph taken in 1963, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

**Nuevo (canon nuevo)**

```
Steel obstetric forceps on an enamel instrument tray, a weakened Spanish woman out of focus in the bed beyond. The instruments laid ready beside the delivery bed during a difficult birth. Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes. Delivery room of the Wittenoom hospital, June 1963, enamel basins, iron bed frame. Single overhead bulb, deep shadows at the room's edges. Close shot, slightly high angle, shallow depth of field, 50mm. A grainy 35mm documentary photograph taken in 1963, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

### 4/12 · spanish_migrant_families · palabras C′ 129 → nuevo 129

Byte a byte igual a C′ de F50i: **no**

Diff palabra por palabra (- C′ de F50i, + nuevo): + people + of - people + European + origin - or + to - hair, + hair + and - eyes, + eyes. - slim - to - medium - builds.

**C′ (F50i)**

```
A sepia baptism photograph of a young Spanish family: the father in a pressed shirt, the mother in a cotton dress, a large infant in a white christening gown. The photograph lying on a dusty table, the family posed at a church font. Spanish Mediterranean people with olive to light skin, dark brown or black hair, dark eyes, slim to medium builds. Tabletop in a sheet-metal miners' house, July 1963. The lower white margin of the photograph reads "7 July 1963" in handwritten ink, in clear crisp lettering. Slanting late-afternoon light through a louvred window. Detail shot, top-down, shallow depth of field, macro. A grainy 35mm documentary photograph taken in 1963, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio.
```

**Nuevo (canon nuevo)**

```
A sepia baptism photograph of a young Spanish family: the father in a pressed shirt, the mother in a cotton dress, a large infant in a white christening gown. The photograph lying on a dusty table, the family posed at a church font. Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes. Tabletop in a sheet-metal miners' house, July 1963. The lower white margin of the photograph reads "7 July 1963" in handwritten ink, in clear crisp lettering. Slanting late-afternoon light through a louvred window. Detail shot, top-down, shallow depth of field, macro. A grainy 35mm documentary photograph taken in 1963, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio.
```

### 5/8 · airport_police, spanish_migrant_families · palabras C′ 134 → nuevo 134

Byte a byte igual a C′ de F50i: **no**

Diff palabra por palabra (- C′ de F50i, + nuevo): + people + of - people + European + origin - or + to - hair, + hair + and - eyes, + eyes. - slim - to - medium - builds.

**C′ (F50i)**

```
An Australian airport police officer, middle-aged, British-descended, in a 1980s light-blue epaulette shirt and peaked cap; a young dark-haired man of Spanish descent in jeans and a jacket across the counter, seen over his shoulder. The officer bows his head over the open passport, reading the birthplace, about to look up again. Spanish Mediterranean people with olive to light skin, dark brown or black hair, dark eyes, slim to medium builds. Passport checkpoint booth in an Australian airport terminal, 1985. Hard overhead fluorescent light, high contrast on the counter. Medium shot, over-the-shoulder eye-level, 85mm, shallow depth of field on the officer. A grainy 35mm documentary photograph taken in 1985, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

**Nuevo (canon nuevo)**

```
An Australian airport police officer, middle-aged, British-descended, in a 1980s light-blue epaulette shirt and peaked cap; a young dark-haired man of Spanish descent in jeans and a jacket across the counter, seen over his shoulder. The officer bows his head over the open passport, reading the birthplace, about to look up again. Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes. Passport checkpoint booth in an Australian airport terminal, 1985. Hard overhead fluorescent light, high contrast on the counter. Medium shot, over-the-shoulder eye-level, 85mm, shallow depth of field on the officer. A grainy 35mm documentary photograph taken in 1985, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

