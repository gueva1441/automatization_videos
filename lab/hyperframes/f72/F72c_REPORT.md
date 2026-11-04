# F72c — guion de pantalla F72b aprobado y render de Wittenoom con gfx (sin packaging)

Handoff: `lab/hyperframes/f72/HANDOFF_F72c.md` (md5 `7761839fa98af4bea9bf5083d017a43f`, verificado con md5sum). Topic `123bbb64-9fca-4395-8bf4-57d60e219ef1`, rama `f11-guion-v4`. Decisión de Omar del 2026-11-03 21:05 («si dale perro»). No toqué código, prompts ni main. No corrí `--plan-edit`, `--plan-only` ni fase3. No borré ningún `_fase2b_work_desfasado_*`.

## Resultado en una línea

El guion quedó aprobado y `run_pipeline --batch` arrancó en «render». Terminó con exit 0 en 21 min 05 s y US$ 0. Salió `<tid>_final_gfx.mp4`: 824,37 s, 2560×1440, 30 fps, los 7 caps con gfx y ninguno en el fallback. El packaging quedó diferido; `etapa_de` = `packaging`. Hay un ✗ de costura en ch07: al segmento le falta un cuadro.

## Etapa 0 — solo lectura (todo OK, se siguió)

| verificación | esperado | en disco | ok |
|---|---|---|---|
| `etapa_de(tid)` | `aprobar_guion` | `('aprobar_guion', 'el guion de … no está aprobado …')` | ✓ |
| md5 `GUION_PANTALLA.md` | `6b2b9944…` | `6b2b9944d70efa89796bb0516172ebde` | ✓ |
| `fondos.json` papel_md5 | `39c99927…` = papel aprobado | `{"papel_md5": "39c99927c5d95fad16a3ecf062661f0b"}`; `01e_pantalla.json` aprobado = `{'por': 'Omar', 'fecha': '2026-10-31T23:04', 'md5': '39c99927c5d95fad16a3ecf062661f0b'}` | ✓ |
| 15 visuales de `_fase2b_work/` con mtime ≥ 2026-11-03 19:37 | sí | sí: van de 19:42:52 a 20:14:30 (tabla abajo) | ✓ |
| `ch01_hybrid_visual.mp4` | `b976a42b…` | `b976a42b1b8672408ee0daac1fa83872` | ✓ |
| `ch07_hybrid_visual.mp4` | `1a343b14…` | `1a343b14d944ba5ae8c3bcdc0865a08b` | ✓ |

| md5 | mtime | archivo |
|---|---|---|
| 9ba8b4bd8a2e4241096d5f81d8a81f66 | 2026-11-03 19:42:52 | ch01_flux_supp.mp4 |
| b976a42b1b8672408ee0daac1fa83872 | 2026-11-03 19:43:27 | ch01_hybrid_visual.mp4 |
| 2e3d431aec616b6b3acade6e1f00cc01 | 2026-11-03 19:46:29 | ch02_flux_visual.mp4 |
| 68accca4693b165701c08253faaaf495 | 2026-11-03 20:14:01 | ch02_visual_preroll.mp4 |
| 38b72aaa14d4be2a24d8a67b968929de | 2026-11-03 19:52:18 | ch03_flux_visual.mp4 |
| e232573dd442954f474f9a436eb7ffc9 | 2026-11-03 20:14:30 | ch03_visual_preroll.mp4 |
| e4632a9a707af1c352f05f0bf5743bba | 2026-11-03 19:56:51 | ch04_flux_visual.mp4 |
| 9d0277d290bdeaedf5e501a9af10e212 | 2026-11-03 20:13:58 | ch04_visual_preroll.mp4 |
| a9882d3eef300bc2fbe27d5badcba278 | 2026-11-03 20:00:53 | ch05_flux_visual.mp4 |
| 1e5c5a164572d61e6717ef65b93a5fbc | 2026-11-03 20:14:16 | ch05_visual_preroll.mp4 |
| a1681ed4e76ecfa3d72d249ca3579ff8 | 2026-11-03 20:05:14 | ch06_flux_visual.mp4 |
| 813fa74323735ac8c1358aa8467c2026 | 2026-11-03 20:14:15 | ch06_visual_preroll.mp4 |
| 182764b244958cea0c40b4ffd49b52aa | 2026-11-03 20:08:42 | ch07_flux_supp.mp4 |
| 1a343b14d944ba5ae8c3bcdc0865a08b | 2026-11-03 20:10:01 | ch07_hybrid_visual.mp4 |
| b662ae18da08dcd37120e651d9d25411 | 2026-11-03 20:13:54 | ch07_visual_preroll.mp4 |

ch01 no tiene `_visual_preroll` y no hay ninguno en el disco; ningún visual tiene mtime anterior a 19:37.

DECISIONES.md: agregué la línea de Omar del 2026-11-03 21:05. Lleva el texto de «Decisión» del handoff y la chascada para F73: el chequeo «inicio de música por cap» ignora los tramos en silencio digital.

## Etapa 1 — `fase2b.py <tid> --aprobar-guion "Omar 2026-11-03"`

```
  ✔ guion de 123bbb64-9fca-4395-8bf4-57d60e219ef1 aprobado por Omar (2026-11-03) · md5 de los planes 05cad6e8204d7309353d3bb08377cc78
exit 0
```

`GUION_PANTALLA.json` no tiene la clave `aprobacion` (da `None`). La aprobación queda en `aprobado`:

```
{'por': 'Omar', 'fecha': '2026-11-03', 'md5_planes': '05cad6e8204d7309353d3bb08377cc78', 'planes': ['gfx_plan_ch01.resolved.json', 'gfx_plan_ch02.resolved.json', 'gfx_plan_ch03.resolved.json', 'gfx_plan_ch04.resolved.json', 'gfx_plan_ch05.resolved.json', 'gfx_plan_ch06.resolved.json', 'gfx_plan_ch07.resolved.json']}
```

`GUION_PANTALLA.md` sigue en `6b2b9944…` después de aprobar. `etapa_de` pasó a `('render', 'guion aprobado por Omar (2026-11-03), planes 05cad6e8…; falta …_final_gfx.mp4')`.

## Etapa 2 — `run_pipeline.py --topic <tid> --batch`

Con la venv y sin `QA_FORM`. Arranque y cierre, textuales:

```
  ⏵ 123bbb64-9fca-4395-8bf4-57d60e219ef1: arranca en «render» — guion aprobado por Omar (2026-11-03), planes 05cad6e8…; falta …_final_gfx.mp4
  ▶ RENDER (fase2b --gfx --gfx-sparse) — 123bbb64-9fca-4395-8bf4-57d60e219ef1
  Fases corridas: render, packaging (diferido)
  ✅ Cadena completa.
  📦 LISTO PARA PACKAGING → python fase3.py 123bbb64-9fca-4395-8bf4-57d60e219ef1
exit 0
```

Arrancó en `render`, así que no lo maté. No corrí fase3. Los flags son los de `RENDER_FLAGS` (`--reuse-visuals --keep-segments --gfx --gfx-sparse`): reusó los 15 visuales de la etapa 0 («reuse-visuals: chNN_*_visual.mp4 (sin DepthFlow)» en los 7 caps) y no los volvió a cocer.

## Etapa 3 — salida

**Corrida:** exit 0 · 21:08:14 → 21:29:19 (**21 min 05 s**) · tracker `Costo total: $0.0000` (US$ 0).

**mp4 final:**

| dato | valor |
|---|---|
| ruta | `output/123bbb64-9fca-4395-8bf4-57d60e219ef1/123bbb64-9fca-4395-8bf4-57d60e219ef1_final_gfx.mp4` |
| md5 | `efc0c71d95b90adfe55c29dd1cdf2cc7` |
| tamaño | 540.010.515 B (515,0 MB) |
| duración (ffprobe) | 824,366667 s |
| video | h264 2560×1440, 30/1 fps |
| audio | aac 44,1 kHz, mono |
| vs `mezcla_preview` (824,4 s) | igual: 824,37 s, diferencia 0,03 s, menos de un cuadro |

El respaldo sin música quedó en `<tid>_final_gfx_no_music.mp4` (538.779.873 B). El `<tid>_final.mp4` sin gfx de F72 (20:12) sigue ahí, sin tocar.

**Por cap:** los 7 salieron con gfx; ninguno cayó al fallback del clip original.

| cap | `[gfx]` en el log | ventanas HyperFrames (sparse) | lint | costura (segmento vs guion) | negro de cierre |
|---|---|---|---|---|---|
| ch01 | ✓ OK en 122 s (disperso) | 4 · 18,9 s de 70,3 s (27 %) | 0 errores, 7 warnings | ✓ 70,300 = 70,300 | ✓ 1,000 s |
| ch02 | ✓ OK en 152 s | 3 · 30,2 s de 107,2 s (28 %) | 0 / 7 | ✓ 107,233 = 107,233 | ✓ 1,000 s |
| ch03 | ✓ OK en 186 s | 5 · 25,4 s de 178,8 s (14 %) | 0 / 9 | ✓ 178,800 = 178,800 | ✓ 1,000 s |
| ch04 | ✓ OK en 150 s | 5 · 27,9 s de 103,5 s (27 %) | 0 / 10 | ✓ 103,500 = 103,500 | ✓ 1,000 s |
| ch05 | ✓ OK en 153 s | 5 · 24,1 s de 135,1 s (18 %) | 0 / 9 | ✓ 135,100 = 135,100 | ✓ 1,000 s |
| ch06 | ✓ OK en 158 s | 5 · 25,0 s de 131,7 s (19 %) | 0 / 9 | ✓ 131,700 = 131,700 | ✓ 1,000 s |
| ch07 | ✓ OK en 110 s | 4 · 15,1 s de 95,2 s (16 %) | 0 / 6 | **✗ 95,233 vs 95,267** (falta 1 cuadro, tolerancia ±0,0333 s) | ✓ 0,967 s |

En total son 31 ventanas HyperFrames. En ningún `gfx_chNN.log` hay errores. El `hyperframes doctor` avisa que hay una versión más nueva disponible (0.8.172 → 0.8.207) en los 7 caps; es solo informativo.

**ch07, costura ✗:** el segmento quedó 33 ms más corto que el guion, un cuadro a 30 fps, apenas fuera de la tolerancia. Por eso el negro de cierre mide 0,967 s y no 1,000 s. No lo investigué ni lo corregí.

**Las 7 preguntas de cierre en el mp4.** Los textos y duraciones salen del plan resuelto (`gfx_plan_chNN.resolved.json`). Los tiempos son los de `GUION_PANTALLA.md`, que coinciden con «inicio del segmento + `start` del plan + 2,5 s»: el mp4 dura 2,5 s más que la suma de los 7 segmentos (821,87 s), por la entrada de 2,5 s. Comprobé dos con un cuadro sacado del mp4 a 69,5 s y a 822,3 s: en los dos se lee la pregunta.

| cap | t en el mp4 | texto | dura | negro | fuente |
|---|---|---|---|---|---|
| ch01 | 01:08.3 | «Dos años antes de la foto, en Madrid, hubo un baile.» | 3,467 s | 1,0 s | voz-final |
| ch02 | 02:54.6 | «Del avión, a la tierra más roja que Víctor había visto en su vida.» | 4,4 s | 1,0 s | voz-final |
| ch03 | 05:51.7 | «Ese mismo año, un recién casado de Madrid se bajaba de un avión en esa misma pista de polvo.» | 6,133 s | 1,0 s | voz-final |
| ch04 | 07:37.5 | «Creyeron que se llevaban de Wittenoom un hijo y nada más.» | 3,8 s | 1,0 s | voz-final |
| ch05 | 09:53.2 | «Y no fue el único que se llevó Wittenoom adentro.» | 3,267 s | 1,0 s | voz-final |
| ch06 | 12:04.9 | «En esa tierra vivía un hombre que no podía irse.» | 3,2 s | 1,0 s | voz-final |
| ch07 | 13:41.5 | «Lo que sobró de la mina, sí.» | 1,867 s | 1,0 s | voz-final |

La mezcla imprimió estas pausas de cierre (pregunta + negro): `{'ch01': 4.467, 'ch02': 5.4, 'ch03': 7.133, 'ch04': 4.8, 'ch05': 4.267, 'ch06': 4.2, 'ch07': 2.867}`.

**Cola del log (últimas 40 líneas):**

```
     [ch01] reused → hook_f28_b.mp3 (loop a 65.7s)
     [ch02] reused → setup_f28_b.mp3 (loop a 98.7s)
     [ch03] reused → rising_tension_f28_a.mp3 (loop a 168.6s)
     [ch04] reused → rising_tension_f28_a.mp3 (loop a 95.6s)
     [ch05] reused → shock_f28_a.mp3 (loop a 127.8s)
     [ch06] reused → consequences_f28_b.mp3 (loop a 124.4s)
     [ch07] reused → outro_f28_b.mp3 (loop a 89.3s)
     paso B: sidechain mix (por-cap)...
     mixing params: vol=0.26, floor=0.16, thr=0.03, ratio=5.0, atk=80.0ms, rel=200.0ms, init_silence=2.5s (F2b: audio solo + remux)
     ⏱ música: 27s (audio solo + remux)
     ✅ música mezclada en 123bbb64-9fca-4395-8bf4-57d60e219ef1_final_gfx.mp4

  ✅ 123bbb64-9fca-4395-8bf4-57d60e219ef1_final_gfx.mp4 — 824.4s · 515.0MB · $0.0000
     📌 topics_db: 123bbb64-9fca-4395-8bf4-57d60e219ef1 → video_generated

════════════════════════════════════════════════════════════
  ✅ FASE 2B BATCH TERMINADA
════════════════════════════════════════════════════════════
  Procesados OK: 1/1
  ▶ Siguiente paso (empaquetar para publicar):
       python fase3.py 123bbb64-9fca-4395-8bf4-57d60e219ef1
════════════════════════════════════════════════════════════


  ⏵ 123bbb64-9fca-4395-8bf4-57d60e219ef1: arranca en «render» — guion aprobado por Omar (2026-11-03), planes 05cad6e8…; falta C:/CLAUDE_PROJECTS/automatization_videos/output/123bbb64-9fca-4395-8bf4-57d60e219ef1/123bbb64-9fca-4395-8bf4-57d60e219ef1_final_gfx.mp4

────────────────────────────────────────────────────────────
  ▶ RENDER (fase2b --gfx --gfx-sparse) — 123bbb64-9fca-4395-8bf4-57d60e219ef1
────────────────────────────────────────────────────────────

════════════════════════════════════════════════════════════
  📊 RUN_PIPELINE — 123bbb64-9fca-4395-8bf4-57d60e219ef1
════════════════════════════════════════════════════════════
  Fases corridas: render, packaging (diferido)
  ✅ Cadena completa.
════════════════════════════════════════════════════════════

  📦 LISTO PARA PACKAGING → python fase3.py 123bbb64-9fca-4395-8bf4-57d60e219ef1

exit 0
```

El orden del log tiene una explicación: la salida del subproceso fase2b quedó escrita antes que los encabezados de `run_pipeline`, porque `print` va por buffer. Por eso «arranca en render» aparece después del render.

## Estado al cerrar

- `etapa_de` = `('packaging', '…_final_gfx.mp4 listo; falta empaquetar (fase3)')`. fase3 no se corrió; `publish/` sigue con los archivos del 1-nov.
- Siguen en disco `_fase2b_work_desfasado_20261031_234112` y `_fase2b_work_desfasado_20261103_193709`.
- Logs sin commitear, en `lab/hyperframes/f72/c/`: `aprobar.log`, `run_pipeline.log`, `inicio.txt`, `cola40.txt` y `mp4_antes.txt`.
- Commit: este reporte, `lab/ESTADO_SESION.md` y `DECISIONES.md`.

## Veredicto del revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | md5 del handoff 7761839f… | OK | `md5sum` da 7761839fa98af4bea9bf5083d017a43f |
| 2 | Etapa 0: tabla de solo lectura (etapa_de, md5 de GUION_PANTALLA, papel_md5, 15 visuales con mtime ≥ 19:37, md5 de ch01/ch07 hybrid) | OK | La tabla está en F72c_REPORT.md. Yo comprobé `GUION_PANTALLA.md` = 6b2b9944… y que los 15 visuales tienen mtime entre 19:42:52 y 20:14:30. No recalculé los md5 de ch01/ch07 hybrid (solo vi sus mtime). El `etapa_de` previo no se puede reconstruir; sale del reporte. |
| 3 | Línea de DECISIONES del 21:05 con el texto de «Decisión» y la chascada de F73 | OK | `git diff DECISIONES.md` suma una sola línea, 2026-11-03 21:05 · F72c, con ambos textos. |
| 4 | Etapa 1: `--aprobar-guion` y pegar la salida y el campo `aprobacion` | OK con salvedad | `GUION_PANTALLA.json` no tiene la clave `aprobacion` (da None). La aprobación está en `aprobado`: {'por': 'Omar', 'fecha': '2026-11-03', 'md5_planes': '05cad6e8…'}. El reporte lo declara. El md5 de GUION_PANTALLA no cambió tras aprobar. |
| 5 | Etapa 2: arranca en `render`, sin fase3, sin plan-edit ni plan-only | OK | `run_pipeline.log` dice «arranca en «render»». Los `gfx_chNN.log` son de 21:10–21:27, o sea del render. El reporte dice que `publish/` sigue con los archivos del 1-nov. |
| 6 | Etapa 3: mp4 final con md5, duración, resolución y fps | OK | `efc0c71d95b90adfe55c29dd1cdf2cc7`. ffprobe: 824,366667 s, h264 2560×1440, 30/1 fps, aac. Coincide con el reporte y con los 824,4 s de la mezcla. |
| 7 | Por cap: gfx o fallback, ventanas, errores | OK | `run_pipeline.log` muestra «✓ [gfx] chNN OK» en los 7 caps (21:10 a 21:27). Los «error» en `gfx_chNN.log` son «lint: 0 errores» y texto del plan. No recalculé el conteo de 31 ventanas. |
| 8 | Costuras | OBSERVACIÓN | `run_pipeline.log:73`: ✗ costura ch07, segmento 95,233 s vs guion 95,267 s (falta un cuadro). El negro de cierre de ch07 mide 0,967 s en vez de 1,0 s. El reporte lo declara y no lo investigó. Las otras 6 costuras están OK. |
| 9 | Los 7 tiempos de la pregunta de cierre | PARCIAL | La tabla está en el reporte y cita el plan resuelto. Solo se comprobaron 2 por cuadro del mp4 (según el reporte). Yo no los verifiqué contra el mp4. |
| 10 | Costo y tiempo | OK | Reporte: US$ 0, 21 min 05 s, exit 0. Los timestamps del log (21:08 a 21:29) son consistentes. |
| 11 | Cola de 40 líneas | OK | Existe `lab/hyperframes/f72/c/cola40.txt` y está pegada en el reporte. |
| 12 | Sin tocar código, prompts ni main; sin borrar `_fase2b_work_desfasado_*` | OK | Los dos `_desfasado_*` siguen en disco. El único .py modificado es `diag_234_cap4.py` (cambia la constante TOPIC), que ya estaba modificado antes (estaba en el gitStatus inicial) y no es de F72c. |
| 13 | PARADA: reporte, ESTADO_SESION y commit | NO VERIFICABLE | El reporte existe. ESTADO_SESION y el commit no están hechos todavía (HEAD = a7d4a5b de F72b), como avisó el pedido. |

Fuera de alcance: ninguno atribuible a F72c. Estaban modificados antes y no deben entrar al commit: `diag_234_cap4.py`, `lab/hyperframes/f28/a/f28a.log`, `lab/hyperframes/f58/pedido_paquetes_wittenoom.txt`.

Riesgos que el contrato no cubre:
- El ✗ de ch07 (un cuadro) no tiene criterio de aceptación en el contrato, y el mp4 queda como entregable con esa costura. Lo decide Omar.
- El handoff pide el campo `aprobacion` y la clave real es `aprobado`.
- Los logs de `lab/hyperframes/f72/c/` están sin commitear. Falta decidir si entran al commit.

## Adenda de CC

- **Fila 9:** después del veredicto saqué un cuadro del mp4 en cada una de las 5 preguntas que faltaban: 175,5 s, 352,5 s, 458,5 s, 594,5 s y 726,3 s. En las 7 se lee el texto de la tabla. Al primer intento, ch05 y ch06 los saqué en 591,8 s y 723,5 s, antes de que arrancara la pregunta: ahí todavía hablaba la voz y se veía el subtítulo. Con los tiempos del guion aparecen las dos.
- **Fila 2:** los md5 de ch01 y ch07 `_hybrid_visual` los calculé en la etapa 0, antes de aprobar: `b976a42b…` y `1a343b14…`, los mismos de F72.
- **Logs de `lab/hyperframes/f72/c/`:** no entran al commit, como en F72 y F72b. El pedido dice «reporte + ESTADO + DECISIONES».
- **ch07, un cuadro:** lo decide Omar. No lo toqué.

PARADA.
