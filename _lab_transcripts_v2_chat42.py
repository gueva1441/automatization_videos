"""
_lab_transcripts_v2_chat42.py — FASE A (chat 42→43). LAB read-only, $0 API, no toca
pipeline. Re-extrae los transcripts de las 28 joyas del Molde 1 CON TIMESTAMPS (segments)
+ marca `formato` (densidad de muletillas) y `drift` (UFO/alien/etc en título/puerta).

NO pisa el v1 (_lab_transcripts_chat42.py + transcripts_chat42.json = evidencia).
Reusa el fetch robusto del v1 (proxy IP-fresca-por-video, track EN más largo, retry SSL).

Output: _lab_out/transcripts_v2_chat42.json

USO:
    python -X utf8 _lab_transcripts_v2_chat42.py            # re-extrae (red)
    python -X utf8 _lab_transcripts_v2_chat42.py --smoke    # solo clasificadores (sin red)
"""
from __future__ import annotations

import json
import re
import sys
import time
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

IN_JSON = Path("_lab_out/molde1_chat42_20260603_010310.json")
OUT_JSON = Path("_lab_out/transcripts_v2_chat42.json")
LANGS = ["en", "en-US", "en-GB"]
SLEEP_SEC = 1.5

# ─── Clasificadores PUROS (los ejerce GATE A) ───
_FILLERS = ["uh", "um", "you know", "i mean", "gonna", "kinda"]
_DRIFT_WORDS = ["ufo", "alien", "pentagon", "navy", "sphere"]


def filler_rate(text: str) -> float:
    """Muletillas por 1000 palabras."""
    words = re.findall(r"\b[\w']+\b", text.lower())
    n = len(words)
    if n == 0:
        return 0.0
    t = " " + text.lower() + " "
    c = 0
    for f in _FILLERS:
        c += len(re.findall(r"\b" + re.escape(f) + r"\b", t))
    return c / n * 1000.0


def detect_formato(text: str) -> str:
    """rate>1.5 → charla_entrevista; rate<0.3 → documental_narrado; resto → mixto."""
    r = filler_rate(text)
    if r > 1.5:
        return "charla_entrevista"
    if r < 0.3:
        return "documental_narrado"
    return "mixto"


def detect_drift(title: str, puerta: str | None) -> bool:
    s = (title + " " + (puerta or "")).lower()
    return any(w in s for w in _DRIFT_WORDS)


# ─── SMOKE (GATE A) ───
def run_smoke() -> int:
    print("  SMOKE clasificadores FASE A (sin red)")
    fails = []
    charla = "So uh you know I mean it was kinda gonna be um a thing you know"
    doc = ("July 19th 1969 as Apollo 11 makes its final approach mysterious lights "
           "appear dazzling the astronauts the truth was buried for decades")
    for name, txt, exp in [("charla", charla, "charla_entrevista"),
                           ("documental", doc, "documental_narrado")]:
        got = detect_formato(txt)
        ok = got == exp
        print(f"    formato({name}) = {got} (rate={filler_rate(txt):.2f}) esp {exp}  "
              f"{'OK' if ok else 'FAIL'}")
        if not ok:
            fails.append(f"formato {name}={got}")
    for name, title, puerta, exp in [
        ("drift-ufo", "Pentagon releases UFO videos", "declassified ocean", True),
        ("no-drift", "15 Largest Abandoned Cities", "ghost towns", False)]:
        got = detect_drift(title, puerta)
        ok = got == exp
        print(f"    drift({name}) = {got} esp {exp}  {'OK' if ok else 'FAIL'}")
        if not ok:
            fails.append(f"drift {name}={got}")
    print("  " + "─" * 50)
    if fails:
        print(f"  [SMOKE FAIL] {fails}")
        return 1
    print("  [SMOKE OK]")
    return 0


# ─── Fetch con segments (reusa el proxy/api del v1) ───
def _fetch_segments(video_id: str):
    """(lang, segments) — track EN más largo; segments raw [{start,duration,text}]."""
    from _lab_transcripts_chat42 import _new_api
    from youtube_transcript_api import NoTranscriptFound
    ytt = _new_api()
    tlist = ytt.list(video_id)
    try:
        transcripts = list(tlist)
    except TypeError:
        transcripts = (list(getattr(tlist, "_transcripts", {}).values())
                       if hasattr(tlist, "_transcripts") else [])
    if not transcripts:
        raise NoTranscriptFound(video_id, LANGS, tlist)  # type: ignore[call-arg]

    en = [t for t in transcripts if getattr(t, "language_code", "") in LANGS]
    if en:
        pool = en
    else:
        manual = [t for t in transcripts if not getattr(t, "is_generated", True)]
        gen = [t for t in transcripts if getattr(t, "is_generated", False)]
        pool = (manual or gen)[:1]

    best, best_len, best_lang, last_err = None, -1, None, None
    for t in pool:
        try:
            raw = t.fetch().to_raw_data()   # [{text, start, duration}, ...]
        except Exception as e:  # noqa: BLE001
            last_err = e
            continue
        total = sum(len(s.get("text", "")) for s in raw)
        if total > best_len:
            best, best_len, best_lang = raw, total, getattr(t, "language_code", "?")
    if best is None:
        raise last_err if last_err else NoTranscriptFound(video_id, LANGS, tlist)  # type: ignore[call-arg]
    return best_lang, best


def main() -> int:
    if "--smoke" in sys.argv:
        return run_smoke()
    if run_smoke() != 0:
        print("  smoke falló → no sigo a la red.")
        return 1

    from youtube_transcript_api import (
        TranscriptsDisabled, NoTranscriptFound, VideoUnavailable)
    definitive = (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable)

    if not IN_JSON.exists():
        print(f"❌ no existe el insumo: {IN_JSON}")
        return 1
    rows = json.loads(IN_JSON.read_text(encoding="utf-8"))
    by_vid: dict[str, dict] = {}
    for r in rows:
        v = r.get("video_id")
        if v and v not in by_vid:
            by_vid[v] = r
    items = list(by_vid.values())
    print(f"\n  {len(rows)} filas → {len(items)} video_ids únicos\n")

    out = []
    ok = 0
    seg_ok = 0
    for i, r in enumerate(items, 1):
        vid = r["video_id"]
        title = r.get("title", "")
        is_jewel = bool(r.get("new"))
        print(f"  [{i:>2}/{len(items)}] {'💎' if is_jewel else '·'} {vid}  {title[:46]}",
              flush=True)

        status, lang, error, segments = "sin_transcript", None, None, []
        try:
            lang, segments = _fetch_segments(vid)
            status = "ok"
        except definitive as e:
            error = type(e).__name__
        except Exception:  # noqa: BLE001  transitorio → 1 retry IP fresca
            try:
                time.sleep(2.0)
                lang, segments = _fetch_segments(vid)
                status = "ok"
            except definitive as e2:
                error = type(e2).__name__
            except Exception as e2:  # noqa: BLE001
                error = f"{type(e2).__name__}: {e2}"[:160]

        transcript = " ".join(s.get("text", "").strip() for s in segments
                              if s.get("text", "").strip())
        formato = detect_formato(transcript) if status == "ok" else None
        drift = detect_drift(title, r.get("puerta"))

        # GATE B: contar cuántos traen start/duration > 0
        if status == "ok" and segments and any(
                (s.get("start", 0) or 0) > 0 and (s.get("duration", 0) or 0) > 0
                for s in segments):
            seg_ok += 1
        if status == "ok":
            ok += 1
            print(f"        ✓ lang={lang} {len(segments)} segs {len(transcript):,} chars "
                  f"formato={formato} drift={drift}")
        else:
            print(f"        ⚠ sin_transcript: {error}")

        out.append({
            "video_id": vid, "title": title, "subnicho": r.get("subnicho"),
            "puerta": r.get("puerta"), "views": r.get("views"), "ratio": r.get("ratio"),
            "median": r.get("median"), "new": is_jewel, "old": r.get("old"),
            "lang": lang, "status": status, "error": error,
            "formato": formato, "drift": drift,
            "segments": segments, "transcript": transcript,
        })
        time.sleep(SLEEP_SEC)

    OUT_JSON.parent.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    print("\n" + "─" * 60)
    print(f"  OK: {ok}/{len(items)} | con segments start/duration>0: {seg_ok}/{ok}")
    from collections import Counter
    fc = Counter(o["formato"] for o in out if o["status"] == "ok")
    print(f"  formato (ok): {dict(fc)}")
    print(f"  drift=True: {sum(1 for o in out if o['drift'])}")
    print(f"  guardado: {OUT_JSON}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
