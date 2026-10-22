"""F9 §3.4: desfase del forced alignment (texto limpio) contra Whisper en los caps de prueba de la voz v4.

Las etiquetas de v4 meten pausas que el texto alineado no tiene: esto mide si el alineado de ElevenLabs sigue pegado al
audio. Por cada palabra que coincide en las dos (alineadas por secuencia), desfase = inicio ElevenLabs − inicio Whisper.
Límite: 150 ms (mediana y p95). Uso (venv con faster-whisper):
    C:/CLAUDE_PROJECTS/viral-video-pipeline/.venv/Scripts/python.exe lab/hyperframes/f9/f9_sync.py
Escribe lab/hyperframes/f9/sync_f9.json.
"""
from __future__ import annotations

import difflib
import json
import re
import statistics
import sys
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
VIDS = {"msnarrador": "ba6c3cac-f7r3-f9voz", "bill": "ba6c3cac-f7r3-f9voz-bill"}
LIMIT_MS = 150


def norm(w: str) -> str:
    w = "".join(c for c in unicodedata.normalize("NFD", str(w).lower()) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9ñ]", "", w)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    from faster_whisper import WhisperModel
    model = WhisperModel("small", device="cpu", compute_type="int8")
    out = {}
    for name, vid in VIDS.items():
        d = ROOT / "output" / "audio" / vid
        for ts in sorted(d.glob("ch*_timestamps.json")):
            cap = ts.name[:4]
            el = [w for w in json.loads(ts.read_text(encoding="utf-8")) if norm(w["word"])]
            segs, _ = model.transcribe(str(d / f"{cap}.mp3"), language="es", word_timestamps=True, vad_filter=False)
            wh = [{"word": w.word, "start": w.start} for s in segs for w in (s.words or []) if norm(w.word)]
            a, b = [norm(w["word"]) for w in el], [norm(w["word"]) for w in wh]
            diffs = []
            for blk in difflib.SequenceMatcher(None, a, b, autojunk=False).get_matching_blocks():
                for k in range(blk.size):
                    diffs.append(1000 * (el[blk.a + k]["start"] - wh[blk.b + k]["start"]))
            ab = sorted(abs(x) for x in diffs)
            out[f"{name}/{cap}"] = {
                "palabras_alineado": len(el), "palabras_whisper": len(wh), "coinciden": len(diffs),
                "mediana_ms": round(float(statistics.median(diffs)), 1) if diffs else None,
                "p95_abs_ms": round(float(ab[int(0.95 * (len(ab) - 1))]), 1) if ab else None,
                "max_abs_ms": round(float(ab[-1]), 1) if ab else None,
                "fuera_de_150ms_pct": round(100 * sum(1 for x in ab if x > LIMIT_MS) / len(ab), 1) if ab else None}
            print(name, cap, out[f"{name}/{cap}"], flush=True)
    (Path(__file__).resolve().parent / "sync_f9.json").write_text(json.dumps(out, ensure_ascii=False, indent=1),
                                                                   encoding="utf-8")


if __name__ == "__main__":
    main()
