# F28_REPORT — paleta musical a producción, mapa de intensidad, re-mezcla de Vajont (B) y render más rápido (C)

CC · 2026-10-25 · base `22582d7` (parte A cerrada con PARADA; ver `F28A_REPORT.md`), rama `f11-guion-v4`, sin merge, nada
publicado, nada borrado (las curated se movieron). Handoff `lab/hyperframes/f28/HANDOFF_F28_paleta_musical.md`
(§B y §C). Elección del analista: `lab/hyperframes/f28/ELECCION_F28_12_pistas.md`.

## En corto
- **B — hecha** (`e3fd23a`):
  - Las 12 pistas elegidas están en `audio_library/<intent>_f28_<a|b>.mp3`: recortadas de fade (157–174 s), con loop
    por acrossfade de 3 s y nivel calibrado. Las curated quedaron en `audio_library/_retiradas/`.
  - En m07, el matcher elige entre las 2 de cada intent y nunca genera.
  - Hay mapa de intensidad por cap (`silencio | fondo | sube | golpe`), aplicado como envolvente en fase2b.
  - Vajont, re-mezcla solo de audio → **`output/f8s3-vajont/f8s3-vajont_final_gfx_v2.mp4`** (1009.1 s, en 37 s de
    mezcla). Con música queda **+0.2 LU sobre la voz sola** (objetivo ≤ 0.5).
- **C — cerrada con lo que hay** (`8e35b25`; Omar canceló la 2.ª corrida):
  - **3 gfx en paralelo: descartado.** 4 de 7 caps quedaron en fallback por timeout; los 69.6 min salieron solo porque
    no dibujó la mitad.
  - **Quedan por defecto NVENC y 6 workers de clips.** Los tiempos de pase medidos son de ch01–ch03 de la corrida 2.
  - **El re-render completo queda NO medido.**
- **Gasto:**
  - Gemini: unos US$ 0.26 medidos (fase2b de la corrida 1) más el matcher de m07 y la corrida 2 cancelada, que no se
    midieron (centavos).
  - ElevenLabs 0, Claude 0, imágenes 0.
- **Suite amplia:** 909 verdes + las 5 previas.

---

## B. Paleta a producción + mapa de intensidad + re-mezcla de Vajont — HECHA (`e3fd23a`)

### B.1 Las 12 a producción (`b/f28b_paleta_produccion.py`, 0 API)
- **Recorte:** los segundos de fade medidos en la parte A, más 0.5 s de margen de cada lado, con libmp3lame 192k.
- **Loop:** `loop_crossfade_s: 3` en el json. fase2b empalma el loop con `acrossfade` de 3 s en vez de `-stream_loop`
  seco; solo con pistas que traen esa clave, así que la ruta vieja no cambia.
- **Nivel — decisión de método.** El chat 40 calibró a oído, en el mixer, y no dejó un LUFS objetivo escrito. Usé el
  **nivel efectivo** de la curated del mismo intent (LUFS integrado + 20·log10 de su `music_volume`, lo que entra a la
  mezcla antes del ducking):
  - `music_volume` nuevo = 10^((efectivo − LUFS de la pista)/20);
  - el `floor` guarda la proporción floor/volume de esa curated;
  - la verificación es la mezcla de Vajont (§B.3).
- **json de cada pista:** `origen`, plan, medidas, nota y descripción de Gemini (también en
  `elevenlabs_metadata.description`, que es lo que lee el matcher), `paleta: "f28"`. `consequences` también cubre
  `resolution`. Copia de los 12 json en `b/audio_library_json/`, porque `audio_library/` no va a git.
- **Curated:** las 7, mp3 + json, **movidas** a `audio_library/_retiradas/`.
- **m07:** si los candidatos del intent son de la paleta, `_match_intent_to_track(..., umbral=0)` elige entre los 2. Si
  el matcher no contesta bien, se queda la «a». Nunca genera. `MUSIC_LENGTH_MS` = 180000, solo informativo.

| pista | origen | recorte in / out (s) | duración (s) | LUFS | music_volume / floor | curated de referencia (efectivo) |
|---|---|---|---|---|---|---|
| hook_f28_a | hook_03 | 1.5 / 9.5 | 169.0 | −11.5 | 0.053 / 0.034 | hook (−37.07) |
| hook_f28_b | hook_05 | 5.5 / 10.5 | 164.0 | −12.0 | 0.056 / 0.036 | hook |
| setup_f28_a | setup_03 | 5.5 / 6.5 | 168.0 | −13.0 | 0.222 / 0.180 | setup (−26.06) |
| setup_f28_b | outro_03 | 5.5 / 8.5 | 166.0 | −13.1 | 0.225 / 0.182 | setup |
| rising_tension_f28_a | rising_tension_04 | 8.5 / 8.5 | 163.0 | −12.0 | 0.096 / 0.062 | rising_tension (−32.38) |
| rising_tension_f28_b | rising_tension_05 | 9.5 / 13.5 | 157.0 | −13.6 | 0.115 / 0.074 | rising_tension |
| shock_f28_a | shock_03 | 2.5 / 7.5 | 170.0 | −12.5 | 0.069 / 0.026 | shock (−35.74) |
| shock_f28_b | shock_04 | 1.5 / 4.5 | 174.0 | −12.2 | 0.067 / 0.025 | shock |
| consequences_f28_a | consequences_03 | 3.5 / 9.5 | 167.0 | −13.5 | 0.202 / 0.121 | consequences (−27.38) |
| consequences_f28_b | consequences_04 | 4.5 / 11.5 | 164.0 | −14.0 | 0.214 / 0.128 | consequences |
| outro_f28_a | outro_01 | 3.5 / 14.5 | 162.0 | −12.8 | 0.038 / 0.028 | outro (−41.16) |
| outro_f28_b | outro_02 | 2.5 / 8.5 | 169.0 | −15.2 | 0.050 / 0.037 | outro |

Las 12 quedaron entre 157 y 174 s, dentro de 150–175.

### B.2 Mapa de intensidad (`script_engine/music_intensity.py`, sin LLM, sin gate)
- **Entradas:** los beats de `01a_escaleta.json` (cap, funcion, intensidad, ids), los párrafos de
  `01b_narracion_v3.json` (cap, beat, texto) y `chNN_timestamps.json`. Cada palabra del texto se ubica en el tiempo
  por proporción contra las palabras de la voz, porque la voz normalizada puede tener más palabras.
- **Reglas fijas:**
  - **fondo:** 0 dB en todo el cap.
  - **sube:** +3 dB, con rampas de 1 s, en los beats con intensidad ≥ 4 que no son el pico del video.
  - **golpe:** +5 dB y vuelta a fondo en 4 s, **solo en el beat de pico** (funcion «pico»).
  - **silencio:** −∞ con fade de 1.5 s. Va (a) en los 1.5 s antes del beat más intenso del cap y (b) durante una cita
    de testigo («…» en un beat que trae una cita del pool con `testigo=True`). Máximo 2 por cap, con (a) primero.
- **Decisión** (dentro de las reglas): un silencio de cita no puede tapar el golpe. En Vajont ch06, la cita de Onorini
  empezaba 3.4 s después del golpe y lo cortaba; se toma la siguiente cita.
- **fase2b:** `_mapa_intensidad` arma el mapa si el topic tiene escaleta, narración y pool, y lo deja en
  `output/audio/<id>/intensity_map.json`. `_build_music_piece_for_chapter(envolvente=)` aplica las ganancias sobre la
  pieza WAV de cada cap, en las dos pistas (ducked y floor). Sin esos archivos no hay envolvente, y la música sale como
  antes.

### B.3 Re-mezcla de Vajont, solo audio (`b/f28b_remezcla.py`)
- **No pisa nada:** usa los insumos del render de F27 (`_concat_video.ts`, `_concat_audio.wav`) y las mismas
  funciones de la etapa de música de fase2b. Escribe **`f8s3-vajont_final_gfx_v2.mp4`** y no toca el
  `_final_gfx.mp4` de F27.
- El `music_map.json` de F26 quedó como `music_map_f26.json` (movido).
- **`--hw-encode`:** solo afecta al clip de arranque de 2.5 s; el video va por copia.
- **Tiempos:** mezcla 37 s; pase total con el matcher 93 s.
- **Verificación:** ffprobe da 1009.1 s de video y audio, y los primeros 20 s decodifican sin errores.

| cap | intent | pista (matcher) | LUFS sin música | con música | Δ | F27 (curated) | tramos del mapa |
|---|---|---|---|---|---|---|---|
| ch01 | hook | hook_f28_a (90) | −24.4 | −24.7 | −0.3 | −24.6 | sube 0–94 s · silencio 34–42 · 56–62 (citas de testigo) |
| ch02 | rising_tension | rising_tension_f28_a (85) | −25.3 | −25.1 | +0.2 | −24.9 | silencio 64–66 (antes del pico del cap) · 69–70 (cita) |
| ch03 | rising_tension | rising_tension_f28_b (92) | −24.6 | −24.7 | −0.1 | −24.4 | fondo |
| ch04 | rising_tension | rising_tension_f28_a (90) | −25.2 | −24.6 | **+0.6** | −24.8 | silencio 51–52 · sube 52–116 |
| ch05 | rising_tension | rising_tension_f28_b (93) | −25.7 | −24.9 | **+0.8** | −25.4 | sube 0–91 · silencio 45–47 · 59–61 · sube 91–166 |
| ch06 | shock | shock_f28_a (**68**) | −24.2 | −24.5 | −0.3 | −24.5 | golpe 0–4 · silencio 39–45 · 57–67 |
| ch07 | outro | outro_f28_b (92) | −24.8 | −24.8 | 0.0 | −24.9 | silencio 10–12 · 23–30 |
| **total** | | | **−24.9** (LRA 5.5) | **−24.7** (LRA 4.4) | **+0.2** | −24.8 (LRA 5.1) | |

- **Total:** ≤ 0.5 LU sobre la voz.
- **Por cap:** ch04 y ch05 pasan de 0.5, y son justo los caps con tramos «sube» (+3 dB).
- **Ruido de la medida:** los Δ negativos (−0.1/−0.3) son la medida por tramo de ebur128 (gating); no hay pérdida
  real.
- **El LRA bajó** de 5.1 (F27) a 4.4.
- **Matcher:** en shock eligió con score 68. Antes, eso disparaba generar una pista nueva; ahora se queda dentro de la
  paleta.
- **Loop:** ch05 (166 s > rising_tension_f28_b 157 s) y ch07 (180 s > outro_f28_b 169 s) usaron el loop con
  crossfade.
- **No lo escuché:** el mapa, los silencios y el empalme del loop **no se verificaron de oído**. Queda para Omar.

### B.4 Tests (sin red) — `test_module_f28b.py`, 9 verdes
- Poda sobre medidas sintéticas. Para eso, `poda()` se sacó a una función en `a/f28a_paleta.py`; las medidas de la
  parte A salen byte-idénticas.
- Mapa de intensidad sobre una escaleta de prueba: silencio antes del pico del cap; la cita sin testigo no calla; el
  golpe va solo en el pico y el silencio no lo tapa; sube en beats ≥ 4; como mucho 2 silencios.
- Envolvente con las ganancias esperadas (0 / +3 / +5 dB con vuelta en 4 s / silencio con fade de 1.5 s) y su
  aplicación a un WAV.
- fase2b: loop con acrossfade (3 copias para 400 s, sin `-stream_loop`) y envolvente; sin `loop_crossfade_s`, la ruta
  de siempre.
- m07: elige entre las 2 de la paleta con umbral 0 y la «a» si el matcher no contesta; nunca genera.

---

## C. Render más rápido — CERRADA CON LO QUE HAY (`8e35b25`)

| variable | estado | dato |
|---|---|---|
| C.1 `--hw-encode` por defecto | **por defecto** | `_HW_ENCODE = True`. `--sw-encode` vuelve a libx264; `--hw-encode` se acepta y no cambia nada. **El candado md5 de ch02 sin gfx (`38e5ba14…`) ahora se mide con `--sw-encode`.** |
| C.2 gfx de 3 caps en paralelo | **DESCARTADO** | **4 de 7 caps quedaron en fallback por timeout; los 69.6 min salieron solo porque no dibujó la mitad.** `GFX_PARALELO = 1`, en fila como antes. |
| C.3 clips animados 4 → 6 workers | **por defecto** | `CLIP_WORKERS = 6`. |
| C.4 re-render completo contra 128.4 min | **NO MEDIDO** | La corrida 1 no vale (sin gfx en 4 caps). La corrida 2 fue cancelada por Omar durante ch03–ch04. |

**Corrida 1** (3 caps a la vez, NVENC, 6 workers; topic copia `f8s3-vajont-f28c` para no pisar F27, mismos assets,
audio, script y pasos):
- 69.6 min.
- `[gfx] chNN fallback a base_clip: GfxError: render excedió timeout 900s` en **ch02, ch04, ch05 y ch06**.
- Los gfx que sí terminaron tardaron 840 s (ch01), 1358 s (ch03) y 1047 s (ch07). En F27 fueron 384, 792 y 678.
- RAM libre mínima **1.44 GB**; VRAM máxima 10.9 GB de 16.
- El mp4 salió de 989.5 s (no 1009: faltan las pausas de cierre de los caps sin gfx) y **1.6 GB** (F27, libx264: 606
  MB).
- Salida apartada en `output/_bak_f8s3-vajont-f28c_run1/` (movida, no borrada).

**Corrida 2 — tiempos de pase medidos (ch01–ch03).** Fue con 2 caps a la vez, NVENC y 6 workers, y se canceló en
ch03–ch04:

| pase | ch01 | ch02 | ch03 |
|---|---|---|---|
| visual base, DepthFlow (6 workers) | 93 s (F27, 4 workers: 85) | 177 s (176) | 163 s (182) |
| gfx (2 caps a la vez) | 629 s (F27, en fila: 384) | 999 s (735) | no terminó |
| flow_director (LLM) | 125 s (F27: 103) | | |

**Lectura:**
- **6 workers no acelera DepthFlow**, que va a la par: el cuello es la GPU.
- **El gfx en paralelo tarda 1.4–1.6× más por cap.** La CPU y la RAM no alcanzan para dos renders de HyperFrames a la
  vez, sin hablar de tres.
- El paso del encode NVENC no se aisló en el log: la ganancia de NVENC es la medida en F2 (~8× en el pase de segmento),
  no una medida de esta tanda.
- Las dos corridas sin crash de DepthFlow (F27 tuvo 1).

**Código** (`fase2b.py`):
- `_visual_base` sacado tal cual de `_build_chapter_segment`, bajo `_VISUAL_LOCK`.
- `_segmentos_en_paralelo` (apagado con `GFX_PARALELO = 1`, se puede prender): orden de segmentos, reintento por
  memoria y **cap que perdió el gfx en paralelo → se rehace en fila**. Agregué esto después de la corrida 1, porque
  `apply_gfx` cae a `base_clip` sin avisar.
- Tests: `test_module_f28c.py` (7, la función se prueba forzando 2).
- Suite amplia: **909 verdes + las 5 previas** (3 `01b_pauses`, 2 `m03_merge_timing`).

---

## Lo que queda abierto
- **Escuchar la v2 de Vajont:** los silencios en las citas de testigo, el golpe del pico y el empalme del loop en ch05
  y ch07.
- **ch04 y ch05 quedan +0.6/+0.8 LU** por los tramos «sube». Si suenan altos, se baja `sube` de +3 dB.
- **`test_module_40_volumen_por_track.py`** (smoke manual del chat 40, fuera de la suite) lee los json de las curated
  en `audio_library/`, que ahora están en `_retiradas/`. Si se corre, falla.
- **Tamaño con NVENC cq19:** el video pesa ~2.7× más que con libx264. Para subir a YouTube no importa; en disco, sí.
- **Por qué fallan los timeouts del gfx:** `gfx_render` tiene un timeout fijo de 900 s por cap. Con caps de 3 min ya
  está cerca en fila: ch05/ch06 de F27 tardaron 956 y 983 s, con el sparse de 1800.

## Archivos
`lab/hyperframes/f28/`:
- **Raíz:** este reporte, `ELECCION_F28_12_pistas.md`, `suite_amplia_b.log`, `suite_amplia_c.log`.
- **`b/`:**
  - Scripts: `f28b_paleta_produccion.py`, `f28b_remezcla.py`.
  - Datos y logs: `paleta_produccion.json`, `remezcla_vajont.json`, `remezcla.out`.
  - Mapas de Vajont: `music_map.json`, `intensity_map.json`.
  - `audio_library_json/` (los 12 json).
- **`c/`:** `f28c_rerender.py`, `f28c_tiempos.py`, `tiempos.json`, logs de las dos corridas (`*_run1_3caps*`,
  `*_run2_2caps_cancelada*`).

**Fuera de git:**
- `audio_library/` (12 pistas nuevas, `_retiradas/`, `_paleta_f28/`).
- `output/f8s3-vajont/f8s3-vajont_final_gfx_v2.mp4`.
- `output/audio/f8s3-vajont/` (`music_map.json` nuevo + `music_map_f26.json` + `intensity_map.json`).
- `output/_bak_f8s3-vajont-f28c_run1/`.
- `output/f8s3-vajont-f28c/` (corrida 2, a medio hacer).
- La copia del topic en `output/audio/f8s3-vajont-f28c/` y `data/scripts/(_steps/)f8s3-vajont-f28c*`.

## Veredicto del revisor-handoff

VEREDICTO: CUMPLE CON OBSERVACIONES

Corrí `test_module_f28b.py` y `test_module_f28c.py`: 16 passed. El log de la suite amplia de C da 909 verdes + 5 fallas previas (3 de 01b_pauses y 2 de m03_merge_timing), como declara el reporte. No re-corrí la suite completa.

| # | requisito | estado | evidencia |
|---|---|---|---|
| B1 | 12 pistas a `audio_library/<intent>_f28_<a|b>.mp3`+json, recortadas de fade, 150–175 s | OK | `ls audio_library`: 12 mp3 + 12 json. Los json coinciden con `lab/hyperframes/f28/b/audio_library_json/` (`cmp` sin diferencias). El mapeo coincide con `ELECCION_F28_12_pistas.md`, incluido `setup_f28_b` = `outro_03`. Duraciones 157–174 s en el reporte. |
| B2 | Loop con acrossfade de 3 s solo si la pista trae `loop_crossfade_s` | OK | `fase2b.py` `_build_music_piece_for_chapter`: la rama usa `acrossfade=d=3`, se activa con `loop_crossfade_s` y la ruta vieja queda intacta. Los 12 json traen `loop_crossfade_s: 3.0`. Los tests lo cubren. |
| B3 | Calibración de `music_volume`/`floor` | OK con salvedad | Método declarado: nivel efectivo de la curated del intent. El json de `hook_f28_a` guarda `calibracion` con `curated`, `I_pista` y `objetivo_efectivo`. La verificación real es la mezcla de Vajont (+0.2 LU en total). El handoff pedía «el mismo método del chat 40», que fue a oído y no dejó LUFS escrito. La decisión es razonable y está declarada. |
| B4 | Curated movidas, no borradas | OK | `audio_library/_retiradas/` tiene 14 archivos (7 mp3 + 7 json, incluida resolution). |
| B5 | m07 elige entre las 2 de la paleta, sin umbral y sin generar; `MUSIC_LENGTH_MS` = 180000 | OK | `m07_music_director.py:1101-1109` (`umbral=0`, y si el matcher no contesta, la «a»). `music_config.py` = 180000. `remezcla.out` muestra «REUSE» en los 7 caps, también shock con score 68. |
| B6 | Mapa de intensidad según las reglas del §B.2 | OK | `music_intensity.py` implementa las reglas. `b/intensity_map.json`: máximo 2 silencios por cap (ch01, ch02, ch05, ch06 y ch07 tienen 2; ch04 tiene 1; ch03 ninguno). Hay un solo golpe, en ch06 (0.14–4.14). Los silencios son «antes del pico del cap» o «cita de testigo». Las cifras de la tabla del reporte coinciden con `remezcla_vajont.json`. |
| B7 | Envolvente aplicada en fase2b sobre la pieza de música de cada cap | OK | `_mapa_intensidad` y `aplicar_a_wav` (`fase2b.py`, ruta ducked y floor). Los tests f28b verifican 0/+3/+5 dB, la vuelta en 4 s y el fade de 1.5 s. |
| B8 | Re-mezcla de Vajont solo audio → `_final_gfx_v2.mp4`, sin tocar el F27 | OK | ffprobe de v2: h264 + aac, 1009.133 s, 635.6 MB. `_final_gfx.mp4` de F27: 1009.133 s, 635.8 MB, fecha 13:43 (anterior a los commits de F28). Total con música −24.7 LUFS contra −24.9 sin música: +0.2 LU, dentro del límite de 0.5. |
| B9 | Tests sin red | OK | 9 tests f28b pasan. Refactor de `poda()` en `a/f28a_paleta.py`, declarado; solo moví el código de lugar. |
| C1 | NVENC por defecto, `--sw-encode` para volver | OK | `fase2b.py`: `_HW_ENCODE = True` y `_HW_ENCODE = not args.sw_encode`. El test f28c lo verifica. |
| C2 | 3 gfx en paralelo | DESCARTADO (conforme a la orden de Omar) | `GFX_PARALELO = 1`, el código queda apagado. `tiempos.json` confirma el fallback a base_clip en ch02, ch04, ch05 y ch06, 69.6 min y RAM mínima 1.44 GB. |
| C3 | Clips a 6 workers | OK | `CLIP_WORKERS = 6`, usado en `_build_flux_visual`. |
| C4 | Re-render medido contra 128 min | NO MEDIDO (conforme a la orden de Omar) | El reporte lo dice así. Los tiempos de ch01–ch03 de la corrida 2 coinciden con `tiempos.json`. |
| C5 | Cifras de C | OK | Gfx de la corrida 2: 629 s (ch01) y 999 s (ch02), contra 384 y 735 en F27. Eso da 1.64× y 1.36×, y el reporte dice «1.4–1.6×» (redondeo laxo). La salida de la corrida 1 pesa 989.5 s y 1628.6 MB según el log. |
| C6 | Un commit por parte, sin merge, sin publicar, sin borrar | OK | `e3fd23a` es B y `8e35b25` es C. El `git diff --stat` no incluye `.env` ni `config.py`. |

Fuera de alcance: ninguno en los commits. Lo modificado y sin commitear ya estaba sucio al arrancar: `diag_234_cap4.py`, `gfx_profiles/lexico_propuestas.json`, `gfx_profiles/misterio.json` y `lab/hyperframes/f28/a/f28a.log`. Antes de commitear el reporte, conviene no incluirlos. `lab/ESTADO_SESION.md` todavía no está actualizado (esperado).

Decisiones juzgadas:
- **Calibración por nivel efectivo:** aceptable. No hay LUFS objetivo escrito del chat 40. La prueba objetiva es la mezcla (+0.2 LU en total), pero ch04 (+0.6) y ch05 (+0.8) superan el 0.5 por cap. El reporte lo declara.
- **Copia del topic para el re-render:** válida, no pisa F27. Quedan restos fuera de git (`output/_bak_f8s3-vajont-f28c_run1/`, `output/f8s3-vajont-f28c/`).
- **Silencio que no tapa el golpe:** dentro de las reglas, y hay un test. El caso real fue la cita de Onorini en ch06.
- **Apagar el paralelo con `GFX_PARALELO=1` en vez de borrar el código:** aceptable. Es código muerto, pero con test, con motivo escrito en el comentario y alineado con «nada se borra».

Observaciones:
1. El help de `--hw-encode` en `fase2b.py` sigue diciendo «Default off (libx264)». Es texto desactualizado.
2. El candado md5 de ch02 sin gfx (`38e5ba14…`) ahora exige `--sw-encode`. Está en el reporte pero no se lo corrió con la bandera.
3. `test_module_40_volumen_por_track.py` falla si se corre, porque las curated están en `_retiradas`. Está declarado.
4. Gasto de Gemini en B y C sin medir exacto (centavos, según el reporte).
5. Todo lo auditivo queda sin verificar: silencios, golpe, empalme del loop en ch05 y ch07, y ch04/ch05 con «sube». Esto es solo para oído de Omar.
6. En ch02 los dos silencios están a 2.7 s de distancia, con fades de 1.5 s. La música casi no suena entre ellos.

Riesgos que el contrato no cubre:
- NVENC por defecto: el mp4 con gfx pesa ~2.7× más que con libx264 (1.6 GB contra 606 MB). Con un pipeline que sube a YouTube desde disco, la diferencia pesa. La ganancia de ~8× en el pase de segmento sale de F2, no de una medida de esta tanda.
- El timeout fijo de 900 s del gfx ya está al borde en fila con caps de 3 min (ch05 tardó 956 s y ch06 983 s en F27). Puede degradar silenciosamente a base_clip.
- No hay medición del tiempo de re-render real con NVENC + 6 workers en fila, así que el beneficio de C sobre los 128 min es desconocido.

**Después del veredicto (CC):** observación 1 corregida en el commit final (el help de `--hw-encode` ahora dice que NVENC es el default y que `--sw-encode` vuelve a libx264). Las demás quedan como están en «Lo que queda abierto».

**PARADA.**
