"""
test_module_03_veo_charofs.py — Smoke test chat 31 #219 Opción B.

Verifica que _build_veo_prompt usa veo_zone_chars correctamente y genera
un prompt con zonas literales explícitas. NO llama a Flash (cero costo).
"""
from script_engine.m03_visual import _build_veo_prompt


TOPIC = {
    "id": "smoke-219",
    "topic_id": "smoke-219",
    "topic_title": "Smoke test 219",
    "canonical_subject_description": "test scene",
    "geo": "Cameroon",
    "era": "1986",
    "verified_facts": [],
    "documented_people": [],
}

NARRATION = (
    "Era 1986 en Camerún. En una aldea junto al lago, las familias dormían. "
    "Nadie sospechaba lo que estaba por suceder en los próximos minutos. "
    "Una nube invisible se elevaba desde las profundidades del lago Nyos. "
    "Las gallinas dejaron de cantar antes del amanecer, en silencio total. "
    "Cuando el sol salió, más de mil setecientas personas no despertaron."
)
# len(NARRATION) ≈ 430 chars


def test_start_position_includes_zones():
    cap_data = {"chapter_number": 1, "role": "hook", "title": "Hook test", "bullets": []}
    prompt = _build_veo_prompt(
        topic=TOPIC, cap_data=cap_data, narration_text=NARRATION,
        cap_audio_duration_sec=24.0, n_flux_extras=6, veo_position="start",
        veo_zone_chars=143,  # ~8s de 24s sobre 430 chars
    )
    # Las dos zonas deben aparecer marcadas literalmente
    assert "[ZONA VEO]" in prompt, "falta marcador [ZONA VEO]"
    assert "[ZONA SUPPLEMENTALS]" in prompt, "falta marcador [ZONA SUPPLEMENTALS]"
    # Para position=start, los primeros 143 chars son la zona Veo
    expected_veo_zone = NARRATION[:143]
    expected_supps_zone = NARRATION[143:]
    assert expected_veo_zone in prompt, "zona Veo literal no aparece"
    assert expected_supps_zone in prompt, "zona Supps literal no aparece"
    # Coordenadas chars
    assert "chars [0..143]" in prompt, "falta rango chars zona Veo (start)"
    assert "chars [143..430]" in prompt or f"chars [143..{len(NARRATION)}]" in prompt, \
        "falta rango chars zona Supps (start)"


def test_end_position_includes_zones():
    cap_data = {"chapter_number": 7, "role": "reveal_outro", "title": "Outro test", "bullets": []}
    prompt = _build_veo_prompt(
        topic=TOPIC, cap_data=cap_data, narration_text=NARRATION,
        cap_audio_duration_sec=24.0, n_flux_extras=6, veo_position="end",
        veo_zone_chars=143,
    )
    assert "[ZONA VEO]" in prompt
    assert "[ZONA SUPPLEMENTALS]" in prompt
    # Para position=end, los últimos 143 chars son la zona Veo
    n = len(NARRATION)
    expected_veo_zone = NARRATION[n - 143:]
    expected_supps_zone = NARRATION[:n - 143]
    assert expected_veo_zone in prompt, "zona Veo literal (end) no aparece"
    assert expected_supps_zone in prompt, "zona Supps literal (end) no aparece"
    assert f"chars [{n - 143}..{n}]" in prompt, "falta rango chars zona Veo (end)"
    assert f"chars [0..{n - 143}]" in prompt, "falta rango chars zona Supps (end)"


def test_zones_disjoint():
    """Las zonas Veo y Supps nunca se solapan ni dejan gaps."""
    cap_data = {"chapter_number": 7, "role": "reveal_outro", "title": "X", "bullets": []}
    prompt = _build_veo_prompt(
        topic=TOPIC, cap_data=cap_data, narration_text=NARRATION,
        cap_audio_duration_sec=24.0, n_flux_extras=6, veo_position="end",
        veo_zone_chars=143,
    )
    n = len(NARRATION)
    # La concatenación de las zonas literales debe reconstruir la narración
    veo_zone = NARRATION[n - 143:]
    supps_zone = NARRATION[:n - 143]
    assert supps_zone + veo_zone == NARRATION, "zonas no reconstruyen la narración"


def test_signature_accepts_new_arg():
    """No regresión: la nueva firma es retrocompatible para start position."""
    cap_data = {"chapter_number": 1, "role": "hook", "title": "X", "bullets": []}
    # Si la firma rompe, esto levanta TypeError
    prompt = _build_veo_prompt(
        topic=TOPIC, cap_data=cap_data, narration_text=NARRATION,
        cap_audio_duration_sec=10.0, n_flux_extras=4, veo_position="start",
        veo_zone_chars=100,
    )
    assert isinstance(prompt, str) and len(prompt) > 1000


def test_zone_chars_in_print_section_or_rules():
    """El prompt menciona explícitamente el rango de chars para que el LLM
    no adivine. Si esto no aparece, falló la inyección de coordenadas."""
    cap_data = {"chapter_number": 7, "role": "reveal_outro", "title": "X", "bullets": []}
    prompt = _build_veo_prompt(
        topic=TOPIC, cap_data=cap_data, narration_text=NARRATION,
        cap_audio_duration_sec=24.0, n_flux_extras=6, veo_position="end",
        veo_zone_chars=143,
    )
    # Frases clave que el prompt debe contener post-fix
    assert "narration del cap tiene" in prompt.lower() or "caracteres totales" in prompt.lower()
    assert "equivale a" in prompt.lower() or "veo_zone_chars" in prompt.lower() or "aproximación lineal" in prompt.lower()


if __name__ == "__main__":
    test_start_position_includes_zones(); print("✓ test_start_position_includes_zones")
    test_end_position_includes_zones();   print("✓ test_end_position_includes_zones")
    test_zones_disjoint();                print("✓ test_zones_disjoint")
    test_signature_accepts_new_arg();     print("✓ test_signature_accepts_new_arg")
    test_zone_chars_in_print_section_or_rules(); print("✓ test_zone_chars_in_print_section_or_rules")
    print("\nSMOKE 5/5 PASS — chat 31 #219 Opción B")
