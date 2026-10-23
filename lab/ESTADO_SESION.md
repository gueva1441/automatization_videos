# ESTADO_SESION — dónde estamos (leer ANTES de programar)

Última actualización: 2026-10-22 (F10 en PARADA §4.3 en `f10-integracion-v3`: guion de Ycuá Bolaños listo para leer) · CC lo actualiza en cada hito (commit, reporte, decisión de Omar).

## Proyecto activo
- Repo: `C:\CLAUDE_PROJECTS\automatization_videos` · rama activa **`f6-guion-v3`** (desde `45c052c`, tip de `f5-guion-v2`, que sale de `39e37ac`). Último commit: «docs(f6): F6c cerrado como laboratorio…» (`git log -1`) en f6-guion-v3, sobre `7ec2025`; f5-guion-v2 termina en `45c052c` («F5f: cierre Orleans (lab)»).
- Cadena de ramas sin mergear: `f2-gfx-director` (F2b @ `31c671c`) → `f3-lab-identidad` (F3–F4e @ `39e37ac`) → `f5-guion-v2` (F5).
- `main` = `43f528a`. NO se toca sin OK explícito de Omar.
- Video de prueba: Orleans `ba6c3cac-a091-41c0-8dad-afd2f4364747` (7 caps; ch02 es el cap de calibración, ch05 el segundo). Copia del research para F5: **`ba6c3cac-f5v2`**.
- Candados vigentes:
  - md5 de ch02 `--only-cap` sin `--gfx` = `38e5ba14…` (último: `lab/hyperframes/f4e/corrida/onlycap_ch02_nogfx_f4e.log`);
  - 364 tests verdes en las suites de guion y gfx. Las 3 fallas de `test_module_01b_pauses.py` son previas a F5.

## F10 — Integración v3 + Ycuá Bolaños — **PARADA §4.3: guion de Ycuá Bolaños listo para leer** (esperando el OK de Omar)
- Rama **`f10-integracion-v3`** desde `790bec9`. Handoff `lab/hyperframes/f10/HANDOFF_F10_integracion_v3.md`; reporte `lab/hyperframes/f10/F10_PARADA_REPORT.md` (revisor íntegro); decisiones `DECISIONES_F10.md` (D1–D18).
- **§4.1 hecho:** `fase1_5 --v3` (m01a = compuerta + escaleta; m01b = guionista → editor → `m01d_particion` → juez), `--from <paso>`, contrato de 7 caps con `narration_tts` e `ids_usados`; corrida en seco de Orleans hasta assemble, verde. Arreglado `topic_researcher` (el pool v3 no llegaba al topic).
- **§4.2 hecho:** topic `f8s1-ycua-bolanos` completado en topics_db (4a–4e); guion: humano Liz Torres, pico T21 11:25, 1,235 palabras, 20 duras. Leer `NARRACION_ycua.md`, `ESCALETA_ycua.md`, `06_judge_ycua.json`.
- **Siguiente (solo con el OK):** si la nota < 8, una corrida de ajuste con notas (`fase1_5 --topic f8s1-ycua-bolanos --v3 --only m01b`, notas en `_steps/f8s1-ycua-bolanos/escaleta_notas.md`); si ≥ 8, §4.4 producción: `fase1_5 --topic f8s1-ycua-bolanos --v3 --from normalizer_gate --batch` → fase2a → fase2b --gfx (B1 antes del render; Firefox cerrado; RAM ≥ 18 GB).
- Costo hasta acá: research del topic US$ 0.99 + guion US$ 0.88.

## F8b + F9 — Research, imágenes y voz v4 — HECHO (§5 completo; Omar escucha y mira al volver)
- Rama **`f9-voz-v4`** desde `cd3f2e5`. Handoff `lab/hyperframes/f9/HANDOFF_F8b_F9.md`; reporte `lab/hyperframes/f9/F8b_F9_REPORT.md` (revisor íntegro); decisiones `DECISIONES_F9.md` (D1–D21). Sin merge, sin render, sin QA Studio.
- **Research:** antigüedad por ítem, PDF enlazado que nombra el evento, R3 con reintento, R1 con Flash alternativo. S2 Cromañón rojo → **amarillo**; S3 Vajont sigue **rojo** solo por 0 elegibles (121 datos). S1 verde.
- **Imágenes:** armas (beat de disparo desde las víctimas), pico humano, texto en el idioma del lugar, escala del pool, clichés; **grade de post** (`script_engine/image_grade.py`, `_graded.png`, solo v3 o `IMAGE_GRADE=1`). Re-humo en `compara_imagenes_f8.html` (3 columnas) y `humo/hoja_contactos_f8b.jpg`. El #7 sigue flojo.
- **Voz:** v4 + MS Narrador (`voice_id_v4` en el perfil; v2 + Bill intactos; `TTS_V2=1`), etiquetas desde el guion (`script_engine/tts_tags.py`, `narration_tts`), voz v4 normalizada a −24 LUFS. Prueba: `lab/hyperframes/f9/audio/cap2_cap4_v4_msnarrador.mp3` y `…_bill.mp3` (fuera de git).
- `max_beats` 14. Tests: 563 verdes + 5 previas. Costo medido de la tanda: US$ 2.23.

## F8 — Imágenes v3 + cierre de guion + 3 semillas — HECHO (§4 completo; Omar lee al volver)
- Rama **`f8-imagenes-v3`** desde `524573d` (punta de `f7-research-v3`). Commits: `a59ab76` §2 · `73e3613` §1 A–F · `c24de5c` humo + semillas · `db387b4` reporte · commit final con el veredicto del revisor. Sin merge, sin render, sin QA Studio.
- **Leer:** `lab/hyperframes/f8/F8_REPORT.md` (revisor íntegro), `compara_imagenes_f8.html`, `humo/hoja_contactos.jpg`, `semillas/SEMILLAS.md`, `DECISIONES_F8.md` (D1–D23).
- **§2:** escaleta con ≥ 2 beats por cap de desarrollo → 12 beats exactos en verde (`video_length`: `min_beats_dev_cap`, `max_beats`); última frase del video = cita o pregunta (blanda al editor, prompt `f8-1`).
- **§1:** Seedream 5.0 Lite (`fal-ai/bytedance/seedream/v5/lite/text-to-image`, `/edit` probado OK, sin `seed`, US$ 0.035), `pipeline.fal_concurrency` 20, 3 intentos en 429/503, `ms` por imagen. m03 v3 (`script_engine/m03_imagenes_v3.py`) solo con escaleta: ancla por beat, estilo al principio y al final, reglas de composición y sensible con validador + re-hechuras, marca `sensible` al manifest; re-encuadre solo como propuesta inerte. v2 byte-idéntico.
- **Humo:** 12/12 imágenes de Orleans f7r3, 35–68 s c/u, 68 s de pared, US$ 0.49 con la rehecha y el `/edit`.
- **Semillas:** S1 Ycuá verde (US$ 1.29) · S2 Cromañón rojo por datos (PDF equivocado de R2, caída de Pro) · S3 Vajont rojo en 0 (la regla «documento > evento + 20 años» descarta todo lo de 1963). No se eligió; S2 y S3 marcadas en el inbox.
- `config.py` (fuera de git) editado en local: `seedream_per_image` 0.035, `pipeline.fal_concurrency` 20.
- Tests: 526 verdes + las 5 fallas previas conocidas.
- Sin commitear a propósito: `diag_234_cap4.py`, `gfx_profiles/lexico_propuestas.json`, `gfx_profiles/misterio.json`, `lab/hyperframes/f7/topics_db_pre_f7b.json`.

## F7 — Research v3 — F7c-3 + F7d HECHOS (cerrado; Omar lee la columna F7c-3)
- Leer `lab/hyperframes/f7/F7c3_REPORT.md` (revisor íntegro) y `compara_orleans_v3r.html` (5 columnas).
- **F7c-3** (§9.1): 7 reglas de oficio en `script_engine/guion_v3_reglas.py` (rol, párrafo sin dato, antagonista con nombre, sin fotos, sin tráiler, ancla de lugar y fecha; eco blando al editor) y 110 + 250 × 5 + 140. Corrida (2.ª, tras arreglar un bug del ancla): 1,143 palabras, 21 duras (re-medidas con las reglas de hoy: F6c 12, F7c 29, F7c-2 23). Arregla roles, tráiler, ancla, Gusman con nombre; queda largo corto (5 caps bajo el mínimo), párrafos sin dato y el candado literal.
- **F7d** (§9.2): `researcher_steps/pool_gate.py` (verde/amarillo/rojo, `POOL_GATE.md`, umbrales en `video_length.py`) antes de la escaleta; research v3 por defecto en `topic_researcher` (`RESEARCH_V3=0` → viejo); seed rojo vuelve al inbox con motivo. Orleans: verde. `run_seed` sin probar con un seed real.
- Tests: 466 verdes (+ las 5 fallas previas fuera de la lista).

## F7 — Research v3 — F7c-2 HECHO
- **F7c-2** (validación del analista sobre F7c: «material de 9, narración 7.5–8»; §8 confirmado por Omar). Leer `lab/hyperframes/f7/F7c2_REPORT.md` (revisor íntegro) y `compara_orleans_v3r.html` (4 columnas).
  - §8: `script_engine/video_length.py` (lee `config.long_video`; `config.py` está fuera de git): 1,500 / 1,700 palabras, caps de 105 s, 16 fotos por cap como máximo (90 por video). `m01a_skeleton.CHAPTER_SCHEMA` y `m01a_escaleta.CAP_WORDS` salen de ahí.
  - Reglas duras nuevas (`script_engine/guion_v3_reglas.py`, desde `m01b_guionista.review`): fragmento de cita ≤ 25 palabras (el candado lo acepta: `evidence.anchors`), una cita por párrafo, gancho sin fotos/fechas/citas de después, juicios fuera del pool, nombre completo 1 vez por cap, repetición de 3 palabras entre caps.
  - Corrida: humano Reed, pico francotiradores (cap 5), gancho agua del inodoro. 1,252 palabras, 12 citas, 7 testigos con nombre, 11 duras (F7c: 16). A la lectura: dos roles cambiados (Ducre, Big Whappy) y juicios que la lista no ve. Notas que no entraron: 6,375 suena 0 veces (fue a pantalla), T39 no se usó y Gusman no se nombra en el cap 2. Largo 83 % del objetivo. Revisor: CUMPLE CON OBSERVACIONES.
  - Tests: 447 verdes en guion/gfx/m01/m03; 5 fallas previas (3 `01b_pauses`, 2 `m03_merge_timing`).

## F7 — Research v3 — F7c (pool v3 por la tubería v3) — HECHO
- **F7c** (pedido: validación del pool «aprobado, materia prima de 9» + 3 arreglos + corrida). Leer `lab/hyperframes/f7/F7c_REPORT.md` (veredicto del revisor íntegro) y `compara_orleans_v3r.html`.
  - Arreglos: `presente_en` por párrafo (±500), elegibles re-armados (12); población con todas sus variantes (oficial 6,375, ACLU/sheriff); `pool["digest"]` y `m01a_escaleta.pool_section` lo usa (flag `ESCALETA_DIGEST`): prompt de escaleta 18.7 k tokens.
  - La corrida destapó 3 problemas del pool contra los validadores de F6 (cita de una palabra, descartes como «personajes», cifras con punto de miles): arreglados en el pool.
  - Resultado (corrida 5, sin notas del analista): más testigos y citas (Reed humano; Richard, Reyes, Burton), pero 940 palabras, densidad 1.70 y 16 duras (F6c: 1,070 / 2.15 / 4). Las duras: el guionista parafrasea citas largas y el candado literal las rechaza.
  - **Pendiente de confirmar:** el §8 del handoff (parámetros de largo 1,500 palabras, tope de fotos en m03, lat/lon en el digest, geocoder) no estaba en el pedido de chat: no aplicado.

## F7 — Research v3 (leer documentos) — F7a y F7b HECHOS (pool aprobado por el analista)
- **Leer:** `lab/hyperframes/f7/F7b_pool.md` (métricas contra f6v3, costo, lo que mirar; veredicto íntegro del revisor: CUMPLE CON OBSERVACIONES) y `F7a_fuentes.md`.
- **Pool** `lab/hyperframes/f7/00_pool_v3.json` (= `data/scripts/_steps/ba6c3cac-f7r3/00_pool_v3.json`): 558 datos (6.1× f6v3), 152 eventos (28 con hora), 188 citas (162 verificadas literal), 25 citas de testigos con nombre verificadas (20 personas), 13 elegibles como humano, 100 % con doc_id + posición. 10 documentos (HRW 2005 bajó por Wayback en el reintento).
- **Abierto:** costo ≈ US$ 2.6–2.8 por tema (> 2.5); cifras canónicas casi vacías; prompt de la escaleta ≈ 63 k tokens con este pool (riesgo 4: propuesta de resumen por documento para F7c); `RESEARCH_V3` sin cablear en `topic_researcher`; 4b–4e no corridos con el pool; faltan BBC, prensa de 2005 y el fallo Waganfeald.
- **Topic** `ba6c3cac-f7r3`: `01_facts_sources.json` (f6v3 + pool nuevo) y entrada nueva en `data/topics_db.json` (copia de f5v2); respaldo `lab/hyperframes/f7/topics_db_pre_f7b.json` sin commitear.
- Re-armar el pool gratis: `python -I lab/hyperframes/f7/f7b_pool_orleans.py --sin-llm --revalidar F01,F03,F08,F09`.
- Handoff: `lab/hyperframes/f7/HANDOFF_F7_research_v3.md`. Rama **`f7-research-v3`** desde `c7da0ba` (f6-guion-v3). Sin merge a main.
- Código: `researcher_steps/research_v3.py` (R1 descubrimiento, R2 descarga, R3 extracción, R4 merge, R5 verificación). Topic nuevo `ba6c3cac-f7r3` (datos en `data/scripts/_steps/ba6c3cac-f7r3/`, fuera de git).
- **F7a** (`lab/hyperframes/f7/f7a_fuentes_orleans.py` → `F7a_fuentes.md`): 10 documentos bajados. R1: las URLs salen SOLO del grounding (el modelo pone la ficha; las que no fichó, Flash); Pro con temperatura 0.7 (con 0.0 contestaba de memoria, sin grounding). Faltan: BBC, Times-Picayune, Toledo Blade y el fallo Waganfeald (no salen en el grounding).
- Ojo: `python -I` ignora `PYTHONIOENCODING` (los runners hacen `sys.stdout.reconfigure`). archive.org devuelve 429 si se le pega seguido: no reintentar en bucle.

## F6 — Guion v3 — F6c CERRADO COMO LABORATORIO; F6d/F6e pendientes hasta F7 (decisión del analista, 2026-10-21)
- Handoff: `lab/hyperframes/f6/HANDOFF_F6_guion_v3.md`. Rama **`f6-guion-v3`**, desde `45c052c`. Sin merge a main.
- **Cierre:** el analista paró F6 acá: no se regeneran la escaleta ni la narración. F6c queda como laboratorio; F6d (partición en 7 caps, `regenerate_caps` v3, m05 ampliado) y F6e (comparación) esperan a F7 (research v3: fuentes con URL, documentos bajados, pool extraído leyéndolos). F7 corre en una sesión nueva, rama `f7-research-v3` desde `f6-guion-v3`, con el handoff `lab/hyperframes/f7/HANDOFF_F7_research_v3.md`.
- **Último commit de F6:** `7ec2025` («feat(f6c): …») + este cierre de ESTADO_SESION.
- **Leer:** `lab/hyperframes/f6/F6c_REPORT.md` (A/B/C, lo que queda, veredicto íntegro del revisor: CUMPLE CON OBSERVACIONES), `NARRACION_orleans_v3.md`, `ESCALETA_orleans.md` (f6b-4) y `F6c_verificacion.md`. Antes: `F6b3_REPORT.md` y `F6ab_REPORT.md`.
- **Frenos (§5) intactos** (+ `m05_narrative` y `m01b_narrator` sin tocar: se usan).
- **A — verificación literal:** `researcher_steps/verify_quotes.verify_literal`. Fuentes bajadas en `data/scripts/_steps/ba6c3cac-f6v3/fuentes/` (BBC/rebelion 2006, PDF de la ACLU 2006, The Lens 2025).
  - Verificadas: Q03 (Burton) y Q04 (Norman, literal BBC «Simplemente abandonaron la cárcel»); D95 nuevo (103 días).
  - Fuera del pool: Q05 (atribución errónea) y Burnley / Chad Joseph (contaminación).
  - Sin verificar: Q06, Q07, Q11–Q13.
- **B — escaleta f6b-4:** reglas `contador`, una cifra en pantalla una vez, pregunta del cap 7 obligatoria, cierre sin eco, `escaleta_solo_apoyo`, citas sin verificar fuera de pantalla.
  - Pico: los cadáveres en el cap 4. 517 en el cap 5 con contador. Norman en los caps 2, 3 y 7.
- **C — guionista y editor:**
  - `script_engine/m01b_guionista.py`: Pro, texto completo, best_of_2, `review` con m05 por cap + reglas v3.
  - `script_engine/m01c_editor.py`: guardia léxica + validadores; un párrafo rechazado vuelve al original.
  - Narración de Orleans (f6c-3): 1,072 palabras, 4 duras; el editor aceptó 10 de 19 cambios.
- **Pendiente para el analista (antes de F6d):**
  - citas en fragmento contra `cap_review`;
  - invenciones semánticas que ningún validador ve (propuesta: validador semántico + regla «nada de pensamientos de personas reales»);
  - el cap 6 en los diques;
  - el costo (≈ US$ 1.9 en esta tanda).
- **Tests:** `test_module_f6a` (3), `f6b` (31) y `f6c` (4). Suites: 448 verdes + 3 viejas.

## F5f — Cierre de Orleans (laboratorio) — CERRADO, PARADA (el analista valida desde disco)
- **Rama:** `f5-guion-v2`. **Último commit:** «F5f: cierre Orleans (lab)» (`git log -1`), sobre `cc625e2` («wip: F5f pre-cierre»). Omar no publica este video.
- **Sin mergear a main** (`main` = `43f528a`, intacta; no se hace merge sin OK de Omar): la cadena `f2-gfx-director` → `f3-lab-identidad` → `f5-guion-v2` (61 commits por delante de main). Quedan aparte `f1-gfx-layer` y `lab/kling-transform-probe`.
- **Leer:** `lab/hyperframes/f5/F5f_REPORT.md` (tabla por cap, lo que no salió y el veredicto íntegro del revisor: CUMPLE CON OBSERVACIONES) y `DECISIONES_F5.md` U1–U11.
- **Hecho:**
  - Arreglos 1–6:
    - sustantivo con ícono sobre adjetivo;
    - palabras del tema a peso 1;
    - reservados con prioridad y motivo de choque;
    - bloque `quote_card`;
    - eco de cifra y 15 s entre recortes;
    - nivel de agua desde un reservado;
    - titulares sin comilla abierta.
  - D15 como reservado del ch02, en el skeleton (respaldo en `produccion/01a_skeleton_pre_f5f.json`).
  - Reloj que cambia de fecha.
  - Render de la capa gfx solo de ch02, ch05, ch06 y ch07 (`render_f5f_caps.py`, `--only-cap --reuse-visuals`). Capas en `_fase2b_work/chNN_gfx.mp4`; las anteriores, en `_bak_f5f_pre/`; hojas en `lab/hyperframes/f5/produccion/hojas_f5f/`.
  - Sin render completo: el `_final_gfx.mp4` sigue siendo el de F5e.
- **Quedó solo en simulación** (`produccion/SIM_F5f.md`, `_sim_gfx/`):
  - ch01: fuera el 6,375 y T04 a los 14.7 s;
  - ch04: T16 y el reloj 30 AGO → 2 SEP.
- **Ojo:** durante la sesión se regeneraron fotos desde el botón «arreglar» de QA Studio: ch01_supp_04, ch03_img_02 y ch03_img_10 (backups en `assets/_qa_backups/`). Eso borró `ch01_hybrid_visual.mp4` y `ch03_flux_visual.mp4`; un render futuro los rehace con DepthFlow. QA Studio sigue abierto en :8000 desde F5e.
- **Tests:** 410 verdes + 3 fallas viejas de `01b_pauses`.
- **Archivos sueltos sin commitear (a propósito):**
  - `gfx_profiles/misterio.json`: el render promueve solo palabras al léxico (por ejemplo «negrura»: 3);
  - `gfx_profiles/lexico_propuestas.json`;
  - `lab/hyperframes/f5/produccion/topics_db_pre.json`;
  - `diag_234_cap4.py`: no es nuestro y nunca se commitea;
  - `lab/hyperframes/f5/produccion/qa_studio.out`;
  - `data/scripts/_steps/ba6c3cac-f5v2/01a_skeleton.json` (fuera de git; D15 aplicado).
  - Además, unos 135 sueltos de laboratorio ajenos a F5 (`_compare_*`, `_lab_*`, `_probe_*`, mp4).

## F5e — Arreglos de capa gfx tras ver el video — render hecho, PARADA tras el commit final
- Pedido (Omar/analista, después de ver Orleans v2): solo capa gfx, sin tocar guion ni imágenes.
- **Hecho y commiteado en `wip(f5e)`:**
  - G2: titular de recorte hasta 12 palabras; de 9 a 12 baja un cuerpo (`archive_head_max_words_pool`, `gfx_project.archive_head_px`). Los datos reservados para pantalla van primero y, si chocan, se corren dentro de la escena (`gfx_pool._free_slot`); un reservado entra aunque la voz no lo nombre (`_sentence_for(reserved=True)`).
  - G1: el crítico recibe dos cuadros (foto sola + bloque dibujado) y no puede decir «repite» por su propio sello (`gfx_critic`, prompt `g1-snap-2`).
  - Sellos: token `stamp_nouns_only`; el director de intensidad devuelve `clase` y `neutra` (`gfx_intensity` PROMPT_VERSION `f5e-1`). Fuera los verbos (`is_verb_form`, `stamp_lexicon`) y las neutras (estrella, suerte, estruendo, agujero).
  - Contador: un contador por hecho (`gfx_pool.count_groups` / `pool_count_up`): 517 y «más de 500» son el mismo hecho; se anima 517 en el primer cap que lo dice (ch05) y se saca el 500 del ch07.
  - m00: `topic_researcher.MAGNITUDE_SECTION` ([DATOS DE MAGNITUD]) solo en el ángulo técnico; humano y misterio quedan idénticos. Solo el prompt; Orleans no se re-investiga.
  - QA Studio: marca «↻ regenerar» por foto (`/mark`, `/marks` → `output/<id>/assets/_qa_marks.json`). `lab/hyperframes/f5/regen_marcadas.py` regenera solo las marcadas con el mismo prompt, otra semilla y sin validador de visión (`qa_studio_server._reseed_core`).
  - Sincronía: `lab/hyperframes/f5/sync_check.py` (faster-whisper del venv `C:/CLAUDE_PROJECTS/viral-video-pipeline/.venv`) → `produccion/SYNC_v2.md` y `SYNC_ba6c3cac_v1.md`. v2 da como v1: mediana +100 ms en los 7 caps, igual en v1, que no tenía aviso (sesgo de Whisper); p95 240–500 ms y máximo 1.04 s (ch06 «inició»). El ASS coincide con los timestamps (el pre-pad de 1.8 s solo va con `--hook`, que no se usó). No se miró a ojo: es una medición.
  - Tests: `test_module_f5e.py` (6). Suites: 397 + 6 verdes, 3 viejas de 01b_pauses.
- **Render hecho:** `produccion_orleans_v2.py --etapa render_gfx` (fase2b `--reuse-visuals --keep-segments --gfx --gfx-sparse --gfx-quality looks`): rc=0 en 41.0 min, RAM 18.7 GB, Firefox cerrado. Logs en `lab/hyperframes/f5/produccion/render_gfx.out` y `fase2b_gfx.out`.
  - **Nuevo final:** `output/ba6c3cac-f5v2/ba6c3cac-f5v2_final_gfx.mp4` (571.2 s, US$ 0.02 de Gemini). El anterior quedó como `…_final_gfx_f5d.mp4`, y capas, planes, hojas y cues anteriores en `_fase2b_work/_bak_f5e_pre/`.
  - **Resultado:** recortes 2 → 5; reservados en pantalla T04 (ch01) y T22 (ch07); T16, T19 y T23 no entraron porque chocan en toda la escena. Ningún sello neutro ni verbo. Crítico 24/27, 0 «repite» por su propio sello. Contador 517 en ch05, sin el 500 en ch07; el 6,375 del ch01 lo limpió el pico.
  - Hojas de contactos en `lab/hyperframes/f5/produccion/hojas_f5e/`. Reporte en `lab/hyperframes/f5/F5e_REPORT.md`; decisiones Q1–Q7 en `DECISIONES_F5.md`.
  - **QA Studio:** abierto en http://127.0.0.1:8000 (topic `ba6c3cac-f5v2`). Todavía no hay marcas.
- **Falta:**
  1. Revisor-handoff, con el veredicto íntegro en `F5e_REPORT.md`, y commit final `feat(f5e)`. Después, PARADA.
  2. Cuando Omar marque fotos en QA Studio: `PYTHONIOENCODING=utf-8 python lab/hyperframes/f5/regen_marcadas.py --topic ba6c3cac-f5v2` y después `produccion_orleans_v2.py --etapa render_gfx`. Antes, borrar o renombrar `_bak_f5e_pre` para que el respaldo nuevo no se saltee, o pasar otro tag.
- No commitear: `diag_234_cap4.py`, `gfx_profiles/lexico_propuestas.json` (lo decide Omar), `lab/hyperframes/f5/produccion/topics_db_pre.json`.

## Producción de Orleans v2 — Omar vio el video; pidió F5e (arriba)
- **Video:** `output/ba6c3cac-f5v2/ba6c3cac-f5v2_final_gfx.mp4` (571.2 s, gfx looks disperso, identidad y crítico activos).
- Leer `lab/hyperframes/f5/F5_PRODUCCION_REPORT.md` (revisor íntegro) y `DECISIONES_F5.md` P1–P9.
- **Hecho:** retoque de los caps 5 y 6; bloque G (G1 crítico sobre snapshot, G2 titular ≤ 8 palabras, G3 `verify_crop` del zoom final, G4 íconos espiral y rayo tachado); TTS, imágenes (81 + Veo ch01/ch07) y un solo render en 77.8 min.
- **Costo de esta tanda:** ≈ US$ 6.2 (imágenes 3.24, Veo 0.48, Gemini ≈ 2.0, TTS ≈ 0.21, íconos 0.27).
- **Abierto:**
  - G1 confunde el sello dibujado con la foto (2 bloques sacados de más);
  - G2 dejó 2 recortes en todo el video;
  - aviso de alineación del TTS sin verificar a ojo;
  - tinte «lavado» del mood muerte.
- Tests: 397 verdes + 3 viejas.

## F5d — Último ajuste antes de producción — superado (producido)
- Leer `lab/hyperframes/f5/RESUMEN_F5d.md` (revisor íntegro) y `DECISIONES_F5.md` M1–M11.
- **Hecho:**
  - cifras canónicas (6,375 oficial; la contradicción solo en el cap 7);
  - fechas como regla dura;
  - largo +15 % con Pro y paráfrasis permitida;
  - datos reservados para pantalla (`pantalla_ids` en el skeleton);
  - count_up solo con cantidades;
  - línea «ningún menor en celdas de adultos» en el canon de m03.
- **Resultado:**
  - ningún cap con reglas duras; densidad por id 1.97; adjetivos 2.58; 1165 palabras; cliffhangers 6/6;
  - pantalla: 6 recortes, los caps 6 y 7 ya tienen;
  - 3-gramas 8.7 % (cap 7).
- **Costo:** Pro US$ 1.46 (2 corridas). Tests: 393 verdes + 3 viejas.
- **Siguiente, solo con el OK del analista:** producción completa de Orleans v2 (imágenes + render con gfx). Antes de renderizar, Firefox cerrado y RAM > 14 GB (memoria).

## F5c — Solo narración: skeleton congelado, narrador Pro, mejor de 3 — superado por F5d
- Leer `lab/hyperframes/f5/RESUMEN_F5c.md` (revisor íntegro) y `DECISIONES_F5.md` L1–L8. La pantalla y §1.6 de F5b no cambian.
- **Hecho:**
  - skeleton de F5 congelado (token `skeleton_frozen`, ids traducidos al pool de F5b; Hubert y Schwarz fuera);
  - con pool, el narrador es Gemini Pro y elige el mejor de 3 por cap (puntaje del analista);
  - reglas duras y blandas en el prompt y en `cap_review` (no inventar, no contaminar);
  - 8 frases nuevas de relleno prohibido.
- **Resultado:**
  - densidad por id 2.16 (F5b 1.26); cliffhangers 6/6; Gusman desde el cap 1;
  - en contra: 1017 palabras, adjetivos 1.87 y 3-gramas 8.6 %;
  - pantalla: 0 fallas S1–S5, 3 recortes;
  - prompts: el reemplazo del niño es ch05 imagen 6, en el centro juvenil; queda ch04 imagen 13 (adolescente en celda de adultos).
- **Costo:** Pro US$ 0.69. Tests: 385 verdes + 3 viejas. Respaldos de F5b: `lab/hyperframes/f5/v2_f5b/`, `output/ba6c3cac-f5v2/_bak_f5c_pre/`.

## F5b — Arreglos de la validación (N1–N5, S1–S6) — superado por F5c en la narración (la pantalla sigue)
- Pedido: `lab/hyperframes/f5/VALIDACION_F5.md` §7. Leer `lab/hyperframes/f5/RESUMEN_F5b.md` (revisor íntegro) y `DECISIONES_F5.md` K1–K20.
- **Hecho:**
  - pool: filtro de relevancia (fuera la posada de 1902 y el médium), personajes solo si actúan (fuera Schwarz y Hubert) y mayúsculas;
  - narrador: declara `datos_usados` (las métricas cuentan por id), cada dato una vez por cap, adjetivos entre 2 y 4/100;
  - pantalla: cláusula completa, cronología, dedupe por hecho (sin el cap siguiente), ícono por mapa literal (token `icon_literal_only`), metros;
  - §1.6: bloque UBICACIONES DOCUMENTADAS en el canon de m03 (FRENOS respetados) y 97 prompts de v2 regenerados (texto).
- **Resultado:**
  - pantalla v2 sin fallas S1–S5;
  - narración con menos datos que la v2 de F5: por hecho, 1.12 contra 2.01 (v1: 0.86); por id, 1.26;
  - P5 (caps 6 y 7 sin recorte) sigue;
  - dos prompts con un niño solo en celda de adultos (ch01 supp 3, ch07 Veo).
- Tests: 379 verdes + 3 viejas de `01b_pauses`. Se reproduce con `correr_f5_orleans.py --etapa todo`. Respaldos de F5 en `lab/hyperframes/f5/v2_f5/`, `output/ba6c3cac-f5v2/_bak_f5b_pre/` y `output/ba6c3cac-a091…/_fase2b_work_f5sim_v1_bak_f5b`.

## F5 — Guion v2 (`lab/hyperframes/f5/HANDOFF_F5_guion_v2.md`) — validado por el analista (`VALIDACION_F5.md`): pidió F5b
- Commits en `f5-guion-v2`: `66ee44b` §1.1 · `2be6c11` §1.2 · `fc955ef` §1.3–§1.5 · `e18e656` §2 · `e7b661c` §3.
- **Hecho:**
  - §1.1 `evidence_pool` en el research (`researcher_steps/evidence_pool.py`, lo llama `step_4a_facts`);
  - §1.2 skeleton con datos por cap, personajes y cliffhanger (`m01a`);
  - §1.3 narrador con los datos del pool y reglas A–G (`m01b`);
  - §1.4 normalizer: horas AM/PM, dólares, %, comillas y siglas (`tts_normalizer`, `m02_5`);
  - §1.5 juez narrativo determinista (`script_engine/m05_narrative.py`);
  - §2 pantalla desde el pool (`script_engine/gfx_pool.py`: candado, recortes y datos, ícono por contenido, reloj, pregunta del cliffhanger) + `apply_gfx(plan_only=True)`;
  - §3 guion v2 de Orleans, comparación y simulación del director sin render.
- **No hecho:** §1.6 (`m03_visual` con lugares y objetos del pool; era opcional). Tampoco los íconos espiral y rayo tachado (F5 es sin imágenes).
- **Dónde está:**
  - comparación v1/v2: `lab/guion/compara_orleans.html` (generador: `lab/guion/build_compara_orleans.py`);
  - cues de la simulación: `lab/hyperframes/f5/cues/gfx_cues_v1_chNN.md` y `gfx_cues_v2_chNN.md`;
  - tablas: `GUION_v1_v2.md` (guion) y `SIM_v1_v2.md` (director);
  - reporte: `lab/hyperframes/f5/F5_REPORT.md` (revisor íntegro por sección: CUMPLE CON OBSERVACIONES);
  - decisiones: `lab/hyperframes/f5/DECISIONES_F5.md` (J0–J44);
  - copia v2 del research: `data/scripts/_steps/ba6c3cac-f5v2/` y `data/scripts/ba6c3cac-f5v2.json` (fuera de git; copia versionada en `lab/hyperframes/f5/v2/`);
  - simulaciones: `output/ba6c3cac-f5v2/_fase2b_work/` (v2) y `output/ba6c3cac-a091-41c0-8dad-afd2f4364747/_fase2b_work_f5sim_v1/` (v1).
  - Se reproduce todo con `lab/hyperframes/f5/correr_f5_orleans.py --etapa todo`.
- **Resultado:**
  - guion: densidad 1.36→3.29, adjetivos 6.2→2.9, datos en más de 2 caps 2→0, Gusman en 6 caps, 41 datos del pool (v1: 12);
  - simulación: recortes del pool 0→7 (**0 con fuente**), «repite» del crítico 12→4, reloj en 3 caps.
- **Abierto:** cliffhanger estricto 4 de 6; contradicción 6,375/6,500 sin contar; año del kicker desde `fecha` no literal en los datos (D72); umbral de adjetivos 3.6 a validar; nombres nuevos sin revisión fonética para TTS.

### Decisiones F5 (J1–J44) en 10 líneas
1. **Pool (J1–J7).** Una llamada Flash por bloque, sin tope. Todo literal del bloque (lo que no, se descarta). La fuente sale solo de las [FUENTES CONSULTADAS] del bloque y si el ítem la nombra; si no, null. Limpieza y merge entre bloques con IDs del código. Geocodificación anclada a la ciudad principal (≤ 400 km; siglas no). Caché de la respuesta cruda.
2. **Skeleton (J8–J13).** `_evidence_plan` con ≥ 3 datos nuevos y ≤ 1 puente por cap, cronología en orden en los caps 2–6, antagonista obligatorio y cliffhanger = ID del dato del cap siguiente. Lo que Flash erra se repara en código y queda en `_evidence_repairs`. Sin pool, el prompt es idéntico al de antes.
3. **Juez (J14–J19).** «Dato usado» = anchor literal. Las cifras valen en dígitos o en palabras (`num_es.py`). Un evento cuenta con su fecha más una palabra de contenido en la misma oración. Densidad y repetición cuentan solo datos duros. El antagonista exigido es el principal.
4. **Adjetivos (J17–J18).** Heurística sin etiquetador. El umbral se recalibró de 8 a 3.6: la heurística mide v1 en 6.2 contra el 14 del analista.
5. **Narrador (J20–J23, J43).** Datos asignados en el prompt (usa 3–6) y reglas A–G validadas por `cap_problems`. Si falla, reintenta (3 intentos). Si sigue fallando solo por reglas del pool, se acepta y queda en `_f5_violations`. Un último intento que rompe el largo cede ante uno anterior que solo fallaba el pool. Citas con el autor dentro de la oración.
6. **Normalizer (J24–J26).** `normalize_pool_forms` determinista, después de los spans del auditor. Siglas ACLU, HRW, DOJ y FEMA. `persist_dict=False` para no tocar el diccionario global en las pruebas.
7. **Pantalla (J28–J31).** Todo detrás de `if pool` (los guiones viejos salen igual). El candado acepta el pool. Recortes y datos desde el pool del cap ±1, nunca desde la narración. Kicker = fuente → fecha → sin recorte (sin el año de la voz). Dedupe por `pool_id` entre caps.
8. **Ícono, pregunta y reloj (J32–J36).** El ícono sale del tema del dato, nunca de la voz (cifras de personas sin ícono; espiral y rayo pendientes). La pregunta sale del cliffhanger (respaldo: F4c). El reloj sale de la cronología solo si el cap avanza de fecha. Los lugares con lat/lon quedan para el mapa de F6.
9. **Prueba (J37–J42).** `plan_only` sin render. Topic de copia `ba6c3cac-f5v2` con los `verified_facts` de v1 idénticos. Fotos de v1 como proxy: palabras de v2 en la duración de v1 y escenas en los mismos cortes, con anchors sintéticos. `record_proposals` apagado en las simulaciones. md5 de los archivos globales iguales antes y después.
10. **Proceso (J0, J27, J44).** Rama desde F4e porque F4f no existe. Los heredocs de Git Bash convierten `\b` en 0x08 (origen de los bugs de F4c y F4d): los parches con barras van por Write y se chequean bytes de control. §1.6 no se hizo.

## F4e — Marca de esquina apagada, crítico visual (6b), hoja de contactos — ESPERANDO A OMAR
- Commit F4e (último). Leer `lab/hyperframes/f4e/RESUMEN_F4e.md` (revisor íntegro: CUMPLE CON OBSERVACIONES), `DECISIONES_F4e.md` (I1–I14), `TABLA_critico.md`, `hoja_contactos_ch02/ch05.jpg`.
- `script_engine/gfx_critic.py`: Gemini juzga cada bloque (cuadro real + voz + bloque en texto) → suma/repite/estorba; solo pasan los «suma». Token `visual_critic`. Few-shot `gfx_profiles/misterio_critico_fewshot.json`. ch02 6/7, ch05 6/8.
- Abierto: el crítico no ve el bloque dibujado → pasaron el recorte truncado en la tarjeta (ch02 1:00.7, I12) y la caja del zoom fuera de los pies (ch02 1:17.9, I13).
- Marca: `channel_bug.corner.enabled=false` (queda el cierre). md5 sin `--gfx` = `38e5ba14…` ✔. Tests: 316 verdes. Respaldo F4d: `_fase2b_work/_bak_f4e_pre`.

## F4d — Pico con preferencia, recortes por cláusula, marca +1 px — superado por F4e
- Commit F4d (último). Leer `lab/hyperframes/f4d/RESUMEN_F4d.md` (revisor íntegro: CUMPLE CON OBSERVACIONES), `DECISIONES_F4d.md` (H1–H11), `TABLA_antes_despues.md`.
- ch02 vuelve al nivel de agua 4.6 m con PUTREFACTA de palabra del pico; los recortes recuperan la fecha y «aguas residuales». ch05: «cadáveres flotando…» con kicker «1 de septiembre» (HRW NO: el research no le atribuye ese fact, H8).
- Marca `corner_dilate_px: 1`; caché del PNG ahora distingue el engrosado (H10). `\b` de `gfx_icons/__init__.py:70` arreglado.
- md5 sin `--gfx` = `38e5ba14…` ✔. Tests: 311 verdes. Respaldo del estado F4c: `_fase2b_work/_bak_f4d_pre`.

## F4c — Doctrina del director + marca sin pixelado — superado por F4d
- Commits: `c05ce25` A (reglas R1–R8 del `ANALISIS_director_trace_2026-10-20.md`; R9 saltada por Omar) · `0acff03` B (marca de la esquina a 4× + lanczos) · resumen (último commit).
- Leer `lab/hyperframes/f4c/RESUMEN_F4c.md` (veredicto del revisor íntegro: CUMPLE CON OBSERVACIONES), `DECISIONES_F4c.md` (G1–G23), `TABLA_antes_despues.md`, `capturas/` (recortes 1:1 de la marca).
- Solo `--only-cap ch02/ch05` (3 corridas; la que vale es `corrida/`). Candado sin `--gfx`: md5 `38e5ba14…` ✔. Tests: 305 verdes.
- Abierto para Omar: (1) el pico se movió por variación de Flash (ch02 sin nivel de agua; intensidad en caché); (2) Flash elige recortes flojos aunque cumplen R6 (arreglo propuesto G22: elegir solo entre las 3–4 mejores); (3) marca más suave pero maciza con +2 px (probar `corner_dilate_px: 1`); (4) bug 0x08 sin tocar en `gfx_icons/__init__.py:70` (G17); (5) léxico: caos/nadie/nunca a peso 1 (G9).
- Tokens nuevos del motor (OFF por default, misterio ON): `peak_word`, `doc_clippings`, `callout_no_repeat`, `question_rubric`. Reservas activas con capa `minima` + SFX propio (brasa, rumor, zumbido, viento, vacio).
- Respaldos: `_fase2b_work/_bak_f4c_pre` (planes/capas F4b de ch02/ch05), `_bak_f4c_v1`, `_bak_f4c_v2`.

## F4b — Marca + director inteligente (HANDOFF_F4b) — ESPERANDO A OMAR (merge)
- Commits: `1762916` §1 intensidad · `f1af5de` §2 fragmentos · `93064c8` §3 zoom foto-primero + §4 íconos gratis + código de la marca (apagada) · §5 render completo (último commit).
- Leer `lab/hyperframes/f4b/RESUMEN_F4b.md`, `F4b_REPORT.md`, `DECISIONES_F4b.md` (E1–E42).
- Marca: candidata 3 elegida por Omar, cosida en `d8d87c6` (llama en el farol, esquina 6 % / 0.7 / +2 px / halo; cierre 2.5 s + negro). Final 715.6 s. Posible ajuste: `corner_dilate_px` 1 si la esquina se ve maciza (re-cosido + re-ensamble ~13 min, sin HyperFrames).
- Falta: merge F4+F4b a `main` con el OK de Omar.
- Regla de Omar: Firefox cerrado en TODO render, siempre (memoria `firefox-cerrado-en-todo-render`).
- game-icons se baja con `script_engine/gfx_icons/fetch_game_icons.sh` (fuera de git).

## F4 — Identidad en producción (HANDOFF_F4, modo nocturno) — ESPERANDO A OMAR (PARADA 2)
- Commits: `4f05f66` §1 (identidad de Omar en el perfil + pregunta concreta) · `f5c54bd` §2 (`gfx_style`: el director aplica la identidad; ch05 PARADA 1) · `b8e6c8e` §3 (el render SÍ escala el video; zoom sin congelado) · `321c489` §4 (render completo, AB_f4).
- Leer `lab/hyperframes/f4/RESUMEN_NOCHE_F4.md` (3 preguntas para Omar), `F4_REPORT.md`, `DECISIONES_F4.md` (D1–D22).
- Falta: §5 merge a `main` + docs (REPO_MAP, ARCHITECTURE, DOC_MAESTRO v1.2, CLAUDE.md) **solo con OK de Omar**; incremental sin medir; pregunta de ch06 abstracta («indiferencia»).
- Final: `output/ba6c3cac…/…_final_gfx.mp4` 712.2 s · `AB_…_f4.mp4`. Respaldos F3/F2b en `_fase2b_work/_bak_f4_pre*/`.

## F3 — Laboratorio de identidad: qué quedó hecho (commits en orden)
- **§A `0902908`** servidor `gfx_lab_server.py` (:8765) + historia (Whisper + audio + fotos) + preview real (`write_project` + player/runtime pineados).
- **§B `9d65b49`** `catalogo.json` (43 piezas), `sugerencias_ch02.json` (borrador de 18), miniaturas CSS, tokens en vivo + candado literal en el preview.
- **§C `04a6025`** ✔/✖, deshacer, resumen en vivo, **Guardar identidad** (`script_engine/gfx_identity.py`).
- **§F `edf5221` / §F2 `2bdfd44`** pantalla tramo por tramo: Probar = un objeto solo sobre la foto fija; "Ver este tramo con todo" y "Ver capítulo completo" solo con lo aprobado; movimiento sobre el PNG (alejar/quieta nuevos en el templater); solo formas que se ven. Vista vieja en `?modo=experto`.
- **Mood agua `d4ed4e5`** sin cáusticas: sombra que sube 1 s / se mantiene / baja + bordes; los otros 3 moods revisados.
- **Íconos + pregunta `beb2b8f`** ícono siempre en bloque (L 360 px + palabra al lado + fuente, zona oscura, sombra + grano), "con ícono" en dato/recorte, ícono propuesto por palabra literal + selector de los 12; **pregunta de cierre automática** (`script_engine/gfx_question.py`, Flash + validador, 2 reintentos, `generated: true`) con **pausa real de 3 s** + drone en fase2b y en el lab.
- **Pico `9d36be7`** (`script_engine/gfx_peak.py`): pico = frase con más palabras de peso 3, UN bloque grande y ±5 s libres; **nivel de agua** (4.6 m → 60 %, cifra literal, 1 por video); **reloj** «29 AGO · 2005» en la esquina libre; zoom de evidencia **+ latido**; **corte a negro 1 s**; ch02 cargado por default; fix del zoom (HyperFrames no escala `<video>` → cuadro congelado); candado 409 entre pestañas del lab.
- Render ch02 `--gfx` actual: **101.6 s** (97.6 voz + 3 pregunta + 1 negro), respaldado en `_fase2b_work/_bak_f3_pregunta/ch02_segment_only.gfx_pico.mp4`.

## Pendiente
- **Malla del mood agua:** corregida en `d4ed4e5` (sin `repeating-*gradient`, test que lo impide), **falta que Omar la confirme a ojo** en el tramo 5. Aparte, muerte se ve "lavado" (desaturación, no patrón): decide Omar.
- **Pregunta más concreta:** la generada para ch02 («¿Cómo el encierro transformó la oscuridad moral de los prisioneros?») cumple el contrato pero es abstracta; ajustar el prompt de `gfx_question` para que apunte a un hecho concreto del cap siguiente. La pregunta escrita a mano por Omar («Quien fue el culpable?») no pasa por el validador.
- **Video completo con pausas:** no se renderizó el video entero con las pausas de cierre (concat + música por cap con `extra_sec`); solo ch02 y tests.
- **Golpe de zoom sobre video:** punch-in, empuje del mood muerte y "corte + golpe" no escalan el clip de video en el render (mismo límite de HyperFrames que el zoom). Se propuso como sesión aparte, pero **no arrancó**: Omar tiene que confiar el repositorio en Claude Desktop (botón "Trust repository" en esa sesión).
- ~~Perfil guardado por Omar SIN commitear~~ → resuelto en F4 §1 (`4f05f66`, D1–D4). Texto original: `gfx_profiles/misterio.json` modificado (acento `#c2302f`, golpe 1.015, `anim_figure` stamp, sello 84 px, `blocks.chapter_question.enabled = true`, clave `identity` con 10 marcas). Con ese perfil fallan 8 tests que fijan la calibración vieja, y `chapter_question.enabled` vuelve a prender la regla de pregunta del director (choca con C56: la pregunta la genera `gfx_question`). Decidir: aceptar los valores y actualizar los tests, y apagar ese bloque.
- §D (plantillas nuevas, Render desde el lab, regenerar ícono) y §E (director que consume identidad + golden; probar en ch05) del HANDOFF_F3 siguen sin hacer.

## Dónde está todo (F3)
- **Identidad guardada por Omar (2026-10-20 01:20):** perfil `gfx_profiles/misterio.json` (sin commitear; respaldo del anterior en `gfx_profiles/misterio.json.bak_f3_20261020_012038`), plan dorado `gfx_profiles/misterio_golden_ch02.json`, resumen `lab/identidad/IDENTIDAD_misterio.md` (ambos sin trackear).
- Sesión de Omar en el lab: `lab/identidad/plan_ch02_lab.json` (+ respaldos `.omar_2231`, `.omar_0004`, `.omar_antes_pico`); no se commitean.
- Pregunta de cierre en caché: `output/…/_fase2b_work/gfx_question_ch02.json`; pausa por cap: `gfx_pause_<cap>.json`.
- Docs: `lab/hyperframes/f3/` → `HANDOFF_F3_laboratorio_identidad.md`, `HANDOFF_F3b_lab_foto_por_foto.md`, `F3_REPORT.md` (veredictos íntegros del revisor por sección), `DECISIONES_F3.md` (C0–C67), `capturas/` (iconos, moods, pico), logs de render y md5.
- Código F3: `gfx_lab_server.py`, `lab/identidad/` (`index.html` + `lab_foto.js`/`.css` = tramo por tramo, experto.html = vista vieja, lab.js = núcleo), `script_engine/gfx_identity.py`, `gfx_question.py`, `gfx_peak.py`.

## Decisiones F3 (C1–C67) en 10 líneas
1. El lab usa `http.server`, el player/runtime pineados y `write_project`: el preview es el templater real, nunca una copia; proyectos propios (`gfx_lab_ch02`, `gfx_lab_ch02_solo`) y base con cola congelada de 4.5 s (C1–C11, C43, C58).
2. Todo cambio del lab pasa por `mutate()` (deshacer, autoguardado) y por el candado literal; la única excepción es la pregunta (manual o `generated`) (C14, C19, C55).
3. Ninguna forma que no se vea: lo que el templater no dibuja no aparece en la pantalla tramo por tramo (C12, C47).
4. Guardar identidad valida el perfil con `load_profile` antes de reemplazarlo y deja respaldo; la identidad vive en la clave `identity` del perfil (C22–C30).
5. Unidad = tramo; Probar = un objeto solo sobre la foto fija; "con todo" = solo lo aprobado (no marcado no aparece) (C42–C48).
6. Movimiento sobre el PNG con "movimiento seguro" (`push/pan/pull/static`); 3D = clip DepthFlow; salida por tramo vía `transitions` (C44–C45).
7. Ícono siempre en bloque L + palabra + fuente en la banda oscura del lado tranquilo; 12 íconos probables en cualquier palabra en el lab (C50–C53).
8. Pregunta generada por Flash con validador del contrato; pausa real (base congelado + `apad` de fase2b + música por cap) solo con `--gfx`; md5 sin gfx intacto (C54–C57).
9. Pico determinista (`gfx_peak`): un bloque grande y ±5 s libres; nivel de agua, reloj, zoom con latido y corte a negro por tokens del perfil (`peak_blocks`, `black_hold_sec`) (C60–C66).
10. Riesgos conocidos: HyperFrames no escala `<video>` (zoom arreglado con cuadro congelado, golpe pendiente), dos pestañas del lab se pisaban (candado 409), heurísticas sin etiquetador (sustantivos, movimiento por prompt) (C36, C54, C64, C67).

## Historia: F2b (HANDOFF_F2b_director_v2.md) — cerrado, en rama f2-gfx-director
- §1 `aec3a4a`, §2 `046c4c9`, PARADA 1 `2879665`, §3 `f3fd3db`, §4 `6819ee5`, pre-merge `11a9d1f`, v2 + re-ensamble `31c671c`. Revisores: CUMPLE CON OBSERVACIONES. Docs en `lab/hyperframes/f2b/` (`F2b_REPORT.md`, `DECISIONES_F2b.md`).
- Esperando a Omar desde F2b: mirar `AB_…_f2b.mp4`, decidir el criterio de PSNR de §4 (B33), merge F1+F2+F2b a `main` solo con OK explícito. Deuda: recortes repetidos entre caps.

## Reglas que no se negocian
- Responder en español (rioplatense). Comentarios en español, identificadores en inglés.
- Todo reporte a Omar pasa antes por `revisor-handoff` (subagente, sonnet) y su veredicto va **íntegro**.
- Candado literal en todo texto en pantalla. Sin `--gfx`, fase2b byte-idéntico (chequeo: md5 de ch02 `--only-cap` = `38e5ba14…`).
- Sin shaders, sin rembg/inpaint. Validar con `--only-cap ch02` + snapshots; renders completos solo cuando se piden.
- Commits F3: `feat(gfx-f3-lab): <sección>` / `fix(gfx-f3-lab): …`, trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`, `git add` por ruta (`diag_234_cap4.py` NO es nuestro; los `plan_ch02_lab*.json` tampoco se commitean).
- Python con `PYTHONIOENCODING=utf-8`. Los heredocs largos de bash fallan (y rompen con acentos): escribir los scripts con Write en el scratchpad.
- `--reuse-visuals` reusa `chXX_gfx.mp4`: moverlo a `_fase2b_work/_bak_*` antes de re-renderizar un cap.
- El lab y otra pestaña pueden pisarse: recargar la página después de cambiar el estado por fuera (el servidor responde 409 a guardados viejos).

## Dónde está todo (general)
- Handoffs: `lab/hyperframes/_handoff_adjuntos/` (F2, nocturno, DOC_MAESTRO) y `lab/hyperframes/f3/` (F3, F3b).
- Código gfx: `gfx_config.py` (motor), `gfx_profiles/*.json` (perfil), `script_engine/gfx_*.py`, `script_engine/gfx_templates/`, `script_engine/sfx/` (`make_sfx.py`, incluye `drone_subida.wav`).
- Salidas: `output/ba6c3cac…/` → `_final.mp4` (A, sin gfx), `_final_gfx.mp4` (B-F2), AB; respaldos en `_fase2b_work/_bak_*`.
- Transcripciones respaldadas antes de cada compactación: `lab/_transcripts/` (hook PreCompact).

## Comandos de uso diario
- Tests: `PYTHONIOENCODING=utf-8 python -m pytest test_module_gfx_*.py test_module_fase2b_reassemble.py test_module_fase2b_hwencode.py test_module_concat_windowed.py test_module_transition_timeout.py -q` (243 verdes con el perfil del commit).
- Lab: `PYTHONIOENCODING=utf-8 python gfx_lab_server.py` → http://localhost:8765 (`?tramo=N` abre en un tramo; `?modo=experto` = vista vieja).
- Un cap: `python fase2b.py <id> --reuse-visuals --gfx --gfx-quality looks --only-cap ch02` (+ `--gfx-debug` para el overlay).
- Video completo: `python fase2b.py <id> --reuse-visuals --keep-segments --gfx --gfx-sparse`.
