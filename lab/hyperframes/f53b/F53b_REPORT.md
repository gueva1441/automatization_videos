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
