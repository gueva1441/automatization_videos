# HANDOFF F29b — Rotulista: el texto de pantalla lo escribe alguien, anclado a la oración

Analista · 2026-10-25 · Para CC. Base: `1711e88` (F29 D). Dos partes A→B; **PARADA al final de B**. Topes: Claude US$ 2 · Gemini US$ 1 · ElevenLabs 0. Banco: Vajont (`f8s3-vajont`), mismo guion, voz, música e imágenes de F28/F29; **solo cambia quién decide los bloques de texto y dónde anclan**. Una variable: el rotulista. Transiciones, forma (entradas/salidas, zonas, tamaños), velocidad del render y subtítulos **no** entran aquí: tienen sus corridas (`claude/ANALISIS_gfx_contenido_y_forma_2026-10-25.md` §5–6, `claude/ANALISIS_render_tiempo_2026-10-25.md`).

## 0. Por qué (leído contra la voz, v3: 4 de 22 bloques cumplen)
Regla acordada con Omar: un bloque vale si **(a)** dice algo que la voz no dice, **(b)** sobre lo que la voz cuenta en ese momento, **(c)** sin adelantar. En v3: 4 cumplen (ch02 D117, ch04 T33, ch05 T64, ch06 D128), 4 tienen el dato bien y el momento o la forma mal, 13 repiten o están fuera de lugar y hay 1 spoiler nuevo (ch06 T58 «devastó Longarone», 75 s antes). Causas: `garantizar_pico` fabrica 7 de los 13; la ventana es el beat y no la oración; «ya dicho» compara palabras; el crítico aprueba por kicker; el candado literal deja muñones; cifras sin etiqueta; y **nadie escribe el texto**: research extrae → escaleta elige 5 `a_pantalla` → `gfx_fragments` corta → Flash devuelve un número. De los 5 `a_pantalla` de la escaleta el cortador arruinó 4 (D117 perdió «13 de 34», D192 no salió, D245 perdió la cifra en liras, Q50 perdió que es la carta del municipio). Detalle bloque por bloque en el análisis citado, §1–2.

## A. El rotulista (Claude ≤ US$ 2 · Gemini ≤ US$ 1 · tests sin red)

### A.1 Entrada por cap (`script_engine/gfx_rotulista.py`, nuevo)
1. **Oraciones de la voz con tiempo:** lista `[{idx, t0, t1, texto}]` del cap, desde el sync map (`music_intensity.tiempos_por_palabra` + corte por puntuación; reusar lo que use `gfx_peak` para `sentence_idx`).
2. **Beats del cap:** lo que ya guarda `gfx_beats_chNN.json` (ventanas, función, `dato_central`, `datos_apoyo`, `cierre`).
3. **Ítems candidatos**, cada uno con `id`, tipo (Q/D/T), **texto fuente completo** del pool, `fuente` (título, año) y, si es `a_pantalla`, su `por_que`. Son: los `a_pantalla` del cap + `dato_central`/`datos_apoyo` de los beats del cap. Nada más.
4. **Ya mostrado** en caps anteriores (ids y textos).
5. **Pico del cap: uno solo.** `escaleta.pico` (cap + frase) → `pico.t` y `sentence_idx`. `gfx_peak` queda solo como respaldo si la escaleta no trae pico. `music_intensity` y el realizador leen ese mismo valor (hoy hay tres fuentes).

### A.2 Llamada
Una por cap, `claude_helpers.make_call`, modelo por defecto `claude-sonnet-5-5` (effort medium, JSON sin esquema forzado, cruda guardada en `_fase2b_work/rotulista_chNN.raw.json`); flag `--rotulista-modelo` para probar `claude-fable-5-1` después. Tope chequeado antes de cada llamada. Si la respuesta no parsea o viola el candado (A.4), **un** reintento con el error en el mensaje; si vuelve a fallar, el cap sale sin bloques de texto y se anota: nunca se inventa.

### A.3 Prompt (entero; CC lo pone en `ROTULISTA_SYSTEM` y `ROTULISTA_USER` sin cambiar palabras)

**SYSTEM:**
```
Sos el rotulista de un documental de historia oscura en español. Recibís la narración de un capítulo, oración por oración y con tiempos, y una lista de datos verificados (citas, cifras, hechos) con su texto fuente. Tu trabajo es decidir qué va escrito en pantalla, en qué oración, de qué tipo y con qué palabras.

Un texto en pantalla vale solo si cumple las tres a la vez:
(a) dice algo que la narración NO dice en ese capítulo (ni antes ni después de esa oración);
(b) es sobre lo que la narración está contando en esa oración exacta;
(c) no adelanta nada que la narración vaya a decir más adelante.
Si para una oración no hay ningún dato que cumpla las tres, no va nada. La pantalla vacía es correcta. Nunca repitas la narración con otras palabras; nunca parafrasees lo que la voz acaba de decir o va a decir.

Tipos de bloque y su compuerta (solo podés usar un tipo cuando la narración, en esa oración, está hablando de eso):
- cifra: la narración habla de esa magnitud (altura, muertos, metros cúbicos, dinero). Lleva etiqueta obligatoria que diga de qué es la cifra. Ej.: «Altura de la presa: 266 m».
- recorte: la narración cuenta ese hecho o ese documento. Aporta el quién, el cargo, la fecha, lo que dice el acta o la carta. Lleva kicker = nombre real del documento o la fuente, con año.
- cita: la narración nombra a esa persona o lee de ella. Texto literal del dato, sin cambiar una palabra, con el autor.
- persona: la narración nombra a alguien por primera vez en el capítulo. Texto = nombre y cargo, tal como están en el dato.
- lupa: la narración nombra un detalle chico que está en la imagen (una fisura, una firma, una fecha en un papel, una marca en el muro). Nunca el sujeto principal de la foto. Texto = qué se señala, ≤ 4 palabras.

Reglas de escritura:
- Máximo 9 palabras (cifra con etiqueta: máximo 6). Oración completa o etiqueta + valor; nunca un fragmento cortado sin sujeto o sin el valor.
- Para citas: copiá el texto del dato literal. Para cifras, recortes, personas y lupas: redactá, pero cada número, nombre propio, fecha y cantidad que escribas tiene que estar en el texto fuente de ese dato. Si el dato no trae el valor, no lo inventes: no va.
- Los datos marcados `a_pantalla` son obligatorios: tienen que salir, en la oración que mejor corresponda, y con lo que pide su `por_que` (si el `por_que` pide «la cifra en liras», la cifra tiene que estar).
- Tope: 5 bloques por capítulo; en el beat `gancho`, máximo 1. Un bloque por oración.
- El pico del capítulo no tiene privilegio: lleva bloque solo si hay un dato que cumpla (a)(b)(c) en esa oración.
- Si un dato ya se mostró en un capítulo anterior, no lo repitas.

Para cada bloque explicá en una línea `aporta` qué dice que la narración no dice (ej.: «el quién: Consejo Superior de Obras Públicas», «la cifra: 1.910 muertos»). Si no podés escribir esa línea con algo concreto, el bloque no va.

Respondé SOLO con JSON válido, sin texto antes ni después.
```

**USER:**
```
CAPÍTULO {cap} — {titulo}

NARRACIÓN (oración por oración, con segundos):
{oraciones: "[idx] t0–t1 · texto"}

BEATS DEL CAPÍTULO (función, ventana en segundos, cierre):
{beats}

PICO DEL CAPÍTULO: oración [{pico_idx}] «{pico_frase}»

DATOS DISPONIBLES (solo estos; cada uno con su texto fuente):
{items: "- id · tipo Q/D/T · a_pantalla: sí/no · por_que: … · fuente: … · texto fuente: «…»"}

YA MOSTRADO EN CAPÍTULOS ANTERIORES (no repetir):
{ya_mostrado}

Devolvé:
{"bloques": [{"sentence_idx": int, "tipo": "cifra|recorte|cita|persona|lupa", "texto": str, "etiqueta_o_kicker": str|null, "pool_id": str, "aporta": str}], "descartados": [{"pool_id": str, "motivo": str}]}
```

### A.4 Después del modelo (código, determinista; cada fallo se anota en el log y el bloque sale)
1. `sentence_idx` existe → `t0 = t1_oración + 0.3 s`; `dur = max(2.5, palabras/3 + 1)` ≤ 6 s; dentro de la ventana del beat de su ítem (la ventana es **freno**, no ancla).
2. Largo: ≤ 9 palabras (cifra ≤ 6). Tipo válido. Cifra sin etiqueta → fuera.
3. **Candado:** `cita` → el texto es subcadena contigua del texto fuente del ítem (normalizando mayúsculas/espacios). Los demás tipos → cada número (en dígitos o en letras, con el conversor que ya usa `gfx_pool`), nombre propio (token con mayúscula inicial que no abre oración) y año del texto aparecen en el texto fuente del ítem.
4. **No dicho:** ningún número ni nombre propio del bloque aparece en la voz de ese cap en `[t0 − 20 s, t0 + 20 s]`; ningún número del bloque aparece en la voz **después** de `t0` en el cap (spoiler). El chequeo semántico («otras palabras») queda a cargo del prompt y del crítico.
5. Topes: ≤ 5 por cap, ≤ 1 en `gancho`, 1 por oración. `a_pantalla` faltantes → **un** reintento con la lista de los que faltan; si siguen faltando, se anota (no se inventa).
6. Mapeo a bloques existentes: `cifra` → `data_callout` kind figure **con cara `anton`/`serif`** (nunca `stamp`) o `water_level`/`count_up` si el rotulista marcó `unidad` en metros/personas; `recorte` → `archive_clipping` con el kicker del rotulista; `cita` → `quote_card`; `persona` → `data_callout` cara `serif`, texto «Nombre · cargo», lado según el sujeto; `lupa` → `evidence_zoom` con la caja de visión del detalle nombrado (si visión no encuentra el detalle, fuera y anotado).

### A.5 Lo que sale del camino (solo cuando hay escaleta; sin escaleta, todo como hoy)
- `garantizar_pico`: apagado (`gfx_rules.garantizar_pico = False`).
- `gfx_fragments` + `gfx_pool.FORMA_CALL` (Flash elige número): fuera del camino para D/T; las citas tampoco pasan por ahí (vienen literales del rotulista).
- Nivel de agua, contador y zoom del director: solo si el rotulista los pidió (A.4.6). El director sigue decidiendo escenas, movimientos y el resto.
- Sellos: **como hoy** (≤ 1, palabra del pico). No se tocan en esta corrida; sello y rótulo pueden coincidir todavía (es forma, va en su corrida).

### A.6 Crítico (Gemini, como hoy, visión sobre el bloque dibujado)
Corre **después** de A.4–A.5 (hoy corre antes de `garantizar_pico`). Pregunta nueva, dos sí/no con motivo de una línea: (1) «¿La narración en los 20 s alrededor habla de lo que este bloque muestra?» (2) «¿El bloque dice algo que la narración no dice en ese tramo?». Recibe la voz ±20 s y el `aporta` del rotulista; **el kicker/fuente no cuenta como aporte**. Cualquier «no» corta el bloque. Se guarda el veredicto junto al bloque.

### A.7 Tests sin red (`test_module_f29b.py`), con fixture de Vajont ch03 y ch06 (oraciones, beats, ítems) y **una respuesta cruda del modelo guardada** en `lab/hyperframes/f29b/fixtures/`
- anclaje: `t0` = fin de oración + 0.3 s, dentro de la ventana del beat del ítem;
- candado: una cita alterada falla; una cifra que no está en la fuente falla; «266» con etiqueta pasa y sin etiqueta falla;
- no dicho: «1.910» con la voz diciendo «mil novecientos diez» a ±20 s falla; «Longarone» en la voz 75 s después → spoiler, falla;
- topes: 6 bloques → 5; gancho 2 → 1; dos en la misma oración → 1;
- `a_pantalla`: D245 sin cifra en liras → reintento; segunda vez sin cifra → anotado y no inventado;
- pico único: con `escaleta.pico` presente, `pico.t` ≠ el de `gfx_peak` y gana la escaleta;
- orden: el crítico corre después de A.5 (un bloque que entra por respaldo también se juzga).
- Suite rápida y amplia verdes (921 + 5 previas); `--only-cap ch02` sin `--gfx` byte-idéntico (`--sw-encode`).

## B. Vajont v4 (solo gfx; Claude ≤ US$ 2 en total con A; Gemini ≤ US$ 1)
1. Copia del topic `f8s3-vajont-f29b` (mismo patrón que F29 C: reusa imágenes, clips, voz, música, intensidad, cachés de visión). Se rehacen rotulista, realizador, crítico, render gfx **en fila** (NVENC cq 23, timeout 1500 s, workers como hoy) y ensamble.
2. Salida `output/f8s3-vajont-f29b/f8s3-vajont_final_gfx_v4.mp4` + `lab/hyperframes/f29b/BLOQUES_v4.jpg`.
3. **Hoja nueva (la que lee el analista en vez de los logs):** un renglón por bloque con (i) el cuadro a 2560 en el instante `t0 + 1 s`, (ii) **miniatura del mismo cuadro a 360 px de ancho** (celular), (iii) la voz −6 s / durante / +6 s, (iv) `aporta` del rotulista, (v) veredicto del crítico, (vi) `pool_id`, tipo, oración, `t0` en el cap y en el mp4 (`offset del cap + t0 + 2.5 s`). Script en `lab/hyperframes/f29b/b/hoja_bloques.py`, reusable para los renders que sigan.
4. Tabla en el reporte, por cap: bloques, tipo, texto, oración, `aporta`, crítico, costo del rotulista (tokens in/out, US$, s), `a_pantalla` cumplidos. Rotulista: cuántos propuso, cuántos cortó A.4 y por qué (candado, no dicho, tope), cuántos cortó el crítico.
5. CC **no** cuenta «cumplen (a)(b)(c)»: eso lo cuenta el analista con la hoja. CC cuenta lo medible: muñones (texto que empieza en minúscula sin sujeto o termina en preposición/artículo) = 0; cifras sin etiqueta = 0; números del bloque dichos por la voz a ±20 s = 0; números del bloque dichos después en el cap = 0; `a_pantalla` 5/5 con lo que pide el `por_que` (D117 con «13 de 34», D192 con «20 técnicos», D245 con la cifra en liras, Q50 como carta del municipio, D128 como hoy).

## Frenos
- Cero cambios en prompts de guion, escaleta y ficha. No se toca m03, voz, música, partición, sellos, transiciones, plantillas HTML/CSS (si `persona` o la cifra con etiqueta no caben en `data_callout` tal cual, se usa la cara `serif` existente y se anota; no se crea plantilla).
- Sin merge, sin publicar, sin borrar. `.env`, `config.py`, `lab/_gpt_probe_analista/`, `gfx_profiles/*` fuera de git.
- Un commit por parte. `lab/ESTADO_SESION.md` al final. Workers al máximo donde haya paralelo (el rotulista puede correr los 7 caps en paralelo: 7 llamadas; el render sigue en fila).

## Reporte `lab/hyperframes/f29b/F29b_REPORT.md`
A: diffs (archivos y líneas), prompt final md5, tests, 2 crudas de ejemplo (ch03, ch06). B: tabla por cap, ruta del `_v4.mp4`, `BLOQUES_v4.jpg`, costos, tiempo de gfx por cap. Veredicto íntegro del revisor-handoff. **PARADA.**
