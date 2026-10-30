# F58 — miniaturas como 3 paquetes (título + texto + foto) · REPORTE (Partes A y B)

Handoff: `lab/hyperframes/f58/HANDOFF_F58_miniaturas_paquetes.md` (md5 `9534c07710504f9270b8ba7ba33ea09c`, verificado; la primera copia en disco era una versión vieja, md5 `1d93a6da…`, por un error de copia del analista: PARADA hasta que se repuso). Rama `f11-guion-v4`. Decisiones de Omar 23:23 ×3, 23:38 y 23:10 en `DECISIONES.md` (primer commit). Parte A sin red, US$ 0. Ningún número fuera de la tabla del handoff. Prompts `PEDIDO_PAQUETES`, `COMPOSICION_MINIATURA` y `PEDIDO_FINAL` byte a byte (tests contra el .md). Lo viejo se borró con sus tests; lo viejo de Wittenoom en `publish/` se movió a `publish/_antes_f58/`. Producción byte-idéntica salvo A8 (tests contra `git show HEAD:`). PARADA A el 2026-10-30 00:16; el analista dio el OK a la Parte A y la Parte B corrió el 2026-10-30 04:38 (abajo). **PARADA B.**

## Para Omar, en corto
- Las miniaturas van a salir como **3 paquetes** (título + texto + foto), cada uno con una estrategia distinta, escritos por Opus en una sola llamada que lee el gancho entero, la narración y el pool completo; toda cifra del título o del texto se coteja por código contra el pool (aviso, no freno).
- La **foto de cada paquete** sale por la misma máquina que las fotos del video (casilleros de Opus sobre una oración literal del gancho + armado + canon), sin cartel y con una oración de composición (la persona en la mitad derecha); el texto va en la **mitad izquierda**, partido por ancho medido y achicando la letra hasta caber (2 líneas, nunca tapa la cara).
- El camino Gemini (6 títulos + 6 textos sueltos + hero con nombres reales) y las bases «existentes» de otro video se borraron. La pantalla de revisión muestra los 3 paquetes y deja editar, cambiar la base, rehacer una foto o pedir 3 nuevos.
- Chascada F57: la instrucción de la foto final de los clips ya no mira el movimiento (A8). **Gasto Parte A: US$ 0.**
- **Parte B (Wittenoom real):** salieron los 3 paquetes con foto y compuesta (estrategias 1 dato brutal, 3 acusación, 4 lugar y año), sin avisos de cifras ni de ancho; ningún prompt nombra a nadie de la ficha ni del canon. **Gasto Parte B: US$ 0,3953** (Opus paquetes 0,168 + casilleros 0,122 + 3 fotos Seedream 0,105; el canon no gastó). La hoja está en `lab/hyperframes/f58/hoja_paquetes.jpg` (no va a git).

## Commits
| commit | qué |
|---|---|
| `efbe36e` | Etapa 0: las 5 líneas de DECISIONES + handoff |
| `13d2690` | Parte A entera (A1–A9), tests, stickers, MAPA, suite, `SALIDA_A.md` |
| `f1a0086` | reporte + ESTADO (Parte A) |
| `8573f67` | veredicto de la Parte A + fix de los tests A3 contra `efbe36e` |
| (este) | Parte B: `parte_b.py`, `SALIDA_B.md`, `parte_b.json/.log`, reporte + ESTADO |

## Decisiones de CC
1. **Subagentes en paralelo** como pide el handoff: S1 (todo `m09_packaging` + `m09_review_server` + sus tests + `test_module_f58.py`), S2 (A8) y S3 (kwargs de m03 + `test_module_f58_a3.py`). El camino A3 (§A3) lo escribí yo antes de lanzarlos y fijé la API de m03 en el brief de S1 para que no se esperaran. Revisé los tres informes y corrí todo junto.
2. **Tests de A3 en un archivo aparte** (`test_module_f58_a3.py`): dos escritores no tocan el mismo archivo; el handoff los nombra dentro de `test_module_f58.py`.
3. **Tercer kwarg `clip_apertura` también en `_render_prompts_seedream`** (el handoff lo lista solo en `_build_seedream_prompt_step2`): hace falta para que llegue hasta ahí; default `True`, byte-idéntico.
4. **`partes["composicion"]` siempre presente** (vacía con el default): el prompt es byte-idéntico, el dict `partes` gana una clave; `test_module_f51a.py:21` (lista de claves) suma `"composicion"`.
5. **Citas en el POOL** con `Q01: ` + `linea_cita` (el handoff da `linea_cita` pero no el separador con el id; mismo `: ` que D/P/L).
6. **`numeros_pool` ignora los ids** (`D07` no aporta un 7): con los ids casi cualquier cifra chica pasaba sin aviso.
7. **A2 con bucle propio de reintentos** (misma cuenta `MAX_RETRY_ATTEMPTS`, feedback del motivo) en vez de `_call_with_validation_retry`, que mete el checklist de anchors de m03 y loguea «cap N».
8. **`metadata.json` se escribe antes de las fotos**: si los casilleros paran, los paquetes ya pagados a Opus no se pierden.
9. **`delete_candidate` / `_qa_backups` del servidor** se fueron con la grilla (el handoff no los nombra; la página nueva no tiene candidatas sueltas que borrar).
10. **Dos tests viejos que ejercitaban lo borrado**: `test_module_f54::test_m09_gancho_primero…` (B.4 del camino Gemini) se borró con nota; `test_module_gfx_auto_icons::test_credito_en_la_descripcion` pasa a `normalizar_paquetes`.
11. **Fila «¿QUIÉN SABÍA…» de la tabla A5**: en esta máquina Pillow mide 550/499 (handoff 553/501, fuera del ±1); líneas y px coinciden. Queda `xfail(strict=True)` con la razón; no se inventó tolerancia. Decide el analista qué medida manda.

## Salida A (entera en `lab/hyperframes/f58/SALIDA_A.md`)

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

### 1. Módulos: antes → después

| módulo | antes | después |
|---|---|---|
| `script_engine/m09_packaging.py` | Gemini: 6 títulos + 6 overlays sueltos (`_META_SYSTEM`) y 3 ideas de foto (`_HERO_SYSTEM`, prompt «SEEDREAM 4.5», sin canon, nombres reales); bases «existentes» de `audit_map.csv` de otro video; leía `data/scripts/<tid>.json` y 10 `verified_facts`; texto partido por palabras (`_wrap_lines`) | **Opus (`MODELO_CASILLEROS`, `ESFUERZO[…]`) en una llamada**: `PEDIDO_PAQUETES` (byte a byte el del handoff; un test lo extrae del .md y compara) con el GANCHO (cap 1 entero), `[Cap N]` 2–7 sin truncar y el POOL completo (D/T/citas con `linea_cita`/P/L, ids tal cual; `cifras_canonicas` al final si viene); `ESQUEMA_PAQUETES`; validación por código con `MAX_RETRY_ATTEMPTS` (n exacto, campos llenos, estrategias distintas, ancla literal del gancho con espacios normalizados, anclas distintas) → `PaquetesParada` si fallan todos; después `titulo[:MAX_TITLE_CHARS]`, `.upper()`, `_truncate_tags`, `with_icon_credit`. Entradas de `_steps/<tid>/` (`01b_narration.json`, `00_pool_v3.json`, `01a_skeleton.json`), falta → `PaquetesParada` con la ruta. **Foto por producción** (`topic_produccion` = `_load_topic_by_id` + `asegurar_canon` + `_f8`; `prompts_paquetes` → `_render_prompts_seedream(…, 1, composicion=COMPOSICION_MINIATURA, sin_cartel=True, clip_apertura=False)` con `refill=True` + `force_assign`; `foto_paquete` → `_generate_image_raw(prompt, out, use_ultra=False)`, error → motivo literal). **Cifras por código** (`numeros_pool`, `avisos_cifras`: «⚠ cifra sin dato: N»). **Texto por ancho** (`partir_texto`, `ancho_linea` con `textbbox` + borde; zona 584 px; de 108 a 75 px de a 1; «⚠ no cabe»). `N_PAQUETES = 3` (reemplaza a `FRESH_THUMBS`). Borrados: `_META_*`, `META_TEMP`, `generate_metadata`, `_meta_user_prompt`, `_HERO_*`, `generate_hero_prompt(_iter)`, `_narration_for_hero`, `HERO_NARRATION_PER_CAP`, `_gemini_json`, imports `gemini_client`/`gt`/`DOCTRINE_*`, `GANCHO_INSTRUCCION`, `_bloque_gancho`, `_load_canonical`, `shortlist_existing`, `SHORTLIST_EXISTING`, `_resolve_png`, `audit_map.csv`, `_wrap_lines`, `_generate_fresh`, `_render_concept_variations`, `_record_iteration`/`_load_iterations`, `--only-fresh`, `--skip-fresh`, `--title N` (→ `--compose --paquete N`). `run_candidates(tid, video_path=None, review=False)` se mantiene; `candidates_ready` exige `paquetes`; `metadata.json.paquetes` acumula con índice global |
| `script_engine/m09_review_server.py` | grilla existing/fresh, panel de crítica al hero, borrar candidatas | 3 paquetes terminados (miniatura, título con cuenta, texto, `id: texto`, `cap_que_paga`, ancla, avisos); editar título/texto (recompone sin red), elegir otra base (`bases_del_video`: `*_graded.png` o la cruda), «rehacer foto» (A3 solo esa ancla), «3 paquetes nuevos» (sin pisar números); `/img` solo dentro de `assets/`, `thumb_candidates/`, `publish/`; `--auto-first` sigue (sin paquetes, genera) |
| `script_engine/m03_visual.py` | `_build_seedream_prompt_step2(…, anios=None)`; `_render_prompts_seedream(…, cap_number)` | `clip_apertura=True` / `composicion=""`, `sin_cartel=False`, `clip_apertura=True` (§A3). Defaults byte-idénticos (test contra `git show HEAD:` sobre Wittenoom real) |
| `script_engine/m03_imagenes_v3.py` | `armar(it, anio, grupos)` | `armar(…, composicion="")`: `partes["composicion"]` después de `tecnica`; vacía → prompt byte-idéntico (78 ítems reales de Wittenoom) |
| `script_engine/video_prompt.py` + `asset_manager.py` | `PEDIDO_FINAL` con «APPROVED MOTION»; `armar_body_final`/`escribir_final` con `video_prompt_aprobado` | A8: `PEDIDO_FINAL` sin el movimiento (abajo); el parámetro sale de las dos; `foto_final_del_clip` mantiene su firma y ya no lo pasa |
| tests | `test_m09_packaging.py`, `test_m09_review_server.py`, `test_fase3.py` (`--only-fresh` → `--review`), `test_module_f57.py` (copia de `PEDIDO_FINAL`), `test_module_f51a.py:21` (lista de claves de `partes` + `composicion`) | adaptados; nuevos `test_module_f58.py` (31 + 1 xfail) y `test_module_f58_a3.py` (9) |

### 2. El usuario de A2 armado para Wittenoom

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

### 3. La tabla de A5 que sale de los tests (Anton bundleada; Pillow 12.2.0, layout BASIC, sin raqm)

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

### 4. A8: `PEDIDO_FINAL` antes → después

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

### 5. Lo viejo de Wittenoom

`output/123bbb64-…/publish/`: `metadata.json`, `metadata_candidatos.md`, `hero_iterations.json`, `thumb_final_01.png`, `thumb_final_02.png` y `_qa_backups/` **movidos** a `publish/_antes_f58/` (no borrados). Quedan `CHECKLIST_PUBLICACION.md` y `thumb_candidates/` vacío (las `existing_*`/`fresh_*` viejas ya estaban en `_qa_backups/`, que se movió entero).

### 6. Suites

`bash lab/hyperframes/f41/verificar.sh f58` (logs en `lab/hyperframes/f41/f58/`): ch02 md5 **`f792f3d483a1fa42daed5f7f0e054f46`** (candado); rápida **53 passed**; amplia (segunda corrida, después de adaptar 2 tests viejos de m09): **1194 passed + 1 xfailed** + 4 fallas, las 4 previas (`m03_merge_timing` ×2, `gfx_lab` ×2). La primera corrida de la amplia tuvo 2 fallas más, de tests que ejercitaban lo borrado: `test_module_f54::test_m09_gancho_primero_y_cap_1_sin_truncar` (el B.4 del camino Gemini viejo; se borró con una nota: el GANCHO entero primero lo cubre `test_module_f58` A2) y `test_module_gfx_auto_icons::test_credito_en_la_descripcion` (`_normalize_metadata` → `normalizar_paquetes`). `python lab/tools/mapa_modulos.py --check`: 158 archivos · **0 fallas**; stickers de los 6 módulos al día. Tests nuevos: `test_module_f58.py` 31 + 1 xfail, `test_module_f58_a3.py` 9; con `test_m09_*`, `test_fase3`, `test_qa_studio`, `test_module_f57`, `f51a`, `f53b*`: 141 passed.

**PARADA A.** La Parte B (Wittenoom real) no arranca sin el OK del analista a la Parte A.


## Suite
Ver §6 de la Salida A: ch02 `f792f3d4…`, rápida 53, amplia 1194 + 1 xfail + 4 previas, MAPA 0.

## Salida B (entera en `lab/hyperframes/f58/SALIDA_B.md`)

Comando: `python -m script_engine.m09_packaging 123bbb64-9fca-4395-8bf4-57d60e219ef1 --candidates` (vía `main()` con ese argv, dentro de `cost_tracker.start_video('f58_parte_b')`). 199.9 s de reloj. Topic `123bbb64-9fca-4395-8bf4-57d60e219ef1`.

### 1. Los 3 paquetes

### Paquete 01 — 1

- **Título** (64 caracteres): Vivió 10 meses junto a una mina de amianto azul y murió a los 55
- **Texto**: «¿QUÉ RESPIRÓ ALLÍ?»
- **Ancla** (oración literal del gancho): «Ese pie va a cerrar; lo que respira mientras espera que cierre va a tardar casi treinta años en matarlo, y lo va a alcanzar a miles de kilómetros de aquí.»
- **cap_que_paga**: 5
- **dato_ids**:
  - `D87`: La familia Écija-Bernal vivió en Wittenoom unos 10 meses, entre 1962 y 1963.
  - `D89`: Daniel Écija padre murió de mesotelioma a los 55 años, nueve meses después de su diagnóstico.
  - `D35`: El asbesto azul (crocidolita), el tipo que se extraía en Wittenoom, es el más mortal de todos los tipos de asbesto.
  - `D85`: Daniel Écija padre se hirió el pie con un trozo de amianto y la herida no se cerraba.
- **Avisos**: ninguno
- **Foto**: paquete_01_base.png · año 1963 (1) el casillero `year` del modelo)
- **Compuesta**: paquete_01.png · base paquete_01_base.png

### Paquete 02 — 3

- **Título** (60 caracteres): Sabían del polvo desde 1944: la mina que mató a Daniel Écija
- **Texto**: «LO LLAMARON ALBOROTADOR»
- **Ancla** (oración literal del gancho): «La familia que la guarda cuenta que le cayó encima un trozo de amianto y que la herida no cerraba.»
- **cap_que_paga**: 3
- **dato_ids**:
  - `D19`: El Inspector de Minas y el Ingeniero de Minas Adjunto del Estado informaron sobre el problema del polvo ya en 1944.
  - `D89`: Daniel Écija padre murió de mesotelioma a los 55 años, nueve meses después de su diagnóstico.
  - `D92`: En 1948, el doctor Eric Saint advirtió por escrito que los niveles de polvo en Wittenoom eran extremadamente peligrosos.
  - `T19`: 1948 · El doctor Eric Saint advirtió por escrito sobre los peligrosos niveles de polvo en la mina.
- **Avisos**: ninguno
- **Foto**: paquete_02_base.png · año 1963 (1) el casillero `year` del modelo)
- **Compuesta**: paquete_02.png · base paquete_02_base.png

### Paquete 03 — 4

- **Título** (63 caracteres): Wittenoom, 1963: el pueblo de amianto que borraron de los mapas
- **Texto**: «NADIE SACÓ UNA PALADA»
- **Ancla** (oración literal del gancho): «Lo que sobró de la mina, en cambio, sigue donde lo dejaron.»
- **cap_que_paga**: 7
- **dato_ids**:
  - `T40`: 1963-06 · Nació Daniel Écija Bernal en el hospital de Wittenoom.
  - `T41`: 1963-07-07 · La familia Écija-Bernal bautizó a su hijo Daniel y poco después abandonó Wittenoom.
  - `D31`: En junio de 2007, el sitio del pueblo de Wittenoom fue oficialmente desclasificado y su nombre eliminado de los mapas y señales de tráfico oficiales.
  - `D71`: No se ha retirado ni una sola palada de asbesto de la tierra Banjima.
  - `D02`: Se estima que los relaves de la minería, que contienen alrededor de un 5% de asbesto, superan los 3 millones de toneladas.
- **Avisos**: ninguno
- **Foto**: paquete_03_base.png · año 2026 (1) el casillero `year` del modelo)
- **Compuesta**: paquete_03.png · base paquete_03_base.png

### 2. Los 3 prompts de foto (enteros)

### Paquete 01

**prompt (el que fue a Seedream):**

    A young adult Spanish migrant miner, olive skin, short dark early-1960s hair, lean work-hardened build, sun-weathered face, in a dust-coated short-sleeved work shirt and drill trousers, one foot wrapped in a pale bandage and the other in a heavy work boot. Stands posing stiffly for a family portrait, weight shifted onto his good leg, the bandaged foot set forward on the ground. Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes. Wittenoom company town, 1963: in front of a low corrugated-iron and fibro-cement company house, its yard surfaced with crumbly blue-grey crocidolite tailings. Hard cold overcast desert light, flat and shadowless, isolating the figure against the pale wall. Medium shot, eye-level, frontal like a period box camera, 50mm lens, moderate depth of field, slightly soft period film grain. The person fills the right half of the frame, face and torso large; the left half is dark, uncluttered negative space. A grainy 35mm documentary photograph taken in 1963, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.

**raw_llm_prompt (casillero de Opus):**

    {"subject": "A young adult Spanish migrant miner, olive skin, short dark early-1960s hair, lean work-hardened build, sun-weathered face, in a dust-coated short-sleeved work shirt and drill trousers, one foot wrapped in a pale bandage and the other in a heavy work boot", "action": "Stands posing stiffly for a family portrait, weight shifted onto his good leg, the bandaged foot set forward on the ground", "gaze_interaction": "Face and eyes square to the camera, shoulders slightly drawn up, a guarded half-smile, arms hanging straight at his sides", "setting": "Wittenoom company town, 1963: in front of a low corrugated-iron and fibro-cement company house, its yard surfaced with crumbly blue-grey crocidolite tailings", "color_palette": "Desaturated black-and-white tonality with a cold blue-grey cast; pale grey fibro walls, dull grey corrugated iron, washed-out red-ochre earth", "props_detail": "The pale bandage around his foot, its edges greyed by a fine fibrous dust", "shot_scale": "medium", "camera_angle": "eye-level, frontal like a period box camera", "lens_technique": "50mm lens, moderate depth of field, slightly soft period film grain", "lighting": "Hard cold overcast desert light, flat and shadowless, isolating the figure against the pale wall", "mood": "A lone figure pinned under flat white sky, fine dust hanging in the air, a stiff pose held a beat too long", "style": "Documentary photographic realism, dark-history, faceless channel look, aged 1960s family snapshot", "text_in_image": {"present": false, "text": "", "font": "", "location": ""}, "hard_fact_ids": [], "people_group": ["spanish_migrant_families"], "year": "1963"}

### Paquete 02

**prompt (el que fue a Seedream):**

    The bandaged foot of a young Spanish migrant miner resting on tailings-surfaced ground, a dusty trouser cuff above it, a jagged fragment of blue crocidolite asbestos lying beside it. The foot rests motionless while the loose fibrous fragment sheds fine threads and powder onto the bandage. Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes. A Wittenoom house yard, 1963, the ground compacted with loose blue-grey crocidolite tailings and red-ochre dust. Hard cold directional overcast light raking across the fibres. Detail shot, high angle looking down, macro-leaning 100mm lens, shallow depth of field, fibres sharp, background soft. The person fills the right half of the frame, face and torso large; the left half is dark, uncluttered negative space. A grainy 35mm documentary photograph taken in 1963, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.

**raw_llm_prompt (casillero de Opus):**

    {"subject": "The bandaged foot of a young Spanish migrant miner resting on tailings-surfaced ground, a dusty trouser cuff above it, a jagged fragment of blue crocidolite asbestos lying beside it", "action": "The foot rests motionless while the loose fibrous fragment sheds fine threads and powder onto the bandage", "gaze_interaction": "Focal direction drawn down to the pale bandage and the frayed blue-grey mineral fragment beside it", "setting": "A Wittenoom house yard, 1963, the ground compacted with loose blue-grey crocidolite tailings and red-ochre dust", "color_palette": "Cold blue-grey crocidolite tones, off-white greyed bandage, muted red-ochre dust, desaturated documentary grade", "props_detail": "A frayed chunk of raw blue asbestos unravelling into fine fibrous threads", "shot_scale": "detail", "camera_angle": "high angle looking down", "lens_technique": "macro-leaning 100mm lens, shallow depth of field, fibres sharp, background soft", "lighting": "Hard cold directional overcast light raking across the fibres", "mood": "Fine fibrous powder settling on the cloth, a dull stain spreading through the bandage weave, utter stillness", "style": "Documentary photographic realism, dark-history, faceless channel look", "text_in_image": {"present": false, "text": "", "font": "", "location": ""}, "hard_fact_ids": [], "people_group": ["spanish_migrant_families"], "year": "1963"}

### Paquete 03

**prompt (el que fue a Seedream):**

    Vast abandoned blue-grey asbestos tailings dumps spilling down the rocky red walls of a Pilbara gorge where the erased mining town once stood. The tailings lie exactly where they were dumped, eroding in slow streaks toward a dry creek bed, the empty town site beyond reduced to bare cleared ground. Wittenoom gorge in the present day: demolished, emptied town site, a permanent barricade across the old road entrance, sparse spinifex, 2026. Cold overcast daylight, flat and colourless over the gorge. Extreme wide shot, high angle aerial view, wide-angle lens, deep depth of field. The person fills the right half of the frame, face and torso large; the left half is dark, uncluttered negative space. A grainy 35mm documentary photograph taken in 2026, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.

**raw_llm_prompt (casillero de Opus):**

    {"subject": "Vast abandoned blue-grey asbestos tailings dumps spilling down the rocky red walls of a Pilbara gorge where the erased mining town once stood", "action": "The tailings lie exactly where they were dumped, eroding in slow streaks toward a dry creek bed, the empty town site beyond reduced to bare cleared ground", "gaze_interaction": "Focal direction pulls from the pale tailings slopes down the gorge toward the empty flat where the town stood", "setting": "Wittenoom gorge in the present day: demolished, emptied town site, no buildings, a permanent barricade across the old road entrance, sparse spinifex", "color_palette": "Desaturated red-ochre rock and earth, blue-grey crocidolite tailings, bleached grey sky, cold documentary grade", "props_detail": "A long scar of loose blue-grey tailings washing into a dry creek bed", "shot_scale": "extreme_wide", "camera_angle": "high angle aerial view", "lens_technique": "wide-angle lens, deep depth of field", "lighting": "Cold overcast daylight, flat and colourless over the gorge", "mood": "An immense silent landscape, wind lifting faint dust off the dumps, no living figure anywhere", "style": "Documentary photographic realism, dark-history, faceless channel look", "text_in_image": {"present": false, "text": "", "font": "", "location": ""}, "hard_fact_ids": ["F02"], "people_group": [], "year": "2026"}

### 3. Nombres de `documented_people` / `ficha.personas` en los prompts (medida, no freno)

Formas buscadas: 126 (nombre y variantes de las 56 personas de la ficha, sin paréntesis; `name` de los 22 `documented_people` del canon), palabra entera, sin distinguir mayúsculas.

Ningún prompt nombra a nadie.

### 4. Hoja

`lab\hyperframes\f58\hoja_paquetes.jpg` — las 3 miniaturas compuestas lado a lado (compuestas en `output/123bbb64-9fca-4395-8bf4-57d60e219ef1/publish/thumb_candidates/`; no van a git).

### 5. Descripción y tags

**Descripción** (1502 caracteres):

    Daniel Écija vivió unos 10 meses en Wittenoom y el amianto que respiró allí lo alcanzó décadas después en Madrid. En 1961, en el Círculo de Bellas Artes de Madrid, conoció a María Bernal en un baile; se casaron el 20 de septiembre de 1962 y cuatro días después emigraron a Australia, parte de los cerca de 8.000 españoles que llegaron con la Operación Canguro. Su destino fue Wittenoom, en la región de Pilbara, un pueblo minero de asbesto azul (crocidolita), el tipo más mortal de todos, explotado por Australian Blue Asbestos, filial de CSR. Con los relaves de la mina se hicieron la pista de aterrizaje, las carreteras y los patios donde jugaban los chicos. Las advertencias existían desde mucho antes: en 1944 el Inspector de Minas informó sobre el problema del polvo, en 1946 otro inspector llamó 'terroríficas' a las condiciones y en 1948 el doctor Eric Saint advirtió por escrito que los niveles de polvo eran extremadamente peligrosos. Aun así, la producción se incrementó en 1961. La mina cerró en 1966 por razones económicas. En 1991, Daniel fue diagnosticado con mesotelioma y murió nueve meses después, a los 55 años. Hoy Wittenoom no figura en los mapas oficiales, más de 3 millones de toneladas de relaves siguen en tierra Banjima y no se ha retirado ni una sola palada de asbesto. Esta es la historia de un hombre, de un pueblo borrado y de todos los que sabían. Suscribite para más historias que la historia oficial prefirió no contar.
    
    Íconos: game-icons.net (CC BY 3.0) · Lucide (MIT)

**Tags** (23): Wittenoom, amianto azul, asbesto, crocidolita, mesotelioma, Daniel Écija, María Bernal, Operación Canguro, emigrantes españoles, Australia Occidental, Pilbara, CSR, pueblo fantasma, pueblo borrado del mapa, historia oscura, documental, desastre industrial, Banjima, Eric Saint, blue asbestos, asbestos mining disaster, ghost town Australia, Wittenoom documentary

### 6. Gasto (cost_tracker, video `f58_parte_b`)

| servicio | descripción | US$ |
|---|---|---|
| Anthropic claude-opus-5-5 | m09:paquetes | 0.16794 |
| Anthropic claude-opus-5-5 | m03:casilleros | 0.12233 |
| fal.ai Seedream 5.0 Lite (t2i) | paquete_01_base: A young adult Spanish migrant miner, olive skin, short dark ... | 0.035 |
| fal.ai Seedream 5.0 Lite (t2i) | paquete_02_base: The bandaged foot of a young Spanish migrant miner resting o... | 0.035 |
| fal.ai Seedream 5.0 Lite (t2i) | paquete_03_base: Vast abandoned blue-grey asbestos tailings dumps spilling do... | 0.035 |

Por rubro: **m09:paquetes** US$ 0.16794 · **casilleros** US$ 0.12233 · **fotos** US$ 0.105

**Total US$ 0.3953**.

`asegurar_canon`: no llamó a Flash (la marca `canon_ficha_md5` del topic coincidía con la ficha).

### 7. Archivos

- `output/123bbb64-9fca-4395-8bf4-57d60e219ef1/publish/metadata.json` (paquetes, descripción, tags) y `thumb_candidates/paquete_NN*.png` (no van a git)
- `lab/hyperframes/f58/hoja_paquetes.jpg`, `parte_b.json` (todo), `parte_b.log` (stdout de la corrida)

## Lo que queda abierto
1. **La oración de composición va en los 3 prompts, tenga o no persona el casillero** (`COMPOSICION_MINIATURA` se suma siempre, byte a byte el pedido del handoff): en el paquete 03 (paisaje aéreo de los relaves, `people_group` vacío, «no living figure anywhere») Seedream puso igual una cara en la mitad derecha; en el 02 (detalle del pie vendado) también metió la cara. Son las fotos que salieron; se informa, no se tocó.
2. **Anchos de la fila «¿QUIÉN SABÍA…»** (decisión 11): xfail estricto; si en la máquina del analista da 553/501 el test lo muestra.
3. **Casilleros que fallan** (`CasillerosParada`, o sin beats) → PARADA de `--candidates` después de escribir los paquetes en `metadata.json` (en Wittenoom no pasó).
4. **A8 cambia la foto final de los clips de producción** (la instrucción ya no ve el movimiento); no hay clip nuevo corrido con esto.
5. **`--auto-first` de QA Studio** con un `metadata.json` viejo (sin `paquetes`): `candidates_ready` da False y genera; en Wittenoom el `metadata.json` nuevo ya tiene los 3 paquetes.
6. **El `anio_fuente` del ítem** se guarda tal cual lo devuelve m03 («(1) el casillero `year` del modelo») y así se imprime en la Salida B: es texto de producción, no se tocó.
7. **`parte_b.py` corre el comando vía `main()` con el argv del handoff** (dentro de `cost_tracker.start_video`), no como proceso aparte: es la única forma de que el gasto quede desglosado por servicio. El primer intento tenía mal el argv (quedaba `-m` en la lista) y `argparse` salió con código 2 antes de llamar a nada: US$ 0, se corrigió y se volvió a correr.
8. **Coherencia dentro del paquete** (observación 2 del revisor): nadie coteja que el texto salga de los `dato_ids` citados ni que la ancla se relacione con el título; en el paquete 02 el texto «LO LLAMARON ALBOROTADOR» viene de la cita Q46 (no citada) y la ancla es la herida del pie. Lo decide el analista.

## Veredicto de revisor-handoff — Parte A (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 0 | Handoff md5 9534c077… | OK | `md5sum` coincide |
| 1 | Etapa 0: las 5 líneas tal cual en DECISIONES (commit propio) | OK | Comparé con Python cada línea del .md contra DECISIONES.md: 5/5 presentes, commit efbe36e |
| 2 | A1 entradas, PARADA si falta, bloque POOL (D/T/citas/P/L, ids tal cual, cifras al final) | OK | m09_packaging.py:171-242; Wittenoom: 362 líneas (D155·T98·Q50·P35·L24), `cifras_canonicas` vacío. Cita en el POOL con `Q01: ` (decisión 5 de CC, el handoff no daba el separador) |
| 3 | A2 `PEDIDO_PAQUETES`, `COMPOSICION_MINIATURA` y `PEDIDO_FINAL` byte a byte | OK | Extraje los 3 bloques ``` del .md y los comparé con las constantes: True/True/True |
| 4 | A2 llamada con kwargs exactos, esquema, validación y reintentos, normalización | OK | m09:332-363 (model, system_instruction=None, response_schema, effort, description="m09:paquetes"); validar_paquetes m09:262-293; normalizar m09:314. Bucle propio con `MAX_RETRY_ATTEMPTS` (decisión 7 de CC) |
| 5 | A2 borrados completos | OK | grep de cada nombre listado en m09_packaging y m09_review_server: 0 resultados. `_wrap_lines` solo sobrevive en gfx_project.py, que es otra función sin relación. Un test los fija |
| 6 | A3 camino en SALIDA_A §A3 con archivo:línea | PARCIAL | Existe y es completo, pero los números de línea son de antes de editar: están corridos 2-8 líneas (p. ej. `armar` composicion en m03_imagenes_v3:650, no 648; `MAX_RETRY_ATTEMPTS` ya no está en m03_visual:867) |
| 7 | A3 kwargs con default byte-idéntico | OK | `git diff efbe36e 13d2690` sobre m03_visual y m03_imagenes_v3: todo va detrás de `clip_apertura and…`, `sin_cartel`, `if composicion`. Corrí `test_module_f58_a3` con `HEAD` reemplazado por `efbe36e`: 9 passed |
| 8 | A3 excepción LR_RE fijada por test | OK | `test_composicion_en_su_lugar_y_f8_la_deja`; LR_RE en m03_imagenes_v3:267-269 no matchea la oración |
| 9 | A3 foto por `_generate_image_raw(..., use_ultra=False)` con motivo literal; si falla, los otros siguen | OK | m09:441-450; `test_a3_rechazo_deja_paquete_sin_foto_y_siguen` |
| 10 | A4 cifras por código, aviso sin freno | OK | m09:369-393; `test_a4_cifras` (46.840 = 46,840). `numeros_pool` ignora los ids (decisión 6 de CC) |
| 11 | A5 tabla (líneas y px exactos, anchos ±1), fila xfail | OK | Reproduje las 7 filas: líneas y px idénticos. Anchos ±1 en 6 filas. «¿QUIÉN SABÍA…» da 550/499 contra 553/501 del handoff. Es xfail(strict) declarado, sin tolerancia inventada |
| 12 | A6 bases: borrados y servidor acotado | OK | `bases_del_video`, `_resolve_base`, `resolve_image` limitan a assets/, thumb_candidates/ y publish/ |
| 13 | A7 CLI, página, `candidates_ready`, firma de `run_candidates`, acumula con índice global, `--compose --paquete`, `--auto-first`, `test_fase3` | OK | m09:638, 692-731, 866, 905-947; m09_review_server.py:213-240 (cuenta de caracteres, `id: texto`, `cap_que_paga`, ancla, avisos). test_fase3 pasa a `--review` |
| 14 | A7 lo viejo de Wittenoom movido a `_antes_f58/`, no borrado | OK | Están metadata.json, metadata_candidatos.md, hero_iterations.json, thumb_final_01/02.png y `_qa_backups/` (con 12 imágenes) |
| 15 | A8 `PEDIDO_FINAL` íntegro; parámetro fuera de `armar_body_final`, `escribir_final` y la llamada | PARCIAL | video_prompt.py y la llamada en asset_manager.py:690 limpios. `foto_final_del_clip` conserva el parámetro `video_prompt_aprobado`, muerto y declarado. El handoff dice «de su llamador (asset_manager:689)», lo que se puede leer de las dos maneras |
| 16 | A9 tests y adaptaciones | OK | test_module_f58 (31 + 1 xfail) cubre A1-A7; adaptados f57, f51a, f54, gfx_auto_icons, m09_*, fase3. Se borró un test viejo de f54 (B.4), con nota |
| 17 | Salida A completa | OK | Módulos, camino A3, usuario A2, tabla A5, A8 antes/después y suites. Los 59 008 caracteres son exactos: reconstruí `armar_pedido` y coincide con `pedido_paquetes_wittenoom.txt` (que agrega una línea de pie `[59008 caracteres]`) |
| 18 | Parte B no corrida | OK | No hay `publish/metadata.json` ni `paquete_*.png` en Wittenoom (solo `_antes_f58/metadata.json`) |
| 19 | Suites verdes | PARCIAL | Corrí las 8 suites pedidas: 113 passed, 1 xfailed, **2 failed**. `mapa --check`: 0 fallas. ch02 md5 f792f3d4… solo lo leí del log, no lo regeneré. Las suites rápida y amplia las leí de los logs, no las corrí |
| 20 | Reporte: decisiones de CC y «lo que queda abierto» | OK | F58_REPORT.md:18-29 y 143-150. El veredicto del revisor figura como «(se pega abajo)», pendiente |

Fuera de alcance: ninguno. `git diff efbe36e~1 HEAD --stat` son 28 archivos, todos de la tanda; los dos modificados sin commit (`diag_234_cap4.py`, `f28a.log`) son previos y no son de F58.

Observaciones:
1. **Falla en HEAD (grave):** `test_module_f58_a3.py::test_armar_sin_el_kwarg_es_byte_identico_a_hoy` y `::test_step2_sin_el_kwarg_es_byte_identico_a_hoy` fallan hoy. Comparan contra `git show HEAD:`, y después del commit 13d2690 HEAD ya trae los kwargs nuevos. El «1194 passed» del reporte fue cierto solo antes de commitear. Esos dos tests quedaron rotos de forma permanente y la prueba durable de «producción byte-idéntica» no existe. Yo la rehice contra efbe36e y da 9/9, y el diff también lo confirma.
2. SALIDA_A §5 y el reporte (abierto 6) dicen que `thumb_candidates/` conserva las `existing_*`/`fresh_*` viejas. Está vacío: esos archivos están en `_antes_f58/_qa_backups/`. La afirmación es falsa, sin mayor consecuencia.
3. Hay números fuera de la tabla del handoff, pero solo en mensajes y logs: `[:60]`, `[:90]`, `[:120]`. No afectan la lógica.
4. Las dos decisiones de CC fuera del handoff (tests de A3 en un archivo aparte, `clip_apertura` también en `_render_prompts_seedream`) están declaradas.

Riesgos que el contrato no cubre: (a) A8 cambia la foto final de los clips de producción y ningún clip nuevo lo valida. (b) La Parte B depende de `asegurar_canon` (puede llamar a Flash) y de la validación de anclas literales: si Opus parte una oración distinto a `oraciones()`, caerá en PARADA tras 3 intentos. (c) Los anchos de Pillow cambian entre máquinas (fila xfail), así que «cabe o no cabe» puede variar en el caso límite.

Nota de mi parte: creé y borré un archivo temporal `_rev_tmp_a3.py` en la raíz para la comprobación contra efbe36e. El repo quedó igual que lo encontré.

## Adenda de CC (Parte A)
- **Observación 1 (grave, corregida en este commit):** los dos tests «byte-idéntico» de `test_module_f58_a3.py` comparaban contra `git show HEAD:`; con los kwargs ya en HEAD se rompían solos. Ahora cargan `efbe36e` (la Etapa 0, último commit con m03 sin los kwargs; constante `ANTES_F58`): 9/9. La amplia volvió a correr con ese arreglo sobre el árbol de este commit: **1194 passed + 1 xfail + las 4 previas** (`lab/hyperframes/f41/f58/suite_amplia_2.log`).
- **Observación 2 (corregida):** `thumb_candidates/` de Wittenoom está vacío; las candidatas viejas estaban en `_qa_backups/`, que se movió entero a `_antes_f58/`. Salida A §5 y abierto 6 lo dicen así ahora.
- **Fila 6 (números de línea de §A3):** son los de `efbe36e`, antes de los kwargs (se escribió antes de programar, como pide el handoff); queda anotado en el título de la sección.
- **Fila 15 (`foto_final_del_clip`):** el parámetro queda a propósito para no cambiar la firma de producción en una chascada (el handoff nombra `armar_body_final`, `escribir_final` y «su llamador», que es la llamada en asset_manager:690, ya sin el argumento); está declarado en el docstring.
- **Observación 3:** `[:60]`, `[:90]`, `[:120]` son recortes de mensajes de log/error, como los que ya había en m09 y asset_manager; no entran a la lógica.

## Veredicto de revisor-handoff — Parte B (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito (handoff B / pedido) | Estado | Evidencia |
|---|---|---|---|
| 1 | Comando `m09_packaging 123bbb64-… --candidates` con cost_tracker | OK | parte_b.py:48-55 (start_video, `sys.argv` con el argv del handoff, `m09.main()`, end_video); parte_b.log exit=0. Corre vía `main()` y no como proceso aparte, y el reporte lo declara (abierto #7). |
| 2 | 3 paquetes enteros con texto de cada dato_ids y avisos | OK | SALIDA_B.md:5-51. Coincide con `publish/metadata.json`: títulos, textos, cap_que_paga, dato_ids, avisos `[]`, estrategias 1/3/4. |
| 3 | Anclas = oraciones literales del gancho | OK | Las 3 están dentro del cap 1 de `01b_narration.json` (verificado por código). |
| 4 | dato_ids existen en el pool | OK | Los 13 ids están en `00_pool_v3.json` (verificado por código). |
| 5 | 3 prompts de foto armados, enteros | OK | SALIDA_B.md:53-83, idénticos a `metadata.json` (`prompt` y `raw_llm_prompt`). |
| 6 | Medida de nombres de documented_people | OK | Yo rearmé las formas desde `ficha_caso.json` y `02_canonical.json`: salieron 121, no 126, porque deduplico distinto. Busqué palabra entera, sin distinguir mayúsculas, en los 6 textos (3 prompts y 3 raw_llm_prompt): 0 coincidencias. Coincide con SALIDA_B:89. |
| 7 | Hoja con las 3 miniaturas lado a lado | OK | `lab/hyperframes/f58/hoja_paquetes.jpg`, 86 KB, 1920x360. La vi: tres miniaturas con el texto a la izquierda. |
| 8 | Descripción y tags | OK | SALIDA_B:95-104; `metadata.json` tiene 1502 caracteres y 23 tags. |
| 9 | Gasto desglosado y si asegurar_canon llama a Flash | OK | `data/cost_history.json`: video `f58_parte_b` (04:38:18) suma 0.395264 con 5 entradas (m09:paquetes, m03:casilleros, 3 Seedream). Coincide con SALIDA_B:109-117. El log dice «[canon] ya armado… se usa», o sea que no hubo Flash. |
| 10 | Imágenes no van a git | OK | `git show --stat 14e5557` lista solo 6 archivos (ESTADO, REPORT, SALIDA_B, parte_b.json/.log/.py). La hoja y los PNG no están en git. |
| 11 | Sin código de producción tocado | OK | El stat solo tiene `lab/` (parte_b.py es nuevo, de lab). |
| 12 | Reporte con Salida B y «lo que queda abierto» | OK | F58_REPORT.md:146 y 271-277. |
| 13 | ESTADO al día (bloque de arriba y línea 3) | OK | ESTADO_SESION.md línea 3 y los bloques «Para Omar» y «Parte B». |
| 14 | Veredicto íntegro de revisor-handoff | PARCIAL | F58_REPORT.md:327-329 tiene el placeholder «(se pega abajo)». Es lo esperado antes de este veredicto, pero queda pendiente pegarlo. |
| 15 | Entregables en disco | OK | `thumb_candidates/` tiene paquete_01..03.png y los 3 `_base.png`, todos con tamaño no nulo. |

Fuera de alcance: ninguno. En `git status` hay sin trackear `lab/hyperframes/f58/ENTRADA_ANALISTA_2026-10-30.md` y `hoja_paquetes.jpg`; no entraron al commit y no son código.

Observaciones:
1. Los prompts de los paquetes 02 (detalle del pie) y 03 (paisaje aéreo sin persona) llevan la oración «The person fills the right half… face and torso large». Contradice el casillero, y la hoja muestra una cara en el 03 y una cara grande en el 02. CC lo declara como abierto #1. Es defecto de producto, no incumplimiento del handoff.
2. En el paquete 02 el texto «LO LLAMARON ALBOROTADOR» no se apoya en sus dato_ids (D19, D89, D92, T19). La cita de Saint «alborotador» está en el pool (Q46) y en la narración, pero no entre los ids citados. Además la ancla (herida del pie) no tiene relación con el título (polvo desde 1944) ni con el texto. El script no lo marca como aviso, porque solo coteja cifras.
3. En SALIDA_B el renglón «Foto» sale como «año 1963 (1) el casillero `year` del modelo)». Es el texto crudo de m03 y CC lo declara (abierto #6).
4. `cost_history.json` tiene dos entradas `f58_parte_b`. La primera (04:37:52) vale US$ 0 y es el intento con el argv mal, declarado en abierto #7. El total real es 0.3953.
5. Pendiente de proceso: pegar este veredicto en F58_REPORT.md.

Riesgos que el contrato no cubre: la medida de nombres solo mira los prompts, no la imagen que genera Seedream (los rostros que aparecen en el 02 y el 03 no se evalúan). Tampoco hay chequeo de coherencia título/texto/ancla/dato_ids. Un paquete cuyos tres elementos no se relacionan pasa sin aviso.

## Adenda de CC (Parte B)
- **Fila 14 / observación 5:** este commit pega el veredicto; no queda nada pendiente de proceso.
- **Observación 2 (para el analista):** es cierto y el handoff no lo pide: la validación por código coteja n, campos, estrategias, anclas y cifras (A2 y A4), no la relación título/texto/ancla/dato_ids. En el paquete 02 el texto se apoya en la cita Q46 («alborotador», Saint), que está en el pool y en la narración pero no en los `dato_ids` que Opus citó; la ancla (la herida del pie) no sostiene ni el título ni el texto. Queda como abierto 8 (abajo), sin tocar nada.
- **Observación 4:** la entrada `f58_parte_b` de US$ 0 (04:37:52) es el intento con el argv mal (abierto 7); el gasto real es la segunda (04:38:18), US$ 0,3953.
- **Fila 6:** 126 formas contadas por el script contra 121 del revisor es solo la forma de deduplicar (el script cuenta las claves del dict antes de unir ficha y canon); el resultado es el mismo: 0 coincidencias.
- **Abierto 8 (nuevo):** chequeo de coherencia título/texto/ancla/`dato_ids` dentro de cada paquete: no existe; el paquete 02 pasó sin aviso con un texto que sale de una cita que no citó y con una ancla que no se relaciona con el título. Decide el analista si es regla nueva (iría por handoff) o se deja a la pantalla de revisión.
