"""F4b §2: fragmento literal más impactante (gfx_fragments) — opciones literales, elección por número, ícono, dedupe."""
from __future__ import annotations

import json

from script_engine import gfx_fragments as gf
from script_engine.gfx_project import GfxScene

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


def test_eleccion_por_numero_icono_y_fallback(tmp_path):
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


def test_titular_ya_usado_en_otro_cap_no_se_repite(tmp_path):
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


def test_sin_llm_quedan_los_textos_de_hoy(tmp_path):
    plan = _plan()
    boom = lambda p, **k: (_ for _ in ()).throw(RuntimeError("caído"))  # noqa: E731
    log: list[str] = []
    assert gf.choose_fragments(plan, ctx={"facts": [FACT_A, FACT_B], "chapter_number": 2}, words=W("x y"),
                               scenes=[GfxScene(0, 0.0, 9.0)], time_offset=0.0, moods=MOODS, work_dir=tmp_path,
                               cap="ch02", call=boom, log=log) == []
    assert plan == _plan() and "Flash falló" in log[0]


def test_parentesis_cortan_clausula():
    fr = gf.fragments("Algunas partes quedaron bajo 15 pies (4.6 metros) de agua.", 6, must="4.6")
    assert "4.6 metros" in fr and not any("pies" in f for f in fr)

