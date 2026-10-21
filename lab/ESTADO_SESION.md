# ESTADO_SESION — dónde estamos (leer ANTES de programar)

Última actualización: 2026-10-21 (F5d terminado, PARADA para el analista; después: producción de Orleans v2) · CC lo actualiza en cada hito (commit, reporte, decisión de Omar).

## Proyecto activo
- Repo: `C:\CLAUDE_PROJECTS\automatization_videos` · rama activa **`f5-guion-v2`**, que sale de `39e37ac` (F4e, tip de `f3-lab-identidad`; F4f no existe). Último commit: F5d (`git log -1`), sobre `c55ca56` (F5c).
- Cadena de ramas sin mergear: `f2-gfx-director` (F2b @ `31c671c`) → `f3-lab-identidad` (F3–F4e @ `39e37ac`) → `f5-guion-v2` (F5).
- `main` = `43f528a`. NO se toca sin OK explícito de Omar.
- Video de prueba: Orleans `ba6c3cac-a091-41c0-8dad-afd2f4364747` (7 caps; ch02 es el cap de calibración, ch05 el segundo). Copia del research para F5: **`ba6c3cac-f5v2`**.
- Candados vigentes:
  - md5 de ch02 `--only-cap` sin `--gfx` = `38e5ba14…` (último: `lab/hyperframes/f4e/corrida/onlycap_ch02_nogfx_f4e.log`);
  - 364 tests verdes en las suites de guion y gfx. Las 3 fallas de `test_module_01b_pauses.py` son previas a F5.

## F5d — Último ajuste antes de producción — PARADA: valida el analista; con su OK, producción completa de Orleans v2
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
