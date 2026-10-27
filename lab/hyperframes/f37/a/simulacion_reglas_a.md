# F37 A — simulación en seco de las reglas del papel (agente `simulador`, íntegro)

Nota de CC: esta simulación corrió **después** de programar A (antes de programar, CC hizo su propia corrida en seco:
`seco_validacion_sobre_f36.txt`). Va como verificación independiente.

Simulación en seco de las reglas A (F37) sobre el papel de F36 de Vajont. Solo lectura y sin llamar a ningún modelo. Usé mi propio parser de años, numerales y nombres, y después contrasté con las funciones de CC (`momentos`, `autor_en`, `voz_no_lo_dice`).

**Resultado.** Mis resultados coinciden con la corrida de CC en todo. Hay cuatro puntos frágiles de lectura, en la sección 3.

**Insumos**
- Respuesta de F36 sin reintento: `data/scripts/_steps/f8s3-vajont/01e_pantalla.raw.json`, clave `final`.
  - Trae 13 beats y 12 fichas.
  - El papel validado de F36 (`01e_pantalla.json`) quedó con 9. Las 3 que cayeron son D47, D105 y Q43.
- Pool: `00_pool_v3.json`. El rango de años del material sale de las `fecha` y da 1943–2023.
- Aclaración: el `archivo` del raw de F36 no trae `fecha`, así que la tomé del pool.
- Scripts y salidas en el scratchpad (no escribí nada en el repo): `sim.py`, `p1.py` (1b y 1c), `p2.py` (A.2) y `p4.py` (A.4).

## 1. Tabla de fichas (las 12 que propuso el modelo)

El momento del relato es el último año dicho por la voz hasta esa oración, incluida y con arrastre entre caps.

| Ficha | Cap [oración] | Año del ítem (`fecha`) | Momento del relato | 1b fecha del relato | 1c cita sin fecha |
|---|---|---|---|---|---|
| D131 | ch01 [15] | sin fecha | 1963 | no aplica | – |
| D117 | ch02 [2] | sin fecha | 1943 | no aplica | – |
| **D47** (cayó en F36) | ch02 [11] | 1950 | 1943 | **pasa solo porque la oración dice «la década del cincuenta»** (año en dos cifras) | – |
| T16 | ch03 [3] | 1959 | 1959 | pasa (igual) | – |
| D49 | ch03 [17] | 1960 | 1960 | pasa (igual) | – |
| **D105** (cayó en F36) | ch04 [15] | 1962-12 | 1963 | pasa (1962 < 1963) | – |
| Q50 | ch05 [2] | sin fecha | 1963 | no aplica | pasa, pero flojo: el «autor» es la Administración del comune di Erto e Casso y matchea por «Erto» en «la tierra de Erto» (sección 3) |
| **Q43** (cayó en F36) | ch05 [23] | sin fecha | 1963 | no aplica | **CORTA**. Autor «Ingeniero jefe (sucesor de Semenza)», rol «Supervisor de obras». Las oraciones [22]–[24] hablan de «aparejador», «alarma» y «barreras». |
| D01 | ch06 [3] | 1963-10-09 | 1963 | pasa (igual) | – |
| D17 | ch06 [29] | sin fecha | 1963 | no aplica | – |
| Q14 | ch07 [1] | 1963-10-12 | 1963 | pasa (igual) | no aplica (tiene fecha) |
| D245 | ch07 [18] | 1997-02-15 | 1971 | pasa por la vecina [19]: «el año dos mil» = 2000 ≥ 1997 | – |

- Los 12 momentos del relato son idénticos a los de `momentos()` de CC.
- Las 5 fichas sin fecha (D131, D117, D17, Q50, Q43) no tienen ningún año en el texto del ítem, así que la ausencia de `fecha` no esconde un anacronismo.
- Para D47 y D105, la fecha que dice el pool coincide con la que dice el texto (1950 y diciembre de 1962).
- Los años que dice la voz y su orden son: 1963 (ch01 [13]), 1943 (ch02 [2]), 1959, 1960, 1959, 1960, 1960, 1961, 1962, 1963, 1963, 1968, 1968, 1971 y 2000.

## 2. Por regla: propuestos → cortados → quedan

**A.1b fecha del relato**
- 12 fichas propuestas. 7 tienen fecha, y las otras 5 la regla ni las mira.
- Cortadas: **0**. Quedan 12.
- Las dos únicas fichas con año posterior al momento se salvan por una salvedad: D245 (1997 vs 1971) por la vecina que dice 2000, y D47 (1950 vs 1943) por «la década del cincuenta».
- Tres ejemplos: D47 (ch02 [11], 1950 contra 1943, pasa por la oración ancla); D245 (ch07 [18], 1997 contra 1971, pasa porque la vecina [19] dice «dos mil»); D105 (ch04 [15], 1962 contra 1963, anterior al momento, no se toca).
- En Vajont esta regla no corta nada.

**A.1c cita sin fecha y no testimonio**
- Candidatas: Q50 y Q43. Q14 tiene fecha y queda fuera.
- Cortadas: **1** (Q43). Queda 1 (Q50).
- Ejemplos: Q43 corta (la voz de [22]–[24] no nombra ni a un «ingeniero jefe» ni a un «supervisor de obras»); Q50 pasa por los topónimos «Erto» y «Casso»; Q14 no aplica.
- Q43 cayó en F36 por `caben` (108 > 94). Ahora cae antes, por 1c, que es la causa de fondo.
- En la corrida de CC, Q50 igual queda fuera por `caben` (127 > 90). Eso es la regla B.2 y no la simulé. Dato aparte: el `caben` de la oración [2] era 152 en F36 y ahora 90.

**A.2 descartes «la voz lo dice» verificados**
- El raw de F36 no trae `tipo` en los descartes (son 82, sin `tipo`). Inferí «voz lo dice» por el motivo «la voz ya dice/cita/cuenta/nombra…», lo que da **58**.
- Resultado: 40 descartes correctos, 14 no verificables (citas sin cifras y D140/T64) y **4 vuelven como candidato**: T21 («3 millones de m³»), T39 («50 millones»), D68 («1,5 cm») y T85 («11 personas»).
- Tres ejemplos: T21 (ch03 no dice «tres millones»); T39 (ch04 no dice «cincuenta millones»); T85 (ch07 dice la remisión a juicio del 20 de febrero de 1968, pero no «11»).
- Lectura alternativa «no dice todas sus cifras»: devolvería 14 y sobre-devuelve casos donde la voz sí dice la cifra principal. Me quedo con «ninguna de sus cifras», que es lo que hace CC.
- Falso positivo: **D68 vuelve y no debería.** La voz de ch04 [14] dice «más de un centímetro y medio por día», y ni mi parser ni el de CC leen «y medio» como 1,5.

**A.4 no_dicho y spoiler dejan de cortar y se preguntan**
- Propuestas: 12. Con coincidencia, 2: D47 (spoiler, «2», primera aparición ch03 [17] «fisura de casi dos kilómetros»; el «2» aparece también en ch04 [5], ch05 [2], ch05 [20], ch07 [2]: la pregunta cita solo la primera) y D105 (no_dicho, «1962», ch04 [14]).
- F36 cortó las dos. Ahora cortadas **0**, preguntadas **2**. Las otras 10 sin coincidencia.

## 3. Dónde no coinciden y puntos frágiles
En los números no hay diferencias. Cuatro lecturas a declarar:
1. **D47 se salva únicamente por la lectura de CC del «año en dos cifras».** Con la lectura literal, 1b corta D47 y nunca llega a la pregunta de A.4.
2. **D245 se salva por la vecina** (cualquier lectura da lo mismo en Vajont).
3. **Q50 pasa 1c por topónimos** («Erto»): con lectura estricta caería por 1c.
4. **D68 es un falso «vuelve»** por las fracciones en letras («y medio», «medio»): es del parser, no de la regla.

Sin efecto en Vajont: las expresiones relativas no entran (ninguna ficha depende de ellas); «último año» y «máximo» dan lo mismo para las 12 fichas.
