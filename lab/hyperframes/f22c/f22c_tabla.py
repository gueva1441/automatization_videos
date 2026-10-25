"""F22c — tablas del reporte con lo que quedó en disco (sin API): escaletas (A sin columna, B con columna; la de F22, con
columna, como referencia; la de Kyshtym) y guiones de Opus 5.5 v5.2 (más Opus a/b de F22b como referencia). Escribe
`tabla_f22c.md` y `resumen_f22c.json`.
Uso: python -I lab/hyperframes/f22c/f22c_tabla.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LAB = Path(__file__).resolve().parent
F22, F22B = LAB.parent / "f22", LAB.parent / "f22b"
sys.path[:0] = [str(ROOT), str(F22), str(F22B)]
STEPS = ROOT / "data" / "scripts" / "_steps"


def _j(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def esc_view(esc: dict) -> dict:
    beats = esc.get("beats") or []
    ids = {i for b in beats for i in [b.get("dato_central"), *(b.get("datos_apoyo") or [])] if i}
    ids |= {x.get("id") for x in esc.get("a_pantalla") or [] if x.get("id")}
    apoyos = [len(b.get("datos_apoyo") or []) for b in beats]
    img = [len(str(b.get("imagen_sensorial") or "").split()) for b in beats]
    return {"beats": len(beats), "beats_por_cap": [sum(1 for b in beats if b.get("cap") == n) for n in range(1, 8)],
            "ids_totales": len(ids), "a_pantalla": len(esc.get("a_pantalla") or []),
            "apoyos_por_beat": apoyos, "apoyos_promedio": round(sum(apoyos) / len(apoyos), 2) if apoyos else 0,
            "palabras_imagen": sum(img), "palabras_imagen_promedio": round(sum(img) / len(img), 1) if img else 0,
            "promesa_gancho": esc.get("promesa_gancho"), "cierre_humano": esc.get("cierre_humano"),
            "humano": (esc.get("humano") or {}).get("nombre"), "pico_beat": (esc.get("pico") or {}).get("beat"),
            "antagonista": esc.get("antagonista"),
            "intentos": [len(x.get("bloqueantes") or []) for x in esc.get("_intentos") or []]}


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    import f22_compara as fc2
    from script_engine import guion_v4 as g4
    yd, kd = STEPS / "f8s1-ycua-bolanos", STEPS / "f18-kyshtym-mayak"
    ypool, yficha = _j(yd / "00_pool_v3.json"), _j(yd / "ficha_caso.json")
    kpool, kficha = _j(kd / "00_pool_v3.json"), _j(kd / "ficha_caso.json")
    escs = [("A1", "sin columna", _j(LAB / "escaleta_ycua_f22c_A1.json")),
            ("A2", "sin columna", _j(LAB / "escaleta_ycua_f22c_A2.json")),
            ("B1", "con columna", _j(LAB / "escaleta_ycua_f22c_B1.json")),
            ("B2", "con columna", _j(LAB / "escaleta_ycua_f22c_B2.json")),
            ("F22 (ref.)", "con columna", _j(F22 / "escaleta_ycua_f22.json")),
            ("K", "Kyshtym F22", _j(F22 / "escaleta_kyshtym_f22.json"))]
    res: dict = {"escaletas": {}, "guiones": {}}
    E = ["| escaleta | columna | beats | beats por cap | ids totales | a_pantalla | apoyos/beat | palabras de imagen "
         "(total · por beat) | intentos (bloqueantes) |", "|---|---|---|---|---|---|---|---|---|"]
    T = ["| escaleta | promesa_gancho | cierre_humano |", "|---|---|---|"]
    for tag, col, esc in escs:
        if not esc:
            E.append(f"| {tag} | {col} | no salió | | | | | | |")
            continue
        v = esc_view(esc)
        res["escaletas"][tag] = {"columna": col, **v}
        E.append(f"| {tag} | {col} | {v['beats']} | {v['beats_por_cap']} | {v['ids_totales']} | {v['a_pantalla']} | "
                 f"{v['apoyos_promedio']} | {v['palabras_imagen']} · {v['palabras_imagen_promedio']} | {v['intentos']} |")
        T.append(f"| {tag} | «{v['promesa_gancho']}» | «{v['cierre_humano']}» |")
    guiones = [("A1", "ycua", LAB / "guion_ycua_f22c_A1.json", LAB / "escaleta_ycua_f22c_A1.json"),
               ("A2", "ycua", LAB / "guion_ycua_f22c_A2.json", LAB / "escaleta_ycua_f22c_A2.json"),
               ("B1", "ycua", LAB / "guion_ycua_f22c_B1.json", LAB / "escaleta_ycua_f22c_B1.json"),
               ("B2", "ycua", LAB / "guion_ycua_f22c_B2.json", LAB / "escaleta_ycua_f22c_B2.json"),
               ("opus52a F22b (ref.)", "ycua", F22B / "guion_ycua_f22b_opus52a.json", F22 / "escaleta_ycua_f22.json"),
               ("opus52b F22b (ref.)", "ycua", F22B / "guion_ycua_f22b_opus52b.json", F22 / "escaleta_ycua_f22.json"),
               ("K", "kyshtym", LAB / "guion_kyshtym_f22c_K.json", F22 / "escaleta_kyshtym_f22.json")]
    costos = {}
    for x in (_j(LAB / "costos_f22c.json") or {}).get("etapas") or []:
        costos[(x["tag"], x["paso"])] = costos.get((x["tag"], x["paso"]), 0) + x["usd"]
    G = ["| guion | escaleta | palabras | min | bloqueantes | citas | personas con nombre | cierre | US$ guion |",
         "|---|---|---|---|---|---|---|---|---|"]
    PC = ["| cap | " + " | ".join(t for t, *_ in guiones) + " |", "|---|" + "---|" * len(guiones)]
    P = ["| guion | personas con nombre por cap |", "|---|---|"]
    vistas = {}
    for tag, tema, gp, ep in guiones:
        g, esc = _j(gp), _j(ep)
        pool, ficha = (ypool, yficha) if tema == "ycua" else (kpool, kficha)
        if not g or not g.get("parrafos") or not esc:
            G.append(f"| {tag} | — | no salió{' (' + g['error'][:80] + ')' if g and g.get('error') else ''} | | | | | | |")
            continue
        v = fc2.guion_view(tema, g, esc, ficha, pool)
        bl = g4.bloqueantes({"id": tema, "evidence_pool": pool}, esc, g["parrafos"], ficha=ficha, version="f22-1")
        m = g.get("metricas") or {}
        vistas[tag] = v
        usd = costos.get((tag, "guion"), (g.get("costo") or {}).get("usd"))
        G.append(f"| {tag} | {ep.stem.replace('escaleta_', '')} | {v['palabras']} | {g.get('minutos')} | {len(bl)} | "
                 f"{m.get('citas')} | {len(v['personas_total'])} | {m.get('cierre')} | "
                 f"{round(usd, 4) if usd is not None else '—'} |")
        res["guiones"][tag] = {"palabras": v["palabras"], "minutos": g.get("minutos"), "bloqueantes": [b["motivo"] for b in bl],
                               "citas": m.get("citas"), "personas": v["personas_total"], "cierre": m.get("cierre"),
                               "usd": usd, "por_cap": {n: {k: c[k] for k in ("palabras", "personas", "citas", "bloqueantes")}
                                                      for n, c in v["por_cap"].items()}}
        P.append(f"| {tag} | " + " · ".join(f"{n}: {', '.join(c['personas']) or '—'}"
                                            for n, c in sorted(v["por_cap"].items())) + " |")
    for n in range(1, 8):
        cel = []
        for tag, *_ in guiones:
            c = (vistas.get(tag) or {}).get("por_cap", {}).get(n)
            cel.append(f"{c['palabras']} · {len(c['personas'])}p · {c['citas']}c · {c['bloqueantes']}b" if c else "—")
        PC.append(f"| {n} | " + " | ".join(cel) + " |")
    total = (_j(LAB / "costos_f22c.json") or {}).get("usd_total")
    md = "\n".join(["#### Escaletas", ""] + E + ["", "#### Promesa del gancho y cierre humano (textuales)", ""] + T
                   + ["", "#### Guiones (Opus 5.5 v5.2, effort high)", ""] + G
                   + ["", "#### Guiones por cap (palabras · personas · citas · bloqueantes)", ""] + PC
                   + ["", "#### Personas con nombre por cap", ""] + P
                   + ["", f"Tanda F22c: US$ {total} de 3.00."]) + "\n"
    (LAB / "tabla_f22c.md").write_text(md, encoding="utf-8")
    (LAB / "resumen_f22c.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
