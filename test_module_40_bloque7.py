"""
test_module_40_bloque7.py — GATE 7-CC (chat 40 bloque 7). AISLADO, NO corre fase2b real.

Casos:
  1. _topic_info devuelve el topic_id (y title si aplica).
  2. mixer.html sirve la lógica de grisar caps skipped ('(sin track)' + disabled).
  3. Lanzar el server con --topic inexistente → muere con mensaje claro, NO abre server.
  4. State machine de /rerun con un STUB rápido (NO fase2b real): 1er start → running;
     2º start mientras corre → conflict (409); al terminar → running=False, rc=0,
     log_tail con la salida del stub.

USO:
    python test_module_40_bloque7.py
"""
from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

import mixer_server as M

HTML = Path("mixer.html")


def main() -> int:
    fails: list[str] = []

    # ── 1. /topic ──
    print("  [1] _topic_info devuelve el topic_id")
    info = M._topic_info()
    ok = info.get("topic_id") == M.TOPIC_ID and "title" in info
    print(f"      topic_id={info.get('topic_id')[:8]}… title={info.get('title')!r}  "
          f"{'OK' if ok else 'FAIL'}")
    if not ok:
        fails.append("1: _topic_info sin topic_id/title")

    # ── 2. html grisa caps skipped ──
    print("  [2] mixer.html grisa caps skipped")
    html = HTML.read_text(encoding="utf-8")
    ok = "(sin track)" in html and "o.disabled = true" in html
    print(f"      '(sin track)'={'(sin track)' in html} | disabled-logic="
          f"{'o.disabled = true' in html}  {'OK' if ok else 'FAIL'}")
    if not ok:
        fails.append("2: html sin lógica de grisado")

    # ── 3. --topic inexistente → muere con mensaje claro, NO abre server ──
    print("  [3] server con --topic inexistente muere con mensaje claro")
    r = subprocess.run(
        [sys.executable, "mixer_server.py", "--topic", "zzz-topic-inexistente-000"],
        cwd=str(M.BASE_DIR), capture_output=True, text=True,
        encoding="utf-8", errors="replace", timeout=30)
    out = r.stdout + r.stderr
    ok = (r.returncode != 0 and "no tiene assets de audio" in out
          and "fase1_5 + fase2a" in out)
    print(f"      exit={r.returncode} (≠0) | mensaje accionable={'no tiene assets de audio' in out}  "
          f"{'OK' if ok else 'FAIL'}")
    if not ok:
        fails.append(f"3: no murió bien (exit={r.returncode}, out={out[:160]!r})")

    # ── 4. state machine de /rerun con STUB (NO fase2b real) ──
    print("  [4] /rerun state machine con stub rápido")
    orig_cmd = M._rerun_command
    M._rerun_command = lambda: [
        sys.executable, "-c",
        "import time,sys; print('[ch04] track=shock_curated ducked=0.080 floor=0.030 (json)'); "
        "sys.stdout.flush(); time.sleep(0.6); print('listo-stub')",
    ]
    try:
        r1 = M._start_rerun()
        running_now = M._rerun_status()["running"]
        r2 = M._start_rerun()                     # 2º mientras corre → conflict
        ok_start = r1.get("started") is True
        ok_running = running_now is True
        ok_conflict = r2.get("conflict") is True
        print(f"      1er start={r1} running={running_now} | 2º start={r2}  "
              f"{'OK' if (ok_start and ok_running and ok_conflict) else 'FAIL'}")
        if not ok_start: fails.append("4: 1er /rerun no arrancó")
        if not ok_running: fails.append("4: no quedó running tras start")
        if not ok_conflict: fails.append("4: 2º /rerun no dio conflict")

        # esperar a que el stub termine
        deadline = time.monotonic() + 8
        while M._rerun_status()["running"] and time.monotonic() < deadline:
            time.sleep(0.1)
        st = M._rerun_status()
        ok_done = (st["running"] is False and st["returncode"] == 0)
        ok_log = any("listo-stub" in ln for ln in st["log_tail"]) and \
                 any("(json)" in ln for ln in st["log_tail"])
        print(f"      al terminar: running={st['running']} rc={st['returncode']} | "
              f"log_tail tiene salida del stub={ok_log}  "
              f"{'OK' if (ok_done and ok_log) else 'FAIL'}")
        if not ok_done: fails.append(f"4: no terminó limpio (running={st['running']} rc={st['returncode']})")
        if not ok_log: fails.append(f"4: log_tail sin salida del stub: {st['log_tail']}")
    finally:
        M._rerun_command = orig_cmd

    print("\n" + "─" * 56)
    if fails:
        print(f"  [FAIL] {len(fails)} chequeo(s):")
        for x in fails:
            print(f"    - {x}")
        return 1
    print("  [OK] GATE 7-CC: 4/4 verde. (stub, NO corrió fase2b real)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
