"""test_module_fase2b_hwencode.py — F2 §3.3: encoder conmutable (libx264 por default, NVENC con --hw-encode).
Correr: python -m pytest test_module_fase2b_hwencode.py -q
"""
import sys

import pytest

import fase2b


def test_default_libx264_sin_cambios(monkeypatch):
    monkeypatch.setattr(fase2b, "_HW_ENCODE", False)
    assert fase2b._venc() == ["-c:v", "libx264"]          # sin flag: mismo comando que antes (md5 igual)


def test_hw_encode_usa_nvenc(monkeypatch):
    monkeypatch.setattr(fase2b, "_HW_ENCODE", True)
    v = fase2b._venc()
    assert v[:2] == ["-c:v", "h264_nvenc"] and "-cq" in v and "p5" in v


def test_no_comparte_la_lista(monkeypatch):
    monkeypatch.setattr(fase2b, "_HW_ENCODE", True)
    fase2b._venc().append("x")
    assert fase2b.NVENC_ARGS[-1] == "19"


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
