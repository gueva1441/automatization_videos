# -*- coding: utf-8 -*-
"""F60 Etapas B + C — madre por PERSONA + secuencia Seedream /edit por la cola de fal (HANDOFF_F60_BC_madre_secuencia_prod).

Sin red: todo lo que llama a fal está mockeado. Cubre: filtro por era (dentro / fuera / era ilegible / year vacío), regla
única de madres (persona + foto_madre_ref, tope 2), agrupación 7 → 6+1 y lote de 1 → una foto, lote incompleto → una foto,
`ok_secuencia` en el manifest y como donante del piso anti-desync, reanudar desde `request_id` guardado, `persona` en supps
y en la foto inicial de caps con clip, m06 (registry + foto_madre_personas + image_f8) y el adaptador de fase2a, la madre
de persona en foto_madre.py (prompt, ≥ 2 fotos, motor ≠ seedream, rechazo sin GPT), QA fix y reseed con persona, rename
`_clip_poll` → `_fal_queue_poll` y constantes con origen."""
from __future__ import annotations

import inspect
import json
from pathlib import Path

import pytest

import asset_manager as am
import foto_madre as fm

PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16
DANIEL = {"name": "Daniel Écija", "era": "1962-1963", "appearance_canon": "a mid-20s Spanish man",
          "condition_by_period": [{"years": "1962-1963", "condition": "His foot is bandaged."},
                                  {"years": "1991-1992", "condition": "He is terminally ill with mesothelioma."}]}
MARIA = {"name": "María Bernal", "era": "1962-1963", "appearance_canon": "a young adult Spanish woman",
         "condition_by_period": [{"years": "1963-1963", "condition": "weakened"}]}


def _dir(p: Path) -> Path:
    p.mkdir(parents=True, exist_ok=True)
    return p


def _madres(tmp_path: Path, *names: str) -> dict[str, str]:
    reg = {}
    for n in names:
        p = tmp_path / "foto_madre" / f"{fm._slug(n)}.png"
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(PNG)
        reg[n] = str(p)
    return reg


PERSONAS = {DANIEL["name"]: {"era": DANIEL["era"], "condition_by_period": DANIEL["condition_by_period"]},
            MARIA["name"]: {"era": MARIA["era"], "condition_by_period": MARIA["condition_by_period"]}}


# ── 1. filtro por era (Omar 20:29) ──────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("anio, esperado", [
    ("1962", True),            # dentro de la era
    ("1991", False),           # fuera de la era y dentro de condition 1991-1992 (fuera de la era) → no aporta
    ("1961", True),            # fuera de la era, en ningún condition → aporta (el baile de 1961)
    ("1966", True),            # fuera de la era, en ningún condition → aporta (Madrid 1966)
    ("c. 1992 (archivo)", False),   # el año es el primer número de 4 dígitos
    ("", True), (None, True),  # year vacío → aporta
    ("sin año", True),         # anio sin 4 dígitos → aporta
])
def test_filtro_por_era_daniel(anio, esperado):
    assert am.persona_aporta_madre(DANIEL, anio) is esperado


def test_filtro_por_era_ilegible_y_sin_canon_aportan():
    assert am.persona_aporta_madre({"era": "antes de la guerra", "condition_by_period": [{"years": "1991-1992", "condition": "x"}]}, "1991") is True
    assert am.persona_aporta_madre(None, "1991") is True
    assert am.persona_aporta_madre({}, "1991") is True
    # condition con años ilegibles → ese tramo no cuenta
    assert am.persona_aporta_madre({"era": "1962-1963", "condition_by_period": [{"years": "later", "condition": "x"}]}, "1991") is True


def test_filtro_por_era_condition_que_se_cruza_con_la_era_no_excluye():
    # el tramo 1963-1965 se cruza con la era 1962-1963 → no es «fuera de su era» → la foto de 1965 aporta
    p = {"era": "1962-1963", "condition_by_period": [{"years": "1963-1965", "condition": "x"}]}
    assert am.persona_aporta_madre(p, "1965") is True
    assert am.persona_aporta_madre({"era": "1962-1963", "condition_by_period": [{"years": "1964-1965", "condition": "x"}]}, "1965") is False


# ── 2. regla única de madres ────────────────────────────────────────────────────────────────────────────────────
def test_regla_unica_persona_primero_mas_foto_madre_ref_tope_2(tmp_path):
    reg = _madres(tmp_path, "Daniel Écija", "María Bernal", "__subject__")
    m = am._madres_para_item(["Daniel Écija", "María Bernal"], ["__subject__"], "1962", reg, PERSONAS)
    assert [r for r, _ in m] == ["Daniel Écija", "María Bernal"]          # principal primero, tope 2 → el objeto queda afuera
    m = am._madres_para_item(["María Bernal"], ["__subject__"], "1962", reg, PERSONAS)
    assert [r for r, _ in m] == ["María Bernal", "__subject__"]
    assert all(Path(p).exists() for _, p in m)
    m = am._madres_para_item([], ["__subject__", "__subject__"], "1962", reg, PERSONAS)
    assert [r for r, _ in m] == ["__subject__"]                            # sin repetir
    assert am._madres_para_item([], [], "1962", reg, PERSONAS) == []


def test_regla_unica_persona_sin_madre_o_fuera_de_era_no_entra(tmp_path):
    reg = _madres(tmp_path, "Daniel Écija", "__subject__")
    assert [r for r, _ in am._madres_para_item(["Daniel Écija"], ["__subject__"], "1991", reg, PERSONAS)] == ["__subject__"]
    assert [r for r, _ in am._madres_para_item(["Ramón de Juan"], [], "1962", reg, PERSONAS)] == []     # sin madre en el registry
    reg["Daniel Écija"] = str(tmp_path / "no_existe.png")
    assert am._madres_para_item(["Daniel Écija"], [], "1962", reg, PERSONAS) == []                      # el archivo no existe
    assert [r for r, _ in am._madres_para_item(["Daniel Écija"], [], "1991", _madres(tmp_path, "Daniel Écija"), None)] == ["Daniel Écija"]   # sin canon → aporta


# ── 3/4. pre-paso: agrupación, lote de 1, lote incompleto, fallo ────────────────────────────────────────────────
def _item(prompt, persona, anio="1962", refs=None, cartel=False):
    return {"prompt": prompt, "persona": persona, "anio": anio, "foto_madre_ref": refs or [],
            "text_in_image": {"present": cartel, "text": "", "font": "", "location": ""}}


def _cap(cid, items):
    return {"id": cid, "render_engine": "flux", "image_prompts": items}


def test_pre_paso_agrupa_7_en_6_mas_1_y_excluye_lo_que_no_entra(tmp_path, monkeypatch):
    monkeypatch.setattr(am, "OUTPUT_DIR", tmp_path)
    reg = _madres(tmp_path, "Daniel Écija", "María Bernal", "__subject__")
    lotes = []

    def fake(video_id, prompts, refs, madre_paths, out_paths):
        lotes.append((refs, list(prompts), [p.name for p in out_paths], madre_paths))
        for p in out_paths:
            p.write_bytes(PNG)
        return list(out_paths)
    monkeypatch.setattr(am, "_llamar_secuencia", fake)
    ch2 = _cap("ch02", [_item(f"d{i}", ["Daniel Écija"]) for i in range(1, 5)]
               + [_item("dos", ["Daniel Écija", "María Bernal"]),           # 2 personas → una foto
                  _item("cartel", ["Daniel Écija"], cartel=True),           # con cartel → una foto
                  _item("conref", ["Daniel Écija"], refs=["__subject__"]),  # con foto_madre_ref → una foto
                  _item("m1", ["María Bernal"])])                           # María: 1 sola foto → una foto
    ch4 = _cap("ch04", [_item(f"d{i}", ["Daniel Écija"]) for i in range(5, 8)]      # 7 de Daniel en total → 6 + 1
               + [_item("viejo", ["Daniel Écija"], anio="1991")])                    # fuera de era → no aporta → una foto
    (tmp_path / "v" / "assets" / "ch04_flux").mkdir(parents=True)
    (tmp_path / "v" / "assets" / "ch04_flux" / "ch04_img_02.png").write_bytes(PNG)   # d6 ya en disco → no entra
    res = am._pre_paso_secuencia([ch2, ch4], "v", reg, PERSONAS)
    assert len(lotes) == 1 and lotes[0][0] == ["Daniel Écija"] and lotes[0][3] == [reg["Daniel Écija"]]
    # orden de guion, lote de 6: d1..d4 (ch02) + d5, d7 (ch04; d6 ya existía) → el 7mo (no hay) y el resto van por una foto
    assert lotes[0][1] == ["d1", "d2", "d3", "d4", "d5", "d7"]
    assert set(res) == {("ch02", "img", 1), ("ch02", "img", 2), ("ch02", "img", 3), ("ch02", "img", 4), ("ch04", "img", 1), ("ch04", "img", 3)}
    r = res[("ch02", "img", 1)]
    assert r["status"] == "ok_secuencia" and r["persona"] == "Daniel Écija" and r["lote"] == "Daniel Écija#1" and r["foto_madre_refs"] == ["Daniel Écija"]


def test_pre_paso_7_fotos_son_6_mas_1_y_el_lote_de_1_va_por_una_foto(tmp_path, monkeypatch):
    monkeypatch.setattr(am, "OUTPUT_DIR", tmp_path)
    reg = _madres(tmp_path, "Daniel Écija")
    lotes = []

    def fake(video_id, prompts, refs, madre_paths, out_paths):
        lotes.append(len(prompts))
        for p in out_paths:
            p.write_bytes(PNG)
        return list(out_paths)
    monkeypatch.setattr(am, "_llamar_secuencia", fake)
    ch = _cap("ch02", [_item(f"d{i}", ["Daniel Écija"]) for i in range(1, 8)])
    res = am._pre_paso_secuencia([ch], "v", reg, PERSONAS)
    assert lotes == [am.FOTOS_POR_LLAMADA] == [6] and len(res) == 6 and ("ch02", "img", 7) not in res
    # dos fotos → UN lote de 2 (sí entra a secuencia); una foto → sin lote
    lotes.clear()
    assert len(am._pre_paso_secuencia([_cap("ch03", [_item("a", ["Daniel Écija"]), _item("b", ["Daniel Écija"])])], "v2", reg, PERSONAS)) == 2 and lotes == [2]
    lotes.clear()
    assert am._pre_paso_secuencia([_cap("ch03", [_item("a", ["Daniel Écija"])])], "v3", reg, PERSONAS) == {} and lotes == []


def test_pre_paso_lote_incompleto_y_lote_fallido_caen_a_una_foto(tmp_path, monkeypatch):
    monkeypatch.setattr(am, "OUTPUT_DIR", tmp_path)
    reg = _madres(tmp_path, "Daniel Écija", "María Bernal")

    def fake(video_id, prompts, refs, madre_paths, out_paths):
        if refs == ["María Bernal"]:
            raise RuntimeError("fal.ai tarea falló")
        for p in out_paths[:2]:                      # devolvió 2 de 3
            p.write_bytes(PNG)
        return list(out_paths[:2])
    monkeypatch.setattr(am, "_llamar_secuencia", fake)
    ch = _cap("ch02", [_item("d1", ["Daniel Écija"]), _item("d2", ["Daniel Écija"]), _item("d3", ["Daniel Écija"]),
                       _item("m1", ["María Bernal"]), _item("m2", ["María Bernal"])])
    res = am._pre_paso_secuencia([ch], "v", reg, PERSONAS)
    assert set(res) == {("ch02", "img", 1), ("ch02", "img", 2)}       # d3 (no devuelta) y María (lote fallido) → una foto


# ── 5. _process_flux_chapter: ok_secuencia en el manifest, piso anti-desync, regla única en el camino de una foto ──
def test_process_flux_chapter_ok_secuencia_dona_al_piso_y_una_foto_lleva_madres(tmp_path, monkeypatch):
    monkeypatch.setattr(am, "OUTPUT_DIR", tmp_path)
    reg = _madres(tmp_path, "Daniel Écija", "María Bernal", "__subject__")
    ch = _cap("ch02", [_item("sec", ["Daniel Écija"]), _item("falla", ["Daniel Écija"]),
                       _item("dos", ["María Bernal", "Daniel Écija"], refs=["__subject__"])])
    d = _dir(tmp_path / "v" / "assets" / "ch02_flux")
    (d / "ch02_img_01.png").write_bytes(PNG)
    secuencia = {("ch02", "img", 1): {"status": "ok_secuencia", "persona": "Daniel Écija", "lote": "Daniel Écija#1",
                                       "path": d / "ch02_img_01.png", "foto_madre_refs": ["Daniel Écija"], "segundos_lote": 12.5}}
    llamadas = []

    def gen(prompt, art_profile, out_path, use_ultra, seed=None, foto_madre_data_uris=None):
        llamadas.append((prompt, foto_madre_data_uris))
        if prompt == "falla":
            raise RuntimeError("timeout")
        out_path.write_bytes(PNG)
        return {"validated": None, "attempts": 1, "last_verdict": {}, "model_used": "flux_pro", "flux_meta": {}}
    monkeypatch.setattr(am, "_generate_flux_image_at", gen)
    monkeypatch.setattr(am, "_path_to_data_uri", lambda p: f"uri:{Path(p).name}")
    res = am._process_flux_chapter(ch, "v", reg, PERSONAS, secuencia)
    imgs = {i["index"]: i for i in res["images"]}
    assert imgs[1]["status"] == "ok_secuencia" and imgs[1]["lote"] == "Daniel Écija#1" and imgs[1]["foto_madre_refs"] == ["Daniel Écija"] and imgs[1]["persona"] == ["Daniel Écija"]
    assert imgs[2]["status"] == "neighbor_fallback" and imgs[2]["fallback_from"] == 1      # la secuencia donó al piso
    assert (d / "ch02_img_02.png").read_bytes() == PNG
    assert imgs[3]["status"] == "ok" and imgs[3]["foto_madre_refs"] == ["María Bernal", "Daniel Écija"]   # principal primero, tope 2
    assert sorted(p for p, _ in llamadas) == ["dos", "falla"]                                        # la de secuencia NO se pidió
    assert dict(llamadas)["dos"] == ["uri:mar_a_bernal.png", "uri:daniel_cija.png"]


# ── 6. _llamar_secuencia: pedido guardado ANTES de esperar, reanudar sin re-pedir, N en el costo ─────────────────
class _Resp:
    def __init__(self, js=None, content=b"", status=200):
        self._js, self.content, self.status_code, self.text = js, content, status, json.dumps(js or {})

    def json(self):
        return self._js

    def raise_for_status(self):
        pass


def test_llamar_secuencia_guarda_el_pedido_antes_de_esperar_y_registra_n(tmp_path, monkeypatch):
    monkeypatch.setattr(am, "OUTPUT_DIR", tmp_path)
    reg = _madres(tmp_path, "Daniel Écija")
    monkeypatch.setattr(am, "_path_to_data_uri", lambda p: "data:x")
    posts, costos = [], []

    def post(url, headers=None, json=None, timeout=None):
        posts.append((url, json, timeout))
        return _Resp({"request_id": "rq1", "status_url": "S", "response_url": "R"})

    def poll(status_url, response_url, timeout=None):
        ped = json.loads((tmp_path / "v" / am.SECUENCIA_DIR / "pedidos.json").read_text(encoding="utf-8"))
        assert [p["request_id"] for p in ped.values()] == ["rq1"]            # en disco ANTES de esperar
        return {"images": [{"url": "u1"}, {"url": "u2"}], "seed": 7}
    monkeypatch.setattr(am.requests, "post", post)
    monkeypatch.setattr(am.requests, "get", lambda url, timeout=None: _Resp(content=PNG + url.encode()))
    monkeypatch.setattr(am, "_fal_queue_poll", poll)
    monkeypatch.setattr(am.cost_tracker, "track_seedream", lambda description, images=1, mode="t2i": costos.append((images, mode)))
    outs = [tmp_path / "v" / "assets" / "ch02_flux" / f"ch02_img_0{i}.png" for i in (1, 2, 3)]
    escritos = am._llamar_secuencia("v", ["p1", "p2", "p3"], ["Daniel Écija"], [reg["Daniel Écija"]], outs)
    assert escritos == outs[:2] and outs[0].exists() and not outs[2].exists()         # devolvió 2 de 3
    assert costos == [(2, "edit")]                                                    # N devueltas en el costo, modo edit
    url, payload, timeout = posts[0]
    assert url.endswith("/edit") and "queue.fal.run" in url and timeout == am.FAL_SUBMIT_TIMEOUT_S == 60
    assert payload["max_images"] == 3 and payload["sequential_image_generation"] == "auto" and payload["num_images"] == 1
    assert payload["image_urls"] == ["data:x"] and payload["prompt"].startswith("A series of 3 separate photographs of the same person")
    assert "Image 1: p1\nImage 2: p2\nImage 3: p3\nEvery image: " in payload["prompt"]
    # reanudar: la misma clave ya tiene request_id → NO se vuelve a pedir
    monkeypatch.setattr(am.requests, "post", lambda *a, **k: pytest.fail("re-pidió un lote ya pedido"))
    monkeypatch.setattr(am, "_fal_queue_poll", lambda s, r, timeout=None: {"images": [{"url": "u1"}, {"url": "u2"}, {"url": "u3"}]})
    assert am._llamar_secuencia("v", ["p1", "p2", "p3"], ["Daniel Écija"], [reg["Daniel Écija"]], outs) == outs
    # ítems distintos → clave distinta → se pide de nuevo
    posts.clear()
    monkeypatch.setattr(am.requests, "post", post)
    am._llamar_secuencia("v", ["p1", "p2", "OTRO"], ["Daniel Écija"], [reg["Daniel Écija"]], outs)
    assert len(posts) == 1
    ped = json.loads((tmp_path / "v" / am.SECUENCIA_DIR / "pedidos.json").read_text(encoding="utf-8"))
    assert len(ped) == 2 and all(p["request_id"] == "rq1" for p in ped.values())


def test_prompt_secuencia_quita_aspecto_y_no_text_de_cada_escena():
    from engine_profiles import select_profile
    from script_engine import m03_imagenes_v3 as v3img
    asp = select_profile("seedream").aspect_ratio_text
    s = am._prompt_secuencia([f"Scene one. {asp} {v3img.NO_TEXT}", f"Scene two. {v3img.NO_TEXT}"])
    assert s.count(asp) == 1 and s.count(v3img.NO_TEXT) == 1
    assert "Image 1: Scene one.\nImage 2: Scene two.\n" in s and s.endswith(f"Every image: {asp} {v3img.NO_TEXT}")


# ── 7. supps de caps con clip (Etapa C) ────────────────────────────────────────────────────────────────────────
def test_supps_entran_a_secuencia_o_llevan_las_madres_de_persona(tmp_path, monkeypatch):
    monkeypatch.setattr(am, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(am, "_chapter_dir", lambda vid, cid, kind: _dir(tmp_path / f"{cid}_{kind}"))
    monkeypatch.setattr(am, "_path_to_data_uri", lambda p: f"uri:{Path(p).name}")
    reg = _madres(tmp_path, "Daniel Écija", "Maitland Parker")
    ch = {"id": "ch01", "render_engine": "veo", "supplemental_image_prompts": [
        {"prompt": "s1", "narration_anchor": "a1", "persona": ["Daniel Écija"], "anio": "1962"},
        {"prompt": "s2", "narration_anchor": "a2", "persona": ["Daniel Écija", "María Bernal"], "anio": "1962"},
        {"prompt": "s3", "narration_anchor": "a3", "persona": [], "anio": "1962"}]}
    sec = {("ch01", "supp", 1): {"status": "ok_secuencia", "persona": "Daniel Écija", "lote": "Daniel Écija#1",
                                  "path": tmp_path / "ch01_flux" / "ch01_supp_01.png", "foto_madre_refs": ["Daniel Écija"]}}
    (tmp_path / "ch01_flux").mkdir(exist_ok=True)
    (tmp_path / "ch01_flux" / "ch01_supp_01.png").write_bytes(PNG)
    vistos = []

    def gen(prompt, art_profile, out_path, use_ultra, seed=None, foto_madre_data_uris=None):
        vistos.append((prompt, foto_madre_data_uris))
        out_path.write_bytes(PNG)
    monkeypatch.setattr(am, "_generate_flux_image_at", gen)
    res = am._generate_supplementals_for_veo_chapter(ch, "v", "ch01", True, reg, PERSONAS, sec)
    assert [r["status"] for r in res] == ["ok_secuencia", "ok", "ok"]
    assert res[0]["lote"] == "Daniel Écija#1" and res[0]["persona"] == ["Daniel Écija"]
    assert res[1]["foto_madre_refs"] == ["Daniel Écija"] and res[2]["foto_madre_refs"] == []   # María sin madre en el registry
    assert vistos == [("s2", ["uri:daniel_cija.png"]), ("s3", None)]                            # s1 no se pidió
    # el pre-paso ve las supps de caps con clip (lista cruda): entra la de UNA persona que aporta, no las demás
    items = am._items_para_secuencia([ch], "v")
    assert [(i["clave"], i["persona"]) for i in items] == [(("ch01", "supp", 1), ["Daniel Écija"]),
                                                            (("ch01", "supp", 2), ["Daniel Écija", "María Bernal"]), (("ch01", "supp", 3), [])]


# ── 8. foto inicial del clip con la madre de image_f8 (Etapa C) ────────────────────────────────────────────────
def test_foto_inicial_del_clip_lleva_las_madres_de_image_f8(tmp_path, monkeypatch):
    monkeypatch.setattr(am, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(am, "_chapter_dir", lambda vid, cid, kind: _dir(tmp_path / kind))
    monkeypatch.setattr(am, "_path_to_data_uri", lambda p: f"uri:{Path(p).name}")
    monkeypatch.setattr(am, "_generate_supplementals_for_veo_chapter", lambda *a: [])
    monkeypatch.setattr(am, "foto_final_del_clip", lambda *a, **k: {"path": None, "ssim": None, "instruccion": "i", "motivo": "x"})
    reg = _madres(tmp_path, "Daniel Écija")
    visto = {}

    def gen(prompt, art_profile, out_path, use_ultra, seed=None, foto_madre_data_uris=None):
        visto["uris"] = foto_madre_data_uris
        out_path.write_bytes(PNG)

    def clip(foto, mov, out, *, image_prompt="", ancla="", foto_final=None, log=None):
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_bytes(b"mp4")
        return out
    monkeypatch.setattr(am, "_generate_flux_image_at", gen)
    monkeypatch.setattr(am, "_generate_clip", clip)
    ch = {"id": "ch01", "video_prompts": ["mov"], "image_prompts": ["ip"], "voz_clip": "voz", "art_profile": "",
          "image_f8": {"persona": ["Daniel Écija"], "anio": "1962", "people_group": ["spanish_migrant_families"]}}
    res = am._process_veo_chapter(ch, "v", reg, PERSONAS, {})
    assert visto["uris"] == ["uri:daniel_cija.png"] and res["clips"][0]["status"] == "ok"
    # Daniel en 1991 → la foto del clip NO lleva su madre (filtro por era); sin image_f8 → sin madres (como antes)
    visto.clear()
    (tmp_path / "veo" / "ch01_img_01.png").unlink()
    (tmp_path / "veo" / "ch01_clip_01.mp4").unlink()
    am._process_veo_chapter({**ch, "image_f8": {"persona": ["Daniel Écija"], "anio": "1991"}}, "v", reg, PERSONAS, {})
    assert visto["uris"] is None
    visto.clear()
    (tmp_path / "veo" / "ch01_img_01.png").unlink()
    (tmp_path / "veo" / "ch01_clip_01.mp4").unlink()
    am._process_veo_chapter({k: v for k, v in ch.items() if k != "image_f8"}, "v", reg, PERSONAS, {})
    assert visto["uris"] is None


# ── 9. m06: registry por persona + foto_madre_personas + image_f8; adaptador de fase2a ─────────────────────────
def test_m06_registry_personas_image_f8_y_adaptador_fase2a(tmp_path, monkeypatch):
    from script_engine import m06_assembler as m6
    import fase2a
    madre = tmp_path / "daniel.png"
    madre.write_bytes(PNG)
    topic = {"id": "t", "central_subject": {"kind": "place", "foto_madre": ""},
             "documented_props": [{"nombre": "pala", "anclado": "si", "foto_madre": str(tmp_path / "pala.png")}],
             "documented_people": [{**DANIEL, "foto_madre": str(madre)}, {**MARIA, "foto_madre": ""}, {"name": "", "foto_madre": "x"}]}
    f8 = {"persona": ["Daniel Écija"], "anio": "1962", "beat": 1}
    visual = {"chapters": [
        {"chapter_number": 1, "image_prompt": "ip", "video_prompt": "vp", "voz_clip": "v", "narration_anchor": "a",
         "supplemental_image_prompts": [{"prompt": "s", "persona": ["Daniel Écija"], "anio": "1962"}], "image_f8": f8},
        {"chapter_number": 2, "image_prompts": [{"prompt": "p", "persona": ["Daniel Écija"], "anio": "1962"}]},
        {"chapter_number": 7, "image_prompt": "ip7", "video_prompt": "vp7", "voz_clip": "v7", "supplemental_image_prompts": []}]}
    monkeypatch.setattr(m6, "_load_topic", lambda tid: topic)
    monkeypatch.setattr(m6, "_load_step", lambda tid, f: visual if f == "03_visual.json" else {"chapters": []})
    monkeypatch.setattr(m6, "SCRIPTS_DIR", tmp_path / "scripts")
    out = json.loads(m6.assemble_final_script("t").read_text(encoding="utf-8"))
    assert out["foto_madre_registry"] == {"pala": str(tmp_path / "pala.png"), "Daniel Écija": str(madre)}   # María sin madre no entra
    assert out["foto_madre_personas"] == {"Daniel Écija": {"era": "1962-1963", "condition_by_period": DANIEL["condition_by_period"]}}
    caps = {c["chapter_number"]: c for c in out["chapters"]}
    assert caps[1]["image_f8"] == f8 and "image_f8" not in caps[7] and "image_f8" not in caps[2]
    assert caps[1]["supplemental_image_prompts"][0]["persona"] == ["Daniel Écija"] and caps[2]["image_prompts"][0]["persona"] == ["Daniel Écija"]
    norm = fase2a._normalize_long(out)
    n = {c["id"]: c for c in norm["chapters"]}
    assert n["ch01"]["image_f8"] == f8 and n["ch07"]["image_f8"] == {} and "image_f8" not in n["ch02"]
    assert norm["foto_madre_personas"] == out["foto_madre_personas"] and norm["foto_madre_registry"] == out["foto_madre_registry"]
    assert n["ch01"]["image_prompts"] == ["ip"] and n["ch01"]["video_prompts"] == ["vp"]            # el adaptador no cambia lo demás


# ── 10. foto_madre.py: madre por persona ────────────────────────────────────────────────────────────────────────
GRUPOS = [{"id": "spanish_migrant_families", "appearance": "Southern European features, with light olive to tanned skin."},
          {"id": "otro", "appearance": "Other group."}]
VISUAL = {"chapters": [
    {"chapter_number": 1, "image_prompt": "ip", "image_f8": {"persona": ["Daniel Écija"], "anio": "1962", "people_group": ["spanish_migrant_families"]},
     "supplemental_image_prompts": [{"prompt": "s", "persona": ["Daniel Écija", "María Bernal"], "anio": "1962", "people_group": ["otro"]}]},
    {"chapter_number": 2, "image_prompts": [
        {"prompt": "a", "persona": ["Daniel Écija"], "anio": "1961", "people_group": ["spanish_migrant_families"]},
        {"prompt": "b", "persona": ["Daniel Écija"], "anio": "1991", "people_group": ["otro"]},        # fuera de era → no cuenta
        {"prompt": "c", "persona": ["Ramón de Juan"], "anio": "1962", "people_group": ["spanish_migrant_families"]}]}]}
PROMPT_DANIEL = ("Head-and-shoulders portrait of a mid-20s Spanish man, wearing a plain, clean, light-coloured shirt. Southern "
                 "European features, with light olive to tanned skin. Neutral expression, facing the camera, plain mid-grey "
                 "background, soft even light. A grainy 35mm documentary photograph taken in 1962, with muted colors and "
                 "slight underexposure, in a dark-history realist style. No readable text, no signage, no labels.")


def test_foto_madre_persona_prompt_byte_a_byte_y_grupo_mas_frecuente():
    fotos = fm._fotos_del_guion(VISUAL)
    assert [(f["cap"], f["kind"], f["idx"]) for f in fotos] == [(1, "f8", 1), (1, "supp", 1), (2, "img", 1), (2, "img", 2), (2, "img", 3)]
    mias = fm._fotos_con_madre_de(DANIEL, fotos)
    assert [(f["cap"], f["kind"], f["idx"]) for f in mias] == [(1, "f8", 1), (1, "supp", 1), (2, "img", 1)]   # 1991 afuera
    grupos = {g["id"]: g for g in GRUPOS}
    assert fm._grupo_mas_frecuente(mias, grupos) == GRUPOS[0]["appearance"]        # 2 a 1
    assert fm._prompt_persona(DANIEL, fm._grupo_mas_frecuente(mias, grupos)) == PROMPT_DANIEL
    assert "bandaged" not in PROMPT_DANIEL and "faceless" not in PROMPT_DANIEL      # condition_by_period y _STYLE no entran
    # empate → el grupo que aparece primero en orden de guion; sin era con 4 dígitos → sin año
    assert fm._grupo_mas_frecuente([{"people_group": ["otro"]}, {"people_group": ["spanish_migrant_families"]}], grupos) == "Other group."
    sin = fm._prompt_persona({**DANIEL, "era": "1960s"}, "")
    assert "taken in 1960," in sin
    sin = fm._prompt_persona({**DANIEL, "era": "antes"}, "")
    assert "taken in" not in sin and "A grainy 35mm documentary photograph, with muted colors" in sin and ". Neutral expression" in sin


def test_foto_madre_personas_solo_con_2_fotos_y_sin_gpt(tmp_path, monkeypatch):
    monkeypatch.setattr(fm, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(fm.api, "image_engine", "seedream", raising=False)
    monkeypatch.setattr(fm, "_generate_madre_gpt", lambda *a, **k: pytest.fail("la madre de persona no cae a GPT"))
    monkeypatch.setattr(fm, "_generate_image_raw", lambda *a, **k: pytest.fail("la madre de persona no cae al motor activo"))
    pedidos = []

    def gen(prompt, dest):
        pedidos.append((prompt, dest.name))
        if "María" in prompt or "woman" in prompt:
            raise am.ContentRejectedError("rechazó prompt: content_policy")
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_bytes(PNG)
        return {"endpoint": "seedream", "path": str(dest), "seed": 1, "nsfw": None, "request_id": "r"}
    monkeypatch.setattr(fm, "_generate_madre_seedream", gen)
    topic = {"id": "t", "documented_people": [dict(DANIEL), dict(MARIA), {"name": "Ramón de Juan", "era": "1962-1964", "appearance_canon": "an adult Spanish man"}],
             "people_groups": GRUPOS}
    visual = {"chapters": [VISUAL["chapters"][0], {"chapter_number": 2, "image_prompts": VISUAL["chapters"][1]["image_prompts"]
                                                   + [{"prompt": "m", "persona": ["María Bernal"], "anio": "1962", "people_group": []}]}]}
    est = fm.generate_fotos_madre_personas(topic, "vid", visual)
    assert [p for p, _ in pedidos] and len(pedidos) == 2                                        # Daniel (3 fotos) y María (2); Ramón 1 → no
    assert topic["documented_people"][0]["foto_madre"] == str((tmp_path / "vid" / "foto_madre" / "daniel_cija.png").resolve())
    assert topic["documented_people"][1]["foto_madre"] == "" and est["María Bernal"]["estado"].startswith("error: ContentRejectedError")
    assert "foto_madre" not in topic["documented_people"][2] and est["Ramón de Juan"]["estado"].startswith("sin madre: 1 foto")
    assert est["Daniel Écija"]["estado"] == "ok" and est["Daniel Écija"]["fotos"] == 3 and est["Daniel Écija"]["prompt"] == PROMPT_DANIEL
    # segunda corrida: skip por archivo existente; adopción manual si el archivo está pero la db no
    pedidos.clear()
    fm.generate_fotos_madre_personas(topic, "vid", visual)
    assert pedidos == [(est["María Bernal"]["prompt"], "mar_a_bernal.png")]                 # Daniel skip; María se vuelve a intentar
    topic["documented_people"][0]["foto_madre"] = ""
    est2 = fm.generate_fotos_madre_personas(topic, "vid", visual)
    assert est2["Daniel Écija"]["estado"] == "ADOPTADA manual" and topic["documented_people"][0]["foto_madre"].endswith("daniel_cija.png")


def test_foto_madre_persona_motor_no_seedream_aviso_sin_madre(tmp_path, monkeypatch):
    monkeypatch.setattr(fm, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(fm.api, "image_engine", "kling", raising=False)
    monkeypatch.setattr(fm, "_generate_madre_seedream", lambda *a: pytest.fail("no debe pedir"))
    avisos = []
    monkeypatch.setattr(fm.error_handler, "log_warning", lambda stage, msg: avisos.append(msg))
    topic = {"id": "t", "documented_people": [dict(DANIEL)], "people_groups": GRUPOS}
    est = fm.generate_fotos_madre_personas(topic, "vid", VISUAL)
    assert est["Daniel Écija"]["estado"] == "sin madre: motor activo kling ≠ seedream" and "foto_madre" not in topic["documented_people"][0]
    assert avisos and "≠ seedream" in avisos[0]


def test_foto_madre_persona_lee_03_visual_de_steps_y_sigue_sin_sujeto(tmp_path, monkeypatch):
    monkeypatch.setattr(fm, "OUTPUT_DIR", tmp_path)
    monkeypatch.setattr(fm, "STEPS_DIR", tmp_path / "_steps")
    monkeypatch.setattr(fm.api, "image_engine", "seedream", raising=False)
    (tmp_path / "_steps" / "t").mkdir(parents=True)
    (tmp_path / "_steps" / "t" / "03_visual.json").write_text(json.dumps(VISUAL), encoding="utf-8")
    monkeypatch.setattr(fm, "_generate_madre_seedream",
                        lambda prompt, dest: (dest.parent.mkdir(parents=True, exist_ok=True), dest.write_bytes(PNG), {"endpoint": "s", "path": str(dest)})[2])
    topic = {"id": "t", "central_subject": {"kind": "person"}, "documented_people": [dict(DANIEL)], "people_groups": GRUPOS}
    fm.generate_foto_madre_for_topic(topic, "t")        # kind=person: sin madre de sujeto, pero la de persona sale igual
    assert topic["documented_people"][0]["foto_madre"].endswith("daniel_cija.png")
    # sin 03_visual.json → sin madres de persona, sin crash
    topic2 = {"id": "t2", "documented_people": [dict(DANIEL)]}
    assert fm.generate_fotos_madre_personas(topic2, "t2") == {} and "foto_madre" not in topic2["documented_people"][0]


def test_generate_madre_seedream_por_la_cola(tmp_path, monkeypatch):
    posts, costos = [], []
    monkeypatch.setattr(fm.requests, "post", lambda url, headers=None, json=None, timeout=None: (posts.append((url, json, timeout)), _Resp({"request_id": "r", "status_url": "S", "response_url": "R"}))[1])
    monkeypatch.setattr(fm, "_fal_queue_poll", lambda s, r, timeout=None: {"images": [{"url": "u"}], "seed": 3})
    monkeypatch.setattr(fm.requests, "get", lambda url, timeout=None: _Resp(content=PNG))
    monkeypatch.setattr(fm.cost_tracker, "track_seedream", lambda description, images=1, mode="t2i": costos.append((images, mode)))
    meta = fm._generate_madre_seedream("P", tmp_path / "m.png")
    url, payload, timeout = posts[0]
    assert "queue.fal.run" in url and url.endswith("/text-to-image") and timeout == am.FAL_SUBMIT_TIMEOUT_S
    assert payload["prompt"] == "P" and payload["num_images"] == 1 and "seed" not in payload and payload["image_size"]["width"] == 2560
    assert (tmp_path / "m.png").read_bytes()[:8] == PNG[:8] and costos == [(1, "t2i")] and meta["seed"] == 3


# ── 11. QA Studio: fix y reseed con la regla única ──────────────────────────────────────────────────────────────
def test_qa_reseed_con_persona_lleva_las_madres(tmp_path, monkeypatch):
    import qa_studio_server as qs
    reg = _madres(tmp_path, "Daniel Écija", "__subject__")
    script = tmp_path / "script.json"
    script.write_text(json.dumps({"foto_madre_registry": reg, "foto_madre_personas": PERSONAS}), encoding="utf-8")

    class S:
        assets_dir = tmp_path / "assets"
        base = tmp_path
        script_path = script

        def resolve_fix_entry(self, name):
            return {"prompt": "p", "art_profile": "", "subject_ref": "s", "persona": ["Daniel Écija"], "anio": "1962",
                    "foto_madre_ref": ["__subject__"]}

        def resolve_image(self, cap, name):
            return None
    got = {}
    ok, why, seed = qs._reseed_core(S(), "t", "ch02", "ch02_img_03.png", seed_fn=lambda v, s: 1, is_hook_fn=lambda c: False,
                                    generate_fn=lambda p, a, out, use_ultra, seed, foto_madre_data_uris=None: got.update(uris=foto_madre_data_uris),
                                    data_uri_fn=lambda p: f"uri:{Path(p).name}")
    assert ok and got["uris"] == ["uri:daniel_cija.png", "uri:subject.png"]      # (el helper nombra el archivo por slug)
    # Daniel en 1991 → solo el sujeto
    S.resolve_fix_entry = lambda self, name: {"prompt": "p", "art_profile": "", "persona": ["Daniel Écija"], "anio": "1991", "foto_madre_ref": ["__subject__"]}
    qs._reseed_core(S(), "t", "ch02", "ch02_img_03.png", seed_fn=lambda v, s: 1, is_hook_fn=lambda c: False,
                    generate_fn=lambda p, a, out, use_ultra, seed, foto_madre_data_uris=None: got.update(uris=foto_madre_data_uris),
                    data_uri_fn=lambda p: f"uri:{Path(p).name}")
    assert got["uris"] == ["uri:subject.png"]


def test_qa_fix_core_con_persona_madres_en_orden_y_texto_a_omar(tmp_path):
    import qa_studio_server as qa
    from test_qa_studio import build_topic, _fix_deps, _call_fix, TID
    build_topic(tmp_path)
    reg = _madres(tmp_path, "Daniel Écija")
    for p in (tmp_path / "data" / "scripts" / f"{TID}.json", tmp_path / "data" / "scripts" / "_steps" / TID / "03_visual.json"):
        d = json.loads(p.read_text(encoding="utf-8"))
        ch = next(c for c in d["chapters"] if c["chapter_number"] == 3)
        ch["image_prompts"][0]["persona"] = ["Daniel Écija"]
        ch["image_prompts"][0]["anio"] = "1962"
        if "foto_madre_registry" in d:
            d["foto_madre_registry"].update(reg)
            d["foto_madre_personas"] = PERSONAS
        p.write_text(json.dumps(d, ensure_ascii=False), encoding="utf-8")
    st = qa.QAState(TID, base_dir=tmp_path)
    assert st.resolve_fix_entry("ch03_img_01.png")["persona"] == ["Daniel Écija"]
    assert st.resolve_fix_entry("ch02_img_03.png")["persona"] == []
    seen = {}

    def gen(prompt, art_profile, out_path, use_ultra, seed, foto_madre_data_uris=None):
        seen["uris"] = foto_madre_data_uris
        out_path.write_bytes(b"X")
        return {}
    (ok, texto), _ = _call_fix(st, "ch03", "ch03_img_01.png", "x", _fix_deps(gen))
    assert ok is True and seen["uris"] == ["uri:daniel_cija.png", "uri:madre.png"]       # persona primero, después __subject__
    assert "madre de Daniel Écija (casillero persona: no cambia con el pedido)" in texto
    assert "persona" not in qa.__dict__.get("CASILLEROS_EDITABLES", ())                 # no editable
    from script_engine import m03_imagenes_v3 as v3img
    assert "persona" not in v3img.CASILLEROS_EDITABLES


# ── 12. rename, constantes con origen, _iter_image_items ───────────────────────────────────────────────────────
def test_rename_fal_queue_poll_y_constantes():
    assert hasattr(am, "_fal_queue_poll") and not hasattr(am, "_clip_poll")
    assert "_fal_queue_poll(" in inspect.getsource(am._call_clip_once) and "timeout=FAL_SUBMIT_TIMEOUT_S" in inspect.getsource(am._call_clip_once)
    assert "_fal_queue_poll(" in inspect.getsource(am._llamar_secuencia) and "_fal_queue_poll(" in inspect.getsource(fm._generate_madre_seedream)
    assert am.FAL_SUBMIT_TIMEOUT_S == 60 and am.FOTOS_POR_LLAMADA == 6 and am.CLIP_POLL_TIMEOUT == 600
    assert fm.ROPA_MADRE == "wearing a plain, clean, light-coloured shirt" and fm.MADRE_PERSONA_MIN_FOTOS == 2
    assert "_flux_poll" in inspect.getsource(am._generate_image_raw)          # _flux_poll no se toca
    assert "_pre_paso_secuencia(chapters, video_id, foto_madre_registry, foto_madre_personas)" in inspect.getsource(am.process_script)


def test_iter_image_items_lleva_anio_y_cartel():
    ch = {"image_prompts": [_item("p", ["Daniel Écija"], anio=" 1962 "), _item("q", [], cartel=True), "legacy", {"prompt": "r"}]}
    it = am._iter_image_items(ch)
    assert [(i["anio"], i["cartel"], i["persona"]) for i in it] == [("1962", False, ["Daniel Écija"]), ("1962", True, []), (None, False, []), (None, False, [])]
    assert am._anio_entero("c. 1962-63") == 1962 and am._anio_entero("") is None and am._anio_entero(None) is None
