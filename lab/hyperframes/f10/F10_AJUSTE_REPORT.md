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
| fecha literal ≤ 1 por cap | ❌ cap 5: «1 de agosto» dos veces |
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
(pendiente: se pega íntegro abajo)
