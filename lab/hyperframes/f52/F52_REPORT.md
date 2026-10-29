# F52 — prueba en lab de 4 modelos de video: etapas 0–2 (fotos y prompts en texto) · PARADA antes de los clips

CC → Omar / analista · 2026-10-29 · rama `f11-guion-v4` · solo lab (`lab/hyperframes/f52/`) · gasto **US$ 0,1906 de 16,00** · handoff `HANDOFF_F52_prueba_modelos_video.md`, md5 `aa964d1f8c107a2e6bd746295129e09f` (coincide).

## Commits
| etapa | commit | qué |
|---|---|---|
| 0 | `35804d2` | DECISIONES 13:24 tal cual (incluye el handoff, md5 en el mensaje) |
| 1 | `8347f5e` | schemas y precios leídos de fal (`schemas_f52.py`, `SCHEMAS_F52.md`, `schemas/`) + las 2 fotos (`fotos_f52.py`, `fotos/`) |
| 2 | `7b8d838` | fichas (`guias/`), `prompts_video.py`, `PROMPTS_F52.md`, `prompts_f52.json` |
| cierre | (este) | reporte y ESTADO |

Producción no se tocó: `config.py`, `asset_manager.py`, `m03_visual.py` y `m03_imagenes_v3.py` sin cambios (`git diff --name-only a365708..HEAD`: solo `DECISIONES.md` y `lab/hyperframes/f52/`).

## Etapa 0
`tail -1 DECISIONES.md`:
```
- 2026-10-29 13:24 · **F52:** prueba en lab de 4 modelos de video (Kling 4.0, Seedance 2.5, FLUX 3 Max, Gemini Omni Flash 1.1) sobre los clips de los caps 1 y 7 de Wittenoom; un prompt por modelo escrito por Opus 5.5 con la ficha de guía de cada modelo; 8 s, 1080p (Seedance 720p por costo), sin audio, 1 toma; hoja ciega; elige Omar; producción no se toca · Omar · F52
```
`lab/TOPE_TANDA.json` = `{"usd": 16.0, "desde": "2026-10-29T13:29:18"}` (archivo trackeado; por regla de la cadena se modifica y no se commitea).

## Schemas y precios leídos de fal antes de llamar
`schemas_f52.py` hace solo GET, sin generar nada: lee el OpenAPI de `fal.ai/api/openapi/queue/openapi.json?endpoint_id=…` y el precio de `api.fal.ai/v1/models/pricing?endpoint_id=…`. Las tablas completas, con descripción de cada campo, están en `SCHEMAS_F52.md`, y los OpenAPI crudos en `schemas/`.

**Campos que se van a usar en la etapa 3** (8 s, 1080p salvo Seedance 720p, sin audio, sin tolerancia):

| letra | endpoint | foto | prompt | duración | resolución | audio | tolerancia | precio leído |
|---|---|---|---|---|---|---|---|---|
| K | `kling/v4/image-to-video` | `start_image_url` (req) | `prompt` | `duration` int 3–30 → `8` | `resolution` 720p/1080p → `1080p` (default) | **sin campo** | **sin campo** | 0,157 US$/s |
| S | `bytedance/seedance-2.5/image-to-video` | `image_url` (req) | `prompt` | `duration` string `auto`/4–30 → `"8"` | `resolution` 480p/720p/1080p → `720p` (default) | `generate_audio` (default true) → `false` | **sin campo** | 0,0214 US$/1000 tokens |
| F | `blackforestlabs/flux-3-max/image-to-video` | `image_url` (req) | `prompt` (req) | `duration` int 5–20 → `8` | `resolution` 720p/1080p → `1080p` (default 720p) | `generate_audio` (default true) → `false` | **sin campo** | 0,02125 US$/s |
| G | `google/gemini-omni-flash/v1.1/image-to-video` | `image_url` (req) | `prompt` (req) | `duration` int 3–10 → `8` (default) | `resolution` 360p/720p/1080p/4k → `1080p` (default 720p) | **sin campo** | **sin campo** | 0,03 US$/s |
| foto | `fal-ai/bytedance/seedream/v5/lite/text-to-image` (etapa 1, por producción: `prompt`, `image_size` 2560×1440, `num_images` 1, `enable_safety_checker` true) | — | — | — | — | — | — | 0,035 US$/imagen |

Campos que existen y no se usan:
- K: `multi_prompt`, `middle_image_urls`, `end_image_url`;
- S: `aspect_ratio` (siempre «auto» en i2v), `codec`, `end_user_id`, `end_image_url`, `draft`, `bitrate_mode`;
- F: `end_image_url`, `aspect_ratio` (default `auto`, sigue a la foto), `seed`, `reasoning_level` (default `high`);
- G: `aspect_ratio` (default 16:9), `end_image_url`.

**Lo que el schema no deja hacer como pide el handoff:**
- **Tolerancia:** ninguno de los 4 tiene un campo de tolerancia o de safety, así que se mandan sin ese campo.
- **Audio:** K y G no tienen campo de audio. Si generan pista, se descarta, como prevé el handoff.

**Tope.** La API de precios no dice a qué resolución corresponde el precio unitario: puede haber un multiplicador por resolución que no se lee ahí. La página de cada modelo se arma con JavaScript y no trae el precio en texto.
- **Con los precios leídos**, los 8 clips cuestan ≈ **US$ 10,7**: K 2 × 1,256 + S 2 × 3,70 (720p: 1280·720·24·8 / 1024 ≈ 172.800 tokens) + F 2 × 0,17 + G 2 × 0,24.
- **Con la estimación del handoff** (K 1,88, S 3,79, F 0,58 y G 1,20 por clip), los 8 suman ≈ US$ 14,9.
- **En los dos casos**, con lo ya gastado (0,19), la tanda queda bajo US$ 16, así que no hay PARADA por precio.
- El costo real de cada clip se anota en la etapa 3.

## Etapa 1 — fotos de arranque (US$ 0,07)
`fotos_f52.py` usa el mismo camino de producción: `asset_manager._generate_flux_image_at(image_prompt, art_profile, path, use_ultra=False)`. Con el validador de visión apagado, eso es una sola llamada a `_generate_image_raw`, que va a Seedream v5 lite en t2i, porque ninguna de las 2 fotos tiene `foto_madre_ref`. Lee el `03_visual.json` de F51f (md5 `0d57b6ba…`, comprobado antes de llamar). Solo importa módulos de producción, no los modifica.

| foto | `veo_position` | archivo | tamaño | seed | ms | nsfw |
|---|---|---|---|---|---|---|
| cap 1 | start | `fotos/cap01.png` | 2560×1440 | 955188763 | 35.239 | no |
| cap 7 | end | `fotos/cap07.png` | 2560×1440 | 1070366601 | 61.302 | no |

Prompt de la foto del cap 1:
```
A young adult Spanish migrant miner, olive skin, short dark early-1960s hair, lean wiry build, in a dust-coated short-sleeved work shirt and drill trousers, one foot wrapped in a white bandage. Stands stiffly posing for a family photograph, weight shifted off the bandaged foot. Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes. Yard of a Wittenoom company house in 1962, red-ochre earth underfoot, dull grey corrugated iron wall behind. Hard cold midday light under a pale washed-out sky, short sharp shadows. Medium shot, eye-level, as a family snapshot camera, 50mm lens, moderate depth of field, bandage sharp in lower frame. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```
Prompt de la foto del cap 7:
```
An old long-handled shovel standing upright in a bank of blue-grey crocidolite tailings at a creek bed edge. The shovel stands unused, blade sunk in untouched tailings, while a thin stream slides past it toward the floodplain. Dry Pilbara creek bed below a Wittenoom gorge, red-ochre banks, shallow pools, spinifex clumps, 2026. Pale cold dawn light, long soft shadows. Wide shot, low angle at creek-bed level, deep depth of field, 24mm lens. A grainy 35mm documentary photograph taken in 2026, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```
**Lectura de CC** (miré las dos imágenes):
- **Cap 1:** el minero sale de cuerpo entero ante la chapa, sobre la tierra roja. El pie vendado está levantado y adelantado, con la punta de los dedos afuera de la venda y en un ángulo raro. El prompt pedía un plano medio y sale casi de cuerpo entero.
- **Cap 7:** la pala está clavada en un montículo de relaves azul gris, junto al arroyo y dentro del desfiladero rojo, con luz de amanecer. Coincide con el prompt.

## Etapa 2 — los 8 prompts en texto (US$ 0,1206)
`prompts_video.py` hace 8 llamadas a Opus 5.5 (effort high, como `m03:casilleros`) en paralelo, una por modelo y clip. Cada pedido lleva la plantilla del handoff tal cual, la ficha de `guias/<letra>.md` (copiada tal cual del handoff) y, del cap, el `image_prompt`, el `narration_anchor` y el `video_prompt` vivo. Producción no tiene una llamada a Opus que devuelva texto (`call_json` parsea JSON), así que la llamada se arma en lab con `claude_helpers._post` y `_track`, con el mismo modelo y esfuerzo. Solo reintenta errores de red, 429 o 5xx, que no se cobran; todas salieron al primer intento. El 03_visual de F51f se comprobó por md5 antes de llamar.

| clip | modelo | palabras | caracteres |
|---|---|---|---|
| cap 1 | K Kling 4.0 | 309 | 1707 |
| cap 1 | S Seedance 2.5 | 139 | 815 |
| cap 1 | F FLUX 3 Max | 110 | 684 |
| cap 1 | G Gemini Omni Flash 1.1 | 156 | 914 |
| cap 7 | K Kling 4.0 | 275 | 1613 |
| cap 7 | S Seedance 2.5 | 136 | 813 |
| cap 7 | F FLUX 3 Max | 111 | 669 |
| cap 7 | G Gemini Omni Flash 1.1 | 171 | 1022 |

Los 8 prompts enteros, los `video_prompt` vivos de referencia, las fichas y la plantilla están en **`lab/hyperframes/f52/PROMPTS_F52.md`**.

**Lectura de CC** (para la revisión del analista; no cambié nada):
- **K sale en castellano.** La ficha K está escrita en castellano y nombra los bloques «[Ajustes generales] / [Secuencia] / [Audio]», y Opus siguió esa forma. Los otros 3 salieron en inglés. Hay que decidir si Kling 4.0 va en castellano o si la ficha se pasa al inglés antes de la etapa 3.
- **K y G describen sonido**, porque sus fichas lo piden: K en «[Audio]» y G en «For sound…». Esos dos endpoints no tienen campo de audio; la pista se descarta.
- **G sale largo:** 156 y 171 palabras, aunque su ficha dice que «prompts cortos y enfocados rinden más». Cap 7 G cierra con «No captions.» en una línea aparte, como pide la ficha.
- **S** usa rangos 0–3 / 3–6 / 6–8 s y dice «one single continuous shot»; describe solo lo que se mueve.
- **F** es una sola oración larga, cámara → sujeto → entorno → look, cerrada con «no on-screen text, no subtitles».
- **Los 8 mantienen la intención del movimiento aprobado:** el acercamiento lento, el polvo y la brisa en el cap 1, y el agua, el spinifex y el polvo de los relaves en el cap 7.

## Gasto
| paso | US$ | de dónde |
|---|---|---|
| schemas y precios | 0 | solo GET |
| 2 fotos Seedream | 0,0700 | `cost_history` `f52_lab` |
| 8 prompts Opus | 0,1206 | `cost_history` `f52_lab_prompts` |
| **total** | **0,1906 de 16,00** | registros de `cost_history` desde 13:29:18 |

## Lo que queda abierto
1. **PARADA:** el analista revisa los 8 prompts en `PROMPTS_F52.md`, y la etapa 3 (los 8 clips, ≈ US$ 10,7–14,9) no se corre hasta que Omar diga «sigue». `prueba_video.py` y la hoja ciega todavía no existen.
2. **Kling en castellano** (ver la lectura de la etapa 2): hay que decidir el idioma antes de gastar.
3. **Tolerancia:** ninguno de los 4 schemas tiene ese campo, así que la permisividad no se puede ajustar en fal. Se va a ver si alguno rechaza o modera en la etapa 3.
4. **Audio en K y G:** no se puede apagar por schema; la pista se descarta.
5. **El precio por resolución no se pudo leer:** el tope de la etapa 3 se controla con el costo real de cada llamada.
6. **La foto del cap 1:** el pie vendado sale en un ángulo raro, con la punta de los dedos afuera de la venda. Es el primer cuadro de los 4 clips del cap 1, así que si se rehace hay que hacerlo antes de la etapa 3.
7. **No corrí las suites:** la tanda no toca código de producción ni tests.

## Veredicto de revisor-handoff
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Etapa 0: DECISIONES tal cual y commit con el md5 del handoff | OK | `md5sum` del handoff da aa964d1f…; la línea nueva de `DECISIONES.md` es idéntica a la del handoff; el commit 35804d2 lleva el md5 en el mensaje |
| 2 | Tope US$ 16 en `lab/TOPE_TANDA.json` | OK | `{"usd": 16.0, "desde": "2026-10-29T13:29:18"}` |
| 3 | Schema leído antes de llamar, y campos pegados en el reporte | OK | `SCHEMAS_F52.md` y `schemas/{K,S,F,G}.json`; tabla de campos en `F52_REPORT.md` líneas 27–39 |
| 4 | Tolerancia más permisiva que acepte el schema | OK, con salvedad | Ningún schema de video trae campo de safety o tolerancia: el grep solo coincide en `seedream.json` y `_resumen.json`. El reporte lo declara. No revisé los OpenAPI campo por campo. |
| 5 | Precio leído contra el tope; PARADA si lo pasa | OK | Con precios leídos los 8 clips cuestan ≈ US$ 10,7. Con las cifras del handoff ≈ 14,9. Gastado 0,19. Ninguno pasa 16. El reporte admite que el precio por resolución no se pudo leer. |
| 6 | Etapa 1: 2 fotos iniciales con el prompt vivo y el camino de producción | OK | `fotos/cap01.png` (421 KB) y `cap07.png` (753 KB); `fotos_f52.json` con el endpoint Seedream v5 lite t2i; los 2 prompts están pegados en el reporte; costo `f52_lab` = 0,07 en `cost_history` |
| 7 | Fichas `guias/{K,S,F,G}.md` tal cual las del handoff | OK | Comparadas una por una con el handoff, líneas 36–42: texto idéntico |
| 8 | Pedido a Opus igual al del handoff, sin ajustes | OK | `PEDIDO` en `prompts_video.py` líneas 31–42 coincide línea por línea con el bloque del handoff. Modelo `claude-opus-5-5`, effort high. |
| 9 | 8 prompts, uno por modelo y clip, con conteo de palabras y fichas | OK | Los 8 prompts de `prompts_f52.json` están en `PROMPTS_F52.md`. Palabras: 309, 139, 110, 156, 275, 136, 111, 171. Opus costó 0,1206. |
| 10 | Etapa 3 no corrida: sin mp4 ni llamadas a los 4 endpoints de video | OK | `find` no encuentra ningún `.mp4` en f52. Los endpoints `*/image-to-video` aparecen solo en `schemas_f52.py` (GETs). `prueba_video.py` no existe. `cost_history` solo tiene `f52_lab` y `f52_lab_prompts`. |
| 11 | Producción sin cambios | OK | `git diff --stat a365708 HEAD` fuera de `lab/hyperframes/f52/` y `DECISIONES.md` está vacío. `git diff` de `config.py`, `asset_manager.py`, `m03_visual.py` y `m03_imagenes_v3.py` está vacío. |
| 12 | PARADA con `PROMPTS_F52.md` y veredicto en el reporte | PARCIAL | `PROMPTS_F52.md` existe. En `F52_REPORT.md` falta pegar el veredicto (queda `{{VEREDICTO}}`). |

Observaciones:
- `F52_REPORT.md` dice que `lab/TOPE_TANDA.json` está "fuera de git", pero está trackeado y figura modificado sin commitear. Error menor del reporte.
- El reporte anuncia un commit "cierre" con reporte y ESTADO que todavía no existe. No verifiqué la actualización de `lab/ESTADO_SESION.md`.
- Kling salió en castellano porque su ficha está en castellano. Gemini salió con 156 y 171 palabras aunque su ficha dice "prompts cortos". El reporte lo señala.
- La foto del cap 1 tiene el pie vendado en un ángulo raro y es el primer cuadro de los 4 clips del cap 1. El reporte lo marca.

Fuera de alcance: ninguno. `diag_234_cap4.py` y `lab/hyperframes/f28/a/f28a.log` ya estaban modificados antes de la tanda. `lab/TOPE_TANDA.json` también figura modificado sin commitear, pero es el tope que pidió Omar.

Riesgos que el contrato no cubre:
- Ningún schema de video trae tolerancia. Si algún modelo modera el contenido oscuro del canal, solo se va a saber al gastar en la etapa 3.
- El precio por resolución (Seedance a 720p, FLUX a 1080p) no se pudo leer; el control del tope depende del costo real de cada clip.
- K y G no tienen campo de audio y sus prompts piden sonido; hay que descartar la pista al medir.

### Adenda de CC (después del veredicto)
- **TOPE_TANDA, «fuera de git»:** tenía razón el revisor. Corregí el reporte: el archivo está trackeado y, por regla de la cadena, se modifica sin commitear. En los reportes de F50f, F51b y F51d-A dije lo mismo, y también estaba mal.
- **#12 y el commit de cierre:** el veredicto queda pegado y ESTADO actualizado en el commit del reporte.
