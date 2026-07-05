"""
test_m09_review_server.py — Tests SIN red del form de review (m09a v2, chat 56).

Ejercen ReviewState (la lógica; el Handler HTTP es capa fina). Monkeypatch de las
funciones Gemini/Flux de m09_packaging para no tocar la red.
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
    """Apunta pkg._publish_dir / _candidates_dir a un tmp y devuelve (pub, cand)."""
    pub = tmp / "publish"; cand = pub / "thumb_candidates"
    cand.mkdir(parents=True)
    pkg._publish_dir = lambda tid: pub
    pkg._candidates_dir = lambda tid: cand
    pkg._final_mp4 = lambda tid: tmp / "video_final_v3_ZOOM.mp4"
    return pub, cand


def test_state():
    _section("1· /state (snapshot) inventario desde carpeta sintética")
    orig = (pkg._publish_dir, pkg._candidates_dir, pkg._final_mp4)
    tmp = Path(tempfile.mkdtemp())
    try:
        pub, cand = _setup(tmp)
        Image.new("RGB", (1080, 1920), (30, 30, 30)).save(cand / "existing_01.png")  # vertical
        Image.new("RGB", (1280, 720), (40, 40, 40)).save(cand / "fresh_01.png")     # 16:9
        (pub / "hero_iterations.json").write_text(json.dumps([
            {"iteration": 0, "hero_prompt": "un prompt", "subject": "la novia espectral", "files": ["fresh_01.png"]}
        ]), encoding="utf-8")
        (pub / "metadata.json").write_text(json.dumps(
            {"titulos": ["T1", "T2", "T3"], "overlays": ["O1", "O2", "O3"]}), encoding="utf-8")
        st = srv.ReviewState("TID").snapshot()
    finally:
        pkg._publish_dir, pkg._candidates_dir, pkg._final_mp4 = orig
    ok = True
    names = [c["name"] for c in st["candidates"]]
    checks = [
        (names == ["existing_01.png", "fresh_01.png"], f"candidatas ordenadas: {names}"),
        (next(c for c in st["candidates"] if c["name"] == "existing_01.png")["vertical"], "marca vertical 9:16"),
        (next(c for c in st["candidates"] if c["name"] == "fresh_01.png")["subject"] == "la novia espectral", "subject de la iteración"),
        (st["hero"]["subject"] == "la novia espectral" and st["hero"]["prompt"] == "un prompt", "hero actual"),
        (st["titles"] == ["T1", "T2", "T3"], "3 títulos de metadata"),
        (st["overlays"] == ["O1", "O2", "O3"], "3 overlays de metadata"),
        (st["generating"] is False, "generating False"),
    ]
    for cond, label in checks:
        if not cond:
            ok = False; print(f"  ✗ {label}")
        else:
            print(f"  ✓ {label}")
    return ok


def test_compose_versioned():
    _section("2· compose versionado (thumb_final_NN 1280×720)")
    orig = (pkg._publish_dir, pkg._candidates_dir, pkg._final_mp4)
    tmp = Path(tempfile.mkdtemp())
    try:
        pub, cand = _setup(tmp)
        Image.new("RGB", (1080, 1920), (30, 30, 30)).save(cand / "existing_01.png")
        (pub / "metadata.json").write_text(json.dumps(
            {"titulos": ["Título uno", "Título dos", "Título tres"], "descripcion": "desc", "tags": ["a", "b"]}
        ), encoding="utf-8")
        state = srv.ReviewState("TID")
        # title llega STRING desde el combobox (sugerencia elegida o escrita a mano)
        r1 = state.compose("existing_01.png", "MUERTE EN X", "Título dos", "center")
        r2 = state.compose("existing_01.png", "OTRA VEZ", "Título a mano", "top")
        bad = state.compose("existing_01.png", "", "Título uno", "center")  # texto vacío → error
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
        if "error" not in bad:
            ok = False; print("  ✗ texto vacío no dio error")
        else:
            print(f"  ✓ texto vacío → error en form (no crash): {bad['error'][:40]}")
    finally:
        pkg._publish_dir, pkg._candidates_dir, pkg._final_mp4 = orig
    return ok


def test_generate_fake():
    _section("3· generate (hero+frescas) con fakes Gemini/Flux + guard de concurrencia")
    orig = (pkg._publish_dir, pkg._candidates_dir, pkg._final_mp4,
            pkg.generate_hero_prompt, pkg._render_fresh_from_hero, pkg._load_canonical, pkg.FRESH_THUMBS)
    tmp = Path(tempfile.mkdtemp())
    try:
        pub, cand = _setup(tmp)
        pkg._load_canonical = lambda tid: {"video_title": "x", "chapters": []}
        # HANDOFF_137d §4: generate_hero_prompt devuelve TRES conceptos distintos
        pkg.generate_hero_prompt = lambda canonical: [
            {"prompt": f"PROMPT FAKE {i}", "subject": f"SUJETO FAKE {i}"} for i in range(3)]

        def _fake_render(hero, cand_dir, count, start):
            files = []
            for k in range(count):
                idx = start + k
                Image.new("RGB", (1280, 720), (10, 10, 10)).save(cand_dir / f"fresh_{idx:02d}.png")
                files.append(f"fresh_{idx:02d}.png")
            return [f"- {f} ok" for f in files], files
        pkg._render_fresh_from_hero = _fake_render
        pkg.FRESH_THUMBS = 3

        state = srv.ReviewState("TID")
        state._run_generate(None)  # síncrono (sin thread) para el test
        ok = True
        hist = json.loads((pub / "hero_iterations.json").read_text(encoding="utf-8"))
        concepts = hist[0].get("concepts") if hist else None
        if len(hist) != 1 or not concepts or concepts[0]["subject"] != "SUJETO FAKE 0":
            ok = False; print(f"  ✗ iteración no registrada (concepts): {hist}")
        else:
            print("  ✓ iteración registrada (concepts alineados a files)")
        if len(hist[0]["files"]) != 3:
            ok = False; print(f"  ✗ esperaba 3 frescas (1 por concepto), {hist[0]['files']}")
        else:
            print("  ✓ 3 frescas generadas (1 por concepto)")
        if state.generating is not False:
            ok = False; print("  ✗ generating no se reseteó")
        else:
            print("  ✓ generating reseteado a False")
        # guard de concurrencia
        state.generating = True
        if state.start_generate(None) is not False:
            ok = False; print("  ✗ start_generate no respetó busy")
        else:
            print("  ✓ start_generate respeta busy (no encola doble)")
        state.generating = False
    finally:
        (pkg._publish_dir, pkg._candidates_dir, pkg._final_mp4,
         pkg.generate_hero_prompt, pkg._render_fresh_from_hero, pkg._load_canonical, pkg.FRESH_THUMBS) = orig
    return ok


def test_rev():
    _section("4· /state rev cambia SOLO cuando el inventario cambia (anti-flasheo)")
    orig = (pkg._publish_dir, pkg._candidates_dir, pkg._final_mp4)
    tmp = Path(tempfile.mkdtemp())
    try:
        pub, cand = _setup(tmp)
        Image.new("RGB", (1280, 720), (20, 20, 20)).save(cand / "fresh_01.png")
        st = srv.ReviewState("TID")
        snap = st.snapshot()
        rev_a = snap.get("rev")
        ok = True
        if not rev_a:
            ok = False; print("  ✗ /state no incluye rev")
        else:
            print("  ✓ /state incluye rev")
        # re-snapshot sin cambios → mismo rev
        if st.snapshot()["rev"] != rev_a:
            ok = False; print("  ✗ rev inestable sin cambios")
        else:
            print("  ✓ rev estable cuando el inventario no cambia")
        # generating toggle NO cambia rev (rev es del inventario, no del estado de corrida)
        st.generating = True
        rev_gen = st.snapshot()["rev"]; st.generating = False
        if rev_gen != rev_a:
            ok = False; print("  ✗ generating cambió rev")
        else:
            print("  ✓ generating NO cambia rev")
        # nueva candidata → rev cambia
        Image.new("RGB", (1280, 720), (30, 30, 30)).save(cand / "fresh_02.png")
        if st.snapshot()["rev"] == rev_a:
            ok = False; print("  ✗ nueva candidata no cambió rev")
        else:
            print("  ✓ nueva candidata cambia rev")
    finally:
        pkg._publish_dir, pkg._candidates_dir, pkg._final_mp4 = orig
    return ok


def main() -> int:
    print("=" * 68 + "\n  TESTS m09 review server (sin red)\n" + "=" * 68)
    results = {
        "state": test_state(),
        "compose_versioned": test_compose_versioned(),
        "generate_fake": test_generate_fake(),
        "rev": test_rev(),
    }
    print("\n" + "=" * 68)
    for k, v in results.items():
        print(f"  {'PASS ✅' if v else 'FAIL ❌'}  {k}")
    print("=" * 68)
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
