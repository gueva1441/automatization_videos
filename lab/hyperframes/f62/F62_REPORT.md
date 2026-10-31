# F62 — objetos de época: el canon nombra vehículos y aparatos por modelo concreto

Rama `f11-guion-v4` · 2026-10-30 · Parte 1 = Etapas 0 y A del handoff `HANDOFF_F62_objetos_de_epoca.md` (md5 8a346945353429af35e118da0d76046c, verificado); las Etapas B, C y D NO se corren (pedido del analista). Parte 2 = producción de Wittenoom hasta fotos y clips en QA Studio.

## Parte 1 — Etapa 0 (registro e impacto, US$ 0)

### 0.1 DECISIONES.md
Las 3 líneas del handoff (23:16, 23:18, 23:23) agregadas tal cual, como ítems `- …`, CRLF (204 saltos, 204 CRLF).

### 0.2 Lectores de `vehicles_machinery` / `technology` — confirmado con grep (subagente, solo lectura)
| lector | qué hace | filtra/compara |
|---|---|---|
| `script_engine/m03_visual.py:388-403` `_lineas_epoca` | imprime las 4 líneas clothing/technology/vehicles_machinery/interiors por period en el pedido de m03 (`_format_seedream_canon_block` l. 441); `_periods_del_cap`/`_tramo` parsean solo `years` | no (muestra) |
| `script_engine/m03_visual.py:208` | prosa del SI «ERA FIELDS ON DEMAND» (nombra las claves) | no |
| `script_engine/m06_classifier.py:141-149` `_load_topic_facts` | copia la `era_visual_canon` entera (l. 146) y la vuelca con `json.dumps` (l. 255) | no (copia) |
| `researcher_steps/step_4e_visual_canon.py:452-453, 483-492, 735, 788` | escritor: `_ERA_REQUIRED_KEYS`, `PERIODO_CAMPOS`, `_clean_era_canon` aplana a string y `strip()` | no (normaliza) |
| `m03_imagenes_v3.py:73`, `m05_judge.py:412-417`, `foto_madre.py:147,181,211`, `fase1_5.py:310` | solo `spans`/`primary_decade`/campos sourced/`periods[].years` | no los leen |
| tests | `test_module_05.py:1287-1288` y `test_module_f50d.py:30-36,53-58` fixtures; `test_module_f50d.py:67-80` compara el texto que imprime `_lineas_epoca`; `test_module_m03_reglas_133.py:45` (no listado por el analista) comprueba que las palabras estén en el SI de m03 | no |
| lab | `lab/hyperframes/f51b/tabla_f51b.py:87-95,118-121` compara con `==` viejo vs nuevo para un informe de diferencias (script de informe, no del pipeline) | sí, fuera del pipeline |

**Sin PARÁ**: ningún lector de producción filtra ni compara esos textos.

### 0.3 Tests que fijan la regla 2
grep de «Rolex», «más genérico», «ampliamente documentado», «genérica de la década», «genéricos de la década», «vacuum tubes», «rotary dials» en `test_*.py` (raíz y lab): 0 hits (los únicos están en scripts `_lab_4e_visual_canon*.py`, sin tildes). `test_module_f50d.py:15-26` y `test_module_f60_a3.py:72-77` verifican otras subcadenas del pedido; `f50d:41-47`, `f50f:38`, `f50a:56` recalculan la marca (sin hash fijo). **Ninguno se rompe.**

## Parte 1 — Etapa A (código)

### A.1 `researcher_steps/step_4e_visual_canon.py` l. 222-226 (regla 2, byte a byte)
```
-   persona: mantené genérico y ampliamente documentado. NO inventes un detalle
-   específico no verificable (ej: "the captain wore a Rolex"). Si dudás entre 2
-   versiones, el más genérico. El detalle de un individuo nombrable vive en
-   documented_people, NO acá.
+   persona: lo ampliamente documentado de la época. NO inventes un detalle de un
+   individuo no verificable (ej: "the captain wore a Rolex"); el detalle de un
+   individuo nombrable vive en documented_people, NO acá. En technology y
+   vehicles_machinery (también los de cada period), cada vehículo, máquina o
+   aparato va con el modelo o tipo concreto de uso común donde ocurre la escena
+   (si el tramo tiene escenas en más de un país, uno por país) y en ESE tramo,
+   con el rasgo visible que lo fecha (ej: "black Bakelite rotary-dial telephone",
+   NO "a telephone"; "Bedford OB coach with a rounded bonnet", NO "a bus"): el
+   tipo genérico solo, el motor de imágenes lo pinta moderno. Sin logotipos ni
+   texto pintado.
```
(la primera línea del bloque, «2. CAPA ÉPOCA-GENÉRICA (clothing, technology, vehicles, interiors) y CUALQUIER», no cambia)

### A.1b Los tres reemplazos chicos (byte a byte; los ANTES coincidieron)
```
- DOS CAPAS, no las mezcles. La capa ÉPOCA es genérica de la década; la capa
+ DOS CAPAS, no las mezcles. La capa ÉPOCA es de la década; la capa
- Sub-campos de ÉPOCA (genéricos de la década, derivados de los facts/contexto):
+ Sub-campos de ÉPOCA (de la década, derivados de los facts/contexto; vehículos y aparatos con modelo concreto, ver regla 2):
-   Ej: "analog gauges, vacuum tubes, rotary dials. NO LEDs, NO digital displays."
+   Ej: "black Bakelite rotary-dial telephones, valve radios, analog gauges. NO LEDs, NO digital displays."
```
Diff total: `step_4e_visual_canon.py` +13/−7 (LF conservado). Nada más tocado: `m03_visual.py`, `m03_imagenes_v3.py`, `foto_madre.py`, `anachronism_blocklist`, `forbidden_anachronisms`, BLOQUE 4 y las demás reglas del pedido, intactos. Ninguna constante nueva. Consecuencia declarada: `marca_canon` incluye el pedido → cualquier tema rehace su canon en su próxima corrida (Wittenoom lo hace en la Parte 2).

### A.2 Test nuevo `test_module_f62.py` (3)
`pedido_canon` con topic y ficha mínimos: contiene «modelo o tipo concreto de uso común», «Sin logotipos ni texto pintado» (el pedido envuelve a 80 columnas; se compara con espacios normalizados) y los dos ejemplos; no contiene «mantené genérico», «el más genérico», «genérica/genéricos de la década» ni el ejemplo viejo de technology; conserva «the captain wore a Rolex» y «documented_people, NO acá»; la marca cambia con el pedido. Con f50d, f50f, f60_a3, f50a: 39 passed.

### A.3 Suites (`lab/hyperframes/f41/f62/`)
ch02 md5 `f792f3d483a1fa42daed5f7f0e054f46` (candado) · rápida 53 passed, 3 skipped · amplia **1337 passed**, 31 skipped, 3 xfailed, 4 failed = las 4 previas (`m03_merge_timing` ×2, `gfx_lab` ×2; no son regresión: las mismas desde F60a). Sticker de `step_4e_visual_canon.py` (zona research) actualizado; MAPA 158 archivos · 0 fallas.

### Veredicto de revisor-handoff — Parte 1, Etapas 0 + A (íntegro)

**VEREDICTO: CUMPLE CON OBSERVACIONES** (solo Etapas 0 y A; B, C y D no revisadas por pedido)

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | md5 del handoff | OK | `md5sum` da 8a346945353429af35e118da0d76046c |
| 2 | 0.1 Tres líneas en DECISIONES.md, tal cual, CRLF | OK | `git diff` muestra +3 líneas, todas con `^M$`. El texto coincide con el handoff §0.1. En la tercera comparé el texto completo y las dos primeras las leí truncadas. |
| 3 | 0.2 Lectores confirmados con archivo:línea; ninguno de producción filtra ni compara | OK | F62_REPORT §0.2 lista `m03_visual:388-403`, `m03_visual:208`, `m06_classifier:141-149` y los demás. Re-grepeé `vehicles_machinery` y `technology` en `.py` fuera de lab y tests. Solo aparecen `step_4e` (esquema y normalización), `m03_visual:208/389-394` (muestra) y `foto_madre:167` (texto fijo, no lee el campo). `m06` copia la era entera. El único comparador es un script de informe de lab (`f51b`), fuera del pipeline. |
| 4 | 0.3 Ningún test fija la regla 2 | OK | grep de «Rolex», «más genérico», «ampliamente documentado» y «mantené genérico» en `test_*.py`: el único archivo con hits es `test_module_f62.py`, el test nuevo. |
| 5 | A.1 Bloque DESPUÉS byte a byte | OK | El `+` del `git diff` de `step_4e_visual_canon.py` (hunk de la regla 2) coincide línea por línea con el DESPUÉS del handoff. El ANTES coincide con los `-`. |
| 6 | A.1b Los tres reemplazos exactos | OK | El diff muestra las líneas 166, 169 y 177 exactamente como pide el handoff. |
| 7 | Solo eso en `step_4e` y nada más tocado | OK | El diff de `step_4e` tiene +13/−7 y solo esos 4 hunks. `m03_visual`, `m03_imagenes_v3`, `foto_madre`, `anachronism_blocklist`, `forbidden_anachronisms` y BLOQUE 4 no están en `git diff`. Ninguna constante nueva. |
| 8 | A.2 Test `test_module_f62.py` | OK | Verifica las dos frases pedidas y que no estén «mantené genérico» ni «el más genérico». Además cubre los dos ejemplos, A.1b, la conservación de «Rolex» y que `marca_canon` cambie. |
| 9 | A.3 Suites | OK | Leí los logs en `lab/hyperframes/f41/f62/`. Rápida: 53 passed, 3 skipped. Amplia: 1337 passed y 4 failed, que son `m03_merge_timing` ×2 y `gfx_lab` ×2, las 4 previas. El log ch02 muestra md5 f792f3d4…, igual al candado. No re-corrí las suites. |
| 10 | Efecto de `marca_canon` declarado | OK | F62_REPORT dice que cualquier tema rehace su canon en la próxima corrida. El handoff lo exige y un test lo cubre. |
| 11 | Sticker y MAPA | OK | `research.json` actualizado con md5 nuevo. `MAPA_PROYECTO.json` pasa de `tests: 5` a `6`. |

**Fuera de alcance:** ninguno de código. Hay cambios en archivos de estado y lab:
- `diag_234_cap4.py`
- `lab/hyperframes/f28/a/f28a.log`
- `lab/MAPA_PROYECTO.*`
- `lab/mapa/stickers/research.json`
- `lab/hyperframes/f62/`
- `lab/hyperframes/f41/f62*`
- `test_module_f62.py`

El diff de `diag_234_cap4.py` y el de `f28a.log` ya aparecían como modificados en el `git status` inicial, antes de F62. No los atribuyo a F62.

**Observaciones:**
1. La frase «Sin logotipos ni texto pintado» cruza un salto de línea en el pedido, y el test normaliza espacios con `" ".join(split())`. Lo juzgo aceptable: el pedido real conserva el texto byte a byte y el test no relaja el contenido, solo el ajuste de líneas.
2. El MAPA regeneró también las filas de `m03_imagenes_v3` y `m03_visual`. Son cambios del campo `ultimo`, de «F59/F60» a «F61», y no tocan el código de esos módulos. Es ruido del generador, aunque esos dos archivos aparecen en el diff del MAPA.
3. El reporte dice «LF conservado» y git avisa que convertirá a CRLF al tocarlo. El archivo ya era LF en HEAD, así que no hay cambio de saltos de línea. El riesgo es solo cosmético.
4. El reporte llama a la 0.2 «confirmada por subagente». No re-ejecuté el grep de `m05_judge` ni `fase1_5`. Revisé en el reporte las líneas que los citan.

**Riesgos que el contrato no cubre:**
- La regla 2 también deja de empujar a lo genérico en `clothing`, `interiors` y personas. El handoff lo declara y B.2 no lo mide.
- El canon se rehace en cualquier tema, no solo en Wittenoom. Un canon nuevo cambia sus prompts aguas abajo, sin medición previa fuera de Wittenoom.
- «Modelo concreto sin búsqueda web» depende de que Opus no invente modelos falsos de época. Eso solo se puede verificar en B.

#### Adenda de CC
- **Obs. 2:** el MAPA se regenera entero con `mapa_modulos.py`; las filas de m03 cambiaron `ultimo` a F61 porque el generador lo lee del historial. Sin efecto en código.
- **Riesgos:** los tres son los que el handoff declara como consecuencias; B (medición en texto) era la etapa que los acotaba y no se corrió por pedido del analista. La primera corrida de producción con el canon nuevo (Wittenoom, cuando Omar apruebe el papel) va a ser la primera medida real: el reporte de esa corrida tiene que pegar `vehicles_machinery`/`technology` por period.

## Parte 2 — producir Wittenoom (`123bbb64-9fca-4395-8bf4-57d60e219ef1`) hasta fotos y clips: **PARÁ en la compuerta del papel**

### Cómo retoma la cadena este topic (leído antes de correr nada)
- `run_pipeline.etapa_de(tid)` → **«papel»** («el papel no está aprobado»): `_paso_papel` abriría la compuerta interactiva del papel (Omar) y no correría nada más. Si el papel estuviera aprobado, `etapa_de` daría «assets» (existen `data/scripts/<tid>.json` del 28-oct y `output/<tid>/assets/assets_manifest.json`) y **saltaría la voz y m03** (los cree hechos); además, con `status = video_generated` y el papel viejo, caería en `cadena_vieja`. Por eso la voz y m03 van forzados por `fase1_5` directo, no por `run_pipeline`.
- `fase1_5.py --topic <tid> --from audio --batch --no-music-gate` correría: **papel (compuerta) → audio** (`audio_manager.process_script(skip_if_exists=True)`: con los mp3 del 28-oct en `output/audio/<tid>/` **reutilizaría la voz vieja** → para forzar la voz nueva hay que apartar esa carpeta a un respaldo antes, sin tocar `_steps`) **→ m07** (music_map) **→ asegurar_canon** (la marca cambió con el pedido F62 → rehace el canon con Opus y lo escribe en topics_db y `_steps/05_visual_canon.json`) **→ m03** (anclas de la voz nueva; pisa `_steps/03_visual.json` del 29-oct 13:00) **→ paso0** (madre del sujeto: `output/<tid>/foto_madre/subject.png` existe → adopción; madres por persona nuevas, Seedream por la cola) **→ assemble** (pisa el guion vivo `data/scripts/<tid>.json`). Salta m01a, m01b y normalizer_gate (research, ficha, escaleta, guion y papel no se re-pagan).
- `fase2a.py --topic <tid>`: con `--topic` no filtra por `status`; LONG → usa el sync_map nuevo; paso0 otra vez (idempotente); `asset_manager.process_script` → pre-paso de secuencia + 96 fotos + 2 clips (Gemini Omni Flash → Kling, foto final F57); como `output/<tid>/assets/` ya tiene las fotos viejas, **las saltaría (`skipped_exists`)** → hay que apartar `assets/` a un respaldo antes; marca `assets_rendered`.
- Guion de pantalla y render: no se corren.

### Lo que pasó
`python fase1_5.py --topic 123bbb64-… --from audio --batch --no-music-gate` (US$ 0):
```
⏸  PARADA del papel: el papel no está aprobado.
   Leer: data\scripts\_stepsSbbb64-9fca-4395-8bf4-57d60e219ef1e_pantalla.md
   Aprobar: python fase1_5.py --topic 123bbb64-9fca-4395-8bf4-57d60e219ef1 --aprobar-papel "Omar <fecha>"
```
`fase1_5.process_topic` (l. 567-573, F39 §A.4, DECISIONES 2026-10-26 19:54): «nada después de m01b (la voz se paga) sin el papel aprobado y vigente; vale también al reanudar (--from normalizer_gate / audio / m07 / m03)». El papel vigente es el del guion nuevo (`01e_pantalla.md`, 29-oct 20:58; 11 fichas, 6 sellos, 3 relojes, 56 descartados, con avisos «pico sin ficha» en ch03 beat 5) y `01e_pantalla.json` no trae `aprobado`. Aprobarlo es decisión de Omar (es él quien lee el papel): CC no lo aprueba en su nombre ni rodea la compuerta llamando los pasos a mano. **PARÁ**: voz, canon, m03, madres, fotos y clips no se corrieron; nada de producción cambió (`_steps`, topics_db, guion vivo, `output/<tid>` con mtimes anteriores a hoy; `data/cost_history.json` sin entradas nuevas de esta parte).

### Qué hace falta para seguir (cuando Omar esté)
1. Omar lee `01e_pantalla.md` y aprueba: `python fase1_5.py --topic 123bbb64-9fca-4395-8bf4-57d60e219ef1 --aprobar-papel "Omar 2026-10-31"`.
2. Apartar la voz vieja y las fotos viejas (respaldo, no borrado): `output/audio/<tid>/` → `output/audio/<tid>_antes_F62/` y `output/<tid>/assets/` → `output/<tid>/assets_antes_F62/` (el `_final.mp4` y `_fase2b_work` del video viejo quedan).
3. `python fase1_5.py --topic <tid> --from audio --batch --no-music-gate` (voz nueva → m07 → canon F62 → m03 → madres → assemble; pegar en el reporte `vehicles_machinery`/`technology` por period del canon nuevo).
4. `python fase2a.py --topic <tid>` (secuencia + fotos + clips) y `python qa_studio_server.py --topic <tid>` para verlo.
Costo esperado de 3 y 4: canon ≈ US$ 0,35, m03 ≈ 2,3, voz (ElevenLabs, 7 caps), madres 8 × 0,035, fotos 96 × 0,035 ≈ 3,4, 2 clips (Gemini/Kling) — se informa al correr.

