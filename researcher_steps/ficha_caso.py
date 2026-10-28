"""
researcher_steps/ficha_caso.py — F12 (HANDOFF_F12 §1): la ficha del caso, los datos depurados ANTES del guion.

    entrada   data/scripts/_steps/<topic>/00_pool_v3.json (solo lectura: el pool no se toca)
    llamada   UNA a gpt-6.1-sol en esfuerzo high, con la estructura de F11c: rol y tarea en el sistema; el pool completo
              (los 509 ítems de Ycuá, con ids, doc_id y offset de cada evidencia) en el usuario, y la tarea al final
    salida    ficha_caso.json + FICHA_<tag>.md (contradicciones arriba), en _steps/<topic>/ y donde diga `out_dirs`

Secciones: personas · cronologia · hechos (60–80) · cifras (con unidad) · citas (15–25; error de transcripción
corregido con `original`) · contradicciones (versiones lado a lado con doc_id y offset; NO se resuelven) · descartados.

F14 (HANDOFF_F14 §1.1): la ficha resuelve las contradicciones con 5 criterios generales (en el prompt):
    1 error de extracción → gana el pasaje · 2 variantes de un nombre → la forma oficial/judicial, si no la más repetida
    3 conteos → la cifra oficial, si no la más repetida (las otras en `otras_versiones`) · 4 hechos disputados → NO se
    resuelven: van a `versiones` · 5 horas y fechas → la que coincide en ≥ 2 fuentes; si ninguna, `aproximada`.
    Cada decisión va a `decisiones` con su `criterio`, su `decision` y `otras_versiones`; lo que no cae en ningún
    criterio queda en `contradicciones`. `personas_descartadas`: personas que el pool descartó (`_descartados`) pero
    que la historia necesita, con el motivo y los ids que las nombran.
    `id_texts(ficha)`: el texto limpio de cada id (cita corregida, cifra con unidad, hecho), para la escaleta y el guion.

F25b: `run(modelo=…)` / `python -m researcher_steps.ficha_caso <topic> --modelo claude-opus-5-5`: un modelo de Claude va
por claude_helpers (streaming, max_tokens 100 000, effort medium, sin esquema forzado) y la respuesta cruda queda en
`_steps/<topic>/ficha_respuesta_cruda.json`. Sin modelo, todo igual (gpt-6.1-sol high).

Chequeo determinista después de la llamada (control de la ficha, no una regla del guion; sin reintento):
    1. todo ítem cita ids que existen en el pool;
    2. toda cifra, hora y fecha del ítem aparece en el texto de esos ids (texto, cita literal y evidencias);
    3. toda cita corregida está a ≤ 3 caracteres (Levenshtein) de su `original`, y el original está en su id;
       en una contradicción, cada versión con su doc_id y offset tiene que ser una evidencia de sus ids.
    Lo que falla sale de su sección y va a `descartados` con el motivo «no respaldado: …».
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Callable

from script_engine import evidence as ev

MODELO, ESFUERZO = "gpt-6.1-sol", "high"
PROMPT_VERSION = "f23-1"           # f12-1: sin criterios (Ycuá F12) · f14-1: criterios (Orleans F14) · f15-1: historia y escenas
                                   # · f22-1: ejemplos del caso inventado (Puerto Cardal), instituciones en personas
                                   # · f23-1: cronología con la fecha que haya (año, mes o día) y conteos con piso más bajo
PROMPT_VERSION_CASO = "f44-1"      # F44 (lab, A/B): el mismo prompt con el <caso> de 4 líneas (convención del repo)
PROMPT_VERSION_F22 = "f22-1"       # F23: la v2.1 de F22 sigue con system("f22-1"), byte-idéntica
PROMPT_VERSION_F15 = "f15-1"       # F22: el sistema v2 de F15 sigue disponible con system("f15-1"), byte-idéntico
MAX_LEV = 3
SECCIONES = ("escenas", "contradicciones", "decisiones", "versiones", "personas", "personas_descartadas", "cifras",
             "cronologia", "hechos", "citas", "descartados")
HISTORIA = ("humanos_candidatos", "giros", "pico", "pregunta_final")   # F15: `historia` (pico y pregunta: un objeto)
SENT_STOP = {"entre", "sobre", "desde", "hasta", "total", "todo", "toda", "todos", "todas", "cada", "otro", "otra",
             "como", "pero", "para", "porque", "donde", "cuando", "mientras", "muy", "mucho", "mucha", "poco", "durante"}
CRITERIOS = {1: "error de extracción: gana el pasaje", 2: "variantes de un nombre: forma oficial o judicial; si no, la más repetida",
             3: "conteos: cifra oficial; si no, la más repetida", 4: "hecho disputado: no se resuelve (versiones)",
             5: "horas y fechas: la que coincide en 2 o más fuentes; si ninguna, aproximada"}

_IDS = {"type": "ARRAY", "items": {"type": "STRING"}}
_VERSIONES = {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
    "dice": {"type": "STRING"}, "doc_id": {"type": "STRING"}, "offset": {"type": "INTEGER"}, "ids": _IDS},
    "required": ["dice", "doc_id", "offset", "ids"]}}
SCHEMA: dict[str, Any] = {
    "type": "OBJECT",
    "properties": {
        "personas": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "nombre": {"type": "STRING"}, "rol": {"type": "STRING"},
            "variantes": {"type": "ARRAY", "items": {"type": "STRING"}}, "ids": _IDS},
            "required": ["nombre", "rol", "variantes", "ids"]}},
        "cronologia": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "fecha": {"type": "STRING"}, "hora": {"type": "STRING"}, "evento": {"type": "STRING"},
            "aproximada": {"type": "BOOLEAN"}, "ids": _IDS},
            "required": ["fecha", "hora", "evento", "aproximada", "ids"]}},
        "historia": {"type": "OBJECT", "properties": {
            "humanos_candidatos": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
                "nombre": {"type": "STRING"}, "rol": {"type": "STRING"}, "arco": {"type": "STRING"}, "ids": _IDS,
                "citas_verificadas": {"type": "INTEGER"}},
                "required": ["nombre", "rol", "arco", "ids", "citas_verificadas"]}},
            "giros": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
                "orden": {"type": "INTEGER"}, "que_cambia": {"type": "STRING"}, "ids": _IDS},
                "required": ["orden", "que_cambia", "ids"]}},
            "pico": {"type": "OBJECT", "properties": {
                "que": {"type": "STRING"}, "por_que": {"type": "STRING"}, "ids": _IDS}, "required": ["que", "por_que", "ids"]},
            "pregunta_final": {"type": "OBJECT", "properties": {
                "pregunta": {"type": "STRING"}, "ids": _IDS}, "required": ["pregunta", "ids"]}},
            "required": ["humanos_candidatos", "giros", "pico", "pregunta_final"]},
        "escenas": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "donde": {"type": "STRING"}, "quien": {"type": "STRING"}, "que_pasa": {"type": "STRING"},
            "sentidos": {"type": "STRING"}, "ids": _IDS},
            "required": ["donde", "quien", "que_pasa", "sentidos", "ids"]}},
        "hechos": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "texto": {"type": "STRING"}, "nivel": {"type": "INTEGER"}, "sirve_para": {"type": "STRING"}, "ids": _IDS},
            "required": ["texto", "nivel", "sirve_para", "ids"]}},
        "cifras": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "que": {"type": "STRING"}, "valor": {"type": "STRING"}, "unidad": {"type": "STRING"},
            "fuente": {"type": "STRING"}, "ids": _IDS,
            "otras_versiones": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
                "valor": {"type": "STRING"}, "unidad": {"type": "STRING"}, "fuente": {"type": "STRING"}, "ids": _IDS},
                "required": ["valor", "unidad", "fuente", "ids"]}}},
            "required": ["que", "valor", "unidad", "fuente", "ids", "otras_versiones"]}},
        "citas": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "autor": {"type": "STRING"}, "rol": {"type": "STRING"}, "verificacion": {"type": "STRING"},
            "texto": {"type": "STRING", "description": "la cita en el idioma de su documento, sin traducir"},
            "original": {"type": "STRING"},
            "traduccion": {"type": "STRING", "description": "la cita en español si «texto» no está en español; si ya "
                                                            "está en español, vacío"},
            "ids": _IDS},
            "required": ["autor", "rol", "verificacion", "texto", "original", "ids"]}},
        "contradicciones": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "tema": {"type": "STRING"},
            "versiones": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
                "dice": {"type": "STRING"}, "doc_id": {"type": "STRING"}, "offset": {"type": "INTEGER"}, "ids": _IDS},
                "required": ["dice", "doc_id", "offset", "ids"]}}},
            "required": ["tema", "versiones"]}},
        "decisiones": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "tema": {"type": "STRING"}, "criterio": {"type": "INTEGER"}, "decision": {"type": "STRING"},
            "ids": _IDS, "otras_versiones": _VERSIONES},
            "required": ["tema", "criterio", "decision", "ids", "otras_versiones"]}},
        "versiones": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "tema": {"type": "STRING"}, "versiones": _VERSIONES}, "required": ["tema", "versiones"]}},
        "personas_descartadas": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "nombre": {"type": "STRING"}, "rol": {"type": "STRING"}, "motivo": {"type": "STRING"}, "ids": _IDS},
            "required": ["nombre", "rol", "motivo", "ids"]}},
        "descartados": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "que": {"type": "STRING"}, "motivo": {"type": "STRING"}, "ids": _IDS},
            "required": ["que", "motivo", "ids"]}},
    },
    "required": ["personas", "cronologia", "historia", "escenas", "hechos", "cifras", "citas", "contradicciones",
                 "decisiones", "versiones", "personas_descartadas", "descartados"],
}


# ═══════════════════════════════════════════════════════════════
#  Prompt (estructura de F11c: sistema = rol + tarea; usuario = datos + tarea al final)
# ═══════════════════════════════════════════════════════════════

# F23 §1.1/§1.2: el bloque SISTEMA de lab/hyperframes/f23/PROMPT_FICHA_v2_2.md, literal (test byte-idéntico
# contra el .md, extraído anclando en «## SISTEMA»).
SYSTEM_F23_1 = """<rol>Sos el documentalista de Misterios Sepultados, un canal de documentales de historia oscura en YouTube. Antes de que el guionista escriba, depurás el research de un caso real y armás su ficha: la única fuente de la escaleta y del guion. Lo que no está en la ficha no existe para ellos.</rol>
<tarea>
Leés el pool de research completo (cada ítem con su id, y cada evidencia con su documento y su posición) y devolvés la ficha del caso:
- personas: un nombre canónico por persona, su rol, las variantes del nombre que encontraste y sus ids. Si dos fuentes dan nombres distintos para la misma persona, no elegís: la persona va también a contradicciones. Las instituciones que deciden en el caso (un ministerio, una empresa, una dirección) van también en personas, con su rol institucional, para que la escaleta pueda nombrarlas.
- cronologia: los eventos en orden, con la fecha que el pool tenga (año, mes o día) y la hora si la hay, tal como están en el pool, y sus ids.
- historia: antes de listar hechos, decidís qué historia hay en este caso. Devolvés:
  - humanos_candidatos (2 a 4): personas con arco, es decir, que entran en el caso en un estado, les pasa algo y salen en otro. Para cada una: nombre canónico, rol, en una oración qué le pasa (entra → sufre → sale), qué ids la sostienen y cuántas citas verificadas tiene. Una persona sin cita verificada puede ser candidata, pero lo decís.
  - giros (3 a 6): los momentos en que la historia cambia de dirección (una orden, un aviso que no llega, una cifra que aparece, una negación oficial). Cada uno con sus ids y en qué orden pasan.
  - pico: el peor momento, el que todo lo anterior prepara. Uno solo, con sus ids y por qué es el pico.
  - pregunta_final: la pregunta que el caso deja abierta y que ningún documento cierra, con los ids que la sostienen.
- escenas (6 a 15): momentos concretos que se pueden ver. Cada escena en una o dos oraciones: dónde, quién, qué está pasando, y lo que un testigo o documento dice que se veía, se oía, se olía o se tocaba. Solo con lo que los ids permiten. Una escena sin ningún detalle sensorial en los datos no es escena: es hecho, y va a hechos.
- hechos: entre 40 y 80 según lo que el pool dé (nivel 1 entre 10 y 20); con un pool chico, menos hechos buenos valen más que relleno. Cada hecho lleva un campo nivel: 1 = sostiene la historia (sin él no se entiende el caso), 2 = apoyo (da contexto o escala). Además, cada hecho lleva el campo sirve_para: gancho, contexto, escalada, giro, pico, consecuencia o cierre.

Los ejemplos que siguen son de un caso que no es este (una estación de radio y faro en una isla, en los años sesenta). Copiá la forma, no el contenido: los ids van como D##, Q##, T## y ## es el número que tenga el id en ESTE pool.

Ejemplo de humano candidato:
{"nombre": "Elvira Soto", "rol": "telegrafista de la estación", "arco": "entra como empleada nueva el invierno del temporal, manda los telegramas pidiendo el barco y recibe las respuestas sin firma, sostiene la radio con las baterías del faro la noche en que se apaga el generador, y sale siendo la única que guardó el libro de telegramas", "ids": ["D##", "Q##", "T##"], "citas_verificadas": 3}

Ejemplo de giro:
{"orden": 2, "que_cambia": "La Dirección responde al primer pedido de barco con «mantener servicio»: la estación no se evacúa", "ids": ["T##", "Q##"]}

Ejemplo de escena:
{"donde": "Sala de radio de la estación, la noche en que se apaga el generador", "quien": "Elvira Soto, Raúl Bascuñán, las tres familias", "que_pasa": "el generador se apaga y Elvira sigue transmitiendo con las baterías del faro", "sentidos": "olor a querosén; ventanas tapadas con mantas; el ruido del generador que tose dos veces y el silencio después; una vela", "ids": ["T##", "D##", "Q##"]}

Ejemplo de hecho nivel 1:
{"texto": "El recuento de la comisión da dos muertos; las familias declaran tres.", "nivel": 1, "sirve_para": "consecuencia", "ids": ["D##", "D##"]}
- hechos: entre 40 y 80 hechos útiles para contar la historia, cada uno en una oración limpia, con sus ids de origen. Sin interpretación.
- cifras: una cifra por conteo (muertos, heridos, evacuados, personas adentro…), con su fuente y las otras versiones. Cada cifra con su unidad (personas, metros, grados, años, la moneda del caso…): nunca un número sin qué cuenta.
- citas: las mejores 10 a 25, con autor, rol, estado de verificación y el texto. Si hay un error evidente de transcripción, lo corregís en «texto» y dejás el texto del pool en «original»; si no corregís nada, «original» va vacío. Si «texto» no está en español, «traduccion» lleva la cita en español.
- cronologia: si la hora o la fecha no coincide en 2 o más fuentes, «aproximada» va en true.
- decisiones, versiones y contradicciones: cada conflicto entre fuentes lo resolvés con estos criterios, que valen para cualquier caso:
  1. Error de extracción (lo que dice el ítem del pool no coincide con lo que dice su pasaje): gana el pasaje.
  2. Variantes de un nombre: gana la forma del documento oficial o judicial; si no hay, la que más fuentes repiten.
  3. Conteos (muertos, heridos, personas): gana la cifra oficial; si no hay, la que más fuentes repiten. Las otras van en otras_versiones (el guion podrá decir «otras fuentes hablan de…»).
  4. Hechos disputados (quién dio una orden, si un aviso llegó a tiempo): no se resuelven. Van a «versiones», cada versión con su fuente, para que el guion las cuente como versiones.
  5. Horas y fechas: gana la que coincide en 2 o más fuentes; si ninguna coincide, se marca aproximada.
  Lo que resolvés con los criterios 1, 2, 3 o 5 va a «decisiones»: el tema, el número de criterio, la decisión en una oración, los ids que la sostienen y las otras versiones (cada una con su doc_id y su offset). Lo del criterio 4 va a «versiones». Lo que no cae en ningún criterio va a «contradicciones», con las versiones lado a lado, y no se resuelve. En las tres secciones, cada versión lleva su doc_id y su offset tal como están en la evidencia.
- personas_descartadas: personas que el research descartó (están en <descartados_del_research>) pero que la historia necesita, con su rol, el motivo por el que hacen falta y los ids del pool que las nombran.
- descartados: lo que dejás afuera por dudoso o fuera del caso, con el motivo en una línea.
En el pool, una evidencia que ya apareció en otro ítem va como «(= arriba)»: es el mismo pasaje del mismo documento.
Cada cifra, hora, fecha y cita que escribas tiene que estar en el texto de los ids que citás. No agregás nada que no esté en el pool.
</tarea>"""

# F22 §1.1: el bloque SISTEMA de lab/hyperframes/f22/PROMPT_FICHA_v2_1.md, literal (test byte-idéntico contra el .md,
# extraído anclando en «## SISTEMA»).
SYSTEM_F22_1 = """<rol>Sos el documentalista de Misterios Sepultados, un canal de documentales de historia oscura en YouTube. Antes de que el guionista escriba, depurás el research de un caso real y armás su ficha: la única fuente de la escaleta y del guion. Lo que no está en la ficha no existe para ellos.</rol>
<tarea>
Leés el pool de research completo (cada ítem con su id, y cada evidencia con su documento y su posición) y devolvés la ficha del caso:
- personas: un nombre canónico por persona, su rol, las variantes del nombre que encontraste y sus ids. Si dos fuentes dan nombres distintos para la misma persona, no elegís: la persona va también a contradicciones. Las instituciones que deciden en el caso (un ministerio, una empresa, una dirección) van también en personas, con su rol institucional, para que la escaleta pueda nombrarlas.
- cronologia: los eventos del día en orden, con la fecha y la hora tal como están en el pool, y sus ids.
- historia: antes de listar hechos, decidís qué historia hay en este caso. Devolvés:
  - humanos_candidatos (2 a 4): personas con arco, es decir, que entran en el caso en un estado, les pasa algo y salen en otro. Para cada una: nombre canónico, rol, en una oración qué le pasa (entra → sufre → sale), qué ids la sostienen y cuántas citas verificadas tiene. Una persona sin cita verificada puede ser candidata, pero lo decís.
  - giros (3 a 6): los momentos en que la historia cambia de dirección (una orden, un aviso que no llega, una cifra que aparece, una negación oficial). Cada uno con sus ids y en qué orden pasan.
  - pico: el peor momento, el que todo lo anterior prepara. Uno solo, con sus ids y por qué es el pico.
  - pregunta_final: la pregunta que el caso deja abierta y que ningún documento cierra, con los ids que la sostienen.
- escenas (8 a 15): momentos concretos que se pueden ver. Cada escena en una o dos oraciones: dónde, quién, qué está pasando, y lo que un testigo o documento dice que se veía, se oía, se olía o se tocaba. Solo con lo que los ids permiten. Una escena sin ningún detalle sensorial en los datos no es escena: es hecho, y va a hechos.
- hechos (60 a 80) con un campo nivel: 1 = sostiene la historia (sin él no se entiende el caso; entre 12 y 20), 2 = apoyo (da contexto o escala). Además, cada hecho lleva el campo sirve_para: gancho, contexto, escalada, giro, pico, consecuencia o cierre.

Los ejemplos que siguen son de un caso que no es este (una estación de radio y faro en una isla, en los años sesenta). Copiá la forma, no el contenido: los ids van como D##, Q##, T## y ## es el número que tenga el id en ESTE pool.

Ejemplo de humano candidato:
{"nombre": "Elvira Soto", "rol": "telegrafista de la estación", "arco": "entra como empleada nueva el invierno del temporal, manda los telegramas pidiendo el barco y recibe las respuestas sin firma, sostiene la radio con las baterías del faro la noche en que se apaga el generador, y sale siendo la única que guardó el libro de telegramas", "ids": ["D##", "Q##", "T##"], "citas_verificadas": 3}

Ejemplo de giro:
{"orden": 2, "que_cambia": "La Dirección responde al primer pedido de barco con «mantener servicio»: la estación no se evacúa", "ids": ["T##", "Q##"]}

Ejemplo de escena:
{"donde": "Sala de radio de la estación, la noche en que se apaga el generador", "quien": "Elvira Soto, Raúl Bascuñán, las tres familias", "que_pasa": "el generador se apaga y Elvira sigue transmitiendo con las baterías del faro", "sentidos": "olor a querosén; ventanas tapadas con mantas; el ruido del generador que tose dos veces y el silencio después; una vela", "ids": ["T##", "D##", "Q##"]}

Ejemplo de hecho nivel 1:
{"texto": "El recuento de la comisión da dos muertos; las familias declaran tres.", "nivel": 1, "sirve_para": "consecuencia", "ids": ["D##", "D##"]}
- hechos: entre 60 y 80 hechos útiles para contar la historia, cada uno en una oración limpia, con sus ids de origen. Sin interpretación.
- cifras: una cifra por conteo (muertos, heridos, evacuados, personas adentro…), con su fuente y las otras versiones. Cada cifra con su unidad (personas, metros, grados, años, la moneda del caso…): nunca un número sin qué cuenta.
- citas: las mejores 15 a 25, con autor, rol, estado de verificación y el texto. Si hay un error evidente de transcripción, lo corregís en «texto» y dejás el texto del pool en «original»; si no corregís nada, «original» va vacío. Si «texto» no está en español, «traduccion» lleva la cita en español.
- cronologia: si la hora o la fecha no coincide en 2 o más fuentes, «aproximada» va en true.
- decisiones, versiones y contradicciones: cada conflicto entre fuentes lo resolvés con estos criterios, que valen para cualquier caso:
  1. Error de extracción (lo que dice el ítem del pool no coincide con lo que dice su pasaje): gana el pasaje.
  2. Variantes de un nombre: gana la forma del documento oficial o judicial; si no hay, la que más fuentes repiten.
  3. Conteos (muertos, heridos, personas): gana la cifra oficial; si no hay, la que más fuentes repiten. Las otras van en otras_versiones (el guion podrá decir «otras fuentes hablan de…»).
  4. Hechos disputados (quién dio una orden, si un aviso llegó a tiempo): no se resuelven. Van a «versiones», cada versión con su fuente, para que el guion las cuente como versiones.
  5. Horas y fechas: gana la que coincide en 2 o más fuentes; si ninguna coincide, se marca aproximada.
  Lo que resolvés con los criterios 1, 2, 3 o 5 va a «decisiones»: el tema, el número de criterio, la decisión en una oración, los ids que la sostienen y las otras versiones (cada una con su doc_id y su offset). Lo del criterio 4 va a «versiones». Lo que no cae en ningún criterio va a «contradicciones», con las versiones lado a lado, y no se resuelve. En las tres secciones, cada versión lleva su doc_id y su offset tal como están en la evidencia.
- personas_descartadas: personas que el research descartó (están en <descartados_del_research>) pero que la historia necesita, con su rol, el motivo por el que hacen falta y los ids del pool que las nombran.
- descartados: lo que dejás afuera por dudoso o fuera del caso, con el motivo en una línea.
En el pool, una evidencia que ya apareció en otro ítem va como «(= arriba)»: es el mismo pasaje del mismo documento.
Cada cifra, hora, fecha y cita que escribas tiene que estar en el texto de los ids que citás. No agregás nada que no esté en el pool.
</tarea>"""

# F15: el sistema de la ficha v2 (f15-1), byte-idéntico: para los tests y para reproducir las fichas de F15–F21.
SYSTEM_F15_1 = """<rol>Sos el documentalista de Misterios Sepultados, un canal de documentales de historia oscura en YouTube. Antes de que el guionista escriba, depurás el research de un caso real y armás su ficha: la única fuente de la escaleta y del guion. Lo que no está en la ficha no existe para ellos.</rol>
<tarea>
Leés el pool de research completo (cada ítem con su id, y cada evidencia con su documento y su posición) y devolvés la ficha del caso:
- personas: un nombre canónico por persona, su rol, las variantes del nombre que encontraste y sus ids. Si dos fuentes dan nombres distintos para la misma persona, no elegís: la persona va también a contradicciones.
- cronologia: los eventos del día en orden, con la fecha y la hora tal como están en el pool, y sus ids.
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
- hechos: entre 60 y 80 hechos útiles para contar la historia, cada uno en una oración limpia, con sus ids de origen. Sin interpretación.
- cifras: una cifra por conteo (muertos, heridos, huérfanos, personas adentro…), con su fuente y las otras versiones. Cada cifra con su unidad (personas, °C, años, guaraníes…): nunca un número sin qué cuenta.
- citas: las mejores 15 a 25, con autor, rol, estado de verificación y el texto. Si hay un error evidente de transcripción, lo corregís en «texto» y dejás el texto del pool en «original»; si no corregís nada, «original» va vacío.
- cronologia: si la hora o la fecha no coincide en 2 o más fuentes, «aproximada» va en true.
- decisiones, versiones y contradicciones: cada conflicto entre fuentes lo resolvés con estos criterios, que valen para cualquier caso:
  1. Error de extracción (lo que dice el ítem del pool no coincide con lo que dice su pasaje): gana el pasaje.
  2. Variantes de un nombre: gana la forma del documento oficial o judicial; si no hay, la que más fuentes repiten.
  3. Conteos (muertos, heridos, personas): gana la cifra oficial; si no hay, la que más fuentes repiten. Las otras van en otras_versiones (el guion podrá decir «otras fuentes hablan de…»).
  4. Hechos disputados (quién dio una orden, cómo estaban las puertas): no se resuelven. Van a «versiones», cada versión con su fuente, para que el guion las cuente como versiones.
  5. Horas y fechas: gana la que coincide en 2 o más fuentes; si ninguna coincide, se marca aproximada.
  Lo que resolvés con los criterios 1, 2, 3 o 5 va a «decisiones»: el tema, el número de criterio, la decisión en una oración, los ids que la sostienen y las otras versiones (cada una con su doc_id y su offset). Lo del criterio 4 va a «versiones». Lo que no cae en ningún criterio va a «contradicciones», con las versiones lado a lado, y no se resuelve. En las tres secciones, cada versión lleva su doc_id y su offset tal como están en la evidencia.
- personas_descartadas: personas que el research descartó (están en <descartados_del_research>) pero que la historia necesita, con su rol, el motivo por el que hacen falta y los ids del pool que las nombran.
- descartados: lo que dejás afuera por dudoso o fuera del caso, con el motivo en una línea.
En el pool, una evidencia que ya apareció en otro ítem va como «(= arriba)»: es el mismo pasaje del mismo documento.
Cada cifra, hora, fecha y cita que escribas tiene que estar en el texto de los ids que citás. No agregás nada que no esté en el pool.
</tarea>"""


def system(version: str = PROMPT_VERSION) -> str:
    """F23: el sistema v2.2; `version="f22-1"` → la v2.1 de F22; `"f15-1"` → el v2 de F15."""
    return {PROMPT_VERSION_F15: SYSTEM_F15_1, PROMPT_VERSION_F22: SYSTEM_F22_1}.get(version, SYSTEM_F23_1)


def _ev_lines(it: dict, seen: set | None = None) -> list[str]:
    """Las evidencias del ítem. Con `seen`, una evidencia (doc@offset + texto) ya escrita en otro ítem va solo como
    referencia («= arriba»): el pool entra completo sin repetir el mismo pasaje."""
    evs = it.get("evidencia") or [{"doc_id": it.get("doc_id"), "offset": it.get("offset"),
                                   "cita_literal": it.get("cita_literal")}]
    out = []
    for e in evs:
        ref, txt = f"{e.get('doc_id')}@{e.get('offset')}", e.get("cita_literal") or ""
        if seen is not None and (ref, txt) in seen:
            out.append(f"    {ref}: (= arriba)")
            continue
        if seen is not None:
            seen.add((ref, txt))
        out.append(f"    {ref}: «{txt}»")
    return out


def item_line(it: dict, seen: set | None = None) -> list[str]:
    """Un ítem del pool, compacto: lo que dice, sus campos de fecha/hora/valor y TODAS sus evidencias."""
    k, i = it["_kind"], it["id"]
    if k == "datos":
        head = f"[{i}] {it.get('texto')} · tipo {it.get('tipo')} · valor {it.get('valor')} · fecha {it.get('fecha')}"
    elif k == "cronologia":
        head = (f"[{i}] {it.get('evento')} · fecha {it.get('fecha')} · hora {it.get('hora')} · "
                f"lugar {it.get('lugar')}")
    elif k == "lugares":
        head = f"[{i}] {it.get('nombre')} · {it.get('rol')}"
    elif k == "citas":
        v = (it.get("verificacion") or {}).get("estado") or "sin verificar"
        head = (f"[{i}] CITA «{it.get('texto')}» — {it.get('autor')} ({it.get('rol')}) · {v} · fecha "
                f"{it.get('fecha')}")
    else:
        var = ", ".join(it.get("variantes_nombre") or [])
        head = f"[{i}] {it.get('nombre')} · {it.get('rol')}" + (f" · variantes: {var}" if var else "")
    return [head] + _ev_lines(it, seen)


def pool_section(pool: dict) -> str:
    its = ev.items(pool)
    out: list[str] = []
    seen: set = set()
    for k in ("personajes", "cronologia", "datos", "citas", "lugares"):
        sub = [x for x in its.values() if x["_kind"] == k]
        out.append(f"<{k} n=\"{len(sub)}\">")
        for x in sub:
            out += item_line(x, seen)
        out.append(f"</{k}>")
    gone = [d for d in pool.get("_descartados") or [] if str(d.get("kind") or "").startswith("personajes")]
    out.append(f"<descartados_del_research n=\"{len(gone)}\">")
    out += [f"  {d.get('texto')} ({d.get('doc_id') or d.get('bloque')}): {d.get('motivo')}" for d in gone]
    out.append("</descartados_del_research>")
    return "\n".join(out)


def caso_block(title: str, caso: dict | None = None) -> str:
    """F44: sin `caso`, `<caso>{title}</caso>` (byte-idéntico a f23-1). Con `caso` (angle/mystery/reveal del topic), las
    mismas 4 líneas que ya recibe la escaleta (`m01a_escaleta.build_prompt_v2`), con su mismo «-» si falta una."""
    if caso is None:
        return f"<caso>{title}</caso>"
    return (f"<caso>\nTÍTULO: {title}\nÁNGULO: {caso.get('angle') or '-'}\nMISTERIO: {caso.get('mystery') or '-'}\n"
            f"REVELACIÓN: {caso.get('reveal') or '-'}\n</caso>")


def prompt(pool: dict, title: str, caso: dict | None = None) -> str:
    return f"""{caso_block(title, caso)}

<pool>
{pool_section(pool)}
</pool>

<tarea>Con el pool de arriba, armá la ficha del caso: personas, personas_descartadas, cronologia, historia, escenas (6–15), hechos (40–80, con nivel y sirve_para), cifras (con unidad), citas (10–25), decisiones (con su criterio), versiones, contradicciones (las que ningún criterio resuelve) y descartados. Devolvé el JSON del esquema.</tarea>"""


# ═══════════════════════════════════════════════════════════════
#  Chequeo determinista
# ═══════════════════════════════════════════════════════════════

_NUM = re.compile(r"\d+(?:[.,]\d+)*")
_HORA = re.compile(r"\b(\d{1,2})[:.h](\d{2})\b")
_ISO = re.compile(r"\b\d{4}-\d{2}(?:-\d{2})?\b")
_ID = re.compile(r"\b[DTQPLF]\d{2,3}\b")      # ids del pool y documentos (D20, P62, F15…): no son cifras


def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def _num_forms(tok: str) -> set[str]:
    """«4.000» → {4000}; «4,6» → {4.6, 46}; «08» → {8}. Con varias formas, basta que una coincida."""
    out = {tok.replace(".", "").replace(",", "")}
    if re.fullmatch(r"\d+[.,]\d{1,2}", tok):
        out.add(tok.replace(",", "."))
    return {x.lstrip("0") or "0" for x in out}


# F15b §1.3: antes de comparar cifras se normalizan los dos lados: sin «US$», «G.», «$», «°» ni espacios entre grupos
# de miles (4.500 = 4500 = 4,500 = 4 500). Ampliación pedida por Omar (el afloje literal no recuperaba ninguna de las 12
# cifras de Ycuá): un número con escala («4.500 millones», «2 mil») vale también por su valor completo, y los números en
# letras («seis», «quince días», «treinta y cinco») cuentan como cifras del texto. «un» y «una» no: son artículos y
# respaldarían cualquier «1» (revisor F15b); sí «uno» y «veintiún»/«veintiuna».
_SCALE = re.compile(r"(\d+(?:[.,]\d+)*)\s*(mil millones|millones|millón|mil)\b", re.I)
_UNITS = {"cero": 0, "uno": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6, "siete": 7,
          "ocho": 8, "nueve": 9, "diez": 10, "once": 11, "doce": 12, "trece": 13, "catorce": 14, "quince": 15,
          "dieciseis": 16, "diecisiete": 17, "dieciocho": 18, "diecinueve": 19, "veinte": 20, "veintiun": 21,
          "veintiuno": 21, "veintiuna": 21, "veintidos": 22, "veintitres": 23, "veinticuatro": 24, "veinticinco": 25,
          "veintiseis": 26, "veintisiete": 27, "veintiocho": 28, "veintinueve": 29}
_TENS = {"treinta": 30, "cuarenta": 40, "cincuenta": 50, "sesenta": 60, "setenta": 70, "ochenta": 80, "noventa": 90}
_HUND = {"cien": 100, "ciento": 100, "doscientos": 200, "doscientas": 200, "trescientos": 300, "trescientas": 300,
         "cuatrocientos": 400, "cuatrocientas": 400, "quinientos": 500, "quinientas": 500, "seiscientos": 600,
         "seiscientas": 600, "setecientos": 700, "setecientas": 700, "ochocientos": 800, "ochocientas": 800,
         "novecientos": 900, "novecientas": 900}


def _canon(text: str) -> str:
    t = re.sub(r"US\$|G\.(?=\s*\d)|\$|°", " ", text or "")
    return re.sub(r"(?<=\d)[ \u00a0](?=\d{3}\b)", "", t)


def _plain_int(tok: str) -> float | None:
    """«4.500» → 4500; «4,5» → 4.5; «2.250.000» → 2250000."""
    if re.fullmatch(r"\d+[.,]\d{1,2}", tok):
        return float(tok.replace(",", "."))
    try:
        return float(tok.replace(".", "").replace(",", ""))
    except ValueError:
        return None


def _scaled(text: str) -> set[str]:
    out = set()
    for m in _SCALE.finditer(text):
        v = _plain_int(m.group(1))
        if v is None:
            continue
        mult = {"mil millones": 1e9, "millones": 1e6, "millón": 1e6, "mil": 1e3}[m.group(2).lower()]
        out.add(str(int(round(v * mult))))
    return out


def word_numbers(text: str) -> set[str]:
    """Números en letras del texto («seis» → 6, «treinta y cinco» → 35, «ciento veinte» → 120, «dos mil» → 2000)."""
    out: set[str] = set()
    for clause in re.split(r"[,;.:!?()\"«»]", ev.norm(text)):           # un número no cruza la puntuación
        out |= _clause_numbers(re.findall(r"[a-z]+", clause))
    return out


def _clause_numbers(ws: list[str]) -> set[str]:
    out: set[str] = set()
    k = 0
    while k < len(ws):
        total, cur, used = 0, 0, 0
        j = k
        while j < len(ws):
            w = ws[j]
            if w in _HUND:
                cur += _HUND[w]
            elif w in _TENS:
                cur += _TENS[w]
            elif w in _UNITS:
                cur += _UNITS[w]
            elif w == "mil" and (cur or used == 0):
                total += (cur or 1) * 1000
                cur = 0
            elif w == "y" and used and j + 1 < len(ws) and ws[j + 1] in _UNITS:
                pass
            else:
                break
            used += 1
            j += 1
        if used:
            out.add(str(total + cur))
            k = j
        else:
            k += 1
    return out


def numbers(text: str) -> set[str]:
    t = _canon(text)
    return {f for x in _NUM.findall(t) for f in _num_forms(x)} | _scaled(t) | word_numbers(t)


def hours(text: str) -> set[str]:
    return {f"{int(h)}:{m}" for h, m in _HORA.findall(text or "")}


def source_text(ids: list[str], its: dict) -> str:
    """Todo lo que dicen esos ids: texto, campos de fecha/hora/valor, cita literal y evidencias."""
    parts = []
    for i in ids:
        it = its.get(i) or {}
        for f in ("texto", "texto_original", "texto_es", "evento", "nombre", "rol", "autor", "fecha", "hora", "valor",
                  "lugar", "cita_literal"):
            if it.get(f):
                parts.append(str(it[f]))
        parts += [str(e.get("cita_literal") or "") for e in it.get("evidencia") or []]
        parts.append(str(((it.get("verificacion") or {}).get("cita_original")) or ""))
    return "\n".join(parts)


def unsupported(text: str, src: str) -> list[str]:
    """Cifras, horas y fechas de `text` que no aparecen en `src` (las horas y fechas ISO se miran enteras)."""
    out = [f"hora {h}" for h in sorted(hours(text)) if h not in hours(src)]
    out += [f"fecha {d}" for d in _ISO.findall(text or "") if d not in src]
    rest = _canon(_ISO.sub(" ", _HORA.sub(" ", _ID.sub(" ", text or ""))))
    src_n = numbers(src)
    for m in _NUM.finditer(rest):
        tok = m.group(0)
        forms = _num_forms(tok) | _scaled(rest[m.start():m.start() + len(tok) + 14])
        if not (forms & src_n):
            out.append(f"cifra {tok}")
    return out


def _strings(x: Any, skip: tuple[str, ...] = ("ids", "original", "doc_id", "offset", "nivel", "orden",
                                              "citas_verificadas", "aproximada", "sirve_para")) -> list[str]:
    if isinstance(x, dict):
        return [s for k, v in x.items() if k not in skip for s in _strings(v, skip)]
    if isinstance(x, list):
        return [s for v in x for s in _strings(v, skip)]
    return [str(x)] if isinstance(x, (str, int, float)) and str(x) else []


def _all_ids(section: str, item: dict) -> list[str]:
    """Los ids que cita un ítem (en contradicciones y versiones, los de sus versiones; en decisiones, también los de
    sus otras versiones)."""
    vs = item.get("versiones") or []
    if section == "decisiones":
        vs = item.get("otras_versiones") or []
    return list(dict.fromkeys(list(item.get("ids") or []) + [i for v in vs for i in v.get("ids") or []]))


def _versions_problems(vs: list[dict], its: dict) -> list[str]:
    """Cada versión: con ids, su doc_id@offset es una evidencia de esos ids y sus cifras están en su texto."""
    out: list[str] = []
    for v in vs:
        vids = v.get("ids") or []
        if not vids:
            out.append(f"versión sin ids («{str(v.get('dice'))[:40]}»)")
            continue
        evs = {(e.get("doc_id"), e.get("offset")) for i in vids
               for e in (its[i].get("evidencia") or []) + [{"doc_id": its[i].get("doc_id"),
                                                             "offset": its[i].get("offset")}]}
        if (v.get("doc_id"), v.get("offset")) not in evs:
            out.append(f"{v.get('doc_id')}@{v.get('offset')} no es evidencia de {', '.join(vids)}")
        out += unsupported(str(v.get("dice") or ""), source_text(vids, its))
    return out


def sentidos_problems(sentidos: str, src: str) -> list[str]:
    """F15b §1.3: basta UNA palabra de contenido (≥ 4 letras, no de la lista de vacías) del campo `sentidos` cuya raíz
    (5 letras) aparezca en el texto de sus ids. (F15 pedía una por tramo.)"""
    if not str(sentidos or "").strip():
        return ["la escena no trae sentidos"]
    srcw = set(re.findall(r"[a-z0-9ñ]+", ev.norm(src)))
    ws = [w for w in re.findall(r"[a-zñ]+", ev.norm(sentidos)) if len(w) >= 4 and w not in SENT_STOP]
    if ws and not any(sw.startswith(w[:5]) for w in ws for sw in srcw):
        return [f"ningún sentido de la escena («{str(sentidos)[:60]}») está en sus ids"]
    return []


def problems(section: str, item: dict, its: dict, gone: set[str] | None = None) -> list[str]:
    """Por qué un ítem de la ficha no está respaldado ([] = está). `gone`: nombres (normalizados) de las personas que
    el pool descartó (`_descartados`), para `personas_descartadas`."""
    ids = _all_ids(section, item)
    if not ids:
        return ["sin ids"]
    bad = [i for i in ids if i not in its]
    if bad:
        return [f"id inexistente {', '.join(bad)}"]
    if section == "descartados":
        return []
    out: list[str] = []
    if section in ("contradicciones", "versiones"):
        return _versions_problems(item.get("versiones") or [], its)
    if section == "decisiones":
        if item.get("criterio") not in (1, 2, 3, 5):
            out.append(f"criterio {item.get('criterio')} no es de decisiones (1, 2, 3 o 5; el 4 va a versiones)")
        out += unsupported(str(item.get("decision") or ""), source_text(item.get("ids") or [], its))
        return out + _versions_problems(item.get("otras_versiones") or [], its)
    if section == "personas_descartadas":
        nom = ev.norm(item.get("nombre") or "")
        if not nom or not any(nom in g or g in nom for g in gone or set()):
            out.append(f"«{item.get('nombre')}» no está entre los descartados del pool")
        from script_engine import nombres
        sur = nombres.apellido(item.get("nombre") or "")               # F21: nombres.py
        if sur and not nombres.menciona(source_text(ids, its), sur):
            out.append(f"sus ids no nombran a «{item.get('nombre')}»")
        return out + unsupported(f"{item.get('nombre')} {item.get('rol')}", source_text(ids, its))
    if section == "cifras":
        out += unsupported(" ".join(_strings({k: item.get(k) for k in ("que", "valor")})), source_text(ids, its))
        for v in item.get("otras_versiones") or []:
            vids = [i for i in v.get("ids") or [] if i in its]
            if len(vids) != len(v.get("ids") or []) or not vids:
                out.append(f"otra versión con ids inexistentes o vacíos ({v.get('ids')})")
                continue
            out += unsupported(str(v.get("valor") or ""), source_text(vids, its))
        return out
    src = source_text(ids, its)
    if section == "escenas":
        out += sentidos_problems(str(item.get("sentidos") or ""), src)
    if section == "citas":
        orig = str(item.get("original") or "").strip()
        texto = str(item.get("texto") or "").strip()
        base = orig or texto
        if orig and orig != texto:
            d = levenshtein(texto, orig)
            if d > MAX_LEV:
                out.append(f"cita corregida a {d} caracteres de su original (máximo {MAX_LEV})")
        if ev.norm(base) not in ev.norm(src):
            out.append("el texto de la cita no está en sus ids")
        out += unsupported(texto, src)
        return out
    out += unsupported(" ".join(_strings(item)), src)
    return out


def check(ficha: dict, pool: dict) -> tuple[dict, list[dict]]:
    """La ficha con solo lo respaldado; lo que falla va a `descartados` («no respaldado: …»). Devuelve también la
    lista de lo que sacó el chequeo (para el reporte)."""
    its = ev.items(pool)
    gone = {ev.norm(d.get("texto") or "") for d in pool.get("_descartados") or []
            if str(d.get("kind") or "").startswith("personajes") and d.get("texto")}
    out: dict[str, list] = {s: [] for s in SECCIONES}
    sacados: list[dict] = []
    for s in SECCIONES:
        for item in ficha.get(s) or []:
            pr = problems(s, item, its, gone)
            if not pr:
                out[s].append(item)
                continue
            ids = _all_ids(s, item)
            rec = {"que": f"[{s}] {_label(s, item)}", "motivo": "no respaldado: " + "; ".join(pr),
                   "ids": [i for i in ids if i in its], "seccion": s, "item": item}
            sacados.append(rec)
            out["descartados"].append({k: rec[k] for k in ("que", "motivo", "ids")})
    if "historia" in ficha:                                   # F15: humanos, giros, pico y pregunta, el mismo control
        hist = ficha.get("historia") or {}
        oh: dict[str, Any] = {"humanos_candidatos": [], "giros": [], "pico": None, "pregunta_final": None}
        for key in HISTORIA:
            val = hist.get(key)
            for item in (val if isinstance(val, list) else [val] if isinstance(val, dict) else []):
                pr = problems("historia", item, its, gone)
                if not pr:
                    if isinstance(oh[key], list):
                        oh[key].append(item)
                    else:
                        oh[key] = item
                    continue
                rec = {"que": f"[historia.{key}] {_label('historia', item)}", "motivo": "no respaldado: " + "; ".join(pr),
                       "ids": [i for i in item.get("ids") or [] if i in its], "seccion": f"historia.{key}", "item": item}
                sacados.append(rec)
                out["descartados"].append({k: rec[k] for k in ("que", "motivo", "ids")})
        out["historia"] = oh
    return out, sacados


def _label(s: str, item: dict) -> str:
    key = {"personas": "nombre", "cronologia": "evento", "hechos": "texto", "cifras": "que", "citas": "texto",
           "contradicciones": "tema", "descartados": "que", "decisiones": "tema", "versiones": "tema",
           "personas_descartadas": "nombre", "escenas": "que_pasa"}.get(s)
    if s == "historia":
        key = next((k for k in ("nombre", "que_cambia", "que", "pregunta") if item.get(k)), "ids")
    return str(item.get(key) or "")[:140]


# ═══════════════════════════════════════════════════════════════
#  Corrida y salidas
# ═══════════════════════════════════════════════════════════════

def build(pool: dict, title: str, *, call: Callable[..., dict], caso: dict | None = None) -> dict:
    return call(prompt(pool, title, caso), system_instruction=system(), response_schema=SCHEMA,
                description="ficha_caso")


def counts(ficha: dict) -> dict[str, int]:
    out = {s: len(ficha.get(s) or []) for s in SECCIONES}
    if "historia" in ficha:
        h = ficha.get("historia") or {}
        out = {"humanos_candidatos": len(h.get("humanos_candidatos") or []), "giros": len(h.get("giros") or []),
               "pico": int(bool(h.get("pico"))), "pregunta_final": int(bool(h.get("pregunta_final"))), **out}
    return out


def _ids(item: dict) -> str:
    ids = item.get("ids") or [i for v in item.get("versiones") or [] for i in v.get("ids") or []]
    return f" <sub>{', '.join(dict.fromkeys(ids))}</sub>" if ids else ""


def markdown(ficha: dict, meta: dict) -> str:
    """FICHA_<tag>.md para leer en el teléfono: conteos arriba y las contradicciones primero."""
    c = counts(ficha)
    L = [f"# Ficha del caso — {meta.get('titulo')}", "",
         f"<sub>{meta.get('topic')} · {meta.get('modelo')} {meta.get('esfuerzo')} · prompt {PROMPT_VERSION} · pool md5 "
         f"{str(meta.get('pool_md5'))[:8]} · US$ {meta.get('usd', 0):.3f}</sub>", "",
         " · ".join(f"**{s}** {n}" for s, n in c.items()), "",
         f"El chequeo determinista sacó {meta.get('sacados', 0)} ítem(s) (están en descartados, «no respaldado»).", ""]
    if "historia" in ficha:
        h = ficha.get("historia") or {}
        L += ["## Historia", "", "### Humanos candidatos", ""]
        L += [f"- **{x.get('nombre')}** — {x.get('rol')} · {x.get('arco')} · citas verificadas: "
              f"{x.get('citas_verificadas')}{_ids(x)}" for x in h.get("humanos_candidatos") or []]
        L += ["", "### Giros", ""]
        L += [f"{x.get('orden')}. {x.get('que_cambia')}{_ids(x)}"
              for x in sorted(h.get("giros") or [], key=lambda g: g.get("orden") or 0)]
        pk, pq = h.get("pico") or {}, h.get("pregunta_final") or {}
        L += ["", "### Pico", "", f"{pk.get('que')} — {pk.get('por_que')}{_ids(pk)}" if pk else "(sin pico respaldado)",
              "", "### Pregunta final", "", f"{pq.get('pregunta')}{_ids(pq)}" if pq else "(sin pregunta respaldada)", ""]
        L += ["## Escenas", ""]
        L += [f"{k}. **{x.get('donde')}** · {x.get('quien')} — {x.get('que_pasa')} · *{x.get('sentidos')}*{_ids(x)}"
              for k, x in enumerate(ficha.get("escenas") or [], 1)]
        L.append("")
    L += ["## Contradicciones (decide Omar)", ""]
    for x in ficha["contradicciones"]:
        L.append(f"**{x.get('tema')}**")
        for v in x.get("versiones") or []:
            L.append(f"- {v.get('dice')} <sub>{v.get('doc_id')}@{v.get('offset')} · {', '.join(v.get('ids') or [])}</sub>")
        L.append("")
    if ficha.get("decisiones") is not None:
        L += ["## Decisiones (resueltas con un criterio)", ""]
        for x in ficha["decisiones"]:
            L.append(f"**{x.get('tema')}** · criterio {x.get('criterio')} ({CRITERIOS.get(x.get('criterio'), '?')})")
            L.append(f"- decisión: {x.get('decision')}{_ids(x)}")
            for v in x.get("otras_versiones") or []:
                L.append(f"- otra versión: {v.get('dice')} <sub>{v.get('doc_id')}@{v.get('offset')} · "
                         f"{', '.join(v.get('ids') or [])}</sub>")
            L.append("")
        L += ["## Versiones (hechos disputados, criterio 4: no se resuelven)", ""]
        for x in ficha["versiones"]:
            L.append(f"**{x.get('tema')}**")
            for v in x.get("versiones") or []:
                L.append(f"- {v.get('dice')} <sub>{v.get('doc_id')}@{v.get('offset')} · "
                         f"{', '.join(v.get('ids') or [])}</sub>")
            L.append("")
    L += ["## Personas", ""]
    for x in ficha["personas"]:
        var = [v for v in x.get("variantes") or [] if v != x.get("nombre")]
        L.append(f"- **{x.get('nombre')}** — {x.get('rol')}" + (f" (también: {', '.join(var)})" if var else "")
                 + _ids(x))
    if ficha.get("personas_descartadas") is not None:
        L += ["", "## Personas que el research descartó y la historia necesita", ""]
        L += [f"- **{x.get('nombre')}** — {x.get('rol')} · {x.get('motivo')}{_ids(x)}"
              for x in ficha["personas_descartadas"]]
    L += ["", "## Cifras", ""]
    for x in ficha["cifras"]:
        L.append(f"- **{x.get('que')}:** {x.get('valor')} {x.get('unidad')} · {x.get('fuente')}" + _ids(x))
        for v in x.get("otras_versiones") or []:
            L.append(f"  - otra versión: {v.get('valor')} {v.get('unidad')} · {v.get('fuente')}"
                     f" <sub>{', '.join(v.get('ids') or [])}</sub>")
    L += ["", "## Cronología", ""]
    for x in ficha["cronologia"]:
        h = f" {x.get('hora')}" if x.get("hora") and str(x.get("hora")).lower() not in ("null", "none") else ""
        ap = " <sub>(aproximada)</sub>" if x.get("aproximada") else ""
        L.append(f"- **{x.get('fecha')}{h}**{ap} — {x.get('evento')}" + _ids(x))
    L += ["", "## Hechos", ""]
    L += [f"{k}. {x.get('texto')}" + (f" <sub>nivel {x['nivel']} · {x.get('sirve_para')}</sub>" if x.get("nivel") else "")
          + _ids(x) for k, x in enumerate(ficha["hechos"], 1)]
    L += ["", "## Citas", ""]
    for x in ficha["citas"]:
        fix = f" <sub>(original: «{x.get('original')}»)</sub>" if x.get("original") and x["original"] != x.get("texto") else ""
        fix += f" <sub>(traducción: «{x['traduccion']}»)</sub>" if x.get("traduccion") else ""
        L.append(f"- «{x.get('texto')}» — **{x.get('autor')}**, {x.get('rol')} · {x.get('verificacion')}{fix}{_ids(x)}")
    L += ["", "## Descartados", ""]
    L += [f"- {x.get('que')} — {x.get('motivo')}{_ids(x)}" for x in ficha["descartados"]]
    return "\n".join(L) + "\n"


def load(topic_id: str, steps_dir: Path | None = None) -> dict | None:
    """La ficha del topic (`_steps/<topic>/ficha_caso.json`) o None si no hay."""
    if steps_dir is None:
        from script_engine.m01a_skeleton import STEPS_DIR as steps_dir
    p = Path(steps_dir) / topic_id / "ficha_caso.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def id_texts(ficha: dict | None) -> dict[str, str]:
    """F14 §1.3: el texto limpio de cada id según la ficha. Una cita va con su texto corregido; una cifra, con su
    unidad y sus otras versiones; un evento, con fecha y hora; si no, el primer hecho que lo cita. Lo que la ficha no
    menciona no está (el guion usa el texto del pool)."""
    out: dict[str, str] = {}
    if not ficha:
        return out

    def put(ids, text):
        for i in ids or []:
            out.setdefault(i, text)
    for c in ficha.get("citas") or []:                   # F19: con traducción, el guion usa la traducción
        put([i for i in c.get("ids") or [] if i.startswith("Q")],
            f"«{c.get('traduccion') or c.get('texto')}» — {c.get('autor')}")
    for c in ficha.get("cronologia") or []:
        h = c.get("hora") if c.get("hora") and str(c.get("hora")).lower() not in ("null", "none", "") else ""
        put([i for i in c.get("ids") or [] if i.startswith("T")],
            f"{c.get('evento')} ({c.get('fecha')}{', ' + h if h else ''}{', aproximada' if c.get('aproximada') else ''})")
    for c in ficha.get("cifras") or []:
        otras = "; ".join(f"{v.get('valor')} {v.get('unidad')}" for v in c.get("otras_versiones") or [])
        put(c.get("ids"), f"{c.get('que')}: {c.get('valor')} {c.get('unidad')}"
                          + (f" (otras fuentes: {otras})" if otras else ""))
    for c in ficha.get("hechos") or []:
        put(c.get("ids"), str(c.get("texto")))
    return out


def esfuerzo_de(modelo: str | None) -> str:
    """F25b: Sol en `ESFUERZO`; Claude en el de la ficha de claude_helpers (medium)."""
    if modelo and modelo.startswith("claude"):
        import claude_helpers
        return claude_helpers.ESFUERZO_POR_ETAPA["ficha"]
    return ESFUERZO


def call_for(modelo: str | None = None, *, crudo: Path | None = None,
             post: Callable[[dict], dict] | None = None) -> Callable[..., dict]:
    """F25b: el `call` de la ficha. Sin modelo, gpt-6.1-sol high; un modelo de Claude va por claude_helpers con su regla
    (streaming, max_tokens 100 000, effort medium, sin esquema forzado: `ficha_caso` está en SALIDA_GRANDE y el JSON se
    saca del texto). `crudo`: cada respuesta de la API, tal cual, se guarda ahí (que no se pierda una salida que no se
    pudo leer). `post` (tests, frenos de costo) reemplaza el envío."""
    modelo = modelo or MODELO
    if modelo.startswith("claude"):
        import claude_helpers as hx
    else:
        import gpt_helpers as hx
    envio = post or hx._post

    def _post(body: dict) -> dict:
        r = envio(body)
        if crudo is not None:
            crudo.parent.mkdir(parents=True, exist_ok=True)
            crudo.write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
        return r
    return hx.make_call(modelo, esfuerzo_de(modelo), post=_post)


def run(topic_id: str, *, steps_dir: Path, title: str, tag: str, out_dirs: list[Path] = (),
        call: Callable[..., dict] | None = None, modelo: str | None = None, caso: dict | None = None) -> dict:
    """Lee el pool, hace UNA llamada, chequea y escribe ficha_caso.json + FICHA_<tag>.md en `_steps/<topic>/` y en
    cada `out_dirs`. `call` por defecto: `call_for(modelo)` (sin modelo, gpt-6.1-sol high), con la respuesta cruda en
    `_steps/<topic>/ficha_respuesta_cruda.json`. F44: `caso` (angle/mystery/reveal) va al bloque `<caso>`
    (`prompt_version` f44-1); sin él, todo igual que hoy."""
    raw_pool = (steps_dir / topic_id / "00_pool_v3.json").read_bytes()
    pool = json.loads(raw_pool.decode("utf-8"))
    if call is None:
        call = call_for(modelo, crudo=steps_dir / topic_id / "ficha_respuesta_cruda.json")
    raw = build(pool, title, call=call, caso=caso) or {}
    return save(topic_id, raw, raw_pool, steps_dir=steps_dir, title=title, tag=tag, out_dirs=out_dirs, modelo=modelo,
                prompt_version=PROMPT_VERSION_CASO if caso is not None else PROMPT_VERSION)


def save(topic_id: str, raw: dict, raw_pool: bytes, *, steps_dir: Path, title: str, tag: str,
         out_dirs: list[Path] = (), usd: float | None = None, modelo: str | None = None,
         prompt_version: str = PROMPT_VERSION) -> dict:
    """Chequeo determinista sobre la salida del modelo (`raw`) y escritura de ficha_caso.json + FICHA_<tag>.md.
    Re-aplicable sobre un crudo guardado, sin otra llamada."""
    pool = json.loads(raw_pool.decode("utf-8"))
    ficha, sacados = check(raw, pool)
    from cost_tracker import cost_tracker
    cv = cost_tracker.current_video
    meta = {"topic": topic_id, "titulo": title, "modelo": modelo or MODELO, "esfuerzo": esfuerzo_de(modelo),
            "prompt_version": prompt_version, "pool_md5": hashlib.md5(raw_pool).hexdigest(),
            "conteos_crudo": counts(raw), "conteos": counts(ficha), "sacados": len(sacados),
            "usd": usd if usd is not None else (round(cv.total_cost, 4) if cv else 0.0)}
    out = {**meta, **ficha, "chequeo": {"sacados": sacados}}
    md = markdown(ficha, meta)
    for d in [steps_dir / topic_id, *out_dirs]:
        d.mkdir(parents=True, exist_ok=True)
        (d / "ficha_caso.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
        (d / f"FICHA_{tag}.md").write_text(md, encoding="utf-8")
    return {"ficha": ficha, "meta": meta, "sacados": sacados, "crudo": raw}


def main(argv: list[str] | None = None) -> None:
    """F25b: python -m researcher_steps.ficha_caso <topic_id> [--modelo claude-opus-5-5] [--title …] [--tag …]"""
    import argparse
    import sys
    from script_engine.m01a_skeleton import STEPS_DIR
    ap = argparse.ArgumentParser(description="ficha del caso (ficha_caso.json + FICHA_<tag>.md en _steps/<topic>/)")
    ap.add_argument("topic_id")
    ap.add_argument("--modelo", default=None, help=f"por defecto {MODELO}; un claude-* va por claude_helpers")
    ap.add_argument("--title", default=None, help="por defecto el video_title de topics_db")
    ap.add_argument("--tag", default=None)
    a = ap.parse_args(argv)
    sys.stdout.reconfigure(encoding="utf-8")
    title = a.title
    if title is None:
        import fase1_5
        title = fase1_5._load_topic_by_id(a.topic_id).get("video_title") or a.topic_id
    res = run(a.topic_id, steps_dir=STEPS_DIR, title=title, tag=a.tag or a.topic_id, modelo=a.modelo)
    print(f"ficha {res['meta']['modelo']} ({res['meta']['esfuerzo']}): {res['meta']['conteos']} · sacados "
          f"{res['meta']['sacados']}")


if __name__ == "__main__":
    main()
