# F30 — Render rápido: el navegador solo pinta bloques · REPORTE

CC · 2026-10-26 · rama `f11-guion-v4`. Handoff `HANDOFF_F30_render_rapido.md`; tanda `PROMPT_CC_tanda_F29b_F30.md` (etapa 2 de 3, después de F29b A `5ae6177` + fix `f6527a1`).
Commits: **A `94d9496`** · **B `537416f`** · **C `7ac4ef8`** · D = este reporte (sin código). API: **US$ 0** (todos los planes salieron de caché).

**Resultado en una línea:** Vajont v3b sale con **los mismos bloques y las mismas transiciones** que v3 (los 7 planes resueltos idénticos, crítico incluido) y la pared baja de **63.9 a 37.1 min** (−42 %; v3 = el reensamble final de F29 C, 63.9 min; la primera corrida de F29 C había tardado 67.0) y el gfx de **59.2 a 32.4 min**. Las metas del handoff (gfx ≤ 20 min, pared ≤ 30) **no se alcanzaron**: quedan el bake (70–110 s por cap flux) y el stitch (29–55 s).

**PARADA antes de la etapa 3 (F29b B no corrió).** El pedido dice «si el SSIM o las transiciones no dan lo que pide el handoff, frená ahí». Las transiciones dan (idénticas en los 7 caps); el SSIM, leído estricto, **no**: con el código final, la escena 1 de ch06 (A.4) da **0.9485** (< 0.95; 0.951 era la corrida intermedia de A), en D hay 4 escenas bajo 0.95 (ch02 esc. 12 0.751, ch05 esc. 14 0.810 — las dos donde v3 estaba mal, ver D —, ch05 esc. 4 **0.940**, ch07 esc. 7 **0.947**; `d/ssim_d_por_escena.json`) y el «resto» de ch04 da **0.978** (< 0.98). No lo reinterpreto: freno, y decide Omar si con esto sigue el rotulista.

Banco: copia del topic **`f8s3-vajont-f30`** (patrón de F29 C/D, para no pisar v3; el handoff decía correr sobre `f8s3-vajont-f29`): mismos assets, voz, música, visual base (hardlinks) y **todas** las cachés de decisión (plan crudo del director, intensidad, cajas de zoom, visión, recortes del pool, crítico). La salida va donde pide el handoff: `output/f8s3-vajont-f29/f8s3-vajont_final_gfx_v3b.mp4`.
Antes de cada render: Firefox cerrado (cierre normal; **lo cerré 3 veces: se volvió a abrir dos veces durante la tanda, una con una ventana de chat**) y RAM libre > 14 GB (16.0–18.3 GB al arrancar).

## Diagnóstico que cambió al medir
- En Vajont **todas** las escenas de los caps flux son «safe», no la mitad: además del router (rostro/manos), la identidad (`gfx_style.plan_movements`) pone en PNG toda forma que no sea «3D» (acercar → push, paneo, quieta, alejar → pull). ch06: 16/16. Escenas «3D» (no se cuecen): ch02 2, ch03 1, ch04 2; ch05 y ch06 ninguna; ch01 y ch07 son híbridos.

## A — El push «safe» lo hace ffmpeg (`94d9496`)
- `script_engine/gfx_safe_bake.py` (nuevo, 163 líneas): cada escena safe se genera desde su PNG con el movimiento de gsap y reemplaza su tramo en `public/base_cocido.mp4` (mismo fps/tamaño/GOP del re-encode). push 1 → 1.08 sine.inOut con `safe.origin`; pull 1.08 → 1 centrado; paneo escala 1.04 y translateX −dx/2 → +dx/2 lineal; quieta. N = duración × fps (la misma progresión que el timeline). Escenas en paralelo (`safe_bake_workers` 3). `gfx_layer._render_sparse` cuece antes de armar las ventanas y pasa las escenas como normales (`safe=None`: en HF solo `<video>`; el freeze del saliente sale del base cocido).
- `gfx_sparse.event_windows(safe_windows=False)`: la escena safe ya no abre ventana (el camino de F2 §4 queda con `gfx_rules.safe_bake = False`). `test_module_gfx_router` adaptado a ese camino explícito.
- **Desvío del handoff, por medida:** `zoompan` recorta en píxeles enteros. Contra el render HF de v3 (ch06, escenas 1–3): con el PNG a 2560×1440·1.08 SSIM **0.77–0.83**; con el PNG ×6, 0.97 pero lee ~166 MB por cuadro y en paralelo cada cuadro tardó 347 ms (bake 374 s). Una afín subpíxel exacta (PIL) da 0.98 contra HF: la curva y el origen están bien; lo que queda es la captura JPEG q80 de HyperFrames. Se usa **ffmpeg `perspective`** (eval=frame, interpolación lineal, 1/256 px, hilos por franjas): **0.976 a ~24 ms/cuadro**.
- **Medida ch06 (solo A):** cobertura 100 → 31 % (15 ventanas), HF 593 → 259 s, bake 148 s, **stitch 50 → 135 s**, total 728 → 686 s. SSIM de las 3 escenas elegidas contra v3 (`corridas/a_bake/ssim_ch06_escenas.json`): escena 1 paneo **0.951** (mín. 0.874, el primer cuadro después del dip; **con el código final de B: 0.9485**, `corridas/b_stitch/ssim_ch06_escenas.json`), escena 2 push centrado **0.963** (0.949), escena 4 push de rostro **0.973** (0.964); todas las escenas del cap 0.951–0.980. Hoja inicio/mitad/fin v3 | nuevo: `corridas/a_bake/hoja_safe_ch06.jpg` (a ojo, iguales). «El resto del cap ≥ 0.98» no aplica en ch06 (no hay escenas no-safe); se midió en D.
- Los mínimos están todos en cortes: dentro de una ventana HF la escena cocida es `<video>` y su primer cuadro sale con el seek atrasado un cuadro (en v3 era el PNG).
- Tests `test_module_f30.py` (4 de A): la escena safe no abre ventana; el bake da N cuadros exactos (push, paneo, alejar, quieta); la curva del push = gsap y el origen queda fijo; el base cocido conserva duración y fps. `--only-cap ch02` sin `--gfx` con `--sw-encode`: md5 **`38e5ba14…`** (el bake solo corre con `--gfx`).

## B — Las transiciones las hace ffmpeg, en el stitch (`537416f`)
- `event_windows` sin ventana por transición. **Regla:** una transición cuyo tramo (con su margen) toca una ventana de bloque, o que no tiene aire para su fundido (otro corte, el final), entra a la ventana y la sigue dibujando HF; se itera hasta que no cambia. `stitch_transitions` = las de corte fuera de toda ventana [a, b): nunca se aplican dos veces. `transition_windows=True` = el camino de antes (`test_module_gfx_sparse` adaptado a ese camino explícito).
- **Stitch reescrito** (`stitch_segments` + `stitch_graph`): el cap en segmentos exactos a cuadro y **un solo `concat`**. Con A, la cadena de un `xfade` por unión era el costo del stitch (15 ventanas: 135 s; un concat de los mismos tramos, 47 s sin grade). Uniones: base↔HF 4 cuadros (como antes); **dissolve** = último cuadro del saliente congelado + `xfade fade` (lineal: el templater usa sine.inOut; un `xfade` con expresión propia costaba ~9 s por transición); **dip** = el saliente congelado baja a negro en d/2 y el entrante sube desde negro en d/2 (`fade`, rampas lineales como el templater); **flash** = corte + `drawbox` blanco por cuadro (0 → flash_peak en d/3, power1.in); **cut_punch** = corte + `zoompan` 1.02 → 1 en .35 s power2.out (es lo que hace el templater: el handoff decía 1.0 → 1.06 → 1.0).
- **Medida ch06 (A+B):** 4 ventanas, cobertura **16 %**, HF **127 s**, stitch 93 s, total **513 s** (v3 728). Transiciones antes/después **idénticas** en instante y tipo (`corridas/b_stitch/gfx_sparse_ch06.json`: 15 transiciones; 13 en el stitch, el flash de 104.97 s y el dissolve de 110.17 s caen en una ventana y los dibuja HF). SSIM ±1 s de 5 cortes contra v3 (`ssim_ch06_cortes.json`): dip 15.47 s **0.966** (mín. 0.867) · dissolve 19.83 s **0.957** (0.930) · cut 26.13 s **0.979** (0.974) · dissolve 37.17 s **0.975** (0.961) · flash 104.97 s **0.978** (0.969, dibujado por HF).
- El cuadro más bajo del cap (**0.491**) es uno solo, el 4037 (134.57 s), en el corte seco de la escena 14: en v3 ese cuadro repite el anterior (el corte llega un cuadro tarde en el render HF) y en v3b el corte cae en el cuadro del cambio real (`snap_cuts`). Los tramos bajos siguientes (0.63–0.81) son 4 dissolves que salen de un push de rostro: **en v3 había un salto** — el freeze del templater para un saliente safe es su PNG con `scale(1.08)` sin `transformOrigin` (centrado), y el push terminaba en el origen del rostro. Ahora el dissolve parte del último cuadro real (`corridas/b_stitch/dissolve_rostro_46s.jpg`).
- Tests (4 de B): grafo del stitch para 4 escenas [cut, dissolve, dip] = el string esperado; una transición dentro de una ventana no la aplica el stitch (la dibuja HF); una sin aire entra a la ventana; duración del cap exacta a ±1 cuadro con cut_punch, dissolve y flash. md5 `38e5ba14…`.

## C — Chascadas de tiempo, medidas (`7ac4ef8`)
| medida (ch06, después de A y B) | antes | después | decisión |
|---|---|---|---|
| C.1 workers HF 5 → 8 (`fase2b --gfx-workers 8`) | HF 127 s · RAM libre mín. 13.0 GB | HF **157 s** · 12.0 GB | **queda en 5** (no bajó ≥ 15 %) |
| C.2 stitch + grade: libx264 ultrafast crf 16 → NVENC cq 23 (mismas entradas) | 86.0 s · 1.25 GB | **52.2 s** · 0.19 GB · SSIM 0.98 contra x264 | **NVENC por defecto** (`gfx_render.stitch_encoder`; si NVENC falla, vuelve a libx264) |

- C.3 costura entre caps (solo medida, `c/costura_f8s3-vajont-f29.json`, sobre v3): ningún `chNN_gfx.mp4` ni `seg_NN_chNN.mp4` tiene cuadros planos. **El cuadro gris plano (luma 140) y 3 blancos aparecen por primera vez en `_concat_video.ts`**, en las fronteras **ch01→ch02** (cuadros 2959–2962) y **ch03→ch04** (10868–10870): el `fadewhite` de `whip_pan_flash` (`transition_applier._XFADE_MAP`). En el mp4 final, los mismos cuadros 75 después (los 2.5 s de entrada). Sin arreglo (F30b).
- El candado md5 sin `--gfx` no se tocó: `38e5ba14…`. Tests (2 de C). Suite amplia 951 verdes + 5 previas.

## D — Render de validación v3b
`f30_vajont.py todo`: `fase2b f8s3-vajont-f30 --keep-segments --reuse-visuals --gfx --gfx-sparse --gfx-quality looks`, rotulista apagado. **rc 0, pared 37.1 min**, RAM libre mín. 11.8 GB, **US$ 0.0000**. Salida **`output/f8s3-vajont-f29/f8s3-vajont_final_gfx_v3b.mp4`** (1.06 GB; v3 1.21 GB). Planes resueltos de los 7 caps **idénticos** a v3 (`f30_planes.py`: 0 claves distintas, veredictos del crítico iguales). En D el stitch aplicó los cinco tipos (p. ej. ch02: dissolve, dip, cut, flash 108.73 s y cut_punch 120.8 s).

| cap | cobertura v3 → v3b | HF s v3 → v3b | bake s | stitch s v3 → v3b | total gfx s v3 → v3b | SSIM cap (media · mín.) | SSIM safe sin cortes | SSIM resto sin cortes |
|---|---|---|---|---|---|---|---|---|
| ch01 (híbrido) | 17 % → 17 % | 50 → 56 | — | 44 → 30 | 130 → 126 | 0.983 · 0.969 | — | 0.983 |
| ch02 | 86 % → 11 % | 409 → 58 | 74 | 63 → 42 | 548 → 244 | 0.953 · 0.526 | 0.946 (*) | 0.981 |
| ch03 | 100 % → 26 % | 453 → 109 | 79 | 39 → 41 | 573 → 303 | 0.973 · 0.549 | 0.976 | 0.984 |
| ch04 | 98 % → 37 % | 421 → 159 | 70 | 55 → 40 | 555 → 341 | 0.974 · 0.546 | 0.975 | **0.978** |
| ch05 | 100 % → 21 % | 570 → 118 | 110 | 51 → 53 | 704 → 364 | 0.945 · 0.530 | 0.942 (*) | — |
| ch06 | 100 % → 16 % | 593 → 90 | 101 | 51 → 53 | 728 → 331 | 0.974 · 0.491 | 0.976 | — |
| ch07 (híbrido) | 26 % → 17 % | 143 → 95 | — | 83 → 55 | 319 → 237 | 0.980 · 0.501 | — | 0.982 |
| **total** | | | | | **59.2 → 32.4 min** | | | |

(`d/v3b_tiempos.json`, `d/ssim_d.json`; «sin cortes» = sin los ±1 s de cada corte.) **Pared 63.9 → 37.1 min** (v3: reensamble final de F29 C).

(*) **Las dos escenas que bajan la media de ch02 y ch05 son la última del cap, y ahí v3 estaba mal:** ch02 escena 12 (alejar, 0.75) y ch05 escena 14 (push de rostro, 0.81). En v3 el proyecto disperso no tenía su PNG (`compose_sparse` solo pasa `safe` si la ventana cubre la escena exacta, y el fin de escena redondeado a 3 decimales, 170.067, no es el fin de ventana alineado a cuadro, 170.0667): v3 mostró el DepthFlow (en ch05, sobre un rostro: lo que el router quería evitar). v3b muestra el movimiento decidido (`d/ultima_escena_v3_vs_v3b.jpg`). Sin esas dos escenas, las cocidas dan 0.94–0.98 por escena (la más baja, ch05 escena 4: 0.940).

**Contra el objetivo del handoff (medido, no prometido):** gfx ≤ 20 min → **32.4** ✗ · pared ≤ 30 min → **37.1** ✗ · SSIM ≥ 0.95 donde se midió → **✗ leído estricto**: B.5 ✓ (0.957–0.979); A.4 ✓ en la corrida de A (0.951) pero 0.9485 con el código final; en D, 4 escenas bajo 0.95 y el resto de ch04 en 0.978 · bloques y transiciones idénticos en instante y tipo → ✓. En v3b el tiempo que queda está en el bake (7.2 min en 5 caps) y el stitch (5.2 min).

## Lo que queda abierto
1. **Metas de tiempo no alcanzadas** (32.4 / 37.1 min). El bake de 70–110 s por cap es lo más grande que queda (las escenas se cuecen de a 3; `perspective` ya usa hilos).
2. **«El resto del cap ≥ 0.98»**: ch04 da **0.978** en sus escenas no cocidas (3D); ch01, ch02, ch03 y ch07, 0.981–0.984. En ch05 y ch06 no hay resto.
3. **El dissolve del stitch es lineal** (HF: sine.inOut) y la escena cocida dentro de una ventana HF entra con el seek de `<video>` (un cuadro tarde en algunos cortes que dibuja HF).
4. **Dos cuadros más en el video** (1009.600 → 1009.667 s: ch02 y ch05 salen con un cuadro más que en v3).
5. Bugs de v3 que v3b corrige sin buscarlo (no es «salir igual»): el salto del dissolve desde un push de rostro (freeze centrado de `_freeze_img`) y la última escena sin su movimiento seguro (`compose_sparse`). `compose_sparse` sigue con ese redondeo: ya no afecta a las escenas cocidas.
6. La costura gris/blanca entre caps (C.3) y los colores: el base cocido sale sin etiquetas de color (como el base de siempre) y la unión con HF (bt709) lo convierte igual que antes.
7. Firefox se volvió a abrir dos veces durante la tanda; lo cerré con cierre normal antes de cada render.

Archivos: `f30_vajont.py` (copia del topic y corridas), `f30_ssim.py`, `f30_ssim_d.py`, `f30_planes.py`, `f30_stitch_enc.py`, `f30_costura.py`; corridas en `corridas/{a_bake,b_stitch,c_w8}/` (los mp4 por hardlink, fuera de git), `c/`, `d/`.


## Veredicto del revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

Verifiqué el reporte contra el código de los commits 94d9496, 537416f y 7ac4ef8, los json y logs de lab/hyperframes/f30, y los mp4 de output/. Corrí `python -I -m pytest test_module_f30.py test_module_gfx_router.py test_module_gfx_sparse.py`: 22 verdes (10 son de f30, como dice el reporte). Medí a mano el SSIM de ch05 entre v3 y v3b. No corrí renders.

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | A: las escenas safe las cuece ffmpeg en el base, `event_windows` ya no abre ventana safe, y las safe cocidas van como `<video>` | OK | gfx_safe_bake.py; gfx_sparse.py `safe_windows=False`; gfx_layer.py `_replace(s, safe=None)`. Cobertura de ch06 100 → 31 % y HF 593 → 259 s, según a_bake/gfx_ch06.log:45,48 |
| 2 | A: `zoompan` del handoff | PARCIAL (declarado) | Se usó `perspective` por medida (SSIM 0.77–0.83 con zoompan). La medida está citada en el docstring y el commit, pero no hay un artefacto aparte con ella |
| 3 | A.4: SSIM ≥ 0.95 en las escenas safe; hoja de contactos | PARCIAL | La hoja existe (hoja_safe_ch06.jpg). Con el código final (b_stitch/ssim_ch06_escenas.json) la escena 1 (paneo) da 0.9485 y la escena 8 (paneo) 0.9506. El reporte cita 0.951 y «0.951–0.980» de la corrida A |
| 4 | B: transiciones al stitch, mismas en instante y tipo, grafo y tests | OK | gfx_sparse_ch06.json: 15 transiciones, 13 en el stitch. f30_planes.py da 0 claves distintas en los 7 caps (lo corrí). No hay un volcado «antes» de `transitions_of`; el reporte lo infiere de la igualdad de planes |
| 5 | B: dissolve, dip y cut_punch como los hace HF | PARCIAL (declarado) | Dissolve lineal (HF usa sine), dip con `fade`, cut_punch 1.02 → 1 como el templater (gfx_project.py:541); el handoff decía 1.0 → 1.06 → 1.0. La ventana por transición se conserva si la transición toca un bloque o no tiene aire |
| 6 | B.5: SSIM de 5 cortes de ch06 ≥ 0.95 | OK | ssim_ch06_cortes.json: 0.957–0.979. El flash de 104.97 s lo dibujó HF, así que no mide el flash del stitch |
| 7 | C.1: workers 5 → 8 | OK | HF 126.8 s con 5 contra 156.9 s con 8 (logs de b_stitch y c_w8); RAM libre mín. 12.97 → 11.98 GB. Queda en 5 (`workers = 5` en gfx_config.py:47) |
| 8 | C.2: NVENC en el stitch | OK | stitch_encoder.json: 86.0 → 52.2 s, 1.25 → 0.19 GB, SSIM 0.9805. Hay fallback a libx264 y un test |
| 9 | C.3: costura entre caps, solo medida | OK | costura_f8s3-vajont-f29.json: gris y blanco aparecen primero en `_concat_video.ts`, cuadros 2959–2962 y 10868–10870; en el mp4 final, 75 cuadros después. Sin arreglo |
| 10 | D: v3b con los planes de v3, salida en la ruta pedida | OK | v3b.mp4 existe (1.06 GB). Pared 37.0 min (fase2b_d.out); gfx 32.4 min (suma de v3b_tiempos.json); costo US$ 0.0000 |
| 11 | D: gfx ≤ 20 min, pared ≤ 30 min, SSIM ≥ 0.95 donde se midió | FALLA (declarado en tiempos) | Los tiempos no se cumplen: gfx 32.4 y pared 37.1 min. El SSIM no cumple en todo lo medido: ssim_d.json da ch05 safe 0.942 y cap 0.945, ch02 safe 0.946, ch04 «resto» 0.978 (<0.98). El reporte acota el «≥ 0.95» a ch06 |
| 12 | Candados: md5 de ch02 sin `--gfx`, suites, nada prohibido en git | OK | md5 `38e5ba14…` en a/b/c; la suite amplia deja 5 fallas previas conocidas (01b_pauses ×3, m03_merge_timing ×2). Ningún commit toca .env, config.py, _gpt_probe_analista ni gfx_profiles |

Observaciones (las dos primeras son las más graves):
1. **Decisión sobre la etapa 3 sin justificar.** El reporte no la menciona. El pedido manda frenar si el SSIM no da lo que pide el handoff, y D tiene ch05 en 0.942/0.945, ch02 en 0.946 y ch04 «resto» en 0.978. El reporte explica la última escena de ch02 y ch05 como un defecto de v3. Esa explicación es plausible: medí ch05 de 145 a 165 s y da 0.80, y la imagen d/ultima_escena_v3_vs_v3b.jpg la respalda. Pero las cifras por escena («0.94–0.98», ch05 escena 4 = 0.940) no están en ningún archivo commiteado, y 0.940 sigue siendo menor que 0.95. Además, el árbol de trabajo ya tiene trabajo de la etapa 3 sin commitear: la bandera `--rotulista` en fase2b.py y la carpeta lab/hyperframes/f29b/b/. Eso es previo a este veredicto.
2. **Afirmación inexacta en B.** El reporte dice que los cuadros más bajos de ch06 (0.63–0.81) son 4 dissolves. El mínimo real del cap es 0.4931, y el reporte de D lo repite como 0.491 sin explicarlo. Medí ch06 completo y el 0.491 es un solo cuadro, el 4037 (134.57 s), en el corte seco de la escena 14. Ahí v3 y v3b difieren en un cuadro, lo que toca «mismos instantes». También salen 0.64–0.68 en el dissolve de 149.6 s y en el de 123.9 s.
3. **Valor de A.4 sobre código que ya cambió.** El reporte cita 0.951 de la corrida A; el código final da 0.9485 en la escena 1. La condición ≥ 0.95 se cumple con holgura mínima y solo en la corrida intermedia.
4. **Base de comparación.** «67.0 → 37.1 min» usa el intento 1 de v3. El v3 final del handoff fue 63.9 min (ESTADO_SESION y F29_REPORT). Contra 63.9 la baja es 42 %, no 45 %.
5. **Desvíos declarados, pero decididos por CC.** perspective en vez de zoompan, copia del topic f8s3-vajont-f30 en vez de correr sobre f29, dissolve lineal, cut_punch 1.02 → 1 y las transiciones que siguen en HF si tocan una ventana. El handoff decía «quitar» las ventanas por transición, y el reporte lo declara. «Resto ≥ 0.98» no se cumple en ch04 (0.978) y el reporte lo dice. El criterio «resto ≥ 0.98» no aplica en ch05 ni ch06, donde no hay escenas fuera del bake.
6. **Cambio visible respecto de v3.** La última escena de ch02 y ch05, y los dissolves desde un push de rostro, ahora salen distintos a v3 (el reporte lo declara en «Lo que queda abierto» 5). Tampoco se mantiene la «duración exacta»: ch02 y ch05 ganan 1 cuadro cada uno. Está en «Lo que queda abierto» 4, dentro de ±1 cuadro.
7. **Registro y evidencia.** La parte D no tiene commit. La sección del revisor en F30_REPORT.md dice «pendiente», y falta la entrada de la tanda en ESTADO_SESION. El log de la suite de A que está commiteado muestra 6 fallas (antes de adaptar el test del router); no hay log commiteado con las 945 verdes que cita el reporte. La suite de C (951 verdes + 5 previas) sí está en el log.

Fuera de alcance: ninguno en los 3 commits de F30. El cambio previo de gfx_project.py viene de 5ae6177 (F29b A). Sin commitear en el árbol y ajenos a F30: fase2b.py (bandera `--rotulista` de la etapa 3), gfx_profiles/*, diag_234_cap4.py, lab/hyperframes/f28/a/f28a.log.

Riesgos que el contrato no cubre: 1) `_render_sparse` pone `safe=None` en todas las escenas aunque `plan_bake` salte alguna (sin PNG o de menos de 2 cuadros); esa escena perdería su movimiento seguro en silencio. 2) El stitch usa NVENC aunque se pase `--sw-encode`; el candado md5 solo cubre el camino sin `--gfx`. 3) La costura gris/blanca entre caps y los 70–110 s de bake por cap quedaron abiertos.

**Después del veredicto (CC):** obs. 1 → **PARADA antes de la etapa 3** (sección de arriba): leído estricto, el SSIM no da lo que pide el handoff, así que F29b B no corrió. Lo preparado para la etapa 3 y sin correr: `lab/hyperframes/f29b/b/` (hoja_bloques.py, f29b_vajont.py, f29b_tabla.py) y la bandera `--rotulista` de fase2b, sacada del árbol y guardada como `lab/hyperframes/f29b/b/fase2b_rotulista_flag.patch`. Las cifras por escena de D quedaron en `d/ssim_d_por_escena.json`. Obs. 2, 3 y 4 → corregidas en el texto (0.491 = cuadro 4037, donde v3 repite el anterior; A.4 con el código final, 0.9485; base 63.9 min). Obs. 7 → D commiteado con este reporte y ESTADO actualizado; la suite de A con 945 verdes no se puede volver a correr sobre ese commit sin cambiar de rama: queda el log con 944 + 6 (la 6.ª, el test del router, se adaptó en el mismo commit). Los riesgos 1 (una escena que `plan_bake` saltea pierde su movimiento seguro) y 2 (NVENC con `--sw-encode`) quedan anotados, sin tocar.
