# PROMPT DE LA FICHA v2 — lo que se AGREGA al de F14

Escrito por el analista, 2026-10-23. Para CC: el `<rol>`, los 5 criterios, las secciones existentes (personas, cronologia, hechos, cifras, citas, decisiones, versiones, contradicciones, personas_descartadas, descartados) y el chequeo determinista **quedan como están**. Se agregan estas secciones al `<tarea>` del sistema y al esquema, en este orden, **antes** de «hechos».

---

## Lo que se agrega al <tarea> del sistema

- historia: antes de listar hechos, decidís qué historia hay en este caso. Devolvés:
  - humanos_candidatos (2 a 4): personas con arco, es decir, que entran en el caso en un estado, les pasa algo y salen en otro. Para cada una: nombre canónico, rol, en una oración qué le pasa (entra → sufre → sale), qué ids la sostienen y cuántas citas verificadas tiene. Una persona sin cita verificada puede ser candidata, pero lo decís.
  - giros (3 a 6): los momentos en que la historia cambia de dirección (una orden, una puerta que no abre, una cifra que aparece, una negación oficial). Cada uno con sus ids y en qué orden pasan.
  - pico: el peor momento, el que todo lo anterior prepara. Uno solo, con sus ids y por qué es el pico.
  - pregunta_final: la pregunta que el caso deja abierta y que ningún documento cierra, con los ids que la sostienen.
- escenas (8 a 15): momentos concretos que se pueden ver. Cada escena en una o dos oraciones: dónde, quién, qué está pasando, y lo que un testigo o documento dice que se veía, se oía, se olía o se tocaba. Solo con lo que los ids permiten. Una escena sin ningún detalle sensorial en los datos no es escena: es hecho, y va a hechos.
- hechos (60 a 80) con un campo nivel: 1 = sostiene la historia (sin él no se entiende el caso; entre 12 y 20), 2 = apoyo (da contexto o escala). Además, cada hecho lleva el campo sirve_para: gancho, contexto, escalada, giro, pico, consecuencia o cierre.

Ejemplo de humano candidato (de otro caso; copiá la forma, no el contenido):
{"nombre": "Pearl Cornelia Bland", "rol": "detenida por una deuda de 398 dólares", "arco": "entra presa por multas, queda encerrada cuando llega el huracán, es agredida en Conchetta sin que los oficiales intervengan, y sale en junio del año siguiente por una orden de liberación", "ids": ["D301", "Q88", "D512"], "citas_verificadas": 1}

Ejemplo de giro:
{"orden": 2, "que_cambia": "El sheriff rechaza la ayuda del Departamento de Correcciones para evacuar: la prisión no se vacía", "ids": ["D35", "Q08"]}

Ejemplo de escena:
{"donde": "Celdas de Templeman III, 30 de agosto", "quien": "presos encerrados", "que_pasa": "el agua de la inundación entra y sube hasta el pecho", "sentidos": "olor a aguas residuales y combustible diésel; oscuridad total; gritos entre pabellones", "ids": ["T93", "D414", "D09", "D545"]}

Ejemplo de hecho nivel 1:
{"texto": "La lista de evacuados no incluye a 517 reclusos.", "nivel": 1, "sirve_para": "consecuencia", "ids": ["D185"]}

---

## Lo que cambia en la escaleta (m01a) para usar esto

- El prompt de la escaleta recibe la ficha completa, con `historia` y `escenas` **primero** (antes de hechos), porque es lo que necesita para elegir humano, pico y beats.
- `imagen_sensorial` de cada beat sale de una `escena` de la ficha cuando hay una para ese momento (se cita su índice); si no hay, la escaleta la escribe como hoy.
- El humano de la escaleta se elige entre `humanos_candidatos`. Si elige otro, lo tiene que justificar en `_avisos`.

## Lo que NO cambia
- Chequeo determinista: todo lo nuevo (humanos, giros, escenas, pico, pregunta) pasa por el mismo control de ids existentes y cifras/horas/fechas respaldadas. Una escena cuyos sentidos no estén en el texto de sus ids se saca y va a descartados con motivo «no respaldado».
- Ningún criterio nuevo. Ninguna regla nueva para el guion.
