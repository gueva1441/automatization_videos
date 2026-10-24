"""
nombres.py — F21 (familia A de la auditoría). Única fuente de verdad sobre nombres de persona.

Reemplaza a las funciones que decidían «qué es un nombre» y «cuál es el apellido» con regex latina y «apellido = última
palabra» (`research_v3.person_key/is_named_person/same_person/name_terms/_names_in`, `evidence_pool.is_person/
_person_key`, `evidence._surname`, `guion_v4._surname/_is_human`, `m01b_guionista._surname`, `verify_quotes._named`,
`m01a_columna._tokens`): las viejas quedan como alias de una línea (`# F21: alias`).
Cualquier alfabeto (`[^\\W\\d_]`), iniciales («V.M. Osetrov»), partículas («Juan de la Cruz»), mononimios con
`mononimo_ok` («Rasputin»), nombres en mayúsculas de un PDF («MARLIN GUSMAN»).
"""
from __future__ import annotations

import re
import unicodedata

PARTICULAS = {"de", "del", "la", "las", "los", "da", "das", "do", "dos", "di", "van", "von", "der", "den", "le",
              "du", "y", "e", "bin", "ibn", "al", "el"}
SUFIJOS = {"jr", "sr", "ii", "iii", "iv", "hijo", "padre"}
ARTICULOS = {"un", "una", "unos", "unas", "a", "an", "the"}
TRATAMIENTOS_BASE = {"mr", "mrs", "ms", "dr", "sra", "srta", "don", "dona",
                     "sheriff", "deputy", "alguacil", "sgt", "sergeant", "lieutenant", "lt", "captain", "capt",
                     "capitan", "colonel", "col", "officer", "oficial", "chief", "jefe", "teniente", "sargento",
                     "secretary", "secretario", "ranking",
                     # F21c: cargos genéricos (no de tema)
                     "warden", "director", "directora", "alcaide", "ministro", "ministra", "comandante", "general",
                     "doctor", "doctora", "profesor", "profesora", "ingeniero", "ingeniera", "presidente", "presidenta",
                     "gerente"} | SUFIJOS   # = el _TITLES_BASE de F20 + F21c; los roles del perfil se suman
_tratamientos = set(TRATAMIENTOS_BASE)

# = evidence_pool._QUOTES (con «´») + «„»
_Q = str.maketrans({"«": '"', "»": '"', "“": '"', "”": '"', "„": '"', "‘": "'", "’": "'", "´": "'"})


def norm(s) -> str:
    """Minúsculas, comillas unificadas, sin tildes **solo en letras latinas** (ü → u sí; й, ё intactas), espacios
    colapsados, sin puntuación final. Para texto latino da lo mismo que el `evidence_pool.norm` de antes."""
    out, keep = [], False
    for c in unicodedata.normalize("NFD", str(s or "").translate(_Q).lower()):
        if unicodedata.category(c) == "Mn":
            if keep:                                          # la marca de una letra no latina (й, ё) se queda
                out.append(c)
            continue                                          # sobre una latina o un signo, se va (como antes)
        keep = c.isalpha() and not unicodedata.name(c, "").startswith("LATIN")
        out.append(c)
    t = unicodedata.normalize("NFC", "".join(out))
    return re.sub(r"\s+", " ", t).strip().strip(" .,;:")


def set_tratamientos(extra) -> None:
    """Lo llama `research_v3.set_vocabulario` con las palabras de `roles_testigo`/`roles_antagonista` del perfil."""
    global _tratamientos
    _tratamientos = TRATAMIENTOS_BASE | {norm(w) for w in extra or [] if len(w) >= 3}


def tratamientos() -> set[str]:
    return set(_tratamientos)


def palabras(name) -> list[str]:
    """Las palabras de un nombre, en cualquier alfabeto, con las iniciales separadas: «V.M. Osetrov» → [V, M, Osetrov]."""
    s = re.sub(r"\([^)]*\)", " ", str(name or ""))
    return re.findall(r"[^\W\d_]+", s)


def _mayus(w: str, todo_mayus: bool) -> bool:
    return w[:1].isupper() and (todo_mayus or not w.isupper() or len(w) == 1)


def partes(name) -> list[str]:
    """Nombre y apellido(s) normalizados, sin tratamientos, sin partículas, sin iniciales. «Deputy Renard Reed» →
    [renard, reed]; «Juan de la Cruz» → [juan, cruz]; «Любовь Ладейщикова» → [любовь, ладейщикова]."""
    ws = palabras(name)
    todo = bool(ws) and all(w.isupper() for w in ws if len(w) > 1)      # «MARLIN GUSMAN» (PDF oficial)
    out = []
    for w in ws:
        n = norm(w)
        # F21 (recheck): un artículo en mayúscula al principio («Un oficial», «Una vecina») no es parte del nombre
        if len(w) == 1 or n in _tratamientos or n in PARTICULAS or n in ARTICULOS or not _mayus(w, todo):
            continue
        out.append(n)
    return out


def iniciales(name) -> list[str]:
    return [norm(w) for w in palabras(name) if len(w) == 1 and w.isupper()]


def clave(name) -> tuple[str, str]:
    """(nombre, apellido). Mononimio → ("", x). Sin partes → ("", "")."""
    p = partes(name)
    if not p:
        return ("", "")
    return (p[0] if len(p) > 1 else "", p[-1])


def apellido(name) -> str:
    return clave(name)[1]


_ORG = {"union", "watch", "departamento", "cuerpo", "oficina", "agencia", "society", "asociacion", "comite",
        "tribunal", "corte", "jurado", "gobierno", "project", "ministerio", "comision", "instituto", "empresa",
        "compania", "company", "committee", "ministry", "institute"}
_GRUPO = re.compile(r"\b(group|grupo|segun|según)\b", re.I)   # lo que queda de _NOT_PERSON: solo grupo/atribución
GRUPOS_BASE = {"officers", "oficiales", "officials", "guards", "guardias", "deputies"}   # formas de grupo, no persona
_grupos = set(GRUPOS_BASE)


def set_grupos(extra) -> None:
    """Lo llama `research_v3.set_vocabulario` con las formas de grupo (plurales) de los roles del perfil."""
    global _grupos
    _grupos = GRUPOS_BASE | {norm(w) for w in extra or []}


def es_persona(name, mononimo_ok: bool = False) -> bool:
    """Un nombre propio de persona: ≥ 1 apellido de ≥ 2 letras más (otra parte, una inicial o un tratamiento/cargo
    delante: «Deputy Foster»), sin palabras de organización ni de grupo. Con `mononimo_ok`, basta el apellido
    («Rasputin», un apodo)."""
    raw = palabras(name)
    ws = {norm(w) for w in raw}
    p = partes(name)
    if not p or ws & _ORG or ws & _grupos or _GRUPO.search(str(name or "")):
        return False
    # F21b, criterios de forma: con coma, « y » o « and » son dos personas («Толстиков, Бочкарева»); un tratamiento o
    # cargo seguido de partícula es un cargo, no una persona («Sheriff de Orleans Parish», «Captain of the Guard»)
    sin_sufijo = re.sub(r",\s*(?:jr|sr|ii|iii|iv)\.?\s*$", "", str(name or ""), flags=re.I)   # «Morgan, Jr.» es uno
    if re.search(r",|\s(?:y|and)\s", sin_sufijo):
        return False
    if any(norm(w) in _tratamientos and k + 1 < len(raw) and norm(raw[k + 1]) in PARTICULAS | {"of"}
           for k, w in enumerate(raw)):
        return False
    # una palabra en minúscula que no es partícula ni tratamiento es una descripción, no un nombre («un preso de…»)
    if any(w[:1].islower() and norm(w) not in PARTICULAS | _tratamientos for w in raw):
        return False
    # un cargo cuenta si va justo delante de una parte del nombre: «Deputy Foster», «el teniente Ivanov»; no en
    # «Un recluso de Templeman 4» (F21, recheck)
    car = _tratamientos - SUFIJOS
    cargo = any(norm(w) in car and k + 1 < len(raw) and norm(raw[k + 1]) in p for k, w in enumerate(raw))
    return len(p) >= 2 or bool(iniciales(name)) or cargo or (mononimo_ok and len(p) == 1)


def misma(a, b) -> bool:
    """Mismo apellido y nombre compatible (igual, uno sin nombre, o las 3 primeras letras iguales)."""
    (fa, la), (fb, lb) = clave(a), clave(b)
    return bool(la) and la == lb and (not fa or not fb or fa[:3] == fb[:3])


def terminos(persona: dict, people: list[dict]) -> list[str]:
    """Cómo buscar a una persona en texto normalizado: «nombre apellido» de cada variante, y el apellido solo si
    nadie más del pool lo comparte."""
    out = []
    for v in [persona.get("nombre")] + list(persona.get("variantes_nombre") or persona.get("variantes") or []):
        f, l = clave(v)
        if f and l:
            out.append(f"{f} {l}")
    sur = apellido(persona.get("nombre"))
    if sur and sum(1 for q in people if apellido(q.get("nombre")) == sur) == 1:
        out.append(sur)
    return list(dict.fromkeys(out))


def menciona(text, termino) -> bool:
    """¿`termino` (ya normalizado) aparece como palabra entera en `text`? Sin `\\b` (falla en cirílico)."""
    t = norm(text)
    return bool(termino) and re.search(rf"(?<![^\W\d_]){re.escape(termino)}(?![^\W\d_])", t) is not None


def plegar(text) -> str:
    """Como `norm` pero con el mismo largo que `text` (una letra por letra, sin colapsar espacios): para buscar
    posiciones dentro de un documento (`research_v3.presence_v3`)."""
    out = []
    for ch in str(text or "").translate(_Q).lower():
        d = unicodedata.normalize("NFD", ch)
        out.append(d[0] if len(d) > 1 and unicodedata.name(d[0], "").startswith("LATIN") and len(d[0]) == 1 else ch)
    return "".join(out)


def posiciones(texto_plegado: str, termino: str) -> list[int]:
    """Dónde aparece `termino` (normalizado; las palabras separadas por espacios o puntos) en un texto ya `plegar`."""
    pat = r"(?<![^\W\d_])" + r"[ .]+".join(re.escape(w) for w in termino.split()) + r"(?![^\W\d_])"
    return [m.start() for m in re.finditer(pat, texto_plegado)]


def nombra(text, persona: dict, people: list[dict]) -> bool:
    return any(menciona(text, x) for x in terminos(persona, people))
