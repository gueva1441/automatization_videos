"""
test_m09_review_server.py — Tests SIN red del form de review (m09a, F58: paquetes).

Ejercen ReviewState (la lógica; el Handler HTTP es capa fina). Monkeypatch de las funciones de m09_packaging que
llaman a Opus o al motor de imagen para no tocar la red.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

from PIL import Image

from script_engine import m09_packaging as pkg
from script_engine import m09_review_server as srv


def _section(t): print("\n" + "─" * 68 + f"\n{t}")


def _setup(tmp: Path):
    """Apunta pkg._publish_dir / _candidates_dir / _assets_dir a un tmp y devuelve (pub, cand, assets)."""
    pub = tmp / "publish"; cand = pub / "thumb_candidates"; assets = tmp / "assets"
    cand.mkdir(parents=True); assets.mkdir()
    pkg._publish_dir = lambda tid: pub
    pkg._candidates_dir = lambda tid: cand
    pkg._assets_dir = lambda tid: assets
    pkg._final_mp4 = lambda tid: tmp / "video_final_v3_ZOOM.mp4"
    return pub, cand, assets


def _orig():
    return (pkg._publish_dir, pkg._candidates_dir, pkg._assets_dir, pkg._final_mp4)


def _restore(o):
    pkg._publish_dir, pkg._candidates_dir, pkg._assets_dir, pkg._final_mp4 = o


def _meta(n=2):
    return {"topic_id": "TID", "stage": "candidates", "descripcion": "desc", "tags": ["a", "b"], "avisos": [],
            "paquetes": [{"n": i, "estrategia": i, "titulo": f"Título {i}", "dato_ids": ["D01"], "datos": {"D01": "dato uno"},
                          "texto": f"TEXTO {i}", "cap_que_paga": 3, "ancla": f"Ancla {i}.", "avisos": ["⚠ cifra sin dato: 9"] if i == 1 else [],
                          "foto": f"paquete_{i:02d}_base.png", "base": f"paquete_{i:02d}_base.png",
                          "miniatura": f"paquete_{i:02d}.png", "motivo_sin_foto": None} for i in range(1, n + 1)]}


def test_state():
    _section("1· /state (snapshot) paquetes desde metadata.json + bases del video")
    o = _orig()
    tmp = Path(tempfile.mkdtemp())
    try:
        pub, cand, assets = _setup(tmp)
        for i in (1, 2):
            Image.new("RGB", (1280, 720), (40, 40, 40)).save(cand / f"paquete_{i:02d}_base.png")
            Image.new("RGB", (1280, 720), (40, 40, 40)).save(cand / f"paquete_{i:02d}.png")
        (assets / "ch02_flux").mkdir()
        Image.new("RGB", (8, 8)).save(assets / "ch02_flux" / "ch02_img_01.png")
        Image.new("RGB", (8, 8)).save(assets / "ch02_flux" / "ch02_img_01_graded.png")
        (pub / "metadata.json").write_text(json.dumps(_meta(), ensure_ascii=False), encoding="utf-8")
        st = srv.ReviewState("TID").snapshot()
    finally:
        _restore(o)
    ok = True
    p1 = st["paquetes"][0]
    checks = [
        ([p["n"] for p in st["paquetes"]] == [1, 2], "2 paquetes en orden"),
        (p1["titulo"] == "Título 1" and p1["chars"] == len("Título 1"), "título con cuenta de caracteres"),
        (p1["texto"] == "TEXTO 1" and p1["datos"] == {"D01": "dato uno"} and p1["cap_que_paga"] == 3, "texto, datos, cap_que_paga"),
        (p1["ancla"] == "Ancla 1." and p1["avisos"] == ["⚠ cifra sin dato: 9"], "ancla y avisos"),
        (p1["img"] == "/img/paquete_01.png", "la miniatura compuesta es la imagen del paquete"),
        (st["bases"] == ["assets/ch02_flux/ch02_img_01_graded.png"], f"bases del video (graded): {st['bases']}"),
        (st["descripcion"] == "desc" and st["tags"] == ["a", "b"], "descripción y tags"),
        (st["generating"] is False, "generating False"),
    ]
    for cond, label in checks:
        if not cond:
            ok = False; print(f"  ✗ {label}")
        else:
            print(f"  ✓ {label}")
    return ok


def test_compose_versioned():
    _section("2· compose(n) versionado (thumb_final_NN 1280×720) + CHECKLIST + on_compose")
    o = _orig()
    tmp = Path(tempfile.mkdtemp())
    try:
        pub, cand, assets = _setup(tmp)
        Image.new("RGB", (1080, 1920), (30, 30, 30)).save(cand / "paquete_01_base.png")
        Image.new("RGB", (1280, 720), (30, 30, 30)).save(cand / "paquete_02_base.png")
        (pub / "metadata.json").write_text(json.dumps(_meta(), ensure_ascii=False), encoding="utf-8")
        packaged = []
        state = srv.ReviewState("TID", on_compose=lambda name: packaged.append(name))
        r1 = state.compose(1, "center")
        r2 = state.compose(2, "top", size_factor=0.8)
        bad = state.compose(9)
        ok = True
        if r1.get("thumb") != "thumb_final_01.png" or r2.get("thumb") != "thumb_final_02.png":
            ok = False; print(f"  ✗ versionado: {r1} {r2}")
        else:
            print("  ✓ versionado thumb_final_01 / _02")
        im = Image.open(pub / "thumb_final_01.png")
        if im.size != (1280, 720):
            ok = False; print(f"  ✗ tamaño {im.size}")
        else:
            print("  ✓ thumb_final_01 es 1280×720")
        if not (pub / "CHECKLIST_PUBLICACION.md").exists():
            ok = False; print("  ✗ no escribió CHECKLIST")
        else:
            print("  ✓ CHECKLIST escrito")
        meta = json.loads((pub / "metadata.json").read_text(encoding="utf-8"))
        if meta.get("titulo_elegido") != "Título 2" or meta.get("stage") != "final":
            ok = False; print(f"  ✗ metadata final: {meta.get('titulo_elegido')!r} {meta.get('stage')!r}")
        else:
            print("  ✓ metadata final con el título del paquete 2")
        if packaged != ["thumb_final_01.png", "thumb_final_02.png"]:
            ok = False; print(f"  ✗ on_compose: {packaged}")
        else:
            print("  ✓ on_compose llamado por cada COMPONER")
        if "error" not in bad:
            ok = False; print("  ✗ paquete inexistente no dio error")
        else:
            print(f"  ✓ paquete inexistente → error en form (no crash): {bad['error'][:50]}")
    finally:
        _restore(o)
    return ok


def test_first_batch_and_rehacer_fake():
    _section("3· primera tanda / 3 paquetes nuevos y rehacer foto con fakes + guard de concurrencia")
    o = _orig()
    orig_fn = (pkg.run_candidates, pkg.rehacer_foto)
    tmp = Path(tempfile.mkdtemp())
    try:
        pub, cand, assets = _setup(tmp)
        calls = []

        def fake_candidates(tid, video_path=None, review=False):
            calls.append(("candidates", tid, video_path))
            (pub / "metadata.json").write_text(json.dumps(_meta(3), ensure_ascii=False), encoding="utf-8")

        def fake_rehacer(tid, n):
            calls.append(("rehacer", tid, n))
            return {}
        pkg.run_candidates = fake_candidates
        pkg.rehacer_foto = fake_rehacer

        state = srv.ReviewState("TID", video_path="/v.mp4")
        state._run(pkg.run_candidates, state.tid, state.video_path)   # síncrono (sin thread) para el test
        state._run(pkg.rehacer_foto, state.tid, 2)
        ok = True
        if calls != [("candidates", "TID", "/v.mp4"), ("rehacer", "TID", 2)]:
            ok = False; print(f"  ✗ llamadas: {calls}")
        else:
            print("  ✓ run_candidates(tid, video_path) y rehacer_foto(tid, n) llamados")
        if len(state.snapshot()["paquetes"]) != 3:
            ok = False; print("  ✗ el snapshot no ve los 3 paquetes")
        else:
            print("  ✓ snapshot ve los 3 paquetes de la tanda")
        if state.generating is not False or state.last_error is not None:
            ok = False; print(f"  ✗ estado tras correr: generating={state.generating} err={state.last_error}")
        else:
            print("  ✓ generating reseteado, sin error")
        # error → last_error, generating vuelve a False
        def boom(*a):
            raise RuntimeError("se rompió")
        state._run(boom)
        if state.last_error != "RuntimeError: se rompió" or state.generating:
            ok = False; print(f"  ✗ error no capturado: {state.last_error}")
        else:
            print("  ✓ excepción → last_error literal")
        state.generating = True
        if state.start_first_batch() is not False or state.start_rehacer_foto(1) is not False:
            ok = False; print("  ✗ start_* no respetó busy")
        else:
            print("  ✓ start_first_batch / start_rehacer_foto respetan busy")
        state.generating = False
    finally:
        _restore(o)
        pkg.run_candidates, pkg.rehacer_foto = orig_fn
    return ok


def test_rev_and_resolve_image():
    _section("4· /state rev cambia SOLO cuando cambian los paquetes; /img solo dentro de assets/candidates/publish")
    o = _orig()
    tmp = Path(tempfile.mkdtemp())
    try:
        pub, cand, assets = _setup(tmp)
        Image.new("RGB", (1280, 720), (20, 20, 20)).save(cand / "paquete_01.png")
        (pub / "metadata.json").write_text(json.dumps(_meta(1), ensure_ascii=False), encoding="utf-8")
        (assets / "ch02_flux").mkdir()
        Image.new("RGB", (8, 8)).save(assets / "ch02_flux" / "ch02_img_01_graded.png")
        (tmp / "fuera.png").write_bytes(b"x")
        st = srv.ReviewState("TID")
        snap = st.snapshot()
        rev_a = snap.get("rev")
        ok = True
        if not rev_a:
            ok = False; print("  ✗ /state no incluye rev")
        else:
            print("  ✓ /state incluye rev")
        if st.snapshot()["rev"] != rev_a:
            ok = False; print("  ✗ rev inestable sin cambios")
        else:
            print("  ✓ rev estable cuando nada cambia")
        st.generating = True
        rev_gen = st.snapshot()["rev"]; st.generating = False
        if rev_gen != rev_a:
            ok = False; print("  ✗ generating cambió rev")
        else:
            print("  ✓ generating NO cambia rev")
        (pub / "metadata.json").write_text(json.dumps(_meta(2), ensure_ascii=False), encoding="utf-8")
        if st.snapshot()["rev"] == rev_a:
            ok = False; print("  ✗ paquete nuevo no cambió rev")
        else:
            print("  ✓ paquete nuevo cambia rev")
        # resolve_image: candidatas, publish y assets/ sí; fuera, no
        r = [st.resolve_image("paquete_01.png"), st.resolve_image("assets/ch02_flux/ch02_img_01_graded.png"),
             st.resolve_image("../fuera.png"), st.resolve_image("assets/../fuera.png"), st.resolve_image("fuera.png"),
             st.resolve_image("metadata.json")]
        if r[0] != cand / "paquete_01.png" or r[1] != assets / "ch02_flux" / "ch02_img_01_graded.png":
            ok = False; print(f"  ✗ no resolvió las válidas: {r[:2]}")
        elif any(x is not None for x in r[2:]):
            ok = False; print(f"  ✗ sirvió algo fuera de las 3 carpetas: {r[2:]}")
        else:
            print("  ✓ /img sirve solo thumb_candidates/, publish/ y assets/ (nada afuera, nada que no sea imagen)")
    finally:
        _restore(o)
    return ok


def main() -> int:
    print("=" * 68 + "\n  TESTS m09 review server (sin red)\n" + "=" * 68)
    results = {
        "state": test_state(),
        "compose_versioned": test_compose_versioned(),
        "first_batch_and_rehacer_fake": test_first_batch_and_rehacer_fake(),
        "rev_and_resolve_image": test_rev_and_resolve_image(),
    }
    print("\n" + "=" * 68)
    for k, v in results.items():
        print(f"  {'PASS ✅' if v else 'FAIL ❌'}  {k}")
    print("=" * 68)
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
