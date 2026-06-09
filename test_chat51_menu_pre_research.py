"""
test_chat51_menu_pre_research.py — valida el menú RICO sobre SEEDS antes del research
(CHAT 51), SIN red ni Gemini. Cubre §3 del handoff.

POR QUÉ: hoy el research caro corre sobre el lote entero y el menú recién aparece DESPUÉS
(sobre topics ya investigados) → se tira el research de N-1. El fix invierte el orden:
seeds → juez → MENÚ ($0) → research SOLO del elegido.

Cubre:
  A) _select_seed_interactive (menú directo):
     - ordena oro→dudoso→descartar, tolera None (channel_median/en_age_months/heaviest).
     - Q → None (no se investiga nada). Multi-select "1,2" → 2 seeds.
  B) run_latido_a (wiring, todo mockeado):
     - auto-exclusión descartar-3/3 antes del menú (ese seed ni se muestra).
     - tras elegir, research_topics se llama con lista de UN solo seed (no el lote).
     - Q → research_topics NO se llama.

Correr:  python -X utf8 test_chat51_menu_pre_research.py
"""
from __future__ import annotations

import builtins
import io
import sys
from contextlib import redirect_stdout
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import fase1
from fase1 import _select_seed_interactive


def _seed(title, verdict, cohort, views, ratio, age, label="VACIO", ontopic=0,
          heaviest=None, channel_median=12345, reason="motivo"):
    return {
        "seed_id": f"id_{title}",
        "seed_title": title,
        "discovery_mode": "spy_arbitrage",
        "judge": {"verdict": verdict, "cohort": cohort, "risk": "ninguno", "reason": reason},
        "evidence": {
            "en_viral": {
                "original_title": f"{title} EN viral",
                "views": views,
                "query": title,
                "outlier_ratio": ratio,
                "channel_median": channel_median,
                "en_age_months": age,
            },
            "es_gap": {"label": label, "heaviest": heaviest, "ontopic_count": ontopic},
        },
    }


def _stub_input(answers):
    """Devuelve un input() que consume respuestas en orden."""
    q = list(answers)

    def _fn(prompt=""):
        return q.pop(0)
    return _fn


def run():
    failures = []

    def check(cond, msg):
        print(f"  [{'✓' if cond else '✗'}] {msg}")
        if not cond:
            failures.append(msg)

    orig_input = builtins.input

    # ── A) menú directo: orden + tolerancia a None + Q + multi ──
    print("A — _select_seed_interactive: orden oro→dudoso, tolerancia None, Q, multi\n")

    seeds = [
        _seed("Dudoso Tema", "dudoso", "2/3", 1_000_000, 5.0, 2),
        _seed("Oro Bajo", "oro", "2/3", 800_000, 8.0, 3),
        _seed("Oro Alto", "oro", "3/3", 3_200_000, 14.0, 4),
        # edge fan-out: sin channel_id → median None, ratio 0.0, edad None, heaviest None
        _seed("Fanout Sin Canal", "oro", "2/3", 600_000, 0.0, None,
              channel_median=None, heaviest=None),
    ]

    # elegir [1] → debe ser un ORO (rank 0), y el de mayor views entre los oro = "Oro Alto"
    try:
        builtins.input = _stub_input(["1"])
        buf = io.StringIO()
        with redirect_stdout(buf):
            chosen = _select_seed_interactive(seeds)
        out = buf.getvalue()
    finally:
        builtins.input = orig_input

    check(chosen is not None and len(chosen) == 1, "elegir '1' → 1 seed")
    check(chosen and chosen[0]["seed_title"] == "Oro Alto",
          f"orden: [1] es el oro de mayor demanda ('Oro Alto'): {chosen and chosen[0]['seed_title']!r}")
    # el dudoso aparece DESPUÉS de los 3 oro en el texto
    pos_oro = out.find("Oro Alto")
    pos_dudoso = out.find("Dudoso Tema")
    check(0 <= pos_oro < pos_dudoso, "oro listado ANTES que dudoso")
    # tolerancia None: no crasheó y muestra '—' / 'desconocida'
    check("ratio —" in out, "ratio None/0.0 → muestra '—' (tolerancia, sin crash)")
    check("desconocida" in out, "en_age_months None → muestra 'desconocida'")

    # Q → None
    try:
        builtins.input = _stub_input(["Q"])
        with redirect_stdout(io.StringIO()):
            r = _select_seed_interactive(seeds)
    finally:
        builtins.input = orig_input
    check(r is None, "Q → None (no se investiga nada)")

    # multi "1,2" → 2 seeds
    try:
        builtins.input = _stub_input(["1,2"])
        with redirect_stdout(io.StringIO()):
            r = _select_seed_interactive(seeds)
    finally:
        builtins.input = orig_input
    check(r is not None and len(r) == 2, f"multi '1,2' → 2 seeds: {len(r) if r else 0}")

    # seeds vacío → None sin crash
    try:
        builtins.input = _stub_input([])
        with redirect_stdout(io.StringIO()):
            r = _select_seed_interactive([])
    finally:
        builtins.input = orig_input
    check(r is None, "seeds vacío → None sin crash")

    # ── B) wiring en run_latido_a: auto-exclusión + research_topics con lista de 1 ──
    print("\nB — run_latido_a: descartar-3/3 excluido, research SOLO del elegido\n")

    all_seeds = [
        _seed("Oro Alto", "oro", "3/3", 3_200_000, 14.0, 4),
        _seed("Dudoso Tema", "dudoso", "2/3", 1_000_000, 5.0, 2),
        _seed("Basura 33", "descartar", "3/3", 90_000, 1.0, 30),   # debe auto-excluirse
    ]

    # monkeypatch de todo lo caro / interactivo
    import script_engine.m_judge_seeds as mj
    import fase1_5

    saved = {
        "load_seeds": fase1._load_seeds,
        "save": fase1._save_seeds_with_judge,
        "judge": mj.judge_seeds,
        "research": fase1.research_topics,
        "load_db": fase1.load_db,
        "validate": fase1.validate_topics,
        "export": fase1.export_fase1_csv,
        "summary": fase1.print_export_summary,
        "menu_end": getattr(fase1_5, "run_one_topic_from_menu", None),
    }
    captured = {"calls": []}
    try:
        fase1._load_seeds = lambda: [dict(s) for s in all_seeds]
        fase1._save_seeds_with_judge = lambda s: None
        mj.judge_seeds = lambda s: s                      # judge ya puesto en los fakes
        fase1.research_topics = lambda lst, video_type=None: captured["calls"].append(
            [x["seed_title"] for x in lst])
        fase1.load_db = lambda: {"topics": [{"id": "t1", "status": "validated"}]}
        fase1.validate_topics = lambda video_type=None: None
        fase1.export_fase1_csv = lambda: Path("data/fase1_review.csv")
        fase1.print_export_summary = lambda p: None
        fase1_5.run_one_topic_from_menu = lambda *a, **k: 0

        # elegir "2" sobre la lista YA ordenada+filtrada (oro, dudoso) → 'Dudoso Tema'
        builtins.input = _stub_input(["2"])
        buf = io.StringIO()
        with redirect_stdout(buf):
            fase1.run_latido_a(video_type="long", skip_niche=True)
        out_b = buf.getvalue()
    finally:
        builtins.input = orig_input
        fase1._load_seeds = saved["load_seeds"]
        fase1._save_seeds_with_judge = saved["save"]
        mj.judge_seeds = saved["judge"]
        fase1.research_topics = saved["research"]
        fase1.load_db = saved["load_db"]
        fase1.validate_topics = saved["validate"]
        fase1.export_fase1_csv = saved["export"]
        fase1.print_export_summary = saved["summary"]
        if saved["menu_end"] is not None:
            fase1_5.run_one_topic_from_menu = saved["menu_end"]

    # el descartar-3/3 puede aparecer en el resumen del juez / mensaje de exclusión (correcto);
    # lo que importa es que NO esté DENTRO del menú de selección.
    menu_section = out_b[out_b.find("SELECCIÓN DE TEMA (antes del research)"):]
    check("Basura 33" not in menu_section,
          "descartar-3/3 NO se muestra DENTRO del menú (auto-exclusión)")
    check(len(captured["calls"]) == 1, f"research_topics se llamó 1 vez: {len(captured['calls'])}")
    check(captured["calls"] and len(captured["calls"][0]) == 1,
          f"research_topics recibió lista de UN solo seed: "
          f"{captured['calls'][0] if captured['calls'] else None}")
    check(captured["calls"] and captured["calls"][0] == ["Dudoso Tema"],
          f"investigó el elegido ('Dudoso Tema'), no el lote: "
          f"{captured['calls'][0] if captured['calls'] else None}")

    # ── B2) Q en el menú → research_topics NO se llama ──
    print("\nB2 — Q en el menú → no se investiga nada\n")
    captured2 = {"calls": []}
    try:
        fase1._load_seeds = lambda: [dict(s) for s in all_seeds]
        fase1._save_seeds_with_judge = lambda s: None
        mj.judge_seeds = lambda s: s
        fase1.research_topics = lambda lst, video_type=None: captured2["calls"].append(lst)
        fase1.load_db = lambda: {"topics": [{"id": "t1", "status": "validated"}]}
        fase1.validate_topics = lambda video_type=None: None
        fase1.export_fase1_csv = lambda: Path("data/fase1_review.csv")
        fase1.print_export_summary = lambda p: None
        fase1_5.run_one_topic_from_menu = lambda *a, **k: 0

        builtins.input = _stub_input(["Q"])
        with redirect_stdout(io.StringIO()):
            fase1.run_latido_a(video_type="long", skip_niche=True)
    finally:
        builtins.input = orig_input
        fase1._load_seeds = saved["load_seeds"]
        fase1._save_seeds_with_judge = saved["save"]
        mj.judge_seeds = saved["judge"]
        fase1.research_topics = saved["research"]
        fase1.load_db = saved["load_db"]
        fase1.validate_topics = saved["validate"]
        fase1.export_fase1_csv = saved["export"]
        fase1.print_export_summary = saved["summary"]
        if saved["menu_end"] is not None:
            fase1_5.run_one_topic_from_menu = saved["menu_end"]

    check(len(captured2["calls"]) == 0, "Q → research_topics NO se llamó (0 gasto)")

    print("\n" + ("✅ TODOS OK" if not failures else f"❌ {len(failures)} FALLO(S): " + "; ".join(failures)))
    return 0 if not failures else 1


if __name__ == "__main__":
    sys.exit(run())
