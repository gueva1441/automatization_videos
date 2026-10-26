## Guion de Vajont de F36-A contra el contrato (tabla «DEBERÍA por línea» de F34) — agente `simulador`, íntegro

**Cumple 0 de 15 líneas. Ninguna se resolvió antes de lo previsto.** Es lo esperado: después de A no se esperaba ninguna.

**El guion de A es idéntico al de F34 B.**
- Los 210 eventos son iguales campo por campo.
- También son iguales todos los metadatos de cada cap y los `chequeos`.
- Lo único que cambia es `generado`, `tiempos_s`, `mezcla.segundos` (13.3 contra 11.3) y `costos.claude_rotulista_usd` (0.0 contra 0.4633). Esto último sale de la caché del modelo.
- La comparación también da igual contra `lab/hyperframes/f36/a/GUION_base.json`. `diff_guion.txt` dice «0 líneas distintas».
- Los datos brutos (`rotulista_chNN.raw.json`, `sellos_clima_chNN.json`, `gfx_critic_*.json`) son de F34 B, de las 15:39–15:45. Solo los `gfx_plan_chNN.resolved.json` son de la corrida de A, de las 17:07–17:08.

### 1. Totales

Conté como texto solo los de tipo ficha, recorte, cita, lupa, persona y contador con `queda: true`. Como sello conté solo los sellos con `queda: true`.

| Concepto | Esperado (DEBERÍA) | Salió con la lista | ¿Sí/No? |
|---|---|---|---|
| Textos | 9: D195 o D118, D117, D49, T39, Q50, D128, D192, T85, D245 | 5: D117, **D71** (sobra), T39, D192, D245. Coinciden 4 de 9; faltan D195/D118, D49, Q50, D128 y T85. | **No** (5 de 9) |
| Sellos | 9: PÁNICO · CALMA + AMENAZA · AVISO · AMENAZA · INMINENTE · COLAPSO + SILENCIO · MEMORIA | 7: PÁNICO (ch01), AMENAZA (ch03, 266.7), AMENAZA (ch04, 447.2), AMENAZA (ch05, 531.9), INMINENTE (ch05), SILENCIO (ch06), AMENAZA (ch07, 897.6) | **No** (7 de 9) |
| Relojes | 4 | 4: ch01 8.3 s, ch04 4.4 s, ch05 12 s, ch07 12 s | Sí (cantidad) |
| Tarjeta | 1 | 1 en el plan (0:00, 3.0 s), pero no se dibuja: `intro_s` sigue en 2.5 | Sí en el plan, **no** en pantalla |
| Aguas | 2 | 2: ch03 «OLA 20 m» y ch04 «COTA AUTORIZADA 715 m» | Sí |
| Punches | 6 | 6: ch02, ch03, ch04, ch05, ch06 y ch07 | Sí |

- **Sellos que coinciden:** 4 de 9, que son PÁNICO, AMENAZA de ch04, INMINENTE y SILENCIO.
- **Sellos con otra palabra o sobrantes:** AMENAZA de ch03 (debería ser AVISO), AMENAZA de ch05 y AMENAZA de ch07.
- **Sellos que faltan:** CALMA, AMENAZA de ch02, AVISO, COLAPSO y MEMORIA.

### 2. Las 15 líneas

Siempre «salió» quiere decir que el guion cumple la columna DEBERÍA. En todas las filas salió **No**. En «qué salió», los números de caracteres, escenas y duraciones salen de los eventos del guion y de los datos brutos.

| # | cap · t_mp4 | DEBERÍA (resumido) | Salió | Qué salió y por qué (regla y motivo de la data bruta) | Parte que lo arregla (§0.3) |
|---|---|---|---|---|---|
| 1 | ch01 · 18.8 | Ficha D195 «LONGARONE · 1.269 de 1.328 habitantes murieron», sin año | No | La ficha existe, pero con la etiqueta «LONGARONE, 1963» y cortada. Regla: rotulista (candado). Motivo: «no están en el texto fuente de D195: ['1963']». En `rotulista_ch01.raw.json` D195 es el único bloque, tras 2 intentos. | B.7 |
| 2 | ch02 · 162.3 | CALMA queda | No | Sello CALMA cortado por el crítico: «El tinte de 'muerte' contradice la escena de vida… y repite lo que ya se ve». Gemini sí devolvió CALMA en `sellos_clima_ch02.json`. | B.2 |
| 3 | ch02 · 211.1 | AMENAZA en la escena 10 | No | El sello «deslizamiento» (AMENAZA) en 211.1 está cortado por catálogo: «un sello por beat: el beat 3 ya tiene el sello AVISO». Pero AVISO (175.8) ya había caído por el crítico: «El tinte de 'agua'… no tiene relación con el contenido visual». O sea, un sello ya cortado ocupó el beat. Hay otros 4 «deslizamiento»/«montaña»/«cicatriz» cortados por la misma razón. | B.2 (crítico antes del reparto) |
| 4 | ch03 · 266.7 | Sello AVISO | No | Sale AMENAZA, con el crítico en «suma». En `sellos_clima_ch03.json` Gemini devuelve AMENAZA ×2, INMINENTE, ALARMA ×2 y NINGUNA; nunca AVISO. | C.3 |
| 5 | ch03 · 316.2 | Ficha D71 fuera | No | D71 «L'UNITÀ · Diario del Partido Comunista Italiano» sigue en 316.2, 4.9 s, con el crítico en sí/sí/no estorba. Ganó el desempate por orden de oración (sentence 13). | B.6 |
| 6 | ch03 · 348.9 | Lupa D49 «ANCHO DE LA FISURA · Más de 1 metro» | No | La lupa D49 está en 348.9, escena 11, lectura 2.7 s, pero cortada. Regla: rotulista (cantidad). Motivo: «un texto por beat: el beat 5 ya tiene D71». En el raw, D71 y D49 son los dos rank 1 del beat 5. | B.6 (D49 tiene cifra) |
| 7 | ch04 · 464.1 | Agua COTA AUTORIZADA, dur 3.9 | No | La agua 715 m sale con dur 4.5. El corte de la escena 7 es en 468.03 s y 464.06 + 4.5 = 468.56, así que lo cruza 0.53 s. Pasó el filtro sin mirar el corte. | B.4 |
| 8 | ch05 · 527.2 | Recorte Q50 literal, ~75 caracteres, 5.0 s | No | El recorte salió largo, con 147 caracteres que piden 9.8 s cuando hay 5.0 s hasta el corte de la escena (30.8 s). Regla: rotulista (lectura). En el raw, la etiqueta y el texto de Q50 miden 43 y 105 caracteres. | B.8 + C.2 |
| 9 | ch05 · 531.95 | Sello AMENAZA fuera | No | El sello AMENAZA queda en 531.9 s (dur 2.5, «crítico: suma») en la misma escena 2 que el recorte Q50 de la línea 8. Q50 está cortado, así que la regla «nunca sobre un texto» no lo saca. | B.2 (orden), una vez que Q50 viva |
| 10 | ch06 · 710.1 | Sello COLAPSO en la escena 2 | No | El sello de 710.1 es INMINENTE y está cortado por el crítico: «contradice la imagen… desplome ya ocurrido». Los otros 9 sellos del beat 10 están cortados por catálogo: «el beat 10 ya tiene el sello INMINENTE». En `sellos_clima_ch06.json` Gemini devolvió COLAPSO ×4. | B.2 |
| 11 | ch06 · 812.7 | Ficha «MUERTOS, RECUENTO OFICIAL · 1.910 personas» (D128) | No | Hay un `contador` de D128 con `texto` «Guglielmo» (la palabra del ancla, no el 1.910), cortado por el realizador: «contador de una cifra que dice la voz». El raw sí traía D128 como cifra «1.910 personas». D192 queda en 822.2, pero en la escena 14, no en la 13. | B.1 |
| 12 | ch07 · 897.6 | Sello AMENAZA fuera | No | El sello AMENAZA queda en 897.6 (dur 2.5, «crítico: suma»). Es el cuarto del video, junto con ch03, ch04 y ch05. | B.3 + C.3 |
| 13 | ch07 · 943.6 | Reloj con dur 4; ficha T85 en 949.9 | No | El reloj «20 FEB · 1968» sale con dur 12.0: 84.7 + 12 = 96.7 contra el corte de la escena 7 en 93.77 s, o sea que cruza el corte. La ficha T85 está cortada en 943.6, el mismo instante del reloj. Regla: rotulista (cantidad). Motivo: «beat pico (12): solo a_pantalla». | **Ninguna** (regla de Omar 14:22). Queda cortada hasta `--plan-edit`. El reloj de 12 s es B.4. |
| 14 | ch07 · 1025.7 | Sello MEMORIA | No | No hay ningún sello en 1025.7. Los de 1013 y 1023 («ola», «inundación») caen por «la escena 13 ya tiene ficha». En `sellos_clima_ch07.json` Gemini no devuelve MEMORIA, solo NINGUNA, AMENAZA, ALARMA, RABIA y SILENCIO. | B.3 + C.3 |
| 15 | 0:00 | Tarjeta que reemplaza la intro (3 s de negro con fecha-hora, todo +0.5 s) | No | La tarjeta «9 OCT 1963 · 22:39» está a 0.0 s con 3.0 s de dur, pero `intro_s` sigue en 2.5 y el title card del ch01 arranca a 2.5 s. La costura dice «intro 2.5 s (primer cuadro congelado) → title card». | B.9 |

**Sobre el reloj de ch05:** el reloj de 596.5 (dur 12.0, en la escena 9 que termina en 89.43 s del cap) también pasa el corte siguiente. Lo calculé a mano con las mismas cifras; no está en tu contrato. Entra en B.4.

### 3. Resumen

**El guion cumple 0 de las 15 líneas, y ninguna se resolvió antes de lo previsto.** Los totales que coinciden (4 relojes, 2 aguas, 6 punches, tarjeta en el plan) ya coincidían en F34 y no dependen de estas líneas. Por parte, B debería cerrar 1, 2, 3, 5, 6, 7, 9, 10, 11 y 15. Las líneas 4, 8, 12 y 14 quedan para C. La 13 no la arregla ninguna parte.
