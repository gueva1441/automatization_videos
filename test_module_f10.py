"""
test_module_f10.py — F10 §4.1: m01d_particion (contrato de 7 caps) y el camino v3 de fase1_5.
"""
from __future__ import annotations

import json

import pytest

import fase1_5 as f15
from script_engine import m01d_particion as md
from script_engine.tts_tags import strip_tags

DEV = "Una oración de relleno con hechos del beat, contada con calma y con detalle. " * 3   # ≈ 230 caracteres


def _esc():
    beats = [{"n": 1, "cap": 1, "funcion": "gancho", "intensidad": 4, "dato_central": "D1",
              "imagen_sensorial": "el agua negra en la celda", "emocion": "miedo", "datos_apoyo": []}]
    k = 2
    for cap in range(2, 7):
        for _ in range(2):
            beats.append({"n": k, "cap": cap, "funcion": "escalada", "intensidad": min(5, cap - 1), "dato_central": f"D{k}",
                          "imagen_sensorial": f"imagen del beat {k}", "emocion": "angustia", "datos_apoyo": []})
            k += 1
    beats.append({"n": k, "cap": 7, "funcion": "cierre", "intensidad": 2, "dato_central": f"D{k}",
                  "imagen_sensorial": "una celda vacía", "emocion": "tristeza", "datos_apoyo": []})
    caps = [{"chapter_number": n, "role": "hook" if n == 1 else "reveal_outro" if n == 7 else "development",
             "render_engine": "veo" if n in (1, 7) else "flux", "duration_seconds": 45 if n in (1, 7) else 105,
             "narrative_intent": "hook" if n == 1 else "setup", "evidence_ids": [f"D{n}"], "cliffhanger": "",
             "pantalla_ids": [f"T{n}"]} for n in range(1, 8)]
    return {"beats": beats, "caps": caps, "pico": {"beat": 9}, "humano": {"id": "P01"}, "antagonista": {"id": "P02"},
            "_pool_plan": {"pantalla": {}}, "prompt_version": "x"}


def _parrafos(esc, n_per_beat=4):
    out = []
    for b in esc["beats"]:
        reps = 2 if b["cap"] in (1, 7) else n_per_beat
        for _ in range(reps):
            out.append({"beat": b["n"], "cap": b["cap"], "texto": DEV.strip(), "ids_usados": [b["dato_central"]]})
    return out


POOL = {"datos": [{"id": f"D{k}", "texto": f"dato {k}"} for k in range(1, 20)], "cronologia": [], "citas": [],
        "personajes": [{"id": "P01", "nombre": "Blas Cristaldo", "rol": "esposo de una víctima"},
                       {"id": "P02", "nombre": "Juan Pío Paiva", "rol": "dueño"}]}


def test_contrato_de_7_caps_completo():
    esc = _esc()
    sk, na, n3 = md.build_contract({"id": "t"}, esc, _parrafos(esc), POOL, title_list=[f"T{n}" for n in range(1, 8)])
    assert len(sk["chapters"]) == 7 and len(na["chapters"]) == 7
    for c in sk["chapters"]:
        assert all(k in c for k in ("chapter_number", "title", "role", "render_engine", "duration_seconds",
                                    "narrative_intent", "bullets", "evidence_ids", "cliffhanger", "pantalla_ids"))
    assert sk["chapters"][1]["bullets"][0] == "imagen del beat 2 · dato 2"         # imagen sensorial + dato central
    assert sk["chapters"][0]["pantalla_ids"] == ["T1"] and sk["chapters"][0]["render_engine"] == "veo"
    assert [p["nombre"] for p in sk["personajes"]] == ["Blas Cristaldo", "Juan Pío Paiva"]
    assert sk["personajes"][1]["antagonista"] is True
    for c in na["chapters"]:
        assert all(k in c for k in ("chapter_number", "narration", "datos_usados", "ids_usados", "narration_tts"))
        assert strip_tags(c["narration_tts"]) == strip_tags(c["narration"]) and "[" not in c["narration"]
    assert na["humanizer_phrases"] == [] and len(n3["parrafos"]) == len(_parrafos(esc))


def test_particion_en_frontera_de_parrafo_y_pico_intacto():
    esc = _esc()
    ps = _parrafos(esc, n_per_beat=6)                       # caps de desarrollo con ≈ 2,800 caracteres: se pasan
    lo, hi = md.len_range("development")
    from script_engine.video_length import char_band
    assert hi == int(char_band("development")[1] * 1.15)             # F23: la banda sale de video_length (antes 2000)
    out, notes = md.rebalance(esc, ps)
    assert all(p["texto"] == DEV.strip() for p in out)   # nunca se corta un párrafo por la mitad
    pico = [p for p in out if p["beat"] == 9]
    assert all(p["cap"] == 5 for p in pico)               # el pico (beat 9, cap 5) no se mueve de cap
    assert any("no se pudo mover ni acortar" in x or "pasa al cap" in x for x in notes)


def test_acortar_con_el_editor_cuando_no_se_puede_mover():
    esc = _esc()
    ps = _parrafos(esc, n_per_beat=6)
    seen = []

    def shorten(text, target):
        seen.append(target)
        return text[: max(50, target)]
    out, notes = md.rebalance(esc, ps, shorten=shorten)
    assert seen and any("acortó" in x for x in notes)


def test_cap_corto_es_aviso_y_no_inventa():
    esc = _esc()
    ps = [p for p in _parrafos(esc, n_per_beat=1)]
    out, notes = md.rebalance(esc, ps)
    assert any("corto" in x for x in notes) and len(out) == len(ps)


def test_titulos_con_respaldo():
    esc = _esc()
    good = lambda prompt, **kw: {"titulos": ["El agua", "La orden", "El viento", "La marea", "El techo", "El sol",
                                              "La lista"]}
    t, src = md.titles(esc, call=good)
    assert src == "flash" and t[0] == "El agua"
    bad = lambda prompt, **kw: {"titulos": ["Los 517 muertos", "x"] * 4}
    t2, src2 = md.titles(esc, call=bad)
    assert src2 == "respaldo" and t2[0] == "El agua negra en la"        # imagen sensorial recortada a 5 palabras
    boom = lambda prompt, **kw: (_ for _ in ()).throw(RuntimeError("sin red"))
    t3, src3 = md.titles(esc, call=boom)
    assert src3 == "respaldo" and len(t3) == 7 and all(t3)


def test_particionar_persiste_los_archivos(tmp_path, monkeypatch):
    monkeypatch.setattr(md, "STEPS_DIR", tmp_path)
    esc = _esc()
    r = md.particionar({"id": "t1"}, esc, _parrafos(esc), POOL, call_titles=lambda p, **k: {"titulos": []})
    for f in ("01a_skeleton.json", "01b_narration.json", "01b_narracion_v3.json"):
        assert (tmp_path / "t1" / f).exists()
    assert r["skeleton"]["_v3"]["particion"]["titulos"] == "respaldo"


# ═══════════════════════════════════════════════════════════════
#  fase1_5
# ═══════════════════════════════════════════════════════════════

def test_audio_script_v2_igual_y_v3_con_narration_tts():
    sk = {"chapters": [{"chapter_number": 1, "narrative_intent": "hook"}]}
    v2 = f15._build_audio_script("t", {"chapters": [{"chapter_number": 1, "narration": "Hola."}]}, sk)
    assert v2["chapters"][0] == {"id": "ch01", "text": "Hola.", "narrative_intent": "hook"}
    v3 = f15._build_audio_script("t", {"chapters": [{"chapter_number": 1, "narration": "Hola.",
                                                      "narration_tts": "Hola. [long pause]"}]}, sk)
    assert v3["chapters"][0]["narration_tts"] == "Hola. [long pause]" and v3["chapters"][0]["text"] == "Hola."


def test_cuando_corre_v3():
    assert not f15.is_v3_topic({"evidence_pool": {"datos": []}})
    assert f15.is_v3_topic({"evidence_pool": {"datos": []}}, flag=True)
    assert f15.is_v3_topic({"evidence_pool": {"datos": []}, "guion_version": 3})
    assert not f15.is_v3_topic({"guion_version": 3})                  # sin pool no hay v3


def test_sin_flag_corre_el_camino_viejo(monkeypatch):
    called = []
    monkeypatch.setattr(f15, "_load_topic_by_id", lambda tid: {"id": tid})
    monkeypatch.setattr(f15, "generate_skeleton", lambda t: called.append("m01a_skeleton") or {"chapters": []})
    monkeypatch.setattr(f15, "run_escaleta_v3", lambda tid, **kw: called.append("escaleta"))   # F22d: + columna=
    r = f15.process_topic("t", from_step="m01a", stop_after_step="m01a")
    assert r["status"] == "PASS" and called == ["m01a_skeleton"]
    called.clear()
    monkeypatch.setattr(f15, "_load_topic_by_id", lambda tid: {"id": tid, "evidence_pool": {"datos": []}})
    r = f15.process_topic("t", from_step="m01a", stop_after_step="m01a", v3=True)
    assert r["status"] == "PASS" and called == ["escaleta"]


def test_el_pool_v3_llega_al_topic():
    import topic_researcher as tr
    seed = {"seed_id": "s", "discovery_mode": "manual", "tags": []}
    data = {"_pre_topic_id": "t9", "video_title": "x", "evidence_pool": {"datos": [{"id": "D01"}]}, "research_version": 3}
    t = tr._enrich_with_seed_metadata(dict(data), seed)
    assert t["id"] == "t9" and t["evidence_pool"]["datos"][0]["id"] == "D01" and t["research_version"] == 3
    t2 = tr._enrich_with_seed_metadata({"video_title": "y"}, seed)
    assert "evidence_pool" not in t2 and "research_version" not in t2          # camino viejo: igual que antes


# ═══════════════════════════════════════════════════════════════
#  B1 — sin ventana del 100 % y validador de cuadro congelado
# ═══════════════════════════════════════════════════════════════

def test_ventana_del_100_por_ciento_se_corta():
    from script_engine import gfx_sparse as sp
    plan = {"callouts": [{"start": t, "duration": 2.0} for t in (1.0, 4.5, 8.0, 11.5, 15.0, 18.5)]}
    w = sp.event_windows(plan, [], 30, 21.0)
    assert len(w) > 1                                         # antes: 1 ventana de todo el cap
    assert sum(b - a for a, b in w) < 0.95 * 21.0
    plan2 = {"callouts": [{"start": 1.0, "duration": 2.0}, {"start": 12.0, "duration": 2.0}]}
    assert len(sp.event_windows(plan2, [], 30, 40.0)) == 2     # lo normal no cambia


def test_validador_de_cuadro_congelado(tmp_path):
    import subprocess
    from script_engine import freeze_check as fc
    mov = tmp_path / "mov.mp4"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "testsrc2=s=320x180:r=30:d=4",
                    "-f", "lavfi", "-i", "color=c=gray:s=320x180:r=30:d=3", "-filter_complex",
                    "[0:v][1:v]concat=n=2:v=1[v]", "-map", "[v]", str(mov)], check=True)
    r = fc.check(mov)
    assert not r["ok"] and abs(r["congelados"][0][0] - 4.0) < 0.3      # el gris quieto desde los 4 s
    assert fc.check(mov, allow=[(3.9, 7.1)])["ok"]                     # una pausa a propósito no cuenta


def test_cap_vacio_frena_la_cadena(tmp_path, monkeypatch):
    monkeypatch.setattr(md, "STEPS_DIR", tmp_path)
    esc = _esc()
    ps = [p for p in _parrafos(esc) if p["cap"] != 3]        # el guionista se salteó los beats del cap 3
    with pytest.raises(md.ParticionError):
        md.particionar({"id": "t2"}, esc, ps, POOL, call_titles=lambda p, **k: {"titulos": []})
    assert (tmp_path / "t2" / "01b_narration.json").exists()   # quedan escritos para leerlos
