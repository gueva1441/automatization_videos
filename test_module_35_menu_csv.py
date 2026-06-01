"""
test_module_35_menu_csv.py — GATE chat 35.

Valida, sin gastar APIs:
  1. export_single_topic_csv escribe UNA fila y parse_decisions_csv la marca
     'approved' con hook_index=1, outro_index=1 (el truco dummy funciona).
  2. export_single_topic_csv levanta ValueError si el topic no está validado.
  3. _select_topic_interactive: input válido → id correcto; "Q" → None;
     sin validados → None.
  4. Smoke de imports (csv_exporter, fase1_5, fase1) — caza import circular/syntax.

Uso:
  python test_module_35_menu_csv.py
"""
import json
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

import csv_exporter
import fase1_5


def _fake_db(topic_id: str = "tid-test-001") -> dict:
    return {
        "topics": [
            {
                "id": topic_id,
                "status": "validated",
                "video_title": "El misterio de prueba",
                "video_type": "long",
                "market_verdict": "arbitraje",
                "suggested_format": "🎬 SUGERIDO LARGO",
                "human_options": {
                    "hooks": ["gancho A", "gancho B", "gancho C"],
                    "outros": ["cierre A", "cierre B", "cierre C"],
                },
                "competition_data": {
                    "verdict": {"emoji": "🟢", "verdict": "arbitraje"},
                },
            }
        ]
    }


def test_1_single_csv_is_approved() -> None:
    tid = "tid-test-001"
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "fase1_review.csv"
        with patch.object(csv_exporter, "_load_topics_db", return_value=_fake_db(tid)):
            csv_exporter.export_single_topic_csv(tid, out)
        assert out.exists(), "no se escribió el CSV"
        parsed = csv_exporter.parse_decisions_csv(out)
        approved = parsed["approved"]
        assert tid in approved, f"{tid} no quedó approved: {parsed}"
        assert approved[tid]["hook_index"] == 1, "hook_index dummy != 1"
        assert approved[tid]["outro_index"] == 1, "outro_index dummy != 1"
        # Una sola fila. OJO: se cuenta por REGISTROS csv (csv.reader), NO por
        # líneas físicas: las columnas QUOTE_ALL (GANCHOS_3/CIERRES_3) llevan
        # saltos de línea embebidos, así que 1 registro ocupa varias líneas.
        import csv as _csv
        with open(out, encoding="utf-8-sig", newline="") as _f:
            records = list(_csv.reader(_f))
        assert len(records) == 2, f"esperaba header + 1 registro, hay {len(records)}"
    print("  ✓ test_1 export_single_topic_csv → approved con dummies OK")


def test_2_unknown_topic_raises() -> None:
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "x.csv"
        with patch.object(csv_exporter, "_load_topics_db", return_value=_fake_db("otro-id")):
            try:
                csv_exporter.export_single_topic_csv("no-existe", out)
            except ValueError:
                print("  ✓ test_2 ValueError en topic inexistente OK")
                return
    raise AssertionError("no levantó ValueError con topic inexistente")


def test_3_menu_selection() -> None:
    tid = "tid-test-001"
    with tempfile.TemporaryDirectory() as d:
        db_path = Path(d) / "topics_db.json"
        db_path.write_text(json.dumps(_fake_db(tid)), encoding="utf-8")
        original = fase1_5.TOPICS_DB
        try:
            fase1_5.TOPICS_DB = db_path
            with patch("builtins.input", return_value="1"):
                assert fase1_5._select_topic_interactive() == tid, "input '1' no devolvió el id"
            with patch("builtins.input", return_value="Q"):
                assert fase1_5._select_topic_interactive() is None, "'Q' no devolvió None"
            # Sin validados
            db_path.write_text(json.dumps({"topics": []}), encoding="utf-8")
            assert fase1_5._select_topic_interactive() is None, "sin validados no devolvió None"
        finally:
            fase1_5.TOPICS_DB = original
    print("  ✓ test_3 _select_topic_interactive (válido/Q/vacío) OK")


def test_4_imports_smoke() -> None:
    import importlib
    for name in ("csv_exporter", "fase1_5", "fase1"):
        importlib.import_module(name)
    print("  ✓ test_4 imports (csv_exporter, fase1_5, fase1) OK")


def main() -> int:
    tests = [
        test_1_single_csv_is_approved,
        test_2_unknown_topic_raises,
        test_3_menu_selection,
        test_4_imports_smoke,
    ]
    passed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except Exception as e:
            print(f"  ✗ {t.__name__} FALLÓ: {type(e).__name__}: {e}")
    print(f"\n  RESULTADO: {passed}/{len(tests)} PASS")
    return 0 if passed == len(tests) else 1


if __name__ == "__main__":
    sys.exit(main())
