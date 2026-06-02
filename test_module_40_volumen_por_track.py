"""
test_module_40_volumen_por_track.py — Smoke del volumen de música POR TRACK (chat 40).

⚠ A diferencia del smoke del chat 39 (que armaba a mano un `mixing` con
music_by_intent adentro → nunca ejercía el camino real), este test NO inventa los
números: lee jsons REALES de audio_library/ vía un music_map sintético, que es
exactamente lo que hace el pipeline en producción (_resolve_music_volumes).

Casos:
  1. Shock calibrado: music_map → shock_curated (json con 0.08/0.03) ⇒ 0.08/0.03.
  2. Track sin claves → base: un track no-shock (json sin las claves) ⇒ 0.26/0.16.
  3. Json ilegible → base + warning: json corrupto ⇒ no crashea, cae a base.
  4. Cap sin entry en music_map → base.
  5. REGRESIÓN chat 32: _mix_music_into_video(music_floor_path=None) sigue intacto
     (la rama vieja del filter_complex sigue viva, sin tocar).

USO:
    python test_module_40_volumen_por_track.py
"""
from __future__ import annotations

import inspect
import shutil
import sys
from pathlib import Path

import audio_profiles
from fase2b import ChapterPlan, _mix_music_into_video, _resolve_music_volumes

# Base del perfil real (fallback esperado para tracks sin calibrar).
MIXING = dict(audio_profiles.AUDIO_PROFILES["MISTERIO_ABISAL"]["mixing"])
BASE_VOL = float(MIXING["music_volume"])      # 0.26
BASE_FLR = float(MIXING["music_volume_floor"])  # 0.16


def _plan(cid: str) -> ChapterPlan:
    # narrative_intent ya NO decide el volumen (chat 40); se setea solo porque el
    # campo existe (voice settings lo usa). Acá da igual.
    return ChapterPlan(
        chapter_id=cid, engine="flux", audio_path=Path(f"{cid}.mp3"),
        audio_duration=8.0, asset_paths=[], timestamps_path=None,
        is_first=False, art_profile=None, narrative_intent="shock",
    )


def _entry(track_id: str, mp3_rel: str) -> dict:
    return {"track_id": track_id, "mp3_path": mp3_rel, "match_source": "reused"}


def main() -> int:
    fails: list[str] = []
    # tmp DENTRO del repo para que mp3_path relativo resuelva contra BASE_DIR.
    tmp = Path("_tmp_test40").resolve()
    tmp.mkdir(exist_ok=True)
    try:
        # ── Caso 1: shock calibrado (json real con 0.08/0.03) ──
        print("  [1] shock_curated (json real 0.08/0.03)")
        mm = {"ch04": _entry("shock_curated", "audio_library/shock_curated.mp3")}
        d, f = _resolve_music_volumes([_plan("ch04")], MIXING, mm)
        ok = abs(d["ch04"] - 0.08) < 1e-9 and abs(f["ch04"] - 0.03) < 1e-9
        print(f"      ch04 ducked={d['ch04']:.3f} floor={f['ch04']:.3f}  "
              f"(esperado 0.080/0.030)  {'OK' if ok else 'FAIL'}")
        if not ok:
            fails.append(f"1: shock {d['ch04']}/{f['ch04']} != 0.08/0.03")

        # ── Caso 2: track no-shock sin claves → base ──
        print("  [2] setup_curated (json real SIN claves) → base")
        mm = {"ch01": _entry("setup_curated", "audio_library/setup_curated.mp3")}
        d, f = _resolve_music_volumes([_plan("ch01")], MIXING, mm)
        ok = abs(d["ch01"] - BASE_VOL) < 1e-9 and abs(f["ch01"] - BASE_FLR) < 1e-9
        print(f"      ch01 ducked={d['ch01']:.3f} floor={f['ch01']:.3f}  "
              f"(esperado base {BASE_VOL}/{BASE_FLR})  {'OK' if ok else 'FAIL'}")
        if not ok:
            fails.append(f"2: setup {d['ch01']}/{f['ch01']} != base")

        # ── Caso 3: json ilegible → base + warning (no crashea) ──
        print("  [3] json corrupto → base + warning (no crashea)")
        (tmp / "badtrack.mp3").write_bytes(b"\x00")           # mp3 debe existir
        (tmp / "badtrack.json").write_text("{ esto no es json", encoding="utf-8")
        mm = {"ch02": _entry("badtrack", "_tmp_test40/badtrack.mp3")}
        try:
            d, f = _resolve_music_volumes([_plan("ch02")], MIXING, mm)
            ok = abs(d["ch02"] - BASE_VOL) < 1e-9 and abs(f["ch02"] - BASE_FLR) < 1e-9
            print(f"      ch02 ducked={d['ch02']:.3f} floor={f['ch02']:.3f}  "
                  f"(esperado base, sin crash)  {'OK' if ok else 'FAIL'}")
            if not ok:
                fails.append(f"3: corrupto {d['ch02']}/{f['ch02']} != base")
        except Exception as e:  # noqa: BLE001
            fails.append(f"3: crasheó con json corrupto ({type(e).__name__})")
            print(f"      [FAIL] crasheó: {e}")

        # ── Caso 4: cap sin entry en music_map → base ──
        print("  [4] cap sin entry en music_map → base")
        d, f = _resolve_music_volumes([_plan("ch99")], MIXING, {})  # music_map vacío
        ok = abs(d["ch99"] - BASE_VOL) < 1e-9 and abs(f["ch99"] - BASE_FLR) < 1e-9
        print(f"      ch99 ducked={d['ch99']:.3f} floor={f['ch99']:.3f}  "
              f"(esperado base)  {'OK' if ok else 'FAIL'}")
        if not ok:
            fails.append(f"4: sin entry {d['ch99']}/{f['ch99']} != base")

        # ── Caso 5: regresión chat 32 (rama music_floor_path=None intacta) ──
        print("  [5] regresión chat 32: _mix_music_into_video rama vieja viva")
        sig = inspect.signature(_mix_music_into_video)
        default_none = sig.parameters["music_floor_path"].default is None
        src = inspect.getsource(_mix_music_into_video)
        # marcadores de la rama chat 32 (volumen global, asplit en 2)
        chat32_alive = ("asplit=2[music_a][music_b]" in src
                        and "volume={music_volume}" in src)
        # marcadores de la rama chat 39/40 (2 WAVs, sin volume= horneado)
        percap_alive = "[music_ducked_src][narr_sc]sidechaincompress" in src
        # sidechain params NO tocados (mismos nombres de param)
        sidechain_intact = all(k in src for k in
                               ("threshold={duck_threshold}", "ratio={duck_ratio}",
                                "attack={duck_attack_ms}", "release={duck_release_ms}"))
        ok = default_none and chat32_alive and percap_alive and sidechain_intact
        print(f"      floor_path default None={default_none} | rama chat32={chat32_alive} | "
              f"rama por-cap={percap_alive} | sidechain intacto={sidechain_intact}  "
              f"{'OK' if ok else 'FAIL'}")
        if not ok:
            fails.append("5: regresión chat 32 — rama vieja o sidechain alterados")

    finally:
        shutil.rmtree(tmp, ignore_errors=True)

    print("\n" + "─" * 56)
    if fails:
        print(f"  [FAIL] {len(fails)}/5 chequeo(s):")
        for x in fails:
            print(f"    - {x}")
        return 1
    print("  [OK] smoke por-track chat 40: 5/5 verde.")
    print("  El volumen ahora viaja en audio_library/<track>.json. Gate de oído = Omar.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
