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


def build_topic(base: Path, *, matching_anchors: bool = True) -> str:
    """Crea el topic sintético. matching_anchors=False rompe el match anchor→words
    (anchors que NO aparecen en el audio) para forzar el reparto uniforme."""
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
        if n in (1, 7):
            chapters.append({
                "chapter_number": n,
                "render_engine": "veo",
                "narration": f"narración cap {n}",
                "narration_anchor": f"apertura del cap {n}",
                "supplemental_image_prompts": [
                    {"prompt": "x", "narration_anchor": f"supp {n}-1"},
                    {"prompt": "y", "narration_anchor": f"supp {n}-2"},
                ],
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
            for m in range(1, 3):
                _png(assets / f"{cid}_flux" / f"{cid}_supp_{m:02d}.png")
            words = _words([f"apertura del cap {n}"])
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

def test_caps_seven_single_in_1_and_7(tmp_path):
    build_topic(tmp_path)
    st = qa.QAState(TID, base_dir=tmp_path)
    caps = st.caps()
    assert len(caps) == 7, f"esperaba 7 caps, hay {len(caps)}"
    by_num = {c["num"]: c for c in caps}
    assert by_num[1]["single"] is True
    assert by_num[7]["single"] is True
    for n in (2, 3, 4, 5, 6):
        assert by_num[n]["single"] is False, f"cap {n} no debería ser single"
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


def test_veo_cap_gallery_and_clip(tmp_path):
    build_topic(tmp_path)
    st = qa.QAState(TID, base_dir=tmp_path)
    payload = st.cap(1)
    assert payload["single"] is True
    assert payload["clip_url"] == "/clip?cap=ch01"
    assert len(payload["gallery"]) == 2
    assert payload["gallery"][0]["anchor"] == "supp 1-1"
    # resolve_clip apunta al mp4 real
    assert st.resolve_clip("ch01") is not None
    assert st.resolve_clip("ch02") is None  # flux no tiene clip


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
