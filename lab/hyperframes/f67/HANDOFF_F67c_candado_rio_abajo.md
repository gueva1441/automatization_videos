# HANDOFF F67c — Candado río abajo: nada después del papel se reusa si no viene del papel aprobado vigente

Modelo → CC: Opus medium. Decisión: orden de la ENTRADA 31g §1.1 + DECISIONES 2026-10-31 22:13. Sin prompts nuevos. Subagentes en paralelo donde convenga. Sin topes en dólares. **No se corre voz, fotos, fondos ni render en esta tanda.** Auditado por subagente (correcciones incorporadas).

## 0. Orden re-derivado
- ¿Construye sobre algo que ya decidimos reemplazar? No: completa el candado de F67/F67b (narración → papel) hacia abajo. Lección F67b: toda excepción al candado es un camino río abajo sin md5.
- ¿Cambia el orden? Sí, va **antes** de que Omar apruebe el papel de Wittenoom: hoy `etapa_de` mira solo existencia de `data/scripts/<id>.json` (28-oct 04:13), `assets_manifest.json` (28-oct 04:34) y `<id>_final.mp4`/visuales base (28-oct 05:28) → tras aprobar el papel saltaría assets y fondos y armaría el video con fotos de una narración vieja. (Wittenoom tiene `status=video_generated` en topics_db; no afecta a `etapa_de` porque el papel existe, run_pipeline.py:191.)

## 1. Constantes y alcance
| valor | origen | quién |
|---|---|---|
| sello = `papel.aprobado.md5` del papel aprobado **y** vigente: `estado_papel` ok **y** `papel_falta is None` (`estado_papel` no compara `narracion_md5`, fase1_5.py:352-364) | F67b | analista |
| desfasado = artefacto sin sello o con sello ≠ el vigente | ENTRADA 31g §1.1 | analista (Omar aprobó el orden) |
| **fuera del candado (reusos legítimos, no tocar):** audio por cap — `audio_manager.process_script` ya invalida por `text_hash`/`tts_hash` (audio_manager.py:614-645); negarlo por sello re-pagaría ElevenLabs si cambia solo el papel. Foto madre — depende del canon de la ficha (`canon_ficha_md5`), no del papel | código actual | analista |
| render: regla actual (más viejo que `GUION_PANTALLA.json` ⇒ render) | `etapa_de` hoy | — |

Sin números nuevos.

## 2. Módulos tocados (hoy → después)
| archivo | hoy | después |
|---|---|---|
| `script_engine/m06_assembler.py` (`assemble_final_script` → `data/scripts/<id>.json`) | sin sello | escribe `papel_md5` (sello vigente §1) y verifica que `01b_narration.json` (lo que lee la voz, fase1_5.py:179) viene de la `01b_narracion_v3` aprobada (mismo md5 de narración); si no hay papel aprobado vigente → error, no escribe. Otros llamadores (`m06_classifier.py:623/640/675/721`, `test_m06_autopass.py`, `test_module_f60_bc.py:353`): se les da un fixture de papel aprobado; no se les abre excepción |
| `asset_manager.py` (`manifest`, imágenes, supps, clips) | reusa por existencia: `needs = not out_path.exists()` (:1134), «supp ya existe — skip» (:1376), «Clip ya existe — skip» (:1464) | copia `papel_md5` del script al manifest; cada uno de esos reusos solo vale si el manifest en disco tiene el **mismo** sello; si no, regenera. (`fase2a._should_skip`/`SKIP_STATUSES` no corre con `--topic`, fase2a.py:446-449: no se toca) |
| `fase2b.py` (fondos, `--plan-only`, `GUION_PANTALLA.json`) | `--plan-only` fuerza `reuse_visuals=True` (:3744-3746) y reusa `chNN_flux_visual.mp4`/`_hybrid_visual.mp4` por existencia (:1051, :1126, `_visual_base_existente` :2869); `assets/flow_specs.json` se reusa sin sello (:2299-2348) | sidecar `output/<id>/_fase2b_work/fondos.json` {`papel_md5`} al terminar los fondos; visuales base y `flow_specs.json` solo se reusan con el mismo sello; `GUION_PANTALLA.json` lleva `papel_md5`. (`flow_plan.json` es solo inspección, :3314: no se toca) |
| `run_pipeline.py` (`etapa_de`) | assets/fondos/guion_pantalla por existencia; fondos se da por hecho sin `_final.mp4` si existen los visuales base (:214-217) | cada etapa: falta **o desfasada** (manifest, `fondos.json`, `GUION_PANTALLA.json`) ⇒ esa etapa, con motivo «sin sello» / «sello X de otro papel». Un desfase arriba arrastra lo de abajo. `voz` sigue por existencia del script **más** su sello (el script sin sello ⇒ `voz`; el audio se reusa solo por su hash) |

Son 4 módulos. Las rutas de QA Studio que reescriben el script/manifest (qa_studio_server.py:1142, :1296, read-modify-write) conservan claves desconocidas: confirmado por el auditor; CC lo cubre con un test.

## 3. Etapas (cada una termina con su salida en texto)
A. **Inventario sin cambiar comportamiento**: confirmar la lista de reusos de §2 y buscar los que falten (música, `flow_specs`, cachés). Salida: tabla `paso · archivo/condición · línea · ¿reusaría lo del 28-oct de Wittenoom? · ¿entra al candado?`. Si aparece un reuso que obligaría a tocar un 5.º módulo, **PARADA** y reportar (no se agrega solo).
B. **Sellos** (§2). Tests **solo** con `DATA_DIR`/`OUTPUT_DIR`/`STEPS_DIR`/topics_db monkeypatcheados a un dir temporal (nada en `data/` ni `output/` reales): papel aprobado P1 → artefactos sellados P1 → se aprueba P2 → `etapa_de` = `voz` y cada reuso de la tabla A se niega; audio con mismo texto se reusa igual (no se re-paga).
C. **`etapa_de`** en cascada. Salida: `python -c` con `etapa_de` de Wittenoom **hoy** (→ `papel`) y simulando el papel aprobado (monkeypatch de `estado_papel`) → `voz`, motivo «data/scripts/<id>.json sin sello».
D. Las comprobaciones por existencia que se reemplazan se borran con sus tests (se actualizan, no se duplican).
E. Reporte `lab/hyperframes/f67/F67c_REPORT.md` (tabla A, salidas, diff, tests, veredicto íntegro del subagente revisor — en este repo `.claude/agents/` tiene `simulador` y `structure-auditor`; si no hay `revisor-handoff`, usar `structure-auditor` y decirlo), ESTADO_SESION cabecera, commit en `f11-guion-v4` (incluye las líneas de DECISIONES.md del 31-oct 21:52–noche). Copia de este handoff con md5.

## 4. PARADA
Sigue F67d en la misma corrida (salvo PARADA de la Etapa A). No se corre producción.
