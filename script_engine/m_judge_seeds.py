"""
m_judge_seeds.py — Juez LLM pre-grounding para seeds spy_arbitrage (FASE 2, cableado).

Promueve la lógica validada en _lab_judge_seeds.py a módulo productivo. Corre ANTES
del grounding caro, sobre los ~8 seeds que sobrevivieron la fórmula, para cazar los dos
falsos positivos que la fórmula no ve:
  1. Ratio inflado sobre canal chico (golpe de suerte, no demanda).
  2. Temas genéricos (formato saturado aunque el label diga hueco).

El juez NO reemplaza la fórmula ni descarta: marca cada seed con seed["judge"] y deja que
el humano decida en el menú. La auto-exclusión del grounding (solo descartar 3/3) la aplica
el CALLER en fase1.py — este módulo solo juzga.

Solo procesa discovery_mode == "spy_arbitrage". Otros modos pasan intactos.

Función pública:
    judge_seeds(seeds, n_votes=3) -> list[dict]   (mismos seeds, con seed["judge"])

Re-validación aislada:
    python -m script_engine.m_judge_seeds
"""

import json
import sys
from collections import Counter
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from gemini_helpers import call_flash_json
from config import DATA_DIR

SEEDS_FILE = DATA_DIR / "selected_seeds.json"
N_VOTES = 3  # votación por mayoría (mismo patrón que m05)


# ───────────────────────────────────────────────────────────────────
#  PROMPT DEL JUEZ (validado en el lab)
# ───────────────────────────────────────────────────────────────────

def _fmt_heaviest(es_gap: dict) -> str:
    h = es_gap.get("heaviest")
    if isinstance(h, dict):
        title = (h.get("title") or "?").strip()
        views = h.get("views")
        return f"{title} ({views:,} vistas)" if isinstance(views, int) else title
    return "ninguno"


def _build_judge_prompt(seed: dict) -> str:
    ev = seed.get("evidence") or {}
    en = ev.get("en_viral") or {}
    es_gap = ev.get("es_gap") or {}
    # T5 (chat 49): la edad puede ser None (fecha no parseable, o subtema de fan-out que no la
    # propaga). Antes llegaba como 999 y el juez lo leía "viejísimo" → sesgaba el voto. Ahora
    # se muestra "desconocida" y el prompt instruye NO penalizar por fecha en ese caso.
    age = en.get("en_age_months")
    age_str = f"{age} meses" if isinstance(age, int) else "desconocida"
    return f"""\
Sos un analista de contenido para un canal faceless de YouTube en español, nicho historia
oscura / desastres / misterio, documental 8-10 min.

Te doy UN candidato a tema, con la data REAL scrapeada de YouTube (no inventes nada fuera
de esto). Decidí si vale la pena producirlo.

DATA DEL CANDIDATO:
- título: {seed.get('seed_title')}
- viral en inglés: {en.get('original_title')}
- vistas EN: {en.get('views')}
- ratio outlier: {en.get('outlier_ratio')}x  (vistas ÷ mediana del canal)
- mediana del canal: {en.get('channel_median')}
- edad del viral: {age_str}
- saturación ES: label={es_gap.get('label')}, competidor más pesado={_fmt_heaviest(es_gap)}

CRITERIOS (en este orden):
1. DEMANDA REAL vs RATIO INFLADO. Ratio alto (ej. 185x) sobre mediana chica (ej. 2.000) =
   golpe de suerte de un canal diminuto, NO demanda del tema. Vistas absolutas altas (1M+)
   sobre mediana grande = demanda sostenida real. Marcá cuál es.
   Si la edad del viral es "desconocida", NO la uses como señal: no asumas que es viejo ni
   penalices por fecha — decidí solo con vistas, ratio, mediana y saturación.
2. ESPECIFICIDAD. Un título genérico ("sitios militares abandonados américa", "lugares
   prohibidos") compite en formato saturado aunque el label diga hueco. Un título con nombre
   propio / lugar / caso concreto ("Corpsewood Manor", "búnkeres de Albania") es defendible.
   Penalizá lo genérico.
3. HUECO ES. label VACÍO/HUECO = español libre (bueno). DISPUTADO = competencia real.

Respondé SOLO con un JSON (sin markdown):
{{"verdict": "oro|dudoso|descartar", "risk": "ninguno|ratio_inflado|generico|disputado", "reason": "1 frase"}}"""


# ───────────────────────────────────────────────────────────────────
#  VOTACIÓN
# ───────────────────────────────────────────────────────────────────

def _judge_once(seed: dict) -> dict:
    """Una evaluación del juez. Tolera respuesta malformada (no rompe la corrida)."""
    prompt = _build_judge_prompt(seed)
    try:
        data = call_flash_json(prompt)
    except Exception as e:
        return {"verdict": "error", "risk": "error", "reason": str(e)[:80]}
    verdict = str(data.get("verdict", "error")).strip().lower()
    risk = str(data.get("risk", "ninguno")).strip().lower()
    reason = str(data.get("reason", "")).strip()
    return {"verdict": verdict, "risk": risk, "reason": reason}


def _aggregate(votes: list[dict], n: int) -> dict:
    """Agrega N votos por mayoría, con manejo defensivo de inestabilidad.

    - flip-flop fuerte oro↔descartar → degrada a "dudoso", risk="inestable",
      cohort marcado con '*'. (El lab no lo necesitó; es defensa.)
    - empate / votos error → mayoría simple; si no hay señal, "dudoso".
    """
    verdicts = [v["verdict"] for v in votes]
    verdict_set = set(verdicts)

    # ── Inestabilidad fuerte: ambos extremos presentes ──
    if "oro" in verdict_set and "descartar" in verdict_set:
        oro_reason = next((v["reason"] for v in votes if v["verdict"] == "oro"), "")
        return {
            "verdict": "dudoso",
            "risk": "inestable",
            "reason": (f"Inestable (flip-flop oro↔descartar): {verdicts}. "
                       f"Degradado a dudoso. {oro_reason}".strip()),
            "cohort": f"{Counter(verdicts).most_common(1)[0][1]}/{n}*",
            "votes": verdicts,
        }

    verdict_counts = Counter(verdicts)
    maj_verdict, maj_count = verdict_counts.most_common(1)[0]

    aligned = [v for v in votes if v["verdict"] == maj_verdict]
    aligned_risks = [v["risk"] for v in aligned]
    maj_risk = Counter(aligned_risks).most_common(1)[0][0] if aligned_risks else "ninguno"
    maj_reason = aligned[0]["reason"] if aligned else ""

    return {
        "verdict": maj_verdict,
        "risk": maj_risk,
        "reason": maj_reason,
        "cohort": f"{maj_count}/{n}",
        "votes": verdicts,
    }


# ───────────────────────────────────────────────────────────────────
#  API PÚBLICA
# ───────────────────────────────────────────────────────────────────

def judge_seeds(seeds: list[dict], n_votes: int = N_VOTES, force: bool = False) -> list[dict]:
    """
    Juzga seeds spy_arbitrage pre-grounding. Devuelve los MISMOS seeds con
    seed["judge"] agregado. NO descarta, NO reordena destructivamente, NO toca otros modos.

    Otros discovery_mode pasan intactos (sin la clave "judge"), sin gastar llamadas.

    Cache: si seed["judge"] YA está persistido (fase1 lo guarda en selected_seeds.json
    para que el juicio sobreviva), NO se re-juzga — evita N llamadas LLM repetidas por
    corrida con seeds reusados. `force=True` (fase1 --rejudge) fuerza el re-juzgado.
    """
    if not seeds:
        return seeds

    spy = [s for s in seeds if s.get("discovery_mode") == "spy_arbitrage"]
    if not spy:
        print("  🤖 Juez: no hay seeds spy_arbitrage para juzgar (otros modos intactos).")
        return seeds

    print(f"\n  🤖 Juez LLM pre-grounding — {len(spy)} seed(s) spy_arbitrage · N={n_votes} votos"
          f"{' · --rejudge (forzado)' if force else ''}")
    for i, seed in enumerate(spy, 1):
        title = seed.get("seed_title", "?")
        if seed.get("judge") and not force:
            j = seed["judge"]
            print(f"    [{i}/{len(spy)}] {title} → (cacheado) {j.get('verdict')} ({j.get('cohort')})")
            continue
        votes = [_judge_once(seed) for _ in range(n_votes)]
        seed["judge"] = _aggregate(votes, n_votes)
        j = seed["judge"]
        print(f"    [{i}/{len(spy)}] {title} → {j['verdict']} ({j['cohort']}) · riesgo: {j['risk']}")
        if j["risk"] == "inestable":
            print(f"          ⚠ inestable: votos {j['votes']} — degradado a dudoso")

    return seeds


# ───────────────────────────────────────────────────────────────────
#  RE-VALIDACIÓN AISLADA
# ───────────────────────────────────────────────────────────────────

def _print_table(seeds: list[dict]) -> None:
    spy = [s for s in seeds if s.get("discovery_mode") == "spy_arbitrage"]
    print(f"\n{'═' * 78}")
    print(f"  RESUMEN JUEZ")
    print(f"{'═' * 78}")
    print(f"  {'VEREDICTO':<11} {'COHORTE':<8} {'RIESGO':<14} {'es_gap':<10} TEMA")
    print(f"  {'-'*11} {'-'*8} {'-'*14} {'-'*10} {'-'*30}")
    for s in spy:
        j = s.get("judge") or {}
        es_gap = (s.get("evidence") or {}).get("es_gap") or {}
        print(f"  {j.get('verdict','?'):<11} {j.get('cohort','?'):<8} "
              f"{j.get('risk','?'):<14} {str(es_gap.get('label')):<10} {s.get('seed_title','?')}")
    print()
    for s in spy:
        j = s.get("judge") or {}
        print(f"  • {s.get('seed_title','?')}: {j.get('reason','')}")
    print()


def _load_seeds_for_main() -> list[dict]:
    """Carga seeds de selected_seeds.json; si está vacío, cae a fixture de topics_db
    (mismo fallback que el lab) para poder re-validar aislado tras una corrida."""
    if SEEDS_FILE.exists():
        raw = json.loads(SEEDS_FILE.read_text(encoding="utf-8"))
        seeds = raw.get("seeds", raw) if isinstance(raw, dict) else raw
        spy = [s for s in (seeds or []) if s.get("discovery_mode") == "spy_arbitrage"
               and (s.get("evidence") or {})]
        if spy:
            return seeds
    # Fallback: reconstruir desde topics_db.json
    db_file = DATA_DIR / "topics_db.json"
    if not db_file.exists():
        return []
    db = json.loads(db_file.read_text(encoding="utf-8"))
    topics = db.get("topics", db) if isinstance(db, dict) else db
    out = []
    for t in (topics or []):
        if t.get("discovery_mode") != "spy_arbitrage":
            continue
        ev = t.get("evidence_from_discovery") or {}
        if not ev:
            continue
        out.append({
            "seed_title": t.get("search_keyword") or t.get("video_title") or "—",
            "discovery_mode": "spy_arbitrage",
            "evidence": ev,
        })
    return out


def main() -> None:
    seeds = _load_seeds_for_main()
    if not seeds:
        print("\n  ⚠ No hay seeds spy_arbitrage para juzgar.")
        return
    judge_seeds(seeds)
    _print_table(seeds)


if __name__ == "__main__":
    main()
