# F67c_REPORT — candado río abajo

Handoff `HANDOFF_F67c_candado_rio_abajo.md`, md5 `e3855fb45d6610ec1e74129db74e6f0f` (la copia es ese mismo archivo) · rama `f11-guion-v4` · base `25ac783` · CC Opus 5.5 medium. **0 llamadas a la API: US$ 0.** No corrió voz, fotos, fondos, guion de pantalla, render, `--papel`, `--criticar` ni `--aprobar-papel`. La narración y el papel de Wittenoom no se tocaron.

## A. Inventario

**Ningún reuso obliga a tocar un 5.º módulo, así que no hubo PARADA:** los módulos tocados son los 4 del §2. Los reusos de otros módulos (gfx_layer, depth_probe, zoom_judge, gfx_critic, image_grade) se niegan desde asset_manager y fase2b moviendo sus archivos. Lo único fuera de los 4 que queda vivo es el empaquetado (abierto 1), que no se tocó porque descartarlo es decisión de Omar.

| paso | archivo / condición | línea | ¿reusaría lo del 28-oct de Wittenoom? | ¿entra al candado? |
|---|---|---|---|---|
| guion → voz | `etapa_de`: existe `data/scripts/<id>.json` | run_pipeline.py (antes :210) | sí: saltaba la voz | **sí**: sello en el script |
| assets | `etapa_de`: existe el manifest | run_pipeline.py (antes :212) | sí | **sí**: sello en el manifest |
| fondos | `etapa_de`: existe `_final.mp4` o los visuales base | run_pipeline.py (antes :214-217) | sí | **sí**: `fondos.json` |
| guion de pantalla | `etapa_de`: existe `GUION_PANTALLA.json` | run_pipeline.py (antes :219) | hoy no existe en Wittenoom; en un tema 2, sí | **sí** |
| imagen | `needs = not out_path.exists()` | asset_manager.py:1134 | sí | **sí** |
| pre-paso de secuencia | `it["path"].exists()` | asset_manager.py:1046 | sí | **sí** (no estaba en el §2) |
| supp | «supp ya existe — skip» | asset_manager.py:1376 | sí | **sí** |
| clip | «Clip ya existe — skip» | asset_manager.py:1464 | sí | **sí** |
| clip con fallback | `fallback_img_path.exists()` | asset_manager.py:1476, :1310, :1313 | sí | **sí** (no estaba en el §2) |
| foto base del clip | `base_img_path.exists()` | asset_manager.py:1488 | sí | **sí** (no estaba en el §2) |
| foto final del clip | `out_path.exists()` | asset_manager.py:691 | sí | **sí** (no estaba en el §2) |
| grade | `dst.exists() and not overwrite` | image_grade.py:68, llamado en asset_manager.py:1633 | sí: crudo nuevo con `_graded` viejo | **sí, sin tocar image_grade**: `_graded` vive en chNN_* y se mueve (no estaba en el §2) |
| piso anti-desync | la copia queda en el slot como `skipped_exists` | asset_manager.py:1272, :1134 | sí | **sí** (idem) |
| pedidos del lote | `pedidos.json`, clave md5 de prompts + refs | asset_manager.py:967 | no: prompt nuevo = clave nueva | no: cubre solo el mismo pedido (y vive en el dir que se mueve) |
| visuales base | `reuse_visuals` + existe | fase2b.py:1051, :1126, :2869 | sí | **sí** |
| flow_specs | existe y cubre los caps | fase2b.py:2348 | sí | **sí** |
| depth y zoom | caché por nombre de foto | fase2b.py:2424, :2436 (depth_probe.py:128, zoom_judge.py:118) | sí: foto nueva con igual nombre hereda | **sí, sin tocar esos dos**: `_archivar_fondos_desfasados` los mueve (no estaba en el §2) |
| capa gfx | `reuse` + `chNN_gfx.mp4` + plan.md5 igual; no mira la foto | gfx_layer.py:596-603, `reuse=` en fase2b.py:1220 | sí: con plan igual, capa con la foto vieja | **sí, sin tocar gfx_layer**: se mueve con `_fase2b_work` (no estaba en el §2) |
| plan congelado | `aprobacion.estado` + existe el resolved | gfx_layer.py:499-510, :608 | no hoy; sí tras re-aprobar | **sí**: el guion desfasado se regenera y el resolved viejo se movió |
| Ken Burns, sfx, pausa, escenas, beats, crítico de rótulos | json de `_fase2b_work` | fase2b.py:2572, :1318, :1576, :2884, :3170; gfx_critic.py:141 | sí | **sí**: se mueven con `_fase2b_work` (no estaban en el §2) |
| segmentos | `--reassemble-from-segments` + hash | fase2b.py:3426 | no: el flag no está en `RENDER_FLAGS` | indirecto: `_fase2b_work` se mueve |
| pre-roll | más nuevo que el base | fase2b.py:1148 | no: mtime | no: se invalida solo |
| visión de fotos | sha1 de los bytes | gfx_vision.py:109 | no: foto nueva, clave nueva | no |
| intensidad | hash de prompt + oraciones | gfx_intensity.py:181 | no si cambia la voz | no |
| render | `_final_gfx.mp4` más viejo que el guion | run_pipeline.py | no hay render con gfx | regla actual (§1) |
| audio por cap | `text_hash`/`tts_hash` | audio_manager.py:614-645 | solo si el texto no cambió | **no** (§1) |
| música | `music_map.json` no se lee: se rehace; la librería elige por intent | m07_music_director.py:1102 | no depende del papel | no |
| m03 | no lee `03_visual.json`: rehace y pisa | m03_visual.py:2027 | no | no hace falta |
| foto madre | **por existencia**, no por `canon_ficha_md5` como dice el §1 | foto_madre.py:374, :449 | sí | **no** (§1): sale del canon de la ficha, no del papel |
| canon | `canon_ficha_md5` | fase1_5.py:311 | sí | no: sale de la ficha |
| `fase2a._should_skip` | status | fase2a.py:241 | no corre con `--topic` (:448) | no (§2) |
| **empaquetado: títulos y miniaturas** | `"paquetes" in metadata.json` | script_engine/m09_packaging.py:638, fase3.py:76 | **sí: `publish/metadata.json` del 30-oct** | **no entra: decisión de Omar** (abierto 1) |
| **`packaged`** | el flag no se limpia con un video nuevo | topics_db.py:96-100, run_pipeline.py | no: Wittenoom lo tiene en None | **no entra** (abierto 1) |

## B y D. Sellos

- `m06_assembler.sello_vigente`: `estado_papel` + `papel_falta` + `estado_narracion` + texto de cada cap de `01b_narration` = `caps` de `01b_narracion_v3`. Si no, `ValueError` y no escribe. Los llamadores no tienen excepción (`test_module_f60_bc` lleva el fixture).
- `asset_manager`: sello al manifest, reuso solo con el mismo sello.
- `fase2b`: `fondos.json`, sello en `GUION_PANTALLA.json`.
- `run_pipeline.etapa_de`: en cascada. **Se borró** `_visuales_base_faltan` y su test; `_fondos_path` queda solo para reconocer la cadena vieja.

## C. Salida

## C. `etapa_de` de Wittenoom

- Hoy: `('papel', 'el papel no está aprobado')`
- `assemble_final_script` hoy: no escribe: «m06_assembler: sin papel aprobado vigente: el papel no está aprobado»
- `01b_narration.json` = la narración aprobada, cap por cap: [True, True, True, True, True, True, True]
- Simulando el papel aprobado (monkeypatch de `estado_papel`): `('voz', 'data/scripts/123bbb64-9fca-4395-8bf4-57d60e219ef1.json sin sello')`

Artefactos del 28-oct que ya no pasan:

- script: script sin sello
- manifest: manifest sin sello
- fondos.json: falta fondos.json
- GUION_PANTALLA.json: falta GUION_PANTALLA.json

Archivos de `_steps/<tid>/` que cambiaron: ninguno

## Tests

- `test_module_f67c.py`: 27 casos, todos en `tmp_path`. El camino del §3 B está en `test_p1_sellado_se_aprueba_p2_y_etapa_de_vuelve_a_la_voz`, los reusos en `test_lo_de_otro_papel…`, `test_todos_los_reusos…`, `test_fondos_de_otro_papel…`, y el audio en `test_el_audio_con_el_mismo_texto…` (1 sola llamada al TTS).
- `test_run_pipeline.py`: `FakePipeline` escribe los sellos; `test_etapa_de_fondos_por_sello_no_por_existencia` reemplaza al de visuales base; casos nuevos por artefacto.
- `test_qa_studio.py`: `test_f67c_fix_y_clipfix_conservan_el_sello_del_script`: `_fix_core` corrido, `_clipfix_core` por lectura de su código.
- Suite amplia + `test_run_pipeline` + `test_qa_studio` + `tests/test_m01f_compuerta` (`f67c/suite_amplia.log`, antes de refrescar los stickers): `6 failed, 1576 passed, 30 skipped, 3 xfailed, 4 warnings in 72.04s (0:01:12)`. Fallas: test_module_f42_mapa.py::test_check_da_0, test_module_f33.py::test_guard_mapa_avisa_si_tocan_gfx_sin_el_mapa, test_module_gfx_lab.py::test_cues_sin_escribir_el_proyecto, test_module_m03_merge_timing.py::test_c_guarda_de_minimo, test_module_m03_merge_timing.py::test_c_veo_path_y_veo_anchor_intacto, test_module_gfx_lab.py::test_preview_usa_las_plantillas_reales: las 4 previas (`gfx_lab` ×2, `m03_merge_timing` ×2) y 2 del mapa por los stickers viejos, que se refrescaron después (ver «Veredicto» y `mapa --check`).

## Diff

```
asset_manager.py               | 59 +++++++++++++++++++++++++++++++++-
 fase2b.py                      | 54 +++++++++++++++++++++++++++++--
 run_pipeline.py                | 73 +++++++++++++++++++++---------------------
 script_engine/m06_assembler.py | 26 +++++++++++++++
 test_module_f60_bc.py          |  1 +
 test_qa_studio.py              | 17 ++++++++++
 test_run_pipeline.py           | 51 +++++++++++++++++++++--------
 7 files changed, 227 insertions(+), 54 deletions(-)
```

## Desvíos y decisiones mías

1. **Reglas de esta tanda rotas sin querer: 2 tests viejos escribieron en `output/` real, solo de Orleans.** `test_module_fase2b_only_cap.py` corrió `fase2b --only-cap ch02` y reescribió `_fase2b_work/ch02_subs.ass` (el segmento tiene backup y volvió a su lugar). `test_module_gfx_lab.py` reescribió `_fase2b_work/gfx_lab_ch02/`. Son archivos que esas corridas regeneran. Wittenoom y `data/` no se tocaron. `test_module_fase2b_only_cap` **falla por su sha de F1** (`ee5e98c3…`, anterior a los subtítulos de F40): no entra a la suite amplia y no lo vuelvo a correr. Por eso **no pude medir el candado md5 de ch02 (`f792f3d4…`)**, que también escribe en `output/`: `--only-cap` solo agrega un aviso.
2. **Mover, no «regenerar sobre lo viejo»:** el §2 pide condicionar cada reuso. En asset_manager y fase2b muevo los archivos desfasados a `_desfasado_*`, y todos los `exists()` dejan de verlos de una vez, incluidos los que el §2 no listaba. Lo pagado no se borra (**ocupa disco**: Wittenoom ≈ 1,2 GB de `_fase2b_work`, más sus fotos).
3. **Corrida de assets cortada:** con `assets_en_curso.json` lo ya regenerado de este papel no se re-paga. No lo pedía el handoff; es una decisión mía: si no, un corte a la mitad re-pagaría todas las fotos.
4. **Un guion largo sin sello no paga fotos:** `process_script` da error en vez de regenerar. Los SHORT quedan como están.
5. **`--plan-only` y `--reuse-visuals` con fondos desfasados paran** (exit 2) en vez de cocer: un render entero no re-cuece DepthFlow sin pedirlo. Si se corre `run_pipeline` no se llega: `etapa_de` manda antes a fondos.
6. **`--only-cap` sigue reusando con aviso:** es el banco del candado md5 de ch02 sobre Orleans, sin sello; no deja video ni sidecar. Es la única excepción y es de laboratorio.
7. **fase2a descarta `papel_md5`** (`_normalize_long`, lista blanca): asset_manager lo lee de `data/scripts/<id>.json`, porque fase2a no se toca.
8. **`01b_narration.json` no lleva md5:** comparo el texto por cap; agregarlo tocaría m01d, un 5.º módulo.
9. **Motivo real:** `data/scripts/<id>.json: sello X… de otro papel` y `… sin sello`, como pide el §3 C.

## Lo que queda abierto

1. **Empaquetado de Wittenoom, para Omar:** `fase3` reusa `publish/metadata.json` del 30-oct (títulos, textos y miniaturas, hechos sobre la narración vieja). Sus bases `assets/<rel>` van a apuntar a fotos nuevas con el mismo nombre, o a nada. Para negarlo hay que renombrar ese archivo a mano o sellarlo en fase3/m09, un 5.º módulo. No lo hice porque esos paquetes pueden tener trabajo elegido. El flag `packaged` tampoco se limpia con un video nuevo; a Wittenoom hoy no le afecta (None).
2. **Foto madre:** el §1 dice `canon_ficha_md5`, pero el reuso es por existencia (`foto_madre.py:449`). Sigue fuera: no sale del papel.
3. **Quedan ≈ 1,2 GB + fotos de Wittenoom en `_desfasado_*`** cuando corra la producción; no se limpian solos.
4. **`--reuse-visuals` a mano sobre un topic viejo sin sello (Orleans) ahora para.** Se destraba con `fase2b <id>` si el manifest tiene sello, y un manifest viejo no lo tiene: esos temas no se re-renderizan sin volver a pasar por voz.
5. **Costo del camino:** tras aprobar el papel de Wittenoom corre voz (audio cacheado si el texto no cambió), m03, assets, fondos y guion de pantalla. Fotos y clips se pagan de nuevo: es lo que pide el candado.

## Veredicto de revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

Corrí `pytest test_module_f67c.py test_run_pipeline.py`: 100 passed. `mapa_modulos.py --check`: 161 archivos, 0 fallas. No corrí nada que escriba en output/ ni que llame APIs.

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Reusos de la tabla: líneas reales | OK | asset_manager.py:691, 1046, 1134, 1310-1313, 1376, 1464, 1476, 1488 coinciden. fase2b.py:1051, 1126, 2348, 2424, 2436, 2869 y gfx_layer.py:596-603 también. foto_madre.py:374/449 y m09_packaging.py:638 también. |
| 2 | Los reusos quedan negados al moverse los archivos | OK | `_archivar_si_desfasado` mueve `chNN_(flux\|veo)` y el manifest (asset_manager.py:1684-1703). Fallbacks, `_graded` y supp viven en esas carpetas (:119-122, :1351, :1449), así que quedan cubiertos. `_archivar_fondos_desfasados` mueve `_fase2b_work` entero y los cachés `flow_specs`, `depth_metrics` y `zoom_verdicts` (fase2b.py:3125-3143). No encontré un reuso río abajo que falte en el listado. |
| 3 | Sin PARADA (ningún reuso obliga a un 5.º módulo) | OK | Lo que queda vivo es `publish/metadata.json` (m09:638, fase3:76) y `packaged`. Ninguno es consecuencia de tocar los 4 módulos: son decisión de Omar y el reporte lo deja como abierto 1. La foto madre depende de la ficha y no del papel; es existencia (foto_madre.py:449), como declara el reporte. |
| 4 | Desvíos declarados | OK | Verificados en el diff: mover en vez de condicionar; `--only-cap` solo avisa (fase2b.py:3315-3323); exit 2 en `--plan-only` y `--reuse-visuals` con fondos desfasados; `ValueError` en LONG sin sello (asset_manager.py:1716-1720). |
| 5 | Etapa C: `etapa_de` de Wittenoom | OK | SALIDAS.md: hoy `('papel','el papel no está aprobado')`. Con `estado_papel` simulado: `('voz','data/scripts/…json sin sello')`. Es coherente con la cascada en run_pipeline.py. |
| 6 | Sello en m06, manifest y `GUION_PANTALLA.json`; `fondos.json` | OK | m06_assembler.py:51-72 y :163. asset_manager.py:1794 (manifest). fase2b.py:3233 (guion) y :3674-3676 (sidecar). |
| 7 | Tests solo en temporales | FALLA | El reporte admite que `test_module_fase2b_only_cap.py` y `test_module_gfx_lab.py` escribieron en `output/` real de Orleans (`ch02_subs.ass` y `gfx_lab_ch02/`). No es Wittenoom ni `data/`. Rompe la regla del handoff §3B y del pedido. |
| 8 | Candado md5 de ch02 | NO VERIFICABLE | `test_module_fase2b_only_cap` falla por su sha de F1 (previo a F40) y escribe en `output/`. El reporte dice que no se pudo medir. |
| 9 | Reporte, veredicto, commit y ESTADO_SESION | NO VERIFICABLE | El veredicto del reporte dice "(pendiente)", el commit no está hecho y ESTADO_SESION se actualiza tras este veredicto. Como pediste, no lo marco como falla. |
| 10 | Suite amplia | PARCIAL | `suite_amplia.log` marca 6 fallas. El reporte las atribuye a 4 previas (gfx_lab ×2, m03_merge_timing ×2) y 2 del mapa por stickers viejos. Los stickers se refrescaron y `mapa --check` da 0, pero la suite no se reejecutó para confirmarlo. |

Fuera de alcance: `git status` muestra `diag_234_cap4.py`, `DECISIONES.md`, `f28a.log` y `pedido_paquetes_wittenoom.txt` modificados. No están en la lista del pedido y no pude atribuirlos a F67c. `DECISIONES.md` entra por el handoff §3E. `diag_234_cap4.py`, `f28a.log` y `pedido_paquetes_wittenoom.txt` no tienen cobertura declarada; confirmar que no son de F67c. No toqué ningún entregable de F67d.

Riesgos que el contrato no cubre:
- El empaquetado de Wittenoom (`metadata.json` del 30-oct, miniaturas) sigue reusable con el papel nuevo. Hay que renombrarlo a mano o decidir sellarlo en fase3/m09.
- Orleans y los demás temas viejos sin sello: `--reuse-visuals` ahora para (exit 2), y cada `fase2b` normal los trata como desfasados (archivan `_fase2b_work`). Re-renderizarlos obliga a volver a pasar por voz.
- Los `_desfasado_*` (≈1,2 GB en `_fase2b_work` de Wittenoom, más sus fotos) no se limpian solos.

## Adenda de CC

Después del veredicto no toqué código de F67c.

- **Fila 7 (FALLA):** es cierta y no se puede deshacer: los dos tests viejos ya escribieron en `output/` de Orleans. Desde que lo detecté no los vuelvo a correr; no entran a ninguna corrida de esta tanda.
- **Fila 8:** el candado md5 de ch02 queda sin medir porque medirlo escribe en `output/`.
- **Fila 10:** después de refrescar los stickers corrí `test_module_f33`, `test_module_f42_mapa`, `test_module_f67c` y `test_run_pipeline`: 113 passed. Las 2 fallas del mapa ya no están. La suite amplia entera vuelve a correr al final de F67d, sin esos dos tests.
- **Fuera de alcance:** `diag_234_cap4.py`, `f28a.log` y `pedido_paquetes_wittenoom.txt` no son míos y no entran al commit.
- **Riesgos:** quedan como abiertos 1, 3 y 4 del reporte.
