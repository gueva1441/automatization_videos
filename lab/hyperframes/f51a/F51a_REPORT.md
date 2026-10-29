# F51a — el armado C del prompt de foto pasa a producción (y se borra el viejo) · PARADA

Handoff `lab/hyperframes/f51a/HANDOFF_F51a_C_a_produccion.md`, **md5 `b4f0879876f38898740e0503f91b7da3`** (coincide con el del pedido).
- Rama `f11-guion-v4`. **US$ 0**: sin fal y sin LLM.
- No se escribió `03_visual.json`, ni el canon, ni topics_db. No se tocaron `name_matching`, el corte Veo, `anio_final` ni `cost_tracker`.

## Qué pasó, en llano
- `armar` (en `script_engine/m03_imagenes_v3.py`) arma ahora C, el armado corto de F50h: sujeto · aspecto · lugar+año · cartel · luz · plano · una oración de estilo con el año · cierre.
- Se borraron `style_head`, `STYLE_TAIL` y las partes mirada, objeto y paleta.
- **Contrato: 20/20 byte a byte iguales a `PROMPTS_F50h.json → C`.**
- Wittenoom rearmado en seco: cambian las 96 fotos; la mediana de palabras baja de 157.5 a 122.5. No se escribió nada: eso es F51d.

## Commits
| etapa | commit |
|---|---|
| 0 | `0fdeee4` |
| 1 | `6817e7a` |
| 2 | `c93428a` |
| reporte, ESTADO y logs de verificación | este commit |

## Etapa 0 — DECISIONES
- md5 del handoff: `b4f0879876f38898740e0503f91b7da3`.
- Las 2 líneas se agregaron al final con CRLF. Antes, el código comprobó que cada una está dentro del handoff y que no estaba ya en DECISIONES.
- `tail -2 DECISIONES.md`:
```
- 2026-10-29 00:07 · **Court:** el borrado de nombres de `name_matching.scrub_documented_names` que rompe 6/3 y 7/11 se QUITA, no se le agregan reglas (se hace en F51c) · Omar · F50g-B
- 2026-10-29 03:23 · **F51:** a) el armado C de F50h va a producción y se borran del armado la mirada, el objeto, la paleta, style_head y STYLE_TAIL con sus tests; b) el estilo por época (C+ép) no, por ahora; c) el canon separa el aspecto fijo (piel, pelo, ojos, complexión) del estado (polvo, enfermedad) y el código pega solo el fijo · Omar · F51
```

## Etapa 1 — `armar` = C
**Código** (`script_engine/m03_imagenes_v3.py`):
- Partes, en este orden: `sujeto`, `aspecto`, `lugar_anio`, `texto`, `luz`, `tecnica`, `estilo`, `cierre`.
- `sujeto`, `aspecto`, `lugar_anio`, `texto`, `tecnica` y `cierre` quedan con el mismo código de antes.
- `luz` = `oracion(lighting)`. Las cláusulas negadas ya salen antes, porque `lighting` sigue en `_PROSA`.
- `estilo` = `ESTILO_C.format(anio=anio)`. `ESTILO_C` es la constante nueva, con el texto exacto de `f50h.py` l. 40.
- Se borraron `style_head`, `STYLE_TAIL`, las partes `mirada` y `objeto`, y `color_palette` en `luz`.
- `_PROSA` ya no tiene `gaze_interaction`, `props_detail` ni `color_palette`.
- Docstring actualizado. `m03_visual.py` no se tocó.
- Sticker de `m03_imagenes_v3.py` actualizado (zona `fase2a`), y MAPA_PROYECTO regenerado: `mapa --check: 157 archivos de producción · 0 fallas`.

**`grep` antes de borrar** (todo el repo, `lab/` incluido):
- Producción: `style_head` y `STYLE_TAIL` solo aparecían en `m03_imagenes_v3.py`. Las partes `mirada` y `objeto` no se leen en ningún otro módulo de producción. El único que llama a `armar` en producción es `m03_visual.py` l. 692, y usa solo `armado["prompt"]`.
- `lab/` (se dejó como está):
  - `lab/hyperframes/f46/f46_corridas.py` l. 224 llama a `v3img.style_head(anio)`;
  - `lab/hyperframes/f46/f46b/f46b_corridas.py` l. 311 llama a `v3img.style_head` y `v3img.STYLE_TAIL`;
  - esos dos scripts ahora fallarían al correrse. Las corridas de F47 y F48 importan `f46b.armar`, así que también.
  - `lab/hyperframes/f50h/f50h.py` (`armar_c`) solo lee las partes que siguen existiendo: sigue funcionando.
  - `lab/mapa/hechos.json` todavía lista `style_head` como función (es el digest de F42, no se regenera en esta tanda).
- Tests: `test_module_f8.py`, `test_module_f50b.py`, `test_module_f50g.py`.

**Tests:**
- `test_module_f8.py`: `test_estilo_en_el_medio_del_armado` pasa a `test_estilo_antes_del_cierre`, con el orden C y `ESTILO_C`. En `test_render_v3_usa_beats_estilo_y_reglas`, `head` pasa a ser `ESTILO_C` con el año.
- `test_module_f50b.py`: `test_armado_en_el_orden_medido` pasa a `test_armado_en_el_orden_c`; además comprueba que no queden mirada, objeto ni paleta.
- `test_module_f50g.py`: `test_f50g_a_un_grupo_va_entre_sujeto_y_mirada` pasa a `..._entre_sujeto_y_lugar`.
- No había tests que solo probaran `style_head` o `STYLE_TAIL` sin el armado: no se borró ninguno entero. Los asserts sobre ellos se reescribieron a `ESTILO_C`.
- `test_module_f51a.py` (nuevo, 3 tests):
  - el orden C, con un cartel y un grupo, contra el prompt entero;
  - `style_head`, `STYLE_TAIL` y los 3 casilleros fuera de `_PROSA`;
  - el contrato 20/20 (se salta si faltan los datos de Wittenoom).
- Corrida puntual: `test_module_f51a.py test_module_f8.py test_module_f8b.py test_module_f50b.py test_module_f50g.py test_module_f50c.py test_module_134d_place.py` → `81 passed`.

**Contrato:**
- Script: `lab/hyperframes/f51a/contrato.py`.
- Usa el `armar` de producción y el post-proceso de producción, vía `f50g/rearmar.rearmar_una`: `f8_backstop` y luego `_sacar_frases_con_texto`, lo mismo que `m03_visual` l. 692–696.
- Corre sobre el `raw_llm_prompt` de las 20 fotos en el 03_visual.json vivo, con los grupos del topic.
- Compara byte a byte (`encode("utf-8")`) con `PROMPTS_F50h.json → fotos[i]["C"]`.
- Salida de `python lab/hyperframes/f51a/contrato.py` (exit 0):

| foto | igual |
|---|---|
| 1/2 | sí |
| 1/3 | sí |
| 1/4 | sí |
| 2/9 | sí |
| 2/11 | sí |
| 2/15 | sí |
| 3/3 | sí |
| 3/6 | sí |
| 3/10 | sí |
| 4/1 | sí |
| 4/11 | sí |
| 4/12 | sí |
| 5/1 | sí |
| 5/8 | sí |
| 5/13 | sí |
| 5/16 | sí |
| 6/5 | sí |
| 6/15 | sí |
| 7/7 | sí |
| 7/9 | sí |

**20/20 byte a byte iguales a PROMPTS_F50h.json → C**

### 1/2 entera, armada con el código de producción

```
A Spanish migrant family posed for a portrait: a young olive-skinned miner in a pressed shirt with a bandaged foot, a slim young dark-haired wife in a cotton dress, a few relatives behind them. The family stands squared to the camera for the portrait while the white-bandaged foot sticks out at the front of the group. Spanish Mediterranean people with olive to light skin, dark brown or black hair, dark eyes, slim to medium builds; women and children tanned and dusted red in Wittenoom. Front of a corrugated sheet-metal house with an asbestos-cement wall panel, packed red earth yard, Wittenoom early 1960s. Hard cold overcast daylight, flat and shadowless. Wide shot, eye-level, like a 1960s box camera, deep depth of field, slight film softness at edges. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

### 1/4 entera, armada con el código de producción

```
Wittenoom, the small operating asbestos mining town in the red Pilbara desert. The town sits under drifting dust from the working mill, tipper trucks spreading tailings along the roads. Wittenoom, Western Australia, 1962: inhabited sheet-metal and asbestos-cement houses, red ranges behind, unsealed blue-grey tailings road. The words "WITTENOOM" are written on the roadside town sign in the foreground in painted block letters, in clear crisp lettering. Hard cold overcast daylight, dust haze flattening the distance. Extreme wide shot, high angle from a ridge, deep depth of field, wide lens. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio.
```

## Etapa 2 — en seco sobre todo Wittenoom (sin escribir)
- Script: `lab/hyperframes/f51a/rearmar_todo.py`. Lo escribió un subagente en paralelo; CC lo leyó entero y lo volvió a correr.
- Toma cada foto de `rg.fotos` → `rg.rearmar_una`. «Antes» es el `prompt` guardado; «después», el rearmado.
- Escribe solo `REARMADO_F51a.md`. `git status --short data/ script_engine/` no mostró nada de `data/`.
- Comprobación de CC: el «después» de la 1/2 está, byte a byte, en el C de F50h.
- Salida de `python lab/hyperframes/f51a/rearmar_todo.py`:
```
fotos 96 · por armar 96 · sin armar 0 []
palabras antes med·máx 157.5 · 273 · después 122.5 · 196 · cambian 96/96
vacías o sin sujeto: ninguna
enteros: 1/2 sí · 2 grupos (1, 3) · veo0 (1, 1)
escrito lab\hyperframes\f51a\REARMADO_F51a.md
```

| | antes | después |
|---|---:|---:|
| fotos | 96 | 96 (96 pasan por `armar`; los 2 cuadros veo0 traen `raw_llm_prompt` en `image_f8`) |
| palabras, mediana | 157.5 | 122.5 |
| palabras, máximo | 273 | 196 |
| cambian | — | 96/96 |
| vacías o sin `sujeto` | — | ninguna |

Los 3 prompts enteros, antes y después (copiados de `REARMADO_F51a.md`, que trae también la tabla por foto):

#### Cap 1, foto 2: 1/2

**Antes** (209 palabras)

```
A Spanish migrant family posed for a portrait: a young olive-skinned miner in a pressed shirt with a bandaged foot, a slim young dark-haired wife in a cotton dress, a few relatives behind them. The family stands squared to the camera for the portrait while the white-bandaged foot sticks out at the front of the group. Spanish Mediterranean people with olive to light skin, dark brown or black hair, dark eyes, slim to medium builds; women and children tanned and dusted red in Wittenoom. Everyone faces the camera; the miner's weight leans off the bandaged foot, wife's hand resting on his shoulder, faces sun-lined and dust-dulled. The bright white bandage on the foot at the front edge of the portrait. Front of a corrugated sheet-metal house with an asbestos-cement wall panel, packed red earth yard, Wittenoom early 1960s. Grainy 35mm documentary photograph, 1962, dark-history realism, muted colors, visible film grain, slightly underexposed. 35mm film grain, muted documentary colors. Hard cold overcast daylight, flat and shadowless. Faded sepia family-photo tones over rust-red earth, grey corrugated metal, cold blue-grey shadow. Wide shot, eye-level, like a 1960s box camera, deep depth of field, slight film softness at edges. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

**Después** (159 palabras)

```
A Spanish migrant family posed for a portrait: a young olive-skinned miner in a pressed shirt with a bandaged foot, a slim young dark-haired wife in a cotton dress, a few relatives behind them. The family stands squared to the camera for the portrait while the white-bandaged foot sticks out at the front of the group. Spanish Mediterranean people with olive to light skin, dark brown or black hair, dark eyes, slim to medium builds; women and children tanned and dusted red in Wittenoom. Front of a corrugated sheet-metal house with an asbestos-cement wall panel, packed red earth yard, Wittenoom early 1960s. Hard cold overcast daylight, flat and shadowless. Wide shot, eye-level, like a 1960s box camera, deep depth of field, slight film softness at edges. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

#### Con 2 grupos (spanish_migrant_families, mine_and_mill_workers): 1/3

**Antes** (206 palabras)

```
A young Spanish migrant miner, olive skin sun-darkened, lean muscular build, dark slicked hair, in a dust-caked work shirt and trousers, one foot bandaged. Standing against a sheet-metal wall after a shift, shifting his weight onto the good foot. Spanish Mediterranean people with olive to light skin, dark brown or black hair, dark eyes, slim to medium builds; women and children tanned and dusted red in Wittenoom. Mixed Australian (British-descended) and Southern, Central and Eastern European men, light to olive skin darkened by sun, short hair, lean muscular builds from heavy manual labour, often coated in fine dust. Face turned toward the camera, eyes shadowed by fatigue, shoulders slumped, fine grey dust in the creases of his shirt and skin. A dust-whitened cloth cap held loosely at his side. Beside a corrugated sheet-metal worker house, red Pilbara earth and blue-grey tailings yard, Wittenoom 1962. Grainy 35mm documentary photograph, 1962, dark-history realism, muted colors, visible film grain, slightly underexposed. 35mm film grain, muted documentary colors. Hard cold overcast daylight from one side. Muted rust-red earth, blue-grey tailings, pale grey dust film, desaturated cold tones. Medium shot, eye-level, 85mm lens, shallow depth of field. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

**Después** (162 palabras)

```
A young Spanish migrant miner, olive skin sun-darkened, lean muscular build, dark slicked hair, in a dust-caked work shirt and trousers, one foot bandaged. Standing against a sheet-metal wall after a shift, shifting his weight onto the good foot. Spanish Mediterranean people with olive to light skin, dark brown or black hair, dark eyes, slim to medium builds; women and children tanned and dusted red in Wittenoom. Mixed Australian (British-descended) and Southern, Central and Eastern European men, light to olive skin darkened by sun, short hair, lean muscular builds from heavy manual labour, often coated in fine dust. Beside a corrugated sheet-metal worker house, red Pilbara earth and blue-grey tailings yard, Wittenoom 1962. Hard cold overcast daylight from one side. Medium shot, eye-level, 85mm lens, shallow depth of field. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

#### Veo (rol veo0): 1/1

**Antes** (191 palabras)

```
A young Spanish migrant miner, olive-skinned, slim and wiry, mid-twenties, seated for a family photograph, his foot wrapped in a white bandage. Holding still for the camera while the bandaged foot rests on the red dirt, the asbestos cut beneath it still not closing. Spanish Mediterranean people with olive to light skin, dark brown or black hair, dark eyes, slim to medium builds; women and children tanned and dusted red in Wittenoom. Focus on the bandaged foot; his body sits stiffly upright above it, shoulders drawn in, dust on his trouser cuffs. Faint grey dust and seepage stains on the fabric. Yard of a corrugated sheet-metal worker house in Wittenoom, early 1960s, red earth underfoot. Grainy 35mm documentary photograph, 1962, dark-history realism, muted colors, visible film grain, slightly underexposed. 35mm film grain, muted documentary colors. Hard cold overcast daylight from one side, flat desert glare without warmth. Desaturated sepia-grey with muted rust-red earth, pale grey dust film, cold blue-grey shadows. Close shot, low angle at ground level, shallow depth of field, 85mm lens, background corrugated wall soft. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

**Después** (148 palabras)

```
A young Spanish migrant miner, olive-skinned, slim and wiry, mid-twenties, seated for a family photograph, his foot wrapped in a white bandage. Holding still for the camera while the bandaged foot rests on the red dirt, the asbestos cut beneath it still not closing. Spanish Mediterranean people with olive to light skin, dark brown or black hair, dark eyes, slim to medium builds; women and children tanned and dusted red in Wittenoom. Yard of a corrugated sheet-metal worker house in Wittenoom, early 1960s, red earth underfoot. Hard cold overcast daylight from one side, flat desert glare without warmth. Close shot, low angle at ground level, shallow depth of field, 85mm lens, background corrugated wall soft. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

## Al cerrar — suites y candado ch02
Salida de `bash lab/hyperframes/f41/verificar.sh f51a` (logs en `lab/hyperframes/f41/f51a/`):
```
md5: f792f3d483a1fa42daed5f7f0e054f46 *output/ba6c3cac-a091-41c0-8dad-afd2f4364747/_fase2b_work/ch02_segment_only.mp4
rapida: 55 passed, 3 skipped in 3.35s
amplia: 4 failed, 994 passed, 30 skipped, 4 warnings in 67.75s (0:01:07)
FAILED test_module_gfx_lab.py::test_cues_sin_escribir_el_proyecto - Assertion...
FAILED test_module_m03_merge_timing.py::test_c_guarda_de_minimo - AssertionEr...
FAILED test_module_m03_merge_timing.py::test_c_veo_path_y_veo_anchor_intacto
FAILED test_module_gfx_lab.py::test_preview_usa_las_plantillas_reales - asser...
```

## Lo que queda abierto
1. **Scripts de lab rotos por el borrado** (se dejaron como están, según el handoff): `lab/hyperframes/f46/f46_corridas.py` l. 224 y `lab/hyperframes/f46/f46b/f46b_corridas.py` l. 311 llaman a `style_head` y `STYLE_TAIL`, que ya no existen. Al correrse, fallan con `AttributeError`; también fallan `f47_corridas.py` y `f48_corridas.py`, que importan `f46b.armar`. Son corridas históricas: nadie las corre hoy.
2. **`lab/hyperframes/f50g/rearmar.py --igual`** ya no da 96/96, porque compara con el prompt guardado, que es el armado viejo. Se espera que siga así hasta F51d, cuando se reescriba `03_visual.json`.
3. **El `03_visual.json` de Wittenoom sigue con el armado viejo** en sus 96 fotos: no se escribe en esta tanda. Eso es F51d, con el canon nuevo.
4. **Opus sigue llenando `gaze_interaction`, `props_detail` y `color_palette`**, que el armado ya no usa. Los usan `depth_probe.py` l. 200 y `m03_imagenes_v3.py` l. 385 (`human_scale`). Dejar de pedirlos es otra variable (la lista del handoff).
5. **El aspecto de `spanish_migrant_families` sigue con «dusted red»** en el canon de producción: la 1/2 armada en producción lo lleva. Es F51b, el canon con el aspecto separado del estado.
6. **`lab/mapa/hechos.json`** sigue listando `style_head` (es el digest de F42; `mapa --check` no lo mira).
7. **`track_gemini_vision` registra una tarifa fija:** F51e (la lista del handoff).
8. **Las demás de la cadena:** «Court» (F51c), el corte Veo y `anio_final`. No se tocaron.
9. **Fuera de git y sin tocar:** `diag_234_cap4.py`, `lab/TOPE_TANDA.json`, `lab/hyperframes/f28/a/f28a.log`, `lab/hyperframes/f50h/llave.json` y las png, y los `ENTRADA_ANALISTA_*.md`.

## Veredicto de revisor-handoff
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | md5 del handoff = b4f08798… | OK | `md5sum` da b4f0879876f38898740e0503f91b7da3 |
| 2 | Etapa 0: 2 líneas tal cual al final de DECISIONES.md y salida de `tail -2` | OK | `tail -2 DECISIONES.md` las muestra, y el diff de 0fdeee4 suma exactamente esas 2 líneas |
| 3 | `armar` con orden C y las 8 claves (sujeto, aspecto, lugar_anio, texto, luz, tecnica, estilo, cierre); `luz` solo `lighting`; `estilo` = ESTILO_C con `{anio}`; docstring actualizado | OK | `m03_imagenes_v3.py` diff, `armar` y `ESTILO_C`. El texto de ESTILO_C es idéntico al del handoff. |
| 4 | Borrados `style_head`, `STYLE_TAIL`, mirada, objeto, paleta; `_PROSA` sin los 3 casilleros; grep previo | OK | El diff muestra los borrados. `grep` en producción (fuera de `lab/`) no encuentra usos. Quedan solo en lab: f46, f46b y f50h, y el informe los lista como abiertos. |
| 5 | Tests reescritos al orden C, borrados los de style_head/STYLE_TAIL, uno nuevo con cartel y un grupo | OK | Diffs de f8, f50b y f50g. `test_module_f51a.py` fija el orden y el prompt exacto con cartel y un grupo. |
| 6 | Contrato 20/20 byte a byte contra PROMPTS_F50h.json → C, con el post-proceso de producción | OK | Corrí `contrato.py`: 20/20 "sí", rc=0, e imprime el 1/2 y una foto con cartel. Usa `rearmar_una` (armar, f8_backstop y _sacar_frases_con_texto). |
| 7 | Etapa 2: `rearmar_todo.py` en seco; REARMADO_F51a.md con conteo, mediana y máximo antes y después, cuántas cambian, 3 prompts (1/2, 2 grupos, Veo) y lista de vacíos | OK | REARMADO_F51a.md: 96 fotos, mediana 157,5 a 122,5, máximo 273 a 196, cambian 96/96, vacíos ninguna. Trae 1/2, 1/3 (2 grupos) y 1/1 (Veo). |
| 8 | No escribir 03_visual.json, canon ni topics_db | OK | `git diff --stat f319280 HEAD` no toca data/. Los `topics_db_pre*.json` sin seguimiento tienen fecha vieja (20 oct) y no son de la tanda. |
| 9 | No tocar name_matching, corte Veo, anio_final ni cost_tracker | OK | El diff solo toca m03_imagenes_v3.py, 4 tests, DECISIONES, MAPA/sticker y archivos de lab/f51a. |
| 10 | Tests de la tanda | OK | Corrí `pytest` en los 4 módulos: 49 passed. |
| 11 | Suite rápida y candado ch02 (f792f3d4…) | OK | Logs en `f41/f51a/`: rápida 55 passed, 3 skipped. md5 del ch02 = f792f3d483a1fa42daed5f7f0e054f46. |
| 12 | Suite amplia | PARCIAL | 4 failed, 994 passed. Son los mismos 4 fallos que en f50i (4 failed, 991 passed). Solo cambió el número de tests que pasan. No los volví a ejecutar contra la rama base. |
| 13 | Un commit por etapa con F51a en el mensaje | OK | 0fdeee4, 6817e7a y c93428a mencionan F51a. |
| 14 | F51a_REPORT.md con lo abierto entero y el veredicto íntegro | PARCIAL | Existe, con 9 puntos abiertos. El veredicto sigue como `{{VEREDICTO}}` (l. 196), a la espera de este informe. ESTADO_SESION todavía no se actualizó, como indicaste. |
| 15 | US$ 0, sin fal ni LLM | NO VERIFICABLE | No hay llamadas a modelos en `contrato.py` ni en `rearmar_todo.py`. El costo cero no lo pude confirmar con un log. |

Observaciones
- Los 4 fallos de la suite amplia no se deben a F51a. El informe no dice explícitamente que son previos, y conviene que lo diga al pegar el veredicto.
- Hay 3 scripts de lab que ahora fallan con `AttributeError` porque llaman a `style_head` o `STYLE_TAIL` (f46 `f46_corridas.py`, f46b `f46b_corridas.py` y f50h `f50h.py`). El handoff pide dejar lo de lab como está y listarlo. El informe nombra f46 y f46b y dice que también fallan las corridas de F47 y F48, que importan `f46b.armar`. No menciona f50h.py. Es una omisión menor.
- `lab/mapa/hechos.json` todavía lista `style_head`. El informe lo declara.

Fuera de alcance: ninguno. Los tres archivos modificados de antes (`diag_234_cap4.py`, `lab/TOPE_TANDA.json`, `f28a.log`) no están en los commits de la tanda.

Riesgos que el contrato no cubre
- El contrato prueba solo 20 de las 96 fotos contra C. Las otras 76 cambian y nadie las miró (96/96 cambian, mediana 157,5 a 122,5 palabras).
- Hasta F51b, el prompt de producción de la 1/2 conserva «dusted red» en el aspecto del canon. El informe lo declara en el punto 5.
- Hay corridas de lab (F46 a F48) que ya no se pueden reproducir.

### Adenda de CC (después del veredicto)
- **#12 y observación 1, las 4 fallas de la amplia:** son las 4 previas conocidas de la cadena: `m03_merge_timing::test_c_guarda_de_minimo`, `m03_merge_timing::test_c_veo_path_y_veo_anchor_intacto`, `gfx_lab::test_cues_sin_escribir_el_proyecto` y `gfx_lab::test_preview_usa_las_plantillas_reales`. No vienen de F51a. Los 3 tests que suben la cuenta (991 → 994) son los de `test_module_f51a.py`.
- **#14:** este veredicto ya está pegado, y ESTADO_SESION se actualiza en el commit de este reporte.
- **#15, US$ 0:** ni `contrato.py` ni `rearmar_todo.py` importan clientes de modelos. Tampoco lo hacen los tests que se agregaron o cambiaron; el de m03 usa Opus falso, igual que antes. No se agregó nada a `cost_history` porque no hubo gasto que registrar.
- **Observación 2, `f50h.py`:** no se rompe. Solo nombra `style_head` y `STYLE_TAIL` en el docstring (l. 7). `armar_c` usa las partes `sujeto`, `aspecto`, `lugar_anio`, `texto`, `tecnica` y `cierre`, que siguen existiendo. Lo comprobé llamando a `f50h.armar_c` con el `armar` nuevo: devuelve «A miner. Loading ore. The mill yard, 1962. Harsh noon. Wide shot. A grainy 35mm …», sin error. Los scripts que fallarían son solo f46 y f46b, y las corridas de F47 y F48 que importan `f46b.armar` (punto 1 de «Lo que queda abierto»).
- **Riesgo 1, las 76 fotos fuera del contrato:** el armado es el mismo código para las 96, y las 20 del contrato cubren 5 con cartel y 15 sin cartel, y 4 fotos sin grupo, 12 con uno y 4 con dos. En las 96, ningún prompt quedó vacío ni sin sujeto. Nadie las miró en imagen: las fotos de las 96 se regeneran en F51d.
