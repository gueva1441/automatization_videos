# HANDOFF F60 · Etapa 0b — secuencia por la cola de fal + madre con ropa limpia (solo lab)

Rama `f11-guion-v4` (main no se toca). Topic Wittenoom `123bbb64-9fca-4395-8bf4-57d60e219ef1`, **sobre la copia de lab que ya existe** (`lab/hyperframes/f60/base/`; no se rehace). Producción NO se toca (ni `asset_manager.py`, ni `foto_madre.py`, ni m03/m06/QA). Subagentes en paralelo donde se pueda. `revisor-handoff` al final; veredicto íntegro en `lab/hyperframes/f60/F60_REPORT.md` (sección nueva «Etapa 0b»). Sin tope de dólares: el costo se reporta después.

Módulos tocados: ninguno de producción. Solo un runner nuevo de lab `lab/hyperframes/f60/etapa0b_secuencia.py` (copia de `etapa0_secuencia.py` con los 4 cambios de abajo). `etapa0_secuencia.py` y la carpeta `e0/` quedan como están (registro de la Etapa 0; `e0/` tiene `madre_daniel_ecija.png` y `lote2/` con 3 fotos; NO hay `e0/lote1`). Del código de producción solo se IMPORTA (`asset_manager._clip_poll`, `asset_manager._fal_headers`, `asset_manager.FLUX_MAX_WORKERS`, `api` de config); importar no lo modifica; si un import falla, PARÁ, no se parchea.

## Por qué
Etapa 0 (commit `2eadb52`): el lote de 6 fotos se cortó a los 240 s (`requests.post(..., timeout=240)` contra `fal.run`, síncrono) sin devolver nada y fal probablemente lo cobró (US$ 0,21); 3 fotos tardaron 142,5 s (≈ 47,5 s/foto → 6 ≈ 285 s). Además la madre salió con camisa de trabajo manchada (el prompt no pedía ropa; «miner» la sugirió) y esa ropa se arrastró a las 3 fotos, incluida Madrid 1966. Manchas en la ropa son lo que hizo rechazar clips en F59 B3.

## Decisiones (anotar en `DECISIONES.md` tal cual, CRLF como el resto)
- 2026-10-30 17:48 · **F60 0b:** la llamada de secuencia va por la cola de fal (`queue.fal.run`: pedir → `request_id` guardado en disco al instante → esperar con poll), no por `fal.run` síncrono; límite de espera = `CLIP_POLL_TIMEOUT` (600 s, existente desde F53b); si la espera se corta, el resultado se recupera después con el `request_id` en vez de perderse · Omar · F60
- 2026-10-30 17:48 · **F60 0b:** la foto madre de una persona lleva ropa neutra y limpia fija en el prompt (la ropa de cada escena la pone la escena); se repiten los lotes 6+3 de Daniel con la madre nueva antes de la Etapa A · Omar · F60

## Constantes
| valor | origen | quién |
|---|---|---|
| fotos por llamada = 6 | handoff F60 (prueba de Omar en fal) | Omar |
| espera máxima de un lote = `CLIP_POLL_TIMEOUT` (600 s) | existente, asset_manager.py:67 (F53b). Con 47,5 s/foto medido, cubre hasta ≈ 12 fotos | existente |
| intervalo de poll 5 s, timeouts HTTP 15/30 s | existentes dentro de `_clip_poll` (asset_manager.py:568) | existente |
| lotes en paralelo = todos a la vez (2), tope `FLUX_MAX_WORKERS` (20) | existente, asset_manager.py:65; regla de Omar: máximo paralelo | existente / Omar |
| frase de ropa de la madre = `wearing a plain, clean, light-coloured shirt` | analista, OK de Omar 17:48 (B: «ropa neutra y limpia fija»). Genérica, no depende del tema | analista / Omar |
| año 1962, `ESTILO_C`, `NO_TEXT`, aspecto del grupo, `image_size` 2560×1440, `sequential_image_generation="auto"`, `num_images=1` | los mismos de la Etapa 0 (SALIDA_0 §0.2–0.3) | existente |

Cualquier otro número: PARÁ y preguntá.

## Los 4 cambios del runner (y nada más)
1. **Cola en vez de síncrono.** Modelos: madre = `model_t2i` (= `prof.render.model_id`, el mismo de la Etapa 0); lotes = `model_edit` (= `model_t2i.replace("text-to-image", "edit")`, ídem). Submit con `requests.post(f"{api.fal_base_url}/{model}", headers=asset_manager._fal_headers(), json=payload, timeout=60)` (`api.fal_base_url` = `https://queue.fal.run`, config.py:77), igual que `_call_clip_once` (asset_manager.py ~l.632). Apenas vuelve el submit, escribir `request_id`, `status_url`, `response_url` y la hora en `etapa0b_pedidos.json` (antes de esperar). `status_url` y `response_url` se usan tal como los devuelve el submit (no se arman a mano: con subruta `/edit` no coinciden). Esperar con `asset_manager._clip_poll(status_url, response_url)` (se importa y se usa tal cual; NO se copia ni se edita). Si el submit ya trae `"images"`, usarlo. Vale para la madre y para los 2 lotes.
   **Sin pedidos duplicados:** al arrancar, si `e0b/etapa0b_pedidos.json` ya tiene un `request_id` para esa llamada (madre / lote 1 / lote 2), NO se vuelve a pedir: se hace poll de ese mismo `status_url`/`response_url`. Si hubiera que re-pedir la madre, los lotes quedan inválidos: PARÁ.
2. **Orden y paralelo.** Primero la madre, sola. Con la madre ya guardada en disco, los 2 lotes se piden a la vez (`ThreadPoolExecutor(max_workers=min(len(lotes), asset_manager.FLUX_MAX_WORKERS))`). Se mide, por llamada, segundos desde el submit hasta que vuelve `_clip_poll` (incluye la cola y el GET de la respuesta), y el tiempo total de pared de los 2 lotes. Nota: los 600 s de `_clip_poll` cuentan también el tiempo en cola.
3. **Madre nueva.** Mismo prompt que la Etapa 0 con la frase de ropa insertada tras el sujeto. Cambio mínimo sobre la línea existente (etapa0_secuencia.py:133): `{canon_sin}.` → `{canon_sin}, {ROPA_MADRE}.` con `ROPA_MADRE = "wearing a plain, clean, light-coloured shirt"` (sin punto final); el resto de la línea no se toca. Prompt exacto que tiene que salir (comparar byte a byte y pegarlo):
   ```
   Head-and-shoulders portrait of a young adult Spanish migrant miner, wearing a plain, clean, light-coloured shirt. Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes. Neutral expression, facing the camera, plain mid-grey background, soft even light. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight underexposure, in a dark-history realist style. No readable text, no signage, no labels.
   ```
   `canon_sin` sigue siendo el recorte de la Etapa 0 («a young adult Spanish migrant miner»). La palabra «miner» se queda en esta prueba (sacar el oficio sin lista de palabras es tema de la Etapa B.1, que ya tiene su PARÁ).
   Los lotes: las mismas 9 fotos, mismo orden, mismo armado del prompt de secuencia que la Etapa 0 (lote 1 = 6, lote 2 = 3); solo cambia la madre: `image_urls=[data-uri del archivo de la madre nueva]` (data-uri del archivo bajado, como en la Etapa 0; NO la URL del CDN de fal).
4. **Salidas en carpeta nueva.** Todo en `lab/hyperframes/f60/e0b/` (`madre_daniel_ecija.png`, `lote1/`, `lote2/`, `etapa0b_pedidos.json`, `etapa0b.json`, `etapa0b.log`); `e0/` no se toca.

## Recuperar el lote 1 de la Etapa 0
No se puede: fue síncrono y no devolvió `request_id`. No intentar. (El gasto probable de US$ 0,21 queda como está.)

## Qué pegar en `SALIDA_0b.md` (PARADA 0b)
1. Prompt de la madre (byte a byte contra el de arriba: igual / diferente) y la foto; ¿qué ropa trae? (¿limpia, sin manchas?). `has_nsfw_concepts` de la madre.
2. Por lote: pedidas / devueltas, `request_id`, segundos submit→vuelta de `_clip_poll`, segundos por foto, seed, `has_nsfw_concepts` por foto, US$ (precio real de fal × devueltas, como en la Etapa 0). Tiempo total de pared de los 2 lotes en paralelo.
3. Tabla por foto (las 9) con 2 miradas (CC + subagente independiente: recibe SOLO la madre nueva, las fotos de `e0b/` y el prompt de cada escena; ni la hoja ni nada de `e0/`), cada una:
   | foto | ¿es la escena pedida? (sí / parcial / no + qué falta) | cara de la madre visible (1–10 o «de espaldas») | contagio (cuántas caras-madre de más) | ropa: ¿la de la escena o la de la madre? | anacronismos a la vista |
4. Comparación con la Etapa 0 en las 3 fotos repetidas del lote 2 (ch04_img_09, ch04_img_14, ch05_img_05): ¿desapareció el arrastre de las manchas?
5. Hoja `e0b/hoja_madre_0b.jpg`: madre nueva arriba (y la madre de la Etapa 0 al lado); por fila foto 0b | foto de la Etapa 0 del mismo slot. Solo existen las 3 de `e0/lote2/` (ch04_img_09, ch04_img_14, ch05_img_05); las 6 del lote 1 van con la celda vacía.
6. Gasto total: madre + lotes, precio real de fal × devueltas por endpoint.
7. «Lo que queda abierto» completo.

Reglas fijas:
- Errores, sin reintento en ninguno: `TimeoutError` → dejar el `request_id` en el reporte y PARÁ; rechazo por contenido (`ContentRejectedError`) → texto literal y PARÁ; `RuntimeError` (FAILED/ERROR) o submit que no devuelve 2xx → texto literal y PARÁ.
- Git: commit en `f11-guion-v4` con paths explícitos: `lab/hyperframes/f60/etapa0b_secuencia.py`, `lab/hyperframes/f60/HANDOFF_F60_0b_cola_y_madre_limpia.md`, `lab/hyperframes/f60/e0b/etapa0b_pedidos.json`, `lab/hyperframes/f60/e0b/etapa0b.json`, `lab/hyperframes/f60/e0b/etapa0b.log`, `lab/hyperframes/f60/SALIDA_0b.md`, `lab/hyperframes/f60/F60_REPORT.md`, `DECISIONES.md` (raíz del repo), `lab/ESTADO_SESION.md`. Imágenes y hojas fuera de git. Push a `origin f11-guion-v4` como en las tandas anteriores; `main` no se toca.

PARADA 0b. No se pasa a la Etapa A sin OK del analista y de Omar.
