# RESUMEN F5d — último ajuste antes de producción · PARADA para el analista

Rama `f5-guion-v2`, desde `c55ca56` (F5c). Sin imágenes ni render. `main` intacta. Decisiones: `DECISIONES_F5.md` M1–M11. Después de tu OK viene la producción completa de Orleans v2 (imágenes y render con gfx); no arranca sin él.

## En una línea
Los 7 caps salen sin reglas duras. Hay una sola cifra de reclusos (6,375, salvo en el cap 7 que cuenta la contradicción), el detector no encontró ninguna fecha fundida y la voz no dice ningún dato reservado para pantalla. Los caps 6 y 7 ya tienen recorte. Sigue alto el porcentaje de fórmulas de 3 palabras repetidas (8.7 %, por el cap 7), y en el cap 1 la cita «donde pertenecen» queda pegada al 29 de agosto: el chequeo no lo ve porque la cita no tiene fecha en el pool. Costo del narrador Pro: **US$ 0.74** (US$ 1.46 con el 1.er intento).

## Lo que se hizo
1. **Cifras canónicas.** El pool marca el estatus de cada cifra de un mismo conteo: 6,375 oficial (estadísticas del Sheriff), 6,500 aproximada, 8,000 de medios, más el rango. El skeleton deja la oficial y saca las variantes; el cap 7, que trae la de medios, es el de la contradicción. Una variante dicha en otro cap es regla dura (M1, M2).
2. **Fechas.** Regla dura: dos fechas en una oración, un evento del cap contado bajo otra fecha o un evento contado sin fecha (M3). En el prompt va la regla L con tu ejemplo del 28 y el 29.
3. **Largo.** Con Pro, el mínimo sube 15 %: hook 345, desarrollo 920, outro 460 (M4).
4. **Paráfrasis.** Literal es solo cifra, nombre, fecha y cita. Con ids declarados, un evento cuenta si su fecha suena aunque el resto esté parafraseado (M5).
5. **Datos reservados para pantalla.** Van en el skeleton (`pantalla_ids`). Prohibido decirlos (regla dura); el director los pone primeros. Asignados: cap 1 T04 (la última comida), cap 4 T16 (prisioneras a Angola), cap 6 T19 (reabren la HOD) y T23 (demanda de Morgan), cap 7 T22 (informe de la ACLU). Los caps 2, 3 y 5 no tienen: el pool no tiene otro dato que cumpla todo (M7).
6. **count_up** solo con personas, dinero o metros; nunca edades ni fechas (M8).
7. **Canon de m03:** última línea fija, «- Ningún menor en celdas de adultos en ninguna escena.» (M9).

## Narración
| | v1 | v2 F5 | v2 F5c* | v2 F5d |
|---|---|---|---|---|
| densidad por id | — | — | 2.36 | 1.97 |
| densidad por hecho | 0.86 | 2.01 | 2.07 | 1.72 |
| datos distintos | 12 | 41 (regex) | 23 | 21 |
| palabras | 1398 | 1397 | 1017 | **1165** |
| adjetivos/100 (2–4) · caps fuera | 6.22 · 7 | 2.93 · 5 | 1.87 · 3 | **2.58 · 1 (cap 7)** |
| 3-gramas repetidos entre caps (< 5 %) | 3.4 % | 4.1 % | 8.6 % | 8.7 % |
| caps con un dato repetido dentro del cap | 2 | 6 | 1 | **0** |
| cifras no canónicas | — | caps 1 y 3 (6,500) | cap 3 (6,500) | **ninguna** |
| problemas de fechas (detectados) | — | 3 | 1 | **0** |
| datos de pantalla dichos por la voz | — | — | cap 6 (HOD) | **ninguno** |
| caps que aceptan una regla dura | — | — | 2 | **0** |
| cliffhanger con el dato | — | 4/6 | 6/6 | 6/6 |

\* La v2 de F5c está remedida con el juez de F5d: un evento declarado cuenta si su fecha suena. Por eso da 2.36 por id y no el 2.16 de su RESUMEN.

**Abierto:**
- La densidad por id baja de 2.36 a 1.97. Influye que el cap 3 ya no tiene el 6,500 y que la HOD del cap 6 ahora va a pantalla; no medí cuánto pesa cada cosa.
- Los 3-gramas los empujan el cap 7 (27 % de fórmulas ya dichas) y el cap 5 (12 %).
- En el cap 6, «reabriendo edificios apenas semanas después» cuenta sin fecha el evento T19 (reabren la HOD, 17 de octubre de 2005), que además es un dato reservado para pantalla. Ni el chequeo de fechas ni el de reservados lo ven, porque no dice el nombre ni la fecha (lo marcó el revisor).
- En el cap 1, «El sheriff Marlin N. Gusman fue claro: se quedarían "donde pertenecen"» queda bajo el «29 de agosto de 2005» con que abre el cap. La cita no tiene fecha en el pool, así que el chequeo de fechas no la ve.

## Pantalla (simulación, sin render)
| | v1 | v2 F5 | v2 F5b | v2 F5c | v2 F5d |
|---|---|---|---|---|---|
| recortes (todos del pool en v2) | 6 | 7 | 5 | 3 | **6** |
| crítico suma / repite / estorba | 39/5/1 | 33/4/2 | 31/6/3 | 26/3/3 | 27/8/1 |
| caps con reloj / pregunta | 0/6 | 3/6 | 2/6 | 3/6 | 3/6 |

- Chequeo S1–S5: **0 fallas**.
- **Los caps 6 y 7 ya tienen recorte:** «El sheriff Gusman reabre el edificio House of Detention (HOD)» (reservado) y «la Prisión de Orleans Parish (OPP) albergaba a 6,375 reclusos».
- Los reservados T04 y T16 también salieron. T23 y T22 no entraron sin pisar otro bloque.
- Contador: solo «500 prisioneros» (en F5c había uno de «10 años»).
- «Repite» del crítico sube a 8.

## Prompts de imagen de v2 (texto)
- 97 prompts, 44 con personas: `PROMPTS_PERSONAS_v2.md`.
- **El que reemplaza al del niño en la celda: ch05 imagen 6** («Entre los atrapados por esta catástrofe había niños de hasta 10 años»), en el centro juvenil.
- No queda ningún prompt con niños en una celda de adultos: los dos con niños van al centro juvenil.

## Dónde está
- Código:
  - `researcher_steps/evidence_pool.py` (`canonical_figures`);
  - `script_engine/m01a_skeleton.py` (`canonize_figures`, `assign_screen_ids`, `finalize_pool_plan`);
  - `m01b_narrator.py` (reglas L–O, largo +15 %);
  - `m05_narrative.py` (`non_canonical`, `screen_leaks`, `date_problems`, conteo por fecha declarada, miles con punto);
  - `gfx_pool.py` (reservados primero);
  - `gfx_director.py` (`is_count_quantity`);
  - `m03_visual.py` (línea de menores).
- Tests: `test_module_f5d.py` (nuevo, 8). Suites de guion y gfx: **393 verdes** + 3 fallas viejas de `01b_pauses`.
- Comparación: `lab/guion/compara_orleans.html`, con columna F5d. Tablas: `GUION_v1_v2.md`, `SIM_v1_v2.md`. Copias: `v2/` (F5d), `v2_f5c/`, `v2_f5b/`, `v2_f5/`.
- Se reproduce con `correr_f5_orleans.py --etapa todo`.
- md5 de `topics_db.json`, `normalizer_custom_dict.json`, `lexico_propuestas.json` y `misterio.json`: iguales.

## Veredicto del revisor (revisor-handoff, íntegro; dado antes del commit: el caso del cap 6 ya está en «Abierto»)

VEREDICTO: CUMPLE CON OBSERVACIONES

Los 7 ítems están implementados y las cifras del RESUMEN coinciden con los json y md. Corrí la suite pedida: 393 verdes y 3 fallas viejas de test_module_01b_pauses.py, como se esperaba. Hay dos observaciones de contenido.

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Cifra canónica en todo el video, validador duro | OK | 01_facts_sources.json trae cifras_canonicas (oficial D57 = 6,375; D05 rango; D33 6,500 aprox.; D58 8,000 medios). En 01b_narration.json, 6,500 no aparece en ningún cap. 8,000 aparece solo en el cap 7 (la contradicción: "oficialmente 6,375… otras fuentes estiman 8,000"). El cap 1 usa solo 6,375. |
| 2 | Fechas, sin fundir dos | PARCIAL | El cap 1 no mezcla 28 y 29: usa solo "29 de agosto de 2005". Pero la cita "donde pertenecen" queda pegada al 29 (el RESUMEN lo declara; Q01 no tiene fecha en el pool y el anuncio del 28, T05, está en el cap 2). En el cap 6, "reabriendo edificios apenas semanas después" cuenta el evento T19 (17-oct-2005) sin su fecha. El RESUMEN no declara este caso. |
| 3 | Largo +15 % para el narrador Pro | OK | Mínimos 345/920/460 en m01b_narrator.py (POOL_MIN_LEN_FACTOR). Caracteres reales: cap 1 = 363, cap 2 = 932, caps 3–6 = 1090–1475, cap 7 = 967. Todos cumplen; el cap 2 pasa por solo 12 caracteres. |
| 4 | Paráfrasis permitida salvo cifra, nombre, fecha o cita | OK (parcial) | Regla en el prompt. Los 3-gramas repetidos entre caps siguen en 8,7 % contra el umbral de 5 %; el RESUMEN lo declara como abierto. |
| 5 | Datos reservados para pantalla (pantalla_ids) | PARCIAL | Asignados: cap 1 T04, cap 4 T16, cap 6 T19 y T23, cap 7 T22. Los caps 6 y 7 tienen al menos uno. La voz no dice los datos de forma literal. Salvedad: el cap 6 narra el evento de T19 ("reabriendo edificios") sin nombre ni fecha; el detector no lo marca. Lo cuento como fuga semántica leve. |
| 6 | count_up solo para cantidades | OK | is_count_quantity en gfx_director.py, con descarte en validate_plan. En lab/hyperframes/f5/cues/gfx_cues_v2_ch07.md:15 hay un único contador, "500 prisioneros". En el ch05 se descartó el de 517 reclusos. No hay edades ni fechas. |
| 7 | Línea de menores en el canon de m03 | OK | m03_visual.py, _format_documented_locations: la línea se agrega después del "if not lines", como última línea del bloque. Sin pool la función devuelve "" antes (línea 315), así que el canon sin pool queda byte-idéntico. Test en test_module_f5d.py:91. |

Otros chequeos:
- Costo: 0,7411 USD en 01b_costo.json y 0,7183 USD en el intento 1. La suma es 1,46 USD, igual al RESUMEN.
- Palabras: 1165, igual a GUION_v1_v2.md y al RESUMEN.
- Bytes 0x08: 0 en todos los .py tocados.
- Entregables: RESUMEN_F5d.md, compara_orleans.html (menciona F5d 9 veces), PROMPTS_PERSONAS_v2.md (97 prompts, 44 con personas, canon con la línea nueva), v2_f5c/ y v2/, DECISIONES_F5 hasta M11. ESTADO_SESION.md actualizado.
- El RESUMEN deja la sección "Veredicto del revisor" como placeholder, a rellenar con este texto.
- Honestidad del RESUMEN: declara lo no logrado (3-gramas en 8,7 %, densidad por id que baja, cita pegada al 29, T23 y T22 sin recorte). No declara el caso del cap 6 (T19).

Fuera de alcance: diag_234_cap4.py, modificado y que no es de F5d (el pedido ya lo dice). El resto de lo modificado está dentro del alcance. Los archivos sin seguimiento (CLAUDE.md, _lab_*, _probe_*, QA_* y similares) son ajenos al trabajo y hay que excluirlos del commit.

Riesgos que el contrato no cubre: (1) los detectores de fechas y de reservados trabajan con las fechas del pool; las citas sin fecha y las paráfrasis sin nombre ni fecha los esquivan. (2) ESTADO_SESION.md dice "Último commit: F5d", pero el commit todavía no existe. (3) La densidad por id baja de 2,36 a 1,97 y no se midió qué la causa.
