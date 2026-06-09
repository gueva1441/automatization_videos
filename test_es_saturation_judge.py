"""
test_es_saturation_judge.py — regresión del fix saturación ES (Diseño B: traducir + juez).
Barra de regresión §4 del handoff, por el lado correcto (vs el T2 relajado que volteaba controles).

Mide cada entidad con el NUEVO _measure_es (traducir grafía → lista ES cruda sin ancla → juez de
relevancia → label con la matemática/umbrales reusados). El juez es estocástico → robustez por
MAYORÍA de N pasadas (como el resto del proyecto), no reglas duras.

Criterio de éxito:
  - Chernobyl y Pripyat (transliterados): label NO-VACIO (SATURADO/DISPUTADO) — el bug arreglado.
  - 5 controles (Pennhurst, Villa Epecuén, Fukushima, Craco, North Brother): NO SATURADO falso
    (no se mata oro). Se reporta además si alguno se mueve de VACIO/HUECO para ojo de Omar.

Necesita Gemini + scrape ES (proxies). Correr:  python -X utf8 test_es_saturation_judge.py
"""
from __future__ import annotations

import sys
from collections import Counter

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from script_engine.subtopic_measurer import _measure_es

N_PASADAS = 3   # mayoría: el juez de relevancia es estocástico

# (entidad, label_viejo_en_seeds, rol)
TARGETS = [
    ("Chernobyl",            "VACIO",  "fix"),     # transliterado → debe dejar de ser VACIO
    ("Pripyat",              "VACIO",  "fix"),     # transliterado → idem
    ("Pennhurst Asylum",     "VACIO",  "control"),
    ("Villa Epecuén",        "HUECO",  "control"),
    ("Fukushima Daiichi",    "VACIO",  "control"),
    ("Craco",                "VACIO",  "control"),
    ("North Brother Island", "HUECO",  "control"),
]

NON_EMPTY = {"SATURADO", "DISPUTADO"}   # "no-VACIO" para el criterio del fix
SANE = {"VACIO", "HUECO"}               # label sano para un control


def _majority_label(name: str):
    labels, sats, queries = [], [], []
    for _ in range(N_PASADAS):
        r = _measure_es(name)
        labels.append(str(r.get("label")))
        sats.append(r.get("saturation") or 0)
        queries.append(r.get("es_query"))
    maj = Counter(labels).most_common(1)[0][0]
    sat_maj = max(s for s, l in zip(sats, labels) if l == maj)
    return maj, sat_maj, labels, (queries[0] if queries else name)


def run():
    print(f"REGRESIÓN fix saturación ES (Diseño B) · mayoría N={N_PASADAS}\n")
    print(f"  {'entidad':<22}{'es_query':<18}{'viejo':<10}{'nuevo':<10}{'votos':<22}OK?")
    print("  " + "─" * 92)

    fix_ok, controls_no_saturado, controls_moved = True, True, []
    rows = []
    for name, old, role in TARGETS:
        maj, sat, votes, esq = _majority_label(name)
        if role == "fix":
            ok = maj in NON_EMPTY
            fix_ok = fix_ok and ok
            mark = "✓ fix" if ok else "✗ SIGUE VACIO"
        else:
            ok = maj != "SATURADO"
            controls_no_saturado = controls_no_saturado and ok
            if maj not in SANE:
                controls_moved.append((name, old, maj))
            mark = "✓" if ok else "✗ SATURADO falso"
            if ok and maj != old:
                mark += f" (movió {old}→{maj})"
        print(f"  {name:<22}{str(esq)[:17]:<18}{old:<10}{maj:<10}{str(votes):<22}{mark}")
        rows.append({"name": name, "old": old, "new": maj, "sat": sat, "votes": votes, "role": role})

    print()
    print(f"  FIX (Chernobyl/Pripyat dejan de ser VACIO): {fix_ok}")
    print(f"  CONTROLES sin SATURADO falso: {controls_no_saturado}")
    if controls_moved:
        print("  ⚠ controles que se movieron de VACIO/HUECO (no es SATURADO, pero ojo de Omar):")
        for n, o, m in controls_moved:
            print(f"      {n}: {o} → {m}  (¿competidor ES real que el ancla substring tapaba?)")

    passed = fix_ok and controls_no_saturado
    strict = passed and not controls_moved   # barra literal: controles quedan en VACIO/HUECO
    print()
    print(f"  VEREDICTO ESTRICTO (controles intactos en VACIO/HUECO): "
          f"{'✅ PASA' if strict else '⚠ PARCIAL'}")
    print(f"  VEREDICTO ESPÍRITU (fix logrado + ningún control en SATURADO falso): "
          f"{'✅ PASA' if passed else '❌ NO PASA'}")
    return 0 if passed else 1


if __name__ == "__main__":
    sys.exit(run())
