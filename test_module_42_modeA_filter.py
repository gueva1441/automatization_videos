"""
test_module_42_modeA_filter.py — GATE 2 (chat 42). Smoke AISLADO de las funciones PURAS
portadas a youtube_scanner para el flujo invertido de Mode A. Sin red.

Ejerce el código REAL de youtube_scanner (no copias): parser corregido, mediana
excluyendo candidato, ratio, y el filtro de UNIÓN sobre los casos límite calibrados
(flying sphere FUERA por canal muerto, gigante 7.9M DENTRO por volumen).

USO:
    python test_module_42_modeA_filter.py
"""
from __future__ import annotations

import sys

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from script_engine.youtube_scanner import (  # noqa: E402
    parse_views_fixed, median_excluding, compute_ratio, passes_en_filter,
    PISO_DEMANDA, PISO_MEDIANA, OUTLIER_MIN, ABS_FLOOR,
)


def main() -> int:
    fails: list[str] = []

    print("  [parser] corregido (arregla el bug del decimal)")
    for text, exp in [("1.2M views", 1_200_000), ("264K", 264_000),
                      ("999", 999), ("2,005,957 views", 2_005_957),
                      ("2.2K views", 2_200), ("3.4B", 3_400_000_000)]:
        got = parse_views_fixed(text)
        ok = got == exp
        print(f"     {text!r:<20} = {got:>14,}  esp {exp:>14,}  {'OK' if ok else 'FAIL'}")
        if not ok:
            fails.append(f"parser {text!r}={got}!={exp}")

    print("\n  [median] excluye el candidato; None si < 5")
    m1 = median_excluding([10, 20, 30, 40, 1000], exclude_value=1000)  # 4 quedan → None
    print(f"     excl deja 4 → {m1} (esp None)  {'OK' if m1 is None else 'FAIL'}")
    if m1 is not None:
        fails.append("median <5 debería None")
    m2 = median_excluding([10, 20, 30, 40, 50, 1000], exclude_value=1000)  # 5 → 30
    print(f"     excl deja 5 → {m2} (esp 30)  {'OK' if m2 == 30 else 'FAIL'}")
    if m2 != 30:
        fails.append(f"median={m2}!=30")

    print("\n  [ratio]")
    r = compute_ratio(240, 30)
    print(f"     240/30 = {r} (esp 8.0)  {'OK' if r == 8.0 else 'FAIL'}")
    if r != 8.0:
        fails.append("ratio!=8")

    print("\n  [filtro UNIÓN] casos límite calibrados (chat 42)")
    cases = [
        # (nombre, views, ratio, median, esperado)
        ("gigante 7.9M nivel normal (entra por VOLUMEN)", 7_904_408, 2.8, 2_850_000, True),
        ("flying sphere canal MUERTO (median 229<piso)", 255_274, 1114.7, 229, False),
        ("joya chica outlier (105k, r33, med 3150)", 105_825, 33.6, 3_150, True),
        ("video chico bajo ABS_FLOOR (50k, r10)", 50_000, 10.0, 4_000, False),
        ("sin baseline (median None, views 200k)", 200_000, 0.0, None, False),
        ("sin baseline pero VOLUMEN (median None, 4M)", 4_000_000, 0.0, None, True),
        ("ratio 2.9 < OUTLIER_MIN, sin volumen", 500_000, 2.9, 100_000, False),
    ]
    for name, v, rt, med, exp in cases:
        got = passes_en_filter(v, rt, med)
        ok = got == exp
        print(f"     {'OK ' if ok else 'FAIL'} {name}: pasa={got} (esp {exp})")
        if not ok:
            fails.append(f"union '{name}' {got}!={exp}")

    print(f"\n  constantes: OUTLIER_MIN={OUTLIER_MIN} PISO_MEDIANA={PISO_MEDIANA:,} "
          f"ABS_FLOOR={ABS_FLOOR:,} PISO_DEMANDA={PISO_DEMANDA:,}")

    print("\n" + "─" * 56)
    if fails:
        print(f"  [FAIL] {len(fails)}:")
        for f in fails:
            print(f"    - {f}")
        return 1
    print("  [OK] GATE 2: funciones puras portadas validadas (flying sphere fuera, "
          "gigante 7.9M dentro).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
