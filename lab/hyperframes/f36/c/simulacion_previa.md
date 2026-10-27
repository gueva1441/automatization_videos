# F36 C — simulación previa (agente `simulador`, antes del código de Fase 2)

Guion de entrada: `output/f8s3-vajont-f30/GUION_PANTALLA.json` (F36 B, md5 e2dacef3 = `lab/hyperframes/f36/b/`). Sin modelos, sin tocar el pipeline. Scripts del agente: `regla_nuevo.py`, `sim_cand.py` (scratchpad de la sesión) + `lab/tools/simular_regla.py`.

Predicado: cada bloque ocupa `[t_mp4, t_mp4 + d]` (cerrado: tocarse choca); sello d = 2.5 s; reloj/contador/agua su `dur`; ficha colocada su `dur`, ficha cortada su `lectura_min` (si pasa el corte, la escena siguiente, como `lectura`). Bloques: ficha/recorte, sello, reloj, agua, contador, tarjeta, title card, pregunta. Los choques entre candidatos se resuelven por tiempo (cota, no la prioridad real).

## R1 «nunca al mismo tiempo» en lugar de «una por escena» (DECISIONES 17:58)

| conjunto | propuestos | siguen cortados | vuelven |
|---|---|---|---|
| colocados hoy (5 textos + 9 sellos + 4 relojes) contra la regla nueva | 18 | **0 se cortan** | 18 quedan |
| R1a (literal): cortados por «la escena ya tiene» | 2 | 1 | **1** |
| R1b (ancha): R1a + 10 por «un sello por beat» | 12 | 2 | **10** |

- Ningún par colocado se solapa (el más cercano: contador 813.21–816.91 vs D192 822.73). Único toque: tarjeta 0–3 s y title card 3–6 s (adyacencia por diseño).
- R1a: **MEMORIA ch07 «ola» 1013.65 queda** (D245 terminó en 1006.43); ch04 «roca» 393.98 sigue cortado (dentro del reloj 4 NOV 1960, 391.13–395.56).
- R1b: los sellos pasarían de 9 a 19 → «un sello por beat» tiene que seguir en alguna parte (el papel).
- Contrato: 14 (MEMORIA cabe en 1013.65 y en 1025.7); 13 (el reloj T85 dura 9.03 s, 944.07–953.10: una ficha T85 en 944.07 choca; solo vale con reloj corto o la ficha en la escena 8); 9 (Q50 de 75 car. desde 527.71 termina 532.71, RABIA arranca 532.45: la regla saca uno); 11 (D192 ya no necesita saltar de escena). Sin efecto: 1–6, 8, 10, 12, 15.

## R2 Fase 2 sin `cantidad`, sin «pico solo a_pantalla» ni desempate; `coherencia` fuera del ORDEN

| escenario | propuestos | siguen cortados | vuelven |
|---|---|---|---|
| con el agua colocada hoy | 8 | 4 | 4 |
| sin agua (catálogo 18:17) | 8 | **3** | **5** |
| R1a + R2, sin agua | 10 | 4 | 6 |

Ejemplos: T21 ch03 b4 vuelve (251.23); D71 ch03 b5 vuelve (contradice la línea 5); D68 ch04 b7 vuelve; T85 ch07 b12 sigue cortada (choca con el reloj); D32 ch07 b13 vuelve. `coherencia` corta 0 eventos en el guion actual. Lectura: con el modelo fuera de Fase 2, el número de fichas depende entero del papel.

## R3 Catálogo 18:17: fuera agua, contador y lupa

3 propuestos → 3 cortados → 0 quedan (ch03 agua «20 m» 04:11.2, ch04 agua «715 m» 07:44.6, ch06 contador «1.910 personas» 13:33.2); la lupa D49 ya estaba cortada. Bloques colocados 36 → 33. Contrato: 7 sale (esperado), 11 solo como ficha, 6 solo como ficha.
