"""
test_m09_packaging.py — Tests SIN red de m09a packaging (chat 56).

Cubre la lógica local: shortlist del audit_map, overlay Pillow, normalización de
metadata (títulos ≤90, tags ≤450). Las llamadas Gemini/Flux las dispara Omar.
"""
from __future__ import annotations

import sys
import tempfile
from pathlib import Path

from PIL import Image

from script_engine import m09_packaging as m


def _section(t): print("\n" + "─" * 68 + f"\n{t}")


def test_shortlist():
    _section("1· shortlist_existing (filtra + ordena)")
    csv_text = (
        "cap,img,filename,verdict_r1,punch_total_r1,foco,zoom_judge_category\n"
        "ch02,1,ch02_img_01,fiel,8,2,\n"            # candidato fuerte
        "ch03,2,ch03_img_02,fiel,7,2,\n"
        "ch04,3,ch04_img_03,fiel,8,1,\n"            # punch 8 pero foco 1 (desempate)
        "ch05,4,ch05_img_04,sujeto_agregado,8,2,\n"  # divergente → excluido
        "ch06,5,ch06_img_05,fiel,8,2,superficie_plana\n"  # superficie_plana → excluido
        "ch02,6,ch02_img_06,fiel,5,2,\n"
    )
    tmp = Path(tempfile.mkdtemp()) / "audit.csv"
    tmp.write_text(csv_text, encoding="utf-8")
    sl = m.shortlist_existing(tmp, n=4)
    names = [r["filename"] for r in sl]
    ok = True
    if "ch05_img_04" in names:
        ok = False; print("  ✗ no excluyó el divergente")
    if "ch06_img_05" in names:
        ok = False; print("  ✗ no excluyó superficie_plana")
    # orden: punch desc, desempate foco desc → img_01(8,2), img_03(8,1), img_02(7,2), img_06(5,2)
    expected = ["ch02_img_01", "ch04_img_03", "ch03_img_02", "ch02_img_06"]
    if names != expected:
        ok = False; print(f"  ✗ orden: {names}\n     esperado: {expected}")
    else:
        print(f"  ✓ shortlist correcta: {names}")
    return ok


def test_overlay():
    _section("2· compose_thumbnail (1280×720, <2MB, texto, esquina inf-DER libre)")
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
    # texto presente: difieren globalmente
    if int(np.abs(a_txt - a_emp).sum()) == 0:
        ok = False; print("  ✗ el texto no se dibujó (idéntico al vacío)")
    else:
        print("  ✓ texto dibujado (difiere del base sin texto)")
    # esquina inferior-DERECHA libre (YouTube pinta duración): sin cambios ahí
    br = np.abs(a_txt[m.THUMB_H-120:, m.THUMB_W-260:] - a_emp[m.THUMB_H-120:, m.THUMB_W-260:]).sum()
    if br != 0:
        ok = False; print(f"  ✗ texto invadió la esquina inferior-derecha (Δ={br})")
    else:
        print("  ✓ esquina inferior-derecha intacta")
    # el texto cayó en el tercio inferior-izquierdo (hay cambios ahí)
    bl = np.abs(a_txt[m.THUMB_H-260:, :m.THUMB_W//2] - a_emp[m.THUMB_H-260:, :m.THUMB_W//2]).sum()
    if bl == 0:
        ok = False; print("  ✗ no hay texto en el tercio inferior-izquierdo")
    else:
        print("  ✓ texto en tercio inferior-izquierdo")
    return ok


def test_metadata_norm():
    _section("3· normalización metadata (títulos ≤90, tags ≤450, 3 títulos, 3 overlays MAYÚS)")
    ok = True
    long_title = "x" * 120
    tags = [f"tag{i}aaaaaaaaaa" for i in range(60)]  # muchos → debe truncar
    data = {"titulos": [long_title, "b", "c", "d"],
            "overlays": ["  muerte en x  ", "tensión cruda", "¿quién fue?", "sobrante"],
            "descripcion": "  hola  ", "tags": tags}
    norm = m._normalize_metadata(data)
    if len(norm["titulos"]) != 3:
        ok = False; print(f"  ✗ títulos={len(norm['titulos'])} (esperaba 3)")
    else:
        print("  ✓ exactamente 3 títulos")
    if len(norm["overlays"]) != 3:
        ok = False; print(f"  ✗ overlays={len(norm['overlays'])} (esperaba 3)")
    elif not all(o == o.upper() for o in norm["overlays"]):
        ok = False; print(f"  ✗ overlays no en MAYÚSCULAS: {norm['overlays']}")
    elif norm["overlays"][0] != "MUERTE EN X":
        ok = False; print(f"  ✗ overlay no strip+upper: {norm['overlays'][0]!r}")
    else:
        print(f"  ✓ 3 overlays en MAYÚSCULAS (strip): {norm['overlays']}")
    if len(norm["titulos"][0]) > m.MAX_TITLE_CHARS:
        ok = False; print(f"  ✗ título sin truncar: {len(norm['titulos'][0])}")
    else:
        print(f"  ✓ título truncado a ≤{m.MAX_TITLE_CHARS}")
    total = sum(len(t) for t in norm["tags"]) + max(0, len(norm["tags"]) - 1)
    if total > m.MAX_TAGS_CHARS:
        ok = False; print(f"  ✗ tags={total} > {m.MAX_TAGS_CHARS}")
    else:
        print(f"  ✓ tags ≤{m.MAX_TAGS_CHARS} ({total} chars)")
    if norm["descripcion"] != "hola":
        ok = False; print(f"  ✗ descripción no normalizada: {norm['descripcion']!r}")
    else:
        print("  ✓ descripción strip")
    return ok


def test_truncate_tags():
    _section("4· _truncate_tags (corte exacto a 450)")
    tags = [f"palabra{i:02d}" for i in range(100)]
    out = m._truncate_tags(tags, m.MAX_TAGS_CHARS)
    total = sum(len(t) for t in out) + max(0, len(out) - 1)
    ok = total <= m.MAX_TAGS_CHARS and len(out) < len(tags)
    print(f"  {'✓' if ok else '✗'} {len(out)} tags, {total} chars (≤450, truncó)")
    return ok


def test_focus_crop():
    _section("5· _fit_cover --focus (top preserva tercio superior de fuente vertical)")
    import numpy as np
    # Fuente vertical 1080×1920: banda ROJA en el tope (cara alta), resto oscuro
    src = Image.new("RGB", (1080, 1920), (20, 20, 20))
    for y in range(0, 220):
        for x in range(1080):
            src.putpixel((x, y), (220, 30, 30))
    def red_in_top(im):
        a = np.asarray(im.convert("RGB"), dtype=int)
        top = a[:140]  # franja superior del thumb 1280×720
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
        print("  ✓ focus=center NO muestra el tope (crop centrado, como el bug de existing_02)")
    if rt <= rc:
        ok = False; print("  ✗ top no preserva más tope que center")
    return ok


def test_hero_user_prompt():
    _section("7· hero user prompt incluye la narración + personaje (PASO 1)")
    canonical = {
        "video_title": "La Antigua Cárcel",
        "canonical_subject_description": "una vieja cárcel de piedra",
        "chapters": [
            {"chapter_number": 1, "narration": "Una historia oscura comienza."},
            {"chapter_number": 3, "narration": "La novia espectral Lavinia Fisher recorre los pasillos al anochecer."},
            {"chapter_number": 7, "narration": "Z" * 2000},  # para probar el truncado por cap
        ],
    }
    u = m._hero_user_prompt(canonical)
    ok = True
    checks = [
        ("Lavinia Fisher" in u, "incluye el personaje de la narración"),
        ("NARRACIÓN COMPLETA" in u and "PASO 1" in u, "instruye PASO 1 con la narración"),
        ("[Cap 3]" in u, "narración por capítulo"),
        ("[…]" in u and u.count("Z") <= m.HERO_NARRATION_PER_CAP, "trunca cap largo al tope"),
    ]
    for cond, label in checks:
        if not cond:
            ok = False; print(f"  ✗ {label}")
        else:
            print(f"  ✓ {label}")
    return ok


def test_resolve_mode():
    _section("8· _resolve_mode (--review solo válido; combos inválidos fallan)")
    ok = True
    # (candidates, compose, review) → modo esperado | None si debe lanzar ValueError
    cases = [
        ((True, False, False), "candidates"),
        ((True, False, True), "candidates"),   # --review acompaña a --candidates
        ((False, True, False), "compose"),
        ((False, False, True), "review"),      # --review SOLO (el bug)
        ((True, True, False), None),           # candidates + compose inválido
        ((False, True, True), None),           # compose + review inválido
        ((False, False, False), None),         # nada
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
    _section("9· compose --fill (blanco / amarillo / rojo)")
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
        region = a[m.THUMB_H - 260:, :m.THUMB_W // 2]   # tercio inferior-izquierdo
        hits = int((np.abs(region - np.array(tgt)).sum(axis=2) < 60).sum())
        if hits < 50:
            ok = False; print(f"  ✗ {name}: solo {hits} px ≈ {tgt}")
        else:
            print(f"  ✓ {name}: {hits} px del color {tgt}")
    # default = blanco
    if m.THUMB_FILL_DEFAULT != "blanco":
        ok = False; print("  ✗ default no es blanco")
    else:
        print("  ✓ default = blanco")
    return ok


def test_run_compose_title_idx():
    _section("10· run_compose: --title N → string (N fuera de rango → SystemExit)")
    orig = (m._publish_dir, m._candidates_dir, m._final_mp4)
    tmp = Path(tempfile.mkdtemp())
    ok = True
    try:
        pub = tmp / "publish"; cand = pub / "thumb_candidates"; cand.mkdir(parents=True)
        m._publish_dir = lambda tid: pub
        m._candidates_dir = lambda tid: cand
        m._final_mp4 = lambda tid: tmp / "v.mp4"
        Image.new("RGB", (1280, 720), (20, 20, 20)).save(cand / "fresh_01.png")
        (pub / "metadata.json").write_text(
            '{"titulos": ["Título uno", "Título dos", "Título tres"], "descripcion": "d", "tags": ["a"]}',
            encoding="utf-8")
        # N válido → resuelve el string y compone; metadata final guarda el título elegido
        m.run_compose("TID", "fresh_01.png", "TEXTO", 2, video_path="/x/v.mp4")
        import json as _json
        meta = _json.loads((pub / "metadata.json").read_text(encoding="utf-8"))
        if meta.get("titulo_elegido") != "Título dos":
            ok = False; print(f"  ✗ título elegido mal: {meta.get('titulo_elegido')!r}")
        else:
            print("  ✓ --title 2 → 'Título dos' (índice resuelto a string)")
        # N fuera de rango → SystemExit
        try:
            m.run_compose("TID", "fresh_01.png", "TEXTO", 9, video_path="/x/v.mp4")
            ok = False; print("  ✗ --title 9 no lanzó SystemExit")
        except SystemExit as e:
            if "fuera de rango" not in str(e):
                ok = False; print(f"  ✗ SystemExit con mensaje raro: {e}")
            else:
                print("  ✓ --title 9 (fuera de rango) → SystemExit")
    finally:
        m._publish_dir, m._candidates_dir, m._final_mp4 = orig
    return ok


def test_compose_title_string():
    _section("11· compose_and_package: title STRING (libre / vacío → ValueError)")
    orig = (m._publish_dir, m._candidates_dir, m._final_mp4)
    tmp = Path(tempfile.mkdtemp())
    ok = True
    try:
        pub = tmp / "publish"; cand = pub / "thumb_candidates"; cand.mkdir(parents=True)
        m._publish_dir = lambda tid: pub
        m._candidates_dir = lambda tid: cand
        m._final_mp4 = lambda tid: tmp / "v.mp4"
        Image.new("RGB", (1280, 720), (20, 20, 20)).save(cand / "fresh_01.png")
        (pub / "metadata.json").write_text('{"titulos": ["A"], "descripcion": "d", "tags": ["a"]}',
                                           encoding="utf-8")
        # título escrito a mano (NO está en titulos) → se acepta tal cual
        written = m.compose_and_package("TID", "fresh_01.png", "TEXTO", "Título a mano",
                                        out_name="thumb_final.png", video_path="/x/v.mp4")
        import json as _json
        meta = _json.loads((pub / "metadata.json").read_text(encoding="utf-8"))
        if meta.get("titulo_elegido") != "Título a mano" or not written.exists():
            ok = False; print(f"  ✗ título libre no se guardó: {meta.get('titulo_elegido')!r}")
        else:
            print("  ✓ título escrito a mano se acepta (combobox editable)")
        # título vacío → ValueError
        try:
            m.compose_and_package("TID", "fresh_01.png", "TEXTO", "   ", video_path="/x/v.mp4")
            ok = False; print("  ✗ título vacío no lanzó ValueError")
        except ValueError:
            print("  ✓ título vacío → ValueError")
    finally:
        m._publish_dir, m._candidates_dir, m._final_mp4 = orig
    return ok


def main() -> int:
    print("=" * 68 + "\n  TESTS m09a packaging (sin red)\n" + "=" * 68)
    results = {
        "shortlist": test_shortlist(),
        "overlay": test_overlay(),
        "metadata_norm": test_metadata_norm(),
        "truncate_tags": test_truncate_tags(),
        "focus_crop": test_focus_crop(),
        "hero_user_prompt": test_hero_user_prompt(),
        "resolve_mode": test_resolve_mode(),
        "fill_color": test_fill_color(),
        "run_compose_title_idx": test_run_compose_title_idx(),
        "compose_title_string": test_compose_title_string(),
    }
    print("\n" + "=" * 68)
    for k, v in results.items():
        print(f"  {'PASS ✅' if v else 'FAIL ❌'}  {k}")
    print("=" * 68)
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
