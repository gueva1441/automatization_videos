"""
fase1.py — Orquestador de Fase 1 · Arquitectura de Dos Latidos (Tanda 3)

LATIDO A (default): Investigación → Dashboard 2.0 (CSV)
  PASO 0. Auditoría de promesas pendientes (channel_memory)
  PASO 1. niche_discoverer    → selected_seeds.json
  PASO 2. topic_researcher    → topics_db.json
  PASO 3. topic_validator     → valida + human_options 3x3 + suggested_format
  PASO 4. csv_exporter        → Dashboard 2.0 (CSV editable por humano)

LATIDO B (--process-csv): DEPRECADO en fase1.py
  La generación de guiones se movió a fase1_5.py (m01a → m05 → m06).
  Si el usuario corre `python fase1.py --process-csv`, fase1 imprime
  un mensaje claro y redirige a fase1_5.py.

Uso:
  python fase1.py                           Latido A interactivo
  python fase1.py --video-type short        Latido A sin prompt
  python fase1.py --video-type long         Latido A sin prompt
  python fase1.py --skip-niche              Latido A reutilizando seeds
  python fase1.py --skip-research           Latido A reutilizando topics
  python fase1.py --skip-validate           Latido A reutilizando validados
  python fase1.py --export-only             solo regenerar el CSV
  python fase1.py --process-csv             (deprecado) imprime redirect a fase1_5.py

NOTAS:
- Ya no se usa config.set_video_type ni el global VIDEO_TYPE.
- El video_type se pasa como parámetro a validate_topics() y queda
  persistido en cada topic["video_type"] para uso downstream.
- channel_memory y topics_db del layout viejo no existen en el repo
  actual: se reemplazaron por stubs locales en este archivo.
"""

import argparse
import json
from datetime import datetime
from pathlib import Path

from config import DATA_DIR
from cost_tracker import cost_tracker
from csv_exporter import (
    OUTPUT_CSV,
    export_fase1_csv,
    parse_decisions_csv,
    print_export_summary,
)
from niche_discoverer import discover_niches
from topic_researcher import research_topics
from topic_validator import validate_topics


# ─────────────────────────────────────────────────────────────
#  STUB: channel_memory (módulo viejo no migrado)
# ─────────────────────────────────────────────────────────────
def check_pending_promises() -> None:
    """Stub temporal. El módulo channel_memory del layout viejo no se
    migró todavía. Esto deja el flujo correr sin auditoría de promesas.
    TODO: migrar channel_memory si la feature se quiere recuperar.
    """
    return None


# ─────────────────────────────────────────────────────────────
#  REEMPLAZO: load_db (antes from modules.topics_db)
# ─────────────────────────────────────────────────────────────
def load_db() -> dict:
    """Carga directa de data/topics_db.json. Mismo patrón que fase1_5.py."""
    import json
    db_path = DATA_DIR / "topics_db.json"
    if not db_path.exists():
        return {"topics": []}
    return json.loads(db_path.read_text(encoding="utf-8"))


SEEDS_FILE: Path = DATA_DIR / "selected_seeds.json"
SCRIPTS_DIR: Path = DATA_DIR / "scripts"


# ═══════════════════════════════════════════════════════════════
#  HELPERS COMUNES
# ═══════════════════════════════════════════════════════════════

def _load_seeds() -> list[dict]:
    """Carga seeds desde selected_seeds.json."""
    if not SEEDS_FILE.exists():
        return []
    try:
        data = json.loads(SEEDS_FILE.read_text(encoding="utf-8"))
        return data.get("seeds", [])
    except Exception:
        return []


def _save_seeds_with_judge(seeds: list[dict]) -> None:
    """Persiste los seeds (con su seed["judge"]) en selected_seeds.json.

    Mismo esquema que niche_discoverer._save_seeds ({"selected_at", "seeds":[...]})
    para que el judge sobreviva al grounding y lo pueda leer el menú.
    """
    data = {
        "selected_at": datetime.now().isoformat(),
        "seeds": seeds,
    }
    SEEDS_FILE.write_text(
        json.dumps(data, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _print_judge_summary(seeds: list[dict]) -> None:
    """Tabla del juez (solo seeds spy_arbitrage con judge). Display-only."""
    judged = [s for s in seeds if s.get("judge")]
    if not judged:
        return
    print(f"\n  🤖 Veredicto del juez (pre-grounding):")
    print(f"     {'VEREDICTO':<11} {'COHORTE':<8} {'RIESGO':<14} TEMA")
    for s in judged:
        j = s["judge"]
        print(f"     {j.get('verdict','?'):<11} {j.get('cohort','?'):<8} "
              f"{j.get('risk','?'):<14} {s.get('seed_title','?')}")


# ═══════════════════════════════════════════════════════════════
#  MENÚ RICO SOBRE SEEDS (chat 51 — selección ANTES del research caro)
# ═══════════════════════════════════════════════════════════════

# Orden del menú: oro arriba, luego dudoso, luego descartar (los descartar 3/3
# ya se auto-excluyeron antes; un descartar 2/3 podría seguir acá).
_VERDICT_ORDER = {"oro": 0, "dudoso": 1, "descartar": 2}


def _fmt_views(v) -> str:
    """3.2M / 850K / 191 / '—'. Redondeo para lectura, el dato crudo se conserva en el seed."""
    try:
        v = int(v or 0)
    except (TypeError, ValueError):
        return "—"
    if v <= 0:
        return "—"
    if v >= 1_000_000:
        return f"{v / 1_000_000:.1f}M"
    if v >= 1_000:
        return f"{v / 1_000:.0f}K"
    return str(v)


def _fmt_ratio(r) -> str:
    """'14×' / '3.2×' / '—' (None o 0.0 → '—', edge fan-out sin channel_id)."""
    if not r:
        return "—"
    return f"{r:.0f}×" if r >= 10 else f"{r:.1f}×"


def _fmt_age(m) -> str:
    """'hace 4 meses' / 'desconocida' (None → desconocida, no asumir viejo)."""
    if not isinstance(m, int):
        return "desconocida"
    if m <= 0:
        return "este mes"
    return "hace 1 mes" if m == 1 else f"hace {m} meses"


def _seed_sort_key(s: dict) -> tuple:
    j = s.get("judge") or {}
    en = (s.get("evidence") or {}).get("en_viral") or {}
    rank = _VERDICT_ORDER.get(j.get("verdict"), 3)
    views = int(en.get("views") or 0)
    ratio = en.get("outlier_ratio") or 0.0
    return (rank, -views, -ratio)


def _select_seed_interactive(seeds: list[dict]) -> list[dict] | None:
    """Menú RICO sobre SEEDS (pre-research, $0). Muestra evidencia del juez +
    en_viral + es_gap y deja elegir uno (o varios, coma-separados). Devuelve los
    seeds elegidos, o None si se cancela (Q) o no hay seeds que mostrar.

    NO consume APIs — solo lee la lista de seeds en memoria (ya con seed["judge"]
    y evidence puestos por PASO 1 / 1.5). Tolerante a None en los campos ricos
    (edge fan-out cuyo video top no tenía channel_id → median/ratio/edad faltantes).
    """
    if not seeds:
        print(f"\n  ⚠ No hay seeds para elegir (¿todos descartados por el juez?).")
        return None

    ordered = sorted(seeds, key=_seed_sort_key)

    print(f"\n{'═' * 60}")
    print(f"  🎬 SELECCIÓN DE TEMA (antes del research) — {len(ordered)} seed(s)")
    print(f"{'═' * 60}")
    print(f"  Elegí ANTES de gastar en research. Solo se investiga lo que elijas.\n")
    for i, s in enumerate(ordered, start=1):
        j = s.get("judge") or {}
        ev = s.get("evidence") or {}
        en = ev.get("en_viral") or {}
        es = ev.get("es_gap") or {}

        title = s.get("seed_title") or "(sin título)"
        tag = f"[{j.get('verdict', '—')} {j.get('cohort', '—')}]" if j else "[sin juez]"
        # CHAT 51: marcar demanda medida con nombre pelado (over-narrow fallback) — puede ser
        # off-angle (Lemieux→hockey, Sri Lanka→street food). Informativo, NO auto-excluye.
        fallback = bool(en.get("query_fallback")) or bool(es.get("query_fallback"))
        warn = "  ⚠ fallback" if fallback else ""
        print(f"  [{i}] {title:<48} {tag}{warn}")
        if fallback:
            print(f"      ⚠ demanda medida con nombre pelado — puede ser off-angle "
                  f"(verificá el viral EN)")

        en_title = en.get("original_title") or "—"
        en_title = (en_title[:48] + "…") if len(en_title) > 49 else en_title
        print(f"      viral EN: \"{en_title}\" · {_fmt_views(en.get('views'))} vistas "
              f"· ratio {_fmt_ratio(en.get('outlier_ratio'))} · {_fmt_age(en.get('en_age_months'))}")

        label = es.get("label") or "—"
        ontopic = es.get("ontopic_count")
        ontopic_str = f"{ontopic} competidores" if isinstance(ontopic, int) else "—"
        print(f"      hueco ES: {label} · {ontopic_str}")

        if j:
            reason = (j.get("reason") or "").strip()
            reason = (reason[:70] + "…") if len(reason) > 71 else reason
            print(f"      juez: riesgo={j.get('risk') or 'ninguno'} · {reason}")

    while True:
        choice = input(f"\n  Elegí tema [1-{len(ordered)}] "
                       f"(coma para varios · Q para salir): ").strip()
        if choice.upper() == "Q":
            print(f"\n  Cancelado por el usuario — no se investiga nada.")
            return None
        parts = [p.strip() for p in choice.split(",") if p.strip()]
        if parts and all(p.isdigit() and 1 <= int(p) <= len(ordered) for p in parts):
            idxs = sorted({int(p) for p in parts})
            return [ordered[i - 1] for i in idxs]
        print(f"  Inválido. Ingresá número(s) entre 1 y {len(ordered)} (ej. 3 o 1,4), o Q.")


def _save_script(script: dict) -> None:
    """Persiste un script como JSON individual en data/scripts/."""
    SCRIPTS_DIR.mkdir(parents=True, exist_ok=True)
    topic_id = script.get("topic_id", "unknown")
    filepath = SCRIPTS_DIR / f"{topic_id}.json"
    filepath.write_text(
        json.dumps(script, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )


def _ask_video_type() -> str:
    """Prompt interactivo para elegir video_type de la corrida (Latido A)."""
    print(f"\n{'═' * 60}")
    print(f"  📺 TIPO DE VIDEO para esta corrida")
    print(f"{'═' * 60}")
    print(f"     [S] SHORT  — 45-60s, vertical, pipeline rápido")
    print(f"     [L] LONG   — 8-10 min, documental (híbrido Veo + Leonardo)")
    choice = input(f"\n  👉 [S/L] (default S): ").strip().upper()
    return "long" if choice == "L" else "short"


def _audit_pending_promises() -> None:
    """
    PASO 0 de ambos latidos — auditoría de deudas con el público.
    Muestra (no bloquea) las promesas narrativas pendientes.
    """
    try:
        pending = check_pending_promises()
    except Exception as e:
        print(f"\n  ⚠ No se pudo leer channel_memory: {e}")
        return

    if not pending:
        return

    print(f"\n{'─' * 60}")
    print(f"  🕰  AUDITORÍA DE PROMESAS PENDIENTES ({len(pending)})")
    print(f"{'─' * 60}")
    print(f"  Deudas con el público (aún sin cumplir ni expirar):\n")
    for p in pending[:10]:
        pid = p.get("id", "?")
        target = p.get("target", "?")
        text = (p.get("text", "") or "")[:70]
        print(f"    • {pid}  →  {target}")
        print(f"       «{text}…»")
    if len(pending) > 10:
        print(f"\n    ... y {len(pending) - 10} más")
    print(f"{'─' * 60}")


def _close_cost_tracking() -> None:
    """Cierra el tracking de costos y guarda el reporte de sesión."""
    if cost_tracker.current_video is not None:
        cost_tracker.end_video()
    if cost_tracker.session_videos:
        cost_tracker.print_session_report()
        try:
            report_path = cost_tracker.save_session_report()
            print(f"  📁 Reporte de costos: {report_path.name}\n")
        except Exception as e:
            print(f"  ⚠ No se pudo guardar el reporte: {e}\n")


# ═══════════════════════════════════════════════════════════════
#  LATIDO A — Investigación → Dashboard 2.0
# ═══════════════════════════════════════════════════════════════

def run_latido_a(
    video_type: str | None = None,
    skip_niche: bool = False,
    skip_research: bool = False,
    skip_validate: bool = False,
    export_only: bool = False,
) -> None:
    """Latido A: de cero (o desde un checkpoint) hasta el CSV Dashboard 2.0."""
    print(f"\n{'═' * 60}")
    print(f"  🎬 FASE 1 · LATIDO A — Investigación")
    print(f"{'═' * 60}")

    _audit_pending_promises()

    # Shortcut: solo regenerar CSV
    if export_only:
        print(f"\n  📋 Modo: solo exportar CSV\n")
        csv_path = export_fase1_csv()
        print_export_summary(csv_path)
        return

    if not video_type:
        video_type = _ask_video_type()
    print(f"\n  ✓ video_type de esta corrida: {video_type.upper()}")

    try:
        # ═════ PASO 1 — Niche Discoverer ═════
        if not skip_niche and not skip_research and not skip_validate:
            existing = _load_seeds()
            if existing:
                print(f"\n  📂 Tenés {len(existing)} seed(s) previos:")
                for s in existing[:5]:
                    mode = s.get("discovery_mode", "?")
                    title = s.get("seed_title", "?")
                    print(f"     → [{mode}] {title}")
                if len(existing) > 5:
                    print(f"     ... y {len(existing) - 5} más")
                reuse = input("\n  ¿Usar estos seeds? [S/n]: ").strip().lower()
                if reuse in ("n", "no"):
                    print(f"\n{'─' * 60}")
                    print(f"  📌 PASO 1/4 — Dashboard de Inteligencia")
                    print(f"{'─' * 60}")
                    seeds = discover_niches()
                    if not seeds:
                        print("\n  ⚠ No se generaron seeds. Abortando.")
                        return
                else:
                    seeds = existing
            else:
                print(f"\n{'─' * 60}")
                print(f"  📌 PASO 1/4 — Dashboard de Inteligencia")
                print(f"{'─' * 60}")
                seeds = discover_niches()
                if not seeds:
                    print("\n  ⚠ No se generaron seeds. Abortando.")
                    return
        else:
            seeds = _load_seeds()
            if not seeds:
                print("\n  ❌ No hay seeds en selected_seeds.json")
                print("  ➡  Corré sin --skip-niche para generarlos.")
                return
            print(f"\n  ⏭  Paso 1 saltado — {len(seeds)} seed(s) existentes")

        # ═════ PASO 1.5 — Juez LLM pre-grounding (solo spy_arbitrage) ═════
        # Marca cada seed spy con seed["judge"]; NO descarta. La auto-exclusión del
        # grounding (solo descartar 3/3) se decide acá abajo. Enriquecimiento: si falla,
        # se continúa SIN judge (no debe tumbar la corrida).
        seeds_to_ground = seeds
        if not skip_research and not skip_validate:
            try:
                from script_engine.m_judge_seeds import judge_seeds
                print(f"\n{'─' * 60}")
                print(f"  📌 PASO 1.5/4 — Juez LLM pre-grounding")
                print(f"{'─' * 60}")
                seeds = judge_seeds(seeds)          # agrega seed["judge"]
                _save_seeds_with_judge(seeds)        # persistir el judge
                _print_judge_summary(seeds)

                # Auto-exclusión SOLO de descartar 3/3 (decisión Omar). El resto se groundea.
                def _is_hard_discard(s: dict) -> bool:
                    j = s.get("judge") or {}
                    return j.get("verdict") == "descartar" and j.get("cohort") == "3/3"

                seeds_to_ground = [s for s in seeds if not _is_hard_discard(s)]
                excluded = [s for s in seeds if _is_hard_discard(s)]
                if excluded:
                    print(f"\n  ⏭  {len(excluded)} seed(s) excluidos del grounding "
                          f"(descartar 3/3): "
                          + ", ".join(s.get("seed_title", "?") for s in excluded))
            except Exception as e:
                print(f"\n  ⚠ Juez falló ({str(e)[:80]}) — se continúa SIN judge.")
                seeds_to_ground = seeds

        # ═════ PASO 1.6 — MENÚ DE SELECCIÓN ($0, ANTES del research caro) ═════
        # Chat 51: invertir el orden. Elegir sobre SEEDS (no sobre topics ya
        # investigados) → research SOLO del elegido. Mueve el checkpoint humano
        # antes del gasto de grounding (3 angle Pro + 4 sub-pasos Flash por seed):
        # antes se investigaba el lote entero para producir 1 y se tiraba el resto.
        # La auto-exclusión descartar-3/3 (PASO 1.5) ya ocurrió → esos ni se muestran.
        if not skip_research and not skip_validate:
            chosen = _select_seed_interactive(seeds_to_ground)
            if not chosen:
                print(f"\n  📌 Sin selección — no se investiga nada. Fin del Latido A.")
                return
            seeds_to_ground = chosen

        # ═════ PASO 2 — Topic Researcher (SOLO el/los elegido(s)) ═════
        if not skip_research and not skip_validate:
            print(f"\n{'─' * 60}")
            print(f"  📌 PASO 2/4 — Investigación de temas")
            if video_type == "long":
                print(f"     🔬 Deep Research activado (4 llamadas/seed)")
            print(f"{'─' * 60}")
            research_topics(seeds_to_ground, video_type=video_type)
        else:
            print(f"\n  ⏭  Paso 2 saltado")

        db = load_db()
        if not db.get("topics"):
            print("\n  ❌ No hay topics en topics_db.json. Abortando.")
            return

        # ═════ PASO 3 — Validator (propaga topic["video_type"]) ═════
        if not skip_validate:
            print(f"\n{'─' * 60}")
            print(f"  📌 PASO 3/4 — Validación de mercado ({video_type.upper()})")
            print(f"{'─' * 60}")
            validate_topics(video_type=video_type)
        else:
            print(f"\n  ⏭  Paso 3 saltado")

        # ═════ PASO 4 — Dashboard 2.0 ═════
        print(f"\n{'─' * 60}")
        print(f"  📌 PASO 4/4 — Exportar Dashboard 2.0 (CSV)")
        print(f"{'─' * 60}")
        csv_path = export_fase1_csv()
        print_export_summary(csv_path)

    finally:
        _close_cost_tracking()

    print(f"\n{'═' * 60}")
    print(f"  ✅ LATIDO A COMPLETADO")
    print(f"{'═' * 60}")
    # Chat 35: encadenar directo al menú de selección (sin parada manual).
    # Import local para evitar cualquier riesgo de import circular a nivel módulo.
    if not export_only:
        from fase1_5 import run_one_topic_from_menu
        print(f"\n  ➡  Pasando directo a la selección de tema...\n")
        run_one_topic_from_menu()
    else:
        print(f"\n  (--export-only) CSV regenerado. Corré `python fase1_5.py` "
              f"cuando quieras elegir un tema.\n")


# ═══════════════════════════════════════════════════════════════
#  LATIDO B — CSV editado → Scripts
# ═══════════════════════════════════════════════════════════════

def run_latido_b(csv_path: Path | None = None) -> None:
    """Latido B deprecado: redirige a fase1_5.py."""
    print(f"\n{'═' * 60}")
    print(f"  ⚠ Latido B (--process-csv) deprecado en fase1.py")
    print(f"{'═' * 60}")
    print(f"\n  La generación de guiones ahora corre en fase1_5.py.")
    print(f"\n  Usá:  python fase1_5.py")
    print(f"\n  Eso lee el CSV editado, corre m01a→m05→m06 sobre los")
    print(f"  topics aprobados, y al [P] genera el JSON final del contrato")
    print(f"  sagrado en data/scripts/<topic_id>.json.\n")
    return


# ═══════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Fase 1 — Pipeline de contenido viral (dos latidos)"
    )

    # Interruptor de latido
    parser.add_argument(
        "--process-csv", action="store_true",
        help="LATIDO B: procesar MI_DECISION del CSV y generar guiones",
    )

    # Flags de Latido A
    parser.add_argument(
        "--video-type", choices=["short", "long"],
        help="(Latido A) Tipo de video; si se omite, se pregunta",
    )
    parser.add_argument(
        "--skip-niche", action="store_true",
        help="(Latido A) Saltar paso 1 (usar seeds existentes)",
    )
    parser.add_argument(
        "--skip-research", action="store_true",
        help="(Latido A) Saltar pasos 1-2 (usar topics existentes)",
    )
    parser.add_argument(
        "--skip-validate", action="store_true",
        help="(Latido A) Saltar pasos 1-3 (usar topics ya validados)",
    )
    parser.add_argument(
        "--export-only", action="store_true",
        help="(Latido A) Solo regenerar el CSV",
    )

    args = parser.parse_args()

    if args.process_csv:
        run_latido_b()
    else:
        run_latido_a(
            video_type=args.video_type,
            skip_niche=args.skip_niche,
            skip_research=args.skip_research,
            skip_validate=args.skip_validate,
            export_only=args.export_only,
        )
