"""test_module_fase2b_only_cap.py — F1b: `fase2b --only-cap`.

- flags presentes en el CLI;
- integración (Orleans ch02, ~45 s): --only-cap sin --gfx produce un segmento BYTE-IDÉNTICO al del
  cap en la corrida completa (sha de referencia medido en F1 con la corrida A), sin tocar
  topics_db ni el _final.mp4. Se saltea si no están los datos del video.
Correr: python -m pytest test_module_fase2b_only_cap.py -q
"""
import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parent
VID = "ba6c3cac-a091-41c0-8dad-afd2f4364747"
REF_SHA16 = "ee5e98c3968bd6d3"     # seg ch02 de la corrida completa A (F1_REPORT §3)
WORK = REPO / "output" / VID / "_fase2b_work"


def test_flags_en_cli():
    out = subprocess.run([sys.executable, "fase2b.py", "--help"], cwd=REPO, capture_output=True,
                         text=True, encoding="utf-8", errors="replace").stdout
    assert "--only-cap" in out and "--gfx-debug" in out


@pytest.mark.skipif(not (WORK / "ch02_flux_visual.mp4").exists(), reason="sin datos de Orleans")
def test_only_cap_sin_gfx_byte_identico():
    final = REPO / "output" / VID / f"{VID}_final.mp4"
    db = REPO / "data" / "topics_db.json"
    seg = WORK / "ch02_segment_only.mp4"
    # el test NO debe pisar el segmento que el usuario esté revisando (gfx_review_ch02.html lo usa)
    backup = seg.with_name(seg.name + ".test_bak")
    if seg.exists():
        seg.replace(backup)
    try:
        before = (final.stat().st_mtime, db.read_bytes())
        r = subprocess.run([sys.executable, "fase2b.py", VID, "--reuse-visuals", "--only-cap", "ch02"],
                           cwd=REPO, capture_output=True, text=True, encoding="utf-8", errors="replace",
                           env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"}, timeout=900)
        assert r.returncode == 0, r.stdout[-500:]
        assert hashlib.sha256(seg.read_bytes()).hexdigest()[:16] == REF_SHA16
        assert (final.stat().st_mtime, db.read_bytes()) == before      # ni _final.mp4 ni topics_db
    finally:
        if backup.exists():
            backup.replace(seg)


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
