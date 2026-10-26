VEREDICTO: CUMPLE CON OBSERVACIONES

Los números del reporte coinciden con `b/medidas.json`, `b/v4/*` y los logs de gfx. Hay cuatro observaciones, ninguna cambia las cifras (detalle abajo).

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | B.1 v4 existe, render completo con los flags pedidos | OK | `ffprobe` da 1009.667 s, 2560x1440, h264+aac, 1 041 232 518 bytes (993 MiB). `render_v4.json` da rc 0 y pared 30.9 min. El runner llama a `fase2b` con `--reuse-visuals --gfx --gfx-sparse --rotulista`. RAM libre 19.3 GB, mínimo 15.1. |
| 2 | Costos | OK | `rotulista_costos.json`: 12 llamadas, suma 0.2336. Por cap coincide con la tabla (0.0112, 0.0356, 0.0389, 0.0389, 0.0406, 0.0228, 0.0456). Gemini 0.0006 está en `render_v4.out`. Paralelo 15.1 s en `prefetch.json`. |
| 3 | Tiempos de gfx y pared | OK | Los 7 caps suman 1576.7 s (el reporte dice 1 577). Coinciden con `render_v4.out` y `medidas.json`. Pared 30.9 contra v3b 37.1, que consta en `lab/ESTADO_SESION.md`. |
| 4 | Tabla por cap (B.3) | OK | Revisé propuestos 16, cantidad 2, lectura 8, candado 3, cortados por el crítico 1, en pantalla 2. Suman 16. Coinciden con los `rotulista: colocados/fuera` de `gfx_chNN.log` y con las crudas. Los beats pico salen de los logs y de `gfx_beats_chNN.json`. «En 5 de 7 caps el pico es el beat más largo» es cierto. |
| 5 | `a_pantalla` 5/5 o motivo exacto de cada faltante | OK | Hay 1 de 5. Los motivos de D117, Q50, D245 y D192 son textuales de `medidas.json` y de los logs. Los números de lectura cierran (82/15=5.5, 247/15=16.5, 63/15=4.2). |
| 6 | B.4 medidas | OK, con nota | Todas dan 0. D128 (123.87–134.57) y D32 (110.80–121.50) caen dentro de su escena y no la cruzan. Nota: «contradicciones» llama a la misma función que se prueba. «dos en escena» solo cuenta bloques del rotulista, y hay 1 por cap. Cumple, pero es una medida débil. |
| 7 | B.2 hoja `BLOQUES_v4.jpg` | PARCIAL | Existe (963 KB) y la vi como imagen. Tiene cuadro, miniatura de 360 px, `aporta`, crítico, beat y t en el mp4. Los t se verifican: 654.799+124.3+2.5=781.6, 823.199+112.5+2.5=938.2 y 484.899+92.5+2.5=579.9. Los cuadros muestran la ficha en esos t. La fila de T61 (cortado) dice «beat None · oración [None]» y trae «−1 / ANCLA / +1» todos en «—». El crítico de D32 está truncado («…relevante en la»). El título de D128 se corta en el borde. |
| 8 | Fixes de coherencia y de las obs. de A en `gfx_rotulista.py` | OK | La regla de «mismos dígitos» salió y entró `_DIFERENCIA`. La tolerancia de 0.05 s salió. El rank sin valor pasa a `len(bl)+1`. El title card marca todas las escenas que pisa. Los tests nuevos están en `test_module_f29c_rotulista.py:183-185`. |
| 9 | Tests | OK | En el árbol actual, 32 pasan (F29c + F29b). Armé una copia de HEAD con solo los 6 hunks de B de `gfx_rotulista.py` (sin los 3 de `pre_roll`) y el test nuevo, y también dan 32. Hizo falta copiar `gsap.min.js`, que no está en git. Los hunks de `pre_roll` están separados de los de B, así que el staging parcial es posible. |
| 10 | Pendientes de Omar y lecturas declaradas | OK | Hay 4 pendientes: `a_pantalla` en el mismo beat, lectura por corte de escena, pico por cap y etiqueta con año. Las lecturas 1–5 están declaradas en el reporte. No hay números nuevos fuera de §0 en lo de B. |
| 11 | `lab/ESTADO_SESION.md` | PARCIAL | El diff dice «F29c B: render v4 en curso». Es falso, el render terminó. Falta el hito de B y la PARADA. |
| 12 | Frenos (sellos, templates, `.env`, `output/`) | OK | B no toca `gfx_templates`, `output/` ni `config.py`. `output/` no aparece en `git status`. |

Observaciones para antes del commit y la lectura de Omar:
1. Actualizar `lab/ESTADO_SESION.md` con el resultado de B (fila 11).
2. La hoja no trae voz ni beat para T61. Si el contrato exige voz por fila, falta eso (fila 7).
3. D32 «uno se suicidó» repite lo que dice la oración −1 de la voz («Pancini… se quitó la vida»). Eso toca la condición (a) del prompt. El código solo chequea números, nombres y años, y el crítico lo dejó pasar. Lo tiene que juzgar el analista con la hoja.
4. La lista de lo que salió en la validación del prefetch omite D245. En `rotulista_ch07.raw.json` D245 aparece rechazado por coherencia con el código viejo, no por lectura como en el render.

Fuera de alcance: ninguno dentro de B. En el árbol hay cambios de F30b (`gfx_style`, `gfx_sparse`, `gfx_project`, `transition_applier`, `fase2b`, `gfx_layer`, `gfx_critic`, `gfx_config`, `test_module_f30b.py`, `lab/hyperframes/f30b/`) y los `gfx_profiles/*` y `diag_234_cap4.py`. Ninguno debe entrar al commit de B. Mientras no se haga el staging por hunks, los 3 hunks de `pre_roll` de `gfx_rotulista.py` quedan sin commitear.

Riesgos que el contrato no cubre:
- Los archivos de F30b se editaron entre las 03:33 y las 03:39, y el render corrió de 03:28 a 03:58. Los módulos ya estaban cargados y los cuadros de la hoja coinciden con lo esperado. Aun así, v4 no es reproducible bit a bit desde el commit de B.
- El tipo `persona` tiende a cortarse por el crítico (T61 salió por la pregunta 2: «ya identifica al director»), porque el prompt le pide justo nombrar a quien la voz ya nombra. Con la regla actual es casi seguro que se corte siempre.

Rutas: `C:\CLAUDE_PROJECTS\automatization_videos\lab\hyperframes\f29c\F29c_REPORT.md`, `C:\CLAUDE_PROJECTS\automatization_videos\lab\hyperframes\f29c\b\medidas.json`, `C:\CLAUDE_PROJECTS\automatization_videos\lab\hyperframes\f29c\BLOQUES_v4.jpg`, `C:\CLAUDE_PROJECTS\automatization_videos\output\f8s3-vajont-f30\f8s3-vajont_final_gfx_v4.mp4`.
