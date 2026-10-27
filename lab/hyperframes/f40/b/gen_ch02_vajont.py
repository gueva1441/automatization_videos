"""F40 §7.4 (a): el .ass documental de Vajont ch02 con la función nueva, sobre las mismas palabras que usa fase2b
(timestamps + narración original vía remap_words_to_original), y la tabla de eventos con ✗ en lo que viole §1.
Solo lectura de output/audio y data/scripts. Escribe lab/hyperframes/f40/b/ch02_vajont.ass y ch02_tabla.md.
Uso: python lab/hyperframes/f40/b/gen_ch02_vajont.py [--pre-pad S]   (por defecto el pre-roll del title card con --gfx)
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
import fase2b  # noqa: E402
from subs_remap import remap_words_to_original  # noqa: E402

TOPIC = "f8s3-vajont-f30"
CAP = "ch02"
OUT = Path(__file__).resolve().parent


def _t(s: str) -> float:
    h, m, sec = s.split(":")
    return int(h) * 3600 + int(m) * 60 + float(sec)


def tabla(ass: Path) -> tuple[str, int]:
    sd = fase2b.subs_doc
    filas, malos = [], 0
    for ln in ass.read_text(encoding="utf-8").splitlines():
        if not ln.startswith("Dialogue:") or ",Documental," not in ln:
            continue
        partes = ln.split(",", 9)
        a, b, txt = _t(partes[1]), _t(partes[2]), partes[9]
        renglones = txt.split("\\N")
        dur = round(b - a, 2)
        x = []
        if len(renglones) > sd.max_renglones:
            x.append(f"{len(renglones)} renglones")
        if any(len(r) > sd.max_chars_renglon for r in renglones):
            x.append("renglón > 42")
        if dur < sd.min_dur:
            x.append("< 0,833 s")
        if dur > sd.max_dur:
            x.append("> 7 s")
        if re.search(r"[«»…]", txt):
            x.append("comillas")
        if "{" in txt:
            x.append("efecto")
        malos += bool(x)
        filas.append(f"| {len(filas) + 1} | {partes[1]} | {partes[2]} | {dur:.2f} | {' / '.join(renglones)} | "
                     f"{' + '.join(str(len(r)) for r in renglones)} | {'✗ ' + ', '.join(x) if x else '✓'} |")
    cab = ["| # | inicio | fin | dur (s) | texto (renglones separados por /) | caracteres por renglón | §1 |",
           "|---|---|---|---|---|---|---|"]
    return "\n".join(cab + filas), malos


def main() -> int:
    from gfx_config import gfx_rules
    ap = argparse.ArgumentParser()
    ap.add_argument("--pre-pad", type=float, default=float(gfx_rules.title_dur) if gfx_rules.title_pre_roll else 0.0)
    args = ap.parse_args()
    lookup = fase2b._load_script_lookup(TOPIC)
    sm = json.loads((ROOT / "output" / "audio" / TOPIC / "sync_map.json").read_text(encoding="utf-8"))
    cap = next(c for c in sm["chapters"] if c["id"] == CAP)
    norm = json.loads((ROOT / "output" / "audio" / TOPIC / cap["timestamps_path"]).read_text(encoding="utf-8"))
    words = remap_words_to_original(lookup[CAP]["narration"], norm) or norm
    out = OUT / "ch02_vajont.ass"
    fase2b._build_ass_documental(words=words, output_path=out, audio_duration=float(cap["duration_sec"]) + args.pre_pad,
                                 video_width=fase2b.pipeline.video_width, video_height=fase2b.pipeline.video_height,
                                 pre_pad=args.pre_pad)
    t, malos = tabla(out)
    (OUT / "ch02_tabla.md").write_text(f"pre_pad = {args.pre_pad} s (pre-roll del title card con --gfx)\n\n{t}\n"
                                       f"\n{malos} eventos con ✗\n", encoding="utf-8")
    print(f"{out} · {malos} eventos con ✗")
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    raise SystemExit(main())
