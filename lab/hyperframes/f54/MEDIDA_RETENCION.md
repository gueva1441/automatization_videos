# F54 — medida de retención por código (adenda 18:30, 1): viejo | nuevo

viejo = `C:\CLAUDE_PROJECTS\automatization_videos\lab\hyperframes\f54\antes` (escaleta f26-1) · nuevo = `C:\CLAUDE_PROJECTS\automatization_videos\data\scripts\_steps\123bbb64-9fca-4395-8bf4-57d60e219ef1` (escaleta f54-1) · 2.4 pal/s. Informa, no frena. Detector: `evidence.used_in` (el de producción) con dos relajaciones solo para medir, iguales para los dos guiones: los años en letras pasan a cifras antes de buscar el ancla, y en un evento con fecha el año y el hecho pueden estar en oraciones vecinas del mismo cap (ver `medida_retencion._dice`).

| ingrediente | viejo | nuevo |
|---|---|---|
| segundos hasta la primera apuesta | 511.3 s (cap 5, pico (T64)) | 550.0 s (cap 5, loop principal (D89)) |
| loops abiertos / pagados | 0 declarado(s) | 2 declarado(s) · loop L1 (D89): pagado; loop L2 (D21): NO pagado; beat 5 paga (D21): NO pagado; beat 9 paga (D89): pagado; beat 11 paga (D10): NO pagado; beat 12 paga (T92): pagado |
| re-gancho | no declarado | sí (cap 3, min 5.33, parecido 1.0) |
| el cierre vuelve a la imagen del gancho | NO (D42 en el cap 7) | sí (Q24 en el cap 7) |

| cap | palabras v | n | años v | n | datos/min v | n |
|---|---|---|---|---|---|---|
| 1 | 86 | 168 | 1 | 2 | 0.0 | 0.9 |
| 2 | 302 | 263 | 3 | 3 | 2.4 | 3.3 |
| 3 | 350 | 368 | 6 | 11 | 1.2 | 2.0 |
| 4 | 239 | 335 | 3 | 2 | 3.6 | 1.7 |
| 5 | 344 | 252 | 8 | 5 | 2.5 | 4.0 |
| 6 | 359 | 278 | 7 | 7 | 0.8 | 1.6 |
| 7 | 207 | 249 | 3 | 5 | 2.1 | 3.5 |

## Detalle

```json
{
 "viejo": {
  "dir": "C:\\CLAUDE_PROJECTS\\automatization_videos\\lab\\hyperframes\\f54\\antes",
  "prompt_escaleta": "f26-1",
  "palabras_por_cap": {
   "1": 86,
   "2": 302,
   "3": 350,
   "4": 239,
   "5": 344,
   "6": 359,
   "7": 207
  },
  "anios_por_cap": {
   "1": 1,
   "2": 3,
   "3": 6,
   "4": 3,
   "5": 8,
   "6": 7,
   "7": 3
  },
  "datos_por_min": {
   "1": 0.0,
   "2": 2.4,
   "3": 1.2,
   "4": 3.6,
   "5": 2.5,
   "6": 0.8,
   "7": 2.1
  },
  "primera_apuesta": {
   "segundos": 511.3,
   "cap": 5,
   "que": "pico (T64)",
   "oracion": "Madrid, mil novecientos noventa y uno."
  },
  "loops": [],
  "re_gancho": {
   "declarado": false,
   "dicho": false,
   "minuto": null
  },
  "cierre": {
   "beat": 14,
   "dato": "D42",
   "cap": 7,
   "dicho": false,
   "gancho_dato": "D85"
  },
  "loops_declarados": 0,
  "beats_con_paga": []
 },
 "nuevo": {
  "dir": "C:\\CLAUDE_PROJECTS\\automatization_videos\\data\\scripts\\_steps\\123bbb64-9fca-4395-8bf4-57d60e219ef1",
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
    "abierto": false,
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
    "pagado": false,
    "primera_oracion": false,
    "cap_pago": 3
   },
   {
    "que": "beat 5 paga",
    "pregunta": "¿De qué está hecho ese polvo que nadie había visto en esa cantidad?",
    "abre": 3,
    "paga": 5,
    "dato": "D21",
    "abierto": false,
    "pagado": false,
    "primera_oracion": false,
    "cap_pago": 3
   },
   {
    "que": "beat 9 paga",
    "pregunta": "¿Qué le pasó al hombre del pie vendado, y por qué una herida que no cierra importa en una historia sobre un pueblo borrado del mapa?",
    "abre": 1,
    "paga": 9,
    "dato": "D89",
    "abierto": false,
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
 }
}
```