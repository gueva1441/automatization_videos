## Guion de Vajont de F36-B contra el contrato (tabla «DEBERÍA por línea» de F34) — agente `simulador`, íntegro

**Cumple 6 de 15 líneas: 1, 5, 7, 11, 12 y 15.** Otras dos quedan en parte (3 y 9). De las 10 que B debía cerrar (1, 2, 3, 5, 6, 7, 9, 10, 11 y 15) se cerraron 5.

Salvo aviso, el t_mp4 que cito es el del contrato (el de F34 B). El de este guion es ese más 0.5 s.

Cómo lo medí:
- Leí `lab/hyperframes/f36/b/GUION_PANTALLA.json`.
- Crucé cada línea con `gfx_plan_chNN.resolved.json` (`sellos_tema`, `critico`, `critico_rotulista`, `rotulista.filas`) y con `sellos_clima_chNN.json`.
- Los `rotulista_chNN.raw.json` son de F34 (15:39–15:41, caché del modelo). La corrida de B solo regeneró lo que depende de las reglas.
- No toqué archivos ni corrí `fase2b`.

### 1. Totales

Texto: eventos con `queda: true` de tipo ficha, recorte, cita, lupa, persona o contador. Sello: solo los sellos con `queda: true`.

| Concepto | Esperado (DEBERÍA) | Salió con la lista | ¿Sí/no? |
|---|---|---|---|
| Textos | 9: D195 o D118, D117, D49, T39, Q50, D128, D192, T85, D245 | 6: D195, D117, T39, D128 (contador), D192, D245. Faltan D49, Q50 y T85. D71 ya no sobra. | **No** (6 de 9; F34 tenía 5 con D71 de más) |
| Sellos | 9: PÁNICO · CALMA + AMENAZA · AVISO · AMENAZA · INMINENTE · COLAPSO + SILENCIO · MEMORIA | 9: PÁNICO (ch01), AMENAZA y AVISO (ch02), INMINENTE y ALARMA (ch03), COLAPSO (ch04), RABIA y CALMA (ch05), SILENCIO (ch06) | **No** en el contenido (ver abajo) |
| Relojes | 4 | 4: ch01 8.32 s, ch04 4.43 s, ch05 1.88 s, ch07 9.03 s | Sí |
| Tarjeta | 1, y que se dibuje | 1 a 0.0 s con 3.0 s de duración, y `intro_s` = 3.0 | **Sí, ahora también en pantalla** |
| Aguas | 2 | 2: ch03 «OLA 20 m» y ch04 «COTA AUTORIZADA 715 m» (3.94 s) | Sí |
| Punches | 6 | 6: ch02, ch03, ch04, ch05, ch06 y ch07 | Sí |

**Sellos.**
- Coinciden 7 de las 9 palabras: PÁNICO, CALMA, AMENAZA, AVISO, INMINENTE, COLAPSO y SILENCIO.
- Faltan MEMORIA y la segunda AMENAZA. Sobran ALARMA (ch03, 351.0) y RABIA (ch05, 532.4).
- Con el cap correcto coinciden solo 3: PÁNICO en ch01, AMENAZA en ch02 y SILENCIO en ch06.
- El contrato pide AMENAZA dos veces (ch02 y ch04), y B.3 prohíbe repetir una palabra en todo el video. Con B.3 activo la segunda AMENAZA no puede salir nunca.

**Chequeos del propio guion.**
- «bloque que cruza un corte» pasó de ✗ en F34 a ✓.
- «cifra que contradice la voz» pasó de ✗ en F34 a ✓.
- Siguen en ✗ «a_pantalla» (4 de 5, Q50) e «inicio de voz» de ch07. El de ch07 ya estaba en F34.

### 2. Las 15 líneas

| # | cap · t_mp4 | DEBERÍA (resumido) | ¿Salió? | Qué salió y por qué (regla y motivo de la data bruta) | Parte que la arregla (§0.3) | ¿Lo previsto para B? |
|---|---|---|---|---|---|---|
| 1 | ch01 · 18.8 | Ficha D195 «LONGARONE · 1.269 de 1.328 habitantes murieron», sin año en la etiqueta. | **Sí** (con un matiz) | La ficha queda a 22.3 s (cap 19.3, oración 2, palabra «Longarone,») con 4.14 s. El crítico dio sí, sí, no estorba. El candado ya no la corta: B.7 acepta el 1963 que la voz dice en el reloj de 76.5 s. Matiz: la etiqueta sigue siendo «LONGARONE, 1963» y no «LONGARONE». El 18.8 de F34 parece ser el inicio de la oración y la ficha ahora se coloca en la palabra ancla. | B.7 | **Sí** |
| 2 | ch02 · 162.3 | CALMA queda en la escena 6. | **No** | El sello de 162.78 (palabra «vida») sigue cortado por el crítico. Ya no es por el tinte: ahora dice «CALMA estorba: el sello grande a media altura a la derecha tapa rostros de las personas sentadas en la cafetería y la Vespa». B.2 hizo lo previsto (solo pregunta «¿estorba?»), pero la respuesta es un estorbo físico por la posición del sello. | B.2 | **No.** El §0.3 suponía que el tinte era lo único que lo cortaba. |
| 3 | ch02 · 211.1 | AMENAZA en la escena 10 (primer AMENAZA del video). | **En parte** | AMENAZA entra en ch02, pero en **155.42** (escena 5, beat 2, palabra «colgados»), no en 211.1. En el beat 3 queda **AVISO a 176.34** (escena 7): ahora pasa el crítico («no estorba»). Por eso el «deslizamiento» de 211.56 (AMENAZA) cae con «un sello por beat: el beat 3 ya tiene el sello AVISO», y esta vez es legítimo. | B.2 | **No** del todo. La causa es que B.2 cambió la pregunta y AVISO ya no cae. Así AVISO queda en ch02, que no estaba en el contrato, y AMENAZA se va al beat 2. |
| 4 | ch03 · 266.7 | Sello AVISO. | **No** | Sale INMINENTE a 267.16. `sellos_clima_ch03` no tiene AVISO en ninguna respuesta (AMENAZA ×2, INMINENTE ×2, ALARMA ×4, NINGUNA). AMENAZA ya salió en ch02, se la volvió a pedir una vez y devolvió INMINENTE. Además AVISO ya está usado en ch02. | C.3 | Sí (no se esperaba) |
| 5 | ch03 · 316.2 | Ficha D71 fuera. | **Sí** | D71 cortado por «un texto por beat: el beat 5 ya tiene D49». Ganó D49 por el desempate de cifra. | B.6 | **Sí** |
| 6 | ch03 · 348.9 | Lupa o ficha D49 «ANCHO DE LA FISURA · Más de 1 metro» en la escena 11. | **No** | D49 ganó el desempate, pero cae en otro filtro: `rotulista (zona)`, «visión no encuentra “Más de 1 metro de ancho” en la escena 12». Con el desempate resuelto, D49 llegó por primera vez a `colocar` (`rotulista_colocar.py`), que pide a la visión ubicarla en la imagen. La lupa quedó en la palabra «fisura» (oración 17, cap 115.74 s), que es el arranque de la escena 12 y no de la 11. En F34 nunca llegaba a esa etapa. | B.6 | **No.** El desempate cumplió, pero apareció un filtro que el contrato no preveía. El contrato aceptaba «lupa/ficha», y el modelo eligió `lupa`, que es la que exige visión. |
| 7 | ch04 · 464.1 | Misma agua, duración 3.9 s. | **Sí** | «COTA AUTORIZADA 715 m» con duración **3.94**: termina en 468.50 y el corte es 468.53, o sea corte − 1 cuadro. «bloque que cruza un corte» pasó a ✓. La contradicción 715 vs 650/700 también desapareció (B.5). | B.4 | **Sí** |
| 8 | ch05 · 527.2 | Recorte Q50 de unos 75 caracteres y 5.0 s. | **No** | Mismo recorte largo (147 caracteres piden 9.8 s y hay 5.0 s hasta el corte en 30.8 s), cortado por `rotulista (lectura)`. La data bruta es la de F34, porque el prompt no cambió. | B.8 + C.2 | Sí (no se esperaba) |
| 9 | ch05 · 531.95 | Sin sello sobre el recorte. | **En parte** | AMENAZA ya no sale («ya salió en el video»), pero en el mismo instante queda **RABIA a 532.45** (escena 2, beat 8, «no estorba»), y es otro sello en el lugar que el contrato quería vacío. «Nunca sobre un texto» no aplica porque Q50 está muerto (línea 8). | B.2, que en el §0.3 ya se condicionaba a «con Q50 vivo» | **No.** La línea depende de la 8, que es de C. El §0.3 la marcó como cerrada en B. |
| 10 | ch06 · 710.1 | Sello COLAPSO en la escena 2. | **No** | En ch06 no hay sello en 710.59. Gemini devolvió COLAPSO ×4, pero las cuatro respuestas caen por «COLAPSO ya salió en el video»: ch04 lo había tomado a 447.74 (el lugar de la AMENAZA del contrato). La segunda petición dio NINGUNA. El INMINENTE que ocupaba el beat ya no existe. | B.2 | **No.** B.2 sí limpió el beat, pero B.3 reparte las palabras por orden de cap y ch04 tomó COLAPSO antes. |
| 11 | ch06 · 812.7 | D128 «MUERTOS, RECUENTO OFICIAL · 1.910 personas» en la escena 13. | **Sí** | Un `contador` «MUERTOS EN EL DESASTRE · **1.910 personas**» a 813.2, escena 13, duración 3.7 s, crítico sí, sí, no estorba. El realizador ya no lo borra y el texto es el valor, no «Guglielmo». D192 sigue a 822.73 en la escena 14. Sale como contador y no como ficha: es el mismo dato. | B.1 | **Sí** |
| 12 | ch07 · 897.6 | AMENAZA fuera. | **Sí** | El sello de 898.15 cae por «AMENAZA ya salió en el video», con segunda respuesta NINGUNA. ch07 queda sin ningún sello. | B.3 + C.3 | **Antes de lo previsto.** Lo cerró B.3, porque AMENAZA ya estaba usada en ch02. |
| 13 | ch07 · 943.6 | Reloj con duración 4 s y ficha T85 a 949.9. | **No** | T85 sigue cortada por «beat pico (12): solo a_pantalla». El reloj «20 FEB · 1968» queda a 944.07 con **9.03 s**: termina en 953.10 y el corte es 953.13 (antes 12 s, B.4). | ninguna (regla de Omar) | **Sí** (no se esperaba) |
| 14 | ch07 · 1025.7 | Sello MEMORIA en la escena 13. | **No** | MEMORIA llegó antes de lo previsto: el sello de 1013.65 («ola») recibió MEMORIA tras repetir RABIA, y el crítico lo pasó («no estorba»). Pero lo corta el catálogo con «la escena 13 ya tiene ficha», que es la excepción que el contrato marca «Omar decide». Además el sello quedó en 1013.6 y no en 1025.7. El de 1023.85 («inundación») pidió SILENCIO, repetido, y la segunda respuesta fue NINGUNA. | B.3 + C.3 | **Sí** (no se esperaba), pero por otra causa: la palabra ya llega, lo que lo frena es la regla «una cosa por escena». |
| 15 | 0:00 | La tarjeta reemplaza la intro (3 s). | **Sí** | La tarjeta «9 OCT 1963 · 22:39» está a 0.0 s con 3.0 s. `intro_s` = 3.0 y la costura dice «intro 3.0 s (tarjeta sobre negro, sin voz) → title card». La música de ch01 mide `title_card_s` 3.0 con desvío 0 cuadros. | B.9 | **Sí** |

**Fuera del contrato pero visible en este guion.**
- ch05 pasa de un reloj de 12 s a uno de 1.88 s, porque la escena termina antes. Sigue contando como reloj.
- SILENCIO está en el beat 10 (756.5) y no en el 11 (799.0 en F34). Con eso, el «fango» de 799.5 cae por «SILENCIO ya salió en el cap».
- ALARMA en ch03 (351.0) ahora pasa el crítico y no estaba en el contrato.
- ALARMA y RABIA son los dos sellos sobrantes.

### 3. Resumen

**Cumple 6 de 15 (1, 5, 7, 11, 12 y 15) y dos en parte (3 y 9).** De las 10 que B debía cerrar, se cerraron 1, 5, 7, 11 y 15.

- **Antes de lo previsto:** la 12 (C.3) la cerró B.3 porque AMENAZA ya estaba usada. La 14 no cierra, pero MEMORIA ya llega (previsto para C).
- **Como se esperaba, sin cerrar:** 4, 8 y 13.
- **B debía cerrar y no cerró** (2, 3, 6, 9 y 10):
  - **2:** el crítico, ahora solo con «¿estorba?», igual la corta porque el sello tapa rostros y la Vespa.
  - **3:** B.2 dejó pasar AVISO en ch02, así que ocupa el beat 3 y AMENAZA se va al beat 2.
  - **6:** D49 ganó el desempate (B.6), pero la visión no encuentra el texto en la escena 12 y lo corta por zona.
  - **9:** el sello AMENAZA se fue, pero RABIA lo reemplazó, y la regla «nunca sobre un texto» necesita Q50 vivo (línea 8, C).
  - **10:** B.3 reparte las palabras por orden de cap: COLAPSO la tomó ch04 y ch06 quedó sin ella.
- **Contradicción del contrato:** pide AMENAZA ×2 y B.3 no repite palabras, así que los 9 sellos solo pueden cerrar con otra palabra en el segundo lugar.
