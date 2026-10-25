"""F26 §D.4 — PreToolUse Bash: antes de `python … fase1_5.py` o `python … fase2a.py`, lee `lab/TOPE_TANDA.json`
(`{"usd": N}`, opcional `"desde": "AAAA-MM-DDTHH:MM:SS"`) y suma el gasto de la tanda en `data/cost_history.json`
(los videos con `created_at` desde `desde`; sin `desde`, desde que se escribió el archivo del tope). Si el gasto ya
llegó al tope, bloquea (exit 2). Sin archivo de tope, no hace nada.
"""
from __future__ import annotations

import json
import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comun import ROOT, bloquear, comando, leer_evento, segmentos  # noqa: E402

SCRIPTS = ("fase1_5.py", "fase2a.py")


def corre_script(cmd: str) -> str | None:
    for w in segmentos(cmd):
        if w and Path(w[0]).name.lower().startswith(("python", "py")):
            for a in w[1:]:
                if Path(a).name in SCRIPTS:
                    return Path(a).name
                if a == "-m" or not a.startswith("-"):
                    break
    return None


def _leer_json(p: Path):
    raw = p.read_bytes()
    try:
        return json.loads(raw.decode("utf-8"))
    except UnicodeDecodeError:                       # cost_tracker escribe sin encoding (cp1252 en Windows)
        return json.loads(raw.decode("cp1252", errors="replace"))


def gasto_desde(historial: list, desde: datetime) -> float:
    total = 0.0
    for v in historial:
        try:
            t = datetime.fromisoformat(str(v.get("created_at"))[:19])
        except ValueError:
            continue
        if t >= desde:
            total += float(v.get("total_cost") or 0)
    return round(total, 4)


def revisar(cmd: str, root: Path = ROOT) -> str | None:
    s = corre_script(cmd)
    if not s:
        return None
    tp = root / "lab" / "TOPE_TANDA.json"
    if not tp.exists():
        return None
    tope = _leer_json(tp)
    desde = (datetime.fromisoformat(tope["desde"]) if tope.get("desde")
             else datetime.fromtimestamp(tp.stat().st_mtime))
    hp = root / "data" / "cost_history.json"
    g = gasto_desde(_leer_json(hp), desde) if hp.exists() else 0.0
    if g >= float(tope["usd"]):
        return (f"tope_tanda: la tanda ya gastó US$ {g:.2f} (cost_history desde {desde:%Y-%m-%d %H:%M}) y el tope es "
                f"US$ {float(tope['usd']):.2f} (lab/TOPE_TANDA.json): {s} no arranca")
    return None


def main() -> None:
    ev = leer_evento()
    motivo = revisar(comando(ev), Path(ev.get("cwd") or ROOT))
    if motivo:
        bloquear(motivo)


if __name__ == "__main__":
    main()
