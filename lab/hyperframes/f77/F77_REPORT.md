# F77: gate ES por API · research más rápido · estante de temas · corrida real de 4 semillas (PARADA)
2026-11-04 · rama f11-guion-v4 · base f63922f · handoff `HANDOFF_F77.md`, md5 `95b4d7bf227d393c4c1d574bd13d6c81` (verificado antes de arrancar)
Omar estaba fuera, así que no hice preguntas: cada decisión que tomé está anotada abajo.

## En corto
- **A (gate ES por API):** hecho. Mide con la API oficial y los Shorts quedan fuera. El contrato de Palomares dio **DISPUTADO, no SATURADO**. La causa es la búsqueda: el video de A toda leche no aparece buscando «Palomares 1966».
- **B (research más rápido):** hecho. En la corrida real, el research tardó **5,4 min (colza) y 7,8 min (Palomares)**, contra 22,6 de Kyshtym.
- **C (estante):** hecho. En el form hay dos menús nuevos, «D · Tanda de semillas» y «E · Estante (N)». Agregué `fase1_5 --hasta-ficha` y la etapa «estante» en `run_pipeline`.
- **D (corrida real):** gate de las 4 semillas → 2 SATURADO sin research, 2 con research completo.
  - **Las 2 fichas no se pudieron hacer: la llave de OpenAI está vencida** (HTTP 401 `expired_secret_key`, la ficha usa `gpt-6.1-sol`). No es irreversible.
  - Cuando Omar renueve la llave, cada ficha se retoma con `python fase1_5.py --topic <tid> --batch --hasta-ficha`, sin repetir el research. Los comandos exactos están en «abierto».
- Gasto: **US$ 2,38** en research, más los juicios del gate. Unidades de API de YouTube: 2.009 en D más 1.005 en A.
- No se tocó Wittenoom (md5 del mp4 `1fb47948…`, el mismo antes y después). No hubo render, voz ni fotos, y nada corrió después de la ficha.
- `topics_db`: tenía 1 topic y ahora tiene 3; no se perdió ninguno. El candado nuevo quedó liberado.
- Subagentes: A y B en paralelo. Los tests de C los escribió un tercero mientras D corría.

## Etapa A: gate ES por API oficial
**Cambios**
- **`script_engine/youtube_scanner.py`**:
  - `list_spanish_candidates` busca **primero por la API**: `search.list` paginado (`type=video`, `relevanceLanguage=es`) hasta `YT_LIMIT_ARCHAEOLOGY`, y después `videos.list` en lotes de 50.
  - **Solo cuentan los videos de más de 180 s.** La salida tiene la misma forma que antes, más `duration_s` y `source`.
  - Si la API falla (403, red, sin llave), vuelve al raspado, con el mismo filtro de duración. Si la duración no se conoce, el video se cuenta.
  - La llave va en el header `X-Goog-Api-Key` y nunca en la URL ni en los logs; un script verificó que no aparece en ninguna salida.
  - Constantes con origen: `SHORTS_MAX_S=180` y `YT_API_PAGE_MAX=50`. **Decisión declarada:** también `YT_UNITS_SEARCH=100` y `YT_UNITS_VIDEOS=1`, que son los dos costos estándar de cuota de la fórmula A4.
  - `ES_GAP_WORKERS=3` ahora solo limita el raspado de respaldo.
  - A4: cada medida deja una línea de log con fuente, páginas, lotes, unidades, crudos y cortos.
- **`script_engine/subtopic_measurer.py`**: `_measure_es` suma `source`, `quota_units`, `candidates` (con peso y si el juez lo da por relevante) y el competidor más pesado con `video_id` y duración.
- **`niche_discoverer.py`** (A2): los loops ES van en paralelo, con tantos workers como ítems. El raspado de respaldo sigue limitado a 3 a la vez.
- **`fase1.py`**: nueva `measure_pick_es(seed, n=3)`, que mide sin preguntar (la usa la tanda). `_verify_pick_es_saturation` la usa y conserva su P/S/Q. **Decisión declarada:** las 3 re-medidas de un mismo pick van en fila; el paralelo es entre títulos (C).
- **A3:** la búsqueda saca lo que está entre paréntesis y la puntuación final. El título del topic no cambia.
- **Tests:** `test_module_f77a.py` (19). Cambié una aserción de `test_es_measure_offline.py` (`source` termina en «+juez»). No había tests que afirmaran el raspado como camino primario.

**Contrato A: «Palomares 1966», corrida real** (`lab/hyperframes/f77/a/contrato_a_palomares.out.txt`)
- Las 3 corridas fueron por API (`api+juez`) y las 3 dieron **DISPUTADO**, con sat 37.805.
- En cada una: 50 resultados crudos → 24 o 25 Shorts fuera → 14 o 15 videos ES largos.
- Gasto: 303 unidades, más 702 de dos diagnósticos.

| # | id | título | dur | views | meses | peso | relevante |
|---|---|---|---|---|---|---|---|
| 1 | 0d9xjzcx-fc | Accidentes Nucleares en la Guerra Fría: Thule y Palomares (SLICE Iberia) | 51:08 | 63.009 | 13 | 0,6 | sí |
| 2 | _dabgyhU3tQ | Palomares: una catástrofe nuclear en España (Megaestructuras franquistas) | 6:32 | 104.241 | 58 | 0,3 | sí |
| 3 | xMGCHflg8ok | El incidente de Palomares (parte 1) | 18:26 | 34.386 | 58 | 0,3 | sí |
| 4 | vduGqR001KM | Palomares: Episodio 1 - «El día que ardió el cielo» | 10:17 | 56.631 | 66 | 0,1 | sí |
| 5 | UnovtMSJ9kA | Preocupación ambiental en Palomares a 57 años… | 16:22 | 15.831 | 37 | 0,3 | sí |
| 6 | LXOPm7JvLyk | 1966: El INFIERNO CAE sobre PALOMARES (1/2) | 19:08 | 40.897 | 76 | 0,1 | sí |
| 7 | zFfSRJF2jno | Las bombas atómicas de Palomares (Almería, 1966) | 24:33 | 27.638 | 164 | 0,1 | sí |
| 8–15 | (8 videos chicos sobre Palomares) | | 3:56–21:36 | 5–3.362 | 0–189 | 0,1–1,0 | sí |

- **Label: DISPUTADO.** El competidor más pesado es SLICE Iberia `0d9xjzcx-fc`.
- Los Shorts `IUpaoH-lvkI` y `Yvo7kps24Fo` **no aparecen**.
- De los largos que esperaba el analista aparecen DMAX, SLICE y Movistar; no aparece Herrera Plaza `lxQeaNdeaZI`.
- **Por qué no es SATURADO: la búsqueda.** `4VgrwqGvIuc` («4 BOMBAS NUCLEARES cayeron en España», 647 s, 212.734 views, 0 meses) pasaría todos los filtros. Pero no está en los primeros 200 resultados de «Palomares 1966» ni en los primeros 50 de «Palomares», porque su título no dice «Palomares». En «bombas nucleares Palomares» queda en el puesto 16.
- No es culpa del juez ni de la fecha. Para atraparlo haría falta una segunda búsqueda, cosa que el handoff no pide; va a «abierto».

## Etapa B: research más rápido (`researcher_steps/research_v3.py`)
- **B1:** los 4 focos de R1 van en paralelo, y después las pistas que falten, también en paralelo. `_r1_cache.json` tiene un solo escritor (un candado) y se guarda de forma atómica.
- **B2: carrera Pro + Flash con búsqueda en cada ronda.**
  - Si los dos traen fuentes, se suman, quitando las URL repetidas con `_dedupe_ground`. Si trae uno solo, queda ese.
  - Si no trae ninguno, hay otra ronda: Pro con `R1_FORCE_SEARCH` más Flash, hasta `R1_RETRIES` = 3 rondas.
  - `via` vale `pro`, `flash`, `ambos` o `sin`. Un error o un 429 cuenta como «sin fuentes», así que el otro modelo igual vale.
  - Se borró la cadena vieja (Pro ×4 en fila → Flash) y su test (`test_module_f8b`). `test_module_f7` se reescribió con Flash mockeado.
- **B3:** en R3, las partes de un mismo documento van en paralelo. El tope total de llamadas a la vez sigue siendo `WORKERS` = 8.
- **B4: reloj por sub-paso.** Va en `tiempos_research`, en `01_v3_costos.json` y en `01_v3_tiempos.json`. **Arreglé** `fase1_5._step_cost`: leía el archivo antes del paso y lo pisaba al final; ahora lo relee después.
- **Decisiones declaradas:**
  - las pistas también corren la carrera;
  - las pistas se eligen una sola vez, después de los focos;
  - el único número literal nuevo es el pool de 2 hilos de la carrera (uno para Pro, uno para Flash), que sale del diseño, no de un ajuste.
- **Tests:** `test_module_f77b.py` (21), con todo mockeado:
  - focos en paralelo (con barrera);
  - carrera: solo Pro / solo Flash / ambos / ninguno hasta 3 rondas → `sin`;
  - caché sin carreras con 8 hilos;
  - R3 en paralelo, igual al resultado en fila;
  - reloj.
- 336 verdes en los archivos que usan research_v3.

## Etapa C: estante de temas
- **`estante.py` (nuevo):**
  - `correr_tanda(titulos)`: semilla del modo C → gate de todos a la vez → un subproceso `fase1_5 --semilla data/estante/<tid>.json --topic <tid> --batch --hasta-ficha` por cada tema que sigue, todos a la vez.
  - `listar()`: el estante, **deducido del disco**: sin `01a_escaleta.json`, y con ficha, o SATURADO, o compuerta roja / sin ficha (⚠).
  - `ordenar()`: VACIO/HUECO → DISPUTADO → SATURADO; dentro de cada grupo, más `elegibles_humano` primero; los ⚠ al final.
  - `body()`: la tabla del menú E.
- **Decisión declarada: `data/estante/<tid>.json`.** Es la semilla más el resultado del gate y la entrada que necesita `fase1_5 --semilla`. Va ahí porque `research_de_semilla` no acepta un `_steps/<tid>/` que ya exista.
  - No es estado nuevo de la cadena: el estante se deduce de los artefactos.
  - Los temas SATURADO solo existen en ese registro, porque no tienen research.
- **`fase1_5.py`:** `--hasta-ficha`, que corre compuerta del pool → ficha si falta y termina con exit 0 (compuerta roja = exit 2). No llega a la escaleta ni al canon.
- **`run_pipeline.py`:**
  - `etapa_de` devuelve `estante` cuando hay ficha sin escaleta. Corre como «guion», es decir fase1_5 desde la escaleta.
  - `ETAPAS` no cambia: el estante ocupa el lugar de «guion» en el orden (`_orden`).
- **`niche_discoverer.py`:**
  - **D (tanda):** el marcador de texto libre de F74 (`tanda_titulos`) recibe los títulos separados por «;».
  - **E (estante):** aparece primero en la lista y como default cuando N > 0. Elegir un tema escribe el sentinel de research [tid], así `run_pipeline --research` sigue con ese tema desde la escaleta. Los demás no se tocan.
  - **Decisión declarada:** D y E están en el menú de métodos (`discovery_mode`), junto a A, B y C. Si hay semillas pendientes, primero aparece la galería, como hoy; con «+ Generar nuevos seeds» se llega al menú.
- **`topic_researcher.py`:** al registrar el topic en `topics_db`, ahora hay **candado entre procesos y guardado atómico**.
  - Por qué: con 4 research a la vez, un lector que viera el archivo a medio escribir lo daba por vacío, y el guardado siguiente borraba los topics.
  - El chequeo de que el proceso dueño del candado sigue vivo es seguro en Windows: usa `OpenProcess`, nunca `os.kill(pid, 0)`, que en Windows termina el proceso.
- **Tests:** `test_module_f77c.py` (58), aislados en tmp_path con un fixture que lo comprueba al final. En `test_module_f74` agregué un doble de `_n_estante` para que el menú no lea el estante real.

## Etapa D: corrida real (equivalente por línea de comando)
`lab/hyperframes/f77/d/correr_tanda.py` llama a la misma función que el form (`estante.correr_tanda`) con los 4 títulos, usando el Python del venv. La tanda entera tardó **599 s**. Tablas: `lab/hyperframes/f77/d/tablas_d.md`.

**(a) Gate de los 4**
| tema | label | competidor más pesado | unidades API | sigue |
|---|---|---|---|---|
| Palomares 1966: el Proyecto Indalo y los vecinos usados como cobayas | **VACIO** | — | 300 | sí |
| Síndrome del aceite tóxico (colza) 1981 | HUECO | «El síndrome tóxico» `rjKL9NbUPoE`, 77.560 views, 61 meses | 303 | sí |
| Accidente radiológico de Goiânia 1987 | SATURADO | «El Robo que Terminó en Desastre Nuclear - El Accidente de Goiania» `DSrn0cBP3Xg`, 1.519.327 views, 43 meses | 303 | no |
| Tragedia del camping Los Alfaques 1978 | SATURADO | «El ACCIDENTE de los Alfaques ⚠️ …» `a4gcbna-fmc`, 460.919 views, 3 meses | 1.103 | no |

⚠ **Palomares dio VACIO por el título largo.** La búsqueda usa el título casi entero: los dos puntos del medio no se sacan, solo la puntuación final. Con un título así, YouTube no devuelve los videos del caso. El mismo tema con el título corto dio DISPUTADO en el Contrato A. Va a «abierto».

**(b) Tiempos por sub-paso (s)** (Kyshtym: R1 ~780 · R3 ~348 · research 1.356)
| tema | perfil | R1 | R2 | R3 | pool | research total |
|---|---|---|---|---|---|---|
| Palomares 1966 | 25 | 151 | 56 | 88 | 149 | **468** (7,8 min) |
| colza 1981 | 20 | 171 | 24 | 43 | 65 | **323** (5,4 min) |

R3 por documento: Palomares F06 tenía 6 partes y tardó 87 s en paralelo; la de Kyshtym, F07, iba en fila.

**(c) R1 por foco** (Wittenoom: 2 de 4 «sin»)
| tema | foco 1 | foco 2 | foco 3 | foco 4 |
|---|---|---|---|---|
| Palomares | sin (3 rondas) | sin (3) | sin (3) | flash, 8 URLs |
| colza | flash, 8 URLs (2 rondas) | sin (3) | pro, 3 URLs (1) | sin (3) |

La carrera no mejoró el grounding: hubo 3 de 4 focos «sin» en Palomares y 2 de 4 en colza, ninguno con `ambos`. El research igual llegó a pools grandes (Palomares 189 datos, compuerta verde; colza 97 datos, amarilla), porque R2 y R3 se apoyan en las fuentes que sí trajo. Va a «abierto».

**(d) Límites de velocidad:** con 2 research a la vez, el log tiene 0 menciones de 429 o rate limit y 0 errores de modelo en las rondas de R1. Solo hubo 2 temas a la vez, no 4, porque 2 quedaron SATURADO, así que la carga real fue la mitad de la prevista.

**(e) Body del menú E**, tal cual lo vería Omar:

Estante (4)

| # | título | gate | pool | ficha | US$ |
|---|---|---|---|---|---|
| 1 | Palomares 1966: el Proyecto Indalo y los vecinos usados como cobayas ⚠ sin ficha (exit 2; ver data/estante/1b2a2c5d-9ff3-433a-bd3b-767ca7b44d89.log) | VACIO | 189 datos · 34 citas · 43 personas · 102 eventos · 9 humanos · verde | — | 1.52 |
| 2 | Síndrome del aceite tóxico (colza) 1981 ⚠ sin ficha (exit 2; ver data/estante/c4934b7d-3f54-448f-ba5f-539dc744f0d8.log) | HUECO · «El síndrome tóxico» 77.560 views, 61 meses | 97 datos · 17 citas · 18 personas · 25 eventos · 5 humanos · amarillo | — | 0.86 |
| 3 | Accidente radiológico de Goiânia 1987 ⚠ SATURADO: sin research | SATURADO · «El Robo que Terminó en Desastre Nuclear - El Accidente de Go» 1.519.327 views, 43 meses | — | — | 0.00 |
| 4 | Tragedia del camping Los Alfaques 1978 ⚠ SATURADO: sin research | SATURADO · «El ACCIDENTE de los Alfaques ⚠️ La Tragedia que Conmocionó a» 460.919 views, 3 meses | — | — | 0.00 |

Hoy no hay ningún tema elegible: los dos que tienen research esperan la ficha.

**(f) US$ por tema** (`01_v3_costos.json`, research): Palomares 1,5214 · colza 0,8575 · Goiânia 0 · Alfaques 0. **Total: 2,38.** Los juicios Gemini del gate (alias + juez, ×3 por tema) no se atribuyen a ningún topic. La ficha no se cobró, porque falló antes de llamar.

## Chascadas
- `audio_master._perfil` → `perfil` (público). Lo usan `audio_manager`, `fase2b`, `transition_applier` y `test_module_f76`.
- `DECISIONES.md`: 4 líneas con fecha 2026-11-04:
  - el master aprobado por oído (15:57);
  - D1–D6;
  - V1–V6;
  - el estante (16:02).

## Verificación
- Suite amplia: 140 archivos más `tests/`, `test_qa_studio.py` y `test_run_pipeline.py`, con `-n auto` y el proxy muerto. Dio 10 fallas: 7 de `f65b`, que habla HTTP con su servidor local y el proxy muerto lo corta, y las 3 heredadas.
  - Volví a correr esos archivos sin proxy: **solo las 3 heredadas** (`f51c[paredes de chapa]` y `m03_merge_timing` ×2).
  - En total, **1747 passed**; las fallas que quedan son las 3 heredadas. Log: `lab/hyperframes/f77/suite.log`.
- `mapa_modulos --check`: 163 archivos · **0 fallas**. Hay sticker nuevo para `estante.py` y quedaron al día los de los 12 archivos tocados.
- Wittenoom: md5 del mp4 igual. `topics_db`: 3 topics, sin candado colgado.

## Abierto
1. **La llave de OpenAI está vencida (bloquea toda ficha).** Hay que renovarla en `config.py`, que está fuera de git. Después, para las dos fichas, sin repetir el research:

   ```bash
   python fase1_5.py --topic 1b2a2c5d-9ff3-433a-bd3b-767ca7b44d89 --batch --hasta-ficha
   ```

   ```bash
   python fase1_5.py --topic c4934b7d-3f54-448f-ba5f-539dc744f0d8 --batch --hasta-ficha
   ```
2. **El gate de Palomares depende del título.** Con el título largo dio VACIO y con «Palomares 1966» dio DISPUTADO; el video de A toda leche no aparece con ninguna de las dos búsquedas. Opciones para el analista:
   - una segunda búsqueda con los alias ES del juez;
   - buscar con el «núcleo» del título, antes de los dos puntos.

   No lo construí porque es comportamiento nuevo fuera del handoff.
3. **El grounding de R1 sigue flojo:** 3 de 4 y 2 de 4 focos quedaron «sin». La carrera hace más rápido R1, pero no consigue más fuentes.
4. **Limitación de la prueba de velocidad.** Solo corrieron 2 research a la vez; no se probaron 4.
5. **Mensaje confuso al elegir del estante (E).** fase1 imprime «No se generaron seeds. Abortando.», pero el sentinel queda con [tid] y `run_pipeline --research` sigue bien. Revisé el camino de código, pero no lo corrí en el form real.
6. **El form no se probó en vivo.** Los menús D y E están probados con tests y en terminal, no en el QA Studio con Omar.
7. **`exit 2` es ambiguo.** Vale para «compuerta roja» y para «ficha fallida»: el estante no distingue el motivo y hay que leer el log (lo observó el revisor).
8. **Costos que no se atribuyen.** Los juicios del gate no quedan atribuidos a ningún topic. Si la API falla después de gastar páginas, esas unidades no se cuentan en el log del respaldo.
9. **Pendientes que siguen de antes:**
   - el pool fusiona homónimos padre/hijo;
   - la escaleta no comprueba que `humano.id` coincida con su `rol`;
   - las rachas no cuentan pronombres;
   - los personajes con partícula.

## Veredicto del revisor-handoff
VEREDICTO: CUMPLE CON OBSERVACIONES

El contrato se cumple salvo un punto: D no llegó a la ficha por la llave de OpenAI vencida, con el research completo hecho. No es un fallo de la tanda.

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Handoff íntegro | OK | md5 95b4d7bf... coincide |
| 2 | A: gate por API, solo videos > 180 s, respaldo por raspado, cuota en el log | OK | diff de `youtube_scanner.py` (+208) y `test_module_f77a.py`; salida del Contrato A en `lab/hyperframes/f77/a/` |
| 3 | A: tabla de candidatos, label y unidades | OK | `lab/hyperframes/f77/a/contrato_a_palomares.out.txt`; el reporte los incluye |
| 4 | Contrato A «SATURADO» esperado | PARCIAL (declarado) | Dio DISPUTADO. La explicación es coherente y está medida: `4VgrwqGvIuc` no entra en los resultados de «Palomares 1966». Es la salida que el handoff permitía: «si no da SATURADO, decir por qué, no es PARADA». |
| 5 | B: R1 con focos en paralelo, carrera Pro+Flash, `via` pro/flash/ambos/sin, R3 en paralelo, reloj por sub-paso | OK | diff de `research_v3.py`; `test_module_f77b.py` (21 tests); `01_v3_tiempos.json` tiene los pasos y las rondas |
| 5b | Cadena vieja borrada con su test | OK | grep sin rastros de la cadena «Pro ×4 → Flash» en `research_v3.py`. El test viejo de `test_module_f8b.py` se quitó y quedó un comentario que apunta al test nuevo. |
| 6 | C: modo D, menú E, `--hasta-ficha`, etapa `estante` | OK | `estante.py` nuevo, `fase1_5.py`, `run_pipeline.py`, `niche_discoverer.py`; `test_module_f77c.py` (58 tests) |
| 7 | D: corrida real de las 4 semillas hasta la ficha | PARCIAL | Gate de las 4 y research de 2 hechos. Las 2 fichas no salieron: `data/estante/1b2a2c5d....log:18-25` muestra `GPTError gpt-6.1-sol HTTP 401 expired_secret_key`. |
| 8 | D: tablas (a)–(f) contra los datos | OK | `tablas_d.md` coincide con `01_v3_tiempos.json`: Palomares perfil 25,41 / R1 150,73 / R2 55,98 / R3 87,55 / pool 148,69 / total 468,36; colza total 322,94. Gate contra `data/estante/*.json`: Palomares VACIO 300 unidades, Alfaques y Goiânia SATURADO. US$ 1,5215 coincide con el log. |
| 9 | Suite pedida | OK | La corrí 3 veces; 2 dieron 188 passed y la primera falló una vez (ver observación 1). |
| 10 | Suite rápida + 3 heredadas | OK | `suite.log`: 1747 passed, 10 failed. 7 son de `f65b` (proxy muerto, y el reporte dice que sin proxy pasan). Las 3 heredadas no las re-corrí. |
| 11 | `mapa_modulos --check` | OK | 163 archivos, 0 fallas |
| 12 | Wittenoom intacto | OK | md5 del mp4 = 1fb47948e43951d4c009e13c0131d184. Los topics previos no los toqué ni modifiqué. |
| 13 | Llave de API no impresa | OK | Grep por AIza y sk- sin coincidencias en `lab/hyperframes/f77`, `data/estante`, `estante.py` ni `data/scripts/_steps`. No miré los logs de otras carpetas. |
| 14 | Sin render, voz, fotos ni nada después de la ficha | OK | `lab/hyperframes/f77/` solo tiene logs y tablas; no hay `01a_escaleta.json` |
| 15 | Chascada `_perfil` → `perfil` | OK | Cero ocurrencias de `_perfil` en `audio_manager.py`, `fase2b.py` y `transition_applier.py` (la comparación del grep excluyó `lab/`). |
| 16 | `DECISIONES.md` con las 4 líneas fechadas | OK | +4 líneas en el diff (no abrí su texto) |
| 17 | Reporte con «abierto» completo y veredicto del revisor | PARCIAL | «Abierto» está completo (8 puntos). La sección del veredicto del revisor está vacía a propósito, para pegar este texto. |
| 18 | Commit archivo por archivo, push, ESTADO_SESION | NO VERIFICABLE | Es posterior a este veredicto. |

**Fuera de alcance:** ninguno de la tanda. Siguen sucios los 3 ajenos declarados (`diag_234_cap4.py`, `f28a.log`, `pedido_paquetes_wittenoom.txt`), que no deben entrar al commit. Los stickers de `lab/mapa/stickers/*.json` son esperables por el `mapa --check`.

**Observaciones**
1. En la primera corrida del comando pedido, `test_module_f77c.py::test_lock_de_pid_vivo_espera` falló con `PermissionError` WinError 32 al borrar `topics_db.json.lock`. Reintentos: 188 passed dos veces y el test aislado pasó. Es una carrera de Windows al limpiar el lock de ese test; es flaky, no está resuelto.
2. Sobre no haber hecho las fichas por la llave de OpenAI vencida: sí fue razonable. El 401 es real y está en el log, el handoff no pedía parar y el research no se pierde. Los comandos para retomar están en «abierto».
3. Ambigüedad de `exit 2`: es a la vez «compuerta roja» y «ficha fallida». En el estante, la ficha caída por 401 quedó marcada como ⚠ sin ficha. No es incorrecto, pero Palomares tiene compuerta verde y la causa real está solo en el log.
4. Palomares dio VACIO con el título largo y DISPUTADO con el corto. La búsqueda de A3 solo quita paréntesis y puntuación final, como pedía el handoff, pero es una debilidad de la medida. Está declarada en «abierto».
5. R1: la carrera acelera pero no mejora el grounding. Hubo 3 de 4 y 2 de 4 focos «sin», y ninguno `ambos`. Está declarado.
6. Solo corrieron 2 research a la vez (no 4), así que la prueba de límites de velocidad es parcial. Está declarado.
7. Cambio no pedido pero declarado: candado y guardado atómico de `topics_db` en `topic_researcher.py`. Es razonable para el paralelismo, pero amplía el alcance.

**Riesgos que el contrato no cubre**
- El form (menús D y E) no se probó en vivo en QA Studio, solo con tests y en terminal. Tampoco se cubre el mensaje «No se generaron seeds» al elegir del estante.
- El gate puede dar VACIO por título largo y gastar un research completo (US$ 1,52 en Palomares) en un tema que debería haber sido DISPUTADO o SATURADO.
- Hay gasto de juicios Gemini del gate que no se atribuye a ningún topic.

### Adenda de CC
- **Obs. 1 (lock flaky):** también podía pasar en producción, porque en Windows no se puede borrar un archivo mientras otro proceso lo lee para sacar el pid. Lo arreglé en `topic_researcher.py`:
  - `_borrar_lock` reintenta ante `PermissionError`;
  - al tomar el candado, un `PermissionError` (candado a medio borrar) cuenta como «ocupado».
  - `test_module_f77c.py` pasó 5 de 5 seguidas. El sticker está al día y `mapa --check` da 0.
- **Obs. 3 (exit 2 ambiguo):** de acuerdo. El estante muestra «sin ficha (exit 2; ver log)» y la compuerta en la columna pool (Palomares verde). La causa de hoy (401) está en el reporte y en «abierto». Distinguir el motivo en el estante queda anotado.
- **Punto 10:** las 3 heredadas las corrí sin proxy: `f51c[paredes de chapa]` y `m03_merge_timing` ×2, nada más.
- **Obs. 7:** el candado era necesario para cumplir «no tocar los topics existentes» con varios research a la vez. Sin él, un lector que agarrara el archivo a medio escribir podía terminar borrando la base. Por eso entró.
