"""F5d+ (producción de Orleans v2): comillas solo para citas, retoque de caps sueltos, G1 crítico sobre el bloque
dibujado, G2 cuerpo del titular. Sin red."""
from __future__ import annotations

from pathlib import Path

import script_engine.m01b_narrator as nb
from script_engine import gfx_critic as gc
from script_engine import m05_narrative as mn
from script_engine.gfx_project import HEAD_STEPS, archive_head_px

POOL = {"datos": [{"id": "D01", "texto": "517 reclusos no estaban contabilizados", "tipo": "cifra", "valor": "517"}],
        "cronologia": [], "lugares": [], "personajes": [],
        "citas": [{"id": "Q01", "texto": "Están en la cárcel, hombre. Mienten", "autor": "Sheriff Gusman"}]}


def test_comillas_solo_para_citas_del_pool():
    t = ('El sheriff dijo: "Están en la cárcel, hombre. Mienten". Y "El sheriff de la cárcel declaró que ningún '
         'preso murió". En la sección "Templeman III" hubo cadáveres.')
    assert mn.false_quotes(t, POOL) == ["El sheriff de la cárcel declaró que ningún preso murió"]


def test_retoque_solo_rehace_los_caps_pedidos(monkeypatch, tmp_path):
    monkeypatch.setattr(nb, "STEPS_DIR", tmp_path)
    nar = {"topic_id": "t", "chapters": [{"chapter_number": n, "narration": f"cap {n} original", "datos_usados": []}
                                         for n in range(1, 8)], "humanizer_phrases": ["a", "b", "c"]}
    seen = []

    def fake(prompt, role, cap, f5, **kw):
        seen.append((cap, [c["narration"] for c in f5["previous"]], "RETOQUE PEDIDO" in prompt))
        kw["declared"][cap] = ["D01"]
        return f"cap {cap} nuevo"
    monkeypatch.setattr(nb, "_best_of_n", fake)
    monkeypatch.setattr(nb, "_prompt_development", lambda t, s, prev, n: f"P{n}")
    out = nb.regenerate_caps({"evidence_pool": POOL}, {"chapters": []}, nar, [6, 5], extra={5: "sin comillas"})
    assert [c["narration"] for c in out["chapters"]] == ["cap 1 original", "cap 2 original", "cap 3 original",
                                                          "cap 4 original", "cap 5 nuevo", "cap 6 nuevo",
                                                          "cap 7 original"]
    assert seen[0] == (5, [f"cap {n} original" for n in range(1, 5)], True)
    assert seen[1][1][-1] == "cap 5 nuevo" and seen[1][2] is False        # el 6 ve el 5 ya retocado
    assert (tmp_path / "t" / "01b_narration.json").exists() and out["_retoque"]["caps"] == [5, 6]


def test_g2_el_titular_baja_un_cuerpo_y_no_se_corta():
    px, k = archive_head_px("las aguas residuales refluyen", 2560, 1440)
    assert k == 0
    long = "palabra " * 60                                          # no entra al cuerpo normal en un cuadro bajo
    px2, k2 = archive_head_px(long.strip(), 2560, 700)
    assert k2 >= 1 and px2 < px and px2 >= round(px * HEAD_STEPS[-1]) - 1


def test_g1_el_critico_mira_el_bloque_dibujado(tmp_path):
    from PIL import Image
    snap = tmp_path / "snap.jpg"
    Image.new("RGB", (64, 36), (40, 40, 40)).save(snap)
    plan = {"emphasis": [{"word": "celdas", "category": "oscuridad_encierro", "start": 5.0, "duration": 2.5}]}
    prompts = []

    def fake(img, prompt, *more):
        prompts.append((Path(more[0]).name if more else Path(img).name, prompt))
        return {"veredicto": "suma", "motivo": "ok"}
    rows = gc.criticize(plan, base=tmp_path / "base.mp4", words=[{"word": "celdas", "start": 5.0, "end": 5.4}], time_offset=0.0,
                        work_dir=tmp_path, cap="ch02", log=[], call=fake, fewshot=[], snaps={6.0: snap})
    assert rows and rows[0]["mira"] == "bloque dibujado" and prompts[0][0] == "snap.jpg"
    assert "YA DIBUJADO" in prompts[0][1] and "IMAGEN 1: la foto sola" in prompts[0][1]   # F5e: dos cuadros
