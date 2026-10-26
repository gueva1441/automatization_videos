# F32 — El guion de pantalla: todo lo que se verá, en texto, antes de renderizar · REPORTE

CC · 2026-10-26 · rama `f11-guion-v4`, base `0253672` (F31). Handoff `HANDOFF_F32_guion_de_pantalla.md`. Pedido de Omar: A → B → C, **un commit por parte** (el handoff pedía uno por arreglo en B; mandó Omar). **Ningún render en esta tanda.**
Commits: **A `308032a`** · **B `2fde994`** · **C** = el commit de este reporte.
Costos de la tanda: **Claude US$ 0.2668** de 1 (el rotulista: el prompt cambió una línea, así que no hubo caché) · **Gemini US$ 0.0016** de 0.5 (crítico sobre la foto y visión: 0.0011 en la corrida de B, verificable en `b/plan_only_B.log` como 0.2679 − 0.2668; 0.0005 en la primera corrida de A, cuyo log se pisó con la corrida siguiente) · ElevenLabs 0.

**En una línea:** `fase2b --plan-only` escribe el guion de pantalla de Vajont (`GUION_PANTALLA.md/.json`: 200 eventos, 82 de ellos propuestas cortadas) y la mezcla de previsualización en **2 min 42 s** (5 min 2 s la primera vez, con el rotulista llamando a Claude), sin navegador ni render. Los 8 arreglos de B están en el código; en Vajont quedan **2 textos en pantalla** (D128, D245), `a_pantalla` 2/5, 10 sellos, preguntas de cierre con lectura 7/7 e inicio de voz con rampa 6/7. Un hallazgo cambia el diagnóstico de B.1: **la voz de v5 no perdía el ataque**.

## Decisiones de Omar aplicadas como «voto del analista» (§0)
1. **2 `a_pantalla` en el mismo beat si van en escenas distintas**: aplicado (`gfx_rotulista.finalizar`, `A_PANTALLA_POR_BEAT = 2`; la segunda ficha espera otra escena del beat en `escena_final`).
2. **Texto en el beat pico: solo `a_pantalla`**: aplicado (lo demás, 0).
3. **Pre-roll del title card de 3 s; ch01 sin pre-roll; la música del cap arranca con el title card**: aplicadas las tres.

## A — El guion de pantalla (`308032a`)
| archivo | qué |
|---|---|
| `script_engine/gfx_guion.py` (nuevo) | eventos (§A.1) en el tiempo del mp4: intro 2.5 s + offset del cap (los segmentos, redondeados a cuadro como el `-t` del render) + tiempo del plan (con el pre-roll). Tipos: title card, ficha, persona, recorte, cita, lupa, sello, reloj, nivel de agua, contador, punch, pregunta de cierre, transición (tipo, razón, escena saliente → entrante), costura (negro → corte → sube desde negro → title card → voz, con los segundos), silencio de voz. Cada línea: `mm:ss · chNN · beat (función) · tipo · «etiqueta \| texto» · dura (lectura mínima) · escena (de a) · voz −1 / ancla / +1 · aporta · fuente · filtro`. Lo propuesto y cortado sale con `✂` y «cortó *quién*: *por qué*» (rotulista por regla, zona, catálogo de sellos, realizador, crítico, candado). Resumen por beat (§A.2) con `⚠ BEAT VACÍO` y `⚠ CAP SIN TEXTO`. 8 chequeos (§A.3). Salida `.md` y `.json` (la misma información) |
| `fase2b.py` | `--plan-only` (implica `--gfx --reuse-visuals`; los visuales base tienen que estar cocidos): prefetch de director y rotulista como siempre → re-codificación -g30 de los 7 caps **en paralelo** (7 hilos) → plan de cada cap **en fila** (cada cap lee lo que ya mostraron los anteriores) → mezcla → guion. `--plan-edit archivo.json`: suma las ediciones a `_fase2b_work/plan_edits.json` y regenera el guion (el rotulista sale de caché). `_mezcla_preview` (§A.4): voz + sfx por cap con el mismo grafo del segmento, unidos sin solapar (como el corte a negro), y la música por el mismo camino del render; el grafo de la mezcla con música quedó en un solo lugar (`_grafo_musica`, el render usa el mismo texto) |
| `script_engine/gfx_layer.py` | `apply_gfx(plan_only=True)`: sin `hyperframes doctor`, sin re-codificar el base para la pausa (la duración se suma), sin proponer léxico (`record_proposals`, como las simulaciones de F5), `reencoded=True` para no re-codificar dos veces; escribe `gfx_escenas_chNN.json` (escenas y duración del cap) en los dos caminos; aplica las ediciones a mano |
| `script_engine/gfx_rotulista.py` | ediciones (§A.5): `texto`, `etiqueta`, `word_idx`, `sentence_idx`, `tipo`, `aporta`, `borrar`, `agregar` (sobre una copia de la respuesta: la caché no se toca; el bloque editado pasa por todas las reglas) y `escena` (arranca en el corte de la escena k) |
| `script_engine/gfx_vision.py` | la caché compartida de visión con candado (re-lee y suma bajo el candado) |

**Tests sin red (§A.6)**, `test_module_f32.py`: guion de un cap de fixture con todos los tipos · beat vacío marcado · cap sin texto marcado · silencio contra la pausa más larga del guion · inicio de voz **sin rampa con el audio de v5 ch01** (fixture `lab/hyperframes/f32/fixtures/v5_mezcla_0a10s.wav`: `✗ … medida 5.62 s · llega a −18 dB en 5.66 s sin rampa (100 ms previos: −34.7 dB …)`) · **con rampa con el de v3b** · corrido 0.2 s falla por tiempo · `--plan-edit` cambia una etiqueta y el guion lo refleja (más borrar, agregar y escena). Suite amplia **983 + 5 previas**, rápida 58, md5 `--only-cap ch02` sin `--gfx` (`--sw-encode`) **`38e5ba14…`** (`a/`).

Línea de base (Vajont en el estado de v5, con el código de A): `a/GUION_PANTALLA_A.md/.json`, 159 s, US$ 0.

### Ejemplo: el cap ch06 entero, tal como sale en `GUION_PANTALLA.md`
(Las transiciones `cut` también son líneas; los `✂` son propuestas cortadas.)

## ch06 — El gran rugido (11:24.7–14:18.9)

Segmento 174.20 s · pre-roll 3.0 s · primera palabra a 3.14 s del cap · pausa más larga del guion 1.86 s (marca de pausa del guion, en «resplandor.») · textos en pantalla 1

- 11:24.7 · ch06 · beat 10 (pico) · costura · «negro 1.0 s (black hold de ch05) → corte → sube desde negro en 10 cuadros (0.33 s) sobre el title card → title card 3.0 s sin voz (pre-roll 3.0 s) → voz a 3.14 s del cap» · escena 0 (0.0 a 18.5 s)
- 11:24.7 · ch06 · beat 10 (pico) · title card · «CAPÍTULO 6 | El gran rugido» · dura 3.0 s · escena 0 (0.0 a 18.5 s) · filtro: pasó
- ✂ 11:33.1 · ch06 · beat 10 (pico) · punch_in · «acercamiento del director» · escena 0 (0.0 a 18.5 s) · voz −1: — · voz ancla: Carlo Onorini, el párroco de Casso, lo contó así: «escucho el ruido de la avalancha, abro la ventana y este ruido aumentaba en forma extraordinaria, al mismo tiempo vi un resplandor». · voz +1: Son las diez y treinta y nueve. · filtro: cortó realizador: punch_in del director: lo reemplaza el zoom_punch del pico (F30b)
- ✂ 11:33.7 · ch06 · beat 10 (pico) · sello · «avalancha» · escena 0 (0.0 a 18.5 s) · voz −1: — · voz ancla: Carlo Onorini, el párroco de Casso, lo contó así: «escucho el ruido de la avalancha, abro la ventana y este ruido aumentaba en forma extraordinaria, al mismo tiempo vi un resplandor». · voz +1: Son las diez y treinta y nueve. · filtro: cortó catálogo: sello de agua: una animación por beat: el beat 10 ya tiene el sello del pico «fisura»
- 11:43.1 · ch06 · beat 10 (pico) · transición · «cut» · escena 1 (18.5 a 22.8 s) · razón: corte · escena 0 → 1
- 11:47.5 · ch06 · beat 10 (pico) · punch · «zoom_punch 12 cuadros» · escena 2 (22.8 a 29.1 s) · razón: pico · escena 1 → 2
- 11:50.1 · ch06 · beat 10 (pico) · sello · «fisura» · dura 2.5 s · escena 2 (22.8 a 29.1 s) · voz −1: El Toc entra al lago. · voz ancla: La ladera entera, la que caminaba, la de la fisura, se desploma de una vez dentro del embalse. · voz +1: El agua no tiene a dónde ir, salvo hacia arriba. · filtro: pasó (crítico: suma)
- 11:53.8 · ch06 · beat 10 (pico) · transición · «cut» · escena 3 (29.1 a 40.2 s) · razón: corte · escena 2 → 3
- 12:04.8 · ch06 · beat 10 (pico) · transición · «cut» · escena 4 (40.2 a 49.1 s) · razón: corte · escena 3 → 4
- ✂ 12:06.4 · ch06 · beat 10 (pico) · sello · «ruido» · escena 4 (40.2 a 49.1 s) · voz −1: Se levanta, pasa por encima de la presa, por encima de la pared que no se rompe, y cae en la garganta hacia el Piave. · voz ancla: Benito Castellano oye un ruido «como de un trueno de verano multiplicado cien veces, muy lóbrego, que duró tres o cuatro minutos». · voz +1: Después, un estruendo con un resplandor, y enseguida un ruido como el que hace una formación de reactores al pasar. · filtro: cortó catálogo: sello de caos: una animación por beat: el beat 10 ya tiene el sello del pico «fisura»
- 12:13.7 · ch06 · beat 10 (pico) · transición · «cut» · escena 5 (49.1 a 58.0 s) · razón: corte · escena 4 → 5
- ✂ 12:17.6 · ch06 · beat 10 (pico) · sello · «ruido» · escena 5 (49.1 a 58.0 s) · voz −1: Benito Castellano oye un ruido «como de un trueno de verano multiplicado cien veces, muy lóbrego, que duró tres o cuatro minutos». · voz ancla: Después, un estruendo con un resplandor, y enseguida un ruido como el que hace una formación de reactores al pasar. · voz +1: En el bar Faè, Germano Accamillesi mira televisión cuando «se interrumpió la iluminación del televisor y casi al mismo tiempo (treinta-cincuenta segundos) se empezaron a sentir fuertes sacudidas telúricas». · filtro: cortó catálogo: sello de caos: una animación por beat: el beat 10 ya tiene el sello del pico «fisura»
- 12:22.7 · ch06 · beat 10 (pico) · transición · «cut» · escena 6 (58.0 a 70.7 s) · razón: corte · escena 5 → 6
- ✂ 12:33.0 · ch06 · beat 10 (pico) · sello · «sacudidas» · escena 6 (58.0 a 70.7 s) · voz −1: Después, un estruendo con un resplandor, y enseguida un ruido como el que hace una formación de reactores al pasar. · voz ancla: En el bar Faè, Germano Accamillesi mira televisión cuando «se interrumpió la iluminación del televisor y casi al mismo tiempo (treinta-cincuenta segundos) se empezaron a sentir fuertes sacudidas telúricas». · voz +1: Después de las sacudidas se apaga también la luz del bar. · filtro: cortó catálogo: sello de caos: una animación por beat: el beat 10 ya tiene el sello del pico «fisura»
- ✂ 12:33.0 · ch06 · beat 10 (pico) · punch_in · «acercamiento del director» · escena 6 (58.0 a 70.7 s) · voz −1: Después, un estruendo con un resplandor, y enseguida un ruido como el que hace una formación de reactores al pasar. · voz ancla: En el bar Faè, Germano Accamillesi mira televisión cuando «se interrumpió la iluminación del televisor y casi al mismo tiempo (treinta-cincuenta segundos) se empezaron a sentir fuertes sacudidas telúricas». · voz +1: Después de las sacudidas se apaga también la luz del bar. · filtro: cortó realizador: punch_in del director: lo reemplaza el zoom_punch del pico (F30b)
- 12:35.4 · ch06 · beat 10 (pico) · transición · «cut» · escena 7 (70.7 a 78.8 s) · razón: corte · escena 6 → 7
- ✂ 12:36.0 · ch06 · beat 10 (pico) · sello · «sacudidas» · escena 7 (70.7 a 78.8 s) · voz −1: En el bar Faè, Germano Accamillesi mira televisión cuando «se interrumpió la iluminación del televisor y casi al mismo tiempo (treinta-cincuenta segundos) se empezaron a sentir fuertes sacudidas telúricas». · voz ancla: Después de las sacudidas se apaga también la luz del bar. · voz +1: Nadie en ese bar sabe todavía qué viene bajando por la garganta. · filtro: cortó catálogo: sello de caos: una animación por beat: el beat 10 ya tiene el sello del pico «fisura»
- ✂ 12:36.0 · ch06 · beat 10 (pico) · punch_in · «acercamiento del director» · escena 7 (70.7 a 78.8 s) · voz −1: En el bar Faè, Germano Accamillesi mira televisión cuando «se interrumpió la iluminación del televisor y casi al mismo tiempo (treinta-cincuenta segundos) se empezaron a sentir fuertes sacudidas telúricas». · voz ancla: Después de las sacudidas se apaga también la luz del bar. · voz +1: Nadie en ese bar sabe todavía qué viene bajando por la garganta. · filtro: cortó realizador: punch_in del director: lo reemplaza el zoom_punch del pico (F30b)
- 12:43.4 · ch06 · beat 10 (pico) · transición · «cut» · escena 8 (78.8 a 84.2 s) · razón: corte · escena 7 → 8
- ✂ 12:43.6 · ch06 · beat 10 (pico) · sello · «ola» · escena 8 (78.8 a 84.2 s) · voz −1: Nadie en ese bar sabe todavía qué viene bajando por la garganta. · voz ancla: La ola baja hacia el Piave. · voz +1: Longarone sigue con las luces encendidas. · filtro: cortó catálogo: sello de agua: una animación por beat: el beat 10 ya tiene el sello del pico «fisura»
- 12:48.9 · ch06 · beat 10 (pico) · transición · «cut» · escena 9 (84.2 a 94.9 s) · razón: corte · escena 8 → 9
- 12:59.6 · ch06 · beat 10 (pico) · transición · «cut» · escena 10 (94.9 a 108.0 s) · razón: corte · escena 9 → 10
- ✂ 13:02.5 · ch06 · beat 10 (pico) · sello · «fuerza» · escena 10 (94.9 a 108.0 s) · voz −1: Nadie avisó. · voz ancla: Micaela siente que la cama toma velocidad y que una fuerza la agarra por la espalda. · voz +1: La ola la arrastra al menos cuatrocientos metros desde su casa. · filtro: cortó catálogo: sello de caos: una animación por beat: el beat 10 ya tiene el sello del pico «fisura»
- ✂ 13:05.1 · ch06 · beat 10 (pico) · sello · «ola» · escena 10 (94.9 a 108.0 s) · voz −1: Micaela siente que la cama toma velocidad y que una fuerza la agarra por la espalda. · voz ancla: La ola la arrastra al menos cuatrocientos metros desde su casa. · voz +1: Ahí la encuentran. · filtro: cortó catálogo: sello de agua: una animación por beat: el beat 10 ya tiene el sello del pico «fisura»
- 13:12.6 · ch06 · beat 10 (pico) · transición · «cut» · escena 11 (108.0 a 113.2 s) · razón: corte · escena 10 → 11
- 13:17.8 · ch06 · beat 11 (respiro) · transición · «dissolve 20 cuadros» · escena 12 (113.2 a 126.9 s) · razón: cambio de beat · escena 11 → 12
- 13:19.0 · ch06 · beat 11 (respiro) · sello · «fango» · dura 2.5 s · escena 12 (113.2 a 126.9 s) · voz −1: Longarone ya no. · voz ancla: Donde había calles hay fango y piedras. · voz +1: Un hombre está parado en el medio y no sabe hacia dónde mirar. · filtro: pasó (crítico: suma)
- ✂ 13:31.5 · ch06 · beat 11 (respiro) · ficha · «Técnicos muertos en el centro de control del estribo izquierdo | 20 técnicos perecieron en el centro de control del estribo izquierdo de la presa.» · lectura mínima 9.5 s · escena 12 (113.2 a 126.9 s) · voz −1: «Conocía Longarone en cada rincón, ahora no sé dónde estoy», dijo uno de los sobrevivientes. · voz ancla: Entre los muertos está Guglielmo Celso, el alcalde socialista de Longarone. · voz +1: Nadie creó un organismo central que informara oficialmente cómo avanzaba el rescate. · fuente: D192 · A Tragedy in the Italian Alps (50th Anniversary) Vajont Dam, 2013 · filtro: cortó rotulista (lectura): sin tiempo de lectura: 143 caracteres piden 9.5 s y hay 9.5 s
- 13:31.5 · ch06 · beat 11 (respiro) · transición · «cut» · escena 13 (126.9 a 137.6 s) · razón: corte · escena 12 → 13
- 13:32.0 · ch06 · beat 11 (respiro) · ficha · «Muertos en el desastre del Vajont (recuento oficial) | 1.910 personas murieron en el desastre.» · dura 9.5 s (lectura mínima 6.1 s) · escena 13 (126.9 a 137.6 s) · voz −1: «Conocía Longarone en cada rincón, ahora no sé dónde estoy», dijo uno de los sobrevivientes. · voz ancla: Entre los muertos está Guglielmo Celso, el alcalde socialista de Longarone. · voz +1: Nadie creó un organismo central que informara oficialmente cómo avanzaba el rescate. · aporta: Da el recuento oficial total de víctimas, que la narración no menciona. · fuente: D128 · Il disastro del Vajont non fu una calamità naturale, 2023 · filtro: pasó (crítico: (1) sí · (2) sí · (3) no estorba)
- ✂ 13:32.0 · ch06 · beat 11 (respiro) · sello · «muertos» · escena 13 (126.9 a 137.6 s) · voz −1: «Conocía Longarone en cada rincón, ahora no sé dónde estoy», dijo uno de los sobrevivientes. · voz ancla: Entre los muertos está Guglielmo Celso, el alcalde socialista de Longarone. · voz +1: Nadie creó un organismo central que informara oficialmente cómo avanzaba el rescate. · filtro: cortó catálogo: sello de muerte: una animación por beat: el beat 11 ya tiene el sello «fango»
- ✂ 13:32.0 · ch06 · beat 11 (respiro) · punch_in · «acercamiento del director» · escena 13 (126.9 a 137.6 s) · voz −1: «Conocía Longarone en cada rincón, ahora no sé dónde estoy», dijo uno de los sobrevivientes. · voz ancla: Entre los muertos está Guglielmo Celso, el alcalde socialista de Longarone. · voz +1: Nadie creó un organismo central que informara oficialmente cómo avanzaba el rescate. · filtro: cortó realizador: punch_in del director: lo reemplaza el zoom_punch del pico (F30b)
- 13:42.2 · ch06 · beat 11 (respiro) · transición · «cut» · escena 14 (137.6 a 152.6 s) · razón: corte · escena 13 → 14
- ✂ 13:43.5 · ch06 · beat 11 (respiro) · sello · «ruido» · escena 14 (137.6 a 152.6 s) · voz −1: Nadie creó un organismo central que informara oficialmente cómo avanzaba el rescate. · voz ancla: Desde el aire llegó el ruido de los rotores. · voz +1: La fuerza estadounidense despachó seis helicópteros. · filtro: cortó catálogo: sello de caos: una animación por beat: el beat 11 ya tiene el sello «fango»
- ✂ 13:45.3 · ch06 · beat 11 (respiro) · sello · «fuerza» · escena 14 (137.6 a 152.6 s) · voz −1: Desde el aire llegó el ruido de los rotores. · voz ancla: La fuerza estadounidense despachó seis helicópteros. · voz +1: Un hombre de una aldea de la zona lo recuerda: «El primer rescatista que vi llegó en un helicóptero del ejército de Estados Unidos». · filtro: cortó catálogo: sello de caos: una animación por beat: el beat 11 ya tiene el sello «fango»
- 13:57.3 · ch06 · beat 11 (respiro) · transición · «dip 10 cuadros» · escena 15 (152.6 a 174.2 s) · razón: cierre · escena 14 → 15
- 14:12.5 · ch06 · beat 11 (respiro) · pregunta de cierre · «Tres días después llegó el presidente del Consejo. La gente ya sabía qué pedirle.» · dura 5.4 s (lectura mínima 5.4 s) · escena 15 (152.6 a 174.2 s) · voz −1: Tres días después llegó el presidente del Consejo. · voz ancla: La gente ya sabía qué pedirle. · voz +1: — · fuente: escaleta (cierre del último beat) · filtro: pasó
- 14:17.9 · ch06 · beat 11 (respiro) · costura · «negro 1.0 s al cierre del cap (black hold)» · dura 1.0 s · escena 15 (152.6 a 174.2 s)

| beat | función | ventana | escenas | propuestos (director · rotulista) | cortados por regla | quedan |
|---|---|---|---|---|---|---|
| 10 | pico | 3.1–112.2 s | 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 | 13 · 0 | **duplica** (3): punch_in «acercamiento del director»: punch_in del director: lo reemplaza el zoom_punch del pico (F30b); punch_in «acercamiento del director»: punch_in del director: lo reemplaza el zoom_punch del pico (F30b); punch_in «acercamiento del director»: punch_in del director: lo reemplaza el zoom_punch del pico (F30b)<br>**tema** (8): sello «avalancha»: sello de agua: una animación por beat: el beat 10 ya tiene el sello del pico «fisura»; sello «ruido»: sello de caos: una animación por beat: el beat 10 ya tiene el sello del pico «fisura»; sello «ruido»: sello de caos: una animación por beat: el beat 10 ya tiene el sello del pico «fisura»; sello «sacudidas»: sello de caos: una animación por beat: el beat 10 ya tiene el sello del pico «fisura»; sello «sacudidas»: sello de caos: una animación por beat: el beat 10 ya tiene el sello del pico «fisura»; sello «ola»: sello de agua: una animación por beat: el beat 10 ya tiene el sello del pico «fisura»; sello «fuerza»: sello de caos: una animación por beat: el beat 10 ya tiene el sello del pico «fisura»; sello «ola»: sello de agua: una animación por beat: el beat 10 ya tiene el sello del pico «fisura» | sello «fisura»; punch ×1 |
| 11 | respiro | 113.2–166.6 s | 11, 12, 13, 14, 15 | 5 · 2 | **duplica** (1): punch_in «acercamiento del director»: punch_in del director: lo reemplaza el zoom_punch del pico (F30b)<br>**lectura** (1): D192 «20 técnicos perecieron en el centro de c»: sin tiempo de lectura: 143 caracteres piden 9.5 s y hay 9.5 s<br>**tema** (3): sello «muertos»: sello de muerte: una animación por beat: el beat 11 ya tiene el sello «fango»; sello «ruido»: sello de caos: una animación por beat: el beat 11 ya tiene el sello «fango»; sello «fuerza»: sello de caos: una animación por beat: el beat 11 ya tiene el sello «fango» | sello «fango»; ficha «1.910 personas murieron en el desastre.»; pregunta de cierre «Tres días después llegó el presidente de» |


## B — Arreglos (`2fde994`), cada uno con su medida en el guion
| # | qué cambió | medida en el guion de Vajont (C) |
|---|---|---|
| B.1 | **Diagnóstico nuevo: la voz de v5 no pierde el ataque.** La voz de ch01 en la mezcla de v5 es el mp3 corrido 2.5 + 3.000 s exactos (correlación: 5.62 s = 2.5 + 3.0 + 0.12 de la primera palabra; los niveles del mp3 y de la mezcla coinciden ventana por ventana). La «rampa» de v3b (−28 → −23 → −16 desde 2.55 s) era **el golpe del title card** (`golpe_grave.wav`, sfx a 0.05 s, −18 dB) que en v3b caía encima del «Hay»; con el pre-roll el golpe queda al entrar el title card y la voz entra 3 s después, sola. El «5.55 esperado» del handoff es ese 0.05 + 5.5. Arreglo: **ch01 sin pre-roll** (`_pre_roll_de`: el primer cap no; vuelve a pegarse el golpe con la voz) y **la pieza de música del cap cubre su title card** (dura `pre_sec` más y la envolvente de intensidad se corre `pre_sec`; antes la pieza se corría con silencio adelante) | inicio de voz: **6/7 ✓** (base A: 5/7). ch01 ✗ → **✓** (100 ms previos −34.6 → −24.4 dB); ch04 ✗ → ✓ (−32.1 → −25.2 dB); **ch07 ✗** (−33.7 dB: la voz arranca seca y la música está baja, −35 dB de mediana en su title card). Tiempo medido = esperado en los 7 (correlación, ±1 cuadro). ch01 vuelve a durar lo de v3b (101.6 s) |
| B.2 | la pregunta de cierre dura caracteres ÷ 15 cps (`lectura_pregunta`); el negro que sigue, 1 s como siempre; `question_pause_sec` queda como interruptor | **7/7 ✓** (base: 0/7): 5.3–6.4 s y 12.9 s la de ch07 (193 caracteres). El video pasa de 1032.4 a 1055.8 s |
| B.3 | si no cabe antes del corte, el bloque arranca en el primer cuadro de la escena siguiente, anclado a la misma oración o la siguiente del mismo beat; solo si tampoco cabe, «sin tiempo de lectura» (`despues_del_corte`) | **no hubo caso en Vajont**: D117 ahora cae por candado (el modelo, en su reintento, escribió la etiqueta «Acta de aprobación, 1943» y 1943 no está en el texto de D117); Q50 se probó en la escena siguiente y tampoco entra (pide 11.9 s, hay 6.6 s hasta el corte de 37.43 s). Probado con test (pasa al corte; si la escena siguiente es corta, no va) |
| B.4 | `a_pantalla` cuyo `por_que` dice carta/acta/informe/documento → tipo `documento` (recorte; sin etiqueta del modelo, la de su fuente) | Q50 sale como recorte con kicker «Carta del municipio de Erto y Casso, 2023» (el modelo ya lo devolvió como documento), pero **cae por lectura** (179 caracteres, 11.9 s). La regla también alcanza a D117 («dato de **acta**, va como rótulo»): pasó de hecho a documento (no cambió su suerte: el candado lo saca igual) |
| B.5 | 2 `a_pantalla` por beat (escenas distintas: las pone `escena_final`); `a_pantalla` en el pico; ya no se mueve del pico al beat siguiente | D128 y D192 pasan los dos la regla de cantidad en el beat 11 de ch06; **D192 cae por lectura** (143 caracteres piden 9.53 s y la oración + la siguiente dan 9.47 s; no es un corte de escena). `a_pantalla` **2/5** (base 1/5): D128 y D245 |
| B.6 | sellos por **tema** de la oración: en cada oración, la palabra de mayor peso (≥ 2) de un mood del catálogo (la misma regla que la palabra del pico) es el sello de ese tema (tabla `TEMA_DE_MOOD`: muerte, agua, veneno, fuego, oscuridad, radiación, abandono, silencio, caos); filtro: una animación por beat (el sello del pico cuenta), nunca en la escena de un texto o del title card, nunca dos en una escena, sin cruzar el corte. `punch_in` del director fuera | sellos en pantalla **5 → 10** (uno en cada beat salvo ch03 beat 4 y ch04, donde la escena o el beat ya tienen otra cosa); 42 candidatos cortados por el catálogo (con su motivo en el guion); **28 `punch_in` fuera** («lo reemplaza el zoom_punch del pico»); los 6 `zoom_punch` del pico, intactos. Ojo: el catálogo trae palabras del léxico del perfil con su peso; en ch02 sale «vida» como sello de *muerte* («la vida siguió con el Piave delante»): «vida» es disparador de muerte con peso 3 en `gfx_profiles/misterio.json` |
| B.7 | el prompt del rotulista suma **una línea** bajo `cifra`: «  devolvé \`unidad\` (metros, personas, m³, liras u otra) y \`valor\` numérico» (md5 del prompt **`c9231e24afbc785d5870b33088ce076e`**; el de F29c, `7dafbb96…`, queda como `ROTULISTA_SYSTEM_F29C`, test contra su handoff). Cifra en metros de un nivel/cota → `water_level`; personas o dinero → `count_up` (si se lee en los 3.7 s del contador); lupa → `evidence_zoom` (ya estaba) | **el modelo no devolvió `unidad` ni `valor` en ninguna de las 8 cifras**: el formato de salida del USER («Devolvé: {"bloques": [{…}]}») no los nombra y no se puede tocar. Respaldo (lectura declarada): sin esos campos, la cifra y su unidad se leen del texto del bloque. Aun así, en Vajont **no sale ninguna animación**: D128 «1.910 personas murieron en el desastre.» pide 6.1 s de lectura (el contador dura 3.7) y D245 (liras) 4.9 s → quedan como ficha; ninguna cifra de cota/nivel fue propuesta |
| B.8 | la ficha un escalón más chica: el dato a `question_font_px` (96 px; el title card sigue en 133) y la etiqueta (`tc_kicker_px`, 45) sobre la placa de `.co-text.stamp` (`rgba(10,10,10,.35)`, aire 6 × 26 px); la raya debajo de la última línea del dato; el title card, byte a byte igual | se ve en la hoja de cuadros del render (no en esta tanda); test del HTML y del CSS |

Tests de B en `test_module_f32.py` (18 en total con A) y adaptados a las reglas nuevas: `test_module_f29c_rotulista.py` (prompt de F29c como histórico, D128 + D192 en el mismo beat, `a_pantalla` del pico, lectura con escena siguiente, clase de la ficha), `test_module_f30b.py` (la pieza de música cubre el pre-roll) y `test_module_gfx_question.py` (la pregunta dura su lectura). Suite amplia **992 + 5 previas** (01b_pauses ×3, m03_merge_timing ×2), rápida 58, md5 ch02 sin `--gfx` **`38e5ba14…`** (`b/`).

## C — Guion de Vajont (sin render)
`fase2b f8s3-vajont-f30 --plan-only --rotulista --rotulista-tope 1.3` (el tope es el del registro del rotulista, que ya traía los US$ 0.2336 de F29c).
- **Guion:** `lab/hyperframes/f32/GUION_PANTALLA.md` y `.json` (copias de `output/f8s3-vajont-f30/`). **Mezcla:** `lab/hyperframes/f32/mezcla_preview.wav` (1055.8 s, 186 MB, **fuera de git**; el original en `output/f8s3-vajont-f30/_fase2b_work/`).
- **Tiempo del `--plan-only`:** 302 s la primera vez (rotulista llamando a Claude, 7 caps en paralelo) · **162–166 s** con el rotulista en caché: -g30 de los 7 caps en paralelo 108 s, plan en fila 46 s, mezcla 10 s. Objetivo «minutos»: cumple.
- **Costos:** Claude US$ 0.2668 (21 llamadas nuevas con los reintentos, prompt nuevo; registro 0.5004 − 0.2336 de F29c) · Gemini US$ 0.0016 (0.0011 verificable en log).

### Tabla A.2 (resumen por beat)
| cap | beat | función | ventana (s del cap) | escenas | propuestos (director · rotulista) | cortados por regla (n) | quedan |
|---|---|---|---|---|---|---|---|
| ch01 | 1 | gancho | 0.1–94.5 | 0 | 8 · 0 | duplica 4; tema 3 | sello «fuerza»; pregunta de cierre «El dique no cedió esa noche. Lo que lleg» |
| ch02 | 2 | planteo | 3.1–68.2 | 0, 1, 2, 3, 4, 5, 6, 7 | 4 · 2 | candado 1; duplica 1; lectura 1; tema 2 | sello «vida» |
| ch02 | 3 | escalada | 68.9–132.7 | 7, 8, 9, 10, 11, 12 | 11 · 0 | duplica 3; tema 6 | sello «montaña»; pregunta de cierre «En marzo del cincuenta y nueve, en otro »; punch ×1 |
| ch03 | 4 | giro | 3.1–64.1 | 0, 1, 2, 3, 4, 5, 6 | 11 · 0 | crítico 1; duplica 4; tema 5 | punch ×1 |
| ch03 | 5 | escalada | 64.9–127.5 | 6, 7, 8, 9, 10, 11, 12 | 1 · 2 | candado 1; crítico 1 | sello «desmoronamiento»; pregunta de cierre «El cuatro de noviembre, durante las prue» |
| ch04 | 6 | giro | 3.1–54.4 | 0, 1, 2, 3, 4, 5 | 6 · 1 | duplica 2; forma 1; tema 3 | reloj «4 NOV · 1960» |
| ch04 | 7 | giro | 55.3–118.6 | 5, 6, 7, 8, 9, 10 | 5 · 1 | cantidad 1; crítico 1; duplica 2; tema 1 | pregunta de cierre «La presa cambió de dueño con el agua tod»; punch ×1 |
| ch05 | 8 | escalada | 3.1–92.7 | 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10 | 10 · 1 | duplica 3; lectura 1; tema 4; zona 1 | sello «estruendos»; punch ×1 |
| ch05 | 9 | giro | 93.7–168.7 | 10, 11, 12, 13, 14 | 4 · 1 | crítico 1; duplica 1; tema 2 | sello «deslizamiento»; pregunta de cierre «A las diez y media de la noche, el párro» |
| ch06 | 10 | pico | 3.1–112.2 | 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11 | 13 · 0 | duplica 3; tema 8 | sello «fisura»; punch ×1 |
| ch06 | 11 | respiro | 113.2–166.6 | 11, 12, 13, 14, 15 | 5 · 2 | duplica 1; lectura 1; tema 3 | sello «fango»; ficha «1.910 personas murieron en el desastre.»; pregunta de cierre «Tres días después llegó el presidente de» |
| ch07 | 12 | revelacion | 3.1–100.6 | 0, 1, 2, 3, 4, 5, 6, 7, 8 | 6 · 1 | duplica 2; spoiler 1; tema 1; zona 1 | sello «grito»; punch ×1 |
| ch07 | 13 | cierre | 101.6–180.6 | 8, 9, 10, 11, 12, 13, 14 | 5 · 1 | duplica 2; tema 2 | ficha «Montedison pagó 55.645.758.500 liras a L»; sello «ola»; pregunta de cierre «La sentencia dice inundación agravada po» |

«propuestos» = lo que quedó + lo que se cortó, por origen (director/realizador: sellos, reloj, `punch_in`; rotulista: textos); la pregunta de cierre es de la escaleta y no cuenta. Reglas: `tema` = el catálogo de sellos; `duplica` = `punch_in` del director; `lectura`, `candado`, `cantidad`, `spoiler`, `forma`, `zona`, `crítico` como en el rotulista. Ningún beat vacío (en la base A había 1); **5 caps sin texto** (ch01–ch05), como en la base.

### Chequeos A.3 (los del guion, pegados)
#### ✗ dos bloques en la misma escena
- ✗ ch01 escena 0: title card «Cama en la oscuridad» + sello «fuerza»
- ✗ ch07 escena 0: title card «Diarios y verdades» + sello «grito»

#### ✓ bloque que cruza un corte
- ✓ ningún texto, sello, nivel de agua ni lupa cruza un corte (el reloj de esquina no cuenta)

#### ✓ texto sin lectura
- ✓ 2 con su lectura a 15 cps

#### ✓ pregunta de cierre sin lectura
- ✓ 7 con su lectura a 15 cps

#### ✓ cifra que contradice la voz
- ✓ 2 textos sin contradicción

#### ✗ a_pantalla
- ✗ 2/5 en pantalla
- ✗ ch02 D117: cortó rotulista (candado): no están en el texto fuente de D117: ['1943']
- ✗ ch05 Q50: cortó rotulista (lectura): sin tiempo de lectura: 179 caracteres piden 11.9 s y hay 10.9 s hasta el corte de escena (30.8 s)
- ✗ ch06 D192: cortó rotulista (lectura): sin tiempo de lectura: 143 caracteres piden 9.5 s y hay 9.5 s

#### ✓ costuras con cuadro no negro
- ✓ ch01→ch02 (01:44.1): negro 100.60–101.60 s hasta el corte · voz callada (máx -120.0 dB) · el entrante sube desde negro (corte a negro, sin fadewhite)
- ✓ ch02→ch03 (04:04.7): negro 139.57–140.57 s hasta el corte · voz callada (máx -120.0 dB) · el entrante sube desde negro (corte a negro, sin fadewhite)
- ✓ ch03→ch04 (06:20.0): negro 134.27–135.27 s hasta el corte · voz callada (máx -120.0 dB) · el entrante sube desde negro (corte a negro, sin fadewhite)
- ✓ ch04→ch05 (08:29.0): negro 127.97–128.97 s hasta el corte · voz callada (máx -120.0 dB) · el entrante sube desde negro (corte a negro, sin fadewhite)
- ✓ ch05→ch06 (11:24.7): negro 174.67–175.67 s hasta el corte · voz callada (máx -120.0 dB) · el entrante sube desde negro (corte a negro, sin fadewhite)
- ✓ ch06→ch07 (14:18.9): negro 173.20–174.20 s hasta el corte · voz callada (máx -120.0 dB) · el entrante sube desde negro (corte a negro, sin fadewhite)

#### ✗ inicio de voz por cap
- ✓ ch01 · voz esperada 2.62 s · medida 2.62 s · llega a −18 dB en 2.65 s con rampa (100 ms previos: -24.4 dB)
- ✓ ch02 · voz esperada 107.18 s · medida 107.18 s · llega a −18 dB en 107.17 s con rampa (100 ms previos: -29.2 dB)
- ✓ ch03 · voz esperada 247.78 s · medida 247.78 s · llega a −18 dB en 247.78 s con rampa (100 ms previos: -25.8 dB)
- ✓ ch04 · voz esperada 383.06 s · medida 383.06 s · llega a −18 dB en 383.06 s con rampa (100 ms previos: -25.2 dB)
- ✓ ch05 · voz esperada 512.05 s · medida 512.05 s · llega a −18 dB en 512.08 s con rampa (100 ms previos: -23.0 dB)
- ✓ ch06 · voz esperada 687.81 s · medida 687.81 s · llega a −18 dB en 687.83 s con rampa (100 ms previos: -29.1 dB)
- ✗ ch07 · voz esperada 861.95 s · medida 861.95 s · llega a −18 dB en 861.94 s sin rampa (100 ms previos: -33.7 dB, bajo la voz presente -30.5 dB)

Base A (estado v5) → C: dos bloques en una escena ✗ → ✗ (los mismos 2: ch01 y ch07, title card + el sello del pico en la escena 0 del Veo; ch01 tiene una sola escena) · cruza un corte ✓ → ✓ · texto sin lectura ✓ → ✓ · **pregunta sin lectura ✗ 0/7 → ✓ 7/7** · contradice la voz ✓ → ✓ · **`a_pantalla` 1/5 → 2/5** · costuras ✓ → ✓ · **inicio de voz 5/7 → 6/7**.

## Lecturas de CC (declaradas)
1. **Inicio de voz medido** = el corrimiento de la voz dentro de la mezcla (correlación con su mp3, ±0.5 s) + la primera palabra; ✓ a ≤ 1 cuadro. **Rampa** = la energía de los 100 ms antes de que la mezcla llegue a −18 dB (RMS de 10 ms, paso de 1 ms; sin los últimos 10 ms, la ventana del salto) está sobre «voz presente», que es el `duck_threshold` del sync map (0.03 = −30.5 dB, el umbral con que el sidechain reconoce la voz). Sin eso, «salta de silencio a −18 dB». Es una lectura: con la regla de «alguna ventana intermedia» v5 ch01 quedaba a 0.04 dB del umbral; con esta queda a 4 dB.
2. **Silencio de voz** = hueco entre palabras mayor que la pausa más larga que el guion marca en ese cap (`[… pause]` del texto de la voz, por posición de palabra ±1; sin marcas, el hueco más largo entre oraciones). En Vajont no hay ninguno: los huecos largos son las marcas mismas.
3. **Costuras sin video**: ✓ si el black hold del cap saliente llega al corte (±1 cuadro), la narración (voz + sfx) está callada durante el negro y la unión es corte a negro (con `--gfx`, `concat_windowed(negro_frames)`: sin `fadewhite`).
4. **Segmentos** redondeados a cuadro hacia arriba (lo que hace el `-t` del render: 137.167 → 137.2 s); el audio de cada parte de la mezcla llega a esa duración (como el AAC del segmento real). Con eso esperado = medido en los 7 caps; antes del arreglo la mezcla se corría 1 cuadro por cap.
5. **B.6**: el tema de una oración = el mood de su palabra de mayor peso (≥ 2), un candidato por oración; el sello del pico queda como estaba. **B.7**: la cifra y su unidad salen del texto del bloque cuando el modelo no devuelve `unidad`/`valor`; un contador solo si su texto se lee en lo que dura (3.7 s).
6. Ediciones (§A.5) por `cap` + `pool_id`, sobre la respuesta del rotulista (después pasan todas las reglas) o, `escena`, sobre el plan colocado.

## Para Omar y el analista (pendientes, no decididos)
1. **La música va adelantada respecto de los caps (previo a F32, medido acá):** la pista de música arranca en el segundo 0 del mp4 (la intro de 2.5 s no la corre) y cada cruce de 2 s entre caps la adelanta otro poco: la música de ch02 empieza 4.6 s antes de su title card y la de ch07, **14.8 s antes**. Lo mismo vale para el mapa de intensidad (los «silencio» y «sube» de F28 caen hasta 15 s antes de su voz). B.1 hizo que la pieza cubra el title card, pero la pieza no está alineada con el cap. Arreglarlo cambia la música del render: no se tocó.
2. **El render tiene que usar el plan aprobado.** El crítico de los sellos, en el render, mira el bloque dibujado (snapshot del navegador) y en el guion la foto sola: puede cambiar de veredicto. El del rotulista no (su caché es por identidad del bloque). El render que se pida después debería tomar los planes del guion aprobado (`gfx_plan_chNN.resolved.json`, que `apply_gfx` ya acepta como `gfx_plan_override`).
3. **`unidad`/`valor` no llegan**: con el prompt congelado salvo la línea de B.7, el formato de salida del USER no los pide; hoy los lee el código del texto. Si se quiere que los devuelva el modelo, hay que sumarlos al formato de salida.
4. **ch07 sin rampa** (−33.7 dB): la voz arranca seca y la música de ch07 está baja durante su title card.
5. **D117** (ch02): el reintento del rotulista escribió «1943» en la etiqueta y el candado lo saca (el año está en la voz, no en el dato). **D192** (ch06): le faltan 0.06 s de lectura. **Q50** (ch05): 179 caracteres no entran en ninguna escena del beat. Los tres son «DEBERÍA» posibles con `--plan-edit` (p. ej. etiqueta sin el año para D117, texto más corto para Q50).
6. **El sello «vida» (ch02) como tema muerte**: viene del léxico del perfil (peso 3); el catálogo lo respeta.
7. **B.4 también alcanza a D117** («dato de acta, va como rótulo»): la regla literal lo vuelve recorte. Si el analista quería solo cartas/actas como documento propio, hay que afinar la palabra.
8. **Dos bloques en la escena 0 de ch01 y ch07** (title card + sello del pico): el sello del pico es fijo; en ch01 hay una sola escena en todo el cap.

## Disco
Fuera de git: `lab/hyperframes/f32/mezcla_preview.wav` (186 MB) y lo regenerable de `output/f8s3-vajont-f30/_fase2b_work/` (planes, escenas, crudas, `mezcla_preview.wav`, `_preview_narracion.wav`). Los planes de v5 quedaron copiados en `output/f8s3-vajont-f30/_fase2b_work/_bak_v5/` antes de la primera corrida (los planes de trabajo ahora son los del guion F32). Nada se borró.

## Veredicto del revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

Las 6 partes de A, los 8 arreglos de B y los frenos están cumplidos. Varias medidas que el handoff pedía para Vajont NO se alcanzaron (B.1, B.3, B.4, B.5, B.7). El reporte las declara con honestidad, pero siguen sin cumplirse.

| # | requisito | estado | evidencia |
|---|---|---|---|
| A.1-A.4 | `gfx_guion.py`, `--plan-only`, `.md/.json`, mezcla wav | OK | `script_engine/gfx_guion.py` (646 líneas). `output/f8s3-vajont-f30/GUION_PANTALLA.md/.json` idénticos a las copias de `lab/hyperframes/f32/` (diff vacío). 200 eventos, 82 cortados y 10 sellos que quedan: coinciden con el reporte. `mezcla_preview.wav` de 186 MB existe y está sin trackear. |
| A.5 | `--plan-edit` | OK | `gfx_rotulista.aplicar_ediciones`, `mover_a_escena`; tests `test_plan_edit_*` |
| A.6 | tests sin red | PARCIAL | 18 de `test_module_f32.py` pasan. El fixture v5 no da el literal «5.65 vs 5.55, sin rampa»: da `✗ 5.62 s, −18 dB en 5.66 s, sin rampa`. Lo medí yo: en el mp3 la voz llega a −18 dB a 0.156 s y en la mezcla v5 a 5.656 s, o sea corrimiento de 5.50 exacto. La voz no pierde el ataque; el «5.55 esperado» del handoff estaba mal. Desvío justificado. |
| B.1 | pre-roll sin perder ataque; ch01 sin pre-roll; música con el title card; inicio de voz ✓ 7/7 | PARCIAL | ch01 esperada 2.62 = medida 2.62, ✓. Inicio de voz 6/7: ch07 ✗ (−33.7 dB). La medida «7/7» del handoff no se alcanzó. |
| B.2 | pregunta = caracteres ÷ 15 cps | OK | 7/7 ✓ en los chequeos A.3 del guion |
| B.3 | lectura contra corte; D117 vuelve | PARCIAL | Código y test OK. En Vajont D117 no vuelve: cae por candado ("1943" en la etiqueta que reescribió el modelo). Declarado. |
| B.4 | `a_pantalla` documento → recorte; Q50 sale | PARCIAL | Regla y test OK. Q50 es recorte pero cae por lectura (179 caracteres, 11.9 s). La medida «Q50 sale» no se cumple. |
| B.5 | 2 `a_pantalla` por beat; permitido en el pico; D128 y D192 en ch06 | PARCIAL | `A_PANTALLA_POR_BEAT=2` aplicado. D192 cae por lectura (143 caracteres piden 9.5 s). En pantalla 2/5 (D128, D245). |
| B.6 | sellos por tema; `punch_in` del director fuera | OK | `TEMA_DE_MOOD`, `sellos_por_tema`. 28 `punch_in` fuera y 6 `zoom_punch` intactos (cuenta propia sobre el json). |
| B.7 | una sola línea nueva en el prompt; cifra → agua / contador / lupa | OK en código, sin efecto en Vajont | md5 del prompt `c9231e24…` (mi corrida, `prompt_md5()`). El de F29c reconstruido da `7dafbb96…` (test `test_module_f32.py:367`). El diff del prompt es 1 línea. El modelo no devuelve `unidad`/`valor` y rige el respaldo por texto. Vajont no muestra ninguna animación. |
| B.8 | ficha más chica y etiqueta con placa | OK | `ficha_html`/`ficha_medida`, CSS `.tc-box.ficha`. `rgba(10,10,10,.35)` y `6px 26px` son los de `.co-text.stamp` (`gfx_common.css:27-28`). |
| C | guion, wav, tabla A.2, chequeos, costos, tiempo | OK | `--plan-only` 162 s (302 s la primera vez). Claude 0.2668 = 0.5004 del registro − 0.2336 previos (cuadra). Chequeos del reporte = `plan_only_C.log`. |
| Frenos | prompts de guion/escaleta/ficha intactos; archivos prohibidos fuera de git; sin render | OK | `git diff 0253672..HEAD --name-only` no toca `.env`, `config.py`, `_gpt_probe_analista` ni `gfx_profiles/`. Ningún prompt tocado salvo el del rotulista. md5 `38e5ba14…` de ch02 sin `--gfx` en `a/` y `b/` (logs; no lo re-corrí, es un render). |
| Suites | rápida y amplia verdes | OK | Corrí yo: rápida 58 passed; amplia 992 passed + 5 previas (01b_pauses ×3, m03_merge_timing ×2), con el árbol sin commitear. |
| Commits | uno por parte; ESTADO al final | PARCIAL | A y B existen (`308032a`, `2fde994`). C no existe todavía. `lab/ESTADO_SESION.md` dice "F32 en curso: A y B hechos"; falta el cierre de C. |

Observaciones:
1. `c/suite_amplia.log` está truncado (se corta al ~64 %). La evidencia de suite para C es solo la mía.
2. Se usó `--rotulista-tope 1.3` contra un tope de pedido de Claude ≤ 1. El gasto acumulado es 0.5004, así que no hubo exceso, pero el guard se aflojó. El handoff hablaba de 7 llamadas; hubo 21 (reintentos).
3. Gemini 0.0016: no aparece en ningún log ni json. NO VERIFICABLE (en el guion solo está `claude_rotulista_usd`).
4. Parámetros de medición nuevos fuera de §0: ventana de 10 ms, paso de 1 ms, correlación ±0.5 s, tolerancia de ±1 cuadro. Además, "voz presente" = `duck_threshold` reinterpreta la regla de rampa de A.3. Todo esto está declarado en «Lecturas», no en §0.
5. El guion final conserva 3 chequeos ✗ (dos bloques en la misma escena en ch01 y ch07; `a_pantalla`; inicio de voz ch07), todos declarados. El reporte sigue sin el veredicto (esperado).

Fuera de alcance: ninguno en los commits A y B. En el árbol, `diag_234_cap4.py`, `gfx_profiles/lexico_propuestas.json`, `gfx_profiles/misterio.json` y `lab/hyperframes/f28/a/f28a.log` figuran como modificados, pero ya lo estaban en el snapshot inicial y no están en los commits F32. Los cambios sin commitear de `gfx_rotulista.py` y `gfx_realizador.py` son de C y el guion de `lab/` está generado con ese código (mtime 12:20 contra guion 12:23).

Riesgos que el contrato no cubre:
- `lab/hyperframes/f32/mezcla_preview.wav` (186 MB) no está en `.gitignore`: un `git add` amplio en C lo mete. Lo mismo vale para los `gfx_profiles/*` modificados.
- El guion usa el crítico sobre la foto y el render lo usará sobre el bloque dibujado: el veredicto puede divergir. Además la música sigue desalineada hasta 14.8 s en ch07 (previo a F32, no tocado).
- Con la regla actual el beat de ch06 queda con solo 2 textos en pantalla en todo Vajont y 5 caps sin texto.

**Después del veredicto (CC):**
- Obs. 1: el revisor leyó `c/suite_amplia.log` mientras corría; terminó completo: **992 passed, 5 failed** (las 5 previas), rápida 58, md5 ch02 sin `--gfx` `38e5ba14…` (`c/onlycap_ch02_nogfx.log`).
- Obs. 2: el tope del rotulista es sobre su registro acumulado, que ya traía US$ 0.2336 de F29c; 1.3 = 1.0 de esta tanda + lo previo, con margen para el peor caso de las llamadas en vuelo (con 1.0 el tope frenó 3 caps en el prefetch y `apply_gfx` los rehízo en fila). Gasto real de la tanda: 0.2668 ≤ 1. Las 21 llamadas son 7 caps × hasta 3 intentos (reintentos por regla de contenido o `a_pantalla` faltante).
- Obs. 3: Gemini verificable = 0.0011 (`b/plan_only_B.log`: total 0.2679 − Claude 0.2668); los 0.0005 de la primera corrida de A quedaron en un log que se pisó. Corregido arriba.
- Obs. 4: son parámetros de la medición (no de la pantalla) y están declarados en «Lecturas»; quedan para que el analista los confirme.
- Obs. 5 y riesgos: declarados en «Para Omar y el analista». La mezcla no entra al commit (staging por ruta).
