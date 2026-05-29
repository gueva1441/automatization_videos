"""
test_module_02.py — Prueba aislada del módulo 02 (asignador de profiles).

Toma un topic + su skeleton (output del 01a) + su narración (output del 01b)
y le pide al módulo 02 los art_profiles por cap.

Requiere que 01a y 01b hayan corrido antes (que existan
01a_skeleton.json y 01b_narration.json en _steps/{topic_id}/).

Uso:
  python test_module_02.py
"""

import json
from collections import Counter
from pathlib import Path

from script_engine.m02_profiles import (
    assign_profiles,
    ProfileValidationError,
)
from art_profiles import VALID_PROFILES


TOPICS_DB = Path("data") / "topics_db.json"
STEPS_DIR = Path("data") / "scripts" / "_steps"


# ═══════════════════════════════════════════════════════════════
#  CARGA
# ═══════════════════════════════════════════════════════════════

def _load_topics_db() -> list[dict]:
    if not TOPICS_DB.exists():
        return []
    try:
        data = json.loads(TOPICS_DB.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "topics" in data:
        return data["topics"]
    return []


def _load_skeleton(topic_id: str) -> dict | None:
    """Lee skeleton 01a y filtra _distribution_plan."""
    f = STEPS_DIR / topic_id / "01a_skeleton.json"
    if not f.exists():
        return None
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return {
        "topic_id": data.get("topic_id"),
        "chapters": data.get("chapters", []),
    }


def _load_narration(topic_id: str) -> dict | None:
    """Lee narración 01b."""
    f = STEPS_DIR / topic_id / "01b_narration.json"
    if not f.exists():
        return None
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _pick_topic_with_inputs(topics: list[dict]) -> tuple[dict, dict, dict] | None:
    """Devuelve (topic, skeleton, narration) o None si no hay nada elegible."""
    eligible = []
    for t in topics:
        tid = t.get("id")
        if not tid:
            continue
        skel = _load_skeleton(tid)
        narr = _load_narration(tid)
        if (
            skel and len(skel.get("chapters") or []) == 7
            and narr and len(narr.get("chapters") or []) == 7
        ):
            eligible.append((t, skel, narr))

    if not eligible:
        return None

    if len(eligible) == 1:
        return eligible[0]

    print("\n  Topics con skeleton 01a + narración 01b disponibles:")
    for i, (t, _, _) in enumerate(eligible, start=1):
        title = t.get("video_title") or "(sin título)"
        print(f"    [{i}] {title}")

    while True:
        choice = input(f"\n  Elegí topic [1-{len(eligible)}]: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(eligible):
            return eligible[int(choice) - 1]
        print("  Inválido, probá de nuevo.")


# ═══════════════════════════════════════════════════════════════
#  IMPRESIÓN DEL OUTPUT
# ═══════════════════════════════════════════════════════════════

def _print_assignment(out: dict, skeleton: dict) -> None:
    skel_titles = {ch["chapter_number"]: ch.get("title", "") for ch in skeleton["chapters"]}
    skel_engines = {ch["chapter_number"]: ch.get("render_engine", "") for ch in skeleton["chapters"]}

    print("\n" + "═" * 70)
    print("  ✅ PROFILES ASIGNADOS")
    print("═" * 70)
    print(f"\n  topic_id : {out.get('topic_id')}")

    profiles_used: list[str] = []
    invalid: list[str] = []

    for ch in out.get("chapters", []):
        cn = ch.get("chapter_number")
        prof = ch.get("art_profile", "?")
        rat = ch.get("rationale", "")
        title = skel_titles.get(cn, "")
        engine = skel_engines.get(cn, "")

        is_valid = prof in VALID_PROFILES
        marker = "✓" if is_valid else "✗"
        if not is_valid:
            invalid.append(prof)
        profiles_used.append(prof)

        print(f"\n  ── Cap {cn} ({engine}) ──────────────────────────────")
        print(f"     title      : {title}")
        print(f"     profile    : {marker} {prof}")
        print(f"     rationale  : {rat}")

    # ─── Resumen / auditorías ───
    print("\n" + "─" * 70)
    counter = Counter(profiles_used)
    print(f"  Distribución de profiles ({len(set(profiles_used))} distintos / 7 caps):")
    for prof, n in counter.most_common():
        marker = "✓" if prof in VALID_PROFILES else "✗"
        print(f"    {marker} {prof:25s} ×{n}")

    # Auditoría 1: profiles inválidos
    if invalid:
        print(f"\n  ⚠  Profiles fuera del catálogo: {invalid}")
    else:
        print(f"\n  ✅ Todos los profiles están en el catálogo (de {len(VALID_PROFILES)} válidos).")

    # Auditoría 2: monotonía (≥6 caps con mismo profile = sospechoso)
    if counter:
        most_common_prof, most_common_count = counter.most_common(1)[0]
        if most_common_count >= 6:
            print(
                f"  ⚠  Posible monotonía: '{most_common_prof}' usado en "
                f"{most_common_count}/7 caps. Revisar narración."
            )

    # Auditoría 3: HISTORICAL en topic moderno (chequeo soft de coherencia)
    if "HISTORICAL" in profiles_used:
        print(
            f"  ℹ  HISTORICAL asignado en algún cap. Verificá que el topic "
            f"sea pre-industrial (siglo XIX o anterior)."
        )

    print("─" * 70)


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    print("\n" + "═" * 70)
    print("  🧪 TEST MÓDULO 02 — asignador de profiles")
    print("═" * 70)
    print(f"\n  Catálogo cargado: {len(VALID_PROFILES)} profiles válidos.")

    topics = _load_topics_db()
    if not topics:
        print(f"\n  ❌ No hay topics en {TOPICS_DB}.")
        return

    triplet = _pick_topic_with_inputs(topics)
    if not triplet:
        print(
            f"\n  ❌ Ningún topic tiene 01a_skeleton.json + 01b_narration.json "
            f"en {STEPS_DIR}/{{topic_id}}/."
        )
        print("     Corré primero test_module_01a.py y test_module_01b.py.")
        return

    topic, skeleton, narration = triplet
    title = topic.get("video_title")
    print(f"\n  Topic seleccionado: {title}")
    print(f"  topic_id          : {topic.get('id')}")
    print(f"  Skeleton          : {len(skeleton['chapters'])} caps")
    print(f"  Narración         : {len(narration['chapters'])} caps")
    print(f"\n  Estimado: ~$0.001, ~5-10s (1 llamada Flash)")

    confirm = input("\n  ¿Arrancar? [S/n]: ").strip().lower()
    if confirm in ("n", "no"):
        print("  Abortado.")
        return

    print("\n  Llamando a Flash...")
    try:
        out = assign_profiles(topic, skeleton, narration)
    except ProfileValidationError as e:
        print(f"\n  ❌ Profiles inválidos: {e}")
        return
    except Exception as e:
        print(f"\n  ❌ Error inesperado: {type(e).__name__}: {e}")
        return

    _print_assignment(out, skeleton)

    out_file = STEPS_DIR / topic["id"] / "02_profiles.json"
    if out_file.exists():
        size_kb = out_file.stat().st_size / 1024
        print(f"\n  📁 Persistido: {out_file} ({size_kb:.1f} KB)")
    else:
        print(f"\n  ⚠  No se encontró {out_file}")

    print("\n" + "═" * 70)
    print("  ✅ Prueba completada")
    print("═" * 70 + "\n")


if __name__ == "__main__":
    main()
