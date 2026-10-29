# F54 — Salida A (sin LLM, US$ 0)

## 1. Diff de los dos prompts (viejo → nuevo, solo las líneas que cambian)

### Escaleta f26-1 → f54-1 (`<oficio>` §2)

```diff
- 2. El gancho es el peor momento, ya en curso. Tomá la escena más fuerte de la ficha y ponela en el beat 1, marcado como flash-forward. Sin contexto, sin año, sin cifras: lo que se ve. La promesa es una sola oración que deja una imagen sin cerrar o una pregunta que el espectador no puede responder todavía. No cuenta lo que va a pasar, no enumera lo que viene, no nombra juicios, comisiones ni consecuencias. Probala así: si la oración se puede leer como un resumen de lo que viene («nadie lo sabrá durante años», «terminará en un juicio»), no es una promesa; es un adelanto. Volvé a escribirla con lo que se ve o lo que no cierra.
+ 2. El gancho es el peor momento, ya en curso. Tomá la escena más fuerte de la ficha y ponela en el beat 1, marcado como flash-forward. Sin contexto, sin año, sin cifras: lo que se ve. La promesa es una sola oración que deja una imagen sin cerrar o una pregunta que el espectador no puede responder todavía. La promesa dice qué va a entender el espectador si se queda: puede nombrar lo que está en juego, con años o cifras si hacen falta; no es un índice de lo que viene.
```

### Guion v5.4 (f25-1) → v5.5 (f54-1) (`<estructura>` 1)

```diff
- 1. Gancho (cap 1): la escena del peor momento, ya en curso. Primera frase: lo que se ve, sin año, sin cifra, sin institución. Segunda: la promesa, como viene en la escaleta, sin agregarle lo que va a pasar después. Antes de terminar el cap, una frase corta con lugar y año. El cap 1 termina volviendo atrás: «horas antes», «días antes».
+ 1. Gancho (cap 1): la escena del peor momento, ya en curso. Primera frase: lo que se ve, sin año, sin cifra, sin institución. Segunda: la promesa: lo que está en juego, con tus palabras, sin índice de lo que viene. Antes de terminar el cap, una frase corta con lugar y año. El cap 1 termina volviendo atrás: «horas antes», «días antes».
```

## 2. `has_figure` sobre las frases de la ENTRADA 29h (§3)

| # | de dónde | frase | antes | ahora | qué lo detecta ahora |
|---|---|---|---|---|---|
| 1 | voz de hoy | Un hombre joven posa para una foto con el pie envuelto en una venda blanca. | no | no | — |
| 2 | voz de hoy | Detrás, tierra roja y paredes de chapa. | no | no | — |
| 3 | voz de hoy | En el retrato de familia todos miran a cámara menos el pie. | no | no | — |
| 4 | voz de hoy | El hombre se llama Daniel Écija. | no | no | — |
| 5 | voz de hoy | Para entender ese pie hay que volver a un baile en Madrid. | no | no | — |
| 6 | cierre_humano | La herida del pie cerró. La otra nadie supo verla a tiempo. | no | no | — |
| 7 | DEBERÍA | Un hombre joven posa con el pie envuelto en una venda blanca. | no | no | — |
| 8 | DEBERÍA | Le cayó un trozo de amianto y la herida no cierra. | no | no | — |
| 9 | DEBERÍA | Wittenoom, Australia, mil novecientos sesenta y dos. | sí | sí | mil, novecientos, sesenta y dos |
| 10 | DEBERÍA | Esa herida va a cerrar. | no | no | — |
| 11 | DEBERÍA | Lo que respiró ese año, no: veintinueve años después, al otro lado del mundo, el polvo lo va a alcanzar. | no | sí | veintinueve |

## 3. `bloqueantes` + `metricas` sobre el guion actual de Wittenoom

Fuente: `data/scripts/_steps/123bbb64-9fca-4395-8bf4-57d60e219ef1/01b_narration.json` (24 párrafos; beat de cada párrafo tomado de `01b_guionista_v4.json` → `reparacion.parrafos`, misma posición dentro del cap). Escaleta `01a_escaleta.json`, ficha `ficha_caso.json`, perfil `_perfil.json`.

### Bloqueantes: 2

| código | cap | beat | motivo | frase |
|---|---|---|---|---|
| d | 3 | 4 | fuera del caso (descartado en el pool): Defensor del empleador no identificado | Un año después, en una sala de arbitraje, la empresa contestó a los que hablaban del polvo. «El mero hecho de que haya n |
| f | 7 | 14 | cierre no dicho: el dato central D42 del beat 14 (cierre) no está en el cap 7 | — |

### Métricas nuevas por cap (solo tabla, sin freno)

| cap | palabras | años dichos | datos usados | datos/min |
|---|---|---|---|---|
| 1 | 86 | 1 | 0 | 0.0 |
| 2 | 303 | 3 | 5 | 2.4 |
| 3 | 350 | 6 | 3 | 1.2 |
| 4 | 239 | 3 | 6 | 3.6 |
| 5 | 345 | 8 | 6 | 2.5 |
| 6 | 361 | 7 | 2 | 0.8 |
| 7 | 207 | 3 | 3 | 2.1 |

Total: 1891 palabras · largo: 1891 palabras ≈ 13.1 min.
