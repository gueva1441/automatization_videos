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
    assert len(gi.ICON_WHITELIST) == 14                            # los 12 + espiral y rayo tachado (F5d+ G4)
    for key, name in gi.ICON_WHITELIST.items():                  # respaldo local, sin red
        if key in ("espiral", "rayo_tachado"):                   # sin Lucide local: solo el SVG propio aprobado
            assert (gc.GFX_PROFILES_DIR / "icons" / f"{key}.svg").exists()
            continue
        assert (gc.GFX_PROFILES_DIR / "icons" / "lucide" / f"{name}.svg").exists()
    moods = gc.active_moods()
    assert gc.ICON_KEYS == set(gi.ICON_WHITELIST)
    assert all(set(m["icon_words"].values()) <= set(gi.ICON_WHITELIST) and m["icon_anim"] in gi.VALID_ICON_ANIMS
               for m in moods.values())
    assert not any(m["icon_anim"] == "engrave" for m in moods.values())          # potrace = rellenos → press_wipe


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
    # engrave sobre un SVG de RELLENOS (potrace) → press_wipe; engrave real solo con trazos (Lucide)
    init, js = gi.anim_js("ic0", "engrave", 2.0, 4.5)
    assert '#ic0 .pw", { y: -12.00' in init[0] and '#ic0 .pw", { y: 240.00, duration: 0.8' in js[0]
    _, js = gi.anim_js("ic0", "engrave", 2.0, 4.5, k=.12, strokes_only=True)
    assert "strokeDashoffset: 0" in js[0]
    assert 'id="ic0-pw"' in a and 'class="pw" transform="translate(0 240.00)"' in a       # arranca abierto


def test_hold_vivo_y_pulso_unico_del_rojo():
    """Entre la entrada y la salida: respiración 0.85–1 (medio ciclo < 1 s), deriva ±3 px, un pulso del rojo."""
    _, js = gi.anim_js("ic0", "ink_bleed", 2.0, 6.0, has_accent=True)
    hold = " ".join(js)
    assert 'opacity: .85, duration: 0.9' in hold and gi.BREATH_SEC < 1.0                   # nunca quieto > 1 s
    assert "x: 3.0" in hold and "x: -3.0" in hold                                          # deriva ±3 px
    assert hold.count(".ic-accent") == 1 and "repeat: 1 }" in hold                          # un único pulso del rojo
    assert hold.index("opacity: .85") < hold.index(".dry circle")                          # después, tinta que se seca
    _, js2 = gi.anim_js("ic0", "ink_bleed", 2.0, 6.0, has_accent=False)
    assert ".ic-accent" not in " ".join(js2)


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


def test_set_aprobado_por_omar_parada_2():
    """PARADA 2: 12 SVG aprobados; rojo SOLO en calavera (ojos), candado (cerradura) y cruz (clavo); sin texto."""
    d = gc.GFX_PROFILES_DIR / "icons"
    for key in gi.ICON_WHITELIST:
        svg = (d / f"{key}.svg").read_text(encoding="utf-8")
        assert 'class="ic-fill"' in svg and "<text" not in svg
        assert ("#c8102e" in svg) == (key in ("calavera", "candado", "cruz")), key


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
