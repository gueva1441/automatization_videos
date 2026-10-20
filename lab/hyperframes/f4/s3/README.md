# F4 §3 — ¿HyperFrames escala el clip de video?

Pruebas (scripts `probe_vscale*.py`, HyperFrames 0.8.172):

| prueba | qué | resultado |
|---|---|---|
| 1 | 640×360 sintético, `scale 1.5` en `#vw` (contenedor), en el `<video>` y por CSS | las 3 escalan (dif vs escalado 2.2, vs sin escala 39.1) |
| 2 | 1280×720, tween animado con `transformOrigin`, calidad looks | escala (16.0 vs 35.7) |
| 3 | dos escenas, el tween en la escena 2 (`data-media-start` 2 s) | escala (16.1 vs 37.1) |
| 4 | clip DepthFlow real de ch05 (2560×1440), zoom de evidencia SIN cuadro congelado, render looks, con y sin grade CSS | el video se acerca (imagen `zoom_sin_congelado_render_snapshot_base.png`: render · snapshot · base) |
| 5 | render de F3 de ch02 ANTERIOR al arreglo C64 (`ch02_gfx.pico_v1.mp4`, 59.6 s) | ya estaba acercado 2.2× (`f3_prefix_render_vs_base_ch02_59s6.png`) |

**Conclusión:** el frame que HyperFrames inyecta en el render es hermano del `<video>` dentro de `#vw`, así que hereda la escala del contenedor. El diagnóstico C64 de F3 no se sostiene en el render ni en el snapshot (probablemente se vio en el preview del navegador). El golpe de zoom, el empuje del mood muerte y el corte + golpe ya escalaban el clip. Lo único que cambió en §3: el zoom de evidencia deja de usar el cuadro congelado en producción (token `zoom_freeze_frame`, false), así el clip 3D/Veo sigue moviéndose durante el zoom. El lab lo conserva (no se pudo verificar su player).

## Verificación en los caps pedidos (render real F4, `--only-cap --gfx --gfx-sparse`, looks)

`measure_punch_ch01_ch04.py`: escala que mejor alinea el cap con gfx contra su base (búsqueda 1.000–1.030, centro del cuadro).

| cap | clip | golpe de zoom | antes del golpe | después del golpe |
|---|---|---|---|---|
| ch01 | híbrido (Veo), escena 0 | 4.279 s | 1.000 (dif 1.7) | **1.015** (dif 2.7) |
| ch04 | DepthFlow 3D, escena 1 | 8.72 s | 1.000 (dif 1.4) | **1.015** (dif 17.5: hay texto encima) |

El golpe suave (1.015) escala el clip de video en los dos. ch01 y ch04 no tienen empuje de muerte ni corte + golpe en F4; usan el mismo `tl.to("#vw…")`, cubierto por las pruebas 1–4.
