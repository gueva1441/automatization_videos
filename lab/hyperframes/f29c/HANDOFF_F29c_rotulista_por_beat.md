# HANDOFF F29c — Rotulista por beat, sin cartel: la ficha es el title card

Analista · 2026-10-26 · Para CC. Base: `d7fac3c` (F29b B). Dos partes A→B; **PARADA al final de B**. Topes: Claude US$ 2 · Gemini US$ 1. Banco: `f8s3-vajont-f30` (ya cocido por F30). **Una variable: las reglas del rotulista (cuánto, cuándo, cuánto dura) + el componente donde sale el texto.** Transiciones, sellos, subtítulos y velocidad no entran.

## 0. Constantes de este handoff y de dónde sale cada una
| constante | valor | origen |
|---|---|---|
| textos por beat | **1 máximo**; `gancho` 0–1; **`pico` 0 (prohibido)**; `respiro` y `cierre` pueden ir en 0 | decisión de Omar (26-10, 02:52) |
| animaciones sin texto (reloj, agua, lupa, sello) | 1 por beat; nunca encima de un texto; nunca dos en la misma escena | decisión de Omar |
| arranque del bloque | en la **palabra clave** del dato (la palabra de la oración que el dato responde: «murió» → el nombre; «aprobó» → el 13 de 34); el rotulista devuelve `word_idx` | decisión de Omar |
| fin del bloque | al terminar la oración que acompaña; si no alcanza el mínimo de lectura, se extiende hasta el fin de la oración siguiente; **siempre muere en el corte de escena** | derivado del relato (no es un número) |
| mínimo de lectura | caracteres del bloque ÷ **15 cps** | estándar de subtitulado (Netflix/BBC: 15–17 caracteres por segundo); se usa el más lento |
| «no dicho» | la oración ancla y sus dos vecinas (anterior y siguiente); spoiler = cualquier oración posterior del cap | unidad del relato (reemplaza los ±20 s) |
| coherencia de cifras | una cifra que contradice otra cifra que la voz dice en **cualquier cap** del video → fuera | caso real: «720 m» contra «700 m» (ch05) y «715» (ch04) |
| largo del texto | lo que cabe en la ficha (A.5): kicker 1 línea, dato ≤ 2 líneas al ancho del title card; sin tope de palabras | manda el componente |
| crédito de la ficha | kicker = etiqueta o fuente; título = dato | reuso del title card (F3, identidad de Omar) |
| fundidos de la ficha | los del title card (`title_card.html.tmpl`, identidad F3) | ya existen; no se inventan |
Se **eliminan** del código y del prompt: tope 5 por cap, tope 1 por oración, ≤ 9 / ≤ 6 / ≤ 4 palabras, `+0.3 s`, `max(2.5, palabras/3+1)`, ±20 s, `TOPE_POR_FUNCION` del realizador (F29) para bloques del rotulista.

## A. Reglas (0 API hasta A.6; Claude ≤ US$ 1.5 en A.6)
### A.1 Cantidad por beat (código, `gfx_rotulista.finalizar`)
Por beat del cap: los candidatos del rotulista anclados a oraciones de ese beat se ordenan **`a_pantalla` primero, después por `aporta`** (el rotulista devuelve un `rank` 1..n dentro del beat); queda **1**. `pico` → 0 (ningún texto cuya oración caiga en el beat `pico`; los `a_pantalla` del beat pico se mueven al beat siguiente si su ítem lo permite, si no se anotan). `gancho` → 0–1. Animaciones sin texto: 1 por beat, y si el beat ya tiene texto, la animación va en otra escena del mismo beat o no va.
### A.2 Arranque y fin (código)
`t0` = inicio de la palabra `word_idx` (del sync map). `t1` = fin de la oración ancla; si `(t1 − t0) < caracteres/15`, `t1` = fin de la oración siguiente; `t1 = min(t1, fin de la escena que contiene t0)`. Si aun así `(t1 − t0) < caracteres/15`, el bloque **no va** y se anota «sin tiempo de lectura» (nunca se acorta el texto para que quepa).
### A.3 «No dicho» y spoiler (código, sobre números, nombres propios y años, como en F29b A.4.4)
Contra la oración ancla ± 1 oración, y contra todas las posteriores del cap.
### A.4 Coherencia de cifras (código, nuevo)
Cada número del bloque con unidad (m, m³, personas, liras, %) se compara con los números de **toda la voz del video** (los 7 caps, del sync map) que tengan la misma unidad o la misma magnitud nombrada en la oración (nivel, cota, altura, muertos): si difiere, el bloque sale y se anota «contradice la voz: X vs Y». Test con el caso 720/700/715.
### A.5 La ficha: el texto sale en el componente del title card (plantilla, sin diseño nuevo)
- `data_callout` **deja de usarse** para bloques del rotulista (queda en el código para topics sin escaleta).
- Nuevo uso del `title_card.html.tmpl` como **ficha**: `kicker` = etiqueta (cifra: «ANCHO DE LA FISURA»; persona: cargo, «GEÓLOGO»; hecho: la fuente corta, «ACTA DEL CONSEJO, 1943») y `title` = el dato («Más de 1 metro», «Giorgio Dal Piaz», «Aprobada con 13 de 34 presentes»). Misma posición, tamaño, raya, wipe de entrada y fundido de salida que el title card; sin `#tc-dim` (la ficha no oscurece la imagen; eso es solo del título de cap). Zona: la del title card (arriba-izquierda); si en esa escena ya hay reloj o title card, la ficha espera a la escena siguiente del beat o no va.
- Recortes de prensa (`archive_clipping`) y citas (`quote_card`): **como están** (Omar los deja). Persona: ficha (kicker = cargo). Cifra: ficha. Lupa: `evidence_zoom` como hoy.
- **Prompt nuevo, entero (reemplaza al de F29b; CC lo pone sin cambiar palabras, md5 en el reporte).**

**SYSTEM:**
```
Sos el rotulista de un documental de historia oscura en español. Recibís la narración de un capítulo, oración por oración, con tiempos y con la palabra numerada, y una lista de datos verificados (citas, cifras, hechos, documentos) con su texto fuente. Decidís qué va escrito en pantalla, en qué palabra de qué oración aparece, de qué tipo es y con qué palabras.

Un texto en pantalla vale solo si cumple las tres a la vez:
(a) dice algo que la narración NO dice en este capítulo;
(b) es sobre lo que la narración cuenta en esa oración exacta;
(c) no adelanta nada que la narración diga después.
Si para una oración no hay ningún dato que cumpla las tres, no va nada. La pantalla vacía es correcta. Nunca repitas ni parafrasees la oración ancla ni la anterior ni la siguiente.

Cada capítulo está dividido en beats. En cada beat puede ir como máximo UN texto; en el beat marcado como pico no va ninguno; en el gancho, a lo sumo uno. Proponé por beat los candidatos que cumplan (a)(b)(c) y ordenalos con `rank` (1 = el que más aporta); los datos marcados `a_pantalla` van siempre con rank 1 en su beat y con lo que pide su `por_que`. El código se queda con uno por beat.

Tipos y su compuerta (solo cuando la narración, en esa oración, habla de eso):
- cifra: la narración habla de esa magnitud. Lleva etiqueta obligatoria (qué es la cifra) y el valor. No uses una cifra que contradiga otra cifra que la narración diga en cualquier parte del video.
- hecho: la narración cuenta ese hecho; aportás el quién, el cargo, la fecha, lo que dice el acta. Lleva etiqueta corta (la fuente o el documento, con año).
- documento: una carta, un acta, un informe que la narración menciona o cuyo momento está contando. Sale como recorte: kicker = nombre real del documento con año; titular = lo esencial en una línea, redactado (no es cita literal).
- cita: la narración nombra a esa persona o lee de ella; texto literal del dato, con el autor.
- persona: la narración nombra a alguien por primera vez en el capítulo; etiqueta = cargo, texto = nombre, tal como están en el dato.
- lupa: la narración nombra un detalle chico que está en la imagen (fisura, firma, fecha en un papel); nunca el sujeto de la foto. Texto = qué se señala.

Escritura: una línea de etiqueta y una o dos líneas de dato; oración completa o etiqueta + valor; nunca un fragmento sin sujeto o sin el valor. Para citas, copiá el dato literal. Para el resto, redactá, pero cada número, nombre propio, fecha y cantidad tiene que estar en el texto fuente de ese dato; si el dato no trae el valor, no va.

Para cada bloque devolvé: `sentence_idx`, `word_idx` (la palabra de esa oración que el dato responde: la narración dice «murió» y el bloque pone el nombre; dice «aprobó» y el bloque pone el acta), `beat`, `rank`, `tipo`, `etiqueta`, `texto`, `pool_id` y una línea `aporta` que diga qué dice que la narración no dice. Si no podés escribir `aporta` con algo concreto, el bloque no va.

Respondé SOLO con un objeto JSON, sin texto antes ni después.
```

**USER:**
```
CAPÍTULO {cap} — {titulo}

NARRACIÓN (oración por oración; cada palabra con su índice):
{oraciones: "[idx] t0–t1 · beat N · texto con palabras numeradas: 0:En 1:marzo 2:de …"}

BEATS DEL CAPÍTULO (n, función, ventana en segundos, cierre); el pico es el beat {pico_beat}:
{beats}

DATOS DISPONIBLES (solo estos; cada uno con su texto fuente):
{items: "- id · tipo Q/D/T · a_pantalla: sí/no · por_que: … · fuente: … · texto fuente: «…»"}

YA MOSTRADO EN CAPÍTULOS ANTERIORES (no repetir):
{ya_mostrado}

Devolvé:
{"bloques": [{"sentence_idx": int, "word_idx": int, "beat": int, "rank": int, "tipo": "cifra|hecho|documento|cita|persona|lupa", "etiqueta": str, "texto": str, "pool_id": str, "aporta": str}], "descartados": [{"pool_id": str, "motivo": str}]}
```
- Mapeo a pantalla: `cifra`, `hecho`, `persona` → ficha (kicker = etiqueta, título = texto); `documento` → `archive_clipping` (kicker = etiqueta, titular = texto); `cita` → `quote_card`; `lupa` → `evidence_zoom`.
### A.6 Arreglos de F29b B
1. Parseo: se toma el primer objeto JSON válido de la respuesta (texto antes/después se ignora); solo si no hay ninguno se reintenta. Test con las 4 crudas fallidas de ch01.
2. Crítico: recibe `por_que` y `aporta`; **un `a_pantalla` no se corta por la pregunta (1)**; se corta solo por (2) o por «estorba» (tapa rostro/texto de la imagen). Test con D245.
3. `--rotulista-tope` y costo en vuelo: como quedó en `7e704de`.
### A.7 Tests sin red (fixtures de F29b + nuevos)
1 por beat y 0 en pico (ch06: D128 y D192 caen en `respiro`, se quedan; un candidato en el beat pico sale); arranque en `word_idx`; fin en oración / oración siguiente / corte de escena; «sin tiempo de lectura» cuando no cabe; no-dicho por oraciones vecinas; spoiler por oración posterior; coherencia 720 vs 700/715; ficha con kicker+título y sin `#tc-dim`; ficha no convive con reloj/title card en la escena; JSON con texto extra parsea; D245 pasa el crítico. Suite rápida y amplia verdes; md5 ch02 sin gfx `38e5ba14…`.

## B. Vajont v4 completo
1. Planes de los 7 caps con el rotulista nuevo (Claude ≤ US$ 1.5 total; 7 llamadas en paralelo), crítico, y **render completo** sobre `f8s3-vajont-f30` (`--reuse-visuals --gfx --gfx-sparse --rotulista`), en fila, Firefox cerrado. Salida `output/f8s3-vajont-f30/f8s3-vajont_final_gfx_v4.mp4`.
2. Hoja `lab/hyperframes/f29c/BLOQUES_v4.jpg` como la de F29b (cuadro + miniatura 360 px + voz −1/ancla/+1 oración + `aporta` + crítico + beat), **con el t en el mp4 entero** (offset del cap + t0 + 2.5 s).
3. Tabla por cap: beats, textos por beat (0/1), animaciones por beat, bloques propuestos / fuera por cada regla (cantidad, lectura, no-dicho, spoiler, coherencia, zona) / cortados por el crítico / en pantalla; `a_pantalla` 5/5 (D117, D128, D192, D245, Q50) **o el motivo exacto de cada uno que falte**; costos; tiempo de gfx por cap y pared total (comparar con v3b 37.1 min).
4. Lo que mide CC: muñones 0; cifras sin etiqueta 0; textos en beat `pico` 0; dos bloques en la misma escena 0; bloque que cruce un corte de escena 0; contradicciones de cifra 0. El «cumplen (a)(b)(c)» lo cuenta el analista con la hoja.

## Frenos
- No se tocan: sellos, transiciones, subtítulos, `gfx_style`, m03, voz, música, prompts de guion/escaleta/ficha. `gfx_templates`: solo lo necesario para usar `title_card` como ficha (sin `#tc-dim`); ningún CSS nuevo de tamaño o color.
- Ningún número nuevo en código o prompt que no esté en la tabla §0; si CC necesita uno, lo anota como «pendiente de Omar» y usa el valor que ya exista en el perfil.
- Un commit por parte. Sin merge, sin publicar, sin borrar. `.env`, `config.py`, `lab/_gpt_probe_analista/`, `gfx_profiles/*` fuera de git. `lab/ESTADO_SESION.md` al final.

## Reporte `lab/hyperframes/f29c/F29c_REPORT.md`
A: diffs, prompt nuevo entero + md5, tests. B: tabla por cap, `_v4.mp4`, hoja, costos, tiempos. Veredicto íntegro del revisor-handoff. **PARADA.**
