# -*- coding: utf-8 -*-
"""F50f B — el canon de Wittenoom por producción: `fase1_5.asegurar_canon` (marca nueva → rehace con Opus y guarda en
topics_db y 05_visual_canon.json; su costo va a 01_v3_costos como paso «canon» y a cost_history con el id del tema).
Antes: copia de topic y 05_visual_canon.json en antes/. Después: medida 4a–4g (`f50e/canon_modelos.medir`) y el
criterio del handoff (todas las fotos con año en algún period y ningún grupo con años sin ropa) → CANON_F50f.md.
Sale 1 si el criterio no se cumple (PARADA). Uso: python -u lab/hyperframes/f50f/canon_b.py
"""
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "lab" / "hyperframes" / "f50e"))
sys.path.insert(0, str(ROOT / "lab" / "hyperframes" / "f50c"))
F50F = Path(__file__).resolve().parent
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"


def main() -> int:
    import canon_modelos as cm
    import fase1_5
    from script_engine.topics_db import get_topic_by_id
    antes = F50F / "antes"
    antes.mkdir(exist_ok=True)
    topic = get_topic_by_id(TID)
    (antes / "topic_wittenoom.json").write_text(json.dumps(topic, ensure_ascii=False, indent=1), encoding="utf-8")
    shutil.copy(fase1_5.STEPS_DIR / TID / "05_visual_canon.json", antes / "05_visual_canon.json")
    costos = fase1_5.STEPS_DIR / TID / "01_v3_costos.json"
    n0 = len(json.loads(costos.read_text(encoding="utf-8")).get("_corridas") or [])
    log: list[str] = []
    t = fase1_5.asegurar_canon(TID, topic, log)
    corridas = json.loads(costos.read_text(encoding="utf-8")).get("_corridas") or []
    canon = {k: t.get(k) for k in fase1_5.CANON_KEYS}
    (F50F / "canon_f50f.json").write_text(json.dumps(canon, ensure_ascii=False, indent=1), encoding="utf-8")
    m = cm.medir(canon, cm.fotos_con_anio())
    ok_fotos = m["cubiertas"] == m["con_anio"]
    ok_ropa = m["grupos_con_anios_sin_ropa"] == 0
    L = ["# CANON_F50f — el canon de Wittenoom con Opus, por producción (F50f B)", "",
         "Salida de `python -u lab/hyperframes/f50f/canon_b.py`: `fase1_5.asegurar_canon` (Opus 5.5, effort high, sin "
         "esquema) y la medida 4a–4g de `lab/hyperframes/f50e/canon_modelos.py`.", "",
         f"- Marca: {str(topic.get('canon_ficha_md5'))[:8]} → {str(t.get('canon_ficha_md5'))[:8]} · log: "
         f"{' | '.join(x.strip() for x in log)}",
         f"- Costo (01_v3_costos, pasos nuevos): {corridas[n0:]}", "",
         "| medida | valor |", "|---|---|",
         f"| 4a periods | {' · '.join(map(str, m['periods']))} |",
         f"| 4b fotos cubiertas | {m['cubiertas']}/{m['con_anio']} · por cap " + " · ".join(
             f"{m['por_cap'][c]['cubiertas']}/{m['por_cap'][c]['con_anio']}" for c in sorted(m["por_cap"], key=int))
         + " |",
         f"| 4c fotos sin period | {len(m['sin_period'])} |",
         f"| 4d grupos | {len(m['grupos'])} · con años sin ropa: {m['grupos_con_anios_sin_ropa']} |",
         f"| 4e years ilegibles | {', '.join(m['ilegibles']) or 'ninguno'} |",
         f"| 4g grupos sin appearance | {len(m['sin_appearance'])}/{len(m['grupos'])}: "
         f"{', '.join(m['sin_appearance']) or 'ninguno'} |", "",
         f"**Criterio (handoff F50f, tabla de constantes):** todas las fotos con año en algún period: "
         f"{'sí' if ok_fotos else 'NO'} · ningún grupo con años sin ropa: {'sí' if ok_ropa else 'NO'} → "
         f"**{'PASA' if ok_fotos and ok_ropa else 'NO PASA — PARADA'}**", "", "## Grupos", "",
         "| grupo | where_when | años | clothing_by_period | años sin ropa |", "|---|---|---|---|---|"]
    L += [f"| `{g['id']}` | {g['where_when']} | {g['anios']} | {' · '.join(map(str, g['ropa']))} | "
          f"{g['anios_sin_ropa'] or '—'} |" for g in m["grupos"]]
    (F50F / "CANON_F50f.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(json.dumps({"marca": t.get("canon_ficha_md5"), "log": log, "costo": corridas[n0:],
                      "cubiertas": f"{m['cubiertas']}/{m['con_anio']}", "periods": m["periods"],
                      "grupos": len(m["grupos"]), "sin_ropa": m["grupos_con_anios_sin_ropa"],
                      "sin_appearance": m["sin_appearance"], "pasa": ok_fotos and ok_ropa}, ensure_ascii=False))
    return 0 if ok_fotos and ok_ropa else 1


if __name__ == "__main__":
    sys.exit(main())
