# F22c_REPORT — ¿la escaleta con columna sale más floja que sin columna?

2026-10-24 · rama `f11-guion-v4` sobre `cd5fde5` · **US$ 2.8094 de 3.00 → PARADA por tope** (faltan B2 completo y K) · sin merge · cero cambios de código fuera de `lab/` (el modelo del guion ya se elegía con `guion_v4.call_for`, F22b).

## 0. Respuesta
**Sí, con la columna la escaleta sale más flaca de datos**, y el guion de Opus lo hereda:

| | sin columna (A1 · A2) | con columna (B1 · F22) |
|---|---|---|
| ids distintos en la escaleta | 54 · 55 | 32 · 31 |
| apoyos por beat | 2.36 · 2.43 | 1.00 · 0.93 |
| `a_pantalla` | 7 · 7 | 4 · 4 |
| palabras de imagen sensorial por beat | 28.6 · 35.5 | 31.5 · 32.6 |
| beats | 14 · 14 | 14 · 14 |
| guion Opus 5.5 v5.2: palabras | 1,590 · 1,604 | 1,332 (B1) · 1,144 / 1,159 (F22b, escaleta F22) |
| personas con nombre en el guion | 24 · 24 | 13 · 13 / 13 |
| citas | 11 · 13 | 8 · 9 / 8 |

- Mismos beats e imágenes de largo parecido: lo que pierde la escaleta con columna son **apoyos** (de ~2.4 a ~1 por beat) y por eso **ids** (≈ 40 % menos). Es coherente con la columna: el `<oficio>` 2 pide «cinco o seis personas en todo el video» y la tarea de la escaleta con columna dice «las personas de cada cap son las que la columna nombra». La escaleta sin columna mete 24 personas; con columna, 13.
- Con Opus, sin columna el guion llega a **≈ 13 min** (1,590–1,604 palabras, más que F16 con Sol: 1,384); con columna, 9.3–10.8 min.
- «Más flojo» en datos y largo, no en bloqueantes: los cinco guiones (tres nuevos + los dos de referencia) salieron con **0 bloqueantes** y cero Cardal. Si la página con menos personas es mejor o peor para el espectador es una lectura del analista: los caps 3 y 6 sin columna nombran 7–11 personas cada uno.
- Muestra chica: dos escaletas sin columna contra una con columna nueva más la de F22 (B2 no llegó a guion por el tope).

## 1. Qué se corrió
Runner `f22c_corridas.py` (Ycuá con la ficha v2 de F15b y el perfil del seed; Kyshtym con su ficha de F22):
- **A1, A2:** escaleta v2.1 **sin columna** (`generate_escaleta(columna=None)`, que es lo que hace `fase1_5 --sin-columna`), Sol high → guion Opus 5.5 v5.2 (effort high).
- **B1, B2:** escaleta v2.1 **con la columna de F22** (`lab/hyperframes/f22/columna_ycua_f22.json`, sin regenerar), Sol high → guion Opus 5.5 v5.2.
- **K:** guion Opus 5.5 v5.2 sobre `escaleta_kyshtym_f22.json` tal cual.
- Las escaletas no se guardaron en `_steps` (no se pisó `01a_escaleta_f22.json`): `escaleta_ycua_f22c_<tag>.json` + `ESCALETA_ycua_f22c_<tag>.md`. Freno antes de cada llamada (lo gastado + el peor caso ≤ US$ 3.00), una facturación por llamada; escaleta con sus 13 bloqueantes y una regeneración; guion sin reparación.

## 2. Qué pasó (en orden)
1. **A1:** escaleta en la regeneración (16 → 0 bloqueantes, US$ 0.28). Guion, **intento 1 cortado**: le di a Opus 20,000 tokens de salida (F22b había usado 24,000) y se cortó en `max_tokens` con el JSON a medias: US$ 0.448 perdidos (`guion_ycua_f22c_A1_intento1_cortado.json`). Subí a 32,000 y rehice el guion (US$ 0.475). **Error mío de dimensionamiento.**
2. **B1:** escaleta en la regeneración (14 → 0, US$ 0.274); guion US$ 0.391.
3. **A2:** escaleta en la regeneración (8 → 0, US$ 0.305); guion US$ 0.503.
4. **B2:** escaleta intento 1 con 12 bloqueantes (US$ 0.134); el freno cortó el intento 2 (US$ 2.809 + peor caso 0.242 > 3.00). **PARADA.** El crudo del intento 1 está en `escaleta_crudos_ycua_f22c_B2.json` (el `_rechazada.json` registra el corte por tope, no un rechazo de los bloqueantes).
5. **K: no corrió.**
Los primeros intentos de las cuatro escaletas fallaron por lo mismo que en F22: un `P13, P80: …` como dato central del beat 2 y varios ids de `a_pantalla` también en beats.

## 3. Tablas
#### Escaletas

| escaleta | columna | beats | beats por cap | ids totales | a_pantalla | apoyos/beat | palabras de imagen (total · por beat) | intentos (bloqueantes) |
|---|---|---|---|---|---|---|---|---|
| A1 | sin columna | 14 | [1, 2, 2, 2, 1, 3, 3] | 54 | 7 | 2.36 | 400 · 28.6 | [16, 0] |
| A2 | sin columna | 14 | [1, 1, 2, 2, 1, 3, 4] | 55 | 7 | 2.43 | 497 · 35.5 | [8, 0] |
| B1 | con columna | 14 | [1, 2, 2, 2, 2, 3, 2] | 32 | 4 | 1.0 | 441 · 31.5 | [14, 0] |
| B2 | con columna | no salió | | | | | | |
| F22 (ref.) | con columna | 14 | [1, 2, 2, 2, 2, 3, 2] | 31 | 4 | 0.93 | 456 · 32.6 | [8, 0] |
| K | Kyshtym F22 | 14 | [1, 1, 2, 2, 2, 2, 4] | 35 | 3 | 1.29 | 427 · 30.5 | [4, 0] |

#### Promesa del gancho y cierre humano (textuales)

| escaleta | promesa_gancho | cierre_humano |
|---|---|---|
| A1 | «Vas a entender cómo una compra terminó en encierro, por qué fue condenado el dueño y qué siguió faltando a quienes salieron con vida.» | «Volver a Liz con Q77: «Soy la vida de muchas personas que cayeron sobre mi cuerpo, me salvaron la vida». La posibilidad de cobrar las reparaciones queda abierta en el beat anterior; después de esta frase no hay moraleja ni explicación.» |
| A2 | «Vas a entender cómo una huida se convirtió en un encierro, qué se discutió sobre las puertas y qué quedó sin resolver después de las condenas.» | «Volver a Liz con Q77: «Soy la vida de muchas personas que cayeron sobre mi cuerpo, me salvaron la vida». Después, dejar abierta la pregunta por la reparación efectiva, sin transformar su supervivencia en una moraleja.» |
| B1 | «Vas a entender qué encontraron quienes intentaron salir, por qué las versiones sobre las puertas se contradicen y qué quedó sin reparar después de las condenas.» | «Volver a Liz como sobreviviente que integra el reclamo organizado, sin atribuirle la demanda del matrimonio Palacios Morínigo. Cerrar con la pregunta pendiente sobre la posibilidad de cobrar las reparaciones.» |
| F22 (ref.) | «Vas a entender qué encontraron quienes intentaban salir, por qué la pericia discutió sus relatos y hasta dónde llegó la condena del dueño.» | «Volver a Liz como integrante de organizaciones de víctimas, sin adjudicarle la indemnización obtenida por otro matrimonio. Terminar con la pregunta: «¿Podrán los sobrevivientes y familiares convertir las sentencias en una reparación económica efectiva, si el principal demandado murió y ni su abogado sabe si quedan bienes de la sociedad para cobrar?»» |
| K | «Vas a entender qué salió de aquel almacenamiento, cómo quedó sin explicación pública y por qué reconocer a sus afectados terminó siendo otra disputa.» | «Volver al técnico del comienzo, sin repetir su testimonio ni atribuirle un destino posterior. Su experiencia no permite contar a todos los afectados. Cerrar con la pregunta pendiente: ¿Cuántas personas afectadas por Mayak quedaron fuera del reconocimiento y de la reparación estatal?» |

#### Guiones (Opus 5.5 v5.2, effort high)

| guion | escaleta | palabras | min | bloqueantes | citas | personas con nombre | cierre | US$ guion |
|---|---|---|---|---|---|---|---|---|
| A1 | ycua_f22c_A1 | 1590 | 12.9 | 0 | 11 | 24 | cita | 0.9234 |
| A2 | ycua_f22c_A2 | 1604 | 13.0 | 0 | 13 | 24 | pregunta | 0.5033 |
| B1 | ycua_f22c_B1 | 1332 | 10.8 | 0 | 8 | 13 | pregunta | 0.3914 |
| B2 | — | no salió | | | | | | |
| opus52a F22b (ref.) | ycua_f22 | 1144 | 9.3 | 0 | 9 | 13 | pregunta | 0.3261 |
| opus52b F22b (ref.) | ycua_f22 | 1159 | 9.4 | 0 | 8 | 13 | pregunta | 0.3086 |
| K | — | no salió | | | | | | |

#### Guiones por cap (palabras · personas · citas · bloqueantes)

| cap | A1 | A2 | B1 | B2 | opus52a F22b (ref.) | opus52b F22b (ref.) | K |
|---|---|---|---|---|---|---|---|
| 1 | 160 · 1p · 1c · 0b | 150 · 1p · 1c · 0b | 148 · 1p · 1c · 0b | — | 130 · 1p · 1c · 0b | 136 · 1p · 1c · 0b | — |
| 2 | 227 · 5p · 1c · 0b | 189 · 4p · 0c · 0b | 152 · 2p · 0c · 0b | — | 126 · 3p · 0c · 0b | 131 · 3p · 0c · 0b | — |
| 3 | 279 · 9p · 3c · 0b | 318 · 7p · 4c · 0b | 171 · 1p · 1c · 0b | — | 145 · 1p · 1c · 0b | 145 · 1p · 1c · 0b | — |
| 4 | 173 · 4p · 1c · 0b | 155 · 3p · 1c · 0b | 168 · 2p · 1c · 0b | — | 146 · 2p · 1c · 0b | 136 · 2p · 1c · 0b | — |
| 5 | 95 · 0p · 2c · 0b | 105 · 0p · 1c · 0b | 187 · 2p · 3c · 0b | — | 106 · 2p · 1c · 0b | 171 · 1p · 2c · 0b | — |
| 6 | 433 · 11p · 1c · 0b | 440 · 9p · 3c · 0b | 196 · 3p · 0c · 0b | — | 215 · 5p · 1c · 0b | 164 · 3p · 0c · 0b | — |
| 7 | 223 · 5p · 2c · 0b | 247 · 5p · 3c · 0b | 310 · 7p · 2c · 0b | — | 276 · 9p · 4c · 0b | 276 · 9p · 3c · 0b | — |

#### Personas con nombre por cap

| guion | personas con nombre por cap |
|---|---|
| A1 | 1: Liz Torres · 2: Alfredo Vallovera, Blas Cristaldo, Liz Torres, Teresa Urbieta, Ángela Pujol · 3: Alejandro Nissen, Beatriz González, Benedicto Pérez, Carlos Halke, Cristian Sosa, Enrique Riera, Liz Torres, Martín Burt, Víctor Galeano · 4: Digna Felicia Cáceres, Liz Torres, Tatiana Gabaglio, Víctor Galeano · 5: — · 6: Blas Cristaldo, Cristian Sosa, Digna Felicia Cáceres, Edgar Sánchez, Ismael Alcaraz, Juan Pío Helvidio Paiva Escobar, Luis Escobar Faella, Nelson Astigarraga, Rubén Urbieta, Teresa Sosa, Víctor Galeano · 7: Daniel Areco, Juan Pío Helvidio Paiva Escobar, Liz Torres, María Estela Morínigo Giménez de Palacios, Tatiana Gabaglio |
| A2 | 1: Liz Torres · 2: Alfredo Vallovera, Blas Cristaldo, Tatiana Gabaglio, Teresa Urbieta · 3: Alejandro Nissen, Beatriz González, Carlos Halke, Cristian Sosa, Enrique Riera, Martín Burt, Víctor Galeano · 4: Digna Felicia Cáceres, Nelson Astigarraga, Víctor Galeano · 5: — · 6: Cristian Sosa, Edgar Sánchez, Ismael Alcaraz, Juan Pío Helvidio Paiva Escobar, Luis Escobar Faella, Nelson Astigarraga, Rubén Urbieta, Teresa Sosa, Víctor Galeano · 7: Antonio Morínigo, Daniel Areco, Juan Pío Helvidio Paiva Escobar, María Estela Morínigo Giménez de Palacios, Víctor Daniel Paiva |
| B1 | 1: Liz Torres · 2: Alfredo Vallovera, Benedicto Pérez · 3: Beatriz González · 4: Digna Felicia Cáceres, Víctor Galeano · 5: Liz Torres, Tatiana Gabaglio · 6: Blas Cristaldo, Digna Felicia Cáceres, Nelson Astigarraga · 7: Antonio Morínigo, Digna Felicia Cáceres, Juan Pío Helvidio Paiva Escobar, Liz Torres, Luis Escobar Faella, María Estela Morínigo Giménez de Palacios, Tatiana Gabaglio |
| opus52a F22b (ref.) | 1: Liz Torres · 2: Alfredo Vallovera, Benedicto Pérez, Liz Torres · 3: Beatriz González · 4: Digna Felicia Cáceres, Víctor Galeano · 5: Liz Torres, Tatiana Gabaglio · 6: Alfredo Vallovera, Digna Felicia Cáceres, Liz Torres, Nelson Astigarraga, Tatiana Gabaglio · 7: Antonio Morínigo, Daniel Areco, Digna Felicia Cáceres, Juan Pío Helvidio Paiva Escobar, Liz Torres, Luis Escobar Faella, Tatiana Gabaglio, Víctor Daniel Paiva, Víctor Galeano |
| opus52b F22b (ref.) | 1: Liz Torres · 2: Alfredo Vallovera, Benedicto Pérez, Liz Torres · 3: Beatriz González · 4: Digna Felicia Cáceres, Víctor Galeano · 5: Tatiana Gabaglio · 6: Digna Felicia Cáceres, Nelson Astigarraga, Tatiana Gabaglio · 7: Antonio Morínigo, Daniel Areco, Digna Felicia Cáceres, Juan Pío Helvidio Paiva Escobar, Liz Torres, Luis Escobar Faella, Tatiana Gabaglio, Víctor Daniel Paiva, Víctor Galeano |

Tanda F22c: US$ 2.8094 de 3.00.

(«US$ guion» de A1 incluye el intento cortado: 0.448 + 0.475.) Narraciones: `NARRACION_ycua_f22c_{A1,A2,B1}.md` (palabras, bloqueantes, citas y personas con nombre por cap, y el texto). **No existen `NARRACION_ycua_f22c_B2.md` ni `NARRACION_kyshtym_f22c_K.md`** (no corrieron). Cero Cardal en las tres narraciones y las tres escaletas.

## 4. Costo
| paso | US$ |
|---|---|
| A1 escaleta · guion cortado · guion | 0.2787 · 0.4483 · 0.4751 |
| B1 escaleta · guion | 0.2738 · 0.3914 |
| A2 escaleta · guion | 0.3052 · 0.5033 |
| B2 escaleta (intento 1; el 2 lo cortó el freno) | 0.1336 |
| **total** | **2.8094** de 3.00 |

## 5. Desvíos y lo que falta
- **Tope de salida de Opus mal dimensionado (mío):** 20,000 en vez de los 24,000 de F22b; costó US$ 0.448 y es la razón de que no alcanzara para B2 y K.
- **Falta:** B2 (reintento de su escaleta + guion, ≈ US$ 0.55) y K (guion de Kyshtym, ≈ US$ 0.35). Con ≈ US$ 0.95 más se completan.
- Ningún cambio de código fuera de `lab/`. En `lab/hyperframes/f22b/f22b_corridas.py`, `narracion()` acepta ahora modelo, versión, tema y texto de la escaleta como parámetros opcionales (por defecto, lo de F22b) para reusarla.

## 6. Archivos
`lab/hyperframes/f22c/`: `F22c_REPORT.md`, `f22c_corridas.py`, `f22c_tabla.py`, `tabla_f22c.md`, `resumen_f22c.json`, `costos_f22c.json`, `escaleta_ycua_f22c_{A1,A2,B1}.json` + `ESCALETA_*.md`, `escaleta_crudos_ycua_f22c_{A1,A2,B1,B2}.json`, `escaleta_ycua_f22c_B2_rechazada.json`, `guion_ycua_f22c_{A1,A2,B1}.json`, `guion_ycua_f22c_A1_intento1_cortado.json`, `NARRACION_ycua_f22c_{A1,A2,B1}.md`, `prompt_*.txt` (con md5), `run_*.log`.

## 7. Veredicto del revisor-handoff (íntegro)

VEREDICTO: NO CUMPLE (entrega parcial, declarada con honestidad). Faltan B2 y K, que el pedido exigía. La causa es un error de dimensionamiento del propio ejecutor. La respuesta del reporte es "Sí" y la sostiene una sola escaleta B nueva.

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | A1, A2: escaleta v2.1 sin columna, Sol, guion Opus 5.5 v5.2 | OK | escaleta_ycua_f22c_A1/A2.json y guion_*.json existen. Corrí un conteo propio sobre las escaletas: A1 y A2 dan 54 y 55 ids, 2.36 y 2.43 apoyos por beat, 400 y 497 palabras de imagen sensorial, igual que el reporte. |
| 2 | B1: con la columna de F22, sin regenerarla | OK | Mi conteo da 32 ids, 1.00 apoyos y 441 palabras, igual que el reporte. run_resto.log dice "columna sí". |
| 3 | B2: escaleta + guion | FALLA | Solo hay el crudo del intento 1 (12 bloqueantes) y escaleta_ycua_f22c_B2_rechazada.json. No hay guion ni NARRACION_B2. run_resto.log: "PARADA (B2): tope… 2.809 + peor caso 0.242 > 3.00". |
| 4 | K: guion Opus 5.5 v5.2 sobre escaleta_kyshtym_f22 | FALLA | No hay guion ni NARRACION_kyshtym_f22c_K.md. Las celdas de K en la tabla van vacías. El reporte lo declara. |
| 5 | Tope US$ 3.00 | OK | Sumé los costos: 0.2787+0.4483+0.4751+0.2738+0.3914+0.3052+0.5033+0.1336 = 2.8094. Coincide con costos_f22c.json y con el log. |
| 6 | Por escaleta: beats, ids, apoyos, palabras de imagen, promesa_gancho y cierre_humano textuales | PARCIAL | Está para A1, A2, B1, la referencia F22 y K. Para K usa la escaleta existente, lo cual es válido. B2 no tiene fila. |
| 7 | Por guion: palabras, bloqueantes, citas, personas por cap | PARCIAL | Está para A1, A2, B1 y los dos Opus de F22b. Faltan B2 y K. |
| 8 | Narraciones con los nombres pedidos | PARCIAL | Existen NARRACION_ycua_f22c_A1, A2 y B1. Faltan B2 y K. Cero Cardal verificado con cero_cardal.py en las 3 narraciones y las 3 escaletas. |
| 9 | Tabla comparativa en F22c_REPORT.md con Opus a/b de F22b | OK | §3 incluye opus52a y opus52b. f22c_tabla.py regenera tabla_f22c.md; la única diferencia con el archivo guardado es una línea en blanco. |
| 10 | Cero cambios de código salvo elegir el modelo | PARCIAL | git diff toca ESTADO_SESION.md y lab/hyperframes/f22b/f22b_corridas.py, que es código de lab. Añadió parámetros opcionales a narracion(); es funcionalmente inocuo y el reporte §5 lo declara. Los demás archivos tocados (diag_234_cap4.py, gfx_profiles/*) no son de esta tanda, según el pedido. |
| 11 | Commit | NO VERIFICABLE | Todo f22c/ está sin trackear y no hay commit F22c. Sigue el commit anterior cd5fde5. Esto queda pendiente hasta el veredicto. |
| 12 | Revisor + PARADA | OK | §7 queda en REVISOR_PENDIENTE para pegar este veredicto. El reporte declara PARADA por tope. |

Fuera de alcance: ninguno nuevo. El único archivo tocado fuera de lab/hyperframes/f22c y ESTADO_SESION.md es lab/hyperframes/f22b/f22b_corridas.py, declarado en el reporte.

Observaciones:
1. Causa de la parada: en el guion de A1 Opus tuvo un tope de salida de 20,000 tokens (F22b había usado 24,000) y se cortó. Eso perdió US$ 0.448. El reporte lo admite (§2 y §5). El código lo confirma en f22c_corridas.py:36.
2. El orden de las corridas agravó el recorte. Se gastó B2-escaleta intento 1 (US$ 0.134) antes de K, que cuesta unos US$ 0.35 y era un requisito explícito. Con US$ 0.19 restantes K tampoco entraba. El reporte estima unos US$ 0.95 para completar B2 y K.
3. La respuesta "Sí, con columna la escaleta sale más flaca" está sostenida solo en datos y largo. Para esa lectura los números coinciden: ids 54–55 contra 31–32, apoyos 2.4 contra 1.0, guion de 1,590–1,604 palabras contra 1,332 o 1,144–1,159, y 24 contra 13 personas. Pero tiene límites:
   - El lado "con columna" es una sola escaleta nueva (B1) más la de F22, que es una corrida ya existente. Eso es n=1 más una referencia. El reporte lo reconoce.
   - A1/A2 son 2 corridas contra 1 B nueva, con diferencias entre corridas del mismo brazo no despreciables (A1 y A2 difieren 97 palabras de imagen sensorial).
   - "Flaca" mide datos y largo, no calidad. Los 5 guiones tienen 0 bloqueantes, y el propio reporte dice que mejor o peor para el espectador es lectura del analista.
4. Costo del guion de A1: la tabla muestra US$ 0.9234, que suma el intento cortado. El reporte lo aclara.
5. ESTADO_SESION.md está actualizado y dice "PARADA por tope" y "faltan B2 y K", coherente con el reporte.

Riesgos que el contrato no cubre: (a) el pedido no preveía qué hacer si el tope se agotaba antes de completar B2 y K, ni el orden de prioridad. (b) Sin K no hay control de que el modelo Opus 5.5 v5.2 se comporta igual en otro caso. (c) Los primeros intentos de las cuatro escaletas fallaron por el mismo defecto de F22 (ids en dato_central y en a_pantalla), y las 3 escaletas aceptadas necesitaron regeneración.
