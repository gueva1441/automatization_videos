"""F55 Salida A (texto): tabla «id · regla (ancla/A1/A2/sonnet/ninguna) · cap · oración» para D21, D10, D42, D85 en los
dos guiones de Wittenoom (viejo = lab/hyperframes/f54/antes, nuevo = lab/hyperframes/f55/antes); `ids_usados` antes
(solo anclas, el `used_in` de antes de F55) → después (regla_dicho + altas de Sonnet) por párrafo; llamadas, caché y
costo del verificador. Llama a Sonnet de verdad en (f)/(h) (lo que el código no vio en un dato_central sin ancla).
Escribe lab/hyperframes/f55/SALIDA_A.md."""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import fase1_5  # noqa: E402
from script_engine import dicho_verificador as dv  # noqa: E402
from script_engine import evidence as ev  # noqa: E402
from script_engine import guion_v4 as g4  # noqa: E402

TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
IDS = ("D21", "D10", "D42", "D85")
GUIONES = {"viejo": ROOT / "lab/hyperframes/f54/antes", "nuevo": ROOT / "lab/hyperframes/f55/antes"}


def used_in_viejo(text: str, it: dict) -> bool:
    """El `used_in` de antes de F55 (solo anclas), para la columna «antes»."""
    ancs = ev.anchors(it)
    dated = it.get("_kind") == "cronologia" or (it.get("_kind") == "datos" and it.get("tipo") == "fecha")
    if not dated:
        return any(ev.literal_in(a, text) for a in ancs)
    words = ev._content(ev.text_of(it)) - {w[:6] for a in ancs for w in re.findall(r"[a-zñ]{5,}", ev.norm(a))}
    return any(any(ev.literal_in(a, s) for a in ancs) and (not words or words & ev._content(s)) for s in ev._sentences(text))


def parrafos(d: Path) -> list[dict]:
    g = json.loads((d / "01b_guionista_v4.json").read_text(encoding="utf-8"))
    return [dict(p) for p in g["reparacion"]["parrafos"]]


def main() -> None:
    topic = dict(fase1_5._load_topic_by_id(TID))
    pool = topic["evidence_pool"]
    its = ev.items(pool)
    fase1_5.cargar_perfil(TID)
    ficha = json.loads((ROOT / "data/scripts/_steps" / TID / "ficha_caso.json").read_text(encoding="utf-8"))
    L = ["# F55 — Salida A (texto)", "", "Regla de `evidence.regla_dicho` por cap y, en (f)/(h), la segunda opinión de Sonnet "
         "(`dicho_verificador`) sobre el `dato_central` sin ancla. viejo = `lab/hyperframes/f54/antes/`, nuevo = "
         "`lab/hyperframes/f55/antes/`.", ""]
    dv.reset()
    resumen = {}
    for nombre, d in GUIONES.items():
        esc = json.loads((d / "01a_escaleta.json").read_text(encoding="utf-8"))
        ps = parrafos(d)
        own = {c: {i for b in esc["beats"] if b["cap"] == c for i in [b["dato_central"], *(b.get("datos_apoyo") or [])]}
               for c in range(1, 8)}
        # antes: solo anclas ∩ ids del beat (lo que producía F54)
        antes = [[i for i in its if its[i]["_kind"] in ("datos", "cronologia", "citas") and i in own[p["cap"]]
                  and used_in_viejo(p["texto"], its[i])] for p in ps]
        ps_new = g4.with_ids(ps, pool, esc)
        log: list[str] = []
        bl = g4.bloqueantes(topic, esc, ps_new, "abierto", ficha, verificar=lambda h, o, **k: dv.verificar(h, o, log=log, **k))
        altas = list(g4.ULTIMAS_ALTAS)
        L += [f"## {nombre}", "", "### 1. D21, D10, D42, D85: regla · cap · oración", "",
              "| id | hecho | regla por código | cap | oración | Sonnet (f/h) |", "|---|---|---|---|---|---|"]
        for i in IDS:
            filas = []
            for c in range(1, 8):
                txt = "\n\n".join(p["texto"] for p in ps if p["cap"] == c)
                r = ev.regla_dicho(txt, its[i])
                if r:
                    k = ev.oracion_dicha(txt, its[i])
                    filas.append((r, c, ev._sentences(txt)[k] if k is not None else ""))
            son = [a for a in altas if a["id"] == i]
            son_txt = "; ".join(f"sí: cap {a['cap']}, oración {a['oracion']} ({a['que']})" for a in son) or \
                      ("no dicho" if any(x["motivo"].find(i) >= 0 for x in bl) else "—")
            if filas:
                for r, c, s in filas:
                    L.append(f"| {i} | {its[i]['texto'][:70]} | {r} | {c} | {s[:140]} | {son_txt} |")
            else:
                L.append(f"| {i} | {its[i]['texto'][:70]} | ninguna | — | — | {son_txt} |")
        L += ["", f"### 2. Bloqueantes (f)/(h) con el detector nuevo + Sonnet: {len([x for x in bl if x['codigo'] in 'fh'])}", ""]
        for x in bl:
            if x["codigo"] in ("f", "h"):
                L.append(f"- cap {x['cap']} beat {x['beat']} ({x['codigo']}): {x['motivo']}")
        L += ["", "Altas de Sonnet (entran a `ids_usados`):", ""] + \
             [f"- {a['id']} → cap {a['cap']}, párrafo {a['parrafo']}, oración {a['oracion']} ({a['que']})" for a in altas] + \
             ["", "### 3. `ids_usados` antes (solo anclas) → después (regla_dicho + Sonnet), por párrafo", "",
              "| cap | párrafo (beat) | antes | + después |", "|---|---|---|---|"]
        for k, (p, a) in enumerate(zip(ps_new, antes)):
            mas = [i for i in p["ids_usados"] if i not in a]
            L.append(f"| {p['cap']} | {k} ({p['beat']}) | {', '.join(a) or '—'} | {', '.join(mas) or '—'} |")
            assert set(a) <= set(p["ids_usados"]), (nombre, k)
        L += ["", "Log del verificador:", ""] + [f"    {x.strip()}" for x in log] + [""]
        resumen[nombre] = {"bloqueantes_fh": [x for x in bl if x["codigo"] in "fh"], "altas": altas,
                           "ids_antes": antes, "ids_despues": [p["ids_usados"] for p in ps_new]}
    est = dv.estado()
    L += ["## Verificador (las dos corridas)", "", f"llamadas {est['llamadas']} · caché {est['cache']} · US$ {est['usd']}", ""]
    (ROOT / "lab/hyperframes/f55/SALIDA_A.md").write_text("\n".join(L), encoding="utf-8", newline="\n")
    (ROOT / "lab/hyperframes/f55/salida_a.json").write_text(json.dumps({**resumen, "verificador": est}, ensure_ascii=False, indent=1),
                                                            encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
