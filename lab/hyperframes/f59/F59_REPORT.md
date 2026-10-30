# F59 — Reporte final: QA Studio arregla con la máquina de producción (foto y clip) + chascadas

Handoff: `lab/hyperframes/f59/HANDOFF_F59_qa_studio_produccion.md` (md5 `9325c5ee7e284e8012aedcf8d1284f07`). Rama `f11-guion-v4`. Modelo Opus high.

## Etapas 0 y A (cerradas, con OK del analista)

- **Etapa 0** (`SALIDA_0.md`, commits `e5b1dbf`, `e612b70`, `f7265fe`): DECISIONES con las 6 líneas del handoff; cuadros vacíos de la galería confirmados (los `*_graded.png` entraban al glob); copia de lab `base/` (629,9 MB, ignorada); candidatos B2. US$ 0. Veredicto: CUMPLE CON OBSERVACIONES.
- **Etapa A** (`SALIDA_A.md`, commits `724c948`, `10f08c0`, `f412923`): `armar_item` sale de m03 byte-idéntico (96/96); `_fix_core` con Opus sobre `CASILLEROS_EDITABLES` + `armar_item` + Seedream + grade + guardado en 03_visual y guion vivo; `_clipfix_core` con Opus sobre el movimiento + foto final F57 + `_generate_clip` G→K; galería sin graded (chascada del analista); hints y «clip» en el front; `COMPOSICION_MINIATURA` nueva; `foto_final_del_clip` sin parámetro muerto; lo viejo borrado con sus tests. US$ 0. Veredicto: CUMPLE CON OBSERVACIONES.

## Etapa B — prueba real en Wittenoom (copia de lab) · PARADA B

Resumen: **B1** 3/3 fotos con la oración nueva (byte-identidad con F58 probada con la oración vieja, 3/3). **B2** ok: Opus cambió solo `action` («looking directly into the camera with a furrowed brow»), el scrub no sacó nada, foto rehecha con la misma semilla; el abogado mira a cámara con el ceño fruncido (hoja `b2/hoja_b2.jpg`). **B3** ok=False: Opus editó bien el movimiento («The camera stays completely still… Only fine red dust moves, rising slowly…»), la foto final salió (SSIM 0,516), pero **Gemini y Kling rechazaron el clip por contenido**; el mp4 viejo quedó intacto (md5 igual) y el movimiento aprobado no se tocó. Total **US$ 0,384**.

### Hallazgo de B3 (por qué rechazaron G y K)

La foto inicial de ch01 en la copia (`ch01_img_01.png`, 28-oct) es un **primer plano de un pie con una venda manchada de rojo**: viene del guion vivo del 28 («A close shot of a young Spanish miner's foot… wrapped in a soiled white bandage»), no del `03_visual.json` del 29 que la copia usa («medium shot of the young miner against the corrugated iron wall»); es el desfase que la Etapa 0 (§5.1) dejó anotado. En producción (F57) Opus escribe el prompt del motor **mirando la foto**, así que el prompt que fue a Gemini empieza «Close on a man's bare foot wrapped in a frayed white bandage stained red…» (el que está dentro del rechazo literal) y la instrucción de la foto final habla de «rust-red stains». Gemini lo marcó «dangerous content» y Kling «model_moderated». El clip viejo del 28-oct lo hizo Veo (manifest `engine: veo`), antes de la cadena G→K del 29-oct. Es decir: el editor de QA y la cadena funcionaron como están diseñados (rechazo → mensaje con los rechazos literales, mp4 intacto); lo que no pasó el filtro es la foto vieja de la copia, no el pedido de Omar. En un guion fresco (m03 + fotos del mismo 03_visual) la foto de ch01 sería el plano medio y este caso no se da; no se re-corrió con otra foto porque el handoff pide ch01 tal cual y la prueba ya mostró el camino del rechazo de punta a punta.

### Salida B (íntegra)
Runner: `lab/hyperframes/f59/parte_b.py` (`QAState(tid, base_dir=lab/hyperframes/f59/base)`, `_fix_core` y `_clipfix_core` directo, dentro de `cost_tracker.start_video('f59_parte_b')`). 620.1 s de reloj. Topic `123bbb64-9fca-4395-8bf4-57d60e219ef1`. Log: `parte_b.log`; todo: `parte_b.json`.

## B1 · Composición (una variable): los 3 paquetes de F58 con la oración nueva, sin LLM

- Oración F58: «The person fills the right half of the frame, face and torso large; the left half is dark, uncluttered negative space.»
- Oración F59 (`COMPOSICION_MINIATURA`, DECISIONES 08:22): «The main subject fills the right half of the frame; the left half is dark, uncluttered negative space.»
- Casilleros = `raw_llm_prompt` de `output/123bbb64-9fca-4395-8bf4-57d60e219ef1/publish/metadata.json`; `anio`/`anio_fuente` del paquete; `sin_cartel=True`, `escala=False`, `lang=en`; `armar_item` → `m09.foto_paquete` (Seedream, `use_ultra=False`) → `compose_thumbnail` con el texto del paquete.

### Paquete 01 — estrategia 1 · «¿QUÉ RESPIRÓ ALLÍ?»

- Con la oración VIEJA el prompt rearmado es byte-idéntico al de F58: **True** (US$ 0).
- Diff del prompt F58 → F59 (por oración):
    -The person fills the right half of the frame, face and torso large; the left half is dark, uncluttered negative space.
    +The main subject fills the right half of the frame; the left half is dark, uncluttered negative space.
- Foto: lab/hyperframes/f59/b1/paquete_01_base_f59.png · 49.1 s · compuesta `lab/hyperframes/f59/b1/paquete_01_f59.png`
- `_f8_problemas`: None · `_f8_slots_scrub`: None · `_f8_texto_fuera`: None

**prompt F59 (el que fue a Seedream):**

    A young adult Spanish migrant miner, olive skin, short dark early-1960s hair, lean work-hardened build, sun-weathered face, in a dust-coated short-sleeved work shirt and drill trousers, one foot wrapped in a pale bandage and the other in a heavy work boot. Stands posing stiffly for a family portrait, weight shifted onto his good leg, the bandaged foot set forward on the ground. Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes. Wittenoom company town, 1963: in front of a low corrugated-iron and fibro-cement company house, its yard surfaced with crumbly blue-grey crocidolite tailings. Hard cold overcast desert light, flat and shadowless, isolating the figure against the pale wall. Medium shot, eye-level, frontal like a period box camera, 50mm lens, moderate depth of field, slightly soft period film grain. The main subject fills the right half of the frame; the left half is dark, uncluttered negative space. A grainy 35mm documentary photograph taken in 1963, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.

### Paquete 02 — estrategia 3 · «LO LLAMARON ALBOROTADOR»

- Con la oración VIEJA el prompt rearmado es byte-idéntico al de F58: **True** (US$ 0).
- Diff del prompt F58 → F59 (por oración):
    -The person fills the right half of the frame, face and torso large; the left half is dark, uncluttered negative space.
    +The main subject fills the right half of the frame; the left half is dark, uncluttered negative space.
- Foto: lab/hyperframes/f59/b1/paquete_02_base_f59.png · 61.6 s · compuesta `lab/hyperframes/f59/b1/paquete_02_f59.png`
- `_f8_problemas`: None · `_f8_slots_scrub`: None · `_f8_texto_fuera`: None

**prompt F59 (el que fue a Seedream):**

    The bandaged foot of a young Spanish migrant miner resting on tailings-surfaced ground, a dusty trouser cuff above it, a jagged fragment of blue crocidolite asbestos lying beside it. The foot rests motionless while the loose fibrous fragment sheds fine threads and powder onto the bandage. Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes. A Wittenoom house yard, 1963, the ground compacted with loose blue-grey crocidolite tailings and red-ochre dust. Hard cold directional overcast light raking across the fibres. Detail shot, high angle looking down, macro-leaning 100mm lens, shallow depth of field, fibres sharp, background soft. The main subject fills the right half of the frame; the left half is dark, uncluttered negative space. A grainy 35mm documentary photograph taken in 1963, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.

### Paquete 03 — estrategia 4 · «NADIE SACÓ UNA PALADA»

- Con la oración VIEJA el prompt rearmado es byte-idéntico al de F58: **True** (US$ 0).
- Diff del prompt F58 → F59 (por oración):
    -The person fills the right half of the frame, face and torso large; the left half is dark, uncluttered negative space.
    +The main subject fills the right half of the frame; the left half is dark, uncluttered negative space.
- Foto: lab/hyperframes/f59/b1/paquete_03_base_f59.png · 36.5 s · compuesta `lab/hyperframes/f59/b1/paquete_03_f59.png`
- `_f8_problemas`: None · `_f8_slots_scrub`: None · `_f8_texto_fuera`: None

**prompt F59 (el que fue a Seedream):**

    Vast abandoned blue-grey asbestos tailings dumps spilling down the rocky red walls of a Pilbara gorge where the erased mining town once stood. The tailings lie exactly where they were dumped, eroding in slow streaks toward a dry creek bed, the empty town site beyond reduced to bare cleared ground. Wittenoom gorge in the present day: demolished, emptied town site, a permanent barricade across the old road entrance, sparse spinifex, 2026. Cold overcast daylight, flat and colourless over the gorge. Extreme wide shot, high angle aerial view, wide-angle lens, deep depth of field. The main subject fills the right half of the frame; the left half is dark, uncluttered negative space. A grainy 35mm documentary photograph taken in 2026, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.

Hojas: `lab/hyperframes/f59/hoja_paquetes_f59.jpg` (las 3 compuestas F59, lado a lado) y `lab/hyperframes/f59/hoja_paquetes_f58_vs_f59.jpg` (arriba F58, abajo F59). No van a git.

## B2 · Foto: `ch03_img_08` — «antes» desde 03_visual + `_fix_core`

- Pedido: «que mire hacia la cámara, con el ceño fruncido». Ancla: ««El mero hecho de que haya nubes de polvo no significa que ese polvo sea peligroso», dijo el defensor del empleador.»
- Semilla: `_seed_for_subject(tid, 'main_subject')` = 956889816 (la misma en la foto antes y en el fix). `use_ultra=False` (ch03 no es gancho). Sin foto madre (`foto_madre_ref` vacío, registry vacío).
- La foto del 28-oct que estaba en la copia (del guion vivo viejo) quedó aparte en `lab/hyperframes/f59/b2/ch03_img_08_28oct.png`.
- Foto «antes» (prompt de 03_visual, 89.0 s): `lab/hyperframes/f59/b2/antes.png` → grade `lab/hyperframes/f59/b2/antes_graded.png`.
- `_fix_core` → ok=**True** · 42.0 s · texto a Omar: «foto rehecha; casilleros editados: action. El filtro de producción no sacó nada.»
- Año: antes ['1949', '1) el casillero `year` del modelo'] → después ['1949', '1) el casillero `year` del modelo'].
- Guion vivo de la copia = 03_visual (prompt y raw_llm_prompt): True.
- Backups en `base/.../assets/_qa_backups/`: 03_visual.json.20261030_145245.bak.json, 123bbb64-9fca-4395-8bf4-57d60e219ef1.json.20261030_145245.bak.json, ch03_img_08.png.20261030_145245.bak.png, ch03_img_08_graded.png.20261030_145245.bak.png.

**Casilleros que Opus cambió (antes → después):**

- `action`:
    antes:   "standing at the head of the table, one palm open as he dismisses the dust clouds"
    después: "standing at the head of the table, looking directly into the camera with a furrowed brow, one palm open as he dismisses the dust clouds"

**Lo que devolvió Opus (salida cruda, por llamada):**

- `qa:fix_foto ch03_img_08.png` · 5.9 s:
    {"subject": "The employer's advocate, a middle-aged Anglo-Australian man, heavy build, in a dark double-breasted suit", "action": "standing at the head of the table, looking directly into the camera with a furrowed brow, one palm open as he dismisses the dust clouds", "setting": "the same 1949 arbitration room, tall window behind him, files stacked on the table", "lighting": "overcast window light, same as the hearing", "camera_angle": "eye-level over the shoulders of seated listeners", "lens_technique": "85mm, shallow depth of field, listeners' shoulders out of focus", "shot_scale": "medium", "text_in_image": {"present": false, "text": "", "font": "", "location": ""}, "year": "1949"}

**Diff del prompt (por oración):**

    -Standing at the head of the table, one palm open as he dismisses the dust clouds.
    +Standing at the head of the table, looking directly into the camera with a furrowed brow, one palm open as he dismisses the dust clouds.

**Informe del scrub** (`_f8_slots_scrub`: None · `_f8_problemas`: None · `_f8_texto_fuera`: None).

**Casilleros antes (03_visual):**

    "subject": "The employer's advocate, a middle-aged Anglo-Australian man, heavy build, in a dark double-breasted suit"
    "action": "standing at the head of the table, one palm open as he dismisses the dust clouds"
    "gaze_interaction": "facing the union men, seen over their shoulders, his gaze level and unhurried; dust motes drift in the window beam beside him"
    "setting": "the same 1949 arbitration room, tall window behind him, files stacked on the table"
    "color_palette": "charcoal suit, varnished timber, pale window glare, floating grey dust motes"
    "props_detail": "a beam of window light thick with drifting dust motes beside the speaker"
    "shot_scale": "medium"
    "camera_angle": "eye-level over the shoulders of seated listeners"
    "lens_technique": "85mm, shallow depth of field, listeners' shoulders out of focus"
    "lighting": "overcast window light, same as the hearing"
    "mood": "a calm upright figure framed by visible floating dust, listeners' shoulders stiff and still"
    "style": "documentary photographic realism, dark-history, faceless"
    "text_in_image": {"present": false, "text": "", "font": "", "location": ""}
    "hard_fact_ids": []
    "people_group": ["company_owners_and_managers", "unions_and_labour_arbitration"]
    "year": "1949"

**Casilleros después:**

    "subject": "The employer's advocate, a middle-aged Anglo-Australian man, heavy build, in a dark double-breasted suit"
    "action": "standing at the head of the table, looking directly into the camera with a furrowed brow, one palm open as he dismisses the dust clouds"
    "gaze_interaction": "facing the union men, seen over their shoulders, his gaze level and unhurried; dust motes drift in the window beam beside him"
    "setting": "the same 1949 arbitration room, tall window behind him, files stacked on the table"
    "color_palette": "charcoal suit, varnished timber, pale window glare, floating grey dust motes"
    "props_detail": "a beam of window light thick with drifting dust motes beside the speaker"
    "shot_scale": "medium"
    "camera_angle": "eye-level over the shoulders of seated listeners"
    "lens_technique": "85mm, shallow depth of field, listeners' shoulders out of focus"
    "lighting": "overcast window light, same as the hearing"
    "mood": "a calm upright figure framed by visible floating dust, listeners' shoulders stiff and still"
    "style": "documentary photographic realism, dark-history, faceless"
    "text_in_image": {"present": false, "text": "", "font": "", "location": ""}
    "hard_fact_ids": []
    "people_group": ["company_owners_and_managers", "unions_and_labour_arbitration"]
    "year": "1949"

**Prompt antes:**

    The employer's advocate, a middle-aged Anglo-Australian man, heavy build, in a dark double-breasted suit. Standing at the head of the table, one palm open as he dismisses the dust clouds. Adult Anglo-Australian men of European descent with fair to sun-weathered skin and short hair. Adult Australian men of European descent with fair to tanned skin. The same 1949 arbitration room, tall window behind him, files stacked on the table. Overcast window light, same as the hearing. Medium shot, eye-level over the shoulders of seated listeners, 85mm, shallow depth of field, listeners' shoulders out of focus. A grainy 35mm documentary photograph taken in 1949, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.

**Prompt después:**

    The employer's advocate, a middle-aged Anglo-Australian man, heavy build, in a dark double-breasted suit. Standing at the head of the table, looking directly into the camera with a furrowed brow, one palm open as he dismisses the dust clouds. Adult Anglo-Australian men of European descent with fair to sun-weathered skin and short hair. Adult Australian men of European descent with fair to tanned skin. The same 1949 arbitration room, tall window behind him, files stacked on the table. Overcast window light, same as the hearing. Medium shot, eye-level over the shoulders of seated listeners, 85mm, shallow depth of field, listeners' shoulders out of focus. A grainy 35mm documentary photograph taken in 1949, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.

Hoja lado a lado (graded antes | después): `lab/hyperframes/f59/b2/hoja_b2.jpg`. Foto después: `lab/hyperframes/f59/b2/despues.png` / `lab/hyperframes/f59/b2/despues_graded.png`.

## B3 · Clip: `_clipfix_core` sobre ch01

- Pedido: «cámara quieta, solo sube el polvo, lento». voz_clip: «Un hombre joven posa para una foto con el pie envuelto en una venda blanca. Detrás, tierra roja y paredes»
- ok=**False** · 337.8 s de reloj · texto a Omar: «filtro: gemini_omni_flash: {"detail":[{"loc":["body","prompt"],"msg":"Unable to show the generated video. The output contains dangerous content that violates Google's Responsible AI practices. Try rephrasing the prompt. If you think this was an error, send feedback.","type":"content_policy_violation","url":"https://docs.fal.ai/errors#content_policy_violation","input":{"prompt":"Slow, somber documentary shot on grainy early-sixties 35mm film, muted colors, slight underexposure. Close on a man's bare foot wrapped in a frayed white bandage stained red, planted on red-ochre earth beside a worn black leath»
- Foto inicial intacta: md5 antes `5078cb32181b5e2ef86bba4e80aa9823` = después `5078cb32181b5e2ef86bba4e80aa9823` → True.
- Foto final (`foto_final_del_clip`, use_ultra=True): path `C:\CLAUDE_PROJECTS\automatization_videos\lab\hyperframes\f59\base\output\123bbb64-9fca-4395-8bf4-57d60e219ef1\assets\ch01_veo\ch01_img_01_final.png` · **SSIM inicial/final 0.516317** · motivo None · 48.7 s. Instrucción del edit: «Pull the camera slowly back and tilt it slightly up so the frame widens. The bandaged bare foot and the dusty black boot with its folded leather cuff and metal snap now sit smaller in the lower third, still sharp. Above them, more of the red-ochre earth stretches back toward the dull grey corrugated iron wall, which now fills the upper half of the frame with its vertical ridges more clearly defined. The bottom edge of the dark drill trouser leg appears above the boot. The man has eased his weight a little further onto the booted foot, so the bandaged foot rests more lightly, its toes barely pressing into the red dust. Keep the same white bandage with its rust-red stains and frayed edges, the same dust-covered toes, the same scattered red and grey grit on the ground, and the same hard cold midday light with short sharp shadows. Preserve the grainy, muted, slightly underexposed 1962 35mm documentary look, the 16:9 framing, and the absence of any text or signage.»
- Clip: antes 8.0 s (`lab/hyperframes/f59/b3/antes.mp4`) → después 8.0 s (`lab/hyperframes/f59/b3/despues.mp4`).
- Movimiento guardado en el guion vivo = en 03_visual: True.
- Backups: 03_visual.json.20261030_145245.bak.json, 123bbb64-9fca-4395-8bf4-57d60e219ef1.json.20261030_145245.bak.json, ch01_clip_01.mp4.20261030_145418.bak.mp4, ch03_img_08.png.20261030_145245.bak.png, ch03_img_08_graded.png.20261030_145245.bak.png.

**Movimiento antes (aprobado):**

    A slow, somber documentary shot on grainy 35mm film from the early sixties, muted colors and slight underexposure. The camera makes a very slow push-in, starting on a medium shot of the young miner against the corrugated iron wall and ending slightly closer, the white bandaged foot still sharp in the lower frame. First, fine red dust drifts low across the ochre earth, then his short shirt sleeves stir faintly in a light breeze as he breathes slowly. Hard, cold midday light under a pale washed-out sky keeps short sharp shadows steady in the dusty yard. He stays in place, posed stiffly with his weight off the bandaged foot, face and body steady.

**Movimiento que quedó guardado después** (si ok=False es el aprobado, intacto):

    A slow, somber documentary shot on grainy 35mm film from the early sixties, muted colors and slight underexposure. The camera makes a very slow push-in, starting on a medium shot of the young miner against the corrugated iron wall and ending slightly closer, the white bandaged foot still sharp in the lower frame. First, fine red dust drifts low across the ochre earth, then his short shirt sleeves stir faintly in a light breeze as he breathes slowly. Hard, cold midday light under a pale washed-out sky keeps short sharp shadows steady in the dusty yard. He stays in place, posed stiffly with his weight off the bandaged foot, face and body steady.

**Lo que devolvió Opus (salida cruda, por llamada):**

- `qa:fix_clip ch01` · 7.7 s:
    {"movimiento": "A slow, somber documentary shot on grainy 35mm film from the early sixties, muted colors and slight underexposure. The camera stays completely still, locked off on a medium shot of the young miner against the corrugated iron wall, the white bandaged foot sharp in the lower frame. Only fine red dust moves, rising slowly from the ochre earth in thin wisps and lifting gently upward through the frame. Hard, cold midday light under a pale washed-out sky keeps short sharp shadows steady in the dusty yard. He stays completely still, posed stiffly with his weight off the bandaged foot, his face, body and short shirt sleeves motionless."}

**Cadena de motores (`_generate_clip`, log por fila):**

- motor **None** · segundos None · None×None · US$ None · foto_final None · rechazos previos: ["gemini_omni_flash: {\"detail\":[{\"loc\":[\"body\",\"prompt\"],\"msg\":\"Unable to show the generated video. The output contains dangerous content that violates Google's Responsible AI practices. Try rephrasing the prompt. If you think this was an error, send feedback.\",\"type\":\"content_policy_violation\",\"url\":\"https://docs.fal.ai/errors#content_policy_violation\",\"input\":{\"prompt\":\"Slow, somber documentary shot on grainy early-sixties 35mm film, muted colors, slight underexposure. Close on a man's bare foot wrapped in a frayed white bandage stained red, planted on red-ochre earth beside a worn black leather trouser cuff wit", "kling_4: {\"detail\":[{\"loc\":[\"body\"],\"msg\":\"The content could not be processed because it contained material flagged by a content checker.\",\"type\":\"content_policy_violation\",\"url\":\"https://docs.fal.ai/errors#content_policy_violation\",\"input\":\"\",\"categories\":[\"model_moderated\"]}]}"]

  **Prompt que fue al motor:**

      (no quedó: _generate_clip solo guarda el prompt en el log cuando el motor acepta; lo que se ve del de Gemini está dentro del rechazo literal, cortado por fal)


**SSIM del clip que quedó en la copia (el viejo del 28-oct, intacto: md5 igual antes y después)** (`asset_manager._ssim`): primer cuadro vs foto inicial 0.751338 · último cuadro vs foto final 0.543362 · último cuadro vs foto inicial 0.661295.
Tiras de 5 cuadros: `lab/hyperframes/f59/b3/tira_antes.jpg` · `lab/hyperframes/f59/b3/tira_despues.jpg`.

## Gasto (cost_tracker, video `f59_parte_b`)

| servicio | descripción | US$ |
|---|---|---|
| fal.ai Seedream 5.0 Lite (t2i) | paquete_01_base_f59: A young adult Spanish migrant miner, olive skin, short dark ... | 0.035 |
| fal.ai Seedream 5.0 Lite (t2i) | paquete_02_base_f59: The bandaged foot of a young Spanish migrant miner resting o... | 0.035 |
| fal.ai Seedream 5.0 Lite (t2i) | paquete_03_base_f59: Vast abandoned blue-grey asbestos tailings dumps spilling do... | 0.035 |
| fal.ai Seedream 5.0 Lite (t2i) | ch03_img_08: The employer's advocate, a middle-aged Anglo-Australian man,... | 0.035 |
| Anthropic claude-opus-5-5 | qa:fix_foto ch03_img_08.png | 0.0106 |
| fal.ai Seedream 5.0 Lite (t2i) | ch03_img_08: The employer's advocate, a middle-aged Anglo-Australian man,... | 0.035 |
| Anthropic claude-opus-5-5 | qa:fix_clip ch01 | 0.01376 |
| Anthropic claude-opus-5-5 | ch01_img_01_final: instruccion | 0.03254 |
| fal.ai Seedream 5.0 Lite (edit) | ch01_img_01_final: Pull the camera slowly back and tilt it slightly up so the f... | 0.035 |
| Anthropic claude-opus-5-5 | ch01_clip_01: prompt gemini_omni_flash | 0.0553 |
| Anthropic claude-opus-5-5 | ch01_clip_01: prompt kling_4 | 0.06184 |

Por servicio: **fal.ai Seedream 5.0 Lite (t2i)** US$ 0.175 · **Anthropic claude-opus-5-5** US$ 0.17404 · **fal.ai Seedream 5.0 Lite (edit)** US$ 0.035

**Total US$ 0.384**.

## Archivos

- `lab/hyperframes/f59/parte_b.py`, `parte_b.json`, `parte_b.log`, `SALIDA_B.md` (van a git).
- `b1/` (bases y compuestas F59), `b2/` (28oct, antes, después, hoja_b2.jpg), `b3/` (antes.mp4, despues.mp4, foto final, tiras), `hoja_paquetes_f59.jpg`, `hoja_paquetes_f58_vs_f59.jpg`: imágenes y mp4, **no van a git**.
- La copia de lab `base/` quedó con la foto nueva de ch03_img_08 (B2), la foto final de ch01 y el clip viejo intacto (B3), con los backups en `assets/_qa_backups/` (ignorada por git).

## Lo que queda abierto (F59)

1. **B3 sin clip nuevo:** G y K rechazaron por la foto vieja del 28-oct de la copia (venda manchada de rojo), no por el movimiento editado. Para ver un clip rehecho de punta a punta hace falta una copia con fotos generadas desde su propio 03_visual (o correrlo en un guion fresco). Opus editó el movimiento como el handoff lo simulaba.
2. **Prompt del motor en el rechazo:** `_generate_clip` solo deja el prompt en el `log` cuando el motor acepta; en un rechazo queda lo que fal devuelve dentro del error (cortado). Si se quiere el prompt entero de G y K en el mensaje a Omar, es una línea en `_generate_clip` (producción, fuera de F59).
3. **SSIM del clip:** se midió sobre el clip que quedó (el viejo), primer cuadro vs inicial 0,751 y último vs final 0,543; no hay SSIM de un clip nuevo.
4. **Foto final de ch01 generada** (`ch01_img_01_final.png`, US$ 0,035 + Opus 0,033) queda en la copia y se reusaría en un segundo intento (`foto_final_del_clip` reusa si existe).
5. Las fotos de B1 cambian con la oración nueva más allá de la composición (Seedream sin semilla en `foto_paquete`: la 02 pasó de «rostro + pie» a «pie solo», la 03 perdió la cara de la derecha): la oración vieja pedía «face and torso large» y la nueva no; es lo que la decisión 08:22 buscaba (sin caras inventadas donde el casillero no tiene persona) y se ve en `hoja_paquetes_f58_vs_f59.jpg`.
6. Los abiertos 1–6 de la Etapa A siguen (foto inicial de un cap con clip no se rehace desde QA; xfail de `_f8_slots_scrub`; grade que falla hace fallar el fix; índices de F42 con nombres viejos; `dst.update(it)` copia el ancla de 03_visual al vivo).
7. Cuadros vacíos de la galería: arreglados en la Etapa A por la chascada del analista (filtro `_IMG_NAME_RE`); queda en producción, no probado sobre el servidor vivo en esta tanda.

## Veredicto de revisor-handoff — Etapa B (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

El pedido B3 no se cumplió en su resultado: no hay clip nuevo. Gemini y Kling rechazaron por contenido, y CC lo reporta honestamente con el camino de rechazo probado. B1 y B2 cumplen.

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | `_fix_core` y `_clipfix_core` directo, `QAState(tid, base_dir=BASE)`, dentro de `start_video('f59_parte_b')` | OK | `parte_b.py` l.136, 190, 219, 254, 286 (`end_video` en el `finally`, l.321). Los wrappers `llamar_mirando`, `foto_final_mirando` y `clip_mirando` (l.118-131, 266-282) anotan y delegan en `_llamar_casilleros`, `am.foto_final_del_clip` y `am._generate_clip` reales. |
| 2 | B1: casilleros de `metadata.json`, `sin_cartel=True`, `escala=False`, sin LLM | OK | l.151-156: `armar_item(..., False, lang, composicion=..., sin_cartel=True, ...)`. En `parte_b.log` no hay llamadas a LLM en B1. Hay 3 Seedream t2i de US$ 0,035 en `cost_tracker`. |
| 3 | B1: byte-identidad con F58 usando la oración vieja | OK | `parte_b.json`: `byte_identico_con_oracion_vieja` es True en los paquetes 1, 2 y 3. Esa comparación es solo del texto del prompt, no de la imagen. |
| 4 | B1: `hoja_paquetes_f59.jpg` al lado de la de F58 | OK | Existen `hoja_paquetes_f59.jpg` (82 KB) y `hoja_paquetes_f58_vs_f59.jpg` (158 KB). |
| 5 | B2: foto «antes» con el prompt de 03_visual y la misma semilla que `_fix_core` | OK | l.206-211: `am._seed_for_subject(TID, subject_ref)`, semilla 956889816. En el log aparece la misma semilla en las dos generaciones. |
| 6 | B2: casilleros y prompt antes/después, scrub pegado | OK | `parte_b.json`: cambió solo `action`, con «looking directly into the camera with a furrowed brow». `reason` dice «El filtro de producción no sacó nada». `_f8_slots_scrub` es null. `vivo_igual_a_03` es True. Los backups quedan en `_qa_backups`. |
| 7 | B2: hoja lado a lado | OK | `b2/hoja_b2.jpg` existe (55 KB), generada con `_hstack` de las dos fotos `_graded`. |
| 8 | B3: rechazos literales, motor, segundos | PARCIAL | Los rechazos literales de gemini_omni_flash y kling_4 están en `clip_log` y en el log. `segundos_total` es 337,8. El motor es `null` porque ningún motor entregó clip. El prompt que fue a Gemini sí está en el rechazo. |
| 9 | B3: SSIM inicial/final | PARCIAL | SSIM de la foto final: 0,516. Los SSIM del clip (0,751, 0,543 y 0,661) se midieron sobre el clip VIEJO, porque `despues.mp4` es una copia del viejo. CC lo declara (F59_REPORT l.177 y 210). |
| 10 | B3: mp4 y foto inicial intactos, movimiento aprobado sin tocar | OK | md5 de `antes.mp4` y `despues.mp4` idéntico (b557c1f2…). md5 de la foto inicial igual antes y después (5078cb32…). `movimiento_antes`, `movimiento_despues` y `movimiento_03_visual` son idénticos. |
| 11 | Gasto por servicio | OK | Suma de las 11 entradas = US$ 0,384, igual a `total_cost` 0,384032 en `data/cost_history.json` (última entrada, `video_id` `f59_parte_b`). Seedream t2i ×5 = 0,175, Seedream edit = 0,035, Opus ×5 = 0,174. |
| 12 | Hipótesis del hallazgo B3 | OK | Vivo ch01 `image_prompt`: «A close shot of a young Spanish miner's foot… soiled white bandage». 03_visual ch01: «A young adult Spanish migrant miner… Stands stiffly posing». `assets_manifest.json` l.30: `engine: veo`. El texto de que el prompt del motor «empieza Close on a man's bare foot…» coincide con el rechazo literal. Que fue la foto vieja y no el pedido es inferencia plausible, no probada: no se corrió el control con otra foto. |
| 13 | Imágenes y mp4 fuera de git | PARCIAL | No hay nada en staging (`git diff --cached` vacío). Pero `b1/`, `b2/`, `b3/`, las hojas y `parte_b.json` y `.log` figuran como `??` y no están ignorados (`git check-ignore` no devolvió nada). Quedan expuestos a un `git add -A`. |
| 14 | `F59_REPORT.md` con «lo que queda abierto» | OK | Sección l.206 y siguientes, con los puntos de B3 sin clip y de SSIM. |

Fuera de alcance: ninguno. Los archivos modificados son solo `diag_234_cap4.py` y `lab/hyperframes/f28/a/f28a.log`, anteriores a la tanda. No se tocó código de producción. Los archivos nuevos son `parte_b.py`, `parte_b.json`, `parte_b.log`, `SALIDA_B.md`, `F59_REPORT.md` y las carpetas de imágenes, todos dentro de `lab/hyperframes/f59/`.

Observaciones:
- Sin clip nuevo no se verificó la parte de B3 que pide el movimiento «después» entregado por el motor, el SSIM de un clip nuevo ni el motor ganador. El código G→K quedó probado solo hasta el rechazo.
- El pedido del analista fijaba ch01 tal cual y el desfase de la copia vino de la Etapa 0, así que el resultado no es falla de ejecución.
- No leí `F59_REPORT.md` entero. Verifiqué el resumen y las citas puntuales (l.12, 14, 16, 150, 177 y 206-210) contra `parte_b.json`.
- No miré las imágenes de `hoja_b2.jpg`, así que «el abogado mira a cámara con el ceño fruncido» no está verificado visualmente.

Riesgos que el contrato no cubre:
- La copia de lab quedó mutada por B2 (ítem de ch03 editado en `03_visual.json` y en el guion vivo) y por la foto final nueva de ch01 (`ch01_img_01_final.png`). Una Etapa C que parta de esa copia ya no arranca limpia.
- Si ch01 de un guion fresco también tuviera una foto que Gemini o Kling rechazan, el flujo termina en rechazo y no en clip.
- El riesgo de que el filtro de contenido bloquee un caso real queda sin medir: un solo caso, con foto vieja.

### Adenda de CC
- **Filas 8, 9 y observación 1:** es así: B3 llegó hasta el rechazo de los dos motores; no hay clip nuevo, motor ganador ni SSIM de un clip nuevo. Está en «lo que queda abierto» 1–3. No se re-corrió con otra foto porque el analista fijó ch01 y porque un segundo intento cuesta Opus ×2 + motor y repetiría el mismo camino con la misma foto.
- **Fila 12:** la causa (foto vieja, no el pedido) es inferencia: el prompt del motor que fue rechazado describe la venda manchada de rojo que está en la foto del 28-oct y no en el movimiento editado por Opus (que no la nombra). El control con otra foto queda para la tanda que lo pida.
- **Fila 13:** las imágenes y mp4 no están en `.gitignore` (como las de F58: `hoja_paquetes.jpg` y `thumb_candidates/`); se dejan fuera del commit por paths explícitos, como en todas las tandas. Si prefieren una regla en `.gitignore` para `lab/hyperframes/*/b[0-9]/` y `*.jpg`, es una línea; no se agregó para no tocar reglas sin pedido.
- **Observación 4:** CC sí miró `hoja_b2.jpg`: en la foto nueva el abogado mira a cámara con el ceño fruncido (en la de antes mira a los sindicalistas, de perfil, como decía `gaze_interaction`).
- **Riesgo 1:** cierto; los backups de `_qa_backups/` (03_visual, guion vivo, PNG crudo y graded de ch03_img_08, mp4 de ch01) permiten volver la copia al estado de la Etapa 0 copiándolos encima, o se vuelve a correr `copia_lab.py`.
