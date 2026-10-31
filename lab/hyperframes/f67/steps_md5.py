# -*- coding: utf-8 -*-
"""F67 §7: foto de _steps/<tid>/ (md5 y mtime de cada archivo) y comparación entre etapas. Solo lectura de _steps.
    python lab/hyperframes/f67/steps_md5.py foto A_antes
    python lab/hyperframes/f67/steps_md5.py compara A_antes A_despues"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

AQUI = Path(__file__).resolve().parent
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
STEPS = AQUI.parents[2] / "data" / "scripts" / "_steps" / TID
FOTOS = AQUI / "md5"


def foto(nombre: str) -> dict:
    FOTOS.mkdir(exist_ok=True)
    d = {p.relative_to(STEPS).as_posix(): [hashlib.md5(p.read_bytes()).hexdigest(), p.stat().st_mtime_ns]
         for p in sorted(STEPS.rglob("*")) if p.is_file()}
    (FOTOS / f"{nombre}.json").write_text(json.dumps(d, indent=0), encoding="utf-8")
    return d


def compara(a: str, b: str) -> list[str]:
    x = json.loads((FOTOS / f"{a}.json").read_text(encoding="utf-8"))
    y = json.loads((FOTOS / f"{b}.json").read_text(encoding="utf-8"))
    return [f"{k}: {(x.get(k) or ['—'])[0][:8]} → {(y.get(k) or ['—'])[0][:8]}" for k in sorted(set(x) | set(y)) if x.get(k) != y.get(k)]


if __name__ == "__main__":
    if sys.argv[1] == "foto":
        print(len(foto(sys.argv[2])), "archivos")
    else:
        print("\n".join(compara(sys.argv[2], sys.argv[3])) or "ninguno cambió")
