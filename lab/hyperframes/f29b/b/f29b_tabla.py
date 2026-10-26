"""F29b §B.4–B.5 — tabla por cap y lo medible, desde los planes resueltos y las crudas del rotulista de
`f8s3-vajont-f29b`. CC no cuenta «cumplen (a)(b)(c)» (eso lo cuenta el analista con la hoja).
Uso: python -I lab/hyperframes/f29b/b/f29b_tabla.py → lab/hyperframes/f29b/b/tabla.md + medidas.json"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
LAB = Path(__file__).resolve().parent
DST = "f8s3-vajont-f29b"
WD = ROOT / "output" / DST / "_fase2b_work"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    import claude_helpers as hx
    from script_engine import gfx_rotulista as gro
    filas, med = [], {"munones": [], "cifras_sin_etiqueta": [], "numeros_voz_20s": [], "numeros_despues": [],
                      "a_pantalla": {}, "por_cap": {}}
    esc = json.loads((ROOT / "data" / "scripts" / "_steps" / "f8s3-vajont" / "01a_escaleta.json").read_text(encoding="utf-8"))
    ap = {str(a["id"]): a for a in esc.get("a_pantalla") or []}
    salieron: dict[str, dict] = {}
    for c in range(1, 8):
        cap = f"ch{c:02d}"
        raw = json.loads((WD / f"rotulista_{cap}.raw.json").read_text(encoding="utf-8"))
        plan = json.loads((WD / f"gfx_plan_{cap}.resolved.json").read_text(encoding="utf-8"))["plan"]
        ent = raw["entrada"]
        words = None
        import fase2b  # noqa: F401  (carga perezosa de config)
        from script_engine.gfx_layer import remapped_words
        from config import OUTPUT_DIR
        ad = OUTPUT_DIR / "audio" / DST
        pl = {p.chapter_id: p for p in fase2b._build_plans(
            json.loads((ad / "sync_map.json").read_text(encoding="utf-8")),
            json.loads((OUTPUT_DIR / DST / "assets" / "assets_manifest.json").read_text(encoding="utf-8")),
            DST, ad, fase2b._load_script_lookup(DST))}
        _, words = remapped_words(pl[cap])
        # costo del rotulista (todas las llamadas del cap)
        tin = tout = 0
        usd = seg = 0.0
        for it in raw["intentos"]:
            for cr in it.get("crudas") or []:
                u = cr["respuesta"].get("usage") or {}
                tin += u.get("input_tokens") or 0
                tout += u.get("output_tokens") or 0
                usd += cr.get("usd") or 0.0
                seg += cr.get("segundos") or 0.0
        propuestos = len((raw.get("final") or {}).get("bloques") or [])
        r = plan.get("rotulista") or {}
        fuera = [f for f in r.get("filas") or [] if f["accion"] == "fuera"]
        colocados = [f for f in r.get("filas") or [] if f["accion"] == "colocado"]
        crit = plan.get("critico_rotulista") or []
        cortados_critico = [x for x in crit if not x["pasa"]]
        quedan = [x for x in crit if x["pasa"]] if crit else colocados
        med["por_cap"][cap] = {"intentos": len(raw["intentos"]), "propuestos": propuestos,
                               "fuera_A4": dict(Counter(f.get("regla") for f in fuera)),
                               "fuera_A4_detalle": [(f.get("pool_id"), f.get("regla"), f.get("motivo")) for f in fuera],
                               "colocados": len(colocados), "cortados_critico": len(cortados_critico),
                               "en_pantalla": len(quedan), "tokens_in": tin, "tokens_out": tout, "usd": round(usd, 4),
                               "segundos": round(seg, 1), "a_pantalla_faltan": r.get("faltan_a_pantalla"),
                               "a_pantalla_incompletos": r.get("a_pantalla_incompletos")}
        bloques = [b for k in ("callouts", "archive_clippings") for b in plan.get(k) or [] if b.get("rotulista")]
        bloques += [plan[k] for k in ("quote_card", "evidence_zoom") if plan.get(k) and plan[k].get("rotulista")]
        for b in sorted(bloques, key=lambda b: b["start"]):
            txt = b.get("text") or b.get("headline") or b.get("detail")
            t0 = float(b["start"])
            cv = b.get("critico") or {}
            veredicto = ("sin veredicto" if cv.get("error") else
                         f"(1) {'sí' if cv.get('habla_de_eso') else 'no'} · (2) {'sí' if cv.get('dice_algo_nuevo') else 'no'}")
            filas.append((cap, b.get("tipo_rotulista"), txt, b.get("kicker"), b.get("sentence_idx"), round(t0, 1),
                          b.get("pool_id"), b.get("aporta"), veredicto))
            if b.get("tipo_rotulista") != "lupa" and gro.munon(txt):
                med["munones"].append((cap, txt))
            if b.get("tipo_rotulista") == "cifra" and ":" not in txt and not gro.numeros(txt):
                med["cifras_sin_etiqueta"].append((cap, txt))
            cerca = " ".join(str(w["word"]) for w in words if t0 - 20 <= float(w["start"]) <= t0 + 20)
            despues = " ".join(str(w["word"]) for w in words if float(w["start"]) >= t0)
            nums = gro.numeros(txt)
            dichos = [n for n in nums if gro.numero_en(n, cerca)]
            if dichos:
                med["numeros_voz_20s"].append((cap, txt, dichos))
            if [n for n in nums if gro.numero_en(n, despues)]:
                med["numeros_despues"].append((cap, txt))
            if b.get("pool_id") in ap:
                salieron[b["pool_id"]] = {"cap": cap, "texto": txt, "kicker": b.get("kicker")}
    for i, a in ap.items():
        s = salieron.get(i)
        med["a_pantalla"][i] = {"cap_escaleta": a.get("cap"), "por_que": a.get("por_que"), "salio": bool(s), **(s or {}),
                                "falta_lo_que_pide": gro.lo_que_pide(a.get("por_que") or "", "", s["texto"])
                                if s else None}
    lines = ["| cap | tipo | texto en pantalla | kicker | oración | t0 (s) | pool_id | aporta | crítico |",
             "|---|---|---|---|---|---|---|---|---|"]
    for f in filas:
        lines.append("| " + " | ".join("—" if x is None else str(x).replace("|", "/") for x in f) + " |")
    lines += ["", "| cap | intentos | propuestos | fuera por A.4 | colocados | cortó el crítico | en pantalla | tokens in/out | US$ | s |",
              "|---|---|---|---|---|---|---|---|---|---|"]
    for cap, m in med["por_cap"].items():
        lines.append(f"| {cap} | {m['intentos']} | {m['propuestos']} | {m['fuera_A4'] or 0} | {m['colocados']} | "
                     f"{m['cortados_critico']} | {m['en_pantalla']} | {m['tokens_in']}/{m['tokens_out']} | {m['usd']} | "
                     f"{m['segundos']} |")
    (LAB / "tabla.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    (LAB / "medidas.json").write_text(json.dumps(med, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n".join(lines), flush=True)
    print(json.dumps({k: v for k, v in med.items() if k != "por_cap"}, ensure_ascii=False, indent=1), flush=True)


if __name__ == "__main__":
    main()
