# REPO_MAP — automatization_videos

> Índice CURADO de los 55 módulos de PRODUCCIÓN. **No** reemplaza ARCHITECTURE.md ni
> MODEL_PROMPTING_RULES.md — los INDEXA (ver §DOCTRINA al final).
>
> **Cómo usar (aflojar el ritual):** leer este mapa primero (orientación en segundos),
> y hacer deep-read SOLO de las secciones de ARCH/MPR que toca el laburo del chat.
> Mantener: actualizar al cierre cuando cambie una responsabilidad (correr el agente
> `structure-auditor` → re-curar este archivo).
>
> Ruido excluido a propósito: `_lab_*`, `_probe_*`, `diag_*`, `test_*`, `migrate_*`,
> `promote_*`, `purge_*`, `art_profiles`/`art_config` (desconectados chat19),
> `version_stamp` (lo corre CC a mano). Son ~165 archivos que NO son el pipeline.

---

## MAPA DE FASES (espina dorsal)

```
fase1 ───► fase1_5 ───► fase2a ───► fase2b ───► fase3
RESEARCH    GUIÓN        ASSETS      ENSAMBLE    PACKAGING
(topics)   (script+TTS) (PNG/clips) (video MP4)  (thumb+meta)

run_pipeline = secuenciador (spawnea cada fase por subprocess)
servers aparte: qa_studio_server (botón Ensamblar) · mixer_server (mezcla audio)
```

---

## FASE 1 — research + validación de topics  *(todos en `root` salvo marcado)*

| módulo | OWNS (qué hace) | entry-point |
|---|---|---|
| **fase1** | Orquestador "Latido A": niche→juez→pick→research→validate→csv, in-process | `run_latido_a()` · CLI |
| **topic_researcher** | Investiga cada seed → topic en topics_db (SHORT 1 call Pro / LONG 3+5 sub-pasos en `researcher_steps/`) | `research_topics()` |
| **topic_validator** | Market Architect v3: valida con Trends + YouTube, genera 3 hooks+3 outros | `validate_topics()` |
| **niche_discoverer** | Entry hub: genera seeds (A spy-arbitraje / B arqueología Gemini / C manual) | `discover_niches()` |
| **subtopic_measurer** `script_engine` | Mide demanda por subtema, compuerta ES-primero (no paga EN si ES saturado) | `_measure_es/_measure_en_laxo` |
| **subtopic_extractor** `script_engine` | Spy stage 2: extrae sujetos-de-segmento de transcript (dormido, `SUBTEMA_FANOUT`) | `extract_segment_subjects()` |
| **subtopic_classifier** `script_engine` | Spy stage 1: clasifica video ATÓMICO/CONTENEDOR (dormido) | `classify()` |
| **subtopic_es_relevance** `script_engine` | Fix saturación ES: traduce nombre EN→ES + filtra relevancia (juez-LLM) | `translate_to_es/filter_relevant` |
| **m_judge_seeds** `script_engine` | Juez LLM pre-grounding de seeds, vota N=3 (marca, no descarta) | `judge_seeds()` · CLI |
| **cost_tracker** | Rastreador de costos (singleton): acumula por video, reporta + historial | `track_*` (singleton) |
| **csv_exporter** | Dashboard CSV `fase1_review.csv` (1 fila/topic, celdas editables) + parse de vuelta | `export_fase1_csv()` |

### Sub-pasos LONG de topic_researcher  (`researcher_steps/`, encadenados — cada uno recibe los previos CERRADOS)

| módulo | OWNS | entry-point |
|---|---|---|
| **step_4a_facts** | Extrae verified_facts + sources de los bloques angulares; taggea cada fact con su source_block (rompe bug 1943↔1937) | `extract_facts_and_sources()` |
| **step_4b_canonical** | Descripción canónica del sujeto recurrente (EN, 20-35 palabras); hereda geo+era literales de facts | `extract_canonical()` |
| **step_4c_meta** | Meta narrativa (title/hook/mystery/reveal/angle/virality); toda fecha debe existir literal en facts | `extract_meta()` |
| **step_4d_summary** | research_summary (1500-3000 chars), materia prima del guionista; contexto narrativo, no redunda facts | `extract_research_summary()` |
| **step_4e_visual_canon** | Canon visual de 2 CAPAS: era_visual_canon = capa ÉPOCA genérica (7 keys viejas) + capa SUJETO PUNTUAL sourced (materials_textures, color_palette flat-string, scale_dimensions, distinctive_features, demographics, visual_reference_availability, condition_evolution{at_event,later}) que consume el 4º ángulo `visual` (eslabón 1); + documented_people (appearance SIN nombre NI era = guards anti-likeness/anti-C5 deterministas) + anachronism_blocklist. color_palette forzado a string vía response_schema nullable. Lo consumen m03 + m05 | `extract_visual_canon()` |

Bus: 4a→4b→4c→4d ; 4e recibe facts+canonical+angle_blocks (incl. `visual`).

## FASE 1.5 — guión (skeleton→narración→visual→jueces→audio→música)

| módulo | OWNS | entry-point |
|---|---|---|
| **fase1_5** | Orquestador del guión: m01a→m01b→normalizer→audio→m07→m03→m05→m06, con `--from` | `process_topic()` · CLI |
| **m01a_skeleton** `script_engine` | Genera esqueleto fijo de 7 caps (1 call Flash) | `generate_skeleton()` |
| **m01b_narrator** `script_engine` | Narración cap-por-cap (hook/5 dev/outro) en 8 calls Flash | `generate_narration()` |
| **m02_5_normalizer_gate** `script_engine` | Gate humano de pronunciación TTS (detecta spans, CLI V/E/R/S) | `gate_normalizer_for_topic()` |
| **m03_visual** `script_engine` | **Genera image_prompts EN con anchor exacto por imagen** (two-step), dispatch por motor: Flux (prosa+ancla) / Kling (prosa+tail-bake) / **Seedream (eslabón 3b: SKELETON de slots → FLUIDIFICADOR Pro per-item teje prosa por la fórmula del perfil 3a → GUARDA 1 candado de cifras por significado + post-check determinista). Lee el canon 2-capas del eslabón 2; R3 invertida (text_in_image rótulo permitido). Path flux migrado; veo bajo seedream cae a prosa flux-style (no skeleton, flag)** | `assign_visual_prompts()` |
| **m05_judge** `script_engine` | Juez visual híbrido (regex + Flash) anchor↔prompt, voting N=3 | `judge_topic_with_voting()` |
| **m06_classifier** `script_engine` | Post-m05: buckea issues (auto_fixable/grave/FP), genera handoff CC | `classify_and_decide()` |
| **m06_assembler** `script_engine` | Ensambla el **"contrato sagrado"** `data/scripts/<id>.json` (topic+narr+visual) | `assemble_final_script()` |
| **m07_music_director** `script_engine` | Matchea/genera música por cap (ElevenLabs Music + gate) → `music_map.json` | `generate_music_map()` |
| **audio_manager** | **Motor audio+sync**: TTS ElevenLabs + Forced Alignment → `sync_map.json` maestro | `process_script()` · CLI |

## FASE 2A — assets (imágenes + clips)

| módulo | OWNS | entry-point |
|---|---|---|
| **fase2a** | Orquestador 2A: lee contrato → corre audio_manager + asset_manager (no ensambla) | `main()` · CLI |
| **asset_manager** | **Motor ciego de assets**: PNG (Flux.2/Kling o3/Seedream 4.5) + clips Veo 3.1 vía fal.ai → `assets_manifest.json`. El render t2i SYNC es profile-driven (lookup por `engine_profiles.select_profile`) | `process_script()` · CLI |
| **engine_profiles** | **Capa modular de perfiles de motor de imagen** (eslabón 3a): `EngineProfile` (render: model_id/base_url/image_size/cost + mitad-prompt para 3b) + `PERFIL_KLING`/`PERFIL_SEEDREAM` + selector. Hace el motor t2i model-swappable. Kling default → render byte-idéntico; Seedream cargado e inerte hasta 3b | `select_profile()` |
| **error_handler** | Errores centralizados: logging + `@retry` backoff + `PipelineStage` enum | `error_handler` (singleton) |

## FASE 2B — ensamble del video final

| módulo | OWNS | entry-point |
|---|---|---|
| **fase2b** | **Ensamble final**: segmento/cap (Veo loop o slideshow DepthFlow) + subs + transiciones + música → `_final.mp4` | `main()` · CLI |
| **flow_director** `script_engine` | Decide movimiento DepthFlow por escena (1 call Flash batch) + clamp + fallback estático | `select_movements_batch()` |
| **parallax_animator_v2** `script_engine` | **Animador 2.5D**: corre DepthFlow (subprocess a `.venv-depthflow`) o fallback Ken Burns | `build_animated_clip()` |
| **depth_probe** `script_engine` | Pre-filtro geométrico del gate de zoom (mide depth map real, DepthAnythingV2) | `probe_images/gate_zoom` |
| **zoom_judge** `script_engine` | Juez de visión del gate de zoom (Flash vision, solo `sujeto_con_fondo` promueve) | `judge_candidates()` |
| **anchor_timing** | Matcher compartido anchor→tiempo (byte-idéntico entre m03 y fase2b) | `compute_anchor_starts()` |
| **transition_applier** `script_engine` | FFmpeg xfade/acrossfade por posición narrativa, fallback hard-cut | `concat_with_transitions()` |
| **subs_remap** | Remap normalizado→original para subs legibles (difflib, costo 0) | `remap_words_to_original()` |

## FASE 3 — packaging

| módulo | OWNS | entry-point |
|---|---|---|
| **fase3** | Runner fino post-2b: resuelve MP4, abre form m09, marca PACKAGED | `package()` · CLI |
| **m09_packaging** `script_engine` | Metadata YouTube + thumbnail (Flux + Pillow/Anton) + checklist publicación | `compose_and_package()` |
| **m09_review_server** `script_engine` | Form web local de revisión de thumbnails (iterar hero / componer) | `serve()` |

## SERVERS / orquestación

| módulo | OWNS | entry-point |
|---|---|---|
| **run_pipeline** | Secuenciador full por **subprocess**: GUIÓN→ASSETS→[gate]→VIDEO→PACKAGING | `main()` · CLI |
| **qa_studio_server** | QA Studio: visor read-only por cap + botón ENSAMBLAR (spawn fase2b) + fixes | `main()` · HTTP |
| **mixer_server** | Mezcla interactiva: Omar calibra music_volume por cap → re-arma (spawn fase2b) | `main()` · HTTP |
| **qa_form_markers** | Emisor compartido de marcadores `@@QAFORM@@` (form asistido) | `emit_choice_marker()` |

## SHARED — config / helpers / stores

| módulo | OWNS | entry-point |
|---|---|---|
| **gemini_helpers** | **Cliente Gemini Flash/Pro JSON** (retry 503 + parse resiliente). TODO el LLM pasa acá | `call_flash_json/call_pro_json` |
| **name_matching** `script_engine` | Único owner de "qué string es nombre documentado" + scrub determinístico (Kling) | `scrub_documented_names()` |
| **vision_validator** `script_engine` | Guardrail de visión Flux↔prompt antes de pagar Veo. ⚠ **DESACTIVADO** (flag) | `validate_image()` |
| **learned_patterns** `script_engine` | Conocimiento aprendido de m05 (heurísticas root-cause, regex). En memoria, no persiste | `get_root_cause()` |
| **flow_config** | Settings DepthFlow + inventario inmutable de movimientos (guardrail anti-alucinación) | `VALID_MOVEMENTS`, `clamp_*` |
| **flow_profiles** | ⚠ DEPRECATED — único export vivo = `FlowSpec` (TypedDict → acceso `["movement"]`) | `FlowSpec` |
| **audio_config** | Switch maestro de perfil de audio → `AUDIO_STYLE` | `ACTIVE_AUDIO_PROFILE` |
| **audio_profiles** | Presets de voz ElevenLabs + mixing/duck + music_prompt | `AUDIO_PROFILES` |
| **music_config** | Config m07: endpoint ElevenLabs Music + 7 prompts por intent | `build_music_prompt()` |
| **nicho_config** | Identidad visual permanente por nicho (hardcoded dark_history), leído por m03 | `get_active_nicho()` |
| **transition_config** | Settings render + inventario inmutable de transiciones (guardrail) | `is_valid/clamp_duration_ms` |
| **transition_profiles** | Reglas duras de transición por art_profile (whitelist/blacklist) | `get_rules()` |
| **tts_normalizer** | Normalizador TTS mínimo (acrónimos/abreviaturas) + custom dict | `normalize_for_tts()` |
| **topics_db** `script_engine` | **Store central de estado de topics** — el hub del handoff por archivo | `load_db/save_db/mark_as_*` |
| **transcript_fetch** `script_engine` | Fetcher de transcripts YouTube (reusa proxy de prod) | `fetch_transcript()` |
| **youtube_scanner** `script_engine` | Scanning YouTube (scrapetube→API v3): competition, viral-EN, saturación ES | `scan_competition/...` |

---

## PRODUCTOR → CONSUMIDOR  *(las aristas que el `import` NO ve — leé el productor antes del consumidor)*

### Subprocess (un proceso spawnea otro)
```
run_pipeline ──python faseX.py──► fase1 / fase1_5 / fase2a / fase2b / fase3
qa_studio_server ──Popen fase2b.py──► fase2b          (botón ENSAMBLAR)
qa_studio_server ──Popen run_pipeline──► pipeline full (botón FORM, QA_FORM=1)
mixer_server ──Popen fase2b.py──► fase2b               (botón RE-ARMAR)
fase3 ──python -m m09_packaging──► m09_packaging        (solo --headless)
parallax_animator_v2 / depth_probe ──.venv-depthflow──► DepthFlow / DepthAnythingV2 (CUDA)
```

### Bus de archivos (productor escribe → consumidor lee, SIN import entre ellos)
```
HUB SEEDS    niche_discoverer ─selected_seeds.json─► fase1, topic_researcher, m_judge_seeds
HUB TOPICS   topic_researcher ─topics_db.json─► validator, csv, fase2a/2b/3 (vía topics_db)
             topic_validator  ─fase1_review.csv (csv_exporter)─► fase1_5, fase2a

GUIÓN        m01a ─01a_skeleton.json─► m01b, m05, m06
             m01b ─01b_narration.json─► normalizer, audio_manager, m06
             normalizer ─01b_narration_normalized.json─► audio_manager (TTS)
             m03_visual ─03_visual.json─► m05, m06   ◄─ m06 MUTA este archivo (write-back loop)
             m06_assembler ─data/scripts/<id>.json ("contrato sagrado")─► fase2a, fase2b, m09

AUDIO        audio_manager ─sync_map.json─► m07, fase2a, asset_manager, fase2b, mixer, qa_studio
             audio_manager ─chXX_timestamps.json─► m03 (anchor merge), fase2b
             m07 ─music_map.json─► fase2b, mixer_server

VIDEO        asset_manager ─assets_manifest.json─► fase2b
             fase2b ─flow_specs.json / depth_metrics.json / zoom_verdicts.json─► (cache propio)
             fase2b ─<id>_final.mp4─► fase3 / m09
             fase2b ─topics_db status=video_generated─► fase3 / run_pipeline (gate)

FORM         qa_form_markers ─stdout @@QAFORM@@─► qa_studio_server._form_reader (stdin reply)
```

---

## ⚠ MUERTO / BASURA / DEUDA  *(candidatos de limpieza — gate Omar, NO tocar sin decisión)*

**BASURA confirmada (borrable):**
- `script_engine/m03_visual copy0507.py` — copia versionada, NADIE la referencia. Candidato a borrado.

**BUG latente (nuevo hallazgo):**
- `seeds_archive.json` con **DOS schemas divergentes**: `topic_researcher` escribe `{"archived":[...]}`, `fase1` escribe `{"seeds":[...]}` — mismo archivo, shapes distintos → revienta si se relee cruzado.

**Deuda silenciosa (mirror manual):**
- `mixer_server._build_mix_filter` es copia MANUAL de `fase2b._mix_music_into_video` — si cambian params de mixing en fase2b, queda stale sin aviso.

**Código muerto / no-op en módulos vivos:**
- `fase1`: `_save_script`, `load_db/check_pending_promises` stubs, `run_latido_b` deprecado
- `niche_discoverer`: `_gemini_generate_queries` + `dynamic_queries_cache.json` (DEPRECATED chat42)
- `m03_visual`: `_build_veo_prompt/_build_flux_prompt` (rollback), `_stitch_zone2_*` (no-op chat19)
- `m06_assembler`: `_mode_art_profile()` no-op chat19 · `audio_manager`: path Whisper completo (reemplazado por ElevenLabs)
- `flow_profiles`: cuerpo deprecado (solo `FlowSpec` vivo) · `cost_tracker`: `track_leonardo()`
- dead imports: `fase1_5` (parse_decisions_csv), `m02_5` (normalize_for_tts), `m07` (MusicConfigError)

**Stale engañoso (texto que miente):**
- `asset_manager`: `ENABLE_VISION_VALIDATOR=False` pero manifest loguea "Vision Guardrail ACTIVO" + engine "Flux 1.1 Pro" (corre Flux.2+Kling)
- docstrings con path viejo `modules/`: `topics_db`, `youtube_scanner`, `transition_applier`

**Provider (factual):** TODO el LLM del pipeline es **Google Gemini**. Ningún módulo de prod usa Anthropic/Claude.

---

## DOCTRINA — dónde leer el detalle (este mapa INDEXA, no reemplaza)

- **ARCHITECTURE.md** — diseño de fases, contratos, §6.7 (m04 ausente), §6 deuda mixer.
- **MODEL_PROMPTING_RULES.md** — reglas Kling/Veo/Flux/Gemini. **Leer ANTES de tocar cualquier prompt.**
- Cadena de prompts visual: `m03_visual` (genera) → `m05_judge` (audita) → `m06_classifier` (buckea).
- Cinematografía: `flow_director` (decide) → `parallax_animator_v2` (renderiza). `FlowSpec` es TypedDict.
- DepthFlow corre en `.venv-depthflow` (CUDA) — perfil GPU per-máquina (doc `DEPTHFLOW_GPU_SETUP.md` pendiente, B-depth-gpu-guard).
