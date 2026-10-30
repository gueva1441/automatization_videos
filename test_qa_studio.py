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
from script_engine import m03_imagenes_v3 as qa_v3   # CASILLEROS_EDITABLES / _PROSA (sin red)


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


# F59: casilleros de m03 v3 en cada ítem (raw_llm_prompt/anio/anio_fuente/beat), como en 03_visual.json real.
_CAS_KEYS = ("subject", "action", "gaze_interaction", "setting", "color_palette", "props_detail", "shot_scale",
             "camera_angle", "lens_technique", "lighting", "mood", "style", "text_in_image", "hard_fact_ids")
_TOPIC = {"id": TID, "people_groups": [{"id": "miners", "appearance": "Lean men in dusty overalls."}],
          "escaleta": {"beats": [{"n": 2, "cap": 2, "funcion": "x", "emocion": "x", "intensidad": 1,
                                  "dato_central": "", "imagen_sensorial": "cientos de hombres llenan la galería"}],
                       "pico": {"beat": 2}},
          "parrafos_v3": []}


def _casilleros(anchor: str) -> dict:
    return {"subject": f"A miner, {anchor}", "action": "stands still at the pit head", "gaze_interaction": "looks away",
            "setting": "a mine", "color_palette": "grey, ochre", "props_detail": "a carbide lamp", "shot_scale": "medium",
            "camera_angle": "eye-level", "lens_technique": "50mm lens", "lighting": "harsh sun", "mood": "grim",
            "style": "documentary", "text_in_image": {"present": False, "text": "", "font": "", "location": ""},
            "hard_fact_ids": [], "people_group": ["miners"], "year": "1962"}


def _item(anchor: str, *, old_script: bool = False, beat: int = 2, madre: list | None = None) -> dict:
    """Un ítem del guion como lo deja m03 v3 (+ m06); old_script=True → sin casilleros/anio (guion viejo)."""
    if old_script:
        return {"prompt": "p", "narration_anchor": anchor}
    cas = _casilleros(anchor)
    return {**cas, "prompt": "p", "narration_anchor": anchor, "beat": beat, "cerrada": False,
            "subject_ref": "main_subject", "foto_madre_ref": madre or [], "art_profile": "",
            "raw_llm_prompt": json.dumps(cas, ensure_ascii=False),
            "anio": "1962", "anio_fuente": "1) el casillero `year` del modelo", "sensible": False, "motivos": []}


def build_topic(base: Path, *, matching_anchors: bool = True,
                cap7_clean: bool = False, cap1_clean: bool = False, old_script: bool = False) -> str:
    """Crea el topic sintético. matching_anchors=False rompe el match anchor→words
    (anchors que NO aparecen en el audio) para forzar el reparto uniforme.
    cap7_clean=True hace que el cap 7 (veo_position=end) tenga supps ORDENADOS +
    base_anchor que matchean → camino timeline sincronizado.
    F59: escribe también _steps/<tid>/03_visual.json (mismos caps) y voz_clip en los caps con clip;
    old_script=True = guion viejo (sin casilleros, sin anio, sin voz_clip)."""
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
            supps1 = [_item(a, old_script=old_script, beat=1)
                      for a in (_CAP1_SUPPS_ORDERED if cap1_clean else ["supp 1-1", "supp 1-2"])]
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
                **({} if old_script else {"voz_clip": "voz del clip uno"}),
            })
        elif n == 7:
            # veo_position=end → modelo timeline (v1.1).
            if cap7_clean:
                supps = [_item(a, old_script=old_script, beat=7) for a in _CAP7_SUPPS_ORDERED]
                base_anchor = _CAP7_BASE_ANCHOR
            else:
                supps = [_item(a, old_script=old_script, beat=7) for a in ("supp 7-1", "supp 7-2")]
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
                **({} if old_script else {"voz_clip": "voz del clip siete"}),
            })
        else:
            anchors = flux_anchor_sets[n]
            chapters.append({
                "chapter_number": n,
                "render_engine": "flux",
                "narration": " ".join(anchors),
                # cap 3, foto 1: anclada a la foto madre del sujeto (F59: foto madre resuelta contra el registry)
                "image_prompts": [_item(a, old_script=old_script,
                                        madre=["__subject__"] if (n == 3 and i == 0) else None)
                                  for i, a in enumerate(anchors)],
            })
    madre = base / "output" / TID / "foto_madre" / "madre.png"
    _png(madre)
    script = {"topic_id": TID, "video_type": "long", "chapters": chapters,
              "foto_madre_registry": {} if old_script else {"__subject__": str(madre)}}
    sp = base / "data" / "scripts" / f"{TID}.json"
    sp.parent.mkdir(parents=True, exist_ok=True)
    sp.write_text(json.dumps(script, ensure_ascii=False), encoding="utf-8")
    # F59: 03_visual.json = la fuente que m06 copia (mismos caps/ítems que el guion vivo, sin las claves de m06)
    vis = {"topic_id": TID, "chapters": json.loads(json.dumps(chapters, ensure_ascii=False))}
    for c in vis["chapters"]:
        c.pop("narration", None)
        c.pop("render_engine", None)
    vp = base / "data" / "scripts" / "_steps" / TID / "03_visual.json"
    vp.parent.mkdir(parents=True, exist_ok=True)
    vp.write_text(json.dumps(vis, ensure_ascii=False, indent=2), encoding="utf-8")

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
#  Zona 1 — fix de foto (/fix_image) · F59 A2: editor de casilleros + armar_item + grade
#  (deps inyectadas: sin red, sin Opus, sin Seedream; el reintento es el REAL de m03_visual)
# ─────────────────────────────────────────────────────────────────

HANDOFF_F59 = Path(__file__).resolve().parent / "lab" / "hyperframes" / "f59" / "HANDOFF_F59_qa_studio_produccion.md"


class _Rejected(Exception):
    """Stub local de ContentRejectedError (no importa asset_manager)."""


class _ClaudeDown(Exception):
    """Stub con la forma de claude_helpers.ClaudeError: los tests lo registran como subclase (ver _fix_deps)."""


def _fake_armar_item(it, anio, grupos, escala, lang, composicion="", sin_cartel=False, anio_fuente=""):
    """Doble de m03_visual.armar_item (contrato A1): muta y devuelve `it` con prompt/raw_llm_prompt/anio/anio_fuente/
    sensible/motivos y, si la acción trae un gesto que HANDS_FACE borra, `_f8_slots_scrub`."""
    it["prompt"] = (f"{it['subject']}. {it['action']}. {it['setting']}, {anio}. escala={escala} lang={lang} "
                    f"grupos={sorted(grupos)} shot={it.get('shot_scale')}")
    it["raw_llm_prompt"] = json.dumps({k: it.get(k) for k in (*_CAS_KEYS, "people_group", "year")}, ensure_ascii=False)
    it["anio"], it["anio_fuente"] = anio, anio_fuente
    it["sensible"], it["motivos"] = False, []
    if "jaw clenched" in it["action"]:
        it["_f8_slots_scrub"] = ["action: HANDS_FACE: jaw clenched"]
    return it


def _opus_casilleros(editar):
    """Fake de Opus (firma de call_flash_json): devuelve el JSON que recibió con `editar` encima; cuenta llamadas."""
    calls = []

    def llamar(prompt, system_instruction=None, response_schema=None, description=None, **_):
        calls.append({"prompt": prompt, "schema": response_schema, "description": description})
        cas = json.loads(prompt.split("CASILLEROS:\n", 1)[1].split("\n\nPEDIDO DE OMAR:", 1)[0])
        return {**cas, **editar}
    llamar.calls = calls
    return llamar


def _fix_deps(generate_fn, *, llamar_fn=None, editar=None, grade_fn=None, topic=None):
    """Deps inyectadas para _fix_core (contrato F59 A2)."""
    import claude_helpers
    from script_engine import m03_visual
    seen = {"grade": []}

    def _grade(src):
        seen["grade"].append(src)
        dst = src.with_name(f"{src.stem}_graded{src.suffix}")
        dst.write_bytes(b"GRADED" + src.read_bytes())
        return dst
    deps = dict(
        llamar_fn=llamar_fn or _opus_casilleros(editar if editar is not None else {"subject": "A miner looking at the camera"}),
        retry_fn=m03_visual._call_with_validation_retry,     # el reintento REAL (MAX_RETRY_ATTEMPTS)
        armar_item_fn=_fake_armar_item,
        topic_fn=lambda tid: topic if topic is not None else _TOPIC,
        seed_fn=lambda vid, sref: 123,
        generate_fn=generate_fn,
        grade_fn=grade_fn or _grade,
        is_hook_fn=lambda cap: cap == "ch01",
        data_uri_fn=lambda p: f"uri:{Path(p).name}",
        content_rejected_exc=_Rejected,
        now_ts="20260614_000000",
    )
    deps["_seen"] = seen
    assert issubclass(claude_helpers.ClaudeError, RuntimeError)
    return deps


def _call_fix(st, cap, img_name, pedido, deps):
    seen = deps.pop("_seen", None)
    return qa._fix_core(st, TID, cap, img_name, pedido, **deps), seen


def _item03(base, cap_n, idx, kind="img"):
    d = json.loads((base / "data" / "scripts" / "_steps" / TID / "03_visual.json").read_text(encoding="utf-8"))
    ch = next(c for c in d["chapters"] if c["chapter_number"] == cap_n)
    return ch["supplemental_image_prompts" if kind == "supp" else "image_prompts"][idx - 1]


def _item_vivo(base, cap_n, idx, kind="img"):
    d = json.loads((base / "data" / "scripts" / f"{TID}.json").read_text(encoding="utf-8"))
    ch = next(c for c in d["chapters"] if c["chapter_number"] == cap_n)
    return ch["supplemental_image_prompts" if kind == "supp" else "image_prompts"][idx - 1]


def test_casilleros_editables_resuelta():
    from script_engine import m03_imagenes_v3 as v3img
    assert v3img.CASILLEROS_EDITABLES == ("subject", "action", "setting", "lighting", "camera_angle",
                                          "lens_technique", "shot_scale", "text_in_image", "year")
    assert v3img.CASILLEROS_EDITABLES[:6] == v3img._PROSA
    assert "people_group" not in v3img.CASILLEROS_EDITABLES     # decisión c: fijo por código


def _bloque_handoff(titulo: str) -> str:
    md = HANDOFF_F59.read_text(encoding="utf-8")
    i = md.index(titulo)
    i = md.index("```\n", i) + 4
    return md[i:md.index("\n```", i)]


def test_pedidos_byte_a_byte_con_el_handoff():
    assert qa.PEDIDO_EDITAR_CASILLEROS == _bloque_handoff("## Pedido del editor de foto")
    assert qa.PEDIDO_EDITAR_MOVIMIENTO == _bloque_handoff("## Pedido del editor de movimiento")
    # placeholders: solo los del handoff (str.format no se traga ninguna llave de más)
    qa.PEDIDO_EDITAR_CASILLEROS.format(ancla="a", casilleros='{"x": 1}', pedido="p")
    qa.PEDIDO_EDITAR_MOVIMIENTO.format(segundos="8", voz_clip="v", movimiento="m", pedido="p")


def test_galeria_ignora_graded(tmp_path):
    """F59 A5 (chascada): los `*_graded.png` no son cuadros: n = crudos, anchors[i] en la foto i, sync_approx False."""
    build_topic(tmp_path)
    assets = tmp_path / "output" / TID / "assets"
    for m in range(1, 4):
        _png(assets / "ch02_flux" / f"ch02_img_{m:02d}_graded.png")
    _png(assets / "ch01_flux" / "ch01_supp_01_graded.png")
    st = qa.QAState(TID, base_dir=tmp_path)
    assert [p.name for p in st._flux_imgs("ch02")] == ["ch02_img_01.png", "ch02_img_02.png", "ch02_img_03.png"]
    assert [p.name for p in st._supp_imgs("ch01")] == ["ch01_supp_01.png", "ch01_supp_02.png"]
    c = st.cap(2)
    assert c["count"] == 3 and c["sync_approx"] is False
    anchors = ["alfa uno dos", "bravo tres cuatro", "charlie cinco seis"]
    for i, s in enumerate(c["segments"]):
        assert s["img_name"] == f"ch02_img_{i + 1:02d}.png" and s["anchor"] == anchors[i]
    assert next(x for x in st.caps() if x["cap"] == "ch02")["count"] == 3


def test_fix_resolve_entry_flux_and_supp(tmp_path):
    build_topic(tmp_path)
    st = qa.QAState(TID, base_dir=tmp_path)
    # flux _img_ → image_prompts[idx-1]  (lo de siempre, lo usan _reseed_core y sus tests)
    e = st.resolve_fix_entry("ch02_img_03.png")
    assert e and e["kind"] == "img" and e["idx"] == 3
    assert e["prompt"] == "p" and e["narration_anchor"] == "charlie cinco seis"
    # F59 A2.1: claves AGREGADAS
    assert isinstance(e["casilleros"], dict) and e["casilleros"]["people_group"] == ["miners"]
    assert e["anio"] == "1962" and e["anio_fuente"].startswith("1)") and e["beat"] == 2
    assert e["foto_madre_ref"] is None                     # [] → None
    assert st.resolve_fix_entry("ch03_img_01.png")["foto_madre_ref"] == ["__subject__"]
    # veo _supp_ → supplemental_image_prompts[idx-1]
    e2 = st.resolve_fix_entry("ch01_supp_02.png")
    assert e2 and e2["kind"] == "supp" and e2["idx"] == 2
    assert e2["narration_anchor"] == "supp 1-2" and isinstance(e2["casilleros"], dict)
    # basura / fuera de rango / traversal → None
    for bad in ("../x.png", "ch02_img_99.png", "ch02_img_03.PNG",
                "ch99_img_01.png", "ch02_clip_01.mp4", "ch02_img_03.png/../x"):
        assert st.resolve_fix_entry(bad) is None, f"debería rechazar {bad!r}"


def test_fix_resolve_entry_guion_viejo_sin_casilleros(tmp_path):
    build_topic(tmp_path, old_script=True)
    st = qa.QAState(TID, base_dir=tmp_path)
    e = st.resolve_fix_entry("ch02_img_03.png")
    assert e and e["prompt"] == "p" and e["casilleros"] is None and e["anio"] is None


def test_fix_core_casilleros_editados_armar_grade_guardado(tmp_path):
    """Camino feliz: Opus edita solo los casilleros editables → armar_item con el año y el contexto correctos → Seedream
    → grade → los 2 archivos guardados (con backups de los 4) · people_group intacto · scrub informado · baked fuera."""
    build_topic(tmp_path)
    st = qa.QAState(TID, base_dir=tmp_path)
    assets = st.assets_dir
    _png(assets / "ch02_flux" / "ch02_img_03_graded.png")
    work = tmp_path / "output" / TID / "_fase2b_work"
    work.mkdir(parents=True, exist_ok=True)
    (work / "ch02_flux_visual.mp4").write_bytes(b"OLDBAKED")
    antes = _item03(tmp_path, 2, 3)
    seen = {}

    def gen(prompt, art_profile, out_path, use_ultra, seed, foto_madre_data_uris=None):
        baks = sorted(p.name for p in (assets / "_qa_backups").iterdir())
        seen["backups_before"] = baks
        seen.update(prompt=prompt, art=art_profile, seed=seed, ultra=use_ultra, uris=foto_madre_data_uris, out=out_path)
        out_path.write_bytes(b"NEWPNGDATA")
        return {"path": out_path}

    deps = _fix_deps(gen, editar={"subject": "A Spanish miner facing the camera, brow furrowed",
                                  "action": "he stares straight into the lens, jaw clenched"})
    opus = deps["llamar_fn"]
    (ok, reason), g = _call_fix(st, "ch02", "ch02_img_03.png", "que mire a la cámara con el ceño fruncido", deps)
    assert ok is True, reason
    # Opus: UNA llamada, solo las claves editables en el JSON, esquema con esas mismas claves, ancla y pedido
    assert len(opus.calls) == 1
    c = opus.calls[0]
    enviados = json.loads(c["prompt"].split("CASILLEROS:\n", 1)[1].split("\n\nPEDIDO DE OMAR:", 1)[0])
    assert set(enviados) == set(qa_v3.CASILLEROS_EDITABLES) and "people_group" not in enviados and "gaze_interaction" not in enviados
    assert set(c["schema"]["properties"]) == set(enviados) and c["schema"]["required"] == list(enviados)
    assert "ANCLA:\ncharlie cinco seis" in c["prompt"] and c["prompt"].endswith("PEDIDO DE OMAR:\nque mire a la cámara con el ceño fruncido")
    # armar_item recibió el año del casillero, escala del beat 2 del cap 2, idioma del lugar y los grupos del canon
    assert seen["prompt"].startswith("A Spanish miner facing the camera, brow furrowed. he stares straight into the lens, jaw clenched. a mine, 1962.")
    assert "escala=True lang=en grupos=['miners'] shot=medium" in seen["prompt"]
    # Seedream: art_profile "", semilla por sujeto, sin foto madre (ref vacía), ch02 no es hook
    assert seen["art"] == "" and seen["seed"] == 123 and seen["ultra"] is False and seen["uris"] is None
    assert seen["out"] == assets / "ch02_flux" / "ch02_img_03.png"
    # backups de los 4 ANTES de generar
    assert seen["backups_before"] == sorted([
        "ch02_img_03.png.20260614_000000.bak.png", "ch02_img_03_graded.png.20260614_000000.bak.png",
        "03_visual.json.20260614_000000.bak.json", f"{TID}.json.20260614_000000.bak.json"])
    # grade sobre el crudo nuevo → _graded.png pisado
    assert g["grade"] == [assets / "ch02_flux" / "ch02_img_03.png"]
    assert (assets / "ch02_flux" / "ch02_img_03_graded.png").read_bytes() == b"GRADEDNEWPNGDATA"
    # guardado en 03_visual.json Y en el guion vivo: casilleros, raw_llm_prompt, prompt, anio, _f8_*
    for it in (_item03(tmp_path, 2, 3), _item_vivo(tmp_path, 2, 3)):
        assert it["subject"] == "A Spanish miner facing the camera, brow furrowed"
        assert it["prompt"] == seen["prompt"] and json.loads(it["raw_llm_prompt"])["subject"] == it["subject"]
        assert it["anio"] == "1962" and it["anio_fuente"] == "1) el casillero `year` del modelo"
        assert it["people_group"] == antes["people_group"] == ["miners"]            # intacto, por código
        assert it["gaze_interaction"] == antes["gaze_interaction"]                   # no editable, tal cual
        assert it["narration_anchor"] == "charlie cinco seis" and it["beat"] == 2    # el resto del ítem se conserva
        assert it["_f8_slots_scrub"] == ["action: HANDS_FACE: jaw clenched"]
    assert _item03(tmp_path, 2, 2)["subject"] == "A miner, bravo tres cuatro"           # el vecino no se toca
    # A2.8: el scrub informado en texto llano
    assert "casilleros editados: subject, action" in reason and "jaw clenched" in reason
    assert not (work / "ch02_flux_visual.mp4").exists()


def test_fix_core_anio_invalido_cae_al_del_item(tmp_path):
    build_topic(tmp_path)
    st = qa.QAState(TID, base_dir=tmp_path)
    seen = {}

    def gen(prompt, art_profile, out_path, use_ultra, seed, foto_madre_data_uris=None):
        seen["prompt"] = prompt
        out_path.write_bytes(b"X")
        return {}
    (ok, reason), _ = _call_fix(st, "ch02", "ch02_img_01.png", "x",
                                _fix_deps(gen, editar={"year": "mil novecientos", "lighting": "dusk"}))
    assert ok is True and ", 1962." in seen["prompt"]
    it = _item03(tmp_path, 2, 1)
    assert it["anio"] == "1962" and it["anio_fuente"] == "1) el casillero `year` del modelo"   # el respaldo del ítem
    assert it["year"] == "mil novecientos" and it["lighting"] == "dusk"


def test_fix_core_sin_scrub_informa_igual(tmp_path):
    build_topic(tmp_path)
    st = qa.QAState(TID, base_dir=tmp_path)

    def gen(prompt, art_profile, out_path, use_ultra, seed, foto_madre_data_uris=None):
        out_path.write_bytes(b"X")
        return {}
    (ok, reason), _ = _call_fix(st, "ch02", "ch02_img_01.png", "x", _fix_deps(gen, editar={"setting": "a dark gallery"}))
    assert ok is True and reason == "foto rehecha; casilleros editados: setting. El filtro de producción no sacó nada."


def test_fix_core_foto_madre_resuelta_contra_registry(tmp_path):
    build_topic(tmp_path)
    st = qa.QAState(TID, base_dir=tmp_path)
    seen = {}

    def gen(prompt, art_profile, out_path, use_ultra, seed, foto_madre_data_uris=None):
        seen["uris"] = foto_madre_data_uris
        out_path.write_bytes(b"X")
        return {}
    (ok, _), _ = _call_fix(st, "ch03", "ch03_img_01.png", "x", _fix_deps(gen))
    assert ok is True and seen["uris"] == ["uri:madre.png"]        # ref __subject__ → path del registry → data URI


def test_fix_core_supp_uses_ultra_for_hook(tmp_path):
    build_topic(tmp_path)
    st = qa.QAState(TID, base_dir=tmp_path)
    seen = {}

    def gen(prompt, art_profile, out_path, use_ultra, seed, foto_madre_data_uris=None):
        seen["ultra"] = use_ultra
        out_path.write_bytes(b"X")
        return {}
    (ok, _), _ = _call_fix(st, "ch01", "ch01_supp_01.png", "cambio", _fix_deps(gen))
    assert ok is True and seen["ultra"] is True  # ch01 = hook → use_ultra (cosmético hoy)
    assert _item_vivo(tmp_path, 1, 1, "supp")["subject"] == "A miner looking at the camera"


def test_fix_core_guion_viejo_no_llama_a_opus(tmp_path):
    build_topic(tmp_path, old_script=True)
    st = qa.QAState(TID, base_dir=tmp_path)

    def gen(*a, **k):
        raise AssertionError("no debe generar con guion viejo")
    deps = _fix_deps(gen)
    (ok, reason), _ = _call_fix(st, "ch02", "ch02_img_03.png", "x", deps)
    assert (ok, reason) == (False, "guion viejo: correr m03 de nuevo") and deps["llamar_fn"].calls == []


def test_fix_core_tres_validaciones_fallidas_no_genera(tmp_path):
    """Opus devuelve 3 veces un objeto con un casillero de prosa vacío → MAX_RETRY_ATTEMPTS llamadas, nada generado,
    ningún archivo tocado."""
    from script_engine import m03_visual
    build_topic(tmp_path)
    st = qa.QAState(TID, base_dir=tmp_path)
    calls = []

    def opus_malo(prompt, system_instruction=None, response_schema=None, description=None, **_):
        calls.append(prompt)
        cas = json.loads(prompt.split("CASILLEROS:\n", 1)[1].split("\n\nPEDIDO DE OMAR:", 1)[0])
        return {**cas, "subject": "   "}

    def gen(*a, **k):
        raise AssertionError("no debe generar si el editor no pasó el validador")
    antes = _item03(tmp_path, 2, 3)
    (ok, reason), _ = _call_fix(st, "ch02", "ch02_img_03.png", "x", _fix_deps(gen, llamar_fn=opus_malo))
    assert ok is False and "casillero de prosa vacío" in reason and len(calls) == m03_visual.MAX_RETRY_ATTEMPTS
    assert "RETRY 2/" in calls[1] and _item03(tmp_path, 2, 3) == antes
    assert not (st.assets_dir / "_qa_backups").exists()


def test_fix_core_validador_rechaza_claves_de_mas_o_de_menos(tmp_path):
    build_topic(tmp_path)
    st = qa.QAState(TID, base_dir=tmp_path)

    def opus_people(prompt, **_):
        cas = json.loads(prompt.split("CASILLEROS:\n", 1)[1].split("\n\nPEDIDO DE OMAR:", 1)[0])
        return {**cas, "people_group": []}         # intenta tocar people_group → sobra

    def opus_lista(prompt, **_):
        return [{"subject": "x"}]                   # no es objeto

    def gen(*a, **k):
        raise AssertionError("no debe generar")
    (ok, reason), _ = _call_fix(st, "ch02", "ch02_img_03.png", "x", _fix_deps(gen, llamar_fn=opus_people))
    assert ok is False and "sobran ['people_group']" in reason
    (ok, reason), _ = _call_fix(st, "ch02", "ch02_img_03.png", "x", _fix_deps(gen, llamar_fn=opus_lista))
    assert ok is False and "no es un objeto" in reason


def test_fix_core_claude_error(tmp_path):
    import claude_helpers
    build_topic(tmp_path)
    st = qa.QAState(TID, base_dir=tmp_path)

    def opus_caido(prompt, **_):
        raise claude_helpers.ClaudeError("429 overloaded")

    def gen(*a, **k):
        raise AssertionError("no debe generar")
    (ok, reason), _ = _call_fix(st, "ch02", "ch02_img_03.png", "x", _fix_deps(gen, llamar_fn=opus_caido))
    assert ok is False and reason == "Opus no editó los casilleros: 429 overloaded"


def test_fix_core_content_rejected_no_guarda(tmp_path):
    build_topic(tmp_path)
    st = qa.QAState(TID, base_dir=tmp_path)
    antes = _item03(tmp_path, 2, 3)

    def gen(*a, **k):
        raise _Rejected("content_policy violation")
    (ok, reason), _ = _call_fix(st, "ch02", "ch02_img_03.png", "x", _fix_deps(gen))
    assert ok is False and reason.startswith("filtro:")
    assert _item03(tmp_path, 2, 3) == antes and _item_vivo(tmp_path, 2, 3) == antes   # el guion no se tocó


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
#  Zona 1.5 — fix de clip (/fix_clip) · F59 A3: editor de movimiento + cadena de producción
# ─────────────────────────────────────────────────────────────────

def _opus_movimiento(movimiento):
    calls = []

    def llamar(prompt, system_instruction=None, response_schema=None, description=None, **_):
        calls.append({"prompt": prompt, "schema": response_schema})
        return {"movimiento": movimiento}
    llamar.calls = calls
    return llamar


def _clipfix_deps(generate_clip_fn, *, movimiento="The camera holds completely still; fine dust rises slowly.",
                  llamar_fn=None, foto_final_fn=None):
    """Deps inyectadas para _clipfix_core (contrato F59 A3): Opus edita el movimiento, la foto final de producción se
    hace (o se reusa) y el clip sale por _generate_clip (G → K)."""
    from script_engine import m03_visual

    def _final(foto_inicial, image_prompt, voz_clip, out_path, *, use_ultra=False):
        if out_path.exists():
            return {"path": out_path, "ssim": 0.9, "instruccion": None, "motivo": "reusada: ya existía"}
        out_path.write_bytes(b"FINAL")
        return {"path": out_path, "ssim": 0.8, "instruccion": f"edit: {image_prompt} / {voz_clip}", "motivo": None}
    return dict(
        llamar_fn=llamar_fn or _opus_movimiento(movimiento),
        retry_fn=m03_visual._call_with_validation_retry,
        foto_final_fn=foto_final_fn or _final,
        generate_clip_fn=generate_clip_fn,
        is_hook_fn=lambda cap: cap == "ch01",
        content_rejected_exc=_Rejected,
        now_ts="20260614_000000",
    )


def _cap_vivo(base, cap_n):
    d = json.loads((base / "data" / "scripts" / f"{TID}.json").read_text(encoding="utf-8"))
    return next(c for c in d["chapters"] if c["chapter_number"] == cap_n)


def _cap03(base, cap_n):
    d = json.loads((base / "data" / "scripts" / "_steps" / TID / "03_visual.json").read_text(encoding="utf-8"))
    return next(c for c in d["chapters"] if c["chapter_number"] == cap_n)


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
    assert e["art_profile"] == "doc" and e["subject_ref"] == "establishing_shot"
    # F59 A3.1: AGREGA voz_clip y _final (None si no existe)
    assert e["voz_clip"] == "voz del clip uno" and e["_final"] is None
    _png(st.assets_dir / "ch01_veo" / "ch01_img_01_final.png")
    assert st.resolve_clip_entry("ch01")["_final"].endswith("ch01_img_01_final.png")
    # guion viejo → voz_clip ""
    build_topic(tmp_path, old_script=True)
    assert qa.QAState(TID, base_dir=tmp_path).resolve_clip_entry("ch07")["voz_clip"] == ""
    # flux cap → no tiene clip → None
    assert st.resolve_clip_entry("ch02") is None
    # cap inexistente / basura → None
    assert st.resolve_clip_entry("ch99") is None
    assert st.resolve_clip_entry("../x") is None


def test_clipfix_core_solo_movimiento_foto_inicial_intacta(tmp_path):
    """F59: la foto inicial NO se toca; el motor recibe el movimiento nuevo, voz_clip y la foto final; backup del mp4
    antes; el movimiento se guarda en 03_visual.json y en el guion vivo; baked invalidado."""
    build_topic(tmp_path)
    st = qa.QAState(TID, base_dir=tmp_path)
    work = tmp_path / "output" / TID / "_fase2b_work"
    work.mkdir(parents=True, exist_ok=True)
    (work / "ch01_hybrid_visual.mp4").write_bytes(b"OLD")
    inicial = st.assets_dir / "ch01_veo" / "ch01_img_01.png"
    inicial_bytes = inicial.read_bytes()
    seen = {}

    def clip(foto, movimiento, out_clip, *, image_prompt="", ancla="", foto_final=None, log=None):
        seen.update(foto=foto, mov=movimiento, out=out_clip, image_prompt=image_prompt, ancla=ancla, final=foto_final)
        seen["backups_before"] = sorted(p.name for p in (st.assets_dir / "_qa_backups").iterdir())
        out_clip.write_bytes(b"NEWCLIP")
        if log is not None:
            log.append({"clip": out_clip.name, "motor": "gemini_omni_flash", "rechazos": [], "segundos": 8.0, "usd": 0.1})
        return out_clip
    deps = _clipfix_deps(clip)
    opus = deps["llamar_fn"]
    ok, reason = qa._clipfix_core(st, TID, "ch01", "cámara quieta, solo sube el polvo, lento", **deps)
    assert ok is True, reason
    # Opus: segundos de producción («8»), VOZ, MOVIMIENTO aprobado y el pedido; esquema {"movimiento": string}
    p = opus.calls[0]["prompt"]
    assert p.startswith("Editás el movimiento de un clip de 8 segundos")
    assert "VOZ:\nvoz del clip uno\n\nMOVIMIENTO:\nStatic camera with subtle upward drift over the skyline\n\n" in p
    assert p.endswith("PEDIDO DE OMAR:\ncámara quieta, solo sube el polvo, lento")
    assert opus.calls[0]["schema"]["required"] == ["movimiento"]
    # el motor: foto inicial, movimiento NUEVO, ancla = voz_clip, image_prompt, foto final hecha
    assert seen["foto"] == inicial and seen["mov"] == "The camera holds completely still; fine dust rises slowly."
    assert seen["ancla"] == "voz del clip uno" and seen["image_prompt"].startswith("A wide panoramic")
    assert seen["final"] == st.assets_dir / "ch01_veo" / "ch01_img_01_final.png" and seen["final"].read_bytes() == b"FINAL"
    assert seen["out"] == st.assets_dir / "ch01_veo" / "ch01_clip_01.mp4"
    # backup del mp4 ANTES; la foto inicial intacta y SIN backup (no se tocó)
    assert seen["backups_before"] == ["ch01_clip_01.mp4.20260614_000000.bak.mp4"]
    assert inicial.read_bytes() == inicial_bytes
    assert (st.assets_dir / "ch01_veo" / "ch01_clip_01.mp4").read_bytes() == b"NEWCLIP"
    # movimiento guardado en los dos archivos (con sus backups), foto inicial/image_prompt sin cambios
    for c in (_cap03(tmp_path, 1), _cap_vivo(tmp_path, 1)):
        assert c["video_prompt"] == "The camera holds completely still; fine dust rises slowly."
        assert c["image_prompt"].startswith("A wide panoramic") and c["voz_clip"] == "voz del clip uno"
    assert (st.assets_dir / "_qa_backups" / "03_visual.json.20260614_000000.bak.json").exists()
    assert (st.assets_dir / "_qa_backups" / f"{TID}.json.20260614_000000.bak.json").exists()
    assert not (work / "ch01_hybrid_visual.mp4").exists()
    assert reason == "clip rehecho con el movimiento nuevo (motor: gemini_omni_flash)"


def test_clipfix_core_reusa_final_existente(tmp_path):
    build_topic(tmp_path)
    st = qa.QAState(TID, base_dir=tmp_path)
    final = st.assets_dir / "ch07_veo" / "ch07_img_01_final.png"
    final.write_bytes(b"VIEJA")
    seen = {}

    def clip(foto, movimiento, out_clip, **kw):
        seen["final"] = kw["foto_final"]
        out_clip.write_bytes(b"NEW")
        return out_clip
    ok, _ = qa._clipfix_core(st, TID, "ch07", "x", **_clipfix_deps(clip))
    assert ok is True and seen["final"] == final and final.read_bytes() == b"VIEJA"     # reusada, no rehecha


def test_clipfix_core_rechazo_g_y_k_mp4_intacto(tmp_path):
    build_topic(tmp_path)
    st = qa.QAState(TID, base_dir=tmp_path)
    mp4 = st.assets_dir / "ch07_veo" / "ch07_clip_01.mp4"
    antes = _cap_vivo(tmp_path, 7)["video_prompt"]

    def clip(*a, **k):
        raise _Rejected("gemini_omni_flash: policy 422 | kling: CAC rejected")
    ok, reason = qa._clipfix_core(st, TID, "ch07", "x", **_clipfix_deps(clip))
    assert (ok, reason) == (False, "filtro: gemini_omni_flash: policy 422 | kling: CAC rejected")
    assert mp4.read_bytes() == b"\x00" * 8                          # el mp4 viejo intacto
    assert _cap_vivo(tmp_path, 7)["video_prompt"] == antes == _cap03(tmp_path, 7)["video_prompt"]


def test_clipfix_core_guion_viejo_sin_voz_clip(tmp_path):
    build_topic(tmp_path, old_script=True)
    st = qa.QAState(TID, base_dir=tmp_path)
    assert st.resolve_clip_entry("ch01") is not None          # /fix_clip NO devuelve 400: el cap sí tiene clip

    def clip(*a, **k):
        raise AssertionError("no debe generar")
    deps = _clipfix_deps(clip)
    ok, reason = qa._clipfix_core(st, TID, "ch01", "x", **deps)
    assert (ok, reason) == (False, "guion viejo: correr m03 de nuevo") and deps["llamar_fn"].calls == []


def test_clipfix_core_validacion_fallida_no_genera(tmp_path):
    from script_engine import m03_visual
    build_topic(tmp_path)
    st = qa.QAState(TID, base_dir=tmp_path)
    calls = []

    def opus_malo(prompt, **_):
        calls.append(prompt)
        return {"movimiento": "  ", "extra": 1}

    def clip(*a, **k):
        raise AssertionError("no debe generar")
    ok, reason = qa._clipfix_core(st, TID, "ch01", "x", **_clipfix_deps(clip, llamar_fn=opus_malo))
    assert ok is False and reason.startswith("el editor no devolvió un movimiento válido") and len(calls) == m03_visual.MAX_RETRY_ATTEMPTS
    assert not (st.assets_dir / "_qa_backups").exists()


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
