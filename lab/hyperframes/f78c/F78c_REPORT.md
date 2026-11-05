# F78c — Reporte: el texto de la escena describe a la persona con SUS rasgos + lab de motor para las manos

Rama `f11-guion-v4`, base `a6ff9a9`. Handoff `lab/hyperframes/f78c/HANDOFF_F78c_aspecto_desde_rasgos.md`; el md5 es `20e28083587038f723e35ed9f9f6cb6a` con la ADENDA 2, que manda.
Etapa A: commit `4beca6b`. Etapa B: lab de 5 fotos en `lab/hyperframes/f78c/b/`, **US$ 0,9119**, sin tocar producción. **PARADA.**

## Qué se hizo
1. **PARADA antes de programar.** El handoff pedía los rasgos antes de m03, pero quién entra en la llamada de rasgos y su `grupo_appearance` salen de las fotos de m03 (`03_visual.json`).
   - Omar eligió la opción (a), que es la adenda 2: m03 solo lee `rasgos.json` si su `md5_entrada` coincide con la entrada armada desde el `03_visual.json` del disco, y nunca llama.
2. **Etapa A** (commit `4beca6b`): código en `foto_madre.py` y `script_engine/m03_visual.py`, más `test_module_f78c.py`.
   - Un subagente ubicó en paralelo la función de producción para rehacer los casilleros de una sola foto (`_f8_refill`) y sus efectos en disco.
   - Suite amplia: 1573 passed, 29 skipped y las 3 heredadas (`a/suite.log`). `mapa_modulos --check`: 0 fallas.
3. **Etapa B** (`b/lab_f78c.py`, venv, 47 s):
   - md5 antes de 422 archivos de producción;
   - casilleros rehechos de las 5 fotos con Opus por `_f8_refill` (nota vacía, mismo ancla y beat), en paralelo;
   - referencia según `_madres_para_item` con el guion vivo;
   - V1 con Lite (5 fotos) y V2 con Nano Banana 2 completo (3 de Arcadio), en paralelo y sin respaldo Seedream;
   - md5 después.
   - Hoja: `lab/hyperframes/f78c/ETAPA_F78c.html`.

## Diff (commit 4beca6b)
- **`foto_madre.py`** (+62 / −18):
  - `_candidatas(topic, visual)`: la selección de personas con madre, que antes vivía dentro de `generate_fotos_madre_personas`. Salió de ahí tal cual.
  - `entrada_rasgos(topic, visual)`: pública; es la entrada exacta de la llamada de rasgos.
  - `rasgos_vigentes(topic, video_id=None)`: solo lectura, nunca llama. Devuelve `({nombre: rasgos}, "ok")` o `({}, motivo)`.
  - `generate_fotos_madre_personas` usa las dos primeras. No cambia nada más.
- **`script_engine/m03_visual.py`** (+19 / −2):
  - `_rasgos_de_madres(topic)` llama a `foto_madre.rasgos_vigentes` con import perezoso. Si no hay rasgos vigentes imprime `[03] WARN PERSONAS DOCUMENTADAS con appearance_canon: rasgos no vigentes (<motivo>)`.
  - En `_format_seedream_canon_block`, una persona con rasgos lleva `appearance: <rasgos>` en lugar de `appearance_canon:` (no las dos). Sin rasgos, la línea vieja. La edad y `condition <años>` no cambian.
- **Carpeta del video** (adenda 1): `OUTPUT_DIR/<id del topic>/foto_madre/rasgos.json`, porque en LONG el id del topic es el del video (fase1_5 paso0: «video_id == topic_id en LONG»; Colza: ambos `c4934b7d…`). `rasgos_vigentes` acepta `video_id` por si algún día no coinciden, pero m03 no lo pasa: no hay hoy un llamador con ids distintos.
- **Única edición de texto de prompt** (la cabecera del bloque):
  - antes: `PERSONAS DOCUMENTADAS (el nombre es solo para el casillero persona; en la prosa usar appearance_canon, NUNCA el nombre):`
  - después: `PERSONAS DOCUMENTADAS (el nombre es solo para el casillero persona; en la prosa usar appearance (o appearance_canon si no hay), NUNCA el nombre):`
- **Tests** (`test_module_f78c.py`, 6 tests, sin red):
  - con cache, la línea `appearance:` reemplaza a la del canon (una sola línea `appearance_canon` queda, la de Moscoso, que no tiene madre); edad y condition intactas; cabecera nueva; m03 no llama;
  - sin `rasgos.json`: línea vieja y WARN, sin llamar;
  - md5 distinto: línea vieja y WARN;
  - topic sin id o sin 03_visual;
  - `entrada_rasgos` = la entrada y el md5 de `rasgos.json` que escribe foto_madre; la segunda corrida sale del cache;
  - **Colza real** (adenda 1.2): el md5 armado desde m03 = `md5_entrada` del `rasgos.json` de Colza, 7 personas, 0 llamadas.

  Los tests viejos del bloque (f48, f50d, f58_a3, f59_a1, f60_a3, m03_reglas_133) pasan sin cambios.

## Bloque PERSONAS DOCUMENTADAS de Colza (Etapa A, función de producción; completo en `a/bloque_personas.md`)
- `rasgos_vigentes`: ok, 7 personas.
- md5 de la entrada desde m03 = `c63309107f9edce99f3f64c0dbde2118` = `md5_entrada` de `rasgos.json`: **0 llamadas nuevas**.

**ANTES**
```
PERSONAS DOCUMENTADAS (el nombre es solo para el casillero persona; en la prosa usar appearance_canon, NUNCA el nombre):
  • Jaime Vaquero García | role: first reported fatal victim, a child who died of a mysterious pneumonia | age 8 | era: 1981
    appearance_canon: an eight-year-old Spanish boy
    condition 1981-1981: Fatally ill with a mysterious pneumonia-like respiratory illness, hospitalized before his death.
  • Jesús Sancho Rof | role: Spanish Minister of Labour, Health and Social Security who downplayed the illness as a minor infection | age unknown | era: 1981
    appearance_canon: a middle-aged Spanish man
  • Antonio Muro Fernández Cavada | role: doctor at Hospital del Rey who defended a digestive origin and was forced out of his post | age unknown | era: 1981
    appearance_canon: a middle-aged Spanish man
  • Arcadio Fernandez | role: victim and director of the Toxic Oil Syndrome victims' association, campaigning for justice | age unknown | era: 1981-1989
    appearance_canon: a middle-aged Spanish man
    condition 1981-1989: Deformed hands and upper body with disabling chronic pain.
  • Angela Menseger | role: victim and mother of two in Leganés | age unknown | era: 1985
    appearance_canon: a middle-aged Spanish woman
    condition 1981-1985: Chronically ill after years of repeated hospitalizations, shuffling with dragging feet, veins exhausted by transfusions, and diagnosed with liver cancer.
  • Javier Moscoso | role: Spanish Attorney General who argued the State might not be obliged to pay compensation | age unknown | era: 1989
    appearance_canon: a middle-aged Spanish man
  • Juan Miguel Bengoechea | role: oil importer sentenced to twenty years in prison | age unknown | era: 1992
    appearance_canon: a middle-aged Spanish man
  • Ferrero | role: oil distributor sentenced to twelve years (also spelled Ferrera in the source) | age unknown | era: 1992
    appearance_canon: a middle-aged Spanish man
  • Enric Salomó | role: oil trader sentenced to four years in prison | age unknown | era: 1992
    appearance_canon: a middle-aged Spanish man
  • Ramón Alabart | role: oil trader sentenced to four years in prison | age unknown | era: 1992
    appearance_canon: a middle-aged Spanish man
  • Jorge Pich | role: oil trader sentenced to ten years in prison | age unknown | era: 1992
    appearance_canon: a middle-aged Spanish man
  • Manuel Hernández | role: public official sentenced to six months for negligence for approving the use of anilines | age unknown | era: 1992
    appearance_canon: a middle-aged Spanish man
  • Jesús Lozano | role: child victim, later deputy secretary of the Seguimos Viviendo platform | age 6 | era: 1981
    appearance_canon: a six-year-old Spanish boy
    condition 1981-1981: Hospitalized in a glass-walled room with ten other children, all crying in pain from the unknown illness.
  • Carmen Cortés | role: adolescent victim, later nursing auxiliary and founder of Seguimos Viviendo | age 14 | era: 1981-2000
    appearance_canon: a fourteen-year-old Spanish girl
    condition 1981-1982: Hospitalized for ten months with organ and neuromuscular damage, losing more than twenty kilos and visibly emaciated.
    condition 1992-2000: Unable to work after a herniated disc, living on a disability pension.
  • Mercedes García | role: victim who fell ill while preparing for civil-service exams | age unknown | era: 1981
    appearance_canon: a young adult Spanish woman
    condition 1981-1981: Suffering cramps and insomnia, too weak to press a typewriter key.
```
**DESPUÉS** (cambian solo la cabecera y las 7 personas con madre; las otras 8 quedan igual)
```
PERSONAS DOCUMENTADAS (el nombre es solo para el casillero persona; en la prosa usar appearance (o appearance_canon si no hay), NUNCA el nombre):
  • Jaime Vaquero García | … | age 8 | era: 1981
    appearance_canon: an eight-year-old Spanish boy
    condition 1981-1981: Fatally ill with a mysterious pneumonia-like respiratory illness, hospitalized before his death.
  • Jesús Sancho Rof | … | age unknown | era: 1981
    appearance: Broad oval face with light olive skin and brown eyes, dark hair neatly combed back and greying at the temples, clean-shaven, thick dark-rimmed glasses, stocky build
  • Antonio Muro Fernández Cavada | … | age unknown | era: 1981
    appearance: Long narrow face with fair skin and brown eyes, dark hair receding at the forehead and cut short, full dark moustache, no glasses, lean wiry build
  • Arcadio Fernandez | … | age unknown | era: 1981-1989
    appearance: Round full face with light olive skin and brown eyes, thick short curly black hair, short full black beard, no glasses, heavyset broad-shouldered build
    condition 1981-1989: Deformed hands and upper body with disabling chronic pain.
  • Angela Menseger | … | age unknown | era: 1985
    appearance: Soft heart-shaped face with fair skin and brown eyes, shoulder-length wavy dark brown hair parted to the side, no glasses, medium sturdy build
    condition 1981-1985: Chronically ill after years of repeated hospitalizations, shuffling with dragging feet, veins exhausted by transfusions, and diagnosed with liver cancer.
  • Javier Moscoso … Manuel Hernández: igual que antes (appearance_canon: a middle-aged Spanish man)
  • Jesús Lozano | … | age 6 | era: 1981
    appearance: Small round face with light olive skin and brown eyes, short straight black hair with a blunt fringe across the forehead, slight skinny build
    condition 1981-1981: Hospitalized in a glass-walled room with ten other children, all crying in pain from the unknown illness.
  • Carmen Cortés | … | age 14 | era: 1981-2000
    appearance: Oval face with fair skin and large brown eyes, long dark brown hair tied back in a single braid, slender build
    condition 1981-1982: Hospitalized for ten months with organ and neuromuscular damage, losing more than twenty kilos and visibly emaciated.
    condition 1992-2000: Unable to work after a herniated disc, living on a disability pension.
  • Mercedes García | … | age unknown | era: 1981
    appearance: Angular face with high cheekbones, light olive skin and brown eyes, long straight black hair worn loose past the shoulders, thin wire-rimmed glasses, slim build
    condition 1981-1981: Suffering cramps and insomnia, too weak to press a typewriter key.
```
Coincide con la tabla que esperaba el analista.

**Periféricos que heredan el bloque** (adenda 3): todo lo que llama a `_format_seedream_canon_block`. Ninguno se regeneró en esta tanda.
- el clip Veo/Omni (`_render_prompts_seedream_veo`);
- los refills de m03 (`_f8_refill`);
- QA Studio, en el editor de foto (`_fix_core` pasa por los casilleros de m03);
- las miniaturas de m09_packaging.

## Etapa B — lab
**Producción intacta:** md5 de los 422 archivos (`output/<tid>/assets` completo, `03_visual.json` y `data/scripts/<tid>.json`), antes y después: **0 distintos** (`b/md5_antes.json` y `b/md5_despues.json`).
- `_persist` y `save_db` quedaron bloqueados durante el lab.
- No se llamó `cost_tracker.end_video`, así que no se escribió `cost_history.json`.

**Motor completo:**
- id `fal-ai/nano-banana-2/edit`;
- precio US$ 0,08 por imagen a 1K, la resolución por defecto y la misma que da Lite (fal.ai/models/fal-ai/nano-banana-2/edit/llms.txt, leído 2026-11-04);
- mismos parámetros que Lite: `aspect_ratio` y `safety_tolerance` del perfil, frase de madres más el prompt.
- No entra a producción.

**Tabla foto → subject** (`b/tabla_subject.md`):

| foto | persona vieja → nueva | subject viejo | subject nuevo |
|---|---|---|---|
| ch01_img_01 | Arcadio → Arcadio | Middle-aged Spanish man, fair olive skin, greying dark hair, thin wasted build, deformed curled hands, sclerodermic tight skin, worn mid-1980s quilted anorak | Heavyset broad-shouldered Spanish man around forty, round full face, light olive skin, thick short curly black hair, short full black beard, worn mid-1980s wool coat, deformed hands resting in his lap |
| ch01_supp_05 | Arcadio → Arcadio | Middle-aged Spanish man, fair olive skin, greying dark hair, wasted upper body, deformed stiff hands, worn wool coat over thick sweater | Heavyset broad-shouldered Spanish man of light olive skin, round full face, thick short curly black hair and short full black beard, in a mid-1980s wool coat over a thick sweater, a scarred chronic oil-poisoning survivor |
| ch06_img_14 | Arcadio → Arcadio | A middle-aged Spanish man, light olive skin, dark greying hair, deformed hands and hunched upper body, thick sweater, the association director | **Arcadio**, a heavyset broad-shouldered Spanish man in his forties … thick short curly black hair and a short full black beard …; his hands and upper body are visibly deformed by chronic illness |
| ch04_img_12 | Lozano → **Carmen + Lozano** | A five-year-old Spanish boy in striped pajamas sitting in bed behind a glass partition, a crowded row of children's beds around him | A slender, visibly emaciated fourteen-year-old Spanish girl … long dark brown hair in a single braid, seen from behind …; beyond a glass partition, a slight skinny five-year-old Spanish boy … short black hair cut in a blunt fringe … |
| ch07_supp_07 | **Carmen → Arcadio** | A Spanish woman in her early thirties, light olive skin, dark short practical hair, very thin frame … | Spanish association director in his fifties, … thick short curly black hair touched with grey, short full black beard, heavyset … |

**Resultados** (5 V1 y 3 V2, todos «ok»; ningún rechazo de moderación sin respaldo):
- **Identidad:** funciona. Con los rasgos en el texto, Arcadio sale en V1 y V2 con barba, pelo negro rizado y corpulento, la misma cara que su madre. En V0 (ch01_img_01) era un hombre de pelo canoso sin barba. El texto ya no contradice la referencia.
- **Manos:** ni Lite ni el completo las dibujan claramente deformes. El texto dice «deformed hands» y la referencia (variante F78b) las tiene, pero en la escena salen casi normales. En ch01_supp_05, V2 curva un poco más los dedos que V1; en ch06_img_14 y ch01_img_01 no hay diferencia clara. **La hipótesis «el motor Lite es el que suaviza» no se confirma con estas 3 fotos.**
- **ch04_img_12:** el refill sumó a Carmen de espaldas (trenza) junto a Lozano detrás del vidrio. Usa 2 referencias (variantes de Carmen y de Lozano).
- **ch07_supp_07:** el refill cambió la persona de Carmen a Arcadio, y la foto ya no prueba lo de Carmen adulta y la trenza. Arcadio en 2000 queda fuera de su era (1981-1989), sin tramo, así que va con su madre limpia; Opus lo describe «in his fifties».
- **ch06_img_14:** el prompt nuevo trae el NOMBRE «Arcadio» en el subject, contra la cabecera («NUNCA el nombre»). Es salida de Opus, no del código.

## Costo real de la Etapa B (`b/costo.json`)
| servicio | llamadas | US$ |
|---|---|---|
| Anthropic Opus 5.5 (casilleros, `_f8_refill`) | 5 | 0,4619 |
| Nano Banana 2 Lite /edit (tarifa estimada de config, 0,042) | 5 | 0,2100 |
| Nano Banana 2 /edit completo (lista de fal, 0,08 a 1K) | 3 | 0,2400 |
| **total** | 13 | **0,9119** |

## Declarado (decidí y sigo)
- El refill es `_f8_refill` con un ancla por foto: es el camino de producción para rehacer una foto. La primera pasada de m03 llena todas las anclas del cap en una sola llamada, así que el resultado no es idéntico a un m03 completo (lo marcó el subagente).
- `cerrada` de los ítems de caps con clip queda en False: `03_visual.json` no la guarda.
- La referencia sale de `_madres_para_item` aplicada al ítem NUEVO (persona nueva), que es lo que haría producción si ese prompt entrara.
- El texto que va al motor es el de producción: frase de madres más el prompt. El costo de Lite es la tarifa estimada de config (F68, «ESTIMADO»); el del completo es la lista de fal.
- m03 avisa con `print("  [03] WARN …")`, como el resto de m03 (no usa error_handler).
- La línea 166 del SYSTEM de casilleros («from a documented person's appearance_canon when it is one») no se tocó: la única edición de prompt permitida era la cabecera.

## Abierto
- **Decisión 1 de Omar:** el texto con rasgos funciona para la identidad. Llevarlo a producción implica rehacer los casilleros de TODAS las fotos con persona antes de la Etapa C de F78a (otra tanda). En un topic nuevo, la primera pasada de m03 sale genérica (adenda 2).
- **Decisión 2 de Omar:** el motor completo no arregla las manos en este lab (3 fotos), cuesta casi el doble (0,08 contra 0,042) y la cara sale igual de bien. No hay evidencia para cambiarlo.
- **Manos deformes:** ni el texto, ni la referencia, ni el motor completo las sostienen en la escena. Queda sin causa medida.
- **Rehacer con nota vacía puede cambiar de persona** (ch07_supp_07 pasó de Carmen a Arcadio; ch04_img_12 sumó a Carmen). Si se rehacen todas antes de la Etapa C, hace falta conservar el sujeto o revisar foto por foto.
- **Fuga del nombre** «Arcadio» en el prompt de ch06_img_14: un nombre real en el texto que va al motor. El casillero lo debería impedir; no hay filtro de nombres en el armado.
- Carmen adulta y la trenza quedaron sin probar (ch07_supp_07 cambió de persona).
- La línea 166 del SYSTEM de casilleros sigue diciendo «appearance_canon»; puede chocar con la cabecera nueva (la regla de la tanda solo permitía tocar la cabecera).
- Lo que sigue de antes: el marco de la madre de Mercedes; `etapa_bc_prueba.py:90` con la firma vieja de `_clave_lote`.

## Veredicto del revisor-handoff
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | m03 reemplaza `appearance_canon` por `appearance: <rasgos>` (no las dos); persona sin rasgos conserva la línea vieja | OK | `script_engine/m03_visual.py` l.473-490 (diff 4beca6b); `test_module_f78c.py` |
| 2 | Adenda 2: m03 solo LEE `rasgos.json` si `md5_entrada` coincide con la entrada armada del 03_visual en disco; si no, línea vieja + WARN, nunca llama | OK | `foto_madre.rasgos_vigentes` (solo `json.loads`, sin llamadas) y `m03._rasgos_de_madres` (WARN con motivo); tests de sin cache y md5 distinto |
| 3 | `entrada_rasgos` pública, misma construcción que `generate_fotos_madre_personas`; md5 igual desde m03 y desde foto_madre | OK | `_candidatas` y `entrada_rasgos` extraídas tal cual; `generate_fotos_madre_personas` las reutiliza; test con Colza real (md5 `c6330910…`, 7 personas, 0 llamadas) |
| 4 | Única edición de prompt = cabecera; sin reglas nuevas | OK | El diff de m03 solo cambia esa frase; antes/después pegados en el reporte |
| 5 | Carpeta del video declarada, sin ruta fija | OK | `rasgos_vigentes(topic, video_id=None)` usa `OUTPUT_DIR/<id>/foto_madre`; reporte l.29 |
| 6 | Tests sin red; suite | OK | Corrí `test_module_f78c.py` con proxy muerto: 6 passed. `a/suite.log`: 1573 passed, 3 failed. Esos 3 fallos (f51c, m03_merge_timing ×2) no los comparé contra la base, así que no sé si ya fallaban |
| 7 | Bloque PERSONAS DOCUMENTADAS antes/después en texto; coincide con lo esperado | OK | Reporte l.47-115 y `a/bloque_personas.md`; las 7 personas coinciden con la tabla del handoff |
| 8 | Commit A | OK | `4beca6b` |
| 9 | Periféricos declarados (Veo/Omni, `_f8_refill`, QA Studio, m09) | OK | Reporte l.118-122 |
| 10 | Lab de 5 fotos en `b/`, V0/V1/V2 (V1 Lite ×5, V2 completo ×3 de Arcadio) | OK | `b/V1/` tiene 5 PNG y `b/V2/` tiene 3; `lab.log` marca 8 «ok»; V0 es la foto de producción |
| 11 | Sin respaldo Seedream | OK | `lab_f78c.py` l.9; `lab.log` sin rechazos |
| 12 | Producción intacta (assets, 03_visual.json, data/scripts/<tid>.json) | OK | `cmp md5_antes.json md5_despues.json` da IGUAL. 422 entradas (420 de assets, el 03_visual y el script). `git status` sin cambios en producción |
| 13 | Hoja `ETAPA_F78c.html` | OK | Existe, 862 KB, imágenes embebidas |
| 14 | Tabla foto → subject viejo/nuevo | OK | `b/tabla_subject.md` y reporte l.137-143 |
| 15 | Id y precio del motor completo declarados | OK | `fal-ai/nano-banana-2/edit`, US$ 0,08 (reporte l.130-131). No verifiqué la página de fal |
| 16 | Costo real por servicio | PARCIAL | `b/costo.json` suma 0,9119. El Opus es medido. Lite (0,042) y el completo (0,08) son tarifa estimada o de lista, no cobro real; el reporte lo declara |
| 17 | DECISIONES.md con fecha 2026-11-04 20:30 | OK | `DECISIONES.md` l.249 |
| 18 | `F78c_REPORT.md` | PARCIAL | Existe y está completo. La sección del veredicto dice «(pegado abajo)» y está vacía hasta pegar este texto |
| 19 | ESTADO_SESION después del veredicto | OK | Sin tocar todavía, como corresponde |
| 20 | PARADA: sin Etapa C ni regeneración de producción | OK | md5 idéntico; sin cambios en `output/` |

Fuera de alcance: ningún archivo de producción tocado. El commit A también modifica `lab/MAPA_PROYECTO.json`, `lab/MAPA_PROYECTO.md`, `lab/mapa/stickers/fase2a.json` y `lab/hyperframes/f78a/a/suite_lista.txt`. Parecen artefactos regenerados por `mapa_modulos` y por la lista de la suite, no están pedidos en el handoff y no los diffeé. `diag_234_cap4.py`, `f28a.log` y `pedido_paquetes_wittenoom.txt` ya estaban modificados antes y no son de F78c. La Etapa B sigue sin commit: `b/`, `ETAPA_F78c.html` y `F78c_REPORT.md` están sin trackear.

Observaciones:
- El reporte admite que ch07_supp_07 pasó de Carmen a Arcadio. Por eso la foto ya no prueba el caso de Carmen adulta con trenza, y esa prueba del lab queda hecha solo a medias.
- El texto nuevo de ch06_img_14 trae el nombre «Arcadio» contra la cabecera («NUNCA el nombre»). Es salida de Opus y está declarado.
- Las conclusiones sobre manos y motor son de 3 fotos y no las revisé a ojo. Quien decida debe mirar la hoja.

Riesgos que el contrato no cubre: (1) un topic nuevo sale genérico en la primera pasada de m03; la adenda 2 lo posterga a otra tanda. (2) Rehacer los casilleros con nota vacía puede cambiar de persona, como pasó en 2 de 5 fotos. (3) La línea 166 del SYSTEM de casilleros sigue diciendo «appearance_canon», lo que puede contradecir la cabecera nueva.

### Adenda de CC
- **Punto 6 (heredadas):** son las mismas 3 de F77, F78a y F78b (`f51c[paredes de chapa]`, `m03_merge_timing` ×2). Ninguna toca m03 de casilleros ni foto_madre.
- **Punto 16:** el cobro real de fal no viene en la respuesta. Lite es la tarifa estimada de config (F68, «ESTIMADO», medida por Omar en el panel) y el completo es la lista de fal a 1K; los dos están declarados.
- **Archivos extra del commit A:** los exigen las reglas fijas del repo: el sticker y el mapa regenerado (`mapa --check` 0) y la línea de la suite para que `f78c` corra en la suite amplia.
- **Riesgo 3 (línea 166 del SYSTEM):** no la toqué, porque la única edición de prompt permitida era la cabecera. Queda en «abierto» para el analista.
- **Mirado a ojo** (hojas de contacto en el scratchpad): la cara de Arcadio coincide con su madre en V1 y V2. Las manos salen casi normales en los dos motores; V2 curva un poco más los dedos en ch01_supp_05.
