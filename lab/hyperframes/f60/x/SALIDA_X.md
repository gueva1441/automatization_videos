# F60 Etapa X — 3 fotos de la Etapa 0b regeneradas con el anacronismo corregido en el prompt

Fecha: 2026-10-30 · solo lab (`lab/hyperframes/f60/x/`), ningún .py de producción tocado · madre: `lab/hyperframes/f60/e0b/madre_daniel_ecija.png` (md5 41e8c58c…, la misma de 0b) · modelo `fal-ai/bytedance/seedream/v5/lite/edit` por la cola (queue.fal.run), image_size 2560×1440, `num_images: 1`, `enable_safety_checker: true`, sin `max_images` ni secuencia (3 llamadas sueltas) · espera con `asset_manager._clip_poll` (no existe todavía `_fal_queue_poll`) · pedidos en `pedidos_x.json` antes de esperar · detalle en `etapa_x.json`, hoja `hoja_x.jpg` (fila = 0b | X), runner `etapa_x.py`.

Fuentes consultadas sin resultado para el nombre concreto: `data/scripts/_steps/123bbb64-…/ficha_caso.json` y el `research_summary` del topic solo dicen «avión pequeño de hélices» (Víctor Calvo, Q15); no nombran reloj ni buzón. Los nombres salieron de la web (URLs abajo).

## 1. ch03_img_16 — avión (Wittenoom, 1962)

- **Anacronismo en 0b** (`e0b/lote1/05_ch03_img_16.png`): un **jet ejecutivo bimotor tipo Gulfstream** (turbinas en la cola, ventanillas ovales, escalera integrada) con una hélice pegada en el morro; la pareja chica y lejos, con aparentes gafas de sol.
- **Frase ANTES → DESPUÉS** (sustitución, resto del prompt byte a byte igual):
  - ANTES: `Stepping down from a small propeller aircraft onto the airstrip.`
  - DESPUÉS: `Stepping down from a twin-engine Douglas DC-3 propeller airliner, tail wheel resting on the strip, onto the airstrip.`
- **Fuente del nombre**: State Library of WA, foto 146072PD «MMA DC3 VH-MMD named RMA Durack on the ground at Wittenoom Gorge Airport, 1961» — https://slwa.wa.gov.au/media/1916 (y https://purl.slwa.wa.gov.au/slwa_b4232624). MMA operó DC-3 de 1945 a 1970 (https://en.wikipedia.org/wiki/MacRobertson_Miller_Airlines); el servicio aéreo a Wittenoom lo abrió MMA desde Port Hedland (https://en.wikipedia.org/wiki/Wittenoom_Gorge_Airport). No puse el nombre de la aerolínea en el prompt para no provocar texto/librea legible.
- **Foto X** (`x_ch03_img_16.png`, 48,5 s): **el anacronismo se fue**. Avión bimotor de hélices con fuselaje metálico, rueda de cola apoyada en la pista, ventanillas cuadradas, escalerilla corta: un DC-3 reconocible. Pista de relaves gris-azulada, casas bajas de chapa, pluma de polvo sobre el cañón, sol duro. Pareja ahora más cerca y sin gafas de sol; la mujer en vestido claro de algodón. Reparo menor: el plano sigue siendo a altura de ojos más que «low angle»; el avión en tres cuartos frontal (plausible).
- **Cara de Daniel vs. madre**: **6/10**. Pelo oscuro corto, cejas marcadas, cara delgada, camisa clara (la de la madre) compatibles; la cara es pequeña en el cuadro y está en sombra, poca resolución para cerrar más.

## 2. ch02_img_05 — reloj (veranda de Wittenoom, 1962)

- **Anacronismo en 0b** (`e0b/lote1/04_ch02_img_05.png`): el hombre de la derecha lleva un **reloj de pulsera moderno con correa negra tipo deportiva/digital** en la muñeca izquierda. El prompt no nombraba ningún reloj.
- **Frase ANTES → DESPUÉS** (agregado tras «the women in modest cotton dresses.»):
  - ANTES: `the women in modest cotton dresses.`
  - DESPUÉS: `the women in modest cotton dresses. One of the men wears a small round early-1960s steel wristwatch with a plain pale dial on a thin brown leather strap.`
- **Fuente del nombre**: relojes de caballero de 1962 de caja redonda de acero 33–34 mm con correa de cuero, p. ej. Omega Seamaster ref. 14759 SC 61 (1962) — https://awco.nl/shop/archive/a-omega/omega-seamaster-1962/ y https://www.catawiki.com/en/l/104390016-omega-seamaster-serviced-14770-sc-61-men-1962. No puse la marca en el prompt (no hay dato de qué reloj tenían los Écija; la ficha no lo trae), solo la forma de época: caja redonda chica, esfera clara, correa de cuero fina.
- **Foto X** (`x_ch02_img_05.png`, 49,0 s): **el anacronismo se fue**. El hombre de la izquierda lleva un reloj redondo chico, caja dorada/acero y esfera clara, **correa de cuero marrón fina**: coherente con 1962. Se mantienen veranda de chapa y fibro, tierra roja, lámpara cálida (ahora colgante de techo), dos parejas, hombres con camisas de trabajo manchadas de polvo, mujeres con vestidos claros. Reparos que no eran el objetivo: siguen posando sentados mirando a cámara (no «comparten una velada»); las dos mujeres tienen el pelo largo suelto (en 0b recogido); el hombre de la derecha vuelve a ser una variante de la cara de la madre (contagio, como en 0b).
- **Cara de Daniel vs. madre**: hombre de la izquierda **7/10** (cejas, nariz, boca, pelo; cara algo más alargada y ojerosa); hombre de la derecha **6/10** (misma cara con rasgos más marcados). Sigue sin ser claro cuál de los dos es «el» protagonista.

## 3. ch05_img_05 — buzón / aparato en la fachada (Madrid, 1966)

- **Anacronismo en 0b** (`e0b/lote2/03_ch05_img_05.png`): **buzón metálico moderno de acero** a la izquierda del portal y **caja gris cuadrada (portero/cámara/alarma)** sobre la puerta; de regalo, el niño con sudadera gris con capucha y zapatillas. El prompt no nombraba ningún objeto de la fachada.
- **Frase ANTES → DESPUÉS** (agregado tras «entering their home.»):
  - ANTES: `entering their home.`
  - DESPUÉS: `entering their home. Beside the doorway only a small brass letter slot set into the wooden street door and a round brass bell push, as in 1960s Madrid; no electronic intercom panel, no camera and no metal mailbox on the facade.`
- **Fuente del nombre**: en los portales españoles de los 60 el contacto con los vecinos lo hacía un portero físico; el portero electrónico de Fermax (primero diseñado en España) llega a principios de los 70 — https://valenciaplaza.com/fermax-70-anos-porteros-automaticos. Los buzones metálicos de chapa de la época eran «frontales individuales» para colocar en grupos (dentro del portal), patente ES83757U de 1960 — https://patents.google.com/patent/ES83757U/es ; en la calle, lo visible era la boca de cartas de latón de la puerta y el pulsador de latón. No encontré una foto de catálogo del buzón concreto de un bloque madrileño de 1966: lo declaro como «objeto de época por inferencia de estas dos fuentes», no como modelo documentado.
- **Foto X** (`x_ch05_img_05.png`, 48,6 s): **el anacronismo se fue**. Puerta de madera maciza con **boca de cartas de latón** y **pulsador redondo de latón**; **sin buzón metálico, sin caja gris, sin cámara**. Bloque de ladrillo con balcones de hierro, zócalo de granito, luz nublada, familia de espaldas entrando. De regalo, el niño ahora lleva **jersey marrón de punto** (la sudadera con capucha desapareció sola). Reparo nuevo: hay una **hoja de papel pegada** en el marco interior de la puerta (parece un aviso; no leo texto legible a este tamaño, pero es un riesgo de NO_TEXT a vigilar); él en cazadora gris-verdosa tipo años 60 y ella en blusa clara y falda, correcto.
- **Cara de Daniel vs. madre**: **de espaldas**, no juzgable; nuca con pelo negro corto y cuerpo delgado compatibles.

## Cierre

- Costo total: **US$ 0,105** (3 × 0,035, precio real de fal para `/edit`), tiempo 48,5 + 49,0 + 48,6 s en serie.
- Semilla: **Seedream v5 Lite `/edit` no acepta `seed` de entrada**, así que no se pudo reusar la semilla de los lotes de 0b; cada foto X es una tirada nueva (seeds devueltas 386697505 / 466224935 / 182242202). Por eso cambian también cosas que el prompt no tocó (pelo de las mujeres, lámpara, encuadre): la comparación es «prompt corregido» contra «prompt original», no «misma semilla con una frase distinta».
- Los 3 anacronismos pedidos se fueron (3/3). Lo demás que ya estaba reportado en 0b y no era el objetivo (pose de retrato en la veranda, contagio de la cara al segundo hombre, ángulo no bajo en la pista) sigue igual.
