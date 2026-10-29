# F52b — rehacer los 8 prompts de video: fichas en inglés y Opus mira la foto (lab) · PARADA antes de los clips

CC → Omar / analista · 2026-10-29 · rama `f11-guion-v4` · solo `lab/hyperframes/f52/` · gasto de F52b **US$ 0,2861**; acumulado de la tanda F52 **US$ 0,4767 de 16** · handoff `HANDOFF_F52b_prompts_con_foto.md`, md5 `716fd22f189b13c6a6c8494b22c5fb10` (coincide).

## Commits
| etapa | commit | qué |
|---|---|---|
| 0 | `d8b98ce` | DECISIONES 13:50 tal cual (incluye el handoff, md5 en el mensaje) + `prompts_f52_v1.json` (copia byte a byte del `prompts_f52.json` de F52) |
| 1 | `cefc1dc` | `guias/{K,S,F,G}.md` en inglés, tal cual del handoff |
| 2 | `80bd71a` | `prompts_video.py` con la foto, `prompts_f52.json` nuevo, `PROMPTS_F52.md`, `lectura_f52b.json` |
| cierre | (este) | reporte y ESTADO |

No se tocó producción (`git diff --name-only 5b56c8d..HEAD`: solo `DECISIONES.md` y `lab/hyperframes/f52/`). No se regeneraron las fotos: el md5 de `cap01.png` (`7f55f96b…`) y de `cap07.png` (`b343bef3…`) es el mismo antes y después. No se corrió la etapa 3: no hay ningún mp4 en `f52/`.

## Etapa 0
`tail -1 DECISIONES.md`:
```
- 2026-10-29 13:50 · **F52b:** fichas de guía de video en inglés y Opus escribe el prompt de video mirando la foto real (si difiere del image_prompt, manda la foto); solo lab · Omar · F52b
```

## Etapa 1
Las 4 fichas se reemplazaron por el texto en inglés del handoff, copiado por script desde el propio handoff (`**K — Kling 4.0** …`, `**S — …`, `**F — …`, `**G — …`).

## Etapa 2
`prompts_video.py`:
- Por cada modelo y clip, el contenido del mensaje es una lista: primero la foto del cap en base64, como bloque `image`; después el pedido de F52b tal cual, que es el de F52 más la línea FIRST FRAME.
- El `body` se arma en el script de lab y sale por `claude_helpers._post` (sin tocar `claude_helpers`). El costo va por `_track`.
- Opus 5.5 con effort high, 8 llamadas en paralelo.

**Primer intento: 8 × HTTP 400, sin cobro.** El mensaje literal fue «The image was specified using the image/png media type, but the image appears to be a image/jpeg image». Seedream devuelve JPEG por defecto, y el camino de producción lo guarda con extensión `.png`. El script ahora lee el tipo de la foto desde sus primeros bytes. El registro de ese intento en `cost_history` es de US$ 0,00, sin entradas.

**Segundo intento: 0 errores, US$ 0,2861.** Las palabras de cada uno, al lado de su v1, y mi línea («¿nombra el encuadre real? ¿en inglés?»):

| clip | modelo | v1 | F52b | en inglés | encuadre real |
|---|---|---|---|---|---|
| cap 1 | K | 309 | 320 | sí (v1 en castellano) | sí, «full figure»; pie «lifted slightly forward». Dice «left foot», pero en la foto es el derecho |
| cap 1 | S | 139 | 152 | sí | sí, «full-length»; pie «resting on its tip» |
| cap 1 | F | 110 | 122 | sí | sí, «full-length»; pie «lifted just off the ground» |
| cap 1 | G | 156 | 167 | sí | sí, «full-length shot»; pie «resting lightly on its toes» |
| cap 7 | K | 275 | 302 | sí (v1 en castellano) | sí, pala a la izquierda y arroyo hacia abajo a la derecha |
| cap 7 | S | 136 | 161 | sí | sí, «the stream on the right» |
| cap 7 | F | 111 | 115 | sí | en parte: no ubica la pala, pero pide «the same framing … as the first frame» |
| cap 7 | G | 171 | 165 | sí | sí, «the shovel left of center» |

Los 8 prompts enteros, cada uno al lado del v1 y con mi línea, están en **`lab/hyperframes/f52/PROMPTS_F52.md`**.
- **Los v1 decían plano medio.** En el cap 1, los 4 decían «start on the medium shot» o algo equivalente. Los 4 nuevos parten del cuerpo entero.
- **Lo que pedían las fichas:** K sigue con «[General settings] / [Sequence] / [Audio]», ahora en inglés. S sigue con rangos 0–3 / 3–6 / 6–8 s. F sigue siendo una sola oración y cierra con «no on-screen text, no subtitles». G cierra con «no captions».

## Gasto
| paso | US$ |
|---|---|
| F52b 1.er intento (8 × HTTP 400) | 0,0000 |
| F52b 8 prompts con foto | 0,2861 |
| F52 (fotos 0,07 + prompts v1 0,1206) | 0,1906 |
| **acumulado F52 desde 13:29:18** | **0,4767 de 16,00** |

El handoff estimaba ≈ US$ 0,15; la diferencia son los tokens de la imagen, que va en las 8 llamadas.

## Lo que queda abierto
1. **PARADA:** el analista revisa los 8 en `PROMPTS_F52.md`. La etapa 3 (clips) no corre hasta el «sigue» de Omar.
2. **Kling cap 1 dice «left foot»**, y en la foto el pie vendado es el derecho del minero. Una orden de izquierda o derecha que contradice el primer cuadro puede hacer que el modelo cambie de pie. No lo corregí, porque el pedido no se ajusta.
3. **El pie, según cada modelo:** S y G lo dejan «apoyado en la punta»; K y F, «levantado». La foto lo muestra adelantado, con la punta apenas tocando el suelo, así que las dos lecturas valen.
4. **G sigue largo:** 167 y 165 palabras, aunque su ficha pide prompts cortos.
5. **Las fotos son JPEG aunque se llamen `.png`.** Pasa igual en producción, porque Seedream devuelve JPEG por defecto. Hay que tenerlo en cuenta si la etapa 3 o producción mandan la foto declarando el tipo por la extensión. Los schemas de fal aceptan JPEG.
6. **Siguen abiertos de F52:** ningún modelo tiene campo de tolerancia; K y G no dejan apagar el audio; el precio por resolución no se pudo leer; el pie de la foto del cap 1 sale en un ángulo raro.
7. **No corrí las suites:** la tanda no toca código de producción ni tests.

## Veredicto de revisor-handoff
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Handoff md5 716fd22f… | OK | `md5sum` del handoff da 716fd22f189b13c6a6c8494b22c5fb10 |
| 2 | Etapa 0: línea DECISIONES 13:50 tal cual | OK | `git diff 5b56c8d HEAD -- DECISIONES.md` agrega la línea idéntica a la del handoff (commit d8b98ce) |
| 3 | `prompts_f52_v1.json` = `prompts_f52.json` de 7b8d838 | OK | El contenido es idéntico: md5 2c123d23… en el blob de 7b8d838 y en el de d8b98ce. El archivo del disco da cce8d2d6… porque tiene saltos de línea CRLF; sin los `\r` coincide. |
| 4 | Etapa 1: las 4 fichas en inglés tal cual | OK | `guias/{K,S,F,G}.md` coinciden palabra por palabra con el handoff líneas 25–34 (diff 5b56c8d..HEAD) |
| 5 | PEDIDO del script = bloque del handoff | OK | `prompts_video.py:36-47` es idéntico al handoff 39–50, con la línea FIRST FRAME. `prompts_f52.json` guarda el pedido enviado. |
| 6 | La foto va como bloque `image` antes del texto, sin tocar `claude_helpers` | OK | `prompts_video.py:62-65`: contenido en lista, imagen primero y texto después. Sale por `ch._post`. El tipo se lee de los bytes (las fotos son JPEG con extensión .png). |
| 7 | 8 llamadas, Opus 5.5 high, en paralelo | OK | `prompts_f52.json`: `claude-opus-5-5`, `high`, 8 entradas con `end_turn`, 0 errores. `ThreadPoolExecutor` en `prompts_video.py:160`. |
| 8 | Fotos sin regenerar | OK | md5 de `cap01.png` (7f55f96b…) y `cap07.png` (b343bef3…) iguales a `git show 8347f5e` |
| 9 | Sin mp4 (no se corrió la etapa 3) | OK | `find f52 -name '*.mp4'` no devuelve nada |
| 10 | Producción sin cambios | OK | `git diff --name-only 5b56c8d HEAD` solo toca `DECISIONES.md` y `lab/hyperframes/f52/`. Los 3 archivos modificados del status son previos a la tanda. |
| 11 | Salida PROMPTS_F52.md con v1, palabras y una línea por prompt | OK | `PROMPTS_F52.md` es de 161 líneas. `lectura_f52b.json` tiene 8 líneas y `escribir_md` imprime v1, F52b y palabras. Las palabras del reporte coinciden con las que conté sobre `prompts_f52.json`. |
| 12 | Las líneas de «encuadre real» y «en inglés» son verdaderas | OK | Vi `cap01.png`: cuerpo entero, pie vendado adelantado con la punta casi tocando el suelo. Ningún prompt nuevo dice «medium shot» ni tiene acentos. |
| 13 | Costo y tope (US$ 16) | OK | `usd_total` 0,2861 y `cost_history` con `f52b_lab_prompts`. Un registro previo sin entradas ni cobro corresponde al intento con HTTP 400. El acumulado de 0,4767 cuadra. |
| 14 | `F52b_REPORT.md` con lo abierto y el veredicto íntegro | PARCIAL | Existe y tiene lo abierto (7 puntos). El veredicto es `{{VEREDICTO}}` y el archivo está sin commit. |

Observaciones:
- **Pie izquierdo/derecho (K cap 1):** el reporte acierta. Dice «left foot» y en la foto el pie vendado está a la izquierda del cuadro, o sea es el pie derecho del minero. El reporte lo declara como abierto.
- **Mojibake al imprimir:** `�` en los guiones de la consola, solo al imprimir en la terminal. No afecta al contenido del archivo.
- **cap07_F:** no ubica la pala en el cuadro. El reporte lo marca «en parte», lo cual es correcto.

Fuera de alcance: ninguno. `ENTRADA_ANALISTA_2026-10-28e.md` y `ENTRADA_ANALISTA_2026-10-29f.md` están sin trackear en `f52/` y no son de esta tanda.

Riesgos que el contrato no cubre:
- El pedido manda la foto, pero nada obliga a que el prompt de video acierte el lado del cuerpo. Un error de izquierda/derecha puede hacer que el modelo cambie de pie.
- El tipo de imagen se declara por los bytes. Si la etapa 3 o producción lo declaran por la extensión .png, vuelve el HTTP 400 y fal puede rechazar la foto.
- La comparación K/S/F/G queda sesgada por la longitud (K 320 y 302 palabras contra F 122 y 115), por lo que las fichas inducen formatos muy distintos.

### Adenda de CC (después del veredicto)
- **#14:** el veredicto queda pegado y el reporte con commit, junto con ESTADO, en el commit de cierre.
- **Riesgo 3, la longitud:** es lo que pide cada ficha («structure … [Sequence] 0–X s» en K; «one sentence» en F). El pedido de F52b no se ajusta, así que queda para que lo juzgue el analista.
- **Los `ENTRADA_ANALISTA_*.md`:** no los escribí yo y, por regla de la cadena, no se commitean.
