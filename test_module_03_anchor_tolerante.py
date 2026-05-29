"""test_module_03_anchor_tolerante.py — #205 chat 32. Valida que el match de
anchors tolere "..." y whitespace, devolviendo offset del TEXTO ORIGINAL."""
from script_engine.m03_visual import (
    _validate_anchor_substring, _normalize_for_anchor_match, VisualValidationError,
)

# Narración con pausas y salto de párrafo, como las del Nyos chat 32.
NARR = ("...21 de agosto de 1986. Una muerte masiva. "
        "apenas unos meses antes de que el Lago Nyos se desatara. \n\n Esta "
        "respuesta sombría ya había resonado...")


def test_match_exacto_sigue_andando():
    # Un anchor literal exacto devuelve su posición real.
    a = "Una muerte masiva."
    pos, _end = _validate_anchor_substring(a, NARR, "t")
    assert NARR[pos:pos + len(a)] == a, "match exacto roto"


def test_anchor_que_recorto_la_pausa():
    # Flash mandó sin el "..." inicial — debe matchear igual.
    pos, _end = _validate_anchor_substring(
        "21 de agosto de 1986.", NARR, "t")
    assert pos >= 0
    # El offset debe apuntar al "21" REAL (después del "..." inicial).
    assert NARR[pos:pos + 2] == "21", f"offset mal re-mapeado: {NARR[pos:pos+5]!r}"


def test_anchor_que_colapso_salto_parrafo():
    # El bug fatal del run real: Flash recortó " \n\n Esta".
    pos, _end = _validate_anchor_substring(
        "apenas unos meses antes de que el Lago Nyos se desatara.", NARR, "t")
    assert pos >= 0
    assert NARR[pos:pos + 6] == "apenas", f"offset mal: {NARR[pos:pos+10]!r}"


def test_offset_original_no_normalizado():
    # El offset devuelto debe ser coordenada del ORIGINAL (con pausas),
    # no del texto colapsado — si no, orden/overlap se rompen.
    a = "apenas unos meses"
    pos, _end = _validate_anchor_substring(a, NARR, "t")
    # En el original, "apenas" está después del primer "..." + texto → pos > 40.
    assert pos > 40, f"offset parece del normalizado, no del original: {pos}"


def test_parafraseo_real_sigue_fallando():
    # La tolerancia NO debe dejar pasar un anchor parafraseado de verdad.
    try:
        _validate_anchor_substring("una tragedia masiva enorme", NARR, "t")
        assert False, "debió fallar: es parafraseo, no porción real"
    except VisualValidationError:
        pass


def test_normalize_elimina_pausas_y_colapsa_ws():
    norm, imap = _normalize_for_anchor_match("a...b  \n c")
    assert norm == "ab c", f"norm inesperada: {norm!r}"
    assert len(imap) == len(norm), "index_map desalineado"


def test_devuelve_tupla_pos_end():
    r = _validate_anchor_substring("Una muerte masiva.", NARR, "t")
    assert isinstance(r, tuple) and len(r) == 2, "debe devolver (pos, end)"
    pos, end = r
    assert NARR[pos:end] == "Una muerte masiva.", f"span mal: {NARR[pos:end]!r}"


def test_end_tolerante_cubre_span_original():
    # Anchor que recortó algo: el end debe cubrir hasta el final REAL del span.
    pos, end = _validate_anchor_substring("21 de agosto de 1986.", NARR, "t")
    assert end > pos
    assert NARR[end - 1] in ".6", f"end no apunta al final real: {NARR[pos:end]!r}"


def test_anchors_adyacentes_no_falso_overlap():
    # Dos anchors consecutivos, el primero termina justo antes del segundo.
    # Simula el caso cap2 img#4 que daba falso overlap.
    a1 = "21 de agosto de 1986."
    a2 = "Una muerte masiva."
    p1, e1 = _validate_anchor_substring(a1, NARR, "t1")
    p2, e2 = _validate_anchor_substring(a2, NARR, "t2")
    assert p2 >= e1, f"falso overlap: a2 empieza en {p2} pero a1 termina en {e1}"


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
