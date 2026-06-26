"""
test_qa_studio.py — tests de QAState (SIN socket, SIN red).

Construye un topic sintético en un tmp_path con la MISMA estructura de disco que el
pipeline real (data/scripts/{tid}.json + output/audio/{tid}/ + output/{tid}/assets/) y
verifica la lógica del visor:

  - cap flux: spans correctos (start < end, crecientes) cuando los anchors matchean.
  - compute_anchor_starts devuelve None → reparto uniforme + sync_approx=True.
  - resolve_image rechaza path traversal (../).
  - caps() = 7, con single=True en los caps veo (1 y 7).

Corre con: python -m pytest test_qa_studio.py -q   (o python test_qa_studio.py)
"""
from __future__ import annotations

import json
from pathlib import Path

import qa_studio_server as qa


# ─────────────────────────────────────────────────────────────────
#  Fixture: arma un topic sintético en disco (estructura real)
# ─────────────────────────────────────────────────────────────────

TID = "test-topic-0001"


def _png(p: Path) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    # PNG mínimo válido (header) — el contenido no importa para la lógica.
    p.write_bytes(b"\x89PNG\r\n\x1a\n" + b"\x00" * 16)


def _words(phrases: list[str], step: float = 0.5) -> list[dict]:
    """Genera word-timestamps a partir de frases; cada palabra dura `step`."""
    words, t = [], 0.0
    for phrase in phrases:
        for w in phrase.split():
            words.append({"word": w, "start": round(t, 3), "end": round(t + step, 3)})
            t += step
    return words


# supps ORDENADOS (en orden de narración) para el cap 7 "limpio" → matchea como flux.
_CAP7_SUPPS_ORDERED = ["sierra uno dos", "tango tres cuatro", "uniform cinco seis"]
_CAP7_BASE_ANCHOR = "victor siete ocho cierre del clip"
# supps ORDENADOS para el cap 1 (veo start) "limpio" → sincroniza por supps solos.
_CAP1_SUPPS_ORDERED = ["alfa bravo charlie", "delta echo foxtrot"]


def build_topic(base: Path, *, matching_anchors: bool = True,
                cap7_clean: bool = False, cap1_clean: bool = False) -> str:
    """Crea el topic sintético. matching_anchors=False rompe el match anchor→words
    (anchors que NO aparecen en el audio) para forzar el reparto uniforme.
    cap7_clean=True hace que el cap 7 (veo_position=end) tenga supps ORDENADOS +
    base_anchor que matchean → camino timeline sincronizado."""
    # ── script: 7 caps, 1 y 7 veo, 2-6 flux ──
    chapters = []
    # anchors flux pensados para matchear las primeras palabras de cada segmento
    flux_anchor_sets = {
        2: ["alfa uno dos", "bravo tres cuatro", "charlie cinco seis"],
        3: ["delta uno", "echo dos", "foxtrot tres"],
        4: ["golf aaa", "hotel bbb"],
        5: ["india xx", "juliet yy", "kilo zz", "lima ww"],
        6: ["mike pp", "november qq"],
    }
    for n in range(1, 8):
        if n == 1:
            # veo_position=start → Option A (clip + galería).
            if cap1_clean:
                supps1 = [{"prompt": "x", "narration_anchor": a} for a in _CAP1_SUPPS_ORDERED]
            else:
                supps1 = [{"prompt": "x", "narration_anchor": "supp 1-1"},
                          {"prompt": "y", "narration_anchor": "supp 1-2"}]
            chapters.append({
                "chapter_number": 1,
                "render_engine": "veo",
                "veo_position": "start",
                "narration": "apertura del cap 1",
                "narration_anchor": "apertura del cap 1",
                "image_prompt": "A wide panoramic city view at dawn",
                "video_prompt": "Static camera with subtle upward drift over the skyline",
                "art_profile": "doc",
                "subject_ref": "establishing_shot",
                "supplemental_image_prompts": supps1,
            })
        elif n == 7:
            # veo_position=end → modelo timeline (v1.1).
            if cap7_clean:
                supps = [{"prompt": "p", "narration_anchor": a} for a in _CAP7_SUPPS_ORDERED]
                base_anchor = _CAP7_BASE_ANCHOR
            else:
                supps = [{"prompt": "x", "narration_anchor": "supp 7-1"},
                         {"prompt": "y", "narration_anchor": "supp 7-2"}]
                base_anchor = "apertura del cap 7"
            chapters.append({
                "chapter_number": 7,
                "render_engine": "veo",
                "veo_position": "end",
                "narration": "cierre del cap 7",
                "narration_anchor": base_anchor,
                "image_prompt": "A vast white marble boulevard",
                "video_prompt": "Slow pull out from a towering building, panning across the plaza",
                "art_profile": "doc",
                "subject_ref": "establishing_shot",
                "supplemental_image_prompts": supps,
            })
        else:
            anchors = flux_anchor_sets[n]
            chapters.append({
                "chapter_number": n,
                "render_engine": "flux",
                "narration": " ".join(anchors),
                "image_prompts": [{"prompt": "p", "narration_anchor": a} for a in anchors],
            })
    script = {"topic_id": TID, "video_type": "long", "chapters": chapters}
    sp = base / "data" / "scripts" / f"{TID}.json"
    sp.parent.mkdir(parents=True, exist_ok=True)
    sp.write_text(json.dumps(script, ensure_ascii=False), encoding="utf-8")

    # ── skeleton (roles) ──
    skel = {"topic_id": TID, "chapters": [
        {"chapter_number": 1, "role": "hook"},
        {"chapter_number": 7, "role": "reveal_outro"},
    ]}
    skp = base / "data" / "scripts" / "_steps" / TID / "01a_skeleton.json"
    skp.parent.mkdir(parents=True, exist_ok=True)
    skp.write_text(json.dumps(skel, ensure_ascii=False), encoding="utf-8")

    # ── audio + timestamps + assets ──
    adir = base / "output" / "audio" / TID
    adir.mkdir(parents=True, exist_ok=True)
    assets = base / "output" / TID / "assets"
    for n in range(1, 8):
        cid = f"ch{n:02d}"
        (adir / f"{cid}.mp3").write_bytes(b"\x00" * 8)  # audio dummy
        if n in (1, 7):
            # veo: clip + supps (en {cid}_flux) + base img (en {cid}_veo)
            _png(assets / f"{cid}_veo" / f"{cid}_img_01.png")
            (assets / f"{cid}_veo" / f"{cid}_clip_01.mp4").parent.mkdir(parents=True, exist_ok=True)
            (assets / f"{cid}_veo" / f"{cid}_clip_01.mp4").write_bytes(b"\x00" * 8)
            if n == 7 and cap7_clean:
                supp_anchors = _CAP7_SUPPS_ORDERED
                n_supp = len(supp_anchors)
                words = _words(supp_anchors + [_CAP7_BASE_ANCHOR, "cola final"])
            elif n == 1 and cap1_clean:
                n_supp = len(_CAP1_SUPPS_ORDERED)
                # narración del clip PRIMERO (no es anchor de supp) → clip ocupa [0, supp1].
                words = _words(["intro narrada del clip uno dos"]
                               + _CAP1_SUPPS_ORDERED + ["cola final del cap"])
            else:
                n_supp = 2
                words = _words([f"apertura del cap {n}"])
            for m in range(1, n_supp + 1):
                _png(assets / f"{cid}_flux" / f"{cid}_supp_{m:02d}.png")
        else:
            anchors = flux_anchor_sets[n]
            for m in range(1, len(anchors) + 1):
                _png(assets / f"{cid}_flux" / f"{cid}_img_{m:02d}.png")
            phrases = anchors if matching_anchors else [f"texto distinto {n} sin ningun anchor adentro"]
            words = _words(phrases + ["cola final del capitulo"])
        (adir / f"{cid}_timestamps.json").write_text(
            json.dumps(words, ensure_ascii=False), encoding="utf-8")

    return TID


# ─────────────────────────────────────────────────────────────────
#  Tests
# ─────────────────────────────────────────────────────────────────

def test_caps_seven_no_single_v17(tmp_path):
    build_topic(tmp_path)
    st = qa.QAState(TID, base_dir=tmp_path)
    caps = st.caps()
    assert len(caps) == 7, f"esperaba 7 caps, hay {len(caps)}"
    by_num = {c["num"]: c for c in caps}
    # v1.7: Option A retirada → NINGÚN cap es single (todos timeline).
    for n in range(1, 8):
        assert by_num[n]["single"] is False, f"cap {n} no debería ser single (v1.7)"
    # role del skeleton
    assert by_num[1]["role"] == "hook"
    assert by_num[7]["role"] == "reveal_outro"


def test_flux_spans_increasing_and_synced(tmp_path):
    build_topic(tmp_path, matching_anchors=True)
    st = qa.QAState(TID, base_dir=tmp_path)
    payload = st.cap(2)
    assert payload["single"] is False
    assert payload["sync_approx"] is False, "con anchors que matchean NO debería ser aproximado"
    segs = payload["segments"]
    assert len(segs) == 3
    for s in segs:
        assert s["start"] < s["end"], f"span no creciente: {s}"
        assert s["dur"] > 0
    # starts estrictamente crecientes
    starts = [s["start"] for s in segs]
    assert starts == sorted(starts) and len(set(starts)) == len(starts)
    # cada segmento trae su anchor + url
    assert all(s["anchor"] for s in segs)
    assert all(s["url"].startswith("/img?cap=ch02&name=ch02_img_") for s in segs)


def test_flux_no_match_falls_back_to_uniform(tmp_path):
    build_topic(tmp_path, matching_anchors=False)
    st = qa.QAState(TID, base_dir=tmp_path)
    payload = st.cap(3)
    assert payload["sync_approx"] is True, "sin match de anchors → reparto uniforme"
    segs = payload["segments"]
    assert len(segs) == 3
    # reparto uniforme: durations ~iguales y crecientes
    durs = [s["dur"] for s in segs]
    assert max(durs) - min(durs) < 1e-6
    for s in segs:
        assert s["start"] < s["end"]


def test_resolve_image_rejects_traversal(tmp_path):
    build_topic(tmp_path)
    st = qa.QAState(TID, base_dir=tmp_path)
    # nombre legítimo resuelve
    ok = st.resolve_image("ch02", "ch02_img_01.png")
    assert ok is not None and ok.exists()
    # traversal y nombres raros → None
    for bad in ("../../etc/passwd", "..\\..\\secret.png", "ch02_img_01.png/../../x",
                "ch99_img_01.png", "ch02_img_01.PNG ", "ch02_../img.png", "ch02_img_01.txt"):
        assert st.resolve_image("ch02", bad) is None, f"debería rechazar {bad!r}"
    # cap mismatch (name no empieza con el cap) → None
    assert st.resolve_image("ch02", "ch03_img_01.png") is None


def test_veo_cap_timeline_shape(tmp_path):
    """v1.7: cap 1 (veo start) es TIMELINE — single False, segments con el clip PRIMERO
    + supps, sin gallery."""
    build_topic(tmp_path)
    st = qa.QAState(TID, base_dir=tmp_path)
    payload = st.cap(1)
    assert payload["single"] is False
    assert "gallery" not in payload and "segments" in payload
    assert payload["has_clip"] is True
    segs = payload["segments"]
    assert segs[0]["is_clip"] is True and segs[0]["clip_url"] == "/clip?cap=ch01"
    # las supps vienen después del clip
    supp_segs = [s for s in segs if not s["is_clip"]]
    assert len(supp_segs) == 2
    # resolve_clip apunta al mp4 real
    assert st.resolve_clip("ch01") is not None
    assert st.resolve_clip("ch02") is None  # flux no tiene clip


def test_veo_end_timeline_synced(tmp_path):
    """cap 7 (veo_position=end) con supps ORDENADOS + base_anchor que matchean →
    segmentos = supps + 1 segmento is_clip final; starts crecientes; el clip
    arranca en el start de su base_anchor."""
    build_topic(tmp_path, cap7_clean=True)
    st = qa.QAState(TID, base_dir=tmp_path)
    p = st.cap(7)
    assert p["single"] is False
    assert p["sync_approx"] is False, "con anchors ordenados NO debería ser aproximado"
    assert p["has_clip"] is True
    segs = p["segments"]
    n_supp = len(_CAP7_SUPPS_ORDERED)
    assert len(segs) == n_supp + 1, "supps + 1 clip"
    # los primeros n_supp son fotos, el último es el clip
    assert all(not s["is_clip"] for s in segs[:n_supp])
    assert segs[-1]["is_clip"] is True
    assert segs[-1]["clip_url"] == "/clip?cap=ch07"
    # starts estrictamente crecientes a lo largo de TODOS los segmentos (supps + clip)
    starts = [s["start"] for s in segs]
    assert all(a < b for a, b in zip(starts, starts[1:])), f"starts no crecientes: {starts}"
    for s in segs:
        assert s["start"] < s["end"] and s["dur"] > 0
    # el clip arranca donde arranca su base_anchor (último anchor) — > último supp
    assert segs[-1]["start"] > segs[-2]["start"]
    assert segs[-1]["end"] == p["total"]


def test_veo_end_fallback_uniform_clip_tile(tmp_path):
    """cap 7 veo end SIN match de anchors → supps uniforme + sync_approx + clip como
    tile final SIN sync (start/end/dur nulos)."""
    build_topic(tmp_path, cap7_clean=False)
    st = qa.QAState(TID, base_dir=tmp_path)
    p = st.cap(7)
    assert p["single"] is False
    assert p["sync_approx"] is True
    segs = p["segments"]
    assert segs[-1]["is_clip"] is True
    assert segs[-1]["start"] is None and segs[-1]["end"] is None and segs[-1]["dur"] is None
    # supps con reparto uniforme
    supp_durs = [s["dur"] for s in segs if not s["is_clip"]]
    assert len(supp_durs) == 2
    assert max(supp_durs) - min(supp_durs) < 1e-6


def test_veo_start_is_timeline(tmp_path):
    """v1.7: cap 1 (veo_position=start) es timeline (no Option A): single False, segments."""
    build_topic(tmp_path, cap7_clean=True)
    st = qa.QAState(TID, base_dir=tmp_path)
    p = st.cap(1)
    assert p["single"] is False
    assert "segments" in p and "gallery" not in p
    assert p["segments"][0]["is_clip"] is True


def test_veo_start_spans_synced(tmp_path):
    """cap 1 timeline con supps ordenados → clip como PRIMER segmento [0, primer supp] +
    supps tiled, cronológicos, sin overlap."""
    build_topic(tmp_path, cap1_clean=True)
    st = qa.QAState(TID, base_dir=tmp_path)
    p = st.cap(1)
    assert p["single"] is False and p["sync_approx"] is False
    segs = p["segments"]
    # segmento 0 = clip, [0, primer supp]
    assert segs[0]["is_clip"] is True
    assert segs[0]["start"] == 0.0
    supp_segs = [s for s in segs if not s["is_clip"]]
    assert segs[0]["end"] == supp_segs[0]["start"]   # clip antes del primer supp
    # spans crecientes y sin overlap a lo largo de TODO
    starts = [s["start"] for s in segs]
    assert all(a < b for a, b in zip(starts, starts[1:])), f"no crecientes: {starts}"
    for s in segs:
        assert s["start"] < s["end"] and s["dur"] > 0
    assert supp_segs[-1]["end"] == p["total"]


def test_veo_start_spans_fallback_when_unmatched(tmp_path):
    """cap 1 sin match de supps → fallback: sync_approx, clip como tile inicial sin sync,
    supps uniformes."""
    build_topic(tmp_path)  # cap1 default: words no contienen los anchors de los supps
    st = qa.QAState(TID, base_dir=tmp_path)
    p = st.cap(1)
    assert p["sync_approx"] is True
    segs = p["segments"]
    assert segs[0]["is_clip"] is True
    assert segs[0]["start"] is None and segs[0]["end"] is None  # clip tile sin sync
    supp_durs = [s["dur"] for s in segs if not s["is_clip"]]
    assert len(supp_durs) == 2 and max(supp_durs) - min(supp_durs) < 1e-6  # uniformes


# ─────────────────────────────────────────────────────────────────
#  Zona 1 — fix de foto (/fix_image)
# ─────────────────────────────────────────────────────────────────

class _Rejected(Exception):
    """Stub local de ContentRejectedError (no importa asset_manager)."""


def _fix_deps(generate_fn, *, new_prompt="A rewritten english prompt"):
    """Deps inyectadas para _fix_core → tests sin red, sin Flux, sin Gemini."""
    return dict(
        rewrite_fn=lambda si, up: {"new_prompt": new_prompt},
        seed_fn=lambda vid, sref: 123,
        generate_fn=generate_fn,
        is_hook_fn=lambda cap: cap == "ch01",
        content_rejected_exc=_Rejected,
        now_ts="20260614_000000",
    )


def test_fix_resolve_entry_flux_and_supp(tmp_path):
    build_topic(tmp_path)
    st = qa.QAState(TID, base_dir=tmp_path)
    # flux _img_ → image_prompts[idx-1]
    e = st.resolve_fix_entry("ch02_img_03.png")
    assert e and e["kind"] == "img" and e["idx"] == 3
    assert e["prompt"] == "p" and e["narration_anchor"] == "charlie cinco seis"
    # veo _supp_ → supplemental_image_prompts[idx-1]
    e2 = st.resolve_fix_entry("ch01_supp_02.png")
    assert e2 and e2["kind"] == "supp" and e2["idx"] == 2
    assert e2["narration_anchor"] == "supp 1-2"
    # basura / fuera de rango / traversal → None
    for bad in ("../x.png", "ch02_img_99.png", "ch02_img_03.PNG",
                "ch99_img_01.png", "ch02_clip_01.mp4", "ch02_img_03.png/../x"):
        assert st.resolve_fix_entry(bad) is None, f"debería rechazar {bad!r}"


def test_fix_core_happy_path_backup_before_generate(tmp_path):
    build_topic(tmp_path)
    st = qa.QAState(TID, base_dir=tmp_path)
    seen = {}

    def gen(prompt, art_profile, out_path, use_ultra, seed):
        # el backup DEBE existir ANTES de pisar
        baks = list((st.assets_dir / "_qa_backups").glob("ch02_img_03.png.*.bak.png"))
        seen["backup_before"] = (len(baks) == 1)
        seen.update(prompt=prompt, seed=seed, ultra=use_ultra)
        out_path.write_bytes(b"NEWPNGDATA")
        return {"path": out_path}

    ok, reason = qa._fix_core(st, TID, "ch02", "ch02_img_03.png", "más oscuro",
                              **_fix_deps(gen))
    assert ok is True and reason is None
    assert seen["backup_before"] is True
    assert seen["prompt"] == "A rewritten english prompt"
    assert seen["seed"] == 123 and seen["ultra"] is False  # ch02 no es hook
    assert (st.assets_dir / "ch02_flux" / "ch02_img_03.png").read_bytes() == b"NEWPNGDATA"


def test_fix_core_supp_uses_ultra_for_hook(tmp_path):
    build_topic(tmp_path)
    st = qa.QAState(TID, base_dir=tmp_path)
    seen = {}

    def gen(prompt, art_profile, out_path, use_ultra, seed):
        seen["ultra"] = use_ultra
        out_path.write_bytes(b"X")
        return {}

    ok, _ = qa._fix_core(st, TID, "ch01", "ch01_supp_01.png", "cambio",
                         **_fix_deps(gen))
    assert ok is True and seen["ultra"] is True  # ch01 = hook → use_ultra (cosmético hoy)


def test_fix_invalidates_baked_visual(tmp_path):
    """Tras un fix OK, el clip visual horneado del cap se borra → ENSAMBLAR re-renderiza
    desde el PNG nuevo (flag #1)."""
    build_topic(tmp_path)
    st = qa.QAState(TID, base_dir=tmp_path)
    work = tmp_path / "output" / TID / "_fase2b_work"
    work.mkdir(parents=True, exist_ok=True)
    baked = work / "ch02_flux_visual.mp4"
    baked.write_bytes(b"OLDBAKED")
    other = work / "ch03_flux_visual.mp4"   # otro cap NO se toca
    other.write_bytes(b"KEEP")

    def gen(prompt, art_profile, out_path, use_ultra, seed):
        out_path.write_bytes(b"X")
        return {}

    ok, _ = qa._fix_core(st, TID, "ch02", "ch02_img_03.png", "x", **_fix_deps(gen))
    assert ok is True
    assert not baked.exists(), "el clip horneado del cap fixeado debe invalidarse"
    assert other.exists(), "otros caps NO se tocan"


def test_fix_core_content_rejected(tmp_path):
    build_topic(tmp_path)
    st = qa.QAState(TID, base_dir=tmp_path)

    def gen(*a, **k):
        raise _Rejected("content_policy violation")

    ok, reason = qa._fix_core(st, TID, "ch02", "ch02_img_03.png", "x", **_fix_deps(gen))
    assert ok is False and reason.startswith("filtro:")


def test_fix_core_empty_rewrite_skips_generate(tmp_path):
    build_topic(tmp_path)
    st = qa.QAState(TID, base_dir=tmp_path)

    def gen(*a, **k):
        raise AssertionError("no debe generar si el rewrite quedó vacío")

    deps = _fix_deps(gen)
    deps["rewrite_fn"] = lambda si, up: {"new_prompt": "   "}
    ok, reason = qa._fix_core(st, TID, "ch02", "ch02_img_03.png", "x", **deps)
    assert ok is False and "vacío" in reason


def test_fix_guard_one_at_a_time(tmp_path):
    build_topic(tmp_path)
    qa.STATE = qa.QAState(TID, base_dir=tmp_path)
    qa.TOPIC_ID = TID
    qa._FIX.update(running=True, done=False, ok=None, reason=None, img_name=None)
    try:
        res = qa._start_fix("ch02", "ch02_img_01.png", "x")
        assert res == {"conflict": True}
    finally:
        qa._FIX.update(running=False, done=False, ok=None, reason=None, img_name=None)


# ─────────────────────────────────────────────────────────────────
#  Zona 1.5 — fix de clip (/fix_clip)
# ─────────────────────────────────────────────────────────────────

def _clipfix_deps(generate_veo_fn, *, generate_fn=None,
                  new_prompt="A rewritten english image prompt"):
    """Deps inyectadas para _clipfix_core (contrato nuevo, HANDOFF clip-regen):
    regenera la FOTO (rewrite del image_prompt con el rewriter de A → still seedream) y
    re-corre Veo con el video_prompt INTACTO."""
    def _default_still(prompt, art_profile, out_path, use_ultra, seed):
        out_path.write_bytes(b"NEWSTILL")
        return {}
    return dict(
        rewrite_fn=lambda si, up: {"new_prompt": new_prompt},   # schema de A (foto)
        seed_fn=lambda vid, sref: 123,
        generate_fn=generate_fn or _default_still,
        is_hook_fn=lambda cap: cap == "ch01",
        generate_veo_fn=generate_veo_fn,
        content_rejected_exc=_Rejected,
        now_ts="20260614_000000",
    )


def test_resolve_clip_entry(tmp_path):
    build_topic(tmp_path)
    st = qa.QAState(TID, base_dir=tmp_path)
    e = st.resolve_clip_entry("ch01")
    assert e and e["cap"] == "ch01"
    assert "upward drift" in e["video_prompt"]
    assert e["image_prompt"].startswith("A wide panoramic")
    assert e["first_frame"].endswith("ch01_img_01.png")
    assert e["out_clip"].endswith("ch01_clip_01.mp4")
    assert e["clip_name"] == "ch01_clip_01.mp4"
    # §4a: art_profile + subject_ref del cap (los necesita el clip-regen para la still)
    assert e["art_profile"] == "doc" and e["subject_ref"] == "establishing_shot"
    # flux cap → no tiene clip → None
    assert st.resolve_clip_entry("ch02") is None
    # cap inexistente / basura → None
    assert st.resolve_clip_entry("ch99") is None
    assert st.resolve_clip_entry("../x") is None


def test_clipfix_core_regenera_foto_video_prompt_intacto(tmp_path):
    """Contrato nuevo: regenerar video = FOTO nueva (rewrite del image_prompt → still seedream)
    + Veo i2v con el video_prompt SIN TOCAR. Backups de still vieja Y clip viejo; baked invalidado."""
    build_topic(tmp_path)
    st = qa.QAState(TID, base_dir=tmp_path)
    work = tmp_path / "output" / TID / "_fase2b_work"
    work.mkdir(parents=True, exist_ok=True)
    (work / "ch01_hybrid_visual.mp4").write_bytes(b"OLD")
    (work / "ch01_flux_visual.mp4").write_bytes(b"OLD")
    seen = {}

    def still(prompt, art_profile, out_path, use_ultra, seed):
        seen["still_prompt"] = prompt
        seen["seed"] = seed
        baks = list((st.assets_dir / "_qa_backups").glob("ch01_img_01.png.*.bak.png"))
        seen["still_backup_before"] = (len(baks) == 1)
        out_path.write_bytes(b"NEWSTILL")
        return {}

    def veo(image_path, prompt, out_path):
        seen["veo_frame"] = str(image_path)
        seen["veo_prompt"] = prompt
        baks = list((st.assets_dir / "_qa_backups").glob("ch01_clip_01.mp4.*.bak.mp4"))
        seen["clip_backup_before"] = (len(baks) == 1)
        out_path.write_bytes(b"NEWCLIP")
        return out_path

    ok, reason = qa._clipfix_core(st, TID, "ch01", "más oscuro, niebla",
                                  **_clipfix_deps(veo, generate_fn=still))
    assert ok is True and reason is None
    # 1. la FOTO se regeneró con el image_prompt EDITADO (rewriter de A), seed por subject_ref
    assert seen["still_prompt"] == "A rewritten english image prompt" and seen["seed"] == 123
    # 2. Veo corrió sobre la still nueva con el video_prompt ORIGINAL (intacto, verbatim)
    assert seen["veo_frame"].endswith("ch01_img_01.png")
    assert "upward drift" in seen["veo_prompt"]            # = entry["video_prompt"] sin tocar
    # 3. backups de la still vieja Y el clip viejo, ANTES de pisar
    assert seen["still_backup_before"] is True and seen["clip_backup_before"] is True
    # 4. still + clip nuevos pisaron el MISMO filename (conteo intacto)
    assert (st.assets_dir / "ch01_veo" / "ch01_img_01.png").read_bytes() == b"NEWSTILL"
    assert (st.assets_dir / "ch01_veo" / "ch01_clip_01.mp4").read_bytes() == b"NEWCLIP"
    # 5. baked invalidado → ENSAMBLAR re-concatena desde el clip nuevo
    assert not (work / "ch01_hybrid_visual.mp4").exists()
    assert not (work / "ch01_flux_visual.mp4").exists()


def test_clipfix_core_content_rejected_veo(tmp_path):
    build_topic(tmp_path)
    st = qa.QAState(TID, base_dir=tmp_path)

    def veo(*a, **k):
        raise _Rejected("content_policy 422")

    ok, reason = qa._clipfix_core(st, TID, "ch07", "x", **_clipfix_deps(veo))
    assert ok is False and reason.startswith("filtro (veo):")


def test_clipfix_core_content_rejected_still(tmp_path):
    build_topic(tmp_path)
    st = qa.QAState(TID, base_dir=tmp_path)

    def still(*a, **k):
        raise _Rejected("content_policy 422 en la foto")

    def veo(*a, **k):
        raise AssertionError("no debe correr Veo si la still fue rechazada")

    ok, reason = qa._clipfix_core(st, TID, "ch07", "x",
                                  **_clipfix_deps(veo, generate_fn=still))
    assert ok is False and reason.startswith("filtro (still):")


def test_clipfix_core_empty_rewrite_skips_generate(tmp_path):
    build_topic(tmp_path)
    st = qa.QAState(TID, base_dir=tmp_path)

    def still(*a, **k):
        raise AssertionError("no debe regenerar la still si el rewrite quedó vacío")

    def veo(*a, **k):
        raise AssertionError("no debe correr Veo si el rewrite quedó vacío")

    deps = _clipfix_deps(veo, generate_fn=still)
    deps["rewrite_fn"] = lambda si, up: {"new_prompt": "  "}
    ok, reason = qa._clipfix_core(st, TID, "ch01", "x", **deps)
    assert ok is False and "vacío" in reason


def test_clipfix_guard_shared_with_photo(tmp_path):
    build_topic(tmp_path)
    qa.STATE = qa.QAState(TID, base_dir=tmp_path)
    qa.TOPIC_ID = TID
    qa._FIX.update(running=True, done=False, ok=None, reason=None, img_name=None)
    try:
        res = qa._start_clipfix("ch01", "x")
        assert res == {"conflict": True}
    finally:
        qa._FIX.update(running=False, done=False, ok=None, reason=None, img_name=None)


# ─────────────────────────────────────────────────────────────────
#  Zona 2 — fix de pronunciación/audio (/fix_narration)
# ─────────────────────────────────────────────────────────────────

def _setup_narr(tmp_path, *, norm_text="La DEA cerró el DEAL grande.", with_sync=True):
    """Topic sintético + 01b_narration_normalized + sync_map + audio del cap 2."""
    build_topic(tmp_path)
    nm = {"chapters": [{"chapter_number": 2, "narration_original": "orig",
                        "narration_normalized": norm_text, "spans_applied": []}]}
    npth = tmp_path / "data" / "scripts" / "_steps" / TID / "01b_narration_normalized.json"
    npth.parent.mkdir(parents=True, exist_ok=True)
    npth.write_text(json.dumps(nm, ensure_ascii=False), encoding="utf-8")
    if with_sync:
        sm = {"video_id": TID, "chapters": [
            {"id": "ch02", "text": "La DEA cerro el DEAL grande.", "narrative_intent": "development"}]}
        smp = tmp_path / "output" / "audio" / TID / "sync_map.json"
        smp.parent.mkdir(parents=True, exist_ok=True)
        smp.write_text(json.dumps(sm, ensure_ascii=False), encoding="utf-8")
    adir = tmp_path / "output" / "audio" / TID
    (adir / "ch02_alignment.json").write_text("[]", encoding="utf-8")
    (adir / "ch02.meta.json").write_text("{}", encoding="utf-8")
    return qa.QAState(TID, base_dir=tmp_path)


def _narr_deps(process_fn, *, found=True, token="DEA", pron="de e a", category="spelled"):
    return dict(
        rewrite_fn=lambda si, up: {"token": token, "pronunciation": pron,
                                   "category": category, "found": found, "note": "x"},
        process_fn=process_fn,
        content_rejected_exc=_Rejected,
        now_ts="20260615_000000",
    )


def test_narrfix_happy_boundary_dict_backup_invalidate(tmp_path):
    st = _setup_narr(tmp_path)
    work = tmp_path / "output" / TID / "_fase2b_work"
    work.mkdir(parents=True, exist_ok=True)
    (work / "ch02_flux_visual.mp4").write_bytes(b"OLD")
    calls = {}

    def proc(script):
        calls["script"] = script

    ok, reason = qa._narrfix_core(st, TID, "ch02", "lee mal la sigla DEA", **_narr_deps(proc))
    assert ok is True and reason is None
    # patch con LÍMITE DE PALABRA: DEA→"de e a", DEAL intacto
    nm = json.loads((st.base / "data" / "scripts" / "_steps" / TID
                     / "01b_narration_normalized.json").read_text(encoding="utf-8"))
    assert nm["chapters"][0]["narration_normalized"] == "La de e a cerró el DEAL grande."
    # custom_dict idempotente con la entry
    cd = json.loads((st.base / "data" / "normalizer_custom_dict.json").read_text(encoding="utf-8"))
    assert [e["token"] for e in cd["entries"]].count("DEA") == 1
    assert cd["entries"][0] == {"token": "DEA", "pronunciation": "de e a", "category": "spelled"}
    # backups (normalized + audio viejo)
    bdir = st.assets_dir / "_qa_backups"
    assert list(bdir.glob("01b_narration_normalized.*.bak.json"))
    assert list(bdir.glob("ch02.mp3.*.bak")) and list(bdir.glob("ch02_timestamps.json.*.bak"))
    # re-TTS: process_fn con script reconstruido del sync_map (text ORIGINAL del cap)
    assert calls["script"]["video_id"] == TID
    assert calls["script"]["chapters"][0]["id"] == "ch02"
    assert "DEAL" in calls["script"]["chapters"][0]["text"]
    # baked invalidado
    assert not (work / "ch02_flux_visual.mp4").exists()


def test_narrfix_idempotent_dict(tmp_path):
    st = _setup_narr(tmp_path)
    qa._narrfix_core(st, TID, "ch02", "DEA mal", **_narr_deps(lambda s: None))
    # 2º fix mismo token (sobre el texto ya patcheado no estaría DEA → usar otro norm)
    # reescribimos el normalized para que DEA vuelva a estar y re-fixear:
    npth = st.base / "data" / "scripts" / "_steps" / TID / "01b_narration_normalized.json"
    nm = json.loads(npth.read_text(encoding="utf-8"))
    nm["chapters"][0]["narration_normalized"] = "Otra vez la DEA."
    npth.write_text(json.dumps(nm, ensure_ascii=False), encoding="utf-8")
    qa._narrfix_core(st, TID, "ch02", "DEA mal", **_narr_deps(lambda s: None))
    cd = json.loads((st.base / "data" / "normalizer_custom_dict.json").read_text(encoding="utf-8"))
    assert [e["token"] for e in cd["entries"]].count("DEA") == 1  # no duplica


def test_narrfix_not_found_no_regen(tmp_path):
    st = _setup_narr(tmp_path)
    before = (st.base / "data" / "scripts" / "_steps" / TID
              / "01b_narration_normalized.json").read_text(encoding="utf-8")
    called = {"n": 0}

    def proc(s):
        called["n"] += 1

    ok, reason = qa._narrfix_core(st, TID, "ch02", "no sé qué suena raro",
                                  **_narr_deps(proc, found=False))
    assert ok is False and "reformulá" in reason
    assert called["n"] == 0  # no re-TTS
    after = (st.base / "data" / "scripts" / "_steps" / TID
             / "01b_narration_normalized.json").read_text(encoding="utf-8")
    assert before == after  # normalized intacto


def test_narrfix_token_absent_aborts(tmp_path):
    st = _setup_narr(tmp_path, norm_text="Un texto sin la sigla buscada.")
    called = {"n": 0}

    def proc(s):
        called["n"] += 1

    ok, reason = qa._narrfix_core(st, TID, "ch02", "lee mal DEA",
                                  **_narr_deps(proc, token="DEA"))
    assert ok is False and "no aparece" in reason
    assert called["n"] == 0  # no regenera al pedo


def test_narrfix_content_rejected(tmp_path):
    st = _setup_narr(tmp_path)

    def proc(s):
        raise _Rejected("content_policy")

    ok, reason = qa._narrfix_core(st, TID, "ch02", "DEA mal", **_narr_deps(proc))
    assert ok is False and reason.startswith("filtro:")


# ─────────────────────────────────────────────────────────────────
#  Form asistido (marcador fase1 + validación de stdin)
# ─────────────────────────────────────────────────────────────────

def test_form_line_sanitize(tmp_path):
    """_sanitize_form_line acepta cualquier respuesta de UNA línea y rechaza inyección
    multilínea / líneas absurdas. Saca el salto final."""
    for good in ("7", "1,4", "Q", "S", "L", "long", ""):
        assert qa._sanitize_form_line(good) == good, f"debería aceptar {good!r}"
    assert qa._sanitize_form_line("7\n") == "7"      # saca el salto final
    assert qa._sanitize_form_line("1,4\r\n") == "1,4"
    for bad in ("1\n2", "a\rb", "x" * 501):           # multilínea / absurda → None
        assert qa._sanitize_form_line(bad) is None, f"debería rechazar {bad!r}"


def test_fase1_form_item_mapping(tmp_path):
    """fase1._seed_to_form_item: risk normalizado, dudoso derivado, números crudos."""
    import fase1
    seed = {"seed_title": "T", "judge": {"verdict": "oro", "cohort": "3/3",
            "risk": "ratio_inflado", "reason": "r"},
            "evidence": {"en_viral": {"views": 2900000, "outlier_ratio": 16.0,
                         "en_age_months": 3, "original_title": "EN", "query_fallback": False},
                         "es_gap": {"label": "HUECO", "ontopic_count": 1, "query_fallback": True}}}
    it = fase1._seed_to_form_item(1, seed)
    assert it["idx"] == 1 and it["title"] == "T" and it["es_label"] == "HUECO"
    assert it["competidores"] == 1 and it["en_views"] == 2900000 and it["en_ratio"] == 16.0
    assert it["risk"] == "inflado"          # ratio_inflado → inflado
    assert it["fallback"] is True           # OR de los dos query_fallback
    assert it["dudoso"] is False            # oro → main
    # verdict != oro → dudoso
    seed2 = {"seed_title": "T2", "judge": {"verdict": "descartar", "risk": "disputado"}, "evidence": {}}
    it2 = fase1._seed_to_form_item(2, seed2)
    assert it2["dudoso"] is True and it2["risk"] == "disputado" and it2["es_label"] == "—"


def test_fase1_marker_ascii_and_shape(tmp_path):
    """El marcador @@QAFORM@@ es 1 línea ASCII pura con el schema del contrato."""
    import io, contextlib, fase1
    seed = {"seed_title": "Café água", "judge": {"verdict": "oro", "risk": "ninguno"},
            "evidence": {"en_viral": {"views": 100}, "es_gap": {"label": "VACIO", "ontopic_count": 0}}}
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        fase1._emit_qaform_seed_marker([seed])
    line = buf.getvalue().strip()
    assert line.startswith("@@QAFORM@@ ") and line.isascii()  # Windows-safe
    m = json.loads(line[len("@@QAFORM@@ "):])
    assert m["menu"] == "seed_pick" and m["accept"] == "int_csv"
    assert len(m["payload"]["seeds"]) == 1 and m["payload"]["seeds"][0]["idx"] == 1


def test_fase1_choice_marker(tmp_path):
    """Marcador genérico de choice: accept='key', options[], default, body. ASCII puro."""
    import io, contextlib, fase1
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        fase1._emit_qaform_choice_marker(
            "video_type", "Tipo de video",
            [{"key": "S", "label": "SHORT — corto"}, {"key": "L", "label": "LONG — largo"}],
            default="S")
    line = buf.getvalue().strip()
    assert line.startswith("@@QAFORM@@ ") and line.isascii()
    m = json.loads(line[len("@@QAFORM@@ "):])
    assert m["menu"] == "video_type" and m["accept"] == "key" and m["default"] == "S"
    assert [o["key"] for o in m["options"]] == ["S", "L"] and m["body"] is None
    # con body + opción deshabilitada
    buf2 = io.StringIO()
    with contextlib.redirect_stdout(buf2):
        fase1._emit_qaform_choice_marker(
            "reuse_seeds", "¿Usar seeds?",
            [{"key": "S", "label": "Usar"}, {"key": "n", "label": "Buscar", "disabled": True}],
            default="S", body="prev seeds")
    m2 = json.loads(buf2.getvalue().strip()[len("@@QAFORM@@ "):])
    assert m2["body"] == "prev seeds" and m2["options"][1]["disabled"] is True


# ── runner directo (sin pytest) ──
if __name__ == "__main__":
    import tempfile
    import traceback

    tests = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    for t in tests:
        with tempfile.TemporaryDirectory() as d:
            try:
                t(Path(d))
                print(f"  ✓ {t.__name__}")
                passed += 1
            except Exception:  # noqa: BLE001
                print(f"  ✗ {t.__name__}")
                traceback.print_exc()
    print(f"\n{passed}/{len(tests)} OK")
    raise SystemExit(0 if passed == len(tests) else 1)
