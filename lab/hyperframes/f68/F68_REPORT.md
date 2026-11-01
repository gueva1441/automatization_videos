# F68 — Nano Banana 2 Lite en producción, fotos de Wittenoom regeneradas

**Resultado:** las 101 fotos de Wittenoom salieron de Nano Banana 2 Lite, una por llamada, con 0 respaldos y 0 fallas. Las 198 imágenes anteriores (101 crudas + 97 `_graded`) están en `output/123bbb64-…/_archivo_seedream5lite/`. Clips intactos. **Abrir QA en http://127.0.0.1:8001**, no en la :8002 (ver «Lo que queda abierto» 1).

Handoff: `HANDOFF_F68.md`, md5 `e933f0a88cc68d64dff6f854cee7a221`. Revisor: CUMPLE CON OBSERVACIONES (íntegro abajo).

## Lectura tomada (Omar durmiendo; revisable)

1. **El motor activo es `api.image_engine = "nb2_lite"`** y se ajustaron los 2 chequeos por nombre (m03_visual, foto_madre). La auditoría proponía dejar «seedream» con un despacho interno; con el nombre real, el manifest y `select_profile` dicen la verdad. Volver atrás es una línea, pero `config.py` no va a git: **el cambio de motor vive solo en esta máquina.**
2. **Regenerar todas gana sobre lo que dejaría el flujo normal:** con el clip hecho, el pipeline se saltaba sus fotos. Ahora las rehace si faltan y no toca el clip (`ch01_img_01`, `ch07_img_01` y sus `_final`).
3. **Foto sin persona = sin referencia, literal:** `foto_madre_ref` no entra con este motor.
4. **Escalado:** 1376×768 no es 16:9 exacto. Se escala cubriendo y se recorta el centro (0,8 % de ancho) para no estirar las caras, en vez del escalado directo.
5. **La foto final del clip va sin la frase «same person»:** su referencia es la foto inicial y su instrucción ya es de edit.
6. **El respaldo y las 2 vueltas extra de la adenda 4 viven en el decorador `retry` que ya existía:** 3 vueltas en total.
7. **`_final` del clip:** se regeneró como las demás, con su instrucción de Opus.

## Correcciones aplicadas de la Etapa 0

| # | Hallazgo | Qué se hizo |
|---|---|---|
| 1 | La secuencia no se apagaba y reusaría fotos viejas de `pedidos.json` | `RenderProfile.secuencia=False`; `process_script` la salta; `_llamar_secuencia` sigue en el código |
| 2 | Las fotos de caps con clip no se rehacían | Rama nueva con el clip existente; `foto_de_arranque_cambio` en el manifest |
| 3 | Los `_graded` viejos se reusarían | Archivados junto con las crudas |
| 3b | (mío) Sin manifest, `_archivar_si_desfasado` habría movido también los clips | El manifest se **copió** al archivo, no se movió; fase2a lo sobrescribió al final |
| 4 | `foto_madre_ref` contra la regla 1 | `madres_solo_persona=True` en el perfil |
| 5 | El respaldo no se dispararía bajo el decorador | `_generar_nb2` corre debajo de `retry`; el 422 pasa directo a Seedream |
| 6 | `no_media_generated` se detectaba por accidente | `_motivo_rechazo` lee el `type` de fal; guarda msg, type y categories sin el `input` |
| 7 | Dependencias de `select_profile("seedream")` y chequeos por nombre | `aspect_ratio_text` intacto (texto de m03 igual); chequeos ajustados |
| 8 | Costos | `track_nb2_lite` estimado; Seedream etiquetado 4.5 a 0,04; 4 líneas en DECISIONES |
| 9 | La cola era código nuevo | `_llamada_cola` + `<foto>.llamada.json`, firma por endpoint y payload; un pedido terminado no se reusa |
| 10 | Tamaños y id de edit | `edit_model_id` en el perfil; recorte al centro |
| 11 | Efectos de fase2a | Anotados abajo; el status del topic ya era `assets_rendered` |
| 12 | La frase en la foto final | `frase_de_madres=False` |
| 13 | Nativos en m09 | Se guardan al lado, como pide el handoff, y `bases_del_video` los salta |
| 14 | Supps secuenciales | Ahora en paralelo, mismo orden |
| 15 | Alcance | Ampliado a `config.py`, `cost_tracker.py`, `m03_visual.py`, `m09_packaging.py` |

## Pruebas

- **Tests (sin red):** 419 verdes, 3 saltados, 3 xfailed, en 20 archivos, incluido `test_module_f68.py` nuevo (20). Reescritas: `test_module_f8`, `f57`, `f60_bc`, `test_qa_studio`; no se borró ninguno.
- **Etapa 2 real (`prueba/`):** Daniel con madre, grupo con persona y sin persona: nativo 1376×768 + 2560×1440, texto en `.llamada.json`. P1 (ahorcado): Nano Banana rechazó con `content_policy_violation` (`model_moderated`) y Seedream 4.5 la entregó. `hoja_prueba.jpg`.
- **QA:** la :8001 sirve las 97 fotos de los cuadros, byte a byte iguales a las nuevas y 0 iguales a las archivadas. Las otras 4 (arranque y final de los clips) están en disco.

## Costo

| Concepto | US$ |
|---|---|
| 101 fotos × 0,042 (estimado, fal no devuelve tokens) | 4,242 |
| Prueba: 3 fotos × 0,042 + 1 respaldo × 0,04 | 0,166 |
| 2 instrucciones de foto final (Opus 5.5) | 0,067 |
| **Total estimado** | **4,475** |

El real se ve en el panel de fal. El resumen de `fase2a` imprime US$ 0,00 en «Costo total»: no es real. Las 3 llamadas de Nano Banana rechazadas no están contadas: no está verificado si cobran.

## Clips afectados (no regenerados)

| Clip | Foto de arranque | Estado |
|---|---|---|
| `ch01_veo/ch01_clip_01.mp4` | `ch01_img_01.png` cambió | Arranca de la foto Seedream 5.0 archivada; la foto final también cambió (ssim nueva inicial/final 0,29) |
| `ch07_veo/ch07_clip_01.mp4` | `ch07_img_01.png` cambió | Igual (ssim 0,39) |

## Lo que queda abierto

1. **El QA de la :8002 (abierto desde el 31-oct 17:46) está viejo y conviene cerrarlo.** Muestra las fotos nuevas, pero con el guion y el código que tenía en memoria: texto de la narración anterior debajo de cada foto y «rehacer foto» por Seedream 5.0. No lo cerré porque es tuyo. El nuevo corre en la pestaña «QA Studio F68» del panel Terminal.
2. **Riesgo para el render: el emparejado de anclas falla en 5 de 7 caps.** `compute_anchor_starts` devuelve None en ch02, ch03, ch05, ch06 y ch07, QA marca «sync aproximado» y `fase2b` cae a reparto uniforme: cada foto dura lo mismo, sin seguir la voz. Es previo a F68, no se tocó y no depende de las fotos. Hipótesis: los timestamps tienen la voz fonética («mil novecientos cuarenta y cuatro») y la aguja conserva «1944»; ch04 también tiene números y sí empareja, así que no está probado que sea toda la causa. **Hay que arreglarlo antes de hornear fondos.**
3. **Nada avisa que `_fase2b_work/` y `_final.mp4` son de fotos viejas:** `etapa_de` solo mira el sello del papel. Hoy dice `fondos`, porque falta `fondos.json`, y `fase2b` sin `--reuse-visuals` recocina; con `--reuse-visuals` mezclaría versiones. `flow_specs.json`, `depth_metrics.json` y `zoom_verdicts.json` de `assets/` también son de las fotos anteriores; no revisé si se recalculan.
4. **Clips ch01 y ch07:** decidir si se regeneran (≈ US$ 1,20 cada uno) para que arranquen de la foto nueva.
5. **3 fotos perdieron el ancla del lugar** (`__subject__`): ch05 img 6, ch06 img 10 y 12. Si se ven mal, se puede devolver esa referencia con otra frase.
6. **ch07 supp 2** trae a Maitland Parker y Marcos Orellana: solo hay madre de Maitland. Coherente con la regla.
7. **Madres:** las 10 actuales se reusaron (Seedream 5.0 Lite o GPT Image). Los `.prompt.txt` solo se escriben al generar una madre nueva, así que estas no lo tienen. Las de persona nuevas saldrán de Seedream 4.5.
8. **Retoques sin medir:** en un rechazo doble cada vuelta vuelve a pedir a los dos motores. El respaldo no se usó en la corrida real, solo en la prueba y en tests.
9. **Sin commitear, ajenos a F68:** `diag_234_cap4.py`, `lab/hyperframes/f28/a/f28a.log` y `lab/hyperframes/f58/pedido_paquetes_wittenoom.txt` (este último lo reescribe `test_module_f58.py`, que corrió en esta tanda; ya estaba modificado antes).

## Tabla por foto

| Foto | Motor | Llamada | Respaldo y motivo | s | US$ (estimado) |
|---|---|---|---|---|---|
| ch01_supp_01.png | nb2_lite | edit (1 ref.) | no | 12.5 | 0.042 |
| ch01_supp_02.png | nb2_lite | t2i (0 ref.) | no | 7.3 | 0.042 |
| ch01_supp_03.png | nb2_lite | t2i (0 ref.) | no | 7.1 | 0.042 |
| ch01_supp_04.png | nb2_lite | edit (1 ref.) | no | 12.5 | 0.042 |
| ch01_supp_05.png | nb2_lite | t2i (0 ref.) | no | 7.3 | 0.042 |
| ch01_supp_06.png | nb2_lite | t2i (0 ref.) | no | 7.3 | 0.042 |
| ch01_supp_07.png | nb2_lite | t2i (0 ref.) | no | 7.2 | 0.042 |
| ch01_supp_08.png | nb2_lite | t2i (0 ref.) | no | 7.3 | 0.042 |
| ch01_img_01.png | nb2_lite | edit (1 ref.) | no | 6.4 | 0.042 |
| ch01_img_01_final.png | nb2_lite | edit (1 ref.) | no | 11.7 | 0.042 |
| ch02_img_01.png | nb2_lite | edit (2 ref.) | no | 13.3 | 0.042 |
| ch02_img_02.png | nb2_lite | edit (2 ref.) | no | 13.7 | 0.042 |
| ch02_img_03.png | nb2_lite | edit (2 ref.) | no | 15.3 | 0.042 |
| ch02_img_04.png | nb2_lite | edit (2 ref.) | no | 15.3 | 0.042 |
| ch02_img_05.png | nb2_lite | edit (2 ref.) | no | 15.4 | 0.042 |
| ch02_img_06.png | nb2_lite | t2i (0 ref.) | no | 7.5 | 0.042 |
| ch02_img_07.png | nb2_lite | t2i (0 ref.) | no | 7.5 | 0.042 |
| ch02_img_08.png | nb2_lite | edit (2 ref.) | no | 15.0 | 0.042 |
| ch02_img_09.png | nb2_lite | t2i (0 ref.) | no | 7.9 | 0.042 |
| ch02_img_10.png | nb2_lite | edit (1 ref.) | no | 14.1 | 0.042 |
| ch02_img_11.png | nb2_lite | t2i (0 ref.) | no | 7.8 | 0.042 |
| ch02_img_12.png | nb2_lite | edit (2 ref.) | no | 13.3 | 0.042 |
| ch02_img_13.png | nb2_lite | t2i (0 ref.) | no | 7.8 | 0.042 |
| ch02_img_14.png | nb2_lite | t2i (0 ref.) | no | 13.0 | 0.042 |
| ch02_img_15.png | nb2_lite | edit (1 ref.) | no | 13.2 | 0.042 |
| ch03_img_01.png | nb2_lite | t2i (0 ref.) | no | 8.0 | 0.042 |
| ch03_img_02.png | nb2_lite | edit (2 ref.) | no | 15.1 | 0.042 |
| ch03_img_03.png | nb2_lite | t2i (0 ref.) | no | 8.1 | 0.042 |
| ch03_img_04.png | nb2_lite | t2i (0 ref.) | no | 8.1 | 0.042 |
| ch03_img_05.png | nb2_lite | edit (1 ref.) | no | 15.0 | 0.042 |
| ch03_img_06.png | nb2_lite | t2i (0 ref.) | no | 8.1 | 0.042 |
| ch03_img_07.png | nb2_lite | edit (1 ref.) | no | 13.6 | 0.042 |
| ch03_img_08.png | nb2_lite | edit (1 ref.) | no | 14.7 | 0.042 |
| ch03_img_09.png | nb2_lite | edit (1 ref.) | no | 14.7 | 0.042 |
| ch03_img_10.png | nb2_lite | t2i (0 ref.) | no | 13.6 | 0.042 |
| ch03_img_11.png | nb2_lite | t2i (0 ref.) | no | 13.6 | 0.042 |
| ch03_img_12.png | nb2_lite | t2i (0 ref.) | no | 13.6 | 0.042 |
| ch03_img_13.png | nb2_lite | t2i (0 ref.) | no | 8.4 | 0.042 |
| ch03_img_14.png | nb2_lite | t2i (0 ref.) | no | 8.4 | 0.042 |
| ch03_img_15.png | nb2_lite | t2i (0 ref.) | no | 8.4 | 0.042 |
| ch03_img_16.png | nb2_lite | edit (1 ref.) | no | 14.8 | 0.042 |
| ch04_img_01.png | nb2_lite | edit (2 ref.) | no | 13.8 | 0.042 |
| ch04_img_02.png | nb2_lite | edit (1 ref.) | no | 12.7 | 0.042 |
| ch04_img_03.png | nb2_lite | edit (1 ref.) | no | 13.1 | 0.042 |
| ch04_img_04.png | nb2_lite | t2i (0 ref.) | no | 6.9 | 0.042 |
| ch04_img_05.png | nb2_lite | edit (1 ref.) | no | 13.4 | 0.042 |
| ch04_img_06.png | nb2_lite | t2i (0 ref.) | no | 12.3 | 0.042 |
| ch04_img_07.png | nb2_lite | edit (1 ref.) | no | 13.5 | 0.042 |
| ch04_img_08.png | nb2_lite | edit (1 ref.) | no | 13.5 | 0.042 |
| ch04_img_09.png | nb2_lite | edit (1 ref.) | no | 14.8 | 0.042 |
| ch04_img_10.png | nb2_lite | edit (1 ref.) | no | 14.9 | 0.042 |
| ch04_img_11.png | nb2_lite | edit (1 ref.) | no | 14.9 | 0.042 |
| ch04_img_12.png | nb2_lite | edit (2 ref.) | no | 15.2 | 0.042 |
| ch04_img_13.png | nb2_lite | edit (2 ref.) | no | 13.6 | 0.042 |
| ch04_img_14.png | nb2_lite | edit (2 ref.) | no | 13.5 | 0.042 |
| ch05_img_01.png | nb2_lite | t2i (0 ref.) | no | 8.1 | 0.042 |
| ch05_img_02.png | nb2_lite | t2i (0 ref.) | no | 8.2 | 0.042 |
| ch05_img_03.png | nb2_lite | t2i (0 ref.) | no | 8.6 | 0.042 |
| ch05_img_04.png | nb2_lite | edit (2 ref.) | no | 15.2 | 0.042 |
| ch05_img_05.png | nb2_lite | t2i (0 ref.) | no | 8.6 | 0.042 |
| ch05_img_06.png | nb2_lite | t2i (0 ref.) | no | 8.7 | 0.042 |
| ch05_img_07.png | nb2_lite | t2i (0 ref.) | no | 8.7 | 0.042 |
| ch05_img_08.png | nb2_lite | edit (1 ref.) | no | 14.9 | 0.042 |
| ch05_img_09.png | nb2_lite | t2i (0 ref.) | no | 13.6 | 0.042 |
| ch05_img_10.png | nb2_lite | t2i (0 ref.) | no | 8.7 | 0.042 |
| ch05_img_11.png | nb2_lite | edit (1 ref.) | no | 14.1 | 0.042 |
| ch05_img_12.png | nb2_lite | edit (1 ref.) | no | 13.9 | 0.042 |
| ch05_img_13.png | nb2_lite | t2i (0 ref.) | no | 8.7 | 0.042 |
| ch05_img_14.png | nb2_lite | t2i (0 ref.) | no | 8.7 | 0.042 |
| ch05_img_15.png | nb2_lite | t2i (0 ref.) | no | 13.7 | 0.042 |
| ch05_img_16.png | nb2_lite | edit (1 ref.) | no | 14.0 | 0.042 |
| ch06_img_01.png | nb2_lite | edit (1 ref.) | no | 14.3 | 0.042 |
| ch06_img_02.png | nb2_lite | edit (1 ref.) | no | 14.2 | 0.042 |
| ch06_img_03.png | nb2_lite | edit (1 ref.) | no | 14.3 | 0.042 |
| ch06_img_04.png | nb2_lite | edit (1 ref.) | no | 15.1 | 0.042 |
| ch06_img_05.png | nb2_lite | t2i (0 ref.) | no | 9.2 | 0.042 |
| ch06_img_06.png | nb2_lite | t2i (0 ref.) | no | 9.2 | 0.042 |
| ch06_img_07.png | nb2_lite | edit (1 ref.) | no | 14.3 | 0.042 |
| ch06_img_08.png | nb2_lite | edit (1 ref.) | no | 14.3 | 0.042 |
| ch06_img_09.png | nb2_lite | t2i (0 ref.) | no | 9.1 | 0.042 |
| ch06_img_10.png | nb2_lite | t2i (0 ref.) | no | 9.0 | 0.042 |
| ch06_img_11.png | nb2_lite | t2i (0 ref.) | no | 9.1 | 0.042 |
| ch06_img_12.png | nb2_lite | t2i (0 ref.) | no | 9.1 | 0.042 |
| ch06_img_13.png | nb2_lite | t2i (0 ref.) | no | 9.1 | 0.042 |
| ch06_img_14.png | nb2_lite | t2i (0 ref.) | no | 9.1 | 0.042 |
| ch06_img_15.png | nb2_lite | t2i (0 ref.) | no | 9.1 | 0.042 |
| ch06_img_16.png | nb2_lite | t2i (0 ref.) | no | 9.0 | 0.042 |
| ch07_supp_01.png | nb2_lite | edit (1 ref.) | no | 14.2 | 0.042 |
| ch07_supp_02.png | nb2_lite | edit (1 ref.) | no | 14.5 | 0.042 |
| ch07_supp_03.png | nb2_lite | edit (1 ref.) | no | 12.9 | 0.042 |
| ch07_supp_04.png | nb2_lite | t2i (0 ref.) | no | 7.3 | 0.042 |
| ch07_supp_05.png | nb2_lite | t2i (0 ref.) | no | 13.0 | 0.042 |
| ch07_supp_06.png | nb2_lite | t2i (0 ref.) | no | 7.3 | 0.042 |
| ch07_supp_07.png | nb2_lite | t2i (0 ref.) | no | 12.8 | 0.042 |
| ch07_supp_08.png | nb2_lite | t2i (0 ref.) | no | 12.9 | 0.042 |
| ch07_supp_09.png | nb2_lite | edit (1 ref.) | no | 13.8 | 0.042 |
| ch07_supp_10.png | nb2_lite | t2i (0 ref.) | no | 13.0 | 0.042 |
| ch07_supp_11.png | nb2_lite | t2i (0 ref.) | no | 12.9 | 0.042 |
| ch07_supp_12.png | nb2_lite | edit (2 ref.) | no | 14.9 | 0.042 |
| ch07_img_01.png | nb2_lite | t2i (0 ref.) | no | 6.1 | 0.042 |
| ch07_img_01_final.png | nb2_lite | edit (1 ref.) | no | 11.7 | 0.042 |

## Veredicto de revisor-handoff, final (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES. No encontré fallas en el código ni en las fotos. Las observaciones son un archivo ajeno modificado y los puntos abiertos. Falta el reporte principal, que aún no existe.

Tests: `pytest` de f68, f8, f60_bc, f57 y qa_studio dio 131 passed. Las aserciones se reescribieron y no se borró ningún test. `test_perfil_seedream_v5_lite` pasó a `test_perfil_seedream_v4_5`, `test_fix_core_foto_madre_...` agregó monkeypatch, y f57 y f60_bc cambiaron firmas y asserts. No usé fal.

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Una foto = una llamada. Con persona va en edit con su madre; sin persona va sin referencia | OK | Cruzé los 101 `.llamada.json` con `data/scripts/<topic>.json`. De los 77 ítems de `image_prompts`, los 77 coinciden con las madres que debía llevar (`persona_aporta_madre`). Las supps también coinciden: ch01 supp 1 y 4 llevan a Daniel, ch07 supp 1-3 a Maitland, supp 9 a Eric, supp 12 a Daniel y María. 0 fotos sin persona con referencia; 53 sin ref, 34 con 1 y 14 con 2. Edit si y solo si hay ref. `asset_manager.py` `_madres_para_item` con `madres_solo_persona`. |
| 2 | Texto exacto del guion; la frase solo en edit de foto | OK | 77 de 77 textos iguales a `prompt` (+ frase de una o varias madres). Las `_final` de ch01 y ch07 salen sin frase (`frase_de_madres=False`). Parámetros idénticos en las 101: `aspect_ratio` 16:9, `safety_tolerance` "6", `num_images` 1. |
| 3 | Respaldo a Seedream 4.5 con mensaje exacto | OK | `prueba/respaldo_P1.llamada.json`: nb2 con error `content_policy_violation`/`model_moderated`, luego `seedream45_respaldo` ok en `v4.5/text-to-image` (0,04 US$). `_motivo_rechazo` lee el `type` de fal, no palabras clave. En la corrida real hubo 0 respaldos, así que el respaldo solo está probado en la prueba y en tests. |
| 4 | Cola con `request_id` guardado antes de esperar | OK | `_llamada_cola` escribe el registro antes de esperar; tests de reanudar y de registro en `test_module_f68.py`. En la corrida real: 101 llamadas, 101 `ok`. |
| 5 | La secuencia sigue existiendo pero sin uso | OK | `process_script` la salta con `perfil.render.secuencia` False; `_llamar_secuencia` no se borró. |
| 6 | Prompt de la madre en disco | OK | `_guardar_prompt_madre` en `foto_madre.py` (`<slug>.prompt.txt`), con test. |
| 7 | Las 101 fotos son Nano Banana y las 198 anteriores están archivadas | OK | Vivas (sin contar `_desfasado*`): 101 fotos, 101 `_native` y 97 `_graded`. Archivo `_archivo_seedream5lite`: 198 png (101 + 97 graded) y 1 json. Los 2 mp4 (`ch01_veo/ch01_clip_01.mp4` y `ch07_veo/ch07_clip_01.mp4`) siguen en assets con mtime 2026-10-31; no hay mp4 en el archivo. |
| 8 | Tamaños: nativo 1376×768 y foto 2560×1440 | OK | Las 101 nativas miden 1376×768 y las 101 fotos 2560×1440. En la prueba, el nativo del respaldo mide 2560×1440 porque es de Seedream. Se escala cubriendo y recortando el centro (0,8 %); está declarado en DECISIONES. |
| 9 | `_graded` nuevos | OK | Ningún `_graded` es más viejo que su foto. Hay 4 fotos sin graded, todas en `ch01_veo` y `ch07_veo` (`img_01` y `img_01_final`). |
| 10 | DECISIONES, stickers y mapa coinciden | OK | 4 líneas nuevas en DECISIONES.md. Los stickers de `orquestador.json` y `fase2a.json` mencionan Nano Banana y sus md5 cambiaron. El mapa subió a 12 y 24 tests. `config.py` está ignorado por git (`.gitignore:2`) y trae `image_engine="nb2_lite"` y `nb2_lite_per_image` 0,042. |
| 11 | QA Studio en :8001 sirve las fotos nuevas | OK | `/caps` lista ch01-ch07. `/img?cap=ch02&name=ch02_img_06.png` devuelve 200 en 2560×1440 y es byte a byte igual a la foto nueva (no a la graded). |
| 12 | No se tocó main, guion, papel, voz, gfx ni render | OK | `git status` no muestra esos archivos como modificados. `data/` no aparece. El manifest nuevo lleva `papel_md5` y 176 marcas `motor: nb2_lite`. |
| 13 | `F68_REPORT.md` | NO VERIFICABLE | No existe todavía (pediste el reporte en construcción). |

Fuera de alcance de F68, modificados sin sello:
- `diag_234_cap4.py`: solo cambia el TOPIC; mtime 29-oct.
- `lab/hyperframes/f28/a/f28a.log`: +33 líneas; mtime 29-oct.
- `lab/hyperframes/f58/pedido_paquetes_wittenoom.txt`: el diff cambia el texto del gancho. Parece efecto de un test que escribe a disco real; mi pytest pudo regenerarlo. Revisá si hay que restaurarlo antes del commit.
- `m09_packaging.py` (saltar `_native`) y el diff de `MAPA_PROYECTO.md` en filas de `qa_studio*` y `m01f` están justificados en el diff, pero conviene confirmarlos.

Tus puntos abiertos:
- (a) Plausible. No lo probé, porque no pegué contra :8002.
- (b) Verificado el efecto. `compute_anchor_starts` devuelve None en ch02, 03, 05 y 06 (lo recalculé con `ch0N_timestamps.json`), y `/cap` marca `sync_approx` True en ch02, 03, 05, 06 y 07; ch01 y ch04 salen False. `anchor_timing.py` no está tocado, así que es previo. Matiz: ch04 también tiene números en sus anclas (2) y sí encaja, así que los números solos no explican la causa. Eso lo dejo como hipótesis. ch07 no lo recalculé por mi cuenta.
- (c) Correcto. Los clips ch01 y ch07 conservan su foto de arranque vieja y `ch01_img_01`/`ch07_img_01` y sus `_final` son nuevas. `etapa_de` no lo detecta, no lo probé.
- (d) Correcto. Pierden la referencia `__subject__` ch05 img 6 y ch06 img 10 y 12. Las tres tienen `foto_madre_ref=['__subject__']` y `persona` vacía. Está declarado en DECISIONES (lectura b).

Falta uno: ch07 supp 2 trae `persona` ["Maitland Parker", "Marcos Orellana"] y solo lleva la madre de Maitland, porque Marcos no está en el registry. Es coherente con la regla, pero la foto tiene un personaje sin ancla.

Riesgos que el contrato no cubre:
- El decorador `retry` sigue por encima de `_generar_nb2`. Si los dos motores rechazan, cada vuelta paga otra vez a nb2 y a Seedream (3 vueltas), y el tope de la adenda 4 depende de eso.
- En esta corrida el costo estimado de las 101 fotos es 4,24 US$ (0,042 cada una), porque fal no devuelve tokens. No hay verificación de que coincida con el panel.
- `fase2b` con fotos nuevas pero con `_fase2b_work` y `_final.mp4` viejos puede mezclar versiones sin aviso.

**Adenda de CC:** el reporte se escribió después de este veredicto; no hubo cambios de código entre el veredicto y el commit. Sobre (a), la :8002 sí la vi: en pantalla muestra debajo de la foto el texto de la narración anterior.

## Veredicto de revisor-handoff, auditoría de la Etapa 0 (íntegro)

VEREDICTO ETAPA 0: NO CUMPLE tal como está escrito. El handoff tiene 3 supuestos que, si se implementan al pie de la letra, generan fotos equivocadas o rompen el alcance. Solo lectura. No corrí tests ni nada que gaste.

HALLAZGOS (de mayor a menor gravedad)

| # | Hallazgo (archivo:línea) | Corrección sugerida, dentro del alcance |
|---|---|---|
| 1 | CRÍTICO. La regla 5 supone que la secuencia "queda sin uso" con el perfil nuevo, pero nada la apaga. `process_script` llama siempre a `_pre_paso_secuencia` (asset_manager.py:1748). Eso agrupa por persona y arma lotes (1046-1057). Las 25 fotos que hoy son `ok_secuencia` saldrían por Seedream /edit, no por Nano Banana. Además `_llamar_secuencia` reanuda por `request_id` con clave md5(prompts+refs) (933, 965-970). `output/123bbb64.../_secuencia/pedidos.json` ya tiene esos pedidos y los prompts no cambian, así que reutilizaría las fotos viejas de Seedream 5.0 sin pagar y las presentaría como nuevas. | Poner una compuerta en `process_script` (por ejemplo `secuencia = {}` cuando el perfil principal es NB2 Lite) sin borrar `_llamar_secuencia`. Mover o ignorar `_secuencia/pedidos.json`. El pedido por foto debe usar otra clave, que incluya modelo, prompt y madres. Adaptar la aserción de test_module_f60_bc.py:545, que fija ese texto en el código fuente. |
| 2 | CRÍTICO. "Regenerar TODAS sin excepción" choca con "clips: NO regenerar". En los caps con clip, `clip_path.exists()` se evalúa antes que la foto (asset_manager.py:1464-1474) y hace `continue`. Si se mueven `ch01_img_01.png` y `ch07_img_01.png` pero se deja el mp4, esas fotos y sus `_final.png` NO se regeneran. Quedan 4 fotos de Seedream 5.0 (ch01_veo y ch07_veo: `img_01` e `img_01_final`). Hay 1 clip por cap (manifest: ch01 y ch07). Las 8 + 12 supps sí se regeneran, porque van por otro camino (1355-1420). La foto inicial usa solo las madres de `image_f8` (1451-1453, 1493). | Decidirlo antes de empezar. Opción conservadora: dejar esas 4 fotos y los 2 clips intactos y declararlo en el reporte. Si Omar quiere las 4 fotos nuevas, se generan con una llamada directa fuera del loop de clips. En ese caso los 2 clips quedan con foto de arranque desfasada ("clips afectados" = ch01 clip 1 y ch07 clip 1). |
| 3 | ALTO. Hay que mover también las `*_graded.png`, no solo las fotos. `image_grade.grade()` devuelve el `_graded` existente sin regenerar (image_grade.py:67-68). `_apply_grade` (asset_manager.py:1615-1641) pondría el `_graded` viejo de Seedream como `path` del manifest. La foto nueva quedaría al lado y no se usaría. | Archivar fotos, `_graded` y `assets_manifest.json` juntos. El SMART SKIP es solo por `exists()` (1134, 1376). `_archivar_si_desfasado` no mueve nada, porque el sello del manifest coincide con el del script: ambos `39c99927…` (verificado). Dejar el archivo en `output/<topic>/_archivo_seedream5lite/`, fuera de `assets/`. |
| 4 | ALTO. La regla 1 ("sin persona: sin referencia") contradice la regla única de madres. `_madres_para_item` (asset_manager.py:826-840) suma `foto_madre_ref` (objeto o lugar, `__subject__`, props) a las madres de `persona`, tope 2. En el manifest actual hay fotos con ref y sin persona: ch05 img 6, ch06 img 10 y 12 (`__subject__`), ch07 supp 2 (Maitland Parker). La supp 12 de ch07 lleva Daniel y María como refs, y las supps del manifest no guardan `persona`. También hay persona sin madre, que ya sale como t2i: McNulty, James Vernon, y Daniel en ch05 img 10 y 13 por el filtro de era (`persona_aporta_madre`, 795). | Para el motor nuevo: madres = solo las de `persona` que aportan por era. Ignorar `foto_madre_ref` aunque exista. Eso cumple la regla 1 tal como está escrita. Si Omar quiere conservar el ancla del `__subject__`, que lo decida él. |
| 5 | ALTO. El respaldo de la regla 3 no se dispara donde el handoff cree. `_generate_image_raw` está decorado con `@error_handler.retry` (asset_manager.py:320). El decorador captura todo, hace 3 intentos con sleep de 5 y 10 s, y al final lanza `PipelineError` (error_handler.py:171-215), no `ContentRejectedError`. Por eso hoy el `except ContentRejectedError` de foto_final (699) y `reject_reason="content"` (1239) no se activan por esa vía. En QA, el mensaje "filtro:" (qa_studio_server.py:1119) tampoco. | Poner el respaldo dentro de la función decorada o por debajo del decorador (un helper sin `@retry`), así el 422 no se reintenta 3 veces. Ya hay `test_429_reintenta_tres_veces` (test_module_f8.py:107-128) que fija 3 intentos. |
| 6 | ALTO. `no_media_generated` solo se detecta por accidente. `CONTENT_REJECTION_KEYWORDS` (asset_manager.py:84-89) no incluye `no_media_generated` ni "unsafe". El mensaje real (lab/_nb_tol6/REPORTE.md:40, caso nb2_P3) coincide únicamente porque fal devuelve el input con `"safety_tolerance":6`, y "safety" es keyword. En cambio `content_policy_violation`/`model_moderated` sí coincide (resultados.json, nb2_lite_P1). El mensaje `no_media_generated` repite el prompt entero. Con `[:300]` (368) el campo `type` queda cortado. | Agregar `no_media_generated` a las keywords. Para el manifest, guardar el mensaje exacto sin truncar a 300, o guardar `type` y `categories` aparte. Probar que un 422 de este tipo dispare el respaldo. |
| 7 | ALTO. Dependencias de `select_profile("seedream")`/`PERFIL_SEEDREAM`: `_seedream_payload_for` (asset_manager.py:264) y `_seedream_edit_payload_for` (285). `_generate_image_raw` (338) elige perfil por `api.image_engine`, que por defecto es "seedream" (config.py:96). El edit se activa con `engine == "seedream"` (344) y las tarifas salen de `_SYNC_COST_TRACKERS` (309-316). Más: `_prompt_secuencia`/`_llamar_secuencia` (943, 961), `_generate_madre_seedream` (foto_madre.py:312), m03_imagenes_v3.py:625/645 (`aspect_ratio_text`), `foto_final_del_clip` (asset_manager.py:698, vía `_generate_image_raw`) y m09 miniaturas (m09_packaging.py:447, `_generate_image_raw`). Guards por nombre: foto_madre.py:384 (`!= "seedream"` ⇒ sin madre de persona) y m03_visual.py:2069 (lanza ValueError si `image_engine != "seedream"`). | NO cambiar `api.image_engine` ni agregar otra clave de motor: rompe esos guards. Hacer que el despacho del motor principal sea interno de `_generate_image_raw`, con una constante nueva, y dejar `api.image_engine="seedream"`. Si PERFIL_SEEDREAM pasa a 4.5, `_generate_madre_seedream` (foto_madre.py:312) usa 4.5 para madres nuevas. Las 10 madres actuales de `foto_madre/` se reusan (skip por archivo) y no cambian. |
| 8 | MEDIO. Costos y etiquetas. `track_seedream` tiene fijo "Seedream 5.0 Lite" y tarifa `pipeline.costs['seedream_per_image']=0.035` (cost_tracker.py:247-250, config.py:156). No hay tracker de Nano Banana. El respaldo a 4.5 (handoff dice 0,04) se registraría como 5.0 Lite a 0,035. Tampoco queda en DECISIONES.md ninguna entrada de NB2 Lite, ni el 0,042 US$, ni la elección de Omar del 1-11. ESTADO_SESION dice que Omar y el analista "miran las hojas". El costo por tokens no se pudo medir en el lab ("API de uso 403"), así que el 0,042 no está verificado. | Agregar un tracker nuevo con su tarifa y marca "estimado". Parametrizar etiqueta y tarifa del respaldo. Registrar en DECISIONES la elección y el 0,042 antes de usarlo (regla de CLAUDE.md). |
| 9 | MEDIO. "Cola de fal con request_id": hoy el motor de fotos es SYNC `fal.run` con `requests.post(...timeout=240)` (asset_manager.py:358-363). Es código nuevo, no "como F60". Reusar `_fal_queue_poll` (573) y `_guardar_pedido` (924). El 422 en cola llega al pedir `response_url`, y ahí se maneja en 585. `_guardar_pedido` escribe en `_secuencia/pedidos.json` bajo `_PEDIDOS_LOCK`. | Clave por foto distinta de `_clave_lote`. Con esa clave, un rechazo no queda guardado como "pedido a reanudar". |
| 10 | MEDIO. Tamaños: `image_width/height` = 2560×1440 es correcto (config.py:132-133). Pero 1376×768 (1,792) a 2560×1440 (1,778) con lanczos directo estira un 0,8 %. El perfil actual manda `image_size` con ese dict. Nano Banana no usa `image_size`: usa `aspect_ratio` y resolución fija 1K (lab/_nb_tol6/ENDPOINTS.md). El edit de NB2 Lite no se deriva con `.replace("text-to-image","edit")` (344-349), porque su id no contiene "text-to-image". Seedream 4.5 sí lo permite. Seedream 4.5 devuelve JPEG con extensión .png (comentario en asset_manager.py:299). | Declarar el id edit de NB2 Lite como constante. Decidir escalar con leve estiramiento o recortar a 16:9 exacto antes del escalado, y anotarlo. Pasar el respaldo por `_ensure_real_png` si se guarda el nativo. |
| 11 | MEDIO. "Paso normal" = `python fase2a.py --topic 123bbb64-9fca-4395-8bf4-57d60e219ef1` (fase2a.py:403-405, `--topic` ignora el status). Hace, además de las fotos: carga el `sync_map` existente (no regenera voz para LONG), corre `generate_foto_madre_for_topic` (skip por archivo; paga solo si falta una madre) y `asset_process`. Después llama `_mark_topic_assets_rendered` (fase2a.py:224-236), que escribe `status='assets_rendered'` y `assets_rendered_at` en topics_db. Si estaba `video_generated`, lo rebaja. También inicia `cost_tracker` para este video (`_ensure_cost_tracking`, asset_manager.py:1644) y no toca guion, papel ni voz. Efecto sobre `etapa_de` (run_pipeline.py:213-219): solo compara el sello del papel, así que las fotos nuevas con el mismo sello no marcan `assets`, `fondos` ni `render` como desfasados. `_fase2b_work/` (incluido `_fase2b_work_desfasado_*`) y `_final.mp4` quedan con las fotos viejas sin que ningún chequeo lo avise. | Mencionarlo en el reporte. No correr fase2b (prohibido). Revisar topics_db después. Si se quiere evitar el cambio de status, llamar `asset_manager.process_script` directo. |
| 12 | MEDIO. Texto de las fotos (pregunta 2): el prompt lo arma m03 (cierre con `aspect_ratio_text` en m03_imagenes_v3.py:645), no el perfil. `m03_visual.py` solo importa `select_profile` (105). Nadie lee `formula`, `negations_in_text`, `style_tail` ni `text_recipe`. El texto cambia solo si `aspect_ratio_text` de PERFIL_SEEDREAM se altera o se pierde al recrear el perfil como 4.5: pasaría a `""` y las fotos pierden la frase de 16:9. Test: test_module_f8.py:186. Además, la regla 2 antepone la frase "same person" también en `foto_final_del_clip` (asset_manager.py:696-698), que ya usa su propia instrucción de edit de Opus. Eso cambia ese texto y viola el "MISMO texto". Y para las fotos de grupo, la frase "same person" se decide por cantidad de madres, no por personas en escena. | Si se re-crea PERFIL_SEEDREAM, copiar `aspect_ratio_text` tal cual. Anteponer la frase solo a las fotos de producción con madre, no a la foto final del clip. Decidir en el código si para la foto final del clip sirve el prefijo plural. |
| 13 | MEDIO. Archivos `*_native.png`. QA no los muestra: `_IMG_NAME_RE` (qa_studio_server.py:76) exige `^ch\d{2}_(img\|supp)_\d+\.png$`, y QA lista por glob de directorio, no por manifest (191-197). El `.glob("ch*_*")` de 274 es de carpetas. m09 sí: `bases_del_video` hace `rglob("*.png")` (m09_packaging.py:580-587) y listaría los `_native` como bases extra de miniatura. m06 y fase2b no globean estas carpetas. Los sidecars `.json`/`.txt` no chocan con nada. | Guardar los nativos fuera de `assets/` (por ejemplo `output/<topic>/_nativos/`), o aceptar la duplicación en m09. |
| 14 | BAJO. Las supps de ch01 (8) y ch07 (12) se generan en un loop secuencial (asset_manager.py:1355). La "regla de máximo paralelo" solo se cumple en caps flux (ThreadPoolExecutor, 1188). | Es una limitación de paralelismo; el handoff no obliga a cambiarlo. |
| 15 | INFORMATIVO. Alcance de módulos: el handoff no lista `config.py`, `cost_tracker.py`, `error_handler.py`, `fase2a.py` ni `qa_studio_server.py`. Los puntos 5, 6 y 8 piden tocar al menos `cost_tracker.py` y la lista de keywords en asset_manager.py. | Anotar `cost_tracker.py` como ampliación mínima. Dejar el resto sin tocar. |

CAMBIOS FUERA DEL ALCANCE DECLARADO: no se tocó ningún archivo en esta etapa.

RESPUESTAS BREVES A TUS 8 PREGUNTAS
1. Ver #7. Pasar a 4.5 cambia: `accepts_seed` (el payload empezaría a mandar `seed`, asset_manager.py:271/293), la etiqueta y tarifa de costos, el modelo de madres de persona nuevas, la foto final y las miniaturas si el despacho no es explícito. QA "rehacer foto" y fix_image usan `_generate_flux_image_at` y entran al mismo motor.
2. Ver #12. Con el despacho interno y el `aspect_ratio_text` intacto, el texto de m03 no cambia.
3. Secuencia y madres: `_pre_paso_secuencia` (asset_manager.py:1034) y `_madres_para_item` (826). Ver #1 y #4. El "bug Daniel#1 Image 5" no está documentado en DECISIONES ni en ESTADO_SESION. En lab/hyperframes/f60/F60_REPORT.md:1221 figuran lotes "Daniel#1". El único dato verificable es que el lote por persona manda "same person" a todas las escenas (asset_manager.py:950), incluida una de pareja. Eso desaparece al gatear la secuencia, pero la foto sigue recibiendo la madre de Daniel por `persona`.
4. Ver #3 y #13.
5. Ver #2. La foto `_final` solo se regenera por `foto_final_del_clip` (asset_manager.py:691-706). Si existe, se reusa; si no, es un edit de Seedream con la foto inicial de referencia. Con el motor nuevo iría por NB2 Lite edit, salvo que se decida otra cosa.
6. Ver #11.
7. QA lee las carpetas `assets/<cap>_flux|_veo` por glob y el guion en `data/scripts/<id>.json` y `_steps/<id>/03_visual.json`. No depende del manifest para mostrar fotos.
8. Ver #5, #6, #9, #10. `_generate_image_raw` es SYNC (asset_manager.py:358). Reanudar por `request_id` es código nuevo para fotos sueltas. Los 3 casos `content_policy_violation` y el `no_media_generated` salen en `lab/_nb_tol6/resultados.json` y `REPORTE.md:39-43`.

NO VERIFICABLE: el 0,042 US$ por foto (lo mide Omar en el panel; en el repo solo consta "sin medir: precio por tokens"). Si fal acepta `seed` en NB2 Lite (los payloads de ejemplo traen `"seed":null`). El efecto exacto de `start_video` sobre un cost file previo de este video. Qué ocurre con las fotos de Seedream 4.5 en `_ensure_real_png` en esta ruta.

RIESGOS QUE EL CONTRATO NO CUBRE
- El `_final.mp4` y `_fase2b_work/` actuales quedan con las fotos viejas sin que `etapa_de` lo detecte (solo mira el sello del papel).
- topics_db pasa a `assets_rendered` aunque el video estuviera `video_generated`.
- Sin entrada en DECISIONES.md para NB2 Lite y su costo, el contrato incumple la regla de CLAUDE.md sobre números.
