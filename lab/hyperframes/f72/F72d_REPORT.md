# F72d — se borra la pregunta de cierre (texto y pausa congelada); nuevo guion de pantalla de Wittenoom sin aprobar

Handoff: `lab/hyperframes/f72/HANDOFF_F72d.md` (md5 `4b8c63c6f9c4eea19b8f1f3ef4fca25b`, verificado con md5sum). Topic `123bbb64-9fca-4395-8bf4-57d60e219ef1`, rama `f11-guion-v4`. Decisión de Omar del 2026-11-03 22:14 («quita esos cierres»).

No corrí `--aprobar-guion`, `--gfx`, `--plan-edit` ni run_pipeline. No toqué prompts, fondos ni main. El mp4 de F72c (`efc0c71d…`) y los `_fase2b_work_desfasado_*` siguen en disco, sin tocar.

## Resultado en una línea

La pregunta de cierre está borrada del código: funciones, plantilla, CSS, perillas, perfiles, lab y tests. El negro de 1 s se queda y ahora arranca donde termina la voz. En `--plan-only` cada cap perdió solo la lectura de su pregunta: 26,13 s en total, con todos los caps dentro de ±1 cuadro. Exit 0, 246 s, US$ 0. La mezcla mide 798,3 s. El guion de pantalla quedó **sin aprobar**.

## A — Inventario

Lo armó un subagente sobre HEAD `f072a2f` y lo crucé con mi grep. Las líneas son de HEAD.

Primero, lo que había que cuidar. Hoy el negro dependía de la pregunta:
- `closing_question` (`gfx_layer.py:304-305`) era la única función que creaba `black_hold`.
- `pausa_de_cierre` (:316-318) daba 0 sin `chapter_question`.

Si se borraba la pregunta tal cual, se iba también el negro. Por eso el negro pasa a una función propia.

| archivo:línea (HEAD) | qué hace | se borra / se queda |
|---|---|---|
| `gfx_layer.py:276-279` `lectura_pregunta` | lectura de la pregunta a 15 cps | **se borra** (los 15 cps de `pantalla_colocar.LECTURA_CPS` siguen para las fichas) |
| `gfx_layer.py:282-307` `closing_question` | pregunta + `black_hold` en `clip_dur + pausa` | **se borra**; la reemplaza `negro_de_cierre`: `black_hold = {start: clip_dur, duration: black_hold_sec}` |
| `gfx_layer.py:310-320` `pausa_de_cierre` | pregunta + negro, 0 sin pregunta | **se queda, cambiada**: devuelve solo `black_hold.duration` |
| `gfx_layer.py:323-333` `pausa_a_disco` | escribe `gfx_pause_<cap>.json` {pause, text} | **se queda** (lo leen la música y el mapa de intensidad); sin `text` |
| `gfx_layer.py:496` `"chapter_question": None` | campo vacío del plan base | **se borra** |
| `gfx_layer.py:704, 725` `question_sources=…` | argumento muerto del candado | **se borra** |
| `gfx_layer.py:739-747` | pregunta en el plan nuevo; pausa en el plan fijo | **se queda la estructura**: `negro_de_cierre` / `pausa_a_disco`; log «negro de cierre: X s» |
| `gfx_layer.py:237` `extend_base`, :748-754 | alarga el base `pause` segundos | **se queda** (ahora con el negro de 1 s) |
| `gfx_realizador.py:15-16, 175-202` | `FUENTES_CIERRE`, `_termina_en_pregunta`, `pregunta_cierre_fuente`, `pregunta_cierre` | **se borran** |
| `gfx_director.py:3, 87-98` | `_STOP` + `question_keyword` (solo la pregunta), imports `re` y `normalize` | **se borran** |
| `gfx_director.py:59-65, 80` `next_sources` | narración del cap siguiente | **se queda**: el lab lo usa para `next_chapter` (`gfx_lab_server.py:244`) |
| `gfx_literal_lock.py:45, 52` `question_sources`; :99-100 | parámetro muerto; texto de la pregunta en `plan_strings` | **se borran** |
| `gfx_project.py:519-521` | cue de la pregunta | **se borra** |
| `gfx_project.py:820-834` | overlay, persiana y fundido de la pregunta (`question_dim`) | **se borra** |
| `gfx_project.py:234, 239, 616, 631` `question_font_px` | tamaño del dato de la ficha (`$question_px` del CSS) | **se queda**: la ficha lo usa (`gfx_common.css:16`) |
| `gfx_project.py:538, 815-818` negro | cue y `<div id="bh">` | **se quedan** |
| `gfx_templates/chapter_question.html.tmpl` | plantilla | **se borra** (archivo) |
| `gfx_templates/gfx_common.css:34-40, 77` | `#cq-dim`, `#cq`, `#cq-text`, `.kw`, `.cq-line` | **se borran**; `.tc-box.ficha` se queda |
| `gfx_sparse.py:6, 66-68, 204-205` | ventana y corrimiento de la pregunta | **se borran**; los del `black_hold` (:73, :189) se quedan |
| `gfx_guion.py:8, 12-13, 305-309, 413, 472-473` | evento «pregunta de cierre», filtro del rotulista y **chequeo 4 «pregunta de cierre sin lectura»** | **se borran**; el evento «costura» del negro (:310) y el chequeo 7 se quedan |
| `gfx_config.py:155-161` | bloque `chapter_question` del catálogo | **se borra** |
| `gfx_config.py:263, 265, 266` | `question_dim`, `question_auto`, `question_pause_sec` | **se borran** |
| `gfx_config.py:264, 267` | `question_font_px`, `black_hold_sec` | **se quedan** (ficha; negro) |
| `gfx_config.py:376, 382` | huérfanas `question_max_words_auto`, `question_rubric`; sfx `chapter_question` | **se borran** de las listas |
| `gfx_profiles/misterio.json` | `question_auto`, `question_pause_sec`, `question_dim`, `question_max_words_auto`, `question_rubric`; sfx y bloque `chapter_question`; marca `identity.marks.chapter_question` | **se borran**; `black_hold_sec: 1.0` se queda |
| `gfx_profiles/finanzas.json:30` | bloque `chapter_question` | **se borra** |
| `gfx_profiles/misterio_golden_ch02.json` | `chapter_question` manual del plan dorado y su marca | **se borran**; el `black_hold` del dorado (start viejo) queda como estaba: es un artefacto del lab |
| `gfx_lab_server.py:24, 182-197, 265-267, 278-289, 598-599, 643-644` | `/question` (ya muerto), pregunta desde la caché `gfx_question`, excepción del candado para la pregunta manual | **se borran**; el negro por defecto del lab pasa a `start = self.duration` |
| `gfx_lab_server.py:126-128` `TAIL_SEC = 4.5` | cola del preview (pregunta 3 + negro 1 + margen) | **se queda**: achicarlo pide un número nuevo, que el handoff no trae |
| `fase2b.py:2679` `gfx_question_{cap}.json` en `_segment_hash` | archivo muerto desde F36 D | **se borra** |
| `fase2b.py:1225-1229, 1572-1583, 1726, 2880-2979, 3583` | silencio del segmento, `_gfx_pauses`, música, `_segmento_de_cap`, `_medir_cierre`, costuras | **se quedan** (leen la pausa genérica, ahora el negro); solo cambian docstrings y mensajes |
| `gfx_style.py:114`, `freeze_check.py:5` | docstrings | **se quedan**, con el texto corregido. El dip «cierre» de la última escena no depende de la pregunta |
| `script_engine/sfx/drone_subida.wav` | sonido de la pregunta (el perfil ya no lo referencia) | **se queda**: es parte del juego de 15 sfx de `sfx/make_sfx.py` y `test_module_f29b` compara la librería entera con ese juego. Lo borré primero y lo restauré |
| `lab/identidad/lab_foto.js`, `index.html` | botón «otra pregunta» del lab | **se quedan** (lab, no producción; `test_module_gfx_lab.py::test_pantalla_iconos_y_pregunta` los lee). El endpoint que llamaban ya estaba muerto |
| `m01a_escaleta.py` `pregunta_pantalla`/`pregunta_valida`, `guion_v4.py` | rúbrica de la escaleta y prompts del guion | **fuera de alcance**: son prompts y Fase 1, no la pregunta de pantalla |

**Tests**
- Borrados:
  - `test_module_f72b.py` (entero) y sus entradas congeladas `lab/hyperframes/f72/b_fase1_wittenoom/`;
  - `f38e_b::test_b4_i_…`, `f32::test_b2_la_pregunta_dura_su_lectura`, `gfx_0d::test_plantilla_question`.
- Reescritos, porque el negro es toda la pausa:
  - `f38e_a`: `test_r8_pausa_de_cierre_es_el_negro`, `test_r8_pausa_a_disco_…`, `test_r8_plan_congelado_alarga_el_base_con_el_negro` (1,0 s) y `test_r8_negro_de_cierre_y_el_plan_fijo_dan_la_misma_pausa`;
  - la costura `test_a3_…` usa `PLAN_N` y el mensaje nuevo.
- Adaptados:
  - `f32::test_guion_de_un_cap_con_todos_los_tipos`;
  - `f30` (la ventana del cierre la abre el negro);
  - `gfx_config` (inventario sin el bloque);
  - `gfx_profiles` (misterio sin las perillas, `black_hold_sec == 1.0`);
  - `gfx_lab::test_candado_en_el_preview` (sin pregunta manual);
  - los fixtures de `f36c_pantalla`, `gfx_emphasis`, `gfx_router` y `gfx_sparse`;
  - los docstrings de `f29a`, `f38e_b` y `gfx_0d`.

## B — borrado y simulación

**Diff:** 38 archivos, +189 / −1778 líneas. La mayor parte son las dos entradas congeladas de F72b (1278 líneas) y `test_module_f72b.py`.

Cómo queda el cierre: `negro_de_cierre(resolved, work_dir, cap, clip_dur)` pone `black_hold = {start: clip_dur, duration: black_hold_sec}` y escribe `gfx_pause_<cap>.json = {"pause": 1.0}`. `pausa_de_cierre` lee solo el negro. Todo lo que viene después sigue leyendo la pausa genérica, sin cambios: el alargue del base, el silencio del segmento, la música, `seg_dur` y la costura.

Simulación por cap. «Antes» es el `seg_dur` del guion F72b/F72c y la pregunta es la de su plan resuelto. «Esperado» es antes − pregunta; el negro queda. «Después» sale del `--plan-only` de la etapa C:

| cap | antes (seg_dur) | pregunta | negro | esperado después | después (plan-only) | diferencia |
|---|---|---|---|---|---|---|
| ch01 | 70.300 | 3.467 | 1.0 | 66.833 | 66.800 | -0.033 |
| ch02 | 107.233 | 4.400 | 1.0 | 102.833 | 102.833 | +0.000 |
| ch03 | 178.800 | 6.133 | 1.0 | 172.667 | 172.700 | +0.033 |
| ch04 | 103.500 | 3.800 | 1.0 | 99.700 | 99.700 | +0.000 |
| ch05 | 135.100 | 3.267 | 1.0 | 131.833 | 131.833 | +0.000 |
| ch06 | 131.700 | 3.200 | 1.0 | 128.500 | 128.500 | +0.000 |
| ch07 | 95.267 | 1.867 | 1.0 | 93.400 | 93.400 | +0.000 |

- Preguntas sacadas: **26,134 s**, como esperaba el handoff (26,13).
- Los 7 caps cuadran dentro de ±1 cuadro (0,0333 s). ch01 y ch03 se corren un cuadro por el redondeo a cuadro de `seg_dur`. No hubo PARADA.
- Video: 795,766 s de segmentos + 2,5 s de entrada = **798,27 s**; la mezcla da 798,3 s. El handoff esperaba ≈ 798,2 s.

En los 7 planes nuevos no hay `chapter_question`. Cada uno trae `black_hold` de 1,0 s que termina en `clip_dur`, y `gfx_pause_chNN.json = {"pause": 1.0}`:

```
ch01 {'start': 65.8, 'duration': 1.0} clip_dur 66.8 · ch02 101.833 → 102.833 · ch03 171.667 → 172.667 · ch04 98.7 → 99.7
ch05 130.833 → 131.833 · ch06 127.5 → 128.5 · ch07 92.367 → 93.367 (seg_dur 93.400)
```

## C — `fase2b.py <tid> --plan-only`

Con la venv. 22:27:37 → 22:31:45, **exit 0**, sin exit 2: `fondos.json` sigue en `68e57663…`. Log en `lab/hyperframes/f72/d/plan_only.log`, sin commitear.

```
     ✓ ch01 plan 19s · segmento 66.80s
     ✓ ch02 plan 29s · segmento 102.83s
     ✓ ch03 plan 14s · segmento 172.70s
     ✓ ch04 plan 8s · segmento 99.70s
     ✓ ch05 plan 8s · segmento 131.83s
     ✓ ch06 plan 8s · segmento 128.50s
     ✓ ch07 plan 8s · segmento 93.40s
  🔊 mezcla de previsualización: …\_fase2b_work\mezcla_preview.wav (798.3s, 12s)
     ✓ dos bloques al mismo tiempo
     ✓ bloque que cruza un corte
     ✗ texto sin lectura
     ✓ cifra que contradice la voz
     ✗ a_pantalla
     ✓ costuras con cuadro no negro
     ✗ inicio de voz por cap
     ✓ gancho no vacío
     ✗ inicio de música por cap
     ✗ papel sin colocar
     ✓ papel sin alinear
     ✓ relojes del papel (informativo)
  ⏱  --plan-only 246s · costos {}
[22:31:45] … Costo total: $0.0000
exit 0
```

- **Chequeos:** ahora son 12, porque el 4, «pregunta de cierre sin lectura», se borró con la pregunta. Los 5 ✗ son los mismos de F72b y F72c. «costuras con cuadro no negro» da ✓ en las 6 costuras: negro de 1 s hasta el corte, voz callada a −120 dB y el entrante sube desde negro.
- **Archivos:**
  - `GUION_PANTALLA.md`: `6b2b9944d70efa89796bb0516172ebde` → **`433eb3e584460e698483ae4fece9c8ce`**.
  - `GUION_PANTALLA.json`: `4f6ba64c…` → `e7aa256fed52b0bdba23421fdfc29bef`. Trae `aprobado: None` y no hay ningún evento «pregunta de cierre» (0 menciones en el .md).
- **Duración de la mezcla:** 798,3 s. **Tiempo:** 246 s. **Costo:** US$ 0.
- **Estado:** `etapa_de` = `('aprobar_guion', 'el guion de … no está aprobado …')`. La aprobación de F72c ya no vale porque cambiaron los planes.

## Suite amplia (la de F72b, una corrida completa al final)

`3 failed, 1402 passed, 29 skipped, 2 xfailed` en 133 s. Log: `lab/hyperframes/f72/d/suite_amplia.log`.

- Las 3 fallas son las heredadas: `test_module_f51c.py::test_f51c_corte_veo_real_de_wittenoom[1-start-paredes de chapa.]`, `test_module_m03_merge_timing.py::test_c_guarda_de_minimo` y `::test_c_veo_path_y_veo_anchor_intacto`.
- Quedan fuera `fase2b_*`, `gfx_lab` y `f58`, como en F72b, porque escriben en disco real. `test_module_gfx_lab.py` lo toqué pero no lo corrí: compila con `ast` y `gfx_lab_server` importa.
- `pedido_paquetes_wittenoom.txt` sigue en `489cb2a0…`.
- Mapa: los stickers de los 16 archivos tienen md5 y texto nuevos, las líneas de las funciones muertas están corridas a su lugar, `pregunta_cierre` salió de las muertas y el sticker de la plantilla se borró. `mapa --check`: **160 archivos de producción · 0 fallas**.

DECISIONES.md: agregué la línea de Omar del 2026-11-03 22:14. Dice que anula el componente 5 del catálogo del 2026-10-26 18:17, F72b A del 2026-11-03 20:50 y la línea del 2026-10-26 11:02 de los 15 cps. Los 15 cps siguen para las fichas.

## D — PARADA

El guion de pantalla nuevo (`433eb3e5…`) espera la validación del analista. No lo aprobé ni corrí render.

Commit: el código, los tests, los perfiles, los stickers, la plantilla y las entradas congeladas borradas, este reporte, `lab/ESTADO_SESION.md` y `DECISIONES.md`. Quedan fuera los logs de `lab/hyperframes/f72/d/`, `diag_234_cap4.py`, `f28a.log`, `pedido_paquetes_wittenoom.txt` y las ENTRADA.

## Veredicto del revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Handoff íntegro (md5) | OK | md5sum = 4b8c63c6…, coincide |
| 2 | A: inventario archivo:línea, se borra/se queda | OK | F72d_REPORT.md:21-57; el negro se separa de la pregunta (`negro_de_cierre`) y se justifica lo que se queda |
| 3 | B: borrado, no apagado (sin flag, plantilla ni tests de lo borrado) | OK | `chapter_question.html.tmpl` y `test_module_f72b.py` borrados (git status). Grep en producción: sin `closing_question`, `pregunta_cierre`, `question_auto`, `question_pause_sec`, `question_dim`, `FUENTES_CIERRE`. Los restos están en comentarios, asserts de ausencia, `.bak_f3` y `IDENTIDAD_misterio.md` |
| 4 | Tests | OK | Corrí 12 archivos tocados: 79 passed, 4 skipped. No corrí gfx_lab, only_cap ni f58. El reporte dice que gfx_lab se tocó pero no se corrió (solo compila) |
| 5 | Simulación por cap (±1 cuadro, total 26,13 s) | OK | Reporte:83-94. ch01 −0,033 y ch03 +0,033 son 1 cuadro. Total 26,134 s. Los 7 planes resueltos no tienen la palabra "question". Cada `black_hold` es de 1,0 s y termina en el `clip_dur`. Cada `gfx_pause_chNN.json` = `{"pause": 1.0}` |
| 6 | C: `--plan-only`, exit 0, costo US$ 0, guion sin aprobar | OK | `lab/hyperframes/f72/d/plan_only.log` (según el reporte). GUION_PANTALLA.md = 433eb3e5…, coincide con el reporte. No verifiqué el estado "sin aprobar" ni el .json |
| 7 | Reglas fijas (nunca aprobar, gfx, plan-edit, run_pipeline; sin tocar el mp4 ni los desfasados) | OK | `_final_gfx.mp4` sigue en efc0c71d…. Los dos `_fase2b_work_desfasado_*` existen. No hay rastro de aprobación en el guion. Prompts y fondos fuera del diff |
| 8 | Mapa y stickers al día | OK | `mapa_modulos.py --check`: 160 archivos, 0 fallas. Solo `fase2b_gfx.json` aparece modificado en `lab/mapa/stickers`, y el reporte dice 16 archivos. No lo contrasté |
| 9 | Suite amplia completa | OK | `suite_amplia.log`: 3 failed, 1402 passed. Las 3 fallas son heredadas (f51c y 2 de m03_merge_timing), y no las reproduje. Se excluyeron fase2b_*, gfx_lab y f58 como en F72b |
| 10 | DECISIONES: línea de Omar 22:14 con lo que anula | OK | `DECISIONES.md:234` |
| 11 | PARADA: F72d_REPORT.md, ESTADO_SESION, commit | PARCIAL | El reporte existe (13 KB). ESTADO_SESION y el commit están pendientes, como se avisó |

Observaciones:
- `gfx_lab_server.py:186` conserva `plan.pop("chapter_question", None)`. Es inocuo, pero es un resto de lo que se iba a borrar.
- `gfx_profiles/IDENTIDAD_misterio.md:12` todavía lista "Pregunta de cierre (chapter_question)". El reporte no lo menciona, así que queda un documento de identidad que contradice la decisión. Lo decidís vos si es doc histórico o hay que corregirlo.
- `lab/mapa/hechos.json` conserva menciones a `closing_question`. Pasa el `--check`, pero es data vieja.
- `test_module_gfx_lab.py:189` conserva "chapter_question" en un set de tipos. Ese test se tocó y no se corrió.
- Diff medido: 36 archivos, +189/−500 en tracked. El reporte dice "38 archivos, +189/−1778" porque cuenta las entradas f72b ya staged. Es consistente.
- El `drone_subida.wav` queda sin referencia en el perfil. Se justifica porque `test_module_f29b` compara la librería entera.

Fuera de alcance: ninguno atribuible a F72d. Los tres que dijiste que venían de antes (`diag_234_cap4.py`, `f28a.log`, `pedido_paquetes_wittenoom.txt`) figuran modificados, pero no son de esta tanda. Los `??` (lab, probes) son previos.

Riesgos que el contrato no cubre:
- `TAIL_SEC = 4.5` en el preview del lab sigue dimensionado para la pregunta de 3 s. Es un número viejo que nadie decidió.
- El render real de ~798 s no se pudo comprobar. Las duraciones salen del plan y de la mezcla de previsualización, no de un mp4.

## Adenda de CC

- **`gfx_lab_server.py:186` `plan.pop("chapter_question", None)`:** está a propósito. El lab carga planes resueltos de renders anteriores que todavía traen la clave; sin el pop, `with_defaults` los pasaría tal cual al proyecto. No queda nada que la dibuje, pero así el plan del lab queda limpio.
- **`gfx_profiles/IDENTIDAD_misterio.md`:** no lo toqué. Es la foto que el lab de identidad sacó el 2026-10-20 01:20. Ya estaba desfasado: dice negro de 0,75 s y el perfil vigente trae 1,0 s. CLAUDE.md lo usa como fuente de números («identidad F3»), y editarlo sería reescribir lo que Omar anotó ese día. Queda abierto para el analista: anotarlo como borrado por F72d o dejarlo como histórico.
- **`test_module_gfx_lab.py:189`:** ese set es la lista de ids de `lab/identidad/catalogo.json`, el catálogo del lab, que sigue teniendo `chapter_question` en la línea 2260. No es producción y no lo cambié. El test que sí tocaba la pregunta, `test_candado_en_el_preview`, quedó sin pregunta manual.
- **`lab/mapa/hechos.json`:** es la salida vieja del auditor de estructura. Se regenera con REPO_MAP, no con `--check`; no lo regeneré.
- **Render de ~798 s:** el handoff pide D = PARADA sin render. La cifra sale del plan (`seg_dur`) y de la mezcla de previsualización.

PARADA.
