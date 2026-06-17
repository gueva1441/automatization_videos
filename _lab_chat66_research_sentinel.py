"""
_lab_chat66_research_sentinel.py — lab read-only (HANDOFF 66a).

Aísla la lógica de resolución de tid del path --research: monkeypatcha el sentinel a un tmp +
fake topics_db, mockea _run (fase1) y sequence(), y afirma qué tid recibiría sequence() o si
NO se llama. NO toca prod (ni el DB real ni el sentinel real).

  C1 — control known-good / repro en verde: sentinel con 1 tid nuevo + DB con un 'validated'
       leftover distinto → resuelve al tid del sentinel, ignora el leftover, sequence(tid_correcto).
  C2 — pick soltado: sentinel [] (o ausente) → --research retorna 0, sequence() NO se llama.
  C3 — desempate sin colgar: sentinel con 2 tids → _newest_validated por validated_at, cero input().
"""
from __future__ import annotations
import json, tempfile, pathlib, sys
import run_pipeline as rp
from script_engine import topics_db


def _run_research(sentinel_tids, db_topics):
    """Corre el path args.research con todo mockeado. Devuelve (rc, tid_secuenciado|None)."""
    tmp = pathlib.Path(tempfile.mkdtemp()) / "_last_research.json"
    if sentinel_tids is not None:
        tmp.write_text(json.dumps({"tids": sentinel_tids, "at": "x"}), encoding="utf-8")

    seq_calls = []
    orig = {
        "SENT": rp.RESEARCH_SENTINEL,
        "_run": rp._run,
        "sequence": rp.sequence,
        "load_db": topics_db.load_db,
        "input": __builtins__["input"] if isinstance(__builtins__, dict) else __builtins__.input,
    }
    rp.RESEARCH_SENTINEL = tmp
    rp._run = lambda *a, **k: 0                      # fase1 sale OK (exit 0)
    rp.sequence = lambda tid, **k: (seq_calls.append(tid) or 0)
    topics_db.load_db = lambda: {"topics": db_topics}
    # input() debe COLGAR si alguien lo llama (el bug hermano): lo hacemos explotar.
    import builtins
    orig_input = builtins.input
    builtins.input = lambda *a, **k: (_ for _ in ()).throw(AssertionError("input() NO debe llamarse"))

    sys.argv = ["run_pipeline.py", "--research"]
    try:
        rc = rp.main()
    finally:
        rp.RESEARCH_SENTINEL = orig["SENT"]; rp._run = orig["_run"]; rp.sequence = orig["sequence"]
        topics_db.load_db = orig["load_db"]; builtins.input = orig_input
    return rc, (seq_calls[0] if seq_calls else None)


def _topic(tid, ts=None):
    t = {"id": tid, "status": "validated"}
    if ts is not None:
        t["competition_data"] = {"validated_at": ts}
    return t


# C1 — sentinel con tid NUEVO + leftover viejo en el DB → ignora el leftover
rc, tid = _run_research(["new-tid-001"], [_topic("old-leftover-999"), _topic("new-tid-001")])
assert rc == 0 and tid == "new-tid-001", (rc, tid)
print("OK C1: resuelve al sentinel, ignora el leftover viejo")

# C2 — pick soltado: sentinel [] → NO secuencia
rc, tid = _run_research([], [_topic("old-leftover-999")])
assert rc == 0 and tid is None, (rc, tid)
print("OK C2 (vacío): no secuencia")
# C2b — sentinel ausente → idem
rc, tid = _run_research(None, [_topic("old-leftover-999")])
assert rc == 0 and tid is None, (rc, tid)
print("OK C2b (ausente): no secuencia")

# C3 — 2 tids → desempate por validated_at (más nuevo), SIN input()
rc, tid = _run_research(["a", "b"], [_topic("a", "2026-01-01"), _topic("b", "2026-06-01")])
assert rc == 0 and tid == "b", (rc, tid)
print("OK C3: desempate por validated_at (b más nuevo), sin colgar")

print("LAB 66a PASS")
