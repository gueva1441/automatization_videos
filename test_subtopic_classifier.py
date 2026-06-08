"""
test_subtopic_classifier.py — C1: valida script_engine.subtopic_classifier contra el corpus
del lab (_lab_out/transcripts_chat42.json), reproduciendo los números cerrados:
  stage 1 BINARIO 24/25 (answer-key con #3→CONTENEDOR) + casos-trampa 4/4.
Si NO reproduce, algo se perdió en la promoción → PARAR.

Correr:  python -X utf8 test_subtopic_classifier.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from script_engine.subtopic_classifier import classify

CORPUS = Path("_lab_out/transcripts_chat42.json")

KEY_ATOMICO = {11, 12, 13, 22, 25}   # #3 reclasificado a CONTENEDOR (Addendum 3 D11)
KEY_DROP = {2, 5, 26}
TRAPS = {10, 14, 17, 21}


def key_of(n):
    if n in KEY_DROP: return "DROP"
    return "ATOMICO" if n in KEY_ATOMICO else "CONTENEDOR"


def clean(raw):
    t = re.sub(r"\[(Music|Applause|Laughter|Audio|música)\]", " ", raw or "", flags=re.IGNORECASE)
    t = re.sub(r">>+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def main():
    videos = json.loads(CORPUS.read_text(encoding="utf-8"))
    classes = ["ATOMICO", "CONTENEDOR"]
    correct = scored = 0
    traps_hit = 0
    misses = []
    print("C1 — subtopic_classifier vs answer-key (binario, #3→CONTENEDOR)\n")
    for i, v in enumerate(videos, 1):
        k = key_of(i)
        c = clean(v.get("transcript") or "")
        if k == "DROP" or len(c) < 50:
            continue
        r = classify(v.get("title", ""), c)
        tipo = r["tipo"]
        scored += 1
        ok = tipo == k
        correct += ok
        if not ok:
            misses.append((i, k, tipo))
        if i in TRAPS:
            traps_hit += (tipo == k)
        mark = "OK" if ok else "MISS"
        trap = " <trap>" if i in TRAPS else ""
        print(f"  #{i:>2} key={k:<10} pred={tipo:<11} {mark}{trap}")

    print(f"\nACCURACY: {correct}/{scored}  (esperado 24/25)")
    print(f"TRAPS: {traps_hit}/4  (esperado 4/4)")
    print(f"misses: {misses or 'ninguno'}")
    ok_acc = correct >= 24
    ok_traps = traps_hit == 4
    print(f"\nC1 classifier: {'PASS' if (ok_acc and ok_traps) else 'FAIL — revisar promoción'}")


if __name__ == "__main__":
    main()
