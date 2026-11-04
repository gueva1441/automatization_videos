"""F73 A+B, prueba real en Wittenoom: run_candidates (archiva lo desfasado, 3 paquetes, fotos con madres) + costo."""
import json
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(R))

from cost_tracker import cost_tracker  # noqa: E402
from script_engine import m09_packaging as m  # noqa: E402

TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
cost_tracker.start_video(TID)
try:
    m.run_candidates(TID)
finally:
    rep = cost_tracker.end_video()
    if rep is not None:
        filas = [{"servicio": e.service, "desc": e.description, "usd": round(e.total_cost, 4)} for e in rep.entries]
        total = round(sum(f["usd"] for f in filas), 4)
        (Path(__file__).parent / "costo.json").write_text(json.dumps({"total_usd": total, "filas": filas}, indent=1,
                                                                      ensure_ascii=False), encoding="utf-8")
        print(f"COSTO total US$ {total}")
