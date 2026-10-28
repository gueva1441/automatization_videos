# Notas de auditoría — zona guion, parte guion_a

Archivos leídos enteros: `m01a_escaleta.py` (1708 líneas), `guion_v4.py` (1244), `guion_v3_reglas.py` (532), `m01a_columna.py` (456). Los md5 al terminar coinciden con los de A. Todos los imports (a nivel de módulo y los de dentro de funciones) resuelven a nombres que existen hoy. Ningún archivo de mi parte importa módulos de la cadena borrada en F41.

## Estado y etapas respecto de A

- `guion_v3_reglas.py`: A lo marca con etapas hasta `render`; en realidad solo corre en `guion`. El camino a `fondos`…`render` es `gfx_pool.py:92` / `gfx_peak.py:52` → `m05_narrative` (para `adjectives`), y `m05_narrative.py:130` importa `guion_v3_reglas.DATE_PARAPHRASE` recién dentro de `_date_paraphrased`, que solo corre en el juez de la narración (en `guion`). Mismo efecto de sobreconteo en `m01a_escaleta`/`guion_v4`/`m01a_columna` (A los pone en research, papel, voz, assets): solo corren en `guion`.
- `m01a_columna.py`: `estado_a` vivo coincide, pero casi todo el archivo es herramienta manual (`--columna`); solo `institucion_de_la_ficha` (`m01a_escaleta.py:1257`) y `variantes_de` (`m01a_escaleta.py:1581`) corren siempre.
- A no marcó ninguna función como `sin_llamador` en mis cuatro archivos; confirmé dos por lectura (`m01a_escaleta.to_markdown`, `m01a_columna.load`) porque su nombre es genérico y A las contó como usadas.

## Código muerto o inalcanzable desde producción

- `m01a_escaleta.py:1658` `to_markdown`: sin llamador en producción ni en tests; solo `lab/hyperframes/f6, f7, f10…`. El docstring (línea 14) sigue anunciándola.
- `m01a_columna.py:400` `load`: solo `test_module_f17.py`.
- `m01a_columna.py:27-28,93-141` `PROMPT_VERSION_F17`, `SYSTEM_F17_1`, `TAREA_F17_1`: constantes que solo lee `test_module_f17.py` (chequeo byte-idéntico contra el .md); producción usa `SYSTEM`/`TAREA`.
- `m01a_escaleta.py:886-1215` `SYSTEM_V2_F25_1`, `SYSTEM_V2_F24_1`, `SYSTEM_V2_F22_2`, `SYSTEM_V2_F22_1`, `SYSTEM_V2_F16_1` y las constantes `PROMPT_VERSION_V2_F*` / `PROMPT_VERSION_COLUMNA_F17`: cinco prompts viejos (≈ 330 líneas) que solo usan tests; `generate_escaleta_v2` manda siempre `SYSTEM_V2` (línea 1569).
- `guion_v4.py:89-433` `SYSTEM_V5`, `SYSTEM_V5_1`, `SYSTEM_V5_2`, `SYSTEM_V5_3` y `guion_v4.py:67-85` `OFICIO`, `EJEMPLOS_VOZ`: prompts viejos (≈ 350 líneas) solo alcanzables con `version="f15-1"/"f15b-1"/"f22-1"/"f23-1"/"f11c-1"`; el único llamador de producción (`fase1_5.py:427`) no pasa `version`, queda el default `f25-1` (`SYSTEM_V5_4`).
- `guion_v4.py:542,739,765,630` `system_f11c`, `prompt_f11c`, `_largo_line`, `escaleta_section`, más `prompt_version` (línea 771) rama `f11c-1/f13-1` y `LARGOS = ("objetivo", "abierto")`: toda la rama de «largo por capítulo» (`largo="objetivo"`, CAP_TOL ±25 %, líneas 984-991 y 642) solo se activa con parámetros que producción nunca pasa (`largo` y `version` salen por default). Los usan solo `test_module_f11/f11c/f13/f15/f22b`.
- `guion_v4.py:539` `system()` devuelve `system_f11c()` para cualquier `version` desconocida (también un typo), sin avisar.
- `m01a_escaleta.py:1491,1512` `_personas_beat`, `metricas_columna`, `1460-1462` rama `columna` de `build_prompt_v2`, `1486` `TAREA_COLUMNA`, `1482` `PROMPT_VERSION_COLUMNA`, `793-795` `columna == "generar"`: `fase1_5.py:390` siempre pasa `columna=None` (F22d); la rama es alcanzable solo desde tests y lab. Y `m01a_columna.section` (línea 409) queda sin camino de producción por lo mismo.
- `m01a_escaleta.py:1609-1651` `_frozen_is_escaleta` / `frozen_escaleta` y el token `escaleta_frozen` / `skeleton_frozen`: nadie los fija en código de producción (solo `fase1_5.py:382` y `m01a_escaleta.py:782` los leen); alcanzable solo si alguien edita `topics_db.json` a mano. Esa rama llama `validate` sin ficha, `apply_pool_plan(instrucciones=True)` (genera `instrucciones_guionista` que el guion v4 no lee) y se saltea el chequeo `EscaletaSinFicha` de F39 (el `if frozen` va antes, línea 782).
- `m01a_escaleta.py:674` `writer_instructions`: solo la llama `apply_pool_plan(instrucciones=True)`, o sea solo la rama frozen anterior; la escaleta v2 pasa `instrucciones=False` (línea 1591).
- `m01a_escaleta.py:174-179,1565,1573` `_profile` / `topic["_largo"]`: nadie asigna `topic["_largo"]` en producción (F23 lo dejó de poner); el valor es siempre `None` y se usa `CAP_WORDS` de `video_length`. `validate(largo=)` y sus ramas quedaron como parámetro sin uso real.
- `m01a_escaleta.py:155` `MAX_APOYOS = 3`: solo es el default de `validate`, que producción llama siempre con `MAX_APOYOS_FICHA` (el propio comentario lo dice).
- `m01a_escaleta.py:118-141` `SCHEMA`: ya no se manda solo (comentario línea 142); sirve de base de `SCHEMA_FICHA`.

## Dos lógicas para lo mismo

- Contrato del antagonista duplicado: `m01a_escaleta.py:384-393` (dentro de `validate`: institución / ninguno / persona) repite lo que `m01a_columna.py:288-302` `antagonista_problemas` hace con los mismos mensajes; la columna dice que es «el mismo contrato».
- `institucion_de_la_ficha` existe dos veces: `m01a_escaleta.py:1253` es un envoltorio que importa `m01a_columna.py:256` (que tiene la lógica).
- Leer ids con explicación («Q19: …» → Q19): `m01a_escaleta.py:1276` `ids_v2` y `m01a_columna.py:204-221` `_ids`/`leer_ids` son dos copias con la misma idea (el comentario de la columna dice «como `m01a_escaleta.ids_v2`»).
- `_tokens` definida en dos módulos con lógicas distintas: `guion_v3_reglas.py:128` (regex sobre texto normalizado) y `m01a_columna.py:224` (alias de `nombres.partes`).
- Partir en oraciones: `guion_v3_reglas.py:237-241` `sentences_of` y `m01b_guionista.sentences` (usada en `guion_v4.py:849,1045`); dos regex distintas para lo mismo.
- Fechas: `guion_v3_reglas.py:47-48` `_DATE` (usada en `hook_problems`) y `:199-200` `MESES`/`DATE_RE` son dos regex de fecha con alcance distinto en el mismo archivo; más `guion_v4.py:1073` arma una tercera con el día calculado.
- Nombre de modelo por defecto en tres sitios: `guion_v4.py:60` (`DEFAULT_MODELO`), `guion_v4.py:64` (`DEFAULT_MODELO_GUION`) y `m01a_escaleta.py:810` (`DEFAULT_MODELO_ESCALETA`); además `m01a_columna.py:439` escribe a mano «gpt-6.1-sol high» en el markdown en vez de leerlo de `call_for`.
- Dependencia circular entre módulos, resuelta con imports dentro de funciones: `m01a_escaleta` ↔ `guion_v4` (`m01a_escaleta.py:762`, `guion_v4.py:587`) y `m01a_escaleta` ↔ `m01a_columna` (`m01a_escaleta.py:794,1257,1461,1494,1517,1581` y `m01a_columna.py:175`). `ficha_section_v2` vive en la escaleta y la usa la columna.

## Comentarios que contradicen el código

- `guion_v4.py:6-14` (docstring): lista (c) como «cap fuera de ±25 % de su objetivo, video > max_words». Hoy `bloqueantes` no mira `max_words` (F25c lo pasó a `metricas`, `largo_txt`) y con `largo="abierto"` (default) tampoco mira el ±25 % (línea 984).
- `guion_v4.py:7`: «UNA llamada a Pro»; el modelo por defecto del guion es `claude-fable-5-1` (línea 64).
- `guion_v4.py:11` y `guion_v3_reglas.py:294-295,246-248`: dicen que `role_problems` «solo distingue preso / guardia»; desde F21 las clases salen del perfil del caso (`_roles`, línea 249) y sin perfil no evalúa nada.
- `guion_v4.py:60` y `:62-63`: «`call_for(None)` (escaleta, columna)» y «escaleta y columna siguen en DEFAULT_MODELO»; la escaleta usa `DEFAULT_MODELO_ESCALETA = claude-fable-5-1` desde F25c (`m01a_escaleta.py:810`); solo la columna usa hoy `DEFAULT_MODELO`.
- `guion_v3_reglas.py:1-18` (docstring): «reglas DURAS … las llama `m01b_guionista.review`». En el camino v4 `review_v3` solo alimenta `metricas` (`duras_v3`), no frena nada (el único bloqueante de este archivo es `role_problems`, `guion_v4.py:966`).
- `m01a_escaleta.py:786`: mensaje «sin pool: camino v2»; ese camino ya no existe (F41).
- `m01a_escaleta.py:1223-1224` y `:1248`: hablan de «14» bloqueantes; la tupla `BLOQUEANTES_V2` (línea 1231) tiene 13 entradas y el docstring de `generate_escaleta_v2` (línea 1556) y el comentario de `generate_escaleta` (línea 772) dicen «13».
- `m01a_escaleta.py:2-9` mezcla el nombre «Módulo 01a v3» y «escaleta v2» (`generate_escaleta_v2`, `SYSTEM_V2`) para lo mismo; `generate_escaleta` dice «escaleta v3» en el ValueError (línea 786).
- `m01a_escaleta.py:75` comentario «antes {1: 110, 2–6: 190, 7: 110}»: ya cambió dos veces (`video_length`: 110/250/140).

## Números sin origen en DECISIONES (buscados por grep en DECISIONES.md: 0 coincidencias)

- `guion_v4.py:51` `CAP_TOL = 0.25`; `:935` `PALABRAS_POR_SEG = 2.4` (el comentario dice «medido en Vajont F26», no hay estándar citado); `:1017` y 1029 textos con pedido de edición fijo.
- `guion_v3_reglas.py:27` `MAX_QUOTES_PER_PARAGRAPH = 1`; `:32` y `:492` citas de «más de 3 palabras»; `:343` `MAX_TRANSITION_SENTENCES = 2`; `:463` `ANCHOR_MAX_WORDS = 10`; `:500` `ECHO_MAX_WORDS = 6`; frases de ≥ 3 palabras con ≥ 2 de contenido de ≥ 4 letras (`repetition_problems`, líneas 144-158).
- `m01a_escaleta.py:76-79` `WORDS_TOL = 0.15`, `MIN_HUMAN_CAPS = 3`, `Q_MAX_WORDS = 8`; `:464` `max(20, …)` palabras mínimas por beat; `:647` umbral 0.6 de «cuenta lo mismo» en `_screen_by_date`; `:815` `MAX_BEATS_POR_CAP = 3`; `:502` `[:1]` y las listas `ADMIN_TERMS`, `ABSTRACT`, `Q_OPENERS` sin fuente citada.
- `m01a_columna.py:30` `CAPS = 7` (coincide con `CHAPTER_SCHEMA`, pero está escrito dos veces: también `range(1, 8)` en la escaleta y `m01a_columna.CAPS`).

## Otras rarezas

- `m01a_escaleta.py:1265` (`bloqueantes` llama `validate(…, final=True)`) y `:494`: eso hace que las preguntas de pantalla objetivas pasen a aviso en lugar de duro (línea 494); solo `pregunta de pantalla del cap 7` frena. El comentario de la línea 485 habla de «último intento» pero `bloqueantes` siempre pasa `final=True`, así que la regla «rechaza y reintenta» para las preguntas no existe en el camino v2.
- `guion_v3_reglas.py:253` `_roles()` llama a `research_v3.vocabulario()` y la reordena cada vez; `role_class` y `_role_before`/`_role_after` la vuelven a llamar dentro de bucles por persona (`role_problems`, líneas 299-319).
- `guion_v4.py:1166-1169`: dentro del bucle por párrafo, `reparar` recalcula `bloqueantes` completo dos veces por candidato (antes y después).
- `guion_v4.py:1029`: el texto del pedido tiene un salto de línea metido a mitad de oración dentro de la f-string del prompt.
- `guion_v4.py:1062` `replace_repeated_dates` vive acá, pero `guion_v3_reglas.py:209-210` conserva un comentario sobre la versión borrada de ese nombre.
