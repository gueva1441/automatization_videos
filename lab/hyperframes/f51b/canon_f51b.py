# -*- coding: utf-8 -*-
"""F51b etapa 2 — el canon de Wittenoom con el pedido nuevo (appearance fijo + condition_by_period), por producción:
`fase1_5.asegurar_canon` (marca nueva → 1 llamada a Opus; escribe topics_db y 05_visual_canon.json, como en
producción). Un reintento solo si sale CanonError (la Parada de asegurar_canon con un CanonError detrás).
Freno del handoff (tope US$ 1,00 = 1 llamada + 1 reintento): `claude_helpers._post` va envuelto y no deja salir una
tercera respuesta cobrada, tampoco por los re-llamados de JSON roto de `call_json`.
Antes: copia del topic y de 05_visual_canon.json en antes/. Después: canon_f51b.json y el costo (01_v3_costos y
cost_history). No escribe 03_visual.json. Uso: python -u lab/hyperframes/f51b/canon_f51b.py
"""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
F51B = Path(__file__).resolve().parent
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
MAX_LLAMADAS = 2                                   # handoff F51b: 1 llamada + 1 reintento


def main() -> int:
    import claude_helpers
    import fase1_5
    from researcher_steps import step_4e_visual_canon as s4e
    from script_engine.topics_db import get_topic_by_id
    antes = F51B / "antes"
    antes.mkdir(exist_ok=True)
    topic = get_topic_by_id(TID)
    (antes / "topic_wittenoom.json").write_text(json.dumps(topic, ensure_ascii=False, indent=1), encoding="utf-8")
    shutil.copy(fase1_5.STEPS_DIR / TID / "05_visual_canon.json", antes / "05_visual_canon.json")
    costos = fase1_5.STEPS_DIR / TID / "01_v3_costos.json"
    n0 = len(json.loads(costos.read_text(encoding="utf-8")).get("_corridas") or [])

    llamadas = []
    post0 = claude_helpers._post

    def post(body):
        if len(llamadas) >= MAX_LLAMADAS:
            raise RuntimeError(f"F51b: freno — ya hubo {len(llamadas)} respuestas cobradas (tope 1 + 1 reintento)")
        r = post0(body)
        llamadas.append({"model": r.get("model"), "usage": r.get("usage"), "stop_reason": r.get("stop_reason")})
        return r
    claude_helpers._post = post

    log: list[str] = []
    intentos = []
    t = None
    for intento in (1, 2):
        try:
            t = fase1_5.asegurar_canon(TID, topic, log)
            intentos.append("ok")
            break
        except fase1_5.Parada as e:
            intentos.append(f"Parada: {e}")
            if not isinstance(e.__cause__, s4e.CanonError) or intento == 2:
                break
    claude_helpers._post = post0
    corridas = json.loads(costos.read_text(encoding="utf-8")).get("_corridas") or []
    out = {"marca_antes": topic.get("canon_ficha_md5"), "marca_despues": (t or {}).get("canon_ficha_md5"),
           "intentos": intentos, "llamadas": llamadas, "costo_01_v3_costos": corridas[n0:], "log": log}
    if t is not None:
        (F51B / "canon_f51b.json").write_text(json.dumps({k: t.get(k) for k in (*fase1_5.CANON_KEYS,
                                                                                 "canon_ficha_md5")},
                                                         ensure_ascii=False, indent=1), encoding="utf-8")
    (F51B / "corrida_f51b.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(out, ensure_ascii=False))
    return 0 if t is not None else 1


if __name__ == "__main__":
    sys.exit(main())
