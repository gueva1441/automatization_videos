"""
script_engine/m01a_escaleta.py — Módulo 01a v3 (F6b, HANDOFF_F6 §2.2): el LLM DECIDE LA HISTORIA antes de escribirla.

Reemplaza el reparto de `m01a_skeleton` (bullets de hechos por cap) por una ESCALETA: 7–12 beats con función,
emoción, intensidad, un dato central, una imagen sensorial, la pregunta que abre, la pregunta de pantalla y el
cierre; un humano con nombre que seguimos todo el video, el antagonista, la promesa del gancho, el pico y el cierre
humano. Una llamada a Gemini Pro (`call_pro_json`) con el pool completo; hasta MAX_ATTEMPTS con las correcciones del
validador. La salida sigue siendo 7 caps (`EXPECTED_CHAPTER_COUNT`): cada beat va a un cap.

    generate_escaleta(topic)   → escaleta (persistida en _steps/<id>/01a_escaleta.json)
    frozen_escaleta(topic)     token `escaleta_frozen` (o `skeleton_frozen` apuntando a una escaleta): usa una ya
                               hecha, traduce sus ids al pool actual por texto, como frozen_skeleton
    is_v3(topic)               GUION_V3=1 o topic["guion_version"] == 3, y el topic tiene evidence_pool
    to_markdown(esc, pool)     la escaleta legible (para Omar)

Validador (determinista). Repara (y lo anota en `_reparaciones`) solo lo mecánico:
    palabras    las `palabras_objetivo` de cada cap se escalan para sumar su largo (hook/outro 110, desarrollo 190)
                si se van más de ±15 %
    apoyo       un id de `datos_apoyo` que no existe o que ya usa otro beat sale del apoyo
    pico.id     si no es el dato central de su beat, pasa a serlo
Rechaza (y reintenta con feedback): menos de 7 o más de 12 beats; un cap sin beats o caps fuera de orden; el beat 1
no es el gancho del cap 1; un dato central que no existe o que repite; intensidad que baja antes del pico; el pico en
el último beat o sin respiro (intensidad 1) después; humano que no es del pool (o colectivo sin fuente); humano en
escena en menos de 3 caps; cifras en la promesa o en la imagen del gancho; imagen sensorial vacía o sin nada para ver,
oír, oler o tocar. La pregunta de pantalla (última de cada cap) pasa la rúbrica §4; si en el último intento no pasa,
queda marcada `pregunta_valida: false` (gfx_question es el respaldo) y no rechaza la escaleta.
Después: `finalize_pool_plan` de m01a_skeleton (cifras canónicas + reservados para pantalla) sobre los caps.

F6b-3 (validación del analista sobre f6b-2):
    flash-forward  el beat 1 puede ser un flash-forward (`flash_forward: true`): un momento posterior y más intenso
                   contado primero. La curva «no baja hasta el pico» se mide desde el beat 2 y no es regresión temporal.
    cierre         la última frase del video (`cierre` del último beat) nombra al humano o a otro testigo verificado.
    a_pantalla     ids que la escaleta manda a PANTALLA y no a la voz (la cita de alguien que no estuvo ahí): no
                   están en ningún beat; entran primero en los `pantalla_ids` de su cap.
    reservados     los reservados automáticos van al cap cuyos beats cubren su FECHA (no por palabras en común).
    verificación   si el pool trae `verificacion` (researcher_steps/verify_quotes): una cita sin verificar se usa SIN
                   el nombre de quien la dijo; `humano_en_escena` solo con un dato VERIFICADO suyo.
    un conteo      517 y «más de 500» son un hecho (gfx_pool.count_groups): la aproximada no va en ningún beat.
    guionista      `instrucciones_guionista`: reglas deterministas para m01b (cifra única, quién no se nombra).
    notas          topic["escaleta_notas"]: indicaciones del editor para ESE tema (van al prompt tal cual).

F6b-4 (validación del analista sobre f6b-3):
    contador       `contador: true` en el beat cuya cifra sale como CONTADOR en pantalla
    una cifra      una cifra se ve en pantalla UNA vez por video (preguntas de pantalla + contadores)
    cap 7          la pregunta de pantalla del cap 7 es obligatoria (sin respaldo de gfx_question)
    sin eco        la última frase no repite textual una cita del pool (≥ 5 palabras seguidas)
    solo apoyo     topic["escaleta_solo_apoyo"]: ids que el editor permite solo como apoyo (nunca dato central)
    pantalla       una cita sin verificar no va a pantalla (ni `a_pantalla` ni reservado automático)
"""
from __future__ import annotations

import copy
import json
import os
import re
from pathlib import Path
from typing import Any, Callable

from script_engine import evidence as ev
from script_engine.m01a_skeleton import CHAPTER_SCHEMA, DEFAULT_INTENT_BY_CAP, STEPS_DIR, finalize_pool_plan

PROMPT_VERSION = "f6b-4"            # f6b-4: contador, una cifra en pantalla una vez, pregunta del cap 7, cierre sin eco
MAX_ATTEMPTS = 3
def _vl(name: str) -> int:
    from script_engine.video_length import get
    return get(name)


MIN_BEATS, MAX_BEATS = _vl("min_beats"), _vl("max_beats")     # F8 §2: tope en video_length (12)
MIN_BEATS_DEV_CAP = _vl("min_beats_dev_cap")                     # F8 §2: ≥ 2 beats en cada cap 2–6


def _cap_words() -> dict[int, int]:
    """Palabras por cap desde config (HANDOFF_F7 §8.2: gancho 110, desarrollo 240 × 5, cierre 130)."""
    from script_engine.video_length import get
    return {1: get("hook_words"), **{n: get("dev_words") for n in range(2, 7)}, 7: get("outro_words")}


CAP_WORDS = _cap_words()          # antes {1: 110, 2–6: 190, 7: 110} (desarrollo 75 s)
WORDS_TOL = 0.15
INTENSITY = (1, 5)
MIN_HUMAN_CAPS = 3
Q_MAX_WORDS = 8
FUNCIONES = ("gancho", "planteo", "escalada", "giro", "pico", "respiro", "consecuencia", "revelacion", "cierre")
ADMIN_TERMS = ("indemnizacion", "indemnizaciones", "generador", "generadores", "registro", "registros", "demanda",
               "demandas", "informe", "informes", "autoridades", "compensacion", "expediente", "tribunal", "juicio",
               "fallo", "jurado", "protocolo", "evacuacion")
Q_OPENERS = ("quien", "quienes", "por que", "donde", "adonde", "a donde", "cuant", "que ", "como", "a quien",
             "a quienes", "de quien", "para que", "cuando", "hasta cuando", "hasta donde", "cual", "cuales", "en que")
# imagen ABSTRACTA = todas sus palabras de contenido son ideas, no cosas (la desesperación, la injusticia del sistema)
ABSTRACT = {"desesperacion", "injusticia", "sistema", "horror", "miedo", "dolor", "abandono", "tragedia", "verdad",
            "olvido", "angustia", "impotencia", "esperanza", "justicia", "culpa", "silencio", "caos", "terror",
            "tension", "incertidumbre", "indiferencia", "crueldad", "corrupcion", "negligencia", "poder", "muerte",
            "vida", "destino", "historia", "memoria", "sociedad", "humanidad", "realidad", "situacion", "momento",
            "decision", "responsabilidad", "sufrimiento", "violencia", "soledad", "rabia", "tristeza", "total",
            "absoluta", "absoluto", "profunda", "profundo", "enorme", "terrible", "cruda", "crudo", "pura", "puro"}


# una cifra escrita en letras («seis mil», «quinientos») también es una cifra; «miles», «cientos», «docenas» no
NUM_WORDS = re.compile(r"\b(dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|once|doce|trece|catorce|quince|veinte|"
                       r"treinta|cuarenta|cincuenta|sesenta|setenta|ochenta|noventa|cien|ciento|doscient\w*|"
                       r"trescient\w*|cuatrocient\w*|quinient\w*|seiscient\w*|setecient\w*|ochocient\w*|"
                       r"novecient\w*|mil|millon|millones)\b")


def has_figure(text: str) -> bool:
    return bool(re.search(r"\d", text or "") or NUM_WORDS.search(ev.norm(text or "")))


class EscaletaValidationError(ValueError):
    """La escaleta que devolvió Pro no cumple el contrato (después de los reintentos)."""


# ═══════════════════════════════════════════════════════════════
#  Schema (Gemini)
# ═══════════════════════════════════════════════════════════════

_S, _I, _B = {"type": "STRING"}, {"type": "INTEGER"}, {"type": "BOOLEAN"}
SCHEMA: dict[str, Any] = {
    "type": "OBJECT",
    "properties": {
        "humano": {"type": "OBJECT", "properties": {
            "id": _S, "nombre": _S, "rol": _S, "por_que": _S, "colectivo": _B, "fuente": _S},
            "required": ["id", "nombre", "rol", "por_que", "colectivo"]},
        "antagonista": {"type": "OBJECT", "properties": {"id": _S, "por_que": _S}, "required": ["id"]},
        "promesa_gancho": _S,
        "pico": {"type": "OBJECT", "properties": {"beat": _I, "id": _S, "por_que": _S}, "required": ["beat", "id", "por_que"]},
        "cierre_humano": _S,
        "beats": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "n": _I, "cap": _I, "funcion": {"type": "STRING", "enum": list(FUNCIONES)}, "emocion": _S,
            "intensidad": _I, "dato_central": _S, "datos_apoyo": {"type": "ARRAY", "items": _S},
            "humano_en_escena": _B, "imagen_sensorial": _S, "pregunta_abierta": _S, "pregunta_pantalla": _S,
            "cierre": _S, "palabras_objetivo": _I, "flash_forward": _B, "contador": _B},
            "required": ["n", "cap", "funcion", "emocion", "intensidad", "dato_central", "datos_apoyo",
                         "humano_en_escena", "imagen_sensorial", "pregunta_abierta", "pregunta_pantalla", "cierre",
                         "palabras_objetivo"]}},
        "a_pantalla": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {"id": _S, "cap": _I, "por_que": _S},
                                                  "required": ["id", "cap"]}},
    },
    "required": ["humano", "antagonista", "promesa_gancho", "pico", "cierre_humano", "beats", "a_pantalla"],
}


# ═══════════════════════════════════════════════════════════════
#  Prompt
# ═══════════════════════════════════════════════════════════════

SYSTEM = ("Sos el guionista jefe de un canal de documentales de misterio en YouTube. Antes de que nadie escriba una "
          "línea, decidís la HISTORIA: a quién seguimos, qué sabe el espectador en cada momento, dónde golpea y por qué "
          "se queda al segundo siguiente. Trabajás SOLO con la investigación que te dan: no inventás nombres, cifras, "
          "fechas ni citas. Respondés SOLO JSON.")

FEWSHOT = """EJEMPLO 1 (OTRO TEMA, solo para la FORMA — no uses nada de su contenido):
Tema: la mina de Sago, 2006. Humano: Randal McCloy, el único minero que salió vivo. Antagonista: la empresa.
promesa_gancho: "Esa noche le dijeron a doce familias que sus hombres estaban vivos. Esta es la historia de las tres horas que siguieron."
beats:
 1 cap1 gancho · miedo 3 · imagen: "un casco con la lámpara todavía encendida, tirado en el barro negro del túnel" · pregunta: "¿qué pasó allá abajo?" · cierre: anticipa la explosión de las 6:26
 2 cap2 planteo · inquietud 2 · imagen: "trece hombres bajando en el carro, termos de café entre las rodillas" · humano en escena
 3 cap3 escalada · angustia 3 · imagen: "golpes con un martillo contra el techo de roca, cada quince minutos"
 4 cap4 escalada · esperanza falsa 4 · imagen: "la iglesia llena, las campanas sonando a medianoche" · pregunta pantalla: "¿Quién dijo que estaban vivos?"
 5 cap5 pico · horror 5 · imagen: "la misma iglesia, tres horas después, alguien grita desde el fondo" · pregunta pantalla: "¿Por qué nadie corrigió la noticia?"
 6 cap5 respiro · duelo 1 · imagen: "una nota escrita a lápiz en el reverso de un seguro de vida"
 7 cap6 consecuencia · rabia 3 · imagen: "un sobre de multas de la mina, sin abrir, sobre un escritorio" · humano en escena
 8 cap7 cierre · tristeza 2 · imagen: "McCloy aprendiendo a caminar otra vez en un pasillo de hospital" · humano en escena · pregunta pantalla: "¿Cuántas minas siguen así?"

EJEMPLO 2 (OTRO TEMA, solo para la FORMA):
Tema: el incendio de la fábrica Triangle, Nueva York, 1911. Humano: una obrera de 16 años que sobrevivió.
promesa_gancho: "Las puertas del noveno piso estaban cerradas con llave. Alguien tenía esa llave."
beats:
 1 cap1 gancho · terror 3 · imagen: "humo saliendo por las ventanas del noveno piso y gente mirando desde la vereda" · cierre: anticipa la puerta cerrada
 2 cap2 planteo · rutina 2 · imagen: "doscientas máquinas de coser, pelusa de algodón flotando en la luz de la tarde" · humano en escena
 3 cap3 escalada · pánico 4 · imagen: "una manija de bronce que no gira" · humano en escena · pregunta pantalla: "¿Quién cerró esa puerta?"
 4 cap4 pico · horror 5 · imagen: "la escalera de los bomberos llega hasta el sexto piso; ellas están en el noveno"
 5 cap5 respiro · silencio 1 · imagen: "zapatos de mujer alineados en el muelle, esperando que alguien los reconozca"
 6 cap6 consecuencia · indignación 3 · imagen: "los dueños saliendo del tribunal entre fotógrafos" · pregunta pantalla: "¿Por qué los dueños salieron libres?"
 7 cap7 cierre · memoria 2 · imagen: "una anciana mirando la misma ventana, setenta años después" · humano en escena · pregunta pantalla: "¿Cuántas puertas siguen cerradas?"
"""

def rules_text(cap_words: dict[int, int], min_beats: int, max_beats: int, min_dev: int = 1) -> str:
    """Las reglas con el perfil de largo (F7d: el amarillo de la compuerta acorta el video)."""
    dev = (f" Los caps de desarrollo (2–6) tienen al menos {min_dev} beats cada uno." if min_dev > 1 else "")
    return f"""REGLAS DE LA ESCALETA (duras: si no se cumplen, se rechaza):
1. Entre {min_beats} y {max_beats} beats, numerados 1..N en orden, cada uno con su `cap` (1–7, no decreciente). Los 7
   caps tienen al menos un beat.{dev} El beat 1 es la `funcion` "gancho" del cap 1.
2. `palabras_objetivo`: los beats de un cap suman su largo: cap 1 ≈ {cap_words[1]}, caps 2–6 ≈ {cap_words[2]} cada uno,
   cap 7 ≈ {cap_words[7]}.
3. `intensidad` de {INTENSITY[0]} a {INTENSITY[1]}: NO BAJA hasta el pico (cada cap peor que el anterior). El pico no es
   el último beat, y después del pico hay al menos un beat de intensidad 1 (respiro: el espectador respira antes del
   cierre). FLASH-FORWARD: el beat 1 puede contar primero un momento POSTERIOR y más intenso (`flash_forward: true`);
   el cap 2 vuelve atrás («cómo se llegó ahí») y la curva se mide desde el beat 2. Solo el beat 1 puede serlo.
4. Cada beat tiene UN `dato_central` (un id D##, T## o Q## del pool) y 0–3 `datos_apoyo`. Un id aparece en UN solo beat
   en todo el video (después se puede parafrasear sin la cifra). `pico.id` = el dato central del beat del pico.
5. `humano`: UNA persona del pool que estuvo ahí (preferí un TESTIGO, con testimonio: es a quien seguimos). Va con su
   `id` P## y su `nombre` EXACTO del pool. Si el pool no tiene testigos con nombre: un personaje colectivo con rostro
   («un preso de Templeman III, 19 años, según la ACLU») con `colectivo: true`, `nombre` = esa descripción, `id` = el
   Q## o D## que lo documenta y `fuente` = el mismo id. NUNCA un nombre inventado.
   `humano_en_escena: true` SOLO en los beats que tienen un dato SUYO VERIFICADO (su cita, o un dato que lo nombra) como
   dato central o de apoyo: el guionista no puede ponerlo en una escena que el research no documenta. Tiene que
   estar así en al menos {MIN_HUMAN_CAPS} caps distintos (el primero, antes del cap 3); si el pool tiene menos datos
   suyos, en tantos caps como datos tenga. En los demás beats se lo puede nombrar, no poner en escena.
6. `antagonista`: el P## del pool al que el research le atribuye la decisión que causó el daño.
7. `imagen_sensorial`: algo que se VE, se OYE, se HUELE o se TOCA en ese momento («agua negra subiendo por la escalera
   de la celda»); nunca una idea abstracta («la desesperación»). Sale del pool: no inventes objetos que contradigan el
   research. Es el ancla de la imagen del cap.
8. Gancho: `promesa_gancho` = UNA frase con lo que el espectador va a descubrir; sin cifras ni años (tampoco en
   letras: «seis mil» es una cifra; «miles» no). La
   `imagen_sensorial` del beat 1 tampoco lleva cifras. La narración va a abrir con esa imagen y esa promesa.
9. `pregunta_pantalla` en el ÚLTIMO beat de cada cap (en los otros, ""): ≤ {Q_MAX_WORDS} palabras, empieza con «¿» y
   termina con «?»; nombra algo que el espectador YA conoce (persona, grupo, lugar u objeto de este cap o de antes);
   implica culpa, consecuencia o un destino no resuelto; sin nombres propios nuevos y sin términos administrativos
   (indemnización, generadores, registros, demanda, informe, autoridades, evacuación). Modelos: «¿Quién apagó las
   luces?», «¿Por qué nadie abrió las celdas?», «¿Dónde están los 517?». Cap 7: no es gancho; es la pregunta humana
   que se queda («¿Cuántos siguen sin nombre?»).
10. `cierre` de cada beat que termina un cap 1–6: anticipa algo CONCRETO del cap siguiente (su dato central o su
    imagen). `pregunta_abierta`: lo que el espectador se pregunta al terminar el beat.
11. Las cifras de conteo van con su id OFICIAL (ver CIFRAS CANÓNICAS); la variante de medios solo en el beat que cuenta
    la contradicción. Un conteo con dos cifras (ver UN HECHO, UNA CIFRA) se cuenta UNA vez, con la precisa: los ids de la
    aproximada no van en ningún beat.
12. CIERRE: el último beat (cap 7) tiene como dato central una CONSECUENCIA (lo que falta, lo que se negó, lo que nunca
    se contó), no una victoria ajena. Su `cierre` es la última frase del video y nombra al humano o a otro testigo
    VERIFICADO. Nunca termina en la cita de alguien que no estuvo ahí: esa va a `a_pantalla`.
13. `a_pantalla`: [{{"id", "cap", "por_que"}}] — ids que preferís que se VEAN y no se digan (la cita de un abogado, una
    fuente, un dato que la imagen cuenta mejor). Un id de `a_pantalla` no está en ningún beat. Máximo 2 por cap.
14. CITAS SIN VERIFICAR (marcadas en el pool): se pueden usar, pero la narración no dice el nombre de quien la dijo
    («un preso», «una guardia»). Solo las VERIFICADAS se dicen con nombre.
15. `contador: true` en el beat cuya cifra conviene ver subir en pantalla (una cantidad: personas, días). UNA CIFRA SE
    VE EN PANTALLA UNA SOLA VEZ en todo el video: si un beat lleva contador, ninguna pregunta de pantalla repite esa
    cifra; y dos preguntas de pantalla no repiten la misma cifra.
16. La pregunta de pantalla del cap 7 es OBLIGATORIA: humana, la que se queda («¿Cuántos siguen sin nombre?»).
17. El `cierre` del último beat describe la última frase del video sin copiar ninguna cita: esa frase va a ser una cita
    (del humano o de un testigo verificado, por su id) o una pregunta; nunca un resumen (F8 §2).

LO QUE RETIENE (cada decisión responde a por qué alguien se iría):
- Los primeros 30 s: una imagen concreta y una promesa, no contexto.
- Un humano con nombre al que seguimos todo el video.
- Curva: cada cap peor que el anterior. Ritmo: respiros.
- Cierres que obligan: culpa o consecuencia, nunca trivia administrativa.
- Final humano: lo que produce el like y el comentario."""


RULES = rules_text(CAP_WORDS, MIN_BEATS, MAX_BEATS, MIN_BEATS_DEV_CAP)


def own_ids(pool: dict, persona: dict) -> list[str]:
    """Datos que valen para poner a la persona EN ESCENA: los que la nombran (o son su cita); con verificación en el
    pool, sus citas cuentan solo si están verificadas."""
    its = ev.items(pool)
    sur = ev.norm(persona["nombre"]).split()[-1]
    vp = any(q.get("verificacion") for q in pool.get("citas") or [])
    out = []
    for i, it in its.items():
        if it["_kind"] not in ("datos", "cronologia", "citas"):
            continue
        if sur not in ev.norm(ev.text_of(it) + " " + str(it.get("autor") or "")):
            continue
        if vp and it["_kind"] == "citas" and (it.get("verificacion") or {}).get("estado") != "verificada":
            continue
        out.append(i)
    return out


def _fmt_people(pool: dict) -> str:
    out = []
    for p in pool.get("personajes") or []:
        tags = [t for t, on in (("TESTIGO", p.get("testigo")), ("VERIFICADO", p.get("testigo_verificado")),
                                ("ANTAGONISTA", p.get("antagonista"))) if on]
        pres = f" · estuvo en {', '.join(p['presente_en'])}" if p.get("presente_en") else ""
        own = own_ids(pool, p) if p.get("testigo") else []
        out.append(f"  [{p['id']}] PERSONA: {p['nombre']} — {p.get('rol') or ''}"
                   + (f" · {' · '.join(tags)}" if tags else "") + pres
                   + (f" · datos que lo ponen en escena: {', '.join(own)} (repartilos en caps distintos)" if own else ""))
    return "\n".join(out) or "  (ninguna)"


def _verif(q: dict) -> str:
    v = q.get("verificacion")
    if not v:
        return ""
    return " · VERIFICADA" if v.get("estado") == "verificada" else " · SIN VERIFICAR (se usa sin el nombre)"


def _fmt_quotes(pool: dict) -> str:
    out = []
    for q in pool.get("citas") or []:
        tag = (" · TESTIMONIO (estuvo ahí)" if q.get("testimonio") else "") + _verif(q)
        rol = f" ({q['rol']})" if q.get("rol") else ""
        src = f" · fuente: {q['fuente']}" if q.get("fuente") else ""
        out.append(f'  [{q["id"]}] CITA: "{q["texto"]}" — {q.get("autor")}{rol}{tag}{src}')
    return "\n".join(out) or "  (ninguna)"


def _fmt_canonical(pool: dict) -> str:
    out = []
    for g in pool.get("cifras_canonicas") or []:
        var = ", ".join(f"{v['id']} ({v['valor']}, {v['estatus']})" for v in g["variantes"])
        out.append(f"  {g['valor']}: la OFICIAL es [{g['oficial']}]; variantes {var}. Usá la oficial; la de medios solo "
                   "en el beat de la contradicción, junto a la oficial.")
    return "\n".join(out) or "  (ninguna)"


def count_variants(pool: dict) -> list[dict]:
    """Un conteo con varias cifras (gfx_pool.count_groups: 517 y «más de 500»): {"canon": id, "num", "variantes": [ids
    cuyo texto trae otra cifra del mismo conteo]}."""
    from script_engine.gfx_pool import count_groups
    out = []
    for g in count_groups(pool):
        c = g["canon"]
        others = {x for x in g["nums"] if re.sub(r"[,.]", "", x) != re.sub(r"[,.]", "", c["num"])}
        var = [d["id"] for d in pool.get("datos") or [] if d["id"] != c["id"]
               and any(re.search(rf"(?<![\d,.]){re.escape(x)}(?![\d,.])", d["texto"]) for x in others)]
        out.append({"canon": c["id"], "num": c["num"], "unit": c["unit"], "variantes": var,
                    "otras": sorted(others, key=lambda x: -len(x))})
    return out


def _fmt_counts(pool: dict) -> str:
    return "\n".join(f"  {g['num']} {g['unit']} = [{g['canon']}]. Las otras cifras del MISMO conteo "
                     f"({', '.join(g['otras'])}: ids {', '.join(g['variantes']) or '—'}) no van en ningún beat."
                     for g in count_variants(pool)) or "  (ninguno)"


def pool_section(pool: dict) -> str:
    # F7c: un pool de research v3 (cientos de datos) trae `digest`, su resumen con ids reales; la escaleta lo lee en vez
    # del pool entero (≈ 63 k → ≤ 20 k tokens). ESCALETA_DIGEST=0 lo apaga. Sin digest, todo igual que antes.
    if (pool.get("digest") or {}).get("texto") and os.environ.get("ESCALETA_DIGEST", "1") != "0":
        return pool["digest"]["texto"]
    ids = [i for i, it in ev.items(pool).items() if it["_kind"] in ("datos", "cronologia", "lugares")]
    return (f"DATOS, CRONOLOGÍA Y LUGARES:\n{ev.format_pool(pool, ids)}\n\nCITAS:\n{_fmt_quotes(pool)}\n\n"
            f"PERSONAS:\n{_fmt_people(pool)}\n\nCIFRAS CANÓNICAS:\n{_fmt_canonical(pool)}\n\n"
            f"UN HECHO, UNA CIFRA:\n{_fmt_counts(pool)}")


def _profile(topic: dict) -> tuple[dict[int, int], int, int, int]:
    """(palabras por cap, mínimo y máximo de beats, mínimo de beats por cap de desarrollo): los de siempre, o los del
    amarillo de la compuerta del pool (`topic["_largo"]`, F7d)."""
    lg = topic.get("_largo") or {}
    return (lg.get("cap_words") or CAP_WORDS, MIN_BEATS, lg.get("max_beats") or MAX_BEATS,
            lg.get("min_beats_dev_cap") or MIN_BEATS_DEV_CAP)


def build_prompt(topic: dict, pool: dict, feedback: list[str] | None = None) -> str:
    fb = ""
    if feedback:
        fb = ("\n═══ TU ESCALETA ANTERIOR SE RECHAZÓ. CORREGÍ ESTO (sin romper lo demás) ═══\n"
              + "\n".join(f"- {x}" for x in feedback) + "\n")
    notes = str(topic.get("escaleta_notas") or "").strip()
    if topic.get("escaleta_solo_apoyo"):
        notes += ("\n" if notes else "") + ("Estos ids van SOLO como datos de apoyo, nunca como dato central: "
                                             + ", ".join(topic["escaleta_solo_apoyo"]) + ".")
    if notes:
        fb = ("\n═══ INDICACIONES DEL EDITOR PARA ESTE TEMA (mandan sobre tu criterio, nunca sobre las reglas) ═══\n"
              + notes + "\n") + fb
    return f"""TEMA DEL VIDEO: {topic.get("video_title") or "(sin título)"}
Ángulo: {topic.get("angle") or "-"}
Hook del research: {topic.get("hook") or "-"}
Misterio: {topic.get("mystery") or "-"}
Revelación: {topic.get("reveal") or "-"}

═══ INVESTIGACIÓN (EVIDENCE POOL): la ÚNICA fuente de nombres, cifras, fechas y citas ═══
{pool_section(pool)}

═══ CÓMO SE VE UNA BUENA ESCALETA ═══
{FEWSHOT}
═══ {rules_text(*_profile(topic))}
{fb}
Devolvé la escaleta de ESTE tema en el JSON pedido. Pensá primero a quién seguimos y dónde está el pico; después
repartí los beats en los 7 caps."""


# ═══════════════════════════════════════════════════════════════
#  Validación
# ═══════════════════════════════════════════════════════════════

def _plain(s: str) -> str:
    return ev.norm(str(s or ""))


def question_problems(q: str, known: str, last_cap: bool, people: list[str]) -> list[str]:
    """Rúbrica §4 de la pregunta de pantalla. `known` = todo lo que el espectador ya vio (título del video y beats
    hasta este cap). La del cap 7 no es gancho («¿Cuántos siguen sin nombre?»): no se le pide nombrar algo ya visto,
    sí el resto de la rúbrica."""
    out = []
    t = str(q or "").strip()
    if not t:
        return ["falta la pregunta de pantalla"]
    if not (t.startswith("¿") and t.endswith("?")):
        out.append("tiene que empezar con «¿» y terminar con «?»")
    words = re.findall(r"[\wáéíóúñü0-9]+", t, re.I)
    if len(words) > Q_MAX_WORDS:
        out.append(f"{len(words)} palabras (máximo {Q_MAX_WORDS})")
    pt = _plain(t).lstrip("¿")
    if not pt.startswith(Q_OPENERS):
        out.append("tiene que preguntar por culpa, consecuencia o destino (¿Quién…? ¿Por qué…? ¿Dónde…? ¿Cuántos…?)")
    adm = [w for w in ADMIN_TERMS if re.search(rf"\b{w}\b", pt)]
    if adm:
        out.append(f"término administrativo {adm}")
    kn = _plain(known)
    caps = [w for w in re.findall(r"\b[A-ZÁÉÍÓÚÑ][\wáéíóúñ]+", t)[1:]]
    new_names = [w for w in caps if _plain(w) not in kn and not any(_plain(w) in _plain(p) for p in people)]
    if new_names:
        out.append(f"nombre propio que el espectador no conoce {new_names}")
    content = [w for w in words if len(w) >= 4 and _plain(w) not in {"quien", "quienes", "porque", "donde", "cuantos",
                                                                    "cuantas", "nadie", "nunca", "todavia", "siguen",
                                                                    "sigue", "estan", "esta", "fueron", "hubo"}]
    if not last_cap and content and not any(re.search(rf"\b{re.escape(_plain(w)[:5])}", kn) for w in content) \
            and not re.search(r"\d", t):
        out.append("no nombra nada que el espectador ya conozca (persona, grupo, lugar u objeto de este cap o anteriores)")
    return out


def _beat_known(beats: list[dict], upto_cap: int, pool: dict, esc: dict, context: str = "") -> str:
    its = ev.items(pool)
    txt = [context, str(esc.get("humano", {}).get("nombre") or ""), str(esc.get("promesa_gancho") or "")]
    for b in beats:
        if b["cap"] > upto_cap:
            break
        txt += [b.get("imagen_sensorial") or "", b.get("pregunta_abierta") or ""]
        for i in [b.get("dato_central")] + list(b.get("datos_apoyo") or []):
            if i in its:
                txt.append(ev.text_of(its[i]) + " " + str(its[i].get("autor") or ""))
    return " ".join(txt)


def validate(raw: dict, pool: dict, *, final: bool = False, context: str = "",
             solo_apoyo: list[str] | tuple[str, ...] = (), largo: dict | None = None
             ) -> tuple[dict, list[str], list[str], list[str]]:
    """(escaleta reparada, problemas duros, reparaciones, avisos). Problemas duros → reintento. `context` = lo que el
    espectador sabe antes del primer segundo (el título del video)."""
    esc = copy.deepcopy(raw or {})
    its = ev.items(pool)
    hard, rep, warn = [], [], []
    beats = sorted([b for b in esc.get("beats") or [] if isinstance(b, dict)], key=lambda b: int(b.get("n") or 0))
    esc["beats"] = beats
    cap_words, min_b, max_b, min_dev = _profile({"_largo": largo} if largo else {})
    if not min_b <= len(beats) <= max_b:
        hard.append(f"{len(beats)} beats (tienen que ser {min_b}–{max_b})")
    for k, b in enumerate(beats, start=1):
        b["n"] = k
        try:
            b["cap"] = int(b.get("cap"))
            b["intensidad"] = int(b.get("intensidad"))
            b["palabras_objetivo"] = int(b.get("palabras_objetivo") or 0)
        except (TypeError, ValueError):
            hard.append(f"beat {k}: cap/intensidad/palabras no numéricos")
            return esc, hard, rep, warn
        b["dato_central"] = str(b.get("dato_central") or "").strip().upper()
        b["datos_apoyo"] = [str(x).strip().upper() for x in b.get("datos_apoyo") or [] if str(x).strip()]
    caps = [b["cap"] for b in beats]
    if caps != sorted(caps) or set(caps) != set(range(1, 8)):
        hard.append(f"caps de los beats {caps}: tienen que ir de 1 a 7, en orden, con al menos un beat cada uno")
    short = [n for n in range(2, 7) if 0 < caps.count(n) < min_dev]
    if short:                                        # F8 §2: ≥ 2 beats por cap de desarrollo (verde)
        hard.append(f"caps de desarrollo con menos de {min_dev} beats: {short} (beats por cap: "
                    f"{[caps.count(n) for n in range(1, 8)]})")
    if beats and (beats[0]["cap"] != 1 or beats[0].get("funcion") != "gancho"):
        hard.append("el beat 1 tiene que ser la función «gancho» del cap 1")
    # ids: un dato central por beat, existente; un id en un solo beat
    seen: dict[str, int] = {}
    for b in beats:
        c = b["dato_central"]
        it = its.get(c)
        if not it or it["_kind"] not in ("datos", "cronologia", "citas"):
            hard.append(f"beat {b['n']}: dato_central «{c}» no existe en el pool (o no es D/T/Q)")
        elif c in seen:
            hard.append(f"beat {b['n']}: dato_central {c} ya está en el beat {seen[c]} (un id, un solo beat)")
        else:
            seen[c] = b["n"]
    for b in beats:
        if b["dato_central"] in solo_apoyo:
            hard.append(f"beat {b['n']}: {b['dato_central']} va solo como apoyo (indicación del editor), no como dato central")
    for b in beats:
        keep = []
        for i in b["datos_apoyo"]:
            it = its.get(i)
            if not it or it["_kind"] not in ("datos", "cronologia", "citas"):
                rep.append(f"beat {b['n']}: apoyo {i} no existe en el pool → fuera")
            elif i in seen and seen[i] != b["n"]:
                rep.append(f"beat {b['n']}: apoyo {i} ya está en el beat {seen[i]} → fuera")
            else:
                seen[i] = b["n"]
                keep.append(i)
        b["datos_apoyo"] = keep[:3]
    # curva
    pk = esc.get("pico") or {}
    try:
        pb = int(pk.get("beat"))
    except (TypeError, ValueError):
        pb = 0
    if not 1 <= pb <= len(beats):
        hard.append(f"pico.beat {pk.get('beat')} no es un beat")
    else:
        if pb == len(beats):
            hard.append("el pico no puede ser el último beat")
        inten = [b["intensidad"] for b in beats]
        if any(not INTENSITY[0] <= x <= INTENSITY[1] for x in inten):
            hard.append(f"intensidades fuera de {INTENSITY}: {inten}")
        ffs = [b["n"] for b in beats if b.get("flash_forward")]
        if any(n != 1 for n in ffs):
            hard.append(f"solo el beat 1 puede ser flash-forward (marcados: {ffs})")
        k0 = 1 if beats[0].get("flash_forward") else 0     # la curva se mide desde el beat 2 si el 1 es flash-forward
        drop = [beats[k]["n"] for k in range(k0 + 1, pb) if inten[k] < inten[k - 1]]
        if drop:
            hard.append(f"la intensidad baja antes del pico en los beats {drop} ({inten}): cada cap peor que el anterior"
                        + (" — si el beat 1 cuenta primero un momento POSTERIOR y más intenso, marcalo "
                           "`flash_forward: true` (la curva se mide desde el beat 2)"
                           if drop == [2] and not beats[0].get("flash_forward") else ""))
        if pb - 1 >= k0 and max(inten[k0:pb]) != inten[pb - 1]:
            hard.append(f"el beat del pico ({pb}) no es el de mayor intensidad hasta ahí ({inten})")
        if k0 and inten[0] > inten[pb - 1]:
            hard.append(f"el flash-forward ({inten[0]}) no puede ser más intenso que el pico ({inten[pb - 1]})")
        if not any(x == INTENSITY[0] for x in inten[pb:]):
            hard.append("falta un beat de intensidad 1 (respiro) después del pico")
        if pk.get("id") != beats[pb - 1]["dato_central"]:
            rep.append(f"pico.id {pk.get('id')} → {beats[pb - 1]['dato_central']} (el dato central del beat {pb})")
            pk["id"] = beats[pb - 1]["dato_central"]
    # humano y antagonista
    hum = esc.get("humano") or {}
    pers = {p["id"]: p for p in pool.get("personajes") or []}
    if hum.get("colectivo"):
        src = str(hum.get("fuente") or hum.get("id") or "").upper()
        if src not in its:
            hard.append(f"humano colectivo sin fuente del pool (fuente «{src}»)")
        if re.search(r"\b[A-ZÁÉÍÓÚ][a-záéíóúñ]+ [A-ZÁÉÍÓÚ][a-záéíóúñ]+\b", str(hum.get("nombre") or "")) and \
                not any(ev.norm(p["nombre"]) in ev.norm(hum["nombre"]) for p in pers.values()):
            hard.append(f"humano colectivo con algo que parece un nombre propio inventado: «{hum.get('nombre')}»")
    else:
        p = pers.get(str(hum.get("id") or "").upper())
        if not p:
            hard.append(f"humano {hum.get('id')} no es una persona del pool")
        elif p["nombre"] != hum.get("nombre"):
            rep.append(f"humano.nombre «{hum.get('nombre')}» → «{p['nombre']}» (el nombre exacto del pool)")
            hum["nombre"] = p["nombre"]
        if p and not p.get("testigo"):
            warn.append(f"el humano {p['nombre']} no es testigo en el pool")
    hcaps = sorted({b["cap"] for b in beats if b.get("humano_en_escena")})
    need = MIN_HUMAN_CAPS
    if not hum.get("colectivo") and pers.get(str(hum.get("id") or "").upper()):
        hp = pers[str(hum["id"]).upper()]
        sur = ev.norm(hp["nombre"]).split()[-1]

        verified_pool = any(q.get("verificacion") for q in pool.get("citas") or [])

        def _his(i: str) -> bool:
            it = its.get(i)
            if not it or it["_kind"] not in ("datos", "cronologia", "citas"):
                return False
            if not sur in ev.norm(ev.text_of(it) + " " + str(it.get("autor") or "")):
                return False
            # con verificación en el pool, una cita suya cuenta solo si está verificada
            return not (verified_pool and it["_kind"] == "citas" and
                        (it.get("verificacion") or {}).get("estado") != "verificada")
        own = [i for i in its if _his(i)]
        need = min(MIN_HUMAN_CAPS, len(own)) or 1
        for b in beats:                              # en escena = con un dato suyo en el beat (cita o mención)
            ids = [b["dato_central"]] + b["datos_apoyo"]
            if b.get("humano_en_escena") and not any(_his(i) for i in ids):
                hard.append(f"beat {b['n']}: {hp['nombre']} en escena sin un dato suyo verificado (ninguna cita ni "
                            f"mención en {ids}); datos suyos que valen: {own}")
        if len(own) < MIN_HUMAN_CAPS:
            warn.append(f"el pool tiene {len(own)} dato(s) de {hp['nombre']} ({own}): en escena en {need} cap(s)")
    if len(hcaps) < need:
        hard.append(f"el humano está en escena en los caps {hcaps}: tienen que ser ≥ {need}")
    elif hcaps and hcaps[0] > 2:
        hard.append(f"el humano entra recién en el cap {hcaps[0]}: tiene que entrar antes del cap 3")
    ant = pers.get(str((esc.get("antagonista") or {}).get("id") or "").upper())
    if not ant:
        hard.append(f"antagonista {(esc.get('antagonista') or {}).get('id')} no es una persona del pool")
    # gancho
    if has_figure(str(esc.get("promesa_gancho") or "")):
        hard.append("la promesa del gancho no lleva cifras ni años (tampoco en letras: «seis mil»; «miles» sí)")
    if not str(esc.get("promesa_gancho") or "").strip():
        hard.append("falta la promesa del gancho")
    if beats and has_figure(beats[0].get("imagen_sensorial") or ""):
        hard.append("la imagen sensorial del gancho no lleva cifras")
    for b in beats:
        im = str(b.get("imagen_sensorial") or "")
        content = [w for w in (_plain(x) for x in re.findall(r"[\wáéíóúñ]+", im)) if len(w) >= 4
                   and w not in {"sobre", "entre", "desde", "hasta", "como", "cuando", "donde", "para", "mientras"}]
        if len(im.split()) < 5:
            hard.append(f"beat {b['n']}: imagen sensorial vacía o demasiado corta")
        elif all(w in ABSTRACT for w in content):
            hard.append(f"beat {b['n']}: la imagen «{im}» es una idea, no algo para ver, oír, oler o tocar")
        if b.get("funcion") not in FUNCIONES:
            warn.append(f"beat {b['n']}: función «{b.get('funcion')}» fuera del catálogo")
    # a_pantalla: existen, no están en ningún beat, ≤ 2 por cap
    used = {i for b in beats for i in [b["dato_central"]] + b["datos_apoyo"]}
    ap, per = [], {}
    for x in esc.get("a_pantalla") or []:
        i, c = str((x or {}).get("id") or "").strip().upper(), (x or {}).get("cap")
        if i not in its or its[i]["_kind"] not in ("datos", "cronologia", "citas"):
            rep.append(f"a_pantalla {i}: no existe en el pool → fuera")
            continue
        if i in used:
            hard.append(f"a_pantalla {i} también está en un beat: lo que va a pantalla no lo dice la voz")
            continue
        if its[i]["_kind"] == "citas" and its[i].get("verificacion") and \
                its[i]["verificacion"].get("estado") != "verificada":
            rep.append(f"a_pantalla {i}: cita sin verificar → no va a pantalla")
            continue
        try:
            c = int(c)
        except (TypeError, ValueError):
            c = 0
        if not 1 <= c <= 7 or per.get(c, 0) >= 2:
            rep.append(f"a_pantalla {i}: cap {c} inválido o lleno → fuera")
            continue
        per[c] = per.get(c, 0) + 1
        ap.append({**x, "id": i, "cap": c})
    esc["a_pantalla"] = ap
    # un hecho, una cifra: la aproximada de un conteo no va en ningún beat
    for g in count_variants(pool):
        for b in beats:
            if b["dato_central"] in g["variantes"]:
                hard.append(f"beat {b['n']}: {b['dato_central']} es otra cifra del conteo {g['num']} [{g['canon']}]: "
                            "un hecho, una cifra (la precisa)")
            gone = [i for i in b["datos_apoyo"] if i in g["variantes"]]
            if gone:
                b["datos_apoyo"] = [i for i in b["datos_apoyo"] if i not in gone]
                rep.append(f"beat {b['n']}: apoyo {gone} es otra cifra del conteo {g['num']} → fuera")
    # cierre: la última frase nombra al humano o a un testigo (verificado, si el pool trae verificación)
    if beats:
        vp = any(q.get("verificacion") for q in pool.get("citas") or [])
        names = [p["nombre"] for p in pers.values() if (p.get("testigo_verificado") if vp else p.get("testigo"))]
        if not hum.get("colectivo") and hum.get("nombre") and (not vp or (pers.get(str(hum.get("id") or "").upper())
                                                                        or {}).get("testigo_verificado")):
            names.append(str(hum["nombre"]))
        names = list(dict.fromkeys(names))
        last = beats[-1].get("cierre") or ""
        if names and not any(ev.norm(n).split()[-1] in ev.norm(last) for n in names):
            hard.append(f"la última frase del video (cierre del beat {beats[-1]['n']}) no nombra al humano ni a un testigo "
                        f"{'verificado ' if vp else ''}({', '.join(names)}): «{last}»")
    # palabras por cap (reparación)
    for n, target in cap_words.items():
        bs = [b for b in beats if b["cap"] == n]
        tot = sum(b["palabras_objetivo"] for b in bs)
        if bs and (tot <= 0 or abs(tot - target) > WORDS_TOL * target):
            for b in bs:
                b["palabras_objetivo"] = max(20, round(target * (b["palabras_objetivo"] or 1) / (tot or len(bs))))
            rep.append(f"cap {n}: palabras {tot} → {sum(b['palabras_objetivo'] for b in bs)} (objetivo {target})")
    # preguntas de pantalla (rúbrica §4) en el último beat de cada cap
    people = [p["nombre"] for p in pers.values()] + [str(hum.get("nombre") or "")]
    qbad = []
    for n in range(1, 8):
        bs = [b for b in beats if b["cap"] == n]
        if not bs:
            continue
        last = bs[-1]
        for b in bs[:-1]:
            if str(b.get("pregunta_pantalla") or "").strip():
                b["pregunta_pantalla"] = ""
        # cap 1 (cold open: lo conocido es la escena que acaba de ver) y cap 7 (la pregunta que se queda): sin el
        # chequeo de «nombra algo ya visto»; el resto de la rúbrica, igual
        probs = question_problems(last.get("pregunta_pantalla"), _beat_known(beats, n, pool, esc, context), n in (1, 7),
                                  people)
        last["pregunta_valida"] = not [x for x in probs if not x.startswith("no nombra nada")]
        if probs:
            qbad.append(f"pregunta de pantalla del cap {n} «{last.get('pregunta_pantalla')}»: {'; '.join(probs)}")
    if qbad:
        # F6b-4: «nombra algo ya conocido» es heurística (raíces de palabras: «¿Por qué se negó a moverlos?» no pasa y
        # es buena) → aviso. El resto de la rúbrica es objetivo → duro (en el último intento, marcada). La del cap 7
        # es obligatoria (sin respaldo de gfx_question): siempre dura.
        soft = [q for q in qbad if re.fullmatch(r".*: no nombra nada que el espectador ya conozca \(.*\)", q)]
        warn.extend(soft)
        objective = [q for q in qbad if q not in soft]
        cap7 = [q for q in objective if q.startswith("pregunta de pantalla del cap 7")]
        (warn if final else hard).extend([q for q in objective if q not in cap7])
        hard.extend(cap7)
    # una cifra se ve en pantalla una sola vez (preguntas de pantalla + contadores)
    seen_fig: dict[str, str] = {}
    for b in beats:
        figs = []
        if b.get("contador") and b["dato_central"] in its:
            it = its[b["dato_central"]]
            figs += re.findall(r"\d[\d,.]*\d|\d", str(it.get("valor") or ev.text_of(it)))[:1]
        figs += re.findall(r"\d[\d,.]*\d|\d", str(b.get("pregunta_pantalla") or ""))
        for f in figs:
            k = re.sub(r"[,.]", "", f)
            where = f"beat {b['n']} ({'contador' if b.get('contador') and f in figs[:1] else 'pregunta'})"
            if k in seen_fig and seen_fig[k] != where:
                hard.append(f"la cifra {f} se ve en pantalla dos veces ({seen_fig[k]} y {where}): una vez por video")
            seen_fig.setdefault(k, where)
    if beats:                                        # la última frase no repite textual una cita
        last5 = _plain(beats[-1].get("cierre") or "")
        for q in pool.get("citas") or []:
            ws = _plain(q.get("texto") or "").split()
            if any(" ".join(ws[k:k + 5]) in last5 for k in range(max(0, len(ws) - 4))) and len(ws) >= 5 or \
                    (len(ws) < 5 and ws and " ".join(ws) in last5):
                hard.append(f"la última frase repite textual la cita {q['id']}: decila con otras palabras")
    # cronología (aviso: la dramaturgia puede volver atrás)
    prev = None
    for b in beats:
        if b.get("flash_forward"):
            continue
        d = ev.item_date(its[b["dato_central"]]) if b["dato_central"] in its else None
        if d and prev and d < prev and 2 <= b["cap"] <= 6:
            warn.append(f"beat {b['n']}: vuelve atrás en el tiempo ({d} < {prev})")
        prev = d or prev
    return esc, hard, rep, warn


# ═══════════════════════════════════════════════════════════════
#  Caps, pool plan y persistencia
# ═══════════════════════════════════════════════════════════════

def caps_view(esc: dict) -> dict:
    """Vista skeleton (chapters con evidence_ids) para heredar canonize_figures / assign_screen_ids."""
    chs = []
    for c in CHAPTER_SCHEMA:
        n = c["chapter_number"]
        bs = [b for b in esc["beats"] if b["cap"] == n]
        ids = [i for b in bs for i in [b["dato_central"]] + b["datos_apoyo"]]
        nxt = next((b for b in esc["beats"] if b["cap"] == n + 1), None)
        chs.append({**c, "evidence_ids": ids, "cliffhanger": nxt["dato_central"] if nxt else "",
                    "narrative_intent": DEFAULT_INTENT_BY_CAP[n]})
    return {"chapters": chs}


def apply_pool_plan(esc: dict, pool: dict) -> None:
    """In place: cifras canónicas y reservados para pantalla (m01a_skeleton.finalize_pool_plan) sobre los caps; las
    variantes que la canónica saca de un cap salen de sus beats (la oficial entra como apoyo del primer beat)."""
    sk = caps_view(esc)
    finalize_pool_plan(sk, pool)
    for ch in sk["chapters"]:
        n = ch["chapter_number"]
        bs = [b for b in esc["beats"] if b["cap"] == n]
        keep = set(ch["evidence_ids"])
        for b in bs:
            if b["dato_central"] not in keep:
                off = next((i for i in ch["evidence_ids"] if i not in {x for y in bs for x in [y["dato_central"]] + y["datos_apoyo"]}), None)
                esc.setdefault("_reparaciones", []).append(
                    f"beat {b['n']}: dato central {b['dato_central']} es variante de una cifra canónica → {off or 'sin cambio'}")
                if off:
                    b["dato_central"] = off
            b["datos_apoyo"] = [i for i in b["datos_apoyo"] if i in keep]
        used = {x for y in bs for x in [y["dato_central"]] + y["datos_apoyo"]}
        extra = [i for i in ch["evidence_ids"] if i not in used]
        if extra and bs:
            bs[0]["datos_apoyo"] = bs[0]["datos_apoyo"] + extra
    _screen_by_date(esc, sk, pool)
    esc["instrucciones_guionista"] = writer_instructions(esc, pool)
    esc["caps"] = [{k: ch[k] for k in ("chapter_number", "role", "render_engine", "duration_seconds",
                                      "narrative_intent", "evidence_ids", "cliffhanger")}
                   | {"pantalla_ids": ch.get("pantalla_ids") or [],
                      "palabras_objetivo": sum(b["palabras_objetivo"] for b in esc["beats"] if b["cap"] == ch["chapter_number"]),
                      **({"contradiccion_cifras": ch["contradiccion_cifras"]} if ch.get("contradiccion_cifras") else {})}
                   for ch in sk["chapters"]]
    esc["_pool_plan"] = sk.get("_pool_plan")


def _cap_spans(esc: dict, pool: dict) -> dict[int, tuple[str, str]]:
    """Rango de fechas que narra cada cap: las fechas de sus DATOS CENTRALES (un apoyo puede ser un antecedente lejano y
    estiraría el rango; el flash-forward no cuenta)."""
    its = ev.items(pool)
    out = {}
    for n in range(1, 8):
        ds = sorted(d for b in esc["beats"] if b["cap"] == n and not b.get("flash_forward")
                    for d in [ev.item_date(its[b["dato_central"]]) if b["dato_central"] in its else None] if d)
        if ds:
            out[n] = (ds[0], ds[-1])
    return out


def _screen_by_date(esc: dict, sk: dict, pool: dict) -> None:
    """F6b-3 (in place sobre sk["chapters"][*]["pantalla_ids"]): primero los `a_pantalla` de la escaleta; después los
    reservados automáticos CON FECHA, por la fecha de los beats: al cap que la contiene (si hay varios, el que empieza
    más cerca de ella); si cae entre caps, al primero que empieza después (mostrar algo anterior a lo narrado vale; algo
    posterior, no); si es posterior a todo lo narrado, al cap siguiente al último con fecha (o más adelante, si el
    reparto por palabras ya lo había puesto ahí). ≤ 2 por cap; un
    reservado que cuenta lo mismo que otro ya en pantalla (≥ 60 % de palabras en común) sale."""
    from script_engine.m01a_skeleton import SCREEN_PER_CAP
    its = ev.items(pool)
    spans = _cap_spans(esc, pool)
    chs = {c["chapter_number"]: c for c in sk["chapters"]}
    auto = [(c["chapter_number"], i) for c in sk["chapters"] for i in c.get("pantalla_ids") or []]
    for c in chs.values():
        c["pantalla_ids"] = []
    notes = []
    for x in esc.get("a_pantalla") or []:
        chs[x["cap"]]["pantalla_ids"].append(x["id"])
    forced = {x["id"] for x in esc.get("a_pantalla") or []}

    def _target(d: str, n0: int) -> int:
        inside = [k for k, (a, b) in spans.items() if a[:10] <= d <= b[:10]]
        if inside:
            return max(inside, key=lambda k: (spans[k][0], -k))
        after = [k for k, (a, _) in spans.items() if a[:10] > d]
        if after:
            return min(after)
        return max(n0, min(7, max(spans) + 1))    # posterior a todo: después del último cap con fecha

    def _dup(i: str) -> str | None:
        w = ev._content(ev.text_of(its[i]))
        for c in chs.values():
            for j in c["pantalla_ids"]:
                o = ev._content(ev.text_of(its[j])) if j in its else set()
                if w and o and len(w & o) / min(len(w), len(o)) >= 0.6:
                    return j
        return None
    for n0, i in auto:
        if i in forced:
            continue
        v = (its.get(i) or {}).get("verificacion")
        if v and v.get("estado") != "verificada":
            notes.append(f"{i}: cita sin verificar → no va a pantalla")
            continue
        d = ev.item_date(its[i]) if i in its else None
        n = n0
        if d and len(d) >= 10 and spans:
            n = _target(d[:10], n0)
        j = _dup(i) if i in its else None
        if j:
            notes.append(f"{i} cuenta lo mismo que {j}, ya en pantalla: fuera")
            continue
        if len(chs[n]["pantalla_ids"]) >= SCREEN_PER_CAP:
            notes.append(f"{i} ({d}) → cap {n} lleno: fuera")
            continue
        chs[n]["pantalla_ids"].append(i)
        if n != n0:
            notes.append(f"{i} ({d}) del cap {n0} al cap {n} (por fecha)")
    esc["_pantalla_por_fecha"] = notes


def writer_instructions(esc: dict, pool: dict) -> list[str]:
    """Reglas deterministas para el guionista (m01b v3)."""
    out = []
    for g in count_variants(pool):
        out.append(f"La cifra {g['num']} {g['unit']} se dice UNA sola vez; nunca «{'», «'.join(g['otras'])}» ni «más de "
                   f"{min(g['otras'], key=len)}».")
    its = ev.items(pool)
    used = {i for b in esc["beats"] for i in [b["dato_central"]] + b["datos_apoyo"]}
    for g in count_variants(pool):                 # una cita que trae otra cifra del mismo conteo: sin esa cifra
        for i in sorted(used):
            it = its.get(i)
            if it and it["_kind"] == "citas" and any(
                    re.search(rf"(?<![\d,.]){re.escape(x)}(?![\d,.])", it["texto"]) for x in g["otras"]):
                out.append(f"{i} trae otra cifra del conteo {g['num']}: se parafrasea SIN esa cifra (no se cita textual).")
    for q in pool.get("citas") or []:
        v = q.get("verificacion") or {}
        if q["id"] in used and v and v.get("estado") != "verificada":
            out.append(f"{q['id']} (de {q.get('autor')}) está SIN VERIFICAR: se usa sin su nombre («un preso», "
                       f"«una guardia»…).")
    for x in esc.get("a_pantalla") or []:
        if x["id"] in its:
            out.append(f"{x['id']} va a pantalla (cap {x['cap']}): la voz no lo dice.")
    return out


def _persist(topic_id: str, esc: dict) -> Path:
    d = STEPS_DIR / topic_id
    d.mkdir(parents=True, exist_ok=True)
    out = d / "01a_escaleta.json"
    out.write_text(json.dumps(esc, ensure_ascii=False, indent=2), encoding="utf-8")
    return out


def pool_gate_profile(topic: dict, pool: dict, *, persist: bool = True, log: list[str] | None = None) -> dict | None:
    """F7d (HANDOFF_F7 §9.2): la compuerta del pool antes de la escaleta, solo para pools de research v3
    (`_research_v3`; los pools viejos siguen igual). Escribe POOL_GATE.md en los pasos del topic. Rojo → PoolGateRed
    (no se gasta en guion). Amarillo → `topic["_largo"]`: palabras por cap escaladas a `target_words` del amarillo y
    hasta `gate_yellow_max_beats` beats. Devuelve el gate (o None)."""
    if not pool.get("_research_v3"):
        return None
    from researcher_steps import pool_gate as pg
    topic_id = topic.get("id") or topic.get("topic_id")
    gate = pg.check(pool, topic_id, STEPS_DIR / topic_id if persist else None)
    if gate["color"] == pg.YELLOW:
        k = gate["target_words"] / max(1, sum(CAP_WORDS.values()))
        topic["_largo"] = {"cap_words": {n: round(w * k) for n, w in CAP_WORDS.items()},
                           "max_beats": gate["max_beats"], "min_beats_dev_cap": _vl("gate_yellow_min_beats_dev_cap")}
    if log is not None:
        log.append(f"  [escaleta] compuerta del pool: {gate['color']} {gate['metricas']}"
                   + (f" · {gate['motivos']}" if gate["motivos"] else ""))
    return gate


def is_v3(topic: dict) -> bool:
    """Guion v3 solo con evidence_pool y con el flag (GUION_V3=1 o topic["guion_version"] == 3)."""
    return bool(topic.get("evidence_pool")) and (os.environ.get("GUION_V3") == "1" or topic.get("guion_version") == 3)


def generate_escaleta(topic: dict, *, call: Callable[..., dict] | None = None, attempts: int = MAX_ATTEMPTS,
                      log: list[str] | None = None, persist: bool = True) -> dict:
    """Escaleta del topic (Pro, hasta `attempts` con feedback). EscaletaValidationError si ninguna pasa."""
    log = log if log is not None else []
    topic_id = topic.get("id") or topic.get("topic_id")
    if not topic_id:
        raise ValueError("topic sin 'id' ni 'topic_id'")
    if topic.get("escaleta_frozen") or _frozen_is_escaleta(topic):
        return frozen_escaleta(topic)
    pool = topic.get("evidence_pool") or {}
    if not pool:
        raise ValueError("la escaleta v3 necesita evidence_pool (sin pool: camino v2)")
    gate = pool_gate_profile(topic, pool, persist=persist, log=log)        # F7d: rojo → PoolGateRed, sin gastar
    if call is None:
        from gemini_helpers import call_pro_json as call
    feedback: list[str] = []
    intentos = []
    for k in range(1, attempts + 1):
        raw = call(build_prompt(topic, pool, feedback), system_instruction=SYSTEM, response_schema=SCHEMA,
                   description=f"m01a_escaleta intento {k}")
        esc, hard, rep, warn = validate(raw, pool, final=k == attempts, context=str(topic.get("video_title") or ""),
                                        solo_apoyo=tuple(topic.get("escaleta_solo_apoyo") or ()),
                                        largo=topic.get("_largo"))
        intentos.append({"intento": k, "problemas": hard, "reparaciones": rep, "avisos": warn})
        log.append(f"  [escaleta] intento {k}: {len(hard)} problema(s) {hard[:4]} · {len(rep)} reparación(es)")
        if not hard:
            esc.update({"topic_id": topic_id, "prompt_version": PROMPT_VERSION, "_reparaciones": rep, "_avisos": warn,
                        "_intentos": intentos})
            if gate:
                esc["pool_gate"] = {k: gate[k] for k in ("color", "metricas", "motivos", "target_words")}
            apply_pool_plan(esc, pool)
            if persist:
                _persist(topic_id, esc)
            return esc
        feedback = hard
    fail = {"topic_id": topic_id, "prompt_version": PROMPT_VERSION, "_intentos": intentos, "ultima": raw}
    if persist:
        (STEPS_DIR / topic_id).mkdir(parents=True, exist_ok=True)
        (STEPS_DIR / topic_id / "01a_escaleta_rechazada.json").write_text(json.dumps(fail, ensure_ascii=False, indent=2),
                                                                          encoding="utf-8")
    raise EscaletaValidationError(f"escaleta rechazada después de {attempts} intentos: {intentos[-1]['problemas']}")


def _frozen_is_escaleta(topic: dict) -> bool:
    cfg = topic.get("skeleton_frozen") or {}
    try:
        return bool(cfg) and "beats" in json.loads(Path(cfg["skeleton"]).read_text(encoding="utf-8"))
    except (OSError, ValueError, KeyError, TypeError):
        return False


def frozen_escaleta(topic: dict) -> dict:
    """Token `escaleta_frozen` = {"escaleta": <01a_escaleta.json>, "pool": <01_facts_sources.json de sus ids>} (o
    `skeleton_frozen` con una escaleta en "skeleton"). Traduce los ids al pool actual por texto; lo que ya no está
    sale (anotado en `_frozen`). Vuelve a validar y a correr el pool plan."""
    cfg = topic.get("escaleta_frozen") or {"escaleta": topic["skeleton_frozen"]["skeleton"],
                                           "pool": topic["skeleton_frozen"].get("pool")}
    esc = json.loads(Path(cfg["escaleta"]).read_text(encoding="utf-8"))
    cur = topic.get("evidence_pool") or {}
    remap: dict[str, str | None] = {}
    if cfg.get("pool"):
        old = json.loads(Path(cfg["pool"]).read_text(encoding="utf-8"))
        old = old.get("evidence_pool", old)
        by_text = {(it["_kind"], ev.norm(ev.text_of(it))): i for i, it in ev.items(cur).items()}
        remap = {i: by_text.get((it["_kind"], ev.norm(ev.text_of(it)))) for i, it in ev.items(old).items()}
    notes = []

    def _m(i: str) -> str | None:
        return remap.get(i) if remap else i
    for b in esc["beats"]:
        nc = _m(b["dato_central"])
        if not nc:
            notes.append(f"beat {b['n']}: {b['dato_central']} fuera del pool actual")
        b["dato_central"] = nc or b["dato_central"]
        b["datos_apoyo"] = [x for x in (_m(i) for i in b["datos_apoyo"]) if x]
    for k in ("humano", "antagonista", "pico"):
        if esc.get(k, {}).get("id") and remap:
            esc[k]["id"] = _m(esc[k]["id"]) or esc[k]["id"]
    esc2, hard, rep, warn = validate(esc, cur, final=True, context=str(topic.get("video_title") or ""),
                                     solo_apoyo=tuple(topic.get("escaleta_solo_apoyo") or ()))
    esc2.update({"topic_id": topic.get("id") or topic.get("topic_id"), "_reparaciones": rep, "_avisos": warn,
                 "_frozen": {"escaleta": str(cfg["escaleta"]), "pool": str(cfg.get("pool") or ""), "notas": notes,
                             "problemas": hard}})
    apply_pool_plan(esc2, cur)
    _persist(esc2["topic_id"], esc2)
    return esc2


# ═══════════════════════════════════════════════════════════════
#  Legible (para Omar)
# ═══════════════════════════════════════════════════════════════

def to_markdown(esc: dict, pool: dict) -> str:
    its = ev.items(pool)

    def _t(i: str) -> str:
        it = its.get(i)
        if not it:
            return i
        x = ev.text_of(it)
        return f"{i} «{x if len(x) <= 140 else x[:137] + '…'}»" + (f" — {it['autor']}" if it.get("autor") else "")
    h, a = esc.get("humano") or {}, esc.get("antagonista") or {}
    pers = {p["id"]: p for p in pool.get("personajes") or []}
    lines = ["# Escaleta — " + str(esc.get("topic_id")), "",
             f"**Humano que seguimos:** {h.get('nombre')} ({h.get('rol')}, {h.get('id')}) — {h.get('por_que')}",
             f"**Antagonista:** {pers.get(a.get('id'), {}).get('nombre', a.get('id'))} — {a.get('por_que') or ''}",
             f"**Promesa del gancho:** {esc.get('promesa_gancho')}",
             f"**Pico:** beat {(esc.get('pico') or {}).get('beat')} · {_t((esc.get('pico') or {}).get('id', ''))} — "
             f"{(esc.get('pico') or {}).get('por_que')}",
             f"**Cierre humano:** {esc.get('cierre_humano')}", "",
             "Curva: " + " → ".join(f"{b['n']}:{b['intensidad']}" for b in esc["beats"]), ""]
    for c in esc.get("caps") or []:
        n = c["chapter_number"]
        lines += [f"## Cap {n} · {c['role']} · {c['palabras_objetivo']} palabras"
                  + (f" · pantalla (no se narra): {', '.join(c['pantalla_ids'])}" if c.get("pantalla_ids") else ""), ""]
        for b in [b for b in esc["beats"] if b["cap"] == n]:
            lines += [f"**Beat {b['n']} — {b['funcion']}{' (flash-forward)' if b.get('flash_forward') else ''} · "
                      f"{b['emocion']} · intensidad {b['intensidad']}"
                      + (" · humano en escena" if b.get("humano_en_escena") else "")
                      + (" · CONTADOR en pantalla" if b.get("contador") else "") + f" · {b['palabras_objetivo']} pal.**",
                      f"- Imagen: {b['imagen_sensorial']}",
                      f"- Dato central: {_t(b['dato_central'])}"]
            if b["datos_apoyo"]:
                lines.append("- Apoyo: " + "; ".join(_t(i) for i in b["datos_apoyo"]))
            lines.append(f"- Queda abierta: {b['pregunta_abierta']}")
            if b.get("pregunta_pantalla"):
                lines.append(f"- Pregunta en pantalla: **{b['pregunta_pantalla']}**"
                             + ("" if b.get("pregunta_valida", True) else " ⚠ no pasa la rúbrica (respaldo: gfx_question)"))
            lines += [f"- Cierre: {b['cierre']}", ""]
    if esc.get("a_pantalla"):
        lines += ["## A pantalla (la escaleta lo manda a pantalla; la voz no lo dice)", ""] + \
                 [f"- cap {x['cap']}: {_t(x['id'])} — {x.get('por_que') or ''}" for x in esc["a_pantalla"]] + [""]
    if esc.get("instrucciones_guionista"):
        lines += ["## Instrucciones al guionista (deterministas)", ""] + \
                 [f"- {x}" for x in esc["instrucciones_guionista"]] + [""]
    if esc.get("_pantalla_por_fecha"):
        lines += ["## Reservados movidos por fecha", ""] + [f"- {x}" for x in esc["_pantalla_por_fecha"]] + [""]
    if esc.get("_reparaciones"):
        lines += ["## Reparaciones del validador", ""] + [f"- {x}" for x in esc["_reparaciones"]] + [""]
    if esc.get("_avisos"):
        lines += ["## Avisos", ""] + [f"- {x}" for x in esc["_avisos"]] + [""]
    return "\n".join(lines)
