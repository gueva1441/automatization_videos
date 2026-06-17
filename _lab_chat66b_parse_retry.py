"""
_lab_chat66b_parse_retry.py — lab read-only (HANDOFF 66b, LEVER A).

Ejercita _parse_with_retry con get_text_fn mockeado. NO llama a la API. Cuenta dumps
monkeypatcheando _dump_invalid_json (no escribe a disco).

  Caso 1 — roto en intento 1, válido en 2 → devuelve dict, sin crash, SIN dump.
  Caso 2 — roto en los 3 intentos → dumpea UNA vez y propaga ValueError con el sufijo de dump.
  Caso 3 — el JSON exacto que crasheó la corrida (comillas dobles sin escapar) en intento 1 +
           limpio en 2 → pasa.
"""
from __future__ import annotations
import gemini_helpers as gh

# monkeypatch del dump: contamos llamadas, no tocamos disco
_dumps = {"n": 0}
gh._dump_invalid_json = lambda raw, text, e: (_dumps.__setitem__("n", _dumps["n"] + 1)
                                              or " | Dump completo: <mocked>")


def _feeder(texts):
    """Devuelve un get_text_fn que entrega texts[0], texts[1], … en cada llamada."""
    it = iter(texts)
    return lambda: next(it)


# --- Caso 1: roto → válido ---
_dumps["n"] = 0
roto = '{"a": "x "y" z"}'          # comillas dobles sin escapar
ok = '{"a": "ok", "b": [1,2]}'
res = gh._parse_with_retry(_feeder([roto, ok]))
assert res == {"a": "ok", "b": [1, 2]}, res
assert _dumps["n"] == 0, "no debió dumpear (segundo intento OK)"
print("OK C1: re-rollea y devuelve el dict, sin dump")

# --- Caso 2: roto en los 3 → dump 1 vez + ValueError con sufijo ---
_dumps["n"] = 0
raised = None
try:
    gh._parse_with_retry(_feeder([roto, roto, roto]))
except ValueError as e:
    raised = e
assert raised is not None, "debió propagar ValueError"
msg = str(raised)
assert "Gemini devolvió JSON inválido en char" in msg, msg
assert "Dump completo:" in msg, msg
assert _dumps["n"] == 1, ("dump exactamente 1 vez (solo el fallo final)", _dumps["n"])
print("OK C2: 3 fallos → 1 dump + ValueError con mismo mensaje/sufijo")

# --- Caso 3: el JSON exacto del crash + limpio en 2 ---
_dumps["n"] = 0
crash = '{"bullets": ["Estancia "aterradora" y "angustiante""]}'   # el del chat 66
clean = '{"bullets": ["Estancia aterradora y angustiante"]}'
res = gh._parse_with_retry(_feeder([crash, clean]))
assert res == {"bullets": ["Estancia aterradora y angustiante"]}, res
assert _dumps["n"] == 0
print("OK C3: el JSON que crasheó la corrida re-rollea y pasa")

# --- shape-normalize preservado: array suelto → {"image_prompts": [...]} ---
res = gh._parse_with_retry(_feeder(['[{"p":"a"},{"p":"b"}]']))
assert res == {"image_prompts": [{"p": "a"}, {"p": "b"}]}, res
print("OK shape-normalize (lista → image_prompts) preservado")

print("LAB 66b-A PASS")
