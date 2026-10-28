# F50 A — canon visual desde la ficha (Wittenoom)

Una llamada a Flash con `step_4e.canon_desde_ficha` (pedido = el de la regeneración S5 de F48, md5 `46ff0c7b…`, verificado en seco con `verificar_a.py`). Guardado en el topic de `topics_db` y en `_steps/<id>/05_visual_canon.json`, con `canon_ficha_md5` = `b02aa6f88586f5e0c8a87a80d2ccb067`.

## people_groups (7)

| id | who | appearance | clothing |
|---|---|---|---|
| `wittenoom_miners_and_mill_workers` | Various European migrant and Australian laborers working in the asbestos mines and processing mill. | Physically robust individuals, often appearing fatigued and covered in a pervasive fine dust, with diverse European features. | Rugged, practical work clothes, heavy-duty trousers and shirts, sometimes with hard hats, all visibly stained and impregnated with asbestos dust. |
| `spanish_migrant_families` | Spanish families who migrated to Wittenoom under government schemes. | Adults and children of Southern European descent, appearing resilient and resourceful, adapting to a harsh desert environment, often showing signs of physical strain or everyday weariness. | Simple, light clothing suitable for a hot, dusty climate; women in plain dresses or skirts/blouses, men in casual shirts and trousers, children in basic playwear, all often soiled with red earth and dust. |
| `australian_public_health_officials` | Doctors, inspectors, and hygienists from Australian public health departments. | Predominantly Caucasian, appearing professional, often with a serious or concerned demeanor due to the health risks. | Formal or semi-formal attire of the era, such as suits, collared shirts, and ties, or clean uniforms for medical staff. |
| `australian_government_representatives` | Various Australian federal and state government officials, including politicians, committee members, and regulators. | Predominantly Caucasian, appearing authoritative and formal, reflecting their political or administrative roles. | Formal business attire, including suits and ties, typical of Australian politicians and civil servants of the respective decades. |
| `csr_corporate_personnel` | Executives, managers, and other personnel from Colonial Sugar Refining (CSR) and its subsidiary, Australian Blue Asbestos (ABA). | Predominantly Caucasian, appearing well-dressed and corporate, often with an air of authority, sometimes dismissive of worker concerns. | Business suits and formal wear, reflecting their executive or managerial positions, often clean and sharp in contrast to the dusty environment. |
| `banjima_traditional_owners_and_advocates` | Indigenous Banjima people, including elders and legal advocates, asserting their rights over contaminated lands. | Indigenous Australian people, often older, appearing resilient and determined, some bearing the visible or implied health consequences of asbestos exposure. | Practical, contemporary casual clothing suitable for the Australian climate and for meetings or public appearances. |
| `australian_airport_police` | Law enforcement personnel working in Australian airports. | Predominantly Caucasian, appearing uniformed and professional. | Standard police uniform of the mid-1980s, typically including a collared shirt, trousers, and a peaked cap. |

## Diff de claves contra `lab/hyperframes/f48/canon_S5.json` (informativo: Flash no es determinista)

| clave | S5 de F48 | F50 (producción) |
|---|---|---|
| anachronism_blocklist | 12 | 10 |
| canon_ficha_md5 | None | b02aa6f88586f5e0c8a87a80d2ccb067 |
| central_subject | 0 subclaves distintas: — | |
| documented_people | 5 | 16 |
| documented_props | 2 | 2 |
| era_visual_canon | 13 subclaves distintas: clothing, color_palette, condition_evolution, demographics, distinctive_features, forbidden_anachronisms, interiors, materials_textures, scale_dimensions, spans, technology, vehicles_machinery, visual_reference_availability | |
| people_groups | 15 | 7 |

- `era_visual_canon.spans`: S5 `1937-2007` → F50 `1937-2026`; `primary_decade` `1960s` → `1960s`.
- Grupos de S5 (15): mine_regulatory_officials, early_mine_operators, public_health_professionals, csr_executives, parliamentary_inquiry_members, banjima_elders_activists, bntac_representatives, spanish_migrant_wives_wittenoom, wittenoom_child_residents, spanish_migrant_miners_wittenoom, asbestos_society_advocates, australian_prime_ministers, wittenoom_general_workers, aba_management, western_australian_officials_modern.
- `central_subject`: `kind` igual (`place`); `foto_madre` vacío (en el canon viejo del research apuntaba a `foto_madre/subject.png`; la foto madre se rehace en la tanda de fotos).
## Personaje del pool (rol) → grupo que lo cubre (informativo, cruce a ojo de CC; no es un corte)

| rol (pool) | lugar · años | grupo |
|---|---|---|
| Funcionario de minas que informó sobre el polvo de asbesto | - · 1944 | `australian_government_representatives` |
| Miembros del Comité Directivo de Wittenoom | - · - | `australian_government_representatives` |
| Prospector y subdirector de mina | Yampire and Wittenoom Gorges · 1937, 1943 | sin grupo (`wittenoom_miners_and_mill_workers` es de obreros) |
| Prospector y dueño de mina | Yampire and Wittenoom Gorges · 1937, 1943 | sin grupo (ídem) |
| Médico del Departamento de Salud Pública | - · 1960, 1962, 1968 | `australian_public_health_officials` |
| Presidente de CSR (×2) | - · 1966 / - | `csr_corporate_personnel` |
| Líder de investigación parlamentaria | - · 1992 | `australian_government_representatives` |
| Presidente de comité parlamentario | - · 1994 | `australian_government_representatives` |
| Anciano Banjima, activista y víctima de mesotelioma | Wittenoom · 2023, 2024 | `banjima_traditional_owners_and_advocates` |
| Vicepresidente de BNTAC y dueño tradicional Banjima | - · 2026 | `banjima_traditional_owners_and_advocates` |
| Esposas de mineros españoles (×2) | Wittenoom · 1962–1964 | `spanish_migrant_families` |
| Hijos e hijas de mineros nacidos o criados en Wittenoom (×5) | Wittenoom · 1962–1964 | `spanish_migrant_families` |
| Minero español en Wittenoom | Wittenoom · 1962–1964 | `wittenoom_miners_and_mill_workers` y `spanish_migrant_families` |
| CEO de la Asbestos Diseases Society of Australia | - · - | sin grupo |
| Doctor de la sanidad pública que advirtió de los peligros | - · 1948–1951 | `australian_public_health_officials` |
| Primer Ministro de Australia (×2) | - · 1947 / - | `australian_government_representatives` |
| Minero; Trabajador; Obrero; Ajustador de molino | - · 1947–1957 | `wittenoom_miners_and_mill_workers` |
| Gerente de ABA | - · 1949 | `csr_corporate_personnel` |
| Comisionado de Salud Pública; Higienista industrial; Inspector de Salud | Wittenoom · 1965 / 1966 / - | `australian_public_health_officials` |
| Ministro de Tierras; Gobierno estatal; Organismo gubernamental | - · 2019 / - | `australian_government_representatives` |
| Organismo de arbitraje laboral | - · - | sin grupo (no es gente que se vea) |

Quedan sin grupo: los dos prospectores de 1937–1943 y la CEO de la sociedad de enfermos. El grupo `australian_airport_police` (mediados de los 80) no cubre a ningún personaje del pool: sale de la ficha.
