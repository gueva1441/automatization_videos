"""F5e: regenera SOLO las fotos que Omar marcó «↻ regenerar» en QA Studio (output/<id>/assets/_qa_marks.json), con el
MISMO prompt del script y otra semilla. Sin reescritura ni validador de visión. Cada regeneración deja backup en
assets/_qa_backups/, invalida el clip horneado del cap (fase2b lo rehace con --reuse-visuals) y queda anotada en
`done` del mismo json; la marca se borra si salió bien.
Uso: PYTHONIOENCODING=utf-8 python lab/hyperframes/f5/regen_marcadas.py [--topic ba6c3cac-f5v2] [--dry-run]
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))


def main() -> None:
    import qa_studio_server as qs
    ap = argparse.ArgumentParser()
    ap.add_argument("--topic", default="ba6c3cac-f5v2")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    state = qs.QAState(a.topic, ROOT)
    d = qs.load_marks(state)
    marks = d["marks"]
    print(f"{len(marks)} foto(s) marcada(s) en {qs.marks_path(state)}")
    for img, m in sorted(marks.items()):
        entry = state.resolve_fix_entry(img)
        print(f"  {img} · {m['cap']} · prompt {'OK' if entry else 'NO RESUELTO'}: "
              f"{(entry or {}).get('prompt', '')[:90]}…")
    if a.dry_run or not marks:
        return
    for img, m in sorted(list(marks.items())):
        attempt = len(d["done"].get(img) or []) + 1
        ok, why, seed = qs._reseed_core(state, a.topic, m["cap"], img, attempt=attempt)
        print(f"  {'✓' if ok else '✗'} {img} semilla {seed}" + (f" — {why}" if why else ""))
        if ok:
            d["done"].setdefault(img, []).append({"seed": seed, "ts": datetime.now().strftime("%Y-%m-%d %H:%M:%S")})
            d["marks"].pop(img, None)
        qs.marks_path(state).write_text(json.dumps(d, ensure_ascii=False, indent=1), encoding="utf-8")


if __name__ == "__main__":
    main()
