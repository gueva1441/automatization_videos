# F54 — medida de retención por código (adenda 18:30, 1): viejo | nuevo

viejo = `C:\CLAUDE_PROJECTS\automatization_videos\lab\hyperframes\f55\antes` (escaleta f54-1) · nuevo = `C:\CLAUDE_PROJECTS\automatization_videos\data\scripts\_steps\123bbb64-9fca-4395-8bf4-57d60e219ef1` (escaleta f55-1) · 2.4 pal/s. Informa, no frena.

| ingrediente | viejo | nuevo |
|---|---|---|
| segundos hasta la primera apuesta | 550.0 s (cap 5, loop principal (D89)) | 545.4 s (cap 5, loop principal (T64)) |
| loops abiertos / pagados | 2 declarado(s) · loop L1 (D89): pagado; loop L2 (D21): pagado, en la primera oración del cap; beat 5 paga (D21): pagado, en la primera oración del cap; beat 9 paga (D89): pagado; beat 11 paga (D10): NO pagado; beat 12 paga (T92): pagado | 2 declarado(s) · loop L1 (T64): pagado; loop L2 (T98): pagado; beat 10 paga (T64): pagado; beat 13 paga (T98): pagado |
| re-gancho | sí (cap 3, min 5.33, parecido 1.0) | declarado pero no dicho (cap 3, min 3.97, parecido 0.36) |
| el cierre vuelve a la imagen del gancho | sí (Q24 en el cap 7) | sí (T98 en el cap 7) |

| cap | palabras v | n | años v | n | datos/min v | n |
|---|---|---|---|---|---|---|
| 1 | 168 | 161 | 2 | 1 | 0.9 | 0.9 |
| 2 | 263 | 220 | 3 | 4 | 3.3 | 3.9 |
| 3 | 368 | 433 | 11 | 5 | 2.0 | 2.0 |
| 4 | 335 | 322 | 2 | 4 | 1.7 | 2.7 |
| 5 | 252 | 292 | 5 | 7 | 4.0 | 3.9 |
| 6 | 278 | 297 | 7 | 4 | 1.6 | 3.4 |
| 7 | 249 | 210 | 5 | 6 | 3.5 | 2.7 |

## Detalle

```json
{
 "viejo": {
  "dir": "C:\\CLAUDE_PROJECTS\\automatization_videos\\lab\\hyperframes\\f55\\antes",
  "prompt_escaleta": "f54-1",
  "palabras_por_cap": {
   "1": 168,
   "2": 263,
   "3": 368,
   "4": 335,
   "5": 252,
   "6": 278,
   "7": 249
  },
  "anios_por_cap": {
   "1": 2,
   "2": 3,
   "3": 11,
   "4": 2,
   "5": 5,
   "6": 7,
   "7": 5
  },
  "datos_por_min": {
   "1": 0.9,
   "2": 3.3,
   "3": 2.0,
   "4": 1.7,
   "5": 4.0,
   "6": 1.6,
   "7": 3.5
  },
  "primera_apuesta": {
   "segundos": 550.0,
   "cap": 5,
   "que": "loop principal (D89)",
   "oracion": "Tenía cincuenta y cinco años."
  },
  "loops": [
   {
    "que": "loop L1",
    "pregunta": "¿Por qué un hombre que vivió diez meses en un pueblo del desierto muere de ese pueblo casi treinta años después y a medio mundo de distancia?",
    "abre": 1,
    "paga": 9,
    "dato": "D89",
    "abierto": true,
    "pagado": true,
    "primera_oracion": false,
    "cap_pago": 5
   },
   {
    "que": "loop L2",
    "pregunta": "¿Qué sabía la empresa del polvo cuando fue a Europa a reclutar a estas familias?",
    "abre": 3,
    "paga": 5,
    "dato": "D21",
    "abierto": false,
    "pagado": true,
    "primera_oracion": true,
    "cap_pago": 3
   },
   {
    "que": "beat 5 paga",
    "pregunta": "¿De qué está hecho ese polvo que nadie había visto en esa cantidad?",
    "abre": 3,
    "paga": 5,
    "dato": "D21",
    "abierto": false,
    "pagado": true,
    "primera_oracion": true,
    "cap_pago": 3
   },
   {
    "que": "beat 9 paga",
    "pregunta": "¿Qué le pasó al hombre del pie vendado, y por qué una herida que no cierra importa en una historia sobre un pueblo borrado del mapa?",
    "abre": 1,
    "paga": 9,
    "dato": "D89",
    "abierto": true,
    "pagado": true,
    "primera_oracion": false,
    "cap_pago": 5
   },
   {
    "que": "beat 11 paga",
    "pregunta": "Si borrar el nombre es el fin del episodio, ¿qué pasa con el polvo que sigue ahí?",
    "abre": 10,
    "paga": 11,
    "dato": "D10",
    "abierto": false,
    "pagado": false,
    "primera_oracion": false,
    "cap_pago": 6
   },
   {
    "que": "beat 12 paga",
    "pregunta": "Si se sabe cómo encapsularlo y cuánto cuesta, ¿por qué no se ha hecho nunca?",
    "abre": 11,
    "paga": 12,
    "dato": "T92",
    "abierto": false,
    "pagado": true,
    "primera_oracion": false,
    "cap_pago": 7
   }
  ],
  "re_gancho": {
   "declarado": true,
   "beat": 5,
   "cap": 3,
   "oracion": "A ese molino cubierto de polvo, a fines de mil novecientos sesenta y dos, iba a entrar un recién casado de Madrid que llevaba cuatro días de matrimonio cuando subió al barco.",
   "dicho": true,
   "parecido": 1.0,
   "minuto": 5.33,
   "oracion_dicha": "A ese molino cubierto de polvo, a fines de mil novecientos sesenta y dos, iba a entrar un recién casado de Madrid que llevaba cuatro días de matrimonio cuando subió al barco."
  },
  "cierre": {
   "beat": 13,
   "dato": "Q24",
   "cap": 7,
   "dicho": true,
   "gancho_dato": "D85"
  },
  "loops_declarados": 2,
  "beats_con_paga": [
   5,
   9,
   11,
   12
  ]
 },
 "nuevo": {
  "dir": "C:\\CLAUDE_PROJECTS\\automatization_videos\\data\\scripts\\_steps\\123bbb64-9fca-4395-8bf4-57d60e219ef1",
  "prompt_escaleta": "f55-1",
  "palabras_por_cap": {
   "1": 161,
   "2": 220,
   "3": 433,
   "4": 322,
   "5": 292,
   "6": 297,
   "7": 210
  },
  "anios_por_cap": {
   "1": 1,
   "2": 4,
   "3": 5,
   "4": 4,
   "5": 7,
   "6": 4,
   "7": 6
  },
  "datos_por_min": {
   "1": 0.9,
   "2": 3.9,
   "3": 2.0,
   "4": 2.7,
   "5": 3.9,
   "6": 3.4,
   "7": 2.7
  },
  "primera_apuesta": {
   "segundos": 545.4,
   "cap": 5,
   "que": "loop principal (T64)",
   "oracion": "En 1991, en Madrid, un diagnóstico puso nombre a lo que Daniel llevaba adentro: mesotelioma."
  },
  "loops": [
   {
    "que": "loop L1",
    "pregunta": "¿Qué le hizo Wittenoom a Daniel en diez meses, si el pueblo ya estaba a miles de kilómetros cuando lo alcanzó?",
    "abre": 1,
    "paga": 10,
    "dato": "T64",
    "abierto": true,
    "pagado": true,
    "primera_oracion": false,
    "cap_pago": 5
   },
   {
    "que": "loop L2",
    "pregunta": "¿Quién sabía que el polvo mataba, desde cuándo, y quién va a limpiar lo que quedó?",
    "abre": 5,
    "paga": 13,
    "dato": "T98",
    "abierto": true,
    "pagado": true,
    "primera_oracion": false,
    "cap_pago": 7
   },
   {
    "que": "beat 10 paga",
    "pregunta": "¿Por qué una herida hecha por un pedazo de mineral no cierra? ¿Qué hay en ese polvo?",
    "abre": 1,
    "paga": 10,
    "dato": "T64",
    "abierto": true,
    "pagado": true,
    "primera_oracion": false,
    "cap_pago": 5
   },
   {
    "que": "beat 13 paga",
    "pregunta": "Si en 1944 y 1948 ya estaba escrito, ¿quién decidió seguir?",
    "abre": 5,
    "paga": 13,
    "dato": "T98",
    "abierto": true,
    "pagado": true,
    "primera_oracion": false,
    "cap_pago": 7
   }
  ],
  "re_gancho": {
   "declarado": true,
   "beat": 6,
   "cap": 3,
   "oracion": "Un año después de que McNulty escribiera ese primer caso, un recién casado de Madrid se bajaba de un avión en esa misma pista de polvo.",
   "dicho": false,
   "parecido": 0.36,
   "minuto": 3.97,
   "oracion_dicha": "En 1944, el inspector de minas y el ingeniero de minas Adjunto del Estado informaron sobre el problema del polvo."
  },
  "cierre": {
   "beat": 13,
   "dato": "T98",
   "cap": 7,
   "dicho": true,
   "gancho_dato": "D85"
  },
  "loops_declarados": 2,
  "beats_con_paga": [
   10,
   13
  ]
 }
}
```