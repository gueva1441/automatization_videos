"""
test_transcript_fetch.py — C3: baja 2-3 transcripts por video_id reusando el proxy de prod,
confirmando que devuelve texto y no throttlea. Usa video_ids del corpus del lab.

Correr:  python -X utf8 test_transcript_fetch.py
"""
from __future__ import annotations

import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from script_engine.transcript_fetch import fetch_transcript

# video_ids reales del corpus transcripts_chat42.json (#1, #11, #13)
SAMPLE = [
    ("W_LRY_vozfA", "Moon Mysteries (NASA Unexplained Files)"),
    ("kgvJD9pKl5Q", "(control: cualquiera con captions)"),
    ("Lwz9KxoX7mY", "(control 2)"),
]


def main():
    print("C3 — transcript_fetch con proxy de prod\n")
    ok_count = 0
    for vid, label in SAMPLE:
        txt = fetch_transcript(vid)
        n = len(txt)
        status = "OK" if n > 200 else ("VACÍO" if n == 0 else "corto")
        ok_count += (n > 200)
        print(f"  {vid}  len={n:>7}  {status}   {label}")
        if n > 200:
            print(f"     head: {txt[:90]}...")
    print(f"\n  {ok_count}/{len(SAMPLE)} con transcript usable")
    print(f"C3 transcript_fetch: {'PASS' if ok_count >= 1 else 'FAIL — proxy/lib?'}")
    print("  (si throttlea, todos VACÍO → revisar _proxies_dict / sesión)")


if __name__ == "__main__":
    main()
