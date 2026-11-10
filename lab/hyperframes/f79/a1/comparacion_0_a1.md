# 0 → a1

- duracion_s: 798.266 → 777.766 (Δ -20.500)
- intro_s: 2.5 → None
- costos: {} → {'gemini_usd': 0.0035}

| cap | offset | seg_dur (Δ) | voz en el mp4 | inicio de voz medido | ok |
|---|---|---|---|---|---|
| ch01 | 2.5 → 0.0 | 66.8 → 66.8 (+0.000) | 2.66 → 0.16 | 2.66 → 0.16 | True → True |
| ch02 | 69.3 → 66.8 | 102.833 → 99.833 (-3.000) | 72.38 → 66.88 | 72.38 → 66.88 | True → True |
| ch03 | 172.133 → 166.633 | 172.7 → 169.7 (-3.000) | 175.213 → 166.713 | 175.213 → 166.713 | False → True |
| ch04 | 344.833 → 336.333 | 99.7 → 96.7 (-3.000) | 347.913 → 336.413 | 347.913 → 336.413 | True → True |
| ch05 | 444.533 → 433.033 | 131.833 → 128.833 (-3.000) | 447.633 → 433.133 | 447.633 → 433.133 | True → True |
| ch06 | 576.366 → 561.866 | 128.5 → 125.5 (-3.000) | 579.466 → 561.966 | 579.466 → 561.966 | True → True |
| ch07 | 704.866 → 687.366 | 93.4 → 90.4 (-3.000) | 707.966 → 687.466 | 707.966 → 687.466 | True → True |

## ch01 — La herida que no cerraba → La herida que no cerraba

| tipo | texto | t antes → después (Δ) | t_mp4 | queda | clase |
|---|---|---|---|---|---|
| costura | intro 2.5 s (primer cuadro congelado, sin voz) → title card  | 0.0 → 0.0 (+0.000) | 2.5 → 0.0 | True → True | igual (texto de costura nuevo) |

13 → 13 eventos; 13 con el mismo `t` y `queda`.

- costura después: el mp4 arranca con este cap → voz a 0.16 s del cap, con el title card encima 3.0 s desde 0.0 s
- tramos después: {'negro_s': 0.0, 'sube_desde_negro_s': 0.0, 'voz_s': 0.16, 'title_card_s': 3.0}

- costura después: negro 1.0 s al cierre del cap (black hold)
- tramos después: None

- golpe del title card: [('title_card', 0.05, 0)] [] → [('title_card', 0.05, 0)] []
- crítico: 5 preguntas, 0 llamadas (sin caché); veredictos que cambiaron: ninguno

## ch02 — A la tierra roja → A la tierra roja

| tipo | texto | t antes → después (Δ) | t_mp4 | queda | clase |
|---|---|---|---|---|---|
| costura | negro 1.0 s (black hold de ch01) → corte → sube desde negro  | 0.0 → 0.0 (+0.000) | 69.3 → 66.8 | True → True | igual (texto de costura nuevo) |
| reloj | 16 SEP · 1961 | 3.08 → 6.48 (+3.400) | 72.38 → 73.28 | True → True | otra |
| transición | cut | 12.667 → 9.667 (-3.000) | 81.967 → 76.467 | True → True | tiempo |
| cita | «En España no teníamos nada, ninguno de los dos.» — María Be | 12.72 → 9.72 (-3.000) | 82.02 → 76.52 | True → True | tiempo |
| transición | cut | 22.633 → 19.633 (-3.000) | 91.933 → 86.433 | True → True | tiempo |
| transición | cut | 31.233 → 28.233 (-3.000) | 100.533 → 95.033 | True → True | tiempo |
| transición | cut | 36.833 → 33.833 (-3.000) | 106.133 → 100.633 | True → True | tiempo |
| punch | zoom_punch 12 cuadros | 42.433 → 39.433 (-3.000) | 111.733 → 106.233 | True → True | tiempo |
| ficha | Operación Canguro, del franquismo, desde 1958 | 42.46 → 39.46 (-3.000) | 111.76 → 106.26 | True → True | tiempo |
| transición | cut | 48.2 → 45.2 (-3.000) | 117.5 → 112.0 | True → True | tiempo |
| transición | cut | 57.9 → 54.9 (-3.000) | 127.2 → 121.7 | True → True | tiempo |
| transición | cut | 66.467 → 63.467 (-3.000) | 135.767 → 130.267 | True → True | tiempo |
| transición | cut | 70.767 → 67.767 (-3.000) | 140.067 → 134.567 | True → True | tiempo |
| transición | cut | 73.767 → 70.767 (-3.000) | 143.067 → 137.567 | True → True | tiempo |
| transición | cut | 77.833 → 74.833 (-3.000) | 147.133 → 141.633 | True → True | tiempo |
| transición | cut | 89.3 → 86.3 (-3.000) | 158.6 → 153.1 | True → True | tiempo |
| transición | cut | 93.3 → 90.3 (-3.000) | 162.6 → 157.1 | True → True | tiempo |
| transición | dip 10 cuadros | 95.967 → 92.967 (-3.000) | 165.267 → 159.767 | True → True | tiempo |
| costura | negro 1.0 s al cierre del cap (black hold) | 101.833 → 98.833 (-3.000) | 171.133 → 165.633 | True → True | tiempo |

20 → 20 eventos; 2 con el mismo `t` y `queda`.

- costura después: negro 1.0 s (black hold de ch01) → corte → sube desde negro en 10 cuadros (0.33 s) → voz a 0.08 s del cap, con el title card encima 3.0 s desde 0.0 s
- tramos después: {'negro_s': 1.0, 'sube_desde_negro_s': 0.333, 'voz_s': 0.08, 'title_card_s': 3.0}

- costura después: negro 1.0 s al cierre del cap (black hold)
- tramos después: None

- golpe del title card: [('title_card', 0.05, 0)] [] → [('title_card', 0.16, 110)] []
- crítico: 2 preguntas, 2 llamadas (sin caché); veredictos que cambiaron: ninguno

## ch03 — Ignorar el veneno → Ignorar el veneno

| tipo | texto | t antes → después (Δ) | t_mp4 | queda | clase |
|---|---|---|---|---|---|
| costura | negro 1.0 s (black hold de ch02) → corte → sube desde negro  | 0.0 → 0.0 (+0.000) | 172.133 → 166.633 | True → True | igual (texto de costura nuevo) |
| transición | cut | 12.533 → 9.533 (-3.000) | 184.666 → 176.166 | True → True | tiempo |
| cita | «el desierto de los desiertos» — Víctor Calvo | 23.36 → 20.36 (-3.000) | 195.493 → 186.993 | True → True | tiempo |
| transición | cut | 31.567 → 28.567 (-3.000) | 203.7 → 195.2 | True → True | tiempo |
| transición | cut | 48.067 → 45.067 (-3.000) | 220.2 → 211.7 | True → True | tiempo |
| transición | cut | 66.733 → 63.733 (-3.000) | 238.866 → 230.366 | True → True | tiempo |
| transición | dissolve 20 cuadros | 81.467 → 78.467 (-3.000) | 253.6 → 245.1 | True → True | tiempo |
| transición | cut | 90.867 → 87.867 (-3.000) | 263.0 → 254.5 | True → True | tiempo |
| sello | AVISO | 90.9 → 97.8 (+6.900) | 263.033 → 264.433 | True → True | otra |
| transición | cut | 106.867 → 103.867 (-3.000) | 279.0 → 270.5 | True → True | tiempo |
| transición | cut | 115.967 → 112.967 (-3.000) | 288.1 → 279.6 | True → True | tiempo |
| transición | cut | 121.167 → 118.167 (-3.000) | 293.3 → 284.8 | True → True | tiempo |
| transición | cut | 130.167 → 127.167 (-3.000) | 302.3 → 293.8 | True → True | tiempo |
| punch | zoom_punch 12 cuadros | 134.833 → 131.833 (-3.000) | 306.966 → 298.466 | True → True | tiempo |
| ficha | Limpiaba el molino para las inspecciones | 138.46 → 135.46 (-3.000) | 310.593 → 302.093 | True → True | tiempo |
| transición | cut | 145.9 → 142.9 (-3.000) | 318.033 → 309.533 | True → True | tiempo |
| transición | cut | 148.333 → 145.333 (-3.000) | 320.466 → 311.966 | True → True | tiempo |
| transición | cut | 156.233 → 153.233 (-3.000) | 328.366 → 319.866 | True → True | tiempo |
| transición | dip 10 cuadros | 165.467 → 162.467 (-3.000) | 337.6 → 329.1 | True → True | tiempo |
| costura | negro 1.0 s al cierre del cap (black hold) | 171.667 → 168.667 (-3.000) | 343.8 → 335.3 | True → True | tiempo |

21 → 21 eventos; 2 con el mismo `t` y `queda`.

- costura después: negro 1.0 s (black hold de ch02) → corte → sube desde negro en 10 cuadros (0.33 s) → voz a 0.08 s del cap, con el title card encima 3.0 s desde 0.0 s
- tramos después: {'negro_s': 1.0, 'sube_desde_negro_s': 0.333, 'voz_s': 0.08, 'title_card_s': 3.0}

- costura después: negro 1.0 s al cierre del cap (black hold)
- tramos después: None

- golpe del title card: [('title_card', 0.05, 0)] [] → [('title_card', 0.16, 110)] []
- crítico: 3 preguntas, 3 llamadas (sin caché); veredictos que cambiaron: [('sello', 'AVISO', ['ESTORBA', 'ESTORBA', 'NO ESTORBA'], ['NO ESTORBA'], [97.8])]

## ch04 — El juego peligroso → El juego peligroso

| tipo | texto | t antes → después (Δ) | t_mp4 | queda | clase |
|---|---|---|---|---|---|
| costura | negro 1.0 s (black hold de ch03) → corte → sube desde negro  | 0.0 → 0.0 (+0.000) | 344.833 → 336.333 | True → True | igual (texto de costura nuevo) |
| sello | CALMA | 0.0 → 92.1 (+92.100) | 344.833 → 428.433 | False → True | crítico |
| transición | cut | 9.2 → 6.2 (-3.000) | 354.033 → 342.533 | True → True | tiempo |
| transición | cut | 18.8 → 15.8 (-3.000) | 363.633 → 352.133 | True → True | tiempo |
| transición | cut | 24.267 → 21.267 (-3.000) | 369.1 → 357.6 | True → True | tiempo |
| transición | cut | 31.667 → 28.667 (-3.000) | 376.5 → 365.0 | True → True | tiempo |
| punch | zoom_punch 12 cuadros | 37.7 → 34.7 (-3.000) | 382.533 → 371.033 | True → True | tiempo |
| cita | «Nadie nos avisó de nada.» — Víctor Calvo | 45.66 → 42.66 (-3.000) | 390.493 → 378.993 | True → True | tiempo |
| transición | cut | 50.8 → 47.8 (-3.000) | 395.633 → 384.133 | True → True | tiempo |
| transición | cut | 55.333 → 52.333 (-3.000) | 400.166 → 388.666 | True → True | tiempo |
| transición | dissolve 20 cuadros | 61.933 → 58.933 (-3.000) | 406.766 → 395.266 | True → True | tiempo |
| ficha | Productor de televisión en España | 69.3 → 66.3 (-3.000) | 414.133 → 402.633 | True → True | tiempo |
| transición | cut | 69.3 → 66.3 (-3.000) | 414.133 → 402.633 | True → True | tiempo |
| transición | cut | 73.633 → 70.633 (-3.000) | 418.466 → 406.966 | True → True | tiempo |
| reloj | 7 JUL · 1963 | 80.3 → 77.3 (-3.000) | 425.133 → 413.633 | True → True | tiempo |
| transición | dissolve 20 cuadros | 80.3 → 77.3 (-3.000) | 425.133 → 413.633 | True → True | tiempo |
| transición | cut | 88.8 → 85.8 (-3.000) | 433.633 → 422.133 | True → True | tiempo |
| transición | dip 10 cuadros | 95.1 → 92.1 (-3.000) | 439.933 → 428.433 | True → True | tiempo |
| costura | negro 1.0 s al cierre del cap (black hold) | 98.7 → 95.7 (-3.000) | 443.533 → 432.033 | True → True | tiempo |

20 → 20 eventos; 2 con el mismo `t` y `queda`.

- costura después: negro 1.0 s (black hold de ch03) → corte → sube desde negro en 10 cuadros (0.33 s) → voz a 0.08 s del cap, con el title card encima 3.0 s desde 0.0 s
- tramos después: {'negro_s': 1.0, 'sube_desde_negro_s': 0.333, 'voz_s': 0.08, 'title_card_s': 3.0}

- costura después: negro 1.0 s al cierre del cap (black hold)
- tramos después: None

- golpe del title card: [('title_card', 0.05, 0)] [] → [] ["sfx descartado: title_card @ 0.05s cae sobre 'Daniel' sin hueco ≤ 120 ms"]
- crítico: 3 preguntas, 3 llamadas (sin caché); veredictos que cambiaron: [('sello', 'CALMA', ['ESTORBA', 'ESTORBA'], ['NO ESTORBA'], [92.1])]

## ch05 — Wittenoom por dentro → Wittenoom por dentro

| tipo | texto | t antes → después (Δ) | t_mp4 | queda | clase |
|---|---|---|---|---|---|
| costura | negro 1.0 s (black hold de ch04) → corte → sube desde negro  | 0.0 → 0.0 (+0.000) | 444.533 → 433.033 | True → True | igual (texto de costura nuevo) |
| transición | cut | 6.9 → 3.9 (-3.000) | 451.433 → 436.933 | True → True | tiempo |
| transición | cut | 15.067 → 12.067 (-3.000) | 459.6 → 445.1 | True → True | tiempo |
| transición | cut | 21.9 → 18.9 (-3.000) | 466.433 → 451.933 | True → True | tiempo |
| transición | cut | 25.167 → 22.167 (-3.000) | 469.7 → 455.2 | True → True | tiempo |
| transición | cut | 29.967 → 26.967 (-3.000) | 474.5 → 460.0 | True → True | tiempo |
| transición | cut | 39.533 → 36.533 (-3.000) | 484.066 → 469.566 | True → True | tiempo |
| ficha | 18,3 millones de dólares australianos a 200 afectados | 41.98 → 38.98 (-3.000) | 486.513 → 472.013 | True → True | tiempo |
| transición | cut | 51.5 → 48.5 (-3.000) | 496.033 → 481.533 | True → True | tiempo |
| sello | INMINENTE | 54.46 → 51.46 (-3.000) | 498.993 → 484.493 | True → True | tiempo |
| transición | dissolve 20 cuadros | 59.433 → 56.433 (-3.000) | 503.966 → 489.466 | True → True | tiempo |
| transición | cut | 68.4 → 65.4 (-3.000) | 512.933 → 498.433 | True → True | tiempo |
| transición | cut | 77.2 → 74.2 (-3.000) | 521.733 → 507.233 | True → True | tiempo |
| transición | cut | 86.667 → 83.667 (-3.000) | 531.2 → 516.7 | True → True | tiempo |
| transición | cut | 93.033 → 90.033 (-3.000) | 537.566 → 523.066 | True → True | tiempo |
| punch | zoom_punch 12 cuadros | 98.5 → 95.5 (-3.000) | 543.033 → 528.533 | True → True | tiempo |
| transición | cut | 111.3 → 108.3 (-3.000) | 555.833 → 541.333 | True → True | tiempo |
| cita | «una empresa que no tuvo reparos» — Daniel Écija (hijo) | 111.88 → 108.88 (-3.000) | 556.413 → 541.913 | True → True | tiempo |
| transición | dip 10 cuadros | 123.567 → 120.567 (-3.000) | 568.1 → 553.6 | True → True | tiempo |
| costura | negro 1.0 s al cierre del cap (black hold) | 130.833 → 127.833 (-3.000) | 575.366 → 560.866 | True → True | tiempo |

22 → 22 eventos; 3 con el mismo `t` y `queda`.

- costura después: negro 1.0 s (black hold de ch04) → corte → sube desde negro en 10 cuadros (0.33 s) → voz a 0.10 s del cap, con el title card encima 3.0 s desde 0.0 s
- tramos después: {'negro_s': 1.0, 'sube_desde_negro_s': 0.333, 'voz_s': 0.1, 'title_card_s': 3.0}

- costura después: negro 1.0 s al cierre del cap (black hold)
- tramos después: None

- golpe del title card: [('title_card', 0.05, 0)] [] → [('title_card', 0.05, 0)] []
- crítico: 4 preguntas, 4 llamadas (sin caché); veredictos que cambiaron: ninguno

## ch06 — El polvo viaja → El polvo viaja

| tipo | texto | t antes → después (Δ) | t_mp4 | queda | clase |
|---|---|---|---|---|---|
| costura | negro 1.0 s (black hold de ch05) → corte → sube desde negro  | 0.0 → 0.0 (+0.000) | 576.366 → 561.866 | True → True | igual (texto de costura nuevo) |
| transición | cut | 8.667 → 5.667 (-3.000) | 585.033 → 567.533 | True → True | tiempo |
| transición | cut | 14.933 → 11.933 (-3.000) | 591.299 → 573.799 | True → True | tiempo |
| transición | cut | 24.533 → 21.533 (-3.000) | 600.899 → 583.399 | True → True | tiempo |
| transición | cut | 31.567 → 28.567 (-3.000) | 607.933 → 590.433 | True → True | tiempo |
| transición | cut | 38.933 → 35.933 (-3.000) | 615.299 → 597.799 | True → True | tiempo |
| transición | cut | 47.033 → 44.033 (-3.000) | 623.399 → 605.899 | True → True | tiempo |
| transición | cut | 51.733 → 48.733 (-3.000) | 628.099 → 610.599 | True → True | tiempo |
| transición | cut | 60.733 → 57.733 (-3.000) | 637.099 → 619.599 | True → True | tiempo |
| sello | ALARMA | 60.76 → 57.76 (-3.000) | 637.126 → 619.626 | True → True | tiempo |
| cita | «solo fueron en una excursión del colegio» — John de Juan | 63.62 → 60.62 (-3.000) | 639.986 → 622.486 | True → True | tiempo |
| transición | cut | 71.267 → 68.267 (-3.000) | 647.633 → 630.133 | True → True | tiempo |
| punch | zoom_punch 12 cuadros | 75.767 → 72.767 (-3.000) | 652.133 → 634.633 | True → True | tiempo |
| ficha | El ministro Jon Ford | 78.34 → 75.34 (-3.000) | 654.706 → 637.206 | True → True | tiempo |
| transición | cut | 85.033 → 82.033 (-3.000) | 661.399 → 643.899 | True → True | tiempo |
| transición | cut | 91.833 → 88.833 (-3.000) | 668.199 → 650.699 | True → True | tiempo |
| transición | cut | 98.5 → 95.5 (-3.000) | 674.866 → 657.366 | True → True | tiempo |
| transición | cut | 108.167 → 105.167 (-3.000) | 684.533 → 667.033 | True → True | tiempo |
| sello | RABIA | 115.9 → 112.9 (-3.000) | 692.266 → 674.766 | True → True | tiempo |
| transición | dip 10 cuadros | 124.233 → 121.233 (-3.000) | 700.599 → 683.099 | True → True | tiempo |
| costura | negro 1.0 s al cierre del cap (black hold) | 127.5 → 124.5 (-3.000) | 703.866 → 686.366 | True → True | tiempo |

22 → 22 eventos; 2 con el mismo `t` y `queda`.

- costura después: negro 1.0 s (black hold de ch05) → corte → sube desde negro en 10 cuadros (0.33 s) → voz a 0.10 s del cap, con el title card encima 3.0 s desde 0.0 s
- tramos después: {'negro_s': 1.0, 'sube_desde_negro_s': 0.333, 'voz_s': 0.1, 'title_card_s': 3.0}

- costura después: negro 1.0 s al cierre del cap (black hold)
- tramos después: None

- golpe del title card: [('title_card', 0.05, 0)] [] → [('title_card', 0.05, 0)] []
- crítico: 8 preguntas, 8 llamadas (sin caché); veredictos que cambiaron: ninguno

## ch07 — La herida ancestral → La herida ancestral

| tipo | texto | t antes → después (Δ) | t_mp4 | queda | clase |
|---|---|---|---|---|---|
| costura | negro 1.0 s (black hold de ch06) → corte → sube desde negro  | 0.0 → 0.0 (+0.000) | 704.866 → 687.366 | True → True | igual (texto de costura nuevo) |
| transición | cut | 7.767 → 4.767 (-3.000) | 712.633 → 692.133 | True → True | tiempo |
| transición | cut | 15.733 → 12.733 (-3.000) | 720.599 → 700.099 | True → True | tiempo |
| transición | cut | 25.9 → 22.9 (-3.000) | 730.766 → 710.266 | True → True | tiempo |
| transición | cut | 30.5 → 27.5 (-3.000) | 735.366 → 714.866 | True → True | tiempo |
| punch | zoom_punch 12 cuadros | 32.667 → 29.667 (-3.000) | 737.533 → 717.033 | True → True | tiempo |
| ficha | 1.500 millones de dólares australianos | 34.88 → 31.88 (-3.000) | 739.746 → 719.246 | True → True | tiempo |
| transición | cut | 41.733 → 38.733 (-3.000) | 746.599 → 726.099 | True → True | tiempo |
| transición | cut | 51.433 → 48.433 (-3.000) | 756.299 → 735.799 | True → True | tiempo |
| transición | cut | 57.3 → 54.3 (-3.000) | 762.166 → 741.666 | True → True | tiempo |
| transición | cut | 61.933 → 58.933 (-3.000) | 766.799 → 746.299 | True → True | tiempo |
| transición | cut | 66.5 → 63.5 (-3.000) | 771.366 → 750.866 | True → True | tiempo |
| transición | cut | 69.267 → 66.267 (-3.000) | 774.133 → 753.633 | True → True | tiempo |
| sello | MEMORIA | 75.34 → 72.34 (-3.000) | 780.206 → 759.706 | True → True | tiempo |
| transición | dip 10 cuadros | 84.367 → 81.367 (-3.000) | 789.233 → 768.733 | True → True | tiempo |
| costura | negro 1.0 s al cierre del cap (black hold) | 92.367 → 89.367 (-3.000) | 797.233 → 776.733 | True → True | tiempo |

17 → 17 eventos; 2 con el mismo `t` y `queda`.

- costura después: negro 1.0 s (black hold de ch06) → corte → sube desde negro en 10 cuadros (0.33 s) → voz a 0.10 s del cap, con el title card encima 3.0 s desde 0.0 s
- tramos después: {'negro_s': 1.0, 'sube_desde_negro_s': 0.333, 'voz_s': 0.1, 'title_card_s': 3.0}

- costura después: negro 1.0 s al cierre del cap (black hold)
- tramos después: None

- golpe del title card: [('title_card', 0.05, 0)] [] → [('title_card', 0.05, 0)] []
- crítico: 2 preguntas, 2 llamadas (sin caché); veredictos que cambiaron: ninguno

## Música por cap

- ch01: {"title_card_s": 2.5, "medido_s": 2.5, "desvio_s": -0.0, "desvio_cuadros": -0.0, "ok": true} → {"inicio_cap_s": 0.0, "medido_s": 0.0, "desvio_s": 0.0, "desvio_cuadros": 0.0, "ok": true}
- ch02: {"title_card_s": 69.3, "medido_s": 69.3, "desvio_s": 0.0, "desvio_cuadros": 0.0, "ok": true} → {"inicio_cap_s": 66.8, "medido_s": 66.8, "desvio_s": 0.0, "desvio_cuadros": 0.0, "ok": true}
- ch03: {"title_card_s": 172.133, "medido_s": 179.033, "desvio_s": 6.9, "desvio_cuadros": 207.01, "ok": false} → {"inicio_cap_s": 166.633, "medido_s": 175.536, "desvio_s": 8.903, "desvio_cuadros": 267.09, "ok": false}
- ch04: {"title_card_s": 344.833, "medido_s": 344.833, "desvio_s": 0.0, "desvio_cuadros": 0.0, "ok": true} → {"inicio_cap_s": 336.333, "medido_s": 336.333, "desvio_s": 0.0, "desvio_cuadros": 0.0, "ok": true}
- ch05: {"title_card_s": 444.533, "medido_s": 444.533, "desvio_s": 0.0, "desvio_cuadros": 0.0, "ok": true} → {"inicio_cap_s": 433.033, "medido_s": 433.033, "desvio_s": 0.0, "desvio_cuadros": 0.0, "ok": true}
- ch06: {"title_card_s": 576.366, "medido_s": 576.366, "desvio_s": 0.0, "desvio_cuadros": 0.0, "ok": true} → {"inicio_cap_s": 561.866, "medido_s": 561.866, "desvio_s": 0.0, "desvio_cuadros": 0.0, "ok": true}
- ch07: {"title_card_s": 704.866, "medido_s": 720.675, "desvio_s": 15.809, "desvio_cuadros": 474.27, "ok": false} → {"inicio_cap_s": 687.366, "medido_s": 700.369, "desvio_s": 13.003, "desvio_cuadros": 390.08, "ok": false}

## Chequeos

- ✓ → ✓ dos bloques al mismo tiempo
- ✓ → ✓ bloque que cruza un corte
- ✗ → ✗ texto sin lectura
    - ✗ ch05 09:01.9 cita ««una empresa que no tuvo reparos» — Dani»: dura 4.47 s y pide 4.53 s
- ✓ → ✓ cifra que contradice la voz
- ✗ → ✗ a_pantalla
    - ✗ 0/6 en pantalla
    - ✗ ch03 D01: el rotulista no lo propuso
    - ✗ ch05 D51: el rotulista no lo propuso
    - ✗ ch05 D23: el rotulista no lo propuso
    - ✗ ch06 D40: el rotulista no lo propuso
    - ✗ ch06 D34: el rotulista no lo propuso
    - ✗ ch07 D61: el rotulista no lo propuso
- ✓ → ✓ costuras con cuadro no negro
- ✗ → ✓ inicio de voz por cap
- ✓ → ✓ gancho no vacío
- ✗ → ✗ inicio de música por cap
    - ✗ ch03: inicio del cap 166.633 s · música medida 175.536 s · desvío +8.903 s (+267.09 cuadros)
    - ✗ ch07: inicio del cap 687.366 s · música medida 700.369 s · desvío +13.003 s (+390.08 cuadros)
- ✗ → ✗ papel sin colocar
    - ✗ ch05 sello SILENCIO: sello del papel «SILENCIO»: no entra en ningún intento: 1 · inicio de la oración (106.40 s): cruza el corte de la escena 13 (108.30 s) · 3 · oración siguiente [18] (108.28 s): cruza el corte de la escena 13 (108.30 s) · 3 · oración siguiente [18], inicio de la escena 14 (108.30 s): se solapa con ficha
- ✓ → ✓ papel sin alinear
- ✓ → ✓ relojes del papel (informativo)
