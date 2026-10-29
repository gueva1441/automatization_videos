# F50g-A — El aspecto del grupo del canon va al prompt de foto, por código (US$ 0) · PARADA

Handoff `lab/hyperframes/f50g/HANDOFF_F50g_A_aspecto_del_canon.md`, **md5 `f92d8bdd2a918a9de6d4a27514a9bf52`** (verificado). Wittenoom `123bbb64-9fca-4395-8bf4-57d60e219ef1`, rama `f11-guion-v4`; `main` no se tocó.
- Costo: US$ 0. Ninguna llamada a modelo ni a fal.
- No se tocó F50g-B: el bug de «Court», el corte Veo y `anio_final` quedan para su handoff.

## Qué pasó, en llano
- `armar` llenaba el renglón `aspecto` vacío desde F46b. Ahora pone ahí la oración `appearance` de cada grupo de gente de la foto, tal cual viene del canon.
- Ejemplo: en la 1/2, la frase «Spanish Mediterranean people with olive to light skin, dark brown or black hair, dark eyes…» queda después del sujeto y la acción.
- 59 de las 96 fotos de Wittenoom ganan esa oración, sin llamar a ningún modelo. Las otras 37 no tienen grupo de gente, y las 2 de grupos sin `appearance` no agregan nada.
- El papel nuevo está en `lab/hyperframes/f50g/`.

## Commits
| etapa | commit |
|---|---|
| 0 | `8ff5961` |
| 1 | `9f4ca2a` |
| 2 | `a3b6684` |
| 3 | `40ea9ee` |
| 4: reporte y ESTADO | este commit |

## Etapa 0
- md5 del handoff: `f92d8bdd2a918a9de6d4a27514a9bf52`.
- `DECISIONES.md`, última línea, tal cual: se comprobó con código que el texto agregado está, idéntico, dentro del handoff.

  «- 2026-10-29 01:29 · **F50g-A:** el aspecto del grupo (`people_groups[].appearance` del canon) va al prompt de foto por código, una oración por grupo en el orden de Opus, pegada tal cual; sin grupo o sin aspecto, nada. Motivo: la 1/2 generada en fal dio asiáticos con «Spanish migrant» y españoles con «Mediterranean features»; el canon ya lo traía y `armar` lo dejaba vacío desde F46b · Omar · F50g-A»

## Etapa 1 — `armar` y tests
`script_engine/m03_imagenes_v3.armar`:
- `"aspecto"` = `" ".join(oracion(grupos[g]["appearance"]) for g in it["people_group"])`, en el orden de `people_group`.
- Si un grupo no está en el canon o no tiene `appearance`, no agrega nada. Si no hay `grupos`, tampoco.
- Docstring actualizado: salió «no se escriben (`aspecto` vacío: así se midió)».
- Ningún nombre de tema, de grupo ni número nuevo en el código.
- Producción ya le pasa `grupos` a `armar` (`m03_visual._render_prompts_seedream`, l. 688), así que no hubo que tocar nada más.

Tests en **`test_module_f50g.py`, en la raíz**. El handoff dice `tests/test_module_f50g.py`, pero el repo no tiene `tests/`: todos los tests viven en la raíz y la suite amplia los busca ahí (`test_module_f[0-9]*`). Resultado: `6 passed`.
- (a) un grupo: su oración va entre sujeto y mirada;
- (b) dos grupos: las 2 oraciones, en el orden de `people_group`;
- (c) sin grupo, o sin canon: el prompt es idéntico al de hoy;
- (d) un grupo sin appearance o desconocido: no agrega nada;
- (e) el resto de las partes y su orden no cambian;
- además, la 1/2 de Wittenoom con sus casilleros guardados y el canon de producción (`f50f/canon_f50f.json`).

Prompt de la 1/2 armado por el test:
```
A Spanish migrant family posed for a portrait: a young olive-skinned miner in a pressed shirt with a bandaged foot, a slim young dark-haired wife in a cotton dress, a few relatives behind them. The family stands squared to the camera for the portrait while the white-bandaged foot sticks out at the front of the group. Spanish Mediterranean people with olive to light skin, dark brown or black hair, dark eyes, slim to medium builds; women and children tanned and dusted red in Wittenoom. Everyone faces the camera; the miner's weight leans off the bandaged foot, wife's hand resting on his shoulder, faces sun-lined and dust-dulled. The bright white bandage on the foot at the front edge of the portrait. Front of a corrugated sheet-metal house with an asbestos-cement wall panel, packed red earth yard, Wittenoom early 1960s. Grainy 35mm documentary photograph, 1962, dark-history realism, muted colors, visible film grain, slightly underexposed. 35mm film grain, muted documentary colors. Hard cold overcast daylight, flat and shadowless. Faded sepia family-photo tones over rust-red earth, grey corrugated metal, cold blue-grey shadow. Wide shot, eye-level, like a 1960s box camera, deep depth of field, slight film softness at edges. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

## Etapa 2 — `rearmar.py` en seco
`lab/hyperframes/f50g/rearmar.py` es una copia adaptada de `f50b/rearmar.py`. La hizo un subagente mientras yo escribía los tests, y la volví a correr yo. Re-arma desde `raw_llm_prompt` + `anio` guardados + el canon del topic, igual que `_render_prompts_seedream`: `armar` → `f8_backstop` → texto legible.
```
--igual (sin grupos): fotos 96 · iguales 96 · distintas []
```
| cap | fotos | con aspecto | sin aspecto | palabras antes med | antes máx | después med | después máx | 0 grupos | 1 grupo | 2+ grupos |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 5 | 3 | 2 | 161 | 181 | 191 | 209 | 2 | 2 | 1 |
| 2 | 16 | 13 | 3 | 141.5 | 174 | 169.5 | 209 | 3 | 12 | 1 |
| 3 | 16 | 13 | 3 | 155 | 195 | 178.5 | 208 | 3 | 10 | 3 |
| 4 | 14 | 9 | 5 | 125.5 | 147 | 149.5 | 170 | 5 | 9 | 0 |
| 5 | 16 | 8 | 8 | 135 | 245 | 157.5 | 273 | 8 | 6 | 2 |
| 6 | 16 | 9 | 7 | 121.5 | 157 | 130 | 172 | 7 | 9 | 0 |
| 7 | 13 | 4 | 9 | 135 | 183 | 139 | 224 | 9 | 2 | 2 |
| **total** | 96 | 59 | 37 | 137.5 | 245 | 157.5 | 273 | 37 | 50 | 9 |
| total sin 1/1, 7/1 | 94 | 58 | 36 | 136 | 245 | 157.5 | 273 | 36 | 49 | 9 |
```
sin grupos = guardado 96/96 · resta del aspecto 96/96 · cambian 59 · ids fuera del canon ninguno · ids sin appearance ['airport_police', 'international_un_official'] · PASA
```
**Coincide con la simulación del analista**, que midió 94 fotos: son las 96 sin los 2 primeros cuadros Veo (1/1 y 7/1).
- 58 con aspecto y 36 sin.
- Mediana de palabras 136 → 157,5; máximo 245 → 273.
- Grupos por foto (0/1/2): 36/49/9.
- Sobre las 96: 59/37.

Verificaciones:
- con grupos vacíos, el re-armado es igual a lo guardado (96/96);
- quitando el texto del aspecto, el prompt nuevo es el de antes (96/96);
- todos los ids de `people_group` existen en el canon.

## Etapa 3 — `--escribir` y papel
- **Escritura:** primero se copió `03_visual.json` a `lab/hyperframes/f50g/antes/03_visual.json` (md5 `7dcfbaa3…`, el de F50f D).
- **Qué cambió:** comparando clave por clave antes y después, 59 diferencias: 58 `prompt` y 1 `image_prompt` (el primer cuadro Veo 1/1). `sensible` y `motivos` se recalcularon y dieron igual.
- **Después de escribir,** `--igual` da 37 iguales y 59 distintas, como se espera: lo guardado ya trae el aspecto.
- **Papel:** `python lab/hyperframes/f50/papel.py --salida lab/hyperframes/f50g` da «fotos 96 (antes 96) · fuentes {… 67, … 29} · rehechas 1 (video 0) · carteles 9 · US$ 2.332». Los US$ 2,332 son el registro de m03 de F50f D; esta tanda no gastó.

Tres prompts enteros:

**1/2** (`spanish_migrant_families`, 209 palabras): el mismo de la etapa 1.

**3/3, una foto con 2 grupos** (`company_managers`, `prospectors_mine_owners`; 205 palabras):
```
Company managers of British descent in lightweight suits and felt hats meeting sun-weathered Australian prospectors in rolled-sleeve work shirts and wide-brimmed hats. A company truck pulling into the gorge camp as the newcomers walk toward the prospectors' huts to take over the workings. Australian men of British descent, fair complexions, neatly cut and combed hair, office-worker builds. Australian men of British or Irish descent, fair skin deeply sun-tanned and weathered, short hair, lean wiry build from bush prospecting. The prospectors stand back with arms folded, watching the suited men approach; faces read only at a distance. The dusty company truck with its freshly painted door lettering. Yampire gorge mining camp, 1943: tents, corrugated sheet-metal huts, a crude crushing shed, red scree slopes. Grainy 35mm documentary photograph, 1943, dark-history realism, muted colors, visible film grain, slightly underexposed. 35mm film grain, muted documentary colors. Harsh midday desert sun, short black shadows. Red earth and dust, blue-grey asbestos spoil heaps, sun-bleached canvas, dull khaki and pale suit linen. Wide shot, eye-level from beside the huts, deep depth of field, 35mm lens. The words "AUSTRALIAN BLUE ASBESTOS" are written on the truck's driver-side door in hand-painted block letters, in clear crisp lettering. The image has a 16:9 aspect ratio.
```

**7/7, una foto con `banjima_traditional_owners`** (157 palabras). Elegí la 7/7 y no la 7/11, que también tiene ese grupo, porque la 7/11 trae el bug de «Court» de F50g-B.
```
An elderly Aboriginal Banjima man with grey hair and beard, slim weathered build, in a collared shirt and broad-brimmed hat, small against the land. He stands at the rim of a red gorge overlooking his country. Aboriginal Australian people with dark brown skin, dark curly or wavy hair, elders with grey hair and beards, builds shaped by outdoor life in the Pilbara. Seen from behind, looking out over the gorge and plains. A worn broad-brimmed hat silhouetted against the sky. Banjima country in the Hamersley Ranges near Wittenoom, contemporary era, red cliffs and spinifex, 2023. Grainy 35mm documentary photograph, 2023, dark-history realism, muted colors, visible film grain, slightly underexposed. 35mm film grain, muted documentary colors. Late afternoon golden light. Intense red rock, gold spinifex, blue-grey distance, warm late light. Wide shot, eye-level from behind on the rim, deep depth of field, 35mm lens. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.
```

## Etapa 4 — verificación
| | antes (F50f, `f41/f50f_2`) | después (`f41/f50g`) |
|---|---|---|
| suite rápida | 55 passed, 3 skipped | 55 passed, 3 skipped |
| suite amplia | 4 failed, 985 passed, 30 skipped | 4 failed, 991 passed, 30 skipped (+6 de `test_module_f50g.py`) |
| ch02 md5 | `f792f3d4…` | `f792f3d483a1fa42daed5f7f0e054f46` (igual) |

- Fallas de la amplia: las 4 de siempre (`m03_merge_timing` ×2, `gfx_lab` ×2).
- Sticker de `m03_imagenes_v3.py` (fase2a) actualizado; `MAPA_PROYECTO --check`: «157 archivos de producción · 0 fallas».

## Lo que queda abierto
1. **F50g-B, que no se tocó:**
   - el bug de `scrub_documented_names` con «Court», que rompe las fotos 6/3 y 7/11;
   - el corte Veo;
   - `anio_final`.
2. **Repeticiones:**
   - En las 9 fotos con 2 grupos (1/3, 2/16, 3/3, 3/6, 3/9, 5/8, 5/9, 7/8, 7/11) entran 2 oraciones de aspecto, y a veces repiten lo que el sujeto ya dice. En la 3/3, «of British descent» va en el sujeto y en las dos oraciones.
   - Lo mismo pasa en fotos de un grupo, como la 1/2: el sujeto ya dice «olive-skinned».
   - El handoff lo acepta, porque es dato y no invento. La prueba L contra C (recortar invento y repeticiones) sigue pendiente.
3. **El aspecto entra aunque el sujeto no muestre gente de cerca.** Por ejemplo, en el cap 7, el aspecto de los Banjima va en la 7/7 (una silueta de espaldas). La regla es «si la foto tiene grupo, va», y el grupo lo decide Opus.
4. **Grupos sin appearance:** `airport_police` e `international_un_official` no agregan nada. Todas las fotos que los usan tienen además otro grupo con aspecto.
5. **El aspecto de las personas documentadas** (`documented_people[].appearance_canon`, p. ej. Daniel) y el look del lugar (`materials_textures`/`interiors`) no van al prompt. Son otras variables, otras tandas (lo dice el handoff).
6. **El papel de F50g** es el de F50f con el aspecto agregado. Las anclas, los casilleros y la re-hechura son los de F50f D. El papel no se volvió a pedir a Opus.
7. **Foto madre:** sigue vacía en topics_db; va en F51.
8. **De tandas anteriores:**
   - F50f: la medida 1 por lista de palabras y los testigos por texto;
   - F50c: los nombres reales por las citas;
   - F50b: las notas F8 viejas;
   - F50: n2, n3, n7, n8, n10 y n12;
   - Veo 3.1 en fal se apaga el 2026-11-17.

## Procesos
Hubo un subagente (el `rearmar.py`, que terminó) y `verificar.sh f50g`, que corrió en primer plano. No queda nada corriendo. No se cerró ningún programa de Omar.

## Veredicto de revisor-handoff
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 0 | md5 del handoff y línea de DECISIONES tal cual | OK | `md5sum` da f92d8bdd…; la línea de DECISIONES.md (+1 en 8ff5961) coincide con la del handoff |
| 1 | `armar`: aspecto = `appearance` de cada grupo de `people_group`, en orden de Opus, con `oracion()`; sin grupo o sin appearance, nada; nada más cambia | OK | `git diff 2da3428 HEAD -- script_engine/m03_imagenes_v3.py`: 8 líneas, solo la línea `"aspecto"` y el docstring. Sin nombre de tema, grupo ni número nuevo; solo las claves `people_group` y `appearance` |
| 1b | Tests: los 5 casos del handoff | OK | `test_module_f50g.py` (5 casos más el de la 1/2 de Wittenoom). `pytest -q test_module_f50g.py test_module_f50b.py` dio 27 passed |
| 2 | rearmar en seco: 58 con / 36 sin, mediana ~157 | OK | Corrí `rearmar.py`: 94 fotos (sin 1/1 y 7/1), 58 con y 36 sin, mediana 157,5, máx 273, grupos 36/49/9. Sobre las 96: 59/37 |
| 3 | `--escribir`: copia previa en `antes/`; solo cambian prompts | OK | Comparación clave por clave de `f50g/antes/03_visual.json` contra el `03_visual.json` vivo: 59 diferencias, 58 `prompt` y 1 `image_prompt`, nada más |
| 3b | Papel nuevo con `papel.py --salida` | OK | `PAPEL_FOTOS_WITTENOOM.json` y `.md` existen y están en 40ea9ee |
| 3c | 3 prompts enteros en el reporte | OK | 1/2, 3/3 (2 grupos, 205 palabras) y 7/7 (Banjima). 1/2 y 7/7 son idénticos al `prompt` guardado. El 3/3 es idéntico (`image_prompts`, cap 3, 205 palabras) |
| 4 | Suite rápida, candado ch02, commits por etapa, ESTADO, REPORT | PARCIAL | Cuatro commits que nombran F50g-A. ESTADO_SESION está modificado sin commitear (esperado: va después del veredicto). El REPORT aún tiene el marcador `{{VEREDICTO}}`. La suite rápida y el md5 de ch02 (`f792f3d4…`) solo se leen del reporte; yo no los corrí |
| 5 | PARADA: sin fal, sin m03 con modelo, sin F50g-B | OK | `git diff --stat 2da3428 HEAD`: no hay archivos de Court, Veo ni `anio_final`. Costo declarado US$ 0 |
| 6 | Sticker y MAPA | OK | `mapa_modulos.py --check`: 157 archivos de producción, 0 fallas. `fase2a.json` está en el diff |

Respuestas a tus puntos:
- (2) El test está en la raíz, no en `tests/`. El handoff dice `tests/test_module_f50g.py`, pero `tests/` no existe y los demás `test_module_*` están en la raíz, así que la lectura es correcta. No encontré dónde se declara el cambio de ruta. Es una desviación menor del handoff.
- (3) Es honesto, con el matiz de que son dos conteos distintos. El reporte dice «coincide con la simulación» y aclara que 94 son las 96 sin los cuadros Veo 1/1 y 7/1, y da también 59/37 sobre las 96. El 58/36 y la mediana 157,5 coinciden con lo que el handoff predijo. Lo del cuadro 1/1 y 7/1 (Veo) lo informa el reporte pero no el handoff.

Observaciones:
- Corrí `rearmar.py` en seco, como pediste. Eso reescribió `REARMADO_F50g.md` y `.json`, que están commiteados con el resultado de la etapa 2 (96/96). Ahora quedaron con la fila «sin grupos = guardado 37/96 … FALLA». Es lo esperado según tu aviso, pero el árbol de trabajo quedó con esa versión. Conviene `git checkout` de esos dos archivos antes del commit del reporte, o decidir cuál versión se conserva.
- Las repeticiones entre sujeto y aspecto, y el aspecto en fotos sin gente de cerca (la 7/7 de espaldas), están declarados en «Lo que queda abierto».

Fuera de alcance: ninguno en los commits de la tanda. Hay archivos sin commitear que ya estaban antes (`diag_234_cap4.py`, `TOPE_TANDA.json`, `f28a.log`). Sin commitear y propios de la tanda: `F50g_A_REPORT.md`, `ENTRADA_ANALISTA_2026-10-29b.md` (no lo revisé), `lab/hyperframes/f41/f50g/` y ESTADO_SESION.

Riesgos que el contrato no cubre:
- `03_visual.json` está en `data/`, que está en `.gitignore`: la única copia versionada del «antes» es `f50g/antes/`; el «después» no queda versionado.
- Los prompts suben a mediana 157,5 y máximo 273 palabras sin prueba de efecto. La prueba L contra C sigue pendiente.

### Adenda de CC (después del veredicto)
- **Punto (2), el test en la raíz:** el cambio de ruta está declarado en la sección «Etapa 1» de este reporte: «Tests en `test_module_f50g.py`, en la raíz. El handoff dice `tests/test_module_f50g.py`, pero el repo no tiene `tests/`…».
- **Observación 1:** `REARMADO_F50g.md/.json` volvieron a la versión commiteada en la etapa 2 (`git checkout HEAD --` de esos dos archivos). El árbol queda con la medida en seco de antes de escribir.
- **`ENTRADA_ANALISTA_2026-10-29b.md`:** no es de esta tanda, es del analista. No se toca ni se commitea.
- **Riesgo 1:** el «después» de `03_visual.json` se puede reconstruir: `PAPEL_FOTOS_WITTENOOM.json`, en git (40ea9ee), trae cada prompt nuevo entero.

