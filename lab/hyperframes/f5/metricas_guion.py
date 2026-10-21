"""F5 §3: evidencia del guion para la validación del analista (preguntas 1–4 del §4) → lab/hyperframes/f5/GUION_v1_v2.md
Uso: PYTHONIOENCODING=utf-8 python lab/hyperframes/f5/metricas_guion.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
from script_engine import evidence as ev  # noqa: E402

V1, V2 = "ba6c3cac-a091-41c0-8dad-afd2f4364747", "ba6c3cac-f5v2"
STEPS = ROOT / "data" / "scripts" / "_steps"
OUT = Path(__file__).resolve().parent / "GUION_v1_v2.md"


def _load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> None:
    pool = _load(STEPS / V2 / "01_facts_sources.json")["evidence_pool"]
    its = ev.items(pool)
    j = {"v1": _load(STEPS / V2 / "06_judge_narrative_v1.json"), "v2": _load(STEPS / V2 / "06_judge_narrative.json")}
    nar = {"v1": [c["narration"] for c in _load(STEPS / V1 / "01b_narration.json")["chapters"]],
           "v2": [c["narration"] for c in _load(STEPS / V2 / "01b_narration.json")["chapters"]]}
    sk2 = _load(STEPS / V2 / "01a_skeleton.json")
    L = ["# F5 §3 — Guion v1 vs v2 (evidencia para VALIDACION_F5)", "",
         "Medido con `script_engine/m05_narrative.py` contra el MISMO evidence_pool para las dos versiones.", ""]
    L += ["## 1. Datos nuevos por cap y Gusman", "", "| cap | v1 datos nuevos | v2 datos nuevos | v2 asignados (skeleton) |",
          "|---|---|---|---|"]
    for v in ("v1", "v2"):
        seen: set[str] = set()
        j[v]["_nuevos"] = []
        for c in j[v]["caps"]:
            new = [i for i in c["datos_usados"] if i not in seen]
            j[v]["_nuevos"].append(new)
            seen |= set(c["datos_usados"])
    for k in range(7):
        asg = next((c.get("evidence_ids") or [] for c in sk2["chapters"] if c["chapter_number"] == k + 1), [])
        L.append(f"| {k + 1} | {len(j['v1']['_nuevos'][k])} | {len(j['v2']['_nuevos'][k])} ({', '.join(j['v2']['_nuevos'][k])}) "
                 f"| {len(asg)} |")
    g1 = [k + 1 for k, t in enumerate(nar["v1"]) if ev.literal_in("Gusman", t)]
    g2 = [k + 1 for k, t in enumerate(nar["v2"]) if ev.literal_in("Gusman", t)]
    L += ["", f"Gusman nombrado: v1 en caps {g1 or 'ninguno'} · v2 en caps {g2 or 'ninguno'}. "
          f"Personajes de v2: " + ", ".join(f"{p['nombre']} (cap {p['entra_en_cap']})" for p in sk2.get("personajes") or []), ""]
    L += ["## 2. Repetición", "", "| dato | v1 caps | v2 caps |", "|---|---|---|"]
    for name, anc in (("6,500", "6,500"), ("«pecho»", "pecho"), ("«29 de agosto»", "29 de agosto"), ("500 desaparecidos", "500"),
                      ("517", "517")):
        c1 = [k + 1 for k, t in enumerate(nar["v1"]) if ev.literal_in(anc, t)]
        c2 = [k + 1 for k, t in enumerate(nar["v2"]) if ev.literal_in(anc, t)]
        L.append(f"| {name} | {len(c1)} {c1} | {len(c2)} {c2} |")
    for v in ("v1", "v2"):
        o = j[v]["video"]["datos_en_mas_de_2_caps"]
        L.append(f"\n{v}: datos duros del pool en más de 2 caps = {len(o)} "
                 + (str({i: c for i, c in o.items()}) if o else ""))
    L += ["", f"3-gramas repetidos entre caps: v1 {j['v1']['video']['trigramas_repetidos']:.1%} · "
          f"v2 {j['v2']['video']['trigramas_repetidos']:.1%} (umbral < 5 %)", ""]
    L += ["## 3. Adjetivos → hechos", "", "| | v1 | v2 |", "|---|---|---|",
          f"| adjetivos / 100 palabras (heurística, umbral calibrado 3.6) | {j['v1']['video']['adj_100']} | {j['v2']['video']['adj_100']} |",
          f"| densidad (datos duros / 100 palabras, umbral 2.0) | {j['v1']['video']['densidad']} | {j['v2']['video']['densidad']} |",
          f"| datos distintos del pool | {j['v1']['video']['datos_distintos']} | {j['v2']['video']['datos_distintos']} |",
          f"| palabras | {j['v1']['video']['palabras']} | {j['v2']['video']['palabras']} |", "",
          "Pares de frases (mismo momento del relato):", ""]
    import re
    sent = lambda t: re.split(r"(?<=[.!?…])\s+", t)  # noqa: E731
    pairs = [(2, "huracán"), (3, "generadores"), (4, "517")]
    for cap, key in pairs:
        a = next((s for s in sent(nar["v1"][cap - 1]) if key in s.lower()), sent(nar["v1"][cap - 1])[1])
        b = next((s for s in sent(nar["v2"][cap - 1]) if key in s.lower()), sent(nar["v2"][cap - 1])[1])
        L += [f"- cap {cap} · v1: «{a}»", f"  · v2: «{b}»"]
    L += ["", "## 4. Cierres (cliffhanger del skeleton → últimas 2 oraciones de v2)", ""]
    for c in j["v2"]["video"]["cliffhangers"]:
        tail = " ".join(sent(nar["v2"][c["cap"] - 1])[-2:])
        L += [f"- **cap {c['cap']} → [{c['id']}]** {c['texto']}", f"  cierre: «{tail}» — {'✔' if c['ok'] else '✘'} "
              + (f"(en el cierre: {', '.join(c['en_cierre'][:4])})" if c["en_cierre"] else "")]
    v = j["v2"].get("violaciones_narrador") or {}
    L += ["", "## Violaciones que el narrador aceptó tras 3 intentos (v2)", ""]
    L += [f"- cap {k}: " + " · ".join(x.lstrip('- ')[:160] for x in vv) for k, vv in sorted(v.items())] or ["- ninguna"]
    L += ["", "## Umbrales del juez", "", f"- v1: {j['v1']['video']['umbral']}", f"- v2: {j['v2']['video']['umbral']}"]
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
