# RECHECK F21 — antes (código de `08d63d9`) | después (F21), sin API

Mismos archivos de disco en las dos corridas (`recheck.py`): perfil → `set_vocabulario`; sobre una copia del pool, `add_quote_authors`, `canonical_names`, `presence_v3`, `person_stats`, cifras canónicas, `verify_pool` (con los txt ya bajados) y `person_stats` → compuerta; ficha (`ficha_caso.check`), columna (`m01a_columna.chequeo`), escaleta (`m01a_escaleta.bloqueantes`) y guion (`guion_v4.bloqueantes` + `metricas`). Kyshtym: pool de F20; ficha, columna y escaleta (crudo del pase 2) de F18 contra el pool de F18; **Kyshtym no tiene guion** (F18 paró en la escaleta y F19 en el research). Orleans no tiene columna. Costo: US$ 0.00 (`data/cost_history.json` con 486 registros antes y después).

## Orleans (`ba6c3cac-f7r3`)

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

## Ycuá (`f8s1-ycua-bolanos`)

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

## Kyshtym (`f18-kyshtym-mayak`)

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
