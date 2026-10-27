# F37 parte B — simulación previa en seco de R1 (duración de la ficha) y R2 (mover en vez de cortar)

Contra: `lab/hyperframes/f36/d/GUION_PANTALLA.json` (F36, 120 eventos), planes resueltos y escenas de
`output/f8s3-vajont-f30/_fase2b_work/`, papel `data/scripts/_steps/f8s3-vajont/01e_pantalla.json`, palabras de
`output/audio/f8s3-vajont-f30/chNN_timestamps.json`. Sin correr fase2b ni ningún modelo; no se tocó nada del pipeline.
Constantes ya existentes: lectura = caracteres ÷ 15; callout_dur_min 2.5; callout_dur_max 6.0; mood_dur 2.5.
Caracteres = etiqueta + dato; la cita suma «» y la raya (+5) y el autor una sola vez (`rotulista_colocar.caracteres`).
Reproduje con las funciones reales (`tiempos`, `despues_del_corte`) los t0/t1 de F36 de las 8 colocadas: coinciden todos.

## R1 — duración = lectura acotada 2.5–6.0 s, nunca más allá del corte; si no alcanza la lectura, no entra desde ahí

Lectura literal usada: `lect = chars/15`; si `lect > 6.0` no entra nunca; `dur = clamp(lect, 2.5, 6.0)`; si
`resto = corte − t0 < lect` no entra desde ahí; si no, `dur = min(dur, resto)`. El instante de partida es la palabra ancla
del papel (no el `t` del guion, que para D117 es el instante ya movido y para Q50 es el pico). Leer «lectura» con o sin el
piso de 2.5 en la prueba del corte no cambia ningún resultado (D49: resto 2.64 ≥ 2.5).

| | propuestos | cortados por R1 | quedan |
|---|---|---|---|
| total | 9 (6 fichas, 2 citas, 1 recorte) | 1 (Q50, que hoy ya está cortada por lectura) | 7 en pantalla (las mismas de hoy) + D117 (cortada por el crítico, no por R1) |
| ch01 | 1 | 0 | 1 |
| ch02 | 1 | 0 | 0 (D117 cortada por el crítico) |
| ch03 | 2 | 0 | 2 |
| ch05 | 1 | 1 (Q50) | 0 |
| ch06 | 2 | 0 | 2 |
| ch07 | 2 | 0 | 2 |

Cambian de duración: 8 de 9 (todas menos Q50, que no tiene duración). Ya no entran en su instante: solo Q50.
R1 no cambia quién entra: cambia cuánto dura. Suma de segundos de texto en pantalla de las 7 colocadas: 50.42 s → 20.93 s.

| cap | id | t0 (palabra) | chars | lectura | dur vieja → nueva | resto al corte | estado |
|---|---|---|---|---|---|---|---|
| ch01 | D131 | 83.24 | 41 | 2.73 | 11.24 → 2.73 | 18.36 | entra |
| ch02 | D117 | 21.24 (hoy 24.60) | 60 | 4.00 | 6.52 → 4.00 | 3.36 desde la palabra | no entra desde la palabra; entra en 24.60 como hoy (F32 §B.3) |
| ch03 | T16 | 14.20 | 39 | 2.60 | 12.74 → 2.60 | 13.80 | entra |
| ch03 | D49 | 113.10 | 32 | 2.13 | 2.64 → 2.50 | 2.64 | entra (piso 2.5) |
| ch05 | Q50 | 27.48 | 127 | 8.47 | (cortada) | 3.35 | no entra nunca: 8.47 > 6.0 |
| ch06 | D01 | 23.06 | 54 | 3.60 | 5.44 → 3.60 | 6.07 | entra |
| ch06 | D17 | 154.94 | 33 | 2.20 | 5.72 → 2.50 | 19.26 | entra (piso 2.5) |
| ch07 | Q14 | 14.88 (hoy 18.20) | 65 | 4.33 | 5.26 → 4.33 | 3.32 desde la palabra | no entra desde la palabra; entra en 18.20 como hoy (F32 §B.3) |
| ch07 | D245 | 126.94 | 40 | 2.67 | 7.38 → 2.67 | 8.36 | entra |

Ejemplos: T16 ch03 14.2 s «LA VÍCTIMA DE PONTESEI / Arcangelo Tiziani»: 12.74 s → 2.60 s. D131 ch01 83.24 s «SALTO DE LA
MASA DE AGUA / Más de 260 metros»: 11.24 s → 2.73 s. Q50 ch05 27.48 s «ADMINISTRACIÓN DE ERTO Y CASSO / viviendo en
continua aprensión y en continua alarma»: 127 caracteres = 8.47 s > 6.0, no entra nunca (ni sin la etiqueta: 97 > 90).

Notas: el veredicto del crítico de fichas se guarda por (cap, id, texto, aporta) y mira el cuadro en t+1.0 s: R1 no cambia
el instante, así que no pide re-juicio de las 7. La guarda del papel (caben ≤ 6.0 × 15 = 90) ya deja a Q50 fuera en el papel.

## R2 — mover en vez de cortar (8 «papel sin colocar» de F36)

Orden: 1) otro instante de la misma oración (palabra de más peso, inicio, palabra ancla); 2) inicio de la escena siguiente
si cae dentro de la misma oración; 3) inicio de la oración siguiente si es del mismo beat; 4) solo crítico: el otro lado.
Cada intento pasa «no cruza el corte / se lee» (sello 2.5 s; ficha con R1), «nunca al mismo tiempo» con lo ya puesto
(title card, fichas con duración R1, reloj, otros sellos) y el crítico. Hoy «nunca al mismo tiempo» no cortó ningún bloque
del papel en F36 (`rotulista.escena` vacío en los 7 caps).

| # | bloque | causa hoy | intentos mecánicos | resultado |
|---|---|---|---|---|
| 1 | AVISO ch04 (oración 14 [87.98, 94.32], escena 7 corta 88.03) | corte | 1) inicio 87.98 + 2.5 > 88.03, falla (no tiene palabra de peso); **2) inicio de la escena 8 = 88.03 s, dentro de la oración, entra (hasta 90.53 < 95.40)** | se coloca en 88.03 (escena 8); el crítico nunca lo vio en esa foto |
| 2 | SILENCIO ch05 (oración 10 [71.66, 73.08], escena 7 corta 74.13) | corte | 1) peso «ola» 71.94 + 2.5 = 74.44 y inicio 71.66 + 2.5 = 74.16 > 74.13 (por 27 ms), fallan; 2) la escena 8 empieza 74.13 > fin de la oración, no aplica; **3) oración 11 (mismo beat 8) en 74.14 s, escena 8, entra** | se coloca en 74.14 (1.06 s después de que termina «De la ola no hablaba nadie»); crítico pendiente |
| 3 | COLAPSO ch06 (oración 20 «Longarone ya no.» [111.16, 112.16], escena 11 corta 113.17) | corte | 1) inicio 111.16 + 2.5 = 113.66 > 113.17, falla; 2) la escena 12 empieza 113.17 > fin de la oración; 3) oración 21 empieza 113.16, pero es del beat 11 (la 20 es del 10), no es del mismo beat (y caería a 7 ms del corte) | **ninguno** |
| 4 | CALMA ch02 (oración 6 [56.14, 60.06]; crítico: tapa rostros y la Vespa, escena 6, derecha) | crítico | 1) peso «vida» 58.18 es el vetado; inicio 56.14 + 2.5 > 56.17, falla; 2) inicio de la escena 6 = 56.17 (misma foto, 2.0 s antes), mecánico ok; 3) oración 7 (mismo beat) 61.08, escena 6, ok; 4) izquierda | existen 3 intentos, los tres sobre la misma foto de la escena 6: **depende del re-juicio del crítico** |
| 5 | INMINENTE ch03 (oración 18 [119.64, 121.92]; crítico: tapa la fisura o el paisaje, escena 12, derecha) | crítico | 1) sin palabra de peso, el inicio es el vetado; 2) no hay corte dentro de la oración; 3) oración 19 (mismo beat) 122.88, escena 12, ok (no toca la pregunta de cierre de 129.0); 4) izquierda | existen 2 intentos, ambos sobre la misma foto de la escena 12: **depende del re-juicio del crítico** |
| 6 | RABIA ch06 (oración 31 [164.84, 166.58]; crítico: se superpone a un rostro, lado izquierdo, escena 15) | crítico | 1) sin palabra de peso, el inicio es el vetado; 2) sin corte en la oración; 3) es la última oración del cap, no hay siguiente; 4) derecha | existe 1 intento (derecha, misma foto): **depende del re-juicio del crítico** |
| 7 | D117 ch02 (oración 2 [19.20, 31.12], 60 chars = 4.0 s; crítico: tapa el documento que sostiene el hombre, escena 2) | crítico | 1) inicio 19.20 en la escena 1 (otra foto), 4.0 s < 5.40 al corte, ok; ancla «aprobó» 21.24 falla (3.36 < 4.0); 2) inicio de la escena 2 = 24.60 es el vetado (veredicto conocido); 3) oración 3 (mismo beat) 31.96, escena 3 (otra foto), ok; 4) derecha en la escena 2 | existen 3 intentos mecánicos, dos sobre fotos que el crítico no vio: **depende del re-juicio del crítico** |
| 8 | Q50 ch05 (lectura) | lectura | ningún instante cambia su lectura (8.47 s > 6.0 de R1; 97 chars incluso sin la etiqueta) | **ninguno**. Con la regla de hoy (sin tope de 6.0) R2 la pondría en el inicio de la oración 18.24 (12.59 s al corte), así que R1 y R2 se contradicen en Q50 |

Resumen: 2 se colocan mecánicamente (AVISO, SILENCIO; los dos todavía deben pasar el crítico en una foto que no vio), 4
dependen del re-juicio (CALMA, INMINENTE, RABIA, D117), 2 sin salida (COLAPSO, Q50). Techo 6 de 8, piso 0 si el crítico
veta lo que mueve. Llamadas al crítico en el peor caso: 11 (AVISO 1, SILENCIO 1, CALMA 3, INMINENTE 2, RABIA 1, D117 3).
