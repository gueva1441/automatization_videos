"""
script_engine/evidence.py — Helpers del evidence_pool (F5) compartidos por m01a, m01b, las métricas del juez y gfx.

    items(pool)            {id: ítem} de datos, cronología, citas, lugares y personajes
    text_of(item)          el texto literal del ítem (texto / evento / cita / nombre)
    anchors(item)          lo que tiene que sonar LITERAL en la narración cuando se usa el ítem: la cifra/fecha/nombre
                           (`valor`), o la fecha del evento, o el autor de la cita, o el nombre del personaje
    format_pool(pool)      el pool numerado para un prompt (ids entre corchetes)
    used_in(text, item)    ¿la narración usa el ítem? (alguno de sus anchors literal; una cifra vale en dígitos o
                           en palabras; un evento o un dato de fecha cuenta solo si en la MISMA oración está la
                           fecha y una palabra de su contenido — «29 de agosto» sola no son seis eventos)
Todo detrás de `if pool`: un guion sin evidence_pool sigue con verified_facts.
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any

KINDS = ("datos", "cronologia", "citas", "lugares", "personajes")
MESES = ("enero", "febrero", "marzo", "abril", "mayo", "junio", "julio", "agosto", "septiembre", "octubre",
         "noviembre", "diciembre")


def norm(s: str) -> str:
    s = "".join(c for c in unicodedata.normalize("NFD", str(s or "").lower()) if unicodedata.category(c) != "Mn")
    s = s.translate(str.maketrans({"“": '"', "”": '"', "«": '"', "»": '"', "’": "'"}))
    return re.sub(r"\s+", " ", s).strip()


def items(pool: dict[str, Any] | None) -> dict[str, dict[str, Any]]:
    out: dict[str, dict[str, Any]] = {}
    for k in KINDS:
        for it in (pool or {}).get(k) or []:
            if it.get("id"):
                out[it["id"]] = {**it, "_kind": k}
    return out


def text_of(it: dict[str, Any]) -> str:
    return str(it.get("texto") or it.get("evento") or it.get("nombre") or "")


def spoken_date(iso: str | None) -> str | None:
    """'2005-08-29' → '29 de agosto' (lo que la voz dice); '2006-08' → 'agosto de 2006'; '2010' → '2010'."""
    if not iso:
        return None
    m = re.fullmatch(r"(\d{4})-(\d{2})-(\d{2})", iso)
    if m:
        return f"{int(m.group(3))} de {MESES[int(m.group(2)) - 1]}"
    m = re.fullmatch(r"(\d{4})-(\d{2})", iso)
    if m:
        return f"{MESES[int(m.group(2)) - 1]} de {m.group(1)}"
    return iso if re.fullmatch(r"\d{4}", iso) else None


def _surname(name: str) -> str:
    ws = [w for w in re.findall(r"[A-Za-zÁÉÍÓÚÑáéíóúñ]+", name) if w[:1].isupper() and len(w) > 2
          and w.lower() not in {"jr", "sr", "sheriff"}]
    return ws[-1] if ws else name


_NUM_UNIT = re.compile(r"\$?\d[\d.,]*\d%?|\$?\d%?")
_DAY_MONTH = re.compile(r"\b\d{1,2} de (?:" + "|".join(MESES) + r")\b", re.I)


def _numbers(s: str) -> list[str]:
    """Cifras de un texto (no años sueltos de 4 dígitos), con la palabra que las sigue si es una unidad corta."""
    out = []
    for m in _NUM_UNIT.finditer(s):
        tok = m.group(0)
        if re.fullmatch(r"(19|20)\d\d", tok):
            continue
        nxt = re.match(r"\s+([a-záéíóúñ]+)", s[m.end():])
        unit = nxt.group(1) if nxt and nxt.group(1) in {"pies", "metros", "metro", "pie", "millones", "dólares",
                                                         "años", "días", "pisos", "horas"} else ""
        out.append(f"{tok} {unit}".strip())
    return out


def anchors(it: dict[str, Any]) -> list[str]:
    """Formas literales que prueban que la narración usó el ítem (cualquiera alcanza).
    datos: fecha → el día y mes; cifra/magnitud → sus cifras (del valor o, si el valor no tiene, del texto); si no
    hay cifras, el valor; nombre/lugar → el valor (cuentan como uso, pero no son «datos duros», ver is_hard)."""
    k = it.get("_kind")
    if k == "datos":
        v, tipo, txt = it.get("valor") or "", it.get("tipo"), it.get("texto") or ""
        if tipo == "fecha":
            dm = _DAY_MONTH.search(v) or _DAY_MONTH.search(txt)
            return [dm.group(0)] if dm else ([spoken_date(it["fecha"])] if spoken_date(it.get("fecha"))
                                             and "-" in str(it.get("fecha")) else [])
        if tipo in ("cifra", "magnitud", "contradiccion"):
            nums = _numbers(v) or _numbers(txt)
            return nums or ([v] if v else [])
        return [v] if v else []
    if k == "cronologia":
        return [x for x in (spoken_date(it.get("fecha")),) if x]
    if k == "citas":                    # F7c-2: con `fragmento` (≤ 25 palabras), decir el fragmento ya es usar la cita
        return [x for x in (it.get("fragmento"), it["texto"]) if x]
    if k == "personajes":
        return [_surname(it["nombre"])]
    if k == "lugares":
        return [it["nombre"]]
    return []


def _num_forms(a: str) -> list[str]:
    """Formas de un anchor con cifras: cada entero en dígitos (con/sin separador) o en palabras (masc./fem.).
    «6,500» → «seis mil quinientas»; «15 pies» → «quince pies». Los decimales («4.6») quedan como están."""
    from script_engine.num_es import variants
    toks = re.findall(r"\d[\d.,]*\d|\d", a)
    forms = [a]
    for tk in toks[:2]:
        forms = [f.replace(tk, v, 1) for f in forms for v in variants(tk)]
    return list(dict.fromkeys(forms))


_NUMWORD = re.compile(r"\b(?:cero|uno?|una|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|once|doce|trece|catorce|"
                      r"quince|dieci\w+|veint\w+|treinta|cuarenta|cincuenta|sesenta|setenta|ochenta|noventa|cien|"
                      r"ciento|\w+cient[oa]s|quinient[oa]s|mil|millon(?:es)?|y)$")


def _hits(anchor: str, text: str) -> set[int]:
    """Posiciones (en el texto normalizado) donde el anchor suena literal. Una cifra dicha en palabras no vale si es
    parte de otra cifra («cincuenta» dentro de «seiscientos cincuenta mil» no es el 50)."""
    t = norm(text)
    out: set[int] = set()
    for f in _num_forms(anchor) if re.search(r"\d", anchor) else [anchor]:
        f = norm(f).strip(" .,;:")
        if not f:
            continue
        spelled = not re.search(r"\d", f) and re.search(r"\d", anchor)
        for m in re.finditer(rf"(?<![\w]){re.escape(f)}(?![\w])", t):
            if spelled:
                before = t[:m.start()].split()[-1:] or [""]
                after = t[m.end():].split()[:1] or [""]
                if _NUMWORD.search(before[0]) or re.match(r"(mil|millon|millones|y)\b", after[0]):
                    continue
            out.add(m.start())
    return out


def literal_in(anchor: str, text: str) -> bool:
    """¿El anchor suena literal en el texto? (ver _hits)."""
    return bool(_hits(anchor, text))


def count_in(anchor: str, text: str) -> int:
    """Cuántas veces suena el anchor (en dígitos o en palabras) en el texto (F5b N3)."""
    return len(_hits(anchor, text))


_FUNC = {"de", "del", "la", "las", "el", "los", "un", "una", "y", "en", "a", "al", "que", "por", "con", "para", "sin",
         "se", "su", "sus", "lo", "es", "fue", "era", "como", "mas", "muy", "entre", "sobre", "hasta", "desde",
         "cuando", "donde", "este", "esta", "estos", "estas"}


def _content(s: str) -> set[str]:
    return {w[:6] for w in re.findall(r"[a-zñ]{5,}", norm(s)) if w not in _FUNC and w not in MESES}


def _sentences(text: str) -> list[str]:
    return [x for x in re.split(r"(?<=[.!?…])\s+", str(text)) if x.strip()]


def used_in(text: str, it: dict[str, Any]) -> bool:
    ancs = anchors(it)
    dated = it.get("_kind") == "cronologia" or (it.get("_kind") == "datos" and it.get("tipo") == "fecha")
    if not dated:
        return any(literal_in(a, text) for a in ancs)
    words = _content(text_of(it)) - {w[:6] for a in ancs for w in re.findall(r"[a-zñ]{5,}", norm(a))}
    for s in _sentences(text):
        if any(literal_in(a, s) for a in ancs) and (not words or words & _content(s)):
            return True
    return False


def format_pool(pool: dict[str, Any] | None, ids: list[str] | None = None) -> str:
    """Pool numerado para prompts. Con `ids`, solo esos (en ese orden)."""
    its = items(pool)
    sel = [its[i] for i in ids if i in its] if ids is not None else list(its.values())
    lab = {"datos": "DATO", "cronologia": "CRONO", "citas": "CITA", "lugares": "LUGAR", "personajes": "PERSONA"}
    out = []
    for it in sel:
        k = it["_kind"]
        extra = ""
        if k == "cronologia":
            extra = f" ({it.get('fecha')}{' ' + it['hora'] if it.get('hora') else ''})"
        elif k == "citas":
            extra = f" — {it.get('autor')}"
        elif k == "personajes":
            extra = f" — {it.get('rol') or ''}{' · ANTAGONISTA' if it.get('antagonista') else ''}"
        elif k == "datos" and it.get("valor"):
            extra = f" [valor: {it['valor']}]"
        src = f" · fuente: {it['fuente']}" if it.get("fuente") else ""
        txt = f'"{it["texto"]}"' if k == "citas" else text_of(it)
        out.append(f"  [{it['id']}] {lab[k]}: {txt}{extra}{src}")
    return "\n".join(out) if out else "(sin evidence_pool)"


def is_hard(it: dict[str, Any]) -> bool:
    """Dato DURO (cuenta para densidad y repetición): cifra, magnitud, fecha con día o contradicción con anchor;
    eventos de la cronología con día; citas. Un nombre, un lugar o un año suelto no son «el dato»."""
    k = it.get("_kind")
    if k == "citas":
        return True
    if k == "cronologia":
        return bool(re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(it.get("fecha") or "")))
    if k == "datos":
        return it.get("tipo") in ("cifra", "magnitud", "fecha", "contradiccion") and bool(anchors(it))
    return False


# ═══════════════════════════════════════════════════════════════
#  F5b — repetición dentro del cap (N3), mismo hecho (S3), fecha del ítem (S2), mayúsculas pegadas (N5)
# ═══════════════════════════════════════════════════════════════

_VAGUE_W = {"algunos", "algunas", "otros", "otras", "muchos", "muchas", "todos", "todas", "varios", "varias",
            "cientos", "mientras", "despues", "antes", "durante", "habian", "fueron", "estaban"}


def signature_phrases(it: dict[str, Any]) -> list[str]:
    """3-gramas del texto del ítem con ≥ 2 palabras de contenido en minúscula («nivel del pecho», «aguas residuales
    refluyen»). Los nombres propios no cuentan: «Prisión de Orleans» repetida no es repetir el dato."""
    ws = re.findall(r"[A-Za-zÁÉÍÓÚÑÜáéíóúñü]+", text_of(it))
    out = []
    for k in range(len(ws) - 2):
        tri = ws[k:k + 3]
        if sum(1 for w in tri if w[:1].islower() and len(w) >= 5 and norm(w) not in _FUNC | _VAGUE_W) >= 2 \
                and not any(w[:1].isupper() for w in tri):
            out.append(" ".join(tri))
    return list(dict.fromkeys(out))


def repeats_in_cap(text: str, ids: list[str], pool: dict[str, Any] | None) -> list[tuple[str, int]]:
    """F5b N3: (forma, veces) de los datos declarados que suenan MÁS de una vez en el cap: su cifra/fecha (anchor) o
    una frase firma del dato. Cada dato se dice una vez; después, paráfrasis sin la cifra."""
    its = items(pool)
    seen: dict[str, int] = {}
    for i in dict.fromkeys(ids or []):
        it = its.get(i)
        if not it or it["_kind"] in ("personajes", "lugares"):
            continue
        for a in anchors(it) + signature_phrases(it):
            if it["_kind"] == "citas" or re.fullmatch(r"(19|20)\d\d", a):
                continue
            n = count_in(a, text)
            key = norm(a)
            if n > 1 and n > seen.get(key, 0):
                seen[key] = n
    # «29 de agosto de 2005» ya cubre «29 de agosto»: se informa la forma más larga
    keys = sorted(seen, key=len, reverse=True)
    return [(k, seen[k]) for k in keys if not any(k != o and k in o and seen[o] >= seen[k] for o in keys)]


_DATE_TXT = re.compile(r"\b(\d{1,2}) de (" + "|".join(MESES) + r")(?: de (\d{4}))?", re.I)


def item_date(it: dict[str, Any], default_year: str | None = None) -> str | None:
    """Fecha ISO (AAAA-MM-DD) del hecho: `fecha` completa, o la fecha escrita en su texto («29 de agosto de 2005»;
    sin año → default_year). None si no tiene día."""
    f = str(it.get("fecha") or "")
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", f):
        return f
    m = _DATE_TXT.search(text_of(it))
    y = (m.group(3) if m else None) or (f[:4] if re.match(r"\d{4}", f) else None) or default_year
    if not m or not y:
        return None
    return f"{y}-{MESES.index(m.group(2).lower()) + 1:02d}-{int(m.group(1)):02d}"


def spoken_dates(text: str, default_year: str | None = None) -> list[str]:
    """Fechas con día que dice un texto (ISO), en orden."""
    out = []
    for m in _DATE_TXT.finditer(str(text)):
        y = m.group(3) or default_year
        if y:
            out.append(f"{y}-{MESES.index(m.group(2).lower()) + 1:02d}-{int(m.group(1)):02d}")
    return out


def _figures(s: str) -> set[str]:
    """Cifras DURAS de un texto, sin separadores: no años, no días de una fecha («2 de septiembre»)."""
    t = _DATE_TXT.sub(" ", str(s))
    out = set()
    for m in re.finditer(r"\$?\d[\d.,]*\d%?|\$?\d%?", t):
        tok = m.group(0)
        if re.fullmatch(r"(19|20)\d\d", tok):
            continue
        out.add(tok.replace("$", "").replace(",", "").rstrip("."))
    return out


def same_fact(a: dict[str, Any], b: dict[str, Any]) -> bool:
    """F5b S3: dos ítems cuentan el MISMO hecho (dedupe por hecho, no por id):
    - comparten una cifra grande (≥ 3 dígitos, o con $ o %) — «650,000» de la indemnización en D50 y D72;
    - o una cifra chica + una palabra de contenido;
    - o, sin cifras, la misma fecha con día y ≥ 50 % de las palabras de contenido del más corto."""
    fa, fb = _figures(text_of(a)), _figures(text_of(b))
    common = fa & fb
    ca, cb = _content(text_of(a)), _content(text_of(b))
    if any(len(re.sub(r"\D", "", x)) >= 3 or "%" in x for x in common):
        return True
    if common and ca & cb:
        return True
    if fa or fb:
        return False
    da, db = item_date(a), item_date(b)
    return bool(da and da == db and ca and cb and len(ca & cb) / min(len(ca), len(cb)) >= 0.5)


_COMMON_CAPS = {"arrestado", "arrestada", "arrestados", "turista", "turistas", "recluso", "reclusa", "reclusos",
                "demandante", "sheriff", "alcaide", "huracán", "huracan", "adjunto", "teniente"}


def fix_glued_caps(text: str) -> str:
    """F5b N5: mayúsculas pegadas del pool a mitad de oración («…de Raphael Schwarz, Arrestado por…» → «…, arrestado
    por…»; «el Sheriff Gusman» → «el sheriff Gusman»). Solo sustantivos/participios comunes conocidos, nunca un
    nombre propio ni el arranque de una oración o de una cita."""
    def _fix(m: re.Match) -> str:
        w = m.group(2)
        return m.group(1) + (w.lower() if norm(w) in {norm(x) for x in _COMMON_CAPS} else w)
    return re.sub(r"((?<![.!?¿¡:\"«“])(?<![.!?¿¡:\"«“]\s)(?<=[\w,;]\s))([A-ZÁÉÍÓÚÑ][a-záéíóúñ]+)", _fix, text)


def resolve_declared(raw: list[Any], pool: dict[str, Any] | None, facts: list[Any] | None, text: str) -> list[str]:
    """F5b N2: lo que el narrador DECLARA en datos_usados → ids del pool. Sigue siendo lo declarado (nunca un regex
    sobre todo el pool):
    - «D07» / «[D07]» → D07;
    - «F05» (un verified_fact) → los ítems del pool que cuentan ese mismo fact (≥ 50 % de palabras de contenido en
      común) y que suenan literales en la narración;
    - un texto («1 de septiembre», «cadáveres flotando») → el ítem del pool cuyo texto o anchor lo contiene, si es
      uno solo (o el único que además suena literal)."""
    its = items(pool)
    out: list[str] = []
    for x in raw or []:
        s = str(x).strip().strip("[]«»\"'").strip()
        if not s:
            continue
        m = re.fullmatch(r"([DTQPL])\s*0*(\d+)", s, re.I)
        if m:
            i = f"{m.group(1).upper()}{int(m.group(2)):02d}"
            if i in its:
                out.append(i)
            continue
        m = re.fullmatch(r"F\s*0*(\d+)", s, re.I)
        if m:
            k = int(m.group(1)) - 1
            f = (facts or [])[k] if 0 <= k < len(facts or []) else None
            ft = str(f.get("fact") if isinstance(f, dict) else f or "")
            cf = _content(ft)
            for i, it in its.items():
                ci = _content(text_of(it))
                if it["_kind"] in ("datos", "cronologia", "citas") and cf and ci \
                        and len(cf & ci) / min(len(cf), len(ci)) >= 0.5 and used_in(text, it):
                    out.append(i)
            continue
        n = norm(s)
        cands = [i for i, it in its.items() if it["_kind"] in ("datos", "cronologia", "citas")
                 and len(n) >= 4 and (n in norm(text_of(it)) or any(n == norm(a) for a in anchors(it)))]
        if len(cands) > 1:
            cands = [i for i in cands if used_in(text, its[i])]
        if len(cands) == 1:
            out.append(cands[0])
    return list(dict.fromkeys(out))


def primary_antagonist(pool: dict[str, Any] | None) -> dict[str, Any] | None:
    """El antagonista principal: el más nombrado (por apellido) en los textos del pool."""
    ants = antagonists(pool)
    if not ants:
        return None
    blob = norm(" ".join(text_of(it) for it in items(pool).values()))
    return max(ants, key=lambda a: blob.count(norm(_surname(a["nombre"]))))


def antagonists(pool: dict[str, Any] | None) -> list[dict[str, Any]]:
    return [p for p in (pool or {}).get("personajes") or [] if p.get("antagonista")]
