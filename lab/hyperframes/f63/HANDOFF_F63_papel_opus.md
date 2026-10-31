# HANDOFF F63 — ¿El papel mejora si lo escribe Opus con toda la información? + verificador de narración (solo lab, solo texto)

Rama `f11-guion-v4`, base `b15e9ba`. Topic: Wittenoom `123bbb64-9fca-4395-8bf4-57d60e219ef1`. **Producción no se toca**: no cambia ningún archivo de `script_engine/`, `data/` (incluido `data/cost_history.json`), `output/` ni `logs/`; se verifica por mtimes al final. Lo único fuera de `lab/hyperframes/f63/` que se escribe es `lab/ESTADO_SESION.md` (como en toda tanda). Sin voz, sin fotos, sin render. Subagentes en paralelo al máximo; todas las llamadas de A y B a la vez (22).

## Por qué (lo que encontró el analista, 2026-10-31)
1. El papel de hoy lo escribe **una llamada a Sonnet 5.5, esfuerzo medio** (`m01e_pantalla.MODELO/EFFORT`, l. 67–68). La revisión del subagente del 2026-10-31 le dio 6/10 (`claude/ENTRADA_ANALISTA_2026-10-31.md` §2). Opus nunca se probó como autor del papel; Sonnet se eligió contra Flash (F36).
2. **El autor no ve todo lo que la escaleta eligió.** `m01e_pantalla._tipo` deja fuera del `archivo` los datos sin cifra y los lugares: el archivo tiene 292 de los 362 ítems del pool. En Wittenoom faltan **7 de los 68 ids que la escaleta usa**: D85 (dato central del gancho, beat 1), D03, D129, D20, D10, D70 (apoyos) y **D34 (`a_pantalla` del cap 6)**. El modelo lo dijo en su descarte: «D85 es el dato central del beat 1 según la escaleta, pero no existe en el archivo».
3. El autor tampoco ve: `promesa_gancho`, `loops`, `pico` del video, `humano`, `cierre_humano`, los campos del beat `emocion`, `imagen_sensorial`, `pregunta_abierta`, ni las versiones en disputa de la ficha (`ficha_caso.versiones`, `contradicciones`), ni el fragmento original de la fuente de cada dato (`cita_literal`).
4. La corrida de producción del papel se cortó por el tope del módulo: `01e_pantalla.raw.json` → `error: "tope US$ 1.00 … gastado 0.7005"`; una sola vuelta de corrección (14 motivos en la vuelta 1, 8 en la validación final).
5. La narración trae detalles que nadie chequea: los chequeos solo miran los `ids_usados` que declara cada párrafo. Párrafo 0 («La foto es en blanco y negro»; el pool solo menciona fotos «sepia» en el `cita_literal` de Q25, de otra escena) y párrafo 22 (cita Q07, fecha 2022, pegada a la abolición de 2007).

## Constantes
| valor | origen | quién |
|---|---|---|
| `claude-sonnet-5-5`, effort `medium` | `m01e_pantalla.MODELO/EFFORT` (producción) | Omar 2026-10-26 |
| `claude-opus-5-5` | id ya usado en el proyecto (canon visual F50f); está en `hx.PRICES` | Omar 2026-10-28 |
| effort `high` (solo brazo O3) | valor de la API; mide si el razonamiento largo suma | analista (voto); Omar confirma al pegar |
| 2 corridas por brazo | mínimo para ver si el resultado cambia entre corridas | analista (voto); Omar confirma al pegar |
| `max_tokens` = `hx.MAX_TOKENS` | el mismo que usa `m01e_pantalla.llamar.autor` | ya existe |
| 22 llamadas a la vez (8 de A + 14 de B) | Omar: workers al máximo (preferencias, 2026-10) | Omar |
| sin tope de dólares en lab | DECISIONES 2026-10-29 (el costo se informa, no frena). Estimado del auditor: ≈ US$ 8–9 en total | Omar |
| `caben`, 15 cps, `callout_dur_max`, velocidad del narrador | los de `m01e_pantalla` tal cual | ya existen |
| `a_pantalla` de la escaleta: 6 (D01, D23, D34, D40, D51, D61) | `01a_escaleta.json` | derivado |
| coincidencia entre corridas = beats (de 13) con el mismo `pool_id` de ficha en las dos, ÷ 13 | derivado | analista |

## Módulos
- `script_engine/m01e_pantalla.py`: **solo se importa**: `cargar`, `entrada`, `entrada_md5`, `_para_modelo`, `PANTALLA_SYSTEM`, `FORMATO_SALIDA`, `validar`, `armar`, `a_markdown`, `estilo_de`. No se edita. **Nunca se llama a `llamar` ni a `generar`** (traen caché, tope, vueltas, modelo fijo y escriben en el directorio del topic).
- `script_engine.clima.vocabulario_clima()` (solo se importa) para el vocabulario.
- `lab/hyperframes/f63/etapa_a_papel.py` (nuevo, lab): arma las entradas, llama a los modelos, valida, escribe los papeles y la tabla.
- `lab/hyperframes/f63/etapa_b_verificador.py` (nuevo, lab): verificador de narración, solo mide.

## Cómo se llama al modelo (A y B)
El runner arma el body como `m01e_pantalla.llamar.autor`: `{"model", "max_tokens": hx.MAX_TOKENS, "system", "messages": [{"role": "user", "content": USER}], "output_config": {"effort"}}` y llama a `hx._post(body)` directo. Costo con `hx.cost_of(model, usage)`; se registra con `hx._track(model, usage, "lab_f63_<brazo>_<n>")` **sin** `cost_tracker.start_video/end_video` (no se escribe `data/cost_history.json`); tokens, US$ y segundos van en el `raw.json` de cada llamada y en el reporte. Si una respuesta no trae JSON: un reintento de la misma llamada; si falla de nuevo, se anota y sigue el resto.

## Parte A — cuatro brazos, 2 corridas cada uno (8 llamadas a la vez)
| brazo | modelo | effort | entrada | prompt |
|---|---|---|---|---|
| S | Sonnet 5.5 | medium | la de hoy | `PANTALLA_SYSTEM` tal cual (md5 `7d2ccdd2…`, el que mida CC) |
| O1 | Opus 5.5 | medium | la de hoy | `PANTALLA_SYSTEM` tal cual |
| O2 | Opus 5.5 | medium | **completa** (A.1) | `PANTALLA_SYSTEM` con la **oración 2** reemplazada (A.2); md5 esperado `85d094bed6090b14d1802ca97433d982` |
| O3 | Opus 5.5 | high | completa | igual que O2 |

S contra O1 mide el modelo; O1 contra O2 mide la información; O2 contra O3 mide el esfuerzo. USER = `json.dumps(<entrada para el modelo>, ensure_ascii=False) + "\n\nFormato de salida: " + FORMATO_SALIDA`, como `m01e_pantalla.pedido`. **Solo intento 1: sin reintento ni vueltas**, en los 4 brazos por igual.

**Entrada de hoy (S, O1):** `carga = cargar(tid, steps_dir)`, `ent = entrada(carga, vocabulario_clima())`, al modelo `_para_modelo(ent)`. **Chequeo:** `entrada_md5(ent)` tiene que dar `a2b19d01f425b58b959b455d2e691c89` (el `entrada_md5` de `01e_pantalla.raw.json`); si no da, PARÁ y reportá qué cambió (p. ej. la velocidad del narrador, que cambia `caben`).

### A.1 Entrada completa (O2, O3) — por código en el runner, igual para cualquier tema
1. `archivo` = **todos** los ítems de `datos`, `cronologia`, `citas`, `personajes` y `lugares`: en el proceso del runner (sin editar el archivo) se reemplaza `m01e_pantalla._tipo` por un mapeo de `_kind` a D/T/Q/P/L para todo ítem y se llama a `entrada(...)`; así `beats_que_lo_cuentan`, `a_pantalla`, `autor`, `rol` y `testimonio` salen igual que hoy. Después, en los ítems L el `texto` pasa a «nombre — rol», y **todo** ítem suma `contexto_fuente` = su `cita_literal` (o la del primer elemento de `evidencia` si falta).
2. `beats`: cada beat de `entrada` **más** `emocion`, `imagen_sensorial`, `pregunta_abierta`, `paga` de `01a_escaleta.json`, cruzados por `n`.
3. `escaleta_video` = `promesa_gancho`, `loops`, `recuerda_loop`, `pico`, `humano`, `antagonista`, `cierre_humano` de `01a_escaleta.json` tal como están.
4. `disputas` = `versiones` y `contradicciones` de `ficha_caso.json` tal como están.
Al modelo va `_para_modelo(ent)` + `escaleta_video` + `disputas` (con el archivo y los beats de arriba). Tamaño medido por el auditor: ≈ 56 k tokens. `estilo_de` ya resuelve L y D sin cifra (normal / papel); no hace falta arreglo.

### A.2 Prompt de O2/O3 — un solo reemplazo en `PANTALLA_SYSTEM` (oración 2 del primer párrafo)
Antes (byte a byte; aparece una vez en el código):
> Recibís la narración completa de un video (7 capítulos, oraciones numeradas), la escaleta (qué cuenta cada beat y cuál es el pico de cada capítulo), el archivo del caso (datos con cifra, fecha, cita o persona, con su fuente) y una lista de palabras de clima.

Después:
> Recibís la narración completa de un video (7 capítulos, oraciones numeradas), la escaleta (qué cuenta cada beat y cuál es el pico de cada capítulo; en `escaleta_video`, la promesa del gancho, las preguntas que el video deja abiertas y dónde las paga, y el pico del video), el archivo del caso (todo lo que encontró la investigación: datos, fechas, citas, personas y lugares, cada uno con su fuente y, en `contexto_fuente`, el fragmento original de la fuente), las versiones en disputa del caso (`disputas`) y una lista de palabras de clima. El `respaldo` se copia siempre del `texto` del dato, nunca de `contexto_fuente`.

Nada más del prompt cambia. md5 del SYSTEM de cada brazo en el reporte (O2/O3 = `85d094bed6090b14d1802ca97433d982`; si no da, PARÁ).

### A.3 Validación «solo anotar»
Antes de validar: `ent["_pool"] = carga["pool"]`. A cada respuesta: `validar(resp, ent, {}, final=True)` (pura, no escribe) y `armar(ent, res)`. No se corta nada en lo que se mira: cada ficha que propuso el modelo queda con **la primera regla que la cortaría** (orden del código) y su motivo, o «pasa». Reglas del código: `anclaje`, `formato`, `respaldo`, `fecha_relato`, `cita_sin_fecha`, `candado`, `no_dicho`, `spoiler`, `contradice`, `una_vez`, `caben`, `sello`; relojes con `error`; `picos_vacios` y `a_pantalla_vacios` tal como salen.

### A.4 Salida A
1. `lab/hyperframes/f63/a/<brazo>_<n>.md` = `a_markdown(armar(...))` con dos cambios en el runner: (a) después de cada línea de beat, por cada ficha que propuso el modelo, `pasa` o `cortaría: <regla> — <motivo>` (los descartados con `quien == "validación"`); (b) en el encabezado, el md5 del SYSTEM de ese brazo en lugar de `prompt_md5()`.
2. `lab/hyperframes/f63/a/<brazo>_<n>.raw.json` (body enviado, respuesta, validación, tokens, US$, segundos).
3. Tabla en `F63_REPORT.md`, una fila por brazo y corrida: fichas propuestas · fichas que pasan · cortadas por primera regla (conteo por regla) · gancho con ficha (sí/no y cuál) · picos con ficha (x/7) · `a_pantalla` cubiertos (x/6) · ids de la escaleta usados · sellos · relojes · tokens in/out · US$ · segundos · coincidencia entre corrida 1 y 2 (definición en Constantes).
4. Copia de los 8 `.md` sin nombre de brazo ni md5, en orden al azar, en `lab/hyperframes/f63/a/ciego/`, con la clave en `a/clave_ciego.json`.

## Parte B — verificador de narración (solo mide; a la vez que A)
Opus 5.5, effort medium, **una llamada por cap** (7 × 2 corridas = 14) sobre `01b_narracion_v3.json` de producción (md5 `c7badfbe260f5eb24a47e780b40406b5`; si no coincide, PARÁ). USER = JSON `{"cap": "chNN", "oraciones": [{"idx", "texto"}], "archivo": [...], "disputas": <A.1.4>}` + `"\n\nFormato de salida: "` + el formato. Las oraciones y sus `idx` son los de `entrada(...)["caps"]` (contados por cap). El `archivo` de B lleva por ítem solo `id`, `texto`, `fecha`, `fuente`, `contexto_fuente` (los de A.1.1).

SYSTEM (entero, literal; md5 esperado `ce31cc515a077d74da72479e9693296e`):
```
Sos el verificador de hechos de un documental de historia en español. Recibís las oraciones numeradas de un capítulo y el archivo del caso: cada dato con su id, su texto, su fecha, su fuente y, en `contexto_fuente`, el fragmento original de la fuente; y las versiones en disputa del caso.

Para cada oración, separá las afirmaciones de hecho que quien escucha va a tomar como verdad: quién, qué, cuándo, cuánto, dónde, cómo era algo, quién dijo qué y en qué momento. No listes preguntas, transiciones ni frases que no afirman un hecho. No juzgues el estilo.

Para cada afirmación, un estado:
- respaldada: un dato del archivo la sostiene (poné su id);
- contradice: un dato del archivo, o su contexto_fuente, dice otra cosa (poné el id y el fragmento literal que lo muestra);
- sin_respaldo: nada del archivo la sostiene ni la contradice.
Una cita atribuida a una fecha o a un hecho distinto del que dice el archivo es «contradice». Si el archivo trae versiones en disputa y la oración da una sola como cierta, es «contradice» con las dos versiones en el fragmento.

Devolvé solo JSON.
```
Formato: `{"cap": "ch01", "afirmaciones": [{"oracion": 0, "afirmacion": "…", "estado": "respaldada" | "contradice" | "sin_respaldo", "ids": ["D85"], "fragmento": "…" | null}]}`

### B.1 Contrato (idx = los de `entrada(...)["caps"]`)
| cap [idx] | qué dice la voz | cuenta como encontrada |
|---|---|---|
| ch01 [1] «Ese pie va a cerrar…» | la herida cierra | contradice D85 («no se cerraba») |
| ch01 [2] «La foto es en blanco y negro.» | color de la foto | contradice Q25 (contexto_fuente «sepia family photos») **o** sin_respaldo; el analista decide cuál vale |
| ch06 [10] «Hacia junio de 2007, según otras referencias en 2006…» | fecha de la abolición | respaldada con D31 o D30 en `ids` |
| ch06 [12] «El gobierno de Australia Occidental lo llamó «el fin de un período oscuro…»» | cita pegada a 2007 | contradice Q07 (fecha 2022) |
Si un idx no coincide con la oración citada, se busca por el texto y se anota el idx real.

### B.2 Salida B
`lab/hyperframes/f63/b/verificador_<cap>_<n>.json` y en `F63_REPORT.md`: por cap y corrida, afirmaciones totales · respaldadas · contradice · sin_respaldo; la lista entera de «contradice» y «sin_respaldo» (oración, afirmación, ids, fragmento); las 4 filas del contrato (qué salió en cada corrida); afirmaciones «contradice» que salen en las dos corridas; tokens, US$, segundos.

## Reglas fijas
- No se edita nada fuera de `lab/hyperframes/f63/` y `lab/ESTADO_SESION.md`. Al final: mtimes de `script_engine/`, `data/scripts/_steps/123bbb64-…/`, `data/cost_history.json`, `output/` y `logs/` antes y después (iguales).
- Los textos de A.2 y de B van byte a byte; md5 de cada SYSTEM en el reporte contra los esperados.
- Commit de `lab/hyperframes/f63/` y `lab/ESTADO_SESION.md` (sin `.env`, `config.py`, `lab/_gpt_probe_analista/`). Sin merge.
- `F63_REPORT.md` con el veredicto íntegro del subagente `revisor-handoff` (el mismo que usó F62) + adenda. Si no está disponible, decilo en el reporte y usá un subagente general con la misma tarea.

## PARADA
Al terminar A y B: commit, reporte, **PARADA**. El analista lee los 8 papeles a ciegas, los califica con DEBERÍA contra el papel de hoy y revisa cada «contradice / sin_respaldo» de B. Omar decide con eso qué entra a producción. Nada de producción en esta tanda.
