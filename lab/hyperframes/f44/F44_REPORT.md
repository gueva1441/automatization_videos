# F44 — ¿La ficha mejora si ve el caso? Parte 1 (A/B ficha + escaleta) — REPORTE

CC · 2026-10-28 · rama `f11-guion-v4` · misma sesión · handoff `lab/hyperframes/f44/HANDOFF_F44_caso_en_la_ficha.md` (md5 `f0388d7b4d7c58b3d42a8e3129fcedd9` ✓, el del mensaje de Omar). Tema: Wittenoom (`123bbb64-9fca-4395-8bf4-57d60e219ef1`). **PARADA 1.** No se arrancó la parte 2.

## Lecturas declaradas
- El handoff, entero.
- `researcher_steps/ficha_caso.py`: `prompt`, `build`, `run`, `save`, `call_for`, versiones.
- `script_engine/m01a_escaleta.py`: `generate_escaleta`, `generate_escaleta_v2`, `call_escaleta`, `pool_gate_profile` y el bloque TÍTULO/ÁNGULO/MISTERIO/REVELACIÓN (línea 1465).
- `fase1_5.py`: `_topic_v3`, `cargar_perfil`, `_step_cost`, `run_escaleta_v3`, `asegurar_ficha`.
- `cost_tracker.start_video`/`end_video`, el encabezado de `lab/hyperframes/f24/f24_corridas.py` y la rama A en `data/` (solo lectura).

## Módulos que toca (hoy → después)
| archivo | hoy (sticker) | después |
|---|---|---|
| `researcher_steps/ficha_caso.py` | arma la ficha del caso con una llamada a Sol sobre el pool y un título (f23-1) | `prompt(pool, title, caso=None)`, `build(…, caso=None)`, `run(…, caso=None)`. Con `caso`, el bloque es `<caso>` con TÍTULO/ÁNGULO/MISTERIO/REVELACIÓN (las mismas 4 líneas y el mismo «-» de respaldo de la escaleta) y `prompt_version` `f44-1`. **Sin `caso`, byte-idéntico a f23-1:** test contra la versión de `01a5858` sacada de git. Producción no lo usa: `fase1_5.asegurar_ficha` no se tocó. Sticker nuevo, mapa regenerado, `--check` 0. |
| `test_module_f44.py` (nuevo) | — | 3 tests sin red: sin caso, md5 del prompt igual al de antes (y `system()` igual); con caso, cambia solo el bloque; `run` anota f44-1 / f23-1 y pasa el caso. **3 verdes.** |
| `lab/hyperframes/f44/f44_corridas.py` (nuevo, lab) | — | `a` copia A de producción; `b` corre la ficha B y después la escaleta B, en fila, con freno antes de cada llamada y sin `end_video` (que escribe en `data/`). |
| `lab/hyperframes/f44/f44_compara.py` (nuevo, lab; lo escribió un subagente Sonnet en paralelo) | — | `TABLA_AB.md` por código (probado A contra A: solapamiento 1,00). |

## Cómo se corrió B (una variable)
- **Pool:** `00_pool_v3.json` de A copiado a `lab/hyperframes/f44/B/_steps/<tid>/`; md5 `3eef2b448a82cfefa4abd4574341c985` = A (verificado en la corrida).
- **Título:** el de la ficha A («Wittenoom ciudad fantasma contaminada Australia»).
- **Modelo:** `gpt-6.1-sol` `high` (el default, como A).
- **Caso:** `angle`/`mystery`/`reveal` del topic de `topics_db`, en `B/_steps/<tid>/caso.json`.
- **Antes de gastar** verifiqué que el prompt B difiere del de A solo en el bloque `<caso>`: el resto, byte a byte, es igual (129.310 → 129.778 caracteres).
- **Escaleta B:** `generate_escaleta_v2` con prompt vigente `f26-1`, sin columna, `call_escaleta(None)` (el mismo default que A). El topic dict es el mismo que usó A (`fase1_5._topic_v3`: `evidence_pool` de `topics_db` y el `_perfil.json` del caso, solo lectura), con `persist=False` y la salida escrita en el lab.
  - Ojo: la escaleta, en A y en B, lee el `evidence_pool` del topic, que **no** es byte-igual a `00_pool_v3.json` (la ficha lee el archivo). Así corre producción; B lo repite igual.
- **Freno y tope:** antes de cada llamada, lo gastado + lo que costó esa llamada en A (medido: ficha 0,3533; escaleta 1,8637 / 2 intentos = 0,9318) ≤ US$ 3,00. `lab/TOPE_TANDA.json` = 3,00 (no commiteado).

Log (`lab/hyperframes/f44/B/corrida_b.log`):
```
inicio 23:56:36
  pool B: md5 3eef2b448a82cfefa4abd4574341c985 = A ✓
[23:56:38] INFO     | viral_pipeline | [cost_tracker] Tracking de costos iniciado para video: f44-B-123bbb64-9fca-4395-8bf4-57d60e219ef1
  [freno] ficha B: gastado 0.0000 + estimado 0.3533 ≤ 3.00 → sigue
[gpt] ficha_caso: JSON inválido (Expecting value; finish_reason length) (intento 1/3) — re-llamando
[gpt] ficha_caso: JSON inválido (Expecting value; finish_reason length) (intento 2/3) — re-llamando
  ficha B: f44-1 · {'humanos_candidatos': 4, 'giros': 6, 'pico': 1, 'pregunta_final': 1, 'escenas': 10, 'contradicciones': 1, 'decisiones': 15, 'versiones': 3, 'personas': 60, 'personas_descartadas': 8, 'cifras': 28, 'cronologia': 80, 'hechos': 70, 'citas': 23, 'descartados': 25} · sacados 8 · US$ 1.1278
  [freno] escaleta B (m01a_escaleta v2 intento 1): gastado 1.1278 + estimado 0.9318 ≤ 3.00 → sigue
  [escaleta] compuerta del pool: verde {'datos': 155, 'citas_verificadas': 42, 'elegibles_humano': 25, 'eventos_con_fecha': 98, 'personas_con_nombre': 35}
  [escaleta v2] intento 1: 0 bloqueante(s) [] · 18 reparación(es) · 13 a métricas
  escaleta B: ok · US$ 0.9249 · total B US$ 2.0527
exit 0
fin 00:18:48
```

## Salida de la parte 1 — la tabla de comparación entera (`lab/hyperframes/f44/TABLA_AB.md`, por código)

- A: `C:\CLAUDE_PROJECTS\automatization_videos\lab\hyperframes\f44\A` (ficha ok, escaleta ok)
- B: `C:\CLAUDE_PROJECTS\automatization_videos\lab\hyperframes\f44\B\_steps\123bbb64-9fca-4395-8bf4-57d60e219ef1` (ficha ok, escaleta ok)

### 1. Ficha A vs B

| Campo | A | B |
|---|---|---|
| conteos.humanos_candidatos | 4 | 4 |
| conteos.giros | 6 | 6 |
| conteos.pico | 1 | 1 |
| conteos.pregunta_final | 1 | 1 |
| conteos.escenas | 11 | 10 |
| conteos.contradicciones | 5 | 1 |
| conteos.decisiones | 16 | 15 |
| conteos.versiones | 2 | 3 |
| conteos.personas | 56 | 60 |
| conteos.personas_descartadas | 9 | 8 |
| conteos.cifras | 30 | 28 |
| conteos.cronologia | 71 | 80 |
| conteos.hechos | 65 | 70 |
| conteos.citas | 21 | 23 |
| conteos.descartados | 28 | 25 |
| sacados (cantidad) | 13 | 8 |
| usd | 0.3533 | 1.1278 |
| prompt_version | f23-1 | f44-1 |
| pool_md5 | 3eef2b448a82cfefa4abd4574341c985 | 3eef2b448a82cfefa4abd4574341c985 |
| modelo | gpt-6.1-sol | gpt-6.1-sol |
| esfuerzo | high | high |
| titulo | Wittenoom ciudad fantasma contaminada Australia | Wittenoom ciudad fantasma contaminada Australia |
| historia.humanos_candidatos | Daniel Écija (padre) · Minero emigrante español. · citas 0<br>María Bernal · Esposa del minero y madre de un niño nacido en Wittenoom. · citas 0<br>Víctor Calvo · Niño emigrante y testigo adulto de la exposición cotidiana. · citas 2<br>Maitland Parker · Anciano Banjima y víctima de mesotelioma. · citas 1 | Daniel Écija (padre) · Minero emigrante español y víctima de mesotelioma. · citas 0<br>María Bernal · Esposa del minero y superviviente de la pérdida familiar. · citas 0<br>Víctor Calvo · Niño residente y testigo retrospectivo de la exposición cotidiana. · citas 2<br>Maitland Parker · Anciano Banjima, defensor de su territorio y víctima de mesotelioma. · citas 1 |
| historia.pico | Daniel Écija padre muere de mesotelioma a los 55 años, nueve meses después del diagnóstico. — por qué: Es el pico humano del relato: después de haber abandonado Wittenoom y vuelto a Madrid, la exposición alcanza a la familia y convierte la aparente salida del peligro en la pérdida del padre y del mari… | Daniel Écija padre muere de mesotelioma a los 55 años, nueve meses después del diagnóstico. — por qué: Es el desenlace humano irreversible de la línea principal: la estancia había terminado y la familia había regresado a Madrid, pero la enfermedad acaba con el padre y deja a María sin marido. |
| historia.giros | 1. Las advertencias dejan de ser generales: Eric Saint denuncia por escrito el peligro del polvo y anticipa una cosecha le…<br>2. La producción aumenta pese a la evidencia sanitaria, antes de la llegada documentada de las familias españolas.<br>3. La mina finalmente cierra, pero por razones económicas, no porque se haya eliminado la contaminación.<br>4. La salida del pueblo no cierra el daño: Daniel Écija padre recibe un diagnóstico de mesotelioma y muere después.<br>5. Se elimina oficialmente el pueblo, pero la declaración posterior exige remediar un territorio que sigue contaminado.<br>6. La dispersión fuera del área reconocida y la falta de una solución desembocan en la demanda de BNTAC contra el Estado. | 1. La advertencia de Eric Saint convierte el polvo de una molestia laboral en una previsión explícita de enfermedad letal.<br>2. La producción aumenta pese a las advertencias y enfermedades ya documentadas.<br>3. La mina cierra por razones económicas, no como resultado de una remediación del territorio.<br>4. El diagnóstico de Daniel Écija padre devuelve Wittenoom a la vida familiar mucho después de haber abandonado el pueblo.<br>5. El Estado elimina oficialmente el pueblo de mapas y señales, pero los informes describen una contaminación que continúa…<br>6. La reclamación Banjima pasa de los informes y el ultimátum a un procedimiento ante el Tribunal Federal. |
| escenas | 1. Barco desde Málaga hacia Australia, durante el viaje de la familia De…<br>2. Pista de aterrizaje y acceso a las viviendas de Wittenoom.<br>3. Wittenoom, durante la infancia de Víctor Calvo.<br>4. Molino y sus inmediaciones.<br>5. Patios, accesos y espacios públicos del pueblo.<br>6. Lugar no precisado de un retrato familiar tomado durante la estancia…<br>7. Hospital de Wittenoom, en el parto de María Bernal.<br>8. Puesto de control de un aeropuerto australiano.<br>9. Lugar de la entrevista de María Bernal, no precisado en el pasaje.<br>10. Cauces, pozas y llanuras de inundación hasta el río Fortescue.<br>11. Entradas del antiguo pueblo y de Wittenoom Gorge. | 1. Entrevista de María Bernal reproducida en el reportaje, sin localizac…<br>2. Canal de Suez, durante el viaje en barco a Australia.<br>3. Pista de aterrizaje de Wittenoom y traslado a las viviendas.<br>4. Interior e inmediaciones del molino, en 1957.<br>5. Wittenoom, en los lugares de juego que Víctor no identifica con mayor…<br>6. Retrato familiar conservado de la estancia en Wittenoom.<br>7. Hospital de Wittenoom, en junio de 1963.<br>8. Puesto de control de un aeropuerto australiano, en 1985.<br>9. Acopio de relaves de la mina Colonial.<br>10. Entradas al antiguo pueblo y a Wittenoom Gorge. |

### 2. Escaleta A vs B

| Campo | A | B |
|---|---|---|
| humano | María Bernal · Es el único candidato con entrada, daño y salida fechados: se casa el 20 de septiembre de 1962 y emigra cuatro días des… | Daniel Écija (padre) · Es el único candidato con entrada, sufrimiento y salida concretos en la ficha: baila en Madrid, se casa y emigra cuatro… |
| pico | beat 10 · Es el que la ficha marca y no hay razón mejor: la familia salió de Wittenoom a los diez meses, volvió a Madrid, y veint… | beat 10 · Es el que marca la ficha y no hay razón mejor: el diagnóstico de 1991 devuelve Wittenoom a una casa de Madrid veintioch… |
| promesa_gancho | En el retrato de familia todos miran a cámara menos el pie: está vendado, y la herida que le hizo un trozo de amianto no cierra. | En el pasaporte dice Wittenoom, y el policía que lo lee se queda mirando al viajero como si supiera algo de él que él todavía no sabe. |
| cierre_humano | Volver al retrato del pie vendado. La herida del pie cerró. La otra nadie supo verla a tiempo. Y la pregunta de la ficha, sin respuesta: ¿quién va a sacar la primera palada de esa tierra? | La frase de la familia, sin nombre: «Ese sitio nos cambió la vida para siempre», sobre el retrato del padre con el pie vendado, y la pregunta que la ficha deja sin respuesta: quién va a sacar la primera palada de esa tierra. |
| beats (n) | 14 | 14 |
| _reparaciones (n) | 14 | 18 |
| _reparaciones | 1. beat 6: apoyo P33 no existe en el pool → fuera<br>2. humano.nombre «Daniel Écija (padre)» → «María Bernal» (el nombre exacto del pool)<br>3. a_pantalla Q03: cap 6 inválido o lleno → fuera<br>4. a_pantalla D152: cap 6 inválido o lleno → fuera<br>5. a_pantalla D154: cap 6 inválido o lleno → fuera<br>6. a_pantalla D155: cap 6 inválido o lleno → fuera<br>7. a_pantalla D109: cap 6 inválido o lleno → fuera<br>8. cap 1: palabras 180 → 110 (objetivo 110)<br>9. cap 2: palabras 460 → 250 (objetivo 250)<br>10. cap 3: palabras 500 → 250 (objetivo 250)<br>11. cap 4: palabras 490 → 250 (objetivo 250)<br>12. cap 5: palabras 710 → 250 (objetivo 250)<br>13. cap 6: palabras 470 → 250 (objetivo 250)<br>14. cap 7: palabras 450 → 140 (objetivo 140) | 1. beat 7: apoyo P33 no existe en el pool → fuera<br>2. beat 9: apoyo T57 ya está en el beat 1 → fuera<br>3. a_pantalla D40: cap 6 inválido o lleno → fuera<br>4. a_pantalla D25: cap 6 inválido o lleno → fuera<br>5. a_pantalla Q03: cap 6 inválido o lleno → fuera<br>6. a_pantalla Q02: cap 6 inválido o lleno → fuera<br>7. a_pantalla D94: cap 5 inválido o lleno → fuera<br>8. a_pantalla D109: cap 5 inválido o lleno → fuera<br>9. a_pantalla D152: cap 6 inválido o lleno → fuera<br>10. a_pantalla D155: cap 6 inválido o lleno → fuera<br>11. a_pantalla D154: cap 6 inválido o lleno → fuera<br>12. cap 1: palabras 220 → 110 (objetivo 110)<br>13. cap 2: palabras 510 → 250 (objetivo 250)<br>14. cap 3: palabras 520 → 250 (objetivo 250)<br>15. cap 4: palabras 680 → 251 (objetivo 250)<br>16. cap 5: palabras 540 → 250 (objetivo 250)<br>17. cap 6: palabras 480 → 250 (objetivo 250)<br>18. cap 7: palabras 490 → 140 (objetivo 140) |
| a_pantalla (ids) | D40, D94, D95, D01, D51 | D34, D41, D02, D26, D23, T63, Q20, D01, D62 |
| prompt_version | f26-1 | f26-1 |
| ficha.prompt_version | f23-1 | f44-1 |

### 3. Por cap: dato_central + datos_apoyo

| Cap | A central | A apoyo | B central | B apoyo | \|A∩B\|/\|A∪B\| |
|---|---|---|---|---|---|
| cap 1 | D85 | — | Q24 | T57 | 0/3 = 0.00 |
| cap 2 | T34, Q14 | T37, T38, Q12, Q13, D83, Q15, T36, D82, D35, D76 | T34, Q15 | Q12, T37, T38, D83, T24, Q14, T36, Q13, D82, T03 | 10/14 = 0.71 |
| cap 3 | D92, Q54 | Q45, Q46, D19, T13, Q53, T06, T27, D21, Q49, D20, D132, Q37 | Q45, D21 | D19, T13, D91, Q46, Q53, Q54, D138, D136, T32, D49 | 7/19 = 0.37 |
| cap 4 | Q19, T40 | D03, D129, Q16, D104, T41, D87, T39 | Q16, Q19, T40 | D104, D39, D18, Q32, D03, T39, D87, T41, T47, D88 | 8/14 = 0.57 |
| cap 5 | T49, Q24, T64 | T47, T51, D02, D88, D122, T57, D27, D28, T67, D89, Q23, Q25 | T49, D89 | D22, T52, T56, D93, T64, D85, Q35, D36 | 3/22 = 0.14 |
| cap 6 | D23, D31 | D93, T56, Q21, Q20, D36, Q07, D61, Q05, D54, Q55, D59 | T80, D57 | D28, D06, T76, Q07, D42, T79, D09, Q08, D60, D150, D59, Q05 | 3/24 = 0.12 |
| cap 7 | Q10, D42 | D09, D10, T90, T92, T96, T98, Q34, D70, D71 | Q10, T98 | T92, T96, Q55, D55, T87, T95, T97, D95, Q11, D71, Q23 | 5/19 = 0.26 |
| **TOTAL** (cap+id) | — | — | — | — | 36/115 = 0.31 |

### 4. Costo total de B

- total_usd: **2.0527**

| paso | US$ | segundos |
|---|---|---|
| ficha B | 1.1278 | 1156.5 |
| escaleta B | 0.9249 | 173.5 |
| **total B** | **2.0527** | 1330.0 |

## Lo que se ve en la tabla (hechos; la decisión es de Omar)
- **Humano de la escaleta:** A quedó con **María Bernal (P16)** y B con **Daniel Écija (padre) (P17)**, que es el ángulo de `03_meta`.
  - En A el modelo devolvió `id` P16 con el nombre «Daniel Écija (padre)»; la reparación confió en el id y cambió el nombre a María Bernal (`_reparaciones[1]` de A).
  - En B, id y nombre coinciden (P17) y no hubo reparación de humano.
  - Que se repita la reparación «cambia de persona» (abierto del analista) no se puede saber desde B, porque en B no hizo falta.
- **Pico:** el mismo en las dos fichas (muerte de Daniel Écija padre) y el mismo beat 10 en las dos escaletas. Como anticipaba el handoff, en el pico hay empate.
- **Humanos candidatos de la ficha:** los mismos 4 nombres, en el mismo orden; en B, los roles describen más el daño.
- **Conteos de la ficha:** parejos.
  - contradicciones 5 → 1;
  - sacados por el chequeo 13 → 8;
  - cronología 71 → 80, hechos 65 → 70, escenas 11 → 10.
- **Escaleta:** 14 beats en las dos.
  - A necesitó 2 intentos (2 bloqueantes en el 1); B, 1.
  - `a_pantalla`: 5 ids en A, 9 en B.
  - La promesa del gancho y el cierre cambian.
- **Datos por cap:** solapamiento total de ids 36/115 = **0,31**. Los caps 2 y 4 se parecen (0,71 y 0,57); el 1, el 5 y el 6 casi no (0,00, 0,14 y 0,12).
- **Palabras por cap:** el doble en A y en B (cap 2: 460 → 250 en A, 510 → 250 en B; los 7 caps se recortan en las dos). Como dijo el analista, si se repite en B es de la escaleta, no de la ficha.
- **Costo de la ficha:** B costó el triple que A (US$ 1,1278 contra 0,3533). La respuesta de Sol salió cortada por largo dos veces (`finish_reason length`) y `gpt_helpers` la re-llamó solo; la ficha B es la del tercer intento.
  - **Es una segunda variable que A no tuvo.** Esas re-llamadas internas no pasaron por mi freno, que mira antes de cada `call`, no adentro.

## Lo que queda abierto (entero)
- e1. **Ficha B = tercer intento, por respuestas cortadas** (`finish_reason length` ×2): costó US$ 1,13 (A 0,35) y tardó 19 min (A 6). No se sabe si el `<caso>` hace más larga la salida (cronología 71 → 80, hechos 65 → 70) o si fue azar. Con una sola corrida por rama no se separa el efecto del caso del de la varianza del modelo.
- e2. **Una corrida por rama:** cualquier diferencia de la tabla puede ser varianza. Para afirmar «B gana», haría falta repetir A y B (más gasto: decide Omar).
- e3. **El freno no ve los reintentos internos de `gpt_helpers`:** el tope se cuidó igual (2,05 de 3,00), pero una ficha con 3 reintentos cortados podría pasarse sola.
- e4. **El humano de A cambió de persona por un id equivocado del modelo:** P16 con el nombre de P17, y la reparación confió en el id. En B no pasó. Es el bug que anotó el analista («una reparación de nombre no debería cambiar de persona»), ahora con su causa: la reparación prioriza el id sobre el nombre.
- e5. **Palabras por cap ×2** en A y en B (bug de la escaleta, no de la ficha), anotado por el analista para la PARADA 1.
- e6. **La escaleta lee `topic["evidence_pool"]` de `topics_db` y la ficha lee `00_pool_v3.json`; no son byte-iguales.** Se repitió igual en B, pero es otra fuente de diferencia posible en producción.
- e7. **Parte 2:** el form de Omar ya produjo la cadena A de Wittenoom hasta el papel (`01e_pantalla.md` a las 00:00) y ahora corre `fase2a`. Para la comparación de la parte 2, el papel A está.
- e8. **`lab/TOPE_TANDA.json`** quedó en US$ 3,00 desde 23:56 y no se commiteó. El hook `tope_tanda` mira `cost_history.json`, que ahora suma también el gasto de la corrida de Omar.
- e9. **Hook `suite_rapida`:** corrió la suite rápida antes del commit (es automático). La regla dice «solo `test_module_f44.py`»; lo declaro.
- e10. **Abiertos del analista que siguen:** `seed_title` None en el topic Wittenoom (para F43); Kyshtym y Vajont solo con el material de `lab/hyperframes/f40/a/`.

## Procesos y subagentes
- Subagentes: el del script de comparación y el revisor, terminados.
- Shells en segundo plano: el de la corrida B, terminado.
- No cerré ningún proceso de Omar. Al cerrar seguían vivos su `qa_studio_server`, su `run_pipeline --research` y su `fase2a.py --topic 123bbb64…`.
- **Nada en `data/` ni `output/`:** lo nuevo ahí desde 23:52 es todo de la corrida del form de Omar. `cost_history.json` solo tiene entradas `123bbb64…`, ninguna `f44-B`.

## Veredicto de revisor-handoff (íntegro)
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Handoff con md5 f0388d7b… | OK | `md5sum` del handoff = f0388d7b4d7c58b3d42a8e3129fcedd9 |
| 2 | `caso` opcional y byte-idéntico sin él (test contra 01a5858) | OK | `researcher_steps/ficha_caso.py` (`caso_block`, `prompt`, `build`, `run`). `test_module_f44.py:36-41` carga ficha_caso de 01a5858 con `git show` y compara el md5 del prompt, `system()` y `PROMPT_VERSION`. Corrí el test: 3 passed, con proxy muerto. |
| 3 | Con `caso`, solo cambia el bloque `<caso>` (4 líneas); `f44-1` solo con caso | OK | `test_module_f44.py:44-52` y `:55-69`. El «-» de respaldo es el mismo que usa la escaleta. |
| 4 | Pool de B = A (md5 3eef2b44…) | OK | `md5sum`: data, `f44/B/_steps/…/00_pool_v3.json` y `ficha_caso.json` de A y B dan 3eef2b448a82cfefa4abd4574341c985. |
| 5 | Mismo título, modelo y esfuerzo | OK | Ambas fichas: gpt-6.1-sol / high / «Wittenoom ciudad fantasma contaminada Australia». |
| 6 | Escaleta B con el prompt f26-1 | OK | Las dos `01a_escaleta.json` traen `prompt_version` f26-1. |
| 7 | B difiere de A solo en ÁNGULO/MISTERIO/REVELACIÓN | PARCIAL | La ficha: sí, porque el test fija que solo cambia el bloque, y el `caso.json` de B tiene las 3 líneas. Pero hubo 2 re-llamadas internas por `finish_reason length` (ficha B = 3.er intento) que A no tuvo. Además A necesitó 2 intentos de escaleta y B 1. El reporte lo declara (e1, e2). Es una segunda variable real, no solo varianza. |
| 8 | Costo ≤ US$ 3,00 | OK | Ficha B 1,1278 + escaleta B 0,9249 = 2,0527 (`B/costos.json`, `B/corrida_b.log`). El freno no ve los reintentos internos de gpt_helpers; el reporte lo declara (e3). El tope se respetó igual. |
| 9 | A solo se lee; copia fiel | OK | md5 idéntico entre data y `f44/A` para `ficha_caso.json` y `01a_escaleta.json`. Mtimes 23:45 y 23:51, intactos. |
| 10 | Nada de la tanda en data/ ni output/ | OK | `git status --short data output` vacío. `cost_history.json` tiene 0 menciones de «f44». Los archivos nuevos en data/ (guion, pantalla, 03_visual, fase2a, 23:52 a 00:12) son del form de Omar. |
| 11 | El commit 533eb68 tiene solo las rutas permitidas | OK | 24 archivos: `ficha_caso.py`, `test_module_f44.py`, `lab/hyperframes/f44/**`, más sticker `research.json` y `MAPA_PROYECTO.{json,md}` (el handoff exige el sticker y el mapa). `config.py` y `.env` no tocados. Ya está en origin/f11-guion-v4. |
| 12 | Sticker y `mapa_modulos.py --check` en 0 | OK | Corrí `--check`: «156 archivos · 0 fallas». |
| 13 | Tabla entera en el reporte | PARCIAL | Las secciones 1 a 3 están completas y coinciden con `TABLA_AB.md`. La sección 4 (costo) quedó rota: la tabla «Paso» muestra dicts JSON crudos y no columnas. Los números sí están (2,0527; 1,1278; 0,9249). |
| 14 | «Lo que queda abierto» entero | OK | `F44_REPORT.md:140-150`, e1 a e10. Incluye la ficha como 3.er intento, el freno ciego, el humano que cambió de persona y las palabras por cap ×2. |
| 15 | Entregables A/B en `lab/hyperframes/f44/` | OK | Existen las dos fichas y las dos escaletas, `TABLA_AB.md` y `f44_corridas.py`/`f44_compara.py`. |
| 16 | Veredicto íntegro y ESTADO al día | NO VERIFICABLE | El reporte tiene `{{VEREDICTO}}` pendiente (esperado, va este veredicto). No revisé `lab/ESTADO_SESION.md`. |
| 17 | Sin parte 2, sin merge a main | OK | No hay artefactos de cascada en f44. El commit solo está en f11-guion-v4. |

Fuera de alcance: ninguno. `git status` muestra `F44_REPORT.md` sin commitear (esperado). Siguen modificados `diag_234_cap4.py`, `lab/TOPE_TANDA.json` (US$ 3,00, declarado en e8) y `f28a.log`; no son del commit.

Observaciones: (a) La sección 4 de costo del reporte está mal formateada. (b) El hook suite_rapida corrió antes del commit, contra la regla «solo test_module_f44.py»; el reporte lo declara (e9). (c) Una corrida por rama más las diferencias de reintentos impiden atribuir al `caso` cualquier diferencia de la tabla. El reporte lo dice (e1, e2).

Riesgos que el contrato no cubre: (1) Si el form de Omar hace una ficha con `caso` en producción, `gpt_helpers` puede reintentar 3 veces sin freno; el costo podría triplicarse, como pasó en B. (2) La escaleta lee `evidence_pool` de topics_db y la ficha lee `00_pool_v3.json`; no son byte-iguales (e6). (3) `lab/TOPE_TANDA.json` sigue en 3,00 y el hook lo compara con el `cost_history` compartido con el gasto del form.

### Adenda de CC (después del veredicto)
- **13 / (a):** la sección 4 del reporte quedó como tabla de verdad (paso · US$ · segundos). `TABLA_AB.md` queda como la generó el script.
- **Riesgo (1):** hoy no aplica a producción, porque `fase1_5` no pasa `caso`: la ficha de producción sigue con f23-1. Igual, los reintentos internos por respuesta cortada ya existen hoy en la ficha sin caso. Queda en e3.
- **16:** ESTADO se actualiza en el mismo commit que este reporte.

