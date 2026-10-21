# F5b S6 — Prompts de imagen de v2 con personas (texto, sin imágenes)

Fuente: `data/scripts/_steps/ba6c3cac-f5v2/03_visual.json` (copia en `lab/hyperframes/f5/v2/03_visual.json`). 97 prompts en total; 44 con personas (sujeto o prompt nombra gente: hombre, mujer, niño, recluso, guardia, multitud, manos, siluetas…).

## Bloque que se agregó al canon (§1.6, lo único que cambia en `m03_visual`)

```
UBICACIONES DOCUMENTADAS (no mezclar en una misma escena):
- Menores detenidos → CYC (instalación juvenil), YSC (instalación juvenil); separados de los adultos.
- Mujeres → Penitenciaría Estatal de Luisiana (Angola); nunca en la misma celda que hombres.
- Evacuados → paso elevado de Broad Street sobre la Interestatal 10.
- turista, demandante → Bourbon Street.
- Ningún menor en celdas de adultos en ninguna escena.
```

## El que reemplaza al del niño en la celda

**v1 · ch02 imagen 8** — ancla «Hombres, mujeres y niños, todos ellos, observaban con impotencia cómo el mundo exterior se ahogaba.»

> A medium shot shows an African American woman and a young boy, about 10 years old, both in orange prison jumpsuits, standing on a bunk, peering out of a small, high, barred window at the rising floodwaters outside. Their attention is fixed outwards, their faces turned away from the camera, their silhouettes framed by the window, inside a dim, concrete prison cell. The dark water has reached halfway up the small windowpane, obscuring the view of the outside world. The color palette features the muted orange of the uniforms against the dark grey of the cell, with the murky brown water visible outside, backlit by the gloomy grey light from the window, with the interior of the cell in deep shadow. The mood is one of trapped helplessness, a quiet, dawning horror as they watch the disaster unfold from a cage, rendered in a documentary photographic realism, dark-history, faceless style, with shallow depth of field, focusing on the figures and the window, blurring the stark cell interior. The camera angle is eye-level, from behind the two figures. The image has a 16:9 aspect ratio.

**v2 · ch05 flux 6 ← REEMPLAZA AL DEL NIÑO EN LA CELDA** — ancla «Entre los atrapados por esta catástrofe había niños de hasta 10 años,» · centro juvenil (CYC/YSC): respeta el canon

> A detail shot captures the small, grimy hand of a 10-year-old African American boy, gripping two rusted steel bars of a cell door, his knuckles white with pressure. The focus is entirely on the hand, a symbol of trapped youth within a juvenile detention cell (CYC), with dark floodwater visible on the floor behind the bars. The child's fingernails are dirty, showing days of neglect, depicted with the reddish-brown of rust, the dark grey of steel, and the dark skin tone of the child's hand. A sliver of harsh light catches the knuckles, emphasizing the tension in the grip, creating a mood of stark vulnerability, the innocence of a child juxtaposed with the brutality of the prison environment, in a style of documentary photographic realism, dark-history, and faceless. Shallow depth of field blurs the cell's interior into a dark backdrop, with the camera eye-level with the hand. The image has a 16:9 aspect ratio.

Mismo lugar del cap en v2 (ch02 imagen 8): ancla «El teniente General del Cuerpo de Ingenieros del Ejército, Carl Strock, más tarde señalaría» — con personas.

### Otros prompts de v2 con niños

| cap | img | ancla | dónde lo ubica el prompt |
|---|---|---|---|
| ch05 | flux 7 | en una prisión cuya población juvenil era un abrumador 98.7% afroamericana. | centro juvenil (CYC/YSC): respeta el canon |

## Todos los prompts con personas

| cap | img | ancla (narración v2) | sujeto / inicio del prompt |
|---|---|---|---|
| ch01 | supp 1 | la Orleans Parish Prison, 6,375 reclusos son abandonados a su suerte. | A medium shot captures a group of incarcerated men, overwhelmingly African American, in orange prison jumpsuits, trapped inside a flooding prison block, standin |
| ch01 | supp 2 | El sheriff Marlin N. Gusman fue claro: se quedarían "donde pertenecen". | A medium shot of a middle-aged Caucasian man in an official sheriff's uniform, seen from behind his shoulder, stands at a press conference podium, making a shar |
| ch01 | supp 3 | Una sentencia dictada antes de que subiera el agua, | A close shot depicts the heavy, solid steel door of a prison cell, slamming shut with the implied sound of its heavy bolt engaging. The focus is on the mechanic |
| ch01 | supp 4 | que sería confirmada por la terrible decisión que el sheriff estaba a punto de anunciar. | A close shot frames the sheriff figure from the press conference, pausing for a weighted moment before speaking, his jaw set and lips pressed into a thin, hard  |
| ch02 | flux 1 | En una conferencia de prensa, el sheriff Marlin N. Gusman confirmó | A middle-aged Caucasian man in a sheriff's uniform, seen from the back and side. |
| ch02 | flux 2 | que los prisioneros no serían evacuados de la Prisión de Orleans Parish. | A group of anonymous, predominantly African American male inmates in orange jumpsuits. |
| ch02 | flux 4 | sumiendo los pabellones en una oscuridad densa. | The silhouettes of several inmates inside a dark cell. |
| ch02 | flux 8 | El teniente General del Cuerpo de Ingenieros del Ejército, Carl Strock, más tarde señalaría | The back of a man in a US Army Corps of Engineers uniform. |
| ch02 | flux 12 | Para los miles de prisioneros atrapados en la negrura, | A group of inmates, mostly African American, some appearing to be youths. |
| ch03 | flux 3 | sumiendo a los miles de prisioneros en una oscuridad absoluta | A vast, multi-tiered prison cell block filled with hundreds of incarcerated men, overwhelmingly African American. |
| ch03 | flux 12 | llenando los espacios confinados con un líquido denso y fétido. | The hands of an incarcerated African American man, gripping the bars of his cell door. |
| ch03 | flux 13 | Durante horas, en medio del caos, no hubo ninguna orden. | An empty prison guard's control station. |
| ch03 | flux 14 | Finalmente, a la medianoche, el sheriff Marlin N. Gusman cambió de parecer. | The hand of a middle-aged male sheriff, visible in a uniform sleeve. |
| ch03 | flux 16 | una decisión tardía que selló el destino de muchos. | Anonymous silhouettes of incarcerated men trapped in a vast, flooded cell block. |
| ch03 | flux 17 | Pero mientras los papeles se movían lentamente en el exterior, en el interior, la inundación avanzaba implacable. Y en a | The lower legs and feet of an incarcerated person wearing an orange jumpsuit. |
| ch04 | flux 0 | El agua no se detuvo en los tobillos. | The feet and lower legs of an incarcerated person, ethnicity indeterminate in the gloom. |
| ch04 | flux 3 | En los edificios Templeman 1 y 2, el agua pestilente, cargada de aguas residuales, ya había llegado hasta el pecho. | Three incarcerated African American men of varying ages. |
| ch04 | flux 4 | Los gritos de los hombres atrapados rebotaban en las paredes, | The face of an incarcerated African American man in his 30s, lean build. |
| ch04 | flux 5 | perdidos en el hedor y el silencio de los guardias ausentes. | An abandoned prison guard's station. |
| ch04 | flux 6 | Durante días, miles de personas sobrevivieron de pie, con el cuerpo sumergido en un caldo tóxico, | A massive crowd of incarcerated men, predominantly African American. |
| ch04 | flux 7 | sin agua potable ni comida. | A pair of dirty, calloused hands. |
| ch04 | flux 8 | La evacuación, cuando finalmente comenzó, fue un caos. | Silhouettes of people against a bright doorway. |
| ch04 | flux 10 | expuestos bajo el sol abrasador. | A group of exhausted incarcerated men on a highway. |
| ch04 | flux 11 | Pero esta operación fue desesperadamente lenta. | A long line of incarcerated people. |
| ch04 | flux 15 | Cuando las autoridades finalmente declararon el complejo vacío, creyeron que lo peor había pasado. | A lone figure in a white hazmat suit, seen from behind. |
| ch04 | flux 16 | Pero un nuevo horror estaba a punto de emerger del caos. Al comparar las listas, un agujero negro apareció en los regist | The hands of an office worker over two documents. |
| ch05 | flux 1 | Human Rights Watch lo confirmó: inmediatamente después de la evacuación, 517 reclusos no estaban contabilizados. | A chaotic pile of official inmate files and manila folders. |
| ch05 | flux 3 | y algunos testimonios ofrecían una respuesta aterradora. | A gaunt, middle-aged African American man with exhausted features, wearing a plain t-shirt. |
| ch05 | flux 5 | mientras eran evacuados. | A group of African American inmates, their orange jumpsuits soaked dark brown. |
| ch05 | flux 6 **← reemplaza al del niño en la celda** | Entre los atrapados por esta catástrofe había niños de hasta 10 años, | The small, grimy hand of a 10-year-old African American boy. |
| ch05 | flux 7 | en una prisión cuya población juvenil era un abrumador 98.7% afroamericana. | Three African American teenage boys in orange jumpsuits. |
| ch05 | flux 9 | "El sheriff de la cárcel declaró que ningún preso murió o escapó. | A white, middle-aged man in a crisp sheriff's uniform, seen from the chest up. |
| ch05 | flux 11 | La contradicción era flagrante, pero el sheriff Gusman la desestimó con desprecio, declarando sobre los testigos: | The same sheriff figure from before. |
| ch05 | flux 12 | "Están en la cárcel, hombre. Mienten... | A tight close-up on the sheriff's mouth as he speaks. |
| ch05 | flux 13 | No confíen en drogadictos, cobardes y criminales para saber cuál es la historia". | An African American inmate in his twenties, his face smudged with dirt. |
| ch06 | flux 1 | Robie Waganfeald, turista, y Paul Kunkel Jr., turista, habían sido arrestados en Bourbon Street por intoxicación pública | Two middle-aged Caucasian men in casual 2000s tourist attire. |
| ch06 | flux 2 | Quedaron atrapados en el mismo infierno que los demás prisioneros, | A group of inmates, predominantly African American, with two Caucasian men among them, all in orange jumpsuits. |
| ch06 | flux 3 | pero a diferencia de ellos, su condición de ciudadanos comunes de Ohio con familias que los buscaban les dio una voz que | A woman's hands, showing signs of age. |
| ch06 | flux 4 | un jurado federal les otorgó más de 650,000 dólares por encarcelamiento falso e indiferencia deliberada. | A pair of hands belonging to a court officer. |
| ch06 | flux 10 | Pero las demandas seguían acumulándose, intentando reconstruir lo sucedido. | A lawyer's desk at night. |
| ch06 | flux 12 | Buscaban pruebas, documentos, listas… y no encontraron nada. | A gloved hand. |
| ch07 | veo 0 | rpos vistos flotando y las vidas borradas del sistema nunca salió a la superficie. ¿Saldrá algún día? | A medium shot captures the still, dark surface of murky floodwater, reflecting the distorted, broken silhouette of a ruined prison building. The scene's focus i |
| ch07 | supp 3 | Oficialmente, la prisión albergaba a 6,375 reclusos, pero otras fuentes estiman que hubo hasta 8,000 evacuados de la pri | An extreme wide shot captures a vast, anonymous crowd of incarcerated men, overwhelmingly African American, in orange jumpsuits, milling about a concrete recrea |
| ch07 | supp 5 | Según un informe de Human Rights Watch, más de 500 prisioneros no figuraban en la lista de personas evacuadas de la cárc | A close shot depicts the hands of a faceless administrative worker at a desk, holding a pen which hovers, hesitating, over a long, typed roster of names on a cl |

## Prompts completos (con personas)

### ch01 · supp 1
- ancla: «la Orleans Parish Prison, 6,375 reclusos son abandonados a su suerte.»

> A medium shot captures a group of incarcerated men, overwhelmingly African American, in orange prison jumpsuits, trapped inside a flooding prison block, standing in dark, thigh-deep water, some clinging to cell bars. A man in the foreground stares directly forward, his eyes wide with pupils dilated, jaw muscles clenched, while others in the background are looking around in the darkness. The scene is the interior of a concrete cell block at Orleans Parish Prison in 2005, plunged into darkness as the power has failed. A dirty, waterlogged mattress is wedged against the bars of a cell door in a futile attempt to block the rising water. The bright orange of uniforms starkly contrasts with the monochromatic greys of concrete, rust-brown of steel, and black, murky water. Almost complete darkness prevails, with a single sliver of ambient light from a high, unseen window glinting off the surface of the filthy water. A mood of rising dread and entrapment is conveyed by the encroaching dark water, the deep shadows, and the tense posture of the men. The style is documentary photographic realism, dark-history, faceless, using a shallow depth of field, focusing on the man in the foreground, with the camera at eye-level with the prisoners. The image has a 16:9 aspect ratio.

### ch01 · supp 2
- ancla: «El sheriff Marlin N. Gusman fue claro: se quedarían "donde pertenecen".»

> A medium shot of a middle-aged Caucasian man in an official sheriff's uniform, seen from behind his shoulder, stands at a press conference podium, making a sharp, dismissive gesture with his hand; his head is turned towards the microphones, his face obscured in shadow and by the camera angle, all within an institutional, wood-paneled press room from the early 2000s, with flags in the background. A tight cluster of boxy, early-2000s press microphones with foam windscreens sits on the lectern, colored by the muted browns of the wood paneling, official dark greens of the uniform, and a sickly yellow cast from overhead lights, all under harsh, institutional overhead fluorescent lighting, conveying a mood of cold, bureaucratic indifference, expressed through the sterile environment and the authoritative, uncaring gesture. This is presented in a documentary photographic realism, dark-history, faceless style, captured with a 50mm lens and deep depth of field from a slightly low angle, emphasizing the figure's authority. The image has a 16:9 aspect ratio.

### ch01 · supp 3
- ancla: «Una sentencia dictada antes de que subiera el agua,»

> A close shot depicts the heavy, solid steel door of a prison cell, slamming shut with the implied sound of its heavy bolt engaging. The focus is on the mechanical finality of the lock, with a guard's hand just pulling away. The setting is a stark corridor in the Orleans Parish Prison before the flood, where the walls and floor are dry. Details include the well-worn, heavy steel deadbolt mechanism, with visible scratches and spots of rust around it. A cold industrial palette features grey steel, off-white concrete block walls, and the dark tones of the guard's uniform sleeve. Stark, overhead fluorescent light from the corridor creates hard shadows on the steel. The mood is one of irreversible finality and foreboding, conveyed by the mass of the steel door and the decisive action of it being locked. The style is documentary photographic realism, dark-history, and faceless, utilizing a shallow depth of field with the focus sharply on the bolt as it slides into place. The camera angle is eye-level, focused tightly on the locking mechanism of the cell door, with "C-BLOCK 4" painted on the wall next to the cell door in stenciled block lettering. The image has a 16:9 aspect ratio.

### ch01 · supp 4
- ancla: «que sería confirmada por la terrible decisión que el sheriff estaba a punto de anunciar.»

> A close shot frames the sheriff figure from the press conference, pausing for a weighted moment before speaking, his jaw set and lips pressed into a thin, hard line. His eyes are obscured by shadow, his focus directed downward toward the podium, building tension before the announcement. The setting is the same press conference podium, but now tightly framed to isolate the subject. A single drop of sweat is visible on his upper lip, caught in the harsh key light. The image features high contrast tones, with deep shadows and specular highlights on the microphones and skin, under dramatic low-key lighting where a single, hard key light from the side carves his features out of the darkness. An ominous suspense emanates, the weight of a terrible decision conveyed through the tense facial muscles and dramatic, shadowy lighting. The style is documentary photographic realism, dark-history, faceless, captured with an 85mm lens and shallow depth of field, isolating his expression from the background. The camera is at a low angle, looking up at his mouth and chin. The image has a 16:9 aspect ratio.

### ch02 · flux 1
- ancla: «En una conferencia de prensa, el sheriff Marlin N. Gusman confirmó»

> A medium shot of a middle-aged Caucasian man in a sheriff's uniform, seen from the back and side, leaning into a cluster of microphones at a press conference lectern, speaking and looking straight ahead, past the cameras, his jaw set firmly, in a wood-paneled press room, crowded with the indistinct shapes of journalists. A dense bouquet of early 2000s microphones with foam covers, some bearing local news channel logos, is visible, all in a color palette of browns from the wood paneling, dark uniform colors, and silver from the microphones. The harsh, direct on-camera flash lighting creates sharp shadows, contributing to a tense, official atmosphere, the air crackling with media attention, in a documentary photographic realism, dark-history, faceless style with deep depth of field, from an eye-level camera angle from the perspective of the press. The image has a 16:9 aspect ratio.

### ch02 · flux 2
- ancla: «que los prisioneros no serían evacuados de la Prisión de Orleans Parish.»

> A medium shot depicts a group of anonymous, predominantly African American male inmates in orange jumpsuits standing in the cramped space of a cell, viewed through its vertical steel bars. Some men stare blankly forward, others look down at the concrete floor, and one man grips the bars, his knuckles white. The setting is a cell block inside the Orleans Parish Prison, with concrete block walls and rusted steel doors, and there is a pattern of rust and peeling paint on the steel bars in the foreground. The color palette features drab institutional off-white, the faded orange of the uniforms, and reddish-brown rust, under dim, flickering overhead fluorescent lighting that casts long, distorted shadows. The mood is an oppressive, stagnant atmosphere of confinement and uncertainty, rendered in a documentary photographic realism style that is dark-history and faceless, with a deep depth of field showing multiple cells receding into the background. The camera angle is eye-level, shooting through the cell bars. The image has a 16:9 aspect ratio.

### ch02 · flux 4
- ancla: «sumiendo los pabellones en una oscuridad densa.»

> A medium shot captures the silhouettes of several inmates inside a dark cell, standing motionless, their forms barely discernible against the faint light from a distant corridor. One figure's head is tilted up toward a high, barred window, a sliver of lighter darkness, inside a prison cell, now in near-total darkness. Motes of dust catch the minimal ambient light, floating in the still air, all rendered in monochromatic shades of deep gray and black with extremely low-key lighting, only faint, indirect light creating subtle rim lighting on the figures' shoulders and heads, evoking a claustrophobic, breathless silence, the feeling of being entombed. The style is documentary photographic realism, dark-history, faceless, employing a shallow depth of field with the foreground figures slightly out of focus, all captured from a low angle, from the floor of the cell looking up. The image has a 16:9 aspect ratio.

### ch02 · flux 8
- ancla: «El teniente General del Cuerpo de Ingenieros del Ejército, Carl Strock, más tarde señalaría»

> A medium shot of the back of a man in a US Army Corps of Engineers uniform, pointing with a single finger to a specific location on a large engineering blueprint. The man's head is bent in concentration over the blueprint; the viewer's eye is guided by his hand. The setting is an operations room, with other maps and charts visible but blurred in the background. The intricate lines and annotations of the levee cross-section are visible on the blueprint. The color palette features the olive drab of the uniform and the stark white and blue of the architectural drawing, under harsh, functional overhead lighting. The mood is clinical, detached analysis in the aftermath of disaster. The style is documentary photographic realism, dark-history, and faceless, with a shallow depth of field. An over-the-shoulder shot focuses on the hand and the diagram. The image has a 16:9 aspect ratio.

### ch02 · flux 12
- ancla: «Para los miles de prisioneros atrapados en la negrura,»

> A medium shot captures a group of inmates, mostly African American and some appearing to be youths, trapped in a flooding cell, standing in murky, chest-deep water. Their eyes are wide, whites visible, straining to see in the darkness. Faces are slick with sweat and foul water, jaws clenched, and one inmate's mouth is open in a silent gasp for air. This scene unfolds in a cell block within the Templeman section of Orleans Parish Prison. A styrofoam tray, carrying remnants of a final meal, floats past in the filthy water. The color palette is near-black and white, with the dark water and pale reflections being the main tones, while the orange of their jumpsuits is a dull, sodden brown. Extremely low-key lighting, with a single, weak beam of external light cutting through a high window, illuminates the rising water and tense faces. The mood is one of raw, rising panic; the air is thick, hot, and heavy with the smell of sewage, and shoulders are drawn up, bodies pressed against walls. The style is documentary photographic realism, dark-history, and faceless. A wide-angle lens makes the cell walls feel like they are closing in, and a water-level camera angle creates a sense of being trapped in the flood with them. The image has a 16:9 aspect ratio.

### ch03 · flux 3
- ancla: «sumiendo a los miles de prisioneros en una oscuridad absoluta»

> A wide shot captures a vast, multi-tiered prison cell block filled with hundreds of incarcerated men, overwhelmingly African American, reacting to a sudden total power loss, their movements becoming uncertain in the blackness. Anonymous silhouettes turn towards the now-dead overhead lights, their faces completely obscured in shadow within the large, open prison block, its cavernous structure now a pitch-black void. The geometric pattern of cell doors and catwalks forms a stark, skeletal silhouette against a single high, barred window. The color palette is almost pure black, with deep grey metallic sheens on railings hit by faint, distant moonlight in near total darkness, with only the faintest ambient moonlight from a high window, creating a sudden, disorienting void, a vast, populated space instantly transformed into a massive tomb. Rendered in a documentary photographic realism, dark-history, faceless style with a wide-angle lens from a low angle, looking up. The image has a 16:9 aspect ratio.

### ch03 · flux 12
- ancla: «llenando los espacios confinados con un líquido denso y fétido.»

> A close shot focuses on the hands of an incarcerated African American man, gripping the bars of his cell door, clinging tightly to the steel bars, knuckles white with strain, just above the surface of the opaque water. The focus is on the desperate, powerful grip of the hands against the immovable steel inside a flooded prison cell, with the water level high, close to the man's chest. The thick, filthy water laps just inches below his hands, its surface littered with small pieces of floating debris. The color palette features the dark, rust-orange of the wet jumpsuit, the grey of the rusted steel bars, and the black-brown of the water, all illuminated by dim, non-directional light reflecting off the murky water's surface. The mood is one of raw desperation, with knuckles white with tension and the body pressed against the bars, a visceral image of being trapped in rising filth, rendered in a documentary photographic realism style, dark-history, and faceless. A shallow depth of field is used, with the camera angle level with the hands and water surface. The image has a 16:9 aspect ratio.

### ch03 · flux 13
- ancla: «Durante horas, en medio del caos, no hubo ninguna orden.»

> A wide shot captures an empty prison guard's control station, an abandoned room where a desk phone lies off the hook and papers are scattered across the wet floor. The camera, positioned inside the booth, looks out through thick, grimy glass into a dark, empty corridor of a prison central control room, which clearly shows signs of a hasty desertion. A bank of dead monitor screens reflects the chaotic state of the room, all rendered in a faded institutional green and beige, and grey concrete, under dim light. A single sliver of light from an exterior window cuts across the scene, contributing to an eerie mood of abandonment and the complete breakdown of order and authority, a chilling vacuum of command. The image is presented with documentary photographic realism, dark-history, and a faceless style, employing a deep depth of field and an eye-level camera angle from inside the booth. The image has a 16:9 aspect ratio.

### ch03 · flux 14
- ancla: «Finalmente, a la medianoche, el sheriff Marlin N. Gusman cambió de parecer.»

> A close shot depicts the hand of a middle-aged male sheriff, visible in a uniform sleeve, signing his name at the bottom of an official document with a deliberate, firm motion. The close-up focuses on the tip of the pen leaving a trail of black ink on the paper, all within a dry, orderly office at night, far removed from the prison's chaos. A brass desk clock is in the soft-focus background, its hands indicating a time close to midnight. The color palette features stark white paper, black ink, the deep navy blue of a uniform sleeve, and the warm brown of a wooden desk. A single, focused desk lamp creates a pool of harsh light on the document, contributing to a mood of cold bureaucratic detachment where the slow, deliberate motion of a pen holds the weight of thousands of lives. The style is documentary photographic realism, dark-history, and faceless, achieved with a shallow depth of field and a high-angle, over-the-shoulder camera angle. The image has a 16:9 aspect ratio.

### ch03 · flux 16
- ancla: «una decisión tardía que selló el destino de muchos.»

> A wide shot shows anonymous silhouettes of incarcerated men trapped in a vast, flooded cell block, standing motionless in chest-deep, filthy water, their forms reflected on the dark surface. Their postures are of exhaustion and waiting, faces lost to the deep shadows, bodies outlined by faint backlight within a cavernous, multi-story prison block, submerged in darkness and contaminated water. The perfect, geometric reflections of the prison bars are warped and broken by ripples in the black water, all rendered with a monochromatic palette of deep blacks and greys, with silvery highlights on the water from a distant, high window. The extreme low-key lighting, backlit by a single faint light source, creates stark, anonymous silhouettes, evoking utter hopelessness, the silent, collective resignation of men abandoned to their fate in a flooded cage. This documentary photographic realism, dark-history, faceless image is captured with a wide-angle lens at eye-level, from a distance. The image has a 16:9 aspect ratio.

### ch03 · flux 17
- ancla: «Pero mientras los papeles se movían lentamente en el exterior, en el interior, la inundación avanzaba implacable. Y en algunos edificios, el nivel del agua ya estaba subiendo mucho más allá de los tobillos.»

> A detail shot captures the lower legs and feet of an incarcerated person wearing an orange jumpsuit, standing still in murky, calf-deep water that is visibly rising, with the focus on the dark, wet stain creeping up the orange fabric of the jumpsuit. This scene unfolds on the concrete floor of a prison cell, featuring a clear, dark waterline on the fabric well above the current water level, showing how quickly the flood is rising. The bright, saturated orange of the jumpsuit turns a dark, muddy brown where it is soaked by the grey-green water, all under dim, ambient light reflecting off the disturbed surface of the water, creating a mood of inexorable dread; the quiet, unstoppable progression of the disaster, a personal, slow-motion submersion. The style is documentary photographic realism, dark-history, faceless, captured with a shallow depth of field from a very low angle, at water level. The image has a 16:9 aspect ratio.

### ch04 · flux 0
- ancla: «El agua no se detuvo en los tobillos.»

> A detail shot captures the feet and lower legs of an incarcerated person, their ethnicity indeterminate in the gloom, standing in murky, dark water that is rising above their ankles, with ripples disturbing the surface. The focal point is on the rising water level against the person's skin and the saturated orange fabric of their uniform. The setting is the concrete floor of a prison cell, disappearing into darkness. The hems of the orange prison jumpsuit are soaked dark, clinging to the person's legs. A monochromatic dark gray and black color palette is present, with a sliver of soiled orange from the uniform reflecting weakly in the water. Low-key ambient light from an unseen source creates a stark, high-contrast scene, conveying an ominous tension and the physical sensation of a slow, inevitable threat. The style is documentary photographic realism, dark-history, and faceless, utilizing a shallow depth of field that focuses sharply on the water line, captured from a low angle, close to the water's surface. The image has a 16:9 aspect ratio.

### ch04 · flux 3
- ancla: «En los edificios Templeman 1 y 2, el agua pestilente, cargada de aguas residuales, ya había llegado hasta el pecho.»

> A medium shot depicts three incarcerated African American men of varying ages standing together for support in a cramped space, submerged to their chests in filthy, opaque water. Their faces are turned slightly away, but their tense shoulders and arms pressed against the wall convey entrapment inside a flooded prison cell in the Templeman building. Small pieces of unidentifiable filth float on the water's surface around them. The color palette features sickly browns and greens of the sewage-filled water, contrasted with the faded orange of their jumpsuits. A single, weak light source from above casts harsh shadows on their submerged bodies, creating a mood of claustrophobic misery and forced intimacy in a toxic environment, rendered in a documentary photographic realism, dark-history, faceless style. An 85mm lens compresses the space to feel more claustrophobic, with the camera at eye-level with the standing men. The image has a 16:9 aspect ratio.

### ch04 · flux 4
- ancla: «Los gritos de los hombres atrapados rebotaban en las paredes,»

> A close shot features the face of an incarcerated African American man in his 30s, lean-built, shouting upwards with his mouth open wide, the tendons in his neck strained and prominent. His eyes are squeezed shut, brow deeply furrowed, and face contorted with the physical effort of the scream, all within the dark confines of a cell, with a concrete block wall visible behind him. Sweat and grime trace paths down his temples and cheeks. The high-contrast chiaroscuro palette uses warm, dark skin tones against deep black shadows. Hard side lighting from a single, low source illuminates one side of his face and leaves the other in shadow, conveying a raw, unheard cry of desperation and immense physical and emotional strain, in a documentary photographic realism, dark-history, faceless style. A shallow depth of field keeps his face in sharp focus, while the background is blurred into darkness, captured from a low angle looking up at his face. The image has a 16:9 aspect ratio.

### ch04 · flux 5
- ancla: «perdidos en el hedor y el silencio de los guardias ausentes.»

> A medium shot of an abandoned prison guard's station depicts an empty post, with a swivel chair pushed back and a landline telephone half-submerged in murky water on the console. The focus is on the empty chair, a symbol of absence and dereliction of duty, within a control booth featuring thick glass windows that look out onto a dark, flooded cell block. A clipboard with papers fused together by water lies on the floor, partially floating. The color palette consists of cold institutional blues and grays, muted by layers of grime and the brown of the floodwater. Flat, dim, ambient light creates a sense of sterile abandonment, contributing to a mood of eerie silence and the profound emptiness of authority having fled. The style is documentary photographic realism, dark-history, and faceless, rendered with a deep depth of field, keeping both the empty station and the dark corridor beyond in focus. The camera angle is eye-level, from outside the booth looking in. The image has a 16:9 aspect ratio.

### ch04 · flux 6
- ancla: «Durante días, miles de personas sobrevivieron de pie, con el cuerpo sumergido en un caldo tóxico,»

> An extreme wide shot captures a massive crowd of incarcerated men, predominantly African American, standing packed together in a vast, dark space, the water up to their chests. Most are seen from behind or in profile, a sea of heads and shoulders; a few faces look up with hollow, exhausted eyes. This scene unfolds in a prison gymnasium or large common hall, submerged in darkness and floodwater. The air is thick with visible humidity, hanging in the dim light, creating a dark tableau of muted oranges from uniforms against the black, reflective water and gray walls. A few isolated beams of light from a damaged ceiling cut through the darkness, illuminating small sections of the crowd, portraying a landscape of mass human suffering and grim, silent endurance. This is rendered with documentary photographic realism, dark-history, and a faceless style, utilizing a wide-angle lens to capture the scale of the hundreds of people, from a high angle looking down on the immense, trapped crowd. The image has a 16:9 aspect ratio.

### ch04 · flux 7
- ancla: «sin agua potable ni comida.»

> A detail shot features a pair of dirty, calloused hands cupped together, lifting brownish, debris-filled water towards a face just out of frame. The focus is entirely on the desperate action of the hands and the unsuitability of the water. This scene unfolds indoors, surrounded by darkness and the surface of the flood. The water held in the hands is opaque, with tiny flecks of filth clearly visible. The color palette consists of earthy, dirty browns and grays, with the paleness of the knuckles showing strain. Soft, dim light from an indeterminate source models the form of the hands, evoking a mood of primal desperation, an agonizing conflict between thirst and poison. The style is documentary photographic realism, dark-history, and faceless, captured with a macro lens, accentuating the texture of the dirty skin and the contaminated water, from an eye-level camera angle. The image has a 16:9 aspect ratio.

### ch04 · flux 8
- ancla: «La evacuación, cuando finalmente comenzó, fue un caos.»

> A medium shot captures the silhouettes of people against a bright doorway, engaged in a chaotic scramble as incarcerated men try to climb from a flooded building onto a waiting rescue boat. The figures are a mass of limbs, all motion directed towards the single point of escape from the flooded prison entrance, which leads out into daylight. The rescue boat is a simple, flat-bottomed metal vessel, already crowded. There is an extreme contrast of deep black silhouettes against a blown-out, harsh white exterior, with harsh backlighting from the sun outside obscuring all detail of the figures. The mood is panic and disarray, a desperate and disorganized flight to safety, presented in a documentary photographic realism, dark-history, faceless style. A wide-angle lens captures the frenetic energy from an eye-level camera angle, from the perspective of the boat. The image has a 16:9 aspect ratio.

### ch04 · flux 10
- ancla: «expuestos bajo el sol abrasador.»

> A medium shot shows a group of exhausted incarcerated men on a highway, sitting and lying directly on the hot asphalt of the overpass, some using their hands to shield their eyes from the sun. Their bodies are slumped, postures of complete physical depletion. Faces are grim, eyes squinting against the glare. They are on the shoulder of the I-10 overpass, surrounded by other evacuees. Heat haze visibly radiates from the surface of the highway, captured with washed-out colors under the harsh sun, pale gray concrete, faded orange uniforms, and the deep black of the asphalt. The lighting is overexposed, with harsh midday sunlight and no cloud cover, casting sharp, short shadows, all contributing to a mood of brutal exposure and exhaustion, a desperate limbo with no relief. The style is documentary photographic realism, dark-history, faceless, using a telephoto lens to compress the scene and enhance the shimmering heat effect, with a low angle emphasizing the heat rising from the ground. The image has a 16:9 aspect ratio.

### ch04 · flux 11
- ancla: «Pero esta operación fue desesperadamente lenta.»

> A wide shot shows a long line of incarcerated people standing motionless, waiting in a line that stretches towards the horizon along the highway overpass. The figures are largely anonymous, their individual identities lost in the immense scale of the line in the vast, exposed expanse of the I-10 overpass. The line appears static, with no discernible movement or progress, under a monotonous palette of gray concrete and repeating spots of orange under a pale, washed-out blue sky. Flat, unforgiving midday sun emphasizes a mood of stagnation and hopelessness, the visual representation of a bureaucratic standstill, in a style of documentary photographic realism, dark-history, and facelessness. A deep depth of field makes the entire line appear sharp, emphasizing its seemingly infinite length from an eye-level camera angle looking down the length of the line. The image has a 16:9 aspect ratio.

### ch04 · flux 15
- ancla: «Cuando las autoridades finalmente declararon el complejo vacío, creyeron que lo peor había pasado.»

> A wide shot captures a lone figure in a white hazmat suit, seen from behind, standing still in the center of a vast, debris-strewn prison courtyard, surveying the damage. The figure's posture is static, taking in the scale of the empty, silent complex, which is the main courtyard of the Orleans Parish Prison, post-evacuation. The ground is a cracked-mud plain, littered with unrecognizable wreckage, with the stark white of the hazmat suit contrasted against the uniform gray and brown of the ruined prison under flat, overcast daylight. The mood is one of a false calm, an eerie quiet that precedes a more terrible discovery, rendered in a style of documentary photographic realism, dark-history, and faceless. A wide-angle lens makes the lone figure seem small against the massive, damaged buildings, shot at eye-level, positioned behind the figure. The image has a 16:9 aspect ratio.

### ch04 · flux 16
- ancla: «Pero un nuevo horror estaba a punto de emerger del caos. Al comparar las listas, un agujero negro apareció en los registros: faltaban más de 500 personas. ¿Dónde estaban?»

> A close shot depicts the hands of an office worker comparing two different prisoner manifests side-by-side; a finger on the left hand traces down a list of names, while the right hand scans the other list, finding only blank spaces, with intense focus on the discrepancy between the two lists, the physical act of discovering the missing people. This takes place in a makeshift office, late at night, where the manifests are dot-matrix printouts, slightly water-damaged, with inconsistent handwritten notes in the margins, all illuminated by the warm yellow of a desk lamp on off-white paper, surrounded by deep shadows. The high-contrast, low-key lighting from a single desk lamp creates a stark, dramatic effect, contributing to a mood of slow-dawning, bureaucratic horror, the chilling realization of a massive, unaccounted-for human toll, rendered in documentary photographic realism, dark-history, faceless style. A shallow depth of field focuses on the finger moving down the page and the empty space on the opposing list, captured from a top-down camera angle, directly over the papers. The image has a 16:9 aspect ratio.

### ch05 · flux 1
- ancla: «Human Rights Watch lo confirmó: inmediatamente después de la evacuación, 517 reclusos no estaban contabilizados.»

> A medium shot captures a chaotic pile of official inmate files and manila folders, floating on the surface of dark, stagnant floodwater that fills a records room. The scene is static, focused on the disarray of lost records in a submerged prison file room, where the tops of metal filing cabinets barely break the water's surface. A single inmate's photograph, a mugshot from the early 2000s, floats face-up, detached from its file. The color palette features greasy black water, muted manila yellow, institutional gray, and patches of green mold. Low-key, single-source light from a distant opening creates long shadows on the water, evoking a mood of irrecoverable loss, the tangible evidence of systemic failure and unaccounted lives. This is presented in a documentary photographic realism style, dark-history, and faceless, with a deep depth of field showing the extent of the flooded room, at an eye-level camera angle with the water's surface. The image has a 16:9 aspect ratio.

### ch05 · flux 3
- ancla: «y algunos testimonios ofrecían una respuesta aterradora.»

> A medium shot of a gaunt, middle-aged African American man with exhausted features, wearing a plain t-shirt, recounting his experience to an unseen person off-camera. His eyes are fixed on a point in the distance, not looking at the camera, his brow furrowed as he accesses a difficult memory, all within a stark, bare room with a concrete wall background, suggesting a temporary shelter or interview space. A single, deep line is etched between his eyebrows from sustained stress, accentuated by muted greys of concrete, drab civilian clothing tones, and sallow skin tones, illuminated by soft, single-source side light that highlights the weary texture of his face. The heavy weight of traumatic memory creates a quiet but profound disturbance in a documentary photographic realism, dark-history, faceless style, captured with an 85mm lens, isolating him from his surroundings, at eye-level, slightly to the side. The image has a 16:9 aspect ratio.

### ch05 · flux 5
- ancla: «mientras eran evacuados.»

> A wide shot captures a group of African American inmates, their orange jumpsuits soaked dark brown, as they wade with great effort through chest-high, murky water, holding onto each other for stability. Their faces are turned away from the camera, focused on the difficult passage, and their bodies are tense with the strain of moving through the water. This large, flooded common area within the prison shows steel tables and benches submerged beneath them, and one inmate clutches a floating plastic bag containing his few possessions. The monochromatic scene of dark water and wet concrete is punctuated by the dark, soaked orange of the uniforms, illuminated by a low-key, ambient light from an unseen source, reflecting weakly off the water's surface. A grim, desperate exodus unfolds, the air thick with the smell of sewage and decay, presented in a documentary photographic realism, dark-history, faceless style. A deep depth of field shows the long line of men stretching into the darkness, viewed at eye-level with the inmates. The image has a 16:9 aspect ratio.

### ch05 · flux 6
- ancla: «Entre los atrapados por esta catástrofe había niños de hasta 10 años,»

> A detail shot captures the small, grimy hand of a 10-year-old African American boy, gripping two rusted steel bars of a cell door, his knuckles white with pressure. The focus is entirely on the hand, a symbol of trapped youth within a juvenile detention cell (CYC), with dark floodwater visible on the floor behind the bars. The child's fingernails are dirty, showing days of neglect, depicted with the reddish-brown of rust, the dark grey of steel, and the dark skin tone of the child's hand. A sliver of harsh light catches the knuckles, emphasizing the tension in the grip, creating a mood of stark vulnerability, the innocence of a child juxtaposed with the brutality of the prison environment, in a style of documentary photographic realism, dark-history, and faceless. Shallow depth of field blurs the cell's interior into a dark backdrop, with the camera eye-level with the hand. The image has a 16:9 aspect ratio.

### ch05 · flux 7
- ancla: «en una prisión cuya población juvenil era un abrumador 98.7% afroamericana.»

> A medium shot depicts three African American teenage boys in orange jumpsuits, huddled together for warmth and security on the top metal bunk of a cell, their feet drawn up away from the water below. They stare out through the cell bars, their young faces a mixture of fear and defiance, with wide eyes and set jaws. The setting is a flooded juvenile dormitory cell where dark water is just inches below their mattress. A thin, worn blanket is wrapped around the shoulders of two of the boys. The color palette features faded orange, dull grey metal, dark water, and the deep tones of their skin, all under dim, oppressive light from the corridor, silhouetting their forms. The mood is one of trapped and abandoned youth, a physical manifestation of a stark statistical reality, rendered in a documentary photographic realism, dark-history, faceless style, with a deep depth of field showing the confined space and the threat of the rising water, captured at eye-level, through the bars. The image has a 16:9 aspect ratio.

### ch05 · flux 9
- ancla: «"El sheriff de la cárcel declaró que ningún preso murió o escapó.»

> A medium shot of a white, middle-aged man in a crisp sheriff's uniform, seen from the chest up, speaking with a rigid posture at a podium, his expression hard and unyielding. He stares directly forward, over the heads of the press, with an air of absolute authority during a press conference, with the out-of-focus seals of the city and state behind him. The star-shaped sheriff's badge on his chest is polished to a high shine, reflecting the khaki uniform, polished brass badge, and deep wood tones of the podium. Flat, bright television lighting washes out nuance from his expression, contributing to a mood of unyielding official denial, the cold face of bureaucratic power, in a style of documentary photographic realism, dark-history, and facelessness. An 85mm lens isolates him against the background, captured at an eye-level camera angle. The image has a 16:9 aspect ratio.

### ch05 · flux 11
- ancla: «La contradicción era flagrante, pero el sheriff Gusman la desestimó con desprecio, declarando sobre los testigos:»

> A medium shot shows the same sheriff figure from before turning his head slightly away from the microphones with a dismissive expression. His eyes look down and to the side, breaking contact, and the corner of his mouth is pulled back in a sneer at the same press conference podium. A muscle in his jaw is visibly clenched, all rendered in a color palette of khaki, brass, and the deep shadows cast by the harsh lighting. Harsh side-lighting emphasizes the contemptuous curl of his lip, conveying an arrogant dismissal, the contempt of an official for the people he oversees, in a documentary photographic realism, dark-history, faceless style. A shallow depth of field is used with an eye-level camera angle. The image has a 16:9 aspect ratio.

### ch05 · flux 12
- ancla: «"Están en la cárcel, hombre. Mienten...»

> A detail shot tightly frames the sheriff's mouth as he speaks, his lips pressed thin and curled slightly at the edge, forming words of contempt. The shot is impersonal, focusing on the physical act of dehumanizing speech in an extreme close-up, removing all background context. There is a faint shadow of stubble on his upper lip. Natural skin tones are visible under the harsh, flattening press conference lights, with direct, bright frontal lighting contributing to the clinical, ugly mechanics of prejudice and dismissal. The style is documentary photographic realism, dark-history, and faceless, captured with a macro lens at a straight-on, eye-level camera angle. The image has a 16:9 aspect ratio.

### ch05 · flux 13
- ancla: «No confíen en drogadictos, cobardes y criminales para saber cuál es la historia".»

> A close shot depicts an African American inmate in his twenties, his face smudged with dirt, standing silently and absorbing a verbal assault. He stares directly into the lens, his eyes wide and unblinking, his jaw clenched so tightly a muscle flexes, and his brow knotted. The setting is a temporary holding area, possibly a gymnasium, with a chain-link fence blurred in the background. A clean track cuts through the grime on his cheek, left by a single tear. The color palette features muted earth tones, the grey of the fence, and the dark orange of his jumpsuit. Low-key, dramatic light illuminates one side of his face and leaves the other in shadow. The mood conveys powerless rage and the crushing weight of being disbelieved and dehumanized. The style is documentary photographic realism, dark-history, and faceless, employing a shallow depth of field, focusing intensely on his expression, from an eye-level camera angle. The image has a 16:9 aspect ratio.

### ch06 · flux 1
- ancla: «Robie Waganfeald, turista, y Paul Kunkel Jr., turista, habían sido arrestados en Bourbon Street por intoxicación pública justo antes de la tormenta.»

> A medium shot shows two middle-aged Caucasian men in casual 2000s tourist attire, being handcuffed from behind by a New Orleans police officer on a crowded street; one man looks down at the pavement with a tight jaw, while the other glances sideways with a confused, slack-jawed expression. The scene is Bourbon Street at dusk, with neon signs glowing and a sense of evening revelry just beginning, and a discarded plastic souvenir cup lies on the ground near the men's feet. Vibrant pink and blue neon lights cast colored glows on the wet pavement, contrasted with the dark blue police uniform, under mixed lighting from street lamps and bright, colorful neon signs. The mood is a moment of mundane trouble, oblivious to the impending larger catastrophe, captured with documentary photographic realism, dark-history, and a faceless style, utilizing a deep depth of field and an eye-level camera angle. The image has a 16:9 aspect ratio.

### ch06 · flux 2
- ancla: «Quedaron atrapados en el mismo infierno que los demás prisioneros,»

> A wide shot shows a group of inmates, predominantly African American, with two Caucasian men among them, all in orange jumpsuits, standing in dark, murky, chest-deep water inside a flooded prison tier. Their faces are barely visible in the gloom, with eyes wide and scanning the darkness, bodies pressed together for stability, within a cell block in Orleans Parish Prison, completely dark and flooded after the levee breach. A single, waterlogged mattress is wedged against cell bars just above the water line. The scene is rendered in a monochromatic palette of dark grays and blacks, with oily sheens on the water reflecting a single distant light source in almost complete darkness, pierced by one weak, distant flashlight beam from an unseen source, conveying silent, collective dread in a pitch-black, submerged environment in a documentary photographic realism, dark-history, faceless style with a deep depth of field at an eye-level camera angle. The image has a 16:9 aspect ratio.

### ch06 · flux 3
- ancla: «pero a diferencia de ellos, su condición de ciudadanos comunes de Ohio con familias que los buscaban les dio una voz que el sistema no pudo ignorar.»

> A close shot frames a woman's hands, showing signs of age, as they clutch a worn, early 2000s color photograph of a smiling family. The knuckles are white with pressure, and a thumb gently strokes the face of a man in the photo, all set in a dimly lit domestic living room, somewhere in the American Midwest. The photograph has slightly curled edges and a glossy finish typical of the era. The scene is rendered in warm, faded tones of a home interior, contrasting with the slightly faded colors of the photograph, illuminated by soft, warm light from a nearby table lamp, evoking a mood of quiet desperation and hope focused on a tangible memory, in a documentary photographic realism, dark-history, faceless style, with a shallow depth of field from a high angle looking down at the hands. The image has a 16:9 aspect ratio.

### ch06 · flux 4
- ancla: «un jurado federal les otorgó más de 650,000 dólares por encarcelamiento falso e indiferencia deliberada.»

> A close shot captures a pair of hands belonging to a court officer, placing a thick legal document, bound with a staple and bearing a court seal, onto a judge's polished wooden bench. The hands move with practiced, formal precision within a federal courtroom with imposing, dark wood paneling. The embossed seal of the federal court is pressed into the top page of the document, which is dated 2010. The scene is rendered with rich mahogany and walnut tones, cream-colored paper, and the gold foil of an official seal, illuminated by sober, even fluorescent courtroom lighting. The weight of official judgment is conveyed through this formal, deliberate action in a documentary photographic realism, dark-history, faceless style, employing a shallow depth of field and an eye-level camera angle. The image has a 16:9 aspect ratio.

### ch06 · flux 10
- ancla: «Pero las demandas seguían acumulándose, intentando reconstruir lo sucedido.»

> A medium shot of a lawyer's desk at night, completely buried under towering, chaotic stacks of legal briefs, depositions, and manila folders. The focus is on the overwhelming volume of paper in a cramped, small law office, long after working hours. A half-empty, cold cup of coffee sits on the only clear corner of the desk, all illuminated by yellow light from a desk lamp on cream and beige paper, surrounded by deep shadows and dark wood. Low-key night lighting dominates, with a single, harsh desk lamp casting the mood of the crushing, endless weight of documenting a tragedy, rendered in documentary photographic realism, dark-history, faceless style with deep depth of field at an eye-level camera angle. The image has a 16:9 aspect ratio.

### ch06 · flux 12
- ancla: «Buscaban pruebas, documentos, listas… y no encontraron nada.»

> A close shot features a gloved hand pulling open the drawer of a rust-eaten, mud-stained filing cabinet, revealing nothing inside; the hand pauses, holding the completely empty drawer open, within a derelict, water-damaged office inside the abandoned Orleans Parish Prison. Water stains and patches of black mold are visible on the wall behind the cabinet, all rendered in a color palette of reddish-brown rust, peeling beige paint, and the gray of oxidized metal. Dim, ambient light filters through a grimy window, contributing to the chilling mood of a void, evidence deliberately erased or utterly lost. This is captured in a documentary photographic realism, dark-history, faceless style, with a shallow depth of field from an eye-level camera angle. The image has a 16:9 aspect ratio.

### ch07 · veo 0
- ancla: «rpos vistos flotando y las vidas borradas del sistema nunca salió a la superficie. ¿Saldrá algún día?»

> A medium shot captures the still, dark surface of murky floodwater, reflecting the distorted, broken silhouette of a ruined prison building. The scene's focus is directed downwards into the opaque, mysterious water on the flooded grounds of the abandoned Orleans Parish Prison, weeks after Hurricane Katrina. A single, unidentifiable piece of fabric floats motionlessly on the water's surface. The monochromatic grays of concrete, dark brackish greens of stagnant water, and dull beige of the walls are illuminated by gray, overcast daylight, creating a flat, non-reflective sheen on the water. A heavy stillness permeates, carrying a palpable sense of unanswered questions held in the murky depths and a grim finality, all rendered with documentary photographic realism, dark-history, and a faceless style. The shallow depth of field keeps the focus sharp on the water's texture, viewed eye-level with the water's surface. The image has a 16:9 aspect ratio.

### ch07 · supp 3
- ancla: «Oficialmente, la prisión albergaba a 6,375 reclusos, pero otras fuentes estiman que hubo hasta 8,000 evacuados de la prisión.»

> An extreme wide shot captures a vast, anonymous crowd of incarcerated men, overwhelmingly African American, in orange jumpsuits, milling about a concrete recreation yard, their movements constrained by high fences topped with razor wire. No individual faces are discernible; the camera's gaze captures the sheer mass of humanity, a sea of orange within a large, secure outdoor yard of the Orleans Parish Prison, pre-storm. A basketball hoop with a torn, weathered net hangs forgotten in a corner of the yard. A field of bright institutional orange against the monolithic gray of concrete walls and steel fences is illuminated by harsh, direct midday sunlight casting sharp, dark shadows. The mood is an overwhelming sense of scale and depersonalization, visualizing the thousands of lives contained and at risk, rendered in a documentary photographic realism, dark-history, faceless style, with a deep depth of field emphasizing the scale of the crowd from a high angle, as if from a guard tower, looking down on the population. The image has a 16:9 aspect ratio.

### ch07 · supp 5
- ancla: «Según un informe de Human Rights Watch, más de 500 prisioneros no figuraban en la lista de personas evacuadas de la cárcel.»

> A close shot depicts the hands of a faceless administrative worker at a desk, holding a pen which hovers, hesitating, over a long, typed roster of names on a clipboard. The unseen person's attention is fixed on the flawed document, where many lines are blank or hastily struck through with black ink. The setting is a makeshift, dimly lit office during the post-Katrina emergency response. A prominent coffee stain blooms on the corner of the evacuation roster, blurring several names into illegibility. The color palette features stark black ink on white paper, the institutional beige of the desk, and muted 2000s office attire. A single, harsh desk lamp from the side creates deep shadows. The mood conveys bureaucratic horror, the chilling realization of human lives lost in paperwork, and a quiet but profound dread, all captured in a style of documentary photographic realism, dark-history, and facelessness. A shallow depth of field, with focus pinned on the list and the tip of the pen, is presented from a slightly high angle, looking down at the desk, hands, and document. The image has a 16:9 aspect ratio.

