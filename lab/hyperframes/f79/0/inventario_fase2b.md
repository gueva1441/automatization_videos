# F79 Etapa 0 — inventario de intro / pre-roll / pre_pad en `fase2b.py` (código de 210873b)

Columnas: **P** texto de un prompt · **CC** clave de caché (crítico, md5) · **IMG** imagen que ve un modelo · **HS** clave de caché de capas/segmentos. «→X» = pasa a X en otro archivo (ver `inventario_script_engine.md`).

En `fase2b.py` ninguno de estos valores entra directo en un prompt, una clave del crítico o un md5.

| Línea | Qué hace | P | CC | IMG | HS |
|---|---|---|---|---|---|
| 110 | `HOOK_DURATION = 1.8` (NO se toca) | No | No | No | No |
| 153 | `INITIAL_SILENCE_SEC = 2.5`, la intro del mp4 | No | No | No | No |
| 1147-1158 | `_visual_con_pre_roll`: `tpad` clona el primer cuadro `pre_roll` s → `{cap}_visual_preroll.mp4` | No | No | →apply_gfx (base sobre el que se dibuja) | **Sí**: entra por el glob `{cap}_*visual*.mp4` de `_segment_hash` (2676), con tamaño y mtime |
| 1161-1167 | `_pre_roll_de`: 0 sin gfx o si `is_first`; si no `title_dur` cuando `title_pre_roll` | No | No | No | No |
| 1202-1203 | `pre_roll`, `pre_pad = HOOK·apply_hook + pre_roll` | — | — | — | — |
| 1218-1226 | visual con pre-roll + `apply_gfx(time_offset=pre_pad, pre_roll=pre_roll)` | →gfx_layer | →gfx_layer | →gfx_layer | →gfx_layer |
| 1229-1232 | `effective_audio = audio + pre_pad` (loop / apad) | No | No | No | No |
| 1265-1295, 320-323, 528-531, 615-618 | ASS: palabras corridas `+pre_pad` | No | No | No | No |
| 1310-1312 | voz del segmento `adelay=pre_pad` | No | No | No | No |
| 1597, 1620-1622 | `_build_music_piece_for_chapter(pre_sec)`: pieza `+pre_sec`, envolvente `_correr_tramos` | No | No | No | No |
| 1684-1690 | `_correr_tramos` | No | No | No | No |
| 1702-1704, 1768, 1779 | `_build_continuous_music_track(pre_sec, intro_sec)`; pieza = `seg − pre + xf` | No | No | No | No |
| 1805, 1845, 1848-1860 | `_con_intro`: `adelay=intro_sec` a la música | No | No | No | No |
| 1955, 2000-2063 | `_mix_music_into_video(intro_sec)`: `tpad` del video + `adelay` de la voz | No | No | No | No |
| 2102-2121 | `_grafo_musica(intro_sec)`: `adelay` de la voz | No | No | No | No |
| 2136-2180 | `_mix_music_audio_only`: `_pad.ts` (primer cuadro clonado) concatenado adelante + `_grafo_musica` | No | No | No | `_pad.ts` se regenera siempre |
| 2883-2891 | `_segmento_de_cap(plan, wd, pre_pad)` → `{clip_dur, seg_dur, pre_pad, pre_roll}`; `pre_roll` sale de `gfx_escenas_<cap>.json` | No | No | No | No |
| 2941-2958 | `_costura_medida`: `pre_pad` recalculado; esperado = `seg_dur` del guion | No | No | No | No |
| 2989-3065 | `_mezcla_preview`: `intro = INITIAL_SILENCE_SEC`, `adelay` por cap, `prerolls` de `gfx_escenas`, `_medir_inicio_musica(intro)`, `mezcla["intro"]` | →gg.armar | No | No | No |
| 3164-3186 | `_solo_plan`: visual con pre-roll → `gfx_<cap>/public/base.mp4`; `apply_gfx(time_offset=pre_pad, pre_roll=…, plan_only=True)` | →gfx_layer (director y crítico) | →gfx_layer | →gfx_layer | glob 2676 |
| 3199-3234 | `off = mezcla["intro"]`; `sentences(words, pre_pad)`; `caps_in` con `offset/seg_dur/pre_pad/pre_roll`; `gg.armar(intro=…)`; `titulo` = `title_card.title` del plan resuelto (3217) | →gfx_guion / gfx_peak | No | No | No |
| 3590-3651 | render final: `prerolls`, `seg_dur` con pre_pad, `intro_sec=INITIAL_SILENCE_SEC` a la música y la mezcla | No | No | No | No |

`_segment_hash` (2661-2686): stat de `{cap}_*visual*.mp4` (incluye `_visual_preroll`), `seg_flags`, sha256 de `gfx_plan_<cap>.json`, `.resolved.json`, `gfx_zoom_box_<cap>.json`, nombre de `ACTIVE_PROFILE`. No guarda `pre_roll`, `pre_pad`, `INITIAL_SILENCE_SEC` como valores.

`ChapterPlan.is_first`: `is_first=(i == 0)` en `_build_plans` (2549); llega a `apply_gfx` dentro de `plan` (1220, 3182) y a `caps_in` (3222).
