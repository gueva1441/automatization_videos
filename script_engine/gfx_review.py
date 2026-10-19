"""
gfx_review.py — Hoja de cues y página de revisión local de la capa gráfica (F1b).

  write_cues(...)   → work_dir/gfx_cues_chNN.md (+ .json): una línea por evento ordenada por tiempo,
                      omisiones/descartes del director, gap_warnings, conteo por bloque, tiempo de render.
  write_review(...) → work_dir/gfx_review_chNN.html: <video> del segmento + lista de cues clicable
                      (salta al segundo, resalta el activo) + botón "copiar nota". HTML estático,
                      sin servidor ni CDN. Precursor de la pestaña de QA Studio (F5).
"""
from __future__ import annotations

import html
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

_NOTE_RE = re.compile(r"(omitido|descartado|recortados|gap_warning)")


def fmt_t(t: float) -> str:
    """Segundos → mm:ss.d"""
    m, s = divmod(max(0.0, t), 60)
    return f"{int(m):02d}:{s:04.1f}"


def write_cues(cap: str, events: list[dict[str, Any]], log_lines: list[str], gaps: list[list[float]],
               render_sec: float | None, work_dir: Path) -> Path:
    """Escribe gfx_cues_<cap>.md y .json. Devuelve el path del .md."""
    notes = [ln.strip() for ln in log_lines if _NOTE_RE.search(ln) and not ln.strip().startswith("plan:")]
    lines = [f"# gfx cues {cap}", "", "| tiempo | bloque | texto | duración |", "|---|---|---|---|"]
    for e in events:
        lines.append(f"| {fmt_t(e['t'])} | {e['block']}{(' ' + e['rank']) if e['rank'] else ''} | "
                     f"{('«' + e['text'] + '»') if e['text'] else ''} | {e['dur']:.2f} s |")
    lines += ["", "## Notas del director (omitido / descartado / gap)"]
    lines += [f"- {n}" for n in notes] or ["- (ninguna)"]
    from gfx_config import gfx_rules
    lines += ["", f"## gap_warning (> {gfx_rules.interrupt_max_sec:.0f} s sin bloque)"]
    lines += [f"- {fmt_t(a)} → {fmt_t(b)} ({b - a:.1f} s)" for a, b in gaps] or ["- (ninguno)"]
    count = Counter(e["block"].split(":")[0] for e in events)
    lines += ["", "## Bloques por tipo"] + [f"- {k}: {v}" for k, v in sorted(count.items())]
    lines += ["", f"Tiempo de render del cap: {render_sec:.1f} s" if render_sec is not None else "Tiempo de render: —"]
    md = work_dir / f"gfx_cues_{cap}.md"
    md.write_text("\n".join(lines) + "\n", encoding="utf-8")
    (work_dir / f"gfx_cues_{cap}.json").write_text(
        json.dumps({"cap": cap, "events": events, "notes": notes, "gaps": gaps, "render_sec": render_sec},
                   ensure_ascii=False, indent=1), encoding="utf-8")
    return md


_PAGE = """<!doctype html>
<html lang="es"><head><meta charset="UTF-8" /><title>gfx review __CAP__</title>
<style>
  body { margin: 0; background: #111; color: #eee; font: 15px/1.4 system-ui, sans-serif; display: flex; height: 100vh; }
  #left { flex: 1; display: flex; flex-direction: column; padding: 12px; gap: 8px; min-width: 0; }
  video { width: 100%; max-height: 80vh; background: #000; }
  #note { display: flex; gap: 8px; } #note input { flex: 1; padding: 6px; background: #222; color: #eee; border: 1px solid #444; }
  button { padding: 6px 12px; background: #c8102e; color: #fff; border: 0; cursor: pointer; }
  #cues { width: 420px; overflow-y: auto; border-left: 1px solid #333; }
  .cue { padding: 6px 10px; border-bottom: 1px solid #222; cursor: pointer; }
  .cue:hover { background: #222; } .cue.on { background: #3a1016; }
  .t { font-family: Consolas, monospace; color: #f4c542; } .b { color: #8fd; } .n { color: #f99; font-size: 13px; }
</style></head><body>
<div id="left">
  <video id="v" src="__VIDEO__" controls preload="auto"></video>
  <div id="note"><input id="c" placeholder="comentario sobre el instante actual" /><button id="copy">copiar nota</button></div>
  <div id="msg"></div>
</div>
<div id="cues"></div>
<script>
var CAP = "__CAP__", DATA = __DATA__;
var v = document.getElementById("v"), box = document.getElementById("cues");
function fmt(t) { var m = Math.floor(t / 60), s = (t % 60).toFixed(1); return (m < 10 ? "0" : "") + m + ":" + (s < 10 ? "0" : "") + s; }
DATA.events.forEach(function (e, i) {
  var d = document.createElement("div"); d.className = "cue"; d.id = "q" + i;
  d.innerHTML = '<span class="t">' + fmt(e.t) + '</span> <span class="b">' + e.block + (e.rank ? " " + e.rank : "") + '</span> '
    + (e.text ? "«" + e.text.replace(/</g, "&lt;") + "»" : "") + ' <span class="t">' + e.dur.toFixed(2) + ' s</span>';
  d.onclick = function () { v.currentTime = e.t; v.play(); };
  box.appendChild(d);
});
DATA.notes.concat(DATA.gaps.map(function (g) { return "gap_warning " + fmt(g[0]) + "–" + fmt(g[1]); })).forEach(function (n) {
  var d = document.createElement("div"); d.className = "cue n"; d.textContent = n; box.appendChild(d);
});
v.ontimeupdate = function () {
  DATA.events.forEach(function (e, i) {
    document.getElementById("q" + i).classList.toggle("on", v.currentTime >= e.t && v.currentTime < e.t + Math.max(e.dur, 0.3));
  });
};
document.getElementById("copy").onclick = function () {
  var txt = CAP + " @ " + fmt(v.currentTime) + " — " + document.getElementById("c").value;
  (navigator.clipboard ? navigator.clipboard.writeText(txt) : Promise.reject()).then(
    function () { document.getElementById("msg").textContent = "copiado: " + txt; },
    function () { document.getElementById("msg").textContent = txt; });
};
</script></body></html>
"""


def write_review(cap: str, segment_path: Path, work_dir: Path) -> Path | None:
    """Página de revisión del segmento. None si no hay cues (p.ej. el cap cayó en fallback)."""
    cues = work_dir / f"gfx_cues_{cap}.json"
    if not cues.exists():
        return None
    data = json.loads(cues.read_text(encoding="utf-8"))
    page = (_PAGE.replace("__CAP__", html.escape(cap))
                 .replace("__VIDEO__", html.escape(Path(segment_path).name))
                 .replace("__DATA__", json.dumps(data, ensure_ascii=False).replace("</", "<\\/")))
    out = work_dir / f"gfx_review_{cap}.html"
    out.write_text(page, encoding="utf-8")
    return out
