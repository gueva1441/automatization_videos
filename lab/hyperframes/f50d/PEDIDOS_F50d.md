# PEDIDOS_F50d — los 7 pedidos de casilleros con la época por tramo (en seco)

Salida de `python lab/hyperframes/f50d/pedidos_f50d.py`. Código de F50d con la llamada a Opus cortada. Referencia: `lab/hyperframes/f50c/pedidos/`. Zonas: «era» = bloque ERA del canon (hasta LUGAR PUNTUAL); «grupo» = las líneas de PEOPLE GROUPS sin su parte CLOTHING; «resto» = todo lo demás.

| cap | años de las fotos | periods que entran | canon nuevo: líneas era / grupo / resto | canon nuevo: fuera del canon entero y de los grupos | grupos | código solo: era / grupo / resto (líneas crudas) |
|---|---|---|---|---:|---:|---|
| 1 | 1961 1962 | 1958-1966 | 13 / 20 / 87 | 0 | 11 | 0 / 0 / 0 (14) |
| 2 | 1961 1962 | 1958-1966 | 13 / 20 / 87 | 0 | 11 | 0 / 0 / 0 (14) |
| 3 | 1943 1944 1946 1948 1957 1961 1962 | 1937-1957 · 1958-1966 | 18 / 20 / 87 | 0 | 11 | 0 / 0 / 0 (14) |
| 4 | 1961 1963 | 1958-1966 | 13 / 20 / 87 | 0 | 11 | 0 / 0 / 0 (14) |
| 5 | 1963 1966 1971 1978 1985 1986 1991 1993 | 1958-1966 | 13 / 20 / 87 | 0 | 11 | 0 / 0 / 0 (14) |
| 6 | 1988 1989 1991 1992 2007 2016 | 1958-1966 | 13 / 20 / 87 | 0 | 11 | 0 / 0 / 0 (14) |
| 7 | 2021 2023 2024 | 1958-1966 | 13 / 20 / 87 | 0 | 11 | 0 / 0 / 0 (14) |

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
+  period 1958-1966:
+  clothing              : Similar workwear for miners, but with some attempts at dust protection; civilian clothing adapted to evolving 1960s styles, still practical for the desert.
+  technology            : Larger-scale mining equipment, introduction of some dust reduction machinery. More common use of landline phones. Early televisions in some homes.
+  vehicles_machinery    : A greater variety of 1950s-1960s trucks and utility vehicles. More modern (for the era) passenger cars. Small propeller aircraft for regional transport.
+  interiors             : Slightly more established home interiors reflecting mid-century styles, though still basic. Mill interiors remained heavily dusty despite mitigation efforts.
+  forbidden_anachronisms: smartphones, LED screens, contemporary clothing (post-2000s), modern flat panels, modern industrial safety equipment, GPS devices, digital cameras, plastic water bottles, modern construction machinery, satellite dishes, modern vehicles post-1970s, advanced personal protective equipment.
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
+  - mine_workers: Predominantly Australian and European migrant men working in the asbestos mines and mill. · Wittenoom, Australia, 1937-1966. · APPEARANCE: Predominantly Caucasian, diverse European ethnicities, dusty and fatigued complexion, often lean build from manual labor.
+  - spanish_migrant_miners: Spanish men recruited for work in the Wittenoom asbestos mines and mill. · Wittenoom, Australia, 1958-1966. · APPEARANCE: Southern European features, often sun-tanned complexion, dusty, physically robust from labor.
+  - wittenoom_residents: Australian and European migrant civilians living in the Wittenoom town. · Wittenoom, Australia, 1937-1978. · APPEARANCE: Diverse Caucasian ethnicities, generally sun-exposed and adapted to desert life.
+  - spanish_migrant_families: Spanish migrant men, women, and children living in Wittenoom, often related to miners. · Wittenoom, Australia, 1962-1971. · APPEARANCE: Southern European features, often sun-exposed. Women and children with practical, modest hairstyles.
+  - wittenoom_children: Children of Australian and European migrant families residing in Wittenoom. · Wittenoom, Australia, 1937-1966. · APPEARANCE: Diverse Caucasian children, often covered in dust, sometimes with signs of play in harsh conditions.
+  - government_officials: Various government roles including mining inspectors, state engineers, public health officials, parliamentary investigators, and ministers. · Wittenoom and various government offices in Australia, 1944-2026. · APPEARANCE: Predominantly Caucasian, well-groomed, formal or semi-formal appearance reflecting their professional roles.
+  - corporate_executives: Executives and managers from companies like ABA and CSR. · Corporate offices and Wittenoom, Australia, 1943-1966. · APPEARANCE: Predominantly Caucasian, well-dressed, confident demeanor.
+  - public_health_professionals: Doctors, industrial hygienists, and other medical/scientific personnel involved in assessing health risks. · Wittenoom and medical/government facilities, 1948-1966. · APPEARANCE: Predominantly Caucasian, professional and academic appearance, serious demeanor.
+  - indigenous_activists: Banjima elders and traditional owners advocating for remediation. · Wittenoom area, Australia, and legal/activist settings, 2023-2026. · APPEARANCE: Indigenous Australian features, often elderly, with expressions of concern and determination.
+  - legal_professionals: Lawyers representing victims and other legal personnel. · Courts and legal offices in Australia, 1988-2026. · APPEARANCE: Diverse, formal and professional appearance, clean-cut.
+  - asbestos_victims_advocates: Individuals and leaders involved in the Asbestos Diseases Society of Australia. · Australia, 1979-present. · APPEARANCE: Diverse, often former residents or their families, reflecting determination and resilience.
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
+  materials_textures           : Weathered corrugated iron, wood, fiber-cement sheeting, red earth, fine pervasive dust, and visible blue asbestos tailings used in construction for roads, yards, and buildings.
+  color_palette                : Exterior dominated by dusty red earth and blue asbestos accents, with weathered browns, greys, and muted tones of corrugated iron and timber structures. Interiors likely had simple, light-colored walls to reflect heat, quickly covered in dust.
+  scale_dimensions             : The subject is an isolated, sprawling ghost town, characterized by deserted buildings and extensive roads within a vast area covering 46,840 hectares, with remnants of mining operations and contaminated landscapes.
+  distinctive_features         : An isolated Australian desert ghost town, uniquely defined by its visible construction from insidious blue asbestos waste from the 1937-1966 mining era, now a vast, toxic, and permanently barricaded forbidden zone.
+  demographics                 : The population primarily consisted of Australian workers and families during the early mining phase, later supplemented by European migrants, notably Spanish, recruited for mining labor. Workers were mostly men, with families residing in the town.
+  condition_evolution.at_event : During its active mining period (1937-1966), Wittenoom was a functional but extremely dusty mining town, with buildings and infrastructure visibly constructed using blue asbestos tailings. Despite evident health risks, operations continued.
+  condition_evolution.later    : Post-1966, Wittenoom gradually became an abandoned ghost town. Buildings were demolished between 1986 and 2007, services were disconnected, and access was permanently barricaded. The area remains a vast, toxic zone with asbestos spread by wind and water, declared unsafe for human occupation.
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
+  • role: Medical inspector / Public health doctor | age unknown | era: 1948
+    appearance_canon: a middle-aged medical inspector with a concerned demeanor
+  • role: Spanish migrant miner | age 26 | era: 1962
+    appearance_canon: an early-20s Spanish migrant miner, likely with a bandaged foot from an injury
+  • role: Spanish migrant wife and Wittenoom resident | age unknown | era: 1962
+    appearance_canon: a young adult Spanish migrant woman, often in family photos, potentially weakened after a complicated childbirth
+  • role: Spanish migrant wife and Wittenoom resident | age unknown | era: 1962
+    appearance_canon: a young adult Spanish migrant woman, friend of Maria Bernal
+  • role: Spanish migrant miner | age unknown | era: 1962
+    appearance_canon: a young adult Spanish migrant miner, working long shifts
+  • role: Child resident of Wittenoom | age unknown | era: 1962
+    appearance_canon: a young child, playing with asbestos material
+  • role: Infant resident of Wittenoom | age 0 | era: 1963
+    appearance_canon: an infant born in Wittenoom, subject of a baptism photo
+  • role: Banjima elder, activist, mesotelioma victim | age unknown | era: 2023
+    appearance_canon: an elderly Indigenous Australian man, activist for land remediation
+  • role: Lawyer for asbestos victims | age unknown | era: 1988
+    appearance_canon: a middle-aged lawyer with a determined demeanor
-    appearance_canon: an elderly corporate chairman making a public announcement
+    appearance_canon: a middle-aged corporate chairman announcing the mine closure
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
+    appearance_canon: a middle-aged government minister discussing remediation costs
+  • role: UN Special Rapporteur | age unknown | era: 2023
+    appearance_canon: a middle-aged UN rapporteur investigating environmental damage
+
+OBJETOS DOCUMENTADOS: (vacío) — describí cualquier objeto que nombre la narración por su forma física según el relato, sin inventar detalles no dichos.
-  - modern cars (post-1970s)
+  - modern industrial safety equipment (e.g., hazmat suits)
+  - GPS devices
-  - modern industrial safety equipment (e.g., advanced respirators)
+  - plastic water bottles
+  - modern construction machinery (e.g., large excavators)
-  - GPS devices
-  - modern communication technology
+  - vehicles post-1970s
+  - advanced personal protective equipment
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
+  period 1958-1966:
+  clothing              : Similar workwear for miners, but with some attempts at dust protection; civilian clothing adapted to evolving 1960s styles, still practical for the desert.
+  technology            : Larger-scale mining equipment, introduction of some dust reduction machinery. More common use of landline phones. Early televisions in some homes.
+  vehicles_machinery    : A greater variety of 1950s-1960s trucks and utility vehicles. More modern (for the era) passenger cars. Small propeller aircraft for regional transport.
+  interiors             : Slightly more established home interiors reflecting mid-century styles, though still basic. Mill interiors remained heavily dusty despite mitigation efforts.
+  forbidden_anachronisms: smartphones, LED screens, contemporary clothing (post-2000s), modern flat panels, modern industrial safety equipment, GPS devices, digital cameras, plastic water bottles, modern construction machinery, satellite dishes, modern vehicles post-1970s, advanced personal protective equipment.
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
+  - mine_workers: Predominantly Australian and European migrant men working in the asbestos mines and mill. · Wittenoom, Australia, 1937-1966. · APPEARANCE: Predominantly Caucasian, diverse European ethnicities, dusty and fatigued complexion, often lean build from manual labor.
+  - spanish_migrant_miners: Spanish men recruited for work in the Wittenoom asbestos mines and mill. · Wittenoom, Australia, 1958-1966. · APPEARANCE: Southern European features, often sun-tanned complexion, dusty, physically robust from labor.
+  - wittenoom_residents: Australian and European migrant civilians living in the Wittenoom town. · Wittenoom, Australia, 1937-1978. · APPEARANCE: Diverse Caucasian ethnicities, generally sun-exposed and adapted to desert life.
+  - spanish_migrant_families: Spanish migrant men, women, and children living in Wittenoom, often related to miners. · Wittenoom, Australia, 1962-1971. · APPEARANCE: Southern European features, often sun-exposed. Women and children with practical, modest hairstyles.
+  - wittenoom_children: Children of Australian and European migrant families residing in Wittenoom. · Wittenoom, Australia, 1937-1966. · APPEARANCE: Diverse Caucasian children, often covered in dust, sometimes with signs of play in harsh conditions.
+  - government_officials: Various government roles including mining inspectors, state engineers, public health officials, parliamentary investigators, and ministers. · Wittenoom and various government offices in Australia, 1944-2026. · APPEARANCE: Predominantly Caucasian, well-groomed, formal or semi-formal appearance reflecting their professional roles.
+  - corporate_executives: Executives and managers from companies like ABA and CSR. · Corporate offices and Wittenoom, Australia, 1943-1966. · APPEARANCE: Predominantly Caucasian, well-dressed, confident demeanor.
+  - public_health_professionals: Doctors, industrial hygienists, and other medical/scientific personnel involved in assessing health risks. · Wittenoom and medical/government facilities, 1948-1966. · APPEARANCE: Predominantly Caucasian, professional and academic appearance, serious demeanor.
+  - indigenous_activists: Banjima elders and traditional owners advocating for remediation. · Wittenoom area, Australia, and legal/activist settings, 2023-2026. · APPEARANCE: Indigenous Australian features, often elderly, with expressions of concern and determination.
+  - legal_professionals: Lawyers representing victims and other legal personnel. · Courts and legal offices in Australia, 1988-2026. · APPEARANCE: Diverse, formal and professional appearance, clean-cut.
+  - asbestos_victims_advocates: Individuals and leaders involved in the Asbestos Diseases Society of Australia. · Australia, 1979-present. · APPEARANCE: Diverse, often former residents or their families, reflecting determination and resilience.
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
+  materials_textures           : Weathered corrugated iron, wood, fiber-cement sheeting, red earth, fine pervasive dust, and visible blue asbestos tailings used in construction for roads, yards, and buildings.
+  color_palette                : Exterior dominated by dusty red earth and blue asbestos accents, with weathered browns, greys, and muted tones of corrugated iron and timber structures. Interiors likely had simple, light-colored walls to reflect heat, quickly covered in dust.
+  scale_dimensions             : The subject is an isolated, sprawling ghost town, characterized by deserted buildings and extensive roads within a vast area covering 46,840 hectares, with remnants of mining operations and contaminated landscapes.
+  distinctive_features         : An isolated Australian desert ghost town, uniquely defined by its visible construction from insidious blue asbestos waste from the 1937-1966 mining era, now a vast, toxic, and permanently barricaded forbidden zone.
+  demographics                 : The population primarily consisted of Australian workers and families during the early mining phase, later supplemented by European migrants, notably Spanish, recruited for mining labor. Workers were mostly men, with families residing in the town.
+  condition_evolution.at_event : During its active mining period (1937-1966), Wittenoom was a functional but extremely dusty mining town, with buildings and infrastructure visibly constructed using blue asbestos tailings. Despite evident health risks, operations continued.
+  condition_evolution.later    : Post-1966, Wittenoom gradually became an abandoned ghost town. Buildings were demolished between 1986 and 2007, services were disconnected, and access was permanently barricaded. The area remains a vast, toxic zone with asbestos spread by wind and water, declared unsafe for human occupation.
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
+  • role: Medical inspector / Public health doctor | age unknown | era: 1948
+    appearance_canon: a middle-aged medical inspector with a concerned demeanor
+  • role: Spanish migrant miner | age 26 | era: 1962
+    appearance_canon: an early-20s Spanish migrant miner, likely with a bandaged foot from an injury
+  • role: Spanish migrant wife and Wittenoom resident | age unknown | era: 1962
+    appearance_canon: a young adult Spanish migrant woman, often in family photos, potentially weakened after a complicated childbirth
+  • role: Spanish migrant wife and Wittenoom resident | age unknown | era: 1962
+    appearance_canon: a young adult Spanish migrant woman, friend of Maria Bernal
+  • role: Spanish migrant miner | age unknown | era: 1962
+    appearance_canon: a young adult Spanish migrant miner, working long shifts
+  • role: Child resident of Wittenoom | age unknown | era: 1962
+    appearance_canon: a young child, playing with asbestos material
+  • role: Infant resident of Wittenoom | age 0 | era: 1963
+    appearance_canon: an infant born in Wittenoom, subject of a baptism photo
+  • role: Banjima elder, activist, mesotelioma victim | age unknown | era: 2023
+    appearance_canon: an elderly Indigenous Australian man, activist for land remediation
+  • role: Lawyer for asbestos victims | age unknown | era: 1988
+    appearance_canon: a middle-aged lawyer with a determined demeanor
-    appearance_canon: an elderly corporate chairman making a public announcement
+    appearance_canon: a middle-aged corporate chairman announcing the mine closure
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
+    appearance_canon: a middle-aged government minister discussing remediation costs
+  • role: UN Special Rapporteur | age unknown | era: 2023
+    appearance_canon: a middle-aged UN rapporteur investigating environmental damage
+
+OBJETOS DOCUMENTADOS: (vacío) — describí cualquier objeto que nombre la narración por su forma física según el relato, sin inventar detalles no dichos.
-  - modern cars (post-1970s)
+  - modern industrial safety equipment (e.g., hazmat suits)
+  - GPS devices
-  - modern industrial safety equipment (e.g., advanced respirators)
+  - plastic water bottles
+  - modern construction machinery (e.g., large excavators)
-  - GPS devices
-  - modern communication technology
+  - vehicles post-1970s
+  - advanced personal protective equipment
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
+  period 1937-1957:
+  clothing              : Basic, durable workwear for miners; modest dresses and simple clothes for women and children in a remote, hot climate.
+  technology            : Rudimentary mining equipment, hand tools, basic mechanical processes. Early radios for communication. Minimal dust control measures.
+  vehicles_machinery    : Early model trucks and basic heavy machinery for mining; older passenger cars for town residents.
+  interiors             : Simple, functional homes made from basic materials; dusty and industrial mine and mill interiors.
+  period 1958-1966:
+  clothing              : Similar workwear for miners, but with some attempts at dust protection; civilian clothing adapted to evolving 1960s styles, still practical for the desert.
+  technology            : Larger-scale mining equipment, introduction of some dust reduction machinery. More common use of landline phones. Early televisions in some homes.
+  vehicles_machinery    : A greater variety of 1950s-1960s trucks and utility vehicles. More modern (for the era) passenger cars. Small propeller aircraft for regional transport.
+  interiors             : Slightly more established home interiors reflecting mid-century styles, though still basic. Mill interiors remained heavily dusty despite mitigation efforts.
+  forbidden_anachronisms: smartphones, LED screens, contemporary clothing (post-2000s), modern flat panels, modern industrial safety equipment, GPS devices, digital cameras, plastic water bottles, modern construction machinery, satellite dishes, modern vehicles post-1970s, advanced personal protective equipment.
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
+  - mine_workers: Predominantly Australian and European migrant men working in the asbestos mines and mill. · Wittenoom, Australia, 1937-1966. · APPEARANCE: Predominantly Caucasian, diverse European ethnicities, dusty and fatigued complexion, often lean build from manual labor.
+  - spanish_migrant_miners: Spanish men recruited for work in the Wittenoom asbestos mines and mill. · Wittenoom, Australia, 1958-1966. · APPEARANCE: Southern European features, often sun-tanned complexion, dusty, physically robust from labor.
+  - wittenoom_residents: Australian and European migrant civilians living in the Wittenoom town. · Wittenoom, Australia, 1937-1978. · APPEARANCE: Diverse Caucasian ethnicities, generally sun-exposed and adapted to desert life.
+  - spanish_migrant_families: Spanish migrant men, women, and children living in Wittenoom, often related to miners. · Wittenoom, Australia, 1962-1971. · APPEARANCE: Southern European features, often sun-exposed. Women and children with practical, modest hairstyles.
+  - wittenoom_children: Children of Australian and European migrant families residing in Wittenoom. · Wittenoom, Australia, 1937-1966. · APPEARANCE: Diverse Caucasian children, often covered in dust, sometimes with signs of play in harsh conditions.
+  - government_officials: Various government roles including mining inspectors, state engineers, public health officials, parliamentary investigators, and ministers. · Wittenoom and various government offices in Australia, 1944-2026. · APPEARANCE: Predominantly Caucasian, well-groomed, formal or semi-formal appearance reflecting their professional roles.
+  - corporate_executives: Executives and managers from companies like ABA and CSR. · Corporate offices and Wittenoom, Australia, 1943-1966. · APPEARANCE: Predominantly Caucasian, well-dressed, confident demeanor.
+  - public_health_professionals: Doctors, industrial hygienists, and other medical/scientific personnel involved in assessing health risks. · Wittenoom and medical/government facilities, 1948-1966. · APPEARANCE: Predominantly Caucasian, professional and academic appearance, serious demeanor.
+  - indigenous_activists: Banjima elders and traditional owners advocating for remediation. · Wittenoom area, Australia, and legal/activist settings, 2023-2026. · APPEARANCE: Indigenous Australian features, often elderly, with expressions of concern and determination.
+  - legal_professionals: Lawyers representing victims and other legal personnel. · Courts and legal offices in Australia, 1988-2026. · APPEARANCE: Diverse, formal and professional appearance, clean-cut.
+  - asbestos_victims_advocates: Individuals and leaders involved in the Asbestos Diseases Society of Australia. · Australia, 1979-present. · APPEARANCE: Diverse, often former residents or their families, reflecting determination and resilience.
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
+  materials_textures           : Weathered corrugated iron, wood, fiber-cement sheeting, red earth, fine pervasive dust, and visible blue asbestos tailings used in construction for roads, yards, and buildings.
+  color_palette                : Exterior dominated by dusty red earth and blue asbestos accents, with weathered browns, greys, and muted tones of corrugated iron and timber structures. Interiors likely had simple, light-colored walls to reflect heat, quickly covered in dust.
+  scale_dimensions             : The subject is an isolated, sprawling ghost town, characterized by deserted buildings and extensive roads within a vast area covering 46,840 hectares, with remnants of mining operations and contaminated landscapes.
+  distinctive_features         : An isolated Australian desert ghost town, uniquely defined by its visible construction from insidious blue asbestos waste from the 1937-1966 mining era, now a vast, toxic, and permanently barricaded forbidden zone.
+  demographics                 : The population primarily consisted of Australian workers and families during the early mining phase, later supplemented by European migrants, notably Spanish, recruited for mining labor. Workers were mostly men, with families residing in the town.
+  condition_evolution.at_event : During its active mining period (1937-1966), Wittenoom was a functional but extremely dusty mining town, with buildings and infrastructure visibly constructed using blue asbestos tailings. Despite evident health risks, operations continued.
+  condition_evolution.later    : Post-1966, Wittenoom gradually became an abandoned ghost town. Buildings were demolished between 1986 and 2007, services were disconnected, and access was permanently barricaded. The area remains a vast, toxic zone with asbestos spread by wind and water, declared unsafe for human occupation.
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
+  • role: Medical inspector / Public health doctor | age unknown | era: 1948
+    appearance_canon: a middle-aged medical inspector with a concerned demeanor
+  • role: Spanish migrant miner | age 26 | era: 1962
+    appearance_canon: an early-20s Spanish migrant miner, likely with a bandaged foot from an injury
+  • role: Spanish migrant wife and Wittenoom resident | age unknown | era: 1962
+    appearance_canon: a young adult Spanish migrant woman, often in family photos, potentially weakened after a complicated childbirth
+  • role: Spanish migrant wife and Wittenoom resident | age unknown | era: 1962
+    appearance_canon: a young adult Spanish migrant woman, friend of Maria Bernal
+  • role: Spanish migrant miner | age unknown | era: 1962
+    appearance_canon: a young adult Spanish migrant miner, working long shifts
+  • role: Child resident of Wittenoom | age unknown | era: 1962
+    appearance_canon: a young child, playing with asbestos material
+  • role: Infant resident of Wittenoom | age 0 | era: 1963
+    appearance_canon: an infant born in Wittenoom, subject of a baptism photo
+  • role: Banjima elder, activist, mesotelioma victim | age unknown | era: 2023
+    appearance_canon: an elderly Indigenous Australian man, activist for land remediation
+  • role: Lawyer for asbestos victims | age unknown | era: 1988
+    appearance_canon: a middle-aged lawyer with a determined demeanor
-    appearance_canon: an elderly corporate chairman making a public announcement
+    appearance_canon: a middle-aged corporate chairman announcing the mine closure
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
+    appearance_canon: a middle-aged government minister discussing remediation costs
+  • role: UN Special Rapporteur | age unknown | era: 2023
+    appearance_canon: a middle-aged UN rapporteur investigating environmental damage
+
+OBJETOS DOCUMENTADOS: (vacío) — describí cualquier objeto que nombre la narración por su forma física según el relato, sin inventar detalles no dichos.
-  - modern cars (post-1970s)
+  - modern industrial safety equipment (e.g., hazmat suits)
+  - GPS devices
-  - modern industrial safety equipment (e.g., advanced respirators)
+  - plastic water bottles
+  - modern construction machinery (e.g., large excavators)
-  - GPS devices
-  - modern communication technology
+  - vehicles post-1970s
+  - advanced personal protective equipment
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
+  period 1958-1966:
+  clothing              : Similar workwear for miners, but with some attempts at dust protection; civilian clothing adapted to evolving 1960s styles, still practical for the desert.
+  technology            : Larger-scale mining equipment, introduction of some dust reduction machinery. More common use of landline phones. Early televisions in some homes.
+  vehicles_machinery    : A greater variety of 1950s-1960s trucks and utility vehicles. More modern (for the era) passenger cars. Small propeller aircraft for regional transport.
+  interiors             : Slightly more established home interiors reflecting mid-century styles, though still basic. Mill interiors remained heavily dusty despite mitigation efforts.
+  forbidden_anachronisms: smartphones, LED screens, contemporary clothing (post-2000s), modern flat panels, modern industrial safety equipment, GPS devices, digital cameras, plastic water bottles, modern construction machinery, satellite dishes, modern vehicles post-1970s, advanced personal protective equipment.
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
+  - mine_workers: Predominantly Australian and European migrant men working in the asbestos mines and mill. · Wittenoom, Australia, 1937-1966. · APPEARANCE: Predominantly Caucasian, diverse European ethnicities, dusty and fatigued complexion, often lean build from manual labor.
+  - spanish_migrant_miners: Spanish men recruited for work in the Wittenoom asbestos mines and mill. · Wittenoom, Australia, 1958-1966. · APPEARANCE: Southern European features, often sun-tanned complexion, dusty, physically robust from labor.
+  - wittenoom_residents: Australian and European migrant civilians living in the Wittenoom town. · Wittenoom, Australia, 1937-1978. · APPEARANCE: Diverse Caucasian ethnicities, generally sun-exposed and adapted to desert life.
+  - spanish_migrant_families: Spanish migrant men, women, and children living in Wittenoom, often related to miners. · Wittenoom, Australia, 1962-1971. · APPEARANCE: Southern European features, often sun-exposed. Women and children with practical, modest hairstyles.
+  - wittenoom_children: Children of Australian and European migrant families residing in Wittenoom. · Wittenoom, Australia, 1937-1966. · APPEARANCE: Diverse Caucasian children, often covered in dust, sometimes with signs of play in harsh conditions.
+  - government_officials: Various government roles including mining inspectors, state engineers, public health officials, parliamentary investigators, and ministers. · Wittenoom and various government offices in Australia, 1944-2026. · APPEARANCE: Predominantly Caucasian, well-groomed, formal or semi-formal appearance reflecting their professional roles.
+  - corporate_executives: Executives and managers from companies like ABA and CSR. · Corporate offices and Wittenoom, Australia, 1943-1966. · APPEARANCE: Predominantly Caucasian, well-dressed, confident demeanor.
+  - public_health_professionals: Doctors, industrial hygienists, and other medical/scientific personnel involved in assessing health risks. · Wittenoom and medical/government facilities, 1948-1966. · APPEARANCE: Predominantly Caucasian, professional and academic appearance, serious demeanor.
+  - indigenous_activists: Banjima elders and traditional owners advocating for remediation. · Wittenoom area, Australia, and legal/activist settings, 2023-2026. · APPEARANCE: Indigenous Australian features, often elderly, with expressions of concern and determination.
+  - legal_professionals: Lawyers representing victims and other legal personnel. · Courts and legal offices in Australia, 1988-2026. · APPEARANCE: Diverse, formal and professional appearance, clean-cut.
+  - asbestos_victims_advocates: Individuals and leaders involved in the Asbestos Diseases Society of Australia. · Australia, 1979-present. · APPEARANCE: Diverse, often former residents or their families, reflecting determination and resilience.
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
+  materials_textures           : Weathered corrugated iron, wood, fiber-cement sheeting, red earth, fine pervasive dust, and visible blue asbestos tailings used in construction for roads, yards, and buildings.
+  color_palette                : Exterior dominated by dusty red earth and blue asbestos accents, with weathered browns, greys, and muted tones of corrugated iron and timber structures. Interiors likely had simple, light-colored walls to reflect heat, quickly covered in dust.
+  scale_dimensions             : The subject is an isolated, sprawling ghost town, characterized by deserted buildings and extensive roads within a vast area covering 46,840 hectares, with remnants of mining operations and contaminated landscapes.
+  distinctive_features         : An isolated Australian desert ghost town, uniquely defined by its visible construction from insidious blue asbestos waste from the 1937-1966 mining era, now a vast, toxic, and permanently barricaded forbidden zone.
+  demographics                 : The population primarily consisted of Australian workers and families during the early mining phase, later supplemented by European migrants, notably Spanish, recruited for mining labor. Workers were mostly men, with families residing in the town.
+  condition_evolution.at_event : During its active mining period (1937-1966), Wittenoom was a functional but extremely dusty mining town, with buildings and infrastructure visibly constructed using blue asbestos tailings. Despite evident health risks, operations continued.
+  condition_evolution.later    : Post-1966, Wittenoom gradually became an abandoned ghost town. Buildings were demolished between 1986 and 2007, services were disconnected, and access was permanently barricaded. The area remains a vast, toxic zone with asbestos spread by wind and water, declared unsafe for human occupation.
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
+  • role: Medical inspector / Public health doctor | age unknown | era: 1948
+    appearance_canon: a middle-aged medical inspector with a concerned demeanor
+  • role: Spanish migrant miner | age 26 | era: 1962
+    appearance_canon: an early-20s Spanish migrant miner, likely with a bandaged foot from an injury
+  • role: Spanish migrant wife and Wittenoom resident | age unknown | era: 1962
+    appearance_canon: a young adult Spanish migrant woman, often in family photos, potentially weakened after a complicated childbirth
+  • role: Spanish migrant wife and Wittenoom resident | age unknown | era: 1962
+    appearance_canon: a young adult Spanish migrant woman, friend of Maria Bernal
+  • role: Spanish migrant miner | age unknown | era: 1962
+    appearance_canon: a young adult Spanish migrant miner, working long shifts
+  • role: Child resident of Wittenoom | age unknown | era: 1962
+    appearance_canon: a young child, playing with asbestos material
+  • role: Infant resident of Wittenoom | age 0 | era: 1963
+    appearance_canon: an infant born in Wittenoom, subject of a baptism photo
+  • role: Banjima elder, activist, mesotelioma victim | age unknown | era: 2023
+    appearance_canon: an elderly Indigenous Australian man, activist for land remediation
+  • role: Lawyer for asbestos victims | age unknown | era: 1988
+    appearance_canon: a middle-aged lawyer with a determined demeanor
-    appearance_canon: an elderly corporate chairman making a public announcement
+    appearance_canon: a middle-aged corporate chairman announcing the mine closure
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
+    appearance_canon: a middle-aged government minister discussing remediation costs
+  • role: UN Special Rapporteur | age unknown | era: 2023
+    appearance_canon: a middle-aged UN rapporteur investigating environmental damage
+
+OBJETOS DOCUMENTADOS: (vacío) — describí cualquier objeto que nombre la narración por su forma física según el relato, sin inventar detalles no dichos.
-  - modern cars (post-1970s)
+  - modern industrial safety equipment (e.g., hazmat suits)
+  - GPS devices
-  - modern industrial safety equipment (e.g., advanced respirators)
+  - plastic water bottles
+  - modern construction machinery (e.g., large excavators)
-  - GPS devices
-  - modern communication technology
+  - vehicles post-1970s
+  - advanced personal protective equipment
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
+  period 1958-1966:
+  clothing              : Similar workwear for miners, but with some attempts at dust protection; civilian clothing adapted to evolving 1960s styles, still practical for the desert.
+  technology            : Larger-scale mining equipment, introduction of some dust reduction machinery. More common use of landline phones. Early televisions in some homes.
+  vehicles_machinery    : A greater variety of 1950s-1960s trucks and utility vehicles. More modern (for the era) passenger cars. Small propeller aircraft for regional transport.
+  interiors             : Slightly more established home interiors reflecting mid-century styles, though still basic. Mill interiors remained heavily dusty despite mitigation efforts.
+  forbidden_anachronisms: smartphones, LED screens, contemporary clothing (post-2000s), modern flat panels, modern industrial safety equipment, GPS devices, digital cameras, plastic water bottles, modern construction machinery, satellite dishes, modern vehicles post-1970s, advanced personal protective equipment.
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
+  - mine_workers: Predominantly Australian and European migrant men working in the asbestos mines and mill. · Wittenoom, Australia, 1937-1966. · APPEARANCE: Predominantly Caucasian, diverse European ethnicities, dusty and fatigued complexion, often lean build from manual labor.
+  - spanish_migrant_miners: Spanish men recruited for work in the Wittenoom asbestos mines and mill. · Wittenoom, Australia, 1958-1966. · APPEARANCE: Southern European features, often sun-tanned complexion, dusty, physically robust from labor.
+  - wittenoom_residents: Australian and European migrant civilians living in the Wittenoom town. · Wittenoom, Australia, 1937-1978. · APPEARANCE: Diverse Caucasian ethnicities, generally sun-exposed and adapted to desert life.
+  - spanish_migrant_families: Spanish migrant men, women, and children living in Wittenoom, often related to miners. · Wittenoom, Australia, 1962-1971. · APPEARANCE: Southern European features, often sun-exposed. Women and children with practical, modest hairstyles.
+  - wittenoom_children: Children of Australian and European migrant families residing in Wittenoom. · Wittenoom, Australia, 1937-1966. · APPEARANCE: Diverse Caucasian children, often covered in dust, sometimes with signs of play in harsh conditions.
+  - government_officials: Various government roles including mining inspectors, state engineers, public health officials, parliamentary investigators, and ministers. · Wittenoom and various government offices in Australia, 1944-2026. · APPEARANCE: Predominantly Caucasian, well-groomed, formal or semi-formal appearance reflecting their professional roles.
+  - corporate_executives: Executives and managers from companies like ABA and CSR. · Corporate offices and Wittenoom, Australia, 1943-1966. · APPEARANCE: Predominantly Caucasian, well-dressed, confident demeanor.
+  - public_health_professionals: Doctors, industrial hygienists, and other medical/scientific personnel involved in assessing health risks. · Wittenoom and medical/government facilities, 1948-1966. · APPEARANCE: Predominantly Caucasian, professional and academic appearance, serious demeanor.
+  - indigenous_activists: Banjima elders and traditional owners advocating for remediation. · Wittenoom area, Australia, and legal/activist settings, 2023-2026. · APPEARANCE: Indigenous Australian features, often elderly, with expressions of concern and determination.
+  - legal_professionals: Lawyers representing victims and other legal personnel. · Courts and legal offices in Australia, 1988-2026. · APPEARANCE: Diverse, formal and professional appearance, clean-cut.
+  - asbestos_victims_advocates: Individuals and leaders involved in the Asbestos Diseases Society of Australia. · Australia, 1979-present. · APPEARANCE: Diverse, often former residents or their families, reflecting determination and resilience.
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
+  materials_textures           : Weathered corrugated iron, wood, fiber-cement sheeting, red earth, fine pervasive dust, and visible blue asbestos tailings used in construction for roads, yards, and buildings.
+  color_palette                : Exterior dominated by dusty red earth and blue asbestos accents, with weathered browns, greys, and muted tones of corrugated iron and timber structures. Interiors likely had simple, light-colored walls to reflect heat, quickly covered in dust.
+  scale_dimensions             : The subject is an isolated, sprawling ghost town, characterized by deserted buildings and extensive roads within a vast area covering 46,840 hectares, with remnants of mining operations and contaminated landscapes.
+  distinctive_features         : An isolated Australian desert ghost town, uniquely defined by its visible construction from insidious blue asbestos waste from the 1937-1966 mining era, now a vast, toxic, and permanently barricaded forbidden zone.
+  demographics                 : The population primarily consisted of Australian workers and families during the early mining phase, later supplemented by European migrants, notably Spanish, recruited for mining labor. Workers were mostly men, with families residing in the town.
+  condition_evolution.at_event : During its active mining period (1937-1966), Wittenoom was a functional but extremely dusty mining town, with buildings and infrastructure visibly constructed using blue asbestos tailings. Despite evident health risks, operations continued.
+  condition_evolution.later    : Post-1966, Wittenoom gradually became an abandoned ghost town. Buildings were demolished between 1986 and 2007, services were disconnected, and access was permanently barricaded. The area remains a vast, toxic zone with asbestos spread by wind and water, declared unsafe for human occupation.
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
+  • role: Medical inspector / Public health doctor | age unknown | era: 1948
+    appearance_canon: a middle-aged medical inspector with a concerned demeanor
+  • role: Spanish migrant miner | age 26 | era: 1962
+    appearance_canon: an early-20s Spanish migrant miner, likely with a bandaged foot from an injury
+  • role: Spanish migrant wife and Wittenoom resident | age unknown | era: 1962
+    appearance_canon: a young adult Spanish migrant woman, often in family photos, potentially weakened after a complicated childbirth
+  • role: Spanish migrant wife and Wittenoom resident | age unknown | era: 1962
+    appearance_canon: a young adult Spanish migrant woman, friend of Maria Bernal
+  • role: Spanish migrant miner | age unknown | era: 1962
+    appearance_canon: a young adult Spanish migrant miner, working long shifts
+  • role: Child resident of Wittenoom | age unknown | era: 1962
+    appearance_canon: a young child, playing with asbestos material
+  • role: Infant resident of Wittenoom | age 0 | era: 1963
+    appearance_canon: an infant born in Wittenoom, subject of a baptism photo
+  • role: Banjima elder, activist, mesotelioma victim | age unknown | era: 2023
+    appearance_canon: an elderly Indigenous Australian man, activist for land remediation
+  • role: Lawyer for asbestos victims | age unknown | era: 1988
+    appearance_canon: a middle-aged lawyer with a determined demeanor
-    appearance_canon: an elderly corporate chairman making a public announcement
+    appearance_canon: a middle-aged corporate chairman announcing the mine closure
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
+    appearance_canon: a middle-aged government minister discussing remediation costs
+  • role: UN Special Rapporteur | age unknown | era: 2023
+    appearance_canon: a middle-aged UN rapporteur investigating environmental damage
+
+OBJETOS DOCUMENTADOS: (vacío) — describí cualquier objeto que nombre la narración por su forma física según el relato, sin inventar detalles no dichos.
-  - modern cars (post-1970s)
+  - modern industrial safety equipment (e.g., hazmat suits)
+  - GPS devices
-  - modern industrial safety equipment (e.g., advanced respirators)
+  - plastic water bottles
+  - modern construction machinery (e.g., large excavators)
-  - GPS devices
-  - modern communication technology
+  - vehicles post-1970s
+  - advanced personal protective equipment
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
+  period 1958-1966:
+  clothing              : Similar workwear for miners, but with some attempts at dust protection; civilian clothing adapted to evolving 1960s styles, still practical for the desert.
+  technology            : Larger-scale mining equipment, introduction of some dust reduction machinery. More common use of landline phones. Early televisions in some homes.
+  vehicles_machinery    : A greater variety of 1950s-1960s trucks and utility vehicles. More modern (for the era) passenger cars. Small propeller aircraft for regional transport.
+  interiors             : Slightly more established home interiors reflecting mid-century styles, though still basic. Mill interiors remained heavily dusty despite mitigation efforts.
+  forbidden_anachronisms: smartphones, LED screens, contemporary clothing (post-2000s), modern flat panels, modern industrial safety equipment, GPS devices, digital cameras, plastic water bottles, modern construction machinery, satellite dishes, modern vehicles post-1970s, advanced personal protective equipment.
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
+  - mine_workers: Predominantly Australian and European migrant men working in the asbestos mines and mill. · Wittenoom, Australia, 1937-1966. · APPEARANCE: Predominantly Caucasian, diverse European ethnicities, dusty and fatigued complexion, often lean build from manual labor.
+  - spanish_migrant_miners: Spanish men recruited for work in the Wittenoom asbestos mines and mill. · Wittenoom, Australia, 1958-1966. · APPEARANCE: Southern European features, often sun-tanned complexion, dusty, physically robust from labor.
+  - wittenoom_residents: Australian and European migrant civilians living in the Wittenoom town. · Wittenoom, Australia, 1937-1978. · APPEARANCE: Diverse Caucasian ethnicities, generally sun-exposed and adapted to desert life.
+  - spanish_migrant_families: Spanish migrant men, women, and children living in Wittenoom, often related to miners. · Wittenoom, Australia, 1962-1971. · APPEARANCE: Southern European features, often sun-exposed. Women and children with practical, modest hairstyles.
+  - wittenoom_children: Children of Australian and European migrant families residing in Wittenoom. · Wittenoom, Australia, 1937-1966. · APPEARANCE: Diverse Caucasian children, often covered in dust, sometimes with signs of play in harsh conditions.
+  - government_officials: Various government roles including mining inspectors, state engineers, public health officials, parliamentary investigators, and ministers. · Wittenoom and various government offices in Australia, 1944-2026. · APPEARANCE: Predominantly Caucasian, well-groomed, formal or semi-formal appearance reflecting their professional roles.
+  - corporate_executives: Executives and managers from companies like ABA and CSR. · Corporate offices and Wittenoom, Australia, 1943-1966. · APPEARANCE: Predominantly Caucasian, well-dressed, confident demeanor.
+  - public_health_professionals: Doctors, industrial hygienists, and other medical/scientific personnel involved in assessing health risks. · Wittenoom and medical/government facilities, 1948-1966. · APPEARANCE: Predominantly Caucasian, professional and academic appearance, serious demeanor.
+  - indigenous_activists: Banjima elders and traditional owners advocating for remediation. · Wittenoom area, Australia, and legal/activist settings, 2023-2026. · APPEARANCE: Indigenous Australian features, often elderly, with expressions of concern and determination.
+  - legal_professionals: Lawyers representing victims and other legal personnel. · Courts and legal offices in Australia, 1988-2026. · APPEARANCE: Diverse, formal and professional appearance, clean-cut.
+  - asbestos_victims_advocates: Individuals and leaders involved in the Asbestos Diseases Society of Australia. · Australia, 1979-present. · APPEARANCE: Diverse, often former residents or their families, reflecting determination and resilience.
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
+  materials_textures           : Weathered corrugated iron, wood, fiber-cement sheeting, red earth, fine pervasive dust, and visible blue asbestos tailings used in construction for roads, yards, and buildings.
+  color_palette                : Exterior dominated by dusty red earth and blue asbestos accents, with weathered browns, greys, and muted tones of corrugated iron and timber structures. Interiors likely had simple, light-colored walls to reflect heat, quickly covered in dust.
+  scale_dimensions             : The subject is an isolated, sprawling ghost town, characterized by deserted buildings and extensive roads within a vast area covering 46,840 hectares, with remnants of mining operations and contaminated landscapes.
+  distinctive_features         : An isolated Australian desert ghost town, uniquely defined by its visible construction from insidious blue asbestos waste from the 1937-1966 mining era, now a vast, toxic, and permanently barricaded forbidden zone.
+  demographics                 : The population primarily consisted of Australian workers and families during the early mining phase, later supplemented by European migrants, notably Spanish, recruited for mining labor. Workers were mostly men, with families residing in the town.
+  condition_evolution.at_event : During its active mining period (1937-1966), Wittenoom was a functional but extremely dusty mining town, with buildings and infrastructure visibly constructed using blue asbestos tailings. Despite evident health risks, operations continued.
+  condition_evolution.later    : Post-1966, Wittenoom gradually became an abandoned ghost town. Buildings were demolished between 1986 and 2007, services were disconnected, and access was permanently barricaded. The area remains a vast, toxic zone with asbestos spread by wind and water, declared unsafe for human occupation.
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
+  • role: Medical inspector / Public health doctor | age unknown | era: 1948
+    appearance_canon: a middle-aged medical inspector with a concerned demeanor
+  • role: Spanish migrant miner | age 26 | era: 1962
+    appearance_canon: an early-20s Spanish migrant miner, likely with a bandaged foot from an injury
+  • role: Spanish migrant wife and Wittenoom resident | age unknown | era: 1962
+    appearance_canon: a young adult Spanish migrant woman, often in family photos, potentially weakened after a complicated childbirth
+  • role: Spanish migrant wife and Wittenoom resident | age unknown | era: 1962
+    appearance_canon: a young adult Spanish migrant woman, friend of Maria Bernal
+  • role: Spanish migrant miner | age unknown | era: 1962
+    appearance_canon: a young adult Spanish migrant miner, working long shifts
+  • role: Child resident of Wittenoom | age unknown | era: 1962
+    appearance_canon: a young child, playing with asbestos material
+  • role: Infant resident of Wittenoom | age 0 | era: 1963
+    appearance_canon: an infant born in Wittenoom, subject of a baptism photo
+  • role: Banjima elder, activist, mesotelioma victim | age unknown | era: 2023
+    appearance_canon: an elderly Indigenous Australian man, activist for land remediation
+  • role: Lawyer for asbestos victims | age unknown | era: 1988
+    appearance_canon: a middle-aged lawyer with a determined demeanor
-    appearance_canon: an elderly corporate chairman making a public announcement
+    appearance_canon: a middle-aged corporate chairman announcing the mine closure
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
+    appearance_canon: a middle-aged government minister discussing remediation costs
+  • role: UN Special Rapporteur | age unknown | era: 2023
+    appearance_canon: a middle-aged UN rapporteur investigating environmental damage
+
+OBJETOS DOCUMENTADOS: (vacío) — describí cualquier objeto que nombre la narración por su forma física según el relato, sin inventar detalles no dichos.
-  - modern cars (post-1970s)
+  - modern industrial safety equipment (e.g., hazmat suits)
+  - GPS devices
-  - modern industrial safety equipment (e.g., advanced respirators)
+  - plastic water bottles
+  - modern construction machinery (e.g., large excavators)
-  - GPS devices
-  - modern communication technology
+  - vehicles post-1970s
+  - advanced personal protective equipment
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
+  period 1958-1966:
+  clothing              : Similar workwear for miners, but with some attempts at dust protection; civilian clothing adapted to evolving 1960s styles, still practical for the desert.
+  technology            : Larger-scale mining equipment, introduction of some dust reduction machinery. More common use of landline phones. Early televisions in some homes.
+  vehicles_machinery    : A greater variety of 1950s-1960s trucks and utility vehicles. More modern (for the era) passenger cars. Small propeller aircraft for regional transport.
+  interiors             : Slightly more established home interiors reflecting mid-century styles, though still basic. Mill interiors remained heavily dusty despite mitigation efforts.
+  forbidden_anachronisms: smartphones, LED screens, contemporary clothing (post-2000s), modern flat panels, modern industrial safety equipment, GPS devices, digital cameras, plastic water bottles, modern construction machinery, satellite dishes, modern vehicles post-1970s, advanced personal protective equipment.
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
+  - mine_workers: Predominantly Australian and European migrant men working in the asbestos mines and mill. · Wittenoom, Australia, 1937-1966. · APPEARANCE: Predominantly Caucasian, diverse European ethnicities, dusty and fatigued complexion, often lean build from manual labor.
+  - spanish_migrant_miners: Spanish men recruited for work in the Wittenoom asbestos mines and mill. · Wittenoom, Australia, 1958-1966. · APPEARANCE: Southern European features, often sun-tanned complexion, dusty, physically robust from labor.
+  - wittenoom_residents: Australian and European migrant civilians living in the Wittenoom town. · Wittenoom, Australia, 1937-1978. · APPEARANCE: Diverse Caucasian ethnicities, generally sun-exposed and adapted to desert life.
+  - spanish_migrant_families: Spanish migrant men, women, and children living in Wittenoom, often related to miners. · Wittenoom, Australia, 1962-1971. · APPEARANCE: Southern European features, often sun-exposed. Women and children with practical, modest hairstyles.
+  - wittenoom_children: Children of Australian and European migrant families residing in Wittenoom. · Wittenoom, Australia, 1937-1966. · APPEARANCE: Diverse Caucasian children, often covered in dust, sometimes with signs of play in harsh conditions.
+  - government_officials: Various government roles including mining inspectors, state engineers, public health officials, parliamentary investigators, and ministers. · Wittenoom and various government offices in Australia, 1944-2026. · APPEARANCE: Predominantly Caucasian, well-groomed, formal or semi-formal appearance reflecting their professional roles.
+  - corporate_executives: Executives and managers from companies like ABA and CSR. · Corporate offices and Wittenoom, Australia, 1943-1966. · APPEARANCE: Predominantly Caucasian, well-dressed, confident demeanor.
+  - public_health_professionals: Doctors, industrial hygienists, and other medical/scientific personnel involved in assessing health risks. · Wittenoom and medical/government facilities, 1948-1966. · APPEARANCE: Predominantly Caucasian, professional and academic appearance, serious demeanor.
+  - indigenous_activists: Banjima elders and traditional owners advocating for remediation. · Wittenoom area, Australia, and legal/activist settings, 2023-2026. · APPEARANCE: Indigenous Australian features, often elderly, with expressions of concern and determination.
+  - legal_professionals: Lawyers representing victims and other legal personnel. · Courts and legal offices in Australia, 1988-2026. · APPEARANCE: Diverse, formal and professional appearance, clean-cut.
+  - asbestos_victims_advocates: Individuals and leaders involved in the Asbestos Diseases Society of Australia. · Australia, 1979-present. · APPEARANCE: Diverse, often former residents or their families, reflecting determination and resilience.
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
+  materials_textures           : Weathered corrugated iron, wood, fiber-cement sheeting, red earth, fine pervasive dust, and visible blue asbestos tailings used in construction for roads, yards, and buildings.
+  color_palette                : Exterior dominated by dusty red earth and blue asbestos accents, with weathered browns, greys, and muted tones of corrugated iron and timber structures. Interiors likely had simple, light-colored walls to reflect heat, quickly covered in dust.
+  scale_dimensions             : The subject is an isolated, sprawling ghost town, characterized by deserted buildings and extensive roads within a vast area covering 46,840 hectares, with remnants of mining operations and contaminated landscapes.
+  distinctive_features         : An isolated Australian desert ghost town, uniquely defined by its visible construction from insidious blue asbestos waste from the 1937-1966 mining era, now a vast, toxic, and permanently barricaded forbidden zone.
+  demographics                 : The population primarily consisted of Australian workers and families during the early mining phase, later supplemented by European migrants, notably Spanish, recruited for mining labor. Workers were mostly men, with families residing in the town.
+  condition_evolution.at_event : During its active mining period (1937-1966), Wittenoom was a functional but extremely dusty mining town, with buildings and infrastructure visibly constructed using blue asbestos tailings. Despite evident health risks, operations continued.
+  condition_evolution.later    : Post-1966, Wittenoom gradually became an abandoned ghost town. Buildings were demolished between 1986 and 2007, services were disconnected, and access was permanently barricaded. The area remains a vast, toxic zone with asbestos spread by wind and water, declared unsafe for human occupation.
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
+  • role: Medical inspector / Public health doctor | age unknown | era: 1948
+    appearance_canon: a middle-aged medical inspector with a concerned demeanor
+  • role: Spanish migrant miner | age 26 | era: 1962
+    appearance_canon: an early-20s Spanish migrant miner, likely with a bandaged foot from an injury
+  • role: Spanish migrant wife and Wittenoom resident | age unknown | era: 1962
+    appearance_canon: a young adult Spanish migrant woman, often in family photos, potentially weakened after a complicated childbirth
+  • role: Spanish migrant wife and Wittenoom resident | age unknown | era: 1962
+    appearance_canon: a young adult Spanish migrant woman, friend of Maria Bernal
+  • role: Spanish migrant miner | age unknown | era: 1962
+    appearance_canon: a young adult Spanish migrant miner, working long shifts
+  • role: Child resident of Wittenoom | age unknown | era: 1962
+    appearance_canon: a young child, playing with asbestos material
+  • role: Infant resident of Wittenoom | age 0 | era: 1963
+    appearance_canon: an infant born in Wittenoom, subject of a baptism photo
+  • role: Banjima elder, activist, mesotelioma victim | age unknown | era: 2023
+    appearance_canon: an elderly Indigenous Australian man, activist for land remediation
+  • role: Lawyer for asbestos victims | age unknown | era: 1988
+    appearance_canon: a middle-aged lawyer with a determined demeanor
-    appearance_canon: an elderly corporate chairman making a public announcement
+    appearance_canon: a middle-aged corporate chairman announcing the mine closure
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
+    appearance_canon: a middle-aged government minister discussing remediation costs
+  • role: UN Special Rapporteur | age unknown | era: 2023
+    appearance_canon: a middle-aged UN rapporteur investigating environmental damage
+
+OBJETOS DOCUMENTADOS: (vacío) — describí cualquier objeto que nombre la narración por su forma física según el relato, sin inventar detalles no dichos.
-  - modern cars (post-1970s)
+  - modern industrial safety equipment (e.g., hazmat suits)
+  - GPS devices
-  - modern industrial safety equipment (e.g., advanced respirators)
+  - plastic water bottles
+  - modern construction machinery (e.g., large excavators)
-  - GPS devices
-  - modern communication technology
+  - vehicles post-1970s
+  - advanced personal protective equipment
```
