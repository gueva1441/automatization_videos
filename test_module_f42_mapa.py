"""F42 §C.3 — el mapa del proyecto (`lab/MAPA_PROYECTO.md/.json`) está al día con el código: `--check` da 0, las
etapas del mapa son las de `run_pipeline.sequence` leídas por AST y todo archivo de producción tiene sticker. Sin API,
sin tocar data/ ni output/."""
from __future__ import annotations

import ast
import json
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "lab" / "tools"))
import mapa_modulos as mm  # noqa: E402


def _etapas_de_run_pipeline() -> list[str]:
    t = ast.parse((ROOT / "run_pipeline.py").read_text(encoding="utf-8"))
    for n in t.body:
        if isinstance(n, ast.Assign) and any(isinstance(x, ast.Name) and x.id == "ETAPAS" for x in n.targets):
            return [e.value for e in n.value.elts]
    raise AssertionError("run_pipeline.py sin ETAPAS")


def test_check_da_0():
    r = subprocess.run([sys.executable, str(ROOT / "lab" / "tools" / "mapa_modulos.py"), "--check"], cwd=ROOT,
                       capture_output=True, text=True, encoding="utf-8", errors="replace")
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]


def test_etapas_del_mapa_son_las_de_sequence():
    mapa = json.loads((ROOT / "lab" / "MAPA_PROYECTO.json").read_text(encoding="utf-8"))
    etapas = [e["etapa"] for e in mapa["secuencia"]["etapas"] if e["etapa"] != "research"]
    assert etapas == _etapas_de_run_pipeline()
    # las cajas del flujograma salen de esas etapas, en el mismo orden
    cajas = [c["etapa"] for c in mapa["cajas"] if c["etapa"] != "research"]
    assert cajas == [e for e in etapas if e in cajas]


def test_todo_archivo_de_produccion_tiene_sticker():
    st, dup = mm.stickers()
    faltan = sorted(set(mm.produccion()) - set(st))
    assert not faltan, f"sin sticker: {faltan}"
    assert not dup, f"stickers repetidos: {dup}"


def test_check_falla_con_sticker_viejo(tmp_path):
    for f in mm.STICKERS.glob("*.json"):
        shutil.copy(f, tmp_path / f.name)
    zona = tmp_path / "guion.json"
    d = json.loads(zona.read_text(encoding="utf-8"))
    d["fase1_5.py"]["md5"] = "0" * 32
    zona.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    fallas = mm.check(tmp_path)
    assert any("sticker viejo: fase1_5.py" in f for f in fallas), fallas
