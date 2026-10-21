"""F6b: escaleta v3 de Orleans (topic ba6c3cac-f6v3, pool con testimonios de F6a). 1 Pro (hasta 3 con feedback).

Topic = el de ba6c3cac-f5v2 en topics_db (hook, misterio, ángulo…) con el evidence_pool de
data/scripts/_steps/ba6c3cac-f6v3/01_facts_sources.json e id ba6c3cac-f6v3 (topics_db no se toca).
Deja data/scripts/_steps/ba6c3cac-f6v3/01a_escaleta.json, lab/hyperframes/f6/escaleta_orleans.json (copia) y
lab/hyperframes/f6/ESCALETA_orleans.md (legible). Con --frozen re-valida la escaleta guardada sin llamar a Pro.
Uso: PYTHONIOENCODING=utf-8 python lab/hyperframes/f6/f6b_escaleta_orleans.py [--frozen]
"""
from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

V2, V3 = "ba6c3cac-f5v2", "ba6c3cac-f6v3"
STEPS = ROOT / "data" / "scripts" / "_steps" / V3
LAB = Path(__file__).resolve().parent


# F6b-3: validación del analista sobre f6b-2 (2026-10-21), ajustada a la verificación de testimonios
# (F6b3_verificacion.md: solo Q03 de Burton y Q04 de Norman están verificadas)
NOTAS_F6B3 = """1. GANCHO = FLASH-FORWARD (beat 1 con flash_forward: true, intensidad 4): el peor momento adentro — el agua al
   pecho, la oscuridad, días sin que nadie venga. Q05, Q06 y Q13 están SIN VERIFICAR: se usan sin el nombre de quien
   lo dijo («un preso»). Q03 (Edward Burton) está verificada: puede ir con nombre. Sin cifras, con la promesa.
   El cap 2 baja a intensidad 2: cómo se llegó ahí (la decisión del sheriff). Curva objetivo ≈ 4-2-3-4-5-1-3-3.
2. CIERRE: el cap 7 tiene como dato central D61 (el sheriff dice que ningún preso murió ni escapó; después su oficina
   emite 14 órdenes de arresto para fugitivos) y la ausencia de registros. Los dos turistas (T26) a lo sumo como ironía
   en una frase (dato de apoyo), nunca como dato central ni presentados de nuevo. La ÚLTIMA FRASE del video con Vincent
   Norman: su cita Q04 (verificada) puede ir como juicio retrospectivo en el cap 6 o 7. Lenore Burnley (Q08) está sin
   verificar: no se la nombra. Q10 (Eric Balaban, abogado) va a PANTALLA (a_pantalla), no a la voz.
3. La pregunta de pantalla del cap 1 va con el cold open: «¿Por qué nadie vino por ellos?» o una similar que pase la
   rúbrica.
4. 517 una sola vez; nunca «más de 500»."""


def topic_v3() -> dict:
    db = json.loads((ROOT / "data" / "topics_db.json").read_text(encoding="utf-8"))
    t = json.loads(json.dumps(next(t for t in db["topics"] if t["id"] == V2)))
    t.update({"id": V3, "video_id": V3, "guion_version": 3, "escaleta_notas": NOTAS_F6B3,
              "evidence_pool": json.loads((STEPS / "01_facts_sources.json").read_text(encoding="utf-8"))["evidence_pool"]})
    return t


def main() -> None:
    from cost_tracker import cost_tracker
    from script_engine import m01a_escaleta as me
    t = topic_v3()
    if "--frozen" in sys.argv:
        t["escaleta_frozen"] = {"escaleta": str(STEPS / "01a_escaleta.json")}
    log: list[str] = []
    prev = json.loads((STEPS / "01a_escaleta.json").read_text(encoding="utf-8")) if (STEPS / "01a_escaleta.json").exists() else {}
    if "--frozen" in sys.argv and (LAB / "escaleta_orleans_pro_original.json").exists() and not prev.get("_costo_pro"):
        prev = json.loads((LAB / "escaleta_orleans_pro_original.json").read_text(encoding="utf-8"))
    cost_tracker.start_video(V3)
    t0 = time.time()
    try:
        esc = me.generate_escaleta(t, log=log)
    finally:
        rep = cost_tracker.end_video()
        print("\n".join(log))
    esc["_costo"] = {"usd": round(getattr(rep, "total_cost", 0.0) or 0.0, 4), "segundos": round(time.time() - t0, 1)}
    if "--frozen" in sys.argv and (esc.get("_costo_pro") or prev.get("_costo")):     # re-validación: el costo es el de Pro
        esc["_costo"] = esc.get("_costo_pro") or prev["_costo"]
    esc["_costo_pro"] = esc["_costo"]
    (STEPS / "01a_escaleta.json").write_text(json.dumps(esc, ensure_ascii=False, indent=2), encoding="utf-8")
    shutil.copy2(STEPS / "01a_escaleta.json", LAB / "escaleta_orleans.json")
    md = me.to_markdown(esc, t["evidence_pool"])
    md += f"\n---\nCosto: US$ {esc['_costo']['usd']} · {esc['_costo']['segundos']} s · intentos: {len(esc.get('_intentos') or [])}\n"
    (LAB / "ESCALETA_orleans.md").write_text(md, encoding="utf-8")
    print(md)


if __name__ == "__main__":
    main()
