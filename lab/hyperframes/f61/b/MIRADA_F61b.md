# MIRADA F61b — revisión visual a ciegas

Fuente: solo `hoja_f61b.jpg` (+ `f61b_05.png`, `f61b_07.png`, `f61b_10.png` abiertas en grande). Sin leer handoff, prompts ni json.

Planos pedidos: #1–#5 medium · #6 close · #7–#9 medium · #10 close.

| # | viva o posada | plano real (vs pedido) | cara visible | parecido a la madre |
|---|---|---|---|---|
| 1 | **3** — pareja parada frente a la casa de chapa, los dos a cámara, brazos caídos; foto de familia quieta (coherente con el ancla, pero posada). | **wide** (cuerpo entero, casa y terreno rojo dominan) — **3**, no coincide con medium. | sí, ambos de frente. | Daniel 8 · Marta 8 (rasgos, pelo y piel muy fieles). |
| 2 | **2** — hombre de pie en medio del camino, quieto, mirando al fotógrafo; carnet de cuerpo entero (botas/medias blancas visibles). | **wide** (cuerpo entero chico contra el galpón de chapa) — **3**, no coincide con medium. | sí, de frente. | Daniel 7 (misma cara, algo más flaco y con el pelo más corto). |
| 3 | **3** — novios en la escalinata de la iglesia, ambos a cámara con la familia detrás, nadie hace nada; retrato de boda clásico. | **medium** (de la cintura para arriba, familia en segundo plano) — **9**, coincide. | sí, ambos de frente. | Daniel 8 · Marta 8 (velo no la tapa; es ella). |
| 4 | **8** — cuatro personas a la mesa con tazas, se miran entre ellos y hablan; se lee la charla. | **medium** (mesa a la cintura) — **9**, coincide. | sí; la mujer izquierda y el hombre derecho de 3/4-perfil, los del centro de frente. | Milagros 6 (mujer de la izquierda: pelo ondulado y cara parecidas, un poco más mayor) · Ramón 5 (hombre de la derecha, de perfil: pelo y contextura sí, la cara se confirma poco). |
| 5 | **8** — niño subiendo la escalerilla del barco de la mano de la madre, mira hacia arriba; momento real, con dirección. | **wide** (cuerpo entero, barco entero de fondo) — **3**, no coincide con medium. | sí, de 3/4 (mirando hacia arriba); la madre de espaldas. | Víctor 6 (mismo pelo y cejas, pero se ve bastante más chico que el retrato madre). |
| 6 | **7** — hombre de espaldas-3/4 mirando hacia la mina, sombra larga; no hay acción pero sí mirada y tensión. | **medium close** (hombros y cabeza, algo de torso) — **7**, casi close; aceptable. | parcial, de perfil, mirando lejos. | Eric 5 (pelo castaño y peinado coinciden; se ve más joven y más flaco que la madre, y la cara apenas se ve). |
| 7 | **7** — mineros saliendo del túnel entre polvo; el protagonista con la mano en la boca (tos), mira a cámara; los demás caminan cabizbajos. Acción clara, aunque el protagonista «sabe» que lo fotografían. | **medium** sobre el protagonista (cintura arriba), grupo en wide — **7**, coincide en lo esencial. | sí, de frente. | Daniel 8 (muy reconocible; es el único de la fila que parece el retrato). |
| 8 | **3** — pareja con el bebé en brazos frente a la casa, los tres a cámara, inmóviles; foto de bautismo posada. | **medium** (muslos para arriba) — **8**, coincide. | sí, ambos de frente. | Marta 8 · Daniel 8. |
| 9 | **7** — hombre mayor sentado en la camilla, el médico de pie le habla/examina; se lee consulta. | **medium** (los dos de la cintura para arriba) — **9**, coincide. | sí, ambos de perfil-3/4. | sin madre (t2i). |
| 10 | **8** — oficial de aduana inclinado leyendo el pasaporte («BIRTHPLACE: WITTENOOM»), joven desenfocado detrás esperando; hay acción y tensión. | **close** (cabeza del oficial + detalle del pasaporte) — **9**, coincide. | oficial de perfil mirando abajo; el joven de frente pero desenfocado. | sin madre (t2i). |

## Totales

- Promedio «viva»: **5,6 / 10** (3+2+3+8+8+7+7+3+7+8 = 56).
- Posadas (viva ≤ 4): **4** (#1, #2, #3, #8) — todas las fotos de Daniel+Marta en Wittenoom/boda/bautismo salen como foto de carnet.
- Plano distinto al pedido: **3** (#1, #2, #5: pedían medium y salieron wide de cuerpo entero). #6 queda en medium-close, lo doy por aceptable.

## Conclusión

1. El parecido con la madre está resuelto: Daniel y Marta se reconocen en 8/10 en todas sus fotos (#1, #2, #3, #7, #8); las madres secundarias (Milagros, Ramón, Víctor, Eric) llegan a 5–6 porque el motor cambia edad o muestra la cara de perfil.
2. El problema es la pose: cuando hay madre y gente «presentada» (pareja, boda, bautismo, el minero solo), el motor devuelve retrato quieto a cámara (4 de 10 posadas); las fotos vivas son las que tienen una acción concreta en el ancla (tomar café, subir la escalera, toser, consulta, leer el pasaporte).
3. El plano medium se respeta solo cuando la escena tiene mesa, camilla o escalinata que corta a la cintura; en exteriores abiertos (casa de chapa, camino, barco) el motor abre a wide y la persona queda chica (3 de 10), lo contrario de lo que se pidió.
