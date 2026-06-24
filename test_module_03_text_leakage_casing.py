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

# ── CAMINO C (fix 110b): regla 3 NO debe rechazar SU PROPIO titular sancionado ──
# (slot text_in_image). El titular entre comillas == intentional_text → exento.
# Otra comilla distinta = fuga real → raise. Eufemismo sin comillas → raise.
print("[CAMINO C] titular sancionado del slot text_in_image (allow_intentional_text):")
TITULAR = "NO APTOS PARA SU PROPÓSITO"
try:  # 1. el titular propio, renderizado por el fluidificador → NO raise
    m._validate_no_text_leakage(
        'A brass plaque, the inscription "no aptos para su propósito" engraved deep',
        "test", allow_intentional_text=True, intentional_text=TITULAR)
    ok = True
except m.VisualValidationError:
    ok = False
check("camino C: titular sancionado → no-raise", ok)
try:  # 2. fuga NO-titular (otra comilla distinta) → SÍ raise
    m._validate_no_text_leakage(
        'A door with the label "acceso restringido" stenciled on it',
        "test", allow_intentional_text=True, intentional_text=TITULAR)
    raised = False
except m.VisualValidationError:
    raised = True
check("camino C: fuga no-titular → raise", raised)
try:  # 3. eufemismo sin comillas → SÍ raise aunque allow_intentional_text
    m._validate_no_text_leakage(
        "A prison wall, a blurred area where the name was once painted",
        "test", allow_intentional_text=True, intentional_text=TITULAR)
    raised = False
except m.VisualValidationError:
    raised = True
check("camino C: eufemismo sin comillas → raise", raised)

_total = len(PASA) + len(RAISE) + 3
print("\n" + (f"ALL GREEN ({len(PASA)} pasa + {len(RAISE)} raise + 3 camino C = {_total})"
              if not FAILS else f"FAILS ({len(FAILS)}): " + ", ".join(FAILS)))
sys.exit(1 if FAILS else 0)
