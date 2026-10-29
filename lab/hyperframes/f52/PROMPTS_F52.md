# PROMPTS_F52 — los 8 prompts de video en texto (F52 etapa 2)

Salida de `python lab/hyperframes/f52/prompts_video.py`: 8 llamadas a `claude-opus-5-5` (effort `high`) en paralelo, una por modelo y clip, con el pedido del handoff tal cual. Entrada: el `03_visual.json` de F51f (md5 `0d57b6ba…`). Costo total: **US$ 0.1206**. Palabras = `len(prompt.split())`.

| clip | modelo | palabras | caracteres | US$ | stop_reason |
|---|---|---|---|---|---|
| cap 1 | F FLUX 3 Max | 110 | 684 | 0.01047 | end_turn |
| cap 1 | G Gemini Omni Flash 1.1 | 156 | 914 | 0.01302 | end_turn |
| cap 1 | K Kling 4.0 | 309 | 1707 | 0.02212 | end_turn |
| cap 1 | S Seedance 2.5 | 139 | 815 | 0.01322 | end_turn |
| cap 7 | F FLUX 3 Max | 111 | 669 | 0.01139 | end_turn |
| cap 7 | G Gemini Omni Flash 1.1 | 171 | 1022 | 0.01422 | end_turn |
| cap 7 | K Kling 4.0 | 275 | 1613 | 0.0236 | end_turn |
| cap 7 | S Seedance 2.5 | 136 | 813 | 0.01256 | end_turn |

## Cap 1 (`veo_position` start)

- Foto: `lab/hyperframes/f52/fotos/cap01.png`
- Ancla: «Un hombre joven posa para una foto con el pie envuelto en una venda blanca.»

**`video_prompt` vivo (referencia):**

```
A slow, somber documentary shot on grainy 35mm film from the early sixties, muted colors and slight underexposure. The camera makes a very slow push-in, starting on a medium shot of the young miner against the corrugated iron wall and ending slightly closer, the white bandaged foot still sharp in the lower frame. First, fine red dust drifts low across the ochre earth, then his short shirt sleeves stir faintly in a light breeze as he breathes slowly. Hard, cold midday light under a pale washed-out sky keeps short sharp shadows steady in the dusty yard. He stays in place, posed stiffly with his weight off the bandaged foot, face and body steady.
```

### cap 1 · K — Kling 4.0

309 palabras · 1707 caracteres

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

139 palabras · 815 caracteres

```
One single continuous shot. The camera makes a very slow, steady push-in from the opening medium framing, ending slightly closer, with the bandaged foot staying sharp in the lower frame.

0–3 s: Fine red dust drifts low across the ground, lifting in thin wisps and settling again.

3–6 s: A light breeze makes his short shirt sleeves stir faintly. His chest rises and falls with slow, shallow breaths.

6–8 s: The dust thins out and the push-in eases to a gentle stop. He holds his stiff pose with his weight kept off the bandaged foot. His face and body stay still apart from his breathing.

Light and shadows remain constant throughout. The grain, muted colors and underexposure of the photograph stay unchanged.

8 seconds, one continuous shot, no cuts, no scene change, no dialogue, no music, no on-screen text.
```

### cap 1 · F — FLUX 3 Max

110 palabras · 684 caracteres

```
A very slow push-in from the original eye-level medium shot, framing and hard cold midday light unchanged, holds on the young Spanish miner standing stiffly posed against the grey corrugated iron wall with his weight off his white-bandaged foot, breathing slowly while his face and body stay still, as fine red dust drifts low across the ochre earth of the Wittenoom yard and his short shirt sleeves stir faintly in a light breeze, short sharp shadows steady under the pale washed-out sky, the bandage staying sharp in the lower frame, in grainy, slightly underexposed early-1960s 35mm documentary film with muted colors, one continuous 8-second shot, no on-screen text, no subtitles.
```

### cap 1 · G — Gemini Omni Flash 1.1

156 palabras · 914 caracteres

```
Slow push-in on a young Spanish miner posing stiffly for a family snapshot in the red-ochre yard of a Wittenoom company house, 1962. Start on the medium eye-level framing against the grey corrugated iron wall and end slightly closer, with the white bandaged foot still sharp in the lower frame. Fine red dust drifts low across the earth, then his short shirt sleeves stir faintly in a light breeze as he breathes slowly. He holds the pose, weight off the bandaged foot, face and body steady. Keep his olive skin, short dark hair, lean build, dust-coated shirt and drill trousers, the white bandage, the corrugated wall and the hard cold midday light with short sharp shadows. The look is a grainy 35mm documentary film: muted colors, slight underexposure, somber realism. For sound, use only a faint dry wind and dust settling, with no music and no dialogue. One continuous 8-second shot with no cuts, no captions.
```

## Cap 7 (`veo_position` end)

- Foto: `lab/hyperframes/f52/fotos/cap07.png`
- Ancla: «No se ha retirado una sola palada de asbesto. ¿Quién va a sacar la primera palada de esa tierra?»

**`video_prompt` vivo (referencia):**

```
A slow, somber documentary shot on grainy 35mm film, muted colors and slight underexposure, in a quiet dark-history realist style. Low at creek-bed level, the camera makes a very slow push-in, starting on the wide view of the upright shovel in the blue-grey tailings and ending on a closer framing of the shovel and its sunken blade against the red-ochre bank. First the thin stream slides steadily past the shovel toward the floodplain, rippling softly over the shallow pools, then a faint breeze stirs the spinifex clumps and lifts a few wisps of pale dust from the tailings. Pale cold dawn light and long soft shadows hold steady over the dry Pilbara gorge throughout.
```

### cap 7 · K — Kling 4.0

275 palabras · 1613 caracteres

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

136 palabras · 813 caracteres

```
One single continuous shot, no cuts. Very slow push-in at creek-bed level, from the wide view toward a closer framing of the upright shovel and its sunken blade against the red-ochre bank. The shovel stays completely still and untouched.

0–3 s: The thin stream slides steadily past the shovel toward the floodplain, rippling softly over the shallow pools.

3–6 s: A faint breeze stirs the spinifex clumps, and a few wisps of pale dust lift from the blue-grey tailings and drift away.

6–8 s: The push-in eases to a gentle stop on the closer framing while the water keeps flowing and the dust settles.

The pale cold dawn light and long soft shadows hold steady throughout. Grainy 35mm film texture, muted colors, slight underexposure, somber documentary feel. 8 seconds, no dialogue, no music, no on-screen text.
```

### cap 7 · F — FLUX 3 Max

111 palabras · 669 caracteres

```
Low at creek-bed level, the camera pushes in very slowly from the wide view toward the upright long-handled shovel, its blade sunk in the untouched blue-grey tailings, standing still as a thin stream slides steadily past it toward the floodplain and ripples over the shallow pools of the dry Pilbara creek bed below the red-ochre gorge banks, while a faint breeze stirs the spinifex clumps and lifts a few wisps of pale dust from the tailings, keeping the original low angle, deep focus, pale cold dawn light, long soft shadows and grainy, muted, slightly underexposed 35mm documentary look of the photo in one continuous 8-second shot. No on-screen text, no subtitles.
```

### cap 7 · G — Gemini Omni Flash 1.1

171 palabras · 1022 caracteres

```
Slow push-in at creek-bed level over 8 seconds, one continuous shot. Start on the wide view of the old long-handled shovel standing upright and unused, its blade sunk in the bank of blue-grey tailings. End on a closer framing of the shovel and its buried blade against the red-ochre bank. The thin stream slides steadily past the shovel toward the floodplain, rippling softly over the shallow pools. Midway, a faint breeze stirs the spinifex clumps and lifts a few wisps of pale dust from the tailings. Nobody enters the frame.

Keep from the photo: the upright shovel and its sunken blade, the blue-grey tailings against the red-ochre banks, the dry Pilbara gorge, the pale cold dawn light and long soft shadows, the low angle, and the deep focus.

Look: grainy 35mm documentary film with muted colors, slight underexposure, and a somber dark-history realism.

Sound: a quiet trickle of water, a low breeze through dry grass, and a distant empty stillness. No music, no dialogue, no cuts, no on-screen text.

No captions.
```

## Fichas usadas (`lab/hyperframes/f52/guias/`)

- **K — Kling 4.0** (guía oficial de Kling, 2026-10-26): lenguaje descriptivo y concreto; pocas palabras abstractas y pocas negaciones (aumentan errores); las únicas negaciones necesarias: sin subtítulos y sin música de fondo. Estructura: [Ajustes generales] escena y textura, estilo visual, tono de cámara · [Secuencia] 0–X s / X–Y s / Y s–final con acción y movimiento de cámara · [Audio]. En imagen a video: sujeto + movimiento, fondo + movimiento.
- **S — Seedance 2.5** (guía de BytePlus vía resúmenes): en imagen a video escribir solo lo que se mueve, construir sobre la foto sin re-describirla; claridad y cero contradicciones valen más que encabezados; rangos de tiempo contiguos (0–3 s, 3–6 s…) guían el orden; si el prompt describe otra escena, el modelo puede cortar: decir que es una sola toma continua.
- **F — FLUX 3 Max** (Black Forest Labs / fal): dirigir la escena, no inventariar objetos; sustantivos y verbos concretos; sobrecargar el prompt vuelve el movimiento menos coherente; una oración en orden cámara → sujeto → acción → entorno → movimiento secundario y look; en imagen a video decir qué se queda igual de la foto (encuadre, luz); cerrar con «no on-screen text, no subtitles».
- **G — Gemini Omni Flash 1.1** (Google vía fal): sujeto, acción, movimiento de cámara, look y sonido, escritos como indicaciones a un equipo de rodaje; movimientos de cámara con su nombre de cine; es menos prescriptivo que Veo: prompts cortos y enfocados rinden más que largos; en imagen a video nombrar lo que de la foto tiene que sobrevivir; cerrar con «no captions».

## El pedido a Opus (plantilla)

```
You write the motion prompt for an image-to-video model. The still image is the first frame. Follow the model guide below exactly; it decides structure, length and closing lines.
MODEL GUIDE:
{ficha}
STILL IMAGE PROMPT (what the first frame shows):
{prompt_foto}
NARRATION AT THIS MOMENT:
{ancla}
APPROVED MOTION (keep its intent, rewrite it for this model):
{video_prompt_vivo}
Clip length: 8 seconds, one continuous shot, no cuts, no dialogue, no music, no on-screen text.
Return only the prompt text.
```

