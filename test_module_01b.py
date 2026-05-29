"""
test_module_01b.py — Prueba aislada del módulo 01b (narrador).

Toma un topic + su skeleton (output del 01a) y le pide al módulo 01b la
narración cap-por-cap + humanizer phrases.

Requiere que el 01a haya corrido antes (que exista 01a_skeleton.json
en _steps/{topic_id}/).

Uso:
  python test_module_01b.py
"""

import json
import re
from pathlib import Path

from script_engine.m01b_narrator import (
    generate_narration,
    NarrationValidationError,
)


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
    """Lee el skeleton persistido por el módulo 01a."""
    skel_file = STEPS_DIR / topic_id / "01a_skeleton.json"
    if not skel_file.exists():
        return None
    try:
        data = json.loads(skel_file.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    # Filtrar _distribution_plan si está (el 01b no lo necesita)
    return {
        "topic_id": data.get("topic_id"),
        "chapters": data.get("chapters", []),
    }


def _pick_topic_with_skeleton(topics: list[dict]) -> tuple[dict, dict] | None:
    """Devuelve (topic, skeleton) o None si no hay nada elegible."""
    eligible = []
    for t in topics:
        tid = t.get("id")
        if not tid:
            continue
        skel = _load_skeleton(tid)
        if skel and len(skel.get("chapters") or []) == 7:
            eligible.append((t, skel))

    if not eligible:
        return None

    if len(eligible) == 1:
        return eligible[0]

    print("\n  Topics con skeleton 01a disponible:")
    for i, (t, _) in enumerate(eligible, start=1):
        title = t.get("video_title") or "(sin título)"
        print(f"    [{i}] {title}")

    while True:
        choice = input(f"\n  Elegí topic [1-{len(eligible)}]: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(eligible):
            return eligible[int(choice) - 1]
        print("  Inválido, probá de nuevo.")


# ═══════════════════════════════════════════════════════════════
#  AUDITORÍAS VISUALES
# ═══════════════════════════════════════════════════════════════

NUMBER_TOKEN = re.compile(r"\b(\d{1,4}(?:[.,]\d+)?|\d{3,4}s?|19\d{2}|20\d{2})\b")
SENTENCE_END = re.compile(r"[.!?]+")


def _first_sentence(text: str) -> str:
    text = text.strip()
    m = SENTENCE_END.search(text)
    if not m:
        return text
    return text[: m.end()].strip()


def _last_sentence(text: str) -> str:
    text = text.strip().rstrip(".!?")
    parts = SENTENCE_END.split(text)
    last = (parts[-1] if parts else text).strip()
    return last


def _word_count(text: str) -> int:
    return len([w for w in text.split() if w.strip()])


def _facts_blob(verified_facts: list) -> str:
    chunks = []
    for f in verified_facts or []:
        if isinstance(f, dict):
            chunks.append(f.get("fact") or "")
        elif isinstance(f, str):
            chunks.append(f)
    return " || ".join(chunks).lower()


def _audit_numbers(text: str, facts_blob: str) -> tuple[int, list[str]]:
    """Devuelve (cantidad de números, lista de números faltantes en facts)."""
    nums = NUMBER_TOKEN.findall(text)
    if not nums:
        return 0, []
    missing = [n for n in nums if n.lower() not in facts_blob]
    return len(nums), missing


# ═══════════════════════════════════════════════════════════════
#  IMPRESIÓN DEL OUTPUT
# ═══════════════════════════════════════════════════════════════

def _print_narration(out: dict, topic: dict) -> None:
    facts_blob = _facts_blob(topic.get("verified_facts") or [])

    print("\n" + "═" * 60)
    print("  ✅ NARRACIÓN GENERADA")
    print("═" * 60)
    print(f"\n  topic_id : {out.get('topic_id')}")

    total_chars = 0
    total_flagged = 0

    for ch in out.get("chapters", []):
        cn = ch.get("chapter_number")
        narr = ch.get("narration", "")
        n = len(narr)
        total_chars += n

        first = _first_sentence(narr)
        last = _last_sentence(narr)
        first_wc = _word_count(first)

        n_nums, missing = _audit_numbers(narr, facts_blob)
        if missing:
            total_flagged += len(missing)

        print(f"\n  ── Cap {cn} ─────────────────────────────────")
        print(f"     Largo: {n} chars  |  primera oración: {first_wc} palabras")
        print(f"     ▸ APERTURA: {first[:120]}")
        print(f"     ▸ CIERRE  : ...{last[-120:] if len(last) > 120 else last}")
        if n_nums == 0:
            print(f"     ▸ Números: 0 (cap sin cifras)")
        elif missing:
            print(f"     ▸ ⚠ Números: {n_nums} totales, {len(missing)} NO en facts: {missing}")
        else:
            print(f"     ▸ ✓ Números: {n_nums} totales, todos en facts")

    print(f"\n  ── HUMANIZER PHRASES ──────────────────────")
    for i, p in enumerate(out.get("humanizer_phrases", []), start=1):
        labels = ["SHOCK", "EMPATÍA", "NO OLVIDAR"]
        label = labels[i - 1] if i <= 3 else f"#{i}"
        print(f"     [{label:11}] ({len(p):2} chars) \"{p}\"")

    print("\n" + "─" * 60)
    print(f"  Largo total narración: {total_chars} chars  (~{total_chars // 5} palabras)")
    if total_flagged == 0:
        print(f"  ✅ Auditoría de números: 0 sospechosos.")
    else:
        print(f"  ⚠  Auditoría: {total_flagged} número(s) que NO aparecen en facts.")
        print(f"     Pueden venir del research_summary (toleable) o ser inventos (revisar).")
    print("─" * 60)


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    print("\n" + "═" * 60)
    print("  🧪 TEST MÓDULO 01b — narrador")
    print("═" * 60)

    topics = _load_topics_db()
    if not topics:
        print(f"\n  ❌ No hay topics en {TOPICS_DB}.")
        return

    pair = _pick_topic_with_skeleton(topics)
    if not pair:
        print(f"\n  ❌ Ningún topic tiene skeleton 01a en {STEPS_DIR}/{{topic_id}}/01a_skeleton.json.")
        print("     Corré primero test_module_01a.py para generarlo.")
        return

    topic, skeleton = pair
    title = topic.get("video_title")
    print(f"\n  Topic seleccionado: {title}")
    print(f"  topic_id          : {topic.get('id')}")
    print(f"  Skeleton          : {len(skeleton['chapters'])} caps cargados")
    print(f"\n  Estimado: ~$0.005, ~30-40s (8 llamadas Flash secuenciales)")

    confirm = input("\n  ¿Arrancar? [S/n]: ").strip().lower()
    if confirm in ("n", "no"):
        print("  Abortado.")
        return

    print()
    try:
        out = generate_narration(topic, skeleton)
    except NarrationValidationError as e:
        print(f"\n  ❌ Narración inválida: {e}")
        return
    except Exception as e:
        print(f"\n  ❌ Error inesperado: {type(e).__name__}: {e}")
        return

    _print_narration(out, topic)

    out_file = STEPS_DIR / topic["id"] / "01b_narration.json"
    if out_file.exists():
        size_kb = out_file.stat().st_size / 1024
        print(f"\n  📁 Persistido: {out_file} ({size_kb:.1f} KB)")
    else:
        print(f"\n  ⚠  No se encontró {out_file}")

    print("\n" + "═" * 60)
    print("  ✅ Prueba completada")
    print("═" * 60 + "\n")


if __name__ == "__main__":
    main()
