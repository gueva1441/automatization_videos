# -*- coding: utf-8 -*-
"""F67c, Etapa C: `etapa_de` de Wittenoom hoy y simulando el papel aprobado (monkeypatch de `estado_papel`), de solo lectura; 0 llamadas
a la API. Salida: lab/hyperframes/f67/f67c/SALIDAS.md. Comprueba con steps_md5 que `_steps/<tid>/` no cambió."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(AQUI))

import steps_md5  # noqa: E402

TID, D = steps_md5.TID, steps_md5.STEPS
S = AQUI / "f67c"


def main() -> None:
    S.mkdir(exist_ok=True)
    steps_md5.foto("F67c_antes")
    import fase1_5 as f15
    import run_pipeline as rp
    from script_engine import m06_assembler as m6
    L = ["# F67c — salidas", "", "## C. `etapa_de` de Wittenoom", "", f"- Hoy: `{rp.etapa_de(TID)}`"]
    n = json.loads((D / "01b_narration.json").read_text(encoding="utf-8"))
    v = json.loads((D / "01b_narracion_v3.json").read_text(encoding="utf-8"))
    try:
        m6.assemble_final_script(TID)
        hoy = "ESCRIBIÓ"
    except ValueError as e:
        hoy = str(e)
    L += [f"- `assemble_final_script` hoy: no escribe: «{hoy}»",
          f"- `01b_narration.json` = la narración aprobada, cap por cap: {[c['narration'] == w['narration'] for c, w in zip(n['chapters'], v['caps'])]}"]
    orig = f15.estado_papel
    f15.estado_papel = lambda t: (True, "papel aprobado (simulado)")
    L += [f"- Simulando el papel aprobado (monkeypatch de `estado_papel`): `{rp.etapa_de(TID)}`"]
    f15.estado_papel = orig
    script = ROOT / "data" / "scripts" / f"{TID}.json"
    man = ROOT / "output" / TID / "assets" / "assets_manifest.json"
    L += ["", "Artefactos del 28-oct que ya no pasan:", ""]
    for nombre, p in (("script", script), ("manifest", man), ("fondos.json", ROOT / "output" / TID / "_fase2b_work" / "fondos.json"),
                      ("GUION_PANTALLA.json", ROOT / "output" / TID / "GUION_PANTALLA.json")):
        L.append(f"- {nombre}: {rp._desfase(p, nombre, 'cualquiera')}")
    steps_md5.foto("F67c_despues")
    L += ["", f"Archivos de `_steps/<tid>/` que cambiaron: {steps_md5.compara('F67c_antes', 'F67c_despues') or 'ninguno'}", ""]
    (S / "SALIDAS.md").write_text("\n".join(L), encoding="utf-8", newline="\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
