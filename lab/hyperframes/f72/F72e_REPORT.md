# F72e — guion F72d aprobado (sin preguntas de cierre) y render de Wittenoom con gfx (sin packaging)

Handoff: `lab/hyperframes/f72/HANDOFF_F72e.md` (md5 `04132f33c27f2210ad0cb516e1b31429`, verificado con md5sum). Topic `123bbb64-9fca-4395-8bf4-57d60e219ef1`, rama `f11-guion-v4`. Mismo camino que F72c.

No corrí `--plan-edit`, `--plan-only` ni fase3. No toqué código, prompts ni main. No borré ningún mp4 ni ningún `_fase2b_work_desfasado_*`.

## Resultado en una línea

Guion aprobado. `run_pipeline --batch` arrancó en «render» y terminó con exit 0 en 28 min 52 s, US$ 0. `<tid>_final_gfx.mp4` dura **798,27 s**, contra los 798,3 s esperados. Los 7 caps salieron con gfx y sin fallback, y las 7 costuras dan ✓, ch07 incluido. A 0,5 s del final de la voz de cada cap solo se ve el subtítulo de la voz: no hay tarjeta de cierre. El packaging quedó diferido.

## Etapa 0 — solo lectura (todo igual, se siguió)

| verificación | esperado | en disco | ok |
|---|---|---|---|
| md5 `GUION_PANTALLA.md` | `433eb3e5…` | `433eb3e584460e698483ae4fece9c8ce` | ✓ |
| `etapa_de(tid)` | `aprobar_guion` | `('aprobar_guion', 'el guion de … no está aprobado …')` | ✓ |
| `fondos.json` | `68e57663…` / papel `39c99927…` | `68e5766312d82b20dace108357596b29` (de F72d) · `{"papel_md5": "39c99927c5d95fad16a3ecf062661f0b"}` | ✓ |
| 15 visuales de `_fase2b_work/` | mismos md5 que en F72c | `diff` de las dos listas (md5 + nombre): vacío, **15/15 iguales** (`lab/hyperframes/f72/e/visuales_f72c.txt` vs `visuales_ahora.txt`) | ✓ |

## Etapa 1 — renombrar el render de F72c (mv, sin borrar)

| antes | después | md5 |
|---|---|---|
| `<tid>_final_gfx.mp4` | `<tid>_final_gfx_F72c_con_cierres.mp4` | `efc0c71d95b90adfe55c29dd1cdf2cc7` = `efc0c71d95b90adfe55c29dd1cdf2cc7` |
| `<tid>_final_gfx_no_music.mp4` | `<tid>_final_gfx_no_music_F72c.mp4` | `ff5d7174ca29101c534a7e53112131a0` = `ff5d7174ca29101c534a7e53112131a0` |

Usé `mv -n`, que no pisa nada. Los dos siguen en `output/<tid>/`.

## Etapa 2 — `fase2b.py <tid> --aprobar-guion "Omar 2026-11-03"`

```
  ✔ guion de 123bbb64-9fca-4395-8bf4-57d60e219ef1 aprobado por Omar (2026-11-03) · md5 de los planes e8c497c1bfa337def1fd3adf89d82d74
exit 0
```

- `GUION_PANTALLA.json` · `aprobado`: `{'por': 'Omar', 'fecha': '2026-11-03', 'md5_planes': 'e8c497c1bfa337def1fd3adf89d82d74', 'planes': [gfx_plan_ch01…ch07.resolved.json]}`.
- `GUION_PANTALLA.md` sigue en `433eb3e5…`.
- `etapa_de` → `('render', 'guion aprobado por Omar (2026-11-03), planes e8c497c1…; falta …_final_gfx.mp4')`. ✓

## Etapa 3 — `run_pipeline.py --topic <tid> --batch`

Con la venv y `PYTHONUNBUFFERED=1`, así esta vez el log sale en orden.

```
  ⏵ 123bbb64-9fca-4395-8bf4-57d60e219ef1: arranca en «render» — guion aprobado por Omar (2026-11-03), planes e8c497c1…; falta …_final_gfx.mp4
  Fases corridas: render, packaging (diferido)
exit 0
```

Arrancó en `render`, así que no lo maté, y no corrí fase3. En cada cap el log dice «capa de otro plan: se rehace»: la caché de capas por md5 del plan detectó que los planes cambiaron y volvió a dibujar las 7 capas. Los 15 visuales de fondo se reusaron.

## Etapa 4 — salida

**Corrida:** exit 0 · 23:10:26 → 23:39:18 (**28 min 52 s**) · tracker `Costo total: $0.0000` (US$ 0). Tardó más que F72c (21 min) porque las 7 capas se rehicieron y la música tardó 82 s en vez de 27 s.

**mp4 final:**

| dato | valor |
|---|---|
| ruta | `output/123bbb64-9fca-4395-8bf4-57d60e219ef1/123bbb64-9fca-4395-8bf4-57d60e219ef1_final_gfx.mp4` |
| md5 | `1fb47948e43951d4c009e13c0131d184` |
| tamaño | 528.982.642 B (504,5 MB) |
| duración (ffprobe) | **798,266667 s**: contra 798,3 s de la mezcla de previsualización, −0,03 s (un cuadro) |
| video | h264 2560×1440, 30/1 fps |

Ya no queda F72c en el nombre activo: F72c duraba 824,37 s y este 798,27 s (−26,10 s). El respaldo sin música quedó en `<tid>_final_gfx_no_music.mp4` (528.232.431 B). Los dos mp4 renombrados de F72c y los `_final.mp4` / `_final_no_music.mp4` de F72 siguen en disco.

**Por cap:** los 7 con gfx; en ningún `gfx_chNN.log` aparece fallback, «sin capa» ni Traceback.

| cap | `[gfx]` en el log | ventanas HyperFrames (sparse) | lint | costura: segmento vs guion | negro de cierre (blackdetect) |
|---|---|---|---|---|---|
| ch01 | ✓ OK en 131 s (disperso) | 4 · 15,4 s de 66,8 s (23 %) | 0 errores, 6 warnings | ✓ 66,800 = 66,800 | ✓ 65,800→66,800 (1,000 s) |
| ch02 | ✓ OK en 194 s | 3 · 25,8 s de 102,8 s (25 %) | 0 / 6 | ✓ 102,833 = 102,833 | ✓ 101,833→102,833 (1,000 s) |
| ch03 | ✓ OK en 251 s | 5 · 19,3 s de 172,7 s (11 %) | 0 / 8 | ✓ 172,700 = 172,700 | ✓ 171,700→172,700 (1,000 s) |
| ch04 | ✓ OK en 207 s | 5 · 24,1 s de 99,7 s (24 %) | 0 / 9 | ✓ 99,700 = 99,700 | ✓ 98,700→99,700 (1,000 s) |
| ch05 | ✓ OK en 216 s | 5 · 20,9 s de 131,8 s (16 %) | 0 / 8 | ✓ 131,833 = 131,833 | ✓ 130,833→131,833 (1,000 s) |
| ch06 | ✓ OK en 231 s | 5 · 21,8 s de 128,5 s (17 %) | 0 / 8 | ✓ 128,500 = 128,500 | ✓ 127,500→128,500 (1,000 s) |
| ch07 | ✓ OK en 152 s | 4 · 13,2 s de 93,4 s (14 %) | 0 / 5 | **✓ 93,400 = 93,400** | **✓ 92,400→93,400 (1,000 s)**: el negro final del video |

Son 31 ventanas HyperFrames en total. Las 6 costuras entre caps y el negro final de ch07 dan ✓. El cuadro que faltaba en ch07 en F72c (95,233 contra 95,267) ya no aparece. La mezcla imprimió `pausas de cierre (gfx): {'ch01': 1.0, … 'ch07': 1.0}`: en cada cap solo queda el negro. El `hyperframes doctor` sigue avisando que hay una versión nueva (0.8.172 → 0.8.207); es solo informativo.

**Cuadro a 0,5 s del final de la voz de cada cap:**

El instante de cada cuadro es: inicio del cap en el mp4 (2,5 s de entrada + la suma de los `seg_dur` anteriores) + el fin de la última palabra (`chNN_timestamps.json`) + el `time_offset` del cap − 0,5 s. Hoja: `lab/hyperframes/f72/e/cierres_7caps.jpg`, con los 7 cuadros sueltos en `cierre_chNN.jpg`.

| cap | última palabra | t en el mp4 | qué se ve |
|---|---|---|---|
| ch01 | «baile.» | 67,379 s | foto del baile y el subtítulo de la voz «Dos años antes de la foto, en Madrid, hubo un baile.»; **sin tarjeta de cierre** |
| ch02 | «vida.» | 168,52 s | el chico sobre el pueblo y el subtítulo «Del avión, a la tierra más roja…»; sin tarjeta |
| ch03 | «polvo.» | 342,953 s | el recién casado en la pista y el subtítulo «…en esa misma pista de polvo.»; sin tarjeta |
| ch04 | «más.» | 442,653 s | la familia en el avión y el subtítulo «Creyeron que se llevaban…»; sin tarjeta |
| ch05 | «adentro.» | 573,133 s | el cementerio y el subtítulo «Y no fue el único que se llevó Wittenoom adentro.»; sin tarjeta |
| ch06 | «irse.» | 703,006 s | el hombre en el pueblo y el subtítulo «En esa tierra vivía un hombre que no podía irse.»; sin tarjeta |
| ch07 | «sí.» | 796,346 s | la mina desde el aire y el subtítulo «Lo que sobró de la mina, sí.»; sin tarjeta |

En los 7 cuadros el único texto es el subtítulo chico abajo, que es la voz. No está el texto grande centrado sobre fondo oscurecido que en F72c se veía en 01:08.3, 02:54.6, …, 13:41.5.

Además saqué un cuadro en el hueco de ch02 entre el fin de la voz y el negro (170,2 s, `tras_voz_ch02.jpg`): imagen limpia, sin texto.

**Cola del log (últimas 40 líneas):**

```
     [ch03] reused → rising_tension_f28_a.mp3 (loop a 168.6s)
     [ch04] reused → rising_tension_f28_a.mp3 (loop a 95.6s)
     [ch05] reused → shock_f28_a.mp3 (loop a 127.8s)
     [ch06] reused → consequences_f28_b.mp3 (loop a 124.4s)
     [ch07] reused → outro_f28_b.mp3 (loop a 89.3s)
     [ch01] reused → hook_f28_b.mp3 (loop a 65.7s)
     [ch02] reused → setup_f28_b.mp3 (loop a 98.7s)
     [ch03] reused → rising_tension_f28_a.mp3 (loop a 168.6s)
     [ch04] reused → rising_tension_f28_a.mp3 (loop a 95.6s)
     [ch05] reused → shock_f28_a.mp3 (loop a 127.8s)
     [ch06] reused → consequences_f28_b.mp3 (loop a 124.4s)
     [ch07] reused → outro_f28_b.mp3 (loop a 89.3s)
     paso B: sidechain mix (por-cap)...
     mixing params: vol=0.26, floor=0.16, thr=0.03, ratio=5.0, atk=80.0ms, rel=200.0ms, init_silence=2.5s (F2b: audio solo + remux)
     ⏱ música: 82s (audio solo + remux)
     ✅ música mezclada en 123bbb64-9fca-4395-8bf4-57d60e219ef1_final_gfx.mp4
[23:39:17] INFO     | viral_pipeline | [cost_tracker] Video 123bbb64-9fca-4395-8bf4-57d60e219ef1 — Costo total: $0.0000

  ✅ 123bbb64-9fca-4395-8bf4-57d60e219ef1_final_gfx.mp4 — 798.3s · 504.5MB · $0.0000
     📌 topics_db: 123bbb64-9fca-4395-8bf4-57d60e219ef1 → video_generated

════════════════════════════════════════════════════════════
  ✅ FASE 2B BATCH TERMINADA
════════════════════════════════════════════════════════════
  Procesados OK: 1/1
  ▶ Siguiente paso (empaquetar para publicar):
       python fase3.py 123bbb64-9fca-4395-8bf4-57d60e219ef1
════════════════════════════════════════════════════════════


════════════════════════════════════════════════════════════
  📊 RUN_PIPELINE — 123bbb64-9fca-4395-8bf4-57d60e219ef1
════════════════════════════════════════════════════════════
  Fases corridas: render, packaging (diferido)
  ✅ Cadena completa.
════════════════════════════════════════════════════════════

  📦 LISTO PARA PACKAGING → python fase3.py 123bbb64-9fca-4395-8bf4-57d60e219ef1

exit 0
```

## Estado al cerrar

- `etapa_de` = `('packaging', '…_final_gfx.mp4 listo; falta empaquetar (fase3)')`. fase3 no se corrió.
- En `output/<tid>/` hay 6 mp4:
  - el nuevo y su respaldo sin música;
  - los dos de F72c, renombrados;
  - `_final.mp4` y `_final_no_music.mp4` de F72.
- Siguen los dos `_fase2b_work_desfasado_*`.
- Sin commitear, en `lab/hyperframes/f72/e/`: los logs (`aprobar.log`, `run_pipeline.log`, `inicio.txt`, `cola40.txt`), los md5 (`mv_antes.txt`, `mv_despues.txt`, `visuales_*.txt`) y los cuadros (`cierre_chNN.jpg`, `cierres_7caps.jpg`, `tras_voz_ch02.jpg`).
- Commit: este reporte y `lab/ESTADO_SESION.md`.

## Veredicto del revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 0 | Handoff md5 04132f33… | OK | md5sum del handoff coincide |
| 1 | Etapa 0 solo lectura: guion 433eb3e5…, fondos y 15 visuales iguales a F72c | OK | md5sum de GUION_PANTALLA.md = 433eb3e584460e698483ae4fece9c8ce. `lab/hyperframes/f72/e/visuales_f72c.txt` y `visuales_ahora.txt` existen. NO RE-VERIFIQUÉ el diff de los 15 visuales ni fondos.json: me baso en el reporte. |
| 2 | mv (no borrar) de los dos mp4 de F72c, md5 antes = después | OK | `e/mv_antes.txt` y `e/mv_despues.txt`: efc0c71d… y ff5d7174…. En disco, `_final_gfx_F72c_con_cierres.mp4` y `_final_gfx_no_music_F72c.mp4` tienen esos mismos md5. |
| 3 | `--aprobar-guion "Omar 2026-11-03"` | OK | GUION_PANTALLA.json (leído en UTF-8): aprobado por Omar, 2026-11-03, md5_planes e8c497c1…, 7 planes. El md5 del .md no cambió. |
| 4 | `etapa_de` da render y run_pipeline arranca en render, con `--batch` y sin fase3 | OK | La primera línea de `e/run_pipeline.log` dice «arranca en «render»». La cola dice «Fases corridas: render, packaging (diferido)». El único `final_gfx.mp4` en disco es el nuevo. |
| 5 | Salida del mp4 (md5, duración, resolución, fps) | OK | Yo medí `_final_gfx.mp4`: md5 1fb47948…, 798,266667 s, h264 2560x1440 a 30 fps. Coincide con el reporte y con los 798,3 s esperados. |
| 6 | Gfx en los 7 caps, sin fallback ni errores | OK | `_fase2b_work/gfx_ch01..07.log` tienen 0 coincidencias de fallback o traceback. El log de run_pipeline muestra «capa de otro plan: se rehace» 7 veces. |
| 7 | Costuras y negro final (tabla del reporte) | NO VERIFICABLE | No corrí ffprobe ni blackdetect por cap. Solo confirmé que la duración total es consistente con la suma de segmentos. |
| 8 | Un cuadro a 0,5 s del final de la voz de cada cap, sin texto de cierre | OK | Miré `e/cierres_7caps.jpg`. Los 7 cuadros muestran solo el subtítulo de la voz y ninguna tarjeta de cierre. La hoja tiene 8 celdas y la última repite ch07. Los `cierre_chNN.jpg` sueltos existen. NO VERIFICABLE que cada cuadro caiga exactamente en el t reportado, porque no extraje los cuadros yo. |
| 9 | No borrar mp4 ni `_fase2b_work_desfasado_*` | OK | Hay 6 mp4 en `output/<tid>/`. Siguen `_fase2b_work_desfasado_20261031_234112` y `_20261103_193709`. |
| 10 | Costo US$ 0 | OK | El reporte cita el tracker en $0.0000 y el log lo respalda. |
| 11 | Revisor-handoff íntegro, ESTADO_SESION y commit | PENDIENTE | El caller dijo que todavía no se hacen. Es la parada final del handoff. |

Fuera de alcance: ninguno. `git status` de archivos rastreados muestra solo diag_234_cap4.py, f28a.log y pedido_paquetes_wittenoom.txt, que ya venían modificados. F72e_REPORT.md y `e/` son untracked, como corresponde, y esperan el commit.

Observaciones:
- `_final_gfx_no_music.mp4` tiene md5 82328f17…, que el reporte no cita. No es defecto, pero conviene agregarlo.
- Quedan sin commitear el reporte, `e/` y ESTADO_SESION. Antes del commit hay que pegar este veredicto en el reporte.

Riesgos que el contrato no cubre:
- Los cuadros de cierre son una sola muestra por cap (0,5 s antes del fin de la voz). No demuestran que no haya texto de cierre en otros instantes del tramo final.
- El mp4 no tiene control de calidad visual más allá de esos 7 cuadros; nadie miró el video completo.
- El mp4 de F72c y el nuevo pesan unos 0,5 GB cada uno, y ya hay 6 mp4 en disco.

## Adenda de CC

- **md5 del respaldo sin música:** `<tid>_final_gfx_no_music.mp4` = `82328f1735f8eae803e33d6548de240c`.
- **Fila 7 (costuras):** las líneas «✓ costura chNN» de la tabla salen de la medición que el render corre sobre cada segmento: `_costura_del_segmento`, con ffprobe y `blackdetect`. Están en `lab/hyperframes/f72/e/run_pipeline.log`, dos por cap.
- **Riesgo «una sola muestra por cap»:** además del cuadro, miré los 7 planes resueltos que se dibujaron. Ninguno tiene `chapter_question`. El último bloque con texto de cada cap termina bastante antes del fin de la voz, así que en el tramo final no hay nada que dibujar salvo el negro:

  | cap | fin de la voz (s del cap) | fin del último bloque con texto |
  |---|---|---|
  | ch01 | 65,38 | 59,94 (sello) |
  | ch02 | 99,72 | 46,79 (ficha) |
  | ch03 | 171,32 | 142,59 (ficha) |
  | ch04 | 98,32 | 88,77 (reloj) |
  | ch05 | 129,10 | 116,35 (ficha) |
  | ch06 | 127,14 | 118,40 (sello) |
  | ch07 | 91,98 | 77,84 (sello) |

  También está el cuadro del hueco de ch02 entre el fin de la voz y el negro (170,2 s): imagen limpia.
- **La celda 8 de la hoja** repite ch07: xstack pide un número par de cuadros.
- **`e/`:** no entra al commit (el pedido es reporte + ESTADO), como en F72c.
- **Mirar el video entero:** queda para Omar.

PARADA.
