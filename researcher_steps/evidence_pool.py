"""
researcher_steps/evidence_pool.py — Sub-paso 4a bis (F5 §1.1): el research COMPLETO como evidence_pool.

Los 6–12 verified_facts siguen igual (los usan las imágenes). Esto es una segunda extracción sobre los mismos
bloques angulares, SIN tope, para que el guion y la pantalla tengan todos los datos del research:

    "evidence_pool": {
      "datos":      [{"id": "D01", "texto", "tipo", "valor", "fecha", "bloque", "fuente"}],
      "cronologia": [{"id": "T01", "fecha", "hora", "evento", "bloque", "fuente"}],
      "lugares":    [{"id": "L01", "nombre", "rol", "bloque", "lat", "lon"}],
      "citas":      [{"id": "Q01", "texto", "autor", "fecha", "bloque", "fuente"}],
      "personajes": [{"id": "P01", "nombre", "rol", "antagonista", "bloque"}]
    }

Reglas (deterministas, después del LLM):
    literal    texto / evento / cita / nombre de lugar y de personaje tienen que estar LITERALES en su bloque
               (comparación sin mayúsculas, espacios ni tipo de comillas). Lo que no está literal se descarta.
               `valor` tiene que estar literal en `texto`; si no, null.
    fuente     solo una de las [FUENTES CONSULTADAS] de ESE bloque, y solo si el ítem (o la línea del bloque de
               donde sale) nombra a la organización/autor de esa fuente. Si no, null. Nunca inventada.
    ids        los asigna el código (D01…, T01…), en el orden de los bloques; duplicados entre bloques → uno
               (cronología: misma fecha + mismo evento; personajes: mismo nombre y apellido; datos: un texto
               contenido en otro del mismo bloque).
    limpieza   personajes = personas (≥ 2 palabras con mayúscula, sin organizaciones); citas que son el título de
               una fuente no son citas.
    lugares    geocodificados una vez con Nominatim (gratis; caché en data/geocode_cache.json), ANCLADOS al lugar
               principal del video (el más nombrado): «nombre, ancla» y solo resultados a ≤ GEO_MAX_KM del ancla;
               siglas sin geocodificar. Sin resultado confiable → null.
F5b:
    relevancia (N1) lo que el propio bloque marca como «no (directamente) relacionado» con el caso queda fuera: el
               párrafo del marcador y las líneas que comparten ≥ 2 raíces RARAS con él (la posada de 1902, el médium).
    nombres    (N5) un personaje entra solo si HACE algo en el research (verbo activo después de su nombre, autor de
               una cita o antagonista); «Raphael Schwarz es arrestado» no alcanza. Sus datos de puro nombre, fuera.
    mayúsculas (N5) «Institución: Prisión…» pierde el rótulo; el rol va en minúscula («arrestado por…»).
    Lo descartado queda en pool["_descartados"] (auditable; evidence.items no lo lee).
LLAMADAS: 1 Flash por bloque (tecnico, humano, misterio).
"""
from __future__ import annotations

import json
import re
import time
import unicodedata
from pathlib import Path
from typing import Any, Callable

BLOCKS = ("tecnico", "humano", "misterio")
TIPOS = ("magnitud", "cifra", "fecha", "nombre", "lugar", "cita", "contradiccion")
GEOCODE_CACHE_NAME = "geocode_cache.json"
NOMINATIM = "https://nominatim.openstreetmap.org/search"
USER_AGENT = "automatization_videos/F5 (research geocoding; contact: repo owner)"

SYSTEM = ("Sos un investigador documental. Copiás datos de un bloque de investigación SIN reescribirlos: cada texto "
          "que devolvés es un fragmento LITERAL del bloque. Nunca inferís ni completás. Respondés SOLO JSON.")

_ITEM = {"type": "OBJECT"}
SCHEMA: dict[str, Any] = {
    "type": "OBJECT",
    "properties": {
        "datos": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "texto": {"type": "STRING"}, "tipo": {"type": "STRING", "enum": list(TIPOS)}, "valor": {"type": "STRING"},
            "fecha": {"type": "STRING"}, "fuente": {"type": "STRING"}}, "required": ["texto", "tipo"]}},
        "cronologia": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "fecha": {"type": "STRING"}, "hora": {"type": "STRING"}, "evento": {"type": "STRING"},
            "fuente": {"type": "STRING"}}, "required": ["fecha", "evento"]}},
        "lugares": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "nombre": {"type": "STRING"}, "rol": {"type": "STRING"}}, "required": ["nombre"]}},
        "citas": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "texto": {"type": "STRING"}, "autor": {"type": "STRING"}, "fecha": {"type": "STRING"},
            "fuente": {"type": "STRING"}}, "required": ["texto", "autor"]}},
        "personajes": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "nombre": {"type": "STRING"}, "rol": {"type": "STRING"}, "antagonista": {"type": "BOOLEAN"}},
            "required": ["nombre", "rol"]}},
    },
    "required": ["datos", "cronologia", "lugares", "citas", "personajes"],
}


# ═══════════════════════════════════════════════════════════════
#  Normalización y literalidad
# ═══════════════════════════════════════════════════════════════

_QUOTES = str.maketrans({"“": '"', "”": '"', "«": '"', "»": '"', "‘": "'", "’": "'", "´": "'"})


def norm(s: str) -> str:
    """Minúsculas, comillas unificadas, sin tildes, espacios colapsados, sin puntuación final."""
    s = str(s or "").translate(_QUOTES).lower()
    s = "".join(c for c in unicodedata.normalize("NFD", s) if unicodedata.category(c) != "Mn")
    s = re.sub(r"\s+", " ", s).strip()
    return s.strip(" .,;:")


def literal_in(fragment: str, block: str) -> bool:
    f = norm(fragment)
    return bool(f) and f in norm(block)


def block_sources(block: str) -> list[str]:
    """Las fuentes listadas en [FUENTES CONSULTADAS] del bloque (sin el guion inicial ni el punto final)."""
    m = re.search(r"\[FUENTES CONSULTADAS\](.*?)(?:\n\[[A-ZÁÉÍÓÚ ]+\]|\Z)", block, re.S)
    if not m:
        return []
    out = []
    for ln in m.group(1).splitlines():
        ln = ln.strip()
        if ln.startswith(("-", "•", "*")):
            out.append(ln.lstrip("-•* ").rstrip(".").strip())
    return [x for x in out if x]


def _source_names(src: str) -> list[str]:
    """Nombres con los que un ítem puede nombrar la fuente: la organización/autor (antes de la 1.ª coma) y su sigla
    entre paréntesis. «American Civil Liberties Union (ACLU), 2006, …» → ["american civil liberties union", "aclu"]."""
    head = src.split(",")[0]
    names = [re.sub(r"\(.*?\)", "", head).strip()]
    names += re.findall(r"\(([A-Za-z.]{2,})\)", head)
    if " / " in head:                                   # «Jawetz, Tom / ACLU National Prison Project»
        names += [x.strip() for x in head.split(" / ")]
    return [norm(n) for n in names if len(norm(n)) >= 3]


def _line_of(fragment: str, block: str) -> str:
    """La línea (o párrafo) del bloque que contiene el fragmento: el contexto donde el research ata la fuente."""
    f = norm(fragment)
    for ln in block.splitlines():
        if f and f in norm(ln):
            return ln
    return ""


def resolve_source(item_text: str, claimed: str | None, block: str) -> str | None:
    """La fuente del ítem SOLO si es del bloque y el ítem (o, si no, su línea) nombra a esa organización/autor.
    Primero se busca en el texto del ítem: la línea puede nombrar otras organizaciones (ASCE ≠ USACE)."""
    srcs = block_sources(block)
    cands = srcs if not claimed else sorted(srcs, key=lambda s: norm(claimed) not in norm(s))
    for ctx in (norm(item_text), norm(_line_of(item_text, block))):
        for s in cands:
            if ctx and any(re.search(rf"\b{re.escape(n)}\b", ctx) for n in _source_names(s)):
                return s
    return None


_ORG_WORDS = {"union", "unión", "watch", "departamento", "cuerpo", "oficina", "agencia", "society", "asociacion",
              "asociación", "aclu", "fema", "comite", "comité", "tribunal", "corte", "jurado", "gobierno", "project"}


def is_person(name: str) -> bool:
    """Persona con nombre propio: ≥ 2 palabras con mayúscula, no una sigla ni una organización."""
    ws = [w for w in re.findall(r"[A-Za-zÁÉÍÓÚÑáéíóúñ.]+", name) if len(w.strip(".")) >= 2]
    caps = [w for w in ws if w[:1].isupper() and not w.isupper()]
    return len(caps) >= 2 and not ({norm(w) for w in ws} & _ORG_WORDS)


def _person_key(name: str) -> tuple[str, str]:
    ws = [norm(w) for w in re.findall(r"[A-Za-zÁÉÍÓÚÑáéíóúñ]+", name) if len(w) >= 2 and w[:1].isupper()]
    ws = [w for w in ws if w not in {"jr", "sr", "sheriff", "teniente", "general", "alcaide", "capitan"}]
    return (ws[0], ws[-1]) if ws else ("", "")


def _content_set(s: str) -> set[str]:
    return {w[:5] for w in re.findall(r"[a-z0-9ñ]+", norm(s)) if len(w) >= 4}


# ═══════════════════════════════════════════════════════════════
#  F5b N1 — relevancia: lo que el bloque marca como no relacionado
# ═══════════════════════════════════════════════════════════════

# sobre texto normalizado (sin tildes): «aunque no directamente relacionado con los eventos», «no prueban nada sobre»
_UNRELATED_RE = re.compile(r"\bno (?:esta |estan |guarda |tiene |es )?(?:directamente |realmente )?"
                           r"(?:relacionad[oa]s?|vinculad[oa]s?)\b|\bsin relacion (?:directa )?con\b|"
                           r"\bno prueban? nada sobre\b|\bajen[oa]s? (?:al caso|a los hechos|a los eventos)\b")
UNRELATED_MIN_SHARED = 2                 # raíces raras en común con la nota del marcador
# palabras del propio marcador y de discurso: no dicen DE QUÉ trata lo no relacionado
_MARKER_WORDS = {"directamente", "relacionado", "relacionada", "relacionados", "relacionadas", "existencia",
                 "ocurrido", "prueban", "perspectiva", "eventos", "vinculado", "vinculada"}
_SENT_SPLIT = re.compile(r"(?<=[a-záéíóúñ]{3}[.!?])\s+(?=[A-ZÁÉÍÓÚÑ¿¡])")


def _sents(text: str) -> list[str]:
    """Oraciones (sin cortar en «EE. UU.» ni en «Jr.»)."""
    return [s for ln in text.splitlines() for s in _SENT_SPLIT.split(ln) if s.strip()]


def _topic_roots(s: str) -> set[str]:
    return {w[:5] for w in re.findall(r"[a-zñ]+", norm(s)) if len(w) >= 7 and w not in _MARKER_WORDS}


def unrelated_lines(block: str) -> list[str]:
    """Regiones del bloque que el propio research marca como NO relacionadas con el caso: la oración del marcador y
    la siguiente (la nota), y las líneas que comparten ≥ UNRELATED_MIN_SHARED raíces RARAS con esa nota (raíz rara =
    de una palabra de ≥ 7 letras que aparece en ≤ 2 líneas del bloque)."""
    lines = [ln for ln in block.splitlines() if ln.strip()]
    sents = _sents(block)
    notes = [" ".join(sents[k:k + 2]) for k, s in enumerate(sents) if _UNRELATED_RE.search(norm(s))]
    if not notes:
        return []
    from collections import Counter
    df = Counter(w for ln in lines for w in _content_set(ln))
    topic = {w for n in notes for w in _topic_roots(n) if df[w] <= 2}
    return notes + [ln for ln in lines if not any(n in ln for n in notes)
                    and len(_content_set(ln) & topic) >= UNRELATED_MIN_SHARED]


def _in_lines(fragment: str, lines: list[str], block: str = "") -> bool:
    """¿El fragmento está en una región no relacionada y en NINGUNA otra parte del bloque? («Nueva Orleans» está en
    la nota de la posada, pero también en todo el resto: se queda)."""
    f = norm(fragment)
    if not f or not any(f in norm(ln) for ln in lines):
        return False
    rest = norm(block)
    for ln in lines:
        rest = rest.replace(norm(ln), " ")
    return f not in rest


# ═══════════════════════════════════════════════════════════════
#  F5b N5 — un nombre entra solo si hace algo
# ═══════════════════════════════════════════════════════════════

_PASSIVE_AUX = {"es", "son", "fue", "fueron", "era", "eran", "sera", "seran", "sido", "habia", "habian"}
_CLITIC = {"no", "se", "le", "les", "lo", "la", "los", "las", "nunca", "luego", "tambien", "ya"}
_NOT_VERB = {"antes", "entre", "sobre", "durante", "mientras", "donde", "cuando", "parte", "noche", "calle", "sheriff"}
_VERB_END = re.compile(r"(o|io|aron|ieron|eron|aba|aban|ia|ian)$")
_PRESENT_END = re.compile(r"(a|e|an|en)$")


def _verb_like(tok: str) -> bool:
    t = norm(tok)
    if t in _NOT_VERB or len(t) < 3:
        return False
    if _VERB_END.search(t) and len(t) >= 4 and tok.lower().endswith(("ó", "ió", "aron", "ieron", "eron", "aba", "aban",
                                                                      "ía", "ían")):
        return True
    return bool(_PRESENT_END.search(t)) and len(t) >= 5


def _fold(s: str) -> str:
    """Minúsculas y sin tildes, carácter por carácter: conserva las posiciones del original."""
    return "".join(unicodedata.normalize("NFD", c)[0] for c in s.lower())


def person_acts(name: str, blocks: list[str], citas: list[dict] | None = None) -> bool:
    """¿El research le atribuye una ACCIÓN a la persona? Autor de una cita, o un verbo activo después de su nombre
    (saltando «Jr.», un sujeto coordinado «y Paul Kunkel Jr.», una aposición «, un recluso,» y un «del Cuerpo de…»).
    «Raphael Schwarz es arrestado» (pasiva) o «el alcaide Cornel Hubert del Elayn Hunt… por la violación» → no."""
    surname = _person_key(name)[1]
    if not surname:
        return False
    if any(_person_key(q.get("autor") or "")[1] == surname for q in citas or []):
        return True
    for block in blocks:
        for sent in _sents(block):
            for m in re.finditer(rf"\b{re.escape(surname)}\b", _fold(sent)):
                toks = re.findall(r"[A-Za-zÁÉÍÓÚÑÜáéíóúñü.]+|,", sent[m.end():])
                i = 0

                def _skip_caps(j: int) -> int:
                    while j < len(toks) and (toks[j][:1].isupper() or norm(toks[j]) in {"de", "del", "la", "los"}):
                        j += 1
                    return j
                while i < len(toks):
                    t = norm(toks[i]).strip(".")
                    if toks[i] == "," or t in {"jr", "sr"}:
                        if toks[i] == "," and i + 1 < len(toks) and norm(toks[i + 1]).strip(".") not in {"jr", "sr"}:
                            j = next((x for x in range(i + 1, min(len(toks), i + 16)) if toks[x] == ","), None)
                            if j is None:
                                break
                            i = j + 1
                            continue
                        i += 1
                    elif t == "y" and i + 1 < len(toks) and toks[i + 1][:1].isupper():
                        i = _skip_caps(i + 1)
                    elif t in {"de", "del"} and i + 1 < len(toks) and toks[i + 1][:1].isupper():
                        i = _skip_caps(i + 1)
                    elif t in _CLITIC:
                        i += 1
                    else:
                        break
                if i < len(toks):
                    t = norm(toks[i]).strip(".")
                    if t not in _PASSIVE_AUX and _verb_like(toks[i].strip(".")):
                        return True
    return False


_COMMON_HEADS = ("Sheriff", "Huracán", "Teniente General", "Teniente", "Alcaide", "Recluso")


def fix_caps(texto: str) -> str:
    """Mayúsculas pegadas del research (F5b N5). El texto sigue literal (la comparación es sin mayúsculas):
    - tras un rótulo «Población carcelaria …: Aproximadamente 6,375…» → «…: aproximadamente 6,375…» (no si sigue un
      nombre propio: «Institución: Prisión Parroquial de Orleans»);
    - cargos y sustantivos comunes delante de un nombre, a mitad de oración: «El Sheriff Gusman» → «El sheriff
      Gusman», «Evento principal: Huracán Katrina» → «…: huracán Katrina»."""
    def _lab(m: re.Match) -> str:
        nxt = (m.group(3) or "").strip()
        return m.group(1) + m.group(2)[:1].lower() + m.group(2)[1:] if not nxt[:1].isupper() else m.group(0)
    s = re.sub(r"(:\s+)([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)(?=(\s+\S+)?)", _lab, texto)
    for h in _COMMON_HEADS:
        s = re.sub(rf"(?<=\S\s){h}(?=\s+[A-ZÁÉÍÓÚÑ])", h.lower(), s)
    return s


def _lower_first(s: str | None) -> str | None:
    """«Arrestado por…» → «arrestado por…» (el rol se pega a mitad de oración); siglas y nombres propios quedan."""
    if not s:
        return s
    w = s.split()[0]
    return s if w.isupper() or (len(s.split()) > 1 and s.split()[1][:1].isupper()) else s[:1].lower() + s[1:]


# ═══════════════════════════════════════════════════════════════
#  Prompt + validación por bloque
# ═══════════════════════════════════════════════════════════════

def build_prompt(block_name: str, block: str) -> str:
    return f"""BLOQUE «{block_name}» DE LA INVESTIGACIÓN:
═══════════════════════════════════════════════════
{block}
═══════════════════════════════════════════════════

Extraé TODO lo verificable del bloque, sin tope y sin resumir:
- datos: cada cifra, magnitud, fecha, nombre propio, lugar o contradicción oficial. "texto" = la frase LITERAL del
  bloque que lo contiene (copiada, no parafraseada, ≤ 30 palabras); "valor" = la cifra/fecha/nombre exacto dentro
  de ese texto; "fecha" = AAAA-MM-DD si el texto la da (si no, vacío); "tipo" ∈ {", ".join(TIPOS)}.
- cronologia: cada evento fechado de la sección [CRONOLOGÍA] (y fechas del resto). "evento" LITERAL del bloque;
  "fecha" AAAA-MM-DD (o AAAA-MM / AAAA si el bloque no da más); "hora" HH:MM solo si el bloque la da.
- lugares: cada lugar con nombre propio (edificio, calle, barrio, ciudad), "nombre" literal; "rol" en ≤ 6 palabras.
- citas: frases entre comillas atribuidas a una persona, "texto" literal SIN las comillas, "autor" literal.
- personajes: personas con nombre propio, "nombre" literal; "rol" en ≤ 10 palabras; antagonista=true solo si el
  bloque le atribuye una decisión que causó el daño.
- "fuente": SOLO si el bloque atribuye ese ítem a una de sus [FUENTES CONSULTADAS] (copiá la fuente tal cual
  figura en la lista). Si no la atribuye, dejalo vacío. NUNCA adivines la fuente.
No inventes nada que no esté escrito en el bloque."""


def _str(x: Any) -> str:
    return re.sub(r"\s+", " ", str(x or "")).strip()


def validate_block(raw: dict[str, Any], block_name: str, block: str, log: list[str]) -> dict[str, list[dict]]:
    """Ítems del bloque que cumplen literalidad; la fuente resuelta por resolve_source."""
    out: dict[str, list[dict]] = {k: [] for k in ("datos", "cronologia", "lugares", "citas", "personajes")}
    drop = 0
    for d in raw.get("datos") or []:
        t = _str(d.get("texto"))
        if not literal_in(t, block) or d.get("tipo") not in TIPOS:
            drop += 1
            continue
        v = _str(d.get("valor"))
        out["datos"].append({"texto": t, "tipo": d["tipo"], "valor": v if v and literal_in(v, t) else None,
                             "fecha": _str(d.get("fecha")) or None, "bloque": block_name,
                             "fuente": resolve_source(t, _str(d.get("fuente")) or None, block)})
    for c in raw.get("cronologia") or []:
        ev = _str(c.get("evento"))
        if not literal_in(ev, block) or not _str(c.get("fecha")):
            drop += 1
            continue
        out["cronologia"].append({"fecha": _str(c["fecha"]), "hora": _str(c.get("hora")) or None, "evento": ev,
                                  "bloque": block_name,
                                  "fuente": resolve_source(ev, _str(c.get("fuente")) or None, block)})
    for p in raw.get("lugares") or []:
        n = _str(p.get("nombre"))
        if not literal_in(n, block):
            drop += 1
            continue
        out["lugares"].append({"nombre": n, "rol": _str(p.get("rol")) or None, "bloque": block_name})
    fuentes_txt = " ".join(block_sources(block))
    for q in raw.get("citas") or []:
        t, a = _str(q.get("texto")).strip('"“”«»\''), _str(q.get("autor"))
        if not literal_in(t, block) or not literal_in(a, block):
            drop += 1
            continue
        if literal_in(t, fuentes_txt):                  # el título de un informe no es una cita
            continue
        out["citas"].append({"texto": t, "autor": a, "fecha": _str(q.get("fecha")) or None, "bloque": block_name,
                             "fuente": resolve_source(t + " " + a, _str(q.get("fuente")) or None, block)})
    for p in raw.get("personajes") or []:
        n = _str(p.get("nombre"))
        if not literal_in(n, block):
            drop += 1
            continue
        if not is_person(n):                            # ACLU, «médium psíquico»: no son personajes
            continue
        out["personajes"].append({"nombre": n, "rol": _str(p.get("rol")) or None,
                                  "antagonista": bool(p.get("antagonista")), "bloque": block_name})
    # datos: un texto contenido en otro dato del mismo bloque es un fragmento repetido
    keep = []
    for d in out["datos"]:
        if any(x is not d and norm(d["texto"]) in norm(x["texto"]) and len(x["texto"]) > len(d["texto"])
               for x in out["datos"]):
            continue
        keep.append(d)
    out["datos"] = keep
    if drop:
        log.append(f"  [4a·pool] {block_name}: {drop} ítem(s) descartado(s) por no estar literales en el bloque")
    # F5b N1: fuera lo que el propio bloque marca como no relacionado con el caso
    unrel = unrelated_lines(block)
    out["_descartados"] = []
    if unrel:
        for k in ("datos", "cronologia", "lugares", "citas", "personajes"):
            kept = []
            for it in out[k]:
                if _in_lines(it[_KEY[k]], unrel, block):
                    out["_descartados"].append({"kind": k, "texto": it[_KEY[k]], "bloque": block_name,
                                                "motivo": "el bloque lo marca como no relacionado con el caso"})
                else:
                    kept.append(it)
            out[k] = kept
        if out["_descartados"]:
            log.append(f"  [4a·pool] {block_name}: {len(out['_descartados'])} ítem(s) fuera por no relacionados "
                       f"({[d['texto'][:40] for d in out['_descartados']]})")
    # F5b N5: mayúsculas pegadas (las citas quedan como las dijo el autor)
    for d in out["datos"]:
        d["texto"] = fix_caps(d["texto"])           # `valor` queda: sigue literal (sin mayúsculas) en el texto
    for c in out["cronologia"]:
        c["evento"] = fix_caps(c["evento"])
    for p in out["lugares"] + out["personajes"]:
        p["rol"] = _lower_first(p.get("rol"))
    return out


# ═══════════════════════════════════════════════════════════════
#  Merge entre bloques + ids
# ═══════════════════════════════════════════════════════════════

_PREFIX = {"datos": "D", "cronologia": "T", "lugares": "L", "citas": "Q", "personajes": "P"}
_KEY = {"datos": "texto", "cronologia": "evento", "lugares": "nombre", "citas": "texto", "personajes": "nombre"}


def merge(per_block: list[dict[str, list[dict]]]) -> dict[str, list[dict]]:
    pool: dict[str, list[dict]] = {k: [] for k in _PREFIX}
    for part in per_block:
        for k in _PREFIX:
            for it in part.get(k) or []:
                key = norm(it[_KEY[k]])

                def _same(x: dict) -> bool:
                    if norm(x[_KEY[k]]) == key:
                        return True
                    if k == "personajes":
                        return _person_key(x["nombre"]) == _person_key(it["nombre"])
                    if k == "lugares":
                        return key in norm(x["nombre"]) or norm(x["nombre"]) in key
                    if k == "cronologia":               # mismo día y el mismo hecho contado por otro bloque
                        a, b = _content_set(x["evento"]), _content_set(it["evento"])
                        return x["fecha"] == it["fecha"] and bool(a and b) and len(a & b) / min(len(a), len(b)) >= 0.5
                    return False
                prev = next((x for x in pool[k] if _same(x)), None)
                if prev is None:
                    pool[k].append(dict(it))
                elif k == "personajes":                 # el nombre más completo y antagonista si algún bloque lo dice
                    if len(it["nombre"]) > len(prev["nombre"]):
                        prev["nombre"] = it["nombre"]
                    prev["antagonista"] = prev.get("antagonista") or it.get("antagonista")
                elif k == "cronologia" and (it.get("fuente") and not prev.get("fuente")
                                            or len(it["evento"]) > len(prev["evento"]) and not prev.get("fuente")):
                    prev.update({kk: it[kk] for kk in ("evento", "bloque", "fuente", "hora") if it.get(kk)})
                elif not prev.get("fuente") and it.get("fuente"):
                    prev["fuente"] = it["fuente"]
    pool["cronologia"].sort(key=lambda c: (c["fecha"], c.get("hora") or ""))
    for k, pre in _PREFIX.items():
        for i, it in enumerate(pool[k], start=1):
            it["id"] = f"{pre}{i:02d}"
            pool[k][i - 1] = {"id": it.pop("id"), **it}
    return pool


# ═══════════════════════════════════════════════════════════════
#  Geocodificación (Nominatim, una vez, con caché)
# ═══════════════════════════════════════════════════════════════

GEO_MAX_KM = 400.0
_BROAD_ROLES = ("pais", "país", "estado", "ciudad", "region", "región")


def _km(a: tuple[float, float], b: tuple[float, float]) -> float:
    import math
    la1, lo1, la2, lo2 = map(math.radians, (*a, *b))
    h = math.sin((la2 - la1) / 2) ** 2 + math.cos(la1) * math.cos(la2) * math.sin((lo2 - lo1) / 2) ** 2
    return 6371.0 * 2 * math.asin(math.sqrt(h))


def anchor_place(lugares: list[dict], texts: list[str]) -> dict | None:
    """El lugar principal del video: la ciudad más nombrada en los textos del pool (rol ciudad), o el más nombrado."""
    blob = norm(" ".join(texts))
    ranked = sorted(lugares, key=lambda p: (not str(p.get("rol") or "").lower().startswith("ciudad"),
                                            -blob.count(norm(p["nombre"]))))
    return ranked[0] if ranked else None


def geocode(lugares: list[dict], cache_path: Path, *, fetch: Callable[[str], list] | None = None,
            log: list[str] | None = None, anchor: dict | None = None) -> None:
    """Agrega lat/lon a cada lugar (in place). Caché por consulta; 1 pedido/s (política OSM). Con ancla: se consulta
    «nombre, ancla» y solo se acepta un resultado a ≤ GEO_MAX_KM del ancla (los de rol país/estado/ciudad, sin tope).
    Siglas (todo mayúsculas, ≤ 5 letras) no se geocodifican. Sin resultado confiable → null."""
    try:
        cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.exists() else {}
    except (OSError, ValueError):
        cache = {}

    def _fetch(q: str) -> list:
        import requests
        r = requests.get(NOMINATIM, params={"q": q, "format": "json", "limit": 1},
                         headers={"User-Agent": USER_AGENT}, timeout=15)
        r.raise_for_status()
        time.sleep(1.1)
        return r.json()
    fetch = fetch or _fetch
    n_new = 0

    def _q(q: str) -> dict | None:
        nonlocal n_new
        key = norm(q)
        if key not in cache:
            try:
                res = fetch(q)
            except Exception as e:  # noqa: BLE001 — sin red: null, no se cachea el error
                if log is not None:
                    log.append(f"  [4a·pool] geocode «{q}» falló: {type(e).__name__}")
                return None
            cache[key] = ({"lat": float(res[0]["lat"]), "lon": float(res[0]["lon"]),
                           "display": res[0].get("display_name", "")} if res else None)
            n_new += 1
        return cache.get(key)

    a_xy = None
    if anchor is not None:
        ah = _q(anchor["nombre"])
        a_xy = (ah["lat"], ah["lon"]) if ah else None
    for p in lugares:
        p["lat"] = p["lon"] = None
        if re.fullmatch(r"[A-Z]{2,5}", p["nombre"].strip()):
            continue
        broad = str(p.get("rol") or "").lower().startswith(_BROAD_ROLES)
        if a_xy is None or broad or p is anchor:
            hits = [_q(p["nombre"])]
        else:
            hits = [_q(f"{p['nombre']}, {anchor['nombre']}"), _q(p["nombre"])]
        for h in hits:
            if h and (a_xy is None or broad or _km(a_xy, (h["lat"], h["lon"])) <= GEO_MAX_KM):
                p["lat"], p["lon"] = h["lat"], h["lon"]
                break
    if n_new:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        cache_path.write_text(json.dumps(cache, ensure_ascii=False, indent=1), encoding="utf-8")


# ═══════════════════════════════════════════════════════════════
#  F5d — cifras canónicas (oficial vs estimación)
# ═══════════════════════════════════════════════════════════════

_OFICIAL = re.compile(r"\b(oficial(?:es)?|estadisticas del|segun (?:el|la|los) (?:sheriff|departamento|oficina|gobierno)|"
                      r"registros oficiales|cifra oficial)\b")
_MEDIOS = re.compile(r"\b(medios de comunicacion|informes de los medios|prensa|estimando|estiman|estimaciones?|"
                     r"extraoficial(?:es)?)\b")
_APROX = re.compile(r"\b(aproximadamente|alrededor de|cerca de|unos|unas|mas de|hasta)\b")
_COUNT_NOUN = re.compile(r"\b(reclusos|personas|presos|prisioneros|evacuados|internos|encarcelad[oa]s)\b")
CANON_RATIO = 1.5                       # cifras del mismo conteo: la mayor ≤ 1.5 × la menor


def _sentence_of(fragment: str, blocks: list[str]) -> str:
    f = norm(fragment)
    for b in blocks:
        for s in _sents(b):
            if f and f in norm(s):
                return s
    return ""


_MESES_RE = r"(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|octubre|noviembre|diciembre)"


def _count_nums(t: str) -> list[str]:
    """Cifras de conteo del texto: sin años ni el día de una fecha («el 29 de agosto»)."""
    t = re.sub(rf"\b\d{{1,2}} de {_MESES_RE}\b", " ", t, flags=re.I)
    return [x for x in re.findall(r"\d[\d,]*\d", t) if not re.fullmatch(r"(19|20)\d\d", x)]


def figure_status(texto: str, blocks: list[str]) -> str:
    """Estatus de una cifra según el propio research: «oficial» (la oración la atribuye a estadísticas o registros
    oficiales), «medios» (estimación de la prensa), «rango» (dos cifras en el mismo texto), «aproximada» o «dato»."""
    t, s = norm(texto), norm(_sentence_of(texto, blocks))
    nums = _count_nums(texto)
    if len(nums) >= 2:
        return "rango"
    if _MEDIOS.search(t):
        return "medios"
    if _APROX.search(t):
        return "aproximada"
    if _OFICIAL.search(s):
        return "oficial"
    return "medios" if _MEDIOS.search(s) else "dato"


def canonical_figures(pool: dict[str, Any], blocks: list[str], log: list[str]) -> None:
    """F5d (in place): agrupa las cifras que cuentan lo MISMO (≥ 1000, mismo sustantivo de conteo, la mayor ≤
    CANON_RATIO × la menor) y, si el research marca una como oficial, la deja como canónica:
    pool["cifras_canonicas"] = [{"oficial": id, "valor": «6,375», "variantes": [{"id", "valor", "estatus"}]}].
    Cada dato del grupo lleva su `estatus`. El narrador usa la oficial; las otras, solo donde cuenta la contradicción."""
    _nums = _count_nums

    def _val(d: dict) -> int | None:
        m = _nums(d["texto"])
        return int(m[-1].replace(",", "")) if m else None
    cands = [d for d in pool.get("datos") or [] if d.get("tipo") in ("cifra", "contradiccion")
             and _val(d) and _val(d) >= 1000 and _COUNT_NOUN.search(norm(d["texto"]))]
    groups: list[list[dict]] = []
    for d in sorted(cands, key=_val):
        g = next((g for g in groups if _val(d) <= CANON_RATIO * min(_val(x) for x in g)), None)
        (g.append(d) if g is not None else groups.append([d]))
    out = []
    for g in groups:
        if len(g) < 2:
            continue
        for d in g:
            d["estatus"] = figure_status(d["texto"], blocks)
        of = [d for d in g if d["estatus"] == "oficial"]
        if not of:
            continue
        o = of[0]
        out.append({"oficial": o["id"], "valor": _nums(o["texto"])[-1],
                    "variantes": [{"id": d["id"], "valor": ", ".join(_nums(d["texto"])),
                                   "estatus": d["estatus"]} for d in g if d is not o]})
    pool["cifras_canonicas"] = out
    if out:
        log.append(f"  [4a·pool] cifras canónicas: {[(c['valor'], [v['valor'] for v in c['variantes']]) for c in out]}")


def acting_filter(pool: dict[str, Any], blocks: list[str], log: list[str]) -> None:
    """F5b N5 (in place): fuera los personajes que no HACEN nada en el research (salvo el antagonista, al que el
    research le atribuye la decisión) y los datos que son solo su nombre. Los ids de lo que queda no cambian."""
    out = pool.setdefault("_descartados", [])
    keep, gone = [], []
    for p in pool.get("personajes") or []:
        if p.get("antagonista") or person_acts(p["nombre"], blocks, pool.get("citas")):
            keep.append(p)
        else:
            gone.append(p)
            out.append({"kind": "personajes", "texto": p["nombre"], "bloque": p.get("bloque"),
                        "motivo": "el research no le atribuye ninguna acción (un nombre entra solo si hace algo)"})
    pool["personajes"] = keep
    gone_keys = {_person_key(p["nombre"]) for p in gone}
    datos = []
    for d in pool.get("datos") or []:
        if d.get("tipo") == "nombre" and _person_key(d["texto"]) in gone_keys and len(d["texto"].split()) <= 4:
            out.append({"kind": "datos", "texto": d["texto"], "bloque": d.get("bloque"),
                        "motivo": "solo el nombre de un personaje que no hace nada"})
            continue
        datos.append(d)
    pool["datos"] = datos
    if gone:
        log.append(f"  [4a·pool] personajes sin acción, fuera: {[p['nombre'] for p in gone]}")


# ═══════════════════════════════════════════════════════════════
#  Pública
# ═══════════════════════════════════════════════════════════════

def extract_evidence_pool(angle_blocks: dict[str, str], *, call: Callable[..., dict] | None = None,
                          geocode_cache: Path | None = None, fetch: Callable[[str], list] | None = None,
                          log: list[str] | None = None, raw_cache: Path | None = None) -> dict[str, list[dict]]:
    """evidence_pool de los 3 bloques (sin tope). Un bloque que falla no rompe el resto. `raw_cache` guarda la
    respuesta cruda de Flash por bloque (y la reusa si el bloque no cambió): el filtro se puede re-correr gratis."""
    log = log if log is not None else []
    if call is None:
        from gemini_helpers import call_flash_json as call
    parts = []
    for name in BLOCKS:
        block = angle_blocks.get(name) or ""
        if not block.strip():
            continue
        import hashlib
        h = hashlib.sha1(build_prompt(name, block).encode("utf-8")).hexdigest()[:12]
        cached = {}
        if raw_cache is not None and raw_cache.exists():
            try:
                cached = json.loads(raw_cache.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                cached = {}
        raw = (cached.get(name) or {}).get("raw") if (cached.get(name) or {}).get("hash") == h else None
        if raw is None:
            try:
                raw = call(build_prompt(name, block), system_instruction=SYSTEM, response_schema=SCHEMA,
                           description=f"4a evidence_pool {name}")
            except Exception as e:  # noqa: BLE001
                log.append(f"  [4a·pool] {name}: Flash falló ({type(e).__name__}) → bloque sin pool")
                continue
            if raw_cache is not None:
                cached[name] = {"hash": h, "raw": raw}
                raw_cache.parent.mkdir(parents=True, exist_ok=True)
                raw_cache.write_text(json.dumps(cached, ensure_ascii=False, indent=1), encoding="utf-8")
        parts.append(validate_block(raw or {}, name, block, log))
    pool = merge(parts)
    pool["_descartados"] = [d for p in parts for d in p.get("_descartados") or []]
    acting_filter(pool, [b for b in angle_blocks.values() if b], log)
    canonical_figures(pool, [b for b in angle_blocks.values() if b], log)
    if geocode_cache is None:
        from config import DATA_DIR
        geocode_cache = DATA_DIR / GEOCODE_CACHE_NAME
    texts = [d["texto"] for d in pool["datos"]] + [c["evento"] for c in pool["cronologia"]]
    geocode(pool["lugares"], geocode_cache, fetch=fetch, log=log, anchor=anchor_place(pool["lugares"], texts))
    log.append("  [4a·pool] " + " · ".join(f"{k} {len(v)}" for k, v in pool.items()))
    return pool
