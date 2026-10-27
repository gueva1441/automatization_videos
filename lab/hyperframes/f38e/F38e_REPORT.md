# F38e — lo que rompe cualquier video, y nada más — REPORTE

Handoff `lab/hyperframes/f38e/HANDOFF_F38e_lo_que_rompe_cualquier_video.md` (md5 `4e8fb36cbd9b569355844b09cab0f77a`).
Rama `f11-guion-v4`, base `7fb43e0`. Modelo: Fable high.

Pedido literal de Omar (palabra por palabra):

> Modelo: Fable high.
> Leé y ejecutá el handoff lab/hyperframes/f38e/HANDOFF_F38e_lo_que_rompe_cualquier_video.md (md5 4e8fb36cbd9b569355844b09cab0f77a), rama f11-guion-v4.
> Orden fijo:
> 0. Paso 0: verificá md5 de DECISIONES.md (463bd8e5…) y del handoff; commit tal cual (si no coinciden: PARADA).
> 1. A (ensamble: r1 caché + R8 negro), B (colocación B1–B4), C (papel m01e-6 con respaldo y autor) y E (títulos) EN PARALELO, un subagente cada una. Los prompts se copian letra por letra de los .md de lab/hyperframes/f38/.
> 2. D (borrar la tarjeta fecha-hora) después de A.
> 3. Cada parte termina con su salida en texto (tablas y mediciones del handoff).
> 4. Suites rápida y amplia; revisor-handoff con veredicto íntegro en lab/hyperframes/f38e/F38e_REPORT.md; ESTADO; commits por parte con rutas explícitas.
> Reglas fijas: sin render completo de Vajont, sin --aprobar-guion, nada en data/, sin fase3 ni merge, tope US$ 1,00, ningún número nuevo fuera de la tabla de constantes.
> PARADA al terminar.

## Lecturas declaradas (enteras, antes de tocar código)
- `CLAUDE.md`; `DECISIONES.md` (md5 `463bd8e513796ef3dd6260f346133cd3`, con la línea 12:32); `lab/ESTADO_SESION.md` (cabecera y bloques de hoy: F38e-0, render v6, F38d, F38c, F38b, F38).
- Notas de cierre de las otras sesiones en la carpeta compartida: `F38_cierre.md`, `F38b_cierre.md`, `F38c_cierre.md`, `F38d_cierre.md`, `v6_cierre.md`.
- El handoff entero; `lab/hyperframes/f38/REVISION_GUION_F38d.md` (§1–§6); `F38_REPORT.md` §Render v6 (abierto r1–r7 y los dos veredictos); `F38e0_REPORT.md` entero (tablas de las dos pruebas, abierto e1–e11, veredicto); `PRUEBA1_prompt_rotulos.md` (md5 `240e3e7bf13656cb62f68b598393f41f`); `PRUEBA2_prompt_titulos.md` (md5 `e644cb0e7adfdd607ecba33a07f67205`); `.claude/commands/tanda.md`; `lab/MAPA_MODULOS.md`.
- Código leído antes de los briefs: `gfx_layer.apply_gfx`/`closing_question`, `fase2b._gfx_pauses`/intro/tarjeta, `pantalla_colocar.instantes`/`repartir`, `gfx_realizador.ventanas`/`pregunta_cierre`, `m01e_pantalla` (constantes, formatos, `validar`, `llamar`, `main`), `m01d_particion.titles`, `voz_datos`, `.claude/hooks/guard_render.py`, `cost_tracker._save_to_history`.

## Paso 0 (`2453cf8`)
- `md5sum DECISIONES.md` = `463bd8e513796ef3dd6260f346133cd3` ✓ (el del handoff); `md5sum` del handoff = `4e8fb36cbd9b569355844b09cab0f77a` ✓ (el del pedido).
- Commit `2453cf8` con solo esos dos archivos, tal cual (`git show --stat`: DECISIONES.md +1, handoff +97).
- `F38e0_REPORT.md` y `ESTADO_SESION.md` no figuraban modificados (ni por fin de línea) al arrancar: no se tocaron en el paso 0. Los M ajenos (`diag_234_cap4.py`, `gfx_profiles/*`, `f28a.log`) y los `??` viejos no entran en ningún commit.

## Módulos que toca la tanda (paso 2 de `/tanda`; sticker = `lab/MAPA_MODULOS.md`)
| parte | módulo | sticker hoy (mapa) | después de la tanda |
|---|---|---|---|
| A | `gfx_layer` | El director de orquesta de la capa gráfica de un capítulo: llama a todos los demás en orden y hace el render en HyperFrames; con el guion aprobado dibuja el plan congelado. | la capa guarda el md5 del plan con que se dibujó y con `reuse` se rehace si no coincide («capa de otro plan: se rehace») |
| A | `fase2b` | El armador final: junta imagen, voz, subtítulos y música de cada capítulo en un segmento y los pega; con `--gfx` la capa; si el plan de ch01 trae la tarjeta, el mp4 arranca con ella. | el segmento dura voz + pausa de la pregunta + negro y el negro se mide en el mp4 (`ffprobe` ±1 cuadro y `blackdetect` del cierre, ✗ en el log) |
| B | `pantalla_colocar` | Pone cada texto del papel en su lugar: duración por lectura, forma, reparto «nunca al mismo tiempo» con el crítico en cada intento, moviendo en vez de cortar. | la escalera prueba todo inicio de escena dentro de la oración ancla (antes o después del ancla); el reloj mueve su fin con el intento; todo movido declara qué falló en cada intento anterior |
| B | `gfx_realizador` | Hace que la pantalla obedezca a la escaleta: ventanas por beat, qué datos puede mostrar cada uno y la pregunta de cierre del último beat (`cierre` literal). | la pregunta de cierre es lo que dice la voz (última oración con «?», o las oraciones de la voz alineadas con el `cierre`; si no, el `cierre`) |
| C | `m01e_pantalla` | Fase 1: el guion de pantalla EN PAPEL, una llamada a Sonnet por video (prompt m01e-5), reintento parcial con vueltas. | prompt m01e-6 (el de la prueba 1, letra por letra); campos `respaldo` y `autor`; el candado mira el respaldo; el autor de la cita se verifica contra el archivo |
| E | `m01d_particion` | Fase 1: parte el guion en 7 caps; `titles()` escribe los títulos con Flash viendo solo `imagen_sensorial`. | `titles()` manda el pedido de la prueba 2 (promesa del cap: función, qué se ve, pregunta que abre, pico y cómo termina) |
| D | `voz_datos`, `m01e_pantalla`, `pantalla_entrada`, `gfx_layer`, `gfx_guion`, `fase2b` | la tarjeta fecha-hora del segundo 0 (sale de la voz; se dibuja en la intro; chequeo 11 del guion) | **borrada** (DECISIONES 11:21): código, filtro de dibujo, chequeo, tests y entrada del guion; el video arranca con la primera imagen |

Una variable por parte: A el ensamble (caché + negro), B la colocación (escalera, reloj, movido, pregunta desde la voz), C el papel (prompt + respaldo + autor), E los títulos, D la tarjeta. El handoff ya las separa; no se mezclaron.

## Constantes (ninguna nueva; la tabla del handoff)
| valor | dónde | origen |
|---|---|---|
| `black_hold_sec` 1,0 s | R8 | perfil `gfx_profiles/misterio.json` (identidad F3, existente) |
| 15 cps | lectura de la pregunta de cierre | `pantalla_entrada.LECTURA_CPS` (estándar de subtitulado, DECISIONES 11:02 del 26) |
| tope US$ 1,00 | C, regenerar papel | `m01e_pantalla.TOPE_USD_RESPALDO` (Omar, F37); el perfil no trae `costos.m01e_tope_usd` |
| md5 `38e5ba14…` | candado de ch02 `--only-cap` sin gfx | ESTADO (existente) |
Derivados sin número propio: «±1 cuadro» = `1/fps` del render; `blackdetect` con los parámetros por defecto de ffmpeg (estándar).

## Cómo se corrió (orquestación)
- **Paralelo** (DECISIONES 01:23): A, B, C y E a la vez, un subagente `general-purpose` cada una, archivos sin solaparse (A `gfx_layer`+`fase2b`; B `pantalla_colocar`+`gfx_realizador`; C `m01e_pantalla`; E `m01d_particion`); tests nuevos en archivos propios (`test_module_f38e_{a,b,c,e}.py`); los tests existentes compartidos (`f34`, `f36`, `f36c_pantalla`) con un solo dueño o sin editar.
- **Los subagentes no commitean ni corren el candado**: commit por parte lo hace CC, en serie, con `lab/hyperframes/f38e/verificar.sh <parte>` (md5 de ch02 de Orleans + suite rápida + suite amplia con `-n auto`), porque cuatro corridas a la vez compartirían `output/` y el índice de git.
- **El `--plan-only` de B.5 corre después del render de A.4**: el guion de Vajont está aprobado (`md5_planes 35576ed6…`) y `guard_render` solo deja pasar `--only-cap ch02 --gfx` mientras los planes no cambien; el `--plan-only` de B los reescribe. Orden real: A.4 → B.5 → D.
- **D después de A, B, C y E**: toca `fase2b`/`gfx_layer` (A) y `m01e_pantalla` (C), además de `voz_datos`, `pantalla_entrada` y `gfx_guion`.
- Antes de B.5 se copió `output/f8s3-vajont-f30/GUION_PANTALLA.*` a `lab/hyperframes/f38e/b/antes/` (md5 `.md` `0af5b1dca3ab8cac1cb00f534e4b24c9`, `.json` `f751e0910e39f41abf119345153108df`).
- Candado por commit: en cada commit de parte, la suite rápida (58) y los tests de la parte, corridos por CC; el `verificar.sh` entero (md5 de ch02 `38e5ba14…` + suite amplia `-n auto`) después del último commit de código (D), porque mientras los otros subagentes editan sus módulos la suite amplia no mide un estado estable. Se anota en cada commit.

## A — Ensamble: r1 caché + R8 negro + costuras en el mp4 (`96c2889`)
Subagente A. Archivos: `script_engine/gfx_layer.py` (+105/−…: `pausa_de_cierre`, `pausa_a_disco`, `sidecar_plan`, `md5_plan_resuelto`, `_sellar_capa`, `capa_reusable`; la rama del plan congelado y `closing_question` usan la misma cuenta; reuse con sidecar; sidecar escrito en los dos `return out`), `fase2b.py` (+90: `_medir_cierre`, `_costura_del_segmento`; llamadas después de «✓ seg_NN …» en el loop en fila y en `_segmentos_en_paralelo`, solo `--gfx`; `_segment_hash` incluye `gfx_plan_<cap>.resolved.json`), `test_module_f38e_a.py` (13 tests), `test_module_gfx_layer_fallback.py` (`test_reuse_no_re_renderiza` ahora escribe plan + sidecar, con el porqué), `lab/hyperframes/f38e/a/` (`A_SALIDA.md`, `onlycap_ch02_gfx.log`, `tabla_v6_segmentos.md`, `medir_v6.py`). CRLF ✓ (comprobado por CC con `file`).

**Causa de R8 (con datos):** `script_engine/gfx_layer.py:674` (HEAD de antes): en la rama del plan congelado (F34; v6 corrió así: «plan congelado» en `gfx_ch02.log` 03:57) `pause = chapter_question.pause` (6,4 s en ch02) **sin** `black_hold.duration` (1,0); `closing_question` (304–307) sí devolvía `pause + bh`. Así `extend_base` alargó 6,4 en vez de 7,4, `clip_dur` = 139,567 = `black_hold.start` → el negro cayó después del fin del clip (el disperso lo descarta en `gfx_sparse.py:189-192`) y el segmento (`-t max(audio, clip)`) salió 1,0 s corto. No era el armado de `fase2b` (sospecha del analista): la capa `chNN_gfx.mp4` ya medía igual que el segmento. Arreglo general: una sola cuenta `pausa_de_cierre(resolved)` = pregunta + negro en los dos caminos, y `gfx_pause_<cap>.json` sale del plan que se dibuja.

Tabla de los 7 segmentos de v6 (medidos con `fase2b._medir_cierre`, solo lectura):

| cap | seg_0N | guion seg_dur | dif | gfx_escenas clip_dur / pausa | gfx_pause | plan: pause + bh (start) | negro al cierre |
|---|---|---|---|---|---|---|---|
| ch01 | 100.600 | 101.600 | -1.000 ✗ | 100.600 / 5.667 | 6.667 | 5.667 + 1.0 (100.600) | ✗ ninguno |
| ch02 | 139.600 | 140.600 | -1.000 ✗ | 139.567 / 6.400 | 7.400 | 6.400 + 1.0 (139.567) | ✗ ninguno |
| ch03 | 134.300 | 135.300 | -1.000 ✗ | 134.267 / 5.267 | 6.267 | 5.267 + 1.0 (134.267) | ✗ ninguno |
| ch04 | 128.000 | 128.967 | -0.967 ✗ | 127.967 / 6.133 | 7.133 | 6.133 + 1.0 (127.966) | ✗ ninguno |
| ch05 | 174.700 | 175.700 | -1.000 ✗ | 174.667 / 5.600 | 6.600 | 5.600 + 1.0 (174.667) | ✗ ninguno |
| ch06 | 173.200 | 174.200 | -1.000 ✗ | 173.200 / 5.400 | 6.400 | 5.400 + 1.0 (173.200) | ✗ ninguno |
| ch07 | 195.900 | 196.900 | -1.000 ✗ | 195.867 / 12.867 | 13.867 | 12.867 + 1.0 (195.867) | ✗ ninguno |

(`blackdetect` también vacío sobre los últimos 8 s con `d` por defecto y `d=0.9667` en seg_01, seg_02, seg_07 y `ch02_gfx.mp4` de v6.)

**r1 — huella elegida y por qué:** md5 de los **bytes** de `gfx_plan_<cap>.resolved.json` (`md5_plan_resuelto`), la misma huella por archivo que `aprobacion.md5_planes` (nombre + bytes): con guion aprobado ese archivo ES el plan congelado que se dibuja; sin aprobación `apply_gfx` lo reescribe al dibujar y el sidecar se escribe después. No JSON canónico: un `--plan-edit` cambia los bytes y eso es lo que hay que detectar, y sería una segunda huella distinta de `md5_planes`. Sidecar `chXX_gfx.plan.md5` formato md5sum. Motivos: «capa sin md5 de plan: se rehace», «capa de otro plan: se rehace (capa xxxx…, plan de hoy yyyy…)», «capa con sidecar ilegible», «sin plan resuelto de hoy». Stdout y log gfx.

**A.3 — qué compara:** duración esperada = `seg_dur` del cap en `GUION_PANTALLA.json` (lo aprobado); sin guion para el cap, la misma cuenta sobre `gfx_escenas` (`_segmento_de_cap`, que con R8 ya incluye el negro). Tolerancia `1/fps`. Negro esperado = `black_hold.duration` del plan resuelto (sin pregunta → «sin negro que medir»). Al fin del archivo `blackdetect` da como `black_end` el pts del ÚLTIMO cuadro negro (1,0 s se reporta 0,967); por eso `d=` = negro − 2 cuadros (tolerancia + ese cuadro; el `d` por defecto 2,0 s no ve 1 s) y a la corrida que toca el fin se le suma su último cuadro. `pix_th` por defecto. ✗ no corta el render.

**Salida en texto (A.4), comando exacto `python fase2b.py f8s3-vajont-f30 --only-cap ch02 --reuse-visuals --gfx --gfx-sparse --gfx-quality looks --sw-encode`, 12:59:47 → 13:04:20, exit 0, `guard_render` pasó** (`lab/hyperframes/f38e/a/onlycap_ch02_gfx.log`):
- r1: `[gfx] ch02 reuse: capa sin md5 de plan: se rehace` · `pausa de cierre (plan fijo): 7.400s = pregunta 6.400 + negro 1.000` · `sidecar: ch02_gfx.plan.md5 = 27cf5298… (md5 del plan resuelto dibujado)` · `OK total 189.4s`. CC comprobó: `cat ch02_gfx.plan.md5` = `md5sum gfx_plan_ch02.resolved.json` = `27cf529861088a8625af9ab28d9162e4` (archivo intacto, mtime 03:04).
- Costuras (stdout): `✓ ch02_segment_only.mp4 — 140.6s` · `✓ costura ch02: segmento 140.600 s vs guion 140.600 s (±0.0333 s, un cuadro)` · `✓ costura ch02: negro de 1.00 s al cierre · blackdetect (d=0.9333) en los últimos 1.033 s: 139.600→140.600 (1.000 s)`.
- Segmento nuevo 140,600 s (4218 cuadros; v6 139,600/4188) = guion; `gfx_escenas_ch02.json` clip_dur 140,567 / pausa 7,4; `ch02_gfx.mp4` 140,600 s, mismo `blackdetect` ✓.
- **Gasto: US$ 0,0000** (plan congelado, sin director/crítico/visión; ninguna llamada a modelo).
- Escrito en `output/f8s3-vajont-f30/_fase2b_work/`: `_bak_f38e_a/{ch02_gfx.mp4, gfx_ch02.log}` (copia de v6, md5 `d5fc61b5…`), `ch02_gfx.mp4` (140,6 s), `ch02_gfx.plan.md5`, `ch02_segment_only.mp4`, `gfx_ch02.log`, `gfx_escenas_ch02.json`, `gfx_pause_ch02.json`, `gfx_sfx/sparse/cues_ch02`, `hoja_contactos_ch02.jpg`, `ch02_subs.ass`, `gfx_review_ch02.html`. Planes resueltos ×7, `GUION_PANTALLA.*`, `seg_0N` de v6 y los mp4 finales: intactos; `aprobacion.estado` vigente `35576ed6…` antes y después (CC lo comprobó: `(True, 'guion aprobado por Omar (2026-10-27), planes 35576ed6…')`).
- `data/cost_history.json` (ignorado por git) lo tocó el `cost_tracker` del pipeline al cerrar el video (US$ 0), como en toda corrida de `fase2b`; no es código de A, pero es una escritura en `data/` y se declara (abierto a6 y «lo que queda abierto» general).

Tests: `f38e_a` 13 verdes (r1: sidecar al dibujar, igual→reusa, cambiado→rehace, sin sidecar→rehace, motivos, `_segment_hash` ve el resolved; R8: `pausa_de_cierre`, `pausa_a_disco`, plan congelado alarga pregunta+negro y el negro termina con el clip, `closing_question` = plan fijo; A.3: lavfi con negro / sin negro / negro en el medio / duración distinta, líneas ✓✗); grupo `f38e_a f32 f33 gfx_layer_fallback fase2b_reassemble fase2b_only_cap::test_flags_en_cli f30b f34 f36` 68 verdes; rápida 58 (CC repitió `f38e_a + gfx_layer_fallback + f32 + f33 + fase2b_reassemble + rápida`: 101 passed). `test_constantes_con_origen`: sin constantes nuevas. Rojos ajenos: `f36c_pantalla` 3 (de C, en curso). Commit `96c2889` por rutas explícitas (9 archivos, con `verificar.sh`).

**Lo que queda abierto, A (entero, del subagente):**
- a1. Vajont v6 sigue sin el negro de cierre en los 7 caps (7 s más corto que el guion); no se re-renderiza (congelado). Un render nuevo daría ~1056,3 s y explica parte de r2 (D128 ~4 s antes = negros faltantes de ch01–ch05).
- a2. El sidecar compara contra el `resolved.json` de disco; sin guion aprobado (lab, `gfx_lab_server`) el plan «de hoy» se recalcularía al dibujar y podría diferir; con reuse y sidecar coincidente se reusa igual. En producción el hook exige aprobación.
- a3. `d=` de `blackdetect` no es «el por defecto» (2,0 s no ve 1 s): negro − 2 cuadros, derivado y explicado. Otra tolerancia es un número del analista.
- a4. El chequeo no mide el negro de un cap sin pregunta de cierre ni la costura de entrada (title card desde negro): solo duración + negro al cierre.
- a5. `_segmentos_en_paralelo` (GFX_PARALELO = 1) recibe el mismo chequeo; no probado en paralelo.
- a6. `data/cost_history.json` lo escribe el `cost_tracker` en toda corrida de `fase2b` (US$ 0 acá); regla «nada en data/» declarada.
- a7. `gfx_pause_<cap>.json` ahora lo escribe también el camino congelado; si el perfil cambia `black_hold_sec` después de aprobar, se dibuja el negro del plan aprobado (F34), no el nuevo.
- a8. `seg_0N` de v6 y `_bak_f38e_a/` (136 MB) no se borraron.
- a9. La primera corrida con `--reuse-visuals` tras este commit rehace las 7 capas de cualquier topic sin sidecars (~20 min en Vajont). Esperado.

## B — Colocación B1–B4 (`5008f4d`; B.5 más abajo)
Subagente B. Archivos: `script_engine/pantalla_colocar.py` (+89/−… : B1 `instantes`; B2 `hasta_el_corte` + bloque del reloj en `repartir`; B3 `en_orden` + `colocar_uno`; `import re`), `script_engine/gfx_realizador.py` (B4 `pregunta_cierre_fuente`; `pregunta_cierre` compatible, texto solo), `test_module_f38e_b.py` (11 tests: B1 ×3, B2 ×2, B3 ×3, B4 ×4, uno con los 7 caps de Vajont desde `lab/hyperframes/f38/b2/fase1/`), `test_module_f37b_colocar.py` (2 tests editados), `test_module_f29c_rotulista.py` (1 editado), `lab/hyperframes/f38e/b/` (`sim_b4_cierre.py`, `B4_simulacion.md`, `B_SALIDA.md`, `antes/`). CRLF ✓. No tocó `gfx_layer`, `fase2b`, `m01e`, `voz_utils`, `pantalla_filtros`, `gfx_guion`. `fase2b` no se corrió. Nada en `data/`.

- **B1:** `instantes` prueba todo inicio de escena con `s.t0 ≤ e.start ≤ s.t1`, antes o después del ancla, **en orden de tiempo** (elección declarada: es el orden de la escalera y coincide con la simulación del analista para D47). Escalera 1→2→3 intacta; `como` = «2 · inicio de la escena N». Propaga sola a filtros (`lectura`), reloj y sellos.
- **B2:** `hasta_el_corte` guarda en el reloj `duracion_plena` (la que trae) y `margen_corte` (1 cuadro, el que ya usaba). `repartir` prueba cada intento con `fin = min(t + duracion_plena, fin de la escena de t − margen)` contra `TICKER_MIN`, cambio de fecha y solape; el elegido queda con esa duración; fila «movido» con «dura X s (corta en Y s)» e `intentos`. Ningún número nuevo. Dato: en v6 el 9 OCT fallaba hasta en su instante original porque `hasta_el_corte` (antes del reparto, F37 C) ya lo había dejado en 1,88 s.
- **B3 — causa (archivo:línea):** no es bug de colocación. El crítico «¿estorba?» tiró los dos intentos de [17] con motivo (`output/…/_fase2b_work/gfx_ch05.log`: 115.5 s «ESTORBA — tapa parte del texto manuscrito de la carta…», 121.9 s «ESTORBA — cubre parte del texto manuscrito…», 128.2 s «NO ESTORBA»). Las fallas quedaron en la fila `rotulista.escena` del plan, pero el guion lee `movido_escena` (`gfx_guion.py:286`) y `pantalla_colocar.py:317` (antes) escribía ahí solo el destino, sin «· antes: …»; `b["critico"]` guardaba solo el veredicto ganador («pasó (no estorba)»); los `intentos_fallidos` de los filtros (2 de lectura) tampoco se sumaban. **Q51 queda en [18] por el crítico** (gusto de Omar → `--plan-edit`). Arreglo general: `colocar_uno` junta fallas de filtros + reparto, las ordena por instante (`en_orden`, sin repetidas) y las escribe en `movido_escena`, `b["intentos_fallidos"]` y la fila «movido» (`intentos` nunca vacío; si no hubiera, «sin falla registrada…»); también en la fila «fuera».
- **B4 — pregunta de cierre desde la voz**, regla exacta del handoff; palabras de contenido = `evidence._content` (las de `ya_dicho`), sin stopwords nuevas, sin umbral. Simulada sobre los 7 caps de Vajont (`sim_b4_cierre.py`):

| cap | ahora | fuente | car. | s |
|---|---|---|---|---|
| ch01 | Pero el dique no cedió esa noche. Lo que llegó a la cama de Micaela vino por encima de él. | voz-alineada | 90 | 6.0 |
| ch02 | En marzo de mil novecientos cincuenta y nueve, en otro embalse de la misma empresa, una montaña caminó primero. | voz-alineada | 111 | 7.4 |
| ch03 | El cuatro de noviembre, durante las pruebas, el agua tuvo su primera respuesta. | voz-alineada | 79 | 5.3 |
| ch04 | La presa cambió de dueño con el agua todavía subiendo. La montaña no se enteró del contrato. | voz-alineada | 92 | 6.1 |
| ch05 | A las diez y media de la noche, el párroco de Casso escuchó algo y abrió la ventana. | voz-alineada | 84 | 5.6 |
| ch06 | Tres días después llegó el presidente del Consejo. La gente ya sabía qué pedirle. | voz-alineada | 81 | 5.4 |
| ch07 | ¿Quién decidió que Micaela siguiera durmiendo? | voz-pregunta | 46 | 3.1 |

Igual a lo esperado por el analista en los 7 (ch07: 46 caracteres contados, él dijo 45). Posición sin cambio.
- Cambio mínimo en `gfx_layer.closing_question` (lo aplica CC después de A, en el commit de B.5): importar `pregunta_cierre_fuente`, `txt, fuente = …`, guardar `"fuente": fuente` y loguearla; `gfx_guion.py:315–319` ya pasa `q.get("fuente")` al guion.

Tests: `f38e_b` 11/11; grupo (`f38e_b + f37b_colocar + f29c + f29a + f32`) 38/38; rápida 58 (CC repitió todo junto: 96 passed). Editados a propósito: f37b `test_b1_q50_corta…` (con B1 Q50 entra en el inicio de la escena 7 a 19,5 s dentro de su oración, antes del ancla, en vez de saltar a la siguiente); f37b `test_c_el_reparto_ve_el_reloj_recortado_al_corte` (con B2 el reparto recorta el reloj por sí mismo); f29c `test_reloj_no_va_encima…` («termina donde terminaba» era lo que B2 reemplaza: ahora termina en el corte de su nueva escena, 18,0). «No editar»: `f34`, `f36` verdes; `f36c_pantalla` 3 rojos sobre `m01e_pantalla.validar` (los edita C en paralelo; verificado por B: con el `m01e_pantalla.py` de HEAD y sus módulos, 9/9). Commit `5008f4d` por rutas explícitas (10 archivos).

**Lo que queda abierto, B (entero, del subagente):**
- b1. `closing_question` sin el cambio mínimo → `fuente` vieja en el guion hasta que CC lo aplique tras A.
- b2. Fila #9 (ch01): el handoff dice «la posición no cambia»; el texto ahora es lo de [14]+[15] pero sigue en la pausa final, no anclado en [14]. Si el analista esperaba la ancla en [14], es posición (excluida).
- b3. Caso límite: `repartir` sin `hasta_el_corte` antes usa margen 0; el segundo `hasta_el_corte` puede dejar TICKER_MIN − 1 cuadro si queda justo TICKER_MIN. En gfx_layer (`hasta_el_corte` antes) no pasa.
- b4. Las fallas del crítico en intentos previos viajan como texto (`movido_escena`/`intentos`), no como filas de `critico_rotulista`.
- b5. B.5 (`--plan-only`) pendiente del aviso de CC. Esperado: #2 D47 a 79,6–84,3; #5 9 OCT en 89,43 con 12 s; #6 Q51 sigue en [18] con 4 fallas declaradas; #8 ch07 «¿Quién decidió que Micaela siguiera durmiendo?»; #9 ch01 texto nuevo, misma posición. Resto igual salvo filas «movido» con «antes: …» y una llamada nueva al crítico (D47 en 79,6; centavos).
- b6. Los 3 rojos de f36c son de C; re-mirar cuando C termine. → Con C commiteada, `f36c_pantalla` 9/9 (CC lo corrió con C y C2: 32 y 113 passed).

### B.5 — `--plan-only` de Vajont con el papel congelado de F38d (`8f7d9cd`)
Subagente B, después del render de A y con el cambio mínimo de `closing_question` ya en el árbol (CC lo aplicó: importa `pregunta_cierre_fuente`, guarda `"fuente"` en `chapter_question` y la loguea; A+B tests 44 verdes). Candados antes de correr: papel `data/scripts/_steps/f8s3-vajont/01e_pantalla.json` md5 `fec9198ab80b05d89afc5871735c5267` = `lab/hyperframes/f38/b4/01e_pantalla.json` ✓; `output/f8s3-vajont-f30/GUION_PANTALLA.md` `0af5b1dc…` = `b/antes/` ✓.

Comando: `PYTHONIOENCODING=utf-8 python fase2b.py f8s3-vajont-f30 --gfx --plan-only > lab/hyperframes/f38e/b/plan_only.log 2>&1` · 13:10:06 → 13:13:25 · «--plan-only 196s · costos {'gemini_usd': 0.0004}» · exit 0. **US$ 0,0004**: 4 llamadas de Gemini Vision del crítico «¿estorba?» en instantes nuevos de B1/B2 sin caché (`estorba_ficha_0080.57` D47 en la escena 8 de ch02; `estorba_sello_0057.17` ×2 CALMA en la escena 6, dos lados; `estorba_ficha_0114.27` Q51 en la escena 12); el resto, caché. Foto de `data/` (1320 mtimes, `b/_data_antes_full.txt` / `_despues_full.txt`): una línea, `data/cost_history.json` 13:04:20 → 13:13:25 (+1887 B, el registro del cost_tracker de `f8s3-vajont-f30` con esas 4 entradas); papel intacto. Salidas: `b/despues/GUION_PANTALLA.json` + `.md` (md5 del .md `492d4851…` = `output/`, comprobado por CC), `plan_only.log`, `diff_guion.py` + `diff_guion.txt`.

Tabla contra la revisión F38d §2:

| # | hoy (antes) | ahora (después) | esperado | |
|---|---|---|---|---|
| 2 ch02 D47 | 03:11.2 · cap 86,6 · sobre [12] (Semenza) · escena 9 | **03:04.5 · cap 79,57–84,27 · sobre [11] (Müller) · escena 8 · 4,7 s** · movido «84.70 → 79.57 s (2 · inicio de la escena 8): 1 · palabra ancla (84.70): sin tiempo de lectura… · 1 · inicio de la oración (79.50): sin tiempo de lectura…» · crítico no estorba | 03:04.2, escena 8, cap 79,6, dentro de [11], termina 84,3 | ✓ (mm:ss del mp4 corre +0,3 por B4 en ch01; en cap 79,57 ≈ 79,6) |
| 5 ch05 9 OCT | ✂ 09:57.0 · cap 87,52 · «quedaría menos de 2 s» ×2 | **10:00.2 · cap 89,433 · «9 OCT · 1963» · 12,0 s · escena 10 (89,4–109,6)** · fila «87.52 → 89.43 s (2 · inicio de la escena 10), dura 12.00 s · antes: 1 · palabra ancla (87.52 s): quedaría menos de 2.0 s (corta en 89.40 s)» | 09:58.9, inicio de la escena 10, duración normal | ✓ (mm:ss corre +1,333 por B4; en cap 89,43) |
| 6 ch05 Q51 | 10:37.7 · [18] · movido sin fallas | **10:39.0 · [18], igual**, movido con sus 5 fallas: inicio de la oración 113,24 (sin lectura) · **2 · inicio de la escena 12 (113.27): estorba — tapa parte del texto manuscrito de la carta** · ancla 115,46: estorba (tapa la carta) · peso 121,86: estorba (cubre la carta) · oración siguiente 128,16 (sin lectura) | Q51 en [17] (cap 115,46) | ✗ a propósito: no es bug de colocación; el crítico tira los 3 instantes de [17] por tapar la carta manuscrita (escena 12), ahora declarado. Si Omar la quiere en [17]: `--plan-edit` (gusto) |
| 8 ch07 pregunta | 17:22.4 · «La sentencia dice…» 190 car. 12,9 s · escaleta | **17:23.7 · «¿Quién decidió que Micaela siguiera durmiendo?» · 46 car. · 3,1 s · fuente voz-pregunta** · misma ancla | mismo texto, 45 car., 3,0 s | ✓ (46/3,1 contados por el código) |
| 9 ch01 pregunta | 01:37.9 · «El dique no cedió…» 5,7 s · escaleta | **01:37.9 · «Pero el dique no cedió esa noche. Lo que llegó a la cama de Micaela vino por encima de él.» · 90 car. · 6,0 s · voz-alineada** · misma posición (pausa final) | texto de [14]+[15]; «ancla en el inicio de [14]» | ✓ texto · posición sin cambio por el handoff («la posición no cambia», F32); si el analista quería la ancla en [14], es otro pedido (b2) |

**Todo lo demás que cambió (diff por evento, `b/diff_guion.txt`):**
1. Pregunta de cierre en los 7 caps: `fuente` escaleta → `voz-alineada` (ch01–ch06) / `voz-pregunta` (ch07). Texto cambiado solo en ch01, ch02 («En marzo de mil novecientos cincuenta y nueve…», 111 car., 7,4 s) y ch07; ch03–ch06 el mismo texto. = la tabla simulada de B4.
2. Duraciones (B4, lectura 15 cps; **no R8**): `seg_dur` ch01 +0,333, ch02 +1,0, ch07 −9,8; ch03–ch06 iguales; `duracion_s` 1056,267 → 1047,8. Por eso los `offset` corren (ch02 +0,333; ch03–ch07 +1,333) y con ellos todos los `t_mp4`/mm:ss, `inicio_voz` esperado/medido (6/7 ✓ como antes; ch07 ✗ previo F32), «inicio de música» 7/7 ✓ desvío 0, y la mezcla. R8 de A no tocó `seg_dur`: el guion ya contaba el negro; R8 arregló el mp4.
3. Costuras: ✓ 6/6, negro 1 s al cierre en los instantes nuevos (ch01 100,93–101,93; ch02 140,57–141,57; ch07 186,07–187,07), voz callada −120 dB, el entrante sube desde negro.
4. Tarjeta fecha-hora: sin cambio, `✓ 00:00.0 «9 OCT 1963 · 22:39» · pasó` (se borra en D).
5. ch05 transición de la escena 10 (89,433): `cut` → `dissolve 20 cuadros (salto de tiempo)`: regla existente de `gfx_style` (reloj que arranca en un corte); efecto de B2. El pico de ch05 (escena 2, zoom_punch) intacto.
6. ch05 chequeo «relojes del papel (informativo)»: línea nueva «ch05 el papel no trae reloj · reloj de la voz «9 OCT 1963» → difiere (anotado)».
7. ch02 CALMA sigue sin colocar; su motivo suma los 2 intentos nuevos de B1 (escena 6 a 56,17, dos lados: estorba).
8. `aprobado` {Omar, md5_planes 35576ed6…} → `None`: los planes cambiaron, la aprobación de F38d cae (lo que pide la compuerta; nadie aprobó nada).
9. `costos` → {'gemini_usd': 0.0004}.
10. .md: 357 líneas distintas, 271 → 272 (la fila del reloj colocado reemplaza la ✂); casi todas por los mm:ss corridos y `escena_t1` de la última escena de ch01/ch02/ch07.
Nada más: fichas, sellos, relojes ch01/ch04/ch07, recorte, punches, title cards, `a_pantalla` 4/5 y los chequeos de cifra/lectura/dos bloques/cruza corte, iguales.

**Abierto nuevo de B.5 (entero):**
- b7. #6 Q51 queda en [18] por el crítico (ahora con 3 «estorba» declarados, incluido el intento nuevo 113,27 de B1); decide Omar en la compuerta.
- b8. `aprobado: None`: cualquier render nuevo necesita `--aprobar-guion` de Omar (fuera de esta tanda); el render de ch02 de A fue antes de esta corrida.
- b9. ch05 escena 10 pasa a dissolve «salto de tiempo» por el reloj nuevo (regla previa de `gfx_style`); que el analista lo vea.
- b10. Los mm:ss del mp4 desde ch02 corren +0,333/+1,333 s por las preguntas más largas de ch01 y ch02: la revisión hay que leerla en tiempo de cap.

## C — Papel m01e-6 con `respaldo` y `autor` (`2965603`) + C2 (`58fc5d7`)
Subagente C. Archivos: `script_engine/m01e_pantalla.py` (99 líneas de diff; CRLF ✓, comprobado por CC), tests actualizados `test_module_f36c_pantalla.py`, `f37a_papel`, `f38a_m01e`, `f38c_papel`, `f38d_vueltas` (ninguno borrado), nuevo `test_module_f38e_c.py` (11), `lab/hyperframes/f38e/c/` (`C_SALIDA.md`, `TABLA.md`, `c0_foto_data.py`, `c1_prompt_del_md.py`, `c_corrida.py`, `c_corrida.log`, `c_corrida.stdout`, `01e_pantalla.json/.md/.raw.json`, `data_foto_antes/despues.json`). `vajont_steps/f8s3-vajont/` (copia entera de `data/scripts/_steps/f8s3-vajont/`, 121 archivos, 21 MB, con `fuentes/` y `_r3_cache`) **no entró al commit**: sus 4 entradas (`00_pool_v3`, `01a_escaleta`, `01a_skeleton`, `01b_narracion_v3`) son byte a byte las de `lab/hyperframes/f38/b2/fase1/` (md5 comprobados por CC) y el papel nuevo está copiado en `c/`. No tocó `pantalla_filtros.py` (el candado del papel se alimenta desde `_validar_ficha`) ni `voz_datos.py`.

**md5 del SYSTEM (C.1), por código:** `c1_prompt_del_md.py` extrae el bloque del md (md5 del md `240e3e7b…`) con el mismo corte que `prueba1_rotulos.system_del_md`, lo escribe en bytes dentro del string triple (cada `\n` → `\r\n`; resto intacto) y verifica importando: `bloque del md: 3098 caracteres · md5 7d2ccdd28055d6e621d1d251a0fe8bb7 · OK` · `md5(m01e_pantalla.PANTALLA_SYSTEM) = 7d2ccdd28055d6e621d1d251a0fe8bb7 · OK` · `PANTALLA_SYSTEM == bloque del md: True`. CC lo repitió antes del commit: los dos md5 iguales, `==` True, `PROMPT_VERSION = "m01e-6"`, `prompt_md5()` = `3b98aef1d8595124967ac7a85b75bab7`.

**Qué hace el código (C.2–C.5):** formatos con `"respaldo": "…", "autor": "…" | null` después de `"texto"` en `FORMATO_SALIDA` y `FORMATO_REINTENTO`. `respaldo` (en `_validar_ficha`, tras anclaje y formato): `ev.norm(respaldo) in ev.norm(x["texto"])`; falta o no subcadena → cae con regla `respaldo`, entra a `motivos`/`motivos_beat` como ficha caída, la vuelta lo puede arreglar. Candado: para lo que no es cita, `candado` recibe el ítem con `texto` = respaldo (cifras/nombres/años de etiqueta y dato contra el respaldo; la etiqueta además contra `fuente`; la excepción de la ancla sigue dentro de `candado`); la cita sigue contra el texto entero (frase literal recortada). Autor: `autor_mostrado(autor_modelo, x)` → el del modelo si cada nombre de `_nombres_del_autor` está en `autor`/`rol`/`texto` del ítem; si no, el del archivo sin cortar; la ficha guarda `autor` (mostrado) y `autor_origen` («modelo» / «archivo: <motivo>»); `caracteres` y el motivo de `caben` usan el mostrado; `a_markdown` muestra «— X (autor: modelo)» y el respaldo. Vueltas/`fusionar` sin cambios; `cortados_al_cierre` y `prompt_md5` incluyen lo nuevo.

**Peor caso estimado antes de llamar** (lógica de `llamar`, USER real 137 035 car., body 150 460): intento 1 US$ 0,2804 (OUT_TOKENS_PEOR 16 000) / 0,3266 (salida 20 623, e4); una vuelta 0,2960 / 0,3422. Tope `TOPE_USD_RESPALDO` 1,00 (`tope_usd()` → «respaldo (el perfil no trae costos.m01e_tope_usd)»). Número nuevo: ninguno.

**Gasto real, UNA corrida, 4 llamadas, 194 s** (`cost_of` por llamada; ledger en memoria; nada al cost_tracker):

| llamada | in | out | US$ | s |
|---|---|---|---|---|
| intento 1 | 66 450 | 20 318 | 0,3361 | 139,8 |
| vuelta 1 | 71 417 | 2 433 | 0,1672 | 20,8 |
| vuelta 2 | 70 936 | 421 | 0,1461 | 8,3 |
| vuelta 3 | 71 053 | 1 814 | 0,1603 | 20,6 |
| **total** | | | **0,8096** | |

Cerró por **tope** («gastado 0.8096 + esta llamada hasta 0.3308 → sin reintento»).

**Foto de `data/`** (mtime + md5, 1320 archivos): dentro de `c_corrida.py` (antes de importar → al salir): cambiados/nuevos ninguno; `cost_history.json` `1f5e5ded…` → `1f5e5ded…`. En la foto de toda la parte (12:56 → 13:06): 1 cambiado, `data/cost_history.json` (`1f5e5ded…` → `237879aa…`, mtime 13:04:20, +139 bytes: `{"video_id": "f8s3-vajont-f30", "created_at": "2026-10-27T12:59:47", "entries": [], "total_cost": 0.0}`) = el `fase2b --only-cap ch02 --gfx` de la parte A (12:59:47 → 13:04:20), no de C (ver a6).

**Salida en texto (C.5): `lab/hyperframes/f38e/c/TABLA.md`, tal cual.** SYSTEM md5 `7d2ccdd2…` · prompt_md5 `3b98aef1…` · claude-sonnet-5-5 (medium) · 4 llamadas = intento 1 + 3 vueltas · cerró por tope · US$ 0,8096.

| cap·beat | v6 hoy (etiqueta · dato · autor) | prueba 1 | NUEVO m01e-6 con vueltas (etiqueta · dato · autor) | respaldo ✓/✗ | cifras | nombres | validar | car./caben | ¿se entiende solo? | autor mostrado | de dónde salió |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ch01·1 | D84: PRESIÓN DE LA OLA DE AIRE · dos bombas de Hiroshima | D195: LOS QUE VIVÍAN EN LONGARONE · Murieron 1.269 de 1.328 | D195: EL PUEBLO DE MICAELA · 1.269 de 1.328 habitantes murieron | ✓ · respaldo: «con 1.269 de 1.328 habitantes fallecidos» | 1.269 literal; 1.328 literal | — | queda | 54/90 |  | — | — |
| ch02·2 | D117: ACTA DEL CONSEJO SUPERIOR · solo 13 de 34 representantes presentes | D240: SESIÓN DE APROBACIÓN · Asistieron solo 13 de los 34 representantes | D117: SESIÓN QUE LA APROBÓ · Solo 13 de 34 representantes presentes | ✓ · respaldo: «con solo 13 de 34 representantes presentes» | 13 literal; 34 literal | — | queda | 58/90 |  | — | — |
| ch02·3 | D47: FRENTE DEL DESMORONAMIENTO · 2 km de frente y 600 m de desarrollo vertical | D47: TAMAÑO DEL DESMORONAMIENTO · 2 km de frente y 600 m de desarrollo vertical | D47: ALTURA DEL DESMORONAMIENTO · 600 m de desarrollo vertical | ✓ · respaldo: «600 m de desarrollo vertical» | 600 literal | — | queda (juzgado por el autor: {"spoiler": ["2"]}) | 54/83 |  | — | — |
| ch03·4 | T15: VOLUMEN DE LA ROCA · 3 millones de metros cúbicos | T16: EL TRABAJADOR MUERTO · Arcangelo Tiziani | T16: LA VÍCTIMA DE LA OLA · Arcangelo Tiziani | ✓ · respaldo: «mata a Arcangelo Tiziani» | — | Tiziani ✓ | queda | 37/83 |  | — | — |
| ch03·5 | D49: ANCHO DE LA FISURA · Más de 1 metro | D49: ANCHO DE LA FISURA · Más de 1 metro | D49: ANCHO DE LA FISURA · Más de 1 metro | ✓ · respaldo: «una fisura de más de 1 metro de ancho» | 1 literal | — | queda | 32/90 |  | — | — |
| ch04·6 | T39: ROCA QUE AMENAZABA ERTO · 50 millones de metros cúbicos | — | T39: LA ADVERTENCIA DE MERLIN · 50 millones de metros cúbicos de roca | ✓ · respaldo: «un derrumbamiento de 50 millones de metros cúbicos de roca que amenaza Erto» | 50 literal | — | queda (juzgado por el autor: {"spoiler": ["50"]}) | 61/90 |  | — | — |
| ch04·7 | T50: COTA ALCANZADA · 720 metros | D106: SOBRE LA COTA SEGURA · 15 metros de más | D106: SOBRE LA COTA SEGURA · 15 metros | ✓ · respaldo: «15 metros por encima de la cota de seguridad recomendada» | 15 literal | — | queda (juzgado por el autor: {"contradice": ["715"]}) | 29/36 |  | — | — |
| ch05·8 | Q50: DOCUMENTO OFICIAL · en continua aprensión · Administración del comune di Erto e Casso | Q50: LO QUE DECÍAN · «en continua aprensión y en continua alarma» — Municipio de Erto y Casso | Q50: MIEDO POR ESCRITO · «continua aprensión y en continua alarma» · autor del modelo: «Municipio de Erto y Casso» | ✓ · respaldo: «están viviendo en continua aprensión y en continua alarma» · cita literal ✓ | — | — | queda | 86/90 |  | Municipio de Erto y Casso | modelo |
| ch05·9 | Q51: ÚLTIMA LÍNEA DE LA POSDATA · Que Dios nos ayude · Alberico Biadene | Q51: LA ÚLTIMA LÍNEA · «Que Dios nos ayude» — Alberico Biadene | Q51: CIERRE DE LA POSDATA · Que Dios nos ayude. · autor del modelo: «Alberico Biadene» | ✓ · respaldo: «Que Dios nos ayude.» · cita literal ✓ | — | Dios ✓ | queda | 60/90 |  | Alberico Biadene | modelo |
| ch06·10 | D86: ALTURA DEL MURO DE AGUA · 70 metros | D86: EL MURO DE AGUA EN LONGARONE · 70 metros de altura | D01: LA ROCA QUE CAYÓ · 270 millones de metros cúbicos | ✓ · respaldo: «270 millones de metros cúbicos de roca» | 270 literal | — | queda | 46/90 |  | — | — |
| ch06·11 | D128: RECUENTO OFICIAL · 1.910 personas | D128: TOTAL DE MUERTOS · 1.910 personas | D128: VÍCTIMAS · 1.910 personas murieron | ✓ · respaldo: «En el desastre murieron 1.910 personas.» | 1.910 literal | — | queda | 31/57 |  | — | — |
| ch07·12 | Q14: RESPUESTA · Y justicia tendréis · Giovanni Leone | Q14: LA RESPUESTA · «Y justicia tendréis» — Giovanni Leone, presidente del Consejo | Q14: LA RESPUESTA · Y justicia tendréis · autor del modelo: «Giovanni Leone» | ✓ · respaldo: «Y justicia tendréis» · cita literal ✓ | — | — | queda | 50/90 |  | Giovanni Leone | modelo |
| ch07·13 | D245: CONDENA A MONTEDISON · 55.645.758.500 liras | D245: CONDENA A MONTEDISON, 1997 · 55.645.758.500 liras | D32: ACUSADOS QUE FALTARON · Otros dos ya habían muerto | ✓ · respaldo: «dos habían muerto» | 2 literal | — | queda | 47/90 |  | — | — |

**Las 3 citas:** Q50 **entra** en ch05 b8 [2] «MIEDO POR ESCRITO · continua aprensión y en continua alarma» — Municipio de Erto y Casso (modelo) · 86/90 · Q51 **entra** en ch05 b9 [17] «CIERRE DE LA POSDATA · Que Dios nos ayude.» — Alberico Biadene (modelo) · 60/90 · Q14 **entra** en ch07 b12 [1] «LA RESPUESTA · Y justicia tendréis» — Giovanni Leone (modelo; el modelo devolvió «Giovanni Leone», pasa) · 50/90.

**Vueltas:** vuelta 1 (beats ch02 b3, ch04 b6, ch04 b7, ch05 b8, ch07 b13; 7 motivos: Q50 cita_sin_fecha en [7], preguntas D47 «2» / T39 «50» / D106 «715», pico ch05 b8 vacío, a_pantalla Q50 en b8 y D245 en b13; 2 aplicados) · vuelta 2 (ch05 b8, ch07 b13; 3 motivos: pregunta T54 «Erto», a_pantalla Q50 y D245; 2 aplicados) · vuelta 3 (ch05 b8, ch07 b13; 5 motivos: Q50 caben 112 > 77, D32 caben 72 > 36, pico b8 vacío, a_pantalla Q50 y D245; 2 aplicados) · tras la vuelta 3: fichas fuera 0 · preguntas 0 · picos vacíos 0, quedaba solo el motivo a_pantalla D245 (ch07 b13, que el autor descarta: «Montedison no se nombra en la voz…») → la vuelta 4 no entró en el tope → cierre **tope**. `cortados_al_cierre`: nada. «Lo que cayó» en la validación final: nada. Preguntas y respuestas: D47 {spoiler [2]} mantenida (otro hecho); T39 {spoiler [50]} mantenida; D106 {contradice [715]} mantenida; T54 {no_dicho [Erto]} la sacó.

**Sellos y relojes:** sellos v6 9 · respuesta 9 · quedan 9; relojes 4 · 4 · 4 sin error; fichas 13 · 13 · 13. Relojes NUEVO = v6 (ch01[13] 9 OCT 1963, ch04[0] 4 NOV 1960, ch07[11] 20 FEB 1968, ch07[14] 29 NOV 1968). Sellos NUEVO: ch01·1 PÁNICO, ch02·2 CALMA, ch02·3 AMENAZA, ch03·4 AVISO, ch03·5 INMINENTE, ch05·8 SILENCIO, ch06·10 COLAPSO, ch07·12 RABIA, ch07·13 MEMORIA. **Picos:** los 7 con ficha (D195, D47, T16, D106, Q50, D01, Q14). **a_pantalla:** D117 (b2) presente, D128 (b11) presente, D192 (b11) ausente, D245 (b13) ausente, Q50 (b8) presente; `a_pantalla_vacios`: ch07 b13 (D245). Tarjeta: 9 OCT 1963 · 22:39 (de la voz; la borra D).

Tests: `f38e_c + f36c_pantalla + f37a_papel + f38a_m01e + f38c_papel + f38d_vueltas + test_constantes_con_origen` → 55 passed (11 nuevos); rápida 58 (CC repitió todo junto: 113 passed). Cambios en tests y por qué: (1) f36c/f37a/f38a/f38c/f38d: las respuestas congeladas (F37/F38b/F38c) y las fichas de mano no traen `respaldo` y ahora caerían por `respaldo`; se completa con `_con_respaldo(resp, ent)` = el texto entero del ítem (fragmento literal trivial → el candado es el de antes y cada test sigue midiendo lo suyo); (2) `PROMPT_VERSION == "m01e-5"` → `"m01e-6"` (f37a, f38a ×2, f38d); (3) `f38c::test_prompt_no_cambia`: md5 `76f1de7a…` → `3b98aef1…`; (4) `f38d::test_5` medía que m01e-5 difería de m01e-4 en una línea; con el SYSTEM reemplazado entero no se puede medir: ahora comprueba que m01e-6 conserva la oración de «caben» con el autor y los 5 de comillas y raya y que el md5 no es el de m01e-4. Ningún test borrado. Commit `2965603` por rutas explícitas (19 archivos).

**C2 (`58fc5d7`, CC):** cierra el abierto c2 (el autor mostrado no llegaba a Fase 2, que leía `it["autor"]` del pool): `pantalla_entrada.preparar_cap` pone el `autor` de la ficha del papel en el ítem del cap, y de ahí lo leen `pantalla_filtros.caracteres`, `pantalla_colocar` (texto «dato» — autor) y el guion; sin autor en el papel, el del pool como antes. Es la «C.4 se muestra» del handoff y «campo autor en citas» de DECISIONES 12:32; una sola línea de código, general. 2 tests sintéticos (`test_module_f38e_c2.py`); `f36c + f38e_c + f37b` 32 passed; rápida 58. CRLF ✓.

**Lo que queda abierto, C (entero, del subagente):**
- c1. **«Pietro Leone» y la letra del handoff.** §C.4 dice «cada nombre propio que **no** abre la frase» con `voz_utils.nombres`; con eso solo «Pietro Leone» pasa (Pietro abre, Leone está en el archivo) y el caso de test obligatorio («no pasa») no se cumple. Se agregó una lectura: el que abre también cuenta cuando va seguido de otro nombre propio (nombre y apellido); seguido de una palabra común («Municipio de…», «Presidente del…») no cuenta. Sin número ni lista; la decide el analista. Consecuencias medidas: «Giovanni Leone, presidente del Consejo» no pasa (Consejo ≠ Consiglio) → se muestra el del archivo; un autor de una palabra («Montedison») pasa sin verificar.
- c2. ~~El autor mostrado no llega a Fase 2~~ → cerrado en C2 (`58fc5d7`); queda la observación de riesgo original: antes Fase 2 dibujaba «Administración del comune di Erto e Casso» (41 car.) donde el papel midió 86/90 con «Municipio de Erto y Casso».
- c3. **Cierre por tope con un motivo que no se va**: el `a_pantalla` D245 de ch07 b13 (el autor lo descarta cada vuelta) mantuvo vivas las vueltas; como los motivos cambiaban en otros beats, «sin progreso» no disparó, y la vuelta 4 chocó con el tope (0,81 + 0,33 > 1,00). Es F38d tal cual (no se tocó `llamar`); las 3 vueltas costaron US$ 0,47 además del intento 1.
- c4. **Respaldo en una persona (P)**: con el respaldo como fuente del candado, en `persona` el cargo de la etiqueta (por raíz) también se mira contra el respaldo (el handoff nombra cifras, nombres y años). Ninguna P entró; no medido.
- c5. **Ninguna ficha cayó por `respaldo` ni por candado** en 4 llamadas; todas las cifras «literal» (ningún redondeo: e3 de F38e-0 sigue sin medir).
- c6. **Cambios respecto de la prueba 1 además de las citas**: ch06·10 D01 «270 millones de m³» (antes D86 70 m); ch07·13 D32 «Otros dos ya habían muerto» (antes D245); ch02·2 volvió a D117 (el a_pantalla); ch02·3 D47 recortada a «600 m» (sacó el «2 km» preguntado, aunque figura «juzgado: otro hecho» porque mantuvo el ítem); ch04·6 T39 entró. «¿Se entiende solo?» vacía (Omar/analista).
- c7. **Q14**: el modelo devolvió «Giovanni Leone» (pasa, «modelo»). Q50 en la vuelta 1 cayó por `cita_sin_fecha` en [7] y en la vuelta 3 quedó en [2] con 86/90.
- c8. **`data/cost_history.json` cambió a las 13:04:20** (entrada `f8s3-vajont-f30` vacía): no es de C (es el render de A, a6); `logs/` sumó logs de `error_handler` de otros procesos.
- c9. **`editar` (`--plan-edit`)** no pide `respaldo`: una ficha editada a mano no lo lleva. No se tocó.
- c10. **`vajont_steps/` pesa 21 MB** (incluye `fuentes/`, `_r3_cache`): el handoff pidió la carpeta entera; no entra al commit (sus entradas = `f38/b2/fase1`, el papel nuevo está en `c/`).
- c11. Desvío declarado: `llamar` cerró en 4 llamadas con el tope 1,00 (DECISIONES 02:36 hablaba de «como mucho 3 vueltas, ~US$ 0,81»: dio exactamente eso, 3 vueltas, 0,8096).

## D — Borrar la tarjeta fecha-hora del segundo 0 (`68e6c41`, con el mapa regenerado)
Subagente D, después de A, B, C y E (toca archivos de A y de C). Archivos (CRLF ✓, comprobado por CC): `script_engine/voz_datos.py` (−173: `tarjeta_inicial`, `tarjeta_de_voz`, `horas_dichas`, `_numero_de`, `_hora_item`, las constantes de horas, `from datetime import date`, docstring y encabezado; `_entero` queda, lo usa `fechas_completas`), `script_engine/m01e_pantalla.py` (`tarjeta()`, claves `tarjeta`/`tarjeta_motivo` de `armar`, línea «Tarjeta» y conteo de `a_markdown`, log de `generar`, clave `_escaleta` de `entrada`, rama de `editar` + 3 docstrings; `editar` ahora **rechaza** una edición sin `ficha` ni `sello` con `ValueError` genérico, sin rama muerta), `script_engine/pantalla_entrada.py` (`rot["tarjeta"]` ×2 + 2 docstrings), `script_engine/gfx_layer.py` (bloque `resolved["tarjeta_inicial"]` + log, docstring, comentario), `script_engine/gfx_guion.py` (intro fija «primer cuadro congelado, sin voz», evento y chequeo 11 fuera, «12–14» → «11–13»), `script_engine/gfx_project.py` (solo docstring de `archive_head_px`: «tarjeta» del recorte → «recorte», para que el grep quede en cero), `fase2b.py` (−85: `_intro_de`, `_ff_ruta`, `_filtro_tarjeta`, `_pad_tarjeta`, parámetro `tarjeta` y ramas en `_mix_music_into_video` —`v_pad` vuelve a `tpad … start_mode=clone`— y `_mix_music_audio_only`; `_mezcla_preview` y `main` usan `INITIAL_SILENCE_SEC` directo; ayuda de `--plan-edit`; 3 comentarios). Tests editados: `test_module_f34.py`, `f36.py`, `f36c_pantalla.py`, `f38a_m01e.py`, `f38a_voz.py`, `f38e_c2.py`. Nuevo: `test_module_f38e_d.py` (4). Borrado el `.pyc` huérfano `script_engine/__pycache__/gfx_rotulista.cpython-311.pyc` (módulo inexistente desde F37). `lab/hyperframes/f38e/d/` (`D_SALIDA.md`, `grep_antes/despues.txt`, `plan_only.log`, `despues/`, `diff_guion.py` + `.txt`). `data/` no tocado.

**Tests borrados por nombre (9) y por qué:** `f34::test_a6_tarjeta_vajont_y_falta_si_no_hay_certeza` (probaba `tarjeta_inicial`); `f36::test_b9_la_tarjeta_reemplaza_la_intro` (`_intro_de`, `_pad_tarjeta`, `_tarjeta.txt`) → reemplazado por `test_b9_la_intro_de_la_musica_es_initial_silence` (conserva la parte que no era tarjeta: `adelay=2500|2500` = `INITIAL_SILENCE_SEC`); `f38a_m01e::test_a2_la_tarjeta_sale_de_voz_datos_y_no_del_autor`, `::test_a2_vajont_tarjeta_real`; en `test_a1_formatos_literales` se quita el assert «TARJETA no está en el prompt» (lo cubre el grep-test nuevo); `f38a_voz::test_a2_horas_dichas_en_letras_y_digitos`, `::test_a2_vajont_9_oct_1963_22_39_de_t66`, `::test_a2_sin_fecha_en_el_gancho_falta`, `::test_a2_voz_sin_hora_solo_fecha`, `::test_a2_sin_pool_ni_vajont_la_hora_sale_del_item_que_coincide` (`horas_dichas` solo servía a la tarjeta → se va con sus tests); `f36c_pantalla`: `_esquema` sin la clave; `test_a` y `test_h` sin la parte de la tarjeta.

**Greps (salida en texto):** antes (`grep_antes.txt`, 88 líneas): fase2b 25, m01e 23, voz_datos 22, gfx_guion 6, gfx_layer 6, pantalla_entrada 4, gfx_project 2 (docstring del recorte), 5 `.pyc`, 3 de zod en `node_modules` (ajeno); tests: f34, f36, f36c_pantalla, f38a_m01e, f38a_voz, f38e_c2. Después: `grep -rn tarjeta script_engine/ fase2b.py` → **vacío** (CC lo repitió: 0 líneas en `.py`); `grep -rln tarjeta test_module_*.py` → `f38a_m01e.py` y `f38a_voz.py` solo por el nombre de archivo `HANDOFF_F38_reintento_tarjeta_juez` en el docstring, y `f38e_d.py` (el que busca la palabra).

**`--plan-only` de Vajont rehecho sin tarjeta** (13:28:18 → 13:31:20, 168 s, exit 0): **US$ 0,0000** (`costos {}`; todo caché, 0 llamadas al crítico). Foto de `data/`: 1320 archivos antes y después; diff = solo `data/cost_history.json` (ledger, entrada vacía). Cuadro de la intro del guion nuevo: «Duración del mp4: 17:27.3 (1047.3 s; intro 2.5 s, title card 3.0 s)» · `00:02.5 · ch01 · beat 1 (gancho) · costura · «intro 2.5 s (primer cuadro congelado, sin voz) → title card 3.0 s desde 0.0 s → voz a 0.12 s del cap (+2.62 s del mp4)»` · `intro_s` 2.5 = `INITIAL_SILENCE_SEC`. Chequeos (13, antes 14): ✓ dos bloques · ✓ cruza corte · ✓ texto sin lectura · ✓ pregunta sin lectura · ✓ cifra contradice · ✗ a_pantalla · ✓ costuras · ✗ inicio de voz (ch07, previo) · ✓ gancho no vacío · ✓ inicio de música · ✗ papel sin colocar (CALMA, previo) · ✓ papel sin alinear · ✓ relojes del papel. Los 3 ✗ son los mismos de B.5; «tarjeta fecha-hora» desapareció. Diff por evento contra B.5 (`d/diff_guion.txt`): QUITADO `tarjeta fecha-hora «9 OCT 1963 · 22:39» @ −3.0`; costura de ch01 «intro 3.0 s (tarjeta … sobre negro)» → «intro 2.5 s (primer cuadro congelado, sin voz)»; chequeo «tarjeta fecha-hora» → null. **Intro 3,0 → 2,5 s: todo el mp4 se corre −0,5 s** (offsets de los 7 caps: ch01 3.0→2.5, ch02 104.933→104.433, ch03 246.533→246.033, ch04 381.833→381.333, ch05 510.8→510.3, ch06 686.5→686.0, ch07 860.7→860.2; inicios de voz y de música −0,5; duración 1047,8 → 1047,3 s; música con desvío 0 cuadros en los 7). Ningún otro evento quitado, nuevo ni cambiado; `seg_dur` iguales.

Tests: nuevo + 6 tocados: 42 verdes; lista pedida (f38e_a/b/c/c2/d, f36c_pantalla, f34, f36, f32, f38a_m01e, f38a_voz, f37a_papel, f38c_papel, f38d_vueltas, gfx_layer_fallback, fase2b_reassemble): 124 verdes; rápida 58. `py_compile` + `pyflakes` limpios (único aviso previo: `total_cost` sin usar en fase2b). CC repitió f38e_a/b/c/c2/d + f36c + f34 + f36 + f38a_m01e + f38a_voz + rápida: 136 passed. `test_module_f38e_d.py`: (1) grep-test sobre `script_engine/*.py` + `fase2b.py`; (2) `gfx_guion.armar` con ch01 sintético y la clave vieja `tarjeta_inicial` puesta a propósito: sin evento, sin chequeo, costura «primer cuadro congelado», `intro_s` = `fase2b.INITIAL_SILENCE_SEC`; (3a) `armar`/`a_markdown` sin la clave ni la palabra; (3b) `editar` con `{tarjeta: …}` → `ValueError`, papel intacto (se eligió rechazar: ignorar escondería un `--plan-edit` viejo).

**Mapa:** CC editó los stickers en `lab/tools/mapa_modulos.py` (fase2b, gfx_layer, gfx_realizador, pantalla_entrada, pantalla_colocar, voz_datos, gfx_guion, m01d_particion, m01e_pantalla) y regeneró `lab/MAPA_MODULOS.md/.json` (`python lab/tools/mapa_modulos.py`: 35 módulos · 115 aristas · 0 muertos; «tarjeta» 0 veces en el mapa; «F38e» 13). Commit `68e6c41` por rutas explícitas (24 archivos).

**Lo que queda abierto, D (entero, del subagente):**
- d1. El papel de Vajont (`data/scripts/_steps/f8s3-vajont/01e_pantalla.json`) sigue con la clave `tarjeta` de F38d; Fase 2 no la lee; se limpia sola la próxima corrida de m01e. No se tocó `data/`.
- d2. Guiones y `gfx_plan_ch01.resolved.json` anteriores a hoy traen el evento/`tarjeta_inicial`; nadie los lee (test d2 lo prueba); con el md5 del plan (A.1) la capa de ch01 se rehace sola.
- d3. Los `.md` de B.5 y F38d en `lab/` quedan como historia.
- d4. `git status` avisa LF→CRLF para `test_module_f38e_c2.py`: ya era LF antes de D (como f38e_c y f38e_d); no se cambiaron finales de línea.
- d5. Sin render (freno): el mp4 real con intro 2,5 s y primer cuadro congelado se ve recién en el próximo render; el guion ya lo describe.

## E — Títulos de cap (`6c1656a`)
Subagente E. Archivos: `script_engine/m01d_particion.py` (+18/−7: `PEDIDO_TITULOS`, cuerpo y docstring de `titles()`; `TITLES_SCHEMA`, `_title_fallback`, validación, `len(ts) != 7 → respaldo`, `call_flash_json` sin cambios), `test_module_f38e_e.py` (7 tests), `lab/hyperframes/f38e/e/` (`e_titulos.py`, `E_SALIDA.md`, `e_titulos.raw.json`, `e_titulos.log`). CRLF preservado (`file`: «with CRLF line terminators»).

**Literal, por código (comprobado también por CC antes del commit):** bloque «Pedido nuevo, entero» de `PRUEBA2_prompt_titulos.md` (md5 del md `e644cb0e…`) extraído con `re.search(r"## Pedido nuevo, entero\n```\n(.*?)\n```")` → md5 `0c3fe5599f500ce523c77aac0e328597`, 494 caracteres, placeholders exactamente `{TITLE_MAX_WORDS}` y `{lines}`; `m01d_particion.PEDIDO_TITULOS` → el mismo md5; `bloque == PEDIDO_TITULOS` → True. Pedido de Vajont con el código nuevo: md5 `9b497da4ce33763d4912bc99eb63cccd` (5185 car.) contra `85e8b649…` (5178) de la prueba 2: **única línea distinta, la 22** («beat 10 pico · pico: …» contra «beat 10 pico: …»), que es la corrección del pico (e7 de F38e-0). `lines`: `CAP n:` / `beat <n> <funcion>[ · pico]: se ve: … · pregunta que abre: …` / `termina (no lo cuentes): <cierre del último beat>`; `pico = int((esc.get("pico") or {}).get("beat") or 0)` (el patrón de `rebalance()`), la marca solo en el beat cuyo `n` coincide.

**Salida en texto (E.3):** el pedido entero tal como sale para Vajont está en `lab/hyperframes/f38e/e/E_SALIDA.md` (md5 `9b497da4…`; el beat 10 lleva « · pico»); corrida real `titles(esc)` tal cual, sin `call` inyectado, una llamada a `gemini-2.5-flash`, `src = "flash"`, 7,6 s, **US$ 0,004071** (in 1354 · out 37 · thinking 1429; `cost_tracker.session_overhead` en memoria). Escaleta congelada `lab/hyperframes/f38/b2/fase1/f8s3-vajont/01a_escaleta.json` (md5 `e0094c37…` = `data/`); skeleton congelado md5 `64f51b5e…` = `data/`.

| cap | hoy (de `01a_skeleton.json` congelado) | nuevo | validación | ¿promete sin contar el final? |
|---|---|---|---|---|
| ch01 | Cama en la oscuridad | La fuerza misteriosa | ✓ |  |
| ch02 | El muro que tapa | La montaña advierte | ✓ |  |
| ch03 | La costura abierta | El agua responde | ✓ |  |
| ch04 | La ola de juguete | Ignorar la evidencia | ✓ |  |
| ch05 | Piedras rodando | Las últimas horas | ✓ |  |
| ch06 | El gran rugido | Cuatro minutos fatales | ✓ |  |
| ch07 | Diarios y verdades | La verdad final | ✓ |  |

Foto de `data/` (mtime + md5, 1320 archivos) antes y después de la llamada: nuevos o tocados ninguno, borrados ninguno; `_dump_invalid_json` desviado a `f38e/e/` (no se usó); sin `start_video`/`end_video`, `data/cost_history.json` intacto.

Tests: `test_module_f38e_e.py` + `f10`, `f11`, `f11b`, `f22`, `f23`, `f33` → 140 passed; suite rápida 58 (CC repitió `f38e_e` + `f10` + rápida: 78 passed). Ningún test existente cambiado: el único que llama `titles(` (`test_module_f10.py::test_titulos_con_respaldo`) no mira el texto del pedido. Commit `6c1656a` por rutas explícitas (6 archivos). Sticker de `m01d_particion` → mapa en el commit final.

**Lo que queda abierto, E (entero, del subagente):**
- e-E1. «beat 10 pico · pico»: en Vajont la `funcion` del beat 10 ya se llama `pico`, así que la línea queda redundante. Es la letra del handoff y del md (« · pico» en el beat del pico, y la función sin tocar); no se cambió. Para un tema cuyo pico tenga otra función (giro, escalada) sale limpio.
- e-E2. Cifra en letras: «Cuatro minutos fatales» pasa la validación de código (sin dígito), igual que en la prueba 2 (e8). El pedido dice «sin cifras»; el código no lo ve. Sin regla nueva (no está en el handoff).
- e-E3. «¿Promete sin contar el final?» queda vacía para Omar / el analista (es a ojo). Para su lectura: ch05 «Las últimas horas» y ch07 «La verdad final» rozan el `cierre` (el riesgo de spoiler que el md anuncia: «si pasa, el `cierre` sale de la entrada»). La variación entre llamadas sigue (e8): con una sola llamada esta es una muestra, no una medición.
- e-E4. Beats sin `pregunta_abierta`/`cierre` (escaletas sintéticas viejas, como la de `test_module_f10`) imprimen «None» en la línea; es el mismo `.get()` sin guardia que ya usaba el pedido viejo para `funcion`/`imagen_sensorial`. Las escaletas reales de F36+ traen los dos campos. Sin regla nueva.
- e-E5. El pedido real no se capturó en la misma llamada: el script arma el pedido con un `call` falso (captura y corta, sin red) y después llama `titles(esc)` a pelo. Son la misma función sobre la misma escaleta (determinista) y el `in` de 1354 tokens es coherente con los 5185 caracteres; no se envolvió `call_flash_json` para no meter otro desvío.
- e-E6. La validación de `titles()` sigue sin estar expuesta como función: el script de lab la copia para la tabla (como `prueba2_titulos.py`, e8). Los tests la ejercitan por `titles(call=…)`.
- e-E7. `logs/`: el import de `cost_tracker` deja un `pipeline_*.log` vacío por corrida (e11 de F38e-0) y los tests de f11b escriben otro con su `t-f11b`; `logs/` está en `.gitignore`. No se borró nada.
- e-E8. Docstring del módulo (líneas 17–18, «7 títulos de ≤ 5 palabras desde la escaleta») sigue válida y no se tocó; el docstring de `titles()` es el que explica lo nuevo.

## Commits de la tanda (`f11-guion-v4`, base `7fb43e0`, todos por rutas explícitas)
| commit | parte |
|---|---|
| `2453cf8` | paso 0: DECISIONES.md (md5 `463bd8e5…`) y el handoff (md5 `4e8fb36c…`), tal cual |
| `6c1656a` | E títulos de cap |
| `5008f4d` | B colocación B1–B4 (código y tests) |
| `96c2889` | A ensamble: r1 + R8 + costuras en el mp4 (+ `verificar.sh` de f38e) |
| `2965603` | C papel m01e-6 (respaldo, autor) |
| `58fc5d7` | C2 el autor del papel llega a Fase 2 (cierra c2) |
| `8f7d9cd` | B.5 fuente de la pregunta en `closing_question` + `--plan-only` de Vajont (antes/después) |
| `68e6c41` | D tarjeta borrada + mapa regenerado |
| `a376bde` | A2: el chequeo «costuras» nunca tira el render (4 fallas de `f28c` en la amplia, ver «Verificación final») |
| (último) | reporte + ESTADO |

## US$ (tope 1,00)
| parte | llamadas | US$ |
|---|---|---|
| A (render ch02, plan congelado) | 0 | 0,0000 |
| B (código) / B.5 (`--plan-only`, crítico) | 0 / 4 Gemini Vision | 0,0000 / 0,0004 |
| C (Sonnet: intento 1 + 3 vueltas) | 4 | 0,8096 |
| D (`--plan-only`, todo caché) | 0 | 0,0000 |
| E (Flash) | 1 | 0,0041 |
| **total** | | **0,8141** |
Peor caso estimado antes de C: 0,2804–0,3266 el intento 1 y 0,2960–0,3422 por vuelta; el tope de `llamar` (1,00) cortó la vuelta 4.

## Candado por commit y al cierre
- En cada commit: suite rápida (`f25c f24 f21`, 58) y los tests de la parte, corridos por CC (E 78 · B 96 · A 101 · C 113 · C2 32 + 58 · B.5 44 · D 136).
- Al cierre, sobre `68e6c41`: `lab/hyperframes/f38e/verificar.sh final` (md5 de ch02 de Orleans sin gfx, rápida, amplia con `-n auto`) → resultado en la sección «Verificación final» de abajo.

## Verificación final (`lab/hyperframes/f38e/verificar.sh final`)
- **Corrida 1, sobre `68e6c41`** (`lab/hyperframes/f38e/final_pre_A2/`): md5 de ch02 de Orleans sin gfx `38e5ba14e3d24fd20f9297c9e1dfee24` ✓ · rápida 58 · amplia **891 passed, 11 failed**: las 5 previas conocidas (`01b_pauses` ×3, `m03_merge_timing` ×2) + `test_module_f28c.py` ×4 (`test_paralelo_respeta_orden_y_tope`, `test_memoria_se_reintenta_de_a_dos`, `test_reensamble_reusa_sin_rehacer`, `test_cap_sin_gfx_en_paralelo_se_rehace_en_fila`: «AttributeError: 'SimpleNamespace' object has no attribute 'is_first'» → el chequeo «costuras» de A leía `plan.is_first` fuera de todo `try`, y en `_segmentos_en_paralelo` una excepción del chequeo hacía caer el cap entero: contra A.3 «✗ no corta el render») + `test_module_gfx_lab.py` ×2 (`test_preview_usa_las_plantillas_reales`, `test_candado_en_el_preview`), que pasan solas y en serie (45/45) y en la corrida 2: fallaron solo bajo `-n auto`.
- **A2 (`a376bde`):** `_costura_del_segmento` envuelve la medición (`_costura_medida`) y cualquier error es una línea «✗ costura …: no se pudo medir», nunca una excepción; test nuevo `test_a3_el_chequeo_nunca_tira_el_render`; `f28c + f38e_a + gfx_lab + rápida` 124 verdes.
- **Corrida 2, sobre `a376bde`** (`lab/hyperframes/f38e/final/`): md5 de ch02 `38e5ba14e3d24fd20f9297c9e1dfee24` ✓ · rápida **58 passed** · amplia **898 passed, 5 failed** = exactamente las 5 previas conocidas (`01b_pauses` ×3, `m03_merge_timing` ×2). Sin medir RAM ni cerrar nada (DECISIONES 00:30).

## Frenos (todos respetados)
- Render completo de Vajont: no se hizo (solo `--only-cap ch02 --gfx` en A.4, como pide el handoff; sin medir RAM).
- `--aprobar-guion`: no se corrió; `aprobado` de Vajont pasó a `None` con el `--plan-only` de B.5 (los planes cambiaron: nadie aprobó nada).
- `data/`: ningún archivo del pipeline escrito ni reescrito (fotos mtime+md5 en C, E, B.5 y D). **Única escritura: `data/cost_history.json`** (ignorado por git), el ledger del `cost_tracker` que todo `fase2b` escribe al cerrar el video: tres entradas de `f8s3-vajont-f30` (A.4 US$ 0; B.5 US$ 0,0004; D US$ 0) y dos de Orleans `ba6c3cac-…` (los dos `--only-cap ch02` sin gfx del `verificar.sh`, US$ 0). Las corridas de lab (C, E) no lo tocaron. Se declara como desvío de «nada en data/»: es el comportamiento de siempre de `fase2b` (F38d B también lo escribió), no un artefacto del pipeline; si Omar quiere que las corridas de lab tampoco lo registren, es un pedido aparte.
- Gasto 0,8141 ≤ 1,00.
- Números nuevos: ninguno fuera de la tabla (`test_constantes_con_origen` verde en C y en la suite amplia). Derivados: `1/fps` (±1 cuadro), `d=` de `blackdetect` = negro − 2 cuadros (a3).
- Fase 3, publicar, merge: no.

## Lo que queda abierto (entero)
Los abiertos por parte están pegados enteros en cada sección (a1–a9, b1–b10, c1–c11, d1–d5, e-E1–e-E8). Lo que cruza partes o es de la tanda:
- g1. **Vajont v6 queda congelado** (DECISIONES 03:29) con sus 7 negros de cierre faltantes (R8, a1), la tarjeta del segundo 0 (D) y los títulos viejos: ningún render nuevo en esta tanda. Un render nuevo necesita `--aprobar-guion` de Omar sobre el guion de D (`lab/hyperframes/f38e/d/despues/`), que ya tiene D47 en [11], 9 OCT, la pregunta de ch07 desde la voz y sin tarjeta; con el md5 del plan (A.1) las 7 capas se rehacen solas (~20 min, a9).
- g2. **El papel m01e-6 de Vajont (`lab/hyperframes/f38e/c/01e_pantalla.*`) no está en `data/`** ni fue a `--plan-only`: el handoff pedía la corrida con `steps_dir` y nada en `data/`. Es la compuerta de Omar si quiere compararlo con v6 (tabla C). Para que Fase 2 lo consuma hay que copiarlo a `data/scripts/_steps/f8s3-vajont/` (fuera de esta tanda).
- g3. **c1 (regla del autor, «Pietro Leone»)**: la letra del handoff («cada nombre propio que no abre la frase») no cumple su propio caso de test; C aplicó la lectura «el que abre cuenta si va seguido de otro nombre propio». La decide el analista.
- g4. **c3**: el cierre por tope con un motivo que no se va (`a_pantalla` que el autor descarta cada vuelta) gastó 3 vueltas (US$ 0,47): «sin progreso» mira todos los motivos, no cada beat. Es F38d tal cual; para Kyshtym conviene que el analista lo mire (costo por video).
- g5. **b2 / #9 ch01**: el texto nuevo va en la pausa final (el handoff: «la posición no cambia»); si el analista quería el ancla en el inicio de [14], es un pedido de posición, no de esta tanda.
- g6. **b7 / #6 Q51** queda en [18] por el crítico (tapa la carta manuscrita en los 3 instantes de [17]); ahora declarado. Gusto → `--plan-edit`.
- g7. **b9**: la escena 10 de ch05 pasa a `dissolve` (salto de tiempo) por el reloj nuevo: regla previa de `gfx_style`; que el analista lo vea.
- g8. **a3**: la tolerancia `d=` de `blackdetect` (negro − 2 cuadros) es derivada y explicada; otra tolerancia es un número del analista.
- g9. **e-E2 / e-E3**: «Cuatro minutos fatales» (cifra en letras) pasa el código; «Las últimas horas» y «La verdad final» rozan el `cierre`. La columna «¿promete sin contar el final?» queda vacía para Omar y el analista, como «¿se entiende solo?» en C.
- g10. **Ledger en `data/cost_history.json`** (arriba, Frenos): tres entradas nuevas de `f8s3-vajont-f30` (A.4, B.5, D) y dos de `ba6c3cac-…` (Orleans) por los dos `--only-cap ch02` sin gfx del `verificar.sh` (13:37 y 13:43; el candado md5 de cada tanda las escribe igual). Lo encontró el revisor (fila 15).
- g11. **Respaldo de la capa de v6**: `output/f8s3-vajont-f30/_fase2b_work/_bak_f38e_a/` (136 MB) y `_bak_v6_capas_v5/` (r5, 3,1 GB) siguen ahí; `ch02_gfx.mp4` de `_fase2b_work/` es ahora la capa rehecha por A.4 (con sidecar), no la de v6.
- g12. **`logs/`**: cada corrida e import de `cost_tracker` deja un `pipeline_*.log` vacío (e11); ignorados por git; no se borraron.
- g13. **Tests que siguen leyendo `data/`** (c8 de F38c: `f37a_papel`, `f38a_voz` cargan escaleta/narración/pool de `data/`): no se tocó en esta tanda; los tests nuevos leen de `lab/`.
- g14. Lo de siempre fuera de la tanda: B5 y d1 (prompt), forma F31b, subtítulos documentales (r3), formato de cifras del research (c9 de F38c), `--plan-edit` sin `respaldo` (c9 de C).

## Procesos (paso 12 de `/tanda`)
Subagentes: A, B, C, E (en paralelo), D, revisor-handoff: los seis terminaron y devolvieron su reporte; ninguno vivo. Shells en segundo plano: los dos `verificar.sh` (terminados, exit 0). Procesos de la tanda: ninguno vivo (los `fase2b`, `ffmpeg` y `pytest` de los subagentes terminaron con ellos). No se cerró ningún programa de Omar.

## Veredicto del revisor (`revisor-handoff`, íntegro)
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 0 | Paso 0: md5 DECISIONES `463bd8e5…` y handoff `4e8fb36c…`, commit tal cual | OK | `md5sum` coincide; `2453cf8` toca solo esos 2 archivos |
| 1 | A.1 r1: sidecar con md5 del plan, reuse solo si coincide, log «capa de otro plan: se rehace» | OK | `gfx_layer.py` `capa_reusable`/`_sellar_capa`/`apply_gfx`; `onlycap_ch02_gfx.log` («capa sin md5 de plan: se rehace»); `test_module_f38e_a.py` pasa |
| 2 | A.2 R8: causa con datos y arreglo general | OK | `pausa_de_cierre`/`pausa_a_disco` (misma cuenta en los dos caminos); tabla de 7 segmentos (−1,0 s) en `a/tabla_v6_segmentos.md`. Desvío declarado: la sospecha del analista (`fase2b`) era falsa; la causa estaba en `gfx_layer` |
| 3 | A.3 chequeo «costuras» medido en el mp4 (ffprobe ±1 cuadro + blackdetect) | OK | `fase2b._medir_cierre`; log «✓ costura ch02: segmento 140.600 s vs guion 140.600 s» y «negro 139.600→140.600». Observación: `d=` de blackdetect = negro − 2 cuadros es un derivado (abierto a3); no está en la tabla de constantes |
| 4 | A.4 salida en texto y md5 de ch02 sin gfx `38e5ba14…` | OK | `f38e/a/onlycap_ch02_gfx.log`; `f38e/final/onlycap_ch02_nogfx.log` y `final_pre_A2/…` dan `38e5ba14e3d24fd2…` (no lo corrí) |
| 5 | B.1 / B.2 / B.3 / B.4 | OK | 11 tests `f38e_b` verdes (los corrí); B3 declara causa (crítico, no bug); B4 simulada en los 7 caps (`b/B4_simulacion.md`) igual a lo esperado |
| 6 | B.5 antes/después y filas #2 #5 #6 #8 #9 + «todo lo demás» | OK | `b/antes` y `b/despues` (md5 .md `0af5b1dc…` / `492d4851…`); `despues` muestra D47 a 03:04.5 escena 8, 9 OCT a 10:00.2, ch07 con la pregunta nueva de 3,1 s. #6 queda en [18] (declarado como ✗ a propósito) y la lista de otros cambios está entera. Sin `--aprobar-guion` |
| 7 | C.1 PANTALLA_SYSTEM letra por letra, md5 `7d2ccdd2…`, `PROMPT_VERSION="m01e-6"` | OK | Recalculé: md5 `7d2ccdd28055d6e621d1d251a0fe8bb7`, igual al bloque del md (3098 car.), `m01e-6`, `prompt_md5` `3b98aef1…` |
| 8 | C.2 / C.3 formatos, respaldo, candado | OK | `m01e_pantalla.py:117-129`, `:605-640`; 11 tests `f38e_c` verdes |
| 9 | C.4 autor (Municipio pasa, «Pietro Leone» no, Q14 reportado) | PARCIAL | Los 3 casos están en tests y en la tabla. Pero «Pietro Leone» no pasa solo porque C agregó una regla que el handoff no trae (`_nombres_del_autor`: el nombre que abre cuenta si lo sigue otro nombre propio). La letra del handoff («cada nombre propio que no abre la frase») lo dejaría pasar. Declarado (c1/g3), lo decide el analista. Efecto: «Giovanni Leone, presidente del Consejo» cae al autor del archivo |
| 10 | C.5 salida en texto (tabla, 3 citas, US$, vueltas), steps_dir sin tocar data/ | OK | `c/TABLA.md`, `c/C_SALIDA.md`; las 3 citas entran; `c_corrida.log`: US$ 0,8096, 4 llamadas, cerró por tope |
| 11 | C.6 tests actualizados, ninguno borrado sin decirlo | OK | 5 archivos ajustados; el cambio de `f38d::test_5` está explicado |
| 12 | E.1–E.3 pedido de títulos letra por letra, corrección del pico, tests, salida | OK | `PEDIDO_TITULOS` md5 `0c3fe5599f500ce523c77aac0e328597` = bloque del md (recalculado); pico desde `esc["pico"]["beat"]`; `f38e_e` verde; `e/E_SALIDA.md` y `e_titulos.log` (US$ 0,004071) |
| 13 | D: borrar la tarjeta (no apagarla), grep antes/después, `--plan-only` rehecho, D después de A | OK | `grep -i tarjeta script_engine/*.py fase2b.py` → 0 (lo corrí); `d/grep_antes.txt` 88 líneas; `68e6c41` es posterior a `96c2889`; `d/plan_only.log` intro 2,5 s; sin llamadas a `tarjeta_*` fuera de tests |
| 14 | Frenos: sin render completo, sin `--aprobar-guion`, sin fase3/merge | OK | Solo `--only-cap ch02` (A.4) y `--plan-only`; no hay `aprobar` en los logs |
| 15 | Nada en `data/` | OK con desvío | `find data -newermt 08:00` → solo `cost_history.json` (ignorado por git), que `fase2b` escribe siempre. El reporte declara 3 entradas de Vajont, pero también hay 2 de Orleans (13:37 y 13:43) de los md5 de `verificar.sh`, no declaradas |
| 16 | Gasto ≤ US$ 1,00 | OK | 0,8096 (C) + 0,0041 (E) + 0,0004 (B.5) = 0,8141, comprobado contra los logs |
| 17 | Ningún número nuevo | OK | `test_constantes_con_origen` verde; derivados declarados (1/fps, negro − 2 cuadros) |
| 18 | Suite rápida y amplia | OK | `final/suite_rapida.log` 58 verdes; `final/suite_amplia.log` 898 verdes y 5 fallas = las 5 previas (`01b_pauses` ×3, `m03_merge_timing` ×2). Corrí aparte `f38e_a/b/c/c2/d/e + f28c + gfx_layer_fallback + constantes` (65 verdes) y `gfx_lab + f36c + f34 + f36` (66 verdes). Los 2 fallos de `gfx_lab` y los 4 de `f28c` de la corrida anterior ya no aparecen |
| 19 | Commits por parte, rutas explícitas, sin M ajenos | OK | `git show --stat` de los 9 commits: ninguno trae `diag_234_cap4.py`, `gfx_profiles/*`, `f28a.log` ni `??` viejos; el status sigue mostrando esos 4 M |
| 20 | F38e_REPORT: sección «Verificación final», veredicto íntegro, ESTADO | NO VERIFICABLE | El reporte llega hasta «Lo que queda abierto» sin esa sección ni mi veredicto. `lab/ESTADO_SESION.md` no está modificado. Falta cerrarlos antes de la PARADA |

Fuera de alcance:
- Commits no previstos en el handoff, ambos declarados: `58fc5d7` (C2) agrega 2 líneas en `pantalla_entrada.py`, un módulo que la tabla del handoff no lista, y cambia lo que Fase 2 dibuja en toda cita. `a376bde` (A2) es una corrección de una regresión de A (4 tests de `f28c`).
- Cambios de D fuera de su lista literal: `gfx_project.py` (solo un docstring, para dejar el grep en cero) y `lab/tools/mapa_modulos.py` + `lab/MAPA_MODULOS.*` (convención del repo).
- Quedan sin commitear en `lab/hyperframes/f38e/`: `vajont_steps/` (declarado), `F38e_REPORT.md` y varios `_data_*.txt` y `_plan_only_*.txt`.

Riesgos que el contrato no cubre:
- r1 compara el sidecar con el `resolved.json` que hay en disco, no con un plan recalculado hoy (abierto a2). Fuera del flujo con guion aprobado, un plan nuevo cuyo `resolved.json` no se reescribió podría reusar una capa vieja.
- Nada de lo nuevo se probó sobre un mp4 real salvo el cap ch02 de Vajont: el render completo con intro 2,5 s, sin tarjeta y con 7 negros de cierre queda sin validar (a1, d5). El `--plan-only` dejó a Vajont en `aprobado: None`: cualquier render nuevo necesita `--aprobar-guion` de Omar.
- La regla de autor c1 y el cierre por tope con un motivo `a_pantalla` que no se va (c3, US$ 0,47 en vueltas) pesan en el costo y la calidad de Kyshtym.

### Adenda de CC (después del veredicto; el texto de arriba queda tal cual)
- Fila 15: las dos entradas de Orleans en `data/cost_history.json` (13:37 y 13:43) son de los dos `--only-cap ch02` sin gfx del `verificar.sh` (el candado md5 de toda tanda las escribe igual). Quedan declaradas en g10 y en «Frenos».
- Fila 20: el revisor corrió mientras la corrida 2 del candado terminaba y antes del cierre del reporte. Ahora están la sección «Verificación final» (corrida 1 sobre D: 891 + 11; A2; corrida 2 sobre `a376bde`: 898 + las 5 previas), este veredicto, y `lab/ESTADO_SESION.md` (cabecera, «Para Omar (F38e)», bloque F38e); todo entra en el commit final junto con los logs de `final/` y `final_pre_A2/`.
- Fuera de alcance, «sin commitear»: `vajont_steps/` no entra (sus entradas = `f38/b2/fase1`, c10); los `_data_*_full.txt` y `_plan_only_*.txt` de `b/` y `d/` son las fotos crudas de mtimes (142 KB cada una) cuya diferencia ya está pegada en `B_SALIDA.md` y `D_SALIDA.md`: no entran, a propósito.
- Fila 9: la lectura c1 queda tal cual para que la decida el analista (g3); el código cumple el caso de test que el handoff exige («Pietro Leone» no pasa) y lo declara.
