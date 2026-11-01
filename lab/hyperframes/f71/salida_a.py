"""F71 Etapa A, salida en texto. Solo lee; sin llamadas. Antes = sin narr_norm (lo que hacía el código viejo); después = con narr_norm."""
import io
import json
import os
import sys
from contextlib import redirect_stdout
from pathlib import Path
RAIZ = Path(r"C:\CLAUDE_PROJECTS\automatization_videos")
os.chdir(RAIZ)
sys.path.insert(0, str(RAIZ))
import anchor_timing as at
import qa_studio_server as qa

WIT, ORL = "123bbb64-9fca-4395-8bf4-57d60e219ef1", "ba6c3cac-a091-41c0-8dad-afd2f4364747"
OUT = RAIZ / "lab" / "hyperframes" / "f71" / "SALIDA_A.md"


def cap_datos(T, ch):
    n = ch["chapter_number"]
    its = ch.get("image_prompts") or ch.get("supplemental_image_prompts") or []
    its = [i for i in its if isinstance(i, dict)]
    cid = f"ch{n:02d}"
    f = RAIZ / "output" / "audio" / T / f"{cid}_timestamps.json"
    if not f.exists():
        return cid, [], []
    w = json.loads(f.read_text(encoding="utf-8"))
    return cid, [(i.get("narration_anchor") or "").strip() for i in its], (w if isinstance(w, list) else w.get("words", []))


def corre(anclas, w, nn):
    b = io.StringIO()
    with redirect_stdout(b):
        st = at.compute_anchor_starts(anclas, w, narr_norm=nn)
    fb = b.getvalue().count("FALLBACK")
    return st, fb


lineas = ["# F71 Etapa A: salida en texto (generada por script, sin llamadas)", "", "## Wittenoom por cap", "",
          "| Cap | Anclas | Antes | Después | Por trigrama | Por fallback | Literales en la narración | Por paso 2 (no literal) |", "|---|---|---|---|---|---|---|---|"]
s = json.loads((RAIZ / "data" / "scripts" / f"{WIT}.json").read_text(encoding="utf-8"))
norm = at.cargar_normalizado(WIT, RAIZ)
detalle = []
for ch in s["chapters"]:
    cid, an, w = cap_datos(WIT, ch)
    nn = norm.get(ch["chapter_number"])
    ant, _ = corre(an, w, None)
    des, fb = corre(an, w, nn)
    orig, cur, lit = nn["narration_original"], 0, 0
    for a in an:
        i = orig.find(a, cur)
        if i >= 0:
            lit += 1
            cur = i + 1
    lineas.append(f"| {cid} | {len(an)} | {'OK' if ant else 'None'} | {'OK' if des else 'None'} | {len(an) - fb if des else '-'} | {fb if des else '-'} | {lit} | {len(an) - lit} |")
    if ch["chapter_number"] in (2, 3, 5, 6, 7):
        detalle += ["", f"### {cid}", "", "| # | start (s) | 3 palabras del audio | Ancla |", "|---|---|---|---|"]
        reales = [x for x in w if at._norm(x.get("word", ""))]
        for k, (a, t) in enumerate(zip(an, des or [])):
            j = next(q for q, x in enumerate(reales) if float(x["start"]) == t)
            tres = " ".join(x["word"].strip() for x in reales[j:j + 3])
            detalle.append(f"| {k + 1} | {t:.2f} | {tres} | {' '.join(a.split()[:7]).replace('|', '/')}… |")
lineas += ["", "## Texto rearmado vs. lo que leyó la voz", ""]
from tts_normalizer import normalize_pool_forms
for n, e in sorted(norm.items()):
    t = e["narration_original"]
    for sp in sorted((x for x in e["spans_applied"] if x.get("decision") == "applied" and x.get("category") != "f5_pool_forms"), key=lambda x: len(x["original"]), reverse=True):
        i = t.find(sp["original"])
        if i >= 0:
            t = t[:i] + sp["suggested"] + t[i + len(sp["original"]):]
    lineas.append(f"- ch{n:02d}: {'idéntico' if normalize_pool_forms(t) == e['narration_normalized'] else 'DIFIERE'} a `narration_normalized`")

lineas += ["", "## QA Studio, `sync_approx` por cap (con el código nuevo)", ""]
st = qa.QAState(WIT, base_dir=RAIZ)
for n in range(1, 8):
    c = st.cap(n)
    lineas.append(f"- ch{n:02d}: sync_approx = {c.get('sync_approx')} · {len(c.get('segments') or [])} segmentos")

lineas += ["", "## Orleans `ba6c3cac-…`, antes y después", ""]
so = json.loads((RAIZ / "data" / "scripts" / f"{ORL}.json").read_text(encoding="utf-8"))
no = at.cargar_normalizado(ORL, RAIZ)
lineas.append(f"Tiene normalizado: {'sí' if no else 'no (usa normalize_for_tts, como antes)'}.")
lineas += ["", "| Cap | Anclas | Antes | Después | Igual |", "|---|---|---|---|---|"]
for ch in so["chapters"]:
    cid, an, w = cap_datos(ORL, ch)
    if not an or not w:
        lineas.append(f"| {cid} | {len(an)} | sin datos | sin datos | - |")
        continue
    a0, _ = corre(an, w, None)
    a1, _ = corre(an, w, no.get(ch["chapter_number"]))
    lineas.append(f"| {cid} | {len(an)} | {'OK' if a0 else 'None'} | {'OK' if a1 else 'None'} | {'sí' if a0 == a1 else 'NO'} |")
lineas += ["", "## Por ancla, ch02, ch03, ch05, ch06 y ch07"] + detalle
OUT.write_text("\n".join(lineas) + "\n", encoding="utf-8")
print("\n".join(lineas[:60]))
