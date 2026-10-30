# HANDOFF F58 — miniaturas como 3 paquetes (título + texto + foto) con la máquina de fotos de producción

Analista → CC · 2026-10-29 · rama `f11-guion-v4` · decisiones de Omar 23:23 y 23:38. Auditado por subagente (25 correcciones aplicadas).

## Por qué (medido en Wittenoom `123bbb64…`)
1. `m09_packaging.py` genera por separado 6 títulos + 6 textos (Gemini) y 3 ideas de foto (hero, Gemini), y Omar los combina a mano.
2. El hero no usa la máquina de fotos de producción: su prompt dice «SEEDREAM 4.5», no ve el canon y nombró personas reales en `hero_iterations.json` («Daniel Écija», «Maitland Parker», «Mercedes de Juan»). En producción salieron 0 nombres en 96 fotos (F51c).
3. Las «bases existentes» salen de `_lab_out/lab_fidelity_punch_chat56/audit_map.csv`, con puntajes de otro video, y se buscan por nombre de archivo en el topic actual.
4. Lee `data/scripts/<tid>.json` (del 28-oct, narración vieja) y solo sus 10 `verified_facts`.
5. El título elegido dice «el sitio más tóxico» y el dato dice «más grande». El overlay «NIÑOS JUGABAN VENENO» está mal construido.
6. `compose_thumbnail` parte las líneas por cantidad de palabras y no mide si cabe: con 5 palabras ocupa el 71 % del ancho y tapa la cara.

## Etapa 0 — anotar en `DECISIONES.md` (primer commit, tal cual)
- `2026-10-29 23:23 · **F58:** las miniaturas salen como 3 PAQUETES (título + texto de miniatura + foto, una unidad por paquete, estrategias distintas) en una llamada de Opus 5.5 que lee el gancho F56, la narración y el pool; la foto de cada paquete sale de la máquina de producción (casilleros Opus + armado C + aspecto del grupo del canon); se borra el camino Gemini (6 títulos + 6 overlays sueltos y el hero) · Omar · F58`
- `2026-10-29 23:23 · **F58:** se borra la lista de bases «existentes» (audit_map de otro video); en la revisión se puede usar como base cualquier foto del video · Omar · F58`
- `2026-10-29 23:23 · **F58:** el texto de la miniatura va en la mitad izquierda (la foto pone a la persona en la mitad derecha); las líneas se parten por ancho y la letra se achica hasta caber (tope 2 líneas) · Omar · F58`
- `2026-10-29 23:38 · **F58:** la foto de cada paquete sale de una oración literal del GANCHO (cap 1) elegida por Opus, por la máquina de producción tal cual más una oración de composición (cumple F54 B.4); del pedido viejo se caen «sin clickbait/emojis», «si dudás, omití» y «solo prometé lo que la narración cuenta», y se queda «el texto no describe la foto: abre una pregunta»; la foto de la miniatura va sin cartel (sin texto dentro) · Omar · F58`
- `2026-10-29 23:10 · chascada: PEDIDO_FINAL sin el movimiento aprobado · Omar · F58`

## Constantes
| constante | valor | origen | quién |
|---|---|---|---|
| `N_PAQUETES` | 3 | `FRESH_THUMBS = 3` (m09:70) | Omar 23:23 |
| modelo y effort del pedido | `MODELO_CASILLEROS` + `ESFUERZO[MODELO_CASILLEROS]` (= high) | m03_visual:133, guion_v4:66 | Omar 2026-10-28 11:15 |
| reintentos de validación | `MAX_RETRY_ATTEMPTS` | ya existe (m03_visual:867) | existente |
| título ≤ 70 (pedido) / recorte 90 | `MAX_TITLE_CHARS = 90` | `_META_SYSTEM`, m09:67 | existentes |
| texto 2–4 palabras, MAYÚSCULAS | — | `_META_SYSTEM`, `_validate_text` | existente |
| tags ≤ 450 / descripción 150–300 palabras | `MAX_TAGS_CHARS` | m09:68, `_META_SYSTEM` | existentes |
| 1280×720, `THUMB_TEXT_SCALE` 0,15 (108 px), `THUMB_STROKE_PX` 8, `THUMB_MARGIN` 56, `THUMB_MAX_LINES` 2, interlínea `font_px + 10` | — | m09:52-66, 454 | existentes |
| ancho de la zona del texto | `THUMB_W // 2 − THUMB_MARGIN` = 584 px | derivado: mitad izquierda | Omar 23:23 |
| piso de la letra | `int(108 × 0,7)` = 75 px, fijo | clamp 0,7 de `size_factor` (m09:449) | existente |
| paso del achique | 1 px | derivado | — |

Si hace falta otro número: PARADA y se pregunta.

## Módulos que toca
| módulo | hoy | después |
|---|---|---|
| `script_engine/m09_packaging.py` | Gemini 6+6 + hero; bases de audit_map; texto por palabras | Opus 3 paquetes; foto por producción; texto por ancho |
| `script_engine/m09_review_server.py` | grilla existing/fresh + crítica al hero | 3 paquetes terminados; editar y rehacer foto; base = foto `_graded` del video |
| `script_engine/m03_visual.py` | `_render_prompts_seedream` / `_build_seedream_prompt_step2` | kwargs con default byte-idéntico (A3) |
| `script_engine/m03_imagenes_v3.py` | `armar(it, anio, grupos)` | `armar(…, composicion="")`, default byte-idéntico |
| `script_engine/video_prompt.py` + `asset_manager.py:689` | `PEDIDO_FINAL` con el movimiento | sin él (A8, **sí cambia la foto final de los clips de producción**) |
| `test_fase3.py`, `test_m09_*.py`, `test_module_f57.py` | — | se adaptan |

Paralelo: un subagente para todo m09 (A1–A7, es un solo archivo) + review_server después de fijar su API; otro para A8; otro para los kwargs de m03 (A3). Ch02 md5 `f792f3d4…` y las suites siguen iguales; `test_module_f57` cambia solo por A8.

## Parte A — código, sin red (US$ 0)

**A1. Entradas.**
- Narración: `_steps/<tid>/01b_narration.json` (`chapters[].chapter_number/narration`); el cap 1 entero es el GANCHO.
- Pool: `_steps/<tid>/00_pool_v3.json`.
- Topic para A3: armado como en producción (`fase1_5._load_topic_by_id` + `asegurar_canon`, fase1_5:663-680, y `_f8` como en m03_visual:2153-2158).
- Ya no se lee `data/scripts/<tid>.json` (se borran `_load_canonical` y el uso de `verified_facts`).
- Si falta un archivo: PARADA con su nombre, sin volver a lo viejo.
- Bloque POOL, con los ids tal cual (sin renumerar) y una línea por ítem, en este orden:
  - `D01: <texto>`
  - `T01 · <fecha or '-'> · <evento>`, como m03_expediente:179
  - citas con `linea_cita` (m03_expediente:125-130)
  - `P01: <nombre> — <rol>`
  - `L01: <nombre> — <rol>`
- Entran todos los ítems, incluidas las citas `verificada_parcial`.
- `cifras_canonicas`: en Wittenoom viene vacío; si viene lleno, cada entrada va en JSON compacto, una por línea, al final.

**A2. El pedido de paquetes** (constante `PEDIDO_PAQUETES` en m09, íntegra; `{n}` = `N_PAQUETES`):
```
Armás el empaquetado de un video documental de historia oscura en español neutro-latino: el título de YouTube, el texto que va sobre la miniatura y la oración del gancho que muestra la foto de la miniatura. Todo sale del material de abajo: un dato que no está en el POOL no existe.

Devolvé {n} PAQUETES. Cada paquete es una unidad: título, texto de la miniatura y foto. Cada paquete usa una estrategia distinta, elegida de esta lista: (1) dato brutal o cifra, (2) misterio o pregunta, (3) acusación, (4) lugar y año, (5) contradicción o ironía histórica, (6) consecuencia humana.

Por paquete:
- estrategia: el número de la lista.
- titulo: hasta 70 caracteres, con el gancho al principio. Toda cifra, fecha o nombre sale tal cual de un ítem del POOL.
- dato_ids: los ids de los ítems del POOL de los que salen el título y el texto.
- texto: de 2 a 4 palabras en MAYÚSCULAS para encima de la miniatura. No describe la foto ni repite el título: abre una pregunta que solo el video responde.
- cap_que_paga: el número del cap cuya narración responde el texto.
- ancla: la oración del GANCHO que muestra la foto, copiada tal cual; una oración distinta en cada paquete.

descripcion: de 150 a 300 palabras. La primera oración es el gancho, sin mentir; después, contexto fiel al material y una línea de cierre del canal.
tags: la mayoría en español y de 3 a 5 en inglés; los nombres propios sirven en los dos idiomas; entre todos, hasta 450 caracteres.

GANCHO (la narración del cap 1 entera; la primera oración del título y el sujeto de la miniatura salen del GANCHO):
{gancho}

NARRACIÓN (caps 2 a 7):
{narracion}

POOL (única fuente de cifras, fechas y nombres):
{pool}
```
- `{narracion}` = `[Cap N] <narración>` por cap 2–7, sin truncar.
- Llamada: `claude_helpers.call_json(prompt, model=MODELO_CASILLEROS, system_instruction=None, response_schema=…, effort=ESFUERZO[MODELO_CASILLEROS], description="m09:paquetes")`.
- Esquema: `{"paquetes": [{"estrategia": INTEGER, "titulo": STRING, "dato_ids": [STRING], "texto": STRING, "cap_que_paga": INTEGER, "ancla": STRING}], "descripcion": STRING, "tags": [STRING]}`.
- Lo que el esquema no puede exigir lo valida el código, con reintentos `MAX_RETRY_ATTEMPTS` como `_call_with_validation_retry`; si fallan todos, PARADA:
  - exactamente n paquetes;
  - todos los campos llenos;
  - estrategias distintas;
  - cada `ancla` es una oración literal del gancho (comparada con espacios normalizados);
  - anclas distintas.
- Después: `titulo[:MAX_TITLE_CHARS]`, texto en mayúsculas, `_truncate_tags` y `with_icon_credit` (se conservan).
- Se borran: `_META_SYSTEM`, `_META_SCHEMA`, `META_TEMP`, `generate_metadata`, `_meta_user_prompt`, `_HERO_SYSTEM`, `_HERO_*_SCHEMA`, `generate_hero_prompt`, `generate_hero_prompt_iter`, `_narration_for_hero`, `HERO_NARRATION_PER_CAP`, `_gemini_json`, los imports `gemini_client`/`gt`/`DOCTRINE_*`, `GANCHO_INSTRUCCION` (su texto queda en el pedido), `_bloque_gancho` y `_load_canonical`.
- Se reescribe el docstring del módulo.

**A3. La foto = producción, cap 1, las 3 anclas.**
- Camino: `_render_prompts_seedream` del cap 1 con las 3 anclas, en una llamada de casilleros.
- Reparto a beats: `assign_beats` funciona porque las anclas son literales; se hace como en `_f8_refill` (m03_visual:727-739, `force_assign`/`refill=True`).
- No corren `_f8_fix_cap` ni el refill ESTABLISHING. Los reintentos de validación de producción sí corren.
- Kwargs nuevos, todos con default byte-idéntico:
  - `_build_seedream_prompt_step2(…, clip_apertura=True)`: con False no va el bloque `OPENING MOTION CLIP` (m03_visual:553-561);
  - `_render_prompts_seedream(…, composicion="", sin_cartel=False)`.
- Con `sin_cartel=True`, `text_in_image.present` pasa a false antes de `armar`.
- `armar(…, composicion=…)` pone la composición después de `tecnica`.
- `COMPOSICION_MINIATURA` (origen: la CAPA CTR de `_HERO_SYSTEM` + la mitad de la decisión 23:23):
```
The person fills the right half of the frame, face and torso large; the left half is dark, uncluttered negative space.
```
- Excepción declarada a D4 (izquierda/derecha, `LR_RE`): un test fija que `f8_backstop` deja esta oración intacta.
- Foto: `asset_manager._generate_image_raw(prompt, out, use_ultra=False)`. Si falla o la rechazan, el paquete queda sin foto con el motivo literal y los otros siguen.
- En `SALIDA_A.md` §A3 va el camino exacto con archivo:línea. Si hace falta cambiar producción más allá de los kwargs con default: PARADA A3.

**A4. Cifras por código.**
- `voz_utils.numeros` (voz_utils:38) sobre título y texto; cada número (`parse_int`) tiene que estar entre los números (`parse_int`) de algún ítem del pool.
- Si no está, el paquete lleva el aviso «⚠ cifra sin dato: <número>»; ni se reintenta ni se corta.
- `dato_ids` solo se muestra.

**A5. Texto encima (`compose_thumbnail`).**
- Zona: mitad izquierda (584 px), abajo como hoy. El ancho de una línea se mide con `textbbox(…, stroke_width=THUMB_STROKE_PX)`.
- Búsqueda: desde 108 px (× `size_factor`, sin bajar del piso) se baja de a 1 px hasta 75. En cada tamaño, entre una línea y cada corte posible en 2, gana el de menor ancho máximo. Desempate: primero la de 1 línea; después, el corte más a la izquierda. El primer tamaño en que cabe gana.
- Si no cabe en 75 px: se compone en 75 y se avisa «⚠ no cabe».
- Se borra `_wrap_lines`.
- Tabla que los tests reproducen (líneas y tamaño exactos; anchos ±1):

| texto | líneas | anchos con borde | px |
|---|---|---|---|
| LOS DEJARON MORIR | LOS DEJARON / MORIR | 545 / 277 | 108 |
| ¿QUIÉN SABÍA EL PELIGRO? | ¿QUIÉN SABÍA / EL PELIGRO? | 553 / 501 | 108 |
| ¿POR QUÉ NO LIMPIARON? | ¿POR QUÉ NO / LIMPIARON? | 530 / 503 | 108 |
| BORRADA DEL MAPA | BORRADA / DEL MAPA | 381 / 417 | 108 |
| 3 MILLONES DE TONELADAS | 3 MILLONES / DE TONELADAS | 486 / 583 | 108 |
| JUGABAN CON VENENO | JUGABAN / CON VENENO | 380 / 499 | 108 |
| 1.269 DE 1.328 HABITANTES MURIERON | — | no cabe | ⚠ 75 |

**A6. Bases.**
- Se borran `shortlist_existing`, `SHORTLIST_EXISTING`, `_resolve_png` y la lectura de `audit_map.csv`, con sus tests.
- La base de un paquete es su foto. Como alternativa, cualquier foto del video: las `*_graded.png` de `_assets_dir(tid)`, o la cruda si no tiene graded.
- El servidor solo sirve rutas dentro de `_assets_dir(tid)`, `thumb_candidates/` y `publish/`.

**A7. Revisión, CLI y archivos viejos.**
- `--candidates` produce, por paquete, `thumb_candidates/paquete_NN_base.png` y `paquete_NN.png` (ya compuesta), y `metadata.json` con `paquetes`, `descripcion`, `tags` y `avisos`.
- `metadata.json.paquetes` acumula con índice global; la descripción y los tags son los de la última tanda.
- `candidates_ready` exige la clave `paquetes`.
- Lo viejo de Wittenoom (`metadata.json`, `metadata_candidatos.md`, `hero_iterations.json`, `thumb_final_*`, `_qa_backups`) se mueve a `publish/_antes_f58/`. No se borra.
- La página muestra por paquete: la miniatura, el título con su cuenta de caracteres, el texto, los datos (`id: texto`), `cap_que_paga`, el ancla y los avisos.
- Se pueden editar el título y el texto (recompone sin red), elegir otra base y «rehacer foto» (A3 solo para esa ancla). «3 paquetes nuevos» corre todo de nuevo sin pisar números.
- `--compose --paquete N` reemplaza a `--title N`. El CHECKLIST sigue igual.
- Se mantiene la firma `run_candidates(tid, video_path=None, review=False)`.
- Se borran `--only-fresh`, `--skip-fresh`, el panel de crítica, `_record_iteration`/`_load_iterations` y `_render_concept_variations`.
- `test_fase3.py:122-126` usa `--only-fresh` como ejemplo de paso de flags: cambiarlo por otro flag que exista.
- `--auto-first` de QA Studio sigue andando: sin paquetes, genera.

**A8. Chascada.** `PEDIDO_FINAL` queda así, íntegro:
```
You write an edit instruction for an image-editing model. The attached image is the first frame of a {segundos}-second continuous documentary shot. Write the instruction that turns it into the last frame of that same shot.
The last frame keeps the same place, the same people with the same faces, bodies and clothes, the same light and the same photographic style; it changes only what changes during those seconds, following the narration.
STILL IMAGE PROMPT (what the first frame was asked to show):
{prompt_foto}
NARRATION DURING THE SHOT (Spanish; the last frame shows the moment at its end):
{voz_clip}
Return only the edit instruction: one paragraph of plain English prose describing the last frame.
```
- Sale el parámetro `video_prompt_aprobado` de `armar_body_final`, de `escribir_final` (video_prompt:130, 183, 188) y de su llamador (asset_manager:689).
- Se actualizan los docstrings (video_prompt:128-129, 186) y la copia de `test_module_f57.py` (:132-153, 179).

**A9. Tests.** `test_module_f58.py` (sin red) cubre:
- A1: PARADA si falta un archivo; el formato de las 5 clases del pool.
- A2: el usuario armado con Wittenoom; la validación (ancla no literal, estrategia repetida, n distinto → reintento).
- A3: con un `_llamar_casilleros` falso (3 anclas, sin el bloque de clip, sin cartel, composición en su lugar, `f8_backstop` no la toca).
- `armar`, `_build_seedream_prompt_step2` y `_render_prompts_seedream` sin los kwargs nuevos: byte-idénticos a hoy sobre ítems de Wittenoom.
- A4: un número ajeno → aviso; «46.840» y «46,840» → mismo número.
- A5: la tabla.

Además: adaptar `test_m09_packaging.py`, `test_m09_review_server.py`, `test_fase3.py` y `test_module_f57.py`, y correr las suites rápida y amplia, el md5 de ch02 y `MAPA --check`.

**SALIDA_A.md:** módulos antes → después; el camino de A3 con archivo:línea; el usuario de A2 armado para Wittenoom entero (con cuántos caracteres tiene); la tabla de A5 que sale de los tests; el antes y el después de A8; las suites. **PARADA A.**

## Parte B — corrida real en Wittenoom (con el OK del analista a A)
- Comando: `python -m script_engine.m09_packaging 123bbb64-9fca-4395-8bf4-57d60e219ef1 --candidates`.
- `SALIDA_B.md` lleva:
  - los 3 paquetes enteros, con el texto de cada `dato_ids`, y los avisos;
  - los 3 prompts de foto armados, enteros;
  - si algún prompt nombra a alguien de `documented_people` (es una medida, no un freno);
  - la hoja `lab/hyperframes/f58/hoja_paquetes.jpg` con las 3 miniaturas lado a lado;
  - la descripción y los tags;
  - el gasto desglosado (`m09:paquetes`, casilleros y fotos).
- Las imágenes no van a git. **PARADA B.**

## Reporte
`lab/hyperframes/f58/F58_REPORT.md`: módulos, decisiones de CC, salidas, «lo que queda abierto» y el veredicto íntegro de `revisor-handoff`, invocado como en F57. `ESTADO_SESION`, stickers y MAPA al día.
