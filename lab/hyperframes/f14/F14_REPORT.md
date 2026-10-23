# F14 — La ficha reemplaza al digest (una prueba, Orleans) — REPORTE → PARADA

CC · 2026-10-23 · rama `f11-guion-v4` (desde `2e13616`). Handoff: `HANDOFF_F14_ficha_en_el_camino.md`. Solo datos → escaleta → guion.

**En una línea:** con la ficha en el camino, Orleans pasa de **777 palabras (6.3 min) a 1,451 (11.8 min)**, con largo abierto y sin exigir palabras. La escaleta usa **53 ids** (antes 32) en **14 beats** (antes 8), y la narración usa **18 ids distintos** (antes 13). Quedan **2 bloqueantes**, y los dos son personas que la ficha rescató de los descartados del pool (ver §3). Costo: **US$ 0.811** de 1.50.

Para leer:
- `FICHA_orleans.md`: lo primero son las contradicciones; después vienen las decisiones con su criterio y las versiones.
- `ESCALETA_orleans_f14.md`.
- `NARRACION_orleans_f14.md`.
- `compara_f14.html`: F13 | F14 por cap, con el embudo arriba. Se lee en el teléfono.

## 0. Qué se hizo

1. **`researcher_steps/ficha_caso.py` (prompt `f14-1`):**
   - Agregué al sistema los **5 criterios** del handoff.
   - Secciones nuevas:
     - `decisiones` (criterios 1, 2, 3 y 5: `tema`, `criterio`, `decision`, `ids`, `otras_versiones` con doc@offset);
     - `versiones` (criterio 4: hechos disputados, sin resolver);
     - `personas_descartadas` (nombre, rol, motivo e ids);
     - `aproximada` en cada evento de la cronología.

     `contradicciones` queda para lo que ningún criterio resuelve.
   - El pool que ve el modelo trae ahora un bloque `<descartados_del_research>` con las personas que el research descartó y su motivo.
   - **Chequeo determinista:** el de F12, más tres controles de las secciones nuevas:
     - una decisión con criterio 4 se rechaza (va a versiones);
     - cada `doc@offset` de una versión tiene que ser evidencia de sus ids;
     - una persona descartada tiene que estar en `_descartados` del pool, y sus ids la tienen que nombrar.

     Son controles de la ficha, no reglas del guion.
   - `id_texts(ficha)` da el texto limpio de cada id: cita corregida, cifra con unidad y otras versiones, evento con fecha, hora y «aproximada», o hecho. `load(topic)` lee la ficha del disco.
2. **`script_engine/m01a_escaleta.py`:**
   - `pool_section(pool, ficha)` y `ficha_section()`: si hay ficha, el prompt de la escaleta lleva la ficha completa con sus ids (personas con las marcas del pool, personas descartadas, cronología, hechos, cifras, citas, versiones, decisiones y contradicciones) y **no** el digest.
   - `generate_escaleta(ficha="auto")` lee `_steps/<topic>/ficha_caso.json` si existe.
   - `datos_apoyo` pasa de 0–3 a **0–6 solo con ficha** (`MAX_APOYOS_FICHA`), en las reglas del prompt y en `validate(max_apoyos=)`. **Sin ficha, el prompt es byte-idéntico:** verificado con los md5 de `HEAD` (Orleans `379d8405…`, Ycuá `f17b1b25…`, con y sin feedback, y `RULES`) y con un test sobre el fixture.
   - Interpretación mía: «sin ficha, todo igual (byte-idéntico)» y «apoyos 0–6» solo son compatibles si los 0–6 valen únicamente con ficha.
   - No agregué ninguna validación nueva. Una escaleta con ficha puede usar ids que no están en la ficha; el reporte lo mide.
3. **`script_engine/guion_v4.py`:**
   - `data_line(..., fx)`, `escaleta_section(..., ficha)`, `prompt(..., ficha)` y `write(..., ficha)`: con ficha, el texto de cada id sale de la ficha; si no, del pool. Las marcas (VERIFICADA, PANTALLA…) salen siempre del pool. Sin ficha, todo queda igual: los md5 de F11c/F13 siguen verdes.
   - `fase1_5.run_guion_v4` pasa la ficha si existe.
   - **Ojo:** Ycuá ya tiene su ficha de F12 en `_steps`, así que desde ahora la escaleta y el guion v4 de Ycuá también la leerían. Acá no se corrió nada de Ycuá.
4. **Tests:**
   - `test_module_f14.py` (14, sin red): un caso por criterio (1, 2, 3, 4 a versiones y no a decisiones, 5 con aproximada); Nagin en `personas_descartadas`; `id_texts`; escaleta sin ficha byte-idéntica; con ficha, lee la ficha y no el digest; apoyos 0–6 solo con ficha; `generate_escaleta` lee la ficha del disco; `data_line` y el prompt v4, con y sin ficha.
   - **Suite amplia: 609 verdes + las 5 fallas previas** (3 `01b_pauses`, 2 `m03_merge_timing`). `test_v3_byte_identico`, verde.
5. **Prueba** (`f14_orleans.py`, en tres etapas reanudables, con un freno de costo común):
   - Ficha: Sol high, una llamada, tope de salida de 60k tokens.
   - Escaleta: Gemini Pro, como siempre; persist=False; sin notas (el topic no tiene).
   - Guion: Sol high, largo abierto, una llamada, sin reparación ni editor.
   - La escaleta de F7c-3 (`01a_escaleta.json`, md5 2f794418…) **no se pisó**: se copió a `01a_escaleta_f7c3.json`. La nueva quedó en `01a_escaleta_f14.json`.
   - No se tocaron `00_pool_v3.json` (md5 verificado) ni `topics_db`.

## 1. Embudo en números (F13 vs F14)

| versión | ítems del pool | → selección | → escaleta | → guion | beats | apoyos por beat |
|---|---|---|---|---|---|---|
| F13 · digest + escaleta F7c-3 | 1,033 | 336 (ids que nombra el digest) | 32 | 13 | 8 | 1.62 |
| **F14 · ficha + escaleta nueva** | 1,033 | **378** (ids que cita la ficha) | **53** | **18** | **14** | 2.07 |

- **Escaleta:** ids de los beats, más los de los caps y `a_pantalla`. Con la misma definición da 32 para F7c-3, el número del handoff.
- **Guion:** ids distintos que usa la narración (lo que suena ∩ lo del beat, `with_ids`).
- **Ids de la escaleta fuera de la selección:**
  - F13: 7 (D08, D25, D431, Q112, Q154, Q177, T64);
  - F14: 2 (D08, D261). Esos 2 no están en la ficha; la escaleta los tomó por otro lado (no hay validación que lo impida, como se dijo arriba).

**Resumen del guion:**

| versión | palabras | **min** | palabras por cap (1–7) | bloq. | duras v3 | citas | ids en el guion | humano (caps en escena) | cierre | US$ |
|---|---|---|---|---|---|---|---|---|---|---|
| F13 | 777 | **6.3** | 96 · 111 · 85 · 93 · 121 · 88 · 183 | 1 | 33 | 9 | 13 | Renard Reed (2, 5, 7) | cita | 0.045 (solo guion) |
| **F14** | **1,451** | **11.8** | 115 · 209 · 205 · 190 · 207 · 316 · 209 | 2 | 36 | 8 | 18 | **Pearl Cornelia Bland** (1, 2, 3, 7) | pregunta | 0.811 (ficha + escaleta + guion) |

- **Ids distintos por cap:** F13 1 · 3 · 0 · 1 · 3 · 0 · 5; F14 1 · 1 · 3 · 3 · 2 · 5 · 3. F13 tenía dos caps (3 y 6) sin ningún id.
- **Repetición interna (3-gramas):** F13 1.1 %; F14 0.0 %. Preguntas: 2 en las dos versiones.
- **Duras v3** (métrica del v3, no bloqueante del v4): F14 tiene 36, con 14 beats y un cap 6 de 316 palabras. Incluyen las de largo de cap del v3, que no aplican con largo abierto.
- **Cambio de humano:** la escaleta nueva no siguió a Renard Reed sino a **Pearl Cornelia Bland**. La ficha le da más material (Katherine Mattes, una persona descartada que la ficha rescató, «cierra el recorrido de Pearl Bland»).

## 2. Contradicciones de Orleans: qué resolvió cada criterio

La ficha final tiene **22 decisiones** (el modelo devolvió 24; el chequeo sacó 2), **10 versiones** y **5 contradicciones sin resolver**.

| criterio | cuántas | ejemplos |
|---|---|---|
| 1 · error de extracción (gana el pasaje) | 14 | horas que la extracción agregó y el pasaje no respalda (evacuación obligatoria, Templeman III, entrega de Brady Richard); el disparo junto al agujero atribuido a Ace Martin y no a un guardia; el traslado de Joyce Gilson confundido con el de otro interno |
| 2 · variantes de un nombre | 1 | el sheriff: **Marlin N. Gusman** (forma del documento oficial) |
| 3 · conteos | 4 | población de OPP durante la tormenta; capacidad previa (Departamento de Justicia); fallecidos («ninguna muerte» como cifra oficial declarada por Gusman, sin resolver las otras); caracterización penal de los internos de CCC |
| 5 · horas y fechas | 3 | llegada de Katrina (29 de agosto de 2005); corte de teléfonos (26 de agosto); pedido de ayuda al DOC cerca de medianoche (aproximada) |
| 4 · disputados → `versiones` | 10 | comida y agua; plan de evacuación; abandono de puestos; quién pidió refuerzos; presos de St. Bernard; **muertes dentro de OPP y personas no localizadas (6 versiones)**; disparos y uso de fuerza; condiciones en Hunt; cocina de Hunt; presencia de Gusman en el recorrido |
| sin criterio → `contradicciones` | 5 | el nombre del sheriff en un testimonio; Iris Hardy / Iris Hardeman; «Mr. Gussman / Gusmen»; el edificio en el testimonio del interno #63; el cargo de Bonita Pittman |

**Lo que sacó el chequeo (13 ítems, todos a `descartados` con «no respaldado»):**
- 2 decisiones: la hora del generador de Templeman III y la fecha de fin de la evacuación (cifras «175» y «84» que no están en los ids citados).
- 6 personas descartadas que no están entre los descartados del pool: internos identificados por número (#5, #33, #51, #53, #56, #220).
- 2 eventos de cronología (#175; una fecha 2005-08-27 que no está en sus ids).
- 1 cita cuyo texto no está en sus ids («Están en la cárcel, hombre. Mienten.»).
- 2 descartados del modelo sin ids.

## 3. Qué pasó con Nagin

- **Ficha:** ✅ Nagin está en `personas_descartadas` («C. Ray Nagin», ids T55 y D30), con el motivo «es necesario para explicar la evacuación obligatoria y la exclusión de los presos».
- **Escaleta nueva:** no lo usa. Ningún beat lleva D30 ni T55. La F7c-3 lo usaba por T55, y de ahí venía el bloqueante falso de F11 y F13.
- **Guion F14:** no lo nombra. **El bloqueante falso de Nagin desapareció**, pero porque la escaleta no lo eligió, no porque se haya resuelto.
- **El mismo problema, con otras dos personas:** los 2 bloqueantes de F14 son (d) «fuera del caso (descartado en el pool)» para **Burl Cain** (cap 6) y **Katherine Mattes** (cap 7). Las dos están en `personas_descartadas` de la ficha: la ficha las rescató con motivo y la escaleta las usó.
  - El bloqueante (d) (`m05.contamination`) sigue mirando los `_descartados` del **pool**, que no se toca, así que las marca igual.
  - No lo cambié: hacer que el (d) lea la ficha sería una regla nueva del guion. Para decidir (Omar y el analista): si la ficha manda, el (d) debería excluir las `personas_descartadas` de la ficha.

## 4. Costo y tokens

| etapa | modelo | llamadas | entrada | salida | razonamiento / thinking | US$ | segundos |
|---|---|---|---|---|---|---|---|
| ficha | gpt-6.1-sol high | 1 | 91,016 | 21,838 | 3,072 | 0.4311 | 391 |
| escaleta | gemini-2.5-pro | 3 intentos | 19,945 / 20,324 / 20,318 | 3,439 / 3,595 / 3,932 | 6,421 / 4,335 / 3,579 | 0.3287 | 212 |
| guion | gpt-6.1-sol high | 1 | 4,515 | 2,223 | 2,047 | 0.0517 | 132 |
| **tanda F14** | | | | | | **0.8115** (tope 1.50) | |

- **Escaleta:**
  - El prompt con la ficha tiene ≈ 20k tokens de entrada (el handoff de F7 hablaba de ≈ 20k con el digest).
  - Hicieron falta 3 intentos, por reglas que ya existían: Joyce Gilson en escena sin un dato suyo verificado, el humano en escena en menos de 3 caps, la última frase sin nombrar al humano o a un testigo, y preguntas de pantalla que no preguntan por culpa.
  - Reparaciones: el apoyo L16 (un lugar) salió del beat, y la cita Q54, sin verificar, no fue a pantalla.
- **Guion:** prompt de usuario 4,515 tokens (en F13, 2,973), porque hay 14 beats y más apoyos.
- **Ficha:** 91k tokens de entrada (los 1,033 ítems con sus evidencias, más los 130 descartados del research).

## 5. Frenos

- No se tocaron `00_pool_v3.json`, `research_v3.py`, `m05`, `evidence.py`, `guion_v3_reglas.py`, `config.py` ni `topics_db`.
- La escaleta de F7c-3 está intacta (y además copiada a `01a_escaleta_f7c3.json`).
- Cero reglas nuevas para el guion: los 5 criterios son de la ficha, y el único número que cambió en la escaleta es apoyos 0–6, solo con ficha.
- Sin merge. `.env` y `lab/_gpt_probe_analista/` no se commitean.
- Sin imágenes, voz ni producción.

## 6. Veredicto del revisor-handoff (íntegro)

Notas de CC, después del veredicto:
- **#16:** `ESTADO_SESION` ahora dice el veredicto.
- **Obs. 2:** probé la ficha F12 de Ycuá (`f12-1`, sin los campos de F14) con el código nuevo. `id_texts` da 157 textos y `ficha_section` arma la sección (50,723 caracteres) sin error, porque las secciones que faltan se leen con `.get`. No corrí la escaleta ni el guion de Ycuá.
- **Obs. 6:** el 378 cuenta los ids distintos que cita la ficha en todas sus secciones menos `descartados`, incluidas las `versiones` y las `otras_versiones`, ∩ los ids del pool (`f14_compara.ficha_ids`). Con otra definición da otro número.
- **«Fuera de alcance»:** `data/` está en `.gitignore`. Las salidas en `_steps` no se commitean; sus copias en `lab/hyperframes/f14/` sí.

VEREDICTO: CUMPLE CON OBSERVACIONES

Corrí yo: pytest de f14, f13, f12, f11, f11b y f11c, con 63 pasados. Corrí también `f14_compara.py` con `-I`; regenera el html y sus números coinciden con el reporte. No corrí `f14_orleans.py` ni nada con APIs.

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Ficha con 5 criterios, y cada decisión con `decision`, `criterio` y `otras_versiones` | OK | `ficha_caso.json` tiene `decisiones` (22), `versiones` (10) y `contradicciones` (5). Conteo por criterio de `decisiones`: 1→14, 2→1, 3→4, 5→3, igual que la tabla del reporte §2. El criterio 4 va a `versiones` y el chequeo rechaza una decisión con criterio 4. |
| 2 | Chequeo determinista y `personas_descartadas` | OK | 8 personas, entre ellas C. Ray Nagin (T55, D30), Burl Cain y Katherine Mattes. `corrida.out` lista 13 ítems sacados, igual que el reporte. |
| 3 | La escaleta lee la ficha y no el digest | OK | `m01a_escaleta.py`: `ficha_section` y `pool_section(pool, ficha)`. `01a_escaleta_f14.json` lleva `ficha: f14-1` y `pool_md5` e90d6ca9. |
| 4 | Sin ficha, la escaleta es byte-idéntica | OK | Cargué `m01a_escaleta.py` de HEAD y la nueva: `build_prompt` sin ficha es idéntico, con y sin feedback. |
| 5 | `datos_apoyo` 0–6 | OK, ver observación 1 | `MAX_APOYOS_FICHA=6` va en las reglas y en `validate(max_apoyos=)`. |
| 6 | `data_line` con ficha | OK | `guion_v4.py` usa `fx`; las marcas siguen saliendo del pool. `run_guion_v4` pasa la ficha si existe. |
| 7 | Cero reglas nuevas para el guion | OK | `guion_v4.system()` y `guion_v3_reglas.py` sin diff. Los controles nuevos son del chequeo de la ficha. |
| 8 | Archivos que no se tocan | OK | `git diff HEAD` sin cambios en config, evidence, m05, research_v3, guion_v3_reglas ni topics_db. md5 de `00_pool_v3.json` = e90d6ca9… |
| 9 | Escaleta F7c-3 no pisada | OK | md5 de `01a_escaleta.json` = 2f794418… La copia `01a_escaleta_f7c3.json` pesa lo mismo (12949 bytes). |
| 10 | Tests sin red | OK | `test_module_f14.py` existe y pasa. Tomo la suite amplia (609 verdes + 5 previas) del reporte; no la corrí. |
| 11 | Tope de costo US$ 1.50 | OK | `costos_f14.json` suma 0.4311 + 0.3287 + 0.0517 = 0.8115. |
| 12 | Entregables | OK | Todos existen y no están vacíos, incluidos los tres prompts, `ficha_crudo_orleans.json` y `resumen_f14.json`. |
| 13 | Números del reporte | OK | Embudo (336→32→13 y 378→53→18), 777 y 1,451 palabras, 6.3 y 11.8 min, 8 y 14 beats, 1.62 y 2.07 apoyos por beat, fuera de selección (D08, D261), 2 bloqueantes, tokens. Todo coincide con `resumen_f14.json`, `corrida.out` y `costos_f14.json`. |
| 14 | Nagin, Burl Cain y Katherine Mattes | OK | Nagin está en `personas_descartadas`. La escaleta no usa D30 ni T55. Burl Cain y Katherine Mattes están en la narración y son los 2 bloqueantes (d), tal como dice el reporte §3. |
| 15 | Sin merge ni commit, y archivos prohibidos | OK | F14 sigue sin commitear. `.env` no aparece en git status. `lab/_gpt_probe_analista/` está sin trackear y no se agrega. |
| 16 | `ESTADO_SESION.md` actualizado | PARCIAL | Está actualizado con F14, pero dice "revisor íntegro" y el veredicto de §6 estaba pendiente. Hay que completarlo al pegar este veredicto. |

Fuera de alcance: ninguno. Los cambios son los declarados (`ficha_caso.py`, `m01a_escaleta.py`, `guion_v4.py`, `fase1_5.py`, `test_module_f14.py`, `ESTADO_SESION.md` y `lab/hyperframes/f14/`). `diag_234_cap4.py` y `gfx_profiles/*` no son de F14. Los archivos nuevos en `_steps/ba6c3cac-f7r3/` están bajo `data/`, una ruta que no pude comprobar si git ignora.

Observaciones:
1. **Apoyos 0–6 solo con ficha.** Es razonable. El handoff pide a la vez "sin ficha byte-idéntico" y "0–6", y solo se pueden cumplir juntos así. Lo verifiqué por diff de prompts. Consecuencia: el tope 0–3 sigue vigente para cualquier tema sin ficha.
2. **Efecto lateral sobre Ycuá.** Ycuá ya tiene ficha F12 en `_steps`. Desde ahora `generate_escaleta(ficha="auto")` y `run_guion_v4` la usarán sola, con ficha de prompt `f12`, que no tiene los campos de F14. El reporte lo avisa; no vi un test que cubra ese caso.
3. **Dos ids de la escaleta fuera de la ficha (D08, D261).** No hay validación que lo impida; el reporte lo declara y lo mide.
4. **Los 2 bloqueantes (d) vienen de que el chequeo m05 mira los descartados del pool y no la ficha.** Quedó sin resolver adrede (sería una regla nueva) y le toca decidirlo a Omar. El "Nagin resuelto" es sin mérito: la escaleta simplemente no lo eligió.
5. **Escaleta con 3 intentos.** Gastó US$ 0.33 de los 0.81 en reintentos por reglas ya existentes. Es lícito y está declarado.
6. **El conteo de 378 ids "seleccionados" depende de la definición.** Los ids que saqué yo de la ficha no coinciden con ese número. Esa discrepancia no pesa en el veredicto.

Riesgos que el contrato no cubre: prueba de un solo tema y una sola corrida, así que la ganancia 6.3→11.8 min no se puede separar del azar del modelo ni del cambio de humano (Reed→Bland). La ficha rescata personas sin que ninguna regla compruebe que la historia las necesita. El prompt de la ficha pasa los 1,033 ítems (≈91k tokens de entrada), costo que crece con el pool.
