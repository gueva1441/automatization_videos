# HANDOFF F46b — El prompt de imagen «como cuchillo»: se arma solo, con todo el dato que tenemos (lab, cap 2 de Wittenoom)

Analista, 2026-10-28 02:35. Pedido de Omar (02:24): «afinar ese prompt como cuchillo, hacé las pruebas; el prompt se debe construir solo; darle toda la información que necesite, tenemos mucha información útil». Gasto: «no es problema» (02:00).
Tema Wittenoom `123bbb64-9fca-4395-8bf4-57d60e219ef1`, cap 2 (16 fotos). Rama `f11-guion-v4`. Base: lo que dejó F46 (`lab/hyperframes/f46/`).

## Qué mostró F46 (medido por el analista sobre las 4 hojas)
- Entrada nueva (B1) arregló **lugar y época** (tierra roja, casas de chapa, ropa de los 60: fotos 6, 8, 13, 14, 16).
- **La gente sigue saliendo de otro origen en las 3 variantes**: asiáticos (A6, A7, B1-7, B1-12, B2-11, B2-12), Medio Oriente / Asia del sur (10 en A, B1, B2), africanos (A14, B1-14). Causa: el sujeto dice solo «Spanish …» (una nacionalidad no es un aspecto) y el canon tampoco trae aspecto (`demographics` = nacionalidades). Seedream rellena con su default.
- El año salió 1961 en las 16 (debía ser 1962 desde la foto 2). El lugar del WHERE casi no llegó a la prosa (el tejido de Flash lo pierde).
- B2 cambió más de una cosa a la vez (sin cola de estilo, sin «faceless»): falla del analista. Acá cada variante cambia **una** cosa respecto de C0.

## Diseño: el prompt se arma solo, por código, con un expediente por foto
```
pool v3 + ficha + perfil + escaleta + narración
   └─ canon (step_4e con la ficha, como B1) + people_groups (NUEVO dato: aspecto y ropa por grupo)
   └─ expediente por foto (código): ancla + párrafo · beat (imagen_sensorial, emoción) · AÑO (código) · DÓNDE · escenas de la ficha · citas del beat (texto entero) · personas del beat (rol, sin nombre) · grupos de gente
        └─ Gemini Pro llena los casilleros (mismo SI de producción + 1 casillero de ruteo `people_group`)
             └─ CÓDIGO arma el prompt en el orden de la guía de Seedream 5 Lite (sujeto → aspecto de la gente → lugar+año → estilo → luz → técnica), sin tejido de Flash
                  └─ reglas F8 de producción (menores, sensibles, motivos) igual que hoy → Seedream 5 Lite
```

## Constantes
| Valor | Origen | Quién |
|---|---|---|
| Año de cada foto: 1) primer año de 1800–2100 dicho en el ancla (`voz_utils.numeros`); 2) si no hay, el año de la foto anterior del mismo cap; 3) si es la primera del cap, el último año del cap anterior; 4) si no hay nada, la fecha más precisa del `dato_central` del beat; 5) si no, `topic_year` de hoy | derivado de la narración. Simulado por el analista en los 7 caps: los años que dice la voz son los correctos (cap 2: foto 1 → 1961, foto 2 → 1962, 3–16 arrastran 1962) | analista |
| Orden del prompt: sujeto/acción → aspecto de la gente → mirada → objeto → lugar+año → estilo → luz+paleta → plano/ángulo/lente → 16:9 + «no text» | guía de fal para Seedream 5 Lite (blog.fal.ai/seedream-5-0-lite-prompting-guide: «Subject > Setting > Style > Lighting > Technical») | estándar citado |
| Largo del prompt | **sin tope**: se mide y se reporta | — |
| Fuera del prompt: casillero `mood` y casillero `style` del LLM (lleva «faceless») | guía: sin relleno abstracto; «faceless» contradice las caras. El estilo lo pone `style_head(año)` | analista |
| Cifras (`hard_fact_ids`): **no** entran en C (fotos 12 y 15 del cap 2 las tenían) | sin tejido de Flash no hay quien escriba la unidad en inglés; se reporta, se decide aparte si C gana | analista |
| 2 fotos por prompt (`num_images` 2) | medir la varianza (abierto h9 de F46) | analista |
| Motor y payload de producción (`seedream/v5/lite`, 2560×1440), grade de producción, workers `FLUX_MAX_WORKERS` | existen | — |
| Tope de la tanda **US$ 6,00** | 96 fotos × 0,035 = 3,36 + canon Flash + 1 llamada Pro + 16 traducciones Flash ≈ 3,8; margen | Omar confirma al pegar |

## Variantes (16 prompts cada una × 2 fotos)
| Variante | Qué es | Contra qué se compara |
|---|---|---|
| **C0** | el diseño de arriba, prompt en inglés | A y B1 de F46 |
| **C1** | C0 traducido al idioma de la gente de la escena (acá, español) por Flash; solo traduce, las cifras y años quedan igual | C0 (mide solo el idioma) |
| **C2** | C0 **sin** la oración de aspecto de la gente | C0 (mide solo `people_groups`) |

## Textos nuevos para los LLM (completos; no hay otros cambios de prompt)
**1. Bloque que se agrega al final del prompt de `step_4e` (canon), solo en el lab** — es un **dato** que se pide, no una regla de estilo:
```
═══ BLOQUE EXTRA: people_groups ═══
Lista de los grupos de personas que el material documenta en este caso (hechos, cronología, escenas y citas de arriba). Por grupo, un objeto:
- id: corto, snake_case, en inglés (p. ej. "spanish_migrant_families")
- who: quiénes son y su origen documentado (EN, una frase)
- where_when: dónde y en qué años aparecen (EN, una frase)
- appearance: cómo se ven físicamente según su origen documentado y su época: tono de piel, color y tipo de pelo, rasgos, contextura típica de su trabajo (EN, una frase)
- clothing: ropa, peinado y accesorios de ESE grupo en ESOS años, ese clima y esa clase social (EN, una frase)
Sin nombres propios de personas. Solo grupos que el material documenta; si el material no dice el origen de un grupo, no lo inventes: dejá appearance vacío.
```
**2. Casillero de ruteo que se agrega al esquema de slots de Pro** (como `foto_madre_ref`; tampoco se dibuja como texto):
```
- people_group: a LIST of ids from PEOPLE GROUPS whose members are visible in THIS image (usually one); [] if no person is visible. Routing only — not rendered as text.
```
**3. Encabezado del expediente** (antes de los datos por foto, en el user-prompt de Pro):
```
CASE FILE PER IMAGE — documented data. Use it to make each image specific to its place, year and people; do not invent beyond it.
```
**4. Traducción de C1** (Flash):
```
Translate this image prompt into Spanish. Keep every number, year and proper place name exactly as written. Return only the translated prompt.
```
Revisión del analista sobre la foto 10 (Suez): con el expediente, Pro recibe la cita Q14 entera («Pasamos por el canal de Suez… el calor… los mareos»), la escena 0 de la ficha, año 1962 y el grupo `spanish_migrant_families` con su aspecto → el prompt de C0 queda «Wide shot of Spanish migrant families … They are [olive skin, dark hair …], wearing [early-1960s …]. … deck of a passenger ship in the Suez Canal, 1962. Grainy 35mm documentary photograph, 1962 …». Lo que antes faltaba (aspecto y año) ahora lo pone el código, no depende de que el LLM se acuerde.

## Módulos
Producción: **ninguno se edita** (sin stickers ni mapa). Se importan: `researcher_steps/step_4e_visual_canon` (prompt + bloque extra en el lab), `script_engine/m03_visual` (SI v3, esquema de slots + `people_group`, `_build_seedream_prompt_step2`, `_f8_finish_item`), `script_engine/m03_imagenes_v3` (`load_beats`, `assign_beats`, `beats_block`, `style_head`), `script_engine/voz_utils.numeros`, `engine_profiles`, `asset_manager._generate_image_raw`, `script_engine/image_grade`.
Nuevos en `lab/hyperframes/f46/f46b/`: `f46b_corridas.py` (expediente, canon, slots, armado, variantes, freno), `f46b_hoja.py`.

## Paso 0
`DECISIONES.md`: «2026-10-28 02:24 · F46b: el prompt de imagen se arma solo por código con un expediente por foto (canon + people_groups + año dicho por la voz + escenas y citas del beat), en el orden de la guía de Seedream 5 Lite; A/B en lab con C0/C1 (idioma)/C2 (sin aspecto) y 2 fotos por prompt; el gasto no es problema · Omar · F46b».

## Parte 1 — prompts (texto)
1. Canon C: el de B1 (`canon_B.json` con la ficha) **regenerado** con el bloque extra → `canon_C.json`. Mostrar `people_groups` entero.
2. Expediente por foto (código): ancla y párrafo; beat (`imagen_sensorial`, `emocion`, `intensidad`); AÑO (regla de la tabla, con de dónde salió); DÓNDE (`lugar` de la cronología de los ids del beat + `nombre` de `pool.lugares` de esos ids + `donde` de las escenas); escenas de la ficha cruzadas por ids (donde · quien · que_pasa · sentidos); **citas** del beat (`citas` cuyo id esté en los ids: `texto` entero); personas del beat (`personajes` de esos ids: rol y lugar, **sin nombre**); PEOPLE GROUPS del canon C. → `expedientes.md`.
3. Una llamada a Pro para las 16 (como producción; anclas y beats de `03_visual.json` con `force_assign`).
4. Armado por código en el orden de la tabla; la oración de aspecto = «The people are {appearance}, wearing {clothing}.» por cada grupo de `people_group`; lugar+año = «{setting}, {año}.»; estilo = `style_head(año)` + `STYLE_TAIL`; después las reglas F8 de producción.
5. C1 (traducción) y C2 (sin la oración de aspecto) desde C0.
6. Salida `PROMPTS_C.md`: por foto ancla, año (y de dónde), grupos elegidos, los 3 prompts enteros, palabras de cada uno; y la tabla de chequeos por código: ¿tiene año? ¿tiene un lugar de los DÓNDE? ¿tiene aspecto? (sí/no por foto).

## Parte 2 — generar y comparar
1. Freno antes de cada llamada paga (como F46); costos con `cost_tracker` en `f46b-lab`.
2. 48 prompts × 2 fotos **en paralelo**; grade de producción; a `f46b/C0`, `C1`, `C2` (`ch02_img_NN_a/_b`).
3. Hojas (4, una cada 4 fotos): columnas A | B1 | C0a | C0b | C1a | C1b | C2a | C2b (las `_graded`), rótulo con n.º, año y las primeras 8 palabras del ancla; ancho ≤ 3840 px.
4. Tabla de costos leída de `cost_history` y fotos rechazadas.

## Reglas fijas
- Nada en `data/` (salvo `cost_history`), `output/` ni `topics_db`. Ningún archivo de producción editado.
- Paralelo al máximo (subagentes y workers).
- Lo único nuevo para los LLM son los 4 textos de arriba, tal cual. Ninguna otra regla.
- Prohibido `pytest --collect-only` y `pytest test_*.py` en bloque.
- Reporte `F46b_REPORT.md` con «lo que queda abierto» y el veredicto íntegro de `revisor-handoff`; `lab/ESTADO_SESION.md`; commit.

## PARADA al final de la parte 2. No se elige variante ni se toca producción.
