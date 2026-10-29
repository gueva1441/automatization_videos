# -*- coding: utf-8 -*-
"""F50d B — los 7 pedidos de casilleros de Wittenoom EN SECO (la llamada a Opus se corta antes de salir) con el código
de F50d, y la verificación del handoff contra `lab/hyperframes/f50c/pedidos/`: fuera del bloque ERA (de «ERA (capa
genérica de la época):» hasta antes de «LUGAR PUNTUAL») y de la parte CLOTHING de las líneas de PEOPLE GROUPS, nada
cambia.

Dos comparaciones:
- «canon nuevo» (la del handoff): topic de hoy (canon de la corrida 1 de C) → `pedidos/pedido_chNN.txt`;
- «código solo»: el mismo código con el canon de antes (`antes/topic_wittenoom.json`, sin periods ni
  clothing_by_period) → `pedidos/codigo_solo/pedido_chNN.txt`. Aísla lo que cambia el código del cambio del canon.
Salida: PEDIDOS_F50d.md. Sale 1 si la comparación «canon nuevo» cambia algo fuera de las dos zonas.
Uso: python lab/hyperframes/f50d/pedidos_f50d.py
"""
from __future__ import annotations

import difflib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "lab" / "hyperframes" / "f50c"))
F50D = Path(__file__).resolve().parent
F50C = ROOT / "lab" / "hyperframes" / "f50c"


def zonas(txt: str) -> list[tuple[str, str]]:
    """[(zona, línea)]: zona = «era», «clothing» (la línea de grupo sin lo de CLOTHING) o «resto»."""
    out, en_era, en_grupos = [], False, False
    for ln in txt.splitlines():
        if ln.startswith("ERA (capa genérica de la época):"):
            en_era = True
        elif ln.startswith("LUGAR PUNTUAL"):
            en_era = False
        if ln == "PEOPLE GROUPS:":
            en_grupos = True
            out.append(("resto", ln))
            continue
        if en_grupos and re.match(r"  - \S+: ", ln):
            out.append(("grupo", ln.split(" · CLOTHING: ")[0]))
            continue
        en_grupos = False
        out.append(("era" if en_era else "resto", ln))
    return out


def comparar(antes: str, despues: str) -> dict:
    za, zd = zonas(antes), zonas(despues)
    res = {}
    for z in ("era", "grupo", "resto"):
        a = [ln for k, ln in za if k == z]
        d = [ln for k, ln in zd if k == z]
        res[z] = [x for x in difflib.unified_diff(a, d, "f50c", "f50d", lineterm="", n=0)
                  if not x.startswith("@@")]
    return res


def main() -> int:
    import expedientes_f50c as ex
    from script_engine import m03_expediente as mexp
    from script_engine import m03_visual as m03
    topic, skel, narr_ch = ex.preparar()
    viejo = json.loads((F50D / "antes" / "topic_wittenoom.json").read_text(encoding="utf-8"))
    topic_viejo = {**topic, **{k: viejo.get(k) for k in ("era_visual_canon", "documented_people",
                                                          "anachronism_blocklist", "documented_props",
                                                          "central_subject", "people_groups")}}
    v = json.loads((ROOT / "data" / "scripts" / "_steps" / ex.TID / "03_visual.json").read_text(encoding="utf-8"))
    (F50D / "pedidos" / "codigo_solo").mkdir(parents=True, exist_ok=True)
    canon_viejo = m03._format_seedream_canon_block(topic_viejo)        # el bloque del canon entero en F50c
    filas, fallas, detalle = [], [], []
    for cap in sorted(v["chapters"], key=lambda c: c["chapter_number"]):
        n = cap["chapter_number"]
        anchors, _ = ex._anclas(cap)
        sch = next(c for c in skel["chapters"] if c["chapter_number"] == n)
        narr = next(c for c in narr_ch if c["chapter_number"] == n)["narration"].strip()
        p_nuevo, exps = ex.pedido_y_expedientes(mexp, topic, sch, narr, anchors, n)
        p_solo, _ = ex.pedido_y_expedientes(mexp, topic_viejo, sch, narr, anchors, n)
        (F50D / "pedidos" / f"pedido_ch{n:02d}.txt").write_text(p_nuevo, encoding="utf-8")
        (F50D / "pedidos" / "codigo_solo" / f"pedido_ch{n:02d}.txt").write_text(p_solo, encoding="utf-8")
        ref = (F50C / "pedidos" / f"pedido_ch{n:02d}.txt").read_text(encoding="utf-8")
        cn, cs = comparar(ref, p_nuevo), comparar(ref, p_solo)
        crudo_solo = [x for x in difflib.unified_diff(ref.splitlines(), p_solo.splitlines(), lineterm="", n=0)
                      if x[:1] in "+-" and not x.startswith(("+++", "---"))]
        # medida fina: fuera del bloque del canon ENTERO (ERA + lugar puntual + personas + anacronismos + props) y
        # de las líneas de PEOPLE GROUPS enteras, ¿cambia algo? (el canon se rehízo en C, antes de B)
        j = ref.index(canon_viejo)
        pre, post = ref[:j], ref[j + len(canon_viejo):]
        k = p_nuevo.find(post[:200], len(pre)) if p_nuevo.startswith(pre) else -1
        sin_g = lambda t: [x for x in t.splitlines() if not re.match(r"  - \S+: .* · APPEARANCE: ", x)]
        fuera_canon = (["(el comienzo o el final del pedido no se encontró)"] if k < 0 else
                       [x for x in difflib.unified_diff(sin_g(post), sin_g(p_nuevo[k:]), lineterm="", n=0)
                        if x[:1] in "+-" and not x.startswith(("+++", "---"))])
        grupos_n = len(re.findall(r"^  - \S+: .* · APPEARANCE: ", p_nuevo, re.M))
        anios = sorted({str(e.get("anio_ancla") or e["respaldo"][0]) for e in exps})
        periods = re.findall(r"^  period (.+):$", p_nuevo, re.M)
        filas.append({"cap": n, "anios": anios, "periods": periods,
                      "nuevo": {z: len(cn[z]) for z in cn}, "solo": {z: len(cs[z]) for z in cs},
                      "solo_lineas_crudas": len(crudo_solo), "fuera_del_canon_y_grupos": len(fuera_canon),
                      "grupos": grupos_n})
        if cn["resto"]:
            fallas.append(f"ch{n:02d} canon nuevo: cambia fuera del bloque ERA y de PEOPLE GROUPS")
        if cs["resto"] or cs["era"] or cs["grupo"]:
            fallas.append(f"ch{n:02d} código solo: cambia fuera de CLOTHING")
        detalle.append((n, cn, cs, crudo_solo))
    L = ["# PEDIDOS_F50d — los 7 pedidos de casilleros con la época por tramo (en seco)", "",
         "Salida de `python lab/hyperframes/f50d/pedidos_f50d.py`. Código de F50d con la llamada a Opus cortada. "
         "Referencia: `lab/hyperframes/f50c/pedidos/`. Zonas: «era» = bloque ERA del canon (hasta LUGAR PUNTUAL); "
         "«grupo» = las líneas de PEOPLE GROUPS sin su parte CLOTHING; «resto» = todo lo demás.", "",
         "| cap | años de las fotos | periods que entran | canon nuevo: líneas era / grupo / resto | canon nuevo: fuera "
         "del canon entero y de los grupos | grupos | código solo: era / grupo / resto (líneas crudas) |",
         "|---|---|---|---|---:|---:|---|"]
    for f in filas:
        L.append(f"| {f['cap']} | {' '.join(f['anios'])} | {' · '.join(f['periods']) or '—'} | "
                 f"{f['nuevo']['era']} / {f['nuevo']['grupo']} / {f['nuevo']['resto']} | "
                 f"{f['fuera_del_canon_y_grupos']} | {f['grupos']} | "
                 f"{f['solo']['era']} / {f['solo']['grupo']} / {f['solo']['resto']} ({f['solo_lineas_crudas']}) |")
    L += ["", f"**Resultado: {'PASA' if not fallas else 'FALLA — PARADA'}**", ""] + [f"- {x}" for x in fallas]
    for n, cn, cs, crudo in detalle:
        L += ["", f"## ch{n:02d}", "", "### código solo (canon de antes): diff crudo contra F50c", "", "```diff",
              *[x[:400] for x in crudo], "```", "", "### canon nuevo: diff por zona", ""]
        for z in ("era", "grupo", "resto"):
            L += [f"**{z}**", "", "```diff", *[x[:400] for x in cn[z]], "```", ""]
    (F50D / "PEDIDOS_F50d.md").write_text("\n".join(L), encoding="utf-8")
    print(json.dumps({"filas": filas, "fallas": fallas}, ensure_ascii=False))
    return 0 if not fallas else 1


if __name__ == "__main__":
    sys.exit(main())
