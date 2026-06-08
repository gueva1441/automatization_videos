"""
_lab_spy_add_parent_chat49.py — POST-PROCESO (chat 49 addendum 2, Decisión 8).
Propaga PROCEDENCIA a los outputs de stage2/stage3 SIN re-correr LLM ni scrape (costo cero).
read-only sobre prod. Solo reescribe los JSON de _lab_out/.

Agrega por subtema: parent_video_id + parent_title (el contenedor del que salió).
- stage2_v2: cada row tiene 'n' (índice 1-based del corpus) → parent = corpus[n-1].
- stage3: subtemas hardcodeados de #15/#17 → mapa explícito.

Correr:  python -X utf8 _lab_spy_add_parent_chat49.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

LAB_OUT = Path("_lab_out")
CORPUS = LAB_OUT / "transcripts_chat42.json"
S2 = LAB_OUT / "spy_subtemas_stage2_v2.json"
S3 = LAB_OUT / "spy_subtemas_stage3.json"

# subtema (stage3) → n del corpus de procedencia (primario)
STAGE3_PARENT_N = {
    "Mary Celeste": 15, "USS Cyclops": 15,
    "Wilhelm Gustloff": 17, "Doña Paz": 17, "Marine Sulphur Queen": 17,
}


def main():
    videos = json.loads(CORPUS.read_text(encoding="utf-8"))
    by_n = {i: v for i, v in enumerate(videos, 1)}

    # ── stage2_v2 ──
    if S2.exists():
        d = json.loads(S2.read_text(encoding="utf-8"))
        for row in d.get("rows", []):
            n = row.get("n")
            v = by_n.get(n, {})
            pvid, ptitle = v.get("video_id"), v.get("title")
            row["parent_video_id"] = pvid
            row["parent_title"] = ptitle
            for bucket in ("concretos", "abstractos"):
                for x in row.get(bucket, []):
                    x["parent_video_id"] = pvid
                    x["parent_title"] = ptitle
                    x["origen"] = f"#{n} \"{(ptitle or '')[:50]}\""
        S2.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[OK] stage2_v2 enriquecido: {sum(len(r.get('concretos',[]))+len(r.get('abstractos',[])) for r in d.get('rows',[]))} subtemas con parent")
    else:
        print("[skip] stage2_v2 todavía no existe (v2 corriendo)")

    # ── stage3 ──
    if S3.exists():
        d = json.loads(S3.read_text(encoding="utf-8"))
        for row in d.get("rows", []):
            name = row.get("subtema")
            n = STAGE3_PARENT_N.get(name)
            v = by_n.get(n, {})
            row["parent_video_id"] = v.get("video_id")
            row["parent_title"] = v.get("title")
            row["origen"] = f"#{n} \"{(v.get('title') or '')[:50]}\"" if n else None
        S3.write_text(json.dumps(d, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"[OK] stage3 enriquecido: {len(d.get('rows',[]))} subtemas con parent/origen")
    else:
        print("[skip] stage3 no existe")


if __name__ == "__main__":
    main()
