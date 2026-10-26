"""
script_engine/gfx_rotulista.py — F29b §A: el rotulista. El texto de pantalla lo escribe alguien, anclado a la oración.

Regla (Omar): un bloque vale si (a) dice algo que la voz no dice, (b) sobre lo que la voz cuenta en ese momento y (c) sin
adelantar. Con `gfx_rules.rotulista` y escaleta (realizador), por cap:
    entrada    oraciones de la voz con tiempos (gfx_peak.sentences, las mismas del `sentence_idx` del pico), beats del
               cap (gfx_beats_chNN.json), ítems = los `a_pantalla` del cap + `dato_central`/`datos_apoyo` de sus beats
               (texto fuente completo, fuente, `por_que`), lo ya mostrado (los `a_pantalla` de caps anteriores: se
               conocen antes de la tanda y dejan correr los 7 caps en paralelo) y el pico ÚNICO del cap (pico_cap).
    llamada    UNA por cap con claude_helpers (Sonnet 5.5 por defecto, effort medium, JSON sin esquema), prompt literal
               (ROTULISTA_SYSTEM / ROTULISTA_USER), cruda en `_fase2b_work/rotulista_chNN.raw.json` (caché por pedido).
               Un reintento si no parsea o si A.4 saca algo; otro si faltan `a_pantalla`. Tope de US$ antes de cada
               llamada. Si no hay respuesta válida, el cap sale sin bloques de texto (nunca se inventa).
    validar    (A.4, determinista) anclaje (t0 = fin de la oración + 0.3 s, dentro de la ventana del beat del ítem),
               largo, tipo, etiqueta de la cifra, candado (cita = subcadena del texto fuente; resto = cada número, nombre
               propio y año en el texto fuente), no dicho (±20 s) y spoiler (después de t0), topes (5, gancho 1, 1 por
               oración, `a_pantalla` primero).
    colocar    cifra → data_callout figure (cara anton, sin sello); recorte → archive_clipping; cita → quote_card;
               persona → data_callout serif «Nombre · cargo»; lupa → evidence_zoom con la caja de visión del detalle.
Lecturas declaradas (F29b_REPORT): «persona» nombra a alguien que la voz nombra → su nombre no cuenta en «no dicho»; un
nombre propio es spoiler si la voz lo dice después de t0 y no antes en el cap; los números, si la voz los dice después.
Sin escaleta o con el flag apagado no corre nada de esto.
"""
from __future__ import annotations

import hashlib
import json
import re
import threading
import time
from pathlib import Path
from typing import Any, Callable

from script_engine import evidence as ev

PROMPT_VERSION = "f29b-1"
MODELO_DEFAULT = "claude-sonnet-5-5"
EFFORT_DEFAULT = "medium"
TIPOS = ("cifra", "recorte", "cita", "persona", "lupa")
TOPE_CAP = 5
TOPE_GANCHO = 1
MAX_PALABRAS, MAX_PALABRAS_CIFRA = 9, 6
ANCLA_S = 0.3                  # el bloque entra 0.3 s después del fin de su oración
DUR_MIN, DUR_MAX = 2.5, 6.0
VOZ_S = 20.0                   # «no dicho»: la voz ±20 s alrededor de t0
OUT_TOKENS_PEOR = 16_000       # peor caso de salida para el tope (razonamiento + JSON)

# ═══════════════════════ prompt (HANDOFF_F29b §A.3, literal) ═══════════════════════

ROTULISTA_SYSTEM = """Sos el rotulista de un documental de historia oscura en español. Recibís la narración de un capítulo, oración por oración y con tiempos, y una lista de datos verificados (citas, cifras, hechos) con su texto fuente. Tu trabajo es decidir qué va escrito en pantalla, en qué oración, de qué tipo y con qué palabras.

Un texto en pantalla vale solo si cumple las tres a la vez:
(a) dice algo que la narración NO dice en ese capítulo (ni antes ni después de esa oración);
(b) es sobre lo que la narración está contando en esa oración exacta;
(c) no adelanta nada que la narración vaya a decir más adelante.
Si para una oración no hay ningún dato que cumpla las tres, no va nada. La pantalla vacía es correcta. Nunca repitas la narración con otras palabras; nunca parafrasees lo que la voz acaba de decir o va a decir.

Tipos de bloque y su compuerta (solo podés usar un tipo cuando la narración, en esa oración, está hablando de eso):
- cifra: la narración habla de esa magnitud (altura, muertos, metros cúbicos, dinero). Lleva etiqueta obligatoria que diga de qué es la cifra. Ej.: «Altura de la presa: 266 m».
- recorte: la narración cuenta ese hecho o ese documento. Aporta el quién, el cargo, la fecha, lo que dice el acta o la carta. Lleva kicker = nombre real del documento o la fuente, con año.
- cita: la narración nombra a esa persona o lee de ella. Texto literal del dato, sin cambiar una palabra, con el autor.
- persona: la narración nombra a alguien por primera vez en el capítulo. Texto = nombre y cargo, tal como están en el dato.
- lupa: la narración nombra un detalle chico que está en la imagen (una fisura, una firma, una fecha en un papel, una marca en el muro). Nunca el sujeto principal de la foto. Texto = qué se señala, ≤ 4 palabras.

Reglas de escritura:
- Máximo 9 palabras (cifra con etiqueta: máximo 6). Oración completa o etiqueta + valor; nunca un fragmento cortado sin sujeto o sin el valor.
- Para citas: copiá el texto del dato literal. Para cifras, recortes, personas y lupas: redactá, pero cada número, nombre propio, fecha y cantidad que escribas tiene que estar en el texto fuente de ese dato. Si el dato no trae el valor, no lo inventes: no va.
- Los datos marcados `a_pantalla` son obligatorios: tienen que salir, en la oración que mejor corresponda, y con lo que pide su `por_que` (si el `por_que` pide «la cifra en liras», la cifra tiene que estar).
- Tope: 5 bloques por capítulo; en el beat `gancho`, máximo 1. Un bloque por oración.
- El pico del capítulo no tiene privilegio: lleva bloque solo si hay un dato que cumpla (a)(b)(c) en esa oración.
- Si un dato ya se mostró en un capítulo anterior, no lo repitas.

Para cada bloque explicá en una línea `aporta` qué dice que la narración no dice (ej.: «el quién: Consejo Superior de Obras Públicas», «la cifra: 1.910 muertos»). Si no podés escribir esa línea con algo concreto, el bloque no va.

Respondé SOLO con JSON válido, sin texto antes ni después."""

ROTULISTA_USER = """CAPÍTULO {cap} — {titulo}

NARRACIÓN (oración por oración, con segundos):
{oraciones: "[idx] t0–t1 · texto"}

BEATS DEL CAPÍTULO (función, ventana en segundos, cierre):
{beats}

PICO DEL CAPÍTULO: oración [{pico_idx}] «{pico_frase}»

DATOS DISPONIBLES (solo estos; cada uno con su texto fuente):
{items: "- id · tipo Q/D/T · a_pantalla: sí/no · por_que: … · fuente: … · texto fuente: «…»"}

YA MOSTRADO EN CAPÍTULOS ANTERIORES (no repetir):
{ya_mostrado}

Devolvé:
{"bloques": [{"sentence_idx": int, "tipo": "cifra|recorte|cita|persona|lupa", "texto": str, "etiqueta_o_kicker": str|null, "pool_id": str, "aporta": str}], "descartados": [{"pool_id": str, "motivo": str}]}"""

_HUECOS = ("{cap}", "{titulo}", '{oraciones: "[idx] t0–t1 · texto"}', "{beats}", "{pico_idx}", "{pico_frase}",
           '{items: "- id · tipo Q/D/T · a_pantalla: sí/no · por_que: … · fuente: … · texto fuente: «…»"}',
           "{ya_mostrado}")


def prompt_md5() -> str:
    return hashlib.md5((ROTULISTA_SYSTEM + "\n\n" + ROTULISTA_USER).encode("utf-8")).hexdigest()


# ═══════════════════════ números y nombres ═══════════════════════

_DIG = re.compile(r"\d[\d.,]*\d|\d")
_NUMW = re.compile(r"^(?:cero|uno|una|un|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|once|doce|trece|catorce|"
                   r"quince|dieci\w+|veint\w*|treinta|cuarenta|cincuenta|sesenta|setenta|ochenta|noventa|cien|ciento|"
                   r"\w+cient[oa]s|quinient[oa]s|mil|millon(?:es)?|y)$")
_W2N: dict[str, int] = {}
_W2N_LOCK = threading.Lock()


def _w2n() -> dict[str, int]:
    """Palabras → entero (0–99 999, masc. y fem.), sin tildes: el conversor de num_es al revés."""
    with _W2N_LOCK:
        if not _W2N:
            from script_engine.num_es import words
            for n in range(100_000):
                for fem in (False, True):
                    _W2N.setdefault(ev.norm(words(n, fem)), n)
    return _W2N


def numeros(texto: str) -> list[str]:
    """Cifras de un texto: en dígitos (tal cual) y en letras (como entero en dígitos). «un/una/uno» sueltos no cuentan
    (son artículos casi siempre)."""
    out = [m.group(0).rstrip(".,") for m in _DIG.finditer(texto or "")]
    toks = re.findall(r"[^\W\d_]+", ev.norm(texto))
    i = 0
    while i < len(toks):
        if not _NUMW.match(toks[i]) or toks[i] == "y":
            i += 1
            continue
        j = i
        while j < len(toks) and _NUMW.match(toks[j]):
            j += 1
        run = toks[i:j]
        while run and run[-1] == "y":
            run.pop()
        k = 0
        while k < len(run):                       # el tramo más largo que es un número, de izquierda a derecha
            for e in range(len(run), k, -1):
                s = " ".join(run[k:e])
                if s in _w2n() and not (e - k == 1 and run[k] in ("un", "una", "uno", "y")):
                    out.append(str(_w2n()[s]))
                    k = e
                    break
            else:
                k += 1
        i = j
    return list(dict.fromkeys(x for x in out if x))


def nombres(texto: str) -> list[str]:
    """Nombres propios: tokens con mayúscula inicial que no abren el texto ni una oración (tras . : ! ? «)."""
    out = []
    for m in re.finditer(r"[A-ZÁÉÍÓÚÑÜ][\wáéíóúñü'’-]*", texto or ""):
        antes = (texto[:m.start()]).rstrip()
        if not antes or antes[-1] in ".:!?¿¡«\"“(·":
            continue
        if len(m.group(0)) < 2:
            continue
        out.append(m.group(0))
    return list(dict.fromkeys(out))


def cargo_de(texto: str) -> list[str]:
    """Las palabras de contenido del cargo de un bloque «persona» (lo que sigue al nombre: «Giorgio Dal Piaz,
    geólogo» → [geólogo]); sin artículos ni preposiciones."""
    nom = nombre_inicial(texto)
    ws = palabras(texto)
    k = 0
    while k < len(ws) and re.sub(r"^[«\"“(]+|[.,;:!?»\"”)·]+$", "", ws[k]) in nom:
        k += 1
    resto = [re.sub(r"[^\wáéíóúñü'’-]", "", w) for w in ws[k:]]
    return [w for w in resto if len(w) >= 4 and ev.norm(w) not in _ARTPREP and ev.norm(w) not in ev._FUNC]


def _raiz_en(w: str, texto: str) -> bool:
    """¿La palabra está en el texto por su raíz de 5 letras («ingeniero» = «ingeniera», «geólogo» = «geólogos»)?"""
    r = ev.norm(w)[:5]
    return bool(r) and any(t.startswith(r) for t in re.findall(r"[^\W\d_]+", ev.norm(texto)))


def _palabra_en(tok: str, texto: str) -> bool:
    return bool(re.search(rf"(?<![\w]){re.escape(ev.norm(tok))}(?![\w])", ev.norm(texto)))


def _valor(tok: str) -> Any:
    from script_engine.num_es import parse_int
    n = parse_int(tok)
    return n if n is not None else tok.replace(",", ".")


def numero_en(num: str, texto: str) -> bool:
    """¿La cifra está en el texto, en dígitos o en letras, por VALOR? «1.910» = «1910» = «mil novecientas diez»; los
    decimales, tal cual («4,6» = «4.6»)."""
    return _valor(num) in {_valor(x) for x in numeros(texto)}


def palabras(t: str) -> list[str]:
    return re.findall(r"\S+", t or "")


_ARTPREP = {"de", "del", "la", "las", "el", "los", "un", "una", "unos", "unas", "a", "al", "en", "con", "por", "para",
            "y", "o", "que", "sin", "sobre", "entre", "hasta", "desde", "su", "sus"}


def munon(texto: str) -> bool:
    """Fragmento cortado: empieza en minúscula (sin sujeto) o termina en preposición/artículo."""
    t = re.sub(r"^[\s«\"“¿¡(]+", "", texto or "")
    if t and t[0].isalpha() and t[0].islower():
        return True
    ws = palabras(re.sub(r"[.,;:!?…»\"”)]+$", "", t))
    return bool(ws) and ev.norm(ws[-1]) in _ARTPREP


# ═══════════════════════ entrada ═══════════════════════

def oraciones(words: list[dict], time_offset: float = 0.0) -> list[dict[str, Any]]:
    from script_engine.gfx_peak import sentences
    return [{"idx": k, "t0": round(s["t0"], 3), "t1": round(s["t1"], 3), "texto": s["text"]}
            for k, s in enumerate(sentences(words, time_offset))]


def _tipo_id(i: str) -> str:
    return (str(i)[:1] or "?").upper()


def items_cap(cap: int, escaleta: dict, beats: list[dict], pool: dict | None) -> list[dict[str, Any]]:
    """Los `a_pantalla` del cap + `dato_central`/`datos_apoyo` de sus beats (nada más), con su texto fuente completo."""
    from script_engine.gfx_realizador import beat_de_pantalla
    its = ev.items(pool) if pool else {}
    out: dict[str, dict[str, Any]] = {}
    for a in escaleta.get("a_pantalla") or []:
        if int(a.get("cap") or 0) != cap:
            continue
        i = str(a.get("id"))
        n, _ = beat_de_pantalla(a, beats)
        if i in its and i not in out:
            out[i] = {"id": i, "a_pantalla": True, "por_que": str(a.get("por_que") or ""), "beats": [n] if n else []}
    for b in beats:
        for i in [b["dato_central"]] + list(b["datos_apoyo"]):
            if not i or i not in its:
                continue
            x = out.setdefault(i, {"id": i, "a_pantalla": False, "por_que": "", "beats": []})
            if b["n"] not in x["beats"]:
                x["beats"].append(b["n"])
    res = []
    for i, x in out.items():
        it = its[i]
        res.append({**x, "tipo": _tipo_id(i), "kind": it["_kind"], "texto": re.sub(r"\s+", " ", ev.text_of(it)).strip(),
                    "fuente": str(it.get("fuente") or ""), "autor": str(it.get("autor") or "")})
    return res


def ya_mostrado(cap: int, escaleta: dict, pool: dict | None) -> list[dict[str, str]]:
    """Los `a_pantalla` de los caps anteriores (salen sí o sí: se saben antes de correr los caps en paralelo). Lo que
    de verdad salió en caps anteriores se vuelve a mirar al colocar (gfx_pool.used_ids_before)."""
    its = ev.items(pool) if pool else {}
    out = []
    for a in escaleta.get("a_pantalla") or []:
        i = str(a.get("id"))
        if int(a.get("cap") or 0) < cap and i in its:
            out.append({"id": i, "texto": re.sub(r"\s+", " ", ev.text_of(its[i])).strip()})
    return sorted(out, key=lambda x: x["id"])


def _raices(t: str) -> set[str]:
    from script_engine.gfx_realizador import _raices as r
    return r(t)


def pico_cap(cap: int, escaleta: dict, beats: list[dict], sents: list[dict], pool: dict | None) -> dict[str, Any] | None:
    """El pico ÚNICO del cap (lo leen el rotulista, el realizador y music_intensity): el beat de `escaleta.pico` si cae
    en este cap; si no, el beat más intenso del cap (empate: el primero, como music_intensity). La frase = la oración
    del beat con más raíces en común con su dato (el de `escaleta.pico` o el `dato_central`); empate: la primera."""
    from script_engine.music_intensity import beat_pico_de_cap
    if not beats or not sents:
        return None
    pk = escaleta.get("pico") or {}
    n = beat_pico_de_cap(beats, pk.get("beat"))
    b = next(x for x in beats if x["n"] == n)
    en_beat = [s for s in sents if b["t0"] - 0.3 <= s["t0"] <= b["t1"]] or sents[:1]
    its = ev.items(pool) if pool else {}
    dato = str(pk.get("id")) if pk.get("beat") == n and pk.get("id") else b["dato_central"]
    ref = _raices(ev.text_of(its[dato])) if dato in its else set()
    s = max(en_beat, key=lambda x: (len(ref & _raices(x["texto"])), -x["idx"]))
    return {"beat": n, "funcion": b["funcion"], "sentence_idx": s["idx"], "frase": s["texto"], "t": s["t0"],
            "dato": dato, "fuente": "escaleta.pico" if pk.get("beat") == n else "escaleta (beat más intenso del cap)"}


def entrada(cap: int, real: dict, escaleta: dict, pool: dict | None, words: list[dict], time_offset: float,
            titulo: str | None = None) -> dict[str, Any]:
    sents = oraciones(words, time_offset)
    beats = real["beats"]
    its = items_cap(cap, escaleta, beats, pool)
    pk = pico_cap(cap, escaleta, beats, sents, pool)
    tit = titulo or " · ".join(dict.fromkeys(b["funcion"] for b in beats))
    return {"cap": cap, "titulo": tit, "oraciones": sents,
            "beats": [{k: b[k] for k in ("n", "funcion", "t0", "t1", "cierre", "dato_central", "datos_apoyo")}
                      for b in beats],
            "items": its, "ya_mostrado": ya_mostrado(cap, escaleta, pool), "pico": pk}


def prompt_user(ent: dict[str, Any]) -> str:
    def item_line(x: dict) -> str:
        fuente = x["fuente"] or "—"
        if x["kind"] == "citas" and x["autor"]:
            fuente += f" (autor: {x['autor']})"
        return (f"- {x['id']} · tipo {x['tipo']} · a_pantalla: {'sí' if x['a_pantalla'] else 'no'} · por_que: "
                f"{x['por_que'] or '—'} · fuente: {fuente} · texto fuente: «{x['texto']}»")
    pk = ent["pico"] or {"sentence_idx": "—", "frase": "—"}
    vals = (str(ent["cap"]), ent["titulo"],
            "\n".join(f"[{s['idx']}] {s['t0']:.1f}–{s['t1']:.1f} · {s['texto']}" for s in ent["oraciones"]),
            "\n".join(f"- beat {b['n']} · {b['funcion']} · {b['t0']:.1f}–{b['t1']:.1f} s · cierre: «{b['cierre'] or '—'}»"
                      for b in ent["beats"]),
            str(pk["sentence_idx"]), pk["frase"],
            "\n".join(item_line(x) for x in ent["items"]) or "(ninguno)",
            "\n".join(f"- {x['id']} «{x['texto']}»" for x in ent["ya_mostrado"]) or "(nada)")
    out = ROTULISTA_USER
    for h, v in zip(_HUECOS, vals):
        out = out.replace(h, v)
    return out


# ═══════════════════════ validar (A.4) ═══════════════════════

def _voz(words: list[dict], time_offset: float, a: float, b: float) -> str:
    return " ".join(str(w.get("word", "")) for w in words if a <= float(w["start"]) + time_offset <= b)


def duracion(texto: str) -> float:
    return round(min(DUR_MAX, max(DUR_MIN, len(palabras(texto)) / 3 + 1)), 2)


def texto_en_pantalla(b: dict[str, Any]) -> str:
    """Lo que se lee. Cifra: si el texto ya trae «etiqueta: valor» o es una frase que nombra la cifra («Murieron 1.910
    personas»), el texto; si es solo el valor («266 m»), «etiqueta: valor». El resto, el texto."""
    t = re.sub(r"\s+", " ", str(b.get("texto") or "")).strip()
    et = re.sub(r"\s+", " ", str(b.get("etiqueta_o_kicker") or "")).strip()
    if b.get("tipo") == "cifra" and et and ":" not in t and re.match(r"^[\s~≈+-]*(?:más de |menos de |casi )?\d", t, re.I):
        return f"{et}: {t}"
    return t


_PARTICULAS = {"de", "del", "da", "dal", "della", "di", "van", "von", "la", "le", "y"}


def nombre_inicial(texto: str) -> set[str]:
    """Los tokens del nombre con que abre un bloque «persona» («Giorgio Dal Piaz, geólogo» → Giorgio, Dal, Piaz)."""
    out: set[str] = set()
    for w in palabras(texto):
        c = re.sub(r"^[«\"“(]+|[.,;:!?»\"”)·]+$", "", w)
        if c and (c[0].isupper() or (out and c.lower() in _PARTICULAS)):
            out.add(c)
            if w != c and w[-1] in ",;:·":
                break
        else:
            break
    return out


def _ventanas(x: dict, beats: list[dict]) -> list[tuple[float, float]]:
    return [(b["t0"], b["t1"]) for b in beats if b["n"] in x["beats"]]


def validar(resp: Any, ent: dict[str, Any], words: list[dict], time_offset: float = 0.0) -> dict[str, Any]:
    """{bloques, rechazos, faltan}: cada bloque que pasa A.4.1–A.4.5 (con t0, dur, beat, pantalla), cada uno que sale
    con su motivo, y los `a_pantalla` que no salieron."""
    its = {x["id"]: x for x in ent["items"]}
    sents = {s["idx"]: s for s in ent["oraciones"]}
    beats = ent["beats"]
    ok, rech = [], []

    def fuera(b: dict, regla: str, motivo: str) -> None:
        rech.append({"pool_id": b.get("pool_id"), "texto": b.get("texto"), "sentence_idx": b.get("sentence_idx"),
                     "regla": regla, "motivo": motivo})
    bl = (resp or {}).get("bloques") if isinstance(resp, dict) else None
    for b in bl if isinstance(bl, list) else []:
        if not isinstance(b, dict):
            continue
        b = dict(b)
        pid = str(b.get("pool_id") or "")
        x = its.get(pid)
        if x is None:
            fuera(b, "A.4.1", f"pool_id {pid!r} no está en los datos del cap")
            continue
        try:
            si = int(b.get("sentence_idx"))
        except (TypeError, ValueError):
            si = None
        s = sents.get(si) if si is not None else None
        if s is None:
            fuera(b, "A.4.1", f"sentence_idx {b.get('sentence_idx')!r} no existe")
            continue
        t0 = round(s["t1"] + ANCLA_S, 3)
        win = _ventanas(x, beats)
        dentro = [w for w in win if w[0] - 0.3 <= t0 <= w[1] + ANCLA_S + 0.05]
        if not dentro:
            fuera(b, "A.4.1", f"t0 {t0:.1f}s fuera de la ventana del beat de {pid} "
                              f"({', '.join(f'{a:.1f}–{c:.1f}' for a, c in win) or 'sin beat'})")
            continue
        tipo = str(b.get("tipo") or "").strip().lower()
        if tipo not in TIPOS:
            fuera(b, "A.4.2", f"tipo {tipo!r} no válido")
            continue
        b["tipo"] = tipo
        txt = re.sub(r"\s+", " ", str(b.get("texto") or "")).strip()
        b["texto"] = txt
        et = re.sub(r"\s+", " ", str(b.get("etiqueta_o_kicker") or "")).strip() or None
        b["etiqueta_o_kicker"] = et
        if not txt:
            fuera(b, "A.4.2", "texto vacío")
            continue
        if tipo == "cifra" and not et:
            fuera(b, "A.4.2", "cifra sin etiqueta")
            continue
        if tipo == "cifra" and not numeros(txt):
            fuera(b, "A.4.2", "cifra sin número")
            continue
        pant = texto_en_pantalla(b)
        tope = MAX_PALABRAS_CIFRA if tipo == "cifra" else (4 if tipo == "lupa" else MAX_PALABRAS)
        if len(palabras(pant)) > tope:
            fuera(b, "A.4.2", f"{len(palabras(pant))} palabras (tope {tope})")
            continue
        if tipo != "lupa" and munon(pant):
            fuera(b, "A.4.2", "fragmento cortado (empieza en minúscula o termina en preposición/artículo)")
            continue
        if not str(b.get("aporta") or "").strip():
            fuera(b, "A.4.2", "sin `aporta`")
            continue
        # A.4.3 candado
        fuente = x["texto"]
        if tipo == "cita":
            limpio = re.sub(r"^[«\"“'…\s]+|[»\"”'…\s]+$", "", txt)
            if ev.norm(limpio) not in ev.norm(fuente):
                fuera(b, "A.4.3", "la cita no es literal del texto fuente")
                continue
        else:
            malos = [n for n in numeros(pant) if not numero_en(n, fuente)]
            malos += [n for n in nombres(pant) if not _palabra_en(n, fuente)]
            if tipo == "persona":              # A.4.3: el nombre (abre el texto: nombres() no lo mira) y el cargo
                malos += [n for n in nombre_inicial(txt) if n.lower() not in _PARTICULAS and not _palabra_en(n, fuente)]
                malos += [w for w in cargo_de(txt) if not _raiz_en(w, fuente)]
            if et and tipo == "recorte":       # el kicker sale del texto o de la fuente del dato
                malos += [n for n in numeros(et) + nombres(et)
                          if not (numero_en(n, fuente + " " + x["fuente"]) or _palabra_en(n, fuente + " " + x["fuente"]))]
            if malos:
                fuera(b, "A.4.3", f"no están en el texto fuente de {pid}: {sorted(set(malos))}")
                continue
        # A.4.4 no dicho y spoiler (sobre el texto que se lee, no sobre el kicker ni la fuente)
        cerca = _voz(words, time_offset, t0 - VOZ_S, t0 + VOZ_S)
        nums = numeros(txt if tipo != "cifra" else pant)
        exento = nombre_inicial(txt) if tipo == "persona" else set()     # el nombre de la persona (lo dice la voz)
        nms = [n for n in nombres(pant) if n not in exento]
        dichos = [n for n in nums if numero_en(n, cerca)] + [n for n in nms if _palabra_en(n, cerca)]
        if dichos:
            fuera(b, "A.4.4", f"la voz lo dice a ±{VOZ_S:.0f} s: {dichos}")
            continue
        despues = _voz(words, time_offset, t0, 1e9)
        antes = _voz(words, time_offset, -1e9, t0)
        spoil = [n for n in nums if numero_en(n, despues)] + \
                [n for n in nms if _palabra_en(n, despues) and not _palabra_en(n, antes)]
        if spoil:
            fuera(b, "A.4.4", f"spoiler: la voz lo dice después de t0: {spoil}")
            continue
        bt = next(bb for bb in beats if (bb["t0"], bb["t1"]) == dentro[0])
        ok.append({**b, "sentence_idx": si, "t0": t0, "dur": duracion(pant), "beat": bt["n"], "funcion": bt["funcion"],
                   "pantalla": pant, "a_pantalla": x["a_pantalla"]})
    # A.4.5 topes: a_pantalla primero, después por oración; 1 por oración, 1 en el gancho, 5 por cap
    ok.sort(key=lambda b: (not b["a_pantalla"], b["sentence_idx"]))
    keep, por_or, gancho, vistos = [], set(), 0, set()
    for b in ok:
        if b["pool_id"] in vistos:
            fuera(b, "A.4.5", "el mismo dato dos veces")
        elif b["sentence_idx"] in por_or:
            fuera(b, "A.4.5", "ya hay un bloque en esa oración")
        elif b["funcion"] == "gancho" and gancho >= TOPE_GANCHO:
            fuera(b, "A.4.5", f"tope del gancho ({TOPE_GANCHO})")
        elif len(keep) >= TOPE_CAP:
            fuera(b, "A.4.5", f"tope del cap ({TOPE_CAP})")
        else:
            keep.append(b)
            por_or.add(b["sentence_idx"])
            vistos.add(b["pool_id"])
            gancho += b["funcion"] == "gancho"
    keep.sort(key=lambda b: b["t0"])
    salen = {b["pool_id"]: b for b in keep}
    faltan = [x["id"] for x in ent["items"] if x["a_pantalla"] and x["id"] not in salen]
    incompletos = {}
    for x in ent["items"]:
        if x["a_pantalla"] and x["id"] in salen:
            falta = lo_que_pide(x["por_que"], x["texto"], salen[x["id"]]["pantalla"])
            if falta:
                incompletos[x["id"]] = falta
    return {"bloques": keep, "rechazos": rech, "faltan": faltan, "incompletos": incompletos}


def lo_que_pide(por_que: str, fuente: str, pantalla: str) -> str | None:
    """Lo que el `por_que` de un `a_pantalla` pide y el bloque no trae (None si cumple): si el `por_que` nombra cifras,
    esas cifras; si pide «la cifra» (o «cifra de …»), al menos una cifra del texto fuente. El resto (que Q50 salga
    «como carta del municipio») no se puede medir con reglas: lo cuenta la hoja."""
    sin_anios = re.sub(r"\b(1[5-9]\d\d|20\d\d)\b(?=\s*[:.,;)]|\s*$)", " ", por_que or "")   # «… de 1943:» es contexto
    pide = numeros(sin_anios)
    if pide:
        faltan = [n for n in pide if not numero_en(n, pantalla)]
        return f"las cifras del por_que {faltan}" if faltan else None
    if re.search(r"\bcifra", ev.norm(por_que)):
        tiene = [n for n in numeros(pantalla) if numero_en(n, fuente)]
        return None if tiene else "la cifra que pide el por_que"
    return None


# ═══════════════════════ llamada ═══════════════════════

_LOCK = threading.Lock()
_EN_VUELO: dict[str, float] = {}      # peor caso (US$) de las llamadas en curso, por carpeta de trabajo


def _ledger(work_dir: Path) -> Path:
    return Path(work_dir) / "rotulista_costos.json"


def gastado(work_dir: Path) -> float:
    f = _ledger(work_dir)
    try:
        return float(json.loads(f.read_text(encoding="utf-8")).get("usd", 0.0)) if f.exists() else 0.0
    except (OSError, ValueError):
        return 0.0


def _post_con_registro(work_dir: Path, cap_id: str, modelo: str, tope: float, crudos: list[dict]) -> Callable[[dict], dict]:
    import claude_helpers as hx

    def post(body: dict) -> dict:
        pin, pout = hx.PRICES.get(hx._base(modelo), (0.0, 0.0))
        peor = len(json.dumps(body, ensure_ascii=False)) / 2.5 / 1e6 * pin + OUT_TOKENS_PEOR / 1e6 * pout
        clave = str(Path(work_dir).resolve())
        with _LOCK:                      # lo gastado + el peor caso de las llamadas que están en vuelo (prefetch en
            vuelo = _EN_VUELO.get(clave, 0.0)   # paralelo: las 7 ven el mismo gasto inicial si solo se mira el ledger)
            if gastado(work_dir) + vuelo + peor > tope:
                raise TopeRotulista(f"tope Claude del rotulista US$ {tope:.2f} (gastado {gastado(work_dir):.4f}, "
                                    f"en vuelo {vuelo:.4f}, esta llamada hasta {peor:.4f})")
            _EN_VUELO[clave] = vuelo + peor
        t0 = time.time()
        try:
            r = hx._post(body)
        finally:
            with _LOCK:
                _EN_VUELO[clave] = max(0.0, _EN_VUELO.get(clave, 0.0) - peor)
        u = r.get("usage") or {}
        usd = round(hx.cost_of(modelo, u), 5)
        crudos.append({"respuesta": r, "segundos": round(time.time() - t0, 1), "usd": usd})
        with _LOCK:
            f = _ledger(work_dir)
            c = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {"llamadas": [], "usd": 0.0}
            c["llamadas"].append({"cap": cap_id, "in": u.get("input_tokens"), "out": u.get("output_tokens"),
                                  "stop": r.get("stop_reason"), "usd": usd, "segundos": round(time.time() - t0, 1)})
            c["usd"] = round(sum(x["usd"] for x in c["llamadas"]), 5)
            f.write_text(json.dumps(c, ensure_ascii=False, indent=1), encoding="utf-8")
        return r
    return post


class TopeRotulista(RuntimeError):
    """El tope de costo del rotulista no alcanza para otra llamada: el cap sale sin bloques de texto."""


def _reintento(user: str, errores: list[str]) -> str:
    return user + "\n\nTU RESPUESTA ANTERIOR TUVO ESTOS PROBLEMAS (corregilos y devolvé el JSON completo otra vez):\n" + \
        "\n".join(f"- {e}" for e in errores)


def llamar(ent: dict[str, Any], words: list[dict], time_offset: float, work_dir: Path, cap_id: str, *,
           modelo: str | None = None, effort: str | None = None, tope: float = 2.0,
           call: Callable[..., dict] | None = None, log: list[str] | None = None) -> dict[str, Any]:
    """Rotulista de un cap (con caché por pedido). Devuelve {modelo, intentos, final, validacion, error?}. `call` (tests)
    reemplaza la llamada: recibe (prompt, system_instruction=, description=) y devuelve el dict parseado."""
    import claude_helpers as hx
    modelo, effort = modelo or MODELO_DEFAULT, effort or EFFORT_DEFAULT
    log = log if log is not None else []
    user = prompt_user(ent)
    clave = hashlib.sha1(f"{PROMPT_VERSION}|{modelo}|{effort}|{ROTULISTA_SYSTEM}|{user}".encode("utf-8")).hexdigest()[:20]
    raw_f = Path(work_dir) / f"rotulista_{cap_id}.raw.json"
    try:
        prev = json.loads(raw_f.read_text(encoding="utf-8")) if raw_f.exists() else None
    except (OSError, ValueError):
        prev = None
    if prev and prev.get("clave") == clave and prev.get("final") is not None:
        prev["validacion"] = validar(prev["final"], ent, words, time_offset)   # A.4 es determinista: con el código de hoy
        v = prev.get("validacion") or {"bloques": []}
        log.append(f"  rotulista {cap_id}: caché ({len(prev.get('intentos') or [])} intento(s), {len(v['bloques'])} bloques)")
        return {**prev, "cache": True}
    out: dict[str, Any] = {"clave": clave, "modelo": modelo, "effort": effort, "prompt_version": PROMPT_VERSION,
                           "prompt_md5": prompt_md5(), "entrada": ent, "intentos": [], "final": None, "validacion": None}
    usados = {"forma": False, "a_pantalla": False}
    pedido = user
    for _ in range(3):
        crudos: list[dict] = []
        t0 = time.time()
        err = None
        try:
            if call is not None:
                resp = call(pedido, system_instruction=ROTULISTA_SYSTEM, description=f"gfx_rotulista {cap_id}")
            else:
                c = hx.make_call(modelo, effort, post=_post_con_registro(work_dir, cap_id, modelo, tope, crudos))
                resp = c(pedido, system_instruction=ROTULISTA_SYSTEM, response_schema=None,
                         description=f"gfx_rotulista {cap_id}")
        except TopeRotulista as e:
            out["error"] = str(e)
            log.append(f"  rotulista: {e} → cap sin bloques de texto")
            break
        except Exception as e:  # noqa: BLE001 — JSON roto tras los reintentos de claude_helpers o la API caída
            resp, err = None, f"{type(e).__name__}: {str(e)[:200]}"
        val = validar(resp, ent, words, time_offset) if resp is not None else None
        out["intentos"].append({"pedido": pedido, "respuesta": resp, "crudas": crudos, "error": err, "validacion": val,
                                "segundos": round(time.time() - t0, 1)})
        if resp is None:
            if usados["forma"]:
                out["final"], out["validacion"] = None, None
                log.append(f"  rotulista: la respuesta no parsea dos veces ({err}) → cap sin bloques de texto")
                break
            usados["forma"] = True
            pedido = _reintento(user, [f"la respuesta no es JSON válido ({err})"])
            continue
        out["final"], out["validacion"] = resp, val
        errores = []
        if val["rechazos"] and not usados["forma"]:
            usados["forma"] = True
            errores += [f"{r['pool_id']} en la oración [{r['sentence_idx']}] «{r['texto']}»: {r['motivo']}"
                        for r in val["rechazos"]]
        if (val["faltan"] or val["incompletos"]) and not usados["a_pantalla"]:
            usados["a_pantalla"] = True
            pq = {x["id"]: x["por_que"] for x in ent["items"]}
            errores += [f"falta el dato a_pantalla {i} (por_que: {pq.get(i)})" for i in val["faltan"]]
            errores += [f"el dato a_pantalla {i} salió sin {f} (por_que: {pq.get(i)})"
                        for i, f in val["incompletos"].items()]
        if not errores:
            break
        pedido = _reintento(user, errores)
    v = out["validacion"]
    if v is not None:
        log.append(f"  rotulista {cap_id}: {len(out['intentos'])} intento(s) · {len(v['bloques'])} bloque(s) · "
                   f"{len(v['rechazos'])} fuera por A.4 · a_pantalla que faltan {v['faltan']} · incompletos {v['incompletos']}")
    raw_f.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


# ═══════════════════════ colocar (A.4.6) ═══════════════════════

def colocar(plan: dict[str, Any], res: dict[str, Any], ent: dict[str, Any], *, scenes: list[Any], pool: dict | None,
            used_before: set[str], lupa_box: Callable[[int, str], tuple[list[float], str] | None] | None,
            zoom_dur: float, log: list[str]) -> list[dict[str, Any]]:
    """Los bloques del rotulista en el plan (reemplazan recortes, datos, cita, contador, nivel de agua y el zoom del
    director). Devuelve una fila por bloque (colocado o fuera, con el motivo)."""
    from script_engine.gfx_pool import short_source
    from script_engine.gfx_project import scene_at
    its = ev.items(pool) if pool else {}
    viejos = {k: plan.get(k) for k in ("archive_clippings", "callouts", "quote_card", "count_up", "water_level",
                                       "evidence_zoom")}
    plan["archive_clippings"], plan["callouts"] = [], []
    for k in ("quote_card", "count_up", "water_level", "evidence_zoom"):
        plan[k] = None
    filas: list[dict[str, Any]] = []
    v = res.get("validacion") or {"bloques": [], "rechazos": [], "faltan": []}
    for r in v["rechazos"]:
        filas.append({**r, "accion": "fuera"})
    for b in v["bloques"]:
        pid, t0, dur = b["pool_id"], b["t0"], b["dur"]
        it = its.get(pid) or {}
        sc = scene_at(scenes, t0)
        side = getattr(sc, "quiet_side", "right") or "right"
        meta = {"pool_id": pid, "rotulista": True, "beat": b["beat"], "sentence_idx": b["sentence_idx"],
                "aporta": b.get("aporta"), "tipo_rotulista": b["tipo"]}
        fila = {"pool_id": pid, "tipo": b["tipo"], "texto": b["pantalla"], "sentence_idx": b["sentence_idx"],
                "t0": t0, "aporta": b.get("aporta"), "beat": b["beat"]}
        if pid in used_before:
            filas.append({**fila, "accion": "fuera", "regla": "A.4.5", "motivo": "ya se mostró en un cap anterior"})
            continue
        if b["tipo"] in ("cifra", "persona"):
            plan["callouts"].append({"text": b["pantalla"], "start": t0, "kind": "figure" if b["tipo"] == "cifra" else "name",
                                     "face": "anton" if b["tipo"] == "cifra" else "serif", "anim": "slide",
                                     "duration": dur, "side": side, "fact_idx": None, **meta})
        elif b["tipo"] == "recorte":
            plan["archive_clippings"].append({"kicker": b.get("etiqueta_o_kicker") or short_source(it.get("fuente")),
                                              "headline": b["pantalla"], "body": "", "scene_idx": sc.idx,
                                              "fact_idx": None, "fuente": it.get("fuente"), "era_decade": 2000,
                                              "start": t0, "duration": dur, "side": side, **meta})
        elif b["tipo"] == "cita":
            if plan.get("quote_card"):
                filas.append({**fila, "accion": "fuera", "regla": "A.4.6", "motivo": "una sola cita por cap (quote_card)"})
                continue
            if not it.get("autor"):
                filas.append({**fila, "accion": "fuera", "regla": "A.4.6", "motivo": "la cita no tiene autor"})
                continue
            plan["quote_card"] = {"text": re.sub(r"^[«\"“]+|[»\"”]+$", "", b["pantalla"]), "author": it["autor"],
                                  "start": t0, "duration": dur, **meta}
        elif b["tipo"] == "lupa":
            got = lupa_box(sc.idx, b["pantalla"]) if lupa_box else None
            if plan.get("evidence_zoom"):
                filas.append({**fila, "accion": "fuera", "regla": "A.4.6", "motivo": "una sola lupa por cap"})
                continue
            if got is None:
                filas.append({**fila, "accion": "fuera", "regla": "A.4.6",
                              "motivo": f"visión no encuentra «{b['pantalla']}» en la escena {sc.idx}"})
                continue
            if sc.end - t0 < zoom_dur:
                filas.append({**fila, "accion": "fuera", "regla": "A.4.6",
                              "motivo": f"la escena termina {sc.end - t0:.1f} s después (el zoom pide {zoom_dur:.1f})"})
                continue
            box, label = got
            plan["evidence_zoom"] = {"scene_idx": sc.idx, "box": box, "start": t0, "anchor": label, "detail": label,
                                     "como": "rotulista", **meta}
        filas.append({**fila, "accion": "colocado"})
    plan["callouts"].sort(key=lambda c: c["start"])
    plan["archive_clippings"].sort(key=lambda c: c["start"])
    plan["rotulista"] = {"modelo": res.get("modelo"), "faltan_a_pantalla": v.get("faltan"),
                         "a_pantalla_incompletos": v.get("incompletos") or {}, "filas": filas,
                         "error": res.get("error"),
                         "director_antes": {k: (len(x) if isinstance(x, list) else bool(x)) for k, x in viejos.items()}}
    log.append(f"  rotulista: colocados {[(f['pool_id'], f['tipo'], f['texto']) for f in filas if f['accion'] == 'colocado']}"
               f" · fuera {[(f.get('pool_id'), f.get('regla'), f.get('motivo')) for f in filas if f['accion'] == 'fuera']}")
    return filas


def lupa_de_detalles(details: dict[int, list[dict]], verify: Callable[[int, dict], bool]
                     ) -> Callable[[int, str], tuple[list[float], str] | None]:
    """La caja del detalle que nombra la lupa: el detalle de visión de esa escena con más raíces en común con el texto
    (≥ 1), confirmado recortando la caja."""
    def box(si: int, texto: str) -> tuple[list[float], str] | None:
        want = {w[:4] for w in re.findall(r"[^\W\d_]{4,}", ev.norm(texto))}
        cands = sorted(((len(want & {w[:4] for w in re.findall(r"[^\W\d_]{4,}", ev.norm(d["label"]))}), d)
                        for d in details.get(si) or []), key=lambda x: -x[0])
        for n, d in cands:
            if n >= 1 and verify(si, d):
                return d["box"], d["label"]
        return None
    return box


# ═══════════════════════ pico (sello) ═══════════════════════

def pico_plan(plan: dict[str, Any], ent: dict[str, Any], *, words: list[dict], scenes: list[Any], moods: dict,
              intensity: dict | None, time_offset: float, freq: dict | None, log: list[str]) -> dict[str, Any] | None:
    """El pico del plan = el de la escaleta (pico_cap), sin privilegio de bloque: solo la palabra del pico (el sello de
    siempre, ≤ 1). gfx_peak no decide el pico cuando hay escaleta."""
    from script_engine.gfx_peak import add_peak_word, sentences
    pk = ent.get("pico")
    if not pk:
        return None
    s = sentences(words, time_offset)[pk["sentence_idx"]]
    peak = {**s, "t": pk["t"]}
    plan["pico"] = {"t": pk["t"], "block": None, "word": None, "sentence": pk["frase"], "sentence_idx": pk["sentence_idx"],
                    "beat": pk["beat"], "fuente": pk["fuente"]}
    from gfx_config import gfx_rules
    if gfx_rules.peak_word:
        em = add_peak_word(plan, peak, words=words, scenes=scenes, moods=moods, block=None, time_offset=time_offset,
                           freq=freq, log=log)
        if em is not None:
            plan["pico"]["word"] = plan["pico"]["palabra"] = em["word"]
    log.append(f"  pico (escaleta, beat {pk['beat']}): oración [{pk['sentence_idx']}] @ {pk['t']:.1f}s «{pk['frase'][:70]}»"
               f" · palabra {plan['pico'].get('word')!r}")
    return plan["pico"]


# ═══════════════════════ prefetch (los 7 caps en paralelo) ═══════════════════════

def preparar_cap(chplan: Any, video_id: str, work_dir: Path, time_offset: float = 0.0
                 ) -> tuple[dict, list[dict], dict] | None:
    """(entrada, palabras, ctx) de un cap, sin escenas ni visión (lo mismo que arma apply_gfx)."""
    from config import DATA_DIR
    from script_engine import gfx_realizador as gr
    from script_engine.gfx_director import load_chapter_context
    from script_engine.gfx_layer import remapped_words
    _, words = remapped_words(chplan)
    ctx = load_chapter_context(video_id, chplan)
    carga = gr.cargar(ctx.get("topic_id") or ctx["video_id"], DATA_DIR / "scripts" / "_steps")
    if carga is None or not ctx.get("pool"):
        return None
    real = gr.preparar(ctx["chapter_number"], carga, ctx.get("pool"), words, time_offset, work_dir, chplan.chapter_id)
    return entrada(ctx["chapter_number"], real, carga["escaleta"], ctx.get("pool"), words, time_offset), words, ctx


def prefetch(plans: list[Any], video_id: str, work_dir: Path, offsets: dict[str, float] | None = None, *,
             modelo: str | None = None, effort: str | None = None, tope: float = 2.0,
             max_workers: int = 7) -> dict[str, Any]:
    """Rotulista de todos los caps en paralelo (threads) → `rotulista_chNN.raw.json`. apply_gfx lo encuentra en caché.
    Nunca lanza: un cap que falla lo vuelve a intentar apply_gfx."""
    from concurrent.futures import ThreadPoolExecutor

    def one(chplan: Any) -> tuple[str, Any]:
        cap = chplan.chapter_id
        t0 = time.time()
        try:
            got = preparar_cap(chplan, video_id, work_dir, (offsets or {}).get(cap, 0.0))
            if got is None:
                return cap, "sin escaleta/pool"
            ent, words, _ = got
            r = llamar(ent, words, (offsets or {}).get(cap, 0.0), work_dir, cap, modelo=modelo, effort=effort, tope=tope)
            v = r.get("validacion") or {}
            return cap, {"segundos": round(time.time() - t0, 1), "cache": bool(r.get("cache")),
                         "bloques": len(v.get("bloques") or []), "intentos": len(r.get("intentos") or [])}
        except Exception as e:  # noqa: BLE001
            return cap, f"falló ({type(e).__name__}: {str(e)[:120]})"
    Path(work_dir).mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        return dict(ex.map(one, plans))
