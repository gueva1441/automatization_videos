# DOC MAESTRO — Capa gráfica HyperFrames en automatization_videos

**Versión:** 1.1 · 2026-10-18 · **Estado:** F1 + F1b cerrados en rama `f1-gfx-layer` (`39e301f`, `3ecba0b`); F2 en handoff
**Fuente única.** Cada handoff referencia una sección de este doc. Si algo cambia, se cambia acá primero.
**Insumos:** `ANALISIS_HyperFrames_vs_pipeline_2026-10-18.md`, `F0_REPORT.md`, `LAB_REPORT.md`, `LAB_V2_REPORT.md` (todos en `lab/hyperframes/` o en el proyecto).

---

## 1. Decisiones cerradas (no se reabren sin dato nuevo)

| # | Decisión | Evidencia |
|---|---|---|
| D1 | HyperFrames es **capa de edición/gráficos/identidad**, no reemplazo de DepthFlow ni de Veo/Wan | Handoff original §4, análisis §3 |
| D2 | Punto de inserción: **dentro de `fase2b._build_chapter_segment`**, después de obtener `base_clip` (flux_visual / hybrid_visual / veo) y **antes** de quemar subs + pegar audio. Flag `--gfx`, fallback al `base_clip` original ante cualquier error | LAB v1 (grade tiñe subs), LAB v2 §7.1 |
| D3 | **Subs siguen siendo el ASS de fase2b**, quemados después de HyperFrames. El bloque custom de karaoke (paridad 205/205) queda en reserva para cuando se quiera rediseñar subs | LAB v2 P1 + §9 (pasada alpha = +33 min/video) |
| D4 | **Grade = CSS en la composición, receta B** (haze 0, teal solo en sombras, viñeta, grano; `gfx_config`). `media-treatment` **descartado**: 2× captura como atributo, 6.29× tiempo real como pasada de footage. En F2 el grade pasa a filtros FFmpeg equivalentes para habilitar el render disperso. Se elimina el "grain tail" del prompt del generador cuando el grade esté en prod | F1_REPORT §2, F1b (elección Omar: B) |
| D5 | **Sin transiciones shader** en prod (1 worker, ~6× costo). Intra-cap: crossfade CSS / flash CSS. Inter-cap: `transition_applier` FFmpeg se queda | LAB v2 §4 |
| D6 | **Mixer no se toca.** Carve de HyperFrames no iguala nivel sin calibrar | LAB v2 P2 |
| D7 | El LLM **nunca escribe HTML ni texto en pantalla**. Elige bloques de un inventario inmutable y llena parámetros. Todo string en pantalla pasa un **candado literal** (facts / narración / skeleton / canonical). Cromo fijo declarado aparte ("CAPÍTULO N", "DETALLE") | Doctrina del repo + LAB v1/v2 |
| D8 | Directores separados: `gfx_director` aparte de `flow_director` y `m07`. Comparten insumos, no prompt | Anti-patrón #1 |
| D9 | Libertad mínima al director: reglas duras primero, aflojar con datos de retención | Decisión Omar 2026-10-18 |
| D10 | Resolución y fps de prod no cambian (2560×1440 @30) | — |
| D11 | Video base para HyperFrames se re-encodea en `work_dir` con `-g 30 -keyint_min 30` (keyframe por frame) antes de renderizar | LAB v2 §4 (draft #1 falló) |
| D12 | Identidad > vistosidad: 5 efectos firma repetidos, no 20 efectos distintos | Decisión Omar |
| D13 | **Animaciones de texto firma:** `cascade` (nombres/lugares), `number_pop` (cifras), `stamp` (años/etiquetas). **Tipografía:** Playfair Display SC para callouts y recorte; Anton para subs, title card y `count_up`. Se integran en F2 | DECISIONES_F1b (elección Omar) |
| D14 | **Legibilidad:** callout = 0.4 s × palabras + 1 s, mín 2.5 s, nunca corta la frase hablada; recorte ≥ 4 s; count_up +2.5 s en el valor. Flash R1 solo en los 2 R1 mayores del cap, al 30 %; R2 12 f, R3 20 f. Zoom box ≤ 0.25 | F1b (feedback Omar al AB) |
| D15 | **Iteración = un cap.** `fase2b --only-cap chNN` (+`--gfx --gfx-debug`) es el camino de prueba; renders completos solo como medición oficial al cierre de una fase | F1b |
| D16 | Merge a `main` es gate de Omar, separado de la entrega de cada fase | Decisión Omar |

## 2. Arquitectura

```
fase2b._build_chapter_segment(plan)
   │
   ├─ base_clip  (flux_visual.mp4 | hybrid_visual.mp4 | veo.mp4)      ← sin cambios
   │
   ├─ [--gfx]  gfx_layer.apply(base_clip, plan, video_id) → gfx_clip
   │      1. reencode -g 30 → work_dir/chXX_base_g30.mp4
   │      2. (F1: grade CSS dentro de la composición · F2: grade FFmpeg sobre base_g30 para render disperso)
   │      3. gfx_plan = gfx_director (cache en work_dir/gfx_plan.json)
   │      4. gfx_literal_lock(gfx_plan)  → falla = plan vacío + warning
   │      5. templater: plantillas HTML + plan → proyecto HF en work_dir/gfx_chXX/
   │      6. hyperframes lint → render draft|looks → chXX_gfx.mp4 (sin audio)
   │      7. cualquier excepción → return base_clip (log)
   │
   ├─ subs ASS (igual)  +  audio (igual)  →  segment.mp4                ← sin cambios
   │
fase2b._concat_segments + transiciones + música                         ← sin cambios
```

Módulos nuevos (todos en `script_engine/` salvo config):
- `gfx_config.py` — settings de render + **inventario inmutable de bloques** + reglas duras + rangos (patrón `flow_config`).
- `gfx_director.py` — 1 call Gemini Flash por cap → plan JSON validado contra inventario (patrón `flow_director`). Cache por video.
- `gfx_literal_lock.py` — candado determinista (patrón del `check_literal.py` del lab).
- `gfx_layer.py` — orquestador de los 7 pasos de arriba + fallback.
- `gfx_templates/` — HTML/CSS/GSAP de los bloques (`.html.tmpl` con `string.Template`; desvío aprobado: sin jinja2).
- `gfx_review.py` — hoja de cues (`gfx_cues_chNN.md/.json`), overlay `--gfx-debug`, página `gfx_review_chNN.html`.
- `cost_tracker.track_gemini` para la call del director (ya cubierto por `call_flash_json`).

## 3. Inventario de bloques (v1.0 — el que ve el LLM)

| Bloque | Parámetros que llena el director | Reglas duras |
|---|---|---|
| `title_card` | `title` (skeleton, literal), `chapter_number` | 1 por cap, siempre, 1.9 s, no congela video |
| `data_callout` | `fact_idx` + fragmento literal (≤ 8 palabras) del fact, `trigger_word_idx`, `kind` year/figure/name/place | máx 3/cap (F2: 5) · omitir si `text_in_image` ya trae el dato · tercio superior · duración D14 |
| `archive_clipping` | `kicker`, `headline`, `body` (literales), `scene_idx`, `era_decade` | máx 1/cap · cuerpo ≥ 52 px · fuente por década |
| `evidence_zoom` | `scene_idx`, `box[x,y,w,h]` (0–1), `label` fijo "DETALLE" | máx 1/cap · sobre frame de video · salida en corte |
| `count_up` | `value` (literal), `unit`, `trigger_word_idx` | máx 1/cap · solo cifras presentes en facts |
| `shot_transition` | por corte: `rank` R1/R2/R3 → flash CSS 30 % (solo 2 R1 mayores) / crossfade 12 f / disolvencia 20 f | determinista desde `emotional_rank`, el LLM no lo elige |
| `punch_in` | `trigger_word_idx` (≤2/cap) | 1.00→1.03 en 200 ms, sobre la capa de video |
| `grade` | — (receta B en `gfx_config`) | todos los caps, incluido Veo |

Pattern interrupt: al menos un bloque visible cada 25–35 s. F1: solo `gap_warning` (Orleans: 4 caps con huecos). F2: el validador rellena el hueco (director v1).

Fuera del inventario v1.0 (entran en fases posteriores): `map_pin` v2, `redacted_doc`, `match_cut_photo_map`, `evidence_board`, `timeline_bar`.

## 4. Fases y orden de entrega

Cada fase cierra **ensamblable sola**. Si el siguiente video sale a mitad de una fase, sale con las fases cerradas.

| Fase | Contenido | Criterio de salida | CC est. |
|---|---|---|---|
| **F1** ✅ | Inserción + grade + 7 bloques + director v0 + lock + tests. **F1b:** `--only-cap`, cues, `--gfx-debug`, página de revisión, calibración D14, grade B, sampler de animaciones, prefetch director, ultrafast | Orleans completo: 0 fallbacks, subs idénticos, sin `--gfx` byte-idéntico. Extra +27.5 min (est. 24.5 tras F1b). Commits `39e301f`, `3ecba0b` | hecho |
| **F2** | Director v1 (facts por cap, guard de época, hueco obligatorio, box por visión, anti-spoiler) + animaciones firma D13 + boosters (render disperso, caps en paralelo, NVENC, re-ensamble incremental) + router DepthFlow/HF-seguro | Orleans ≤ 25 min extra; re-ensamble ≤ 5 min; 0 facts foráneos; 0 deformaciones | 14–18 h |
| **F3** | `map_pin` v2 (10 m, perspectiva, capas por beat) + geo en canonical (`step_4b`) + `segments_map.json` desde fase2b | Mapa automático en ch01 | 4–5 h |
| **F4** | Efectos firma secundarios: `redacted_doc`, `match_cut_photo_map`, `timeline_bar` | En inventario, usados ≤1/video | 3–4 h |
| **F5** | Pestaña "gráficos" en QA Studio (editar/apagar plan por cap) + re-render parcial por escena | Omar edita un callout sin tocar JSON a mano | 4–6 h |
| **F6** | Audio: calibrar carve (strength 0.25–0.4) vs mixer; subs custom adentro si hace falta rediseño; `--batch rows.json` como templater | Solo si LUFS/ducking igualan | 4–6 h |

Para el **siguiente video**: F1 + F2 obligatorias; F3 si entra.

## 5. Métricas a registrar por video

- Tiempo extra de render `--gfx` (objetivo ≤ 20 min por video de 15 min sin shaders).
- Nº de fallbacks a `base_clip` (objetivo 0).
- Nº de strings rechazados por el lock (si > 0, el director está alucinando).
- Retención YouTube a 7 días vs. video anterior (único dato que justifica F4+).

## 6. Riesgos y deudas abiertas

| Riesgo / deuda | Dueño | Fase |
|---|---|---|
| Captions desaparecen 0.3 s bajo shaders (bug HF) — evitado por D5, no resuelto | HF upstream | — |
| `anchor_timing` vs corte real: 45 ms constantes de adelanto; causa no identificada | F2 | investigar antes de sumar constante |
| Canonical sin `geo` | F3 | `step_4b` |
| Offsets de caps dentro del final no derivables del sync_map | F3 | `segments_map.json` |
| `verified_facts` sin `id` (hard_fact_ids referencia F01…) | F3 | el director asume orden = id; proponer `id` en `step_4a` |
| Lock: substring sin límite de palabra ("6 metros" ⊂ "4.6 metros"); mitigado por fragmento ≤ 8 palabras del fact elegido | F2 | límite de palabra en el lock |
| Director v0 elige facts de otros caps y adivina el box del zoom | F2 | director v1 |
| Re-ensamble completo (~18 min) por cualquier corrección | F2 | incremental |
| Laptop: throttling térmico y RAM (Firefox 5.6 GB) limitan paralelismo | Omar | cerrar Firefox al renderizar; torre solo si > 60 videos/mes |
| Carve +3 dB voz / −17.5 dB cama | F6 | calibrar |
| Render time si se mete cualquier shader | todos | D5 |
| Patrón 80 %: cada fase cierra con medición oficial en video completo | Omar | gate por fase |

## 7. Vigilante mensual (chascada aprobada)

Tarea programada mensual, 30 min: novedades por capa (gen. imagen, I2V, parallax, HyperFrames releases, TTS, subtítulos). Informe de 10 líneas "cambia algo / no cambia nada". Pendiente de crear.

## 8. Historial
- 2026-10-18 v1.0 — decisiones tras F0/LAB v1/LAB v2.
- 2026-10-18 v1.1 — F1 + F1b cerrados; D4 cambiado a grade CSS B; D13–D16 nuevas; F2 redefinida (director v1 + boosters + router).
