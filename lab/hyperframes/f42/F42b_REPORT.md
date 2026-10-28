# F42b — Las librerías del form y que una falla se vea como falla (REPORTE)

CC · 2026-10-27 · rama `f11-guion-v4` · misma sesión que F42 · handoff `lab/hyperframes/f42/HANDOFF_F42b_dependencias_y_fallas_visibles.md` (md5 `c8f1cad417564f1c6e16a08f217efa92` ✓, el del mensaje de Omar).

## Lecturas declaradas
- Del handoff: entero.
- Del código, enteros los trozos que toca:
  - `run_pipeline.py` (`main`, `_run`, `sequence`);
  - `fase1.py` (`run_latido_a` entero, `__main__`);
  - `topic_researcher.py` (`research_topics` entero);
  - `researcher_steps/research_v3.py:672-760`, 868-880 (`html_to_text`, `pdf_to_text`, `linked_pdf`);
  - `audio_manager.py:108-128`;
  - `qa_form.html:185-195`;
  - `requirements.txt`;
  - los fixtures de `test_run_pipeline.py` y `test_module_f7d.py`;
  - los tests que se rompieron, de `test_module_f33.py` y `test_module_f36.py`.
- De la sesión: `CLAUDE.md`, `DECISIONES.md` y `ESTADO` ya estaban leídos en F42.

## Módulos que toca (hoy → después; stickers de `lab/MAPA_PROYECTO.md`)
| archivo | hoy | después |
|---|---|---|
| `dependencias.py` (nuevo) | — | Sigue los imports desde los scripts de etapa de `run_pipeline` (leídos por AST) y separa las librerías de afuera en requeridas u opcionales, con archivo:línea. `faltantes()` usa `find_spec` sin importar. `--requirements` da `distribución==versión`. Sticker nuevo (vivo, `orquestador/form`). |
| `run_pipeline.py` | «el director de orquesta: corre una tras otra las etapas…». Con `--research`, un error de fase1 decía «falló o se canceló». | Antes de cualquier etapa, `_chequeo_dependencias()`: si falta una requerida, PARADA con exit 1, la lista y el comando de pip; las opcionales solo avisan. Con `--research`, «⛔ fase1: el research falló (exit N)…». |
| `topic_researcher.py` | Una semilla que falla se loguea y se sigue. | `research_topics` devuelve `Investigados` (la misma lista de siempre más `.fallas`, con seed_id, título y error). El resumen dice «N semilla(s) fallaron» y no manda a `topic_validator`. `PoolGateRed` no cambia. |
| `fase1.py` | Sin topics → `return` (exit 0). | Imprime cada falla («semilla X: error Y; sigue en la bandeja») y sale con 1. Soltar el pick o cancelar sigue en 0. |
| `requirements.txt` | Le faltaban `beautifulsoup4` y `pypdf`. | Las agrega, y `requests` y `urllib3` quedan con la versión del Python del form. |
| `test_module_f42b.py` (nuevo), `test_run_pipeline.py` (fixture), `test_module_f33.py` y `test_module_f36.py` (contrato del mapa de F42) | — | Ver B, C y la validación. |

Stickers de `dependencias`, `run_pipeline`, `fase1` y `topic_researcher` reescritos con su md5. Mapa regenerado: `--check` = 0 (156 archivos).

## Commits (en `origin/f11-guion-v4`; `main` sin tocar)
| parte | commit |
|---|---|
| A | `bf8cbf4` dependencias.py, requirements.txt, sticker y mapa, handoff |
| B | `d58d1a3` PARADA por librería faltante en run_pipeline.main + tests |
| C | `fd5e956` la falla del research se ve: research_topics, fase1 y el mensaje de run_pipeline + tests |
| arreglo de F42 | `4e3c438` 3 tests del contrato viejo del mapa (f33 ×2, f36 ×1) que F42 rompió sin verlos, más los logs de la validación |
| reporte | el último (este archivo + ESTADO) |

---

## A — El Python del form y lo que le falta
**Python del form: `C:\CLAUDE_PROJECTS\viral-video-pipeline\.venv\Scripts\python.exe`** (3.11.9, venv con `include-system-site-packages = false`).
- **Cómo lo identifiqué:** cuando arrancó F42b ya no había ningún proceso `python` vivo (`Get-CimInstance Win32_Process` = 0); el `qa_studio_server` de Omar ya no corría. La ruta sale de la lectura del proceso vivo que hice en esta misma sesión, durante F42 (22:28 y 22:47):
  - PID 36024, `…\.venv\Scripts\python.exe qa_studio_server.py`, con su hijo PID 38136, el `python.exe` base que lanza el venv;
  - el `run_pipeline.py --research --video-type long --batch` y el `fase1.py --no-chain` de la corrida de las 21:58 tenían el mismo ejecutable.
- No cerré ni toqué nada.

### Tabla 1 — antes de instalar (`"<Python del form>" dependencias.py`)
```
Python: C:\CLAUDE_PROJECTS\viral-video-pipeline\.venv\Scripts\python.exe
| librería | requerida u opcional | archivo:línea | la tiene |
|---|---|---|---|
| PIL | requerida | foto_madre.py:64, script_engine/gfx_critic.py:187, script_engine/gfx_project.py:592 (+3) | sí |
| bs4 | requerida | researcher_steps/research_v3.py:687, researcher_steps/research_v3.py:874 | NO |
| faster_whisper | requerida | audio_manager.py:120 | sí |
| google | requerida | config.py:26, gemini_helpers.py:6, gemini_helpers.py:7 (+13) | sí |
| langdetect | requerida | script_engine/youtube_scanner.py:68 | sí |
| numpy | requerida | fase2b.py:3074, script_engine/gfx_guion.py:84, script_engine/gfx_guion.py:92 (+6) | sí |
| pdfplumber | opcional | researcher_steps/research_v3.py:748 | NO |
| pypdf | requerida | researcher_steps/research_v3.py:756 | NO |
| pyphen | requerida | fase2b.py:44 | sí |
| pytrends | requerida | topic_validator.py:48 | sí |
| requests | requerida | asset_manager.py:45, audio_manager.py:46, foto_madre.py:22 (+5) | sí |
| scrapetube | requerida | script_engine/youtube_scanner.py:67 | sí |
| trafilatura | opcional | researcher_steps/research_v3.py:681 | NO |
| typing_extensions | requerida | flow_profiles.py:20 | sí |
| urllib3 | requerida | script_engine/youtube_scanner.py:42 | sí |
| youtube_transcript_api | opcional | script_engine/transcript_fetch.py:64, script_engine/transcript_fetch.py:75 | sí |

2 requeridas faltantes · 2 opcionales faltantes
```

### Instalación (solo las requeridas que faltaban, en el Python del form)
```
$ "C:\CLAUDE_PROJECTS\viral-video-pipeline\.venv\Scripts\python.exe" -m pip install beautifulsoup4 pypdf
Successfully installed beautifulsoup4-4.15.0 pypdf-6.21.3 soupsieve-3.0.4
$ … -m pip check
No broken requirements found.
```
- `bs4` es el nombre de import del paquete `beautifulsoup4`.
- No instalé las opcionales (`trafilatura`, `pdfplumber`): la regla 5 dice «solo las requeridas que falten».

### requirements.txt (diff)
```
+beautifulsoup4==4.15.0
+pypdf==6.21.3
-requests==2.33.1
+requests==2.34.2
-urllib3==2.6.3
+urllib3==2.7.0
```
Las versiones salen de `dependencias.py --requirements`, que usa `importlib.metadata` en el Python del form. El resto de las requeridas ya estaba con la misma versión. `scrapetube` sigue con la línea del fork de git.

### Tabla 2 — después
```
Python: C:\CLAUDE_PROJECTS\viral-video-pipeline\.venv\Scripts\python.exe
| librería | requerida u opcional | archivo:línea | la tiene |
|---|---|---|---|
| PIL | requerida | foto_madre.py:64, script_engine/gfx_critic.py:187, script_engine/gfx_project.py:592 (+3) | sí |
| bs4 | requerida | researcher_steps/research_v3.py:687, researcher_steps/research_v3.py:874 | sí |
| faster_whisper | requerida | audio_manager.py:120 | sí |
| google | requerida | config.py:26, gemini_helpers.py:6, gemini_helpers.py:7 (+13) | sí |
| langdetect | requerida | script_engine/youtube_scanner.py:68 | sí |
| numpy | requerida | fase2b.py:3074, script_engine/gfx_guion.py:84, script_engine/gfx_guion.py:92 (+6) | sí |
| pdfplumber | opcional | researcher_steps/research_v3.py:748 | NO |
| pypdf | requerida | researcher_steps/research_v3.py:756 | sí |
| pyphen | requerida | fase2b.py:44 | sí |
| pytrends | requerida | topic_validator.py:48 | sí |
| requests | requerida | asset_manager.py:45, audio_manager.py:46, foto_madre.py:22 (+5) | sí |
| scrapetube | requerida | script_engine/youtube_scanner.py:67 | sí |
| trafilatura | opcional | researcher_steps/research_v3.py:681 | NO |
| typing_extensions | requerida | flow_profiles.py:20 | sí |
| urllib3 | requerida | script_engine/youtube_scanner.py:42 | sí |
| youtube_transcript_api | opcional | script_engine/transcript_fetch.py:64, script_engine/transcript_fetch.py:75 | sí |

0 requeridas faltantes · 2 opcionales faltantes
```
**0 requeridas faltantes.**

---

## B — PARADA antes de gastar si falta una librería
Salida de la PARADA simulada, tal cual. Es `find_spec` simulado (`bs4` = None, el resto presente) y un `_run` que falla si lo llaman; corrió con el Python del sistema, por eso esa ruta en «Python:».
```
$ python run_pipeline.py --research --video-type long --batch   (find_spec simulado: falta bs4)

════════════════════════════════════════════════════════════
  ⛔ PARADA antes de gastar: a este Python le faltan librerías que la cadena necesita
     Python: C:\Users\Canada\AppData\Local\Programs\Python\Python311\python.exe
     - bs4: researcher_steps/research_v3.py:687, researcher_steps/research_v3.py:874
  ➡  Instalalas y retomá: "C:\Users\Canada\AppData\Local\Programs\Python\Python311\python.exe" -m pip install -r requirements.txt
════════════════════════════════════════════════════════════

exit 1
```

El chequeo real con el Python del form, sin simular (`lab/hyperframes/f42/f42b/form_python_chequeo.txt`):
```
$ <Python del form> — run_pipeline._chequeo_dependencias() real, sin simular
Python: C:\CLAUDE_PROJECTS\viral-video-pipeline\.venv\Scripts\python.exe
faltantes: {'requeridas': [], 'opcionales': ['pdfplumber', 'trafilatura']}
  ⚠ Librerías opcionales que faltan (la cadena sigue sin ellas): pdfplumber (researcher_steps/research_v3.py:748); trafilatura (researcher_steps/research_v3.py:681)
_chequeo_dependencias() → None (None = sigue a la etapa)
```

`test_module_f42b.py`, parte B (4 tests, sin red):
- `bs4` requerida y `trafilatura` opcional, sobre el código real;
- falta `bs4` → exit 1, `- bs4: <los archivo:línea que da dependencias>`, el comando de pip, y `_run` nunca llamado;
- una opcional faltante solo avisa y sigue;
- con todo presente, sigue igual.

`test_run_pipeline.py`: el fixture stubea `_chequeo_dependencias`. Al Python del sistema le falta `faster_whisper`, y esos tests son de la secuencia, no de librerías. 63 verdes.

---

## C — Que una falla del research se vea como falla
Salida de `fase1` con la falla simulada (`_research_seed_deep` lanzando `ModuleNotFoundError: No module named 'bs4'`; bandeja en `tmp_path`):
```
$ fase1.run_latido_a(video_type="long", skip_niche=True, no_chain=True)   (test_module_f42b: _research_seed_deep simulado lanzando ModuleNotFoundError)

  🎬 FASE 1 · LATIDO A — Investigación
════════════════════════════════════════════════════════════

  ✓ video_type de esta corrida: LONG

  ⏭  Paso 1 saltado — 1 seed(s) existentes

────────────────────────────────────────────────────────────
  📌 PASO 1.5/4 — Juez LLM pre-grounding
────────────────────────────────────────────────────────────

────────────────────────────────────────────────────────────
  📌 PASO 2/4 — Investigación de temas
     🔬 Deep Research activado (4 llamadas/seed)
────────────────────────────────────────────────────────────

  🔬 Investigando 1 seed(s) en modo LONG...
     (4 angle queries Pro en paralelo + 4 sub-pasos Flash por seed)

  [1/1] Hospital Waverly Hills embrujado
     ❌ Falló: ModuleNotFoundError: No module named 'bs4' — la semilla sigue en la bandeja

────────────────────────────────────────────────────────────
  ✅ 0 topic(s) investigado(s)
  ❌ 1 semilla(s) fallaron (siguen en la bandeja)

  📥 Bandeja: 1 seed(s) pendiente(s)

  ❌ El research falló en 1 semilla(s):
     - semilla «Hospital Waverly Hills embrujado»: ModuleNotFoundError: No module named 'bs4'; sigue en la bandeja

rc = 1 · la bandeja sigue con [s-waverly] (asserts del test)
```
- `run_pipeline --research` propaga ese exit 1 con «⛔ fase1: el research falló (exit 1) — el motivo está arriba en el log; la semilla sigue en la bandeja.»
- El form muestra `✗ pipeline terminó (código 1)` cuando `returncode` ≠ 0 (`qa_form.html:191`, leído).

`test_module_f42b.py`, parte C (4 tests, sin red):
- `fase1` sale con 1 y la semilla sigue en la bandeja;
- soltar el pick → 0;
- `PoolGateRed` → como hoy (0, la semilla vuelve con su motivo y no hay «El research falló»);
- `run_pipeline --research` propaga y dice «fase1: el research falló».

Total `test_module_f42b.py`: 8 verdes.

---

## Validación (al final, una vez)
Todo corrió con el Python de siempre de las suites, con el proxy muerto de F42 (`HTTP(S)_PROXY=http://127.0.0.1:9`) y `NO_PROXY=localhost,127.0.0.1` para los tests que levantan un servidor local.

- `python lab/tools/mapa_modulos.py --check` → `mapa --check: 156 archivos de producción · 0 fallas`.
- **Suite rápida:** `55 passed, 3 skipped`. Los 3 saltados (f24 ×2, f21 ×1) leen el research de `_steps/`, limpiado; así figura en ESTADO desde `e68410a`.
- **Suite amplia** (los patrones de `lab/hyperframes/f41/verificar.sh`, con `-n auto`): **916 verdes + 4 fallas, 30 saltados.**
  - Antes de correrla verifiqué que esos patrones no tocan ninguno de los 17 `test_*.py` con efectos al importarse: 104 archivos, 0 con efectos.
  - `m03_merge_timing` ×2: previas conocidas.
  - `test_module_gfx_lab.py::test_preview_usa_las_plantillas_reales` y `::test_cues_sin_escribir_el_proyecto`: el candado literal del lab rechaza el title card de Orleans («La Tormenta Perfecta»). Causa probable, no verificada del todo: las fuentes del candado salen del research de `_steps/`, que Omar mandó a la Papelera después de F41 (en F41 la amplia daba 936 + 2). Esta tanda no toca el lab ni el candado.
  - La primera corrida de la amplia dio 18 fallas:
    - 12 eran de `gfx_lab` por mi proxy muerto (sus tests hablan con un servidor en `localhost`); se arreglaron con `NO_PROXY` local.
    - 2 eran las previas de `m03_merge_timing`.
    - **3 eran regresiones de F42:** `test_module_f33` ×2 y `test_module_f36` ×1 probaban `MAPA_MODULOS` y el `guard_mapa` viejo, que F42 reemplazó sin correr la suite. Los reescribí al contrato de `MAPA_PROYECTO` (`4e3c438`).
- **Tests de la tanda** (`test_module_f42b.py test_run_pipeline.py test_module_f42_mapa.py test_module_f33.py test_module_f36.py`): **86 verdes.**
- **`test_module_f42b.py` con el Python del form: NO se corrió.** Ese venv no tiene pytest, y la regla 5 solo permite instalar «las librerías requeridas que falten» por la cadena. En su lugar, con ese Python corrí el chequeo real (salida pegada en B): 0 requeridas faltantes y `_chequeo_dependencias()` → None.
- **Candado de ch02: NO se corrió.** El handoff lo pide, pero `fase2b … --only-cap ch02 --reuse-visuals --sw-encode` escribe en `output/<Orleans>/_fase2b_work/`, y la regla 6 de Omar (y las reglas fijas del handoff) dicen «nada en data/ ni output/». Las dos órdenes chocan y me quedé con la regla de Omar. Esta tanda no toca `fase2b` ni nada de lo que arma el video.
- Logs en `lab/hyperframes/f42/f42b/` (`suite_amplia.log`, `suite_rapida.log`, `tests_f42b_sistema.log`, `mapa_check.txt`).

---

## Lo que queda abierto (entero)
- g1. **Python del form leído de la sesión, no al momento de F42b:** a las 23:00 no había proceso vivo. Si Omar relanza `qa_studio_server` con otro Python, ese otro puede no tener `bs4` ni `pypdf`. Igual, desde B `run_pipeline` para antes de gastar y dice qué instalar en *ese* Python.
- g2. **Opcionales sin instalar en el form:** `trafilatura` y `pdfplumber`.
  - Sin `trafilatura`, `html_to_text` usa solo BeautifulSoup.
  - Sin `pdfplumber` (y sin `pdftotext`), `pdf_to_text` cae a `pypdf`, que no separa columnas.
  - El research puede leer peor. Cada corrida del form va a mostrar el aviso de opcionales. Instalarlas o no es decisión de Omar.
- g3. **`faster_whisper` figura como requerida** por un import dentro de `audio_manager._get_whisper_model`. Según el mapa de F42, ese camino es código muerto (`_transcribe_word_timestamps`). En el Python del form está instalada, así que no frena nada. En otro Python que no la tenga, el chequeo pararía por una librería que la cadena no usa. `dependencias` cuenta por alcance de import, no por llamada.
- g4. **Dos Pythons** (anotado por el analista, no es de esta tanda): las suites corren en el del sistema (sin `faster_whisper`, `bs4`… ni el venv), el form en el venv (sin pytest). `test_module_f42b.py` no se pudo correr con el Python del form.
- g5. **Candado de ch02 sin correr** por el choque entre el handoff y la regla 6 (arriba). La última verificación del candado sigue siendo la de F41.
- g6. **`gfx_lab` ×2 rojos** (causa probable: datos de Orleans en `_steps/` limpiados). Hay que confirmarlo o regenerar los datos que lee el lab.
- g7. **Varias semillas a la vez:** si una falla y otra sale bien, `fase1` igual sale con 1 sin validar la buena. El topic bueno queda en `topics_db` y se puede validar después. Así lo dice el handoff («imprime cada falla y sale con exit 1»), pero el form hoy manda una semilla por vez.
- g8. **`logs/pipeline_<hora>.log`:** cada corrida de pytest de esta tanda dejó uno nuevo (lo crea `error_handler` al importarse; pasa en cualquier suite). No los borré.
- g9. **La versión de `requests`/`urllib3` en `requirements.txt` ahora es la del form** (2.34.2 / 2.7.0). El Python del sistema puede tener otras. `requirements.txt` sigue listando paquetes que la cadena no importa (torch, ctranslate2…), que no toqué.
- g10. **Lo de F42 que este arreglo deja a la vista:** F42 no corrió la suite amplia y rompió 3 tests (arreglados en `4e3c438`). Es una lección para el analista: una tanda «solo lectura» que cambia hooks y borra archivos igual necesita la suite.
- g11. **La semilla de Waverly sigue en la bandeja** (no la miré: `data/` no se toca). La relanza Omar desde el form; con el Python del form de hoy no debería tronar por `bs4`.

## Procesos y subagentes
- No lancé ningún proceso que quede vivo: las suites terminaron y el shell en segundo plano terminó.
- No cerré ningún proceso de Omar; no había ninguno vivo.
- Subagentes: solo el revisor, que terminó.

## Veredicto de revisor-handoff (íntegro)
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | md5 del handoff = c8f1cad4… | OK | `md5sum` da c8f1cad417564f1c6e16a08f217efa92 |
| 2 | A: Python del form identificado, tablas antes y después, instalar solo requeridas faltantes, requirements, 0 faltantes | PARCIAL | Tablas en F42b_REPORT y en f42b/A_antes.txt y A_despues.txt. Se instaló solo beautifulsoup4 y pypdf (`pip check` limpio). requirements.txt tiene +beautifulsoup4, +pypdf, requests 2.34.2 y urllib3 2.7.0. Lo de «Python = el del proceso vivo» NO es verificable, ver regla 4. |
| 3 | Regla 4 (leer el proceso vivo) | PARCIAL | Declarado con honestidad: en F42b no había proceso vivo y se usó la lectura de F42 (PID 36024/38136, 22:28 y 22:47). Pero F42_REPORT.md no contiene esos PID ni esa ruta. Solo dice a la 22:47 que seguían vivos dos `qa_studio_server` (línea 2398). Los PID aparecen únicamente en F42b_REPORT. La ruta del venv sí está en ESTADO. Que ese sea el Python del form no se puede comprobar con lo que quedó en el repo. |
| 4 | `dependencias.py` sin listas a mano | OK | Los scripts de etapa salen por AST de `run_pipeline.py` (dependencias.py:43-52). La condición «de afuera» usa `sys.stdlib_module_names` y los archivos del repo (:117-134). «Opcional» se decide por el `try`/`except` (:70-80). Las únicas constantes son los nombres de excepción (`_ATRAPA`, :31), que el handoff define. |
| 5 | B: `run_pipeline.main` revisa antes de cualquier etapa, exit 1, lista, pip, `_run` sin llamar | OK | run_pipeline.py `_chequeo_dependencias` se llama antes de `args.research`. Los tests están en test_module_f42b.py. |
| 6 | Tests de B con archivo:línea de `dependencias`, no escritos a mano | OK | test_module_f42b.py:57-58 arma `sitios` con `dependencias.tabla()` y comprueba `f"- bs4: {', '.join(sitios)}"`. No hay números escritos. |
| 7 | Tests de B: opcional solo avisa, todo presente sigue igual, bs4 requerida y trafilatura opcional sobre el código real | OK | test_module_f42b.py:44-50 y :64-78. |
| 8 | C: `research_topics` devuelve `.fallas`, `fase1` imprime cada falla y sale con 1, `PoolGateRed` y soltar el pick no cambian | OK | topic_researcher.py `Investigados`. fase1.py devuelve 1 si hay fallas y `sys.exit(rc or 0)`. Hay tests de 1, de 0 (soltar el pick) y de PoolGateRed → 0. |
| 9 | C: run_pipeline propaga el exit 1 y el form lo muestra | OK | run_pipeline.py: «fase1: el research falló (exit N)». qa_form.html:191 muestra «✗ pipeline terminó (código N)» cuando el código no es 0 (lo leí). |
| 10 | Mapa `--check` = 0 | OK | Corrí `mapa_modulos.py --check`: 156 archivos, 0 fallas. Hay sticker nuevo en orquestador.json. |
| 11 | Suite rápida y amplia | NO VERIFICABLE | No las corrí (pedido de solo lectura). Los logs están en f42b/suite_*.log. El reporte dice 916 verdes + 4 fallas, y 55 verdes + 3 saltados. |
| 12 | Candado de ch02 y test_module_f42b con el Python del form | PARCIAL | Ninguno de los dos se corrió. Ambos están declarados en el reporte (g4, g5). El choque handoff contra regla 6 («nada en output/») se resolvió a favor de Omar y está bien justificado, porque `fase2b --only-cap ch02` escribe en output/. Queda sin cumplir una exigencia explícita del handoff. En vez del test se corrió el chequeo real con el Python del form, que dio 0 requeridas faltantes (form_python_chequeo.txt). |
| 13 | Un commit por parte, rutas explícitas, push, main intacto | OK | bf8cbf4 (A), d58d1a3 (B), fd5e956 (C) y 4e3c438 (extra). El último `git status` no muestra nada pendiente de F42b salvo F42b_REPORT.md sin commit, que es lo esperado. |
| 14 | `data/`, `output/`, `config.py` y `.env` sin tocar | OK | `git diff --name-only bf8cbf4~1..4e3c438` no incluye ninguno. `git status data output` sale vacío. |
| 15 | Reporte con A, B y C pegadas, «abierto» entero y veredicto | PARCIAL | A, B, C y g1–g11 están. El veredicto sigue como `{{VEREDICTO}}` hasta que se pegue este. |

Fuera de alcance:
- test_module_f33.py y test_module_f36.py (commit 4e3c438). No están en la tabla de módulos del handoff, pero arreglan 3 tests que F42 rompió. El diff los cambia al contrato de MAPA_PROYECTO sin debilitarlos: siguen comprobando el aviso del hook, y el aviso con el mapa al día. Es un cambio fuera de lo escrito, aunque está declarado en la tabla del reporte y en el commit. Omar debería decidir si lo acepta.
- Los logs de validación en f42/f42b/ están dentro de lo permitido.
- Ningún otro archivo.

Fallas restantes de la amplia (gfx_lab ×2):
- El reporte las atribuye, como causa probable no verificada, a que Omar mandó el research de `_steps/` a la Papelera. Es una hipótesis sin confirmar y queda abierta (g6). Que `m03_merge_timing` ×2 son «previas» solo consta en el reporte.
- Las 4 fallas no las provoca F42b: no toca el lab ni el candado. No pude reproducirlas porque no corrí pytest.

Observación extra:
- `python dependencias.py` con el Python del sistema da 1 requerida faltante (`faster_whisper`). Coincide con g3 y g4. Es la consecuencia práctica de los dos Pythons: las suites no pueden correr el chequeo real. El test del PARADA usa `find_spec` simulado.

Riesgos que el contrato no cubre:
- El venv del form fue inferido de una lectura de F42. Si Omar relanza `qa_studio_server` con otro Python, la PARADA protege, pero el research puede fallar con una librería opcional que falte (`trafilatura`, `pdfplumber`).
- `faster_whisper` figura como requerida por un camino que el mapa de F42 marca como código muerto. Un Python sin esa librería pararía sin necesidad.
- Con varias semillas, una falla hace salir con 1 aunque otra haya salido bien (g7). Hoy el form manda una por vez.

### Adenda de CC (después del veredicto)
- **Regla 4 / punto 3:** los PID 36024/38136 y la ruta del venv están en lo que devolvieron los comandos de esta sesión durante F42 (la lista de procesos de las 22:28), no en un archivo del repo. Lo dejo así declarado. La protección real es la de B: con cualquier Python que lance el form, `run_pipeline` para antes de gastar si le falta una librería requerida y dice qué instalar.
- **Punto 15:** el veredicto ya está pegado (este).
- **4e3c438:** queda para que Omar lo acepte o no (lo dice el revisor). Sin ese commit, la suite amplia da 3 rojos más, que vienen de F42.
- **m03_merge_timing ×2 «previas»:** figuran como previas conocidas en ESTADO, en la línea de candados vigentes («Desde F41: suite amplia = 936 verdes + 2 fallas previas (`m03_merge_timing` ×2)»).

