"""F4b §2: fragmento literal más impactante (gfx_fragments) — opciones literales, elección por número, ícono, dedupe."""
from __future__ import annotations

import json

from dataclasses import replace

import pytest

import gfx_config
from script_engine import gfx_fragments as gf
from script_engine.gfx_project import GfxScene


@pytest.fixture
def sin_doctrina(monkeypatch):
    """Comportamiento F4b (opciones de la narración, sin kicker obligatorio): las reglas R6/R7 apagadas; ícono por
    categoría (F5b S4 apagado: icon_literal_only=False)."""
    monkeypatch.setattr(gfx_config, "gfx_rules", replace(gfx_config.gfx_rules, doc_clippings=False,
                                                         icon_literal_only=False))

FACT_A = "Los presos estuvieron con el agua hasta el pecho, agua putrefacta, durante días."
FACT_B = "Aproximadamente 6,500 personas estaban en la prisión."
MOODS = {"veneno_enfermedad": {"triggers": {"putrefacta": 3, "veneno": 3}, "icon_words": {"veneno": "calavera", "tóxico": "calavera",
                                                                                           "plaga": "biohazard"}},
         "agua": {"triggers": {"agua": 1}, "icon_words": {"agua": "gota"}}}


def W(text: str, step: float = 0.5) -> list[dict]:
    return [{"word": w, "start": round(k * step, 3), "end": round(k * step + 0.4, 3)} for k, w in enumerate(text.split())]


def test_fragmentos_literales_por_clausula():
    fr = gf.fragments(FACT_A, 8, key_words={"putrefacta"})
    assert fr[0] == "agua putrefacta"                                      # trae palabra de carga y es corto
    assert "agua hasta el pecho" in fr and all(gf.literal_in(f, FACT_A) for f in fr)
    assert all(len(f.split()) <= 8 for f in fr) and not any(f.split()[0].lower() in gf.EDGE_STOP for f in fr)
    assert all("6,500" in f for f in gf.fragments(FACT_B + " Eran 6,500 almas.", 6, must="6,500"))
    assert gf.core_token("6,500 personas") == "6,500" and gf.core_token("Templeman III") == "Templeman"


def _plan():
    return {"archive_clippings": [{"headline": "Los presos estuvieron con el agua hasta el pecho", "fact_idx": 0,
                                   "scene_idx": 0, "start": 1.0}],
            "callouts": [{"text": "6,500 personas", "fact_idx": 1, "start": 1.0, "kind": "figure"}]}


def test_eleccion_por_numero_icono_y_fallback(tmp_path, sin_doctrina):
    words = W("Eran 6,500 almas encerradas en el agua putrefacta.")
    scenes = [GfxScene(0, 0.0, 20.0)]
    ctx = {"facts": [FACT_A, FACT_B], "chapter_number": 3}
    plan = _plan()
    seen = {}

    def fake(prompt, **kw):
        seen["p"] = prompt
        items = gf.build_items(_plan(), facts=ctx["facts"], words=words, scenes=scenes, time_offset=0.0,
                               key_words={w for m in MOODS.values() for w in m["triggers"]})
        n_a = items[0]["options"].index("agua putrefacta") + 1
        n_b = items[1]["options"].index("6,500 almas") + 1
        return {"elecciones": [{"id": "recorte0", "n": n_a}, {"id": "dato0", "n": n_b}]}
    tab = gf.choose_fragments(plan, ctx=ctx, words=words, scenes=scenes, time_offset=0.0, moods=MOODS, work_dir=tmp_path,
                              cap="ch03", call=fake)
    assert plan["archive_clippings"][0]["headline"] == "agua putrefacta" and plan["callouts"][0]["text"] == "6,500 almas"
    assert plan["archive_clippings"][0]["icon"] == "calavera" and tab[0]["categoria"] == "veneno_enfermedad"   # «con ícono»
    assert all(e in seen["p"] for e in gf.EXAMPLES[:2]) and "1. Los presos estuvieron" in seen["p"]
    plan2 = _plan()
    gf.choose_fragments(plan2, ctx=ctx, words=words, scenes=scenes, time_offset=0.0, moods=MOODS, work_dir=tmp_path / "x",
                        cap="ch03", call=lambda p, **k: {"elecciones": [{"id": "recorte0", "n": 999}]})
    assert plan2["archive_clippings"][0]["headline"] == _plan()["archive_clippings"][0]["headline"]          # fuera de lista → el de hoy


def test_titular_ya_usado_en_otro_cap_no_se_repite(tmp_path, sin_doctrina):
    (tmp_path / "gfx_plan_ch01.resolved.json").write_text(json.dumps({"plan": {"archive_clippings": [{"headline": "agua putrefacta"}]}}),
                                                          encoding="utf-8")
    words, scenes = W("agua putrefacta"), [GfxScene(0, 0.0, 20.0)]
    ctx = {"facts": [FACT_A, FACT_B], "chapter_number": 3}
    plan = _plan()

    def pick(prompt, **kw):
        items = gf.build_items(_plan(), facts=ctx["facts"], words=words, scenes=scenes, time_offset=0.0, key_words={"putrefacta"})
        return {"elecciones": [{"id": "recorte0", "n": items[0]["options"].index("agua putrefacta") + 1}]}
    gf.choose_fragments(plan, ctx=ctx, words=words, scenes=scenes, time_offset=0.0, moods=MOODS, work_dir=tmp_path,
                        cap="ch03", call=pick)
    assert plan["archive_clippings"][0]["headline"] == "Los presos estuvieron con el agua hasta el pecho"


def test_sin_llm_quedan_los_textos_de_hoy(tmp_path, sin_doctrina):
    plan = _plan()
    boom = lambda p, **k: (_ for _ in ()).throw(RuntimeError("caído"))  # noqa: E731
    log: list[str] = []
    assert gf.choose_fragments(plan, ctx={"facts": [FACT_A, FACT_B], "chapter_number": 2}, words=W("x y"),
                               scenes=[GfxScene(0, 0.0, 9.0)], time_offset=0.0, moods=MOODS, work_dir=tmp_path,
                               cap="ch02", call=boom, log=log) == []
    assert plan == _plan() and "Flash falló" in log[0]


# ── F4c R6: el recorte es un documento · R7: el dato no repite

FACT_K = "El huracán Katrina tocó tierra el 29 de agosto de 2005."
FACT_S = "Los prisioneros quedaron atrapados durante días en celdas inundadas con agua contaminada con aguas residuales."


def test_documento_suma_algo_y_kicker_obligatorio():
    span = "Katrina desató su furia implacable sobre la ciudad"
    assert gf.adds_something("Katrina tocó tierra el 29 de agosto", span) == "fecha «29 de agosto»"
    assert gf.adds_something("Katrina desató su furia", span) is None                         # repite la voz
    assert gf.adds_something("agua contaminada con aguas residuales", "celdas inundadas con agua") == "palabra «contaminada»"
    assert "Katrina tocó tierra el 29 de agosto" in gf.fragments(FACT_K, 8)                   # el año se va al kicker
    assert gf.doc_kicker(FACT_K, "", "Katrina tocó tierra el 29 de agosto", "") == "2005"
    assert gf.doc_kicker(FACT_S, "", "celdas inundadas", "Era 2005 en Orleans.") == "2005"       # el año que dice la voz
    assert gf.doc_kicker(FACT_S, "", "celdas inundadas", "sin años") == ""
    assert gf.doc_kicker(FACT_S, "Human Rights Watch, 2005", "x", "") == "Human Rights Watch, 2005"


def test_recorte_sin_narracion_y_sin_kicker_se_quita(tmp_path):
    words = W("Katrina desató su furia implacable. Los presos quedaron en celdas inundadas.")
    scenes = [GfxScene(0, 0.0, 20.0)]
    ctx = {"facts": [FACT_K, FACT_S], "chapter_number": 2, "fact_source": {}}
    plan = {"archive_clippings": [{"headline": "Katrina desató su furia implacable", "fact_idx": 0, "scene_idx": 0,
                                   "start": 1.0, "kicker": "2005"},
                                  {"headline": "celdas inundadas", "fact_idx": 1, "scene_idx": 0, "start": 8.0, "kicker": ""}],
            "callouts": []}
    seen = {}

    def fake(prompt, **kw):
        seen["p"] = prompt
        return {"elecciones": []}
    log: list[str] = []
    tab = gf.choose_fragments(plan, ctx=ctx, words=words, scenes=scenes, time_offset=0.0, moods=MOODS, work_dir=tmp_path,
                              cap="ch02", call=fake, log=log)
    a = plan["archive_clippings"]
    assert [x["fact_idx"] for x in a] == [0] and a[0]["kicker"] == "2005"                    # sin año ni fuente → fuera
    assert gf.literal_in(a[0]["headline"], FACT_K) and "desató" not in a[0]["headline"]
    opts = [ln for ln in seen["p"].splitlines() if ln.strip()[:2].rstrip(".").isdigit()]
    assert opts and not any("desató" in ln for ln in opts)                                   # nunca de la narración
    assert "La voz en ese tramo ya dice" in seen["p"] and "(suma: fecha «29 de agosto»" in seen["p"]
    assert any(r["ahora"] is None and "kicker" in r["motivo"] for r in tab)


def test_dato_que_la_voz_dice_se_quita():
    words = W("Según Human Rights Watch eran seis mil quinientas personas en Templeman III.")
    plan = {"callouts": [{"text": "Human Rights Watch", "start": 0.5}, {"text": "6,500", "start": 2.5},
                         {"text": "Templeman III", "start": 5.0}]}
    rows = gf.drop_repeated_callouts(plan, words=words, time_offset=0.0, log=[])
    assert [c["text"] for c in plan["callouts"]] == ["6,500"] and len(rows) == 2               # la cifra en dígitos suma


def test_parentesis_cortan_clausula():
    fr = gf.fragments("Algunas partes quedaron bajo 15 pies (4.6 metros) de agua.", 6, must="4.6")
    assert "4.6 metros" in fr and not any("pies" in f for f in fr)



def test_documento_kicker_nunca_repetido_y_candado_sin_comillas():
    """F4c R6: una opción cuyo año/fecha ya está en el titular sin otro kicker posible no entra; tampoco una que el
    candado rechazaría (el fact trae comillas que el fragmento pierde)."""
    fact_q = "Reclusos de la sección 'Templeman III' informaron haber visto cadáveres flotando."
    assert not gf.lock_ok("sección Templeman III informaron", fact_q) and gf.lock_ok("cadáveres flotando", fact_q)
    words = W("La tormenta llegó a la costa.")
    items = gf.build_items({"archive_clippings": [{"headline": "Katrina tocó tierra el 29 de agosto", "fact_idx": 0,
                                                  "scene_idx": 0, "start": 1.0}]},
                           facts=[FACT_K], words=words, scenes=[GfxScene(0, 0.0, 20.0)], time_offset=0.0,
                           key_words=set(), documents=True)
    assert not any("2005" in o for o in items[0]["options"])                   # «… de 2005» dejaría el kicker vacío
    assert gf._doc_rank("agua contaminada con aguas residuales", "celdas inundadas", "celdas inundadas presos agua") < \
        gf._doc_rank("prisioneros quedaron atrapados durante días", "celdas inundadas", "prisioneros quedaron atrapados")
