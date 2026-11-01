# LAB NB-AHORCADO — reporte

## Lectura

**Pasaron 5 de 21: las 5 son de `nb2_lite`. `nb2` no pasó ninguna, ni a 1K ni a 2K.** A2 (el minero en el galpón) no pasó en ningún modelo: 0 de 7.

- **A1 es el mismo texto que P1 de NB-TOL6, y el resultado se invirtió.** Allá, con una corrida por modelo, pasó `nb2` y se bloqueó el lite; acá el lite pasa 2 de 3 y `nb2` 0 de 4. Una sola corrida no sirve para elegir motor: el filtro varía de una llamada a otra, y 3 corridas tampoco alcanzan para dar un porcentaje.
- **El lite no es seguro para estos temas:** en A1, la misma foto pasó 2 veces y se bloqueó 1. En producción, cada bloqueo manda la foto al respaldo Seedream 4.5; con 3 corridas no se puede decir cada cuánto.
- **A3 pasa 3 de 3 en el lite.** Es el ahorcado más lejano y en silueta. Las 2 fotos de A1 muestran horca, capucha y cuerpo colgado: no se ve censura suave en lo pedido. A1 sale en blanco y negro aunque el prompt pide «muted colors». La calidad la juzgan Omar y el analista.
- **2K:** no hay fotos para comparar; las 3 llamadas se bloquearon, igual que a 1K.

Límites: 21 llamadas lanzadas juntas en un lapso de 22 s; no sé si el filtro de fal se comporta distinto en otro momento. 1 de las 16 es `no_media_generated`, que no dice la causa (nb2_1K_A3_2).

`PROMPTS.json` md5 5bfd1e3cc633d62e4c9c742d896ee2ea, byte a byte. Text-to-image, sin referencia, 16:9, 1 imagen, `safety_tolerance` 6. OpenAPI vivo (2026-11-01): `google/nano-banana-2-lite` ['1', '2', '3', '4', '5', '6'] y `fal-ai/nano-banana-2` ['1', '2', '3', '4', '5', '6']: **6 sigue siendo el máximo**. Detalle por llamada: `resultados.json`; registro de cada pedido: `llamadas/`.

## Modelo × prompt (pasaron)

| Modelo y resolución | A1 horca en prisión | A2 minero en el galpón | A3 silueta en el árbol |
|---|---|---|---|
| nb2_lite 1K | 2/3 | 0/3 | 3/3 |
| nb2 1K | 0/3 | 0/3 | 0/3 |
| nb2 2K | 0/1 | 0/1 | 0/1 |

Resolución devuelta: `google/nano-banana-2-lite` → 1376x768.

## Mensajes de bloqueo y error, exactos

- **nb2_1K_A1_1** (BLOQUEADO), request_id `01a1989d-2f34-7bf1-85f5-db452d4b0344`: type `content_policy_violation` · msg `The content could not be processed because it contained material flagged by a content checker.` · categories `['model_moderated']`
- **nb2_1K_A1_2** (BLOQUEADO), request_id `01a1989d-2f35-7d22-b803-2d4839dacf72`: type `content_policy_violation` · msg `The content could not be processed because it contained material flagged by a content checker.` · categories `['model_moderated']`
- **nb2_1K_A1_3** (BLOQUEADO), request_id `01a1989d-2f48-7691-a973-cbc11255d85c`: type `content_policy_violation` · msg `The content could not be processed because it contained material flagged by a content checker.` · categories `['model_moderated']`
- **nb2_1K_A2_1** (BLOQUEADO), request_id `01a1989d-2f31-7ea1-bdd3-54c2bef774d4`: type `content_policy_violation` · msg `The content could not be processed because it contained material flagged by a content checker.` · categories `['model_moderated']`
- **nb2_1K_A2_2** (BLOQUEADO), request_id `01a1989d-2f36-7c11-a9cd-d9032829a073`: type `content_policy_violation` · msg `The content could not be processed because it contained material flagged by a content checker.` · categories `['model_moderated']`
- **nb2_1K_A2_3** (BLOQUEADO), request_id `01a1989d-2f4a-7551-98c8-fbaf9637ddb9`: type `content_policy_violation` · msg `The content could not be processed because it contained material flagged by a content checker.` · categories `['model_moderated']`
- **nb2_1K_A3_1** (BLOQUEADO), request_id `01a1989d-2f37-7362-bf9f-bed7c9013278`: type `content_policy_violation` · msg `The content could not be processed because it contained material flagged by a content checker.` · categories `['model_moderated']`
- **nb2_1K_A3_2** (BLOQUEADO), request_id `01a1989d-2f39-7613-a9b4-62c134f8a8b8`: type `no_media_generated` · msg `The model did not generate the expected output for this prompt. This may occur for several reasons, including unsafe content, a prompt that is incompatible with the selected media type (e.g., prompting an image model to generate audio), references to missing attachments, or other cases where the input cannot be processed as the requested output type. Please review your inputs and try again. If the issue persists, contact support.`
- **nb2_1K_A3_3** (BLOQUEADO), request_id `01a1989d-2f4a-79e1-986d-a5c2d682ce69`: type `content_policy_violation` · msg `The content could not be processed because it contained material flagged by a content checker.` · categories `['model_moderated']`
- **nb2_2K_A1_1** (BLOQUEADO), request_id `01a1989d-2f4a-73d3-b5ec-80ca2abc0f45`: type `content_policy_violation` · msg `The content could not be processed because it contained material flagged by a content checker.` · categories `['model_moderated']`
- **nb2_2K_A2_1** (BLOQUEADO), request_id `01a1989d-2f47-7640-b495-031f032ca196`: type `content_policy_violation` · msg `The content could not be processed because it contained material flagged by a content checker.` · categories `['model_moderated']`
- **nb2_2K_A3_1** (BLOQUEADO), request_id `01a1989d-2f37-7362-bf9f-bee19a5f5be5`: type `content_policy_violation` · msg `The content could not be processed because it contained material flagged by a content checker.` · categories `['model_moderated']`
- **nb2_lite_1K_A1_3** (BLOQUEADO), request_id `01a1989d-2f15-7642-8c89-346885317b4b`: type `content_policy_violation` · msg `The content could not be processed because it contained material flagged by a content checker.` · categories `['model_moderated']`
- **nb2_lite_1K_A2_1** (BLOQUEADO), request_id `01a1989d-2f22-73b0-89e5-cd17e6ac16e8`: type `content_policy_violation` · msg `The content could not be processed because it contained material flagged by a content checker.` · categories `['model_moderated']`
- **nb2_lite_1K_A2_2** (BLOQUEADO), request_id `01a1989d-2f16-7c23-9793-a624c49fca20`: type `content_policy_violation` · msg `The content could not be processed because it contained material flagged by a content checker.` · categories `['model_moderated']`
- **nb2_lite_1K_A2_3** (BLOQUEADO), request_id `01a1989d-2f16-7e61-bf54-e5e004dd2020`: type `content_policy_violation` · msg `The content could not be processed because it contained material flagged by a content checker.` · categories `['model_moderated']`

## Costo

**Total conocido: US$ 0.00** (0 fotos de nb2: las 12 llamadas de nb2 se bloquearon). No incluye las 5 fotos del lite, que no tienen número.

| Modelo | Costo por foto | Origen |
|---|---|---|
| nb2_lite (1K fija) | por tokens, sin medir | fal.ai/models/google/nano-banana-2-lite/llms.txt; fal no devuelve tokens |
| nb2 1K | US$ 0.08 | lista: api.fal.ai/v1/models/pricing (fal-ai/nano-banana-2: 0,08 por imagen) y fal.ai/models/fal-ai/nano-banana-2/llms.txt (2K = 1,5 veces el precio base) |
| nb2 2K | US$ 0.12 | lista: api.fal.ai/v1/models/pricing (fal-ai/nano-banana-2: 0,08 por imagen) y fal.ai/models/fal-ai/nano-banana-2/llms.txt (2K = 1,5 veces el precio base) |

API de uso de fal: `google/nano-banana-2-lite` → HTTP 403; `fal-ai/nano-banana-2` → HTTP 403. Se asume que una llamada bloqueada no cobra; no está verificado.

## Hojas de contacto

- `hoja_A1.png`
- `hoja_A2.png`
- `hoja_A3.png`

## Veredicto de revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | PROMPTS.json con md5 5bfd1e3c... | OK | `md5sum` = 5bfd1e3cc633d62e4c9c742d896ee2ea |
| 2 | Prompts byte a byte, parámetros pedidos | OK | Comparé el `texto` de las 21 `.llamada.json` contra PROMPTS.json (0 diferencias). Todas llevan aspect_ratio 16:9, safety_tolerance "6", num_images 1 y referencias_md5 vacío |
| 3 | Reutiliza cola y rechazos de producción, sin otra forma de llamar a fal | OK | `run_lab.py:98` usa `am._llamada_cola` y `:111` usa `am._motivo_rechazo`. Importa `asset_manager` y `tol6`. `git diff` de asset_manager.py y config.py está vacío |
| 4 | Máximo de safety_tolerance confirmado en OpenAPI vivo | OK | `resultados.json` guarda `openapi_vivo`: ambos endpoints ['1'..'6']. No lo reconsulté (necesita clave); queda como registro del lab |
| 5 | 21 llamadas: lite 1K 3×3, nb2 1K 3×3, nb2 2K 3×1 | OK | `resultados.json` tiene 21 entradas con los endpoints correctos. nb2 manda `resolution` 1K o 2K; el lite no manda resolución (fijo 1K, la ficha de fal lo dice) |
| 6 | Campos por llamada en resultados.json | PARCIAL | Están modelo, resolución pedida, prompt_id, corrida, request_id, estado, type, msg, segundos y resolución devuelta. El campo `costo_usd` es null en las 21, incluso en las 5 fotos del lite y en las 12 de nb2 bloqueadas. El precio de lista solo está en REPORTE. La resolución pedida del lite es un texto largo, no "1K" |
| 7 | Png de cada OK con nombre modelo_res_prompt_corrida | OK | 5 png `nb2_lite_1K_A1_1`, `A1_2`, `A3_1`, `A3_2`, `A3_3`, todos 1376x768 y de 1.4 a 1.6 MB. Coinciden con los 5 OK |
| 8 | Tabla modelo × prompt desde resultados.json | OK | Recalculé: lite 2/3, 0/3, 3/3. nb2 1K 0/3 en los tres prompts. nb2 2K 0/1 en los tres. Coincide con REPORTE líneas 18-22 |
| 9 | Mensajes de bloqueo exactos, sin el input repetido | OK | Los 16 de REPORTE coinciden con los `.llamada.json`. type y msg están textuales, sin `input`. Hay 15 `content_policy_violation` y 1 `no_media_generated` (nb2_1K_A3_2) |
| 10 | Costo con precio de lista citado | OK | Verifiqué en el llms.txt público de fal: nb2 US$0.08 por imagen y 2K a 1.5 veces, o sea 0.12. Lite por tokens, sin medir. El pricing API pidió clave y el REPORTE lo cita como fuente. El total US$0.00 es coherente, porque las 12 de nb2 se bloquearon, pero es un supuesto declarado como no verificado |
| 11 | Hojas A1, A2 y A3 rotuladas por modelo, resolución y corrida | OK | Las tres existen (1920x1200). Las miré: cada celda tiene rótulo y BLOQUEADO en rojo. A1 tiene 2 fotos del lite, A2 es todo bloqueado y A3 tiene 3 fotos del lite |
| 12 | «Lectura» se sostiene con los datos | OK | 5 de 21 pasaron, todas del lite. A2 pasa 0 de 7. nb2 en A1 pasa 0 de 4. Las 16 bloqueadas se reparten 12 de nb2 y 4 del lite. Los tiempos van de 3.5 s a 21.3 s, dentro del lapso de 22 s que cita |
| 13 | A1 = P1 de NB-TOL6 y resultados citados | OK | El texto de P1 en `lab/_nb_tol6/run_lab.py:68` coincide con el de A1. En `_nb_tol6/resultados.json`, `nb2_P1` fue OK y `nb2_lite_P1` BLOQUEADO. Es lo que dice la Lectura, y en TOL6 nb21, nbpro y nb_lite también se bloquearon |
| 14 | Reglas fijas: sin tocar producción, output/ ni main | OK | `git status` no muestra ningún versionado nuevo modificado. Solo `diag_234_cap4.py`, `f28a.log` y `pedido_paquetes_wittenoom.txt`, que ya estaban así. Lo nuevo está en lab/_nb_ahorcado/ |
| 15 | Veredicto en REPORTE, commit y línea de ESTADO | NO VERIFICABLE | Pendientes, como indicaste |

Observaciones menores:
- Los afirmados de la Lectura sobre calidad (A1 en blanco y negro pese a «muted colors», sin censura suave visible) son plausibles con las hojas. Una de las tres fotos de A3 tiene franjas negras arriba y abajo (corrida 3).
- «Se asume que una llamada bloqueada no cobra; no está verificado» está declarado en el REPORTE. La API de uso devolvió 403.

Fuera de alcance: ninguno.

Riesgos que el contrato no cubre:
- Las 21 llamadas salieron juntas, en 22 s. Un bloqueo de nb2 podría depender de la carga o del momento y no solo del contenido, y 3 corridas no separan las dos causas.
- Que nb2 bloquee todo aquí y haya dejado pasar P1 en TOL6 indica un filtro variable. Con n=3 no hay base para decidir motor.
- `no_media_generated` (nb2_1K_A3_2, 3.5 s) está contado como bloqueo sin que se sepa la causa.

**Adenda mía, posterior al veredicto:** por el requisito 6 agregué a cada llamada de `resultados.json` el campo `precio_lista_usd` (0,08 y 0,12 en nb2; «por tokens, sin medir» en el lite). `costo_usd` sigue en null porque ninguna llamada con precio de lista dio foto. Ningún resultado cambió y no hubo llamadas nuevas.
