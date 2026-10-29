# F53b — motor de clips nuevo: Parte A (perfiles, costo, escritor del prompt de video) · PARADA A

CC → Omar / analista · 2026-10-29 · rama `f11-guion-v4`. Handoff `HANDOFF_F53b_motor_de_clips.md`, md5 `3058bd0373ad63b5d3ba96b4917054d5` (coincide), con la adenda `ADENDA_F53b_kling_respaldo.md`, md5 `5f2f5fd60c63381e90b1db072e3cf271` (coincide): **el respaldo es Kling 4.0 (K) a 1080p; Seedance no entra.** Gasto de la Parte A: **US$ 0,065 de 3,00**. La Parte B no se empezó: espera el «sigue» de Omar.

## Commits
| paso | commit | qué |
|---|---|---|
| etapa 0 | `630a7d0` | DECISIONES 14:43 (handoff) y 15:00 (adenda), tal cual; incluye el handoff y la adenda, con los md5 en el mensaje |
| Parte A | `7986ff7` | `engine_profiles.py`, `cost_tracker.py`, `script_engine/video_prompt.py` (nuevo), 3 archivos de tests, stickers y MAPA |
| seco | `c350e17` | `lab/hyperframes/f53b/seco_g.py`, `SECO_G.md`, `seco_g.json` |
| cierre | (este) | reporte, ESTADO y logs de `lab/hyperframes/f41/f53b_a/` |

`lab/TOPE_TANDA.json` = `{"usd": 3.0, "desde": "2026-10-29T15:02:37"}`. Está trackeado, pero se modifica sin commitearlo. El tope de F53a-K, que era 5, se reemplazó por el de esta tanda, como pidió Omar («TOPE_TANDA = 3 desde ahora»).

## Etapa 0
`tail -2 DECISIONES.md`:
```
- 2026-10-29 14:43 · **F53b:** motor de clips = Gemini Omni Flash 1.1 a 1080p; si Google lo rechaza por contenido, Seedance 2.5 a 1080p automático; no se suavizan los prompts; Veo se borra · Omar · F53b
- 2026-10-29 15:00 · **F53b adenda:** el respaldo de Gemini Omni Flash es Kling 4.0 a 1080p (F53a-K pasó la moderación sin suavizar); Seedance sale de la cadena · Omar · F53b
```

## Parte A — módulos tocados (antes → después)
Hice el punto 1 yo mismo, porque fija la interfaz que usan los otros dos. Los puntos 2 y 3 los hicieron 2 subagentes en paralelo; revisé su salida y corrí sus tests.

| módulo | antes | después |
|---|---|---|
| `engine_profiles.py` | perfiles de motor de **imagen** (`EngineProfile` Kling y Seedream, `select_profile`) | **además** `VideoProfile`, DATA sin HTTP. Tiene endpoint, `campo_imagen`, rango de duración, si la duración va como texto, resolución, `campo_audio` (None = la pista se quita con ffmpeg), `ficha` (la guía de F52b en inglés, tal cual), `usd_por_s_leido`, `mult_resolucion` y el método `costo(segundos, ancho, alto)`. Hay dos perfiles: **`PERFIL_VIDEO_G`** (`google/gemini-omni-flash/v1.1/image-to-video`, `image_url`, 3–10 s, 1080p, sin audio, 0,03 × 5 = 0,15 US$/s, o sea 1,20 por clip de 8 s) y **`PERFIL_VIDEO_K`** (`kling/v4/image-to-video`, `start_image_url`, 3–30 s, 1080p, sin audio, 0,157 × 1,5 = 0,235 US$/s, o sea 1,884 por clip de 8 s). Se eligen con `select_video_profile(engine_key)`. No hay perfil de Seedance |
| `cost_tracker.py` | `track_fal` cobra fijo `pipeline.costs["fal_per_clip"]` (0,24, «Veo») | **además** `track_video(perfil, segundos, ancho, alto, description)`: la entrada en `stage` VIDEO, `service` = «fal <endpoint>», unidades en segundos y `total_cost` = `perfil.costo(…)`. `track_fal` queda con un comentario de que se borra con Veo en la Parte B |
| `config.py` (**fuera de git**, `.gitignore:2`: guarda las llaves) | las estimaciones `estimated_cost_per_long_video` y `estimated_cost_per_short_video` usan `costs["fal_per_clip"]` | usan `PERFIL_VIDEO_G.costo(8)` = 1,20, con import perezoso por el import circular, y el 8 citado como `m03_visual.VEO_CLIP_DURATION_SEC`. El cambio está solo en el disco y ningún commit lo lleva |
| `script_engine/video_prompt.py` (**nuevo**) | — | `escribir(perfil, foto, image_prompt, ancla, video_prompt_aprobado, *, post=None, description=None) -> str` es el escritor de F52b pasado a producción. Usa Opus 5.5 (`MODELO_CASILLEROS`) con effort high (`guion_v4.ESFUERZO`). Manda primero la foto como bloque `image`, con el tipo leído de los bytes (JPEG o PNG; otro formato da `ValueError`), y después `PEDIDO` (copiado byte a byte de `lab/hyperframes/f52/prompts_video.py`; un test lo verifica) con `perfil.ficha`. Sin ancla o sin movimiento aprobado va «(none)». Reintenta como `claude_helpers.call_json`; otro 4xx o una negativa (`refusal`) dan `ClaudeError`. Devuelve el texto |

**Decisiones de CC, para revisar:**
1. **`track_fal` y `fal_per_clip` se borran en la Parte B, no en la A.** El handoff pone «`fal_per_clip` se borra de `config.py`» en la Parte A. Pero su único llamador de producción es el camino de Veo de `asset_manager` (l. 648), que se borra en la B. Borrarlo ahora rompería producción hasta entonces, así que en la A agregué `track_video` y cambié las estimaciones. Hay un llamador más, en lab: `lab/hyperframes/f50/veo_prueba.py:51` se va a romper en la B.
2. **Si Opus responde sin texto, `escribir` da `ClaudeError`** en vez de devolver «»: así nunca llega un prompt vacío al motor. No es una regla del pedido a Opus, es una guarda de código.
3. **`config.py` está fuera de git**, así que su cambio no va en ningún commit.

## Tests nuevos
| archivo | qué prueba | resultado |
|---|---|---|
| `test_module_f53b.py` (4) | los campos de G y K contra el schema de fal de F52, las fichas iguales a `f52/guias/{G,K}.md`, costo de 8 s (G 1,20, K 1,884) y que no haya perfil de Seedance | 4 passed |
| `test_module_f53b_costo.py` (5) | `track_video` con G y K, sin video activo; estimaciones sin `fal_per_clip`; la diferencia exacta contra el cálculo viejo | 5 passed |
| `test_module_f53b_video_prompt.py` (11) | `PEDIDO` byte a byte igual al de lab; el body (imagen primero, jpeg/png de los bytes, ficha G/K, opus 5.5, high); «(none)»; negativa → ClaudeError; reintentos 529/red/400; WebP → error | 11 passed |

Corridos juntos con f51f y f50b: 53 passed. Stickers: `engine_profiles.py`, `cost_tracker.py`, `config.py` y uno nuevo para `script_engine/video_prompt.py`, en estado «huérfano» hasta la Parte B. `mapa_modulos.py --check`: 158 archivos · 0 fallas.

## Corrida en seco de `video_prompt.py` para G (US$ 0,065)
`lab/hyperframes/f53b/seco_g.py` hace 2 llamadas a Opus por el módulo de producción, en paralelo, sin ningún clip. Usa las fotos `lab/hyperframes/f52/fotos/cap01.png` y `cap07.png`, y el `image_prompt`, el `narration_anchor` y el `video_prompt` vivos de los caps 1 y 7 del `03_visual.json` de Wittenoom (F51f, md5 `0d57b6ba…`). Guarda de tope: 0 + 0,15 < 3.

**Cap 1** (174 palabras):
```
A slow, somber documentary shot on grainy early-sixties 35mm film, muted colors, slight underexposure. A young miner stands full-length in a red-earth yard before a grey corrugated iron wall. He wears a dust-stained shirt with rolled sleeves and dark dusty trousers. His white-bandaged foot is lifted, with only its tip resting on the ground and his weight on the booted foot. Camera: a very slow push-in from the full shot, ending slightly closer, with the bandaged foot staying sharp in the lower frame. Action: fine red dust drifts low across the ochre ground, his shirt stirs faintly in a light breeze, and he breathes slowly. He holds his stiff pose, with his steady stare into the lens and his face and body otherwise still. Keep from the image: his face, clothing, pose, the white bandage, the corrugated wall, the red earth and the pale washed-out sky. Sound: soft dry wind and a faint tick of sheet metal, with no music and no dialogue. One continuous 8-second shot, no cuts, no on-screen text, no captions.
```
**Cap 7** (145 palabras):
```
Slow push-in at creek-bed level on the old rusted shovel standing upright in the blue-grey tailings pile, its blade sunk and untouched. The thin stream slides steadily past on the right toward the floodplain, rippling softly over stones and shallow pools. Midway, a faint breeze stirs the spinifex clumps and lifts a few pale wisps of dust off the tailings. The camera ends on a closer framing of the shovel and sunken blade against the red-ochre bank, with the gorge still visible behind. Keep the shovel's position and shape, the blue-grey pile, the stream's course, the red banks, the gorge walls and the pale cold dawn light with long soft shadows unchanged. Grainy 35mm documentary look, muted colors, slight underexposure, somber dark-history realism. Sound: quiet trickle of water, soft wind through the grass, no music, no dialogue. One continuous 8-second shot, no cuts, no captions.
```
**Lectura de CC:**
- **Cap 1:** nombra el encuadre real de la foto: cuerpo entero y el pie vendado levantado, apoyado en la punta. No dice de qué lado es el pie.
- **Cap 7:** ubica el arroyo a la derecha, como en la foto.
- **Largo:** 174 y 145 palabras. Son más cortos que los de F52b (167 y 165), pero la ficha de G pide «short focused prompts».

## Al cerrar
`bash lab/hyperframes/f41/verificar.sh f53b_a` (logs en `lab/hyperframes/f41/f53b_a/`):
```
md5: f792f3d483a1fa42daed5f7f0e054f46 *output/ba6c3cac-a091-41c0-8dad-afd2f4364747/_fase2b_work/ch02_segment_only.mp4
rapida: 55 passed, 3 skipped in 3.24s
amplia: 4 failed, 1039 passed, 30 skipped, 4 warnings in 67.94s (0:01:07)
FAILED test_module_gfx_lab.py::test_cues_sin_escribir_el_proyecto - Assertion...
FAILED test_module_m03_merge_timing.py::test_c_veo_path_y_veo_anchor_intacto
FAILED test_module_m03_merge_timing.py::test_c_guarda_de_minimo - AssertionEr...
FAILED test_module_gfx_lab.py::test_preview_usa_las_plantillas_reales - asser...
```
- Candado ch02 `f792f3d4…` sin cambio; rápida 55.
- Amplia: 1039 passed + 4 failed, las 4 previas de siempre (`m03_merge_timing` ×2, `gfx_lab` ×2). La cuenta: 1019 de F51f + 20 nuevos (4 + 5 + 11) = 1039.

## Lo que queda abierto
1. **PARADA A:** el analista revisa los 2 prompts de G. La Parte B (cableado en `asset_manager`, borrar Veo, 1 clip real del cap 7) no arranca sin el «sigue» de Omar.
2. **Parte B:** borrar `track_fal` y `fal_per_clip`, junto con `_call_veo_once`, `_generate_veo_clip`, `_veo_duration`, `VEO_DURACIONES_S`, `VEO_NEGATIVE_PROMPT` y sus tests; `lab/hyperframes/f50/veo_prueba.py` se rompe.
3. **`video_prompt.py` está huérfano** hasta que `asset_manager._generate_clip` lo llame en la Parte B. Quien lo llame va a tener que atrapar `ClaudeError`, por la API o una negativa, y `ValueError`, por una foto en un formato inválido.
4. **`config.py` fuera de git:** el cambio de las estimaciones vive solo en este disco.
5. **No se renombra el concepto «veo»** (`veo_position`, `veo_chapters`, `_process_veo_chapter`, `VEO_CLIP_DURATION_SEC`), como dice el handoff.
6. **La cadena G→K todavía no existe.** `video_prompt.escribir` sirve para los dos perfiles, pero el prompt de K solo se probó en los tests, con un `_post` falso. La cadena se arma en la Parte B.

## Veredicto de revisor-handoff
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | md5 handoff y adenda | OK | `md5sum`: 3058bd03… y 5f2f5fd6…, los dos coinciden |
| 2 | Etapa 0: DECISIONES 14:43 y 15:00 tal cual | OK | `git diff a560817 HEAD -- DECISIONES.md`: las 2 líneas son literales a las del handoff y la adenda. La de 14:43 sigue diciendo «Seedance» porque así la dicta el handoff; la 15:00 la corrige |
| 3 | TOPE_TANDA = 3 | OK | `lab/TOPE_TANDA.json` en disco: `{"usd": 3.0, "desde": "2026-10-29T15:02:37"}`. Está modificado sin commit; el reporte lo declara |
| 4 | `VideoProfile` G y K, sin Seedance | OK | `engine_profiles.py:~112-177`: solo `PERFIL_VIDEO_G` y `PERFIL_VIDEO_K`. Los endpoints y campos coinciden con handoff y adenda: G `image_url`, 3–10, int; K `start_image_url`, 3–30, int; 1080p, sin audio. `grep -i seedance` solo aparece en un comentario y en el test que exige que no exista el perfil |
| 5 | Fichas = `f52/guias/{G,K}.md` | OK | Comparación por script: iguales tras `strip()`. No son idénticas byte a byte, porque el .md termina en salto de línea y la ficha no |
| 6 | `PEDIDO` byte a byte = `f52/prompts_video.py` | OK | Script: `m.PEDIDO == v.PEDIDO` da True. El test del repo también lo verifica |
| 7 | Costos | OK | G: 0,03×5 = 0,15/s, 1,20 por clip de 8 s. K: 0,157×1,5 = 0,235/s, 1,884 por clip de 8 s (la adenda dice ≈1,88). Coincide con la tabla |
| 8 | `cost_tracker.track_video(perfil, s, ancho, alto)` | OK | `cost_tracker.py:286-302`: total = `perfil.costo(...)` |
| 9 | Estimaciones de `config.py` con el costo de G a 8 s | OK | `config.py:~228 y ~253` usan `PERFIL_VIDEO_G.costo(8)`. El archivo está en .gitignore, así que el cambio solo existe en disco y ningún commit lo lleva. NO VERIFICABLE por git |
| 10 | `video_prompt.py`: Opus 5.5 high, foto como bloque image, tipo leído de los bytes | OK | `video_prompt.py:46-52` (`tipo_imagen`), `:68-71` (`armar_body`). Una respuesta sin texto da `ClaudeError`, como indica el reporte |
| 11 | Sin reglas nuevas en el pedido a Opus ni en las fichas | OK | El pedido es el de F52b y las fichas son las de F52b. Lo único agregado es el valor «(none)» para ancla o movimiento ausentes, igual que en F53a |
| 12 | Tests nuevos verdes | OK | Corrí `pytest` sobre los 3 archivos: 20 passed (4+5+11). `mapa_modulos.py --check`: 158 archivos, 0 fallas |
| 13 | Corrida en seco: 2 prompts de G, enteros | OK | `lab/hyperframes/f53b/seco_g.json` tiene los prompts de cap01 y cap07 y coinciden con los pegados en el reporte. Costo en `data/cost_history.json`, registro `f53b_seco_g`: 0,031436 + 0,033596 = US$ 0,065032. El gasto es consistente con lo declarado y está dentro del tope |
| 14 | Parte B no empezada | OK | `git diff a560817 HEAD` no toca `asset_manager.py`, `m03_visual.py` ni `qa_studio_server.py`. `git status` tampoco los muestra modificados |
| 15 | No renombrar «veo» | OK | No hay renombres en el diff |
| 16 | Decisión de CC: `track_fal` y `fal_per_clip` quedan hasta la Parte B | OK, la juzgo correcta | `config.py:158` conserva `fal_per_clip` y `cost_tracker.py:276` conserva `track_fal`. Su único llamador de producción es el camino de Veo de `asset_manager`, que el handoff manda borrar en la B. Borrarlos en A rompería producción sin motivo. El reporte declara el desvío y deja un comentario en el código. El texto literal del handoff (punto 2) no se cumple en esta parte, pero el desvío está justificado y se paga en la B |
| 17 | Reporte | PARCIAL | `F53b_REPORT.md` está sin commit y con `{{VEREDICTO}}` pendiente. Es lo esperado antes de pegar este veredicto |

Fuera de alcance: ninguno en los commits de la Parte A. En el árbol de trabajo hay modificados `diag_234_cap4.py` y `lab/hyperframes/f28/a/f28a.log`, que ya estaban así al empezar (snapshot de gitStatus); no son de F53b. `lab/TOPE_TANDA.json` está modificado y sin commit, por pedido de Omar.

Riesgos que el contrato no cubre:
- `video_prompt.py` y los perfiles están huérfanos hasta la B. El prompt de K solo se probó con un `_post` falso; el primer prompt real para K sale recién en la Parte B.
- El cambio de `config.py` solo está en este disco; si se pierde, las estimaciones vuelven a depender de `fal_per_clip`.
- En la B, `lab/hyperframes/f50/veo_prueba.py:51` se rompe al borrar `track_fal`. Las 4 fallas de la suite amplia son las de siempre (`m03_merge_timing` ×2, `gfx_lab` ×2). Esa suite no la corrí: no verifiqué la cifra 1039 passed, solo la tomé del reporte.

### Adenda de CC (después del veredicto)
- **#17:** el veredicto queda pegado y el reporte con commit, junto con ESTADO, en el commit de cierre.
- **Riesgo 3, la suite amplia:** la cifra sale de `lab/hyperframes/f41/f53b_a/suite_amplia.log`, que va en el commit de cierre: «4 failed, 1039 passed, 30 skipped».

---

# F53b — Parte B: cableado de la cadena G → K, sale Veo · PARADA B

Omar: «sigue» (2026-10-29). Mismo handoff (md5 `3058bd03…`) más la adenda (md5 `5f2f5fd6…`), los dos verificados. Gasto de la tanda F53b: **US$ 1,3369 de 3,00** (A 0,065 + B 1,2719).

## Commits
| paso | commit | qué |
|---|---|---|
| B | `4fda044` | `asset_manager._generate_clip` con la cadena; se borra Veo y `track_fal`; `qa_studio_server`; `fase2a`; test de la cadena; seco de K; clip real |
| B | `0c1a16e` | sticker de `asset_manager.py` al md5 final |
| B | `1c492ea` | `lab/hyperframes/f50/papel.py` sin los imports de Veo (ver «Decisiones de CC») |
| cierre | (este) | reporte, ESTADO y logs de `lab/hyperframes/f41/f53b_b/` |

## Módulos (antes → después)
| módulo | antes | después |
|---|---|---|
| `asset_manager.py` | `_call_veo_once`, `_generate_veo_clip` y `_veo_poll` llaman a `fal-ai/veo3.1/lite` con `negative_prompt` (`VEO_NEGATIVE_PROMPT`), `duration` «8s» (`_veo_duration`, `VEO_DURACIONES_S`), `image/png` fijo y `track_fal` (0,24 fijo) | **`_generate_clip(foto, intento_movimiento, salida, *, image_prompt, ancla, log)`** recorre `api.video_engines` (`gemini_omni_flash` → `kling_4`). Por cada motor, `video_prompt.escribir` le pide a Opus el prompt con la ficha del perfil, mirando la foto, y se llama al motor por la cola de fal (`_call_clip_once`, `_clip_payload`, `_clip_poll`). El payload lleva la foto con el tipo leído de los bytes, `duration` int 8 (`VEO_CLIP_DURATION_SEC`), `resolution` de `api.video_resolution` y no lleva campo de audio. Si el motor rechaza por contenido, pasa al siguiente sin suavizar. Si falla la red (429 o 5xx), reintenta el mismo motor (`CLIP_MAX_ATTEMPTS_NON_REJECTION` = 3, el de Veo) y no salta de motor. La pista de audio se quita con `ffmpeg -an -c:v copy`, y un mp4 sin video legible da error. `track_video` registra los segundos reales. Al log del pipeline (y a `log`, si se pasa) van el motor, los rechazos literales, los segundos y el costo. Se borran las 7 piezas de Veo; `VEO_POLL_TIMEOUT` y `VEO_MAX_ATTEMPTS_NON_REJECTION` pasan a `CLIP_POLL_TIMEOUT` y `CLIP_MAX_ATTEMPTS_NON_REJECTION`, con los mismos valores. La clave `veo_config` del manifiesto queda y suma `video_engines` y `video_resolution` |
| `cost_tracker.py` | `track_fal` | se borra (`track_video` es de la Parte A) |
| `config.py` (**fuera de git**) | `fal_video_model`, `fal_veo_resolution`, `costs["fal_per_clip"]`; estimaciones con `PERFIL_VIDEO_G.costo(8)` | `video_engines = ("gemini_omni_flash", "kling_4")` y `video_resolution = "1080p"`, citando DECISIONES. Se borran los 3 campos viejos. **Chascada 1:** las estimaciones usan `VEO_CLIP_DURATION_SEC` con import perezoso (`m03_visual` importa `config`), en vez del 8 escrito a mano. Largo US$ 10,00 y corto US$ 5,00 |
| `qa_studio_server.py` l. 1060 | `generate_veo_fn or am._generate_veo_clip` | `generate_veo_fn or am._generate_clip`. Es una línea, y el nombre del parámetro queda, porque «veo» no se renombra |
| `fase2a.py` | el cap veo normalizado no lleva el ancla | `norm_ch["narration_anchor"]` (ver «Decisiones de CC») |
| `test_module_f50b.py` | `test_payload_veo_con_negative_prompt_y_duration` | borrado |
| `test_module_f53b_cadena.py` (nuevo, 15, fal simulado) | — | 1) G rechaza con el 422 literal de F53a y K lo hace (1 POST a cada uno, `track_video` con K, el log con el rechazo literal); 2) G lo hace y K no se llama; 3) 504 en el submit o en el status de G reintenta G y no salta a K, y si el 504 persiste, lanza el error sin llamar a K; 4) payload G/K (`image_url`/`start_image_url`, `duration` int 8, 1080p, sin audio, la foto como `image/jpeg` aunque el archivo sea .png); 5) si los dos rechazan da `ContentRejectedError`, con log `motor` None; 6) Veo y `track_fal` ya no existen |

`script_engine/m03_visual._seedream_video_prompt` **no se borra**, porque m03 lo sigue usando para escribir el `video_prompt` aprobado del `03_visual` (l. 1989), que es el «APPROVED MOTION» de la cadena.

## Mapa: quién llamaba a Veo antes → quién llama a `_generate_clip` ahora (grep)
| antes (Veo) | después |
|---|---|
| `asset_manager._process_veo_chapter` l. 1136 → `_generate_veo_clip` | `asset_manager._process_veo_chapter` l. 1156 → `_generate_clip(…, image_prompt=raw_img_prompt, ancla=chapter["narration_anchor"])` |
| `asset_manager._generate_veo_clip` → `_call_veo_once` → `_veo_poll`; `cost_tracker.track_fal` | `_generate_clip` → `video_prompt.escribir` → `_call_clip_once` → `_clip_poll`; `cost_tracker.track_video` |
| `qa_studio_server._clipfix_core` l. 1060 → `am._generate_veo_clip` | l. 1060 → `am._generate_clip` (sin ancla ni image_prompt; ver abiertos) |
| `config.api.fal_video_model` / `fal_veo_resolution` / `costs["fal_per_clip"]` | `config.api.video_engines` / `video_resolution`; perfiles en `engine_profiles` |
| lab: `lab/hyperframes/f50/veo_prueba.py` (`_call_veo_once`, `track_fal`, `fal_video_model`) | **roto** (permitido; ver abiertos) |
| lab: `lab/hyperframes/f50/papel.py` (`VEO_NEGATIVE_PROMPT`, `_veo_duration`) | arreglado: muestra `api.video_engines` y `VEO_CLIP_DURATION_SEC` |
| tests: `test_module_f50b.py` (payload de Veo) | borrado; nuevo `test_module_f53b_cadena.py` |

Al cierre, `grep` de `_call_veo_once|_generate_veo_clip|_veo_duration|VEO_DURACIONES_S|VEO_NEGATIVE_PROMPT|track_fal|fal_per_clip|fal_video_model|fal_veo_resolution|_veo_poll` en los `.py` de producción da 0. Solo queda en `veo_prueba.py` (roto), en el regex de `lab/tools/mapa_modulos.py`, en los asserts de los tests nuevos y en el texto de `test_module_f53b_costo.py`.

## Chascada 2 — prompt de K en seco (US$ 0,0392)
`lab/hyperframes/f53b/seco_k.py` hace 1 llamada a Opus por `video_prompt.escribir(PERFIL_VIDEO_K, …)` sobre `f52/fotos/cap01.png`, con las mismas entradas que SECO_G. No genera ningún clip.

**K, cap 1** (299 palabras):
```
[General settings]
Dusty yard of a company house in 1962, red-ochre earth underfoot, a long dull grey corrugated iron wall behind, a pale washed-out sky above. Grainy 35mm documentary film look, muted colors, slight underexposure, somber dark-history realism. Hard midday light casts short sharp shadows. The camera tone is slow, steady and observational, like a family snapshot camera at eye level. One continuous 8-second shot.

Subject: a lean young miner with olive skin and short dark hair stands full-length in the center of the frame and stares straight into the lens. He wears a dust-stained tan work shirt with sleeves rolled to the elbows and dark trousers streaked with red dust. His right foot is wrapped in a white bandage and held lifted just above the earth, and his weight rests on his left booted foot.

Background: the corrugated iron wall stays still. Fine red dust drifts low across the ochre ground.

[Sequence]
0–3 s: Static wide framing. Fine red dust drifts low across the yard from left to right. The young man holds his stiff pose, chest rising and falling slowly. His gaze stays fixed on the camera.

3–6 s: The camera begins a very slow push-in toward him. The loose fabric of his shirt stirs faintly in a light breeze. The bandaged foot hangs steadily just above the ground. His fingers tense slightly at his sides.

6 s–end: The push-in ends slightly closer, framing him from the head down to the white bandaged foot, which stays sharp in the lower frame. He stays in place, posed and still, breathing slowly. Short sharp shadows stay steady on the red earth.

[Audio]
Soft wind across the open yard, faint hiss of drifting dust, a quiet creak from the corrugated iron wall, his slow breathing. No subtitles, no background music.
```
**G, cap 1** (el de SECO_G, 174 palabras):
```
A slow, somber documentary shot on grainy early-sixties 35mm film, muted colors, slight underexposure. A young miner stands full-length in a red-earth yard before a grey corrugated iron wall. He wears a dust-stained shirt with rolled sleeves and dark dusty trousers. His white-bandaged foot is lifted, with only its tip resting on the ground and his weight on the booted foot. Camera: a very slow push-in from the full shot, ending slightly closer, with the bandaged foot staying sharp in the lower frame. Action: fine red dust drifts low across the ochre ground, his shirt stirs faintly in a light breeze, and he breathes slowly. He holds his stiff pose, with his steady stare into the lens and his face and body otherwise still. Keep from the image: his face, clothing, pose, the white bandage, the corrugated wall, the red earth and the pale washed-out sky. Sound: soft dry wind and a faint tick of sheet metal, with no music and no dialogue. One continuous 8-second shot, no cuts, no on-screen text, no captions.
```
**Lectura de CC:**
- **K:** sigue la estructura de su ficha («[General settings] / [Sequence] 0–3 / 3–6 / 6 s–end / [Audio]», «No subtitles, no background music»).
- **El pie:** K dice que el vendado es el **derecho**, que es lo correcto. En F52b, con el mismo pedido, Opus había dicho «left». G no dice de qué lado es.
- **El arranque:** K empieza con «Static wide framing» y el acercamiento llega a los 3 s; G lo hace desde el primer cuadro.

## El clip real — cap 7 de Wittenoom, por el camino de producción
`lab/hyperframes/f53b/clip_real.py` llama a `am._generate_clip(f52/fotos/cap07.png, video_prompt del cap 7, …, image_prompt=…, ancla=…, log=…)`, con las entradas del `03_visual` de F51f (md5 `0d57b6ba…`).
- **Guarda de tope:** gastado 0,1042 + peor caso 1,24 < 3.
- **Cadena limitada a G en esta corrida** (`api.video_engines = ("gemini_omni_flash",)`, en el script): si G hubiera rechazado, K habría llevado el peor caso a 0,10 + 1,24 + 1,92 = 3,26, más que el tope de 3. El handoff pide este clip con G. En producción, la cadena sigue siendo G → K.

**Log del clip** (`clip_real.json`, y en el log del pipeline: «[clip] cap07_clip_01.mp4: gemini_omni_flash · 8.00 s · US$ 1.2000»):

| motor | rechazo de G | segundos | ffprobe | costo de cost_tracker | tabla del handoff |
|---|---|---|---|---|---|
| `gemini_omni_flash` | ninguno | 8,000 | h264 · 1920×1080 · 24 fps · 192 cuadros · **sin audio** (quitado con `-an`) | fal G **1,2000** + Opus del prompt 0,0327 = 1,2327 | 0,15 US$/s × 8,0 s = **1,20**: igual |

**Prompt de G** que escribió Opus para el clip:
```
Slow push-in at creek-bed level on an old rusted shovel standing upright, blade sunk in a mound of blue-grey crocidolite tailings, as a thin creek slides past it through red-ochre ground. The water ripples steadily over stones and shallow pools. Late in the shot, a faint breeze stirs the spinifex clumps and lifts a few wisps of pale dust from the tailings. The camera ends on a closer framing of the shovel and its buried blade against the red bank. The shovel never moves.

Keep from the image: the shovel's position and angle, the blue-grey mound, the winding stream on the right, the red banks and spinifex, the dark gorge cliffs and pale sky.

Look: grainy 35mm documentary film, muted colors, slight underexposure, pale cold dawn light with long soft shadows, somber and still.

Sound: quiet running water and a soft, thin wind; no music, no dialogue.

One continuous 8-second shot, no cuts, no on-screen text, no captions.
```
**Tira a 1 cuadro/s** (`clip/cap07_tira.jpg`, ver-render; lectura de CC): un acercamiento lento a la pala, el agua que corre, polvo que se levanta de los relaves alrededor de los 5 s y la pala quieta. Sin cortes y sin cambio de escena. El mp4 (`clip/cap07_clip_01.mp4`, 23,6 MB) queda fuera de git.

**El costo real** se confirma en el panel de fal. Esta llave no tiene permiso para leer el uso (403, F52).

## Decisiones de CC (para revisar)
1. **`fase2a.py` lleva `narration_anchor`.** Sin esa línea, `_process_veo_chapter` no tiene la frase de la voz y Opus la recibiría «(none)». El handoff no lista `fase2a` entre los módulos, pero `video_prompt.escribir` usa el ancla por diseño (Parte A).
2. **`papel.py` se arregló**, aunque solo se había avisado que `veo_prueba.py` se podía romper. Importaba `VEO_NEGATIVE_PROMPT` y `_veo_duration` al arrancar, así que quedaba roto entero, y es la herramienta del papel de fotos. Ahora muestra los motores y la duración, y su salida es igual a la de F51f salvo esas líneas.
3. **Guarda de mp4 sin video legible:** si ffprobe no lee video, `_call_clip_once` da `RuntimeError` en vez de registrar costo 0. La encontró el subagente de los tests.
4. **El clip real corrió solo con G**, por el tope (arriba).

## Al cerrar (Parte B)
`bash lab/hyperframes/f41/verificar.sh f53b_b` (logs en `lab/hyperframes/f41/f53b_b/`):
```
md5: f792f3d483a1fa42daed5f7f0e054f46 *output/ba6c3cac-a091-41c0-8dad-afd2f4364747/_fase2b_work/ch02_segment_only.mp4
rapida: 55 passed, 3 skipped in 3.54s
amplia: 4 failed, 1053 passed, 30 skipped, 4 warnings in 73.70s (0:01:13)
FAILED test_module_m03_merge_timing.py::test_c_veo_path_y_veo_anchor_intacto
FAILED test_module_m03_merge_timing.py::test_c_guarda_de_minimo - AssertionEr...
FAILED test_module_gfx_lab.py::test_preview_usa_las_plantillas_reales - asser...
FAILED test_module_gfx_lab.py::test_cues_sin_escribir_el_proyecto - Assertion...
```
- **Candado ch02** `f792f3d4…` sin cambio; rápida 55.
- **Amplia:** 1053 passed + 4 failed, las 4 previas. La cuenta: 1039 de la Parte A + 15 de `test_module_f53b_cadena.py` − 1 test de Veo borrado = 1053.
- **Tests de F53b** (f53b, costo, video_prompt, cadena) más f50b, qa_studio y veo_supplementals: 87 passed. `mapa_modulos.py --check`: 158 · 0 fallas.
- **Gasto de F53b en `cost_history`** desde 15:02:37: `f53b_seco_g` 0,065 + `f53b_seco_k` 0,0392 + `f53b_clip_real` 1,2327 = **1,3369**. Los 2 registros de `ba6c3cac` por US$ 0 son el candado ch02.

## Lo que queda abierto (Parte B)
1. **PARADA B.**
2. **`lab/hyperframes/f50/veo_prueba.py` está roto**, porque usa `_call_veo_once`, `track_fal` y `fal_video_model`. Estaba permitido.
3. **El costo real** de los 1,20 de G se confirma en el panel de fal.
4. **La cadena todavía no pasó a K en una corrida real.** El clip real fue G sin rechazo, y K solo se probó en seco (el prompt) y simulado (los tests). Probarlo de verdad con una foto oscura costaría ≈ US$ 1,92 más un prompt.
5. **`qa_studio_server._clipfix_core`** llama a `_generate_clip(first_frame, video_prompt, out_clip)` sin `image_prompt` ni `ancla`, así que Opus recibe «(none)» en los dos. Cambiar esa llamada para pasarlos sería más que la línea que pide el handoff.
6. **Heredado de Veo, sin cambios** (lo vio el subagente de los tests):
   - si fal ya generó el clip y falla la bajada del mp4, el reintento vuelve a pedirlo, fal puede cobrar 2 veces y `track_video` registra 1;
   - un timeout de la cola (600 s) entra como transitorio y se reintenta hasta 3 veces.
7. **`config.py` está fuera de git**, así que sus cambios (`video_engines`, `video_resolution`, el borrado de `fal_video_model`, `fal_veo_resolution` y `fal_per_clip`, y las estimaciones) viven solo en este disco. Otra máquina con un `config.py` viejo sin `video_engines` rompe `_generate_clip`.
8. **No se renombra el concepto «veo»** (`veo_position`, `_process_veo_chapter`, `VEO_CLIP_DURATION_SEC`, `generate_veo_fn`, la clave `veo_config`).
9. **El digest del mapa** (`lab/mapa/hechos.json`, `lab/mapa/stickers/_partes/*`) todavía nombra las funciones borradas. Los stickers vivos y el `--check` están al día; el digest se refresca en la próxima pasada del structure-auditor.

## Veredicto de revisor-handoff (Parte B)
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | `_generate_clip` con cadena G→K, rechazo pasa a K sin suavizar, red/429/5xx reintenta el mismo motor | OK | `asset_manager.py` `_generate_clip`: `ContentRejectedError` hace `break` al siguiente motor. Los transitorios reintentan con `attempt` hasta 3 y luego hacen `raise`, sin saltar a K. Tests `test_g_rechaza_k_lo_hace`, `test_g_lo_hace_k_no_se_llama`, `test_504_una_vez_reintenta_g`, `test_504_persistente_levanta_sin_k` y `test_los_dos_rechazan` |
| 2 | Veo borrado con sus tests, `track_fal` y `fal_per_clip` | OK | grep en código de producción: cero resultados de `_call_veo_once`, `_generate_veo_clip`, `_veo_duration`, `VEO_*` viejos, `track_fal`, `fal_per_clip`, `fal_video_model` y `fal_veo_resolution`. Solo quedan en `lab/mapa/hechos.json`, `lab/mapa/stickers/_partes/*` y notas (ver Riesgos). El test de f50b se borró (`test_module_f50b.py` -23 líneas). `test_sin_veo_en_asset_manager` y `test_sin_track_fal_en_cost_tracker` lo fijan |
| 3 | `qa_studio_server` l. 1060 apunta a `_generate_clip` | OK | `qa_studio_server.py:1060`, una sola línea cambiada |
| 4 | `config.py` con `video_engines = ("gemini_omni_flash","kling_4")` y `video_resolution="1080p"` | OK | `config.py:75-76`. El archivo está en `.gitignore`: el cambio vive solo en disco |
| 5 | Agregado 1: el 8 a mano pasa a la constante de duración, con import perezoso | OK | `config.py:228-229` y `254-255` importan `VEO_CLIP_DURATION_SEC` dentro del método y llaman a `PERFIL_VIDEO_G.costo(...)` |
| 6 | Agregado 2: seco de K sobre `cap01.png`, 1 llamada a Opus, sin clip, prompt entero | OK | `seco_k.py:40-42` usa `PERFIL_VIDEO_K` con el `image_prompt`, el ancla y el `video_prompt` de `seco_g.json`. `SECO_K.md` tiene el prompt de 299 palabras. Costo US$ 0,0392 |
| 7 | Test con fal simulado: G rechaza → K; G hace → K no se llama; 504 reintenta G | OK | `test_module_f53b_cadena.py`, 15 tests. Corrí los 87 tests de la lista y pasaron (87 passed) |
| 8 | 1 clip real del cap 7 con G a 1080p, ffprobe, costo contra la tabla | OK | `ffprobe` de `clip/cap07_clip_01.mp4`: 1920×1080, 8,000 s, sin stream de audio. `clip_real.json`: motor G, sin rechazos, US$ 1,20 = 0,15×8. El total de la corrida es 1,2327 con el Opus de 0,0327 |
| 9 | Sin reglas nuevas en PEDIDO ni en las fichas; Veo sin renombrar | OK | `git diff e5f6f98 HEAD` sobre `script_engine/`, `engine_profiles.py`, `lab/hyperframes/f52/` y `DECISIONES.md`: vacío. Los nombres `veo_position`, `_process_veo_chapter`, `VEO_CLIP_DURATION_SEC` y `veo_config` siguen igual |
| 10 | Tope de US$ 3 | OK | `lab/TOPE_TANDA.json` = 3,0. Gasto de F53b: 0,065 + 0,0392 + 1,2327 = 1,3369 (cifra del reporte; no la recalculé desde `cost_history.json`) |
| 11 | Suites y ch02 | PARCIAL | El reporte da ch02 `f792f3d4…`, rápida 55 y amplia 1053 passed + 4 failed. Corrí `mapa_modulos.py --check`: 158 archivos, 0 fallas. Volví a correr `test_module_m03_merge_timing.py`: falla en `test_c_guarda_de_minimo` y `test_c_veo_path_y_veo_anchor_intacto`, que el reporte ya cita como fallas previas (no probé con `git stash`). No re-corrí la suite amplia ni el candado de ch02 |
| 12 | Reporte con mapa antes→después, log del clip, prompt de K, abiertos y veredicto | PARCIAL | La sección «Parte B» de `F53b_REPORT.md` tiene abiertos, suites y gasto. Falta el veredicto: queda `{{VEREDICTO_B}}`. El reporte sigue sin commit |
| 13 | ESTADO actualizado | FALLA | `lab/ESTADO_SESION.md` no está modificado desde e5f6f98 (Parte A). Su encabezado dice «PARADA A» y no registra la Parte B ni la PARADA B |

Decisiones de CC:
- **`narration_anchor` en `fase2a.py`:** justificada, porque sin el campo el ancla llega vacía a Opus. El archivo estaba fuera de la lista de módulos del handoff, pero está declarado y el cambio es de 2 líneas.
- **`papel.py` arreglado:** razonable. Solo reemplaza las líneas del clip por motores y duración, y no toca otras.
- **Guarda de mp4 sin video:** razonable. Es una validación nueva de `_call_clip_once` que no cambia lo que se genera.
- **Clip real con la cadena limitada a G por el tope:** aceptable. El costo de K en una foto oscura no se probó en real, solo simulado y en seco, y el reporte lo declara como abierto 4.

Fuera de alcance: ninguno en código. Los archivos tocados están dentro de lo declarado. `fase2a.py` y `papel.py` no estaban en la lista del handoff, pero son las decisiones declaradas arriba.

Riesgos que el contrato no cubre:
- `config.py` está fuera de git. Una máquina con un `config.py` viejo, sin `video_engines`, rompe `_generate_clip`.
- `_clipfix_core` llama a `_generate_clip` sin `image_prompt` ni `ancla`, así que Opus recibe «(none)» en los dos. Además, si falla la bajada del mp4 después de que fal ya generó el clip, el reintento puede cobrar dos veces y `track_video` registra una.
- `lab/mapa/hechos.json` y `lab/mapa/stickers/_partes/*` todavía nombran funciones borradas (`_generate_veo_clip`, `track_fal`, `fal_video_model`), aunque `mapa_modulos.py --check` da 0 fallas. El costo real de los 1,20 de G falta confirmarlo en el panel de fal.

### Adenda de CC (después del veredicto)
- **#13, ESTADO:** se actualiza en el commit de cierre, junto con este veredicto, como en todas las tandas. El revisor revisó antes del cierre.
- **#10, gasto:** recalculado desde `cost_history.json` (registros desde 15:02:37): `f53b_seco_g` 0,065, `f53b_seco_k` 0,0392 y `f53b_clip_real` 1,2327, que suman 1,3369. Hay 2 registros más de `ba6c3cac` por US$ 0, que son del candado ch02.
- **Riesgo 3, `hechos.json` y `_partes/`:** son el digest del structure-auditor, lo que alimenta los stickers. Los stickers vivos ya están al día y el `--check` da 0. El digest se refresca en la próxima pasada del mapa; queda en abiertos.
