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
101 constantes numéricas · 35 con origen · **66 sin origen**

| # | constante | valor del motor | valor del perfil (si lo pisa) | archivo:línea | comentario de hoy |
|---|---|---|---|---|---|
| 1 | `GfxRenderSettings.timeout_sec` | `1500` |  | gfx_config.py:48 | por cap; excedido → fallback a base_clip (F29: 900 → 1500; con caps de |
| 2 | `GfxRenderSettings.player_ready_timeout_ms` | `240_000` |  | gfx_config.py:50 | lab v2: 45 s default no alcanza a 1440p |
| 3 | `GfxRenderSettings.protocol_timeout_ms` | `600_000` |  | gfx_config.py:51 |  |
| 4 | `GfxRenderSettings.reencode_gop` | `30` |  | gfx_config.py:56 |  |
| 5 | `GfxRenderSettings.reencode_crf` | `14` |  | gfx_config.py:57 |  |
| 6 | `GfxRules.rotulista_tope_usd` | `2.0` |  | gfx_config.py:223 | F29b: tope Claude de la tanda, chequeado antes de cada llamada |
| 7 | `GfxRules.interrupt_min_sec` | `25.0` | 12.0 | gfx_config.py:225 | pattern interrupt: un bloque cada 25–35 s |
| 8 | `GfxRules.interrupt_max_sec` | `35.0` | 18.0 | gfx_config.py:226 |  |
| 9 | `GfxRules.zoom_rect_sec` | `0.65` |  | gfx_config.py:251 |  |
| 10 | `GfxRules.zoom_approach_sec` | `1.2` |  | gfx_config.py:252 |  |
| 11 | `GfxRules.zoom_box_min` | `0.06` |  | gfx_config.py:256 | lado mínimo del box normalizado |
| 12 | `GfxRules.zoom_box_max` | `0.25` |  | gfx_config.py:257 |  |
| 13 | `GfxRules.zoom_label_margin_px` | `40` |  | gfx_config.py:258 | "DETALLE" a ≥ 40 px del borde |
| 14 | `GfxRules.archive_max_per_cap` | `2` |  | gfx_config.py:262 |  |
| 15 | `GfxRules.archive_min_scene` | `4.0` |  | gfx_config.py:270 | la escena de inicio debe dar aire al recorte |
| 16 | `GfxRules.archive_min_sec` | `4.0` |  | gfx_config.py:271 |  |
| 17 | `GfxRules.punch_scale` | `1.025` | 1.015 | gfx_config.py:277 |  |
| 18 | `GfxRules.punch_out_sec` | `0.4` |  | gfx_config.py:280 | solo si punch_hold=False |
| 19 | `GfxRules.cut_snap_window_sec` | `0.3` |  | gfx_config.py:285 | el corte se ancla al cambio REAL de imagen (±0.3 s del anchor) |
| 20 | `GfxRules.r1_cut_punch_scale` | `1.02` |  | gfx_config.py:289 |  |
| 21 | `GfxRules.cascade_stagger` | `0.025` |  | gfx_config.py:297 | 25 ms por letra |
| 22 | `GfxRules.cascade_rise_px` | `60` |  | gfx_config.py:298 |  |
| 23 | `GfxRules.stamp_from_scale` | `1.4` |  | gfx_config.py:299 |  |
| 24 | `GfxRules.stamp_rotation` | `-3.0` |  | gfx_config.py:300 |  |
| 25 | `GfxRules.stamp_sec` | `0.18` |  | gfx_config.py:301 |  |
| 26 | `GfxRules.pop_from_scale` | `1.08` |  | gfx_config.py:302 |  |
| 27 | `GfxRules.pop_sec` | `0.25` |  | gfx_config.py:303 |  |
| 28 | `GfxRules.safe_push_scale` | `1.08` |  | gfx_config.py:305 | push-in 1.00 → 1.08 con easing |
| 29 | `GfxRules.safe_pan_frac` | `0.03` |  | gfx_config.py:306 | paneo 3 % del ancho |
| 30 | `GfxRules.safe_bake_workers` | `3` |  | gfx_config.py:308 | F30 §A: escenas cocidas a la vez (perspective ya usa hilos por franjas) |
| 31 | `GfxRules.question_dur` | `2.3` |  | gfx_config.py:311 | 2.0–2.5 s al cierre del cap |
| 32 | `GfxRules.question_dim` | `0.5` | 0.7 | gfx_config.py:312 |  |
| 33 | `GfxRules.question_max_words` | `9` |  | gfx_config.py:313 |  |
| 34 | `GfxRules.question_font_px` | `96` |  | gfx_config.py:314 |  |
| 35 | `GfxRules.question_max_words_auto` | `12` | 8 | gfx_config.py:317 | F3: tope de la pregunta generada |
| 36 | `GfxRules.black_hold_sec` | `0.0` | 1.0 | gfx_config.py:318 | F3: corte a negro después de la pregunta de cierre (se suma a la pausa) |
| 37 | `GfxRules.fast_cut_sec` | `3.5` |  | gfx_config.py:323 | plano de < 3.5 s (entrante o saliente) → corte (ritmo rápido) |
| 38 | `GfxRules.dip_max_per_cap` | `1` |  | gfx_config.py:324 | fundido a negro: 1 por cap |
| 39 | `GfxRules.dip_min_t` | `10.0` |  | gfx_config.py:325 | …no antes de los 10 s (el título abre el cap) |
| 40 | `GfxRules.punch_max_identity` | `4` |  | gfx_config.py:326 | golpes de zoom por cap (F4 §1.2.1: Omar aprobó la forma, no 8) |
| 41 | `GfxRules.icon_stamp_px` | `112` |  | gfx_config.py:327 | sello dentro del bloque de ícono: M (F4 §1.2.3), aunque el suelto sea S |
| 42 | `GfxRules.ticker_min_times` | `0` | 2 | gfx_config.py:328 | F4: el reloj solo sale con ≥ N horas verificadas (misterio: 2) |
| 43 | `GfxRules.archive_head_max_words_pool` | `12` |  | gfx_config.py:343 | F5e G2: titular del recorte del pool hasta 12 palabras (> 8 → cuerpo menor) |
| 44 | `GfxRules.archive_min_gap_sec` | `15.0` |  | gfx_config.py:345 | mínimo entre el fin de un recorte y el arranque del siguiente |
| 45 | `GfxRules.archive_figure_echo_sec` | `10.0` |  | gfx_config.py:346 | un recorte con una cifra que la voz dice a ± esto queda fuera |
| 46 | `GfxRules.quote_dur` | `5.0` |  | gfx_config.py:347 | bloque cita: texto literal + autor, 4–5 s, fondo oscurecido |
| 47 | `GfxRules.quote_min_sec` | `4.0` |  | gfx_config.py:348 |  |
| 48 | `GfxRules.quote_dim` | `0.6` |  | gfx_config.py:349 |  |
| 49 | `GfxRules.quote_max_words` | `30` |  | gfx_config.py:350 |  |
| 50 | `GfxRules.quote_min_words` | `6` |  | gfx_config.py:351 | «donde pertenecen» (2) no es un bloque de cita |
| 51 | `GfxRules.source_tag_scale` | `0.4` |  | gfx_config.py:356 | 40 % del tamaño del callout |
| 52 | `GfxRules.sfx_gain_db` | `-18.0` |  | gfx_config.py:357 | bajo la voz |
| 53 | `GfxRules.sfx_shift_max_ms` | `120` |  | gfx_config.py:358 | se corre al hueco entre palabras más cercano |
| 54 | `GfxRules.emphasis_base_per_cap` | `3` |  | gfx_config.py:360 | selección inicial (las más raras); el relleno de huecos sube hasta max_per_cap |
| 55 | `GfxRules.emphasis_same_cat_gap_sec` | `20.0` |  | gfx_config.py:361 | mínimo entre moods de la misma categoría |
| 56 | `GfxRules.emphasis_stamp_sec` | `1.6` |  | gfx_config.py:364 | el sello se ve 1.6 s dentro del mood |
| 57 | `GfxRules.emphasis_stamp_px` | `112` | 84 | gfx_config.py:365 |  |
| 58 | `GfxRules.icon_px` | `190` | 360 | gfx_config.py:367 | lado del ícono del icon_callout |
| 59 | `GfxRules.icon_array_max` | `500` |  | gfx_config.py:369 |  |
| 60 | `GfxRules.icon_array_dur` | `4.0` |  | gfx_config.py:370 |  |
| 61 | `GfxRules.icon_array_px` | `34` |  | gfx_config.py:371 | lado de cada figura |
| 62 | `GfxRules.grain_opacity` | `0.15` | 0.0 | gfx_config.py:374 | F2 §0c: tokens del perfil (antes constantes de _GRADE_OFF) |
| 63 | `GfxRules.vignette_opacity` | `0.20` | 0.15 | gfx_config.py:375 |  |
| 64 | `GfxRules.grain_jumps_per_sec` | `12` |  | gfx_config.py:376 |  |
| 65 | `TransitionRenderSettings.crf` | `18` |  | transition_config.py:30 | CRF=18 mantiene calidad cinematográfica |
| 66 | `TransitionRenderSettings.fps` | `30` |  | transition_config.py:33 | debe coincidir con flow_render.fps |

Con origen:

- `GfxRenderSettings.workers` = `5` · DECISIONES: 2
- `GfxRules.title_dur` = `3.0` · identidad F3
- `GfxRules.title_fade_out` = `0.4` · identidad F3
- `GfxRules.title_scale` = `0.7` · identidad F3
- `GfxRules.title_dim` = `0.4` · identidad F3
- `GfxRules.callout_dur_min` = `2.5` · identidad F3
- `GfxRules.callout_dur_max` = `6.0` · identidad F3
- `GfxRules.callout_dur` = `2.5` · identidad F3
- `GfxRules.callout_sec_per_word` = `0.4` · identidad F3
- `GfxRules.callout_base_sec` = `1.0` · identidad F3
- `GfxRules.callout_font_weight` = `900` · identidad F3
- `GfxRules.callout_font_px` = `158` · identidad F3
- `GfxRules.callout_anton_px` = `168` · identidad F3
- `GfxRules.zoom_hold_min_sec` = `1.0` · identidad F3
- `GfxRules.zoom_scale` = `2.2` · identidad F3
- `GfxRules.zoom_conf_min` = `0.7` · identidad F3
- `GfxRules.archive_dur` = `6.0` · identidad F3
- `GfxRules.archive_scale` = `0.68` · identidad F3
- `GfxRules.archive_max_w_frac` = `0.30` · identidad F3
- `GfxRules.archive_head_max_words` = `8` · identidad F3
- `GfxRules.archive_body_head_max_words` = `4` · identidad F3
- `GfxRules.archive_body_max_words` = `12` · identidad F3
- `GfxRules.archive_body_lines` = `2` · identidad F3
- `GfxRules.archive_body_px` = `40` · identidad F3
- `GfxRules.count_dur` = `1.2` · identidad F3
- `GfxRules.count_hold_sec` = `2.5` · identidad F3
- `GfxRules.punch_in_sec` = `0.4` · identidad F3
- `GfxRules.transition_frames` = `field(default_factory=lambda: {"R1": 3, "R2": 20, "R3": 30})` · identidad F3
- `GfxRules.dip_frames` = `10` · identidad F3
- `GfxRules.flash_peak` = `0.3` · identidad F3
- `GfxRules.flash_max_per_cap` = `2` · identidad F3
- `GfxRules.flash_min_gap_sec` = `20.0` · identidad F3
- `GfxRules.question_pause_sec` = `3.0` · identidad F3
- `GfxRules.crossfade_frames` = `20` · DECISIONES: 2
- `GfxRules.mood_dur` = `2.5` · identidad F3

## B — Compuerta del render: sin guion aprobado no hay `--gfx` (`f97c6f1`)
- **Aprobación**: `fase2b <topic> --aprobar-guion "Omar <fecha>"` (`script_engine/aprobacion.py`, solo biblioteca
  estándar) escribe en `output/<topic>/GUION_PANTALLA.json` `aprobado: {por, fecha, md5_planes, planes}`; `md5_planes` =
  md5 conjunto (nombre y bytes, en orden) de los `gfx_plan_chNN.resolved.json` del topic. Falla si no hay guion, si no
  hay planes o si algún plan es más nuevo que el guion. **CC lo corre solo cuando el prompt de Omar dice literalmente
  «aprobado»** (está en `/tanda` y en el skill). Lo invalida cualquier `--plan-edit` o `--plan-only` posterior: el guion
  se reescribe sin `aprobado`, y si los planes cambian el md5 ya no coincide.
- **Hook `guard_render`** (`.claude/hooks/guard_render.py`, en `settings.json`, mismo patrón que `guard_git`): ante un
  comando que corre `fase2b … --gfx` mira el guion del topic; sin guion, sin `aprobado` o con los planes cambiados,
  **bloquea** (exit 2) y dice qué falta. Pasan: `--plan-only`, `--plan-edit`, `--aprobar-guion`, `--only-cap … --gfx-debug`
  y todo fase2b sin `--gfx` (la salida del candado md5 de ch02). `--dry-run` y el modo batch con `--gfx` se bloquean.
- **Tests** (`test_module_f33.py`): sin guion o sin aprobación bloquea; con aprobación pasa; después de un `--plan-edit`
  (un plan cambia) vuelve a bloquear, y también después de regenerar el guion; `--plan-only` y lo que no es render nunca
  se bloquean; `--dry-run` y batch con `--gfx` sí; aprobar falla con un plan más nuevo que el guion; el hook está en
  `settings.json`.

### Prueba del hook (B.3 / E.1)
Por stdin (`lab/hyperframes/f33/b/prueba_guard_render.txt`):
```
$ python fase2b.py f8s3-vajont-f30 --gfx --dry-run                                  → exit 2 (no está aprobado)
$ python fase2b.py f8s3-vajont-f30 --keep-segments --reuse-visuals --gfx --gfx-sparse --gfx-quality looks --rotulista
                                                                                     → exit 2 (no está aprobado)
$ python fase2b.py f8s3-vajont-f30 --plan-only --rotulista                           → exit 0
$ python fase2b.py ba6c3cac-a091-41c0-8dad-afd2f4364747 --only-cap ch02 --reuse-visuals --sw-encode → exit 0
```
**En vivo, en esta sesión** (`lab/hyperframes/f33/e/prueba_en_vivo.txt`): CC escribió el comando de render en seco de
Vajont y Claude Code lo frenó antes de correrlo:
```
PreToolUse:Bash hook error: [python -I "$CLAUDE_PROJECT_DIR/.claude/hooks/guard_render.py"]: guard_render: sin guion
aprobado no hay render — el guion de f8s3-vajont-f30 no está aprobado (Omar lo aprueba; CC corre `fase2b f8s3-vajont-f30
--aprobar-guion "Omar <fecha>"` solo si su prompt dice «aprobado»)
```
**Falso positivo encontrado en E y arreglado:** el hook del commit B frenaba también comandos que solo *mencionaban* el
render (un heredoc que escribía la evidencia, un parche con ese texto). El primer arreglo (contar solo comandos que
empiezan con `python`) abría un hueco que encontró el revisor (`timeout 600 python fase2b.py … --gfx` pasaba); el arreglo
final saca el cuerpo de los heredocs antes de mirar, no cuenta los comandos de texto (`echo`, `grep`, `git`, `cat`…),
mira detrás de cualquier prefijo (`timeout`, `nohup`, `time`, `env`, `cmd /c`, `start`) y dentro de `bash -c "…"`. Tests:
heredoc y echo no se bloquean; los seis prefijos, `bash -c` y un fase2b después de un heredoc sí. En vivo, después del
arreglo final, `timeout 600 python fase2b.py f8s3-vajont-f30 --gfx --dry-run` quedó bloqueado.

## C — `/tanda`, skills y simulador (`2d87032`)
- `.claude/commands/tanda.md` (copia en `~/.claude/commands/tanda.md`); skills `.claude/skills/guion-de-pantalla/` y
  `.claude/skills/simular-reglas/` (solo en el repo: son del pipeline); agente `.claude/agents/simulador.md`;
  `lab/tools/simular_regla.py`. El agente **`revisor-handoff` ya era de usuario** (`~/.claude/agents/revisor-handoff.md`,
  del 18-10): no se copió.
- Ejemplo del simulador contra el guion de F32 (`lab/hyperframes/f33/c/simulacion_sello_repite_voz.md`), con la regla de
  DECISIONES «sello = clima: no repite la voz ni el subtítulo»:

#### Regla simulada: el sello no repite la voz (DECISIONES 2026-10-25: sello = clima)

Sobre lo que hoy queda en pantalla: **10 propuestos → 10 cortados por esta regla → 0 quedan**.

| cap | propuestos | cortados por esta regla | quedan |
|---|---|---|---|
| ch01 | 1 | 1 | 0 |
| ch02 | 2 | 2 | 0 |
| ch03 | 1 | 1 | 0 |
| ch04 | 0 | 0 | 0 |
| ch05 | 2 | 2 | 0 |
| ch06 | 2 | 2 | 0 |
| ch07 | 2 | 2 | 0 |
| **total** | **10** | **10** | **0** |

Ejemplos de lo que corta (3 de 10):
- 00:39.9 · ch01 · beat 1 · sello «fuerza» · voz: ««La sensación de que la cama tomaba velocidad, una fuerza espantosa que me agarraba por la espalda, me doblaba en dos, me aplastaba», dijo Coletti.» → repite la palabra de la voz
- 02:42.3 · ch02 · beat 2 · sello «vida» · voz: «Abajo, en Longarone, la vida siguió con el Piave delante.» → repite la palabra de la voz
- 02:55.8 · ch02 · beat 3 · sello «montaña» · voz: «La gente de la zona llamaba al monte Toc «la montaña que camina», y lo decían los residentes desde antes de que nadie fuera a medirla.» → repite la palabra de la voz

Programada así, la regla deja el video sin sellos: hace falta el vocabulario de clima (pendiente de Omar) antes de
prenderla.

## E — Verificación
Suite rápida 58 · suite amplia **1003 + 5 previas** (01b_pauses ×3, m03_merge_timing ×2; incluye
`test_constantes_con_origen.py` y `test_module_f33.py`) · md5 `--only-cap ch02` sin `--gfx` (`--sw-encode`)
**`38e5ba14…`** en A, B, C, D y E (`lab/hyperframes/f33/{a,b,c,d,e}/`) · hook de render probado en seco con Vajont: bloquea
(arriba).

## Valores de formato (no del pipeline) que aparecen en hooks, tests y herramientas (§0)
- Timeout de los dos hooks nuevos en `settings.json`: 30 s (el mismo de `guard_git` y `tope_tanda`).
- `simular_regla.py`: 3 ejemplos por defecto (`--ejemplos`), el número que pide el handoff.
- Tests: tamaños de fixtures (dos planes de juguete, 20 ms entre archivos para el orden de mtime, +5 s para un plan «más
  nuevo»); el test de constantes exige > 100 constantes encontradas (hoy 101) para saber que el parser leyó las clases.

## Lecturas de CC (declaradas)
1. **«identidad F3»** = la constante vale lo mismo que el token del perfil `misterio` (la identidad guardada por Omar
   el 2026-10-20 en el lab). Si el perfil la pisa con otro valor, el valor del motor no es la identidad y queda sin
   etiqueta.
2. **Estado en el mapa** = en el camino de producción de hoy (topic con escaleta + `fase2b --gfx --rotulista`, perfil
   misterio; `--plan-only` recorre lo mismo). «Muerto» = en ese camino no aporta al video: nadie lo llama, o se
   llama y su resultado se descarta (lo dice la columna «por qué»); el código sigue (lo usan los topics sin escaleta o
   sin rotulista, o el lab). Además de módulos, el mapa lista **funciones** muertas (el handoff nombra
   `garantizar_pico`, que es una función).
3. **Hook de render**: ve el comando que se escribe en la herramienta (con heredocs fuera, prefijos y `bash -c "…"` por
   dentro); un runner de lab que llama a fase2b por dentro (runpy/subprocess, como `lab/hyperframes/f30b/f30b_vajont.py
   render`) o un script `.ps1`/`.sh` que lo contenga **no pasan por el hook**. Prefiere el falso positivo: cualquier
   comando que no sea de texto y nombre `fase2b.py … --gfx` se mira. `/tanda` lo prohíbe
   igual («no se esquiva con runners»), pero no hay candado técnico para eso.
4. El skill `guion-de-pantalla` dice la regla («el render usa los planes aprobados y no re-decide») y también lo que hoy
   no la cumple: el render vuelve a correr `apply_gfx` y el crítico de los sellos mira el bloque dibujado; el lock de
   planes queda para la tanda de correcciones.

## Lo que queda abierto
1. **66 constantes sin origen** (tabla de A): las tiene que clasificar Omar con el analista; hasta entonces el test
   corre en modo inventario. Cuando estén, `CONSTANTES_ESTRICTO=1` en la suite.
2. **DECISIONES leído por el código** (último pendiente de infraestructura de DECISIONES): no se hizo.
3. **Runners de lab** que llaman a fase2b por dentro no pasan por `guard_render` (lectura 3).
4. **Lock de planes en el render** (el render no re-decide): pendiente para la tanda de correcciones; hoy la compuerta
   asegura que el plan aprobado es el que había al empezar el render, no que el render lo use tal cual.
5. **La página con el flujograma** la hace el analista con `lab/MAPA_MODULOS.json` (`modulos`, `aristas`, `muertos`).
6. Los **muertos** del mapa no se borraron (nada se borra sin decisión de Omar); `data_callout.html.tmpl` y `gfx_fragments`
   todavía sirven a los topics sin escaleta.
7. Lo que dice la ENTRADA y no cuadra (A.1) queda para que el analista lo corrija en su copia.

## C — `/tanda` (pegado)

````markdown
---
description: Arma y corre una tanda de CC desde un handoff del analista (procedimiento F33): lectura, módulos que toca, una variable, PARADA corta por parte, compuertas, reporte con el revisor y ESTADO.
argument-hint: <ruta del handoff> [autorización de Omar, p. ej. «hacelo entero A → C»]
---
Tanda pedida: $ARGUMENTS

Seguí este orden. No te saltees pasos; si uno no se puede cumplir, frená y decí por qué.

1. **Leer** (enteros, antes de tocar código):
   - `CLAUDE.md`;
   - `DECISIONES.md` (el registro de decisiones de Omar; un número que no esté ahí, en la identidad F3 o en un estándar citado, no entra al código);
   - `lab/ESTADO_SESION.md`: la cabecera y las dos últimas tandas;
   - el handoff indicado arriba, y lo que él mande leer.
2. **Declarar los módulos que toca**, antes de programar: una lista con el nombre y el sticker de `lab/MAPA_MODULOS.md` (qué hace hoy para el video) y qué va a hacer después de la tanda. Si un módulo no está en el mapa, agregarlo al mapa en la misma tanda.
3. **Una variable por etapa.** Si el handoff mezcla dos, separarlas en partes y decirlo.
4. **Constantes solo con origen**: cada número nuevo lleva en su línea `# DECISIONES: …`, `# identidad F3`, `# estándar: …`, `# derivado: …` o `# medido: …` (`test_constantes_con_origen.py` las lista). Sin origen, no entra: se pregunta.
5. **Regla o filtro nuevo → simulador antes del código**: si el handoff trae una regla o un filtro de contenido, invocar al subagente `simulador` (skill `simular-reglas`) contra el `GUION_PANTALLA.json` del topic de prueba **antes de escribir código**, y pegar su tabla (propuestos → cortados por esa regla → quedan, con 3 ejemplos) en el reporte.
6. **Cada parte termina con su salida en texto pegada en el reporte** (el guion, la tabla, el log, lo que el módulo produce) **y PARADA corta**: seguir con la parte siguiente solo si el prompt de Omar lo autoriza expresamente («hacelo entero», «A → E»); si no, esperar.
7. **Nunca `fase2b --gfx` sin guion de pantalla aprobado** (`fase2b <topic> --plan-only` → revisión → Omar dice «aprobado» → `fase2b <topic> --aprobar-guion "Omar <fecha>"`). El hook `guard_render` lo frena igual; no se esquiva con runners.
8. **En cada commit**: suite rápida (`test_module_f25c.py test_module_f24.py test_module_f21.py`) y amplia (`test_module_f[0-9]*`, `gfx_*`, `01a*`, `01b*`, `m03_*`, fase2b reassemble/hwencode, concat_windowed, transition_timeout, `test_constantes_con_origen.py`; 5 fallas previas conocidas: 01b_pauses ×3, m03_merge_timing ×2) y el md5 de `fase2b ba6c3cac-a091-41c0-8dad-afd2f4364747 --only-cap ch02 --reuse-visuals --sw-encode` = `38e5ba14…`. Un commit por parte; `.env`, `config.py`, `lab/_gpt_probe_analista/`, `gfx_profiles/*` fuera de git; sin merge, sin publicar, sin borrar.
9. Si el commit toca `script_engine/gfx_*.py` o `fase2b.py`, actualizar `lab/MAPA_MODULOS.md`/`.json` (el hook `guard_mapa` avisa) o decir en el reporte por qué el mapa no cambió.
10. **Reporte** `lab/hyperframes/fNN/FNN_REPORT.md`: lo hecho por parte con su salida pegada, lecturas declaradas, la sección **«lo que queda abierto» entera** (nada resumido), y el **veredicto íntegro del subagente `revisor-handoff`** (se lo invoca antes de cerrar, con el handoff y el pedido literal de Omar).
11. `lab/ESTADO_SESION.md` actualizado al final (y en cada commit). **PARADA.**
````

## C — skill `guion-de-pantalla` (pegado)

````markdown
---
name: guion-de-pantalla
description: Generar, leer, editar y aprobar el guion de pantalla de un topic (fase2b --plan-only / --plan-edit / --aprobar-guion) antes de cualquier render. Usar cuando una tanda toca lo que se ve en pantalla, cuando hay que mostrarle a Omar o al analista qué va a salir, o antes de pedir un render.
---
# Guion de pantalla (F32/F33)

**Regla (DECISIONES 2026-10-26 11:13): texto antes que render, siempre.** Nada se renderiza con `--gfx` sin el guion
revisado y aprobado por Omar; el hook `guard_render` lo frena.

## 1. Generarlo
```bash
PYTHONIOENCODING=utf-8 python fase2b.py <topic> --plan-only --rotulista
```
- Implica `--gfx --reuse-visuals`: los visuales base (`chNN_flux_visual.mp4` / `chNN_hybrid_visual.mp4`) tienen que
  estar cocidos (no cuece DepthFlow). Sin navegador, sin HyperFrames, sin render.
- Corre director, rotulista, reglas y crítico (el crítico mira la foto sola), -g30 de los caps en paralelo y el plan en
  fila. Vajont: ~2.7 min con el rotulista en caché; ~5 min si el rotulista llama a Claude.
- Escribe `output/<topic>/GUION_PANTALLA.md` y `.json` (la misma información) y
  `output/<topic>/_fase2b_work/mezcla_preview.wav` (voz + música + sfx, con el grafo del render: para **oír** costuras y
  silencios). Regenerar reescribe el guion **sin** aprobación.

## 2. Qué trae
- **Una línea por evento**, en el segundo del mp4 final (intro de 2.5 s y pre-roll ya sumados):
  `mm:ss · chNN · beat n (función) · tipo · «etiqueta | texto» · dura X s (lectura mínima Y s) · escena k (de a) · voz −1 / ancla / +1 · aporta · fuente · filtro`.
  Tipos: costura, title card, ficha, persona, recorte, cita, lupa, sello, reloj, nivel de agua, contador, punch,
  pregunta de cierre, transición, silencio de voz. **`✂`** = propuesto y cortado: «cortó *quién* (*regla*): *motivo*»
  (rotulista por regla, zona, catálogo de sellos, realizador, crítico, candado).
- **Tabla por beat** al final de cada cap: función · ventana (s del cap) · escenas · propuestos (director · rotulista)
  · cortados por regla (con el motivo de cada uno) · quedan. `⚠ BEAT VACÍO` = nada en el beat; `⚠ CAP SIN TEXTO` en la
  cabecera del cap.
  Cómo leerla: si «propuestos · rotulista» es alto y «quedan» es 0, el material estaba y lo mató una regla (mirar qué
  regla en «cortados»); si «propuestos» es 0, el problema está antes (escaleta, pool, el modelo).
- **Chequeos** (✓/✗ con el dato): dos bloques en una escena, bloque que cruza un corte, texto sin lectura (15 cps),
  pregunta sin lectura, cifra que contradice la voz, `a_pantalla` (cuántos salen y por qué falta cada uno), costuras
  (negro hasta el corte, voz callada), inicio de voz por cap (a tiempo ±1 cuadro y con rampa).

## 3. Editarlo sin volver a llamar al modelo (`--plan-edit`)
```bash
PYTHONIOENCODING=utf-8 python fase2b.py <topic> --plan-edit ediciones.json
```
Las ediciones se suman a `_fase2b_work/plan_edits.json` (las nuevas, después: ganan) y se regenera el guion; el rotulista
sale de caché y el crítico solo mira lo editado (caché por identidad del bloque). Cada edición va por `cap` + `pool_id`
sobre la respuesta del rotulista (después pasa **todas** las reglas: candado, lectura, zona, crítico) o, con `escena`,
sobre el plan colocado. Campos: `texto`, `etiqueta`, `word_idx`, `sentence_idx`, `tipo`, `aporta`, `borrar`, `agregar`,
`escena`. Ejemplos reales de Vajont (`f8s3-vajont-f30`, guion de F32):
```json
{"ediciones": [
  {"cap": "ch02", "pool_id": "D117", "etiqueta": "Consejo Superior de Obras Públicas"},
  {"cap": "ch05", "pool_id": "Q50", "texto": "Las poblaciones de Erto y Casso viven en continua aprensión y alarma."},
  {"cap": "ch06", "pool_id": "D192", "texto": "20 técnicos perecieron en el centro de control."},
  {"cap": "ch06", "pool_id": "D128", "escena": 13},
  {"cap": "ch07", "pool_id": "T85", "borrar": true},
  {"cap": "ch03", "agregar": {"pool_id": "T21", "sentence_idx": 1, "word_idx": 5, "tipo": "cifra",
                              "etiqueta": "Deslizamiento de Pontesei", "texto": "3 millones de m³ de roca",
                              "aporta": "el volumen de roca que cayó, que la voz no dice"}}
]}
```
(D117 cayó por candado por el «1943» de su etiqueta; Q50 y D192, por lectura; T85 es una propuesta de ch07; el
`agregar` usa el dato T21 del pool —«3 millones de m³ de roca» en Pontesei— anclado en la palabra «roca» de la oración
[1] de ch03 («Ese marzo, una masa de roca entró al agua…»). Toda edición vuelve a pasar el candado: si un número o un
nombre no está en el texto fuente del dato, sale.)

## 4. Aprobarlo
Solo cuando el prompt de Omar dice literalmente **«aprobado»**:
```bash
PYTHONIOENCODING=utf-8 python fase2b.py <topic> --aprobar-guion "Omar 2026-10-27"
```
Escribe `aprobado: {por, fecha, md5_planes, planes}` en `GUION_PANTALLA.json` (md5 conjunto de los
`gfx_plan_chNN.resolved.json`). Falla si algún plan es más nuevo que el guion. Cualquier `--plan-edit` o `--plan-only`
posterior la invalida (el guion se reescribe sin `aprobado`, y si los planes cambian el md5 ya no coincide).

## 5. El render
`guard_render` deja pasar `fase2b <topic> … --gfx` solo con la aprobación vigente. **Regla: el render usa los planes
aprobados y no re-decide** (el crítico del rotulista reusa su veredicto por identidad del bloque). Ojo, abierto desde
F32: hoy el render vuelve a correr `apply_gfx` y el crítico de los **sellos** mira el bloque dibujado (snapshot), así que
puede cambiar un veredicto; el lock de planes (`gfx_plan_override` con los planes aprobados) está pendiente para la tanda
de correcciones. Hasta entonces, comparar el plan del render con el aprobado (`md5_planes`) después de renderizar.
````

## C — skill `simular-reglas` (pegado)

````markdown
---
name: simular-reglas
description: Correr una regla o un filtro de contenido EN SECO contra el guion de pantalla (GUION_PANTALLA.json) o los planes resueltos antes de programarla, y devolver la tabla propuestos → cortados por esa regla → quedan con 3 ejemplos. Usar siempre que un handoff traiga una regla o filtro nuevo, antes de escribir código.
---
# Simular una regla antes de programarla (F33)

Lección de F29c: las reglas del analista se cancelaron con el material (lectura contra cortes de ~10 s, una por beat,
una por escena) y Vajont salió con 2 textos. Simular primero cuesta segundos.

## Entrada
- La **descripción de la regla** (del handoff, literal).
- El guion del topic de prueba: `output/<topic>/GUION_PANTALLA.json` (si no existe o es viejo: `fase2b <topic>
  --plan-only --rotulista`). Para reglas sobre lo que el guion no trae, los planes `output/<topic>/_fase2b_work/
  gfx_plan_chNN.resolved.json`.

## Cómo
1. Traducir la regla a un predicado de Python sobre un evento `e` del guion (claves: `cap`, `beat`, `funcion`, `tipo`,
   `etiqueta`, `texto`, `dur`, `lectura_min`, `escena`, `escena_t0`, `escena_t1`, `voz_prev`, `voz_ancla`, `voz_next`,
   `aporta`, `fuente`, `filtro`, `queda`, `t`, `t_mp4`, `pool_id`, `regla`). Verdadero (o un texto con el motivo) = la
   regla lo corta. Hay `re` disponible. Si la regla no se puede expresar con lo que trae el guion, decirlo (y qué falta).
2. Correr:
   ```bash
   python lab/tools/simular_regla.py output/<topic>/GUION_PANTALLA.json --nombre "<regla>" \
       [--tipos sello,ficha] [--sobre quedan|todos] --regla "<predicado>"
   ```
   `--sobre quedan` (default): lo que hoy está en pantalla (¿qué más cortaría?). `--sobre todos`: también lo que ya cortó
   otro filtro (¿se solapa con una regla existente?). Para reglas largas, `--archivo regla.py` con `def regla(e)`.
3. Pegar la salida tal cual en el reporte: total y por cap (propuestos → cortados → quedan) y 3 ejemplos con el minuto,
   el texto y la voz.

## Ejemplo (Vajont, guion de F32): «el sello no repite la voz» (DECISIONES: sello = clima)
```bash
python lab/tools/simular_regla.py output/f8s3-vajont-f30/GUION_PANTALLA.json --nombre "el sello no repite la voz" \
    --tipos sello --regla "re.search(r'(?<!\w)'+re.escape(e['texto'].lower())+r'(?!\w)', e['voz_ancla'].lower()) and 'repite la palabra de la voz'"
```
→ **10 propuestos → 10 cortados → 0 quedan** (fuerza, vida, montaña…): la regla, programada así, deja el video sin
sellos; hace falta el vocabulario de clima antes de prenderla.

## Qué no hace
No toca el código del pipeline ni el guion; no llama a ningún modelo. Si la tabla dice que la regla mata casi todo,
eso va al reporte **antes** de programarla, para que decidan Omar y el analista.
````

## C — agente `simulador` (pegado)

````markdown
---
name: simulador
description: Simula en seco una regla o un filtro de contenido nuevo contra el guion de pantalla (GUION_PANTALLA.json) o los planes resueltos de un topic, con el skill simular-reglas, y devuelve la tabla propuestos → cortados por esa regla → quedan con 3 ejemplos. /tanda lo invoca obligatoriamente cuando un handoff trae una regla o filtro nuevo, ANTES de escribir código. Solo lectura del pipeline.
tools: Read, Grep, Glob, Bash
model: sonnet
---
Sos el simulador de reglas del pipeline de documentales (repo `C:\CLAUDE_PROJECTS\automatization_videos`). No programás
la regla: medís qué haría si existiera.

Recibís: (a) la regla o el filtro tal como lo escribe el handoff, (b) el topic de prueba (por defecto `f8s3-vajont-f30`).

Procedimiento (skill `.claude/skills/simular-reglas/SKILL.md`):
1. Leé `output/<topic>/GUION_PANTALLA.json` (si no existe, decilo y pará: se genera con `fase2b <topic> --plan-only
   --rotulista`, que no corrés vos). Mirá dos o tres eventos para ver las claves.
2. Traducí la regla a un predicado sobre el evento `e`. Si la regla es ambigua, elegí la lectura más literal, decí cuál
   y, si cambia mucho el resultado, corré también la otra.
3. Corré `python lab/tools/simular_regla.py output/<topic>/GUION_PANTALLA.json --nombre "…" --regla "…"` (con
   `--tipos` y `--sobre quedan|todos` según la regla). No edites archivos del pipeline ni el guion.
4. Devolvé: el predicado usado, la salida del script tal cual (total, tabla por cap, 3 ejemplos), y una línea de lectura
   («la regla corta N de M; los cortes son / no son lo que el handoff busca porque …»). Si la regla no se puede
   expresar con los campos del guion, decí qué dato falta y de dónde saldría (planes resueltos, pool, escaleta).
````

## D — Mapa de módulos (`ba7e958`), pegado entero (`lab/MAPA_MODULOS.md`; datos y aristas en `.json`)

### MAPA DE MÓDULOS — capa gráfica y lo que la alimenta

Generado por `lab/tools/mapa_modulos.py` (F33 §D) leyendo el código: quién llama a quién y cuándo nació cada archivo salen del AST y de git; sticker, recibe/entrega y estado los escribió CC después de leer cada módulo. Estado = en el camino de producción de hoy: topic con escaleta + `fase2b <topic> --gfx --rotulista` (perfil misterio); `--plan-only` recorre lo mismo sin el render. Los datos con las aristas, para el flujograma, en `lab/MAPA_MODULOS.json`.

| módulo | sticker | recibe | entrega | quién lo llama | tanda en que nació | estado |
|---|---|---|---|---|---|---|
| `gfx_bug` | La marca del canal (la llama en el farol): la esquina está apagada desde F4e; queda el cierre del último cap si no hay pregunta. | SVG de la marca + plan | PNG de la marca para el cosido | gfx_layer.py, gfx_sparse.py (+ 3 tests) | F4b (`93064c8`) | vivo (solo el cierre) |
| `gfx_critic` | El editor de último momento: Gemini mira la foto (y en el render el bloque dibujado) y saca lo que repite la voz, no aporta o tapa algo. | plan + cuadros del video + voz | plan sin lo que no pasa + veredictos | gfx_layer.py (+ 5 tests) | F4e (`39e37ac`) | vivo |
| `gfx_director` | El primer borrador de la pantalla: Gemini Flash propone bloques mirando la narración; acá también se carga el contexto del cap y se arman los sfx de cada bloque. | narración, hechos, escenas | plan crudo y resuelto, contexto, eventos de sfx | fase2b.py, gfx_lab_server.py, gfx_fragments.py, make_bug.py, gfx_layer.py, gfx_literal_lock.py, gfx_peak.py, gfx_rotulista.py (+ 8 tests) | F1 (`39e301f`) | vivo (sus textos los reemplaza el rotulista; sus sellos, el catálogo) |
| `gfx_fragments` | Elegía con Gemini el fragmento más impactante de un dato para recortes y rótulos; hoy solo presta el ícono de categoría del sello. | datos + léxico | fragmentos; ícono de categoría | gfx_director.py, gfx_layer.py, gfx_pool.py (+ 2 tests) | F4b (`f1af5de`) | solo sin escaleta (vive por `category_icon`) |
| `gfx_guion` | Escribe el guion de pantalla: todo lo que se va a ver, en texto, con lo cortado y por quién, y los chequeos (lectura, costuras, inicio de voz) sobre la mezcla de audio. | planes, escenas, beats, mezcla | GUION_PANTALLA.md/.json | fase2b.py (+ 1 tests) | F32 (`308032a`) | vivo |
| `gfx_identity` | Guarda la identidad del canal que Omar arma en el laboratorio (F3) dentro del perfil. | estado del lab | `identity` en gfx_profiles/<perfil>.json | gfx_lab_server.py (+ 1 tests) | F3 (`04a6025`) | muerto en el pipeline (lo usa solo el lab, gfx_lab_server) |
| `gfx_intensity` | Gemini marca cuánto pesa cada frase y qué palabras cargan miedo, muerte o agua; ese léxico alimenta los sellos. | oraciones del cap + vecinas | pico, cargas, léxico del cap | gfx_layer.py, gfx_peak.py (+ 5 tests) | F4b (`1762916`) | vivo |
| `gfx_layer` | El director de orquesta de la capa gráfica de un capítulo: llama a todos los demás en orden (plan, textos, sellos, crítico, transiciones) y hace el render en HyperFrames. | visual base del cap + palabras con tiempos + contexto | `chNN_gfx.mp4`, plan resuelto, sfx, escenas | fase2b.py, gfx_lab_server.py, gfx_critic.py, demo.py, strip.py, gfx_rotulista.py (+ 4 tests) | F1 (`39e301f`) | vivo |
| `gfx_literal_lock` | El candado: un texto que no está literal en las fuentes (narración, pool) no sale. | plan + fuentes | plan sin lo no literal + rechazados | gfx_lab_server.py, gfx_director.py, gfx_fragments.py, gfx_layer.py (+ 8 tests) | F1 (`39e301f`) | vivo |
| `gfx_peak` | El pico del capítulo: busca su frase y la palabra de más peso para el sello del pico; trae las piezas de oraciones y palabras que usan los demás. | palabras con tiempos + léxico de moods | frase y palabra del pico, sello | fase2b.py, gfx_lab_server.py, gfx_critic.py, gfx_director.py, gfx_layer.py, gfx_pool.py, gfx_rotulista.py (+ 8 tests) | F3 (`9d36be7`) | vivo (el pico de la escaleta; `plan_peak` ya no corre) |
| `gfx_pool` | La pantalla alimentada por el pool de evidencia: fuentes literales para el candado, lo ya mostrado en caps anteriores y el reloj de fechas. | pool de evidencia + palabras | fuentes, ids ya usados, reloj | gfx_director.py, gfx_layer.py, gfx_peak.py, gfx_realizador.py, gfx_rotulista.py, m01a_escaleta.py, m01a_skeleton.py (+ 4 tests) | F5 (`e18e656`) | vivo (recortes, citas y contadores del pool ya no corren) |
| `gfx_project` | El dibujante: convierte el plan en la página HTML que HyperFrames renderiza (title card, ficha, recorte, cita, sello, reloj, agua, contador, zoom). | plan resuelto + escenas | proyecto HyperFrames (index.html, CSS) | gfx_lab_server.py, gfx_director.py, demo.py, strip.py, gfx_layer.py, gfx_pool.py, gfx_rotulista.py, gfx_sparse.py (+ 27 tests) | F1 (`39e301f`) | vivo |
| `gfx_question` | Escribe una pregunta de cierre con Gemini cuando la escaleta no trae una. | narración del cap y del siguiente | pregunta validada | gfx_lab_server.py, gfx_layer.py (+ 3 tests) | F3 (`beb2b8f`) | solo respaldo (con escaleta la pregunta es el cierre del último beat) |
| `gfx_realizador` | Hace que la pantalla obedezca a la escaleta: ventanas de tiempo de cada beat, qué datos puede mostrar cada uno, la pregunta de cierre del último beat y los topes. | escaleta + narración por beat + pool | `gfx_beats_chNN.json`, candidatos, filas de lo quitado | gfx_layer.py, gfx_pool.py, gfx_rotulista.py (+ 3 tests) | F29 (`2fcd603`) | vivo |
| `gfx_review` | La hoja de cues: un renglón por bloque visible con su segundo, para revisar el render. | eventos del plan | `gfx_cues_chNN.md/.json`, página de revisión | fase2b.py, gfx_layer.py (+ 2 tests) | F1 (`39e301f`) | vivo |
| `gfx_rotulista` | El que escribe los textos de pantalla (Claude Sonnet): por beat, anclados a una palabra, con candado de lo literal, tiempo de lectura, spoiler y contradicción; los coloca como ficha, recorte, cita, lupa, agua o contador, y pone los sellos por tema. | oraciones de la voz con tiempos, beats, datos del pool | bloques de texto en el plan, filas de lo cortado y por qué | fase2b.py, gfx_guion.py, gfx_layer.py (+ 4 tests) | F29b (`5ae6177`) | vivo |
| `gfx_safe_bake` | Cuece con ffmpeg el movimiento suave de cada foto (acercar, alejar, paneo) para no pagarlo en HyperFrames. | escenas con movimiento seguro + sus PNG | `base_cocido.mp4` | gfx_layer.py (+ 1 tests) | F30 (`94d9496`) | vivo |
| `gfx_sparse` | El ahorrador: HyperFrames solo donde hay algo que dibujar; el resto del cap lo cose ffmpeg, con las transiciones, el grano y la viñeta. | plan + escenas + base | `chNN_gfx.mp4` cosido | gfx_layer.py (+ 8 tests) | F2 (`f3d42ed`) | vivo |
| `gfx_style` | La identidad del canal aplicada al plan: qué movimiento lleva cada foto y qué transición va en cada corte según el relato (corte, golpe de zoom en el pico, fundido, dip al cierre). | escenas + plan + beats | movimientos y transiciones | gfx_lab_server.py, gfx_director.py, gfx_layer.py, gfx_project.py, gfx_sparse.py (+ 2 tests) | F4 (`f5c54bd`) | vivo |
| `gfx_vision` | Gemini mira cada foto y dice qué detalles tiene y dónde (rostro, manos, objetos); con eso se decide el movimiento seguro y la caja de la lupa. | PNG / cuadro de la escena | detalles con caja, sí/no del recorte | gfx_layer.py (+ 1 tests) | F4b (`93064c8`) | vivo |
| `aprobacion` | La compuerta del render: guarda quién aprobó el guion de pantalla y la huella de los planes; si algo cambió después, no hay render. | GUION_PANTALLA.json + planes resueltos | `aprobado` en el guion; sí/no para el hook | fase2b.py (+ 1 tests) | F33 (`f97c6f1`) | vivo |
| `m01a_escaleta` | Fase 1: arma la escaleta (los beats del video con función, intensidad, datos y cierre) desde la ficha del caso; es lo que el gfx lee para saber qué va dónde. | ficha del caso + pool | `01a_escaleta.json` | fase1_5.py, guion_v4.py, m01a_columna.py, m01b_guionista.py, m01c_editor.py, m01d_particion.py, tts_tags.py (+ 18 tests) | F6 (`4b41280`) | vivo (fase 1; el gfx lee su salida) |
| `m01d_particion` | Fase 1: parte el guion en los 7 capítulos con su texto para la voz; de ahí salen la narración por cap y por beat que leen el realizador y el rotulista. | guion + escaleta | narración por cap y por beat | fase1_5.py, guion_v4.py (+ 5 tests) | F10 (`317c5f1`) | vivo (fase 1) |
| `music_intensity` | Decide cuándo la música calla, acompaña o sube en cada cap según la escaleta; también da el beat pico de cada cap. | escaleta + narración por beat + tiempos de la voz | tramos de volumen por cap, beat pico | fase2b.py, gfx_realizador.py, gfx_rotulista.py (+ 2 tests) | F28 (`e3fd23a`) | vivo |
| `transition_applier` | Pega los capítulos uno detrás de otro. Con --gfx: corte a negro y el siguiente sube desde negro; sin --gfx, las transiciones del perfil de arte (incluido el flash blanco). | segmentos por cap | `_concat_video.ts` + `_concat_audio.wav` y el mp4 sin música | fase2b.py (+ 3 tests) | previo a F1 (`e33f84a`) | vivo |
| `gfx_config` | El tablero de perillas de la capa gráfica: duraciones, tamaños, colores y qué reglas están prendidas; el perfil del canal (identidad F3) pisa los valores. | gfx_profiles/<perfil>.json | `gfx_rules`, `gfx_render`, moods, sfx por bloque | fase2b.py, gfx_lab_server.py, gfx_bug.py, gfx_critic.py, gfx_director.py, gfx_fragments.py, demo.py, strip.py, gfx_identity.py, gfx_intensity.py, gfx_layer.py, gfx_literal_lock.py, gfx_peak.py, gfx_pool.py, gfx_project.py, gfx_question.py, gfx_review.py, gfx_rotulista.py, gfx_safe_bake.py, gfx_sparse.py, gfx_style.py (+ 17 tests) | F1 (`39e301f`) | vivo |
| `fase2b` | El armador final: junta imagen, voz, subtítulos y música de cada capítulo en un segmento y los pega en el video. Con `--gfx` le pone encima la capa gráfica; con `--plan-only` solo escribe el guion de pantalla. | assets del topic (imágenes/clips), voz por cap + tiempos, sync map, música | `*_final(_gfx).mp4`; o GUION_PANTALLA + mezcla | diag_234_cap4.py, diag_235_matcher_ba6c.py, diag_236_pacing_ba6c.py, gfx_lab_server.py (+ 21 tests) | previo a F1 (inicial) (`e33f84a`) | vivo |
| `transition_config` | Las perillas del pegado entre capítulos (calidad del video, fps) y el inventario de transiciones de los perfiles de arte. | — | `transition_render` y el inventario | transition_applier.py, transition_profiles.py | previo a F1 (`e33f84a`) | vivo (con --gfx solo calidad y fps; el inventario es del camino sin gfx) |
| `archive_clipping.html.tmpl` | La forma del recorte de diario (papel, kicker, titular). | un recorte del plan | HTML | gfx_project.py | F1 (`39e301f`) | vivo (documentos del rotulista) |
| `chapter_question.html.tmpl` | La forma de la pregunta de cierre sobre la foto oscurecida. | la pregunta | HTML | gfx_project.py | F2 (`b7b86fd`) | vivo |
| `count_up.html.tmpl` | La forma del contador que sube hasta la cifra. | cifra + unidad + etiqueta | HTML | gfx_project.py | F1 (`39e301f`) | vivo (F32 B.7; en Vajont no salió ninguno) |
| `data_callout.html.tmpl` | La forma vieja del dato en letras grandes sueltas. | un rótulo del plan | HTML | gfx_project.py | F1 (`39e301f`) | muerto en el camino con rotulista (todo texto es ficha); vive sin rotulista |
| `evidence_zoom.html.tmpl` | La forma de la lupa: recuadro, «DETALLE» y acercamiento. | caja del detalle | HTML | gfx_project.py | F1 (`39e301f`) | vivo (lupa del rotulista) |
| `grade_css.html.tmpl` | Un grade de color por CSS de la primera versión. | — | — | — | F1 (`39e301f`) | muerto (nadie la carga; el grade lo hace el CSS común y ffmpeg) |
| `index.html.tmpl` | La página base de cada proyecto HyperFrames (escenas, overlays, timeline). | escenas + overlays | index.html | gfx_project.py | F1 (`39e301f`) | vivo |
| `scene.html.tmpl` | La forma de una escena (la foto o el clip con su movimiento). | una escena | HTML | gfx_project.py | F1 (`39e301f`) | vivo |
| `title_card.html.tmpl` | La forma del title card del capítulo; desde F29c también la de la ficha. | kicker + título | HTML | gfx_project.py | F1 (`39e301f`) | vivo |

### Módulos y funciones muertos — lo que el camino de producción ya no llama (muertos)

| qué | por qué | desde |
|---|---|---|
| `gfx_peak.plan_peak (y water_level, zoom_latido, time_ticker, reserved_water_level, clear_around)` | con el rotulista el pico es el de la escaleta (`gfx_rotulista.pico_plan`) | 5ae6177 2026-10-25 feat(f29b-a): el rotulista — el texto de pantalla lo escribe Claude,  |
| `gfx_realizador.garantizar_pico` | `--rotulista` apaga `garantizar_pico` | 7e704de 2026-10-26 fix(f29b): dos observaciones del revisor antes de la parte B — el can |
| `gfx_pool.plan_pool_documents, plan_pool_quote, pool_count_up, enforce_reserved` | con el rotulista los textos los escribe él (`rot_on` en apply_gfx) | 5ae6177 2026-10-25 feat(f29b-a): el rotulista — el texto de pantalla lo escribe Claude,  |
| `gfx_fragments.choose_fragments` | con pool los recortes salían de gfx_pool (F5) y después del rotulista | e18e656 2026-10-20 feat(f5-gfx): la pantalla se alimenta del evidence_pool — candado, re |
| `gfx_fragments.drop_repeated_callouts` | con el rotulista corre su regla de no dicho | 5ae6177 2026-10-25 feat(f29b-a): el rotulista — el texto de pantalla lo escribe Claude,  |
| `gfx_vision.pick_zoom` | con el rotulista la lupa la propone él | 5ae6177 2026-10-25 feat(f29b-a): el rotulista — el texto de pantalla lo escribe Claude,  |
| `gfx_director.fill_gaps` | `gap_fill` apagado | 2fcd603 2026-10-25 feat(f29a): el gfx obedece a la escaleta — script_engine/gfx_realizad |
| `gfx_question.question_for` | con escaleta la pregunta es el `cierre` del último beat (queda de respaldo) | 2fcd603 2026-10-25 feat(f29a): el gfx obedece a la escaleta — script_engine/gfx_realizad |
| `gfx_style.identity_transitions` | **se llama y se descarta**: con escaleta la pisa `transiciones_por_relato` | 7d0d0e5 2026-10-26 feat(f30b-a): transiciones por relato — por corte, la primera que apl |
| `gfx_style.select_punches` | **se llama y se descarta**: el realizador saca todos los `punch_in` (los reemplaza el zoom_punch del pico) | 2fde994 2026-10-26 feat(f32-b): arreglos del guion de pantalla — B.1 ch01 sin pre-roll y |
| `gfx_director.place_emphasis (sellos por léxico)` | **se llama y se descarta**: `sellos_por_tema` los reemplaza | 2fde994 2026-10-26 feat(f32-b): arreglos del guion de pantalla — B.1 ch01 sin pre-roll y |
| `data_callout.html.tmpl` | con el rotulista todo texto sale como ficha | cc3f079 2026-10-26 feat(f29c-a): rotulista por beat y la ficha es el title card — prompt |
| `grade_css.html.tmpl` | nadie la carga | a878836 2026-10-19 feat(gfx): F2 §0b calibración en ch02 (grade off, cortes reales, zoom |
| `gfx_identity (todo el módulo)` | solo lo usa el lab de identidad (gfx_lab_server) | nunca en fase2b |

Muerto = en el camino con escaleta y rotulista no aporta nada al video: o nadie lo llama, o **se llama y su resultado se descarta** (`select_punches`, `identity_transitions`, `place_emphasis`: lo dice la columna «por qué»). El código sigue ahí (los topics sin escaleta o sin rotulista lo usan, o el lab). No se borra nada sin decisión de Omar.

Hook `guard_mapa` (`.claude/hooks/guard_mapa.py`): antes de un `git commit` que toque `script_engine/gfx_*.py` o `fase2b.py` sin tocar `lab/MAPA_MODULOS.md`/`.json`, avisa (no bloquea). **Este commit (E) toca solo hooks, tests y lab; los de A–D no tocaron `gfx_*.py` (A tocó `gfx_config.py`, que no es `gfx_*`, solo en comentarios; B tocó `fase2b.py` para `--aprobar-guion`, antes de que existiera el mapa, que en D ya lo describe).**

## Veredicto del revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES (A–D cumplen; E está a medio cerrar y el arreglo del hook sin commitear abre un hueco en la compuerta)

| # | requisito | estado | evidencia |
|---|---|---|---|
| A.1 | DECISIONES.md y ENTRADA al repo sin editar | OK, con un NO VERIFICABLE | `git show 651cb25:` da el mismo md5 que el árbol (231c8f15 / cd5edb63), sin CRLF. No existe copia original. El mtime de ENTRADA (13:33) es anterior al commit. El de DECISIONES (14:23) es posterior al commit A (14:18), aunque `git status` lo da limpio. Byte a byte contra el original: NO VERIFICABLE. |
| A.2 | test de constantes en modo inventario y etiquetas | OK | `pytest test_constantes_con_origen.py`: 2 pasan. 101 constantes / 35 con origen / 66 sin origen (coincide con el reporte). Las 33 «identidad F3» coinciden con `misterio.json`, tanto en HEAD como en el árbol. |
| A.2b | Ningún valor cambia | OK | AST de `gfx_config.py` en `cd60c74` contra hoy: idéntico. El diff solo trae comentarios. |
| A.3 | Línea de DECISIONES en CLAUDE.md | OK | `CLAUDE.md:3`. |
| B.1 | `--aprobar-guion` y bloque `aprobado` | OK | `script_engine/aprobacion.py:37-54`; `fase2b.py` +18 líneas. |
| B.2 | Hook bloquea sin guion, sin aprobar o con md5 distinto | OK | Corrí `guard_render.py` por stdin con Vajont (`f8s3-vajont-f30`, `--dry-run` y el render completo): exit 2. Con `--plan-only`, `--plan-edit` y `--only-cap ch02` sin `--gfx`: exit 0. Está en `settings.json`. |
| B.3 | Tests de la compuerta | OK | `test_module_f33.py` + constantes: 11 pasan. |
| C.1–C.5 | `/tanda`, 2 skills, agente `simulador`, simulador, copias | OK | Todo existe. `~/.claude/commands/tanda.md` es idéntico al del repo. Los skills están solo en el repo. `revisor-handoff` ya era de usuario. El simulador reproduce 10 → 10 → 0. Los ids de Vajont del skill (D117, Q50, D192, D128, T85) existen en el guion y los campos de edición coinciden con `CAMPOS_EDITABLES`. |
| D.1–D.2 | Mapa .md y .json | OK | 37 filas, 117 aristas, 14 muertos. «Quién lo llama» coincide con mi grep de imports en 10 módulos. Las fechas de nacimiento y de «muerto» las verifiqué con `git log` (7e704de, 5ae6177, a878836, cc3f079, 2fcd603, e18e656). |
| D.3 | Hook `guard_mapa` | OK | En un repo temporal con un `gfx_*.py` staged, el `git commit` produce el aviso (rc 0). |
| E.1 | Suites, md5 y prueba del hook | OK | Suite amplia: 1003 pasan + las 5 previas esperadas (corrida mía). Rápida 58. md5 `38e5ba14…` en los logs a–e y en el mp4 en disco. |
| E.2 | Reporte y ESTADO | PARCIAL | El reporte tiene todas las secciones y su mapa pegado es idéntico al archivo, pero termina en «## Veredicto» sin contenido. `ESTADO_SESION.md` no cierra E. No hay commit E. |
| Frenos | Sin render, sin tocar `.env`, `config.py`, `lab/_gpt_probe_analista/` ni `gfx_profiles/*`; sin borrar | OK | Ningún commit toca ninguno. `gfx_profiles/*`, `diag_234_cap4.py` y `f28a.log` salen modificados en el árbol, pero con fechas anteriores a la tanda. No hay borrados en `cd60c74..HEAD`. |

Observaciones (las dos primeras te las dejo para que decidas):
1. **Hueco en la compuerta, hoy sin commitear.** El arreglo de E pide que el comando simple empiece con `python`/`py`/`fase2b.py`. Pasa (exit 0) `timeout 600 python fase2b.py f8s3-vajont-f30 --gfx`, y también `nohup python …`, `time python …` y `cmd /c python …`. El hook de `HEAD` (commit D) sí los frenaba. El reporte (lectura 3 y «Lo que queda abierto») solo admite los runners de lab; no dice nada de estos prefijos. El falso positivo es real: el hook de D también frenaba el heredoc. Pero el arreglo cambió ese falso positivo por una forma de saltarse la compuerta.
2. **El mapa llama «muerto» a lo que sigue corriendo.** La definición es «nadie lo llama». Pero `select_punches`, `identity_transitions` y `place_emphasis` se llaman igual (`gfx_layer.py:783/786`, `gfx_director.py:776`) y su resultado se descarta; la columna «por qué» lo dice, pero la definición no. Además `data_callout.html.tmpl` figura «solo sin rotulista» en la tabla principal y «muerto» en la lista de muertos.
3. **Pendiente de cierre.** Falta el veredicto en el reporte, el estado de E en ESTADO y el commit E. Al commitear: `git add -f` para `.claude/hooks/guard_render.py`, más `test_module_f33.py`, el reporte y `lab/hyperframes/f33/e/`. Esos archivos de E están sin trackear o modificados.

Fuera de alcance: ninguno en `cd60c74..HEAD`. En el árbol hay archivos modificados o sin trackear anteriores a la tanda y no tocados por ella.

Riesgos que el contrato no cubre: el hook solo ve el comando escrito (no `bash -c`, `powershell -Command` ni runners de lab que llamen a fase2b por dentro); la aprobación no impide que el render vuelva a decidir (el reporte lo admite). Las 66 constantes sin origen quedan en inventario sin que nada falle.

**Después del veredicto (CC):**
- Obs. 1 (hueco): arreglado. El hook final saca el cuerpo de los heredocs antes de mirar, no cuenta los comandos de texto (`echo`, `printf`, `grep`, `rg`, `git`, `sed`, `awk`, `cat`, `head`, `tail`, `Write-Output`, `Write-Host`, `Select-String`, `findstr`), busca `fase2b.py`/`-m fase2b` detrás de cualquier prefijo y mira dentro de un argumento que sea un comando entero (`bash -c "…"`, `powershell -Command "…"`). Tests nuevos: `timeout 600`, `nohup`, `time`, `cmd /c`, `env A=1`, `start /b`, `bash -c "…"` y un fase2b después de un heredoc **bloquean**; el heredoc y el echo que solo lo mencionan **no**. En vivo: `timeout 600 python fase2b.py f8s3-vajont-f30 --gfx --dry-run` quedó bloqueado (`e/prueba_en_vivo.txt`, punto 3). El riesgo de `bash -c` / `powershell -Command` queda cubierto; siguen fuera los runners y los scripts `.sh`/`.ps1` (lectura 3, abierto 3).
- Obs. 2 (definición de muerto): el mapa ahora dice «muerto = en el camino con escaleta y rotulista no aporta: nadie lo llama, o se llama y su resultado se descarta», y las tres funciones que se calculan y se tiran llevan «**se llama y se descarta**» en su «por qué». `data_callout.html.tmpl` pasó a «muerto en el camino con rotulista; vive sin rotulista» en la tabla, igual que en la lista.
- Obs. 3: veredicto pegado, ESTADO cerrado y commit E con `git add -f` para lo de `.claude/`.
- A.1 NO VERIFICABLE: los archivos se agregaron con `git add` tal como estaban en disco, sin ninguna edición de CC (no hay `Edit`/`Write` sobre ellos en esta sesión); el mtime de DECISIONES posterior al commit sin diff en `git status` es un toque de mtime sin cambio de contenido.
