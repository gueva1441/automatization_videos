"""
test_module_00_4e.py — Prueba aislada del SUB-PASO 4e (visual_canon).

Reutiliza los insumos ya generados en disco para Wittenoom + USS Scorpion
(facts del 4a + canonical del 4b + angle_blocks del 00) y corre SOLO el 4e.

Esto evita re-correr todo el módulo 00 (~7 min, ~$0.025) cada vez que se
itera el prompt del 4e. Costo de esta prueba: ~$0.002 total (1 Flash × 2 topics).

Uso:
  python test_module_00_4e.py

Output:
  - Imprime auditoría pretty-printed del canon visual generado.
  - Persiste el resultado en data/scripts/_steps/{topic_id}/05_visual_canon.json
    para que el próximo paso (refactor m03) lo pueda leer.

NO toca topics_db.json ni el resto del pipeline.
"""

import json
import re
import sys
from pathlib import Path

from researcher_steps.step_4e_visual_canon import extract_visual_canon


# ═══════════════════════════════════════════════════════════════
#  TOPICS DE VALIDACIÓN
# ═══════════════════════════════════════════════════════════════

TOPICS = [
    {
        "label": "Wittenoom (asbesto azul, outback Australia)",
        "topic_id": "68ccaee5-aca8-47fb-962f-520b5de1e611",
        "expected_era_keywords": ["1940", "1950", "1960", "1970", "20th century", "mid-century"],
        "expected_blocklist_min_items": 6,
    },
    {
        "label": "USS Scorpion (submarino, 1968)",
        "topic_id": "b9b1adf2-c662-4eac-a71f-18df30dc5227",
        "expected_era_keywords": ["1960", "mid-century", "20th century"],
        "expected_blocklist_min_items": 6,
    },
]

DATA_DIR = Path("data")
STEPS_DIR = DATA_DIR / "scripts" / "_steps"
TOPICS_DB_FILE = DATA_DIR / "topics_db.json"


# ═══════════════════════════════════════════════════════════════
#  TABLA DE MAPEO EDAD → DESCRIPTOR (espejo del prompt del 4e)
# ═══════════════════════════════════════════════════════════════

AGE_RANGES = [
    (20, 23, "early-20s"),
    (24, 26, "mid-20s"),
    (27, 29, "late-20s"),
    (30, 33, "early-30s"),
    (34, 36, "mid-30s"),
    (37, 39, "late-30s"),
    (40, 43, "early-40s"),
    (44, 46, "mid-40s"),
    (47, 49, "late-40s"),
    (50, 53, "early-50s"),
    (54, 56, "mid-50s"),
    (57, 59, "late-50s"),
]


def _expected_age_descriptor(age: int) -> str | None:
    """Devuelve el descriptor esperado según la tabla del prompt."""
    for lo, hi, desc in AGE_RANGES:
        if lo <= age <= hi:
            return desc
    if age >= 60:
        return "elderly"  # también acepta "in his/her 60s"
    return None


# ═══════════════════════════════════════════════════════════════
#  CARGADORES DE INSUMOS DESDE DISCO
# ═══════════════════════════════════════════════════════════════

def _load_step(topic_id: str, step_filename: str) -> dict:
    """Carga un sub-paso intermedio del módulo 00 desde disco."""
    path = STEPS_DIR / topic_id / step_filename
    if not path.exists():
        raise FileNotFoundError(
            f"No existe {path}. ¿Corriste el módulo 00 para este topic?"
        )
    return json.loads(path.read_text(encoding="utf-8"))


def _load_seed_title(topic_id: str) -> str:
    """Saca el seed_title del topic desde topics_db.json."""
    if not TOPICS_DB_FILE.exists():
        return "(topics_db.json no encontrado)"
    db = json.loads(TOPICS_DB_FILE.read_text(encoding="utf-8"))
    for t in db.get("topics", []):
        if t.get("id") == topic_id:
            return t.get("video_title") or t.get("seed_id", "?")
    return "(topic no encontrado en db)"


def _persist_canon(topic_id: str, canon: dict) -> Path:
    """Guarda el output del 4e en _steps/{topic_id}/05_visual_canon.json."""
    out_dir = STEPS_DIR / topic_id
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "05_visual_canon.json"
    payload = {"topic_id": topic_id, **canon}
    out_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return out_path


# ═══════════════════════════════════════════════════════════════
#  AUDITORÍA DEL OUTPUT
# ═══════════════════════════════════════════════════════════════

def _audit(canon: dict, expected: dict, label: str) -> tuple[int, int]:
    """
    Audita el output del 4e contra criterios duros.

    Returns:
        (passed, total) — número de checks pasados sobre el total.
    """
    print(f"\n  ─── Auditoría dura: {label} ───")
    passed = 0
    total = 0

    def check(condition: bool, message: str):
        nonlocal passed, total
        total += 1
        if condition:
            passed += 1
            print(f"    ✓ {message}")
        else:
            print(f"    ✗ {message}")

    # ─── Bloque 1: era_visual_canon ───
    era = canon.get("era_visual_canon", {})
    required_keys = {
        "primary_decade", "spans", "clothing", "technology",
        "vehicles_machinery", "interiors", "forbidden_anachronisms",
    }
    check(set(era.keys()) >= required_keys, f"era_visual_canon tiene las 7 keys")
    check(bool(era.get("primary_decade", "").strip()), "primary_decade no vacío")
    check(bool(era.get("spans", "").strip()), "spans no vacío")
    check(bool(era.get("clothing", "").strip()), "clothing no vacío")
    check(bool(era.get("technology", "").strip()), "technology no vacío")
    check(bool(era.get("vehicles_machinery", "").strip()), "vehicles_machinery no vacío")
    check(bool(era.get("interiors", "").strip()), "interiors no vacío")
    check(bool(era.get("forbidden_anachronisms", "").strip()), "forbidden_anachronisms no vacío")

    # Era detectada coincide con expectativa
    primary = era.get("primary_decade", "").lower()
    spans = era.get("spans", "").lower()
    era_text = f"{primary} {spans}"
    expected_kws = expected["expected_era_keywords"]
    matches = [kw for kw in expected_kws if kw.lower() in era_text]
    check(
        len(matches) >= 1,
        f"era detectada coincide con expectativa "
        f"(primary='{era.get('primary_decade')}', spans='{era.get('spans')}', "
        f"matches={matches})",
    )

    # ─── Bloque 2: documented_people ───
    people = canon.get("documented_people", [])
    check(isinstance(people, list), "documented_people es lista")

    # Para cada persona: appearance_canon no debe contener el name
    for p in people:
        name = p.get("name", "")
        appearance = p.get("appearance_canon", "").lower()
        # Buscar tokens del name (split por espacio) en appearance
        name_tokens = [t for t in name.split() if len(t) > 2]
        leaks = [t for t in name_tokens if t.lower() in appearance]
        check(
            len(leaks) == 0,
            f"persona '{name}' — appearance_canon SIN nombre (leaks: {leaks})",
        )

    # Para cada persona con age_at_event: descriptor coherente
    for p in people:
        age = p.get("age_at_event")
        if age is None:
            continue
        if not isinstance(age, int):
            continue
        expected_desc = _expected_age_descriptor(age)
        if expected_desc is None:
            continue
        appearance = p.get("appearance_canon", "").lower()
        # Acepta "mid-30s" o "in his/her 30s" o equivalentes naturales
        ok = expected_desc.lower() in appearance
        # Para >=60 también aceptamos "60s"
        if age >= 60 and not ok:
            ok = "60s" in appearance or "elderly" in appearance
        check(
            ok,
            f"persona '{p.get('name')}' edad {age} → appearance contiene "
            f"'{expected_desc}' (got: '{p.get('appearance_canon', '')[:80]}...')",
        )

    # ─── Bloque 3: anachronism_blocklist ───
    blocklist = canon.get("anachronism_blocklist", [])
    check(isinstance(blocklist, list), "anachronism_blocklist es lista")
    check(
        len(blocklist) >= expected["expected_blocklist_min_items"],
        f"blocklist tiene ≥{expected['expected_blocklist_min_items']} items "
        f"(got: {len(blocklist)})",
    )

    # Items obligatorios (al menos uno de cada categoría)
    bl_text = " | ".join(b.lower() for b in blocklist)
    check("smartphone" in bl_text or "phone" in bl_text, "blocklist incluye smartphones")
    check(
        "led" in bl_text or "flat panel" in bl_text or "digital display" in bl_text,
        "blocklist incluye LED/flat-panel/digital display",
    )
    check(
        "contemporary" in bl_text or "modern clothing" in bl_text or "2000s" in bl_text or "2020s" in bl_text,
        "blocklist incluye ropa contemporánea",
    )

    return passed, total


# ═══════════════════════════════════════════════════════════════
#  PRETTY-PRINT DEL CANON
# ═══════════════════════════════════════════════════════════════

def _pretty_print_canon(canon: dict, label: str):
    """Imprime el canon visual de forma legible."""
    print(f"\n  ─── Canon visual generado: {label} ───")

    era = canon.get("era_visual_canon", {})
    print(f"\n    [era_visual_canon]")
    print(f"      primary_decade:        {era.get('primary_decade', '')!r}")
    print(f"      spans:                 {era.get('spans', '')!r}")
    for field in ("clothing", "technology", "vehicles_machinery", "interiors", "forbidden_anachronisms"):
        val = era.get(field, "")
        print(f"      {field}:")
        # Wrap a ~70 chars
        line = ""
        for word in val.split():
            if len(line) + len(word) + 1 > 70:
                print(f"        {line}")
                line = word
            else:
                line = f"{line} {word}".strip()
        if line:
            print(f"        {line}")

    people = canon.get("documented_people", [])
    print(f"\n    [documented_people] ({len(people)} personas)")
    for p in people:
        print(f"      • {p.get('name')} ({p.get('role')})")
        print(f"          age_at_event: {p.get('age_at_event')}, era: {p.get('era')}")
        appearance = p.get("appearance_canon", "")
        print(f"          appearance_canon: {appearance[:120]}...")

    blocklist = canon.get("anachronism_blocklist", [])
    print(f"\n    [anachronism_blocklist] ({len(blocklist)} items)")
    for item in blocklist:
        print(f"      - {item}")


# ═══════════════════════════════════════════════════════════════
#  RUNNER PRINCIPAL
# ═══════════════════════════════════════════════════════════════

def _run_topic(topic_cfg: dict) -> tuple[int, int]:
    """Corre el 4e para un topic. Retorna (passed, total) de la auditoría."""
    topic_id = topic_cfg["topic_id"]
    label = topic_cfg["label"]

    print("\n" + "═" * 60)
    print(f"  TOPIC: {label}")
    print(f"  ID:    {topic_id}")
    print("═" * 60)

    # ─── Cargar insumos ───
    try:
        pool = _load_step(topic_id, "00_pool_etiquetado.json")
        facts_step = _load_step(topic_id, "01_facts_sources.json")
        canonical_step = _load_step(topic_id, "02_canonical.json")
    except FileNotFoundError as e:
        print(f"\n  ❌ Insumos faltantes:\n     {e}")
        return (0, 1)

    angle_blocks = pool.get("angle_blocks", {})
    verified_facts = facts_step.get("verified_facts", [])
    canonical = canonical_step.get("canonical_subject_description")
    seed_title = _load_seed_title(topic_id)

    print(f"\n  Insumos cargados:")
    print(f"    - angle_blocks:    {len(angle_blocks)} bloques "
          f"(total {sum(len(b) for b in angle_blocks.values())} chars)")
    print(f"    - verified_facts:  {len(verified_facts)} facts")
    print(f"    - canonical:       {(canonical or '(None)')[:80]}...")
    print(f"    - seed_title:      {seed_title}")

    # ─── Llamar al 4e ───
    print(f"\n  → Llamando a extract_visual_canon (1 Flash)...")
    seed_dict = {"seed_title": seed_title}
    canon = extract_visual_canon(seed_dict, angle_blocks, verified_facts, canonical)

    # ─── Persistir output ───
    out_path = _persist_canon(topic_id, canon)
    print(f"  ✓ Persistido en: {out_path}")

    # ─── Pretty print ───
    _pretty_print_canon(canon, label)

    # ─── Auditoría dura ───
    passed, total = _audit(canon, topic_cfg, label)

    return (passed, total)


def main():
    print("\n" + "═" * 60)
    print("  🧪 TEST MÓDULO 00 — SUB-PASO 4e (visual_canon) AISLADO")
    print("═" * 60)
    print(f"\n  Topics a probar: {len(TOPICS)}")
    for t in TOPICS:
        print(f"    - {t['label']}")
    print(f"\n  Llamadas Flash: {len(TOPICS)} (1 por topic)")
    print(f"  Costo estimado: ~$0.002 total")
    print(f"  Tiempo estimado: ~30s\n")

    confirm = input("  ¿Arrancar? [S/n]: ").strip().lower()
    if confirm in ("n", "no"):
        print("  Abortado.")
        return

    results: list[tuple[str, int, int]] = []
    for topic_cfg in TOPICS:
        try:
            passed, total = _run_topic(topic_cfg)
        except Exception as e:
            print(f"\n  ❌ Excepción en topic {topic_cfg['label']}:\n     {type(e).__name__}: {e}")
            passed, total = 0, 1
        results.append((topic_cfg["label"], passed, total))

    # ─── Reporte final ───
    print("\n" + "═" * 60)
    print("  REPORTE FINAL")
    print("═" * 60)
    total_passed = 0
    total_checks = 0
    for label, passed, total in results:
        marker = "✓" if passed == total else "✗"
        print(f"  {marker} {label}: {passed}/{total} checks pasaron")
        total_passed += passed
        total_checks += total
    print(f"\n  TOTAL: {total_passed}/{total_checks} checks pasaron en {len(TOPICS)} topics")

    if total_passed == total_checks:
        print("\n  ✅ Todos los checks pasaron. Listo para integrar al orquestador.")
    else:
        print("\n  ⚠ Hubo fallas. Revisar el output arriba para iterar el prompt del 4e.")

    print("\n" + "═" * 60 + "\n")


if __name__ == "__main__":
    main()
