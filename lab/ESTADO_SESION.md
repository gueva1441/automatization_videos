# ESTADO_SESION — dónde estamos (leer ANTES de programar)

Última actualización: 2026-10-27 (F39: Fase 1 de la semilla al papel en producción + Kyshtym en limpio; HECHA, PARADA en el papel de `f39-kyshtym`; el analista da la nota 1–10 de Fase 1) · CC lo actualiza en cada hito (commit, reporte, decisión de Omar).

## Proyecto activo
- Repo: `C:\CLAUDE_PROJECTS\automatization_videos` · rama activa **`f11-guion-v4`** (desde `b8ff4ef`, en `f10-integracion-v3`). `f10-integracion-v3` termina en `fccecd0` (docs del freno de Omar). Historia vieja: f6-guion-v3 sale de `45c052c` (tip de `f5-guion-v2`, que sale de `39e37ac`).
- Cadena de ramas sin mergear: `f2-gfx-director` (F2b @ `31c671c`) → `f3-lab-identidad` (F3–F4e @ `39e37ac`) → `f5-guion-v2` (F5).
- `main` = `43f528a`. NO se toca sin OK explícito de Omar.
- Video de prueba: Orleans `ba6c3cac-a091-41c0-8dad-afd2f4364747` (7 caps; ch02 es el cap de calibración, ch05 el segundo). Copia del research para F5: **`ba6c3cac-f5v2`**.
- Candados vigentes:
  - md5 de ch02 `--only-cap` sin `--gfx` = `38e5ba14…` (último: `lab/hyperframes/f4e/corrida/onlycap_ch02_nogfx_f4e.log`);
  - 364 tests verdes en las suites de guion y gfx. Las 3 fallas de `test_module_01b_pauses.py` son previas a F5.
  - F29: suite amplia = 921 verdes + 5 previas.
  - F16: suite amplia (`test_module_f[0-9]*`, `gfx_*`, `01a*`, `01b*`, `m03_*`, fase2b reassemble/hwencode, concat, transition) = 650 verdes + 5 previas; `test_module_f11.py::test_v3_byte_identico` verde.

## 👀 Para Omar (F39): Fase 1 ya corre sola de la semilla al papel con un comando de producción, y paró donde debe: en el papel. Kyshtym (topic limpio `f39-kyshtym`) corrió sin manos en 41 min por US$ 4,76 (tope 5,00). Para leer: el papel entero en `data/scripts/_steps/f39-kyshtym/01e_pantalla.md` (copia en `lab/hyperframes/f39/b/salida/`), y el reporte `lab/hyperframes/f39/F39_REPORT.md` (B.4 por paso, lado a lado con F23, «lo que queda abierto» f1–f22, veredicto del revisor). Hallazgos que frenan o hay que decidir: el gancho de ch01 quedó **sin ficha** (las 4 vueltas del papel se gastaron ahí: f1); el guion quedó con 2 bloqueantes que la reparación no arregló (f6); el tope del papel es el de respaldo porque el perfil no trae `costos.m01e_tope_usd` (f2). Para seguir a la voz: `python fase1_5.py --topic f39-kyshtym --aprobar-papel "Omar <fecha>"` (solo si Omar aprueba). La rama está en GitHub (`origin/f11-guion-v4`); `main` no se tocó.

## F39 — Fase 1 de la semilla al papel, en producción + Kyshtym en limpio (handoff del analista, 2026-10-27) — HECHA, **PARADA**
- Handoff `lab/hyperframes/f39/HANDOFF_F39_fase1_de_la_semilla.md` (md5 `d2cfa61b…`). Paso 0: secretos 0 (`lab/hyperframes/f39/paso0_secretos.txt`) · `d49178d` DECISIONES 15:23 + handoff · `a67ed45` perfil vigente tal cual · push `origin/f11-guion-v4` (rama nueva; `main` intacto).
- A (en paralelo, 3 subagentes + CC): `f930596` escaleta sin ficha v2 = `EscaletaSinFicha`, rama vieja borrada (9 tests borrados, 6 ajustados, prompts v2 idénticos) · `e664390` `topic_researcher.investigar_semilla(seed, topic_id)` · `6b2b717` `fase1_5`: `--semilla … --topic …`, compuerta → ficha si falta → escaleta, compuerta del papel después de m01b (md5), `--aprobar-papel`. Tabla §1 por código: 2 de 8 topics paran, los dos de lab. Candado: md5 ch02 `38e5ba14…`, rápida 58, amplia 913 + las 5 previas.
- B: `python fase1_5.py --semilla lab/hyperframes/f39/b/semilla_kyshtym.json --topic f39-kyshtym --v3 --guion v4 --batch`, una corrida, sin manos (16:04 → 16:45), US$ 4,7627: research 1,48 · ficha 0,40 · escaleta 0,81 · guion 1,07 · reparación 0,10 · partición 0,13 · papel 0,77. Paró en la PARADA del papel; nada después (ni voz ni `output/`). Semilla: la de F18 (no está en `seeds_archive.json`).
- Escrituras en `data/`: `_steps/f39-kyshtym/`, `topics_db.json` (+ respaldo `topics_db.pre_f39-kyshtym.json`), `cost_history.json` y `geocode_cache.json` (no previsto en el handoff, declarado).
- Abierto f1–f22 en el reporte. Lo siguiente: el analista lee el papel y da la nota 1–10 de Fase 1 con cada falla «se queda / se arregla a mano / frena».
- Reglas aprendidas: la búsqueda de secretos deja su salida en un archivo (el revisor no pudo reconstruir el rango después del push); un comando largo sin manos va en segundo plano con su log y hora de inicio/fin en archivos; la tabla B.4 por paso la arma un subagente de solo lectura mientras CC hace B.5 y costos.

## 👀 Para Omar (F38e): el sistema quedó listo para Kyshtym en lo que esta tanda cubría; Vajont v6 sigue congelado (no se re-renderizó, nadie aprobó nada). Para mirar: (1) el papel m01e-6 de Vajont en `lab/hyperframes/f38e/c/01e_pantalla.md` y su tabla contra v6 y la prueba 1 en `c/TABLA.md` (las 3 citas entran, con autor en español; columna «¿se entiende solo?» vacía); (2) los 7 títulos nuevos en `lab/hyperframes/f38e/e/E_SALIDA.md` (columna «¿promete sin contar el final?» vacía); (3) el guion de pantalla de Vajont con B1–B4 y sin tarjeta en `lab/hyperframes/f38e/d/despues/GUION_PANTALLA.md` (D47 sobre Müller, reloj 9 OCT, ch07 «¿Quién decidió que Micaela siguiera durmiendo?», intro 2,5 s). Decisiones que quedan para Omar/analista: c1 (regla del autor), Q51 en [18] por el crítico (gusto → `--plan-edit`), b9 (dissolve en ch05). Reporte entero con el veredicto del revisor: `lab/hyperframes/f38e/F38e_REPORT.md`.

## F38e — Lo que rompe cualquier video, y nada más (handoff del analista, 2026-10-27) — HECHA, **PARADA**
- Handoff `lab/hyperframes/f38e/HANDOFF_F38e_lo_que_rompe_cualquier_video.md` (md5 `4e8fb36c…`). Paso 0 `2453cf8` (DECISIONES 12:32, md5 `463bd8e5…`). Commits por parte en `f11-guion-v4`: E `6c1656a` · B `5008f4d` · A `96c2889` · C `2965603` · C2 `58fc5d7` · B.5 `8f7d9cd` · D `68e6c41` (mapa regenerado) · A2 `a376bde` · reporte + ESTADO (último). A, B, C y E en paralelo (un subagente cada una); B.5 después del render de A (la aprobación); D después de las cuatro.
- **A:** r1 la capa deja `chNN_gfx.plan.md5` y con `--reuse-visuals` se rehace si no es el del plan de hoy; R8 causa con datos (`gfx_layer` rama del plan congelado alargaba el base con la pregunta sin el negro: los 7 `seg_0N` de v6 miden 1,0 s menos que el guion) → `pausa_de_cierre` = pregunta + negro; chequeo «costuras» medido en el mp4 (ffprobe ±1 cuadro + blackdetect); `--only-cap ch02 --gfx` de Vajont: segmento 140,600 s = guion, negro ✓, US$ 0. A2: el chequeo nunca tira el render.
- **B:** B1 todo inicio de escena dentro de la oración ancla; B2 el reloj mueve su fin con el intento; B3 Q51 [17]→[18] fue el crítico (tapa la carta), no bug; todo movido declara sus fallas; B4 pregunta de cierre desde la voz (= lo esperado en los 7 caps). B.5 `--plan-only`: #2 D47 sobre Müller ✓, #5 9 OCT 89,43 s ✓, #8 ch07 46 car. ✓, #9 ch01 texto ✓ (misma posición), #6 Q51 queda en [18] por el crítico; `aprobado` → None; US$ 0,0004.
- **C:** prompt m01e-6 = PRUEBA1 letra por letra (md5 `7d2ccdd2…`), `respaldo` y `autor` en el formato, regla `respaldo`, candado contra el respaldo, autor del modelo verificado contra el archivo (`autor_origen`); corrida en `lab/hyperframes/f38e/c/` con `steps_dir` (nada en `data/`): 4 llamadas, US$ 0,8096, cerró por tope; 13 fichas, 7/7 picos, las 3 citas entran. C2: el autor del papel llega a Fase 2.
- **D:** tarjeta fecha-hora borrada de `voz_datos`, `m01e`, `pantalla_entrada`, `gfx_layer`, `gfx_guion`, `fase2b` y tests (grep 88 → 0; 9 tests borrados por nombre); `--plan-only` sin tarjeta: intro 2,5 s, el mp4 corre −0,5 s, US$ 0.
- **E:** `titles()` manda el pedido de PRUEBA2 letra por letra (`PEDIDO_TITULOS`, md5 `0c3fe559…`) con pico desde `esc.pico.beat`; corrida real: 7 títulos ✓, US$ 0,0041.
- Gasto total US$ 0,8141 (tope 1,00). Frenos: sin render completo, sin `--aprobar-guion`, nada del pipeline en `data/` (único desvío declarado: el ledger `data/cost_history.json` que todo `fase2b` escribe), sin fase3/merge, ningún número nuevo.
- Candado al cierre (sobre `a376bde`, `lab/hyperframes/f38e/final/`): md5 ch02 `38e5ba14…` ✓, rápida 58, amplia 898 + las 5 previas conocidas (`01b_pauses` ×3, `m03_merge_timing` ×2), con `-n auto`. La corrida anterior (sobre D) tuvo 4 fallas de `f28c` (arregladas en A2) y 2 de `gfx_lab` solo bajo `-n auto`. Revisor: veredicto íntegro en el reporte.
- Abierto: por parte (a1–a9, b1–b10, c1–c11, d1–d5, e-E1–e-E8) y general (g1–g14) en `F38e_REPORT.md`. Lo siguiente: Kyshtym de la semilla al papel (otro handoff).
- Reglas aprendidas en esta tanda: con cuatro subagentes a la vez, el candado (md5 + amplia) lo corre CC en serie al final, no cada subagente; un `--plan-only` sobre un topic aprobado invalida la aprobación → cualquier `--only-cap … --gfx` de esa tanda va antes; un chequeo nuevo en el armado de segmentos se envuelve entero (una excepción en paralelo tira el cap).

## 👀 Para Omar y el analista (F38e-0): llenar las columnas vacías de `lab/hyperframes/f38/prueba1/TABLA.md` («¿se entiende solo?») y `prueba2/TABLA.md` («¿promete sin contar el final?»); las dos tablas están también en `lab/hyperframes/f38/F38e0_REPORT.md`. No se decidió nada.

## F38e-0 — Dos pruebas en seco: rótulos y títulos (pedido de Omar, 2026-10-27) — HECHA, **PARADA**
- Handoff `lab/hyperframes/f38/HANDOFF_F38e0_pruebas_en_seco.md` (md5 `ef89918b…`). Paso 0 `2819c09` (DECISIONES 11:21/11:44, los dos prompts de prueba y el handoff, md5 comprobados).
- A (Sonnet, una llamada, US$ 0,3391): prompt m01e-6-prueba letra por letra; 12 fichas, todas con respaldo literal y cifras literales; las 3 citas cortan por el candado («— autor» dentro del dato). B (Flash ×3, US$ 0,0152): 21 títulos, todos pasan la validación de hoy. Total US$ 0,3543. Sin tocar el pipeline, nada escrito en data/ ni output/.
- Abierto e1–e11 en el reporte; revisor íntegro (CUMPLE CON OBSERVACIONES).

## 👀 Para Omar (render v6): **mirar `output/f8s3-vajont-f30/f8s3-vajont_final_gfx_v6.mp4`** (17:29, 2560×1440, md5 `b0640b60…`; sin música: `_v6_no_music.mp4`). Ojo: la primera corrida reusó las capas gfx de v5 sin avisar (bug del caché, abierto r1); se movieron a `_fase2b_work/_bak_v6_capas_v5/` y se re-renderizó.

## Render v6 de Vajont (pedido de Omar, 2026-10-27) — **HECHO, PARADA**
- Paso 0 `fbe517a` (DECISIONES 03:29/03:34/03:37 + `REVISION_GUION_F38d.md`, md5 comprobados). Paso 1: plan `0af5b1dc…` = `f38/b4/`. Paso 2: `--aprobar-guion "Omar 2026-10-27"` hecho. Paso 3: 9.6 GB libres → PARADA; nada cerrado. Omar ordenó arrancar con 13.6 GB («no le pares bola»). Corrida 1 (4:45) reusó las capas gfx de v5 (caché de `apply_gfx` con `--reuse-visuals`, abierto r1) → capas movidas a `_bak_v6_capas_v5/` → corrida 2 (25:11): 7/7 gfx OK, sin base_clip ni timeouts, RAM mínima 10.58 GB, md5_planes `35576ed6…` = aprobado. `f8s3-vajont_final_gfx_v6.mp4` 1049.3 s · 2560×1440 · md5 `b0640b60…`. Sección «Render v6» en `lab/hyperframes/f38/F38_REPORT.md`; logs en `lab/hyperframes/f38/v6/`.

## 👀 Para Omar (F38d): leer `lab/hyperframes/f38/b4/01e_pantalla.md` (13 fichas, 7/7 picos, D128 «1.910 personas», Q50 y D245 adentro, tarjeta 9 OCT 1963 · 22:39) y la lista «para la compuerta de Omar» de la sección F38d de `F38_REPORT.md` (gancho D84 o D131, T50 «720 m», D192, Q51, CALMA, sello del gancho). Si está bien: «aprobado» → `--aprobar-guion` → render v6. Nada se renderizó.

## F38d — Vueltas de reintento y caben medido igual (pedido de Omar, 2026-10-27) — HECHA, **PARADA**
- Handoff `lab/hyperframes/f38/HANDOFF_F38d_vueltas_y_caben.md` (md5 `7af6d606…`). Base `cc7058d`. Paso 0 `25c2f6c` (DECISIONES 02:36 + handoff).
- **A HECHO** (`beb8118`; código y tests en paralelo; revisor de A en paralelo con B: CUMPLE CON OBSERVACIONES): vueltas de reintento parcial (motivos, progreso, tope del perfil; lo nuevo se pregunta; `confirmados` acumulados; `cortados_al_cierre`; `reintento.vueltas/cierre`); prompt `m01e-5`, solo la oración de caben (md5 `163e1fd1…` → `76f1de7a…`); motivo de caben con desglose y máximo del beat. md5 `38e5ba14…`, rápida 58, amplia 856 + 5 previas.
- **B HECHO** (commit B): m01e US$ 0.4751 (intento 1 + 1 vuelta, cierre «sin motivos», nada cortado sin pregunta); papel 13 fichas, 9 sellos, tarjeta ✓. `--plan-only`: 13/13 fichas, 7/7 picos, 8 sellos (CALMA sin colocar), a_pantalla 4/5, cifra ✓. Archivos en `lab/hyperframes/f38/b4/`.
- **PARADA final F38d** (sección F38d de `F38_REPORT.md`, los dos veredictos íntegros, abierto d1–d8).

## 👀 Para Omar (F38c): leer `lab/hyperframes/f38/b3/01e_pantalla.md` (10 fichas: D128 «1.910 personas» y D245 entraron; D131 de vuelta en [15]) y la lista «para la compuerta de Omar» de la sección F38c de `F38_REPORT.md` (picos vacíos ch04 b7 y ch05 b8, D192, CALMA/RABIA). Decidir: `sim_f38c.py` frenado por `guard_git` (abierto c1). Nada se renderizó.

## F38c — Marcas a_pantalla, contradicción como pregunta, decimales (pedido de Omar, 2026-10-27) — HECHA, **PARADA**
- Handoff `lab/hyperframes/f38/HANDOFF_F38c_marcas_contradice_decimales.md` (md5 `3221f784…`). Base `1f365cb`. Paso 0 `7aeae89` (DECISIONES 01:56, handoff, archivado del borrador; borrador borrado; `sim_f38c.py` NO: lo frena `guard_git`).
- **A HECHO** (`95f2e49`, dos subagentes en paralelo): `a_pantalla` en campo propio y motivo del reintento; `contradicciones_de` + pregunta `contradice` al autor + `juicio_autor` hasta el chequeo 5 (vía `pantalla_colocar`, 5.º módulo); `_num_tok` decimales. Prompt `163e1fd1…` sin cambios. md5 `38e5ba14…`, rápida 58, amplia 850 + 5 previas. Entradas de Fase 1 congeladas para tests en `f38/b2/fase1/`.
- **B HECHO** (commit B): m01e US$ 0.4720; papel 10 fichas (D128 b11, D245 b13, D131 [15]), 10 sellos, tarjeta ✓; el reintento cambió D105 → D241 «723 m» y cayó por `contradice` sin pregunta (abierto c2); Q50 cayó por caben dos veces. `--plan-only`: 10/10 fichas, 5/7 picos, 8 sellos, chequeo de cifra ✓, a_pantalla 3/5. Archivos en `lab/hyperframes/f38/b3/`.
- **PARADA final F38c** (sección F38c de `F38_REPORT.md`, revisor íntegro, abierto c1–c11).

## 👀 Para Omar (F38b): leer `lab/hyperframes/f38/b2/01e_pantalla.md` (papel sin editar: 12 fichas, 9 sellos, tarjeta 9 OCT 1963 · 22:39) y la lista «para la compuerta de Omar» de la sección F38b de `F38_REPORT.md` (gancho D84 a 1:04 u otro, D40 «722.50», D86/D01, D228/D128, D37/D245, ch05 b9 vacío, CALMA y SILENCIO sin colocar). Nada se renderizó.

## F38b — Quitar la causa, no agregar un juez (pedido de Omar, 2026-10-27) — HECHA, **PARADA**
- Handoff `lab/hyperframes/f38/HANDOFF_F38b_quitar_juez.md` (el del juez-2, archivado, no se usó). Base `cde0de6`. Paso 0 `d79cd9d`.
- **A HECHO** (`ab1b2c5`): la línea del gancho vuelve, literal, a la de m01e-1 (`m01e-4`, md5 `f8babc02…` → `163e1fd1…`); el juez de anclaje borrado entero (código, 6 tests, grabación, caché); se quedan reintento parcial, tarjeta desde la voz y fracciones. md5 `38e5ba14…`, rápida 58, amplia 828 + 5 previas. Mapa 35 módulos, 0 muertos.
- **B HECHO** (commit B): m01e US$ 0.5228; papel 12 fichas (gancho D84 en [10], Q14 de vuelta), 9 sellos, 4 relojes, tarjeta ✓; reintento parcial cambió 2 de 5 beats con motivo. `--plan-only`: 12/12 fichas, 7/7 picos, 7 sellos (CALMA, SILENCIO sin colocar), 3 relojes, tarjeta ✓; ✗ cifra «722.50» leída 72 250 (previo, abierto b2). Archivos en `lab/hyperframes/f38/b2/`.
- **PARADA final F38b** (sección F38b de `F38_REPORT.md`, revisor íntegro, abierto b1–b7).

## 👀 Para el analista (F38, superado por F38b): el juez de anclaje con el prompt literal marcó «adelanta» en 18 de 18 fichas → el papel de Vajont (`data/scripts/_steps/f8s3-vajont/01e_pantalla.*`) quedó con **0 fichas**; decidir la redacción del juez (abierto 1 de `lab/hyperframes/f38/F38_REPORT.md`). El papel de F37 está en `lab/hyperframes/f37/c/`. Tarjeta 9 OCT 1963 · 22:39 sale sola. Nada se renderizó.

## F38 — Reintento parcial, tarjeta desde la voz, juez de anclaje, fracciones (pedido de Omar, 2026-10-27) — HECHA, **PARADA**
- Handoff `lab/hyperframes/f38/HANDOFF_F38_reintento_tarjeta_juez.md`. Base `f39c28f`. Paso 0 `ebcf2ba` (DECISIONES 00:30 «RAM, no Firefox» + handoff, tal cual). Verificador `lab/hyperframes/f38/verificar.sh <parte>` (sin chequeo de RAM/Firefox por DECISIONES 00:30; amplia con `-n auto`, `pytest-xdist` 3.8.0 instalado).
- **A HECHO** (`ebe788e`, dos subagentes en paralelo): `m01e-3` (md5 `f8babc02…`): reintento parcial `{"cambios"}` fusionado por (cap, beat), lo demás congelado, `motivos_beat`, `reintento.ignorados`; juez `juez-1` (md5 `4264a968…`, `config.api.gemini_model`, caché `01e_juez.raw.json`, segunda ronda solo sobre lo nuevo del reintento, lo que sigue marcado sale con regla `juez`); TARJETA fuera del prompt del autor; `voz_datos.tarjeta_de_voz` + `horas_dichas` (Vajont 9 OCT 1963 · 22:39, T66); `voz_utils` fracciones en letras + `misma_cifra` (D68 ya no vuelve). Tests f38a 12 + 14. md5 `38e5ba14…`, rápida 58, amplia 832 + 5 previas. Mapa 35 módulos, 116 aristas, 0 muertos.
- **B HECHO** (commit B): m01e suelto US$ 0.6147 (Claude 0.5634 + juez 0.0514); intento 1 con 12 fichas (D131 gancho, Q14, D195…) → juez 10/10 marcadas → reintento cambió 12 beats → juez 8/8 marcadas → **papel 0 fichas**, 10 sellos, 4 relojes, tarjeta ✓. `--plan-only`: tarjeta ✓ en 00:00, 0 fichas, 8 sellos (SILENCIO y RABIA sin colocar), 3 relojes. Archivos en `lab/hyperframes/f38/b/`.
- **PARADA final F38** (`F38_REPORT.md`, revisor íntegro, abierto entero: 14; el revisor encontró tests de A que leían el papel vivo de data/ — arreglado en B, amplia 832 + 5 previas).

## 👀 Para Omar (F37): leer `lab/hyperframes/f37/c/01e_pantalla.md` (el papel nuevo, sin editar), la lista «para la compuerta de Omar» de `F37_REPORT.md` §C.3 / abierto 3 (gancho, D195, D128/D228, Q14/T85, T16/T15, Q50/D161, Q43, sellos) y decidir la tarjeta fecha-hora (el papel no la trae). Agregar `costos.m01e_tope_usd` (1.00) a `gfx_profiles/misterio.json`. Nada se renderizó.

## F37 — El papel elige más y mejor; Fase 2 mueve en vez de cortar (pedido de Omar, 2026-10-26) — HECHA, **PARADA**
- Handoff `lab/hyperframes/f37/HANDOFF_F37_papel_y_colocar.md`. Base `2067c77`. Tres partes A → B → C, un commit cada una, sin PARADA entre ellas salvo §Frenos. Contrato: `lab/hyperframes/f36/REVISION_PAPEL.md`. Verificador `lab/hyperframes/f37/verificar.sh <parte>` (copia del de F36).
- **Paso 0 HECHO** (`6631703`): `DECISIONES.md` tal cual (22:26, 22:32, orden 3b) + `REVISION_PAPEL.md` y el handoff F37, tal cual.
- **A HECHO** (commit A): `m01e_pantalla` m01e-2 (reemplazo literal de A.3a; md5 del prompt `ababbc8b…`, del SYSTEM `e7b3e0a3…`; `tipo` en los descartes): archivo con `fecha`/`rol`/`testimonio`; validación en papel «fecha del relato» (año del ítem contra el último año que dijo la voz; el año en dos cifras lo sitúa: D47 «la década del cincuenta») y «cita sin fecha» (autor por nombre o rol en la oración o una vecina); coincidencias de `no_dicho`/`spoiler` = preguntas al autor (su respuesta del reintento es final; Fase 2 respeta `juicio_autor`); descartes «voz_lo_dice» verificados (cifras o nombres); picos sin ficha; UN reintento con todos los motivos. `SEG_POR_PALABRA` derivado (`voz_utils.seg_por_palabra`: mediana de 200 oraciones de 9 caps del narrador = 0.3459; respaldo 0.35); `caben` sin pasar de `callout_dur_max` × 15; `TOPE_USD` = `costos.m01e_tope_usd` del perfil (respaldo 1.00; la clave la agrega Omar, `gfx_profiles` fuera de git; `gfx_config` acepta `costos`). En seco sobre la respuesta de F36 (`f37/a/seco_validacion_sobre_f36.txt`): Q43 cae por cita sin fecha, D47 y D105 van como pregunta, T39/T21/D68/T85 vuelven, Q50 cae por caben (127 > 90), pico ch05 b8 vacío. Tests `test_module_f37a_papel.py` (9). md5 `38e5ba14…`, rápida 58, amplia 842 + 5 previas. API US$ 0. Simulador (después del código, declarado): coincide en todo con la corrida en seco (`f37/a/simulacion_reglas_a.md`; frágiles: D47 depende del año en dos cifras, Q50 pasa 1c por «Erto», D68 vuelve por «y medio» sin parsear).
- **B HECHO** (commit B): simulador ANTES del código (`f37/b/simulacion_previa.md`: R1 acorta las fichas —T16 12.74 → 2.60 s— y deja fuera a Q50 de 127 car.; R2 coloca AVISO y SILENCIO mecánicamente, 4 dependen del crítico, COLAPSO y Q50 sin salida). `pantalla_colocar` (antes `rotulista_colocar`): duración = lectura entre `callout_dur_min`/`max` sin pasar el corte; escalera de intentos (`instantes`: otro instante de la oración, la escena siguiente dentro de ella, la oración siguiente del beat) y `repartir` (reemplaza a `escena_final`): nunca al mismo tiempo + crítico «¿estorba?» en cada intento y en el otro lado (sello y recorte); lo que no entra queda «sin colocar» con cada intento. `pantalla_filtros.lectura` deja los intentos que entran (el de otra oración re-pasa candado/no dicho/spoiler). `clima.sellos_del_papel` con la misma escalera. `gfx_critic.estorba` por intento (se borraron `criticize_rotulista` y `blocks`). Papel = único camino: borrador del director (Gemini, prompt, esquema, caché, prefetch) borrado; title card del título de la partición (`gfx_layer.plan_base`); `--rotulista` ya no existe; restos de F36 (abierto 19) y muertos (abierto 13) borrados; 15 perillas que solo leía el borrador fuera (las 9 que el perfil trae, declaradas huérfanas). Renombres: `pantalla_entrada` (sin fachada), `pantalla_filtros`, `pantalla_colocar`. Runners de lab rotos borrados (6). Mapa 35 módulos, **0 muertos**. Prueba `--plan-only` con el papel de F36 (`f37/b/plan_only_papel_f36.log`): corre entero, AVISO → escena 8, INMINENTE → otro lado, D117/D17 → otro intento. Tests `test_module_f37b_colocar.py` (8). md5 `38e5ba14…`, rápida 58, amplia 804 + 5 previas (Firefox abierto al primer intento: cerrado con cierre normal, 15.6 GB).
- **C HECHO** (commit C): `m01e_pantalla` suelto para Vajont: 2 llamadas (65 940 in · 29 803 out · US$ 0.4299; reintento 66 978 · 20 103 · US$ 0.3350) = **US$ 0.7649** (tope 1.00, respaldo); 12 fichas, 8 sellos, 4 relojes, **sin tarjeta** (null en el reintento); 5 preguntas al autor (D47, T15, T39, D105, D161: «otro hecho» las 5); 0 caídas en la validación; gancho D131 en [1]; T39 de vuelta; Q43 fuera (lo descartó el autor). `--plan-only` (4 corridas; la corrida encontró dos regresiones de B, arregladas con test: el intento 3 prueba también la escena que arranca dentro de la oración siguiente —F32 §B.3— y el reparto ve el reloj ya recortado al corte): **12 de 12 fichas en pantalla, 7 de 7 picos con ficha, ninguna > 6 s** (máx. 4.73), 5 sellos (CALMA, SILENCIO, RABIA sin colocar con su lista: el crítico), 3 relojes (ch05 fuera por `TICKER_MIN`), tarjeta ✗. Simulador contra `REVISION_PAPEL.md` (`f37/c/comparacion_simulador.md` + adenda en el reporte). md5 `38e5ba14…`, rápida 58, amplia 806 + 5 previas; mapa 35 módulos, 0 muertos.
- **PARADA final F37** (`lab/hyperframes/f37/F37_REPORT.md`, revisor íntegro). Abierto entero en el reporte (22): tarjeta, el reintento reescribe todo (perdió D128, Q14, AVISO, ALARMA, tarjeta), gusto para Omar, sellos sin colocar, lo que cumplió el modelo y no la regla, D68 «y medio», spoiler por hechos, clave del perfil y huérfanas.

## 👀 Para Omar (F36): leer `data/scripts/_steps/f8s3-vajont/01e_pantalla.md` (= `lab/hyperframes/f36/c/01e_pantalla.md`), el resumen de `F36_REPORT.md` (C, D, abierto) y decidir: aceptar o revertir D2 (`04755b2`); qué hacer con D195/T85/D128 en el papel (`--plan-edit`); borrar las claves huérfanas de `misterio.json`. Nada se renderizó.

## F36 — Estructura de la capa de texto (pedido de Omar, 2026-10-26) — HECHA, **PARADA** (D2 espera a Omar)
- Handoff `lab/hyperframes/f36/HANDOFF_F36_estructura.md`. Base `1973ba1`. Un commit por parte (A→B→C→D), PARADA corta en cada una; A y D exigen diff vacío del guion. Contrato: tabla DEBERÍA de `lab/hyperframes/f34/REVISION_GUION.md`. Reporte `lab/hyperframes/f36/F36_REPORT.md`; verificador `lab/hyperframes/f36/verificar.sh <parte>`; comparador `lab/hyperframes/f36/diff_guion.py`.
- **Paso 0 HECHO:** `DECISIONES.md` tal cual (`74a309f`).
- **A HECHO** (commit A): `gfx_rotulista` partido en `rotulista_llm`, `rotulista_filtros` (`ORDEN` de filtros, el de F34: lectura antes que coherencia), `rotulista_colocar`, `clima` (+ `peak_word` de gfx_peak), `voz_datos`, `voz_utils` (parsers de español y oraciones); `gfx_rotulista` = fachada. Guion de Vajont regenerado (caché, US$ 0): **diff vacío** contra F34. md5 ch02 `38e5ba14…`, rápida 58, amplia 1025 + 5 previas. Simulador: 0/15 líneas (esperado). Mapa 43 módulos, 14 muertos.
- **B HECHO** (commit B): contador del rotulista queda (B.1), crítico antes del reparto y «¿estorba?» para sellos de clima y agua sin prompt nuevo (B.2), sello que ya salió en el video se repide una vez (B.3), agua y reloj hasta el corte − 1 cuadro (B.4), cota con cota en la vecindad (B.5), desempate con cifra (B.6), candado del gancho con la voz del video y el gancho no es pico para textos (B.7, DECISIONES 14:28), `max_chars` y reintento con el número (B.8, sin prompt), tarjeta reemplaza la intro: 3 s, todo +0.5 s, música 0 cuadros (B.9). Simulador: 6/15 (1, 5, 7, 11, 12, 15) + 2 en parte; B debía 10, cerró 5 (2 CALMA tapa rostros, 3 AVISO ya no cae, 6 D49 lupa sin visión, 9 depende de Q50, 10 COLAPSO tomado por ch04). Contrato pide AMENAZA ×2 contra B.3. Gemini US$ 0.1257. md5 `38e5ba14…`, rápida 58, amplia 1036 + 5 previas. RAM 13.6 GB antes del md5 de B (bajo la regla; el verificador ahora frena).
- **PARADA antes de C** (`F36_REPORT.md`, última sección): el pedido de Omar solo autoriza los literales de C.2 y C.3; C.1 trae otra frase literal y C.4 (`tipo: "agua"`) necesita texto nuevo en el prompt. Pregunta enviada a la sesión que lanzó la tanda; sin respuesta, no se llama a Sonnet.
- **Omar cambió el diseño (DECISIONES 18:17 y 19:54): C y D se rehacen con `lab/hyperframes/f36/HANDOFF_F36_C_D_pantalla.md`** (sesión nueva, base `bce140e`). Paso 0 (`52c7d48`): la C vieja sin commitear en `stash@{0}` «f36-c-vieja-descartada» (no borrada), DECISIONES + handoff + RESPUESTA_C + REVISION_GUION tal cual.
- **C nueva HECHA** (commit C): `script_engine/m01e_pantalla.py` (Fase 1, después de la partición; `fase1_5.run_pantalla`; suelto `python -m script_engine.m01e_pantalla <topic>`): una llamada a Sonnet con el prompt literal de C.2 (`m01e-1`, md5 `aa1ebc33…`), validación en papel, `01e_pantalla.json/.md` en `data/scripts/_steps/f8s3-vajont/` (el topic de Fase 1 de Vajont es `f8s3-vajont`, no `ba6c3cac` como dice la aclaración 1). Vajont: 59 976 tokens de entrada, US$ 0.3091, 9 fichas · 9 sellos · 4 relojes · tarjeta en papel; el reintento por 3 fichas caídas no entró por el tope de 0.50. Fase 2 lee el papel (sin modelo de texto): alineación 161/161, `ORDEN` = anclar papel, no dicho del gancho, candado, no dicho, spoiler, lectura; «nunca al mismo tiempo»; crítico «¿estorba?»; sellos del papel; `--plan-edit` edita el papel. Guion: 7 textos, 3 sellos, 4 relojes, tarjeta, 6 punches; contrato 6/13 + 1 en parte (`c/comparacion_simulador.md`). md5 `38e5ba14…`, rápida 58, amplia 1042 + 5 previas.
- **D1 HECHO** (commit D1): borrado lo de DECISIONES 18:17 y lo muerto que no toca el guion (rotulista_llm, gfx_bug/fragments/question/identity, 4 plantillas, agua/contador/lupa/fuente/íconos, Gemini de clima, crítico F4e, ediciones del plan, garantizar_pico, plan_peak, pick_zoom, 33 perillas; el perfil tolera las claves huérfanas declaradas). Guion de Vajont: **diff vacío contra C**. md5 `38e5ba14…`, rápida 58, amplia 881 + 5 previas (163 tests de lo borrado fuera, 2 nuevos). 
- **D2 HECHO** (commit D2 `04755b2`, aparte): `select_punches`, `place_emphasis` y su cadena, el sello de la palabra del pico, sfx por bloque salvo el golpe del title card, 5 perillas. Guion: **en pantalla idéntico a C (120 eventos), chequeos iguales**; el diff son las 51 filas ✂ de lo borrado + contadores por beat → **PARADA del pedido** («si D no da diff vacío»): Omar acepta o revierte `04755b2` solo. md5 `38e5ba14…`, rápida 58, amplia 833 + 5 previas (tests 1047 → 838 en la tanda). Mapa 35 módulos, **1 muerto** (el borrador del director: borrarlo toca su prompt → abierto).
- **PARADA final F36** (`F36_REPORT.md` completo, revisor íntegro). Abierto entero en el reporte: contrato 6/13 + 1 (decide Omar con el papel), reintento sin lugar en el tope, D sin cifra fuera del archivo, 6 sellos y 2 fichas del papel cortados en Fase 2, claves huérfanas de `misterio.json` para Omar.

## F34 — Reglas de pantalla corregidas (pedido de Omar, 2026-10-26) — HECHA, **PARADA** (sin render, sin aprobar)
- Handoff `lab/hyperframes/f34/HANDOFF_F34_reglas_de_pantalla.md`. Base `fc889c9`. Un commit por parte.
- **Simulación previa** (agente `simulador`, antes del código): `lab/hyperframes/f34/a/simulacion_previa.md`.
- **A HECHO** (commit A): prompt del rotulista con los 3 reemplazos de A.1 (md5 `d90ae69a…`, versión `f34-1`; el de F32 queda como `ROTULISTA_SYSTEM_F32`/`ROTULISTA_USER_F32`); gancho con todo el pool del video marcado «la narración lo dice: sí/no» (sin los `a_pantalla` de otros caps); candado con lo que dice la oración ancla, no dicho/spoiler antes que la lectura, spoiler con la voz de caps anteriores; reparto por oración en caps de una sola escena (`unidades`), el sello deja de ser fijo y no frena al reloj; reloj desde la voz si la cronología no da reloj; sellos de CLIMA (Gemini Flash, prompt literal de A.4, vocabulario `sellos_clima` del perfil, en disco: `gfx_profiles/misterio.json` fuera de git); agua desde la voz (una por cap); tarjeta fecha-hora (`9 OCT 1963 · 22:39`, T57 + T66); plan congelado (`gfx_layer.plan_congelado`: con guion aprobado el render dibuja el plan tal cual y no lo reescribe); música alineada con `--gfx` (pieza = segmento + crossfade, después de la intro) y medida en la mezcla; crítico de forma para sello de clima y agua de la voz; `.claude/settings.json` modelo `claude-opus-5-5`; `/tanda` paso 12 (cerrar tareas en segundo plano). Tests `test_module_f34.py` (18). Suite amplia 1021 + 5 previas, rápida 58, md5 ch02 sin gfx `38e5ba14…` (`lab/hyperframes/f34/a/`). Salida en texto: `lab/hyperframes/f34/a/salida_a.txt`.
- **B HECHO** (commit B `2f04030`): guion regenerado `lab/hyperframes/f34/GUION_PANTALLA.*` (Claude US$ 0.4633, Gemini 0.2392). Contra §1 (agente simulador, `b/comparacion_simulador.md`): relojes 4 + tarjeta, 2 aguas, 6 punches = §1; **5 textos de 9** (D117, T39, D192, D245 y D71 en vez de D49; faltan D118, D128 —bug del realizador que borra todo count_up—, T85 —pico solo a_pantalla—, Q50 —lectura—); **7 sellos de 8** (AMENAZA ×4). Música alineada con el title card 7/7, desvío 0 cuadros medido.
- **Cierre** (commit de cierre): `lab/hyperframes/f34/F34_REPORT.md` con la tabla del simulador y el veredicto íntegro del revisor (CUMPLE CON OBSERVACIONES). Abierto (F34_REPORT): textos 5/9 y sus causas, AMENAZA repetido y orden sello→crítico, agua de ch04 cruza el corte, tarjeta sin dibujar (intro 2.5 s vs `title_dur` 3 s), `sellos_clima` fuera de git, procesos viejos de otras tandas (grep 23064/31616/21988, bash 29824/500) sin cerrar: el permiso lo bloqueó, cerrarlos a mano.

## 👀 Para Omar (F34): leer `lab/hyperframes/f34/GUION_PANTALLA.md` y el resumen de `F34_REPORT.md`; decir «aprobado» o qué cambiar. Nada se renderizó.

## F33 — Infraestructura: procedimiento, compuertas y mapa (pedido de Omar, 2026-10-26) — HECHA, **PARADA** (sin render, sin cambios del pipeline)
- Handoff `lab/hyperframes/f33/HANDOFF_F33_infraestructura.md`. Base `cd60c74`. Un commit por parte.
- **A HECHO** (commit A): `DECISIONES.md` y `lab/hyperframes/f32/ENTRADA_ANALISTA_2026-10-26.md` al repo tal cual; `CLAUDE.md` con la línea de DECISIONES; `test_constantes_con_origen.py` en modo inventario (101 constantes numéricas en GfxRules/GfxRenderSettings/TransitionRenderSettings; 35 con origen: 33 «identidad F3» = igual al token del perfil, `crossfade_frames` y `workers` por DECISIONES; **66 sin origen** → `lab/hyperframes/f33/a/inventario_constantes.md`; solo comentarios, ningún valor). `CONSTANTES_ESTRICTO=1` lo vuelve estricto.
- **B HECHO** (commit B): compuerta del render. `fase2b <topic> --aprobar-guion "Omar <fecha>"` (CC solo si el prompt de Omar dice «aprobado») escribe `aprobado: {por, fecha, md5_planes, planes}` en `GUION_PANTALLA.json` (`script_engine/aprobacion.py`, solo stdlib); hook `.claude/hooks/guard_render.py` (en `settings.json`) bloquea `fase2b … --gfx` sin guion, sin `aprobado` o con planes cambiados; `--plan-only`/`--plan-edit`/`--aprobar-guion`/`--only-cap --gfx-debug`/sin `--gfx` pasan; `--dry-run` y batch con `--gfx` se bloquean. Vajont hoy: bloquea (`lab/hyperframes/f33/b/prueba_guard_render.txt`). Límite: no ve los runners de lab que llaman a fase2b por dentro.
- **C HECHO** (commit C): `/tanda` (`.claude/commands/tanda.md`, copia en `~/.claude/commands/`), skills `guion-de-pantalla` y `simular-reglas` (solo en el repo), agente `simulador` (`.claude/agents/`), `lab/tools/simular_regla.py` (predicado sobre los eventos del guion → propuestos → cortados → quedan + 3 ejemplos). Ejemplo: «el sello no repite la voz» corta 10 de 10 sellos de Vajont (`lab/hyperframes/f33/c/simulacion_sello_repite_voz.md`). `revisor-handoff` ya era de usuario (`~/.claude/agents/`).
- **D HECHO** (commit D): **`lab/MAPA_MODULOS.md`/`.json`** (37 módulos: `script_engine/gfx_*.py`, `aprobacion`, `gfx_config`, `fase2b`, `transition_config`, `transition_applier`, plantillas, `m01a_escaleta`, `m01d_particion`, `music_intensity`; 117 aristas; 14 muertos con la fecha en que dejaron de correr), generado por `lab/tools/mapa_modulos.py` sobre los hechos del código (`lab/tools/mapa_hechos.py`: AST + git). Hook `guard_mapa` avisa si un commit toca `gfx_*.py`/`fase2b.py` sin el mapa.
- **E HECHO** (commit E): suites (amplia 1003 + 5 previas, rápida 58) y md5 ch02 `38e5ba14…` en cada commit; **hook de render probado en vivo con Vajont: bloquea** (`lab/hyperframes/f33/e/prueba_en_vivo.txt`). En E se arregló un falso positivo del hook (heredocs que solo mencionaban el render) y, después del revisor, el hueco del primer arreglo (prefijos como `timeout`): el hook final saca los heredocs, ignora comandos de texto y mira detrás de prefijos y dentro de `bash -c`. Reporte `lab/hyperframes/f33/F33_REPORT.md` (inventario de constantes, `/tanda` y skills pegados, mapa pegado, muertos, revisor íntegro: CUMPLE CON OBSERVACIONES). API US$ 0.
- **Abierto (F33_REPORT):** 66 constantes sin origen para que Omar y el analista las clasifiquen; DECISIONES leído por el código (no hecho); runners de lab y scripts `.sh`/`.ps1` no pasan por `guard_render`; lock de planes en el render (tanda de correcciones); la página del flujograma la hace el analista con `lab/MAPA_MODULOS.json`.

## F32 — El guion de pantalla (pedido de Omar, 2026-10-26) — HECHA, **PARADA** (sin render: el render se pide aparte cuando el guion esté aprobado)
- Handoff `lab/hyperframes/f32/HANDOFF_F32_guion_de_pantalla.md`. Base `0253672`. Tres commits (A, B, C), uno por parte (Omar; el handoff pedía uno por arreglo en B). **Esta tanda no renderiza.**
- **A HECHO** (commit A): `fase2b --plan-only` (director + rotulista + reglas + crítico, sin navegador ni render; implica `--gfx --reuse-visuals`; el -g30 de los 7 caps en paralelo, el plan en fila) → `output/<id>/GUION_PANTALLA.md/.json` (`script_engine/gfx_guion.py`: eventos en el tiempo del mp4, ✂ lo cortado con quién y por qué, resumen por beat, 8 chequeos) + `_fase2b_work/mezcla_preview.wav` (voz + música + sfx con el grafo del render). `fase2b --plan-edit archivo.json` (ediciones en `_fase2b_work/plan_edits.json`; el rotulista sale de caché). Vajont en estado v5: 161 s de pared, US$ 0 Claude, línea de base en `lab/hyperframes/f32/a/GUION_PANTALLA_A.*`. **Hallazgo B.1:** la voz de v5 no pierde el ataque (es el mp3 corrido 3.000 s exactos); la «rampa» de v3b era el golpe del title card (sfx a 0.05 s) encima de la voz.
- **B HECHO** (commit B, un commit para los 8 arreglos): ch01 sin pre-roll y la música del cap suena desde su title card (B.1); pregunta = caracteres ÷ 15 cps (B.2); si no cabe antes del corte, arranca en la escena siguiente (B.3); `a_pantalla` con carta/acta/informe/documento → recorte (B.4); 2 `a_pantalla` por beat y `a_pantalla` en el pico (B.5); sellos por tema de la oración con el filtro del catálogo y sin `punch_in` del director (B.6); prompt del rotulista + 1 línea (md5 `c9231e24…`; el de F29c queda como `ROTULISTA_SYSTEM_F29C`), cifra → agua/contador (B.7: el modelo no devuelve `unidad`/`valor` porque el formato de salida del USER no los nombra → respaldo: se leen del texto); ficha con el dato a `question_px` y la etiqueta con placa (B.8). Vajont: Claude US$ 0.2668, `a_pantalla` 2/5 (D128, D245), inicio de voz ✓ 6/7 (ch07 sin rampa), preguntas ✓ 7/7. Suite amplia 992 + 5 previas, rápida 58, md5 ch02 `38e5ba14…`. Evidencia `lab/hyperframes/f32/b/`.
- **C HECHO** (commit C): **guion `lab/hyperframes/f32/GUION_PANTALLA.md/.json`** (200 eventos, 82 propuestas cortadas con quién y por qué) y **mezcla `lab/hyperframes/f32/mezcla_preview.wav`** (1055.8 s, 186 MB, fuera de git). `--plan-only` 162 s con el rotulista en caché (302 s con Claude). Chequeos: preguntas ✓ 7/7, inicio de voz 6/7 (ch07 sin rampa), `a_pantalla` 2/5 (faltan D117 candado «1943», Q50 y D192 lectura), 2 textos en pantalla (D128, D245), 10 sellos, 5 caps sin texto, dos bloques en la escena 0 de ch01 y ch07 (title card + sello del pico). Reporte `lab/hyperframes/f32/F32_REPORT.md` (revisor íntegro: CUMPLE CON OBSERVACIONES). Costos: Claude US$ 0.2668 de 1, Gemini 0.0016 de 0.5. Suite amplia 992 + 5 previas, rápida 58, md5 ch02 sin gfx `38e5ba14…`.
- **Pendientes de Omar/analista (F32_REPORT):** la música va adelantada respecto de los caps (previo: 2.5 s en ch01 hasta 14.8 s en ch07, y con ella el mapa de intensidad); el render tiene que tomar los planes aprobados (el crítico de sellos del render mira el bloque dibujado); `unidad`/`valor` no llegan del modelo (el formato del USER no los pide); B.4 también alcanza a D117 («dato de acta»); el sello «vida» como tema muerte (léxico del perfil); las lecturas de la rampa (umbral = `duck_threshold`).

## 👀 Para Omar (F32): leer `lab/hyperframes/f32/GUION_PANTALLA.md` y oír `lab/hyperframes/f32/mezcla_preview.wav`; decir «render» o «cambiá X» (`fase2b f8s3-vajont-f30 --plan-edit archivo.json`)

## 👀 Para Omar al despertar (tanda nocturna F29c → F30b → F31) — mirar en este orden
1. **`output/f8s3-vajont-f30/f8s3-vajont_final_gfx_v4.mp4`** — Vajont con el rotulista por beat (F29c): solo 2 textos en todo el video (ch06 13:01 «1.910 personas», ch07 15:38 «Dos habían muerto y uno se suicidó.»).
2. **`output/f8s3-vajont-f30/f8s3-vajont_final_gfx_v5.mp4`** — lo mismo con transiciones por relato, caps unidos a negro y title card con 3 s sin voz (F30b).
3. **`lab/hyperframes/f29c/BLOQUES_v4.jpg`** — los bloques (y el cortado por el crítico) con la voz al lado.
4. **`lab/hyperframes/f30b/COSTURAS_v5.jpg`** — las 6 uniones entre caps, 12 cuadros cada una.
5. **`lab/hyperframes/f31/VARIANTES_ch06.jpg`** — las variantes de forma de ch06 a 360 px (elegir: entrada/salida V1–V3, sello S1–S3 con/sin placa, reloj R1–R2); clips `lab/hyperframes/f31/ch06_*.mp4`.
Decisiones que esperan a Omar: ver «Pendientes de Omar» en cada reporte (F29c: un texto por beat con dos `a_pantalla`, lectura vs corte de escena, pico = 0 en todos los caps; F30b: fadewhite sin gfx, arranque largo de ch01, música muda en el title card; F31: cuál variante).

## Tanda nocturna F29c → F30b → F31 (pedido de Omar, 2026-10-26) — HECHA, **PARADA**
- Prompt `lab/hyperframes/f29c/PROMPT_CC_tanda_nocturna_F29c_F30b_F31.md`. Base `d7fac3c`.
- **F29c HECHO** (A `cc3f079`, B = commit siguiente). Reporte `lab/hyperframes/f29c/F29c_REPORT.md` (revisores A y B íntegros: CUMPLE CON OBSERVACIONES ×2). Prompt A.5 md5 `7dafbb96…`. **v4 `output/f8s3-vajont-f30/f8s3-vajont_final_gfx_v4.mp4`** (1009.7 s, 993 MB, pared 30.9 min vs v3b 37.1), hoja `lab/hyperframes/f29c/BLOQUES_v4.jpg`. **Solo 2 textos en pantalla** (ch06 D128, ch07 D32): 16 propuestos, 8 fuera por «sin tiempo de lectura» (el corte de escena), 2 por cantidad, 3 por candado, 1 por el crítico (T61 persona). `a_pantalla` 1/5. B.4 todo 0. Claude US$ 0.234, Gemini 0.0006. **Pendientes de Omar:** dos `a_pantalla` en un beat (D128/D192), lectura vs corte de escena (el rotulista no ve los cortes), pico = 0 en todos los caps, etiqueta de `hecho` con el año de la fuente, `persona` casi siempre cortada por el crítico.
- **F30b HECHO** (3 commits A/B/C). Reporte `lab/hyperframes/f30b/F30b_REPORT.md` (revisor íntegro). **v5 `output/f8s3-vajont-f30/f8s3-vajont_final_gfx_v5.mp4`** (1032.4 s, 968 MB, pared 35.4 min). Transiciones por relato (`gfx_style.transiciones_por_relato`: lupa→cut, pico→zoom_punch, cambio de beat / salto de fecha→dissolve 20 f, cierre→dip 10 f, resto cut; los 6 punch por el stitch). Caps unidos a negro (`concat_windowed(negro_frames)`, solo con --gfx): 0 cuadros planos no negros en las 6 fronteras; el gris era el medio del `fadewhite`. Pre-roll del title card de 3 s (`gfx_rules.title_pre_roll`, solo con --gfx): voz `.mp3` 7/7 idéntica, cada segmento +3.000 s, bloques +90 cuadros. Chascada `«»…` fuera del `.ass` (solo --gfx). Hoja `lab/hyperframes/f30b/COSTURAS_v5.jpg`. Claude 0, Gemini 0.0021 (visión de los caps híbridos y crítico de sellos: cachés por bytes de cuadro). md5 ch02 sin gfx `38e5ba14…`; suite amplia 970 + 5 previas. **Pendientes:** `fadewhite` sigue en el camino sin --gfx; la API no fue 0.
- **F31 HECHO** (1 commit). Reporte `lab/hyperframes/f31/F31_REPORT.md` (revisor íntegro: CUMPLE CON OBSERVACIONES; su falla en los cuadros de entrada de la ficha, corregida). Flag `fase2b --forma-variante V,S,R` (V1–V3 entrada/salida de ficha y recorte, S1–S3 sello ±P placa, R1–R2 reloj); `gfx_rules.forma_variante = ""` → **sin el flag el HTML es byte a byte el de antes**. 11 corridas `--only-cap ch06` (rc 0, US$ 0; las 3 repetidas y R1 dan el mismo mp4: render determinista; ch06 no tiene reloj ni recorte), clips `lab/hyperframes/f31/ch06_*.mp4` (15.5 s, sin trackear), hoja `VARIANTES_ch06.jpg`, medidas (dato de la ficha 6.0:1, kicker rojo 1.2:1 y 5.4 px a 360, sello 1.1–1.7:1). **Ninguna variante es default: Omar elige → F31b.** Los mp4 de las corridas (3.7 GB) quedan en `lab/hyperframes/f31/corridas/` sin trackear.
- **Costos de la tanda:** Claude US$ 0.234 de 2 (todo en el rotulista de F29c) · Gemini US$ 0.0027 · ElevenLabs 0. Commits: F29c `cc3f079`, `e852788` · F30b `7d0d0e5`, `6c5092c`, `a19dbbc` · F31 = el último. Sin merge, sin publicar, sin borrar.

## Tanda F29b A → F30 A–D → F29b B (pedido de Omar) — HECHA, **PARADA** (el analista lee `lab/hyperframes/f29b/BLOQUES_v4.jpg`)
- Prompt `lab/hyperframes/f30/PROMPT_CC_tanda_F29b_F30.md`; handoffs `lab/hyperframes/f29b/HANDOFF_F29b_rotulista.md` y `lab/hyperframes/f30/HANDOFF_F30_render_rapido.md`. Sobre `3b47cd5`.
- **Resultado y PARADA:** reportes `lab/hyperframes/f30/F30_REPORT.md` (revisor íntegro: CUMPLE CON OBSERVACIONES) y `lab/hyperframes/f29b/F29b_REPORT.md` (revisor íntegro: CUMPLE CON OBSERVACIONES; abiertos para antes de B: el primer token de «persona» sin candado de nombres, la ventana −0.3/+0.35 s, sin test de integración de `apply_gfx` con rotulista, el tope del prefetch en paralelo). **Vajont v3b** `output/f8s3-vajont-f29/f8s3-vajont_final_gfx_v3b.mp4` (copia del topic `f8s3-vajont-f30`): mismos bloques y transiciones que v3 (7 planes idénticos, API 0), pared 63.9 → 37.1 min, gfx 59.2 → 32.4 min (metas ≤ 20/≤ 30 no alcanzadas). Se frenó la etapa 3 porque el SSIM, leído estricto, no da: A.4 ch06 esc. 1 = 0.9485 con el código final; en D 4 escenas < 0.95 (dos son la última escena de ch02/ch05, donde v3 mostraba DepthFlow por un redondeo de `compose_sparse`) y el resto de ch04 0.978. Lo de la etapa 3 quedó preparado sin correr: `lab/hyperframes/f29b/b/` (hoja, runner, tabla) y la bandera `fase2b --rotulista` como `b/fase2b_rotulista_flag.patch`. `gfx_rules.rotulista` sigue en False.
- **F29b B (2026-10-26, Omar aceptó F30 y pidió B):** arreglos `7e704de`: candado de «persona» con nombre y cargo en el texto fuente; tope de Claude con las llamadas en vuelo; `fase2b --rotulista` y `--rotulista-tope`. Corrida sobre `f8s3-vajont-f30` (planes de v3b apartados como `*.resolved.v3b.json`): rotulista de los 7 caps en paralelo (26.8 s), planes en orden, render `--only-cap ch03` (gfx 294 s) y `ch06` (340 s). En los planes quedan **8 bloques** (ch01 0, ch02 1, ch03 4, ch04 1, ch05 0, ch06 2, ch07 0; dibujados los 6 de ch03 y ch06): 14 propuestos, 3 fuera por A.4, 3 cortados por el crítico. Muñones, cifras sin etiqueta y números dichos por la voz: 0. **`a_pantalla` 3/5**: D245 salió con las liras pero lo cortó el crítico; Q50 quedó fuera por largo (cita de 15 palabras). Hoja `lab/hyperframes/f29b/BLOQUES_v4.jpg`. Claude US$ 0.291 de 2 (A+B), Gemini 0.003. Sin `_v4.mp4` del video entero (el pedido fue `--only-cap`). Reporte `lab/hyperframes/f29b/F29b_REPORT.md` (revisor de B íntegro: CUMPLE CON OBSERVACIONES; riesgo: los cortes del crítico en caps sin render, D245 y Q44, miran la foto sola).
- **F29b A (rotulista, sin render):** `script_engine/gfx_rotulista.py` (prompt literal md5 `50e6ae74…`, Sonnet 5.5 medium, cruda en `_fase2b_work/rotulista_chNN.raw.json`, A.4 determinista, colocación, prefetch de los 7 caps en paralelo), pico único (`music_intensity.beat_pico_de_cap`), crítico del rotulista (`gfx_critic.criticize_rotulista`, después del respaldo: `gfx_realizador.cerrar`), excepción del candado literal para `rotulista: true`. **`gfx_rules.rotulista = False`** por defecto (se prende en la etapa 3). Crudas de ejemplo ch03/ch06 en `lab/hyperframes/f29b/a/` (Claude US$ 0.114). Tests `test_module_f29b_rotulista.py` (19); suite amplia 940 verdes + 5 previas; md5 ch02 sin gfx (`--sw-encode`) = `38e5ba14…`. Ojo: `fase2b.py` no corre con `python -I fase2b.py` (sin el dir en sys.path): usar runpy o sin `-I`. Fix `f6527a1`: `--rotulista-modelo` (GfxRules es frozen).
- **F30 A (push safe con ffmpeg):** `script_engine/gfx_safe_bake.py` cuece cada escena safe desde su PNG con `perspective` (eval=frame, subpíxel) en `public/base_cocido.mp4`; la escena cocida va como `<video>` en HF y no abre ventana (`event_windows(safe_windows=False)`). `zoompan` (el handoff) descartado por medida: recorte entero → SSIM 0.77–0.83 (×1.08) o 166 MB/cuadro (×6). En Vajont **todas** las escenas flux son safe (identidad), no la mitad. ch06 (copia del topic `f8s3-vajont-f30`, planes de v3 idénticos, API 0): cobertura 100 → 31 %, HF 593 → 259 s, bake 148 s, **stitch 50 → 135 s** (cadena de 30 xfade), total 728 → 686 s; SSIM por escena 0.951–0.980, mínimos solo en cortes (1 cuadro de seek de `<video>` en ventanas HF). Suite amplia 945 + 5 previas; md5 ch02 sin gfx `38e5ba14…`. Commit `94d9496`.
- **F30 B (transiciones en el stitch):** las transiciones ya no abren ventana; la que toca una ventana (o sin aire) entra y la dibuja HF (`event_windows`, `stitch_transitions`). Stitch reescrito como segmentos exactos a cuadro + UN `concat` (la cadena de xfade era el costo): dissolve = último cuadro congelado + `xfade fade` (lineal; HF es sine), dip = `fade` a negro / desde negro, flash = `drawbox` blanco por cuadro, cut_punch = `zoompan`. ch06: 4 ventanas, cobertura 16 %, HF 127 s, stitch 93 s, **total 513 s** (v3 728); transiciones idénticas (13/15 en el stitch); SSIM ±1 s de 5 cortes 0.957–0.979. Los mínimos (0.63–0.81) son 4 dissolves desde un push de rostro: **v3 tenía un salto** (freeze del templater centrado; `_freeze_img`), ahora sigue el último cuadro real (`corridas/b_stitch/dissolve_rostro_46s.jpg`). Suite 949 + 5; md5 `38e5ba14…`. Commit `537416f`.
- **F30 C (medidas):** workers 5 → 8 en ch06: HF 127 → 157 s, RAM libre mín. 13.0 → 12.0 GB → **queda en 5** (`fase2b --gfx-workers N` para medir). Stitch + grade con **NVENC cq 23** (`gfx_render.stitch_encoder`, vuelve a libx264 si NVENC falla): 86 → 52 s, 1.25 → 0.19 GB, SSIM 0.98 contra x264. Costura (solo medida, sin arreglo): el cuadro gris plano (luma 140) + 3 blancos aparece por primera vez en `_concat_video.ts`, fronteras ch01→ch02 y ch03→ch04 (`fadewhite` de `whip_pan_flash`, transition_applier); en el mp4 final +75 cuadros. Suite 951 + 5; md5 `38e5ba14…`.

## F29 — El gfx obedece a la escaleta (realizador) · sfx ElevenLabs · Sonnet vs Flash — HECHO, **PARADA** (Omar mira la v3 y la hoja de bloques)
- Sobre `e971a8f`. Handoff `lab/hyperframes/f29/HANDOFF_F29_gfx_realizador.md`. Reporte `lab/hyperframes/f29/F29_REPORT.md` (revisor íntegro: CUMPLE CON OBSERVACIONES).
- **B** (`6eb6fda`): 15 sfx con ElevenLabs (−20 LUFS, techo −1 dBFS; los cortos quedan en −22…−26), `make_sfx.py` con caché `_prompts.json`; los de F2 en `script_engine/sfx/_f2_sintetizados/`. US$ 0.037. En mezcla +0.0–0.2 LU: casi no se oyen; ganancias sin recalibrar (Omar escucha).
- **A** (`2fcd603`): `script_engine/gfx_realizador.py` — ventanas por beat (`gfx_beats_chNN.json`), candidatos = a_pantalla en su beat + datos no dichos, topes por función y 5 por cap, sello solo el del pico (filtro; el diccionario palabra→ícono NO se tocó), pregunta = `cierre`, duración por texto, crítico parejo, `gap_fill` off (`gfx_rules.gap_fill`), `gfx_rules.realizador` on. Sin escaleta, camino viejo.
- **C** (`115d999`): **timeout render gfx 1500 s, NVENC cq 23** (Vajont 1.21 GB vs 1.6 GB con cq 19). Pico desde la escaleta si gfx_peak no da; rótulo del pico sin ids repetidos. **Vajont v3: `output/f8s3-vajont-f29/f8s3-vajont_final_gfx_v3.mp4`** (copia del topic `f8s3-vajont-f29`), `lab/hyperframes/f29/BLOQUES_v3.jpg`. F27 → F29: bloques 35 → 22, sellos 15 → 4, spoilers 2 → 0, pico con bloque 1/7 → 7/7. Reensamble 63.9 min; gfx por cap ≤ 781 s. Gemini US$ 0.012. Intento 1 apartado (`_v3_intento1.mp4`, `_bak_c_intento1/`).
- **D** (`1711e88`): `gfx_pool.FORMA_CALL`; Sonnet 5.5 eligió igual que Flash en los 4 recortes de ch05/ch06 → mp4 idénticos byte a byte. Claude US$ 0.0028. El modelo solo decide la cláusula del recorte; tipo/lado/duración son deterministas. Hoja `lab/hyperframes/f29/D_flash_vs_sonnet.jpg`. Copia `output/f8s3-vajont-f29d/`.
- Suite amplia 921 verdes + 5 previas. **Abierto:** rótulos del pico que repiten la voz (ch02 Q53, ch03 T18, ch07 Q13: el respaldo de `garantizar_pico` no filtra «ya dicho» y el crítico corre antes); sello de ch04 en la palabra del pico pero 49 s antes; rótulo + sello juntos en el pico de ch01/02/07; rótulo largo del pico de ch06 se sale del cuadro; los `chNN_gfx.mp4` intermedios pesan ~1.2 GB cada uno.

## F28 — Paleta musical (A, B, C) — HECHO, **PARADA** (Omar escucha la v2 de Vajont)
- Sobre `4e18e8a`. Handoff `lab/hyperframes/f28/HANDOFF_F28_paleta_musical.md`. Reportes `F28A_REPORT.md` (parte A) y `F28_REPORT.md` (B y C; revisor íntegro: CUMPLE CON OBSERVACIONES). Elección del analista: `ELECCION_F28_12_pistas.md`.
- **A** (`22582d7`): 30 pistas generadas, medidas y escuchadas por Gemini (`audio_library/_paleta_f28/`, fuera de git). ElevenLabs US$ 13.95 (precio publicado; Omar confirma en el panel), el plan admite 2 pedidos a la vez.
- **B** (`e3fd23a`): las 12 elegidas en `audio_library/<intent>_f28_<a|b>.mp3` (recortadas de fade, 157–174 s, loop con acrossfade de 3 s, nivel = efectivo de la curated del intent); **curated en `audio_library/_retiradas/`**. m07: con la paleta el matcher elige entre las 2 sin umbral y nunca genera. `script_engine/music_intensity.py`: mapa silencio/fondo/sube/golpe por cap, aplicado como envolvente en fase2b (si hay escaleta). **Vajont v2: `output/f8s3-vajont/f8s3-vajont_final_gfx_v2.mp4`** (solo audio, 37 s de mezcla; con música +0.2 LU sobre la voz; ch04/ch05 +0.6/+0.8 por los «sube»). Sin escuchar.
- **C** (`8e35b25`): **NVENC por defecto** (`--sw-encode` para libx264; **el candado md5 de ch02 sin gfx se mide ahora con `--sw-encode`**), clips con 6 workers. **gfx en paralelo DESCARTADO** (`GFX_PARALELO = 1`): con 3, 4 de 7 caps cayeron a base_clip por el timeout de 900 s y la RAM libre bajó a 1.4 GB; con 2, el gfx de cada cap tardó 1.4–1.6×; Omar canceló la 2.ª corrida. **Re-render completo NO medido.** Restos fuera de git: `output/_bak_f8s3-vajont-f28c_run1/`, `output/f8s3-vajont-f28c/` (copia del topic).
- Suite amplia 909 verdes + 5 previas. Abierto: escuchar la v2; `test_module_40_volumen_por_track.py` (smoke manual) busca las curated en `audio_library/`; con NVENC el mp4 pesa ~2.7× más; el timeout de 900 s del gfx está al borde en fila.

## F27 — Que salga Vajont + tres cortes en la reparación — HECHO, **PARADA** (Omar mira el video)
- Sobre `26c0065`. Handoff `lab/hyperframes/f27/HANDOFF_F27_vajont_sale.md`. Reporte `lab/hyperframes/f27/F27_REPORT.md` (revisor íntegro: CUMPLE CON OBSERVACIONES).
- **VIDEO:** `output/f8s3-vajont/f8s3-vajont_final_gfx.mp4` — 1009.1 s (16.8 min), 2560×1440, 606 MB, gfx en los 7 caps, música curada. **No publicado** (fase3 no se corrió). Hoja de contactos `lab/hyperframes/f27/b/hoja_contactos_vajont.jpg`.
- **A** (`b181889`, 0 API): `gemini_helpers` (respuesta sin texto = fallo de parseo; `finish_reason`/`block_reason` en log y dump); m03 `_fluidify_item` atrapa el `ValueError` por imagen y, si los 3 intentos vuelven vacíos, la imagen sigue con los slots sin tejer (**backstop nuevo: el revisor lo marca como lógica más allá del `except`; Omar tiene que aceptarlo**); reparación (e) quita el nombre y deja la oración (`guion_v4.PEDIDO_E`); editor m01c fuera de `reparar` (`fase1_5 --editor`); `PALABRAS_POR_SEG` 2.4. Suite 888 verdes + 5 previas.
- **B** (`6a65ccb`): m03 en el 1.er intento; cap 1 con 37 respuestas vacías de Flash `PROHIBITED_CONTENT` → 3 imágenes (#3–#5 del gancho) por el backstop, **para que Omar las mire** (`b/cap1_backstop_3_4_5.jpg`; la #5 es un primer plano de cara). 92 imágenes (0 re-hechuras), 2 Veo, render 128 min (Firefox cerrado con cierre normal, RAM 17.9 GB). Gemini US$ 1.62 de 4, fal 3.70, Claude 0; foto madre GPT ×2 sin medir.
- Para revisar en el video: un rótulo gfx con inglés mal formado (≈ 4:00, cap 3) y un cap flux con «anchor matching falló — fallback uniforme».

## F26 — Nocturno: escaleta f26-1, primer video (Vajont), workers, hooks, ficha de Opus con forma — HECHO salvo B (**PARADA en m03**), **PARADA final**
- Sobre `c80e601`. Handoff `lab/hyperframes/f26/HANDOFF_F26_nocturno.md`. Reporte `lab/hyperframes/f26/F26_REPORT.md` (revisor íntegro: CUMPLE CON OBSERVACIONES). Total US$ 10.80: Claude 7.97 (A 5.66 de 8, E 2.32 de 4), Gemini 2.42 de 5, ElevenLabs 0.41, imágenes 0.
- **A** (`16900bd`): escaleta f26-1 (bloque `2e67791c…`; f25-1 = `SYSTEM_V2_F25_1`). Kyshtym fS2: kE1 pasa en la 2.ª pasada, kE2 en la 1.ª; ninguna promesa adelanta; antagonistas sin paréntesis; sin `a_pantalla` repetido. gkE1 2,168 palabras 0 bloqueantes; gkE2: la reparación (e) corre sola pero BORRA la oración (no deja el rol) y el editor m01c (corre porque el crudo tenía bloqueante) recorta 98 palabras y se lleva la promesa del gancho → para el analista.
- **B** (`e24c57b`): PARADA en m03 (falló dos veces). Hecho: topic `f8s3-vajont` en `data/topics_db.json` (respaldo `topics_db.pre_f26.json`; 4a–4e; título «Vajont: la montaña que caminaba»), pasos viejos en `_steps/f8s3-vajont/_pre_f26/`, partición sin recorte (ningún párrafo movido), voz v4 MS Narrador **980.8 s = 16.3 min** (`output/audio/f8s3-vajont/`), música fija a los `*_curated`, plan de 92 imágenes a 10.75 s. Falla: el cap 1 (gancho, la niña en la cama) → Gemini Flash devuelve respuesta sin texto y `gemini_helpers._try_json_parse` hace `None.strip()` (`b/m03_traceback.txt`). Sin imágenes, sin render, sin video. Para seguir: decidir el arreglo (None como fallo de parseo en `_try_json_parse`, o nota de gancho) y `python -I lab/hyperframes/f26/b/f26b_produccion.py --etapa guion` (reusa voz y música) → `imagenes` → `render` (Firefox cerrado, RAM > 14 GB).
- **C** (`16def01`): R2/R3 con hilos (`research_v3.WORKERS = 8`, `topic_researcher --workers N`), mismo manifest/pool que en fila; `cost_tracker` con lock; `fase1_5 --temas a,b,c` (un proceso por tema, implica --batch). R3 latencia simulada 16.7 → 2.8 s. Suite amplia **877 verdes + 5 previas**.
- **D** (`40a434d`): hooks en `.claude/settings.json` + `.claude/hooks/` (guard_git, suite_rapida, md5_prompt, tope_tanda), prueba 22/22, README. **Activos**: todo `git commit` corre la suite rápida; `git add`/`commit` de `.env`, `config.py`, `lab/_gpt_probe_analista/` o una llave queda bloqueado.
- **E** (`c343954`): Opus 5.5 con los nombres de campo en el pedido → 16/17 problemas (sin forma: 58/71; Sol fS2: 18), cifras 29/46; cuesta 3–4× Sol. No cambia producción.

## F25c — Escaleta con Fable por defecto (f25-1), guion v5.4, largo 2200 · Kyshtym y Vajont — HECHO, **PARADA**
- Sobre `187166a`. Reporte `lab/hyperframes/f25c/F25c_REPORT.md` (revisor íntegro: CUMPLE CON OBSERVACIONES). Claude US$ 11.43 de 14, pared 1,388 s.
- Producción: `m01a_escaleta.DEFAULT_MODELO_ESCALETA = claude-fable-5-1` (`call_escaleta`, medium; Sol con `modelo=` / `fase1_5 --modelo-escaleta`); escaleta f25-1 (`9325ad38…`; la f24-1 queda `SYSTEM_V2_F24_1`); guion v5.4 `f25-1` (`2f66c1e0…`; el v5.3 con `system("f23-1")`); `video_length.max_words` 2200 y el bloqueante (c) del tope pasa a `metricas["largo"]`. **`config.py` local también en 2200 (no se commitea): en otra máquina hay que cambiarlo.** Suite 868 verdes + 5 previas.
- Corrida: 1 de 2 escaletas por tema (kE1 y vE1 rechazadas por `a_pantalla` repetido / antagonista con paréntesis). gkE2 2,006 palabras, 1 bloqueante (Q20 sin verificar con nombre); gvE2 2,355, 0 bloqueantes, 18 citas. La promesa pasa literal al gancho; la de Kyshtym sigue adelantando.

## F25b — ficha_caso con --modelo; Opus 5.5 ×2 contra Sol ×2 (Kyshtym, pool F23) — HECHO, **PARADA**
- Sobre `b2db299`. Reporte `lab/hyperframes/f25b/F25b_REPORT.md` (revisor íntegro: CUMPLE CON OBSERVACIONES). Claude US$ 2.57 de 6, OpenAI US$ 0.65 de 1, pared 474 s.
- `ficha_caso`: `call_for(modelo, crudo=, post=)`, `run(modelo=)`, `esfuerzo_de`, CLI `python -m researcher_steps.ficha_caso <topic> --modelo …`; Claude por claude_helpers (stream, 100k, medium, sin esquema), respuesta cruda en `_steps/<topic>/ficha_respuesta_cruda.json`. Prompt y chequeo sin tocar. Suite 863 verdes + 5 previas.
- Resultado: Opus termina (53–60k tokens, US$ 1.2–1.4) con arcos más concretos, pero el chequeo le saca 58/71 ítems y le deja 0 cifras: sin esquema usa otros nombres de campo (`fuente.ids`, `que_cuenta`, `id`). Sol: 8/18 problemas, US$ 0.32. La ficha sigue en Sol hasta normalizar campos o dar la forma en el pedido.

## F25a — Modelo de la ficha y de la escaleta (Kyshtym, pool F23, en paralelo) — HECHO, **PARADA**
- Sobre `b27f54c`. Reporte `lab/hyperframes/f25a/F25a_REPORT.md` (revisor íntegro: CUMPLE CON OBSERVACIONES). Claude US$ 13.57 de 15, OpenAI US$ 1.37 de 4, pared 2,637 s (suma de 4 corridas).
- Ficha: Sol fS1/fS2 OK (9–11 problemas); Fable ninguna (HTTP 400 por el esquema; 2 cortadas en 32k; fF1 con 100k terminó en 46k tokens pero el JSON no se leyó; fF2 frenada por el tope). Escaleta (las 4 sobre fS2): Sol eS1 OK (1·1·2·2·1·3·3), eS2 rechazada; Fable eF2 OK (81 ids, 4.8 apoyos/beat), eF1 rechazada. Guiones Fable: gS1 1,499 palabras 0 bloqueantes; gF2 2,047 (bloqueante de tope). Decisión: Sol en ficha y escaleta.
- Regla de Omar en `claude_helpers.py`: max_tokens 100 000 con streaming (`leer_stream`), `ESFUERZO_POR_ETAPA` (guion high; ficha y escaleta medium), `SALIDA_GRANDE` sin esquema + `json_del_texto`. Suite 860 verdes + 5 previas.

## F24 — Fuentes que se acumulan, beats repartidos, dos temas nuevos — HECHO, **PARADA** (el analista lee los dos guiones y la tabla de la fase 1 y le da a Omar la nota 1–10)
- C (sin tocar producción, `f24_corridas.py`): **Pennhurst** `4ac37187-pennhurst` (1908–1987 prolongado; verde 236/37/25/108/40; humano Terri Lee Halderman; guion Fable 1,435 palabras, 0 bloqueantes, 2 citas) y **Vajont** `f8s3-vajont` (1963 puntual; verde 245/45/23/78/52; humano Micaela Coletti; 1,755 palabras, 1 bloqueante por el tope de 1700 — la reparación no entró en el tope de 1.20). Escaletas con 1–3 beats por cap desde la 1.ª pasada. Tanda US$ 8.27 de 14.00. Reporte `lab/hyperframes/f24/F24_REPORT.md` (revisor íntegro: CUMPLE CON OBSERVACIONES), `compara_f24.html`.
- D (pedido de Omar): R3 con claude-sonnet-5-5 sobre los 8 docs de Kyshtym F23 → 167/59/12/34/24 ítems, 30 citas verificadas (Gemini 21), 44 descartados (67), US$ 0.97 (Gemini 0.59), 434 s; nombres rusos en transcripción española y duplicados sin unir. `lab/hyperframes/f24/d_r3_sonnet/`.
- Nota de Omar: Fable en cualquier escaleta futura con max_tokens 32 000 (F1 se cortó en 16 000).
- Sobre `03370af`. Handoff `lab/hyperframes/f24/HANDOFF_F24_fuentes_beats_dos_temas.md` (md5 `7ccd8f35…`). Tope total US$ 14.00.
- A: `research_v3` registro de fuentes por tema (`fuentes.json` = registro `f24-1`; la salida de R1 pasa a `fuentes_r1.json`), R1 unido (`unir_fuentes`, aporte primero), R2 reusa lo bajado (`previos`), R3 caché por texto (`r3_txt_<sha1>.json`). Kyshtym: registro armado de disco (36 fuentes, 23 bajadas, 21 con aporte; Osetrov entra reusado en el cupo ruso) — `lab/hyperframes/f24/registro_kyshtym.md`.
- B: bloqueante «entre 1 y 3 beats por cap» (`MAX_BEATS_POR_CAP`); escaleta `f24-1` (md5 `006a195f…`; la f22-2 queda `SYSTEM_V2_F22_2`). B.3 (US$ 1.66): Fable cortado en max_tokens; S1 rechazada (humano = id de cita); S2 1·1·2·2·2·3·3 → **Sol para C** (`TABLA_B3.md`).
- Suite amplia 855 verdes + las 5 previas.

## F23 — Familias D + G + H + I: el tiempo del caso, umbrales a métrica, intent desde la escaleta, idiomas — HECHO, **PARADA** (el analista lee el guion y el diff; si Kyshtym da ≥ 8, F24)
- Sobre `2dcc428`. Reporte `lab/hyperframes/f23/F23_REPORT.md` (revisor íntegro: CUMPLE CON OBSERVACIONES), `compara_f23.html` (F22d | F23 por cap).
- Perfil: `anio_inicio/anio_fin/tipo_evento/cobertura_ingles/idiomas_research`. Kyshtym: **1948–1967 prolongado**, [ruso, inglés, español]; Orleans 2005 puntual; Ycuá 2004 puntual (a esos dos solo se les sumaron los campos nuevos; respaldo `_perfil_f22.json`).
- Contaminación solo si año < inicio − 20 (Kyshtym: 0 descartes; F22: 36). Compuerta: rojo solo con datos < 40 / personas < 2 / eventos < 3; amarillo informativo. Prompts: ficha v2.2 `f23-1` (bloque md5 `070b75df…`), guion v5.3 `f23-1` (`8ca9aa49…`); escaleta y columna sin cambio. Intent por cap = `m01a_escaleta.intent_de_cap`.
- Kyshtym desde la semilla: compuerta verde (154 · 21 · 16 · 56 · 23) → ficha v2.2 → escaleta f22-2 sin columna (2 intentos) → guion Fable v5.3 1,446 palabras, 0 bloqueantes, 8 citas. Sin Osetrov/Komarov/Serov (la R1 nueva no trajo su documento); el cap 6 tiene 601 palabras y los caps 2–4, 76–134.
- En `_steps/f18-kyshtym-mayak`: pool/perfil/ficha nuevos; respaldos `00_pool_v3_f22.json`, `_perfil_f22.json`, `ficha_caso_f22.json`, `_f22/`. Arreglo en `m05.cap_review` (min vacío). Suite amplia 845 verdes + las 5 previas. Sin merge.

## F22e — Fable 5.1 por defecto en el guion · promesa en la escaleta — HECHO, **PARADA**
- Sobre `f56c018`, cero corridas. Reporte `lab/hyperframes/f22e/F22e_REPORT.md` (revisor íntegro: CUMPLE CON OBSERVACIONES).
- `guion_v4.DEFAULT_MODELO_GUION = claude-fable-5-1` (effort high, max_tokens 32 000); Opus 5.5 y Sol con `--modelo`; escaleta y columna siguen en Sol.
- Escaleta v2.1 `f22-2`: en `<oficio>` §2, «Es una imagen o una pregunta, nunca un resumen de lo que va a pasar ni una lista de lo que viene.» Archivo y `SYSTEM_V2` iguales (md5 `22cfd68b…`); la de F22 queda como `SYSTEM_V2_F22_1` (`7ea18a6a…`).
- Tests f12/f17/f22/f22d adaptados; suite amplia 806 verdes + las 5 previas. Sin merge.

## F22d — Sin columna y Opus por defecto · Kyshtym — HECHO, **PARADA**
- Sobre `ee54850`. Reporte `lab/hyperframes/f22d/F22d_REPORT.md` (revisor íntegro: CUMPLE CON OBSERVACIONES), runner `f22d_corridas.py`.
- **Decisión del analista, en código (prompts sin cambios):** `fase1_5` corre la escaleta siempre sin columna; `--columna` genera la columna solo como `COLUMNA_<id>.md` de lectura; `--sin-columna` queda como no-op. `guion_v4.DEFAULT_MODELO_GUION = claude-opus-5-5` (effort high, max_tokens 32 000) para `write`/`reparar`/`run_guion_v4`; `call_for(None)` (escaleta, columna) sigue en Sol.
- Kyshtym desde la ficha de F22: escaleta sin columna (Sol; humano Kutepova, antagonista institución Mayak, 44 ids) → guion Opus 1,695 palabras ≈ 13.8 min, 0 bloqueantes, 9 citas. US$ 0.7736 de 1.50.
- Tests `test_module_f22d.py` (3) + f10/f12/f17 adaptados; suite amplia 806 verdes + las 5 previas. Sin merge.
- **Adenda Fable 5.1** (pedido de Omar): `claude-fable-5-1` en PRICES (10/50) y en la cadena; guion v5.2 sobre la misma escaleta: 1,579 palabras ≈ 12.8 min, 0 bloqueantes, 10 citas, US$ 0.947. Tanda F22d US$ 1.721 de 3.00.

## F22c — ¿Escaleta con columna más floja? — HECHO PARCIAL, **PARADA por tope** (faltan B2 y K)
- Sobre `cd5fde5`, sin cambios de código fuera de lab. Reporte `lab/hyperframes/f22c/F22c_REPORT.md` (revisor íntegro: NO CUMPLE — entrega parcial declarada, faltan B2 y K), tabla `tabla_f22c.md`, runner `f22c_corridas.py`.
- Ycuá, escaleta v2.1 Sol + guion Opus 5.5 v5.2: **sin columna** (A1, A2) 54–55 ids, 2.4 apoyos/beat, guion 1,590 / 1,604 palabras, 24 personas; **con columna** (B1; F22 de ref.) 31–32 ids, 1 apoyo/beat, guion 1,332 (F22b: 1,144 / 1,159), 13 personas. Todos 0 bloqueantes, cero Cardal.
- Freno: Opus con 20 000 tokens de salida se cortó en A1 (US$ 0.448 perdidos, error mío) → B2 quedó en el intento 1 de la escaleta y K no corrió. US$ 2.8094 de 3.00. Sin merge.

## F22b — Corrector de cifras «recibidas», Claude Opus 5.5 en el guion v4, cinco guiones de Ycuá — HECHO, **PARADA**
- Sobre `ed55399`. Reporte `lab/hyperframes/f22b/F22b_REPORT.md` (revisor íntegro: CUMPLE CON OBSERVACIONES), tabla `tabla_f22b.md`, runner `f22b_corridas.py`, prueba de la llave `prueba_llave.py`.
- (a): `invented_numbers(recibido=)` + `guion_v4.datos_recibidos` (líneas con [id] del bloque <escaleta>, sin ids) → el «1982» de Kyshtym F22 ya no es bloqueante (su guion de F22 pasa con 0).
- `claude_helpers.py` (Messages API por HTTP, `anthropic-version` 2026-10-21, llave de `.env` ANTHROPIC_API_KEY, nunca impresa; PRICES Opus 5.5 4/20, Sonnet 5.5 2/10); `--modelo claude-opus-5-5` (effort high) en `fase1_5` y `guion_v4.call_for`. Prueba de 10 tokens: HTTP 200.
- Corridas (misma escaleta de F22, solo guion, 0 bloqueantes todas): Sol v5.2 939 / 846 palabras; Sol v5.1 (`f15b-1`, el pedido decía `f15-1`, que es el v5) 803; Opus 5.5 v5.2 1,144 / 1,159. **La caída de largo de F22 viene de la escaleta, no del v5.2.** Cero Cardal. US$ 0.9897 de 4.00.
- Tests `test_module_f22b.py` (8); suite amplia 803 verdes + las 5 previas. Sin merge.

## F22 — Familias C + E (ejemplos de Puerto Cardal, antagonista de tres tipos) y nombre en documento — HECHO, **PARADA** (el analista revisa el diff de prompts y lee las dos cadenas)
- Sobre `8be0ea9`. Handoff `lab/hyperframes/f22/HANDOFF_F22_ejemplos_y_antagonista.md` (md5 2685deec…, con sus 5 archivos verificados). Reporte `lab/hyperframes/f22/F22_REPORT.md` (diff línea a línea de los 4 prompts; revisor íntegro: CUMPLE CON OBSERVACIONES) y `compara_f22.html` (teléfono OK). Runner `f22_corridas.py`, página `f22_compara.py`, diff `f22_diffs.py`, `cero_cardal.py`. `_transfer_tmp/` borrado.
- Prompts literales: ficha `f22-1`, columna `f22-1` (+ tarea con QUIÉN DECIDE), escaleta v2.1 `f22-1` (con o sin columna), guion v5.2 `f22-1`. **Los viejos quedan en código con su versión** (`ficha_caso.system("f15-1")`, `m01a_columna.SYSTEM_F17_1/TAREA_F17_1`, `m01a_escaleta.SYSTEM_V2_F16_1`, `guion_v4.system("f15b-1")`). Escaleta v1 y tareas de escaleta/guion byte-idénticas.
- E: `antagonista {tipo persona|institucion|ninguno, id, nombre, por_que}` en columna (chequeo), escaleta (bloqueante; copia variantes de la ficha), m01d (la institución queda en `personajes` con `tipo`), `antagonist_problems`/`_ANON_VOICE` solo con persona; métricas `antagonista_tipo/_caps`. R3: `nombre_en_documento`/`autor_en_documento` (verify_pool, presencia, validate).
- Corridas: **Ycuá** 0 bloqueantes (Liz Torres; Paiva persona) pero **838 palabras ≈ 6.8 min** (F16: 1,384). **Kyshtym**: pool de F21c recalculado (verde, 7 elegibles; `00_pool_v3_f20.json` respaldo; topics_db sin tocar), ficha nueva, columna (humano Komarov, **antagonista «ninguno»**), escaleta OK, guion 1,003 palabras con **1 bloqueante (a) «1982»** (año en `fuente`, no en el texto) → PARADA. Cero Cardal en todo. US$ 1.4672 de 3.00.
- Hallazgos para el analista: 3 cambios de los prompts fuera de su «qué cambia»; «Осетров» no verifica (declinación: junto a la cita dice «Осетрова»); dos `P09` en el pool de Kyshtym (`add_quote_authors`); el dorado v3 cambió solo por los 5 mensajes (probado).
- Tests `test_module_f22.py` (52) + 7 adaptados; suite amplia 795 verdes + las 5 previas. Sin merge.

## F21c — Cargos genéricos, perfil de Orleans, elegible = persona — HECHO, **PARADA**
- Sobre `fd54356`. Sección «F21c» al final de `lab/hyperframes/f21/F21_REPORT.md` (revisor íntegro: CUMPLE CON OBSERVACIONES) y `RECHECK_f21c.md` (F21b → F21c).
- **`nombres.TRATAMIENTOS_BASE`** suma 17 cargos genéricos (warden, director, alcaide, ministro, general, doctor, ingeniero, presidente, gerente…). «Warden de Hunt…» y «Director of…» dejan de ser personas. Efectos: «General Motors» pasa a persona, y en Ycuá entra «Ingeniero Cristaldo», duplicado de Blas Cristaldo.
- **Perfil de Orleans** con `seed_profile` (1 Flash, US$ 0.0021): `nombres_lugar` en inglés; respaldo `_perfil_f21b.json`; detalle en `f21c_perfil_orleans.json`. La población vuelve con 6,375 (F01) oficial y **6 de 7 variantes**: falta D533 («complejo carcelario», que no está en los nombres del perfil).
- **Komsomolskaya Pravda:**
  - camino de entrada: `add_quote_authors` en el research de F20, con la regla vieja (autor «periódico Komsomolskaya Pravda», Q15) → quedó guardado como P09;
  - después, `verify_pool` lo verificaba sin apellido y `person_stats` lo marcaba elegible;
  - arreglo: `person_stats` exige `es_persona` (con mononimio).
- Recheck F21b → F21c: Orleans 33 → 32 (sale Warden); Ycuá 34 → 35 (entra Ingeniero Cristaldo); Kyshtym 8 → 7 (sale Komsomolskaya). Bloqueantes iguales.
- Tests `test_module_f21.py` 43; suite 743 verdes + las 5 previas. US$ 0.0021.

## F21b — Perfil en el guion, atribución oficial, criterios de forma — HECHO, **PARADA** (pendiente de Omar: ¿«warden»/«director» como cargos?)
- Sobre `b24c505`, cero API (US$ 0.00) y cero prompts. Sección «F21b» al final de `lab/hyperframes/f21/F21_REPORT.md` (revisor íntegro: CUMPLE CON OBSERVACIONES). Comparación de cifras en `RECHECK_f21b.md`.
- **Perfil en el guion:** `fase1_5.cargar_perfil` (desde `_topic_v3`, escaleta y guion v4) carga `_steps/<id>/_perfil.json` en `set_vocabulario`. Sin perfil, `guion_v4.nota_b()` = «(b) sin perfil: no evaluado» (queda en `01b_guionista_v4.json` y se imprime). Perfil canónico: en Orleans e Ycuá, `_perfil.json` = `_perfil_f20.json`; el viejo de Ycuá quedó como `_perfil_pre_f20.json`; Orleans no tenía.
- **`_official_says`:** el rol que decide cuenta en cualquier parte del dato. **Orleans vuelve a 6,375 (F01) como oficial**, pero el grupo trae solo la variante 7,000, porque el perfil de Orleans no tiene `nombres_lugar` y entonces no hay sujeto. Además sigue el grupo 6,295 de F21.
- **`es_persona`:**
  - con coma, « y » o « and » no es persona, salvo la coma antes de un sufijo (Jr., III);
  - un tratamiento seguido de partícula es un cargo;
  - **«Warden de Hunt…» sigue como persona, porque «warden» no es tratamiento** (F20 lo sacó); decide Omar.
- Recheck F21 → F21b: Orleans y Ycuá sin cambios; Kyshtym 9 → 8 elegibles (sale «Толстиков, Бочкарева»). `RECHECK_f21.md` verificado contra `b24c505` (idéntico; solo cambió el título).
- Tests: `test_module_f21.py` 38 (+14). Suite amplia 738 verdes + las 5 previas.

## F21 — Familias A + B + F de la auditoría (nombres, molde de Orleans, jueces con la traducción) — HECHO, **PARADA** (el analista revisa el diff `git diff 08d63d9..HEAD -- researcher_steps script_engine`, lee `RECHECK_f21.md` y escribe F22)
- Handoff `lab/hyperframes/f21/HANDOFF_F21_nombres_y_borrados.md` (md5 19fcbb90…); auditoría `AUDITORIA_fase1_supuestos.md`. Reporte `lab/hyperframes/f21/F21_REPORT.md` (revisor íntegro: CUMPLE CON OBSERVACIONES) y `RECHECK_f21.md` (antes con el código de 08d63d9 | después, sin API: `recheck.py`, `recheck_md.py`). `_transfer_tmp/` borrado. **US$ 0.00, cero prompts tocados (md5 de los 4 iguales).**
- Código:
  - `script_engine/nombres.py`: única fuente sobre nombres (cualquier alfabeto, iniciales, partículas, mononimio con rol, MAYÚSCULAS). Las 13 funciones viejas quedan como alias (`# F21: alias`). Lecturas declaradas: los artículos no son parte del nombre; un cargo cuenta solo justo delante del nombre; en `verify_pool`, el autor cerca de la cita con el apellido o cualquier parte del nombre.
  - Borrados (B):
    - `SUBJECT_RE_DEFAULT`, `_OTHER_PLACE` y `_OFFICIAL_SAYS` (el sujeto sale del perfil), las stopwords de Orleans y `_NOT_PERSON`;
    - preso/guardia en `role_class` (ahora testigo/antagonista del perfil; sin perfil, (b) no evalúa);
    - `JUDGMENTS` de caso, `photo_problems` sin cámara ni imagen, `_COMMON_CAPS` (`fix_glued_caps(pool=)`) y 4 rellenos de `FORBIDDEN_FILLER`;
    - `ADMIN_TERMS` v1 pasa a aviso; `INSTITUTION` sale de la ficha y pasa a métrica; `verify_quotes` sin el tema escrito.
  - F: `guion_v4.pool_con_traducciones` al entrar a `bloqueantes()`.
  - Tests `test_module_f21.py` (24) + 6 tests viejos adaptados (f7, f11, f5b, f5c, f6b, f20). Suite amplia 724 verdes + las 5 previas.
- Recheck:
  - **Orleans y Ycuá:** verde/verde, elegibles 32 → 33 y 32 → 34 (no sale nadie), guion y escaleta con 0 bloqueantes antes y después. Citas verificadas: Orleans igual (162), Ycuá 52 → 53.
  - **Kyshtym:** elegibles 4 → 9. Osetrov, Komarov, Serov y Ladeishchikova entran como personas, pero **solo Ladeishchikova es elegible**: los otros tres tienen citas parciales por transliteración (Osetrov ↔ Осетров).
  - Entraron como elegibles algunos que no son personas: Komsomolskaya Pravda, «Мама de Надежда Кутепова», «Толстиков, Бочкарева» y, en Orleans, «Warden de Hunt Correctional Center».
  - Kyshtym no tiene guion, así que lo de las «citas falsas» se probó con tests.
- Queda para F23: `evidence_pool._content_set` y `person_acts` (regex latinas que deciden), transliteración y comentarios J.
- Sin merge.

## F20 (parte 1 de 3) — El research se adapta al tema — HECHO, **PARADA** (el analista valida antes de la parte 2: que Orleans e Ycuá no empeoraron, que los elegibles de Kyshtym son los que la historia necesita y que las listas carcelarias ya no están en el código)
- Handoff `lab/hyperframes/f20/HANDOFF_F20_research_por_tema.md`; `f20.b64` es la misma copia en gzip + base64 y no se commitea. Reporte `lab/hyperframes/f20/F20_REPORT.md` (revisor íntegro: CUMPLE CON OBSERVACIONES). Runner `f20_corridas.py` (`recalculo`, `research`, `vocab_kyshtym`).
- Código (solo `research_v3.py`):
  - `seed_vocabulario` (1 Flash después de R1; esquema `{es, otras}` + `_formas` como lectura de formato) → `roles_testigo`, `roles_antagonista` y `sustantivos_conteo` en `_perfil.json`. `set_vocabulario` los aplica:
    - R3 con los roles del perfil;
    - `_TITLES` y `_NOT_PERSON` sin términos de tema (sheriff, deputy y alguacil siguen como cargos: declarado; el revisor lo marca como reinterpretación);
    - conteo con los sustantivos del perfil, más «personas» y «víctimas».
  - `download_sources`: 10 descargas por idioma (`fuente_idioma`).
  - `person_stats`: elegible = no antagonista, sin un rol de `roles_antagonista` (el rol empieza con él), y cita propia verificada o ≥ 3 ítems; `presente_en_evento` queda informativo.
  - Tests `test_module_f20.py` (8) y 4 tests de `test_module_f7.py` adaptados (fixture con el vocabulario de Orleans; Duncan pasa a elegible). Suite amplia 700 verdes + las 5 previas.
- Resultado:
  - **Orleans** verde → verde, elegibles 12 → 32 (no sale nadie; entran funcionarios como Blanco y Stalder); canónica 6,375 (se pierde la variante 6,500).
  - **Ycuá** verde → verde, 15 → 32, sin canónica.
  - **Kyshtym ROJO → VERDE** (208 / 20 / **4 elegibles**: Krestinina, Vazhenin, Medvedev, Tumerman / 22). Los testigos de la explosión (Osetrov, Komarov, Serov) y las voces en cirílico tienen citas verificadas, pero no son personajes: `evidence_pool.is_person` rechaza iniciales y cirílico. Queda para la parte 2.
  - **US$ 1.013** (research Kyshtym 0.963 de 3.50).
- Disco:
  - Orleans e Ycuá: solo archivos `_f20` nuevos;
  - Kyshtym: pool, perfil y fuentes de F20 (F19 en `00_pool_v3_f19.json` y `_f19/`; intento 1 respaldado);
  - **el topic de Kyshtym en `topics_db` tiene el pool de F20** (respaldo `topics_db.pre_f20.json`).
- Sin merge. **No seguir a ficha ni guion.**

## F19 — Kyshtym otra vez: cirílico en el research — HECHO, **PARADA en el research** (compuerta ROJA: 0 humanos elegibles; no corrió ficha, columna, escaleta ni guion)
- Handoff `lab/hyperframes/f19/HANDOFF_F19_kyshtym_cirilico.md`. Reporte `lab/hyperframes/f19/F19_REPORT.md` (revisor íntegro: CUMPLE CON OBSERVACIONES) y `compara_f19.html` (embudo F18 | F19 por idioma; teléfono OK a 375 px). Runner `f19_corridas.py`, página `f19_compara.py`.
- Código (§1, sin chequeos nuevos):
  - `research_v3.seed_profile` pide `nombres_locales`; `place_regex` = latinos con `\b` como antes + locales con lookarounds. Sin locales, el `place_re` de siempre. El perfil sigue en Flash: el handoff decía «Pro», pero también «el mismo paso».
  - `m01a_escaleta`: antagonista `tipo` persona o institución (`institucion_de_la_ficha`: persona de la ficha o ≥ 2 hechos; el artículo inicial no cuenta). Sin ficha, nada cambia.
  - `build_prompt_v2(beats=)`: «Esta escaleta lleva entre N y M beats» solo cuando hay compuerta.
  - `ficha_caso`: citas con `traduccion` (en el esquema) e `id_texts` usa la traducción.
  - Tests `test_module_f19.py` (15); suite amplia 692 verdes + las 5 previas.
- Corrida:
  - research rehecho sobre el mismo topic. Con el cirílico, **8 documentos rusos aportan 239 ítems (0 en F18)** y el pool pasa de 175 a 302 ítems;
  - **ROJO por elegibles_humano 0**: Tumerman bajó a 1 cita y 2 datos, porque en.wikipedia no salió en el R1 nuevo (el perfil nuevo cambió las consultas: 20 fuentes) y el tope de 10 descargas se llenó con rusos. Hubo 3 HTTP 429;
  - sin reintento (no es una causa de descarga demostrable). **US$ 0.932 de 5.00.**
- Disco:
  - en `_steps/f18-kyshtym-mayak/`, el pool, el perfil y `fuentes/` son los de F19 (rojo); lo de F18 está en `00_pool_v3_f18.json` y `_f18/`;
  - **el topic de `topics_db` sigue con el pool de F18** (respaldo `topics_db.pre_f19.json`).
- **Para Omar:** no hay guion. Opciones (no ejecutadas):
  - (a) reintentar el research una vez, con en.wikipedia y las 429;
  - (b) humano colectivo frente a la compuerta;
  - (c) tope de descargas para temas bilingües.

## F18 — Kyshtym / Mayak (cadena completa en un tema de Omar, nocturna) — HECHO, **PARADA** (la escaleta no salió: no hay guion; el analista lee ficha y columna y decide)
- Handoff `lab/hyperframes/f18/HANDOFF_F18_kyshtym_nocturno.md`. Reporte `lab/hyperframes/f18/F18_REPORT.md` (revisor íntegro: CUMPLE CON OBSERVACIONES) y `compara_f18.html` (embudo, columna, PARADA de la escaleta; teléfono OK a 375 px). Runner `f18_corridas.py` (topes por paso + freno antes de cada llamada de Sol), página `f18_compara.py` (sin API).
- Topic `f18-kyshtym-mayak` creado por el camino normal (`research_topics` long con el id fijo, como F10): seed b6b84f96 tal cual + `idioma_local` ruso/español. Está en `data/topics_db.json` (respaldo `topics_db.pre_f18.json`); la semilla salió del inbox y pasó al archivo. Título 4c: «Kyshtym Mayak: El Desastre Nuclear Abandonado De La URSS».
- **Estado exacto:**
  - research v3 + 4a–4e: US$ 0.965, compuerta 🟡 **AMARILLO** (97 datos, 13 citas verificadas, 1 elegible humano, 11 eventos);
  - ficha v2: US$ 0.322, 5 citas de 18 (las traducciones no pasan el chequeo), 2 candidatos (Medvedev, Tumerman);
  - columna: US$ 0.073, 1 intento; humano **Lev Tumerman**, pico en el cap 5 (la explosión del tanque), **3 personas con nombre**;
  - **escaleta v2: PARADA.** En el pase 1, la regeneración quedó solo con «antagonista None»: en este caso no hay una persona que decida, decide el Estado. El pase 2 lo decidí yo (precedente F15); el revisor lo marca como desvío no previsto. Dio 8 bloqueantes y el freno cortó la regeneración.
  - Sin guion. **Total US$ 1.739 de 5.00.**
- **Roturas del tema nuevo (anotadas, sin reglas nuevas, sin tocar código):**
  - (1) las 5 fuentes rusas bajaron (113 k caracteres) pero aportaron 0 ítems: `place_re` de `seed_profile` no tiene cirílico. El pool es 100 % de 5 fuentes en inglés;
  - (2) citas traducidas al español frente al chequeo de Levenshtein de la ficha;
  - (3) el bloqueante «antagonista es persona» frente a un antagonista institucional;
  - (4) los 7–8 beats de la compuerta amarilla frente al «de 7 a 14» del sistema v2.
- Tests: no hay código nuevo fuera de `lab/`; la suite amplia sigue en 677 verdes + las 5 previas. Sin merge.
- **Para Omar al despertar:** no hay guion para puntuar. Para decidir:
  - si se arregla la búsqueda en cirílico (`research_v3`, prohibido en esta tanda) y se rehace el research;
  - qué hacer con el antagonista institucional y con el rango de beats en amarillo.

## F17 — Columna vertebral (ficha → columna → escaleta → guion) — **CERRADO en PARADA 1** (2026-10-24: Omar cambió de tema → F18 Kyshtym/Mayak; **Ycuá queda en PARADA 1 para siempre**: no se regenera su columna ni se corre nada más de Ycuá; Orleans tampoco). Reporte corto `lab/hyperframes/f17/F17_REPORT.md` (dos veredictos del revisor íntegros: CUMPLE CON OBSERVACIONES)
- Handoff `lab/hyperframes/f17/HANDOFF_F17_columna_vertebral.md`; prompt `PROMPT_COLUMNA_v1.md` (sistema md5 1408569c…, extraído anclando en «## SISTEMA», LF). Runner `lab/hyperframes/f17/f17_corridas.py` (tope US$ 2.00, `costos_f17.json`).
- Código: `script_engine/m01a_columna.py` (`f17-1`, Sol high, chequeo: 7 caps, humano y personas de la ficha, ids; una regeneración → PARADA; métrica de personas con nombre; `columna_notas.md` = UNA regeneración con notas). `m01a_escaleta`: `build_prompt_v2(columna=)` (columna antes de la ficha, `TAREA_COLUMNA` literal), `generate_escaleta(columna=None|dict|"generar")`, `metricas_columna`; **sin columna, byte-idéntica a F16** (md5 de fixtures y de los prompts reales de Ycuá/Orleans). `fase1_5 --sin-columna`. `cost_tracker` no escribe el historial bajo pytest.
- `data/cost_history.json`: sacadas las entradas `t-f11b` (encontré 33 por US$ 99.0, no 59; respaldo `data/cost_history.pre_f17.json`; 505 → 472).
- Tests: `test_module_f17.py` (27); suite amplia 677 verdes + las 5 previas; dorado v3 verde.
- Corrida: **columna de Ycuá v1** (US$ 0.089, 1 intento, 0 problemas): humano Tatiana Gabaglio, pico cap 5 (Liz Torres), 7 personas con nombre → guardada como `COLUMNA_ycua_v1.md` / `01a_columna_v1.json`.
- **Decisión de Omar (2026-10-24):** tres notas en `_steps/f8s1-ycua-bolanos/columna_notas.md` (humano Liz Torres, Tatiana como segunda historia en caps 4 y 6; las puertas: la orden en el cap 4 y las versiones en el cap 7; el cap 3 arranca con lo que se oye y se ve). Regeneración única con las notas en la tarea: US$ 0.080, 1 intento, 0 problemas; humano Liz Torres, 6 personas con nombre. Tanda US$ 0.169. **PARADA**; no hubo «dale»: el plan cambió a F18.

## F16 — Escaleta v2 (13 bloqueantes, Sol) · Ycuá y Orleans completos — HECHO, **PARADA** (el analista revisa el diff y lee escaletas y guiones; si Ycuá da ≥ 8, lo que sigue es producción)
- Handoff `lab/hyperframes/f16/HANDOFF_F16_escaleta_v2.md`; prompt `PROMPT_ESCALETA_v2.md` (md5 8d573288…). Reporte `F16_REPORT.md` (revisor íntegro: CUMPLE CON OBSERVACIONES) y `compara_f16.html` (teléfono OK).
- Código (`m01a_escaleta`):
  - `SYSTEM_V2` y `TAREA_V2`, literales (md5 del sistema 49ed74d9…); `build_prompt_v2` (caso · ficha con historia y escenas primero · tarea); `generate_escaleta_v2` con Sol high (`guion_v4.call_for`), `SCHEMA_FICHA` y una sola regeneración; si vuelve a fallar, PARADA.
  - `bloqueantes()` = los 13 mensajes de `validate`, tal cual (`BLOQUEANTES_V2`); el resto va a `metricas_escaleta()`.
  - `apply_pool_plan(instrucciones=False)` con ficha.
  - `ids_v2`: lee el id del texto («Q19: …» → Q19). Lo eligió Omar después de que el primer pase terminara en PARADA en los dos temas, porque el ejemplo del prompt induce ese formato.
  - **Sin ficha, todo byte-idéntico** (md5 de HEAD).
- Tests: `test_module_f16.py` (22); suite amplia 650 verdes + las 5 previas.
- Resultado:
  - Las dos escaletas pasaron en la regeneración: humano candidato (**Liz Torres**; en Orleans, **Joyce Gilson**), el pico de la ficha, gancho y pico con escena (flash-forward), 8 escenas y 6 de 6 giros.
  - **Guion v5.1: Ycuá 1,384 palabras (11.3 min), Orleans 1,443 (11.7 min), 0 bloqueantes.**
  - Tanda **US$ 1.359** de 2.00.
- Escaletas nuevas: `01a_escaleta_f16.json` (no se pisó ninguna). Sin merge. **No seguir a producción sin el OK.**

## F15b — v5.1: la escena merece un párrafo (Ycuá y Orleans) — HECHO, **PARADA** (la escaleta nueva de Ycuá no salió; el analista revisa el diff y lee los guiones)
- Handoff `lab/hyperframes/f15b/HANDOFF_F15b_escena_por_parrafo.md`; prompt `lab/hyperframes/f15/PROMPT_GUIONISTA_v5_1.md` (md5 6dcc4294…). Reporte `F15b_REPORT.md` (revisor íntegro: CUMPLE CON OBSERVACIONES; la escaleta de Ycuá en PARADA) y `compara_f15b.html` (teléfono OK).
- Código:
  - `guion_v4.SYSTEM_V5_1`, literal (md5 cdce609a…); `PROMPT_VERSION` `f15b-1`; el v5 sigue con `version="f15-1"`.
  - `m01a`: el texto de ESCENAS pide gancho y pico desde las escenas, y avisa «gancho sin escena de la ficha». Sin ficha, byte-idéntica.
  - `ficha_caso`: cifras normalizadas (G., $, US$, °, espacios, miles) **+ números en letras y «millones» (ampliación que eligió Omar: el afloje literal recuperaba 0 de 12)**; sentidos: alcanza con una palabra.
- Tests: `test_module_f15b.py` (7); suite amplia 628 verdes + las 5 previas.
- Re-chequeo sin llamada: en Ycuá vuelven los 17 (12 cifras + 5 escenas); en Orleans vuelven 6 y siguen afuera 14 que no están respaldados. Fichas F15 respaldadas como `ficha_caso_f15.json`.
- Resultado:
  - **Frases por párrafo: Ycuá 2.0 → 4.0 y Orleans 2.2 → 3.9; párrafos de 1 frase: 14 → 3 y 7 → 3.** Los dos guiones duran 7.0 min y tienen 0 bloqueantes.
  - Orleans: escaleta nueva (humano Burton, el pico con escena E9, el gancho sin escena) y guion de 867 palabras.
  - **Ycuá: la escaleta nueva quedó rechazada en 3 pases (7 intentos), por reglas que ya existían** (sobre todo la curva de intensidad en el beat 2, porque el gancho sale de una escena sin `flash_forward`, y Liz Torres en escena con Q20 sin verificar). El freno de costo la cortó: **PARADA**. Como sustituto, el guion v5.1 sobre la escaleta F15: 858 palabras, con el gancho de las cenizas.
  - Tanda **US$ 1.321** de 1.50.
- Sin merge. **No seguir a producción.**

## F15 — Prompt del guionista v5 + ficha v2 (Ycuá y Orleans) — HECHO, **PARADA** (el analista revisa el diff y después lee fichas, escaletas y guiones)
- Handoff `lab/hyperframes/f15/HANDOFF_F15_prompt_v5.md`; prompts del analista `PROMPT_GUIONISTA_v5.md` (md5 411782fa…) y `PROMPT_FICHA_v2.md` (1fdbd0b9…). Reporte `F15_REPORT.md` (revisor íntegro: 1.ª NO CUMPLE por el sistema mal extraído → arreglado → 2.ª CUMPLE CON OBSERVACIONES) y `compara_f15.html` (teléfono OK).
- Código:
  - `guion_v4`: `SYSTEM_V5` y `TAREA_V5`, literales (test contra el .md); `PROMPT_VERSION` `f15-1`; `prompt_v5` (caso con el porqué, «CAP n (función)», intensidad, marca «VERSIÓN DE: quién»). `version="f11c-1"` reproduce F11c–F14. `largo` vale `abierto` por defecto en el prompt, los bloqueantes y la reparación.
  - (d) con ficha: `pool_sin_rescatados` (`m05` intacto).
  - `ficha_caso` `f15-1`: `historia`, `escenas` (los sentidos tienen que estar en sus ids), `nivel` y `sirve_para`.
  - `m01a`: con ficha v2, historia y escenas van primero; `SCHEMA_FICHA` (`escena_idx`, `justificacion_humano`) y `ficha_notes`. **Sin ficha, byte-idéntica.**
- Tests: `test_module_f15.py` (12) + aserciones viejas pinneadas a `version="f11c-1"`; suite amplia 621 verdes + las 5 previas.
- Resultado:
  - **Ycuá 1,153 → 755 palabras (9.4 → 6.1 min). Orleans 1,451 → 866 (11.8 → 7.0 min).** 0 bloqueantes y 0 preguntas en los dos.
  - **Incidente arreglado:** la primera extracción del SISTEMA v5 tomaba el `<rol>` del párrafo introductorio del .md (md5 f157a2ce…). Ahora se ancla en «## SISTEMA» (md5 2ff2a5cd…) y el test también. Los dos guiones se re-corrieron (los contaminados quedan como `*_preambulo`; daban 718 y 763).
  - Humano: Liz Torres en Ycuá y Brady Richard en Orleans (los dos, candidatos de la ficha). Pico: el de la ficha.
  - Escenas usadas: Ycuá 0, Orleans 5.
  - La escaleta de Orleans quedó rechazada en los 3 intentos la primera vez («un hecho, una cifra», D533/D214) y salió en un segundo pase.
  - Tanda **US$ 2.116** de 2.50.
- Fichas anteriores respaldadas (`ficha_caso_f12.json`, `ficha_caso_f14.json`); `ficha_caso.json` es ahora la v2 en los dos temas. Escaletas nuevas: `01a_escaleta_f15.json`. Sin merge. **No seguir a producción.**

## F14 — La ficha en el camino (Orleans) — HECHO, **PARADA** (el analista lee la ficha, la escaleta y el guion y le dice a Omar si el video ganó material y filo)
- Handoff `lab/hyperframes/f14/HANDOFF_F14_ficha_en_el_camino.md`. Reporte `lab/hyperframes/f14/F14_REPORT.md` (revisor íntegro: CUMPLE CON OBSERVACIONES) y `compara_f14.html` (F13 | F14 con el embudo; teléfono OK). Textos: `FICHA_orleans.md`, `ESCALETA_orleans_f14.md`, `NARRACION_orleans_f14.md`.
- Código:
  - `ficha_caso` `f14-1`: 5 criterios → `decisiones` (1, 2, 3, 5), `versiones` (4), `contradicciones` (el resto), `personas_descartadas` y `aproximada`, más el chequeo de las secciones nuevas; `id_texts` y `load`.
  - `m01a_escaleta`: con ficha (`generate_escaleta(ficha="auto")` lee `_steps/<topic>/ficha_caso.json`), la escaleta lee la ficha y no el digest, con apoyos 0–6. **Sin ficha es byte-idéntica** (md5 de HEAD), con apoyos 0–3.
  - `guion_v4.data_line`: con ficha, el texto de cada id sale de la ficha. `fase1_5.run_guion_v4` pasa la ficha si existe. **Ojo: Ycuá ya tiene ficha (F12) en `_steps`.**
- Tests: `test_module_f14.py` (14); suite amplia 609 verdes + las 5 previas.
- Resultado:
  - **777 → 1,451 palabras (6.3 → 11.8 min)** con largo abierto.
  - Embudo pool → selección → escaleta → guion: 1,033 → 336 (digest) / 378 (ficha) → 32 / 53 → 13 / 18. Beats: 8 → 14. Humano: Reed → Pearl Cornelia Bland.
  - Decisiones: 22 (criterio 1: 14; 2: 1; 3: 4; 5: 3); versiones: 10; contradicciones abiertas: 5.
  - **Nagin:** rescatado en la ficha y no usado por la escaleta, así que su bloqueante falso desapareció. **Los 2 bloqueantes de F14 son (d) por Burl Cain y Katherine Mattes, que la ficha rescató de los descartados del pool**: el (d) mira el pool, no la ficha. Decide Omar.
  - Tanda **US$ 0.811** de 1.50.
- La escaleta F7c-3 no se pisó (copia en `01a_escaleta_f7c3.json`; la nueva es `01a_escaleta_f14.json`). Pool y `topics_db` intactos. Sin merge. **No seguir a producción.**

## F13 — Largo abierto (Orleans + Ycuá, Sol high) — HECHO, **PARADA** (el analista lee las dos versiones abiertas y le dice a Omar si el guion gana filo y cuántos minutos da)
- Handoff `lab/hyperframes/f13/HANDOFF_F13_largo_abierto.md`. Reporte `lab/hyperframes/f13/F13_REPORT.md` (revisor íntegro: CUMPLE CON OBSERVACIONES) y `compara_f13.html` (objetivo | abierto por cap; teléfono OK). Textos `NARRACION_{orleans,ycua}_f13_abierto.md`.
- Código: `guion_v4` con `largo="objetivo"|"abierto"` en `prompt`, `escaleta_section`, `write` y `bloqueantes`.
  - `abierto` = sin «≈ N palabras» ni el total, con «Cada cap dura lo que su historia necesita: ni relleno ni resumen.», sin el ±25 % (c) y prompt `f13-1`.
  - `objetivo` (el valor por defecto) es byte-idéntico a `f11c-1`, con test.
- Tests: `test_module_f13.py` (4); suite amplia 595 verdes + las 5 previas.
- Resultado (Sol high, una llamada, sin notas, sin reparación):
  - **Orleans: 1,456 → 777 palabras (11.8 → 6.3 min).**
  - **Ycuá: 1,425 → 1,153 palabras (11.6 → 9.4 min).**
  - Bloqueantes iguales (Orleans 1, el Nagin de siempre; Ycuá 0).
  - La «repetición interna» (3-gramas) casi no separa las versiones, porque el relleno es paráfrasis: el cap 3 de Orleans objetivo da 0 %.
  - Tanda **US$ 0.109** de 0.50.
- Referencias objetivo (no se re-corrieron): `lab/_gpt_probe_analista/orleans/orleans_v4c_sol.json` (no se commitea) y el crudo de `f11c/guion_ycua_v4c_sol.json`. No se escribió en `_steps` ni en `topics_db`. Sin merge. **No seguir a producción.**

## F12 — Ficha del caso (Ycuá) — HECHO, **PARADA** (el analista lee la ficha y le pasa a Omar las contradicciones para decidir)
- Handoff `lab/hyperframes/f12/HANDOFF_F12_ficha_del_caso.md`. Reporte `lab/hyperframes/f12/F12_REPORT.md` (revisor íntegro: CUMPLE CON OBSERVACIONES). Ficha `FICHA_ycua.md` (contradicciones arriba) + `ficha_caso.json`, en `lab/hyperframes/f12/` y en `data/scripts/_steps/f8s1-ycua-bolanos/`.
- **Decisión de Omar:** el guionista es GPT-6.1 Sol (high) con el prompt de F11c, y se terminaron las pruebas de modelos. `guion_v4.DEFAULT_MODELO = "gpt-6.1-sol"` (sin `--modelo` → Sol high; `config.py` intacto).
- Código:
  - `researcher_steps/ficha_caso.py`: UNA llamada a Sol high con el pool completo (509 ítems, evidencias con doc@offset; repetidas como «(= arriba)»), estructura de F11c. Secciones: personas, cronologia, hechos, cifras con unidad, citas con `original`, contradicciones (sin resolver) y descartados.
  - Chequeo determinista (ids existen; cifras, horas y fechas en el texto de sus ids; cita corregida ≤ 3 Levenshtein) → `descartados` «no respaldado», sin reintento. `save()` re-aplica el chequeo sobre un crudo guardado.
  - `gpt_helpers.call_json(max_completion_tokens=)`.
- Tests: `test_module_f12.py` (12); suite amplia 591 verdes + las 5 previas.
- Resultado: 24 contradicciones (Paiva hijo ✅: Emiliano F05 / Víctor Daniel F15 / Víctor F10 / Daniel F09; también totales de muertos y heridos, la orden de cerrar, puertas e identidades fusionadas en P62 y P74), 99 personas, 61 cifras, 20 de cronología, 76 hechos, 25 citas (Q34 «portón» ✅) y 34 descartados. Chequeo: 12 falsos positivos en la corrida (los ids «F15» se leían como cifras) → corregido → 0 en el rechequeo, sobre el mismo crudo. **US$ 0.339** de 0.50.
- **Siguiente (otra tanda, después de que Omar decida):** cablear la ficha a la escaleta y al guionista. No se corrió escaleta ni guion. Sin merge.

## F11c — Prompt con estructura oficial + Gemini 4 Argon vs GPT-6.1 Sol (Ycuá) — HECHO, **PARADA** (el analista lee los dos crudos y finales y le da la nota a Omar)
- Handoff `lab/hyperframes/f11c/HANDOFF_F11c_estructura_y_modelos.md`. Reporte `lab/hyperframes/f11c/F11c_REPORT.md` (revisor íntegro: CUMPLE CON OBSERVACIONES) y `compara_f11c.html` (teléfono OK). Textos `NARRACION_ycua_v4c_{argon,sol}.md` (crudo + final); prompt único `prompt_ycua_v4c_{sistema,usuario}.txt` + `.md5`.
- Código:
  - `guion_v4` `f11c-1`: `system()` = rol, voz, oficio y ejemplos (Orleans F7c-3, literal); `prompt()` = <caso>, <escaleta> y <tarea> al final;
  - `--modelo gemini-4-argon` (`gemini_helpers.make_call`, sin temperature ni thinking; `gemini_model_research` intacto; precio 2/10 en `cost_tracker`);
  - m01c se saltea con 0 bloqueantes.
- Tests: `test_module_f11c.py` (8) + 2 aserciones de estructura adaptadas en f11/f11b; suite amplia 579 verdes + las 5 previas.
- Resultado: **Sol high 1,425 palabras, 0 bloqueantes, crudo = final → cumple**; preguntas 20 → 6. **Argon 1,220 → 1,111 palabras, 1 bloqueante → no cumple:** la cita inventada se sacó, pero el cap 4 quedó corto y el m01c lo recortó a 115/250, porque acepta por conteo. Humo de argon OK (thinking informado 0). Tanda **US$ 0.196** de 1.50.
- Abierto para Omar: Paiva hijo («Emiliano», solo F05, contra «Víctor Daniel», en F09/F10/F15/F16); las dos narraciones dicen «Emiliano». Y la aceptación del m01c por conteo cuando un cap ya está corto.
- No se pisó nada ni se tocó `topics_db` ni `config.py`. Sin merge. **No seguir a producción.**

## F11b — v4 con largo + comparación de modelos (Ycuá) — HECHO, **PARADA** (el analista lee las tres narraciones y le da nota a Omar)
- Handoff `lab/hyperframes/f11b/HANDOFF_F11b_largo_y_modelos.md`. Reporte `lab/hyperframes/f11b/F11b_REPORT.md` (revisor íntegro) y `compara_f11b.html`. Textos `NARRACION_ycua_v4b_{gem,sol,astra}.md`; prompt único `prompt_ycua_v4b.txt`.
- Código:
  - línea de largo en el prompt v4 (`f11b-1`);
  - guardia de la regeneración solo cifras, nombres y citas (`lexical_guard(checks=)`, `regenerate_cap_v3(guard=)`; v3 intacto);
  - modelo enchufable: `gpt_helpers.py`, `guion_v4.call_for` y `fase1_5 --guion v4 --modelo gemini-pro|gpt-6.1-sol|gpt-6-astra`; llave `OPENAI_API_KEY` en `.env` (ignorado);
  - ids por beat (`used_items ∩ beat_ids`).
- Tests: `test_module_f11b.py` (15); suite 571 verdes + las 5 previas.
- Resultado (Ycuá v1, sin notas):

  | corrida | palabras finales | bloqueantes | US$ |
  |---|---|---|---|
  | gem | 882 | 5 | 0.611 |
  | sol | 1,229 (crudo 1,501) | 0 | 0.187 |
  | astra | 1,270 (crudo 1,489) | 0 | 0.405 |

  Tanda US$ 1.204 de 2.00. Ninguna final cumple 1,350–1,700: **la pasada del editor m01c recorta ≈ 220–270 palabras de los GPT**. Los crudos de Sol y Astra cumplen. Decide Omar con el analista; no se tocó la ronda.
- D80/D81/D97: el ancla «1» (de «A-1» en el texto) se expande a «una/uno» y matchea cualquier artículo; D97 tiene valor «una». No se parcheó.
- No se pisó F11, `_v1`, `_ajuste` ni `topics_db`. Sin merge. **No seguir a producción.** Commit `4fe4db7`. Revisor: CUMPLE CON OBSERVACIONES.

## F11 — Guion v4 (menos reglas, oficio, reparar por edición) — HECHO, **NO cumple el criterio → PARADA** (el analista lee del disco)
- Handoff `lab/hyperframes/f11/HANDOFF_F11_guion_v4.md`. Reporte `lab/hyperframes/f11/F11_REPORT.md` (revisor íntegro: CUMPLE CON OBSERVACIONES) y `compara_v3_v4.html` (teléfono OK). Textos: `NARRACION_{orleans,ycua}_v4{A,B}.md`.
- Código:
  - `script_engine/guion_v4.py`: prompt corto con marcas como dato y 8 líneas de oficio; una llamada a Pro; bloqueantes a–e con funciones existentes; reparación de UNA ronda; métricas.
  - `fase1_5 --v3 --guion v4` (o `guion_version == 4`). El camino v3 queda byte-idéntico (test con hash).
  - `m01d.regenerate_cap_v3`: `attempts` y cap vacío.
  - Tests: `test_module_f11.py` (10); suite 564 verdes + las 5 previas.
- Convergencia (escaletas fijas F7c-3 e Ycuá v1, sin notas): prompt 6.7 k → 2.8 k tokens (Orleans) y 7.9 k → 3.4 k (Ycuá). Bloqueantes finales Orleans A/B 6/7, Ycuá A/B 6/7 (criterio 0–2 ❌); ningún cap vacío ✅; A vs B ≤ 2 ✅. **Causa: el v4 escribe 450–790 palabras** (objetivo ≈ 1,500). La regeneración de caps cortos choca con la guardia léxica: 5 de 26 pasaron. Costo US$ 1.992 de 2.00.
- Abierto para Omar y el analista (no se programó nada): el largo del v4, la guardia de la regeneración, Nagin (el pool lo descarta y la escaleta lo usa), comillas simples que no ve `false_quotes`, Q20 de Liz Torres (verificada_parcial, va con nombre por la excepción §1.1).
- Salidas en `_steps/<topic>/*_v4{A,B}.json`. No se pisó `_v1`, `_ajuste`, F7c-3 ni topics_db. Sin merge. **No seguir a producción.**

## ⛔ 2026-10-23 — Omar: la narración v3 se va a REESTRUCTURAR (demasiados remiendos). No seguir con arreglos ni producción de Ycuá
- Omar canceló los arreglos quirúrgicos sobre la v1 (la corrida se mató a mitad: solo alcanzó a reescribir `_steps/f8s1-ycua-bolanos/01a_escaleta.json` = escaleta v1 + D192 a la voz; la narración vigente sigue siendo la del ajuste; v1 y ajuste guardadas como `*_v1` / `*_ajuste`). El código de `b8ff4ef` (regenerate_cap_v3, cut_phrases, replace_repeated_dates) quedó commiteado pero sin usar.
- Omar analiza con el analista (Claude web) y manda indicaciones nuevas → llegaron como F11 (arriba).

## F10 — Ajuste de Ycuá: **NO cumplió el criterio → PARADA** (esperando decisión de Omar)
- Leer `lab/hyperframes/f10/F10_AJUSTE_REPORT.md` (revisor íntegro) y `ajuste_chequeos.json`. Cierre en la cita de Liz ✅, 11:25 ✅, fecha doble en el cap 5 ❌, 26 duras ❌ (tope 12) y **cap 3 vacío** (el guionista se salteó los beats 4 y 5). No se empezó producción.
- Hecho además: regla de fechas + paráfrasis «ese domingo» (m05), juicios nuevos, título provisional «Ycuá Bolaños: el domingo que cerraron las puertas», `ParticionError` si un cap queda vacío, B1 adelantado (ventana dispersa ≠ 100 %, `script_engine/freeze_check.py`).
- Versiones: v1 en `_steps/f8s1-ycua-bolanos/*_v1.json` y `lab/hyperframes/f10/*_v1.*`; la del ajuste es la vigente en los pasos (`*_ajuste.*` en lab).
- Opciones para Omar (reporte §4): otra corrida con prompt más liviano · editor solo sobre caps flojos desde la v1 · v1 + arreglos a mano.

## F10 — Integración v3 + Ycuá Bolaños — PARADA §4.3 (superada por el ajuste de arriba)
- Rama **`f10-integracion-v3`** desde `790bec9`. Handoff `lab/hyperframes/f10/HANDOFF_F10_integracion_v3.md`; reporte `lab/hyperframes/f10/F10_PARADA_REPORT.md` (revisor íntegro); decisiones `DECISIONES_F10.md` (D1–D18).
- **§4.1 hecho:** `fase1_5 --v3` (m01a = compuerta + escaleta; m01b = guionista → editor → `m01d_particion` → juez), `--from <paso>`, contrato de 7 caps con `narration_tts` e `ids_usados`; corrida en seco de Orleans hasta assemble, verde. Arreglado `topic_researcher` (el pool v3 no llegaba al topic).
- **§4.2 hecho:** topic `f8s1-ycua-bolanos` completado en topics_db (4a–4e); guion: humano Liz Torres, pico T21 11:25, 1,235 palabras, 20 duras. Leer `NARRACION_ycua.md`, `ESCALETA_ycua.md`, `06_judge_ycua.json`.
- **Siguiente (solo con el OK):** si la nota < 8, una corrida de ajuste con notas (`fase1_5 --topic f8s1-ycua-bolanos --v3 --only m01b`, notas en `_steps/f8s1-ycua-bolanos/escaleta_notas.md`); si ≥ 8, §4.4 producción: `fase1_5 --topic f8s1-ycua-bolanos --v3 --from normalizer_gate --batch` → fase2a → fase2b --gfx (B1 antes del render; Firefox cerrado; RAM ≥ 18 GB).
- Costo hasta acá: research del topic US$ 0.99 + guion US$ 0.88.

## F8b + F9 — Research, imágenes y voz v4 — HECHO (§5 completo; Omar escucha y mira al volver)
- Rama **`f9-voz-v4`** desde `cd3f2e5`. Handoff `lab/hyperframes/f9/HANDOFF_F8b_F9.md`; reporte `lab/hyperframes/f9/F8b_F9_REPORT.md` (revisor íntegro); decisiones `DECISIONES_F9.md` (D1–D21). Sin merge, sin render, sin QA Studio.
- **Research:** antigüedad por ítem, PDF enlazado que nombra el evento, R3 con reintento, R1 con Flash alternativo. S2 Cromañón rojo → **amarillo**; S3 Vajont sigue **rojo** solo por 0 elegibles (121 datos). S1 verde.
- **Imágenes:** armas (beat de disparo desde las víctimas), pico humano, texto en el idioma del lugar, escala del pool, clichés; **grade de post** (`script_engine/image_grade.py`, `_graded.png`, solo v3 o `IMAGE_GRADE=1`). Re-humo en `compara_imagenes_f8.html` (3 columnas) y `humo/hoja_contactos_f8b.jpg`. El #7 sigue flojo.
- **Voz:** v4 + MS Narrador (`voice_id_v4` en el perfil; v2 + Bill intactos; `TTS_V2=1`), etiquetas desde el guion (`script_engine/tts_tags.py`, `narration_tts`), voz v4 normalizada a −24 LUFS. Prueba: `lab/hyperframes/f9/audio/cap2_cap4_v4_msnarrador.mp3` y `…_bill.mp3` (fuera de git).
- `max_beats` 14. Tests: 563 verdes + 5 previas. Costo medido de la tanda: US$ 2.23.

## F8 — Imágenes v3 + cierre de guion + 3 semillas — HECHO (§4 completo; Omar lee al volver)
- Rama **`f8-imagenes-v3`** desde `524573d` (punta de `f7-research-v3`). Commits: `a59ab76` §2 · `73e3613` §1 A–F · `c24de5c` humo + semillas · `db387b4` reporte · commit final con el veredicto del revisor. Sin merge, sin render, sin QA Studio.
- **Leer:** `lab/hyperframes/f8/F8_REPORT.md` (revisor íntegro), `compara_imagenes_f8.html`, `humo/hoja_contactos.jpg`, `semillas/SEMILLAS.md`, `DECISIONES_F8.md` (D1–D23).
- **§2:** escaleta con ≥ 2 beats por cap de desarrollo → 12 beats exactos en verde (`video_length`: `min_beats_dev_cap`, `max_beats`); última frase del video = cita o pregunta (blanda al editor, prompt `f8-1`).
- **§1:** Seedream 5.0 Lite (`fal-ai/bytedance/seedream/v5/lite/text-to-image`, `/edit` probado OK, sin `seed`, US$ 0.035), `pipeline.fal_concurrency` 20, 3 intentos en 429/503, `ms` por imagen. m03 v3 (`script_engine/m03_imagenes_v3.py`) solo con escaleta: ancla por beat, estilo al principio y al final, reglas de composición y sensible con validador + re-hechuras, marca `sensible` al manifest; re-encuadre solo como propuesta inerte. v2 byte-idéntico.
- **Humo:** 12/12 imágenes de Orleans f7r3, 35–68 s c/u, 68 s de pared, US$ 0.49 con la rehecha y el `/edit`.
- **Semillas:** S1 Ycuá verde (US$ 1.29) · S2 Cromañón rojo por datos (PDF equivocado de R2, caída de Pro) · S3 Vajont rojo en 0 (la regla «documento > evento + 20 años» descarta todo lo de 1963). No se eligió; S2 y S3 marcadas en el inbox.
- `config.py` (fuera de git) editado en local: `seedream_per_image` 0.035, `pipeline.fal_concurrency` 20.
- Tests: 526 verdes + las 5 fallas previas conocidas.
- Sin commitear a propósito: `diag_234_cap4.py`, `gfx_profiles/lexico_propuestas.json`, `gfx_profiles/misterio.json`, `lab/hyperframes/f7/topics_db_pre_f7b.json`.

## F7 — Research v3 — F7c-3 + F7d HECHOS (cerrado; Omar lee la columna F7c-3)
- Leer `lab/hyperframes/f7/F7c3_REPORT.md` (revisor íntegro) y `compara_orleans_v3r.html` (5 columnas).
- **F7c-3** (§9.1): 7 reglas de oficio en `script_engine/guion_v3_reglas.py` (rol, párrafo sin dato, antagonista con nombre, sin fotos, sin tráiler, ancla de lugar y fecha; eco blando al editor) y 110 + 250 × 5 + 140. Corrida (2.ª, tras arreglar un bug del ancla): 1,143 palabras, 21 duras (re-medidas con las reglas de hoy: F6c 12, F7c 29, F7c-2 23). Arregla roles, tráiler, ancla, Gusman con nombre; queda largo corto (5 caps bajo el mínimo), párrafos sin dato y el candado literal.
- **F7d** (§9.2): `researcher_steps/pool_gate.py` (verde/amarillo/rojo, `POOL_GATE.md`, umbrales en `video_length.py`) antes de la escaleta; research v3 por defecto en `topic_researcher` (`RESEARCH_V3=0` → viejo); seed rojo vuelve al inbox con motivo. Orleans: verde. `run_seed` sin probar con un seed real.
- Tests: 466 verdes (+ las 5 fallas previas fuera de la lista).

## F7 — Research v3 — F7c-2 HECHO
- **F7c-2** (validación del analista sobre F7c: «material de 9, narración 7.5–8»; §8 confirmado por Omar). Leer `lab/hyperframes/f7/F7c2_REPORT.md` (revisor íntegro) y `compara_orleans_v3r.html` (4 columnas).
  - §8: `script_engine/video_length.py` (lee `config.long_video`; `config.py` está fuera de git): 1,500 / 1,700 palabras, caps de 105 s, 16 fotos por cap como máximo (90 por video). `m01a_skeleton.CHAPTER_SCHEMA` y `m01a_escaleta.CAP_WORDS` salen de ahí.
  - Reglas duras nuevas (`script_engine/guion_v3_reglas.py`, desde `m01b_guionista.review`): fragmento de cita ≤ 25 palabras (el candado lo acepta: `evidence.anchors`), una cita por párrafo, gancho sin fotos/fechas/citas de después, juicios fuera del pool, nombre completo 1 vez por cap, repetición de 3 palabras entre caps.
  - Corrida: humano Reed, pico francotiradores (cap 5), gancho agua del inodoro. 1,252 palabras, 12 citas, 7 testigos con nombre, 11 duras (F7c: 16). A la lectura: dos roles cambiados (Ducre, Big Whappy) y juicios que la lista no ve. Notas que no entraron: 6,375 suena 0 veces (fue a pantalla), T39 no se usó y Gusman no se nombra en el cap 2. Largo 83 % del objetivo. Revisor: CUMPLE CON OBSERVACIONES.
  - Tests: 447 verdes en guion/gfx/m01/m03; 5 fallas previas (3 `01b_pauses`, 2 `m03_merge_timing`).

## F7 — Research v3 — F7c (pool v3 por la tubería v3) — HECHO
- **F7c** (pedido: validación del pool «aprobado, materia prima de 9» + 3 arreglos + corrida). Leer `lab/hyperframes/f7/F7c_REPORT.md` (veredicto del revisor íntegro) y `compara_orleans_v3r.html`.
  - Arreglos: `presente_en` por párrafo (±500), elegibles re-armados (12); población con todas sus variantes (oficial 6,375, ACLU/sheriff); `pool["digest"]` y `m01a_escaleta.pool_section` lo usa (flag `ESCALETA_DIGEST`): prompt de escaleta 18.7 k tokens.
  - La corrida destapó 3 problemas del pool contra los validadores de F6 (cita de una palabra, descartes como «personajes», cifras con punto de miles): arreglados en el pool.
  - Resultado (corrida 5, sin notas del analista): más testigos y citas (Reed humano; Richard, Reyes, Burton), pero 940 palabras, densidad 1.70 y 16 duras (F6c: 1,070 / 2.15 / 4). Las duras: el guionista parafrasea citas largas y el candado literal las rechaza.
  - **Pendiente de confirmar:** el §8 del handoff (parámetros de largo 1,500 palabras, tope de fotos en m03, lat/lon en el digest, geocoder) no estaba en el pedido de chat: no aplicado.

## F7 — Research v3 (leer documentos) — F7a y F7b HECHOS (pool aprobado por el analista)
- **Leer:** `lab/hyperframes/f7/F7b_pool.md` (métricas contra f6v3, costo, lo que mirar; veredicto íntegro del revisor: CUMPLE CON OBSERVACIONES) y `F7a_fuentes.md`.
- **Pool** `lab/hyperframes/f7/00_pool_v3.json` (= `data/scripts/_steps/ba6c3cac-f7r3/00_pool_v3.json`): 558 datos (6.1× f6v3), 152 eventos (28 con hora), 188 citas (162 verificadas literal), 25 citas de testigos con nombre verificadas (20 personas), 13 elegibles como humano, 100 % con doc_id + posición. 10 documentos (HRW 2005 bajó por Wayback en el reintento).
- **Abierto:** costo ≈ US$ 2.6–2.8 por tema (> 2.5); cifras canónicas casi vacías; prompt de la escaleta ≈ 63 k tokens con este pool (riesgo 4: propuesta de resumen por documento para F7c); `RESEARCH_V3` sin cablear en `topic_researcher`; 4b–4e no corridos con el pool; faltan BBC, prensa de 2005 y el fallo Waganfeald.
- **Topic** `ba6c3cac-f7r3`: `01_facts_sources.json` (f6v3 + pool nuevo) y entrada nueva en `data/topics_db.json` (copia de f5v2); respaldo `lab/hyperframes/f7/topics_db_pre_f7b.json` sin commitear.
- Re-armar el pool gratis: `python -I lab/hyperframes/f7/f7b_pool_orleans.py --sin-llm --revalidar F01,F03,F08,F09`.
- Handoff: `lab/hyperframes/f7/HANDOFF_F7_research_v3.md`. Rama **`f7-research-v3`** desde `c7da0ba` (f6-guion-v3). Sin merge a main.
- Código: `researcher_steps/research_v3.py` (R1 descubrimiento, R2 descarga, R3 extracción, R4 merge, R5 verificación). Topic nuevo `ba6c3cac-f7r3` (datos en `data/scripts/_steps/ba6c3cac-f7r3/`, fuera de git).
- **F7a** (`lab/hyperframes/f7/f7a_fuentes_orleans.py` → `F7a_fuentes.md`): 10 documentos bajados. R1: las URLs salen SOLO del grounding (el modelo pone la ficha; las que no fichó, Flash); Pro con temperatura 0.7 (con 0.0 contestaba de memoria, sin grounding). Faltan: BBC, Times-Picayune, Toledo Blade y el fallo Waganfeald (no salen en el grounding).
- Ojo: `python -I` ignora `PYTHONIOENCODING` (los runners hacen `sys.stdout.reconfigure`). archive.org devuelve 429 si se le pega seguido: no reintentar en bucle.

## F6 — Guion v3 — F6c CERRADO COMO LABORATORIO; F6d/F6e pendientes hasta F7 (decisión del analista, 2026-10-21)
- Handoff: `lab/hyperframes/f6/HANDOFF_F6_guion_v3.md`. Rama **`f6-guion-v3`**, desde `45c052c`. Sin merge a main.
- **Cierre:** el analista paró F6 acá: no se regeneran la escaleta ni la narración. F6c queda como laboratorio; F6d (partición en 7 caps, `regenerate_caps` v3, m05 ampliado) y F6e (comparación) esperan a F7 (research v3: fuentes con URL, documentos bajados, pool extraído leyéndolos). F7 corre en una sesión nueva, rama `f7-research-v3` desde `f6-guion-v3`, con el handoff `lab/hyperframes/f7/HANDOFF_F7_research_v3.md`.
- **Último commit de F6:** `7ec2025` («feat(f6c): …») + este cierre de ESTADO_SESION.
- **Leer:** `lab/hyperframes/f6/F6c_REPORT.md` (A/B/C, lo que queda, veredicto íntegro del revisor: CUMPLE CON OBSERVACIONES), `NARRACION_orleans_v3.md`, `ESCALETA_orleans.md` (f6b-4) y `F6c_verificacion.md`. Antes: `F6b3_REPORT.md` y `F6ab_REPORT.md`.
- **Frenos (§5) intactos** (+ `m05_narrative` y `m01b_narrator` sin tocar: se usan).
- **A — verificación literal:** `researcher_steps/verify_quotes.verify_literal`. Fuentes bajadas en `data/scripts/_steps/ba6c3cac-f6v3/fuentes/` (BBC/rebelion 2006, PDF de la ACLU 2006, The Lens 2025).
  - Verificadas: Q03 (Burton) y Q04 (Norman, literal BBC «Simplemente abandonaron la cárcel»); D95 nuevo (103 días).
  - Fuera del pool: Q05 (atribución errónea) y Burnley / Chad Joseph (contaminación).
  - Sin verificar: Q06, Q07, Q11–Q13.
- **B — escaleta f6b-4:** reglas `contador`, una cifra en pantalla una vez, pregunta del cap 7 obligatoria, cierre sin eco, `escaleta_solo_apoyo`, citas sin verificar fuera de pantalla.
  - Pico: los cadáveres en el cap 4. 517 en el cap 5 con contador. Norman en los caps 2, 3 y 7.
- **C — guionista y editor:**
  - `script_engine/m01b_guionista.py`: Pro, texto completo, best_of_2, `review` con m05 por cap + reglas v3.
  - `script_engine/m01c_editor.py`: guardia léxica + validadores; un párrafo rechazado vuelve al original.
  - Narración de Orleans (f6c-3): 1,072 palabras, 4 duras; el editor aceptó 10 de 19 cambios.
- **Pendiente para el analista (antes de F6d):**
  - citas en fragmento contra `cap_review`;
  - invenciones semánticas que ningún validador ve (propuesta: validador semántico + regla «nada de pensamientos de personas reales»);
  - el cap 6 en los diques;
  - el costo (≈ US$ 1.9 en esta tanda).
- **Tests:** `test_module_f6a` (3), `f6b` (31) y `f6c` (4). Suites: 448 verdes + 3 viejas.

## F5f — Cierre de Orleans (laboratorio) — CERRADO, PARADA (el analista valida desde disco)
- **Rama:** `f5-guion-v2`. **Último commit:** «F5f: cierre Orleans (lab)» (`git log -1`), sobre `cc625e2` («wip: F5f pre-cierre»). Omar no publica este video.
- **Sin mergear a main** (`main` = `43f528a`, intacta; no se hace merge sin OK de Omar): la cadena `f2-gfx-director` → `f3-lab-identidad` → `f5-guion-v2` (61 commits por delante de main). Quedan aparte `f1-gfx-layer` y `lab/kling-transform-probe`.
- **Leer:** `lab/hyperframes/f5/F5f_REPORT.md` (tabla por cap, lo que no salió y el veredicto íntegro del revisor: CUMPLE CON OBSERVACIONES) y `DECISIONES_F5.md` U1–U11.
- **Hecho:**
  - Arreglos 1–6:
    - sustantivo con ícono sobre adjetivo;
    - palabras del tema a peso 1;
    - reservados con prioridad y motivo de choque;
    - bloque `quote_card`;
    - eco de cifra y 15 s entre recortes;
    - nivel de agua desde un reservado;
    - titulares sin comilla abierta.
  - D15 como reservado del ch02, en el skeleton (respaldo en `produccion/01a_skeleton_pre_f5f.json`).
  - Reloj que cambia de fecha.
  - Render de la capa gfx solo de ch02, ch05, ch06 y ch07 (`render_f5f_caps.py`, `--only-cap --reuse-visuals`). Capas en `_fase2b_work/chNN_gfx.mp4`; las anteriores, en `_bak_f5f_pre/`; hojas en `lab/hyperframes/f5/produccion/hojas_f5f/`.
  - Sin render completo: el `_final_gfx.mp4` sigue siendo el de F5e.
- **Quedó solo en simulación** (`produccion/SIM_F5f.md`, `_sim_gfx/`):
  - ch01: fuera el 6,375 y T04 a los 14.7 s;
  - ch04: T16 y el reloj 30 AGO → 2 SEP.
- **Ojo:** durante la sesión se regeneraron fotos desde el botón «arreglar» de QA Studio: ch01_supp_04, ch03_img_02 y ch03_img_10 (backups en `assets/_qa_backups/`). Eso borró `ch01_hybrid_visual.mp4` y `ch03_flux_visual.mp4`; un render futuro los rehace con DepthFlow. QA Studio sigue abierto en :8000 desde F5e.
- **Tests:** 410 verdes + 3 fallas viejas de `01b_pauses`.
- **Archivos sueltos sin commitear (a propósito):**
  - `gfx_profiles/misterio.json`: el render promueve solo palabras al léxico (por ejemplo «negrura»: 3);
  - `gfx_profiles/lexico_propuestas.json`;
  - `lab/hyperframes/f5/produccion/topics_db_pre.json`;
  - `diag_234_cap4.py`: no es nuestro y nunca se commitea;
  - `lab/hyperframes/f5/produccion/qa_studio.out`;
  - `data/scripts/_steps/ba6c3cac-f5v2/01a_skeleton.json` (fuera de git; D15 aplicado).
  - Además, unos 135 sueltos de laboratorio ajenos a F5 (`_compare_*`, `_lab_*`, `_probe_*`, mp4).

## F5e — Arreglos de capa gfx tras ver el video — render hecho, PARADA tras el commit final
- Pedido (Omar/analista, después de ver Orleans v2): solo capa gfx, sin tocar guion ni imágenes.
- **Hecho y commiteado en `wip(f5e)`:**
  - G2: titular de recorte hasta 12 palabras; de 9 a 12 baja un cuerpo (`archive_head_max_words_pool`, `gfx_project.archive_head_px`). Los datos reservados para pantalla van primero y, si chocan, se corren dentro de la escena (`gfx_pool._free_slot`); un reservado entra aunque la voz no lo nombre (`_sentence_for(reserved=True)`).
  - G1: el crítico recibe dos cuadros (foto sola + bloque dibujado) y no puede decir «repite» por su propio sello (`gfx_critic`, prompt `g1-snap-2`).
  - Sellos: token `stamp_nouns_only`; el director de intensidad devuelve `clase` y `neutra` (`gfx_intensity` PROMPT_VERSION `f5e-1`). Fuera los verbos (`is_verb_form`, `stamp_lexicon`) y las neutras (estrella, suerte, estruendo, agujero).
  - Contador: un contador por hecho (`gfx_pool.count_groups` / `pool_count_up`): 517 y «más de 500» son el mismo hecho; se anima 517 en el primer cap que lo dice (ch05) y se saca el 500 del ch07.
  - m00: `topic_researcher.MAGNITUDE_SECTION` ([DATOS DE MAGNITUD]) solo en el ángulo técnico; humano y misterio quedan idénticos. Solo el prompt; Orleans no se re-investiga.
  - QA Studio: marca «↻ regenerar» por foto (`/mark`, `/marks` → `output/<id>/assets/_qa_marks.json`). `lab/hyperframes/f5/regen_marcadas.py` regenera solo las marcadas con el mismo prompt, otra semilla y sin validador de visión (`qa_studio_server._reseed_core`).
  - Sincronía: `lab/hyperframes/f5/sync_check.py` (faster-whisper del venv `C:/CLAUDE_PROJECTS/viral-video-pipeline/.venv`) → `produccion/SYNC_v2.md` y `SYNC_ba6c3cac_v1.md`. v2 da como v1: mediana +100 ms en los 7 caps, igual en v1, que no tenía aviso (sesgo de Whisper); p95 240–500 ms y máximo 1.04 s (ch06 «inició»). El ASS coincide con los timestamps (el pre-pad de 1.8 s solo va con `--hook`, que no se usó). No se miró a ojo: es una medición.
  - Tests: `test_module_f5e.py` (6). Suites: 397 + 6 verdes, 3 viejas de 01b_pauses.
- **Render hecho:** `produccion_orleans_v2.py --etapa render_gfx` (fase2b `--reuse-visuals --keep-segments --gfx --gfx-sparse --gfx-quality looks`): rc=0 en 41.0 min, RAM 18.7 GB, Firefox cerrado. Logs en `lab/hyperframes/f5/produccion/render_gfx.out` y `fase2b_gfx.out`.
  - **Nuevo final:** `output/ba6c3cac-f5v2/ba6c3cac-f5v2_final_gfx.mp4` (571.2 s, US$ 0.02 de Gemini). El anterior quedó como `…_final_gfx_f5d.mp4`, y capas, planes, hojas y cues anteriores en `_fase2b_work/_bak_f5e_pre/`.
  - **Resultado:** recortes 2 → 5; reservados en pantalla T04 (ch01) y T22 (ch07); T16, T19 y T23 no entraron porque chocan en toda la escena. Ningún sello neutro ni verbo. Crítico 24/27, 0 «repite» por su propio sello. Contador 517 en ch05, sin el 500 en ch07; el 6,375 del ch01 lo limpió el pico.
  - Hojas de contactos en `lab/hyperframes/f5/produccion/hojas_f5e/`. Reporte en `lab/hyperframes/f5/F5e_REPORT.md`; decisiones Q1–Q7 en `DECISIONES_F5.md`.
  - **QA Studio:** abierto en http://127.0.0.1:8000 (topic `ba6c3cac-f5v2`). Todavía no hay marcas.
- **Falta:**
  1. Revisor-handoff, con el veredicto íntegro en `F5e_REPORT.md`, y commit final `feat(f5e)`. Después, PARADA.
  2. Cuando Omar marque fotos en QA Studio: `PYTHONIOENCODING=utf-8 python lab/hyperframes/f5/regen_marcadas.py --topic ba6c3cac-f5v2` y después `produccion_orleans_v2.py --etapa render_gfx`. Antes, borrar o renombrar `_bak_f5e_pre` para que el respaldo nuevo no se saltee, o pasar otro tag.
- No commitear: `diag_234_cap4.py`, `gfx_profiles/lexico_propuestas.json` (lo decide Omar), `lab/hyperframes/f5/produccion/topics_db_pre.json`.

## Producción de Orleans v2 — Omar vio el video; pidió F5e (arriba)
- **Video:** `output/ba6c3cac-f5v2/ba6c3cac-f5v2_final_gfx.mp4` (571.2 s, gfx looks disperso, identidad y crítico activos).
- Leer `lab/hyperframes/f5/F5_PRODUCCION_REPORT.md` (revisor íntegro) y `DECISIONES_F5.md` P1–P9.
- **Hecho:** retoque de los caps 5 y 6; bloque G (G1 crítico sobre snapshot, G2 titular ≤ 8 palabras, G3 `verify_crop` del zoom final, G4 íconos espiral y rayo tachado); TTS, imágenes (81 + Veo ch01/ch07) y un solo render en 77.8 min.
- **Costo de esta tanda:** ≈ US$ 6.2 (imágenes 3.24, Veo 0.48, Gemini ≈ 2.0, TTS ≈ 0.21, íconos 0.27).
- **Abierto:**
  - G1 confunde el sello dibujado con la foto (2 bloques sacados de más);
  - G2 dejó 2 recortes en todo el video;
  - aviso de alineación del TTS sin verificar a ojo;
  - tinte «lavado» del mood muerte.
- Tests: 397 verdes + 3 viejas.

## F5d — Último ajuste antes de producción — superado (producido)
- Leer `lab/hyperframes/f5/RESUMEN_F5d.md` (revisor íntegro) y `DECISIONES_F5.md` M1–M11.
- **Hecho:**
  - cifras canónicas (6,375 oficial; la contradicción solo en el cap 7);
  - fechas como regla dura;
  - largo +15 % con Pro y paráfrasis permitida;
  - datos reservados para pantalla (`pantalla_ids` en el skeleton);
  - count_up solo con cantidades;
  - línea «ningún menor en celdas de adultos» en el canon de m03.
- **Resultado:**
  - ningún cap con reglas duras; densidad por id 1.97; adjetivos 2.58; 1165 palabras; cliffhangers 6/6;
  - pantalla: 6 recortes, los caps 6 y 7 ya tienen;
  - 3-gramas 8.7 % (cap 7).
- **Costo:** Pro US$ 1.46 (2 corridas). Tests: 393 verdes + 3 viejas.
- **Siguiente, solo con el OK del analista:** producción completa de Orleans v2 (imágenes + render con gfx). Antes de renderizar, Firefox cerrado y RAM > 14 GB (memoria).

## F5c — Solo narración: skeleton congelado, narrador Pro, mejor de 3 — superado por F5d
- Leer `lab/hyperframes/f5/RESUMEN_F5c.md` (revisor íntegro) y `DECISIONES_F5.md` L1–L8. La pantalla y §1.6 de F5b no cambian.
- **Hecho:**
  - skeleton de F5 congelado (token `skeleton_frozen`, ids traducidos al pool de F5b; Hubert y Schwarz fuera);
  - con pool, el narrador es Gemini Pro y elige el mejor de 3 por cap (puntaje del analista);
  - reglas duras y blandas en el prompt y en `cap_review` (no inventar, no contaminar);
  - 8 frases nuevas de relleno prohibido.
- **Resultado:**
  - densidad por id 2.16 (F5b 1.26); cliffhangers 6/6; Gusman desde el cap 1;
  - en contra: 1017 palabras, adjetivos 1.87 y 3-gramas 8.6 %;
  - pantalla: 0 fallas S1–S5, 3 recortes;
  - prompts: el reemplazo del niño es ch05 imagen 6, en el centro juvenil; queda ch04 imagen 13 (adolescente en celda de adultos).
- **Costo:** Pro US$ 0.69. Tests: 385 verdes + 3 viejas. Respaldos de F5b: `lab/hyperframes/f5/v2_f5b/`, `output/ba6c3cac-f5v2/_bak_f5c_pre/`.

## F5b — Arreglos de la validación (N1–N5, S1–S6) — superado por F5c en la narración (la pantalla sigue)
- Pedido: `lab/hyperframes/f5/VALIDACION_F5.md` §7. Leer `lab/hyperframes/f5/RESUMEN_F5b.md` (revisor íntegro) y `DECISIONES_F5.md` K1–K20.
- **Hecho:**
  - pool: filtro de relevancia (fuera la posada de 1902 y el médium), personajes solo si actúan (fuera Schwarz y Hubert) y mayúsculas;
  - narrador: declara `datos_usados` (las métricas cuentan por id), cada dato una vez por cap, adjetivos entre 2 y 4/100;
  - pantalla: cláusula completa, cronología, dedupe por hecho (sin el cap siguiente), ícono por mapa literal (token `icon_literal_only`), metros;
  - §1.6: bloque UBICACIONES DOCUMENTADAS en el canon de m03 (FRENOS respetados) y 97 prompts de v2 regenerados (texto).
- **Resultado:**
  - pantalla v2 sin fallas S1–S5;
  - narración con menos datos que la v2 de F5: por hecho, 1.12 contra 2.01 (v1: 0.86); por id, 1.26;
  - P5 (caps 6 y 7 sin recorte) sigue;
  - dos prompts con un niño solo en celda de adultos (ch01 supp 3, ch07 Veo).
- Tests: 379 verdes + 3 viejas de `01b_pauses`. Se reproduce con `correr_f5_orleans.py --etapa todo`. Respaldos de F5 en `lab/hyperframes/f5/v2_f5/`, `output/ba6c3cac-f5v2/_bak_f5b_pre/` y `output/ba6c3cac-a091…/_fase2b_work_f5sim_v1_bak_f5b`.

## F5 — Guion v2 (`lab/hyperframes/f5/HANDOFF_F5_guion_v2.md`) — validado por el analista (`VALIDACION_F5.md`): pidió F5b
- Commits en `f5-guion-v2`: `66ee44b` §1.1 · `2be6c11` §1.2 · `fc955ef` §1.3–§1.5 · `e18e656` §2 · `e7b661c` §3.
- **Hecho:**
  - §1.1 `evidence_pool` en el research (`researcher_steps/evidence_pool.py`, lo llama `step_4a_facts`);
  - §1.2 skeleton con datos por cap, personajes y cliffhanger (`m01a`);
  - §1.3 narrador con los datos del pool y reglas A–G (`m01b`);
  - §1.4 normalizer: horas AM/PM, dólares, %, comillas y siglas (`tts_normalizer`, `m02_5`);
  - §1.5 juez narrativo determinista (`script_engine/m05_narrative.py`);
  - §2 pantalla desde el pool (`script_engine/gfx_pool.py`: candado, recortes y datos, ícono por contenido, reloj, pregunta del cliffhanger) + `apply_gfx(plan_only=True)`;
  - §3 guion v2 de Orleans, comparación y simulación del director sin render.
- **No hecho:** §1.6 (`m03_visual` con lugares y objetos del pool; era opcional). Tampoco los íconos espiral y rayo tachado (F5 es sin imágenes).
- **Dónde está:**
  - comparación v1/v2: `lab/guion/compara_orleans.html` (generador: `lab/guion/build_compara_orleans.py`);
  - cues de la simulación: `lab/hyperframes/f5/cues/gfx_cues_v1_chNN.md` y `gfx_cues_v2_chNN.md`;
  - tablas: `GUION_v1_v2.md` (guion) y `SIM_v1_v2.md` (director);
  - reporte: `lab/hyperframes/f5/F5_REPORT.md` (revisor íntegro por sección: CUMPLE CON OBSERVACIONES);
  - decisiones: `lab/hyperframes/f5/DECISIONES_F5.md` (J0–J44);
  - copia v2 del research: `data/scripts/_steps/ba6c3cac-f5v2/` y `data/scripts/ba6c3cac-f5v2.json` (fuera de git; copia versionada en `lab/hyperframes/f5/v2/`);
  - simulaciones: `output/ba6c3cac-f5v2/_fase2b_work/` (v2) y `output/ba6c3cac-a091-41c0-8dad-afd2f4364747/_fase2b_work_f5sim_v1/` (v1).
  - Se reproduce todo con `lab/hyperframes/f5/correr_f5_orleans.py --etapa todo`.
- **Resultado:**
  - guion: densidad 1.36→3.29, adjetivos 6.2→2.9, datos en más de 2 caps 2→0, Gusman en 6 caps, 41 datos del pool (v1: 12);
  - simulación: recortes del pool 0→7 (**0 con fuente**), «repite» del crítico 12→4, reloj en 3 caps.
- **Abierto:** cliffhanger estricto 4 de 6; contradicción 6,375/6,500 sin contar; año del kicker desde `fecha` no literal en los datos (D72); umbral de adjetivos 3.6 a validar; nombres nuevos sin revisión fonética para TTS.

### Decisiones F5 (J1–J44) en 10 líneas
1. **Pool (J1–J7).** Una llamada Flash por bloque, sin tope. Todo literal del bloque (lo que no, se descarta). La fuente sale solo de las [FUENTES CONSULTADAS] del bloque y si el ítem la nombra; si no, null. Limpieza y merge entre bloques con IDs del código. Geocodificación anclada a la ciudad principal (≤ 400 km; siglas no). Caché de la respuesta cruda.
2. **Skeleton (J8–J13).** `_evidence_plan` con ≥ 3 datos nuevos y ≤ 1 puente por cap, cronología en orden en los caps 2–6, antagonista obligatorio y cliffhanger = ID del dato del cap siguiente. Lo que Flash erra se repara en código y queda en `_evidence_repairs`. Sin pool, el prompt es idéntico al de antes.
3. **Juez (J14–J19).** «Dato usado» = anchor literal. Las cifras valen en dígitos o en palabras (`num_es.py`). Un evento cuenta con su fecha más una palabra de contenido en la misma oración. Densidad y repetición cuentan solo datos duros. El antagonista exigido es el principal.
4. **Adjetivos (J17–J18).** Heurística sin etiquetador. El umbral se recalibró de 8 a 3.6: la heurística mide v1 en 6.2 contra el 14 del analista.
5. **Narrador (J20–J23, J43).** Datos asignados en el prompt (usa 3–6) y reglas A–G validadas por `cap_problems`. Si falla, reintenta (3 intentos). Si sigue fallando solo por reglas del pool, se acepta y queda en `_f5_violations`. Un último intento que rompe el largo cede ante uno anterior que solo fallaba el pool. Citas con el autor dentro de la oración.
6. **Normalizer (J24–J26).** `normalize_pool_forms` determinista, después de los spans del auditor. Siglas ACLU, HRW, DOJ y FEMA. `persist_dict=False` para no tocar el diccionario global en las pruebas.
7. **Pantalla (J28–J31).** Todo detrás de `if pool` (los guiones viejos salen igual). El candado acepta el pool. Recortes y datos desde el pool del cap ±1, nunca desde la narración. Kicker = fuente → fecha → sin recorte (sin el año de la voz). Dedupe por `pool_id` entre caps.
8. **Ícono, pregunta y reloj (J32–J36).** El ícono sale del tema del dato, nunca de la voz (cifras de personas sin ícono; espiral y rayo pendientes). La pregunta sale del cliffhanger (respaldo: F4c). El reloj sale de la cronología solo si el cap avanza de fecha. Los lugares con lat/lon quedan para el mapa de F6.
9. **Prueba (J37–J42).** `plan_only` sin render. Topic de copia `ba6c3cac-f5v2` con los `verified_facts` de v1 idénticos. Fotos de v1 como proxy: palabras de v2 en la duración de v1 y escenas en los mismos cortes, con anchors sintéticos. `record_proposals` apagado en las simulaciones. md5 de los archivos globales iguales antes y después.
10. **Proceso (J0, J27, J44).** Rama desde F4e porque F4f no existe. Los heredocs de Git Bash convierten `\b` en 0x08 (origen de los bugs de F4c y F4d): los parches con barras van por Write y se chequean bytes de control. §1.6 no se hizo.

## F4e — Marca de esquina apagada, crítico visual (6b), hoja de contactos — ESPERANDO A OMAR
- Commit F4e (último). Leer `lab/hyperframes/f4e/RESUMEN_F4e.md` (revisor íntegro: CUMPLE CON OBSERVACIONES), `DECISIONES_F4e.md` (I1–I14), `TABLA_critico.md`, `hoja_contactos_ch02/ch05.jpg`.
- `script_engine/gfx_critic.py`: Gemini juzga cada bloque (cuadro real + voz + bloque en texto) → suma/repite/estorba; solo pasan los «suma». Token `visual_critic`. Few-shot `gfx_profiles/misterio_critico_fewshot.json`. ch02 6/7, ch05 6/8.
- Abierto: el crítico no ve el bloque dibujado → pasaron el recorte truncado en la tarjeta (ch02 1:00.7, I12) y la caja del zoom fuera de los pies (ch02 1:17.9, I13).
- Marca: `channel_bug.corner.enabled=false` (queda el cierre). md5 sin `--gfx` = `38e5ba14…` ✔. Tests: 316 verdes. Respaldo F4d: `_fase2b_work/_bak_f4e_pre`.

## F4d — Pico con preferencia, recortes por cláusula, marca +1 px — superado por F4e
- Commit F4d (último). Leer `lab/hyperframes/f4d/RESUMEN_F4d.md` (revisor íntegro: CUMPLE CON OBSERVACIONES), `DECISIONES_F4d.md` (H1–H11), `TABLA_antes_despues.md`.
- ch02 vuelve al nivel de agua 4.6 m con PUTREFACTA de palabra del pico; los recortes recuperan la fecha y «aguas residuales». ch05: «cadáveres flotando…» con kicker «1 de septiembre» (HRW NO: el research no le atribuye ese fact, H8).
- Marca `corner_dilate_px: 1`; caché del PNG ahora distingue el engrosado (H10). `\b` de `gfx_icons/__init__.py:70` arreglado.
- md5 sin `--gfx` = `38e5ba14…` ✔. Tests: 311 verdes. Respaldo del estado F4c: `_fase2b_work/_bak_f4d_pre`.

## F4c — Doctrina del director + marca sin pixelado — superado por F4d
- Commits: `c05ce25` A (reglas R1–R8 del `ANALISIS_director_trace_2026-10-20.md`; R9 saltada por Omar) · `0acff03` B (marca de la esquina a 4× + lanczos) · resumen (último commit).
- Leer `lab/hyperframes/f4c/RESUMEN_F4c.md` (veredicto del revisor íntegro: CUMPLE CON OBSERVACIONES), `DECISIONES_F4c.md` (G1–G23), `TABLA_antes_despues.md`, `capturas/` (recortes 1:1 de la marca).
- Solo `--only-cap ch02/ch05` (3 corridas; la que vale es `corrida/`). Candado sin `--gfx`: md5 `38e5ba14…` ✔. Tests: 305 verdes.
- Abierto para Omar: (1) el pico se movió por variación de Flash (ch02 sin nivel de agua; intensidad en caché); (2) Flash elige recortes flojos aunque cumplen R6 (arreglo propuesto G22: elegir solo entre las 3–4 mejores); (3) marca más suave pero maciza con +2 px (probar `corner_dilate_px: 1`); (4) bug 0x08 sin tocar en `gfx_icons/__init__.py:70` (G17); (5) léxico: caos/nadie/nunca a peso 1 (G9).
- Tokens nuevos del motor (OFF por default, misterio ON): `peak_word`, `doc_clippings`, `callout_no_repeat`, `question_rubric`. Reservas activas con capa `minima` + SFX propio (brasa, rumor, zumbido, viento, vacio).
- Respaldos: `_fase2b_work/_bak_f4c_pre` (planes/capas F4b de ch02/ch05), `_bak_f4c_v1`, `_bak_f4c_v2`.

## F4b — Marca + director inteligente (HANDOFF_F4b) — ESPERANDO A OMAR (merge)
- Commits: `1762916` §1 intensidad · `f1af5de` §2 fragmentos · `93064c8` §3 zoom foto-primero + §4 íconos gratis + código de la marca (apagada) · §5 render completo (último commit).
- Leer `lab/hyperframes/f4b/RESUMEN_F4b.md`, `F4b_REPORT.md`, `DECISIONES_F4b.md` (E1–E42).
- Marca: candidata 3 elegida por Omar, cosida en `d8d87c6` (llama en el farol, esquina 6 % / 0.7 / +2 px / halo; cierre 2.5 s + negro). Final 715.6 s. Posible ajuste: `corner_dilate_px` 1 si la esquina se ve maciza (re-cosido + re-ensamble ~13 min, sin HyperFrames).
- Falta: merge F4+F4b a `main` con el OK de Omar.
- Regla de Omar: Firefox cerrado en TODO render, siempre (memoria `firefox-cerrado-en-todo-render`).
- game-icons se baja con `script_engine/gfx_icons/fetch_game_icons.sh` (fuera de git).

## F4 — Identidad en producción (HANDOFF_F4, modo nocturno) — ESPERANDO A OMAR (PARADA 2)
- Commits: `4f05f66` §1 (identidad de Omar en el perfil + pregunta concreta) · `f5c54bd` §2 (`gfx_style`: el director aplica la identidad; ch05 PARADA 1) · `b8e6c8e` §3 (el render SÍ escala el video; zoom sin congelado) · `321c489` §4 (render completo, AB_f4).
- Leer `lab/hyperframes/f4/RESUMEN_NOCHE_F4.md` (3 preguntas para Omar), `F4_REPORT.md`, `DECISIONES_F4.md` (D1–D22).
- Falta: §5 merge a `main` + docs (REPO_MAP, ARCHITECTURE, DOC_MAESTRO v1.2, CLAUDE.md) **solo con OK de Omar**; incremental sin medir; pregunta de ch06 abstracta («indiferencia»).
- Final: `output/ba6c3cac…/…_final_gfx.mp4` 712.2 s · `AB_…_f4.mp4`. Respaldos F3/F2b en `_fase2b_work/_bak_f4_pre*/`.

## F3 — Laboratorio de identidad: qué quedó hecho (commits en orden)
- **§A `0902908`** servidor `gfx_lab_server.py` (:8765) + historia (Whisper + audio + fotos) + preview real (`write_project` + player/runtime pineados).
- **§B `9d65b49`** `catalogo.json` (43 piezas), `sugerencias_ch02.json` (borrador de 18), miniaturas CSS, tokens en vivo + candado literal en el preview.
- **§C `04a6025`** ✔/✖, deshacer, resumen en vivo, **Guardar identidad** (`script_engine/gfx_identity.py`).
- **§F `edf5221` / §F2 `2bdfd44`** pantalla tramo por tramo: Probar = un objeto solo sobre la foto fija; "Ver este tramo con todo" y "Ver capítulo completo" solo con lo aprobado; movimiento sobre el PNG (alejar/quieta nuevos en el templater); solo formas que se ven. Vista vieja en `?modo=experto`.
- **Mood agua `d4ed4e5`** sin cáusticas: sombra que sube 1 s / se mantiene / baja + bordes; los otros 3 moods revisados.
- **Íconos + pregunta `beb2b8f`** ícono siempre en bloque (L 360 px + palabra al lado + fuente, zona oscura, sombra + grano), "con ícono" en dato/recorte, ícono propuesto por palabra literal + selector de los 12; **pregunta de cierre automática** (`script_engine/gfx_question.py`, Flash + validador, 2 reintentos, `generated: true`) con **pausa real de 3 s** + drone en fase2b y en el lab.
- **Pico `9d36be7`** (`script_engine/gfx_peak.py`): pico = frase con más palabras de peso 3, UN bloque grande y ±5 s libres; **nivel de agua** (4.6 m → 60 %, cifra literal, 1 por video); **reloj** «29 AGO · 2005» en la esquina libre; zoom de evidencia **+ latido**; **corte a negro 1 s**; ch02 cargado por default; fix del zoom (HyperFrames no escala `<video>` → cuadro congelado); candado 409 entre pestañas del lab.
- Render ch02 `--gfx` actual: **101.6 s** (97.6 voz + 3 pregunta + 1 negro), respaldado en `_fase2b_work/_bak_f3_pregunta/ch02_segment_only.gfx_pico.mp4`.

## Pendiente
- **Malla del mood agua:** corregida en `d4ed4e5` (sin `repeating-*gradient`, test que lo impide), **falta que Omar la confirme a ojo** en el tramo 5. Aparte, muerte se ve "lavado" (desaturación, no patrón): decide Omar.
- **Pregunta más concreta:** la generada para ch02 («¿Cómo el encierro transformó la oscuridad moral de los prisioneros?») cumple el contrato pero es abstracta; ajustar el prompt de `gfx_question` para que apunte a un hecho concreto del cap siguiente. La pregunta escrita a mano por Omar («Quien fue el culpable?») no pasa por el validador.
- **Video completo con pausas:** no se renderizó el video entero con las pausas de cierre (concat + música por cap con `extra_sec`); solo ch02 y tests.
- **Golpe de zoom sobre video:** punch-in, empuje del mood muerte y "corte + golpe" no escalan el clip de video en el render (mismo límite de HyperFrames que el zoom). Se propuso como sesión aparte, pero **no arrancó**: Omar tiene que confiar el repositorio en Claude Desktop (botón "Trust repository" en esa sesión).
- ~~Perfil guardado por Omar SIN commitear~~ → resuelto en F4 §1 (`4f05f66`, D1–D4). Texto original: `gfx_profiles/misterio.json` modificado (acento `#c2302f`, golpe 1.015, `anim_figure` stamp, sello 84 px, `blocks.chapter_question.enabled = true`, clave `identity` con 10 marcas). Con ese perfil fallan 8 tests que fijan la calibración vieja, y `chapter_question.enabled` vuelve a prender la regla de pregunta del director (choca con C56: la pregunta la genera `gfx_question`). Decidir: aceptar los valores y actualizar los tests, y apagar ese bloque.
- §D (plantillas nuevas, Render desde el lab, regenerar ícono) y §E (director que consume identidad + golden; probar en ch05) del HANDOFF_F3 siguen sin hacer.

## Dónde está todo (F3)
- **Identidad guardada por Omar (2026-10-20 01:20):** perfil `gfx_profiles/misterio.json` (sin commitear; respaldo del anterior en `gfx_profiles/misterio.json.bak_f3_20261020_012038`), plan dorado `gfx_profiles/misterio_golden_ch02.json`, resumen `lab/identidad/IDENTIDAD_misterio.md` (ambos sin trackear).
- Sesión de Omar en el lab: `lab/identidad/plan_ch02_lab.json` (+ respaldos `.omar_2231`, `.omar_0004`, `.omar_antes_pico`); no se commitean.
- Pregunta de cierre en caché: `output/…/_fase2b_work/gfx_question_ch02.json`; pausa por cap: `gfx_pause_<cap>.json`.
- Docs: `lab/hyperframes/f3/` → `HANDOFF_F3_laboratorio_identidad.md`, `HANDOFF_F3b_lab_foto_por_foto.md`, `F3_REPORT.md` (veredictos íntegros del revisor por sección), `DECISIONES_F3.md` (C0–C67), `capturas/` (iconos, moods, pico), logs de render y md5.
- Código F3: `gfx_lab_server.py`, `lab/identidad/` (`index.html` + `lab_foto.js`/`.css` = tramo por tramo, experto.html = vista vieja, lab.js = núcleo), `script_engine/gfx_identity.py`, `gfx_question.py`, `gfx_peak.py`.

## Decisiones F3 (C1–C67) en 10 líneas
1. El lab usa `http.server`, el player/runtime pineados y `write_project`: el preview es el templater real, nunca una copia; proyectos propios (`gfx_lab_ch02`, `gfx_lab_ch02_solo`) y base con cola congelada de 4.5 s (C1–C11, C43, C58).
2. Todo cambio del lab pasa por `mutate()` (deshacer, autoguardado) y por el candado literal; la única excepción es la pregunta (manual o `generated`) (C14, C19, C55).
3. Ninguna forma que no se vea: lo que el templater no dibuja no aparece en la pantalla tramo por tramo (C12, C47).
4. Guardar identidad valida el perfil con `load_profile` antes de reemplazarlo y deja respaldo; la identidad vive en la clave `identity` del perfil (C22–C30).
5. Unidad = tramo; Probar = un objeto solo sobre la foto fija; "con todo" = solo lo aprobado (no marcado no aparece) (C42–C48).
6. Movimiento sobre el PNG con "movimiento seguro" (`push/pan/pull/static`); 3D = clip DepthFlow; salida por tramo vía `transitions` (C44–C45).
7. Ícono siempre en bloque L + palabra + fuente en la banda oscura del lado tranquilo; 12 íconos probables en cualquier palabra en el lab (C50–C53).
8. Pregunta generada por Flash con validador del contrato; pausa real (base congelado + `apad` de fase2b + música por cap) solo con `--gfx`; md5 sin gfx intacto (C54–C57).
9. Pico determinista (`gfx_peak`): un bloque grande y ±5 s libres; nivel de agua, reloj, zoom con latido y corte a negro por tokens del perfil (`peak_blocks`, `black_hold_sec`) (C60–C66).
10. Riesgos conocidos: HyperFrames no escala `<video>` (zoom arreglado con cuadro congelado, golpe pendiente), dos pestañas del lab se pisaban (candado 409), heurísticas sin etiquetador (sustantivos, movimiento por prompt) (C36, C54, C64, C67).

## Historia: F2b (HANDOFF_F2b_director_v2.md) — cerrado, en rama f2-gfx-director
- §1 `aec3a4a`, §2 `046c4c9`, PARADA 1 `2879665`, §3 `f3fd3db`, §4 `6819ee5`, pre-merge `11a9d1f`, v2 + re-ensamble `31c671c`. Revisores: CUMPLE CON OBSERVACIONES. Docs en `lab/hyperframes/f2b/` (`F2b_REPORT.md`, `DECISIONES_F2b.md`).
- Esperando a Omar desde F2b: mirar `AB_…_f2b.mp4`, decidir el criterio de PSNR de §4 (B33), merge F1+F2+F2b a `main` solo con OK explícito. Deuda: recortes repetidos entre caps.

## Reglas que no se negocian
- Responder en español (rioplatense). Comentarios en español, identificadores en inglés.
- Todo reporte a Omar pasa antes por `revisor-handoff` (subagente, sonnet) y su veredicto va **íntegro**.
- Candado literal en todo texto en pantalla. Sin `--gfx`, fase2b byte-idéntico (chequeo: md5 de ch02 `--only-cap` = `38e5ba14…`).
- Sin shaders, sin rembg/inpaint. Validar con `--only-cap ch02` + snapshots; renders completos solo cuando se piden.
- Commits F3: `feat(gfx-f3-lab): <sección>` / `fix(gfx-f3-lab): …`, trailer `Co-Authored-By: Claude Opus 5.5 <noreply@anthropic.com>`, `git add` por ruta (`diag_234_cap4.py` NO es nuestro; los `plan_ch02_lab*.json` tampoco se commitean).
- Python con `PYTHONIOENCODING=utf-8`. Los heredocs largos de bash fallan (y rompen con acentos): escribir los scripts con Write en el scratchpad.
- `--reuse-visuals` reusa `chXX_gfx.mp4`: moverlo a `_fase2b_work/_bak_*` antes de re-renderizar un cap.
- El lab y otra pestaña pueden pisarse: recargar la página después de cambiar el estado por fuera (el servidor responde 409 a guardados viejos).

## Dónde está todo (general)
- Handoffs: `lab/hyperframes/_handoff_adjuntos/` (F2, nocturno, DOC_MAESTRO) y `lab/hyperframes/f3/` (F3, F3b).
- Código gfx: `gfx_config.py` (motor), `gfx_profiles/*.json` (perfil), `script_engine/gfx_*.py`, `script_engine/gfx_templates/`, `script_engine/sfx/` (`make_sfx.py`, incluye `drone_subida.wav`).
- Salidas: `output/ba6c3cac…/` → `_final.mp4` (A, sin gfx), `_final_gfx.mp4` (B-F2), AB; respaldos en `_fase2b_work/_bak_*`.
- Transcripciones respaldadas antes de cada compactación: `lab/_transcripts/` (hook PreCompact).

## Comandos de uso diario
- Tests: `PYTHONIOENCODING=utf-8 python -m pytest test_module_gfx_*.py test_module_fase2b_reassemble.py test_module_fase2b_hwencode.py test_module_concat_windowed.py test_module_transition_timeout.py -q` (243 verdes con el perfil del commit).
- Lab: `PYTHONIOENCODING=utf-8 python gfx_lab_server.py` → http://localhost:8765 (`?tramo=N` abre en un tramo; `?modo=experto` = vista vieja).
- Un cap: `python fase2b.py <id> --reuse-visuals --gfx --gfx-quality looks --only-cap ch02` (+ `--gfx-debug` para el overlay).
- Video completo: `python fase2b.py <id> --reuse-visuals --keep-segments --gfx --gfx-sparse`.
