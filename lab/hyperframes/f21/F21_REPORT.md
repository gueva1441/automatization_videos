# F21 — Familias A + B + F: un solo módulo de nombres, fuera el molde de Orleans, los jueces leen la traducción · REPORTE

2026-10-24 · rama `f11-guion-v4` (base `08d63d9`) · handoff `HANDOFF_F21_nombres_y_borrados.md` (md5 `19fcbb9059995791e75b08ba0b6ff35e`, verificado) · **cero llamadas a modelos, cero prompts tocados, ningún umbral tocado**. La app se cerró a mitad de la tanda; retomé desde los alias de §1.1, con `nombres.py`, `recheck.py` y `recheck_antes.json` ya en disco (el «antes» se tomó sobre el código de `08d63d9` sin cambios, antes de tocar nada).

## 0. En una línea
- **Orleans e Ycuá cumplen §2:** mismo color de compuerta (verde), elegibles iguales o más (no sale nadie), bloqueantes de escaleta y de guion iguales (0) y ningún bloqueante nuevo.
- **Kyshtym cumple §2 en parte.**
  - Entran como personas Osetrov, Komarov, Serov, Ladeishchikova y otras cinco voces en cirílico o con iniciales.
  - Los elegibles pasan de 4 a 9, pero **de los cuatro que nombra el handoff solo Ladeishchikova queda elegible**. Las citas de Osetrov, Komarov y Serov quedan como verificada_parcial, porque el autor viene transliterado («V.M. Osetrov») y el documento ruso dice «Осетров» (transliteración: fuera de §1), y no tienen 3 ítems.
  - **Kyshtym no tiene guion** (F18 paró en la escaleta y F19 en el research): lo de las «citas falsas» y el (b) teniente/sobreviviente se prueba con tests, no con un guion real.
- Costo **US$ 0.00** (`data/cost_history.json`: 486 registros antes y después).

## 1. `RECHECK_f21.md` (íntegro)

Mismos archivos de disco en las dos corridas (`recheck.py`): perfil → `set_vocabulario`; sobre una copia del pool, `add_quote_authors`, `canonical_names`, `presence_v3`, `person_stats`, cifras canónicas, `verify_pool` (con los txt ya bajados) y `person_stats` → compuerta; ficha (`ficha_caso.check`), columna (`m01a_columna.chequeo`), escaleta (`m01a_escaleta.bloqueantes`) y guion (`guion_v4.bloqueantes` + `metricas`). Kyshtym: pool de F20; ficha, columna y escaleta (crudo del pase 2) de F18 contra el pool de F18; **Kyshtym no tiene guion** (F18 paró en la escaleta y F19 en el research). Orleans no tiene columna. Costo: US$ 0.00 (`data/cost_history.json` con 486 registros antes y después).

### Orleans (`ba6c3cac-f7r3`)

| medida | antes | después | Δ |
|---|---|---|---|
| compuerta | verde | verde | = |
| métrica: datos | 558 | 558 | = |
| métrica: citas_verificadas | 162 | 162 | = |
| métrica: elegibles_humano | 32 | 33 | +1 |
| métrica: eventos_con_fecha | 127 | 127 | = |
| personajes en el pool | 69 | 70 | +1 |
| citas verificadas (verify_pool) | 162 | 162 | = |
| citas verificadas parcial | 25 | 25 | = |
| citas sin verificar | 0 | 0 | = |
| cifra canónica | 6,375 | 6,295 | ≠ |
| ficha: lo que sacaría el chequeo | 1 | 1 | = |
| columna: problemas | — | — | = |
| escaleta: bloqueantes | 0 | 0 | = |
| guion: bloqueantes | 0 | 0 | = |
| guion: palabras | 1443 | 1443 | = |
| guion: citas | 7 | 7 | = |
| guion: duras_v3 | 44 | 44 | = |
| guion: humano_caps | [1] | [1] | = |

**Elegibles:** 32 → 33. **Entran:** Warden de Hunt Correctional Center. **Salen:** nadie.
**Personajes nuevos en el pool:** Warden de Hunt Correctional Center. **Que ya no están:** ninguno.
Log antes: ["  [R4] población: oficial 6,375 (F01) · variantes [('5,919', 'D214'), ('6,000', 'D198'), ('6,000', 'D87'), ('6,295', 'D213'), ('6,375', 'D533'), ('7,000', 'D152'), ('8,000', 'D219')]"] · después: ["  [R4] autores de cita sumados como personajes: ['Warden de Hunt Correctional Center']"]
**ficha (igual antes y después):** ['[descartados] [descartados] [descartados] Personas descartadas del research sin pasa → no respaldado: sin ids']
**Guion, bloqueante que aparece:** ninguno · **que desaparece:** ninguno.

### Ycuá (`f8s1-ycua-bolanos`)

| medida | antes | después | Δ |
|---|---|---|---|
| compuerta | verde | verde | = |
| métrica: datos | 227 | 227 | = |
| métrica: citas_verificadas | 52 | 53 | +1 |
| métrica: elegibles_humano | 32 | 34 | +2 |
| métrica: eventos_con_fecha | 62 | 62 | = |
| personajes en el pool | 82 | 84 | +2 |
| citas verificadas (verify_pool) | 52 | 53 | +1 |
| citas verificadas parcial | 30 | 29 | -1 |
| citas sin verificar | 0 | 0 | = |
| cifra canónica | — | — | = |
| ficha: lo que sacaría el chequeo | 0 | 0 | = |
| columna: problemas | 0 | 0 | = |
| escaleta: bloqueantes | 0 | 0 | = |
| guion: bloqueantes | 0 | 0 | = |
| guion: palabras | 1384 | 1384 | = |
| guion: citas | 9 | 9 | = |
| guion: duras_v3 | 40 | 40 | = |
| guion: humano_caps | [1] | [1] | = |

**Elegibles:** 32 → 34. **Entran:** María Berzabé Meza Vda. de Brizuela, don Julio. **Salen:** nadie.
**Personajes nuevos en el pool:** María Berzabé Meza Vda. de Brizuela, don Julio. **Que ya no están:** ninguno.
Log antes: [] · después: ["  [R4] autores de cita sumados como personajes: ['don Julio', 'María Berzabé Meza Vda. de Brizuela']"]
**Guion, bloqueante que aparece:** ninguno · **que desaparece:** ninguno.

### Kyshtym (`f18-kyshtym-mayak`)

| medida | antes | después | Δ |
|---|---|---|---|
| compuerta | verde | verde | = |
| métrica: datos | 208 | 208 | = |
| métrica: citas_verificadas | 20 | 18 | -2 |
| métrica: elegibles_humano | 4 | 9 | +5 |
| métrica: eventos_con_fecha | 22 | 22 | = |
| personajes en el pool | 8 | 16 | +8 |
| citas verificadas (verify_pool) | 20 | 18 | -2 |
| citas verificadas parcial | 4 | 6 | +2 |
| citas sin verificar | 0 | 0 | = |
| cifra canónica | — | — | = |
| ficha: lo que sacaría el chequeo | 1 | 1 | = |
| columna: problemas | 0 | 0 | = |
| escaleta: bloqueantes | 7 | 7 | = |
| guion: bloqueantes | — | — | = |

**Elegibles:** 4 → 9. **Entran:** periódico Komsomolskaya Pravda, В.Д. Камынин, Любовь Ладейщикова, Мама de Надежда Кутепова, Толстиков, Бочкарева. **Salen:** nadie.
**Personajes nuevos en el pool:** I.F. Serov, V.I. Komarov, V.M. Osetrov, Андрей Талевлин, В.Д. Камынин, Любовь Ладейщикова, Мама de Надежда Кутепова, Толстиков, Бочкарева. **Que ya no están:** ninguno.
Log antes: [] · después: ["  [R4] autores de cita sumados como personajes: ['Андрей Талевлин', 'Толстиков, Бочкарева', 'В.Д. Камынин', 'V.M. Osetrov', 'V.I. Komarov', 'I.F. Serov', 'Любовь Ладейщикова', 'Мама de Надежда Кутепова']"]
**ficha (igual antes y después):** ['[descartados] [descartados] [descartados] A. I. Burnazyan, M. A. Demyanovich, Diane  → no respaldado: sin ids']
**escaleta (igual antes y después):** ['a_pantalla D04 también está en un beat: lo que va a pantalla no lo dice la voz', 'a_pantalla D80 también está en un beat: lo que va a pantalla no lo dice la voz', 'a_pantalla Q12 también está en un beat: lo que va a pantalla no lo dice la voz', 'a_pantalla T20 también está en un beat: lo que va a pantalla no lo dice la voz', 'a_pantalla T32 también está en un beat: lo que va a pantalla no lo dice la voz', 'a_pantalla T34 también está en un beat: lo que va a pantalla no lo dice la voz', 'antagonista D50, D68 no es una persona del pool']

Personajes de Kyshtym después (todos):

| nombre | rol | testigo | antagonista | citas | datos | presente en el evento | elegible |
|---|---|---|---|---|---|---|---|
| Lyudmila Krestinina | Jefa del laboratorio de epidemiología del Centro Científico y Práctico de Medicina de Radiación de los Urales | False | False | 2 | 1 | False | **True** |
| Andrei Vazhenin | Oncólogo jefe de la región de Chelyabinsk | False | False | 1 | 0 | False | **True** |
| Zhores Medvedev | Genetista soviético exiliado | False | False | 2 | 11 | True | **True** |
| Lev Tumerman | Científico soviético | True | False | 2 | 3 | False | **True** |
| Igor Vasil'evich Kurchatov | Padre de la ciencia atómica en la Unión Soviética | True | True | 0 | 3 | False | **False** |
| N. V. Timofeyev-Resovskiy | Científico que realizó investigaciones radioecológicas | True | False | 0 | 0 | False | **False** |
| Josef Stalin | Líder de la URSS | False | True | 0 | 1 | False | **False** |
| periódico Komsomolskaya Pravda | — | False | False | 1 | 0 | False | **True** |
| Андрей Талевлин | Abogado de la organización "Pravoznaniye" de Cheliábinsk | False | False | 1 | 0 | False | **False** |
| Толстиков, Бочкарева | Investigadores | False | False | 1 | 0 | False | **True** |
| В.Д. Камынин | Investigador | False | False | 1 | 2 | False | **True** |
| V.M. Osetrov | Maquinista de la estación de bombeo | True | False | 1 | 0 | False | **False** |
| V.I. Komarov | Técnico | True | False | 1 | 0 | False | **False** |
| I.F. Serov | Teniente coronel retirado | True | False | 1 | 1 | True | **False** |
| Любовь Ладейщикова | Residente de la aldea de Mitino | True | False | 1 | 0 | True | **True** |
| Мама de Надежда Кутепова | Practicante en clínica para enfermos por radiación | True | False | 1 | 0 | True | **True** |


## 2. Alias creados y regex latinas que quedan

### 2.1 Alias (función vieja → `script_engine/nombres.py`), marcados `# F21: alias`
| función vieja | ahora |
|---|---|
| `research_v3.person_key` | `nombres.clave` |
| `research_v3.is_named_person` | `nombres.es_persona` |
| `research_v3.same_person` | `nombres.misma` |
| `research_v3.name_terms` | `nombres.terminos` |
| `research_v3._names_in` | `any(nombres.menciona(text, t))` |
| `research_v3._TITLES` / `_TITLES_BASE` | `nombres.tratamientos()` / `nombres.TRATAMIENTOS_BASE` |
| `evidence_pool.norm` | `nombres.norm` (para texto latino da lo mismo que antes: test sobre 500 cadenas de Orleans; «Озёрск» conserva la ё) |
| `evidence_pool.is_person` / `_person_key` | `nombres.es_persona` / `nombres.clave` (y `_ORG_WORDS` → `nombres._ORG`) |
| `evidence._surname` | `nombres.apellido` |
| `guion_v4._surname` / `_is_human` | `nombres.apellido` / `nombres.misma(autor, humano)` |
| `m01b_guionista._surname` | `nombres.apellido` |
| `verify_quotes._named` | `nombres.es_persona` |
| `m01a_columna._tokens` (y con él `persona_de`) | `nombres.partes` |

También pasan por `nombres`, sin alias:
- `research_v3.presence_v3`: `nombres.plegar` + `nombres.posiciones`, porque necesita posiciones dentro del documento y `norm` no conserva el largo. Las dos funciones las agregué yo.
- El chequeo de personajes en R3: `es_persona(…, mononimo_ok=rol)` y «el apellido o cualquier parte del nombre está en el documento».
- `verify_pool`: el autor cerca de la cita, con el apellido o cualquier parte del nombre.
- `m01a_escaleta`: `own_ids`, `_his` y `_sin_verificar_suya` (antes 258-263, 642 y 1265).
- `ficha_caso.problems` (personas descartadas, antes 455).
- `m05.silent_names` y `names_with_role`.
- `guion_v4.unverified_named`: `es_persona`, `menciona`, sin `len(sur) > 3`, y busca también `texto_original`.
- `guion_v3_reglas.role_problems`: `terminos`, `misma` y `menciona`.
- `research_v3.slugify` agrega `-{id}`; `_path_tokens` y `_words` usan `\w+`; `evidence._content` usa `[^\W\d_]`.

### 2.2 Regex latinas que quedan en los archivos de la fase 1
| archivo:línea | qué hace | ¿decide? |
|---|---|---|
| `research_v3.py:556` | saca números de nota pegados a una letra latina | no (limpieza de texto) |
| `evidence_pool.py:126` | siglas entre paréntesis del nombre de una fuente | no (camino v2) |
| `evidence_pool.py:164` `_content_set` | palabras de contenido `[a-z0-9ñ]` | **sí**: `research_v3.same_fact` lo usa para fusionar datos de dos documentos. En cirílico da conjunto vacío, así que dos datos rusos iguales **no se fusionan**. Para F23 |
| `evidence_pool.py:188` | palabras marcadoras | no (camino v2) |
| `evidence_pool.py:257` `person_acts` | busca el verbo después del nombre | **sí**: `acting_filter`, que `build_pool` aplica a los personajes que no son testigos. Un nombre en cirílico no encuentra el verbo y queda afuera. Para F23 |
| `evidence_pool.py:301` `fix_caps` | mayúscula después de «:» | no (formato) |
| `evidence_pool.py:688` | presencia por apellido | no (camino v2) |
| `ficha_caso.py:425-426` `sentidos_problems` | palabras de los sentidos | casi no: la ficha se escribe en español |
| `evidence.py:170` y `:224` | anchors y frases firma | no (métrica de repetición) |
| `evidence.py:332` `fix_glued_caps` | la palabra pegada en mayúscula latina | no (formato) |
| `m05_narrative.py:84`, `181`, `199`, `419`, `456` | palabras, nombres propios y adjetivos para métricas | no (métrica) |
| `guion_v3_reglas.py:105` `full_name_problems` | nombre completo repetido en un cap | no (métrica en v4; dura en v3) |
| `guion_v3_reglas.py:129` | palabras | no |
| `m01a_escaleta.py:1426/1430` `_personas_beat` | personas de la ficha en el texto de un beat (F17) | no (métrica de la columna) |

## 3. Lo que se borró o cambió (§1.2 y §1.3)
- **`research_v3.py`:**
  - `SUBJECT_RE_DEFAULT` (Orleans Parish Prison), `_OTHER_PLACE` (Hunt, Angola, Jena, Templeman…) y `_OFFICIAL_SAYS` (sheriff) se borraron.
  - El sujeto ahora es `subject_re_del_perfil(perfil)` (`nombres_lugar` + `nombres_locales`); `run_seed` se lo pasa a `build_pool`. «Otro lugar» sale de `lugares_excluidos` del perfil (hoy ningún perfil lo trae). La atribución oficial es `oficial(es)|official|registros?|records?|autoridad(es)` + «según <rol de `roles_antagonista`>».
  - `population_canon(subject_re=None)`: no hay default.
  - Las stopwords orleans/parish/prison/katrina/hurricane de `_words` se borraron.
  - `_NOT_PERSON` y `_NOT_PERSON_BASE` se borraron. Las partículas las maneja `nombres.partes`, y los grupos `nombres._GRUPO` + `set_grupos`.
  - `set_vocabulario` llama `nombres.set_tratamientos(roles)` con los roles enteros, como dice el handoff. En F20 los partía en palabras, y así «condado de Orleans» metía «orleans» como tratamiento.
- **`guion_v3_reglas.py`:**
  - `_ROLE_PRESO`, `_ROLE_GUARDIA` y la dicotomía preso/guardia se borraron. `role_class` devuelve «testigo» o «antagonista» según los roles del perfil (`research_v3.vocabulario()`), y sin perfil `None`: **(b) no evalúa nada**. `_ROLE_BEFORE` y `_ROLE_AFTER` se arman con esas palabras.
  - `JUDGMENTS` quedó en «deliberad…», «a propósito/intencional» y «sabían que». Se borraron los de Orleans e Ycuá. «a sabiendas», que el handoff nombra, **no se agregó** (sería un patrón nuevo).
  - `photo_problems` queda solo con foto/fotografía/fotógrafo.
- **`evidence.py`:** `_COMMON_CAPS` se borró. `fix_glued_caps(text, pool=None)` baja a minúscula solo las palabras que van en minúscula en el rol de algún personaje del pool, o un tratamiento de `nombres`. El pool se pasa desde `guion_v4.write` (vía `m01b_guionista.normalize`), `guion_v4.editor_pass`, `m01c_editor.edit` y el narrador v2. `_surname` pasa a alias (y con él se va «sheriff»).
- **`m05_narrative.py`:** de `FORBIDDEN_FILLER` salieron «manto de», «el monstruo», «infierno flotante» y «ecos de».
- **`m01a_escaleta.py`:** `ADMIN_TERMS` en v1 pasa de duro a aviso. La pregunta sigue sin mostrarse en pantalla (`pregunta_valida` no cambia).
- **`m01b_guionista.py`:** `INSTITUTION` (parish, opp, aclu, fema, sheriff…) pasa a ser `institution_re(ficha)`: las «personas» de la ficha que no son personas, más `nombres._ORG`. El gancho con institución pasa a métrica; con año o cifra sigue duro.
- **`verify_quotes.py`:** `build_prompt(q, tema)` y `verify_testimonios(…, tema)`. Sin el tema escrito: es una función dormida, no uno de los cuatro prompts.
- **`evidence_pool.py`:** `_ORG_WORDS` → `nombres._ORG`. `_NOT_VERB`/`_COMMON_HEADS`, `build_prompt` y `_OFICIAL`/`_COUNT_NOUN` son del camino v2 (`RESEARCH_V3=0`): **no se tocaron**.
- **§1.3:** `guion_v4.pool_con_traducciones(pool, ficha)` se aplica al entrar a `bloqueantes()`. Le llega a `false_quotes`, `role_problems` y `unverified_named`; `invented_numbers` y `contamination` siguen con el pool original. `unverified_named` busca la cita por `texto`, `texto_original` y `fragmento`.
- **Comentarios con nombres de Orleans (familia J):** no los neutralicé. Es cosmético, y lo dejo para la tanda que vuelva a abrir esos archivos.

**Diferencias con el texto del handoff, todas de lectura del nombre (no son chequeos nuevos):**
- (1) `nombres.ARTICULOS` (un, una, unos, unas, a, an, the) no cuentan como parte del nombre. Con el código del handoff, «Un oficial» y «Un hijo de Berzabé» eran personas con apellido «un» o «berzabe», y sus citas pasaban de verificada a parcial (lo mostró el recheck).
- (2) Un cargo cuenta solo si va **justo delante** de una parte del nombre («Deputy Foster», «el teniente Ivanov»). Con el código del handoff, «Un recluso de Templeman 4» era persona y elegible en Orleans.
- (3) En `verify_pool`, el autor cerca de la cita vale con el apellido **o cualquier parte del nombre**, el mismo criterio que el handoff fija para R3. Con solo el apellido, Ycuá perdía 4 citas verificadas (Chamorro, Brizuela); ahora gana 5 (Gabaglio, Pujol, Liz Torres, López, Roa) y pierde 4: 52 → 53.
- (4) Agregué `nombres.plegar` y `nombres.posiciones` para `presence_v3`.
- (5) Agregué `research_v3.vocabulario()` (lo pide el handoff) y `"lugares_excluidos"` en `_VOC`.

**Lo que queda raro en el recheck** (para el analista; no lo arreglo, porque haría falta una regla o una lista nueva):
- **Orleans:** entra como persona y elegible «Warden de Hunt Correctional Center». Antes lo descartaba el «de» de `_NOT_PERSON`, que el handoff saca para que «Juan de la Cruz» sea persona. Distinguir «de + lugar» de «de + apellido» necesita una lista.
- **Kyshtym:**
  - entran como elegibles «periódico Komsomolskaya Pravda» (ya era personaje desde F20; ahora su cita verifica porque el autor no es persona, así que no se le pide el apellido cerca), «Мама de Надежда Кутепова» (descripción con nombres) y «Толстиков, Бочкарева» (dos autores en uno). `person_stats` no exige que el personaje sea persona;
  - la transliteración latina ↔ cirílica (Osetrov ↔ Осетров) no existe: es la familia A, «variantes/transliteración del pool» de la auditoría.
- **Tests y `pista_covered`:**
  - `test_module_f7.py::test_pista_covered` dejó de pasar con la pista corta: `_words` ya no resta orleans/parish/katrina. `pista_covered` solo se usa con `pistas`, y `run_seed` nunca las pasa.
  - Adapté 6 tests viejos que codificaban el molde de Orleans, para que reciban el vocabulario por el perfil o el pool: `test_module_f7.py` (fixture Orleans con `abogado`, `lugares_excluidos` y `SUBJECT_ORLEANS`; `test_rule1_role_of_speaker`; `test_pista_covered`), `test_module_f11.py` (b con perfil), `test_module_f5b.py` (`fix_glued_caps` con pool), `test_module_f5c.py` (los 4 rellenos borrados), `test_module_f6b.py` (`ADMIN_TERMS` como aviso) y `test_module_f20.py` (sin `_NOT_PERSON`).

## 4. md5 de los cuatro prompts (iguales a F20; test `test_md5_de_los_cuatro_prompts`)
| prompt | md5 |
|---|---|
| ficha (`ficha_caso.system()`) | `2e151732da47e09acf0cb48eb7089fcb` |
| columna (`m01a_columna.SYSTEM`) | `1408569c5c9de22ec406a10ba0cd9b13` |
| escaleta v2 (`m01a_escaleta.SYSTEM_V2`) | `49ed74d941def064cdda077212629ff1` |
| guion v5.1 (`guion_v4.system()`) | `cdce609abea95ee36d0eb4f44d74dda8` |

## 5. Tests
- `test_module_f21.py` (24):
  - `es_persona` con los 12 casos del handoff, más «un preso de Templeman III»;
  - `clave`, `misma`, `menciona`, `terminos`;
  - `norm` sobre 500 cadenas de Orleans (idéntico al de antes) y con cirílico;
  - `slugify`;
  - los alias;
  - personajes de R3 con iniciales y mononimio en cirílico;
  - `role_class` con perfil, sin perfil y con teniente/sobreviviente;
  - `fix_glued_caps` con los roles del pool;
  - `photo_problems`;
  - sin sujeto de Orleans;
  - `pool_con_traducciones`;
  - md5 de los cuatro prompts.
- Suite amplia: **724 verdes + las 5 previas** (3 `01b_pauses`, 2 `m03_merge_timing`). Incluye el dorado v3 y la escaleta sin ficha byte-idéntica (F16/F17).

## 6. Costo
US$ 0.00. `data/cost_history.json` tiene 486 registros antes y después de las dos corridas del recheck y de los tests.

## 7. Veredicto del revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

Corrí los 7 archivos de test: 133 passed. Corrí `recheck.py revisor` y reproduce el "después" del reporte (Orleans 33 elegibles, Ycuá 34, Kyshtym 9; bloqueantes de escaleta y guion iguales). Borré `recheck_revisor.json`. `cost_history` tiene 486 registros. El md5 del handoff coincide (19fcbb90...).

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | §1.1 `nombres.py` y alias | PARCIAL | El archivo es el del handoff más 4 desvíos. Declarados: `ARTICULOS`, cargo justo delante (`nombres.py:122-126`), `plegar`/`posiciones` (`:155-168`). No declarados: "ranking" en `TRATAMIENTOS_BASE` (es del `_TITLES_BASE` viejo, `research_v3.py:1228` en `08d63d9`, así que es fiel); `"´"` en `_Q` (también estaba en `evidence_pool._QUOTES:93`); `norm` reimplementado por categoría Mn, no por el código literal del handoff; `tratamientos()` agregado. Los alias y conexiones listados están. |
| 2 | §1.2 tabla de borrados | OK | `JUDGMENTS` quedó con 3 patrones estructurales (`guion_v3_reglas.py:73-79`). "a sabiendas" no se agregó, y está declarado. `photo_problems` usa `_PHOTO_ANY`. `_ROLE_PRESO`/`_ROLE_GUARDIA` borrados. `FORBIDDEN_FILLER` sin las 4 frases. El `soft` de `ADMIN_TERMS` v1 está en `m01a_escaleta`. `subject_re_del_perfil` existe (`research_v3.py:1706`). Sin "Orleans Parish" activo en `research_v3`; solo quedan comentarios y docstrings. Los comentarios J no se neutralizaron, y está declarado. |
| 3 | §1.3 `pool_con_traducciones` | OK | `guion_v4.py:604-614` es el del handoff. Test en `test_module_f21.py`. |
| 4 | §1.4/§4 sin prompts, umbrales ni API | OK | 486 registros en `cost_history`. Test de md5 de los 4 prompts en verde. `git diff --stat` no toca `config` ni `m03*`. `_transfer_tmp` no existe. No hay `.env` en el status. `lab/_gpt_probe_analista/` sigue sin trackear, bien. |
| 5 | §2 lo que tiene que pasar | PARCIAL | Orleans e Ycuá: colores iguales (verde), nadie sale, 0 bloqueantes antes y después. Kyshtym: los 4 nombres entran como personas, pero solo Ladeishchikova queda elegible. Osetrov, Komarov y Serov quedan parciales. El guion de F19 no existe, así que "pierde las citas falsas" y "(b) no dispara" se prueban solo con tests, no con un guion real. |
| 6 | §3 tests | OK | Hay 24 tests de F21. Los 6 tests viejos adaptados reflejan solo borrados pedidos por el handoff. Las 6 adaptaciones son legítimas. La excepción es `test_pista_covered` (f7), que perdió la resta de orleans/parish/katrina. Eso es consecuencia directa del §1.2 y queda declarado. |
| 7 | Reporte fiel a los archivos | PARCIAL | Dos desajustes menores. (a) §2.2 dice que `m01a_escaleta` `_personas_beat` "queda" como regex latina, pero el diff lo reescribió con `nombres.clave`/`menciona`. Quedó mejor que lo declarado, pero el reporte no coincide. (b) El §7 del reporte está vacío ("se pega abajo"), a la espera de este veredicto. |

**Sobre las diferencias declaradas (pregunta 1)**
- ARTICULOS, cargo justo delante y `verify_pool` "apellido o cualquier parte del nombre" son lecturas más estrictas o más laxas de qué cuenta como nombre. No agregan ninguna regla de rechazo nueva.
- El recheck muestra que sin ARTICULOS y sin "justo delante" el código del handoff metía falsos positivos en Orleans.
- El desvío de `verify_pool` es el más cercano a criterio nuevo: se aplicó al camino de verificación de citas, no solo a R3. Es defendible porque el handoff fija ese criterio para R3, pero no lo pide para `verify_pool`.
- `set_tratamientos(roles)` con roles enteros es lo que el handoff escribe literalmente.

**Sobre la PARADA de Kyshtym (pregunta 5)**
- El handoff dice "si no, PARADA y me lo contás antes de tocar nada más". El criterio fallido es "entran … como candidatos a elegible … Osetrov, Komarov, Serov". Se cumplió a medias.
- Aun así, creo que reportarlo alcanza. Las citas de los 3 quedan parciales por transliteración latina↔cirílica, y eso es la familia A pendiente de la auditoría. No se resuelve sin una regla o lista nueva, que §4 prohíbe.
- La tanda ya estaba terminada y no se tocó nada después de verlo. Omar decide si lo considera falla del criterio.
- Hay un efecto lateral que el reporte declara: Kyshtym suma "Komsomolskaya Pravda", "Мама de Надежда Кутепова" y "Толстиков, Бочкарева" como elegibles que no son personas.
- Orleans gana "Warden de Hunt Correctional Center" como elegible, también declarado.
- El recheck da `ficha 1` en Orleans, igual antes y después.

**Fuera de alcance:** ninguno. Los archivos modificados son los del §1 más los 6 tests adaptados. Los untracked previos (`_lab_*`, `_probe_*`, `lab/_gpt_probe_analista/`) no son de F21 y no hay que commitearlos.

**Riesgos que el contrato no cubre:**
- `evidence_pool._content_set` y `person_acts` siguen con regex latinas que sí deciden: datos rusos iguales no se fusionan y los nombres cirílicos quedan fuera de `acting_filter`. Están listados para F23.
- Kyshtym no tiene guion: "Kyshtym cumple §2" es solo verdad hasta la escaleta.

**Notas de CC después del veredicto** (verificadas, sin cambios de código):
- (a) **No se sostiene.** `_personas_beat` (`m01a_escaleta.py:1415-1432`) sigue con `re.findall(r"[a-z0-9ñ]+", ev.norm(…))`. F21 tocó en ese archivo `own_ids`, `_his` y `_sin_verificar_suya`, no `_personas_beat`, así que §2.2 dice lo que hay en el archivo.
- Los desvíos «no declarados» de la fila 1 quedan declarados acá:
  - «ranking» en `TRATAMIENTOS_BASE` y «´» en `_Q`: son los valores de antes (`_TITLES_BASE` y `evidence_pool._QUOTES`), y se agregaron para que `norm` y los tratamientos no cambien en texto latino;
  - `norm` escrito por categoría Mn: el código literal del handoff dejaba las tildes ya descompuestas (frecuentes en PDF), y el viejo las sacaba;
  - `tratamientos()` es un getter que usan `research_v3._TITLES` y `canonical_names`.

---

## F21b — perfil en el guion, atribución oficial, dos criterios de forma (sobre `b24c505`; cero API, cero prompts)

### 1. Qué se hizo
1. **El perfil entra en el camino del guion.**
   - `fase1_5.cargar_perfil(topic_id)` carga `_steps/<id>/_perfil.json` en `research_v3.set_vocabulario`. La llama `_topic_v3`, que usan la escaleta y el guion v4, así que corre antes de cualquier bloqueante; sin perfil, vacía el vocabulario.
   - `guion_v4.nota_b()` devuelve «(b) sin perfil: no evaluado» cuando no hay roles. `run_guion_v4` la guarda en `01b_guionista_v4.json` (`nota_b`) y la imprime.
   - Perfil canónico: en Orleans e Ycuá copié `_perfil_f20.json` a `_perfil.json`. Ycuá ya tenía uno y quedó como `_perfil_pre_f20.json`; Orleans no tenía (`data/` no se commitea).
   - `recheck.py` lee `_perfil.json` en los tres temas.
2. **Atribución oficial:** `research_v3._official_says` cuenta un rol de `roles_antagonista` en cualquier parte del dato (palabra entera), no solo después de «según».
   - **Orleans vuelve a 6,375 (F01) como oficial**: el dato D51 del documento F01 tiene «sheriff».
   - Pero el grupo de población trae solo la variante 7,000 (antes de F21 eran 5,919, 6,000 ×2, 6,295, 6,375, 7,000 y 8,000). El perfil de Orleans no tiene `nombres_lugar`, porque su `place_re` de F7 se escribió a mano y nunca pasó por `seed_profile`. Entonces `subject_re_del_perfil` da `None`, y solo entran los datos con atribución oficial. Además sigue el grupo 6,295 de `canonical_v3`, que ya estaba en F21.
   - Para recuperar las variantes, el perfil de Orleans necesita `nombres_lugar`. No lo toqué.
3. **`nombres.es_persona`, criterios de forma:**
   - con coma, « y » o « and » no es una persona. La coma antes de un sufijo (Jr., Sr., II, III, IV) sí es parte del nombre: «Leroy P. Gardner, III» y «Ronnie Lee Morgan, Jr.» siguen siendo personas. Sin ese ajuste dejaban de serlo, y la cita de Gardner se verificaba sin pedir el apellido, lo que lo volvía elegible;
   - un tratamiento o cargo seguido de partícula («de», «del», «of»…) es un cargo («Sheriff de Orleans Parish», «Captain of the Guard»);
   - `add_quote_authors` los salta porque usa `is_named_person` (test).
   - **No alcanza a «Warden de Hunt Correctional Center»**: «warden» no es tratamiento (F20 lo sacó de `_TITLES` por ser término de tema, y el perfil de Orleans no lo trae). Tampoco a «Director of…», que no es tratamiento, aunque «Director of Corrections» ya era no-persona por la palabra en minúscula. Para que esos dos entren hay que agregar «warden» y «director» a `TRATAMIENTOS_BASE`, o a los roles del perfil. Decide Omar.
4. **Recheck en HEAD.** Corrí `recheck.py` con el código exacto de `b24c505`: worktree con `data/` enlazado y `config` leído del repo, sin copiarlo porque tiene una clave. Dio **idéntico** al `recheck_despues.json` commiteado. `RECHECK_f21.md` ya correspondía al commit, y lo regeneré igual (solo cambió el título).

Tests: 14 nuevos en `test_module_f21.py` (38 en total):
- (b) con perfil evalúa y sin perfil no, más `nota_b` y `cargar_perfil`;
- el rol que decide en cualquier parte;
- los criterios de forma, incluido el sufijo;
- `add_quote_authors`.

Suite amplia: **738 verdes + las 5 previas**. US$ 0.00 (`cost_history` 486).

### 2. Cifras F21 (`b24c505`) → F21b (`RECHECK_f21b.md`)

Mismos archivos de disco en las dos corridas (`recheck.py`): perfil → `set_vocabulario`; sobre una copia del pool, `add_quote_authors`, `canonical_names`, `presence_v3`, `person_stats`, cifras canónicas, `verify_pool` (con los txt ya bajados) y `person_stats` → compuerta; ficha (`ficha_caso.check`), columna (`m01a_columna.chequeo`), escaleta (`m01a_escaleta.bloqueantes`) y guion (`guion_v4.bloqueantes` + `metricas`). Kyshtym: pool de F20; ficha, columna y escaleta (crudo del pase 2) de F18 contra el pool de F18; **Kyshtym no tiene guion** (F18 paró en la escaleta y F19 en el research). Orleans no tiene columna. Costo: US$ 0.00 (`data/cost_history.json` con 486 registros antes y después).

### Orleans (`ba6c3cac-f7r3`)

| medida | antes | después | Δ |
|---|---|---|---|
| compuerta | verde | verde | = |
| métrica: datos | 558 | 558 | = |
| métrica: citas_verificadas | 162 | 162 | = |
| métrica: elegibles_humano | 33 | 33 | = |
| métrica: eventos_con_fecha | 127 | 127 | = |
| personajes en el pool | 70 | 70 | = |
| citas verificadas (verify_pool) | 162 | 162 | = |
| citas verificadas parcial | 25 | 25 | = |
| citas sin verificar | 0 | 0 | = |
| cifra canónica | 6,295 | 6,375; 6,295 | ≠ |
| ficha: lo que sacaría el chequeo | 1 | 1 | = |
| columna: problemas | — | — | = |
| escaleta: bloqueantes | 0 | 0 | = |
| guion: bloqueantes | 0 | 0 | = |
| guion: palabras | 1443 | 1443 | = |
| guion: citas | 7 | 7 | = |
| guion: duras_v3 | 44 | 44 | = |
| guion: humano_caps | [1] | [1] | = |

**Elegibles:** 33 → 33. **Entran:** nadie. **Salen:** nadie.
**Personajes nuevos en el pool:** ninguno. **Que ya no están:** ninguno.
Log antes: ["  [R4] autores de cita sumados como personajes: ['Warden de Hunt Correctional Center']"] · después: ["  [R4] autores de cita sumados como personajes: ['Warden de Hunt Correctional Center']", "  [R4] población: oficial 6,375 (F01) · variantes [('7,000', 'D152')]"]
**ficha (igual antes y después):** ['[descartados] [descartados] [descartados] Personas descartadas del research sin pasa → no respaldado: sin ids']
**Guion, bloqueante que aparece:** ninguno · **que desaparece:** ninguno.

### Ycuá (`f8s1-ycua-bolanos`)

| medida | antes | después | Δ |
|---|---|---|---|
| compuerta | verde | verde | = |
| métrica: datos | 227 | 227 | = |
| métrica: citas_verificadas | 53 | 53 | = |
| métrica: elegibles_humano | 34 | 34 | = |
| métrica: eventos_con_fecha | 62 | 62 | = |
| personajes en el pool | 84 | 84 | = |
| citas verificadas (verify_pool) | 53 | 53 | = |
| citas verificadas parcial | 29 | 29 | = |
| citas sin verificar | 0 | 0 | = |
| cifra canónica | — | — | = |
| ficha: lo que sacaría el chequeo | 0 | 0 | = |
| columna: problemas | 0 | 0 | = |
| escaleta: bloqueantes | 0 | 0 | = |
| guion: bloqueantes | 0 | 0 | = |
| guion: palabras | 1384 | 1384 | = |
| guion: citas | 9 | 9 | = |
| guion: duras_v3 | 40 | 40 | = |
| guion: humano_caps | [1] | [1] | = |

**Elegibles:** 34 → 34. **Entran:** nadie. **Salen:** nadie.
**Personajes nuevos en el pool:** ninguno. **Que ya no están:** ninguno.
**Guion, bloqueante que aparece:** ninguno · **que desaparece:** ninguno.

### Kyshtym (`f18-kyshtym-mayak`)

| medida | antes | después | Δ |
|---|---|---|---|
| compuerta | verde | verde | = |
| métrica: datos | 208 | 208 | = |
| métrica: citas_verificadas | 18 | 18 | = |
| métrica: elegibles_humano | 9 | 8 | -1 |
| métrica: eventos_con_fecha | 22 | 22 | = |
| personajes en el pool | 16 | 15 | -1 |
| citas verificadas (verify_pool) | 18 | 18 | = |
| citas verificadas parcial | 6 | 6 | = |
| citas sin verificar | 0 | 0 | = |
| cifra canónica | — | — | = |
| ficha: lo que sacaría el chequeo | 1 | 1 | = |
| columna: problemas | 0 | 0 | = |
| escaleta: bloqueantes | 7 | 7 | = |
| guion: bloqueantes | — | — | = |

**Elegibles:** 9 → 8. **Entran:** nadie. **Salen:** Толстиков, Бочкарева.
**Personajes nuevos en el pool:** ninguno. **Que ya no están:** Толстиков, Бочкарева.
Log antes: ["  [R4] autores de cita sumados como personajes: ['Андрей Талевлин', 'Толстиков, Бочкарева', 'В.Д. Камынин', 'V.M. Osetrov', 'V.I. Komarov', 'I.F. Serov', 'Любовь Ладейщикова', 'Мама de Надежда Кутепова']"] · después: ["  [R4] autores de cita sumados como personajes: ['Андрей Талевлин', 'В.Д. Камынин', 'V.M. Osetrov', 'V.I. Komarov', 'I.F. Serov', 'Любовь Ладейщикова', 'Мама de Надежда Кутепова']"]
**ficha (igual antes y después):** ['[descartados] [descartados] [descartados] A. I. Burnazyan, M. A. Demyanovich, Diane  → no respaldado: sin ids']
**escaleta (igual antes y después):** ['a_pantalla D04 también está en un beat: lo que va a pantalla no lo dice la voz', 'a_pantalla D80 también está en un beat: lo que va a pantalla no lo dice la voz', 'a_pantalla Q12 también está en un beat: lo que va a pantalla no lo dice la voz', 'a_pantalla T20 también está en un beat: lo que va a pantalla no lo dice la voz', 'a_pantalla T32 también está en un beat: lo que va a pantalla no lo dice la voz', 'a_pantalla T34 también está en un beat: lo que va a pantalla no lo dice la voz', 'antagonista D50, D68 no es una persona del pool']

Personajes de Kyshtym después (todos):

| nombre | rol | testigo | antagonista | citas | datos | presente en el evento | elegible |
|---|---|---|---|---|---|---|---|
| Lyudmila Krestinina | Jefa del laboratorio de epidemiología del Centro Científico y Práctico de Medicina de Radiación de los Urales | False | False | 2 | 1 | False | **True** |
| Andrei Vazhenin | Oncólogo jefe de la región de Chelyabinsk | False | False | 1 | 0 | False | **True** |
| Zhores Medvedev | Genetista soviético exiliado | False | False | 2 | 11 | True | **True** |
| Lev Tumerman | Científico soviético | True | False | 2 | 3 | False | **True** |
| Igor Vasil'evich Kurchatov | Padre de la ciencia atómica en la Unión Soviética | True | True | 0 | 3 | False | **False** |
| N. V. Timofeyev-Resovskiy | Científico que realizó investigaciones radioecológicas | True | False | 0 | 0 | False | **False** |
| Josef Stalin | Líder de la URSS | False | True | 0 | 1 | False | **False** |
| periódico Komsomolskaya Pravda | — | False | False | 1 | 0 | False | **True** |
| Андрей Талевлин | Abogado de la organización "Pravoznaniye" de Cheliábinsk | False | False | 1 | 0 | False | **False** |
| В.Д. Камынин | Investigador | False | False | 1 | 2 | False | **True** |
| V.M. Osetrov | Maquinista de la estación de bombeo | True | False | 1 | 0 | False | **False** |
| V.I. Komarov | Técnico | True | False | 1 | 0 | False | **False** |
| I.F. Serov | Teniente coronel retirado | True | False | 1 | 1 | True | **False** |
| Любовь Ладейщикова | Residente de la aldea de Mitino | True | False | 1 | 0 | True | **True** |
| Мама de Надежда Кутепова | Practicante en clínica para enfermos por radiación | True | False | 1 | 0 | True | **True** |


### 3. Lo que sigue raro
- **Orleans:** «Warden de Hunt Correctional Center» sigue como persona y elegible (punto 3).
- **Kyshtym:** siguen como elegibles «periódico Komsomolskaya Pravda», que ya era personaje desde F20 y `person_stats` no exige que sea persona, y «Мама de Надежда Кутепова», porque «Мама» no es cargo. Osetrov, Komarov y Serov siguen con citas parciales por transliteración.

### 4. Veredicto del revisor-handoff sobre F21b (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Perfil cargado en el camino del guion antes de los bloqueantes; `_perfil.json` canónico; sin perfil dice «(b) sin perfil: no evaluado» | OK | `fase1_5.py` `cargar_perfil` (llamada desde `_topic_v3`), `guion_v4.nota_b`, `run_guion_v4` guarda `nota_b` y la imprime. Orleans: `_perfil.json` y `_perfil_f20.json` idénticos (`cmp`). Ycuá: `_perfil.json` idéntico a `_perfil_f20.json`, con `_perfil_pre_f20.json` presente. Orleans no tenía perfil previo, así que no hay respaldo, y el reporte lo dice. Test `test_f21b_bloqueante_b_con_y_sin_perfil`. |
| 2 | `_official_says`: un rol de `roles_antagonista` vale en cualquier parte del dato; Orleans vuelve a 6,375 (F01) | OK | `research_v3.py` `_official_says`. El log de Orleans dice «oficial 6,375 (F01)» y lo corrí yo: sale igual. Test `test_f21b_rol_que_decide_en_cualquier_parte`. |
| 3a | Coma, « y » o « and » no es persona; `add_quote_authors` los salta | OK | `nombres.py` `es_persona`. En Kyshtym «Толстиков, Бочкарева» sale de los personajes (elegibles 9 → 8). Tests `test_f21b_criterios_de_forma` y `test_f21b_add_quote_authors_los_salta`. |
| 3b | Tratamiento o cargo + partícula es un cargo; el pedido cita «Warden de Hunt…» y «Director of…» | PARCIAL | La regla de forma está en `nombres.py`. «Warden de Hunt Correctional Center» sigue como persona elegible: lo muestra el log de Orleans y el reporte lo admite (§3 y «Lo que sigue raro»). «Director of Corrections» ya salía por otra regla. |
| 4 | Re-correr `recheck` «después» en HEAD, regenerar `RECHECK_f21.md` y anexar la sección F21b con el diff de cifras | OK | `recheck_f21.json` es idéntico a `recheck_despues.json` (`cmp`). `RECHECK_f21.md` solo cambió el título. `F21_REPORT.md` trae la sección F21b con tablas antes/después de las tres corridas. |
| 5 | Cero API y cero prompts | OK | El reporte dice US$ 0.00 (`cost_history` 486 antes y después). Esa cifra no la verifiqué. Mi `recheck.py revisor` corrió sin API. |

Lo que corrí yo:
- Tests: `pytest` de f21, f20, f7 y f11 dio 97 passed. No verifiqué la cifra «738 verdes + 5 previas» del reporte.
- Recheck: `python -I recheck.py revisor` dio un JSON idéntico a `recheck_f21b.json`. Borré `recheck_revisor.json` después.

Sobre tus tres preguntas:
- Punto 2: está bien explicado y no hacía falta parar. 6,375 volvió como oficial, que era la condición del pedido. El grupo trae solo 7,000 porque el perfil de Orleans no tiene `nombres_lugar` y `subject_re` da `None`. Esa causa es coherente con el código, pero no la reconstruí línea por línea. El reporte la declara y no toca el perfil.
- Punto 3: la excepción del sufijo (Jr., III…) es una reinterpretación razonable. Sin ella, «Leroy P. Gardner, III» y «Ronnie Lee Morgan, Jr.» dejaban de ser personas, cosa que el pedido no quería. Con «Warden de Hunt…» el pedido sí queda sin cumplir: lo nombra como ejemplo, el resultado en Orleans es el contrario y la causa es que «warden» no es tratamiento. Se hizo bien en dejarlo a decisión de Omar y en decirlo claro, pero no se cumplió. Por eso el veredicto es CON OBSERVACIONES y no CUMPLE.
- Punto 4: el método del worktree no es reproducible desde el repo, pero el resultado se sostiene. El `recheck` de `b24c505` da lo mismo que `recheck_despues.json`, y el reporte no afirma más que eso. Sin el worktree borrado no puedo verificar cómo se corrió, solo el resultado.

Fuera de alcance:
- `diag_234_cap4.py`, `gfx_profiles/lexico_propuestas.json` y `gfx_profiles/misterio.json` aparecen modificados contra `b24c505`. Ya figuraban modificados en el `git status` inicial y no tienen relación con F21b. Hay que excluirlos del commit.
- `recheck_f21.json` (copia de `despues`), `RECHECK_f21b.md` y `recheck_f21b.json` son entregables propios de F21b.
- Los cambios en `recheck.py` y `recheck_md.py` (perfil canónico, argumentos de la CLI) están dentro del punto 4.

Riesgos que el contrato no cubre:
- Orleans queda con «Warden de Hunt Correctional Center» como elegible, y con 7,000 como única variante porque falta `nombres_lugar` en su perfil. `data/` está ignorado, así que los perfiles `_perfil.json` no quedan en el commit.
- Kyshtym sigue con «periódico Komsomolskaya Pravda» y «Мама de Надежда Кутепова» como elegibles (reporte §3).
