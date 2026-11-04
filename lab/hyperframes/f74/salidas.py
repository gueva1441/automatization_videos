"""F74 — salidas de las 2 etapas, sin red ni disco fuera de esta carpeta.
Correr con QA_FORM=1 (los marcadores se emiten como en el form):
  QA_FORM=1 python lab/hyperframes/f74/salidas.py
Etapa 1: imprime un marcador text real del emisor que corre (copia local de niche_discoverer).
Etapa 2: _run_manual con input() alimentado («Palomares 1966», nicho 0, enter vacío) → semilla_palomares.json;
después fase1._verify_pick_es_saturation con _measure_es MOCKEADO (DISPUTADO, sat 62 000, la medida real del analista
del 2026-11-04) y respuesta [P] → gate_mock.log."""
import builtins
import contextlib
import io
import json
import os
import sys
from pathlib import Path

R = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(R))
AQUI = Path(__file__).parent
assert os.environ.get("QA_FORM"), "correr con QA_FORM=1"

import fase1  # noqa: E402
import niche_discoverer as nd  # noqa: E402

print("=== Etapa 1: marcador text (stdout crudo) ===")
nd._emit_qaform_text_marker("manual_title", "Tema (enter vacío = terminar)")

respuestas = iter(["Palomares 1966", "0", ""])
builtins.input = lambda prompt="": (print(prompt + "<form>"), next(respuestas))[1]
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    seeds = nd._run_manual()
(AQUI / "run_manual.log").write_text(buf.getvalue(), encoding="utf-8")
semilla = seeds[0]
(AQUI / "semilla_palomares.json").write_text(json.dumps(semilla, ensure_ascii=False, indent=1), encoding="utf-8")
print("\n=== Etapa 2: semilla manual ===")
print(json.dumps(semilla, ensure_ascii=False, indent=1))


def medir_mock(q, entity, already_es=False):
    print(f"      [mock _measure_es] q={q!r} entity={entity!r} already_es={already_es}")
    return {"label": "DISPUTADO", "saturation": 62000}


fase1._measure_es = medir_mock
resp = iter(["P"])
builtins.input = lambda prompt="": (print(prompt + "P  <form>"), next(resp))[1]
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    kept = fase1._verify_pick_es_saturation([semilla], n=3)
    print(f"\n[resultado] kept = {[s['seed_title'] for s in kept] if kept else kept}")
(AQUI / "gate_mock.log").write_text(buf.getvalue(), encoding="utf-8")
print("\n=== gate con _measure_es MOCKEADO ===")
print(buf.getvalue())
