"""
test_module_f66.py — F66 (HANDOFF_F66_verificador_narracion): el verificador de la narración a producción.
    Etapa A  narracion_verificador: SYSTEM_B/FORMATO_B literales del lab (md5), user_b, parseo, 1 reintento (sin JSON o
             excepción de API), paralelismo con 7 caps, un cap que falla dos veces no frena.
Sin API: toda llamada va con `post` falso.
"""
from __future__ import annotations

import hashlib
import json
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from script_engine import narracion_verificador as nv  # noqa: E402

ROOT = Path(__file__).resolve().parent
MD5_SYSTEM_B = "ce31cc515a077d74da72479e9693296e"       # F63 B (candado)


def _cap(n: int, oraciones: list[str]) -> dict:
    return {"cap": f"ch{n:02d}", "n": n, "titulo": "", "oraciones": [{"idx": i, "beat": n, "texto": t, "caben": 50}
                                                                      for i, t in enumerate(oraciones)]}


ARCHIVO = [{"id": "D1", "texto": "El pie no cerraba.", "fecha": "1963", "fuente": "F", "contexto_fuente": "never healed"}]
DISPUTAS = {"versiones": [], "contradicciones": []}


def _msg(obj: dict | str, usage: dict | None = None) -> dict:
    txt = obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False)
    return {"content": [{"type": "text", "text": txt}], "usage": usage or {"input_tokens": 100, "output_tokens": 10},
            "stop_reason": "end_turn"}


# ═══════════════════════ Etapa A ═══════════════════════

def test_a1_system_y_formato_literales_del_lab():
    assert hashlib.md5(nv.SYSTEM_B.encode("utf-8")).hexdigest() == MD5_SYSTEM_B
    lab = (ROOT / "lab" / "hyperframes" / "f63" / "etapa_b_verificador.py").read_text(encoding="utf-8").replace("\r\n", "\n")
    assert f'SYSTEM_B = """{nv.SYSTEM_B}"""' in lab
    assert nv.FORMATO_B.startswith('{"cap": "ch01", "afirmaciones": [{"oracion": 0, "afirmacion": "…", "estado": "respaldada"')
    assert (nv.MODELO, nv.EFFORT, nv.INTENTOS) == ("claude-opus-5-5", "medium", 2)


def test_a2_user_b_como_el_lab_y_archivo_b_reduce():
    cap = _cap(1, ["Uno.", "Dos."])
    u = nv.user_b(cap, ARCHIVO, DISPUTAS)
    assert u.endswith("\n\nFormato de salida: " + nv.FORMATO_B)
    cuerpo = json.loads(u.split("\n\nFormato de salida: ")[0])
    assert list(cuerpo) == ["cap", "oraciones", "archivo", "disputas"]
    assert cuerpo["oraciones"] == [{"idx": 0, "texto": "Uno."}, {"idx": 1, "texto": "Dos."}]    # sin beat ni caben
    ent = {"archivo": [{"id": "D1", "texto": "t", "fuente": "F", "fecha": "1", "beats_que_lo_cuentan": [1], "autor": "a",
                        "contexto_fuente": "c"}]}
    assert nv.archivo_b(ent) == [{"id": "D1", "texto": "t", "fecha": "1", "fuente": "F", "contexto_fuente": "c"}]


def test_a3_parseo_body_y_listas():
    pedidos: list[dict] = []
    resp = {"cap": "ch01", "afirmaciones": [
        {"oracion": 0, "afirmacion": "va a cerrar", "estado": "contradice", "ids": ["D1"], "fragmento": "no cerraba"},
        {"oracion": 1, "afirmacion": "dos", "estado": "sin_respaldo", "ids": [], "fragmento": None},
        {"oracion": 1, "afirmacion": "tres", "estado": "respaldada", "ids": ["D1"], "fragmento": None},
        {"oracion": 9, "afirmacion": "fuera", "estado": "contradice", "ids": ["D1"], "fragmento": "x"}]}

    def post(body):
        pedidos.append(body)
        return _msg(resp)
    log: list[str] = []
    r = nv.verificar_caps([_cap(1, ["Ese pie va a cerrar.", "Dos."])], ARCHIVO, DISPUTAS, post=post, log=log)
    b = pedidos[0]
    assert (b["model"], b["system"], b["output_config"]) == ("claude-opus-5-5", nv.SYSTEM_B, {"effort": "medium"})
    assert r["contradice"][0] == {"cap": "ch01", "oracion": 0, "texto": "Ese pie va a cerrar.", "beat": 1,
                                  "afirmacion": "va a cerrar", "ids": ["D1"], "fragmento": "no cerraba"}
    assert r["contradice"][1]["oracion"] == 9 and r["contradice"][1]["texto"] is None      # idx inexistente: anotado
    assert [x["afirmacion"] for x in r["sin_respaldo"]] == ["dos"]
    pc = r["por_cap"]["ch01"]
    assert len(pc["afirmaciones"]) == 4 and pc["error"] is None and pc["intentos"] == 1 and pc["usd"] > 0
    assert r["usd"] == pc["usd"] and log


def test_a4_un_reintento_sin_json_y_por_excepcion():
    n = {"k": 0}

    def post(body):
        n["k"] += 1
        return _msg("no hay json") if n["k"] == 1 else _msg({"afirmaciones": []})
    r = nv.verificar_caps([_cap(1, ["Uno."])], ARCHIVO, DISPUTAS, post=post)
    assert n["k"] == 2 and r["por_cap"]["ch01"]["intentos"] == 2 and r["por_cap"]["ch01"]["error"] is None
    m = {"k": 0}

    def post2(body):
        m["k"] += 1
        if m["k"] == 1:
            raise TimeoutError("api")
        return _msg({"afirmaciones": []})
    r2 = nv.verificar_caps([_cap(1, ["Uno."])], ARCHIVO, DISPUTAS, post=post2)
    assert m["k"] == 2 and r2["por_cap"]["ch01"]["error"] is None


def test_a5_un_cap_que_falla_dos_veces_no_frena_y_los_demas_siguen():
    def post(body):
        if json.loads(body["messages"][0]["content"].split("\n\nFormato")[0])["cap"] == "ch02":
            raise TimeoutError("api caída")
        return _msg({"afirmaciones": [{"oracion": 0, "afirmacion": "x", "estado": "contradice", "ids": [], "fragmento": "y"}]})
    r = nv.verificar_caps([_cap(1, ["Uno."]), _cap(2, ["Dos."])], ARCHIVO, DISPUTAS, post=post)
    assert "TimeoutError" in r["por_cap"]["ch02"]["error"] and r["por_cap"]["ch02"]["afirmaciones"] == []
    assert r["por_cap"]["ch02"]["intentos"] == 2 and [x["cap"] for x in r["contradice"]] == ["ch01"]


def test_a6_los_siete_caps_van_en_paralelo():
    barrera = threading.Barrier(7, timeout=20)                 # solo pasa si las 7 llamadas están a la vez adentro

    def post(body):
        barrera.wait()
        return _msg({"afirmaciones": []})
    t0 = time.time()
    r = nv.verificar_caps([_cap(n, ["Uno."]) for n in range(1, 8)], ARCHIVO, DISPUTAS, post=post)
    assert sorted(r["por_cap"]) == [f"ch{n:02d}" for n in range(1, 8)] and time.time() - t0 < 20
    assert all(v["error"] is None for v in r["por_cap"].values())


def test_a7_sin_caps_no_llama():
    def post(body):
        raise AssertionError("no debe llamar")
    assert nv.verificar_caps([], ARCHIVO, DISPUTAS, post=post)["usd"] == 0.0
