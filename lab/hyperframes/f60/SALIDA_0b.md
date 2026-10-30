# F60 — Salida 0b (secuencia por la cola de fal + madre con ropa limpia, solo lab) — PARADA 0b

Handoff `lab/hyperframes/f60/HANDOFF_F60_0b_cola_y_madre_limpia.md` (md5 `30a632c578d98fa832bbc02bd90f1a34`, verificado). Sobre la copia de lab `lab/hyperframes/f60/base/` ya existente (no se rehizo). Runner `lab/hyperframes/f60/etapa0b_secuencia.py` (copia de `etapa0_secuencia.py` con los 4 cambios del handoff) → `e0b/etapa0b_pedidos.json`, `e0b/etapa0b.json`, `e0b/etapa0b.log`, imágenes en `e0b/` (fuera de git). `e0/` y `etapa0_secuencia.py` intactos. Producción intacta: de `asset_manager` solo se importan `_clip_poll`, `_fal_headers`, `FLUX_MAX_WORKERS`, `CLIP_POLL_TIMEOUT`; de `config`, `api` (`fal_base_url` = `https://queue.fal.run`).

**Resultado en una línea:** por la cola de fal los dos lotes volvieron completos (6/6 y 3/3) en paralelo, 286,1 s de pared; la madre con ropa limpia salió con camisa clara sin manchas; las manchas de la Etapa 0 ya no se arrastran, pero la camisa clara de la madre sigue siendo la base en las escenas que no imponen otra prenda (cubierta, veranda, pista, hospital, bajo el mameluco); en la foto de los mineros esta vez sí están de espaldas y Daniel aparte, sin contagio. Sin errores de fal, sin reintentos. Gasto US$ 0,35.

## 0b.1 Madre (Seedream v5 Lite t2i por la cola, `model_id` del perfil, `image_size` 2560×1440)

Prompt que fue a fal — **byte a byte igual** al del handoff (`prompt_madre_igual_al_handoff: true` en `etapa0b.json`):

    Head-and-shoulders portrait of a young adult Spanish migrant miner, wearing a plain, clean, light-coloured shirt. Spanish people of Mediterranean European origin with olive to light skin, dark brown to black hair and dark eyes. Neutral expression, facing the camera, plain mid-grey background, soft even light. A grainy 35mm documentary photograph taken in 1962, with muted colors and slight underexposure, in a dark-history realist style. No readable text, no signage, no labels.

- `request_id` `01a18ed4-d49e-7fb2-a5df-3b83d8972901` · submit 18:01:15 → vuelta 18:01:52 · **37,8 s** (submit → vuelta de `_clip_poll`, con cola) · seed 460661449 · 2560×1440 (JPEG con extensión .png) · `has_nsfw_concepts`: **no viene en la respuesta** (`None`; v5 Lite no lo devuelve, igual que `width`/`height`) · US$ 0,035.
- Foto `e0b/madre_daniel_ecija.png`: hombre joven, pelo oscuro corto, afeitado (sombra de barba leve), expresión neutra, fondo gris liso. **Ropa: camisa clara (crema), lisa, limpia, sin manchas ni polvo.** La frase de ropa funcionó; en la Etapa 0 la misma madre salió con camisa de trabajo manchada.

## 0b.2 Lotes (`/edit` secuencia por la cola, `image_urls=[data-uri de e0b/madre_daniel_ecija.png]`, `max_images=len(lote)`, `sequential_image_generation="auto"`, `num_images=1`, mismo prompt de secuencia que la Etapa 0)

Los 2 lotes se pidieron a la vez (`ThreadPoolExecutor(max_workers=min(2, FLUX_MAX_WORKERS=20))`) con la madre ya en disco; `request_id` escrito en `etapa0b_pedidos.json` antes de esperar; espera con `asset_manager._clip_poll` (600 s, poll 5 s, HTTP 15/30 s, tal cual).

| lote | fotos | pedidas / devueltas | `request_id` | submit → vuelta | s/foto | seed | `has_nsfw_concepts` | US$ (0,035 × devueltas) |
|---|---|---|---|---|---|---|---|---|
| 1 | ch02_img_01, ch02_img_02, ch02_img_04, ch02_img_05, ch03_img_16, ch04_img_07 (prompt 4608 chars) | 6 / **6** | `01a18ed5-6dfa-7ee0-ade6-d38eed7886dd` | 18:01:54 → 18:06:36 · **283,0 s** | 47,2 | 1780408611 | no viene (`None`) | 0,21 |
| 2 | ch04_img_09, ch04_img_14, ch05_img_05 (prompt 2405 chars) | 3 / **3** | `01a18ed5-6dff-7282-addd-f57d7bd862db` | 18:01:54 → 18:04:19 · **145,7 s** | 48,6 | 1200455859 | no viene (`None`) | 0,105 |

- **Tiempo de pared de los 2 lotes en paralelo: 286,1 s** (= el lote de 6; el de 3 corrió adentro). Las 9 fotos miden 2560×1440.
- El lote de 6 (283 s) confirma la proyección de la Etapa 0 (≈ 47,5 s/foto → 285 s): con `fal.run` síncrono a 240 s no entraba; con la cola y `CLIP_POLL_TIMEOUT` 600 s sobra. El submit nunca trajo `images` (siempre hubo que esperar).
- Ningún `TimeoutError`, `ContentRejectedError`, `RuntimeError` ni submit no-2xx. Sin reintentos.

## 0b.3 Tabla por foto — dos miradas

### Mirada de CC

| foto | ¿es la escena pedida? | cara de la madre (1–10 o «de espaldas») | contagio (caras-madre de más) | ropa del protagonista: ¿escena o madre? | anacronismos a la vista |
|---|---|---|---|---|---|
| L1 #1 ch02_img_01 (1961, baile) | **sí**: salón con arañas, dorados, parquet, parejas bailando desenfocadas; él y ella en el borde de la pista, cabeza inclinada hacia ella | 8 (perfil: cejas, nariz, pelo, mentón) | 0 | **escena**: traje oscuro, camisa blanca, corbata | ninguno; el vestido de ella es liso crema (el prompt pedía cotton-satin), menor |
| L1 #2 ch02_img_02 (1962, muelle) | **sí**: muelle, transatlántico, pasarela, grúas, multitud, carrito de equipaje, valijas de cartón; de espaldas/perfil hacia el barco; ángulo bajo | 6 (perfil parcial bajo el sombrero; pelo y nariz compatibles) | 0 | **escena**: traje oscuro y sombrero | ninguno |
| L1 #3 ch02_img_04 (1962, cubierta) | **sí**: cubierta, mar, baranda, ella pegada bajo su brazo, pasajeros desenfocados, plano medio tres cuartos | **9** (misma cara que la madre, de frente) | 0 | **escena = madre**: camisa clara en mangas de camisa; el prompt pide «shirtsleeves», así que coincide con la escena, y de paso es la camisa de la madre (limpia) | ninguno |
| L1 #4 ch02_img_05 (1962, veranda) | **sí**: veranda de chapa y fibro, tierra roja, dos parejas sentadas, lámpara, atardecer | 8 (el hombre de la izquierda) | **1 débil**: el hombre de la derecha se le parece (pelo, cejas) pero es otra cara | **escena**: camisa blanca **con polvo/manchas** (el prompt pide dust-coated); la ropa de la escena pisa a la de la madre | reloj de pulsera en el hombre de la derecha (posible, no claro); menor |
| L1 #5 ch03_img_16 (1962, pista) | **parcial**: pareja bajando por la escalerilla, casas de chapa, polvareda sobre la garganta, sol duro; **pero el avión es un jet ejecutivo moderno (estilo Gulfstream) con una hélice pegada en la nariz y turbinas en la cola**, y la pista es asfalto negro, no tailings gris-azulado | 7 (chico en el cuadro; pelo, cejas, cara compatible) | 0 | **escena**: camisa clara con manchas y pantalón oscuro (el prompt pide work shirt) | **sí**: el avión (jet de los 80–2000 con hélice) |
| L1 #6 ch04_img_07 (1963, hospital) | **sí** (solo, anochecer, ventana iluminada, calle de tailings, cerros); el edificio es de 2 plantas de revoque, no «low fibro-cement», menor | **8–9** (de frente, misma cara; pelo algo más abundante) | 0 | **escena**: camisa clara **muy sucia de polvo** (el prompt pide dust in his work shirt) | ninguno |
| L2 #1 ch04_img_09 (1962, bocamina) | **sí**: bocamina con portal de madera, paredes rojas, polvo en suspensión, tailings; **los mineros de espaldas y él aparte, mirando a cámara** (en la Etapa 0 estaban todos de frente) | **9** (de frente) | **0** (los demás de espaldas o de perfil lejano) | **mixta**: mameluco de trabajo sucio (escena) sobre **la camisa clara de la madre** asomando en el cuello | cascos (válidos en 1962); ninguno |
| L2 #2 ch04_img_14 (1963, pista con bebé) | **sí**: familia de espaldas, bebé envuelto, valijas junto a la avioneta de ala alta, pista de tailings gris-azulada, cañón rojo, hora dorada, sombras largas | de espaldas | 0 | **escena**: mameluco/camisa gris de trabajo | ninguno (avioneta tipo Cessna de ala alta, plausible en 1963) |
| L2 #3 ch05_img_05 (1966, Madrid) | **sí**: familia de espaldas entrando por el portal de un bloque de ladrillo con balcones de hierro, calle estrecha, luz nublada | de espaldas | 0 | **escena**: chaqueta oscura y pantalón | leves: aparato cuadrado en la fachada (¿portero eléctrico/caja?) y buzón metálico modernos; el nene con una especie de buzo con capucha; calle sin un solo coche ni cartel (demasiado limpia) |

### Segunda mirada independiente (subagente: recibió solo la madre nueva, las 9 fotos de `e0b/` y el prompt de cada escena; ni la hoja ni nada de `e0/`) — íntegra

#### 1) Foto madre `madre_daniel_ecija.png`
Hombre de ~22–26 años, retrato frontal tipo carnet, fondo gris-azulado liso con grano/rayas de foto vieja. Pelo castaño oscuro casi negro, corto, peinado hacia atrás/costado con flequillo apenas levantado. Cejas gruesas y oscuras, ojos marrones grandes, nariz recta, boca cerrada y seria, orejas algo salidas. **Sin barba**: solo sombra de afeitado leve en mentón y bigote. Expresión neutra/seria, mirada a cámara. **Ropa: camisa blanca-crema (blanco roto) de cuello abierto, sin corbata, limpia, sin manchas ni polvo.** Nada más visible (busto solo).

#### 2) Tabla

| foto | ¿es la escena pedida? | cara de la madre (1–10) | contagio (caras-madre de más) | ropa del protagonista | anacronismos |
|---|---|---|---|---|---|
| lote1/01_ch02_img_01 (baile 1961) | **Parcial**. Salón ornamentado con arañas, molduras doradas, parquet, parejas bailando, luz cálida: todo OK. Pero NO es plano abierto a altura de ojos: es plano medio-cerrado de la pareja en perfil (los bustos ocupan el cuadro). Ella trae un vestido/blusa crema lisa sin forma 1961, no «cotton-satin dress» hasta la rodilla. | **8** (de perfil: ceja gruesa, nariz recta, pelo oscuro peinado atrás, mentón; afeitado igual). Perfil dificulta la certeza plena. | 0 (los demás están desenfocados; ninguno con cara madre). | **La de la escena**: traje oscuro de solapa estrecha, camisa blanca, corbata negra. Correcto. | Ninguno visible. |
| lote1/02_ch02_img_02 (puerto 1962) | **Sí**. Transatlántico, grúas, muelle, multitud de emigrantes, carros de equipaje, maletas de cartón, mañana clara, ángulo bajo que enfatiza el barco. Él con traje y sombrero, ella con vestido claro y abrigo claro. | **De espaldas / 3/4 trasero**: solo se ve mejilla y oreja; rasgos insuficientes para juzgar. Pelo oscuro bajo el sombrero coincide. | 0 (multitud de fondo sin cara madre reconocible). | **La de la escena**: traje oscuro planchado + sombrero fedora. Correcto. | Ninguno; sombreros/maletas coherentes con los 60. |
| lote1/03_ch02_img_04 (cubierta 1962) | **Parcial**. Cubierta de paseo, mar, pasajeros desenfocados, luz suave de tarde, profundidad corta, ella bajo su brazo: OK. Pero es plano frontal (no 3/4) y el matrimonio mira a cámara en pose de retrato, no «caminando». | **10** – es la madre sin ninguna duda (misma ceja, ojos, nariz, boca, afeitado, peinado, mirada). | 0. | **Se parece a la madre**: camisa blanco-crema de cuello abierto, limpia. El prompt pide «shirtsleeves» así que es compatible con la escena, pero coincide exactamente con la camisa de la madre (mismo color, mismo cuello). | Ninguno. |
| lote1/04_ch02_img_05 (veranda Wittenoom) | **Sí** (con matiz). Casa de chapa acanalada + fibro, tierra roja, lámpara cálida, atardecer, plano desde el patio, dos parejas, hombres con camisas sucias, mujeres con vestidos de algodón. Matiz: las 4 personas posan sentadas mirando a cámara, no «comparten una velada». | **Dos candidatos**: hombre izquierdo **7** (ceja, nariz, boca, pelo muy parecidos; cara algo más redonda). Hombre derecho **5** (mismo pelo y cejas, nariz más ancha y piel más oscura). Sin zoom al original no puedo cerrar cuál es «el» protagonista. | **1** cara-madre de más: el segundo hombre es una variante clara del mismo rostro (contagio al «otro» marido). | **La de la escena**: camisa clara manchada de polvo/tierra marrón (ambos hombres). Correcto — pero la base es otra vez la camisa crema de la madre, ahora ensuciada. | Hombre derecho lleva **reloj de pulsera moderno (correa negra tipo deportiva)** en la muñeca izquierda. Lámpara de mesa eléctrica de pantalla: plausible pero el modelo luce contemporáneo. |
| lote1/05_ch03_img_16 (pista Wittenoom) | **Parcial / no**. Hay avión con hélice, pista oscura de relaves, casas de chapa, cañón y pluma de polvo, sol duro: OK. PERO el avión es **un jet ejecutivo bimotor tipo Gulfstream** (turbinas en cola, ventanillas ovales, escalera integrada) con una hélice pegada en el morro: híbrido absurdo, no «small propeller aircraft» de 1962. La pareja no está en primer plano desde ángulo bajo sino lejos y chica. | **5**: cara muy pequeña; pelo oscuro, cejas marcadas y complexión delgada compatibles, pero el rostro casi no tiene resolución; **parece tener gafas de sol** (sombra oscura en los ojos) lo que impide comparar. | 0. | **Mixta**: camisa clara (crema) con manchas marrones + pantalón oscuro. Compatible con «work shirt and trousers», pero otra vez la camisa de la madre. | **Jet ejecutivo** (anacronismo mayor, modelo ~1970s–2000s); posibles **gafas de sol**; las casas de chapa pintadas de azul claro con ventanas modernas en el borde derecho. |
| lote1/06_ch04_img_07 (hospital de noche) | **Parcial**. Hombre solo, noche, edificio bajo con una ventana iluminada, calle de relaves, cerros: OK. Pero es plano medio-cerrado frontal, no «wide shot from across the street»; el edificio es de dos plantas y cemento, no «low fibro-cement». | **9**: misma ceja, ojos, nariz, boca, afeitado, pelo; mirada hacia un lado, muy reconocible. | 0. | **La de la escena**: camisa clara MUY manchada de polvo/grasa (base crema igual a la madre, pero ensuciada). Correcto. | Lámpara fluorescente en la ventana superior (tubo blanco), plausible pero dudoso en Wittenoom 1963. Nada grave. |
| lote2/01_ch04_img_09 (bocamina tras la voladura) | **Sí**. Mineros de espaldas con cascos, portal de madera, paredes rojas, relaves, polvo que vela la luz, uno apartado en primer plano a la derecha. | **9–10**: es la madre de frente, sin duda (cejas, ojos, nariz, boca, afeitado, peinado). | 0 (todos los demás de espaldas o de perfil sin rasgos). | **Mixta**: camisa crema de cuello abierto (= madre, limpia bajo el mono) + **mono/overol de trabajo con tirantes** color tierra polvoriento encima. El mono es coherente con la escena; la camisa de abajo es la de la madre. | Los cascos son redondos tipo «salacot/casco de bombero» uniformes, aceptables. Ninguno moderno visible. |
| lote2/02_ch04_img_14 (familia a la pista, de espaldas) | **Parcial**. Familia de espaldas, pista de relaves oscura, avioneta de hélice (Cessna de ala alta, correcto para «small propeller aircraft»), maletas, cañón al fondo, sombras largas: OK. Pero NO es ángulo bajo (es a altura de ojos) y la mujer tiene **pelo negro largo suelto** (no coincide con la esposa de las otras fotos, recogida), vestido sin mangas con infante en brazos: bien. | **De espaldas**: imposible juzgar; pelo oscuro compatible. | 0. | **No la de la madre**: mono/overol gris-verdoso de una pieza (coherente con «work shirt» laxamente; más mono que camisa). | Avioneta Cessna de ala alta con ruedas carenadas: modelo ~1970s+ pero tolerable. Zapatillas/calzado claro de él poco definido. Mujer con pelo largo suelto estilo contemporáneo. |
| lote2/03_ch05_img_05 (Madrid 1966, de espaldas) | **Sí**. Familia de espaldas entrando por el portal de un bloque de ladrillo con balcones de hierro, calle estrecha, cielo nublado, visto desde enfrente. Él con chaqueta oscura y pantalón, ella con blusa clara y falda negra, niño de la mano. | **De espaldas**: no juzgable. | 0. | **La de la escena**: chaqueta oscura tipo cazadora + pantalón oscuro (no se ve camisa). Correcto. | **Caja/aparato gris en la fachada (parece timbre/portero o cámara/alarma moderna)** sobre la puerta; **buzón metálico moderno** a la izquierda del portal; rejas y ventanas lucen contemporáneas; calle asfaltada muy limpia con cordones modernos. El niño con **sudadera gris de capucha/cuello redondo y zapatillas** (anacrónico para 1966). |

#### 3) Conclusiones
**(a) Consistencia de identidad**: muy alta en las fotos donde la cara se ve de frente (03, 06, lote2/01 = 9–10; 01 de perfil 8). Donde la cara es pequeña (05) o de espaldas (02, lote2/02, lote2/03) no se puede verificar; en 04 la identidad se duplica en los dos hombres, con el izquierdo como mejor candidato. La «esposa» no es consistente entre fotos (recogido castaño en 01–04, pelo negro largo suelto en lote2/02).

**(b) Arrastre de la ropa de la madre**: sí, claro. La camisa crema de cuello abierto de la madre aparece como base en 03 (idéntica, limpia), 04, 05, 06 (ensuciada con polvo) y lote2/01 (debajo del mono). Solo se rompe cuando el prompt impone prenda fuerte y distinta: traje (01, 02), mono (lote2/02), chaqueta (lote2/03). Como para las escenas de mina «work shirt» ≈ camisa clara sucia, el arrastre es tolerable ahí; en 03 (cubierta) el modelo directamente copió la camisa de la madre.

**(c) Rarezas**: 05 es el problema serio: **jet ejecutivo con hélice pegada**, pareja chiquita y con gafas de sol aparentes. 04: **reloj moderno** en el segundo hombre + duplicación de la cara. lote2/03: fachada con **caja/cámara y buzón modernos**, niño con **sudadera y zapatillas**. No vi texto legible, carteles ni miembros extra en ninguna de las 9. Varias fotos (03, 04, 06) tienen pose «retrato mirando a cámara» en vez de la acción pedida, y los planos «wide» salen como plano medio (01, 03, 06).

**Nota de CC sobre la segunda mirada:** coincide con la mía en identidad (9–10 de frente), contagio (solo ch02_img_05, 1 cara) y en que la camisa clara de la madre sigue de base cuando la escena no impone otra prenda; difiere en que el subagente marca como «parcial» los planos que salieron más cerrados que el «wide» pedido (ch02_img_01, ch02_img_04, ch04_img_07) y las poses de retrato; yo lo di por escena cumplida con matiz. Lo del avión (ch03_img_16) lo vimos los dos.

## 0b.4 Comparación con la Etapa 0 en las 3 fotos repetidas (lote 2)

| foto | Etapa 0 (madre con camisa manchada) | Etapa 0b (madre con camisa limpia) | ¿desapareció el arrastre de las manchas? |
|---|---|---|---|
| ch04_img_09 | 8 mineros en fila **todos de frente**, nadie aparte; madre en el 7.º y parecido en el 6.º (contagio 2); camisa manchada de la madre | mineros **de espaldas**, Daniel **aparte** de frente; contagio 0; mameluco de trabajo sucio con la camisa clara limpia abajo | **sí** (la suciedad que hay es la del mameluco que pide la escena, no la mancha de la madre) |
| ch04_img_14 | familia de espaldas; el hombre con la camisa manchada de la madre | familia de espaldas; mameluco gris de trabajo sin manchas marcadas | **sí** |
| ch05_img_05 | familia de espaldas; el hombre con la camisa manchada en Madrid 1966 | el hombre con chaqueta oscura y pantalón (lo que pide la escena) | **sí** |

Lectura: con la madre limpia el modelo pone la ropa que dice cada escena (traje, sombrero, mameluco, chaqueta) y solo deja la camisa de la madre cuando la escena pide «shirtsleeves» o la deja asomar bajo el mameluco. El cambio de composición en ch04_img_09 (de espaldas / aparte) puede ser también efecto de la seed; no se puede atribuir solo a la ropa.

## 0b.5 Hoja

`e0b/hoja_madre_0b.jpg` (fuera de git): madre 0b arriba a la izquierda y la madre de la Etapa 0 al lado; por fila foto 0b | foto de la Etapa 0 del mismo slot. Solo tienen par las 3 de `e0/lote2/`; las 6 del lote 1 llevan la celda derecha vacía con la leyenda «sin foto de la Etapa 0: el lote 1 se cortó».

## 0b.6 Gasto total (precio real de fal, GET `api.fal.ai/v1/models/pricing`, 0,035 US$/imagen en los dos endpoints × devueltas)

| endpoint | qué | imágenes | US$ |
|---|---|---|---|
| `fal-ai/bytedance/seedream/v5/lite/text-to-image` | madre | 1 | 0,035 |
| `fal-ai/bytedance/seedream/v5/lite/edit` | lote 1 | 6 | 0,21 |
| `fal-ai/bytedance/seedream/v5/lite/edit` | lote 2 | 3 | 0,105 |
| **total Etapa 0b** | | 10 | **0,35** |

(Etapa 0: 0,14 confirmado + 0,21 probable del lote cortado; queda como está, no se intentó recuperar.)

## Lo que queda abierto (Etapa 0b)

1. **`has_nsfw_concepts` no viene** en la respuesta de v5 Lite (ni en t2i ni en `/edit`): se reporta `None`. Si hace falta ese dato, hay que mirar qué devuelve el schema de salida (en la Etapa 0 tampoco vino).
2. **Anacronismo del avión en ch03_img_16** (jet ejecutivo con hélice en la nariz): error del modelo frente a «small propeller aircraft»; en ch04_img_14 la avioneta sí salió bien. Es tema del prompt/escena, no de la madre.
3. **Contagio débil en ch02_img_05** (el segundo hombre se parece a la madre): con dos parejas en escena el modelo tiende a reutilizar la cara. En la Etapa 0 el contagio fue más fuerte (2–3 caras de 8).
4. **La camisa de la madre asoma** bajo el mameluco en ch04_img_09 y es la camisa de ch02_img_04 («shirtsleeves»): es compatible con las escenas, pero muestra que la ropa de la madre sigue entrando cuando la escena no la pisa.
5. **Composición de ch04_img_09:** esta vez el modelo respetó «mostly seen from behind» y «standing apart»; no se sabe si fue la ropa limpia, la seed o azar (una corrida).
6. **Detalles modernos en ch05_img_05** (aparato en la fachada, buzón, buzo con capucha del nene): leves, pero son del tipo que Omar marca.
7. **ch04_img_07:** el hospital salió de 2 plantas de revoque en vez de «low fibro-cement building»; la escena se entiende igual.
8. El gasto probable de US$ 0,21 del lote cortado de la Etapa 0 sigue sin confirmar (no se intentó recuperar: fue síncrono, sin `request_id`).
9. Sigue pendiente de la Etapa B.1 sacar «miner» del canon sin lista de palabras (PARÁ previo).
