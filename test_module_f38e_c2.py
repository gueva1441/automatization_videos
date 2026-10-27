"""F38e §C.4 (abierto c2 de la parte C): el autor que el papel muestra en una cita (el del modelo, en español, verificado
contra el archivo; o el del archivo) es el que ve Fase 2 (`pantalla_entrada.preparar_cap` lo pone en el ítem del cap,
y de ahí lo leen los filtros, `pantalla_colocar` y el guion). Sin papel con autor, el del pool, como antes. Sintético:
nada de data/."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

from script_engine import pantalla_entrada as pe  # noqa: E402

TXT = "La gente pidió justicia en la plaza."


def _papel(tmp_path: Path, autor: str | None) -> Path:
    ficha = {"pool_id": "Q14", "sentence_idx": 0, "palabra": "justicia", "etiqueta": "LA RESPUESTA",
             "texto": "Y justicia tendréis", "estilo": "cita", "aporta": "x"}
    if autor is not None:
        ficha["autor"] = autor
    papel = {"topic_id": "t", "prompt_version": "m01e-6", "modelo": "x",
             "caps": [{"cap": "ch01", "oraciones": [TXT]}],
             "beats": [{"cap": "ch01", "beat": 1, "funcion": "revelacion", "ficha": ficha, "sello": None}],
             "relojes": [], "tarjeta": None, "descartados": []}
    d = tmp_path / "steps" / "t"
    d.mkdir(parents=True)
    (d / "01e_pantalla.json").write_text(json.dumps(papel, ensure_ascii=False), encoding="utf-8")
    return tmp_path / "steps"


def _entrada(tmp_path: Path, autor: str | None) -> dict:
    steps = _papel(tmp_path, autor)
    words = [{"word": w, "start": i * 0.5, "end": i * 0.5 + 0.4} for i, w in enumerate(TXT.split())]
    real = {"beats": [{"n": 1, "funcion": "revelacion", "t0": 0.0, "t1": 20.0, "cierre": "", "dato_central": "",
                       "datos_apoyo": []}]}
    ctx = {"topic_id": "t", "chapter_number": 1,
           "escaleta": {"beats": [{"n": 1, "cap": 1, "funcion": "revelacion"}], "a_pantalla": []},
           "pool": {"citas": [{"id": "Q14", "texto": "Y justicia tendréis", "autor": "Giovanni Leone", "fuente": "x"}]},
           "chapters": [{"chapter_number": 1, "narration": TXT}]}
    ent, rot = pe.preparar_cap(1, "ch01", real, ctx, words, 0.0, steps_dir=steps)
    assert len(rot["final"]["bloques"]) == 1
    return ent


def test_el_autor_del_papel_es_el_que_ve_fase_2(tmp_path):
    ent = _entrada(tmp_path, "Giovanni Leone, presidente del Consejo")
    assert ent["items"][0]["id"] == "Q14"
    assert ent["items"][0]["autor"] == "Giovanni Leone, presidente del Consejo"


def test_sin_autor_en_el_papel_queda_el_del_pool(tmp_path):
    ent = _entrada(tmp_path, None)
    assert ent["items"][0]["autor"] == "Giovanni Leone"
