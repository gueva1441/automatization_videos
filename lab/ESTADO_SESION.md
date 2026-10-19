# ESTADO_SESION — dónde estamos (leer ANTES de programar)

Última actualización: 2026-10-19 · CC lo actualiza en cada hito (commit, reporte, decisión de Omar).

## Proyecto activo
- Repo: `C:\CLAUDE_PROJECTS\automatization_videos` · rama **`f3-lab-identidad`** (desde `31c671c`, tip de `f2-gfx-director`) · `main` = `43f528a` (NO tocar sin OK explícito de Omar).
- **Decisión de Omar (2026-10-19): F2b NO se mergea a `main` todavía**; queda en `f2-gfx-director` @ `31c671c`.
- Fase: **F3 Laboratorio de identidad** (`lab/hyperframes/f3/HANDOFF_F3_laboratorio_identidad.md`). F0–F2b cerrados.
- Video de prueba: Orleans `ba6c3cac-a091-41c0-8dad-afd2f4364747` (7 caps; ch02 es el cap de calibración, ch05 el segundo).

## Trabajo activo: F3 (lab interactivo en http://localhost:8765)
- Orden §5.2: A → B → C → **PARADA ÚNICA** (Omar abre el lab, juega 30 min, guarda) → D → E.
- Arranque 2026-10-19: rama creada, handoff copiado a `lab/hyperframes/f3/`.
- §A (servidor + historia + preview): `gfx_lab_server.py` + `lab/identidad/{index.html,lab.js,lab.css}`. Preview = `write_project` (plantillas reales) + runtime/player pineados. md5 sin gfx = 38e5ba14 ✔. Decisiones C1–C11 en `lab/hyperframes/f3/DECISIONES_F3.md`.
- Levantar el lab: `PYTHONIOENCODING=utf-8 python gfx_lab_server.py` (→ http://localhost:8765). Proyecto del preview: `_fase2b_work/gfx_lab_ch02/` (nunca el `gfx_ch02/` del render).
- Commits F3: `feat(gfx-f3-lab): <sección>`; revisor-handoff antes de cada uno; veredictos íntegros en `lab/hyperframes/f3/F3_REPORT.md`.

## Historia: F2b (HANDOFF_F2b_director_v2.md, modo autónomo) — cerrado, en rama f2-gfx-director
- Omar respondió las 3 preguntas del nocturno con el handoff F2b: titular determinista (sí), tocar el concat (sí, §4), visión de retratos filtrada (sí).
- Orden: §1 → §2 → render ch02 looks → **PARADA 1** (página de revisión ch02) → §3 → **PARADA 2** (tira_iconos_12.jpg) → §4 → render completo → AB → F2b_REPORT.md.
- Hecho: §1 `aec3a4a` (revisor: CUMPLE CON OBSERVACIONES). md5 sin gfx ch02 = 38e5ba14 ✔.
- Hecho: §2 `046c4c9` (revisor: CUMPLE CON OBSERVACIONES). ch02 looks: 2 recortes, 3 énfasis, 0 huecos > 18 s.
- PARADA 1 cerrada: Omar dio OK a ch02 con dos cambios → commit `2879665` (oscuridad sin parpadeos = token `mood_dark_flicker`; léxico con peso 1–3, orden peso → rareza).
- PARADA 2 cerrada: Omar eligió 1b 2a 3a 4a 5b 6a 7a 8b 9b 10b 11b 12a; rojo solo en ojos de calavera, cerradura y clavo de la cruz → commit §3 `f3fd3db`.
- §4 commiteado `6819ee5` (revisor: CUMPLE CON OBSERVACIONES; el PSNR ≥ 50 dB contra el final viejo NO se cumple a la letra: 44.8 Y, porque el viejo pierde contra la fuente → criterio luma, Omar decide).
- Render completo HECHO: 37.9 min (+19.3 vs A ✔), concat+música 85 s ✔, incremental 7.5 min (✘ ≤ 6), 5 recortes, densidad 8.9 s. Entregables: `output/…/…_final_gfx.mp4`, `AB_…_f2b.mp4`, `lab/hyperframes/f2b/F2b_REPORT.md` (+ corrida_final/). Fix ch05 (B35) re-ensamblado.
- Revisor final: CUMPLE CON OBSERVACIONES (corregido el conteo de recortes; md5 sin gfx re-verificado 38e5ba14). Commit de cierre hecho.

## Esperando a Omar
- Pre-merge commiteado `11a9d1f` (íconos por palabra + mapa de muerte de Omar, press_wipe + hold vivo, recortes). Render completo nuevo (38.3 min, 10 recortes en 7 caps) + AB nuevo. Productos v1 en `_fase2b_work/_bak_f2b_v1_antes_premerge/`.
- Pre-merge v2 + re-ensamble de 6 caps con "un fact = un bloque" HECHO (`31c671c`): «6,500» como contador 4 → 1, 0 violaciones, AB nuevo 100 % regla nueva. **Esperando a Omar** (mirar AB; merge a main solo con su OK). Deuda: recortes repetidos entre caps.
- Ver AB_…_f2b.mp4 y el final; decidir el criterio de PSNR de §4 (B33). Merge F1+F2+F2b a `main` solo con OK explícito.
- Medición §4 en segmentos F2: concat 62 s (antes ~15 min), mismos frames; nuevo más fiel a la fuente que el viejo (Y 58.6 vs 47.3).
- Gemini F2b: 30 llamadas (< $0.05). fal (íconos): 36 × Flux.2 Pro ≈ $1.08.
- OJO render completo (§4): `--reuse-visuals` reusa los `chXX_gfx.mp4` viejos → moverlos a `_fase2b_work/_bak_*` antes (ch02 ya en `_bak_f2_pre_f2b/`).
- Gemini F2b hasta ahora: 30 llamadas (< $0.05).
- Docs: `lab/hyperframes/f2b/` → `F2b_REPORT.md` (veredictos íntegros), `DECISIONES_F2b.md`.
- Tope Gemini F2b: $2. Merge a `main`: solo con OK explícito.

## Reglas que no se negocian
- Responder en español (rioplatense). Comentarios en español, identificadores en inglés.
- Todo reporte a Omar pasa antes por `revisor-handoff` (subagente, sonnet) y su veredicto va **íntegro**.
- Candado literal en todo texto en pantalla. Sin `--gfx`, fase2b byte-idéntico (chequeo: md5 de ch02 `--only-cap` = `38e5ba14…`).
- Sin shaders, sin rembg/inpaint. Validar con `--only-cap ch02` + snapshots; renders completos solo cuando se piden.
- Commits: `feat(gfx-f2): <sección>`, trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`, `git add` selectivo (`diag_234_cap4.py` NO es nuestro).
- Python con `PYTHONIOENCODING=utf-8`. Los heredocs largos de bash fallan: escribir los scripts con Write en el scratchpad.

## Dónde está todo
- Handoffs: `lab/hyperframes/_handoff_adjuntos/` (F2 director/boosters, nocturno, DOC_MAESTRO).
- Reportes F2: `lab/hyperframes/f2/` → `F2_REPORT.md` (veredictos), `DECISIONES_F2_nocturno.md` (34 decisiones), `RESUMEN_NOCHE.md`, tiras `.jpg`, `corrida_final/`.
- Código gfx: `gfx_config.py` (motor), `gfx_profiles/*.json` (perfil), `script_engine/gfx_*.py`, `script_engine/gfx_templates/`, `script_engine/sfx/`.
- Salidas: `output/ba6c3cac…/` → `_final.mp4` (A, sin gfx), `_final_gfx.mp4` (B-F2 oficial), `AB_…_f2.mp4`; respaldos en `_fase2b_work/_bak_*`.
- Transcripciones respaldadas antes de cada compactación: `lab/_transcripts/` (hook PreCompact).

## Comandos de uso diario
- Tests gfx: `PYTHONIOENCODING=utf-8 python -m pytest test_module_gfx_*.py test_module_fase2b_reassemble.py test_module_fase2b_hwencode.py -q`
- Un cap: `python fase2b.py <id> --reuse-visuals --gfx --gfx-quality looks --only-cap ch02` (+ `--gfx-debug` para el overlay).
- Video completo: `python fase2b.py <id> --reuse-visuals --keep-segments --gfx --gfx-sparse`.
