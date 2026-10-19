"""test_module_gfx_icons.py — F2b §3: íconos (lista blanca, respaldo Lucide, animaciones, icon_callout, icon_array).
Correr: python -m pytest test_module_gfx_icons.py -q
"""
import sys
from pathlib import Path

import numpy as np
import pytest
from PIL import Image

import gfx_config as gc
import script_engine.gfx_director as gd
import script_engine.gfx_icons as gi
from script_engine.gfx_literal_lock import lock, plan_strings
from script_engine.gfx_project import GfxScene, cue_events, write_project

TOY = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200" class="gfx-icon">'
       '<path class="ic-fill" fill="#e8e0cc" fill-rule="evenodd" d="M10 10L190 10L190 190Z"/>'
       '<path class="ic-accent" fill="#c8102e" d="M50 50L60 50L60 60Z"/>'
       '<g class="ic-strokes" fill="none" stroke="#e8e0cc"><path pathLength="1" d="M10 10L190 10L190 190Z"/></g></svg>')


@pytest.fixture
def approved(tmp_path, monkeypatch):
    """Set aprobado de prueba: calavera, cruz y persona (el resto sin aprobar)."""
    for k in ("calavera", "cruz", "persona"):
        (tmp_path / f"{k}.svg").write_text(TOY, encoding="utf-8")
    monkeypatch.setattr(gi, "ICONS_DIR", tmp_path)
    monkeypatch.setattr(gi, "LUCIDE_DIR", gc.GFX_PROFILES_DIR / "icons" / "lucide")
    return tmp_path


def test_lista_blanca_12_y_lucide_local():
    assert len(gi.ICON_WHITELIST) == 12
    for name in gi.ICON_WHITELIST.values():                      # respaldo local, sin red
        assert (gc.GFX_PROFILES_DIR / "icons" / "lucide" / f"{name}.svg").exists()
    moods = gc.active_moods()
    assert all(m["icon"] in gi.ICON_WHITELIST and m["icon_anim"] in gi.VALID_ICON_ANIMS for m in moods.values())


def test_sin_svg_aprobado_no_hay_icono(approved):
    assert gi.icon_svg("gota") is None                           # no aprobado, sin respaldo → texto solo
    assert gi.icon_svg("inventado") is None                      # fuera de la lista blanca: nunca
    assert gi.icon_svg("calavera") == TOY
    luc = gi.icon_svg("gota", fallback=True)                     # respaldo Lucide restilizado
    assert luc and "lucide-ink" in luc and 'stroke="#e8e0cc"' in luc and "<!--" not in luc


def test_scoped_svg_y_animaciones_deterministas():
    a = gi.scoped_svg(TOY, "ic0", 190)
    assert a == gi.scoped_svg(TOY, "ic0", 190)                   # mismo uid → mismo SVG (máscara determinista)
    assert 'id="ic0-dry"' in a and 'id="ic0-dm"' in a and 'width="190"' in a
    for anim in ("engrave", "ink_bleed", "stamp"):
        init, js = gi.anim_js("ic0", anim, 2.0, 4.5)
        assert any(".dry circle" in j for j in js) and any("opacity: 0" in j for j in js)   # salida única: tinta que se seca
    _, js = gi.anim_js("ic0", "engrave", 2.0, 4.5)
    assert "strokeDashoffset: 0" in js[0] and "inset(0% 0% 0% 0%)" in js[0]                # contorno y luego el rayado


def test_trace_saca_paths_reales_sin_texto(tmp_path):
    from script_engine.gfx_icons.trace import trace_png
    im = np.zeros((600, 600), np.uint8)
    yy, xx = np.mgrid[0:600, 0:600]
    im[(xx - 300) ** 2 + (yy - 300) ** 2 < 180 ** 2] = 255                # disco blanco
    im[(xx - 300) ** 2 + (yy - 300) ** 2 < 25 ** 2] = 0                   # hueco chico → acento
    im[10:14, :] = 255                                                     # rayón en el borde → se descarta
    Image.fromarray(im).save(tmp_path / "x.png")
    r = trace_png(tmp_path / "x.png")
    assert r["accent"] and 'class="ic-fill"' in r["svg"] and "<text" not in r["svg"]


def test_icon_callout_max_3_y_sin_icono_listado(approved):
    out = {"emphasis": [{"word": w, "category": c, "icon": ic, "start": t, "duration": 2.5}
                        for w, c, ic, t in (("veneno", "veneno_enfermedad", "calavera", 5), ("cadáveres", "muerte", "cruz", 30),
                                            ("agua", "agua", "gota", 50), ("muertos", "muerte", "cruz", 70),
                                            ("arsénico", "veneno_enfermedad", "calavera", 95))]}
    log: list[str] = []
    gd.mark_icon_callouts(out, log)
    assert [e["icon_callout"] for e in out["emphasis"]] == [True, True, False, True, False]   # gota sin aprobar; tope 3
    assert gd.emphasis_without_icon(out) == ["agua", "arsénico"]
    assert any("sin SVG aprobado" in m for m in log) and any("tope por cap" in m for m in log)


def test_icon_array_desde_fact_literal(approved):
    facts = ["Murieron 12 de los 300 presos de la sección.", "Había 6,500 personas.", "Fueron 600 de 900."]
    assert gd.array_candidates(facts, None) == [(0, 12, 300, "12 de los 300")]            # > 500 y sin relación: fuera
    words = [{"word": w, "start": float(i), "end": i + .9} for i, w in enumerate("Ese día 12 de los 300 no salieron".split())]
    log: list[str] = []
    ia = gd.place_icon_array([], ctx={"facts": facts, "eligible": None}, words=words, scenes=[GfxScene(0, 0.0, 20.0)],
                             time_offset=0.0, log=log)
    assert ia["affected"] == 12 and ia["total"] == 300 and ia["start"] == 2.0
    plan = {"chapter_number": 2, "callouts": [], "icon_array": ia}
    ok, rej = lock(plan, {"f": facts[0]}, chapter_number=2)
    assert ok["icon_array"] and "12 de los 300" in plan_strings(ok)
    bad, rej = lock({**plan, "icon_array": {**ia, "label": "12 de 999"}}, {"f": facts[0]}, chapter_number=2)
    assert bad["icon_array"] is None and rej[0]["block"] == "icon_array"


def test_templater_icon_callout_e_icon_array(approved, tmp_path):
    (tmp_path / "proj" / "public").mkdir(parents=True)
    (tmp_path / "proj" / "public" / "base.mp4").write_bytes(b"x")
    plan = {"chapter_number": 2, "title_card": None, "callouts": [], "count_up": None, "archive_clippings": [],
            "evidence_zoom": None, "punch_in": [],
            "emphasis": [{"word": "cadáveres", "category": "muerte", "layer": "muerte", "icon": "cruz", "icon_anim": "ink_bleed",
                          "icon_callout": True, "start": 2.0, "duration": 2.5, "side": "left", "stamp": True, "sid": 0}],
            "icon_array": {"affected": 12, "total": 30, "label": "12 de los 30", "start": 6.0, "duration": 4.0, "side": "right"}}
    write_project(plan, [GfxScene(0, 0.0, 12.0)], tmp_path / "proj", duration=12.0, width=2560, height=1440, fps=30)
    html = (tmp_path / "proj" / "index.html").read_text(encoding="utf-8")
    assert 'id="icc0"' in html and 'id="ic0"' in html and "cadáveres" in html and 'id="em0"' not in html
    assert html.count('href="#ia-sym"') == 30 and html.count(f'color:{gc.gfx_rules.accent_hex}"') == 12
    ev = cue_events(plan, [GfxScene(0, 0.0, 12.0)], 30)
    assert any(e["block"] == "icon_callout:muerte" for e in ev) and any(e["block"] == "icon_array" for e in ev)


def test_set_aprobado_por_omar_parada_2():
    """PARADA 2: 12 SVG aprobados; rojo SOLO en calavera (ojos), candado (cerradura) y cruz (clavo); sin texto."""
    d = gc.GFX_PROFILES_DIR / "icons"
    for key in gi.ICON_WHITELIST:
        svg = (d / f"{key}.svg").read_text(encoding="utf-8")
        assert 'class="ic-fill"' in svg and "<text" not in svg
        assert ("#c8102e" in svg) == (key in ("calavera", "candado", "cruz")), key


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
