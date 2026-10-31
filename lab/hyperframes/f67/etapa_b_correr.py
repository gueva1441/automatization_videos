# -*- coding: utf-8 -*-
"""F67 Etapa B: `fase1_5 --verificar-narracion` sobre Wittenoom (paga verificador y crítico; se informa). Antes: respaldo de lo que
se va a pisar en b/antes/ y comparación de la entrada con el USER del lab F67a. Después: md5 de _steps y b/validacion.md."""
from __future__ import annotations

import hashlib
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(AQUI))

import steps_md5  # noqa: E402

TID, D, B = steps_md5.TID, steps_md5.STEPS, AQUI / "b"


def _por_k(val: dict, campo: str) -> str:
    return "; ".join("#" + str(f["k"]) + " " + ", ".join(f[campo]) for f in val["deberia"] if f[campo]) or "—"


def main() -> int:
    import fase1_5 as f15
    from script_engine import m01f_critico as mf
    (B / "antes").mkdir(parents=True, exist_ok=True)
    for n in ("06_judge_narrative.json", "01b_verificacion.json", "01b_verificacion.md", "01_v3_costos.json"):
        shutil.copy2(D / n, B / "antes" / n)
    steps_md5.foto("B_antes")
    # la entrada contra la del lab: lo único que cambia es `metricas` (declarado, §0) y la tabla si el verificador corre de nuevo
    pool = f15._topic_v3(TID)["evidence_pool"]
    ent = mf.entrada(TID, pool=pool)
    nuevo = json.loads(mf.armar_user(ent["e"], ent["metricas"], ent["verificacion"], mf.FORMATO).split("\n\nFormato de salida")[0])
    lab = json.loads((AQUI / "a" / "user.json").read_text(encoding="utf-8").split("\n\nFormato de salida")[0])
    iguales = {k: nuevo[k] == lab[k] for k in lab}
    claves = {"lab": sorted(lab["metricas"]), "juez": sorted(nuevo["metricas"]), "lab_caps": sorted(lab["metricas"]["caps"][0]), "juez_caps": sorted(nuevo["metricas"]["caps"][0])}
    print("entrada == lab F67a:", iguales)
    print("claves de metricas:", json.dumps(claves, ensure_ascii=False))
    if not all(v for k, v in iguales.items() if k not in ("metricas", "verificacion")):
        print("PARÁ: la entrada no es la del lab")
        return 3
    n3_md5 = hashlib.md5((D / "01b_narracion_v3.json").read_bytes()).hexdigest()
    with open(B / "run.log", "w", encoding="utf-8") as fh:
        rc = subprocess.run([sys.executable, "fase1_5.py", "--topic", TID, "--verificar-narracion"], cwd=ROOT, stdout=fh, stderr=subprocess.STDOUT,
                            env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"}).returncode
    steps_md5.foto("B_despues")
    c = json.loads((D / "01f_critico.json").read_text(encoding="utf-8"))
    v = json.loads((D / "01b_verificacion.json").read_text(encoding="utf-8"))
    val = c["validacion"]
    L = ["# F67 Etapa B — validación del crítico en producción (Wittenoom)", "",
         f"exit {rc} · narración bytes `{n3_md5}` → `{hashlib.md5((D / '01b_narracion_v3.json').read_bytes()).hexdigest()}` · `narracion_md5` {c['narracion_md5']} · SYSTEM `{c['system_md5']}` · USER `{c['user_md5']}`", "",
         f"Entrada contra `a/user.json` del lab: {iguales}", "", f"Claves de `metricas` del lab: {claves['lab']}; caps {claves['lab_caps']}", "", f"Claves de `metricas` del juez: {claves['juez']}; caps {claves['juez_caps']}", "",
         "| nota | n DEBERÍA | ids inválidos | oraciones inválidas | cifras sin respaldo | marcas | US$ crítico | s | US$ verificador | «contradice» |", "|---|---|---|---|---|---|---|---|---|---|",
         f"| {(c['respuesta'] or {}).get('nota_total')} | {c['n_deberia']} | {', '.join(val['ids_invalidos']) or '—'} | {', '.join(val['oraciones_invalidas']) or '—'} | "
         f"{_por_k(val, 'cifras_sin_respaldo')} | {_por_k(val, 'marcas')} | {c['usd']:.4f} | {c['segundos']} | {v['usd_verificador']:.4f} | {len(v['quedan'])} |", "",
         "| k | cap | oraciones | palabras antes → después |", "|---|---|---|---|"]
    L += [f"| {f['k']} | {f['cap']} | {f['idx']} | {f['palabras_antes']} → {f['palabras_despues']} |" for f in val["deberia"]]
    L += ["", "Archivos del topic que cambiaron (md5):", ""] + [f"- {x}" for x in steps_md5.compara("B_antes", "B_despues")] + [""]
    (B / "validacion.md").write_text("\n".join(L), encoding="utf-8", newline="\n")
    print("\n".join(L))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
