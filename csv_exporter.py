"""
modules/csv_exporter.py — Dashboard 3.0 (Blindaje de datos · 3 parámetros)

Exporta CSV con UNA fila por topic. El humano solo edita 3 celdas:

  HOOK_SEL    → 1, 2 o 3  (cuál gancho usar)       | N = descartar | vacío = pending
  OUTRO_SEL   → 1, 2 o 3  (cuál cierre usar)       | N = descartar | vacío = pending
  FORMAT_SEL  → SHORT | LONG  (pre-llenado con la sugerencia de IA;
                               se puede sobreescribir manualmente)

Estructura completa:
  topic_id | VEREDICTO | SUGERENCIA_IA | TITULO |
  GANCHOS_3 | CIERRES_3 | COSTO_EST |
  HOOK_SEL | OUTRO_SEL | FORMAT_SEL

Reglas de fila "aprobada":
  - HOOK_SEL ∈ {1,2,3}  AND  OUTRO_SEL ∈ {1,2,3}  → aprobado
  - HOOK_SEL = "N" o OUTRO_SEL = "N"              → descartado (skipped)
  - ambos vacíos                                   → pending
  - uno vacío y otro con valor                     → malformado
  - FORMAT_SEL normalizado a 'short' | 'long' (cualquier otra cosa → usa
    topic["video_type"] guardado en DB)

Blindaje:
  - csv.QUOTE_ALL en escritura → ninguna coma/salto de línea rompe celdas
  - Lectura con DictReader soporta multilinea (las celdas de ganchos van con \\n)
"""

from __future__ import annotations

import csv
import json
from pathlib import Path

from config import DATA_DIR, estimated_cost_for


# ═══════════════════════════════════════════════════════════════
#  CONSTANTES
# ═══════════════════════════════════════════════════════════════

TOPICS_DB_FILE: Path = DATA_DIR / "topics_db.json"
OUTPUT_CSV: Path = DATA_DIR / "fase1_review.csv"

FIELDNAMES: list[str] = [
    "topic_id",
    "VEREDICTO",
    "SUGERENCIA_IA",
    "TITULO",
    "GANCHOS_3",
    "CIERRES_3",
    "COSTO_EST",
    "HOOK_SEL",
    "OUTRO_SEL",
    "FORMAT_SEL",
]

_VALID_INDICES: set[str] = {"1", "2", "3"}
_SKIP_TOKENS: set[str] = {"N", "NO", "SKIP", "X"}
_VALID_FORMATS: set[str] = {"SHORT", "LONG"}


# ═══════════════════════════════════════════════════════════════
#  CARGA DE TOPICS
# ═══════════════════════════════════════════════════════════════

def _load_topics_db() -> dict:
    """Lee topics_db.json o devuelve estructura vacía."""
    if TOPICS_DB_FILE.exists():
        try:
            return json.loads(TOPICS_DB_FILE.read_text(encoding="utf-8"))
        except Exception:
            return {"topics": []}
    return {"topics": []}


# ═══════════════════════════════════════════════════════════════
#  FORMATEO DE CELDAS
# ═══════════════════════════════════════════════════════════════

def _verdict_display(verdict: dict) -> str:
    """Convierte verdict dict a 'emoji nombre'."""
    emoji = verdict.get("emoji", "⚪")
    v = verdict.get("verdict", "desconocido")
    return f"{emoji} {v}"


def _format_numbered(items: list[str]) -> str:
    """
    Formatea lista como '1. ...\\n2. ...\\n3. ...' o '—' si vacía.
    Con QUOTE_ALL los \\n quedan embebidos en la celda sin romper el CSV.
    """
    if not items:
        return "—"
    return "\n".join(f"{i}. {text}" for i, text in enumerate(items, 1))


def _clean_format(suggested_format: str) -> str:
    """
    Extrae solo la palabra SHORT o LONG de suggested_format.
    Entrada típica: "⚡ SUGERIDO SHORT" o "🎬 SUGERIDO LARGO" → "SHORT" / "LONG"
    Fallback: "SHORT".
    """
    if not suggested_format:
        return "SHORT"
    upper = suggested_format.upper()
    if "LARGO" in upper or "LONG" in upper:
        return "LONG"
    return "SHORT"


def _build_row(topic: dict) -> dict:
    """Construye una fila del Dashboard 3.0 para un topic validado."""
    verdict = topic.get("competition_data", {}).get("verdict", {})
    human = topic.get("human_options", {}) or {}
    hooks = human.get("hooks", []) or []
    outros = human.get("outros", []) or []

    video_type = topic.get("video_type", "short")
    try:
        cost = estimated_cost_for(video_type)
        cost_cell = f"${cost:.2f}"
    except Exception:
        cost_cell = "—"

    return {
        "topic_id": topic.get("id", ""),
        "VEREDICTO": _verdict_display(verdict),
        "SUGERENCIA_IA": topic.get("suggested_format", ""),
        "TITULO": topic.get("video_title", ""),
        "GANCHOS_3": _format_numbered(hooks),
        "CIERRES_3": _format_numbered(outros),
        "COSTO_EST": cost_cell,
        # ─── Campos editables por el humano ───
        "HOOK_SEL": "",
        "OUTRO_SEL": "",
        "FORMAT_SEL": _clean_format(topic.get("suggested_format", "")),
    }


# ═══════════════════════════════════════════════════════════════
#  EXPORTADOR
# ═══════════════════════════════════════════════════════════════

def export_fase1_csv(output_path: Path | None = None) -> Path:
    """
    Exporta CSV Dashboard 3.0 de todos los topics con status='validated'.
    UTF-8 con BOM para Excel en Windows. QUOTE_ALL blinda los saltos de línea.
    """
    output_path = output_path or OUTPUT_CSV
    db = _load_topics_db()
    topics = [t for t in db.get("topics", []) if t.get("status") == "validated"]

    rows = [_build_row(t) for t in topics]

    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f, fieldnames=FIELDNAMES, quoting=csv.QUOTE_ALL
        )
        writer.writeheader()
        writer.writerows(rows)

    return output_path


def export_single_topic_csv(
    topic_id: str,
    output_path: Path | None = None,
) -> Path:
    """Chat 35 — Escribe fase1_review.csv con UNA sola fila: la del topic elegido.

    Reusa _build_row (mismo formato/columnas que el Dashboard completo) pero
    pre-llena HOOK_SEL y OUTRO_SEL con "1" para que parse_decisions_csv marque
    la fila como aprobada SIN que el humano edite nada y SIN tocar esa función.
    Los valores son dummy: el motor (fase1_5) ya no consume hook_index /
    outro_index / format_override.

    fase2a lee solo la columna topic_id → sigue funcionando sin cambios.

    Args:
        topic_id: id del topic validado a escribir.
        output_path: destino del CSV (default: OUTPUT_CSV).

    Returns:
        Path del CSV escrito.

    Raises:
        ValueError si topic_id no existe entre los validados de topics_db.json.
    """
    output_path = output_path or OUTPUT_CSV
    db = _load_topics_db()
    topic = next(
        (
            t for t in db.get("topics", [])
            if t.get("id") == topic_id and t.get("status") == "validated"
        ),
        None,
    )
    if topic is None:
        raise ValueError(
            f"export_single_topic_csv: topic_id {topic_id!r} no encontrado "
            f"entre los topics con status='validated' en topics_db.json."
        )

    row = _build_row(topic)
    # Pre-llenado de aprobación. Valores dummy: el motor no los consume, pero
    # parse_decisions_csv necesita HOOK_SEL y OUTRO_SEL en {1,2,3} para marcar
    # la fila como 'approved'. Así el menú aprueba el tema sin intervención.
    row["HOOK_SEL"] = "1"
    row["OUTRO_SEL"] = "1"

    with open(output_path, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(
            f, fieldnames=FIELDNAMES, quoting=csv.QUOTE_ALL
        )
        writer.writeheader()
        writer.writerow(row)

    return output_path


def print_export_summary(output_path: Path | None = None) -> None:
    """Imprime resumen del CSV exportado + instrucciones de edición."""
    output_path = output_path or OUTPUT_CSV
    if not output_path.exists():
        print("  ⚠ No se encontró el CSV.")
        return

    with open(output_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    verdicts = {"🚀": 0, "🟢": 0, "🟡": 0, "💀": 0, "⚪": 0}
    for r in rows:
        v = r.get("VEREDICTO", "")
        for emoji in verdicts:
            if v.startswith(emoji):
                verdicts[emoji] += 1
                break

    print(f"\n{'═' * 60}")
    print(f"  📋 CSV EXPORTADO — Dashboard 3.0")
    print(f"{'═' * 60}")
    print(f"  Total topics validados: {len(rows)}")
    print(f"\n  Veredicto de mercado:")
    print(f"    🚀 Oro:         {verdicts['🚀']}")
    print(f"    🟢 Arbitraje:   {verdicts['🟢']}")
    print(f"    🟡 Caliente:    {verdicts['🟡']}")
    print(f"    💀 Frío:        {verdicts['💀']}")
    print(f"    ⚪ Desconocido: {verdicts['⚪']}")
    print(f"\n  ✏️  EDITÁ 3 COLUMNAS:")
    print(f"     HOOK_SEL    → 1, 2 o 3  (o 'N' para descartar)")
    print(f"     OUTRO_SEL   → 1, 2 o 3  (o 'N' para descartar)")
    print(f"     FORMAT_SEL  → SHORT o LONG  (ya viene pre-llenado)")
    print(f"\n  📁 Archivo: {output_path}")
    print(f"{'═' * 60}\n")


# ═══════════════════════════════════════════════════════════════
#  PARSER PARA LATIDO B (lee el CSV editado por el usuario)
# ═══════════════════════════════════════════════════════════════

def _parse_index(raw: str) -> str | int | None:
    """
    Normaliza HOOK_SEL / OUTRO_SEL.
    Returns:
        int 1-3  → índice válido
        "SKIP"   → usuario marcó N/NO/X
        None     → vacío o inválido
    """
    if not raw:
        return None
    s = raw.strip().upper()
    if not s:
        return None
    if s in _SKIP_TOKENS:
        return "SKIP"
    if s in _VALID_INDICES:
        return int(s)
    return None


def _parse_format(raw: str) -> str | None:
    """
    Normaliza FORMAT_SEL. Tolera 'short', 'SHORT', 'largo', 'LONG', etc.
    Returns: 'short' | 'long' | None (si queda ilegible se usa el del DB).
    """
    if not raw:
        return None
    s = raw.strip().upper()
    if "LARGO" in s or "LONG" in s:
        return "long"
    if "SHORT" in s or "CORTO" in s:
        return "short"
    return None


def parse_decisions_csv(csv_path: Path | None = None) -> dict:
    """
    Lee el CSV editado por el usuario y clasifica cada fila.

    Reglas:
        HOOK_SEL y OUTRO_SEL ambos 1-3   → approved
        cualquiera de los dos = SKIP     → skipped
        ambos vacíos                     → pending
        uno vacío / formato inválido     → malformed
        FORMAT_SEL ilegible              → None (se usa topic.video_type del DB)

    Returns:
        {
          "approved":  {
              topic_id: {
                  "hook_index":      int 1-3,
                  "outro_index":     int 1-3,
                  "format_override": 'short' | 'long' | None,
              }, ...
          },
          "skipped":   [topic_id, ...],
          "pending":   [topic_id, ...],
          "malformed": [(topic_id, raw_hook, raw_outro, raw_format), ...],
        }

    Raises:
        FileNotFoundError si el CSV no existe.
    """
    csv_path = csv_path or OUTPUT_CSV
    if not csv_path.exists():
        raise FileNotFoundError(f"No se encontró el CSV en {csv_path}")

    approved: dict[str, dict] = {}
    skipped: list[str] = []
    pending: list[str] = []
    malformed: list[tuple[str, str, str, str]] = []

    with open(csv_path, "r", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        for row in reader:
            tid = (row.get("topic_id") or "").strip()
            if not tid:
                continue

            raw_hook = (row.get("HOOK_SEL") or "").strip()
            raw_outro = (row.get("OUTRO_SEL") or "").strip()
            raw_format = (row.get("FORMAT_SEL") or "").strip()

            hook = _parse_index(raw_hook)
            outro = _parse_index(raw_outro)

            # Descartado explícito
            if hook == "SKIP" or outro == "SKIP":
                skipped.append(tid)
                continue

            # Ambos vacíos → pendiente
            if hook is None and outro is None:
                pending.append(tid)
                continue

            # Uno válido y el otro inválido/vacío → malformado
            if not (isinstance(hook, int) and isinstance(outro, int)):
                malformed.append((tid, raw_hook, raw_outro, raw_format))
                continue

            approved[tid] = {
                "hook_index": hook,
                "outro_index": outro,
                "format_override": _parse_format(raw_format),
            }

    return {
        "approved": approved,
        "skipped": skipped,
        "pending": pending,
        "malformed": malformed,
    }


# ═══════════════════════════════════════════════════════════════
#  CLI DIRECTO
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    path = export_fase1_csv()
    print_export_summary(path)
