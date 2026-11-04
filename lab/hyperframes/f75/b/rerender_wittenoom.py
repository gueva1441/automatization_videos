# -*- coding: utf-8 -*-
"""F75 B2: re-genera el .md del crítico de Wittenoom desde el 01f_critico.json que ya existe, SIN API (US$ 0).

    python lab/hyperframes/f75/b/rerender_wittenoom.py

- Lee (solo lectura) data/scripts/_steps/<tid>/: 01f_critico.json, 01b_narracion_v3.json, 01a_escaleta.json, 01a_skeleton.json,
  00_pool_v3.json, 06_judge_narrative.json. No escribe en data/ ni en output/: no pisa el 01f_critico.md de _steps.
- metricas = m05 `retencion()` llamada directo con los archivos del disco y seg_por_palabra = el de 06_judge_narrative.json
  (0,34; nunca `velocidad()`). Con la m05 nueva (F75 A) el personaje es Daniel; con la vieja, María.
- Escribe lab/hyperframes/f75/b/01f_critico.md y lab/hyperframes/f75/b/entre_promesas.json, e imprime la sección
  «## Promesas nuevas (código)» y el personaje.
"""
from __future__ import annotations

import inspect
import json
import sys
sys.stdout.reconfigure(encoding="utf-8")   # consola cp1252 de Windows: la flecha → no entra
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))

from script_engine import m01e_pantalla as mp  # noqa: E402
from script_engine import m01f_critico as mf  # noqa: E402
from script_engine import m05_narrative as m5  # noqa: E402
from script_engine.m01d_particion import md5_narracion  # noqa: E402

TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
SD = ROOT / "data" / "scripts" / "_steps"
OUT = Path(__file__).resolve().parent


def _lee(nombre: str) -> dict:
    return json.loads((SD / TID / nombre).read_text(encoding="utf-8"))


def metricas(carga: dict, seg: float) -> dict:
    """`retencion()` con lo que su firma pida (la reescribe F75 A en paralelo): párrafos, skeleton, escaleta, pool y seg."""
    hay = {"parrafos": carga["parrafos"], "skeleton": _lee("01a_skeleton.json"), "escaleta": carga["escaleta"], "pool": carga["pool"], "seg": seg}
    params = inspect.signature(m5.retencion).parameters
    falta = [p for p, v in params.items() if v.default is inspect.Parameter.empty and p not in hay]
    if falta:
        raise SystemExit(f"retencion() pide {falta}: actualizar este script")
    return m5.retencion(**{p: hay[p] for p in params if p in hay})


def main() -> int:
    critica = _lee("01f_critico.json")
    seg = _lee("06_judge_narrative.json")["retencion"]["seg_por_palabra"]
    carga = mp.cargar(TID, SD)
    # mismo corte e idx por cap que `entrada.caps`; `seg` explícito para que m01e no mida la voz (caben no se usa acá)
    e = mp._para_modelo(mp.entrada(carga, [], {"valor": seg, "oraciones": 0, "caps": 0, "voz": "06_judge_narrative"}))
    met = metricas(carga, seg)
    n_md5 = md5_narracion(_lee("01b_narracion_v3.json"))
    val, texto = mf.rerender(critica, e["caps"], met, n_md5)
    (OUT / "01f_critico.md").write_text(texto, encoding="utf-8")
    (OUT / "entre_promesas.json").write_text(json.dumps(val["entre_promesas"], ensure_ascii=False, indent=1), encoding="utf-8")
    per = met.get("personaje") or {}
    quien = ("Daniel (m05 nueva)" if "Daniel" in str(per.get("nombre")) else
             "María (m05 vieja)" if "María" in str(per.get("nombre")) else f"otro: {per or met.get('personaje_motivo')}")
    print(f"seg_por_palabra {seg} · narración disco {n_md5} · crítico {critica.get('narracion_md5')}")
    print(f"personaje: {per.get('id')} {per.get('nombre')} · oraciones {per.get('oraciones')} → {quien}")
    i, j = texto.index("## Promesas nuevas (código)"), texto.index("## Pico")
    print(texto[i:j])
    print(f"→ {OUT / '01f_critico.md'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
