"""Test del fix de casing del validador text-leakage / regla 3 (HANDOFF B-textleak §4).
python test_module_03_text_leakage_casing.py  → 12/12 (7 pasa + 5 raise).

MONOTONICIDAD (no-regresión): el fix solo RELAJA el patrón de comillas (de "cualquier
palabra de 4+ letras entre comillas" a "solo palabra CAPITALIZADA entre comillas") corriéndolo
case-sensitive sobre el prompt original. → el set de raises post-fix ⊆ pre-fix; ningún prompt
que pasaba antes ahora levanta. Los eufemismos (5 patrones) y el mensaje de error no cambian.
"""
import os, sys

sys.path.insert(0, os.path.join(os.getcwd(), "script_engine"))
import m03_visual as m

FAILS = []
def check(name, cond):
    print(("  OK  " if cond else "  XX  ") + name)
    if not cond:
        FAILS.append(name)

# ── DEBEN PASAR (no raise) — comillas de énfasis, los falsos positivos reales del cap 6 ──
PASA = [
    'A weathered industrial corridor, an air of "scarred" decay, dim cold light',
    "Faint 'echoes' of old machinery linger in deep shadow",
    'A "dangerous" red glow spilling across the empty reactor hall',
    "A heavy sense of 'contradiction' inside the abandoned control room",
    'A wide desolate plaza with a "sold" feeling of abandonment',
    'An "escalofriante" stillness over the empty apartments',  # español: NO es trabajo de este validador
    'A clean weathered concrete wall, no signage, smooth surfaces',  # control limpio
]

# ── DEBEN SEGUIR LEVANTANDO (raise) — leaks reales ──
RAISE = [
    'A rusted metal sign reading "Pripyat" mounted on a pole',          # nombre propio capitalizado
    'A prison wall with a sign where the name was once painted',        # eufemismo (pattern existente)
    'A faded map showing the town name in the corner',                  # eufemismo
    'A blurred area where text used to be on the door',                 # eufemismo
    'The inscription "Reactor" engraved on a brass plaque',             # nombre capitalizado
]

print("[PASA] no deben levantar (comillas de énfasis):")
for p in PASA:
    try:
        m._validate_no_text_leakage(p, "test")
        ok = True
    except m.VisualValidationError:
        ok = False
    check(f"no-raise: {p[:48]}...", ok)

print("[RAISE] deben levantar (leaks reales):")
for p in RAISE:
    try:
        m._validate_no_text_leakage(p, "test")
        raised = False
    except m.VisualValidationError:
        raised = True
    check(f"raise: {p[:48]}...", raised)

print("\n" + (f"ALL GREEN ({len(PASA)} pasa + {len(RAISE)} raise = {len(PASA)+len(RAISE)}/12)"
              if not FAILS else f"FAILS ({len(FAILS)}): " + ", ".join(FAILS)))
sys.exit(1 if FAILS else 0)
