# F60 — Salida A3 (el canon de cada persona separa aspecto fijo de estado) — PARADA A3

Handoff `lab/hyperframes/f60/HANDOFF_F60_A3_canon_persona_fijo.md` (md5 `aec44c60935087a110db6c83a247094f`, verificado). Sustituciones exactas (1a, 1b, 1c, 1d, `_clean_person`, bloque PERSONAS de m03, `TEXTO_PERSONA`): todos los ANTES coincidieron byte a byte (el script de edición aborta si no). Tests nuevos `test_module_f60_a3.py` (6). Prueba sobre la copia `lab/hyperframes/f60/base/`; NUNCA topics_db ni `_steps` reales; cero fotos. Runners `etapa_a3_canon.py` (canon con Opus, sin `asegurar_canon`) y `etapa_a3_m03.py` (7 caps, canon inyectado al topic, anclas fijas de `a/03_visual_despues.json`). Salidas en `a3/`.

**Resultado en una línea:** con el canon nuevo (Daniel = «a mid-20s Spanish man» + `condition 1962-1963: foot bandaged…`) y el casillero sin «and condition», **Daniel entra en 13 fotos** (A: 4, A2: 2): baile, boda, barco, «mi marido», pista, las dos de la mina, bautizo, Madrid 1966, más las 3 del cap 1. La venda aparece solo en las fotos de Wittenoom 1962-1963 (5 de 13). Sin falsos positivos con las otras familias. Dos cosas a mirar: Daniel aparece también a los 55 años (1991) y en el detalle del pie del clip; y «se fueron» (familia de espaldas) perdió a los dos. Anclas fijas: 96/96 pares con la referencia. Control de nombres: 0 PARÁ, 1 revisar («Court»). Costo US$ 2.6248.

## a) Canon nuevo (Opus, 129.8 s, US$ 0.3437; `a3/05_visual_canon_a3.json`)

Lectura a mano para el PARÁ: ningún `appearance_canon` trae oficio, ropa, herida, enfermedad, ánimo ni acción; Daniel trae la herida en `condition_by_period` → sin PARÁ. Personas: 22 (nuevas: [], desaparecidas: []). Observaciones: Eric Saint pasó de «young adult» a «middle-aged» y Daniel ganó `age_at_event` 25 (Daniel hijo 22): inferencias de Opus sobre la misma ficha, no datos nuevos; Marcos Orellana sin nacionalidad («a middle-aged man»).

| persona | appearance_canon ANTES | appearance_canon AHORA | condition_by_period |
|---|---|---|---|
| Eric Saint | a young adult Australian medical officer in shirtsleeves and tie with an earnest, concerned demeanor | a middle-aged Australian man | — |
| Hancock | a young adult Australian prospector and mine owner in rugged outback work clothes and a wide-brimmed hat | an adult Australian man | — |
| Wright | a young adult Australian prospector in practical outback work clothes | an adult Australian man | — |
| Chifley | a middle-aged to elderly Australian national politician in a dark suit with a confident public manner | an older Australian man | — |
| McNulty | a middle-aged Australian public health physician in a plain suit | a middle-aged Australian man | — |
| Víctor Calvo | a young Spanish boy in simple shorts and shirt, curious and dust-covered | a young Spanish boy | 1962-1964: His hands and mouth are dusted with fine asbestos powder from playing with frayed fibre. |
| Ramón de Juan | a young adult Spanish miner in dust-coated work clothes with a fatigued expression | an adult Spanish man | 1962-1964: He is worn down by frequent 16-hour shifts and covered in mine dust. |
| Milagros Barroso | a young adult Spanish migrant mother in a modest cotton dress | a young adult Spanish woman | 1963-1963: She is in the late stage of pregnancy and then recovering after giving birth in Wittenoom. |
| Mercedes | a young Spanish girl in a simple cotton frock | a young Spanish girl | — |
| John Patrick | a newborn infant wrapped in a plain cotton blanket | a newborn infant of Spanish parentage | — |
| Daniel Écija | a young adult Spanish migrant miner in work clothes, one foot visibly bandaged | a mid-20s Spanish man | 1962-1963: His foot is bandaged over a non-healing wound caused by a falling chunk of asbestos.<br>1991-1992: He is terminally ill with mesothelioma and gaunt in the final months of life. |
| María Bernal | a young adult Spanish newlywed migrant woman in a modest cotton dress, hopeful yet physically weakened | a young adult Spanish woman | 1963-1963: She is physically weakened by a kidney infection and a complicated forceps delivery of a very large baby. |
| Daniel Écija hijo | a young adult Spanish man presenting travel documents at an airport checkpoint | an early-20s Spanish man | — |
| Davidson | a middle-aged Australian senior health official in a lightweight suit with a stern demeanor | a middle-aged Australian man | — |
| Major | a middle-aged Australian industrial hygienist in shirtsleeves, inspecting machinery with a notebook | a middle-aged Australian man | — |
| James Vernon | a middle-aged Australian corporate executive in a dark business suit | a middle-aged Australian man | — |
| Peter Gordon | a young adult to middle-aged Australian lawyer in a dark business suit | an adult Australian man | — |
| Court | a middle-aged Australian state politician in a business suit | a middle-aged Australian man | — |
| Ben Wyatt | a middle-aged Australian state government minister in a contemporary business suit | a middle-aged Australian man | — |
| Marcos Orellana | a middle-aged international human rights official in smart contemporary attire | a middle-aged man | — |
| Maitland Parker | an elderly Aboriginal Australian Banjima man with a dignified, resolute demeanor | an elderly Aboriginal Australian man | 2023-2024: He is visibly ill and frail with mesothelioma, which caused his death in 2024. |
| Melita Markey | a middle-aged Australian woman advocate in contemporary professional attire | a middle-aged Australian woman | — |

Grupos (`people_groups`, por id): el pedido del canon es una sola llamada, así que Opus rehizo también los grupos y la era (efecto declarado en el handoff). Ids: 8 nuevos, 8 desaparecidos, 4 cambian; m03 A3 usa solo ids del canon nuevo (ids fuera del canon nuevo: ninguno).

| grupo | igual / cambia / nuevo / desaparece | appearance nueva (si cambia) |
|---|---|---|
| airport_border_police | nuevo |  |
| asbestos_victims_advocates_and_lawyers | cambia: who, where_when, condition_by_period, clothing_by_period |  |
| australian_airport_police | desaparece |  |
| australian_politicians | desaparece |  |
| banjima_traditional_owners | cambia: who, where_when, appearance, condition_by_period, clothing_by_period | Aboriginal Australian features, with dark brown skin, dark wavy to curly hair, brown eyes, and broad facial features. |
| company_executives_managers | nuevo |  |
| company_owners_and_managers | desaparece |  |
| environmental_assessors | desaparece |  |
| european_recruited_workers | nuevo | Varied European features, with fair to olive skin, light to dark hair, and medium working builds. |
| government_mines_and_health_officials | desaparece |  |
| health_and_mines_officials | nuevo |  |
| international_human_rights_observers | desaparece |  |
| mine_and_mill_workers | cambia: who, where_when, appearance, condition_by_period, clothing_by_period |  |
| politicians_and_government | nuevo |  |
| prospectors_and_mine_owners | nuevo |  |
| spanish_migrant_families | cambia: who, where_when, appearance, condition_by_period, clothing_by_period | Southern European features, with light olive to tanned skin, dark brown or black hair that is straight to wavy, brown ey… |
| union_and_arbitration_bodies | nuevo |  |
| unions_and_labour_arbitration | desaparece |  |
| wittenoom_residents_and_children | nuevo |  |
| wittenoom_town_residents | desaparece |  |

Props: ninguno en los dos canones. Era (`era_visual_canon`):

| campo | igual / cambia | valor nuevo (recorte) |
|---|---|---|
| clothing | cambia | Mining-era miners and mill hands wear sweat-stained cotton work shirts, khaki or denim work trousers, leather work boots… |
| color_palette | cambia | Exterior: intense red earth and red dust, blue crocidolite tailings on roads and yards, silver-grey corrugated iron and … |
| condition_evolution | cambia | {'at_event': 'Wittenoom is an operating mining town: the mill is shrouded in a thick dust cloud, workers are coated in d… |
| demographics | cambia | The residents were Australian and European migrant miners and mill workers, including post-war displaced persons in 1948… |
| distinctive_features | cambia | A remote Pilbara mining town on intense red earth whose roads, yards, airstrip and school playground were literally surf… |
| forbidden_anachronisms | cambia | No smartphones, digital screens, modern hi-vis vests, disposable respirators or modern hazmat suits in 1937-1966 scenes.… |
| interiors | cambia | Sparse company houses built of corrugated iron, timber and fibro sheeting, with simple mid-century furniture and fine du… |
| materials_textures | cambia | Houses are built of corrugated iron, timber and fibro sheeting. Loose, friable fibrous asbestos tailings are spread as a… |
| periods | cambia: tramos antes ['1937-1949', '1950-1966', '1967-2007', '2008-2026'] → ahora ['1937-1949', '1950-1966', '1967-1992', '1993-2026'] |  |
| primary_decade | igual |  |
| scale_dimensions | cambia | The Wittenoom Asbestos Management Area covers 46,840 hectares, and more than three million tonnes of tailings remain on … |
| spans | igual |  |
| technology | cambia | Mechanical ore crushing and fibre milling, belt conveyors, jute or hessian fibre sacks, dial telephones, manual typewrit… |
| vehicles_machinery | cambia | Small propeller aircraft landing on a dirt airstrip, mid-century flatbed and tipper trucks hauling tailings, utility tru… |
| visual_reference_availability | cambia | No [VISUAL] research block was supplied, so all place details come from TEXT sources: oral testimony of Spanish migrant … |

`central_subject`: igual · `anachronism_blocklist`: cambia (12 → 11).

## b) Tabla de verdad de SALIDA_A (escenas de Daniel) — A (corrida 2) / A2 / A3, por ancla

Anclas fijas en A3 (las de la referencia, 96/96 pares; `_reconcile_anchor_timing` no movió ninguna; caps con `_plan_anchors` real: ninguno). A2 solo cubrió caps 2-4 y con anclas propias; donde no hay par se dice.

| escena | tabla de verdad (analista) | A | A2 | A3 | lectura |
|---|---|---|---|---|---|
| baile | Daniel Écija | `[]` | `['María Bernal']` | `['Daniel Écija', 'María Bernal']` | **Daniel entra** (con María). |
| boda | Daniel Écija | `['María Bernal']` | `['María Bernal']` | `['Daniel Écija', 'María Bernal']` | **Daniel entra**. |
| barco | Daniel Écija (+ María) | `['María Bernal']` | `[]` | `['Daniel Écija', 'María Bernal']` | **Daniel entra**. |
| mi marido | Daniel Écija (+ María) | `['María Bernal']`, `[]` | `['María Bernal']`, `[]` | `['María Bernal', 'Daniel Écija']`, `[]` | **Daniel entra** (María primero: «recuerda su mujer»). |
| dos parejas | Daniel (+ quizá Ramón) | `['Milagros Barroso', 'Ramón de Juan']` | `['Milagros Barroso', 'Ramón de Juan']` | `['Milagros Barroso', 'Ramón de Juan']` | igual que A y A2: Milagros y Ramón; faltan los Écija (la ancla nombra a la otra pareja). |
| pista | Daniel Écija | `[]` | `['María Bernal']` | `['Daniel Écija', 'María Bernal']` | **Daniel entra** («los Écija»). |
| mina (Daniel trabajaba) | Daniel (dudoso: Ramón) | `['Ramón de Juan']` | `['Ramón de Juan']` | `['Daniel Écija', 'Ramón de Juan']` | **Daniel entra**, con Ramón. |
| mina (primer día) | Daniel Écija | `[]` | `[]` | `['Daniel Écija']` | **Daniel entra** (sin venda: el primer día, antes de la herida). |
| fórceps / bautizo | (no en la tabla; de espaldas/bautizo) | `['María Bernal', 'Daniel Écija']` | `[]` | `['María Bernal', 'Daniel Écija']` | como en A (en A2 se había perdido). |
| se fueron | Daniel Écija | `['María Bernal', 'Daniel Écija']` | `['María Bernal']` | `[]` | **se pierde**: en A traía a los dos; A3 da `[]` (familia de espaldas con el bebé; única regresión). |
| Madrid 1966 | Daniel o "" | `[]` | `[]` | `['Daniel Écija', 'María Bernal']` | Daniel y María; aceptable para la tabla («Daniel o ""»), aunque el canon dice mid-20s y la escena ~30. |
| 1991 médico | "" | `[]` | `[]` | `['Daniel Écija']` | **Daniel a los 55**: la tabla esperaba `""`; el casillero pide «at the age the canon describes» (mid-20s) pero el canon trae `condition 1991-1992` y Opus lo incluyó. Ver e). |
| muere 55 | "" | `[]` | `[]` | `[]` | `[]`, correcto (cama vacía). |
| retrato pie | "" (solo el pie en la foto vieja) | `['Daniel Écija']` | `['Daniel Écija']` | `['Daniel Écija', 'María Bernal']` | ahora la foto es la familia entera con el pie vendado → Daniel y María; coherente con la escena. |
| clip pie | Daniel (Etapa C) | `[]` | `[]` | `['Daniel Écija']` | la foto del clip es el detalle del pie vendado («The bandaged foot…») y trae Daniel: contradice «[] if only a body part is shown» (en A y A2 daba `[]`). Ver e). |
| se llama Daniel | Daniel (Etapa C) | `['Daniel Écija']` | `['Daniel Écija']` | `['Daniel Écija']` | igual que A y A2. |

Cuenta sobre las ≈ 9 escenas de Daniel de la tabla (baile, boda, barco, mi marido, dos parejas, pista, mina ×2, se fueron): **A3 7 de 9** (faltan «dos parejas» y «se fueron»); A 1 de 9; A2 0 de 8.

## c) Falsos positivos

Fotos con Daniel en `persona` (A3): **13**. Ninguna es de la familia Calvo, de Milagros/Ramón solos ni de Eric Saint: las 13 tienen a Daniel en la ancla o en el párrafo («los Écija», «se casan», «mi marido», «su padre», «Daniel trabajaba»). Las fotos de Víctor Calvo (6), Milagros/Ramón y Eric Saint no traen a Daniel. Dudas que no son falsos positivos de identidad sino de regla: `chapters[0].image_prompt` (detalle del pie; regla «body part») y `chapters[4].img[12]` (1991, 55 años; regla de edad), en e).

## d) Venda: cada foto con Daniel

| foto | `persona` | year | ¿prompt con venda/cojera? | ancla |
|---|---|---|---|---|
| `chapters[0].image_prompt` | `['Daniel Écija']` | 1962 | sí | con el pie envuelto en una venda blanca |
| `chapters[0].supp[0]` | `['Daniel Écija', 'María Bernal']` | 1962 | sí | En el retrato de familia todos miran a cámara menos el pie: está vendado, y la herida que le hizo un trozo de … |
| `chapters[0].supp[1]` | `['Daniel Écija']` | 1962 | sí | El hombre se llama Daniel Écija y es minero. |
| `chapters[1].img[0]` | `['Daniel Écija', 'María Bernal']` | 1961 | no | Dieciséis de septiembre de mil novecientos sesenta y uno. En el salón de baile del Círculo de Bellas Artes de … |
| `chapters[1].img[1]` | `['Daniel Écija', 'María Bernal']` | 1962 | no | Un año después se casan: el jueves veinte de septiembre de mil novecientos sesenta y dos. |
| `chapters[1].img[3]` | `['Daniel Écija', 'María Bernal']` | 1962 | no | De Wittenoom no saben nada; saben que hay trabajo y que van juntos. |
| `chapters[1].img[4]` | `['María Bernal', 'Daniel Écija']` | 1962 | no | «Iba pegadita a mi marido, como una niña», recuerda su mujer. |
| `chapters[2].img[15]` | `['Daniel Écija', 'María Bernal']` | 1962 | no | En mil novecientos sesenta y uno la producción subió. Al año siguiente, los Écija bajaban de aquel avión. |
| `chapters[3].img[8]` | `['Daniel Écija', 'Ramón de Juan']` | 1962 | sí | Daniel trabajaba en la mina. Ramón de Juan, el amigo, hacía jornadas de dieciséis horas. |
| `chapters[3].img[9]` | `['Daniel Écija']` | 1962 | no | Uno de los hijos de Daniel cuenta que el primer día de trabajo de su padre hubo una explosión y murió gente. |
| `chapters[3].img[12]` | `['María Bernal', 'Daniel Écija']` | 1963 | sí | El bebé era muy grande. Lo sacaron con fórceps. Le pusieron Daniel, como el padre. Hay una foto del bautizo: s… |
| `chapters[4].img[4]` | `['Daniel Écija', 'María Bernal']` | 1966 | no | Ese mismo año, los Écija entran a su casa en Madrid. |
| `chapters[4].img[12]` | `['Daniel Écija']` | 1991 | no | Madrid, mil novecientos noventa y uno. Daniel Écija va al médico. Le hacen pruebas. La palabra es mesotelioma. |

Esperado: venda solo en el tramo de la herida (1962-1963 en Wittenoom). Resultado: venda en 5 fotos, todas de Wittenoom 1962-1963 (el retrato, el clip, «se llama Daniel», «Daniel trabajaba en la mina», el bautizo); sin venda en 1961 (baile), en la boda y el barco (antes de llegar), en la pista (llegada), en el primer día (antes de la herida), en Madrid 1966 y en 1991. Fotos de 1962-1963 sin venda: ['chapters[1].img[1]', 'chapters[1].img[3]', 'chapters[1].img[4]', 'chapters[2].img[15]', 'chapters[3].img[9]'] — todas anteriores a la herida o fuera de Wittenoom. **La venda dejó de ser identidad y pasó a ser estado por tramo.**

## e) María, Daniel hijo y confusiones de edad

- **¿Padre/hijo confundidos?** No: Daniel Écija hijo aparece en 1 foto, la del aeropuerto de 1985 (`chapters[4].img[8]`), y Daniel padre no está en ella. María: 9 fotos, todas de 1961-1966 y con Daniel salvo el hospital (`chapters[3].img[11]`).
- **¿Daniel en la escena de 1991 (55 años)?** **Sí**: `chapters[4].img[12]` («Daniel Écija va al médico») → `['Daniel Écija']`. El casillero pide «at the age the canon describes» (el canon dice «a mid-20s Spanish man», era 1962-1963), pero el canon también trae `condition 1991-1992: terminally ill…`, y Opus leyó ese tramo como parte de la persona. Para la Etapa B importa: la madre de Daniel sería la de un hombre de 25 y entraría en una foto de 55. La de la muerte (`chapters[4].img[13]`, cama vacía) da `[]`.
- **Detalle del pie (clip del cap 1):** `chapters[0].image_prompt` es «The bandaged foot of a slim mid-20s Spanish miner…» y `image_f8.persona` = `['Daniel Écija']`; la regla dice `[]` si solo se muestra una parte del cuerpo (A y A2 daban `[]`). Opus lo leyó como persona porque el prompt sigue con «The young miner stands still for a family photograph».
- **¿Víctor Calvo adulto?** No: sus 6 fotos son de 1962-1963 (`chapters[1].img[7]` (1962), `chapters[1].img[9]` (1962), `chapters[1].img[10]` (1962), `chapters[1].img[13]` (1962), `chapters[3].img[1]` (1963), `chapters[3].img[2]` (1963)).
- **Orden principal-primero:** en «mi marido» (`chapters[1].img[4]`) y en el bautizo (`chapters[3].img[12]`) María va primero; en el resto Daniel primero.

María:

| foto | `persona` | year | ancla |
|---|---|---|---|
| `chapters[0].supp[0]` | `['Daniel Écija', 'María Bernal']` | 1962 | En el retrato de familia todos miran a cámara menos el pie: está vendado, y la herida que le hizo un… |
| `chapters[1].img[0]` | `['Daniel Écija', 'María Bernal']` | 1961 | Dieciséis de septiembre de mil novecientos sesenta y uno. En el salón de baile del Círculo de Bellas… |
| `chapters[1].img[1]` | `['Daniel Écija', 'María Bernal']` | 1962 | Un año después se casan: el jueves veinte de septiembre de mil novecientos sesenta y dos. |
| `chapters[1].img[3]` | `['Daniel Écija', 'María Bernal']` | 1962 | De Wittenoom no saben nada; saben que hay trabajo y que van juntos. |
| `chapters[1].img[4]` | `['María Bernal', 'Daniel Écija']` | 1962 | «Iba pegadita a mi marido, como una niña», recuerda su mujer. |
| `chapters[2].img[15]` | `['Daniel Écija', 'María Bernal']` | 1962 | En mil novecientos sesenta y uno la producción subió. Al año siguiente, los Écija bajaban de aquel a… |
| `chapters[3].img[11]` | `['María Bernal']` | 1963 | Tres meses después le tocó a María. Llegó al hospital de Wittenoom debilitada por una infección rena… |
| `chapters[3].img[12]` | `['María Bernal', 'Daniel Écija']` | 1963 | El bebé era muy grande. Lo sacaron con fórceps. Le pusieron Daniel, como el padre. Hay una foto del … |
| `chapters[4].img[4]` | `['Daniel Écija', 'María Bernal']` | 1966 | Ese mismo año, los Écija entran a su casa en Madrid. |

Daniel hijo:

| foto | `persona` | year | ancla |
|---|---|---|---|
| `chapters[4].img[8]` | `['Daniel Écija hijo']` | 1985 | «Así que de Wittenoom, ¿eh? Un sitio terrorífico», dijo el policía. |

## f) Control de nombres (regla 19:35) sobre las 96 fotos

Nombres de `documented_people[].name` del canon nuevo (22), sin mayúsculas ni acentos, borde de palabra. **PARÁ (2+ palabras): 0.** Revisar (1 palabra): 1.

PARÁ: (ninguno)

Revisar:
- `chapters[6].supp[9]` · «Court» (nombre del canon «Court», 1 palabra → revisar) · prompt completo:

      Banjima representatives, Aboriginal Australian men and women of mixed ages in smart casual clothing, with white Australian lawyers in dark business suits, seen from behind. The group walks up the wide steps into the Federal Court building to lodge the case. Aboriginal Australian features, with dark brown skin, dark wavy to curly hair, brown eyes, and broad facial features. Exterior of the Federal Court of Australia building in Perth, 2026. Flat overcast daylight. Wide shot, low angle from the foot of the steps, deep depth of field, 28mm lens. A grainy 35mm documentary photograph taken in 2026, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.


## g) Prompt de video del cap 1

`image_f8.persona` = `['Daniel Écija']`. Foto del clip: «The bandaged foot of a slim mid-20s Spanish miner with tanned olive skin, a red-dusted work boot set aside beside it. The young miner stands still for a family photograph, weight shifted off the bandaged foot onto the other leg. Southern European features, wit…». Video prompt: «A slow, somber documentary close shot on grainy 35mm film, muted colors and slight underexposure in a dark-history realist style. The camera makes a slow push-in at ground level over eight seconds, starting on the bandaged foot and the red-dusted boot beside it and ending a little tighter on the white bandage. First, fine red dust and bluish fibrous grit drift lightly across the compacted earth, t…». **Conserva el pie vendado** (en la foto y en el movimiento: «starting on the bandaged foot… ending a little tighter on the white bandage»).

## h) Costo real

| qué | US$ |
|---|---|
| canon nuevo (Opus `claude-opus-5-5`, esfuerzo high) | 0.3437 |
| m03 7 caps (Opus casilleros + Flash; anclas fijas sin llamada de paso 1) | 2.2811 |
| **total A3** | **2.6248** |

## Suites y producción

Suites (`lab/hyperframes/f41/f60a3/`): ch02 md5 `f792f3d483a1fa42daed5f7f0e054f46` (candado; fase2b no importa m03, así que el md5 no depende del SI) · rápida 53 verdes + 3 skipped · amplia 1301 verdes + 31 skipped + 3 xfail + 4 fallas = las 4 previas (`m03_merge_timing` ×2, `gfx_lab` ×2). Producción tocada: `researcher_steps/step_4e_visual_canon.py` (BLOQUE 2, ejemplos, JSON, docstring, `_clean_person`) y `script_engine/m03_visual.py` (línea `condition` en PERSONAS, `TEXTO_PERSONA`). Stickers de los dos y MAPA (`--check` 0). Ningún test existente tenía estos textos literales (f50b/f50a/f51b/f50d/f50f/f59_a1/f58_a3 verdes sin tocar). Efecto declarado: `canon_ficha_md5` cambia para todos los temas (la próxima corrida de producción rehace su canon).

## Lo que queda abierto (A3)

1. Daniel a los 55 (`chapters[4].img[12]`): el tramo `condition 1991-1992` del canon hace que Opus lo cuente aunque el casillero pida la edad del canon. Decidir si el casillero dice que `condition` fuera de la era no cuenta, o si el canon de persona no lista tramos fuera de `era`, o si la Etapa B filtra por año.
2. Detalle del pie del clip (`chapters[0].image_prompt`) con `persona` = Daniel: contradice «body part». Etapa C lo va a leer.
3. «Se fueron» (`chapters[3].img[13]`, familia de espaldas con el bebé) perdió a Daniel y María (A los traía). Una corrida; puede ser ruido.
4. «Dos parejas» sigue sin los Écija (la ancla nombra solo a Milagros y Ramón): límite del «at most TWO» y de la lectura de la ancla.
5. Opus rehízo grupos y era con ids nuevos: m06/foto madre de grupos y cualquier cosa que guarde ids de `people_groups` de Wittenoom cambia en la próxima corrida de producción (efecto declarado del handoff; no se tocó producción de datos).
6. Canon: Eric Saint «middle-aged» (antes «young adult»), Orellana sin nacionalidad: variación de Opus sobre la misma ficha.
7. «Court» como sustantivo sigue en «revisar».
