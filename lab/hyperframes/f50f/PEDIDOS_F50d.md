# PEDIDOS_F50d — los 7 pedidos de casilleros con la época por tramo (en seco)

Salida de `python lab/hyperframes/f50d/pedidos_f50d.py`. Código de F50d con la llamada a Opus cortada. Referencia: `lab/hyperframes/f50c/pedidos/`. Zonas: «era» = bloque ERA del canon (hasta LUGAR PUNTUAL); «grupo» = las líneas de PEOPLE GROUPS sin su parte CLOTHING; «resto» = todo lo demás.

| cap | años de las fotos | periods que entran | canon nuevo: líneas era / grupo / resto | canon nuevo: fuera del canon entero y de los grupos | grupos | código solo: era / grupo / resto (líneas crudas) |
|---|---|---|---|---:|---:|---|
| 1 | 1961 1962 | 1946-1966 | 13 / 21 / 117 | 0 | 12 | 0 / 0 / 0 (14) |
| 2 | 1961 1962 | 1946-1966 | 13 / 21 / 117 | 0 | 12 | 0 / 0 / 0 (14) |
| 3 | 1943 1944 1946 1948 1957 1961 1962 | 1937-1945 · 1946-1966 | 18 / 21 / 117 | 0 | 12 | 0 / 0 / 0 (14) |
| 4 | 1961 1963 | 1946-1966 | 13 / 21 / 117 | 0 | 12 | 0 / 0 / 0 (14) |
| 5 | 1963 1966 1971 1978 1985 1986 1991 1993 | 1946-1966 · 1967-1992 · 1993-2026 | 23 / 21 / 117 | 0 | 12 | 0 / 0 / 0 (14) |
| 6 | 1988 1989 1991 1992 2007 2016 | 1967-1992 · 1993-2026 | 18 / 21 / 117 | 0 | 12 | 0 / 0 / 0 (14) |
| 7 | 2021 2023 2024 | 1993-2026 | 13 / 21 / 117 | 0 | 12 | 0 / 0 / 0 (14) |

**Resultado: FALLA — PARADA**

- ch01 canon nuevo: cambia fuera del bloque ERA y de PEOPLE GROUPS
- ch02 canon nuevo: cambia fuera del bloque ERA y de PEOPLE GROUPS
- ch03 canon nuevo: cambia fuera del bloque ERA y de PEOPLE GROUPS
- ch04 canon nuevo: cambia fuera del bloque ERA y de PEOPLE GROUPS
- ch05 canon nuevo: cambia fuera del bloque ERA y de PEOPLE GROUPS
- ch06 canon nuevo: cambia fuera del bloque ERA y de PEOPLE GROUPS
- ch07 canon nuevo: cambia fuera del bloque ERA y de PEOPLE GROUPS

## ch01

### código solo (canon de antes): diff crudo contra F50c

```diff
-  - wittenoom_miners_and_mill_workers: Various European migrant and Australian laborers working in the asbestos mines and processing mill. · Wittenoom, from 1937 to 1966. · APPEARANCE: Physically robust individuals, often appearing fatigued and covered in a pervasive fine dust, with diverse European features. · CLOTHING: Rugged, practical work clothes, heavy-duty trousers and shirts, sometimes wi
-  - spanish_migrant_families: Spanish families who migrated to Wittenoom under government schemes. · Wittenoom, primarily 1958-1966. · APPEARANCE: Adults and children of Southern European descent, appearing resilient and resourceful, adapting to a harsh desert environment, often showing signs of physical strain or everyday weariness. · CLOTHING: Simple, light clothing suitable for a hot, dusty cl
-  - australian_public_health_officials: Doctors, inspectors, and hygienists from Australian public health departments. · Wittenoom and state offices, 1944-1966. · APPEARANCE: Predominantly Caucasian, appearing professional, often with a serious or concerned demeanor due to the health risks. · CLOTHING: Formal or semi-formal attire of the era, such as suits, collared shirts, and ties, or clean uni
-  - australian_government_representatives: Various Australian federal and state government officials, including politicians, committee members, and regulators. · Government offices and occasional visits to Wittenoom, 1940s-2020s. · APPEARANCE: Predominantly Caucasian, appearing authoritative and formal, reflecting their political or administrative roles. · CLOTHING: Formal business attire, includ
-  - csr_corporate_personnel: Executives, managers, and other personnel from Colonial Sugar Refining (CSR) and its subsidiary, Australian Blue Asbestos (ABA). · Corporate offices and Wittenoom, 1937-1966. · APPEARANCE: Predominantly Caucasian, appearing well-dressed and corporate, often with an air of authority, sometimes dismissive of worker concerns. · CLOTHING: Business suits and formal wear, r
-  - banjima_traditional_owners_and_advocates: Indigenous Banjima people, including elders and legal advocates, asserting their rights over contaminated lands. · Wittenoom area and legal forums, 2010s-2020s. · APPEARANCE: Indigenous Australian people, often older, appearing resilient and determined, some bearing the visible or implied health consequences of asbestos exposure. · CLOTHING: Practical
-  - australian_airport_police: Law enforcement personnel working in Australian airports. · Australian airport checkpoint, 1985. · APPEARANCE: Predominantly Caucasian, appearing uniformed and professional. · CLOTHING: Standard police uniform of the mid-1980s, typically including a collared shirt, trousers, and a peaked cap.
+  - wittenoom_miners_and_mill_workers: Various European migrant and Australian laborers working in the asbestos mines and processing mill. · Wittenoom, from 1937 to 1966. · APPEARANCE: Physically robust individuals, often appearing fatigued and covered in a pervasive fine dust, with diverse European features. · CLOTHING: -
+  - spanish_migrant_families: Spanish families who migrated to Wittenoom under government schemes. · Wittenoom, primarily 1958-1966. · APPEARANCE: Adults and children of Southern European descent, appearing resilient and resourceful, adapting to a harsh desert environment, often showing signs of physical strain or everyday weariness. · CLOTHING: -
+  - australian_public_health_officials: Doctors, inspectors, and hygienists from Australian public health departments. · Wittenoom and state offices, 1944-1966. · APPEARANCE: Predominantly Caucasian, appearing professional, often with a serious or concerned demeanor due to the health risks. · CLOTHING: -
+  - australian_government_representatives: Various Australian federal and state government officials, including politicians, committee members, and regulators. · Government offices and occasional visits to Wittenoom, 1940s-2020s. · APPEARANCE: Predominantly Caucasian, appearing authoritative and formal, reflecting their political or administrative roles. · CLOTHING: -
+  - csr_corporate_personnel: Executives, managers, and other personnel from Colonial Sugar Refining (CSR) and its subsidiary, Australian Blue Asbestos (ABA). · Corporate offices and Wittenoom, 1937-1966. · APPEARANCE: Predominantly Caucasian, appearing well-dressed and corporate, often with an air of authority, sometimes dismissive of worker concerns. · CLOTHING: -
+  - banjima_traditional_owners_and_advocates: Indigenous Banjima people, including elders and legal advocates, asserting their rights over contaminated lands. · Wittenoom area and legal forums, 2010s-2020s. · APPEARANCE: Indigenous Australian people, often older, appearing resilient and determined, some bearing the visible or implied health consequences of asbestos exposure. · CLOTHING: -
+  - australian_airport_police: Law enforcement personnel working in Australian airports. · Australian airport checkpoint, 1985. · APPEARANCE: Predominantly Caucasian, appearing uniformed and professional. · CLOTHING: -
```

### canon nuevo: diff por zona

**era**

```diff
--- f50c
+++ f50d
-  clothing              : Miners wore rugged work clothes, often appearing dirty and dusty. Town residents wore practical, light attire suitable for hot desert conditions, including simple dresses, shirts, and shorts. Government and corporate officials wore more formal attire, such as suits, appropriate for their roles and the era.
-  technology            : Analog gauges, basic mining machinery with exposed components, rudimentary processing plants, simple residential appliances (e.g., older refrigerators, stoves), landline telephones, and radios. NO LEDs, NO digital displays, NO smartphones, NO advanced computing devices.
-  vehicles_machinery    : Early to mid-20th century trucks (e.g., for asbestos transport), desert-adapted 4x4 vehicles, passenger cars from the 1940s-1960s. Propeller-driven small aircraft for transport to the remote town. Mining equipment included drills, crushers, and conveyor belt systems.
-  interiors             : Residential interiors were basic and utilitarian, often in houses of corrugated iron, wood, and asbestos cement, prone to dust accumulation. Offices featured simple desks, manual typewriters, and basic filing systems. Public buildings like hospitals had functional, unadorned spaces with period-appropriate medical equipment.
-  forbidden_anachronisms: smartphones, LED screens, contemporary clothing (post-2000s), modern flat panels, modern cars (post-1970s), digital cameras, modern industrial safety equipment (e.g., advanced respirators), satellite dishes, renewable energy installations.
+  period 1946-1966:
+  clothing              : Dust-covered miners and mill hands in work shirts, shorts or trousers and boots; migrant families in modest European clothing adapted to heat; officials and doctors in lightweight suits or short sleeves with ties.
+  technology            : Full-scale crushing mill with conveyors, fans and later dust-reducing equipment, valve radios, telephones, typewriters, film cameras producing sepia and black-and-white family photos.
+  vehicles_machinery    : Ore and tipper trucks spreading tailings on roads and yards, small propeller aircraft on the tailings-surfaced airstrip, mid-century sedans and bush vehicles, ocean liners carrying migrants.
+  interiors             : Sheet-metal, timber and asbestos-cement houses, town hospital, school with tailings-covered yard, churches and community buildings, dusty mill interior.
+  forbidden_anachronisms: In mining-era scenes: no modern respirators, hazmat suits, hi-visibility vests or hard hats with modern logos; no sealed bitumen roads with painted lines; no modern four-wheel drives, SUVs or pickup trucks; no jet aircraft at the airstrip; no plastic warning signs or asbestos-hazard pictograms; no mobile phones, digital cameras, computers or LED lighting; no solar panels
```

**grupo**

```diff
--- f50c
+++ f50d
-  - wittenoom_miners_and_mill_workers: Various European migrant and Australian laborers working in the asbestos mines and processing mill. · Wittenoom, from 1937 to 1966. · APPEARANCE: Physically robust individuals, often appearing fatigued and covered in a pervasive fine dust, with diverse European features.
-  - spanish_migrant_families: Spanish families who migrated to Wittenoom under government schemes. · Wittenoom, primarily 1958-1966. · APPEARANCE: Adults and children of Southern European descent, appearing resilient and resourceful, adapting to a harsh desert environment, often showing signs of physical strain or everyday weariness.
-  - australian_public_health_officials: Doctors, inspectors, and hygienists from Australian public health departments. · Wittenoom and state offices, 1944-1966. · APPEARANCE: Predominantly Caucasian, appearing professional, often with a serious or concerned demeanor due to the health risks.
-  - australian_government_representatives: Various Australian federal and state government officials, including politicians, committee members, and regulators. · Government offices and occasional visits to Wittenoom, 1940s-2020s. · APPEARANCE: Predominantly Caucasian, appearing authoritative and formal, reflecting their political or administrative roles.
-  - csr_corporate_personnel: Executives, managers, and other personnel from Colonial Sugar Refining (CSR) and its subsidiary, Australian Blue Asbestos (ABA). · Corporate offices and Wittenoom, 1937-1966. · APPEARANCE: Predominantly Caucasian, appearing well-dressed and corporate, often with an air of authority, sometimes dismissive of worker concerns.
-  - banjima_traditional_owners_and_advocates: Indigenous Banjima people, including elders and legal advocates, asserting their rights over contaminated lands. · Wittenoom area and legal forums, 2010s-2020s. · APPEARANCE: Indigenous Australian people, often older, appearing resilient and determined, some bearing the visible or implied health consequences of asbestos exposure.
-  - australian_airport_police: Law enforcement personnel working in Australian airports. · Australian airport checkpoint, 1985. · APPEARANCE: Predominantly Caucasian, appearing uniformed and professional.
+  - prospectors_mine_owners: Australian prospectors and early mine owners who opened blue asbestos workings in the Hamersley Ranges gorges. · Wittenoom and Yampire gorges, 1937-1943. · APPEARANCE: Australian men of British or Irish descent, fair skin deeply sun-tanned and weathered, short hair, lean wiry build from bush prospecting.
+  - company_managers: Managers and executives of ABA and its parent CSR, a Sydney sugar company with little mining experience, plus town steering committee members. · Wittenoom and corporate offices, 1943-1966. · APPEARANCE: Australian men of British descent, fair complexions, neatly cut and combed hair, office-worker builds.
+  - mine_and_health_officials: Australian state mines inspectors, deputy mining engineers, public health doctors, a health commissioner, health inspectors and an industrial hygienist who reported on the dust. · Wittenoom mine, mill and town and government offices, 1944-1968. · APPEARANCE: Australian men of British descent, fair skin, short neat hair, professional office builds.
+  - mine_and_mill_workers: Asbestos miners, mill hands and fitters: Australian workers, post-war European displaced persons on federal contracts, European recruits from CSR trips, and Spanish migrants. · Wittenoom mines, mill and town, 1937-1966, with a high-turnover workforce throughout. · APPEARANCE: Mixed Australian (British-descended) and Southern, Central and Eastern European men, light to o
+  - spanish_migrant_families: Spanish migrant miners' families from Madrid who came under the Spain-Australia migration agreement, including wives, infants and children, and their later adult children working in media. · Ships via Suez and Wittenoom 1962-1964, Australia until 1971, Madrid from 1966 and 1971, an Australian airport in 1985, and later interviews into the 2020s. · APPEARANCE: Spanish
+  - town_children: Children of miners, including Spanish migrant children, who grew up in the tailings-paved town and played with asbestos. · Wittenoom streets, yards and schoolyard, 1950s-1966. · APPEARANCE: Australian, European and Spanish children with light to olive skin, tanned, tousled hair, dusted with red earth and fine asbestos powder.
+  - union_and_arbitration: Australian Workers' Union representatives, employer advocates and members of the arbitration Board of Reference who negotiated the dust allowance. · Wittenoom mill and arbitration hearings, 1946-1959. · APPEARANCE: Australian men of British descent, fair skin, short neat hair, mixed office and former manual-labour builds.
+  - australian_politicians: Australian prime ministers, state premiers, ministers, parliamentary inquiry leaders and committee chairs dealing with Wittenoom. · Canberra and Perth government and parliament settings, 1947, 1978-1994, 2016-2026. · APPEARANCE: Predominantly Australian men of British descent, fair skin, short groomed hair, middle-aged office builds.
+  - victims_advocates_and_lawyers: Former Wittenoom workers and residents with asbestos disease, the Asbestos Diseases Society of Australia, and the lawyers who litigated against the company and the state. · Perth, courts and offices, 1979-1989 and 2020s-2026. · APPEARANCE: Mixed Australian and European-born adults; ill former workers aged, thin and frail from lung disease.
+  - banjima_traditional_owners: Banjima Aboriginal traditional owners, elders and members of BNTAC whose country includes Wittenoom. · Banjima country around Wittenoom and the Pilbara, 2023-2026. · APPEARANCE: Aboriginal Australian people with dark brown skin, dark curly or wavy hair, elders with grey hair and beards, builds shaped by outdoor life in the Pilbara.
+  - international_un_official: A visiting United Nations special rapporteur investigating toxic contamination. · Australia, meeting Banjima elders, 2023. · APPEARANCE: -
+  - airport_police: Australian airport police officers at a passport and identity checkpoint. · An Australian airport checkpoint, 1985. · APPEARANCE: -
```

**resto**

```diff
--- f50c
+++ f50d
-  materials_textures           : Corrugated iron, wood, asbestos cement, pervasive red earth, blue asbestos waste, fine asbestos dust, loose granular tailings, deposited asbestos fibers, weathered metallic tones, barricade construction materials.
-  color_palette                : Exterior palette dominated by red earth, dusty grey, weathered metallic hues (corrugated iron), and the distinctive blue of asbestos. Interiors typically featured pale, functional colors on walls, often obscured by dust.
-  scale_dimensions             : Extensive desert landscapes, a small town footprint with residential and industrial structures of modest scale (typically one to two stories), large mining waste dumps, and vast areas of ground-level asbestos deposits spreading across 46,840 hectares. Transported asbestos fibers are microscopic but accumulate in large visible deposits.
-  distinctive_features         : An isolated Australian ghost town in the Pilbara desert, visibly constructed with and heavily contaminated by insidious blue asbestos waste from the 1937-1966 mining era. The pervasive red earth and fine, constantly disturbed asbestos dust are omnipresent, defining the toxic and deserted environment.
-  demographics                 : The population consisted primarily of Australian and European migrant workers (including Spanish and displaced persons) from the 1940s-1960s, working as miners and mill workers, along with their families. Children were present, often playing in contaminated areas. Later, Aboriginal Banjima traditional owners became prominent in advocacy regarding the contaminated 
-  condition_evolution.at_event : A remote, functional mining town with active blue asbestos mining and processing operations. Its infrastructure and residential areas were visibly constructed using asbestos tailings, resulting in pervasive dust and rudimentary, functional buildings.
-  condition_evolution.later    : A deserted ghost town characterized by demolished buildings, permanent barricades blocking access to an officially contaminated area of 46,840 hectares, and extensive asbestos contamination spread by wind and water across the landscape.
+  materials_textures           : Worker houses built from corrugated sheet metal, timber and asbestos-cement sheeting; loose, crumbling fibrous asbestos that shreds into fine powder when handled; compacted asbestos tailings laid as the surface of roads, yards, driveways, the schoolyard, public spaces and the airstrip; fine powdery dust coating people, buildings and the mill; loose tailings dumps 
+  color_palette                : Exterior dominated by intense red earth and red dust under harsh desert light, with blue-grey asbestos tailings surfaces and pale grey dust films over buildings and workers; interiors not documented; surviving family imagery described as sepia-toned.
+  scale_dimensions             : A small, isolated outback mining town with a dirt airstrip sized for small propeller aircraft, three mines in the surrounding gorges, more than three million tonnes of tailings left behind, and an official asbestos management area of 46,840 hectares extending down drainage lines toward the Fortescue River.
+  distinctive_features         : A small mining town in the red Pilbara desert whose own roads, yards, schoolyard and airstrip were paved with blue asbestos tailings, so the poison literally formed the ground people walked and played on; today it is an emptied, demolished, unmapped zone sealed by permanent barricades.
+  demographics                 : Documented workforce of Australian miners and mill workers, post-war European displaced persons assigned under federal work contracts (1948-1951), European recruits from private CSR recruitment trips (from 1950), and Spanish migrant families under the Spain-Australia migration agreement (early 1960s), with wives and young children living in town; mill workers dres
+  condition_evolution.at_event : An operating mining town in the early 1960s: inhabited sheet-metal and asbestos-cement houses, a working mill wrapped in thick dust clouds, trucks dumping tailings to surface roads, yards and the schoolyard, children playing on the ground, and small propeller planes landing on the tailings airstrip.
+  condition_evolution.later    : After mining ended in December 1966 the town was progressively reduced from 1978, its school, nursing post and police station closed and buildings demolished from 1986 to 1992, the airport closed in 1993, power cut in 2006, the town formally abolished and erased from maps and signs in 2007, the last residents gone by 2022-2023 and remaining structures demolished, 
-  • role: Doctor/Health Official | age unknown | era: 1948
-    appearance_canon: a middle-aged health official, likely Australian, with a serious demeanor
-  • role: Spanish Migrant Miner | age 26 | era: 1962
-    appearance_canon: a mid-20s Spanish migrant miner, often working long hours in dusty conditions, potentially appearing fatigued
-  • role: Spanish Migrant Resident | age 26 | era: 1962
-    appearance_canon: a mid-20s Spanish migrant woman, resilient in harsh living conditions, possibly showing signs of fatigue from a complicated childbirth
-  • role: Spanish Migrant Resident | age 26 | era: 1962
-    appearance_canon: a mid-20s Spanish migrant woman, forming friendships in a challenging desert environment
-  • role: Spanish Migrant Miner | age 26 | era: 1962
-    appearance_canon: a mid-20s Spanish migrant miner, working excessively long hours in dangerous conditions, likely appearing dust-covered and exhausted
-  • role: Child Resident | age 7 | era: 1962
-    appearance_canon: a child of early elementary school age, playing in a dusty, asbestos-laden environment, potentially appearing oblivious to danger
-  • role: Television Producer / Wittenoom-born | age 22 | era: 1985
-    appearance_canon: an early-20s Spanish-Australian young adult, looking at his documentation while being questioned by an airport police officer
-  • role: Banjima Elder / Activist | age unknown | era: 2023
-    appearance_canon: an elderly Aboriginal Banjima man, bearing the physical toll of asbestos exposure
-  • role: Lawyer | age unknown | era: 1988
-    appearance_canon: a middle-aged lawyer, determined in legal proceedings regarding corporate accountability
-  • role: Daughter of Migrant Miners | age unknown | era: 1971
-    appearance_canon: a young adult of Spanish descent, having lived in Wittenoom as a child, choosing to remain in Australia
-  • role: Infant Resident | age 0 | era: 1963
-    appearance_canon: an infant born in Wittenoom to Spanish migrant parents
-  • role: Public Health Official | age unknown | era: 1965
-    appearance_canon: a middle-aged health official, likely Australian, sternly addressing safety concerns
-  • role: Industrial Hygienist | age unknown | era: 1966
-    appearance_canon: a middle-aged industrial hygienist, meticulously documenting safety deficiencies
-  • role: CSR Chairman | age unknown | era: 1966
-    appearance_canon: an elderly corporate chairman making a public announcement
-  • role: Minister for Lands | age unknown | era: 2019
-    appearance_canon: a middle-aged Aboriginal Australian government minister, addressing environmental remediation responsibilities
-  • role: UN Rapporteur | age unknown | era: 2023
-    appearance_canon: a middle-aged UN rapporteur, conducting interviews related to environmental contamination
-
-OBJETOS DOCUMENTADOS (mantené la FORMA GENERAL constante entre imágenes;
-la narración puede nombrarlos por metáfora, función o material):
-  • objeto: Asbestos tailings
-    forma: Finely crushed rock and blue asbestos fibers, used as construction material or deposited as waste, appearing as loose granular piles or spread over surfaces, easily disturbed to release fine dust.
-  • objeto: Wittenoom's deserted buildings
-    forma: Shabby structures of corrugated iron, wood, and asbestos cement, often appearing neglected or partially demolished, constructed directly with or heavily contaminated by blue asbestos waste.
+  • role: Prospector and mine owner in Wittenoom and Yampire gorges whose interests were taken over by ABA | age unknown | era: 1937-1943
+    appearance_canon: an adult Australian prospector in rugged bush work clothes and wide-brimmed hat, weathered by outdoor work
+  • role: Prospector and mine partner in Wittenoom and Yampire gorges whose interests were taken over by ABA | age unknown | era: 1937-1943
+    appearance_canon: an adult Australian prospector and mine manager in practical bush work clothes, sun-weathered
+  • role: Public health doctor who warned in writing that dust levels were extremely dangerous | age unknown | era: 1948
+    appearance_canon: an adult Australian government medical officer in a lightweight suit and tie with a serious, concerned demeanor
+  • role: Prime Minister of Australia who described the mine's life as practically unlimited | age unknown | era: 1947
+    appearance_canon: a senior Australian statesman in a formal dark suit with a composed public demeanor
+  • role: Public health doctor who reported a mesothelioma case in a former mill worker | age unknown | era: 1962
+    appearance_canon: a middle-aged Australian public health physician in a shirt and tie with a clinical, attentive demeanor
+  • role: Public Health Commissioner who reprimanded the school principal for covering the schoolyard with tailings | age unknown | era: 1965
+    appearance_canon: a middle-aged Australian senior health official in a suit with a stern, authoritative demeanor
+  • role: Industrial hygienist who described spills, leaks and poor machinery modifications | age unknown | era: 1966
+    appearance_canon: a middle-aged Australian industrial hygienist in shirt sleeves and tie, inspecting machinery with a critical eye
+  • role: CSR chairman who announced the closure of the mining operations | age unknown | era: 1966
+    appearance_canon: a middle-aged Australian corporate executive in a dark tailored suit with a formal boardroom demeanor
+  • role: State premier whose government rejected the parliamentary clean-up report | age unknown | era: 1992
+    appearance_canon: a middle-aged Australian state politician in a dark business suit with a guarded official demeanor
+  • role: Lawyer who obtained the 1988 Wittenoom verdict against the company | age unknown | era: 1988
+    appearance_canon: an adult Australian litigation lawyer in a business suit with a determined courtroom demeanor
+  • role: State minister who argued the responsible companies should pay for remediation | age unknown | era: 2019
+    appearance_canon: a middle-aged Australian state government minister in a modern business suit
+  • role: UN special rapporteur who visited Australia and interviewed a Banjima elder about the contamination | age unknown | era: 2023
+    appearance_canon: a middle-aged international UN human rights expert in modern business attire with an attentive, listening demeanor
+  • role: Banjima elder and activist who spoke about persistent harm and died of mesothelioma | age unknown | era: 2023-2024
+    appearance_canon: an elderly Aboriginal Australian Banjima elder in casual outback clothing with a dignified, weary bearing
+  • role: CEO of the Asbestos Diseases Society of Australia estimating deaths may exceed 4,000 | age unknown | era: 2020s
+    appearance_canon: a middle-aged Australian woman advocate in modern professional attire with an earnest demeanor
+  • role: Spanish migrant miner in Wittenoom, injured in the foot, later died of mesothelioma | age unknown | era: 1962-1963
+    appearance_canon: a young adult Spanish migrant miner in dusty work clothes, in one portrait with a bandaged foot
+  • role: Wife of a Spanish miner and Wittenoom resident who gave birth in the town hospital | age unknown | era: 1962-1963
+    appearance_canon: a young adult Spanish woman in a simple cotton dress, physically weakened after a difficult birth, hopeful but strained
+  • role: Son of a Spanish miner, born in Wittenoom, later a television producer | age unknown | era: 1963-1985
+    appearance_canon: a young adult man of Spanish descent born in Australia, in casual travel clothes at an airport checkpoint
+  • role: Wife of a Spanish miner and Wittenoom resident who gave birth in the town | age unknown | era: 1962-1964
+    appearance_canon: a young adult Spanish mother in a modest cotton dress, caring for small children in the heat and dust
+  • role: Spanish migrant miner in Wittenoom who often worked 16-hour shifts | age unknown | era: 1962-1964
+    appearance_canon: an adult Spanish migrant miner in dust-covered work shirt and trousers, visibly exhausted from long shifts
+  • role: Child of the De Juan-Barroso family who lived in Wittenoom and later recalled it | age unknown | era: 1962-1964
+    appearance_canon: a young Spanish boy in shorts and a cotton shirt, red dust on skin and clothes
+  • role: Son of a Spanish miner born in Wittenoom | age unknown | era: 1963
+    appearance_canon: a newborn infant of Spanish parents wrapped in a light cotton blanket
+  • role: Daughter of a Spanish miner who lived in Wittenoom as a child and remained in Australia | age unknown | era: 1962-1971
+    appearance_canon: a young Spanish girl in a simple cotton frock with dust on her sandals
+
+OBJETOS DOCUMENTADOS: (vacío) — describí cualquier objeto que nombre la narración por su forma física según el relato, sin inventar detalles no dichos.
-  - contemporary clothing (post-2000s)
-  - modern cars (post-1970s)
-  - digital cameras
-  - modern industrial safety equipment (e.g., advanced respirators)
-  - satellite dishes
-  - GPS devices
-  - modern communication technology
+  - contemporary clothing
+  - modern industrial safety equipment in mining-era scenes
+  - hazmat suits and modern respirators before the 1980s
+  - hi-visibility vests
+  - sealed bitumen roads with painted lines
+  - modern SUVs and pickup trucks in mining-era scenes
+  - jet aircraft at the town airstrip
+  - plastic asbestos-hazard warning signs before closure
+  - solar panels and satellite dishes
```


## ch02

### código solo (canon de antes): diff crudo contra F50c

```diff
-  - wittenoom_miners_and_mill_workers: Various European migrant and Australian laborers working in the asbestos mines and processing mill. · Wittenoom, from 1937 to 1966. · APPEARANCE: Physically robust individuals, often appearing fatigued and covered in a pervasive fine dust, with diverse European features. · CLOTHING: Rugged, practical work clothes, heavy-duty trousers and shirts, sometimes wi
-  - spanish_migrant_families: Spanish families who migrated to Wittenoom under government schemes. · Wittenoom, primarily 1958-1966. · APPEARANCE: Adults and children of Southern European descent, appearing resilient and resourceful, adapting to a harsh desert environment, often showing signs of physical strain or everyday weariness. · CLOTHING: Simple, light clothing suitable for a hot, dusty cl
-  - australian_public_health_officials: Doctors, inspectors, and hygienists from Australian public health departments. · Wittenoom and state offices, 1944-1966. · APPEARANCE: Predominantly Caucasian, appearing professional, often with a serious or concerned demeanor due to the health risks. · CLOTHING: Formal or semi-formal attire of the era, such as suits, collared shirts, and ties, or clean uni
-  - australian_government_representatives: Various Australian federal and state government officials, including politicians, committee members, and regulators. · Government offices and occasional visits to Wittenoom, 1940s-2020s. · APPEARANCE: Predominantly Caucasian, appearing authoritative and formal, reflecting their political or administrative roles. · CLOTHING: Formal business attire, includ
-  - csr_corporate_personnel: Executives, managers, and other personnel from Colonial Sugar Refining (CSR) and its subsidiary, Australian Blue Asbestos (ABA). · Corporate offices and Wittenoom, 1937-1966. · APPEARANCE: Predominantly Caucasian, appearing well-dressed and corporate, often with an air of authority, sometimes dismissive of worker concerns. · CLOTHING: Business suits and formal wear, r
-  - banjima_traditional_owners_and_advocates: Indigenous Banjima people, including elders and legal advocates, asserting their rights over contaminated lands. · Wittenoom area and legal forums, 2010s-2020s. · APPEARANCE: Indigenous Australian people, often older, appearing resilient and determined, some bearing the visible or implied health consequences of asbestos exposure. · CLOTHING: Practical
-  - australian_airport_police: Law enforcement personnel working in Australian airports. · Australian airport checkpoint, 1985. · APPEARANCE: Predominantly Caucasian, appearing uniformed and professional. · CLOTHING: Standard police uniform of the mid-1980s, typically including a collared shirt, trousers, and a peaked cap.
+  - wittenoom_miners_and_mill_workers: Various European migrant and Australian laborers working in the asbestos mines and processing mill. · Wittenoom, from 1937 to 1966. · APPEARANCE: Physically robust individuals, often appearing fatigued and covered in a pervasive fine dust, with diverse European features. · CLOTHING: -
+  - spanish_migrant_families: Spanish families who migrated to Wittenoom under government schemes. · Wittenoom, primarily 1958-1966. · APPEARANCE: Adults and children of Southern European descent, appearing resilient and resourceful, adapting to a harsh desert environment, often showing signs of physical strain or everyday weariness. · CLOTHING: -
+  - australian_public_health_officials: Doctors, inspectors, and hygienists from Australian public health departments. · Wittenoom and state offices, 1944-1966. · APPEARANCE: Predominantly Caucasian, appearing professional, often with a serious or concerned demeanor due to the health risks. · CLOTHING: -
+  - australian_government_representatives: Various Australian federal and state government officials, including politicians, committee members, and regulators. · Government offices and occasional visits to Wittenoom, 1940s-2020s. · APPEARANCE: Predominantly Caucasian, appearing authoritative and formal, reflecting their political or administrative roles. · CLOTHING: -
+  - csr_corporate_personnel: Executives, managers, and other personnel from Colonial Sugar Refining (CSR) and its subsidiary, Australian Blue Asbestos (ABA). · Corporate offices and Wittenoom, 1937-1966. · APPEARANCE: Predominantly Caucasian, appearing well-dressed and corporate, often with an air of authority, sometimes dismissive of worker concerns. · CLOTHING: -
+  - banjima_traditional_owners_and_advocates: Indigenous Banjima people, including elders and legal advocates, asserting their rights over contaminated lands. · Wittenoom area and legal forums, 2010s-2020s. · APPEARANCE: Indigenous Australian people, often older, appearing resilient and determined, some bearing the visible or implied health consequences of asbestos exposure. · CLOTHING: -
+  - australian_airport_police: Law enforcement personnel working in Australian airports. · Australian airport checkpoint, 1985. · APPEARANCE: Predominantly Caucasian, appearing uniformed and professional. · CLOTHING: -
```

### canon nuevo: diff por zona

**era**

```diff
--- f50c
+++ f50d
-  clothing              : Miners wore rugged work clothes, often appearing dirty and dusty. Town residents wore practical, light attire suitable for hot desert conditions, including simple dresses, shirts, and shorts. Government and corporate officials wore more formal attire, such as suits, appropriate for their roles and the era.
-  technology            : Analog gauges, basic mining machinery with exposed components, rudimentary processing plants, simple residential appliances (e.g., older refrigerators, stoves), landline telephones, and radios. NO LEDs, NO digital displays, NO smartphones, NO advanced computing devices.
-  vehicles_machinery    : Early to mid-20th century trucks (e.g., for asbestos transport), desert-adapted 4x4 vehicles, passenger cars from the 1940s-1960s. Propeller-driven small aircraft for transport to the remote town. Mining equipment included drills, crushers, and conveyor belt systems.
-  interiors             : Residential interiors were basic and utilitarian, often in houses of corrugated iron, wood, and asbestos cement, prone to dust accumulation. Offices featured simple desks, manual typewriters, and basic filing systems. Public buildings like hospitals had functional, unadorned spaces with period-appropriate medical equipment.
-  forbidden_anachronisms: smartphones, LED screens, contemporary clothing (post-2000s), modern flat panels, modern cars (post-1970s), digital cameras, modern industrial safety equipment (e.g., advanced respirators), satellite dishes, renewable energy installations.
+  period 1946-1966:
+  clothing              : Dust-covered miners and mill hands in work shirts, shorts or trousers and boots; migrant families in modest European clothing adapted to heat; officials and doctors in lightweight suits or short sleeves with ties.
+  technology            : Full-scale crushing mill with conveyors, fans and later dust-reducing equipment, valve radios, telephones, typewriters, film cameras producing sepia and black-and-white family photos.
+  vehicles_machinery    : Ore and tipper trucks spreading tailings on roads and yards, small propeller aircraft on the tailings-surfaced airstrip, mid-century sedans and bush vehicles, ocean liners carrying migrants.
+  interiors             : Sheet-metal, timber and asbestos-cement houses, town hospital, school with tailings-covered yard, churches and community buildings, dusty mill interior.
+  forbidden_anachronisms: In mining-era scenes: no modern respirators, hazmat suits, hi-visibility vests or hard hats with modern logos; no sealed bitumen roads with painted lines; no modern four-wheel drives, SUVs or pickup trucks; no jet aircraft at the airstrip; no plastic warning signs or asbestos-hazard pictograms; no mobile phones, digital cameras, computers or LED lighting; no solar panels
```

**grupo**

```diff
--- f50c
+++ f50d
-  - wittenoom_miners_and_mill_workers: Various European migrant and Australian laborers working in the asbestos mines and processing mill. · Wittenoom, from 1937 to 1966. · APPEARANCE: Physically robust individuals, often appearing fatigued and covered in a pervasive fine dust, with diverse European features.
-  - spanish_migrant_families: Spanish families who migrated to Wittenoom under government schemes. · Wittenoom, primarily 1958-1966. · APPEARANCE: Adults and children of Southern European descent, appearing resilient and resourceful, adapting to a harsh desert environment, often showing signs of physical strain or everyday weariness.
-  - australian_public_health_officials: Doctors, inspectors, and hygienists from Australian public health departments. · Wittenoom and state offices, 1944-1966. · APPEARANCE: Predominantly Caucasian, appearing professional, often with a serious or concerned demeanor due to the health risks.
-  - australian_government_representatives: Various Australian federal and state government officials, including politicians, committee members, and regulators. · Government offices and occasional visits to Wittenoom, 1940s-2020s. · APPEARANCE: Predominantly Caucasian, appearing authoritative and formal, reflecting their political or administrative roles.
-  - csr_corporate_personnel: Executives, managers, and other personnel from Colonial Sugar Refining (CSR) and its subsidiary, Australian Blue Asbestos (ABA). · Corporate offices and Wittenoom, 1937-1966. · APPEARANCE: Predominantly Caucasian, appearing well-dressed and corporate, often with an air of authority, sometimes dismissive of worker concerns.
-  - banjima_traditional_owners_and_advocates: Indigenous Banjima people, including elders and legal advocates, asserting their rights over contaminated lands. · Wittenoom area and legal forums, 2010s-2020s. · APPEARANCE: Indigenous Australian people, often older, appearing resilient and determined, some bearing the visible or implied health consequences of asbestos exposure.
-  - australian_airport_police: Law enforcement personnel working in Australian airports. · Australian airport checkpoint, 1985. · APPEARANCE: Predominantly Caucasian, appearing uniformed and professional.
+  - prospectors_mine_owners: Australian prospectors and early mine owners who opened blue asbestos workings in the Hamersley Ranges gorges. · Wittenoom and Yampire gorges, 1937-1943. · APPEARANCE: Australian men of British or Irish descent, fair skin deeply sun-tanned and weathered, short hair, lean wiry build from bush prospecting.
+  - company_managers: Managers and executives of ABA and its parent CSR, a Sydney sugar company with little mining experience, plus town steering committee members. · Wittenoom and corporate offices, 1943-1966. · APPEARANCE: Australian men of British descent, fair complexions, neatly cut and combed hair, office-worker builds.
+  - mine_and_health_officials: Australian state mines inspectors, deputy mining engineers, public health doctors, a health commissioner, health inspectors and an industrial hygienist who reported on the dust. · Wittenoom mine, mill and town and government offices, 1944-1968. · APPEARANCE: Australian men of British descent, fair skin, short neat hair, professional office builds.
+  - mine_and_mill_workers: Asbestos miners, mill hands and fitters: Australian workers, post-war European displaced persons on federal contracts, European recruits from CSR trips, and Spanish migrants. · Wittenoom mines, mill and town, 1937-1966, with a high-turnover workforce throughout. · APPEARANCE: Mixed Australian (British-descended) and Southern, Central and Eastern European men, light to o
+  - spanish_migrant_families: Spanish migrant miners' families from Madrid who came under the Spain-Australia migration agreement, including wives, infants and children, and their later adult children working in media. · Ships via Suez and Wittenoom 1962-1964, Australia until 1971, Madrid from 1966 and 1971, an Australian airport in 1985, and later interviews into the 2020s. · APPEARANCE: Spanish
+  - town_children: Children of miners, including Spanish migrant children, who grew up in the tailings-paved town and played with asbestos. · Wittenoom streets, yards and schoolyard, 1950s-1966. · APPEARANCE: Australian, European and Spanish children with light to olive skin, tanned, tousled hair, dusted with red earth and fine asbestos powder.
+  - union_and_arbitration: Australian Workers' Union representatives, employer advocates and members of the arbitration Board of Reference who negotiated the dust allowance. · Wittenoom mill and arbitration hearings, 1946-1959. · APPEARANCE: Australian men of British descent, fair skin, short neat hair, mixed office and former manual-labour builds.
+  - australian_politicians: Australian prime ministers, state premiers, ministers, parliamentary inquiry leaders and committee chairs dealing with Wittenoom. · Canberra and Perth government and parliament settings, 1947, 1978-1994, 2016-2026. · APPEARANCE: Predominantly Australian men of British descent, fair skin, short groomed hair, middle-aged office builds.
+  - victims_advocates_and_lawyers: Former Wittenoom workers and residents with asbestos disease, the Asbestos Diseases Society of Australia, and the lawyers who litigated against the company and the state. · Perth, courts and offices, 1979-1989 and 2020s-2026. · APPEARANCE: Mixed Australian and European-born adults; ill former workers aged, thin and frail from lung disease.
+  - banjima_traditional_owners: Banjima Aboriginal traditional owners, elders and members of BNTAC whose country includes Wittenoom. · Banjima country around Wittenoom and the Pilbara, 2023-2026. · APPEARANCE: Aboriginal Australian people with dark brown skin, dark curly or wavy hair, elders with grey hair and beards, builds shaped by outdoor life in the Pilbara.
+  - international_un_official: A visiting United Nations special rapporteur investigating toxic contamination. · Australia, meeting Banjima elders, 2023. · APPEARANCE: -
+  - airport_police: Australian airport police officers at a passport and identity checkpoint. · An Australian airport checkpoint, 1985. · APPEARANCE: -
```

**resto**

```diff
--- f50c
+++ f50d
-  materials_textures           : Corrugated iron, wood, asbestos cement, pervasive red earth, blue asbestos waste, fine asbestos dust, loose granular tailings, deposited asbestos fibers, weathered metallic tones, barricade construction materials.
-  color_palette                : Exterior palette dominated by red earth, dusty grey, weathered metallic hues (corrugated iron), and the distinctive blue of asbestos. Interiors typically featured pale, functional colors on walls, often obscured by dust.
-  scale_dimensions             : Extensive desert landscapes, a small town footprint with residential and industrial structures of modest scale (typically one to two stories), large mining waste dumps, and vast areas of ground-level asbestos deposits spreading across 46,840 hectares. Transported asbestos fibers are microscopic but accumulate in large visible deposits.
-  distinctive_features         : An isolated Australian ghost town in the Pilbara desert, visibly constructed with and heavily contaminated by insidious blue asbestos waste from the 1937-1966 mining era. The pervasive red earth and fine, constantly disturbed asbestos dust are omnipresent, defining the toxic and deserted environment.
-  demographics                 : The population consisted primarily of Australian and European migrant workers (including Spanish and displaced persons) from the 1940s-1960s, working as miners and mill workers, along with their families. Children were present, often playing in contaminated areas. Later, Aboriginal Banjima traditional owners became prominent in advocacy regarding the contaminated 
-  condition_evolution.at_event : A remote, functional mining town with active blue asbestos mining and processing operations. Its infrastructure and residential areas were visibly constructed using asbestos tailings, resulting in pervasive dust and rudimentary, functional buildings.
-  condition_evolution.later    : A deserted ghost town characterized by demolished buildings, permanent barricades blocking access to an officially contaminated area of 46,840 hectares, and extensive asbestos contamination spread by wind and water across the landscape.
+  materials_textures           : Worker houses built from corrugated sheet metal, timber and asbestos-cement sheeting; loose, crumbling fibrous asbestos that shreds into fine powder when handled; compacted asbestos tailings laid as the surface of roads, yards, driveways, the schoolyard, public spaces and the airstrip; fine powdery dust coating people, buildings and the mill; loose tailings dumps 
+  color_palette                : Exterior dominated by intense red earth and red dust under harsh desert light, with blue-grey asbestos tailings surfaces and pale grey dust films over buildings and workers; interiors not documented; surviving family imagery described as sepia-toned.
+  scale_dimensions             : A small, isolated outback mining town with a dirt airstrip sized for small propeller aircraft, three mines in the surrounding gorges, more than three million tonnes of tailings left behind, and an official asbestos management area of 46,840 hectares extending down drainage lines toward the Fortescue River.
+  distinctive_features         : A small mining town in the red Pilbara desert whose own roads, yards, schoolyard and airstrip were paved with blue asbestos tailings, so the poison literally formed the ground people walked and played on; today it is an emptied, demolished, unmapped zone sealed by permanent barricades.
+  demographics                 : Documented workforce of Australian miners and mill workers, post-war European displaced persons assigned under federal work contracts (1948-1951), European recruits from private CSR recruitment trips (from 1950), and Spanish migrant families under the Spain-Australia migration agreement (early 1960s), with wives and young children living in town; mill workers dres
+  condition_evolution.at_event : An operating mining town in the early 1960s: inhabited sheet-metal and asbestos-cement houses, a working mill wrapped in thick dust clouds, trucks dumping tailings to surface roads, yards and the schoolyard, children playing on the ground, and small propeller planes landing on the tailings airstrip.
+  condition_evolution.later    : After mining ended in December 1966 the town was progressively reduced from 1978, its school, nursing post and police station closed and buildings demolished from 1986 to 1992, the airport closed in 1993, power cut in 2006, the town formally abolished and erased from maps and signs in 2007, the last residents gone by 2022-2023 and remaining structures demolished, 
-  • role: Doctor/Health Official | age unknown | era: 1948
-    appearance_canon: a middle-aged health official, likely Australian, with a serious demeanor
-  • role: Spanish Migrant Miner | age 26 | era: 1962
-    appearance_canon: a mid-20s Spanish migrant miner, often working long hours in dusty conditions, potentially appearing fatigued
-  • role: Spanish Migrant Resident | age 26 | era: 1962
-    appearance_canon: a mid-20s Spanish migrant woman, resilient in harsh living conditions, possibly showing signs of fatigue from a complicated childbirth
-  • role: Spanish Migrant Resident | age 26 | era: 1962
-    appearance_canon: a mid-20s Spanish migrant woman, forming friendships in a challenging desert environment
-  • role: Spanish Migrant Miner | age 26 | era: 1962
-    appearance_canon: a mid-20s Spanish migrant miner, working excessively long hours in dangerous conditions, likely appearing dust-covered and exhausted
-  • role: Child Resident | age 7 | era: 1962
-    appearance_canon: a child of early elementary school age, playing in a dusty, asbestos-laden environment, potentially appearing oblivious to danger
-  • role: Television Producer / Wittenoom-born | age 22 | era: 1985
-    appearance_canon: an early-20s Spanish-Australian young adult, looking at his documentation while being questioned by an airport police officer
-  • role: Banjima Elder / Activist | age unknown | era: 2023
-    appearance_canon: an elderly Aboriginal Banjima man, bearing the physical toll of asbestos exposure
-  • role: Lawyer | age unknown | era: 1988
-    appearance_canon: a middle-aged lawyer, determined in legal proceedings regarding corporate accountability
-  • role: Daughter of Migrant Miners | age unknown | era: 1971
-    appearance_canon: a young adult of Spanish descent, having lived in Wittenoom as a child, choosing to remain in Australia
-  • role: Infant Resident | age 0 | era: 1963
-    appearance_canon: an infant born in Wittenoom to Spanish migrant parents
-  • role: Public Health Official | age unknown | era: 1965
-    appearance_canon: a middle-aged health official, likely Australian, sternly addressing safety concerns
-  • role: Industrial Hygienist | age unknown | era: 1966
-    appearance_canon: a middle-aged industrial hygienist, meticulously documenting safety deficiencies
-  • role: CSR Chairman | age unknown | era: 1966
-    appearance_canon: an elderly corporate chairman making a public announcement
-  • role: Minister for Lands | age unknown | era: 2019
-    appearance_canon: a middle-aged Aboriginal Australian government minister, addressing environmental remediation responsibilities
-  • role: UN Rapporteur | age unknown | era: 2023
-    appearance_canon: a middle-aged UN rapporteur, conducting interviews related to environmental contamination
-
-OBJETOS DOCUMENTADOS (mantené la FORMA GENERAL constante entre imágenes;
-la narración puede nombrarlos por metáfora, función o material):
-  • objeto: Asbestos tailings
-    forma: Finely crushed rock and blue asbestos fibers, used as construction material or deposited as waste, appearing as loose granular piles or spread over surfaces, easily disturbed to release fine dust.
-  • objeto: Wittenoom's deserted buildings
-    forma: Shabby structures of corrugated iron, wood, and asbestos cement, often appearing neglected or partially demolished, constructed directly with or heavily contaminated by blue asbestos waste.
+  • role: Prospector and mine owner in Wittenoom and Yampire gorges whose interests were taken over by ABA | age unknown | era: 1937-1943
+    appearance_canon: an adult Australian prospector in rugged bush work clothes and wide-brimmed hat, weathered by outdoor work
+  • role: Prospector and mine partner in Wittenoom and Yampire gorges whose interests were taken over by ABA | age unknown | era: 1937-1943
+    appearance_canon: an adult Australian prospector and mine manager in practical bush work clothes, sun-weathered
+  • role: Public health doctor who warned in writing that dust levels were extremely dangerous | age unknown | era: 1948
+    appearance_canon: an adult Australian government medical officer in a lightweight suit and tie with a serious, concerned demeanor
+  • role: Prime Minister of Australia who described the mine's life as practically unlimited | age unknown | era: 1947
+    appearance_canon: a senior Australian statesman in a formal dark suit with a composed public demeanor
+  • role: Public health doctor who reported a mesothelioma case in a former mill worker | age unknown | era: 1962
+    appearance_canon: a middle-aged Australian public health physician in a shirt and tie with a clinical, attentive demeanor
+  • role: Public Health Commissioner who reprimanded the school principal for covering the schoolyard with tailings | age unknown | era: 1965
+    appearance_canon: a middle-aged Australian senior health official in a suit with a stern, authoritative demeanor
+  • role: Industrial hygienist who described spills, leaks and poor machinery modifications | age unknown | era: 1966
+    appearance_canon: a middle-aged Australian industrial hygienist in shirt sleeves and tie, inspecting machinery with a critical eye
+  • role: CSR chairman who announced the closure of the mining operations | age unknown | era: 1966
+    appearance_canon: a middle-aged Australian corporate executive in a dark tailored suit with a formal boardroom demeanor
+  • role: State premier whose government rejected the parliamentary clean-up report | age unknown | era: 1992
+    appearance_canon: a middle-aged Australian state politician in a dark business suit with a guarded official demeanor
+  • role: Lawyer who obtained the 1988 Wittenoom verdict against the company | age unknown | era: 1988
+    appearance_canon: an adult Australian litigation lawyer in a business suit with a determined courtroom demeanor
+  • role: State minister who argued the responsible companies should pay for remediation | age unknown | era: 2019
+    appearance_canon: a middle-aged Australian state government minister in a modern business suit
+  • role: UN special rapporteur who visited Australia and interviewed a Banjima elder about the contamination | age unknown | era: 2023
+    appearance_canon: a middle-aged international UN human rights expert in modern business attire with an attentive, listening demeanor
+  • role: Banjima elder and activist who spoke about persistent harm and died of mesothelioma | age unknown | era: 2023-2024
+    appearance_canon: an elderly Aboriginal Australian Banjima elder in casual outback clothing with a dignified, weary bearing
+  • role: CEO of the Asbestos Diseases Society of Australia estimating deaths may exceed 4,000 | age unknown | era: 2020s
+    appearance_canon: a middle-aged Australian woman advocate in modern professional attire with an earnest demeanor
+  • role: Spanish migrant miner in Wittenoom, injured in the foot, later died of mesothelioma | age unknown | era: 1962-1963
+    appearance_canon: a young adult Spanish migrant miner in dusty work clothes, in one portrait with a bandaged foot
+  • role: Wife of a Spanish miner and Wittenoom resident who gave birth in the town hospital | age unknown | era: 1962-1963
+    appearance_canon: a young adult Spanish woman in a simple cotton dress, physically weakened after a difficult birth, hopeful but strained
+  • role: Son of a Spanish miner, born in Wittenoom, later a television producer | age unknown | era: 1963-1985
+    appearance_canon: a young adult man of Spanish descent born in Australia, in casual travel clothes at an airport checkpoint
+  • role: Wife of a Spanish miner and Wittenoom resident who gave birth in the town | age unknown | era: 1962-1964
+    appearance_canon: a young adult Spanish mother in a modest cotton dress, caring for small children in the heat and dust
+  • role: Spanish migrant miner in Wittenoom who often worked 16-hour shifts | age unknown | era: 1962-1964
+    appearance_canon: an adult Spanish migrant miner in dust-covered work shirt and trousers, visibly exhausted from long shifts
+  • role: Child of the De Juan-Barroso family who lived in Wittenoom and later recalled it | age unknown | era: 1962-1964
+    appearance_canon: a young Spanish boy in shorts and a cotton shirt, red dust on skin and clothes
+  • role: Son of a Spanish miner born in Wittenoom | age unknown | era: 1963
+    appearance_canon: a newborn infant of Spanish parents wrapped in a light cotton blanket
+  • role: Daughter of a Spanish miner who lived in Wittenoom as a child and remained in Australia | age unknown | era: 1962-1971
+    appearance_canon: a young Spanish girl in a simple cotton frock with dust on her sandals
+
+OBJETOS DOCUMENTADOS: (vacío) — describí cualquier objeto que nombre la narración por su forma física según el relato, sin inventar detalles no dichos.
-  - contemporary clothing (post-2000s)
-  - modern cars (post-1970s)
-  - digital cameras
-  - modern industrial safety equipment (e.g., advanced respirators)
-  - satellite dishes
-  - GPS devices
-  - modern communication technology
+  - contemporary clothing
+  - modern industrial safety equipment in mining-era scenes
+  - hazmat suits and modern respirators before the 1980s
+  - hi-visibility vests
+  - sealed bitumen roads with painted lines
+  - modern SUVs and pickup trucks in mining-era scenes
+  - jet aircraft at the town airstrip
+  - plastic asbestos-hazard warning signs before closure
+  - solar panels and satellite dishes
```


## ch03

### código solo (canon de antes): diff crudo contra F50c

```diff
-  - wittenoom_miners_and_mill_workers: Various European migrant and Australian laborers working in the asbestos mines and processing mill. · Wittenoom, from 1937 to 1966. · APPEARANCE: Physically robust individuals, often appearing fatigued and covered in a pervasive fine dust, with diverse European features. · CLOTHING: Rugged, practical work clothes, heavy-duty trousers and shirts, sometimes wi
-  - spanish_migrant_families: Spanish families who migrated to Wittenoom under government schemes. · Wittenoom, primarily 1958-1966. · APPEARANCE: Adults and children of Southern European descent, appearing resilient and resourceful, adapting to a harsh desert environment, often showing signs of physical strain or everyday weariness. · CLOTHING: Simple, light clothing suitable for a hot, dusty cl
-  - australian_public_health_officials: Doctors, inspectors, and hygienists from Australian public health departments. · Wittenoom and state offices, 1944-1966. · APPEARANCE: Predominantly Caucasian, appearing professional, often with a serious or concerned demeanor due to the health risks. · CLOTHING: Formal or semi-formal attire of the era, such as suits, collared shirts, and ties, or clean uni
-  - australian_government_representatives: Various Australian federal and state government officials, including politicians, committee members, and regulators. · Government offices and occasional visits to Wittenoom, 1940s-2020s. · APPEARANCE: Predominantly Caucasian, appearing authoritative and formal, reflecting their political or administrative roles. · CLOTHING: Formal business attire, includ
-  - csr_corporate_personnel: Executives, managers, and other personnel from Colonial Sugar Refining (CSR) and its subsidiary, Australian Blue Asbestos (ABA). · Corporate offices and Wittenoom, 1937-1966. · APPEARANCE: Predominantly Caucasian, appearing well-dressed and corporate, often with an air of authority, sometimes dismissive of worker concerns. · CLOTHING: Business suits and formal wear, r
-  - banjima_traditional_owners_and_advocates: Indigenous Banjima people, including elders and legal advocates, asserting their rights over contaminated lands. · Wittenoom area and legal forums, 2010s-2020s. · APPEARANCE: Indigenous Australian people, often older, appearing resilient and determined, some bearing the visible or implied health consequences of asbestos exposure. · CLOTHING: Practical
-  - australian_airport_police: Law enforcement personnel working in Australian airports. · Australian airport checkpoint, 1985. · APPEARANCE: Predominantly Caucasian, appearing uniformed and professional. · CLOTHING: Standard police uniform of the mid-1980s, typically including a collared shirt, trousers, and a peaked cap.
+  - wittenoom_miners_and_mill_workers: Various European migrant and Australian laborers working in the asbestos mines and processing mill. · Wittenoom, from 1937 to 1966. · APPEARANCE: Physically robust individuals, often appearing fatigued and covered in a pervasive fine dust, with diverse European features. · CLOTHING: -
+  - spanish_migrant_families: Spanish families who migrated to Wittenoom under government schemes. · Wittenoom, primarily 1958-1966. · APPEARANCE: Adults and children of Southern European descent, appearing resilient and resourceful, adapting to a harsh desert environment, often showing signs of physical strain or everyday weariness. · CLOTHING: -
+  - australian_public_health_officials: Doctors, inspectors, and hygienists from Australian public health departments. · Wittenoom and state offices, 1944-1966. · APPEARANCE: Predominantly Caucasian, appearing professional, often with a serious or concerned demeanor due to the health risks. · CLOTHING: -
+  - australian_government_representatives: Various Australian federal and state government officials, including politicians, committee members, and regulators. · Government offices and occasional visits to Wittenoom, 1940s-2020s. · APPEARANCE: Predominantly Caucasian, appearing authoritative and formal, reflecting their political or administrative roles. · CLOTHING: -
+  - csr_corporate_personnel: Executives, managers, and other personnel from Colonial Sugar Refining (CSR) and its subsidiary, Australian Blue Asbestos (ABA). · Corporate offices and Wittenoom, 1937-1966. · APPEARANCE: Predominantly Caucasian, appearing well-dressed and corporate, often with an air of authority, sometimes dismissive of worker concerns. · CLOTHING: -
+  - banjima_traditional_owners_and_advocates: Indigenous Banjima people, including elders and legal advocates, asserting their rights over contaminated lands. · Wittenoom area and legal forums, 2010s-2020s. · APPEARANCE: Indigenous Australian people, often older, appearing resilient and determined, some bearing the visible or implied health consequences of asbestos exposure. · CLOTHING: -
+  - australian_airport_police: Law enforcement personnel working in Australian airports. · Australian airport checkpoint, 1985. · APPEARANCE: Predominantly Caucasian, appearing uniformed and professional. · CLOTHING: -
```

### canon nuevo: diff por zona

**era**

```diff
--- f50c
+++ f50d
-  clothing              : Miners wore rugged work clothes, often appearing dirty and dusty. Town residents wore practical, light attire suitable for hot desert conditions, including simple dresses, shirts, and shorts. Government and corporate officials wore more formal attire, such as suits, appropriate for their roles and the era.
-  technology            : Analog gauges, basic mining machinery with exposed components, rudimentary processing plants, simple residential appliances (e.g., older refrigerators, stoves), landline telephones, and radios. NO LEDs, NO digital displays, NO smartphones, NO advanced computing devices.
-  vehicles_machinery    : Early to mid-20th century trucks (e.g., for asbestos transport), desert-adapted 4x4 vehicles, passenger cars from the 1940s-1960s. Propeller-driven small aircraft for transport to the remote town. Mining equipment included drills, crushers, and conveyor belt systems.
-  interiors             : Residential interiors were basic and utilitarian, often in houses of corrugated iron, wood, and asbestos cement, prone to dust accumulation. Offices featured simple desks, manual typewriters, and basic filing systems. Public buildings like hospitals had functional, unadorned spaces with period-appropriate medical equipment.
-  forbidden_anachronisms: smartphones, LED screens, contemporary clothing (post-2000s), modern flat panels, modern cars (post-1970s), digital cameras, modern industrial safety equipment (e.g., advanced respirators), satellite dishes, renewable energy installations.
+  period 1937-1945:
+  clothing              : Rough bush work clothes for prospectors and early miners: cotton shirts, braces, wide-brimmed felt hats, heavy boots; officials in wartime-austere suits and hats.
+  technology            : Small-scale hand and early mechanical asbestos extraction, basic crushing, valve radios, typewriters, paper inspection reports; no dust control beyond rudimentary measures.
+  vehicles_machinery    : Early mid-century trucks and utility vehicles on unsealed tracks, simple mine headings in gorge walls, horse-drawn or truck-hauled loads.
+  interiors             : Rough camps, tents and basic sheet-metal huts; spartan government offices.
+  period 1946-1966:
+  clothing              : Dust-covered miners and mill hands in work shirts, shorts or trousers and boots; migrant families in modest European clothing adapted to heat; officials and doctors in lightweight suits or short sleeves with ties.
+  technology            : Full-scale crushing mill with conveyors, fans and later dust-reducing equipment, valve radios, telephones, typewriters, film cameras producing sepia and black-and-white family photos.
+  vehicles_machinery    : Ore and tipper trucks spreading tailings on roads and yards, small propeller aircraft on the tailings-surfaced airstrip, mid-century sedans and bush vehicles, ocean liners carrying migrants.
+  interiors             : Sheet-metal, timber and asbestos-cement houses, town hospital, school with tailings-covered yard, churches and community buildings, dusty mill interior.
+  forbidden_anachronisms: In mining-era scenes: no modern respirators, hazmat suits, hi-visibility vests or hard hats with modern logos; no sealed bitumen roads with painted lines; no modern four-wheel drives, SUVs or pickup trucks; no jet aircraft at the airstrip; no plastic warning signs or asbestos-hazard pictograms; no mobile phones, digital cameras, computers or LED lighting; no solar panels
```

**grupo**

```diff
--- f50c
+++ f50d
-  - wittenoom_miners_and_mill_workers: Various European migrant and Australian laborers working in the asbestos mines and processing mill. · Wittenoom, from 1937 to 1966. · APPEARANCE: Physically robust individuals, often appearing fatigued and covered in a pervasive fine dust, with diverse European features.
-  - spanish_migrant_families: Spanish families who migrated to Wittenoom under government schemes. · Wittenoom, primarily 1958-1966. · APPEARANCE: Adults and children of Southern European descent, appearing resilient and resourceful, adapting to a harsh desert environment, often showing signs of physical strain or everyday weariness.
-  - australian_public_health_officials: Doctors, inspectors, and hygienists from Australian public health departments. · Wittenoom and state offices, 1944-1966. · APPEARANCE: Predominantly Caucasian, appearing professional, often with a serious or concerned demeanor due to the health risks.
-  - australian_government_representatives: Various Australian federal and state government officials, including politicians, committee members, and regulators. · Government offices and occasional visits to Wittenoom, 1940s-2020s. · APPEARANCE: Predominantly Caucasian, appearing authoritative and formal, reflecting their political or administrative roles.
-  - csr_corporate_personnel: Executives, managers, and other personnel from Colonial Sugar Refining (CSR) and its subsidiary, Australian Blue Asbestos (ABA). · Corporate offices and Wittenoom, 1937-1966. · APPEARANCE: Predominantly Caucasian, appearing well-dressed and corporate, often with an air of authority, sometimes dismissive of worker concerns.
-  - banjima_traditional_owners_and_advocates: Indigenous Banjima people, including elders and legal advocates, asserting their rights over contaminated lands. · Wittenoom area and legal forums, 2010s-2020s. · APPEARANCE: Indigenous Australian people, often older, appearing resilient and determined, some bearing the visible or implied health consequences of asbestos exposure.
-  - australian_airport_police: Law enforcement personnel working in Australian airports. · Australian airport checkpoint, 1985. · APPEARANCE: Predominantly Caucasian, appearing uniformed and professional.
+  - prospectors_mine_owners: Australian prospectors and early mine owners who opened blue asbestos workings in the Hamersley Ranges gorges. · Wittenoom and Yampire gorges, 1937-1943. · APPEARANCE: Australian men of British or Irish descent, fair skin deeply sun-tanned and weathered, short hair, lean wiry build from bush prospecting.
+  - company_managers: Managers and executives of ABA and its parent CSR, a Sydney sugar company with little mining experience, plus town steering committee members. · Wittenoom and corporate offices, 1943-1966. · APPEARANCE: Australian men of British descent, fair complexions, neatly cut and combed hair, office-worker builds.
+  - mine_and_health_officials: Australian state mines inspectors, deputy mining engineers, public health doctors, a health commissioner, health inspectors and an industrial hygienist who reported on the dust. · Wittenoom mine, mill and town and government offices, 1944-1968. · APPEARANCE: Australian men of British descent, fair skin, short neat hair, professional office builds.
+  - mine_and_mill_workers: Asbestos miners, mill hands and fitters: Australian workers, post-war European displaced persons on federal contracts, European recruits from CSR trips, and Spanish migrants. · Wittenoom mines, mill and town, 1937-1966, with a high-turnover workforce throughout. · APPEARANCE: Mixed Australian (British-descended) and Southern, Central and Eastern European men, light to o
+  - spanish_migrant_families: Spanish migrant miners' families from Madrid who came under the Spain-Australia migration agreement, including wives, infants and children, and their later adult children working in media. · Ships via Suez and Wittenoom 1962-1964, Australia until 1971, Madrid from 1966 and 1971, an Australian airport in 1985, and later interviews into the 2020s. · APPEARANCE: Spanish
+  - town_children: Children of miners, including Spanish migrant children, who grew up in the tailings-paved town and played with asbestos. · Wittenoom streets, yards and schoolyard, 1950s-1966. · APPEARANCE: Australian, European and Spanish children with light to olive skin, tanned, tousled hair, dusted with red earth and fine asbestos powder.
+  - union_and_arbitration: Australian Workers' Union representatives, employer advocates and members of the arbitration Board of Reference who negotiated the dust allowance. · Wittenoom mill and arbitration hearings, 1946-1959. · APPEARANCE: Australian men of British descent, fair skin, short neat hair, mixed office and former manual-labour builds.
+  - australian_politicians: Australian prime ministers, state premiers, ministers, parliamentary inquiry leaders and committee chairs dealing with Wittenoom. · Canberra and Perth government and parliament settings, 1947, 1978-1994, 2016-2026. · APPEARANCE: Predominantly Australian men of British descent, fair skin, short groomed hair, middle-aged office builds.
+  - victims_advocates_and_lawyers: Former Wittenoom workers and residents with asbestos disease, the Asbestos Diseases Society of Australia, and the lawyers who litigated against the company and the state. · Perth, courts and offices, 1979-1989 and 2020s-2026. · APPEARANCE: Mixed Australian and European-born adults; ill former workers aged, thin and frail from lung disease.
+  - banjima_traditional_owners: Banjima Aboriginal traditional owners, elders and members of BNTAC whose country includes Wittenoom. · Banjima country around Wittenoom and the Pilbara, 2023-2026. · APPEARANCE: Aboriginal Australian people with dark brown skin, dark curly or wavy hair, elders with grey hair and beards, builds shaped by outdoor life in the Pilbara.
+  - international_un_official: A visiting United Nations special rapporteur investigating toxic contamination. · Australia, meeting Banjima elders, 2023. · APPEARANCE: -
+  - airport_police: Australian airport police officers at a passport and identity checkpoint. · An Australian airport checkpoint, 1985. · APPEARANCE: -
```

**resto**

```diff
--- f50c
+++ f50d
-  materials_textures           : Corrugated iron, wood, asbestos cement, pervasive red earth, blue asbestos waste, fine asbestos dust, loose granular tailings, deposited asbestos fibers, weathered metallic tones, barricade construction materials.
-  color_palette                : Exterior palette dominated by red earth, dusty grey, weathered metallic hues (corrugated iron), and the distinctive blue of asbestos. Interiors typically featured pale, functional colors on walls, often obscured by dust.
-  scale_dimensions             : Extensive desert landscapes, a small town footprint with residential and industrial structures of modest scale (typically one to two stories), large mining waste dumps, and vast areas of ground-level asbestos deposits spreading across 46,840 hectares. Transported asbestos fibers are microscopic but accumulate in large visible deposits.
-  distinctive_features         : An isolated Australian ghost town in the Pilbara desert, visibly constructed with and heavily contaminated by insidious blue asbestos waste from the 1937-1966 mining era. The pervasive red earth and fine, constantly disturbed asbestos dust are omnipresent, defining the toxic and deserted environment.
-  demographics                 : The population consisted primarily of Australian and European migrant workers (including Spanish and displaced persons) from the 1940s-1960s, working as miners and mill workers, along with their families. Children were present, often playing in contaminated areas. Later, Aboriginal Banjima traditional owners became prominent in advocacy regarding the contaminated 
-  condition_evolution.at_event : A remote, functional mining town with active blue asbestos mining and processing operations. Its infrastructure and residential areas were visibly constructed using asbestos tailings, resulting in pervasive dust and rudimentary, functional buildings.
-  condition_evolution.later    : A deserted ghost town characterized by demolished buildings, permanent barricades blocking access to an officially contaminated area of 46,840 hectares, and extensive asbestos contamination spread by wind and water across the landscape.
+  materials_textures           : Worker houses built from corrugated sheet metal, timber and asbestos-cement sheeting; loose, crumbling fibrous asbestos that shreds into fine powder when handled; compacted asbestos tailings laid as the surface of roads, yards, driveways, the schoolyard, public spaces and the airstrip; fine powdery dust coating people, buildings and the mill; loose tailings dumps 
+  color_palette                : Exterior dominated by intense red earth and red dust under harsh desert light, with blue-grey asbestos tailings surfaces and pale grey dust films over buildings and workers; interiors not documented; surviving family imagery described as sepia-toned.
+  scale_dimensions             : A small, isolated outback mining town with a dirt airstrip sized for small propeller aircraft, three mines in the surrounding gorges, more than three million tonnes of tailings left behind, and an official asbestos management area of 46,840 hectares extending down drainage lines toward the Fortescue River.
+  distinctive_features         : A small mining town in the red Pilbara desert whose own roads, yards, schoolyard and airstrip were paved with blue asbestos tailings, so the poison literally formed the ground people walked and played on; today it is an emptied, demolished, unmapped zone sealed by permanent barricades.
+  demographics                 : Documented workforce of Australian miners and mill workers, post-war European displaced persons assigned under federal work contracts (1948-1951), European recruits from private CSR recruitment trips (from 1950), and Spanish migrant families under the Spain-Australia migration agreement (early 1960s), with wives and young children living in town; mill workers dres
+  condition_evolution.at_event : An operating mining town in the early 1960s: inhabited sheet-metal and asbestos-cement houses, a working mill wrapped in thick dust clouds, trucks dumping tailings to surface roads, yards and the schoolyard, children playing on the ground, and small propeller planes landing on the tailings airstrip.
+  condition_evolution.later    : After mining ended in December 1966 the town was progressively reduced from 1978, its school, nursing post and police station closed and buildings demolished from 1986 to 1992, the airport closed in 1993, power cut in 2006, the town formally abolished and erased from maps and signs in 2007, the last residents gone by 2022-2023 and remaining structures demolished, 
-  • role: Doctor/Health Official | age unknown | era: 1948
-    appearance_canon: a middle-aged health official, likely Australian, with a serious demeanor
-  • role: Spanish Migrant Miner | age 26 | era: 1962
-    appearance_canon: a mid-20s Spanish migrant miner, often working long hours in dusty conditions, potentially appearing fatigued
-  • role: Spanish Migrant Resident | age 26 | era: 1962
-    appearance_canon: a mid-20s Spanish migrant woman, resilient in harsh living conditions, possibly showing signs of fatigue from a complicated childbirth
-  • role: Spanish Migrant Resident | age 26 | era: 1962
-    appearance_canon: a mid-20s Spanish migrant woman, forming friendships in a challenging desert environment
-  • role: Spanish Migrant Miner | age 26 | era: 1962
-    appearance_canon: a mid-20s Spanish migrant miner, working excessively long hours in dangerous conditions, likely appearing dust-covered and exhausted
-  • role: Child Resident | age 7 | era: 1962
-    appearance_canon: a child of early elementary school age, playing in a dusty, asbestos-laden environment, potentially appearing oblivious to danger
-  • role: Television Producer / Wittenoom-born | age 22 | era: 1985
-    appearance_canon: an early-20s Spanish-Australian young adult, looking at his documentation while being questioned by an airport police officer
-  • role: Banjima Elder / Activist | age unknown | era: 2023
-    appearance_canon: an elderly Aboriginal Banjima man, bearing the physical toll of asbestos exposure
-  • role: Lawyer | age unknown | era: 1988
-    appearance_canon: a middle-aged lawyer, determined in legal proceedings regarding corporate accountability
-  • role: Daughter of Migrant Miners | age unknown | era: 1971
-    appearance_canon: a young adult of Spanish descent, having lived in Wittenoom as a child, choosing to remain in Australia
-  • role: Infant Resident | age 0 | era: 1963
-    appearance_canon: an infant born in Wittenoom to Spanish migrant parents
-  • role: Public Health Official | age unknown | era: 1965
-    appearance_canon: a middle-aged health official, likely Australian, sternly addressing safety concerns
-  • role: Industrial Hygienist | age unknown | era: 1966
-    appearance_canon: a middle-aged industrial hygienist, meticulously documenting safety deficiencies
-  • role: CSR Chairman | age unknown | era: 1966
-    appearance_canon: an elderly corporate chairman making a public announcement
-  • role: Minister for Lands | age unknown | era: 2019
-    appearance_canon: a middle-aged Aboriginal Australian government minister, addressing environmental remediation responsibilities
-  • role: UN Rapporteur | age unknown | era: 2023
-    appearance_canon: a middle-aged UN rapporteur, conducting interviews related to environmental contamination
-
-OBJETOS DOCUMENTADOS (mantené la FORMA GENERAL constante entre imágenes;
-la narración puede nombrarlos por metáfora, función o material):
-  • objeto: Asbestos tailings
-    forma: Finely crushed rock and blue asbestos fibers, used as construction material or deposited as waste, appearing as loose granular piles or spread over surfaces, easily disturbed to release fine dust.
-  • objeto: Wittenoom's deserted buildings
-    forma: Shabby structures of corrugated iron, wood, and asbestos cement, often appearing neglected or partially demolished, constructed directly with or heavily contaminated by blue asbestos waste.
+  • role: Prospector and mine owner in Wittenoom and Yampire gorges whose interests were taken over by ABA | age unknown | era: 1937-1943
+    appearance_canon: an adult Australian prospector in rugged bush work clothes and wide-brimmed hat, weathered by outdoor work
+  • role: Prospector and mine partner in Wittenoom and Yampire gorges whose interests were taken over by ABA | age unknown | era: 1937-1943
+    appearance_canon: an adult Australian prospector and mine manager in practical bush work clothes, sun-weathered
+  • role: Public health doctor who warned in writing that dust levels were extremely dangerous | age unknown | era: 1948
+    appearance_canon: an adult Australian government medical officer in a lightweight suit and tie with a serious, concerned demeanor
+  • role: Prime Minister of Australia who described the mine's life as practically unlimited | age unknown | era: 1947
+    appearance_canon: a senior Australian statesman in a formal dark suit with a composed public demeanor
+  • role: Public health doctor who reported a mesothelioma case in a former mill worker | age unknown | era: 1962
+    appearance_canon: a middle-aged Australian public health physician in a shirt and tie with a clinical, attentive demeanor
+  • role: Public Health Commissioner who reprimanded the school principal for covering the schoolyard with tailings | age unknown | era: 1965
+    appearance_canon: a middle-aged Australian senior health official in a suit with a stern, authoritative demeanor
+  • role: Industrial hygienist who described spills, leaks and poor machinery modifications | age unknown | era: 1966
+    appearance_canon: a middle-aged Australian industrial hygienist in shirt sleeves and tie, inspecting machinery with a critical eye
+  • role: CSR chairman who announced the closure of the mining operations | age unknown | era: 1966
+    appearance_canon: a middle-aged Australian corporate executive in a dark tailored suit with a formal boardroom demeanor
+  • role: State premier whose government rejected the parliamentary clean-up report | age unknown | era: 1992
+    appearance_canon: a middle-aged Australian state politician in a dark business suit with a guarded official demeanor
+  • role: Lawyer who obtained the 1988 Wittenoom verdict against the company | age unknown | era: 1988
+    appearance_canon: an adult Australian litigation lawyer in a business suit with a determined courtroom demeanor
+  • role: State minister who argued the responsible companies should pay for remediation | age unknown | era: 2019
+    appearance_canon: a middle-aged Australian state government minister in a modern business suit
+  • role: UN special rapporteur who visited Australia and interviewed a Banjima elder about the contamination | age unknown | era: 2023
+    appearance_canon: a middle-aged international UN human rights expert in modern business attire with an attentive, listening demeanor
+  • role: Banjima elder and activist who spoke about persistent harm and died of mesothelioma | age unknown | era: 2023-2024
+    appearance_canon: an elderly Aboriginal Australian Banjima elder in casual outback clothing with a dignified, weary bearing
+  • role: CEO of the Asbestos Diseases Society of Australia estimating deaths may exceed 4,000 | age unknown | era: 2020s
+    appearance_canon: a middle-aged Australian woman advocate in modern professional attire with an earnest demeanor
+  • role: Spanish migrant miner in Wittenoom, injured in the foot, later died of mesothelioma | age unknown | era: 1962-1963
+    appearance_canon: a young adult Spanish migrant miner in dusty work clothes, in one portrait with a bandaged foot
+  • role: Wife of a Spanish miner and Wittenoom resident who gave birth in the town hospital | age unknown | era: 1962-1963
+    appearance_canon: a young adult Spanish woman in a simple cotton dress, physically weakened after a difficult birth, hopeful but strained
+  • role: Son of a Spanish miner, born in Wittenoom, later a television producer | age unknown | era: 1963-1985
+    appearance_canon: a young adult man of Spanish descent born in Australia, in casual travel clothes at an airport checkpoint
+  • role: Wife of a Spanish miner and Wittenoom resident who gave birth in the town | age unknown | era: 1962-1964
+    appearance_canon: a young adult Spanish mother in a modest cotton dress, caring for small children in the heat and dust
+  • role: Spanish migrant miner in Wittenoom who often worked 16-hour shifts | age unknown | era: 1962-1964
+    appearance_canon: an adult Spanish migrant miner in dust-covered work shirt and trousers, visibly exhausted from long shifts
+  • role: Child of the De Juan-Barroso family who lived in Wittenoom and later recalled it | age unknown | era: 1962-1964
+    appearance_canon: a young Spanish boy in shorts and a cotton shirt, red dust on skin and clothes
+  • role: Son of a Spanish miner born in Wittenoom | age unknown | era: 1963
+    appearance_canon: a newborn infant of Spanish parents wrapped in a light cotton blanket
+  • role: Daughter of a Spanish miner who lived in Wittenoom as a child and remained in Australia | age unknown | era: 1962-1971
+    appearance_canon: a young Spanish girl in a simple cotton frock with dust on her sandals
+
+OBJETOS DOCUMENTADOS: (vacío) — describí cualquier objeto que nombre la narración por su forma física según el relato, sin inventar detalles no dichos.
-  - contemporary clothing (post-2000s)
-  - modern cars (post-1970s)
-  - digital cameras
-  - modern industrial safety equipment (e.g., advanced respirators)
-  - satellite dishes
-  - GPS devices
-  - modern communication technology
+  - contemporary clothing
+  - modern industrial safety equipment in mining-era scenes
+  - hazmat suits and modern respirators before the 1980s
+  - hi-visibility vests
+  - sealed bitumen roads with painted lines
+  - modern SUVs and pickup trucks in mining-era scenes
+  - jet aircraft at the town airstrip
+  - plastic asbestos-hazard warning signs before closure
+  - solar panels and satellite dishes
```


## ch04

### código solo (canon de antes): diff crudo contra F50c

```diff
-  - wittenoom_miners_and_mill_workers: Various European migrant and Australian laborers working in the asbestos mines and processing mill. · Wittenoom, from 1937 to 1966. · APPEARANCE: Physically robust individuals, often appearing fatigued and covered in a pervasive fine dust, with diverse European features. · CLOTHING: Rugged, practical work clothes, heavy-duty trousers and shirts, sometimes wi
-  - spanish_migrant_families: Spanish families who migrated to Wittenoom under government schemes. · Wittenoom, primarily 1958-1966. · APPEARANCE: Adults and children of Southern European descent, appearing resilient and resourceful, adapting to a harsh desert environment, often showing signs of physical strain or everyday weariness. · CLOTHING: Simple, light clothing suitable for a hot, dusty cl
-  - australian_public_health_officials: Doctors, inspectors, and hygienists from Australian public health departments. · Wittenoom and state offices, 1944-1966. · APPEARANCE: Predominantly Caucasian, appearing professional, often with a serious or concerned demeanor due to the health risks. · CLOTHING: Formal or semi-formal attire of the era, such as suits, collared shirts, and ties, or clean uni
-  - australian_government_representatives: Various Australian federal and state government officials, including politicians, committee members, and regulators. · Government offices and occasional visits to Wittenoom, 1940s-2020s. · APPEARANCE: Predominantly Caucasian, appearing authoritative and formal, reflecting their political or administrative roles. · CLOTHING: Formal business attire, includ
-  - csr_corporate_personnel: Executives, managers, and other personnel from Colonial Sugar Refining (CSR) and its subsidiary, Australian Blue Asbestos (ABA). · Corporate offices and Wittenoom, 1937-1966. · APPEARANCE: Predominantly Caucasian, appearing well-dressed and corporate, often with an air of authority, sometimes dismissive of worker concerns. · CLOTHING: Business suits and formal wear, r
-  - banjima_traditional_owners_and_advocates: Indigenous Banjima people, including elders and legal advocates, asserting their rights over contaminated lands. · Wittenoom area and legal forums, 2010s-2020s. · APPEARANCE: Indigenous Australian people, often older, appearing resilient and determined, some bearing the visible or implied health consequences of asbestos exposure. · CLOTHING: Practical
-  - australian_airport_police: Law enforcement personnel working in Australian airports. · Australian airport checkpoint, 1985. · APPEARANCE: Predominantly Caucasian, appearing uniformed and professional. · CLOTHING: Standard police uniform of the mid-1980s, typically including a collared shirt, trousers, and a peaked cap.
+  - wittenoom_miners_and_mill_workers: Various European migrant and Australian laborers working in the asbestos mines and processing mill. · Wittenoom, from 1937 to 1966. · APPEARANCE: Physically robust individuals, often appearing fatigued and covered in a pervasive fine dust, with diverse European features. · CLOTHING: -
+  - spanish_migrant_families: Spanish families who migrated to Wittenoom under government schemes. · Wittenoom, primarily 1958-1966. · APPEARANCE: Adults and children of Southern European descent, appearing resilient and resourceful, adapting to a harsh desert environment, often showing signs of physical strain or everyday weariness. · CLOTHING: -
+  - australian_public_health_officials: Doctors, inspectors, and hygienists from Australian public health departments. · Wittenoom and state offices, 1944-1966. · APPEARANCE: Predominantly Caucasian, appearing professional, often with a serious or concerned demeanor due to the health risks. · CLOTHING: -
+  - australian_government_representatives: Various Australian federal and state government officials, including politicians, committee members, and regulators. · Government offices and occasional visits to Wittenoom, 1940s-2020s. · APPEARANCE: Predominantly Caucasian, appearing authoritative and formal, reflecting their political or administrative roles. · CLOTHING: -
+  - csr_corporate_personnel: Executives, managers, and other personnel from Colonial Sugar Refining (CSR) and its subsidiary, Australian Blue Asbestos (ABA). · Corporate offices and Wittenoom, 1937-1966. · APPEARANCE: Predominantly Caucasian, appearing well-dressed and corporate, often with an air of authority, sometimes dismissive of worker concerns. · CLOTHING: -
+  - banjima_traditional_owners_and_advocates: Indigenous Banjima people, including elders and legal advocates, asserting their rights over contaminated lands. · Wittenoom area and legal forums, 2010s-2020s. · APPEARANCE: Indigenous Australian people, often older, appearing resilient and determined, some bearing the visible or implied health consequences of asbestos exposure. · CLOTHING: -
+  - australian_airport_police: Law enforcement personnel working in Australian airports. · Australian airport checkpoint, 1985. · APPEARANCE: Predominantly Caucasian, appearing uniformed and professional. · CLOTHING: -
```

### canon nuevo: diff por zona

**era**

```diff
--- f50c
+++ f50d
-  clothing              : Miners wore rugged work clothes, often appearing dirty and dusty. Town residents wore practical, light attire suitable for hot desert conditions, including simple dresses, shirts, and shorts. Government and corporate officials wore more formal attire, such as suits, appropriate for their roles and the era.
-  technology            : Analog gauges, basic mining machinery with exposed components, rudimentary processing plants, simple residential appliances (e.g., older refrigerators, stoves), landline telephones, and radios. NO LEDs, NO digital displays, NO smartphones, NO advanced computing devices.
-  vehicles_machinery    : Early to mid-20th century trucks (e.g., for asbestos transport), desert-adapted 4x4 vehicles, passenger cars from the 1940s-1960s. Propeller-driven small aircraft for transport to the remote town. Mining equipment included drills, crushers, and conveyor belt systems.
-  interiors             : Residential interiors were basic and utilitarian, often in houses of corrugated iron, wood, and asbestos cement, prone to dust accumulation. Offices featured simple desks, manual typewriters, and basic filing systems. Public buildings like hospitals had functional, unadorned spaces with period-appropriate medical equipment.
-  forbidden_anachronisms: smartphones, LED screens, contemporary clothing (post-2000s), modern flat panels, modern cars (post-1970s), digital cameras, modern industrial safety equipment (e.g., advanced respirators), satellite dishes, renewable energy installations.
+  period 1946-1966:
+  clothing              : Dust-covered miners and mill hands in work shirts, shorts or trousers and boots; migrant families in modest European clothing adapted to heat; officials and doctors in lightweight suits or short sleeves with ties.
+  technology            : Full-scale crushing mill with conveyors, fans and later dust-reducing equipment, valve radios, telephones, typewriters, film cameras producing sepia and black-and-white family photos.
+  vehicles_machinery    : Ore and tipper trucks spreading tailings on roads and yards, small propeller aircraft on the tailings-surfaced airstrip, mid-century sedans and bush vehicles, ocean liners carrying migrants.
+  interiors             : Sheet-metal, timber and asbestos-cement houses, town hospital, school with tailings-covered yard, churches and community buildings, dusty mill interior.
+  forbidden_anachronisms: In mining-era scenes: no modern respirators, hazmat suits, hi-visibility vests or hard hats with modern logos; no sealed bitumen roads with painted lines; no modern four-wheel drives, SUVs or pickup trucks; no jet aircraft at the airstrip; no plastic warning signs or asbestos-hazard pictograms; no mobile phones, digital cameras, computers or LED lighting; no solar panels
```

**grupo**

```diff
--- f50c
+++ f50d
-  - wittenoom_miners_and_mill_workers: Various European migrant and Australian laborers working in the asbestos mines and processing mill. · Wittenoom, from 1937 to 1966. · APPEARANCE: Physically robust individuals, often appearing fatigued and covered in a pervasive fine dust, with diverse European features.
-  - spanish_migrant_families: Spanish families who migrated to Wittenoom under government schemes. · Wittenoom, primarily 1958-1966. · APPEARANCE: Adults and children of Southern European descent, appearing resilient and resourceful, adapting to a harsh desert environment, often showing signs of physical strain or everyday weariness.
-  - australian_public_health_officials: Doctors, inspectors, and hygienists from Australian public health departments. · Wittenoom and state offices, 1944-1966. · APPEARANCE: Predominantly Caucasian, appearing professional, often with a serious or concerned demeanor due to the health risks.
-  - australian_government_representatives: Various Australian federal and state government officials, including politicians, committee members, and regulators. · Government offices and occasional visits to Wittenoom, 1940s-2020s. · APPEARANCE: Predominantly Caucasian, appearing authoritative and formal, reflecting their political or administrative roles.
-  - csr_corporate_personnel: Executives, managers, and other personnel from Colonial Sugar Refining (CSR) and its subsidiary, Australian Blue Asbestos (ABA). · Corporate offices and Wittenoom, 1937-1966. · APPEARANCE: Predominantly Caucasian, appearing well-dressed and corporate, often with an air of authority, sometimes dismissive of worker concerns.
-  - banjima_traditional_owners_and_advocates: Indigenous Banjima people, including elders and legal advocates, asserting their rights over contaminated lands. · Wittenoom area and legal forums, 2010s-2020s. · APPEARANCE: Indigenous Australian people, often older, appearing resilient and determined, some bearing the visible or implied health consequences of asbestos exposure.
-  - australian_airport_police: Law enforcement personnel working in Australian airports. · Australian airport checkpoint, 1985. · APPEARANCE: Predominantly Caucasian, appearing uniformed and professional.
+  - prospectors_mine_owners: Australian prospectors and early mine owners who opened blue asbestos workings in the Hamersley Ranges gorges. · Wittenoom and Yampire gorges, 1937-1943. · APPEARANCE: Australian men of British or Irish descent, fair skin deeply sun-tanned and weathered, short hair, lean wiry build from bush prospecting.
+  - company_managers: Managers and executives of ABA and its parent CSR, a Sydney sugar company with little mining experience, plus town steering committee members. · Wittenoom and corporate offices, 1943-1966. · APPEARANCE: Australian men of British descent, fair complexions, neatly cut and combed hair, office-worker builds.
+  - mine_and_health_officials: Australian state mines inspectors, deputy mining engineers, public health doctors, a health commissioner, health inspectors and an industrial hygienist who reported on the dust. · Wittenoom mine, mill and town and government offices, 1944-1968. · APPEARANCE: Australian men of British descent, fair skin, short neat hair, professional office builds.
+  - mine_and_mill_workers: Asbestos miners, mill hands and fitters: Australian workers, post-war European displaced persons on federal contracts, European recruits from CSR trips, and Spanish migrants. · Wittenoom mines, mill and town, 1937-1966, with a high-turnover workforce throughout. · APPEARANCE: Mixed Australian (British-descended) and Southern, Central and Eastern European men, light to o
+  - spanish_migrant_families: Spanish migrant miners' families from Madrid who came under the Spain-Australia migration agreement, including wives, infants and children, and their later adult children working in media. · Ships via Suez and Wittenoom 1962-1964, Australia until 1971, Madrid from 1966 and 1971, an Australian airport in 1985, and later interviews into the 2020s. · APPEARANCE: Spanish
+  - town_children: Children of miners, including Spanish migrant children, who grew up in the tailings-paved town and played with asbestos. · Wittenoom streets, yards and schoolyard, 1950s-1966. · APPEARANCE: Australian, European and Spanish children with light to olive skin, tanned, tousled hair, dusted with red earth and fine asbestos powder.
+  - union_and_arbitration: Australian Workers' Union representatives, employer advocates and members of the arbitration Board of Reference who negotiated the dust allowance. · Wittenoom mill and arbitration hearings, 1946-1959. · APPEARANCE: Australian men of British descent, fair skin, short neat hair, mixed office and former manual-labour builds.
+  - australian_politicians: Australian prime ministers, state premiers, ministers, parliamentary inquiry leaders and committee chairs dealing with Wittenoom. · Canberra and Perth government and parliament settings, 1947, 1978-1994, 2016-2026. · APPEARANCE: Predominantly Australian men of British descent, fair skin, short groomed hair, middle-aged office builds.
+  - victims_advocates_and_lawyers: Former Wittenoom workers and residents with asbestos disease, the Asbestos Diseases Society of Australia, and the lawyers who litigated against the company and the state. · Perth, courts and offices, 1979-1989 and 2020s-2026. · APPEARANCE: Mixed Australian and European-born adults; ill former workers aged, thin and frail from lung disease.
+  - banjima_traditional_owners: Banjima Aboriginal traditional owners, elders and members of BNTAC whose country includes Wittenoom. · Banjima country around Wittenoom and the Pilbara, 2023-2026. · APPEARANCE: Aboriginal Australian people with dark brown skin, dark curly or wavy hair, elders with grey hair and beards, builds shaped by outdoor life in the Pilbara.
+  - international_un_official: A visiting United Nations special rapporteur investigating toxic contamination. · Australia, meeting Banjima elders, 2023. · APPEARANCE: -
+  - airport_police: Australian airport police officers at a passport and identity checkpoint. · An Australian airport checkpoint, 1985. · APPEARANCE: -
```

**resto**

```diff
--- f50c
+++ f50d
-  materials_textures           : Corrugated iron, wood, asbestos cement, pervasive red earth, blue asbestos waste, fine asbestos dust, loose granular tailings, deposited asbestos fibers, weathered metallic tones, barricade construction materials.
-  color_palette                : Exterior palette dominated by red earth, dusty grey, weathered metallic hues (corrugated iron), and the distinctive blue of asbestos. Interiors typically featured pale, functional colors on walls, often obscured by dust.
-  scale_dimensions             : Extensive desert landscapes, a small town footprint with residential and industrial structures of modest scale (typically one to two stories), large mining waste dumps, and vast areas of ground-level asbestos deposits spreading across 46,840 hectares. Transported asbestos fibers are microscopic but accumulate in large visible deposits.
-  distinctive_features         : An isolated Australian ghost town in the Pilbara desert, visibly constructed with and heavily contaminated by insidious blue asbestos waste from the 1937-1966 mining era. The pervasive red earth and fine, constantly disturbed asbestos dust are omnipresent, defining the toxic and deserted environment.
-  demographics                 : The population consisted primarily of Australian and European migrant workers (including Spanish and displaced persons) from the 1940s-1960s, working as miners and mill workers, along with their families. Children were present, often playing in contaminated areas. Later, Aboriginal Banjima traditional owners became prominent in advocacy regarding the contaminated 
-  condition_evolution.at_event : A remote, functional mining town with active blue asbestos mining and processing operations. Its infrastructure and residential areas were visibly constructed using asbestos tailings, resulting in pervasive dust and rudimentary, functional buildings.
-  condition_evolution.later    : A deserted ghost town characterized by demolished buildings, permanent barricades blocking access to an officially contaminated area of 46,840 hectares, and extensive asbestos contamination spread by wind and water across the landscape.
+  materials_textures           : Worker houses built from corrugated sheet metal, timber and asbestos-cement sheeting; loose, crumbling fibrous asbestos that shreds into fine powder when handled; compacted asbestos tailings laid as the surface of roads, yards, driveways, the schoolyard, public spaces and the airstrip; fine powdery dust coating people, buildings and the mill; loose tailings dumps 
+  color_palette                : Exterior dominated by intense red earth and red dust under harsh desert light, with blue-grey asbestos tailings surfaces and pale grey dust films over buildings and workers; interiors not documented; surviving family imagery described as sepia-toned.
+  scale_dimensions             : A small, isolated outback mining town with a dirt airstrip sized for small propeller aircraft, three mines in the surrounding gorges, more than three million tonnes of tailings left behind, and an official asbestos management area of 46,840 hectares extending down drainage lines toward the Fortescue River.
+  distinctive_features         : A small mining town in the red Pilbara desert whose own roads, yards, schoolyard and airstrip were paved with blue asbestos tailings, so the poison literally formed the ground people walked and played on; today it is an emptied, demolished, unmapped zone sealed by permanent barricades.
+  demographics                 : Documented workforce of Australian miners and mill workers, post-war European displaced persons assigned under federal work contracts (1948-1951), European recruits from private CSR recruitment trips (from 1950), and Spanish migrant families under the Spain-Australia migration agreement (early 1960s), with wives and young children living in town; mill workers dres
+  condition_evolution.at_event : An operating mining town in the early 1960s: inhabited sheet-metal and asbestos-cement houses, a working mill wrapped in thick dust clouds, trucks dumping tailings to surface roads, yards and the schoolyard, children playing on the ground, and small propeller planes landing on the tailings airstrip.
+  condition_evolution.later    : After mining ended in December 1966 the town was progressively reduced from 1978, its school, nursing post and police station closed and buildings demolished from 1986 to 1992, the airport closed in 1993, power cut in 2006, the town formally abolished and erased from maps and signs in 2007, the last residents gone by 2022-2023 and remaining structures demolished, 
-  • role: Doctor/Health Official | age unknown | era: 1948
-    appearance_canon: a middle-aged health official, likely Australian, with a serious demeanor
-  • role: Spanish Migrant Miner | age 26 | era: 1962
-    appearance_canon: a mid-20s Spanish migrant miner, often working long hours in dusty conditions, potentially appearing fatigued
-  • role: Spanish Migrant Resident | age 26 | era: 1962
-    appearance_canon: a mid-20s Spanish migrant woman, resilient in harsh living conditions, possibly showing signs of fatigue from a complicated childbirth
-  • role: Spanish Migrant Resident | age 26 | era: 1962
-    appearance_canon: a mid-20s Spanish migrant woman, forming friendships in a challenging desert environment
-  • role: Spanish Migrant Miner | age 26 | era: 1962
-    appearance_canon: a mid-20s Spanish migrant miner, working excessively long hours in dangerous conditions, likely appearing dust-covered and exhausted
-  • role: Child Resident | age 7 | era: 1962
-    appearance_canon: a child of early elementary school age, playing in a dusty, asbestos-laden environment, potentially appearing oblivious to danger
-  • role: Television Producer / Wittenoom-born | age 22 | era: 1985
-    appearance_canon: an early-20s Spanish-Australian young adult, looking at his documentation while being questioned by an airport police officer
-  • role: Banjima Elder / Activist | age unknown | era: 2023
-    appearance_canon: an elderly Aboriginal Banjima man, bearing the physical toll of asbestos exposure
-  • role: Lawyer | age unknown | era: 1988
-    appearance_canon: a middle-aged lawyer, determined in legal proceedings regarding corporate accountability
-  • role: Daughter of Migrant Miners | age unknown | era: 1971
-    appearance_canon: a young adult of Spanish descent, having lived in Wittenoom as a child, choosing to remain in Australia
-  • role: Infant Resident | age 0 | era: 1963
-    appearance_canon: an infant born in Wittenoom to Spanish migrant parents
-  • role: Public Health Official | age unknown | era: 1965
-    appearance_canon: a middle-aged health official, likely Australian, sternly addressing safety concerns
-  • role: Industrial Hygienist | age unknown | era: 1966
-    appearance_canon: a middle-aged industrial hygienist, meticulously documenting safety deficiencies
-  • role: CSR Chairman | age unknown | era: 1966
-    appearance_canon: an elderly corporate chairman making a public announcement
-  • role: Minister for Lands | age unknown | era: 2019
-    appearance_canon: a middle-aged Aboriginal Australian government minister, addressing environmental remediation responsibilities
-  • role: UN Rapporteur | age unknown | era: 2023
-    appearance_canon: a middle-aged UN rapporteur, conducting interviews related to environmental contamination
-
-OBJETOS DOCUMENTADOS (mantené la FORMA GENERAL constante entre imágenes;
-la narración puede nombrarlos por metáfora, función o material):
-  • objeto: Asbestos tailings
-    forma: Finely crushed rock and blue asbestos fibers, used as construction material or deposited as waste, appearing as loose granular piles or spread over surfaces, easily disturbed to release fine dust.
-  • objeto: Wittenoom's deserted buildings
-    forma: Shabby structures of corrugated iron, wood, and asbestos cement, often appearing neglected or partially demolished, constructed directly with or heavily contaminated by blue asbestos waste.
+  • role: Prospector and mine owner in Wittenoom and Yampire gorges whose interests were taken over by ABA | age unknown | era: 1937-1943
+    appearance_canon: an adult Australian prospector in rugged bush work clothes and wide-brimmed hat, weathered by outdoor work
+  • role: Prospector and mine partner in Wittenoom and Yampire gorges whose interests were taken over by ABA | age unknown | era: 1937-1943
+    appearance_canon: an adult Australian prospector and mine manager in practical bush work clothes, sun-weathered
+  • role: Public health doctor who warned in writing that dust levels were extremely dangerous | age unknown | era: 1948
+    appearance_canon: an adult Australian government medical officer in a lightweight suit and tie with a serious, concerned demeanor
+  • role: Prime Minister of Australia who described the mine's life as practically unlimited | age unknown | era: 1947
+    appearance_canon: a senior Australian statesman in a formal dark suit with a composed public demeanor
+  • role: Public health doctor who reported a mesothelioma case in a former mill worker | age unknown | era: 1962
+    appearance_canon: a middle-aged Australian public health physician in a shirt and tie with a clinical, attentive demeanor
+  • role: Public Health Commissioner who reprimanded the school principal for covering the schoolyard with tailings | age unknown | era: 1965
+    appearance_canon: a middle-aged Australian senior health official in a suit with a stern, authoritative demeanor
+  • role: Industrial hygienist who described spills, leaks and poor machinery modifications | age unknown | era: 1966
+    appearance_canon: a middle-aged Australian industrial hygienist in shirt sleeves and tie, inspecting machinery with a critical eye
+  • role: CSR chairman who announced the closure of the mining operations | age unknown | era: 1966
+    appearance_canon: a middle-aged Australian corporate executive in a dark tailored suit with a formal boardroom demeanor
+  • role: State premier whose government rejected the parliamentary clean-up report | age unknown | era: 1992
+    appearance_canon: a middle-aged Australian state politician in a dark business suit with a guarded official demeanor
+  • role: Lawyer who obtained the 1988 Wittenoom verdict against the company | age unknown | era: 1988
+    appearance_canon: an adult Australian litigation lawyer in a business suit with a determined courtroom demeanor
+  • role: State minister who argued the responsible companies should pay for remediation | age unknown | era: 2019
+    appearance_canon: a middle-aged Australian state government minister in a modern business suit
+  • role: UN special rapporteur who visited Australia and interviewed a Banjima elder about the contamination | age unknown | era: 2023
+    appearance_canon: a middle-aged international UN human rights expert in modern business attire with an attentive, listening demeanor
+  • role: Banjima elder and activist who spoke about persistent harm and died of mesothelioma | age unknown | era: 2023-2024
+    appearance_canon: an elderly Aboriginal Australian Banjima elder in casual outback clothing with a dignified, weary bearing
+  • role: CEO of the Asbestos Diseases Society of Australia estimating deaths may exceed 4,000 | age unknown | era: 2020s
+    appearance_canon: a middle-aged Australian woman advocate in modern professional attire with an earnest demeanor
+  • role: Spanish migrant miner in Wittenoom, injured in the foot, later died of mesothelioma | age unknown | era: 1962-1963
+    appearance_canon: a young adult Spanish migrant miner in dusty work clothes, in one portrait with a bandaged foot
+  • role: Wife of a Spanish miner and Wittenoom resident who gave birth in the town hospital | age unknown | era: 1962-1963
+    appearance_canon: a young adult Spanish woman in a simple cotton dress, physically weakened after a difficult birth, hopeful but strained
+  • role: Son of a Spanish miner, born in Wittenoom, later a television producer | age unknown | era: 1963-1985
+    appearance_canon: a young adult man of Spanish descent born in Australia, in casual travel clothes at an airport checkpoint
+  • role: Wife of a Spanish miner and Wittenoom resident who gave birth in the town | age unknown | era: 1962-1964
+    appearance_canon: a young adult Spanish mother in a modest cotton dress, caring for small children in the heat and dust
+  • role: Spanish migrant miner in Wittenoom who often worked 16-hour shifts | age unknown | era: 1962-1964
+    appearance_canon: an adult Spanish migrant miner in dust-covered work shirt and trousers, visibly exhausted from long shifts
+  • role: Child of the De Juan-Barroso family who lived in Wittenoom and later recalled it | age unknown | era: 1962-1964
+    appearance_canon: a young Spanish boy in shorts and a cotton shirt, red dust on skin and clothes
+  • role: Son of a Spanish miner born in Wittenoom | age unknown | era: 1963
+    appearance_canon: a newborn infant of Spanish parents wrapped in a light cotton blanket
+  • role: Daughter of a Spanish miner who lived in Wittenoom as a child and remained in Australia | age unknown | era: 1962-1971
+    appearance_canon: a young Spanish girl in a simple cotton frock with dust on her sandals
+
+OBJETOS DOCUMENTADOS: (vacío) — describí cualquier objeto que nombre la narración por su forma física según el relato, sin inventar detalles no dichos.
-  - contemporary clothing (post-2000s)
-  - modern cars (post-1970s)
-  - digital cameras
-  - modern industrial safety equipment (e.g., advanced respirators)
-  - satellite dishes
-  - GPS devices
-  - modern communication technology
+  - contemporary clothing
+  - modern industrial safety equipment in mining-era scenes
+  - hazmat suits and modern respirators before the 1980s
+  - hi-visibility vests
+  - sealed bitumen roads with painted lines
+  - modern SUVs and pickup trucks in mining-era scenes
+  - jet aircraft at the town airstrip
+  - plastic asbestos-hazard warning signs before closure
+  - solar panels and satellite dishes
```


## ch05

### código solo (canon de antes): diff crudo contra F50c

```diff
-  - wittenoom_miners_and_mill_workers: Various European migrant and Australian laborers working in the asbestos mines and processing mill. · Wittenoom, from 1937 to 1966. · APPEARANCE: Physically robust individuals, often appearing fatigued and covered in a pervasive fine dust, with diverse European features. · CLOTHING: Rugged, practical work clothes, heavy-duty trousers and shirts, sometimes wi
-  - spanish_migrant_families: Spanish families who migrated to Wittenoom under government schemes. · Wittenoom, primarily 1958-1966. · APPEARANCE: Adults and children of Southern European descent, appearing resilient and resourceful, adapting to a harsh desert environment, often showing signs of physical strain or everyday weariness. · CLOTHING: Simple, light clothing suitable for a hot, dusty cl
-  - australian_public_health_officials: Doctors, inspectors, and hygienists from Australian public health departments. · Wittenoom and state offices, 1944-1966. · APPEARANCE: Predominantly Caucasian, appearing professional, often with a serious or concerned demeanor due to the health risks. · CLOTHING: Formal or semi-formal attire of the era, such as suits, collared shirts, and ties, or clean uni
-  - australian_government_representatives: Various Australian federal and state government officials, including politicians, committee members, and regulators. · Government offices and occasional visits to Wittenoom, 1940s-2020s. · APPEARANCE: Predominantly Caucasian, appearing authoritative and formal, reflecting their political or administrative roles. · CLOTHING: Formal business attire, includ
-  - csr_corporate_personnel: Executives, managers, and other personnel from Colonial Sugar Refining (CSR) and its subsidiary, Australian Blue Asbestos (ABA). · Corporate offices and Wittenoom, 1937-1966. · APPEARANCE: Predominantly Caucasian, appearing well-dressed and corporate, often with an air of authority, sometimes dismissive of worker concerns. · CLOTHING: Business suits and formal wear, r
-  - banjima_traditional_owners_and_advocates: Indigenous Banjima people, including elders and legal advocates, asserting their rights over contaminated lands. · Wittenoom area and legal forums, 2010s-2020s. · APPEARANCE: Indigenous Australian people, often older, appearing resilient and determined, some bearing the visible or implied health consequences of asbestos exposure. · CLOTHING: Practical
-  - australian_airport_police: Law enforcement personnel working in Australian airports. · Australian airport checkpoint, 1985. · APPEARANCE: Predominantly Caucasian, appearing uniformed and professional. · CLOTHING: Standard police uniform of the mid-1980s, typically including a collared shirt, trousers, and a peaked cap.
+  - wittenoom_miners_and_mill_workers: Various European migrant and Australian laborers working in the asbestos mines and processing mill. · Wittenoom, from 1937 to 1966. · APPEARANCE: Physically robust individuals, often appearing fatigued and covered in a pervasive fine dust, with diverse European features. · CLOTHING: -
+  - spanish_migrant_families: Spanish families who migrated to Wittenoom under government schemes. · Wittenoom, primarily 1958-1966. · APPEARANCE: Adults and children of Southern European descent, appearing resilient and resourceful, adapting to a harsh desert environment, often showing signs of physical strain or everyday weariness. · CLOTHING: -
+  - australian_public_health_officials: Doctors, inspectors, and hygienists from Australian public health departments. · Wittenoom and state offices, 1944-1966. · APPEARANCE: Predominantly Caucasian, appearing professional, often with a serious or concerned demeanor due to the health risks. · CLOTHING: -
+  - australian_government_representatives: Various Australian federal and state government officials, including politicians, committee members, and regulators. · Government offices and occasional visits to Wittenoom, 1940s-2020s. · APPEARANCE: Predominantly Caucasian, appearing authoritative and formal, reflecting their political or administrative roles. · CLOTHING: -
+  - csr_corporate_personnel: Executives, managers, and other personnel from Colonial Sugar Refining (CSR) and its subsidiary, Australian Blue Asbestos (ABA). · Corporate offices and Wittenoom, 1937-1966. · APPEARANCE: Predominantly Caucasian, appearing well-dressed and corporate, often with an air of authority, sometimes dismissive of worker concerns. · CLOTHING: -
+  - banjima_traditional_owners_and_advocates: Indigenous Banjima people, including elders and legal advocates, asserting their rights over contaminated lands. · Wittenoom area and legal forums, 2010s-2020s. · APPEARANCE: Indigenous Australian people, often older, appearing resilient and determined, some bearing the visible or implied health consequences of asbestos exposure. · CLOTHING: -
+  - australian_airport_police: Law enforcement personnel working in Australian airports. · Australian airport checkpoint, 1985. · APPEARANCE: Predominantly Caucasian, appearing uniformed and professional. · CLOTHING: -
```

### canon nuevo: diff por zona

**era**

```diff
--- f50c
+++ f50d
-  clothing              : Miners wore rugged work clothes, often appearing dirty and dusty. Town residents wore practical, light attire suitable for hot desert conditions, including simple dresses, shirts, and shorts. Government and corporate officials wore more formal attire, such as suits, appropriate for their roles and the era.
-  technology            : Analog gauges, basic mining machinery with exposed components, rudimentary processing plants, simple residential appliances (e.g., older refrigerators, stoves), landline telephones, and radios. NO LEDs, NO digital displays, NO smartphones, NO advanced computing devices.
-  vehicles_machinery    : Early to mid-20th century trucks (e.g., for asbestos transport), desert-adapted 4x4 vehicles, passenger cars from the 1940s-1960s. Propeller-driven small aircraft for transport to the remote town. Mining equipment included drills, crushers, and conveyor belt systems.
-  interiors             : Residential interiors were basic and utilitarian, often in houses of corrugated iron, wood, and asbestos cement, prone to dust accumulation. Offices featured simple desks, manual typewriters, and basic filing systems. Public buildings like hospitals had functional, unadorned spaces with period-appropriate medical equipment.
-  forbidden_anachronisms: smartphones, LED screens, contemporary clothing (post-2000s), modern flat panels, modern cars (post-1970s), digital cameras, modern industrial safety equipment (e.g., advanced respirators), satellite dishes, renewable energy installations.
+  period 1946-1966:
+  clothing              : Dust-covered miners and mill hands in work shirts, shorts or trousers and boots; migrant families in modest European clothing adapted to heat; officials and doctors in lightweight suits or short sleeves with ties.
+  technology            : Full-scale crushing mill with conveyors, fans and later dust-reducing equipment, valve radios, telephones, typewriters, film cameras producing sepia and black-and-white family photos.
+  vehicles_machinery    : Ore and tipper trucks spreading tailings on roads and yards, small propeller aircraft on the tailings-surfaced airstrip, mid-century sedans and bush vehicles, ocean liners carrying migrants.
+  interiors             : Sheet-metal, timber and asbestos-cement houses, town hospital, school with tailings-covered yard, churches and community buildings, dusty mill interior.
+  period 1967-1992:
+  clothing              : Remaining residents and visitors in 1970s-1980s casual wear; lawyers, judges and politicians in period suits; ill former workers in hospital gowns or casual clothes.
+  technology            : Landline phones, typewriters giving way to early computers in offices, CRT televisions, court and parliamentary paperwork.
+  vehicles_machinery    : 1970s-1980s sedans and four-wheel drives, demolition machinery removing town buildings, no mining machinery operating.
+  interiors             : Shrinking town with closed school, nursing post and police station; courtrooms, parliamentary rooms, migrant family homes in Madrid.
+  period 1993-2026:
+  clothing              : Contemporary casual wear for Banjima traditional owners and activists; modern business attire for lawyers, officials and a UN rapporteur; modern protective coveralls and respirators for anyone inside the zone.
+  technology            : Modern warning signage, permanent barricades, contemporary offices and media equipment.
+  vehicles_machinery    : Modern four-wheel drives stopped outside barricaded access roads; no aircraft at the closed airstrip.
+  interiors             : Modern government offices, legal offices, interview settings with framed old family photographs.
+  forbidden_anachronisms: In mining-era scenes: no modern respirators, hazmat suits, hi-visibility vests or hard hats with modern logos; no sealed bitumen roads with painted lines; no modern four-wheel drives, SUVs or pickup trucks; no jet aircraft at the airstrip; no plastic warning signs or asbestos-hazard pictograms; no mobile phones, digital cameras, computers or LED lighting; no solar panels
```

**grupo**

```diff
--- f50c
+++ f50d
-  - wittenoom_miners_and_mill_workers: Various European migrant and Australian laborers working in the asbestos mines and processing mill. · Wittenoom, from 1937 to 1966. · APPEARANCE: Physically robust individuals, often appearing fatigued and covered in a pervasive fine dust, with diverse European features.
-  - spanish_migrant_families: Spanish families who migrated to Wittenoom under government schemes. · Wittenoom, primarily 1958-1966. · APPEARANCE: Adults and children of Southern European descent, appearing resilient and resourceful, adapting to a harsh desert environment, often showing signs of physical strain or everyday weariness.
-  - australian_public_health_officials: Doctors, inspectors, and hygienists from Australian public health departments. · Wittenoom and state offices, 1944-1966. · APPEARANCE: Predominantly Caucasian, appearing professional, often with a serious or concerned demeanor due to the health risks.
-  - australian_government_representatives: Various Australian federal and state government officials, including politicians, committee members, and regulators. · Government offices and occasional visits to Wittenoom, 1940s-2020s. · APPEARANCE: Predominantly Caucasian, appearing authoritative and formal, reflecting their political or administrative roles.
-  - csr_corporate_personnel: Executives, managers, and other personnel from Colonial Sugar Refining (CSR) and its subsidiary, Australian Blue Asbestos (ABA). · Corporate offices and Wittenoom, 1937-1966. · APPEARANCE: Predominantly Caucasian, appearing well-dressed and corporate, often with an air of authority, sometimes dismissive of worker concerns.
-  - banjima_traditional_owners_and_advocates: Indigenous Banjima people, including elders and legal advocates, asserting their rights over contaminated lands. · Wittenoom area and legal forums, 2010s-2020s. · APPEARANCE: Indigenous Australian people, often older, appearing resilient and determined, some bearing the visible or implied health consequences of asbestos exposure.
-  - australian_airport_police: Law enforcement personnel working in Australian airports. · Australian airport checkpoint, 1985. · APPEARANCE: Predominantly Caucasian, appearing uniformed and professional.
+  - prospectors_mine_owners: Australian prospectors and early mine owners who opened blue asbestos workings in the Hamersley Ranges gorges. · Wittenoom and Yampire gorges, 1937-1943. · APPEARANCE: Australian men of British or Irish descent, fair skin deeply sun-tanned and weathered, short hair, lean wiry build from bush prospecting.
+  - company_managers: Managers and executives of ABA and its parent CSR, a Sydney sugar company with little mining experience, plus town steering committee members. · Wittenoom and corporate offices, 1943-1966. · APPEARANCE: Australian men of British descent, fair complexions, neatly cut and combed hair, office-worker builds.
+  - mine_and_health_officials: Australian state mines inspectors, deputy mining engineers, public health doctors, a health commissioner, health inspectors and an industrial hygienist who reported on the dust. · Wittenoom mine, mill and town and government offices, 1944-1968. · APPEARANCE: Australian men of British descent, fair skin, short neat hair, professional office builds.
+  - mine_and_mill_workers: Asbestos miners, mill hands and fitters: Australian workers, post-war European displaced persons on federal contracts, European recruits from CSR trips, and Spanish migrants. · Wittenoom mines, mill and town, 1937-1966, with a high-turnover workforce throughout. · APPEARANCE: Mixed Australian (British-descended) and Southern, Central and Eastern European men, light to o
+  - spanish_migrant_families: Spanish migrant miners' families from Madrid who came under the Spain-Australia migration agreement, including wives, infants and children, and their later adult children working in media. · Ships via Suez and Wittenoom 1962-1964, Australia until 1971, Madrid from 1966 and 1971, an Australian airport in 1985, and later interviews into the 2020s. · APPEARANCE: Spanish
+  - town_children: Children of miners, including Spanish migrant children, who grew up in the tailings-paved town and played with asbestos. · Wittenoom streets, yards and schoolyard, 1950s-1966. · APPEARANCE: Australian, European and Spanish children with light to olive skin, tanned, tousled hair, dusted with red earth and fine asbestos powder.
+  - union_and_arbitration: Australian Workers' Union representatives, employer advocates and members of the arbitration Board of Reference who negotiated the dust allowance. · Wittenoom mill and arbitration hearings, 1946-1959. · APPEARANCE: Australian men of British descent, fair skin, short neat hair, mixed office and former manual-labour builds.
+  - australian_politicians: Australian prime ministers, state premiers, ministers, parliamentary inquiry leaders and committee chairs dealing with Wittenoom. · Canberra and Perth government and parliament settings, 1947, 1978-1994, 2016-2026. · APPEARANCE: Predominantly Australian men of British descent, fair skin, short groomed hair, middle-aged office builds.
+  - victims_advocates_and_lawyers: Former Wittenoom workers and residents with asbestos disease, the Asbestos Diseases Society of Australia, and the lawyers who litigated against the company and the state. · Perth, courts and offices, 1979-1989 and 2020s-2026. · APPEARANCE: Mixed Australian and European-born adults; ill former workers aged, thin and frail from lung disease.
+  - banjima_traditional_owners: Banjima Aboriginal traditional owners, elders and members of BNTAC whose country includes Wittenoom. · Banjima country around Wittenoom and the Pilbara, 2023-2026. · APPEARANCE: Aboriginal Australian people with dark brown skin, dark curly or wavy hair, elders with grey hair and beards, builds shaped by outdoor life in the Pilbara.
+  - international_un_official: A visiting United Nations special rapporteur investigating toxic contamination. · Australia, meeting Banjima elders, 2023. · APPEARANCE: -
+  - airport_police: Australian airport police officers at a passport and identity checkpoint. · An Australian airport checkpoint, 1985. · APPEARANCE: -
```

**resto**

```diff
--- f50c
+++ f50d
-  materials_textures           : Corrugated iron, wood, asbestos cement, pervasive red earth, blue asbestos waste, fine asbestos dust, loose granular tailings, deposited asbestos fibers, weathered metallic tones, barricade construction materials.
-  color_palette                : Exterior palette dominated by red earth, dusty grey, weathered metallic hues (corrugated iron), and the distinctive blue of asbestos. Interiors typically featured pale, functional colors on walls, often obscured by dust.
-  scale_dimensions             : Extensive desert landscapes, a small town footprint with residential and industrial structures of modest scale (typically one to two stories), large mining waste dumps, and vast areas of ground-level asbestos deposits spreading across 46,840 hectares. Transported asbestos fibers are microscopic but accumulate in large visible deposits.
-  distinctive_features         : An isolated Australian ghost town in the Pilbara desert, visibly constructed with and heavily contaminated by insidious blue asbestos waste from the 1937-1966 mining era. The pervasive red earth and fine, constantly disturbed asbestos dust are omnipresent, defining the toxic and deserted environment.
-  demographics                 : The population consisted primarily of Australian and European migrant workers (including Spanish and displaced persons) from the 1940s-1960s, working as miners and mill workers, along with their families. Children were present, often playing in contaminated areas. Later, Aboriginal Banjima traditional owners became prominent in advocacy regarding the contaminated 
-  condition_evolution.at_event : A remote, functional mining town with active blue asbestos mining and processing operations. Its infrastructure and residential areas were visibly constructed using asbestos tailings, resulting in pervasive dust and rudimentary, functional buildings.
-  condition_evolution.later    : A deserted ghost town characterized by demolished buildings, permanent barricades blocking access to an officially contaminated area of 46,840 hectares, and extensive asbestos contamination spread by wind and water across the landscape.
+  materials_textures           : Worker houses built from corrugated sheet metal, timber and asbestos-cement sheeting; loose, crumbling fibrous asbestos that shreds into fine powder when handled; compacted asbestos tailings laid as the surface of roads, yards, driveways, the schoolyard, public spaces and the airstrip; fine powdery dust coating people, buildings and the mill; loose tailings dumps 
+  color_palette                : Exterior dominated by intense red earth and red dust under harsh desert light, with blue-grey asbestos tailings surfaces and pale grey dust films over buildings and workers; interiors not documented; surviving family imagery described as sepia-toned.
+  scale_dimensions             : A small, isolated outback mining town with a dirt airstrip sized for small propeller aircraft, three mines in the surrounding gorges, more than three million tonnes of tailings left behind, and an official asbestos management area of 46,840 hectares extending down drainage lines toward the Fortescue River.
+  distinctive_features         : A small mining town in the red Pilbara desert whose own roads, yards, schoolyard and airstrip were paved with blue asbestos tailings, so the poison literally formed the ground people walked and played on; today it is an emptied, demolished, unmapped zone sealed by permanent barricades.
+  demographics                 : Documented workforce of Australian miners and mill workers, post-war European displaced persons assigned under federal work contracts (1948-1951), European recruits from private CSR recruitment trips (from 1950), and Spanish migrant families under the Spain-Australia migration agreement (early 1960s), with wives and young children living in town; mill workers dres
+  condition_evolution.at_event : An operating mining town in the early 1960s: inhabited sheet-metal and asbestos-cement houses, a working mill wrapped in thick dust clouds, trucks dumping tailings to surface roads, yards and the schoolyard, children playing on the ground, and small propeller planes landing on the tailings airstrip.
+  condition_evolution.later    : After mining ended in December 1966 the town was progressively reduced from 1978, its school, nursing post and police station closed and buildings demolished from 1986 to 1992, the airport closed in 1993, power cut in 2006, the town formally abolished and erased from maps and signs in 2007, the last residents gone by 2022-2023 and remaining structures demolished, 
-  • role: Doctor/Health Official | age unknown | era: 1948
-    appearance_canon: a middle-aged health official, likely Australian, with a serious demeanor
-  • role: Spanish Migrant Miner | age 26 | era: 1962
-    appearance_canon: a mid-20s Spanish migrant miner, often working long hours in dusty conditions, potentially appearing fatigued
-  • role: Spanish Migrant Resident | age 26 | era: 1962
-    appearance_canon: a mid-20s Spanish migrant woman, resilient in harsh living conditions, possibly showing signs of fatigue from a complicated childbirth
-  • role: Spanish Migrant Resident | age 26 | era: 1962
-    appearance_canon: a mid-20s Spanish migrant woman, forming friendships in a challenging desert environment
-  • role: Spanish Migrant Miner | age 26 | era: 1962
-    appearance_canon: a mid-20s Spanish migrant miner, working excessively long hours in dangerous conditions, likely appearing dust-covered and exhausted
-  • role: Child Resident | age 7 | era: 1962
-    appearance_canon: a child of early elementary school age, playing in a dusty, asbestos-laden environment, potentially appearing oblivious to danger
-  • role: Television Producer / Wittenoom-born | age 22 | era: 1985
-    appearance_canon: an early-20s Spanish-Australian young adult, looking at his documentation while being questioned by an airport police officer
-  • role: Banjima Elder / Activist | age unknown | era: 2023
-    appearance_canon: an elderly Aboriginal Banjima man, bearing the physical toll of asbestos exposure
-  • role: Lawyer | age unknown | era: 1988
-    appearance_canon: a middle-aged lawyer, determined in legal proceedings regarding corporate accountability
-  • role: Daughter of Migrant Miners | age unknown | era: 1971
-    appearance_canon: a young adult of Spanish descent, having lived in Wittenoom as a child, choosing to remain in Australia
-  • role: Infant Resident | age 0 | era: 1963
-    appearance_canon: an infant born in Wittenoom to Spanish migrant parents
-  • role: Public Health Official | age unknown | era: 1965
-    appearance_canon: a middle-aged health official, likely Australian, sternly addressing safety concerns
-  • role: Industrial Hygienist | age unknown | era: 1966
-    appearance_canon: a middle-aged industrial hygienist, meticulously documenting safety deficiencies
-  • role: CSR Chairman | age unknown | era: 1966
-    appearance_canon: an elderly corporate chairman making a public announcement
-  • role: Minister for Lands | age unknown | era: 2019
-    appearance_canon: a middle-aged Aboriginal Australian government minister, addressing environmental remediation responsibilities
-  • role: UN Rapporteur | age unknown | era: 2023
-    appearance_canon: a middle-aged UN rapporteur, conducting interviews related to environmental contamination
-
-OBJETOS DOCUMENTADOS (mantené la FORMA GENERAL constante entre imágenes;
-la narración puede nombrarlos por metáfora, función o material):
-  • objeto: Asbestos tailings
-    forma: Finely crushed rock and blue asbestos fibers, used as construction material or deposited as waste, appearing as loose granular piles or spread over surfaces, easily disturbed to release fine dust.
-  • objeto: Wittenoom's deserted buildings
-    forma: Shabby structures of corrugated iron, wood, and asbestos cement, often appearing neglected or partially demolished, constructed directly with or heavily contaminated by blue asbestos waste.
+  • role: Prospector and mine owner in Wittenoom and Yampire gorges whose interests were taken over by ABA | age unknown | era: 1937-1943
+    appearance_canon: an adult Australian prospector in rugged bush work clothes and wide-brimmed hat, weathered by outdoor work
+  • role: Prospector and mine partner in Wittenoom and Yampire gorges whose interests were taken over by ABA | age unknown | era: 1937-1943
+    appearance_canon: an adult Australian prospector and mine manager in practical bush work clothes, sun-weathered
+  • role: Public health doctor who warned in writing that dust levels were extremely dangerous | age unknown | era: 1948
+    appearance_canon: an adult Australian government medical officer in a lightweight suit and tie with a serious, concerned demeanor
+  • role: Prime Minister of Australia who described the mine's life as practically unlimited | age unknown | era: 1947
+    appearance_canon: a senior Australian statesman in a formal dark suit with a composed public demeanor
+  • role: Public health doctor who reported a mesothelioma case in a former mill worker | age unknown | era: 1962
+    appearance_canon: a middle-aged Australian public health physician in a shirt and tie with a clinical, attentive demeanor
+  • role: Public Health Commissioner who reprimanded the school principal for covering the schoolyard with tailings | age unknown | era: 1965
+    appearance_canon: a middle-aged Australian senior health official in a suit with a stern, authoritative demeanor
+  • role: Industrial hygienist who described spills, leaks and poor machinery modifications | age unknown | era: 1966
+    appearance_canon: a middle-aged Australian industrial hygienist in shirt sleeves and tie, inspecting machinery with a critical eye
+  • role: CSR chairman who announced the closure of the mining operations | age unknown | era: 1966
+    appearance_canon: a middle-aged Australian corporate executive in a dark tailored suit with a formal boardroom demeanor
+  • role: State premier whose government rejected the parliamentary clean-up report | age unknown | era: 1992
+    appearance_canon: a middle-aged Australian state politician in a dark business suit with a guarded official demeanor
+  • role: Lawyer who obtained the 1988 Wittenoom verdict against the company | age unknown | era: 1988
+    appearance_canon: an adult Australian litigation lawyer in a business suit with a determined courtroom demeanor
+  • role: State minister who argued the responsible companies should pay for remediation | age unknown | era: 2019
+    appearance_canon: a middle-aged Australian state government minister in a modern business suit
+  • role: UN special rapporteur who visited Australia and interviewed a Banjima elder about the contamination | age unknown | era: 2023
+    appearance_canon: a middle-aged international UN human rights expert in modern business attire with an attentive, listening demeanor
+  • role: Banjima elder and activist who spoke about persistent harm and died of mesothelioma | age unknown | era: 2023-2024
+    appearance_canon: an elderly Aboriginal Australian Banjima elder in casual outback clothing with a dignified, weary bearing
+  • role: CEO of the Asbestos Diseases Society of Australia estimating deaths may exceed 4,000 | age unknown | era: 2020s
+    appearance_canon: a middle-aged Australian woman advocate in modern professional attire with an earnest demeanor
+  • role: Spanish migrant miner in Wittenoom, injured in the foot, later died of mesothelioma | age unknown | era: 1962-1963
+    appearance_canon: a young adult Spanish migrant miner in dusty work clothes, in one portrait with a bandaged foot
+  • role: Wife of a Spanish miner and Wittenoom resident who gave birth in the town hospital | age unknown | era: 1962-1963
+    appearance_canon: a young adult Spanish woman in a simple cotton dress, physically weakened after a difficult birth, hopeful but strained
+  • role: Son of a Spanish miner, born in Wittenoom, later a television producer | age unknown | era: 1963-1985
+    appearance_canon: a young adult man of Spanish descent born in Australia, in casual travel clothes at an airport checkpoint
+  • role: Wife of a Spanish miner and Wittenoom resident who gave birth in the town | age unknown | era: 1962-1964
+    appearance_canon: a young adult Spanish mother in a modest cotton dress, caring for small children in the heat and dust
+  • role: Spanish migrant miner in Wittenoom who often worked 16-hour shifts | age unknown | era: 1962-1964
+    appearance_canon: an adult Spanish migrant miner in dust-covered work shirt and trousers, visibly exhausted from long shifts
+  • role: Child of the De Juan-Barroso family who lived in Wittenoom and later recalled it | age unknown | era: 1962-1964
+    appearance_canon: a young Spanish boy in shorts and a cotton shirt, red dust on skin and clothes
+  • role: Son of a Spanish miner born in Wittenoom | age unknown | era: 1963
+    appearance_canon: a newborn infant of Spanish parents wrapped in a light cotton blanket
+  • role: Daughter of a Spanish miner who lived in Wittenoom as a child and remained in Australia | age unknown | era: 1962-1971
+    appearance_canon: a young Spanish girl in a simple cotton frock with dust on her sandals
+
+OBJETOS DOCUMENTADOS: (vacío) — describí cualquier objeto que nombre la narración por su forma física según el relato, sin inventar detalles no dichos.
-  - contemporary clothing (post-2000s)
-  - modern cars (post-1970s)
-  - digital cameras
-  - modern industrial safety equipment (e.g., advanced respirators)
-  - satellite dishes
-  - GPS devices
-  - modern communication technology
+  - contemporary clothing
+  - modern industrial safety equipment in mining-era scenes
+  - hazmat suits and modern respirators before the 1980s
+  - hi-visibility vests
+  - sealed bitumen roads with painted lines
+  - modern SUVs and pickup trucks in mining-era scenes
+  - jet aircraft at the town airstrip
+  - plastic asbestos-hazard warning signs before closure
+  - solar panels and satellite dishes
```


## ch06

### código solo (canon de antes): diff crudo contra F50c

```diff
-  - wittenoom_miners_and_mill_workers: Various European migrant and Australian laborers working in the asbestos mines and processing mill. · Wittenoom, from 1937 to 1966. · APPEARANCE: Physically robust individuals, often appearing fatigued and covered in a pervasive fine dust, with diverse European features. · CLOTHING: Rugged, practical work clothes, heavy-duty trousers and shirts, sometimes wi
-  - spanish_migrant_families: Spanish families who migrated to Wittenoom under government schemes. · Wittenoom, primarily 1958-1966. · APPEARANCE: Adults and children of Southern European descent, appearing resilient and resourceful, adapting to a harsh desert environment, often showing signs of physical strain or everyday weariness. · CLOTHING: Simple, light clothing suitable for a hot, dusty cl
-  - australian_public_health_officials: Doctors, inspectors, and hygienists from Australian public health departments. · Wittenoom and state offices, 1944-1966. · APPEARANCE: Predominantly Caucasian, appearing professional, often with a serious or concerned demeanor due to the health risks. · CLOTHING: Formal or semi-formal attire of the era, such as suits, collared shirts, and ties, or clean uni
-  - australian_government_representatives: Various Australian federal and state government officials, including politicians, committee members, and regulators. · Government offices and occasional visits to Wittenoom, 1940s-2020s. · APPEARANCE: Predominantly Caucasian, appearing authoritative and formal, reflecting their political or administrative roles. · CLOTHING: Formal business attire, includ
-  - csr_corporate_personnel: Executives, managers, and other personnel from Colonial Sugar Refining (CSR) and its subsidiary, Australian Blue Asbestos (ABA). · Corporate offices and Wittenoom, 1937-1966. · APPEARANCE: Predominantly Caucasian, appearing well-dressed and corporate, often with an air of authority, sometimes dismissive of worker concerns. · CLOTHING: Business suits and formal wear, r
-  - banjima_traditional_owners_and_advocates: Indigenous Banjima people, including elders and legal advocates, asserting their rights over contaminated lands. · Wittenoom area and legal forums, 2010s-2020s. · APPEARANCE: Indigenous Australian people, often older, appearing resilient and determined, some bearing the visible or implied health consequences of asbestos exposure. · CLOTHING: Practical
-  - australian_airport_police: Law enforcement personnel working in Australian airports. · Australian airport checkpoint, 1985. · APPEARANCE: Predominantly Caucasian, appearing uniformed and professional. · CLOTHING: Standard police uniform of the mid-1980s, typically including a collared shirt, trousers, and a peaked cap.
+  - wittenoom_miners_and_mill_workers: Various European migrant and Australian laborers working in the asbestos mines and processing mill. · Wittenoom, from 1937 to 1966. · APPEARANCE: Physically robust individuals, often appearing fatigued and covered in a pervasive fine dust, with diverse European features. · CLOTHING: -
+  - spanish_migrant_families: Spanish families who migrated to Wittenoom under government schemes. · Wittenoom, primarily 1958-1966. · APPEARANCE: Adults and children of Southern European descent, appearing resilient and resourceful, adapting to a harsh desert environment, often showing signs of physical strain or everyday weariness. · CLOTHING: -
+  - australian_public_health_officials: Doctors, inspectors, and hygienists from Australian public health departments. · Wittenoom and state offices, 1944-1966. · APPEARANCE: Predominantly Caucasian, appearing professional, often with a serious or concerned demeanor due to the health risks. · CLOTHING: -
+  - australian_government_representatives: Various Australian federal and state government officials, including politicians, committee members, and regulators. · Government offices and occasional visits to Wittenoom, 1940s-2020s. · APPEARANCE: Predominantly Caucasian, appearing authoritative and formal, reflecting their political or administrative roles. · CLOTHING: -
+  - csr_corporate_personnel: Executives, managers, and other personnel from Colonial Sugar Refining (CSR) and its subsidiary, Australian Blue Asbestos (ABA). · Corporate offices and Wittenoom, 1937-1966. · APPEARANCE: Predominantly Caucasian, appearing well-dressed and corporate, often with an air of authority, sometimes dismissive of worker concerns. · CLOTHING: -
+  - banjima_traditional_owners_and_advocates: Indigenous Banjima people, including elders and legal advocates, asserting their rights over contaminated lands. · Wittenoom area and legal forums, 2010s-2020s. · APPEARANCE: Indigenous Australian people, often older, appearing resilient and determined, some bearing the visible or implied health consequences of asbestos exposure. · CLOTHING: -
+  - australian_airport_police: Law enforcement personnel working in Australian airports. · Australian airport checkpoint, 1985. · APPEARANCE: Predominantly Caucasian, appearing uniformed and professional. · CLOTHING: -
```

### canon nuevo: diff por zona

**era**

```diff
--- f50c
+++ f50d
-  clothing              : Miners wore rugged work clothes, often appearing dirty and dusty. Town residents wore practical, light attire suitable for hot desert conditions, including simple dresses, shirts, and shorts. Government and corporate officials wore more formal attire, such as suits, appropriate for their roles and the era.
-  technology            : Analog gauges, basic mining machinery with exposed components, rudimentary processing plants, simple residential appliances (e.g., older refrigerators, stoves), landline telephones, and radios. NO LEDs, NO digital displays, NO smartphones, NO advanced computing devices.
-  vehicles_machinery    : Early to mid-20th century trucks (e.g., for asbestos transport), desert-adapted 4x4 vehicles, passenger cars from the 1940s-1960s. Propeller-driven small aircraft for transport to the remote town. Mining equipment included drills, crushers, and conveyor belt systems.
-  interiors             : Residential interiors were basic and utilitarian, often in houses of corrugated iron, wood, and asbestos cement, prone to dust accumulation. Offices featured simple desks, manual typewriters, and basic filing systems. Public buildings like hospitals had functional, unadorned spaces with period-appropriate medical equipment.
-  forbidden_anachronisms: smartphones, LED screens, contemporary clothing (post-2000s), modern flat panels, modern cars (post-1970s), digital cameras, modern industrial safety equipment (e.g., advanced respirators), satellite dishes, renewable energy installations.
+  period 1967-1992:
+  clothing              : Remaining residents and visitors in 1970s-1980s casual wear; lawyers, judges and politicians in period suits; ill former workers in hospital gowns or casual clothes.
+  technology            : Landline phones, typewriters giving way to early computers in offices, CRT televisions, court and parliamentary paperwork.
+  vehicles_machinery    : 1970s-1980s sedans and four-wheel drives, demolition machinery removing town buildings, no mining machinery operating.
+  interiors             : Shrinking town with closed school, nursing post and police station; courtrooms, parliamentary rooms, migrant family homes in Madrid.
+  period 1993-2026:
+  clothing              : Contemporary casual wear for Banjima traditional owners and activists; modern business attire for lawyers, officials and a UN rapporteur; modern protective coveralls and respirators for anyone inside the zone.
+  technology            : Modern warning signage, permanent barricades, contemporary offices and media equipment.
+  vehicles_machinery    : Modern four-wheel drives stopped outside barricaded access roads; no aircraft at the closed airstrip.
+  interiors             : Modern government offices, legal offices, interview settings with framed old family photographs.
+  forbidden_anachronisms: In mining-era scenes: no modern respirators, hazmat suits, hi-visibility vests or hard hats with modern logos; no sealed bitumen roads with painted lines; no modern four-wheel drives, SUVs or pickup trucks; no jet aircraft at the airstrip; no plastic warning signs or asbestos-hazard pictograms; no mobile phones, digital cameras, computers or LED lighting; no solar panels
```

**grupo**

```diff
--- f50c
+++ f50d
-  - wittenoom_miners_and_mill_workers: Various European migrant and Australian laborers working in the asbestos mines and processing mill. · Wittenoom, from 1937 to 1966. · APPEARANCE: Physically robust individuals, often appearing fatigued and covered in a pervasive fine dust, with diverse European features.
-  - spanish_migrant_families: Spanish families who migrated to Wittenoom under government schemes. · Wittenoom, primarily 1958-1966. · APPEARANCE: Adults and children of Southern European descent, appearing resilient and resourceful, adapting to a harsh desert environment, often showing signs of physical strain or everyday weariness.
-  - australian_public_health_officials: Doctors, inspectors, and hygienists from Australian public health departments. · Wittenoom and state offices, 1944-1966. · APPEARANCE: Predominantly Caucasian, appearing professional, often with a serious or concerned demeanor due to the health risks.
-  - australian_government_representatives: Various Australian federal and state government officials, including politicians, committee members, and regulators. · Government offices and occasional visits to Wittenoom, 1940s-2020s. · APPEARANCE: Predominantly Caucasian, appearing authoritative and formal, reflecting their political or administrative roles.
-  - csr_corporate_personnel: Executives, managers, and other personnel from Colonial Sugar Refining (CSR) and its subsidiary, Australian Blue Asbestos (ABA). · Corporate offices and Wittenoom, 1937-1966. · APPEARANCE: Predominantly Caucasian, appearing well-dressed and corporate, often with an air of authority, sometimes dismissive of worker concerns.
-  - banjima_traditional_owners_and_advocates: Indigenous Banjima people, including elders and legal advocates, asserting their rights over contaminated lands. · Wittenoom area and legal forums, 2010s-2020s. · APPEARANCE: Indigenous Australian people, often older, appearing resilient and determined, some bearing the visible or implied health consequences of asbestos exposure.
-  - australian_airport_police: Law enforcement personnel working in Australian airports. · Australian airport checkpoint, 1985. · APPEARANCE: Predominantly Caucasian, appearing uniformed and professional.
+  - prospectors_mine_owners: Australian prospectors and early mine owners who opened blue asbestos workings in the Hamersley Ranges gorges. · Wittenoom and Yampire gorges, 1937-1943. · APPEARANCE: Australian men of British or Irish descent, fair skin deeply sun-tanned and weathered, short hair, lean wiry build from bush prospecting.
+  - company_managers: Managers and executives of ABA and its parent CSR, a Sydney sugar company with little mining experience, plus town steering committee members. · Wittenoom and corporate offices, 1943-1966. · APPEARANCE: Australian men of British descent, fair complexions, neatly cut and combed hair, office-worker builds.
+  - mine_and_health_officials: Australian state mines inspectors, deputy mining engineers, public health doctors, a health commissioner, health inspectors and an industrial hygienist who reported on the dust. · Wittenoom mine, mill and town and government offices, 1944-1968. · APPEARANCE: Australian men of British descent, fair skin, short neat hair, professional office builds.
+  - mine_and_mill_workers: Asbestos miners, mill hands and fitters: Australian workers, post-war European displaced persons on federal contracts, European recruits from CSR trips, and Spanish migrants. · Wittenoom mines, mill and town, 1937-1966, with a high-turnover workforce throughout. · APPEARANCE: Mixed Australian (British-descended) and Southern, Central and Eastern European men, light to o
+  - spanish_migrant_families: Spanish migrant miners' families from Madrid who came under the Spain-Australia migration agreement, including wives, infants and children, and their later adult children working in media. · Ships via Suez and Wittenoom 1962-1964, Australia until 1971, Madrid from 1966 and 1971, an Australian airport in 1985, and later interviews into the 2020s. · APPEARANCE: Spanish
+  - town_children: Children of miners, including Spanish migrant children, who grew up in the tailings-paved town and played with asbestos. · Wittenoom streets, yards and schoolyard, 1950s-1966. · APPEARANCE: Australian, European and Spanish children with light to olive skin, tanned, tousled hair, dusted with red earth and fine asbestos powder.
+  - union_and_arbitration: Australian Workers' Union representatives, employer advocates and members of the arbitration Board of Reference who negotiated the dust allowance. · Wittenoom mill and arbitration hearings, 1946-1959. · APPEARANCE: Australian men of British descent, fair skin, short neat hair, mixed office and former manual-labour builds.
+  - australian_politicians: Australian prime ministers, state premiers, ministers, parliamentary inquiry leaders and committee chairs dealing with Wittenoom. · Canberra and Perth government and parliament settings, 1947, 1978-1994, 2016-2026. · APPEARANCE: Predominantly Australian men of British descent, fair skin, short groomed hair, middle-aged office builds.
+  - victims_advocates_and_lawyers: Former Wittenoom workers and residents with asbestos disease, the Asbestos Diseases Society of Australia, and the lawyers who litigated against the company and the state. · Perth, courts and offices, 1979-1989 and 2020s-2026. · APPEARANCE: Mixed Australian and European-born adults; ill former workers aged, thin and frail from lung disease.
+  - banjima_traditional_owners: Banjima Aboriginal traditional owners, elders and members of BNTAC whose country includes Wittenoom. · Banjima country around Wittenoom and the Pilbara, 2023-2026. · APPEARANCE: Aboriginal Australian people with dark brown skin, dark curly or wavy hair, elders with grey hair and beards, builds shaped by outdoor life in the Pilbara.
+  - international_un_official: A visiting United Nations special rapporteur investigating toxic contamination. · Australia, meeting Banjima elders, 2023. · APPEARANCE: -
+  - airport_police: Australian airport police officers at a passport and identity checkpoint. · An Australian airport checkpoint, 1985. · APPEARANCE: -
```

**resto**

```diff
--- f50c
+++ f50d
-  materials_textures           : Corrugated iron, wood, asbestos cement, pervasive red earth, blue asbestos waste, fine asbestos dust, loose granular tailings, deposited asbestos fibers, weathered metallic tones, barricade construction materials.
-  color_palette                : Exterior palette dominated by red earth, dusty grey, weathered metallic hues (corrugated iron), and the distinctive blue of asbestos. Interiors typically featured pale, functional colors on walls, often obscured by dust.
-  scale_dimensions             : Extensive desert landscapes, a small town footprint with residential and industrial structures of modest scale (typically one to two stories), large mining waste dumps, and vast areas of ground-level asbestos deposits spreading across 46,840 hectares. Transported asbestos fibers are microscopic but accumulate in large visible deposits.
-  distinctive_features         : An isolated Australian ghost town in the Pilbara desert, visibly constructed with and heavily contaminated by insidious blue asbestos waste from the 1937-1966 mining era. The pervasive red earth and fine, constantly disturbed asbestos dust are omnipresent, defining the toxic and deserted environment.
-  demographics                 : The population consisted primarily of Australian and European migrant workers (including Spanish and displaced persons) from the 1940s-1960s, working as miners and mill workers, along with their families. Children were present, often playing in contaminated areas. Later, Aboriginal Banjima traditional owners became prominent in advocacy regarding the contaminated 
-  condition_evolution.at_event : A remote, functional mining town with active blue asbestos mining and processing operations. Its infrastructure and residential areas were visibly constructed using asbestos tailings, resulting in pervasive dust and rudimentary, functional buildings.
-  condition_evolution.later    : A deserted ghost town characterized by demolished buildings, permanent barricades blocking access to an officially contaminated area of 46,840 hectares, and extensive asbestos contamination spread by wind and water across the landscape.
+  materials_textures           : Worker houses built from corrugated sheet metal, timber and asbestos-cement sheeting; loose, crumbling fibrous asbestos that shreds into fine powder when handled; compacted asbestos tailings laid as the surface of roads, yards, driveways, the schoolyard, public spaces and the airstrip; fine powdery dust coating people, buildings and the mill; loose tailings dumps 
+  color_palette                : Exterior dominated by intense red earth and red dust under harsh desert light, with blue-grey asbestos tailings surfaces and pale grey dust films over buildings and workers; interiors not documented; surviving family imagery described as sepia-toned.
+  scale_dimensions             : A small, isolated outback mining town with a dirt airstrip sized for small propeller aircraft, three mines in the surrounding gorges, more than three million tonnes of tailings left behind, and an official asbestos management area of 46,840 hectares extending down drainage lines toward the Fortescue River.
+  distinctive_features         : A small mining town in the red Pilbara desert whose own roads, yards, schoolyard and airstrip were paved with blue asbestos tailings, so the poison literally formed the ground people walked and played on; today it is an emptied, demolished, unmapped zone sealed by permanent barricades.
+  demographics                 : Documented workforce of Australian miners and mill workers, post-war European displaced persons assigned under federal work contracts (1948-1951), European recruits from private CSR recruitment trips (from 1950), and Spanish migrant families under the Spain-Australia migration agreement (early 1960s), with wives and young children living in town; mill workers dres
+  condition_evolution.at_event : An operating mining town in the early 1960s: inhabited sheet-metal and asbestos-cement houses, a working mill wrapped in thick dust clouds, trucks dumping tailings to surface roads, yards and the schoolyard, children playing on the ground, and small propeller planes landing on the tailings airstrip.
+  condition_evolution.later    : After mining ended in December 1966 the town was progressively reduced from 1978, its school, nursing post and police station closed and buildings demolished from 1986 to 1992, the airport closed in 1993, power cut in 2006, the town formally abolished and erased from maps and signs in 2007, the last residents gone by 2022-2023 and remaining structures demolished, 
-  • role: Doctor/Health Official | age unknown | era: 1948
-    appearance_canon: a middle-aged health official, likely Australian, with a serious demeanor
-  • role: Spanish Migrant Miner | age 26 | era: 1962
-    appearance_canon: a mid-20s Spanish migrant miner, often working long hours in dusty conditions, potentially appearing fatigued
-  • role: Spanish Migrant Resident | age 26 | era: 1962
-    appearance_canon: a mid-20s Spanish migrant woman, resilient in harsh living conditions, possibly showing signs of fatigue from a complicated childbirth
-  • role: Spanish Migrant Resident | age 26 | era: 1962
-    appearance_canon: a mid-20s Spanish migrant woman, forming friendships in a challenging desert environment
-  • role: Spanish Migrant Miner | age 26 | era: 1962
-    appearance_canon: a mid-20s Spanish migrant miner, working excessively long hours in dangerous conditions, likely appearing dust-covered and exhausted
-  • role: Child Resident | age 7 | era: 1962
-    appearance_canon: a child of early elementary school age, playing in a dusty, asbestos-laden environment, potentially appearing oblivious to danger
-  • role: Television Producer / Wittenoom-born | age 22 | era: 1985
-    appearance_canon: an early-20s Spanish-Australian young adult, looking at his documentation while being questioned by an airport police officer
-  • role: Banjima Elder / Activist | age unknown | era: 2023
-    appearance_canon: an elderly Aboriginal Banjima man, bearing the physical toll of asbestos exposure
-  • role: Lawyer | age unknown | era: 1988
-    appearance_canon: a middle-aged lawyer, determined in legal proceedings regarding corporate accountability
-  • role: Daughter of Migrant Miners | age unknown | era: 1971
-    appearance_canon: a young adult of Spanish descent, having lived in Wittenoom as a child, choosing to remain in Australia
-  • role: Infant Resident | age 0 | era: 1963
-    appearance_canon: an infant born in Wittenoom to Spanish migrant parents
-  • role: Public Health Official | age unknown | era: 1965
-    appearance_canon: a middle-aged health official, likely Australian, sternly addressing safety concerns
-  • role: Industrial Hygienist | age unknown | era: 1966
-    appearance_canon: a middle-aged industrial hygienist, meticulously documenting safety deficiencies
-  • role: CSR Chairman | age unknown | era: 1966
-    appearance_canon: an elderly corporate chairman making a public announcement
-  • role: Minister for Lands | age unknown | era: 2019
-    appearance_canon: a middle-aged Aboriginal Australian government minister, addressing environmental remediation responsibilities
-  • role: UN Rapporteur | age unknown | era: 2023
-    appearance_canon: a middle-aged UN rapporteur, conducting interviews related to environmental contamination
-
-OBJETOS DOCUMENTADOS (mantené la FORMA GENERAL constante entre imágenes;
-la narración puede nombrarlos por metáfora, función o material):
-  • objeto: Asbestos tailings
-    forma: Finely crushed rock and blue asbestos fibers, used as construction material or deposited as waste, appearing as loose granular piles or spread over surfaces, easily disturbed to release fine dust.
-  • objeto: Wittenoom's deserted buildings
-    forma: Shabby structures of corrugated iron, wood, and asbestos cement, often appearing neglected or partially demolished, constructed directly with or heavily contaminated by blue asbestos waste.
+  • role: Prospector and mine owner in Wittenoom and Yampire gorges whose interests were taken over by ABA | age unknown | era: 1937-1943
+    appearance_canon: an adult Australian prospector in rugged bush work clothes and wide-brimmed hat, weathered by outdoor work
+  • role: Prospector and mine partner in Wittenoom and Yampire gorges whose interests were taken over by ABA | age unknown | era: 1937-1943
+    appearance_canon: an adult Australian prospector and mine manager in practical bush work clothes, sun-weathered
+  • role: Public health doctor who warned in writing that dust levels were extremely dangerous | age unknown | era: 1948
+    appearance_canon: an adult Australian government medical officer in a lightweight suit and tie with a serious, concerned demeanor
+  • role: Prime Minister of Australia who described the mine's life as practically unlimited | age unknown | era: 1947
+    appearance_canon: a senior Australian statesman in a formal dark suit with a composed public demeanor
+  • role: Public health doctor who reported a mesothelioma case in a former mill worker | age unknown | era: 1962
+    appearance_canon: a middle-aged Australian public health physician in a shirt and tie with a clinical, attentive demeanor
+  • role: Public Health Commissioner who reprimanded the school principal for covering the schoolyard with tailings | age unknown | era: 1965
+    appearance_canon: a middle-aged Australian senior health official in a suit with a stern, authoritative demeanor
+  • role: Industrial hygienist who described spills, leaks and poor machinery modifications | age unknown | era: 1966
+    appearance_canon: a middle-aged Australian industrial hygienist in shirt sleeves and tie, inspecting machinery with a critical eye
+  • role: CSR chairman who announced the closure of the mining operations | age unknown | era: 1966
+    appearance_canon: a middle-aged Australian corporate executive in a dark tailored suit with a formal boardroom demeanor
+  • role: State premier whose government rejected the parliamentary clean-up report | age unknown | era: 1992
+    appearance_canon: a middle-aged Australian state politician in a dark business suit with a guarded official demeanor
+  • role: Lawyer who obtained the 1988 Wittenoom verdict against the company | age unknown | era: 1988
+    appearance_canon: an adult Australian litigation lawyer in a business suit with a determined courtroom demeanor
+  • role: State minister who argued the responsible companies should pay for remediation | age unknown | era: 2019
+    appearance_canon: a middle-aged Australian state government minister in a modern business suit
+  • role: UN special rapporteur who visited Australia and interviewed a Banjima elder about the contamination | age unknown | era: 2023
+    appearance_canon: a middle-aged international UN human rights expert in modern business attire with an attentive, listening demeanor
+  • role: Banjima elder and activist who spoke about persistent harm and died of mesothelioma | age unknown | era: 2023-2024
+    appearance_canon: an elderly Aboriginal Australian Banjima elder in casual outback clothing with a dignified, weary bearing
+  • role: CEO of the Asbestos Diseases Society of Australia estimating deaths may exceed 4,000 | age unknown | era: 2020s
+    appearance_canon: a middle-aged Australian woman advocate in modern professional attire with an earnest demeanor
+  • role: Spanish migrant miner in Wittenoom, injured in the foot, later died of mesothelioma | age unknown | era: 1962-1963
+    appearance_canon: a young adult Spanish migrant miner in dusty work clothes, in one portrait with a bandaged foot
+  • role: Wife of a Spanish miner and Wittenoom resident who gave birth in the town hospital | age unknown | era: 1962-1963
+    appearance_canon: a young adult Spanish woman in a simple cotton dress, physically weakened after a difficult birth, hopeful but strained
+  • role: Son of a Spanish miner, born in Wittenoom, later a television producer | age unknown | era: 1963-1985
+    appearance_canon: a young adult man of Spanish descent born in Australia, in casual travel clothes at an airport checkpoint
+  • role: Wife of a Spanish miner and Wittenoom resident who gave birth in the town | age unknown | era: 1962-1964
+    appearance_canon: a young adult Spanish mother in a modest cotton dress, caring for small children in the heat and dust
+  • role: Spanish migrant miner in Wittenoom who often worked 16-hour shifts | age unknown | era: 1962-1964
+    appearance_canon: an adult Spanish migrant miner in dust-covered work shirt and trousers, visibly exhausted from long shifts
+  • role: Child of the De Juan-Barroso family who lived in Wittenoom and later recalled it | age unknown | era: 1962-1964
+    appearance_canon: a young Spanish boy in shorts and a cotton shirt, red dust on skin and clothes
+  • role: Son of a Spanish miner born in Wittenoom | age unknown | era: 1963
+    appearance_canon: a newborn infant of Spanish parents wrapped in a light cotton blanket
+  • role: Daughter of a Spanish miner who lived in Wittenoom as a child and remained in Australia | age unknown | era: 1962-1971
+    appearance_canon: a young Spanish girl in a simple cotton frock with dust on her sandals
+
+OBJETOS DOCUMENTADOS: (vacío) — describí cualquier objeto que nombre la narración por su forma física según el relato, sin inventar detalles no dichos.
-  - contemporary clothing (post-2000s)
-  - modern cars (post-1970s)
-  - digital cameras
-  - modern industrial safety equipment (e.g., advanced respirators)
-  - satellite dishes
-  - GPS devices
-  - modern communication technology
+  - contemporary clothing
+  - modern industrial safety equipment in mining-era scenes
+  - hazmat suits and modern respirators before the 1980s
+  - hi-visibility vests
+  - sealed bitumen roads with painted lines
+  - modern SUVs and pickup trucks in mining-era scenes
+  - jet aircraft at the town airstrip
+  - plastic asbestos-hazard warning signs before closure
+  - solar panels and satellite dishes
```


## ch07

### código solo (canon de antes): diff crudo contra F50c

```diff
-  - wittenoom_miners_and_mill_workers: Various European migrant and Australian laborers working in the asbestos mines and processing mill. · Wittenoom, from 1937 to 1966. · APPEARANCE: Physically robust individuals, often appearing fatigued and covered in a pervasive fine dust, with diverse European features. · CLOTHING: Rugged, practical work clothes, heavy-duty trousers and shirts, sometimes wi
-  - spanish_migrant_families: Spanish families who migrated to Wittenoom under government schemes. · Wittenoom, primarily 1958-1966. · APPEARANCE: Adults and children of Southern European descent, appearing resilient and resourceful, adapting to a harsh desert environment, often showing signs of physical strain or everyday weariness. · CLOTHING: Simple, light clothing suitable for a hot, dusty cl
-  - australian_public_health_officials: Doctors, inspectors, and hygienists from Australian public health departments. · Wittenoom and state offices, 1944-1966. · APPEARANCE: Predominantly Caucasian, appearing professional, often with a serious or concerned demeanor due to the health risks. · CLOTHING: Formal or semi-formal attire of the era, such as suits, collared shirts, and ties, or clean uni
-  - australian_government_representatives: Various Australian federal and state government officials, including politicians, committee members, and regulators. · Government offices and occasional visits to Wittenoom, 1940s-2020s. · APPEARANCE: Predominantly Caucasian, appearing authoritative and formal, reflecting their political or administrative roles. · CLOTHING: Formal business attire, includ
-  - csr_corporate_personnel: Executives, managers, and other personnel from Colonial Sugar Refining (CSR) and its subsidiary, Australian Blue Asbestos (ABA). · Corporate offices and Wittenoom, 1937-1966. · APPEARANCE: Predominantly Caucasian, appearing well-dressed and corporate, often with an air of authority, sometimes dismissive of worker concerns. · CLOTHING: Business suits and formal wear, r
-  - banjima_traditional_owners_and_advocates: Indigenous Banjima people, including elders and legal advocates, asserting their rights over contaminated lands. · Wittenoom area and legal forums, 2010s-2020s. · APPEARANCE: Indigenous Australian people, often older, appearing resilient and determined, some bearing the visible or implied health consequences of asbestos exposure. · CLOTHING: Practical
-  - australian_airport_police: Law enforcement personnel working in Australian airports. · Australian airport checkpoint, 1985. · APPEARANCE: Predominantly Caucasian, appearing uniformed and professional. · CLOTHING: Standard police uniform of the mid-1980s, typically including a collared shirt, trousers, and a peaked cap.
+  - wittenoom_miners_and_mill_workers: Various European migrant and Australian laborers working in the asbestos mines and processing mill. · Wittenoom, from 1937 to 1966. · APPEARANCE: Physically robust individuals, often appearing fatigued and covered in a pervasive fine dust, with diverse European features. · CLOTHING: -
+  - spanish_migrant_families: Spanish families who migrated to Wittenoom under government schemes. · Wittenoom, primarily 1958-1966. · APPEARANCE: Adults and children of Southern European descent, appearing resilient and resourceful, adapting to a harsh desert environment, often showing signs of physical strain or everyday weariness. · CLOTHING: -
+  - australian_public_health_officials: Doctors, inspectors, and hygienists from Australian public health departments. · Wittenoom and state offices, 1944-1966. · APPEARANCE: Predominantly Caucasian, appearing professional, often with a serious or concerned demeanor due to the health risks. · CLOTHING: -
+  - australian_government_representatives: Various Australian federal and state government officials, including politicians, committee members, and regulators. · Government offices and occasional visits to Wittenoom, 1940s-2020s. · APPEARANCE: Predominantly Caucasian, appearing authoritative and formal, reflecting their political or administrative roles. · CLOTHING: -
+  - csr_corporate_personnel: Executives, managers, and other personnel from Colonial Sugar Refining (CSR) and its subsidiary, Australian Blue Asbestos (ABA). · Corporate offices and Wittenoom, 1937-1966. · APPEARANCE: Predominantly Caucasian, appearing well-dressed and corporate, often with an air of authority, sometimes dismissive of worker concerns. · CLOTHING: -
+  - banjima_traditional_owners_and_advocates: Indigenous Banjima people, including elders and legal advocates, asserting their rights over contaminated lands. · Wittenoom area and legal forums, 2010s-2020s. · APPEARANCE: Indigenous Australian people, often older, appearing resilient and determined, some bearing the visible or implied health consequences of asbestos exposure. · CLOTHING: -
+  - australian_airport_police: Law enforcement personnel working in Australian airports. · Australian airport checkpoint, 1985. · APPEARANCE: Predominantly Caucasian, appearing uniformed and professional. · CLOTHING: -
```

### canon nuevo: diff por zona

**era**

```diff
--- f50c
+++ f50d
-  clothing              : Miners wore rugged work clothes, often appearing dirty and dusty. Town residents wore practical, light attire suitable for hot desert conditions, including simple dresses, shirts, and shorts. Government and corporate officials wore more formal attire, such as suits, appropriate for their roles and the era.
-  technology            : Analog gauges, basic mining machinery with exposed components, rudimentary processing plants, simple residential appliances (e.g., older refrigerators, stoves), landline telephones, and radios. NO LEDs, NO digital displays, NO smartphones, NO advanced computing devices.
-  vehicles_machinery    : Early to mid-20th century trucks (e.g., for asbestos transport), desert-adapted 4x4 vehicles, passenger cars from the 1940s-1960s. Propeller-driven small aircraft for transport to the remote town. Mining equipment included drills, crushers, and conveyor belt systems.
-  interiors             : Residential interiors were basic and utilitarian, often in houses of corrugated iron, wood, and asbestos cement, prone to dust accumulation. Offices featured simple desks, manual typewriters, and basic filing systems. Public buildings like hospitals had functional, unadorned spaces with period-appropriate medical equipment.
-  forbidden_anachronisms: smartphones, LED screens, contemporary clothing (post-2000s), modern flat panels, modern cars (post-1970s), digital cameras, modern industrial safety equipment (e.g., advanced respirators), satellite dishes, renewable energy installations.
+  period 1993-2026:
+  clothing              : Contemporary casual wear for Banjima traditional owners and activists; modern business attire for lawyers, officials and a UN rapporteur; modern protective coveralls and respirators for anyone inside the zone.
+  technology            : Modern warning signage, permanent barricades, contemporary offices and media equipment.
+  vehicles_machinery    : Modern four-wheel drives stopped outside barricaded access roads; no aircraft at the closed airstrip.
+  interiors             : Modern government offices, legal offices, interview settings with framed old family photographs.
+  forbidden_anachronisms: In mining-era scenes: no modern respirators, hazmat suits, hi-visibility vests or hard hats with modern logos; no sealed bitumen roads with painted lines; no modern four-wheel drives, SUVs or pickup trucks; no jet aircraft at the airstrip; no plastic warning signs or asbestos-hazard pictograms; no mobile phones, digital cameras, computers or LED lighting; no solar panels
```

**grupo**

```diff
--- f50c
+++ f50d
-  - wittenoom_miners_and_mill_workers: Various European migrant and Australian laborers working in the asbestos mines and processing mill. · Wittenoom, from 1937 to 1966. · APPEARANCE: Physically robust individuals, often appearing fatigued and covered in a pervasive fine dust, with diverse European features.
-  - spanish_migrant_families: Spanish families who migrated to Wittenoom under government schemes. · Wittenoom, primarily 1958-1966. · APPEARANCE: Adults and children of Southern European descent, appearing resilient and resourceful, adapting to a harsh desert environment, often showing signs of physical strain or everyday weariness.
-  - australian_public_health_officials: Doctors, inspectors, and hygienists from Australian public health departments. · Wittenoom and state offices, 1944-1966. · APPEARANCE: Predominantly Caucasian, appearing professional, often with a serious or concerned demeanor due to the health risks.
-  - australian_government_representatives: Various Australian federal and state government officials, including politicians, committee members, and regulators. · Government offices and occasional visits to Wittenoom, 1940s-2020s. · APPEARANCE: Predominantly Caucasian, appearing authoritative and formal, reflecting their political or administrative roles.
-  - csr_corporate_personnel: Executives, managers, and other personnel from Colonial Sugar Refining (CSR) and its subsidiary, Australian Blue Asbestos (ABA). · Corporate offices and Wittenoom, 1937-1966. · APPEARANCE: Predominantly Caucasian, appearing well-dressed and corporate, often with an air of authority, sometimes dismissive of worker concerns.
-  - banjima_traditional_owners_and_advocates: Indigenous Banjima people, including elders and legal advocates, asserting their rights over contaminated lands. · Wittenoom area and legal forums, 2010s-2020s. · APPEARANCE: Indigenous Australian people, often older, appearing resilient and determined, some bearing the visible or implied health consequences of asbestos exposure.
-  - australian_airport_police: Law enforcement personnel working in Australian airports. · Australian airport checkpoint, 1985. · APPEARANCE: Predominantly Caucasian, appearing uniformed and professional.
+  - prospectors_mine_owners: Australian prospectors and early mine owners who opened blue asbestos workings in the Hamersley Ranges gorges. · Wittenoom and Yampire gorges, 1937-1943. · APPEARANCE: Australian men of British or Irish descent, fair skin deeply sun-tanned and weathered, short hair, lean wiry build from bush prospecting.
+  - company_managers: Managers and executives of ABA and its parent CSR, a Sydney sugar company with little mining experience, plus town steering committee members. · Wittenoom and corporate offices, 1943-1966. · APPEARANCE: Australian men of British descent, fair complexions, neatly cut and combed hair, office-worker builds.
+  - mine_and_health_officials: Australian state mines inspectors, deputy mining engineers, public health doctors, a health commissioner, health inspectors and an industrial hygienist who reported on the dust. · Wittenoom mine, mill and town and government offices, 1944-1968. · APPEARANCE: Australian men of British descent, fair skin, short neat hair, professional office builds.
+  - mine_and_mill_workers: Asbestos miners, mill hands and fitters: Australian workers, post-war European displaced persons on federal contracts, European recruits from CSR trips, and Spanish migrants. · Wittenoom mines, mill and town, 1937-1966, with a high-turnover workforce throughout. · APPEARANCE: Mixed Australian (British-descended) and Southern, Central and Eastern European men, light to o
+  - spanish_migrant_families: Spanish migrant miners' families from Madrid who came under the Spain-Australia migration agreement, including wives, infants and children, and their later adult children working in media. · Ships via Suez and Wittenoom 1962-1964, Australia until 1971, Madrid from 1966 and 1971, an Australian airport in 1985, and later interviews into the 2020s. · APPEARANCE: Spanish
+  - town_children: Children of miners, including Spanish migrant children, who grew up in the tailings-paved town and played with asbestos. · Wittenoom streets, yards and schoolyard, 1950s-1966. · APPEARANCE: Australian, European and Spanish children with light to olive skin, tanned, tousled hair, dusted with red earth and fine asbestos powder.
+  - union_and_arbitration: Australian Workers' Union representatives, employer advocates and members of the arbitration Board of Reference who negotiated the dust allowance. · Wittenoom mill and arbitration hearings, 1946-1959. · APPEARANCE: Australian men of British descent, fair skin, short neat hair, mixed office and former manual-labour builds.
+  - australian_politicians: Australian prime ministers, state premiers, ministers, parliamentary inquiry leaders and committee chairs dealing with Wittenoom. · Canberra and Perth government and parliament settings, 1947, 1978-1994, 2016-2026. · APPEARANCE: Predominantly Australian men of British descent, fair skin, short groomed hair, middle-aged office builds.
+  - victims_advocates_and_lawyers: Former Wittenoom workers and residents with asbestos disease, the Asbestos Diseases Society of Australia, and the lawyers who litigated against the company and the state. · Perth, courts and offices, 1979-1989 and 2020s-2026. · APPEARANCE: Mixed Australian and European-born adults; ill former workers aged, thin and frail from lung disease.
+  - banjima_traditional_owners: Banjima Aboriginal traditional owners, elders and members of BNTAC whose country includes Wittenoom. · Banjima country around Wittenoom and the Pilbara, 2023-2026. · APPEARANCE: Aboriginal Australian people with dark brown skin, dark curly or wavy hair, elders with grey hair and beards, builds shaped by outdoor life in the Pilbara.
+  - international_un_official: A visiting United Nations special rapporteur investigating toxic contamination. · Australia, meeting Banjima elders, 2023. · APPEARANCE: -
+  - airport_police: Australian airport police officers at a passport and identity checkpoint. · An Australian airport checkpoint, 1985. · APPEARANCE: -
```

**resto**

```diff
--- f50c
+++ f50d
-  materials_textures           : Corrugated iron, wood, asbestos cement, pervasive red earth, blue asbestos waste, fine asbestos dust, loose granular tailings, deposited asbestos fibers, weathered metallic tones, barricade construction materials.
-  color_palette                : Exterior palette dominated by red earth, dusty grey, weathered metallic hues (corrugated iron), and the distinctive blue of asbestos. Interiors typically featured pale, functional colors on walls, often obscured by dust.
-  scale_dimensions             : Extensive desert landscapes, a small town footprint with residential and industrial structures of modest scale (typically one to two stories), large mining waste dumps, and vast areas of ground-level asbestos deposits spreading across 46,840 hectares. Transported asbestos fibers are microscopic but accumulate in large visible deposits.
-  distinctive_features         : An isolated Australian ghost town in the Pilbara desert, visibly constructed with and heavily contaminated by insidious blue asbestos waste from the 1937-1966 mining era. The pervasive red earth and fine, constantly disturbed asbestos dust are omnipresent, defining the toxic and deserted environment.
-  demographics                 : The population consisted primarily of Australian and European migrant workers (including Spanish and displaced persons) from the 1940s-1960s, working as miners and mill workers, along with their families. Children were present, often playing in contaminated areas. Later, Aboriginal Banjima traditional owners became prominent in advocacy regarding the contaminated 
-  condition_evolution.at_event : A remote, functional mining town with active blue asbestos mining and processing operations. Its infrastructure and residential areas were visibly constructed using asbestos tailings, resulting in pervasive dust and rudimentary, functional buildings.
-  condition_evolution.later    : A deserted ghost town characterized by demolished buildings, permanent barricades blocking access to an officially contaminated area of 46,840 hectares, and extensive asbestos contamination spread by wind and water across the landscape.
+  materials_textures           : Worker houses built from corrugated sheet metal, timber and asbestos-cement sheeting; loose, crumbling fibrous asbestos that shreds into fine powder when handled; compacted asbestos tailings laid as the surface of roads, yards, driveways, the schoolyard, public spaces and the airstrip; fine powdery dust coating people, buildings and the mill; loose tailings dumps 
+  color_palette                : Exterior dominated by intense red earth and red dust under harsh desert light, with blue-grey asbestos tailings surfaces and pale grey dust films over buildings and workers; interiors not documented; surviving family imagery described as sepia-toned.
+  scale_dimensions             : A small, isolated outback mining town with a dirt airstrip sized for small propeller aircraft, three mines in the surrounding gorges, more than three million tonnes of tailings left behind, and an official asbestos management area of 46,840 hectares extending down drainage lines toward the Fortescue River.
+  distinctive_features         : A small mining town in the red Pilbara desert whose own roads, yards, schoolyard and airstrip were paved with blue asbestos tailings, so the poison literally formed the ground people walked and played on; today it is an emptied, demolished, unmapped zone sealed by permanent barricades.
+  demographics                 : Documented workforce of Australian miners and mill workers, post-war European displaced persons assigned under federal work contracts (1948-1951), European recruits from private CSR recruitment trips (from 1950), and Spanish migrant families under the Spain-Australia migration agreement (early 1960s), with wives and young children living in town; mill workers dres
+  condition_evolution.at_event : An operating mining town in the early 1960s: inhabited sheet-metal and asbestos-cement houses, a working mill wrapped in thick dust clouds, trucks dumping tailings to surface roads, yards and the schoolyard, children playing on the ground, and small propeller planes landing on the tailings airstrip.
+  condition_evolution.later    : After mining ended in December 1966 the town was progressively reduced from 1978, its school, nursing post and police station closed and buildings demolished from 1986 to 1992, the airport closed in 1993, power cut in 2006, the town formally abolished and erased from maps and signs in 2007, the last residents gone by 2022-2023 and remaining structures demolished, 
-  • role: Doctor/Health Official | age unknown | era: 1948
-    appearance_canon: a middle-aged health official, likely Australian, with a serious demeanor
-  • role: Spanish Migrant Miner | age 26 | era: 1962
-    appearance_canon: a mid-20s Spanish migrant miner, often working long hours in dusty conditions, potentially appearing fatigued
-  • role: Spanish Migrant Resident | age 26 | era: 1962
-    appearance_canon: a mid-20s Spanish migrant woman, resilient in harsh living conditions, possibly showing signs of fatigue from a complicated childbirth
-  • role: Spanish Migrant Resident | age 26 | era: 1962
-    appearance_canon: a mid-20s Spanish migrant woman, forming friendships in a challenging desert environment
-  • role: Spanish Migrant Miner | age 26 | era: 1962
-    appearance_canon: a mid-20s Spanish migrant miner, working excessively long hours in dangerous conditions, likely appearing dust-covered and exhausted
-  • role: Child Resident | age 7 | era: 1962
-    appearance_canon: a child of early elementary school age, playing in a dusty, asbestos-laden environment, potentially appearing oblivious to danger
-  • role: Television Producer / Wittenoom-born | age 22 | era: 1985
-    appearance_canon: an early-20s Spanish-Australian young adult, looking at his documentation while being questioned by an airport police officer
-  • role: Banjima Elder / Activist | age unknown | era: 2023
-    appearance_canon: an elderly Aboriginal Banjima man, bearing the physical toll of asbestos exposure
-  • role: Lawyer | age unknown | era: 1988
-    appearance_canon: a middle-aged lawyer, determined in legal proceedings regarding corporate accountability
-  • role: Daughter of Migrant Miners | age unknown | era: 1971
-    appearance_canon: a young adult of Spanish descent, having lived in Wittenoom as a child, choosing to remain in Australia
-  • role: Infant Resident | age 0 | era: 1963
-    appearance_canon: an infant born in Wittenoom to Spanish migrant parents
-  • role: Public Health Official | age unknown | era: 1965
-    appearance_canon: a middle-aged health official, likely Australian, sternly addressing safety concerns
-  • role: Industrial Hygienist | age unknown | era: 1966
-    appearance_canon: a middle-aged industrial hygienist, meticulously documenting safety deficiencies
-  • role: CSR Chairman | age unknown | era: 1966
-    appearance_canon: an elderly corporate chairman making a public announcement
-  • role: Minister for Lands | age unknown | era: 2019
-    appearance_canon: a middle-aged Aboriginal Australian government minister, addressing environmental remediation responsibilities
-  • role: UN Rapporteur | age unknown | era: 2023
-    appearance_canon: a middle-aged UN rapporteur, conducting interviews related to environmental contamination
-
-OBJETOS DOCUMENTADOS (mantené la FORMA GENERAL constante entre imágenes;
-la narración puede nombrarlos por metáfora, función o material):
-  • objeto: Asbestos tailings
-    forma: Finely crushed rock and blue asbestos fibers, used as construction material or deposited as waste, appearing as loose granular piles or spread over surfaces, easily disturbed to release fine dust.
-  • objeto: Wittenoom's deserted buildings
-    forma: Shabby structures of corrugated iron, wood, and asbestos cement, often appearing neglected or partially demolished, constructed directly with or heavily contaminated by blue asbestos waste.
+  • role: Prospector and mine owner in Wittenoom and Yampire gorges whose interests were taken over by ABA | age unknown | era: 1937-1943
+    appearance_canon: an adult Australian prospector in rugged bush work clothes and wide-brimmed hat, weathered by outdoor work
+  • role: Prospector and mine partner in Wittenoom and Yampire gorges whose interests were taken over by ABA | age unknown | era: 1937-1943
+    appearance_canon: an adult Australian prospector and mine manager in practical bush work clothes, sun-weathered
+  • role: Public health doctor who warned in writing that dust levels were extremely dangerous | age unknown | era: 1948
+    appearance_canon: an adult Australian government medical officer in a lightweight suit and tie with a serious, concerned demeanor
+  • role: Prime Minister of Australia who described the mine's life as practically unlimited | age unknown | era: 1947
+    appearance_canon: a senior Australian statesman in a formal dark suit with a composed public demeanor
+  • role: Public health doctor who reported a mesothelioma case in a former mill worker | age unknown | era: 1962
+    appearance_canon: a middle-aged Australian public health physician in a shirt and tie with a clinical, attentive demeanor
+  • role: Public Health Commissioner who reprimanded the school principal for covering the schoolyard with tailings | age unknown | era: 1965
+    appearance_canon: a middle-aged Australian senior health official in a suit with a stern, authoritative demeanor
+  • role: Industrial hygienist who described spills, leaks and poor machinery modifications | age unknown | era: 1966
+    appearance_canon: a middle-aged Australian industrial hygienist in shirt sleeves and tie, inspecting machinery with a critical eye
+  • role: CSR chairman who announced the closure of the mining operations | age unknown | era: 1966
+    appearance_canon: a middle-aged Australian corporate executive in a dark tailored suit with a formal boardroom demeanor
+  • role: State premier whose government rejected the parliamentary clean-up report | age unknown | era: 1992
+    appearance_canon: a middle-aged Australian state politician in a dark business suit with a guarded official demeanor
+  • role: Lawyer who obtained the 1988 Wittenoom verdict against the company | age unknown | era: 1988
+    appearance_canon: an adult Australian litigation lawyer in a business suit with a determined courtroom demeanor
+  • role: State minister who argued the responsible companies should pay for remediation | age unknown | era: 2019
+    appearance_canon: a middle-aged Australian state government minister in a modern business suit
+  • role: UN special rapporteur who visited Australia and interviewed a Banjima elder about the contamination | age unknown | era: 2023
+    appearance_canon: a middle-aged international UN human rights expert in modern business attire with an attentive, listening demeanor
+  • role: Banjima elder and activist who spoke about persistent harm and died of mesothelioma | age unknown | era: 2023-2024
+    appearance_canon: an elderly Aboriginal Australian Banjima elder in casual outback clothing with a dignified, weary bearing
+  • role: CEO of the Asbestos Diseases Society of Australia estimating deaths may exceed 4,000 | age unknown | era: 2020s
+    appearance_canon: a middle-aged Australian woman advocate in modern professional attire with an earnest demeanor
+  • role: Spanish migrant miner in Wittenoom, injured in the foot, later died of mesothelioma | age unknown | era: 1962-1963
+    appearance_canon: a young adult Spanish migrant miner in dusty work clothes, in one portrait with a bandaged foot
+  • role: Wife of a Spanish miner and Wittenoom resident who gave birth in the town hospital | age unknown | era: 1962-1963
+    appearance_canon: a young adult Spanish woman in a simple cotton dress, physically weakened after a difficult birth, hopeful but strained
+  • role: Son of a Spanish miner, born in Wittenoom, later a television producer | age unknown | era: 1963-1985
+    appearance_canon: a young adult man of Spanish descent born in Australia, in casual travel clothes at an airport checkpoint
+  • role: Wife of a Spanish miner and Wittenoom resident who gave birth in the town | age unknown | era: 1962-1964
+    appearance_canon: a young adult Spanish mother in a modest cotton dress, caring for small children in the heat and dust
+  • role: Spanish migrant miner in Wittenoom who often worked 16-hour shifts | age unknown | era: 1962-1964
+    appearance_canon: an adult Spanish migrant miner in dust-covered work shirt and trousers, visibly exhausted from long shifts
+  • role: Child of the De Juan-Barroso family who lived in Wittenoom and later recalled it | age unknown | era: 1962-1964
+    appearance_canon: a young Spanish boy in shorts and a cotton shirt, red dust on skin and clothes
+  • role: Son of a Spanish miner born in Wittenoom | age unknown | era: 1963
+    appearance_canon: a newborn infant of Spanish parents wrapped in a light cotton blanket
+  • role: Daughter of a Spanish miner who lived in Wittenoom as a child and remained in Australia | age unknown | era: 1962-1971
+    appearance_canon: a young Spanish girl in a simple cotton frock with dust on her sandals
+
+OBJETOS DOCUMENTADOS: (vacío) — describí cualquier objeto que nombre la narración por su forma física según el relato, sin inventar detalles no dichos.
-  - contemporary clothing (post-2000s)
-  - modern cars (post-1970s)
-  - digital cameras
-  - modern industrial safety equipment (e.g., advanced respirators)
-  - satellite dishes
-  - GPS devices
-  - modern communication technology
+  - contemporary clothing
+  - modern industrial safety equipment in mining-era scenes
+  - hazmat suits and modern respirators before the 1980s
+  - hi-visibility vests
+  - sealed bitumen roads with painted lines
+  - modern SUVs and pickup trucks in mining-era scenes
+  - jet aircraft at the town airstrip
+  - plastic asbestos-hazard warning signs before closure
+  - solar panels and satellite dishes
```
