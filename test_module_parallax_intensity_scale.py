"""test_module_parallax_intensity_scale.py — chat 32. Valida que _build_options
escale intensity por duración corta + respete el floor + no toque imágenes largas."""
# parallax_animator_v2 vive en script_engine/ en este layout, no en raíz.
from script_engine.parallax_animator_v2 import _build_options

# FlowSpec mínimo para los tests (mismas keys que usa el código real)
def spec(movement="vertical", intensity=0.9, steady=0.4):
    return {"movement": movement, "intensity": intensity, "steady": steady}


def test_duracion_larga_no_escala():
    # Imagen de 10s con intensity 0.9 → debe quedar en 0.9, sin tocar.
    opts = _build_options(spec(intensity=0.9), duration_seconds=10.0)
    assert opts["intensity"] == 0.9, f"intensity cambió en imagen larga: {opts['intensity']}"


def test_duracion_referencia_no_escala():
    # Exactamente 7s = referencia. No debe escalar (cap inferior).
    opts = _build_options(spec(intensity=0.9), duration_seconds=7.0)
    assert opts["intensity"] == 0.9, f"escaló en duración referencia: {opts['intensity']}"


def test_duracion_corta_escala_lineal():
    # 3.5s = mitad del target → intensity al 50%.
    opts = _build_options(spec(intensity=0.9), duration_seconds=3.5)
    expected = 0.9 * 0.5
    assert abs(opts["intensity"] - expected) < 1e-6, f"escalado mal: {opts['intensity']}, esperado {expected}"


def test_duracion_muy_corta_floor():
    # 1.8s → factor 0.257, pero el floor es 0.45.
    opts = _build_options(spec(intensity=0.9), duration_seconds=1.8)
    expected = 0.9 * 0.45
    assert abs(opts["intensity"] - expected) < 1e-6, f"floor no aplicó: {opts['intensity']}, esperado {expected}"


def test_otros_kwargs_intactos_en_corta():
    # Aunque intensity cambie, isometric/depth/smooth/loop deben quedar EXACTOS.
    opts_h = _build_options(spec(movement="horizontal"), duration_seconds=3.5)
    assert opts_h.get("isometric") == 0.6, "isometric cambió en horizontal corta"
    assert opts_h.get("steady") == 0.4, "steady cambió en horizontal corta"
    assert opts_h.get("smooth") is True
    assert opts_h.get("loop") is True

    opts_o = _build_options(spec(movement="orbital"), duration_seconds=3.5)
    assert opts_o.get("depth") == 0.9, "depth cambió en orbital corta"


def test_caso_real_ch02_img04():
    # El caso que Omar vio en el MP4: ch02_img_04 (cap 2 vertical, i=0.90, 3.58s).
    opts = _build_options(spec(movement="vertical", intensity=0.9, steady=0.0),
                          duration_seconds=3.58)
    # Factor = 3.58/7 = 0.5114 → intensity = 0.9 * 0.5114 = ~0.460
    assert 0.45 < opts["intensity"] < 0.47, f"caso real mal: {opts['intensity']}"


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
