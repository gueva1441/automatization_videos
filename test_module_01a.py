"""
test_module_01a.py — Prueba aislada del módulo 01a (estructurador).

Toma un topic existente del topics_db.json (output del módulo 00) y le
pide al módulo 01a el skeleton de 7 capítulos.

NO toca fase1.py ni el resto del pipeline. Solo valida que el 01a:
  - Recibe un topic en formato post-módulo-00.
  - Llama a Flash y devuelve un dict con 7 caps válidos.
  - Persiste data/scripts/_steps/{topic_id}/01a_skeleton.json.

Uso:
  python test_module_01a.py
"""

import json
import re
from pathlib import Path

from script_engine.m01a_skeleton import generate_skeleton, SkeletonValidationError


TOPICS_DB = Path("data") / "topics_db.json"
STEPS_DIR = Path("data") / "scripts" / "_steps"


# ═══════════════════════════════════════════════════════════════
#  CARGA DE TOPIC
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


def _pick_topic(topics: list[dict]) -> dict | None:
    """Si hay 1 topic, lo devuelve. Si hay varios, deja al usuario elegir."""
    if not topics:
        return None

    # Filtrar solo topics LONG con research deep completo
    eligible = [
        t for t in topics
        if t.get("verified_facts") and t.get("canonical_subject_description")
    ]
    if not eligible:
        return None

    if len(eligible) == 1:
        return eligible[0]

    print("\n  Topics disponibles:")
    for i, t in enumerate(eligible, start=1):
        title = t.get("video_title") or "(sin título)"
        n_facts = len(t.get("verified_facts") or [])
        print(f"    [{i}] {title}  ({n_facts} facts)")

    while True:
        choice = input(f"\n  Elegí topic [1-{len(eligible)}]: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(eligible):
            return eligible[int(choice) - 1]
        print("  Inválido, probá de nuevo.")


# ═══════════════════════════════════════════════════════════════
#  INSPECCIÓN VISUAL DEL OUTPUT
# ═══════════════════════════════════════════════════════════════

NUMBER_TOKEN = re.compile(r"\b(\d{1,4}(?:[.,]\d+)?|\d{3,4}s?|19\d{2}|20\d{2})\b")


def _extract_facts_text(verified_facts: list) -> str:
    """Junta todos los facts en un solo string para chequeo de substring."""
    chunks = []
    for f in verified_facts or []:
        if isinstance(f, dict):
            chunks.append((f.get("fact") or ""))
        elif isinstance(f, str):
            chunks.append(f)
    return " || ".join(chunks).lower()


def _bullet_audit(bullet: str, facts_blob: str) -> str:
    """
    Marca el bullet con un símbolo informativo:
      ✓  = sin números o todos los números aparecen literal en algún fact
      ⚠  = tiene números, al menos uno NO está literal en facts
    """
    nums = NUMBER_TOKEN.findall(bullet)
    if not nums:
        return "✓ "
    bl = bullet.lower()
    missing = [n for n in nums if n.lower() not in facts_blob]
    if missing:
        return "⚠ "
    return "✓ "


def _print_skeleton(skeleton: dict, topic: dict) -> None:
    facts_blob = _extract_facts_text(topic.get("verified_facts") or [])

    chapters = skeleton.get("chapters", [])
    print("\n" + "═" * 60)
    print("  ✅ SKELETON GENERADO")
    print("═" * 60)
    print(f"\n  topic_id : {skeleton.get('topic_id')}")
    print(f"  caps     : {len(chapters)}")

    flagged_total = 0
    for ch in chapters:
        n = ch.get("chapter_number")
        title = ch.get("title")
        role = ch.get("role")
        engine = ch.get("render_engine")
        dur = ch.get("duration_seconds")
        bullets = ch.get("bullets") or []

        print(f"\n  ── Cap {n} [{role} / {engine} / {dur}s] ─────────────────")
        print(f"     Título: {title}")
        print(f"     Bullets ({len(bullets)}):")
        for b in bullets:
            mark = _bullet_audit(b, facts_blob)
            if mark.strip() == "⚠":
                flagged_total += 1
            print(f"       {mark} {b}")

    print("\n" + "─" * 60)
    if flagged_total == 0:
        print(f"  ✅ Auditoría de números: 0 bullets sospechosos.")
    else:
        print(f"  ⚠  Auditoría: {flagged_total} bullet(s) con número que NO")
        print(f"     aparece literal en verified_facts. Revisar manualmente.")
    print("─" * 60)


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    print("\n" + "═" * 60)
    print("  🧪 TEST MÓDULO 01a — estructurador (skeleton 7 caps)")
    print("═" * 60)

    # ─── 1. Cargar topics_db ───
    topics = _load_topics_db()
    if not topics:
        print(f"\n  ❌ No hay topics en {TOPICS_DB}.")
        print("     Corré primero test_module_00.py para generar uno.")
        return

    topic = _pick_topic(topics)
    if not topic:
        print(f"\n  ❌ Ningún topic con research deep completo en {TOPICS_DB}.")
        return

    title = topic.get("video_title")
    n_facts = len(topic.get("verified_facts") or [])
    print(f"\n  Topic seleccionado: {title}")
    print(f"  topic_id          : {topic.get('id')}")
    print(f"  verified_facts    : {n_facts}")
    print(f"  canonical         : {(topic.get('canonical_subject_description') or '')[:80]}...")
    print(f"\n  Estimado: ~$0.005, ~10s (1 llamada Flash)")

    confirm = input("\n  ¿Arrancar? [S/n]: ").strip().lower()
    if confirm in ("n", "no"):
        print("  Abortado.")
        return

    # ─── 2. Correr módulo 01a ───
    try:
        skeleton = generate_skeleton(topic)
    except SkeletonValidationError as e:
        print(f"\n  ❌ Skeleton inválido: {e}")
        return
    except Exception as e:
        print(f"\n  ❌ Error inesperado: {type(e).__name__}: {e}")
        return

    # ─── 3. Imprimir output ───
    _print_skeleton(skeleton, topic)

    # ─── 4. Verificar persistencia ───
    out_file = STEPS_DIR / topic["id"] / "01a_skeleton.json"
    if out_file.exists():
        size_kb = out_file.stat().st_size / 1024
        print(f"\n  📁 Persistido: {out_file} ({size_kb:.1f} KB)")
    else:
        print(f"\n  ⚠  No se encontró {out_file}")

    print("\n" + "═" * 60)
    print("  ✅ Prueba completada con éxito")
    print("═" * 60 + "\n")


if __name__ == "__main__":
    main()
