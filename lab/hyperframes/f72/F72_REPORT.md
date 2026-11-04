# F72 — Wittenoom: fondos → guion de pantalla, PARADA en aprobar_guion

Handoff: `lab/hyperframes/f72/HANDOFF_F72.md` (md5 `6aea795970f77fc2539433f8ecd232b9`, verificado). Topic `123bbb64-9fca-4395-8bf4-57d60e219ef1`, rama `f11-guion-v4`. Sin cambios de código, prompts ni main.

## Resultado en una línea

`run_pipeline --batch` corrió fondos + guion de pantalla en 64 min 22 s (19:37:05 → 20:41:27), US$ 0,1239 (fondos 0,0883 + guion 0,0356, Gemini), exit 0, y se paró sola en la compuerta del guion. `etapa_de` ahora = `aprobar_guion`.

## Paso 0 — etapa antes de correr

Con `viral-video-pipeline/.venv`: `etapa_de(tid)` → `('fondos', 'falta fondos.json')`. Era la esperada; seguí.

## Paso 1 — corrida

Comando: `python run_pipeline.py --topic 123bbb64-9fca-4395-8bf4-57d60e219ef1 --batch` (venv, sin `QA_FORM`). Log completo: `lab/hyperframes/f72/run_pipeline.log`; horas: `lab/hyperframes/f72/inicio.txt`.

Workers: los que trae el código, sin tocarlo: clips `CLIP_WORKERS = 6`, base -g30 de los 7 caps en paralelo (188 s); el plan por cap corre en fila (1553 s) porque `GFX_PARALELO = 1` y no hay forma de subirlo sin tocar código.

Cierre del log, textual:

```
  Fases corridas: fondos, guion de pantalla, compuerta del guion de pantalla
  ⛔ Frenó en: GUION DE PANTALLA
     Motivo: el guion de 123bbb64-9fca-4395-8bf4-57d60e219ef1 no está aprobado (Omar lo aprueba; CC corre `fase2b 123bbb64-9fca-4395-8bf4-57d60e219ef1 --aprobar-guion "Omar <fecha>"` solo si su prompt dice «aprobado») (la compuerta no se aprueba sola: sin el form la aprueba Omar a mano)
exit 0
```

Fondos, extracto:

```
  📦 fondos de otro papel: movidos a _fase2b_work_desfasado_20261103_193709
  🎥 flow_specs cache ausente/incompleto → flow_director (LLM)
  🎬 flow_director: 97 imagen(es) de 7 cap(s) (ch01, ch02, ch03, ch04, ch05, ch06, ch07)...
  [fase2b] ch01 híbrido veo+flux: Veo 8.0s @ pos=start + 8 Flux supps (57.6s)
  [fase2b] ch07 híbrido veo+flux: Veo 8.0s @ pos=end + 12 Flux supps (81.3s)
  ✅ 123bbb64-9fca-4395-8bf4-57d60e219ef1_final.mp4 — 771.5s · 395.7MB · $0.0883
     📌 topics_db: 123bbb64-9fca-4395-8bf4-57d60e219ef1 → video_generated
```

Guion de pantalla, extracto:

```
  ♻  reuse-visuals: salteando flow_director (clips ya horneados)
  🎞  base -g30 de 7 caps en paralelo: 188s
  ⏱  --plan-only 1755s · costos {'gemini_usd': 0.0356}
```

Sobre `--reuse-visuals`: yo no lo pasé y `run_pipeline` tampoco (el paso de pantalla es `fase2b.py <tid> --plan-only`). La línea «♻ reuse-visuals» la imprime `--plan-only` solo: lee los fondos recién cocidos en este mismo run y no vuelve a llamar al flow_director. No se corrió `--gfx`, `--aprobar-guion` ni `--plan-edit`.

## Paso 2 — verificación en disco

Script de solo lectura con la venv; la salida va tal cual:

### fondos.json

- `output/123bbb64-9fca-4395-8bf4-57d60e219ef1/_fase2b_work/fondos.json`: {"papel_md5": "39c99927c5d95fad16a3ecf062661f0b"} · `68e5766312d82b20dace108357596b29` · 2026-11-03 20:12:09
- `aprobado.md5` del papel: `39c99927c5d95fad16a3ecf062661f0b` (por Omar, 2026-10-31T23:04)
- manifest `papel_md5`: `39c99927c5d95fad16a3ecf062661f0b` · coincide los tres: **True**

### Híbridos de ch01 y ch07

| archivo | antes | después |
|---|---|---|
| _fase2b_work/ch01_hybrid_visual.mp4 | FALTA | `b976a42b1b8672408ee0daac1fa83872` · 2026-11-03 19:43:27 |
| _fase2b_work/ch07_hybrid_visual.mp4 | `d1858575c3d557988d5dfdf2fd51c846` · 2026-11-01 00:11:54 | `1a343b14d944ba5ae8c3bcdc0865a08b` · 2026-11-03 20:10:01 |

Clip fuente según el manifest (lo que `_resolve_chapter_paths` le da a fase2b):

- ch01: `assets\ch01_veo\ch01_clip_01.mp4` · status ok · `5aa387cde1f850cc78f97cba112323cd` · 2026-11-01 15:42:08 (el clip de F69: Daniel solo) · igual antes y después.
- ch07: `assets\ch07_veo\ch07_clip_01.mp4` · status ok · `5f36c8eee006f1a80c229e1fce7b9487` · 2026-11-01 07:37:56 (el clip de F68b) · igual antes y después.

Los dos clips no se tocaron. El ch07 viejo (`d1858575…`, del 1-nov 00:11, de los clips Seedream) quedó en `_fase2b_work_desfasado_20261103_193709/`. El ch01 no tenía híbrido antes porque F69 lo había invalidado.

### Fotos que entraron al bake (rutas del manifest)

| foto | crudo (.png) md5 | graded que usa el bake · mtime |
|---|---|---|
| ch01 supp 2 | `017cbe8a219da54fffde72ec11b69f78` | `b5918b6731055ebfefaf5b3c072f3988` · 2026-11-03 19:11:46 |
| ch03 img 8 (F70b) | `bda61effa664a156681c132e7a632423` | `efe680ff9826771f418d189d858b57d4` · 2026-11-01 15:45:25 |
| ch03 img 15 (F70b) | `ac76049d56699832dba461058576ed7b` | `79c236301734c80f02008e454a066889` · 2026-11-01 15:45:26 |
| ch06 img 7 (F70b) | `b60bafcd2ad2ae4131055eca7b0ae31a` | `6ea9c63af0656cc675f3a1900bc324e0` · 2026-11-01 15:45:26 |
| ch03 img 16 (no pedida, cambió hoy) | `5d4636bfca3cd35887c347f39bf9e0d6` | `c440074949c92fdd110a462bd030ec09` · 2026-11-03 19:14:48 |

Los visuales base de ch03 y ch06 se cocieron después de esas fotos: ch03 `38b72aaa14d4be2a24d8a67b968929de` · 2026-11-03 19:52:18 · ch06 `a1681ed4e76ecfa3d72d249ca3579ff8` · 2026-11-03 20:05:14.

**`ch01_supp_02` no es la foto de F71b.** La de F71b (`lab/hyperframes/f71/ch01_supp_02_despues.png`, md5 `9ca00e1ca95c87c258f473c2c1a612c7`) está en `assets/_qa_backups/` con sello 20261103_190920. O sea, alguien la rehízo en QA Studio hoy entre 19:09 y 19:11, tres veces (backups 190920, 191022, 191136). La que entró al bake es la última, de las 19:11:46 (`017cbe8a…`). A las 19:14 también se rehízo `ch03_img_16`. Las dos son ediciones humanas de hoy, previas a la corrida, y quedaron en el manifest. No las toqué: el bake usó lo que dice el manifest. Si la que quería Omar era la de F71b, hay que restaurarla y volver a cocer ch01.

### Anclas

| cap | anclas | por trigrama | por fallback | sync_approx (QA) |
|---|---|---|---|---|
| ch01 | 8 | 8 | 0 | False |
| ch02 | 15 | 15 | 0 | False |
| ch03 | 16 | 16 | 0 | False |
| ch04 | 14 | 14 | 0 | False |
| ch05 | 16 | 16 | 0 | False |
| ch06 | 16 | 16 | 0 | False |
| ch07 | 12 | 12 | 0 | False |

Total: 97 anclas, 0 por fallback.

### Guion de pantalla

- `output/123bbb64-…/GUION_PANTALLA.md`: `27c0d8c13291c6558b211cfd5c6a9595` · 2026-11-03 20:41:26
- `output/123bbb64-…/GUION_PANTALLA.json`: `45c296f2a6a89b369307f0020548431e` · 2026-11-03 20:41:26
- `papel_md5`: `39c99927c5d95fad16a3ecf062661f0b` · `aprobado`: None
- costos: {'gemini_usd': 0.0356} · tiempos_s: {'base_g30_paralelo': 187.7, 'plan_en_fila': 1553.4, 'mezcla': 11.8, 'total': 1753.0}
- chequeos: ✓ dos bloques al mismo tiempo; ✓ bloque que cruza un corte; ✗ texto sin lectura; ✓ pregunta de cierre sin lectura; ✓ cifra que contradice la voz; ✗ a_pantalla; ✓ costuras con cuadro no negro; ✗ inicio de voz por cap; ✓ gancho no vacío; ✗ inicio de música por cap; ✗ papel sin colocar; ✓ papel sin alinear; ✓ relojes del papel (informativo)

5 chequeos en ✗. No son fallas de la corrida: son avisos que el guion le muestra a Omar y al analista. No los abrí ni los corregí; eso va en la revisión del guion.

## Tiempo y costo de la corrida

| etapa | tiempo | costo |
|---|---|---|
| fondos (fase2b sin gfx) | 19:37:09 → 20:12:09 (35 min) | US$ 0,0883 (flow_director, Gemini) |
| guion de pantalla (`--plan-only`) | 20:12:11 → 20:41:26 (1755 s) | US$ 0,0356 (Gemini) |
| **total** | **64 min 22 s** | **US$ 0,1239** |

## Efectos que el handoff no nombra

1. **Se archivaron los fondos viejos:** `_fase2b_work` y las caches `flow_specs`/`depth_metrics`/`zoom_verdicts` → `output/<tid>/_fase2b_work_desfasado_20261103_193709/` (candado F67c: no tenían `fondos.json`). Nada se borró.
2. **Fondos rehízo `<tid>_final.mp4`** (771,5 s, 395,7 MB, sin gfx, con música) y su `_final_no_music.mp4`, y dejó topics_db en `video_generated`. Es lo que hace fase2b sin `--gfx`, no un render con gfx. El `_final.mp4` todavía no es el video a publicar: falta el guion aprobado y el render con gfx.
3. `ch01_supp_02` y `ch03_img_16` son las rehechas en QA hoy (ver arriba), no las de F71b/F68.

## Qué quedó parado

- `etapa_de` = `('aprobar_guion', 'el guion de … no está aprobado …')`.
- Omar lee `output/123bbb64-9fca-4395-8bf4-57d60e219ef1/GUION_PANTALLA.md` y decide: aprobar, editar (el analista, `--plan-edit`) o restaurar `ch01_supp_02` de F71b antes.
- Sin `--gfx`, sin `--aprobar-guion`, sin `--plan-edit`, sin `--reuse-visuals` en ningún comando mío.
- Commit: solo este reporte y `lab/ESTADO_SESION.md`. El log y `inicio.txt` quedan sin commitear en `lab/hyperframes/f72/`.

## Veredicto del revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 0 | etapa_de = fondos antes de correr | OK | Reporte l.11 y log "arranca en «fondos» — falta fondos.json". No lo re-corrí. |
| 1 | run_pipeline --batch sin form: fondos, guion de pantalla, para sola en aprobar_guion, exit 0 | OK | Cola del log: "Frenó en: GUION DE PANTALLA", "exit 0". |
| 2 | Sin --reuse-visuals, --gfx, --aprobar-guion ni --plan-edit | OK | El comando del reporte no los lleva. La línea "reuse-visuals" del log la imprime --plan-only; el reporte lo aclara y es plausible. |
| 3 | fondos.json con papel_md5 del papel aprobado | OK | Disco: fondos.json md5 68e57663…, contenido {"papel_md5":"39c99927…"}. GUION_PANTALLA.json trae el mismo papel_md5. |
| 4 | ch01/ch07 hybrid re-cocidos (md5, mtime antes/después, clip fuente) | OK | Disco: ch01 b976a42b… (19:43:27), ch07 1a343b14… (20:10:01). El ch07 viejo d1858575… está en _fase2b_work_desfasado_20261103_193709. Clips fuente: ch01_veo/ch01_clip_01.mp4 = 5aa387cd…, ch07_veo/ch07_clip_01.mp4 = 5f36c8ee…. Coinciden con el reporte. |
| 5 | Bake de ch01 usa ch01_supp_02 de F71b | FALLA (de la corrida, no del reporte) | La foto de F71b (lab/hyperframes/f71/ch01_supp_02_despues.png, 9ca00e1c…) hoy está solo como backup 20261103_190920. La activa es 017cbe8a… (graded b5918b67…). Alguien la rehízo 3 veces en QA entre 19:09 y 19:11. El reporte lo declara con esos md5. |
| 6 | Fotos F70b de ch03/ch06 en el bake | OK | El reporte da md5 crudo y graded con mtime 11-01 15:45. No recomputé los md5 de esas fotos. |
| 7 | GUION_PANTALLA.md/.json en output/<tid>/ con tiempo y costo | OK | Disco: md5 27c0d8c1… y 45c296f2…. El json trae costos {'gemini_usd': 0.0356} y tiempos_s. Tiempo total y costo suman 64 min 22 s y US$ 0,1239, y coinciden con el log. |
| 8 | 97 anclas con sync_approx False en los 7 caps | PARCIAL | La tabla da 97 (8+15+16+14+16+16+12) y 0 por fallback. Pero "sync_approx" no aparece en GUION_PANTALLA.json (grep = 0). No pude reverificar el 97/False con la fuente que el reporte llama "QA". |
| 9 | Sin cambios de código; commit solo reporte y ESTADO | OK / PENDIENTE | git diff: solo diag_234_cap4.py, DECISIONES.md y 2 archivos de lab. diag_234_cap4.py ya estaba modificado en el git status inicial. El commit aún no se hizo, como se dijo. |

Fuera de alcance: ninguno atribuible a F72. Hay efectos no nombrados por el handoff que el reporte sí declara: se archivaron los fondos viejos en _fase2b_work_desfasado_20261103_193709, y fase2b sin gfx rehízo <tid>_final.mp4 y _final_no_music.mp4. Los archivos sin trackear (log e inicio.txt en f72) no se van a commitear.

Observaciones:
1. Decisión para Omar: la foto de ch01_supp_02 en el bake NO es la de F71b. Es la última de 3 rehechas en QA hoy. También cambió ch03_img_16. Si la buena era la de F71b, hay que restaurarla y re-cocer ch01.
2. El reporte dice que el guion trae 5 chequeos en ✗ (texto sin lectura, a_pantalla, inicio de voz, inicio de música, papel sin colocar) y no los abrió. Es correcto no parchar, pero Omar debe verlos antes de aprobar. No verifiqué esos chequeos.
3. El reporte no cita el comando ni la salida exacta del script de verificación de anclas. Falta trazabilidad de la fuente "sync_approx (QA)".

Riesgos que el contrato no cubre: el contrato no prevé que ediciones humanas en QA entre F71b y F72 cambien las fotos. El _final.mp4 regenerado sin gfx puede confundirse con un video publicable. La corrida de fondos movió los fondos viejos, así que cualquier comparación con el híbrido anterior depende de esa carpeta de archivo.

## Adenda de CC

- Obs. 3 / fila 8: la columna «sync_approx (QA)» no sale de `GUION_PANTALLA.json`, sino del mismo objeto que usa QA Studio para mostrar «sync aproximado»: `qa_studio_server.QAState(tid, base_dir=raíz).cap(n)["sync_approx"]`, con la venv. Las columnas «por trigrama» y «por fallback» salen de `anchor_timing.compute_anchor_starts(anclas, words, narr_norm=cargar_normalizado(tid)[n])`, contando las líneas «FALLBACK» que imprime. Las anclas son `narration_anchor` de `image_prompts` o `supplemental_image_prompts` de cada cap en `data/scripts/<tid>.json`. Las palabras salen de `output/audio/<tid>/chNN_timestamps.json`. Comando: `PYTHONIOENCODING=utf-8 viral-video-pipeline/.venv/Scripts/python.exe verificar_f72.py f72_antes.txt f72_verificacion.md`, un script de solo lectura en el scratchpad de la sesión. Su salida está pegada arriba tal cual.
- Fila 6: los md5 crudos de las fotos F70b los recalculé después de la corrida: `bda61eff…`, `ac76049d…` y `b60bafcd…`. Son iguales al snapshot de antes y a F70b.
- Fila 9: `DECISIONES.md` ya venía modificado de antes de F72, igual que `diag_234_cap4.py`. No es mío y no entra al commit.
