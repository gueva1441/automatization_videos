# F38e §A — Ensamble (r1 caché de capas + R8 negro de cierre + A.3 costuras en el mp4) — salida en texto

Subagente A · 2026-10-27 · base `2453cf8` (rama `f11-guion-v4`). Archivos: `script_engine/gfx_layer.py`, `fase2b.py`,
`test_module_f38e_a.py` (nuevo), `test_module_gfx_layer_fallback.py` (un test ajustado, dice por qué). Nada commiteado.

## 1. Los 7 segmentos de v6 (solo lectura), medidos con `fase2b._medir_cierre` (`medir_v6.py` → `tabla_v6_segmentos.md`)

| cap | seg_0N (ffprobe) | guion seg_dur | diferencia | gfx_escenas clip_dur / pausa | gfx_pause | plan: pause + black_hold | negro al cierre (blackdetect) |
|---|---|---|---|---|---|---|---|
| ch01 | 100.600 | 101.600 | -1.000 ✗ | 100.600 / 5.667 | 6.667 | 5.667 + 1.0 (start 100.600) | ✗ ninguno (d=0.9333) |
| ch02 | 139.600 | 140.600 | -1.000 ✗ | 139.567 / 6.400 | 7.400 | 6.400 + 1.0 (start 139.567) | ✗ ninguno (d=0.9333) |
| ch03 | 134.300 | 135.300 | -1.000 ✗ | 134.267 / 5.267 | 6.267 | 5.267 + 1.0 (start 134.267) | ✗ ninguno (d=0.9333) |
| ch04 | 128.000 | 128.967 | -0.967 ✗ | 127.967 / 6.133 | 7.133 | 6.133 + 1.0 (start 127.966) | ✗ ninguno (d=0.9333) |
| ch05 | 174.700 | 175.700 | -1.000 ✗ | 174.667 / 5.600 | 6.600 | 5.600 + 1.0 (start 174.667) | ✗ ninguno (d=0.9333) |
| ch06 | 173.200 | 174.200 | -1.000 ✗ | 173.200 / 5.400 | 6.400 | 5.400 + 1.0 (start 173.200) | ✗ ninguno (d=0.9333) |
| ch07 | 195.900 | 196.900 | -1.000 ✗ | 195.867 / 12.867 | 13.867 | 12.867 + 1.0 (start 195.867) | ✗ ninguno (d=0.9333) |

Lectura: en los 7, `gfx_escenas.clip_dur` = voz + pre-roll + **solo la pausa de la pregunta** (sin el negro), el
`black_hold.start` del plan coincide con ese `clip_dur` (el negro empezaba donde terminaba el clip) y la capa
`chNN_gfx.mp4` mide lo mismo que el segmento (p. ej. ch02: 139.600 s, 4188 cuadros ambos). `blackdetect` sobre los
últimos 8 s (d por defecto 2.0 y d=0.9667) y sobre los últimos 1.5 s (d=0.9333): ningún negro en seg_01, seg_02,
seg_07 ni en `ch02_gfx.mp4`. `gfx_pause_chNN.json` (escrito por `--plan-only` a las 03:04) sí traía pausa + negro
(7.400 en ch02): la música se alargó 1 s más que el segmento. ch04 da -0.967 por la grilla de cuadros (ceil a 1/30).

## 2. Causa de R8 (archivo:línea), antes / después

**Causa:** `script_engine/gfx_layer.py:674` (HEAD `2453cf8`), rama del plan congelado (F34, el camino de todo render con
guion aprobado — v6 lo fue: «plan congelado: guion aprobado y vigente» en `gfx_ch02.log` 03:57):

```python
# antes (gfx_layer.py:671-674)
if gfx_plan_override is None:
    pause = closing_question(resolved, ctx, work_dir, cap, clip_dur, log)      # devuelve pause + bh
else:
    pause = float((resolved.get("chapter_question") or {}).get("pause") or 0.0)  # ← solo la lectura, sin el negro
```

`closing_question` (línea 304-307) planea `black_hold = {start: clip_dur + pause, duration: bh}` y devuelve `pause + bh`;
con el plan congelado nadie la llama, se tomaba `chapter_question.pause` (6.4 s en ch02) y `extend_base` alargaba el
base 6.4 s en vez de 7.4: `clip_dur` quedó en 139.567 = `black_hold.start`, el negro cayó **después del final del
clip** (el disperso lo descarta al mapear ventanas, `gfx_sparse.py:189-192`; en el no disperso quedaría fuera de la
composición), y el segmento (`-t max(audio, clip)`) salió 1.0 s más corto que el guion (que se calculó en
`--plan-only`, donde `closing_question` sí suma el negro). No era el armado del segmento en `fase2b` (el `-t` y el
`apad` respetan `clip_duration`): el clip ya venía corto.

**Después** (general, sin números nuevos):
- `gfx_layer.pausa_de_cierre(resolved)` = `chapter_question.pause + black_hold.duration` (el `black_hold_sec` del
  perfil que ya está en el plan); `pausa_a_disco(work_dir, cap, resolved)` escribe `gfx_pause_<cap>.json` desde el
  plan (o lo borra si no hay pregunta) y devuelve esa pausa.
- Los dos caminos usan la misma cuenta: `closing_question` termina en `return pausa_a_disco(...)` y la rama del plan
  congelado hace `pause = pausa_a_disco(work_dir, cap, resolved)` (log: «pausa de cierre (plan fijo): 7.400s =
  pregunta 6.400 + negro 1.000»). El base se alarga pregunta + negro; `black_hold` termina donde termina el clip;
  `gfx_escenas.clip_dur` (lo que lee el guion) incluye el negro; `gfx_pause` (lo que lee la música) coincide.

## 3. Corrida A.4: `fase2b.py f8s3-vajont-f30 --only-cap ch02 --reuse-visuals --gfx --gfx-sparse --gfx-quality looks --sw-encode`

Log entero: `lab/hyperframes/f38e/a/onlycap_ch02_gfx.log` (12:59:47 → 13:04:20, exit 0). El hook `guard_render` dejó
pasar (guion aprobado por Omar, planes `35576ed6…`, antes y después de la corrida). Respaldo previo de la capa de v6
(copiada, no movida): `output/f8s3-vajont-f30/_fase2b_work/_bak_f38e_a/{ch02_gfx.mp4 (md5 d5fc61b5…), gfx_ch02.log}`.

**r1 en el log del render (stdout) y en `gfx_ch02.log`:**
```
  [gfx] ch02 reuse: capa sin md5 de plan: se rehace
  reuse: ch02_gfx.mp4 existente pero capa sin md5 de plan: se rehace
  plan congelado: guion aprobado y vigente → se dibuja el plan aprobado (…)
  pausa de cierre (plan fijo): 7.400s = pregunta 6.400 + negro 1.000
  sidecar: ch02_gfx.plan.md5 = 27cf5298… (md5 del plan resuelto dibujado)
  OK total 189.4s → ch02_gfx.mp4 (disperso)
```
Sidecar escrito: `ch02_gfx.plan.md5` = `27cf529861088a8625af9ab28d9162e4  gfx_plan_ch02.resolved.json` =
`md5sum gfx_plan_ch02.resolved.json` (el archivo del plan no cambió: mtime 03:04:47).

**Chequeo costuras (stdout):**
```
     ✓ ch02_segment_only.mp4 — 140.6s
     ✓ costura ch02: segmento 140.600 s vs guion 140.600 s (±0.0333 s, un cuadro)
     ✓ costura ch02: negro de 1.00 s al cierre · blackdetect (d=0.9333) en los últimos 1.033 s: 139.600→140.600 (1.000 s)
```

**Segmento nuevo contra el guion:** `ch02_segment_only.mp4` = 140.600 s (4218 cuadros; v6: 139.600 / 4188) = guion
`seg_dur` 140.600 = voz 130.0 + pre-roll 3.0 + pregunta 6.400 + negro 1.000 = 140.400 → 140.567 de clip (el base -g30
mide 133.167) → 140.6 en la grilla. `gfx_escenas_ch02.json`: `clip_dur 140.567, pausa 7.4` (antes 139.567 / 6.4).
`gfx_pause_ch02.json`: `pause 7.4` (igual al de `--plan-only`). `ch02_gfx.mp4` nuevo: 140.600 s.

**blackdetect del cierre** (`_medir_cierre`, d = 1.0 − 2/30 = 0.9333, sobre los últimos 1.033 s):
- `ch02_segment_only.mp4`: `black_start 139.600 → black_end 140.600, black_duration 1.000, al_fin` → ✓
- `ch02_gfx.mp4`: idéntico → ✓

**Gasto:** `[cost_tracker] Video f8s3-vajont-f30 — Costo total: $0.0000` (plan congelado: sin director, crítico ni
visión). Ninguna llamada a modelo.

**Lo nuevo en `output/f8s3-vajont-f30/_fase2b_work/` (ls, fecha de hoy > 12:50):**
```
2026-10-27 12:56:45  _bak_f38e_a/            (respaldo: ch02_gfx.mp4 136 868 813 B 04:00 · gfx_ch02.log 04:00)
2026-10-27 13:00:13  gfx_pause_ch02.json     124 B (pause 7.4, igual que antes; ahora lo escribe el plan congelado)
2026-10-27 13:00:28  gfx_escenas_ch02.json   1 766 B (clip_dur 140.567, pausa 7.4)
2026-10-27 13:00:28  gfx_sfx_ch02.json · gfx_sparse_ch02.json
2026-10-27 13:02:56  ch02_gfx.mp4            135 561 568 B (140.600 s)
2026-10-27 13:02:56  ch02_gfx.plan.md5       63 B   ← sidecar nuevo
2026-10-27 13:02:56  gfx_ch02.log · gfx_cues_ch02.{json,md} · hoja_contactos_ch02.jpg · ch02_subs.ass
2026-10-27 13:04:19  ch02_segment_only.mp4   70 243 674 B (140.600 s)
2026-10-27 13:04:20  gfx_review_ch02.html
```
No cambiaron: `gfx_plan_ch0N.resolved.json` ×7 (03:04–03:07), `GUION_PANTALLA.json` (03:39) y `.md` (03:07),
`seg_0N_chNN.mp4` ×7 de v6, los mp4 finales. `aprobacion.estado` después: vigente, `35576ed6…`.
Fuera de `output/`: `data/cost_history.json` (ignorado por git) lo tocó el `cost_tracker` del pipeline al cerrar el
video (US$ 0), como en cualquier corrida de fase2b; no es algo que escriba el código de A.

## 4. r1 — qué huella y por qué

Sidecar `chXX_gfx.plan.md5` junto a `chXX_gfx.mp4`, en formato md5sum (`<md5>  gfx_plan_chXX.resolved.json`). El md5
es el de los **bytes** de `gfx_plan_<cap>.resolved.json` (`gfx_layer.md5_plan_resuelto`): es la misma huella por
archivo que `aprobacion.md5_planes` junta (nombre + bytes de cada plan) para el `md5_planes` del guion aprobado, así
que «capa del plan aprobado» y «guion aprobado y vigente» miran el mismo archivo. Con guion aprobado, ese archivo es
exactamente el plan congelado que se dibuja; sin aprobación (el hook no deja renderizar, pero `apply_gfx` también lo
usa el lab), `apply_gfx` reescribe el resolved.json al dibujar y el sidecar se escribe después, así que también ahí
queda el md5 de lo dibujado. No usé un JSON canónico porque un `--plan-edit` o una regeneración cambian los bytes y
eso es justamente lo que hay que detectar; y porque un md5 distinto al de `md5_planes` habría sido una segunda huella.

`apply_gfx(reuse=True)`: `capa_reusable(work_dir, cap)` → (ok, motivo). Reusa solo si existe la capa, existe su sidecar
y el md5 coincide con el del plan de hoy. Motivos cuando no: «capa sin md5 de plan: se rehace», «capa de otro plan:
se rehace (capa xxxx…, plan de hoy yyyy…)», «capa con sidecar ilegible: se rehace», «sin plan resuelto de hoy contra
el que comparar: se rehace». Se escribe en `gfx_<cap>.log` y se imprime en stdout (`[gfx] chXX reuse: …`): el render
v6 corrida 1 se descubrió porque el log no traía ninguna línea gfx.

Además (misma familia de bug, una línea): `fase2b._segment_hash` ahora incluye `gfx_plan_<cap>.resolved.json` entre los
insumos; antes miraba solo el plan crudo `gfx_plan_<cap>.json` (del director borrado en F37), así que
`--reassemble-from-segments` reusaba `seg_NN` aunque el plan resuelto hubiera cambiado.

## 5. A.3 — el chequeo costuras medido en el mp4

`fase2b._medir_cierre(seg, esperado_s, negro_s, fps)` y `_costura_del_segmento(plan, seg_path, work_dir, hook=)`,
llamado después de «✓ seg_NN … — X.Xs» en el loop en fila y en `_segmentos_en_paralelo`, solo con `--gfx`.
- Duración esperada: `seg_dur` del cap en `output/<topic>/GUION_PANTALLA.json` (lo aprobado); si no hay guion para
  ese cap, la misma cuenta del guion sobre `gfx_escenas_<cap>.json` (`_segmento_de_cap`: max(voz + pre-pad, clip) en
  cuadros enteros; con el arreglo de R8 el `clip_dur` ya incluye el negro). Tolerancia ±1 cuadro = `1/fps`.
- Negro esperado: `black_hold.duration` del plan resuelto (el `black_hold_sec` del perfil); sin pregunta de cierre en
  el plan, «· costura chXX: sin pregunta de cierre en el plan → sin negro que medir».
- `blackdetect`: medido con lavfi (test) que cuando la corrida negra llega al fin del archivo ffmpeg da como
  `black_end` el pts del **último** cuadro negro (una corrida de 1.0 s al cierre se reporta 0.967) y en el medio da el
  fin exacto. Por eso `d=` = negro − 2 cuadros (la tolerancia + ese cuadro final; el `d` por defecto, 2.0 s, no vería
  un negro de 1 s — ninguna de las dos cosas es un número nuevo: salen de `black_hold_sec` y `1/fps`), a la corrida que
  toca el fin se le suma su último cuadro, y pasa si toca el fin y dura ≥ negro − 1 cuadro. Umbral de negro
  (`pix_th`): el de ffmpeg por defecto. `-ss` antes de `-i` (rápido: decodifica solo el cierre), tiempos vueltos a
  absolutos.
- Si falla: «✗ costura chXX: …» con los números; nunca corta el render (rc no cambia).

## 6. Tests

- `test_module_f38e_a.py` (nuevo, 13): r1 (sidecar al dibujar; plan igual + reuse → se reusa; plan cambiado + reuse →
  se rehace; sin sidecar + reuse → se rehace; motivos de `capa_reusable`; `_segment_hash` ve el plan resuelto), R8
  (`pausa_de_cierre`, `pausa_a_disco`, plan congelado alarga pregunta + negro y el negro termina con el clip,
  `closing_question` y el plan fijo dan la misma pausa), A.3 (`_medir_cierre` con negro al cierre, sin negro, negro en
  el medio que no cuenta, duración distinta; líneas ✓/✗ contra guion y contra gfx_escenas). mp4 sintéticos lavfi 64×64.
- `test_module_gfx_layer_fallback.py::test_reuse_no_re_renderiza`: ajustado (ahora el reuse exige el sidecar del plan
  de hoy; el test escribe plan + sidecar). Comentario en el test.
- Corridos: `test_module_f38e_a.py test_module_f32.py test_module_f33.py test_module_gfx_layer_fallback.py
  test_module_fase2b_reassemble.py test_module_fase2b_only_cap.py::test_flags_en_cli test_module_f30b.py
  test_module_f34.py test_module_f36.py` → **68 verdes**. Rápida (`f25c f24 f21`) → **58 verdes**.
- `test_module_fase2b_only_cap.py::test_only_cap_sin_gfx_byte_identico` NO lo corrí: es el md5 de ch02 de Orleans
  (candado del paso 5, lo corre el padre en serie).
- `test_module_f36c_pantalla.py`: 3 rojos (`test_a_salida_valida_el_esquema`, `test_b_candado_en_papel_rechaza_el_anio…`,
  `test_d_un_dato_no_sale_dos_veces…`) — son de `m01e_pantalla.py` (parte C, en curso en paralelo; `git status` lo
  muestra M junto con sus tests). No los toqué.
- `test_constantes_con_origen.py`: sin constantes nuevas (no agregué ninguna a `gfx_config`).

## 7. Lo que queda abierto de A (entero)

- a1. **Vajont v6 sigue sin el negro de cierre** en los 7 caps (y 7 s más corto que el guion). No se re-renderiza
  (handoff: «Vajont sigue congelado»). Con el arreglo, un render nuevo daría 1056.3 s aprox. en vez de 1049.3 y los
  tiempos del guion coincidirían (esto explica parte de r2 del render v6: D128 4 s antes en el mp4 = los negros que
  faltaban de ch01–ch05, más lo que falte).
- a2. El sidecar compara contra el `resolved.json` de disco. Sin guion aprobado (`plan_congelado` = None, p. ej. el
  lab o `gfx_lab_server`), el plan «de hoy» se recalcularía al dibujar y podría diferir del de disco; con reuse y
  sidecar coincidente se reusa igual. En producción el hook exige aprobación, así que no pasa; lo declaro.
- a3. `d=` de blackdetect no es «el por defecto» (2.0 s no ve un negro de 1 s): es negro − 2 cuadros, derivado y
  explicado en el docstring y arriba. Si el analista quiere otra tolerancia, es un número suyo.
- a4. El chequeo costuras no mide el negro de un cap sin pregunta de cierre (no hay `black_hold` en el plan) ni la
  costura de entrada (title card desde negro): mide lo que pidió el handoff (duración + negro al cierre).
- a5. `_segmentos_en_paralelo` (GFX_PARALELO = 1, apagado) recibe el mismo chequeo; no lo probé en paralelo.
- a6. `data/cost_history.json` lo escribe el `cost_tracker` en toda corrida de fase2b (también en esta, US$ 0). No es
  del código de A; queda dicho por la regla «nada en data/».
- a7. `gfx_pause_<cap>.json` ahora lo escribe también el camino congelado (antes quedaba el de `--plan-only`). Si en un
  topic el perfil cambia `black_hold_sec` después de aprobar, el plan congelado sigue con el negro aprobado (lo que
  está en el plan), no el nuevo del perfil: es lo que pide F34 (dibujar lo aprobado).
- a8. Los `seg_0N` viejos de v6 y la capa `ch02_gfx.mp4` de v6 (en `_bak_f38e_a/`, 136 MB) no se borraron.
- a9. La doble corrida con `--reuse-visuals` ahora rehace las 7 capas de un topic que no tenga sidecars (todas las de
  hoy): la primera corrida después de este commit siempre re-renderiza la capa (~20 min en Vajont). Es lo esperado.

## 8. Stickers nuevos para `lab/MAPA_MODULOS.md`

- `gfx_layer`: El director de orquesta de la capa gráfica de un capítulo: llama a todos los demás en orden (plan base
  con el title card de la partición, textos del papel, reparto con crítico, sellos, transiciones) y hace el render en
  HyperFrames. Desde F34, con el guion aprobado dibuja el plan aprobado tal cual (plan congelado) y no lo reescribe.
  F38e: la pausa de cierre es pregunta + negro en los dos caminos (`pausa_de_cierre`), así el negro queda dentro del
  clip; la capa deja junto a `chNN_gfx.mp4` el md5 de su plan (`chNN_gfx.plan.md5`) y con `--reuse-visuals` se reusa
  solo si es el del plan de hoy (si no, «capa de otro plan / sin md5 de plan: se rehace»).
- `fase2b`: (al sticker actual, agregar:) F38e: después de armar cada segmento con `--gfx`, chequeo «costuras» medido
  en el mp4 (`_medir_cierre`): duración con ffprobe contra el `seg_dur` del guion aprobado (±1 cuadro) y `blackdetect`
  del negro de cierre; ✓/✗ en el log del render. La huella del re-ensamble (`_segment_hash`) ve el plan resuelto.
