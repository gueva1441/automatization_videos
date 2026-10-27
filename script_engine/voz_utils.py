"""
script_engine/voz_utils.py — F36 §A: la utilería de la voz que usan varios módulos de la capa de texto (movida de
gfx_rotulista sin cambios): cifras en dígitos y en letras (`numeros`, `numero_en`), nombres propios (`nombres`,
`nombre_inicial`), muñones, palabras de contenido, el analizador de cifras con unidad y magnitud (`_analiza`, lo usan la
coherencia, el contador y el agua) y las oraciones de la voz con cada palabra numerada (`oraciones`, `beat_de_oracion`).
Va aparte porque la usan rotulista_filtros, rotulista_colocar, clima, voz_datos y m01e_pantalla (decisión de F36 A).
"""
from __future__ import annotations

import re
import threading
from typing import Any

from script_engine import evidence as ev


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


# ═══════════════════════ cifras con unidad y magnitud (§A.4) ═══════════════════════

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


# ═══════════════════════ oraciones de la voz ═══════════════════════

def oraciones(words: list[dict], time_offset: float = 0.0) -> list[dict[str, Any]]:
    """Las oraciones de la voz (gfx_peak.sentences) con cada palabra numerada dentro de su oración y sus tiempos."""
    from script_engine.gfx_peak import sentences
    out = []
    for k, s in enumerate(sentences(words, time_offset)):
        pal = [{"k": j, "w": str(words[i]["word"]).strip(), "t0": round(float(words[i]["start"]) + time_offset, 3),
                "t1": round(float(words[i]["end"]) + time_offset, 3)} for j, i in enumerate(s["idx"])]
        out.append({"idx": k, "t0": round(s["t0"], 3), "t1": round(s["t1"], 3), "texto": s["text"], "palabras": pal})
    return out


def frases(text: str) -> list[str]:
    """Frases de una narración (corte en . ! ? … sin perder ¿…? completas). Movida de gfx_question.sentences sin cambios
    (F36 §D: gfx_question se borró; la usa gfx_layer para las frases vecinas del director de intensidad)."""
    parts = re.split(r"(?<=[.!?…])\s+", re.sub(r"\s+", " ", str(text)).strip())
    return [p.strip() for p in parts if p.strip()]


def oraciones_de_texto(texto: str) -> list[str]:
    """F36 §C.1: el mismo corte de `oraciones` (gfx_peak.sentences: la palabra que termina en . ! ? …) aplicado a un texto
    sin tiempos (la narración de Fase 1): el guion en papel y la voz se parten igual y Fase 2 los alinea por texto."""
    from script_engine.gfx_peak import sentences
    return [s["text"] for s in sentences([{"word": w, "start": 0.0, "end": 0.0} for w in palabras(texto)])]


def norm_oracion(texto: str) -> str:
    """F36 §C.4 (aclaración 2): una oración para alinear papel ↔ voz: sin tildes, puntuación, mayúsculas, etiquetas de
    TTS (`[pausa]`, `<break …/>`) ni pausas."""
    t = re.sub(r"\[[^\]]*\]|<[^>]*>", " ", str(texto or ""))
    return " ".join(re.findall(r"[^\W_]+", ev.norm(t)))


# ═══════════════════════ años del relato (F37 §A.1b) ═══════════════════════

def anios_de(fechas: list[Any]) -> tuple[int, int] | None:
    """El rango de años del material (el primero y el último año de las `fecha` del pool): un número de la voz es un año
    solo si cae ahí (derivado: el caso dice en qué años pasa; «setecientos quince» no es un año, «mil novecientos
    sesenta y tres» sí). None si el material no trae fechas."""
    ys = [int(m.group(1)) for f in fechas for m in [re.match(r"\s*(\d{4})", str(f or ""))] if m]
    return (min(ys), max(ys)) if ys else None


def anio_de(fecha: Any) -> int | None:
    m = re.match(r"\s*(\d{4})", str(fecha or ""))
    return int(m.group(1)) if m else None


def anios_dichos(texto: str, rango: tuple[int, int] | None) -> list[int]:
    """Los años que dice un texto, en dígitos o en letras («mil novecientos sesenta y tres», «dos mil»): las cifras de
    `numeros` que caen en el rango de años del material (`anios_de`)."""
    if not rango:
        return []
    out = []
    for n in numeros(texto):
        v = _valor(n)
        if isinstance(v, int) and rango[0] <= v <= rango[1]:
            out.append(v)
    return out


def dice_anio(anio: int, texto: str, rango: tuple[int, int] | None) -> bool:
    """¿El texto dice ese año o uno posterior? En cifras completas, o el año dicho en sus dos últimas cifras («en la
    década del cincuenta» = 1950: así se dicen los años en castellano; derivado, sin lista de palabras)."""
    if any(y >= anio for y in anios_dichos(texto, rango)):
        return True
    return any(_valor(n) == anio % 100 for n in numeros(texto)) if anio % 100 else False


# ═══════════════════════ velocidad del narrador (F37 §0: SEG_POR_PALABRA derivado) ═══════════════════════

def narrador() -> str | None:
    """La voz con que se va a narrar el video: la del perfil de audio activo para guiones v3 (ElevenLabs v4,
    audio_manager: `voice_id_v4`, si no `voice_id`)."""
    try:
        from audio_config import AUDIO_STYLE
    except Exception:  # noqa: BLE001 — sin perfil de audio no hay narrador conocido
        return None
    return AUDIO_STYLE.get("voice_id_v4") or AUDIO_STYLE.get("voice_id")


def seg_por_palabra(voz: str | None = None, audio_dir: Any = None) -> dict[str, Any] | None:
    """F37 §0: segundos por palabra del narrador = la mediana, oración por oración, de todas las voces ya generadas con
    él (`output/audio/<topic>/chNN.meta.json` con su `voice_id` y los tiempos de palabra de ElevenLabs en
    `chNN_timestamps.json`; el mismo audio copiado en varios topics cuenta una vez, por su `tts_hash`). None si no hay
    ninguna (el que llama usa su respaldo y lo anota). {valor, oraciones, caps, voz}."""
    import json
    import statistics
    from pathlib import Path
    from script_engine.gfx_peak import sentences
    voz = voz or narrador()
    if audio_dir is None:
        from config import OUTPUT_DIR
        audio_dir = Path(OUTPUT_DIR) / "audio"
    vistos: set[str] = set()
    por_oracion: list[float] = []
    caps = 0
    for meta in sorted(Path(audio_dir).glob("*/ch*.meta.json")):
        try:
            m = json.loads(meta.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        clave = str(m.get("tts_hash") or meta)
        if not voz or m.get("voice_id") != voz or clave in vistos:
            continue
        ts = meta.with_name(meta.name.replace(".meta.json", "_timestamps.json"))
        try:
            words = json.loads(ts.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        vistos.add(clave)
        caps += 1
        for s in sentences(words):
            if len(s["idx"]) and s["t1"] > s["t0"]:
                por_oracion.append((s["t1"] - s["t0"]) / len(s["idx"]))
    if not por_oracion:
        return None
    return {"valor": round(statistics.median(por_oracion), 4), "oraciones": len(por_oracion), "caps": caps, "voz": voz}


def beat_de_oracion(s: dict, beats: list[dict]) -> int | None:
    """El beat de una oración: el que contiene su inicio (con la tolerancia de pico_cap); si cae entre beats, el último
    que ya empezó."""
    for b in beats:
        if b["t0"] - 0.3 <= s["t0"] <= b["t1"]:
            return b["n"]
    prev = [b for b in beats if b["t0"] <= s["t0"]]
    return (prev[-1] if prev else beats[0])["n"] if beats else None
