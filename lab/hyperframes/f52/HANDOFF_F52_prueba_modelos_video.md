# HANDOFF F52 — prueba de 4 modelos de video contra los 2 clips de Wittenoom (lab, sin tocar producción)

Analista → CC · 2026-10-29 · rama `f11-guion-v4` · solo lab: `lab/hyperframes/f52/`

## Por qué
fal retira todo `fal-ai/veo3.1` (también el `lite` de `config.fal_video_model`) el 2026-11-17 y no nombra reemplazo. Omar (2026-10-29 13:24) pidió probar primero los modelos con los clips reales de Wittenoom, con un prompt por modelo escrito por Opus 5.5 según la guía oficial de cada uno, y elegir mirando. Ningún reporte público mide contenido oscuro como el del canal: esto es lo que decide.

## Antes de escribir (método)
- ¿Construye sobre algo que se va a reemplazar? No: es lab; producción (`m03_visual._seedream_video_prompt`, `asset_manager` Veo) no se toca hasta que Omar elija.
- ¿Cambia el orden? Sí, a favor: va antes de F51d-B, que ya no genera clips Veo.

## Constantes
| constante | valor | origen | quién |
|---|---|---|---|
| duración del clip | 8 s | `m03_visual.VEO_CLIP_DURATION_SEC` (l. 840) | ya en el proyecto |
| resolución | 1080p en los 4 | `config.fal_veo_resolution` | Omar (ya en config) |
| audio | apagado | `asset_manager` l. 612 `generate_audio: False` | ya en el proyecto; si un modelo no deja apagarlo, se genera y la pista se descarta |
| tomas | 1 por modelo y clip | voto del analista (comparar modelos, no suerte) | Omar confirma al pegar |
| permisividad | el valor más permisivo que acepte el schema de fal del modelo (p. ej. `safety_tolerance` de FLUX 3) | DECISIONES: el motor tiene que ser permisivo con el contenido del canal | Omar |
| tope de la tanda | US$ 16 | derivado: Kling 2 × 1,88 + Seedance 2 × 9,31… ver nota | Omar confirma |

Nota del tope: a 1080p, Seedance 2.5 sale ≈ US$ 1,164/s → 2 clips ≈ US$ 18,6. Por eso **Seedance va a 720p** (≈ 0,473/s → ≈ US$ 7,57) y se declara en la hoja; los otros 3 a 1080p: Kling 4.0 ≈ 2 × 1,88 = 3,76 · Gemini Omni Flash 1.1 ≈ 2 × 1,20 = 2,40 · FLUX 3 Max ≈ 2 × 0,58 (promo hasta 7-nov) = 1,16 · 2 fotos Seedream ≈ 0,10 · Opus ≈ 0,20 → ≈ US$ 15,2. Si el precio leído del schema/pricing de fal al correr difiere, CC lo anota y para si pasa el tope.

## Los 4 endpoints (image-to-video, foto inicial = primer cuadro)
| letra interna | modelo | endpoint fal |
|---|---|---|
| K | Kling 4.0 | `kling/v4/image-to-video` |
| S | Seedance 2.5 | `bytedance/seedance-2.5/image-to-video` |
| F | FLUX 3 Max | `blackforestlabs/flux-3-max/image-to-video` |
| G | Gemini Omni Flash 1.1 | `google/gemini-omni-flash/v1.1/image-to-video` |
CC lee el schema de cada endpoint en fal antes de llamar (nombres de campos: `image_url` / `start_image_url`, `duration`, `resolution`, audio, tolerancia) y pega en el reporte los campos usados.

## Fichas de guía (entrada para Opus, no reglas nuevas en prompts de producción)
Se guardan como `lab/hyperframes/f52/guias/{K,S,F,G}.md`, tal cual:

**K — Kling 4.0** (guía oficial de Kling, 2026-10-26): lenguaje descriptivo y concreto; pocas palabras abstractas y pocas negaciones (aumentan errores); las únicas negaciones necesarias: sin subtítulos y sin música de fondo. Estructura: [Ajustes generales] escena y textura, estilo visual, tono de cámara · [Secuencia] 0–X s / X–Y s / Y s–final con acción y movimiento de cámara · [Audio]. En imagen a video: sujeto + movimiento, fondo + movimiento.

**S — Seedance 2.5** (guía de BytePlus vía resúmenes): en imagen a video escribir solo lo que se mueve, construir sobre la foto sin re-describirla; claridad y cero contradicciones valen más que encabezados; rangos de tiempo contiguos (0–3 s, 3–6 s…) guían el orden; si el prompt describe otra escena, el modelo puede cortar: decir que es una sola toma continua.

**F — FLUX 3 Max** (Black Forest Labs / fal): dirigir la escena, no inventariar objetos; sustantivos y verbos concretos; sobrecargar el prompt vuelve el movimiento menos coherente; una oración en orden cámara → sujeto → acción → entorno → movimiento secundario y look; en imagen a video decir qué se queda igual de la foto (encuadre, luz); cerrar con «no on-screen text, no subtitles».

**G — Gemini Omni Flash 1.1** (Google vía fal): sujeto, acción, movimiento de cámara, look y sonido, escritos como indicaciones a un equipo de rodaje; movimientos de cámara con su nombre de cine; es menos prescriptivo que Veo: prompts cortos y enfocados rinden más que largos; en imagen a video nombrar lo que de la foto tiene que sobrevivir; cerrar con «no captions».

## Etapas (paralelo al máximo: subagentes y llamadas fal en paralelo donde no dependan)

### Etapa 0
`DECISIONES.md`: «2026-10-29 13:24 · **F52:** prueba en lab de 4 modelos de video (Kling 4.0, Seedance 2.5, FLUX 3 Max, Gemini Omni Flash 1.1) sobre los clips de los caps 1 y 7 de Wittenoom; un prompt por modelo escrito por Opus 5.5 con la ficha de guía de cada modelo; 8 s, 1080p (Seedance 720p por costo), sin audio, 1 toma; hoja ciega; elige Omar; producción no se toca · Omar · F52». md5 del handoff en el commit.

### Etapa 1 — fotos iniciales (≈ US$ 0,10)
Las 2 fotos de arranque de los clips (cap 1 y cap 7, `veo_position` start/end) con el prompt vivo del `03_visual.json` de Wittenoom (md5 `0d57b6ba…`), con el mismo motor y armado de producción (Seedream). Salida: `f52/fotos/cap01.png`, `cap07.png` y los 2 prompts pegados en el reporte.

### Etapa 2 — 8 prompts en texto (≈ US$ 0,20) → PARADA
Script `f52/prompts_video.py`: por modelo y clip, una llamada a Opus 5.5 (effort high, como `m03:casilleros`) con: la ficha de guía del modelo + la misma entrada que hoy usa `m03_visual._seedream_video_prompt` (prompt de la foto, oración ancla de la voz, etiqueta) + el `video_prompt` vivo del `03_visual` como referencia del movimiento ya aprobado. Pedido a Opus (completo, no se ajusta):

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
Salida: `f52/PROMPTS_F52.md` con los 8 prompts enteros, palabra por conteo, y la ficha usada. **PARADA: el analista revisa los 8 en texto antes de gastar en clips.**

### Etapa 3 — 8 clips (≈ US$ 15) — solo con «sigue» del analista/Omar
- 8 llamadas en paralelo. Por clip: endpoint, campos usados, duración y resolución reales (ffprobe), tiempo de espera, costo leído, y si rechazó o moderó (mensaje literal; si cobró el rechazo).
- **Hoja ciega:** por cap, un mp4 lado a lado 2×2 con etiquetas 1–4 en orden aleatorio, y una hoja de contactos (cuadros a 0, 2, 4, 6, 8 s). La llave (número → modelo) va en `f52/LLAVE.md`, aparte. Skill `ver-render` para las medidas.
- Salida: `f52/F52_REPORT.md` con la tabla por clip y lo abierto. **PARADA: Omar mira la hoja ciega y elige.**

## Módulos
- Producción: ninguno. `config.py`, `asset_manager.py`, `m03_visual.py`, `m03_imagenes_v3.py` no se tocan.
- Nuevos, en lab: `f52/prompts_video.py` (pedido a Opus por modelo), `f52/prueba_video.py` (llamadas fal y hoja ciega), `f52/guias/*.md`.

## Después (no en esta tanda)
Con el ganador: su ficha de guía pasa al perfil del motor (`engine_profiles.py`), duraciones del perfil (hoy `asset_manager.VEO_DURACIONES_S` fija 4/6/8), y se borra lo de Veo con sus tests.
