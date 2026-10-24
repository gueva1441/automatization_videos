### Resumen

| corrida | modelo · guion | palabras | min | bloqueantes | citas | personas con nombre | cierre | US$ |
|---|---|---|---|---|---|---|---|---|
| sol52a | gpt-6.1-sol · v5.2 | 939 | 7.6 | 0 | 7 | 13 | pregunta | 0.0968 |
| sol52b | gpt-6.1-sol · v5.2 | 846 | 6.9 | 0 | 7 | 11 | pregunta | 0.1372 |
| sol51 | gpt-6.1-sol · v5.1 | 803 | 6.5 | 0 | 7 | 13 | pregunta | 0.1209 |
| opus52a | claude-opus-5-5 · v5.2 | 1144 | 9.3 | 0 | 9 | 13 | pregunta | 0.3261 |
| opus52b | claude-opus-5-5 · v5.2 | 1159 | 9.4 | 0 | 8 | 13 | pregunta | 0.3086 |
| F22 (ref.) | gpt-6.1-sol · v5.2 | 838 | 6.8 | 0 | 7 | 13 | pregunta | — |
| F16 (ref.) | gpt-6.1-sol · v5.1 · escaleta F16 | 1384 | 11.3 | 0 | 9 | 24 | cita | — |

### Por cap (palabras · personas con nombre · citas · bloqueantes)

| cap | sol52a | sol52b | sol51 | opus52a | opus52b | F22 (ref.) | F16 (ref.) |
|---|---|---|---|---|---|---|---|
| 1 | 90 · 1p · 1c · 0b | 84 · 1p · 1c · 0b | 79 · 1p · 1c · 0b | 130 · 1p · 1c · 0b | 136 · 1p · 1c · 0b | 82 · 1p · 1c · 0b | 94 · 1p · 1c · 0b |
| 2 | 99 · 2p · 0c · 0b | 92 · 2p · 0c · 0b | 91 · 2p · 0c · 0b | 126 · 3p · 0c · 0b | 131 · 3p · 0c · 0b | 88 · 2p · 0c · 0b | 129 · 4p · 1c · 0b |
| 3 | 119 · 1p · 1c · 0b | 119 · 1p · 1c · 0b | 108 · 1p · 1c · 0b | 145 · 1p · 1c · 0b | 145 · 1p · 1c · 0b | 112 · 1p · 1c · 0b | 295 · 7p · 2c · 0b |
| 4 | 109 · 2p · 1c · 0b | 106 · 2p · 1c · 0b | 102 · 2p · 1c · 0b | 146 · 2p · 1c · 0b | 136 · 2p · 1c · 0b | 102 · 2p · 1c · 0b | 177 · 4p · 1c · 0b |
| 5 | 109 · 1p · 2c · 0b | 107 · 1p · 2c · 0b | 85 · 1p · 2c · 0b | 106 · 2p · 1c · 0b | 171 · 1p · 2c · 0b | 107 · 1p · 2c · 0b | 46 · 0p · 1c · 0b |
| 6 | 158 · 1p · 0c · 0b | 143 · 1p · 0c · 0b | 130 · 1p · 0c · 0b | 215 · 5p · 1c · 0b | 164 · 3p · 0c · 0b | 143 · 1p · 0c · 0b | 340 · 6p · 0c · 0b |
| 7 | 255 · 6p · 2c · 0b | 195 · 3p · 2c · 0b | 208 · 5p · 2c · 0b | 276 · 9p · 4c · 0b | 276 · 9p · 3c · 0b | 204 · 5p · 2c · 0b | 303 · 8p · 3c · 0b |

### Personas con nombre por cap

| corrida | personas con nombre por cap |
|---|---|
| sol52a | 1: Liz Torres · 2: Alfredo Vallovera, Benedicto Pérez · 3: Beatriz González · 4: Digna Felicia Cáceres, Víctor Galeano · 5: Tatiana Gabaglio · 6: Nelson Astigarraga · 7: Antonio Morínigo, Daniel Areco, Juan Pío Helvidio Paiva Escobar, Luis Escobar Faella, Víctor Daniel Paiva, Víctor Galeano |
| sol52b | 1: Liz Torres · 2: Alfredo Vallovera, Benedicto Pérez · 3: Beatriz González · 4: Digna Felicia Cáceres, Víctor Galeano · 5: Tatiana Gabaglio · 6: Nelson Astigarraga · 7: Antonio Morínigo, Juan Pío Helvidio Paiva Escobar, Luis Escobar Faella |
| sol51 | 1: Liz Torres · 2: Alfredo Vallovera, Benedicto Pérez · 3: Beatriz González · 4: Digna Felicia Cáceres, Víctor Galeano · 5: Tatiana Gabaglio · 6: Nelson Astigarraga · 7: Antonio Morínigo, Daniel Areco, Juan Pío Helvidio Paiva Escobar, Luis Escobar Faella, Víctor Daniel Paiva |
| opus52a | 1: Liz Torres · 2: Alfredo Vallovera, Benedicto Pérez, Liz Torres · 3: Beatriz González · 4: Digna Felicia Cáceres, Víctor Galeano · 5: Liz Torres, Tatiana Gabaglio · 6: Alfredo Vallovera, Digna Felicia Cáceres, Liz Torres, Nelson Astigarraga, Tatiana Gabaglio · 7: Antonio Morínigo, Daniel Areco, Digna Felicia Cáceres, Juan Pío Helvidio Paiva Escobar, Liz Torres, Luis Escobar Faella, Tatiana Gabaglio, Víctor Daniel Paiva, Víctor Galeano |
| opus52b | 1: Liz Torres · 2: Alfredo Vallovera, Benedicto Pérez, Liz Torres · 3: Beatriz González · 4: Digna Felicia Cáceres, Víctor Galeano · 5: Tatiana Gabaglio · 6: Digna Felicia Cáceres, Nelson Astigarraga, Tatiana Gabaglio · 7: Antonio Morínigo, Daniel Areco, Digna Felicia Cáceres, Juan Pío Helvidio Paiva Escobar, Liz Torres, Luis Escobar Faella, Tatiana Gabaglio, Víctor Daniel Paiva, Víctor Galeano |
| F22 (ref.) | 1: Liz Torres · 2: Alfredo Vallovera, Benedicto Pérez · 3: Beatriz González · 4: Digna Felicia Cáceres, Víctor Galeano · 5: Tatiana Gabaglio · 6: Nelson Astigarraga · 7: Antonio Morínigo, Daniel Areco, Juan Pío Helvidio Paiva Escobar, Luis Escobar Faella, Víctor Daniel Paiva |
| F16 (ref.) | 1: Liz Torres · 2: Alfredo Vallovera, Blas Cristaldo, Teresa Urbieta, Ángela Pujol · 3: Beatriz González, Benedicto Pérez, Carlos Halke, Cristian Sosa, Enrique Riera, Martín Burt, Víctor Galeano · 4: Alejandro Nissen, Digna Felicia Cáceres, Tatiana Gabaglio, Víctor Galeano · 5: — · 6: Cristian Sosa, Juan Pío Helvidio Paiva Escobar, Luis Escobar Faella, Nelson Astigarraga, Rubén Urbieta, Víctor Galeano · 7: Daniel Areco, Digna Felicia Cáceres, Edgar Sánchez, Ismael Alcaraz, Juan Pío Helvidio Paiva Escobar, Luis Escobar Faella, María Estela Morínigo Giménez de Palacios, Teresa Sosa |

Tanda F22b: US$ 0.9897 de 4.00 (incluye la llamada de prueba de la llave).
