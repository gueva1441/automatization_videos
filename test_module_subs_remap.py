"""
test_module_subs_remap.py — tests aislados del remap normalizado→original.

Cubre (§5 handoff): token igual, expansión 1→N (año), nombre fonetizado N→M,
sigla deletreada, texto sin cambios (idéntico al input), + un caso N→M
multi-token que valida el reparto proporcional (starts crecientes, sin solape).

Corre con pytest o directo:  python test_module_subs_remap.py
"""
from __future__ import annotations

from subs_remap import remap_words_to_original


def _w(word: str, start: float, end: float) -> dict:
    return {"word": word, "start": start, "end": end}


def _assert_monotonic_no_overlap(out: list[dict]) -> None:
    """starts estrictamente crecientes; cada start >= end del anterior (sin solape);
    end >= start en todos."""
    for i in range(len(out)):
        assert out[i]["end"] >= out[i]["start"], f"end<start en {out[i]}"
    for i in range(1, len(out)):
        assert out[i]["start"] > out[i - 1]["start"], (
            f"starts no crecientes: {out[i-1]} -> {out[i]}"
        )
        assert out[i]["start"] >= out[i - 1]["end"] - 1e-9, (
            f"solape: {out[i-1]} -> {out[i]}"
        )


def test_token_igual_conserva_timing():
    """Token sin cambio → timing copiado tal cual."""
    norm = [_w("Hola", 0.0, 0.5), _w("mundo", 0.5, 1.0)]
    out = remap_words_to_original("Hola mundo", norm)
    assert [o["word"] for o in out] == ["Hola", "mundo"]
    assert out[0]["start"] == 0.0 and out[0]["end"] == 0.5
    assert out[1]["start"] == 0.5 and out[1]["end"] == 1.0


def test_expansion_1_a_N_anio():
    """'1820' ↔ 'mil ochocientos veinte' (1→3): el token original recibe el
    span combinado [start del primero, end del último]. Incluye un token espacio
    para verificar que se filtra."""
    norm = [
        _w("En", 0.0, 0.2),
        _w(" ", 0.2, 0.2),               # debe filtrarse
        _w("mil", 0.2, 0.5),
        _w("ochocientos", 0.5, 1.0),
        _w("veinte", 1.0, 1.4),
        _w("pasó", 1.4, 1.8),
    ]
    out = remap_words_to_original("En 1820 pasó", norm)
    assert [o["word"] for o in out] == ["En", "1820", "pasó"]
    # token igual antes/después conserva timing
    assert out[0]["start"] == 0.0 and out[0]["end"] == 0.2
    assert out[2]["start"] == 1.4 and out[2]["end"] == 1.8
    # '1820' = span combinado del run normalizado que reemplaza
    assert out[1]["word"] == "1820"
    assert abs(out[1]["start"] - 0.2) < 1e-9   # start de 'mil'
    assert abs(out[1]["end"] - 1.4) < 1e-9     # end de 'veinte'
    _assert_monotonic_no_overlap(out)


def test_nombre_fonetizado_N_a_M_proporcional():
    """'ov de Bílding' (3) ↔ 'of the Building' (3): replace N→M, ventana
    combinada repartida proporcional al largo en chars. starts crecientes, sin
    solape, cubre exactamente la ventana."""
    norm = [
        _w("ov", 2.0, 2.3),
        _w("de", 2.3, 2.6),
        _w("Bílding", 2.6, 3.6),
    ]
    out = remap_words_to_original("of the Building", norm)
    assert [o["word"] for o in out] == ["of", "the", "Building"]
    # cubre exactamente la ventana combinada [2.0, 3.6]
    assert abs(out[0]["start"] - 2.0) < 1e-9
    assert abs(out[-1]["end"] - 3.6) < 1e-9
    # reparto proporcional por chars: of(2) the(3) Building(8) sobre 1.6s
    total = 2 + 3 + 8
    assert abs((out[0]["end"] - out[0]["start"]) - 1.6 * 2 / total) < 1e-6
    assert abs((out[1]["end"] - out[1]["start"]) - 1.6 * 3 / total) < 1e-6
    _assert_monotonic_no_overlap(out)


def test_sigla_deletreada():
    """'FBI' ↔ 'efe be i' (1→3): igual que el año, el token recibe el span
    combinado."""
    norm = [
        _w("El", 0.0, 0.2),
        _w("efe", 0.2, 0.6),
        _w("be", 0.6, 0.9),
        _w("i", 0.9, 1.1),
        _w("llegó", 1.1, 1.5),
    ]
    out = remap_words_to_original("El FBI llegó", norm)
    assert [o["word"] for o in out] == ["El", "FBI", "llegó"]
    assert out[1]["word"] == "FBI"
    assert abs(out[1]["start"] - 0.2) < 1e-9   # start de 'efe'
    assert abs(out[1]["end"] - 1.1) < 1e-9     # end de 'i'
    _assert_monotonic_no_overlap(out)


def test_texto_sin_cambios_identico():
    """Si original == normalizado, la salida es idéntica al input (mismas words y
    timings)."""
    norm = [_w("La", 0.0, 0.3), _w("antigua", 0.3, 0.9), _w("cárcel.", 0.9, 1.5)]
    out = remap_words_to_original("La antigua cárcel.", norm)
    assert out == norm


def test_caso_real_american_college():
    """Caso real cap6: 'American College of the Building Arts' donde el
    normalizado fonetiza 5 tokens y 'Arts'=='Arts' (equal)."""
    norm = [
        _w("Américan", 15.36, 15.7),
        _w("Cólech", 15.7, 16.2),
        _w("ov", 16.2, 16.4),
        _w("de", 16.4, 16.6),
        _w("Bílding", 16.6, 17.5),
        _w("Arts", 17.68, 18.02),
    ]
    out = remap_words_to_original("American College of the Building Arts", norm)
    assert [o["word"] for o in out] == [
        "American", "College", "of", "the", "Building", "Arts",
    ]
    # 'Arts' es bloque equal → timing intacto
    assert out[-1]["start"] == 17.68 and out[-1]["end"] == 18.02
    # el span fonetizado cubre [15.36, 17.5]
    assert abs(out[0]["start"] - 15.36) < 1e-9
    assert abs(out[4]["end"] - 17.5) < 1e-9
    _assert_monotonic_no_overlap(out)


def _run_all():
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_")]
    passed = 0
    for fn in fns:
        fn()
        print(f"  ✓ {fn.__name__}")
        passed += 1
    print(f"\n{passed}/{len(fns)} tests OK")


if __name__ == "__main__":
    _run_all()
