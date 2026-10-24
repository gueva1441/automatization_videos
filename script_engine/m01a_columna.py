"""
m01a_columna.py — F17: la columna vertebral del caso (una página) antes de la escaleta.

Sol high, UNA llamada con el SISTEMA literal de `lab/hyperframes/f17/PROMPT_COLUMNA_v1.md` y el usuario = caso + ficha
completa (la misma sección que usa la escaleta v2) + tarea literal. Salida: humano, pico, siete filas (qué pasa /
termina / personas / ids) y afuera.

Chequeo determinista (estructura e ids, nada de estilo): 7 caps, el humano es persona de la ficha, los ids existen y
las personas de cada cap existen en la ficha. Si falla, UNA regeneración; si vuelve a fallar, ColumnaError (PARADA).
Métrica informativa: personas distintas con nombre en toda la columna.
F22 (v1.1): ejemplo del caso inventado de Puerto Cardal; QUIÉN DECIDE = `antagonista` {tipo persona | institucion |
ninguno, nombre, por_que, ids}, con el chequeo de `antagonista_problemas` (el mismo contrato que la escaleta v2.1).

Se guarda `_steps/<topic>/01a_columna.json`; `to_markdown` da la página legible (`COLUMNA_<tema>.md`).
"""
from __future__ import annotations

import copy
import json
import re
from pathlib import Path
from typing import Any, Callable

from script_engine import evidence as ev
from script_engine.m01a_skeleton import STEPS_DIR

PROMPT_VERSION = "f22-1"            # F22: columna v1.1 (caso inventado en el ejemplo, QUIÉN DECIDE)
PROMPT_VERSION_F17 = "f17-1"        # la v1 de F17: SYSTEM_F17_1 / TAREA_F17_1, byte-idénticos
REGENERACIONES = 1                  # F17 §1.1: si falla el chequeo, UNA regeneración; si vuelve a fallar, PARADA
CAPS = 7


class ColumnaError(ValueError):
    """La columna no pasó el chequeo después de la regeneración (PARADA)."""


# F22 §1.1: el bloque SISTEMA de lab/hyperframes/f22/PROMPT_COLUMNA_v1_1.md, literal (test byte-idéntico contra el
# .md, extraído anclando en «## SISTEMA»).
SYSTEM = """<rol>
Sos el guionista jefe de Misterios Sepultados, un canal de documentales de historia oscura en YouTube. Antes de armar la escaleta, decidís la columna vertebral de la historia: a quién seguimos, qué pasa en cada uno de los siete capítulos, dónde golpea y con qué termina. Trabajás solo con la ficha del caso. No inventás nombres, cifras, fechas ni citas.
</rol>

<que_es>
La columna es una página. Siete filas, una por capítulo, con dos cosas en cada una: qué pasa (los hechos y las personas que entran, en tres o cuatro frases) y con qué termina (la frase que deja la puerta abierta al siguiente). Arriba, el humano, quién decide y el pico. Abajo, qué dejaste afuera y por qué. No es el guion ni la escaleta: es la decisión. Alguien que no sabe nada del caso tiene que leerla en un minuto y entender qué video va a ver.
</que_es>

<oficio>
1. Un humano. El que tenga arco (entra, sufre, sale) y más momentos concretos. Lo seguimos del cap 1 al 7.
2. Pocas personas con nombre: cinco o seis en todo el video, además del humano. Una persona entra solo si hace algo que se ve o dice algo que se oye. Cada nombre que agregás le quita memoria al espectador para los que importan.
3. Quién decide: la persona o la institución a la que la ficha atribuye la decisión que causó el daño. Si la ficha no se lo atribuye a nadie, decís «ninguno» y por qué; no inventás un culpable.
4. Cap 1: el peor momento, ya en curso. Una imagen física (lo que se ve, se oye, se huele) con el humano adentro. Sin año, sin cifras, sin juicio. Termina volviendo atrás.
5. Cap 2: la vida antes. Quién era esta gente y qué hacía ahí. Es el único cap tranquilo; termina con la primera señal del peligro.
6. Caps 3 y 4: la escalada. Cada uno agrega un giro de la ficha y termina peor que el anterior.
7. Cap 5: el pico. El de la ficha, salvo razón mejor. Es el cap con más hechos, no el de menos: todo lo anterior lo prepara. Termina con la frase más corta del video.
8. Cap 6: el respiro y las consecuencias inmediatas: los que salen, los cuerpos, la búsqueda, las cifras oficiales (que van a pantalla).
9. Cap 7: las versiones en disputa, lo que la justicia dijo, y el humano otra vez. Termina con una cita del humano o la pregunta final de la ficha.
10. Lo que queda afuera se dice: nombres, hechos y escenas que no entraron, con una razón de una línea.
</oficio>

<ejemplo>
De un caso que no es el tuyo (una estación de radio y faro en una isla, mil novecientos sesenta y ocho). Copiá la forma, no el contenido: ninguno de estos nombres ni cifras está en tu ficha.

HUMANO: Elvira Soto, telegrafista de la estación: manda los telegramas pidiendo el barco, recibe las respuestas sin firma, sostiene la radio con las baterías del faro la noche del pico, y años después es la única que guardó el registro.
QUIÉN DECIDE: la Dirección de Faros y Balizas (institución): los telegramas de «mantener servicio» salen de ahí y nadie los firma.
PICO: cap 5, la noche en que el generador se apaga y muere el niño.

CAP 1 · QUÉ PASA: una mujer transmite en morse a la luz de una vela; la sala huele a querosén; afuera el faro sigue encendido; once personas esperan un barco. TERMINA: Tres semanas antes de la vela, llegó un telegrama. Y con él, una orden.
CAP 2 · QUÉ PASA: la estación en invierno: once personas, tres familias, el Alborada que viene cada quince días; Elvira recién llegada; el primer telegrama de la Dirección cuando el temporal cierra el paso: mantener servicio. TERMINA: El Alborada tenía que llegar el lunes. No llegó el lunes.
CAP 3 · QUÉ PASA: Elvira pide el barco; la respuesta es la misma; el combustible del generador se raciona; Bascuñán apaga la calefacción de las casas para que el faro siga. TERMINA: Cuando se apagó la última estufa, empezaron a mirar los muebles.
CAP 4 · QUÉ PASA: el niño enferma; el mecánico Ismael Rojo sale a revisar el generador bajo la tormenta y no vuelve; el séptimo telegrama; la misma respuesta. TERMINA: El séptimo telegrama tampoco tuvo firma.
CAP 5 · QUÉ PASA: el generador tose y se apaga; Elvira transmite con las baterías del faro; Bascuñán rompe la primera silla y la mete en la estufa; esa noche el niño deja de toser. TERMINA: Uno menos.
CAP 6 · QUÉ PASA: el Alborada entra a la bahía; el padre Quiroga cuenta a los que bajan; dos muertos para la comisión, tres para las familias; Teo Marín, marinero: «el capitán leyó el papel y dio la vuelta». TERMINA: El papel que leyó el capitán nunca apareció.
CAP 7 · QUÉ PASA: la comisión; el capitán: nunca zarpó por el temporal; los telegramas de Elvira: zarpó y recibió orden de volver; nadie de la Dirección firma nada; Elvira, años después, lee su libro en la radio. TERMINA: «Yo mandaba los telegramas. Nadie me dijo que los leyeran.»

AFUERA: la historia del farero anterior (buen arco, pero es otro invierno); la discusión técnica sobre el alcance del faro (va a pantalla si hace falta); el nombre del capitán del Alborada (la versión alcanza con «el capitán»); los nombres de las tres familias (entran solo el niño y su madre, sin nombre, en el cap 5).
</ejemplo>

<errores>
- Repartir todas las personas de la ficha entre los caps para «aprovechar el material». La ficha puede tener decenas de personas; el video tiene lugar para seis.
- Un cap 1 que explica lo que va a pasar («esto terminará en una comisión») en vez de mostrar el peor momento.
- Un cap 5 con un solo hecho. El pico es el cap más denso.
- Resumir al final de un cap. La frase de cierre abre el siguiente, no cierra este.
- Cambiar de humano porque otro candidato «también es interesante». Se elige uno.
- Inventar un culpable para que haya antagonista. Si la ficha no se lo atribuye a nadie, «ninguno».
</errores>"""
# F22 §1.1: la tarea del bloque USUARIO del mismo archivo, literal (con QUIÉN DECIDE y `antagonista`).
TAREA = """<tarea>
Con la ficha de arriba, escribí la columna vertebral de este caso: HUMANO, QUIÉN DECIDE, PICO, siete filas CAP n · QUÉ PASA / TERMINA, y AFUERA. Devolvé el JSON del esquema: {"humano": {"nombre", "por_que", "ids"}, "antagonista": {"tipo": "persona"|"institucion"|"ninguno", "nombre", "por_que", "ids"}, "pico": {"cap", "que", "ids"}, "caps": [{"cap", "que_pasa", "termina", "personas", "ids"}], "afuera": [{"que", "por_que"}]}. En `ids`, los ids de la ficha que sostienen cada fila; en `personas`, los nombres que entran en ese cap.
</tarea>"""

# F17 §1.1: el bloque SISTEMA de lab/hyperframes/f17/PROMPT_COLUMNA_v1.md, literal (test byte-idéntico contra el .md,
# extraído anclando en «## SISTEMA»: el párrafo de arriba del archivo también nombra un <rol>).
SYSTEM_F17_1 = """<rol>
Sos el guionista jefe de Misterios Sepultados, un canal de documentales de historia oscura en YouTube. Antes de armar la escaleta, decidís la columna vertebral de la historia: a quién seguimos, qué pasa en cada uno de los siete capítulos, dónde golpea y con qué termina. Trabajás solo con la ficha del caso. No inventás nombres, cifras, fechas ni citas.
</rol>

<que_es>
La columna es una página. Siete filas, una por capítulo, con dos cosas en cada una: qué pasa (los hechos y las personas que entran, en tres o cuatro frases) y con qué termina (la frase que deja la puerta abierta al siguiente). Arriba, el humano y el pico. Abajo, qué dejaste afuera y por qué. No es el guion ni la escaleta: es la decisión. Alguien que no sabe nada del caso tiene que leerla en un minuto y entender qué video va a ver.
</que_es>

<oficio>
1. Un humano. El que tenga arco (entra, sufre, sale) y más momentos concretos. Lo seguimos del cap 1 al 7.
2. Pocas personas con nombre: cinco o seis en todo el video, además del humano. Una persona entra solo si hace algo que se ve o dice algo que se oye. Cada nombre que agregás le quita memoria al espectador para los que importan.
3. Cap 1: el peor momento, ya en curso. Una imagen física (lo que se ve, se oye, se huele) con el humano adentro. Sin año, sin cifras, sin juicio. Termina volviendo atrás.
4. Cap 2: la vida antes. Quién era esta gente y qué hacía ahí. Es el único cap tranquilo; termina con la primera señal del peligro.
5. Caps 3 y 4: la escalada. Cada uno agrega un giro de la ficha y termina peor que el anterior.
6. Cap 5: el pico. El de la ficha, salvo razón mejor. Es el cap con más hechos, no el de menos: todo lo anterior lo prepara. Termina con la frase más corta del video.
7. Cap 6: el respiro y las consecuencias inmediatas: los que salen, los cuerpos, la búsqueda, las cifras oficiales (que van a pantalla).
8. Cap 7: las versiones en disputa, lo que la justicia dijo, y el humano otra vez. Termina con una cita del humano o la pregunta final de la ficha.
9. Lo que queda afuera se dice: nombres, hechos y escenas que no entraron, con una razón de una línea.
</oficio>

<ejemplo>
De otro caso (una cárcel durante un huracán). Copiá la forma, no el contenido.

HUMANO: Renard Reed, oficial del sheriff: entra de servicio la noche de la tormenta, ve irse a sus compañeros, ve los disparos desde el techo, y años después es el único que lo dice en voz alta.
PICO: cap 5, los francotiradores disparan a los presos que intentan salir del agua.

CAP 1 · QUÉ PASA: un hombre bebe agua del inodoro en una celda a oscuras; miles de presos encerrados en una cárcel inundada; Reed está de servicio adentro. TERMINA: Días antes de la sed, llegó la tormenta. Y con ella, una decisión.
CAP 2 · QUÉ PASA: 28 de agosto, evacuación obligatoria de la ciudad; la excepción son los presos; el sheriff rechaza la ayuda para evacuar («donde pertenecen»); Reed ve a los oficiales renunciar cuando se va la luz. TERMINA: Cuando la luz se fue, los guardias también empezaron a irse.
CAP 3 · QUÉ PASA: fallan los generadores; Templeman III sin luz ni aire; gritos entre pabellones; el agua empieza a entrar. TERMINA: En la oscuridad total, el agua empieza a subir.
CAP 4 · QUÉ PASA: agua negra hasta el pecho, basura y heces; dos cadáveres flotando en el pabellón médico; presos de pie durante días; empiezan a romper ventanas y a quemar sábanas para que los vean. TERMINA: La respuesta no fue un rescate.
CAP 5 · QUÉ PASA: Richard ve francotiradores en el techo del HOD disparando a los reclusos; Reed: «parecía que estaban abatiendo a la gente»; alguien grita «están tratando de escapar»; los presos entre el agua y los disparos. TERMINA: ¿Escapar o sobrevivir?
CAP 6 · QUÉ PASA: el paso elevado de Broad Street, monos naranjas al sol; jaulas detrás de la estación; sándwiches por encima de la cerca; los trasladan por todo el estado. TERMINA: Cuando se armó la lista de evacuados, faltaban cientos de nombres.
CAP 7 · QUÉ PASA: 517 ausentes de la lista; la portavoz: «nadie se ahogó, nadie se quedó atrás»; Reyes: «todavía hay presos muertos ahí dentro»; Reed. TERMINA: «Aunque estén en la cárcel, son seres humanos.»

AFUERA: Pearl Bland y su deuda de 398 dólares (buen arco, pero compite con Reed por el hilo); Iris Hardeman en Central Lock-Up (entra solo si el cap 6 queda corto); Nagin (el contexto de la evacuación alcanza sin su nombre); las cifras legales de las condenas (van a pantalla).
</ejemplo>

<errores>
- Repartir todas las personas de la ficha entre los caps para «aprovechar el material». La ficha tiene 90 personas; el video tiene lugar para seis.
- Un cap 1 que explica lo que va a pasar («esto terminará en un juicio») en vez de mostrar el peor momento.
- Un cap 5 con un solo hecho. El pico es el cap más denso.
- Resumir al final de un cap. La frase de cierre abre el siguiente, no cierra este.
- Cambiar de humano porque otro candidato «también es interesante». Se elige uno.
</errores>"""

# F17 §1.1: la tarea del bloque USUARIO del mismo archivo, literal.
TAREA_F17_1 = """<tarea>
Con la ficha de arriba, escribí la columna vertebral de este caso: HUMANO, PICO, siete filas CAP n · QUÉ PASA / TERMINA, y AFUERA. Devolvé el JSON del esquema: {"humano": {"nombre", "por_que", "ids"}, "pico": {"cap", "que", "ids"}, "caps": [{"cap", "que_pasa", "termina", "personas", "ids"}], "afuera": [{"que", "por_que"}]}. En `ids`, los ids de la ficha que sostienen cada fila; en `personas`, los nombres que entran en ese cap.
</tarea>"""

_S, _I = {"type": "STRING"}, {"type": "INTEGER"}
TIPOS_ANTAGONISTA = ("persona", "institucion", "ninguno")           # F22 §1.2: el contrato de punta a punta
_IDS = {"type": "ARRAY", "items": _S}
SCHEMA: dict[str, Any] = {
    "type": "OBJECT",
    "properties": {
        "humano": {"type": "OBJECT", "properties": {"nombre": _S, "por_que": _S, "ids": _IDS},
                   "required": ["nombre", "por_que", "ids"]},
        # F22 §1.2: QUIÉN DECIDE (persona de la ficha, institución de la ficha o ninguno)
        "antagonista": {"type": "OBJECT", "properties": {
            "tipo": {"type": "STRING", "enum": list(TIPOS_ANTAGONISTA)}, "nombre": _S, "por_que": _S, "ids": _IDS},
            "required": ["tipo", "nombre", "por_que", "ids"]},
        "pico": {"type": "OBJECT", "properties": {"cap": _I, "que": _S, "ids": _IDS}, "required": ["cap", "que", "ids"]},
        "caps": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "cap": _I, "que_pasa": _S, "termina": _S, "personas": {"type": "ARRAY", "items": _S}, "ids": _IDS},
            "required": ["cap", "que_pasa", "termina", "personas", "ids"]}},
        "afuera": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {"que": _S, "por_que": _S},
                                              "required": ["que", "por_que"]}},
    },
    "required": ["humano", "antagonista", "pico", "caps", "afuera"],
}


# ═══════════════════════════════════════════════════════════════
#  Prompt
# ═══════════════════════════════════════════════════════════════

def build_prompt(topic: dict, pool: dict, ficha: dict, feedback: list[str] | None = None,
                 notas: str | None = None) -> str:
    """<caso> · <ficha> (la misma sección que la escaleta v2: historia y escenas primero) · <tarea> literal. Con
    `feedback` (la única regeneración), lo que no pasó el chequeo va antes de la tarea. Con `notas` (F17 §2: los cambios
    que pida Omar, una sola vez), van dentro de la tarea, al final."""
    from script_engine.m01a_escaleta import ficha_section_v2
    fb = ""
    if feedback:
        fb = ("<rechazo>\nTu columna anterior no pasó estos controles. Corregilos sin cambiar lo demás:\n"
              + "\n".join(f"- {x}" for x in feedback) + "\n</rechazo>\n\n")
    tarea = TAREA
    if notas and notas.strip():
        tarea = TAREA.replace("\n</tarea>", f"\nNotas del editor sobre la columna anterior:\n{notas.strip()}\n</tarea>")
    return f"""<caso>
TÍTULO: {topic.get("video_title") or "(sin título)"}
ÁNGULO: {topic.get("angle") or "-"}
MISTERIO: {topic.get("mystery") or "-"}
REVELACIÓN: {topic.get("reveal") or "-"}
</caso>

<ficha>
{ficha_section_v2(ficha, pool)}
</ficha>

{fb}{tarea}"""


# ═══════════════════════════════════════════════════════════════
#  Lectura de ids y personas (formato de la salida, no chequeo)
# ═══════════════════════════════════════════════════════════════

_ID = re.compile(r"\b[PDTQ]\d{1,4}\b")


def _ids(xs: Any) -> list[str]:
    """Los ids de una lista que puede traer explicaciones («Q19: Liz…» → Q19), como `m01a_escaleta.ids_v2`."""
    out: list[str] = []
    for x in xs or []:
        found = _ID.findall(str(x or "").upper())
        out += found or [str(x).strip()]
    return list(dict.fromkeys(out))


def leer_ids(raw: dict) -> dict:
    col = copy.deepcopy(raw or {})
    for k in ("humano", "antagonista", "pico"):
        if isinstance(col.get(k), dict):
            col[k]["ids"] = _ids(col[k].get("ids"))
    for c in col.get("caps") or []:
        if isinstance(c, dict):
            c["ids"] = _ids(c.get("ids"))
    return col


def _tokens(s: str) -> list[str]:
    from script_engine import nombres
    return nombres.partes(s)                                            # F21: alias


def personas_ficha(ficha: dict) -> list[dict]:
    """Las personas de la ficha (personas, personas descartadas que la historia necesita, humanos candidatos), cada una
    con sus nombres (el nombre y sus variantes)."""
    out = []
    for sec in ("personas", "personas_descartadas"):
        for p in ficha.get(sec) or []:
            out.append({"nombre": p.get("nombre"), "nombres": [p.get("nombre"), *(p.get("variantes") or [])],
                        "ids": p.get("ids") or []})
    for p in (ficha.get("historia") or {}).get("humanos_candidatos") or []:
        out.append({"nombre": p.get("nombre"), "nombres": [p.get("nombre")], "ids": p.get("ids") or []})
    return out


def persona_de(nombre: str, ficha: dict) -> str | None:
    """El nombre en la ficha de la persona que nombra `nombre` (igual, o todas sus palabras dentro de un nombre de la
    ficha: «Tatiana Gabaglio» → «Tatiana Gabaglio»), o None."""
    t = _tokens(nombre)
    if not t:
        return None
    for p in personas_ficha(ficha):
        for n in p["nombres"]:
            tn = _tokens(n)
            if tn and (t == tn or set(t) <= set(tn)):
                return p["nombre"]
    return None


def institucion_de_la_ficha(nombre: str, ficha: dict) -> bool:
    """F19 §1.2 + F22 §1.2: una institución existe en la ficha si su nombre es el nombre o una de las variantes de una
    de las `personas` de la ficha, o si aparece literal en el texto de 2 o más hechos. El artículo de adelante no
    cuenta, en ninguno de los dos lados («el Ministerio…» está en «al Ministerio…»)."""
    from script_engine import nombres

    def _n(x: str) -> str:
        return re.sub(r"^(el|la|los|las|the) ", "", nombres.norm(x or ""))
    n = _n(nombre)
    if len(n) < 3:
        return False
    for p in ficha.get("personas") or []:
        if n in {_n(x) for x in [p.get("nombre"), *(p.get("variantes") or [])] if x}:
            return True
    return sum(1 for h in ficha.get("hechos") or [] if n in nombres.norm(h.get("texto") or "")) >= 2


def variantes_de(nombre: str, ficha: dict) -> list[str]:
    """F22 §1.2: las variantes de la ficha de la persona o institución `nombre` (las de su entrada en `personas`), para
    que la escaleta, la partición y el guion la busquen con todas sus formas. Lectura, no chequeo."""
    from script_engine import nombres

    def _n(x: str) -> str:
        return re.sub(r"^(el|la|los|las|the) ", "", nombres.norm(x or ""))
    n = _n(nombre)
    for p in ficha.get("personas") or []:
        vs = [x for x in [p.get("nombre"), *(p.get("variantes") or [])] if x]
        if n and n in {_n(x) for x in vs}:
            return [x for x in vs if _n(x) != n]
    return []


def antagonista_problemas(ag: dict | None, ficha: dict, *, persona_ok: Callable[[dict], bool] | None = None
                          ) -> list[str]:
    """F22 §1.2: el contrato del antagonista (columna y escaleta v2.1). persona → está en la ficha (`persona_ok`, por
    defecto `persona_de`); institucion → `institucion_de_la_ficha`; ninguno → `por_que` no vacío. Mensajes con la
    forma «antagonista … no es …» de siempre (es el bloqueante de la escaleta)."""
    ag = ag or {}
    tipo = str(ag.get("tipo") or "persona")
    if tipo == "ninguno":
        return [] if str(ag.get("por_que") or "").strip() else ["antagonista «ninguno» sin por_que: decí por qué la "
                                                                 "ficha no le atribuye la decisión a nadie"]
    if tipo == "institucion":
        return [] if institucion_de_la_ficha(str(ag.get("nombre") or ""), ficha) else [
            f"antagonista «{ag.get('nombre')}» no es una persona del pool ni una institución de la ficha"]
    ok = persona_ok(ag) if persona_ok else bool(persona_de(str(ag.get("nombre") or ""), ficha))
    return [] if ok else [f"antagonista «{ag.get('nombre') or ag.get('id')}» no es una persona del pool ni de la ficha"]


# ═══════════════════════════════════════════════════════════════
#  Chequeo (estructura e ids) y métrica
# ═══════════════════════════════════════════════════════════════

def chequeo(col: dict, pool: dict, ficha: dict) -> list[str]:
    """F17 §1.1: 7 caps (1–7, una fila cada uno), el humano es persona de la ficha, los ids existen, las personas de cada
    cap existen en la ficha. F22 §1.2: más el antagonista (`antagonista_problemas`). Nada más."""
    its = ev.items(pool)
    prob: list[str] = []
    caps = [c for c in col.get("caps") or [] if isinstance(c, dict)]
    nums = []
    for c in caps:
        try:
            nums.append(int(c.get("cap")))
        except (TypeError, ValueError):
            nums.append(c.get("cap"))
    if nums != list(range(1, CAPS + 1)):
        prob.append(f"la columna tiene que tener los caps 1 a {CAPS}, una fila cada uno, en orden (vinieron {nums})")
    hum = col.get("humano") or {}
    if not persona_de(hum.get("nombre") or "", ficha):
        prob.append(f"humano «{hum.get('nombre')}» no es una persona de la ficha")
    prob += antagonista_problemas(col.get("antagonista"), ficha)
    filas = [("humano", hum), ("antagonista", col.get("antagonista") or {}), ("pico", col.get("pico") or {})] + \
        [(f"cap {c.get('cap')}", c) for c in caps]
    for donde, x in filas:
        for i in x.get("ids") or []:
            if i not in its:
                prob.append(f"{donde}: el id «{i}» no existe en la ficha")
    for c in caps:
        for n in c.get("personas") or []:
            if not persona_de(n, ficha):
                prob.append(f"cap {c.get('cap')}: «{n}» no es una persona de la ficha")
    return prob


def personas_con_nombre(col: dict, ficha: dict) -> list[str]:
    """Métrica (informativa): las personas distintas con nombre en toda la columna (humano + personas de cada cap)."""
    nombres = [(col.get("humano") or {}).get("nombre") or ""]
    nombres += [n for c in col.get("caps") or [] for n in (c.get("personas") or [])]
    out: list[str] = []
    for n in nombres:
        p = persona_de(n, ficha) or n.strip()
        if p and p not in out:
            out.append(p)
    return out


# ═══════════════════════════════════════════════════════════════
#  Generación
# ═══════════════════════════════════════════════════════════════

def generate_columna(topic: dict, pool: dict, ficha: dict, *, call: Callable[..., dict] | None = None,
                     log: list[str] | None = None, persist: bool = True, notas: str | None = None) -> dict:
    """UNA llamada (Sol high por `guion_v4.call_for`) → chequeo → si falla, UNA regeneración con lo que falló →
    si vuelve a fallar, ColumnaError (PARADA)."""
    log = log if log is not None else []
    topic_id = topic.get("id") or topic.get("topic_id")
    if call is None:
        from script_engine.guion_v4 import call_for
        call = call_for(None)
    feedback: list[str] = []
    intentos = []
    raw: dict = {}
    for k in range(1, REGENERACIONES + 2):
        raw = call(build_prompt(topic, pool, ficha, feedback, notas), system_instruction=SYSTEM,
                   response_schema=SCHEMA, description=f"m01a_columna intento {k}")
        col = leer_ids(raw)
        prob = chequeo(col, pool, ficha)
        intentos.append({"intento": k, "problemas": prob})
        log.append(f"  [columna] intento {k}: {len(prob)} problema(s) {prob[:4]}")
        if not prob:
            col.update({"topic_id": topic_id, "prompt_version": PROMPT_VERSION, "_intentos": intentos,
                        "notas": notas or None,
                        "ficha": {"prompt_version": ficha.get("prompt_version"), "pool_md5": ficha.get("pool_md5")}})
            pers = personas_con_nombre(col, ficha)
            col["_metricas"] = {"personas_con_nombre": len(pers), "personas": pers}
            if persist:
                save(topic_id, col)
            return col
        feedback = prob
    fail = {"topic_id": topic_id, "prompt_version": PROMPT_VERSION, "_intentos": intentos, "ultima": raw}
    if persist:
        (STEPS_DIR / topic_id).mkdir(parents=True, exist_ok=True)
        (STEPS_DIR / topic_id / "01a_columna_rechazada.json").write_text(json.dumps(fail, ensure_ascii=False, indent=2),
                                                                         encoding="utf-8")
    raise ColumnaError(f"columna rechazada después de {len(intentos)} intento(s) (PARADA): {intentos[-1]['problemas']}")


def save(topic_id: str, col: dict, steps_dir: Path | None = None) -> Path:
    p = Path(steps_dir or STEPS_DIR) / topic_id / "01a_columna.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(col, ensure_ascii=False, indent=2), encoding="utf-8")
    return p


def load(topic_id: str, steps_dir: Path | None = None) -> dict | None:
    p = Path(steps_dir or STEPS_DIR) / topic_id / "01a_columna.json"
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


# ═══════════════════════════════════════════════════════════════
#  Texto: para la escaleta y la página legible
# ═══════════════════════════════════════════════════════════════

def section(col: dict) -> str:
    """La columna para el usuario de la escaleta (con la forma del ejemplo del prompt, más personas e ids)."""
    def ids(x: dict) -> str:
        return " [" + ", ".join(x.get("ids") or []) + "]" if x.get("ids") else ""
    h, pk = col.get("humano") or {}, col.get("pico") or {}
    L = [f"HUMANO: {h.get('nombre')}: {h.get('por_que')}{ids(h)}"]
    if col.get("antagonista"):                                    # F22 §1.2: la forma del ejemplo del prompt
        L.append(f"QUIÉN DECIDE: {quien_decide(col)}{ids(col['antagonista'])}")
    L += [f"PICO: cap {pk.get('cap')}, {pk.get('que')}{ids(pk)}", ""]
    for c in col.get("caps") or []:
        L.append(f"CAP {c.get('cap')} · QUÉ PASA: {c.get('que_pasa')} PERSONAS: "
                 f"{', '.join(c.get('personas') or []) or '—'}. TERMINA: {c.get('termina')}{ids(c)}")
    L += ["", "AFUERA: " + "; ".join(f"{a.get('que')} ({a.get('por_que')})" for a in col.get("afuera") or [])]
    return "\n".join(L)


def quien_decide(col: dict) -> str:
    """F22: la línea QUIÉN DECIDE como en el ejemplo del prompt: «nombre (institución): por qué»; «ninguno: por qué»."""
    a = col.get("antagonista") or {}
    tipo = str(a.get("tipo") or "persona")
    if tipo == "ninguno":
        return f"ninguno: {a.get('por_que')}"
    return f"{a.get('nombre')}{' (institución)' if tipo == 'institucion' else ''}: {a.get('por_que')}"


def to_markdown(col: dict, titulo: str = "") -> str:
    """La página que lee Omar: la forma del ejemplo del prompt; abajo, personas e ids por cap."""
    h, pk = col.get("humano") or {}, col.get("pico") or {}
    m = col.get("_metricas") or {}
    L = [f"# Columna vertebral{' — ' + titulo if titulo else ''}", "",
         f"_{col.get('prompt_version')} · gpt-6.1-sol high · personas con nombre en toda la columna: "
         f"{m.get('personas_con_nombre')}_", "",
         f"**HUMANO:** {h.get('nombre')}: {h.get('por_que')}", ""]
    if col.get("antagonista"):                                    # F22 §1.1: entre HUMANO y PICO
        L += [f"**QUIÉN DECIDE:** {quien_decide(col)}", ""]
    L += [f"**PICO:** cap {pk.get('cap')}, {pk.get('que')}", ""]
    for c in col.get("caps") or []:
        L += [f"**CAP {c.get('cap')} · QUÉ PASA:** {c.get('que_pasa')} **TERMINA:** {c.get('termina')}", ""]
    L.append("**AFUERA:** " + "; ".join(f"{a.get('que')} ({a.get('por_que')})" for a in col.get("afuera") or []))
    L += ["", "---", "", "| cap | personas | ids |", "|---|---|---|",
          f"| humano | {h.get('nombre')} | {', '.join(h.get('ids') or [])} |",
          f"| quién decide | {(col.get('antagonista') or {}).get('nombre') or '—'} | "
          f"{', '.join((col.get('antagonista') or {}).get('ids') or [])} |",
          f"| pico | — | {', '.join(pk.get('ids') or [])} |"]
    L += [f"| {c.get('cap')} | {', '.join(c.get('personas') or []) or '—'} | {', '.join(c.get('ids') or [])} |"
          for c in col.get("caps") or []]
    L += ["", f"Personas con nombre ({m.get('personas_con_nombre')}): {', '.join(m.get('personas') or [])}", ""]
    return "\n".join(L)
