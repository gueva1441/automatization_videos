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

## §3 — Íconos (hasta la PARADA 2; sin commit hasta que Omar elija)

- Set propio de 12 íconos × 3 tiradas con Flux.2 Pro (prompt base fijo y semillas 1441/1442/1443), vectorizados con potrace (`potracer`). Prompt, semilla y motor de cada candidato están en `gfx_profiles/icons/README.md` y `manifest.json`. Costo ≈ $1.08 (B22).
- Respaldo: Lucide local (12 SVG con licencia ISC), restilizado por código. Lista blanca de 12 claves: sin SVG aprobado no hay ícono.
- Bloques:
  - `icon_callout`: ícono más palabra en sello, hasta 3 por cap.
  - `icon_array`: filas de 10 figuras con las víctimas en rojo; solo para facts con la forma «A de los B ≤ 500». Orleans no tiene ninguno.
- Animaciones: `ink_bleed`, `engrave` y `stamp`, con salida "tinta que se seca".
- Tests: 114 verdes. La tira usa la misma composición HyperFrames que el templater: lint con 0 errores.
- Entregable: **`lab/hyperframes/f2b/tira_iconos_12.jpg`**. Omar elige por número (1a…12c); los rechazados van a una tirada más y, si siguen mal, a Lucide.
- Notas para elegir:
  - Los 3 relojes traen números o marcas (cuenta como texto).
  - El 9c (cruz) salió con dos barras blancas en los bordes.
  - El acento rojo es automático: en el candado cae bien (cerradura); en otros cae en un detalle arbitrario y se fija a mano después de elegir.

### Veredicto revisor-handoff §3 (íntegro)

```
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Set de 12 íconos de la lista (calavera, gota, llama, biohazard, reloj, candado, ojo tachado, balanza, cruz, persona, edificio en ruina, pregunta), 3 tiradas c/u | OK | `gfx_profiles/icons/candidates/` = 36 SVG; `icons_raw/` = 36 PNG; ICON_WHITELIST en `script_engine/gfx_icons/__init__.py:27` |
| 2 | Producción por t2i con prompt base fijo, mismo seed/estilo, potrace, limpieza de paths chicos | OK | `manifest.json` (flux-2-pro, seeds 1441/1442/1443, prompt base idéntico al contrato, turdsize 20). Se usó `potracer` en vez del binario (B23, declarado) |
| 3 | Registrar prompt/seed/motor por ícono en README | OK | `gfx_profiles/icons/README.md` (tabla de 36 candidatos con seed y paths) |
| 4 | Sin texto dentro del ícono / sin SVG a mano | PARCIAL | La tira lo delata: reloj 5a y 5c traen números y 5b agujas/marcas; la propia tira lo marca ("ojo: trae números (texto)"). Los 3 reloj quedan dudosos contra la regla "prohibido texto". Ningún SVG a mano (solo Lucide de respaldo) |
| 5 | Tira `tira_iconos_12.jpg`: 3 candidatos por ícono, fondo de ch02, fila 2 con `engrave` a mitad | OK | Existe (678 KB). Vista con Read: 12 bloques, 3 candidatos arriba, 3 "a mitad" abajo, fondo de la cárcel inundada de ch02 |
| 6 | Calidad de la tira | PARCIAL | La cruz 9c salió defectuosa: dos barras blancas gigantes en los bordes (artefacto de trazado, no es un grabado válido). Varios acentos rojos son manchas arbitrarias (5b: gran mancha roja arriba; 10a/10c: pies rojos); el contrato pide "un solo detalle". B24 lo declara como regla automática |
| 7 | Respaldo Lucide local, lista blanca, nunca SVG inventado, sin ícono si nada aplica | OK | `gfx_profiles/icons/lucide/` 12 SVG + LICENSE (ISC, no MIT: declarado en B25). `icon_svg` solo acepta claves de lista blanca; no hay SVG aprobados aún, así que no sale ícono (`ls gfx_profiles/icons/*.svg` = vacío) |
| 8 | Bloques `icon_callout` (máx 3/cap) e `icon_array` (máx 1/cap, ≤500, relación total/afectados en facts) | OK | `gfx_config.py` (bloques + `icon_array_max=500`), `misterio.json`, `gfx_director.py` (`mark_icon_callouts`, `place_icon_array`); candado literal en `gfx_literal_lock.py` (label del array) |
| 9 | 3 animaciones (`ink_bleed` 0.7 s, `engrave` 0.8 s, `stamp`) + salida "tinta que se seca" + lint 0 errores | PARCIAL | Mapeadas en `misterio.json` y descritas en B28/B29; la tira usa el motor real (lint 0 errores, 4 warnings, según B29). No re-corrí el lint ni medí duraciones; la fila "a mitad" muestra `engrave` solo |
| 10 | Candados §6: lock literal, sin `--gfx` byte-idéntico, sin shaders, main intacta, tests verdes, ningún texto/ícono inventado | OK | `pytest test_module_gfx_*.py test_module_fase2b_*` → 114 passed; el diff no toca `fase2b.py`, `transition_applier.py` ni `main.py`; rama f2-gfx-director |
| 11 | Costo ≤ $1 | PARCIAL | ≈ $1.08 (8 % sobre el techo), declarado en B22. El cost_tracker lo asienta a $1.62 (tarifa interna) |
| 12 | §3 sin commitear hasta aprobación; parada en la tira | OK | Árbol de trabajo sin commit de §3; README dice "Elección de Omar: pendiente" |
| 13 | Decisiones registradas | OK | `DECISIONES_F2b.md` B22–B29 |

Fuera de alcance: ninguno (todo está en la lista de §3; `diag_234_cap4.py` y los `??` previos ignorados por instrucción).

Riesgos que el contrato no cubre: (a) los 3 candidatos de reloj tienen números o marcas de texto y la cruz 9c está rota, así que con la regla "rechazado = una tirada más, luego Lucide" el reloj y la cruz probablemente salgan por Lucide o repitan tirada. (b) Los acentos rojos automáticos pueden caer en un detalle arbitrario, y fijarlos a mano es trabajo extra. (c) No se verificó que el lint de HyperFrames y la duración de las animaciones se mantengan con íconos reales aprobados dentro de un video, porque aún no hay ninguno.
```

## PARADA 2 — elección de Omar y commit de §3

- Omar eligió **1b, 2a, 3a, 4a, 5b, 6a, 7a, 8b, 9b, 10b, 11b, 12a**. Pidió rojo solo donde significa algo: ojos de la calavera, cerradura y cruz.
- Cómo quedó el rojo:
  - Calavera: óvalos rojos detrás de la tinta (se ven por las cuencas).
  - Candado: la cerradura.
  - Cruz: un clavo rojo en el cruce (la cruz entera se leía como "Cruz Roja").
  - Los otros 9: sin rojo (B30).
- `script_engine/gfx_icons/approve.py` deja los 12 en `gfx_profiles/icons/<clave>.svg`.
- ch02 re-renderizado con los íconos aprobados (`tira_s3_iconos_en_ch02.jpg`, `gfx_cues_ch02_s3.md`): 3 `icon_callout` (candado en «oscuro» y «encierro», gota con `engrave` en «sumergidos»), lint con 0 errores.
- Los pesos se notan: «sumergidos» (peso 3) entró en lugar de «diques» (peso 1).
- Tests: 115 verdes.
- Commit de §3: entran el código, el perfil, los 12 aprobados, los 36 candidatos, Lucide, el manifest, el README, la tira y la evidencia. Quedan fuera de git `icons_raw/` (27 MB de PNG) y `tira_iconos_proj/` (se regeneran con `make_icons.py`).

### Veredicto revisor-handoff PARADA 2 (íntegro)

```
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Los 12 íconos son los elegidos (1b,2a,3a,4a,5b,6a,7a,8b,9b,10b,11b,12a) | OK | manifest.json "approved": 1b,2a,3a,4a,5b,6a,7a,8b,9b,10b,11b,12a, igual a CHOICE en approve.py:22. Los 12 SVG existen en gfx_profiles/icons/ (40 KB a 180 KB). |
| 2 | Acento rojo SOLO en calavera, candado y cruz | OK | grep de c8102e/ic-accent: 1 coincidencia en calavera.svg, candado.svg y cruz.svg, y 0 en los otros 9. manifest accent=true solo en esos 3. |
| 3 | Rojo "donde significa algo": ojos, cerradura, cruz | OK, con interpretación | Ojos: 2 elipses rojas detrás de la tinta (approve.py:42-44). Cerradura: acento automático del trace. Cruz: solo un clavo rojo r=6 en el cruce (cruz.svg:45), no la cruz entera. La tira muestra el candado con cerradura roja. La calavera y la cruz no aparecen en ch02, así que no las pude ver renderizadas en video. |
| 4 | Sin texto inventado | OK | Ningún `<text>` ni `<tspan>` en los 12 SVG. Los textos de la tira ("OSCURO", "SUMERGIDOS", "ENCIERRO") salen de la narración (gfx_cues_ch02_s3.md:11,13,26). |
| 5 | Lint 0 errores | OK | gfx_ch02.log: "lint: 0 errores, 11 warnings". |
| 6 | Tests verdes | OK | Corrí el comando indicado: 115 passed en 3.66 s. Existe test_set_aprobado_por_omar_parada_2 en test_module_gfx_icons.py. |
| 7 | Nunca ícono equivocado | PARCIAL | En ch02 hay 3 icon_callout: candado en "oscuro" y en "encierro", gota en "sumergidos". Son coherentes. Solo pude ver 3 cues en un capítulo; las otras 9 claves no se ejercitaron en video. |
| 8 | Dibujar a mano ≤ 15 min por ícono | OK | Solo hay 2 retoques manuales (ojos de la calavera y clavo de la cruz), ambos coordenadas en approve.py. |
| 9 | Decisión B30 documentada | OK | DECISIONES_F2b.md:37. |
| 10 | Entregables existen y no están vacíos | OK | tira_s3_iconos_en_ch02.jpg (79 KB), onlycap_ch02_s3_looks.log, gfx_cues_ch02_s3.md (45 líneas) y README.md en icons/. |

Fuera de alcance (para el commit de §3):
- script_engine/transition_applier.py (+160 líneas) y test_module_concat_windowed.py son de §4. No mezclarlos.
- F2b_REPORT.md (+41) y DECISIONES_F2b.md (+9) están modificados. Revisar que sus hunks sean solo de §3 antes de commitear.
- Untracked de §3 que conviene decidir si entran: icons_gen.log, icons_raw/, tira_fondo_ch02.jpg, tira_iconos_12.jpg, tira_iconos_proj/.
- gfx_profiles/icons/candidates/ y lucide/ ya existen: confirmar si van al commit o se ignoran.
- Los demás archivos modificados no son de §3: diag_234_cap4.py, gfx_config.py, misterio.json, gfx_director.py, gfx_literal_lock.py, gfx_project.py, gfx_sparse.py, test_module_gfx_config.py.

Riesgos que el contrato no cubre:
- Solo 3 de los 12 íconos se vieron en un video real (candado y gota). Reloj (5b, con marcas y números romanos) y cruz (clavo rojo) siguen sin verificación visual en cuadro.
- El video real tiene un warning de lint que no revisé (11 warnings).
```

Respuesta de CC al "fuera de alcance":
- `gfx_config.py`, `misterio.json`, `gfx_director.py`, `gfx_literal_lock.py`, `gfx_project.py`, `gfx_sparse.py` y `test_module_gfx_config.py` **sí son de §3**: los bloques `icon_callout` e `icon_array` y su cableado se revisaron en el veredicto §3 de arriba. §1, §2 y PARADA 1 ya estaban commiteados.
- `transition_applier.py` y `test_module_concat_windowed.py` (§4) quedan fuera de este commit.
- Los hunks de `F2b_REPORT.md` y `DECISIONES_F2b.md` son solo de §3 (B22–B30).

## §4 — Concat + música sin re-encode

- `transition_applier.concat_windowed`: cada segmento se parte por copia en sus keyframes y solo se re-encodea una ventana por frontera (xfade adentro, mismo encoder que los segmentos). Las piezas se pegan con `-c copy`, el audio va con `acrossfade` solo y al final se muxea.
- `fase2b._mix_music_audio_only`: el mismo grafo de música, pero solo sobre el audio. El padding inicial es un clip codificado aparte y el final es un remux con `-c copy`.
- Si algo falla, cae al camino clásico (con aviso en el log); `--legacy-concat` fuerza el camino viejo.
- Medición sobre los 7 segmentos reales de F2:
  - Concat en **62 s** (antes, ~15 min). Mismos frames que el final viejo (20 583 = 20 583).
  - PSNR del final nuevo contra el viejo: Y 44.8 / promedio 46.2 (sin ch04, que se rehízo después).
  - Contra la fuente (`seg_02`): el viejo da **Y 47.3** (pierde por su re-encode crf 18 y por el resampleo de croma del xfade); el nuevo da **Y 58.6** en un tramo con ventana y **∞** en el cuerpo (copia exacta). Detalle en `measure_concat_f2segs.json` y `measure_concat_vs_fuente.json`.
- **Decisión para Omar:** el handoff pedía PSNR ≥ 50 dB contra el final de hoy, y eso no se cumple a la letra (44.8 dB). Lo que baja el número es la pérdida del camino viejo, no la del nuevo. El criterio que dejé es duración ± 1 frame + PSNR de luma ≥ 50 dB contra el camino viejo sin pérdida (B33, DOC_MAESTRO §6). Queda a confirmar por Omar.
- Tests: 126 verdes.

### Veredicto revisor-handoff §4 (íntegro)

```
VEREDICTO: CUMPLE CON OBSERVACIONES

Los 126 tests pasaron (12 s) y los candados verificables se sostienen. Dos puntos del contrato no se cumplen a la letra: el PSNR ≥ 50 dB solo se cumple en el test sintético, y las ventanas son más anchas que ±1 s.

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Xfade inter-cap re-encodea solo ±1 s alrededor de cada frontera, el resto va con `-c copy` | PARCIAL | `script_engine/transition_applier.py` `concat_windowed`/`plan_windows`/`_split_copy` implementan cuerpos copiados y ventanas. Con GOP 250 la ventana llega a ~10 s por lado (B31, declarado), no ±1 s. Sigue siendo ~1,5 % del video. |
| 2 | Verificar parámetros de encode iguales; si no, normalizar en `_build_chapter_segment` | OK | Las ventanas usan `_venc()`, el mismo encoder que los segmentos (B32). El diff de `fase2b.py` no toca `_build_chapter_segment`. |
| 3 | Música como audio solo + remux `-c:v copy` | OK | `fase2b.py` `_mix_music_audio_only` (remux con `-c copy -shortest`). Test `test_musica_audio_solo_mismo_largo_que_la_clasica` pasa. |
| 4 | `--hw-encode` para las ventanas si está disponible | OK | Las ventanas heredan `_venc()`, así que usan NVENC solo si los segmentos también (B32). |
| 5 | Segmentos sin `--gfx` byte-idénticos | OK | `git diff fase2b.py`: ningún hunk dentro de `_build_chapter_segment`. Tests de reassemble y hwencode verdes. |
| 6 | "Igual que hoy" ahora = PSNR ≥ 50 dB y duración ±1 frame, anotado en el doc maestro | PARCIAL | El test sintético exige PSNR de luma ≥ 50 dB (`test_module_concat_windowed.py:60-66`), contra una referencia sin pérdida del camino viejo, no contra un final viejo real. DOC_MAESTRO §6 y §8 anotado (línea 115). Duración: 20 583 = 20 583 frames. |
| 7 | Tiempo: concat+música ≤ 2,5 min | NO VERIFICABLE | Solo hay medición parcial: concat 62,3 s (`lab/hyperframes/f2b/measure_concat_f2segs.json`). Falta el tiempo de la mezcla de música sobre el render real. |
| 8 | Tiempo: incremental ≤ 6 min y corrida completa extra ≤ 22 min | NO VERIFICABLE | Dependen del render completo, que va después. |
| 9 | Candados §6: lock literal, sin shaders, sin rembg, `main` intacta, tests verdes | OK | Tests verdes. El diff solo toca ffmpeg y flags, sin shaders ni rembg ni texto del LLM. No miré la rama `main`. |
| 10 | Entregables de §4 existen | OK | `test_module_concat_windowed.py` (6341 B), `measure_concat_f2segs.py/.json/.log` (no vacíos), B31–B34 en `DECISIONES_F2b.md`. |

**Punto del PSNR:** contra el final viejo real el PSNR da 44,8 dB de luma (sin ch04), debajo de 50. Con ch04 da 41,2. No cumple la letra del contrato. CC lo reinterpretó en B33 y lo anotó en el doc maestro, pero esa reinterpretación la hizo él. Su argumento es técnico y razonable: el xfade viejo resamplea el croma de todos los frames, así que el viejo pierde contra la fuente.
- Las cifras que sostienen el argumento (Y 47,3 viejo vs fuente, Y 58,6 nuevo, ∞ en los cuerpos) no están en ningún artefacto del repo. El JSON/log solo guarda 44,78 / 46,23 / 41,16 / 42,75.
- Falta el medidor contra la fuente, y la exclusión de ch04 (284,87–401 s) no está explicada en el JSON.
- No está dicho que Omar haya aceptado el criterio nuevo; Omar debe decidir si lo acepta.

Fuera de alcance: `diag_234_cap4.py` (solo cambia el TOPIC; el contexto dice que no es de §4). `lab/hyperframes/_handoff_adjuntos/DOC_MAESTRO_HyperFrames.md` está untracked, pero el contrato lo pide.

Riesgos que el contrato no cubre:
- La ventana real depende del keyframe cada 250 frames: con otros GOP o fronteras cercanas `plan_windows` devuelve None y cae al xfade clásico, silenciosamente, con solo un aviso en consola.
- El fallback a la mezcla clásica ante error también es silencioso, así que un render completo podría tardar el tiempo viejo sin falla visible.
- No se midió sincronía A/V ni la unión entre el padding inicial y el video más allá de la duración en frames.
```

Respuesta de CC:
- Las cifras contra la fuente ahora están en `measure_concat_vs_fuente.py/.json`: viejo Y 47.26 (5–60 s) y 47.39 (20–60 s); nuevo Y 58.64 (5–60 s) e ∞ (20–60 s). La exclusión de ch04 está explicada en el docstring.
- Los fallbacks se van a verificar en el log del render completo, que tiene que decir «⚡ concat por ventanas» y «audio solo + remux». La sincronía A/V y la unión del padding se miden ahí (duración de audio vs video y un frame de la unión).

## Render completo de Orleans (looks, disperso, sin `--hw-encode`)

Comando: `python fase2b.py ba6c3cac-a091-41c0-8dad-afd2f4364747 --reuse-visuals --keep-segments --gfx --gfx-sparse` (log `full_run_f2b.log`). Los productos de F2 se respaldaron antes en `_fase2b_work/_bak_f2_pre_f2b_full/`, para que `--reuse-visuals` no reusara las capas viejas.

Entregables en `output/ba6c3cac…/`:
- `…_final_gfx.mp4`: B-F2b, 688.4 s.
- `AB_ba6c3cac…_f2b.mp4`: A sin gfx | B-F2b, 1920×540, 688.5 s, con audio.
- Cues y página de revisión de los 7 caps en `lab/hyperframes/f2b/corrida_final/` (los `gfx_review_chNN.html` apuntan a los segmentos en `_fase2b_work/`).

### Bloques por cap

| cap | bloques | recortes | énfasis / con ícono | zoom con box / sin | densidad s (máx hueco) | capa gfx s |
|---|---|---|---|---|---|---|
| ch01 | 7 | 0 | 1 / 1 | 1 / 1 | 6.0 (máx 8.8) | 106.6 |
| ch02 | 11 | 2 | 3 / 3 | 0 / 0 | 8.9 (máx 16.9) | 252.7 |
| ch03 | 16 | 0 | 5 / 3 | 0 / 1 | 9.6 (máx 17.7) | 344.5 |
| ch04 | 14 | 1 | 4 / 3 | 1 / 0 | 8.7 (máx 17.3) | 297.0 |
| ch05 | 14 | 1 | 3 / 3 | 0 / 1 | 10.0 (máx 15.7) | 287.0 |
| ch06 | 13 | 1 | 1 / 1 | 1 / 0 | 8.4 (máx 17.2) | 260.5 |
| ch07 | 9 | 0 | 3 / 3 | 0 / 1 | 9.1 (máx 16.2) | 204.3 |

- **Recortes: 5 en el video (antes 0).**
  - ch02: «El huracán Katrina tocó tierra» (kicker 2005) y «Los prisioneros quedaron atrapados durante días en celdas».
  - ch04: «Había niños de hasta 10 años».
  - ch05: «Reclusos de la sección 'Templeman III' informaron».
  - ch06: el mismo titular del fact 5 que ch02. Un fact puede repetirse entre caps: no hay regla anti-repetición entre caps (deuda).
  - Sin recorte: ch01, ch03 y ch07. El objetivo de 1–2 por cap se cumple en 4 de 7.
- **Densidad:** 8.9 s promedio entre bloques; el hueco más largo es de 17.7 s (máximo pedido: 18 s). 0 `gap_warning`.
- **Zoom guiado por narración:**
  - 3 zooms con box de visión: ch01, ch04 y ch06.
  - 4 descartados: sin frase ancla en su escena o visión bajo 0.7. ch02 no propuso zoom.
  - Ningún zoom fuera del detalle narrado: sin box, no hay zoom.
- **Moods e íconos usados:**
  - oscuridad (candado): 8.
  - agua (gota): 6.
  - muerte (cruz): 2, «cadáveres» en ch05 y ch07.
  - veneno: 0; la narración de Orleans no dispara su léxico.
  - `icon_array`: 0; ningún fact de Orleans tiene la forma «A de los B».
  - `chapter_question`: apagada.
- **Palabras de énfasis sin ícono:** «ahogados» y «ahogaba» (ch03) y «atrapados» (ch04). Las tres son por el **tope de 3 `icon_callout` por cap**, no por falta de ícono: las 4 categorías activas tienen ícono. Para el vigilante mensual: 0 palabras sin ícono por categoría.
- **Router:** la visión de retratos corrió sobre 29 imágenes y ninguna salió `cara_closeup` → high = 0, movimiento seguro en 0 imágenes.
- Fallbacks de la capa gfx: 0. Lint: 0 errores en los 7 caps.
- Candado sin `--gfx` re-verificado al cierre: md5 de ch02 `--only-cap` = `38e5ba14e3d24fd20f9297c9e1dfee24`, igual que en §1 (`onlycap_ch02_nogfx_final.log`).

### Tiempos

| medida | F2 (nocturno) | F2b | objetivo |
|---|---|---|---|
| corrida completa | 3138 s (52.3 min) | **2272 s (37.9 min)** | — |
| extra vs A sin gfx (1114 s) | +33.7 min | **+19.3 min** | ≤ 22 min ✔ |
| concat + música | ~15 min | **85 s** (67 + 18) | ≤ 2.5 min ✔ |
| incremental (cambiar un callout de ch04) | 22.2 min | **7.5 min** (log `incremental_ch04_f2b.log`) | ≤ 6 min ✘ |

- El incremental no llega a 6 min por la capa gfx de ch04 (297 s: render HF 210 + cosido 56), que se rehace entera. Concat y música ya suman 84 s. Para bajar de 6 min habría que re-renderizar solo las ventanas que cambiaron dentro del cap (deuda, fuera de este handoff).
- La prueba incremental quitó el callout «nivel del pecho» y se verificó que ya no está en las cues. Después se restauró el final oficial (md5 igual al respaldo); el incremental quedó en `_bak_f2b_incremental/`.
- Final: video 688.43 s y audio 688.52 s, los dos arrancan en 0. Decodifica sin errores. La unión del padding inicial no se nota (`union_padding.jpg`).

### Corrección después del render (solo ch05)

En la corrida completa ch05 mostró dos defectos:
1. El recorte del fact 7 se descartaba porque el validador chequeaba el kicker de fuente («Human Rights Watch, 2005») contra el fact y no contra `sources[]`.
2. El titular del fact 8 terminaba en «…informaron haber».

Ambos están corregidos (B35, test nuevo) y se re-ensambló solo ch05 (`reassemble_ch05_fix.log`, 7.2 min). El fact 7 ahora pasa la validación, pero no entra por solape con el callout «Human Rights Watch» y el contador «500» de esa escena: regla de no solapar, no bug. Después se regeneró el AB.

### PSNR (§4)

- Mismos frames que el concat viejo: 20 583 = 20 583.
- Nuevo vs viejo, sin ch04: Y 44.8 / promedio 46.2.
- Contra la fuente: viejo Y 47.3, nuevo Y 58.6 (∞ en cuerpos). Detalle en la sección §4 y en B33.
- `--hw-encode` no se usó: NVENC midió 48.7 dB (< 50) en F2.

### Gemini

- Llamadas F2b: 41 (director v1.5: 7 + 1 de ch02; visión de retratos: 29; zoom con ancla: ~4). Costo según el cost_tracker: $0.0598 en la corrida completa más las de ch02 → **≈ $0.10, bajo el tope de $2**.
- Aparte, fal (Flux.2 Pro, íconos): 36 imágenes ≈ $1.08.

### Para Omar
1. Mirar el **AB** (`AB_…_f2b.mp4`) y el final `…_final_gfx.mp4`.
2. Decidir si acepta el criterio de PSNR de §4 (luma contra el camino viejo sin pérdida, B33) en lugar de "≥ 50 dB contra el final de hoy".
3. Deudas que deja F2b:
   - Incremental de 7.5 min (hace falta re-render por ventana dentro del cap).
   - Recortes repetidos entre caps.
   - `chapter_question` espera `cliffhanger` por cap de m01b.
   - El reloj aprobado (5b) tiene números romanos.

### Veredicto revisor-handoff del cierre (íntegro)

```
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Commits por sección §1–§4 (§3 tras aprobación de Omar) | OK | `git log`: aec3a4a, 046c4c9, 2879665, f3fd3db, 6819ee5. PARADA 2 documentada en F2b_REPORT.md:172 |
| 2 | `tira_iconos_12.jpg` | OK | existe, 678 KB (lab/hyperframes/f2b/) |
| 3 | Render completo looks+disperso, sin `--hw-encode` (PSNR 48.7 < 50) | OK | `_final_gfx.mp4` 688.52 s con audio, 2560x1440. Comando y B32 en el reporte |
| 3b | `AB_{id}_f2b.mp4` | OK | existe, 77.9 MB, 1920x540, 688.47 s, nombre exacto, generado 13:40 (después del fix ch05) |
| 3c | Cues de los 7 caps + página de revisión | OK | `corrida_final/` tiene `gfx_cues_ch01..07.md` y `gfx_review_ch01..07.html`, ninguno vacío |
| 4 | F2b_REPORT: bloques, moods e íconos, recortes, zooms con/sin box, densidad, tiempos, énfasis sin ícono, PSNR, Gemini | PARCIAL | Todas las secciones están (F2b_REPORT.md:270-380). Pero el texto dice "Recortes: 6 en el video" y la suma real es 5: tabla 0+2+0+1+1+1+0, cues `archive_clipping` ch02 2, ch04 1, ch05 1, ch06 1, y `report_data_f2b.json`. Además el texto dice ch02 tiene 2 recortes y el JSON lista solo 1 para ch02 y el de «prisioneros» en ch06. El texto de recortes tiene que corregirse |
| 4b | Tiempos | OK (objetivo incremental NO cumplido) | Reporte: total 2272 s, concat+música 85 s, incremental 7.5 s min vs objetivo ≤ 6 min. Lo declara como ✘ y deuda, sin ocultarlo |
| 5 | Prueba incremental ch04 | OK | `incremental_ch04_f2b.log` existe. B36 documenta que se restauró el final oficial con md5 verificado. No re-medí ese md5 |
| 6 | Veredictos del revisor íntegros | PARCIAL | Íntegros: §1, §2, ajuste PARADA 1, §3, PARADA 2 y §4 (F2b_REPORT.md:17, 58, 104, 146, 186, 233). Falta el veredicto sobre el cierre (fix ch05 + render final), que es este |
| 7 | Candado: lock literal | PARCIAL | Cambio de cierre en `gfx_director.py` acepta como kicker la fuente de `sources[]`. El texto sale de `sources[]`, no del LLM, y el test nuevo lo cubre. El reporte dice que el candado lo re-chequea. Esa re-verificación no la corrí sobre el video final |
| 8 | Candado: sin `--gfx` byte-idéntico | PARCIAL | `git diff aec3a4a..HEAD -- fase2b.py`: hunks solo en `_mix_music_into_video`, `_concat_segments`, `_assemble_one_video`, `main`. `_build_chapter_segment` no se toca y el diff sin commitear de `fase2b.py` está vacío. Pero hay cambios en `_segment_hash` y en gfx_config/director posteriores a §1. El md5 `38e5ba14…` no se re-midió desde §1 (lo cubre el reporte). No se ejecutó nada |
| 9 | Candado: sin shaders, sin rembg, sin texto/ícono inventado por el LLM | NO VERIFICABLE | No audité el código de §2–§3 contra esto. El reporte declara íconos propios (set de 12) y que el director v1.5 es determinista. No hay evidencia independiente de mi parte |
| 10 | `main` intacta | OK | `git log -1 main` = 43f528a |
| 11 | Tests verdes | OK | Corrí el comando del contrato: 127 passed en 11.28 s |

Fuera de alcance: `diag_234_cap4.py` (modificado, ajeno según el contexto; el cambio es de 1 línea). El resto de lo sin commitear está dentro de `lab/hyperframes/f2b/` o son los archivos esperados del cierre: `script_engine/gfx_director.py`, `test_module_gfx_director.py`, `F2b_REPORT.md`, `DECISIONES_F2b.md`.

Riesgos que el contrato no cubre: (1) El final de ch05 se re-ensambló después del render completo y no hay chequeo posterior de PSNR/duración del final nuevo; el reporte solo cita 688.43/688.52 s. (2) `gfx_review_chNN.html` apunta a `_fase2b_work/`, así que dependen de que esa carpeta se conserve. (3) Los recortes repetidos entre caps (ch02 y ch06, mismo titular) están declarados como deuda.
```

Respuesta de CC al veredicto del cierre:
- **#4:** el conteo está corregido a **5 recortes** (ch02 2, ch04 1, ch05 1, ch06 1). ch02 tiene 2 según sus cues: «El huracán Katrina tocó tierra» y «Los prisioneros… en celdas».
- **#8:** el md5 sin `--gfx` se re-midió después del veredicto: `38e5ba14e3d24fd20f9297c9e1dfee24` (`onlycap_ch02_nogfx_final.log`). El candado se mantiene.
- **#7:** el `lock rechazados: 0` de ch05 en el re-ensamble está en `gfx_ch05.log`. El kicker de fuente pasó por el candado literal.
- **Riesgo (1):** las duraciones 688.43 / 688.52 s y la decodificación sin errores se midieron sobre el final posterior al fix de ch05.

## Pre-merge — tres fixes pedidos por Omar (ch02 en looks + página de revisión; se para acá)

1. **Íconos por palabra, no por categoría (B37).** Si la palabra no es lo que el ícono dibuja, va sin ícono (sello + mood).
   - Candado ← encerrados / encierro / celda(s) / calabozo(s) / atrapados / bajo llave (barrotes y rejas sin ícono).
   - La oscuridad (oscuro, a oscuras, sin luz…) va sin ícono.
   - Gota ← solo agua / aguas.
   - Cruz ← tumba / fosa / sepultados / cementerio / muerte / muertos / murieron / fallecidos.
   - Calavera ← cadáver(es) / cuerpos / restos, y también veneno / arsénico / cianuro / tóxico.
   - Biohazard ← infección / contaminado / epidemia / plaga / peste / cólera / tifus / disentería.
   - Enfermos, fiebre e inundación van sin ícono.
2. **`engrave` sobre potrace: no dibujaba trazo a trazo (B38).** Los SVG son rellenos; `engrave` dibujaba el **contorno** de 40 manchas (de 100–209 sub-paths) y después barría el relleno. Se reemplazó por **`press_wipe`**: revelado de arriba abajo con borde rugoso, 0.8 s, sin tocar los SVG. `engrave` queda solo para trazos reales (Lucide).
   - **Hold vivo (B39):** respiración 1 ↔ 0.85 (medio ciclo de 0.9 s, nunca quieto más de 1 s), deriva ±3 px y un único pulso del rojo. La salida "tinta que se seca" no cambia.
3. **Recortes (B40):**
   - Un fact con fuente + año va antes que los callouts.
   - Si el único choque es el contador, el recorte pasa a la derecha.
   - Si el cap queda sin recortes con facts propios, se convierte el mejor callout.

**ch02 en looks** (`onlycap_ch02_premerge_looks.log`, render de 245 s, lint con 0 errores):
- Recortes: 2 (los mismos de antes).
- Énfasis:
  - «oscuro» → sin ícono (sello + mood oscuridad).
  - «sumergidos» → sin ícono (la gota es solo para «agua»).
  - «encierro» → candado en sello, con hold vivo y el pulso de la cerradura.
- Página de revisión: `gfx_review_ch02_premerge.html`. También `gfx_cues_ch02_premerge.md` y `tira_premerge_ch02.jpg`.
- En ch02 no cae ninguna palabra con `press_wipe` ni `ink_bleed`. Para verlas: `demo_iconos_premerge.mp4`, 6 s, HyperFrames real, lint con 0 errores. Muestra gota/press_wipe, calavera y cruz/ink_bleed, candado/stamp, el hold vivo y la salida. Cuadros en `demo_iconos_premerge_frames.jpg`.

Tests: 145 verdes (+8 nuevos: ícono por palabra ×14 casos, press_wipe/engrave, hold vivo, prioridad del recorte con fuente, conversión de callout, cambio de lado por el contador).

**No se re-renderizó el video completo ni el AB**: Omar pidió parar en ch02. El `_final_gfx.mp4` y el AB actuales son de antes de estos fixes.

### Veredicto revisor-handoff pre-merge (íntegro)

```
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1a | Ícono por palabra; oscuridad_encierro partida: encerrados/celda/atrapados → candado; oscuro/a oscuras/sin luz → sin ícono | OK | misterio.json `icon_words` (oscuridad_encierro no mapea oscuro/oscuras/sin luz/oscuridad/penumbra); gfx_director.py `place_emphasis` usa `icon_words.get(trig)`; test `test_icono_por_palabra_no_por_categoria` (14 casos) |
| 1b | Revisar las otras 3 categorías con el mismo criterio | PARCIAL | agua → solo "agua/aguas" → gota (inundación, ahogados, sumergidos sin ícono). Pero `barrotes`/`rejas` → candado: un candado no dibuja barrotes ni rejas (contradice la regla de Omar). `cuerpos`/`restos` → calavera y `muerte`/`morir`/`muertos` → cruz son discutibles. Es juicio de Omar, no lo puedo cerrar. |
| 1c | Validación de config (icon_words ⊂ triggers e ICON_KEYS) | OK | gfx_config.py:398-409; test `gc.ICON_KEYS == set(gi.ICON_WHITELIST)` |
| 2a | Confirmar si engrave dibuja trazo a trazo sobre potrace | OK | Dicho explícitamente: NO, son rellenos (DECISIONES B38, F2b_REPORT "Pre-merge" §2, docstring gfx_icons/__init__.py). No contrasté el conteo "40 de 100–209 sub-paths". |
| 2b | Si no, reemplazar por press_wipe (arriba→abajo, borde rugoso, 0.8 s), sin rehacer SVG | OK | gfx_icons/__init__.py: `PRESS_SEC=0.8`, `_rough_edge`, engrave→press_wipe si `not strokes_only`; misterio.json sin engrave (agua y otros → press_wipe); SVG de gfx_profiles/icons no tocados (git status) |
| 2c | Hold vivo: opacidad 0.85–1, deriva ±3 px, pulso único del rojo, nunca quieto >1 s | OK | `BREATH_SEC=0.9`, `DRIFT_PX=3`, accent `.45` yoyo repeat 1 solo con `has_accent`; test `test_hold_vivo_y_pulso_unico_del_rojo`. Tramos de hasta ~0.9 s sin cubrir al final del hold (por `int()`), dentro del límite. Solo demostrado en demo_iconos_premerge.mp4 (no lo reproduje). |
| 2d | Salida tinta que se seca | OK | `.dry circle` + opacidad conservados (diff) |
| 3a | Fact con fuente+año → recorte antes que callout | OK | gfx_director.py `_place_archive` con `fsrc` antes del bucle de callouts; test `test_recorte_con_fuente_gana_al_callout` |
| 3b | Cap en 0 recortes con facts elegibles → convertir mejor callout | OK (solo en test) | `convert_callout_to_archive`; test `test_cap_sin_recortes_convierte_el_mejor_callout`. En ch02 no se ejercitó (ya tenía 2 recortes, log líneas 358+). |
| 3c | Solape con contador → cambiar de lado, no descartar | OK (solo en test) | `_place_archive` fuerza lado derecho; test `test_solape_con_contador_cambia_de_lado`. Asume contador siempre arriba a la izquierda. |
| 4 | Tests verdes | OK | corrí el comando del contrato: 145 passed |
| 5 | render ch02 looks + página de revisión | OK | Existen y no vacíos: onlycap_ch02_premerge_looks.log (2.7 KB), gfx_review_ch02_premerge.html (6 KB), gfx_cues_ch02_premerge.md, tira_premerge_ch02.jpg, demo mp4 y frames. Plan en gfx_ch02.log:358: oscuro→sin ícono, sumergidos→sin ícono (press_wipe), encierro→candado. No vi las imágenes ni el HTML; no verifiqué el render visual. |
| 6 | Parar ahí (sin render completo, sin commit) | OK | git log HEAD=6da04d3, cambios sin commitear; reporte lo declara |
| 7 | Candados §6: sin shaders, sin texto/ícono inventado por el LLM, main intacta | OK | Íconos solo de lista blanca; `fact_idx` agregado solo a callouts del director; main en 43f528a. No leí el §6 del handoff completo. |

Fuera de alcance: diag_234_cap4.py (modificado, cambia TOPIC; el pedido lo declara preexistente, pero igual figura en `git diff` sin relación con los 3 fixes). Cuidado de no commitearlo. icons_raw/, tira_iconos_proj/ y demo_iconos_premerge_proj/ regenerables, sin commitear.

Riesgos que el contrato no cubre: (1) los caminos 3b y 3c solo están probados con tests unitarios, no en un render real. (2) "sumergidos" sin ícono: la prueba visual de press_wipe en agua solo está en el demo, no en ch02. (3) El render completo y el AB quedan desactualizados respecto de estos fixes (el reporte lo admite).
```

Respuesta de CC:
- **1b:** barrotes y rejas ya no llevan candado (B37 corregido, test con «barrotes» → sin ícono; 146 verdes). No afecta el render de ch02, que no usa esas palabras.
- **A decidir por Omar:** cuerpos/restos → calavera y muerte/morir/muertos → cruz. Si para él la cruz solo dibuja una tumba, se dejan esas palabras sin ícono y queda una línea en `misterio.json`.
- **Sin commitear**, a propósito: Omar dijo "parás ahí; yo miro". Con su OK va un commit `feat(gfx-f2b): pre-merge (íconos por palabra, press_wipe + hold vivo, recortes)` y después lo que pida (¿render completo + AB nuevos antes del merge?).

### Aprobación de Omar + mapa de muerte (B41)

Omar aprobó el pre-merge con este mapa:
- cadáveres / muertos / cuerpos / restos → calavera.
- tumba / enterrados / fosa / sepultados → cruz.
- muerte / morir / murieron → sin ícono.

«enterrados» se agregó al léxico con sus flexiones. Lo no nombrado (fallecidos, cementerio, difuntos…) va sin ícono. Tests: 151 verdes.

#### Veredicto revisor-handoff del commit pre-merge (íntegro)

```
VEREDICTO: CUMPLE

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | cadáver(es), muerto/a/os/as, cuerpos, restos → calavera | OK | misterio.json moods.muerte.icon_words (8 entradas → "calavera"); test_icono_por_palabra_no_por_categoria (cadáveres, muertos, restos) |
| 2 | tumba(s), enterrados/as, fosa(s), sepultados → cruz | OK | icon_words muerte: tumba, tumbas, enterrado/a/os/as, fosa, fosas, sepultados → "cruz"; tests tumba y enterrados |
| 3 | muerte / morir / murieron → sin ícono | OK | icon_words.get devuelve None para los tres; tests ("murieron", None), ("muerte", None) |
| 4 | enterrado/a/os/as agregadas a triggers | OK | muerte.triggers: enterrados/enterrado/enterrada/enterradas = 2 |
| 5 | B41 documentado; palabras no nombradas sin ícono | OK | DECISIONES_F2b.md:48. Verificado: fallecidos y cementerio dan None; tests ("fallecidos", None) |
| 6 | barrotes/rejas sin candado | OK | oscuridad_encierro.icon_words no contiene barrotes ni rejas (get → None); test ("barrotes", None); sus triggers siguen activos (mood intacto) |
| 7 | B37 y F2b_REPORT corregidos | OK | DECISIONES_F2b.md:44 ("barrotes y rejas sin ícono... corregido tras el revisor"); F2b_REPORT.md:392 y :447 |
| 8 | Tests del contrato | OK | `pytest test_module_gfx_*.py ... test_module_transition_timeout.py -q` → 151 passed |
| 9 | Afirmación "ch02 no cambia" | OK | No se puede verificar con render (prohibido), pero ch02_premerge existe y los cambios de (a)/(b) solo tocan palabras de muerte y barrotes/rejas; el contrato indica que ch02 no las usa |
| 10 | Archivos del commit presentes | OK | Los 10 modificados y los demás (demo.py, 8 artefactos premerge) existen; demo.py y los artefactos figuran como untracked, o sea que requieren `git add` explícito |

Fuera de alcance: diag_234_cap4.py figura modificado (ajeno; declarado como NO va). Untracked que NO van: icons_raw/, tira_iconos_proj/, demo_iconos_premerge_proj/. Ningún otro archivo tocado fuera de la lista.

Riesgos que el contrato no cubre:
- Fallecidos, falleció, cementerio, difuntos, mataron, asesinados y morgue quedan sin ícono por criterio literal. Si Omar esperaba cruz o calavera para alguno, se ve recién en un render real.
- Los .md se normalizarán a CRLF al commitear (warning de git); no afecta el contenido.
- Hay que hacer `git add` por ruta, no `-A`, para no arrastrar diag_234_cap4.py ni los directorios untracked excluidos.
```

## Render completo pre-merge (commit `11a9d1f`, looks + disperso)

Log: `full_run_f2b_premerge.log`. Los productos anteriores (final, no_music, AB y capas gfx de la versión 1) quedaron en `_fase2b_work/_bak_f2b_v1_antes_premerge/`.

**Entregables vigentes:**
- `output/…/…_final_gfx.mp4`: 688.4 s. Video y audio arrancan en 0; el audio dura 688.52 s. Decodifica sin errores.
- `AB_ba6c3cac…_f2b.mp4`: A | B, 1920×540, 688.5 s, con audio.
- Cues y revisión de los 7 caps: `lab/hyperframes/f2b/corrida_premerge/`.

| cap | bloques | recortes | énfasis / con ícono | zoom con box / sin | densidad s (máx hueco) | capa gfx s |
|---|---|---|---|---|---|---|
| ch01 | 8 | 1 | 1 / 1 | 1 / 1 | 4.8 (máx 7.1) | 106.0 |
| ch02 | 11 | 2 | 3 / 1 | 0 / 0 | 8.9 (máx 16.9) | 283.9 |
| ch03 | 16 | 1 | 5 / 1 | 0 / 1 | 9.6 (máx 17.7) | 341.7 |
| ch04 | 14 | 1 | 4 / 2 | 1 / 0 | 8.7 (máx 17.3) | 306.0 |
| ch05 | 13 | 2 | 3 / 1 | 0 / 1 | 10.0 (máx 15.7) | 298.9 |
| ch06 | 14 | 2 | 1 / 1 | 1 / 0 | 7.7 (máx 17.2) | 274.9 |
| ch07 | 10 | 1 | 3 / 1 | 0 / 1 | 8.1 (máx 16.2) | 205.8 |

- **Recortes: 10, al menos 1 en cada cap** (antes 5, con 3 caps en 0).
  - ch03 salió por **conversión** del callout «Templeman 1 y 2» → «El agua dentro de algunos edificios».
  - En **4** recortes se cambió de lado por el contador (ch01, ch05, ch06 y ch07).
  - Se repite «Los prisioneros quedaron atrapados durante días en celdas» (ch02 y ch06) y «Aproximadamente 6,500 personas» (ch01 y ch07).
- **Íconos por palabra:** salieron 8. Candado en encerradas, encierro, celdas y atrapados ×3; calavera en «cadáveres» (ch05 y ch07). Otros 12 énfasis van **sin ícono porque la palabra no lo dibuja**: oscuro, oscuridad ×2, sin luz, aislados, sumergidos, inundación, ahogados, ahogaba, anegadas, flotando, marea. Ninguno quedó fuera por tope.
  - «agua» no salió como énfasis en Orleans, así que la gota con `press_wipe` no aparece en este video (sí en `demo_iconos_premerge.mp4`).
- **Densidad:** 8.6 s promedio y hueco máximo de 17.7 s (máximo pedido: 18). 0 fallbacks.
- **Tiempos:** total **38.3 min** (+19.8 sobre A ✔ ≤ 22); concat **69 s** + música **19 s** ✔. Gemini $0 en esta corrida (el plan del director estaba cacheado).

### ⚠ Problema que generó la regla "solape con contador → cambiar de lado"

En **ch01 y ch07** el recorte «Aproximadamente 6,500 personas» comparte pantalla con el contador «6,500» del **mismo fact**. En ch05, «Más de 500 prisioneros no figuraban» se solapa 0.3 s con el contador «500». Es el mismo dato dos veces a la vez (`tira_premerge_full.jpg`, arriba). La regla hace lo que dice, pero no distingue si el recorte y el contador son del mismo fact.

**No lo corregí** porque pediste parar acá. Propuesta mínima: si el recorte es del **mismo fact** que el contador, el recorte se descarta (o se muda a otra escena) y el cambio de lado queda solo para facts distintos. Se arregla en una línea y se re-ensamblan ch01, ch05 y ch07 (~7 min c/u en incremental).

### Veredicto revisor-handoff del render pre-merge (íntegro)

```
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Mapa muerte: cadáveres/muertos/cuerpos/restos → calavera | OK | `gfx_profiles/misterio.json:60` `icon_words` (cadáver(es), muerto/a(s), cuerpos, restos → calavera). Las calaveras aparecen en la corrida (cues ch05 y ch07). |
| 2 | tumba/enterrados/fosa/sepultados → cruz | OK | Mismo `icon_words`: tumba(s), enterrado/a(s), fosa(s), sepultados → cruz. |
| 3 | muerte/morir/murieron → sin ícono | OK | Están en `triggers` pero ausentes de `icon_words`, así que dan mood sin ícono. |
| 4 | Commitear los fixes pre-merge | OK | HEAD `11a9d1f` (17 archivos, +549/−63: director, icons, config, profile, tests, lab). Sin Co-Authored-By distinto al del reporte; solo lo hecho. |
| 5 | Re-render completo en looks, disperso | OK | `full_run_f2b_premerge.log`: los 7 caps "(disperso)", mezcla de música, "FASE 2B BATCH TERMINADA 1/1", 38m16s. |
| 6 | AB nuevo | OK | `AB_…_f2b.mp4` 1920×540, 688.47 s, con audio, fecha 15:10 (el v1 respaldado es de 13:40, distinto tamaño). |
| 7 | Actualizar F2b_REPORT | OK | Sección "Render completo pre-merge" (+34 líneas). Cotejado con `report_data_f2b_premerge.json` y el log: bloques por cap, 10 recortes, 8 íconos, 12 énfasis sin ícono (la lista coincide ítem por ítem), 4 cambios de lado, densidad 8.6 s, concat 69 s, música 19 s, 38.3 min. Las duraciones por cap están en el JSON. |
| 8 | Final válido | OK | ffprobe: video 688.43 s y audio 688.52 s, ambos con start 0. Backups v1 presentes en `_bak_f2b_v1_antes_premerge/`. |
| 9 | "Parás ahí" | OK | No hay commits nuevos; HEAD sigue en `11a9d1f`; no se corrigió el problema del contador. |
| 10 | Honestidad sobre recorte + contador del mismo fact | OK | El reporte tiene un apartado ⚠ que lo nombra (ch01, ch07 mismo fact 6,500; ch05 solape de 0.3 s con «500»), dice que no se corrigió porque pediste parar, y da una propuesta. |
| 11 | Candados §6: main intacta, tests, lock | OK | `git log -1 main` = 43f528a. Tests: 151 passed. Sin cambio en archivos de lock/texto del LLM en el diff. |

Observaciones:
- Los números del reporte coinciden con los datos, salvo 688.4 s (video) frente a 688.5 s (audio y log). Es redondeo, no error.
- ESTADO_SESION.md dice "(+ commit del reporte pre-merge)" y ese commit aún no existe; está pendiente.
- La estimación "~7 min c/u en incremental" no se puede verificar con la evidencia dada. Tampoco pude verificar el tamaño de lado ni el solape visual (no se hizo ni se pidió render).

Fuera de alcance: ninguno. Los tracked modificados son F2b_REPORT.md (esperado), `build_report_data.py` (herramienta del reporte, aceptable) y `diag_234_cap4.py` (ajeno, declarado). Los ?? restantes son artefactos de la corrida o preexistentes.

Riesgos que el contrato no cubre: el bug recorte + contador del mismo fact sigue vivo en 3 de 7 caps del video entregable. El reporte, el JSON y ESTADO están sin commitear, así que el commit siguiente debe hacerse por ruta. El reporte se normalizará a CRLF al commitear.
```

Respuesta de CC: el commit del reporte se hace ahora, por ruta. Los ~7 min por cap salen del incremental medido (ch04: 7.5 min; ch05: 7.2 min); para 3 caps serían unos 3 × 5 min de capa gfx + 1.5 min de concat y música si se re-ensamblan juntos.

## Pre-merge v2 — un fact = un bloque + dedupe de cifras (B42)

- **Un fact = un bloque:** recorte y contador del mismo fact o la misma cifra → gana el contador; el recorte pasa al siguiente fact elegible, y si no hay, el cap queda sin ese recorte.
- **Dedupe a nivel video:** una cifra se anima como contador una sola vez; la 2.ª vez, recorte de ese fact o nada.
- **Se quitó "cambiar de lado".**
- Tests: 155 verdes (+5).
- **Alcance:** aplicar la regla cambia 6 de 7 caps (ch01, ch02, ch04, ch05, ch06 y ch07), no solo los 3 pedidos. ch02 y ch04 repiten el contador «6,500» de ch01 y ch06 tiene recorte y contador del fact 6 («650,000»). Se consulta a Omar antes de re-ensamblar.

### Veredicto revisor-handoff del fix (íntegro)

```
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Un fact = un bloque; si recorte y contador comparten fact_idx o cifra, gana el contador y el recorte pasa al siguiente fact elegible | OK | gfx_director.py `_shares_counter`, `_next_fact`, `_place_archive` (comparación por fact_idx y por dígitos del titular) |
| 2 | Si no hay otro fact elegible, el cap queda sin recorte | OK | `_place_archive`: `if alt is None: return False` + log |
| 3 | Dedupe de cifras a nivel video: 1.ª vez contador, 2.ª recorte o nada | OK (código) | `counted_figures_before` + `ctx["video_counted"]` en gfx_layer.py; el `count_up` repetido pasa a `second_cifra` y se coloca con `_place_archive` o se descarta. El resultado real depende del render: NO VERIFICABLE |
| 4 | Quitar la regla "cambiar de lado" | OK | diff: borrado `hits`/`cu_iv`/`side="right"`; solape ⇒ `if not _free(a,b)` descarta |
| 5 | Tests | OK | los 5 archivos de test indicados: 155 passed en 12 s. Los 5 tests nuevos reemplazan `test_solape_con_contador_cambia_de_lado` |
| 6 | Re-ensamblar solo ch01/ch05/ch07 (incremental) | NO VERIFICABLE | el re-ensamble va después del commit. Ver el punto de abajo |
| 7 | AB nuevo + reporte actualizado + parar | NO VERIFICABLE | todavía no existen. DECISIONES_F2b.md tiene B42, pero el reporte no se actualizó |
| 8 | main intacta | OK | `git log -1 --format=%h main` = 43f528a; HEAD = eb97a86 |

Punto a juzgar (6 de 7 caps contra los 3 nombrados): la CC tiene razón en el hecho, pero ya contradice la letra del pedido. Releí los `gfx_plan_chNN.resolved.json` actuales:
- ch01: contador «6,500» y recorte del fact 4 «Aproximadamente 6,500 personas». Comparten cifra.
- ch02 y ch04: repiten el contador «6,500» de ch01. Es la 2.ª vez, así que cae por el dedupe de video.
- ch05: contador «500» y recorte «Más de 500 prisioneros». Comparten cifra.
- ch06: contador «650,000» y recorte del fact 6 con «650,000». Comparten fact y cifra.
- ch07: contador «6,500» y recorte «Aproximadamente 6,500 personas». Comparten cifra, y además es repetición de ch01.
- ch03: sin contador, no cambia.

Estas condiciones son consecuencia necesaria de las dos reglas que Omar mismo dictó (un fact = un bloque y dedupe a nivel video). Dejar ch02, ch04 y ch06 sin re-ensamblar deja un video final que viola esas reglas. No es un rediseño de la CC. Pero "solo ch01/ch05/ch07" es una restricción literal, y la CC la desbordó por su cuenta: lo anotó en B42, no consultó a Omar. Hay que reportarlo explícitamente a Omar como desvío del alcance, no como cumplimiento. Que re-ensamble ch02, ch04 y ch06 sin su visto bueno sería actuar fuera del pedido.

Fuera de alcance: ninguno nuevo en el fix. Cambios sin commitear: gfx_director.py, gfx_layer.py, test_module_gfx_director.py y DECISIONES_F2b.md (todos del fix) y diag_234_cap4.py (preexistente, ajeno).

Riesgos que el contrato no cubre:
- `counted_figures_before` lee los planes resueltos en disco. Si ch02 y ch04 no se re-ensamblan, o se re-ensamblan fuera de orden, el dedupe de ch07 depende de planes viejos y puede dar resultados distintos.
- Con 3 caps nombrados y 6 afectados, el AB de ch02, ch04 y ch06 no estará cubierto si se respeta el alcance literal.
```

Respuesta de CC: de acuerdo, es un desvío de alcance y no lo ejecuto sin el OK de Omar. El código está commiteado; el re-ensamble espera su respuesta (6 caps según la regla o solo los 3 pedidos).

### Re-ensamble con la regla nueva (OK de Omar: los 6 caps)

Re-ensamble incremental de ch01, ch02, ch04, ch05, ch06 y ch07; ch03 se reusó porque no tiene contador (`reassemble_regla_un_fact.log`, **29.2 min**: concat 65 s + música 18 s). El final y el AB anteriores quedaron en `_fase2b_work/_bak_f2b_premerge_v1/`.

**Entregables vigentes, 100 % regla nueva:**
- `…_final_gfx.mp4` (16:09): video 688.43 s / audio 688.52 s, ambos desde 0, decodifica sin errores.
- `AB_…_f2b.mp4` (16:11, generado sobre ese final): 1920×540, 688.5 s, con audio.
- Cues y revisión de los 7 caps en `lab/hyperframes/f2b/corrida_un_fact/`.

**Verificación de la regla** (`check_un_fact_un_bloque.py` → `.json`): **0 violaciones**. Ningún recorte comparte fact ni cifra con el contador de su cap, y cada cifra se anima como contador una sola vez.

- **«6,500» salía 4 veces como contador (ch01, ch02, ch04 y ch07); ahora sale 1 (ch01).**
  - En ch02 y ch04 el contador se cae. En ch04 el recorte de reemplazo no entró por solape → nada.
  - En ch07 el contador se cae y la cifra queda solo como recorte («Aproximadamente 6,500 personas»).
- Contadores del video: «6,500» (ch01), «500» (ch05) y «650,000» (ch06), una vez cada uno.
- Recortes que cambiaron de fact:
  - ch01: fact 4 («6,500») → fact 0, «El agua dentro de algunos edificios».
  - ch05: fact 7 («500») → fact 8, que ya tenía recorte → ch05 queda con 1.
  - ch06: fact 6 («650,000») → fact 7, que no entró por solape → ch06 queda con su otro recorte.
- **Recortes: 8, al menos 1 por cap** (ch02 tiene 2). Siguen repitiéndose entre caps «El agua dentro de algunos edificios» (ch01, ch03) y «Los prisioneros quedaron atrapados…» (ch02, ch06): deuda anotada.

| cap | bloques | recortes | énfasis / con ícono | zoom con box / sin | densidad s (máx hueco) | capa gfx s |
|---|---|---|---|---|---|---|
| ch01 | 7 | 1 | 1 / 1 | 1 / 1 | 6.0 (máx 8.8) | 102.2 |
| ch02 | 11 | 2 | 3 / 1 | 0 / 0 | 8.9 (máx 16.9) | 244.1 |
| ch03 | 16 | 1 | 5 / 1 | 0 / 1 | 9.6 (máx 17.7) | 341.7 (reusado) |
| ch04 | 13 | 1 | 4 / 2 | 1 / 0 | 9.4 (máx 17.3) | 291.6 |
| ch05 | 14 | 1 | 3 / 1 | 0 / 1 | 10.0 (máx 15.7) | 283.5 |
| ch06 | 13 | 1 | 1 / 1 | 1 / 0 | 8.4 (máx 17.2) | 246.2 |
| ch07 | 9 | 1 | 3 / 1 | 0 / 1 | 9.1 (máx 16.2) | 197.1 |

Densidad: 9.1 s promedio, hueco máximo de 17.7 s (máximo pedido: 18). Lint: 0 errores en los 6 caps re-hechos. 0 fallbacks.

Verificación visual (`tira_un_fact_ch01_ch07.jpg`): en ch01 a los 18 s está solo el contador «6,500», sin recorte; en ch07 a los 22.5 s está solo el recorte «Aproximadamente 6,500 personas», sin contador.

#### Veredicto revisor-handoff del re-ensamble (íntegro)

```
VEREDICTO: CUMPLE

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Los 6 caps re-hechos (ch01, 02, 04, 05, 06, 07) | OK | Log línea 62: "1 reusados, 6 re-hechos". ch01/02/04/05/06/07_gfx.mp4 con fecha 15:42-16:07; ch03_gfx.mp4 de 14:43 (reusado, no tiene contador). |
| 2 | Final posterior al re-ensamble | OK | final_gfx.mp4 16:09:31; segments_manifest 16:08; duración 688.515 s. |
| 3 | AB 100% regla nueva | OK | AB_..._f2b.mp4 16:11:33, posterior al final (16:09:31) y al log (16:09:31.85). El AB viejo (15:40, 77.8 MB) quedó en _bak_f2b_premerge_v1; el vigente es otro archivo (77.68 MB), 688.47 s. |
| 4 | Regla verificada | OK | check_un_fact_un_bloque.py: rc 0, "VIOLACIONES: ninguna". Contadores por cifra: 6500:1, 500:1, 650000:1. Contador de ch01 en 6,500 y recorte de ch07 con "Aproximadamente 6,500 personas". |
| 5 | Reporte anota "6,500" 4 veces como contador, ahora 1 | OK | F2b_REPORT.md:594 en adelante, sección "Re-ensamble con la regla nueva": "salía 4 veces como contador (ch01, ch02, ch04 y ch07); ahora sale 1 (ch01)". |
| 6 | Dato "antes 4" real | OK | Cues de corrida_premerge: count_up «6,500» presente en ch01 (11), ch02 (18), ch04 (22) y ch07 (11). En ch01 y ch02 había además una línea de callout omitido (solape) con la misma cifra, sin impacto. |
| 7 | Reporte actualizado | OK | F2b_REPORT.md modificado a las 16:12, posterior al AB. +33 líneas. Incluye tabla por cap, lint 0 errores y 0 fallbacks. |
| 8 | Parar tras el reporte | OK | No hay artefactos posteriores a las 16:12. Sin commit: HEAD = bd59bc7. |
| 9 | main intacta | OK | `git log -1 --format=%h main` = 43f528a. |

Fuera de alcance: ninguno atribuible a este trabajo. `git diff --stat` muestra solo F2b_REPORT.md (+33) y diag_234_cap4.py (preexistente, ajeno). Los ?? nuevos corresponden a la corrida: check_un_fact_un_bloque.py/.json, reassemble_regla_un_fact.log, report_data_f2b_un_fact.json y corrida_un_fact/.

Riesgos que el contrato no cubre: 1) La regla se verificó sobre planes y cues, no revisando el AB cuadro a cuadro; es consistente por fechas y log, no por inspección visual. 2) Siguen repitiéndose entre caps los recortes «El agua dentro de algunos edificios» (ch01, ch03) y «Los prisioneros…» (ch02, ch06); el reporte lo anota como deuda. 3) El ffprobe del AB combinado falló por mi sintaxis; las duraciones se midieron por archivo y sí coinciden (688.5 s).
```

Respuesta de CC al riesgo 1: la verificación visual de arriba (frames de ch01 y ch07) se hizo después del veredicto.
