# HANDOFF F69 — QA Studio: la foto de arranque del clip se puede rehacer

## Por qué (Omar, 2026-11-01 14:34)
En el gancho (ch01, cap con clip) salen 6 niños junto a Daniel. Omar pidió en QA «solo Daniel» y no cambió nada. Causa, por diseño de F59:
- En caps con clip, QA muestra el clip como tile (`img_name: None`, qa_studio_server.py ~398/413/470/491): la foto de arranque `chNN_img_01.png` no aparece y no tiene «rehacer foto».
- «rehacer clip» (`_clipfix_core`, ~1194) edita SOLO el movimiento; la foto inicial no se toca y `foto_final_del_clip` reusa `_final` si existe. Los niños están en las dos fotos, así que el clip los repite.
Causa del contenido: el prompt de la foto dice «Posing stiffly for a family portrait» y «period box-camera framing»; Nano Banana lo obedece (niños + borde de diapositiva).

## Qué hace después
En todo cap con clip, la foto de arranque es un ítem más de QA, con su miniatura y «rehacer foto». Al rehacerla:
1. `_fix_image_core` (la misma de las demás fotos, PEDIDO_EDITAR_CASILLEROS sin cambiar) edita los casilleros del `image_prompt` del cap y genera con el motor activo (nb2_lite).
2. La foto final `_final` vieja va a backup (deriva de la foto vieja) y se rehace con `foto_final_del_clip`.
3. El clip se rehace con `_generate_clip` (G → K), mismo `video_prompt` aprobado, nueva foto inicial y final. Backup del mp4 viejo.
4. Manifest: `foto_arranque_md5` nuevo. `_invalidate_baked` del cap.
Todo de un solo botón: Omar no tiene que pedir el clip aparte.

## Constantes
| Valor | Origen | Quién |
|---|---|---|
| Motor foto: nb2_lite, respaldo Seedream 4.5 | DECISIONES 2026-11-01 (F68) | Omar |
| Motor clip: Gemini Omni Flash 1.1 1080p, respaldo Kling 4.0 | DECISIONES 29-oct | Omar |
| Costo por rehacer ≈ 2 × 0,042 + 1,20 US$ (se reporta, no es tope) | F68 / F68b | derivado |

## Módulos
- `qa_studio_server.py`: hoy el cap con clip no expone la foto de arranque y «rehacer clip» solo toca el movimiento → expone `chNN_img_01.png` como ítem rehacible y encadena foto → final → clip.
- `qa_studio.html`: hoy muestra solo el tile del clip → muestra también la foto de arranque con su botón.
- Nada en asset_manager, m03 ni prompts: se reusan las funciones de producción tal cual.

## Reglas
1. Cero reglas ni prompts nuevos; PEDIDO_EDITAR_CASILLEROS y PEDIDO_EDITAR_MOVIMIENTO byte a byte.
2. «rehacer clip» (solo movimiento) queda como está.
3. Lo viejo a backup, no se borra.
4. Tests sin red con deps inyectadas, como los de F59.
5. Prueba real: ch01 de Wittenoom con el pedido «solo Daniel, sin niños, sin borde de diapositiva». Salida: foto, final y primer cuadro del clip en `lab/hyperframes/f69/`, más los casilleros antes/después.
