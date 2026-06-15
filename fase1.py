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
import os
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
from script_engine.subtopic_measurer import _measure_es   # CHAT 52 B2: gate de verificación del pick


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


# ─────────────────────────────────────────────────────────────────
#  Marcador del FORM (QA Studio). La terminal NO cambia: el marcador se imprime
#  SOLO si está seteada la env var QA_FORM (la setea el form al lanzar el subprocess).
#  Corrida por terminal pura (sin QA_FORM) = byte-idéntica a hoy. Contrato chat 61.
# ─────────────────────────────────────────────────────────────────

_QA_FORM = bool(os.environ.get("QA_FORM"))  # módulo-level, una vez


def _normalize_form_risk(risk: str | None) -> str:
    """judge.risk (ninguno|ratio_inflado|generico|disputado) → vocabulario del HTML
    de Design (ninguno|disputado|inflado). 'generico'/desconocido → 'ninguno'."""
    if risk == "disputado":
        return "disputado"
    if risk == "ratio_inflado":
        return "inflado"
    return "ninguno"


def _seed_to_form_item(idx: int, s: dict) -> dict:
    """Serializa UN seed de `ordered` al item del payload del form (§3 del contrato).
    Números CRUDOS (el formateo 8.0M / 200× lo hace el HTML)."""
    j = s.get("judge") or {}
    ev = s.get("evidence") or {}
    en = ev.get("en_viral") or {}
    es = ev.get("es_gap") or {}
    verdict = j.get("verdict")
    return {
        "idx": idx,
        "title": s.get("seed_title") or "(sin título)",
        "es_label": es.get("label") or "—",
        "competidores": es.get("ontopic_count"),
        "en_views": en.get("views"),
        "en_ratio": en.get("outlier_ratio"),
        "en_title": en.get("original_title"),
        "en_age_months": en.get("en_age_months"),
        "fallback": bool(en.get("query_fallback")) or bool(es.get("query_fallback")),
        "risk": _normalize_form_risk(j.get("risk")),
        "reason": (j.get("reason") or "").strip(),
        "verdict": verdict,
        "cohort": j.get("cohort"),
        "dudoso": verdict != "oro",   # oro → main; resto (dudoso/descartar) → dudosos
    }


def _emit_qaform_choice_marker(
    menu: str, prompt: str, options: list[dict],
    *, default: str | None = None, body: str | None = None,
) -> None:
    """Marcador GENÉRICO de choice (botones) — accept='key'. Para los menús de letras
    (S/L, S/n, etc.). El form dibuja un botón por option; el `key` es lo que el input()
    ya parsea. ASCII puro, 1 línea. Igual que el seed: solo se emite con _QA_FORM."""
    marker = {
        "menu": menu,
        "accept": "key",
        "prompt": prompt,
        "options": options,   # [{key, label, disabled?}]
        "default": default,
        "body": body,
    }
    print("@@QAFORM@@ " + json.dumps(marker, ensure_ascii=True), flush=True)


def _emit_qaform_seed_marker(ordered: list[dict]) -> None:
    """Imprime el marcador @@QAFORM@@ (1 línea, JSON ASCII puro — Windows-safe) que el
    form detecta para renderizar el diálogo de selección de seeds. El input()/parseo de
    abajo NO se tocan: el form escribe en stdin lo que ese input() ya parsea."""
    marker = {
        "menu": "seed_pick",
        "accept": "int_csv",
        "prompt": f"Elegí tema [1-{len(ordered)}] (coma para varios · Q para salir)",
        "payload": {"seeds": [_seed_to_form_item(i, s) for i, s in enumerate(ordered, start=1)]},
    }
    print("@@QAFORM@@ " + json.dumps(marker, ensure_ascii=True), flush=True)


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

    # Marcador del form (env-gated): el form lo detecta y renderiza el diálogo de Design.
    # Sin QA_FORM no se imprime → corrida por terminal idéntica.
    if _QA_FORM:
        _emit_qaform_seed_marker(ordered)

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


# CHAT 52 B2 — orden de "saturación" de los labels ES (para quedarse con el PEOR al re-medir).
_ES_LABEL_RANK = {"VACIO": 0, "HUECO": 1, "DISPUTADO": 2, "SATURADO": 3}


def _verify_pick_es_saturation(chosen: list[dict], n: int = 3) -> list[dict] | None:
    """CHAT 52 B2 — gate anti-varianza-de-scrape: re-mide ES `n` veces SOLO el/los pick(s) y se
    queda con el PEOR label (más saturado), igual que el patrón conservador del discovery
    (saturación del evento = la MÁS ALTA entre variantes). NO toca el discovery masivo.

    Si el peor label de las n corridas es SATURADO o DISPUTADO, avisa y PREGUNTA a Omar
    [P]roducir igual / [S]acar este pick / [Q]salir. NO auto-excluye. (El discovery masivo sigue
    descartando SOLO SATURADO — embudo ancho; el gate del pick es la red FINAL, más estricta: tras
    B1 los evergreen grandes sin fecha caen en DISPUTADO, no SATURADO, y no queremos producir sobre
    ellos sin confirmar.) Imprime las n mediciones para que se vea la dispersión. Seeds sin receta
    `remeasure` (Mode B / viejos) se conservan sin re-medir (no se puede re-medir lo que no se sabe medir).

    Devuelve la lista de picks que sobreviven, o None si Omar sale (Q) o no queda ninguno."""
    if not chosen:
        return None
    kept: list[dict] = []
    for seed in chosen:
        title = seed.get("seed_title") or "(sin título)"
        recipe = seed.get("remeasure")
        if not recipe or not recipe.get("es_query"):
            print(f"\n  ℹ '{title}': sin receta remeasure (Mode B / seed viejo) — no se re-mide.")
            kept.append(seed)
            continue

        print(f"\n  🔁 Verificando el pick '{title}' — re-mido ES {n}× (anti-varianza de scrape)...")
        measurements: list[tuple[str, float]] = []
        for k in range(n):
            try:
                r = _measure_es(recipe["es_query"], recipe.get("entity"),
                                already_es=recipe.get("already_es", False))
            except Exception as e:
                print(f"      corrida {k + 1}/{n}: EXCEPCIÓN ({str(e)[:70]})")
                continue
            lab = r.get("label")
            if lab == "ERROR":
                print(f"      corrida {k + 1}/{n}: ERROR ({r.get('error')})")
                continue
            sat = r.get("saturation") or 0
            measurements.append((lab, sat))
            print(f"      corrida {k + 1}/{n}: {lab} (sat={sat:,.0f})")

        if not measurements:
            print(f"      ⚠ todas las corridas fallaron — no se pudo verificar. Conservo el pick.")
            kept.append(seed)
            continue

        worst_lab, worst_sat = max(
            measurements, key=lambda m: (_ES_LABEL_RANK.get(m[0], -1), m[1]))
        orig_lab = ((seed.get("evidence") or {}).get("es_gap") or {}).get("label") or "—"
        print(f"      → peor de {len(measurements)}: {worst_lab} (sat={worst_sat:,.0f}) "
              f"· el seed decía: {orig_lab}")

        if worst_lab not in ("SATURADO", "DISPUTADO"):
            kept.append(seed)
            continue

        detail = ("el nicho NO está libre (competidor tamaño viral)" if worst_lab == "SATURADO"
                  else "hay competencia real, no es hueco limpio — confirmá antes de gastar")
        print(f"\n  ⚠ El pick '{title}' FLIPEÓ a {worst_lab} al re-medir — {detail}.")
        while True:
            ans = input(f"     [P]roducir igual · [S]acar este pick · [Q]salir: ").strip().upper()
            if ans == "P":
                print(f"     → producís igual (bajo tu criterio).")
                kept.append(seed)
                break
            if ans == "S":
                print(f"     → saco '{title}' del research.")
                break
            if ans == "Q":
                print(f"     → salgo. No se investiga nada.")
                return None
            print(f"     Opción inválida (P/S/Q).")

    if not kept:
        print(f"\n  📌 Ningún pick sobrevivió la verificación — no se investiga nada.")
        return None
    return kept


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
    if _QA_FORM:
        _emit_qaform_choice_marker(
            "video_type", "Tipo de video para esta corrida",
            [{"key": "S", "label": "SHORT — 45-60s, vertical, pipeline rápido"},
             {"key": "L", "label": "LONG — 8-10 min, documental (híbrido Veo + Leonardo)"}],
            default="S",
        )
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
    rejudge: bool = False,
    no_chain: bool = False,
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
                if _QA_FORM:
                    _prev = "\n".join(
                        f"[{s.get('discovery_mode', '?')}] {s.get('seed_title', '?')}"
                        for s in existing[:5])
                    if len(existing) > 5:
                        _prev += f"\n... y {len(existing) - 5} más"
                    _emit_qaform_choice_marker(
                        "reuse_seeds", f"Tenés {len(existing)} seed(s) previos — ¿usarlos?",
                        # 'n' (discovery) abre menús anidados todavía sin marcador → colgaría
                        # en el form; lo dejamos deshabilitado (el happy path asistido es reusar).
                        [{"key": "S", "label": "Usar estos seeds"},
                         {"key": "n", "label": "Buscar nuevos (discovery) — desde la terminal",
                          "disabled": True}],
                        default="S", body=_prev,
                    )
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
                seeds = judge_seeds(seeds, force=rejudge)   # agrega/respeta seed["judge"]
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
            # CHAT 52 B2 — GATE DE VERIFICACIÓN DEL PICK (mata la varianza de scrape del elegido):
            chosen = _verify_pick_es_saturation(chosen, n=3)
            if not chosen:
                return    # Omar abortó (Q) o ningún pick sobrevivió tras re-medir
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
    # Chat 57 (--no-chain): cuando run_pipeline --research maneja el resto, fase1 NO
    # debe auto-encadenar al guion (ahí el tid queda enterrado en run_one_topic_from_menu
    # y no se puede secuenciar 2a/2b/3). El default (no_chain=False) encadena como hoy.
    if export_only:
        print(f"\n  (--export-only) CSV regenerado. Corré `python fase1_5.py` "
              f"cuando quieras elegir un tema.\n")
    elif no_chain:
        print(f"\n  ✅ Tema validado. Seguí con: python run_pipeline.py --research "
              f"(ya encadena)\n")
    else:
        from fase1_5 import run_one_topic_from_menu
        print(f"\n  ➡  Pasando directo a la selección de tema...\n")
        run_one_topic_from_menu()


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
    parser.add_argument(
        "--rejudge", action="store_true",
        help="(Latido A) Forzar re-juzgado de seeds spy aunque ya tengan seed['judge'] "
             "cacheado (default: respeta el judge persistido, sin re-llamar al LLM).",
    )
    parser.add_argument(
        "--no-chain", action="store_true",
        help="(Latido A) NO auto-encadenar al guion (fase1_5) al final. Para cuando "
             "run_pipeline --research toma el control y secuencia el resto.",
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
            rejudge=args.rejudge,
            no_chain=args.no_chain,
        )
