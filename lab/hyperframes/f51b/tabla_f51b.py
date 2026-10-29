# -*- coding: utf-8 -*-
"""F51b — tabla del canon de Wittenoom viejo → nuevo, sin juicio: solo los textos y el diff.
1. `people_groups` por `id`: appearance viejo · appearance nuevo · condition_by_period nuevo · estado (igual /
   cambia / nuevo / desaparece).
2. Lo demás del canon: `era_visual_canon` (claves sueltas y `periods` por tramo), `anachronism_blocklist`,
   `documented_people` (appearance_canon por name), `documented_props` (por nombre) y `central_subject` campo por campo.
3. Las fotos 2/9, 4/11, 4/12 y 5/8 armadas en memoria con el código de producción (`f50g/rearmar.rearmar_una`, como
   `f51a/contrato.py`) con los grupos del canon nuevo, al lado del C′ de F50i (`PROMPTS_F50i.json → Cp`) y el diff
   palabra por palabra. Sin modelos, sin fal; solo lee (03_visual.json, topics_db y 05_visual_canon.json intactos).

Uso:
  python lab/hyperframes/f51b/tabla_f51b.py                       # nuevo = f51b/canon_f51b.json
  python lab/hyperframes/f51b/tabla_f51b.py --nuevo <ruta.json>   # otro canon como nuevo (prueba: antes/05_visual_canon.json)
Escribe lab/hyperframes/f51b/CANON_F51b.md.
"""
import argparse
import difflib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "lab" / "hyperframes" / "f50g"))
F51B = Path(__file__).resolve().parent
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
VIEJO = F51B / "antes" / "05_visual_canon.json"
NUEVO = F51B / "canon_f51b.json"
F50I = ROOT / "lab" / "hyperframes" / "f50i" / "PROMPTS_F50i.json"
SALIDA = F51B / "CANON_F51b.md"
FOTOS = ("2/9", "4/11", "4/12", "5/8")


def leer(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def rel(p: Path) -> str:
    try:
        return p.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return str(p)


def celda(x) -> str:
    """Texto de una celda: listas/dicts en JSON, sin saltos ni barras sueltas."""
    if x is None or x == "" or x == []:
        return "—"
    s = x if isinstance(x, str) else json.dumps(x, ensure_ascii=False)
    return s.replace("\n", " ").replace("|", "\\|")


def por(lista, clave: str) -> dict:
    return {d[clave]: d for d in lista or [] if isinstance(d, dict) and d.get(clave)}


def estado(k, viejo: dict, nuevo: dict) -> str:
    return "nuevo" if k not in viejo else "desaparece" if k not in nuevo else "igual"


def claves(viejo: dict, nuevo: dict) -> list:
    return list(viejo) + [k for k in nuevo if k not in viejo]


def diff_palabras(a: str, b: str) -> str:
    return " ".join(d for d in difflib.ndiff(a.split(), b.split()) if d[0] in "+-")


def condicion(g: dict | None) -> str:
    cbp = (g or {}).get("condition_by_period") or []
    return "; ".join(f"{c.get('years', '')}: {c.get('condition', '')}" for c in cbp if isinstance(c, dict))


def tabla_grupos(cv: dict, cn: dict) -> list[str]:
    gv, gn = por(cv.get("people_groups"), "id"), por(cn.get("people_groups"), "id")
    L = ["| id | estado | appearance viejo | appearance nuevo | condition_by_period nuevo |", "|---|---|---|---|---|"]
    for k in claves(gv, gn):
        v, n = gv.get(k), gn.get(k)
        e = estado(k, gv, gn)
        if e == "igual" and (v.get("appearance") != n.get("appearance") or condicion(v) != condicion(n)):
            e = "cambia"                                   # está en los dos, con otro appearance o condition
        L.append(f"| {k} | {e} | {celda((v or {}).get('appearance'))} | "
                 f"{celda((n or {}).get('appearance'))} | {celda(condicion(n))} |")
    return L


def diff_dicts(v: dict, n: dict, saltar=()) -> list[str]:
    """Campo por campo: «igual» si nada cambió; si no, una línea por campo distinto."""
    L = []
    for k in claves(v, n):
        if k in saltar or v.get(k) == n.get(k):
            continue
        quien = "agregado" if k not in v else "quitado" if k not in n else "cambia"
        L.append(f"- `{k}` ({quien}): {celda(v.get(k))} → {celda(n.get(k))}")
    return L or ["igual"]


def diff_por_clave(v_lista, n_lista, clave: str, campos=None) -> list[str]:
    """Lista de dicts por `clave`: agregados, quitados y, de los que siguen, los campos que cambian."""
    v, n = por(v_lista, clave), por(n_lista, clave)
    L = []
    for k in claves(v, n):
        e = estado(k, v, n)
        if e == "nuevo":
            L.append(f"- **{k}** (agregado): {celda(n[k] if campos is None else {c: n[k].get(c) for c in campos})}")
        elif e == "desaparece":
            L.append(f"- **{k}** (quitado): {celda(v[k] if campos is None else {c: v[k].get(c) for c in campos})}")
        else:
            a = v[k] if campos is None else {c: v[k].get(c) for c in campos}
            b = n[k] if campos is None else {c: n[k].get(c) for c in campos}
            d = diff_dicts(a, b)
            if d != ["igual"]:
                L += [f"- **{k}**:"] + ["  " + x for x in d]
    return L or ["igual"]


def resto(cv: dict, cn: dict) -> list[str]:
    ev, en = cv.get("era_visual_canon") or {}, cn.get("era_visual_canon") or {}
    L = ["### era_visual_canon (claves sueltas, sin periods)", "", *diff_dicts(ev, en, saltar=("periods",)), "",
         "### era_visual_canon.periods (por years: years y clothing)", "",
         *diff_por_clave(ev.get("periods"), en.get("periods"), "years", ("years", "clothing")), "",
         "### anachronism_blocklist", ""]
    bv, bn = cv.get("anachronism_blocklist") or [], cn.get("anachronism_blocklist") or []
    if bv == bn:
        L.append("igual")
    else:
        L += [f"- quitado: {x}" for x in bv if x not in bn] + [f"- agregado: {x}" for x in bn if x not in bv]
        if set(bv) == set(bn):
            L.append("- mismos ítems, otro orden")
    L += ["", "### documented_people (por name: appearance_canon)", "",
          *diff_por_clave(cv.get("documented_people"), cn.get("documented_people"), "name", ("appearance_canon",)),
          "", "### documented_props (por nombre: nombre · forma · anclado · foto_madre)", "",
          *diff_por_clave(cv.get("documented_props"), cn.get("documented_props"), "nombre"),
          "", "### central_subject (campo por campo)", "",
          *diff_dicts(cv.get("central_subject") or {}, cn.get("central_subject") or {})]
    return L


def prompts(cn: dict) -> list[str]:
    import rearmar as rg
    from script_engine import m03_imagenes_v3 as v3
    from script_engine.topics_db import get_topic_by_id
    vivo = leer(rg.VISUAL)
    topic = get_topic_by_id(TID)
    beats = v3.load_beats(topic, rg.STEPS)
    grupos = por(cn.get("people_groups"), "id")
    items = {f"{c['chapter_number']}/{i}": it for c in vivo["chapters"] for i, (it, _) in enumerate(rg.fotos(c), 1)}
    f50i = {f["foto"]: f for f in leer(F50I)}
    L = []
    for foto in FOTOS:
        it = items[foto]
        cap = int(foto.split("/")[0])
        by_n = {b["n"]: b for b in beats.get(cap) or []}
        escala = bool((by_n.get(it.get("beat")) or {}).get("escala"))
        p, _ = rg.rearmar_una(it, escala, topic.get("documented_people"), grupos)
        cp = f50i[foto]["Cp"]
        pg = [g for g in json.loads(it["raw_llm_prompt"]).get("people_group") or [] if isinstance(g, str)]
        igual = p.encode("utf-8") == cp.encode("utf-8")
        L += [f"### {foto} · {', '.join(pg) or '—'} · palabras C′ {len(cp.split())} → nuevo {len(p.split())}", "",
              f"Byte a byte igual a C′ de F50i: **{'sí' if igual else 'no'}**", "",
              f"Diff palabra por palabra (- C′ de F50i, + nuevo): {diff_palabras(cp, p) or '—'}", "",
              "**C′ (F50i)**", "", "```", cp, "```", "", "**Nuevo (canon nuevo)**", "", "```", p, "```", ""]
    return L


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--nuevo", type=Path, default=NUEVO)
    a = ap.parse_args()
    if not a.nuevo.exists():
        print(f"no existe {rel(a.nuevo)}")
        return 1
    cv, cn = leer(VIEJO), leer(a.nuevo)
    cmd = "python lab/hyperframes/f51b/tabla_f51b.py" + ("" if a.nuevo.resolve() == NUEVO.resolve()
                                                         else f" --nuevo {rel(a.nuevo)}")
    L = ["# CANON_F51b — canon de Wittenoom viejo → nuevo, y 4 fotos armadas con el nuevo", "",
         f"Salida de `{cmd}`. Viejo = `{rel(VIEJO)}`, nuevo = `{rel(a.nuevo)}`. Sin modelos, sin fal; nada de "
         "producción se escribe. Solo los textos y el diff, sin juicio.", "",
         f"- `canon_ficha_md5` viejo: `{cv.get('canon_ficha_md5')}`",
         f"- `canon_ficha_md5` nuevo: `{cn.get('canon_ficha_md5')}`", "",
         "## 1. people_groups por id", "", *tabla_grupos(cv, cn), "",
         "## 2. Lo demás del canon (viejo → nuevo)", "", *resto(cv, cn), "",
         "## 3. Prompts armados con el canon nuevo (en memoria) al lado del C′ de F50i", "",
         "Código de producción como `f51a/contrato.py`: `rg.fotos(cap)` sobre el 03_visual.json vivo (solo lectura), "
         "`escala` del beat, `rg.rearmar_una(it, escala, topic['documented_people'], grupos)` con `grupos` = "
         "`people_groups` del canon nuevo; `topic` = `get_topic_by_id` (topics_db vivo).", "", *prompts(cn)]
    SALIDA.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
