"""F44 §1 — `ficha_caso.prompt` con `caso` opcional. Sin `caso`, el prompt es byte-idéntico al de antes de F44
(`01a5858`, sacado de git); con `caso`, solo cambia el bloque `<caso>` (las 4 líneas de la escaleta). Sin red.

    HTTP_PROXY=http://127.0.0.1:9 HTTPS_PROXY=http://127.0.0.1:9 python -m pytest -q test_module_f44.py
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
from pathlib import Path

from researcher_steps import ficha_caso as fc

ROOT = Path(__file__).resolve().parent
ANTES = "01a5858"                       # el último commit antes de F44 (F42b, reporte)
POOL = ROOT / "lab" / "hyperframes" / "f7" / "00_pool_v3.json"
TITULO = "Wittenoom ciudad fantasma contaminada Australia"
CASO = {"angle": "Daniel Écija (padre) murió de mesotelioma.", "mystery": "¿Qué esconde Wittenoom?",
        "reveal": "3 millones de toneladas de relaves."}


def _ficha_antes(tmp: Path):
    src = subprocess.run(["git", "show", f"{ANTES}:researcher_steps/ficha_caso.py"], cwd=ROOT, capture_output=True,
                         text=True, encoding="utf-8", check=True).stdout
    f = tmp / "ficha_caso_antes.py"
    f.write_text(src, encoding="utf-8")
    spec = importlib.util.spec_from_file_location("ficha_caso_antes", f)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def test_sin_caso_el_prompt_es_byte_identico(tmp_path):
    pool = json.loads(POOL.read_text(encoding="utf-8"))
    antes = _ficha_antes(tmp_path)
    assert _md5(fc.prompt(pool, TITULO)) == _md5(antes.prompt(pool, TITULO))
    assert fc.system() == antes.system()
    assert fc.PROMPT_VERSION == antes.PROMPT_VERSION == "f23-1"


def test_con_caso_solo_cambia_el_bloque_caso():
    pool = json.loads(POOL.read_text(encoding="utf-8"))
    sin, con = fc.prompt(pool, TITULO), fc.prompt(pool, TITULO, CASO)
    bloque = (f"<caso>\nTÍTULO: {TITULO}\nÁNGULO: {CASO['angle']}\nMISTERIO: {CASO['mystery']}\n"
              f"REVELACIÓN: {CASO['reveal']}\n</caso>")
    assert con.startswith(bloque + "\n\n<pool>\n")
    assert con[len(bloque):] == sin[len(f"<caso>{TITULO}</caso>"):]          # el resto, byte a byte
    assert fc.prompt(pool, TITULO, {}).startswith(f"<caso>\nTÍTULO: {TITULO}\nÁNGULO: -\nMISTERIO: -\nREVELACIÓN: -\n")


def test_run_con_caso_anota_f44_1_y_sin_caso_f23_1(tmp_path):
    """`run` pasa el caso a la llamada y anota la versión; sin caso, f23-1 como hoy. `call` falso (sin red)."""
    d = tmp_path / "t1"
    d.mkdir()
    (d / "00_pool_v3.json").write_bytes(POOL.read_bytes())
    vistos: list[str] = []

    def call(p, **k):
        vistos.append(p)
        return {}
    con = fc.run("t1", steps_dir=tmp_path, title=TITULO, tag="t1", call=call, caso=CASO)
    sin = fc.run("t1", steps_dir=tmp_path, title=TITULO, tag="t1", call=call)
    assert con["meta"]["prompt_version"] == "f44-1" and sin["meta"]["prompt_version"] == "f23-1"
    assert "ÁNGULO: " + CASO["angle"] in vistos[0] and "ÁNGULO" not in vistos[1]
    assert con["meta"]["pool_md5"] == hashlib.md5(POOL.read_bytes()).hexdigest()
