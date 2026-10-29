"""F50 B — el expediente por foto del pedido de casilleros (m03): por cada ancla, el año dicho, dónde, el párrafo de la
voz, las escenas de la ficha, los hechos, las citas (con autor) y las personas que nombra el ancla (desde la ficha; si no
nombra a nadie, las de la última ancla del mismo párrafo), y al final los grupos de gente del canon con aspecto y ropa.
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


_ANIO4 = re.compile(r"\b(1[89]\d\d|20\d\d)\b")
ARRASTRE = " (named earlier in the paragraph)"   # F50c A: texto literal del handoff (dato, no regla)


def _formas(persona: dict) -> list[str]:
    """F50c A: `nombre` y cada `variantes[]` de la ficha, sin lo que va entre paréntesis."""
    return [f for f in (re.sub(r"\s*\(.*?\)", "", str(x or "")).strip()
                        for x in [persona.get("nombre"), *(persona.get("variantes") or [])]) if f]


def _calificativo(persona: dict) -> str:
    m = re.search(r"\((.*?)\)", persona.get("nombre") or "")
    return m.group(1).strip().lower() if m else ""


def _anios_persona(persona: dict, excluir: set, pool: dict) -> set[int]:
    """Años de 4 cifras de `fechas_presente` de sus ids P y de `fecha` de sus ids de cronología y datos, sin `excluir`."""
    tablas = [{x["id"]: x for x in pool.get(k) or []} for k in ("personajes", "cronologia", "datos")]
    ys: set[int] = set()
    for i in set(persona.get("ids") or []) - excluir:
        p, t, d = (tb.get(i) or {} for tb in tablas)
        for f in [*(p.get("fechas_presente") or []), t.get("fecha"), d.get("fecha")]:
            ys |= {int(y) for y in _ANIO4.findall(str(f or ""))}
    return ys


def personas_del_ancla(ancla: str, anio: int | None, ficha_personas: list[dict], pool: dict) -> tuple[list, list]:
    """F50c A: las personas de la ficha que nombra el ancla. Por persona vale su forma más larga que aparece (palabra
    entera, sin mayúsculas). Una forma de varias personas: gana la que el ancla sigue con su calificativo («Daniel Écija
    hijo» → «(hijo)»); si no, la de años más cerca del año de la foto (sin los ids que comparten); empate o sin año:
    nadie. Devuelve (personas en el orden de la ficha, formas sin resolver)."""
    por_forma: dict[str, list[dict]] = {}
    for p in ficha_personas or []:
        hay = [f for f in _formas(p) if re.search(rf"\b{re.escape(f)}\b", ancla or "", re.I)]
        if hay:
            por_forma.setdefault(max(hay, key=len).lower(), []).append(p)
    out, dudas = [], []
    for forma, ps in por_forma.items():
        if len(ps) == 1:
            out.append(ps[0])
            continue
        q = [p for p in ps if _calificativo(p)
             and re.search(rf"\b{re.escape(forma)}\W+{re.escape(_calificativo(p))}\b", ancla, re.I)]
        if len(q) == 1:
            out.append(q[0])
            continue
        comunes = set.intersection(*[set(p.get("ids") or []) for p in ps])
        if anio is not None:
            d = sorted((min((abs(anio - y) for y in _anios_persona(p, comunes, pool)), default=10**4), k)
                       for k, p in enumerate(ps))
            if d[0][0] < d[1][0]:
                out.append(ps[d[0][1]])
                continue
        dudas.append(forma)
    unicas: list[dict] = []
    for p in out:
        if p not in unicas:
            unicas.append(p)
    return unicas, dudas


def linea_persona(persona: dict, pers_pool: dict) -> str:
    """`rol de la ficha · lugar · años`: lugar y años del primer id P de la persona que los tenga en el pool."""
    ps = [pers_pool[i] for i in persona.get("ids") or [] if i in pers_pool]
    lugar = next((p["lugar"] for p in ps if p.get("lugar")), None)
    anios = next((p["fechas_presente"] for p in ps if p.get("fechas_presente")), None)
    return f"{(persona.get('rol') or '').strip().rstrip('.')} · {lugar or '-'} · {', '.join(anios or []) or '-'}"


def linea_cita(q: dict) -> str:
    """F50c B: `«texto» — autor · rol` + ` · fecha` si la trae + ` · witness` si `testigo`."""
    quien = " · ".join(x for x in (str(q.get("autor") or "").strip(),
                                   str(q.get("rol") or "").strip().rstrip(".")) if x)
    return (f"«{q.get('texto')}»" + (f" — {quien}" if quien else "") + (f" · {q['fecha']}" if q.get("fecha") else "")
            + (" · witness" if q.get("testigo") is True else ""))


def expedientes(topic: dict, fu: dict, cap_beats: list[dict], anchors: list[str], assign: list[dict],
                anio_prev: str | None, year_topic: str) -> list[dict]:
    """Un expediente por ancla (en el orden del pedido)."""
    pool = topic.get("evidence_pool") or {}
    lugares = {l["id"]: l.get("nombre") for l in pool.get("lugares") or []}
    crono = {t["id"]: t for t in pool.get("cronologia") or []}
    citas = {q["id"]: q for q in pool.get("citas") or []}
    pers = {p["id"]: p for p in pool.get("personajes") or []}
    ficha_personas = (fu.get("ficha") or {}).get("personas") or []
    nombro: dict[str, list[dict]] = {}          # párrafo → personas de la última ancla que nombró a alguien
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
        if anio_prev:
            respaldo = (anio_prev, "3) el último año dicho en la narración de los caps anteriores")
        elif re.match(r"\d{4}", b.get("fecha") or ""):
            respaldo = (b["fecha"][:4], "4) la fecha del dato_central del beat")
        else:
            respaldo = (year_topic, "5) topic_year")
        anio_ancla = anio_del_texto(ancla)
        a0 = str(anio_ancla or respaldo[0] or "")
        quien, dudas = personas_del_ancla(ancla, int(a0) if a0.isdigit() else None, ficha_personas, pool)
        fuente = "ancla" if quien else None
        if quien:
            nombro[par] = quien
        elif nombro.get(par):                              # arrastre dentro del mismo párrafo, nunca entre párrafos
            quien, fuente = nombro[par], "arrastre"
        out.append({
            "foto": i, "ancla": ancla, "parrafo": par, "beat": bn, "donde": donde,
            "escenas": [" · ".join(str(e.get(k) or "") for k in ("donde", "quien", "que_pasa", "sentidos")) for e in escenas],
            "facts": facts,
            "citas": [linea_cita(citas[x]) for x in ids if x in citas],
            "people3": [linea_persona(p, pers) + (ARRASTRE if fuente == "arrastre" else "") for p in quien],
            "personas": [p.get("nombre") for p in quien], "personas_fuente": fuente, "personas_dudas": dudas,
            "anio_ancla": anio_ancla, "respaldo": respaldo})
    return out


def bloque(exps: list[dict], people_groups: list[dict]) -> str:
    """El bloque de texto del expediente (= lab `f48.bloque` en S5)."""
    L = ["", _SEP, TEXTO_3_ENCABEZADO, _SEP]
    for e in exps:
        L += [f"  [{e['foto']}] YEAR: {e.get('anio_ancla') or '-'} · WHERE: {'; '.join(e['donde']) or '-'}",
              f"      PARAGRAPH: «{e['parrafo']}»",
              f"      SCENES: {' | '.join('«' + s + '»' for s in e['escenas']) or '-'}",
              f"      FACTS: {' | '.join('«' + q + '»' for q in e['facts']) or '-'}",
              f"      QUOTES: {' | '.join(e['citas']) or '-'}",
              f"      PEOPLE (role · where · years): {'; '.join(e['people3']) or '-'}"]
    L += ["PEOPLE GROUPS:"]
    for g in people_groups or []:
        L.append(f"  - {g.get('id')}: {g.get('who') or ''} · {g.get('where_when') or ''}"     # F50c C: + aspecto y ropa
                 f" · APPEARANCE: {g.get('appearance') or '-'} · CLOTHING: {g.get('clothing') or '-'}")
    return "\n".join(L) + "\n"
