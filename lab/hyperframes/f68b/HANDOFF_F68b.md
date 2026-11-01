# HANDOFF F68b — rehacer los 2 clips de Wittenoom desde las fotos Nano Banana

## Por qué
Los clips `ch01_veo/ch01_clip_01.mp4` (03:23) y `ch07_veo/ch07_clip_01.mp4` (03:34) son anteriores a las fotos de F68 (06:00–06:03): arrancan de la foto Seedream 5.0 con la cara deforme. En el video se ve el clip, no la foto, así que el gancho (ch01) sigue mostrando la cara fea. Omar lo vio (2026-11-01 07:32).

## Constantes
| Valor | Origen | Quién |
|---|---|---|
| Motor de clip: Gemini Omni Flash 1.1, 1080p | DECISIONES 29-oct | Omar |
| Respaldo por moderación: Kling 4.0 | DECISIONES 29-oct | Omar |
| Foto inicial = `chNN_img_01.png` y final = `chNN_img_01_final.png` actuales (Nano Banana, F68) | F68 | Omar (motor) |
| Costo esperado ≈ US$ 1,20 por clip (se reporta después, no es tope) | F68_REPORT, «abierto» 4 | derivado |

## Módulos
- `asset_manager.py` (rama de clips): hoy salta el cap si el mp4 existe. Sin cambio de código si moviendo el mp4 el camino normal rehace el clip con las fotos que ya están; si no, cambio mínimo para que use las fotos existentes y NO las regenere.
- Nada más. No se tocan guion, papel, voz, fotos, gfx ni render.

## Reglas
1. Las 4 fotos (`img_01`, `img_01_final` de ch01 y ch07) NO se regeneran: son las de F68.
2. Mismo prompt de movimiento que el clip anterior (no se suaviza para la moderación).
3. Clips viejos a `output/<topic>/_archivo_seedream5lite/clips/`, no se borran.
4. Los 2 clips en paralelo.
5. Manifest: el clip nuevo lleva el md5 de su foto inicial; borrar la marca `foto_de_arranque_cambio`.
