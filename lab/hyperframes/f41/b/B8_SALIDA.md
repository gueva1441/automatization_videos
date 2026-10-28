# F41 B.8 — Salida en texto de la Parte B

Rama `f11-guion-v4` · 2026-10-27 · US$ 0 (nada real corrió: la tabla es solo lectura; los recorridos usan las fases falsas de `test_run_pipeline.FakePipeline` en un directorio temporal, sin subprocess, sin API, sin escribir en `data/` ni `output/`).

## 1. La tabla `etapa_de` para cada topic de `data/topics_db.json`

Script: `lab/hyperframes/f41/b/tabla_etapas.py` (solo lectura). Comando: `PYTHONIOENCODING=utf-8 python lab/hyperframes/f41/b/tabla_etapas.py`.

| topic | status (topics_db) | etapa_de | qué correría `run_pipeline --topic X` | por qué |
|---|---|---|---|---|
| `ba6c3cac-a091-41c0-8dad-afd2f4364747` | video_generated | **cadena_vieja** | nada (PARADA: topic de la cadena borrada) | sin papel pero con ba6c3cac-a091-41c0-8dad-afd2f4364747.json, assets_manifest.json, ba6c3cac-a091-41c0-8dad-afd2f4364747_final.mp4, ba6c3cac-a091-41c0-8dad-afd2f4364747_final_gfx.mp4, status video_generated en topics_db: topic de la cadena borrada (DECISIONES 2026-10-27 20:59); no se retoma para no volver a pagar lo hecho |
| `eca6d3e2-fc1d-4341-82de-07c6d159e801` | video_generated | **cadena_vieja** | nada (PARADA: topic de la cadena borrada) | sin papel pero con eca6d3e2-fc1d-4341-82de-07c6d159e801.json, assets_manifest.json, eca6d3e2-fc1d-4341-82de-07c6d159e801_final.mp4, status video_generated en topics_db: topic de la cadena borrada (DECISIONES 2026-10-27 20:59); no se retoma para no volver a pagar lo hecho |
| `92146ab7-6c85-4bbc-b813-d7e31afc9876` | video_generated | **cadena_vieja** | nada (PARADA: topic de la cadena borrada) | sin papel pero con 92146ab7-6c85-4bbc-b813-d7e31afc9876.json, assets_manifest.json, 92146ab7-6c85-4bbc-b813-d7e31afc9876_final.mp4, status video_generated en topics_db: topic de la cadena borrada (DECISIONES 2026-10-27 20:59); no se retoma para no volver a pagar lo hecho |
| `ba6c3cac-f5v2` | video_generated | **cadena_vieja** | nada (PARADA: topic de la cadena borrada) | sin papel pero con ba6c3cac-f5v2.json, assets_manifest.json, ba6c3cac-f5v2_final_gfx.mp4, status video_generated en topics_db: topic de la cadena borrada (DECISIONES 2026-10-27 20:59); no se retoma para no volver a pagar lo hecho |
| `ba6c3cac-f7r3` | video_generated | **cadena_vieja** | nada (PARADA: topic de la cadena borrada) | sin papel pero con status video_generated en topics_db: topic de la cadena borrada (DECISIONES 2026-10-27 20:59); no se retoma para no volver a pagar lo hecho |
| `f8s1-ycua-bolanos` | researched | **guion** | fase1_5 --topic X --batch | no hay papel (C:\CLAUDE_PROJECTS\automatization_videos\data\scripts\_steps\f8s1-ycua-bolanos\01e_pantalla.json): m01e no dejó guion de pantalla, no hay nada que aprobar |
| `f18-kyshtym-mayak` | researched | **guion** | fase1_5 --topic X --batch | no hay papel (C:\CLAUDE_PROJECTS\automatization_videos\data\scripts\_steps\f18-kyshtym-mayak\01e_pantalla.json): m01e no dejó guion de pantalla, no hay nada que aprobar |
| `f8s3-vajont` | video_generated | **papel** | compuerta del papel (A/P) | el papel no está aprobado |
| `f39-kyshtym` | researched | **voz** | fase1_5 --topic X --from normalizer_gate --batch | papel aprobado por Omar (2026-10-27), md5 7db98e46…; falta C:/CLAUDE_PROJECTS/automatization_videos/data/scripts/f39-kyshtym.json |

Nota (hipótesis, solo lectura): si Omar aprobara el papel de `f8s3-vajont`, `etapa_de` daría **guion_pantalla** (tiene script, manifest y los 7 visuales base cocidos en `_fase2b_work`; no tiene `GUION_PANTALLA.json` en `output/f8s3-vajont/`): no volvería a pagar voz, imágenes ni fondos.

## 2. Recorridos en seco del form

Script: `lab/hyperframes/f41/b/recorrido_form.py`. Corre `run_pipeline.main()` en proceso con QA_FORM prendido y lee su salida como la lee `qa_studio_server._form_reader` (header → fase del form; `@@QAFORM@@` → marcador). fase1 es un stub: sus propios marcadores (reuse_seeds, seed_pick, video_type) salen de su subprocess y acá no aparecen. Los documentos de las compuertas son los del stub (unas líneas); en la corrida real el marcador lleva el `01e_pantalla.md` / `GUION_PANTALLA.md` entero en `body`.


(Regenerado por CC después de cablear la medida de RAM antes del render, DECISIONES 2026-10-27 00:30: el recorrido usa un stub de RAM suficiente; con la RAM real de hoy, 13,3 GB < 14, el render pararía antes de correr.)

### Recorrido 1 — research → fase3, A en el papel, C en el visor, A en el guion de pantalla

argv: `run_pipeline.py --research --video-type long --batch` · respuestas del form por stdin: ['A', 'C', 'A']

```
  FASE RESEARCH   ← «▶ RESEARCH (fase1)»
    subprocess (stub): python fase1.py --no-chain --video-type long
  FASE GUION   ← «▶ GUION (fase1_5) — top_f41»
    subprocess (stub): python fase1_5.py --topic top_f41 --batch
  FASE PAPEL   ← «▶ PAPEL (compuerta del papel) — top_f41»
  MARCADOR papel_gate · botones ['A', 'P'] · documento 70 caracteres (1.ª línea: '# Papel de top_f41')
    form → stdin: 'A'
    subprocess (stub): python fase1_5.py --topic top_f41 --aprobar-papel "Omar 2026-10-27"
  FASE VOZ   ← «▶ VOZ (fase1_5 --from normalizer_gate) — top_f41»
    subprocess (stub): python fase1_5.py --topic top_f41 --from normalizer_gate --batch
  FASE ASSETS   ← «▶ ASSETS (fase2a) — top_f41»
    subprocess (stub): python fase2a.py --topic top_f41
  FASE FONDOS   ← «▶ FONDOS (fase2b sin gfx) — top_f41»
  MARCADOR visor_gate · botones ['C'] · documento 0 caracteres (1.ª línea: '—')
    form → stdin: 'C'
    subprocess (stub): python fase2b.py top_f41
  FASE PANTALLA   ← «▶ PANTALLA (fase2b --plan-only) — top_f41»
    subprocess (stub): python fase2b.py top_f41 --plan-only
  FASE PANTALLA   ← «▶ PANTALLA (compuerta del guion de pantalla) — top_f41»
  MARCADOR guion_gate · botones ['A', 'P'] · documento 68 caracteres (1.ª línea: '# GUION DE PANTALLA — top_f41')
    form → stdin: 'A'
    subprocess (stub): python fase2b.py top_f41 --aprobar-guion "Omar 2026-10-27"
  FASE RENDER   ← «▶ RENDER (fase2b --gfx --gfx-sparse) — top_f41»
    subprocess (stub): python fase2b.py top_f41 --reuse-visuals --keep-segments --gfx --gfx-sparse
    reporte: ✅ Cadena completa.
    reporte: 📦 LISTO PARA PACKAGING → python fase3.py top_f41
  exit code de run_pipeline: 0
```

Comandos corridos (stub) en esta corrida: ['research', 'guion', 'aprobar-papel', 'voz', 'assets', 'fondos', 'plan-only', 'aprobar-guion', 'render']

### Recorrido 2a — research → P en la compuerta del papel

argv: `run_pipeline.py --research --video-type long --batch` · respuestas del form por stdin: ['P']

```
  FASE RESEARCH   ← «▶ RESEARCH (fase1)»
    subprocess (stub): python fase1.py --no-chain --video-type long
  FASE GUION   ← «▶ GUION (fase1_5) — top_f41»
    subprocess (stub): python fase1_5.py --topic top_f41 --batch
  FASE PAPEL   ← «▶ PAPEL (compuerta del papel) — top_f41»
  MARCADOR papel_gate · botones ['A', 'P'] · documento 70 caracteres (1.ª línea: '# Papel de top_f41')
    form → stdin: 'P'
    reporte: ⛔ Frenó en: PAPEL
    reporte: ➡  Próximos comandos:
    reporte: leer:    C:/Users/Canada/AppData/Local/Temp/f41b_recorrido_2ztyk23x/dos/data/scripts/_steps/top_f41/01e_pantalla.md
    reporte: aprobar: python fase1_5.py --topic top_f41 --aprobar-papel "Omar <fecha>"
    reporte: retomar: python run_pipeline.py --topic top_f41
  exit code de run_pipeline: 0
```

Comandos corridos (stub) en esta corrida: ['research', 'guion']

etapa_de(top_f41) después de la P: ('papel', 'el papel no está aprobado')

### Recorrido 2b — «Retomar» (/form_resume) → A en el papel, C en el visor, A en el guion

argv: `run_pipeline.py --topic top_f41 --batch` · respuestas del form por stdin: ['A', 'C', 'A']

```
  FASE PAPEL   ← «▶ PAPEL (compuerta del papel) — top_f41»
  MARCADOR papel_gate · botones ['A', 'P'] · documento 70 caracteres (1.ª línea: '# Papel de top_f41')
    form → stdin: 'A'
    subprocess (stub): python fase1_5.py --topic top_f41 --aprobar-papel "Omar 2026-10-27"
  FASE VOZ   ← «▶ VOZ (fase1_5 --from normalizer_gate) — top_f41»
    subprocess (stub): python fase1_5.py --topic top_f41 --from normalizer_gate --batch
  FASE ASSETS   ← «▶ ASSETS (fase2a) — top_f41»
    subprocess (stub): python fase2a.py --topic top_f41
  FASE FONDOS   ← «▶ FONDOS (fase2b sin gfx) — top_f41»
  MARCADOR visor_gate · botones ['C'] · documento 0 caracteres (1.ª línea: '—')
    form → stdin: 'C'
    subprocess (stub): python fase2b.py top_f41
  FASE PANTALLA   ← «▶ PANTALLA (fase2b --plan-only) — top_f41»
    subprocess (stub): python fase2b.py top_f41 --plan-only
  FASE PANTALLA   ← «▶ PANTALLA (compuerta del guion de pantalla) — top_f41»
  MARCADOR guion_gate · botones ['A', 'P'] · documento 68 caracteres (1.ª línea: '# GUION DE PANTALLA — top_f41')
    form → stdin: 'A'
    subprocess (stub): python fase2b.py top_f41 --aprobar-guion "Omar 2026-10-27"
  FASE RENDER   ← «▶ RENDER (fase2b --gfx --gfx-sparse) — top_f41»
    subprocess (stub): python fase2b.py top_f41 --reuse-visuals --keep-segments --gfx --gfx-sparse
    reporte: ✅ Cadena completa.
    reporte: 📦 LISTO PARA PACKAGING → python fase3.py top_f41
  exit code de run_pipeline: 0
```

Comandos corridos (stub) en esta corrida: ['aprobar-papel', 'voz', 'assets', 'fondos', 'plan-only', 'aprobar-guion', 'render']

etapa_de(top_f41) al final: ('packaging', 'top_f41_final_gfx.mp4 listo; falta empaquetar (fase3)')

¿Se corrió dos veces alguna fase? False
