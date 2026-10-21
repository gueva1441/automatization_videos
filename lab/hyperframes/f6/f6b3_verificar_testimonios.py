"""F6b-3: verificación de las citas testimonio del pool de Orleans v3 (1 Flash + Google Search por cita, ≈ US$ 0.10).
Actualiza data/scripts/_steps/ba6c3cac-f6v3/01_facts_sources.json en el lugar (caché: 00e_verificacion.json) y deja
lab/hyperframes/f6/F6b3_verificacion.md.
Uso: PYTHONIOENCODING=utf-8 python lab/hyperframes/f6/f6b3_verificar_testimonios.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
STEPS = ROOT / "data" / "scripts" / "_steps" / "ba6c3cac-f6v3"
REPORT = Path(__file__).resolve().parent / "F6b3_verificacion.md"


def main() -> None:
    from cost_tracker import cost_tracker
    from researcher_steps.verify_quotes import verify_testimonios
    f = STEPS / "01_facts_sources.json"
    fs = json.loads(f.read_text(encoding="utf-8"))
    log: list[str] = []
    cost_tracker.start_video("ba6c3cac-f6v3")
    t0 = time.time()
    try:
        n = verify_testimonios(fs["evidence_pool"], cache=STEPS / "00e_verificacion.json", log=log,
                               retry_model="gemini-2.5-pro")
    finally:
        rep = cost_tracker.end_video()
    usd = round(getattr(rep, "total_cost", 0.0) or 0.0, 4)
    fs.setdefault("_f6b3", {})["verificacion"] = {"conteo": n, "log": log, "usd_tokens": usd}
    f.write_text(json.dumps(fs, ensure_ascii=False, indent=2), encoding="utf-8")
    lines = ["# F6b-3 — Verificación de testimonios (Orleans v3)", "",
             "- Flash + búsqueda; las citas con nombre que no se verificaron, 2.º intento con Pro + búsqueda.",
             f"- {n['verificada']} verificadas · {n['sin_verificar']} sin verificar · {time.time() - t0:.0f} s · "
             f"US$ {usd} de tokens (la búsqueda de Google no la cuenta cost_tracker: ≤ US$ 0.035 por cita si se pasa "
             "la cuota gratis diaria).",
             "- **Verificada** = Flash + Google Search encontró la cita atribuida a esa persona y dio una URL cuyo dominio "
             "está entre las fuentes reales de la búsqueda. Una **sin verificar** no se usa con nombre en la narración.",
             "", "| id | autor | estado | url_fuente / motivo | original |", "|---|---|---|---|---|"]
    for q in fs["evidence_pool"]["citas"]:
        v = q.get("verificacion")
        if not v:
            continue
        lines.append(f"| {q['id']} | {q.get('autor')} | **{v['estado']}** | "
                     f"{v['url_fuente'] if v['estado'] == 'verificada' else v['motivo']} | "
                     f"{(v.get('cita_original') or '')[:120].replace('|', '/')} |")
    lines += ["", "Testigos verificados: " + ", ".join(
        p["nombre"] for p in fs["evidence_pool"]["personajes"] if p.get("testigo_verificado")) or "ninguno"]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    main()
