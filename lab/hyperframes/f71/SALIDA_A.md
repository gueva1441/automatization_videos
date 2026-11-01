# F71 Etapa A: salida en texto (generada por script, sin llamadas)

## Wittenoom por cap

| Cap | Anclas | Antes | Después | Por trigrama | Por fallback | Literales en la narración | Por paso 2 (no literal) |
|---|---|---|---|---|---|---|---|
| ch01 | 8 | OK | OK | 8 | 0 | 8 | 0 |
| ch02 | 15 | None | OK | 15 | 0 | 14 | 1 |
| ch03 | 16 | None | OK | 16 | 0 | 16 | 0 |
| ch04 | 14 | OK | OK | 14 | 0 | 14 | 0 |
| ch05 | 16 | None | OK | 16 | 0 | 16 | 0 |
| ch06 | 16 | None | OK | 16 | 0 | 15 | 1 |
| ch07 | 12 | None | OK | 12 | 0 | 11 | 1 |

## Texto rearmado vs. lo que leyó la voz

- ch01: idéntico a `narration_normalized`
- ch02: idéntico a `narration_normalized`
- ch03: idéntico a `narration_normalized`
- ch04: idéntico a `narration_normalized`
- ch05: idéntico a `narration_normalized`
- ch06: idéntico a `narration_normalized`
- ch07: idéntico a `narration_normalized`

## QA Studio, `sync_approx` por cap (con el código nuevo)

- ch01: sync_approx = False · 9 segmentos
- ch02: sync_approx = False · 15 segmentos
- ch03: sync_approx = False · 16 segmentos
- ch04: sync_approx = False · 14 segmentos
- ch05: sync_approx = False · 16 segmentos
- ch06: sync_approx = False · 16 segmentos
- ch07: sync_approx = False · 13 segmentos

## Orleans `ba6c3cac-…`, antes y después

Tiene normalizado: no (usa normalize_for_tts, como antes).

| Cap | Anclas | Antes | Después | Igual |
|---|---|---|---|---|
| ch01 | 4 | OK | OK | sí |
| ch02 | 15 | OK | OK | sí |
| ch03 | 18 | OK | OK | sí |
| ch04 | 17 | OK | OK | sí |
| ch05 | 16 | OK | OK | sí |
| ch06 | 15 | OK | OK | sí |
| ch07 | 10 | OK | OK | sí |

## Por ancla, ch02, ch03, ch05, ch06 y ch07

### ch02

| # | start (s) | 3 palabras del audio | Ancla |
|---|---|---|---|
| 1 | 0.08 | El baile fue | El baile fue en el Círculo de… |
| 2 | 9.72 | De esa noche | De esa noche y de lo que… |
| 3 | 19.68 | Me pegué a | «Me pegué a mi marido, como una… |
| 4 | 28.28 | Se casaron un | Se casaron un año más tarde, el… |
| 5 | 33.88 | Cuatro días después | Cuatro días después estaban en un barco.… |
| 6 | 39.46 | No iban solos: | No iban solos: cerca de ocho mil… |
| 7 | 45.20 | y CSR, la | y CSR, la compañía dueña de la… |
| 8 | 54.90 | Allá los esperaban | Allá los esperaban ya Ramón de Juan… |
| 9 | 63.46 | con ellos, recuerda | con ellos, recuerda ella, se harían íntimos… |
| 10 | 67.76 | Víctor Calvo hizo | Víctor Calvo hizo esa travesía de niño.… |
| 11 | 70.76 | Salieron de Málaga | Salieron de Málaga y tardaron más de… |
| 12 | 74.80 | Pasaron por el | Pasaron por el canal de Suez. «Puf,… |
| 13 | 86.24 | Nadie sabía bien | Nadie sabía bien adónde iban ni cómo… |
| 14 | 90.22 | Del barco, a | Del barco, a un avión pequeño.… |
| 15 | 92.86 | Del avión, a | Del avión, a la tierra más roja… |

### ch03

| # | start (s) | 3 palabras del audio | Ancla |
|---|---|---|---|
| 1 | 0.08 | El avión era | El avión era pequeño, de hélices, y… |
| 2 | 9.60 | Aterrizamos en una | «Aterrizamos en una pista en medio de… |
| 3 | 28.62 | La pista donde | La pista donde aterrizaron estaba hecha con… |
| 4 | 45.12 | Las escuelas y | «Las escuelas y el jardín de infantes,… |
| 5 | 63.78 | Ese era el | Ese era el suelo donde Daniel iba… |
| 6 | 78.50 | En mil novecientos | En 1944, el inspector de minas y… |
| 7 | 87.90 | En mil novecientos | En 1948, un médico joven llegó en… |
| 8 | 103.90 | ABA era la | ABA era la empresa de CSR que… |
| 9 | 112.98 | Me desestimaron y, | «Me desestimaron y, de hecho, me tildaron… |
| 10 | 118.16 | La empresa tenía | La empresa tenía otra lectura: «El mero… |
| 11 | 127.14 | Faltaban catorce años | Faltaban catorce años para que Daniel Écija… |
| 12 | 131.78 | En mil novecientos | En 1957, un tribunal laboral entró al… |
| 13 | 142.82 | Faltaban cinco años. | Faltaban cinco años.… |
| 14 | 145.24 | En mil novecientos | En 1961, el año en que Daniel… |
| 15 | 153.14 | En mil novecientos | En 1962, un médico, Jim McNulty, comunicó… |
| 16 | 162.36 | Ese mismo año, | Ese mismo año, un recién casado de… |

### ch05

| # | start (s) | 3 palabras del audio | Ancla |
|---|---|---|---|
| 1 | 0.10 | Lo que dejaban | Lo que dejaban atrás siguió moliendo tres… |
| 2 | 4.00 | En diciembre de | En diciembre de 1966, James Vernon, de… |
| 3 | 12.16 | Las razones del | Las razones del anuncio eran económicas: no… |
| 4 | 19.00 | Ese mismo año | Ese mismo año los Écija volvieron a… |
| 5 | 22.24 | Con la mina | Con la mina cerrada, el suelo del… |
| 6 | 27.04 | En mil novecientos | En 1978 el gobierno del Estado empezó… |
| 7 | 36.60 | Y en mil | Y en 1988 un juez determinó que… |
| 8 | 48.56 | Veintidós años después | Veintidós años después del cierre. Para entonces,… |
| 9 | 56.48 | María guarda las | María guarda las fotografías en sepia: el… |
| 10 | 65.44 | En mil novecientos | En 1991, en Madrid, un diagnóstico puso… |
| 11 | 74.24 | La misma palabra | La misma palabra que McNulty había escrito… |
| 12 | 83.70 | Eso había en | Eso había en el polvo. Eso respiraba… |
| 13 | 90.04 | Daniel tenía cincuenta | Daniel tenía cincuenta y cinco años. María… |
| 14 | 95.48 | Nueve meses después | Nueve meses después del diagnóstico, Daniel Écija… |
| 15 | 108.28 | Ese lugar cambió | «Ese lugar cambió nuestras vidas para siempre»,… |
| 16 | 120.52 | Daniel había estado | Daniel había estado en Wittenoom diez. Y… |

### ch06

| # | start (s) | 3 palabras del audio | Ancla |
|---|---|---|---|
| 1 | 0.10 | Daniel se había | Daniel se había llevado de Wittenoom un… |
| 2 | 5.74 | El niño del | El niño del bautizo volvió a Australia… |
| 3 | 12.00 | Lo llevaba escrito | Lo llevaba escrito en el pasaporte. En… |
| 4 | 21.60 | Así que de | «Así que de Wittenoom, ¿eh? Un sitio… |
| 5 | 28.62 | Mercedes de Juan, | Mercedes de Juan, la hija de Ramón,… |
| 6 | 35.96 | Vive con una | Vive con una cita que se repite.… |
| 7 | 44.06 | Melita Markey dirige | Melita Markey dirige la Sociedad de Enfermedades… |
| 8 | 48.76 | Dice que el | Dice que el gobierno dejó de contar… |
| 9 | 57.76 | Daniel Écija es | Daniel Écija es uno de ellos. Markey… |
| 10 | 68.28 | El pueblo, mientras | El pueblo, mientras tanto, dejó de existir… |
| 11 | 72.76 | En junio de | En junio de 2007, Wittenoom fue abolido… |
| 12 | 82.02 | La zona quedó | La zona quedó declarada «no apta para… |
| 13 | 88.82 | Lo que no | Lo que no se puede abolir son… |
| 14 | 95.46 | El agua los | El agua los arrastra por los arroyos… |
| 15 | 105.12 | En dos mil | En 2016, un documento estatal aconsejó no… |
| 16 | 121.16 | En esa tierra | En esa tierra vivía un hombre que… |

### ch07

| # | start (s) | 3 palabras del audio | Ancla |
|---|---|---|---|
| 1 | 0.10 | Méitland Parker era | Maitland Parker era Banjima, y esa tierra… |
| 2 | 4.84 | En dos mil | En 2023, Marcos Orellana visitó Australia y… |
| 3 | 12.82 | Todavía lloro por | «Todavía lloro por mi territorio, pero eso… |
| 4 | 22.98 | Las barricadas que | Las barricadas que cortan la entrada al… |
| 5 | 27.56 | Maitland Parker murió | Maitland Parker murió de mesotelioma en 2024.… |
| 6 | 29.72 | en dos mil | En 2026, el pueblo Banjima llevó al… |
| 7 | 38.76 | Sus abogados sostienen | Sus abogados sostienen que el Estado no… |
| 8 | 48.44 | Quién sabía está | Quién sabía está escrito: dos inspectores en… |
| 9 | 54.28 | un médico al | un médico al que llamaron alborotador en… |
| 10 | 58.90 | un tribunal que | un tribunal que entró al molino en… |
| 11 | 63.46 | La mina siguió | La mina siguió hasta que dejó de… |
| 12 | 66.20 | La palada, todavía | La palada, todavía nadie. Daniel Écija vivió… |
