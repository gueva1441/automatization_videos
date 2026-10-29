# ADENDA F53b — el respaldo es Kling 4.0, no Seedance (2026-10-29 15:00)

F53a-K: Kling 4.0 hizo las 2 fotos oscuras sin rechazo ni suavizado. Por DECISIONES 14:50, Kling a 1080p reemplaza a Seedance como respaldo. Esta adenda cambia solo eso en `HANDOFF_F53b_motor_de_clips.md` (md5 3058bd03…); todo lo demás sigue igual.

| constante | valor | origen |
|---|---|---|
| cadena | G (Gemini Omni Flash 1.1) → K (Kling 4.0) si G rechaza por contenido | DECISIONES 14:50 + F53a-K |
| K endpoint · campos | `kling/v4/image-to-video` · `start_image_url`, `prompt`, `duration` int 3–30, `resolution` 720p/1080p; sin campo de audio ni tolerancia (la pista se quita con ffmpeg `-an`) | `f52/SCHEMAS_F52.md` |
| K resolución | 1080p | DECISIONES 14:50 |
| K costo | 0,157 US$/s × 1,5 a 1080p = 0,235 US$/s (≈ 1,88 por clip de 8 s) | panel de fal 14:22: 23,95 s cobrados por 16,08 s generados en F52 |
| K ficha | `lab/hyperframes/f52/guias/K.md` (inglés) | F52b |

- Parte A: `VideoProfile` de G y K (no de S). Si S ya está escrito, se borra (no se deja apagado).
- Parte B: `video_engines = ("gemini_omni_flash", "kling_4")`; los tests de la cadena usan K como respaldo.
- DECISIONES: «2026-10-29 15:00 · **F53b adenda:** el respaldo de Gemini Omni Flash es Kling 4.0 a 1080p (F53a-K pasó la moderación sin suavizar); Seedance sale de la cadena · Omar · F53b».
