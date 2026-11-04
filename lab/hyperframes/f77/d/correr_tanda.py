"""F77 Etapa D: la tanda real de 4 semillas hasta el estante (research + ficha), sin preguntas.

Equivalente por línea de comando del camino del form («D · Tanda de semillas» → niche_discoverer._run_tanda): llama a
la MISMA función, `estante.correr_tanda`, con los 4 títulos del handoff. Los subprocesos `fase1_5 --hasta-ficha` corren
con el Python del venv del pipeline (el mismo que usa run_pipeline). Nada después de la ficha.
Uso (desde la raíz del repo): PYTHONIOENCODING=utf-8 <venv python> lab/hyperframes/f77/d/correr_tanda.py
"""
import json
import sys
import time
from pathlib import Path

R = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(R))
import estante  # noqa: E402

TITULOS = [
    "Palomares 1966: el Proyecto Indalo y los vecinos usados como cobayas",
    "Síndrome del aceite tóxico (colza) 1981",
    "Accidente radiológico de Goiânia 1987",
    "Tragedia del camping Los Alfaques 1978",
]
t0 = time.time()
recs = estante.correr_tanda(TITULOS, python=sys.executable)
out = Path(__file__).parent
(out / "tanda_registros.json").write_text(json.dumps(recs, ensure_ascii=False, indent=1), encoding="utf-8")
items = estante.listar()
(out / "estante_body.md").write_text(estante.body(items) + "\n", encoding="utf-8")
print(f"\n  ⏱ tanda total: {time.time() - t0:.0f} s")
print(estante.body(items))
