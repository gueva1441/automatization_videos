# HANDOFF F52b — rehacer los 8 prompts de video: fichas en inglés y Opus mira la foto (lab, sin tocar producción)

Analista → CC · 2026-10-29 · rama `f11-guion-v4` · solo `lab/hyperframes/f52/`

## Por qué (dos fallas de F52 etapa 2, causa raíz)
1. **Kling salió en castellano.** Causa: el analista escribió las 4 fichas en castellano; Opus siguió la de K al pie («[Ajustes generales]»). Las otras 3 salieron en inglés por azar. La prueba tiene que variar solo el modelo de video, no el idioma. Arreglo general: las 4 fichas en inglés (mismo contenido, traducido).
2. **Los 8 prompts contradicen la foto.** La foto del cap 1 salió de cuerpo entero con el pie vendado levantado; los 8 dicen «start on the medium shot». Causa: Opus escribe el movimiento leyendo el `image_prompt`, no la foto que de verdad salió. Seedance avisa que una contradicción con el primer cuadro puede causar cortes. Arreglo general: Opus recibe la foto real (visión) y, si difiere del texto, manda la foto.

## Antes de escribir (método)
- ¿Construye sobre algo que se va a reemplazar? No: lab. Si mirar la foto mejora los prompts, pasa a producción en la tanda del ganador (el prompt de video se escribiría con la foto ya generada).
- ¿Cambia el orden? No: sigue siendo la PARADA antes de los clips.

## Constantes
Ninguna nueva. Opus 5.5 effort high, 8 llamadas, fotos `fotos/cap01.png` y `cap07.png` sin regenerar (las 4 versiones de cada cap parten del mismo cuadro: comparación justa). Tope US$ 16 sigue.

## Módulos
- `lab/hyperframes/f52/guias/{K,S,F,G}.md`: hoy en castellano → en inglés (texto abajo, tal cual).
- `lab/hyperframes/f52/prompts_video.py`: hoy manda solo texto → manda la foto del cap como bloque de imagen + el pedido nuevo. Producción: ninguno.

## Etapa 0
`DECISIONES.md`: «2026-10-29 13:50 · **F52b:** fichas de guía de video en inglés y Opus escribe el prompt de video mirando la foto real (si difiere del image_prompt, manda la foto); solo lab · Omar · F52b». md5 del handoff en el commit. Guardar los 8 prompts de etapa 2 como `prompts_f52_v1.json` (no se borran: sirven para comparar).

## Etapa 1 — fichas en inglés (reemplazar el texto, tal cual)
**K.md**
**K — Kling 4.0** (official Kling guide, 2026-10-26): descriptive, concrete language; few abstract words and few negations (they increase errors); the only negations needed: no subtitles and no background music. Structure: [General settings] scene and texture, visual style, camera tone · [Sequence] 0–X s / X–Y s / Y s–end with action and camera movement · [Audio]. In image-to-video: subject + motion, background + motion.

**S.md**
**S — Seedance 2.5** (BytePlus guide via summaries): in image-to-video write only what moves, build on the image without re-describing it; clarity and zero contradictions matter more than headers; contiguous time ranges (0–3 s, 3–6 s…) guide the order; if the prompt describes a different scene the model may cut: say it is one single continuous shot.

**F.md**
**F — FLUX 3 Max** (Black Forest Labs / fal): direct the scene, don't inventory objects; concrete nouns and verbs; overloading the prompt makes motion less coherent; one sentence in the order camera → subject → action → setting → secondary motion and look; in image-to-video say what stays the same from the image (framing, light); close with "no on-screen text, no subtitles".

**G.md**
**G — Gemini Omni Flash 1.1** (Google via fal): subject, action, camera movement, look and sound, written as directions to a film crew; camera moves by their film name; less prescriptive than Veo: short focused prompts work better than long ones; in image-to-video name what from the image must survive; close with "no captions".

## Etapa 2 — 8 prompts con la foto (≈ US$ 0,15) → PARADA
Cada llamada lleva primero la foto del cap (`fotos/capNN.png`, base64, bloque `image`) y después este pedido (completo, no se ajusta; cambia solo la línea FIRST FRAME respecto de F52):
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
Si `claude_helpers._post` no acepta bloques de imagen, armar el `body` con `content` en lista (imagen + texto) en el script de lab, sin tocar `claude_helpers`.

Salida: `PROMPTS_F52.md` regenerado con los 8 nuevos, y al lado de cada uno el de F52 (v1), palabras de los dos, y una línea de CC por prompt: ¿nombra el encuadre real (cap 1: cuerpo entero, pie levantado)? ¿en inglés? Commit + reporte corto `F52b_REPORT.md` con lo abierto y el veredicto íntegro de `revisor-handoff`. **PARADA: el analista revisa los 8; la etapa 3 (clips) sigue sin correr hasta el «sigue» de Omar.**

## Reglas fijas
- No tocar producción ni regenerar fotos. Llamadas en paralelo (subagentes donde ayude).
- Sin reglas nuevas en el pedido fuera de la línea FIRST FRAME.
