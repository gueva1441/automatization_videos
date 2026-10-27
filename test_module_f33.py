"""
test_module_f33.py — F33: la compuerta del render (§B: aprobación del guion + hook guard_render) y el aviso del mapa
(§D.3: hook guard_mapa), sin red ni render.
"""
from __future__ import annotations

import importlib.util
import json
import os
import time
from pathlib import Path

from script_engine import aprobacion as ap

ROOT = Path(__file__).resolve().parent


def _hook(nombre: str):
    spec = importlib.util.spec_from_file_location(nombre, ROOT / ".claude" / "hooks" / f"{nombre}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GR = _hook("guard_render")


def _topic(tmp: Path, guion: bool = True) -> Path:
    t = tmp / "output" / "vajont"
    (t / "_fase2b_work").mkdir(parents=True)
    for c in ("ch01", "ch02"):
        (t / "_fase2b_work" / f"gfx_plan_{c}.resolved.json").write_text(json.dumps({"plan": {"cap": c}}), encoding="utf-8")
    if guion:
        time.sleep(0.02)
        (t / "GUION_PANTALLA.json").write_text(json.dumps({"version": "f32-1", "caps": []}), encoding="utf-8")
    return t


RENDER = "PYTHONIOENCODING=utf-8 python fase2b.py vajont --keep-segments --reuse-visuals --gfx --gfx-sparse --rotulista"


def test_sin_guion_o_sin_aprobacion_bloquea(tmp_path):
    t = _topic(tmp_path, guion=False)
    assert "no existe" in GR.revisar(RENDER, tmp_path / "output")
    (t / "GUION_PANTALLA.json").write_text("{}", encoding="utf-8")
    assert "no está aprobado" in GR.revisar(RENDER, tmp_path / "output")


def test_con_aprobacion_pasa_y_un_plan_edit_la_invalida(tmp_path):
    t = _topic(tmp_path)
    a = ap.aprobar(t, "Omar", "2026-10-27")
    assert a["por"] == "Omar" and a["md5_planes"] == ap.md5_planes(t) and len(a["planes"]) == 2
    assert GR.revisar(RENDER, tmp_path / "output") is None
    assert GR.revisar("python fase2b.py vajont --gfx --dry-run", tmp_path / "output") is None
    # --plan-edit / regeneración: cambia un plan → el md5 ya no coincide
    (t / "_fase2b_work" / "gfx_plan_ch02.resolved.json").write_text(json.dumps({"plan": {"cap": "ch02", "x": 1}}),
                                                                       encoding="utf-8")
    m = GR.revisar(RENDER, tmp_path / "output")
    assert m and "los planes cambiaron" in m
    # y regenerar el guion (--plan-only lo reescribe sin `aprobado`) también la invalida
    (t / "GUION_PANTALLA.json").write_text(json.dumps({"version": "f32-1", "caps": []}), encoding="utf-8")
    assert "no está aprobado" in GR.revisar(RENDER, tmp_path / "output")


def test_plan_only_y_lo_que_no_es_render_nunca_se_bloquea(tmp_path):
    _topic(tmp_path, guion=False)
    for cmd in ("python fase2b.py vajont --plan-only --rotulista",
                "python fase2b.py vajont --plan-edit ed.json",
                "python fase2b.py vajont --aprobar-guion \"Omar 2026-10-27\"",
                "python fase2b.py ba6c3cac --only-cap ch02 --reuse-visuals --sw-encode",      # el candado md5 de ch02
                "python fase2b.py vajont --only-cap ch06 --gfx --gfx-debug",
                "git commit -m 'fase2b --gfx'", "python otro.py vajont --gfx",
                "cat > f.txt <<'X'\n$ python fase2b.py vajont --gfx --dry-run\nX",        # un texto que lo menciona
                "echo python fase2b.py vajont --gfx"):
        assert GR.revisar(cmd, tmp_path / "output") is None, cmd


def test_dry_run_y_batch_con_gfx_se_bloquean(tmp_path):
    _topic(tmp_path)
    assert GR.revisar("python fase2b.py vajont --gfx --dry-run", tmp_path / "output")
    assert "modo batch" in GR.revisar("python fase2b.py --gfx --gfx-sparse", tmp_path / "output")
    assert GR.revisar("cd x && python -m fase2b vajont --only-cap ch06 --gfx", tmp_path / "output")
    # los prefijos no salvan al comando (el hueco que encontró el revisor de F33 en el primer arreglo de E)
    for pre in ("timeout 600 ", "nohup ", "time ", "cmd /c ", "env A=1 ", "start /b "):
        assert GR.revisar(f"{pre}python fase2b.py vajont --gfx", tmp_path / "output"), pre
    assert GR.revisar('bash -c "PYTHONIOENCODING=utf-8 python fase2b.py vajont --gfx"', tmp_path / "output")
    assert GR.revisar("cat > a.sh <<'X'\necho hola\nX\npython fase2b.py vajont --gfx", tmp_path / "output")
    assert GR.topic_de(["--hook", "Hola", "vajont", "--gfx"]) == "vajont"


def test_aprobar_falla_si_un_plan_es_mas_nuevo_que_el_guion(tmp_path):
    t = _topic(tmp_path)
    p = t / "_fase2b_work" / "gfx_plan_ch01.resolved.json"
    os.utime(p, (time.time() + 5, time.time() + 5))
    try:
        ap.aprobar(t, "Omar")
    except RuntimeError as e:
        assert "más nuevos que el guion" in str(e)
    else:
        raise AssertionError("aprobó un guion viejo")


def test_el_hook_esta_en_settings():
    s = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
    cmds = [h["command"] for x in s["hooks"]["PreToolUse"] for h in x["hooks"]]
    assert any("guard_render.py" in c for c in cmds)


# ═══════════════ §C.3: simular una regla en seco ═══════════════

def test_simular_regla_cuenta_por_cap_y_da_ejemplos():
    spec = importlib.util.spec_from_file_location("simular_regla", ROOT / "lab" / "tools" / "simular_regla.py")
    sr = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sr)
    ev = lambda cap, tipo, texto, voz, queda=True: {"cap": cap, "beat": 1, "tipo": tipo, "texto": texto, "voz_ancla": voz,
                                                   "queda": queda, "t_mp4": 10.0}
    guion = {"caps": [{"cap": "ch01", "eventos": [ev("ch01", "sello", "fuerza", "una fuerza espantosa"),
                                                 ev("ch01", "sello", "pánico", "la gente corrió"),
                                                 ev("ch01", "transición", "cut", ""),
                                                 ev("ch01", "sello", "ola", "la ola", queda=False)]},
                      {"cap": "ch02", "eventos": [ev("ch02", "ficha", "1.910", "murieron")]}]}
    regla = sr.cargar_regla("e['texto'].lower() in e['voz_ancla'].lower() and 'repite la voz'", None)
    r = sr.simular(guion, regla, tipos={"sello"})
    assert r["por_cap"] == {"ch01": [2, 1, 1], "ch02": [0, 0, 0]} and r["cortados"][0]["motivo_simulado"] == "repite la voz"
    assert sr.simular(guion, regla, tipos={"sello"}, sobre="todos")["por_cap"]["ch01"] == [3, 2, 1]
    t = sr.tabla("sello repite", r, "quedan")
    assert "**2 propuestos → 1 cortados por esta regla → 1 quedan**" in t and "sello «fuerza»" in t


# ═══════════════ §D.3: el aviso del mapa ═══════════════

def test_guard_mapa_avisa_si_tocan_gfx_sin_el_mapa():
    gm = _hook("guard_mapa")
    assert "guard_mapa" in gm.aviso(["script_engine/gfx_rotulista.py", "test_module_f33.py"])
    assert "fase2b.py" in gm.aviso(["fase2b.py"])
    assert gm.aviso(["script_engine/gfx_rotulista.py", "lab/MAPA_MODULOS.md"]) is None
    assert gm.aviso(["script_engine/aprobacion.py", "lab/ESTADO_SESION.md"]) is None
    s = json.loads((ROOT / ".claude" / "settings.json").read_text(encoding="utf-8"))
    assert any("guard_mapa.py" in h["command"] for x in s["hooks"]["PreToolUse"] for h in x["hooks"])


def test_el_mapa_cubre_los_modulos_y_trae_aristas():
    m = json.loads((ROOT / "lab" / "MAPA_MODULOS.json").read_text(encoding="utf-8"))
    nombres = {f["modulo"] for f in m["modulos"]}
    hay = {p.stem for p in (ROOT / "script_engine").glob("gfx_*.py")}
    assert hay <= nombres and {"fase2b", "gfx_config", "transition_config", "transition_applier", "m01a_escaleta",
                               "m01d_particion", "music_intensity", "title_card.html.tmpl"} <= nombres
    assert all(f["sticker"] and f["estado"] for f in m["modulos"])
    assert {"de": "gfx_layer", "a": "gfx_rotulista"} in [{k: a[k] for k in ("de", "a")} for a in m["aristas"]]
    # F36 §D: lo muerto se borró; no queda en el mapa ni como módulo ni como muerto
    assert not any("garantizar_pico" in x["que"] for x in m["muertos"])
    assert not {"gfx_bug", "gfx_fragments", "gfx_question", "gfx_identity", "rotulista_llm"} & nombres
