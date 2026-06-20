"""test_module_flow_director_fallback.py — chat 87 (B-QA-3).
Candar la doctrina vertical-default del fallback determinista.
Standalone: python test_module_flow_director_fallback.py
Importa flow_director (requiere config real — CC en Windows).
"""
import os, sys
sys.path.insert(0, os.path.join(os.getcwd(), "script_engine"))
import flow_director as fd

FAILS = []
def check(name, cond, extra=""):
    print(("  OK  " if cond else "  XX  ") + name + (("  | " + extra) if extra and not cond else ""))
    if not cond:
        FAILS.append(name)

TOTAL = 6
# FlowSpec es TypedDict → acceso por subscript ["movement"], NO atributo.
fb = lambda n: fd._fallback_spec(f"ch{n:02d}", TOTAL)["movement"]

# posiciones ancla
check("hook (ch01) -> orbital", fb(1) == "orbital", fb(1))
check("outro (ch06) -> horizontal", fb(6) == "horizontal", fb(6))

# medio: vertical-default (par) / orbital (impar) — B-QA-3
check("ch02 (par) -> vertical", fb(2) == "vertical", fb(2))
check("ch03 (impar) -> orbital", fb(3) == "orbital", fb(3))
check("ch04 (par) -> vertical", fb(4) == "vertical", fb(4))
check("ch05 (impar) -> orbital", fb(5) == "orbital", fb(5))

# candado de la inversion:
mids = [fb(n) for n in range(2, 6)]
check("horizontal NO aparece en el medio (solo outro)", "horizontal" not in mids, str(mids))
check("vertical SI entro a la alternancia", "vertical" in mids, str(mids))

print("\n" + ("ALL GREEN" if not FAILS else f"FAILS ({len(FAILS)}): " + ", ".join(FAILS)))
sys.exit(1 if FAILS else 0)
