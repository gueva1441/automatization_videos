"""F21 §2 — RECHECK_f21.md a partir de recheck_antes.json (código de 08d63d9) y recheck_despues.json (F21).
Uso: python -I lab/hyperframes/f21/recheck_md.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

LAB = Path(__file__).resolve().parent
NOMBRE = {"orleans": "Orleans (`ba6c3cac-f7r3`)", "ycua": "Ycuá (`f8s1-ycua-bolanos`)",
          "kyshtym": "Kyshtym (`f18-kyshtym-mayak`)"}


def _j(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def _d(a, b) -> str:
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return f"{b - a:+d}" if b != a else "="
    return "=" if a == b else "≠"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    A, B = _j(LAB / "recheck_antes.json"), _j(LAB / "recheck_despues.json")
    L = ["# RECHECK F21 — antes (código de `08d63d9`) | después (F21), sin API", "",
         "Mismos archivos de disco en las dos corridas (`recheck.py`): perfil → `set_vocabulario`; sobre una copia del pool,"
         " `add_quote_authors`, `canonical_names`, `presence_v3`, `person_stats`, cifras canónicas, `verify_pool` (con los"
         " txt ya bajados) y `person_stats` → compuerta; ficha (`ficha_caso.check`), columna (`m01a_columna.chequeo`),"
         " escaleta (`m01a_escaleta.bloqueantes`) y guion (`guion_v4.bloqueantes` + `metricas`). Kyshtym: pool de F20;"
         " ficha, columna y escaleta (crudo del pase 2) de F18 contra el pool de F18; **Kyshtym no tiene guion** (F18 paró"
         " en la escaleta y F19 en el research). Orleans no tiene columna. Costo: US$ 0.00 (`data/cost_history.json` "
         "con 486 registros antes y después).", ""]
    for tema in ("orleans", "ycua", "kyshtym"):
        a, b = A[tema], B[tema]
        pa, pb = a["pool"], b["pool"]
        rows = [("compuerta", pa["color"], pb["color"])]
        rows += [(f"métrica: {k}", pa["metricas"][k], pb["metricas"][k]) for k in pa["metricas"]]
        rows += [("personajes en el pool", len(pa["personajes"]), len(pb["personajes"])),
                 ("citas verificadas (verify_pool)", pa["verificacion"].get("verificada"), pb["verificacion"].get("verificada")),
                 ("citas verificadas parcial", pa["verificacion"].get("verificada_parcial"),
                  pb["verificacion"].get("verificada_parcial")),
                 ("citas sin verificar", pa["verificacion"].get("sin_verificar"), pb["verificacion"].get("sin_verificar")),
                 ("cifra canónica", "; ".join(c["valor"] or "—" for c in pa["canonicas"]) or "—",
                  "; ".join(c["valor"] or "—" for c in pb["canonicas"]) or "—")]
        fa, fb = a.get("ficha"), b.get("ficha")
        rows.append(("ficha: lo que sacaría el chequeo", fa["problemas"] if fa else "—", fb["problemas"] if fb else "—"))
        ca, cb = a.get("columna"), b.get("columna")
        rows.append(("columna: problemas", len(ca["problemas"]) if ca else "—", len(cb["problemas"]) if cb else "—"))
        ea, eb = a.get("escaleta"), b.get("escaleta")
        rows.append(("escaleta: bloqueantes", len(ea.get("bloqueantes") or []) if ea else "—",
                     len(eb.get("bloqueantes") or []) if eb else "—"))
        ga, gb = a.get("guion"), b.get("guion")
        rows.append(("guion: bloqueantes", len(ga["bloqueantes"]) if ga else "—", len(gb["bloqueantes"]) if gb else "—"))
        if ga and gb:
            rows += [(f"guion: {k}", ga["metricas"].get(k), gb["metricas"].get(k))
                     for k in ("palabras", "citas", "duras_v3", "humano_caps")]
        L += [f"## {NOMBRE[tema]}", "", "| medida | antes | después | Δ |", "|---|---|---|---|"]
        L += [f"| {k} | {x} | {y} | {_d(x, y)} |" for k, x, y in rows]
        ea_n, eb_n = set(pa["elegibles"]), set(pb["elegibles"])
        L += ["", f"**Elegibles:** {len(ea_n)} → {len(eb_n)}. "
              f"**Entran:** {', '.join(sorted(eb_n - ea_n)) or 'nadie'}. **Salen:** {', '.join(sorted(ea_n - eb_n)) or 'nadie'}."]
        na, nb = {p["nombre"] for p in pa["personajes"]}, {p["nombre"] for p in pb["personajes"]}
        L += [f"**Personajes nuevos en el pool:** {', '.join(sorted(nb - na)) or 'ninguno'}. "
              f"**Que ya no están:** {', '.join(sorted(na - nb)) or 'ninguno'}."]
        if pa["log"] != pb["log"]:
            L += [f"Log antes: {pa['log']} · después: {pb['log']}"]
        for nombre, x, y in (("ficha", fa, fb), ("escaleta", ea, eb)):
            if x and y:
                xa = set(x.get("sacados") or x.get("bloqueantes") or [])
                yb = set(y.get("sacados") or y.get("bloqueantes") or [])
                if xa != yb:
                    L += [f"**{nombre}, aparece:** {sorted(yb - xa)} · **desaparece:** {sorted(xa - yb)}"]
                elif xa:
                    L += [f"**{nombre} (igual antes y después):** {sorted(xa)}"]
        if ga and gb:
            sa = {(z["codigo"], z["cap"], z["beat"], z["motivo"]) for z in ga["bloqueantes"]}
            sb = {(z["codigo"], z["cap"], z["beat"], z["motivo"]) for z in gb["bloqueantes"]}
            L += [f"**Guion, bloqueante que aparece:** {sorted(sb - sa) or 'ninguno'} · **que desaparece:** "
                  f"{sorted(sa - sb) or 'ninguno'}."]
            da, db = set(ga["metricas"].get("duras_v3_lista") or []), set(gb["metricas"].get("duras_v3_lista") or [])
            if da != db:
                L += [f"Duras v3 (métrica) que aparecen: {sorted(db - da)} · que desaparecen: {sorted(da - db)}"]
        L.append("")
        pk = {p["nombre"]: p for p in pb["personajes"]}
        if tema == "kyshtym":
            L += ["Personajes de Kyshtym después (todos):", "",
                  "| nombre | rol | testigo | antagonista | citas | datos | presente en el evento | elegible |",
                  "|---|---|---|---|---|---|---|---|"]
            L += [f"| {p['nombre']} | {p.get('rol') or '—'} | {p.get('testigo')} | {p.get('antagonista')} | {p.get('n_citas')} "
                  f"| {p.get('n_datos')} | {p.get('presente_en_evento')} | **{p.get('elegible_humano')}** |"
                  for p in pk.values()]
            L.append("")
    (LAB / "RECHECK_f21.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
