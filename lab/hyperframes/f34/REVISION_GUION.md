# REVISIÓN DEL GUION DE PANTALLA — Vajont, tanda F34 (analista, 2026-10-26)

> **Correcciones al contrato (26-10 18:05, después de F36 B):** ver `lab/hyperframes/f36/RESPUESTA_C.md` — línea 2 aceptada cortada (tapa rostros); línea 3 vale en 155.4 o 211.1; ch03 AVISO y **ch04 ALARMA** (no AMENAZA ×2); línea 6 D49 como **ficha** (regla B.10: lupa sin detalle → ficha); línea 14 pendiente de Omar («una por escena» en escenas largas); línea 13 pendiente de Omar (excepción al pico).


Fuente: `output/f8s3-vajont-f30/GUION_PANTALLA.json` (regenerado en F34 B, commit 2f04030), `_fase2b_work/rotulista_chNN.raw.json`, `F34_REPORT.md` §B.2 (tabla del simulador, verificada línea por línea contra la data bruta). Segundos = t_mp4 del guion actual (con intro de 2.5 s). **Render: NO con este guion. SÍ después de las ediciones de abajo (todas por `--plan-edit`, sin volver a llamar al modelo) + que la tarjeta se dibuje.**

## Semáforo
| cap | antes (F32) | ahora | qué falta |
|---|---|---|---|
| ch01 | 🔴 | 🟡 | texto del gancho (cortado por un año inventado) |
| ch02 | 🔴 | 🟡 | sellos CALMA / AMENAZA (crítico y orden de filtros) |
| ch03 | 🟡 | 🟡 | fisura D49 perdió contra L'Unità D71 por orden; AVISO salió AMENAZA |
| ch04 | 🟡 | 🟢 | agua cruza el corte 0.53 s |
| ch05 | 🟡 | 🟡 | recorte Q50 (147 caracteres, no cabe) |
| ch06 | 🟢 | 🟡 | D128 (1.910 muertos) borrado por bug viejo del realizador; COLAPSO perdido por orden de filtros |
| ch07 | 🟢 | 🟡 | T85 (11 imputados) cortado por «pico solo a_pantalla»; MEMORIA nunca sale de Gemini |

Lo que ya está bien y no se toca: tarjeta 0:00 (en el plan), 4 relojes, 2 aguas, 6 punches, música alineada (0 cuadros), D117, T39, D192, D245, PÁNICO, INMINENTE, SILENCIO.

## DEBERÍA por línea (edición por `--plan-edit`; nada de modelo)
| # | cap · t_mp4 | hoy | DEBERÍA | fuente / por qué |
|---|---|---|---|---|
| 1 | ch01 · 18.8 | ficha D195 cortada por candado («1963» no está en D195) | ficha **«LONGARONE · 1.269 de 1.328 habitantes murieron»** (sin año en la etiqueta), ancla «…es una niña de Longarone», escena única, dur = lectura 3.3 s | D195. El año lo inventó el modelo; quitarlo pasa el candado. Voto del analista: D195 retiene más que D118 (266 m); Omar decide. Alternativa: ficha D118 «LA PRESA DEL VAJONT · 266 m de alto» en 0:10. |
| 2 | ch02 · 162.3 | sello CALMA cortado por el crítico («el tinte de muerte contradice la escena de vida») | **CALMA queda** en 162.3 (escena 6) | El crítico objeta la forma del sello (tinte oscuro), no la palabra; eso es de F31b. |
| 3 | ch02 · 211.1 | sin sello en el beat 3 (AVISO 175.8 cortado por el crítico) | sello **AMENAZA** en 211.1 (escena 10, voz «deslizamiento») | Primer AMENAZA del video, donde la montaña empieza a moverse. |
| 4 | ch03 · 266.7 | sello AMENAZA | sello **AVISO** | Pontesei es el aviso; AMENAZA ya va en ch02. |
| 5 | ch03 · 316.2 | ficha D71 «L'UNITÀ · Diario del Partido Comunista Italiano» | **fuera** | Dato débil; decisión 14:36: la ficha de ch03 es la fisura. |
| 6 | ch03 · 348.9 | lupa D49 cortada («el beat 5 ya tiene D71») | lupa/ficha **«ANCHO DE LA FISURA · Más de 1 metro»** en 348.9 (escena 11, 104.2–115.7 del cap; lectura 2.7 s) | D49; Omar 14:36. |
| 7 | ch04 · 464.1 | agua COTA AUTORIZADA 715 m, dur 4.5 (termina 0.53 s después del corte 468.03) | misma agua, **dur 3.9** (derivado: corte − inicio − margen) | El chequeo «715 vs 650/700» es falso positivo (niveles anteriores). |
| 8 | ch05 · 527.2 | recorte Q50 cortado por lectura (147 caracteres, 9.8 s; hay 5.0 s) | recorte **«CARTA DEL MUNICIPIO DE ERTO Y CASSO · "en continua aprensión y en continua alarma"»** (cita literal, ~75 caracteres, 5.0 s) | Q50 literal (candado de cita). Ancla correcta: «Desde el dos de octubre, los avisos se multiplicaron». |
| 9 | ch05 · 531.95 | sello AMENAZA (misma escena que el recorte) | **fuera** | «nunca un sello sobre un texto»; ch05 se queda con INMINENTE 660.1. |
| 10 | ch06 · 710.1 | sello INMINENTE cortado por el crítico («ya se ve el desplome») | sello **COLAPSO** en 710.1 (escena 2) | Gemini devolvió COLAPSO 4 veces; lo tapó INMINENTE, que después cayó. |
| 11 | ch06 · 812.7 | contador D128 borrado por el realizador (y con texto «Guglielmo») | **ficha «MUERTOS, RECUENTO OFICIAL · 1.910 personas»** en 812.7 (escena 13, 126.9–137.6 del cap; dur 4 s = lectura) | D128; la voz nunca dice 1.910. Como ficha esquiva el bug del contador. D192 sigue en 822.2 (escena 14): dos datos, dos escenas. |
| 12 | ch07 · 897.6 | sello AMENAZA | **fuera** | Cap del juicio; AMENAZA no es el clima; cuarto AMENAZA del video. |
| 13 | ch07 · 943.6 | reloj 20 FEB 1968 (dur 12) + ficha T85 cortada en el mismo instante | reloj queda, **dur 4**; ficha **«REMISIÓN A JUICIO · 11 imputados»** en 949.9 (oración 12 «El juez no aceptó la palabra imprevisible», misma escena 7, 84.5–93.8 del cap; lectura 2.5 s) | T85. Primero la fecha, después el hecho; no se pisan. |
| 14 | ch07 · 1025.7 | nada | sello **MEMORIA** en 1025.7 (oración 25 «…decidió que Longarone no debía saber», escena 13) | Gemini nunca devuelve MEMORIA. Excepción a «una por escena»: la escena 13 dura 40 s y la ficha D245 terminó en 1006. Omar decide. |
| 15 | 0:00 | tarjeta «9 OCT 1963 · 22:39» en el plan pero **no se dibuja** (el mp4 arranca con 2.5 s de primer cuadro congelado) | la tarjeta **reemplaza** la intro: 3 s de negro con fecha-hora (`title_dur`), luego la primera imagen; todo se corre +0.5 s | Omar 14:36. Única línea que necesita código, no edición. |

Resultado esperado tras las ediciones: **9 textos** (D195 o D118, D117, D49, T39, Q50, D128, D192, T85, D245); **9 sellos** (PÁNICO · CALMA + AMENAZA · AVISO · AMENAZA · INMINENTE · COLAPSO + SILENCIO · MEMORIA); 4 relojes + tarjeta; 2 aguas; 6 punches.

## Bugs para código (tanda aparte, después de ver v6; no frenan el render)
1. `gfx_realizador.finalizar` borra todo `count_up`, también el del rotulista (desde F29); y el contador toma como texto la palabra del ancla («Guglielmo») en vez del valor.
2. Orden de filtros de sellos: «un sello por beat» corre **antes** del crítico; un sello que el crítico después saca ya ocupó el beat (ch02 ×2, ch06). El crítico tiene que ir antes del reparto.
3. Sellos: Gemini inclina a AMENAZA (×4) y nunca devuelve MEMORIA; A.4 solo prohíbe repetir dentro del cap. Falta «no repetir en el video» (o tope 1 por palabra) y pedir la palabra de cierre explícitamente.
4. Agua (A.5) y reloj fijan duración sin mirar el corte de escena siguiente (agua ch04 0.53 s; relojes de 12 s).
5. Chequeo `contradicciones`: compara una cota con niveles anteriores del embalse (falso positivo 715 vs 650/700).
6. «Un texto por beat» con dos rank 1 elige por orden de oración, no por valor (D71 ganó a D49). Falta criterio: a_pantalla → rank → **dato con cifra** → oración.
7. Candado del gancho: el modelo pone el año del hecho en la etiqueta y el candado lo corta aunque la voz lo diga en el video (1963 a 1:16). Para el gancho, el candado debería aceptar lo que la voz dice en todo el video (mismo pool).
8. El modelo (Sonnet) escribió 147 caracteres pese a «UNA línea corta» (Q50): poner tope de caracteres en el formato de salida, no solo en la instrucción.

## De quién es cada falla
- **Analista (yo):** esperé D118, CALMA/AVISO/MEMORIA sin simular qué devuelve el modelo (el mismo error de las reglas en papel); el desempate «un texto por beat» sin criterio de valor; no pedí el arreglo del contador en F34 aunque estaba en la ENTRADA del 26; las líneas 14:28/14:36 de DECISIONES no estaban en el disco (CC tenía razón; ya están).
- **CC:** contó 6 textos / 8 sellos (eran 5 / 7; lo corrigió el simulador); ESTADO sin actualizar al cierre (lo atajó el revisor); el orden «reparto antes del crítico» de sellos; 5 procesos viejos vivos.
- **Modelos:** Sonnet inventó «1963» y escribió 147 caracteres; Gemini da AMENAZA a todo.
- **Omar:** nada.
