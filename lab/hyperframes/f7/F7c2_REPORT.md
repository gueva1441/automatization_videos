# F7c-2 — Orleans con el §8 (largo) y las reglas nuevas del guion

Rama `f7-research-v3` · topic `ba6c3cac-f7r3` · pedido: validación del analista sobre F7c («material de 9, narración 7.5–8»), §8 del handoff confirmado por Omar, reglas 1–5 y re-corrida.

**Leer:** [compara_orleans_v3r.html](compara_orleans_v3r.html) (4 columnas: v2 · F6c · F7c · F7c-2) · [NARRACION_orleans_v3r2.md](NARRACION_orleans_v3r2.md) · [ESCALETA_orleans_v3r2.md](ESCALETA_orleans_v3r2.md).

## 1. Qué cambió

**§8 — largo** (`script_engine/video_length.py`, que lee `config.long_video` con estos mismos valores por defecto; `config.py` está fuera de git porque tiene las claves, así que los campos están en el config local y el código no depende de que existan):
- `target_words` 1500 · `max_words` 1700 (dura en la revisión del guion) · gancho 110 · desarrollo 240 × 5 · cierre 130 (`m01a_escaleta.CAP_WORDS`, suma 1,440).
- `dev_cap_seconds` 105 (antes 75) en `m01a_skeleton.CHAPTER_SCHEMA`; gancho y cierre, 45. Contrato de 7 caps intacto.
- `max_images_per_video` 90: en `m03_visual` solo el tope de `_calculate_image_count` = lo que dejan los caps veo, repartido entre los de desarrollo → **16 fotos por cap como máximo** (5 × 16 + 2 × 5 = 90). Un cap de 75 s sigue dando lo mismo.

**Reglas nuevas** (`script_engine/guion_v3_reglas.py`, las suma `m01b_guionista.review` → valen para el guionista y para el editor; también en el prompt del guionista, reglas 6 y 12–15):
1. **Citas por fragmento:** cada cita del pool trae `fragmento` (≤ 25 palabras, literal: la primera oración que entra; una cita corta es su propio fragmento). Entre comillas va solo el fragmento, con atribución; el resto se parafrasea. **El candado lo acepta:** `evidence.anchors` de una cita = `[fragmento, texto]` (cambio aditivo de 2 líneas en `evidence.py`; sin fragmento, igual que antes). Dura: más de una cita literal por párrafo.
2. **Gancho:** dura si el cap 1 describe una foto, da una fecha o adelanta una cita que la escaleta pone en un cap siguiente. El flash-forward del cap 4/5 va en las notas de la escaleta (punto 5).
3. **Juicios:** dura una interpretación del narrador cuya idea no está en ningún ítem del pool (lista de 14 patrones: «deliberado», «no eran considerados humanos», «colapso de la humanidad», «castigo», «como animales», «no les importaba», «caos deliberado»…). Si el pool lo dice (un documento habla de «castigo»), vale.
4. **Nombre completo** del humano más de una vez en un cap → dura. **Repetición entre caps:** una frase de 3 palabras (≥ 2 de contenido, sin nombres propios ni cifras) ya dicha en un cap anterior → dura.
5. **Notas del analista** (`NOTAS_F7C2` en el runner, van a la escaleta como `escaleta_notas`): pico = francotiradores en el cap 5 (Q14, Q47); cadáveres flotando como dato en el cap 4 o 5 (D228/D297/D391); 6,375 (D51) una vez; Gusman antagonista en el cap 2 con Q08 y **T39** —el «T05» de la nota es del pool viejo: en este pool T05 es el arresto de Shawn Duncan en 2001; T39 es la reunión del sheriff del 28 de agosto; la nota se le pasó así a la escaleta, que **no usó T39** (ver §5)—; cierre con Reyes (Q60) y Reed.

Tests: `test_module_f7.py` (34) · suites de guion, gfx, m01 y m03: **447 verdes**. Fallan 5 que ya fallaban antes: 3 de `test_module_01b_pauses` y 2 de `test_module_m03_merge_timing` (`_reconcile_anchor_timing`, idéntica a HEAD). Ajusté `test_module_f6b.py` (su escaleta de prueba asumía 190 palabras por cap).

## 2. La corrida

Escaleta al 5.º intento (los 4 primeros: humano en < 3 caps, pregunta con término administrativo, humano tarde). Humano: **Renard Reed**. Pico: **beat 7, cap 5, Q14** (los francotiradores). Gancho: **Q184**, Burton bebiendo agua del inodoro (flash-forward). Guionista: intento 2 (11 duras). Editor: 13 de 24 cambios aceptados. **Costo: US$ 0.86** (escaleta 0.49, guionista 0.16, editor 0.20).

| métrica | v2 F5d | F6c | F7c | **F7c-2** |
|---|---|---|---|---|
| palabras | 1,165 | 1,070 | 940 | **1,252** |
| densidad (ids / 100 pal.) | 1.97 | 2.15 | 1.81 | 1.44 |
| datos distintos | 21 | 23 | 17 | 18 |
| adjetivos / 100 | 2.58 | 2.43 | 1.81 | 1.52 |
| trigramas repetidos | 0.087 | 0.007 | 0.020 | 0.016 |
| cliffhangers | 6/6 | 6/6 | 6/6 | 6/6 |
| citas usadas | 2 | 4 | 9 | **12** |
| testigos con nombre citados | — | 2 | 5 | **7** (Richard, Reyes, Reed, Burton, Ducre, Big Whappy, Gusman) |
| duras de su corrida | — | 4 | 16 | **11** |
| duras con las reglas de F7c-2 (re-medido) | — | 6 | 25 | **11** |

(La densidad de F7c pasa de 1.70 a 1.81 respecto de F7c_REPORT: se mide con el pool de hoy, donde decir el fragmento ya cuenta como usar la cita.)

## 3. Lo que queda (honesto)

**Duras (11):** 6 son del candado literal (datos declarados que no suenan literales: D545, D540, D183, Q183…); 1 dato reservado para pantalla dicho (D180); 1 párrafo con 2 citas (Gusman y su vocera, cap 6); 3 repeticiones entre caps («alguien vendría a ayudarlos», «del primer piso», «sus últimas rondas»).

**A la lectura, cosas que ningún validador ve:**
- **Roles cambiados:** «La reclusa Rhonda Ducre» — en el pool es *alguacil en el edificio HOD*; «Un guardia lo describió: “Hombre, ese lugar olía a muerte”» — es de Big Whappy, *preso*. Son invenciones. Propuesta: validador «el rol con el que se presenta a quien habla = su rol en el pool».
- **Juicios que pasan la lista:** «La prisión se había convertido en una zona de guerra», «el caos que él mismo había creado», «Fue una decisión» (última frase), «La evacuación era otro tipo de infierno» («infierno» y «caos» están en el pool, por eso no saltan). La lista de patrones no alcanza; un juez semántico (Flash: «¿esta frase afirma algo que no dicen los datos?») sería la vía.
- **Foto fuera del gancho:** el cap 6 abre con «Las imágenes dieron la vuelta al mundo en 2005…». La regla de fotos solo mira el cap 1.
- El gancho cita a Burton (es el dato del beat 1, permitido) y el cap 2 la orden de Gusman sin decir que es suya («La orden fue clara: «…»»): la cita sin atribución dentro de la oración pasa porque la atribución está en la frase anterior.

## 4. Archivos

Código: `script_engine/video_length.py` (nuevo), `script_engine/guion_v3_reglas.py` (nuevo), `m01a_escaleta.py` (CAP_WORDS), `m01a_skeleton.py` (duraciones), `m03_visual.py` (tope), `evidence.py` (anchors de cita), `m01b_guionista.py` (línea de cita, reglas del prompt, revisión, tope de 1,700), `researcher_steps/research_v3.py` (fragmento). `config.py` local: campos nuevos en `LongVideoConfig` (no se commitea). Runner: `lab/hyperframes/f7/f7c_orleans.py --f7c2`; comparación: `build_compara_v3r.py`. Salidas: `compara_orleans_v3r.html`, `f7c_metricas_compara.json`, `escaleta_orleans_v3r2.json`, `ESCALETA_orleans_v3r2.md`, `NARRACION_orleans_v3r2.md`, `f7c2_costos.json`, `f7c2_run.out`; F7c guardada en `f7c_v1/`.

## 5. Notas del analista: qué entró y qué no (corregido después del revisor)

| nota | resultado |
|---|---|
| pico = francotiradores, cap 5 | ✔ Q14 (beat 7, cap 5), Q47 de apoyo |
| gancho flash-forward sensorial | ✔ Q184 (agua del inodoro) y Q181, intensidad 4. Pero la última frase del cap 1 adelanta, parafraseada, la orden de Q08 («mantener a los prisioneros donde… pertenecen») que suena en el cap 2; la dura solo mira 4 palabras literales seguidas |
| cadáveres flotando en cap 4/5 | ✔ D228 en el cap 4 («Un preso vio 2 cadáveres flotando…») |
| 6,375 una vez | ✖ **suena 0 veces**: la escaleta mandó D51 (6,375) a pantalla del cap 2 («la voz no lo dice») |
| Gusman antagonista en cap 2 con T05/Q08 | ✖ **a medias**: el cap 2 usa Q08 y T55 (la evacuación obligatoria de Nagin); **T39 no entró** en la escaleta (en §1.5 lo nombré como si se hubiera usado). Q08 está `verificada_parcial`, así que va sin nombre: el cap 2 nunca nombra a Gusman («La orden fue clara: «…»»). Aparece recién en los caps 6 y 7 |
| cierre con Reyes + Reed | ✔ Q60, Q50 |

**Largo:** 1,252 palabras contra el objetivo de 1,500 (83 %). Los caps 2–6 pasan el mínimo (85 % de 240), el 1 tiene 96 (objetivo 110) y el 7, 118 (objetivo 130). Además, la suma de `CAP_WORDS` del §8 (110 + 240 × 5 + 130) es 1,440, no 1,500.

Fuera de los entregables nombrados: `00_pool_v3.json` se regeneró (con `fragmento` en cada cita) y `f7b_run.out` es el log de ese re-armado.

## 6. Veredicto del revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES (el código cumple; la corrida incumple la nota del sheriff/T39 y la del 6,375 sin decirlo en el reporte)

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | §8: target 1500, max 1700, dev_cap 105 s, max_images 90 | OK | script_engine/video_length.py:11-19 (mismos defaults que el config local); m01a_skeleton.py CHAPTER_SCHEMA y m01a_escaleta._cap_words leen de ahí; el tope de 1,700 es dura en m01b_guionista.review |
| 2 | m03 solo cambia el tope de _calculate_image_count | OK | git diff m03_visual.py: un solo hunk (+7/-1) en esa función; 16 fotos por cap como máximo |
| 3 | Regla 1: fragmento ≤25 palabras literal, el candado lo acepta, máx. 1 cita por párrafo | OK | evidence.py:98 (anchors = fragmento y texto); research_v3.add_fragments; guion_v3_reglas.quotes_per_paragraph. Las 187 citas del pool tienen fragmento ≤25 palabras y contenido en el texto |
| 4 | Regla 2: gancho flash-forward, sin fotos ni fechas, sin citas siguientes | PARCIAL | hook_problems existe y el prompt tiene la regla 12. El gancho (Q184, agua del inodoro) es sensorial, pero parafrasea la orden de Q08 («mantener a los prisioneros donde… pertenecen»), cuya cita suena en el cap 2. La dura solo mira 4 palabras seguidas literales, así que no lo atrapa |
| 5 | Regla 3: sin juicios fuera del pool | PARCIAL | judgment_problems tiene 14 patrones. El reporte admite que pasan «zona de guerra», «el caos que él mismo había creado», «Fue una decisión» |
| 6 | Regla 4: nombre completo 1 vez por cap; repetición ≥3 palabras → dura | OK | full_name_problems y repetition_problems. La corrida las dispara: 3 repeticiones quedan en la lista de duras |
| 7 | Nota 5a: pico = francotiradores en cap 5 | OK | 01a_escaleta.json: pico Q14 en el beat 7 (cap 5), con Q47 de apoyo. El cap 5 lo narra |
| 8 | Nota 5b: gancho flash-forward sensorial | OK | Cap 1 con Q184 (agua del inodoro, Burton) y Q181, intensidad 4 |
| 9 | Nota 5c: cadáveres D228/D297/D391 en cap 4 o 5 | OK | Beat de cap 4 con D228 (+D58). La narración dice «Un preso vio 2 cadáveres flotando…» |
| 10 | Nota 5d: 6,375 una sola vez | PARCIAL | 6,375 aparece 0 veces en la narración. D51 (6375) fue a pantalla del cap 2 («la voz no lo dice»). Hay una cifra canónica 5.919 que prohíbe «6.375» en la voz. La nota pedía una vez y el reporte no dice que quedó en 0 |
| 11 | Nota 5e: Gusman antagonista en cap 2 con T05/Q08 | FALLA parcial | Cap 2 usa Q08 más T55 (Nagin, evacuación obligatoria). T39 no aparece en 01a_escaleta.json. El §1.5 del reporte nombra T39 como si se hubiera usado y no avisa que no entró. Q08 es «verificada_parcial» (va sin nombre), así que el cap 2 nunca nombra a Gusman: «La orden fue clara: «…»» |
| 12 | Verificación T05 vs T39 en el pool | OK | 00_pool_v3.json: T05 = arresto de Shawn Duncan en 2001 (F01). T39 = reunión del sheriff Gusman el 28-ago-2005. El reporte acierta en que T05 es otro evento |
| 13 | Cierre con Reyes (Q60) y Reed | OK | Cap 7 con Q60, Q50 y D546 en la escaleta. Reed es el humano |
| 14 | Tests pedidos | OK | Corrí el comando: 447 passed en 22 s. No verifiqué las «5 fallas previas» porque quedan fuera de esa lista |
| 15 | Cifras del reporte vs archivos | OK | La tabla coincide con f7c_metricas_compara.json (1,252 palabras, 1.44, 18 datos, 12 citas, 7 testigos, 11 duras). Costos 0.4933 + 0.1613 + 0.2018 = 0.856 (US$ 0.86), coincide con f7c2_costos.json. Las 11 duras de 01b_narracion_v3.json se reparten como dice el reporte: 6 de candado, 1 de D180, 1 de dos citas en un párrafo, 3 repeticiones |
| 16 | Roles cambiados de Ducre y Big Whappy | OK | La narración dice «La reclusa Rhonda Ducre» y el pool dice «Alguacil en el edificio HOD». Dice «Un guardia lo describió» sobre Q181 y el pool dice «Preso» (Big Whappy) |

Fuera de alcance: `lab/hyperframes/f7/f7b_run.out` (reescrito, sin aviso en el reporte) y `lab/hyperframes/f7/00_pool_v3.json` (565 líneas, regenerado con fragmentos; es consecuencia esperada de add_fragments, pero no está en la lista de entregables). `lab/ESTADO_SESION.md` es la actualización exigida por el CLAUDE.md. Quedan sin commitear `diag_234_cap4.py` y `gfx_profiles/*.json`, ya modificados antes de esta etapa. No se tocó nada más.

Observaciones:
- Largo: 1,252 palabras contra el objetivo de 1,500 (83%). El cap 1 tiene 96 palabras (objetivo 110) y el cap 7 tiene 118 (objetivo 130). La suma de CAP_WORDS es 1,440, no 1,500. El reporte muestra la cifra pero no la presenta como desvío del §8.
- La salida final no queda limpia: 11 duras, entre ellas una violación directa de la regla 1 (dos citas literales en el párrafo 22, cap 6) y 3 repeticiones de la regla 4. El reporte lo declara.
- El reporte lista como «foto fuera del gancho» el cap 6 que abre con «Las imágenes dieron la vuelta al mundo». La regla de fotos solo mira el cap 1.

Riesgos que el contrato no cubre: la cita sin atribución (el sheriff nunca nombrado) y los roles inventados no tienen validador. Los juicios dependen de una lista de patrones. Todo esto solo se detecta leyendo.
