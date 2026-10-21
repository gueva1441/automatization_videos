# RESUMEN F5c — narración: skeleton congelado, narrador Pro, mejor de 3 · PARADA para el analista

Rama `f5-guion-v2`, desde `2fbac37`. Solo narración: la pantalla y §1.6 de F5b quedan igual. Sin imágenes ni render. `main` intacta. Decisiones: `DECISIONES_F5.md` L1–L8.

## En una línea
Los datos vuelven: densidad por id 2.16 (F5b 1.26), por hecho 1.97 (F5 2.01). Los cliffhangers pasan a 6 de 6, Gusman vuelve al cap 1, y no hay contaminación ni cifras inventadas. A cambio, el guion es más corto (1017 palabras), los adjetivos quedan debajo del piso (1.87) y las fórmulas repetidas entre caps suben a 8.6 %. El narrador Pro costó **US$ 0.69**.

## Lo que se hizo
1. **Skeleton congelado** (token `skeleton_frozen`): el de F5 (`e7b661c`), con sus ids traducidos al pool de F5b. Salen D71 (el médium), Hubert y Schwarz. Gusman y Hunter entran en el cap 1 (L1).
2. **Narrador Gemini Pro** solo en los 7 caps de m01b. Todo lo demás sigue con Flash. **Costo: US$ 0.69 de Pro (20 llamadas) + US$ 0.0025 de Flash (1)** (`v2/01b_costo.json`) (L2).
3. **Prioridad de reglas**, en el prompt y en el validador (`cap_review`):
   - duras: no inventar, datos asignados una vez y literales, no contaminar, cliffhanger con el dato; además el relleno prohibido (L3);
   - blandas: adjetivos y 3-gramas, con aviso y un solo reintento;
   - el prompt lleva la frase literal: «Si no podés cumplir todo, sacrificá la ventana de adjetivos, nunca los datos ni los nombres.»
4. **Mejor de 3 por cap**, con el puntaje del analista. Elegidos: cap 1 el 2.º, cap 2 el 1.º, cap 3 el 2.º, caps 4 y 5 el 3.º, cap 6 el 1.º y cap 7 el 2.º (de 2). No es «el último»: en los caps 2 y 6 ganó el primero (L5).
5. **Relleno prohibido:** se suman las 8 frases del analista (L6).

## Narración
| | v1 | v2 F5 | v2 F5b | v2 F5c |
|---|---|---|---|---|
| conteo | regex | regex | por id | por id |
| densidad por id | — | — | 1.26 | **2.16** |
| densidad por hecho (anclas distintas) | 0.86 | 2.01 | 1.12 | **1.97** |
| datos distintos del pool | 12 | 41* | 18 | 21 |
| palabras | 1398 | 1397 | 1431 | **1017** |
| adjetivos/100 (2–4) | 6.22 | 2.93 | 4.19 | 1.87 |
| caps fuera de 2–4 | 7 | 5 | 5 | 3 (1, 2, 6) |
| 3-gramas repetidos entre caps (< 5 %) | 3.4 % | 4.1 % | 7.0 % | **8.6 %** |
| caps con un dato repetido dentro del cap | 2 | 6 | 0 | 1 (cap 3: «29 de agosto» ×2) |
| datos en más de 2 caps | 2 | 0 | 0 | 0 |
| nombres sin acción · contaminación | — | Hubert, Schwarz · 1902, médium | ninguno | **ninguno** |
| cliffhanger con el dato | — | 4/6 | 4/6 | **6/6** |
| Gusman nombrado en caps | ninguno | 6 caps (desde el 1) | 2, 3, 5, 6 | **1, 2, 3, 5** |

\* El 41 de F5 se contó por regex: un «29 de agosto» prendía varios ids.

**Abierto:**
- 2 caps aceptan una regla dura: el cap 1 declaró D04 sin que suene literal, y el cap 3 dice «29 de agosto» dos veces y declaró T12. Ningún candidato de esos caps salió sin duras.
- Los 3-gramas los empujan el cap 7 (21 % de fórmulas ya dichas) y el cap 5 (14 %).
- El texto más corto viene de que Pro escribe cerca del piso del largo en caracteres.

## Pantalla (mismo código F5b, guion F5c)
- Chequeo S1–S5: **0 fallas**.
- 3 recortes, todos del pool (F5b 5, F5 7). Crítico: suma 26, repite 3, estorba 3. Reloj en 3 caps, pregunta en 6.
- El cap 6 sigue sin recorte: sus candidatos chocan con otros bloques o la voz no los cuenta. El 7 tampoco tiene: ninguna cláusula completa suma con fuente o fecha.
- Un ícono en «tóxica» (calavera): está en el mapa literal del perfil, así que cumple S4.

## Prompts de imagen de v2 (texto)
- 97 prompts, 42 con personas: `PROMPTS_PERSONAS_v2.md`.
- **El que reemplaza al del niño en la celda: ch05 imagen 6** («Entre los rostros anónimos de esa tragedia había niños de hasta 10 años»). Es un chico en el agua dentro de un centro juvenil («youth detention facility»).
- ch05 imagen 7 también va al centro juvenil.
- **Queda uno:** ch04 imagen 13, un recluso adolescente solo en una celda de la prisión. Su ancla («Cuatro días en la oscuridad, en el agua sucia») no nombra niños y el canon no lo frena (K20).

## Dónde está
- Código:
  - `script_engine/m01a_skeleton.py` (`frozen_skeleton`);
  - `script_engine/m01b_narrator.py` (`_best_of_n`, `POOL_NARRATOR`, `POOL_BEST_OF`, reglas en el prompt);
  - `script_engine/m05_narrative.py` (`cap_review`, `invented_numbers`, `contamination`, `trigram_vs_previous`, relleno).
- Tests: `test_module_f5c.py` (nuevo, 6). Suites de guion y gfx: **385 verdes** + 3 fallas viejas de `01b_pauses`.
- Skeleton y pool de F5: `lab/hyperframes/f5/f5c/`.
- Comparación: `lab/guion/compara_orleans.html` (v1 · F5 · F5b · F5c). Tablas: `GUION_v1_v2.md`, `SIM_v1_v2.md`. Copias: `v2/` (F5c), `v2_f5b/`, `v2_f5/`.
- Se reproduce con `correr_f5_orleans.py --etapa todo`.
- md5 de `topics_db.json`, `normalizer_custom_dict.json`, `lexico_propuestas.json` y `misterio.json`: iguales a los de F5b.

## Veredicto del revisor (revisor-handoff, íntegro; dado antes del commit)

VEREDICTO: CUMPLE CON OBSERVACIONES

Tests: 385 passed + 3 failed (los 3 viejos de test_module_01b_pauses), igual que lo esperado. Bytes 0x08 en .py: ninguno. Los gfx_*.py y m03_visual.py no aparecen en git status, así que no cambiaron.

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Skeleton congelado de e7b661c, ids traducidos, sin Flash, sin Hubert | OK | `frozen_skeleton` (m01a_skeleton.py, diff +55) se dispara con `topic["skeleton_frozen"]` antes de cualquier llamada a Flash. Comparé el 01a_skeleton.json de `ba6c3cac-f5v2` con `git show e7b661c:…/01a_skeleton.json`: caps 1–5 idénticos. El cap 6 cambia D72→D69 (la traducción), y el cap 5 cambia el cliffhanger D72→D69 por la misma traducción. El cap 7 pierde D71 (el médium, fuera del pool actual). Personajes: salen Hubert y Schwarz, quedan 6 de 8. Todo está en `_frozen.notas`. El RESUMEN dice que Hubert queda fuera porque solo es el demandado, y eso concuerda. |
| 2 | Pro solo en los 7 caps de m01b, Flash en el resto, costo reportado | OK | `_call_narrator` usa `call_pro_json` si el modelo es "pro". `POOL_NARRATOR="pro"` se aplica solo con pool; sin pool se llama a `_call_with_length_retry` con Flash, como antes. 01b_costo.json: Pro US$0.69, Flash US$0.0025, total 0.6926, 21 llamadas. Los candidatos suman 20 llamadas de Pro (3+3+3+3+3+3+2), que es lo que dice el RESUMEN. El único Flash es el de humanizer_phrases. |
| 3 | Reglas duras y blandas en prompt y validador, frase literal | OK | La frase literal está en m01b_narrator.py, bloque "PRIORIDAD DE LAS REGLAS (F5c)". El validador es `cap_review`, que devuelve hard y soft por separado. Las blandas (adjetivos y 3-gramas) reintentan una sola vez (`soft_retry`) y nunca rechazan. |
| 4 | Mejor de 3 por puntaje, no el último | OK | Recalculé el criterio de `_best_of_n` (sin duras → mayor puntaje → menos blandas → menor k) sobre `_f5c_candidatos`, y los 7 elegidos coinciden con el mejor por puntaje. Elegidos: cap1=2 (13), cap2=1 (10), cap3=2 (11), cap4=3 (11), cap5=3 (23), cap6=1 (10), cap7=2 (15). Hay dos observaciones: en el cap 6 los tres candidatos empatan en 10 y gana el primero por desempate. En el cap 2 el candidato 3 tenía puntaje 11 contra 10 del elegido (1), pero el 3 tiene 1 dura y el 1 tiene 0. Eso sale de las reglas del propio contrato. |
| 5 | Ocho frases de relleno nuevas | OK | Las 8 frases están en la regla F del prompt (diff de m01b). El RESUMEN cita L6 para las del validador; no leí `FORBIDDEN_FILLER` directamente. |
| 6 | Regenerar v2, compara_orleans.html (columna F5c), re-simular 7 caps, prompts de imagen con anclas con personas, commit, RESUMEN | PARCIAL | Existen RESUMEN_F5c.md, PROMPTS_PERSONAS_v2.md, SIM, los cues y v2/ regenerados, y los .out de pruebas. Las cifras que cotejé coinciden con los datos: 1017 palabras (conté 1017 en 01b_narration.json), densidad 2.16 y 3-gramas 8.6 % (aparecen en GUION_v1_v2.md), 21 % del cap 7, y el cap 1 con D04 declarado sin ser literal y el cap 3 con «29 de agosto» ×2 (están en `_f5_violations`). No verifiqué el HTML ni los 97 prompts de imagen. El commit no existe todavía: HEAD sigue en 2fbac37 y todo está sin commitear. La sección "Veredicto del revisor" del RESUMEN dice "(se pega abajo, íntegro)", o sea que está vacía. |

Lo no logrado está declarado en el RESUMEN, con una excepción. Declara las 2 reglas duras aceptadas (cap 1 y cap 3), los adjetivos bajo el piso (1.87), los 3-gramas en 8.6 % contra el umbral de 5 %, el texto más corto y la ausencia de recortes en los caps 6 y 7. Lo que falta decir es que el cap 3 también acepta una cuarta violación dura: «29 de agosto» ×2. Además, `_f5_violations` del cap 3 lista solo 2 duras, y el candidato elegido (2) figura con "duras: 2", lo que coincide con eso.

Fuera de alcance: ninguno en código de pantalla (gfx_*.py y m03_visual.py intactos). Se tocaron m01a_skeleton.py, m01b_narrator.py y m05_narrative.py, todos dentro del pedido. diag_234_cap4.py aparece modificado, pero el pedido dice que NO es nuestro. No debe entrar al commit.

Riesgos que el contrato no cubre:
- El guion quedó 29 % más corto (1017 contra 1431 palabras) con Pro apuntando al piso del largo, y eso baja el tiempo de pantalla.
- Hay 2 caps con reglas duras aceptadas (datos no literales o repetidos). Esto va contra la prioridad "duras rechazan" y depende de que el analista lo apruebe.
- Falta commitear y pegar este veredicto en el RESUMEN.
