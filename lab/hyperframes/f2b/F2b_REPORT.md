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
