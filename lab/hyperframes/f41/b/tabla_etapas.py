"""F41 B.8 — la tabla `etapa_de` para cada topic de data/topics_db.json. SOLO LECTURA: no corre ninguna fase, no
escribe nada (etapa_de mira artefactos en disco; fase1_5.estado_papel y aprobacion.estado solo leen).

    PYTHONIOENCODING=utf-8 python lab/hyperframes/f41/b/tabla_etapas.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RAIZ))

import run_pipeline as rp  # noqa: E402

COMANDO = {"guion": "fase1_5 --topic X --batch", "papel": "compuerta del papel (A/P)",
           "voz": "fase1_5 --topic X --from normalizer_gate --batch", "assets": "fase2a --topic X",
           "fondos": "visor (form) + fase2b X", "guion_pantalla": "fase2b X --plan-only",
           "aprobar_guion": "compuerta del guion de pantalla (A/P)",
           "render": "fase2b X " + " ".join(rp.RENDER_FLAGS), "packaging": "fase3 X (o reporte en --batch)",
           "listo": "nada", rp.CADENA_VIEJA: "nada (PARADA: topic de la cadena borrada)"}


def main() -> int:
    db = json.loads((RAIZ / "data" / "topics_db.json").read_text(encoding="utf-8"))
    print("| topic | status (topics_db) | etapa_de | qué correría `run_pipeline --topic X` | por qué |")
    print("|---|---|---|---|---|")
    for t in db.get("topics", []):
        tid = t.get("id")
        try:
            etapa, motivo = rp.etapa_de(tid)
        except Exception as e:  # noqa: BLE001 — la tabla no se cae por un topic
            etapa, motivo = "ERROR", f"{type(e).__name__}: {e}"
        print(f"| `{tid}` | {t.get('status')} | **{etapa}** | {COMANDO.get(etapa, '—')} | "
              f"{motivo.replace('|', '/').replace(chr(10), ' ')} |")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
