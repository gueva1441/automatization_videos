"""
researcher_steps/ficha_caso.py — F12 (HANDOFF_F12 §1): la ficha del caso, los datos depurados ANTES del guion.

    entrada   data/scripts/_steps/<topic>/00_pool_v3.json (solo lectura: el pool no se toca)
    llamada   UNA a gpt-6.1-sol en esfuerzo high, con la estructura de F11c: rol y tarea en el sistema; el pool completo
              (los 509 ítems de Ycuá, con ids, doc_id y offset de cada evidencia) en el usuario, y la tarea al final
    salida    ficha_caso.json + FICHA_<tag>.md (contradicciones arriba), en _steps/<topic>/ y donde diga `out_dirs`

Secciones: personas · cronologia · hechos (60–80) · cifras (con unidad) · citas (15–25; error de transcripción
corregido con `original`) · contradicciones (versiones lado a lado con doc_id y offset; NO se resuelven) · descartados.

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
PROMPT_VERSION = "f12-1"
MAX_LEV = 3
SECCIONES = ("contradicciones", "personas", "cifras", "cronologia", "hechos", "citas", "descartados")

_IDS = {"type": "ARRAY", "items": {"type": "STRING"}}
SCHEMA: dict[str, Any] = {
    "type": "OBJECT",
    "properties": {
        "personas": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "nombre": {"type": "STRING"}, "rol": {"type": "STRING"},
            "variantes": {"type": "ARRAY", "items": {"type": "STRING"}}, "ids": _IDS},
            "required": ["nombre", "rol", "variantes", "ids"]}},
        "cronologia": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "fecha": {"type": "STRING"}, "hora": {"type": "STRING"}, "evento": {"type": "STRING"}, "ids": _IDS},
            "required": ["fecha", "hora", "evento", "ids"]}},
        "hechos": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "texto": {"type": "STRING"}, "ids": _IDS}, "required": ["texto", "ids"]}},
        "cifras": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "que": {"type": "STRING"}, "valor": {"type": "STRING"}, "unidad": {"type": "STRING"},
            "fuente": {"type": "STRING"}, "ids": _IDS,
            "otras_versiones": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
                "valor": {"type": "STRING"}, "unidad": {"type": "STRING"}, "fuente": {"type": "STRING"}, "ids": _IDS},
                "required": ["valor", "unidad", "fuente", "ids"]}}},
            "required": ["que", "valor", "unidad", "fuente", "ids", "otras_versiones"]}},
        "citas": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "autor": {"type": "STRING"}, "rol": {"type": "STRING"}, "verificacion": {"type": "STRING"},
            "texto": {"type": "STRING"}, "original": {"type": "STRING"}, "ids": _IDS},
            "required": ["autor", "rol", "verificacion", "texto", "original", "ids"]}},
        "contradicciones": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "tema": {"type": "STRING"},
            "versiones": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
                "dice": {"type": "STRING"}, "doc_id": {"type": "STRING"}, "offset": {"type": "INTEGER"}, "ids": _IDS},
                "required": ["dice", "doc_id", "offset", "ids"]}}},
            "required": ["tema", "versiones"]}},
        "descartados": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "que": {"type": "STRING"}, "motivo": {"type": "STRING"}, "ids": _IDS},
            "required": ["que", "motivo", "ids"]}},
    },
    "required": ["personas", "cronologia", "hechos", "cifras", "citas", "contradicciones", "descartados"],
}


# ═══════════════════════════════════════════════════════════════
#  Prompt (estructura de F11c: sistema = rol + tarea; usuario = datos + tarea al final)
# ═══════════════════════════════════════════════════════════════

def system() -> str:
    return """<rol>Sos el documentalista de Misterios Sepultados, un canal de documentales de historia oscura en YouTube. Antes de que el guionista escriba, depurás el research de un caso real y armás su ficha: la única fuente de la escaleta y del guion. Lo que no está en la ficha no existe para ellos.</rol>
<tarea>
Leés el pool de research completo (cada ítem con su id, y cada evidencia con su documento y su posición) y devolvés la ficha del caso:
- personas: un nombre canónico por persona, su rol, las variantes del nombre que encontraste y sus ids. Si dos fuentes dan nombres distintos para la misma persona, no elegís: la persona va también a contradicciones.
- cronologia: los eventos del día en orden, con la fecha y la hora tal como están en el pool, y sus ids.
- hechos: entre 60 y 80 hechos útiles para contar la historia, cada uno en una oración limpia, con sus ids de origen. Sin interpretación.
- cifras: una cifra por conteo (muertos, heridos, huérfanos, personas adentro…), con su fuente y las otras versiones. Cada cifra con su unidad (personas, °C, años, guaraníes…): nunca un número sin qué cuenta.
- citas: las mejores 15 a 25, con autor, rol, estado de verificación y el texto. Si hay un error evidente de transcripción, lo corregís en «texto» y dejás el texto del pool en «original»; si no corregís nada, «original» va vacío.
- contradicciones: cada conflicto entre fuentes (nombres, cifras, fechas, roles), con las versiones lado a lado, cada una con su doc_id y su offset tal como están en la evidencia. No resolvés nada: decide el productor.
- descartados: lo que dejás afuera por dudoso o fuera del caso, con el motivo en una línea.
En el pool, una evidencia que ya apareció en otro ítem va como «(= arriba)»: es el mismo pasaje del mismo documento.
Cada cifra, hora, fecha y cita que escribas tiene que estar en el texto de los ids que citás. No agregás nada que no esté en el pool.
</tarea>"""


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
    return "\n".join(out)


def prompt(pool: dict, title: str) -> str:
    return f"""<caso>{title}</caso>

<pool>
{pool_section(pool)}
</pool>

<tarea>Con el pool de arriba, armá la ficha del caso: personas, cronologia, hechos (60–80), cifras (con unidad), citas (15–25), contradicciones (sin resolver, con doc_id y offset) y descartados. Devolvé el JSON del esquema.</tarea>"""


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


def numbers(text: str) -> set[str]:
    return {f for t in _NUM.findall(text or "") for f in _num_forms(t)}


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
    rest = _ISO.sub(" ", _HORA.sub(" ", _ID.sub(" ", text or "")))
    src_n = numbers(src)
    for tok in _NUM.findall(rest):
        if not (_num_forms(tok) & src_n):
            out.append(f"cifra {tok}")
    return out


def _strings(x: Any, skip: tuple[str, ...] = ("ids", "original", "doc_id", "offset")) -> list[str]:
    if isinstance(x, dict):
        return [s for k, v in x.items() if k not in skip for s in _strings(v, skip)]
    if isinstance(x, list):
        return [s for v in x for s in _strings(v, skip)]
    return [str(x)] if isinstance(x, (str, int, float)) and str(x) else []


def problems(section: str, item: dict, its: dict) -> list[str]:
    """Por qué un ítem de la ficha no está respaldado ([] = está)."""
    ids = list(item.get("ids") or [])
    if section == "contradicciones":
        ids = [i for v in item.get("versiones") or [] for i in v.get("ids") or []]
    if not ids:
        return ["sin ids"]
    bad = [i for i in ids if i not in its]
    if bad:
        return [f"id inexistente {', '.join(bad)}"]
    if section == "descartados":
        return []
    out: list[str] = []
    if section == "contradicciones":
        for v in item.get("versiones") or []:
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
    out: dict[str, list] = {s: [] for s in SECCIONES}
    sacados: list[dict] = []
    for s in SECCIONES:
        for item in ficha.get(s) or []:
            pr = problems(s, item, its)
            if not pr:
                out[s].append(item)
                continue
            ids = item.get("ids") or [i for v in item.get("versiones") or [] for i in v.get("ids") or []]
            rec = {"que": f"[{s}] {_label(s, item)}", "motivo": "no respaldado: " + "; ".join(pr),
                   "ids": [i for i in ids if i in its], "seccion": s, "item": item}
            sacados.append(rec)
            out["descartados"].append({k: rec[k] for k in ("que", "motivo", "ids")})
    return out, sacados


def _label(s: str, item: dict) -> str:
    key = {"personas": "nombre", "cronologia": "evento", "hechos": "texto", "cifras": "que", "citas": "texto",
           "contradicciones": "tema", "descartados": "que"}[s]
    return str(item.get(key) or "")[:140]


# ═══════════════════════════════════════════════════════════════
#  Corrida y salidas
# ═══════════════════════════════════════════════════════════════

def build(pool: dict, title: str, *, call: Callable[..., dict]) -> dict:
    return call(prompt(pool, title), system_instruction=system(), response_schema=SCHEMA,
                description="ficha_caso")


def counts(ficha: dict) -> dict[str, int]:
    return {s: len(ficha.get(s) or []) for s in SECCIONES}


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
    L += ["## Contradicciones (decide Omar)", ""]
    for x in ficha["contradicciones"]:
        L.append(f"**{x.get('tema')}**")
        for v in x.get("versiones") or []:
            L.append(f"- {v.get('dice')} <sub>{v.get('doc_id')}@{v.get('offset')} · {', '.join(v.get('ids') or [])}</sub>")
        L.append("")
    L += ["## Personas", ""]
    for x in ficha["personas"]:
        var = [v for v in x.get("variantes") or [] if v != x.get("nombre")]
        L.append(f"- **{x.get('nombre')}** — {x.get('rol')}" + (f" (también: {', '.join(var)})" if var else "")
                 + _ids(x))
    L += ["", "## Cifras", ""]
    for x in ficha["cifras"]:
        L.append(f"- **{x.get('que')}:** {x.get('valor')} {x.get('unidad')} · {x.get('fuente')}" + _ids(x))
        for v in x.get("otras_versiones") or []:
            L.append(f"  - otra versión: {v.get('valor')} {v.get('unidad')} · {v.get('fuente')}"
                     f" <sub>{', '.join(v.get('ids') or [])}</sub>")
    L += ["", "## Cronología", ""]
    for x in ficha["cronologia"]:
        h = f" {x.get('hora')}" if x.get("hora") and str(x.get("hora")).lower() not in ("null", "none") else ""
        L.append(f"- **{x.get('fecha')}{h}** — {x.get('evento')}" + _ids(x))
    L += ["", "## Hechos", ""]
    L += [f"{k}. {x.get('texto')}{_ids(x)}" for k, x in enumerate(ficha["hechos"], 1)]
    L += ["", "## Citas", ""]
    for x in ficha["citas"]:
        fix = f" <sub>(original: «{x.get('original')}»)</sub>" if x.get("original") and x["original"] != x.get("texto") else ""
        L.append(f"- «{x.get('texto')}» — **{x.get('autor')}**, {x.get('rol')} · {x.get('verificacion')}{fix}{_ids(x)}")
    L += ["", "## Descartados", ""]
    L += [f"- {x.get('que')} — {x.get('motivo')}{_ids(x)}" for x in ficha["descartados"]]
    return "\n".join(L) + "\n"


def run(topic_id: str, *, steps_dir: Path, title: str, tag: str, out_dirs: list[Path] = (),
        call: Callable[..., dict] | None = None) -> dict:
    """Lee el pool, hace UNA llamada, chequea y escribe ficha_caso.json + FICHA_<tag>.md en `_steps/<topic>/` y en
    cada `out_dirs`. `call` por defecto: gpt-6.1-sol high."""
    raw_pool = (steps_dir / topic_id / "00_pool_v3.json").read_bytes()
    pool = json.loads(raw_pool.decode("utf-8"))
    if call is None:
        import gpt_helpers
        call = gpt_helpers.make_call(MODELO, ESFUERZO)
    raw = build(pool, title, call=call) or {}
    return save(topic_id, raw, raw_pool, steps_dir=steps_dir, title=title, tag=tag, out_dirs=out_dirs)


def save(topic_id: str, raw: dict, raw_pool: bytes, *, steps_dir: Path, title: str, tag: str,
         out_dirs: list[Path] = (), usd: float | None = None) -> dict:
    """Chequeo determinista sobre la salida del modelo (`raw`) y escritura de ficha_caso.json + FICHA_<tag>.md.
    Re-aplicable sobre un crudo guardado, sin otra llamada."""
    pool = json.loads(raw_pool.decode("utf-8"))
    ficha, sacados = check(raw, pool)
    from cost_tracker import cost_tracker
    cv = cost_tracker.current_video
    meta = {"topic": topic_id, "titulo": title, "modelo": MODELO, "esfuerzo": ESFUERZO,
            "prompt_version": PROMPT_VERSION, "pool_md5": hashlib.md5(raw_pool).hexdigest(),
            "conteos_crudo": counts(raw), "conteos": counts(ficha), "sacados": len(sacados),
            "usd": usd if usd is not None else (round(cv.total_cost, 4) if cv else 0.0)}
    out = {**meta, **ficha, "chequeo": {"sacados": sacados}}
    md = markdown(ficha, meta)
    for d in [steps_dir / topic_id, *out_dirs]:
        d.mkdir(parents=True, exist_ok=True)
        (d / "ficha_caso.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
        (d / f"FICHA_{tag}.md").write_text(md, encoding="utf-8")
    return {"ficha": ficha, "meta": meta, "sacados": sacados, "crudo": raw}
