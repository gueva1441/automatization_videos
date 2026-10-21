"""F4e: crítico visual (gfx_critic) — veredictos, solo pasan los «suma», caché, error no vacía el cap, hoja de
contactos; y la marca de esquina apagada desde el perfil (queda el cierre)."""
from __future__ import annotations

import subprocess

import numpy as np
from PIL import Image

import gfx_config as gc
from script_engine import gfx_bug as gb
from script_engine import gfx_critic as cr


def W(text: str, step: float = 0.5) -> list[dict]:
    return [{"word": w, "start": round(k * step, 3), "end": round(k * step + 0.4, 3)} for k, w in enumerate(text.split())]


def _video(path, dur=12):
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", f"testsrc=s=640x360:r=30:d={dur}",
                    "-pix_fmt", "yuv420p", str(path)], check=True)
    return path


def _plan():
    return {"emphasis": [{"word": "putrefacta", "category": "veneno_enfermedad", "start": 1.0, "duration": 2.5,
                          "icon": "biohazard", "icon_callout": True, "side": "right"},
                         {"word": "agua", "category": "agua", "start": 5.0, "duration": 2.5, "side": "left"}],
            "archive_clippings": [{"headline": "Katrina tocó tierra el 29 de agosto", "kicker": "2005", "start": 7.0,
                                   "duration": 4.0, "side": "left"}],
            "callouts": [{"text": "4.6 metros", "start": 3.0, "duration": 2.0, "side": "left"}],
            "water_level": {"value_text": "4.6", "unit": "metros", "height": 0.6, "start": 2.0, "duration": 4.5},
            "evidence_zoom": None, "count_up": None, "pico": {"t": 2.0, "block": "water_level", "word": "sumergidos"}}


def test_describe_y_bloques():
    b = cr.blocks(_plan())
    assert [x["kind"] for x in b] == ["icono", "nivel_agua", "dato", "sello", "recorte"]
    assert "ÍCONO «biohazard»" in b[0]["desc"] and "60 %" in b[1]["desc"] and "kicker «2005»" in b[4]["desc"]


def test_solo_pasan_los_suma_cache_y_log(tmp_path):
    base = _video(tmp_path / "base.mp4")
    words = W("Calles sumergidas bajo 4.6 metros de agua putrefacta. La voz sigue hablando del agua. Fin.")
    seen = []
    verdict = {"icono": "suma", "nivel_agua": "suma", "dato": "repite", "sello": "repite", "recorte": "estorba"}

    def fake(img, prompt):
        seen.append(prompt)
        kind = next(k for k, lab in (("icono", "ÍCONO"), ("nivel_agua", "NIVEL DE AGUA"), ("dato", "DATO"),
                                     ("sello", "SELLO"), ("recorte", "RECORTE")) if f"BLOQUE PROPUESTO: {lab}" in prompt)
        return {"veredicto": verdict[kind], "motivo": f"motivo {kind}"}
    plan, log = _plan(), []
    rows = cr.criticize(plan, base=base, words=words, time_offset=0.0, work_dir=tmp_path, cap="ch02", log=log,
                        call=fake, fewshot=[{"bloque": "RECORTE x", "voz": "y", "veredicto": "suma"}])
    assert [r["veredicto"] for r in rows] == ["suma", "suma", "repite", "repite", "estorba"]
    assert [e["word"] for e in plan["emphasis"]] == ["putrefacta"] and plan["callouts"] == []
    assert plan["archive_clippings"] == [] and plan["water_level"]                         # el nivel de agua pasó
    assert sum("crítico:" in ln and "→" in ln for ln in log) == 5 and "2/5 bloques pasan" in log[-1]
    assert "EJEMPLOS aprobados" in seen[0] and "LA VOZ EN ESTE INSTANTE DICE" in seen[0] and "putrefacta" in seen[0]
    n = len(seen)
    cr.criticize(_plan(), base=base, words=words, time_offset=0.0, work_dir=tmp_path, cap="ch02", log=[], call=fake,
                 fewshot=[{"bloque": "RECORTE x", "voz": "y", "veredicto": "suma"}])
    assert len(seen) == n                                                                    # caché por (cuadro, bloque)
    sheet = cr.contact_sheet(base, rows, tmp_path / "hoja_contactos_ch02.jpg")
    im = Image.open(sheet)
    assert im.width == 3 * 648 + 8 and im.height > 360                                        # 2 cuadros en una fila


def test_error_de_gemini_no_saca_el_bloque(tmp_path):
    base = _video(tmp_path / "base.mp4", 6)
    plan = {"emphasis": [], "archive_clippings": [], "callouts": [{"text": "1 de septiembre", "start": 1.0}]}
    boom = lambda img, p: (_ for _ in ()).throw(RuntimeError("caído"))  # noqa: E731
    rows = cr.criticize(plan, base=base, words=W("hola mundo."), time_offset=0.0, work_dir=tmp_path, cap="ch05", log=[],
                        call=boom, fewshot=[])
    assert rows[0]["veredicto"] == "error" and plan["callouts"]                              # queda
    assert not (tmp_path / "gfx_critic_ch05.json").exists()                                  # y no se cachea


def test_fewshot_del_plan_dorado_y_token():
    fs = cr.load_fewshot()
    assert len(fs) == 5 and all(e["veredicto"] == "suma" for e in fs)
    assert gc.gfx_rules.visual_critic is True


def test_marca_esquina_apagada_queda_el_cierre(tmp_path, monkeypatch):
    from test_module_gfx_bug import SVG
    assert gb.config()["corner_enabled"] is False                                            # perfil misterio (F4e)
    (tmp_path / "bug").mkdir()
    (tmp_path / "bug" / "b.svg").write_text(SVG, encoding="utf-8")
    monkeypatch.setattr(gb, "GFX_PROFILES_DIR", tmp_path)
    cfg = gb.config({"channel_bug": {"enabled": True, "svg": "bug/b.svg", "height_frac": 0.2, "outro_sec": 1.0,
                                     "outro_black_sec": 0.5, "corner": {"enabled": False}}})
    assert cfg["corner_enabled"] is False
    clip = _video(tmp_path / "ch07_gfx.mp4", 2)
    out = tmp_path / "out.mp4"
    info = gb.burn_on_clip(clip, {"callouts": [], "emphasis": []}, out, cap="ch07", last_cap=True, width=640, height=360,
                           fps=30, png_dir=tmp_path / "p", cfg=cfg)
    assert info["pause"] == 1.5                                                              # el cierre sigue

    def fr(v, t):
        raw = subprocess.run(["ffmpeg", "-v", "error", "-ss", str(t), "-i", str(v), "-frames:v", "1", "-f", "rawvideo",
                              "-pix_fmt", "gray", "-"], capture_output=True, check=True).stdout
        return np.frombuffer(raw, np.uint8).reshape(360, 640).astype(float)
    assert np.abs(fr(out, 1.0) - fr(clip, 1.0)).mean() < 2.0                                 # sin marca en la esquina
