# HANDOFF F70b — 3 fotos del lab F70 a producción

## Por qué (Omar, 2026-11-01 15:04)
Las fotos del lab F70 ch03_img_08, ch03_img_15 y ch06_img_07 salieron mejor que las de producción (F68). Omar dijo sí a pasarlas. Topic Wittenoom `123bbb64-9fca-4395-8bf4-57d60e219ef1`.

## Constantes
| Valor | Origen | Quién |
|---|---|---|
| Lista de 3 fotos | Omar 2026-11-01 15:04 | Omar |
| 2560×1440 / nativo 1376×768 | DECISIONES 2026-11-01 F68 (tamaño) | analista F68 |
Ninguna otra. Costo esperado: US$ 0 (sin llamadas).

## Módulos
- Nuevo `lab/hyperframes/f70/promover.py` (descartable de lab): copia, grade, manifest, invalidación.
- Reusa sin tocar `qa_studio_server._grade_como_produccion` (grade = el de producción).
- No toca `script_engine/`, `qa_studio_server.py` (F69), `asset_manager.py`, `03_visual.json` ni el guion vivo: los casilleros no cambiaron; el cambio F70 es de armado y su arreglo general va antes del tema 2.

## Etapa 1 — promover.py (por foto F, cap C, D = output/<topic>/assets/<C>_flux/)
1. Backup a `assets/_qa_backups/<nombre>.<ts>.bak<sufijo>` (molde `_backup`): D/F.png, F_graded.png, F_native.png, F.llamada.json; `assets_manifest.json` una vez.
2. Copiar del lab: F.png → D/F.png, F_native.png → D/F_native.png, F.llamada.json → D/F.llamada.json.
3. `_grade_como_produccion(D/F.png)` → D/F_graded.png. Si devuelve None → PARADA.
4. Manifest, entrada de F (por `path_original`): `prompt` = texto de la llamada del lab; `motor`, `usd`, `segundos`, `respaldo_motivo` y `flux_meta.{endpoint,motor,usd,segundos,respaldo_motivo}` desde la llamada del lab cuando existan. Nada más cambia (ni `papel_md5`, ni `seed_used`, ni otras entradas). Mismo indent/encoding que producción.
5. Invalidar horneado de ch03 y ch06: borrar `_fase2b_work/<cap>_flux_visual.mp4` y `<cap>_hybrid_visual.mp4` (como `_invalidate_baked`).

## Etapa 2 — verificación (texto en el reporte)
- Tabla por foto: md5 antes → después de .png/_native/_graded; md5 producción == md5 lab; tamaños 2560×1440 y 1376×768.
- Manifest: diff de las 3 entradas; resto idéntico (comparar los JSON sin esas 3).
- `papel_md5` y `etapa_de` del topic iguales antes/después (imprimir).
- Hoja vieja|nueva del _graded de las 3: `lab/hyperframes/f70/promovidas_hoja.jpg`.

## Reglas fijas
Cero llamadas a fal/Opus/Gemini; backup antes de pisar; solo se borran los mp4 horneados; no correr fase2b ni run_pipeline; DECISIONES.md: agregar la línea de Omar 15:04. Commit: promover.py, reporte, DECISIONES (png fuera, .gitignore). Revisor-handoff íntegro en el reporte. Una línea en ESTADO_SESION. PARADA: `lab/hyperframes/f70/F70b_REPORT.md`.
