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
