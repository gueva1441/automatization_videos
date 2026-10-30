# F59 — Salida B (prueba real en Wittenoom, copia de lab)

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