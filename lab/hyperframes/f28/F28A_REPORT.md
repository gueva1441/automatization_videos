# F28A_REPORT — paleta musical del canal: 30 pistas → medidas → Gemini escucha → PARADA (el analista elige 12)

CC · 2026-10-25 · base `4e18e8a`, rama `f11-guion-v4`, sin merge, nada publicado, nada borrado. Handoff
`lab/hyperframes/f28/HANDOFF_F28_paleta_musical.md`, **solo la parte A**.

## En corto
- **Generación:** 30 pistas de 180 s (5 por intent) más una de prueba, con ElevenLabs Music, endpoint `detailed` +
  `composition_plan` escrito por Gemini Flash.
  - Todas en `audio_library/_paleta_f28/`. No pasaron por el gate ni a la librería.
  - Gasto: **ElevenLabs US$ 13.95 de 25** (31 × 3 min a US$ 0.15/min). **Gemini US$ 0.86 de 3.** Claude 0.
- **Con las reglas de poda del handoff no queda ninguna.** Las 31 tienen fade en la costura.
  - ElevenLabs entra y sale en silencio aunque el plan pida «no fade-in / no fade-out». Los fades duran 0–10 s al
    entrar y 4–18 s al salir: son recortables.
  - Si se quita solo esa regla, quedan hook 5 · setup 2 · rising_tension 1 · shock 2 · consequences 3 · outro 1.
    **Rising_tension y outro quedan con menos de 3.**
  - La segunda causa es la tonalidad: 15 pistas dan «D major» o «A major» (la paralela o la dominante de Re menor).
- **Gemini escucha** las 30 sin errores.
  - Le pone 9–10 a las que son drone puro, y 3–7 a las que tienen un piano que «toca una melodía».
  - Como uso, elige «setup» en 28 de 30: para elegir intent no discrimina.
- **Archivos para elegir:** hoja `PALETA_espectros.jpg` (una fila por intent) y tabla completa abajo. **PARADA.**

## A.0 Pista de prueba y costo
- **Máximo de `music_length_ms`:** según la documentación del endpoint (`/v1/music/detailed`), va de 3,000 a
  **600,000 ms**, así que 180,000 entra.
  - Con `composition_plan`, `prompt` y `music_length_ms` no se usan (son excluyentes).
  - El largo es la suma de las secciones, de 3,000 a 120,000 ms cada una.
- **Cómo medí el costo (desvío):** la llave de ElevenLabs no tiene permiso `user_read`, así que no hay panel ni
  suscripción legible por API (HTTP 401 `missing_permissions`).
  - La respuesta de Music **no trae cabeceras de costo**: solo `song-id`, `x-trace-id` y `x-region` (guardadas
    completas en cada `pistas/<id>.json`).
  - Usé el precio publicado de la Music API: **US$ 0.15 por minuto en todos los planes**, facturado en dólares y no en
    créditos (elevenlabs.io/pricing/api).
  - Prueba: 180.04 s → US$ 0.45. 30 pistas ≈ US$ 13.50, menos de 25 → **30 pistas**.
  - Conviene que Omar lo confirme en su panel.

## A.1 Generación
- **Código** (`script_engine/m07_music_director.py`, sin tocar lo que ya existía):
  - `plan_composicion(intent, descripcion_del_canal, largo_ms)`: la función del test de Pripyat, con Gemini Flash.
  - `fijar_plan`: aplica las reglas fijas sin depender del modelo:
    - `"D minor"` en `positive_global_styles` (cualquier otra tonalidad se saca);
    - `NEGATIVE_GLOBAL_STYLES` de `music_config`;
    - nada con «fade» en los positivos;
    - «fade-in» en los negativos de la 1.ª sección y «fade-out» en la última;
    - la última sección con los mismos estilos que la primera (misma densidad);
    - 3–5 secciones;
    - duraciones que suman exactamente `largo_ms`.
  - `generar_con_plan(plan)`: POST `detailed` con `composition_plan`, una sola llamada, sin reintento.
  - `music_config`: `SONIDO_DEL_CANAL` (el párrafo del handoff, literal), `PALETA_INTENTS` (qué pide cada intent
    dentro de ese sonido, en inglés) y `PALETA_TONALIDAD`.
  - Tests: `test_module_f28a.py` (5, sin red). Suite amplia: **893 verdes + las 5 previas**.
- **Corrida** (`a/f28a_paleta.py generar`): freno con lock antes de cada pista (ElevenLabs 25, Gemini 3).
  - **8 de 30 cayeron con HTTP 429.** El plan de Omar admite **2 pedidos simultáneos** y yo mandé 3. Una más dio
    `system_busy`.
  - Un 429 no genera ni factura. **(Decisión)** Bajé a 2 workers y generé esas 8. Sus JSON fallidos quedaron en
    `_fallidas_429/` (movidos, no borrados).
  - Las 31 salieron de 180.0 s, en unos 30 s cada una.
  - Gemini Flash para los 31 planes: US$ 0.28.

## A.2 Medidas (0 API: numpy + ffmpeg; no hay librosa ni scipy, y no instalé nada)
`PALETA_medidas.json`.

**Medidas del handoff:**
- **ebur128:** I, LRA y pico.
- **Pulso:** autocorrelación de los ataques, en lags de 40–200 BPM. Calibrado: el drone de prueba da 0.08 y
  `hook_curated`, que pide «insistent pulse», da 0.83. La primera versión daba 0.83 también en el drone; está corregida.
- **Melodía:** cromagrama → entropía, dominancia y cambios de la nota dominante cada 2 s.
- **Tonalidad:** Krumhansl–Kessler.
- **Banda de la voz:** energía en 1–4 kHz y centroide espectral.
- **Costura:** coseno de los espectros de los últimos 2 s contra los primeros 2 s, y RMS de cada extremo contra la
  mediana.
- **Parecido:** distancia coseno de los MFCC medios entre pistas del mismo intent.

**Medidas agregadas, informativas (no cambian la poda):**
- **Duración de los fades** en segundos.
- **Huecos:** segundos con más de 20 dB por debajo de la mediana, entre los fades. hook_02 tiene **13 s de silencio
  en el medio**, que se ve en la hoja.
- **Pulso lento**, de 15–40 BPM (golpes cada 1.5–4 s, que la hoja muestra). Da alto en consequences_05 (0.64),
  setup_01 (0.44), consequences_02 (0.37) y rising_tension_01 (0.355).

**Rangos en las 30:**
- I −16.7 a −11.2 LUFS; LRA 2.0–9.7, así que **ninguna pasa de 12**.
- Banda de la voz ≤ 0.007: **ninguna se acerca a 0.30**. Son todas graves.
- Costura 0.17–0.90.
- Pulso > 0.35 solo en consequences_02 (0.38).

**Cómo leer la tonalidad:** sale D minor 12, **D major 10**, A major 4, A minor 2, F major 1 y A# major 1. En un
drone, la tercera es débil y Krumhansl confunde Re menor con Re mayor. La tónica es Re en 22 de 30. Apliqué la regla
tal como está (fuera si no es Re m / Fa M / La m); el analista decide si la tónica alcanza.

**Desacuerdo con Gemini en la melodía:** mi medida de melodía marca solo 1 (shock_02); Gemini oye melodía en 12. La
medida por nota dominante cada 2 s no ve un piano lento sobre un drone fuerte: **para melodía, mejor el oído de
Gemini.**

**Parecido:** dentro de cada intent, las pistas se parecen mucho (distancia de MFCC medio 0.001–0.10; las más cercanas,
setup_03/setup_05 0.0011 y hook_03/hook_04 0.0048). Es esperable: mismo plan base, misma tonalidad, mismo sonido.

## A.3 Gemini escucha
- Gemini 2.5 Pro con el mp3 entero (`Part.from_bytes`), una llamada por pista, 4 a la vez. El prompt lleva el párrafo
  del sonido del canal literal y esquema de respuesta. Crudo en `a/escucha/<id>.json`, con `finish_reason`.
- US$ 0.58. Ninguna respuesta vacía ni JSON roto.
- **Nota 10** (14 pistas): consequences_03, hook_02, hook_03, hook_04, hook_05, outro_01, outro_02, outro_03, rising_tension_04,
  rising_tension_05, setup_03, shock_01, shock_03, shock_04. Ninguna tiene melodía, pulso ni tráiler según Gemini.
- **Notas bajas, por melodía de piano:** rising_tension_01 3, consequences_05 3, setup_01 4 y shock_02 4 (shock_02
  también «suena a tráiler»).

## Tabla de las 30
| id | tonalidad (r) | pulso · lento | LRA | I LUFS | voz 1–4k | fade in/out s | hueco s | poda (reglas del handoff) | Gemini: nota · melodía · pulso · tráiler · compite | Gemini: mejor intent | lo que oye Gemini (corto) |
|---|---|---|---|---|---|---|---|---|---|---|---|
| hook_01 | D minor (0.62) | 0.09 · 0.02 | 2.3 | -11.7 | 0.001 | 2/12 | 0 | fade en la costura (-11.47 / -17.82 dB) | 6 · sí · no · no · sí | setup | Una pieza orquestal lenta y atmosférica |
| hook_02 | D minor (0.71) | 0.15 · 0.09 | 5.3 | -13.6 | 0.000 | 3/9 | 13 | fade en la costura (-78.52 / -69.39 dB) | 10 · no · no · no · no | setup | La pista consiste en drones de baja frecuencia y notas de un instrumento de cuerda grave, posiblemente un viol |
| hook_03 | D minor (0.56) | 0.07 · 0.05 | 3.2 | -11.2 | 0.000 | 1/9 | 0 | fade en la costura (-8.78 / -56.67 dB) | 10 · no · no · no · no | setup | Una pieza atmosférica y oscura construida sobre drones de cuerdas graves, como cellos y contrabajos |
| hook_04 | D minor (0.68) | 0.05 · 0.04 | 9.5 | -13.0 | 0.001 | 6/18 | 0 | fade en la costura (-49.05 / -50.06 dB) | 10 · no · no · no · no | setup | Una pista atmosférica construida sobre un drone de sintetizador grave y sostenido |
| hook_05 | D minor (0.61) | 0.08 · 0.05 | 5.1 | -11.8 | 0.000 | 5/10 | 0 | fade en la costura (-34.08 / -62.97 dB) | 10 · no · no · no · no | setup | Es una pista de ambiente oscuro y paciente, construida sobre drones de cuerdas graves y pads de sintetizador |
| setup_01 | D major (0.71) | 0.17 · 0.44 | 4.8 | -16.7 | 0.003 | 5/5 | 0 | tonalidad D major; fade en la costura (-32.47 / -28.88 dB) | 4 · sí · no · no · sí | setup | Una pieza atmosférica y melancólica |
| setup_02 | D major (0.66) | 0.11 · 0.08 | 5.6 | -12.5 | 0.002 | 3/8 | 0 | tonalidad D major; fade en la costura (-54.04 / -59.94 dB) | 6 · sí · no · no · sí | setup | Una pieza atmosférica que comienza con un drone grave y se desarrolla con la entrada de cuerdas sostenidas y p |
| setup_03 | D minor (0.63) | 0.08 · 0.05 | 3.0 | -12.8 | 0.000 | 5/6 | 0 | fade en la costura (-44.91 / -58.78 dB) | 10 · no · no · no · no | setup | Una pista ambiental y muy espaciosa construida sobre drones graves y pads etéreos que evolucionan lentamente |
| setup_04 | D minor (0.76) | 0.01 · 0.26 | 8.7 | -13.8 | 0.004 | 9/9 | 0 | fade en la costura (-45.56 / -43.26 dB) | 5 · sí · no · sí · sí | setup | Música atmosférica y lenta que comienza con pads profundos y un piano sencillo |
| setup_05 | A# major (0.73) | 0.08 · 0.07 | 8.5 | -13.6 | 0.000 | 8/7 | 0 | tonalidad A# major; fade en la costura (-45.47 / -53.2 dB) | 9 · no · no · no · no | setup | Una pista ambiental y atmosférica construida con pads de sintetizador que evolucionan lentamente |
| rising_tension_01 | A major (0.59) | 0.03 · 0.35 | 4.4 | -13.3 | 0.000 | 3/9 | 0 | tonalidad A major; fade en la costura (-39.61 / -63.43 dB) | 3 · sí · no · no · sí | setup | Una pista ambiental y lenta, dominada por una melodía de piano clara y melancólica |
| rising_tension_02 | D major (0.62) | 0.29 · 0.02 | 4.3 | -13.2 | 0.000 | 7/11 | 0 | tonalidad D major; fade en la costura (-47.81 / -80.06 dB) | 6 · sí · no · no · sí | setup | Pista atmosférica y melancólica con un piano espaciado y reverberante sobre un colchón de sintetizadores grave |
| rising_tension_03 | D minor (0.60) | 0.06 · 0.08 | 3.1 | -12.7 | 0.000 | 3/12 | 0 | fade en la costura (-22.94 / -54.14 dB) | 6 · sí · no · no · sí | setup | Una pieza ambiental y atmosférica construida sobre un drone grave y pads de sintetizador |
| rising_tension_04 | D major (0.74) | 0.07 · 0.07 | 4.9 | -11.8 | 0.001 | 8/8 | 0 | tonalidad D major; fade en la costura (-55.5 / -58.44 dB) | 10 · no · no · no · no | setup | Una pista ambiental y atmosférica con un carácter grave y paciente |
| rising_tension_05 | D major (0.76) | 0.08 · 0.07 | 7.3 | -13.4 | 0.005 | 9/13 | 0 | tonalidad D major; fade en la costura (-40.02 / -59.09 dB) | 10 · no · no · no · no | setup | Una pieza ambiental y atmosférica construida sobre capas de cuerdas graves sostenidas |
| shock_01 | A minor (0.63) | 0.07 · 0.07 | 2.0 | -11.7 | 0.000 | 2/4 | 0 | fade en la costura (-9.5 / -38.61 dB) | 10 · no · no · no · no | setup | Un drone grave y continuo, con texturas de cuerdas bajas que evolucionan lentamente |
| shock_02 | D major (0.70) | 0.04 · 0.04 | 3.4 | -12.2 | 0.002 | 2/9 | 0 | tonalidad D major; fade en la costura (-11.14 / -64.93 dB) | 4 · no · no · sí · sí | rising_tension | Una pieza de ambiente oscuro y tenso, construida sobre drones de cuerdas muy graves y sintetizadores |
| shock_03 | D minor (0.77) | 0.08 · 0.04 | 2.1 | -12.3 | 0.006 | 2/7 | 0 | fade en la costura (-10.85 / -54.07 dB) | 10 · no · no · no · no | setup | Una pista de drone ambiental, oscura y solemne |
| shock_04 | D major (0.66) | 0.06 · 0.06 | 7.7 | -11.9 | 0.000 | 1/4 | 0 | tonalidad D major; fade en la costura (-4.41 / -74.63 dB) | 10 · no · no · no · no | setup | Un drone grave y atmosférico creado por capas de cuerdas bajas sostenidas |
| shock_05 | A major (0.78) | 0.09 · 0.07 | 4.1 | -12.5 | 0.005 | 1/8 | 0 | tonalidad A major; fade en la costura (-7.39 / -74.24 dB) | 6 · sí · no · no · sí | setup | Una pista atmosférica y grave con una base de drones de cuerdas bajas y sintetizadores |
| consequences_01 | A minor (0.67) | 0.11 · 0.05 | 2.7 | -13.4 | 0.004 | 1/8 | 0 | fade en la costura (-6.49 / -50.67 dB) | 9 · no · no · no · no | setup | Una pista ambiental y sombría que comienza con un drone grave y profundo |
| consequences_02 | D minor (0.87) | 0.38 · 0.37 | 8.8 | -14.1 | 0.003 | 2/7 | 0 | pulso 0.382; fade en la costura (-16.87 / -59.25 dB) | 7 · sí · no · no · sí | setup | Una pista atmosférica y lenta que comienza con un drone grave |
| consequences_03 | D major (0.83) | 0.15 · 0.08 | 9.7 | -13.3 | 0.004 | 3/9 | 0 | tonalidad D major; fade en la costura (-28.12 / -51.43 dB) | 10 · no · no · no · no | setup | Una atmósfera grave y paciente creada por capas de cuerdas sostenidas con mucha reverberación |
| consequences_04 | D minor (0.66) | 0.03 · 0.17 | 7.4 | -13.9 | 0.001 | 4/11 | 0 | fade en la costura (-32.76 / -46.9 dB) | 9 · no · no · no · no | setup | Una pieza ambiental y lenta que se construye sobre pads de sintetizador graves y sostenidos |
| consequences_05 | F major (0.66) | 0.32 · 0.64 | 6.3 | -14.3 | 0.000 | 0/11 | 0 | fade en la costura (-3.01 / -74.89 dB) | 3 · sí · no · no · sí | setup | Un piano con mucha reverberación toca una melodía lenta, arpegiada y melancólica |
| outro_01 | D minor (0.78) | 0.08 · 0.08 | 3.9 | -12.6 | 0.002 | 3/14 | 0 | fade en la costura (-26.7 / -74.62 dB) | 10 · no · no · no · no | setup | Una pista ambiental y atmosférica construida con capas de sintetizadores y cuerdas sostenidas |
| outro_02 | D major (0.64) | 0.09 · 0.04 | 3.6 | -15.0 | 0.000 | 2/8 | 0 | tonalidad D major; fade en la costura (-9.29 / -45.14 dB) | 10 · no · no · no · no | setup | Una pieza atmosférica y lenta construida sobre drones de cuerdas graves, como cellos y contrabajos |
| outro_03 | D major (0.66) | 0.09 · 0.06 | 6.1 | -13.0 | 0.001 | 5/8 | 0 | tonalidad D major; fade en la costura (-28.59 / -63.0 dB) | 10 · no · no · no · no | setup | Una cama musical atmosférica y lenta, compuesta por capas de pads y cuerdas sintetizadas sostenidas |
| outro_04 | A major (0.76) | 0.09 · 0.06 | 5.6 | -13.5 | 0.004 | 10/8 | 0 | tonalidad A major; fade en la costura (-41.24 / -67.31 dB) | 7 · sí · no · no · sí | setup | Una pieza orquestal de cuerdas, lenta y sombría |
| outro_05 | A major (0.65) | 0.03 · 0.08 | 4.4 | -13.9 | 0.001 | 7/10 | 0 | tonalidad A major; fade en la costura (-47.02 / -63.7 dB) | 5 · sí · no · no · sí | consequences | Una pieza melancólica que comienza con cuerdas graves y sostenidas |

**Lectura de CC, para ayudar y no para elegir.** Cruzando las reglas del handoff menos la de fade, nota de Gemini ≥ 9,
sin melodía según Gemini y sin hueco, quedan:

| intent | pistas |
|---|---|
| hook | hook_03, hook_04, hook_05 |
| setup | setup_03 |
| rising_tension | ninguna |
| shock | shock_01, shock_03 |
| consequences | consequences_01, consequences_04 |
| outro | outro_01 |

- **Rising_tension:** sus dos notas 10 (rising_tension_04 y _05) caen solo por «D major».
- **Outro:** outro_02 y outro_03 (nota 10) caen por lo mismo.
- **Consequences:** consequences_03 (nota 10) también cae solo por «D major».

## Lo que se rompió o queda abierto
- **El plan no evita los fades.** ElevenLabs entra y sale en silencio igual. Para el loop de B hay que recortarlos al
  cargar (los segundos de cada pista están en la tabla) o hacer el crossfade del loop más largo.
- **429 por concurrencia** con 3 a la vez: el plan admite 2. Queda anotado en el runner.
- **Créditos no legibles:** la llave no tiene `user_read` y la respuesta no trae costo. Usé el precio publicado.
- **La tonalidad en drones es ambigua** para Krumhansl (menor ↔ mayor paralela).
- **Gemini no discrimina el uso:** pone «setup» en 28 de 30.
- **Lo que no se hizo:** los 30 mp3 no entraron a la librería ni a producción. B y C no se tocaron.

## Gasto
| | US$ | tope |
|---|---|---|
| ElevenLabs Music (31 pistas × 3 min, precio publicado) | 13.95 | 25 |
| Gemini (planes Flash 0.28 + escucha Pro 0.58) | 0.86 | 3 |
| Claude | 0 | 0 |

## Archivos
`lab/hyperframes/f28/`:
- **Raíz:** este reporte, `PALETA_espectros.jpg` (6 filas = intents × 5 pistas, en rojo las que podó la regla),
  `PALETA_medidas.json`, `suite_amplia_a.log`.
- **`a/`:**
  - Scripts y tabla: `f28a_paleta.py` (runner), `f28a_tabla.py`, `TABLA_PALETA.md`.
  - Costos y logs: `costos_f28a.json`, `f28a.log`, `generar.out`, `escucha.out`.
  - `escucha/` (30 crudos de Gemini) y `espectros/` (30 png).
  - `pistas/` (los 31 JSON: plan, plan devuelto, cabeceras, costo) y `pistas/_fallidas_429/`.
- **Los mp3** están en `audio_library/_paleta_f28/`, fuera de git: `audio_library/` está en `.gitignore`.

## Veredicto del revisor-handoff

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito (handoff F28 parte A) | estado | evidencia |
|---|---|---|---|
| 1 | A.0 prueba de 3 min antes de generar; costo anotado; tope US$25 para 30 pistas; máximo de music_length_ms | OK con desvío | costos_f28a.json: `_prueba_hook` 180.04 s, US$0.4501. Total 31 pistas = 13.953 (suma verificada). Reporte A.0 cita 600000 ms de la documentación (no lo pude verificar sin red). |
| 2 | 30 pistas de ~180 s, 5 por intent, endpoint detailed + composition_plan | OK | 31 mp3 en audio_library/_paleta_f28/ (todos 2.88 MB; ignorado por .gitignore:13). 30 JSON de pista + prueba; hook..outro × 5. |
| 3 | plan_composicion en m07, 3–5 secciones, Re menor, NEGATIVE_GLOBAL_STYLES, sin fade, primera=última densidad | OK | m07_music_director.py diff (plan_composicion, fijar_plan, generar_con_plan). Revisé los 31 planes guardados: `positive_global_styles[0]=="D minor"`, 3–5 secciones, suma exacta 180000, primera==última en estilos locales, "fade-in" en negativos de la 1.ª. 0 incumplimientos. test_module_f28a.py: 5 passed (lo corrí). Suite amplia: 893 verdes + 5 previas (suite_amplia_a.log). |
| 4 | SONIDO_DEL_CANAL literal | OK | music_config.py: coincide palabra por palabra con el párrafo del handoff. |
| 5 | No pasan por gate ni a la librería; no interactivo | OK | `git status`: sin cambios en audio_library; mp3 solo en _paleta_f28/. |
| 6 | Medidas: ebur128 (I, LRA, pico), pulso, melodía, tonalidad, banda 1–4 kHz + centroide, costura (corr + RMS), parecido MFCC | OK con desvío | PALETA_medidas.json: 30 pistas (+prueba), todos los campos presentes (pico_dbtp, pulso, entropia/dominancia/cambios, tonalidad_r, banda_voz, centroide_hz, costura_corr, rms_inicio/final, _mfcc). Calculado con numpy, no librosa (el handoff admitía "o librosa si se instala"; para melodía y tonalidad pedía cromagrama librosa: aquí equivalente propio). |
| 7 | Poda: marca, no borra; reglas del handoff; avisar si intent <3 | OK | Los 30 mp3 siguen en disco; el campo "poda" marca. Reglas en el JSON coinciden con el handoff. `quedan_por_intent` = 0 en todos (30 con fade); sin fade: hook 5, setup 2, rising 1, shock 2, cons 3, outro 1. Coincide con el reporte, que avisa rising y outro <3 (también setup y shock <3, el reporte lo da en la lista). |
| 8 | Gemini 2.5 Pro escucha las 30, JSON con los campos pedidos, crudo guardado, tope US$3 | OK | gemini_model_research = "gemini-2.5-pro" (config.py:61). 30 JSON en a/escucha/ con los 8 campos + finish_reason. Gemini total 0.8589 (0.0066+0.0545+0.2164+0.5814). |
| 9 | Reporte con tabla de 30 filas, créditos/US$, lo que se rompió | OK | F28A_REPORT.md: 30 filas, sección de gasto, "se rompió". |
| 10 | Hoja de 30 espectrogramas 6×5 | OK | PALETA_espectros.jpg (744 KB): la miré, 6 filas × 5 columnas, etiquetada. Las 30 salen marcadas PODA, así que el rojo no discrimina nada. |
| 11 | PARADA; veredicto como REVISOR_PENDIENTE | OK | F28A_REPORT.md:183-187. |

Contraste de cifras del reporte con los archivos:
- Coinciden: US$13.95 ElevenLabs; 8 fallos 429 (los 8 JSON en _fallidas_429/, generar.out muestra 7 por concurrencia y 1 system_busy); I −16.7 a −11.2; LRA 2.0–9.7; banda voz máx 0.0064; costura 0.17–0.90; pulso >0.35 solo consequences_02; tonalidades D minor 12 / D major 10 / A major 4 / A minor 2 / F major 1 / A# major 1; tónica Re 22; fades in 0–10 / out 4–18; hueco solo hook_02 (13 s); 14 notas 10 (lista idéntica); notas bajas 3,3,4,4; "quedan" por intent recalculado igual al del reporte.
- Cifras erradas en el reporte (menores): Gemini oye melodía en **12**, no 13; Gemini pone "setup" en **28**, no 27. Pulso lento de rising_tension_01 es 0.355 (reporte dice 0.36, redondeo). "Las 31 tienen fade": en las 30 de la paleta son 30/30; la prueba también.

Desvíos declarados:
- Costo por precio publicado (US$0.15/min): ACEPTABLE pero NO VERIFICADO. Las cabeceras de costo están vacías en todos los JSON (`cabeceras de costo {}`) y la llave no tiene user_read; la cifra es estimada, no medida. El reporte lo dice y pide a Omar confirmarlo en el panel. El handoff pedía "panel o cabecera"; ninguna fuente existió.
- Reintento de los 8 con 429 con 2 workers: ACEPTABLE. Un 429 no factura (afirmación del reporte, no comprobable aquí); no hay gasto doble en costos (31 entradas = 31 pistas). Los JSON fallidos se movieron, no se borraron.
- Medidas con numpy: ACEPTABLE, calibrado con drone vs hook_curated (0.08 vs 0.83) según reporte; la medida de melodía queda débil (marca 1 contra 12 de Gemini) y el reporte lo admite.
- Medidas extra (fades, huecos, pulso lento): ACEPTABLE, informativas, no cambian la poda. Pero "hueco" sí entra en la "Lectura de CC", que es una cuarta capa fuera de las reglas del handoff; está rotulada como ayuda.
- Corrección manual del costo Gemini de generar: ACEPTABLE y declarada en costos_f28a.json ("nota"). generar_1 = 0.2164 sale del log (0.223 − 0.0066), no del contador. Aritmética consistente (0.2775 en planes, 0.86 total).

Observaciones:
1. Resultado práctico de la poda: con las reglas literales no queda ninguna; la regla de fade (ElevenLabs entra y sale en silencio pese al plan) la dispara en 30/30. El reporte lo dice y da el conteo sin esa regla. Es hallazgo, no incumplimiento.
2. Tonalidad: Krumhansl confunde Re menor/mayor en drones; la poda por tonalidad es poco fiable y el reporte lo advierte.
3. El plan pidió "sin fade" en positivos y "fade-in/out" en negativos; no funcionó (ElevenLabs lo ignora). Para B habrá que recortar o hacer crossfade.

Fuera de alcance:
- M diag_234_cap4.py, M gfx_profiles/lexico_propuestas.json, M gfx_profiles/misterio.json: son ediciones del árbol anteriores a F28 (timestamps del 26-jun, 21-oct y 25-oct 13:30, antes del commit base de 13:48; el primer git status ya los traía). No son de la parte A. Deben quedar fuera del commit de F28A. Lo mismo para los untracked previos (_lab_*, _probe_*, QA_*, etc.) y lab/_gpt_probe_analista/ (el handoff prohíbe commitearlo).
- Dentro de alcance: music_config.py, script_engine/m07_music_director.py (solo adiciones), test_module_f28a.py, lab/hyperframes/f28/**. `.env` y config.py no tocados. Pendiente: ESTADO_SESION.md aún no actualizado (se hace después del veredicto, según el pedido). Sin merge, publicación ni borrado.

Riesgos que el contrato no cubre:
- El gasto de ElevenLabs es una estimación; si el plan de Omar factura en créditos distintos, el real puede diferir. Conviene contrastarlo con su panel antes de B.
- La paleta puede salir sin ninguna pista "limpia" por intent (rising_tension y outro): la elección de 12 (2 por intent) obliga al analista a aceptar pistas fuera de la regla de tonalidad o recortar fades.
- Las 30 pistas son muy parecidas entre sí (MFCC 0.001–0.10); la variedad real entre las 2 elegidas por intent puede ser baja.

**Después del veredicto (CC):** corregidas en el cuerpo las cifras que marca el revisor (melodía según Gemini 12, «setup» 28 de 30, pulso lento de rising_tension_01 0.355). Las 31 con fade = las 30 de la paleta + la prueba.

**PARADA: el analista elige las 12 (2 por intent) y las nombra.**
