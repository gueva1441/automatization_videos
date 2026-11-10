"""test_module_audio_mixer_floor.py — chat 32. Valida que _mix_music_into_video
arme bien el filter_complex con rama-piso (F79: sin padding inicial). NO corre ffmpeg."""
import fase2b
from audio_profiles import AUDIO_PROFILES


def test_profile_tiene_music_volume_floor():
    m = AUDIO_PROFILES["MISTERIO_ABISAL"]["mixing"]
    assert "music_volume_floor" in m, "falta music_volume_floor en MISTERIO_ABISAL"
    assert 0.0 < m["music_volume_floor"] < m["music_volume"], "floor debe ser >0 y < music_volume"


def test_otros_profiles_intactos():
    # No deben tener music_volume_floor (default a 0 = backward compat).
    for name in ("SABIDURIA_ESTOICA", "TRUE_CRIME_TERROR"):
        m = AUDIO_PROFILES[name]["mixing"]
        assert "music_volume_floor" not in m, f"{name} no debía tocarse"


def test_filter_complex_se_construye_sin_error():
    """El grafo real de la mezcla (`_grafo_musica`, el mismo de la mezcla clásica y la de audio solo) con los valores del
    profile: las 3 ramas del amix y el piso. F79: sin intro, la narración entra sin `adelay` (y no hay `tpad`)."""
    from pathlib import Path
    m = AUDIO_PROFILES["MISTERIO_ABISAL"]["mixing"]
    fc, _ = fase2b._grafo_musica(Path("v.wav"), Path("m.wav"), m, None)
    assert fc.startswith("[0:a]aresample=44100,asplit=2[narr_main][narr_sc];")
    assert f"[music_b]volume={float(m['music_volume_floor'])}[music_floor]" in fc
    assert "amix=inputs=3" in fc
    assert "[narr_main][music_ducked][music_floor]" in fc
    assert "adelay" not in fc and "tpad" not in fc


if __name__ == "__main__":
    import sys
    fns = [v for k, v in sorted(globals().items())
           if k.startswith("test_") and callable(v)]
    fails = 0
    for fn in fns:
        try:
            fn(); print(f"  OK  {fn.__name__}")
        except AssertionError as e:
            fails += 1; print(f"  XX  {fn.__name__}: {e}")
    print(f"\n{'PASS' if not fails else 'FAIL'} - {len(fns)-fails}/{len(fns)}")
    sys.exit(1 if fails else 0)
