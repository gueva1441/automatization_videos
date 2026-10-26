# F31 — Laboratorio de forma: variantes para que Omar elija · REPORTE

CC · 2026-10-26 (tanda nocturna) · rama `f11-guion-v4`, base = F30b C `a19dbbc`. Handoff `HANDOFF_F31_lab_forma.md`; tanda `../f29c/PROMPT_CC_tanda_nocturna_F29c_F30b_F31.md` (etapa 3). Un commit. API: Claude 0, Gemini 0.

**En una línea:** las variantes viven detrás de `fase2b --forma-variante` (el default de cada propiedad queda exactamente como hoy: test), y salen las 11 corridas `--only-cap ch06` con los planes de v5, los 11 clips de los tramos con bloque, la hoja `VARIANTES_ch06.jpg` (celdas a 360 px) y las medidas. **No se decide nada.**

## Flags (`--forma-variante V,S,R`; sin el flag, como hoy)
| eje | valor | qué hace | de dónde sale el valor |
|---|---|---|---|
| V entrada/salida de ficha y recorte | V1 | como hoy (ficha: wipe del title card + raya; fundido de salida · recorte: cae con giro y cascada; fundido de salida) | — |
| | V2 | fundido simple al entrar y al salir, entero, con la duración del fundido del title card | `title_fade_out` = 0.4 s |
| | V3 | V2 + desplazamiento vertical del alto de la raya del title card, curvas del title card | `#tc-line` 6 px; `power4.out` / `power2.in` |
| S sello | S1 · S2 · S3 | el sello de hoy ×1 · ×2 · ×3 (cuerpo, borde y aire juntos) | `emphasis_stamp_px` (84 en el perfil), borde 7 px, aire 8/26/4 px |
| | …P | con placa `rgba(10,10,10,.35)`; sin P, sin placa | la de `.co-text.stamp` |
| R reloj | R1 · R2 | 64 px (hoy) · al tamaño del kicker del title card | `tc_kicker_px` = 45 px |

Ojo con «hoy»: **el sello de hoy ya lleva la placa** (`background:rgba(10,10,10,.35)` en línea, `gfx_project`), así que «S1 como hoy» = **S1P**; S1 sin P le saca la placa. El handoff decía «nada lleva placa».

## Las 11 corridas (§B.1)
| # | etiqueta | flag | grupo | rc | pared s | RAM mín GB | clip |
|---|---|---|---|---|---|---|---|
| 1 | V1_S2P_R2 | `V1,S2P,R2` | V | 0 | 344.7 | 14.76 | `ch06_V1_S2P_R2.mp4` (15.5 s) |
| 2 | V2_S2P_R2 | `V2,S2P,R2` | V | 0 | 355.8 | 15.28 | `ch06_V2_S2P_R2.mp4` (15.5 s) |
| 3 | V3_S2P_R2 | `V3,S2P,R2` | V | 0 | 352.6 | 15.29 | `ch06_V3_S2P_R2.mp4` (15.5 s) |
| 4 | V2_S1_R2 | `V2,S1,R2` | S | 0 | 355.7 | 15.23 | `ch06_V2_S1_R2.mp4` (15.5 s) |
| 5 | V2_S1P_R2 | `V2,S1P,R2` | S | 0 | 403.6 | 14.98 | `ch06_V2_S1P_R2.mp4` (15.5 s) |
| 6 | V2_S2_R2 | `V2,S2,R2` | S | 0 | 387.8 | 14.94 | `ch06_V2_S2_R2.mp4` (15.5 s) |
| 7 | V2_S2P_R2_b | `V2,S2P,R2` | S | 0 | 355.8 | 14.16 | `ch06_V2_S2P_R2_b.mp4` (15.5 s) |
| 8 | V2_S3_R2 | `V2,S3,R2` | S | 0 | 354.8 | 15.34 | `ch06_V2_S3_R2.mp4` (15.5 s) |
| 9 | V2_S3P_R2 | `V2,S3P,R2` | S | 0 | 355.6 | 15.15 | `ch06_V2_S3P_R2.mp4` (15.5 s) |
| 10 | V2_S2P_R1 | `V2,S2P,R1` | R | 0 | 355.7 | 14.12 | `ch06_V2_S2P_R1.mp4` (15.5 s) |
| 11 | V2_S2P_R2_c | `V2,S2P,R2` | R | 0 | 357.6 | 15.1 | `ch06_V2_S2P_R2_c.mp4` (15.5 s) |

Cada corrida: `fase2b f8s3-vajont-f30 --only-cap ch06 --reuse-visuals --gfx --gfx-sparse --gfx-quality looks --rotulista --forma-variante …` (`f31_variantes.py todas`), en fila, Firefox cerrado y RAM libre > 14 GB antes de cada una (18.8–19.1 GB). Los planes, bloques y transiciones salen de los de v5 (rotulista y crítico de caché: **US$ 0.0000** en las 11). Segmento, plan y log de cada una en `corridas/<etiqueta>/`.
- **Las combinaciones repetidas** (V2,S2P,R2 aparece en los tres grupos: corridas 2, 7 y 11) dan el **mismo `ch06_gfx.mp4` byte a byte** (md5 `fe31ba57…`): el render es determinista. **La 10 (R1) también es idéntica**: ch06 no tiene reloj (abajo).
- **Clips** `ch06_<etiqueta>.mp4`: los tramos con bloque ± una oración, concatenados: 22.9–28.5 s (sello) + 126.8–136.8 s (ficha) = **15.5 s** cada uno (el handoff calculaba ~40 s; ch06 tiene solo 2 bloques).

## Medidas (§B.3)
| variante | bloque · parte | contraste WCAG (≥ 4.5) | cuadros de entrada | cuadros de salida | cuerpo a 2560 | alto de mayúscula a 360 px |
|---|---|---|---|---|---|---|
| V1_S2P_R2 | sello «fisura» · sello | 1.7 (no) | 1 | 2 | 168 px | 20.3 px |
| V1_S2P_R2 | ficha D128 · ficha título | 5.99 (sí) | 5 | 3 | 133 px | 16.1 px |
| V1_S2P_R2 | ficha D128 · ficha kicker | 1.19 (no) | 5 | 5 | 45 px | 5.4 px |
| V2_S2P_R2 | sello «fisura» · sello | 1.7 (no) | 1 | 2 | 168 px | 20.3 px |
| V2_S2P_R2 | ficha D128 · ficha título | 5.99 (sí) | 3 | 4 | 133 px | 16.1 px |
| V2_S2P_R2 | ficha D128 · ficha kicker | 1.19 (no) | 7 | 6 | 45 px | 5.4 px |
| V3_S2P_R2 | sello «fisura» · sello | 1.7 (no) | 1 | 2 | 168 px | 20.3 px |
| V3_S2P_R2 | ficha D128 · ficha título | 6.01 (sí) | 2 | 3 | 133 px | 16.1 px |
| V3_S2P_R2 | ficha D128 · ficha kicker | 1.2 (no) | 5 | 5 | 45 px | 5.4 px |
| V2_S1_R2 | sello «fisura» · sello | 1.37 (no) | 1 | 3 | 84 px | 10.2 px |
| V2_S1_R2 | ficha D128 · ficha título | 5.99 (sí) | 3 | 4 | 133 px | 16.1 px |
| V2_S1_R2 | ficha D128 · ficha kicker | 1.19 (no) | 7 | 6 | 45 px | 5.4 px |
| V2_S1P_R2 | sello «fisura» · sello | 1.54 (no) | 1 | 4 | 84 px | 10.2 px |
| V2_S1P_R2 | ficha D128 · ficha título | 5.99 (sí) | 3 | 4 | 133 px | 16.1 px |
| V2_S1P_R2 | ficha D128 · ficha kicker | 1.19 (no) | 7 | 6 | 45 px | 5.4 px |
| V2_S2_R2 | sello «fisura» · sello | 1.37 (no) | 1 | 2 | 168 px | 20.3 px |
| V2_S2_R2 | ficha D128 · ficha título | 5.99 (sí) | 3 | 4 | 133 px | 16.1 px |
| V2_S2_R2 | ficha D128 · ficha kicker | 1.19 (no) | 7 | 6 | 45 px | 5.4 px |
| V2_S2P_R2_b | sello «fisura» · sello | 1.7 (no) | 1 | 2 | 168 px | 20.3 px |
| V2_S2P_R2_b | ficha D128 · ficha título | 5.99 (sí) | 3 | 4 | 133 px | 16.1 px |
| V2_S2P_R2_b | ficha D128 · ficha kicker | 1.19 (no) | 7 | 6 | 45 px | 5.4 px |
| V2_S3_R2 | sello «fisura» · sello | 1.13 (no) | 0 | 1 | 252 px | 30.5 px |
| V2_S3_R2 | ficha D128 · ficha título | 5.99 (sí) | 3 | 4 | 133 px | 16.1 px |
| V2_S3_R2 | ficha D128 · ficha kicker | 1.19 (no) | 7 | 6 | 45 px | 5.4 px |
| V2_S3P_R2 | sello «fisura» · sello | 1.53 (no) | 0 | 1 | 252 px | 30.5 px |
| V2_S3P_R2 | ficha D128 · ficha título | 5.99 (sí) | 3 | 4 | 133 px | 16.1 px |
| V2_S3P_R2 | ficha D128 · ficha kicker | 1.19 (no) | 7 | 6 | 45 px | 5.4 px |
| V2_S2P_R1 | sello «fisura» · sello | 1.7 (no) | 1 | 2 | 168 px | 20.3 px |
| V2_S2P_R1 | ficha D128 · ficha título | 5.99 (sí) | 3 | 4 | 133 px | 16.1 px |
| V2_S2P_R1 | ficha D128 · ficha kicker | 1.19 (no) | 7 | 6 | 45 px | 5.4 px |
| V2_S2P_R2_c | sello «fisura» · sello | 1.7 (no) | 1 | 2 | 168 px | 20.3 px |
| V2_S2P_R2_c | ficha D128 · ficha título | 5.99 (sí) | 3 | 4 | 133 px | 16.1 px |
| V2_S2P_R2_c | ficha D128 · ficha kicker | 1.19 (no) | 7 | 6 | 45 px | 5.4 px |

Método (`f31_variantes.py medidas`, `medidas.json`): el texto se detecta por su color en la zona del bloque (blanco del dato; rojo del acento en el kicker y el sello) cuadro a cuadro; el contraste WCAG es la luminancia relativa media del texto contra la de su fondo inmediato (el recuadro del texto menos el texto dilatado), en el cuadro con más texto; la entrada y la salida, los cuadros entre el 5 % y el 95 % del texto, descontado el piso de ese color en el fondo (la mediana de los 0.25 s antes del bloque: la foto tiene blancos que el umbral cuenta como texto). Se reportan, no se juzgan. Dos intentos anteriores (contra el visual base sin gfx y contra el mismo segmento 0.15 s antes) quedaron descartados: las escenas safe vienen cocidas desde el PNG y la imagen tiene empuje de cámara, así que no había un fondo «sin bloque» comparable.
- **Ficha**: el dato blanco da ~6.0:1 en las tres V (pasa 4.5); el **kicker rojo da 1.2:1** y a 360 px su mayúscula mide **5.4 px**. La entrada del dato mide **5 cuadros (V1, wipe), 3 (V2, fundido) y 2 (V3, fundido + subida)**; la salida 3 · 4 · 3. El umbral de color lee los fundidos **más cortos** que los 12 cuadros nominales (0.4 s): el texto blanco cuenta recién cerca de la opacidad plena. *La primera versión de esta medida contaba desde el borde de la ventana (no descontaba el piso de blancos del fondo) y daba 18/20/14: la corrigió el revisor; los números de arriba son los corregidos.*
- **Sello**: rojo sobre la roca, **1.1–1.7:1** en todas; la placa sube el contraste (S1 1.37 → S1P 1.54; S2 1.37 → S2P 1.70) y el tamaño lo baja un poco (más borde rojo dentro del recuadro). Mayúscula a 360 px: S1 10.2 px · S2 20.3 · S3 30.5.
- **Reloj**: sin medida (no está en ch06). R1 64 px → mayúscula 7.7 px a 360; R2 45 px → 5.4 px (cuenta con la métrica de Anton).

## Hoja `VARIANTES_ch06.jpg` (§B.2)
Una fila por bloque de ch06, una columna por variante. Cada celda: 6 cuadros a 360 px de ancho (2 de la entrada, 2 de la mitad, 2 de la salida) y debajo el recorte del bloque a 2560 (1:1, la zona del bloque: el cuadro entero a 2560 por celda no entra en una hoja legible).

## Lo que ch06 no muestra
En los planes de v5, ch06 tiene **la ficha D128 y el sello «fisura»**; no tiene recorte ni reloj (el cap no avanza de fecha: `reloj (cronología): no` en el log de gfx). Entonces: V se ve solo en la ficha; **R1 y R2 dan el mismo video en ch06** (el eje no aparece). Las corridas igual se hicieron (el pedido son 11); si Omar quiere ver el reloj, el cap con reloj en v5 es ch04 (10.6 s).

## Tests
`test_module_f31.py` (4): sin flag todo como hoy (ficha con wipe, recorte de siempre, sello 84 px con borde 7 y placa, reloj 64 px); V2/V3 entran y salen enteros; S1 sin placa, S3P ×3 con placa, R2 a 45 px; el flag existe y no es default. Suite amplia **974 verdes + 5 previas**, suite rápida 58, md5 `--only-cap ch02` sin `--gfx` (`--sw-encode`) **`38e5ba14…`** (`c/`).

## Lecturas de CC (declaradas)
1. «El doble / el triple» del sello = cuerpo, borde y aire juntos (el sello entero escala; si solo creciera el cuerpo, el borde de 7 px quedaría finito).
2. V2/V3 en el recorte: el papel queda con la inclinación final de hoy (−2.5°) y el titular sin cascada (entra entero). La ficha en V2/V3 entra entera (kicker, dato y raya juntos).
3. «Debajo el cuadro a 2560»: el recorte 1:1 de la zona del bloque (1080 × 420 px) por celda, no el cuadro entero (11 cuadros de 2560 por fila no entran en una hoja que se pueda leer).
4. Las 11 corridas son las del handoff aunque 3 coincidan (V2,S2P,R2 en los tres grupos) y R no aparezca en ch06: sirvieron para probar que el render es determinista.

## Veredicto del revisor-handoff (íntegro)

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

**Después del veredicto (CC):**
- Fila 11 (FALLA, cuadros de entrada/salida del dato de la ficha): corregida. La medida ahora descuenta el piso de blancos del fondo (mediana de los 0.25 s antes del bloque) y da 5 · 3 · 2 cuadros de entrada (V1 · V2 · V3), lo mismo que midió el revisor; tabla y texto rehechos, y la explicación del umbral dada vuelta (lee los fundidos más cortos, no más largos).
- Fila 6: V2 usa curva lineal (`ease: "none"`): el handoff dice «fundido simple» sin curva; queda declarado acá. V3 usa las del title card.
- Fila 9: el recorte 1:1 corta el sello S3 arriba y abajo (el sello ×3 no entra en 420 px de alto); el cuadro entero a 2560 de cada corrida se saca del segmento en `corridas/<etiqueta>/` (declarado como lectura 3).
- Efecto lateral en `output/`: el `ch06_gfx.mp4` de v5 volvió a `_fase2b_work/` (el respaldo de `_bak_f31`, 181 478 798 B); el de la última variante y su `ch06_segment_only.mp4` quedaron apartados en `_bak_f31/` (nada se borró). El segmento de v5 que cuenta es `seg_06_ch06.mp4` (`--keep-segments`), que las corridas `--only-cap` no tocan; el `ch06_segment_only.mp4` de v5 no tenía respaldo y no se usa en ningún ensamble.
- Riesgo 3 (V3 desplaza 6 px, casi no se ve a 360 px): es el valor del handoff; Omar lo ve en los clips a 2560.

