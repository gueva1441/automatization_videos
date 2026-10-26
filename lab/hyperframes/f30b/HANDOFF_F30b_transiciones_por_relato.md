# HANDOFF F30b — Transiciones por relato y costura entre capítulos

Analista · 2026-10-26 · Para CC. Base: el commit final de F29c. Tres partes A→C; **PARADA al final de C**. API: 0 (planes de gfx de F29c en caché; el rotulista no se vuelve a llamar). Banco: `f8s3-vajont-f30`. **Una variable: qué transición va dónde, y cómo se une un cap con el siguiente.** Bloques, sellos, subtítulos (salvo la chascada §C.3) y velocidad no entran.

## 0. Constantes y de dónde salen
| constante | valor | origen |
|---|---|---|
| fundido cruzado | 20 cuadros | identidad de Omar (F3, `gfx_rules.crossfade_frames`) |
| dip a negro | 10 cuadros | identidad (F3, `gfx_rules.dip_frames`) |
| `zoom_punch` | el del inventario (`transition_config`: 1.0→1.4 saliente / 1.4→1.0 entrante, 400 ms) | ya existe, sin uso |
| aire del title card | = `gfx_rules.title_dur` (3 s, identidad F3) | valor existente; el título dura lo que ya dura, solo que **sin voz encima** |
| flash blanco | **no existe más** (ni dentro del cap ni entre caps) | decisión de Omar (25-10, 21:48) |
| regla general | corte por defecto; cada transición con una razón nombrable | decisión de Omar |

## A. Transiciones dentro del cap (código, `gfx_style.identity_transitions` → reescrita; `emotional_rank` deja de decidir)
Por cada corte de escena (escena entrante `s`), en este orden; la primera que aplica, manda:
1. **La escena saliente tuvo lupa** (`evidence_zoom` terminó en ella) → `cut` («después de la lupa»). Nunca si no hubo lupa (hoy se dispara sin ella en ch02–04).
2. **El corte es el más cercano a `pico.t`** dentro del beat `pico` del cap (uno por cap) → `zoom_punch` («pico»). Si el pico no tiene corte de escena en su beat, no hay punch.
3. **Cambia el beat** (la escena entrante pertenece a otro beat que la saliente, según las ventanas de `gfx_beats_chNN.json`) → `dissolve` («cambio de beat»).
4. **Salta la fecha** (arranca un `time_ticker` en la escena entrante) → `dissolve` («salto de tiempo»).
5. **Última escena del cap** (la que lleva la pregunta de cierre) → `dip` («cierre»).
6. Todo lo demás → `cut`.
Quedan fuera: «≥ 1 corte cada 3», «1 fundido por cap», «ritmo rápido», «mismo lugar», `flash`, `cut_punch`, `R1/R2/R3`. `gfx_style.py` conserva movimientos y punches; solo cambia `identity_transitions`. Las transiciones siguen saliendo por el stitch (F30 B) o por HF cuando caen en ventana, sin cambios ahí. Tests: un cap de 6 escenas con lupa, pico, cambio de beat, ticker y cierre produce [cut, punch, dissolve, dissolve, dip]; sin lupa no hay cut «después de la lupa»; máx 1 punch por cap; `emotional_rank` no cambia nada.

## B. Costura entre capítulos (fase2b / `transition_applier` / `concat_windowed`)
1. **Entre caps: negro.** `whip_pan_flash` (`fadewhite`) fuera del camino de este perfil: la unión cap→cap es el `black_hold` que ya existe al final del cap (1 s, F2) y el cap siguiente **entra desde negro con un fundido de `dip_frames`**. Ningún `fadewhite` en ningún lado (`grep` en el reporte).
2. **Sin cuadro gris.** Diagnosticar en `concat_windowed` por qué aparece el cuadro de luma 140 en la frontera (F30 C.3 lo ubicó en `_concat_video.ts`) y eliminarlo. Medida: a 30 fps, en los 10 cuadros alrededor de cada una de las 6 fronteras del mp4 final, ningún cuadro plano que no sea negro.
3. **Title card con aire.** El cap arranca con el title card sobre su primera imagen **sin voz** durante `title_dur`; la voz, los subtítulos, la música del cap, el mapa de intensidad y los tiempos del plan gfx se desplazan `title_dur` **completos** (es un pre-roll del cap, no un recorte: nada del cap cambia salvo que empieza `title_dur` después). El reloj (`time_ticker`), si arranca en 0, arranca al salir el title card. Medidas: md5 del `.wav` de voz de cada cap **idéntico** al de F29c; duración total = v4 + 7 × `title_dur`; cada bloque del plan gfx aparece en el mp4 exactamente `title_dur` después que en v4 (3 bloques medidos a cuadro); la pregunta de cierre y el black_hold no cambian de duración.
4. Tests: la unión produce `fadeblack`/negro y nunca `fadewhite`; el pre-roll desplaza subs, plan y música exactamente `title_dur`; el `.wav` de voz no se toca.

## C. Render v5 y chascadas
1. `fase2b f8s3-vajont-f30 --reuse-visuals --gfx --gfx-sparse --rotulista` con los planes de F29c en caché (bloques idénticos a v4: verificar con el comparador de planes de F30 D). Salida `output/f8s3-vajont-f30/f8s3-vajont_final_gfx_v5.mp4`. Firefox cerrado.
2. Tabla: por cap, transiciones v4 → v5 (tipo e instante, con su razón: lupa / pico / beat / tiempo / cierre / corte); tiempo de gfx y pared (comparar con v4); las 6 fronteras medidas (B.2); el desplazamiento medido (B.3). Hoja `lab/hyperframes/f30b/COSTURAS_v5.jpg`: por frontera, los 12 cuadros de la unión (negro → title card → primera imagen con voz).
3. **Chascada subtítulos:** al generar el `.ass` en `fase2b.py`, quitar `«`, `»` y `…` del texto (Anton dibuja `»` como `>>`). **Freno:** solo en la generación del `.ass`; el texto que va a ElevenLabs y el sync map no se tocan; md5 del `.wav` de voz idéntico. Test: una línea con «cita» sale sin comillas y con los mismos tiempos.

## Frenos
- No se tocan: bloques del rotulista, sellos, `gfx_templates` (salvo que el pre-roll lo exija para el title card: anotar), m03, voz, música (solo se desplaza), prompts.
- Ningún número nuevo fuera de la tabla §0. Un commit por parte. Sin merge, sin publicar, sin borrar. `.env`, `config.py`, `lab/_gpt_probe_analista/`, `gfx_profiles/*` fuera de git. `--only-cap ch02` sin `--gfx` byte-idéntico con `--sw-encode` (el pre-roll y la chascada solo con `--gfx`; si el pre-roll tiene que vivir sin `--gfx`, anotar y medir el md5 nuevo). `lab/ESTADO_SESION.md` al final.

## Reporte `lab/hyperframes/f30b/F30b_REPORT.md`
A: diff y tabla de transiciones con razón. B: diagnóstico del gris, md5 de voz, desplazamiento medido. C: `_v5.mp4`, hoja de costuras, tiempos. Veredicto íntegro del revisor-handoff. **PARADA.**
