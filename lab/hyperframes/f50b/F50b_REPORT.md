# F50b — Tres bugs del armado y el papel re-armado en seco (US$ 0)

Handoff `lab/hyperframes/f50/HANDOFF_F50b_tres_bugs_del_armado.md`, md5 `7c816ed03b8196d81f80e4d7060b5172` (verificado). Tema Wittenoom `123bbb64-9fca-4395-8bf4-57d60e219ef1`, rama `f11-guion-v4`. **Cero llamadas a modelos, cero fal, cero fotos.** La foto madre no se tocó.

Lecturas: `CLAUDE.md`, `DECISIONES.md` (hasta 21:23), `lab/ESTADO_SESION.md` (bloque F50), el handoff, el código de `armar`/`f8_backstop`/`frase_cartel` (`m03_imagenes_v3.py`) y `_render_prompts_seedream` (`m03_visual.py`).

## Paso 0
`DECISIONES.md`, última línea, tal cual: «2026-10-28 21:23 · Foto madre de Wittenoom: se regenera con el canon nuevo de la ficha en la tanda de fotos (F51); la `subject.png` vieja pasa a `lab/hyperframes/f50/antes/` y no se adopta · Omar · F51». La `subject.png` **no** se movió: el pedido de Omar dice que la foto madre no se toca en esta tanda; queda para F51.

## Módulo que toca
`script_engine/m03_imagenes_v3.py` (sticker `fase2a`: «reglas de las imágenes del guion v3: … arma la frase de cada imagen desde sus casilleros en un orden fijo …»). Después: lo mismo, y antes de armar saca las cláusulas negadas de cada casillero y baja a minúscula lo que queda en mitad de oración. Sticker actualizado; `MAPA_PROYECTO` regenerado, `--check`: «157 archivos de producción · 0 fallas».

## Arreglos 1–3
1. **`HARM`**: `shot` → `shot\s+(?:dead|down)|gunshot\w*`; fuera `body|bodies` (los cubre `BODY`).
2. **`_sin_negadas(texto)`** (nueva): en cada casillero de prosa (`subject`, `action`, `gaze_interaction`, `props_detail`, `setting`, `lighting`, `color_palette`, `camera_angle`, `lens_technique`) saca la cláusula entre `,` `;` `.` que empieza con `no|nobody|nothing|never|none`, con `with` delante opcional. `without` no se toca. Si el `setting` queda vacío, se omite la oración de lugar y año (el año sigue en el estilo). En Wittenoom ningún casillero quedó vacío.
3. **`_minuscula_media(x)`** (nueva): `camera_angle`, `lens_technique`, `font` y, en `location` con preposición de `_PREP_LUGAR`, la preposición inicial: primera letra a minúscula si la primera palabra es «Xxxx» (≥ 2 letras, mayúscula y después ninguna mayúscula). Toda en mayúsculas o con cifra al inicio, igual.

Constantes nuevas: ninguna (palabras de gramática inglesa, declaradas en el handoff).

Tests (`test_module_f50b.py`, 18 → 21, todos verdes):
- `test_f50b_plano_con_shot_no_es_menor_en_danio`: «Wide shot, eye-level, child's height…» sin problemas; «The boy was shot dead.» da «menor en daño».
- `test_f50b_clausula_negada_sale_del_setting`: «with no figure anywhere» sale del `setting`; «swings without seats» queda; un `setting` que queda vacío se omite.
- `test_f50b_minuscula_en_mitad_de_oracion`: «shot, Eye-level» → «shot, eye-level»; «Over the entrance» → «over the entrance»; «Federal Court» no cambia; «DSLR», «35mm» quedan.

## Re-armado en seco (paso 2)
Copia previa: `lab/hyperframes/f50b/antes/03_visual.json` (md5 `85d1f969…`, igual al de producción antes de escribir).
Script: `lab/hyperframes/f50b/rearmar.py`. Toma los casilleros guardados (`raw_llm_prompt`, que ya pasaron por `scrub_slots`/`fix_text_slot`) y el `anio` de cada foto, y corre `armar` → `f8_backstop` (con la `escala` del beat y `documented_people`) → `_sacar_frases_con_texto`, igual que `_render_prompts_seedream`.

**Control antes de tocar el código:** con el código de F50, `rearmar.py --igual` → «fotos 96 · iguales 96 · distintas []». El re-armado reproduce byte a byte los 96 prompts guardados.

Escritura: solo `prompt` (o `image_prompt` en el primer cuadro del cap 7) de las 33 que cambian. `sensible` y `motivos` se recalcularon sobre el prompt nuevo y dieron los mismos valores. Comparación clave por clave de antes/después de `03_visual.json`: 33 diferencias, 32 `prompt` + 1 `image_prompt`, nada más. md5 nuevo `23a81881…`.

Los `video_prompt` de los caps 1 y 7 **no se rehicieron** (handoff §2): no traen negaciones, y el primer cuadro del cap 7 cambia solo en la cláusula negada y la técnica. El cap 1 no tiene ninguna foto que cambie.

## DIFF_PAPEL (paso 3), salida pegada
```
cambian 33 · 1=3 2=4 3=29 {'tecnica': 29, 'texto': 2} · PASA
```
De `lab/hyperframes/f50b/DIFF_PAPEL.md`:
- Fotos: 96 · cambian: 33 · iguales: 63
- Arreglo 1 (`HARM`): 3 fotos [(2, 13), (4, 1), (5, 16)] · tabla [(2, 13), (4, 1), (5, 16)]
- Arreglo 2 (cláusulas negadas): 4 fotos [(4, 14), (6, 1), (7, 1), (7, 11)] · tabla [(4, 14), (6, 1), (7, 1), (7, 11)]
- Arreglo 3 (minúscula en mitad de oración): 29 fotos · oración de plano 29 (tabla 29) · carteles 2 (tabla 2) · otras partes tocadas: ninguna
- Cambios sin arreglo que los explique: ninguno
- **Resultado: PASA**

Cómo se atribuye: un arreglo «toca» una foto si al apagar solo ese arreglo cambia el prompt. Para el arreglo 3, además, se verifica qué parte del armado cambió: solo `tecnica` (29) y `texto` (2).

Las 29 de la técnica son las 16 del cap 5 y las 13 del cap 7. Los 2 carteles son del cap 7 («written over the entrance in metal block letters» y «written on the warning sign … in bold block stencil»). Las 33 fotos son 3 + 4 + 29 menos 3 que se repiten: 5/16 (arreglos 1 y 3), 7/1 y 7/11 (arreglos 2 y 3).

Lo que entra y sale en las 7 de los arreglos 1 y 2:
- 2/13 y 4/1: vuelve la oración de plano «Wide shot, eye-level, child's height, …».
- 5/16: vuelve «Sitting very still, body curled forward toward one photograph of a bandaged infant foot».
- 4/14: sale «never looking back».
- 6/1: sale «with no figure anywhere».
- 7/1: salen «nobody has dug and the shovel stands unused» y «no machinery anywhere».
- 7/11: sale «no work, no vehicles».

## Papel regenerado (paso 4)
`python lab/hyperframes/f50/papel.py --salida lab/hyperframes/f50b`. El único cambio en `papel.py` es el argumento `--salida`; sin él escribe en `f50/` como antes.
```
fotos 96 (antes 96) · fuentes {'2) el casillero `year` del modelo': 68, '1) dicho en el ancla': 28} · rehechas 0 (video 0) · carteles 10 · US$ 2.1205
```
Contra el papel de F50: 33 fotos difieren, y solo en `prompt`. Los US$ 2,1205 son el registro de F50 D en `cost_history`; F50b no gastó nada.

## Verificación
| | antes (F50 D, `f41/f50_D`) | después (`f41/f50b`) |
|---|---|---|
| suite rápida | 55 passed, 3 skipped | 55 passed, 3 skipped |
| suite amplia | 4 failed, 944 passed, 30 skipped | 4 failed, 947 passed, 30 skipped (944 + 3 tests nuevos) |
| ch02 md5 | `f792f3d4…` | `f792f3d483a1fa42daed5f7f0e054f46` (igual) |

Fallas de la amplia: las mismas 4 de antes, que ya estaban en F49 (`f49/verif_p1/suite_amplia.log`): `gfx_lab::test_cues_sin_escribir_el_proyecto`, `gfx_lab::test_preview_usa_las_plantillas_reales`, `m03_merge_timing::test_c_guarda_de_minimo`, `m03_merge_timing::test_c_veo_path_y_veo_anchor_intacto`.

## Lo que queda abierto
1. **Notas F8 viejas en el papel.** El handoff pide escribir solo `prompt`/`sensible`/`motivos`, así que `_f8_problemas` sigue con las notas de F50. En el papel nuevo, 2/13, 4/1 y 5/16 todavía muestran «menor en daño: …», aunque ese problema ya no existe y la frase volvió. Las 4 del arreglo 2 no tienen nota (la negación nunca fue nota F8). Si se quiere, en la tanda de fotos las notas se recalculan solas.
2. **Foto madre**: la `subject.png` vieja sigue donde estaba y la ruta en topics_db sigue vacía (F50 n4). Se mueve a `f50/antes/` y se regenera en F51, según DECISIONES 21:23.
3. Del handoff, a la lista y sin arreglar:
   - «loosely wound» lo corta la F8 como «wound» (1/1);
   - «blue asbestos veins» lo corta como manos/cara (3/2, solo la paleta);
   - «in typewriter» / «in typewritten» en la letra de 2 carteles;
   - 5/16 dice «a baby's bandaged foot» donde debería ser el pie del joven (Daniel, cap 1): error del modelo, se arregla en QA Studio con la foto.
4. **Mayúsculas en otros casilleros.** El arreglo 3 solo toca los casilleros que van en mitad de oración según el handoff. En `setting` siguen mayúsculas del modelo que pueden ser nombres propios, como 7/1 «Abandoned Colonial mine waste dump». No se tocaron.
5. **`_minuscula_media` no distingue nombres propios.** Si `camera_angle`, `lens_technique` o `font` empiezan con un nombre propio de la forma «Xxxx» (una marca de lente, por ejemplo), lo baja. En Wittenoom no hay ninguno; lo dice la regla del handoff.
6. **Atribución.** La verificación cuenta fotos por arreglo y las compara con la tabla. Las 29 de la técnica salen de un conteo, no de una lista por foto, porque la tabla del handoff no las enumera.
7. Siguen abiertos de F50: n2 (gasto sin registrar de la corrida cortada), n3 (canon con 7 grupos), n7 (no hay camino de fotos sin escaleta), n8 (el cap Veo no se midió contra el lab), n10 (precio real de Veo 4 s), n12 (claves nuevas de `03_visual` contra m06). Ninguno se tocó acá.
8. Fecha límite: fal apaga Veo 3.1 el 2026-11-17.

## Procesos
Un solo proceso en segundo plano, `verificar.sh f50b` (md5 y suites), y terminó con exit 0. No quedó ningún subagente ni shell abierto. No se cerró ningún programa de Omar.

## Veredicto de revisor-handoff
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 0 | Handoff íntegro (md5 7c816ed0…) | OK | `md5sum` coincide. |
| 1 | Paso 0: línea de DECISIONES 21:23 tal cual | OK | `git diff DECISIONES.md`: línea agregada con el texto del handoff. |
| 2 | Foto madre no se toca | OK | El reporte lo declara. `git status` no muestra ningún cambio en `subject.png`. |
| 3 | Arreglo 1: `HARM` | OK | `m03_imagenes_v3.py`: `shot\s+(?:dead\|down)\|gunshot\w*`, y se quitan `body\|bodies`. Coincide con el handoff. |
| 4 | Arreglo 2: `_sin_negadas` | OK | Cláusulas entre `,;.` que empiezan con no/nobody/nothing/never/none, con `with` opcional. `without` no se toca. Un casillero vacío se omite. Se aplica a los 9 casilleros de prosa. |
| 5 | Arreglo 3: minúscula en mitad de oración | OK | `_minuscula_media` solo baja palabras «Xxxx». Se aplica a `camera_angle`, `lens_technique`, `font` y a la preposición inicial de `location` (lista cerrada `_PREP_LUGAR`). Los tests cubren «Federal Court», «DSLR» y «35mm». |
| 6 | Tests de §Pasos 1 (7 casos) | OK | `test_module_f50b.py` pasó de 18 a 21 tests. Corrí `pytest -q test_module_f50b.py`: 21 passed. |
| 7 | Módulos: solo `HARM`, `armar` y `_sin_negadas` | PARCIAL | Se agregó además `_minuscula_media` y se modificó `frase_cartel`. Es necesario para el arreglo 3, pero el handoff nombra solo `HARM`, `armar` y `_sin_negadas`. Ver observación 3. |
| 8 | Copia previa de `03_visual.json` | OK | Existe `lab/hyperframes/f50b/antes/03_visual.json`. |
| 9 | Re-armado en seco de las 96 fotos | OK | Corrí `rearmar.py --igual` sobre el `03_visual.json` de producción: 96 iguales, 0 distintas, es decir que lo guardado coincide con el código de hoy. Corrí `rearmar.py` en seco: «cambian 33 · 1=3 2=4 3=29 {'tecnica': 29, 'texto': 2} · PASA». |
| 10 | Se escribe solo `prompt` (y `sensible`/`motivos`) | OK | Comparé clave por clave `antes/03_visual.json` contra el de producción: 33 diferencias, todas `prompt` o `image_prompt`. Las 32 que están bajo `image_prompts`/`supplemental_image_prompts` son `prompt`, y la del cap 7 (`/chapters/6/image_prompt`) es `image_prompt`. Ninguna toca `video_prompt`. |
| 11 | DIFF_PAPEL con verificación contra la tabla | OK | `rearmar.py:27-29` fija la tabla del handoff (2/13, 4/1, 5/16; 4/14, 6/1, 7/1, 7/11; 29 de técnica y 2 carteles). `rearmar.py:105-114` marca falla si el conjunto difiere, si el arreglo 3 toca otra parte del armado o si algo cambia sin arreglo que lo explique. `DIFF_PAPEL.json` tiene `fallas: []`. |
| 12 | Papel regenerado en `f50b/` | OK | `PAPEL_FOTOS_WITTENOOM.md` y `.json` existen y no están vacíos. El único cambio en `papel.py` es `--salida`. |
| 13 | Sticker y MAPA al día | OK | El md5 del sticker (38d665f1…) coincide con el archivo actual. `MAPA_PROYECTO` regenerado; el reporte indica `--check` 0 fallas. No lo re-corrí. |
| 14 | Suites antes/después | OK | Rápida: 55 passed, 3 skipped, igual antes y después. Amplia: antes 4 failed, 944 passed, 30 skipped; después 4 failed, 947 passed, 30 skipped. Son las mismas 4 fallas previas, y la diferencia son los 3 tests nuevos. Logs en `lab/hyperframes/f41/f50b/` y `f50_D/`. |
| 15 | Candado de ch02 | OK | `onlycap_ch02_nogfx.log` termina en md5 f792f3d483a1fa42daed5f7f0e054f46, el mismo de antes. |
| 16 | `F50b_REPORT.md` con lo abierto entero | OK | Sección «Lo que queda abierto» con 8 puntos. Incluye los 4 «a la lista» del handoff, las notas F8 viejas, la foto madre y los abiertos de F50. El marcador `{{VEREDICTO}}` sigue sin llenar y es correcto, porque se llena con este veredicto. |
| 17 | `ESTADO_SESION` actualizado | OK | `lab/ESTADO_SESION.md` línea 3 y bloque F50b (líneas 17-19). |
| 18 | Cero modelos, cero fal | NO VERIFICABLE | El código es determinista y no hay llamadas en `rearmar.py`. El reporte declara US$ 0, pero no pude auditar `cost_history`. |

Observaciones:
1. Las notas F8 de 2/13, 4/1 y 5/16 en el papel nuevo siguen diciendo «menor en daño», porque el handoff manda escribir solo `prompt`/`sensible`/`motivos`. El reporte lo declara (abierto 1). El papel puede confundir al leer, aunque el prompt ya esté bien.
2. La verificación de las 29 fotos de técnica compara un conteo, no una lista por foto, porque la tabla no las enumera. El reporte lo declara (abierto 6).
3. `_minuscula_media` baja cualquier palabra «Xxxx» al inicio, incluidos nombres propios. El handoff lo permite. El reporte lo declara (abierto 5).

Fuera de alcance: ninguno nuevo. `diag_234_cap4.py`, `lab/TOPE_TANDA.json` y `lab/hyperframes/f28/a/f28a.log` ya estaban modificados antes de esta tanda. Los archivos nuevos (`lab/hyperframes/f50b/`, `lab/hyperframes/f41/f50b/`, el propio handoff y `ENTRADA_ANALISTA_2026-10-27g.md`) están en el alcance.

Riesgos que el contrato no cubre: (a) `_sin_negadas` corta por coma, así que una cláusula negada con comas internas, por ejemplo «no work, no vehicles», se saca bien, pero una frase como «never, ever, looking» dejaría restos. En Wittenoom no ocurre. (b) Los `video_prompt` de los caps 1 y 7 no se rehicieron, y el primer cuadro del cap 7 cambió en la técnica y en la cláusula negada. Si el clip se genera desde el prompt viejo, puede no coincidir con el primer cuadro nuevo. (c) El commit incluye `lab/TOPE_TANDA.json` y otros archivos modificados antes de la tanda, y conviene stagearlos de forma selectiva.

### Adenda de CC (después del veredicto)
- **#7, `_minuscula_media` y `frase_cartel`:** el arreglo 3 del handoff pide bajar `font` y la preposición de `location`, y las dos viven en `frase_cartel`, que `armar` llama. No se tocó ningún otro módulo.
- **#18, US$ 0:** `rearmar.py` y `papel.py` solo leen y escriben archivos. No se abrió ningún `cost_tracker`, y `cost_history.json` no cambió en esta tanda: fuera del lab, git no muestra cambios en `data/`, y el papel sigue mostrando el mismo último registro de F50 D, US$ 2,1205.
- **Riesgo (b), el clip del cap 7:** el `video_prompt` es el movimiento, y Veo lo aplica sobre el primer cuadro que se genere. La foto sale del `image_prompt` nuevo y no hay nada que pueda «no coincidir». Lo que no se rehízo es el texto del movimiento, como manda el handoff §2.
- **Riesgo (c):** el commit va por rutas explícitas; `TOPE_TANDA.json`, `diag_234_cap4.py` y `f28a.log` quedan fuera.

