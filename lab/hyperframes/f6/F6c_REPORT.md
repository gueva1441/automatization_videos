# F6c — Verificación literal, escaleta f6b-4 y narración v3 (guionista + editor) · PARADA: el analista lee la narración

Rama `f6-guion-v3`. `main` no se tocó. Frenos de §5 intactos: el diff de la rama no toca `m01a_skeleton`, `m01b_narrator`, `m05_narrative`, `evidence.py`, m03, fase2a/2b ni `gfx_*`. Los módulos nuevos usan sus funciones sin cambiarlas.

**Para leer:**
- `NARRACION_orleans_v3.md`: la narración por beat, con `ids_usados`, los `cambios[]` del editor y los problemas que quedan;
- `ESCALETA_orleans.md` (f6b-4);
- `F6c_verificacion.md`.

## A — Verificación literal (`researcher_steps/verify_quotes.verify_literal`)
- **Regla nueva del analista:** se baja el documento fuente y se busca la cita LITERAL, no el dominio.
  - Vale un documento con fecha ≤ evento + 20 años que nombre el lugar o el evento.
  - Se busca el texto del pool o su original en inglés, tolerando los caracteres rotos de la copia.
  - Verificada = literal + el autor a ≤ 400 caracteres. Literal sin el autor = se usa sin nombre.
- **Documentos bajados** (`data/scripts/_steps/ba6c3cac-f6v3/fuentes/`):
  - BBC «Los presos de Katrina» (Olenka Frenkiel, 2006), en la copia de rebelion.org;
  - el PDF completo de la ACLU «Abandoned and Abused» (2006), pasado a texto con `pdftotext`;
  - The Lens (2025).
- **Resultado:**
  - **Q03 Burton** → verificada (The Lens, en inglés y literal).
  - **Q04 Norman** → verificada con el literal de la BBC, «**Simplemente abandonaron la cárcel**». Antes era «Básicamente abandonaron la prisión», la traducción de Gemini; el texto anterior quedó en `texto_anterior`.
  - **D95 (nuevo):** «Norman no debería haber estado allí más de una semana. En vez, pasó 103 días…» (literal BBC).
  - **Sin verificar:** Q06 y Q07, y Q11–Q13, que **no están en el PDF completo de la ACLU** ni en la BBC.
- **Fuera del pool, con motivo** en `_descartados`:
  - Q08, P12, D78 y D79 (Lenore Burnley / Chad Joseph): contaminación, según el analista (nota ACLU 2026, Trinidad).
  - **Q05** «campo de concentración»: atribución errónea. En la ACLU 2006 lo dice un preso anónimo sobre la cárcel de **Hunt**, no Norman ni la OPP.
- **Literales en la BBC que no se sumaron** (el pedido era solo los 103 días):
  - Andrew Joseph vio un cuerpo flotando con una rata en el pecho;
  - Cardell Williams: «Nos abandonaron a nuestra suerte»;
  - la escena de Ducre con la linterna.

  Están listados en `F6c_verificacion.md`.
- **Costo:** US$ 0 de API: se bajan páginas y se compara texto.

## B — Escaleta f6b-4
- **Reglas nuevas** (generales, en `m01a_escaleta`):
  - `contador` (la cifra de ese beat sale como contador en pantalla);
  - **una cifra en pantalla una sola vez por video**, entre preguntas y contadores;
  - la pregunta del cap 7 es obligatoria;
  - la última frase no repite textual ninguna cita;
  - `escaleta_solo_apoyo` (ids que el editor solo permite como apoyo);
  - una cita sin verificar nunca va a pantalla;
  - el rango de fechas de un cap sale de sus datos centrales;
  - el prompt lista por testigo «los datos que lo ponen en escena (repartilos en caps distintos)».
  - «Nombra algo ya visto» pasó a aviso: rechazaba preguntas buenas como «¿Por qué se negó a moverlos?».
- **Orleans f6b-4:**
  - **Pico:** los cadáveres (D60) en el cap 4, intensidad 5.
  - **517:** revelación del cap 5, intensidad 4, con **contador**; la pregunta va sin cifra («¿Dónde están los prisioneros desaparecidos?»).
  - **Cap 6:** pregunta «¿De quién fue la culpa de la inundación?»; los turistas, solo como apoyo.
  - **Cap 7:** D61 + D62 y Norman con D95; pregunta «¿Cuántos nombres siguen perdidos en el agua?».
  - **Norman en escena:** caps 2 (D72), 3 (Q04) y 7 (D95).
  - **Curva:** 4-2-3-5-4-1-3-3.
- **Costo:** US$ 1.04 (estimado: 0.25).
  - Intento A: los turistas como dato central.
  - Dos corridas rechazadas: preguntas marcadas por la heurística y Norman en 2 caps (mis notas pedían D95 y Q04 juntos en el cap 7).
  - La final.

  La f6b-3 quedó guardada para comparar.

## C — Guionista y editor (HANDOFF §2.3–2.4)
- **`script_engine/m01b_guionista.py`** (Pro, texto completo, best_of_2).
  - **Prompt:** la escaleta por beat (imagen, dato central y apoyo con «lo que tiene que sonar literal», cierre obligatorio con los términos del dato del cap siguiente, párrafos de 55–80 palabras), material extra opcional del pool por cap, las instrucciones al guionista y las reglas de prosa v2.
  - **`review`:** por cap, `_validate_narration` (frases prohibidas, primera oración) y `m05.cap_review` (no inventar, datos asignados y declarados, una vez, contaminación, relleno, comillas, canónica, reservados, fechas, cliffhanger). Más las v3: gancho sin año, cifra ni institución en la frase 1; ritmo (≥ 1 frase de ≤ 6 palabras por beat, ninguna de más de 30, dos cortas antes del pico); el humano en ≥ 3 caps; las citas sin verificar sin nombre; un conteo, una cifra; palabras por cap (mínimo 85 %).
- **`script_engine/m01c_editor.py`** (Pro): solo corta, acorta, reordena dentro del párrafo y refuerza el ritmo; devuelve los mismos párrafos más `cambios[]`.
  - Cada párrafo editado pasa la **guardia léxica**: no puede agregar cifras, nombres, adjetivos ni citas.
  - Después, los **validadores otra vez**: si el cap empeora, el párrafo vuelve al original.
- **Narración de Orleans** (3 corridas; el prompt se ajustó entre una y otra):

  | prompt | palabras | duras | qué cambió |
  |---|---|---|---|
  | f6c-1 | 612 | 20 | — |
  | f6c-2 | 715 | 12 | lo que suena literal por id, cierre con términos, palabras por cap |
  | **f6c-3** | **1072** | **4** | párrafos de 55–80 palabras y material extra por cap |

  - Editor en f6c-3: 19 párrafos editados, **10 aceptados y 9 rechazados** (7 dejaban el cap bajo el mínimo o le sacaban un dato asignado; 1 agregaba el adjetivo «oscuras»).
  - Costo de las 3 corridas: US$ 0.88. La final: guionista US$ 0.16 + editor US$ 0.20.
  - Las versiones anteriores quedaron en `NARRACION_orleans_v3_f6c1.md` y `_f6c2.md`.
- **Tests:** `test_module_f6c.py` (4) y `test_module_f6b.py` (31, con los de f6b-4). Suites: 448 verdes + las 3 viejas de `01b_pauses`.

## Lo que queda (para el analista)
1. **4 problemas duros en la narración final:**
   - **Cap 1:** cita fragmentos LITERALES de Q13 y Q11 (sin verificar, sin nombre), pero `m05.cap_review` exige la cita entera para darla por usada. ¿Se permite citar un fragmento literal (cambio de m05 en F6d) o se pide la cita entera?
   - **Cap 4:** «Templeman III» suena 2 veces.
   - **Beat 8:** no tiene una frase de ≤ 6 palabras.
2. **Lo que ningún validador ve** (lo leí yo):
   - **Pensamientos inventados (beat 2):** «escuchaba las noticias. No le dio mayor importancia. Como todos, confiaba en las autoridades». A un preso real se le atribuyen cosas que el research no dice. Propongo una regla dura para F6c/F6d: no atribuirle a una persona real pensamientos ni acciones que el pool no dice.
   - **Dato tergiversado (cap 6):** «al menos 14 personas que el sheriff declaró perdidas»; las 14 son **órdenes de arresto** (D61).
   - **Afirmación sin dato (cap 2):** «El sheriff aseguró que todos estarían a salvo», sin respaldo en el pool.
   - **Desvío del cap 6:** se va a los diques del Cuerpo de Ingenieros (dato central de la escaleta f6b-4) y se aleja de la cárcel.
3. **Costo de esta tanda:** ≈ US$ 1.9 (escaleta US$ 1.04 + narración US$ 0.88), contra los ≈ US$ 0.35 estimados para B + C, por los reintentos.
   Por corrida, según la salida de cost_tracker en la consola (los `.out` y los `_costo` guardan solo la última):
   - escaleta: 0.2694 (intento A) + 0.2848 (rechazada) + 0.2326 (rechazada) + 0.2567 (final) = 1.0435;
   - narración: f6c-1 0.1008 + 0.1184; f6c-2 0.1295 + 0.1713; f6c-3 0.1601 + 0.1959 = 0.876.
4. **Más invenciones (las encontró el revisor; se suman al punto 2):** sin respaldo en el pool:
   - **Cap 4:** «les llegaba a la cintura» (el pool dice al pecho), y «el olor» / «Nadie podría olvidar el olor».
   - **Cap 3:** «los vientos arrancaban los techos», «pozo ciego», «calor húmedo… aire espeso».
   - **Cap 6:** «Con la admisión, llegaron las demandas» (liga la demanda de los turistas al testimonio de Strock).
   - **Cap 7:** «Los archivos se perdieron» (D62 solo dice que no hay registros), y «pasó 103 días perdido en el sistema» (la BBC dice «en la cárcel»).
   - **Cap 5:** «Human Rights Watch comenzó a investigar»; además, D16 está declarado y no suena.
   - **Cap 1:** «otra rea».
   - **Cifra 14:** suena en los caps 6 y 7 sin declarar.
   - **La última frase** («simplemente lo habían abandonado») hace eco casi textual de Q04: el chequeo de 5 palabras seguidas no la atrapa.

   Los validadores solo ven cifras, nombres y citas. Para F6d (o un F6c-bis) propongo:
   - un **validador semántico** (Flash): cada oración con un hecho concreto tiene que tener respaldo en los datos del beat o del pool;
   - la regla dura **«nada de pensamientos ni acciones de una persona real que el pool no diga»**.

## Veredicto del revisor
(íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

Tests: corrí tu comando. Dio 448 verdes y 3 fallas, las 3 viejas de test_module_01b_pauses. Bytes 0x08 en .py: ninguno. No llamé APIs.

| # | requisito | estado | evidencia |
|---|---|---|---|
| A1 | Verificación literal contra el documento bajado | OK | Busqué yo en fuentes/. Q04 («Simplemente abandonaron la cárcel») y D95 están en rebelion_presos_katrina.txt, con Frenkiel y fecha 15/08/2006. Q03 («nobody there, we was left for dead, man») está en thelens_2025_opp.txt, con Burton al lado. Borderline: el documento es del 29/08/2025, justo evento+20 años. |
| A2 | D95 literal | OK | El pool dice «no debería haber estado allí más de una semana… pasó 103 días en la cárcel sin agua ni comida y en condiciones insalubres, mientras el agua subía». Es idéntico a la BBC (solo cambia la «ó» rota de «comida» en la copia). |
| A3 | Burnley/Chad Joseph y Q05 fuera con motivo | OK | Q08, P12, D78, D79 y Q05 están en `evidence_pool._descartados` con su motivo. Ninguna de las otras listas del pool los contiene, y tampoco la escaleta ni la narración. Q05 es real: en la ACLU aparece «It was like a concentration camp», dicho por un preso anónimo de Hunt. Los tres 00*_*.json intermedios todavía los conservan, pero no alimentan el pool vivo. |
| A4 | Q06, Q07, Q11–Q13 | OK | Los busqué en aclu_abandoned_and_abused.txt, que sale en dos columnas y rompe las frases, y también en aclu_raw.txt, que no las rompe. Ninguno aparece literal, así que quedan «sin_verificar», lo cual es honesto. Q06 tampoco está en la BBC. |
| B1 | Pico = cadáveres, cap 4, intensidad 5 | OK | escaleta_orleans.json: beat 4 con D60. La curva es 4-2-3-5-4-1-3-3. |
| B2 | 517 en cap 5, intensidad 4, contador, pregunta sin cifra | OK | Beat 5 lleva CONTADOR. La pregunta es «¿Dónde están los prisioneros desaparecidos?». |
| B3 | Cap 6 sin pregunta sobre turistas | OK | La pregunta es «¿De quién fue la culpa de la inundación?». Los turistas quedan solo como apoyo. |
| B4 | Cap 7 con Norman + 103 días + pregunta, sin repetir Q04 | PARCIAL | D95 y la pregunta de pantalla «¿Cuántos nombres siguen perdidos en el agua?» están en la escaleta. El cierre «para el sistema, simplemente lo habían abandonado» hace eco casi textual de Q04 («Simplemente abandonaron la cárcel»). El reporte dice «cierre sin eco». La pregunta vive solo en pantalla; la narración del cap 7 no tiene ninguna. |
| B5 | Una cifra en pantalla una sola vez | OK | La regla está en m01a_escaleta.py:44 y :626. Las preguntas de pantalla no llevan cifra y el único contador es 517. |
| C1 | Una llamada Pro por intento, texto completo, best_of_2 | OK | m01b_guionista.py:35 (BEST_OF=2) y :362-381. Se elige el intento 1 (el 2 tuvo 13 duras). |
| C2 | Editor con cambios[], guardia léxica, validadores post-editor, párrafo rechazado vuelve al original | OK | m01c_editor.py:129-174. 19 editados: 10 aceptados y 9 rechazados, y los rechazados conservan el original. Salvedad: el criterio compara cantidad de duras (`len(rv.hard) > len(cur.hard)`). Un párrafo que cambia una dura por otra pasaría. |
| C3 | NARRACION_orleans_v3.md con beat, ids_usados, cambios[] | OK | Cada párrafo trae beat e ids_usados; hay sección «Cambios del editor» con antes/después/estado/motivo. |
| C4 | Costos declarados vs logs | PARCIAL | Coinciden las corridas finales: escaleta $0.2567, guionista $0.1601, editor $0.1959 (f6b4_run.out, f6c_run.out, `_costo` de los JSON). Los totales US$1.04 y US$0.88 (≈1.9) no se pueden verificar; los logs guardan solo la última corrida. |
| C5 | Narración sin invenciones ni tergiversaciones más allá de lo declarado | FALLA (parcial) | Ver abajo. |
| C6 | Los 4 duros que quedan | Declarados | Cap 1 (Q13/Q11 citados en fragmento), «Templeman III» ×2 en cap 4, y beat 8 sin frase de ≤6 palabras. El reporte los declara; ya aparecen arriba en la narración. |

Hallazgos de C5 (narración contra el pool). El reporte ya declara los cuatro primeros: pensamientos de Norman, «sheriff aseguró que todos estarían a salvo», «14 personas perdidas» (son órdenes de arresto), y el desvío del cap 6 a los diques. Lo NO declarado:
- Cap 6: «Con la admisión, llegaron las demandas». El pool no liga la demanda de los turistas a Strock. Además, «error de cálculo fatal» y «investigación nacional» no están en el pool.
- Cap 7: «Los archivos se perdieron» (D62 solo dice que no hay registros) y «Cientos de historias como la suya nunca se contaron». «Pasó 103 días perdido en el sistema» contradice a la BBC, que dice «en la cárcel». «Vincent solo tenía que pagar una multa» es una inferencia.
- Cap 4: «líquido negro que les llegaba a la cintura» (el pool dice «pecho»), «el olor» y «Nadie podría olvidar el olor». El pool no tiene nada de eso.
- Cap 3: «vientos arrancaban los techos», «pozo ciego», «calor húmedo… aire espeso», «Silencio, roto solo por los gritos». El pool no los respalda.
- Cap 2: «No era cierto. Gusman estaba equivocado», juicio editorial. «Complejo de concreto y acero» no está en el pool.
- Cap 5: «Miles… sin documentos ni registros», «el número se hizo público» y «Human Rights Watch comenzó a investigar» no están en el pool tal cual. D16 está en `ids_usados` pero no suena en el texto.
- Cap 1: «Otra rea» es un término incorrecto. «Los guardias se habían ido» es plausible pero no es dato del pool.
- La cifra 14 suena en cap 6 y en cap 7, y las dos veces aparece sin declarar. Eso contradice la regla de una cifra una vez que valdría para la voz.
- El validador no detecta ninguna de estas invenciones; solo ve cifras y nombres.

Fuera de alcance: ninguno de F6c. Los frenos (m01a_skeleton, m01b_narrator, m05, evidence.py, m03, fase2a/2b, gfx_*.py, normalizer, TTS) no aparecen en `git diff 45c052c`. Los únicos archivos ajenos sin commitear son diag_234_cap4.py, gfx_profiles/lexico_propuestas.json y gfx_profiles/misterio.json, como avisaste. lab/ESTADO_SESION.md fue actualizado, como pide el CLAUDE.md.

Riesgos que el contrato no cubre:
- La regla «no atribuir pensamientos a personas reales» y «afirmaciones sin dato» no tiene validador duro. Lo único que las atrapa es la lectura humana del analista.
- Las citas sin verificar de Q11 y Q13 siguen en cap 1 y chocan con `m05.cap_review`. Hace falta una decisión del analista antes de F6d.
- Los costos acumulados (≈US$1.9 contra los 0.35 estimados) no tienen traza auditable por corrida.

**Qué se hizo con las observaciones (CC):**
- C5: las invenciones no declaradas se sumaron al punto 4 de «Lo que queda», con la propuesta del validador semántico. No se regeneró: el analista lee esta narración.
- C4: el costo por corrida, sacado de la consola, quedó en el punto 3.
- B4: el eco de Q04 quedó declarado en el punto 4 (el chequeo de 5 palabras seguidas no lo atrapa).
- ESTADO_SESION: actualizado en este cierre (al momento de la revisión todavía estaba el de F6b-3).
