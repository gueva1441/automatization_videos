# F73 — miniaturas con foto madre y sello de narración; QA muestra toda la voz de cada foto; D en PARADA

Topic 123bbb64-9fca-4395-8bf4-57d60e219ef1 (Wittenoom), rama f11-guion-v4, HEAD de partida 58915cc (render vigente F72e).
Fecha 2026-11-04. Costo total: **US$ 0,4468** (todo en A+B; C y D US$ 0).

## Resumen
- **A** hecho. Las fotos de los 3 paquetes nuevos se anclaron a la foto madre de Daniel Écija con la regla única (`am._madres_para_item`). Cada `llamada.json` trae `referencias_md5` lleno y endpoint `/edit`.
- **B** hecho. `metadata.json` lleva el sello `narracion_md5`. Los 3 paquetes viejos (sin sello) se movieron a `publish/_desfasado_20261104_073537/`, y en su lugar salieron 3 nuevos.
- **C** hecho. Cada segmento del QA lleva `voz`, el texto desde su ancla hasta la siguiente, y se ve en gris debajo del ancla. La cobertura da **100 % en los 7 caps**.
- **D: PARADA después de la simulación.** La regla del handoff (máscara «al menos una muestra ≠ 0» + float64) **no** lleva ch03/ch07 a ≈0: quedan en +4,600 s y +13,818 s. **`fase2b.py` no se tocó**, así que D no tiene tabla de la función real ni test. La causa y dos salidas posibles están en la sección D: decide el analista o Omar.
- `_fase2b_work/` tiene el mismo md5 en la etapa 0 y al final. GUION_PANTALLA.md sigue en 433eb3e5…. No se re-planeó, no hubo render y no se tocaron fondos ni prompts.

## Etapa 0 (solo lectura)
| qué | esperado | medido |
|---|---|---|
| HANDOFF_F73.md | 4f00a1fe33372fc5146cc0387fc7258f | igual ✓ |
| HANDOFF_F73_ADENDA.md | 2a6b2b07521aa2ea689dcd8bc5e737ff | igual ✓ |
| HEAD | 58915cc | 58915cc ✓ |
| GUION_PANTALLA.md | 433eb3e5… | 433eb3e584460e698483ae4fece9c8ce ✓ |
| `_fase2b_work/` (348 archivos, md5 de la lista `md5sum` ordenada) | — | `321f4c53b4bd8fb1dcfbe8b4e84d8c00` (`d/fase2b_work_md5_etapa0.txt`) |

## A — madres en la foto del paquete
Código, en `script_engine/m09_packaging.py`:
- **`madres_del_paquete(tid, item)`** llama a `am._madres_para_item` con los mismos argumentos que `qa_studio_server._madres_de_entrada`: `persona`, `foto_madre_ref`, `anio`, y `foto_madre_registry` / `foto_madre_personas` del guion vivo `data/scripts/<tid>.json`, más el `prompt`. No tiene tope ni filtro propios.
- **`foto_paquete(prompt, out, madres)`** pasa las madres como `foto_madre_data_uris` (`am._path_to_data_uri`). Sin madres va `None`, que es el t2i de siempre.
  - Se borró la llamada vieja sin madres, así que queda un solo camino.
  - `rehacer_foto` pasa por lo mismo, vía `_foto_del_paquete`.
- **`_foto_del_paquete`** guarda en el paquete `persona` y `foto_madre_refs`, que son las madres que anclaron.

Prueba real (los 3 paquetes nuevos):

| n | ancla | persona | foto_madre_refs | endpoint | referencias_md5 |
|---|---|---|---|---|---|
| 1 | «La familia que la guarda cuenta que le cayó encima un trozo de amianto y que la herida no cerraba.» | Daniel Écija | Daniel Écija | google/nano-banana-2-lite/edit | ae577008ad569f90426ebbb8303df37b |
| 2 | «Lo que sobró de la mina, en cambio, sigue ahí: más de tres millones de toneladas.» | Daniel Écija | Daniel Écija | google/nano-banana-2-lite/edit | ae577008ad569f90426ebbb8303df37b |
| 3 | «El hombre se llama Daniel Écija, es minero, y llegó de Madrid hace unos meses.» | Daniel Écija | Daniel Écija | google/nano-banana-2-lite/edit | ae577008ad569f90426ebbb8303df37b |

Los títulos y textos los eligió Opus; no se tocó el prompt de `pedir_paquetes`:
1. «La herida no cerraba: 10 meses en Wittenoom que lo mataron en Madrid» · «¿QUÉ RESPIRÓ ALLÍ?»
2. «Borraron el pueblo del mapa, no sus más de 3 millones de toneladas» · «¿ADÓNDE VA AHORA?»
3. «Wittenoom, 1963: un minero de Madrid y un polvo advertido en 1944» · «¿QUIÉN LO LLEVÓ ALLÍ?»

Ninguno trae avisos de cifras.

Las 3 miniaturas compuestas:
- `lab/hyperframes/f73/a/paquete_01.jpg`, `paquete_02.jpg` y `paquete_03.jpg`.
- La hoja `lab/hyperframes/f73/a/miniaturas_nuevas_arriba_viejas_abajo.jpg` pone las 3 nuevas arriba y las 3 archivadas abajo.
- Lectura de CC: en las 3 nuevas aparece el mismo minero, la cara de la madre de Daniel.
- La foto 2 (la de los relaves) también lleva a Daniel, porque los casilleros lo pusieron en `persona`. No lo corregí: es la regla única tal como es.

Costo de la corrida (`a/costo.json`, cost_tracker): US$ 0,4468.

| partida | US$ |
|---|---|
| Opus `m09:paquetes` | 0,198 |
| Opus `m03:casilleros` | 0,1228 |
| 3 fotos Nano Banana 2 Lite /edit (estimado del registro F68) | 3 × 0,042 |

## B — sello de narración
Código:
- **`m09_packaging.narracion_vigente(tid)`** devuelve el `aprobado.md5` de `01b_narracion_v3.json` si `fase1_5.estado_narracion` da aprobada y vigente; si no, None.
- **`archivar_paquetes_desfasados(tid)`** actúa si hay paquetes sin sello o con el sello de otra narración. Mueve a `publish/_desfasado_<ts>/`:
  - `thumb_candidates/`;
  - lo compuesto con esos paquetes (`thumb_final*.png`, `CHECKLIST_PUBLICACION.md`);
  - una copia entera del `metadata.json`.

  En el `metadata.json` vigente se quitan `paquetes`, `descripcion`, `tags`, `avisos` y los campos del final.
- **`run_candidates`**:
  - sin narración aprobada para con `PaquetesParada` («sin narración aprobada vigente no se generan paquetes (…)»);
  - si hay narración aprobada, archiva lo desfasado, genera de cero (los números arrancan en 1) y escribe `narracion_md5`.
- **`candidates_ready`** solo da True con el sello vigente, así que `fase3` regenera.
- **`m09_review_server.serve`** archiva al abrir y avisa. `run_pipeline._paso_packaging` archiva antes de diferir o de lanzar fase3.

Antes y después, en `output/<tid>/publish/metadata.json`:

| | antes (`b/metadata_antes.json`) | después |
|---|---|---|
| claves | topic_id, stage, paquetes, descripcion, tags, avisos | topic_id, stage, paquetes, descripcion, tags, **narracion_md5**, avisos |
| `narracion_md5` | (no existe) | `cd0fe3bfcc81bf45871f575c3c0077dc` (= `aprobado.md5` de 01b_narracion_v3.json) |
| paquetes | 3 (30-oct / 1-nov, ancla del 01 «Ese pie va a cerrar…») | 3 nuevos (n 1–3, tabla de A) |

- **Archivado:** `output/<tid>/publish/_desfasado_20261104_073537/`. Ahí quedan `thumb_candidates/` (las 3 viejas con sus bases), `metadata.json` (los 3 paquetes viejos, sin sello) y `CHECKLIST_PUBLICACION.md`. No se borró nada.
- **Lo que no se movió:** `publish/_antes_f58/`.
- **Narración del pedido:** `01b_narration.json`, la que lee `cargar_narracion`, tiene el mismo texto que la aprobada `01b_narracion_v3.json` en los 7 caps (comparado con los espacios juntados).

## C — toda la voz debajo de cada foto en QA
Esta etapa la hizo un subagente; revisé el diff.
- **`qa_studio_server.py`:**
  - Función nueva `voz_por_anclas(texto, anclas, primero_desde_inicio)`. Busca las anclas en orden y solo tolera diferencias de espacios. Cada tramo va del texto original, desde su ancla hasta la siguiente encontrada; el último llega hasta el final.
  - El clip que va primero arranca en el inicio del texto. El clip que va al final arranca en su ancla.
  - Si un ancla no se encuentra, su `voz` es solo el ancla.
  - `cap()` agrega `voz` a cada segmento en los tres caminos (flux, veo primero, veo al final). Tiempos, anclas y video no cambian.
- **Fuente del texto:** `chapters[].narration` de `data/scripts/<tid>.json`, el mismo archivo de donde salen las anclas.
- **`qa_studio.html`:** debajo del ancla, en la tarjeta y en el panel, se ve el resto de `voz` en gris (`#a5a5b8`, el gris que ya usa `.fc-sub`).

Cobertura por cap. Script de solo lectura con la función real (`lab/hyperframes/f73/c_cobertura.py`):

| cap | palabras narración | palabras suma `voz` | % | segmentos |
|---|---|---|---|---|
| ch01 (veo primero) | 181 | 181 | 100,0 % | 9 |
| ch02 | 220 | 220 | 100,0 % | 15 |
| ch03 | 384 | 384 | 100,0 % | 16 |
| ch04 | 232 | 232 | 100,0 % | 14 |
| ch05 | 267 | 267 | 100,0 % | 16 |
| ch06 | 299 | 299 | 100,0 % | 16 |
| ch07 (veo al final) | 197 | 197 | 100,0 % | 13 |

Todas las anclas se encontraron. Dos de ellas solo aparecen después de juntar los espacios: ch02 «Cuatro días después…» y ch06 «Daniel Écija es uno de ellos…».

Ejemplo ch03. Las 7 oraciones que antes no se veían en QA (están en `voz` y en ninguna ancla):
1. (foto 2) «, recuerda uno de los chicos que bajaron de ese avión.» (es la cola de la oración de la cita que hace de ancla)
2. (foto 2) «Los llevaron a las casas: chapa, madera y uralita.»
3. (foto 3) «Con lo mismo se hicieron las carreteras, los patios y los espacios públicos del pueblo, y la empresa descargaba los relaves a pedido de los vecinos.»
4. (foto 4) «El pueblo entero, la pista, los patios, la escuela: todo estaba hecho con lo que sobraba de la mina.»
5. (foto 5) «Y lo que sobraba de la mina ya tenía nombre en los informes.»
6. (foto 5) «Los informes eran anteriores a la boda, al barco y al avión.»
7. (foto 8) «La respuesta la contó él:»

No se miró la vista en un navegador.

## D — inicio de música por cap: PARADA en la simulación
**Reconstrucción (ADENDA 2).** `lab/hyperframes/f73/d/simular_d.py` llama a `_build_continuous_music_track` con los mismos argumentos que `_mezcla_preview`:
- plans de `_build_plans` (sync_map + manifest + script);
- music_map, `ducked` de `_resolve_music_volumes`;
- `pauses` de `_gfx_pauses`;
- intensidad de `music_intensity.mapa_del_topic`, que es `_mapa_intensidad` sin su `write_text` a `output/audio/<id>/intensity_map.json`;
- prerolls y `seg_dur` de `_segmento_de_cap`, cotejados contra los `seg_dur` de GUION_PANTALLA.json (7/7 iguales);
- intro 2,5 s y `conservar_piezas=True`.

Detalles de la reconstrucción:
- **work_dir:** `lab/hyperframes/f73/d/work/`. De `_fase2b_work` solo se copiaron los dos archivos que esas funciones leen: `gfx_escenas_<cap>.json` y `gfx_pause_<cap>.json`.
- **Medida:** se mide con dos copias de la función que no borran piezas.
- **Validación:** la columna «hoy» reproduce al milésimo lo que dice GUION_PANTALLA.md, así que la pista reconstruida es la del guion.

Tabla de la simulación (desvío del inicio medido contra el title card; ✓ = ±1 cuadro):

| cap | title card s | GUION_PANTALLA (vigente) | hoy (copia de la función, +1e-9) | con el cambio del handoff (float64 + ventana con ≥1 muestra ≠ 0) |
|---|---|---|---|---|
| ch01 | 2,500 | −0,000 ✓ | −0,000 ✓ | −0,000 ✓ |
| ch02 | 69,300 | +0,000 ✓ | +0,000 ✓ | +0,000 ✓ |
| ch03 | 172,133 | +6,900 ✗ | +6,900 ✗ | **+4,600 ✗** |
| ch04 | 344,833 | +0,000 ✓ | +0,000 ✓ | +0,000 ✓ |
| ch05 | 444,533 | +0,000 ✓ | +0,000 ✓ | +0,000 ✓ |
| ch06 | 576,366 | +0,000 ✓ | +0,000 ✓ | +0,000 ✓ |
| ch07 | 704,866 | +15,809 ✗ | +15,809 ✗ | **+13,818 ✗** |

Ningún cap fuera de ch03/ch07 cambia, pero ch03/ch07 no llegan a ≈0, que era el resultado esperado. Por eso no programé el cambio.

**Causa, medida.** Los tramos de la cita no son ceros puros. En la búsqueda de ch03 hay 125 236 muestras en 0, y entre ellas quedan sueltas muestras de ~2,7·10⁻¹⁰.
- **Lag elegido:**
  - ch03, a +4,6 s: una ventana con 10 muestras ≠ 0 entre 44 100.
  - ch07, a +13,8 s: una ventana con 14.
- **Por qué gana esa ventana:** pasa la máscara del handoff, pero su energía por cumsum da exactamente 0,0 en float64. Son 10 cuadrados de ~10⁻²⁰ restados entre dos acumulados de ~15, y la resta los cancela. El puntaje queda en `inf` y gana.
- **El lag real** (desvío 0,000) tiene correlación normalizada 0,9992 en ch03 y 0,9999 en ch07.
- **Precisión no alcanza:** aun con la energía exacta, el ruido de la correlación por FFT dividido por una norma de ~10⁻¹⁰ supera al pico real. No es un problema de precisión que se arregle sin un criterio nuevo.

**Dos salidas.** Ninguna está en el handoff, así que no apliqué ninguna. Decide el analista o Omar:
1. **Máscara estricta, sin número:** solo son candidatas las ventanas sin ninguna muestra en 0 (conteo exacto con cumsum de enteros, == largo de la ventana). Simulada (`d/diag_mascara_estricta.py`; la causa en `d/diag_causa.py`):
   - ch03 y ch07 → 0,000 ✓;
   - ch02/04/05/06 → 0,000 ✓;
   - **ch01 cambia**: −0,000 → +0,027 ✓ (sigue dentro de un cuadro, 0,033 s).

   Por la regla «si cambia otro cap, PARADA», la dejo como dato. Riesgo: una pieza con un cero digital dentro de su ventana real quedaría sin candidato y daría «no se pudo medir».
2. **Un piso de energía derivado de la precisión de la FFT** (eps de float64 × normas). Es una constante nueva, y la ADENDA 4 la prohíbe sin decisión.

D.2 (tabla de la función real después del cambio) y D.3 (test) no corrieron porque no hubo cambio.
- **Archivos de D:** `d/simulacion.log` y `d/tabla_sim.json`.
- **No entran al commit:** la pista y las piezas reconstruidas en `d/work/` (271 MB, wav).

**Cierre de `_fase2b_work/`:** la lista de md5 final da `321f4c53b4bd8fb1dcfbe8b4e84d8c00`, igual a la de la etapa 0 (348 archivos). `cmp` de las dos listas da iguales. GUION_PANTALLA.md sigue en 433eb3e5….

## Tests y mapa
- **`test_module_f73.py`**, sin red: **21 passed**.
  - A (5): argumentos de la regla única, sin guion no hay madres, data URIs, el paquete guarda persona y madres, un solo camino.
  - B (6): sin sello se archiva todo, sello de otra narración, sello vigente no se toca, sin aprobar no genera, `run_candidates` archiva + sella + arranca en 1, serve y run_pipeline archivan.
  - C (10), del subagente.
- **Mapa:** stickers de `run_pipeline.py`, `m09_packaging.py` y `m09_review_server.py` al día (texto + md5). Los de `qa_studio_server.py` y `qa_studio.html` los puso al día el subagente. `mapa_modulos.py --check` da 0 fallas.
- **Suite amplia (como F71b):** 139 archivos (`test_module_f[0-9]*`, `gfx_*` sin gfx_lab, `01a*`, `01b*`, `m03_*`, concat_windowed, transition_timeout, test_constantes_con_origen, 135_thumbs, qa_form_cost; sin f58 ni only_cap), `-n auto`. Resultado: **3 failed, 1414 passed, 29 skipped, 2 xfailed**, en 67 s (`lab/hyperframes/f73/suite.log`). Las 3 son las heredadas de F71b/F72b: `f51c[1-start-paredes de chapa.]`, `m03_merge_timing::test_c_guarda_de_minimo` y `::test_c_veo_path_y_veo_anchor_intacto`. Ninguna es nueva.

## Archivos
- **Producción:**
  - `script_engine/m09_packaging.py`, `script_engine/m09_review_server.py` y `run_pipeline.py` (A, B);
  - `qa_studio_server.py` y `qa_studio.html` (C);
  - `lab/mapa/stickers/orquestador.json`.
- **Tests:** `test_module_f73.py`.
- **Lab:**
  - `lab/hyperframes/f73/a/` (script de la corrida, log, costo, miniaturas);
  - `b/` (metadata antes, md5 de publish antes);
  - `d/` (simulador, log, tabla, md5 de `_fase2b_work`).
- **Salidas en output** (no van al commit): `output/<tid>/publish/` con 3 paquetes nuevos y `_desfasado_20261104_073537/`.
- **No tocados:** prompts (`pedir_paquetes`, fotos), fondos, GUION_PANTALLA, render, `fase2b.py`, main, `_fase2b_work_desfasado_*`.

## Para Omar
- Las 3 miniaturas nuevas, en la hoja `a/miniaturas_nuevas_arriba_viejas_abajo.jpg` o en el form de miniaturas.
- Decidir D: la máscara estricta (mueve ch01 +0,027 s, dentro de un cuadro) o un piso derivado de eps.

## Veredicto del revisor-handoff
VEREDICTO: CUMPLE CON OBSERVACIONES

Para D, lo que se verificó es la parada y su causa, no la entrega: D no está hecho. Ese hueco ya estaba declarado en el reporte y es la observación 1.

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 0 | Etapa 0 solo lectura (md5 de los handoffs, HEAD, GUION_PANTALLA) | OK | Los md5 de HANDOFF_F73 (4f00a1fe…) y de la ADENDA (2a6b2b07…) coinciden. HEAD es 58915cc. GUION_PANTALLA.md da 433eb3e5…. |
| 0b | `_fase2b_work/` igual al final | OK | Recalculé la lista de md5 sobre el árbol vivo (348 archivos) y es idéntica a `d/fase2b_work_md5_final.txt`. Ese archivo es igual al de la etapa 0 (`cmp`). |
| A1 | Madres con la regla única `_madres_para_item`, pasadas como `foto_madre_data_uris` | OK | `m09_packaging.py`: `madres_del_paquete` y `foto_paquete(..., madres)`. Sin madres va `None`, el t2i de siempre. |
| A2 | `foto_madre_refs` en el paquete y `referencias_md5` lleno | OK | `metadata.json` trae `foto_madre_refs` = Daniel Écija en los 3 paquetes. `paquete_01_base.llamada.json` tiene endpoint `/edit` y `referencias_md5` = ae577008…. |
| A3 | Se borra la llamada sin madres (un solo camino); `rehacer_foto` pasa por lo mismo | OK | El diff elimina la firma vieja. El test de un solo camino pasa. |
| B1 | `narracion_md5` en `metadata.json`; sin narración aprobada no genera | OK | `metadata.json` tiene `cd0fe3bf…`. `run_candidates` lanza `PaquetesParada` sin narración aprobada. |
| B2 | Sin sello o sello distinto: archivar a `_desfasado_<ts>/` en `run_candidates`, `serve` y el paso `packaging` | OK | `archivar_paquetes_desfasados` está llamada desde `m09_review_server.py` y `run_pipeline.py`. Existe `publish/_desfasado_20261104_073537/`. |
| B3 | Prueba real en Wittenoom: se archivan 3 y salen 3 nuevos | OK | Hay 3 paquetes nuevos con sus `.png` y `.llamada.json` en `thumb_candidates/`. |
| C1 | `voz` por segmento, ancla a ancla, con respaldo al ancla | OK | `voz_por_anclas` y `_poner_voz` en `qa_studio_server.py`. El texto sale del guion vivo. |
| C2 | `qa_studio.html` muestra el resto de `voz` en gris, sin tocar tiempos | OK | `.voz-resto` (línea 223) y `vozResto` se usan en la tarjeta (619) y en el panel (682). |
| C3 | Cobertura 100 % en los 7 caps | NO VERIFICABLE por mí | La tabla está en el reporte y el script es `c_cobertura.py`. No lo corrí. Hay 10 tests de C que pasan. El reporte admite que no se miró la vista en un navegador. |
| D1 | Simulación sobre piezas reconstruidas en `d/`; PARADA si cambia otro cap | OK | `simulacion.log` y `tabla_sim.json` existen. La columna «hoy» da ch03 +6,9 y ch07 +15,809, igual que el guion vigente. Con el cambio, ch03 +4,6 y ch07 +13,818: no llegan a ≈0 y ningún otro cap cambia. |
| D2 | Tabla de la función real y test de D | NO HECHO, por PARADA | `fase2b.py` sin diff. Falta D.2 y D.3, y la causa de que falten es legítima. |
| E | Tests nuevos sin red en `test_module_f73.py` | OK | Corrí `test_module_f73.py`: 21 passed. |
| F | Suite amplia como en F71b | OK | `suite.log`: 3 failed, 1414 passed. Las 3 fallas son las heredadas (`f51c`, `m03_merge_timing` ×2). No la re-corrí. |
| G | Prohibiciones: prompts, `fase2b.py`, fondos, GUION_PANTALLA, main, render | OK | `git diff` sobre `fase2b.py` está vacío. `pedir_paquetes` no aparece en el diff. GUION_PANTALLA mantiene su md5. |
| H | Costo al final; reporte, ESTADO_SESION y commit | PARCIAL | Costo US$ 0,4468 en el reporte. ESTADO_SESION tiene la entrada F73. El commit aún no existe, lo cual es lo esperado. |

Fuera de alcance: ninguno de producción. Los cambios están solo en `m09_packaging.py`, `m09_review_server.py`, `run_pipeline.py`, `qa_studio_server.py`, `qa_studio.html` y `lab/mapa/stickers/orquestador.json`, más `test_module_f73.py` y `lab/hyperframes/f73/`. Quedan fuera de la tanda (ajenos): `diag_234_cap4.py`, `f28a.log` y `pedido_paquetes_wittenoom.txt`, más `lab/hyperframes/f72/REVISION_GUION.md`, que aparece sin trackear. `d/work/` (271 MB de wav) no debe entrar al commit.

Observaciones:
1. D quedó incompleto, con el motivo justificado. La regla del handoff no lleva ch03/ch07 a ≈0, y la ADENDA prohíbe constantes nuevas. Hay que decidir entre una de estas dos salidas:
   - La máscara estricta, que sin número deja ch03/ch07 en 0 pero mueve ch01 +0,027 s, dentro de un cuadro. Es un dato de simulación: no la verifiqué.
   - Un piso de eps, que es una constante nueva y la ADENDA la prohíbe.
2. La foto 2 (los relaves) lleva a Daniel porque los casilleros lo pusieron en `persona`. Es la regla única tal cual, pero es una decisión visual para Omar.
3. El costo de las 3 fotos (3 × 0,042) es una estimación del registro F68, no un gasto medido. Falta ver las miniaturas compuestas, algo que Omar debe hacer.
4. El mensaje de `archivar_paquetes_desfasados` imprime con emoji. El código ya lo hacía así en otros puntos, así que es menor.

Riesgos que el contrato no cubre:
- `candidates_ready` ahora exige el sello y llama a `narracion_vigente`, que lee archivos de la narración. Cualquier topic con paquetes viejos sin sello se archiva sin avisar, también al abrir el form.
- Dos de las tres fallas heredadas de la suite siguen sin dueño.
- La máscara estricta de D podría dar «no se pudo medir» en una pieza con un cero digital real dentro de su ventana.

### Adenda de CC
- **Obs. 1 (D):** de acuerdo, D queda para decisión. Yo propongo la máscara estricta, porque no agrega ningún número. Antes de programarla haría falta aceptar que ch01 se mueve +0,027 s (sigue en ✓). Si se elige, D.2 y D.3 se corren en una tanda chica, con la misma reconstrucción de `d/`.
- **Obs. 2:** queda para Omar en la hoja de miniaturas. No se tocó ningún prompt.
- **Obs. 3:** el 0,042 es el valor registrado en DECISIONES (F68), porque fal no devuelve el costo. Las miniaturas quedan para que Omar las mire.
- **Riesgo «se archiva sin avisar»:** no es así. `archivar_paquetes_desfasados` siempre imprime la carpeta, y `serve` agrega un aviso «⚠». Además, archivar es mover, no borrar: lo archivado se puede recuperar desde `_desfasado_*`.
- **`d/work/` y `REVISION_GUION.md`:** `d/work/` no entra al commit. `REVISION_GUION.md` es ajeno y no lo toqué.
