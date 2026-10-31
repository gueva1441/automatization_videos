# SALIDA F60 Etapas B + C — madre por persona + secuencia en producción (caps flux y caps con clip)

Fecha: 2026-10-30 · rama `f11-guion-v4` · handoff `HANDOFF_F60_BC_madre_secuencia_prod.md` (md5 ec7ae49fce9d199a535828197a58db92, verificado) sobre `HANDOFF_F60_madre_personas_secuencia.md` §Etapa B/C · PARADA B+C: nada de producción de Wittenoom sin OK de Omar.

## 1. Código (Etapa B)

### `asset_manager.py` (CRLF)
- Constantes nuevas, con origen en el comentario: `FAL_SUBMIT_TIMEOUT_S = 60` (el literal de `_call_clip_once`, que ahora lo usa), `FOTOS_POR_LLAMADA = 6` (DECISIONES 18:34), `SECUENCIA_DIR = "_secuencia"`.
- `_clip_poll` → `_fal_queue_poll` (mismo cuerpo; docstring con el rename). Único llamador de producción (`_call_clip_once`) actualizado. Sin alias: `lab/hyperframes/f60/etapa0b_secuencia.py` queda roto (importa `am._clip_poll`) y no se re-corre. `_flux_poll` no se toca.
- `_iter_image_items` devuelve además `anio` (str sin espacios o None) y `cartel` (`text_in_image.present`); `persona` ahora pasa por `_norm_persona`.
- **Filtro por era** `persona_aporta_madre(canon_persona, anio)`: año = primer número de 4 dígitos de `anio` (`_anio_entero`); tramos con `m03_visual._tramo` (import perezoso). No aporta solo si el año cae fuera del tramo de `era` **y** dentro de un tramo de `condition_by_period` que no se cruza con la era. `era`/`anio`/`years` ilegibles → aporta; sin canon → aporta.
- **Regla única** `_madres_para_item(persona, foto_madre_refs, anio, registry, personas_canon) → [(ref, path)]`: madres de `persona` en orden (solo las que aportan por era y existen en el registry) + `foto_madre_ref`, sin repetir, tope 2 (el de `_norm_foto_madre_refs`). La usan `_process_flux_chapter`, el pre-paso, las supps, la foto inicial del clip y QA.
- **Pre-paso de secuencia** `_pre_paso_secuencia(chapters, video_id, registry, personas_canon)`: una vez en `process_script`, antes del bucle de caps. `_items_para_secuencia` lista image_prompts de caps flux y supps de caps con clip (orden de guion). Entran los ítems sin archivo en disco, `len(persona) == 1`, `persona[0]` con madre que aporta, `foto_madre_ref == []`, sin cartel. Agrupados por persona, lotes de `FOTOS_POR_LLAMADA`; un lote de 1 foto no se pide (camino de una foto). Todos los lotes a la vez (`ThreadPoolExecutor`, tope `FLUX_MAX_WORKERS`). Devuelve `{(cap_id, "img"|"supp", idx): {status: "ok_secuencia", persona, lote, path, foto_madre_refs, segundos_lote}}`. Lote fallido → aviso y sus fotos van por una foto; lote incompleto → las no devueltas van por una foto.
- `_llamar_secuencia(video_id, prompts, refs, madre_paths, out_paths)`: `/edit` del perfil Seedream por `api.fal_base_url` (queue.fal.run) con `_seedream_edit_payload_for` + `max_images = N` + `sequential_image_generation = "auto"`, submit con `FAL_SUBMIT_TIMEOUT_S`; `request_id/status_url/response_url` a `output/<vid>/_secuencia/pedidos.json` (clave = md5 de prompts + refs en orden) **antes** de esperar con `_fal_queue_poll`; si la clave ya tiene `request_id`, reanuda sin re-pedir. Baja las imágenes devueltas (imagen i → out_path i) y registra N en el costo con `cost_tracker.track_seedream(images=N, mode="edit")` (tarifa del perfil 0,035; fal no devuelve el costo en la respuesta).
- `_prompt_secuencia(prompts)`: el prompt de la Etapa 0 (una escena por línea, sin la frase de aspecto ni `NO_TEXT`, que van una vez al final). **Declarado:** «the same **person** shown in the reference image» en vez de «man» (0b era solo Daniel; la madre puede ser de una mujer o de un niño).
- `_process_flux_chapter(chapter, video_id, registry, personas_canon=None, secuencia=None)`: ítems del pre-paso → `status: "ok_secuencia"` con `persona`, `lote`, `segundos_lote` (no `skipped_exists`), donantes del piso anti-desync; el resto con las madres de la regla única. Todas las entradas del manifest llevan `persona`.
- `_generate_supplementals_for_veo_chapter(..., registry=None, personas_canon=None, secuencia=None)`: supp del pre-paso → `ok_secuencia`; las demás con las madres de la regla única (`foto_madre_data_uris` solo si hay madres) y `foto_madre_refs` en el resultado.
- `_process_veo_chapter(chapter, video_id, registry=None, personas_canon=None, secuencia=None)`: la foto inicial del clip lleva las madres leídas de `chapter["image_f8"]` (persona/anio; `foto_madre_ref` no viene en image_f8 → []); solo para la primera foto del cap. La foto final sigue saliendo por `/edit` desde la inicial (F57).
- `process_script`: lee `foto_madre_personas` del contrato, corre el pre-paso una vez y pasa registry + personas + secuencia a los dos procesadores.

### `foto_madre.py` (LF)
- `ROPA_MADRE = "wearing a plain, clean, light-coloured shirt"` (Omar 17:48) y `MADRE_PERSONA_MIN_FOTOS = 2` (analista, handoff base) a producción; `STEPS_DIR` (patcheable) para leer `03_visual.json`.
- `_fotos_del_guion(visual)`: todas las fotos en orden de guion (image_f8, image_prompts, supps) con `persona`, `anio`, `people_group`. `_fotos_con_madre_de(person, fotos)`: nombre en `persona` (cualquier posición) **y** aporta por era. `_grupo_mas_frecuente`: people_group más frecuente sobre esas fotos; empate → el primero en orden de guion.
- `_prompt_persona(person, appearance_grupo)`: el prompt del punto 2 del handoff, en código, sin LLM, sin `_STYLE` («faceless»), sin `condition_by_period`; año de la madre = primer número de 4 dígitos de `era` (sin número → `ESTILO_C` sin «taken in {anio}»). Sin PARÁ de B.1: `appearance_canon` ya es solo el aspecto fijo (A3).
- `_generate_madre_seedream(prompt, dest)`: Seedream t2i del perfil (`select_profile("seedream")`, image_size 2560×1440) por la cola de fal (`FAL_SUBMIT_TIMEOUT_S`, `_fal_queue_poll`), PNG real, `track_seedream(images=1)`. Rechazo → `ContentRejectedError`, **no cae a GPT**.
- `generate_fotos_madre_personas(topic, video_id, visual=None)`: para cada `documented_people` con ≥ 2 fotos que aportan: skip si `foto_madre` existe, adopción manual si el archivo está, aviso y sin madre si `api.image_engine != "seedream"`, madres de distintas personas a la vez (tope `FLUX_MAX_WORKERS`), error → `foto_madre = ""` + aviso. Devuelve `{nombre: {estado, fotos, fotos_ids, prompt, dest, …}}`. `generate_foto_madre_for_topic` la llama al final (y ya no retorna temprano cuando el sujeto es `person/other`: las madres de persona salen igual). paso0 corre en fase1_5 **después** de m03 → `03_visual.json` existe.

### `script_engine/m06_assembler.py` (CRLF)
- Registry + `{name: foto_madre}` de cada `documented_people` con madre; nuevo campo del contrato `foto_madre_personas = {name: {era, condition_by_period}}` (lo que asset_manager necesita para el filtro por era sin leer topics_db).
- Caps con clip: `cap_out["image_f8"] = vis["image_f8"]` si existe (antes solo viajaba `image_prompt`; `persona` de la foto del clip se perdía).

### `fase2a.py` (LF) — el adaptador m06 → asset_manager (`_normalize_long`)
- Caps veo: `norm_ch["image_f8"] = ch.get("image_f8") or {}`; el script normalizado lleva `foto_madre_personas`. Nada más cambia.

### `qa_studio_server.py` (CRLF)
- `resolve_fix_entry` devuelve `persona` (lista normalizada; no editable).
- `_uris_madres(state, entry, …)`: la regla única (`asset_manager._madres_para_item`) contra `foto_madre_registry`/`foto_madre_personas` del guion vivo; solo lee `entry`.
- `_fix_core` (paso 8) la usa en vez del bucle propio sobre `foto_madre_ref`; parámetro inyectable `madres_fn`. El texto a Omar agrega «Foto anclada a la madre de X (casillero persona: no cambia con el pedido)» cuando se usó una madre de persona.
- `_reseed_core` también la usa (parámetros `madres_fn`, `data_uri_fn`); **declarado:** antes el reseed salía siempre t2i aunque el ítem tuviera `foto_madre_ref`; ahora lleva las mismas madres que producción.

### Etapa C — funciones tocadas
`process_script`, `_generate_supplementals_for_veo_chapter`, `_process_veo_chapter`, el pre-paso (`_pre_paso_secuencia`/`_items_para_secuencia`/`_llamar_secuencia`, nuevas), el adaptador (`fase2a._normalize_long`) y m06. Ninguna otra función de producción: sin PARÁ.

### Tests
`test_module_f60_bc.py` (30): filtro por era (dentro / fuera / fuera sin condition / era ilegible / year vacío / condition que se cruza con la era), regla única (orden, tope 2, sin registry, fuera de era, archivo inexistente), agrupación 7 → 6 + 1 y lote de 1 → una foto, exclusiones (2 personas, cartel, foto_madre_ref, ya en disco, fuera de era), lote incompleto y lote fallido → una foto, `ok_secuencia` en el manifest y donante del piso, `_llamar_secuencia` (pedido en disco antes de esperar, payload, N en el costo, reanudar sin re-pedir, clave nueva si cambian los ítems), prompt de secuencia, supps de caps con clip (secuencia / madres / lista cruda), foto inicial del clip con `image_f8` (1962 sí / 1991 no / sin image_f8 no), m06 + adaptador, madre de persona (prompt byte a byte de Daniel, grupo más frecuente, ≥ 2 fotos, rechazo sin GPT, skip/adopción, motor ≠ seedream, lectura de `_steps`, `_generate_madre_seedream` por la cola), QA reseed y fix con persona (orden, texto a Omar, `persona` no editable), rename y constantes, `_iter_image_items`.
Tests previos que tocan las firmas cambiadas: f57, qa_studio, f5e, foto_madre_prompts, m06_autopass, f41_cadena, f50b, f60_a3 → 113 verdes sin cambios. `test_module_veo_supplementals.py` (script) → GATE 2 PASS.

### Constantes usadas (todas de la tabla del handoff)
fotos por llamada = 6 (DECISIONES 18:34) · madres por llamada ≤ 2 (`_norm_foto_madre_refs`) · madre si ≥ 2 fotos dentro de su era (analista base + filtro Omar 20:29) · espera de la cola = `CLIP_POLL_TIMEOUT` 600 s · `ROPA_MADRE` (Omar 17:48) · 0,035 US$/imagen (perfil Seedream / `pipeline.costs`; fal no devuelve el costo en la respuesta) · submit a la cola = `FAL_SUBMIT_TIMEOUT_S` 60 (literal de `_call_clip_once`) · año de la madre = primer número de 4 dígitos de `era`. Ningún número nuevo.

### Declaraciones (lo que el handoff no fija y CC decidió; todo reversible)
1. «Tramo de `condition_by_period` fuera de su era» = tramo que **no se cruza** con el tramo de `era` (sin intersección). Un tramo que se solapa parcialmente con la era (p. ej. 1963-1965 con era 1962-1963) no excluye. Es la lectura más conservadora; la otra (cualquier año fuera de la era que caiga en un condition) está a una línea.
2. Prompt de secuencia: «the same **person**» (el de 0b decía «man»).
3. `foto_madre_personas` es un campo nuevo del contrato (m06 → fase2a → asset_manager): el handoff pide registry `{nombre: foto_madre}` y «filtro por era» en asset_manager; sin el campo, asset_manager tendría que leer topics_db (el seam de 128).
4. `_iter_image_items` suma `cartel` además de `anio` (el pre-paso necesita `text_in_image.present`).
5. El manifest lleva `persona` en cada entrada de foto (ok, skipped, ok_secuencia) y `lote`/`segundos_lote` en las de secuencia.
6. `_reseed_core` ahora lleva madres (antes salía t2i siempre).
7. `lab/hyperframes/f60/etapa0b_secuencia.py` queda roto (importa `_clip_poll`); no se re-corre. La Etapa X corrió antes del rename con `getattr(am, "_fal_queue_poll", None) or am._clip_poll`.
8. En la prueba, el pedido `madre si ≥ 2 fotos» cuenta sobre las fotos que aportan por era (el handoff: «contado sobre esas mismas fotos»).

### Suites (lab/hyperframes/f41/f60bc/)
ch02 md5 `f792f3d483a1fa42daed5f7f0e054f46` (candado) · rápida 53 passed, 3 skipped · amplia **1331 passed**, 31 skipped, 3 xfailed, 4 failed = las 4 previas (`m03_merge_timing` ×2, `gfx_lab` ×2). Stickers ×5 (fase2a: foto_madre, m06, fase2a; orquestador: asset_manager, qa_studio), MAPA 158 archivos · 0 fallas.

## 2. Prueba en la copia (`lab/hyperframes/f60/etapa_bc_prueba.py` → `bc/`)
Entradas: canon `a3/05_visual_canon_a3.json` inyectado al topic (CANON_KEYS) y `a3/03_visual_a3.json` copiado a `base/data/scripts/_steps/<tid>/03_visual.json` (el anterior respaldado en `bc/03_visual_copia_antes.json`; el guion de la copia en `bc/guion_copia_antes.json`). Rutas parcheadas: `foto_madre.OUTPUT_DIR/STEPS_DIR`, `asset_manager.OUTPUT_DIR`, `m06.STEPS_DIR/SCRIPTS_DIR/_load_topic`; `config` intacto; `save_db` no se llama; `cost_tracker.start_video("f60_bc_lab")`. **`process_script` no se llamó**: madre → m06 → `fase2a._normalize_long` → `_pre_paso_secuencia` → camino de una foto ítem por ítem (`_generate_flux_image_at` con `_madres_para_item`), solo las 33 fotos con `persona`. Cero clips. `output/` propio y fresco en `bc/output/` (todas las fotos con persona se generaron). Corrida en seco previa (`--dry`, fal mockeado) dio la misma tabla.

### Madres (53,1 s de pared, 8 a la vez; Seedream v5 Lite t2i por la cola, 2560×1440, nsfw None)
| persona | fotos que aportan | estado |
|---|---|---|
| Daniel Écija | 12 (ch01_f8_01, ch01_supp_01, ch01_supp_02, ch02_img_01/02/04/05, ch03_img_16, ch04_img_09/10/13, ch05_img_05) — **sin ch05_img_13 (1991)** | ok |
| María Bernal | 9 | ok |
| Víctor Calvo | 6 | ok |
| Milagros Barroso | 5 | ok |
| Ramón de Juan | 4 | ok |
| Eric Saint | 2 | ok |
| Mercedes | 2 (1963, 1971; era 1962-1971) | ok |
| Maitland Parker | 2 | ok |
| Hancock, Wright, John Patrick, Daniel Écija hijo, James Vernon, Marcos Orellana, Melita Markey | 1 | sin madre (< 2) |
| Chifley, McNulty, Davidson, Major, Peter Gordon, Court, Ben Wyatt | 0 | sin madre |

Coincide con la simulación del auditor (Daniel 13 → 12 con madre; sin madre solo la de 1991; las 8 personas con madre son las mismas). Prompt real de Daniel (byte a byte el de la tabla del handoff con `appearance_canon` A3 y el `people_group` más frecuente `spanish_migrant_families`):
```
Head-and-shoulders portrait of a mid-20s Spanish man, wearing a plain, clean, light-coloured shirt. Southern European features, with light olive to tanned skin, dark brown or black hair that is straight to wavy, brown eyes, and slim to medium builds. Neutral expression, facing the camera, plain mid-grey background, soft even light. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight underexposure, in a dark-history realist style. No readable text, no signage, no labels.
```
Hoja de madres: `bc/hoja_madres.jpg`.

### Secuencia (pre-paso, 180,3 s de pared, 3 lotes a la vez; `bc/output/<tid>/_secuencia/pedidos.json`)
| lote | fotos pedidas / devueltas | s | request_id |
|---|---|---|---|
| Daniel Écija#1 | 2 / 2 (ch01_supp_02, ch04_img_10) | 118,6 | 01a18fba-3670-7e73-8b89-a800cbc32a0b |
| Eric Saint#1 | 2 / 2 (ch03_img_04, ch03_img_06) | 140,9 | 01a18fba-3b72-7e20-b210-0a827d23ab6c |
| Víctor Calvo#1 | 4 / 4 (ch02_img_08, ch02_img_10, ch02_img_14, ch04_img_02) | 180,3 | 01a18fba-3be4-78c3-becc-14a7559af20d |

Los lotes cruzan caps (Daniel junta `ch01_supp_02` con `ch04_img_10`, como pedía el handoff). **Fotos que la cola no devolvió: ninguna** (8/8); sin caídas al camino de una foto; sin errores ni reintentos. Daniel tiene 12 fotos con madre pero solo 2 con `len(persona) == 1`: las otras 10 llevan a María o a Ramón → camino de una foto con 2 madres.

### Tabla foto → camino → lote → tiempo (33 fotos con `persona`; 25 por una foto en 88,6 s de pared)
| foto | persona | año | camino | madres | lote | s |
|---|---|---|---|---|---|---|
| ch01_img_01 (foto inicial del clip) | Daniel | 1962 | una foto /edit | Daniel | – | 41,8 |
| ch01_supp_01 | Daniel, María | 1962 | una foto /edit | Daniel, María | – | 49,9 |
| ch01_supp_02 | Daniel | 1962 | **secuencia** | Daniel | Daniel#1 | 118,6 |
| ch02_img_01 | Daniel, María | 1961 | una foto /edit | Daniel, María | – | 43,2 |
| ch02_img_02 | Daniel, María | 1962 | una foto /edit | Daniel, María | – | 43,4 |
| ch02_img_04 | Daniel, María | 1962 | una foto /edit | Daniel, María | – | 45,9 |
| ch02_img_05 | María, Daniel | 1962 | una foto /edit | María, Daniel | – | 44,1 |
| ch02_img_06 | Milagros, Ramón | 1962 | una foto /edit | Milagros, Ramón | – | 52,3 |
| ch02_img_07 | Milagros, Ramón | 1962 | una foto /edit | Milagros, Ramón | – | 50,0 |
| ch02_img_08 | Víctor | 1962 | **secuencia** | Víctor | Víctor#1 | 180,3 |
| ch02_img_10 | Víctor | 1962 | **secuencia** | Víctor | Víctor#1 | 180,3 |
| ch02_img_11 | Víctor, Milagros | 1962 | una foto /edit | Víctor, Milagros | – | 50,6 |
| ch02_img_14 | Víctor | 1962 | **secuencia** | Víctor | Víctor#1 | 180,3 |
| ch02_img_15 | Ramón, Milagros | 1962 | una foto /edit | Ramón, Milagros | – | 53,2 |
| ch03_img_03 | Hancock, Wright | 1943 | una foto t2i (sin madre en registry) | – | – | 40,0 |
| ch03_img_04 | Eric Saint | 1948 | **secuencia** | Eric Saint | Eric Saint#1 | 140,9 |
| ch03_img_06 | Eric Saint | 1948 | **secuencia** | Eric Saint | Eric Saint#1 | 140,9 |
| ch03_img_16 | Daniel, María | 1962 | una foto /edit | Daniel, María | – | 52,5 |
| ch04_img_02 | Víctor | 1963 | **secuencia** | Víctor | Víctor#1 | 180,3 |
| ch04_img_03 | Víctor, Mercedes | 1963 | una foto /edit | Víctor, Mercedes | – | 73,2 |
| ch04_img_09 | Daniel, Ramón | 1962 | una foto /edit | Daniel, Ramón | – | 47,4 |
| ch04_img_10 | Daniel | 1962 | **secuencia** | Daniel | Daniel#1 | 118,6 |
| ch04_img_11 | Milagros, John Patrick | 1963 | una foto /edit | Milagros | – | 41,3 |
| ch04_img_12 | María | 1963 | una foto /edit | María | – | 52,9 |
| ch04_img_13 | María, Daniel | 1963 | una foto /edit | María, Daniel | – | 68,3 |
| ch05_img_01 | James Vernon | 1966 | una foto t2i (sin madre en registry) | – | – | 40,2 |
| ch05_img_05 | Daniel, María | 1966 | una foto /edit | Daniel, María | – | 50,6 |
| ch05_img_06 | Mercedes | 1971 | una foto /edit | Mercedes | – | 46,6 |
| ch05_img_09 | Daniel Écija hijo | 1985 | una foto t2i (sin madre en registry) | – | – | 38,8 |
| **ch05_img_13** | Daniel | **1991** | **una foto t2i — sin madre por era** | – | – | 36,6 |
| ch06_img_05 | Melita Markey | 2023 | una foto t2i (sin madre en registry) | – | – | 27,2 |
| ch07_supp_07 | Maitland Parker, Marcos Orellana | 2023 | una foto /edit | Maitland Parker | – | 46,8 |
| ch07_supp_08 | Maitland Parker | 2023 | una foto /edit | Maitland Parker | – | 34,2 |

`[Milagros, John Patrick]` y `[Maitland Parker, Marcos Orellana]` fueron por una foto con una sola madre (el otro no la tiene), como pide el handoff. Daniel 1991 salió t2i sin madre (filtro por era) y la foto muestra un hombre mayor de espaldas frente a la radiografía: correcto.

### Costo real (cost_tracker, `video_id` de lab `f60_bc_lab`)
41 imágenes × 0,035 = **US$ 1,435**: t2i 13 (8 madres + 5 fotos sin madre) = 0,455; /edit 28 (8 por secuencia en 3 llamadas + 20 por una foto) = 0,98. Etapa X aparte: US$ 0,105. Total de la tanda **US$ 1,54**.

### Producción intacta
mtimes antes = después de `data/topics_db.json`, `data/scripts/<tid>.json`, `data/scripts/_steps/<tid>/` y `output/<tid>/` (`etapa_bc.json: produccion_intacta: true`). Todo lo escrito está en `lab/hyperframes/f60/bc/` y en la copia `base/` (03_visual y guion de la copia, con respaldo).

## 3. Dos miradas por foto
Hojas por persona (madre + sus fotos, etiqueta archivo · camino · año): `bc/hoja_daniel_cija.jpg`, `hoja_mar_a_bernal.jpg`, `hoja_v_ctor_calvo.jpg`, `hoja_milagros_barroso.jpg`, `hoja_ram_n_de_juan.jpg`, `hoja_eric_saint.jpg`, `hoja_mercedes.jpg`, `hoja_maitland_parker.jpg`.

### Mirada 1 (CC)
**Madres.** Las 8 son busto, camisa clara, fondo gris, luz pareja, sin texto. Daniel (mid-20s), Ramón (≈30), Eric Saint (≈50), Maitland Parker (anciano aborigen) a la edad del canon. **Víctor Calvo** («a young Spanish boy») salió de ≈15 años y **Mercedes** («a young Spanish girl») de ≈13: el canon A3 no da edad numérica a los niños y «young boy/girl» rinde adolescente; en las escenas, en cambio, salen de ≈8-10 (el prompt de escena manda), así que la madre ancla menos para ellos. María y Milagros son dos «young adult Spanish woman» y se parecen bastante entre sí (mismo tipo del canon): en `ch02_img_06` (veranda, Milagros + Ramón) las dos mujeres parecen la misma persona.

**Daniel (12 fotos con madre).** Cara frente a la madre: ch01_supp_01 8, ch01_supp_02 (secuencia, de espaldas mirando atrás) 7, ch02_img_01 (baile, lejos) 6, ch02_img_02 (boda, lejos) 6-7, ch02_img_05 (barco, perfil) 8, ch03_img_16 (avión, lejos) 5, ch04_img_09 (mina, con casco) 6, **ch04_img_10 (secuencia, grupo de mineros) 8** —es claramente la madre y los demás mineros tienen otras caras—, **ch04_img_13 (bautizo) 8**, ch05_img_05 (Madrid, lejos) 6; ch02_img_04 de espaldas y ch01_img_01 solo el pie (no se puntúan). Promedio ≈ 7 en las que se ve la cara; en 0b (Daniel solo, lotes de 6) andaba 8-10 de frente: las fotos con dos madres y las de plano abierto bajan la nota. Contagio: no vi al segundo hombre con la cara de Daniel (ch04_img_09: el otro minero es mayor; ch04_img_10: caras distintas). La venda: en las fotos de secuencia sale como venda (supp_02, img_10); en las de una foto sale como **yeso blanco entero** (ch01_img_01, supp_01, ch04_img_13) — el prompt dice «bandaged» y Seedream lo lee como escayola; no es de B/C pero vale anotarlo.
**María (9).** supp_01 7, boda 7, barco 7-8 (pañuelo), hospital `ch04_img_12` 8 (embarazada, enfermera), bautizo 8, baile/avión/Madrid lejos 5-6, barco de espaldas.
**Víctor Calvo (6).** Las 4 de secuencia tienen **la misma cara entre sí** (niño ≈10: barco, cubierta, pista, jugando con fibra) y 7 frente a la madre (más joven que ella). `ch02_img_11` durmiendo 6, `ch04_img_03` 7. Anacronismos: `ch04_img_02` **aparato de aire acondicionado** en la pared de la casa; `ch04_img_03` **camión volquete moderno** (cabina actual).
**Milagros (5) / Ramón (4).** Veranda `ch02_img_06`: Milagros 7, Ramón 7, pero el cuarto comensal tiene **la cara negra de polvo** (lee como pintura, no como polvo) y las dos mujeres son casi iguales (contagio María/Milagros por tipo). `ch02_img_07` y `ch02_img_15` lejos 6; `ch04_img_11` Milagros con el bebé 8; `ch04_img_09` Ramón 5 (sale mayor y con casco).
**Eric Saint (2, secuencia).** 8 y 8, la misma cara en las dos; avioneta monomotor de 1948 plausible; traje y sombrero de época.
**Mercedes (2).** `ch04_img_03` niña ≈8 frente a madre ≈13: 6; `ch05_img_06` de espaldas (1971, transatlántico de época).
**Maitland Parker (2).** 9 y 9, el mejor anclaje; Orellana con otra cara (sin contagio).
**Anacronismos generales:** `ch03_img_16` avión turbohélice moderno (cola en T, tipo King Air) para 1962 —el mismo que la Etapa X corrigió en el prompt de 0b, acá el prompt A3 sigue genérico—; el aire acondicionado y el camión de arriba; nada de texto legible; `ch02_img_02` coches de los 60 correctos.
**Secuencia vs una foto:** con el mismo motor, las fotos de secuencia conservan mejor la cara entre fotos de la misma persona (Víctor 4/4, Eric 2/2) y la venda como venda; las de una foto con dos madres conservan la cara ≈7 pero mezclan los dos rostros femeninos cuando son del mismo tipo.

### Mirada 2 (subagente que no vio e0/e0b/a3/x ni los informes previos) — íntegra en `bc/MIRADA_SUBAGENTE.md`
Promedios de cara frente a la madre: Daniel 7,2 (10 puntuables de 14) · María 7,4 · Víctor 5,3 · Milagros 6,0 · Ramón 4,0 · Eric 5,5 · Mercedes 4,0 · Maitland 8,0. Contagio: Daniel 2 (**`ch05_img_13`: el médico tiene la cara de la madre de Daniel** mientras el paciente está de espaldas —esa foto salió t2i sin madre: el parecido es del prompt/canon, no de la madre—; `ch04_img_10` parcial), Milagros/Ramón 2 (**`ch02_img_06` y `ch02_img_07`: el varón es Daniel, no Ramón**; las dos mujeres de la mesa tienen la misma cara). Anacronismos: Daniel 5, María 4, Víctor 2, Eric 1, Mercedes 1.
Sus 5 conclusiones (tal cual):
1. La cara se mantiene bien en Daniel, María y Maitland (7–9 cuando la cara es grande y frontal) y se degrada en cuanto la persona es chica en el cuadro o es un niño: Víctor y Mercedes salen sistemáticamente con 3–6 años menos que su madre, y Ramón de Juan directamente no entra (en 2 de 4 fotos el varón es la cara de Daniel).
2. Las fotos de «secuencia» no se ven peor que las de «una foto»: las de Víctor (ch02_img_08/10/14, ch04_img_02) y Eric (ch03_img_04/06) tienen la misma consistencia de pelo y tipo que las de /edit; lo que las hunde es el tamaño de la cara y la edad, no el camino. Las de secuencia de Daniel (ch01_supp_02 de espaldas, ch04_img_10 frontal 8) confirman lo mismo.
3. El problema estructural es que las madres de María Bernal y Milagros Barroso son la misma mujer (y Daniel/Ramón son el mismo tipo): en ch02_img_06 las dos mujeres de la mesa tienen la cara de la madre y el varón del centro es Daniel, y en ch02_img_07 el supuesto Ramón es Daniel. Mientras las madres no se distingan entre sí, el contagio entre personajes es inevitable y no se puede medir con limpieza.
4. La madre de Víctor Calvo (~15–16) y la de Mercedes (~12–13) son demasiado grandes para niños de 1962–1963: en escena el motor los rejuvenece a 8–12 y 6–7, por lo que la madre no ancla la cara. Convendría generar las madres a la edad real del guion (o una madre por tramo de edad), igual que Daniel debería tener una madre canosa para 1991 (ch05_img_13).
5. Anacronismos que se repiten y conviene filtrar en prompt: aviones modernos (turbohélice 70s en ch03_img_16, Caravan 80s en ch03_img_04 para 1948), vehículos (sedán tipo 124 en 1962 en ch02_img_02, camión moderno en ch04_img_03), aire acondicionado split (ch04_img_02), calzado y ropa actual (zapatillas/chancletas en ch04_img_03 y ch05_img_05, sudaderas con capucha en ch04_img_13), y continuidad de la lesión de Daniel (yeso/venda en el pie en ch01 y ch04_img_09, venda en la mano en ch04_img_13). No vi relojes ni texto legible.
Otro hallazgo: en `ch02_img_06` el varón de la izquierda tiene cara y brazos pintados de negro-azul uniforme (lee como maquillaje, no como polvo).

**Dónde coinciden las dos miradas:** Daniel, María y Maitland anclan (7–9 de frente); Víctor y Mercedes no (madre adolescente, escena de niño); las madres de María y Milagros son intercambiables; la secuencia no es peor que una foto; los anacronismos son de prompt. **Dónde difieren:** la mirada 2 puntúa más bajo a Ramón (4 vs mi 5-7) y a Eric (5,5 vs mi 8), y ve a Daniel donde yo vi a Ramón (`ch02_img_07`, lejos) — con dos madres del mismo tipo masculino la diferencia es opinable; a resolver con madres distinguibles (abierto 2).

## X. Anacronismos (subagente aparte, en paralelo; `lab/hyperframes/f60/x/SALIDA_X.md`, `etapa_x.json`, `hoja_x.jpg`)
3 `/edit` sueltos con la madre de 0b (`e0b/madre_daniel_ecija.png`, misma md5), prompts de 0b con una sola frase cambiada o agregada, por la cola con `pedidos_x.json` antes de esperar. US$ 0,105 (3 × 0,035), ≈ 49 s por foto. **Semilla: Seedream v5 Lite `/edit` no acepta `seed`** → cada foto X es una tirada nueva (cambian también cosas que el prompt no tocó). Nada de producción.

| foto | anacronismo en 0b | ANTES → DESPUÉS | fuente | ¿se fue? |
|---|---|---|---|---|
| ch03_img_16 (avión, 1962) | jet ejecutivo tipo Gulfstream con una hélice en el morro | `Stepping down from a small propeller aircraft onto the airstrip.` → `Stepping down from a twin-engine Douglas DC-3 propeller airliner, tail wheel resting on the strip, onto the airstrip.` | State Library of WA 146072PD, MMA DC-3 VH-MMD en Wittenoom Gorge 1961 (https://slwa.wa.gov.au/media/1916); MMA operó DC-3 1945-1970 | **Sí**: DC-3 reconocible (bimotor, rueda de cola, ventanillas cuadradas). Cara de Daniel 6/10 (chica, en sombra). |
| ch02_img_05 (reloj, veranda 1962) | reloj moderno de correa negra tipo deportivo | agregado tras «the women in modest cotton dresses.»: `One of the men wears a small round early-1960s steel wristwatch with a plain pale dial on a thin brown leather strap.` | relojes de caballero 1962 (Omega Seamaster 14759 SC 61: awco.nl, catawiki); marca no puesta en el prompt | **Sí**: reloj redondo chico, esfera clara, correa de cuero marrón. Cara 7/10 (izq.) y 6/10 (der.: contagio como en 0b). |
| ch05_img_05 (buzón/aparato, Madrid 1966) | buzón metálico moderno + caja gris (portero/cámara) sobre la puerta; niño con sudadera con capucha | agregado tras «entering their home.»: `Beside the doorway only a small brass letter slot set into the wooden street door and a round brass bell push, as in 1960s Madrid; no electronic intercom panel, no camera and no metal mailbox on the facade.` | portero electrónico Fermax desde principios de los 70 (valenciaplaza.com); buzones de chapa en grupo, patente ES83757U 1960 — objeto de época **por inferencia**, no modelo documentado | **Sí**: boca de cartas y pulsador de latón, sin buzón ni caja; el niño con jersey de punto. Riesgo nuevo: una hoja de papel pegada en el marco (sin texto legible, a vigilar). De espaldas, cara no juzgable. |

La ficha (`ficha_caso.json`) y el `research_summary` de Wittenoom solo dicen «avión pequeño de hélices» (Q15, Víctor Calvo); no nombran reloj ni buzón → los nombres salieron de la web, citados arriba. 3/3 anacronismos pedidos se fueron. Lo que ya estaba en 0b y no era el objetivo (pose de retrato en la veranda, contagio al segundo hombre) sigue igual. En la prueba B+C de arriba el avión de `ch03_img_16` volvió a salir moderno porque el prompt A3 sigue siendo el genérico: la corrección de X es de prompt, no de código, y queda para el analista decidir dónde vive (research/ficha o regla de m03).

## 4. Lo que queda abierto (decisión del analista y de Omar)
1. **Madres de niños**: «a young Spanish boy/girl» del canon A3 rinde adolescente (Víctor ≈15, Mercedes ≈13) mientras las escenas los piden de ≈8-10; la madre ancla menos (mirada 2: Víctor 5,3, Mercedes 4,0). Opciones: edad numérica en `appearance_canon` para menores (es del pedido del canon, A3), una madre por tramo de edad (la mirada 2 lo sugiere también para Daniel 1991), o aceptar.
2. **Dos madres del mismo tipo** (María y Milagros, ambas «young adult Spanish woman»; Daniel y Ramón, dos hombres españoles de 25-30): en la veranda las dos mujeres salen iguales y en `ch02_img_07` el varón parece Daniel. El tope de 2 madres y el orden ya se cumplen; distinguirlas es del canon (rasgos que diferencien a dos personas del mismo grupo), no de B. La mirada 2 lo llama «el problema estructural».
3. **Fotos de dos personas** son la mayoría de las de Daniel (10 de 12) → van por una foto con 2 madres, no por secuencia; la secuencia solo tomó 8 de las 33. Si Omar quiere más secuencia, la condición `len(persona) == 1` es la que manda (DECISIÓN del handoff).
4. **Interpretación «condition fuera de su era»** = sin intersección (declaración 1). Si el analista prefiere la otra lectura, es una línea en `persona_aporta_madre`.
5. **Venda → yeso** en fotos de una foto (`ch01_img_01`, `ch01_supp_01`, `ch04_img_13`): el prompt dice «bandaged»; es del prompt/motor, no de B/C. Y los anacronismos de escena de la prueba (avión moderno `ch03_img_16`, aire acondicionado `ch04_img_02`, camión moderno `ch04_img_03`) son de prompt (la Etapa X muestra que una frase concreta los corrige).
6. **`foto_madre_personas`** como campo nuevo del contrato (declaración 3): si el analista prefiere que asset_manager lea el canon de otro lado, se cambia en m06/fase2a/asset_manager.
7. Costo en producción por tema: ≈ 0,035 × (madres + fotos con persona); en Wittenoom la madre de persona suma 8 imágenes (US$ 0,28) y no cambia el costo por foto (las fotos con persona ya salían por t2i o /edit al mismo precio).
8. `etapa0b_secuencia.py` roto por el rename (declaración 7).

## PARADA B+C
Nada de producción de Wittenoom (voz, fotos reales, clips, render) sin OK de Omar.

Revisor-handoff: **CUMPLE CON OBSERVACIONES** (veredicto íntegro + adenda en `F60_REPORT.md` §Etapas B + C).
