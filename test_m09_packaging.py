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
    _section("3· normalización metadata (títulos ≤90, tags ≤450, 3 títulos)")
    ok = True
    long_title = "x" * 120
    tags = [f"tag{i}aaaaaaaaaa" for i in range(60)]  # muchos → debe truncar
    data = {"titulos": [long_title, "b", "c", "d"], "descripcion": "  hola  ", "tags": tags}
    norm = m._normalize_metadata(data)
    if len(norm["titulos"]) != 3:
        ok = False; print(f"  ✗ títulos={len(norm['titulos'])} (esperaba 3)")
    else:
        print("  ✓ exactamente 3 títulos")
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


def main() -> int:
    print("=" * 68 + "\n  TESTS m09a packaging (sin red)\n" + "=" * 68)
    results = {
        "shortlist": test_shortlist(),
        "overlay": test_overlay(),
        "metadata_norm": test_metadata_norm(),
        "truncate_tags": test_truncate_tags(),
        "focus_crop": test_focus_crop(),
    }
    print("\n" + "=" * 68)
    for k, v in results.items():
        print(f"  {'PASS ✅' if v else 'FAIL ❌'}  {k}")
    print("=" * 68)
    return 0 if all(results.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
