"""F5e: sincronía voz ↔ subtítulo de Orleans v2. Los subtítulos (ASS karaoke por palabra) salen de
output/audio/<id>/chNN_timestamps.json (forced alignment de ElevenLabs, que avisó «loss alto» 0.53–0.65). Esto mide
esos tiempos contra una transcripción independiente (faster-whisper, palabras con tiempo) del mismo chNN.mp3:
por cada palabra que coincide en las dos (alineadas por secuencia), desfase = inicio ElevenLabs − inicio Whisper.
Además chequea que el primer Dialogue de cada chNN_subs.ass arranque donde dicen los timestamps (+ el pre-pad del
hook en ch01). Escribe lab/hyperframes/f5/produccion/SYNC_v2.md.
Uso (venv con faster-whisper): C:/CLAUDE_PROJECTS/viral-video-pipeline/.venv/Scripts/python.exe lab/hyperframes/f5/sync_check.py
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
V2 = sys.argv[1] if len(sys.argv) > 1 else "ba6c3cac-f5v2"
AUDIO = ROOT / "output" / "audio" / V2
WORK = ROOT / "output" / V2 / "_fase2b_work"
OUT = Path(__file__).resolve().parent / "produccion" / ("SYNC_v2.md" if V2 == "ba6c3cac-f5v2" else f"SYNC_{V2[:8]}_v1.md")
LIMIT_MS = 150


def norm(w: str) -> str:
    w = "".join(c for c in unicodedata.normalize("NFD", str(w).lower()) if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9ñ]", "", w)


def ass_first_start(path: Path) -> float | None:
    for ln in path.read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"Dialogue:\s*\d+,(\d+):(\d+):(\d+)\.(\d+),", ln)
        if m:
            h, mi, s, cs = map(int, m.groups())
            return h * 3600 + mi * 60 + s + cs / 100
    return None


def main() -> None:
    from faster_whisper import WhisperModel
    try:
        model = WhisperModel("small", device="cuda", compute_type="float16")
    except Exception:  # noqa: BLE001 — sin GPU
        model = WhisperModel("small", device="cpu", compute_type="int8")
    rows, L = [], ["# Sincronía voz ↔ subtítulo — Orleans v2", "",
                   "Desfase = inicio de la palabra en los timestamps de ElevenLabs (los que usan los subtítulos) − inicio "
                   "de la misma palabra según faster-whisper (modelo small) sobre el mismo audio. Positivo = el "
                   f"subtítulo llega tarde. Umbral: {LIMIT_MS} ms.", "",
                   "| cap | palabras comparadas | mediana | p95 \\|desfase\\| | máx \\|desfase\\| | > 150 ms | 1.er Dialogue ASS vs timestamps |",
                   "|---|---|---|---|---|---|---|"]
    worst_all = []
    for n in range(1, 8):
        cap = f"ch{n:02d}"
        el = json.loads((AUDIO / f"{cap}_timestamps.json").read_text(encoding="utf-8"))
        el = el if isinstance(el, list) else el.get("words")
        segs, _ = model.transcribe(str(AUDIO / f"{cap}.mp3"), language="es", word_timestamps=True, vad_filter=False)
        wh = [{"word": w.word, "start": w.start, "end": w.end} for s in segs for w in (s.words or [])]
        a = [norm(x["word"]) for x in el]
        b = [norm(x["word"]) for x in wh]
        sm = difflib.SequenceMatcher(a=a, b=b, autojunk=False)
        d = []
        for blk in sm.get_matching_blocks():
            for k in range(blk.size):
                i, j = blk.a + k, blk.b + k
                if a[i] and len(a[i]) >= 3:
                    d.append((float(el[i]["start"]) - float(wh[j]["start"]), el[i]["word"], float(el[i]["start"])))
        offs = [x[0] for x in d]
        ab = sorted(abs(x) for x in offs)
        p95 = ab[int(0.95 * (len(ab) - 1))] if ab else 0.0
        over = [x for x in d if abs(x[0]) * 1000 > LIMIT_MS]
        worst = sorted(d, key=lambda x: -abs(x[0]))[:3]
        worst_all += [(cap, *w) for w in worst]
        ass = WORK / f"{cap}_subs.ass"
        first = ass_first_start(ass) if ass.exists() else None
        pre = 0.0                                   # el pre-pad del hook solo va con --hook (no se usó)
        ass_note = (f"{first:.2f} s vs {float(el[0]['start']) + pre:.2f} s" if first is not None else "sin ASS")
        rows.append((cap, len(d), statistics.median(offs) if offs else 0.0, p95, ab[-1] if ab else 0.0, len(over)))
        L.append(f"| {cap} | {len(d)} de {len(el)} | {statistics.median(offs) * 1000:+.0f} ms | {p95 * 1000:.0f} ms | "
                 f"{(ab[-1] if ab else 0) * 1000:.0f} ms | {len(over)} ({100 * len(over) / max(1, len(d)):.0f} %) | {ass_note} |")
        print(cap, len(d), round(statistics.median(offs) * 1000), round(p95 * 1000), len(over), flush=True)
    L += ["", "## Las 3 palabras con más desfase por cap", ""]
    L += [f"- {c} · «{w}» @ {t:.2f} s: {o * 1000:+.0f} ms" for c, o, w, t in worst_all]
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(OUT)


if __name__ == "__main__":
    sys.exit(main())
