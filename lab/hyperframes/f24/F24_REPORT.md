# F24_REPORT — fuentes que se acumulan, beats repartidos, dos temas nuevos de la semilla al guion (+ R3 con Sonnet)

CC · 2026-10-25 · base `03370af`, rama `f11-guion-v4`, sin merge. Handoff `HANDOFF_F24_fuentes_beats_dos_temas.md` (md5
`7ccd8f35c4cf2383abf1ac0b906b9a36`). A+B: commit `41b5618`; C y D: el commit siguiente, con este reporte. **Tanda US$ 8.2733 de 14.00**
(más D, US$ 0.9712 de crédito Claude, con su tope aparte de 5.00).

**En corto.** Pennhurst y Vajont llegaron de la semilla al guion y a la partición **sin tocar código de producción**.
- **Pennhurst:** 1,435 palabras ≈ 11.7 min, 0 bloqueantes, solo 2 citas.
- **Vajont:** 1,755 palabras ≈ 14.3 min. Le queda 1 bloqueante («1755 palabras: el tope es 1700»), porque la reparación no
  entró en el tope de US$ 1.20 del guion.
- **Las dos escaletas** quedaron con 1–3 beats en todos los caps desde la primera pasada.
- **Lo que se rompió fue mi runner de lab**, no la tubería: el freno de la ficha estaba mal dimensionado y el armado del
  `.md` de la narración tenía un error. Las dos cosas se arreglaron en `f24_corridas.py`, sin repetir llamadas.
- **D:** Sonnet 5.5 en R3 sobre los 8 documentos de Kyshtym da más ítems y más citas verificadas que Gemini (167/34 contra
  154/24) y descarta menos, a 1.6× el costo. Pero transcribe al español los nombres rusos y deja duplicados sin unir.

## 1. Parte A — fuentes que se acumulan

- **Código** (`research_v3.py`):
  - `fuentes.json` pasa a ser el **registro del tema** (`registro: "f24-1"`, una entrada por URL con `{url, titulo, tipo,
    idioma, anio, primera_vez, veces_vista, bajada_ok, chars, aporte {datos, citas, personajes}}` y la entrada de manifest
    para reusar). La salida de R1 de cada corrida queda en `fuentes_r1.json`.
  - `cargar_registro`: si no hay registro, o si `fuentes.json` es la salida de R1 de antes, lo arma con lo que hay en disco
    (`registro_desde_disco`: salidas de R1, manifests y pools `00_pool_v3*.json`; el aporte es el del último pool que
    extrajo ese documento).
  - `unir_fuentes`: candidatos = R1 + lo del registro que R1 no trajo, ordenados por aporte y después por la prioridad
    de R1.
  - `download_sources(previos=…)`: lo que el registro ya tiene bajado no se vuelve a pedir, y el cupo de cada idioma va
    primero a lo de más aporte.
  - `extract_document`: caché por texto (`r3_txt_<sha1>.json`). Un mismo trozo no se vuelve a extraer aunque el documento
    tenga otro id.
  - `actualizar_registro` suma la corrida.
- **Desvío (nombre):** el handoff dice `_docs/`; en este repo los documentos viven en `fuentes/` (txt + manifest). Lo
  apliqué ahí.
- **Desvío (A.3):** «reutiliza sus ítems del pool anterior» lo hice reusando la **respuesta cruda de R3** de ese mismo
  texto, re-validada contra el documento con su id nuevo. El resultado es el mismo: cero llamadas e ids nuevos. Lo que
  cambia es que los ítems pasan otra vez por `validate_doc_items`. Las cachés viejas de R3 (por id) no se migraron. El
  ahorro arranca con la primera corrida que usa este código.
- **Kyshtym (A.4):** el registro se armó desde disco sin llamar a nada (`f24_registro.py`, `registro_kyshtym.md`):
  - **36 fuentes**, **23 bajadas** (con su txt en `fuentes/`), **21 con aporte**. `veces_vista` = en cuántos archivos de
    disco figura.
  - El artículo de Osetrov (`cyberleninka …kyshtymskaya-radiatsionnaya-avariya-1957-goda…`, txt `cyberleninka_2018_1957.txt`)
    figura con aporte **27 datos / 6 citas / 5 personajes**, tomado de `00_pool_v3_f22.json`.
- **R1 unido en seco (D.1):** la R1 de F23 (10 fuentes) más el registro dan 36 candidatos. En el orden del cupo, el
  artículo de Osetrov queda **F04 → reusado, cupo ruso 4/10**. Con este código, F23 no lo habría perdido.
- **En vivo:** Vajont tenía las fuentes de F8 en disco. La R1 de F24 trajo 19 y el registro sumó **16 más** (19 en el
  registro). R2 bajó **19 documentos** (10 it, 7 en, 2 es), contra los 7 de F8. Pennhurst es tema nuevo: registro vacío y
  20 de R1, todas nuevas.
- No se agregó ningún chequeo.

## 2. Parte B — beats repartidos

- **Bloqueante de estructura** «entre 1 y 3 beats por cap»: `validate(max_por_cap=…)`, que solo la v2 pasa
  (`MAX_BEATS_POR_CAP = 3`). Entra en `BLOQUEANTES_V2`, así que pasan a ser 14. El camino viejo (v1) no cambia. La
  escaleta de Kyshtym de F23 (6 beats en el cap 6) **no pasaría**, y hay un test que lo cubre.
- **Prompt f24-1:** el bloque SISTEMA md5 **`006a195f0ce4be014df34d71644aedb1`** (antes `22cfd68b7cee4734e95bb3ee27bb96b2`,
  que queda como `SYSTEM_V2_F22_2`). El archivo es `PROMPT_ESCALETA_v2_1_f24.md`. Diff línea a línea, la única línea que
  cambia:

```diff
- - Repartir el material parejo para llenar siete caps. Un cap puede tener dos beats densos y otro uno solo.
+ - Meter seis beats en un cap y uno en los demás. Cada cap lleva entre uno y tres beats; el material que no cabe se deja afuera, no se apila.
```

  `PROMPT_VERSION_COLUMNA` también pasa a f24-1: la columna usa el mismo `SYSTEM_V2`.
- **Tabla de B.3** (Kyshtym, ficha v2.2 de F23; US$ 1.6568 de 2.00):

| | modelo | 1.ª pasada: beats por cap | caps fuera de 1–3 | bloqueantes 1.ª → 2.ª | final | ids · apoyos/beat | promesa | guion |
|---|---|---|---|---|---|---|---|---|
| F1 | Fable 5.1 high | cortada: `max_tokens` 16 000 (US$ 1.0549; 25 491 in) | — | — | — | — | — | no |
| S1 | Sol high | 1·1·2·2·2·3·3 | **0** | 11 → 1 (el humano es el id de una cita, Q17) → rechazada | — | — | «¿Cómo se borra del relato público una explosión que hizo temblar un edificio?» | no |
| S2 | Sol high | 1·1·2·1·3·3·3 | **0** | 19 → **0** | **1·1·2·2·2·3·3** | 44 · 2.14 | «¿Cómo se consigue ocultar una nube que ya salió de la fábrica?» | no |
| F2 | Fable 5.1 high | no corrió: freno (1.657 + peor caso 0.984 > 2.00) | | | | | | no |

- **Guiones de B.3: ninguno.** Después de las escaletas quedaban US$ 0.34, y el peor caso de un guion con Fable es 1.14.
  El handoff pedía «escaleta Sol ×2 y Fable ×2, guion con Fable de las cuatro» con US$ ≤ 2.00. Con los precios reales, eso
  no entra: solo las cuatro escaletas pedían ~US$ 2.7. Lo declaro como no hecho por el tope.
- **Decisión: escaleta con Sol en C.** Sol no dejó ningún cap fuera de 1–3 en ninguna primera pasada, y sus promesas son
  preguntas. Fable no devolvió una escaleta, y una pasada suya (≈ US$ 1.05) no entra en el tope de escaleta de C (0.40).
  El analista confirmó seguir con Sol.
- **Nota del analista (para el futuro):** F1 se cortó por `max_tokens` 16 000. El guion ya usa 32 000, y ese tiene que
  ser el tope de Fable en cualquier escaleta futura. F1 no se repitió.
- **Tests:** `test_module_f24.py` (10). Se adaptaron `test_module_f17`, `f22`, `f22d` y `f23` para que fijen la f22-2 con
  su versión. Suite amplia: **855 verdes + las 5 previas** (3 `01b_pauses`, 2 `m03_merge_timing`). Después del commit
  A+B no se tocó código de producción.

## 3. Parte C — Pennhurst y Vajont, de la semilla al guion

Camino normal: `run_seed` (perfil → R1 unido → R2 → R3 → R4/R5 → compuerta) → ficha v2.2 (Sol) → escaleta f24-1 sin
columna (Sol) → guion v5.3 (Fable) → `reparar` → `m01d_particion.particionar`. Runner: `f24_corridas.py`.
- **Desvío:** el topic se arma en memoria (título = el de la semilla). No corrieron los pasos 4a–4e de `topic_researcher`
  (meta: ángulo, hook, misterio), así que la escaleta los recibe como «-». Igual que en las corridas de laboratorio
  anteriores, `topics_db` no se toca.
- **Topic id:** el de Pennhurst es `4ac37187-pennhurst`. Vajont usa `f8s3-vajont`, la carpeta de F8, para que el
  registro use lo que ya había. Su perfil viejo pasó a `_perfil_pre_f24.json` y el pool a `00_pool_v3_pre_f24.json`.

| | Pennhurst (`4ac37187`) | Vajont (`f8s3-vajont`) |
|---|---|---|
| perfil | **1908–1987, prolongado**, [inglés, español] | **1963–1963, puntual**, [italiano, inglés, español] |
| R1 | 4 focos: 3 con grounding de Pro, 1 sin grounding (después de 3 reintentos y del recurso de Flash) · 20 fuentes | 4 focos: 1 Pro, 1 Flash, 2 sin grounding · 19 de R1 + 16 del registro |
| R2 | 10 OK (en 10) de 12 intentados | 19 OK (it 10, en 7, es 2) de 31 intentados |
| compuerta | **verde**: datos 236 · citas verificadas 37 · elegibles 25 · eventos con fecha 108 · personas 40 | **verde**: 245 · 45 · 23 · 78 · 52 |
| citas (R5) | 37 verificadas, 4 parciales, 0 sin verificar | 45, 12, 0 |
| ficha | 73 hechos, 20 citas, 11 escenas, 49 personas · 17 sacados | 69 hechos, 25 citas, 13 escenas, 66 personas · 3 sacados |
| humano · antagonista | **Terri Lee Halderman** · Estado de Pensilvania (institución) | **Micaela Coletti** · Società Adriatica di Elettricità, SADE (institución) |
| escaleta | 13 beats · 1.ª pasada 1·1·3·1·1·3·3 (0 caps fuera de 1–3; 14 bloqueantes de forma) → final **1·1·2·2·1·3·3** · 34 ids · 1.62 apoyos/beat | 13 beats · 1.ª pasada 1·1·3·3·1·2·2 (0 fuera; 12 bloqueantes) → final **1·1·3·3·1·2·2** · 40 ids · 2.08 |
| promesa | «¿Quién podía obligar a Pennhurst a cuidar de Terri cuando ella había perdido las palabras?» | «¿Cómo pudo el agua alcanzar la cama de una niña mientras la presa seguía en pie?» |
| guion | **1,435 palabras ≈ 11.7 min · 0 bloqueantes · 2 citas** · 43 duras de v3 (métrica) | **1,755 ≈ 14.3 min · 1 bloqueante** (tope de palabras 1700) · 7 citas · 37 duras de v3 |
| reparación | no hizo falta (0 bloqueantes antes) | **no corrió**: freno (0.914 + peor caso 0.444 > 1.20) → el bloqueante queda |
| partición | cap 7 acortado (567 → 211 caracteres); cap 2 corto (aviso) | último párrafo del cap 4 al cap 5; cap 7 acortado (813 → 263) |

**Por cap** (intent desde los beats · palabras del guion → después de la partición · personas con nombre · citas · fechas
literales: la métrica en dígitos da 0 en todos los caps de los dos temas, porque Fable escribe las fechas en letras; acá
van las de día + mes contadas en letras):

| cap | Pennhurst | Vajont |
|---|---|---|
| 1 | hook · 122 → 122 · Terri Lee Halderman, Legislatura de Pensilvania · 0 · 1 («Ocho de enero de 1975») | hook · 106 · Micaela Coletti · 0 · 1 («nueve de octubre») |
| 2 | setup · 81 · Halderman · 0 · 0 | setup · 134 · Fundación Vajont · 0 · 0 |
| 3 | rising_tension · 186 · Bill Baldini, David Ferleger, Halderman, Legislatura · 0 · 1 | rising_tension · 399 · Edoardo Semenza, Giorgio Dal Piaz, Tina Merlin, L'Unità, Fundación Vajont · 0 · 1 |
| 4 | rising_tension · 200 · Theresa Sobetsky · 0 · 0 | rising_tension · 437 → 337 · Alberico Biadene, Mario Pancini, Lab. Univ. de Padua, Fundación · 2 · 3 |
| 5 | shock · 158 · Linda Taub, Raymond J. Broderick, Halderman · 1 · 0 | shock · 195 → 295 · Gianfranco Trevisano · 1 · 1 |
| 6 | rising_tension · 331 · Raymond J. Broderick, Hearing Master, Legislatura · 0 · 2 | resolution · 179 · Aniello Coppola, Giorgio Bocca · 3 · 0 |
| 7 | outro · 356 → 300 · Halderman, Justice Stevens, Parent-Staff Association · 1 · 3 | outro · 302 → 204 · Biadene, Sensidoni, Bocca, Pancini, Coletti, Fundación · 1 · 2 |

**Qué se rompió y dónde:**
- **Tubería: nada se cayó.** Lo que quedó flojo:
  - Vajont termina con 1 bloqueante (1,755 palabras contra un tope de 1,700). La reparación no entró en el tope del guion
    (la escritura con Fable costó 0.914 y el editor tenía un peor caso de 0.444).
  - Pennhurst usa 2 citas teniendo 37 verificadas en el pool.
  - Vajont dice «nueve de octubre» en 4 caps (1, 4, 5, 7). Es la fecha sin año, así que la regla de «la fecha completa
    una vez» no la cuenta.
  - Los dos ganchos están libres de las frases de tráiler de la lista, pero cada uno tiene una oración que anticipa:
    «Lo que esta casa hace con los que no pueden defenderse se ve en ese cuerpo dormido…» y «…cómo llegó es lo que hay
    que entender».
  - El contador de personas cuenta instituciones como personas («Legislatura de Pensilvania», «Hearing Master»,
    «Fundación Vajont»).
- **Mi runner (lab, no producción):**
  - **(1)** La primera vuelta de la ficha paró en los dos temas antes de llamar: el freno con 50 000 tokens de salida
    daba 0.604 y 0.623, contra un tope de 0.60. Bajé la salida acotada a 40 000 (Kyshtym había usado 23 340) y corrió;
    las fichas usaron menos de 0.44.
  - **(2)** El `.md` de la narración fallaba (`KeyError: 'costo'` en la función reusada de F22b). Lo rehíce sin API con
    `_narracion`. El guion ya estaba guardado y no se repitió ninguna llamada.

Costo por paso (US$; topes: research 3.50, ficha 0.60, escaleta 0.40, guion + reparación 1.20, partición 0.20 [este tope
lo puse yo; el handoff no lo daba]):

| tema | research | ficha | escaleta | guion | reparación | partición | total |
|---|---|---|---|---|---|---|---|
| Pennhurst | 1.3712 (1,235 s) | 0.4018 | 0.3090 | 1.0790 | 0.0000 | 0.0099 | **3.1709** |
| Vajont | 1.7913 (1,895 s) | 0.4374 | 0.2794 | 0.9138 | 0.0000 (no entró) | 0.0237 | **3.4456** |
| B.3 (Kyshtym) | | | 1.6568 | 0 | | | **1.6568** |
| **tanda** | | | | | | | **8.2733** |

Prompts con md5 (en `<tema>/prompt_*.txt`): ficha `070b75df…` (sistema) · Pennhurst usuario `eb0a41b5…`, Vajont
`4ecb5b99…`; escaleta `006a195f…` · `1c450be5…` / `8ad8a238…`; guion `8ca9aa49…` · `bb72ddd1…` / `770deff1…`.

## 4. La tabla de la fase 1

| paso | Pennhurst | Vajont |
|---|---|---|
| perfil | corrió solo | corrió solo (el perfil de F8 quedó como respaldo) |
| R1 | corrió solo (reintentos internos de grounding; 1 foco sin grounding) | corrió solo (reintentos internos; 2 focos sin grounding; el registro sumó 16) |
| R2 | corrió solo (10 de 12) | corrió solo (19 de 31) |
| R3 | corrió solo (10 documentos, 0 extracciones fallidas) | corrió solo (19 documentos, 0 fallidas) |
| R4 | corrió solo | corrió solo |
| R5 | corrió solo | corrió solo |
| compuerta | verde | verde |
| ficha | **necesitó reintento**, por mi freno (lab), no por la tubería: la 1.ª vuelta paró antes de llamar | igual |
| escaleta | corrió solo (la regeneración de siempre: 14 → 0) | corrió solo (12 → 0) |
| guion | corrió solo (0 bloqueantes) | **paró con 1 bloqueante**: la reparación no entró en el tope de 1.20 |
| partición | corrió solo | corrió solo |

Ningún paso falló por red o timeout, así que no hubo que usar el reintento permitido.

## 5. Parte D — R3 con claude-sonnet-5-5 sobre Kyshtym (pedido de Omar)

`d_r3_sonnet/d_r3_sonnet.py`:
- Los mismos 8 documentos del pool de F23 (txt ya bajados en `fuentes/`, sin buscar ni bajar nada), el mismo seed y
  perfil, `build_extraction_prompt`, `R3_SYSTEM` y `R3_SCHEMA`. Solo cambia `call`: Sonnet 5.5, effort high (lo elegí yo;
  el pedido no lo fijaba), `max_tokens` 32 000.
- Caché propia. Después corre el mismo `build_pool` (R4 + R5, deterministas) → `00_pool_v3_sonnet.json`.
- No toqué código de producción.

| | Gemini 2.5 Pro (F23) | **Sonnet 5.5 (F24 D)** |
|---|---|---|
| datos · cronología · lugares · citas · personajes | 154 · 56 · 14 · 24 · 23 | **167 · 59 · 12 · 34 · 24** |
| personajes que son persona (`nombres.es_persona`) | 20 | 21 |
| elegibles humano | 16 | 17 |
| citas verificadas · parciales | 21 · 3 | **30 · 4** |
| descartados | 67 (52 «nombre del lugar no está», 4 «cita_literal no está», 2 por año) | **44** (31 lugar, 0 cita_literal, 1 por año) |
| compuerta | verde (154/21/16/56/23) | verde (167/30/17/59/24) |
| costo R3 | US$ 0.5923 (8 llamadas) | **US$ 0.9712** (8 llamadas; 87 701 in / 79 582 out) |
| tiempo R3 | no medido aparte (el research entero de F23 tardó 1,301 s) | 434 s (17–118 s por documento) |

- **Nombres:** Sonnet escribe los nombres rusos transcriptos al español («Anatoli Vasílievich Dubrovski», «Mijaíl
  Kuléshov», «Serguéi Mitrojin»), no en la forma inglesa que usan el resto del pool y las fichas.
- **Duplicados sin unir:** deja al mismo personaje dos veces («E.P. Slavsky» y «Efim Slavski»; «M. A. Demyanovich» y
  «Mijaíl Demiánovich»).
- **Personas nuevas:** suma a Ralph Nader, a Mijalski y a V. V. Ustiuzhanin.
- **Lo que deja afuera:** el diario «Chelyabinsky Rabochy» como persona (bien), y además a Timur y a Vyatkin.
- **Fecha del caso:** sigue descartando por año el reconocimiento de 1989.
- **No miré la calidad ítem por ítem.** La tabla es de conteos.

## 6. Archivos

`lab/hyperframes/f24/`:
- **Reporte y comparación:** `F24_REPORT.md`, `compara_f24.html`, `resumen_f24.json`, `TABLA_B3.md`,
  `modelo_escaleta_f24.json`.
- **Prompt y registro:** `PROMPT_ESCALETA_v2_1_f24.md`, `registro_kyshtym.{md,json}`.
- **Scripts:** `f24_registro.py`, `f24_corridas.py`, `f24_compara.py`.
- **Costos y logs:** `costos_f24.json`, logs `run_*.log`.
- **`b3/`:** escaletas, crudos y prompts de F1/S1/S2, `tabla_b3.json`.
- **`pennhurst/` y `vajont/`:** `PERFIL.md`, `POOL_GATE.md`, `FICHA.md`, `ESCALETA.md`, `NARRACION_<tema>_f24.md`,
  `prompt_{ficha,escaleta,guion}.txt` con md5, `costos.json`, `estado.json`, `research.json`, `registro_fuentes.json`,
  `fuentes_r1.json`, `manifest.json`, `ficha.json`, `ficha_crudo.json`, `escaleta*.json`, `guion.json`,
  `particion.json`, logs.
- **`d_r3_sonnet/`:** `d_r3_sonnet.py`, `00_pool_v3_sonnet.json`, `comparacion.json`, `_r3_cache/`, logs.

`_transfer_tmp/` borrado. En `_steps/` (no versionado): las carpetas de los dos temas con perfil, registro, fuentes, pool,
ficha, escaleta y partición; en Kyshtym, `fuentes.json` = el registro (la R1 de F23 quedó en `fuentes_r1.json`).

## 7. Veredicto del revisor-handoff

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | A: registro por tema `fuentes.json` con los campos pedidos (unión de corridas) | OK | `git show 41b5618`: research_v3.py (+220); `data/scripts/_steps/*/fuentes.json` existen para Kyshtym, Pennhurst y Vajont |
| 2 | A: R1 unido con prioridad por aporte; R2 no re-baja; R3 sin re-extraer | OK, con desvío | Código en el diff 03370af..41b5618; no ejecuté el código. R3 reusa la respuesta cruda por sha1 del texto y la re-valida, no los ítems del pool (declarado en reporte §1). El handoff decía `_docs/`; el repo usa `fuentes/` (declarado) |
| 3 | A.4: Kyshtym armado de disco, Osetrov en el cupo | OK | `registro_kyshtym.md:53,87`: F04 «reusada», cupo ru 4/10; reporte: 36 fuentes, 23 bajadas, 21 con aporte |
| 4 | B.1: bloqueante «1–3 beats por cap», 14 bloqueantes | OK | `m01a_escaleta.py`: `MAX_BEATS_POR_CAP = 3`, `max_por_cap` en validate; `test_module_f24.py` |
| 5 | B.2: prompt con una sola línea cambiada y md5 | OK | El diff muestra la línea de `<errores>` exacta del handoff; el bloque anterior queda como `SYSTEM_V2_F22_2`. El reporte da md5 `006a195f…`; no recalculé el md5 del bloque |
| 6 | B.3: cuatro escaletas (Sol×2, Fable×2) y guion con Fable de las cuatro, tope ≤ 2.00 | PARCIAL (declarado) | F1 cortada por max_tokens (1.0549), S1 rechazada, S2 OK, F2 no corrió por freno; ningún guion. `costos_f24.json`: 1.0549+0.3144+0.2875 = 1.6568 |
| 7 | B.3: decisión de modelo, con la tabla en el reporte | OK | Sol, con criterio coherente con el handoff (0 caps fuera de 1–3 en la primera pasada). «El analista confirmó seguir con Sol» no se puede verificar en el repo |
| 8 | Nota de Omar sobre max_tokens 32000 para Fable en futuras escaletas | OK | Reporte §2 |
| 9 | C: sin tocar código de producción | OK | `git diff 41b5618 -- researcher_steps script_engine` vacío; fuera de lab/ solo difieren `diag_234_cap4.py` y `gfx_profiles/*`, que no son de esta tarea |
| 10 | C: números de Pennhurst y Vajont coinciden con los archivos | OK | `guion.json`: 1435 palabras, 11.7 min, 2 citas, 0 bloqueantes (Pennhurst); 1755, 14.3, 7 citas, 1 bloqueante «tope 1700» (Vajont). Compuertas en `research.json`: 236/37/25/108/40 y 245/45/23/78/52. Palabras por cap iguales a la tabla |
| 11 | C: costos por paso y topes | OK | Pennhurst 3.1709 y Vajont 3.4456 suman bien por paso; B.3 1.6568; tanda 8.2733 ≤ 14.00. Cada paso respeta su tope (guion 1.079 y 0.9138 ≤ 1.20) |
| 12 | C: tabla de la fase 1 | OK | Reporte §4 coincide con `estado.json` (todo «solo»). El estado «necesitó reintento» de la ficha por el freno del runner está en el reporte, pero `estado.json` dice «solo» |
| 13 | D: R3 con Sonnet 5.5 sobre los txt ya bajados, comparación pool contra pool | OK | `d_r3_sonnet/comparacion.json`: 167/59/12/34/24; es_persona 21 contra 20; citas 30+4 contra 21+3; descartados 44 contra 67; US$ 0.9712 contra 0.5923 (1.64×, el «1.6×» del reporte es correcto); 433.5 s; 8 documentos; tope 5.00 respetado |
| 14 | `_transfer_tmp/` borrado | OK | `ls` falla: no existe |
| 15 | Suite | OK | 855 passed, 5 failed (3 `01b_pauses`, 2 `m03_merge_timing`), como se esperaba |
| 16 | Veredicto del revisor pegado en §7 | NO VERIFICABLE | §7 dice REVISOR_PENDIENTE; se completa con este informe |
| 17 | `compara_f24.html`, `F24_REPORT.md`, `PERFIL.md`, `FICHA.md`, `ESCALETA.md`, `NARRACION_*_f24.md`, `costos.json`, prompts por tema | OK | Los archivos existen en `pennhurst/` y `vajont/` |

Observaciones:
- **ESTADO_SESION desactualizado.** `lab/ESTADO_SESION.md` sigue en «EN CURSO… PARADA corta antes de C» (línea 15). El handoff §E y el CLAUDE.md piden actualizarlo en cada hito, y C y D ya terminaron.
- **Vajont con 1 bloqueante.** El reporte lo declara. El mensaje de `guion.json` dice «paso 0.914 + peor caso 0.444 > 1.20», así que el freno por tope del guion es real. Es un desvío de calidad, no de contrato.
- **Alcance de C.** El «sin tocar código de producción» se cumple. Pero `f24_corridas.py` (lab, modificado) se ajustó durante C: el freno de la ficha bajó de 50000 a 40000 tokens de salida y se arregló el armado del `.md`. Está declarado y no es producción.
- **Tablas de B.3 y D.** B.3 no hizo los guiones de las cuatro escaletas. D no mide el tiempo de Gemini (declarado «no medido»).
- **Reporte.** El encabezado dice «C y D: el commit de este reporte», pero C y D están sin commitear.

Fuera de alcance: `diag_234_cap4.py`, `gfx_profiles/lexico_propuestas.json`, `gfx_profiles/misterio.json` (modificados antes, ajenos a F24). No vi `.env`, `config.py` ni `lab/_gpt_probe_analista/` entre los archivos modificados, pero este último aparece sin versionar, así que no debe entrar en el commit.

Riesgos que el contrato no cubre: (1) la calidad de los guiones, las ocho personas que son instituciones y la fecha repetida en Vajont no tienen revisión humana todavía. (2) La comparación de D es de conteos, no de calidad ítem por ítem (declarado). (3) Hay logs `run_*.log` y `error_guion.txt` sin versionar que pueden terminar en el commit.

*(Después del veredicto, CC: actualizó `lab/ESTADO_SESION.md` (F24 HECHO, PARADA); puso en `estado.json` de los dos temas la ficha como «reintento» (el freno del runner) y, en Vajont, el guion como «paró» (1 bloqueante), igual que la tabla §4; y cambió el encabezado a «C y D: el commit siguiente». Los logs y `error_guion.txt` se versionan a propósito: son el registro del error del runner.)*
