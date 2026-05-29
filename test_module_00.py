"""
test_module_00.py — Prueba aislada del módulo 00 (topic_researcher rediseñado).

Crea 1 seed manual y corre el flujo deep completo:
  3 angle queries Pro → sub-paso 4a → 4b → 4c → 4d
  → topic consolidado guardado en topics_db.json

Uso:
  python test_module_00.py

NO toca fase1.py ni nada del pipeline viejo. Solo prueba el research.
"""

import json
import uuid
from pathlib import Path

from topic_researcher import research_topics


def main():
    # ─── 1. Seed manual de prueba ───
    seed = {
        "seed_id": str(uuid.uuid4()),
        "seed_title": "Lake Nyos Camerun erupcion limnica 1986 desastre gas CO2 muertes",
        "discovery_mode": "manual",
        "root_niche": "desastres",
        "tags": ["desastre natural", "africa", "camerun", "ciencia", "muerte masiva", "gas toxico"],
        "evidence": {
            "user_input": True,
            "test_run": True,
        },
    }
    print("\n" + "═" * 60)
    print("  🧪 TEST MÓDULO 00 — research deep")
    print("═" * 60)
    print(f"\n  Seed de prueba: {seed['seed_title']}")
    print(f"  Modo: long (3 angle queries Pro + 4 sub-pasos Flash)")
    print(f"  Estimado: ~7-8 minutos, ~$0.025\n")

    confirm = input("  ¿Arrancar? [S/n]: ").strip().lower()
    if confirm in ("n", "no"):
        print("  Abortado.")
        return

    # ─── 2. Correr research_topics directo ───
    topics = research_topics(seeds=[seed], video_type="long")

    if not topics:
        print("\n  ❌ No se generó ningún topic. Revisar logs.")
        return

    topic = topics[0]

    # ─── 3. Imprimir resultado resumido ───
    print("\n" + "═" * 60)
    print("  ✅ RESULTADO")
    print("═" * 60)
    print(f"\n  Topic ID:    {topic.get('id')}")
    print(f"  Título:      {topic.get('video_title')}")
    print(f"  Search KW:   {topic.get('search_keyword')}")
    print(f"  Hook:        {topic.get('hook')}")
    print(f"  Mystery:     {topic.get('mystery')}")
    print(f"  Reveal:      {topic.get('reveal')}")
    print(f"  Virality:    {topic.get('virality_score')}")
    print(f"  Canonical:   {(topic.get('canonical_subject_description') or '')[:100]}...")
    print(f"\n  Verified facts ({len(topic.get('verified_facts', []))}):")
    for i, f in enumerate(topic.get("verified_facts", [])[:5], 1):
        if isinstance(f, dict):
            print(f"    {i}. [{f.get('source_block')}] {f.get('fact')[:80]}")
        else:
            print(f"    {i}. {str(f)[:80]}")
    if len(topic.get("verified_facts", [])) > 5:
        print(f"    ... y {len(topic.get('verified_facts', [])) - 5} más")

    print(f"\n  Sources ({len(topic.get('sources', []))}):")
    for i, s in enumerate(topic.get("sources", [])[:3], 1):
        print(f"    {i}. {str(s)[:80]}")

    rs = topic.get("research_summary") or ""
    print(f"\n  Research summary: {len(rs)} chars")
    print(f"    Preview: {rs[:200]}...")

    # ─── 4. Verificar persistencia intermedia ───
    steps_dir = Path("data") / "scripts" / "_steps" / topic["id"]
    if steps_dir.exists():
        files = list(steps_dir.glob("*.json"))
        print(f"\n  📁 Archivos intermedios en {steps_dir}:")
        for f in sorted(files):
            print(f"    - {f.name} ({f.stat().st_size} bytes)")

    print("\n" + "═" * 60)
    print("  ✅ Prueba completada con éxito")
    print("═" * 60 + "\n")


if __name__ == "__main__":
    main()
