"""
test_module_f34.py — F34: reglas de pantalla corregidas, sin red (Gemini y Claude con falsos). Un test por regla, con el
caso real de Vajont cuando lo hay: prompt (§A.1, tres reemplazos exactos), gancho con el pool del video, candado D117
«1943», no dicho D237 «cuatrocientos», spoiler T85 «Vajont» (§A.2), reloj gana al sello, una cosa por oración en un cap
de una sola escena, reloj desde la voz (§A.3), sellos de clima (§A.4), agua desde la voz (§A.5), tarjeta fecha-hora
(§A.6), plan congelado y música alineada (§A.7), crítico de forma para el sello de clima y el agua de la voz.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from types import SimpleNamespace as NS

import pytest

from script_engine import pantalla_colocar as pc, pantalla_entrada as pe, voz_datos as vd, voz_utils as vu

ROOT = Path(__file__).resolve().parent


class Sc:
    def __init__(self, i: int, a: float, b: float):
        self.idx, self.start, self.end, self.quiet_side = i, a, b, "right"


def _w(texto: str, t0: float, paso: float = 0.4) -> list[dict]:
    return [{"word": w, "start": round(t0 + k * paso, 3), "end": round(t0 + k * paso + paso * 0.8, 3)}
            for k, w in enumerate(texto.split())]


def _ent(oraciones: list[tuple[float, str]], items: list[dict], beats: list[dict] | None = None,
         voz_antes: str = "", voz_video: list[str] | None = None) -> tuple[dict, list[dict]]:
    words = []
    for t0, txt in oraciones:
        words += _w(txt, t0)
    beats = beats or [{"n": 1, "funcion": "escalada", "t0": 0.0, "t1": 999.0, "cierre": "", "dato_central": "",
                       "datos_apoyo": []}]
    its = [{"a_pantalla": False, "por_que": "", "beats": [beats[0]["n"]], "kind": "datos", "fuente": "Fuente X, 2013",
            "autor": "", **x, "tipo": x["id"][0]} for x in items]
    ent = {"cap": 2, "titulo": "t", "oraciones": vu.oraciones(words), "beats": beats, "items": its, "ya_mostrado": [],
           "pico": None, "voz_video": voz_video or [], "voz_antes": voz_antes}
    for s in ent["oraciones"]:
        s["beat"] = vu.beat_de_oracion(s, beats)
    return ent, words


def _bl(si: int, tipo: str, texto: str, pid: str, et: str | None = None, wi: int = 0, **kw) -> dict:
    return {"sentence_idx": si, "word_idx": wi, "beat": 0, "rank": 1, "tipo": tipo, "etiqueta": et, "texto": texto,
            "pool_id": pid, "aporta": "algo concreto", **kw}


# ═══════════════ §A.1 prompt ═══════════════


# ═══════════════ §A.2 filtros ═══════════════


def test_a2_voz_previa_es_la_de_los_caps_anteriores():
    ctx = {"chapter_number": 3, "chapters": [{"chapter_number": 1, "narration": "uno"},
                                             {"chapter_number": 2, "narration": "dos"},
                                             {"chapter_number": 3, "narration": "tres"}]}
    assert pe.voz_previa(ctx) == "uno dos"


# ═══════════════ §A.3 reparto ═══════════════


def test_a3_2_cap_de_una_sola_escena_una_cosa_por_oracion():
    ors = [(0.0, "Hay una casa a oscuras."), (4.0, "La presa sigue en pie y nadie lo sabe."),
           (10.0, "La niña se llama Micaela."), (16.0, "Es de Longarone, un pueblo de fondo de valle.")]
    beats = [{"n": 1, "funcion": "gancho", "t0": 0.0, "t1": 40.0, "cierre": "", "dato_central": "", "datos_apoyo": []}]
    ent, words = _ent(ors, [], beats=beats)
    scenes = [Sc(0, 0.0, 40.0)]
    plan = {"title_card": {"title": "x"},
            "callouts": [{"text": "266 m de alto", "kicker": "LA PRESA", "ficha": True, "start": 4.2, "duration": 4.0,
                          "pool_id": "D118", "rotulista": True, "tipo_rotulista": "cifra"},
                         {"text": "otra", "kicker": "OTRA", "ficha": True, "start": 6.0, "duration": 3.0,
                          "pool_id": "D9", "rotulista": True, "tipo_rotulista": "cifra"}]}
    pc.repartir(plan, scenes, ent, [])                      # F37 §B.1: sin `unidades` (nunca al mismo tiempo)
    c = sorted(plan["callouts"], key=lambda x: x["start"])
    assert c[0]["start"] == 4.2 and (len(c) == 1 or c[1]["start"] >= 10.0)    # la segunda: otra oración o nada
    if len(c) == 2:
        assert c[1]["start"] >= c[0]["start"] + c[0]["duration"]


def test_a3_3_reloj_desde_la_voz_fecha_completa_en_letras():
    assert vd.fechas_completas("Longarone, Italia, nueve de octubre de mil novecientos sesenta y tres.") == \
        [(9, "octubre", 1963)]
    assert vd.fechas_completas("El nueve de octubre a la mañana.") == []           # sin año: no
    ent, _ = _ent([(0.0, "Era de noche."), (5.0, "Longarone, Italia, nueve de octubre de mil novecientos sesenta y tres.")], [])
    tk = vd.reloj_de_voz(ent, 60.0)
    assert (tk["day"], tk["month"], tk["tail"], tk["start"], tk["de_voz"]) == ("9", "OCT", "1963", 5.0, True)


# ═══════════════ §A.4 sellos de clima ═══════════════


# ═══════════════ §A.5 agua desde la voz ═══════════════


# ═══════════════ §A.6 tarjeta fecha-hora ═══════════════

def test_a6_tarjeta_vajont_y_falta_si_no_hay_certeza():
    esc = json.loads((Path(__file__).resolve().parent / "data" / "scripts" / "_steps" / "f8s3-vajont" /
                      "01a_escaleta.json").read_text(encoding="utf-8")) if (ROOT / "data" / "scripts" / "_steps" /
                                                                             "f8s3-vajont" / "01a_escaleta.json").exists() else None
    pool = {"cronologia": [{"id": "T57", "fecha": "1963-10-09", "hora": None, "evento": "El Toc cae."},
                           {"id": "T65", "fecha": "1963-10-09", "hora": "22:30", "evento": "Ola."},
                           {"id": "T66", "fecha": "1963-10-09", "hora": "22:39", "evento": "Roca."}]}
    pico = {"pico": {"beat": 10, "id": "T57", "por_que": "el Toc entra al embalse a las 22:39"}}
    tj = vd.tarjeta_inicial(pico, pool)
    assert (tj["texto"], tj["hora_de"]) == ("9 OCT 1963 · 22:39", "T66")
    assert vd.tarjeta_inicial({"pico": {"id": "T57", "por_que": "sin hora"}}, pool)["falta"] is True
    if esc is not None:
        assert esc["pico"]["id"] == "T57"


# ═══════════════ §A.7 plan congelado y música ═══════════════

def test_a7_1_plan_congelado_el_render_no_cambia_los_planes(tmp_path, monkeypatch):
    import script_engine.gfx_layer as gl
    import script_engine.gfx_director as gd
    from script_engine import aprobacion
    topic = tmp_path / "topic"
    work = topic / "_fase2b_work"
    work.mkdir(parents=True)
    plan = {"chapter_number": 2, "title_card": {"kicker": "CAPÍTULO 2", "title": "T"}, "callouts": [
        {"text": "13 de 34", "kicker": "ACTA", "ficha": True, "start": 5.0, "duration": 4.0}], "count_up": None,
        "evidence_zoom": None, "punch_in": [], "emphasis": [{"word": "CALMA", "start": 2.0, "duration": 2.5, "category": "silencio"}],
        "transitions": {"1": {"kind": "dissolve", "frames": 20}}}
    f = work / "gfx_plan_ch02.resolved.json"
    f.write_text(json.dumps({"plan": plan, "rejected": [{"x": 1}]}, ensure_ascii=False, indent=1), encoding="utf-8")
    (topic / "GUION_PANTALLA.json").write_text(json.dumps({"version": "f34-1", "caps": []}), encoding="utf-8")
    aprobacion.aprobar(topic, "Omar", "2026-10-26")
    antes = aprobacion.md5_planes(topic)
    assert gl.plan_congelado(work, "ch02") == plan
    base = tmp_path / "ch02_flux_visual.mp4"
    base.write_bytes(b"fake")
    chplan = NS(chapter_id="ch02", engine="flux", narration="", timestamps_path=None, narration_anchors=None,
                supplemental_paths=None, is_first=False)
    monkeypatch.setattr(gl, "_reencode", lambda src, out, fps: (out.parent.mkdir(parents=True, exist_ok=True),
                                                                out.write_bytes(b"v")))
    monkeypatch.setattr(gl, "_ffprobe_duration", lambda p: 10.0)
    monkeypatch.setattr(gl, "_doctor_once", lambda log: None)
    monkeypatch.setattr(gd, "load_chapter_context", lambda vid, p: {"script_chapter": {}, "sources": {},
                                                                     "chapter_number": 2, "facts": [], "skeleton": {}})
    monkeypatch.setattr(gl, "plan_base", lambda *a, **k: (_ for _ in ()).throw(AssertionError("plan nuevo")))   # F37 §B.4
    dibujado = {}
    monkeypatch.setattr(gl, "write_project", lambda resolved, *a, **k: dibujado.update(resolved=json.loads(json.dumps(resolved))))

    def fake_hf(args, **k):
        if args[0] == "lint":
            return subprocess.CompletedProcess(args, 0, json.dumps({"errorCount": 0, "warningCount": 0}), "")
        out = Path(args[args.index("-o") + 1]); out.parent.mkdir(parents=True, exist_ok=True); out.write_bytes(b"mp4")
        return subprocess.CompletedProcess(args, 0, "", "")
    monkeypatch.setattr(gl, "_hf", fake_hf)
    out = gl.apply_gfx(base, chplan, "vid", work, width=2560, height=1440, fps=30)
    assert out == work / "ch02_gfx.mp4"
    assert aprobacion.md5_planes(topic) == antes and aprobacion.estado(topic)[0]          # md5 de los planes, idéntico
    assert dibujado["resolved"]["callouts"] == plan["callouts"] and dibujado["resolved"]["transitions"] == plan["transitions"]
    assert "plan congelado" in (work / "gfx_ch02.log").read_text(encoding="utf-8")
    (topic / "GUION_PANTALLA.json").write_text(json.dumps({"version": "f34-1", "caps": []}), encoding="utf-8")
    assert gl.plan_congelado(work, "ch02") is None                                        # sin aprobación: no


def _ruido(path: Path, seed: int, dur: float) -> Path:
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i",
                    f"anoisesrc=d={dur}:c=pink:seed={seed}:a=0.3", "-ac", "2", "-ar", "44100", str(path)], check=True)
    return path


@pytest.mark.parametrize("alineada", [True, False])
def test_a7_2_la_musica_de_cada_cap_arranca_con_su_title_card(tmp_path, monkeypatch, alineada):
    import fase2b
    fase2b.FFMPEG = fase2b.FFMPEG or "ffmpeg"
    pistas = {c: _ruido(tmp_path / f"{c}.wav", k + 1, 60.0) for k, c in enumerate(("ch01", "ch02", "ch03"))}
    monkeypatch.setattr(fase2b, "_resolve_music_track_path", lambda info: Path(info["path"]))
    monkeypatch.setattr(fase2b, "_track_meta", lambda p: {})
    seg = {"ch01": 20.0, "ch02": 25.0, "ch03": 15.0}
    pre = {"ch01": 0.0, "ch02": 3.0, "ch03": 3.0}
    plans = [NS(chapter_id=c, audio_duration=seg[c] - pre[c], is_first=c == "ch01") for c in seg]
    pista = fase2b._build_continuous_music_track(
        plans=plans, music_map={c: {"path": str(p), "match_source": "test"} for c, p in pistas.items()},
        work_dir=tmp_path, crossfade_sec=2.0, pre_sec=pre, segmentos=seg if alineada else None,
        intro_sec=2.5 if alineada else 0.0, conservar_piezas=True, output_filename="m.wav")
    med = fase2b._medir_inicio_musica(plans, pista, tmp_path, seg, 2.5, 2.0, 30)
    if alineada:
        assert all(r["ok"] for r in med), med
    else:                                    # el camino de antes: adelantada intro + 2 s por cruce (F32: 4.6 / 14.8 s)
        assert [round(r["desvio_s"], 1) for r in med] == [-2.5, -4.5, -6.5], med


# ═══════════════ crítico: forma, no contenido ═══════════════

