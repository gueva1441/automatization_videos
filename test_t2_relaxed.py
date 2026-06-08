"""
test_t2_relaxed.py — valida OFFLINE los dos predicados relajados de T2 (idioma + anchor),
sin scrapetube. La tabla de regresión real (controles + Chernobyl) la produce
_lab_es_saturation_relaxed_chat49.py contra YouTube vivo.

Correr:  python -X utf8 test_t2_relaxed.py
"""
from __future__ import annotations

import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from langdetect import DetectorFactory
DetectorFactory.seed = 0   # determinismo

from _lab_es_saturation_relaxed_chat49 import _lang_ok_relaxed, _anchor_ok_relaxed


def run():
    failures = []

    def check(cond, msg):
        print(f"  [{'✓' if cond else '✗'}] {msg}")
        if not cond:
            failures.append(msg)

    print("T2.1 — idioma relajado: ES sí, EN sí (mal-detectado real), ruso/árabe NO\n")
    check(_lang_ok_relaxed("Chernobyl: la verdad del desastre nuclear en español") is True,
          "título español → cuenta")
    check(_lang_ok_relaxed("The Chernobyl Disaster Full Documentary History Channel") is True,
          "título inglés → cuenta (relajación: detect mislabela ES real como EN)")
    check(_lang_ok_relaxed("Чернобыль вся правда о ядерной катастрофе документальный фильм") is False,
          "título ruso → NO cuenta (mercado extranjero)")
    check(_lang_ok_relaxed("كارثة تشيرنوبيل النووية الوثائقي الكامل بالتفصيل") is False,
          "título árabe → NO cuenta (mercado extranjero)")

    print("\nT2.2 — anchor relajado: top-5 orgánico O substring de anchor >4 letras\n")
    # top-5: cuenta sin anchor
    check(_anchor_ok_relaxed("Cualquier video sin la palabra", ["chernobyl"], rank=0) is True,
          "rank 0 (top-5) → cuenta aunque NO matchee anchor (YT lo posicionó)")
    check(_anchor_ok_relaxed("Cualquier video sin la palabra", ["chernobyl"], rank=4) is True,
          "rank 4 (aún top-5) → cuenta")
    # fuera del top-5: depende del anchor substring
    check(_anchor_ok_relaxed("Documental sobre Chernobyl hoy", ["chernobyl"], rank=10) is True,
          "rank 10 + anchor 'chernobyl' (>4) substring en título → cuenta")
    check(_anchor_ok_relaxed("Un tema totalmente distinto", ["chernobyl"], rank=10) is False,
          "rank 10 + anchor NO presente → NO cuenta")
    # anchors cortos (<=4 letras) no relajan por substring; solo el top-5 los salva
    check(_anchor_ok_relaxed("USS algo lejano", ["uss"], rank=10) is False,
          "rank 10 + anchor corto 'uss' (≤4) → NO cuenta por substring")
    check(_anchor_ok_relaxed("USS algo lejano", ["uss"], rank=2) is True,
          "rank 2 (top-5) + anchor corto → cuenta igual (por posición)")

    print("\n" + ("✅ TODOS OK" if not failures else f"❌ {len(failures)} FALLO(S): " + "; ".join(failures)))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(run())
