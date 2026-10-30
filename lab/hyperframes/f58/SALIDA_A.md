# F58 — Salida A (texto)

Handoff `lab/hyperframes/f58/HANDOFF_F58_miniaturas_paquetes.md` (md5 `9534c07710504f9270b8ba7ba33ea09c`, verificado; la primera copia en disco, md5 `1d93a6da…`, era una versión vieja por error de copia y se repuso antes de empezar). US$ 0.

## §A3 — el camino de la foto de un paquete (escrito ANTES de programar A3; los números de línea son los de `efbe36e`, antes de los kwargs)

La foto de cada paquete sale del cap 1 por `_render_prompts_seedream` con las 3 anclas (las oraciones literales del gancho que eligió Opus) en UNA llamada de casilleros, igual que producción, con tres diferencias pedidas: sin el bloque del clip de apertura, sin cartel y con una oración de composición. Todo entra por kwargs con default byte-idéntico; **no hace falta cambiar producción más allá de eso → no hay PARADA A3**.

1. **Topic como en producción.** `fase1_5._load_topic_by_id(tid)` (fase1_5.py:139) → `fase1_5.asegurar_canon(tid, topic, log)` (fase1_5.py:289; en producción se llama en fase1_5.py:677 antes de m03) → `topic["_f8"]` armado como `m03_visual.assign_visual_prompts` (m03_visual.py:2153-2158): `beats = v3img.load_beats(topic, STEPS_DIR)`, `year = v3img.topic_year(topic, beats)`, `lang = v3img.place_language(topic)`, `fuentes = mexp.fuentes(tid, STEPS_DIR)`, `anio_prev = {n: mexp.anio_previo(narr_chapters, n)}`. Sin beats (guion v2) `_render_prompts_seedream` levanta `VisualValidationError` (m03_visual.py:632-633): PARADA con ese mensaje.
2. **cap_data** = el cap 1 de `_steps/<tid>/01a_skeleton.json` (`chapters[0]`: `role: hook`, `narrative_intent: hook`, `render_engine: veo`); **narración** = cap 1 de `01b_narration.json` (el GANCHO entero); **plan** = `{"anchors": [{"anchor": a} for a in las 3 anclas]}`.
3. **Reparto a beats como `_f8_refill`** (m03_visual.py:727-739): `f8 = dict(topic["_f8"], refill=True, force_assign=v3img.assign_beats(narracion, anclas, cap_beats))` (m03_imagenes_v3.py:82; funciona porque las anclas son literales). Con `refill=True` NO corren ni el log `_log_sin_period` (m03_visual.py:645-646) ni `_f8_fix_cap` (m03_visual.py:708-709: sin cuerpos en el cap 1, arma, ESTABLISHING); `force_assign` reemplaza a `assign_beats` en m03_visual.py:635-636.
4. **Expediente y bloque extra** sin cambios: `mexp.expedientes` (m03_visual.py:637), `v3img.beats_block` + `mexp.bloque` (m03_visual.py:639-642), `anios` por expediente (m03_visual.py:644).
5. **Pedido de casilleros:** `_build_seedream_prompt_step2(topic, cap_data, narration, anchors, extra, anios, clip_apertura=…)` (m03_visual.py:538-547, 647). Kwarg nuevo `clip_apertura=True`: con `False` no entra `opening_clip_rule` (m03_visual.py:553-561, el bloque «OPENING MOTION CLIP» que hoy entra porque `narrative_intent == "hook"`). `_render_prompts_seedream` lo recibe también como kwarg (`clip_apertura=True`) y lo pasa; con el default, byte-idéntico.
6. **Opus con validación y reintentos de producción:** `_call_with_validation_retry(prompt, _validator, cap_number, system_instruction=SYSTEM_INSTRUCTION_CASILLEROS, response_schema=_casilleros_schema(n), caller=_llamar_casilleros, description="m03:casilleros")` (m03_visual.py:667-669; `_call_with_validation_retry` m03_visual.py:1836, `MAX_RETRY_ATTEMPTS = 3` m03_visual.py:867; `_llamar_casilleros` m03_visual.py:309 → `claude_helpers.call_json` con `MODELO_CASILLEROS` y `ESFUERZO[MODELO_CASILLEROS]`). `CasillerosParada` si Opus no llena (m03_visual.py:670-671).
7. **Después de Opus** (m03_visual.py:672-679): `scrub_slots`, `fix_text_slot`, `_apply_place_exterior_filter` sin cambios. **`sin_cartel=True`** (kwarg nuevo de `_render_prompts_seedream`): antes de armar, `it["text_in_image"]["present"] = False` para cada ítem (así `armar` no pone `frase_cartel` y el cierre lleva `NO_TEXT`, m03_imagenes_v3.py:631-632 y 650; y `_sacar_frases_con_texto` corre con `intentional_text=""`, m03_visual.py:693-694).
8. **Armado:** `v3img.armar(it, anio, grupos, composicion=…)` (m03_visual.py:691; `armar` m03_imagenes_v3.py:624). Kwarg nuevo `composicion=""`: `partes["composicion"] = oracion(composicion)` después de `"tecnica"` (m03_imagenes_v3.py:648) y antes de `"estilo"`; con `""` la parte queda vacía y el prompt es byte-idéntico (`" ".join(p for p in partes.values() if p)`). `COMPOSICION_MINIATURA` vive en m09 y llega por `_render_prompts_seedream(…, composicion=COMPOSICION_MINIATURA)`.
9. **F8 backstop sin cambios:** `v3img.f8_backstop` (m03_visual.py:692; m03_imagenes_v3.py:655): `fix_counts_lr` usa `LR_RE` (m03_imagenes_v3.py:267-269), que NO matchea «fills the right half of the frame» ni «the left half is dark» (sus alternativas exigen «on/to/at/from the … left/right», «left/right-hand/side/third/edge/foreground/background» o «left/right of the frame|corner»): la oración de composición queda intacta (un test lo fija: excepción declarada a D4).
10. **Foto:** `asset_manager._generate_image_raw(prompt, out, use_ultra=False)` (asset_manager.py:312; motor `api.image_engine` = seedream, t2i sin foto madre). `ContentRejectedError` u otro error → el paquete queda sin foto con el motivo literal; los demás siguen.
11. **Salida por paquete:** `prompt` (prosa final), `raw_llm_prompt` (casilleros), `anio`/`anio_fuente`, `_f8_problemas`, `_f8_texto_fuera` (m03_visual.py:695-705), más el path de la foto o el motivo.

Firmas nuevas (defaults byte-idénticos):
- `m03_visual._build_seedream_prompt_step2(topic, cap_data, narration_text, anchors, extra_block="", anios=None, clip_apertura=True)`
- `m03_visual._render_prompts_seedream(topic, cap_data, narration, plan, cap_number, composicion="", sin_cartel=False, clip_apertura=True)`
- `m03_imagenes_v3.armar(it, anio, grupos=None, composicion="")`

## 1. Módulos: antes → después

| módulo | antes | después |
|---|---|---|
| `script_engine/m09_packaging.py` | Gemini: 6 títulos + 6 overlays sueltos (`_META_SYSTEM`) y 3 ideas de foto (`_HERO_SYSTEM`, prompt «SEEDREAM 4.5», sin canon, nombres reales); bases «existentes» de `audit_map.csv` de otro video; leía `data/scripts/<tid>.json` y 10 `verified_facts`; texto partido por palabras (`_wrap_lines`) | **Opus (`MODELO_CASILLEROS`, `ESFUERZO[…]`) en una llamada**: `PEDIDO_PAQUETES` (byte a byte el del handoff; un test lo extrae del .md y compara) con el GANCHO (cap 1 entero), `[Cap N]` 2–7 sin truncar y el POOL completo (D/T/citas con `linea_cita`/P/L, ids tal cual; `cifras_canonicas` al final si viene); `ESQUEMA_PAQUETES`; validación por código con `MAX_RETRY_ATTEMPTS` (n exacto, campos llenos, estrategias distintas, ancla literal del gancho con espacios normalizados, anclas distintas) → `PaquetesParada` si fallan todos; después `titulo[:MAX_TITLE_CHARS]`, `.upper()`, `_truncate_tags`, `with_icon_credit`. Entradas de `_steps/<tid>/` (`01b_narration.json`, `00_pool_v3.json`, `01a_skeleton.json`), falta → `PaquetesParada` con la ruta. **Foto por producción** (`topic_produccion` = `_load_topic_by_id` + `asegurar_canon` + `_f8`; `prompts_paquetes` → `_render_prompts_seedream(…, 1, composicion=COMPOSICION_MINIATURA, sin_cartel=True, clip_apertura=False)` con `refill=True` + `force_assign`; `foto_paquete` → `_generate_image_raw(prompt, out, use_ultra=False)`, error → motivo literal). **Cifras por código** (`numeros_pool`, `avisos_cifras`: «⚠ cifra sin dato: N»). **Texto por ancho** (`partir_texto`, `ancho_linea` con `textbbox` + borde; zona 584 px; de 108 a 75 px de a 1; «⚠ no cabe»). `N_PAQUETES = 3` (reemplaza a `FRESH_THUMBS`). Borrados: `_META_*`, `META_TEMP`, `generate_metadata`, `_meta_user_prompt`, `_HERO_*`, `generate_hero_prompt(_iter)`, `_narration_for_hero`, `HERO_NARRATION_PER_CAP`, `_gemini_json`, imports `gemini_client`/`gt`/`DOCTRINE_*`, `GANCHO_INSTRUCCION`, `_bloque_gancho`, `_load_canonical`, `shortlist_existing`, `SHORTLIST_EXISTING`, `_resolve_png`, `audit_map.csv`, `_wrap_lines`, `_generate_fresh`, `_render_concept_variations`, `_record_iteration`/`_load_iterations`, `--only-fresh`, `--skip-fresh`, `--title N` (→ `--compose --paquete N`). `run_candidates(tid, video_path=None, review=False)` se mantiene; `candidates_ready` exige `paquetes`; `metadata.json.paquetes` acumula con índice global |
| `script_engine/m09_review_server.py` | grilla existing/fresh, panel de crítica al hero, borrar candidatas | 3 paquetes terminados (miniatura, título con cuenta, texto, `id: texto`, `cap_que_paga`, ancla, avisos); editar título/texto (recompone sin red), elegir otra base (`bases_del_video`: `*_graded.png` o la cruda), «rehacer foto» (A3 solo esa ancla), «3 paquetes nuevos» (sin pisar números); `/img` solo dentro de `assets/`, `thumb_candidates/`, `publish/`; `--auto-first` sigue (sin paquetes, genera) |
| `script_engine/m03_visual.py` | `_build_seedream_prompt_step2(…, anios=None)`; `_render_prompts_seedream(…, cap_number)` | `clip_apertura=True` / `composicion=""`, `sin_cartel=False`, `clip_apertura=True` (§A3). Defaults byte-idénticos (test contra `git show HEAD:` sobre Wittenoom real) |
| `script_engine/m03_imagenes_v3.py` | `armar(it, anio, grupos)` | `armar(…, composicion="")`: `partes["composicion"]` después de `tecnica`; vacía → prompt byte-idéntico (78 ítems reales de Wittenoom) |
| `script_engine/video_prompt.py` + `asset_manager.py` | `PEDIDO_FINAL` con «APPROVED MOTION»; `armar_body_final`/`escribir_final` con `video_prompt_aprobado` | A8: `PEDIDO_FINAL` sin el movimiento (abajo); el parámetro sale de las dos; `foto_final_del_clip` mantiene su firma y ya no lo pasa |
| tests | `test_m09_packaging.py`, `test_m09_review_server.py`, `test_fase3.py` (`--only-fresh` → `--review`), `test_module_f57.py` (copia de `PEDIDO_FINAL`), `test_module_f51a.py:21` (lista de claves de `partes` + `composicion`) | adaptados; nuevos `test_module_f58.py` (31 + 1 xfail) y `test_module_f58_a3.py` (9) |

## 2. El usuario de A2 armado para Wittenoom

Entero en `lab/hyperframes/f58/pedido_paquetes_wittenoom.txt` (copia literal de `armar_pedido`, lo escribe el test): **59 008 caracteres, 436 líneas**: PEDIDO + GANCHO (834 caracteres, los 2 párrafos del cap 1) + NARRACIÓN `[Cap 2]`…`[Cap 7]` sin truncar + POOL de 362 líneas (D 155 · T 98 · Q 50 · P 35 · L 24; `cifras_canonicas` vacío → nada). Empieza y termina así:

```
Armás el empaquetado de un video documental de historia oscura en español neutro-latino: el título de YouTube, el texto que va sobre la miniatura y la oración del gancho que muestra la foto de la miniatura. Todo sale del material de abajo: un dato que no está en el POOL no existe.

Devolvé 3 PAQUETES. Cada paquete es una unidad: título, texto de la miniatura y foto. Cada paquete usa una estrategia distinta, elegida de esta lista: (1) dato brutal o cifra, (2) misterio o pregunta, (3) acusación, (4) lugar y año, (5) contradicción o ironía histórica, (6) consecuencia humana.

Por paquete:
- estrategia: el número de la lista.
- titulo: hasta 70 caracteres, con el gancho al principio. Toda cifra, fecha o nombre sale tal cual de un ítem del POOL.
- dato_ids: los ids de los ítems del POOL de los que salen el título y el texto.
- texto: de 2 a 4 palabras en MAYÚSCULAS para encima de la miniatura. No describe la foto ni repite el título: abre una pregunta que solo el video responde.
- cap_que_paga: el número del cap cuya narración responde el texto.
- ancla: la oración del GANCHO que muestra la foto, copiada tal cual; una oración distinta en cada paquete.

descripcion: de 150 a 300 palabras. La primera oración es el gancho, sin mentir; después, contexto fiel al material y una línea de cierre del canal.
tags: la mayoría en español y de 3 a 5 en inglés; los nombres propios sirven en los dos idiomas; entre todos, hasta 450 caracteres.

GANCHO (la narración del cap 1 entera; la primera or
[…]
esto.
L16: Perth — La gran ciudad más cercana a Wittenoom, a unos 1.400 kilómetros.
L17: Madrid — Ciudad de origen de las familias Écija y De Juan antes de emigrar
L18: Círculo de Bellas Artes — Lugar donde se conocieron María Bernal y Daniel Écija
L19: Roebourne — Puerto costero
L20: Meekatharra — Cabecera de ferrocarril
L21: Port Samson — Puerto para exportación de asbesto
L22: Mount Isa Mines — Mina que sirve de comparación por sus estrictas normas de seguridad, en contraste con ABA.
L23: Millstream aquifer — Acuífero y fuente de agua municipal alimentada por el río Fortescue
L24: Karratha — La ciudad más grande del noroeste que utiliza el agua del acuífero Millstream

[59008 caracteres]
```

## 3. La tabla de A5 que sale de los tests (Anton bundleada; Pillow 12.2.0, layout BASIC, sin raqm)

| texto | líneas | anchos con borde (medidos) | handoff | px |
|---|---|---|---|---|
| LOS DEJARON MORIR | LOS DEJARON / MORIR | 544 / 276 | 545 / 277 | 108 |
| ¿QUIÉN SABÍA EL PELIGRO? | ¿QUIÉN SABÍA / EL PELIGRO? | **550 / 499** | 553 / 501 | 108 |
| ¿POR QUÉ NO LIMPIARON? | ¿POR QUÉ NO / LIMPIARON? | 529 / 502 | 530 / 503 | 108 |
| BORRADA DEL MAPA | BORRADA / DEL MAPA | 380 / 417 | 381 / 417 | 108 |
| 3 MILLONES DE TONELADAS | 3 MILLONES / DE TONELADAS | 486 / 582 | 486 / 583 | 108 |
| JUGABAN CON VENENO | JUGABAN / CON VENENO | 379 / 499 | 380 / 499 | 108 |
| 1.269 DE 1.328 HABITANTES MURIERON | — (1.269 DE 1.328 / HABITANTES MURIERON = 426 / 644 > 584) | no cabe | no cabe | ⚠ 75 |

Líneas y px: idénticos a la tabla en las 7 filas. Anchos: ±1 en 6; la fila «¿QUIÉN SABÍA…» da −3/−2 px (medición de Pillow en esta máquina, no lógica): queda como `xfail(strict=True)` en `test_module_f58.py` con la razón escrita; si en otra máquina da 553/501 el test lo muestra. No se inventó tolerancia.

## 4. A8: `PEDIDO_FINAL` antes → después

Antes (F57) tenía, después de la narración, el bloque «APPROVED MOTION (where the camera ends up): {video_prompt_vivo}» y la segunda línea terminaba «…following the narration and the approved motion.». Después (byte a byte el del handoff):
```
You write an edit instruction for an image-editing model. The attached image is the first frame of a {segundos}-second continuous documentary shot. Write the instruction that turns it into the last frame of that same shot.
The last frame keeps the same place, the same people with the same faces, bodies and clothes, the same light and the same photographic style; it changes only what changes during those seconds, following the narration.
STILL IMAGE PROMPT (what the first frame was asked to show):
{prompt_foto}
NARRATION DURING THE SHOT (Spanish; the last frame shows the moment at its end):
{voz_clip}
Return only the edit instruction: one paragraph of plain English prose describing the last frame.
```
`armar_body_final(foto, image_prompt, voz_clip)`, `escribir_final(foto, image_prompt, voz_clip, *, post, description)`; `asset_manager.foto_final_del_clip` conserva su firma (recibe `video_prompt_aprobado` y ya no lo usa para la instrucción). **Sí cambia la foto final de los clips de producción** (la instrucción ya no ve el movimiento).

## 5. Lo viejo de Wittenoom

`output/123bbb64-…/publish/`: `metadata.json`, `metadata_candidatos.md`, `hero_iterations.json`, `thumb_final_01.png`, `thumb_final_02.png` y `_qa_backups/` **movidos** a `publish/_antes_f58/` (no borrados). Quedan `CHECKLIST_PUBLICACION.md` y `thumb_candidates/` vacío (las `existing_*`/`fresh_*` viejas ya estaban en `_qa_backups/`, que se movió entero).

## 6. Suites

`bash lab/hyperframes/f41/verificar.sh f58` (logs en `lab/hyperframes/f41/f58/`): ch02 md5 **`f792f3d483a1fa42daed5f7f0e054f46`** (candado); rápida **53 passed**; amplia (segunda corrida, después de adaptar 2 tests viejos de m09): **1194 passed + 1 xfailed** + 4 fallas, las 4 previas (`m03_merge_timing` ×2, `gfx_lab` ×2). La primera corrida de la amplia tuvo 2 fallas más, de tests que ejercitaban lo borrado: `test_module_f54::test_m09_gancho_primero_y_cap_1_sin_truncar` (el B.4 del camino Gemini viejo; se borró con una nota: el GANCHO entero primero lo cubre `test_module_f58` A2) y `test_module_gfx_auto_icons::test_credito_en_la_descripcion` (`_normalize_metadata` → `normalizar_paquetes`). `python lab/tools/mapa_modulos.py --check`: 158 archivos · **0 fallas**; stickers de los 6 módulos al día. Tests nuevos: `test_module_f58.py` 31 + 1 xfail, `test_module_f58_a3.py` 9; con `test_m09_*`, `test_fase3`, `test_qa_studio`, `test_module_f57`, `f51a`, `f53b*`: 141 passed.

**PARADA A.** La Parte B (Wittenoom real) no arranca sin el OK del analista a la Parte A.
