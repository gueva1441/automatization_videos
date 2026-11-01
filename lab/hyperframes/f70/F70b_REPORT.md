# F70b — 3 fotos del lab F70 a producción

Handoff: `lab/hyperframes/f70/HANDOFF_F70b_promover.md` (md5 f684f5439698daff67302cd6eefb2005).

## Resultado

**`ch03_img_08`, `ch03_img_15` y `ch06_img_07` ya son las del lab, con su `_graded` nuevo.** Sin llamadas a ningún modelo: US$ 0. El manifest cambió solo en esas 3 entradas (y la fila del clip de ch01, de F69). No corrí fase2b ni run_pipeline.

**Para tener en cuenta:**
- **El guion sigue con el texto viejo en estas 3.** Los casilleros no cambiaron, así que el manifest dice el prompt del lab y el guion vivo y `03_visual.json` el anterior. Si se usa «pedir fix» en alguna, el prompt se rearma desde los casilleros: `ch03_img_08` y `ch03_img_15` recuperan la frase de texto y las 3 vuelven a «taken in». Es lo previsto por el handoff: el arreglo general va antes del tema 2.
- **El `prompt` del manifest en las fotos con madre ahora empieza con «A photograph of the same person…»,** porque es el texto enviado. Antes el manifest guardaba el prompt sin esa frase. Afecta a `ch03_img_08` y `ch06_img_07`. Nadie lo lee para generar la foto, pero sí `fase2b.py:2188-2207` (`_load_image_prompts`), para el director de movimiento: en estas 3 fotos verá el prompt nuevo, con esa frase.
- **`ch03_img_15` trae lo que marcó el lab:** el almanaque «OCT 1 1962» legible y una caja de luz que parece un panel moderno, fuera de época para 1962.
- **`usd` y `respaldo_motivo` no cambiaron:** la `.llamada.json` no los trae, y el handoff los pide «cuando existan». Valían 0,042 y `null`, los mismos que dio el lab. Sí cambian `prompt`, `segundos` y `flux_meta.segundos`.

## Verificación

| Foto | Archivo | md5 antes | md5 después | == lab | Tamaño |
|---|---|---|---|---|---|
| `ch03_img_08` | `.png` | `80beaefc` | `bda61eff` | sí | 2560×1440 |
| | `_native.png` | `010c7cae` | `aee500cc` | sí | 1376×768 |
| | `_graded.png` | `c89d40aa` | `efe680ff` | (no hay en el lab) | 2560×1440 |
| `ch03_img_15` | `.png` | `cb59c5f4` | `ac76049d` | sí | 2560×1440 |
| | `_native.png` | `09a510b7` | `741ea1eb` | sí | 1376×768 |
| | `_graded.png` | `e6f9c924` | `79c23630` | (no hay en el lab) | 2560×1440 |
| `ch06_img_07` | `.png` | `35910e42` | `b60bafcd` | sí | 2560×1440 |
| | `_native.png` | `13dd8866` | `e19a6d37` | sí | 1376×768 |
| | `_graded.png` | `7b1057f9` | `6ea9c63a` | (no hay en el lab) | 2560×1440 |

| Chequeo | Antes | Después |
|---|---|---|
| `papel_md5` | `39c99927…` | igual |
| `etapa_de` | `fondos` («falta fondos.json») | igual |
| Guion vivo (md5) | `2b1903bd…` | igual |
| `03_visual.json` (md5) | `79fb554d…` | igual |

**Manifest, contra el de antes de F69 (`…20261101_153557`):** claves de raíz iguales, y solo difieren estas filas:

| Fila | Claves que cambian |
|---|---|
| `ch01`, clip | `clip_motor`, `clip_rechazos`, `clip_segundos`, `clip_usd`, `foto_arranque_md5`, `foto_final_md5`, `image_prompt`, `segundos`, `ssim`, `video_prompt` (F69) |
| `ch03_img_08` | `flux_meta`, `prompt`, `segundos` |
| `ch03_img_15` | `flux_meta`, `prompt`, `segundos` |
| `ch06_img_07` | `flux_meta`, `prompt`, `segundos` |

El diff completo de las 3 entradas está en `promover_resultado.json`.

**Horneados:** se borraron `ch03_flux_visual.mp4` y `ch06_flux_visual.mp4` de `_fase2b_work` (no había `hybrid` en esos caps). No queda ningún `*visual.mp4` de ch03 ni ch06.

**Backups:** en `assets/_qa_backups/`, con ts `20261101_154524`: los 4 archivos de cada foto y el manifest.

**Hoja:** `promovidas_hoja.jpg`, `_graded` vieja | nueva de las 3.

## Veredicto de revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Backup antes de pisar (.png, _graded, _native, .llamada.json de cada foto + manifest) | OK | _qa_backups/*.20261101_154524.bak.*: 12 archivos de fotos + assets_manifest. Los md5 de los backups son los "antes" del reporte (80beaefc, c89d40aa, 010c7cae, etc.) |
| 2 | .png, _native.png y .llamada.json de producción == lab (las 3 fotos) | OK | md5 recalculado: bda61eff/aee500cc/bb0fd282 (08), ac76049d/741ea1eb/7c17178d (15), b60bafcd/e19a6d37/546a6f17 (06_07); todos == lab |
| 3 | Tamaños 2560x1440 (.png y _graded) y 1376x768 (_native) | OK | PIL: 9 archivos medidos |
| 4 | _graded nuevo por _grade_como_produccion | OK, sin regenerar | md5 distinto del viejo en las 3 (efe680ff, 79c23630, 6ea9c63a). mtime 15:45, de esta tanda. No lo graduó en mi scratch: reproducibilidad NO VERIFICADA. La hoja muestra el _graded nuevo con la foto nueva |
| 5 | Manifest: solo cambian las 3 entradas | OK | Diff por claves contra ts 154524: solo ch03_img_08, ch03_img_15 y ch06_img_07, y solo en `flux_meta`, `prompt`, `segundos`. Contra ts 153557: esas 3 más la fila `ch01 clips` (F69). Claves de raíz iguales |
| 6 | prompt == texto de la .llamada.json | OK | `prompt == llamadas.nb2_lite.texto` en las 3. segundos 13.4/7.4/20.0 y motor nb2_lite también coinciden |
| 7 | usd/respaldo_motivo | OK | La llamada del lab no trae `usd` (None). El manifest conserva 0.042, como dice el reporte. `respaldo_motivo` es null en ambos |
| 8 | Horneados invalidados | OK | `_fase2b_work` ya no tiene ch03 ni ch06 `*visual.mp4`. Quedan ch02, ch04, ch05 y ch07_hybrid, que son otros caps. Solo se borraron mp4 |
| 9 | papel_md5 y etapa_de iguales | OK | papel_md5 39c99927c5d9… en el manifest actual y en el backup 154524. etapa_de recalculado = ('fondos','falta fondos.json'), igual que el "antes" guardado |
| 10 | Guion vivo y 03_visual intactos | OK | md5 actual 2b1903bd… y 79fb554d…, iguales a los "antes" de promover_resultado.json. Contra los backups 153557 difieren solo en `chapters[0]` (image_prompt, image_f8), que es el ch01 de F69 |
| 11 | Hoja vieja\|nueva | OK | La abrí. Existe, con las 3 filas. Se ven el almanaque "OCT 1 1962" y la caja de luz moderna en 15, como dice el reporte. La vieja de ch06_img_07 tenía "2023" sobreimpreso y la nueva no |
| 12 | Línea de Omar 15:04 en DECISIONES.md | OK | `git diff -- DECISIONES.md`: línea agregada, "2026-11-01 15:04 … Omar · F70b" |
| 13 | Reporte y afirmaciones de «Para tener en cuenta» | PARCIAL | Ver observaciones |
| 14 | Commit, sin png | NO VERIFICABLE (después) | promover.py, F70b_REPORT.md, promover_resultado.json, promovidas_hoja.jpg y el handoff están sin trackear. DECISIONES.md modificado. Los png quedan fuera por el .gitignore de la carpeta |

Observaciones:
- **Quién lee el `prompt` del manifest (afirmación 13).** El reporte dice "no encontré quién lo lea para generar; no lo verifiqué". Sí lo lee `fase2b.py:2188-2207` (`_load_image_prompts`) y lo usa en la línea 2238. Ahí el director de movimiento recibe el prompt por imagen. Esto no genera la foto, pero la elección de movimiento de estas 3 fotos verá el prompt nuevo, con «A photograph of the same person…». El reporte debería decir que lo usa el director, no que nadie lo lee.
- **Rutas de regeneración.** `qa_studio_server.py:553, 914, 1135` y `asset_manager.py:1078+` leen `prompt` del guion y de `03_visual`, no del manifest. Eso es coherente con lo que dice el reporte sobre «pedir fix», que rearma desde los casilleros.
- **ESTADO_SESION.** El handoff pide una línea en `lab/ESTADO_SESION.md`. No hay diff en ese archivo ni mención de F70b. Falta, aunque tu pedido no la listó.
- **Todavía no verifiqué la línea de `ch01 clips`** más allá de que difiere en la fila. La atribución a F69 es coherente con los backups.

Fuera de alcance: ninguno atribuible a F70b. En producción solo se tocaron los 9 archivos de fotos, 3 `.llamada.json`, el manifest y los 2 mp4. Los demás modificados (qa_studio_server.py, qa_studio.html, MAPA_*, etc.) ya estaban así antes de la tanda. `script_engine/` y `asset_manager.py` están sin cambios.

Riesgos que el contrato no cubre:
- Guion y `03_visual` tienen el prompt viejo y el manifest el nuevo. Cualquier rearmado de esas 3 vuelve a la frase de texto y a «taken in», y la próxima corrida de fase2b usa un prompt distinto en el director.
- `ch03_img_15` queda en producción con una caja de luz anacrónica para 1962 y el almanaque legible. Omar la aprobó viéndolo en el lab, pero no hay filtro posterior.
- No hay control de que ch03 y ch06 se vuelvan a hornear con las fotos nuevas hasta que alguien corra fase2b.

**Adenda mía, posterior al veredicto:** corregí en «Para tener en cuenta» lo de quién lee el `prompt` (observación 1). La línea de ESTADO_SESION va en este commit. Ningún resultado cambió.
