# F10 — Corrida de ajuste del guion de Ycuá Bolaños → **NO cumple el criterio: PARADA**

**Rama:** `f10-integracion-v3`. **Pedido:** OK de Omar con ajuste (F10 §4.3 → §4.4): una corrida de ajuste con 7 notas
y, **solo si** el resultado cumple «cierre en cita, 11:25 presente, fecha ≤ 1 por cap y duras ≤ 12», seguir directo a
producción. **No se cumplió → no se siguió a producción** (no hay audio, m03, assemble ni render de `f8s1-ycua-bolanos`).
**Decisiones:** `DECISIONES_F10.md` D19–D25. **Para leer:** `NARRACION_ycua_ajuste.md` (la corrida de ajuste) contra
`NARRACION_ycua_v1.md` (la primera); `ajuste_chequeos.json`.

## 1. Qué se hizo
- **Notas 1–6 → al guionista** como `instrucciones_guionista` (el canal que m01b ya lee).
- **Lo estructural, en la escaleta** (validada de nuevo, 0 duras):
  - D192 (327 oficiales) sale de pantalla y pasa a ser el dato central del beat 9 (la morgue), que ya lleva contador: se dice una vez en la voz y el contador sube en ese momento;
  - apoyo para los caps cortos: Blas Cristaldo hora por hora (T19, T20; T25, T27) y Tatiana Gabaglio adulta (Q03);
  - el cierre del último beat apunta a la cita de Liz Torres (Q77).
- **Reglas nuevas** (código, con tests):
  - fecha literal: máximo 1 por cap, y la fecha completa una sola vez en el video;
  - un evento contado con «ese domingo / esa noche…» cuenta como dicho;
  - «fue una masacre», «un peligro que nadie veía» y «esperar un milagro» pasan a la lista de juicios.
- **Nota 7 (título):** tres propuestas sin «400», la primera queda provisional en `topics_db` (la de 4c se guarda en `video_title_4c`):
  1. **Ycuá Bolaños: el domingo que cerraron las puertas** (provisional)
  2. Ycuá Bolaños: 327 muertos detrás de puertas cerradas
  3. Ycuá Bolaños: la orden de cerrar las puertas
- **Corrida:** `fase1_5 --v3 --only m01b` (guionista best_of_2 → editor → partición → juez).
- **B1 adelantado** (lo necesita cualquier render; D25):
  - el render disperso ya no deja una ventana del 100 % del cap;
  - nuevo validador de cuadro congelado (`script_engine/freeze_check.py`).
  - Hay tests, pero no se probó en un render.

## 2. Resultado contra el criterio de Omar
| criterio | resultado |
|---|---|
| cierre en la cita de Liz Torres | ✅ la última frase es «Soy la vida de muchas personas que cayeron sobre mi cuerpo, me salvaron la vida» |
| «11:25» en la voz | ✅ |
| fecha literal ≤ 1 por cap | ❌ cap 5: «1 de agosto» dos veces. Además, aunque «1 de agosto de 2004» completa sale una sola vez (cap 1), «1 de agosto» se repite en los caps 2, 4 y 5 y «ese domingo» no aparece nunca: la nota 2 se incumple más de lo que mide la regla (que permite una por cap) |
| duras ≤ 12 | ❌ **26** (la primera versión tenía 20) |

**Lo grave:**
- **El guionista se salteó los beats 4 y 5: el cap 3 quedó vacío.** El total bajó a 1,127 palabras; por cap: 126 · 238 · **0** · 223 · 215 · 216 · 109.
- `fase1_5` dio PASS igual. Ahora la partición frena la cadena si un cap queda sin narración (`ParticionError`, con test), para que un cap vacío nunca llegue al audio.

**Lo que sí mejoró:**
- el cierre;
- la hora del pico;
- los juicios viejos desaparecieron;
- el 327 se dice una sola vez.

**Lo que empeoró o sigue:**
- cuatro párrafos de relleno;
- ids declarados que no suenan literales;
- repeticiones entre caps;
- el gancho adelanta una cita;
- el cap 7 sigue corto (109 palabras contra un mínimo de 119).

**Mi lectura:**
- Seis notas largas como instrucciones del guionista, más las reglas de siempre, le cargaron demasiado el prompt: el puntaje de los dos intentos sale con 28–29 duras, contra 23–26 en la primera corrida.
- Las notas de cierre y de hora sí las cumplió; perdió estructura (beats salteados).

## 3. Costos
| tramo | US$ |
|---|---|
| Corrida de ajuste (guionista 2 intentos + editor + títulos) | 0.38 |
| Guion acumulado de Ycuá (v1 + ajuste) | 1.26 |
| Con el research del topic | 2.25 |

Producción: US$ 0 (no se empezó).

## 4. Para decidir (Omar / analista)
1. **Otra corrida** con el prompt más liviano: en vez de las 6 notas como instrucciones, la escaleta ya ajustada (cierre, contador, apoyos) y solo dos notas cortas (fecha y 11:25)?
2. **O una pasada del editor solo sobre los caps flojos** (`m01d_particion.regenerate_cap`, sin volver a escribir todo), partiendo de la v1, que tenía todos los caps?
3. **O aceptar la v1 + arreglos a mano** de cierre, hora y fecha, y seguir a producción?

## 5. Veredicto del revisor-handoff
VEREDICTO: CUMPLE CON OBSERVACIONES. La parada es correcta y las cifras coinciden. El guion en sí NO cumple el criterio de Omar y se declara así.

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1.1 | Cierre = contradicción pericia vs testimonios, pregunta final, última frase de Liz Torres | OK | 01b_narration.json termina en «Soy la vida de muchas personas que cayeron sobre mi cuerpo, me salvaron la vida». La pregunta final está en el texto. La contradicción de las 3 puertas no la verifiqué línea por línea. |
| 1.2 | Fecha completa una sola vez; después «ese domingo» | PARCIAL | «1 de agosto de 2004» aparece una vez, en el cap 1. Pero «1 de agosto» sale además en caps 2, 4 y 5 (dos veces en el 5). «ese domingo» aparece 0 veces. El reporte lo declara solo como falla del cap 5. |
| 1.3 | «11:25» en voz | OK | Aparece una vez, en el cap 5. |
| 1.4 | Fuera juicios/relleno | PARCIAL | Las tres frases ya no están (0 coincidencias) y se agregaron a la lista de juicios (guion_v3_reglas). Pero el editor marca 4 párrafos de relleno (beats 6, 7, 10 y 11). El reporte lo declara. |
| 1.5 | Caps 4, 5 y 7 al mínimo con Blas Cristaldo y Tatiana adulta | PARCIAL | Los apoyos entraron a la escaleta (T19, T20, T25, T27, Q03). El cap 7 queda en 109 palabras contra mínimo 119. Los caps 4 y 7 declaran ids que no suenan literales (Q34, D47, D195). |
| 1.6 | 327 en voz una vez + contador, fuera de reservados | OK | «327» aparece una vez, en el cap 5. D192 pasó al beat 9, que ya tenía contador. Que el contador sincronice con ese momento depende de producción, que no existe. |
| 1.7 | Título: 3 sin «400», el primero provisional | OK, con detalle | D22 y la entrada en topics_db tienen el título «Ycuá Bolaños: el domingo que cerraron las puertas». El `hook`, el `mystery` y el `angle` de topics_db todavía dicen «400 personas»; la nota pedía solo título. |
| 2 | Criterio medido bien y NO seguir a producción | OK | ajuste_chequeos.json coincide con 01b_narration.json: cierre y 11:25 en true, fecha ≤1 por cap en false, duras en 26 (tope 12). No existen output/audio/f8s1-ycua-bolanos, 03_visual.json ni data/scripts/f8s1-ycua-bolanos.json. Hay PARADA en D23 y en el reporte. |
| 3 | Cifras del reporte | OK | Palabras por cap 126, 238, 0, 223, 214, 216, 109. El reporte dice 215 para el cap 5: diferencia de 1, irrelevante. Costos: 0.1872 + 0.1874 + 0.0032 = 0.378, que da los 0.38 del reporte. Acumulado v1 0.8848 + 0.378 = 1.263, que da los 1.26 del reporte. Cap 3 vacío confirmado. |
| 4 | FRENOS §3 | OK | En el diff 7a81632..HEAD no hay evidence.py, m02_5, tts_normalizer, m07, fase2a/2b, m03_visual ni config.py. Se tocó gfx_sparse.py (F10 B1, 24 líneas). |
| 5 | Tests | OK | Suite pedida: 459 passed. Suite amplia: 576 passed y 5 failed, que son exactamente las 5 previas esperadas (3 de 01b_pauses y 2 de m03_merge_timing). No corrí nada que llame APIs pagas. |
| 6 | No se commitearon los archivos prohibidos | OK | diag_234_cap4.py, lexico_propuestas.json y misterio.json siguen como modificados sin commitear. topics_db_pre_f7b.json sigue sin trackear. config.py no aparece. |

**Sobre el punto 4 (gfx_sparse.py).** La justificación es válida. El handoff §4.4 ordena el B1 antes del render, y el B1 es el bug de cuadro congelado de ch05 de Orleans. El cambio es acotado. Si la fusión de ventanas deja ≥95% del cap en una sola ventana, se vuelve a fusionar con gap 0.

Dos reparos:
- El handoff decía «cortar siempre en cuts/ aunque la ventana sea 100%». La implementación hace otra cosa: re-fusiona con gap 0. Es una interpretación propia, y el reporte lo dice («no se probó en un render»).
- Se adelantó trabajo de producción dentro de una corrida de ajuste que terminó en PARADA. El diff y los tests lo cubren, pero el cambio quedó sin validar en render.

**Otras observaciones.**
- El reporte presenta como falla solo la fecha del cap 5. En realidad la fecha literal se repite en 4 caps y nunca se usó la paráfrasis «ese domingo». La nota 2 está más incumplida de lo que el reporte sugiere.
- El código nuevo cumple: el guion_v3_reglas ahora detecta las fechas repetidas y ParticionError frena un cap vacío, ambos con tests.
- Las 26 duras salen de los chequeos guardados. No re-corrí el juez porque llama a la API.

**Fuera de alcance.** Ninguno en el diff. lab/ESTADO_SESION.md está actualizado, como pide el CLAUDE.md.

**Riesgos que el contrato no cubre.**
- El guionista saltea beats cuando se le cargan muchas notas. Las tres salidas del reporte (prompt liviano, regenerate_cap, v1 más arreglos a mano) siguen abiertas para Omar.
- topics_db conserva «400» en hook, mystery y angle.
- El B1 nunca se probó en un render real.

Respuesta del autor (después del veredicto): la observación de las fechas quedó corregida en §2 del reporte (fila de fecha). El «400» de hook/mystery/angle no lo toqué (la nota 7 pedía solo el título): queda para Omar junto con la decisión de cómo seguir (§4).
