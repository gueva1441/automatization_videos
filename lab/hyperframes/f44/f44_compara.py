# -*- coding: utf-8 -*-
"""F44 · tabla A/B de la ficha del caso. Solo lee JSON, sin API, sin escribir fuera de lab/hyperframes/f44/.

Uso:
  python lab/hyperframes/f44/f44_compara.py                      # defaults (A de lab, o producción si no está; B de lab)
  python lab/hyperframes/f44/f44_compara.py --a-dir DIR --b-dir DIR [--costos costos.json] [--out TABLA_AB.md]
Cada dir tiene ficha_caso.json y 01a_escaleta.json. Imprime el Markdown y lo guarda en TABLA_AB.md.
"""
import argparse
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]
F44 = RAIZ / "lab" / "hyperframes" / "f44"
TOPIC = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
PROD = RAIZ / "data" / "scripts" / "_steps" / TOPIC
ND = "—"


def cargar(d, nombre):
    p = Path(d) / nombre
    if not p.exists():
        return None
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:  # json roto: se avisa y se sigue
        print(f"⚠ no pude leer {p}: {e}", file=sys.stderr)
        return None


def get(o, *ks):
    for k in ks:
        if isinstance(o, dict) and k in o:
            o = o[k]
        else:
            return None
    return o


def cel(v, n=None):
    """Celda segura: «—» si falta, recorta, escapa | y saltos de línea."""
    if v is None or v == "" or v == []:
        return ND
    if not isinstance(v, str):
        v = json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else str(v)
    v = " ".join(v.split())
    if n and len(v) > n:
        v = v[: n - 1].rstrip() + "…"
    return v.replace("|", "\\|")


def txt(v, n=None):
    """Como cel pero sin escapar (para componer antes de escapar todo junto)."""
    if v is None or v == "":
        return ND
    v = " ".join(str(v).split())
    if n and len(v) > n:
        v = v[: n - 1].rstrip() + "…"
    return v


def tabla(cols, filas):
    out = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    out += ["| " + " | ".join(f) + " |" for f in filas]
    return "\n".join(out)


def fila2(nombre, a, b, n=None):
    return [cel(nombre), cel(a, n), cel(b, n)]


def lista_humanos(f):
    hs = get(f, "historia", "humanos_candidatos")
    if not isinstance(hs, list):
        return None
    return "<br>".join(
        cel(f"{h.get('nombre', '?')} · {txt(h.get('rol'), 80)} · citas {h.get('citas_verificadas', ND)}")
        for h in hs if isinstance(h, dict)) or None


def pico_ficha(f):
    p = get(f, "historia", "pico")
    if not isinstance(p, dict):
        return None
    return f"{txt(p.get('que'), 200)} — por qué: {txt(p.get('por_que'), 200)}"


def giros(f):
    g = get(f, "historia", "giros")
    if not isinstance(g, list):
        return None
    out = []
    for i, x in enumerate(g, 1):
        t = x.get("que_cambia") if isinstance(x, dict) else x
        out.append(cel(f"{i}. {txt(t, 120)}"))
    return "<br>".join(out) or None


def escenas(f):
    es = f.get("escenas") if isinstance(f, dict) else None
    if not isinstance(es, list):
        return None
    out = []
    for i, x in enumerate(es, 1):
        if isinstance(x, dict):
            t = x.get("titulo") or x.get("nombre") or x.get("donde") or x.get("que_pasa")
        else:
            t = x
        out.append(cel(f"{i}. {txt(t, 70)}"))
    return "<br>".join(out) or None


def ids_por_cap(e):
    """(ids, centrales, apoyos) por cap: beats agrupados por beat['cap']."""
    res, centrales, apoyos = {}, {}, {}
    for b in (get(e, "beats") or []):
        if not isinstance(b, dict):
            continue
        c = b.get("cap")
        dc = b.get("dato_central")
        ap = b.get("datos_apoyo") or []
        res.setdefault(c, set())
        centrales.setdefault(c, [])
        apoyos.setdefault(c, [])
        for i in ([dc] if dc else []) + list(ap):
            res[c].add(i)
        if dc:
            centrales[c].append(dc)
        apoyos[c] += list(ap)
    return res, centrales, apoyos


def jacc(x, y):
    u = x | y
    return f"{len(x & y)}/{len(u)} = {len(x & y) / len(u):.2f}" if u else ND


def main():
    ap = argparse.ArgumentParser(description="Tabla A/B de la ficha del caso (F44)")
    a_def = F44 / "A" if (F44 / "A" / "ficha_caso.json").exists() else PROD
    ap.add_argument("--a-dir", default=str(a_def))
    ap.add_argument("--b-dir", default=str(F44 / "B" / "_steps" / TOPIC))
    ap.add_argument("--costos", default=str(F44 / "B" / "costos.json"))
    ap.add_argument("--out", default=str(F44 / "TABLA_AB.md"))
    a = ap.parse_args()

    fa, fb = cargar(a.a_dir, "ficha_caso.json"), cargar(a.b_dir, "ficha_caso.json")
    ea, eb = cargar(a.a_dir, "01a_escaleta.json"), cargar(a.b_dir, "01a_escaleta.json")
    cs = cargar(Path(a.costos).parent, Path(a.costos).name)
    fa, fb, ea, eb = (x if isinstance(x, dict) else {} for x in (fa, fb, ea, eb))

    L = ["# F44 · Tabla A/B de la ficha del caso", "",
         f"- A: `{a.a_dir}` (ficha {'ok' if fa else 'FALTA'}, escaleta {'ok' if ea else 'FALTA'})",
         f"- B: `{a.b_dir}` (ficha {'ok' if fb else 'FALTA'}, escaleta {'ok' if eb else 'FALTA'})", ""]

    # 1. Ficha
    H = ["Campo", "A", "B"]
    filas = []
    ca, cb = get(fa, "conteos") or {}, get(fb, "conteos") or {}
    for k in list(ca) + [k for k in cb if k not in ca]:
        filas.append(fila2(f"conteos.{k}", ca.get(k), cb.get(k)))
    sa, sb = fa.get("sacados"), fb.get("sacados")
    filas.append(fila2("sacados (cantidad)", len(sa) if isinstance(sa, list) else sa,
                       len(sb) if isinstance(sb, list) else sb))
    for k in ("usd", "prompt_version", "pool_md5", "modelo", "esfuerzo", "titulo"):
        filas.append(fila2(k, fa.get(k), fb.get(k)))
    # estas ya vienen con celdas escapadas (llevan <br>): no pasan otra vez por cel
    for nombre, fn in (("historia.humanos_candidatos", lista_humanos), ("historia.pico", pico_ficha),
                       ("historia.giros", giros), ("escenas", escenas)):
        va, vb = fn(fa), fn(fb)
        filas.append([cel(nombre), va if nombre in ("historia.humanos_candidatos", "historia.giros", "escenas") and va else cel(va),
                      vb if nombre in ("historia.humanos_candidatos", "historia.giros", "escenas") and vb else cel(vb)])
    L += ["## 1. Ficha A vs B", "", tabla(H, filas), ""]

    # 2. Escaleta
    def hum(e):
        h = e.get("humano")
        return f"{h.get('nombre', '?')} · {txt(h.get('por_que'), 120)}" if isinstance(h, dict) else None

    def pic(e):
        p = e.get("pico")
        return f"beat {p.get('beat', '?')} · {txt(p.get('por_que'), 120)}" if isinstance(p, dict) else None

    def ap_ids(e):
        x = e.get("a_pantalla")
        return ", ".join(i.get("id", "?") if isinstance(i, dict) else str(i) for i in x) if isinstance(x, list) else None

    def nb(e):
        x = e.get("beats")
        return len(x) if isinstance(x, list) else None

    def nrep(e):
        x = e.get("_reparaciones")
        return len(x) if isinstance(x, list) else None

    def rep(e):
        x = e.get("_reparaciones")
        if not isinstance(x, list) or not x:
            return ND
        return "<br>".join(cel(f"{i}. {r}") for i, r in enumerate(x, 1))

    filas = [fila2("humano", hum(ea), hum(eb)), fila2("pico", pic(ea), pic(eb)),
             fila2("promesa_gancho", ea.get("promesa_gancho"), eb.get("promesa_gancho")),
             fila2("cierre_humano", ea.get("cierre_humano"), eb.get("cierre_humano")),
             fila2("beats (n)", nb(ea), nb(eb)),
             fila2("_reparaciones (n)", nrep(ea), nrep(eb)),
             [cel("_reparaciones"), rep(ea), rep(eb)],
             fila2("a_pantalla (ids)", ap_ids(ea), ap_ids(eb)),
             fila2("prompt_version", ea.get("prompt_version"), eb.get("prompt_version")),
             fila2("ficha.prompt_version", get(ea, "ficha", "prompt_version"), get(eb, "ficha", "prompt_version"))]
    L += ["## 2. Escaleta A vs B", "", tabla(H, filas), ""]

    # 3. Por cap
    ia, ca_, aa = ids_por_cap(ea)
    ib, cb_, ab = ids_por_cap(eb)
    caps = sorted(set(ia) | set(ib), key=lambda c: (c is None, c))
    filas, ua, ub = [], set(), set()
    for c in caps:
        sa_, sb_ = ia.get(c, set()), ib.get(c, set())
        ua |= {(c, i) for i in sa_}
        ub |= {(c, i) for i in sb_}
        filas.append([cel(f"cap {c}"),
                      cel(", ".join(ca_.get(c, []))), cel(", ".join(aa.get(c, []))),
                      cel(", ".join(cb_.get(c, []))), cel(", ".join(ab.get(c, []))),
                      jacc(sa_, sb_)])
    filas.append(["**TOTAL** (cap+id)", ND, ND, ND, ND, jacc(ua, ub)])
    L += ["## 3. Por cap: dato_central + datos_apoyo", "",
          tabla(["Cap", "A central", "A apoyo", "B central", "B apoyo", "\\|A∩B\\|/\\|A∪B\\|"], filas), ""]

    # 4. Costo
    L += ["## 4. Costo total de B", ""]
    if isinstance(cs, dict):
        L.append(f"- total_usd: **{cel(cs.get('total_usd'))}**")
        ps = cs.get("pasos")
        if isinstance(ps, list) and ps:
            L += ["", tabla(["Paso"], [[cel(p)] for p in ps])]
    else:
        L.append(f"{ND} (no existe `{a.costos}`)")

    md = "\n".join(L) + "\n"
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    print(md)
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(md, encoding="utf-8")
    print(f"→ guardado en {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
