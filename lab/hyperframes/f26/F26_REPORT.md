# F26_REPORT — nocturno: escaleta f26-1, primer video (Vajont), workers en el research, hooks, ficha de Opus con forma

CC · 2026-10-25 · base `c80e601`, rama `f11-guion-v4`, sin merge, nada publicado, nada borrado. Handoff
`lab/hyperframes/f26/HANDOFF_F26_nocturno.md`. Sin paradas intermedias: las decisiones que tomé están marcadas
**(decisión)**.

**Gasto total US$ 10.80:**
- Claude US$ 7.97: A 5.66 de 8, E 2.32 de 4, B 0 de 2.
- Gemini US$ 2.42 (B, de 5).
- ElevenLabs US$ 0.41 (B).
- Imágenes: 0 de 100.

**En corto.**

| parte | estado | commit |
|---|---|---|
| A | **HECHA.** Las dos escaletas f26-1 pasan y ninguna promesa adelanta. La reparación (e) corre sola, pero borra la oración (no deja el rol). En gkE2, además, corrió el editor m01c y se llevó la promesa del gancho. | `16900bd` |
| B | **PARADA en m03 (falló dos veces).** Hechos: topic, partición, voz (16.3 min) y música. El cap 1 (el gancho) no sale de m03: Gemini Flash devuelve una respuesta sin texto y `gemini_helpers` hace `None.strip()`. No hay imágenes, render ni video. | `e24c57b` |
| C | **HECHA.** R2/R3 en hilos dan el mismo resultado que en fila. R3 con latencia simulada: 16.7 s → 2.8 s. Suite: 877 verdes + las 5 previas. | `16def01` |
| D | **HECHA.** 4 hooks, prueba 22/22. El guard frenó un `git add` real de esta sesión: era un falso positivo y lo corregí. | `40a434d` |
| E | **HECHA.** Opus con los nombres de campo en el pedido: 16 y 17 problemas, contra 58 y 71 sin ellos (Sol: 18). Las cifras vuelven (29 y 46). Cuesta 3–4 veces lo que Sol. | `c343954` |

Orden: A → B → C → D → E, como pide el handoff, pero mientras corrían las llamadas largas de A y B fui escribiendo el
código de C y D (0 API) **(decisión)**. Por eso los commits salieron en el orden en que terminó cada parte: A, C, D, B, E.

---

## A. Escaleta f25-1 → f26-1 y re-corrida de Kyshtym — HECHA

### A.1 Prompt
- **Archivo:** `lab/hyperframes/f26/PROMPT_ESCALETA_f26_1.md` (md5 `1aa22901…`). El bloque SISTEMA (md5
  **`2e67791cedbfa7492f8b6de1268b7b30`**) es igual a `m01a_escaleta.SYSTEM_V2`, con test byte a byte.
- **La f25-1** queda como `SYSTEM_V2_F25_1` (`9325ad38…`), con `PROMPT_VERSION_V2_F25_1`.
- **Versiones:** `PROMPT_VERSION_V2` y `PROMPT_VERSION_COLUMNA` pasan a `f26-1`.
- **Cambio:** tres agregados literales al final de sus líneas. Nada más cambia y no hay chequeos nuevos.
  `test_module_f26.py` verifica que la diferencia son exactamente esas tres líneas.
  - `<oficio>` §2, después de la promesa: «Probala así: si la oración se puede leer como un resumen de lo que viene
    («nadie lo sabrá durante años», «terminará en un juicio»), no es una promesa; es un adelanto. Volvé a escribirla con
    lo que se ve o lo que no cierra.»
  - `<oficio>` §10: «Un id que va a `a_pantalla` no va en ningún beat.»
  - `<que_es_una_escaleta>`, al final del párrafo del antagonista: «Su nombre va exactamente como está escrito en la
    ficha, sin siglas ni paréntesis agregados.»
- **Tests adaptados:** `test_module_f25c` (la f25-1 con su versión) y `test_module_f17` (columna f26-1).

### A.2 Re-corrida (Kyshtym, ficha fS2 de F25a, pool F23)
`f26a_corridas.py`:
- Fable 5.1 en las dos etapas: escaleta con effort medium; guion v5.4 y reparación con effort high.
- Las 2 escaletas a la vez, y después los 2 guiones a la vez.
- Freno con lock antes de cada llamada y respuesta cruda guardada en `a/<tag>/respuesta_*.json`.
- 7 llamadas, todas `end_turn`, ninguna cortada. **US$ 5.657 de 8**, pared 337 s + 353 s.

| | 1.ª pasada | final (beats por cap) | ids · apoyos/beat | humano · antagonista | a_pantalla repetido en beats | US$ |
|---|---|---|---|---|---|---|
| kE1 | 1 bloqueante: «beat 2: dato_central «L09» no existe en el pool (o no es D/T/Q)» → pasa en la 2.ª | 1·2·2·2·1·3·3 | 66 · 3.71 | Dubrovsky · persona Yefim Slavsky | ninguno | 1.8119 |
| kE2 | **0: pasa en la 1.ª** | 1·2·3·2·2·2·2 | 71 · 4.07 | Dubrovsky · institución «Gobierno de la URSS» | ninguno | 0.8570 |

En F25c, kE1 y vE1 habían caído por `a_pantalla` repetido y por antagonistas con paréntesis. Esta vez no se repitió
ninguno de los dos errores: los antagonistas van sin siglas ni paréntesis.

**Promesas, textuales:**

| | promesa de la escaleta | ¿adelanta? |
|---|---|---|
| kE1 | «La película sigue proyectándose mientras el edificio tiembla, y nadie en la sala tiene una palabra para lo que acaba de oír.» | No: deja una imagen sin cerrar. |
| kE2 | «Un electricista siente temblar el cine y sale a la calle; lo que cayó del cielo esa tarde no tiene nombre, y la ciudad donde cayó no está en ningún mapa.» | No: «no tiene nombre» y «no está en ningún mapa» son cosas que no cierran. No cuenta lo que pasa después. |

Con f25-1, la de Kyshtym era «…y durante diecinueve años nadie en el mundo va a saber por qué», que sí adelantaba. **La
lectura de «adelanta» es mía; n = 2.**

**Guiones (v5.4, Fable high) + reparación de producción:**

| | escaleta | crudo: palabras · bloqueantes | final: largo · bloqueantes | citas | palabras por cap | 2.ª frase del gancho = promesa | US$ |
|---|---|---|---|---|---|---|---|
| gkE1 | kE1 | 2,168 · 0 | 2,168 ≈ 17.6 min · **0** | 11 | 142 · 348 · 299 · 254 · 145 · 498 · 474 | sí, literal | 1.2862 |
| gkE2 | kE2 | 1,811 · **1** (e) «Q20 está SIN VERIFICAR y va con el nombre de Mikhail Kuleshov» | 1,713 ≈ 13.9 min · **0** | 11 | 104 · 237 · 389 · 259 · 252 · 246 · 215 | **no: el editor m01c la sacó** | 1.7019 |

### A.3 Reparación (e) automática — sí corre sola, con dos observaciones
- **Cómo se llamó:** el runner llama `guion_v4.reparar(topic, esc, parrafos, call=…, ficha=…)` exactamente como lo
  llama `fase1_5.run_guion_v4`. No hay código nuevo.
- **gkE1:** el crudo vino con 0 bloqueantes, así que la reparación no llamó a nada.
- **gkE2:** el bloqueante (e) entró en la edición por oración (beat 10) y la edición se aceptó (US$ 0.03).
- **Observación 1. No dejó el rol: borró la oración entera.**
  - Oración borrada: «Kuleshov recuerda instalaciones inundadas, tablones para caminar a oscuras, champú y productos
    químicos que no limpiaban nada.»
  - Lo que esperaba el handoff: «quita el nombre, deja el rol».
  - Por qué: el pedido de edición de producción dice «Sacá esas frases o corregilas», y el modelo eligió sacarla.
- **Observación 2. Como el crudo tenía un bloqueante, también corrió el editor m01c (regla de F11c).**
  - Tocó 10 párrafos y dejó el guion en −98 palabras (1,811 → 1,713).
  - En el gancho (beat 1) **sacó la promesa**: la 2.ª frase del cap 1 pasó a ser la cita del cine.
  - El editor no sabe que esa oración viene literal de la escaleta (v5.4). No toqué nada: lo anoto para el analista.

Archivos: `ESCALETA_kE1.md`, `ESCALETA_kE2.md`, `NARRACION_gkE1.md`, `NARRACION_gkE2.md` (final reparado); en
`a/<tag>/`: `resultado.json` (con `parrafos_crudo`, `bloqueantes_crudo` y `reparacion.pasos`), los prompts con md5 y
las respuestas crudas.

---

## B. Producción del video de Vajont — PARADA en m03 (el paso falló dos veces)

`b/f26b_produccion.py`, por etapas: preparar → partición → guion (normalizer → audio → m07 → m03 → paso0 → assemble)
→ imágenes (fase2a) → render (fase2b). Log en `b/produccion.log` y costos en `b/costos_f26b.json`.

**Lo que se hizo:**

1. **Preparar.**
   - `f8s3-vajont` no estaba en `data/topics_db.json` (solo en `selected_seeds.json`). Lo agregué **(decisión)**,
     siguiendo el patrón de `f5/produccion_orleans_v2.py`.
   - Corrí 4a–4e (`topic_researcher.extract_*` sobre `research_v3.pool_to_blocks` del pool de F24, Gemini Flash
     US$ 0.07) para tener `era_visual_canon`, `documented_people/props` y `central_subject`, que m03 y la foto madre
     necesitan.
   - Título del handoff, «Vajont: la montaña que caminaba». El que proponía 4c («Vajont La Ola De 250 Metros…») queda
     en `titulo_4c`.
   - `status` validated, `guion_version` 4.
   - Respaldo en `data/topics_db.pre_f26.json`.
   - Los pasos viejos de `_steps/f8s3-vajont/` (escaleta f24-1, skeleton, narración) se movieron a `_pre_f26/`.
     `01a_escaleta.json` = vE2 y `01b_guionista_v4.json` = gvE2.
2. **Partición.**
   - `m01d_particion.particionar(..., shorten=None)` **(decisión: sin el recorte del editor)**. Con
     `md.editor_shorten()`, el último párrafo del cap 7 perdía unos 1,160 caracteres, y el handoff dice «no reescribir
     nada».
   - Resultado: 7 caps con intents desde la escaleta: hook · rising_tension ×4 · shock · outro.
   - **No se movió ningún párrafo** (palabras por cap iguales al guion: 253 · 327 · 281 · 282 · 391 · 406 · 411).
   - Quedan 4 avisos de largo («cap 1: 1325 caracteres > 986…», también en los caps 5, 6 y 7). Son avisos, no recortes.
3. **Voz.**
   - ElevenLabs v4, «MS Narrador», `narration_tts` con las etiquetas del intent de cada cap (stability 0.45–0.6 según el
     intent). US$ 0.414.
   - **980.8 s = 16.3 min**, no 19.1: la voz va a ~2.4 palabras/s, no a 2.05.
   - Duración por cap: 94.8 · 130.0 · 126.4 · 118.7 · 166.0 · 164.7 · 180.2 s.
   - La pérdida del Forced Alignment fue 0.58–0.62 en los 7 caps, igual que en la producción de Orleans (0.53–0.65).
4. **Música.**
   - `music_map` fijo a los `audio_library/<intent>_curated` **(decisión)**. El handoff dice «sin música nueva», y el
     matcher de m07 puede decidir generar.
   - Lo hice reemplazando `generate_music_map` dentro del proceso del runner, sin tocar m07.
5. **Imágenes: el plan.**
   - Con la regla de siempre (7 s por imagen y el tope de 90 que no se aplica a los caps Veo) daban ~110.
   - Subí `m03_visual.SECONDS_PER_IMAGE_TARGET` a **10.75 s** en el proceso. Es un parámetro, no lógica.
   - Plan: **92 imágenes** (9 · 13 · 13 · 11 · 15 · 16 · 15) repartidas por la duración real. Dejé margen bajo el tope
     de 100 para las re-hechuras del guardia de visión.

**Dónde se trabó:**
- **m03 falló dos veces con `AttributeError: 'NoneType' object has no attribute 'strip'`.**
  - 1.er intento: por `process_topic`, que se traga el traceback.
  - 2.º intento: llamado directo para guardar el traceback (`b/m03_traceback.txt`).
- **La cadena del error:**
  - `_fluidify_one` → `_fluidify_with_leakage_guard` → `_fluidify_item` → `gemini_helpers.call_flash_json` →
    `_parse_with_retry` → `_try_json_parse`.
  - Ahí, `raw_text.strip()` con `raw_text = None`: Flash devolvió una respuesta sin texto.
- **Siempre falla el mismo cap.** En los dos intentos validaron los caps 2–7 y **no terminó el cap 1** (el gancho: la
  niña en la cama que «corre», marcada por las reglas F8 como «menor en daño»). Mi lectura es que Flash bloquea por
  seguridad el re-tejido de esa imagen. **No está confirmado:** el helper no guarda el `finish_reason`.
- **Regla del handoff:** «si un paso falla dos veces, PARADA de B». No hubo tercer intento ni arreglo de código.
  `gemini_helpers` no está en la lista de lo que podía tocar, y el cambio sería de lógica.
- **Arreglo posible (no ejecutado):** que `_try_json_parse` trate `None` como un fallo de parseo (reintento y después
  `_JsonParseError`), para que el guardia de leakage y el backstop de m03 decidan sobre esa imagen sin tirar el video.
  Otra opción: una nota de gancho sin la niña en esa imagen.
- **No corrió:** paso0 (foto madre), assemble, fase2a, fase2b, gfx, QA Studio. **No hay `video_vajont_f26.mp4`.**
  El gfx no se llegó a probar con 19 minutos.

**Costo de B, por paso:**

| paso | servicio | US$ |
|---|---|---|
| 4a–4e | Gemini 2.5 Flash | 0.0683 |
| partición (títulos) | Gemini 2.5 Flash | 0.0056 |
| normalizer_gate + voz | Gemini Flash 0.0183 · ElevenLabs 0.414 | 0.4323 |
| m03 intento 1 | Gemini Flash 0.3629 · Pro 0.815 | 1.1779 |
| m03 intento 2 | Gemini Flash 0.2559 · Pro 0.8892 | 1.1451 |
| **total B** | Gemini 2.4152 de 5 · ElevenLabs 0.414 · Claude 0 de 2 · imágenes 0 de 100 | **2.8292** |

Una nota sobre esta tabla: el `cost_tracker` acumula todo lo del proceso. La primera versión del runner anotaba el
audio dos veces dentro de m03. Lo corregí a mano en el JSON, que lo dice en su campo `nota`, y el runner ahora anota cada
etapa por diferencia.

**Estado en disco para retomar:**
- `output/audio/f8s3-vajont/`: 7 mp3, timestamps, `sync_map.json` y `music_map.json`.
- `_steps/f8s3-vajont/`: skeleton, narración, narración normalizada y 01–05 de 4a–4e.
- Topic en `topics_db`.
- Para retomar, `--etapa guion` reusa la voz y la música (no las vuelve a pagar) y vuelve a correr solo m03.

---

## C. Workers en el research — HECHA (0 API)

- **`research_v3.py`:**
  - `WORKERS = 8`.
  - `download_sources(..., workers=)`:
    - `_prebajar` baja en hilos por oleadas. En cada idioma, las siguientes fuentes «bajar» hasta el cupo que falta.
    - Un pedido a la vez por sitio (`_por_sitio`).
    - Después, el recorrido en fila de siempre decide con lo ya bajado. El manifest y el log salen como en fila.
  - `extract_documents(..., workers=, tope_usd=)` (R3):
    - Un documento por hilo; los de texto idéntico, en el mismo hilo (la caché por texto de F24 sigue sirviendo).
    - Log y `_extraccion_fallida` se juntan en el orden de los documentos.
    - Tope opcional con lock: antes de cada documento reserva su peor caso contra lo que ya anotó el `cost_tracker`.
  - `run_seed(..., workers=)`. R4/R5 sin cambios.
- **`cost_tracker.py`:** `_lock` (RLock) en `_add_entry`, así dos hilos no se pisan el append ni el total.
- **`topic_researcher.py`:** `--workers N`.
- **`fase1_5.py`:**
  - `--temas a,b,c` lanza un proceso por tema (`temas_cmds` / `run_temas`), con log en
    `_steps/<tema>/fase1_5_temas.log`.
  - **(decisión)** `--temas` implica `--batch`: los gates interactivos no se pueden contestar desde varios procesos.
- **Tests sin red (`test_module_f26c.py`, 6):**
  - R2 1 vs 8 hilos da el mismo manifest y el mismo log, con un mock de red. Los pedidos son los mismos (no pasa el
    cupo).
  - R3 1 vs 8 da **el mismo pool**. El mock de R3 devuelve las respuestas guardadas en la caché de Kyshtym, y después
    corre `build_pool`.
  - El tope con lock no lee lo que no entra.
  - `cost_tracker`: 8 hilos × 500 entradas.
  - `--temas`.
  - **Dorado v3 verde. Suite amplia: 877 verdes + las 5 previas** (3 `01b_pauses`, 2 `m03_merge_timing`).
- **Prueba sin gasto (`c/f26c_prueba.py`, `c/prueba_workers.json`):** se hizo sobre una copia en el scratchpad,
  con el registro de fuentes de F24 (36 candidatos).

| | 1 worker | 8 workers |
|---|---|---|
| R2 (20 OK, 12 no intentadas, 3 sin texto, 1 error; 4 pedidos de red, el resto reusado) | 14.3 s | 12.4 s |
| R3 con caché (8 documentos del pool F23, 288 ítems, cero llamadas) | 1.12 s | 0.79 s |
| R3 con latencia simulada (8 trozos × 2 s, mismo resultado que la caché) | 16.7 s | **2.8 s** |

- **R2 casi no gana, porque casi todo estaba bajado.** El manifest de 1 y de 8 difiere en un solo documento (F25): la
  Wayback contestó 429 en una corrida y 200 en la otra. Es la red, no el paralelo. El estado final es el mismo (error,
  texto de 0 caracteres).
- **Desvío:** la primera versión de la prueba usaba un título de semilla inventado. La clave de la caché de R3 no
  coincidía y daba 0 ítems; como el `call` prohibido fallaba, se iban 480 s en reintentos. Lo corregí con el título
  real («Desastre nuclear Kyshtym Mayak», de `seeds_archive.json`): 8/8 aciertos.

---

## D. Hooks de Claude Code — HECHA (0 API)

- **Dónde:** `.claude/settings.json` y `.claude/hooks/*.py` + `README.md`. Están commiteados con `git add -f` por ruta,
  porque `.claude/` está en `.gitignore`.
- **(decisión)** El matcher de los PreToolUse es `Bash|PowerShell`.

| hook | evento | qué hace |
|---|---|---|
| `guard_git.py` | PreToolUse | Bloquea `git add`/`commit` con `.env`, `config.py`, `lab/_gpt_probe_analista/` o una llave adentro. Lo que entra en el add se lo pregunta a `git add --dry-run`. También bloquea `git push` a main y `git merge` sobre main. |
| `suite_rapida.py` | PreToolUse | Antes de `git commit` corre f25c + f24 + f21 (unos 4 s). Si sale rojo, bloquea con la cola del error. |
| `md5_prompt.py` | PostToolUse Edit/Write/MultiEdit | Si el archivo es un `PROMPT_*.md` o tiene `## SISTEMA` o `SYSTEM_V2`, avisa el md5 del archivo ahora y en HEAD, y el del bloque SISTEMA. |
| `tope_tanda.py` | PreToolUse | Antes de `python … fase1_5.py` o `fase2a.py`, compara `lab/TOPE_TANDA.json` con la suma de `cost_history` desde `desde` (o desde que se escribió el tope). |

**Prueba** (`d/prueba_hooks.py` → `d/prueba_hooks.md`): **22/22**, con un caso que bloquea y uno que pasa por hook.

| hook | bloquea | pasa |
|---|---|---|
| guard_git | `git add .env`; `cd … && git add config.py b.py`; `git add -A` (con `lab/_gpt_probe_analista/`); `git add llave.txt`; commit con la llave en el índice; `git push origin main`; `git push origin rama:main`; `git checkout main && git merge rama` | `git add b.py`; commit de b.py; `git push origin rama`; `git merge main` desde rama |
| suite_rapida | commit con un test rojo (`HOOK_SUITE_RAPIDA`) | commit con la suite de verdad (3.9 s); `git status` |
| tope_tanda | fase2a y `python -I fase1_5.py` con 3.50 gastados de 3.00 | fase2a con 3.50 de 10.00; fase2b (no lo mira) |
| md5_prompt | — (no bloquea) | avisa en `PROMPT_ESCALETA_f26_1.md` y en `m01a_escaleta.py`; nada en `video_length.py` |

**En vivo.** Los hooks quedaron activos en esta misma sesión.
- **Falso positivo de guard_git:** frenó el `git add` del commit de A porque el handoff menciona los prefijos de las
  llaves como texto. Lo corregí: ahora hace falta el prefijo seguido de ≥ 20 caracteres de llave. Con el prefijo solo,
  no bloquea.
- **Bug de guard_git:** `.lstrip("./")` convertía `.env` en `env`. Lo encontró la prueba y está corregido.
- **suite_rapida** corrió antes de cada commit de F26.

**Límites, en el README:**
- Los hooks no ven lo que un script lanza por dentro.
- `cost_history` solo se escribe al cerrar un video en fase2b.
- `cost_history.json` hoy no es UTF-8 válido (cost_tracker lo escribe sin `encoding`). El hook lo lee con respaldo
  cp1252.

---

## E. Ficha con Opus 5.5 y la forma de los campos en el pedido — HECHA (opcional)

- **Qué se corrió:** `e/f26e_fichas.py`. Es el prompt de producción, con un párrafo al final de `<tarea>` generado de
  `ficha_caso.SCHEMA` («Forma del JSON: … exactamente estos nombres de campo…»). El sistema no se tocó y no hay esquema
  forzado (claude_helpers: streaming, 100k, medium).
- **Por qué en fila (decisión):** dos peores casos de 100k no entran en el tope de US$ 4.
- **Costo:** US$ 2.32 de 4. Nada cambia en producción. Tabla en `e/TABLA_E.md`.

| ficha | problemas del chequeo | cifras | decisiones · versiones · contradicciones | hechos n1 / n2 | citas (verificadas) | escenas | personas | salida (tokens) | US$ |
|---|---|---|---|---|---|---|---|---|---|
| **fO3** (Opus + forma) | **16** | 29 | 9 · 3 · 7 | 19 / 42 | 13 (13) | 10 | 36 | 45,212 | 1.0641 |
| **fO4** (Opus + forma) | **17** | 46 | 8 · 2 · 7 | 20 / 44 | 15 (15) | 10 | 39 | 54,611 | 1.2521 |
| fS2 (Sol, F25b) | 18 | 47 | 17 · 8 · 7 | 16 / 54 | 18 (16) | 11 | 45 | 27,312 | 0.3279 |
| fO1 (Opus sin forma, F25b) | 58 | 0 | 7 · 4 · 7 | 20 / 50 | 14 (14) | 11 | 43 | 59,909 | 1.3559 |
| fO2 (Opus sin forma, F25b) | 71 | 0 | 0 · 0 · 0 | 20 / 36 | 18 (17) | 10 | 38 | 52,753 | 1.2128 |

**Lectura:**
- **El problema de F25b era de forma, y se resuelve diciéndola en el pedido.**
- **Lo que el chequeo saca ahora es de contenido:** citas cuyo texto no está en sus ids (4 y 5) y cifras no respaldadas
  (años y conteos).
- **Contra Sol:** Opus da menos decisiones (8–9 contra 17), menos versiones y menos citas, y cuesta 3–4 veces más.
- **Candidatos a humano:** los mismos tres que Sol (Dubrovsky, Kuleshov, Chanova).
- Es para decidir después.

---

## Archivos
`lab/hyperframes/f26/`:
- **Raíz:** `HANDOFF_F26_nocturno.md`, `PROMPT_ESCALETA_f26_1.md`, `f26a_corridas.py`, `ESCALETA_kE{1,2}.md`,
  `NARRACION_gkE{1,2}.md`, `suite_amplia.log`, este reporte.
- **`a/`:** por tag, los resultados, prompts y respuestas crudas; `costos_f26a.json`; los logs.
- **`b/`:** runner, logs, `particion.json`, `plan_imagenes.json`, `costos_f26b.json`, `m03_traceback.txt`,
  `_4a_4e.json`.
- **`c/`:** `f26c_prueba.py`, `prueba_workers.json`, `prueba.log`.
- **`d/`:** `prueba_hooks.{py,md,json}`.
- **`e/`:** runner, `fO3/`, `fO4/`, `FICHA_fO{3,4}.md`, `TABLA_E.md`, `costos_f26e.json`.

**Fuera de git:**
- `data/topics_db.json` (con Vajont) y su respaldo `topics_db.pre_f26.json`.
- `_steps/f8s3-vajont/` (con `_pre_f26/`).
- `output/audio/f8s3-vajont/`.

**No commiteados, a propósito:** `.env`, `config.py`, `lab/_gpt_probe_analista/`, `diag_234_cap4.py`, `gfx_profiles/*`.

## Veredicto del revisor-handoff

VEREDICTO: CUMPLE CON OBSERVACIONES

Las partes A, C, D y E cumplen el handoff. La parte B no entregó el video, pero se paró como el handoff manda y el reporte lo dice sin maquillaje. Hay dos fallas de forma: el estado de sesión quedó desactualizado y el reporte no está commiteado.

| # | requisito | estado | evidencia |
|---|---|---|---|
| A1 | Prompt f26-1: solo los tres agregados literales; md5 nuevo; SYSTEM_V2 idéntico al archivo | OK | `diff` f25_1.md vs f26_1.md: solo las 3 líneas pedidas (+ nota de cabecera del .md). `m01a_escaleta.py`: SYSTEM_V2 nuevo, f25-1 conservado como SYSTEM_V2_F25_1. `test_module_f26.py` verifica la diferencia. |
| A1b | Ningún chequeo nuevo | OK | El diff de `m01a_escaleta.py` solo toca constantes de versión y bloques de texto. |
| A2 | Re-corrida Kyshtym: escaleta ×2 y guion ×2 en paralelo; promesa, 1.ª pasada, bloqueantes, palabras, citas | OK | `a/costos_f26a.json`: 7 llamadas, todas `end_turn`, US$ 5.657 (tope 8). Las cifras del reporte coinciden con `a/*/resultado.json` y con `metricas`. Faltaba `Read` completo de los guiones, pero costo y metadatos cuadran. |
| A2b | Si una promesa adelanta, anotarlo | OK | Reporte A.2: ninguna adelanta. El reporte aclara que esa lectura es suya (n=2). |
| A3 | Reparación (e) corre sola | OK, con desvío declarado | gkE2: el crudo traía 1 bloqueante. La reparación costó US$ 0.03 y borró la oración en vez de «quitar nombre, dejar rol». También corrió el editor m01c, que sacó la promesa del gancho. El reporte lo marca. Es una observación para el analista. |
| B1 | Producción hasta video (partición, imágenes, voz, gfx, ensamble, `video_vajont_f26.mp4`) | NO CUMPLE por PARADA, declarada | `b/produccion.log` y `b/m03_traceback.txt`. m03 falló 2 veces con `None.strip()` en `gemini_helpers._try_json_parse` (línea 46). El handoff dice «si un paso falla dos veces, PARADA de B». |
| B1b | Declaración honesta de lo no hecho | OK | Reporte B dice: sin paso0, assemble, fase2a, fase2b, gfx ni QA Studio, y «No hay video_vajont_f26.mp4». Costos de B (Gemini 2.4152, ElevenLabs 0.414, Claude 0, imágenes 0) cuadran con `b/costos_f26b.json`. |
| B2 | Partición en 7 caps con intents de la escaleta; sin mover párrafos; sin reescribir | OK | `produccion.log`: 7 caps, palabras por cap iguales al guion, 4 avisos de largo sin recorte. Decisión `shorten=None` declarada. |
| B3 | Voz ElevenLabs v4 | OK | Log y costos: 980.8 s = 16.3 min. El reporte aclara que no son los 19 min del handoff. |
| B4 | Sin música nueva; sin cambios de lógica en m03/voz/gfx | OK | `git diff --name-only c80e601..HEAD` no toca `m03*`, `gfx*`, voz ni `gemini_helpers`. El cambio de `SECONDS_PER_IMAGE_TARGET` (10.75) y el reemplazo de `generate_music_map` se hicieron en el proceso del runner, `b/f26b_produccion.py`. Eso es parámetro, no lógica, y está anotado. |
| B5 | No arreglar la lógica tras la parada | OK | El arreglo posible (que `_try_json_parse` trate `None` como fallo de parseo) está descrito y no se ejecutó. |
| B6 | Frenos de costo | OK | `b/f26b_produccion.py`: `_freno_gemini` con peor caso antes de 4a–4e (líneas 82-100), partición (180), normalizer (240) y m03 (253, 1.50 de peor caso). Gemini quedó en 2.42 de 5. |
| B7 | Respuesta cruda guardada | PARCIAL | Está en las llamadas Claude de A y E. En B las llamadas Gemini van por helpers y no se guarda cruda. El helper tampoco guarda `finish_reason`, así que la hipótesis de bloqueo por seguridad en el cap 1 queda sin confirmar. El reporte lo reconoce. |
| C | Workers R2/R3 (8 por defecto, `--workers`), cost_tracker con lock, `--temas`, tests sin red, prueba sin gasto | OK | Diff de `research_v3.py`, `cost_tracker.py` (RLock), `topic_researcher.py` (`--workers`) y `fase1_5.py` (`--temas`). `test_module_f26c.py` tiene 6 tests. `c/prueba_workers.json`: R3 con latencia simulada 16.7 → 2.8 s. R2 casi no gana (14.3 → 12.4 s) y el reporte lo explica. |
| C-suite | Suite amplia verde | OK, con salvedad | `suite_amplia.log`: 877 pasan y 5 fallan (`01b_pauses` ×3, `m03_merge_timing` ×2). El reporte las llama «previas», pero no las verifiqué contra la base `c80e601`. |
| D | 4 hooks en `.claude/` con caso que bloquea y caso que pasa, README | OK | `.claude/settings.json` y `.claude/hooks/*`. `d/prueba_hooks.md`: 22/22 casos. El falso positivo y el bug de `lstrip` están declarados. Desvío menor: el matcher es `Bash\|PowerShell`, no solo Bash. |
| E | Opus ×2 con la forma de los campos en el pedido, tope US$ 4, sin tocar producción | OK | `e/costos_f26e.json`: US$ 2.3162. Cifras de `TABLA_E.md` coinciden con el reporte. |
| G1 | Un commit por parte, con trailer Co-Authored-By | NO VERIFICADO | Hay 5 commits, uno por parte, pero no inspeccioné los mensajes completos para ver el trailer. El orden fue A, C, D, B, E por trabajar en paralelo; está declarado. |
| G2 | No commitear `.env`, `config.py`, `lab/_gpt_probe_analista/`, `diag_234_cap4.py`, `gfx_profiles/*` | OK | Ninguno aparece en `git diff --name-only c80e601..HEAD`. |
| G3 | `lab/ESTADO_SESION.md` actualizado al final con el estado exacto | FALLA | Sigue diciendo «F26 nocturno EN CURSO: A commiteada; B, C, D, E en marcha». Está modificado pero sin commitear, y el estado final falta. |
| G4 | Reporte F26_REPORT.md con hecho/no hecho/desvío por parte y costos | OK | Existe y está completo. Total US$ 10.80 = 7.97 + 2.42 + 0.41, que cuadra. La sección del veredicto dice REVISOR_PENDIENTE, lo esperado. El archivo no está commiteado: `git ls-files` no lo devuelve. |

Fuera de alcance: ninguno en el repo. Fuera de git, y declarado en el reporte: `data/topics_db.json` (Vajont agregado, respaldo `topics_db.pre_f26.json`), `_steps/f8s3-vajont/` (pasos viejos movidos a `_pre_f26/`, no borrados) y `output/audio/f8s3-vajont/`.

Observaciones:
1. `b/costos_f26b.json`, intento 1: el costo se «corrigió a mano». La nota dice que el tracker acumulaba el audio. El reporte lo declara, pero ese número no es medición directa.
2. La reparación (e) y el editor m01c sacaron la promesa del gancho de gkE2. El reporte lo advierte sin tocar nada.
3. El video quedó en 16.3 min, no en 19.

Riesgos que el contrato no cubre:
- El fallo de B depende de una respuesta vacía de Gemini Flash en el cap 1 (el gancho, una niña). Reintentar con el mismo código probablemente cae igual.
- Los hooks quedaron activos en la sesión y `suite_rapida` bloquea todo commit si la suite rápida se pone roja.
- Faltan commitear el reporte y `ESTADO_SESION.md` antes de mostrar el veredicto a Omar.

**Después del veredicto (CC):** G1: los 5 commits de F26 llevan el trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>` (`git log c80e601..HEAD --format=%B`, 5 de 5). G3 y G4: el reporte y `lab/ESTADO_SESION.md` con el estado final entran en el commit final, después de este veredicto.

**PARADA final.**
