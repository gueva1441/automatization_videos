# F79 — aire muerto fuera (intro, pre-roll del title card, pausa tras cita) — REPORTE

Rama `f11-guion-v4`, base `210873b`. Handoff `lab/hyperframes/f79/HANDOFF_F79.md`, md5 `253d4a7b8e6ebb3ae16a2fb1d5dbde09` (verificado). Sin render, sin TTS, sin tocar prompts.

## Etapa 0 — línea base (sin tocar código)

**Copias:** `lab/hyperframes/f79/antes/` (37 archivos: `GUION_PANTALLA.json/.md` + de `_fase2b_work/` `gfx_plan_ch*.resolved.json`, `gfx_escenas_ch*.json`, `gfx_sfx_ch*.json`, `gfx_critic_rot_ch*.json`, `gfx_ch*.log`). Plan-only con el código de `210873b`: `python fase2b.py 123bbb64-9fca-4395-8bf4-57d60e219ef1 --plan-only` (venv), 223 s, exit 0, costos `{}` (0 llamadas al crítico: todas de caché) → mismos archivos en `lab/hyperframes/f79/0/` (log en `0/plan_only.log`). Scripts del lab: `copiar.py`, `comparar.py` (solo leen; la comparación entera está en `0/comparacion_antes_0.md`).

**Comparación `0/` contra `antes/`:** reproduce el guion guardado.
- `duracion_s` 798,266 → 798,266.
- Los 7 `gfx_plan_ch*.resolved.json` son byte a byte iguales (md5).
- Por cap, los eventos (`tipo`, `texto`, `queda`, `t`): ch01 13/13 · ch02 20/20 · ch03 21/21 · ch04 20/20 · ch05 22/22 · ch06 22/22 · ch07 17/17 iguales.
- Crítico: 30 preguntas, 0 llamadas, ningún veredicto distinto.
- `GUION_PANTALLA.json` cambia de md5 (`95ca1692…` → `8c9e75a4…`) solo por `generado`, `tiempos_s` y porque perdió `aprobado` (Omar, 2026-11-03, `md5_planes e8c497c1…`): el aviso del handoff §7 se cumplió; no se restaura.
- `data/cost_history.json` reescrito por el plan-only (`540a084c…` → `b7fb9c24…`).

**Offset / voz en el mp4 de la línea base:**

| cap | offset | seg_dur | voz en el mp4 | inicio de voz medido |
|---|---|---|---|---|
| ch01 | 2,5 | 66,8 | 2,66 | 2,66 ✓ |
| ch02 | 69,3 | 102,833 | 72,38 | 72,38 ✓ |
| ch03 | 172,133 | 172,7 | 175,213 | 175,213 ✗ (sin rampa) |
| ch04 | 344,833 | 99,7 | 347,913 | 347,913 ✓ |
| ch05 | 444,533 | 131,833 | 447,633 | 447,633 ✓ |
| ch06 | 576,366 | 128,5 | 579,466 | 579,466 ✓ |
| ch07 | 704,866 | 93,4 | 707,966 | 707,966 ✓ |

**Golpe del title card (línea base):** los 7 caps a 0,05 s, `shift_ms` 0, ninguno descartado.

**Chequeos que ya vienen en ✗ en la línea base (no cuentan como falla de F79):**
- ✗ texto sin lectura: ch05 09:16.4 cita «una empresa que no tuvo reparos» — dura 4,47 s y pide 4,53 s.
- ✗ a_pantalla: 0/6 (ch03 D01, ch05 D51, ch05 D23, ch06 D40, ch06 D34, ch07 D61: «el rotulista no lo propuso»).
- ✗ inicio de voz por cap: ch03 175,21 s sin rampa (100 ms previos −32,7 dB, bajo −30,5 dB).
- ✗ inicio de música por cap: ch03 +6,900 s (+207,01 cuadros), ch07 +15,809 s (+474,27 cuadros) (falso positivo conocido de F72b/F73).
- ✗ papel sin colocar: ch04 sello CALMA, ch05 sello SILENCIO (no entran en ningún intento).
- Los otros 7 en ✓ (dos bloques al mismo tiempo, bloque que cruza un corte, cifra que contradice, costuras, gancho no vacío, papel sin alinear, relojes).

**Inventario** (tres subagentes en paralelo; tablas completas en `0/inventario_fase2b.md` y `0/inventario_script_engine.md`; tests en la sección de A1):

| Valor | Dónde | (i) prompt | (ii) caché | (iii) imagen | (iv) caché de capas/segmentos |
|---|---|---|---|---|---|
| `INITIAL_SILENCE_SEC` / `intro_sec` / `intro` | fase2b 153, 1704/1805/1845/1848-1860 (`_con_intro`), 1955-2063 (`tpad`/`adelay` del mix clásico), 2102-2121 (`_grafo_musica`), 2136-2180 (`_pad.ts`), 2989-3065 (`_mezcla_preview`, `mezcla["intro"]`), 3070-3112 (`_medir_inicio_musica`), 3199, 3234, 3615-3651 | no | no | no | no |
| `intro_s` | gfx_guion 253-264 (costura, `tramos.intro_s`), 641 (json), 675 (md) | no (solo GUION_PANTALLA) | no | no | no |
| `title_pre_roll` | gfx_config 197; fase2b 1167, 3592 | no | no | no | no |
| `pre_roll` / `_pre_roll_de` / `_visual_con_pre_roll` | fase2b 1147-1167, 1202-1226, 2891, 2948, 3042, 3164-3186, 3219-3220, 3591-3597; gfx_layer 133/155 (corte del Veo), 431/436 (`gfx_escenas`), 533/546/606/610/764; pantalla_entrada 94/155 (campo muerto); gfx_guion 257, 639, 682 | no | **sí, indirecto**: `round(t,2)` en la clave del crítico (gfx_critic 152) — aceptado §5.4 | **sí, indirecto**: el cuadro que mira el crítico (gfx_critic 158) se toma del base en `t` — mismo cuadro, otro segundo | **sí**: `chXX_visual_preroll.mp4` entra al glob `{cap}_*visual*.mp4` de `_segment_hash` (fase2b 2676) |
| `prerolls` / `pre_sec` / `_correr_tramos` | fase2b 1597-1622, 1684-1690, 1702, 1768, 1779, 3042-3055, 3591-3628 | no | no | no | no |
| `pre_pad` (= `HOOK_DURATION`·hook + pre_roll) | fase2b 1203, 2948, 3180, 3596; ASS 320/528/615; `adelay` 1312; `apply_gfx(time_offset)` | no | vía `time_offset` → mismo caso (ii) | vía `time_offset` → (iii) | no |

El prompt del crítico (`gfx_critic.build_prompt_rot`) lleva descripción, voz, aporta y por_qué: ningún tiempo. Ningún valor de intro ni pre-roll entra al **texto de un prompt** → la PARADA (b) no se da; la (a) tampoco (la línea base reproduce el guion). Se sigue sin parar.

**`chXX_visual_preroll.mp4` viejos:** Wittenoom tiene 6 (ch02–ch07) en `_fase2b_work/`. Después de F79 nadie los genera ni los lee como base, pero el glob de `_segment_hash` los sigue sumando a la huella del segmento (tamaño + mtime) mientras estén en disco: solo puede invalidar un segmento reusado (se rehace), nunca hace que se lea su contenido. Se listan; no se borran (no es de esta tanda).

## Etapa A1 — sin intro y sin pre-roll

**Qué se borró (código):**
- `fase2b.py`: `INITIAL_SILENCE_SEC`; `_visual_con_pre_roll`, `_pre_roll_de`, `_correr_tramos`, `_con_intro`; `pre_sec` de `_build_music_piece_for_chapter` y de `_build_continuous_music_track` (la pieza alineada dura `seg_dur` + cruce); `intro_sec` de `_build_continuous_music_track`, `_mix_music_into_video`, `_grafo_musica` y `_mix_music_audio_only`; el `tpad` y el `adelay` de la mezcla clásica (el video ahora se copia, `-c:v copy`: sin `tpad` no hace falta re-codificar) y el `_pad.ts` de la mezcla audio-solo; `mezcla["intro"]` y `intro` de `_medir_inicio_musica` (la fila pasa de `title_card_s` a `inicio_cap_s`, el 0,0 del cap); `pre_roll` de `_segmento_de_cap`, `_solo_plan`, `caps_in` y el render final; el `+ pre_roll` de `pre_pad` en las cuatro sumas (`pre_pad` queda solo con el `HOOK_DURATION` del hook, que no se tocó).
- `gfx_config.py`: el campo `GfxRules.title_pre_roll` (el `GfxBlock` `title_card` no se tocó).
- `script_engine/gfx_layer.py`: `pre_roll` de `build_scenes` (el Veo de arranque corta en `veo_dur`), de `escenas_a_disco` (y la clave del json) y de `apply_gfx` (firma y docstring), y de las llamadas.
- `script_engine/pantalla_entrada.py`: el parámetro `pre_roll` y el campo muerto `ent["pre_roll"]`.
- `script_engine/gfx_guion.py`: `intro` de `eventos_cap` y de `armar`; `intro_s` y `pre_roll` del json y del md. La costura describe lo que hay. En el primer cap: «el mp4 arranca con este cap → voz a … s del cap, con el title card encima 3.0 s desde 0.0 s». En los demás: «negro 1.0 s (black hold de chNN) → corte → sube desde negro en 10 cuadros (0.33 s) → voz a … s del cap, con el title card encima …». `tramos` lleva `negro_s`, `sube_desde_negro_s`, `voz_s` y `title_card_s` (este último solo si hay title card). El chequeo de costuras ya no resta la intro; el de música dice «inicio del cap».
- `inicio_de_voz` (gfx_guion): la ventana de correlación arranca en `max(0, base − buscar_s)` y el `lag` se cuenta desde ahí. La ventana de la rampa arranca en `max(0, esperado − 2·RAMPA_S)` y el pico se busca desde `esperado − RAMPA_S`, recortado a la ventana real. Sin números nuevos. Test nuevo: `test_module_f32.py::test_inicio_de_voz_sin_intro_no_mide_antes_de_0`. Con la voz a 0,12 s del mp4 da 0,12 ✓; con la fórmula vieja daba −0,38 ✗ (medido).
- Docs: docstrings de `gfx_critic.clave_identidad`, de `gfx_guion` (l.7) y de `inicio_de_voz`; comentario de `mixer_server._build_mix_filter`; `.claude/skills/guion-de-pantalla/SKILL.md:23`.

**Tests (A1):**

| test | qué | por qué |
|---|---|---|
| `test_module_audio_mixer_floor.py::test_constante_silencio_inicial` | **borrado** | solo afirmaba `INITIAL_SILENCE_SEC == 2.5` |
| `test_module_audio_mixer_floor.py::test_filter_complex_se_construye_sin_error` | **actualizado** | antes armaba su propia fórmula con la intro; ahora prueba el grafo real (`_grafo_musica`) con el perfil: 3 ramas y piso, sin `adelay` ni `tpad` |
| `test_module_concat_windowed.py::test_musica_audio_solo_mismo_largo_que_la_clasica` | **actualizado** | las dos mezclas dan el largo del video sin música (antes, ese largo + 2,5 s × 30 cuadros) |
| `test_module_f30b.py::test_pre_roll_corre_los_subtitulos_y_la_chascada_saca_las_comillas` | **actualizado** → `test_la_chascada_saca_las_comillas_de_los_subtitulos` | queda la chascada; el corrimiento de `pre_pad` (hook) ya lo prueba `test_module_f40_subs.py::test_pre_pad_corre_los_subtitulos` |
| `test_module_f30b.py::test_visual_con_pre_roll_agrega_title_dur_de_primer_cuadro` | **borrado** | la función ya no existe |
| `test_module_f30b.py::test_pieza_de_musica_cubre_el_pre_roll` | **borrado** | `pre_sec` ya no existe |
| `test_module_f32.py`, fixtures `_cap`/`_plan_todo`/`_guion` | **actualizados** | `pre` por defecto pasa a 0,0 (era el pre-roll), sin `pre_roll` ni `intro`. En `test_guion_de_un_cap_con_todos_los_tipos`: 107,4 → 104,4 y «01:47.4» → «01:44.4». En `test_silencio_contra_la_pausa_mas_larga_del_guion`: 16,22 → 13,22 |
| `test_module_f32.py::test_b1_ch01_sin_pre_roll_y_la_musica_arranca_con_el_title_card` | **borrado** | afirmaba `_pre_roll_de`, `_correr_tramos` y `pre_sec` |
| `test_module_f32.py::test_inicio_de_voz_*` (3) | sin tocar | prueban el medidor sobre fixtures grabados con intro; siguen valiendo |
| `test_module_f34.py::test_a7_2_la_musica_de_cada_cap_arranca_con_su_title_card` | **actualizado** → `…_arranca_en_el_0_del_cap` | sin `pre` ni `intro`; el camino no alineado da [0,0, −2,0, −4,0] (antes [−2,5, −4,5, −6,5]) |
| `test_module_f36.py::test_b9_la_intro_de_la_musica_es_initial_silence` | **borrado** | solo afirmaba la intro |
| `test_module_f38e_d.py::test_d2_…_y_la_intro_es_el_primer_cuadro` | **actualizado** → `…_y_el_mp4_arranca_con_el_cap` | la costura dice «el mp4 arranca con este cap → voz a…» y no hay `intro_s` |
| `test_module_f38e_a.py::test_a3_lineas_de_costura_contra_el_guion` | **actualizado** | sin la clave `pre_roll` en el json de escenas |

**Suite amplia con el código de A1:**
- 1581 verdes, más las 3 heredadas y 2 del mapa. Esas 2 fallaban porque los stickers todavía no estaban reescritos.
- Con los stickers al día, `test_module_f33.py` + `test_module_f42_mapa.py` dan 13/13.
- `mapa --check`: 0 fallas.

**Plan-only A1.** Salida en `lab/hyperframes/f79/a1/`: 544 s (con la suite corriendo al lado), exit 0. La comparación completa está en `a1/comparacion_0_a1.md`.

| Qué | Antes (Etapa 0) | Esperado | A1 |
|---|---|---|---|
| `duracion_s` | 798,266 | 777,766 ± 0,23 | **777,766** ✓ |
| `offset` ch02…ch07 | 69,3 · 172,133 · 344,833 · 444,533 · 576,366 · 704,866 | 66,8 · 166,633 · 336,333 · 433,033 · 561,866 · 687,366 | 66,8 · 166,633 · 336,333 · 433,033 · 561,866 · 687,366 ✓ |
| Inicio de voz en el mp4, ch01…ch07 | 2,66 · 72,38 · 175,213 · 347,913 · 447,633 · 579,466 · 707,966 | 0,16 · 66,88 · 166,713 · 336,413 · 433,133 · 561,966 · 687,466 | medido 0,16 · 66,88 · 166,713 · 336,413 · 433,133 · 561,966 · 687,466: los 7 ✓ (ch03 estaba ✗ «sin rampa» en la línea base; ahora ✓) |
| ch01 | title card 2,5–5,5 s del mp4; voz 2,66 | title card 0,0–3,0; voz 0,16 | title card con `t_mp4` 0,0 y 3,0 s; voz 0,16 ✓ |
| ch02–ch07, costura | negro 1,0 → sube 0,333 → title card 3,0 sin voz → voz 3,08–3,10 | negro 1,0 → sube 0,333 → voz 0,08–0,10 con el title card encima 0,0–3,0 | así, con el texto de costura nuevo; voz a 0,08 (ch02–ch04) y 0,10 (ch05–ch07) ✓ |
| `seg_dur` ch02–ch07 | 102,833 · 172,7 · 99,7 · 131,833 · 128,5 · 93,4 | −3,0 cada uno | 99,833 · 169,7 · 96,7 · 128,833 · 125,5 · 90,4 ✓ |
| Eventos ch02–ch07 | — | todo `t` > 0 baja 3,0; en 0,0 quedan la costura, el title card y los cortados sin instante | los eventos con `t` > 0 bajan 3,000 exactos salvo 3 (detalle abajo); en 0,0 quedan la costura (texto nuevo), el title card y SILENCIO (ch05, cortado) |
| Eventos ch01 | — | `t` igual, `t_mp4` −2,5, texto de costura nuevo | 13/13 con el mismo `t`; `t_mp4` −2,5; costura nueva ✓ |
| Reloj «16 SEP · 1961» (ch02) | 3,08 s, dura 9,55 s | lo decide `repartir` | **corrido a 6,48 s del cap (73,28 del mp4); dura 3,15 s.** Motivo que da el código: «0.08 → 6.48 s (3 · oración siguiente [1]), dura 3.15 s (corta en 9.63 s) · antes: 1 · palabra ancla (0.08 s): se solapa con title card». Clase **reserva del title card** |
| Otros bloques movidos o cortados por la reserva | — | ninguno | ninguno |
| «dos bloques al mismo tiempo» | ✓ | ✓ | ✓ |
| Golpe del title card | los 7 caps a 0,05 s | predicción §5.3 | coincide con la predicción: ch01 a 0,05 s (voz a 0,16); **ch02 y ch03 corridos +110 ms → 0,16 s** (hueco después de la primera palabra); **ch04 descartado** («cae sobre 'Daniel' sin hueco ≤ 120 ms»); ch05–ch07 a 0,05 s, pegado al ataque (voz a 0,10) |
| Música, inicio por cap | ch01, ch02 y ch04–ch06 ✓ en 0,0 · ch03 +6,900 ✗ · ch07 +15,809 ✗ | arranca en el 0,0 del cap; mismo desvío | ch01, ch02 y ch04–ch06 ✓ (desvío 0,000) · **ch03 +8,903 ✗ · ch07 +13,003 ✗** (ver «otra», punto 4) |
| Crítico | 0 llamadas | nº, US$ y veredictos que cambian | **22 llamadas** (ch01 0 · ch02 2 · ch03 3 · ch04 3 · ch05 4 · ch06 8 · ch07 2), **US$ 0,0035**; cambiaron 2 veredictos (puntos 2 y 3) |

**Diferencias que no son corrimiento de tiempo.** Todas listadas; ninguna se parchó.
1. **ch02, reloj «16 SEP · 1961»:** pasa de 3,08 a 6,48 s del cap, y de 9,55 a 3,15 s en pantalla. Clase **reserva del title card**: lo decidió la regla que ya existía en `pantalla_colocar`, sin regla nueva.
2. **ch03, sello AVISO:** pasa de 90,9 a 97,8 s del cap (lo esperado era 87,9). En la línea base, el crítico dijo ESTORBA las dos veces que se preguntó por el intento 1 («palabra de más peso», 100,8 s), y el sello cayó al intento siguiente (90,9 s). Con la clave nueva, el crítico volvió a preguntar por ese mismo intento (97,8 s = 100,8 − 3,0), dijo NO ESTORBA y el sello queda ahí. Clase **crítico**.
3. **ch04, sello CALMA:** en la línea base estaba cortado («no entra en ningún intento»: en el inicio de la escena 13, ESTORBA de los dos lados). Ahora, en el mismo intento (92,1 s = 95,1 − 3,0), el crítico dijo NO ESTORBA y el sello **queda**. Clase **crítico**. Por eso «papel sin colocar» pierde la línea de CALMA; sigue ✗ solo por SILENCIO de ch05.
4. **Música de ch03 y ch07:** siguen en ✗, que es el falso positivo conocido de F72b/F73 (la medida sobre una pieza que tiene adelante el silencio de una cita). Pero el desvío cambió y no es el corrimiento de tiempo: ch03 pasa de +6,900 a +8,903 s y ch07 de +15,809 a +13,003 s. Lectura no verificada: sin pre-roll, la voz arranca en el segundo 0 de la pista y no en el 3. Entonces la envolvente de intensidad (los silencios, en el tiempo de la voz) cae sobre otro tramo de la pista, y la ventana «más fuerte» de 4 s que busca la medida es otra. Clase **otra**. Se lista; no se corrige en esta tanda.

`GUION_PANTALLA.md/.json` de Wittenoom quedaron sin aprobar, como en la Etapa 0.

## Etapa A2 — el primer cap sin title card

**Código:**
- `script_engine/gfx_layer.py`: `plan_base(ctx, *, primero)`. El parámetro es obligatorio, sin valor por defecto. Con `primero` verdadero, el cap sale con `title_card: None`. `apply_gfx` le pasa `plan.is_first` (`ChapterPlan.is_first`, que ya existía). Caso límite: en un video de un solo cap, ese cap es el primero, así que no lleva title card.
- `fase2b.py`: el `titulo` del cap en el guion sale de `ctx["skeleton"]["title"]`, no del title card del plan.
- `sfx_title_card` no se tocó: sin title card no hay golpe.
- En A1 ya quedó que `tramos` y el chequeo de música no nombran un title card que no existe.

**Tests (A2):** nuevo `test_module_f79.py`, sumado a `suite_lista.txt`:
- `test_a2_el_primer_cap_no_lleva_title_card`: `plan_base` con `primero` da `None`; sin `primero`, da el title card con kicker y título.
- `test_a2_cap_sin_title_card_en_el_guion`: un cap sin title card no tiene el evento. Su costura no lo nombra y no lleva `title_card_s`. El encabezado `## ch01 — La herida que no cerraba (` no queda vacío.

**Plan-only A2** (`lab/hyperframes/f79/a2/`, 209 s, exit 0, costos `{}`, 0 llamadas al crítico). La comparación completa está en `a2/comparacion_a1_a2.md`.

| Qué | A1 | Esperado | A2 |
|---|---|---|---|
| ch01, evento `title card` | 0,0 s, 3,0 s | no está | no está ✓ (13 → 12 eventos; los otros 12, con el mismo `t` y `queda`) |
| ch01, golpe del title card | 0,05 s | no está | `gfx_sfx_ch01.json` = `[]` ✓ |
| ch01, `titulo` / encabezado | «La herida que no cerraba» | igual, ahora del skeleton | «La herida que no cerraba»; encabezado `## ch01 — La herida que no cerraba (00:00.0–01:06.8)` ✓ |
| ch01, costura / `tramos` | «… con el title card encima 3.0 s desde 0.0 s» · `title_card_s` 3,0 | sin nombrar el title card | «el mp4 arranca con este cap → voz a 0.16 s del cap» · `{negro_s 0, sube_desde_negro_s 0, voz_s 0.16}` ✓ |
| ch01, chequeo de música | «title card» (en A1 ya «inicio del cap») | no nombra el title card | «✓ ch01: inicio del cap 0.000 s · música medida 0.000 s» ✓ |
| ch02–ch07 | — | idénticos a A1 | mismos eventos y mismos `t`; los 6 `gfx_plan_ch0{2..7}.resolved.json` iguales byte a byte a A1 ✓ |
| `duracion_s` | 777,766 | igual a A1 | 777,766 ✓ |
| Bloques que se mueven a los 3 s liberados de ch01 | — | se listan | ninguno (los 12 eventos de ch01 conservan su `t`) |
| Chequeos | 5 ✗ | — | los mismos 12 con el mismo resultado que A1 |
