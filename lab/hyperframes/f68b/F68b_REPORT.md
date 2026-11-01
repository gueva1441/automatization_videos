# F68b — rehacer los 2 clips de Wittenoom desde las fotos Nano Banana

Handoff: `lab/hyperframes/f68b/HANDOFF_F68b.md` (md5 2a94eb888297f711aab7c7fa6af43505).

## Resultado

Los 2 clips nuevos salieron por Gemini Omni Flash 1.1, sin rechazos, sin Kling y sin cambios de código. Son de 8,00 s, 1920×1080 y sin audio. Arrancan de las fotos de F68: las 4 fotos tienen el mismo md5 antes y después.

**Para mirar: la foto del gancho trae 6 chicos que el prompt no pide.** `ch01_img_01.png` es de F68 y el clip nuevo la hereda. El prompt dice «posing stiffly for a family portrait» y «Spanish people with…», probable origen de los chicos; la voz habla de un hombre joven solo («Un hombre joven posa para un retrato con el pie vendado»). La cara ya no es la deforme, pero la escena cambió. Además, la foto tiene un borde negro redondeado de diapositiva, visible en el primer cuadro. No toqué nada porque la regla 1 prohíbe rehacer fotos. ch07 sale bien.

| | ch01 | ch07 |
|---|---|---|
| Primer cuadro nuevo vs. `img_01` de F68 | **0,774** | **0,721** |
| Primer cuadro viejo vs. `img_01` de F68 | 0,140 | 0,293 |
| Primer cuadro viejo vs. su foto vieja (control) | 0,878 | 0,755 |
| Último cuadro nuevo vs. `img_01_final` | 0,837 | 0,707 |
| md5 de la foto inicial, en el manifest | `5f3170e1…` | `1edad691…` |

El ssim no da 1 porque el motor reencodea, y el primer cuadro viejo contra su propia foto tampoco da 1. Sin umbral: ni DECISIONES ni el handoff lo fijan. Los clips nuevos se parecen a su foto casi como los viejos a la suya, y los viejos no se parecen a la foto nueva.

**Cuadros** (en esta carpeta): `ch01_nuevo_primer_cuadro.png`, `ch01_nuevo_cuadro_medio.png`, `ch07_nuevo_primer_cuadro.png`, `ch07_nuevo_cuadro_medio.png`. También el último cuadro y el primero del clip viejo, para comparar.

**Costo:** US$ 2,5131 según el rastreador: 2 clips a US$ 1,20 (tarifa medida en F52 × 8 s) + 2 prompts de Opus, US$ 0,1131 (por tokens reales). fal no devuelve el costo del clip por API, así que el dato final está en su panel.

**Manifest:** solo cambian las 2 filas de los clips: `status: ok`, `foto_arranque_md5`, `foto_final_md5`, `clip_motor`, `clip_rechazos`, `clip_segundos`, `clip_usd`, sin `foto_de_arranque_cambio`. `motor`, `segundos` y `usd` siguen siendo de la foto. Sello y fecha sin tocar. Clips viejos en `output/123bbb64-…/_archivo_seedream5lite/clips/`.

**Abierto:**
- `process_script` reescribe esas filas si se vuelve a correr (el clip vuelve a `skipped_exists` sin md5). `run_pipeline` hoy retoma en `fondos`, después de ese paso.
- `_fase2b_work/ch01_hybrid_visual.mp4` y el de ch07 siguen armados con los clips viejos. Solo se reusan con `--reuse-visuals` (`fase2b.py:1051`): con ese flag, el gancho saldría con la cara vieja. Sin él se rearman. No los toqué: fase2b está fuera de esta tanda.

## Etapa 0 — cómo se rehace un clip si se mueve su mp4 (solo lectura)

**Usa las fotos que ya existen; no las regenera. No hace falta cambiar `asset_manager.py`.**

`_process_veo_chapter` (`asset_manager.py:1634`), con el mp4 movido:

| Línea | Qué hace | Con Wittenoom |
|---|---|---|
| 1675 | `clip_path.exists()` | Falso: sigue |
| 1704 | Si `chNN_flux/chNN_img_01.png` existe, salta como «ya tiene fallback» y **no hace el clip** | Esa foto no existe en `ch01_flux` ni en `ch07_flux`: sigue |
| 1716 | Si falta la foto inicial, la genera | Existe: no se llama a Nano Banana |
| 1741 / 894 | `foto_final_del_clip` reusa `_final` si existe («reusada: ya existía») | Existe: no se llama a Opus ni a Nano Banana |
| 1746 | `_generate_clip(foto, video_prompt, clip, image_prompt, ancla=voz_clip, foto_final)` | Único paso que paga |

### Por qué no corro `process_script` entero

El camino normal reusa las fotos, pero tiene tres problemas para esta tanda. Por eso llamo a `_generate_clip`, la misma función, desde `rehacer_clips.py`:

1. **Es secuencial** (`process_script`, línea 1984): recorre los caps de a uno, y la regla 4 pide los 2 clips en paralelo.
2. **Reescribe el manifest entero:** las 97 fotos volverían como `skipped_exists` y perderían sus marcas de motor de F68.
3. **Si los dos motores rechazan, genera una foto** (`_ensure_fallback_image`, línea 1784), y la regla 1 lo prohíbe.

### El prompt de movimiento

- `_generate_clip` no le manda el `video_prompt` directo al motor. Opus lo reescribe para ese motor mirando las dos fotos (`PEDIDO_CON_FINAL`: «APPROVED MOTION (keep its intent, rewrite it for this model)»). Es el paso de producción desde F53b.
- **Lectura:** «mismo prompt» = el mismo `video_prompt` aprobado del guion, sin suavizar, pasando por esa cadena. No se guardó el texto que Opus escribió para los clips viejos, y aquel describía otras fotos.

El texto que se le mandó al motor queda en `clips_llamadas.json`.

## Veredicto de revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

Handoff md5 2a94eb88... coincide. Recalculé md5 de las fotos, ffprobe, ssim, manifest y git. No corrí pytest ni hice llamadas pagas.

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| E0 | Etapa 0: documentar cómo rehace el clip `asset_manager`, escrito en el REPORT | OK | F68b_REPORT.md, sección «Etapa 0». Cita `_process_veo_chapter` líneas 1675/1704/1716/1741/1746. Sin cambio de código: `git status` no muestra `asset_manager.py` ni `fase2b.py` tocados. No re-verifiqué cada número de línea, solo que el archivo no cambió. |
| 1 | Clips viejos movidos a `_archivo_seedream5lite/clips/`, no borrados | OK | `ch01_clip_01.mp4` 7,97 MB (23:23) y `ch07_clip_01.mp4` 13,6 MB (23:34), con la fecha vieja |
| 2 | 2 clips nuevos, en paralelo, Gemini Omni Flash 1.1 1080p, Kling solo si hay rechazo | OK | `rehacer_clips.py`: `ThreadPoolExecutor(max_workers=2)`. `clips_llamadas.json`: motor `gemini_omni_flash`, rechazos `[]`. ffprobe: h264 1920x1080 8,0 s ambos. |
| 3 | No regenerar fotos (regla 1) | OK | md5 de las 4 fotos: 5f3170e1, 914e951b, 1edad691, d0b71ed9. Coinciden con el manifest y con `fotos_antes == fotos_despues`. Fotos y `.llamada.json` con mtime 01:00 del 1-nov, anteriores al clip (07:37). El script frena si falta una foto. |
| 4 | Verificación ssim: nuevo parecido, viejo no | OK | Recalculé con ffmpeg: nuevo 0,774478 / 0,721283; viejo 0,140491 / 0,292947. Coincide con `verificacion_clips.json` y con el REPORT. El control viejo vs. su foto vieja (0,878 / 0,755) no lo recalculé. |
| 5 | PNG de primer cuadro y cuadro medio de cada clip nuevo en `f68b/` | OK | 8 PNG presentes, no vacíos (los 4 pedidos más último cuadro y primer cuadro viejo) |
| 6 | Manifest: md5 de la foto inicial y sin `foto_de_arranque_cambio` | OK | Filas ch01 y ch07: `foto_arranque_md5` correcto, la marca no está. Solo cambian las filas de los clips. `papel_md5` y `generated_at` intactos. No quedó `.tmp`. |
| 7 | Costo real al final | OK, con salvedad | US$ 2,5131 = 2×1,20 (tarifa medida en F52) + 2 Opus (0,1131). El REPORT dice que fal no devuelve el costo por API, así que el dato es estimado, no facturado. |
| 8 | Commit y ESTADO_SESION | NO VERIFICABLE | Se hacen después del veredicto; no es falla. |

Los 4 puntos que pediste juzgar:
(a) «mismo prompt» es defendible, pero no es literal. Se usó el `video_prompt` aprobado del guion; el script exige que sea idéntico al del manifest y al del guion. Pasó por la reescritura de Opus de `_generate_clip`, que es la cadena de producción. El texto que Opus había escrito para los clips viejos no se guardó, así que no se puede comparar. Lo que va al motor está en `clips_llamadas.json`. Opus ve las fotos y sí cambia la redacción: el prompt de ch01 menciona a «the children around him», «boy in the grey cardigan» y «girl in white». Omar debe decidir si esto es «mismo prompt».
(b) Llamar `_generate_clip` desde un script cumple el handoff. El handoff pide «en paralelo» (regla 4) y «sin regenerar fotos» (regla 1), y `process_script` es secuencial, reescribiría el manifest entero y generaría una foto si ambos motores rechazan. Es la misma función de producción, no hay cambio de código y el REPORT justifica el desvío. Costo: `process_script` no se ejercitó, y el REPORT admite que si se vuelve a correr pisa las filas con `skipped_exists` sin md5.
(c) La afirmación del REPORT es cierta. Vi `ch01_nuevo_primer_cuadro.png`. Aparecen 6 chicos junto al minero (dos niños y una niña a cada lado, y una niña de blanco detrás). El borde negro de esquinas redondeadas se ve en los cuatro lados. Eso viene de la foto de F68, no del clip. El gancho no quedó limpio: la cara ya no es la deforme, pero la escena no coincide con la voz («un hombre joven», solo).
(d) Río abajo en fase2b, con el manifest nuevo y sin tocar nada:
- `status: ok` y path `.mp4` tienen el mismo efecto que antes: `fase2b.py:1414-1417` solo desvía a `flux` si el status es fallback o el path es `.png`. Los campos nuevos no se leen.
- El sello `papel_md5` no cambió.
- Los clips duran 8,0 s, igual que los viejos, así que el timing no varía.
- Riesgo real: `_fase2b_work/ch01_hybrid_visual.mp4` y el de ch07 siguen armados con los clips viejos. Con `--reuse-visuals` (`fase2b.py:1051`) el gancho saldría con la cara vieja. El REPORT lo dice y no lo tocó, correcto por alcance.

Fuera de alcance: ninguno. Versionados modificados: `diag_234_cap4.py`, `f28a.log` y `pedido_paquetes_wittenoom.txt`, los 3 ya modificados antes de la tanda. El resto es no versionado, `lab/hyperframes/f68b/` más lo que ya había. Los cambios del manifest y de los mp4 en `output/` quedan fuera de git.

Riesgos que el contrato no cubre:
1. El ssim no tiene umbral (DECISIONES no lo fija); 0,72 y 0,77 son «parecidos» solo por comparación con el viejo (0,14 y 0,29).
2. El gancho de ch01 sale con 6 chicos y borde de diapositiva, y la regla 1 impidió corregirlo; hace falta una tanda que decida sobre la foto.
3. Si se vuelve a correr `process_script`, el manifest pierde las marcas de motor y el md5 de F68b.
