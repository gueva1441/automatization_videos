"""Simulacion en seco (solo lectura) de la regla: escaleta sin ficha v2 = error que para."""
import json
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]
STEPS = RAIZ / "data" / "scripts" / "_steps"
DB = RAIZ / "data" / "topics_db.json"
SALIDA = Path(__file__).resolve().parent / "tabla_sin_ficha.md"


def leer(p):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception as e:
        return {"__error__": str(e)}


def main():
    db = leer(DB)
    ids = {t.get("id") for t in db.get("topics", [])}
    filas = []
    for d in sorted(STEPS.iterdir()):
        if not d.is_dir() or not (d / "00_pool_v3.json").exists():
            continue
        fp = d / "ficha_caso.json"
        hay = fp.exists()
        f = leer(fp) if hay else {}
        pv = f.get("prompt_version", "-") if isinstance(f, dict) else "-"
        hist = isinstance(f, dict) and "historia" in f
        esc = (d / "01a_escaleta.json").exists()
        b = sorted(x.name for x in d.glob("01b_*"))
        en_db = d.name in ids
        para = not hist
        prod = en_db and (esc or bool(b))
        filas.append((d.name, hay, pv, hist, esc, len(b), en_db, para, prod))
    sn = lambda x: "sí" if x else "no"
    out = ["| topic | ficha_caso.json | prompt_version | historia | 01a_escaleta | 01b_* | en topics_db | ¿para? | clasif. (si para) |",
           "|---|---|---|---|---|---|---|---|---|"]
    for n, hay, pv, hist, esc, nb, en_db, para, prod in filas:
        cl = ("producción" if prod else "lab") if para else "-"
        out.append(f"| {n} | {sn(hay)} | {pv} | {sn(hist)} | {sn(esc)} | {nb} | {sn(en_db)} | {sn(para)} | {cl} |")
    out.append(f"\nTotal con pool v3: {len(filas)}; paran: {sum(1 for f in filas if f[7])}.")
    txt = "\n".join(out)
    SALIDA.write_text(txt + "\n", encoding="utf-8")
    print(txt)


main()
