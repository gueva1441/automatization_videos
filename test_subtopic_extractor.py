"""
test_subtopic_extractor.py — C1: valida script_engine.subtopic_extractor contra el corpus,
reproduciendo: #15→~17, #17→~18, #20→~30, #6 alto (~89), #23 bajo (~8), y que el roster
limpio de #15/#17/#20 mantiene Mary Celeste / USS Cyclops / Gustloff / Doña Paz / Ourang Medan.

Correr:  python -X utf8 test_subtopic_extractor.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from script_engine.subtopic_extractor import extract_segment_subjects

CORPUS = Path("_lab_out/transcripts_chat42.json")

# (n, rango esperado aprox, must_contain substrings)
EXPECT = {
    15: ((12, 24), ["mary celeste", "cyclops"]),
    17: ((12, 26), ["gustloff", "paz"]),
    20: ((20, 40), ["ourang medan"]),
    6:  ((40, 130), []),    # alto, NO se espera 0 (filtro nicho no es del extractor)
    23: ((3, 16), []),      # bajo
}


def clean(raw):
    t = re.sub(r"\[(Music|Applause|Laughter|Audio|música)\]", " ", raw or "", flags=re.IGNORECASE)
    t = re.sub(r">>+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def main():
    videos = json.loads(CORPUS.read_text(encoding="utf-8"))
    by_n = {i: v for i, v in enumerate(videos, 1)}
    print("C1 — subtopic_extractor (sujeto-de-segmento) vs lab\n")
    all_pass = True
    for n, ((lo, hi), must) in EXPECT.items():
        v = by_n[n]
        subs = extract_segment_subjects(v.get("title", ""), clean(v.get("transcript") or ""))
        cnt = len(subs)
        in_range = lo <= cnt <= hi
        # CHAT 51: subs ahora son dicts {nombre_en, search_query_en, angle_en}
        joined = " | ".join((s.get("nombre_en") or "").lower() for s in subs)
        miss_must = [m for m in must if m not in joined]
        ok = in_range and not miss_must
        all_pass = all_pass and ok
        print(f"  #{n:>2} n={cnt:<3} esperado[{lo}-{hi}] {'OK' if in_range else 'FUERA'}"
              + (f"  falta:{miss_must}" if miss_must else ""))
        if n in (15, 17, 20):
            print("       " + " · ".join((s.get("nombre_en") or "") for s in subs[:10]))
    print(f"\nC1 extractor: {'PASS' if all_pass else 'FAIL — revisar promoción'}")


if __name__ == "__main__":
    main()
