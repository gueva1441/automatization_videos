"""
script_engine/gfx_rotulista.py — F29b §A: el rotulista. El texto de pantalla lo escribe alguien, anclado a la oración.
F29c: por beat, anclado a la palabra, y la ficha es el title card.

Regla (Omar): un bloque vale si (a) dice algo que la voz no dice, (b) sobre lo que la voz cuenta en ese momento y (c) sin
adelantar. Con `gfx_rules.rotulista` y escaleta (realizador), por cap:
    entrada    oraciones de la voz con tiempos y cada palabra numerada (gfx_peak.sentences), el beat de cada oración,
               beats del cap (gfx_beats_chNN.json), ítems = los `a_pantalla` del cap + `dato_central`/`datos_apoyo` de
               sus beats (texto fuente completo, fuente, `por_que`), lo ya mostrado (los `a_pantalla` de caps
               anteriores: dejan correr los 7 caps en paralelo), el pico ÚNICO del cap (pico_cap) y la voz de todo el
               video (para la coherencia de cifras).
    llamada    UNA por cap con claude_helpers (Sonnet 5.5 por defecto, effort medium, JSON sin esquema), prompt literal
               (ROTULISTA_SYSTEM / ROTULISTA_USER, HANDOFF_F29c §A.5), cruda en `_fase2b_work/rotulista_chNN.raw.json`
               (caché por pedido). De la respuesta se toma el primer objeto JSON válido (§A.6.1). Un reintento si no
               parsea o si una regla de contenido saca algo; otro si faltan `a_pantalla`. Tope de US$ antes de cada
               llamada (con las llamadas en vuelo). Sin respuesta válida, el cap sale sin bloques (nunca se inventa).
    validar    (determinista) anclaje (oración y palabra que existen, en un beat del ítem; el `a_pantalla` del beat pico
               pasa al beat siguiente si su ítem es de ese beat), forma (tipo, etiqueta, valor, muñón, que quepa en la
               ficha), candado (cita = subcadena del texto fuente; resto = cada número, nombre propio y año en el texto
               fuente), tiempos (§A.2: t0 = la palabra `word_idx`; t1 = fin de la oración, o de la siguiente si no
               alcanza el mínimo de lectura caracteres ÷ 15; nunca después del corte de escena; si no alcanza, no va),
               no dicho (oración ancla ± 1) y spoiler (oraciones posteriores del cap) (§A.3), coherencia de cifras con
               la voz de todo el video (§A.4).
    finalizar  (§A.1) por beat queda 1 (`a_pantalla` primero, después `rank`); el beat pico, 0.
    colocar    cifra, hecho, persona → ficha (el title card sin #tc-dim: kicker = etiqueta, título = dato); documento →
               archive_clipping; cita → quote_card; lupa → evidence_zoom con la caja de visión del detalle.
    escena     (§0/§A.5, después del reloj y el sello) una cosa por escena: la ficha espera a la escena siguiente del
               beat si en la suya hay title card, reloj, sello u otro bloque; el reloj (animación) no va encima de un
               texto ni en el beat de otra animación.
Lecturas declaradas (F29b_REPORT y F29c_REPORT). Sin escaleta o con el flag apagado no corre nada de esto.
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

PROMPT_VERSION = "f29c-1"
MODELO_DEFAULT = "claude-sonnet-5-5"
EFFORT_DEFAULT = "medium"
TIPOS = ("cifra", "hecho", "documento", "cita", "persona", "lupa")
FICHA = ("cifra", "hecho", "persona")              # §A.5: salen en la ficha (= title card)
CON_ETIQUETA = ("cifra", "hecho", "documento", "persona")
LECTURA_CPS = 15.0             # §0: mínimo de lectura = caracteres ÷ 15 cps (estándar de subtitulado, el más lento)
OUT_TOKENS_PEOR = 16_000       # peor caso de salida para el tope (razonamiento + JSON)
REGLAS_REINTENTO = ("anclaje", "forma", "candado", "no_dicho", "spoiler", "coherencia")

# ═══════════════════════ prompt (HANDOFF_F29c §A.5, literal) ═══════════════════════

ROTULISTA_SYSTEM = """Sos el rotulista de un documental de historia oscura en español. Recibís la narración de un capítulo, oración por oración, con tiempos y con la palabra numerada, y una lista de datos verificados (citas, cifras, hechos, documentos) con su texto fuente. Decidís qué va escrito en pantalla, en qué palabra de qué oración aparece, de qué tipo es y con qué palabras.

Un texto en pantalla vale solo si cumple las tres a la vez:
(a) dice algo que la narración NO dice en este capítulo;
(b) es sobre lo que la narración cuenta en esa oración exacta;
(c) no adelanta nada que la narración diga después.
Si para una oración no hay ningún dato que cumpla las tres, no va nada. La pantalla vacía es correcta. Nunca repitas ni parafrasees la oración ancla ni la anterior ni la siguiente.

Cada capítulo está dividido en beats. En cada beat puede ir como máximo UN texto; en el beat marcado como pico no va ninguno; en el gancho, a lo sumo uno. Proponé por beat los candidatos que cumplan (a)(b)(c) y ordenalos con `rank` (1 = el que más aporta); los datos marcados `a_pantalla` van siempre con rank 1 en su beat y con lo que pide su `por_que`. El código se queda con uno por beat.

Tipos y su compuerta (solo cuando la narración, en esa oración, habla de eso):
- cifra: la narración habla de esa magnitud. Lleva etiqueta obligatoria (qué es la cifra) y el valor. No uses una cifra que contradiga otra cifra que la narración diga en cualquier parte del video.
- hecho: la narración cuenta ese hecho; aportás el quién, el cargo, la fecha, lo que dice el acta. Lleva etiqueta corta (la fuente o el documento, con año).
- documento: una carta, un acta, un informe que la narración menciona o cuyo momento está contando. Sale como recorte: kicker = nombre real del documento con año; titular = lo esencial en una línea, redactado (no es cita literal).
- cita: la narración nombra a esa persona o lee de ella; texto literal del dato, con el autor.
- persona: la narración nombra a alguien por primera vez en el capítulo; etiqueta = cargo, texto = nombre, tal como están en el dato.
- lupa: la narración nombra un detalle chico que está en la imagen (fisura, firma, fecha en un papel); nunca el sujeto de la foto. Texto = qué se señala.

Escritura: una línea de etiqueta y una o dos líneas de dato; oración completa o etiqueta + valor; nunca un fragmento sin sujeto o sin el valor. Para citas, copiá el dato literal. Para el resto, redactá, pero cada número, nombre propio, fecha y cantidad tiene que estar en el texto fuente de ese dato; si el dato no trae el valor, no va.

Para cada bloque devolvé: `sentence_idx`, `word_idx` (la palabra de esa oración que el dato responde: la narración dice «murió» y el bloque pone el nombre; dice «aprobó» y el bloque pone el acta), `beat`, `rank`, `tipo`, `etiqueta`, `texto`, `pool_id` y una línea `aporta` que diga qué dice que la narración no dice. Si no podés escribir `aporta` con algo concreto, el bloque no va.

Respondé SOLO con un objeto JSON, sin texto antes ni después."""

ROTULISTA_USER = """CAPÍTULO {cap} — {titulo}

NARRACIÓN (oración por oración; cada palabra con su índice):
{oraciones: "[idx] t0–t1 · beat N · texto con palabras numeradas: 0:En 1:marzo 2:de …"}

BEATS DEL CAPÍTULO (n, función, ventana en segundos, cierre); el pico es el beat {pico_beat}:
{beats}

DATOS DISPONIBLES (solo estos; cada uno con su texto fuente):
{items: "- id · tipo Q/D/T · a_pantalla: sí/no · por_que: … · fuente: … · texto fuente: «…»"}

YA MOSTRADO EN CAPÍTULOS ANTERIORES (no repetir):
{ya_mostrado}

Devolvé:
{"bloques": [{"sentence_idx": int, "word_idx": int, "beat": int, "rank": int, "tipo": "cifra|hecho|documento|cita|persona|lupa", "etiqueta": str, "texto": str, "pool_id": str, "aporta": str}], "descartados": [{"pool_id": str, "motivo": str}]}"""

_HUECOS = ("{cap}", "{titulo}",
           '{oraciones: "[idx] t0–t1 · beat N · texto con palabras numeradas: 0:En 1:marzo 2:de …"}',
           "{pico_beat}", "{beats}",
           '{items: "- id · tipo Q/D/T · a_pantalla: sí/no · por_que: … · fuente: … · texto fuente: «…»"}',
           "{ya_mostrado}")

PROMPT_VERSION_F29B = "f29b-1"     # el de F29b queda para la historia (md5 50e6ae74…): F29b_REPORT


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
    """Nombres propios: tokens con mayúscula inicial que no abren el texto ni una oración (tras . : ! ? «). Un texto todo
    en mayúsculas («ANCHO DE LA FISURA») no dice qué es nombre: no devuelve nada."""
    if texto and texto.upper() == texto and re.search(r"[A-ZÁÉÍÓÚÑ]{2}", texto):
        return []
    out = []
    for m in re.finditer(r"[A-ZÁÉÍÓÚÑÜ][\wáéíóúñü'’-]*", texto or ""):
        antes = (texto[:m.start()]).rstrip()
        if not antes or antes[-1] in ".:!?¿¡«\"“(·":
            continue
        if len(m.group(0)) < 2:
            continue
        out.append(m.group(0))
    return list(dict.fromkeys(out))


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


_PARTICULAS = {"de", "del", "da", "dal", "della", "di", "van", "von", "la", "le", "y"}


def nombre_inicial(texto: str) -> set[str]:
    """Los tokens del nombre con que abre un bloque («Giorgio Dal Piaz, geólogo» → Giorgio, Dal, Piaz)."""
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


def palabras_de_contenido(texto: str) -> list[str]:
    """Las palabras de contenido (≥ 4 letras, sin artículos ni preposiciones): el cargo de una persona."""
    ws = [re.sub(r"[^\wáéíóúñü'’-]", "", w) for w in palabras(texto)]
    return [w for w in ws if len(w) >= 4 and ev.norm(w) not in _ARTPREP and ev.norm(w) not in ev._FUNC]


# ═══════════════════════ coherencia de cifras (§A.4) ═══════════════════════

_UNIDAD_1 = {"m": "m", "metro": "m", "metros": "m", "m³": "m3", "m3": "m3", "km": "km", "kilometro": "km",
             "kilometros": "km", "cm": "cm", "centimetro": "cm", "centimetros": "cm", "persona": "personas",
             "personas": "personas", "muertos": "personas", "victimas": "personas", "habitantes": "personas",
             "lira": "liras", "liras": "liras", "%": "%"}
_UNIDAD_2 = {("metros", "cubicos"): "m3", ("metro", "cubico"): "m3", ("por", "ciento"): "%"}
# §A.4: «la misma magnitud nombrada en la oración (nivel, cota, altura, muertos)»; nivel y cota son la misma
_MAGNITUD = {"nivel": ("nivel", "cota"), "altura": ("altura",), "muertos": ("muert", "muri")}
_DIFERENCIA = {("por", "encima"), ("por", "debajo"), ("mas", "que"), ("menos", "que")}


def _toks(texto: str) -> list[str]:
    return re.findall(r"\d[\d.,]*\d|\d|%|[^\W\d_]+", ev.norm(texto or ""))


def _num_tok(tok: str) -> float | None:
    from script_engine.num_es import parse_int
    if not _DIG.fullmatch(tok):
        return None
    n = parse_int(tok)
    if n is not None:
        return float(n)
    try:
        return float(tok.replace(".", "").replace(",", "."))
    except ValueError:
        return None


def _num_en(toks: list[str], i: int) -> tuple[float | None, int]:
    """El número que arranca en toks[i] (dígitos o letras, con «mil»/«millones» detrás) y dónde termina."""
    v = _num_tok(toks[i])
    j = i + 1
    if v is None:
        if not _NUMW.match(toks[i]) or toks[i] in ("y", "mil", "millon", "millones"):
            return None, i + 1
        e = i
        while e < len(toks) and _NUMW.match(toks[e]):
            e += 1
        for k in range(e, i, -1):
            s = " ".join(toks[i:k])
            if s in _w2n() and not (k - i == 1 and toks[i] in ("un", "una", "uno")):
                v, j = float(_w2n()[s]), k
                break
        if v is None:
            return None, i + 1
    while j < len(toks) and toks[j] in ("mil", "millon", "millones"):
        v *= 1000.0 if toks[j] == "mil" else 1e6
        j += 1
    return v, j


def _analiza(texto: str) -> tuple[list[tuple[float, str | None, int]], list[tuple[str, int]]]:
    """(cifras [(valor, unidad, posición)], magnitudes [(magnitud, posición)]) de un texto."""
    toks = _toks(texto)
    nums: list[tuple[float, str | None, int]] = []
    i = 0
    while i < len(toks):
        v, j = _num_en(toks, i)
        if v is None:
            i = j
            continue
        k = j + (1 if j < len(toks) and toks[j] == "de" else 0)
        u2 = _UNIDAD_2.get(tuple(toks[k:k + 2]))
        u = u2 or _UNIDAD_1.get(toks[k] if k < len(toks) else "")
        e = k + (2 if u2 else 1 if u else 0)
        if tuple(toks[e:e + 2]) in _DIFERENCIA:          # «15 metros por encima de la cota»: una diferencia, no la cota
            u = "diferencia"
        nums.append((v, u, i))
        i = j
    mags = [(m, p) for p, t in enumerate(toks) for m, raices in _MAGNITUD.items() if any(t.startswith(r) for r in raices)]
    return nums, mags


def _fmt(v: float) -> str:
    return str(int(v)) if float(v).is_integer() else str(v)


def contradicciones(bloque: str, voz: list[str]) -> list[str]:
    """§A.4: cada cifra del bloque con unidad contra las cifras de la voz de todo el video. Lectura declarada de «misma
    unidad o misma magnitud nombrada en la oración»: la cifra de la voz se compara si (1) tiene la misma unidad y la
    oración nombra la misma magnitud que el bloque («setecientos metros sobre el nivel del mar» contra «Nivel del
    embalse: 720 m»); o (2) no tiene unidad pero viene después de la magnitud del bloque en su oración («la cota
    autorizada fue de setecientos quince»). La misma unidad sola no alcanza («ola de veinte metros» no es la cota; la
    oferta de ENEL en liras no es la condena a Montedison), y una diferencia («15 metros por encima de la cota») no se
    compara con la cota."""
    nb, mb = _analiza(bloque)
    mags_b = {m for m, _ in mb}
    out = []
    for v, u, _ in nb:
        if u is None or u == "diferencia":
            continue
        for s in voz:
            ns, ms = _analiza(s)
            mags_s = {m for m, _ in ms}
            for w, uw, p in ns:
                misma = (uw == u and bool(mags_b & mags_s)) or \
                        (uw is None and any(m in mags_b and q < p for m, q in ms))
                if misma and abs(w - v) > 1e-9:
                    out.append(f"{_fmt(v)} {u} vs {_fmt(w)}{' ' + uw if uw else ''} («{s.strip()[:70]}»)")
    return list(dict.fromkeys(out))


# ═══════════════════════ entrada ═══════════════════════

def oraciones(words: list[dict], time_offset: float = 0.0) -> list[dict[str, Any]]:
    """Las oraciones de la voz (gfx_peak.sentences) con cada palabra numerada dentro de su oración y sus tiempos."""
    from script_engine.gfx_peak import sentences
    out = []
    for k, s in enumerate(sentences(words, time_offset)):
        pal = [{"k": j, "w": str(words[i]["word"]).strip(), "t0": round(float(words[i]["start"]) + time_offset, 3),
                "t1": round(float(words[i]["end"]) + time_offset, 3)} for j, i in enumerate(s["idx"])]
        out.append({"idx": k, "t0": round(s["t0"], 3), "t1": round(s["t1"], 3), "texto": s["text"], "palabras": pal})
    return out


def beat_de_oracion(s: dict, beats: list[dict]) -> int | None:
    """El beat de una oración: el que contiene su inicio (con la tolerancia de pico_cap); si cae entre beats, el último
    que ya empezó."""
    for b in beats:
        if b["t0"] - 0.3 <= s["t0"] <= b["t1"]:
            return b["n"]
    prev = [b for b in beats if b["t0"] <= s["t0"]]
    return (prev[-1] if prev else beats[0])["n"] if beats else None


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


def voz_del_video(ctx: dict[str, Any]) -> list[str]:
    """§A.4: la voz de los 7 caps, oración por oración (el texto de la narración: el mismo que los subtítulos remapeados
    del sync map)."""
    out = []
    for c in sorted(ctx.get("chapters") or [], key=lambda c: int(c.get("chapter_number") or 0)):
        out += [s for s in re.split(r"(?<=[.!?…])\s+", str(c.get("narration") or "").strip()) if s.strip()]
    return out


def entrada(cap: int, real: dict, escaleta: dict, pool: dict | None, words: list[dict], time_offset: float,
            titulo: str | None = None, voz_video: list[str] | None = None, pre_roll: float = 0.0) -> dict[str, Any]:
    """La entrada del rotulista de un cap. `pre_roll` (F30b §B.3): los segundos de title card sin voz que el cap tiene
    adelante; los tiempos quedan en el tiempo del plan (con el pre-roll) y el pedido los imprime sin él, así el prompt
    (y su caché) es el mismo con o sin pre-roll."""
    sents = oraciones(words, time_offset)
    beats = real["beats"]
    for s in sents:
        s["beat"] = beat_de_oracion(s, beats)
    its = items_cap(cap, escaleta, beats, pool)
    pk = pico_cap(cap, escaleta, beats, sents, pool)
    tit = titulo or " · ".join(dict.fromkeys(b["funcion"] for b in beats))
    return {"cap": cap, "titulo": tit, "oraciones": sents,
            "beats": [{k: b[k] for k in ("n", "funcion", "t0", "t1", "cierre", "dato_central", "datos_apoyo")}
                      for b in beats],
            "items": its, "ya_mostrado": ya_mostrado(cap, escaleta, pool), "pico": pk,
            "voz_video": list(voz_video or []), "pre_roll": round(float(pre_roll), 3)}


def prompt_user(ent: dict[str, Any]) -> str:
    def item_line(x: dict) -> str:
        fuente = x["fuente"] or "—"
        if x["kind"] == "citas" and x["autor"]:
            fuente += f" (autor: {x['autor']})"
        return (f"- {x['id']} · tipo {x['tipo']} · a_pantalla: {'sí' if x['a_pantalla'] else 'no'} · por_que: "
                f"{x['por_que'] or '—'} · fuente: {fuente} · texto fuente: «{x['texto']}»")

    def or_line(s: dict) -> str:
        pal = s.get("palabras") or [{"k": j, "w": w} for j, w in enumerate(palabras(s["texto"]))]
        return (f"[{s['idx']}] {round(s['t0'] - pr, 3):.1f}–{round(s['t1'] - pr, 3):.1f} · beat {s.get('beat', '—')} · "
                + " ".join(f"{p['k']}:{p['w']}" for p in pal))
    pr = float(ent.get("pre_roll") or 0.0)
    pk = ent["pico"] or {"beat": "—"}
    vals = (str(ent["cap"]), ent["titulo"],
            "\n".join(or_line(s) for s in ent["oraciones"]),
            str(pk["beat"]),
            "\n".join(f"- {b['n']} · {b['funcion']} · {round(b['t0'] - pr, 3):.1f}–{round(b['t1'] - pr, 3):.1f} s · cierre: «{b['cierre'] or '—'}»"
                      for b in ent["beats"]),
            "\n".join(item_line(x) for x in ent["items"]) or "(ninguno)",
            "\n".join(f"- {x['id']} «{x['texto']}»" for x in ent["ya_mostrado"]) or "(nada)")
    out = ROTULISTA_USER
    for h, v in zip(_HUECOS, vals):
        out = out.replace(h, v)
    return out


# ═══════════════════════ validar ═══════════════════════

def _escena_de(escenas: list[Any] | None, t: float) -> Any | None:
    if not escenas:
        return None
    for s in escenas:
        if s.start <= t < s.end:
            return s
    return escenas[-1]


def tiempos(sents: list[dict], si: int, t0: float, chars: int, escenas: list[Any] | None = None
            ) -> tuple[float, str | None]:
    """§A.2: (t1, motivo si no va). t1 = fin de la oración ancla; si no alcanza el mínimo de lectura (caracteres ÷ 15),
    el fin de la oración siguiente; nunca después del corte de la escena que contiene t0."""
    need = chars / LECTURA_CPS
    t1 = sents[si]["t1"]
    if t1 - t0 < need and si + 1 < len(sents):
        t1 = sents[si + 1]["t1"]
    sc = _escena_de(escenas, t0)
    if sc is not None:
        t1 = min(t1, sc.end)
    t1 = round(t1, 3)
    if t1 - t0 < need:
        return t1, (f"sin tiempo de lectura: {chars} caracteres piden {need:.1f} s y hay {t1 - t0:.1f} s"
                    + (f" hasta el corte de escena ({sc.end:.1f} s)" if sc is not None and t1 == round(sc.end, 3) else ""))
    return t1, None


def caracteres(tipo: str, etiqueta: str | None, texto: str, autor: str = "") -> int:
    """Lo que se lee del bloque: etiqueta + dato (la cita, con su autor)."""
    return len(etiqueta or "") + len(texto) + (len(autor) if tipo == "cita" else 0)


def validar(resp: Any, ent: dict[str, Any], words: list[dict], time_offset: float = 0.0,
            escenas: list[Any] | None = None) -> dict[str, Any]:
    """{bloques, rechazos, faltan, motivo_faltan, incompletos}: los bloques que pasan las reglas y la cantidad por beat
    (con t0, t1, dur, beat, pantalla), cada uno que sale con su regla y su motivo, y los `a_pantalla` que no salieron.
    Sin `escenas` (prefetch) el fin no se corta en la escena: eso lo hace `colocar`."""
    its = {x["id"]: x for x in ent["items"]}
    sents = oraciones(words, time_offset)
    beats = ent["beats"]
    for s in sents:
        s["beat"] = beat_de_oracion(s, beats)
    funcion = {b["n"]: b["funcion"] for b in beats}
    pk_beat = (ent.get("pico") or {}).get("beat")
    voz_video = ent.get("voz_video") or [s["texto"] for s in sents]
    ok, rech = [], []

    def fuera(b: dict, regla: str, motivo: str) -> None:
        rech.append({"pool_id": b.get("pool_id"), "tipo": b.get("tipo"), "etiqueta": b.get("etiqueta"),
                     "texto": b.get("texto"), "sentence_idx": b.get("sentence_idx"), "regla": regla, "motivo": motivo})
    bl = (resp or {}).get("bloques") if isinstance(resp, dict) else None
    for b in bl if isinstance(bl, list) else []:
        if not isinstance(b, dict):
            continue
        b = dict(b)
        pid = str(b.get("pool_id") or "")
        x = its.get(pid)
        if x is None:
            fuera(b, "anclaje", f"pool_id {pid!r} no está en los datos del cap")
            continue
        try:
            si = int(b.get("sentence_idx"))
        except (TypeError, ValueError):
            si = -1
        if not 0 <= si < len(sents):
            fuera(b, "anclaje", f"sentence_idx {b.get('sentence_idx')!r} no existe")
            continue
        s = sents[si]
        movido = None
        if pk_beat is not None and s["beat"] == pk_beat and x["a_pantalla"]:     # §A.1: al beat siguiente si se puede
            nxt = next((bb["n"] for bb in beats if bb["n"] > pk_beat), None)
            s2 = next((ss for ss in sents if ss["beat"] == nxt), None) if nxt in x["beats"] else None
            if s2 is not None:
                movido = f"del beat pico {pk_beat} (oración [{si}]) al beat {nxt} (oración [{s2['idx']}], palabra 0)"
                si, s, b["word_idx"] = s2["idx"], s2, 0
        try:
            wi = int(b.get("word_idx"))
        except (TypeError, ValueError):
            wi = -1
        if not 0 <= wi < len(s["palabras"]):
            fuera(b, "anclaje", f"word_idx {b.get('word_idx')!r} no existe en la oración [{si}]")
            continue
        if s["beat"] not in x["beats"]:
            fuera(b, "anclaje", f"la oración [{si}] es del beat {s['beat']} y {pid} es del beat {x['beats']}")
            continue
        tipo = str(b.get("tipo") or "").strip().lower()
        if tipo not in TIPOS:
            fuera(b, "forma", f"tipo {tipo!r} no válido")
            continue
        b["tipo"] = tipo
        txt = re.sub(r"\s+", " ", str(b.get("texto") or "")).strip()
        if tipo == "cita":
            txt = re.sub(r"^[«\"“]+|[»\"”]+$", "", txt).strip()
        et = re.sub(r"\s+", " ", str(b.get("etiqueta") or "")).strip() or None
        b["texto"], b["etiqueta"] = txt, et
        if not txt:
            fuera(b, "forma", "texto vacío")
            continue
        if tipo in CON_ETIQUETA and not et:
            fuera(b, "forma", f"{tipo} sin etiqueta")
            continue
        if tipo == "cifra" and not numeros(txt):
            fuera(b, "forma", "cifra sin el valor")
            continue
        if tipo != "lupa" and munon(txt):
            fuera(b, "forma", "fragmento cortado (empieza en minúscula o termina en preposición/artículo)")
            continue
        if not str(b.get("aporta") or "").strip():
            fuera(b, "forma", "sin `aporta`")
            continue
        if tipo in FICHA:
            from script_engine.gfx_project import ficha_medida
            m = ficha_medida(et or "", txt)
            if m["kicker"] > 1 or m["title"] > 2:
                fuera(b, "forma", f"no cabe en la ficha: etiqueta en {m['kicker']} línea(s), dato en {m['title']} (1 y 2)")
                continue
        # candado (F29b A.4.3)
        fuente = x["texto"]
        if tipo == "cita":
            if ev.norm(txt.strip("…").strip()) not in ev.norm(fuente):
                fuera(b, "candado", "la cita no es literal del texto fuente")
                continue
        else:
            malos = [n for n in numeros(txt) if not numero_en(n, fuente)]
            malos += [n for n in nombres(txt) if not _palabra_en(n, fuente)]
            if tipo == "persona":              # el nombre (abre el texto: nombres() no lo mira) y el cargo (etiqueta)
                malos += [n for n in nombre_inicial(txt) if n.lower() not in _PARTICULAS and not _palabra_en(n, fuente)]
                malos += [w for w in palabras_de_contenido(et or "") if not _raiz_en(w, fuente)]
            elif et:                           # la etiqueta sale del texto o de la fuente del dato
                ff = fuente + " " + x["fuente"]
                malos += [n for n in numeros(et) + nombres(et) if not (numero_en(n, ff) or _palabra_en(n, ff))]
            if malos:
                fuera(b, "candado", f"no están en el texto fuente de {pid}: {sorted(set(malos))}")
                continue
        # §A.2 tiempos
        t0 = s["palabras"][wi]["t0"]
        chars = caracteres(tipo, et, txt, x["autor"])
        t1, sin_t = tiempos(sents, si, t0, chars, escenas)
        if sin_t:
            fuera(b, "lectura", sin_t)
            continue
        # §A.3 no dicho (oración ancla ± 1) y spoiler (oraciones posteriores del cap), sobre el dato
        vecinas = " ".join(ss["texto"] for ss in sents[max(0, si - 1):si + 2])
        despues = " ".join(ss["texto"] for ss in sents[si + 1:])
        antes = " ".join(ss["texto"] for ss in sents[:si + 1])
        nums = numeros(txt)
        exento = nombre_inicial(txt) if tipo == "persona" else set()     # el nombre de la persona (lo dice la voz)
        nms = [n for n in nombres(txt) if n not in exento]
        dichos = [n for n in nums if numero_en(n, vecinas)] + [n for n in nms if _palabra_en(n, vecinas)]
        if dichos:
            fuera(b, "no_dicho", f"la voz lo dice en la oración ancla o en una vecina: {dichos}")
            continue
        spoil = [n for n in nums if numero_en(n, despues)] + \
                [n for n in nms if _palabra_en(n, despues) and not _palabra_en(n, antes)]
        if spoil:
            fuera(b, "spoiler", f"la voz lo dice en una oración posterior del cap: {spoil}")
            continue
        # §A.4 coherencia con la voz de todo el video
        contra = contradicciones(f"{et or ''} {txt}", voz_video)
        if contra:
            fuera(b, "coherencia", "contradice la voz: " + "; ".join(contra[:3]))
            continue
        try:
            rank = int(b.get("rank"))
        except (TypeError, ValueError):
            rank = len(bl) + 1                     # sin rank: después de todos los que lo traen
        ok.append({**b, "sentence_idx": si, "word_idx": wi, "palabra": s["palabras"][wi]["w"], "t0": t0, "t1": t1,
                   "dur": round(t1 - t0, 3), "beat": s["beat"], "funcion": funcion.get(s["beat"], ""), "rank": rank,
                   "pantalla": txt, "etiqueta": et, "a_pantalla": x["a_pantalla"], "por_que": x["por_que"],
                   "caracteres": chars, "lectura_s": round(chars / LECTURA_CPS, 2), "movido": movido})
    keep, rech_c = finalizar(ok, pk_beat)
    rech += rech_c
    salen = {b["pool_id"]: b for b in keep}
    faltan = [x["id"] for x in ent["items"] if x["a_pantalla"] and x["id"] not in salen]
    motivo_faltan = {}
    for i in faltan:
        r = [f"{r['regla']}: {r['motivo']}" for r in rech if r["pool_id"] == i]
        motivo_faltan[i] = r[-1] if r else "el rotulista no lo propuso"
    incompletos = {}
    for x in ent["items"]:
        if x["a_pantalla"] and x["id"] in salen:
            b = salen[x["id"]]
            falta = lo_que_pide(x["por_que"], x["texto"], f"{b['etiqueta'] or ''} {b['pantalla']}")
            if falta:
                incompletos[x["id"]] = falta
    return {"bloques": keep, "rechazos": rech, "faltan": faltan, "motivo_faltan": motivo_faltan,
            "incompletos": incompletos}


def finalizar(validos: list[dict[str, Any]], pico_beat: Any) -> tuple[list[dict], list[dict]]:
    """§A.1: por beat queda 1 (`a_pantalla` primero, después `rank`, después la oración); el beat pico, 0; el mismo dato
    una sola vez. Devuelve (los que quedan, en orden de t0; los que salen por cantidad)."""
    keep, rech, vistos, por_beat = [], [], set(), {}
    for b in sorted(validos, key=lambda b: (not b["a_pantalla"], b["rank"], b["sentence_idx"])):
        motivo = ("el mismo dato dos veces" if b["pool_id"] in vistos else
                  f"beat pico ({b['beat']}): 0 textos" if pico_beat is not None and b["beat"] == pico_beat else
                  f"un texto por beat: el beat {b['beat']} ya tiene {por_beat[b['beat']]}" if b["beat"] in por_beat
                  else None)
        if motivo:
            rech.append({"pool_id": b["pool_id"], "tipo": b["tipo"], "etiqueta": b["etiqueta"], "texto": b["pantalla"],
                         "sentence_idx": b["sentence_idx"], "regla": "cantidad", "motivo": motivo})
            continue
        keep.append(b)
        vistos.add(b["pool_id"])
        por_beat[b["beat"]] = b["pool_id"]
    return sorted(keep, key=lambda b: b["t0"]), rech


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


def primer_json(txt: str) -> dict | None:
    """§A.6.1: el primer objeto JSON válido del texto (lo que haya antes o después se ignora); None si no hay ninguno."""
    dec = json.JSONDecoder()
    for m in re.finditer(r"\{", txt or ""):
        try:
            obj, _ = dec.raw_decode(txt, m.start())
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            return obj
    return None


def _solo_el_json(r: dict) -> dict:
    """La respuesta de la API con el texto reemplazado por su primer objeto JSON válido (si hay uno): claude_helpers
    parsea eso y no vuelve a pedir por un texto de más antes o después."""
    txt = "".join(b.get("text") or "" for b in r.get("content") or [] if b.get("type") == "text")
    obj = primer_json(txt)
    if obj is None:
        return r
    return {**r, "content": [{"type": "text", "text": json.dumps(obj, ensure_ascii=False)}]}


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
        return _solo_el_json(r)
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
        prev["validacion"] = validar(prev["final"], ent, words, time_offset)   # determinista: con el código de hoy
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
        except Exception as e:  # noqa: BLE001 — sin ningún JSON tras los reintentos de claude_helpers o la API caída
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
        de_contenido = [r for r in val["rechazos"] if r["regla"] in REGLAS_REINTENTO]
        if de_contenido and not usados["forma"]:
            usados["forma"] = True
            errores += [f"{r['pool_id']} en la oración [{r['sentence_idx']}] «{r['texto']}»: {r['motivo']}"
                        for r in de_contenido]
        no_propuestos = [i for i in val["faltan"]
                         if not any(r["pool_id"] == i and r["regla"] in ("cantidad", "lectura") for r in val["rechazos"])]
        if (no_propuestos or val["incompletos"]) and not usados["a_pantalla"]:
            usados["a_pantalla"] = True
            pq = {x["id"]: x["por_que"] for x in ent["items"]}
            errores += [f"falta el dato a_pantalla {i} (por_que: {pq.get(i)})" for i in no_propuestos]
            errores += [f"el dato a_pantalla {i} salió sin {f} (por_que: {pq.get(i)})"
                        for i, f in val["incompletos"].items()]
        if not errores:
            break
        pedido = _reintento(user, errores)
    v = out["validacion"]
    if v is not None:
        log.append(f"  rotulista {cap_id}: {len(out['intentos'])} intento(s) · {len(v['bloques'])} bloque(s) · "
                   f"{len(v['rechazos'])} fuera · a_pantalla que faltan {v['motivo_faltan']} · incompletos {v['incompletos']}")
    raw_f.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


# ═══════════════════════ colocar ═══════════════════════

KIND_FICHA = {"cifra": "figure", "persona": "name", "hecho": "fact"}


def colocar(plan: dict[str, Any], res: dict[str, Any], ent: dict[str, Any], *, scenes: list[Any], pool: dict | None,
            used_before: set[str], lupa_box: Callable[[int, str], tuple[list[float], str] | None] | None,
            zoom_dur: float, log: list[str], words: list[dict] | None = None, time_offset: float = 0.0
            ) -> list[dict[str, Any]]:
    """Los bloques del rotulista en el plan (reemplazan recortes, datos, cita, contador, nivel de agua y el zoom del
    director). Con `words`, la validación se rehace con las escenas reales (el fin muere en el corte). Devuelve una fila
    por bloque (colocado o fuera, con la regla y el motivo)."""
    from script_engine.gfx_pool import short_source
    from script_engine.gfx_project import scene_at
    its = ev.items(pool) if pool else {}
    viejos = {k: plan.get(k) for k in ("archive_clippings", "callouts", "quote_card", "count_up", "water_level",
                                       "evidence_zoom")}
    plan["archive_clippings"], plan["callouts"] = [], []
    for k in ("quote_card", "count_up", "water_level", "evidence_zoom"):
        plan[k] = None
    filas: list[dict[str, Any]] = []
    if words is not None and res.get("final") is not None:
        v = validar(res["final"], ent, words, time_offset, escenas=scenes)
    else:
        v = res.get("validacion") or {"bloques": [], "rechazos": [], "faltan": []}
    for r in v["rechazos"]:
        filas.append({**r, "accion": "fuera"})
    for b in v["bloques"]:
        pid, t0, dur = b["pool_id"], b["t0"], b["dur"]
        it = its.get(pid) or {}
        sc = scene_at(scenes, t0)
        side = getattr(sc, "quiet_side", "right") or "right"
        meta = {"pool_id": pid, "rotulista": True, "beat": b["beat"], "sentence_idx": b["sentence_idx"],
                "word_idx": b["word_idx"], "aporta": b.get("aporta"), "tipo_rotulista": b["tipo"],
                "a_pantalla": b["a_pantalla"], "por_que": b.get("por_que") or "", "t1": b["t1"],
                "lectura_s": b["lectura_s"], "movido": b.get("movido")}
        fila = {"pool_id": pid, "tipo": b["tipo"], "etiqueta": b["etiqueta"], "texto": b["pantalla"],
                "sentence_idx": b["sentence_idx"], "word_idx": b["word_idx"], "palabra": b.get("palabra"), "t0": t0,
                "t1": b["t1"], "aporta": b.get("aporta"), "beat": b["beat"], "a_pantalla": b["a_pantalla"],
                "movido": b.get("movido")}
        if pid in used_before:
            filas.append({**fila, "accion": "fuera", "regla": "ya_mostrado", "motivo": "ya se mostró en un cap anterior"})
            continue
        if b["tipo"] in FICHA:
            plan["callouts"].append({"text": b["pantalla"], "kicker": b["etiqueta"] or "", "ficha": True, "start": t0,
                                     "kind": KIND_FICHA[b["tipo"]], "duration": dur, "side": "left", "fact_idx": None,
                                     **meta})
        elif b["tipo"] == "documento":
            plan["archive_clippings"].append({"kicker": b["etiqueta"] or short_source(it.get("fuente")),
                                              "headline": b["pantalla"], "body": "", "scene_idx": sc.idx,
                                              "fact_idx": None, "fuente": it.get("fuente"), "era_decade": 2000,
                                              "start": t0, "duration": dur, "side": side, **meta})
        elif b["tipo"] == "cita":
            if not it.get("autor"):
                filas.append({**fila, "accion": "fuera", "regla": "zona", "motivo": "la cita no tiene autor"})
                continue
            plan["quote_card"] = {"text": b["pantalla"], "author": it["autor"], "start": t0, "duration": dur, **meta}
        elif b["tipo"] == "lupa":
            got = lupa_box(sc.idx, b["pantalla"]) if lupa_box else None
            if got is None:
                filas.append({**fila, "accion": "fuera", "regla": "zona",
                              "motivo": f"visión no encuentra «{b['pantalla']}» en la escena {sc.idx}"})
                continue
            if sc.end - t0 < zoom_dur:
                filas.append({**fila, "accion": "fuera", "regla": "lectura",
                              "motivo": f"la escena termina {sc.end - t0:.1f} s después (el zoom pide {zoom_dur:.1f})"})
                continue
            box, label = got
            plan["evidence_zoom"] = {"scene_idx": sc.idx, "box": box, "start": t0, "anchor": label, "detail": label,
                                     "como": "rotulista", **meta}
        filas.append({**fila, "accion": "colocado"})
    plan["callouts"].sort(key=lambda c: c["start"])
    plan["archive_clippings"].sort(key=lambda c: c["start"])
    plan["rotulista"] = {"modelo": res.get("modelo"), "faltan_a_pantalla": v.get("faltan"),
                         "motivo_faltan": v.get("motivo_faltan") or {},
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


# ═══════════════════════ escena (§0 animaciones, §A.5 zona de la ficha) ═══════════════════════

def _sello_queda(e: dict, plan: dict) -> bool:
    """El sello que sobrevive al realizador (solo el de la palabra del pico)."""
    pw = str((plan.get("pico") or {}).get("word") or "").lower().strip(".,;:")
    return bool(e.get("peak_word")) or (bool(pw) and str(e.get("word", "")).lower().strip(".,;:") == pw)


def escena_final(plan: dict[str, Any], scenes: list[Any], ent: dict[str, Any], log: list[str]) -> list[dict[str, Any]]:
    """Una cosa por escena (después del reloj y del sello, antes del realizador y del crítico):
    - fijos: el title card (su escena) y el sello del pico;
    - los textos que no son ficha (documento, cita, lupa), por prioridad (`a_pantalla`, después t0): si su escena ya
      tiene otra cosa, el documento y la cita esperan a la escena siguiente del beat (la lupa no: su detalle está en esa
      foto) o no van;
    - el reloj (animación): nunca encima de un texto que no sea ficha ni en la escena del sello; uno por beat (si su
      beat tiene sello o lupa, no va); si choca, arranca en la escena siguiente de su beat (sin pasar un cambio de fecha
      y con ≥ TICKER_MIN en pantalla) o no va;
    - las fichas (§A.5): si en su escena hay title card, reloj, sello u otro bloque, esperan a la escena siguiente del
      beat o no van.
    Al moverse, un bloque arranca en el corte de la escena nueva y su fin se recalcula con §A.2. Devuelve las filas."""
    from gfx_config import gfx_rules
    from script_engine.gfx_pool import TICKER_MIN
    from script_engine.gfx_project import scene_at
    filas: list[dict[str, Any]] = []
    if not scenes:
        return filas
    sents = ent["oraciones"]
    beats = ent["beats"]

    def beat_en(t: float) -> dict | None:
        for b in beats:
            if b["t0"] - 0.3 <= t <= b["t1"]:
                return b
        prev = [b for b in beats if b["t0"] <= t]
        return prev[-1] if prev else (beats[0] if beats else None)

    def escenas_del_beat_desde(sc: Any, b: dict | None) -> list[Any]:
        return [s for s in scenes if s.start > sc.start and b is not None and b["t0"] - 0.3 <= s.start <= b["t1"]]

    def oracion_en(t: float) -> int:
        k = next((s["idx"] for s in sents if s["t0"] <= t <= s["t1"]), None)
        return k if k is not None else next((s["idx"] for s in sents if s["t0"] >= t), len(sents) - 1)

    ocupa: dict[int, list[str]] = {}

    def marca(si: int, que: str) -> None:
        ocupa.setdefault(si, []).append(que)

    if plan.get("title_card"):
        for s in scenes:                       # todas las escenas que pisa el title card (dura title_dur)
            if s.start < gfx_rules.title_dur:
                marca(s.idx, "title card")
    for e in plan.get("emphasis") or []:
        if _sello_queda(e, plan):
            marca(scene_at(scenes, float(e["start"])).idx, "sello")

    def mover(b: dict, desde: Any, libre: Callable[[Any], bool]) -> str | None:
        """Mueve el bloque a la primera escena libre de su beat; devuelve el motivo si no puede."""
        bt = beat_en(float(b["start"]))
        for s2 in escenas_del_beat_desde(desde, bt):
            if not libre(s2):
                continue
            si = oracion_en(s2.start)
            chars = caracteres(b.get("tipo_rotulista", ""), b.get("kicker"), str(b.get("text") or b.get("headline") or ""),
                               str(b.get("author") or ""))
            t1, sin_t = tiempos(sents, si, round(s2.start, 3), chars, scenes)
            if sin_t:
                continue
            b["movido_escena"] = f"{float(b['start']):.2f} → {s2.start:.2f} s (escena {desde.idx} → {s2.idx})"
            b["start"], b["t1"], b["duration"] = round(s2.start, 3), t1, round(t1 - s2.start, 3)
            if "scene_idx" in b:
                b["scene_idx"] = s2.idx
            return None
        return "no hay otra escena libre en su beat (con tiempo de lectura)"

    def fuera(campo: str, b: dict, motivo: str) -> None:
        filas.append({"pool_id": b.get("pool_id"), "tipo": b.get("tipo_rotulista"),
                      "texto": b.get("text") or b.get("headline") or b.get("detail"), "t0": b.get("start"),
                      "regla": "zona", "accion": "fuera", "motivo": motivo, "campo": campo})

    def prio(b: dict) -> tuple:
        return (not b.get("a_pantalla"), float(b["start"]))

    # 1. textos que no son ficha
    otros: list[tuple[str, dict]] = [("archive_clippings", a) for a in plan.get("archive_clippings") or []
                                     if a.get("rotulista")]
    for k in ("quote_card", "evidence_zoom"):
        if plan.get(k) and plan[k].get("rotulista"):
            otros.append((k, plan[k]))
    for campo, b in sorted(otros, key=lambda x: prio(x[1])):
        sc = scene_at(scenes, float(b["start"]))
        if not ocupa.get(sc.idx):
            marca(sc.idx, campo)
            continue
        motivo = (f"la escena {sc.idx} ya tiene {', '.join(ocupa[sc.idx])}" +
                  ("; la lupa no se mueve (su detalle está en esa foto)" if campo == "evidence_zoom" else ""))
        no = motivo if campo == "evidence_zoom" else mover(b, sc, lambda s2: not ocupa.get(s2.idx))
        if no:
            fuera(campo, b, motivo if no == motivo else f"{motivo}; {no}")
            if campo == "archive_clippings":
                plan[campo] = [a for a in plan[campo] if a is not b]
            else:
                plan[campo] = None
        else:
            marca(scene_at(scenes, float(b["start"])).idx, campo)
    # 2. el reloj
    tk = plan.get("time_ticker")
    reloj: tuple[float, float] | None = None
    if tk:
        end = float(tk["start"]) + float(tk["duration"])
        bt = beat_en(float(tk["start"]))
        anim_beat = []
        for e in plan.get("emphasis") or []:
            if _sello_queda(e, plan) and beat_en(float(e["start"])) is bt:
                anim_beat.append("sello")
        if plan.get("evidence_zoom") and beat_en(float(plan["evidence_zoom"]["start"])) is bt:
            anim_beat.append("lupa")

        def choca(st: float) -> list[str]:
            return [f"escena {s.idx}: {', '.join(ocupa[s.idx])}" for s in scenes
                    if s.start < end and s.end > st and ocupa.get(s.idx)]
        motivo = None
        if anim_beat:
            motivo = f"una animación por beat: el beat {bt['n'] if bt else '?'} ya tiene {', '.join(anim_beat)}"
        elif choca(float(tk["start"])):
            c0 = choca(float(tk["start"]))
            cambios = [float(c["t"]) for c in tk.get("changes") or []]
            nuevo = next((s.start for s in escenas_del_beat_desde(scene_at(scenes, float(tk["start"])), bt)
                          if not choca(s.start) and end - s.start >= TICKER_MIN
                          and not any(float(tk["start"]) < c <= s.start for c in cambios)), None)
            if nuevo is None:
                motivo = f"encima de otra cosa ({'; '.join(c0)}) y sin otra escena libre en su beat"
            else:
                filas.append({"bloque": "time_ticker", "regla": "zona", "accion": "movido",
                              "motivo": f"{float(tk['start']):.2f} → {nuevo:.2f} s ({'; '.join(c0)})"})
                tk["start"], tk["duration"] = round(nuevo, 3), round(end - nuevo, 3)
        if motivo:
            filas.append({"bloque": "time_ticker", "texto": f"{tk.get('day')} {tk.get('month')}", "t0": tk["start"],
                          "regla": "zona", "accion": "fuera", "motivo": motivo})
            plan["time_ticker"] = None
        else:
            reloj = (float(tk["start"]), float(tk["start"]) + float(tk["duration"]))
    # 3. las fichas
    fichas = [c for c in plan.get("callouts") or [] if c.get("ficha")]

    def libre_ficha(s2: Any) -> bool:
        return not ocupa.get(s2.idx) and not (reloj and s2.start < reloj[1] and s2.end > reloj[0])
    for c in sorted(fichas, key=prio):
        sc = scene_at(scenes, float(c["start"]))
        if libre_ficha(sc):
            marca(sc.idx, "ficha")
            continue
        hay = list(ocupa.get(sc.idx) or []) + (["reloj"] if reloj and sc.start < reloj[1] and sc.end > reloj[0] else [])
        motivo = f"la escena {sc.idx} ya tiene {', '.join(hay)}"
        no = mover(c, sc, libre_ficha)
        if no:
            fuera("callouts", c, f"{motivo}; {no}")
            plan["callouts"] = [x for x in plan["callouts"] if x is not c]
        else:
            filas.append({"pool_id": c.get("pool_id"), "tipo": c.get("tipo_rotulista"), "texto": c["text"],
                          "regla": "zona", "accion": "movido", "motivo": f"{motivo} → {c['movido_escena']}"})
            marca(scene_at(scenes, float(c["start"])).idx, "ficha")
    plan["callouts"] = sorted(plan.get("callouts") or [], key=lambda c: c["start"])
    rot = plan.setdefault("rotulista", {})
    rot["escena"] = filas
    log.append(f"  rotulista escena: {[(f.get('pool_id') or f.get('bloque'), f['accion'], f['motivo']) for f in filas]}"
               f" · title card {gfx_rules.title_dur:.1f} s")
    return filas


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
    return entrada(ctx["chapter_number"], real, carga["escaleta"], ctx.get("pool"), words, time_offset,
                   voz_video=voz_del_video(ctx)), words, ctx


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
