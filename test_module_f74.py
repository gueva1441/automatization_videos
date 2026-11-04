"""F74 — semilla manual desde el form (modo C) + receta remeasure para medirla. Sin red: `input()` y `_measure_es`
se reemplazan por dobles; nada escribe en disco (discover_niches se corta en el primer input)."""
import json
import re
import sys
from pathlib import Path

import pytest

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R))

import fase1  # noqa: E402
import niche_discoverer as nd  # noqa: E402
import qa_form_markers as qfm  # noqa: E402

PREFIJO = "@@QAFORM@@ "


def _marcadores(out: str) -> list[dict]:
    return [json.loads(l[len(PREFIJO):]) for l in out.splitlines() if l.startswith(PREFIJO)]


def _inputs(monkeypatch, respuestas, prompts=None):
    it = iter(respuestas)

    def falso(prompt=""):
        if prompts is not None:
            prompts.append(prompt)
        return next(it)
    monkeypatch.setattr("builtins.input", falso)


# ─── Etapa 1: contrato del marcador de texto libre ───
@pytest.mark.parametrize("emitir", [nd._emit_qaform_text_marker, qfm.emit_text_marker])
def test_marcador_text_contrato(monkeypatch, capsys, emitir):
    monkeypatch.setattr(nd, "_QA_FORM", True)
    monkeypatch.setattr(qfm, "QA_FORM", True)
    emitir("manual_title", "Tema (enter vacío = terminar)", body="Temas agregados: 1")
    out = capsys.readouterr().out
    lineas = out.splitlines()
    assert len(lineas) == 1 and lineas[0].startswith(PREFIJO)
    assert lineas[0].isascii()
    m = json.loads(lineas[0][len(PREFIJO):])
    assert m == {"menu": "manual_title", "accept": "text", "prompt": "Tema (enter vacío = terminar)",
                 "placeholder": None, "body": "Temas agregados: 1"}


@pytest.mark.parametrize("emitir", [nd._emit_qaform_text_marker, qfm.emit_text_marker])
def test_marcador_text_sin_qa_form_no_imprime(monkeypatch, capsys, emitir):
    monkeypatch.setattr(nd, "_QA_FORM", False)
    monkeypatch.setattr(qfm, "QA_FORM", False)
    emitir("manual_title", "Tema")
    assert capsys.readouterr().out == ""


def test_menus_manuales_no_son_nombres_especiales_del_form():
    html = (R / "qa_form.html").read_text(encoding="utf-8")
    for menu in ("manual_title", "manual_root"):
        assert menu not in html                      # no lo intercepta handleMarker → va a showDialog
    assert not any(m.endswith("_gate") for m in ("manual_title", "manual_root"))


def test_host_enruta_text_a_qa_text_antes_de_render_seeds():
    html = (R / "qa_form.html").read_text(encoding="utf-8")
    assert "m.accept==='text'" in html and "'|text|'" in html
    assert "'__text__'" in html
    assert html.index("renderText(marker)") < html.index("renderSeeds(")
    import qa_studio_server as qs
    assert qs._FORM_MENU_HTML["__text__"] == qs.BASE_DIR / "qa_text.html"
    assert (R / "qa_text.html").exists()


def test_qa_text_nunca_manda_cancel_y_value_es_string():
    src = (R / "qa_text.html").read_text(encoding="utf-8")
    assert "function renderText" in src and "qaFormAnswer" in src
    src = re.sub(r"<!--.*?-->", "", src, flags=re.S)
    src = re.sub(r"//[^\n]*|/\*.*?\*/", "", src.split("<script>", 1)[1], flags=re.S)   # solo código, sin comentarios
    assert "'cancel'" not in src and '"cancel"' not in src
    assert "action:'choose'" in src.replace(" ", "") or 'action:"choose"' in src.replace(" ", "")


class _Stdin:
    def __init__(self, qs, falla=False):
        self.qs, self.falla, self.vistos = qs, falla, []

    def write(self, s):
        if self.falla:
            raise BrokenPipeError("cerrado")
        self.vistos.append((s, self.qs._FORM["marker"]))

    def flush(self):
        pass


class _Proc:
    def __init__(self, stdin):
        self.stdin = stdin

    def poll(self):
        return None


def test_form_answer_limpia_el_marcador_antes_de_escribir(monkeypatch):
    """El race de F74: Tema y Nicho salen seguidos; si la limpieza va después de escribir, borra el del nicho."""
    import qa_studio_server as qs
    st = _Stdin(qs)
    monkeypatch.setitem(qs._FORM_PROC, "p", _Proc(st))
    monkeypatch.setitem(qs._FORM, "marker", {"menu": "manual_title", "accept": "text"})
    assert qs._form_answer("Palomares 1966") == {"ok": True}
    assert st.vistos == [("Palomares 1966\n", None)]


def test_form_answer_si_falla_la_escritura_devuelve_el_marcador(monkeypatch):
    import qa_studio_server as qs
    m = {"menu": "manual_title", "accept": "text"}
    monkeypatch.setitem(qs._FORM_PROC, "p", _Proc(_Stdin(qs, falla=True)))
    monkeypatch.setitem(qs._FORM, "marker", m)
    assert "error" in qs._form_answer("x")
    assert qs._FORM["marker"] == m


def test_form_answer_acepta_linea_vacia_para_terminar(monkeypatch):
    import qa_studio_server as qs
    st = _Stdin(qs)
    monkeypatch.setitem(qs._FORM_PROC, "p", _Proc(st))
    monkeypatch.setitem(qs._FORM, "marker", None)
    assert qs._form_answer("") == {"ok": True}
    assert st.vistos == [("\n", None)]


# ─── Etapa 2: modo C en el form ───
def test_modo_c_habilitado_en_el_menu(monkeypatch, capsys):
    monkeypatch.setattr(nd, "_QA_FORM", True)
    monkeypatch.setattr(nd, "_n_estante", lambda: 0)     # F77: el menú lee el estante; el test no toca el disco real

    class Corte(Exception):
        pass

    def corta(prompt=""):
        raise Corte
    monkeypatch.setattr("builtins.input", corta)
    with pytest.raises(Corte):
        nd.discover_niches()
    m = _marcadores(capsys.readouterr().out)[0]
    assert m["menu"] == "discovery_mode"
    c = next(o for o in m["options"] if o["key"] == "C")
    assert "disabled" not in c and c["label"] == "✏️ Inyección manual — escribí el tema"


def test_run_manual_con_qa_form_emite_text_y_choice_y_trae_remeasure(monkeypatch, capsys):
    monkeypatch.setattr(nd, "_QA_FORM", True)
    _inputs(monkeypatch, ["Palomares 1966", "0", ""])
    seeds = nd._run_manual()
    ms = _marcadores(capsys.readouterr().out)
    assert [(m["menu"], m["accept"]) for m in ms] == [("manual_title", "text"), ("manual_root", "key"),
                                                       ("manual_title", "text")]
    assert ms[0]["prompt"] == "Tema (enter vacío = terminar)" and ms[0]["body"] is None
    raiz = ms[1]
    assert raiz["default"] == "0"
    claves = [o["key"] for o in raiz["options"]]
    assert claves == [str(i) for i in range(1, len(nd.ROOT_NICHES) + 1)] + ["0"]
    assert raiz["options"][-1]["label"] == "Ninguno / otro"
    assert ms[2]["body"] == "Temas agregados: 1"
    assert len(seeds) == 1
    s = seeds[0]
    assert s["seed_title"] == "Palomares 1966" and s["discovery_mode"] == "manual" and s["root_niche"] is None
    assert s["remeasure"] == {"es_query": "Palomares 1966", "entity": "Palomares 1966", "already_es": True}


def test_run_manual_nicho_elegido_por_numero(monkeypatch):
    monkeypatch.setattr(nd, "_QA_FORM", True)
    _inputs(monkeypatch, ["Palomares 1966", "1", ""])
    assert nd._run_manual()[0]["root_niche"] == list(nd.ROOT_NICHES)[0]


def test_run_manual_sin_qa_form_igual_que_hoy(monkeypatch, capsys):
    monkeypatch.setattr(nd, "_QA_FORM", False)
    prompts = []
    _inputs(monkeypatch, ["Palomares 1966", "0", ""], prompts)
    seeds = nd._run_manual()
    out = capsys.readouterr().out
    assert PREFIJO.strip() not in out
    assert prompts == ["     📌 Tema: ", "        👉 ", "     📌 Tema: "]
    assert "[0] Ninguno / otro" in out
    assert seeds[0]["remeasure"]["already_es"] is True


def test_gate_re_mide_la_semilla_manual_disputado_pregunta_psq(monkeypatch, capsys):
    monkeypatch.setattr(nd, "_QA_FORM", False)
    _inputs(monkeypatch, ["Palomares 1966", "0", ""])
    seed = nd._run_manual()[0]
    capsys.readouterr()
    llamadas = []

    def medir(q, entity, already_es=False):
        llamadas.append((q, entity, already_es))
        return {"label": "DISPUTADO", "saturation": 62000}
    monkeypatch.setattr(fase1, "_measure_es", medir)
    monkeypatch.setattr(fase1, "_QA_FORM", True)
    _inputs(monkeypatch, ["P"])
    kept = fase1._verify_pick_es_saturation([seed], n=3)
    out = capsys.readouterr().out
    assert llamadas == [("Palomares 1966", "Palomares 1966", True)] * 3
    assert "sin receta remeasure" not in out
    assert "FLIPEÓ a DISPUTADO" in out
    m = [x for x in _marcadores(out) if x["menu"] == "remeasure_pick"][0]
    assert [o["key"] for o in m["options"]] == ["P", "S", "Q"]
    assert kept == [seed]


@pytest.mark.parametrize("resp,esperado", [("S", None), ("Q", None)])
def test_gate_semilla_manual_sacar_o_salir(monkeypatch, capsys, resp, esperado):
    seed = nd._build_seed("Palomares 1966", "manual", None, {},
                          remeasure={"es_query": "Palomares 1966", "entity": "Palomares 1966", "already_es": True})
    monkeypatch.setattr(fase1, "_measure_es", lambda *a, **k: {"label": "DISPUTADO", "saturation": 62000})
    monkeypatch.setattr(fase1, "_QA_FORM", False)
    _inputs(monkeypatch, [resp])
    assert fase1._verify_pick_es_saturation([seed], n=3) == esperado
