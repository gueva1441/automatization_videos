"""F30 §D — SSIM por cap entre los chNN_gfx.mp4 de v3 y los de v3b (f8s3-vajont-f30): el cap entero, las escenas
cocidas (safe) y el resto (escenas 3D de los caps flux y los caps híbridos, que no se cuecen), sin los ±1 s de los
cortes. Uso: python -I lab/hyperframes/f30/f30_ssim_d.py"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB))
import f30_ssim as fs  # noqa: E402

V3B = ROOT / "output" / "f8s3-vajont-f30" / "_fase2b_work"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    res = {}
    for c in range(1, 8):
        cap = f"ch{c:02d}"
        v = fs.ssim_por_cuadro(fs.V3 / f"{cap}_gfx.mp4", V3B / f"{cap}_gfx.mp4", LAB / "d" / f"{cap}.json")
        plan = json.loads((V3B / f"gfx_plan_{cap}.resolved.json").read_text(encoding="utf-8"))["plan"]
        mov = {m["scene"]: m["forma"] for m in (plan.get("identity") or {}).get("movimientos") or []}
        sc = fs.escenas(cap)
        cortes = {round(a * fs.FPS) for a, _ in sc[1:]}
        cerca = lambda k: any(abs(k - c0) <= fs.FPS for c0 in cortes)          # noqa: E731
        safe_k, resto_k = [], []
        for i, (a, b) in enumerate(sc):
            dst = safe_k if mov.get(i) not in (None, "3D") else resto_k
            dst += [k for k in range(round(a * fs.FPS), min(len(v), round(b * fs.FPS))) if not cerca(k)]

        def st(ks):
            x = [v[k] for k in ks]
            return {"cuadros": len(x), "media": round(sum(x) / len(x), 4), "min": round(min(x), 4)} if x else None
        res[cap] = {"cap": {"cuadros": len(v), "media": round(sum(v) / len(v), 4), "min": round(min(v), 4)},
                    "safe_sin_cortes": st(safe_k), "resto_sin_cortes": st(resto_k),
                    "cortes_±1s": st([k for k in range(len(v)) if cerca(k)])}
        print(cap, res[cap], flush=True)
    (LAB / "d" / "ssim_d.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
