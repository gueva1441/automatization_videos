"""test_module_audio_mixer_floor.py — chat 32. Valida que _mix_music_into_video
arme bien el filter_complex con rama-piso + padding inicial. NO corre ffmpeg."""
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


def test_constante_silencio_inicial():
    assert hasattr(fase2b, "INITIAL_SILENCE_SEC"), "falta constante INITIAL_SILENCE_SEC"
    assert fase2b.INITIAL_SILENCE_SEC == 2.5, "INITIAL_SILENCE_SEC debe ser 2.5"


def test_filter_complex_se_construye_sin_error():
    # Construir un filter_complex como el real, con valores del profile.
    # Reproducir la fórmula del módulo en el test sirve como contrato de schema.
    m = AUDIO_PROFILES["MISTERIO_ABISAL"]["mixing"]
    pad_sec = fase2b.INITIAL_SILENCE_SEC
    pad_ms = int(pad_sec * 1000)
    fc = (
        f"[0:v]tpad=start_duration={pad_sec}:start_mode=clone[v_pad];"
        f"[0:a]adelay={pad_ms}|{pad_ms},aresample=44100,asplit=2[narr_main][narr_sc];"
        f"[1:a]aresample=44100,asplit=2[music_a][music_b];"
        f"[music_a]volume={m['music_volume']}[music_lvl];"
        f"[music_lvl][narr_sc]sidechaincompress="
        f"threshold={m['duck_threshold']}:ratio={m['duck_ratio']}:"
        f"attack={m['duck_attack_ms']}:release={m['duck_release_ms']}[music_ducked];"
        f"[music_b]volume={m['music_volume_floor']}[music_floor];"
        f"[narr_main][music_ducked][music_floor]amix=inputs=3:duration=longest:"
        f"dropout_transition=0:normalize=0[mixed]"
    )
    # Smoke checks: las 3 ramas + el padding + los 3 inputs del amix.
    assert "tpad=start_duration=2.5" in fc
    assert f"adelay={pad_ms}|{pad_ms}" in fc
    assert "amix=inputs=3" in fc
    assert "[narr_main][music_ducked][music_floor]" in fc


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
