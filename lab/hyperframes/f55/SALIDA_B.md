# F55 — Salida B (texto): dedupe de citas del pool de Wittenoom

Regla: mismo autor (igualdad exacta tras `norm`) + |Ca∩Cb| / min(|Ca|,|Cb|) ≥ 0.7 (DECISIONES 2026-10-29 19:30). Citas: 58 → 50. Escrito en topics_db.json y 01_facts_sources.json.

## 1. Los pares: cuál quedó y por qué

| sale | queda | similitud | autor | n_fuentes (sale → queda) | por qué queda | texto que sale | texto que queda |
|---|---|---|---|---|---|---|---|
| Q12 | Q25 | 0.88 | María Bernal | 1 → 2 (docs ['F08', 'F07']) | más larga (empate en fuentes) | Iba pegadita a mi marido, como una niña. Pero estaba orgullosa. Me había enamorado de aque | Me pegué a mi marido, como una niña pequeña. Pero estaba orgullosa. Me había enamorado de  |
| Q26 | Q14 | 0.88 | Víctor Calvo | 1 → 2 (docs ['F07', 'F08']) | más larga (empate en fuentes) | Salimos de Málaga y tardamos más de 20 días en barco en llegar a Australia. Pasamos por el | Salimos de Málaga y tardamos más de 20 días en llegar en barco a Australia. Pasamos por el |
| Q15 | Q27 | 0.9 | Víctor Calvo | 1 → 2 (docs ['F08', 'F07']) | más larga (empate en fuentes) | El avión era pequeño, de hélices, y se movía muchísimo. Aterrizamos en una pista en medio  | El avión era pequeño, de hélice, y se movía mucho. Aterrizamos en una pista en medio de un |
| Q28 | Q16 | 0.89 | Daniel Écija (hijo) | 1 → 2 (docs ['F07', 'F08']) | más larga (empate en fuentes) | El primer día de trabajo de nuestro padre hubo una explosión y murieron varias personas. C | El primer día de trabajo de nuestro padre hubo una explosión y murieron varias personas. Y |
| Q29 | Q17 | 0.73 | Víctor Calvo | 1 → 2 (docs ['F07', 'F08']) | más larga (empate en fuentes) | Apenas había medidas de seguridad. Había muchos accidentes y las ambulancias venían todo e | No tenían apenas medidas de seguridad. Había muchos accidentes y cada dos por tres aparecí |
| Q30 | Q18 | 0.92 | Daniel Écija (hijo) | 1 → 2 (docs ['F07', 'F08']) | más larga (empate en fuentes) | Mi padre describía Wittenoom como un lugar sin ley. Un pueblo con una vida bastante primit | Mi padre nos habló de Wittenoom como un lugar sin ley. Un pueblo con una vida bastante pri |
| Q20 | Q33 | 0.94 | Melita Markey | 1 → 2 (docs ['F08', 'F07']) | más larga (empate en fuentes) | El Gobierno dejó de contar en 2.000, pero ahora se calcula que la cifra puede ser superior | El gobierno dejó de contar en 2000, pero ahora se estima que la cifra puede ser superior a |
| Q23 | Q35 | 0.71 | Daniel Écija (hijo) | 1 → 2 (docs ['F08', 'F07']) | más larga (empate en fuentes) | Ese sitio nos cambió la vida para siempre. Nosotros nos quedamos sin padre, y mi madre sin | Ese lugar cambió nuestras vidas para siempre. Perdimos a nuestro padre, y mi madre perdió  |

Pares que NO se deduplican (control del handoff §4):

- Q30/Q36: similitud no se compara (autores distintos o sin autor) · autores «Daniel Écija (hijo)» / «Un oficial de policía»
- Q18/Q36: similitud no se compara (autores distintos o sin autor) · autores «Daniel Écija (hijo)» / «Un oficial de policía»
- Q19/Q32: similitud 0.50 · autores «Víctor Calvo» / «Víctor Calvo»

## 2. Qué apunta hoy a ids descartados (solo listar; la Parte D regenera todo desde la escaleta)

| archivo | dónde | id | debería ser |
|---|---|---|---|
| 01a_escaleta.json | beats[1].datos_apoyo[2] | Q12 | Q25 |
| 01a_escaleta.json | beats[2].datos_apoyo[0] | Q15 | Q27 |
| 01a_escaleta.json | beats[8].datos_apoyo[1] | Q23 | Q35 |
| 01a_escaleta.json | beats[12].datos_apoyo[2] | Q20 | Q33 |
| 01a_escaleta.json | caps[1].evidence_ids[3] | Q12 | Q25 |
| 01a_escaleta.json | caps[1].evidence_ids[8] | Q15 | Q27 |
| 01a_escaleta.json | caps[4].evidence_ids[9] | Q23 | Q35 |
| 01a_escaleta.json | caps[6].evidence_ids[10] | Q20 | Q33 |
| 01a_skeleton.json | chapters[1].evidence_ids[3] | Q12 | Q25 |
| 01a_skeleton.json | chapters[1].evidence_ids[8] | Q15 | Q27 |
| 01a_skeleton.json | chapters[4].evidence_ids[9] | Q23 | Q35 |
| 01a_skeleton.json | chapters[6].evidence_ids[10] | Q20 | Q33 |
| 01b_guionista_v4.json | parrafos[1].ids_usados[5] | Q12 | Q25 |
| 01b_guionista_v4.json | parrafos[12].ids_usados[0] | Q23 | Q35 |
| 01b_guionista_v4.json | reparacion.parrafos[1].ids_usados[5] | Q12 | Q25 |
| 01b_guionista_v4.json | reparacion.parrafos[12].ids_usados[0] | Q23 | Q35 |
| 01b_narration.json | chapters[1].datos_usados[5] | Q12 | Q25 |
| 01b_narration.json | chapters[1].ids_usados[5] | Q12 | Q25 |
| 01b_narration.json | chapters[4].datos_usados[6] | Q23 | Q35 |
| 01b_narration.json | chapters[4].ids_usados[6] | Q23 | Q35 |
| 01e_pantalla.json | descartados[5].pool_id | Q15 | Q27 |
| 01e_pantalla.json | descartados[12].pool_id | Q23 | Q35 |

Total de referencias a ids descartados: 22.

## 3. Las tres copias del pool (D.0)

| copia | citas | ids de citas | descartados (citas) |
|---|---|---|---|
| topics_db.json | 50 | Q01, Q02, Q03, Q04, Q05, Q06, Q07, Q08, Q09, Q10, Q11, Q13, Q14, Q16, Q17, Q18, Q19, Q21, Q22, Q24, Q25, Q27, Q31, Q32, Q33, Q34, Q35, Q36, Q37, Q38, Q39, Q40, Q41, Q42, Q43, Q44, Q45, Q46, Q47, Q48, Q49, Q50, Q51, Q52, Q53, Q54, Q55, Q56, Q57, Q58 | Q12, Q15, Q20, Q23, Q26, Q28, Q29, Q30 |
| 01_facts_sources.json | 50 | Q01, Q02, Q03, Q04, Q05, Q06, Q07, Q08, Q09, Q10, Q11, Q13, Q14, Q16, Q17, Q18, Q19, Q21, Q22, Q24, Q25, Q27, Q31, Q32, Q33, Q34, Q35, Q36, Q37, Q38, Q39, Q40, Q41, Q42, Q43, Q44, Q45, Q46, Q47, Q48, Q49, Q50, Q51, Q52, Q53, Q54, Q55, Q56, Q57, Q58 | Q12, Q15, Q20, Q23, Q26, Q28, Q29, Q30 |
| 00_pool_v3.json | 50 | Q01, Q02, Q03, Q04, Q05, Q06, Q07, Q08, Q09, Q10, Q11, Q13, Q14, Q16, Q17, Q18, Q19, Q21, Q22, Q24, Q25, Q27, Q31, Q32, Q33, Q34, Q35, Q36, Q37, Q38, Q39, Q40, Q41, Q42, Q43, Q44, Q45, Q46, Q47, Q48, Q49, Q50, Q51, Q52, Q53, Q54, Q55, Q56, Q57, Q58 | Q12, Q15, Q20, Q23, Q26, Q28, Q29, Q30 |

Las tres copias tienen los MISMOS ids de citas y los mismos descartados.

Log:

    [dedupe citas] Q12 → Q25 (0.88); Q26 → Q14 (0.88); Q15 → Q27 (0.9); Q28 → Q16 (0.89); Q29 → Q17 (0.73); Q30 → Q18 (0.92); Q20 → Q33 (0.94); Q23 → Q35 (0.71)

Escrito: `C:\CLAUDE_PROJECTS\automatization_videos\data\topics_db.json` (respaldo `topics_db.pre_f55_dedupe.json`), `C:\CLAUDE_PROJECTS\automatization_videos\data\scripts\_steps\123bbb64-9fca-4395-8bf4-57d60e219ef1\01_facts_sources.json` y `C:\CLAUDE_PROJECTS\automatization_videos\data\scripts\_steps\123bbb64-9fca-4395-8bf4-57d60e219ef1\00_pool_v3.json` (su copia de antes: `C:\CLAUDE_PROJECTS\automatization_videos\lab\hyperframes\f55\antes\00_pool_v3.json`).