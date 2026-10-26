# F30b — Transiciones por relato y costura entre capítulos · REPORTE

CC · 2026-10-26 (tanda nocturna) · rama `f11-guion-v4`, base = F29c B `e852788`. Handoff `HANDOFF_F30b_transiciones_por_relato.md`; tanda `../f29c/PROMPT_CC_tanda_nocturna_F29c_F30b_F31.md` (etapa 2).
Tres commits, uno por parte (ver «Commits» abajo). Costos: **Claude US$ 0** (el rotulista salió de caché) · **Gemini US$ 0.0021** (ver C) · ElevenLabs 0.

**En una línea:** v5 sale con las transiciones nuevas (corte por defecto; `zoom_punch` en el pico de 6 caps; `dissolve` en cambio de beat y salto de fecha; `dip` al cierre), **las 6 costuras en negro sin un solo cuadro plano gris ni blanco**, el title card con **3 s de aire** en cada cap (voz `.mp3` idéntica, cada segmento exactamente +3.000 s, los bloques entran 90 cuadros después) y los subtítulos sin `«»…`. El pre-roll entró sin tocar la voz ni el md5 de ch02 sin `--gfx`.

## A — Transiciones dentro del cap (`gfx_style.transiciones_por_relato`)
Por cada corte (escena entrante), la primera que aplica: (1) la saliente tuvo lupa → `cut` «después de la lupa»; (2) el corte más cercano a `pico.t` dentro del beat pico (uno por cap) → `zoom_punch` «pico»; (3) cambia el beat → `dissolve` 20 f «cambio de beat»; (4) arranca el reloj en la entrante → `dissolve` 20 f «salto de tiempo»; (5) última escena → `dip` 10 f «cierre»; (6) el resto → `cut` «corte». El `emotional_rank` no decide nada; no quedan `flash`, `cut_punch`, «≥ 1 corte cada 3», «1 fundido por cap», «ritmo rápido» ni «mismo lugar».
- Corre **después del crítico** (en `gfx_layer`, tras `cerrar`), sobre el plan final: una lupa que el crítico saca no deja su corte (en v3/v4 el «después del zoom» se disparaba sin lupa). Solo con escaleta (realizador); sin escaleta queda `identity_transitions` de siempre.
- `zoom_punch` (el del inventario: 1.0→1.4 saliente / 1.4→1.0 entrante, 400 ms = 12 cuadros, mitad y mitad): en el stitch, dos segmentos con `zoompan` (`zp_out` sobre los 6 cuadros reales antes del corte, `zp_in` sobre los 6 después); en HF, como HyperFrames no escala `<video>`, el primer/último cuadro fijo encima con la escala animada. **En v5 los 6 los dibujó el stitch** (ninguno cayó en una ventana HF). Cuadro a cuadro del de ch06: `b/zoom_punch_ch06.jpg`.

| cap | cortes | v4 (conteo por tipo) | v5 (conteo por tipo) · escena del punch / dissolve / dip |
|---|---|---|---|
| ch01 | 0 | — (una sola escena: híbrido Veo) | — |
| ch02 | 12 | dissolve 6 · cut 3 · dip 1 · flash 1 · cut_punch 1 | cut 10 · zoom_punch 1 (esc. 8, pico) · dip 1 (esc. 12, cierre) |
| ch03 | 12 | dissolve 6 · cut 4 · dip 1 · flash 1 | cut 9 · zoom_punch 1 (esc. 1) · dissolve 1 (esc. 7, cambio de beat) · dip 1 (esc. 12) |
| ch04 | 10 | dissolve 5 · cut 3 · dip 1 · flash 1 | cut 6 · dissolve 2 (esc. 1 salto de tiempo, esc. 6 cambio de beat) · zoom_punch 1 (esc. 7) · dip 1 (esc. 10) |
| ch05 | 14 | dissolve 8 · cut 4 · dip 1 · flash 1 | cut 11 · zoom_punch 1 (esc. 2) · dissolve 1 (esc. 11) · dip 1 (esc. 14) |
| ch06 | 15 | dissolve 9 · cut 4 · dip 1 · flash 1 | cut 12 · zoom_punch 1 (esc. 2) · dissolve 1 (esc. 12) · dip 1 (esc. 15) |
| ch07 | 14 | dissolve 9 · cut 4 · dip 1 | cut 11 · zoom_punch 1 (esc. 1) · dissolve 1 (esc. 9) · dip 1 (esc. 14) |
Detalle escena por escena con razón en `b/medidas.json` → `transiciones`. En ch02 el corte de cambio de beat (2→3) es el mismo que el del pico: gana el punch (orden del handoff). Ningún cap tuvo lupa (el rotulista no propuso ninguna en v4).

## B — Costura entre capítulos
### B.1 Entre caps: negro
Con `--gfx`, `concat_windowed(negro_frames=dip_frames)`: cada unión es un corte **sin solapar** (el cap saliente ya termina en su `black_hold` de 1 s) y el entrante **sube desde negro en 10 cuadros** (`fade=in` en la ventana re-codificada); el audio se pega sin `acrossfade`. Si las ventanas fallan, concat seco (nunca el xfade de los perfiles de arte). **Grep de `fadewhite`** (`c/grep_fadewhite.txt`): queda solo en `transition_applier._XFADE_MAP` (`whip_pan_flash`, `fade_to_white`) y en el inventario de `transition_config`, que usa **solo el camino sin `--gfx`**; con `--gfx` las uniones no pasan por ese mapa. *Pendiente de Omar:* ¿sacarlo también del camino sin gfx (el «flash blanco no existe más» de §0 es general)?
### B.2 Sin cuadro gris — diagnóstico
El cuadro gris plano (luma 140) que F30 C ubicó en `_concat_video.ts` era **el paso intermedio del `fadewhite`** de `whip_pan_flash` sobre la cola negra del cap: a mitad del fundido, negro + blanco al 50 % = un gris plano; los 3 blancos siguientes, el resto del flash (aparecía solo en ch01→ch02 y ch03→ch04, las uniones `hook_to_body` y `body_to_climax` del perfil, las que resuelven a `whip_pan_flash`). Sin `fadewhite`, desaparece. **Medida (mp4 final v5, 30 fps, 10 cuadros alrededor de cada frontera): 0 cuadros planos que no sean negros en las 6** — los 5 anteriores al corte son negro puro (luma 0.0, el `black_hold`) y desde el corte la luma sube (p. ej. ch01→ch02: 0.2 · 1.2 · 4.2 · 8.3; ch04→ch05 más clara: 1.0 · 8.2 · 17.8 · 27.4).
### B.3 Title card con aire (pre-roll de `title_dur`)
Con `--gfx` (`gfx_rules.title_pre_roll`, default sí): `fase2b` le agrega al visual base 3 s adelante (su primer cuadro, `tpad clone`: la imagen del title card), y corre `title_dur` completos la voz (`adelay`, el `.mp3` no se toca), los subtítulos, los sfx, el plan gfx (`time_offset`), la música del cap (la pieza se corre con silencio adelante; la envolvente de intensidad se aplica antes, así se corre igual) y el corte del Veo de arranque. El rotulista imprime los tiempos sin el pre-roll (mismo pedido → caché) y el crítico reusa su veredicto por identidad del bloque (`gfx_critic.clave_identidad`: el pre-roll re-codifica el base y cambia los bytes de los cuadros). El reloj que arrancaba en 0 ahora arranca al salir el title card (todo se corre 3 s).
| medida | resultado |
|---|---|
| md5 de la voz de cada cap (`output/audio/f8s3-vajont-f30/chNN.mp3`) | **7/7 idénticos** antes y después de v5 (`b/md5_voz_antes_v5.txt`, `b/medidas.json`) |
| duración total | v4 1009.667 s → v5 **1032.367 s** = v4 + 7 × 3 s (1030.667) **+ 1.7 s**: las uniones de v4 solapaban 1.7 s en total (xfade 200–350 ms); las de v5 no solapan. Cada segmento: **+3.000 s exactos** (7/7) |
| bloques del plan | todos los bloques, el reloj, la pregunta y el black hold: Δ = **+3.000 s** en el plan (21 medidos); la pregunta de cierre (3.0 s) y el black hold (1.0 s) **no cambian de duración** |
| a cuadro (segmentos v4 vs v5, `b/a_cuadro.json`) | ficha D32 (ch07): **+90 cuadros** · sello «fisura» (ch06): **+90 cuadros** · ficha D128 (ch06): +93 (la primera medida, en `medidas.json`, buscaba desde 0.5 s antes y dio 88; `a_cuadro.json` la reemplaza) — en las dos la medida se contamina: en v4 la escena entraba con disolvencia de 20 cuadros desde 123.87 s y la detección la toma antes que la ficha; en v5 el corte es seco. Son los únicos 2 bloques del rotulista de todo el video; el tercero medido es el sello |
| md5 `--only-cap ch02` sin `--gfx` (`--sw-encode`) | **`38e5ba14…`** (pre-roll y chascada solo con `--gfx`) |
### B.4 Tests (`test_module_f30b.py`, 12)
6 escenas con lupa, pico, cambio de beat, reloj y cierre → `[cut, zoom_punch, dissolve, dissolve, dip]`; sin lupa no hay «después de la lupa» y 1 solo punch; pico sin corte en su beat → sin punch; `emotional_rank` no cambia nada; `zoom_punch` en el stitch (mitad y mitad); unión real con ffmpeg sobre dos clips sintéticos: 180 cuadros (sin solapar), ningún blanco, sube desde negro en 10; con `--gfx` nunca el xfade de arte; el pre-roll corre los subtítulos 3 s y la chascada saca `«»…` con los mismos tiempos; el visual gana 90 cuadros; la pieza de música se corre; el rotulista hace el mismo pedido con y sin pre-roll; el crítico reusa el veredicto por identidad.

## C — Render v5 y chascada
- `f30b_vajont.py render`: `fase2b f8s3-vajont-f30 --keep-segments --reuse-visuals --gfx --gfx-sparse --gfx-quality looks --rotulista`, Firefox cerrado, RAM libre 19.2 GB (mín. 14.8). **rc 0, pared 35.4 min** (v4 30.9). Salida **`output/f8s3-vajont-f30/f8s3-vajont_final_gfx_v5.mp4`** (1032.4 s, 968 MB). Lo de v4 quedó en `_fase2b_work/_bak_v4/`.
- **Bloques idénticos a v4**: los mismos 2 del rotulista (D128, D32) con el mismo texto y el mismo veredicto (caché por identidad: 3 cargados), corridos +3.000 s; ningún pedido nuevo a Claude.
- gfx por cap v4 → v5 (s): ch01 107 → 115 · ch02 237 → 237 · ch03 195 → 190 · ch04 200 → 200 · ch05 302 → 285 · ch06 324 → 324 · **ch07 212 → 310**. ch07 (y en menos ch01) son híbridos: la visión mira cuadros sacados del base para las escenas Veo, su caché es por bytes y el base con pre-roll es otro archivo → volvió a llamar a Gemini (el paso de plan de ch07 pasó de 63 a 175 s). Eso y el crítico de los sellos (que también mira bytes) son los **US$ 0.0021** de Gemini. *Pendiente de Omar:* la API no quedó en 0 por eso.
- **Hoja `COSTURAS_v5.jpg`**: por frontera, 12 cuadros: cola del cap saliente (−0.30, −0.15, −1 cuadro), el corte (+0.00, negro), la subida desde negro (+0.13), el title card (+0.30, +1.0, +2.0, +2.9) y la primera imagen con voz (+3.1, +3.5, +4.5: aparecen los subtítulos).
- **Chascada (C.3)**: `_build_ass_from_words(sin_comillas=gfx)` saca `«`, `»` y `…` del texto de cada palabra del `.ass`; los tiempos, los cortes de renglón (se arman con el texto original) y el texto de ElevenLabs no cambian (md5 de la voz idéntico). Test con «basta».

## Lecturas de CC (declaradas)
1. El «beat pico» y `pico.t` son los del plan (los de F29c: `pico_cap`), uno por cap.
2. El fade-in desde negro va en la ventana de la frontera (cabeza del cap entrante), no en el segmento: el segmento sigue arrancando con el title card a pleno; el `--only-cap` no lo muestra.
3. La pieza de música del cap se corre con silencio adelante (literal «se desplazan»): durante el title card no suena la música del cap, solo la cola del anterior por el crossfade de las pistas.
4. El title card dura lo mismo (3 s) y sigue oscureciendo la imagen (`#tc-dim`); el plan no se tocó.
5. `zoom_punch`: curvas cuadráticas (entra acelerando, sale frenando), mitad y mitad del corte; el inventario no da la curva.

## Commits
Tres commits, uno por parte (con staging parcial de `fase2b.py` y `gfx_layer.py`, que tocan las tres): **A** transiciones (`gfx_style`, `gfx_sparse`, `gfx_project`, el bloque de `gfx_layer` que las recalcula); **B** costura y pre-roll (`transition_applier`, `fase2b` sin la chascada, `gfx_config`, `gfx_layer` pre-roll, `gfx_rotulista` pedido sin pre-roll, `gfx_critic` clave por identidad); **C** chascada (`fase2b`), tests, runner, medidas, hojas, reporte y ESTADO. El render v5 corrió con las tres juntas (el árbol de C).

## Veredicto del revisor-handoff (íntegro)

**VEREDICTO: CUMPLE CON OBSERVACIONES**

Corrí `python -I -m pytest test_module_f30b.py -q -p no:cacheprovider` con `PYTHONIOENCODING=utf-8`: 12 passed. Los commits todavía no existen, así que no pude verificar el staging parcial.

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| A1 | Orden de reglas lupa, pico, beat, fecha, cierre, corte | OK | `script_engine/gfx_style.py` `transiciones_por_relato`. Los 6 planes v5 coinciden con la función recalculada desde los logs. |
| A2 | Corre sobre el plan final, después del crítico | OK | `script_engine/gfx_layer.py` ~851, después de `cerrar(...)`. |
| A3 | Sin flash, sin `cut_punch`, sin `emotional_rank`; máx 1 punch por cap; frames 12/20/10 | OK | Planes v5: un `zoom_punch` y un `dip` por cap; ningún flash. |
| A4 | Regla de lupa en datos reales | NO VERIFICABLE | Ningún cap tuvo lupa. Solo la cubre el test. |
| B1 | Entre caps a negro, sin `fadewhite` | PARCIAL | Con `--gfx` la unión es corte más `fade=in` de 10 cuadros. Pero `fadewhite` sigue en `script_engine/transition_applier.py:138,143` y `transition_config.py:113` (camino sin gfx). El handoff dice «en ningún lado»; CC lo declara y lo deja a Omar. |
| B2 | 6 fronteras sin cuadro plano no negro | OK | Re-medí con ffmpeg: 7 cuadros en Y=16 (negro) y luego subida con contraste (max 30 a 190). Ningún cuadro gris plano. |
| B3a | md5 de voz idéntico | OK | Los 7 mp3 coinciden con `b/md5_voz_antes_v5.txt` y su mtime es del 25-10, anterior a F29c. |
| B3b | +3.000 s por segmento | OK | ffprobe: 7/7 exactos. Correlación de audio de ch03 y ch06 contra v4: desfase 3.0 s, r=0.998. |
| B3c | Total = v4 + 7×3 | PARCIAL | v5 1032.367 contra 1030.667 esperado (+1.7 s). Se explica porque v4 solapaba en las uniones; el handoff no lo previó. Declarado. |
| B3d | Desplazamiento de bloques | OK, con una falla | Todos los campos de tiempo de los 7 planes se corrieron exactamente +3.0 s. La pregunta (3.0 s) y el black hold (1.0 s) no cambian de duración. A cuadro: 2 de 3 en +90; D128 da +93 y `medidas.json` da 88, ver observación 4. |
| B3e | Title card sin voz, subs, música y plan corridos | OK | Voz y música entran ~3 s después (RMS). Subtítulos desde +3.1 s en `COSTURAS_v5.jpg`. |
| B4 / md5 ch02 sin gfx | `38e5ba14…` | OK | `c/onlycap_ch02_nogfx.log` coincide con el md5 de F29c. |
| C1 | Render v5 y bloques idénticos a v4 | OK | rc 0, v5.mp4 existe (968 MB). Los textos y bloques del rotulista son iguales a v4; solo cambian los tiempos (+3 s). |
| C2 | Hoja `COSTURAS_v5.jpg` y tabla | PARCIAL | La hoja es correcta: negro, subida, title card, imagen con voz. La tabla de A del reporte está mal, ver observación 1. |
| C3 | Chascada sin `«»…`, mismos tiempos, voz intacta | OK | Conté con Python: 0 `«`, `»` y `…` en los 7 `.ass`. Hay test. |
| Costo | API 0 | PARCIAL | Gemini 0.0021 y Claude 0; el handoff decía 0. Declarado (visión y crítico por bytes). |
| Candados | Sin tocar bloques, sellos, `gfx_templates`, m03, voz, prompts | OK | El diff no incluye ninguno. El cambio en `gfx_rotulista.py` solo resta el pre-roll al imprimir tiempos, y el pedido queda igual (hubo caché). |

**Observaciones**
1. La tabla A del reporte mezcla índices con conteos. «8 zoom_punch», «12 dip», «7 dissolve» son índices de escena; los planes tienen 1 punch, 1 dip y 0 o 1 dissolve por cap. Hay que corregir el texto antes de pegarlo a Omar.
2. El handoff pedía reescribir `identity_transitions`. CC dejó la vieja, con flash y `cut_punch`, para el camino sin escaleta, y agregó una función nueva.
3. Números fuera de §0: curvas cuadráticas (`power2`), mitades `frames//2` (6 cuadros), offsets de 0.5 y 1.5 cuadros en los congelados. Están en la lectura 5 del reporte, pero §0 decía «ningún número nuevo». `ZOOM_PUNCH_SCALE` 1.4 y 400 ms vienen del inventario, y la tolerancia 0.3 ya existía en `gfx_rotulista` y `gfx_realizador`.
4. Evidencia inconsistente sobre D128: `lab/hyperframes/f30b/b/a_cuadro.json` dice 93 cuadros y `b/medidas.json` dice 88. El reporte cita «22 medidos» y el JSON tiene 21.
5. El crítico escribe los snapshots antes de recalcular las transiciones (ver `_criticar` en `gfx_layer.py`). Es un efecto menor.

**Fuera de alcance:** ninguno atribuible a F30b. El árbol tiene `diag_234_cap4.py`, `lab/hyperframes/f28/a/f28a.log`, `gfx_profiles/*.json` y `lab/ESTADO_SESION.md` modificados. Los tres primeros ya estaban modificados en el snapshot inicial (los `gfx_profiles` con mtime 00:57, anterior a F30b) y no deben entrar a los commits. `ESTADO_SESION.md` lo autoriza el handoff. `lab/_gpt_probe_analista/` sigue sin trackear.

**Riesgos que el contrato no cubre**
- ch01 abre con 2.5 s de `INITIAL_SILENCE_SEC` más 3 s de pre-roll. Medí silencio digital en los primeros ~2 s y voz recién cerca de 5.5 s. Para Omar es un arranque largo.
- La música del cap no suena durante el title card (lectura 3 de CC). Entre caps queda solo la cola del anterior.
- La suite amplia da 970 passed y 5 failed según `c/suite_amplia.log`. No la volví a correr; CC dice que los 5 fallos son previos.

**Después del veredicto (CC):**
- Obs. 1: tabla de A corregida (conteos por tipo y, aparte, la escena del punch/dissolve/dip), verificada contra `b/medidas.json`.
- Obs. 2: `identity_transitions` queda para los topics sin escaleta (los viejos); con escaleta corre la nueva. Declarado; si Omar quiere borrar la vieja, es un cambio aparte.
- Obs. 3: las curvas y la mitad/mitad del `zoom_punch` son la forma de un efecto que el inventario define solo por escala y duración (lectura 5); los 0.5/1.5 cuadros de los congelados son el mismo criterio de `_extract_freeze` de siempre (F2 §0b.4). Pendiente de Omar si quiere otra curva.
- Obs. 4: corregido el «22» → 21 y aclarado que la medida de D128 de `a_cuadro.json` (93) reemplaza la primera (88); las dos están contaminadas por la disolvencia de v4.
- Obs. 5: los snapshots del crítico se dibujan antes de recalcular las transiciones; no cambia ningún veredicto (el crítico mira el bloque, no el corte). Queda anotado.
- Riesgo 1 (arranque de ch01: 2.5 s de intro + 3 s de pre-roll ≈ 5.5 s sin voz): pendiente de Omar.
- Riesgo 2 (música del cap muda durante el title card): pendiente de Omar (lectura 3).

