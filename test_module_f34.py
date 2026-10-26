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

from script_engine import gfx_rotulista as gro

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
    ent = {"cap": 2, "titulo": "t", "oraciones": gro.oraciones(words), "beats": beats, "items": its, "ya_mostrado": [],
           "pico": None, "voz_video": voz_video or [], "voz_antes": voz_antes}
    for s in ent["oraciones"]:
        s["beat"] = gro.beat_de_oracion(s, beats)
    return ent, words


def _bl(si: int, tipo: str, texto: str, pid: str, et: str | None = None, wi: int = 0, **kw) -> dict:
    return {"sentence_idx": si, "word_idx": wi, "beat": 0, "rank": 1, "tipo": tipo, "etiqueta": et, "texto": texto,
            "pool_id": pid, "aporta": "algo concreto", **kw}


# ═══════════════ §A.1 prompt ═══════════════

def test_a1_prompt_tres_reemplazos_exactos_y_el_resto_igual():
    md = (ROOT / "lab" / "hyperframes" / "f34" / "HANDOFF_F34_reglas_de_pantalla.md").read_text(encoding="utf-8")
    for viejo, nuevo in gro.A1_SYSTEM[:2]:                 # los dos primeros, literales del handoff
        assert f"`{viejo}`" in md and f"`{nuevo}`" in md
        assert nuevo in gro.ROTULISTA_SYSTEM and viejo not in gro.ROTULISTA_SYSTEM
    assert "`, y si es cifra también unidad y valor`" in md and '`"unidad": str|null, "valor": number|null`' in md
    assert "`pool_id`, y si es cifra también unidad y valor y una línea `aporta`" in gro.ROTULISTA_SYSTEM
    assert '"pool_id": str, "unidad": str|null, "valor": number|null, "aporta": str}' in gro.ROTULISTA_USER
    # deshechos los tres reemplazos, es el de F32 byte a byte
    assert hashlib.md5((gro.ROTULISTA_SYSTEM_F32 + "\n\n" + gro.ROTULISTA_USER_F32).encode("utf-8")).hexdigest() == \
        "c9231e24afbc785d5870b33088ce076e"
    assert gro.prompt_md5() == "d90ae69a2dc8c7928bd410ead421dc6b" and gro.PROMPT_VERSION == "f34-1"


def test_a1_gancho_trae_el_pool_del_video_marcado_y_descarta_lo_que_dice_la_voz():
    pool = {"datos": [{"id": "D118", "texto": "La presa más alta del mundo, con 266 metros de altura.", "tipo": "cifra",
                       "valor": "266 metros", "fuente": "Tragedia della diga del Vajont, 2018"},
                      {"id": "D128", "texto": "En el desastre murieron 1.910 personas.", "tipo": "cifra",
                       "valor": "1.910", "fuente": "F"}]}
    beats = [{"n": 1, "funcion": "gancho", "t0": 0.0, "t1": 999.0, "cierre": "", "dato_central": "", "datos_apoyo": []}]
    voz = ["Una niña siente que su cama empieza a correr.", "Murieron mil novecientas diez personas."]
    its = gro.items_gancho(beats, pool, set(), voz)
    assert {x["id"]: x["dice_voz"] for x in its} == {"D118": False, "D128": True}
    assert all(x["gancho"] and x["beats"] == [1] for x in its)
    ent, words = _ent([(0.0, "Una niña siente que su cama empieza a correr."),
                       (4.0, "La presa que todos creyeron caída sigue en pie.")], [], beats=beats, voz_video=voz)
    ent["items"] = its
    u = gro.prompt_user(ent)
    assert "D118 · tipo D · a_pantalla: no · por_que: — · solo para el gancho · la narración lo dice en el video: no" in u
    v = gro.validar({"bloques": [_bl(1, "cifra", "266 m de alto", "D118", et="LA PRESA DEL VAJONT"),
                                 _bl(0, "cifra", "1.910 personas", "D128", et="MUERTOS")]}, ent, words)
    assert [b["pool_id"] for b in v["bloques"]] == ["D118"]
    assert any(r["pool_id"] == "D128" and r["regla"] == "no_dicho" for r in v["rechazos"])


# ═══════════════ §A.2 filtros ═══════════════

def test_a2_1_candado_d117_el_anio_que_dice_la_oracion_ancla_cuenta():
    item = {"id": "D117", "a_pantalla": True, "texto": "El Consejo Superior de Obras Públicas aprobó el proyecto de la "
            "presa mediante un procedimiento irregular, con solo 13 de 34 representantes presentes.",
            "fuente": "Tragedia della diga del Vajont: 9 ottobre 1963, 2018"}
    ent, words = _ent([(0.0, "En mil novecientos cuarenta y tres el Consejo aprobó la obra.")], [item])
    b = _bl(0, "cifra", "13 de 34 representantes presentes", "D117", et="ACTA DEL CONSEJO SUPERIOR, 1943")
    v = gro.validar({"bloques": [b]}, ent, words)
    assert [x["pool_id"] for x in v["bloques"]] == ["D117"]
    ent2, words2 = _ent([(0.0, "El Consejo aprobó la obra.")], [item])          # sin el año en la voz: candado
    v2 = gro.validar({"bloques": [b]}, ent2, words2)
    assert v2["rechazos"][0]["regla"] == "candado" and "1943" in v2["rechazos"][0]["motivo"]


def test_a2_2_no_dicho_d237_cuatrocientos_cae_por_repetir_y_no_por_lectura():
    item = {"id": "D237", "texto": "En la construcción de la represa trabajaron cerca de 400 operarios.",
            "fuente": "Tragedia della diga del Vajont: 9 ottobre 1963, 2018"}
    ent, words = _ent([(0.0, "Cuando empezaron las obras, unos cuatrocientos hombres colgados de andamios la fueron "
                             "levantando.")], [item])
    largo = "Para la construcción de la presa se contrató a cerca de cuatrocientos operarios."
    v = gro.validar({"bloques": [_bl(0, "cifra", largo, "D237", et="Tragedia della diga del Vajont, 2018")]}, ent, words,
                    escenas=[Sc(0, 0.0, 3.0), Sc(1, 3.0, 30.0)])
    assert v["rechazos"][0]["regla"] == "no_dicho" and "400" in v["rechazos"][0]["motivo"]


def test_a2_3_spoiler_t85_vajont_dicho_en_un_cap_anterior_no_es_spoiler():
    item = {"id": "T85", "texto": "Se presenta la sentencia de remisión a juicio contra 11 personas por el desastre del "
            "Vajont.", "fuente": "Vajont: fu disastro colposo (Cassazione 1971), 2003"}
    ors = [(0.0, "El juez firmó la remisión a juicio."), (6.0, "El país esperó años."), (12.0, "Nadie olvidó el Vajont.")]
    b = _bl(0, "hecho", "11 imputados por el desastre del Vajont", "T85", et="REMISIÓN A JUICIO")
    ent, words = _ent(ors, [item])
    assert gro.validar({"bloques": [b]}, ent, words)["rechazos"][0]["regla"] == "spoiler"
    ent2, words2 = _ent(ors, [item], voz_antes="La presa del Vajont era la más alta del mundo.")
    assert [x["pool_id"] for x in gro.validar({"bloques": [b]}, ent2, words2)["bloques"]] == ["T85"]


def test_a2_voz_previa_es_la_de_los_caps_anteriores():
    ctx = {"chapter_number": 3, "chapters": [{"chapter_number": 1, "narration": "uno"},
                                             {"chapter_number": 2, "narration": "dos"},
                                             {"chapter_number": 3, "narration": "tres"}]}
    assert gro.voz_previa(ctx) == "uno dos"


# ═══════════════ §A.3 reparto ═══════════════

def test_a3_1_el_reloj_gana_al_sello_del_pico():
    beats = [{"n": 12, "funcion": "revelacion", "t0": 0.0, "t1": 30.0, "cierre": "", "dato_central": "", "datos_apoyo": []}]
    ent, words = _ent([(0.0, "Hubo un grito en el valle."), (8.0, "La causa llegó al juez el veinte de febrero de mil "
                                                                "novecientos sesenta y ocho."), (20.0, "Nadie habló.")], [],
                      beats=beats)
    scenes = [Sc(0, 0.0, 8.0), Sc(1, 8.0, 20.0), Sc(2, 20.0, 30.0)]
    plan = {"pico": {"word": "grito"}, "emphasis": [{"word": "grito", "start": 8.5, "duration": 2.5, "peak_word": True}],
            "time_ticker": {"day": "20", "month": "FEB", "start": 8.2, "duration": 6.0, "changes": []}}
    filas = gro.escena_final(plan, scenes, ent, [])
    assert plan["time_ticker"] is not None and not any(f.get("bloque") == "time_ticker" for f in filas)
    gro.sellos_por_tema(plan, scenes, ent, words, 0.0, {"caos_gritos": {"layer": "minima", "triggers": {"grito": 3}}},
                        [], call=lambda p: "MEMORIA")
    sellos = plan["emphasis"]
    assert all(not (1 == next(s.idx for s in scenes if s.start <= e["start"] < s.end)) for e in sellos)
    assert any("ya tiene reloj" in f["motivo"] for f in plan["sellos_tema"])


def test_a3_2_cap_de_una_sola_escena_una_cosa_por_oracion():
    ors = [(0.0, "Hay una casa a oscuras."), (4.0, "La presa sigue en pie y nadie lo sabe."),
           (10.0, "La niña se llama Micaela."), (16.0, "Es de Longarone, un pueblo de fondo de valle.")]
    beats = [{"n": 1, "funcion": "gancho", "t0": 0.0, "t1": 40.0, "cierre": "", "dato_central": "", "datos_apoyo": []}]
    ent, words = _ent(ors, [], beats=beats)
    scenes = [Sc(0, 0.0, 40.0)]
    us = gro.unidades(scenes, ent)
    assert [(u.idx, u.start, u.end) for u in us] == [(0, 0.0, 4.0), (1, 4.0, 10.0), (2, 10.0, 16.0), (3, 16.0, 40.0)]
    plan = {"title_card": {"title": "x"},
            "callouts": [{"text": "266 m de alto", "kicker": "LA PRESA", "ficha": True, "start": 4.2, "duration": 4.0,
                          "pool_id": "D118", "rotulista": True, "tipo_rotulista": "cifra"},
                         {"text": "otra", "kicker": "OTRA", "ficha": True, "start": 6.0, "duration": 3.0,
                          "pool_id": "D9", "rotulista": True, "tipo_rotulista": "cifra"}]}
    gro.escena_final(plan, scenes, ent, [])
    c = sorted(plan["callouts"], key=lambda x: x["start"])
    assert c[0]["start"] == 4.2 and (len(c) == 1 or c[1]["start"] >= 10.0)    # la segunda: otra oración o nada
    if len(c) == 2:
        assert c[1]["start"] >= c[0]["start"] + c[0]["duration"]


def test_a3_3_reloj_desde_la_voz_fecha_completa_en_letras():
    assert gro.fechas_completas("Longarone, Italia, nueve de octubre de mil novecientos sesenta y tres.") == \
        [(9, "octubre", 1963)]
    assert gro.fechas_completas("El nueve de octubre a la mañana.") == []           # sin año: no
    ent, _ = _ent([(0.0, "Era de noche."), (5.0, "Longarone, Italia, nueve de octubre de mil novecientos sesenta y tres.")], [])
    tk = gro.reloj_de_voz(ent, 60.0)
    assert (tk["day"], tk["month"], tk["tail"], tk["start"], tk["de_voz"]) == ("9", "OCT", "1963", 5.0, True)


# ═══════════════ §A.4 sellos de clima ═══════════════

def test_a4_prompt_literal_y_filtros_de_la_palabra():
    md = (ROOT / "lab" / "hyperframes" / "f34" / "HANDOFF_F34_reglas_de_pantalla.md").read_text(encoding="utf-8")
    assert "```\n" + gro.SELLO_CLIMA_PROMPT + "\n```" in md
    lista = gro.vocabulario_clima()
    assert lista == ["PÁNICO", "CALMA", "AMENAZA", "AVISO", "ALARMA", "INMINENTE", "COLAPSO", "SILENCIO", "RABIA", "MEMORIA"]
    p = gro.prompt_clima(lista, "a", "b", "c", "pico")
    assert p.startswith("Elegí UNA palabra de esta lista") and "PÁNICO, CALMA" in p and "«a» «b» «c»" in p
    assert gro.palabra_clima("Pánico.", lista, ["", "", ""]) == ("PÁNICO", None)
    assert gro.palabra_clima("TERROR", lista, ["", "", ""])[0] is None
    assert gro.palabra_clima("AVISO", lista, ["", "llegaron los avisos", ""])[0] is None       # por su raíz
    assert gro.palabra_clima("NINGUNA", lista, ["", "", ""])[0] is None


def test_a4_un_sello_por_beat_sin_repetir_palabra_y_sin_vocabulario_no_hay(monkeypatch):
    beats = [{"n": 1, "funcion": "planteo", "t0": 0.0, "t1": 9.9, "cierre": "", "dato_central": "", "datos_apoyo": []},
             {"n": 2, "funcion": "escalada", "t0": 10.0, "t1": 30.0, "cierre": "", "dato_central": "", "datos_apoyo": []}]
    ent, words = _ent([(0.0, "Los cadáveres flotaban."), (10.0, "Murieron los técnicos."),
                       (20.0, "Los cuerpos quedaron en el barro.")], [], beats=beats)
    moods = {"muerte": {"layer": "muerte", "triggers": {"cadáveres": 3, "murieron": 2, "cuerpos": 3}}}
    scenes = [Sc(0, 0.0, 10.0), Sc(1, 10.0, 20.0), Sc(2, 20.0, 30.0)]
    llamadas: list[str] = []
    plan: dict = {"emphasis": []}
    gro.sellos_por_tema(plan, scenes, ent, words, 0.0, moods, [], call=lambda p: llamadas.append(p) or "SILENCIO")
    assert [e["word"] for e in plan["emphasis"]] == ["SILENCIO"] and len(llamadas) == 3
    mot = [f["motivo"] for f in plan["sellos_tema"]]
    assert any("ya salió en el cap" in m for m in mot) or any("un sello por beat" in m for m in mot)
    from script_engine import clima                  # F36 §A: sellos_por_tema vive en clima (gro lo re-exporta)
    monkeypatch.setattr(clima, "vocabulario_clima", lambda: [])
    plan2: dict = {"emphasis": []}
    gro.sellos_por_tema(plan2, scenes, ent, words, 0.0, moods, [], call=lambda p: "SILENCIO")
    assert plan2["emphasis"] == [] and all("sin vocabulario" in f["motivo"] for f in plan2["sellos_tema"])


def test_a4_cache_por_prompt(tmp_path):
    n = []
    out = gro.elegir_clima(["p1", "p2"], tmp_path / "c.json", call=lambda p: n.append(p) or "CALMA")
    out2 = gro.elegir_clima(["p1", "p2"], tmp_path / "c.json", call=lambda p: n.append(p) or "RABIA")
    assert out == out2 == ["CALMA", "CALMA"] and len(n) == 2


# ═══════════════ §A.5 agua desde la voz ═══════════════

def test_a5_agua_desde_la_voz_cota_antes_que_nivel_y_sin_falsos():
    ent, _ = _ent([(0.0, "El embalse estaba a setecientos metros sobre el nivel del mar."),
                   (6.0, "La cota autorizada fue de setecientos quince."),
                   (12.0, "La ola la arrastra cuatrocientos metros."),
                   (18.0, "Cayeron setecientos mil metros cúbicos.")], [])
    plan: dict = {}
    wl = gro.agua_de_voz(plan, ent, [])
    assert (wl["etiqueta"], wl["value_text"], wl["start"], wl["de_voz"]) == ("COTA AUTORIZADA", "715", 6.0, True)
    assert gro._agua_de("Una ola de veinte metros.", "") == ("OLA", 20.0, "20")
    assert gro._agua_de("La ola la arrastra cuatrocientos metros.", "") is None
    assert gro._agua_de("Una ola de veinte años.", "") is None
    assert gro.agua_de_voz({"water_level": {"x": 1}}, ent, []) is None             # no pisa el del rotulista


# ═══════════════ §A.6 tarjeta fecha-hora ═══════════════

def test_a6_tarjeta_vajont_y_falta_si_no_hay_certeza():
    esc = json.loads((Path(__file__).resolve().parent / "data" / "scripts" / "_steps" / "f8s3-vajont" /
                      "01a_escaleta.json").read_text(encoding="utf-8")) if (ROOT / "data" / "scripts" / "_steps" /
                                                                             "f8s3-vajont" / "01a_escaleta.json").exists() else None
    pool = {"cronologia": [{"id": "T57", "fecha": "1963-10-09", "hora": None, "evento": "El Toc cae."},
                           {"id": "T65", "fecha": "1963-10-09", "hora": "22:30", "evento": "Ola."},
                           {"id": "T66", "fecha": "1963-10-09", "hora": "22:39", "evento": "Roca."}]}
    pico = {"pico": {"beat": 10, "id": "T57", "por_que": "el Toc entra al embalse a las 22:39"}}
    tj = gro.tarjeta_inicial(pico, pool)
    assert (tj["texto"], tj["hora_de"]) == ("9 OCT 1963 · 22:39", "T66")
    assert gro.tarjeta_inicial({"pico": {"id": "T57", "por_que": "sin hora"}}, pool)["falta"] is True
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
    monkeypatch.setattr(gd, "select_gfx_plan", lambda *a, **k: (_ for _ in ()).throw(AssertionError("director")))
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

def test_critico_sello_de_clima_y_agua_de_voz_solo_salen_si_estorban(tmp_path):
    from script_engine import gfx_critic as gc
    plan = {"emphasis": [{"word": "PÁNICO", "start": 1.0, "duration": 2.5, "clima": True},
                         {"word": "agua", "start": 9.0, "duration": 2.5}],
            "water_level": {"start": 5.0, "duration": 4.5, "value_text": "715", "unit": "m", "height": 0.5,
                            "de_voz": True}}
    img = tmp_path / "f.jpg"
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "lavfi", "-i", "color=c=gray:s=64x36:d=12", str(tmp_path / "b.mp4")],
                   check=True)
    veredicto = {"PÁNICO": "repite", "715": "repite", "agua": "repite"}

    def call(im, prompt, *a, **k):
        for t, v in veredicto.items():
            if f"«{t}" in prompt or f"«{t.upper()}" in prompt:
                return {"veredicto": v, "motivo": "x"}
        return {"veredicto": "suma", "motivo": "x"}
    rows = gc.criticize(plan, base=tmp_path / "b.mp4", words=[], time_offset=0.0, work_dir=tmp_path, cap="ch01", log=[],
                        call=call, fewshot=[])
    assert [e["word"] for e in plan["emphasis"]] == ["PÁNICO"] and plan["water_level"] is not None
    assert img.parent.exists() and len(rows) == 3
