# HANDOFF F60 — foto madre por PERSONA + modo secuencia (Seedream v5 Lite /edit, varias fotos por llamada)

Rama `f11-guion-v4` (main no se toca). Topic de prueba: Wittenoom `123bbb64-9fca-4395-8bf4-57d60e219ef1`, **siempre sobre copia de lab** (`lab/hyperframes/f60/base/`, mismo método que `lab/hyperframes/f59/copia_lab.py`). Subagentes en paralelo donde se pueda. `revisor-handoff` al final de cada etapa, veredicto íntegro en `lab/hyperframes/f60/F60_REPORT.md`. Sin tope de dólares: el costo se reporta después.

## Por qué
Hoy solo objetos y lugares tienen foto madre (`foto_madre.py`); las personas salen t2i → Daniel Écija tiene otra cara en cada foto. Omar probó en fal (30-oct): madre + `/edit` en **modo secuencia** (`max_images`, un prompt con varias escenas, todas en una llamada) → cara ≈ 8,3 con 4.5; con **v5 Lite** «igual o mejor» (Omar 16:14). Defecto aceptado: contagio entre fotos del mismo lote.
Simulación del analista: la voz nombra a Daniel en una minoría de sus fotos («él», «su padre», «el pie») y hay dos familias españolas descritas igual → el código no puede saber quién sale. Por eso m03 (Opus) devuelve un casillero de **ruteo** `persona` (OK de Omar 15:45), como ya hace con `people_group` y `year`.

## Decisiones (anotar en `DECISIONES.md` en la Etapa 0, tal cual)
- 2026-10-30 15:42 — Omar: personas con foto madre + Seedream `/edit` en modo secuencia (varias fotos por llamada, un prompt con las escenas). Descartado una-por-pedido.
- 15:45 — Omar: OK al casillero de ruteo `persona` en m03.
- 16:14 — Omar: v5 Lite (el modelo de producción) funciona igual o mejor que 4.5 en secuencia → se usa v5 Lite.
- 16:14 — Omar («sigamos», sobre el voto del analista): «sale la persona» = reconocible aunque sea de espaldas, misma edad y estado que el canon; plano de solo una parte del cuerpo (pie, mano) o foto dentro de otra foto → sin persona. Caps con clip (hoy 1 y 7) entran en una Etapa C aparte.

## Constantes
| valor | origen | quién |
|---|---|---|
| fotos por llamada de secuencia = 6 | prueba de Omar en fal (4.5 y v5 Lite, `max_images` 6). v5 Lite permite más (Omar vio hasta 12); subirlo es decisión de Omar después de ver la Etapa 0 | Omar |
| madres por llamada ≤ 2 | tope existente `_norm_foto_madre_refs` (asset_manager.py) | existente |
| madre solo si la persona sale en ≥ 2 fotos (cuenta `persona` en cualquier posición, en todos los caps, incluidos los de clip) | derivado: con 1 foto no hay cara que mantener | analista |
| motor de la madre de persona = Seedream v5 Lite t2i, `model_id` del perfil (engine_profiles.py:72) | Omar «usemos seedream» 14:59 | Omar |
| tamaño madre = `image_size` del perfil seedream (2560×1440) | existente (engine_profiles.py) | existente |
| timeout de la llamada de secuencia, reintentos, workers | usar los existentes (`_generate_image_raw` timeout, `@error_handler.retry`, `FLUX_MAX_WORKERS`); si alguno no alcanza para N fotos, PARÁ y mostrá la medición | existente |
| orden dentro de un lote = orden del guion (cap, índice de foto) | derivado: fotos vecinas comparten lugar → el contagio molesta menos | analista |
| año de la madre = primer número de 4 dígitos de `era` del canon; sin número → sin año en el prompt | derivado del canon | analista |

Cualquier otro número: PARÁ y preguntá.

## Módulos
| módulo | hoy | después |
|---|---|---|
| `script_engine/m03_visual.py` | casilleros con `people_group`, `year`, `foto_madre_ref`; el bloque del canon lista personas «NUNCA el nombre» | + `persona` (lista, ruteo); el bloque del canon muestra el nombre como dato de ruteo |
| `foto_madre.py` | madre de object/place y props (GPT Image 2) | + madre por persona (Seedream), lee `persona` de `03_visual.json` |
| `script_engine/m06_assembler.py` | registry `__subject__` + props | + `{nombre: foto_madre}` por persona con madre |
| `asset_manager.py` | 1 llamada por foto | + pre-paso de secuencia (caps flux) y función que baja N imágenes y registra N en el costo |
| `qa_studio_server.py` | fix con refs de `foto_madre_ref` | fix y nueva-semilla con la madre de `persona` |

Son 5 → la tanda va partida en etapas con PARADA; cada etapa termina con su salida en texto.

## Tabla de verdad del analista (Wittenoom, `03_visual.json`; `chapters[k]` = posición en la lista, base 0 = cap k+1; img = `image_prompts`, supp = `supplemental_image_prompts`)
| foto | esperado `persona` |
|---|---|
| chapters[1].img[0] (1961, traje) | Daniel Écija |
| chapters[1].img[1], img[3] | Daniel Écija (img[3] también María Bernal) |
| chapters[1].img[4] (dos parejas) | Daniel Écija (+ quizá Ramón de Juan) |
| chapters[1].img[5] (la otra familia) | NO Daniel |
| chapters[2].img[15] | Daniel Écija |
| chapters[3].img[6] | Daniel Écija (dudoso: podría ser Ramón) |
| chapters[3].img[8] (aparte de los otros mineros), img[13] (de espaldas) | Daniel Écija |
| chapters[4].img[4] (1966, de espaldas, ~30) | Daniel Écija o "" (las dos aceptables) |
| chapters[4].img[12], img[13] (1991, 55 años) | "" |
| chapters[4].img[14] (foto sepia en 2023) | "" |
| chapters[0].supp[0] (solo el pie) | "" |
| chapters[0].image_prompt, chapters[0].supp[3] | Daniel Écija — cap con clip, Etapa C |
Si alguna referencia no coincide con lo que describe, PARÁ y reportá.

## Etapa 0 — prueba de secuencia en lab, SIN tocar código de producción
1. Leer el schema de `fal-ai/bytedance/seedream/v5/lite/edit` (mismo método que `lab/hyperframes/f52/schemas_f52.py`) y pegar los parámetros de cantidad (`max_images`, `num_images`) y el límite referencias+salidas. `num_images` queda en 1.
2. Madre de Daniel Écija: Seedream v5 Lite t2i con el prompt de la Etapa B.1 armado a mano con los datos reales; pegar prompt y foto.
3. Las fotos flux de Daniel de la tabla (sin caps con clip) en orden de guion → lotes de 6 → UNA llamada `/edit` por lote, `image_urls=[madre]`, `max_images = len(lote)`. Prompt de secuencia (armado en código, sin LLM):
   ```
   A series of {N} separate photographs of the same man shown in the reference image. Each image is a different scene:
   Image 1: {prompt de la foto 1, sin las frases de aspecto 16:9 y de no-texto}
   Image 2: ...
   Every image: {frase de aspecto 16:9 de los prompts} {NO_TEXT de m03_imagenes_v3}
   ```
4. Pegar por lote: imágenes pedidas/devueltas, si la imagen i es la escena i (mirarlas), segundos, precio real por imagen (pricing de fal para el endpoint `/edit`; `track_seedream` tiene tarifa fija y no sirve), y hoja: madre + todas las fotos, con la foto t2i vieja de cada una al lado.
5. `DECISIONES.md` con las 4 líneas de arriba.
PARADA 0 — `SALIDA_0.md`.

## Etapa A — casillero `persona` en m03 (nada lo consume todavía)
Dos cambios, se declaran los dos (cambian el input y la salida de todos los ítems):
1. Input: en `_format_seedream_canon_block` (m03_visual.py, ~l.457) cada persona documentada lleva su `name` al principio de la línea, y el encabezado pasa a: «PERSONAS DOCUMENTADAS (el nombre es solo para el casillero persona; en la prosa usar appearance_canon, NUNCA el nombre)». El bloque viejo duplicado (~l.1063) no se toca.
2. Salida: texto nuevo concatenado tras `TEXTO_S4_YEAR` dentro de `_si_casilleros`:
```
- persona: a LIST with the exact name, as written in PERSONAS DOCUMENTADAS, of each documented person who is recognisably shown in THIS image (even from behind), at the same age and condition the canon describes — the main one first, at most TWO; [] if none, if only a body part is shown, if they appear inside a photograph or picture within the scene, or if unsure. Routing only — not rendered as text.
```
Esquema: `persona` ARRAY de STRING, en `required` después de `people_group`. Agregar `persona` a `CLAVES_F8_PAPEL` (para que llegue a las supps de caps con clip; la foto del clip NO la recibe por m06 — eso es Etapa C) y a `_iter_image_items`. `persona` NO entra en `CASILLEROS_EDITABLES`. Actualizar `test_module_f50b.py` (l.116, `required[-2:]`).
Prueba: m03 (casilleros) sobre la copia de lab; tabla foto → `persona` contra la tabla de verdad; cada desacuerdo con su ancla y párrafo; diff de 5 ítems contra el `03_visual` anterior (la prosa no debe traer nombres propios: grep de los nombres del canon en `prompt`).
PARADA A.

## Etapa B — madre por persona + secuencia en caps flux
1. `foto_madre.py`: lee `persona` de `data/scripts/_steps/<id>/03_visual.json`; madre para cada persona del canon con ≥ 2 fotos. Motor Seedream t2i del perfil; si el motor activo no es seedream o hay rechazo → sin madre de persona y aviso (no cae a GPT). Mismo skip/adopción manual. Destino `output/<vid>/foto_madre/<slug>.png` (aceptar el slug actual que come acentos), path en `documented_people[i].foto_madre`.
   Prompt (en código, sin LLM; NO usar `_STYLE` con «faceless»; reusar `v3img.ESTILO_C` y `v3img.NO_TEXT`, no retipearlos):
   ```
   Head-and-shoulders portrait of {appearance_canon sin la parte de ropa y sin estados del cuerpo (vendas, heridas)}. {appearance del people_group más frecuente en las fotos donde su nombre está en `persona` (cualquier posición); empate → el del primero en orden de guion}. Neutral expression, facing the camera, plain mid-grey background, soft even light. {ESTILO_C con el año de la madre} {NO_TEXT}
   ```
   Ropa fuera de la madre (la pone cada escena). Cómo se recorta «la parte de ropa y estados» de `appearance_canon`: si no hay forma general sin lista de palabras, PARÁ y mostrá 5 `appearance_canon` reales; el analista decide. Pegar el prompt real de Daniel.
2. `m06_assembler.py`: registry + `{nombre: foto_madre}` por persona con madre.
3. `asset_manager.py`: regla única de madres para TODOS los caminos (secuencia, una foto, QA): refs = madres de `persona` (en orden) + `foto_madre_ref`, principal primero, tope 2. Pre-paso antes de los caps flux: entran a secuencia SOLO los ítems sin archivo en disco, con `persona[0]` en el registry, `len(persona) == 1`, `foto_madre_ref == []` y sin cartel (`text_in_image.present` falso) → su única ref es la madre de `persona[0]` → agrupar por `persona[0]`, orden de guion, lotes de 6 → una llamada `/edit` secuencia por lote → cada imagen al `out_path` de su ítem. El resto de ítems con persona va por el camino de una foto con la regla única. Función nueva que baja las N imágenes y registra N en el costo con el precio real. El pre-paso devuelve sus resultados por (cap, idx) a `_process_flux_chapter`: manifest `status: "ok_secuencia"` (no `skipped_exists`), con persona y lote; `ok_secuencia` cuenta como donante en el piso anti-desync. Ítem que la llamada no devolvió → camino normal `/edit` de una foto con las mismas madres. Lotes de distintas personas en paralelo. El validador de visión está apagado: la secuencia no lo usa. Grade igual que cualquier foto.
4. `qa_studio_server.py`: `resolve_fix_entry` devuelve `persona`; `_fix_core` y `_reseed_core` usan la regla única de madres del punto 3, agregadas solo en `entry` (no en `it` ni en el ítem guardado). Si el pedido de Omar cambia quién sale, `persona` no cambia (no es editable): decirlo en el texto a Omar.
5. Tests: agrupación (7 → 6+1), persona con 1 foto → t2i, lote incompleto → caída a una foto, `ok_secuencia` en manifest y piso anti-desync, `persona` llega a supps de caps con clip, QA fix y reseed con persona, tope 2. Nada que borrar (es un camino nuevo; si CC encuentra algo que queda muerto, lo nombra y lo borra).
Prueba: copia de lab, solo fotos con `persona` de caps flux. Hoja por persona y costo.
PARADA B.

## Etapa C (después, mismo handoff) — caps con clip
Supps y foto inicial del clip (m06 hoy copia `image_prompt` sin `image_f8` → hay que llevar la `persona` de la foto del clip; hoy por `_generate_supplementals_for_veo_chapter` y `_process_veo_chapter`, sin registry) entran al pre-paso. La foto final del clip ya sale por `/edit` desde la inicial (hereda la cara). Diseño detallado al cerrar B.

## Fuera de alcance
Look 1962 (grano, saturación), anacronismo del barco, mancha roja de la venda y rechazo de clips, etiqueta «Flux-PRO» del log: lista aparte.
