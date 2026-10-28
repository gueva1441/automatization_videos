# HANDOFF F48 — Que al prompt de foto le llegue lo que el research ya tiene (entrada arreglada, medida en texto con Opus, por etapas)

Analista, 2026-10-28 03:50. Pedido de Omar (03:34): «si dale» a arreglar primero la entrada del prompt de foto (en texto, barato) y recién después fotos con Opus. Opus 5.5 queda como el modelo de los casilleros para estas pruebas (F47b; Omar 03:30–03:34).
Tema Wittenoom `123bbb64-9fca-4395-8bf4-57d60e219ef1`. Rama `f11-guion-v4`. Base: `lab/hyperframes/f47/` (E = Opus en F47b) y `lab/hyperframes/f46/f46b/`.

## Qué encontró el analista leyendo el pedido entero de F47b (cap 6) y el pool
| # | Hueco | Medido |
|---|---|---|
| 1 | El pedido dice `GEO: (sin geo)` · `ERA: (sin era)` | `m03_visual.py:1468-1469` lee `canonical_geo/canonical_era`; **nadie los escribe** en producción |
| 2 | Hardcode de Orleans en todos los videos | `m03_visual.py:360` «Ningún menor en celdas de adultos…»; `_LOC_GROUPS` (menores/mujeres/evacuados de la cárcel) |
| 3 | «UBICACIONES DOCUMENTADAS» pone a la gente donde vive hoy | «Minero español en Wittenoom. → Madrid» con «no mezclar en una misma escena»: toma los lugares de cualquier texto que nombre el apellido |
| 4 | El dato de cada beat no llega como texto | cada beat tiene 3–7 ids (D/T/Q); el expediente solo muestra las citas (Q) y el lugar de T; los `datos.texto` (D) y `cronologia.evento` (T) no van |
| 5 | Personas del beat casi siempre vacías | 0 en el cap 2. Si se suman los `personajes` cuyo **nombre entero** sale en el ancla: 11 fotos de los caps 2, 5, 6, 7 ganan su rol (p. ej. cap 7 foto 7 → «Anciano Banjima, activista y víctima de mesotelioma · Wittenoom · 2023, 2024») |
| 6 | Ningún `people_group` Banjima | el pool tiene 35 `personajes` con rol, lugar y años; el canon no los recibe |
| 7 | El año arrastrado choca con la voz | cap 6 foto 2 («diez años antes»): el código pone 1989, los 4 modelos escriben 1979 → el prompt dice «1979 … 1989». Simulado con E: 18/60 fotos tienen año dicho en el ancla, 23/60 el modelo ya pone un año en el setting (solo 1 distinto del código: ese), 19/60 quedan al respaldo |
| 8 | El año sale dos veces | E 33/60 («…Pilbara, 2023, …, 2023.») |
Lo que **no** entra (medido o de otro módulo, va a la lista): la imagen sensorial repetida por beat (Opus ya sigue el ancla: cap 6 fotos 1–9 salen 9 escenas distintas) · `hora` vacía en 0/98 eventos de la cronología (research) · escenas de la ficha sin cruce en beats 4, 8, 11, 12 · canon de una sola época (`spans` 1937-2007) y estilo por época (decisión de Omar) · idioma del cartel por foto · clip Veo.

## Constantes
| Valor | Origen | Quién |
|---|---|---|
| Modelo de los casilleros: `claude-opus-5-5`, effort high | F47b (E); Omar 03:30–03:34 | Omar |
| Caps 2, 5, 6, 7 | los de F47/F47b | analista |
| GEO = `lugar_principal` del perfil (`_steps/<id>/_perfil.json`) | dato existente del research | derivado |
| ERA = «primer año–último año» dichos en la narración del video (`voz_utils.numeros`, 1800–2100) | derivado (Wittenoom: 1943–2024; el perfil dice `anio_fin` 2007 y está mal) | derivado |
| Año por foto: 1) dicho en el ancla; 2) el casillero `year` del modelo; 3)–5) el respaldo de F46b (último del cap anterior, fecha del `dato_central`, `topic_year`). **Se borra** la regla «el de la foto anterior del cap» | simulación de arriba | analista |
| Personas por foto: `personajes` de los ids del beat ∪ `personajes` cuyo `nombre` entero sale en el ancla | simulación de arriba (11 fotos) | analista |
| 5 etapas acumuladas × 1 llamada de Opus por cap | una variable por etapa | analista |
| Tope **US$ 7,00** | E costó 1,13 por los 4 caps en F47b → 5 × 1,13 = 5,65 + canon Flash (~0,01) + margen | Omar confirma al pegar |

## Etapas (acumuladas: cada una = la anterior + UN cambio; todas con Opus en los 4 caps)
| Etapa | Cambio | Dónde | Reemplaza / quita |
|---|---|---|---|
| **S1** | GEO y ERA con los valores de la tabla · se **borra** el bloque «UBICACIONES DOCUMENTADAS» entero | producción `script_engine/m03_visual.py` | quita `_format_documented_locations`, `_documented_places`, `_LOC_GROUPS`, `_LOC_DEST`, su uso en la línea 438 y sus tests en `test_module_f5b.py` / `test_module_f5d.py`. Lo reemplazan el DÓNDE y las PERSONAS por foto del expediente |
| **S2** | El expediente suma **FACTS** por foto: de los ids del beat, `datos.texto` y `cronologia` «fecha · evento», enteros | lab | nada (dato nuevo; las citas siguen) |
| **S3** | **PEOPLE** por foto con la regla de la tabla: rol · lugar · años, sin nombre | lab | reemplaza «personas del beat» (solo ids) de F46b |
| **S4** | Casillero de ruteo `year` + regla de año de la tabla; en la prosa el año va **una vez**: si el `setting` ya trae un año o una década, no se agrega `, {año}`; `style_head` lleva el año final | lab (`armar`, esquema, expediente: la línea `YEAR` muestra solo el año dicho en el ancla o «-», nunca uno arrastrado, para no empujar al modelo) | quita la regla 2 «el de la foto anterior del cap» y el `{setting}, {año}.` incondicional |
| **S5** | Canon regenerado: al final del bloque `people_groups` (texto 1 de F46b) se agrega la lista de `personajes` del pool (rol · lugar · años, sin nombre) | lab (`canon_c`) | nada; el canon de F46b sigue de base |

## Textos nuevos para los LLM (completos; no hay otros)
**S4 — casillero en el esquema y su línea en el SI (junto a `people_group`):**
```
- year: the year (YYYY) in which THIS image's scene takes place, read from the narration fragment, its paragraph and the case file (a year said earlier in the paragraph, «ten years before» a stated year, «now» = the most recent year in the case file). Routing only — not rendered as text.
```
**S2 — encabezado de la línea nueva del expediente:** `FACTS: «…» | «…»` (mismo formato que `QUOTES`).
**S3 — encabezado:** `PEOPLE (role · where · years): …` (reemplaza `PEOPLE (roles)`).
**S5 — se agrega al final del texto 1 de F46b:**
```
Personajes del material (rol · lugar · años; sin nombres). Que ningún grupo que aparezca acá quede fuera de people_groups:
- {rol} · {lugar o "-"} · {años o "-"}
...
```
Revisión del analista sobre el cap 7 foto 7 («En 2023, Marcos Orellana … con Maitland Parker, un anciano Banjima»): S3 le da al modelo «Anciano Banjima, activista y víctima de mesotelioma · Wittenoom · 2023, 2024»; S5 debería crear un grupo Banjima y la foto ir a él en vez de `asbestos_advocates_victims`; S4 no cambia el año (2023 dicho en el ancla). Cap 6 foto 2: S4 → `year` 1979, el prompt deja de decir «1989».

## Chequeos por etapa (tabla S0 = E de F47b | S1 | S2 | S3 | S4 | S5, totales por cap)
Los 10 de F47b, más:
11. año final de la foto y de dónde (1 ancla / 2 `year` / respaldo) y si choca con el año o década del `setting`;
12. foto con persona del pool (S3+) y si la prosa dice su origen;
13. `people_group` de las fotos 7 y 8 del cap 7, y lista entera de `people_groups` del canon (S5).
Además, por etapa: el **diff** del user-prompt contra la etapa anterior para el cap 6 (para ver que cambió solo lo de esa etapa) y los prompts enteros de S5.
**Chascada:** el chequeo 5 (nombres reales) busca solo el `nombre` entero (se va el falso positivo «Subcomité de Wittenoom»).

## Módulos
- `script_engine/m03_visual.py` (producción): hoy arma el pedido de los casilleros con GEO/ERA vacíos y el bloque de ubicaciones de Orleans → después GEO/ERA desde el perfil y la narración, sin bloque de ubicaciones. Tests viejos de ese bloque borrados; test nuevo de GEO/ERA con el perfil de Wittenoom.
- Nuevo `lab/hyperframes/f48/f48_corridas.py`: importa f47/f46b; S2–S5 viven solo en el lab (pasan a producción con C2).

## Paso 0
`DECISIONES.md`, tal cual: «2026-10-28 03:34 · F48: antes de las fotos se arregla la entrada del prompt de foto, medida en texto con Opus 5.5 por etapas (GEO/ERA, fuera el bloque de ubicaciones con el hardcode de Orleans, datos y personas por foto, año por casillero `year` y una sola vez en la prosa, canon con los personajes del pool). Opus 5.5 es el modelo de los casilleros para las pruebas · Omar · F48».

## Parte única
1. S1 en producción + tests (suite rápida verde) → commit.
2. S1…S5 con Opus, caps 2, 5, 6, 7; dentro de cada etapa las 4 llamadas en paralelo; freno antes de cada una; `cost_tracker` con `f48-lab`.
3. Salida `PROMPTS_F48.md`: tablas por etapa, diffs del cap 6, prompts enteros de S5; crudos `slots_S{n}_chNN.json`; `canon_S5.json`; costos.

## Reglas fijas
- Nada en `data/` (salvo `cost_history`), `output/` ni `topics_db`. Cero fotos, cero fal.
- Lo único nuevo para los LLM son los textos de arriba, tal cual.
- Paralelo al máximo (subagentes y workers).
- Prohibido `pytest --collect-only` y `pytest test_*.py` en bloque.
- `F48_REPORT.md` con «lo que queda abierto» y el veredicto íntegro de `revisor-handoff`; `lab/ESTADO_SESION.md`; commit.

## PARADA al terminar. No se pasa nada más a producción ni se generan fotos.
