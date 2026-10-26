# F33 — Infraestructura: que el proceso viva en archivos, no en cabezas · REPORTE

CC · 2026-10-26 · rama `f11-guion-v4`, base `cd60c74` (F32 C). Handoff `HANDOFF_F33_infraestructura.md`. Pedido de Omar:
A → E, un commit por parte. **Ningún render, ningún cambio de regla, prompt, plantilla ni valor del pipeline**: el
video no cambia (md5 de ch02 sin `--gfx` `38e5ba14…` en cada commit). API: US$ 0.
Commits: **A `651cb25`** · **B `f97c6f1`** · **C `2d87032`** · **D `ba7e958`** · **E** = el commit de este reporte.

## A — `DECISIONES.md`, la ENTRADA y el origen de las constantes (`651cb25`)
1. `DECISIONES.md` (raíz) y `lab/hyperframes/f32/ENTRADA_ANALISTA_2026-10-26.md` entraron **tal como estaban** (sin
   editar). Lo que no cuadra con el repo (para el analista; no se tocó):
   - DECISIONES, «Velocidad»: «2026-10-25 · 8 workers no mejoran (medido); se queda en 5 · aplicada F30 C». La medida es de
     F30 C, commit `7ac4ef8` del **2026-10-26 00:44**.
   - DECISIONES, último ítem de infraestructura: «Este archivo leído por el código (`gfx_config` carga constantes desde
     aquí)» **no se hizo en F33** (el handoff pide comentarios de origen, no cargar el archivo).
   - ENTRADA §2: «agua/lupa/contador **sin quién los proponga** desde F29b». Desde F32 B.7 los propone el rotulista
     (cifra con unidad → agua o contador; lupa → zoom); en Vajont no salió ninguno.
   - ENTRADA §2 manda pasar el DEBERÍA a `lab/hyperframes/f32/REVISION_GUION.md`, que **no existe** (es del analista).
     Los `claude/…` que cita son de la carpeta del analista, no del repo. Los 14 commits que lista existen.
2. `test_constantes_con_origen.py` (modo inventario; `CONSTANTES_ESTRICTO=1` lo vuelve estricto): recorre con el AST las
   clases `GfxRules` y `GfxRenderSettings` (`gfx_config.py`) y `TransitionRenderSettings` (`transition_config.py`); toda
   constante numérica (int/float, o dict/tupla de números) tiene que tener en su línea `# DECISIONES: …`, `# identidad
   F3`, `# estándar: …`, `# derivado: …` o `# medido: …`. **101 constantes · 35 con origen · 66 sin origen.**
   CC etiquetó (solo comentarios; el test verifica que ningún valor cambió):
   - **33 «identidad F3»**: las que valen lo mismo que el token del perfil `gfx_profiles/misterio.json` (la identidad
     que Omar guardó en F3): `title_dur`, `title_fade_out`, `title_scale`, `title_dim`, las 8 del callout, `zoom_scale`,
     `zoom_hold_min_sec`, `zoom_conf_min`, las 8 del recorte, `count_dur`, `count_hold_sec`, `punch_in_sec`,
     `transition_frames`, `dip_frames`, `flash_*` (3), `question_pause_sec`, `mood_dur`;
   - **2 por DECISIONES**: `crossfade_frames` (fundido 20 f, 2026-10-25 21:48) y `gfx_render.workers` (5).
   - Las 11 que el perfil **pisa con otro valor** (`interrupt_*`, `punch_scale`, `question_dim`, `question_max_words_auto`,
     `black_hold_sec`, `ticker_min_times`, `emphasis_stamp_px`, `icon_px`, `grain_opacity`, `vignette_opacity`) quedan sin
     etiqueta: el valor del motor no es el de la identidad (la tabla trae los dos). Los 15 cps de lectura viven en
     `gfx_rotulista.LECTURA_CPS` (fuera de estas clases; ya dicen «estándar de subtitulado» en su comentario).
3. `CLAUDE.md`: primera línea nueva «Leé `DECISIONES.md` antes de cualquier tanda; un número que no esté ahí, en la
   identidad F3 o en un estándar citado, no entra al código».

### Inventario de constantes sin origen (para que Omar y el analista las clasifiquen)
