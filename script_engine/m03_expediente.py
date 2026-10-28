"""F50 B — el expediente por foto del pedido de casilleros (m03): por cada ancla, el año dicho, dónde, el párrafo de la
voz, las escenas de la ficha, los hechos, las citas y las personas de su beat, y al final los grupos de gente del canon.
Es el de la candidata de F46b–F49 (lab: `f46b.expedientes` + `f48.extra_por_foto` y `f48.bloque` en S5), portado sin
cambiar lo que se midió; el único cambio es la regla 3 del año de respaldo: el último año dicho en la NARRACIÓN de los
caps anteriores (en producción los caps corren en paralelo y las anclas de otros caps todavía no existen)."""
from __future__ import annotations

import json
import re
from pathlib import Path

from script_engine import m03_imagenes_v3 as v3img

# el texto del lab, tal cual (F46b texto 3)
TEXTO_3_ENCABEZADO = ("CASE FILE PER IMAGE — documented data. Use it to make each image specific to its place, year and "
                      "people; do not invent beyond it.")
_SEP = "═══════════════════════════════════════════════════"


def _j(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else {}


def fuentes(topic_id: str, steps_dir: Path) -> dict:
    """Lo que lee el expediente de `_steps/<id>/`: la escaleta (dato_central y datos_apoyo de cada beat), la ficha
    (escenas) y los párrafos de la narración v3."""
    d = steps_dir / topic_id
    return {"esc": _j(d / "01a_escaleta.json"), "ficha": _j(d / "ficha_caso.json"),
            "parrafos": _j(d / "01b_narracion_v3.json").get("parrafos") or []}


def anio_del_texto(texto: str) -> str | None:
    """Primer año de 1800–2100 dicho en el texto: la primera cláusula que trae uno (`voz_utils.numeros` no devuelve
    las cifras en orden de aparición; por cláusula sí queda el orden)."""
    from script_engine import voz_utils as vu
    for cl in re.split(r"[.;:,¿?¡!]", texto or ""):
        ys = [y for y in vu.numeros(cl) if re.fullmatch(r"\d{4}", y) and 1800 <= int(y) <= 2100]   # derivado: F48
        if ys:
            return ys[0]
    return None


def anio_previo(narr_chapters: list[dict], cap: int) -> str | None:
    """Regla 3 del año: el último año dicho en la narración de los caps anteriores a `cap` (por cláusula, en orden)."""
    ultimo = None
    for ch in sorted(narr_chapters or [], key=lambda c: c.get("chapter_number") or 0):
        if (ch.get("chapter_number") or 0) >= cap:
            break
        for cl in re.split(r"[.;:,¿?¡!]", ch.get("narration") or ""):
            ultimo = anio_del_texto(cl) or ultimo
    return ultimo


def _sale_entero(nombre: str, texto: str) -> bool:
    return bool(re.search(rf"\b{re.escape(nombre)}\b", texto or "", re.I))


def expedientes(topic: dict, fu: dict, cap_beats: list[dict], anchors: list[str], assign: list[dict],
                anio_prev: str | None, year_topic: str) -> list[dict]:
    """Un expediente por ancla (en el orden del pedido)."""
    pool = topic.get("evidence_pool") or {}
    lugares = {l["id"]: l.get("nombre") for l in pool.get("lugares") or []}
    crono = {t["id"]: t for t in pool.get("cronologia") or []}
    citas = {q["id"]: q for q in pool.get("citas") or []}
    pers = {p["id"]: p for p in pool.get("personajes") or []}
    datos = {x["id"]: x for x in pool.get("datos") or []}
    esc_beats = {b["n"]: b for b in (fu.get("esc") or {}).get("beats") or []}
    by_n = {b["n"]: b for b in cap_beats or []}
    parrafos = fu.get("parrafos") or []
    out = []
    for i, (ancla, a) in enumerate(zip(anchors, assign), start=1):
        bn = a.get("beat")
        b = by_n.get(bn) or {}
        eb = esc_beats.get(bn) or {}
        ids = [x for x in [eb.get("dato_central"), *(eb.get("datos_apoyo") or [])] if x]
        clave = v3img._norm_ws(ancla)[:40]
        par = next((p["texto"] for p in parrafos if clave and clave in v3img._norm_ws(p.get("texto") or "")),
                   next((p["texto"] for p in parrafos if p.get("beat") == bn), ""))
        escenas = [e for e in (fu.get("ficha") or {}).get("escenas") or [] if set(e.get("ids") or []) & set(ids)]
        donde: list[str] = []
        for x in [*((crono.get(i_) or {}).get("lugar") for i_ in ids), *(lugares.get(i_) for i_ in ids),
                  *(e.get("donde") for e in escenas)]:
            if x and x not in donde:
                donde.append(x)
        facts = []
        for x in ids:
            if x in datos and datos[x].get("texto"):
                facts.append(datos[x]["texto"])
            if x in crono and crono[x].get("evento"):
                facts.append(f"{crono[x].get('fecha') or '-'} · {crono[x]['evento']}")
        quien = [pers[x] for x in ids if x in pers]
        quien += [p for p in pers.values() if p not in quien and _sale_entero(p["nombre"], ancla)]
        if anio_prev:
            respaldo = (anio_prev, "3) el último año dicho en la narración de los caps anteriores")
        elif re.match(r"\d{4}", b.get("fecha") or ""):
            respaldo = (b["fecha"][:4], "4) la fecha del dato_central del beat")
        else:
            respaldo = (year_topic, "5) topic_year")
        out.append({
            "foto": i, "ancla": ancla, "parrafo": par, "beat": bn, "donde": donde,
            "escenas": [" · ".join(str(e.get(k) or "") for k in ("donde", "quien", "que_pasa", "sentidos")) for e in escenas],
            "facts": facts,
            "citas": [citas[x].get("texto") for x in ids if x in citas],
            "people3": [f"{(p.get('rol') or '').strip().rstrip('.')} · {p.get('lugar') or '-'} · "
                        f"{', '.join(p.get('fechas_presente') or []) or '-'}" for p in quien],
            "anio_ancla": anio_del_texto(ancla), "respaldo": respaldo})
    return out


def bloque(exps: list[dict], people_groups: list[dict]) -> str:
    """El bloque de texto del expediente (= lab `f48.bloque` en S5)."""
    L = ["", _SEP, TEXTO_3_ENCABEZADO, _SEP]
    for e in exps:
        L += [f"  [{e['foto']}] YEAR: {e.get('anio_ancla') or '-'} · WHERE: {'; '.join(e['donde']) or '-'}",
              f"      PARAGRAPH: «{e['parrafo']}»",
              f"      SCENES: {' | '.join('«' + s + '»' for s in e['escenas']) or '-'}",
              f"      FACTS: {' | '.join('«' + q + '»' for q in e['facts']) or '-'}",
              f"      QUOTES: {' | '.join('«' + q + '»' for q in e['citas']) or '-'}",
              f"      PEOPLE (role · where · years): {'; '.join(e['people3']) or '-'}"]
    L += ["PEOPLE GROUPS:"]
    for g in people_groups or []:
        L.append(f"  - {g.get('id')}: {g.get('who') or ''} · {g.get('where_when') or ''}")
    return "\n".join(L) + "\n"
