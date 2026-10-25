"""F28 §C.4: tiempos pase por pase de dos corridas de fase2b de Vajont (F27 en fila con libx264 y 4 workers; F28c con
NVENC, gfx de a 3 caps y 6 workers), leídos de sus logs. → lab/hyperframes/f28/c/tiempos.json + tabla en pantalla.
Pases: flow_director (LLM), visual base de cada cap (de su primer «[depthflow]» al último antes del gfx), gfx de cada
cap (lo que reporta «✓ [gfx] chNN OK en Ns»), crashes de DepthFlow (reintentos), música y total.
"""
from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
LAB = Path(__file__).resolve().parent
LOGS = {"F27": ROOT / "lab" / "hyperframes" / "f27" / "b" / "fase2b.out", "F28c 3 caps (corrida 1)": LAB / "fase2b_run1_3caps.out",
        "F28c 2 caps (corrida 2, cancelada)": LAB / "fase2b_run2_2caps_cancelada.out"}
TS = re.compile(r"^\[(\d\d:\d\d:\d\d)\]")


def leer(p: Path) -> dict:
    lineas = p.read_text(encoding="utf-8", errors="replace").splitlines()
    t = lambda s: datetime.strptime(s, "%H:%M:%S")  # noqa: E731
    ts = [(t(m.group(1)), l) for l in lineas if (m := TS.match(l))]
    out: dict = {"crashes_depthflow": sum(1 for _, l in ts if "DepthFlowError" in l),
                 "gfx_cayo_a_base_clip": [m.group(1) for _, l in ts if (m := re.search(r"\[gfx\] (ch\d\d) fallback", l))]}
    ini, fin = ts[0][0], ts[-1][0]
    out["total_min"] = round((fin - ini).total_seconds() / 60, 1)
    fd = [x for x, l in ts if "[flow_director]" in l]
    out["flow_director_s"] = int((fd[-1] - fd[0]).total_seconds()) if len(fd) >= 2 else None
    out["gfx_s"] = {m.group(1): int(m.group(2)) for _, l in ts if (m := re.search(r"\[gfx\] (ch\d\d) OK en (\d+)s", l))}
    vis: dict[str, list] = {}
    for x, l in ts:
        m = re.search(r"\[depthflow\] \w+ .* sobre (ch\d\d)_", l)
        if m:
            vis.setdefault(m.group(1), [x, x])[1] = x
    out["visual_base_s"] = {c: int((b - a).total_seconds()) + 30 for c, (a, b) in vis.items()}   # +30: el último clip
    mus = [l for l in lineas if "⏱ música" in l]
    out["musica"] = mus[-1].strip() if mus else None
    return out


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    res = {k: leer(p) for k, p in LOGS.items() if p.exists()}
    (LAB / "tiempos.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    for k, v in res.items():
        print(k, json.dumps(v, ensure_ascii=False))


if __name__ == "__main__":
    main()
