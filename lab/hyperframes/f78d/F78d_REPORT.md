# F78d — identidad de las personas en producción + Etapa C de F78a en Colza

Handoff `lab/hyperframes/f78d/HANDOFF_F78d_identidad_produccion.md`. El md5 del pedido era 27827aa6…; con la ADENDA 1 (09:15, respuesta a la PARADA de CC) es `cbed0677e2a6ee94148e34dc0b520555`. Rama `f11-guion-v4`, base `af72da1`. Topic Colza `c4934b7d-3f54-448f-ba5f-539dc744f0d8`.

- **Commit A:** `7078adb` (código, tests y lista sin llamar).
- **Commit B+C:** el que lleva este reporte (lab, hoja y ESTADO).
- **Costo total:** US$ 7,5482 (B 3,2859 + C 4,2623).
- **PARADA:** Omar revisa las fotos en QA Studio. No hay render ni nada subido.

## PARADA previa (resuelta por la adenda 1)
El editor de foto F59 de QA Studio no deja ninguna marca en el ítem: `_fix_core` escribe las mismas claves que m03. La adenda 1 resolvió tres cosas:
1. «Tocada en QA» significa que existe la copia `output/<tid>/assets/_qa_backups/<foto>.png.<ts>.bak.png`.
2. El refill vuelve a pasar la indicación previa de m03.
3. Si se rehace la foto de arranque de un clip, también se regenera su movimiento.

## Etapa A — código (`7078adb`)

**`script_engine/m03_visual.py`**
- **l.166 (`DOCTRINE_PEOPLE`)**, antes y después en `a/l166.md`:
  - ANTES: `…taken from demographics (and from a documented person's appearance_canon when it is one), matching what the beat narrates.…`
  - DESPUÉS: `…taken from demographics (and from a documented person's appearance (or appearance_canon if there is none) when it is one), matching what the beat narrates.…`
  - Es la única edición de prompt.
- **`_f8_refill(..., personas_fijas=None)`:**
  - Si viene `personas_fijas`, la llamada recibe una copia del topic con `documented_people` filtrado a esas personas.
  - Los rasgos se leen del topic entero, porque el md5 de la entrada usa todas las personas.
  - Al volver, se compara el casillero `persona` nuevo con `personas_fijas` como conjunto, sin importar el orden. Si no coincide, queda el ítem viejo con `_rasgos_refill: "persona_distinta"` y no hay reintento.
  - Con `note=""` ya no deja `_f8_rehecha` vacío.
- **`aspecto_fuente`:**
  - `_render_prompts_seedream` lee los rasgos una sola vez por llamada (o los recibe en `_f8["rasgos"]`) y se los pasa al bloque (`_format_seedream_canon_block(..., rasgos)`).
  - `_marcar_aspecto` marca «rasgos» si había rasgos vigentes para TODAS las `persona` del ítem; si no, «canon». Un ítem sin persona no lleva la clave.
  - `aspecto_fuente` y `_rasgos_refill` se sumaron a `CLAVES_F8_PAPEL`, así que viajan a las supps y a `image_f8`.
- **`rehacer_aspecto_personas(topic, skeleton, narration, video_id)`**, con la lista `fotos_aspecto`, que no llama a nada:
  - Toma cada foto con persona y la clasifica:
    - `qa`: tiene copia en `_qa_backups` (adenda 1.1);
    - `persona_distinta`: ya volvió con otra persona antes;
    - `ya_rasgos`;
    - `sin_rasgos`: alguna persona sin rasgos vigentes;
    - `rehacer`.
  - Para las «rehacer» llama a `_f8_refill(note=<_f8_rehecha previo o "">, personas_fijas=persona)` en paralelo (`CAP_MAX_WORKERS`).
  - Si la foto rehecha es la de arranque de un clip, actualiza `image_prompt` e `image_f8`, `image_sensible` y `subject_ref` (con la misma expresión de `_render_prompts_seedream_veo`). El `video_prompt` se regenera con `_seedream_video_prompt` (adenda 1.3).
  - Escribe el 03_visual una sola vez. Si no hay nada que rehacer, no llama ni escribe.
  - Un `CasillerosParada` en una foto deja la vieja y la lista en `errores`.
- **Refactor sin cambio de conducta:** `_con_f8` (el `_f8` que armaba `assign_visual_prompts`) y `_supp_de` (la forma de las supps) salen como funciones para no duplicar código.

**`fase1_5.py`**
- Paso `aspecto` después de paso0 (foto madre) y antes de assemble.
- `aspecto` entra en `VALID_FROM_STEPS` y en `_PIPELINE_ORDER`. `--only aspecto` corre el paso y el ensamblado y corta.
- El costo queda en `01_v3_costos.json` como paso «aspecto».

**Tests**
- `test_module_f78d.py`, 13 tests sin red. Cubren:
  - l.166;
  - el filtro de personas;
  - sin `personas_fijas` es lo de siempre;
  - persona distinta → queda lo viejo, sin reintento;
  - `aspecto_fuente` y que el bloque no lee el disco si recibe los rasgos;
  - la lista sin llamar;
  - la nota previa, el movimiento del clip y la forma de las supps;
  - la idempotencia (misma md5 y 0 llamadas la segunda vez), persona distinta sin reintento y el salto de QA;
  - sin rasgos vigentes no llama;
  - `--only aspecto` en orden.
- Test viejo actualizado: `test_module_f50d.py` l.141. Su falso `_format_seedream_canon_block` recibe también `rasgos`.

**Suite y mapa**
- Suite amplia (`lab/hyperframes/f78d/a/suite.log`, `-n auto`): **1586 passed, 3 failed**. Son las 3 heredadas (ver Chascada). La lista de la suite suma `test_module_f78d.py`.
- Mapa: los stickers de `m03_visual.py` (fase2a) y `fase1_5.py` (guion) se reescribieron con su md5; `mapa --check` da 0.

**Colza sin llamar** (`a/lista_aspecto.md`):
- 41 fotos con persona: **38 a rehacer** y 3 `sin_rasgos`. Las 3 son personas con una sola foto, sin madre: Jaime Vaquero (ch02_img_08), Bengoechea (ch07_supp_03) y Manuel Hernández (ch07_supp_04).
- **0 tocadas en QA:** no existe `_qa_backups`.
- **Las 3 con nota previa** (adenda 1.2), las tres con el mismo texto: «do NOT show the motif «pasillo» (already used twice in this video). Motifs already used twice in this video (avoid them all): pasillo. Show another part of the beat's sensory image.»
  - ch05_img_01 (Jesús Lozano)
  - ch05_img_03 (Jesús Lozano)
  - ch05_img_12 (Angela Menseger)

## Etapa B — Colza: textos (`fase1_5.py --topic <tid> --only aspecto`, venv; `b/etapa_b.py`, log `b/fase1_5.log`)

**Resultado**
- **32 rehechas, 6 `persona_distinta`, 0 errores, 0 saltadas por QA.** Después de escribir, los rasgos siguen vigentes («ok»): el md5 de la entrada de rasgos no se movió.
- **Las 6 `persona_distinta`**, con su texto viejo: ch02_img_06, ch02_img_07 (Arcadio), ch03_img_15 (Muro), ch07_supp_07, ch07_supp_08 y ch07_supp_09 (Carmen adulta).
  - Carmen adulta sigue sin probarse con su texto nuevo.
- **Idempotencia en Colza:** la lista sin llamar después de B da `{'ya_rasgos': 32, 'persona_distinta': 6, 'sin_rasgos': 3}`, 0 a rehacer.
- **Tabla foto → persona → subject viejo → subject nuevo → marca:** `b/tabla_subject.md`. Las 41 filas también están en la hoja.

**md5 de la narración y el papel aprobados, antes y después: IGUALES** (`b/md5_antes.json` = `b/md5_despues.json`, 104 entradas):
- `01a_skeleton.json`, `01b_narracion_v3.json`, `01b_narration.json`, `01b_narration_normalized.json`, `01e_pantalla.json` y `01e_pantalla.md`;
- el `papel_md5` del guion;
- los 97 archivos de `foto_madre/`. Paso0 corrió y no rehízo nada.

**Movimiento de los clips** (`b/movimiento.md`, adenda 1.3)
- **Gancho (ch01), CAMBIÓ:**
  - VIEJO: «A slow, somber documentary shot on grainy film, with muted colors and slight underexposure. The camera makes a slow push-in from the aisle, starting on a medium shot of the seated man and ending closer on his face and curled hands. First the blurred neighbors beside him shout and gesture toward the dock, then the man breathes slowly and lowers his gaze slightly. Hard cold daylight from high pavilion windows mixes with a flat fluorescent wash over the rows of public seats. Everyone stays in place, the man's face and body steady.»
  - NUEVO: «A slow, somber documentary shot on grainy 35mm film, muted colors and slight underexposure. Locked-off medium shot at eye level with a subtle, slow drift inward, starting on the seated heavyset man among the crowded benches and ending a touch closer on his still face and the hands in his lap. First the standing neighbours beside him thrust their arms forward and shout, their blurred shapes shifting at the frame edges; then the seated man breathes slowly and his eyes lower slightly. Hard cold fluorescent light mixed with flat grey daylight from high windows holds steady over the packed courtroom benches. Everyone stays in place, faces and bodies steady.»
- **ch07, igual:** su foto de arranque no tiene persona, así que no se rehízo.

**Costo B:** US$ 3,2859 (Opus 5.5, medido).
- 38 `m03:casilleros`: US$ 3,2652.
- 2 `m03:motion`: US$ 0,0207. Una es el reintento por largo que ya trae `_seedream_video_prompt`.

## Etapa C — Colza: fotos y clips (`c/etapa_c.py`, venv; `asset_manager.process_script`, motor Lite)

**Regla de qué se regenera** (declarada; `c/lista.json` trae el motivo de cada foto):
- Foto /edit (con al menos una madre por `_madres_para_item`, contra el guion vivo) cuyo prompt cambió en B, o con alguna madre o variante más nueva que la foto (rehecha en F78a o F78b después de ella).
- Más los clips del gancho y de ch07 (F78a_REPORT l.127): clip, foto de arranque y foto final.

**Qué se regeneró**
- **38 fotos** (36 /edit + ch01_img_01 + ch07_img_01) **y 2 clips**.
  - Las 6 `persona_distinta` con madre más nueva (ch02_img_06/07, ch03_img_15, ch07_supp_08/09) se regeneraron con su texto viejo y la madre nueva.
  - ch07_supp_07 no entró: su madre no es más nueva, porque ya era foto de control en F78b.
- **Preflight:** antes de mover no faltaba nada; después de mover faltaba exactamente la lista (40); después de generar no falta nada.
- **Lo viejo** está en `<carpeta del cap>/_previas_f78d/`: png, `_native`, `_graded`, `.llamada.json` y, en los clips, el mp4 y la foto final. `c/movidos.json` tiene la lista.
- **Resultado:** 0 fallas, 1 rechazo de Nano Banana → respaldo Seedream (ch04_img_12, Lozano con la chica de espaldas). 68 fotos Flux en el manifest, 2 clips ok.

**Costo C real por servicio** (`c/costo.json`, cost_tracker): **US$ 4,2623**

| servicio | US$ | nota |
|---|---|---|
| fal Nano Banana 2 Lite /edit | 1,596 | tarifa estimada de config (F68) |
| fal Nano Banana 2 Lite t2i | 0,042 | ch07_img_01, sin madre; tarifa estimada |
| fal Seedream 4.5 edit | 0,04 | ch04_img_12, respaldo |
| fal gemini-omni-flash image-to-video | 2,40 | 2 clips de 8 s, 1,20 cada uno |
| Anthropic Opus 5.5 | 0,1842 | instrucción de la foto final + prompt del clip, ×2 |

**Hoja:** `lab/hyperframes/f78d/ETAPA_C.html`.
- Por foto: referencia | vieja | nueva, más persona, marca, subject nuevo, prompt y motivo.
- En los clips: un cuadro del clip viejo y del nuevo, y el movimiento nuevo.

**Mirado a ojo** (hojas de contacto en el scratchpad):
- **La identidad coincide con la madre** en las fotos nuevas: Arcadio con barba y rizos, en todas incluido el gancho; Sancho Rof con lentes gruesos; Muro con bigote; Mercedes con lentes y pelo lacio; Carmen con trenza; Lozano con flequillo; Angela con el pelo ondulado.
- **ch04_img_12** (respaldo Seedream): la chica del primer plano sale de espaldas con la espalda descubierta. Omar tiene que mirarla.

## Chascada (`a/chascada_3_tests.md`)
Los 3 corren en el árbol de `a6ff9a9` (`git archive`, data y output reales en solo lectura) y **ya fallaban ahí, con el mismo error**. No se arregló nada.
- **f51c [1-start]:** un dato real cambió. El `sync_map` de Wittenoom (fuera de git) se reescribió el 2026-10-31 23:08: el ch01 pasó de 32,96 s a 65,68 s, la zona del clip se achicó y el corte cae en «venda blanca.».
- **m03_merge_timing ×2:** el código cambió. Desde `f59d205` (2026-07-04, `anchor_timing.py`), un ancla de una palabra necesita 4 letras o más; las anclas del test («a», «uno»…) no encuentran tiempo.

## Abierto (para Omar y el analista)
1. **El nombre real se volvió a colar** en el texto: ch06_img_06 («Arcadio») y ch07_supp_13 («Arcadio Fernandez»). DECISIONES 08:57 lo pone en «se arregla si se repite», y se repitió (2 de 32). Las fotos ya se generaron con ese texto.
2. **Carmen adulta** (ch07_supp_07/08/09): las 3 volvieron con otra persona y quedaron con su texto viejo. El caso de Carmen adulta con trenza sigue sin probarse.
3. **El refill puede sumar personas que el casillero no nombra.** En ch04_img_12 aparece la chica de 14 años en primer plano y `persona` sigue siendo solo Lozano, así que pasa el chequeo.
4. **Riesgo no cubierto en la cadena completa.** m03 marca `aspecto_fuente` con los rasgos leídos contra el 03_visual de antes de su corrida. Si la foto madre de esa misma corrida rehace los rasgos, las fotos marcadas «rasgos» quedan con los rasgos viejos y el paso no las vuelve a tocar.
5. **ch07_clip_01 se regeneró con el mismo texto** (su foto de arranque no tiene persona), porque el handoff pide los dos clips.

## Veredicto del revisor-handoff
(pegado abajo, íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

Solo leí código y artefactos, y corrí los 13 tests sin red. No corrí fase1_5, etapa_b, etapa_c ni nada que llame a APIs. Tampoco volví a correr los 3 tests de la chascada: confío en `a/chascada_3_tests.md`, que dice haberlos corrido en un `git archive` de a6ff9a9.

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Handoff con md5 cbed0677… | OK | `md5sum` del handoff da cbed0677e2a6ee94148e34dc0b520555 |
| 2 | l.166: única edición de prompt | OK | `git show 7078adb`: el único cambio de texto de prompt es «appearance (or appearance_canon if there is none)». El resto son firmas y código. `a/l166.md` trae antes/después. |
| 3 | `_f8_refill(personas_fijas)` filtra `documented_people`, rasgos del topic entero, persona distinta → ítem viejo con `_rasgos_refill: persona_distinta`, sin reintentos | OK | m03_visual.py `_f8_refill` en el diff: copia del topic filtrada, comparación como conjunto, un solo intento. |
| 4 | `aspecto_fuente` rasgos/canon, sin clave si no hay persona | OK | `_marcar_aspecto`; `aspecto_fuente` y `_rasgos_refill` se agregaron a `CLAVES_F8_PAPEL`. |
| 5 | Paso `aspecto` después de foto madre y antes de assemble, en paralelo, idempotente | OK | fase1_5.py: `_PIPELINE_ORDER`, `VALID_FROM_STEPS` y el bloque nuevo. `rehacer_aspecto_personas` usa `ThreadPoolExecutor`. Si no hay nada que rehacer, no llama ni escribe. En Colza, la lista sin llamar después de B da 0 a rehacer (`{'ya_rasgos': 32, 'persona_distinta': 6, 'sin_rasgos': 3}`). |
| 6 | `--only aspecto` = paso + assemble | OK | fase1_5.py: assemble acepta `from_step == "aspecto"`. |
| 7 | Adenda 1.1: «editado a mano» = copia en `assets/_qa_backups`, leído del disco, `qa_studio_server` intacto | OK | `fotos_aspecto` hace glob de `_qa_backups`. `git log -- qa_studio_server.py` no muestra commits de F78d y no hay diff. |
| 8 | Adenda 1.2: la nota previa `_f8_rehecha` se vuelve a pasar | OK | `nota` se pasa como `note`. Las 3 de Colza (ch05_img_01, ch05_img_03, ch05_img_12) están listadas en el reporte. |
| 9 | Adenda 1.3: si se rehace la foto de arranque de un clip, se regenera el movimiento | OK | Se regenera `video_prompt` con `_seedream_video_prompt`. `b/movimiento.md` y el reporte traen texto viejo y nuevo. El gancho cambió. ch07 no se rehízo porque su foto de arranque no tiene persona, y el reporte lo dice. |
| 10 | Tests sin red, test viejo actualizado y no borrado | OK | `test_module_f78d.py`: 13 passed (corrido por mí con el pedido exacto). `test_module_f50d.py` l.141 solo suma el parámetro `rasgos`. |
| 11 | Etapa A: diff de l.166 y lista de Colza sin llamar | OK | `a/l166.md`, `a/lista_aspecto.md` (41 con persona, 38 a rehacer, 3 sin rasgos, 0 de QA). |
| 12 | Etapa B: tabla por foto, cantidad de `persona_distinta` y QA saltadas | OK | `b/tabla_subject.md`. `b/cambiadas.json` tiene 32 fotos, que más las 6 `persona_distinta` suman las 38. |
| 13 | md5 del papel y la narración sin cambio tras B | OK | Comparé `b/md5_antes.json` con `b/md5_despues.json`: 104 entradas, 0 diferencias. |
| 14 | Etapa C: lo viejo a `_previas_f78d`, nada se borra | OK | `c/lista.json` (38) y `c/movidos.json` (38) tienen las mismas claves. Los 158 archivos de `movidos.json` existen, no están vacíos y coinciden con los 158 que hay en `_previas_f78d`, repartidos en 9 carpetas (ch01 a ch07 flux, ch01 y ch07 veo). Las 38 fotos nuevas existen. |
| 15 | Hoja `ETAPA_C.html` y costo real por servicio | OK | El archivo existe. `c/costo.json` suma US$ 4,2623 por servicio y `b/costo.json` US$ 3,2859, o sea 7,5482 en total. |
| 16 | Chascada: correr los 3 tests en a6ff9a9 y solo reportar | OK, no re-corrida por mí | `a/chascada_3_tests.md`: los 3 ya fallaban en a6ff9a9 con el mismo error. Dice no haber arreglado nada. |
| 17 | DECISIONES.md con fecha 08:57 y lo que NO entra | OK | La línea F78d trae manos, nombre real y Nano Banana 2 como «Lo que NO entra». |
| 18 | Veredicto en el reporte, ESTADO_SESION después | OK, pendiente a propósito | La sección del veredicto está vacía, como pediste. No toqué ESTADO_SESION. |
| 19 | PARADA: sin render ni subida | NO VERIFICABLE | Solo leí el reporte. No hay artefactos de render ni de subida en `lab/hyperframes/f78d`. |
| 20 | Sin hardcode ni flags | OK | No vi constantes numéricas nuevas. `QA_BACKUPS_DIR` es un nombre de carpeta que ya existía en QA Studio. No hay flags que apaguen lo viejo. |

Fuera de alcance: ninguno en código. Las modificaciones sin commitear fuera de la tanda (`diag_234_cap4.py`, `f28a.log`, `pedido_paquetes_wittenoom.txt`) ya estaban en el git status inicial y no son de F78d. `data/scripts/_steps/c4934b7d…/03_visual.json`, `data/scripts/c4934b7d….json` y `output/c4934b7d…/assets/*` cambiaron por B y C, como estaba autorizado.

Observaciones:
- `lab/hyperframes/f78d/a/lista_aspecto.md` quedó modificado en el árbol de trabajo después del commit A. Hoy refleja el estado posterior a B, no el estado «sin llamar» que dice el mensaje del commit.
- Nombre real colado de nuevo: ch06_img_06 («Arcadio») y ch07_supp_13 («Arcadio Fernandez»). DECISIONES lo deja en «se arregla si se repite» y se repitió (2 de 32). Las fotos ya se generaron con ese texto.
- Carmen adulta (ch07_supp_07/08/09) volvió con otra persona las 3 veces y quedó con su texto viejo, sin probar con rasgos.
- ch04_img_12 salió por respaldo Seedream con una chica de espaldas con la espalda descubierta. El reporte pide que Omar la mire.
- ch07_clip_01 se regeneró con el mismo texto, porque su foto de arranque no tiene persona y el handoff pedía los dos clips.

Riesgos que el contrato no cubre:
- Si en una misma corrida la foto madre rehace los rasgos, las fotos marcadas «rasgos» quedan con los rasgos viejos y el paso no las vuelve a tocar. El reporte lo declara en «Abierto» punto 4.
- El chequeo de `persona` no detecta personas extra que el refill meta en la imagen sin nombrarlas.
- Detectar «tocada en QA» por la copia en `_qa_backups` depende de que ese editor siga guardando la copia. Una edición sin copia no se detecta.

### Adenda de CC
- **`a/lista_aspecto.md`:** volvió al contenido del commit A, la lista «sin llamar». La lista de después de B (0 a rehacer) quedó en `b/lista_despues_b.md`.
- **Punto 19 (PARADA):** no corrí fase2b, render ni subida. Los únicos procesos fueron `fase1_5 --only aspecto` (B) y `asset_manager.process_script` (C).
- **Costo:** el Opus y los clips de Omni Flash son cobro medido. Lite y Seedream son la tarifa de config (F68), como en F78c.
- **Riesgo de QA sin copia:** lo dejo como dato. La adenda 1.1 fija esta regla.
