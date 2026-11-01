"""¿Algún trigrama cayó en otro lugar? Compara 8 tokens de la aguja contra el audio en el start y busca dónde está de verdad."""
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
T = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
s = json.loads((RAIZ / "data" / "scripts" / f"{T}.json").read_text(encoding="utf-8"))
norm = at.cargar_normalizado(T, RAIZ)
L = []
tot = mal = 0
for ch in s["chapters"]:
    n = ch["chapter_number"]
    its = ch.get("image_prompts") or ch.get("supplemental_image_prompts")
    an = [i["narration_anchor"].strip() for i in its if isinstance(i, dict)]
    w = json.loads((RAIZ / "output" / "audio" / T / f"ch{n:02d}_timestamps.json").read_text(encoding="utf-8"))
    w = w if isinstance(w, list) else w["words"]
    reales = [x for x in w if at._norm(x.get("word", ""))]
    rn = [at._norm(x["word"]) for x in reales]
    with redirect_stdout(io.StringIO()):
        st = at.compute_anchor_starts(an, w, narr_norm=norm[n])
    ag8 = at._agujas_de_voz(an, norm[n], n=8)
    for k, (a, t, ag) in enumerate(zip(an, st, ag8)):
        tot += 1
        j = next(q for q, x in enumerate(reales) if float(x["start"]) == t)
        largo = len(ag)
        coincide = rn[j:j + largo] == ag
        if coincide:
            continue
        # la posición verdadera: la primera con los 8 tokens, desde el start
        ver = next((q for q in range(j, len(rn) - largo + 1) if rn[q:q + largo] == ag), None)
        pasos = sum(x == y for x, y in zip(rn[j:j + largo], ag))
        if ver is None:
            L.append(f"ch{n:02d} #{k + 1} start {t:.2f}: aguja de 8 no aparece entera (coinciden {pasos}/8 desde el start): audio «{' '.join(rn[j:j + 8])}» · aguja «{' '.join(ag)}»")
            continue
        mal += 1
        L.append(f"ch{n:02d} #{k + 1} FALSO: start {t:.2f} «{' '.join(rn[j:j + 6])}»; verdadero {float(reales[ver]['start']):.2f} «{' '.join(rn[ver:ver + 6])}» · adelanto {float(reales[ver]['start']) - t:.2f} s")
print(tot, "anclas;", mal, "falsas")
print("\n".join(L))
