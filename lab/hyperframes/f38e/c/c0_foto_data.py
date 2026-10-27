"""F38e §C · foto de data/ (mtime + md5 de cada archivo) antes y después de la tanda; nada se escribe en data/.

    python lab/hyperframes/f38e/c/c0_foto_data.py antes     → c/data_foto_antes.json
    python lab/hyperframes/f38e/c/c0_foto_data.py despues   → c/data_foto_despues.json + diff contra `antes` (pegado)
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
DATA = ROOT / "data"


def foto() -> dict[str, dict]:
    out = {}
    for f in sorted(DATA.rglob("*")):
        if f.is_file():
            st = f.stat()
            out[str(f.relative_to(ROOT)).replace("\\", "/")] = {
                "mtime": st.st_mtime, "size": st.st_size, "md5": hashlib.md5(f.read_bytes()).hexdigest()}
    return out


def main(cual: str) -> int:
    f = foto()
    (HERE / f"data_foto_{cual}.json").write_text(json.dumps(f, indent=1), encoding="utf-8")
    print(f"data/: {len(f)} archivos · foto {cual} → {HERE / f'data_foto_{cual}.json'}")
    if cual == "despues":
        a = json.loads((HERE / "data_foto_antes.json").read_text(encoding="utf-8"))
        cambiados = sorted(k for k in set(a) | set(f) if a.get(k) != f.get(k))
        print(f"antes {len(a)} · después {len(f)} · cambiados/nuevos/borrados: {cambiados or 'ninguno'}")
        return 1 if cambiados else 0
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1] if len(sys.argv) > 1 else "antes"))
