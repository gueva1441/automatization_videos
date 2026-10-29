# F51d-A — Wittenoom: m03 en texto con el armado C, el canon F51b y los arreglos F51c → papel de fotos · PARADA

CC → Omar / analista · 2026-10-29 · rama `f11-guion-v4` · gasto **US$ 2,2653 de 3,00** · **cero fal** (ni fotos, ni clips, ni foto madre) · handoff `HANDOFF_F51d_A_m03_en_texto.md`, md5 `e636a00d679e54d0fb6162eaaba8e511` (coincide).

## Commits
| etapa | commit | qué |
|---|---|---|
| 0 | `7b6b112` | DECISIONES 12:28 tal cual + chascada de rótulos + `test_module_f51d.py` (incluye el handoff) |
| 1 | `7c9860b` | copia del 03_visual anterior en `f51d/antes/` y el log de m03 (`f51d/m03.log`) |
| 2 | `122a3b8` | papel (`PAPEL_FOTOS_WITTENOOM.md/.json`), `MEDIDAS_F51d.md` + `medidas_f51d.py`, contrato F51a fijado |
| cierre | (este) | reporte, ESTADO, logs de `lab/hyperframes/f41/f51d/` |

El `03_visual.json` nuevo está en `data/`, que está en `.gitignore`: no va en ningún commit. md5 antes `59a8484d…` → después `72fdd85c…`.

## Etapa 0 — DECISIONES y chascada
`tail -1 DECISIONES.md`:
```
- 2026-10-29 12:28 · **F51d-A:** Wittenoom corre m03 en texto (casilleros con Opus + armado C + canon F51b + arreglos F51c), tope US$ 3, cero fotos y cero clips; el papel de fotos lo revisa el analista y Omar da el OK antes de generar (F51d-B) · Omar · F51d
```
Chascada (F51c, abierto 4 y riesgo 3 del revisor):
- `m03_expediente.py` l. 168–172 rotula el respaldo en el origen: «2) el último año dicho en la narración de los caps anteriores», «3) la fecha del dato_central del beat», «4) topic_year».
- `m03_imagenes_v3.anio_final` devuelve `tuple(e["respaldo"])` tal cual: se borra el `re.sub`.
- `test_module_f51d.py` (3, parametrizado): `mexp.expedientes` da cada uno de los 3 rótulos, y `anio_final` los pasa sin tocar (y con `year` válido gana «1) el casillero `year` del modelo»). `test_module_f50b.py` al rótulo nuevo.
- f51d + f51c + f50b: 29 passed · rápida 55 · contrato F51a 20/20 · stickers (`m03_expediente`, `m03_imagenes_v3`: md5) y `mapa_modulos.py --check`: 157 archivos · 0 fallas.

## Etapa 1 — m03 de Wittenoom
- Copia: `lab/hyperframes/f51d/antes/03_visual.json` (md5 `59a8484d…`, igual al vivo antes de correr).
- `lab/TOPE_TANDA.json` = `{"usd": 3.0, "desde": "2026-10-29T12:37:02"}` (fuera de git).
- Antes de correr: la marca del canon guardada y la calculada coinciden (`4828d0e6`), así que `asegurar_canon` no llama a Opus. `--only m03` corta en `fase1_5.py` l. 684, antes de la foto madre (l. 690): sin fal.
- `PYTHONIOENCODING=utf-8 python fase1_5.py --topic 123bbb64-9fca-4395-8bf4-57d60e219ef1 --only m03` → **exit 0, PASS 1, PARADA 0**. Los 7 caps en paralelo con los workers que ya tiene m03 (sin cambiar código).

| cap | motor | fotos | sin period | anclas por fallback |
|---|---|---|---|---|
| 1 | veo (start) | 1 + 4 | 0 de 5 | no |
| 2 | flux | 16 | 0 de 16 | no |
| 3 | flux | 16 | 0 de 16 | no |
| 4 | flux | 14 | 0 de 14 | no |
| 5 | flux | 16 | 0 de 16 | no |
| 6 | flux | 16 | 0 de 16 | no |
| 7 | veo (end) | 1 + 12 | 0 de 13 | no |

- Total 96 fotos. Ninguna línea «anchors por fallback determinístico» en el log.
- **Cap 3:** `[03][audit] cap 3: matcher anchor→tiempo no resolvió (anchor sin match o starts no crecientes) — sin reconciliación temporal`. No es PARADA; el cap salió «✓ 16 imgs validadas». Ver abierto 3.
- **Gasto** (log de m03 = `cost_history` = `01_v3_costos` «m03»): **US$ 2,2653**.

| paso | llamadas | in / out | US$ |
|---|---|---|---|
| m03:casilleros (Opus 5.5) | 7 | 218.734 / 63.839 | 2,1517 |
| m03:motion (Opus 5.5) | 3 | 3.232 / 730 | 0,0275 |
| anclas (Gemini 2.5 Flash, «motor sin tag») | 7 | 4.852 / 2.692 (think 31.152) | 0,0861 |
| canon | 0 | — | 0 |

  `cost_history`: 1 registro del tema desde 12:37:02 (created_at 12:37:14, total 2,26531, 17 entradas).

## Etapa 2 — papel y medidas
`python lab/hyperframes/f50/papel.py --salida lab/hyperframes/f51d/`:
```
fotos 96 (antes 96) · fuentes {'1) el casillero `year` del modelo': 96} · rehechas 0 (video 0) · carteles 8 · US$ 2.2653
```
`MEDIDAS_F51d.md` (lo generó `medidas_f51d.py`, escrito por un subagente y probado sobre `antes/`, donde la medida 1 daba 20 como se esperaba):

1. **Fotos con un `people_group` que no está en el canon vivo: 0** (antes 20).
2. **Fotos con todos sus grupos sin `appearance`: 6.** Para ver si el sujeto ya trae la etnia:

| foto | grupo | `subject` (casillero) |
|---|---|---|
| 4/3 | wittenoom_town_residents | small figures of children scattered across a town ground … (sin etnia) |
| 5/9 | australian_airport_police | … a mid-1980s Australian police officer … (sin etnia) |
| 5/12 | wittenoom_town_residents | … a lone sun-weathered Anglo-Australian resident in his sixties … |
| 6/7 | asbestos_victims_advocates_and_lawyers | A middle-aged Anglo-Australian woman advocate, medium build … |
| 6/8 | wittenoom_town_residents | Middle-aged Anglo-Australian adults in their sixties … |
| 7/4 | environmental_assessors | A few adult Anglo-Australian environmental assessors, lean builds … |

   4 de 6 traen la etnia en el sujeto; 4/3 y 5/9 no.
3. **Fotos con un texto de `condition_by_period` en el prompt: 0.**
4. Prompts enteros de 2/9, 4/11, 4/12 y 5/8: en el .md. (Las anclas se re-planearon: las posiciones ya no son las fotos con manchas de F51b.)
5. **6/3, 7/11 y 3/16:**
   - 6/3 (ancla del juez, 1988): «Western Australian Supreme Court courtroom, 1988», «Court» intacto, año 1988 de `year`.
   - El ancla del Tribunal Federal quedó en **7/10**, no en 7/11: «The words "Federal Court" are written over the entrance in carved, in clear crisp lettering.» «Court» intacto. 7/11 es ahora otra ancla («Nadie ha empezado a limpiar.»), sin «Court».
   - 3/16 (los Écija bajan del avión): **1962**, de `year`; el lugar también dice 1962.
6. **Caps 1 y 7: ninguna ancla a mitad de palabra** (tampoco a mitad de oración):

| cap | foto | rol | ancla | posición |
|---|---|---|---|---|
| 1 | 1/1 | Veo | «Un hombre joven posa para una foto con el pie envuelto en una venda blanca.» | 0–75 |
| 1 | 1/2 | apoyo | «En el retrato de familia todos miran a cámara menos el pie: …» | 116–244 |
| 1 | 1/3 | apoyo | «El hombre se llama Daniel Écija y es minero.» | 245–289 |
| 7 | 7/1 | Veo | «No se ha retirado una sola palada de asbesto. ¿Quién va a sacar la primera palada de esa tierra?» | 1137–1233 |
| 7 | 7/12 | apoyo | «En los accesos al pueblo y desfiladero hay bloqueos.» | 989–1041 |
| 7 | 7/13 | apoyo | «El gobierno de Australia Occidental habla de un «grave problema de salud y seguridad pública».» | 1042–1136 |

   En F51c, 7/13 terminaba en «seguri|». Los 2 `video_prompt`, enteros y tal cual, están en el .md (§6).
7. **`anio_fuente`:** «1) el casillero `year` del modelo» 96 de 96 (antes: 67 `year` + 29 ancla).
8. **Palabras por prompt:** mediana **115**, máximo **155** (2/1); antes 157,5 y 273.
9. **Gasto por paso:** ver la etapa 1. Total de la tanda: US$ 2,2653.

**Contrato F51a.** Después de m03 dio **0/20**. Era lo esperable: leía los casilleros del `03_visual.json` vivo, y m03 los rehízo. Lo fijé a `f51d/antes/03_visual.json`, que es el vivo de hasta hoy (md5 `59a8484d…`, el mismo con el que dio 20/20 en F51a, F51b y F51c). Es el mismo caso que en F51b con el canon. Con eso: **20/20 byte a byte iguales a PROMPTS_F50h.json → C**.

## Al cerrar
`bash lab/hyperframes/f41/verificar.sh f51d` (logs en `lab/hyperframes/f41/f51d/`):
```
md5: f792f3d483a1fa42daed5f7f0e054f46 *output/ba6c3cac-a091-41c0-8dad-afd2f4364747/_fase2b_work/ch02_segment_only.mp4
rapida: 55 passed, 3 skipped in 3.06s
amplia: 4 failed, 1007 passed, 30 skipped, 4 warnings in 68.96s (0:01:08)
FAILED test_module_m03_merge_timing.py::test_c_veo_path_y_veo_anchor_intacto
FAILED test_module_m03_merge_timing.py::test_c_guarda_de_minimo - AssertionEr...
FAILED test_module_gfx_lab.py::test_cues_sin_escribir_el_proyecto - Assertion...
FAILED test_module_gfx_lab.py::test_preview_usa_las_plantillas_reales - asser...
```
- Candado ch02 `f792f3d4…` sin cambio; rápida 55.
- Amplia: 1007 passed + 4 failed, las 4 previas de siempre. La cuenta: F51c 1003 + la intermitente de entonces (pasó esta vez) + 3 de `test_module_f51d.py` = 1007.
- Contrato F51a 20/20. Stickers + `MAPA --check`: 157 · 0 fallas (etapa 0; las etapas 1 y 2 no tocan producción).
- Cero fal: `--only m03` no llega a la foto madre. `find output data -newer lab/TOPE_TANDA.json -type f`, sin contar `output/ba6c3cac…/_fase2b_work/`, que es donde `verificar.sh` rearma en local el candado ch02 y el gfx_lab, da solo 3 archivos: `data/cost_history.json`, `01_v3_costos.json` y `03_visual.json` de Wittenoom. Ningún png ni mp4 de Wittenoom.

## Lo que queda abierto
1. **Revisión del papel** (`PAPEL_FOTOS_WITTENOOM.md`) por el analista, con formato DEBERÍA. Después, el OK de Omar para F51d-B. No se generó nada.
2. **2 fotos sin aspecto y sin etnia en el sujeto:** 4/3 (niños del pueblo) y 5/9 (policía del aeropuerto). Sus grupos tienen `appearance` vacío desde F51b. Las otras 4 de la medida 2 traen la etnia en el `subject`.
3. **Cap 3: sin reconciliación temporal.** El matcher ancla→tiempo no resolvió. Por eso m03 no fusionó las fotos de apoyo demasiado juntas en ese cap, y puede haber fotos muy cortas en pantalla. No es PARADA, pero conviene mirarlo antes de F51d-B: los tiempos están en el papel.
4. **«sun-weathered» en un `subject` (5/12).** Opus lo escribió en el casillero, no viene del aspecto del canon. Va con la decisión pendiente de F51b sobre el estado en el aspecto.
5. **Cartel de 7/10:** «in carved, in clear crisp lettering». El casillero `font` vino «carved» y el armado lo pega tal cual. No es de esta tanda (el armado no se toca); lo anoto para el analista.
6. **Contrato F51a:** ahora lee `f51d/antes/03_visual.json`. Si se borra esa copia, el contrato deja de correr.
7. **Las anclas se re-planean en cada corrida**, así que las posiciones de F51b y F51c (2/9, 4/11, 4/12, 5/8, 7/11) ya no son las mismas fotos. Las medidas 4 y 5 dan las dos cosas: la posición y la búsqueda por texto.
8. Siguen de antes: el prompt de video Veo con la guía de Google (tanda aparte; los 2 `video_prompt` salieron con el código de siempre); la foto madre con el canon nuevo (F51d-B); `track_gemini_vision` (F51e); los scripts de lab rotos de F51c (abierto 2) y `_lab_name_scrub.py`; las 4 fallas previas de la suite.

## Veredicto de revisor-handoff
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | md5 del handoff en el reporte | OK | `md5sum` da e636a00d…; el reporte l.3 lo cita |
| 2 | DECISIONES: línea 12:28 tal cual, al final | OK | `git diff` de DECISIONES.md: +1 línea idéntica al handoff |
| 3 | Chascada: rótulo «2)/3)/4)» en el origen, regex borrado, test de los 3 rótulos | OK | `m03_expediente.py` l.168-172; `m03_imagenes_v3.anio_final` ahora `return tuple(e["respaldo"])`; `test_module_f51d.py` con 3 casos |
| 4 | Suite rápida y contrato 20/20 | OK | Corrí `pytest test_module_f51d.py test_module_f50b.py`: 24 passed. `contrato.py` da exit 0 y «20/20 byte a byte iguales». El log de verificar muestra «rapida: 55 passed» |
| 5 | Copia previa de `03_visual.json` en `f51d/antes/` | OK | md5 59a8484d… en `antes/`; el vivo es 72fdd85c… |
| 6 | `TOPE_TANDA` en 3,00 y m03 con `--only m03`, sin PARADA | OK | `TOPE_TANDA.json` = 3.0. `m03.log`: PASS 1, PARADA 0, FAIL 0, 7 caps ✓ |
| 7 | Gasto ≤ US$ 3,00 | OK | `m03.log`: TOTAL US$ 2,2653. Coincide con `cost_history` (2,26531, 17 entradas) |
| 8 | Log por cap: fotos, sin period, anclas por fallback | OK | `m03.log`: 0 sin period en los 7 caps, 96 fotos (5+16+16+14+16+16+13). No aparece la línea de fallback |
| 9 | Cero fal | OK | `find output data -newer TOPE_TANDA.json` (sin `_fase2b_work`) da solo `cost_history.json`, `01_v3_costos.json` y `03_visual.json`. No hay png ni mp4 |
| 10 | Papel `PAPEL_FOTOS_WITTENOOM.md/.json` en `f51d/` | OK | Los dos existen, no están vacíos y están en el commit 122a3b8 |
| 11 | `MEDIDAS_F51d.md` con las 9 medidas y su lista | OK | Está en el repo; las 9 secciones están en las l.12-218 del .md. Rehíce `medidas_f51d.py` y el resultado es idéntico al commiteado |
| 12 | Medida 1 = 0 y medida 3 = 0 | OK | Reporte §Etapa 2 (1: 0, 3: 0). Coincide con mi rehecha del .md |
| 13 | Medidas 4 a 6 (prompts enteros, Court/año, anclas Veo y vecinas sin corte a mitad de palabra) | OK | .md §4-§6; el reporte explica que las anclas se re-planearon y que el Tribunal Federal pasó a 7/10 |
| 14 | Candado ch02 f792f3d4… | OK | El log de verificar da md5 f792f3d483a1… |
| 15 | Suite amplia | PARCIAL | Log: 4 failed, 1007 passed. Son `test_module_m03_merge_timing` (2) y `test_module_gfx_lab` (2). El reporte los llama «previas de siempre», pero no corrí la amplia para confirmarlo |
| 16 | Stickers y `MAPA --check` | OK | Corrí `mapa_modulos.py --check`: 157 archivos, 0 fallas |
| 17 | Commit por etapa con F51d-A | OK | 7b6b112, 7c9860b, 122a3b8 |
| 18 | `F51d_A_REPORT.md` con lo abierto entero y el veredicto | PARCIAL | Existe, con 8 abiertos. Quedan `{{SUITES}}` y `{{VEREDICTO}}` sin llenar. El ESTADO se actualiza después |
| 19 | No tocar canon, pedido del canon, `cost_tracker`, armado (salvo chascada) ni prompt Veo | OK | `git diff 3045d93 HEAD` en `script_engine/` solo toca `m03_expediente.py` y `m03_imagenes_v3.py`, y solo en las líneas de la chascada |

Fuera de alcance:
- `lab/hyperframes/f51a/contrato.py` (commit 122a3b8). No está en la tabla de módulos del handoff. El cambio es mínimo (lee `f51d/antes/03_visual.json`), está declarado y era necesario: sin él el contrato daba 0/20. Es una observación, no una falla.
- `lab/hyperframes/f51d/medidas_f51d.py`: script nuevo, necesario para las medidas.
- Los archivos modificados que ya figuraban en el estado inicial (`diag_234_cap4.py`, `lab/hyperframes/f28/a/f28a.log`) no son de esta tanda.
- `lab/TOPE_TANDA.json` quedó en 3,0 sin commit (el reporte lo dice).

Riesgos que el contrato no cubre:
- El contrato F51a ahora depende de que exista `f51d/antes/03_visual.json`. Si se borra, deja de correr (abierto 6 del reporte).
- El cap 3 no tuvo reconciliación temporal (matcher ancla→tiempo sin resolver). Puede haber fotos muy cortas en pantalla (abierto 3 del reporte).
- Quedan sin aspecto ni etnia en el sujeto las fotos 4/3 y 5/9 (abierto 2 del reporte). Además, 7/10 dice «in carved, in clear crisp lettering» (abierto 5).

### Adenda de CC (después del veredicto)
- **#4, 24 contra 29:** el revisor corrió 2 archivos (f51d y f50b); CC corrió 3 (más f51c): 29 passed.
- **#15, las 4 fallas:** son las mismas 4 que en `lab/hyperframes/f41/f51b/suite_amplia.log` y `f51c/suite_amplia.log`: `m03_merge_timing::test_c_guarda_de_minimo`, `m03_merge_timing::test_c_veo_path_y_veo_anchor_intacto`, `gfx_lab::test_cues_sin_escribir_el_proyecto` y `gfx_lab::test_preview_usa_las_plantillas_reales`. Esta vez no hubo fallo intermitente de `gfx_lab`.
- **#18:** `{{SUITES}}` y `{{VEREDICTO}}` quedaron llenos en el commit del reporte.
