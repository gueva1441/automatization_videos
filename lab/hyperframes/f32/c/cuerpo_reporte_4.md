
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
