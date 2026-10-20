# ESTADO_SESION — dónde estamos (leer ANTES de programar)

Última actualización: 2026-10-20 19:40 (F4c commiteado; espera a Omar) · CC lo actualiza en cada hito (commit, reporte, decisión de Omar).

## Proyecto activo
- Repo: `C:\CLAUDE_PROJECTS\automatization_videos` · rama **`f3-lab-identidad`** (desde `31c671c`, tip de `f2-gfx-director`). Último commit: F4b §5 (ver `git log`); F4 cerró en `56085d1`.
- `main` = `43f528a` (NO tocar sin OK explícito de Omar). **F2b NO se mergeó** (decisión de Omar 2026-10-19): sigue en `f2-gfx-director` @ `31c671c`; F3 se apoya encima.
- Video de prueba: Orleans `ba6c3cac-a091-41c0-8dad-afd2f4364747` (7 caps; ch02 = cap de calibración, ch05 el segundo).
- Candados vigentes: md5 sin `--gfx` de ch02 `--only-cap` = `38e5ba14…` (último en `lab/hyperframes/f4b/onlycap_ch02_nogfx_f4b.log`); 305 tests verdes (F4c).

## F4c — Doctrina del director + marca sin pixelado — ESPERANDO A OMAR
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
