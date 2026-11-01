# F69 — QA Studio: la foto de arranque del clip se puede rehacer

Handoff: `lab/hyperframes/f69/HANDOFF_F69.md` (md5 15344a3797d87be781a82b47e593af35).

## Resultado

**El botón funciona y el gancho quedó con Daniel solo.** La prueba real de ch01 con «solo Daniel, sin niños, sin borde de diapositiva» dio foto y clip sin niños y sin borde. Foto, final y clip nuevos ya están en producción.

**Para mirar:**
- **Costó US$ 2,15, no ≈ 1,30.** Gemini devolvió error y el clip salió por Kling 4.0 (US$ 1,89).
- **Ese salto pudo ser un falso rechazo.** Gemini respondió `invalid_request`: «Could not generate a video with the given inputs». No es un mensaje de contenido. `_is_content_rejection` busca palabras clave en todo el cuerpo, y fal repite ahí el prompt. No confirmé qué palabra coincidió. No lo toqué: `asset_manager.py` está fuera de esta tanda.
- **La ropa tiene manchas rojas grandes.** El tono es polvo del Pilbara, pero en camisa y pantalón puede leerse como sangre. No está en lo pedido: juzgalo vos.
- **La foto final cambia de pose:** mano en el pecho y sin la caja, mientras que la foto inicial tiene el pie sobre la caja. El clip va de una a la otra, y no lo vi en movimiento: solo el primer cuadro y las fotos.

## Qué cambió en el código

| Archivo | Cambio |
|---|---|
| `qa_studio_server.py` | El tile del clip trae `foto_img_name` y `foto_url`. `_fotoclip_core`: foto → final → clip → manifest → `_invalidate_baked`. `/fix_image` deriva `chNN_img_01.png` de un cap con clip a esa cadena |
| `qa_studio.html` | Miniatura, «✎ rehacer foto» y su panel, dentro del tile del clip |
| `test_module_f69.py` | Tests sin red con deps inyectadas |
| `lab/mapa/stickers/orquestador.json`, `lab/MAPA_PROYECTO.*` | Stickers y mapa de los 2 archivos |

`PEDIDO_EDITAR_CASILLEROS` y `PEDIDO_EDITAR_MOVIMIENTO` no cambian (`test_pedidos_byte_a_byte_con_el_handoff`). `asset_manager.py` y `script_engine/` no se tocaron. «Regenerar clip» sigue igual.

## Lecturas mías

1. **`_fix_image_core` es `_fix_core`,** el nombre real en el código.
2. **Los caps con clip guardan la foto en otra forma:** `image_prompt` (texto) + `image_f8`, sin lista `image_prompts`. `_fix_core` no la encontraba. `_foto_de_clip` la presenta como un ítem normal y `_guardar_foto_de_clip` la devuelve con las claves que usa m03.
3. **La foto va dentro del tile del clip, no como segmento propio.** No ocupa tiempo en el video y un segmento nuevo corría la línea de tiempo.
4. **Sin `_graded`:** producción no gradúa la foto del clip y el video usa el mp4.
5. **Respaldo extra:** también `_native` y `.llamada.json` de la foto y de la final, porque el motor los pisa.
6. **Si falla algo:** si la foto falla, no se toca nada más. Si el clip falla, queda la foto nueva con el mp4 viejo y el mensaje lo dice; el manifest no cambia.
7. **Filas del manifest:** además de `foto_arranque_md5`, se actualizan `foto_final_md5`, `image_prompt`, `video_prompt`, `ssim`, `clip_*` y los datos del motor de la foto. Si no, la fila quedaba contando la foto anterior.

## Prueba real (una sola)

Pedido: «solo Daniel, sin niños, sin borde de diapositiva». Respuesta del sistema:

> foto rehecha; casilleros editados: subject, action, lens_technique. El filtro de producción sacó: lens_technique: full-bleed image running edge to edge with no border or slide mount. Foto anclada a la madre de Daniel Écija (casillero persona: no cambia con el pedido). Foto final y clip rehechos (motor: kling_4).

| Casillero | Antes | Después |
|---|---|---|
| `subject` | A lean mid-20s Spanish miner … one foot wrapped in a thick white bandage | … one foot wrapped in a thick white bandage, **the only person in the frame** |
| `action` | Posing stiffly for a **family portrait**, the bandaged foot set forward on an upturned crate | Posing stiffly **alone for a solo portrait**, the bandaged foot set forward on an upturned crate, **the yard empty around him** |
| `lens_technique` | 50mm lens, moderate depth of field, **period box-camera framing** | 50mm lens, moderate depth of field |

| | Antes | Después |
|---|---|---|
| `ch01_img_01.png` | `5f3170e1…` | `8aa36439…` |
| `ch01_img_01_final.png` | `914e951b…` | `7f773837…` |
| `ch01_clip_01.mp4` | `77a6a80f…` | `5aa387cd…` (1920×1080, 8,04 s, sin audio) |
| `video_prompt` | el aprobado en tu «regenerar clip» de las 14:32 | **igual** |
| `papel_md5` | `39c99927…` | igual |

Lo viejo quedó en `assets/_qa_backups/*.20261101_153557.*`: foto, final, nativos, llamadas, mp4, 03_visual, guion y manifest. `ch01_hybrid_visual.mp4` ya no existe: fase2b lo rearma.

**Evidencia:** `antes_foto.png`, `despues_foto.png`, `antes_final.png`, `despues_final.png`, `antes_primer_cuadro.png`, `despues_primer_cuadro.png`, `prueba_real.json`.

**Pantalla:** la abrí en una instancia nueva (:8003). Se ven miniatura, botón y panel, sin errores de consola. Abrí el panel, pero no lo envié: la única corrida real fue por `prueba_real.py`, y la ruta está probada con un test aparte.

## Costo

| Paso | US$ |
|---|---|
| Opus, casilleros | 0,0149 |
| Nano Banana, foto | 0,042 (estimado) |
| Opus, instrucción de la final | 0,0352 |
| Nano Banana, final | 0,042 (estimado) |
| Opus, prompt de Gemini (rechazado) | 0,0574 |
| Opus, prompt de Kling | 0,0659 |
| Kling 4.0, 8,04 s | 1,8938 (tarifa del perfil) |
| **Total** | **2,1512** |

Es lo que registra el rastreador; el dato facturado está en el panel de fal. No sé si Gemini cobró el intento fallido: el rastreador no lo cuenta.

## Veredicto de revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

Corrí pytest sin red: 61 passed (test_module_f69.py + test_qa_studio.py). No lancé qa_studio ni hice llamadas pagas. El md5 del handoff coincide (15344a37...).

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | La foto de arranque es ítem de QA con miniatura y «rehacer foto» | OK | `_foto_clip_campos` en qa_studio_server.py (foto_img_name y foto_url dentro del tile del clip). qa_studio.html +46 líneas. No pude ver la pantalla: el reporte dice que la abrió en :8003 |
| 2 | Cadena: `_fix_core` → backup de `_final` y rehacerla → backup del mp4 y `_generate_clip` (G→K) con el mismo video_prompt → `foto_arranque_md5` → `_invalidate_baked` | OK | `_fotoclip_core`. `/fix_image` deriva a `_start_fotoclip`. En el manifest, foto_arranque_md5 = 8aa36439..., igual al md5 de la foto en producción |
| 3 | «rehacer clip» queda igual | OK | `_clipfix_core` no aparece en el diff (0 líneas -def) |
| 4 | Tests sin red con deps inyectadas | OK | 61 passed |
| 5 | PEDIDO_* byte a byte | OK | `grep PEDIDO_` sobre el diff de server, html y orquestador.json: 0 apariciones. asset_manager.py y script_engine/ no están en `git status` |
| 6 | Guion vivo y 03_visual: solo image_prompt + image_f8 de ch01 | OK | Contra los backups ts 153557, ambos difieren solo en chapters[0].image_prompt, image_f8.lens_technique, raw_llm_prompt y _f8_slots_scrub. video_prompt y image_sensible no cambian. Los casilleros subject y action no tienen clave propia en image_f8: viven dentro de image_prompt, que cambió |
| 7 | Manifest: solo la parte de ch01 | OK | En ch01.clips[0] cambian ssim, video_prompt, image_prompt, clip_*, segundos, foto_arranque_md5 y foto_final_md5. Los campos de cabecera no cambian |
| 8 | Video_prompt «igual» al aprobado | OK | El del manifest nuevo es idéntico al del guion vivo. El del backup del manifest era uno viejo y desactualizado: el reporte tiene razón al decir «igual al aprobado» |
| 9 | Foto, _final y clip en producción; evidencia en f69/ | OK | md5 de producción = md5 de despues_foto.png (8aa36439...) y de despues_final.png (7f773837...). antes_foto = backup (5f3170e1...). mp4 5aa387cd..., 1920x1080, 8,04 s. Están los 6 PNG, prueba_real.json y prueba_real.py |
| 10 | Primer cuadro parecido a la foto nueva | OK | ssim 0,960 (el cuadro del f69 y el extraído por mí del mp4 dan lo mismo). El primer cuadro «antes» da 0,145 contra la foto nueva, así que es otra imagen |
| 11 | Sin niños ni borde de diapositiva | OK | Lo vi en las tres imágenes: Daniel solo y sin marco. Pie sobre la caja en foto y primer cuadro. Foto final: mano en el pecho, sin caja |
| 12 | Commit y F69_REPORT.md con el veredicto | NO VERIFICABLE | El reporte existe, pero el commit y el pegado van después y no cuentan como falla |

**Gemini → Kling.** El reporte dice «no confirmé qué palabra». Lo recalculé:
- `_is_content_rejection` hace `str(body).lower()` y busca: content_policy, content policy, safety, moderation, rejected, blocked, violates, prohibited, nsfw, safety_checker.
- Los 600 caracteres visibles del cuerpo no tienen ninguna de esas palabras. Tampoco la tiene el payload (no manda campos de safety).
- fal repite en el cuerpo todo el input, incluidas las fotos en data-URI base64.
- Convertí a base64 y pasé a minúsculas las dos fotos que se mandaron (foto y final). Ambas contienen «nsfw»: 3 veces cada una. Expected por azar: varias.
- **Causa más probable:** un falso positivo de «nsfw» dentro del base64 de las imágenes. No es contenido real.
- **Falta para confirmarlo:** el cuerpo completo del error. El log lo corta a 300 caracteres y el manifest a 600. No está guardado.
- El prompt de Opus a Gemini tampoco queda guardado, así que no puedo descartar del todo una palabra del prompt.
- **Consecuencia:** el salto a Kling (US$ 1,89) probablemente no fue un rechazo real. Esto afecta a cualquier clip con foto en base64, no solo a F69. El reporte lo dice a medias y bien.

**Las 7 lecturas del reporte:**
- 1, 2, 3, 4, 5 y 7: razonables y coherentes con el código.
- 6: es correcta, pero deja caminos inconsistentes (ver riesgos).

**Fuera de alcance:**
- DECISIONES.md tiene +1 línea (la de F70, 15:04). No es de F69 ni de este diff.
- El resto de `git status` (diag_234_cap4.py, mapa, f28a.log, pedido_paquetes_wittenoom.txt) no lo toca F69.
- qa_studio_server.py, qa_studio.html, orquestador.json, MAPA_PROYECTO.* y test_module_f69.py están dentro del reporte.

**Riesgos que el contrato no cubre:**
1. **Producción inconsistente si el clip falla.** Si G y K fallan, queda foto nueva + _final nuevo + mp4 viejo, con el manifest viejo (foto_arranque_md5 desactualizado) y sin `_invalidate_baked`. Si `foto_final_fn` lanza una excepción, `_final` ya fue borrado (el backup existe) y no hay mensaje de ese estado. El reporte solo cubre el caso G+K rechazados.
2. **Falso positivo «nsfw».** Como el cuerpo de error repite el base64, Gemini puede caer a Kling sin motivo real: en este caso costó ~US$ 1,89 y no lo atrapa ningún test. asset_manager.py está fuera de esta tanda.
3. **Calidad visual.** Ropa con manchas rojas que pueden leerse como sangre (el prompt a Gemini dice «red-stained»). La foto final cambia de pose respecto de la inicial. No vi el clip en movimiento.

**Adenda mía, posterior al veredicto:**
- **No cambié código.** Si el clip falla, el manifest conserva el md5 de la foto de la que realmente arrancó el mp4 viejo: es lo correcto para esa fila. El mensaje a Omar dice que el clip sigue siendo el viejo; `_fix_core` ya invalidó el horneado. `foto_final_del_clip` atrapa sus errores y devuelve `path` None, así que el caso de la excepción no se da hoy.
- **El falso positivo no es de F69 y no lo arreglé,** porque `asset_manager.py` está prohibido en esta tanda. Queda abierto.
- La frase de arriba, «no confirmé qué palabra», sigue siendo cierta: el revisor da «nsfw» como lo más probable, no confirmado.
