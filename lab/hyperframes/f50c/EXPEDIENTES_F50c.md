# EXPEDIENTES_F50c — personas, citas y grupos en el pedido de foto (Wittenoom, en seco)

Salida de `python lab/hyperframes/f50c/expedientes_f50c.py`. Los pedidos de casilleros de los 7 caps salen del código de producción con la llamada a Opus cortada antes de salir. «antes» es el expediente de F50b (`1ecf045`) y «después» el de F50c. Las anclas son las del papel de F50b. Cero modelos, cero fal.

## Verificación automática

| | resultado | esperado |
|---|---:|---:|
| con_people | 73 | 73 |
| ancla | 35 | 35 |
| arrastre | 38 | 38 |
| ambiguas | 0 | 0 |
| con_quotes | 84 | 84 |
| grupos | 7 | 7 |
| fotos con PEOPLE antes | 17 | 17 |
| 1 / 2 / 3 personas | 48 / 23 / 2 | 48 / 23 / 2 |
| citas sin autor | 0 | 0 |
| caps con diff fuera de PEOPLE/QUOTES/PEOPLE GROUPS | 0 | 0 |

**Fotos testigo**

| foto | ancla | personas | fuente | ok |
|---|---|---|---|---|
| 1/3 | «El hombre se llama Daniel Écija y es minero. Vino de Madrid.» | Daniel Écija (padre) | ancla | sí |
| 1/4 | «Wittenoom, Australia Occidental, mil novecientos sesenta y dos.» | Daniel Écija (padre) | arrastre | sí |
| 2/1 | «Dieciséis de septiembre de mil novecientos sesenta y uno. En el salón » | Daniel Écija (padre), María Bernal | ancla | sí |
| 2/8 | «Víctor Calvo era un niño cuando subió a ese barco. «Salimos de Málaga » | Víctor Calvo | ancla | sí |
| 3/7 | «Lo que pasó con la carta lo contó él mismo: «Me desestimaron y, de hec» | Eric Saint | arrastre | sí |
| 3/16 | ««porque estaban acostumbrados; lo esperaban», dijo McNulty. En mil nov» | Jim McNulty | ancla | sí |
| 5/9 | «El agente abre el documento de Daniel Écija hijo, lee el lugar de naci» | Daniel Écija (hijo) | ancla | sí |
| 5/14 | «Madrid, mil novecientos noventa y uno. Daniel Écija va al médico. Le h» | Daniel Écija (padre) | ancla | sí |

**Beats:** `assign_beats` de producción da los mismos beats que los guardados en los 7 caps.

**Resultado: PASA**


## PEOPLE GROUPS (después, igual en los 7 caps)

- `- wittenoom_miners_and_mill_workers: Various European migrant and Australian laborers working in the asbestos mines and processing mill. · Wittenoom, from 1937 to 1966. · APPEARANCE: Physically robust individuals, often appearing fatigued and covered in a pervasive fine dust, with diverse European features. · CLOTHING: Rugged, practical work clothes, heavy-duty trousers and shirts, sometimes with hard hats, all visibly stained and impregnated with asbestos dust.`
- `- spanish_migrant_families: Spanish families who migrated to Wittenoom under government schemes. · Wittenoom, primarily 1958-1966. · APPEARANCE: Adults and children of Southern European descent, appearing resilient and resourceful, adapting to a harsh desert environment, often showing signs of physical strain or everyday weariness. · CLOTHING: Simple, light clothing suitable for a hot, dusty climate; women in plain dresses or skirts/blouses, men in casual shirts and trousers, children in basic playwear, all often soiled with red earth and dust.`
- `- australian_public_health_officials: Doctors, inspectors, and hygienists from Australian public health departments. · Wittenoom and state offices, 1944-1966. · APPEARANCE: Predominantly Caucasian, appearing professional, often with a serious or concerned demeanor due to the health risks. · CLOTHING: Formal or semi-formal attire of the era, such as suits, collared shirts, and ties, or clean uniforms for medical staff.`
- `- australian_government_representatives: Various Australian federal and state government officials, including politicians, committee members, and regulators. · Government offices and occasional visits to Wittenoom, 1940s-2020s. · APPEARANCE: Predominantly Caucasian, appearing authoritative and formal, reflecting their political or administrative roles. · CLOTHING: Formal business attire, including suits and ties, typical of Australian politicians and civil servants of the respective decades.`
- `- csr_corporate_personnel: Executives, managers, and other personnel from Colonial Sugar Refining (CSR) and its subsidiary, Australian Blue Asbestos (ABA). · Corporate offices and Wittenoom, 1937-1966. · APPEARANCE: Predominantly Caucasian, appearing well-dressed and corporate, often with an air of authority, sometimes dismissive of worker concerns. · CLOTHING: Business suits and formal wear, reflecting their executive or managerial positions, often clean and sharp in contrast to the dusty environment.`
- `- banjima_traditional_owners_and_advocates: Indigenous Banjima people, including elders and legal advocates, asserting their rights over contaminated lands. · Wittenoom area and legal forums, 2010s-2020s. · APPEARANCE: Indigenous Australian people, often older, appearing resilient and determined, some bearing the visible or implied health consequences of asbestos exposure. · CLOTHING: Practical, contemporary casual clothing suitable for the Australian climate and for meetings or public appearances.`
- `- australian_airport_police: Law enforcement personnel working in Australian airports. · Australian airport checkpoint, 1985. · APPEARANCE: Predominantly Caucasian, appearing uniformed and professional. · CLOTHING: Standard police uniform of the mid-1980s, typically including a collared shirt, trousers, and a peaked cap.`

## Por foto: PEOPLE y QUOTES, antes → después

### Cap 1 · foto 1

- Ancla: «con el pie envuelto en una venda blanca»
- PEOPLE antes: -
- PEOPLE después: -
- QUOTES antes: -
- QUOTES después: -

### Cap 1 · foto 2

- Ancla: «En el retrato de familia todos miran a cámara menos el pie: está vendado, y la herida que le hizo un trozo de amianto no cierra.»
- PEOPLE antes: -
- PEOPLE después: -
- QUOTES antes: -
- QUOTES después: -

### Cap 1 · foto 3 — ancla

- Ancla: «El hombre se llama Daniel Écija y es minero. Vino de Madrid.»
- PEOPLE antes: -
- PEOPLE después: Minero español, esposo de María Bernal; murió de mesotelioma después de abandonar Wittenoom · Wittenoom · 1962, 1963 (Daniel Écija (padre))
- QUOTES antes: -
- QUOTES después: -

### Cap 1 · foto 4 — arrastre

- Ancla: «Wittenoom, Australia Occidental, mil novecientos sesenta y dos.»
- PEOPLE antes: -
- PEOPLE después: Minero español, esposo de María Bernal; murió de mesotelioma después de abandonar Wittenoom · Wittenoom · 1962, 1963 (named earlier in the paragraph) (Daniel Écija (padre))
- QUOTES antes: -
- QUOTES después: -

### Cap 1 · foto 5 — arrastre

- Ancla: «Para entender ese pie hay que volver a un baile en Madrid, un año antes de la foto.»
- PEOPLE antes: -
- PEOPLE después: Minero español, esposo de María Bernal; murió de mesotelioma después de abandonar Wittenoom · Wittenoom · 1962, 1963 (named earlier in the paragraph) (Daniel Écija (padre))
- QUOTES antes: -
- QUOTES después: -

### Cap 2 · foto 1 — ancla

- Ancla: «Dieciséis de septiembre de mil novecientos sesenta y uno. En el salón de baile del Círculo de Bellas Artes de Madrid, Daniel Écija conoce a María Bernal.»
- PEOPLE antes: Esposa del minero Daniel Écija y residente de Wittenoom · Wittenoom · 1962, 1963
- PEOPLE después: Minero español, esposo de María Bernal; murió de mesotelioma después de abandonar Wittenoom · Wittenoom · 1962, 1963; Esposa del minero Daniel Écija, madre de Daniel y Arantxa; emigrante y residente de Wittenoom · Wittenoom · 1962, 1963 (Daniel Écija (padre), María Bernal)
- QUOTES antes: «Iba pegadita a mi marido, como una niña. Pero estaba orgullosa. Me había enamorado de aquel hombre y confiaba en el futuro…, aunque estuviera tan lejos. En España no teníamos nada ninguno de los dos.» | «Conocimos allí a otro matrimonio de Madrid. Milagros y Ramón. Enseguida nos hicimos íntimos amigos.»
- QUOTES después: «Iba pegadita a mi marido, como una niña. Pero estaba orgullosa. Me había enamorado de aquel hombre y confiaba en el futuro…, aunque estuviera tan lejos. En España no teníamos nada ninguno de los dos.» — María Bernal · Residente de Wittenoom y esposa de minero · witness | «Conocimos allí a otro matrimonio de Madrid. Milagros y Ramón. Enseguida nos hicimos íntimos amigos.» — María Bernal · Residente de Wittenoom y esposa de minero · witness

### Cap 2 · foto 2 — arrastre

- Ancla: «Un año después se casan: el jueves veinte de septiembre de mil novecientos sesenta y dos.»
- PEOPLE antes: -
- PEOPLE después: Minero español, esposo de María Bernal; murió de mesotelioma después de abandonar Wittenoom · Wittenoom · 1962, 1963 (named earlier in the paragraph); Esposa del minero Daniel Écija, madre de Daniel y Arantxa; emigrante y residente de Wittenoom · Wittenoom · 1962, 1963 (named earlier in the paragraph) (Daniel Écija (padre), María Bernal)
- QUOTES antes: «Iba pegadita a mi marido, como una niña. Pero estaba orgullosa. Me había enamorado de aquel hombre y confiaba en el futuro…, aunque estuviera tan lejos. En España no teníamos nada ninguno de los dos.» | «Conocimos allí a otro matrimonio de Madrid. Milagros y Ramón. Enseguida nos hicimos íntimos amigos.»
- QUOTES después: «Iba pegadita a mi marido, como una niña. Pero estaba orgullosa. Me había enamorado de aquel hombre y confiaba en el futuro…, aunque estuviera tan lejos. En España no teníamos nada ninguno de los dos.» — María Bernal · Residente de Wittenoom y esposa de minero · witness | «Conocimos allí a otro matrimonio de Madrid. Milagros y Ramón. Enseguida nos hicimos íntimos amigos.» — María Bernal · Residente de Wittenoom y esposa de minero · witness

### Cap 2 · foto 3 — arrastre

- Ancla: «Cuatro días más tarde ya están en el barco. Van a Australia con el acuerdo migratorio por el que pasaron cerca de ocho mil españoles.»
- PEOPLE antes: -
- PEOPLE después: Minero español, esposo de María Bernal; murió de mesotelioma después de abandonar Wittenoom · Wittenoom · 1962, 1963 (named earlier in the paragraph); Esposa del minero Daniel Écija, madre de Daniel y Arantxa; emigrante y residente de Wittenoom · Wittenoom · 1962, 1963 (named earlier in the paragraph) (Daniel Écija (padre), María Bernal)
- QUOTES antes: «Iba pegadita a mi marido, como una niña. Pero estaba orgullosa. Me había enamorado de aquel hombre y confiaba en el futuro…, aunque estuviera tan lejos. En España no teníamos nada ninguno de los dos.» | «Conocimos allí a otro matrimonio de Madrid. Milagros y Ramón. Enseguida nos hicimos íntimos amigos.»
- QUOTES después: «Iba pegadita a mi marido, como una niña. Pero estaba orgullosa. Me había enamorado de aquel hombre y confiaba en el futuro…, aunque estuviera tan lejos. En España no teníamos nada ninguno de los dos.» — María Bernal · Residente de Wittenoom y esposa de minero · witness | «Conocimos allí a otro matrimonio de Madrid. Milagros y Ramón. Enseguida nos hicimos íntimos amigos.» — María Bernal · Residente de Wittenoom y esposa de minero · witness

### Cap 2 · foto 4 — arrastre

- Ancla: «De Wittenoom no saben nada; saben que hay trabajo y que van juntos.»
- PEOPLE antes: -
- PEOPLE después: Minero español, esposo de María Bernal; murió de mesotelioma después de abandonar Wittenoom · Wittenoom · 1962, 1963 (named earlier in the paragraph); Esposa del minero Daniel Écija, madre de Daniel y Arantxa; emigrante y residente de Wittenoom · Wittenoom · 1962, 1963 (named earlier in the paragraph) (Daniel Écija (padre), María Bernal)
- QUOTES antes: «Iba pegadita a mi marido, como una niña. Pero estaba orgullosa. Me había enamorado de aquel hombre y confiaba en el futuro…, aunque estuviera tan lejos. En España no teníamos nada ninguno de los dos.» | «Conocimos allí a otro matrimonio de Madrid. Milagros y Ramón. Enseguida nos hicimos íntimos amigos.»
- QUOTES después: «Iba pegadita a mi marido, como una niña. Pero estaba orgullosa. Me había enamorado de aquel hombre y confiaba en el futuro…, aunque estuviera tan lejos. En España no teníamos nada ninguno de los dos.» — María Bernal · Residente de Wittenoom y esposa de minero · witness | «Conocimos allí a otro matrimonio de Madrid. Milagros y Ramón. Enseguida nos hicimos íntimos amigos.» — María Bernal · Residente de Wittenoom y esposa de minero · witness

### Cap 2 · foto 5 — arrastre

- Ancla: ««Iba pegadita a mi marido, como una niña», recuerda su mujer.»
- PEOPLE antes: -
- PEOPLE después: Minero español, esposo de María Bernal; murió de mesotelioma después de abandonar Wittenoom · Wittenoom · 1962, 1963 (named earlier in the paragraph); Esposa del minero Daniel Écija, madre de Daniel y Arantxa; emigrante y residente de Wittenoom · Wittenoom · 1962, 1963 (named earlier in the paragraph) (Daniel Écija (padre), María Bernal)
- QUOTES antes: «Iba pegadita a mi marido, como una niña. Pero estaba orgullosa. Me había enamorado de aquel hombre y confiaba en el futuro…, aunque estuviera tan lejos. En España no teníamos nada ninguno de los dos.» | «Conocimos allí a otro matrimonio de Madrid. Milagros y Ramón. Enseguida nos hicimos íntimos amigos.»
- QUOTES después: «Iba pegadita a mi marido, como una niña. Pero estaba orgullosa. Me había enamorado de aquel hombre y confiaba en el futuro…, aunque estuviera tan lejos. En España no teníamos nada ninguno de los dos.» — María Bernal · Residente de Wittenoom y esposa de minero · witness | «Conocimos allí a otro matrimonio de Madrid. Milagros y Ramón. Enseguida nos hicimos íntimos amigos.» — María Bernal · Residente de Wittenoom y esposa de minero · witness

### Cap 2 · foto 6 — ancla

- Ancla: «Con el tiempo se hicieron amigos íntimos de otra pareja, Milagros Barroso y Ramón de Juan. Esa familia madrileña había hecho el mismo viaje un mes antes.»
- PEOPLE antes: Esposa del minero Ramón de Juan y residente de Wittenoom · Wittenoom · 1962, 1963, 1964; Minero español en Wittenoom · Wittenoom · 1962, 1963, 1964
- PEOPLE después: Esposa de Ramón de Juan, madre de Víctor Calvo y residente de Wittenoom · Wittenoom · 1962, 1963, 1964; Minero español, esposo de Milagros Barroso y amigo de Daniel Écija · Wittenoom · 1962, 1963, 1964 (Milagros Barroso, Ramón de Juan)
- QUOTES antes: «Iba pegadita a mi marido, como una niña. Pero estaba orgullosa. Me había enamorado de aquel hombre y confiaba en el futuro…, aunque estuviera tan lejos. En España no teníamos nada ninguno de los dos.» | «Conocimos allí a otro matrimonio de Madrid. Milagros y Ramón. Enseguida nos hicimos íntimos amigos.»
- QUOTES después: «Iba pegadita a mi marido, como una niña. Pero estaba orgullosa. Me había enamorado de aquel hombre y confiaba en el futuro…, aunque estuviera tan lejos. En España no teníamos nada ninguno de los dos.» — María Bernal · Residente de Wittenoom y esposa de minero · witness | «Conocimos allí a otro matrimonio de Madrid. Milagros y Ramón. Enseguida nos hicimos íntimos amigos.» — María Bernal · Residente de Wittenoom y esposa de minero · witness

### Cap 2 · foto 7 — arrastre

- Ancla: «Un niño que hizo ese viaje todavía recuerda el calor.»
- PEOPLE antes: -
- PEOPLE después: Esposa de Ramón de Juan, madre de Víctor Calvo y residente de Wittenoom · Wittenoom · 1962, 1963, 1964 (named earlier in the paragraph); Minero español, esposo de Milagros Barroso y amigo de Daniel Écija · Wittenoom · 1962, 1963, 1964 (named earlier in the paragraph) (Milagros Barroso, Ramón de Juan)
- QUOTES antes: «Iba pegadita a mi marido, como una niña. Pero estaba orgullosa. Me había enamorado de aquel hombre y confiaba en el futuro…, aunque estuviera tan lejos. En España no teníamos nada ninguno de los dos.» | «Conocimos allí a otro matrimonio de Madrid. Milagros y Ramón. Enseguida nos hicimos íntimos amigos.»
- QUOTES después: «Iba pegadita a mi marido, como una niña. Pero estaba orgullosa. Me había enamorado de aquel hombre y confiaba en el futuro…, aunque estuviera tan lejos. En España no teníamos nada ninguno de los dos.» — María Bernal · Residente de Wittenoom y esposa de minero · witness | «Conocimos allí a otro matrimonio de Madrid. Milagros y Ramón. Enseguida nos hicimos íntimos amigos.» — María Bernal · Residente de Wittenoom y esposa de minero · witness

### Cap 2 · foto 8 — ancla

- Ancla: «Víctor Calvo era un niño cuando subió a ese barco. «Salimos de Málaga y tardamos más de 20 días en llegar en barco a Australia», dice Calvo.»
- PEOPLE antes: Hijo de Milagros Barroso, vivió en Wittenoom de niño · Wittenoom · 1962, 1963, 1964
- PEOPLE después: Hijo de Milagros Barroso e hijastro de Ramón de Juan; llegó a Wittenoom de niño y testimonia sobre la exposición infantil · Wittenoom · 1962, 1963, 1964 (Víctor Calvo)
- QUOTES antes: «Salimos de Málaga y tardamos más de 20 días en llegar en barco a Australia. Pasamos por el canal de Suez… Puf, el calor que hacía allí. Recuerdo los mareos. La incertidumbre. Aquella sensación de no saber muy bien adónde íbamos ni cómo viviríamos.» | «El avión era pequeño, de hélices, y se movía muchísimo. Aterrizamos en una pista en medio de una tierra muy muy roja. Había polvo por todas partes. Nunca había visto tanto polvo. Nos llevaron a las casas, de chapa, madera y uralita.»
- QUOTES después: «Salimos de Málaga y tardamos más de 20 días en llegar en barco a Australia. Pasamos por el canal de Suez… Puf, el calor que hacía allí. Recuerdo los mareos. La incertidumbre. Aquella sensación de no saber muy bien adónde íbamos ni cómo viviríamos.» — Víctor Calvo · Residente de Wittenoom de niño, hijastro de minero · witness | «El avión era pequeño, de hélices, y se movía muchísimo. Aterrizamos en una pista en medio de una tierra muy muy roja. Había polvo por todas partes. Nunca había visto tanto polvo. Nos llevaron a las casas, de chapa, madera y uralita.» — Víctor Calvo · Residente de Wittenoom de niño, hijastro de minero · witness

### Cap 2 · foto 9 — arrastre

- Ancla: «Recuerda el canal de Suez y el calor que hacía ahí, un calor que todavía lo hace resoplar cuando lo cuenta.»
- PEOPLE antes: -
- PEOPLE después: Hijo de Milagros Barroso e hijastro de Ramón de Juan; llegó a Wittenoom de niño y testimonia sobre la exposición infantil · Wittenoom · 1962, 1963, 1964 (named earlier in the paragraph) (Víctor Calvo)
- QUOTES antes: «Salimos de Málaga y tardamos más de 20 días en llegar en barco a Australia. Pasamos por el canal de Suez… Puf, el calor que hacía allí. Recuerdo los mareos. La incertidumbre. Aquella sensación de no saber muy bien adónde íbamos ni cómo viviríamos.» | «El avión era pequeño, de hélices, y se movía muchísimo. Aterrizamos en una pista en medio de una tierra muy muy roja. Había polvo por todas partes. Nunca había visto tanto polvo. Nos llevaron a las casas, de chapa, madera y uralita.»
- QUOTES después: «Salimos de Málaga y tardamos más de 20 días en llegar en barco a Australia. Pasamos por el canal de Suez… Puf, el calor que hacía allí. Recuerdo los mareos. La incertidumbre. Aquella sensación de no saber muy bien adónde íbamos ni cómo viviríamos.» — Víctor Calvo · Residente de Wittenoom de niño, hijastro de minero · witness | «El avión era pequeño, de hélices, y se movía muchísimo. Aterrizamos en una pista en medio de una tierra muy muy roja. Había polvo por todas partes. Nunca había visto tanto polvo. Nos llevaron a las casas, de chapa, madera y uralita.» — Víctor Calvo · Residente de Wittenoom de niño, hijastro de minero · witness

### Cap 2 · foto 10 — arrastre

- Ancla: «Recuerda los mareos. Y la incertidumbre: no saber muy bien adónde iban ni cómo iban a vivir.»
- PEOPLE antes: -
- PEOPLE después: Hijo de Milagros Barroso e hijastro de Ramón de Juan; llegó a Wittenoom de niño y testimonia sobre la exposición infantil · Wittenoom · 1962, 1963, 1964 (named earlier in the paragraph) (Víctor Calvo)
- QUOTES antes: «Salimos de Málaga y tardamos más de 20 días en llegar en barco a Australia. Pasamos por el canal de Suez… Puf, el calor que hacía allí. Recuerdo los mareos. La incertidumbre. Aquella sensación de no saber muy bien adónde íbamos ni cómo viviríamos.» | «El avión era pequeño, de hélices, y se movía muchísimo. Aterrizamos en una pista en medio de una tierra muy muy roja. Había polvo por todas partes. Nunca había visto tanto polvo. Nos llevaron a las casas, de chapa, madera y uralita.»
- QUOTES después: «Salimos de Málaga y tardamos más de 20 días en llegar en barco a Australia. Pasamos por el canal de Suez… Puf, el calor que hacía allí. Recuerdo los mareos. La incertidumbre. Aquella sensación de no saber muy bien adónde íbamos ni cómo viviríamos.» — Víctor Calvo · Residente de Wittenoom de niño, hijastro de minero · witness | «El avión era pequeño, de hélices, y se movía muchísimo. Aterrizamos en una pista en medio de una tierra muy muy roja. Había polvo por todas partes. Nunca había visto tanto polvo. Nos llevaron a las casas, de chapa, madera y uralita.» — Víctor Calvo · Residente de Wittenoom de niño, hijastro de minero · witness

### Cap 2 · foto 11

- Ancla: «Después del barco, un avión pequeño, de hélices, que se sacude durante todo el vuelo.»
- PEOPLE antes: -
- PEOPLE después: -
- QUOTES antes: «Salimos de Málaga y tardamos más de 20 días en llegar en barco a Australia. Pasamos por el canal de Suez… Puf, el calor que hacía allí. Recuerdo los mareos. La incertidumbre. Aquella sensación de no saber muy bien adónde íbamos ni cómo viviríamos.» | «El avión era pequeño, de hélices, y se movía muchísimo. Aterrizamos en una pista en medio de una tierra muy muy roja. Había polvo por todas partes. Nunca había visto tanto polvo. Nos llevaron a las casas, de chapa, madera y uralita.»
- QUOTES después: «Salimos de Málaga y tardamos más de 20 días en llegar en barco a Australia. Pasamos por el canal de Suez… Puf, el calor que hacía allí. Recuerdo los mareos. La incertidumbre. Aquella sensación de no saber muy bien adónde íbamos ni cómo viviríamos.» — Víctor Calvo · Residente de Wittenoom de niño, hijastro de minero · witness | «El avión era pequeño, de hélices, y se movía muchísimo. Aterrizamos en una pista en medio de una tierra muy muy roja. Había polvo por todas partes. Nunca había visto tanto polvo. Nos llevaron a las casas, de chapa, madera y uralita.» — Víctor Calvo · Residente de Wittenoom de niño, hijastro de minero · witness

### Cap 2 · foto 12

- Ancla: «Aterriza en una pista en medio de una tierra muy roja, en el desierto de Pilbara, en Australia Occidental.»
- PEOPLE antes: -
- PEOPLE después: -
- QUOTES antes: «Salimos de Málaga y tardamos más de 20 días en llegar en barco a Australia. Pasamos por el canal de Suez… Puf, el calor que hacía allí. Recuerdo los mareos. La incertidumbre. Aquella sensación de no saber muy bien adónde íbamos ni cómo viviríamos.» | «El avión era pequeño, de hélices, y se movía muchísimo. Aterrizamos en una pista en medio de una tierra muy muy roja. Había polvo por todas partes. Nunca había visto tanto polvo. Nos llevaron a las casas, de chapa, madera y uralita.»
- QUOTES después: «Salimos de Málaga y tardamos más de 20 días en llegar en barco a Australia. Pasamos por el canal de Suez… Puf, el calor que hacía allí. Recuerdo los mareos. La incertidumbre. Aquella sensación de no saber muy bien adónde íbamos ni cómo viviríamos.» — Víctor Calvo · Residente de Wittenoom de niño, hijastro de minero · witness | «El avión era pequeño, de hélices, y se movía muchísimo. Aterrizamos en una pista en medio de una tierra muy muy roja. Había polvo por todas partes. Nunca había visto tanto polvo. Nos llevaron a las casas, de chapa, madera y uralita.» — Víctor Calvo · Residente de Wittenoom de niño, hijastro de minero · witness

### Cap 2 · foto 13

- Ancla: «Hay polvo por todas partes. Ese niño cuenta que nunca había visto tanto polvo.»
- PEOPLE antes: -
- PEOPLE después: -
- QUOTES antes: «Salimos de Málaga y tardamos más de 20 días en llegar en barco a Australia. Pasamos por el canal de Suez… Puf, el calor que hacía allí. Recuerdo los mareos. La incertidumbre. Aquella sensación de no saber muy bien adónde íbamos ni cómo viviríamos.» | «El avión era pequeño, de hélices, y se movía muchísimo. Aterrizamos en una pista en medio de una tierra muy muy roja. Había polvo por todas partes. Nunca había visto tanto polvo. Nos llevaron a las casas, de chapa, madera y uralita.»
- QUOTES después: «Salimos de Málaga y tardamos más de 20 días en llegar en barco a Australia. Pasamos por el canal de Suez… Puf, el calor que hacía allí. Recuerdo los mareos. La incertidumbre. Aquella sensación de no saber muy bien adónde íbamos ni cómo viviríamos.» — Víctor Calvo · Residente de Wittenoom de niño, hijastro de minero · witness | «El avión era pequeño, de hélices, y se movía muchísimo. Aterrizamos en una pista en medio de una tierra muy muy roja. Había polvo por todas partes. Nunca había visto tanto polvo. Nos llevaron a las casas, de chapa, madera y uralita.» — Víctor Calvo · Residente de Wittenoom de niño, hijastro de minero · witness

### Cap 2 · foto 14

- Ancla: «Los llevan a las casas: chapa, madera y uralita.»
- PEOPLE antes: -
- PEOPLE después: -
- QUOTES antes: «Salimos de Málaga y tardamos más de 20 días en llegar en barco a Australia. Pasamos por el canal de Suez… Puf, el calor que hacía allí. Recuerdo los mareos. La incertidumbre. Aquella sensación de no saber muy bien adónde íbamos ni cómo viviríamos.» | «El avión era pequeño, de hélices, y se movía muchísimo. Aterrizamos en una pista en medio de una tierra muy muy roja. Había polvo por todas partes. Nunca había visto tanto polvo. Nos llevaron a las casas, de chapa, madera y uralita.»
- QUOTES después: «Salimos de Málaga y tardamos más de 20 días en llegar en barco a Australia. Pasamos por el canal de Suez… Puf, el calor que hacía allí. Recuerdo los mareos. La incertidumbre. Aquella sensación de no saber muy bien adónde íbamos ni cómo viviríamos.» — Víctor Calvo · Residente de Wittenoom de niño, hijastro de minero · witness | «El avión era pequeño, de hélices, y se movía muchísimo. Aterrizamos en una pista en medio de una tierra muy muy roja. Había polvo por todas partes. Nunca había visto tanto polvo. Nos llevaron a las casas, de chapa, madera y uralita.» — Víctor Calvo · Residente de Wittenoom de niño, hijastro de minero · witness

### Cap 2 · foto 15

- Ancla: «La familia de Juan-Barroso había llegado en agosto de mil novecientos sesenta y dos. De esa tierra sacan crocidolita, el asbesto azul, un mineral que se paga bien porque aguanta el calor y no se gasta.»
- PEOPLE antes: -
- PEOPLE después: -
- QUOTES antes: «Salimos de Málaga y tardamos más de 20 días en llegar en barco a Australia. Pasamos por el canal de Suez… Puf, el calor que hacía allí. Recuerdo los mareos. La incertidumbre. Aquella sensación de no saber muy bien adónde íbamos ni cómo viviríamos.» | «El avión era pequeño, de hélices, y se movía muchísimo. Aterrizamos en una pista en medio de una tierra muy muy roja. Había polvo por todas partes. Nunca había visto tanto polvo. Nos llevaron a las casas, de chapa, madera y uralita.»
- QUOTES después: «Salimos de Málaga y tardamos más de 20 días en llegar en barco a Australia. Pasamos por el canal de Suez… Puf, el calor que hacía allí. Recuerdo los mareos. La incertidumbre. Aquella sensación de no saber muy bien adónde íbamos ni cómo viviríamos.» — Víctor Calvo · Residente de Wittenoom de niño, hijastro de minero · witness | «El avión era pequeño, de hélices, y se movía muchísimo. Aterrizamos en una pista en medio de una tierra muy muy roja. Había polvo por todas partes. Nunca había visto tanto polvo. Nos llevaron a las casas, de chapa, madera y uralita.» — Víctor Calvo · Residente de Wittenoom de niño, hijastro de minero · witness

### Cap 2 · foto 16

- Ancla: «Nadie les dijo qué era el polvo. La compañía lo sabía desde hacía dieciocho años.»
- PEOPLE antes: -
- PEOPLE después: -
- QUOTES antes: «Salimos de Málaga y tardamos más de 20 días en llegar en barco a Australia. Pasamos por el canal de Suez… Puf, el calor que hacía allí. Recuerdo los mareos. La incertidumbre. Aquella sensación de no saber muy bien adónde íbamos ni cómo viviríamos.» | «El avión era pequeño, de hélices, y se movía muchísimo. Aterrizamos en una pista en medio de una tierra muy muy roja. Había polvo por todas partes. Nunca había visto tanto polvo. Nos llevaron a las casas, de chapa, madera y uralita.»
- QUOTES después: «Salimos de Málaga y tardamos más de 20 días en llegar en barco a Australia. Pasamos por el canal de Suez… Puf, el calor que hacía allí. Recuerdo los mareos. La incertidumbre. Aquella sensación de no saber muy bien adónde íbamos ni cómo viviríamos.» — Víctor Calvo · Residente de Wittenoom de niño, hijastro de minero · witness | «El avión era pequeño, de hélices, y se movía muchísimo. Aterrizamos en una pista en medio de una tierra muy muy roja. Había polvo por todas partes. Nunca había visto tanto polvo. Nos llevaron a las casas, de chapa, madera y uralita.» — Víctor Calvo · Residente de Wittenoom de niño, hijastro de minero · witness

### Cap 3 · foto 1 — ancla

- Ancla: «En mil novecientos cuarenta y cuatro, el inspector de minas y el ingeniero de minas Adjunto del Estado ya habían informado sobre el problema del polvo.»
- PEOPLE antes: -
- PEOPLE después: Funcionario no identificado por nombre que informó sobre el problema del polvo · - · 1944; Funcionario no identificado por nombre que también informó sobre el problema del polvo · - · - (Inspector de Minas, Ingeniero de Minas Adjunto del Estado)
- QUOTES antes: «En un año o dos, ABA producirá la cosecha más rica y letal de casos de asbestosis en la literatura mundial... Naturalmente, creo que algunos de estos pechos deberían ser examinados.» | «Dije 'Miren, tienen problemas'... Me menospreciaron y de hecho me etiquetaron como un alborotador... No escucharon. Yo era solo un joven, un médico aéreo... Acababa de llegar de Inglaterra y pensaron '¿Quién es este tipo engreído?' Esa fue la actitud.» | «La Compañía no admite que ese polvo [de Wittenoom] sea peligroso. El simple hecho de que haya nubes de polvo no significa que ese polvo sea peligroso.»
- QUOTES después: «En un año o dos, ABA producirá la cosecha más rica y letal de casos de asbestosis en la literatura mundial... Naturalmente, creo que algunos de estos pechos deberían ser examinados.» — Eric Saint · Médico aéreo · 1948/1951 · witness | «Dije 'Miren, tienen problemas'... Me menospreciaron y de hecho me etiquetaron como un alborotador... No escucharon. Yo era solo un joven, un médico aéreo... Acababa de llegar de Inglaterra y pensaron '¿Quién es este tipo engreído?' Esa fue la actitud.» — Eric Saint · Médico aéreo · 1948/1951 · witness | «La Compañía no admite que ese polvo [de Wittenoom] sea peligroso. El simple hecho de que haya nubes de polvo no significa que ese polvo sea peligroso.» — El defensor del empleador · Defensor del empleador · 1949

### Cap 3 · foto 2 — arrastre

- Ancla: «En mil novecientos cuarenta y seis ya había diagnósticos de asbestosis, y un inspector describió las condiciones de trabajo como terroríficas.»
- PEOPLE antes: -
- PEOPLE después: Funcionario no identificado por nombre que informó sobre el problema del polvo · - · 1944 (named earlier in the paragraph); Funcionario no identificado por nombre que también informó sobre el problema del polvo · - · - (named earlier in the paragraph) (Inspector de Minas, Ingeniero de Minas Adjunto del Estado)
- QUOTES antes: «En un año o dos, ABA producirá la cosecha más rica y letal de casos de asbestosis en la literatura mundial... Naturalmente, creo que algunos de estos pechos deberían ser examinados.» | «Dije 'Miren, tienen problemas'... Me menospreciaron y de hecho me etiquetaron como un alborotador... No escucharon. Yo era solo un joven, un médico aéreo... Acababa de llegar de Inglaterra y pensaron '¿Quién es este tipo engreído?' Esa fue la actitud.» | «La Compañía no admite que ese polvo [de Wittenoom] sea peligroso. El simple hecho de que haya nubes de polvo no significa que ese polvo sea peligroso.»
- QUOTES después: «En un año o dos, ABA producirá la cosecha más rica y letal de casos de asbestosis en la literatura mundial... Naturalmente, creo que algunos de estos pechos deberían ser examinados.» — Eric Saint · Médico aéreo · 1948/1951 · witness | «Dije 'Miren, tienen problemas'... Me menospreciaron y de hecho me etiquetaron como un alborotador... No escucharon. Yo era solo un joven, un médico aéreo... Acababa de llegar de Inglaterra y pensaron '¿Quién es este tipo engreído?' Esa fue la actitud.» — Eric Saint · Médico aéreo · 1948/1951 · witness | «La Compañía no admite que ese polvo [de Wittenoom] sea peligroso. El simple hecho de que haya nubes de polvo no significa que ese polvo sea peligroso.» — El defensor del empleador · Defensor del empleador · 1949

### Cap 3 · foto 3 — ancla

- Ancla: «La mina era entonces de ABA, una filial de CSR que en mil novecientos cuarenta y tres había tomado los intereses de Hancock y Wright.»
- PEOPLE antes: -
- PEOPLE después: Empresa operadora de la explotación, filial de CSR · - · -; Empresa matriz de ABA; participó en la explotación, anunció el cierre, creó un fondo de asistencia y pagó indemnizaciones · - · - (Australian Blue Asbestos Ltd., CSR)
- QUOTES antes: «En un año o dos, ABA producirá la cosecha más rica y letal de casos de asbestosis en la literatura mundial... Naturalmente, creo que algunos de estos pechos deberían ser examinados.» | «Dije 'Miren, tienen problemas'... Me menospreciaron y de hecho me etiquetaron como un alborotador... No escucharon. Yo era solo un joven, un médico aéreo... Acababa de llegar de Inglaterra y pensaron '¿Quién es este tipo engreído?' Esa fue la actitud.» | «La Compañía no admite que ese polvo [de Wittenoom] sea peligroso. El simple hecho de que haya nubes de polvo no significa que ese polvo sea peligroso.»
- QUOTES después: «En un año o dos, ABA producirá la cosecha más rica y letal de casos de asbestosis en la literatura mundial... Naturalmente, creo que algunos de estos pechos deberían ser examinados.» — Eric Saint · Médico aéreo · 1948/1951 · witness | «Dije 'Miren, tienen problemas'... Me menospreciaron y de hecho me etiquetaron como un alborotador... No escucharon. Yo era solo un joven, un médico aéreo... Acababa de llegar de Inglaterra y pensaron '¿Quién es este tipo engreído?' Esa fue la actitud.» — Eric Saint · Médico aéreo · 1948/1951 · witness | «La Compañía no admite que ese polvo [de Wittenoom] sea peligroso. El simple hecho de que haya nubes de polvo no significa que ese polvo sea peligroso.» — El defensor del empleador · Defensor del empleador · 1949

### Cap 3 · foto 4

- Ancla: «Mil novecientos cuarenta y ocho. Un médico llega en avión y escribe una carta a máquina: los niveles de polvo son extremadamente peligrosos.»
- PEOPLE antes: -
- PEOPLE después: -
- QUOTES antes: «En un año o dos, ABA producirá la cosecha más rica y letal de casos de asbestosis en la literatura mundial... Naturalmente, creo que algunos de estos pechos deberían ser examinados.» | «Dije 'Miren, tienen problemas'... Me menospreciaron y de hecho me etiquetaron como un alborotador... No escucharon. Yo era solo un joven, un médico aéreo... Acababa de llegar de Inglaterra y pensaron '¿Quién es este tipo engreído?' Esa fue la actitud.» | «La Compañía no admite que ese polvo [de Wittenoom] sea peligroso. El simple hecho de que haya nubes de polvo no significa que ese polvo sea peligroso.»
- QUOTES después: «En un año o dos, ABA producirá la cosecha más rica y letal de casos de asbestosis en la literatura mundial... Naturalmente, creo que algunos de estos pechos deberían ser examinados.» — Eric Saint · Médico aéreo · 1948/1951 · witness | «Dije 'Miren, tienen problemas'... Me menospreciaron y de hecho me etiquetaron como un alborotador... No escucharon. Yo era solo un joven, un médico aéreo... Acababa de llegar de Inglaterra y pensaron '¿Quién es este tipo engreído?' Esa fue la actitud.» — Eric Saint · Médico aéreo · 1948/1951 · witness | «La Compañía no admite que ese polvo [de Wittenoom] sea peligroso. El simple hecho de que haya nubes de polvo no significa que ese polvo sea peligroso.» — El defensor del empleador · Defensor del empleador · 1949

### Cap 3 · foto 5 — ancla

- Ancla: «El médico escribe que en un año o dos ABA va a producir la cosecha más abundante y letal de casos de asbestosis de la literatura mundial»
- PEOPLE antes: -
- PEOPLE después: Empresa operadora de la explotación, filial de CSR · - · - (Australian Blue Asbestos Ltd.)
- QUOTES antes: «En un año o dos, ABA producirá la cosecha más rica y letal de casos de asbestosis en la literatura mundial... Naturalmente, creo que algunos de estos pechos deberían ser examinados.» | «Dije 'Miren, tienen problemas'... Me menospreciaron y de hecho me etiquetaron como un alborotador... No escucharon. Yo era solo un joven, un médico aéreo... Acababa de llegar de Inglaterra y pensaron '¿Quién es este tipo engreído?' Esa fue la actitud.» | «La Compañía no admite que ese polvo [de Wittenoom] sea peligroso. El simple hecho de que haya nubes de polvo no significa que ese polvo sea peligroso.»
- QUOTES después: «En un año o dos, ABA producirá la cosecha más rica y letal de casos de asbestosis en la literatura mundial... Naturalmente, creo que algunos de estos pechos deberían ser examinados.» — Eric Saint · Médico aéreo · 1948/1951 · witness | «Dije 'Miren, tienen problemas'... Me menospreciaron y de hecho me etiquetaron como un alborotador... No escucharon. Yo era solo un joven, un médico aéreo... Acababa de llegar de Inglaterra y pensaron '¿Quién es este tipo engreído?' Esa fue la actitud.» — Eric Saint · Médico aéreo · 1948/1951 · witness | «La Compañía no admite que ese polvo [de Wittenoom] sea peligroso. El simple hecho de que haya nubes de polvo no significa que ese polvo sea peligroso.» — El defensor del empleador · Defensor del empleador · 1949

### Cap 3 · foto 6 — ancla

- Ancla: «y que convendría examinar algunos de esos tórax. Se llama Eric Saint.»
- PEOPLE antes: Doctor de la sanidad pública que advirtió de los peligros · - · 1948, 1949, 1950, 1951
- PEOPLE después: Médico que atendía Wittenoom como médico aéreo y advirtió sobre el polvo y la asbestosis · - · 1948, 1949, 1950, 1951 (Eric Saint)
- QUOTES antes: «En un año o dos, ABA producirá la cosecha más rica y letal de casos de asbestosis en la literatura mundial... Naturalmente, creo que algunos de estos pechos deberían ser examinados.» | «Dije 'Miren, tienen problemas'... Me menospreciaron y de hecho me etiquetaron como un alborotador... No escucharon. Yo era solo un joven, un médico aéreo... Acababa de llegar de Inglaterra y pensaron '¿Quién es este tipo engreído?' Esa fue la actitud.» | «La Compañía no admite que ese polvo [de Wittenoom] sea peligroso. El simple hecho de que haya nubes de polvo no significa que ese polvo sea peligroso.»
- QUOTES después: «En un año o dos, ABA producirá la cosecha más rica y letal de casos de asbestosis en la literatura mundial... Naturalmente, creo que algunos de estos pechos deberían ser examinados.» — Eric Saint · Médico aéreo · 1948/1951 · witness | «Dije 'Miren, tienen problemas'... Me menospreciaron y de hecho me etiquetaron como un alborotador... No escucharon. Yo era solo un joven, un médico aéreo... Acababa de llegar de Inglaterra y pensaron '¿Quién es este tipo engreído?' Esa fue la actitud.» — Eric Saint · Médico aéreo · 1948/1951 · witness | «La Compañía no admite que ese polvo [de Wittenoom] sea peligroso. El simple hecho de que haya nubes de polvo no significa que ese polvo sea peligroso.» — El defensor del empleador · Defensor del empleador · 1949

### Cap 3 · foto 7 — arrastre

- Ancla: «Lo que pasó con la carta lo contó él mismo: «Me desestimaron y, de hecho, me tildaron de alborotador», dijo Saint.»
- PEOPLE antes: -
- PEOPLE después: Médico que atendía Wittenoom como médico aéreo y advirtió sobre el polvo y la asbestosis · - · 1948, 1949, 1950, 1951 (named earlier in the paragraph) (Eric Saint)
- QUOTES antes: «En un año o dos, ABA producirá la cosecha más rica y letal de casos de asbestosis en la literatura mundial... Naturalmente, creo que algunos de estos pechos deberían ser examinados.» | «Dije 'Miren, tienen problemas'... Me menospreciaron y de hecho me etiquetaron como un alborotador... No escucharon. Yo era solo un joven, un médico aéreo... Acababa de llegar de Inglaterra y pensaron '¿Quién es este tipo engreído?' Esa fue la actitud.» | «La Compañía no admite que ese polvo [de Wittenoom] sea peligroso. El simple hecho de que haya nubes de polvo no significa que ese polvo sea peligroso.»
- QUOTES después: «En un año o dos, ABA producirá la cosecha más rica y letal de casos de asbestosis en la literatura mundial... Naturalmente, creo que algunos de estos pechos deberían ser examinados.» — Eric Saint · Médico aéreo · 1948/1951 · witness | «Dije 'Miren, tienen problemas'... Me menospreciaron y de hecho me etiquetaron como un alborotador... No escucharon. Yo era solo un joven, un médico aéreo... Acababa de llegar de Inglaterra y pensaron '¿Quién es este tipo engreído?' Esa fue la actitud.» — Eric Saint · Médico aéreo · 1948/1951 · witness | «La Compañía no admite que ese polvo [de Wittenoom] sea peligroso. El simple hecho de que haya nubes de polvo no significa que ese polvo sea peligroso.» — El defensor del empleador · Defensor del empleador · 1949

### Cap 3 · foto 8

- Ancla: «Un año después, en una sala de arbitraje, la empresa contestó a los que hablaban del polvo.»
- PEOPLE antes: -
- PEOPLE después: -
- QUOTES antes: «En un año o dos, ABA producirá la cosecha más rica y letal de casos de asbestosis en la literatura mundial... Naturalmente, creo que algunos de estos pechos deberían ser examinados.» | «Dije 'Miren, tienen problemas'... Me menospreciaron y de hecho me etiquetaron como un alborotador... No escucharon. Yo era solo un joven, un médico aéreo... Acababa de llegar de Inglaterra y pensaron '¿Quién es este tipo engreído?' Esa fue la actitud.» | «La Compañía no admite que ese polvo [de Wittenoom] sea peligroso. El simple hecho de que haya nubes de polvo no significa que ese polvo sea peligroso.»
- QUOTES después: «En un año o dos, ABA producirá la cosecha más rica y letal de casos de asbestosis en la literatura mundial... Naturalmente, creo que algunos de estos pechos deberían ser examinados.» — Eric Saint · Médico aéreo · 1948/1951 · witness | «Dije 'Miren, tienen problemas'... Me menospreciaron y de hecho me etiquetaron como un alborotador... No escucharon. Yo era solo un joven, un médico aéreo... Acababa de llegar de Inglaterra y pensaron '¿Quién es este tipo engreído?' Esa fue la actitud.» — Eric Saint · Médico aéreo · 1948/1951 · witness | «La Compañía no admite que ese polvo [de Wittenoom] sea peligroso. El simple hecho de que haya nubes de polvo no significa que ese polvo sea peligroso.» — El defensor del empleador · Defensor del empleador · 1949

### Cap 3 · foto 9

- Ancla: ««El mero hecho de que haya nubes de polvo no significa que ese polvo sea peligroso», dijo el defensor del empleador.»
- PEOPLE antes: -
- PEOPLE después: -
- QUOTES antes: «En un año o dos, ABA producirá la cosecha más rica y letal de casos de asbestosis en la literatura mundial... Naturalmente, creo que algunos de estos pechos deberían ser examinados.» | «Dije 'Miren, tienen problemas'... Me menospreciaron y de hecho me etiquetaron como un alborotador... No escucharon. Yo era solo un joven, un médico aéreo... Acababa de llegar de Inglaterra y pensaron '¿Quién es este tipo engreído?' Esa fue la actitud.» | «La Compañía no admite que ese polvo [de Wittenoom] sea peligroso. El simple hecho de que haya nubes de polvo no significa que ese polvo sea peligroso.»
- QUOTES después: «En un año o dos, ABA producirá la cosecha más rica y letal de casos de asbestosis en la literatura mundial... Naturalmente, creo que algunos de estos pechos deberían ser examinados.» — Eric Saint · Médico aéreo · 1948/1951 · witness | «Dije 'Miren, tienen problemas'... Me menospreciaron y de hecho me etiquetaron como un alborotador... No escucharon. Yo era solo un joven, un médico aéreo... Acababa de llegar de Inglaterra y pensaron '¿Quién es este tipo engreído?' Esa fue la actitud.» — Eric Saint · Médico aéreo · 1948/1951 · witness | «La Compañía no admite que ese polvo [de Wittenoom] sea peligroso. El simple hecho de que haya nubes de polvo no significa que ese polvo sea peligroso.» — El defensor del empleador · Defensor del empleador · 1949

### Cap 3 · foto 10

- Ancla: «Nueve años después, otro organismo entró al molino y escribió lo que vio.»
- PEOPLE antes: -
- PEOPLE después: -
- QUOTES antes: «En un año o dos, ABA producirá la cosecha más rica y letal de casos de asbestosis en la literatura mundial... Naturalmente, creo que algunos de estos pechos deberían ser examinados.» | «Dije 'Miren, tienen problemas'... Me menospreciaron y de hecho me etiquetaron como un alborotador... No escucharon. Yo era solo un joven, un médico aéreo... Acababa de llegar de Inglaterra y pensaron '¿Quién es este tipo engreído?' Esa fue la actitud.» | «La Compañía no admite que ese polvo [de Wittenoom] sea peligroso. El simple hecho de que haya nubes de polvo no significa que ese polvo sea peligroso.»
- QUOTES después: «En un año o dos, ABA producirá la cosecha más rica y letal de casos de asbestosis en la literatura mundial... Naturalmente, creo que algunos de estos pechos deberían ser examinados.» — Eric Saint · Médico aéreo · 1948/1951 · witness | «Dije 'Miren, tienen problemas'... Me menospreciaron y de hecho me etiquetaron como un alborotador... No escucharon. Yo era solo un joven, un médico aéreo... Acababa de llegar de Inglaterra y pensaron '¿Quién es este tipo engreído?' Esa fue la actitud.» — Eric Saint · Médico aéreo · 1948/1951 · witness | «La Compañía no admite que ese polvo [de Wittenoom] sea peligroso. El simple hecho de que haya nubes de polvo no significa que ese polvo sea peligroso.» — El defensor del empleador · Defensor del empleador · 1949

### Cap 3 · foto 11 — ancla

- Ancla: «Mil novecientos cincuenta y siete. La Junta de Referencia entra al molino y deja constancia: condiciones extremadamente polvorientas»
- PEOPLE antes: Organismo de arbitraje laboral · - · -
- PEOPLE después: Órgano de arbitraje laboral que constató las condiciones polvorientas del molino · - · - (Junta de Referencia)
- QUOTES antes: «Las condiciones dentro del molino eran extremadamente polvorientas y... los trabajadores del molino estaban mugrientos de polvo... Una espesa nube de polvo estaba presente en las inmediaciones del molino.» | «Cuando las Casandras... advirtieron que el polvo era un problema y predijeron el desarrollo de enfermedades [en Wittenoom], no sonaron las alarmas en las personas involucradas en la industria minera porque estaban acostumbradas a ello; lo esperaban.» | «para todos los fines prácticos, la vida de la mina [de Wittenoom] es ilimitada.»
- QUOTES después: «Las condiciones dentro del molino eran extremadamente polvorientas y... los trabajadores del molino estaban mugrientos de polvo... Una espesa nube de polvo estaba presente en las inmediaciones del molino.» — Junta de Referencia · Organismo de arbitraje laboral · 1957 | «Cuando las Casandras... advirtieron que el polvo era un problema y predijeron el desarrollo de enfermedades [en Wittenoom], no sonaron las alarmas en las personas involucradas en la industria minera porque estaban acostumbradas a ello; lo esperaban.» — McNulty · Médico de Salud Ocupacional | «para todos los fines prácticos, la vida de la mina [de Wittenoom] es ilimitada.» — Prime Minister Chifley · Primer Ministro de Australia · 1947

### Cap 3 · foto 12 — arrastre

- Ancla: «trabajadores cubiertos de polvo de pies a cabeza. «Una espesa nube de polvo estaba presente en las inmediaciones del molino», escribió la Junta.»
- PEOPLE antes: -
- PEOPLE después: Órgano de arbitraje laboral que constató las condiciones polvorientas del molino · - · - (named earlier in the paragraph) (Junta de Referencia)
- QUOTES antes: «Las condiciones dentro del molino eran extremadamente polvorientas y... los trabajadores del molino estaban mugrientos de polvo... Una espesa nube de polvo estaba presente en las inmediaciones del molino.» | «Cuando las Casandras... advirtieron que el polvo era un problema y predijeron el desarrollo de enfermedades [en Wittenoom], no sonaron las alarmas en las personas involucradas en la industria minera porque estaban acostumbradas a ello; lo esperaban.» | «para todos los fines prácticos, la vida de la mina [de Wittenoom] es ilimitada.»
- QUOTES después: «Las condiciones dentro del molino eran extremadamente polvorientas y... los trabajadores del molino estaban mugrientos de polvo... Una espesa nube de polvo estaba presente en las inmediaciones del molino.» — Junta de Referencia · Organismo de arbitraje laboral · 1957 | «Cuando las Casandras... advirtieron que el polvo era un problema y predijeron el desarrollo de enfermedades [en Wittenoom], no sonaron las alarmas en las personas involucradas en la industria minera porque estaban acostumbradas a ello; lo esperaban.» — McNulty · Médico de Salud Ocupacional | «para todos los fines prácticos, la vida de la mina [de Wittenoom] es ilimitada.» — Prime Minister Chifley · Primer Ministro de Australia · 1947

### Cap 3 · foto 13 — arrastre

- Ancla: «Siete meses después, con unos equipos reductores de polvo ya instalados, el suplemento salarial por polvo se redujo y se restringió.»
- PEOPLE antes: -
- PEOPLE después: Órgano de arbitraje laboral que constató las condiciones polvorientas del molino · - · - (named earlier in the paragraph) (Junta de Referencia)
- QUOTES antes: «Las condiciones dentro del molino eran extremadamente polvorientas y... los trabajadores del molino estaban mugrientos de polvo... Una espesa nube de polvo estaba presente en las inmediaciones del molino.» | «Cuando las Casandras... advirtieron que el polvo era un problema y predijeron el desarrollo de enfermedades [en Wittenoom], no sonaron las alarmas en las personas involucradas en la industria minera porque estaban acostumbradas a ello; lo esperaban.» | «para todos los fines prácticos, la vida de la mina [de Wittenoom] es ilimitada.»
- QUOTES después: «Las condiciones dentro del molino eran extremadamente polvorientas y... los trabajadores del molino estaban mugrientos de polvo... Una espesa nube de polvo estaba presente en las inmediaciones del molino.» — Junta de Referencia · Organismo de arbitraje laboral · 1957 | «Cuando las Casandras... advirtieron que el polvo era un problema y predijeron el desarrollo de enfermedades [en Wittenoom], no sonaron las alarmas en las personas involucradas en la industria minera porque estaban acostumbradas a ello; lo esperaban.» — McNulty · Médico de Salud Ocupacional | «para todos los fines prácticos, la vida de la mina [de Wittenoom] es ilimitada.» — Prime Minister Chifley · Primer Ministro de Australia · 1947

### Cap 3 · foto 14 — ancla

- Ancla: «CSR venía de la industria azucarera y tenía muy poca experiencia en minas. Los reguladores del Estado hicieron poco más que emitir advertencias y pedir equipos para el polvo.»
- PEOPLE antes: -
- PEOPLE después: Empresa matriz de ABA; participó en la explotación, anunció el cierre, creó un fondo de asistencia y pagó indemnizaciones · - · - (CSR)
- QUOTES antes: «Las condiciones dentro del molino eran extremadamente polvorientas y... los trabajadores del molino estaban mugrientos de polvo... Una espesa nube de polvo estaba presente en las inmediaciones del molino.» | «Cuando las Casandras... advirtieron que el polvo era un problema y predijeron el desarrollo de enfermedades [en Wittenoom], no sonaron las alarmas en las personas involucradas en la industria minera porque estaban acostumbradas a ello; lo esperaban.» | «para todos los fines prácticos, la vida de la mina [de Wittenoom] es ilimitada.»
- QUOTES después: «Las condiciones dentro del molino eran extremadamente polvorientas y... los trabajadores del molino estaban mugrientos de polvo... Una espesa nube de polvo estaba presente en las inmediaciones del molino.» — Junta de Referencia · Organismo de arbitraje laboral · 1957 | «Cuando las Casandras... advirtieron que el polvo era un problema y predijeron el desarrollo de enfermedades [en Wittenoom], no sonaron las alarmas en las personas involucradas en la industria minera porque estaban acostumbradas a ello; lo esperaban.» — McNulty · Médico de Salud Ocupacional | «para todos los fines prácticos, la vida de la mina [de Wittenoom] es ilimitada.» — Prime Minister Chifley · Primer Ministro de Australia · 1947

### Cap 3 · foto 15 — ancla

- Ancla: «Jim McNulty lo explicó así: cuando las Casandras advirtieron que el polvo era un problema y predijeron la enfermedad, en la industria minera no se encendieron las alarmas»
- PEOPLE antes: Médico del Departamento de Salud Pública · - · 1960, 1962, 1968
- PEOPLE después: Médico de salud pública que diagnosticó y comunicó casos relacionados con Wittenoom · - · 1960, 1962, 1968 (Jim McNulty)
- QUOTES antes: «Las condiciones dentro del molino eran extremadamente polvorientas y... los trabajadores del molino estaban mugrientos de polvo... Una espesa nube de polvo estaba presente en las inmediaciones del molino.» | «Cuando las Casandras... advirtieron que el polvo era un problema y predijeron el desarrollo de enfermedades [en Wittenoom], no sonaron las alarmas en las personas involucradas en la industria minera porque estaban acostumbradas a ello; lo esperaban.» | «para todos los fines prácticos, la vida de la mina [de Wittenoom] es ilimitada.»
- QUOTES después: «Las condiciones dentro del molino eran extremadamente polvorientas y... los trabajadores del molino estaban mugrientos de polvo... Una espesa nube de polvo estaba presente en las inmediaciones del molino.» — Junta de Referencia · Organismo de arbitraje laboral · 1957 | «Cuando las Casandras... advirtieron que el polvo era un problema y predijeron el desarrollo de enfermedades [en Wittenoom], no sonaron las alarmas en las personas involucradas en la industria minera porque estaban acostumbradas a ello; lo esperaban.» — McNulty · Médico de Salud Ocupacional | «para todos los fines prácticos, la vida de la mina [de Wittenoom] es ilimitada.» — Prime Minister Chifley · Primer Ministro de Australia · 1947

### Cap 3 · foto 16 — ancla

- Ancla: ««porque estaban acostumbrados; lo esperaban», dijo McNulty. En mil novecientos sesenta y uno la producción subió. Al año siguiente, los Écija bajaban de aquel avión.»
- PEOPLE antes: -
- PEOPLE después: Médico de salud pública que diagnosticó y comunicó casos relacionados con Wittenoom · - · 1960, 1962, 1968 (Jim McNulty)
- QUOTES antes: «Las condiciones dentro del molino eran extremadamente polvorientas y... los trabajadores del molino estaban mugrientos de polvo... Una espesa nube de polvo estaba presente en las inmediaciones del molino.» | «Cuando las Casandras... advirtieron que el polvo era un problema y predijeron el desarrollo de enfermedades [en Wittenoom], no sonaron las alarmas en las personas involucradas en la industria minera porque estaban acostumbradas a ello; lo esperaban.» | «para todos los fines prácticos, la vida de la mina [de Wittenoom] es ilimitada.»
- QUOTES después: «Las condiciones dentro del molino eran extremadamente polvorientas y... los trabajadores del molino estaban mugrientos de polvo... Una espesa nube de polvo estaba presente en las inmediaciones del molino.» — Junta de Referencia · Organismo de arbitraje laboral · 1957 | «Cuando las Casandras... advirtieron que el polvo era un problema y predijeron el desarrollo de enfermedades [en Wittenoom], no sonaron las alarmas en las personas involucradas en la industria minera porque estaban acostumbradas a ello; lo esperaban.» — McNulty · Médico de Salud Ocupacional | «para todos los fines prácticos, la vida de la mina [de Wittenoom] es ilimitada.» — Prime Minister Chifley · Primer Ministro de Australia · 1947

### Cap 4 · foto 1

- Ancla: «Los chicos del pueblo juegan con el mineral.»
- PEOPLE antes: -
- PEOPLE después: -
- QUOTES antes: «En Wittenoom, un pueblo levantado de la nada, se había utilizado muchísimo. Nosotros jugábamos con él y lo íbamos deshilachando. Nos lo metíamos en la boca. Cuando lo tocábamos salía un polvillo que lo impregnaba todo. Estábamos rodeados de amianto azul, pero no nos daba miedo. Nadie nos avisó de nada.»
- QUOTES después: «En Wittenoom, un pueblo levantado de la nada, se había utilizado muchísimo. Nosotros jugábamos con él y lo íbamos deshilachando. Nos lo metíamos en la boca. Cuando lo tocábamos salía un polvillo que lo impregnaba todo. Estábamos rodeados de amianto azul, pero no nos daba miedo. Nadie nos avisó de nada.» — Víctor Calvo · Residente de Wittenoom de niño, hijastro de minero · witness

### Cap 4 · foto 2 — ancla

- Ancla: «Víctor Calvo lo cuenta: «Nosotros jugábamos con él y lo íbamos deshilachando. Nos lo metíamos en la boca. Cuando lo tocábamos salía un polvillo que lo impregnaba todo».»
- PEOPLE antes: Hijo de Milagros Barroso, vivió en Wittenoom de niño · Wittenoom · 1962, 1963, 1964
- PEOPLE después: Hijo de Milagros Barroso e hijastro de Ramón de Juan; llegó a Wittenoom de niño y testimonia sobre la exposición infantil · Wittenoom · 1962, 1963, 1964 (Víctor Calvo)
- QUOTES antes: «En Wittenoom, un pueblo levantado de la nada, se había utilizado muchísimo. Nosotros jugábamos con él y lo íbamos deshilachando. Nos lo metíamos en la boca. Cuando lo tocábamos salía un polvillo que lo impregnaba todo. Estábamos rodeados de amianto azul, pero no nos daba miedo. Nadie nos avisó de nada.»
- QUOTES después: «En Wittenoom, un pueblo levantado de la nada, se había utilizado muchísimo. Nosotros jugábamos con él y lo íbamos deshilachando. Nos lo metíamos en la boca. Cuando lo tocábamos salía un polvillo que lo impregnaba todo. Estábamos rodeados de amianto azul, pero no nos daba miedo. Nadie nos avisó de nada.» — Víctor Calvo · Residente de Wittenoom de niño, hijastro de minero · witness

### Cap 4 · foto 3 — arrastre

- Ancla: «Estaban rodeados de amianto azul y no les daba miedo. Tampoco había dónde no estar rodeados.»
- PEOPLE antes: -
- PEOPLE después: Hijo de Milagros Barroso e hijastro de Ramón de Juan; llegó a Wittenoom de niño y testimonia sobre la exposición infantil · Wittenoom · 1962, 1963, 1964 (named earlier in the paragraph) (Víctor Calvo)
- QUOTES antes: «En Wittenoom, un pueblo levantado de la nada, se había utilizado muchísimo. Nosotros jugábamos con él y lo íbamos deshilachando. Nos lo metíamos en la boca. Cuando lo tocábamos salía un polvillo que lo impregnaba todo. Estábamos rodeados de amianto azul, pero no nos daba miedo. Nadie nos avisó de nada.»
- QUOTES después: «En Wittenoom, un pueblo levantado de la nada, se había utilizado muchísimo. Nosotros jugábamos con él y lo íbamos deshilachando. Nos lo metíamos en la boca. Cuando lo tocábamos salía un polvillo que lo impregnaba todo. Estábamos rodeados de amianto azul, pero no nos daba miedo. Nadie nos avisó de nada.» — Víctor Calvo · Residente de Wittenoom de niño, hijastro de minero · witness

### Cap 4 · foto 4 — arrastre

- Ancla: «Los relaves del molino se usaron para construir el pueblo y la pista de aterrizaje.»
- PEOPLE antes: -
- PEOPLE después: Hijo de Milagros Barroso e hijastro de Ramón de Juan; llegó a Wittenoom de niño y testimonia sobre la exposición infantil · Wittenoom · 1962, 1963, 1964 (named earlier in the paragraph) (Víctor Calvo)
- QUOTES antes: «En Wittenoom, un pueblo levantado de la nada, se había utilizado muchísimo. Nosotros jugábamos con él y lo íbamos deshilachando. Nos lo metíamos en la boca. Cuando lo tocábamos salía un polvillo que lo impregnaba todo. Estábamos rodeados de amianto azul, pero no nos daba miedo. Nadie nos avisó de nada.»
- QUOTES después: «En Wittenoom, un pueblo levantado de la nada, se había utilizado muchísimo. Nosotros jugábamos con él y lo íbamos deshilachando. Nos lo metíamos en la boca. Cuando lo tocábamos salía un polvillo que lo impregnaba todo. Estábamos rodeados de amianto azul, pero no nos daba miedo. Nadie nos avisó de nada.» — Víctor Calvo · Residente de Wittenoom de niño, hijastro de minero · witness

### Cap 4 · foto 5 — arrastre

- Ancla: «Se extendieron como suelo en las carreteras, en los patios, en los espacios públicos: el acceso a la escuela, el jardín de infantes, la iglesia.»
- PEOPLE antes: -
- PEOPLE después: Hijo de Milagros Barroso e hijastro de Ramón de Juan; llegó a Wittenoom de niño y testimonia sobre la exposición infantil · Wittenoom · 1962, 1963, 1964 (named earlier in the paragraph) (Víctor Calvo)
- QUOTES antes: «En Wittenoom, un pueblo levantado de la nada, se había utilizado muchísimo. Nosotros jugábamos con él y lo íbamos deshilachando. Nos lo metíamos en la boca. Cuando lo tocábamos salía un polvillo que lo impregnaba todo. Estábamos rodeados de amianto azul, pero no nos daba miedo. Nadie nos avisó de nada.»
- QUOTES después: «En Wittenoom, un pueblo levantado de la nada, se había utilizado muchísimo. Nosotros jugábamos con él y lo íbamos deshilachando. Nos lo metíamos en la boca. Cuando lo tocábamos salía un polvillo que lo impregnaba todo. Estábamos rodeados de amianto azul, pero no nos daba miedo. Nadie nos avisó de nada.» — Víctor Calvo · Residente de Wittenoom de niño, hijastro de minero · witness

### Cap 4 · foto 6 — arrastre

- Ancla: «El pueblo entero estaba hecho de eso.»
- PEOPLE antes: -
- PEOPLE después: Hijo de Milagros Barroso e hijastro de Ramón de Juan; llegó a Wittenoom de niño y testimonia sobre la exposición infantil · Wittenoom · 1962, 1963, 1964 (named earlier in the paragraph) (Víctor Calvo)
- QUOTES antes: «En Wittenoom, un pueblo levantado de la nada, se había utilizado muchísimo. Nosotros jugábamos con él y lo íbamos deshilachando. Nos lo metíamos en la boca. Cuando lo tocábamos salía un polvillo que lo impregnaba todo. Estábamos rodeados de amianto azul, pero no nos daba miedo. Nadie nos avisó de nada.»
- QUOTES después: «En Wittenoom, un pueblo levantado de la nada, se había utilizado muchísimo. Nosotros jugábamos con él y lo íbamos deshilachando. Nos lo metíamos en la boca. Cuando lo tocábamos salía un polvillo que lo impregnaba todo. Estábamos rodeados de amianto azul, pero no nos daba miedo. Nadie nos avisó de nada.» — Víctor Calvo · Residente de Wittenoom de niño, hijastro de minero · witness

### Cap 4 · foto 7 — arrastre

- Ancla: «Y en ese pueblo, en junio de mil novecientos sesenta y tres, nació un niño.»
- PEOPLE antes: -
- PEOPLE después: Hijo de Milagros Barroso e hijastro de Ramón de Juan; llegó a Wittenoom de niño y testimonia sobre la exposición infantil · Wittenoom · 1962, 1963, 1964 (named earlier in the paragraph) (Víctor Calvo)
- QUOTES antes: «En Wittenoom, un pueblo levantado de la nada, se había utilizado muchísimo. Nosotros jugábamos con él y lo íbamos deshilachando. Nos lo metíamos en la boca. Cuando lo tocábamos salía un polvillo que lo impregnaba todo. Estábamos rodeados de amianto azul, pero no nos daba miedo. Nadie nos avisó de nada.»
- QUOTES después: «En Wittenoom, un pueblo levantado de la nada, se había utilizado muchísimo. Nosotros jugábamos con él y lo íbamos deshilachando. Nos lo metíamos en la boca. Cuando lo tocábamos salía un polvillo que lo impregnaba todo. Estábamos rodeados de amianto azul, pero no nos daba miedo. Nadie nos avisó de nada.» — Víctor Calvo · Residente de Wittenoom de niño, hijastro de minero · witness

### Cap 4 · foto 8 — ancla

- Ancla: «Daniel trabajaba en la mina. Ramón de Juan, el amigo, hacía jornadas de dieciséis horas.»
- PEOPLE antes: Minero español en Wittenoom · Wittenoom · 1962, 1963, 1964
- PEOPLE después: Minero español, esposo de María Bernal; murió de mesotelioma después de abandonar Wittenoom · Wittenoom · 1962, 1963; Minero español, esposo de Milagros Barroso y amigo de Daniel Écija · Wittenoom · 1962, 1963, 1964 (Daniel Écija (padre), Ramón de Juan)
- QUOTES antes: «El primer día de trabajo de nuestro padre hubo una explosión y murieron varias personas. Yo creo que cuando él vio todo eso pensó que tenía que salir de allí cuanto antes, pero mi madre estaba embarazada y no tenían dinero, así que se quedaron unos meses.»
- QUOTES después: «El primer día de trabajo de nuestro padre hubo una explosión y murieron varias personas. Yo creo que cuando él vio todo eso pensó que tenía que salir de allí cuanto antes, pero mi madre estaba embarazada y no tenían dinero, así que se quedaron unos meses.» — Daniel Écija (hijo) · Hijo de minero, nacido en Wittenoom · witness

### Cap 4 · foto 9 — ancla

- Ancla: «Uno de los hijos de Daniel cuenta que el primer día de trabajo de su padre hubo una explosión y murió gente.»
- PEOPLE antes: -
- PEOPLE después: Minero español, esposo de María Bernal; murió de mesotelioma después de abandonar Wittenoom · Wittenoom · 1962, 1963 (Daniel Écija (padre))
- QUOTES antes: «El primer día de trabajo de nuestro padre hubo una explosión y murieron varias personas. Yo creo que cuando él vio todo eso pensó que tenía que salir de allí cuanto antes, pero mi madre estaba embarazada y no tenían dinero, así que se quedaron unos meses.»
- QUOTES después: «El primer día de trabajo de nuestro padre hubo una explosión y murieron varias personas. Yo creo que cuando él vio todo eso pensó que tenía que salir de allí cuanto antes, pero mi madre estaba embarazada y no tenían dinero, así que se quedaron unos meses.» — Daniel Écija (hijo) · Hijo de minero, nacido en Wittenoom · witness

### Cap 4 · foto 10 — ancla

- Ancla: «En marzo de mil novecientos sesenta y tres, Milagros Barroso dio a luz en Wittenoom a John Patrick.»
- PEOPLE antes: Esposa del minero Ramón de Juan y residente de Wittenoom · Wittenoom · 1962, 1963, 1964
- PEOPLE después: Esposa de Ramón de Juan, madre de Víctor Calvo y residente de Wittenoom · Wittenoom · 1962, 1963, 1964; Hijo de Milagros Barroso y Ramón de Juan, nacido en Wittenoom · Wittenoom · 1963, 1964 (Milagros Barroso, John Patrick de Juan)
- QUOTES antes: «El primer día de trabajo de nuestro padre hubo una explosión y murieron varias personas. Yo creo que cuando él vio todo eso pensó que tenía que salir de allí cuanto antes, pero mi madre estaba embarazada y no tenían dinero, así que se quedaron unos meses.»
- QUOTES después: «El primer día de trabajo de nuestro padre hubo una explosión y murieron varias personas. Yo creo que cuando él vio todo eso pensó que tenía que salir de allí cuanto antes, pero mi madre estaba embarazada y no tenían dinero, así que se quedaron unos meses.» — Daniel Écija (hijo) · Hijo de minero, nacido en Wittenoom · witness

### Cap 4 · foto 11 — ancla

- Ancla: «Tres meses después le tocó a María. Llegó al hospital de Wittenoom debilitada por una infección renal. El bebé era muy grande. Lo sacaron con fórceps. Le pusieron Daniel, como el padre.»
- PEOPLE antes: -
- PEOPLE después: Minero español, esposo de María Bernal; murió de mesotelioma después de abandonar Wittenoom · Wittenoom · 1962, 1963; Esposa del minero Daniel Écija, madre de Daniel y Arantxa; emigrante y residente de Wittenoom · Wittenoom · 1962, 1963 (Daniel Écija (padre), María Bernal)
- QUOTES antes: «El primer día de trabajo de nuestro padre hubo una explosión y murieron varias personas. Yo creo que cuando él vio todo eso pensó que tenía que salir de allí cuanto antes, pero mi madre estaba embarazada y no tenían dinero, así que se quedaron unos meses.»
- QUOTES después: «El primer día de trabajo de nuestro padre hubo una explosión y murieron varias personas. Yo creo que cuando él vio todo eso pensó que tenía que salir de allí cuanto antes, pero mi madre estaba embarazada y no tenían dinero, así que se quedaron unos meses.» — Daniel Écija (hijo) · Hijo de minero, nacido en Wittenoom · witness

### Cap 4 · foto 12 — arrastre

- Ancla: «Hay una foto del bautizo: siete de julio de mil novecientos sesenta y tres.»
- PEOPLE antes: -
- PEOPLE después: Minero español, esposo de María Bernal; murió de mesotelioma después de abandonar Wittenoom · Wittenoom · 1962, 1963 (named earlier in the paragraph); Esposa del minero Daniel Écija, madre de Daniel y Arantxa; emigrante y residente de Wittenoom · Wittenoom · 1962, 1963 (named earlier in the paragraph) (Daniel Écija (padre), María Bernal)
- QUOTES antes: «El primer día de trabajo de nuestro padre hubo una explosión y murieron varias personas. Yo creo que cuando él vio todo eso pensó que tenía que salir de allí cuanto antes, pero mi madre estaba embarazada y no tenían dinero, así que se quedaron unos meses.»
- QUOTES después: «El primer día de trabajo de nuestro padre hubo una explosión y murieron varias personas. Yo creo que cuando él vio todo eso pensó que tenía que salir de allí cuanto antes, pero mi madre estaba embarazada y no tenían dinero, así que se quedaron unos meses.» — Daniel Écija (hijo) · Hijo de minero, nacido en Wittenoom · witness

### Cap 4 · foto 13 — arrastre

- Ancla: «Después de esa foto, las maletas. Diez meses en Wittenoom.»
- PEOPLE antes: -
- PEOPLE después: Minero español, esposo de María Bernal; murió de mesotelioma después de abandonar Wittenoom · Wittenoom · 1962, 1963 (named earlier in the paragraph); Esposa del minero Daniel Écija, madre de Daniel y Arantxa; emigrante y residente de Wittenoom · Wittenoom · 1962, 1963 (named earlier in the paragraph) (Daniel Écija (padre), María Bernal)
- QUOTES antes: «El primer día de trabajo de nuestro padre hubo una explosión y murieron varias personas. Yo creo que cuando él vio todo eso pensó que tenía que salir de allí cuanto antes, pero mi madre estaba embarazada y no tenían dinero, así que se quedaron unos meses.»
- QUOTES después: «El primer día de trabajo de nuestro padre hubo una explosión y murieron varias personas. Yo creo que cuando él vio todo eso pensó que tenía que salir de allí cuanto antes, pero mi madre estaba embarazada y no tenían dinero, así que se quedaron unos meses.» — Daniel Écija (hijo) · Hijo de minero, nacido en Wittenoom · witness

### Cap 4 · foto 14 — arrastre

- Ancla: «Se fueron antes de que nadie les dijera nada. Nadie les había dicho nada.»
- PEOPLE antes: -
- PEOPLE después: Minero español, esposo de María Bernal; murió de mesotelioma después de abandonar Wittenoom · Wittenoom · 1962, 1963 (named earlier in the paragraph); Esposa del minero Daniel Écija, madre de Daniel y Arantxa; emigrante y residente de Wittenoom · Wittenoom · 1962, 1963 (named earlier in the paragraph) (Daniel Écija (padre), María Bernal)
- QUOTES antes: «El primer día de trabajo de nuestro padre hubo una explosión y murieron varias personas. Yo creo que cuando él vio todo eso pensó que tenía que salir de allí cuanto antes, pero mi madre estaba embarazada y no tenían dinero, así que se quedaron unos meses.»
- QUOTES después: «El primer día de trabajo de nuestro padre hubo una explosión y murieron varias personas. Yo creo que cuando él vio todo eso pensó que tenía que salir de allí cuanto antes, pero mi madre estaba embarazada y no tenían dinero, así que se quedaron unos meses.» — Daniel Écija (hijo) · Hijo de minero, nacido en Wittenoom · witness

### Cap 5 · foto 1 — ancla

- Ancla: «Diciembre de mil novecientos sesenta y seis. James Vernon anuncia que CSR cierra Wittenoom.»
- PEOPLE antes: Presidente de CSR · - · 1966
- PEOPLE después: Presidente de CSR que anunció el cierre por razones económicas · - · 1966; Empresa matriz de ABA; participó en la explotación, anunció el cierre, creó un fondo de asistencia y pagó indemnizaciones · - · - (Sir James Vernon, CSR)
- QUOTES antes: -
- QUOTES después: -

### Cap 5 · foto 2 — arrastre

- Ancla: «No lo cierra el polvo: lo cierra el dinero. El molino se apaga y el polvo se asienta sobre las cintas.»
- PEOPLE antes: -
- PEOPLE después: Presidente de CSR que anunció el cierre por razones económicas · - · 1966 (named earlier in the paragraph); Empresa matriz de ABA; participó en la explotación, anunció el cierre, creó un fondo de asistencia y pagó indemnizaciones · - · - (named earlier in the paragraph) (Sir James Vernon, CSR)
- QUOTES antes: -
- QUOTES después: -

### Cap 5 · foto 3 — arrastre

- Ancla: «Afuera, en los desfiladeros, quedan más de tres millones de toneladas de relaves. Nadie los mueve.»
- PEOPLE antes: -
- PEOPLE después: Presidente de CSR que anunció el cierre por razones económicas · - · 1966 (named earlier in the paragraph); Empresa matriz de ABA; participó en la explotación, anunció el cierre, creó un fondo de asistencia y pagó indemnizaciones · - · - (named earlier in the paragraph) (Sir James Vernon, CSR)
- QUOTES antes: -
- QUOTES después: -

### Cap 5 · foto 4 — arrastre

- Ancla: «De los hombres que habían pasado por la mina, cincuenta y nueve de cada cien se habían ido antes de cumplir seis meses.»
- PEOPLE antes: -
- PEOPLE después: Presidente de CSR que anunció el cierre por razones económicas · - · 1966 (named earlier in the paragraph); Empresa matriz de ABA; participó en la explotación, anunció el cierre, creó un fondo de asistencia y pagó indemnizaciones · - · - (named earlier in the paragraph) (Sir James Vernon, CSR)
- QUOTES antes: -
- QUOTES después: -

### Cap 5 · foto 5 — arrastre

- Ancla: «Ese mismo año, los Écija entran a su casa en Madrid.»
- PEOPLE antes: -
- PEOPLE después: Presidente de CSR que anunció el cierre por razones económicas · - · 1966 (named earlier in the paragraph); Empresa matriz de ABA; participó en la explotación, anunció el cierre, creó un fondo de asistencia y pagó indemnizaciones · - · - (named earlier in the paragraph) (Sir James Vernon, CSR)
- QUOTES antes: -
- QUOTES después: -

### Cap 5 · foto 6 — ancla

- Ancla: «Los de Juan-Barroso estuvieron unos dos años y medio en el pueblo y volvieron a Madrid en mil novecientos setenta y uno; Mercedes de Juan se quedó en Australia.»
- PEOPLE antes: Hija de Ramón de Juan, vivió en Wittenoom de niña · Wittenoom · 1962, 1963, 1964
- PEOPLE después: Hija de Ramón de Juan; vivió en Wittenoom de niña, permaneció en Australia y relata sus controles médicos · Wittenoom · 1962, 1963, 1964 (Mercedes de Juan)
- QUOTES antes: -
- QUOTES después: -

### Cap 5 · foto 7 — ancla

- Ancla: «Cerró la mina. Nadie cerró el polvo. Veinte años después, un policía iba a reconocer el nombre del pueblo en un pasaporte.»
- PEOPLE antes: -
- PEOPLE después: Agente no identificado que reconoció Wittenoom en la documentación de Daniel Écija hijo · - · - (Policía del aeropuerto)
- QUOTES antes: -
- QUOTES después: -

### Cap 5 · foto 8

- Ancla: «Mil novecientos ochenta y cinco. Un aeropuerto australiano, un puesto de control.»
- PEOPLE antes: -
- PEOPLE después: -
- QUOTES antes: «Así que de Wittenoom, ¿eh? Un sitio terrorífico.»
- QUOTES después: «Así que de Wittenoom, ¿eh? Un sitio terrorífico.» — Un policía · Agente de control de aeropuerto · 1985

### Cap 5 · foto 9 — ancla

- Ancla: «El agente abre el documento de Daniel Écija hijo, lee el lugar de nacimiento, baja la cabeza hacia el papel, vuelve a mirarlo.»
- PEOPLE antes: -
- PEOPLE después: Hijo del minero y de María Bernal, nacido en Wittenoom; productor de televisión y transmisor de la memoria familiar · Wittenoom · 1962, 1963 (Daniel Écija (hijo))
- QUOTES antes: «Así que de Wittenoom, ¿eh? Un sitio terrorífico.»
- QUOTES después: «Así que de Wittenoom, ¿eh? Un sitio terrorífico.» — Un policía · Agente de control de aeropuerto · 1985

### Cap 5 · foto 10 — arrastre

- Ancla: ««Así que de Wittenoom, ¿eh? Un sitio terrorífico», dijo el policía.»
- PEOPLE antes: -
- PEOPLE después: Hijo del minero y de María Bernal, nacido en Wittenoom; productor de televisión y transmisor de la memoria familiar · Wittenoom · 1962, 1963 (named earlier in the paragraph) (Daniel Écija (hijo))
- QUOTES antes: «Así que de Wittenoom, ¿eh? Un sitio terrorífico.»
- QUOTES después: «Así que de Wittenoom, ¿eh? Un sitio terrorífico.» — Un policía · Agente de control de aeropuerto · 1985

### Cap 5 · foto 11 — arrastre

- Ancla: «Para entonces, desde mil novecientos setenta y ocho, el gobierno del Estado venía reduciendo el pueblo y empujando a la gente a irse, por las fibras en el aire.»
- PEOPLE antes: -
- PEOPLE después: Hijo del minero y de María Bernal, nacido en Wittenoom; productor de televisión y transmisor de la memoria familiar · Wittenoom · 1962, 1963 (named earlier in the paragraph) (Daniel Écija (hijo))
- QUOTES antes: «Así que de Wittenoom, ¿eh? Un sitio terrorífico.»
- QUOTES después: «Así que de Wittenoom, ¿eh? Un sitio terrorífico.» — Un policía · Agente de control de aeropuerto · 1985

### Cap 5 · foto 12 — arrastre

- Ancla: «Entre mil novecientos ochenta y seis y mil novecientos noventa y dos demolieron edificios y cerraron los servicios básicos.»
- PEOPLE antes: -
- PEOPLE después: Hijo del minero y de María Bernal, nacido en Wittenoom; productor de televisión y transmisor de la memoria familiar · Wittenoom · 1962, 1963 (named earlier in the paragraph) (Daniel Écija (hijo))
- QUOTES antes: «Así que de Wittenoom, ¿eh? Un sitio terrorífico.»
- QUOTES después: «Así que de Wittenoom, ¿eh? Un sitio terrorífico.» — Un policía · Agente de control de aeropuerto · 1985

### Cap 5 · foto 13 — arrastre

- Ancla: «En mil novecientos noventa y tres cerró el aeropuerto. Seis años después de aquel control, su padre fue al médico.»
- PEOPLE antes: -
- PEOPLE después: Hijo del minero y de María Bernal, nacido en Wittenoom; productor de televisión y transmisor de la memoria familiar · Wittenoom · 1962, 1963 (named earlier in the paragraph) (Daniel Écija (hijo))
- QUOTES antes: «Así que de Wittenoom, ¿eh? Un sitio terrorífico.»
- QUOTES después: «Así que de Wittenoom, ¿eh? Un sitio terrorífico.» — Un policía · Agente de control de aeropuerto · 1985

### Cap 5 · foto 14 — ancla

- Ancla: «Madrid, mil novecientos noventa y uno. Daniel Écija va al médico. Le hacen pruebas. La palabra es mesotelioma.»
- PEOPLE antes: -
- PEOPLE después: Minero español, esposo de María Bernal; murió de mesotelioma después de abandonar Wittenoom · Wittenoom · 1962, 1963 (Daniel Écija (padre))
- QUOTES antes: «Ese sitio nos cambió la vida para siempre. Nosotros nos quedamos sin padre, y mi madre sin marido, por una empresa que no tuvo reparos en poner en riesgo la vida de sus trabajadores con tal de ganar dinero, y por unas autoridades que no lo impidieron.» | «Me pegué a mi marido, como una niña pequeña. Pero estaba orgullosa. Me había enamorado de ese hombre y confiaba en el futuro… aunque estuviera tan lejos. En España no teníamos nada, ninguno de los dos.»
- QUOTES después: «Ese sitio nos cambió la vida para siempre. Nosotros nos quedamos sin padre, y mi madre sin marido, por una empresa que no tuvo reparos en poner en riesgo la vida de sus trabajadores con tal de ganar dinero, y por unas autoridades que no lo impidieron.» — Daniel Écija (hijo) · Hijo de minero, nacido en Wittenoom · witness | «Me pegué a mi marido, como una niña pequeña. Pero estaba orgullosa. Me había enamorado de ese hombre y confiaba en el futuro… aunque estuviera tan lejos. En España no teníamos nada, ninguno de los dos.» — María Bernal · Esposa de minero y residente de Wittenoom · witness

### Cap 5 · foto 15 — ancla

- Ancla: «Nueve meses. Daniel muere a los cincuenta y cinco años, veintiocho años después de la foto del bautizo.»
- PEOPLE antes: -
- PEOPLE después: Minero español, esposo de María Bernal; murió de mesotelioma después de abandonar Wittenoom · Wittenoom · 1962, 1963 (Daniel Écija (padre))
- QUOTES antes: «Ese sitio nos cambió la vida para siempre. Nosotros nos quedamos sin padre, y mi madre sin marido, por una empresa que no tuvo reparos en poner en riesgo la vida de sus trabajadores con tal de ganar dinero, y por unas autoridades que no lo impidieron.» | «Me pegué a mi marido, como una niña pequeña. Pero estaba orgullosa. Me había enamorado de ese hombre y confiaba en el futuro… aunque estuviera tan lejos. En España no teníamos nada, ninguno de los dos.»
- QUOTES después: «Ese sitio nos cambió la vida para siempre. Nosotros nos quedamos sin padre, y mi madre sin marido, por una empresa que no tuvo reparos en poner en riesgo la vida de sus trabajadores con tal de ganar dinero, y por unas autoridades que no lo impidieron.» — Daniel Écija (hijo) · Hijo de minero, nacido en Wittenoom · witness | «Me pegué a mi marido, como una niña pequeña. Pero estaba orgullosa. Me había enamorado de ese hombre y confiaba en el futuro… aunque estuviera tan lejos. En España no teníamos nada, ninguno de los dos.» — María Bernal · Esposa de minero y residente de Wittenoom · witness

### Cap 5 · foto 16 — ancla

- Ancla: «Uno de los hijos dice que ese sitio les cambió la vida para siempre. Daniel no fue el primero. Para entonces, el Estado ya tenía un número.»
- PEOPLE antes: -
- PEOPLE después: Minero español, esposo de María Bernal; murió de mesotelioma después de abandonar Wittenoom · Wittenoom · 1962, 1963 (Daniel Écija (padre))
- QUOTES antes: «Ese sitio nos cambió la vida para siempre. Nosotros nos quedamos sin padre, y mi madre sin marido, por una empresa que no tuvo reparos en poner en riesgo la vida de sus trabajadores con tal de ganar dinero, y por unas autoridades que no lo impidieron.» | «Me pegué a mi marido, como una niña pequeña. Pero estaba orgullosa. Me había enamorado de ese hombre y confiaba en el futuro… aunque estuviera tan lejos. En España no teníamos nada, ninguno de los dos.»
- QUOTES después: «Ese sitio nos cambió la vida para siempre. Nosotros nos quedamos sin padre, y mi madre sin marido, por una empresa que no tuvo reparos en poner en riesgo la vida de sus trabajadores con tal de ganar dinero, y por unas autoridades que no lo impidieron.» — Daniel Écija (hijo) · Hijo de minero, nacido en Wittenoom · witness | «Me pegué a mi marido, como una niña pequeña. Pero estaba orgullosa. Me había enamorado de ese hombre y confiaba en el futuro… aunque estuviera tan lejos. En España no teníamos nada, ninguno de los dos.» — María Bernal · Esposa de minero y residente de Wittenoom · witness

### Cap 6 · foto 1

- Ancla: «En mil novecientos ochenta y nueve ya habían muerto más de quinientos antiguos trabajadores y residentes de Wittenoom.»
- PEOPLE antes: -
- PEOPLE después: -
- QUOTES antes: «Nos hacen un escáner y una prueba de función pulmonar.» | «El Gobierno dejó de contar en 2.000, pero ahora se calcula que la cifra puede ser superior a los 4.000. Y sigue aumentando. Hay hijos de funcionarios que trabajaban en el pueblo, como policías o maestros, que están ahora enfermando.»
- QUOTES después: «Nos hacen un escáner y una prueba de función pulmonar.» — Mercedes de Juan · Residente de Wittenoom de niña, hijastra de minero · witness | «El Gobierno dejó de contar en 2.000, pero ahora se calcula que la cifra puede ser superior a los 4.000. Y sigue aumentando. Hay hijos de funcionarios que trabajaban en el pueblo, como policías o maestros, que están ahora enfermando.» — Melita Markey · CEO de la Asbestos Deseases Society of Australia

### Cap 6 · foto 2 — ancla

- Ancla: «Los que seguían vivos se habían juntado diez años antes en la Asbestos Diseases Society of Australia.»
- PEOPLE antes: -
- PEOPLE después: Organización de afectados constituida para impulsar reclamos y revelar documentación sobre los riesgos · - · - (Asbestos Diseases Society of Australia)
- QUOTES antes: «Nos hacen un escáner y una prueba de función pulmonar.» | «El Gobierno dejó de contar en 2.000, pero ahora se calcula que la cifra puede ser superior a los 4.000. Y sigue aumentando. Hay hijos de funcionarios que trabajaban en el pueblo, como policías o maestros, que están ahora enfermando.»
- QUOTES después: «Nos hacen un escáner y una prueba de función pulmonar.» — Mercedes de Juan · Residente de Wittenoom de niña, hijastra de minero · witness | «El Gobierno dejó de contar en 2.000, pero ahora se calcula que la cifra puede ser superior a los 4.000. Y sigue aumentando. Hay hijos de funcionarios que trabajaban en el pueblo, como policías o maestros, que están ahora enfermando.» — Melita Markey · CEO de la Asbestos Deseases Society of Australia

### Cap 6 · foto 3 — arrastre

- Ancla: «En mil novecientos ochenta y ocho un juez leyó su veredicto: la compañía había mostrado un desprecio continuo, consciente y contumaz por la seguridad y la salud de sus trabajadores.»
- PEOPLE antes: -
- PEOPLE después: Organización de afectados constituida para impulsar reclamos y revelar documentación sobre los riesgos · - · - (named earlier in the paragraph) (Asbestos Diseases Society of Australia)
- QUOTES antes: «Nos hacen un escáner y una prueba de función pulmonar.» | «El Gobierno dejó de contar en 2.000, pero ahora se calcula que la cifra puede ser superior a los 4.000. Y sigue aumentando. Hay hijos de funcionarios que trabajaban en el pueblo, como policías o maestros, que están ahora enfermando.»
- QUOTES después: «Nos hacen un escáner y una prueba de función pulmonar.» — Mercedes de Juan · Residente de Wittenoom de niña, hijastra de minero · witness | «El Gobierno dejó de contar en 2.000, pero ahora se calcula que la cifra puede ser superior a los 4.000. Y sigue aumentando. Hay hijos de funcionarios que trabajaban en el pueblo, como policías o maestros, que están ahora enfermando.» — Melita Markey · CEO de la Asbestos Deseases Society of Australia

### Cap 6 · foto 4 — ancla

- Ancla: «Mercedes de Juan, que se quedó en Australia, entra en un escáner y después sopla en un tubo.»
- PEOPLE antes: Hija de Ramón de Juan, vivió en Wittenoom de niña · Wittenoom · 1962, 1963, 1964
- PEOPLE después: Hija de Ramón de Juan; vivió en Wittenoom de niña, permaneció en Australia y relata sus controles médicos · Wittenoom · 1962, 1963, 1964 (Mercedes de Juan)
- QUOTES antes: «Nos hacen un escáner y una prueba de función pulmonar.» | «El Gobierno dejó de contar en 2.000, pero ahora se calcula que la cifra puede ser superior a los 4.000. Y sigue aumentando. Hay hijos de funcionarios que trabajaban en el pueblo, como policías o maestros, que están ahora enfermando.»
- QUOTES después: «Nos hacen un escáner y una prueba de función pulmonar.» — Mercedes de Juan · Residente de Wittenoom de niña, hijastra de minero · witness | «El Gobierno dejó de contar en 2.000, pero ahora se calcula que la cifra puede ser superior a los 4.000. Y sigue aumentando. Hay hijos de funcionarios que trabajaban en el pueblo, como policías o maestros, que están ahora enfermando.» — Melita Markey · CEO de la Asbestos Deseases Society of Australia

### Cap 6 · foto 5 — ancla

- Ancla: ««Nos hacen un escáner y una prueba de función pulmonar», dice Mercedes.»
- PEOPLE antes: -
- PEOPLE después: Hija de Ramón de Juan; vivió en Wittenoom de niña, permaneció en Australia y relata sus controles médicos · Wittenoom · 1962, 1963, 1964 (Mercedes de Juan)
- QUOTES antes: «Nos hacen un escáner y una prueba de función pulmonar.» | «El Gobierno dejó de contar en 2.000, pero ahora se calcula que la cifra puede ser superior a los 4.000. Y sigue aumentando. Hay hijos de funcionarios que trabajaban en el pueblo, como policías o maestros, que están ahora enfermando.»
- QUOTES después: «Nos hacen un escáner y una prueba de función pulmonar.» — Mercedes de Juan · Residente de Wittenoom de niña, hijastra de minero · witness | «El Gobierno dejó de contar en 2.000, pero ahora se calcula que la cifra puede ser superior a los 4.000. Y sigue aumentando. Hay hijos de funcionarios que trabajaban en el pueblo, como policías o maestros, que están ahora enfermando.» — Melita Markey · CEO de la Asbestos Deseases Society of Australia

### Cap 6 · foto 6 — arrastre

- Ancla: «Las fibras pueden causar mesotelioma, asbestosis y cáncer de pulmón.»
- PEOPLE antes: -
- PEOPLE después: Hija de Ramón de Juan; vivió en Wittenoom de niña, permaneció en Australia y relata sus controles médicos · Wittenoom · 1962, 1963, 1964 (named earlier in the paragraph) (Mercedes de Juan)
- QUOTES antes: «Nos hacen un escáner y una prueba de función pulmonar.» | «El Gobierno dejó de contar en 2.000, pero ahora se calcula que la cifra puede ser superior a los 4.000. Y sigue aumentando. Hay hijos de funcionarios que trabajaban en el pueblo, como policías o maestros, que están ahora enfermando.»
- QUOTES después: «Nos hacen un escáner y una prueba de función pulmonar.» — Mercedes de Juan · Residente de Wittenoom de niña, hijastra de minero · witness | «El Gobierno dejó de contar en 2.000, pero ahora se calcula que la cifra puede ser superior a los 4.000. Y sigue aumentando. Hay hijos de funcionarios que trabajaban en el pueblo, como policías o maestros, que están ahora enfermando.» — Melita Markey · CEO de la Asbestos Deseases Society of Australia

### Cap 6 · foto 7 — ancla

- Ancla: «La cuenta oficial se detuvo. «El gobierno dejó de contar en 2.000, pero ahora se calcula que la cifra puede ser superior a los 4.000. Y sigue aumentando», dice Melita Markey.»
- PEOPLE antes: CEO de la Asbestos Deseases Society of Australia · - · -
- PEOPLE después: CEO de la Asbestos Diseases Society of Australia; aporta una estimación de mortalidad superior al recuento periodístico más repetido · - · - (Melita Markey)
- QUOTES antes: «Nos hacen un escáner y una prueba de función pulmonar.» | «El Gobierno dejó de contar en 2.000, pero ahora se calcula que la cifra puede ser superior a los 4.000. Y sigue aumentando. Hay hijos de funcionarios que trabajaban en el pueblo, como policías o maestros, que están ahora enfermando.»
- QUOTES después: «Nos hacen un escáner y una prueba de función pulmonar.» — Mercedes de Juan · Residente de Wittenoom de niña, hijastra de minero · witness | «El Gobierno dejó de contar en 2.000, pero ahora se calcula que la cifra puede ser superior a los 4.000. Y sigue aumentando. Hay hijos de funcionarios que trabajaban en el pueblo, como policías o maestros, que están ahora enfermando.» — Melita Markey · CEO de la Asbestos Deseases Society of Australia

### Cap 6 · foto 8 — arrastre

- Ancla: «Están enfermando hijos de policías y de maestros que trabajaron en el pueblo.»
- PEOPLE antes: -
- PEOPLE después: CEO de la Asbestos Diseases Society of Australia; aporta una estimación de mortalidad superior al recuento periodístico más repetido · - · - (named earlier in the paragraph) (Melita Markey)
- QUOTES antes: «Nos hacen un escáner y una prueba de función pulmonar.» | «El Gobierno dejó de contar en 2.000, pero ahora se calcula que la cifra puede ser superior a los 4.000. Y sigue aumentando. Hay hijos de funcionarios que trabajaban en el pueblo, como policías o maestros, que están ahora enfermando.»
- QUOTES después: «Nos hacen un escáner y una prueba de función pulmonar.» — Mercedes de Juan · Residente de Wittenoom de niña, hijastra de minero · witness | «El Gobierno dejó de contar en 2.000, pero ahora se calcula que la cifra puede ser superior a los 4.000. Y sigue aumentando. Hay hijos de funcionarios que trabajaban en el pueblo, como policías o maestros, que están ahora enfermando.» — Melita Markey · CEO de la Asbestos Deseases Society of Australia

### Cap 6 · foto 9 — arrastre

- Ancla: «Mientras los enfermos se contaban a sí mismos, el Estado decidió qué hacer con el pueblo: borrarlo.»
- PEOPLE antes: -
- PEOPLE después: CEO de la Asbestos Diseases Society of Australia; aporta una estimación de mortalidad superior al recuento periodístico más repetido · - · - (named earlier in the paragraph) (Melita Markey)
- QUOTES antes: «Nos hacen un escáner y una prueba de función pulmonar.» | «El Gobierno dejó de contar en 2.000, pero ahora se calcula que la cifra puede ser superior a los 4.000. Y sigue aumentando. Hay hijos de funcionarios que trabajaban en el pueblo, como policías o maestros, que están ahora enfermando.»
- QUOTES después: «Nos hacen un escáner y una prueba de función pulmonar.» — Mercedes de Juan · Residente de Wittenoom de niña, hijastra de minero · witness | «El Gobierno dejó de contar en 2.000, pero ahora se calcula que la cifra puede ser superior a los 4.000. Y sigue aumentando. Hay hijos de funcionarios que trabajaban en el pueblo, como policías o maestros, que están ahora enfermando.» — Melita Markey · CEO de la Asbestos Deseases Society of Australia

### Cap 6 · foto 10

- Ancla: «Junio de dos mil siete; otras fuentes dicen dos mil seis. Wittenoom es abolido formalmente.»
- PEOPLE antes: -
- PEOPLE después: -
- QUOTES antes: «un fin a un período oscuro en la historia de nuestro Estado.» | «La minería en las gargantas ha dejado una contaminación que solo puede describirse como vergonzosa, incluso para los estándares de la época. Es casi increíble que la propiedad de los vertederos de relaves se haya transferido, por defecto, al Gobierno del Estado.» | «Tenemos el deber de prevenir una mayor propagación de los relaves de asbesto para reducir el riesgo de mesotelioma para los residentes, los visitantes actuales y las generaciones futuras»
- QUOTES después: «un fin a un período oscuro en la historia de nuestro Estado.» — Gobierno de Australia Occidental · Gobierno estatal · 2022 | «La minería en las gargantas ha dejado una contaminación que solo puede describirse como vergonzosa, incluso para los estándares de la época. Es casi increíble que la propiedad de los vertederos de relaves se haya transferido, por defecto, al Gobierno del Estado.» — Larry Graham · Presidente del Comité Selecto sobre Wittenoom · 1994 | «Tenemos el deber de prevenir una mayor propagación de los relaves de asbesto para reducir el riesgo de mesotelioma para los residentes, los visitantes actuales y las generaciones futuras» — Mark Nevill · ex-MP y autor del informe · 1992

### Cap 6 · foto 11 — ancla

- Ancla: «Le quitan el nombre a las señales de la carretera y lo sacan de los mapas. El gobierno de Australia Occidental habla de «el fin de un período oscuro en la historia de nuestro Estado».»
- PEOPLE antes: -
- PEOPLE después: Gobierno estatal que impulsó el cierre del pueblo, restringe el acceso y es demandado por BNTAC; incluye al Gabinete y al gobierno de Court mencionados en las decisiones sobre remediación · - · - (Gobierno de Australia Occidental)
- QUOTES antes: «un fin a un período oscuro en la historia de nuestro Estado.» | «La minería en las gargantas ha dejado una contaminación que solo puede describirse como vergonzosa, incluso para los estándares de la época. Es casi increíble que la propiedad de los vertederos de relaves se haya transferido, por defecto, al Gobierno del Estado.» | «Tenemos el deber de prevenir una mayor propagación de los relaves de asbesto para reducir el riesgo de mesotelioma para los residentes, los visitantes actuales y las generaciones futuras»
- QUOTES después: «un fin a un período oscuro en la historia de nuestro Estado.» — Gobierno de Australia Occidental · Gobierno estatal · 2022 | «La minería en las gargantas ha dejado una contaminación que solo puede describirse como vergonzosa, incluso para los estándares de la época. Es casi increíble que la propiedad de los vertederos de relaves se haya transferido, por defecto, al Gobierno del Estado.» — Larry Graham · Presidente del Comité Selecto sobre Wittenoom · 1994 | «Tenemos el deber de prevenir una mayor propagación de los relaves de asbesto para reducir el riesgo de mesotelioma para los residentes, los visitantes actuales y las generaciones futuras» — Mark Nevill · ex-MP y autor del informe · 1992

### Cap 6 · foto 12 — arrastre

- Ancla: «Quince años antes, en mil novecientos noventa y dos, una investigación parlamentaria había recomendado limpiar los relaves. El gobierno rechazó esas recomendaciones.»
- PEOPLE antes: -
- PEOPLE después: Gobierno estatal que impulsó el cierre del pueblo, restringe el acceso y es demandado por BNTAC; incluye al Gabinete y al gobierno de Court mencionados en las decisiones sobre remediación · - · - (named earlier in the paragraph) (Gobierno de Australia Occidental)
- QUOTES antes: «un fin a un período oscuro en la historia de nuestro Estado.» | «La minería en las gargantas ha dejado una contaminación que solo puede describirse como vergonzosa, incluso para los estándares de la época. Es casi increíble que la propiedad de los vertederos de relaves se haya transferido, por defecto, al Gobierno del Estado.» | «Tenemos el deber de prevenir una mayor propagación de los relaves de asbesto para reducir el riesgo de mesotelioma para los residentes, los visitantes actuales y las generaciones futuras»
- QUOTES después: «un fin a un período oscuro en la historia de nuestro Estado.» — Gobierno de Australia Occidental · Gobierno estatal · 2022 | «La minería en las gargantas ha dejado una contaminación que solo puede describirse como vergonzosa, incluso para los estándares de la época. Es casi increíble que la propiedad de los vertederos de relaves se haya transferido, por defecto, al Gobierno del Estado.» — Larry Graham · Presidente del Comité Selecto sobre Wittenoom · 1994 | «Tenemos el deber de prevenir una mayor propagación de los relaves de asbesto para reducir el riesgo de mesotelioma para los residentes, los visitantes actuales y las generaciones futuras» — Mark Nevill · ex-MP y autor del informe · 1992

### Cap 6 · foto 13 — ancla

- Ancla: ««La minería en los desfiladeros ha dejado una contaminación que solo puede describirse como vergonzosa, incluso para los estándares de la época», dijo Larry Graham.»
- PEOPLE antes: Presidente de comité parlamentario · - · 1994
- PEOPLE después: Presidente del comité parlamentario sobre Wittenoom; denunció la contaminación y la transferencia de los relaves al Estado · - · 1994 (Larry Graham)
- QUOTES antes: «un fin a un período oscuro en la historia de nuestro Estado.» | «La minería en las gargantas ha dejado una contaminación que solo puede describirse como vergonzosa, incluso para los estándares de la época. Es casi increíble que la propiedad de los vertederos de relaves se haya transferido, por defecto, al Gobierno del Estado.» | «Tenemos el deber de prevenir una mayor propagación de los relaves de asbesto para reducir el riesgo de mesotelioma para los residentes, los visitantes actuales y las generaciones futuras»
- QUOTES después: «un fin a un período oscuro en la historia de nuestro Estado.» — Gobierno de Australia Occidental · Gobierno estatal · 2022 | «La minería en las gargantas ha dejado una contaminación que solo puede describirse como vergonzosa, incluso para los estándares de la época. Es casi increíble que la propiedad de los vertederos de relaves se haya transferido, por defecto, al Gobierno del Estado.» — Larry Graham · Presidente del Comité Selecto sobre Wittenoom · 1994 | «Tenemos el deber de prevenir una mayor propagación de los relaves de asbesto para reducir el riesgo de mesotelioma para los residentes, los visitantes actuales y las generaciones futuras» — Mark Nevill · ex-MP y autor del informe · 1992

### Cap 6 · foto 14 — arrastre

- Ancla: «Le parecía casi increíble que la propiedad de los depósitos de relaves hubiera pasado, por defecto, al gobierno estatal.»
- PEOPLE antes: -
- PEOPLE después: Presidente del comité parlamentario sobre Wittenoom; denunció la contaminación y la transferencia de los relaves al Estado · - · 1994 (named earlier in the paragraph) (Larry Graham)
- QUOTES antes: «un fin a un período oscuro en la historia de nuestro Estado.» | «La minería en las gargantas ha dejado una contaminación que solo puede describirse como vergonzosa, incluso para los estándares de la época. Es casi increíble que la propiedad de los vertederos de relaves se haya transferido, por defecto, al Gobierno del Estado.» | «Tenemos el deber de prevenir una mayor propagación de los relaves de asbesto para reducir el riesgo de mesotelioma para los residentes, los visitantes actuales y las generaciones futuras»
- QUOTES después: «un fin a un período oscuro en la historia de nuestro Estado.» — Gobierno de Australia Occidental · Gobierno estatal · 2022 | «La minería en las gargantas ha dejado una contaminación que solo puede describirse como vergonzosa, incluso para los estándares de la época. Es casi increíble que la propiedad de los vertederos de relaves se haya transferido, por defecto, al Gobierno del Estado.» — Larry Graham · Presidente del Comité Selecto sobre Wittenoom · 1994 | «Tenemos el deber de prevenir una mayor propagación de los relaves de asbesto para reducir el riesgo de mesotelioma para los residentes, los visitantes actuales y las generaciones futuras» — Mark Nevill · ex-MP y autor del informe · 1992

### Cap 6 · foto 15 — ancla

- Ancla: ««Tenemos el deber de impedir una mayor dispersión de los relaves de asbesto», dijo Mark Nevill, por los residentes, por los visitantes, por las generaciones futuras.»
- PEOPLE antes: Líder de investigación parlamentaria · - · 1992
- PEOPLE después: Responsable, junto con Alan Rogers, de la investigación parlamentaria sobre Wittenoom; defendió la limpieza de los relaves · - · 1992 (Mark Nevill)
- QUOTES antes: «un fin a un período oscuro en la historia de nuestro Estado.» | «La minería en las gargantas ha dejado una contaminación que solo puede describirse como vergonzosa, incluso para los estándares de la época. Es casi increíble que la propiedad de los vertederos de relaves se haya transferido, por defecto, al Gobierno del Estado.» | «Tenemos el deber de prevenir una mayor propagación de los relaves de asbesto para reducir el riesgo de mesotelioma para los residentes, los visitantes actuales y las generaciones futuras»
- QUOTES después: «un fin a un período oscuro en la historia de nuestro Estado.» — Gobierno de Australia Occidental · Gobierno estatal · 2022 | «La minería en las gargantas ha dejado una contaminación que solo puede describirse como vergonzosa, incluso para los estándares de la época. Es casi increíble que la propiedad de los vertederos de relaves se haya transferido, por defecto, al Gobierno del Estado.» — Larry Graham · Presidente del Comité Selecto sobre Wittenoom · 1994 | «Tenemos el deber de prevenir una mayor propagación de los relaves de asbesto para reducir el riesgo de mesotelioma para los residentes, los visitantes actuales y las generaciones futuras» — Mark Nevill · ex-MP y autor del informe · 1992

### Cap 6 · foto 16 — arrastre

- Ancla: «En dos mil dieciséis, los documentos dicen por qué los relaves siguen donde están: no porque no se pueda, sino por lo que cuesta. En dos mil veintitrés, los estudios del Estado sobre hasta dónde llega la contaminación ya estaban desactualizados. Borraron el nombre del mapa. El polvo no leía mapas.»
- PEOPLE antes: -
- PEOPLE después: Responsable, junto con Alan Rogers, de la investigación parlamentaria sobre Wittenoom; defendió la limpieza de los relaves · - · 1992 (named earlier in the paragraph) (Mark Nevill)
- QUOTES antes: «un fin a un período oscuro en la historia de nuestro Estado.» | «La minería en las gargantas ha dejado una contaminación que solo puede describirse como vergonzosa, incluso para los estándares de la época. Es casi increíble que la propiedad de los vertederos de relaves se haya transferido, por defecto, al Gobierno del Estado.» | «Tenemos el deber de prevenir una mayor propagación de los relaves de asbesto para reducir el riesgo de mesotelioma para los residentes, los visitantes actuales y las generaciones futuras»
- QUOTES después: «un fin a un período oscuro en la historia de nuestro Estado.» — Gobierno de Australia Occidental · Gobierno estatal · 2022 | «La minería en las gargantas ha dejado una contaminación que solo puede describirse como vergonzosa, incluso para los estándares de la época. Es casi increíble que la propiedad de los vertederos de relaves se haya transferido, por defecto, al Gobierno del Estado.» — Larry Graham · Presidente del Comité Selecto sobre Wittenoom · 1994 | «Tenemos el deber de prevenir una mayor propagación de los relaves de asbesto para reducir el riesgo de mesotelioma para los residentes, los visitantes actuales y las generaciones futuras» — Mark Nevill · ex-MP y autor del informe · 1992

### Cap 7 · foto 1

- Ancla: «No se ha retirado una sola palada de asbesto. ¿Quién va a sacar la primera palada de esa tierra?»
- PEOPLE antes: -
- PEOPLE después: -
- QUOTES antes: «Todavía lloro por mi País, pero eso está arraigado en mí, simplemente no puedo alejarme de él.»
- QUOTES después: «Todavía lloro por mi País, pero eso está arraigado en mí, simplemente no puedo alejarme de él.» — Maitland Parker · Dueño tradicional Banjima · witness

### Cap 7 · foto 2

- Ancla: «Los relaves del vertedero de Colonial se van con el agua.»
- PEOPLE antes: -
- PEOPLE después: -
- QUOTES antes: «Todavía lloro por mi País, pero eso está arraigado en mí, simplemente no puedo alejarme de él.»
- QUOTES después: «Todavía lloro por mi País, pero eso está arraigado en mí, simplemente no puedo alejarme de él.» — Maitland Parker · Dueño tradicional Banjima · witness

### Cap 7 · foto 3

- Ancla: «Un informe técnico lo marcó como la fuente principal y la vía del asbesto: la erosión, los lechos de arroyo, las pozas, las llanuras de inundación hacia el río Fortescue.»
- PEOPLE antes: -
- PEOPLE después: -
- QUOTES antes: «Todavía lloro por mi País, pero eso está arraigado en mí, simplemente no puedo alejarme de él.»
- QUOTES después: «Todavía lloro por mi País, pero eso está arraigado en mí, simplemente no puedo alejarme de él.» — Maitland Parker · Dueño tradicional Banjima · witness

### Cap 7 · foto 4

- Ancla: «Fibras azules que el agua deja donde se seca.»
- PEOPLE antes: -
- PEOPLE después: -
- QUOTES antes: «Todavía lloro por mi País, pero eso está arraigado en mí, simplemente no puedo alejarme de él.»
- QUOTES después: «Todavía lloro por mi País, pero eso está arraigado en mí, simplemente no puedo alejarme de él.» — Maitland Parker · Dueño tradicional Banjima · witness

### Cap 7 · foto 5

- Ancla: «En dos mil veintiuno, una nota ambiental registró fibras en canales de arroyos fuera de la zona marcada como contaminada.»
- PEOPLE antes: -
- PEOPLE después: -
- QUOTES antes: «Todavía lloro por mi País, pero eso está arraigado en mí, simplemente no puedo alejarme de él.»
- QUOTES después: «Todavía lloro por mi País, pero eso está arraigado en mí, simplemente no puedo alejarme de él.» — Maitland Parker · Dueño tradicional Banjima · witness

### Cap 7 · foto 6

- Ancla: «El mismo informe advirtió que, sin intervención, el aporte de asbesto a la cuenca del Fortescue puede seguir durante cientos de años.»
- PEOPLE antes: -
- PEOPLE después: -
- QUOTES antes: «Todavía lloro por mi País, pero eso está arraigado en mí, simplemente no puedo alejarme de él.»
- QUOTES después: «Todavía lloro por mi País, pero eso está arraigado en mí, simplemente no puedo alejarme de él.» — Maitland Parker · Dueño tradicional Banjima · witness

### Cap 7 · foto 7 — ancla

- Ancla: «Es tierra Banjima. En dos mil veintitrés, Marcos Orellana visitó Australia y se sentó con Maitland Parker, un anciano Banjima.»
- PEOPLE antes: Anciano Banjima, activista y víctima de mesotelioma · Wittenoom · 2023, 2024
- PEOPLE después: Anciano Banjima que denunció el daño a su territorio, habló con el relator de la ONU y murió de mesotelioma · Wittenoom · 2023, 2024; Relator especial de la ONU sobre sustancias tóxicas y derechos humanos; visitó Australia y entrevistó a Maitland Parker · Wittenoom · 2023, 2024 (Maitland Parker, Marcos Orellana)
- QUOTES antes: «Todavía lloro por mi País, pero eso está arraigado en mí, simplemente no puedo alejarme de él.»
- QUOTES después: «Todavía lloro por mi País, pero eso está arraigado en mí, simplemente no puedo alejarme de él.» — Maitland Parker · Dueño tradicional Banjima · witness

### Cap 7 · foto 8 — arrastre

- Ancla: ««Todavía lloro por mi territorio, pero eso está arraigado en mí; simplemente no puedo alejarme de él», dijo Parker.»
- PEOPLE antes: -
- PEOPLE después: Anciano Banjima que denunció el daño a su territorio, habló con el relator de la ONU y murió de mesotelioma · Wittenoom · 2023, 2024 (named earlier in the paragraph); Relator especial de la ONU sobre sustancias tóxicas y derechos humanos; visitó Australia y entrevistó a Maitland Parker · Wittenoom · 2023, 2024 (named earlier in the paragraph) (Maitland Parker, Marcos Orellana)
- QUOTES antes: «Todavía lloro por mi País, pero eso está arraigado en mí, simplemente no puedo alejarme de él.»
- QUOTES después: «Todavía lloro por mi País, pero eso está arraigado en mí, simplemente no puedo alejarme de él.» — Maitland Parker · Dueño tradicional Banjima · witness

### Cap 7 · foto 9 — ancla

- Ancla: «Maitland Parker murió de mesotelioma en dos mil veinticuatro.»
- PEOPLE antes: Anciano Banjima, activista y víctima de mesotelioma · Wittenoom · 2023, 2024
- PEOPLE después: Anciano Banjima que denunció el daño a su territorio, habló con el relator de la ONU y murió de mesotelioma · Wittenoom · 2023, 2024 (Maitland Parker)
- QUOTES antes: «Todavía lloro por mi País, pero eso está arraigado en mí, simplemente no puedo alejarme de él.»
- QUOTES después: «Todavía lloro por mi País, pero eso está arraigado en mí, simplemente no puedo alejarme de él.» — Maitland Parker · Dueño tradicional Banjima · witness

### Cap 7 · foto 10 — ancla

- Ancla: «Dos años después, Gordon Legal presentó en nombre de BNTAC un proceso contra Australia Occidental en el Tribunal Federal.»
- PEOPLE antes: -
- PEOPLE después: Corporación Banjima cuya junta decidió impulsar acciones legales para obtener la limpieza y que demanda al Estado · - · 2026; Estudio jurídico que inició el proceso contra Australia Occidental en representación de BNTAC; es también fuente de afirmaciones de la parte demandante · - · -; Órgano judicial ante el que se presentó el proceso de BNTAC; el pool no contiene una sentencia sobre esa demanda · - · - (Banjima Native Title Aboriginal Corporation, Gordon Legal, Tribunal Federal)
- QUOTES antes: «Todavía lloro por mi País, pero eso está arraigado en mí, simplemente no puedo alejarme de él.»
- QUOTES después: «Todavía lloro por mi País, pero eso está arraigado en mí, simplemente no puedo alejarme de él.» — Maitland Parker · Dueño tradicional Banjima · witness

### Cap 7 · foto 11 — arrastre

- Ancla: «Nadie ha empezado a limpiar.»
- PEOPLE antes: -
- PEOPLE después: Corporación Banjima cuya junta decidió impulsar acciones legales para obtener la limpieza y que demanda al Estado · - · 2026 (named earlier in the paragraph); Estudio jurídico que inició el proceso contra Australia Occidental en representación de BNTAC; es también fuente de afirmaciones de la parte demandante · - · - (named earlier in the paragraph); Órgano judicial ante el que se presentó el proceso de BNTAC; el pool no contiene una sentencia sobre esa demanda · - · - (named earlier in the paragraph) (Banjima Native Title Aboriginal Corporation, Gordon Legal, Tribunal Federal)
- QUOTES antes: «es consciente del 'grave problema de salud y seguridad pública' en torno a Wittenoom y continúa trabajando en opciones a largo plazo para el área y las tierras circundantes.»
- QUOTES después: «es consciente del 'grave problema de salud y seguridad pública' en torno a Wittenoom y continúa trabajando en opciones a largo plazo para el área y las tierras circundantes.» — Gobierno de Australia Occidental · Gobierno estatal

### Cap 7 · foto 12

- Ancla: «En los accesos al pueblo y desfiladero hay bloqueos.»
- PEOPLE antes: -
- PEOPLE después: -
- QUOTES antes: «es consciente del 'grave problema de salud y seguridad pública' en torno a Wittenoom y continúa trabajando en opciones a largo plazo para el área y las tierras circundantes.»
- QUOTES después: «es consciente del 'grave problema de salud y seguridad pública' en torno a Wittenoom y continúa trabajando en opciones a largo plazo para el área y las tierras circundantes.» — Gobierno de Australia Occidental · Gobierno estatal

### Cap 7 · foto 13 — ancla

- Ancla: «El gobierno de Australia Occidental habla de un «grave problema de salud y seguri»
- PEOPLE antes: -
- PEOPLE después: Gobierno estatal que impulsó el cierre del pueblo, restringe el acceso y es demandado por BNTAC; incluye al Gabinete y al gobierno de Court mencionados en las decisiones sobre remediación · - · - (Gobierno de Australia Occidental)
- QUOTES antes: «es consciente del 'grave problema de salud y seguridad pública' en torno a Wittenoom y continúa trabajando en opciones a largo plazo para el área y las tierras circundantes.»
- QUOTES después: «es consciente del 'grave problema de salud y seguridad pública' en torno a Wittenoom y continúa trabajando en opciones a largo plazo para el área y las tierras circundantes.» — Gobierno de Australia Occidental · Gobierno estatal
