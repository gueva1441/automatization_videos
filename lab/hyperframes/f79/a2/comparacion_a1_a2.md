# a1 → a2

- duracion_s: 777.766 → 777.766 (Δ +0.000)
- intro_s: None → None
- costos: {'gemini_usd': 0.0035} → {}

| cap | offset | seg_dur (Δ) | voz en el mp4 | inicio de voz medido | ok |
|---|---|---|---|---|---|
| ch01 | 0.0 → 0.0 | 66.8 → 66.8 (+0.000) | 0.16 → 0.16 | 0.16 → 0.16 | True → True |
| ch02 | 66.8 → 66.8 | 99.833 → 99.833 (+0.000) | 66.88 → 66.88 | 66.88 → 66.88 | True → True |
| ch03 | 166.633 → 166.633 | 169.7 → 169.7 (+0.000) | 166.713 → 166.713 | 166.713 → 166.713 | True → True |
| ch04 | 336.333 → 336.333 | 96.7 → 96.7 (+0.000) | 336.413 → 336.413 | 336.413 → 336.413 | True → True |
| ch05 | 433.033 → 433.033 | 128.833 → 128.833 (+0.000) | 433.133 → 433.133 | 433.133 → 433.133 | True → True |
| ch06 | 561.866 → 561.866 | 125.5 → 125.5 (+0.000) | 561.966 → 561.966 | 561.966 → 561.966 | True → True |
| ch07 | 687.366 → 687.366 | 90.4 → 90.4 (+0.000) | 687.466 → 687.466 | 687.466 → 687.466 | True → True |

## ch01 — La herida que no cerraba → La herida que no cerraba

| tipo | texto | t antes → después (Δ) | t_mp4 | queda | clase |
|---|---|---|---|---|---|
| costura | el mp4 arranca con este cap → voz a 0.16 s del cap, con el t | 0.0 → 0.0 (+0.000) | 0.0 → 0.0 | True → True | igual (texto de costura nuevo) |
| title card | La herida que no cerraba | 0.0 → — | 0.0 → — | True → — | otra (no está) |

13 → 12 eventos; 12 con el mismo `t` y `queda`.

- costura después: el mp4 arranca con este cap → voz a 0.16 s del cap
- tramos después: {'negro_s': 0.0, 'sube_desde_negro_s': 0.0, 'voz_s': 0.16}

- costura después: negro 1.0 s al cierre del cap (black hold)
- tramos después: None

- golpe del title card: [('title_card', 0.05, 0)] [] → [] []
- crítico: 5 preguntas, 0 llamadas (sin caché); veredictos que cambiaron: ninguno

## ch02 — A la tierra roja → A la tierra roja

| tipo | texto | t antes → después (Δ) | t_mp4 | queda | clase |
|---|---|---|---|---|---|

20 → 20 eventos; 20 con el mismo `t` y `queda`.

- costura después: negro 1.0 s (black hold de ch01) → corte → sube desde negro en 10 cuadros (0.33 s) → voz a 0.08 s del cap, con el title card encima 3.0 s desde 0.0 s
- tramos después: {'negro_s': 1.0, 'sube_desde_negro_s': 0.333, 'voz_s': 0.08, 'title_card_s': 3.0}

- costura después: negro 1.0 s al cierre del cap (black hold)
- tramos después: None

- golpe del title card: [('title_card', 0.16, 110)] [] → [('title_card', 0.16, 110)] []
- crítico: 2 preguntas, 0 llamadas (sin caché); veredictos que cambiaron: ninguno

## ch03 — Ignorar el veneno → Ignorar el veneno

| tipo | texto | t antes → después (Δ) | t_mp4 | queda | clase |
|---|---|---|---|---|---|

21 → 21 eventos; 21 con el mismo `t` y `queda`.

- costura después: negro 1.0 s (black hold de ch02) → corte → sube desde negro en 10 cuadros (0.33 s) → voz a 0.08 s del cap, con el title card encima 3.0 s desde 0.0 s
- tramos después: {'negro_s': 1.0, 'sube_desde_negro_s': 0.333, 'voz_s': 0.08, 'title_card_s': 3.0}

- costura después: negro 1.0 s al cierre del cap (black hold)
- tramos después: None

- golpe del title card: [('title_card', 0.16, 110)] [] → [('title_card', 0.16, 110)] []
- crítico: 3 preguntas, 0 llamadas (sin caché); veredictos que cambiaron: ninguno

## ch04 — El juego peligroso → El juego peligroso

| tipo | texto | t antes → después (Δ) | t_mp4 | queda | clase |
|---|---|---|---|---|---|

20 → 20 eventos; 20 con el mismo `t` y `queda`.

- costura después: negro 1.0 s (black hold de ch03) → corte → sube desde negro en 10 cuadros (0.33 s) → voz a 0.08 s del cap, con el title card encima 3.0 s desde 0.0 s
- tramos después: {'negro_s': 1.0, 'sube_desde_negro_s': 0.333, 'voz_s': 0.08, 'title_card_s': 3.0}

- costura después: negro 1.0 s al cierre del cap (black hold)
- tramos después: None

- golpe del title card: [] ["sfx descartado: title_card @ 0.05s cae sobre 'Daniel' sin hueco ≤ 120 ms"] → [] ["sfx descartado: title_card @ 0.05s cae sobre 'Daniel' sin hueco ≤ 120 ms"]
- crítico: 3 preguntas, 0 llamadas (sin caché); veredictos que cambiaron: ninguno

## ch05 — Wittenoom por dentro → Wittenoom por dentro

| tipo | texto | t antes → después (Δ) | t_mp4 | queda | clase |
|---|---|---|---|---|---|

22 → 22 eventos; 22 con el mismo `t` y `queda`.

- costura después: negro 1.0 s (black hold de ch04) → corte → sube desde negro en 10 cuadros (0.33 s) → voz a 0.10 s del cap, con el title card encima 3.0 s desde 0.0 s
- tramos después: {'negro_s': 1.0, 'sube_desde_negro_s': 0.333, 'voz_s': 0.1, 'title_card_s': 3.0}

- costura después: negro 1.0 s al cierre del cap (black hold)
- tramos después: None

- golpe del title card: [('title_card', 0.05, 0)] [] → [('title_card', 0.05, 0)] []
- crítico: 4 preguntas, 0 llamadas (sin caché); veredictos que cambiaron: ninguno

## ch06 — El polvo viaja → El polvo viaja

| tipo | texto | t antes → después (Δ) | t_mp4 | queda | clase |
|---|---|---|---|---|---|

22 → 22 eventos; 22 con el mismo `t` y `queda`.

- costura después: negro 1.0 s (black hold de ch05) → corte → sube desde negro en 10 cuadros (0.33 s) → voz a 0.10 s del cap, con el title card encima 3.0 s desde 0.0 s
- tramos después: {'negro_s': 1.0, 'sube_desde_negro_s': 0.333, 'voz_s': 0.1, 'title_card_s': 3.0}

- costura después: negro 1.0 s al cierre del cap (black hold)
- tramos después: None

- golpe del title card: [('title_card', 0.05, 0)] [] → [('title_card', 0.05, 0)] []
- crítico: 8 preguntas, 0 llamadas (sin caché); veredictos que cambiaron: ninguno

## ch07 — La herida ancestral → La herida ancestral

| tipo | texto | t antes → después (Δ) | t_mp4 | queda | clase |
|---|---|---|---|---|---|

17 → 17 eventos; 17 con el mismo `t` y `queda`.

- costura después: negro 1.0 s (black hold de ch06) → corte → sube desde negro en 10 cuadros (0.33 s) → voz a 0.10 s del cap, con el title card encima 3.0 s desde 0.0 s
- tramos después: {'negro_s': 1.0, 'sube_desde_negro_s': 0.333, 'voz_s': 0.1, 'title_card_s': 3.0}

- costura después: negro 1.0 s al cierre del cap (black hold)
- tramos después: None

- golpe del title card: [('title_card', 0.05, 0)] [] → [('title_card', 0.05, 0)] []
- crítico: 2 preguntas, 0 llamadas (sin caché); veredictos que cambiaron: ninguno

## Música por cap

- ch01: {"inicio_cap_s": 0.0, "medido_s": 0.0, "desvio_s": 0.0, "desvio_cuadros": 0.0, "ok": true} → {"inicio_cap_s": 0.0, "medido_s": 0.0, "desvio_s": 0.0, "desvio_cuadros": 0.0, "ok": true}
- ch02: {"inicio_cap_s": 66.8, "medido_s": 66.8, "desvio_s": 0.0, "desvio_cuadros": 0.0, "ok": true} → {"inicio_cap_s": 66.8, "medido_s": 66.8, "desvio_s": 0.0, "desvio_cuadros": 0.0, "ok": true}
- ch03: {"inicio_cap_s": 166.633, "medido_s": 175.536, "desvio_s": 8.903, "desvio_cuadros": 267.09, "ok": false} → {"inicio_cap_s": 166.633, "medido_s": 175.536, "desvio_s": 8.903, "desvio_cuadros": 267.09, "ok": false}
- ch04: {"inicio_cap_s": 336.333, "medido_s": 336.333, "desvio_s": 0.0, "desvio_cuadros": 0.0, "ok": true} → {"inicio_cap_s": 336.333, "medido_s": 336.333, "desvio_s": 0.0, "desvio_cuadros": 0.0, "ok": true}
- ch05: {"inicio_cap_s": 433.033, "medido_s": 433.033, "desvio_s": 0.0, "desvio_cuadros": 0.0, "ok": true} → {"inicio_cap_s": 433.033, "medido_s": 433.033, "desvio_s": 0.0, "desvio_cuadros": 0.0, "ok": true}
- ch06: {"inicio_cap_s": 561.866, "medido_s": 561.866, "desvio_s": 0.0, "desvio_cuadros": 0.0, "ok": true} → {"inicio_cap_s": 561.866, "medido_s": 561.866, "desvio_s": 0.0, "desvio_cuadros": 0.0, "ok": true}
- ch07: {"inicio_cap_s": 687.366, "medido_s": 700.369, "desvio_s": 13.003, "desvio_cuadros": 390.08, "ok": false} → {"inicio_cap_s": 687.366, "medido_s": 700.369, "desvio_s": 13.003, "desvio_cuadros": 390.08, "ok": false}

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
- ✓ → ✓ inicio de voz por cap
- ✓ → ✓ gancho no vacío
- ✗ → ✗ inicio de música por cap
    - ✗ ch03: inicio del cap 166.633 s · música medida 175.536 s · desvío +8.903 s (+267.09 cuadros)
    - ✗ ch07: inicio del cap 687.366 s · música medida 700.369 s · desvío +13.003 s (+390.08 cuadros)
- ✗ → ✗ papel sin colocar
    - ✗ ch05 sello SILENCIO: sello del papel «SILENCIO»: no entra en ningún intento: 1 · inicio de la oración (106.40 s): cruza el corte de la escena 13 (108.30 s) · 3 · oración siguiente [18] (108.28 s): cruza el corte de la escena 13 (108.30 s) · 3 · oración siguiente [18], inicio de la escena 14 (108.30 s): se solapa con ficha
- ✓ → ✓ papel sin alinear
- ✓ → ✓ relojes del papel (informativo)
