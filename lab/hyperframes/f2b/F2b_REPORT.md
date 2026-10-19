# F2b_REPORT — Director v2 (énfasis, íconos, recortes de verdad) + concat sin re-encode

Rama `f2-gfx-director` (base `0cc1997`). `main` intacta. Decisiones: `DECISIONES_F2b.md`.
Este reporte se completa sección por sección; los números finales (recortes, densidad, tiempos, PSNR, Gemini) van al cierre, después del render completo.

## §1 — Correcciones al director (v1 → v1.5)

- 1.1 Titular determinista: el LLM elige solo `fact_idx` + `scene_idx`; `build_headline` arma ≤ 8 palabras literales (la cláusula con la cifra, si la hay) y `build_kicker` pone fuente o año.
- 1.2 Zoom guiado por narración: el LLM marca la frase ancla (`anchor_word_idx` + `anchor_len`, dentro de la escena). Visión busca **esa** frase. Sin box o con confianza < 0.7 → sin zoom.
- 1.3 `chapter_question` OFF en el perfil. **Deuda de guion:** reactivarla cuando m01b emita `cliffhanger` por cap.
- 1.4 Densidad: máximo 18 s sin bloque (antes 35).
- 1.5 Router: visión solo sobre imágenes con persona en el prompt (40/81 en Orleans; 29 sin veredicto previo).
- 1.6 Grano 0, viñeta 0.15 (revierte D21).
- Candado sin `--gfx`: md5 de ch02 `--only-cap` = `38e5ba14e3d24fd20f9297c9e1dfee24` ✔ (log `onlycap_ch02_nogfx_s1.log`).
- Tests: 97 verdes.

### Veredicto revisor-handoff §1 (íntegro)

```
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1.1 | Titular determinista: el LLM manda fact_idx+scene_idx, el validador arma headline (≤8 palabras, cláusula con cifra) y kicker (fuente/año) | OK | gfx_director.py build_headline/build_kicker (~l.326-400); validate_plan l.485-489 ignora headline/kicker del LLM; schema archive_clippings solo pide fact_idx/scene_idx (l.244). Probado a mano: "Partes de Nueva Orleans quedaron bajo 15 pies". Test test_titular_lo_arma_el_validador |
| 1.1b | Objetivo 1–2 recortes por cap | NO VERIFICABLE | Hace falta el render de ch02/Orleans (cues/reporte). Es criterio de resultado, no de código |
| 1.2 | Zoom guiado por frase ancla; box de visión o null; sin box → sin zoom; umbral de confianza explícito | OK | zoom_anchor, _ZOOM_SYSTEM/judge_zoom_box(image, anchor), apply_zoom_vision (conf < zoom_conf_min=0.7 → sin zoom); gfx_config.py:225, misterio.json; test_zoom_sin_ancla_en_su_escena_no_va |
| 1.3 | chapter_question OFF por default en el perfil, el código queda | OK | misterio.json enabled=false; max_per_cap('chapter_question')=0 (corrido); _QUESTION_RULE condicional; la deuda "m01b cliffhanger" está en B8 (falta mencionarla en el reporte final, pendiente) |
| 1.4 | Intervalo máximo 18 s (antes 35); relleno: énfasis de palabra, callout de fact, punch_in | PARCIAL | interrupt_max_sec=18 (corrido: 18.0) y min 12. El orden de relleno queda callout→punch_in; el énfasis de palabra depende de §2, que aún no existe (B9 lo declara; sin tests nuevos de densidad) |
| 1.5 | Visión para retratos solo sobre imágenes con persona/rostro/retrato/manos/cuerpo; alimenta router (high si retrato) | OK | depth_probe.portrait_candidates (l.~193-210) + fase2b.py:2093-2119 (solo candidatos sin veredicto previo, cacheado en zoom_verdicts.json); alto = cara_closeup sin cambios; test en test_module_gfx_router.py (+10 líneas) |
| 1.6 | Grano 0, viñeta 0.15, quitar desviación D21 | OK | misterio.json grain 0.0 / vignette 0.15; gfx_rules cargado: 0.0/0.15 (corrido); gfx_layer.py:260 no genera textura si grain=0; B11 anota la reversión de D21. El default en código (gfx_config.py:282) sigue en 0.15, lo pisa el perfil |
| 6a | Tests verdes | OK | pytest gfx_* + reassemble + hwencode: 97 passed in 14.61s |
| 6b | Lock literal | OK | Headline se re-chequea con _literal_in (build_headline devuelve "" si no es literal) y sigue pasando por script_engine.gfx_literal_lock en gfx_layer.py. El ancla del zoom son palabras literales de la voz |
| 6c | Ningún texto/ícono inventado por el LLM | OK | El LLM ya no escribe headline/kicker; solo índices. Íconos no existen aún (§3) |
| 6d | Sin --gfx segmentos byte-idénticos | NO VERIFICABLE | Depende del md5 del render en curso que corre CC. Por diff: fase2b.py solo cambia _route_safe (ruta con gfx), así que no hay riesgo estático evidente |

Fuera de alcance: ninguno. Hay 12 archivos tocados, todos los declarados (diag_234_cap4.py excluido por indicación); lab/hyperframes/f2b/ existe y no está vacío (DECISIONES_F2b.md y un .log). Sin commits.

Riesgos que el contrato no cubre: (1) fase2b.py:2112 envuelve la visión nueva en un except genérico, así que una falla de Gemini se degrada en silencio a veredictos cacheados (queda un print). (2) El zoom ahora depende de que el LLM acierte anchor_word_idx dentro de ±1 s de la escena. Si falla más seguido de lo esperado, el zoom desaparece (conservador, pero baja la densidad). (3) El filtro de retratos usa regex en inglés/español sobre el prompt. Términos como "figure" o "silhouette" pueden disparar llamadas de visión de más (29 en Orleans, según B10), con costo de Gemini acotado.
```

Respuesta de CC a las observaciones: 1.4 se completa en §2 (el énfasis de palabra entra primero en el orden de relleno). 6d verificado después del veredicto: md5 `38e5ba14…` ✔.

## §2 — Léxico de moods + énfasis de palabra

- `gfx_profiles/misterio.json` → `moods`: 4 categorías activas (veneno_enfermedad 54 disparadores, agua 39, muerte 33, oscuridad_encierro 29) y 5 de reserva inactivas.
- `keyword_emphasis`: se detecta por regex sobre la narración, sin LLM. Por cap entran primero las 3 palabras más raras; el relleno de huecos suma más, hasta 5. Máximo 1 por frase y ≥ 20 s entre moods de la misma categoría. Cada una dispara su capa de mood (CSS, 2.5 s), el sello rojo con la palabra literal y el SFX `tic_sordo.wav`.
- Orden de relleno de §1.4 completo: énfasis → callout → punch_in.
- Render de ch02 en looks (`--only-cap`):
  - **2 recortes** (antes 0): «El huracán Katrina tocó tierra» con kicker 2005, y «Los prisioneros quedaron atrapados durante días en celdas».
  - 3 énfasis: diques/agua, oscuro y encierro/oscuridad.
  - 0 huecos > 18 s y lint con 0 errores.
  - Sin zoom: el LLM no propuso ninguno.
  - Render: 283 s; total del cap: 6 min 10 s.
- Detalle: al primer intento `--reuse-visuals` reusó el `ch02_gfx.mp4` de F2 y no rerenderizó. El viejo quedó respaldado en `_fase2b_work/_bak_f2_pre_f2b/`. **Para el render completo de §4 hay que mover los `chXX_gfx.mp4` de F2 antes de correrlo.**
- Entregables: `gfx_review_ch02.html` (página de revisión), `gfx_cues_ch02_s2.md`, `gfx_plan_ch02_s2.resolved.json` y `tira_s2_enfasis_ch02.jpg`.
- Límite: en ch02 solo aparecen las capas agua y oscuridad. Veneno y muerte están cubiertas por tests (templater y lock); su evidencia visual llega con el render completo.

### Veredicto revisor-handoff §2 (íntegro)

```
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | `moods` en misterio.json: 4 activas, ≥25 disparadores, preset de capa | OK | Conteo por script: veneno_enfermedad 54, agua 39, muerte 33, oscuridad_encierro 29. gfx_config.py valida capa y mínimo 25 en `load_profile` (+ test) |
| 2 | Reserva inactiva en el JSON (fuego, caos_gritos, radiacion_quimico, frio_abandono, silencio) | OK | misterio.json: las 5 con `active:false` y `layer:null` |
| 3 | 4 capas CSS (veneno, agua, muerte, oscuridad), 1–3 s, intensidad baja | OK | gfx_project.py `mood_layer`: las 4 ramas con duración de 2.5 s (`mood_dur`). Hay capa de bloque y de render para el sello y los moods |
| 4 | Detección por regex, sin LLM; literal por construcción | OK | gfx_director.py `emphasis_candidates`/`place_emphasis`. `llm_decides=False` en gfx_config.py. Decisión B12 |
| 5 | 3–5 palabras por cap, más raras si hay más de 5 | OK | `emphasis_base_per_cap=3`, `max_per_cap=5`; orden por rareza (frecuencia en la narración completa) |
| 6 | Máx 1 por frase, ≥20 s entre moods de la misma categoría | OK | `place_emphasis` (sid, `emphasis_same_cat_gap_sec`). test_module_gfx_emphasis.py: `test_maximo_uno_por_frase…` y `test_misma_categoria_separada_20_s` |
| 7 | Sello rojo con la palabra pasa por el lock literal | OK | gfx_literal_lock.py: sello fuera si la palabra no es literal. `test_lock_y_cues_y_templater` |
| 8 | SFX tic sordo asociado | OK | tic_sordo.wav existe (21 KB), `sfx.keyword_emphasis` en el perfil, `sfx_events` lo marca. `make_sfx.py` gana `only=` y deja los demás WAV intactos |
| 9 | §1.4 orden de relleno: énfasis, callout, punch_in | OK | gfx_director.py `fill_gaps`: énfasis primero, luego callout. Test `test_resolve_pone_enfasis_y_rellena_hueco_primero_con_enfasis`. Salvedad: la nota B9 del DECISIONES dice "callout → punch_in hasta que §2…" y no se actualizó, aunque B12–B19 lo cubren |
| 10 | Intervalo máximo 18 s y gap_warning del reporte | OK | gfx_review.py usa `interrupt_max_sec`. Cues de ch02: "gap_warning (> 18 s) ninguno" |
| 11 | Íconos por categoría quedan para §3 | OK | `icon:null` en el léxico y `emphasis_without_icon()`. Decisión B19. §3 sin hacer no es falla |
| 12 | Evidencia de render real en ch02 con looks | OK | onlycap_ch02_s2_looks.log, gfx_cues_ch02_s2.md (3 énfasis: diques/agua, oscuro y encierro/oscuridad), resolved.json, tira_s2…jpg (114 KB), gfx_review_ch02.html. Log del cap: "lint: 0 errores, 8 warnings" |
| 13 | Tests verdes | OK | Corrí pytest con el comando indicado: 106 passed en 3.7 s |
| 14 | Sin `--gfx` byte-idéntico (no toca fase2b.py) | OK | `git diff HEAD --stat -- fase2b.py script_engine/transition_applier.py` sin salida. Verificación estructural, no corrí un render comparado |
| 15 | Sin shaders, sin texto ni ícono inventado por el LLM | OK | Todo CSS/GSAP con blend modes. El texto sale solo de la narración de la voz y pasa por el lock |
| 16 | Decisiones B12–B19 anotadas | OK | DECISIONES_F2b.md (+8 líneas) |

Fuera de alcance: diag_234_cap4.py (M, ya declarado como ajeno, ignorado). lab/hyperframes/_handoff_adjuntos/HANDOFF_F1_gfx_layer.md aparece sin trackear. No me consta que sea de este trabajo. F2b_REPORT.md no está modificado. Todo lo demás está dentro del alcance de §2.

Observaciones (no bloquean):
- En el render de ch02 solo se ven las capas `agua` y `oscuridad`. `veneno` y `muerte` no tienen evidencia visual real; solo tests.
- "Muerte" hace un push-in (1.015) de la capa de video y desatura con blend `saturation`. Lo pide el handoff, pero es lo más cercano a tocar la imagen. B17 lo documenta.
- Hay 8 warnings de lint en el render. No miré cuáles son.

Riesgos que el contrato no cubre: el match exacto por token depende de listar a mano cada flexión, así que un tema fuera del léxico no dispara nada. El sello activado por defecto (B16) quedó como decisión visual de Omar en la PARADA 1.
```

Respuesta de CC: la nota B9 ya está actualizada. `HANDOFF_F1_gfx_layer.md` es un archivo previo, ajeno a F2b, y no se commitea.

## PARADA 1 — OK de Omar a ch02 con ajustes

- Pedido de Omar: OK a ch02 con el mood oscuridad **sin parpadeos** (token del perfil) y **peso 1–3 por palabra** en el léxico (cadáveres = 3, diques = 1), ordenando por peso y después por rareza.
- Hecho:
  - Token `mood_dark_flicker`: queda `false` en misterio y `true` en el motor.
  - `triggers` del léxico pasa a ser `{palabra: peso}`, y `load_profile` valida que los pesos estén entre 1 y 3.
  - La selección ordena por peso, después por rareza y después por tiempo.
  - Pesos por categoría: veneno 25/21/8 (3/2/1), agua 13/21/5, muerte 12/17/4 y oscuridad 14/10/5. El criterio está en B21.
- Tests: 107 verdes. No se volvió a renderizar ch02 (ya aprobado); el cambio se ve en el render completo.

### Veredicto revisor-handoff del ajuste (íntegro)

```
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Mood oscuridad sin parpadeos (solo bordes + haz de linterna) | OK | gfx_project.py:163-180 (el div `-fl` y los 2 tl.set solo se emiten si `mood_dark_flicker`); misterio.json:32 `mood_dark_flicker:false`; test_module_gfx_emphasis.py afirma `-beam` presente y `-fl` ausente |
| 2 | Es token del perfil | OK | gfx_config.py:295 (`GfxRules.mood_dark_flicker`, default True = motor/finanzas intactos); override en misterio.json; test_module_gfx_profiles.py añade el token al set de diffs esperado |
| 3 | Peso 1–3 por palabra (cadáveres=3, diques=1) | OK | misterio.json: muerte.cadáveres=3, agua.diques=1; test_peso_gana_a_la_rareza verifica ambos valores |
| 4 | Ordenar por peso y después por rareza | OK | gfx_director.py:~889 tupla `(-wt, rarity, t, ...)` ordenada; test: con "diques" más raro, gana "cadáveres" |
| 5 | Validación del esquema | OK | gfx_config.py:382 rechaza pesos fuera de 1–3 o triggers que no son dict; test con peso 5 |
| 6 | Tests verdes | OK | corrí la suite indicada: 107 passed |
| 7 | Léxico/texto literal, sin texto inventado por el LLM | OK | el sello sigue usando la palabra literal de la voz; solo cambia el orden y el campo `weight` en el JSON de salida |
| 8 | Documentado en DECISIONES (B20/B21) | OK | DECISIONES_F2b.md +2 filas (B20 flicker, B21 pesos) |
| 9 | Commit del ajuste | NO VERIFICABLE | el cambio sigue sin commitear (HEAD 046c4c9); el contrato pide commitearlo, queda pendiente o lo hace quien reporta |
| 10 | Sin --gfx byte-idéntico / ch02 visual | NO VERIFICABLE | no hubo render; falta un render/diff de ch02. Por código, sin --gfx no pasa por este camino |

Fuera de alcance: ninguno. Los 7 archivos modificados son exactamente los declarados; diag_234_cap4.py aparece modificado pero se ignoró según indicaste (1 línea, ajeno).

Observaciones:
- Los pesos (excepto cadáveres/diques) los asignó CC por criterio propio; está declarado en B21 y Omar puede corregirlos en el JSON. Las categorías inactivas quedan todas en peso 2 (plano).
- El campo nuevo `weight` en cada entrada de `emphasis` cambia el esquema de salida del director (lo tolera el código actual; ningún consumidor roto en los tests).

Riesgos que el contrato no cubre: (1) el perfil finanzas no define moods, así que nada rompe con el nuevo formato dict; cualquier perfil futuro con triggers en lista fallará en load_profile (a propósito). (2) La ausencia de parpadeo solo se probó con tests de HTML, no visualmente en ch02.
```
