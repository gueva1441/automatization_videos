VEREDICTO: CUMPLE CON OBSERVACIONES. Una medida está mal (cuadros de entrada y salida de la ficha título) y hay que corregirla o declararla antes del commit.

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Sin flag, cada propiedad queda como hoy | OK | Generé el HTML con el código de HEAD (`git archive`) y con el de trabajo, con ficha, recorte, sello y reloj: `cmp` byte a byte idéntico, md5 `5527333649bc…`. `V1,S1P,R1` también da diff vacío. `forma_variante=""` es el default y no está en los perfiles. |
| 2 | V2 = fundido simple, con la duración de `title_fade_out` | OK | `gfx_project.py:370-380`: duración 0.4 en los dos sentidos; en el HTML generado salen `duration: 0.4`, `opacity` 0→1→0. |
| 3 | V3 = V2 + desplazamiento del alto de `#tc-line`, ease del title card | OK | `tc_metrics()["line_h"]`=6. Genera `y:6→0` y `0→-6`, con `power4.out` y `power2.in`. |
| 4 | Sello ×2/×3 con y sin placa; la placa es `rgba(10,10,10,.35)` | OK | S2 sale con 168 px, borde 14, aire 16/52/8. S3 con 252 px, borde 21, aire 24/78/12. La placa es la de siempre. Observación: «S1 como hoy» es S1P, porque el sello de hoy ya lleva placa; el reporte lo dice. |
| 5 | Reloj R2 = `tc_kicker_px` | OK | Genera 45 px = `round(64·0.7)`. R1 queda en 64. |
| 6 | Valores nuevos no etiquetados | PARCIAL | El borde y el aire por k son derivados declarados. V2 usa `ease:"none"` (lineal), una elección que el handoff no define y el reporte no menciona. En V2/V3 el recorte pierde la cascada del titular y queda en −2.5°; el reporte lo declara. |
| 7 | 11 corridas `--only-cap ch06`, rc 0, Firefox cerrado, RAM > 14 GB | OK | Los 11 `corrida.json` dan rc 0. `todas.out` dice «Firefox cerrado» antes de cada una. La RAM mínima va de 14.12 a 15.34 GB. Los 11 `gfx_plan_ch06.resolved.json` tienen el mismo md5 `caa6a48f…`, así que contenido y transiciones no se tocaron. |
| 8 | Clips `ch06_<variante>.mp4` | PARCIAL | Existen 11, de 2560×1440 con audio y 15.48 s cada uno. El handoff pedía ~40 s; el reporte lo explica (ch06 tiene solo 2 bloques). |
| 9 | Hoja: fila por bloque, columna por variante, 6 cuadros a 360 px y debajo el cuadro a 2560 | PARCIAL | Revisé `VARIANTES_ch06.jpg` (12360×1832): 2 filas × 11 columnas, con tira de 6 cuadros a 360 px en cada celda. Pero lo de abajo es un recorte 1:1 de 1080×420 y no el cuadro a 2560 (lectura declarada). En S3 y S3P el sello queda cortado arriba y abajo dentro de ese recorte. |
| 10 | Medidas: contraste WCAG y alto de letra a 360 px | OK | Los valores son consistentes y el método está declarado en el reporte y en `medidas()`. Mide el fondo inmediato al texto y no «la luma media bajo el bloque» como pedía el handoff; el reporte lo cuenta, no lo oculta. |
| 11 | Medidas: cuadros de entrada y salida reales | FALLA | En la ficha título la máscara blanca tiene un piso de ~1040 px aun sin texto (el fondo tiene blancos), que supera el 5 % del máximo (~735). Por eso `on[0]` es siempre el primer cuadro de la ventana (t0−0.3 s) y `on[-1]` el último. Los 18/20/14 de entrada y 14/19/15 de salida son «cuadros desde el borde de la ventana hasta el texto lleno». Medí cuadro a cuadro: el texto sube en unos 5 (V1), 3 (V2) y 2 (V3) cuadros. El kicker de la misma ficha da 7/6 en V2 contra 20/19 del título. El sello y el kicker rojo sí son reales, con piso 0, pero un umbral de color lee los fundidos más cortos que los 12 cuadros nominales. La explicación del reporte («el umbral estira los fundidos») es la contraria de lo que pasa. |
| 12 | Lo que ch06 no muestra está dicho | OK | El reporte dice que no hay recorte ni reloj, que R1 y R2 dan el mismo video y que el cap con reloj es ch04. Lo confirma el log: «reloj (cronología): no». El md5 `ch06_gfx.mp4` de R1 es idéntico al de R2. |
| 13 | md5 ch02 sin gfx = 38e5ba14… | OK | `c/verif.out` y `c/onlycap_ch02_nogfx.log` dan `38e5ba14e3d24fd20f9297c9e1dfee24`. |
| 14 | Tests | OK | `python -I -m pytest test_module_f31.py -q -p no:cacheprovider`: 4 passed. Los logs de la suite amplia (974 verdes + 5 previas) y la rápida (58) coinciden con el reporte. No los corrí de nuevo. |
| 15 | No se tocó contenido, transiciones, subtítulos ni velocidad | OK | El diff de código solo toca la forma del sello, la ficha, el recorte y el reloj. Los planes son idénticos entre corridas. |

Fuera de alcance: ningún archivo de código fuera de lo declarado.
- Tocados por F31: `fase2b.py`, `gfx_config.py`, `script_engine/gfx_project.py`, `test_module_f31.py`, `lab/hyperframes/f31/` y `lab/ESTADO_SESION.md`.
- No son de F31: `gfx_profiles/*`, `diag_234_cap4.py` y `f28a.log`.
- Efecto lateral fuera del repo: las 11 corridas pisaron `output/f8s3-vajont-f30/_fase2b_work/ch06_segment_only.mp4` y `ch06_gfx.mp4`. Hoy contienen la variante `V2,S2P,R2`.
  - El `ch06_gfx.mp4` de v5 quedó respaldado en `_bak_f31` (el más viejo, 181478798 B).
  - El `ch06_segment_only.mp4` de v5 no tiene respaldo.
  - El reporte no lo menciona.

Riesgos que el contrato no cubre:
- Un reensamblado o una reutilización de caché desde `_fase2b_work` arrastraría el ch06 con la variante, aunque nada está commiteado como default.
- Antes de pasar a Omar la tabla de medidas, hay que corregir o declarar las columnas de cuadros de la «ficha título». Con los valores actuales V3 parece rápida y V2 lenta, y la diferencia es un artefacto.
- V3 desplaza 6 px sobre 2560×1440 (ya en el handoff). Va a ser casi imperceptible, y la hoja no puede mostrarlo a 360 px.

Archivos relevantes: C:\CLAUDE_PROJECTS\automatization_videos\lab\hyperframes\f31\f31_variantes.py (`_mascara`, `medidas`), C:\CLAUDE_PROJECTS\automatization_videos\lab\hyperframes\f31\medidas.json, C:\CLAUDE_PROJECTS\automatization_videos\lab\hyperframes\f31\VARIANTES_ch06.jpg, y C:\CLAUDE_PROJECTS\automatization_videos\script_engine\gfx_project.py (líneas 360-380, 393-396, 410, 992-1003, 1080-1103).
