"""
test_m09_packaging.py — Tests SIN red de m09a packaging (chat 56, adaptado a F58: paquetes).

Cubre la lógica local: overlay Pillow (mitad izquierda, esquina inf-DER libre), normalización de los paquetes
(títulos ≤90, tags ≤450, texto MAYÚSCULAS), `_truncate_tags`, `_fit_cover`, `_resolve_mode`, `--fill`,
`run_compose --paquete N`, `compose_and_package` y el ruteo de la foto por el productor (`_generate_image_raw`).
Lo que pide el handoff F58 (A1–A7) vive en test_module_f58.py.
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

from PIL import Image

from script_engine import m09_packaging as m


def _section(t): print("\n" + "─" * 68 + f"\n{t}")


def _meta_paquetes():
    return {"topic_id": "TID", "stage": "candidates", "descripcion": "d", "tags": ["a"], "avisos": [],
            "paquetes": [{"n": i, "estrategia": i, "titulo": f"Título {['uno', 'dos', 'tres'][i-1]}",
                          "dato_ids": ["D01"], "datos": {"D01": "x"}, "texto": "TEXTO", "cap_que_paga": 3,
                          "ancla": "A.", "avisos": [], "foto": "paquete_01_base.png", "base": "paquete_01_base.png",
                          "miniatura": None, "motivo_sin_foto": None} for i in (1, 2, 3)]}


def test_overlay():
    _section("1· compose_thumbnail (1280×720, <2MB, texto, esquina inf-DER libre)")
    tmpd = Path(tempfile.mkdtemp())
    base = tmpd / "base.png"
    Image.new("RGB", (1080, 1920), (60, 60, 70)).save(base)  # fuente 9:16 → cover-crop
    out_txt = tmpd / "final.png"
    out_empty = tmpd / "empty.png"
    p_txt = m.compose_thumbnail(base, "MUERTE EN CHARLESTON", out_txt)
    p_empty = m.compose_thumbnail(base, "", out_empty)

    ok = True
    im = Image.open(p_txt)
    if im.size != (m.THUMB_W, m.THUMB_H):
        ok = False; print(f"  ✗ tamaño {im.size} != (1280,720)")
    else:
        print("  ✓ 1280×720")
    if p_txt.stat().st_size > m.THUMB_MAX_BYTES:
        ok = False; print(f"  ✗ {p_txt.stat().st_size} > 2MB")
    else:
        print(f"  ✓ <2MB ({p_txt.stat().st_size//1024} KB)")

    import numpy as np
    a_txt = np.asarray(Image.open(p_txt).convert("RGB"), dtype=int)
    a_emp = np.asarray(Image.open(p_empty).convert("RGB"), dtype=int)
    if int(np.abs(a_txt - a_emp).sum()) == 0:
        ok = False; print("  ✗ el texto no se dibujó (idéntico al vacío)")
    else:
        print("  ✓ texto dibujado (difiere del base sin texto)")
    # F58: la mitad DERECHA entera queda intacta (el texto vive en la mitad izquierda)
    br = np.abs(a_txt[:, m.THUMB_W // 2 + m.THUMB_STROKE_PX:] - a_emp[:, m.THUMB_W // 2 + m.THUMB_STROKE_PX:]).sum()
    if br != 0:
        ok = False; print(f"  ✗ texto invadió la mitad derecha (Δ={br})")
    else:
        print("  ✓ mitad derecha intacta (esquina inferior-derecha libre)")
    bl = np.abs(a_txt[m.THUMB_H-300:, :m.THUMB_W//2] - a_emp[m.THUMB_H-300:, :m.THUMB_W//2]).sum()
    if bl == 0:
        ok = False; print("  ✗ no hay texto abajo a la izquierda")
    else:
        print("  ✓ texto abajo a la izquierda")
    return ok


def test_normalizar_paquetes():
    _section("2· normalizar_paquetes (títulos ≤90, tags ≤450, texto MAYÚS, descripción con crédito)")
    ok = True
    tags = [f"tag{i}aaaaaaaaaa" for i in range(60)]  # muchos → debe truncar
    data = {"paquetes": [{"estrategia": 1, "titulo": "x" * 120, "dato_ids": ["D01"], "texto": "  muerte en x  ",
                          "cap_que_paga": 2, "ancla": "A.  B."}],
            "descripcion": "  hola  ", "tags": tags}
    norm = m.normalizar_paquetes(data)
    p = norm["paquetes"][0]
    if len(p["titulo"]) > m.MAX_TITLE_CHARS:
        ok = False; print(f"  ✗ título sin truncar: {len(p['titulo'])}")
    else:
        print(f"  ✓ título truncado a ≤{m.MAX_TITLE_CHARS}")
    if p["texto"] != "MUERTE EN X":
        ok = False; print(f"  ✗ texto no strip+upper: {p['texto']!r}")
    else:
        print("  ✓ texto en MAYÚSCULAS (strip)")
    if p["ancla"] != "A. B.":
        ok = False; print(f"  ✗ ancla sin normalizar espacios: {p['ancla']!r}")
    else:
        print("  ✓ ancla con espacios normalizados")
    total = sum(len(t) for t in norm["tags"]) + max(0, len(norm["tags"]) - 1)
    if total > m.MAX_TAGS_CHARS:
        ok = False; print(f"  ✗ tags={total} > {m.MAX_TAGS_CHARS}")
    else:
        print(f"  ✓ tags ≤{m.MAX_TAGS_CHARS} ({total} chars)")
    if not norm["descripcion"].startswith("hola") or m.ICON_CREDIT not in norm["descripcion"]:
        ok = False; print(f"  ✗ descripción no normalizada: {norm['descripcion']!r}")
    else:
        print("  ✓ descripción strip + crédito de íconos")
    return ok


def test_truncate_tags():
    _section("3· _truncate_tags (corte exacto a 450)")
    tags = [f"palabra{i:02d}" for i in range(100)]
    out = m._truncate_tags(tags, m.MAX_TAGS_CHARS)
    total = sum(len(t) for t in out) + max(0, len(out) - 1)
    ok = total <= m.MAX_TAGS_CHARS and len(out) < len(tags)
    print(f"  {'✓' if ok else '✗'} {len(out)} tags, {total} chars (≤450, truncó)")
    return ok


def test_focus_crop():
    _section("4· _fit_cover --focus (top preserva tercio superior de fuente vertical)")
    import numpy as np
    src = Image.new("RGB", (1080, 1920), (20, 20, 20))
    for y in range(0, 220):
        for x in range(1080):
            src.putpixel((x, y), (220, 30, 30))
    def red_in_top(im):
        a = np.asarray(im.convert("RGB"), dtype=int)
        top = a[:140]
        return int(((top[..., 0] > 150) & (top[..., 1] < 90)).sum())
    top_img = m._fit_cover(src, m.THUMB_W, m.THUMB_H, "top")
    ctr_img = m._fit_cover(src, m.THUMB_W, m.THUMB_H, "center")
    ok = True
    if top_img.size != (m.THUMB_W, m.THUMB_H) or ctr_img.size != (m.THUMB_W, m.THUMB_H):
        ok = False; print("  ✗ tamaño incorrecto")
    rt, rc = red_in_top(top_img), red_in_top(ctr_img)
    if rt <= 0:
        ok = False; print(f"  ✗ focus=top NO preservó la banda superior (rojo={rt})")
    else:
        print(f"  ✓ focus=top preserva el tope (rojo={rt})")
    if rc != 0:
        ok = False; print(f"  ✗ focus=center mostró la banda superior (rojo={rc}, debería decapitarla)")
    else:
        print("  ✓ focus=center NO muestra el tope (crop centrado)")
    if rt <= rc:
        ok = False; print("  ✗ top no preserva más tope que center")
    return ok


def test_resolve_mode():
    _section("5· _resolve_mode (--review solo válido; combos inválidos fallan)")
    ok = True
    cases = [
        ((True, False, False), "candidates"),
        ((True, False, True), "candidates"),
        ((False, True, False), "compose"),
        ((False, False, True), "review"),
        ((True, True, False), None),
        ((False, True, True), None),
        ((False, False, False), None),
    ]
    for (c, co, r), exp in cases:
        try:
            got = m._resolve_mode(c, co, r)
            if exp is None:
                ok = False; print(f"  ✗ ({c},{co},{r}) debía fallar, dio {got!r}")
            elif got != exp:
                ok = False; print(f"  ✗ ({c},{co},{r}) → {got!r} != {exp!r}")
            else:
                print(f"  ✓ ({c},{co},{r}) → {got}")
        except ValueError:
            if exp is not None:
                ok = False; print(f"  ✗ ({c},{co},{r}) lanzó pero esperaba {exp!r}")
            else:
                print(f"  ✓ ({c},{co},{r}) → ValueError (inválido)")
    return ok


def test_fill_color():
    _section("6· compose --fill (blanco / amarillo / rojo)")
    import numpy as np
    tmpd = Path(tempfile.mkdtemp())
    base = tmpd / "base.png"
    Image.new("RGB", (1280, 720), (15, 15, 15)).save(base)
    targets = {"blanco": (255, 255, 255), "amarillo": (255, 214, 0), "rojo": (231, 29, 29)}
    ok = True
    for name, tgt in targets.items():
        out = tmpd / f"{name}.png"
        m.compose_thumbnail(base, "TEXTO COLOR", out, fill=name)
        a = np.asarray(Image.open(out).convert("RGB"), dtype=int)
        region = a[m.THUMB_H - 300:, :m.THUMB_W // 2]
        hits = int((np.abs(region - np.array(tgt)).sum(axis=2) < 60).sum())
        if hits < 50:
            ok = False; print(f"  ✗ {name}: solo {hits} px ≈ {tgt}")
        else:
            print(f"  ✓ {name}: {hits} px del color {tgt}")
    if m.THUMB_FILL_DEFAULT != "blanco":
        ok = False; print("  ✗ default no es blanco")
    else:
        print("  ✓ default = blanco")
    return ok


def test_run_compose_paquete():
    _section("7· run_compose: --paquete N → título/texto/base del paquete (N inexistente → SystemExit)")
    orig = (m._publish_dir, m._candidates_dir, m._final_mp4, m._assets_dir)
    tmp = Path(tempfile.mkdtemp())
    ok = True
    try:
        pub = tmp / "publish"; cand = pub / "thumb_candidates"; cand.mkdir(parents=True)
        m._publish_dir = lambda tid: pub
        m._candidates_dir = lambda tid: cand
        m._assets_dir = lambda tid: tmp / "assets"
        m._final_mp4 = lambda tid: tmp / "v.mp4"
        Image.new("RGB", (1280, 720), (20, 20, 20)).save(cand / "paquete_01_base.png")
        (pub / "metadata.json").write_text(json.dumps(_meta_paquetes(), ensure_ascii=False), encoding="utf-8")
        m.run_compose("TID", 2, video_path="/x/v.mp4")
        meta = json.loads((pub / "metadata.json").read_text(encoding="utf-8"))
        if meta.get("titulo_elegido") != "Título dos" or meta.get("base_thumb") != "paquete_01_base.png":
            ok = False; print(f"  ✗ paquete 2 mal resuelto: {meta.get('titulo_elegido')!r} {meta.get('base_thumb')!r}")
        else:
            print("  ✓ --paquete 2 → 'Título dos' + su base")
        try:
            m.run_compose("TID", 9, video_path="/x/v.mp4")
            ok = False; print("  ✗ --paquete 9 no lanzó SystemExit")
        except SystemExit as e:
            if "fuera de rango" not in str(e):
                ok = False; print(f"  ✗ SystemExit con mensaje raro: {e}")
            else:
                print("  ✓ --paquete 9 (inexistente) → SystemExit")
    finally:
        m._publish_dir, m._candidates_dir, m._final_mp4, m._assets_dir = orig
    return ok


def test_compose_title_string():
    _section("8· compose_and_package: title STRING (libre / vacío → ValueError)")
    orig = (m._publish_dir, m._candidates_dir, m._final_mp4, m._assets_dir)
    tmp = Path(tempfile.mkdtemp())
    ok = True
    try:
        pub = tmp / "publish"; cand = pub / "thumb_candidates"; cand.mkdir(parents=True)
        m._publish_dir = lambda tid: pub
        m._candidates_dir = lambda tid: cand
        m._assets_dir = lambda tid: tmp / "assets"
        m._final_mp4 = lambda tid: tmp / "v.mp4"
        Image.new("RGB", (1280, 720), (20, 20, 20)).save(cand / "paquete_01_base.png")
        (pub / "metadata.json").write_text(json.dumps(_meta_paquetes()), encoding="utf-8")
        written = m.compose_and_package("TID", "paquete_01_base.png", "TEXTO", "Título a mano",
                                        out_name="thumb_final.png", video_path="/x/v.mp4")
        meta = json.loads((pub / "metadata.json").read_text(encoding="utf-8"))
        if meta.get("titulo_elegido") != "Título a mano" or not written.exists():
            ok = False; print(f"  ✗ título libre no se guardó: {meta.get('titulo_elegido')!r}")
        else:
            print("  ✓ título escrito a mano se acepta")
        try:
            m.compose_and_package("TID", "paquete_01_base.png", "TEXTO", "   ", video_path="/x/v.mp4")
            ok = False; print("  ✗ título vacío no lanzó ValueError")
        except ValueError:
            print("  ✓ título vacío → ValueError")
    finally:
        m._publish_dir, m._candidates_dir, m._final_mp4, m._assets_dir = orig
    return ok


def test_foto_paquete_routes_to_producer():
    _section("9· foto_paquete rutea por el productor (seedream, use_ultra=False); fallo → motivo literal")
    import asset_manager as am
    ok = True
    calls = []

    def fake_raw(prompt, output_path, use_ultra, seed=None, foto_madre_data_uris=None):
        calls.append({"prompt": prompt, "out": output_path, "use_ultra": use_ultra})
        Image.new("RGB", (2560, 1440), (10, 10, 10)).save(output_path)
        return {"endpoint": "seedream/v4.5/t2i"}

    orig = am._generate_image_raw
    am._generate_image_raw = fake_raw
    try:
        cand = Path(tempfile.mkdtemp())
        err = m.foto_paquete("PROSA", cand / "paquete_01_base.png")
        if err is not None or len(calls) != 1 or calls[0]["use_ultra"] is not False or calls[0]["prompt"] != "PROSA":
            ok = False; print(f"  ✗ args al productor mal: {calls} err={err}")
        elif not (cand / "paquete_01_base.png").exists():
            ok = False; print("  ✗ no escribió la foto")
        else:
            print("  ✓ productor llamado con (prompt, out, use_ultra=False) y escribió la foto")
    finally:
        am._generate_image_raw = orig

    src = Path(m.__file__).read_text(encoding="utf-8")
    if "_flux_16x9" in src or "fal_image_model" in src or "track_flux_pro" in src or "gemini_client" in src:
        ok = False; print("  ✗ quedó wiring viejo (flux/gemini) en el módulo")
    else:
        print("  ✓ sin wiring Flux/Gemini en el módulo")

    def fake_boom(prompt, output_path, use_ultra, seed=None, foto_madre_data_uris=None):
        raise RuntimeError("boom")

    am._generate_image_raw = fake_boom
    try:
        err2 = m.foto_paquete("PROSA", Path(tempfile.mkdtemp()) / "paquete_01_base.png")
    finally:
        am._generate_image_raw = orig
    if err2 != "RuntimeError: boom":
        ok = False; print(f"  ✗ el motivo no es literal: {err2!r}")
    else:
        print("  ✓ fallo → motivo literal 'RuntimeError: boom' (el paquete queda sin foto, sin excepción)")
    return ok


def main() -> int:
    print("=" * 68 + "\n  TESTS m09a packaging (sin red)\n" + "=" * 68)
    results = {
        "overlay": test_overlay(),
        "normalizar_paquetes": test_normalizar_paquetes(),
        "truncate_tags": test_truncate_tags(),
        "focus_crop": test_focus_crop(),
        "resolve_mode": test_resolve_mode(),
        "fill_color": test_fill_color(),
        "run_compose_paquete": test_run_compose_paquete(),
        "compose_title_string": test_compose_title_string(),
        "foto_paquete_routes_to_producer": test_foto_paquete_routes_to_producer(),
    }
    print("\n" + "=" * 68)
    for k, v in results.items():
        print(f"  {'PASS ✅' if v else 'FAIL ❌'}  {k}")
    print("=" * 68)
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
