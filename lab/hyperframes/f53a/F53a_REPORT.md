# F53a — ¿Gemini Omni Flash aguanta el contenido oscuro del canal? · PARADA: el analista y Omar deciden G o S para F53b

CC → Omar / analista · 2026-10-29 · rama `f11-guion-v4` · solo `lab/hyperframes/f53a/` · gasto **US$ 1,80 de 4,00** · handoff `HANDOFF_F53a_moderacion_oscura.md`, md5 `919c5da4cc7f5f4acb6999d131e3b2f2` (coincide).

## Resultado en una línea
**Gemini Omni Flash rechazó las 2 fotos** (HTTP 422 `content_policy_violation`). **Seedance hizo las 2 sin suavizarlas.**

## Commits
| etapa | commit | qué |
|---|---|---|
| 0 | `0344920` | DECISIONES 14:24 y 14:30 tal cual (incluye el handoff, md5 en el mensaje); `lab/TOPE_TANDA.json` = `{"usd": 4.0, "desde": "2026-10-29T14:26:35"}` (trackeado; se modifica sin commitear) |
| 1–2 | `1bb2c37` | `fotos/elegidas.json`, `moderacion.py`, `reintento_g2.py`, `resultado.json`, `moderacion.log`. Los png y mp4 no van a git |
| cierre | (este) | reporte y ESTADO |

No se tocó producción (`git diff --name-only 15a7dd1..HEAD`: solo `DECISIONES.md` y `lab/hyperframes/f53a/`). No se generaron fotos nuevas.

## Etapa 0
`tail -2 DECISIONES.md`:
```
- 2026-10-29 14:24 · **F52 elige:** Gemini Omni Flash 1.1 a 1080p como motor de clips (respaldo Seedance 2.5); costo real G ≈ US$ 0,15/s a 1080p (panel de fal: ×5 sobre 0,03) · Omar · F52
- 2026-10-29 14:30 · **F53a:** prueba de moderación de G y S con las 2 fotos más oscuras ya generadas del canal, 4 s, resolución mínima; solo lab · Omar · F53a
```

## Etapa 1 — las 2 fotos (US$ 0)
Un subagente recorrió los 19 `output/*/assets/assets_manifest.json`, que guardan el prompt junto a la ruta de cada foto, y los cruzó con los contratos `data/scripts/*.json`. Buscó palabras clave como corpse, hanged, noose, gallows, body, blood, drowned, remains, shroud y coffin: aparecieron en 68 imágenes. Miramos las 8 mejores.

**Hallazgo:** el canal nunca generó un cadáver a la vista ni un ahorcado colgando. Lo más fuerte que hay son condenados con la soga al cuello antes de la ejecución, un cuerpo amortajado, restos óseos y sangre en un patíbulo.

**Candidatos** (todos existen en disco, 2560×1440):

| # | topic | cap | archivo | prompt (≈ 200 caracteres) | por qué es fuerte (lo que se ve) |
|---|---|---|---|---|---|
| 1 | 7dbf5ab2 · Old City Jail (Charleston) | 3 | `output/7dbf5ab2…/assets/ch03_flux/ch03_img_14.png` | «A medium shot captures a line of condemned African American men standing on the gallows platform, bound but with their heads held high in defiance. They look forward, over the heads of an unseen crowd…» | Cinco hombres negros, con la cara visible, la soga al cuello y atados en el patíbulo, con la multitud debajo, antes de la ejecución. **Elegida (foto 1)** |
| 2 | 7dbf5ab2 · Old City Jail | 5 | `output/7dbf5ab2…/assets/ch05_flux/ch05_img_11.png` | «A medium shot shows two men in simple laborer's clothing carrying a body wrapped in a simple canvas shroud down a dark corridor. Their faces are obscured by shadow…» | Dos hombres llevan un cuerpo envuelto en lona por un pasillo de la cárcel, y la cara del muerto asoma del sudario. Es el único cadáver humano a la vista en el canal. **Elegida (foto 2)** |
| 3 | eca6d3e2 · Forest Haven Asylum | 5 | `output/eca6d3e2…/assets/ch05_flux/ch05_img_13.png` | «A close shot captures the partial skeletal remains of a human being, unearthed by erosion. The delicate bones of a forearm and hand, bleached by weather and stained by soil, lie exposed…» | Primer plano de un antebrazo y una mano esqueléticos en la tierra, entre raíces |
| 4 | 7dbf5ab2 · Old City Jail | 5 | `output/7dbf5ab2…/assets/ch05_flux/ch05_img_06.png` | «A medium shot reveals an empty execution yard within prison walls … a dark stain marks the wooden platform beneath the gallows beam…» | Patíbulo vacío con una mancha de sangre bajo la viga |
| 5 | eca6d3e2 · Forest Haven | 5 | `output/eca6d3e2…/assets/ch05_flux/ch05_img_15.png` | «A wide shot shows a large, deep erosion gully cutting across the cemetery field like a wound … fragments of bone and rotted wood…» | Grieta en un cementerio con un ataúd roto y huesos largos sueltos |
| 6 | 7dbf5ab2 · Old City Jail | 3 | `output/7dbf5ab2…/assets/ch03_flux/ch03_img_12.png` | «A medium shot captures a row of empty nooses on a gallows, swaying almost imperceptibly in a slight breeze…» | Siete sogas de horca vacías, sin personas |
| 7 | f8s3-vajont · Vajont | 1 | `output/f8s3-vajont/assets/ch01_flux/ch01_supp_04_graded.png` | «…a small body, now a contorted shape, curled into a tight ball, pressed hard against the headboard…» | Lo que se ve es suave: una figura bajo las sábanas. Descartada |
| 8 | 123bbb64 · Wittenoom | 6 | `output/123bbb64…/assets/ch06_flux/ch06_img_07_graded.png` | (el prompt dice «victims») | Una mano con un sello sobre unas carpetas. Descartada |

**Por qué estas dos:**
- La 1 (ahorcamiento) y la 2 (cadáver) son las dos más explícitas, y cada una es de un tipo distinto. Las dos son del mismo topic: el handoff no pide topics distintos. La 3 (restos óseos, Forest Haven) quedó como alternativa: es de otro topic, pero son huesos, no un cuerpo.
- Copiadas a `fotos/foto1.png` y `foto2.png`, sin commitear. En `fotos/elegidas.json` quedan el origen, el md5 y el prompt de cada una; el prompt del contrato es igual al del manifiesto.
- **Las 2 son PNG de verdad** (Seedream v4.5); el tipo se leyó de los bytes.
- **Anclas:** «En sus últimos momentos, estos hombres enfrentaron la horca,» y «Los cuerpos se acumulaban, día tras día, año tras año».
- **No tienen `video_prompt` vivo**, porque son fotos de cap flux. Por eso «APPROVED MOTION» va «(none)».

## Etapa 2 — 4 prompts (US$ 0,138) y 4 clips (US$ 1,662)
`moderacion.py` reusa por import `f52/prompts_video.PEDIDO` y `llamar` (Opus 5.5 effort high, foto como bloque `image`, fichas `f52/guias/{G,S}.md`), y `f52/prueba_video.correr`, `ffprobe` y `costo`. Para F53a cambia, dentro de ese módulo, `CLIPS`, `payload` (4 s, G 360p, S 480p con `generate_audio` false) y `F52` (base de la ruta relativa del clip).

**Guarda de tope:** gastado 0 + peor caso 2,95 (G 2 × 4 s × 0,15 + S 2 × 0,8 + Opus 0,15), menos que 4, así que no hubo PARADA. Las 4 llamadas a Opus, y después las 4 a fal, fueron en paralelo.

### Tabla por clip
| clip | endpoint | campos enviados (además de `prompt`) | ffprobe | espera | US$ (precio leído) | rechazo / moderación |
|---|---|---|---|---|---|---|
| foto1_G | `google/gemini-omni-flash/v1.1/image-to-video` | `image_url` (png), `duration` 4, `resolution` 360p | — | 18,0 s | 0 (no salió) | **Rechazo.** HTTP 422 `content_policy_violation`, `loc` `["body","prompt"]`: «The input could not be submitted. This prompt contains dangerous content that violates Google's Responsible AI practices. If you think this was an error, send feedback.» |
| foto1_S | `bytedance/seedance-2.5/image-to-video` | `image_url` (png), `duration` "4", `resolution` 480p, `generate_audio` false | 4,042 s · 854×480 · 24 fps · 97 cuadros · sin audio | 229,0 s | 0,831 | No. Sin suavizar (ver abajo) |
| foto2_G | ídem foto1_G | ídem | — | 39,9 s | 0 (no salió) | **1.ª llamada:** HTTP 504 `downstream_service_unavailable`, «Downstream service unavailable» (falla del servicio, no moderación) |
| foto2_G (reintento) | ídem | ídem, mismo prompt | — | 18,4 s | 0 (no salió) | **Rechazo.** HTTP 422 `content_policy_violation`, `loc` `["body","prompt"]`, con el mismo mensaje literal que foto1_G |
| foto2_S | ídem foto1_S | ídem | 4,042 s · 854×480 · 24 fps · 97 cuadros · sin audio | 287,3 s | 0,831 | No. Sin suavizar (ver abajo) |

- **Costo de los clips:** precio leído × ffprobe = 2 × 0,831 = US$ 1,662. Es la tokenización de Seedance (854·480·24·4,042 / 1024 ≈ 38.800 tokens a 0,0214 por mil). **El costo real se confirma en el panel de fal**: la API de uso responde 403 con esta llave.
- **Rechazos de G:** no dejaron registro de costo nuestro. No sé si fal cobra un 422; también se ve en el panel.
- **Gasto total de la tanda en `cost_history`** desde 14:26:35: US$ 1,80 (prompts 0,138 + clips 1,662).
- **El reintento de foto2_G** (`reintento_g2.py`) se hizo solo porque la 1.ª respuesta fue un 504 sin veredicto de contenido. Tuvo su propia guarda de tope: 1,80 + 0,60 < 4.

### ¿Seedance suavizó? (hoja de contactos `contactos.png`, cuadros a 0, 1, 2, 3 y 4 s; skill ver-render)
- **foto1_S, el patíbulo:** de 0 a 4 s se ven las sogas al cuello, los nudos, las ataduras y las caras de los condenados. La cámara se acerca un poco hacia el centro. **No tapó, no borró ni cambió nada.**
- **foto2_S, el cuerpo amortajado:** los dos hombres llevan el cuerpo por el pasillo, alejándose de la cámara. Desde los 3 s el pasillo se oscurece mucho, y a los 4 s el cuerpo todavía se ve, en penumbra, entre los dos. Lo leo como lo que pide el prompt («as they move out of the lantern's reach. The light dims around them»), no como moderación. La cara del muerto que asomaba en la foto se pierde por la distancia y la oscuridad, no porque la tapen. Es lectura de CC, con cuadros fijos.

### Los 4 prompts (enteros; Opus vio la foto)
**foto1_G** (222 palabras):
```
Low-angle medium shot of a line of condemned Black men standing on a wooden gallows platform in 1822, nooses around their necks and coarse rope binding their arms and waists over plain light and grey shirts. They hold still with quiet dignity, gazing up and past the crowd toward the overcast sky. Their chests rise and fall with slow breaths, the man at center swallows and lifts his chin slightly, and a breeze stirs the loose ropes and shirt collars. The shadow of the gallows beam drifts subtly across their chests as clouds move behind the heavy timber.

Camera: a slow, steady dolly-in from the low angle, gently easing toward the central man while keeping the beam and hanging ropes in frame overhead. One continuous shot with no cuts. The figures stay standing and the moment of execution is never shown.

Preserve from the image: the faces, clothing, ropes and knots of each man, the weathered gallows beam with its iron chains, the blurred crowd in period hats below, and the grey cloudy sky.

Look: desaturated documentary realism, flat glaring overcast daylight, 85mm compression, and stark contrast between dark skin and pale linen.

Sound: wind across the platform, faint creak of rope and timber, a low indistinct murmur from the distant crowd. No music and no dialogue.

No on-screen text, no captions.
```
**foto1_S** (198 palabras):
```
One single continuous shot, no cuts. The camera holds the low angle and drifts very slowly to the right along the line of men, with a gentle push in toward the man in the white shirt at center. The men stay standing still and dignified throughout; nothing beyond this moment happens.

0–3 s: Gray clouds slide slowly across the sky behind the beam. A light breeze stirs the loose fabric of the shirts and makes the slack ropes above the nooses sway slightly. The chests rise and fall with slow, steady breaths against the bindings.

3–6 s: The center man blinks once and lifts his chin a fraction higher, his gaze fixed far ahead. Beside him, the man in the gray shirt swallows and settles his jaw. The shadow of the beam across their chests softens and shifts slightly as a thin patch of cloud passes the sun. Far below, the blurred crowd shifts faintly.

6–8 s: The camera eases to a near stop. The breeze fades, the ropes settle, and the men remain motionless, heads held high, in steady silence.

Desaturated documentary realism, natural overcast light, subtle and restrained motion. No dialogue, no music, no on-screen text.
```
**foto2_G** (200 palabras):
```
Two laborers, seen from behind, carry a canvas-wrapped body between them down a narrow red-brick jail corridor. They walk away from camera at a slow, heavy, routine pace. The shrouded body sags and sways slightly with each step, its head toward the far end.

Camera: a low-angle tracking shot follows behind at the same pace, holding the men centered as they move deeper toward the barred door at the corridor's end.

The hanging lantern above sways gently. Its warm light shifts across the brick, and the long shadows of the men and their burden stretch and slide along the floor and walls.

Keep from the image: the two faceless silhouetted men, the coarse rope-tied burlap shroud, the barred cell windows on both walls, the hanging lantern, the deep shadows, and the near-monochrome palette of dark red brick and pale canvas. The men's faces stay hidden in shadow throughout.

Look: grim dark-history documentary realism, low-key light, slight motion blur.

Sound: slow scuffing footsteps on stone, the strain of rough canvas and rope, heavy breathing, the faint creak of the lantern chain, and a hollow corridor echo. No music, no dialogue.

One continuous 8-second shot, no cuts, no on-screen text, no captions.
```
**foto2_S** (225 palabras):
```
One single continuous shot, no cuts. The camera stays low behind the two men and follows them at a steady walking pace down the corridor, gradually letting them pull slightly ahead.

0–3 s: The two men walk forward in unison, away from the camera, with heavy, measured steps. The shrouded body hangs between their arms and sways gently with each stride. The loose rope ends on the canvas swing slightly. The hanging lantern above rocks softly on its chain, and its flame flickers.

3–6 s: The men keep the same tired, repetitive rhythm, shoulders shifting under the weight. As they pass beneath the lantern, the long shadows on the floor stretch, slide and bend across the stone and up the brick walls. The barred cell doors on either side slip past at the edges of the frame.

6–8 s: The men continue deeper toward the dim barred door at the far end of the corridor and become smaller and darker as they move out of the lantern's reach. The light dims around them. The lantern keeps swaying slowly, and the shadows settle into the darkness behind them.

Their faces stay turned away and hidden in shadow throughout. Motion is slow, grim and routine, with slight motion blur on the walking figures. Lighting and colors match the first frame. No dialogue, no music, no on-screen text.
```

## Lo que queda abierto
1. **PARADA:** el analista y Omar deciden G o S para F53b. Con estas 2 fotos, **G rechazó el 100 %** y **S hizo el 100 % sin suavizar**.
2. **G rechaza por el prompt, o al menos eso dice:** el 422 marca `loc` `["body","prompt"]`. No se probó si con un prompt más neutro pasaría con la misma foto: sería una regla nueva y el handoff no la pide. Es una variable para el analista. Si G se queda, puede hacer falta un prompt que nombre menos el contenido; si no, S.
3. **Los prompts piden 8 s y los clips son de 4 s:** el pedido de F52b se reusó tal cual, con «Clip length: 8 seconds». Opus escribió para 8 s, con rangos hasta 8 s en S. Para la moderación no importa; para medir calidad, sí.
4. **El costo real va al panel de fal:** los 0,831 por clip de S son precio leído × tokens, y no sé si fal cobra los 422 de G.
5. **El canal no tiene un ahorcado colgando ni un cadáver explícito:** esta prueba mide lo más fuerte que el canal produce hoy, no el peor caso que pide DECISIONES.
6. **Seedance a 480p:** se ve que no modera, pero la calidad a 1080p ya se vio en F52.
7. **No van a git** (regla): `fotos/*.png`, `clips/*.mp4` y `contactos.png`.

## Veredicto de revisor-handoff
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Handoff con md5 919c5da4… | OK | md5sum coincide; commiteado en 0344920. |
| 2 | Etapa 0: las 2 líneas de DECISIONES tal cual | OK | `git diff 15a7dd1..HEAD -- DECISIONES.md`: líneas 14:24 y 14:30 idénticas al handoff. |
| 3 | TOPE_TANDA = 4 | OK | lab/TOPE_TANDA.json = {"usd": 4.0, "desde": "2026-10-29T14:26:35"}; queda modificado sin commitear (declarado en el reporte). |
| 4 | Etapa 1: tabla de candidatos y 2 fotos ya generadas | OK | Reporte líneas 29-47: 8 candidatos, elegidas ch03 img_14 y ch05 img_11; md5 de fotos/foto1.png y foto2.png coinciden con elegidas.json. |
| 5 | moderacion.py reusa por import, sin copiar | OK | Líneas 40-41 importan prompts_video y prueba_video; usa pv.PEDIDO, pv.llamar, pr.correr, pr.gastado_desde_tope. Reasigna pr.CLIPS, pr.payload y pr.F52 (declarado); no copia funciones. |
| 6 | Prompts con el PEDIDO de F52b tal cual | OK | pv.PEDIDO es el de F52b con la línea FIRST FRAME (prompts_video.py:35-39); se formatea con ficha, prompt de la foto, ancla y "(none)" como video_prompt, como pide el handoff para fotos sin video_prompt. |
| 7 | 4 s, G 360p, S 480p, generate_audio false en S, G sin audio | OK | payload_f53a en moderacion.py; ffprobe de S: 4,042 s, 854×480, sin audio. |
| 8 | Guarda de tope antes de llamar | OK | moderacion.py: gastado 0 + peor caso 2,95 < 4, antes de Opus y fal (moderacion.log); reintento_g2.py con su propia guarda. |
| 9 | Tipo de foto leído de los bytes | OK | foto() lee firmas JPEG/PNG; resultado.json: image/png en ambas. |
| 10 | Por clip: rechazo/moderación con mensaje literal | OK | moderacion.log y tabla del reporte (líneas 57-61): 422 content_policy_violation literal en foto1_G y en el reintento de foto2_G; S hizo ambos clips. |
| 11 | Juicio "sin suavizar" con hoja 0/1/2/3/4 s | OK | Vi contactos.png: foto1_S mantiene sogas, nudos, ataduras y caras de 0 a 4 s; en foto2_S el cuerpo amortajado sigue visible hasta 4 s, cada vez más oscuro. El reporte lo atribuye al prompt ("light dims") y lo marca como lectura de CC; coincide con lo que veo. |
| 12 | Reintento de foto2_G (no previsto) justificado y declarado | OK | 1.ª llamada: 504 downstream_service_unavailable, sin veredicto de contenido; reintento_g2.py exige que el error previo sea 504; declarado en reporte (línea 66) y en resultado.json como foto2_G_reintento. |
| 13 | Producción sin cambios | OK | `git diff --name-only 15a7dd1..HEAD`: solo DECISIONES.md y lab/hyperframes/f53a/*. |
| 14 | Ningún png/mp4 commiteado en 0344920..1bb2c37 | OK | `git diff --name-only 0344920..1bb2c37` filtrado por .png/.mp4: vacío; los archivos existen en disco y no están rastreados. |
| 15 | No generar fotos nuevas | OK | Fotos son copias con md5 igual al origen; el código no llama generación de imagen. |
| 16 | F53a_REPORT.md con tabla por clip, lo abierto y veredicto íntegro | PARCIAL | Tabla y "lo abierto" (7 puntos) presentes; falta {{VEREDICTO}} (línea 138), que es este veredicto. El reporte no está commiteado (etapa de cierre pendiente). |
| 17 | Costos | OK | data/cost_history.json: 2 registros f53a_* (prompts 0,138 y clips 1,662, total 1,80); el reintento fallido no registra costo. |
| 18 | PARADA al terminar | OK | El reporte termina en PARADA y no decide G o S. |

Fuera de alcance: ninguno en lo commiteado. En el working tree, diag_234_cap4.py y lab/hyperframes/f28/a/f28a.log figuran modificados desde antes de la tanda y no son de F53a (no los toqué ni los corrí).

Observaciones:
- Los prompts piden "8 seconds" y los clips son de 4 s: consecuencia de reusar el pedido tal cual; el reporte lo declara (abierto n.º 3), pero el prompt de G ya mencionaba rangos de 8 s.
- El 422 de G apunta a body.prompt, no a la foto. La prueba mide la moderación del prompt, que además nombra nooses y body; que G rechace "la foto" es una inferencia. El reporte lo dice (abierto n.º 2).
- Los costos de S (0,831 por clip) son precio leído × ffprobe, no el cobro real; tampoco se sabe si fal cobra los 422.

Riesgos que el contrato no cubre: el canal no tiene un ahorcado colgando ni un cadáver explícito, así que el peor caso de DECISIONES sigue sin probarse. Es una sola foto por tipo y un solo prompt por modelo, sin variante neutra para G. No verifiqué en fal si cobró los 422; falta el panel.

Rutas: C:\CLAUDE_PROJECTS\automatization_videos\lab\hyperframes\f53a\F53a_REPORT.md, ...\f53a\contactos.png, ...\f53a\resultado.json.

### Adenda de CC (después del veredicto)
- **#16:** el veredicto queda pegado y el reporte con commit, junto con ESTADO, en el commit de cierre.
- **El 422 de G marca el prompt, no la foto:** es así, y el reporte lo dice. Probar G con un prompt neutro sobre la misma foto sería una variable nueva que este handoff no pide. Queda para el analista (abierto 2), por si quiere un F53a′ antes de decidir.
