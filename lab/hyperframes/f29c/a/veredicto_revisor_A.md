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
