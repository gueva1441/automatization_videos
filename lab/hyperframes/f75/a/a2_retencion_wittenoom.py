# -*- coding: utf-8 -*-
"""F75 A2: `m05_narrative.retencion()` directo sobre Wittenoom con los archivos del disco (sin LLM, US$ 0, no escribe nada
fuera de lab/hyperframes/f75/a/). Mismas entradas que `judge_narration`: párrafos de 01b_narracion_v3.json, escaleta
01a_escaleta.json, skeleton 01a_skeleton.json (títulos), pool 01_facts_sources.json → evidence_pool. seg = el
`retencion.seg_por_palabra` ya guardado en 06_judge_narrative.json (no se llama a `velocidad()`)."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from script_engine import m05_narrative as m5  # noqa: E402

TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
D = ROOT / "data" / "scripts" / "_steps" / TID
CONTRATO_CAND = {"P17": 16, "P16": 7, "P21": 3, "P20": 3}
CONTRATO = {"ch01": (14, 1, 7), "ch02": (18, 1, 16), "ch03": (25, 3, 10), "ch04": (19, 2, 12), "ch05": (23, 6, 8),
            "ch06": (25, 2, 12), "ch07": (15, 1, 10)}


def lee(n):
    return json.loads((D / n).read_text(encoding="utf-8"))


parrafos = lee("01b_narracion_v3.json")["parrafos"]
esc = lee("01a_escaleta.json")
sk = lee("01a_skeleton.json")
pool = lee("01_facts_sources.json")["evidence_pool"]
seg = lee("06_judge_narrative.json")["retencion"]["seg_por_palabra"]

r = m5.retencion(parrafos, sk, esc, pool, seg)
print("seg_por_palabra:", seg, "| oraciones:", sum(c["oraciones"] for c in r["caps"]))
print("retencion.personaje =", json.dumps(r["personaje"], ensure_ascii=False))
print("retencion.personaje_motivo =", r["personaje_motivo"])

from script_engine.voz_utils import oraciones_de_texto  # noqa: E402
textos = [t for n in sorted({int(p["cap"]) for p in parrafos}) for p in parrafos if int(p["cap"]) == n
          for t in oraciones_de_texto(p["texto"])]
el = m5.elegir_personaje(textos, pool["personajes"], esc)
print("\ncandidatos (oraciones, primera oración global):")
for c in el["candidatos"]:
    q = next(x for x in pool["personajes"] if x.get("id") == c["id"])
    t, pila = m5.terminos_retencion(q, pool["personajes"])
    print(f"  {c['id']} {c['nombre']}: {c['oraciones']} (primera {c['primera']}) términos {t + ([pila] if pila else [])}")
got_c = {c["id"]: c["oraciones"] for c in el["candidatos"]}
# la tabla del contrato lista los 4 primeros; el resto (≤ 2 oraciones) no figura y se imprime arriba
top = {k: got_c.get(k) for k in CONTRATO_CAND}
fuera = {k: v for k, v in got_c.items() if k not in CONTRATO_CAND and v >= min(CONTRATO_CAND.values())}
print("candidatos del contrato:", "OK" if top == CONTRATO_CAND and not fuera else f"DIFIERE {top} {fuera}",
      "| gana:", r["personaje"]["id"], "| fuera de la tabla del contrato (todos < 3):",
      {k: v for k, v in got_c.items() if k not in CONTRATO_CAND})

print("\n| cap | oraciones/con/racha | contrato | desde-hasta | |")
print("|---|---|---|---|---|")
ok = True
for c in r["caps"]:
    got = (c["oraciones"], c["oraciones_con_personaje"], c["racha_max_sin_personaje"])
    exp = CONTRATO.get(c["cap"])
    ok &= got == exp
    print(f"| {c['cap']} | {'/'.join(map(str, got))} | {'/'.join(map(str, exp))} | {c['racha_desde_hasta']} | "
          f"{'OK' if got == exp else 'DIFIERE'} |")
print("\nrachas vs contrato:", "OK" if ok and len(r["caps"]) == len(CONTRATO) else "DIFIERE")
print("cap_mas_humano:", r["cap_mas_humano"])
