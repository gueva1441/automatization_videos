# F29c — Rotulista por beat, sin cartel: la ficha es el title card · REPORTE

CC · 2026-10-26 (tanda nocturna, Omar duerme) · rama `f11-guion-v4`, base `d7fac3c`. Handoff `HANDOFF_F29c_rotulista_por_beat.md`; tanda `PROMPT_CC_tanda_nocturna_F29c_F30b_F31.md` (etapa 1).
Commits: **A `cc3f079`** · **B** = el commit de este reporte (arreglos de la coherencia y del revisor de A, runner, tabla, hoja, v4).
Costos de F29c: Claude **US$ 0.2336** de 1.5 (tope de la tanda: 2) · Gemini **US$ 0.0006** (crítico en el render) · ElevenLabs 0.

**En una línea:** el rotulista nuevo corre como pide el handoff y **v4 sale con 2 textos en todo el video** (ch06 D128 «1.910 personas», ch07 D32 «Dos habían muerto y uno se suicidó.»). Las reglas nuevas sacan casi todo: el beat pico de cada cap es 0 (y en 5 de 7 caps el pico es el beat más largo), y la regla «muere en el corte de escena + lectura a 15 cps» deja afuera 8 propuestas (las escenas duran ~10 s y el modelo no ve los cortes). Las medidas de B.4 dan todas 0. **`a_pantalla` 1/5.**

## Para Omar (pendientes, no decididos)
1. **Dos `a_pantalla` en el mismo beat** (D128 y D192, ch06 beat 11 `respiro`): con «1 texto por beat» queda uno (D128); el handoff pide a la vez «se quedan» (A.7) y 5/5 (B.3). Apliqué el máximo de §0. ¿Excepción para `a_pantalla`?
2. **«Sin tiempo de lectura» por el corte de escena**: es la causa n.º 1 de pérdida (8 de 16 propuestas; D117, Q50 y D245, tres `a_pantalla`, caen por esto). El rotulista no recibe los cortes de escena (no están en el prompt de A.5, que no se toca). Opciones: pasarle los cortes, o dejar que el bloque arranque en el corte siguiente si no cabe (hoy A.5 solo deja «esperar» por zona, no por lectura).
3. **El beat pico de cada cap = el de `pico_cap`** (uno por cap, también en caps sin función «pico», como el prompt pide con `{pico_beat}`): en ch01 el único beat (gancho) es el pico → 0 textos; en ch02–ch07 el beat más intenso queda vacío.
4. **Etiqueta de `hecho` con el año de la fuente**: D117 salía como «Aprobación del proyecto, 2018» (2018 es el año del libro, no de la aprobación; el candado lo deja pasar porque 2018 está en la fuente). No llegó a pantalla (lectura), pero el prompt lo induce.

## A — Reglas (`cc3f079`)
| archivo | qué |
|---|---|
| `script_engine/gfx_rotulista.py` | prompt literal de A.5; `oraciones` con la palabra numerada; `beat_de_oracion`; `validar` (anclaje, forma, candado, tiempos A.2, no dicho / spoiler A.3, coherencia A.4); `finalizar` (A.1); `colocar` (ficha / recorte / cita / lupa); `escena_final` (§0 animaciones y §A.5 zona); `primer_json` (A.6.1) |
| `script_engine/gfx_project.py` | `tc_metrics` (medidas del title card en un solo lugar), `ficha_medida` (líneas con la fuente Anton real), `ficha_html` (el title card con id propio, sin `#tc-dim`; con dato en 2 líneas la raya baja una línea con la misma cuenta del CSS); `cue_events` etiqueta «ficha» |
| `gfx_templates/title_card.html.tmpl`, `gfx_common.css` | el template toma id, inicio, `dim_html` y estilo de la raya; el CSS pasa de `#tc-*` a clases `.tc-*` (mismos valores, ningún tamaño ni color nuevo) |
| `script_engine/gfx_critic.py` | crítico del rotulista con `por_que` (solo `a_pantalla`), `aporta` y una 3.ª pregunta «estorba»; `pasa_rot`: sale por (2) o por estorba; por (1) solo si no es `a_pantalla`; la voz = oración ancla ± 1 (versión `f29c-1`) |
| `gfx_layer.py`, `gfx_realizador.py`, `gfx_pool.py` | cableado (voz del video, validación con escenas en `colocar`, `cerrar(escena=…)`), `TICKER_MIN` = el 2.0 que ya existía |

**Prompt nuevo, literal del handoff (SYSTEM + "\n\n" + USER): md5 `7dafbb964d7ff71daafc65c028834017`** (test `test_prompt_literal_del_handoff_f29c` lo compara contra el .md). El de F29b (`50e6ae74…`) queda nombrado en el código.

### Cómo quedó cada punto
- **A.1** por beat de la oración ancla: `a_pantalla` primero, después `rank`, después la oración; queda 1. Beat pico → 0. Gancho → a lo sumo 1 (es el mismo tope). Un `a_pantalla` anclado en el beat pico pasa al primer renglón del beat siguiente (palabra 0) si su ítem es de ese beat; si no, se anota.
- **A.2** `t0` = inicio de la palabra `word_idx`; `t1` = fin de la oración, o de la siguiente si no alcanza `caracteres ÷ 15`; nunca después del corte de escena; si no alcanza, «sin tiempo de lectura» (no se acorta). En el prefetch (sin escenas) no se corta en la escena; `colocar` revalida con las escenas reales.
- **A.3** números, nombres propios y años del dato contra la oración ancla ± 1 (no dicho) y contra las oraciones posteriores del cap (spoiler).
- **A.4** coherencia contra la voz de los 7 caps (texto de la narración = el de los subtítulos remapeados).
- **A.5** cifra, hecho, persona → ficha (kicker = etiqueta en mayúsculas como el «CAPÍTULO N», título = dato; posición, tamaño, raya, wipe y fundido del title card; z 21; sin oscurecer); documento → `archive_clipping`; cita → `quote_card`; lupa → `evidence_zoom`. Largo = que quepa (kicker 1 línea, dato ≤ 2), medido con Anton a 2560.
- **A.6** (1) primer objeto JSON válido de la respuesta (las 4 crudas de ch01 de F29b, que fallaban con «Extra data», parsean: test con fixture). (2) crítico como arriba. (3) tope y costo en vuelo como en `7e704de`.
- **Una cosa por escena (§0 + §A.5, `escena_final`)**: fijos el title card (todas las escenas que pisa en sus 3 s) y el sello del pico; recorte/cita esperan a la escena siguiente del beat si la suya está ocupada (la lupa no se mueve); el reloj no va encima de un texto ni en el beat de otra animación (si su beat tiene sello o lupa, no va; si choca, arranca en la escena siguiente del beat, sin pasar un cambio de fecha y con ≥ 2 s); la ficha espera si en su escena hay title card, reloj, sello u otro bloque.

### Lecturas de CC (declaradas)
1. «Caracteres del bloque» = etiqueta + dato (+ autor en citas).
2. **Coherencia**: la cifra de la voz se compara si tiene la misma unidad y su oración nombra la misma magnitud que el bloque (nivel/cota, altura, muertos), o si no tiene unidad y viene después de esa magnitud («la cota autorizada fue de setecientos quince»). Una diferencia («15 metros por encima de la cota») no se compara. *En B se sacó una regla mía del commit A* (misma unidad, sin magnitud, mismos dígitos): daba falsos positivos (D106 «15 m por encima de la cota» contra la ola de 20 m; D245 contra la oferta de ENEL en liras). El caso del handoff sigue cayendo: 720 contra los 700 y 650 m «sobre el nivel del mar» y la cota de 715 de ch04 (el «setecientos metros» de ch05 no nombra la magnitud y ya no se compara).
3. Se mantiene de F29b que el ítem tiene que ser del beat de su oración (la «compuerta» del `a_pantalla` que pasa del pico al beat siguiente depende de eso), y la excepción del spoiler de nombres: un nombre que la voz ya dijo antes del ancla no es spoiler (sin eso, cualquier nombre repetido en el cap sería spoiler).
4. La «persona» queda exenta de «no dicho» por su nombre (la voz la nombra en esa oración: es la compuerta del tipo).
5. El crítico mira la oración ancla ± 1 (la unidad nueva de «no dicho») en lugar de ±20 s.

### Tests y verificaciones de A
`test_module_f29c_rotulista.py` (15: prompt literal; 1 por beat y 0 en el pico con la fixture de ch06; `a_pantalla` del pico al beat siguiente; gancho; arranque en `word_idx`; fin en oración / siguiente / corte; sin tiempo de lectura; no dicho por vecinas; spoiler por posterior; coherencia 720/700/715 + diferencia + liras; ficha con kicker y título y sin `#tc-dim`; ficha que espera al title card y al reloj; reloj que no va encima de un recorte; las 4 crudas; D245 pasa el crítico) + `test_module_f29b_rotulista.py` adaptado al esquema nuevo (17). Suite amplia **958 verdes + 5 previas** (01b_pauses ×3, m03_merge_timing ×2), suite rápida 58, md5 `--only-cap ch02` sin `--gfx` (`--sw-encode`) **`38e5ba14…`** (`a/`).

## B — Vajont v4 completo
Sobre `f8s3-vajont-f30` (ya cocido por F30). `b/f29c_vajont.py`:
- `prefetch`: el rotulista de los 7 caps en paralelo, **15.1 s** de pared, 12 llamadas (7 + 5 reintentos), **US$ 0.2336** (las crudas de F29b quedaron como `rotulista_chNN.f29b.raw.json`; el ledger de F29b como `rotulista_costos.f29b.json`).
- `render`: `fase2b --keep-segments --reuse-visuals --gfx --gfx-sparse --gfx-quality looks --rotulista`, en fila, Firefox cerrado y RAM libre 19.3 GB antes (mín. 15.1 durante). **rc 0, pared 30.9 min** (v3b: 37.1), gfx 1 577 s = 26.3 min en total. Salida **`output/f8s3-vajont-f30/f8s3-vajont_final_gfx_v4.mp4`** (1 009.7 s, 993 MB). El rotulista salió de caché en el render (0 llamadas nuevas). Evidencia copiada en `b/v4/` (planes resueltos, logs de gfx, crudas, beats, ledger).

### Tabla por cap (B.3; `b/medidas.json`)
| cap | beats (pico) | textos por beat | animaciones por beat | propuestos | fuera: cantidad · lectura · no dicho · spoiler · coherencia · zona · contenido | cortó el crítico | en pantalla | Claude US$ | gfx s |
|---|---|---|---|---|---|---|---|---|---|
| ch01 | 1 gancho (pico) | 1:0 | 1: sello | 0 | — | 0 | 0 | 0.011 | 107 |
| ch02 | 2 planteo · 3 escalada (pico) | 0 · 0 | 0 · sello | 1 | 0 · 1 · 0 · 0 · 0 · 0 · 0 | 0 | 0 | 0.036 | 237 |
| ch03 | 4 giro (pico) · 5 escalada | 0 · 0 | 0 · 0 | 3 | 1 · 2 · 0 · 0 · 0 · 0 · 0 | 0 | 0 | 0.039 | 195 |
| ch04 | 6 giro · 7 giro (pico) | 0 · 0 | reloj · 0 | 4 | 0 · 1 · 0 · 0 · 0 · 0 · 3 (candado) | 0 | 0 | 0.039 | 200 |
| ch05 | 8 escalada (pico) · 9 giro | 0 · 0 | sello · 0 | 2 | 0 · 1 · 0 · 0 · 0 · reloj · 0 | 1 (T61) | 0 | 0.041 | 302 |
| ch06 | 10 pico (pico) · 11 respiro | 0 · 1 | sello · 0 | 3 | 1 · 1 · 0 · 0 · 0 · 0 · 0 | 0 | **1** (D128) | 0.023 | 324 |
| ch07 | 12 revelación (pico) · 13 cierre | 0 · 1 | sello · 0 | 3 | 0 · 2 · 0 · 0 · 0 · reloj · 0 | 0 | **1** (D32) | 0.046 | 212 |
| **total** | | | | **16** | **2 · 8 · 0 · 0 · 0 · 2 relojes · 3** | **1** | **2** | **0.234** | **1 577** |
(«zona» en ch05 y ch07 es el reloj, que sale porque su beat ya tiene el sello del pico; ningún texto salió por zona. «contenido» = candado: T33 y T39 con un año que no está en la fuente, D104 con «Univ.». En la validación del prefetch, sin escenas, salían además D106 y D245 por coherencia —antes del arreglo— y Q50 por «no dicho»: «Erto y Casso» en la oración vecina; con las escenas, Q50 cae antes por lectura.)

| cap | tipo | en pantalla | pool_id | beat · oración · palabra | t0 en el cap | t en el mp4 | crítico |
|---|---|---|---|---|---|---|---|
| ch06 | cifra (ficha) | MUERTOS EN EL DESASTRE DEL VAJONT (RECUENTO OFICIAL) · 1.910 personas | D128 | 11 · 24 · 2 «muertos» | 124.3–133.8 s | 781.6 s | sí · sí · no estorba |
| ch07 | hecho (ficha) | ACUSADOS · Dos habían muerto y uno se suicidó. | D32 | 13 · 16 · 5 «ocho» | 112.5–120.6 s | 938.2 s | sí · sí · no estorba |
| ch05 | persona (ficha) — **cortada** | DIRECTOR · Alberico Biadene | T61 | 9 · 14 · 5 | 92.5 s | 579.9 s | (2) NO: «la narración ya identifica a Alberico Biadene como el director técnico» |

**`a_pantalla` 1/5**, con el motivo exacto de cada faltante:
- **D128** sale (ch06).
- **D192** (ch06): «cantidad: un texto por beat: el beat 11 ya tiene D128» (pendiente 1).
- **D117** (ch02): «sin tiempo de lectura: 82 caracteres piden 5.5 s y hay 3.4 s hasta el corte de escena (21.6 s)».
- **Q50** (ch05): «sin tiempo de lectura: 247 caracteres piden 16.5 s y hay 10.9 s hasta el corte de escena (27.8 s)».
- **D245** (ch07): «sin tiempo de lectura: 63 caracteres piden 4.2 s y hay 2.4 s hasta el corte de escena (132.3 s)».

### Lo que mide CC (B.4) — todas en 0
Muñones **0** · cifras sin etiqueta **0** · textos en el beat pico **0** · dos bloques en la misma escena **0** · bloque que cruce un corte de escena **0** · contradicciones de cifra **0** (sobre los 2 en pantalla). El «cumplen (a)(b)(c)» lo cuenta el analista con la hoja.

### Hoja `BLOQUES_v4.jpg` (+ `BLOQUES_v4.json`, cuadros a 2560 en `_BLOQUES_v4/`)
Un renglón por bloque en pantalla y uno por bloque cortado por el crítico: cuadro del mp4 entero en t + 1 s (a 1280 en la hoja), miniatura de 360 px, voz −1 / ANCLA / +1 oración, `aporta`, crítico (3 preguntas), cap · beat · tipo · pool_id · oración · palabra, t0 en el cap y **t en el mp4 entero = offset del cap en `_concat_video.ts` + t0 + 2.5 s** (la intro de fase2b clona el primer cuadro 2.5 s: es el +2.5 de la fórmula; los offsets de los caps descuentan las transiciones entre caps de v4). Forma que se ve (va a F31): el kicker de D128 es largo y a 360 px no se lee; la ficha de D32 pasa cerca de la cabeza del hombre (el crítico dijo «no estorba»).

## Costos y tiempos
Claude US$ 0.2336 (rotulista, 12 llamadas) de 1.5 · Gemini US$ 0.0006 · pared del render 30.9 min (v3b 37.1) · rotulista en paralelo 15.1 s.

## Veredicto del revisor-handoff de la parte A (íntegro)
Ver `a/veredicto_revisor_A.md` (pegado acá abajo, sin resumir).

VEREDICTO: CUMPLE CON OBSERVACIONES

Revisé el commit cc3f079 (base d7fac3c), parte A. El árbol de trabajo está sucio con cambios posteriores al commit en `script_engine/gfx_rotulista.py` y `test_module_f29c_rotulista.py`; parecen de la parte B, que ya empezó (`lab/hyperframes/f29c/b/`). Por eso extraje el commit con `git archive` a una carpeta temporal y corrí ahí los tests: 32 pasan. A esa copia le agregué `config.py` y `gsap.min.js`, que son archivos del entorno y no están en git.

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Prompt SYSTEM/USER literal de A.5, md5 7dafbb96… | OK | Extraje los dos bloques del .md y comparé con `ROTULISTA_SYSTEM` y `ROTULISTA_USER` (`gfx_rotulista.py:56-95`): iguales. `prompt_md5()` da 7dafbb964d7ff71daafc65c028834017. El test `test_prompt_literal_del_handoff_f29c` lo vuelve a comprobar. |
| 2 | A.1: 1 texto por beat, 0 en el pico, `a_pantalla` primero y después `rank` | OK, con nota | `finalizar` (`:668`). El `a_pantalla` del pico pasa al beat siguiente si su ítem es de ese beat (`validar :548-553`). Ver observación 1. |
| 3 | A.2: arranque en `word_idx`, fin según oración / siguiente / corte de escena, lectura a 15 cps, «sin tiempo de lectura» sin acortar | OK | `tiempos` (`:488`), `LECTURA_CPS` (`:50`). Tests de arranque, fin y lectura. |
| 4 | A.3: no dicho por oración ancla ± 1, spoiler por posteriores | OK, con nota | `validar :620-635`. Ver observación 2. |
| 5 | A.4: coherencia de cifras con la voz de los 7 caps | PARCIAL | El caso 720/700/715 pasa. La regla (2) del commit (misma unidad, sin magnitud, mismos dígitos) da falsos positivos. En el commit, «15 metros por encima de la cota» contra «ola de veinte metros» da «15 m vs 20 m». Ver observación 3. |
| 6 | A.5: la ficha es el title card, sin `#tc-dim` | OK | `ficha_html`, `ficha_medida`, `tc_metrics` en `gfx_project.py`; el template usa `${dim_html}` y `${tid}`. `data_callout` ya no se usa para el rotulista (`colocar :906`). |
| 7 | A.5: mapeo a pantalla | OK | `colocar :906-932`: cifra, hecho y persona van a la ficha; documento a `archive_clipping`; cita a `quote_card`; lupa a `evidence_zoom`. |
| 8 | A.5: la ficha espera si hay reloj o title card en la escena | OK | `escena_final :969-1126` y dos tests. |
| 9 | A.6.1: primer JSON válido, probado con las 4 crudas de ch01 | OK | `primer_json` (`:720`), fixture nuevo y test. |
| 10 | A.6.2: el crítico recibe `por_que` y `aporta`; un `a_pantalla` no se corta por la pregunta 1 | OK | `gfx_critic.pasa_rot` y `build_prompt_rot`; test D245. |
| 11 | A.6.3: tope y costo en vuelo como en `7e704de` | OK | `test_tope_cuenta_las_llamadas_en_vuelo` pasa. |
| 12 | A.7: tests sin red y suites | OK | Los 32 tests pasan en el commit. El log de la suite amplia (`lab/hyperframes/f29c/a/suite_amplia.log`) dice 958 pasan + 5 previas. Las 5 son las mismas de F29b: 01b_pauses ×3 y m03_merge_timing ×2; las corrí y fallan igual, y ningún archivo del commit las toca. Además, 478 tests de f1x–f5x pasan, corridos sobre el árbol sucio. No pude reproducir la suite amplia completa: varios archivos usan `sys.exit` al importar y pytest lo rechaza. |
| 13 | md5 de ch02 sin gfx igual a 38e5ba14… | OK | `md5sum` del `ch02_segment_only.mp4` da 38e5ba14e3d24fd20f9297c9e1dfee24. |
| 14 | Frenos: no se tocan prompts de guion/escaleta/ficha, `.env`, `config.py`, `gfx_profiles`, `lab/_gpt_probe_analista` | OK | `git diff --name-only d7fac3c cc3f079` solo lista `script_engine/gfx_*` (críticos, layer, pool, project, realizador, rotulista, 2 templates), 2 tests, y archivos de `lab/hyperframes/f29c`. El commit no toca sellos, transiciones, subtítulos ni m03. El CSS solo cambia selectores de id a clase, sin valores nuevos. |
| 15 | Números nuevos fuera de la tabla §0 | PARCIAL | Ver observación 4. |

Observaciones
1. Los dos `a_pantalla` de ch06, D128 y D192, caen en el mismo beat 11 (`respiro`). Con «1 por beat» solo queda uno: el test confirma que D192 sale por «cantidad». El handoff dice «se quedan» (A.7) y pide `a_pantalla` 5/5 (B.3). Las dos cosas no pueden cumplirse a la vez; Omar debería decidir antes de leer la parte B. El «beat pico» de CC es el de `pico_cap`: uno por cap, también en caps sin función «pico». En el fixture de ch06 el beat pico cubre de 0.14 a 109 s, casi todo el cap, y ahí no sale ningún texto. Esa lectura es coherente con `{pico_beat}` del prompt, pero el handoff no la dice.
2. El spoiler de nombres propios conserva una excepción heredada de F29b: no cuenta como spoiler un nombre que la voz ya dijo antes (`:632`). El handoff define spoiler como «cualquier oración posterior». Esa excepción no figura entre las lecturas que me pasaron.
3. Después del commit, CC ya está cambiando la regla de coherencia en el árbol sin commitear: quita la regla de «mismos dígitos» y agrega `_DIFERENCIA`. El commit que pedí revisar tiene el defecto de la fila 5. Antes de dar por buena la parte A, hay que confirmar que el arreglo entra al commit de la parte B.
4. Números sin hueco en §0:
   - tolerancia 0.05 s en `oracion_en`;
   - `word_idx = 0` al mover un `a_pantalla` del pico al beat siguiente;
   - la regla de «mismos dígitos» (observación 3);
   - ancho 2560 fijo por defecto en `ficha_medida`, en vez del ancho real de render;
   - `rank` por defecto 99.
   Ninguno está anotado como «pendiente de Omar». `TICKER_MIN = 2.0` conserva el valor que ya existía; 0.3, 4 letras y 16 000 también ya estaban.
5. `lab/ESTADO_SESION.md` no se actualizó en este commit, y CLAUDE.md pide hacerlo en cada hito. `F29c_REPORT.md` tampoco existe todavía, así que las lecturas «declaradas» solo están en docstrings.

Fuera de alcance: ninguno en el commit. Entraron los dos .md de contrato, los logs de `lab/hyperframes/f29c/a` y el fixture de las 4 crudas, todo dentro de f29c.

Riesgos que el contrato no cubre
- `escena_final` marca como ocupada solo la escena que contiene el t=0 del title card, que dura 3 s. Si esa escena dura menos de 3 s, una ficha o un reloj podrían quedar sobre el title card.
- La validación de la ficha se hace con un ancho de 2560 px fijo. Si el render usa otro ancho, la medida de líneas no coincidiría con lo que se dibuja.

**Después del veredicto de A (CC):** obs. 3 (regla de coherencia «mismos dígitos»): sacada en B, con tests de los dos falsos positivos. Obs. 4: la tolerancia de 0.05 s salió; el `rank` que falta va después de todos los que lo traen (antes 99); el title card ocupa todas las escenas que pisa en sus 3 s (riesgo 1); `word_idx = 0` al mover un `a_pantalla` es la primera palabra del beat siguiente (no es un número de ajuste); el ancho 2560 de `ficha_medida` es el del render de este canal (pendiente si cambia el ancho). Obs. 1 y 2: declaradas arriba (pendiente 1 y lectura 3). Obs. 5: ESTADO actualizado y este reporte.

## Veredicto del revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

Los números del reporte coinciden con `b/medidas.json`, `b/v4/*` y los logs de gfx. Hay cuatro observaciones, ninguna cambia las cifras (detalle abajo).

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | B.1 v4 existe, render completo con los flags pedidos | OK | `ffprobe` da 1009.667 s, 2560x1440, h264+aac, 1 041 232 518 bytes (993 MiB). `render_v4.json` da rc 0 y pared 30.9 min. El runner llama a `fase2b` con `--reuse-visuals --gfx --gfx-sparse --rotulista`. RAM libre 19.3 GB, mínimo 15.1. |
| 2 | Costos | OK | `rotulista_costos.json`: 12 llamadas, suma 0.2336. Por cap coincide con la tabla (0.0112, 0.0356, 0.0389, 0.0389, 0.0406, 0.0228, 0.0456). Gemini 0.0006 está en `render_v4.out`. Paralelo 15.1 s en `prefetch.json`. |
| 3 | Tiempos de gfx y pared | OK | Los 7 caps suman 1576.7 s (el reporte dice 1 577). Coinciden con `render_v4.out` y `medidas.json`. Pared 30.9 contra v3b 37.1, que consta en `lab/ESTADO_SESION.md`. |
| 4 | Tabla por cap (B.3) | OK | Revisé propuestos 16, cantidad 2, lectura 8, candado 3, cortados por el crítico 1, en pantalla 2. Suman 16. Coinciden con los `rotulista: colocados/fuera` de `gfx_chNN.log` y con las crudas. Los beats pico salen de los logs y de `gfx_beats_chNN.json`. «En 5 de 7 caps el pico es el beat más largo» es cierto. |
| 5 | `a_pantalla` 5/5 o motivo exacto de cada faltante | OK | Hay 1 de 5. Los motivos de D117, Q50, D245 y D192 son textuales de `medidas.json` y de los logs. Los números de lectura cierran (82/15=5.5, 247/15=16.5, 63/15=4.2). |
| 6 | B.4 medidas | OK, con nota | Todas dan 0. D128 (123.87–134.57) y D32 (110.80–121.50) caen dentro de su escena y no la cruzan. Nota: «contradicciones» llama a la misma función que se prueba. «dos en escena» solo cuenta bloques del rotulista, y hay 1 por cap. Cumple, pero es una medida débil. |
| 7 | B.2 hoja `BLOQUES_v4.jpg` | PARCIAL | Existe (963 KB) y la vi como imagen. Tiene cuadro, miniatura de 360 px, `aporta`, crítico, beat y t en el mp4. Los t se verifican: 654.799+124.3+2.5=781.6, 823.199+112.5+2.5=938.2 y 484.899+92.5+2.5=579.9. Los cuadros muestran la ficha en esos t. La fila de T61 (cortado) dice «beat None · oración [None]» y trae «−1 / ANCLA / +1» todos en «—». El crítico de D32 está truncado («…relevante en la»). El título de D128 se corta en el borde. |
| 8 | Fixes de coherencia y de las obs. de A en `gfx_rotulista.py` | OK | La regla de «mismos dígitos» salió y entró `_DIFERENCIA`. La tolerancia de 0.05 s salió. El rank sin valor pasa a `len(bl)+1`. El title card marca todas las escenas que pisa. Los tests nuevos están en `test_module_f29c_rotulista.py:183-185`. |
| 9 | Tests | OK | En el árbol actual, 32 pasan (F29c + F29b). Armé una copia de HEAD con solo los 6 hunks de B de `gfx_rotulista.py` (sin los 3 de `pre_roll`) y el test nuevo, y también dan 32. Hizo falta copiar `gsap.min.js`, que no está en git. Los hunks de `pre_roll` están separados de los de B, así que el staging parcial es posible. |
| 10 | Pendientes de Omar y lecturas declaradas | OK | Hay 4 pendientes: `a_pantalla` en el mismo beat, lectura por corte de escena, pico por cap y etiqueta con año. Las lecturas 1–5 están declaradas en el reporte. No hay números nuevos fuera de §0 en lo de B. |
| 11 | `lab/ESTADO_SESION.md` | PARCIAL | El diff dice «F29c B: render v4 en curso». Es falso, el render terminó. Falta el hito de B y la PARADA. |
| 12 | Frenos (sellos, templates, `.env`, `output/`) | OK | B no toca `gfx_templates`, `output/` ni `config.py`. `output/` no aparece en `git status`. |

Observaciones para antes del commit y la lectura de Omar:
1. Actualizar `lab/ESTADO_SESION.md` con el resultado de B (fila 11).
2. La hoja no trae voz ni beat para T61. Si el contrato exige voz por fila, falta eso (fila 7).
3. D32 «uno se suicidó» repite lo que dice la oración −1 de la voz («Pancini… se quitó la vida»). Eso toca la condición (a) del prompt. El código solo chequea números, nombres y años, y el crítico lo dejó pasar. Lo tiene que juzgar el analista con la hoja.
4. La lista de lo que salió en la validación del prefetch omite D245. En `rotulista_ch07.raw.json` D245 aparece rechazado por coherencia con el código viejo, no por lectura como en el render.

Fuera de alcance: ninguno dentro de B. En el árbol hay cambios de F30b (`gfx_style`, `gfx_sparse`, `gfx_project`, `transition_applier`, `fase2b`, `gfx_layer`, `gfx_critic`, `gfx_config`, `test_module_f30b.py`, `lab/hyperframes/f30b/`) y los `gfx_profiles/*` y `diag_234_cap4.py`. Ninguno debe entrar al commit de B. Mientras no se haga el staging por hunks, los 3 hunks de `pre_roll` de `gfx_rotulista.py` quedan sin commitear.

Riesgos que el contrato no cubre:
- Los archivos de F30b se editaron entre las 03:33 y las 03:39, y el render corrió de 03:28 a 03:58. Los módulos ya estaban cargados y los cuadros de la hoja coinciden con lo esperado. Aun así, v4 no es reproducible bit a bit desde el commit de B.
- El tipo `persona` tiende a cortarse por el crítico (T61 salió por la pregunta 2: «ya identifica al director»), porque el prompt le pide justo nombrar a quien la voz ya nombra. Con la regla actual es casi seguro que se corte siempre.

Rutas: `C:\CLAUDE_PROJECTS\automatization_videos\lab\hyperframes\f29c\F29c_REPORT.md`, `C:\CLAUDE_PROJECTS\automatization_videos\lab\hyperframes\f29c\b\medidas.json`, `C:\CLAUDE_PROJECTS\automatization_videos\lab\hyperframes\f29c\BLOQUES_v4.jpg`, `C:\CLAUDE_PROJECTS\automatization_videos\output\f8s3-vajont-f30\f8s3-vajont_final_gfx_v4.mp4`.

**Después del veredicto (CC):**
- Obs. 1: ESTADO actualizado con el resultado de B y la etapa siguiente.
- Obs. 2: la fila de T61 sale del registro del crítico, que no guarda oración ni beat (el bloque ya no está en el plan): queda así; su voz está en el log (`b/v4/gfx_ch05.log`). El crítico de D32 y el kicker de D128 se cortan en el renglón de texto de la hoja: los textos completos están en `BLOQUES_v4.json`.
- Obs. 3: para el analista (la regla del código no mira cláusulas; la (a) del prompt sí).
- Obs. 4: corregido arriba: en el prefetch D245 salía por coherencia con la regla vieja (antes del arreglo); con la regla nueva y las escenas, por lectura.
- Riesgo 1: v4 corrió con el código de A + los arreglos de B ya cargados (los archivos de F30b se editaron después de que el proceso los importó); el commit de B deja el código con que corrió.
- Riesgo 2 (persona): pendiente de Omar, con el pendiente 3 de arriba.
