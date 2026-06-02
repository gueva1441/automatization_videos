"""
test_module_40_rerun_encoding.py — GATE FIX-CC (chat 40, fix encoding del /rerun).

El smoke del Bloque 7 usó un stub ASCII → NO cazó el cp1252. Este SÍ: el stub imprime
emoji utf-8 (lo que fase2b emite). Antes del fix, el lector se caía con
UnicodeDecodeError y rc=-1. Tras el fix (encoding="utf-8", errors="replace") el log se
lee completo y rc=0.

USO:
    python test_module_40_rerun_encoding.py
"""
from __future__ import annotations

import sys
import time

import mixer_server as M


def _run_stub_and_wait(cmd: list[str], timeout: float = 8.0) -> dict:
    orig = M._rerun_command
    M._rerun_command = lambda: cmd
    try:
        M._start_rerun()
        deadline = time.monotonic() + timeout
        while M._rerun_status()["running"] and time.monotonic() < deadline:
            time.sleep(0.1)
        # log_tail con bastante margen para ver todo
        with M._RERUN_LOCK:
            full_log = list(M._RERUN["log"])
        st = M._rerun_status()
        st["full_log"] = full_log
        return st
    finally:
        M._rerun_command = orig


def main() -> int:
    fails: list[str] = []

    # ── 1. stub con emoji utf-8 (lo que fase2b imprime) ──
    print("  [1] stub con emoji utf-8 → log se lee, rc=0, sin UnicodeDecodeError")
    st = _run_stub_and_wait([
        sys.executable, "-c",
        "import sys; sys.stdout.reconfigure(encoding='utf-8'); "
        "print('✅ música mezclada'); print('[ch04] (json)')",
    ])
    log = st["full_log"]
    no_crash = not any("UnicodeDecodeError" in ln for ln in log)
    rc0 = st["returncode"] == 0
    has_emoji = any("✅ música mezclada" in ln for ln in log)
    print(f"      rc={st['returncode']} | sin UnicodeDecodeError={no_crash} | "
          f"emoji decodificado={has_emoji}")
    print(f"      log: {log}")
    if not rc0: fails.append(f"1: rc={st['returncode']} != 0")
    if not no_crash: fails.append("1: hubo UnicodeDecodeError en el log")
    if not has_emoji: fails.append("1: no se encontró la línea con emoji bien decodificada")

    # ── 2. (opcional) byte inválido crudo → errors='replace' no tumba el lector ──
    print("  [2] byte inválido crudo → errors='replace', lector NO se cae (rc=0)")
    st2 = _run_stub_and_wait([
        sys.executable, "-c",
        # escribe un byte 0x90 crudo a stdout binario (inválido en utf-8) + una línea ok
        "import sys; sys.stdout.buffer.write(b'\\x90 raw\\n'); sys.stdout.buffer.flush(); "
        "print('ok-despues-del-byte')",
    ])
    log2 = st2["full_log"]
    no_crash2 = not any("UnicodeDecodeError" in ln for ln in log2)
    rc0_2 = st2["returncode"] == 0
    survived = any("ok-despues-del-byte" in ln for ln in log2)
    print(f"      rc={st2['returncode']} | sin UnicodeDecodeError={no_crash2} | "
          f"siguió leyendo tras el byte={survived}")
    print(f"      log: {log2}")
    if not rc0_2: fails.append(f"2: rc={st2['returncode']} != 0")
    if not no_crash2: fails.append("2: el byte inválido tumbó el lector")
    if not survived: fails.append("2: no leyó la línea posterior al byte inválido")

    print("\n" + "─" * 56)
    if fails:
        print(f"  [FAIL] {len(fails)} chequeo(s):")
        for x in fails:
            print(f"    - {x}")
        return 1
    print("  [OK] GATE FIX-CC: encoding utf-8 en el /rerun (emoji + byte inválido).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
