# F64 Etapa 3 — SIM_VERIFICADOR: los 8 papeles de F63 contra el `validar` nuevo + verificador real

Topic `123bbb64-9fca-4395-8bf4-57d60e219ef1` · entrada completa de producción (archivo 362 ítems) · verificador `claude-opus-5-5` medium · una llamada por papel, 8 a la vez · fuente: `lab/hyperframes/f63/a/*_[12].raw.json` (`respuesta`) · salidas crudas en `lab/hyperframes/f64/sim/`.

## Totales por papel

| papel | marcas | fichas marcadas | pasa | corta | descartes marcados | dicho | no_dicho | tokens in/out | US$ | s (llamada) | intentos | error |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| O1_1 | 8 | 3 | 3 | 0 | 4 | 4 | 0 | 9948/1153 | 0.0629 | 10.4 | 1 | — |
| O1_2 | 5 | 3 | 2 | 1 | 2 | 2 | 0 | 9306/804 | 0.0533 | 7.1 | 1 | — |
| O2_1 | 9 | 3 | 3 | 0 | 6 | 6 | 0 | 9814/1164 | 0.0625 | 10.1 | 1 | — |
| O2_2 | 7 | 4 | 4 | 0 | 2 | 2 | 0 | 10039/1131 | 0.0628 | 11.0 | 1 | — |
| O3_1 | 10 | 4 | 3 | 1 | 6 | 6 | 0 | 10154/1366 | 0.0679 | 11.7 | 1 | — |
| O3_2 | 8 | 2 | 2 | 0 | 6 | 6 | 0 | 9582/1041 | 0.0592 | 8.5 | 1 | — |
| S_1 | 12 | 5 | 4 | 1 | 5 | 5 | 0 | 11117/1822 | 0.0809 | 15.1 | 1 | — |
| S_2 | 5 | 2 | 1 | 1 | 2 | 2 | 0 | 9246/857 | 0.0541 | 7.1 | 1 | — |
| **total** | 64 | | 22 | 4 | | 33 | 0 | | **0.5036** | 81.0 | | |

## Cada marca, con su veredicto

### O1_1

| que | id | cap/beat | regla | token (dónde lo dice la voz) | veredicto | motivo del verificador | oración |
|---|---|---|---|---|---|---|---|
| ficha | Q25 | ch02 b2 | spoiler | «2» (ch02 [7]) | **pasa** | La voz cuenta que ella iba cerca de él y confiaba en lo que venía, pero no cita la frase de que en España no tenían nada; el «2» de la coincidencia habla de otr | — |
| ficha | D94 | ch05 b9 | fecha_relato | «1989» (ch05 [8]) | **pasa** | La voz menciona el fallo de 1988, pero no el pago de 18,3 millones a 200 afectados en 1989; la ficha suma una consecuencia que la voz no dice. | — |
| ficha | D23 | ch05 b10 | contradice | «30» (ch05 [18]) | **pasa** | Los «casi treinta años» de Daniel no tienen relación con el corte de más de 500 muertos para 1989; la voz no dice esa cifra. | — |
| ficha | D23 | ch05 b10 | contradice | «2024» (ch07 [4]) | **pasa** | Los «casi treinta años» de Daniel no tienen relación con el corte de más de 500 muertos para 1989; la voz no dice esa cifra. | — |
| descarte | T13 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice que en 1946 ya había diagnósticos de asbestosis. | ch03 [14] |
| descarte | D21 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice que en 1961 la producción subió, tras narrar las advertencias previas. | ch03 [28] |
| descarte | T80 | — | voz_lo_dice | no dice Ministro, Desarrollo, Regional, Hon, Jon, Ford, MLC | **dicho** | La voz cuenta la abolición oficial hacia junio de 2007, aunque omite al ministro. | ch06 [10] |
| descarte | D95 | — | voz_lo_dice | no dice 1.500 | **dicho** | La voz dice la reclamación de mil quinientos millones de dólares australianos por la tierra Banjima. | ch07 [6] |

- fichas que quedan: 11/13 · cortadas por el verificador: [] · cortadas por el código: [('D26', 'caben'), ('Q19', 'caben')] · vuelven: [] · motivos para una vuelta: 9

### O1_2

| que | id | cap/beat | regla | token (dónde lo dice la voz) | veredicto | motivo del verificador | oración |
|---|---|---|---|---|---|---|---|
| ficha | Q25 | ch02 b2 | spoiler | «2» (ch02 [7]) | **pasa** | La voz cuenta que ella confiaba en lo que venía y cita «me pegué a mi marido», pero nunca dice que en España no tuvieran nada. | — |
| ficha | T38 | ch02 b3 | spoiler | «1962» (ch02 [8]) | **corta** | La voz ya da la fecha en la vecina: boda el 20 de septiembre de 1962 y «cuatro días después estaban en un barco», es decir, el 24. | ch02 [5] |
| ficha | D94 | ch05 b9 | fecha_relato | «1989» (ch05 [8]) | **pasa** | La voz habla del fallo de 1988, pero nunca menciona el pago de 18,3 millones a 200 afectados en 1989. | — |
| descarte | D21 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice «En 1961 la producción subió», justo después de enumerar las advertencias. | ch03 [28] |
| descarte | D95 | — | voz_lo_dice | no dice 1.500 | **dicho** | La voz menciona la reclamación de 1.500 millones de dólares australianos por la tierra Banjima contra Australia Occidental. | ch07 [6] |

- fichas que quedan: 12/13 · cortadas por el verificador: ['T38'] · cortadas por el código: [] · vuelven: [] · motivos para una vuelta: 7

### O2_1

| que | id | cap/beat | regla | token (dónde lo dice la voz) | veredicto | motivo del verificador | oración |
|---|---|---|---|---|---|---|---|
| ficha | D108 | ch01 b1 | no_dicho | «Australia» (ch01 [6]) | **pasa** | La voz nunca califica a Wittenoom como el peor desastre industrial de Australia; solo coincide la palabra 'Australia'. | — |
| ficha | D83 | ch02 b3 | no_dicho | «Australia» (ch02 [6]) | **pasa** | La voz menciona el acuerdo entre gobiernos, pero no su nombre (Operación Canguro) ni el año 1958; la ficha suma ambos datos. | — |
| ficha | D94 | ch05 b9 | fecha_relato | «1989» (ch05 [8]) | **pasa** | La voz cuenta el fallo de 1988, pero no el pago de 18,3 millones a 200 afectados en 1989; es un hecho nuevo. | — |
| descarte | D03 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice que el pueblo, la pista, los patios y la escuela estaban hechos con lo que sobraba de la mina. | ch03 [9] |
| descarte | D129 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice que con relaves se hicieron las carreteras, los patios y los espacios públicos. | ch03 [7] |
| descarte | T13 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice que en 1946 ya había diagnósticos de asbestosis. | ch03 [14] |
| descarte | D21 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice que en 1961 la producción subió, después de las advertencias que acaba de contar. | ch03 [28] |
| descarte | T27 | — | voz_lo_dice | no dice 3, 4 | **dicho** | La voz cuenta que, al instalarse los equipos, se recortó y restringió el suplemento salarial por polvo; omite la cifra. | ch03 [26] |
| descarte | D95 | — | voz_lo_dice | no dice 1.500 | **dicho** | La voz menciona la reclamación de mil quinientos millones de dólares australianos. | ch07 [6] |

- fichas que quedan: 13/13 · cortadas por el verificador: [] · cortadas por el código: [] · vuelven: [] · motivos para una vuelta: 5

### O2_2

| que | id | cap/beat | regla | token (dónde lo dice la voz) | veredicto | motivo del verificador | oración |
|---|---|---|---|---|---|---|---|
| ficha | D108 | ch01 b1 | no_dicho | «Australia» (ch01 [6]) | **pasa** | La voz nunca califica a Wittenoom como el peor desastre industrial de Australia; solo coincide la palabra «Australia». | — |
| ficha | Q25 | ch02 b2 | spoiler | «2» (ch02 [7]) | **pasa** | La voz cita otra frase de María («Me pegué a mi marido…») y habla de su confianza, pero no dice que en España no tuvieran nada. | — |
| ficha | D94 | ch05 b9 | fecha_relato | «1989» (ch05 [8]) | **pasa** | La voz cuenta el fallo de 1988, pero no la indemnización de 1989 ni sus cifras; la ficha suma un hecho nuevo. | — |
| ficha | D23 | ch05 b10 | contradice | «30» (ch05 [18]) | **pasa** | El corte histórico de más de 500 muertos para 1989 no está en la voz; los «casi treinta años» de Daniel son otro hecho, y las cifras de ch06 (dos mil, más de cu | — |
| ficha | D23 | ch05 b10 | contradice | «2024» (ch07 [4]) | **pasa** | El corte histórico de más de 500 muertos para 1989 no está en la voz; los «casi treinta años» de Daniel son otro hecho, y las cifras de ch06 (dos mil, más de cu | — |
| descarte | D21 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice que en 1961 la producción subió, tras narrar las advertencias de 1944 a 1957. | ch03 [28] |
| descarte | D95 | — | voz_lo_dice | no dice 1.500 | **dicho** | La voz menciona la reclamación de mil quinientos millones de dólares australianos por la tierra Banjima contra Australia Occidental. | ch07 [6] |

- fichas que quedan: 12/13 · cortadas por el verificador: [] · cortadas por el código: [('T86', 'candado')] · vuelven: [] · motivos para una vuelta: 7

### O3_1

| que | id | cap/beat | regla | token (dónde lo dice la voz) | veredicto | motivo del verificador | oración |
|---|---|---|---|---|---|---|---|
| ficha | D108 | ch01 b1 | no_dicho | «Australia» (ch01 [6]) | **pasa** | La voz nunca califica a Wittenoom como el peor desastre industrial de Australia; solo coincide la palabra «Australia». | — |
| ficha | Q25 | ch02 b2 | spoiler | «2» (ch02 [7]) | **pasa** | La voz cita otra frase de María («Me pegué a mi marido…»), pero no dice que en España no tuvieran nada. | — |
| ficha | T38 | ch02 b3 | spoiler | «1962» (ch02 [8]) | **corta** | La voz sitúa la boda el 20 de septiembre de 1962 y dice que cuatro días después estaban en el barco, es decir, el 24 de septiembre. | ch02 [5] |
| ficha | D94 | ch05 b9 | fecha_relato | «1989» (ch05 [8]) | **pasa** | La voz no menciona el pago de 18,3 millones de 1989 ni los 200 afectados; la ficha suma un hecho nuevo al fallo de 1988. | — |
| descarte | D03 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice que la pista y el pueblo entero estaban hechos con lo que sobraba de la mina. | ch03 [9] |
| descarte | D129 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice que con los relaves se hicieron las carreteras, los patios y los espacios públicos. | ch03 [7] |
| descarte | T13 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice que en 1946 ya había diagnósticos de asbestosis. | ch03 [14] |
| descarte | D21 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice «En 1961 la producción subió», tras enumerar las advertencias. | ch03 [28] |
| descarte | T27 | — | voz_lo_dice | no dice 3, 4 | **dicho** | La voz dice que, al instalarse los equipos contra el polvo, se recortó y restringió el suplemento salarial; omite la cifra en peniques. | ch03 [26] |
| descarte | D95 | — | voz_lo_dice | no dice 1.500 | **dicho** | La voz menciona la reclamación de mil quinientos millones de dólares australianos por la tierra Banjima. | ch07 [6] |

- fichas que quedan: 12/13 · cortadas por el verificador: ['T38'] · cortadas por el código: [] · vuelven: [] · motivos para una vuelta: 8

### O3_2

| que | id | cap/beat | regla | token (dónde lo dice la voz) | veredicto | motivo del verificador | oración |
|---|---|---|---|---|---|---|---|
| ficha | Q25 | ch02 b2 | spoiler | «2» (ch02 [7]) | **pasa** | La voz nunca cita ni dice que en España no tuvieran nada; el «dos» coincide con los dos gobiernos del acuerdo migratorio, que es otro hecho. | — |
| ficha | D94 | ch05 b9 | fecha_relato | «1989» (ch05 [8]) | **pasa** | La voz cuenta el fallo de 1988, pero no menciona en ningún momento el pago de 18,3 millones a 200 afectados en 1989; la ficha suma un hecho nuevo. | — |
| descarte | D03 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice que la pista se hizo con relaves de la mina, y en idx9 que el pueblo entero también. | ch03 [6] |
| descarte | D129 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice que con relaves se hicieron las carreteras, los patios y los espacios públicos. | ch03 [7] |
| descarte | T13 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice que en 1946 ya había diagnósticos de asbestosis. | ch03 [14] |
| descarte | D21 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice que en 1961 la producción subió, después de narrar las advertencias previas. | ch03 [28] |
| descarte | T27 | — | voz_lo_dice | no dice 3, 4 | **dicho** | La voz cuenta que, tras instalar los equipos contra el polvo, se recortó y restringió el suplemento; solo omite los peniques. | ch03 [26] |
| descarte | D95 | — | voz_lo_dice | no dice 1.500 | **dicho** | La voz dice que la prensa habla de una reclamación de mil quinientos millones de dólares australianos por la tierra Banjima. | ch07 [6] |

- fichas que quedan: 11/13 · cortadas por el verificador: [] · cortadas por el código: [('D115', 'candado'), ('D102', 'candado')] · vuelven: [] · motivos para una vuelta: 8

### S_1

| que | id | cap/beat | regla | token (dónde lo dice la voz) | veredicto | motivo del verificador | oración |
|---|---|---|---|---|---|---|---|
| ficha | D79 | ch01 b1 | no_dicho | «2000» (ch06 [7]) | **corta** | La voz da más adelante el recuento de muertos (el gobierno dejó de contar en dos mil, otras estimaciones más de cuatro mil); la ficha lo adelantaría con otra ve | ch06 [7] |
| ficha | D79 | ch01 b1 | spoiler | «2000» (ch06 [7]) | **corta** | La voz da más adelante el recuento de muertos (el gobierno dejó de contar en dos mil, otras estimaciones más de cuatro mil); la ficha lo adelantaría con otra ve | ch06 [7] |
| ficha | Q17 | ch04 b7 | spoiler | «2» (ch05 [4]) | **pasa** | La voz cuenta una explosión el primer día, pero nunca dice que las ambulancias fueran frecuentes; el «dos» y el «tres» coinciden hablando de otra cosa. | — |
| ficha | Q17 | ch04 b7 | spoiler | «3» (ch04 [14]) | **pasa** | La voz cuenta una explosión el primer día, pero nunca dice que las ambulancias fueran frecuentes; el «dos» y el «tres» coinciden hablando de otra cosa. | — |
| ficha | D94 | ch05 b9 | fecha_relato | «1989» (ch05 [8]) | **pasa** | La voz cuenta el fallo de 1988, pero no la indemnización de 1989 de 18,3 millones a 200 afectados. | — |
| ficha | D73 | ch06 b11 | no_dicho | «2.000» (ch06 [7]) | **pasa** | Los dos mil de la voz son el recuento oficial de muertos; los clientes de Peter Gordon no se mencionan. | — |
| ficha | D64 | ch06 b12 | spoiler | «2» (ch07 [9]) | **pasa** | La voz da tres millones de toneladas, pero no la comparación con el Melbourne Cricket Ground; la ficha la suma. | — |
| descarte | T13 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice que en 1946 ya había diagnósticos de asbestosis. | ch03 [14] |
| descarte | D21 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice «En 1961 la producción subió», después de las advertencias. | ch03 [28] |
| descarte | T27 | — | voz_lo_dice | no dice 3, 4 | **dicho** | La voz cuenta que, con los equipos contra el polvo, se recortó y restringió el suplemento salarial; solo omite los peniques. | ch03 [26] |
| descarte | T80 | — | voz_lo_dice | no dice Ministro, Desarrollo, Regional, Hon, Jon, Ford, MLC | **dicho** | La voz dice que hacia junio de 2007 Wittenoom fue abolido oficialmente; solo omite quién lo anunció. | ch06 [10] |
| descarte | D95 | — | voz_lo_dice | no dice 1.500 | **dicho** | La voz dice que la reclamación por la tierra Banjima es de mil quinientos millones de dólares australianos. | ch07 [6] |

- fichas que quedan: 10/13 · cortadas por el verificador: ['D79'] · cortadas por el código: [('D109', 'candado')] · vuelven: [] · motivos para una vuelta: 10

### S_2

| que | id | cap/beat | regla | token (dónde lo dice la voz) | veredicto | motivo del verificador | oración |
|---|---|---|---|---|---|---|---|
| ficha | D79 | ch01 b1 | no_dicho | «2000» (ch06 [7]) | **corta** | La voz cuenta en ch06 el recuento de muertos (el gobierno dejó de contar en dos mil y otras estimaciones hablan de más de cuatro mil); la ficha lo adelantaría. | ch06 [7] |
| ficha | D79 | ch01 b1 | spoiler | «2000» (ch06 [7]) | **corta** | La voz cuenta en ch06 el recuento de muertos (el gobierno dejó de contar en dos mil y otras estimaciones hablan de más de cuatro mil); la ficha lo adelantaría. | ch06 [7] |
| ficha | D141 | ch05 b9 | spoiler | «2.5» (ch05 [4]) | **pasa** | La voz habla de razones económicas pero no da la cifra de pérdidas; el 2.5 coincide solo con los «dos años y medio» de los de Juan, que es otra cosa. | — |
| descarte | D21 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice que en 1961 la producción subió. | ch03 [28] |
| descarte | D95 | — | voz_lo_dice | no dice 1.500 | **dicho** | La voz menciona la reclamación de mil quinientos millones de dólares australianos por la tierra Banjima. | ch07 [6] |

- fichas que quedan: 11/13 · cortadas por el verificador: ['D79'] · cortadas por el código: [('D115', 'candado')] · vuelven: [] · motivos para una vuelta: 9

## Contra la tabla DEBERÍA de REVISION_CIEGA_F63.md §2 (para el analista)

Lo que el analista marcó bueno (DEBERÍA del beat) y el verificador **corta**:

- (ninguna)

Lo que el analista marcó flojo o malo y el verificador **pasa** (el verificador juzga el hecho, no la calidad: informativo):

- S_1: Q17 (ch04 b7, spoiler «2») → pasa: La voz cuenta una explosión el primer día, pero nunca dice que las ambulancias fueran frecuentes; el «dos» y el «tres» coinciden hablando de otra cosa.
- S_1: Q17 (ch04 b7, spoiler «3») → pasa: La voz cuenta una explosión el primer día, pero nunca dice que las ambulancias fueran frecuentes; el «dos» y el «tres» coinciden hablando de otra cosa.
- S_1: D73 (ch06 b11, no_dicho «2.000») → pasa: Los dos mil de la voz son el recuento oficial de muertos; los clientes de Peter Gordon no se mencionan.
- S_1: D64 (ch06 b12, spoiler «2») → pasa: La voz da tres millones de toneladas, pero no la comparación con el Melbourne Cricket Ground; la ficha la suma.

Fichas cortadas por el verificador que NO están en el DEBERÍA ni en lo marcado malo (ni bueno ni malo para el analista):

- (ninguna)

## Contra los veredictos que el handoff espera (§Etapa 3, «Revisión del prompt por el analista»)

| id | que | regla | esperado | papeles donde hay marca | veredictos obtenidos |
|---|---|---|---|---|---|
| D79 | ficha | cualquiera | corta | S_1 (no_dicho «2000»); S_1 (spoiler «2000»); S_2 (no_dicho «2000»); S_2 (spoiler «2000») | corta, corta, corta, corta ✓ |
| D23 | ficha | cualquiera | pasa | O1_1 (contradice «30»); O1_1 (contradice «2024»); O2_2 (contradice «30»); O2_2 (contradice «2024») | pasa, pasa, pasa, pasa ✓ |
| D108 | ficha | cualquiera | pasa | O2_1 (no_dicho «Australia»); O2_2 (no_dicho «Australia»); O3_1 (no_dicho «Australia») | pasa, pasa, pasa ✓ |
| Q25 | ficha | cualquiera | pasa | O1_1 (spoiler «2»); O1_2 (spoiler «2»); O2_2 (spoiler «2»); O3_1 (spoiler «2»); O3_2 (spoiler «2») | pasa, pasa, pasa, pasa, pasa ✓ |
| D94 | ficha | fecha_relato | pasa | O1_1 (fecha_relato «1989»); O1_2 (fecha_relato «1989»); O2_1 (fecha_relato «1989»); O2_2 (fecha_relato «1989»); O3_1 (fecha_relato «1989»); O3_2 (fecha_relato «1989»); S_1 (fecha_relato «1989») | pasa, pasa, pasa, pasa, pasa, pasa, pasa ✓ |
| D141 | ficha | cualquiera | pasa | S_2 (spoiler «2.5») | pasa ✓ |
| D21 | descarte | cualquiera | dicho | O1_1; O1_2; O2_1; O2_2; O3_1; O3_2; S_1; S_2 | dicho, dicho, dicho, dicho, dicho, dicho, dicho, dicho ✓ |
| T80 | descarte | cualquiera | dicho | O1_1; S_1 | dicho, dicho ✓ |

Costo de la simulación: US$ 0.5036 (8 llamadas; estimado del handoff ≈ 0,5).
