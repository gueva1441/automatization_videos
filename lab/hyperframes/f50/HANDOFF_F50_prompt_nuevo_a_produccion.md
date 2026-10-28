# HANDOFF F50 — El prompt nuevo de foto y de video pasa a producción; Wittenoom en papel

Analista, 2026-10-28 11:50. Pedido de Omar (11:15 y 11:22): la candidata de F49 pasa a producción (Opus 5.5 llena los casilleros, entrada nueva S2–S5, armado por código) y Wittenoom se regenera entero, con fotos y clips; «sí a todo», el gasto no frena (hasta ~US$ 10).
Tema Wittenoom `123bbb64-9fca-4395-8bf4-57d60e219ef1`. Rama `f11-guion-v4`.

**Qué es esta tanda, en llano:** hoy las fotos se piden a Gemini Pro y Flash «teje» la frase. Las pruebas F46b–F49 (lab) mostraron que sale mejor si Opus llena los casilleros con un expediente por foto y el código arma la frase. Esta tanda copia eso a producción **sin cambiar lo que se midió** (se verifica byte a byte contra el lab), borra el camino viejo, alinea el prompt del clip Veo con la guía de Google y deja los 96 prompts de Wittenoom **en papel**. Cero fotos.

## Orden (vuelto a derivar)
1. ¿Construye sobre algo que se decidió reemplazar? No: reemplaza el tejido de Flash (decidido 11:15) y lo borra.
2. ¿Una decisión de hoy cambia el orden? Sí, una: **el canon (la ficha de época y de grupos de personas) tiene que salir de la ficha**, no del research viejo. En el lab la candidata usó un canon armado desde `ficha_caso.json` con `people_groups`; en producción el canon sale del paso 4e del research, con 10 `verified_facts` y sin grupos. Por eso va la parte A antes que la B.
3. Hallazgo para Omar (no cambia esta tanda): **fal apaga toda la familia Veo 3.1 el 2026-11-17** (aviso en la página de `fal-ai/veo3.1/lite/image-to-video`). Wittenoom llega a tiempo con Veo; el reemplazo del motor de clips es una prueba aparte (candidato a medir: `google/gemini-omni-flash/image-to-video` en fal).

## Constantes
| Valor | Origen | Quién |
|---|---|---|
| Modelo de los casilleros: `claude-opus-5-5`, effort `high` (`guion_v4.ESFUERZO`) | DECISIONES 2026-10-28 03:30–03:34 y 11:15 | Omar |
| Modelo del canon: Gemini Flash (`call_flash_json` de `step_4e`, como hoy) | existente | — |
| Modelo del movimiento del clip Veo: el mismo de los casilleros (Opus 5.5 high), en lugar de Pro | decisión 11:15 («el prompt de video se alinea») + una sola fuente de modelo | analista, declarado |
| Años válidos 1800–2100 | existente (`m03_visual._geo_era`, F48) | — |
| Orden del año de cada foto: 1) dicho en el ancla 2) casillero `year` 3) último año dicho **en la narración** de los caps anteriores 4) fecha del `dato_central` 5) `topic_year` | F48 S4; el 3) cambia de «anclas» a «narración» porque en producción los caps corren en paralelo y las anclas de otros caps no existen todavía. Medido: en S5 **0 de 60** fotos usaron 3)–5) | analista, declarado |
| `duration` del clip: `"8s"` = `m03_visual.VEO_CLIP_DURATION_SEC` (8,0) | existente (el planificador ya corta ventanas de 8 s); hoy no se manda y fal usa 8 s por defecto: mismo resultado, ahora explícito | — |
| `resolution` `1080p`, `generate_audio` false | existentes (`config.fal_veo_resolution`, `asset_manager`) | — |
| Largo del `video_prompt`: 120–700 caracteres | existente (`PROMPT_MIN_CHARS`/`PROMPT_MAX_CHARS`, `_validate_prompt_length`) | — |
| `negative_prompt` del clip: **ver §C.2** (lista fija del canal) | voto del analista | **Omar confirma al pegar** |
| Llamada de prueba Veo: 4 s, 1 vez | verificar que el endpoint vive y acepta `negative_prompt`/`duration` | analista |
| Tope de la tanda **US$ 5,00** (`lab/TOPE_TANDA.json`, `desde` = hora de pegado) | Opus 7 caps ≈ 2,0 (F47b: 0,28/cap) + re-hechuras F8 ≈ 0,5 + canon Flash ≈ 0,01 + movimiento 2 × ≈ 0,05 + Veo 4 s ≈ 0,20 → ≈ 2,8; margen. Omar 11:22: «no importa si salen 10» | Omar |
| Workers: los de producción (`CAP_MAX_WORKERS` 7, `FLUX_MAX_WORKERS`) | existentes | — |

Textos para modelos: **los del lab, tal cual** (los copia el código desde los archivos de lab, se verifican por byte): `TEXTO_1_PEOPLE_GROUPS`, `TEXTO_2_PEOPLE_GROUP`, `TEXTO_3_ENCABEZADO` (`lab/hyperframes/f46/f46b/f46b_corridas.py`), `TEXTO_S4_YEAR`, `TEXTO_S5` (`lab/hyperframes/f48/f48_corridas.py`). El único texto nuevo es el del movimiento (§C.1), escrito entero abajo.

## Módulos que toca
| Parte | Módulo | Hoy | Después |
|---|---|---|---|
| A | `researcher_steps/step_4e_visual_canon.py` | canon desde `verified_facts` del research, sin grupos | + `canon_desde_ficha(topic, ficha)`: adaptador ficha → hechos (de `lab/.../f46_corridas.adaptador_facts`), `people_groups` en el esquema, texto 1 + `TEXTO_S5` + lista de `personajes` del pool (rol · lugar · años) al final del pedido (= `f48.canon_s5`) |
| A | `fase1_5.py` | ficha → escaleta | `asegurar_canon` después de `asegurar_ficha`, y **antes de m03 en todo camino** (`--from m03`, `--only m03`): si el canon del topic no trae la marca `canon_ficha_md5` igual al md5 de la ficha de hoy, se arma y se guarda donde lo leen m03 y foto madre |
| A | `topic_researcher.py` | sub-paso 4e (canon) en el research | **se borra** la llamada 4e y su guardado, con sus tests (el canon ya no nace ahí) |
| B | **nuevo** `script_engine/m03_expediente.py` | — | expediente por foto (= `f46b.expedientes` + `f48.extra_por_foto`) y su bloque de texto (= `f48.bloque` en S5) |
| B | `script_engine/m03_visual.py` | casilleros con Pro → tejido de Flash (fluidificador, Guarda 1, candado de cifras, re-tejido por texto filtrado) | casilleros con Opus (SI v3 + `people_group` + `year`; esquema + `people_group` + `year`) → armado por código → F8 con backstop. Re-hechuras (`_f8_refill`) por el mismo camino. **Se borran** fluidificador, Guarda 1, candado de cifras, re-tejido y `SEEDREAM_SLOTS_USE_PRO`, con sus tests |
| B | `script_engine/m03_imagenes_v3.py` | `wrap_style`, `fix_counts_lr` | + `armar` (= `f46b.armar` + regla del setting con año de `f48.armar_etapa`), `f8_backstop` (= `f46b.f8`), `anio_final` (= `f48.anio_final`); chascadas §B.4; `wrap_style` se borra si nadie más la usa |
| C | `script_engine/m03_visual.py` | `_seedream_video_prompt`: Pro, 2–3 frases de movimiento | Opus, texto §C.1 |
| C | `asset_manager.py` | `_call_veo_once` manda `prompt`, `image_url`, `generate_audio`, `resolution` | + `negative_prompt` (§C.2) y `duration` |

Solo lectura (verificar que no se rompen, sin cambios): `script_engine/m09_packaging.py` (importa las `DOCTRINE_*` de m03), `qa_studio_server.py` (arreglo de foto sobre el prompt final; clip con `am._generate_veo_clip`, hereda C), `foto_madre.py`.

## Paso 0
1. `DECISIONES.md`, tal cual:
   - «2026-10-28 11:15 · Opus se queda; la candidata (C2 armado por código + S2–S5 + Opus) pasa a producción. Wittenoom se regenera entero con el prompt nuevo: las 96 fotos (78 de caps 2–6 + 18 de los caps Veo 1 y 7) y los 2 clips Veo. El prompt de video se alinea con la guía de Google antes de regenerar · Omar · F50».
   - «2026-10-28 11:22 · Sí a todo: F50 con chascadas (cifra al inicio de oración en minúscula; cartel «On the … reads»); el gasto de la regeneración no frena, hasta ~US$ 10 · Omar · F50».
   - «2026-10-28 11:50 · El canon visual sale de la ficha (con `people_groups` y la lista de personajes del pool) y se arma antes de m03; el 4e del research se borra. Motivo: la candidata que ganó en F49 usó ese canon; el del research tenía 10 hechos y ningún grupo · analista, dentro de 11:15 · F50».
2. `lab/TOPE_TANDA.json` = `{"usd": 5.0, "desde": <hora de pegado>}`.
3. Copia de seguridad: `data/scripts/_steps/<TID>/03_visual.json` y `05_visual_canon.json` → `lab/hyperframes/f50/antes/`.

## Parte A — canon desde la ficha
1. `canon_desde_ficha` y `asegurar_canon` como en la tabla. Un solo llamado a Flash por canon: el pedido es **el de la regeneración S5 de F48** (texto 1 + `TEXTO_S5` + personajes), y de esa respuesta se toman **todas** las claves (en el lab el resto del canon venía de otra llamada, la de F46b: declarado, una sola llamada es lo correcto para producción).
2. Verificación automática: el pedido de producción para Wittenoom (sistema + usuario + esquema) tiene el **mismo md5** que el pedido de la regeneración S5 de F48 (reconstruirlo en seco con `f48.canon_s5` atrapando el pedido, sin API). Si no coincide, PARADA con el diff.
3. Correr `asegurar_canon` en Wittenoom (1 llamada Flash real). Salida en texto: `lab/hyperframes/f50/A_CANON.md` con los `people_groups` (id · who · appearance · clothing) y el diff de claves contra `lab/hyperframes/f48/canon_S5.json` (Flash no es determinista: el diff es informativo, no frena; sí frena si `people_groups` sale vacío). Además, tabla informativa personaje del pool (rol) → grupo que lo cubre o «sin grupo» (el cruce es a ojo del analista, no un corte: F49 m7 dejó 5 fotos con gente sin grupo).
4. Tests: el adaptador (ficha → hechos), la marca md5 (ficha nueva → canon nuevo; misma ficha → no llama), el borrado del 4e.

## Parte B — prompt de foto en producción
1. `m03_expediente.py` + cambios de `m03_visual` y `m03_imagenes_v3` como en la tabla. El pedido a Opus = `_build_seedream_prompt_step2` + `beats_block` + bloque del expediente (S5); SI = v3 + `TEXTO_2_PEOPLE_GROUP` + `TEXTO_S4_YEAR` después de la línea `- foto_madre_ref:`; esquema + `people_group` + `year`. **Los casilleros `mood`, `style` y `hard_fact_ids` se siguen pidiendo** (así se midió; el armado no los usa) — quitarlos es otra prueba en texto (a la lista de abiertos).
2. Armado por código y F8 = los del lab: sujeto/acción → mirada → objeto → lugar + año (sin «, año» si el setting ya trae año o década) → `style_head(año)` + `STYLE_TAIL` → luz + paleta → plano/ángulo/lente → texto del cartel → 16:9 + `NO_TEXT` si no hay cartel; después nombres documentados fuera, `fix_counts_lr`, escala, y si hay problemas F8 se **saca la frase** (sin re-tejido). La pasada 1 de `_validate_no_text_leakage` (eufemismos de texto) queda como backstop que saca la frase (medido: 0 de 60 prompts S5 la disparan). Marcas `sensible` y `motivos` sobre el prompt final, como hoy.
3. Re-hechuras de F8 (`_f8_fix_cap`, `_f8_fix_video`): mismo camino (Opus para 1 foto con la nota + armado). Si Opus se niega (`ClaudeError` por `refusal`): se reporta la foto y el cap queda en PARADA; **sin** volver a Pro en silencio.
4. Chascadas (generales, con test):
   - **Cartel:** hoy sale «On the warning sign … reads "DANGER ASBESTOS" in faded block stencil lettering» (sin sujeto; «letters lettering»). Regla: si `location` empieza con preposición → `The words "<texto>" are written <location> in <font>, in clear crisp lettering.`; si no → `The <location sin artículo> reads "<texto>" in <font>, in clear crisp lettering.`; sin `location` → `A sign reads …`. Se quita el «lettering» que se pegaba al `font`. Las preposiciones son gramática inglesa, no de un tema: on, in, at, above, across, along, over, under, beneath, beside, behind, inside, outside, near, around, by, from, onto, into, upon. Simulado sobre los 5 carteles de S5: 5/5 quedan con sujeto (tabla abajo).
   - **Cifra al inicio de oración (m8 de F49):** «Three inmates stand» → hoy «a few inmates stand». Regla: la cantidad vaga va en mayúscula si la cifra o su artículo iban en mayúscula. Tests: «Three inmates stand.» → «A few inmates stand.»; «The two men sit» → «A couple of men sit»; «two men sit» → «a couple of men sit».
5. Verificación automática (en seco, sin API):
   - **Pedido:** para el cap 2 de Wittenoom con `lab/hyperframes/f48/canon_S5.json` y las anclas/beats de `03_visual.json` (de antes), sistema + usuario + esquema de producción = `lab/hyperframes/f48/pedidos/pedido_S5_ch02.txt` (+ el esquema de S5) **byte a byte**. Si no, PARADA con el diff.
   - **Armado:** con los casilleros crudos de `lab/hyperframes/f48/slots_S5_ch02.json` y `slots_S5_ch07.json`, los prompts de producción = los de S5 en `lab/hyperframes/f49/PROMPTS_F49.json` **salvo** las fotos que tocan las dos chascadas; esas se listan antes → después. Cualquier otra diferencia: PARADA.
6. Salida en texto: `lab/hyperframes/f50/B_VERIFICACION.md` (md5 de pedidos, tabla de diferencias del armado, lista de lo borrado con sus tests).

## Parte C — prompt del clip Veo
1. `_seedream_video_prompt` pasa a Opus con este sistema (texto nuevo, entero) y el esquema `{video_prompt: string}`:

```
You write the motion prompt for an image-to-video model (Google Veo) that animates ONE documentary still. The still is the first frame and it is final: everything visible in it stays as it is. Follow Google's order: shot type and tone first, then the camera, then what moves, then light and place.

Write 3 to 5 sentences of plain English, between 120 and 700 characters, in this order:
1. Shot and tone: the kind of shot and its tone, in the still's own photographic style (for example: "A slow, somber documentary shot on grainy 35mm film, muted colors.").
2. Camera: ONE camera movement in film terms (slow push-in, slow pull-out, slow pan, slow tilt, locked-off shot with a subtle drift, slow orbit), its speed, and the framing where it starts and where it ends.
3. Motion: what moves, using only things already in the still (dust, smoke, water, cloth, grass, hair, a person breathing or slowly turning the head). If more than one thing moves, describe it step by step ("first ..., then ...").
4. Light and place: the still's light and place, the same for the whole clip.
5. People, only if the still shows people: they stay in their places, faces and bodies steady.

Write only what should be seen. Anything that must not happen goes in a separate negative prompt that the code adds, so do not write negations. No names, numbers or on-screen text.
Return only the JSON field video_prompt.
```

   Usuario: `FIRST FRAME (final):\n<prompt armado de la foto 0 del cap>\n\nNARRATOR OVER THIS CLIP (Spanish, context only): «<ancla>»\n\nCLIP LENGTH: <VEO_CLIP_DURATION_SEC> seconds.` Se borra `_VEO_VIDEO_PROMPT_STRUCT` y `_SEEDREAM_MOTION_SYSTEM` (el texto de arriba los reemplaza). Validación de largo: la de hoy, con su reintento.
2. `negative_prompt` (constante del canal, en `asset_manager`, una sola vez; **Omar la confirma al pegar**): `text, subtitles, captions, watermark, logo, morphing faces, distorted hands, extra limbs, people entering the frame, sudden lighting change, camera shake, fast cuts, cartoon, CGI look`. Sin «elementos modernos»: el cap 7 de Wittenoom es 2024 y los cortaría; la época la fija la foto.
3. `_call_veo_once` manda `negative_prompt` y `duration` (`f"{int(VEO_CLIP_DURATION_SEC)}s"`; si no es 4/6/8 → error, no se redondea).
4. **Llamada de prueba (1, 4 s):** el primer cuadro de hoy del cap 1 (`output/<TID>/assets/ch01_veo/`), su `video_prompt` de hoy, el `negative_prompt` y `duration` `"4s"`, a `lab/hyperframes/f50/veo_prueba.mp4`. Se reporta: respuesta de fal, duración medida con ffprobe y costo. Si fal rechaza `negative_prompt` o `duration`: PARADA con el error tal cual.
5. Revisión del analista sobre los dos casos reales (simulada, para el papel): cap 1 (pie vendado, plano cerrado, 1961) → «A slow, somber documentary shot on grainy 35mm film with muted colors. The camera holds low at ground level and makes a very slow push-in, starting on the whole foot and ending close on the stained bandage. Fine red dust drifts low across the ochre earth, then the loose end of the bandage stirs in a faint breeze. The harsh overcast daylight and the soft corrugated iron behind stay the same for the whole clip.» (≈ 430 caracteres: entra). Cap 7 (pala, 2024) → movimiento de alejamiento lento que muestra más del llano vacío, pasto seco que tiembla y polvo rojo que pasa; luz de tarde y sombra larga constantes. Riesgo visto: si la foto 0 nueva trae gente, el punto 5 del sistema la mantiene quieta; si la foto 0 es un plano muy abierto, «push-in» de 8 s puede quedar corto: el modelo elige el movimiento.

## Parte D — Wittenoom en papel (cero fotos)
1. `python fase1_5.py --topic 123bbb64-9fca-4395-8bf4-57d60e219ef1 --only m03` (asegura el canon de A, re-planea anclas, casilleros con Opus, armado, F8, re-hechuras, movimiento de los 2 clips). Sin foto madre, sin assemble, sin fase2a.
2. Salida en texto: `lab/hyperframes/f50/PAPEL_FOTOS_WITTENOOM.md` y `.json`, por cap y por foto: n.º · ancla (las palabras de la voz) · beat · año y de dónde salió · `people_group` · plano · **prompt entero** · notas F8 (frases sacadas) · si fue rehecha y por qué. Caps 1 y 7: además el `video_prompt`, el `negative_prompt` y la `duration` del clip. Al final: fotos por cap (contra las 96 de antes: si cambia el número, decirlo), años por fuente, re-hechuras, carteles, costos reales por modelo.
3. Revisión: el analista la hace con formato DEBERÍA antes de que Omar la vea; Omar da el OK; recién ahí la tanda de fotos y clips (otra tanda).

## Reglas fijas
- Nada se genera en fal salvo la llamada de prueba de 4 s. Nada en `main`. Las PNG/MP4 no van a git.
- Paralelo al máximo: subagentes para A, B y C donde no dependan entre sí (A y la parte de código de B/C pueden ir juntas; la verificación de B usa el canon de lab, no el de A); workers de producción en D.
- Cada parte termina con su salida en texto y su verificación automática; si una verificación falla, PARADA en esa parte con el diff. Si pasan, se sigue sin esperar.
- Lo viejo se borra con sus tests (tejido, Guarda 1, candado de cifras, re-tejido, `SEEDREAM_SLOTS_USE_PRO`, 4e del research, `_VEO_VIDEO_PROMPT_STRUCT`, `_SEEDREAM_MOTION_SYSTEM`, `wrap_style` si queda sin uso). Grep final: ningún uso vivo de lo borrado.
- Stickers (md5) y `lab/MAPA_PROYECTO.md` (`--check` 0) para cada archivo de producción tocado y el nuevo.
- Suites: rápida y amplia (`lab/hyperframes/f41/verificar.sh`), número antes/después. Prohibido `pytest --collect-only` y `pytest test_*.py` en bloque.
- `F50_REPORT.md` con «lo que queda abierto» entero y el veredicto íntegro de `revisor-handoff`; `lab/ESTADO_SESION.md`; commits por parte.

## Tabla de simulación (cartel, sobre los 5 de S5)
| foto | location | sale hoy | sale con la regla |
|---|---|---|---|
| S5 ch07 11 | on the warning sign fixed to the barricade | On the warning sign … reads "DANGER ASBESTOS" in faded block stencil lettering | The words "DANGER ASBESTOS" are written on the warning sign fixed to the barricade in faded block stencil |
| S5 ch02 13 | on the wooden sign board beside the shed | On the wooden sign board … reads "WITTENOOM" in hand-painted block letters lettering | The words "WITTENOOM" are written on the wooden sign board beside the shed in hand-painted block letters |
| S5 ch06 10 | on the sign panel being lowered | On the sign panel … reads "WITTENOOM" … letters lettering | The words "WITTENOOM" are written on the sign panel being lowered in white highway block letters |
| S5 ch06 15 | on the folder tab | On the folder tab reads "Wittenoom Gorge" in typed serif lettering | The words "Wittenoom Gorge" are written on the folder tab in typed serif |
| S5 ch05 8 | place of birth line on the passport page | Place of birth line … reads "WITTENOOM" in typed passport typeface lettering | The place of birth line on the passport page reads "WITTENOOM" in typed passport typeface |
(todas terminan en «, in clear crisp lettering.»; la pasada 1 del filtro de texto no las corta: medido)

## PARADA al terminar D. Cero fotos, cero clips (salvo la prueba de 4 s).
