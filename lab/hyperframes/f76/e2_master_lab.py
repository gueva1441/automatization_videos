"""F76 E2 — lab: master_mp4 sobre la COPIA de Wittenoom (nunca output/). US$ 0, sin API."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from script_engine.audio_master import master_mp4  # noqa: E402

HERE = Path(__file__).resolve().parent
COPIA = HERE / "wittenoom_copia.mp4"
LOG = HERE / "e2.log"
RESULT = HERE / "e2_result.json"

assert "output" not in COPIA.parts, COPIA

lineas: list[str] = []


def log(s: str) -> None:
    print(s, flush=True)
    lineas.append(s)


log(f"E2 master_mp4 sobre {COPIA}")
res = master_mp4(COPIA, log=log)
log(f"pasadas: {len(res['pasadas'])} · elegida: {res['elegida']['pasada']} · aviso: {res['aviso']}")
LOG.write_text("\n".join(lineas) + "\n", encoding="utf-8")
RESULT.write_text(json.dumps(res, ensure_ascii=False, indent=2), encoding="utf-8")
