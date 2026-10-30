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

Comprobación de CC: las anclas de `03_visual.json` (5 + 16 + 16 + 14 + 16 + 16 + 13) están **todas** en la narración del guion vivo (96/96) y casi ninguna en el 01b del 29-oct (3/96): el 03_visual del 29-oct 13:00 (F51d-A/F51f) se armó sobre la narración del 28. La copia es coherente (anclas ↔ narración).

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
