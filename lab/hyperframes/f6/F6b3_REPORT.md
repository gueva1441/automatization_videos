# F6b-3 — Escaleta de Orleans con la validación del analista · PARADA (el analista valida f6b-3 antes de F6c)

Rama `f6-guion-v3`. `main` no se tocó. Los frenos de §5 siguen intactos: el diff de la rama no toca `m01a_skeleton`, `m01b_narrator`, `evidence.py`, m03, fase2a/2b ni `gfx_*`.

**Para validar:**
- `ESCALETA_orleans.md` (f6b-3) y `escaleta_orleans.json`;
- para comparar: `ESCALETA_orleans_f6b2.md` y `escaleta_orleans_f6b2.json`;
- `F6b3_verificacion.md`.

## Qué se hizo, punto por punto

1. **Gancho = flash-forward.**
   - El beat tiene un campo nuevo, `flash_forward`. Solo puede marcarse en el beat 1, y no puede ser más intenso que el pico.
   - La curva «no baja hasta el pico» se mide desde el beat 2, y el flash-forward no cuenta como regresión temporal.
   - En Orleans: beat 1 a intensidad 4 (agua negra subiendo por los barrotes, a oscuras; Q13, con Q06 y D08 de apoyo, sin nombres). El cap 2 baja a 2.
   - Curva **4-2-2-3-3-4-5-1-3-3-3**; el objetivo era ≈ 4-2-3-4-5-1-3-3.
2. **Cierre humano.**
   - Regla nueva: la última frase del video nombra al humano o a un testigo verificado.
   - Campo nuevo `a_pantalla`: ids que la escaleta manda a pantalla y no a la voz.
   - Cap 7: beat 10 con central **D61** (ningún preso murió ni escapó, y después 14 órdenes de arresto) y apoyo **D62** (no hay registros); beat 11 con **Q04 de Norman** como juicio retrospectivo y la última frase con Norman.
   - Los turistas (T26) entran como apoyo en el cap 6, en el beat de la negación del sheriff, no como dato central.
   - **Q10 (Balaban) va a pantalla** en el cap 6. Burnley no aparece: su cita está sin verificar (punto 6).
3. **Reservados por fecha del beat.**
   - Primero entran los `a_pantalla`. Después, cada reservado con fecha va al cap cuyos beats la cubren; si cae entre caps, al primero que empieza después; si es posterior a todo, después del último cap con fecha.
   - Un reservado que cuenta lo mismo que otro ya en pantalla sale.
   - En Orleans:
     - T04 ya no va al cap 5: en esta escaleta T04 está narrado (beat 3), así que no es reservado;
     - T09 pasa al cap 3 y T03 al cap 2;
     - T30 pasa al cap 4;
     - T22 sale porque repite a T21.
4. **517 una sola vez.**
   - `count_variants` (sobre `gfx_pool.count_groups`): la cifra aproximada de un conteo no entra en ningún beat; si va como apoyo, se saca, y si es dato central, la escaleta se rechaza.
   - `instrucciones_guionista` (deterministas):
     - «La cifra 517 reclusos se dice UNA sola vez; nunca «500» ni «más de 500»» (y lo mismo para 6,375 y 6,500);
     - Q12 («éramos más de 500 mujeres y niños») se parafrasea sin la cifra;
     - las citas sin verificar van sin nombre;
     - lo de `a_pantalla` no lo dice la voz.
5. **Pregunta del cap 1:** «¿Por qué nadie vino por ellos?» (pasa). En el cap 1 (cold open) y en el cap 7 (la pregunta que se queda) ya no se exige el chequeo de «nombra algo ya visto»; el resto de la rúbrica sí.
6. **Verificación de testimonios** (`researcher_steps/verify_quotes.py`).
   - Cómo se hizo: una búsqueda (Flash + Google Search) por cada cita testimonio, y un 2.º intento con Pro solo para las que tienen nombre. Queda **verificada** solo si el modelo da una URL cuyo dominio está entre las fuentes REALES de la búsqueda; las redirecciones de Google se resuelven a la URL final.
   - Resultado:
     - **Q03 de Edward Burton** → verificada (thelensnola.org, 2025);
     - **Q04 de Vincent Norman** → verificada (blog sobre el documental «Prisoners of Katrina»);
     - Q05, Q06 (Norman), Q07 (Ducre), Q08 (Burnley) y los 3 anónimos → **sin verificar**. Pro dijo «aclu.org» para Q06, Q07 y Q08, pero sin ninguna fuente en la búsqueda: no cuenta.
   - Regla: una cita sin verificar se usa **sin el nombre** de quien la dijo. `humano_en_escena` exige un dato VERIFICADO suyo.
   - El pool y la escaleta muestran las marcas VERIFICADA / SIN VERIFICAR. Costo: US$ 0.065 de tokens; la búsqueda de Google no la cuenta `cost_tracker`.
7. **Notas del editor por tema:** `topic["escaleta_notas"]` va al prompt como «indicaciones del editor (mandan sobre tu criterio, nunca sobre las reglas)». Las de Orleans están en `f6b_escaleta_orleans.py` (`NOTAS_F6B3`), ajustadas a la verificación.

## Desvíos respecto de la validación (por la verificación)
- **Flash-forward «con Norman (Q05)»:** Q05 está sin verificar, así que el beat 1 usa Q13, Q06 y D08 sin nombres. Norman entra con nombre en el beat 3 (D72: «chef arrestado por una multa impaga») y en el cierre (Q04).
- **Última frase «con Norman o Lenore Burnley»:** Burnley (Q08) no se pudo verificar, así que va Norman.
- **«Seguimos al humano todo el video»:** con la verificación, Norman solo puede estar en escena donde hay un dato suyo verificado (D72 y Q04), es decir en 2 caps. Lo acompaña Burton (Q03, verificada) como respiro en el cap 6.

## Corridas y costo
- **f6b-3 intento A** (`escaleta_orleans_f6b3_intento_a.json`): pasó al primer intento por US$ 0.09, pero la promesa decía «más de **seis mil** personas»: una cifra en letras, y el validador solo veía dígitos.
  - Agregué `has_figure`: números escritos en letras; «miles» sigue permitido.
  - Regeneré.
- **f6b-3 final:** 3 intentos, US$ 0.27. Los rechazos fueron:
  - el humano entraba en el cap 3;
  - preguntas de los caps 1 y 4;
  - Norman en escena con datos sin verificar;
  - «generadores» en la pregunta del cap 3.
- **Re-validaciones en frozen:** sin costo. Primero, una regex que el heredoc había roto (byte 0x08, corregido). Después, el reparto por fecha.
- **Total f6b-3:** ≈ US$ 0.42 (escaletas US$ 0.35 + verificación US$ 0.07). La verificación corrió dos veces: la 1.ª, solo con Flash, salió US$ 0.0376 y se re-juzgó gratis desde la caché; la 2.ª, con el reintento con Pro, salió US$ 0.0272. `01_facts_sources.json._f6b3` guarda solo la 2.ª; la 1.ª figura en la salida de cost_tracker de esa corrida.
- **Tests:** `test_module_f6b.py` pasa de 19 a 28. Suites: 441 verdes + las 3 fallas viejas de `01b_pauses`.

## Dudas para el analista
1. **El pico se movió.** Ahora es el beat 7 (los 517 sin contabilizar, en el paso elevado); los cadáveres (D60) quedan en el beat 6, con intensidad 4. En f6b-2 el pico eran los cadáveres. ¿Cuál es el pico de Orleans?
2. **El cap 7 no tiene pregunta de pantalla** (queda marcado; el respaldo es `gfx_question`). El handoff pide una pregunta humana que se quede.
3. **Pregunta del beat 3:** «¿Por qué un chef estaba en esa celda?» pasa la rúbrica, pero es más curiosidad que culpa.
4. **La última frase repite Q04 textual** («Como dijo Vincent Norman: "Básicamente abandonaron la prisión"») y `cierre_humano` dice lo mismo: queda flojo como final. El guionista lo puede trabajar en F6c.
5. **T03 se ve en pantalla en el cap 2** (el arresto de los turistas, del 27 de agosto), pero los turistas recién se nombran en el cap 6.
6. **La fuente de Q04 es un blog** sobre el documental, no el documental en sí: verificada según la regla, pero débil.
   «Verificada» significa que el dominio de la URL está entre las fuentes reales de la búsqueda; nadie leyó la página.
7. **Los turistas en pantalla (lo marcó el revisor):** T26 entra como apoyo, pero la pregunta de pantalla de ese beat,
   «¿Por qué la justicia llegó para dos turistas?», les da peso propio, justo lo que la validación pedía evitar. ¿Se
   cambia la pregunta o se acepta?
8. **«Los 517» en pantalla:** la voz lo dice una vez (instrucción al guionista), pero la cifra también sale en la pregunta
   de pantalla del cap 5 y en la pregunta abierta del beat 10. ¿Vale en pantalla o va solo en la voz?

## Veredicto del revisor
(íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

Los seis ítems están implementados y los desvíos declarados (Q05 y Burnley sin verificar) están bien justificados. Hay dos observaciones de fondo (pico y T26) y varias menores.

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Gancho flash-forward, intensidad 4, `flash_forward:true`, sin cifras, con promesa, cap 2 baja a 2, curva ≈ 4-2-3-4-5-1-3-3 | PARCIAL | Beat 1: intensidad 4, `flash_forward` True, sin cifras (promesa «Miles de hombres…»). Cap 2 baja a 2. La curva real es 4-2-2-3-3-4-5-1-3-3-3 (11 beats). El pico pasó al beat 7 (D19, 517) y los cadáveres (D60) quedaron en 4. El reporte lo declara y lo pregunta. |
| 1b | Norman en el gancho (Q05) | OK (desvío justificado) | Q05 es `sin_verificar`: la búsqueda no la encontró, ni con Pro (F6b3_verificacion.md, 00e_verificacion.json). El beat 1 usa Q13, Q06 y D08 sin nombres. |
| 2 | Cap 7: D61 central, ausencia de registros, última frase con Norman o Burnley, Q10 a pantalla, Q04 a cap 6–7 | OK | Beat 10: D61 central y D62 de apoyo. Beat 11: Q04 central. `a_pantalla` incluye Q10 (cap 6). La última frase «Como dijo Vincent Norman: 'Básicamente abandonaron la prisión'» coincide con Q04, que está verificada (00e: thelensnola.org y blogspot). Burnley (Q08) es `sin_verificar` y no entra: desvío justificado. |
| 2b | T26 como ironía en una frase, no dato central ni presentación nueva | PARCIAL | T26 está de apoyo en el beat 9 (cap 6), no en el cap 7. La pregunta de pantalla de ese beat es «¿Por qué la justicia llegó para dos turistas?», que presenta a los turistas con peso propio, justo lo que el analista pidió evitar. |
| 3 | Reservados a pantalla por fecha; T04 no va a cap 5 | OK | `a_pantalla`: T21 y Q10 (cap 6). `_pantalla_por_fecha`: T09→cap 3, T03→cap 2, T30→cap 4, T22 fuera por repetir T21. T04 está narrado en el beat 3 (cap 2). |
| 4 | Instrucción 517 una sola vez, nunca «más de 500» | PARCIAL | `instrucciones_guionista` lo dice y manda parafrasear Q12 sin la cifra. Pero la pregunta de pantalla del beat 7 dice «¿Dónde están los 517 desaparecidos?» y `queda_abierta` del beat 10 repite «los 517». La instrucción aplica a la voz, pero la cifra se reitera en el texto de pantalla y en el hilo narrativo. |
| 5 | Pregunta del cap 1 que pase la rúbrica | OK | «¿Por qué nadie vino por ellos?». El aviso de «no nombra nada ya visto» desapareció en f6b3_frozen.out porque se exceptuó el cap 1 en el validador, no porque la pregunta lo cumpla. |
| 6 | Verificación de testimonios con url_fuente o `sin_verificar`; las `sin_verificar` no se usan con nombre | OK | 9 citas: 2 verificadas (Q03, Q04) y 7 `sin_verificar`; el pool lo registra en `_f6b3`. Los beats con `humano_en_escena` (3 y 11) se apoyan en D72 y Q04, ambos verificables o verificados. Q06, Q11, Q12 y Q13 quedan anónimas en las instrucciones. |
| 7 | Ids contra el pool | OK | Los 35 ids de la escaleta existen en `01_facts_sources.json`. `escaleta_orleans.json` es idéntico a `01a_escaleta.json`. |
| 8 | Costos declarados | OK | cost_history: intento A 0.0881; final 0.0787+0.0940+0.0939 = 0.2666, igual que el `.out` y el reporte. La verificación en 00e es 0.0272, pero el reporte dice 0.065 y «≈0.42 en total». Esa diferencia no se pudo cotejar. |
| 9 | Frenos §5 y tests | OK | Ningún archivo prohibido (skeleton, narrator, evidence, m03, fase2, gfx_*, normalizer, TTS) aparece modificado en el diff. Tests: 441 verdes y 3 fallas viejas de `01b_pauses`, como se esperaba. Cero bytes 0x08 en el diff de .py. |

Observaciones menores:
- Q10 (Balaban) va a pantalla con nombre sin estar verificada. La regla solo prohíbe usarla con nombre en la narración.
- La fuente de Q04 es un blog de 2011 sobre el documental. La regla la da por verificada, pero es débil.
- La última frase repite Q04 literal y `cierre_humano` dice lo mismo, así que queda flojo como final.
- El cap 7 no tiene pregunta de pantalla (el reporte lo marca).

Fuera de alcance: ninguno propio de F6b-3. Siguen sin commitear los ajenos declarados: diag_234_cap4.py, gfx_profiles/lexico_propuestas.json y gfx_profiles/misterio.json.

Riesgos que el contrato no cubre:
- «Verificada» significa que el dominio de la URL está entre las fuentes de la búsqueda. No se leyó el contenido de la página, así que no equivale a cita confirmada.
- El pico quedó en los 517 y no en los cadáveres, que era el de f6b-2. Hay que resolverlo antes de F6c.
- El reporte dice que la verificación costó ≈US$ 0.065. 00e solo respalda 0.0272.

**Qué se hizo con las observaciones (CC):**
- Costo: aclarado en «Corridas y costo» (dos corridas de verificación).
- T26 en la pregunta, «los 517» en pantalla, Q10 con nombre en pantalla y verificación por dominio: quedan como dudas 6–8 del reporte, para el analista. No se regeneró.
