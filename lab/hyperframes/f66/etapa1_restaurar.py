# -*- coding: utf-8 -*-
"""
lab/hyperframes/f66/etapa1_restaurar.py — F66b Etapa 1 (CERO llamadas; DECISIONES 2026-10-31 17:25): vuelve la narración de antes de F66.
  1. guarda lo de F66 en despues_descartado/ y copia de antes/ a _steps los 6 archivos del pedido; PARÁ si la narración no da c7badfbe…;
  2. rehace 01b_verificacion.json/.md desde la 1.ª pasada de F66 (los 7 «contradice» como aviso, sin ediciones); el formato es el de
     fase1_5._verificacion_md. El JSON de F66 entero queda en despues_descartado/.
  3. PARÁ si el USER del autor no vuelve a 018f9cc1… (el md5 con que se midió la entrada completa).
El papel y su raw NO se tocan acá: la Etapa 2 los respalda. El raw de antes/ no se restaura: sería un hit de caché con el papel viejo.
ch03 [15], que solo marcó la re-verificación descartada, NO entra a `quedan` (el pedido dice 7): queda como dato aparte en el JSON y el .md.
"""
from __future__ import annotations

import hashlib
import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import fase1_5 as f15  # noqa: E402
from script_engine import evidence as ev  # noqa: E402
from script_engine import m01e_pantalla as m  # noqa: E402
from script_engine.clima import vocabulario_clima  # noqa: E402

TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
D = ROOT / "data/scripts/_steps" / TID
F = Path(__file__).resolve().parent
ANTES, DESC = F / "antes", F / "despues_descartado"
ARCHIVOS = ("01b_narracion_v3.json", "01a_skeleton.json", "01b_narration.json", "01b_narration_normalized.json",
            "01b_guionista_v4.json", "06_judge_narrative.json")
NARRACION = "c7badfbe260f5eb24a47e780b40406b5"
USER = "018f9cc1b939e2afdcfad5eb5ebcc36f"


def md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def main() -> None:
    DESC.mkdir(exist_ok=True)
    assert md5(ANTES / "01b_narracion_v3.json") == NARRACION, "PARÁ: el respaldo no es la narración esperada"
    for n in ARCHIVOS + ("01b_verificacion.json", "01b_verificacion.md"):
        if not (DESC / n).exists():                # idempotente: lo de F66 se guarda una sola vez
            shutil.copy2(D / n, DESC / n)
    for n in ARCHIVOS:
        print(f"{n}: F66 {md5(DESC / n)[:8]} → {md5(ANTES / n)[:8]}")
        shutil.copy2(ANTES / n, D / n)
        assert md5(D / n) == md5(ANTES / n)
    if md5(D / "01b_narracion_v3.json") != NARRACION:
        raise SystemExit("PARÁ: la narración restaurada no da c7badfbe…")
    v = json.loads((DESC / "01b_verificacion.json").read_text(encoding="utf-8"))
    pr = v["primera"]
    assert v["narracion_md5_antes"] == NARRACION and len(pr["contradice"]) == 7
    voz = ev.norm(" ".join(p["texto"] for p in json.loads((D / "01b_narracion_v3.json").read_text(encoding="utf-8"))["parrafos"]))
    assert all(ev.norm(x["texto"]) in voz for x in pr["contradice"]), "un «contradice» no está en la narración restaurada"
    res = {"narracion_md5": NARRACION, "primera": pr,
           "quedan": [{k: x.get(k) for k in ("cap", "oracion", "texto", "afirmacion", "ids", "fragmento")} for x in pr["contradice"]],
           "usd_verificador": pr["usd"],
           "re_verificacion_descartada": {"nota": "marcado solo por la re-verificación de F66, sobre la narración descartada; no es parte del aviso",
                                          "contradice": v["nuevas"]}}
    (D / "01b_verificacion.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    texto = f15._verificacion_md(res)
    extra = ["", "## Visto solo en la re-verificación descartada (no cuenta en el aviso)", ""]
    for x in v["nuevas"]:
        en = "está" if ev.norm(x["texto"]) in voz else "NO está"
        extra.append(f"- {x['cap']} [{x['oracion']}] «{x['texto']}»: {x['afirmacion']} · {', '.join(x['ids'])} · «{x['fragmento']}» (esa oración {en} en la narración restaurada; el índice es el de la narración de F66)")
    (D / "01b_verificacion.md").write_text(texto + "\n".join(extra) + "\n", encoding="utf-8")
    ent = m.entrada(m.cargar(TID, ROOT / "data/scripts/_steps"), vocabulario_clima())
    h = m.entrada_md5(ent)
    print("narración", md5(D / "01b_narracion_v3.json"), "· USER", h, "· quedan", len(res["quedan"]))
    if h != USER:
        raise SystemExit(f"PARÁ: el USER {h} no es {USER}")
    print((D / "01b_verificacion.md").read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()
