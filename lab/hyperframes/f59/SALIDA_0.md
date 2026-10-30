# F59 — Salida 0 (solo lectura y docs, US$ 0) · PARADA 0

Handoff `lab/hyperframes/f59/HANDOFF_F59_qa_studio_produccion.md` (md5 `9325c5ee7e284e8012aedcf8d1284f07`, verificado). Rama `f11-guion-v4`. Topic Wittenoom `123bbb64-9fca-4395-8bf4-57d60e219ef1`. Dos subagentes en paralelo (punto 2 y punto 3); nada de producción se tocó (`data/`, `output/`, `script_engine/`, `qa_studio_server.py` intactos; sin pytest, sin LLM, sin fotos).

## 1. DECISIONES
Las 6 líneas del handoff (08:18, 08:22 ×4 y la del analista «dentro de 08:22») están tal cual al final de `DECISIONES.md` (commit `e5b1dbf`).

## 2. Cuadros vacíos de la galería — causa confirmada

Medido con `QAState(tid)` real sobre `output/<tid>/assets`, el guion vivo `data/scripts/<tid>.json` y `_steps/<tid>/03_visual.json`. «cuadros» = `len(_flux_imgs)` (caps flux) o `len(_supp_imgs)` (caps con clip) = lo que `/caps` cuenta y `/cap` dibuja; «vacíos» = segmentos cuyo `img_name` da `None` en `resolve_image`.

| cap | clip | cuadros dibujados | PNG crudos img | crudos supp | `*_graded.png` | guion vivo ip / sip | 03_visual ip / sip | vacíos | orden que sale |
|---|---|---|---|---|---|---|---|---|---|
| ch01 | sí | 8 (supp) | 0 | 4 | 4 | 0 / 4 | 0 / 4 | **4 / 8** | supp_01..04_graded (idx 0) y después supp_01..04 (1..4) |
| ch02 | no | 32 | 16 | 0 | 16 | 16 / 0 | 16 / 0 | **16 / 32** | img_01..16_graded (todos 0) y después img_01..16 (1..16) |
| ch03 | no | 32 | 16 | 0 | 16 | 16 / 0 | 16 / 0 | **16 / 32** | ídem |
| ch04 | no | 28 | 14 | 0 | 14 | 14 / 0 | 14 / 0 | **14 / 28** | ídem |
| ch05 | no | 32 | 16 | 0 | 16 | 16 / 0 | 16 / 0 | **16 / 32** | ídem |
| ch06 | no | 32 | 16 | 0 | 16 | 16 / 0 | 16 / 0 | **16 / 32** | ídem |
| ch07 | sí | 24 (supp) | 0 | 12 | 12 | 0 / 12 | 0 / 12 | **12 / 24** | supp_01..12_graded (0) y después supp_01..12 |

**Se confirma la causa del analista**, camino real hasta el cuadro:
- `QAState._flux_imgs` (`qa_studio_server.py:185-189`) y `_supp_imgs` (`:191-195`): `glob("chNN_img_*.png")` / `glob("chNN_supp_*.png")` matchean también `chNN_img_NN_graded.png` (los escribe `script_engine/image_grade.py`, `SUFFIX = "_graded"` l. 31, salida `<stem>_graded.png` al lado del original, l. 65).
- `_img_idx` (`:181-183`, regex `_(\d+)\.png$`) no matchea `_graded.png` → 0; `sorted` es estable → **los graded van primero**.
- `_cap_flux` (`:312-353`) / `_cap_veo` (`:366-431`) / `_cap_veo_timeline` (`:433-500`) emiten un segmento por Path vía `_seg` (`:356-365`) con `img_name = p.name` y `url = /img?cap=…&name=…_graded.png`; el front (`qa_studio.html:493-499`, `imgSrc` `:317-318`) pide esa URL tal cual.
- `/img` (`:1834-1836`) → `resolve_image` (`:215-232`) rechaza el nombre en `:218` por `_IMG_NAME_RE` (`:76`, `^ch\d{2}_(img|supp)_\d+\.png$`) → `None` → `_send_file` (`:1760-1762`) responde 404 `{"error":"no encontrado"}` → `<img>` roto = cuadro vacío. **La mitad exacta de los cuadros de cada cap.**

Tres efectos más que el analista no listó (misma causa):
1. **Orden:** los vacíos ocupan las posiciones 1..16 y las fotos reales vienen después.
2. **Anclas corridas:** `_seg` (`:360`) asigna `anchors[i]` por posición en la lista mezclada → los 16 graded (vacíos) se llevan los 16 anchors; las 16 fotos visibles quedan con `anchor` vacío/`None` (medido en ch02: seg 17 = `ch02_img_01.png` con anchor `''`).
3. **Sync perdido en los 7 caps:** `_cap_flux` solo usa `compute_anchor_starts` si `len(anchors) == n` (`:321`); con n = 32 y 16 anchors cae al reparto uniforme → `sync_approx: True` en ch01..ch07 (medido); lo mismo en `_cap_veo` (`:388`) y `_cap_veo_timeline` (`:453`).

Los `*_graded.png` sí son esperados en `m09_packaging.py:575-584` y `m09_review_server.py` (bases de miniatura). **No se arregla en F59** (va como chascada propuesta al reporte): una línea de arreglo sería filtrar `_flux_imgs`/`_supp_imgs` con `_IMG_NAME_RE`.

## 3. Copia de lab de Wittenoom — `lab/hyperframes/f59/base/`

Script `lab/hyperframes/f59/copia_lab.py` (idempotente: borra `base/` y la rehace; corrido 2 veces, rc 0). Qué hace:
1. md5 del guion vivo y de `03_visual.json`, `01a_skeleton.json`, `01b_narration.json` de producción antes de todo; al final `assert` de que no cambiaron.
2. `m06_assembler.assemble_final_script(tid)` **sin LLM** con `m6.SCRIPTS_DIR` apuntado a `base/data/scripts` (restaurado en `finally`; `STEPS_DIR` y `TOPICS_DB` quedan en producción, solo lectura); `assert` de que el path devuelto es el de la copia.
3. En la copia: `narration` de cada cap = la del **guion vivo** (no la de `01b_narration.json` del 29/30-oct); en los caps con clip (1 y 7) `voz_clip = m3.voz_del_clip(narr, veo_position, ventana)` con `veo_position` del cap en `03_visual.json` y la ventana como `f57/clip_b.py` l. 62-64 (`dur = palabras / PALABRAS_POR_SEG`; `ventana = max(1, min(int(VEO_CLIP_DURATION_SEC · len/dur), len − 1))`). Ninguna clave fuera del contrato (`voz_clip` ya la propaga m06 desde 03_visual, l. 109).
4. **Agregado de CC:** copia `03_visual.json` (con el mismo `voz_clip` en caps 1 y 7) y `01a_skeleton.json` a `base/data/scripts/_steps/<tid>/`: QAState lee el skeleton para los roles (`_load_skeleton_roles`, l. 144) y la Etapa A guardará en el 03_visual de la copia. El de producción no se toca (en producción ningún cap tiene `voz_clip`; md5 sin cambio).
5. `copytree` de `output/<tid>/assets` (196 archivos, 615,4 MB) y de `output/audio/<tid>` (31 archivos, 13,2 MB, < 100 MB: se copió; QAState lee ahí los timestamps).

**Narración: `01b_narration.json` (29-oct 20:55, con el gancho F56) vs guion vivo (28-oct 00:13)** — difieren en los 7 caps; la copia lleva la del vivo:

| cap | chars 01b | chars vivo | md5 01b | md5 vivo |
|---|---|---|---|---|
| 1 | 834 | 453 | ec9d4d5f | 8765aaf4 |
| 2 | 1188 | 1664 | 8fe5ecd3 | 0de61909 |
| 3 | 3056 | 2105 | 34fa2417 | 9e404f1e |
| 4 | 1259 | 1343 | ef464253 | 1309d196 |
| 5 | 1682 | 1961 | 4ef159fd | 22310727 |
| 6 | 1712 | 2186 | 407dc929 | 3c7af1b0 |
| 7 | 1266 | 1233 | 7ea3bf10 | 7933696e |

Comprobación de CC: las anclas de `03_visual.json` (5 + 16 + 16 + 14 + 16 + 16 + 13) están **todas** en la narración del guion vivo (96/96 normalizando espacios; 95/96 literal: ch03 ítem 16 lleva un espacio donde la narración tiene «\n\n» antes de «dijo McNulty») y casi ninguna en el 01b del 29-oct (3/96): el 03_visual del 29-oct 13:00 (F51d-A/F51f) se armó sobre la narración del 28. La copia es coherente (anclas ↔ narración).

**`voz_clip`** (sobre la narración del guion vivo):

| cap | veo_position | palabras | chars | ventana (chars) | palabras voz_clip | voz_clip |
|---|---|---|---|---|---|---|
| 1 | start | 86 | 453 | 101 | 20 | «Un hombre joven posa para una foto con el pie envuelto en una venda blanca. Detrás, tierra roja y paredes» |
| 7 | end | 207 | 1233 | 114 | 21 | «seguridad pública». No se ha retirado una sola palada de asbesto. ¿Quién va a sacar la primera palada de esa tierra?» |

(En el cap 7 arranca en `seguridad pública».` porque `voz_del_clip` toma las palabras que terminan dentro de la ventana, texto tal cual.)

**Árbol** (archivos · MB por directorio):
```
base/
  data/scripts/                 1 · 1,0   (<tid>.json)
    _steps/<tid>/               2 · 0,4   (03_visual.json, 01a_skeleton.json)
  output/<tid>/assets/          4 · 0,2   (assets_manifest, depth_metrics, flow_specs, zoom_verdicts)
    ch01_flux 8 · 26,0 | ch01_veo 2 · 10,6 | ch02_flux 32 · 98,6 | ch03_flux 32 · 97,3 | ch04_flux 28 · 85,3
    ch05_flux 32 · 95,1 | ch06_flux 32 · 95,7 | ch07_flux 24 · 77,6 | ch07_veo 2 · 29,1
  output/audio/<tid>/          31 · 13,2
TOTAL 230 archivos · 629,9 MB
```
`QAState(tid, base_dir=base)`: 7 caps (ch01 veo/start, 4 supp, role hook; ch02–06 flux 16/16/14/16/16 anclas; ch07 veo/end, 12 supp); `_flux_imgs("ch02")` = 32 (con los graded, como en producción); `resolve_clip("ch01")` = `ch01_veo/ch01_clip_01.mp4`; `_load_words("ch01")` = 86.

md5: guion vivo `f762dc482027e9a65ccd7fa38316510e` antes y después (intacto); copia `26549ade…` (cambia entre corridas solo por `created_at`, m06 l. 140). `base/` queda **ignorada entera por git** (reglas `data/` y `output/` del `.gitignore`, l. 11-12; `git check-ignore` lo confirma); lo único nuevo en git es `copia_lab.py`.

## 4. Ítems candidatos para B2 («rehacer foto», ítem `medium` con persona visible)

**Hallazgo que hay que tener presente:** los PNG de `output/<tid>/assets/chNN_flux/` (28-oct 00:20–00:34, `assets_manifest.json` 00:34) salieron de los prompts del **guion vivo del 28**; `03_visual.json` es del **29-oct 13:00** (m03 de F51d-A, con casilleros nuevos) y sus fotos nunca se generaron: en ch03 el manifest coincide 16/16 con el guion vivo y 0/16 con 03_visual. Los ítems del guion vivo no tienen `people_group` ni `anio`. Por eso B2 pide primero la foto «antes» desde los casilleros de 03_visual con la misma semilla: así el antes/después compara el mismo guion. Índices 1-based por posición en `image_prompts` (`chNN_img_{i:02d}.png`, confirmado por el manifest).

Candidatos de `03_visual.json` (caps 2–6, `shot_scale == "medium"`, `people_group` no vacío; todos con `foto_madre_ref: []`, crudo y graded en disco):

| # | cap / idx / archivo | subject (03_visual) | people_group | anio | beat | PNG real en disco (graded, visto) |
|---|---|---|---|---|---|---|
| 1 | ch03 / 8 / `ch03_img_08.png` | The employer's advocate, a middle-aged Anglo-Australian man, heavy build, in a dark double-breasted suit | company_owners_and_managers, unions_and_labour_arbitration | 1949 | 4 | **persona grande, cara de perfil muy visible**; el vivo idx 8 («company lawyer, heavy-set Australian man») cuenta lo mismo |
| 2 | ch03 / 6 / `ch03_img_06.png` | The young Anglo-Australian flying doctor, slim, in shirtsleeves and loosened tie, seated alone on a timber bench | government_mines_and_health_officials | 1949 | 4 | persona grande, cara frontal; el vivo es «middle-aged doctor in a crumpled suit (Eric Saint)» de pie, con rasgos que no cuadran con el subject |
| 3 | ch02 / 4 / `ch02_img_04.png` | A young Spanish wife, mid-twenties, slight build, olive skin, dark set hair, in a modest cotton dress, pressed against her lean dark-haired husband in shirtsleeves | spanish_migrant_families | 1962 | 2 | pareja abrazada en cubierta, cara de ella de perfil (el vivo idx 4 es otro prompt) |
| 4 | ch02 / 10 / `ch02_img_10.png` | A Spanish boy around eight, pale and drawn, in a rumpled shirt, beside his young olive-skinned mother in a cotton dress | spanish_migrant_families | 1962 | 3 | no visto |
| 5 | ch04 / 11 / `ch04_img_11.png` | a young Spanish migrant mother, about 25, slender and weakened, dark hair damp with sweat, and an Anglo-Australian nurse in white holding a very large swaddled baby | spanish_migrant_families | 1963 | 7 | no visto |
| — | ch06 / 14 / `ch06_img_14.png` | A middle-aged Anglo-Australian committee chairman, stocky, short greying hair, early-1990s dark suit | australian_politicians | 1994 | 12 | **sin persona** en disco (agua de río con fibras): no sirve |

Otros `medium` + `people_group` (de espaldas o cara oculta): ch03/10, ch04/2, ch04/13, ch05/10, ch05/14, ch06/4, ch06/5.

**Recomendación de CC para B2:** `ch03_img_08` (persona grande, cara visible, sin foto madre; único donde 03_visual y el PNG en disco cuentan lo mismo). Alternativa `ch03_img_06`. Pedido ajustado a quien está en la foto: «que mire hacia la cámara, con el ceño fruncido» sirve tal cual para el abogado del 08.

## 5. Lo que no cuadra o queda para el analista
1. **Guion vivo (28-oct) ≠ `01b_narration.json` (29-oct, gancho F56) ≠ fotos en disco (28-oct) ≠ `03_visual.json` (29-oct, casilleros nuevos sin fotos).** La copia de lab sigue el handoff (03_visual + narración del vivo) y es coherente en anclas; pero QA Studio sobre la copia muestra los PNG del 28 bajo los ítems del 29. B2 lo salva con la foto «antes» regenerada; se informa.
2. El guion vivo tiene claves que fase2 agregó después del ensamble (pesa 1 079 664 bytes; la copia 1 019 230): la copia es la de m06 «limpia» + narración del vivo + `voz_clip`.
3. Chascada propuesta (no F59): filtrar los `_graded.png` en `_flux_imgs`/`_supp_imgs`; con eso vuelven el orden, las anclas y el sync (efectos 1–3 del §2).
4. Nada de la Etapa 0 pidió gastar: US$ 0.

## Veredicto de revisor-handoff — Etapa 0 (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | 6 líneas en DECISIONES = handoff (l. 19-24) | OK | El blob de e5b1dbf tiene las 6 líneas sin CR y su md5 es igual al de las l. 19-24 del handoff (c090493f…). El archivo de trabajo tiene CRLF, que es autocrlf y no está en el commit. Handoff md5 9325c5ee… verificado. |
| 2 | Tabla §2 contra disco | OK | Medido en assets/chNN_flux: crudos/graded = 4/4, 16/16, 16/16, 14/14, 16/16, 16/16, 12/12 (ch01..ch07). Los totales 8/32/32/28/32/32/24 coinciden con la tabla. |
| 2b | Líneas citadas de qa_studio_server.py y qa_studio.html | OK | Verificadas una por una: _IMG_NAME_RE en l. 76; _img_idx en 181-183; _flux_imgs y _supp_imgs en 185-195; resolve_image en 215-232 (rechazo por regex en 218); `len(anchors)==n` en 321; _seg en 356-365 (anchors[i] en 360); /img en 1834-1836; _send_file 404 en 1760-1762; imgSrc en html 317-318; el grid en html 493-499. m09_packaging 575-584 usa los graded y image_grade.py:31 define SUFFIX="_graded". |
| 3 | copia_lab.py no escribe en data/, output/ ni script_engine/ | OK | Solo lee de producción. Todas las escrituras van a BASE (rmtree, dump, copyfile, copytree con destino BASE). m6.SCRIPTS_DIR se redirige y se restaura en `finally` (l. 99-110). Hay asserts de md5 del vivo y de los _steps (l. 109, 207-210). |
| 3b | m06 sin LLM, narración del vivo, voz_clip como f57/clip_b.py l. 62-64 | OK | La fórmula de ventana (l. 78-83) es idéntica a clip_b.py:62-64. Usa m3.voz_del_clip y la narración del vivo (l. 127). No importa ningún módulo LLM. |
| 3c | base/data/scripts/<tid>.json | OK | voz_clip presente solo en caps 1 (105 chars) y 7 (116 chars). Los 7 caps tienen la misma narración que el vivo (comparado en Python). check-ignore confirma que base/ está ignorada. |
| 3d | Guion vivo md5 f762dc48… | OK | md5sum de data/scripts/123bbb64….json = f762dc482027e9a65ccd7fa38316510e. |
| 4 | Anclas 96/96 en el vivo, 3/96 en 01b | PARCIAL | Los totales por cap (5+16+16+14+16+16+13 = 96) y 3/96 en 01b son exactos. En el vivo, literalmente, son 95/96. La excepción es ch03 image_prompts[15]: el ancla lleva un espacio antes de «dijo McNulty» y la narración lleva "\n\n". Es un desajuste de espacios y no de contenido, pero «96/96» no es literal. |
| 5 | Sin código de producción tocado | OK | `git show --stat`: e5b1dbf toca DECISIONES.md y el handoff. e612b70 toca ESTADO_SESION.md, SALIDA_0.md y copia_lab.py. No hay nada en script_engine/, qa_studio* ni data/. |
| 5b | Sin gasto | OK | El último timestamp de data/cost_history.json es 2026-10-30T04:41:38 (el Seedream de f58 parte B, total 0,3953). No hay entradas posteriores. cost_history.json no está modificado en git status. |
| 6 | Salida en texto y ESTADO al día | OK | SALIDA_0.md incluye tabla, causa, árbol y candidatos B2. ESTADO_SESION.md l. 3 (fecha y hito) y el bloque «Para Omar (F59, PARADA 0)» en l. 17-24 están actualizados. |
| 7 | B2: ch03_img_08 es medium con people_group no vacío | OK | 03_visual.json, cap 3, image_prompts[7]: shot_scale "medium", people_group [company_owners_and_managers, unions_and_labour_arbitration], subject «The employer's advocate…». El manifest tiene ch03_img_08 y su graded. |
| 8 | Reglas fijas (no tocar prompts, sin números nuevos) | OK | Ningún prompt de producción cambió. Los números de la Etapa 0 son mediciones. |

Fuera de alcance: ninguno. Los demás archivos sin trackear y los dos modificados (diag_234_cap4.py, f28a.log) ya estaban en el status inicial y no son de esta tanda.

Observaciones:
- «96/96» debe leerse como 95/96 literal y 96/96 normalizando espacios (fila 4).
- No verifiqué por separado las afirmaciones de SALIDA_0 sobre las fotos en disco: el hallazgo de que los PNG del 28-oct no coinciden con 03_visual, el «visto» de las imágenes y el conteo 0/16 en el manifest de ch03. Sí encontré ch03_img_08 y su graded en el manifest.
- Los pesos de 629,9 MB y los 230 archivos no se re-midieron.

Riesgos que el contrato no cubre:
- Sobre la copia de lab, QA Studio mostrará los PNG del 28-oct bajo los ítems de 03_visual del 29-oct. La Etapa B2 solo es coherente si primero regenera la foto «antes», lo que implica gasto.
- La copia de m06 pesa 1,02 MB frente a 1,08 MB del vivo: le faltan claves que agregó fase2.

### Adenda de CC
- **Fila 4:** corregido en §3: 96/96 normalizando espacios, 95/96 literal (el ítem 16 de ch03 tiene un espacio donde la narración trae un salto de párrafo; `norm` de mi comprobación colapsaba espacios).
- **Observación 2:** el conteo 0/16 del manifest de ch03 contra 03_visual y el «visto» de las imágenes son del subagente de la Etapa 0 (vio los graded con la herramienta de imagen); las fechas de archivo (PNG 28-oct 00:20–00:34, 03_visual 29-oct 13:00) las comprobé yo con `ls`.
- **Riesgo 1:** es lo que pide B2 (foto «antes» desde los casilleros con la misma semilla, ≈ US$ 0,035), ya previsto en el handoff.
- **Riesgo 2:** §5.2 lo declara; QAState solo lee `chapters` (anclas, narración, render_engine), que la copia tiene entero.
