# PROMPTS_F52 — los 8 prompts de video en texto (F52b: fichas en inglés + Opus mira la foto)

Salida de `python lab/hyperframes/f52/prompts_video.py`: 8 llamadas a `claude-opus-5-5` (effort `high`) en paralelo, una por modelo y clip. Cada una lleva primero la foto real del cap (`fotos/capNN.png`, bloque `image`) y después el pedido del handoff F52b tal cual. Entrada: el `03_visual.json` de F51f (md5 `0d57b6ba…`). Costo de las 8: **US$ 0.2861**. Al lado de cada prompt nuevo va el de F52 etapa 2 (v1, `prompts_f52_v1.json`: fichas en castellano, sin la foto). Palabras = `len(prompt.split())`.

| clip | modelo | palabras v1 | palabras F52b | US$ F52b |
|---|---|---|---|---|
| cap 1 | K Kling 4.0 | 309 | 320 | 0.04103 |
| cap 1 | S Seedance 2.5 | 139 | 152 | 0.03398 |
| cap 1 | F FLUX 3 Max | 110 | 122 | 0.03668 |
| cap 1 | G Gemini Omni Flash 1.1 | 156 | 167 | 0.03226 |
| cap 7 | K Kling 4.0 | 275 | 302 | 0.04291 |
| cap 7 | S Seedance 2.5 | 136 | 161 | 0.03522 |
| cap 7 | F FLUX 3 Max | 111 | 115 | 0.03304 |
| cap 7 | G Gemini Omni Flash 1.1 | 171 | 165 | 0.03104 |

## Cap 1 (`veo_position` start)

- Foto (la que ve Opus): `lab/hyperframes/f52/fotos/cap01.png`
- Ancla: «Un hombre joven posa para una foto con el pie envuelto en una venda blanca.»

**`video_prompt` vivo (referencia):**

```
A slow, somber documentary shot on grainy 35mm film from the early sixties, muted colors and slight underexposure. The camera makes a very slow push-in, starting on a medium shot of the young miner against the corrugated iron wall and ending slightly closer, the white bandaged foot still sharp in the lower frame. First, fine red dust drifts low across the ochre earth, then his short shirt sleeves stir faintly in a light breeze as he breathes slowly. Hard, cold midday light under a pale washed-out sky keeps short sharp shadows steady in the dusty yard. He stays in place, posed stiffly with his weight off the bandaged foot, face and body steady.
```

### cap 1 · K — Kling 4.0

**Lectura de CC:** En inglés: sí. Encuadre real: sí, «stands in full figure», «the camera holds the full-figure framing»; pie vendado «lifted slightly forward, with its tip barely touching the red earth». Ojo: dice «His left foot»; en la foto el vendado es el que queda a la izquierda del cuadro, o sea su pie derecho.

**F52b** (320 palabras · 1863 caracteres)

```
[General settings]
A dusty yard of a 1960s mining-town company house: red-ochre earth in the foreground, a long dull grey corrugated iron wall across the middle, and a pale washed-out sky above. Grainy 35mm documentary film look from the early sixties, with muted colors, slight underexposure, a somber realist tone, and one continuous shot. A young miner with olive skin and short dark hair stands in full figure at the center. He wears a dust-stained tan work shirt with sleeves rolled to the elbows, dark dusty trousers, and one worn leather boot. His left foot is wrapped in a white bandage and lifted slightly forward, with its tip barely touching the red earth and his weight resting on the booted foot. Hard sunlight casts a sharp shadow from his legs across the ground. He looks straight into the lens with a stiff, serious expression.

[Sequence]
0–3 s: The camera holds the full-figure framing and begins a very slow push-in. Fine red dust drifts low across the ochre earth around his feet. He stands still in his stiff pose and breathes slowly, his chest rising and falling under the open collar.

3–6 s: The slow push-in continues. A light breeze makes the loose shirt fabric and rolled sleeves stir faintly. The bandaged foot stays lifted and steady, its white wrapping sharp against the red ground. His gaze stays fixed on the camera, and his hands hang loosely at his sides.

6 s–end: The camera settles slightly closer, with the bandaged foot still sharp in the lower frame and the corrugated wall flat and still behind him. Dust settles back onto the earth, and the sharp shadows hold steady in the hard light. He remains posed, quiet and unmoving, as if waiting for the shutter.

[Audio]
Soft dry wind across open ground, a faint hiss of drifting dust, and an occasional low tick of sun-heated corrugated iron. No subtitles, no background music.
```

**v1, F52** (309 palabras)

```
[Ajustes generales]
Patio de tierra rojo ocre frente a una casa de empresa en Wittenoom, 1962, con una pared de chapa ondulada gris mate al fondo. Un joven minero español de piel oliva, pelo oscuro corto y complexión delgada y fibrosa lleva una camisa de trabajo de manga corta cubierta de polvo y pantalones de dril. Tiene un pie envuelto en una venda blanca y posa rígido para una foto familiar, con el peso apoyado en el pie sano. Película documental de 35 mm con grano marcado, colores apagados y ligera subexposición, en estilo realista sombrío. La luz es dura y fría de mediodía bajo un cielo pálido y desvaído, con sombras cortas y nítidas. La cámara avanza a la altura de los ojos con un acercamiento muy lento y suave. Es un único plano continuo de 8 segundos.

[Secuencia]
0–3 s: Plano medio del minero ante la pared de chapa, con la venda blanca nítida en la parte inferior del encuadre. Un polvo rojo fino flota a ras del suelo sobre la tierra ocre. La cámara inicia un acercamiento muy lento.
3–6 s: Las mangas cortas de su camisa se agitan levemente con una brisa ligera mientras él respira despacio, con el pecho subiendo y bajando suavemente. El polvo sigue derivando bajo y las sombras cortas permanecen firmes sobre el patio.
6 s–final: La cámara termina un poco más cerca, con la venda blanca todavía nítida abajo en el encuadre. Él sigue quieto en su pose rígida, con el rostro y el cuerpo firmes y el peso fuera del pie vendado. La pared gris permanece inmóvil al fondo bajo la luz fría.

[Audio]
Ambiente seco y tranquilo de un patio minero: el leve soplo del viento, un roce suave de polvo sobre la tierra y un crujido metálico lejano de la chapa. Sin subtítulos. Sin música de fondo.
```

### cap 1 · S — Seedance 2.5

**Lectura de CC:** En inglés: sí. Encuadre real: sí, «from the full-length framing»; el pie, «the bandaged foot resting on its tip» (apoyado en la punta, no «levantado»).

**F52b** (152 palabras · 903 caracteres)

```
One single continuous shot, no cuts. The camera makes a very slow, steady push-in from the full-length framing toward a slightly closer shot, keeping the white bandaged foot sharp and inside the lower frame throughout.

0–3 s: Fine red dust drifts low across the ochre earth, lifting and settling around his boot and the bandaged foot resting on its tip. He holds his stiff pose, weight on the booted leg, eyes fixed on the camera.

3–6 s: A light breeze faintly stirs the loose dusty shirt and its rolled sleeves. His chest rises and falls with slow, shallow breaths, and his face stays still and unsmiling.

6–8 s: The push-in eases to a stop. He remains in place, the bandaged foot motionless, while short sharp shadows stay steady under the hard, cold midday light.

Grainy early-1960s 35mm documentary look, muted colors, slight underexposure, somber pace. No dialogue, no music, no on-screen text.
```

**v1, F52** (139 palabras)

```
One single continuous shot. The camera makes a very slow, steady push-in from the opening medium framing, ending slightly closer, with the bandaged foot staying sharp in the lower frame.

0–3 s: Fine red dust drifts low across the ground, lifting in thin wisps and settling again.

3–6 s: A light breeze makes his short shirt sleeves stir faintly. His chest rises and falls with slow, shallow breaths.

6–8 s: The dust thins out and the push-in eases to a gentle stop. He holds his stiff pose with his weight kept off the bandaged foot. His face and body stay still apart from his breathing.

Light and shadows remain constant throughout. The grain, muted colors and underexposure of the photograph stay unchanged.

8 seconds, one continuous shot, no cuts, no scene change, no dialogue, no music, no on-screen text.
```

### cap 1 · F — FLUX 3 Max

**Lectura de CC:** En inglés: sí. Encuadre real: sí, «from the full-length eye-level framing»; pie «lifted just off the ground».

**F52b** (122 palabras · 745 caracteres)

```
A very slow push-in from the full-length eye-level framing to a slightly closer shot, keeping the same hard midday light, pale washed-out sky and sharp white bandage in the lower frame, on a young dark-haired miner in a dust-stained rolled-sleeve work shirt and dark trousers who holds his stiff pose with the bandaged foot lifted just off the ground, breathing slowly and staring steadily into the lens, in a red-ochre yard before a dull grey corrugated iron wall, as fine red dust drifts low across the earth and his shirt stirs faintly in a light breeze, short sharp shadows unchanged, grainy early-1960s 35mm documentary look with muted colors and slight underexposure, one continuous 8-second shot, no cuts, no on-screen text, no subtitles.
```

**v1, F52** (110 palabras)

```
A very slow push-in from the original eye-level medium shot, framing and hard cold midday light unchanged, holds on the young Spanish miner standing stiffly posed against the grey corrugated iron wall with his weight off his white-bandaged foot, breathing slowly while his face and body stay still, as fine red dust drifts low across the ochre earth of the Wittenoom yard and his short shirt sleeves stir faintly in a light breeze, short sharp shadows steady under the pale washed-out sky, the bandage staying sharp in the lower frame, in grainy, slightly underexposed early-1960s 35mm documentary film with muted colors, one continuous 8-second shot, no on-screen text, no subtitles.
```

### cap 1 · G — Gemini Omni Flash 1.1

**Lectura de CC:** En inglés: sí. Encuadre real: sí, «this full-length shot»; el pie, «resting lightly on its toes» (apoyado en la punta, no «levantado»).

**F52b** (167 palabras · 990 caracteres)

```
Grainy early-1960s 35mm documentary look, muted colors, slight underexposure. Very slow push-in from this full-length shot of the young miner standing in the red-ochre yard in front of the grey corrugated iron wall. End slightly closer, with the white bandaged foot still sharp in the lower frame. He holds his stiff pose, weight on his booted foot, the bandaged foot resting lightly on its toes. His face stays steady and serious, eyes on the lens, and he breathes slowly. Fine red dust drifts low across the earth. The rolled sleeves of his dust-stained shirt stir faintly in a light breeze. Hard, cold midday light under a pale washed-out sky keeps the short sharp shadows steady. Keep his face, the dusty tan shirt, the dark dirt-streaked trousers, the white bandage, the corrugated wall and the red ground exactly as in the image. Sound: faint dry wind and a soft hiss of dust, distant quiet outback stillness. One continuous 8-second shot, no cuts, no dialogue, no music, no captions.
```

**v1, F52** (156 palabras)

```
Slow push-in on a young Spanish miner posing stiffly for a family snapshot in the red-ochre yard of a Wittenoom company house, 1962. Start on the medium eye-level framing against the grey corrugated iron wall and end slightly closer, with the white bandaged foot still sharp in the lower frame. Fine red dust drifts low across the earth, then his short shirt sleeves stir faintly in a light breeze as he breathes slowly. He holds the pose, weight off the bandaged foot, face and body steady. Keep his olive skin, short dark hair, lean build, dust-coated shirt and drill trousers, the white bandage, the corrugated wall and the hard cold midday light with short sharp shadows. The look is a grainy 35mm documentary film: muted colors, slight underexposure, somber realism. For sound, use only a faint dry wind and dust settling, with no music and no dialogue. One continuous 8-second shot with no cuts, no captions.
```

## Cap 7 (`veo_position` end)

- Foto (la que ve Opus): `lab/hyperframes/f52/fotos/cap07.png`
- Ancla: «No se ha retirado una sola palada de asbesto. ¿Quién va a sacar la primera palada de esa tierra?»

**`video_prompt` vivo (referencia):**

```
A slow, somber documentary shot on grainy 35mm film, muted colors and slight underexposure, in a quiet dark-history realist style. Low at creek-bed level, the camera makes a very slow push-in, starting on the wide view of the upright shovel in the blue-grey tailings and ending on a closer framing of the shovel and its sunken blade against the red-ochre bank. First the thin stream slides steadily past the shovel toward the floodplain, rippling softly over the shallow pools, then a faint breeze stirs the spinifex clumps and lifts a few wisps of pale dust from the tailings. Pale cold dawn light and long soft shadows hold steady over the dry Pilbara gorge throughout.
```

### cap 7 · K — Kling 4.0

**Lectura de CC:** En inglés: sí. Encuadre real: sí, la pala en el montículo «on the left of the frame» y el arroyo hacia «the lower right», y los acantilados oscuros a los dos lados.

**F52b** (302 palabras · 1749 caracteres)

```
[General settings]
Early-morning creek bed in a red Pilbara gorge, filmed as a slow, somber documentary on grainy 35mm film with muted colors, slight underexposure, and a quiet dark-history realist tone. An old long-handled shovel with a rusted blade stands upright, its blade sunk in a mound of blue-grey crocidolite tailings on the left of the frame. A thin, clear stream winds out of the distance and flows past the mound toward the lower right, over flat red-ochre stones. Behind the mound lies a still shallow pool. Spinifex clumps line the red-ochre bank on the right. Dark red cliffs rise on both sides under a pale, cold dawn sky. Long soft shadows lie across the ground. The camera is low at creek-bed level and moves very slowly in one continuous shot.

[Sequence]
0–3 s: Wide view of the upright shovel in the blue-grey tailings. The camera begins a very slow push-in toward the shovel. The stream slides steadily past the base of the mound, rippling softly over the flat stones and catching glints of pale light.

3–6 s: The slow push-in continues. A faint breeze stirs the spinifex clumps on the right bank, and their thin blades sway gently. A few wisps of pale dust lift from the surface of the tailings and drift low across the mound. The water keeps flowing past the mound toward the lower right.

6 s–end: The camera settles on a closer framing of the shovel's handle and sunken rusted blade, with the red-ochre bank and the moving stream behind it. The shovel stays perfectly still. Pale cold dawn light and long soft shadows hold steady over the gorge.

[Audio]
Soft, steady trickle of shallow water over stones, a faint dry wind, and a light rustle of spinifex. Quiet ambient gorge atmosphere. No background music. No subtitles.
```

**v1, F52** (275 palabras)

```
[Ajustes generales]
Lecho seco de un arroyo de Pilbara bajo un desfiladero de Wittenoom, al amanecer. Una vieja pala de mango largo se alza vertical, con la hoja hundida en un banco intacto de relaves de crocidolita gris azulado, junto a orillas rojo ocre, pozas poco profundas y matas de spinifex. Fotografía documental en película de 35 mm, con grano visible, colores apagados y ligera subexposición, en un estilo realista sobrio de historia oscura. Luz pálida y fría del amanecer, con sombras largas y suaves que permanecen estables. Cámara baja a ras del lecho, objetivo de 24 mm, gran profundidad de campo y tono contemplativo. Una sola toma continua de 8 segundos.

[Secuencia]
0–3 s: Plano general de la pala erguida en los relaves gris azulado. Un hilo de agua se desliza constante junto a la pala hacia la llanura de inundación y ondula suavemente sobre las pozas. La cámara inicia un acercamiento muy lento a ras del suelo.
3–6 s: Una brisa tenue mece las matas de spinifex y levanta unas finas volutas de polvo pálido de la superficie de los relaves. El agua sigue fluyendo junto a la pala. La cámara continúa avanzando con suavidad.
6 s–final: El acercamiento termina en un encuadre más cercano de la pala y su hoja hundida, recortadas contra la orilla rojo ocre. El polvo se asienta despacio mientras la luz fría del amanecer y las sombras largas se mantienen quietas sobre el desfiladero.

[Audio]
Sonido ambiente natural y tenue: el murmullo suave del agua sobre las piedras, una brisa ligera entre el spinifex y el silencio abierto del desfiladero al amanecer. Sin subtítulos. Sin música de fondo.
```

### cap 7 · S — Seedance 2.5

**Lectura de CC:** En inglés: sí. Encuadre real: sí, la pala en los relaves y «the stream on the right»; describe solo lo que se mueve.

**F52b** (161 palabras · 956 caracteres)

```
One single continuous shot, no cuts. Grainy 35mm documentary look, muted colors and slight underexposure, quiet and somber.

0–3 s: From low at creek-bed level, the camera begins a very slow, steady push-in toward the upright shovel in the blue-grey tailings. The stream on the right slides steadily past the mound, its surface rippling softly and glinting in the pale light.

3–6 s: The push-in continues smoothly. The water keeps flowing past the edge of the tailings and over the shallow pools. A faint breeze stirs the spinifex clumps on the right bank and in the background.

6–8 s: The camera settles on a closer framing of the shovel and its sunken blade against the red-ochre bank. A few thin wisps of pale dust lift gently from the tailings and drift away. The shovel stays completely still and untouched. Light and shadows stay unchanged throughout.

Clip length: 8 seconds, one continuous shot, no cuts, no dialogue, no music, no on-screen text.
```

**v1, F52** (136 palabras)

```
One single continuous shot, no cuts. Very slow push-in at creek-bed level, from the wide view toward a closer framing of the upright shovel and its sunken blade against the red-ochre bank. The shovel stays completely still and untouched.

0–3 s: The thin stream slides steadily past the shovel toward the floodplain, rippling softly over the shallow pools.

3–6 s: A faint breeze stirs the spinifex clumps, and a few wisps of pale dust lift from the blue-grey tailings and drift away.

6–8 s: The push-in eases to a gentle stop on the closer framing while the water keeps flowing and the dust settles.

The pale cold dawn light and long soft shadows hold steady throughout. Grainy 35mm film texture, muted colors, slight underexposure, somber documentary feel. 8 seconds, no dialogue, no music, no on-screen text.
```

### cap 7 · F — FLUX 3 Max

**Lectura de CC:** En inglés: sí. Encuadre real: en parte: no dice dónde está la pala en el cuadro, pero pide «the same framing … as the first frame» y nombra el montículo, el arroyo y los acantilados oscuros.

**F52b** (115 palabras · 680 caracteres)

```
Low at creek-bed level, the camera pushes in very slowly from the wide view toward the upright rusted shovel whose blade stays sunk in the blue-grey tailings, while the thin stream slides steadily past it over the stones and ripples through the shallow pools toward the floodplain, the red-ochre banks and dark gorge walls holding their place as a faint breeze stirs the spinifex clumps and lifts a few wisps of pale dust from the tailings, the same framing, pale cold dawn light and long soft shadows as the first frame kept throughout one continuous 8-second shot on grainy 35mm film with muted colors and slight underexposure, somber and still, no on-screen text, no subtitles.
```

**v1, F52** (111 palabras)

```
Low at creek-bed level, the camera pushes in very slowly from the wide view toward the upright long-handled shovel, its blade sunk in the untouched blue-grey tailings, standing still as a thin stream slides steadily past it toward the floodplain and ripples over the shallow pools of the dry Pilbara creek bed below the red-ochre gorge banks, while a faint breeze stirs the spinifex clumps and lifts a few wisps of pale dust from the tailings, keeping the original low angle, deep focus, pale cold dawn light, long soft shadows and grainy, muted, slightly underexposed 35mm documentary look of the photo in one continuous 8-second shot. No on-screen text, no subtitles.
```

### cap 7 · G — Gemini Omni Flash 1.1

**Lectura de CC:** En inglés: sí. Encuadre real: sí, «the shovel left of center in the tailings, the winding stream … the dark gorge walls» en la lista de lo que tiene que quedar.

**F52b** (165 palabras · 947 caracteres)

```
Slow push-in at creek-bed level on an old rusted shovel standing upright in a mound of blue-grey asbestos tailings, a thin creek flowing past on the right toward the floodplain. The shot starts wide and ends on a closer framing of the shovel and its sunken blade. The stream slides steadily over the stones and ripples into the shallow pools. Midway, a faint breeze stirs the spinifex clumps and lifts a few wisps of pale dust from the tailings. The shovel stays untouched and does not move. Keep the composition from the image: the shovel left of center in the tailings, the winding stream, the red-ochre banks and pools, the dark gorge walls under a pale sky. Pale cold dawn light and long soft shadows hold steady. The look is grainy 35mm documentary, muted colors, slight underexposure, somber and realist. Sound: only the soft trickle of water and a low breeze, with no music and no voices. One continuous 8-second shot, no cuts, no captions.
```

**v1, F52** (171 palabras)

```
Slow push-in at creek-bed level over 8 seconds, one continuous shot. Start on the wide view of the old long-handled shovel standing upright and unused, its blade sunk in the bank of blue-grey tailings. End on a closer framing of the shovel and its buried blade against the red-ochre bank. The thin stream slides steadily past the shovel toward the floodplain, rippling softly over the shallow pools. Midway, a faint breeze stirs the spinifex clumps and lifts a few wisps of pale dust from the tailings. Nobody enters the frame.

Keep from the photo: the upright shovel and its sunken blade, the blue-grey tailings against the red-ochre banks, the dry Pilbara gorge, the pale cold dawn light and long soft shadows, the low angle, and the deep focus.

Look: grainy 35mm documentary film with muted colors, slight underexposure, and a somber dark-history realism.

Sound: a quiet trickle of water, a low breeze through dry grass, and a distant empty stillness. No music, no dialogue, no cuts, no on-screen text.

No captions.
```

## Fichas usadas (`lab/hyperframes/f52/guias/`, en inglés)

- **K — Kling 4.0** (official Kling guide, 2026-10-26): descriptive, concrete language; few abstract words and few negations (they increase errors); the only negations needed: no subtitles and no background music. Structure: [General settings] scene and texture, visual style, camera tone · [Sequence] 0–X s / X–Y s / Y s–end with action and camera movement · [Audio]. In image-to-video: subject + motion, background + motion.
- **S — Seedance 2.5** (BytePlus guide via summaries): in image-to-video write only what moves, build on the image without re-describing it; clarity and zero contradictions matter more than headers; contiguous time ranges (0–3 s, 3–6 s…) guide the order; if the prompt describes a different scene the model may cut: say it is one single continuous shot.
- **F — FLUX 3 Max** (Black Forest Labs / fal): direct the scene, don't inventory objects; concrete nouns and verbs; overloading the prompt makes motion less coherent; one sentence in the order camera → subject → action → setting → secondary motion and look; in image-to-video say what stays the same from the image (framing, light); close with "no on-screen text, no subtitles".
- **G — Gemini Omni Flash 1.1** (Google via fal): subject, action, camera movement, look and sound, written as directions to a film crew; camera moves by their film name; less prescriptive than Veo: short focused prompts work better than long ones; in image-to-video name what from the image must survive; close with "no captions".

## El pedido a Opus (plantilla F52b; la foto va antes, como bloque `image`)

```
You write the motion prompt for an image-to-video model. The still image is the first frame. Follow the model guide below exactly; it decides structure, length and closing lines.
MODEL GUIDE:
{ficha}
FIRST FRAME: the attached image. Where it differs from the still image prompt (framing, pose, what is visible), describe the motion from the image as it is.
STILL IMAGE PROMPT (what the first frame was asked to show):
{prompt_foto}
NARRATION AT THIS MOMENT:
{ancla}
APPROVED MOTION (keep its intent, rewrite it for this model):
{video_prompt_vivo}
Clip length: 8 seconds, one continuous shot, no cuts, no dialogue, no music, no on-screen text.
Return only the prompt text.
```

