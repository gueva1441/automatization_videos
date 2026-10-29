# HANDOFF F53b — motor de clips nuevo en producción: Gemini Omni Flash, y si Google rechaza, Seedance (sale Veo)

Analista → CC · 2026-10-29 · rama `f11-guion-v4`

## Por qué
fal retira Veo 3.1 el 2026-11-17. F52 (hoja ciega): ganó Gemini Omni Flash 1.1 (G) en los dos caps. F53a: G rechazó con HTTP 422 `content_policy_violation` las 2 fotos más oscuras del canal; Seedance 2.5 (S) las hizo sin suavizar. Omar (14:43): **G primero; si G rechaza, S, automático; no se suavizan los prompts** (suavizar pierde retención).

## Antes de escribir (método)
- ¿Construye sobre algo que se reemplaza? Reemplaza Veo: se borra (no se apaga) con sus tests. Lo que NO se renombra: el concepto «cap con clip» (`veo_position`, `veo_chapters`, `_process_veo_chapter`, `VEO_CLIP_DURATION_SEC`): renombrarlo toca ~20 tests sin cambiar nada; queda en la lista de abiertos.
- ¿Cambia el orden? No: después de F53b siguen miniaturas + QA Studio y F51d-B (fotos de Wittenoom).

## Constantes
| constante | valor | origen | quién |
|---|---|---|---|
| cadena de motores | G → S (S solo si G devuelve rechazo de contenido) | DECISIONES 14:43 | Omar |
| G endpoint · campos | `google/gemini-omni-flash/v1.1/image-to-video` · `image_url`, `prompt`, `duration` int 3–10, `resolution`; sin campo de audio ni tolerancia | `lab/hyperframes/f52/SCHEMAS_F52.md` | leído de fal |
| S endpoint · campos | `bytedance/seedance-2.5/image-to-video` · `image_url`, `prompt`, `duration` string 4–30, `resolution`, `generate_audio` | ídem | leído de fal |
| resolución | 1080p los dos | G: Omar 14:24; S de respaldo: voto del analista 14:45 (solo entra en clips fuertes, que suelen ser el gancho), Omar lo cambia si quiere | Omar / analista |
| duración | 8 s | `m03_visual.VEO_CLIP_DURATION_SEC` | ya en el proyecto |
| audio | S `generate_audio` false; G no tiene campo → la pista se quita con ffmpeg (`-an`, copia de video) antes de guardar | F52 | ya decidido |
| costo G | 0,03 US$/s × 5 a 1080p = 0,15 US$/s | panel de fal 2026-10-29 14:22 (80,43 s cobrados por 16,09 s generados) | medido |
| costo S | 0,0214 US$ por 1000 tokens; tokens = ancho·alto·24·s / 1024 | panel de fal (347,4 mil tokens = los 2 clips de F52 a 720p) | medido |
| tipo de la foto | leído de los bytes (Seedream entrega JPEG con extensión .png) | F52b (HTTP 400) | medido |
| ficha de guía por modelo | `lab/hyperframes/f52/guias/{G,S}.md`, textos en inglés tal cual | F52b | Omar 13:50 |

## Módulos (5 → dos partes con PARADA en medio)
**Parte A (sin cambiar qué se genera):**
1. `engine_profiles.py` — hoy: perfiles de motor de imagen. Después: también `VideoProfile` G y S (endpoint, campos, rango de duración, resolución, campo de audio o None, ficha de guía, regla de costo). Data, sin HTTP.
2. `cost_tracker.py` — hoy: `track_fal` cobra fijo `pipeline.costs["fal_per_clip"]` (0,24, «Veo»). Después: `track_video(perfil, segundos, ancho, alto)` con la regla del perfil; `fal_per_clip` se borra de `config.py` y las estimaciones de `config.py` (l. 229, 252) usan el costo de G a 8 s.
3. `script_engine/video_prompt.py` (nuevo) — el escritor del prompt de video de F52b pasado a producción: Opus 5.5 effort high (`MODELO_CASILLEROS`), foto como bloque `image` (tipo de los bytes), pedido de F52b tal cual (`lab/hyperframes/f52/prompts_video.py` `PEDIDO`) con la ficha del perfil, `image_prompt`, ancla y el `video_prompt` del `03_visual` como «APPROVED MOTION». Devuelve texto. Se borra de `m03_visual` solo el uso de `_seedream_video_prompt` que quede sin quien lo llame en la parte B (en A no se toca).
Salida A: tests nuevos verdes; `video_prompt.py` corrido en seco sobre las 2 fotos de `f52/fotos/` para G (2 llamadas Opus, ≈ US$ 0,08): los 2 prompts pegados. **PARADA A: el analista revisa.**

**Parte B (cableado):**
4. `asset_manager.py` — hoy: `_call_veo_once` / `_generate_veo_clip` (Veo, `negative_prompt`, `VEO_DURACIONES_S`, `image/png` fijo). Después: `_generate_clip(foto, intento_movimiento, salida)` recorre la cadena: escribe el prompt con `video_prompt.py` para G, llama; si `ContentRejectedError` → escribe el prompt para S (con su ficha) y llama S; reintentos de red/429/5xx como hoy; quita audio si el perfil no tiene campo; `track_video`. Se borran `_call_veo_once`, `_generate_veo_clip`, `_veo_duration`, `VEO_DURACIONES_S`, `VEO_NEGATIVE_PROMPT` y sus tests. `qa_studio_server.py` l. 1060 apunta a `_generate_clip` (una línea).
5. `config.py` — `fal_video_model` y `fal_veo_resolution` → `video_engines = ("gemini_omni_flash", "seedance_2_5")` y `video_resolution = "1080p"`.
Log por clip: motor que lo hizo, si hubo rechazo de G (mensaje literal), segundos, costo.
Salida B:
- mapa en el reporte: quién llamaba a Veo antes y quién llama a `_generate_clip` ahora (grep), tests borrados y nuevos;
- test con fal simulado: G rechaza → S lo hace; G hace → S no se llama; red 504 → reintenta G, no salta a S;
- **1 clip real** por el camino de producción: cap 7 de Wittenoom (foto `f52/fotos/cap07.png`), G a 1080p, ≈ US$ 1,30; motor, segundos, ffprobe (1920×1080, sin audio) y costo de `cost_tracker` contra el precio de la tabla;
- suites: rápida, amplia y ch02 md5 como siempre.
**PARADA B.**

## Reglas fijas
- Sin reglas nuevas en el pedido a Opus ni en las fichas; no suavizar prompts.
- Subagentes en paralelo donde no dependan (A: 1, 2, 3 en paralelo).
- Tope de la tanda: US$ 3 (`lab/TOPE_TANDA.json`).
- Etapa 0: `DECISIONES.md` «2026-10-29 14:43 · **F53b:** motor de clips = Gemini Omni Flash 1.1 a 1080p; si Google lo rechaza por contenido, Seedance 2.5 a 1080p automático; no se suavizan los prompts; Veo se borra · Omar · F53b». md5 del handoff en el commit.
