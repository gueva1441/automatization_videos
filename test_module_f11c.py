"""
test_module_f11c.py — F11c (estructura oficial del prompt + modelo propio del guionista): el sistema trae rol, voz,
oficio y ejemplos; el usuario trae los datos y termina en <tarea>; `gemini-4-argon` es del guion v4 y no toca
`gemini_model_research`; el editor m01c se saltea con 0 bloqueantes (y corre con bloqueantes). Sin red.
"""
from __future__ import annotations

from pathlib import Path

import gemini_helpers as gh
from script_engine import guion_v4 as g4
from test_module_f11 import TOPIC, _esc_ok, _parrafos

ROOT = Path(__file__).resolve().parent


# ═══════════════════════════════════════════════════════════════
#  Estructura del prompt (§1.1)
# ═══════════════════════════════════════════════════════════════

def test_sistema_rol_voz_oficio_ejemplos_en_orden():
    s = g4.system()
    tags = ["<rol>", "</rol>", "<voz>", "</voz>", "<oficio>", "</oficio>", "<ejemplos_de_voz>", "</ejemplos_de_voz>"]
    pos = [s.index(t) for t in tags]
    assert pos == sorted(pos)
    assert "Misterios Sepultados" in s and "No inventás" in s
    assert all(x in s for x in g4.OFICIO) and len(g4.OFICIO) == 8
    assert all(e in s for e in g4.EJEMPLOS_VOZ) and len(g4.EJEMPLOS_VOZ) == 2
    assert "═══" not in s and "──" not in s                            # un solo formato de delimitadores (XML)


def test_ejemplos_literales_de_orleans_f7c3():
    src = (ROOT / "lab/hyperframes/f7/NARRACION_orleans_v3r3.md").read_text(encoding="utf-8").splitlines()
    assert all(e in src for e in g4.EJEMPLOS_VOZ)                       # párrafos enteros, copiados literal


def test_usuario_datos_primero_y_tarea_al_final():
    esc = _esc_ok()
    p = g4.prompt(TOPIC, esc)
    assert p.startswith("<caso>") and p.index("</caso>") < p.index("<escaleta>") < p.index("</escaleta>")
    assert p.rstrip().endswith("</tarea>") and p.index("<tarea>") > p.index("</escaleta>")
    assert "el espectador se pregunta:" in p and "queda abierta" not in p
    assert not any(x in p for x in g4.OFICIO) and "<rol>" not in p    # el oficio y el rol van en el sistema
    assert "═══" not in p and "──" not in p
    assert g4.PROMPT_VERSION == "f11c-1"


def test_write_manda_sistema_y_usuario_separados():
    esc = _esc_ok()
    seen = {}

    def call(prompt, **kw):
        seen.update(prompt=prompt, system=kw.get("system_instruction"))
        return {"parrafos": [{"beat": p["beat"], "texto": p["texto"]} for p in _parrafos(esc)]}
    g4.write(TOPIC, esc, call=call)
    assert seen["system"] == g4.system() and seen["prompt"] == g4.prompt(TOPIC, esc)


# ═══════════════════════════════════════════════════════════════
#  Modelo propio del guionista (§1.2)
# ═══════════════════════════════════════════════════════════════

def test_argon_es_del_guion_y_no_del_research(monkeypatch):
    seen = {}

    class _Models:
        def generate_content(self, model, contents, config):
            seen.update(model=model, config=config)

            class R:
                text = '{"texto": "hola"}'
                usage_metadata = None
            return R()

    class _Client:
        models = _Models()
    monkeypatch.setattr(gh, "_client", _Client())
    call = g4.call_for("gemini-4-argon")
    assert call.model == "gemini-4-argon"
    assert call("x", response_schema=g4.EDIT_SCHEMA, description="t") == {"texto": "hola"}
    assert seen["model"] == "gemini-4-argon"
    assert gh._cfg.gemini_model_research != "gemini-4-argon"           # el research sigue con su modelo
    cfg = seen["config"]
    assert cfg.temperature is None and cfg.top_p is None and cfg.top_k is None and cfg.thinking_config is None
    assert g4.call_for("gemini-pro") is gh.call_pro_json                 # F12: None → Sol (test_module_f12)


def test_argon_precio_oficial():
    from cost_tracker import _gemini_rates_for
    assert _gemini_rates_for("gemini-4-argon") == {"input": 2.00, "output": 10.00}


# ═══════════════════════════════════════════════════════════════
#  Sin m01c con 0 bloqueantes (§1.3)
# ═══════════════════════════════════════════════════════════════

def _fake(calls):
    def call(prompt, **kw):
        calls.append(kw.get("description"))
        if kw.get("description") == "guion_v4 editor":
            return {"parrafos": [], "cambios": []}
        if kw.get("description") == "guion_v4 editar frase":
            return {"texto": prompt.split("PÁRRAFO:\n")[1].replace(" Murieron 412 personas.", "")}
        raise AssertionError(kw.get("description"))
    return call


def test_sin_m01c_con_cero_bloqueantes():
    esc = _esc_ok()
    ps = _parrafos(esc)
    assert g4.bloqueantes(TOPIC, esc, ps) == []
    calls: list = []
    log: list[str] = []
    r = g4.reparar(TOPIC, esc, ps, call=_fake(calls), log=log)
    assert calls == [] and r["pasos"]["editor"] == []
    assert [p["texto"] for p in r["parrafos"]] == [p["texto"] for p in ps]
    assert any("sin pasada del editor m01c" in x for x in log)


def test_con_bloqueantes_la_ronda_sigue_igual():
    esc = _esc_ok()
    ps = _parrafos(esc)
    ps[0]["texto"] += " Murieron 412 personas."
    calls: list = []
    g4.reparar(TOPIC, esc, ps, call=_fake(calls))
    assert calls == ["guion_v4 editar frase", "guion_v4 editor"]       # edición de oración + editor m01c
