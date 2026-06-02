"""
test_module_40_mixer_save.py — Smoke AISLADO del mixer multi-cap (chat 40 bloque 4).
GATE 4-CC. NO escribe en jsons reales (usa un DUMMY copiado).

Casos:
  1. _write_volume_to_json (el corazón de /save): sobre un json DUMMY, escribe SOLO
     las 2 claves y deja TODO el resto intacto (compara todas las demás keys).
  2. _track_mp3_and_json resuelve los 7 caps del Tuskegee (mp3 + json en disco).
  3. _suggested_start(cap) devuelve el SAVED del json (shock_curated ya tiene 0.08/0.03).
  4. _caps_list lista los 7 con su track_id; _preflight sin problemas.

USO:
    python test_module_40_mixer_save.py
"""
from __future__ import annotations

import json
import shutil
import sys
import tempfile
from pathlib import Path

import mixer_server as M

REAL_JSON = Path("audio_library/hook_curated.json").resolve()  # sin claves de volumen


def main() -> int:
    # Cargar el music_map del topic cableado (como hace main()).
    M._set_topic(M.TOPIC_ID)
    try:
        M.MUSIC_MAP = M._load_music_map()
    except Exception as e:  # noqa: BLE001
        print(f"[FAIL] no se pudo cargar music_map: {e}"); return 1

    fails: list[str] = []
    tmp = Path(tempfile.mkdtemp(prefix="mixer_save_"))
    try:
        # ── 1. write quirúrgico sobre DUMMY ──
        print("  [1] _write_volume_to_json sobre json DUMMY (resto intacto)")
        dummy = tmp / "dummy.json"
        shutil.copy(REAL_JSON, dummy)
        before = json.loads(dummy.read_text(encoding="utf-8"))
        meta = M._write_volume_to_json(dummy, 0.123, 0.0456)   # mvf redondea a 0.046
        after = json.loads(dummy.read_text(encoding="utf-8"))
        ok_keys = (after.get("music_volume") == 0.123 and after.get("music_volume_floor") == 0.046)
        # todo lo demás idéntico al original
        rest_before = {k: v for k, v in before.items() if k not in ("music_volume", "music_volume_floor")}
        rest_after = {k: v for k, v in after.items() if k not in ("music_volume", "music_volume_floor")}
        ok_rest = rest_before == rest_after
        added = set(after) - set(before)
        print(f"      claves escritas: mv={after.get('music_volume')} floor={after.get('music_volume_floor')}  "
              f"{'OK' if ok_keys else 'FAIL'}")
        print(f"      resto del json intacto: {'OK' if ok_rest else 'FAIL'}  "
              f"(claves nuevas: {sorted(added)})")
        if not ok_keys: fails.append("1: claves no escritas/redondeadas mal")
        if not ok_rest: fails.append("1: el resto del json cambió")

        # ── 2. resolución cap→mp3+json para los 7 ──
        print("  [2] _track_mp3_and_json resuelve los 7 caps")
        for c in M._caps_list():
            cap = c["cap"]
            try:
                mp3, jsn = M._track_mp3_and_json(cap)
                ok = mp3.exists() and jsn.exists() and M._voice_path(cap).exists()
                print(f"      {cap} — {c['track_id']:<24} mp3+json+voz {'OK' if ok else 'FAIL'}")
                if not ok: fails.append(f"2: {cap} falta mp3/json/voz")
            except Exception as e:  # noqa: BLE001
                fails.append(f"2: {cap} {type(e).__name__}: {e}")
                print(f"      {cap} FAIL {e}")

        # ── 3. suggested_start devuelve el saved del shock ──
        print("  [3] _suggested_start('ch04') trae saved 0.08/0.03 del json real")
        ss = M._suggested_start("ch04")
        ok = ss["music_volume_saved"] == 0.08 and ss["music_volume_floor_saved"] == 0.03
        print(f"      saved={ss['music_volume_saved']}/{ss['music_volume_floor_saved']} "
              f"| suggested(medido)={ss['music_volume_suggested']}/{ss['music_volume_floor_suggested']} "
              f"| track={ss['track_id']}  {'OK' if ok else 'FAIL'}")
        if not ok: fails.append(f"3: saved shock {ss['music_volume_saved']}/{ss['music_volume_floor_saved']} != 0.08/0.03")
        # un cap sin calibrar → saved None
        ss1 = M._suggested_start("ch01")
        ok2 = ss1["music_volume_saved"] is None
        print(f"      ch01 (sin calibrar) saved={ss1['music_volume_saved']}  {'OK' if ok2 else 'FAIL'}")
        if not ok2: fails.append("3: ch01 debería tener saved=None")

        # ── 4. caps + preflight ──
        print("  [4] _caps_list (7) + _preflight limpio")
        caps = M._caps_list()
        ok_caps = len(caps) == 7
        problems = M._preflight()
        ok_pre = len(problems) == 0
        print(f"      caps={len(caps)} {'OK' if ok_caps else 'FAIL'} | "
              f"preflight {'OK' if ok_pre else 'FAIL ' + str(problems)}")
        if not ok_caps: fails.append(f"4: caps={len(caps)} != 7")
        if not ok_pre: fails.append(f"4: preflight {problems}")

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n" + "─" * 56)
    if fails:
        print(f"  [FAIL] {len(fails)} chequeo(s):")
        for x in fails: print(f"    - {x}")
        return 1
    print("  [OK] GATE 4-CC: 4/4 verde. /save no tocó jsons reales (dummy).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
