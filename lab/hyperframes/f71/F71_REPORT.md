# F71 — las fotos siguen a la voz (anclas) + chascada del falso «nsfw»

Handoff: `lab/hyperframes/f71/HANDOFF_F71.md` (md5 b7c72cedf51815ed3e1bbfb5b8f29258). Sin llamadas pagas ni prompts; no corrió fase2b, run_pipeline ni la voz.

## Resultado

**Los 7 caps de Wittenoom ya siguen a la voz: 97 de 97 anclas por trigrama, 0 por fallback.** QA da `sync_approx` False en los 7 y Orleans no cambia. El rechazo falso por «nsfw» ya no se dispara.

**Dos cosas para decidir** (no las cambié: el handoff dice que el matcher no cambia y el camino del error de clip se reporta sin tocar):

1. **Un ancla cae 2,16 s antes: `ch07` #6.** El ancla «En 2026, el pueblo Banjima…» da la aguja `en dos mil`, que ya aparece justo antes en «murió de mesotelioma en dos mil veinticuatro». La foto entra en 29,72 s y le corresponde 31,88 s. Comparé 8 tokens en las 97 anclas (`falsos_trigrama.py`): es la única que cae en un lugar equivocado. Puede repetirse en cualquier video con años, porque los años hablados comparten sus primeras 3 palabras.
2. **Un error de clip que no es rechazo ahora no pasa a Kling** (ver Etapa B). El caso de ch01 en F69 hoy daría error en vez de ir a Kling, y en una corrida del pipeline el clip se reemplazaría por una foto.

## Etapa A — anclas

`anchor_timing.py` arma la aguja como en el handoff: ubica el ancla en `narration_original`, re-aplica los spans y aplica `normalize_pool_forms`. Si el ancla no está literal, aplica los spans a su texto. Sin normalizado, `normalize_for_tts`. La escalera y el cursor no cambian.

| Cap | Anclas | Antes | Después | Por trigrama | Por fallback | Literales | Por paso 2 |
|---|---|---|---|---|---|---|---|
| ch01 | 8 | OK | OK | 8 | 0 | 8 | 0 |
| ch02 | 15 | None | OK | 15 | 0 | 14 | 1 |
| ch03 | 16 | None | OK | 16 | 0 | 16 | 0 |
| ch04 | 14 | OK | OK | 14 | 0 | 14 | 0 |
| ch05 | 16 | None | OK | 16 | 0 | 16 | 0 |
| ch06 | 16 | None | OK | 16 | 0 | 15 | 1 |
| ch07 | 12 | None | OK | 12 | 0 | 11 | 1 |

- **Por paso 2 son 3, no 2 como en el handoff:** la simulación probaba además con los primeros 40 caracteres del ancla. El handoff pide pasar directo al paso 2, y así quedó. Las 3 emparejan.
- **Rearmar el texto da lo que leyó la voz:** spans + `normalize_pool_forms` reproducen `narration_normalized` idéntico en los 7 caps.
- **QA:** `sync_approx` False en los 7.
- **`fase2b._compute_durations_from_anchors`** (la función, sin correr fase2b) da duraciones en los 7, con mínimo 2,16 s y máximo 19,02 s. El mínimo de 2,16 s es el de `ch07` #5, que se acorta por el falso de #6.
- **Orleans `ba6c3cac-…`:** no tiene normalizado, así que usa `normalize_for_tts`. Los 7 caps dan OK y los mismos starts antes y después.

El start y las 3 palabras del audio de cada ancla de ch02, ch03, ch05, ch06 y ch07 están en [SALIDA_A.md](SALIDA_A.md).

**Llamadores:** `fase2b.py:796`, `qa_studio_server.py` (3) y `script_engine/gfx_layer.py:143`. **Agregué** `gfx_layer.py:150`, que no estaba en la lista: es la misma función para los caps con clip, y sin él ch07 seguiría fallando. **No toqué** `m03_visual.py:1408` (`_reconcile_anchor_timing`): `script_engine/m03` no estaba en la lista y sigue con `normalize_for_tts`. Si se rearma m03 con audio ya grabado, puede caer en el mismo None de antes.

**Lo viejo:** `_needle_normalized` queda, porque es el paso 3. `diag_235_matcher_ba6c.py` no cambia ni se borra: lo importa, y Orleans (su único topic) no tiene normalizado, así que sigue siendo fiel al matcher.

## Etapa B — chascada

- `_is_content_rejection` quita el eco antes de buscar: claves `input` y strings `data:` si es JSON; `data:` y corridas base64 de 200 o más caracteres si no lo es.
- `no_media_generated` entra en `CONTENT_REJECTION_KEYWORDS`.
- El cuerpo completo de cada error de fal va a `output/<topic>/assets/_errores_fal/<ts>_<nombre>.json`. Puede pesar varios MB, porque trae las fotos que fal repite. Fuera de `output/` no guarda, y nunca rompe la llamada. Cubre clip, foto (cola y sync), secuencia y madres.

| Cuerpo sintético | Antes | Ahora |
|---|---|---|
| `invalid_request` + base64 con «nsfw» | rechazo | **no** |
| `content_policy_violation` | rechazo | rechazo |
| `no_media_generated` | rechazo solo por el «safety» del eco | rechazo |
| solo `safety_tolerance` en el input | rechazo | **no** |

**Qué camino toma hoy un error de clip que NO es rechazo (sin cambiarlo):**
1. `_fal_queue_poll` o `_call_clip_once` lo suben como `HTTPError` y `_generate_clip` lo atrapa.
2. **Reintenta el mismo motor solo si parece transitorio:** el texto tiene 429 o similar, 500, 502, 503, 504 o «timeout». Hasta `CLIP_MAX_ATTEMPTS_NON_REJECTION` intentos.
3. **Si no, falla sin pasar a Kling:** Kling solo entra por `ContentRejectedError`.
4. **Quién lo recibe:**
   - **Pipeline** (`_process_veo_chapter`): cae en `technical_fallback`, genera una foto con `_ensure_fallback_image` y el cap sale con foto en lugar de clip, sin frenar la corrida.
   - **QA** («rehacer foto» o «regenerar clip»): muestra el error y el mp4 viejo queda.

Esa búsqueda de 500/502/503/504 mira todo el texto del error, incluida la URL con el `request_id`, así que puede reintentar por azar. Es de antes de esta tanda.

## Tests

- **`test_module_f71.py`, 31 verdes sin red:** los 5 casos reales, «Maitland» en su primera aparición, ancla no literal, cap sin normalizado, los 7 caps de Wittenoom, los 4 cuerpos y el guardado.
- **Suite amplia** (los `pytest` de `verificar.sh`, sin red): 1480 verdes, 30 saltados, 3 xfailed y 5 fallas.
  - **2 previas:** `m03_merge_timing` (×2), conocidas desde F41.
  - **2 eran el mapa viejo:** `f33` y `f42_mapa`. Con los stickers al día, pasan.
  - **1 no es de F71:** `test_f51c_corte_veo_real_de_wittenoom[1-start…]` lee una narración congelada (`lab/hyperframes/f54/antes/01b_narration.json`) que no termina como espera el test, y solo usa `m03._carve_veo_zones`, que F71 no toca. No la corrí sobre el commit anterior para confirmarlo.
- **No corrí** la parte de `verificar.sh` que lanza `fase2b.py` (el md5 de ch02), porque la tanda lo prohíbe. Tampoco `test_module_gfx_lab.py`, que escribe en disco real. `test_module_f58` reescribe `pedido_paquetes_wittenoom.txt`: lo restauré a como estaba.

Costo: US$ 0.

## Veredicto de revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

Recalculé por mi cuenta y los números del reporte coinciden. Hay 3 puntos abiertos: el falso de ch07 #6, que el error de clip que no es rechazo ya no pasa a Kling, y que m03_visual.py:1408 sigue con la aguja vieja. Ninguno es falla del contrato. Los dos primeros ya están declarados en el reporte.

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Aguja desde `01b_narration_normalized.json` (ubicar ancla, re-aplicar spans más largo primero y primera aparición, offset, `normalize_pool_forms`) | OK | anchor_timing.py `_agujas_de_voz`. Comparé las 97 anclas contra un replay propio de `sim_analista_replay.py`: 0 diferencias en las literales. Las 2 distintas (ch06 #9, ch07 #12) son las no literales, que la simulación dejaba en None. El offset es equivalente: un offset dentro de un span cae al inicio del reemplazo. |
| 2 | Ancla no literal: spans sobre su texto. Cap sin normalizado: `normalize_for_tts`. Helper `cargar_normalizado` | OK | Ramas `else` y `narr_norm` None en anchor_timing.py; `cargar_normalizado` usa el mismo criterio que `audio_manager._resolve_text_for_tts`. |
| 3 | Llamadores pasan `narr_norm` | OK | fase2b.py:796, qa_studio_server.py:325/399/465, gfx_layer.py:143 y 150. |
| 4 | Tests: 5 casos reales, Maitland, ancla no literal, cap sin normalizado, los 4 cuerpos | OK | Corrí `test_module_f71.py`, `test_qa_studio.py`, `test_module_135e_matcher.py` y `test_module_f42_mapa.py`: 78 pasan, sin red. También pasan f53, f60, f68 y f69 (109 y 53). |
| 5 | Tabla por cap; start y 3 palabras de ch02/03/05/06/07; `sync_approx` False en los 7; Orleans | OK | Corrí `salida_a.py` sobre una copia con el venv: da idéntico a `SALIDA_A.md`. Las 3 palabras del audio corresponden al ancla en todas las filas. En años solo se oye «en mil novecientos», que no distingue el año. Texto rearmado idéntico a `narration_normalized` en los 7 caps. Orleans: 7 caps OK, mismos starts antes y después. |
| 6 | Otros trigramas falsos | OK, con una excepción | `falsos_trigrama.py` da 97 anclas y 1 falsa: ch07 #6 («En 2026…» cae en 29,72 s y debería caer en 31,88 s, 2,16 s antes). Es real y está declarado. El ancla anterior (ch07 #5) queda acortada por ese falso. No hay otros: la comprobación de 8 tokens cubre los años repetidos de ch03 y ch05. |
| 7 | Etapa B: `_is_content_rejection` sin eco del input; `no_media_generated` en las palabras clave; cuerpos guardados en `_errores_fal/` | OK | asset_manager.py: `_sin_eco_del_input`, el keyword nuevo y `_guardar_error_fal`. Los 4 cuerpos dan lo esperado. Pasé casos de borde: `detail` como string da rechazo; texto no JSON con `type` da rechazo; `ctx.input` con «safety» ya no dispara. |
| 8 | No se perdió un rechazo real | OK | Revisé todos los usos: asset_manager 228, 523, 619, 666, 840, 847, 908, 1245 y foto_madre 124, 333. Todos reciben `e.response.text` o `json.dumps(data)`, es decir JSON. En el cuerpo real de fal (`lab/_nb_tol6/REPORTE.md`) `msg` y `type` están en el elemento de `detail`, antes de `input`, no dentro. Límite: un texto no JSON con prefijo, tipo `"HTTPError "+json`, no se limpia de `input` y puede seguir dando falso rechazo por `safety_tolerance`. Hoy ningún camino pasa eso. |
| 9 | `_generar_nb2` / F68 igual | OK | `_motivo_rechazo` (por `type`) no se tocó. Solo se agregó el guardado en `_llamada_cola`. Los tests de f68 pasan. |
| 10 | Thread-local `_destino_error` | OK, con observaciones | Todo poll (`_flux_poll`, `_fal_queue_poll`) lo ejecuta una función que fijó el destino antes, en el mismo hilo (`_generate_image_raw`, `_call_clip_once`, `_llamar_secuencia`, las 2 madres, `_llamada_cola`). No encontré un camino que guarde en el topic equivocado. El valor nunca se limpia, así que un poll futuro sin fijarlo heredaría un destino viejo. Fuera de `output/` o ante error no guarda ni rompe. Si el error no trae cuerpo JSON (por ejemplo `str(e)`), el archivo se llama `.json` pero tiene texto plano. Los archivos pueden pesar varios MB y no hay limpieza. Hoy no existe ningún `_errores_fal` en `output/`. |
| 11 | Camino de error de clip que no es rechazo (sin cambiarlo) | OK | El reporte coincide con el código. En `_generate_clip` (asset_manager.py:1006-1017) se reintenta el mismo motor si el texto trae 429, 500, 502, 503, 504 o «timeout», hasta 3 intentos. Si no, hace `raise` y no pasa a Kling, que solo entra por `ContentRejectedError`. En `_process_veo_chapter` (:1822) cae en `technical_fallback` y el cap sale con foto. En `_clipfix_core` (:1320) y `_fotoclip_core` (:1471) devuelve `False` con el mensaje. El mp4 viejo queda, porque `_backup` copia y no mueve. |
| 12 | Lo viejo se borra; `diag_235` | OK | `_needle_normalized` sigue en uso como paso 3, por lo que no se borra. `diag_235_matcher_ba6c.py` no cambia: lo importa, y Orleans no tiene normalizado, así que usa el mismo camino que antes. |
| 13 | Suite amplia verde salvo previas | OK | `suite/amplia.log`: 1480 pasan y 5 fallan. `m03_merge_timing` ×2 son previas (ESTADO_SESION:42). `f33` y `f42_mapa` eran el mapa viejo y hoy pasan (corrí f42). La que queda es `test_f51c_corte_veo_real_de_wittenoom[1-start]`: **no es de F71**. Lee `lab/hyperframes/f54/antes/01b_narration.json`, que git no muestra modificado, y `output/audio/<T>/sync_map.json`. Usa solo `m03._carve_veo_zones`, que F71 no tocó. La frase del cap 1 que lee no termina en «paredes de chapa.», así que la narración congelada no coincide con lo que espera el test. No corrí el commit anterior para confirmarlo. |
| 14 | DECISIONES 16:19 | OK | DECISIONES.md, +1 línea. |
| 15 | Una línea en ESTADO_SESION | No es falla | Sin modificar todavía; queda para el commit, como indicaste. |
| 16 | `pedido_paquetes_wittenoom.txt` igual que al empezar | NO VERIFICABLE | Hoy `git diff --stat` da 15 insertadas y 25 borradas contra HEAD, con mtime 16:37 de hoy. El archivo se tocó durante la tanda: el reporte dice que `test_module_f58` lo reescribe y que lo restauró. No tengo una copia del estado inicial para comparar. Si Omar tiene el diff del arranque, hay que contrastarlo. |

Preguntas puntuales:
- **`m03_visual.py:1408` sin `narr_norm`.** Es un riesgo real pero acotado. Solo afecta si se rearma m03 con audio ya grabado. El matcher devuelve None, no fusiona anclas apretadas y avisa con `[audit]`. Es el mismo comportamiento de antes y fase2b igual reparte bien. El costo es que una ancla chica como ch07 #5 no se fusione. No es bloqueante.
- **`gfx_layer.py:150`.** Está justificado. Es la rama `veo` de `build_scenes` con `supplemental_anchors`. Sin el cambio, un cap con clip cuyas anclas llevan año (por ejemplo ch07) caería en `single` sin avisar, porque el `except` lo traga.

Fuera de alcance: `diag_234_cap4.py` (cambia `TOPIC`; mtime del 29-oct, anterior a F71, no figura en la evidencia de F71) y `lab/hyperframes/f28/a/f28a.log` (mtime del 29-oct). Ambos son previos a la tanda. Lo demás tocado está en alcance: anchor_timing, asset_manager, foto_madre, fase2b, qa_studio_server, gfx_layer, DECISIONES, stickers y MAPA, que solo refresca md5, texto F71 y commit. Los archivos nuevos son `test_module_f71.py` y `lab/hyperframes/f71/`.

Riesgos que el contrato no cubre:
1. Cualquier video con años hablados puede repetir el falso de ch07 #6: los años comparten sus primeras 3 palabras y el matcher no desempata. Las fotos entrarían antes.
2. `_errores_fal` guarda cuerpos de varios MB sin límite ni limpieza, y el nombre `.json` puede contener texto plano.
3. El reintento por «500/502/503/504» busca en todo el texto del error, incluida la URL con el `request_id`. Puede reintentar por casualidad (esto es anterior a F71).

**Adenda mía, posterior al veredicto:**
- **Requisito 16:** guardé una copia de `pedido_paquetes_wittenoom.txt` antes de correr la suite, y el archivo quedó byte a byte igual. El archivo no entra al commit.
- Ajusté el texto de la falla de `f51c` en «Tests» con lo que encontró el revisor. Ningún resultado cambió.
