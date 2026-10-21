"""
gfx_intensity.py — Director de intensidad (F4b §1): un LLM LEE el cap y marca dónde pega, sin escribir texto.

Contrato
    entrada  narración del cap en frases numeradas (+ últimas 2 del cap anterior y primeras 2 del siguiente, contexto)
    salida   {"pico_sentence_idx", "intensidad": [0–1 por frase], "cargas": [{word, sentence_idx, categoria, peso 1–3,
             concreta}] (hasta 10; F4c R1: se quedan las 5 de MAYOR PESO, empate → la más rara del video; peso 1 nunca)}
    valida   word LITERAL en esa frase (misma flexión, sin tildes de diferencia); categoria ∈ moods del perfil (activas o
             reserva); peso 1–3; intensidad con una cifra por frase (0–1). Lo inválido se descarta (no el resto).
             2 intentos; si los 2 fallan → None (el pipeline usa el léxico fijo, como en F4).
    cache    work_dir/gfx_intensity_<cap>.json con la respuesta CRUDA + hash de la narración (cambia la narración → re-llama)

Uso en el pipeline (gfx_layer): augmented_moods() suma las cargas válidas de categorías ACTIVAS al léxico del cap (el
léxico fijo es el piso); peak_from_intensity() da el pico = frase de mayor intensidad (empate: más cargas de peso 3).
record_proposals() guarda las palabras nuevas en gfx_profiles/lexico_propuestas.json y promueve al léxico del perfil
las que aparecieron en 2 videos distintos.
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import time
import unicodedata
from pathlib import Path
from typing import Any, Callable

ATTEMPTS = 2
MIN_CARGAS, MAX_CARGAS = 3, 5
ASK_CARGAS = 10                     # F4c R1: Flash propone hasta 10; el validador se queda con las MAX_CARGAS de más peso
PROMPT_VERSION = "f5e-1"            # entra al hash del cache: cambiar el prompt re-llama (F5e: clase + neutra)
# F4c R2: sensorial sobre abstracto (pares mejor/peor, del análisis del 2026-10-20)
SENSORY_PAIRS = (("putrefacta", "catástrofe"), ("cadáveres", "tragedia"), ("sumergidos", "desastre"),
                 ("celdas", "caos"), ("pútrida", "horror"))
SYSTEM = ("Sos editor de un documental de misterio. Leés la narración de UN capítulo y marcás dónde pega más fuerte: "
          "la frase pico, la intensidad de cada frase y las palabras de carga. NUNCA escribís texto nuevo: solo copiás "
          "palabras que ya están en la narración. Respondés SOLO JSON.")
SCHEMA: dict[str, Any] = {
    "type": "OBJECT",
    "properties": {
        "pico_sentence_idx": {"type": "INTEGER"},
        "intensidad": {"type": "ARRAY", "items": {"type": "NUMBER"}},
        "cargas": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "word": {"type": "STRING"}, "sentence_idx": {"type": "INTEGER"}, "categoria": {"type": "STRING"},
            "peso": {"type": "INTEGER"}, "concreta": {"type": "BOOLEAN"},
            "clase": {"type": "STRING", "enum": ["sustantivo", "adjetivo", "verbo", "otro"]},
            "neutra": {"type": "BOOLEAN"}},
            "required": ["word", "sentence_idx", "categoria", "peso", "concreta", "clase", "neutra"]}},
    },
    "required": ["pico_sentence_idx", "intensidad", "cargas"],
}
PROPOSALS: Path = Path(__file__).resolve().parents[1] / "gfx_profiles" / "lexico_propuestas.json"


def _plain(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", str(s).lower()) if unicodedata.category(c) != "Mn")


def tok(w: str) -> str:
    return re.sub(r"^[¿¡\"'«“(]+|[.,;:!?…\"'»”)]+$", "", str(w).strip()).lower()


def build_prompt(sents: list[str], prev2: list[str], next2: list[str], moods: dict[str, dict[str, Any]],
                 rejected: list[str]) -> str:
    cats = "\n".join(f"- {k}: ej. {', '.join(list((m.get('triggers') or {}).keys())[:6])}" for k, m in moods.items())
    lines = ["CATEGORÍAS DEL CANAL (usá SOLO estas claves):", cats, ""]
    if prev2:
        lines += ["CONTEXTO — final del capítulo anterior:", *[f"  {s}" for s in prev2], ""]
    lines += ["CAPÍTULO (frases numeradas):", *[f"  {i}: {s}" for i, s in enumerate(sents)], ""]
    if next2:
        lines += ["CONTEXTO — comienzo del capítulo siguiente:", *[f"  {s}" for s in next2], ""]
    lines += [
        f"Devolvé:",
        f"- intensidad: una cifra 0–1 por cada frase del capítulo ({len(sents)} cifras, en orden);",
        "- pico_sentence_idx: la frase de más impacto emocional (la que el espectador recuerda);",
        f"- cargas: hasta {ASK_CARGAS} palabras de carga COPIADAS EXACTAS de la frase indicada (misma flexión), con "
        "su categoría, peso 2–3 (3 = golpe fuerte; una palabra de peso 1 NO es carga: no la listes) y concreta=true si "
        "es un sustantivo que se puede dibujar (celda, cadáver) o false si es abstracta (miedo, tragedia).",
        "- Preferí palabras que se puedan OLER, TOCAR o VER (putrefacta, cadáveres, sumergidos, celdas) sobre "
        "palabras-resumen (catástrofe, tragedia, caos, desastre, horror); las palabras-resumen solo si no hay "
        "sensoriales en esa frase. Revisá SIEMPRE la frase pico: su palabra más sensorial tiene que estar.",
        "- Ejemplos (mejor > peor): " + " · ".join(f"«{a}» > «{b}»" for a, b in SENSORY_PAIRS) + ".",
        "- Palabras comunes que se repiten en todo el relato (agua, oscuro) no son carga salvo que la frase las vuelva golpe.",
        "- clase: sustantivo | adjetivo | verbo | otro (de la palabra en ESA frase). neutra=true si la palabra SOLA no "
        "carga nada aunque la frase sí (estrella, suerte, agujero, estruendo, decisión): el golpe lo da la frase, no "
        "la palabra. Los sellos van solo en sustantivos y adjetivos con carga propia (cadáveres, putrefacta, celdas).",
        "No inventes palabras ni categorías.",
    ]
    if rejected:
        lines += ["", "El intento anterior NO sirvió:", *[f"- {r}" for r in rejected]]
    return "\n".join(lines)


def validate(raw: dict[str, Any], sents: list[str], moods: dict[str, dict[str, Any]],
             freq: dict[str, int] | None = None) -> tuple[dict[str, Any] | None, list[str]]:
    """(resultado válido | None, motivos). Las cargas inválidas se descartan una por una. F4c R1: peso 1 no es carga;
    de las válidas quedan las MAX_CARGAS de mayor peso (empate: la más rara en `freq`, la narración del video entero;
    después el orden del LLM)."""
    why: list[str] = []
    n = len(sents)
    inten = raw.get("intensidad") if isinstance(raw, dict) else None
    if not isinstance(inten, list) or len(inten) != n:
        return None, [f"intensidad con {len(inten) if isinstance(inten, list) else 0} cifras (se piden {n})"]
    try:
        inten = [max(0.0, min(1.0, float(x))) for x in inten]
    except (TypeError, ValueError):
        return None, ["intensidad no numérica"]
    cargas, seen = [], set()
    for c in raw.get("cargas") or []:
        try:
            si, peso = int(c.get("sentence_idx")), int(c.get("peso"))
        except (TypeError, ValueError):
            why.append(f"carga sin índice/peso: {c}")
            continue
        w, cat = tok(c.get("word", "")), str(c.get("categoria", ""))
        if not (0 <= si < n) or not w:
            why.append(f"«{w}»: frase {si} inexistente")
            continue
        if w not in {tok(x) for x in sents[si].split()}:
            why.append(f"«{w}» no está literal en la frase {si}")
            continue
        if cat not in moods:
            why.append(f"«{w}»: categoría «{cat}» no existe")
            continue
        if not 1 <= peso <= 3:
            why.append(f"«{w}»: peso {peso}")
            continue
        if peso >= 2 and _stamp_rule() and is_theme_word(w):
            why.append(f"«{w}»: palabra del tema → peso 1")         # F5f: «reclusos», «cárcel»… no son cargas
            peso = 1
        if peso == 1:
            why.append(f"«{w}»: peso 1 (no es carga)")
            continue
        if (w, si) in seen:
            continue
        # sin `clase` (respuesta anterior a F5e) solo se filtra la forma verbal
        clase, neutra = str(c.get("clase") or ""), bool(c.get("neutra"))
        if _stamp_rule() and ((clase and clase not in ("sustantivo", "adjetivo")) or neutra or is_verb_form(w)):
            why.append(f"«{w}»: {clase}{' neutra' if neutra else ''} (sellos solo en sustantivos/adjetivos de carga)")
            continue
        seen.add((w, si))
        cargas.append({"word": w, "sentence_idx": si, "categoria": cat, "peso": peso, "concreta": bool(c.get("concreta")),
                       "clase": clase, "neutra": neutra})
    if not cargas:
        return None, why + ["ninguna carga válida"]
    pk = raw.get("pico_sentence_idx")
    f = freq or {}
    order = sorted(range(len(cargas)), key=lambda k: (-cargas[k]["peso"], f.get(cargas[k]["word"], 0), k))
    if len(cargas) > MAX_CARGAS:
        why.append(f"fuera por tope de {MAX_CARGAS} (menos peso): {[cargas[k]['word'] for k in order[MAX_CARGAS:]]}")
    cargas = [cargas[k] for k in order[:MAX_CARGAS]]
    return {"intensidad": inten, "cargas": cargas,
            "pico_llm": int(pk) if isinstance(pk, int) and 0 <= pk < n else None}, why


def narration_hash(text: str) -> str:
    return hashlib.sha1(f"{PROMPT_VERSION}|{text}".encode("utf-8")).hexdigest()[:12]


def word_freq(text: str) -> dict[str, int]:
    out: dict[str, int] = {}
    for w in str(text).split():
        t = tok(w)
        if t:
            out[t] = out.get(t, 0) + 1
    return out


def intensity_for(sents: list[str], *, cap: str, work_dir: Path, moods_all: dict[str, dict[str, Any]],
                  prev2: list[str] | None = None, next2: list[str] | None = None,
                  call: Callable[..., dict] | None = None, log: list[str] | None = None,
                  video_text: str | None = None) -> dict[str, Any] | None:
    """Resultado validado del cap (cacheado por hash de la narración + versión del prompt). None → fallback al léxico
    fijo. `video_text` = narración del video entero (rareza para el desempate de R1)."""
    log = log if log is not None else []
    freq = word_freq(video_text if video_text is not None else " ".join(sents))
    h = narration_hash(" ".join(sents))
    cache = Path(work_dir) / f"gfx_intensity_{cap}.json"
    raw = None
    if cache.exists():
        try:
            c = json.loads(cache.read_text(encoding="utf-8"))
            raw = c.get("raw") if c.get("hash") == h else None
        except (OSError, ValueError):
            raw = None
    if raw is not None:
        res, why = validate(raw, sents, moods_all, freq)
        if res:
            return res
    if call is None:
        from gemini_helpers import call_flash_json as call
    rejected: list[str] = []
    for _ in range(ATTEMPTS):
        try:
            raw = call(build_prompt(sents, prev2 or [], next2 or [], moods_all, rejected), system_instruction=SYSTEM,
                       response_schema=SCHEMA, thinking_budget=0, description=f"gfx_intensity {cap}")
        except Exception as e:  # noqa: BLE001
            rejected.append(f"error {type(e).__name__}")
            continue
        res, why = validate(raw, sents, moods_all, freq)
        if why:
            log.append(f"  intensidad: descartado {why}")
        if res:
            cache.write_text(json.dumps({"hash": h, "raw": raw, "generado_en": time.strftime("%Y-%m-%d %H:%M:%S")},
                                        ensure_ascii=False, indent=1), encoding="utf-8")
            return res
        rejected += why
    log.append(f"  intensidad: el LLM falló {ATTEMPTS} veces → léxico fijo ({rejected[-3:]})")
    return None


_VERB_FORM = re.compile(r"(ó|ió|aron|ieron|eron|aba|aban|ía|ían|ando|iendo|endo|arse|erse|irse|iera|ieran|ara|aran)$")
_NOT_VERB_FORM = {"cara", "clara", "para", "agua", "aguas", "fiebre", "frente", "muerte", "suerte", "tumba", "barra",
                  "guerra", "tierra", "sierra", "torre", "disentería", "policía", "energía", "compañía", "agonía",
                  "alegría", "galería", "batería", "porquería"}


def is_verb_form(word: str) -> bool:
    """F5e: forma verbal conjugada, gerundio o infinitivo («murió», «ahogaban», «flotando», «ahogarse», «subiera»).
    Los participios (atrapados, encerradas) son adjetivos: no cuentan."""
    t = tok(word)
    if t in _NOT_VERB_FORM or len(t) < 4:
        return False
    return bool(_VERB_FORM.search(t))       # (sin infinitivos sueltos: «lugar», «mujer» no son verbos)


def _stamp_rule() -> bool:
    from gfx_config import gfx_rules
    return bool(gfx_rules.stamp_nouns_only)


def is_theme_word(word: str) -> bool:
    """F5f: palabra del TEMA del video (gfx_rules.theme_words: reclusos, prisioneros, presos, cárcel, prisión…): se
    repite en todo el relato, no es una carga."""
    from gfx_config import gfx_rules
    return tok(word) in {tok(w) for w in gfx_rules.theme_words}


def stamp_lexicon(moods: dict[str, dict[str, Any]]) -> dict[str, dict[str, Any]]:
    """F5e (token stamp_nouns_only): el léxico del cap sin formas verbales; los sellos y moods solo disparan con
    sustantivos y adjetivos (las cargas del director ya vienen filtradas por clase y neutra). F5f: las palabras del
    tema quedan con peso 1 (nunca sello ni mood)."""
    if not _stamp_rule():
        return moods
    out = copy.deepcopy(moods)
    for m in out.values():
        trig = m.get("triggers") or {}
        for w in [w for w in trig if is_verb_form(w)]:
            del trig[w]
        for w in [w for w in trig if is_theme_word(w)]:
            trig[w] = 1
        iw = m.get("icon_words") or {}
        for w in [w for w in iw if is_verb_form(w)]:
            del iw[w]
    return out


def augmented_moods(active: dict[str, dict[str, Any]], res: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    """Léxico del cap = léxico fijo (piso) + cargas válidas de categorías ACTIVAS (las de reserva no tienen capa).
    F4c: una palabra que ya está en el léxico conserva el peso DEL LÉXICO (Flash inflaba «agua» de 1 a 2); las
    cargas solo suman palabras nuevas."""
    out = copy.deepcopy(active)
    for c in (res or {}).get("cargas") or []:
        m = out.get(c["categoria"])
        if not m:
            continue
        trig = m.setdefault("triggers", {})
        if c["word"] not in trig:
            trig[c["word"]] = int(c["peso"])
    return out


def peak_sentence(res: dict[str, Any]) -> int:
    """Frase pico = mayor intensidad; empate → más cargas de peso 3; después la primera."""
    inten = res["intensidad"]
    n3 = [sum(1 for c in res["cargas"] if c["sentence_idx"] == i and c["peso"] == 3) for i in range(len(inten))]
    return max(range(len(inten)), key=lambda i: (inten[i], n3[i], -i))


def new_words(res: dict[str, Any] | None, base: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    known = {w for m in base.values() for w in (m.get("triggers") or {})}
    return [c for c in (res or {}).get("cargas") or [] if c["word"] not in known]


def record_proposals(res: dict[str, Any] | None, base: dict[str, dict[str, Any]], *, video_id: str,
                     path: Path = PROPOSALS, profile_path: Path | None = None, log: list[str] | None = None) -> list[str]:
    """Guarda las palabras nuevas; las que aparecen en 2 videos distintos entran al léxico del perfil. Devuelve las
    promovidas (para anotar en el reporte)."""
    nw = new_words(res, base)
    if not nw:
        return []
    try:
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except (OSError, ValueError):
        data = {}
    for c in nw:
        e = data.setdefault(c["word"], {"categoria": c["categoria"], "peso": c["peso"], "videos": [], "concreta": c["concreta"]})
        if video_id not in e["videos"]:
            e["videos"].append(video_id)
        e["peso"] = max(int(e["peso"]), int(c["peso"]))
    promoted = []
    if profile_path is not None:
        text = profile_path.read_text(encoding="utf-8")
        prof = json.loads(text)
        for w, e in data.items():
            if len(set(e["videos"])) >= 2 and not e.get("promovida"):
                m = (prof.get("moods") or {}).get(e["categoria"])
                k = text.find(f'"{e["categoria"]}": {{')
                t = text.find('"triggers": {', k) if k >= 0 else -1
                if m is not None and t >= 0 and w not in (m.get("triggers") or {}):
                    t += len('"triggers": {')                   # edición mínima: el perfil conserva su formato
                    text = text[:t] + f'{json.dumps(w, ensure_ascii=False)}: {int(e["peso"])}, ' + text[t:]
                    e["promovida"] = time.strftime("%Y-%m-%d")
                    promoted.append(w)
        if promoted:
            json.loads(text)                                     # sigue siendo JSON válido
            profile_path.write_text(text, encoding="utf-8")
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    if log is not None and (nw or promoted):
        log.append(f"  léxico: {len(nw)} propuesta(s) nueva(s) {[c['word'] for c in nw]}; promovidas {promoted}")
    return promoted
