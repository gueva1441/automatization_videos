# F59 — Salida A (código, US$ 0) · PARADA A

Handoff `lab/hyperframes/f59/HANDOFF_F59_qa_studio_produccion.md` (md5 `9325c5ee7e284e8012aedcf8d1284f07`). OK del analista a la Etapa 0 con una chascada nueva (galería sin `*_graded.png`; DECISIONES 2026-10-30, «F59 A5 (analista, chascada nueva)»). Tres subagentes en paralelo: S1 = A1 (m03), S2 = A2 + A3 + galería (QA Studio), S3 = A4 + A5 (front y chascadas); CC integró (test de F57 del clipfix, informe del scrub en pantalla, stickers, MAPA, suites). Sin red, sin LLM. Commits: `724c948` (A1 aparte) y el de la Parte A entera.

## 1. Los 2 pedidos como quedaron en el código (`qa_studio_server.py:724` y `:739`; un test los extrae de los bloques ``` del handoff y los compara byte a byte)

```
PEDIDO_EDITAR_CASILLEROS = """Editás los casilleros de una foto de un video documental de historia oscura. Los CASILLEROS son un JSON en inglés que después arma el código en el prompt de la foto. El ANCLA es la oración de la narración que la foto muestra. Omar pide un cambio en español.

Devolvé el mismo JSON, con las mismas claves. Cambiá solo los casilleros que el pedido toca; los demás van copiados tal cual. Escribí lo que se ve, en inglés: si el pedido saca algo, nombrá qué ocupa su lugar. Si el pedido es una emoción, escribila como gesto visible. Si el pedido choca con el ANCLA, hacé lo más cercano que el ANCLA permita.

ANCLA:
{ancla}

CASILLEROS:
{casilleros}

PEDIDO DE OMAR:
{pedido}"""
```
```
PEDIDO_EDITAR_MOVIMIENTO = """Editás el movimiento de un clip de {segundos} segundos de un video documental de historia oscura. El MOVIMIENTO aprobado está en inglés; la VOZ es lo que se oye durante el clip. Omar pide un cambio en español.

Devolvé el MOVIMIENTO con el cambio aplicado, en inglés y de largo parecido; lo que el pedido no toca va igual. Escribí lo que pasa en cámara y en la escena (si el pedido dice que algo no se mueva, escribí que queda quieto).

VOZ:
{voz_clip}

MOVIMIENTO:
{movimiento}

PEDIDO DE OMAR:
{pedido}"""
```
Se rellenan con `str.format`; el JSON de casilleros va como valor (`json.dumps(…, ensure_ascii=False, indent=2)`), no en la plantilla. `{segundos}` = `video_prompt._segundos()` (`VEO_CLIP_DURATION_SEC`, «8»). Esquemas: objeto con las claves editables presentes en el ítem (`required` = esas) / `{"movimiento": string}`. Reintentos: `m03_visual._call_with_validation_retry` real (`MAX_RETRY_ATTEMPTS`, `checklist=""`, `caller=_llamar_casilleros`), validador que lanza `VisualValidationError` (no es objeto / faltan o sobran claves / prosa vacía); `claude_helpers.ClaudeError` → `(False, "Opus no editó …")`; validador agotado → `(False, "el editor no devolvió … válidos")`, sin generar.

## 2. `CASILLEROS_EDITABLES` (m03_imagenes_v3.py:623, al lado de `_PROSA`)

`CASILLEROS_EDITABLES = (*_PROSA, "shot_scale", "text_in_image", "year")` → `('subject', 'action', 'setting', 'lighting', 'camera_angle', 'lens_technique', 'shot_scale', 'text_in_image', 'year')`. `people_group` fuera (decisión c): vuelve por código; `gaze_interaction`, `color_palette`, `props_detail`, `mood`, `style`, `hard_fact_ids` tampoco llegan a Opus (el armado C no los lee).

## 3. Antes → después por función

| Función | Antes | Después |
|---|---|---|
| `m03_visual._render_prompts_seedream` (A1) | el armado de cada ítem vivía en dos bucles (scrub + fix_text_slot l. 676-683; anio_final → armar → f8_backstop → _sacar_frases_con_texto → prompt/raw_llm_prompt/sensible/motivos l. 690-715) | asigna beat/cerrada, `_apply_place_exterior_filter`, y por ítem `anio, fuente = v3img.anio_final(e, it)` → `armar_item(it, anio, grupos, escala, lang, composicion=, sin_cartel=, anio_fuente=fuente)`. Salida byte-idéntica (abajo) |
| **`m03_visual.armar_item(it, anio, grupos, escala, lang, composicion="", sin_cartel=False, anio_fuente="") -> it`** (nueva, l. 697) | — | scrub_slots + fix_text_slot (`_f8_slots_scrub`, `texto_en_imagen`), `sin_cartel` apaga `text_in_image.present`, `armar` → `f8_backstop(escala)` → `_sacar_frases_con_texto`; deja `raw_llm_prompt`, `prompt`, `art_profile`, `anio`, `anio_fuente`, `_f8_problemas`/`_f8_texto_fuera` (si hay), `sensible`, `motivos`. **Decisión de CC:** kwarg extra `anio_fuente` (el handoff lo dejaba fuera): si `armar_item` escribiera solo `anio` y m03 pusiera `anio_fuente` después, la clave iría al final del dict y el `03_visual.json` persistido ya no sería byte-idéntico. Orden del scrub: ahora corre después de `_apply_place_exterior_filter` y de `anio_final`; es inocuo porque `scrub_slots` solo toca strings y ningún patrón de HANDS_FACE/FORBIDDEN/WEAPONS matchea un año de 4 dígitos, un `shot_scale` válido ni un `subject_ref`; `anio_final` solo lee `year`; el filtro place reasigna `foto_madre_ref` (lista). Lo fija el test de orden de claves |
| `QAState._flux_imgs` / `_supp_imgs` (chascada, l. 185-197) | `glob` arrastraba `*_graded.png` (idx 0 → cuadros vacíos, orden, anclas corridas, `sync_approx`) | filtran con `_IMG_NAME_RE`; los `_graded.png` siguen en disco para m09 |
| `resolve_fix_entry` (l. ~516) | {cap, img_name, kind, idx, prompt, art_profile, subject_ref, narration_anchor} | **agrega** `casilleros` (raw_llm_prompt parseado o None), `anio`, `anio_fuente`, `beat`, `foto_madre_ref` (lista, None si vacía); lo viejo igual (`_reseed_core` y sus tests pasan) |
| `resolve_clip_entry` (l. ~575) | sin voz ni foto final | **agrega** `voz_clip` (o "") y `_final` (path si `<stem>_final.png` existe) |
| `_fix_core(state, tid, cap, img_name, pedido, *, llamar_fn, retry_fn, armar_item_fn, topic_fn, seed_fn, generate_fn, grade_fn, is_hook_fn, data_uri_fn, content_rejected_exc, now_ts)` (l. 957) | Flash reescribía el prompt final (`_FIX_REWRITE_INSTRUCTION`), pisaba solo el `.png` crudo, sin foto madre, sin grade, sin guardar | sin `casilleros`/`anio` → `(False, "guion viejo: correr m03 de nuevo")`; Opus edita solo `CASILLEROS_EDITABLES` presentes; casilleros finales = ítem + editados (`people_group` por código); `anio_final({"respaldo": (anio, anio_fuente)}, nuevos)`; contexto sin LLM (`fase1_5._load_topic_by_id`, `grupos`, `escala` del beat vía `load_beats(topic, base/data/scripts/_steps)`, `place_language`); `armar_item`; backups de PNG crudo + `_graded.png` + `03_visual.json` + guion vivo; Seedream (`_generate_flux_image_at(prompt, "", out, use_ultra, seed=_seed_for_subject(…), foto_madre_data_uris=` resueltos contra `foto_madre_registry`); grade → `_graded.png`; guarda el ítem en `_steps/<tid>/03_visual.json` (relativo a `state.base`) y en `state.script_path`; `_invalidate_baked`; `(True, "foto rehecha; casilleros editados: X. El filtro de producción sacó: …")`. Rechazo → `(False, "filtro: …")` sin tocar el guion. **Decisión de CC:** grade que falla → `(False, "grade falló: … (la foto cruda quedó nueva; el guion no se tocó)")` para no desacoplar video y guion (hoy `_apply_grade` solo avisa) |
| `_clipfix_core(state, tid, cap, pedido, *, llamar_fn, retry_fn, foto_final_fn, generate_clip_fn, is_hook_fn, content_rejected_exc, now_ts)` (l. 1167) | rehacía la FOTO inicial con el rewriter de foto, Veo con `video_prompt` intacto, `generate_veo_fn` de 3 posicionales, sin foto final ni voz | sin `voz_clip` → `(False, "guion viejo: correr m03 de nuevo")`; Opus edita el MOVIMIENTO; `foto_final_del_clip(first_frame, image_prompt, voz_clip, <stem>_final.png, use_ultra=)` (reusa si existe); backup del mp4; `_generate_clip(first_frame, movimiento, out_clip, image_prompt=, ancla=voz_clip, foto_final=final["path"], log=)`; rechazo G y K → `(False, "filtro: <rechazos literales>")`, mp4 intacto; guarda `video_prompt` en 03_visual.json y guion vivo (con backups); `_invalidate_baked`. La foto inicial no se toca |
| `/fix_clip` | — | igual: el 400 «el cap no tiene clip Veo regenerable» queda para caps sin clip; «guion viejo» lo devuelve `_clipfix_core` |
| `_fix_worker` / `_clipfix_worker` | «✓ ok» | «✓ ok · <informe>»; el informe del scrub llega a `/fix_status.reason` |
| `qa_studio.html:508` (A4) | placeholders genéricos | los 2 hints de `PENDIENTE_C_QA_hint.md` tal cual (comillas dobles → `&quot;`); «Veo» → «clip» (l. 803, 814, 816; `grep Veo` = 0). **Agregado de CC** (`pollFix`, l. 792): cuando `ok`, muestra `reason` («✅ lista · foto rehecha; … El filtro de producción sacó: …»); antes el front ignoraba `reason` en el camino ok y Omar no veía el informe (A2.8) |
| `m09_packaging.COMPOSICION_MINIATURA` (A5, l. 79) | «The person fills the right half of the frame, face and torso large; …» | «The main subject fills the right half of the frame; the left half is dark, uncluttered negative space.» (DECISIONES 08:22); comentario al día; `test_module_f58.py:253` compara contra el literal nuevo |
| `asset_manager.foto_final_del_clip` (A5, l. 675) | `(foto_inicial, image_prompt, voz_clip, video_prompt_aprobado, out_path, *, use_ultra)` | `(foto_inicial, image_prompt, voz_clip, out_path, *, use_ultra=False)`; llamadas: asset_manager:1210, `f57/clip_b.py:80`, `test_module_f57.py` 268/288/304 y `def final(…)` 326 (hay uno solo, no «doble»). `video_prompt.escribir(..., video_prompt_aprobado, ...)` intacto |
| Borrado (con sus tests) | `_FIX_REWRITE_INSTRUCTION` (l. 698-756), `_build_fix_user_prompt` (762-771), `_fix_core` viejo con el import de Flash (851-926), bloque «⚠ DORMIDO» + `_FIX_CLIP_REWRITE_INSTRUCTION` (967-1011), `_build_clipfix_user_prompt` (1014-1024), `_clipfix_core` viejo con `generate_veo_fn` y el paso de la foto (1027-1120); `test_module_137c_fix_recetario.py` (git rm); en `test_qa_studio.py` `_fix_deps`/`_clipfix_deps` viejos y los tests de fix/clipfix (347-475, 479-617) reescritos; `test_module_f57.py::test_clipfix_core_sigue_con_3_posicionales_y_sin_final` (buscaba el texto literal de `generate_veo_fn`) borrado con nota | — |

Helpers nuevos en qa_studio_server.py (l. ~838-955): `_steps_dir`, `_visual_path`, `_foto_final_path`, `_read_json`, `_write_json` (indent=2 como m03/m06), `_chapter_of`, `_item_of`, `_backup` (`_qa_backups/<nombre>.<ts>.bak<sufijo>`), `_refs_madre` (str o lista, como `am._norm_foto_madre_refs`), `_editar_con_opus`, `_esquema_casilleros`, `_grade_como_produccion`, `_informe_scrub`. Números: solo `MAX_RETRY_ATTEMPTS` y `VEO_CLIP_DURATION_SEC` (vía `_segundos()`); ninguno nuevo.

## 4. Ejemplos de los tests

**Casilleros antes / después** (`test_fix_core_casilleros_editados_armar_grade_guardado`, pedido «que mire a la cámara con el ceño fruncido»):
- Antes: `subject = "A miner, charlie cinco seis"`, `action = "stands still at the pit head"`, `people_group = ["miners"]`, `gaze_interaction = "looks away"`.
- A Opus llegan solo las 9 claves editables (sin `people_group` ni `gaze_interaction`); esquema con esas 9 en `required`.
- Después (guardado igual en 03_visual.json y en el guion vivo): `subject = "A Spanish miner facing the camera, brow furrowed"`, `action = "he stares straight into the lens, jaw clenched"`, `people_group` y `gaze_interaction` intactos, `anio = "1962"`, `_f8_slots_scrub = ["action: HANDS_FACE: jaw clenched"]`, prompt rearmado con `escala=True`, `lang=en`. Respuesta: «foto rehecha; casilleros editados: subject, action. El filtro de producción sacó: action: HANDS_FACE: jaw clenched.»
- Humo a mano (no es test; sobre una copia temporal de la copia de lab, con el `armar_item` real, ch02_img_04): prompt antes «…in a modest cotton dress, pressed against her lean dark-haired husband…» → después «…in a modest cotton dress, looking straight into the camera with a furrowed brow, pressed against her…»; `anio 1962`; `people_group ['spanish_migrant_families']` intacto; 03_visual.json == guion vivo; 4 backups.

**Movimiento antes / después** (`test_clipfix_core_solo_movimiento_foto_inicial_intacta`, pedido «cámara quieta, solo sube el polvo, lento»):
- Antes: `video_prompt = "Static camera with subtle upward drift over the skyline"`; el prompt a Opus empieza «Editás el movimiento de un clip de 8 segundos…», con `VOZ:\nvoz del clip uno`, el movimiento aprobado y el pedido.
- Después: el motor recibe `"The camera holds completely still; fine dust rises slowly."`, `ancla="voz del clip uno"`, `image_prompt` del cap, `foto_final=ch01_img_01_final.png`; `video_prompt` guardado en los dos archivos; `image_prompt`/`voz_clip`/foto inicial sin cambios; backup `ch01_clip_01.mp4.<ts>.bak.mp4` antes de generar.

**A1 byte-idéntico:** fixture fijo `lab/hyperframes/f59/a1_fixture.json` (de `a1_fixture.py`: 96 ítems de Wittenoom = caps 2-6 (16/16/14/16/16), supp de caps 1 y 7 (4 + 12), `image_f8` de 1 y 7; `people_groups` de topics_db, `escala` por beat, `lang=en`): **96/96** iguales en `prompt`, `raw_llm_prompt`, `sensible`, `motivos` (y `anio`, `anio_fuente`, `art_profile`). Más `_render_prompts_seedream` ANTES (`git show f7265fe:`) vs DESPUÉS con `_llamar_casilleros` mockeado (4 casilleros: uno normal; uno con cliché de manos + prohibida + `interior_scene`; uno con `year="circa 1960s"`; uno con texto en español), `refill=True`, en 3 modos (default / sin_cartel / composicion): JSON completo, prompt a Opus y orden de claves idénticos. 2 xfail strict declarados: `_f8_slots_scrub` de `ch01_supp_01` y `ch07_supp_01` no se reproduce desde los casilleros ya scrubeados (`raw_llm_prompt` se escribe después del scrub; el prompt sí sale idéntico). Al margen: en `ch01_supp_01` el scrub sacó «loosely **wound** white cotton bandage» por `\bwounds?\b` (falso positivo del participio), no es de esta tanda.

## 5. Tests nuevos (sin red; `retry_fn` es el real)
`test_qa_studio.py` (42, antes 32): `test_casilleros_editables_resuelta`, `test_pedidos_byte_a_byte_con_el_handoff`, `test_galeria_ignora_graded` (n = crudos, `anchors[i]` en la foto i, `sync_approx False`, `caps()[count]`), `test_fix_resolve_entry_flux_and_supp` (+ claves nuevas), `…_guion_viejo_sin_casilleros`, `test_fix_core_casilleros_editados_armar_grade_guardado`, `…_anio_invalido_cae_al_del_item`, `…_sin_scrub_informa_igual`, `…_foto_madre_resuelta_contra_registry`, `…_supp_uses_ultra_for_hook`, `…_guion_viejo_no_llama_a_opus`, `…_tres_validaciones_fallidas_no_genera` (= `MAX_RETRY_ATTEMPTS` llamadas), `…_validador_rechaza_claves_de_mas_o_de_menos`, `…_claude_error`, `…_content_rejected_no_guarda`, `test_fix_guard_one_at_a_time`, `test_resolve_clip_entry` (+ `voz_clip`, `_final`), `test_clipfix_core_solo_movimiento_foto_inicial_intacta`, `…_reusa_final_existente`, `…_rechazo_g_y_k_mp4_intacto`, `…_guion_viejo_sin_voz_clip`, `…_validacion_fallida_no_genera`, `test_clipfix_guard_shared_with_photo`. `build_topic` extendido (casilleros, `raw_llm_prompt`/`anio`/`anio_fuente`/`beat`/`foto_madre_ref`, `voz_clip` en caps 1 y 7, `foto_madre_registry`, `_steps/<tid>/03_visual.json`; `old_script=True`). `test_module_f59_a1.py` (102 + 2 xfail).

## 6. Suites
`bash lab/hyperframes/f41/verificar.sh f59` (logs en `lab/hyperframes/f41/f59/`):
- ch02 `--only-cap` md5 **`f792f3d483a1fa42daed5f7f0e054f46`** (candado intacto).
- rápida: **53 passed**, 3 skipped.
- amplia: **1295 passed**, 31 skipped, **3 xfailed** (2 de `test_module_f59_a1` + 1 previo de `test_module_f58`), **4 failed = las 4 previas** (`test_module_m03_merge_timing` ×2, `test_module_gfx_lab` ×2; no son de F59).
- `test_qa_studio.py` (no está en la amplia) + `test_module_f57.py`: **61 passed**.
- `python lab/tools/mapa_modulos.py --check`: 158 archivos · **0 fallas**. Stickers al día: `qa_studio_server.py`, `qa_studio.html`, `asset_manager.py`, `script_engine/m09_packaging.py` (orquestador), `script_engine/m03_visual.py`, `script_engine/m03_imagenes_v3.py` (fase2a); `_build_clipfix_user_prompt` salió de `funciones_muertas`; el modelo del fix pasa de Gemini a Opus.

## Veredicto de revisor-handoff — Etapa A (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Los 2 pedidos byte a byte | OK | Extraje los bloques del handoff (l. 97-108 y 115-126) con un script propio y los comparé con `qa_studio_server.PEDIDO_EDITAR_CASILLEROS` y `PEDIDO_EDITAR_MOVIMIENTO`: True y True. Placeholders `{ancla}/{casilleros}/{pedido}` y `{segundos}/{voz_clip}/{movimiento}/{pedido}`. |
| 2 | `CASILLEROS_EDITABLES` | OK | m03_imagenes_v3.py:623 `(*_PROSA, "shot_scale", "text_in_image", "year")`. Resuelve a las 9 claves del handoff; `people_group` queda fuera. |
| 3 | A1 byte-idéntico | OK | `pytest test_module_f59_a1.py`: 102 passed, 2 xfailed (los 2 xfail declarados en SALIDA_A). `a1_fixture.json` es una copia fija de 96 ítems. El test «antes vs después» carga m03 de `git show f7265fe` (l. 21, 137) y compara el JSON completo y el orden de claves en 3 modos. Ese test sí lee `topics_db.json` y `01b_narration.json` vivos (l. 106, 111), pero los mismos datos alimentan los dos lados, y se saltea si faltan. |
| 4a | A2 puntos 1-9 | OK | El código sigue el handoff punto por punto. Desviaciones declaradas: kwarg `anio_fuente` en `armar_item` y grade que falla hace fallar el fix. |
| 4b | A3 puntos 1-6 | OK | Mismo resultado, uno por uno contra `_clipfix_core`. |
| 4c | Borrados completos | PARCIAL | En código, tests y html no queda `_FIX_REWRITE_INSTRUCTION`, `_build_fix_user_prompt`, `generate_veo_fn` ni `DORMIDO` (solo un comentario en test_module_f57.py:370). Sí quedan nombres viejos en: `lab/mapa/stickers/_partes/orquestador_a.json:17` (`_build_clipfix_user_prompt`, `_FIX_CLIP_REWRITE_INSTRUCTION`, DORMIDO) y `test_module_137c_fix_recetario.py` en `lab/MAPA_PROYECTO.json:8109`, `lab/mapa/tests_collect.json:182`, `lab/mapa/tests_lab.json:1637`. |
| 5 | Chascada de la galería | OK | qa_studio_server.py:185-197 filtra con `_IMG_NAME_RE`. `test_galeria_ignora_graded` (test_qa_studio.py:497) cubre n = crudos, `anchors[i]` en la foto i y `sync_approx` False. Pasa. |
| 6 | A4 hints y «Veo» | OK | Los 2 placeholders de qa_studio.html:508 coinciden con `PENDIENTE_C_QA_hint.md`, con `&quot;` en las comillas dobles. `grep -c Veo qa_studio.html` = 0. Agregado de CC: `pollFix` muestra `reason` cuando ok. |
| 7 | A5 | OK | `COMPOSICION_MINIATURA` es literalmente la oración de DECISIONES 08:22 y el comentario está actualizado. `foto_final_del_clip(foto_inicial, image_prompt, voz_clip, out_path, *, use_ultra)` sin `video_prompt_aprobado`. Las llamadas (asset_manager:1210, clip_b.py:80, test_module_f57 268/288/304, `def final` 326, qa_studio_server) están todas actualizadas. `video_prompt.escribir` intacto. |
| 8 | Números nuevos | PARCIAL | `MAX_RETRY_ATTEMPTS` y `_segundos()` tienen origen. Hay recortes de mensaje nuevos sin origen declarado: `[:200]` (l. ~345/347) y `[:600]` (`filtro:` del clip). Antes no existían en el archivo (0 ocurrencias en f7265fe); `[:160]` viene del código previo. |
| 9 | Suites y MAPA | OK | Corrí `pytest test_qa_studio.py test_module_f57.py test_module_f58.py`: 94 passed, 1 xfailed. `mapa_modulos.py --check`: 158 archivos, 0 fallas. Logs de f41/f59: rápida 53 passed y 3 skipped; amplia 1295 passed, 3 xfailed, 4 failed (`m03_merge_timing` ×2 y `gfx_lab` ×2, atribuidas a previas por SALIDA_A, no re-verificadas); ch02 md5 `f792f3d4…`. |
| 10 | Sin gasto y B sin correr | OK | `data/cost_history.json` tiene un registro nuevo (10:24:51, video `ba6c3cac`) con `entries: []` y total 0.0, que corresponde al `--only-cap` ch02 del candado. No hay `F59_REPORT.md`, ni hoja f59, ni `_qa_backups` en `base/`. |
| 11 | SALIDA_A y ESTADO | OK | SALIDA_A.md (84 líneas) trae los pedidos, `CASILLEROS_EDITABLES`, la tabla antes y después, los ejemplos y las suites. ESTADO_SESION al día con PARADA A y la B esperando OK. |

Fuera de alcance: ninguno. Todo lo tocado está en la lista del contrato (MAPA y stickers incluidos). `diag_234_cap4.py` y `f28a.log` ya estaban modificados antes de la tanda.

Observaciones:
- Referencias viejas en los sticker `_partes` y en los índices del MAPA (fila 4c). `--check` no las detecta.
- Los recortes `[:200]` y `[:600]` no tienen origen (fila 8).
- `_fix_core` lee el guion vivo y `03_visual.json` antes de generar y los escribe completos después de Seedream y grade. Un fix de narración u otro writer en ese intervalo se pisa. Además `dst.update(it)` copia al guion vivo todos los campos de `03_visual` del ítem; si el ancla difiere por espacios (95/96 literal en Etapa 0), el guion vivo queda con el ancla de `03_visual`.
- La orden de scrub en `armar_item` cambió respecto de m03 (corre después del filtro place y de `anio_final`). CC lo justificó y el test de orden de claves y los 96/96 lo respaldan, pero no hay prueba exhaustiva.

Riesgos que el contrato no cubre: (1) en la Etapa B todavía no se probó que el `video_prompt` guardado por QA sobreviva a un m06 nuevo ni que `_generate_clip` entregue «rechazos literales» con motores reales. (2) Los 4 fallos previos de la amplia no se re-verificaron contra f7265fe.

### Adenda de CC
- **Fila 4c:** `lab/mapa/stickers/_partes/*.json`, `lab/mapa/hechos.json`, `lab/mapa/tests_collect.json` y `lab/mapa/tests_lab.json` son los insumos y auditorías de F42 (commit `6ed0c41`), no se regeneran por tanda; los stickers vivos (`orquestador.json`, `fase2a.json`) y `MAPA_PROYECTO.{json,md}` (de `mapa_modulos.py`) están al día, y `_build_clipfix_user_prompt` salió de `funciones_muertas`. La fila «test: test_module_137c_fix_recetario.py» de `MAPA_PROYECTO.json:8109` viene de `hechos.json` (F42): queda como abierto 5 (abajo), sin tocar a mano un archivo generado.
- **Fila 8:** `[:200]` y `[:600]` son recortes de mensajes de error para `/fix_status.reason` (como los `[:160]` que ya había y los `[:60]/[:90]/[:120]` de F58); no entran a la lógica. Se declaran.
- **Observación 3 (ventana de escritura y `dst.update(it)`):** es cierto; el guard `_FIX` ya impide dos fixes a la vez (foto, clip y narración comparten el guard), así que el intervalo solo lo pisa un writer externo (p. ej. un m06 nuevo), que es el caso que la decisión b) del analista contempla guardando en los dos archivos. El ancla del ítem de 03_visual pasa al guion vivo tal cual: en Wittenoom la única diferencia es un espacio por un salto de párrafo (ch03 ítem 16). Queda como abierto 6.
- **Observación 4:** el razonamiento del orden está en §3; lo fijan el test de orden de claves por ítem, los 96/96 y los 3 modos del test antes/después con casilleros que disparan scrub, filtro place y respaldo de año.
- **Riesgos:** son los de la Etapa B (clip real, m06 nuevo); se miden ahí.

## Lo que queda abierto (Etapa A)
1. La foto inicial de un cap con clip no se rehace desde QA (decisión a del analista).
2. Fila xfail de A1: `_f8_slots_scrub` no se reproduce desde casilleros ya scrubeados (y el falso positivo «loosely wound bandage» por `\bwounds?\b`, fuera de F59).
3. Grade que falla hace fallar el fix (decisión de CC; `_apply_grade` de producción solo avisa): si prefieren avisar y guardar igual, es una línea.
4. El informe del scrub llega a Omar por `/fix_status.reason` y el front lo muestra junto al «✅ lista» (agregado de CC, A2.8).
5. `lab/mapa/hechos.json` / `tests_lab.json` / `tests_collect.json` / `_partes` (F42) siguen nombrando `test_module_137c_fix_recetario.py` y `_build_clipfix_user_prompt`: índices históricos, no se regeneran por tanda.
6. `_fix_core` copia el ítem entero de 03_visual al guion vivo (`dst.update(it)`): el ancla queda la de 03_visual (en Wittenoom difiere en un espacio en ch03 ítem 16).
7. Etapa B: con OK del analista. B1 ≈ US$ 0,105 (3 fotos), B2 ≈ 0,035 + Opus + 1 foto, B3 Opus + foto final + clip (G o K).
