# F5f — Cierre de Orleans (laboratorio) · PARADA

Rama `f5-guion-v2` · `wip: F5f pre-cierre` = `cc625e2`. `main` intacta, sin merge. El video **no se publica**: no hubo render completo, no se regeneraron fotos y no se abrió QA Studio (ya estaba abierto desde F5e).

## Qué se hizo
- **Arreglos 1–6 de F5f** (decisiones U1–U8 en `DECISIONES_F5.md`):
  - sustantivo con ícono sobre adjetivo;
  - palabras del tema a peso 1;
  - reservados con prioridad y motivo de choque;
  - bloque cita;
  - eco de cifras y 15 s entre recortes;
  - nivel de agua desde un reservado;
  - titulares sin comilla abierta.
- **D15 (4.6 m) como reservado del ch02** (U9): se sumó a `pantalla_ids` del skeleton (respaldo en `produccion/01a_skeleton_pre_f5f.json`; la narración no cambia). El nivel de agua sube a 4.6 metros a los 46.5 s del ch02.
- **Reloj que cambia de fecha** (U10): cuando la voz nombra la fecha siguiente, la fecha vieja sube y sale y la nueva entra con un destello en el acento. **En los 4 caps renderizados no dispara:** el único con reloj es ch02, y su voz dice una sola fecha. En la simulación dispara en ch04 (30 AGO → 2 SEP a los 57.5 s), que no se renderizó.
- **Render de la capa gfx** solo de ch02, ch05, ch06 y ch07 (`render_f5f_caps.py`: `fase2b --gfx --gfx-sparse --gfx-quality looks --reuse-visuals --only-cap`). Los 4 dieron rc=0 en 24 min, con Firefox cerrado y RAM libre de 18 GB o más. Costo: menos de US$ 0.01 de Gemini.
  - Capas nuevas: `output/ba6c3cac-f5v2/_fase2b_work/chNN_gfx.mp4` y `chNN_segment_only.mp4`.
  - Capas anteriores: `_fase2b_work/_bak_f5f_pre/`.
  - Hojas de contactos: `lab/hyperframes/f5/produccion/hojas_f5f/`.
- Tests: 410 verdes (`test_module_f5f.py`, 7) + 3 fallas viejas de `01b_pauses`.

## Bloques por cap (plan resuelto del render)
### ch02

| t | bloque | texto | fuente / kicker | por qué suma |
|---|---|---|---|---|
| 0.0 s | título | CAPÍTULO 2 · El Diluvio y la Traición | skeleton | abre el capítulo |
| 0.1 s | reloj | 28 AGO · 2005 | T05 | ubica la fecha que narra la voz (cronología del pool) |
| 8.3 s | recorte | los prisioneros no serán evacuados de la Prisión de Orleans Parish | 2005 · T05 | crítico SUMA: El bloque aporta un dato crucial sobre la decisión de no evacuar prisioneros en 2005, información que ni la imagen ni la voz dan en este instante, y no tapa ele |
| 15.4 s | sello | abandono | mood frio_abandono, peso 2 | crítico SUMA: El sello enfatiza una palabra clave de la voz, lo cual no se considera repetición, y el tinte refuerza el ambiente de la imagen. |
| 46.5 s | nivel de agua | 4.6 metros | D15 | crítico SUMA: El gráfico de '1m' aporta una escala de profundidad del agua que no se menciona en la voz ni es evidente en la imagen, ayudando a dimensionar la escena sin esto |
| 57.3 s | zoom | atrapados | visión sobre la foto | crítico SUMA: El zoom en las manos aferradas a los barrotes enfatiza visualmente la palabra clave 'atrapados' de la voz, añadiendo un detalle crucial sobre la desesperación d |
| 59.1 s | sello (pico) | negrura | mood oscuridad_encierro, peso 3 | crítico SUMA: El sello enfatiza una palabra clave de la voz sin repetir una frase completa, y el tinte refuerza la atmósfera de oscuridad y encierro sin tapar elementos impor |
| 69.1 s | pregunta | ¿Cómo se quedaron sin energía? | generada (gfx_question) | cierre del cap: engancha con el siguiente |

### ch05

| t | bloque | texto | fuente / kicker | por qué suma |
|---|---|---|---|---|
| 0.0 s | título | CAPÍTULO 5 · Los Desaparecidos y los Cuerpos | skeleton | abre el capítulo |
| 14.0 s | contador | 517 reclusos | D19 | crítico SUMA: El bloque enfatiza un dato numérico clave mencionado por la voz, facilitando su retención visual sin repetir una frase completa ni obstruir la imagen. |
| 31.2 s | sello (pico) | cadáveres + calavera | mood muerte, peso 3 | crítico SUMA: El sello enfatiza una palabra clave de la voz, añadiendo impacto visual sin repetir una frase completa ni lo que se ve en la imagen, y el tinte refuerza el ambi |
| 42.1 s | cita | Están en la cárcel, hombre. Mienten... No confíen en drogadictos, cobardes y criminales para saber cuál es la historia | — Sheriff Gusman · Q02 | crítico SUMA: El bloque aporta la cita completa y su atribución a Sheriff Gusman, información que la voz no da en su totalidad. |
| 100.3 s | pregunta | ¿Cómo lograron esto los turistas? | generada (gfx_question) | cierre del cap: engancha con el siguiente |

### ch06

| t | bloque | texto | fuente / kicker | por qué suma |
|---|---|---|---|---|
| 0.0 s | título | CAPÍTULO 6 · Demandas y Reparaciones Tardías | skeleton | abre el capítulo |
| 5.5 s | recorte (reservado) | El sheriff Gusman reabre el edificio House of Detention (HOD) | 2005 · T19 | crítico SUMA: El bloque aporta una fecha (2005) y un evento (reapertura del HOD por el sheriff Gusman) distintos a los que menciona la voz (fallo judicial de 2010), añadiendo |
| 9.5 s | contador | 650,000 dólares | fact 6 | crítico SUMA: El bloque aporta la cifra exacta de la compensación, que la voz solo menciona de forma aproximada, sin tapar elementos importantes de la imagen. |
| 18.8 s | sello (pico) | intoxicación | mood veneno_enfermedad, peso 3 | crítico SUMA: El sello enfatiza una palabra clave de la voz, lo cual está permitido como énfasis, y el tinte de mood refuerza la atmósfera sombría del relato sin tapar elemen |
| 51.7 s | sello | devastadora | mood caos_gritos, peso 3 | crítico SUMA: El sello enfatiza una palabra clave de la voz, y el tinte de mood refuerza el impacto emocional de la "carta devastadora" sin tapar información crucial. |
| 63.5 s | recorte (reservado) | El recluso Ronnie L. Morgan, Jr. presenta una demanda federal | 2006 · T23 | crítico SUMA: El bloque aporta un ejemplo específico de las luchas legales mencionadas en la voz, con un nombre y una fecha concreta, complementando la imagen de 'normalidad' |
| 91.7 s | pregunta | ¿Qué ocultaron las autoridades de Orleans? | generada (gfx_question) | cierre del cap: engancha con el siguiente |

### ch07

| t | bloque | texto | fuente / kicker | por qué suma |
|---|---|---|---|---|
| 0.0 s | título | CAPÍTULO 7 · Un Horror Sin Registros | skeleton | abre el capítulo |
| 3.0 s | recorte (reservado) | La ACLU publica el informe | American Civil Liberties Union (ACLU), 2006 · T22 | crítico SUMA: El bloque aporta una fuente y fecha clave (informe de la ACLU en 2006) que complementa la ausencia de registros oficiales mencionada por la voz, sin tapar eleme |
| 29.3 s | sello | vidas | mood muerte, peso 3 | crítico SUMA: El sello enfatiza una palabra clave de la voz, reforzando el impacto emocional de la escena sin tapar elementos importantes. |
| 68.2 s | sello (pico) | cuerpos + calavera | mood muerte, peso 3 | crítico SUMA: El sello enfatiza una palabra clave de la voz y la imagen, reforzando el tema central del documental sin obstruir la visual principal. |


## Lo que SIM_F5f prometía y no salió

**En los 4 caps renderizados:** todos los bloques del plan simulado salieron (comparado bloque por bloque con `tabla_f5f.py`).

**No salió en video:**
- **Cambio de fecha del reloj:** está programado y testeado, pero no dispara en ningún cap renderizado. Solo pasa en ch04 (30 AGO → 2 SEP a los 57.5 s), que no entraba en esta tanda.
- **ch01, simulación únicamente:**
  - eco de cifra y 15 s entre recortes: el 6,375 (D57) queda fuera;
  - T04 a los 14.7 s;
  - pico «abandonados» en lugar de «reclusos».
- **ch04, simulación únicamente:** T16 (reservado) a los 58.0 s.
- **ch03, sin simular de nuevo:** después de la regeneración desde QA Studio no tiene clip base, así que no tiene plan F5f.
- **SFX del recorte:** en ch06 (63.5 s, T23) y en ch07 (3.0 s, T22) se descartó, porque caía sobre una palabra sin un hueco de 120 ms o menos (`gfx_sfx`). El recorte sale, sin sonido de papel.

## Notas para el analista
- **Fuera del alcance de esta tanda:** ch01, ch03 y ch04 no se re-renderizaron. Sus capas y planes son los de F5e, y son los que lee el dedupe entre caps de ch05 a ch07. En la simulación, T04 (ch01) y T16 (ch04) salen, pero eso no está renderizado.
- **Fotos regeneradas desde QA Studio durante la sesión:** alguien usó el botón «arreglar» de QA Studio, no `regen_marcadas.py`.
  - ch01_supp_04 a las 11:20 y 11:21; ch03_img_02 y ch03_img_10 a las 14:10 y 14:12.
  - Los backups están en `assets/_qa_backups/`.
  - Eso borró los clips base `ch01_hybrid_visual.mp4` y `ch03_flux_visual.mp4`. Un render futuro de esos caps los rehace con DepthFlow.
- **Lo que se ve en las hojas:**
  - ch02: en el nivel de agua se lee «2 m» porque el cuadro cae durante la subida; termina en 4.6.
  - ch02: el titular del recorte está a medio animar.
  - ch05: el tinte del mood muerte sigue lavado (pendiente desde F5e, no tocado).
- **Crítico:** juzgó 17 bloques sobre el bloque dibujado y pasaron 16. Sacó el zoom «espalda prisionero» del ch07 (REPITE: la foto ya muestra a los prisioneros), igual que en F5e. Los reservados y la cita dieron SUMA por sí solos, así que no hizo falta la regla «el reservado queda aunque no sume».

## Veredicto del revisor
(íntegro; se le pasó el reporte antes de completar la lista «no salió», que después se corrigió: ver B5)

VEREDICTO: CUMPLE CON OBSERVACIONES

Tests: 410 verdes + 3 fallas viejas de 01b_pauses (las esperadas), corridos por mí. Bytes 0x08 en .py: ninguno.

| # | requisito | estado | evidencia |
|---|---|---|---|
| A1 | sustantivo con ícono gana a adjetivo | OK | gfx_ch05.log: de ('escalofriantes','cadáveres',...) sale "cadáveres + calavera" @31.2s; test_module_f5f verde |
| A2 | reclusos/prisioneros/presos/cárcel/prisión a peso 1 | OK (por código/tests) | Cambios en gfx_pool.py y gfx_config.py dentro de cc625e2; test verde. No lo contrasté sello por sello en los renders |
| A3 | reservados con motivo de choque, prioridad, bloque cita en ch05 | OK | gfx_ch06.log:111 "reservado T19 @5.5s desplaza ['dato «2010»']"; fragmentos[].motivo en SIM_F5f.md; ch05 "cita Q02 … Sheriff Gusman @42.1s (5.0 s) · desplaza nada" |
| A4 | cifra repetida ±10 s fuera; 15 s entre recortes | PARCIAL | Solo en la simulación (SIM_F5f.md: contador 6,375, "menos de 15 s"). ch01 no se re-renderizó, así que "6,375 en ch01" no está verificado en render |
| A5 | nivel de agua desde reservado de altura | OK | gfx_ch02.log:93 "nivel de agua (reservado D15): 4.6 metros @ 46.5s"; D15 en pantalla_ids del skeleton (línea 184) |
| A6 | titular sin comilla abierta | OK (por tests) | test_module_f5f verde. Ningún titular de los 4 caps termina en comilla |
| B1 | commit wip en f5-guion-v2 | OK con desvío | cc625e2 existe, 17 archivos, sin mp4 ni diag_234. Faltan los cambios posteriores: gfx_pool, gfx_project, gfx_sparse, gfx_literal_lock, test_module_f5f, DECISIONES, SIM_F5f y sim_f5f.out (diff +324/-59) siguen sin commitear; entrarán en el commit final |
| B2 | D15 + animación de fecha del reloj | PARCIAL | D15 aplicado (respaldo 01a_skeleton_pre_f5f.json). La animación está en el código (gfx_project.py, #tk-d y cue "time_ticker_change"), pero no se dibujó en ningún cap renderizado ni se verificó en video |
| B3 | no QA Studio, no fotos, no render completo | OK | Ningún archivo de assets/ch02, ch05, ch06 ni ch07 tiene fecha posterior a 07:00 (find vacío). Los backups de _qa_backups son solo ch01_supp_04, ch03_img_02 y ch03_img_10; esas fotos no se usan en los 4 caps. Solo se renderizó la capa gfx |
| B4 | fase2b ch02/05/06/07 + hojas | OK | ch0{2,5,6,7}_gfx.mp4 de 14:38 a 14:57 (250–329 MB); 4 hojas en hojas_f5f/ con nombres hoja_contactos_chNN.jpg; los 4 logs terminan en "OK total" |
| B5 | F5f_REPORT.md: tabla por cap + lista de lo no salido | PARCIAL | Existe (8.4 KB) y la tabla coincide con tabla_f5f.md. Pero la sección "Lo que SIM_F5f prometía y no salió" dice "- nada", y el mismo reporte (línea 15) admite que el cambio de fecha del reloj NO dispara en ningún cap renderizado. Es una contradicción: debe listarse. También falta decir que A4/ch01 solo está simulado |
| B6 | revisor, commit final, ESTADO_SESION | NO VERIFICABLE | Declarado como pendiente; falta ver ESTADO_SESION y el commit "F5f: cierre Orleans (lab)" |

Desvío de B1 (add -A): está bien justificado. Hay una contradicción en el propio pedido B: B1 pide add -A y B6 exige que misterio.json, lexico_propuestas.json y topics_db_pre.json queden sin commitear. Además lab/ESTADO_SESION.md:63 y :238 prohíben commitear diag_234_cap4.py y lexico_propuestas.json, y add -A habría metido ~135 sueltos ajenos. Dos precisiones: misterio.json no está en esa lista, pero Omar pide dejarlo suelto; y el commit sí incluyó lab/ESTADO_SESION.md.

Fuera de alcance: ninguno en cc625e2 (solo gfx, lab/f5 y tests). Sin commitear y a no commitear: diag_234_cap4.py, lexico_propuestas.json, topics_db_pre.json, y misterio.json por pedido de Omar.

Observaciones menores:
- El trailer del commit dice "Claude Opus 5.5", y la instrucción actual pide "Sonnet 5.5". ESTADO_SESION usa Opus como convención, así que solo conviene definir cuál va.
- En ch06 y ch07 se descartó el sfx de archive_clipping (63.47 s y 3.00 s) por caer sobre una palabra sin hueco ≤120 ms. No está en el reporte.
- El crítico del nivel de agua habla de "1m" aunque el bloque dice 4.6, y en la hoja se ve "2 m" porque el cuadro cae durante la subida. El reporte ya avisa de esto.

Riesgos que el contrato no cubre: (1) ch01, ch03 y ch04 quedan con capas de F5e; los ítems A4 y el reloj solo existen en simulación. (2) Los clips base de ch01 y ch03 se borraron por las regeneraciones desde QA Studio, y un render futuro los rehace con DepthFlow. (3) El código post-wip sin commitear es el que generó los renders: hay que incluirlo en el commit final, o el commit y los renders no coinciden.

**Qué se hizo con las observaciones (CC):**
- B5: la lista «Lo que SIM_F5f prometía y no salió» ahora detalla el reloj, A4 y T04 en ch01, T16 en ch04, ch03 sin plan y los SFX descartados.
- Riesgo 3: el código posterior al wip entra en el commit final.
- Trailer: el pedido no menciona Sonnet. El trailer vigente del proyecto es «Claude Opus 5.5»; se mantiene.
