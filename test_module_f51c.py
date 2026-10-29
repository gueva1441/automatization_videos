"""F51c — sin el borrado de nombres documentados en `f8_backstop` y el corte de la zona Veo en el final de oración más
cercano (sin oración, en el espacio; empate → zona Veo más corta). Offline: lee la narración y el sync_map reales de
Wittenoom, sin modelos."""
import json
from pathlib import Path

import pytest

from script_engine import m03_imagenes_v3 as v3
from script_engine import m03_visual as m3
from script_engine import name_matching

ROOT = Path(__file__).resolve().parent
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
NARR = ROOT / "data" / "scripts" / "_steps" / TID / "01b_narration.json"
SYNC = ROOT / "output" / "audio" / TID / "sync_map.json"


def test_f51c_f8_backstop_deja_el_apellido_documentado():
    p = "Inside the Perth Supreme Court, 1988. A dim wood-panelled courtroom."
    assert v3.f8_backstop(p, {"shot_scale": "wide"}, False) == (p, [])
    assert not hasattr(name_matching, "scrub_documented_names") and not hasattr(name_matching, "_neutral_descriptor")
    assert hasattr(name_matching, "iter_name_patterns")                      # m05 la sigue usando


def _caps_reales():
    if not (NARR.exists() and SYNC.exists()):
        pytest.skip("sin la narración o el sync_map de Wittenoom")
    nar = {c["chapter_number"]: c["narration"].strip() for c in json.loads(NARR.read_text(encoding="utf-8"))["chapters"]}
    dur = {c["id"]: float(c["duration_sec"]) for c in json.loads(SYNC.read_text(encoding="utf-8"))["chapters"]}
    out = {}
    for n in (1, 7):
        t = nar[n]
        out[n] = (t, max(1, min(int(m3.VEO_CLIP_DURATION_SEC * len(t) / dur[f"ch{n:02d}"]), len(t) - 1)))
    return out


def _sin_cortar_palabra(t, c):
    return not (t[c - 1].isalnum() and t[c].isalnum())


@pytest.mark.parametrize("n, pos, termina", [(1, "start", "paredes de chapa."), (7, "end", "seguridad pública».")])
def test_f51c_corte_veo_real_de_wittenoom(n, pos, termina):
    t, vz = _caps_reales()[n]
    vlo, vhi, slo, shi = m3._carve_veo_zones(t, pos, vz)
    if pos == "start":
        assert (vlo, slo, shi) == (0, vhi, len(t)) and t[:vhi].endswith(termina)
        assert t[slo:].startswith(" En el retrato")
        cut = vhi
    else:
        assert (vhi, slo, shi) == (len(t), 0, vlo) and t[:shi].endswith(termina)
        assert t[vlo:].startswith(" No se ha retirado")
        cut = vlo
    assert cut != (vz if pos == "start" else len(t) - vz)                    # el corte de hoy caía a mitad de palabra
    assert _sin_cortar_palabra(t, cut)


def test_f51c_sin_punto_corta_en_un_espacio():
    t = "una voz larga sin ningun final de oracion en toda la narracion"
    for pos, vz in (("start", 12), ("end", 20)):
        vlo, vhi, slo, shi = m3._carve_veo_zones(t, pos, vz)
        cut = vhi if pos == "start" else vlo
        assert t[cut] == " " and _sin_cortar_palabra(t, cut)


def test_f51c_empate_deja_la_zona_veo_mas_corta():
    t = "Uno dos. Tres cuatros. Cinco seis siete."                           # finales en 8 y 22; largo 40
    assert m3._carve_veo_zones(t, "start", 16)[:2] == (0, 22)               # 16: a 8 de 8 y a 6 de 22 → el más cercano
    assert m3._carve_veo_zones(t, "start", 15)[:2] == (0, 8)                # 15: a 7 de los dos → zona Veo más corta
    # end: el corte de hoy es len − veo_zone_chars; 26 → 14 (a 6 de 8) → 8; 25 → 15, empate → 22 (zona Veo más corta)
    assert m3._carve_veo_zones(t, "end", 26)[:2] == (8, 40)
    assert m3._carve_veo_zones(t, "end", 25)[:2] == (22, 40)
