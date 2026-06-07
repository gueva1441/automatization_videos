"""
_lab_judge_seeds.py — LAB del juez LLM pre-grounding para seeds spy-arbitrage.

NO cablea nada. NO escribe a disco. Solo corre el juez N=3 sobre seeds reales
(o, si selected_seeds.json está vacío, sobre fixtures reconstruidos de la
evidencia ya persistida en topics_db.json) e imprime una tabla comparativa para
validar contra lo esperado ANTES de diseñar el cableado (FASE 2).

Costo: N × seeds llamadas a Flash (centavos).

Uso:
    python _lab_judge_seeds.py
"""

import json
import sys
from collections import Counter
from pathlib import Path

# Salida UTF-8 (títulos con acentos/ñ) — evita UnicodeEncodeError en consolas cp1252.
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

from gemini_helpers import call_flash_json

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"
SEEDS_FILE = DATA_DIR / "selected_seeds.json"
TOPICS_DB_FILE = DATA_DIR / "topics_db.json"

N_VOTES = 3  # votación por mayoría (mismo patrón que m05)


# ───────────────────────────────────────────────────────────────────
#  CARGA DE SEEDS (real → fallback fixture desde topics_db)
# ───────────────────────────────────────────────────────────────────

def _load_real_seeds() -> list[dict]:
    """Seeds spy_arbitrage de selected_seeds.json (con evidence poblada)."""
    if not SEEDS_FILE.exists():
        return []
    raw = json.loads(SEEDS_FILE.read_text(encoding="utf-8"))
    seeds = raw.get("seeds", raw) if isinstance(raw, dict) else raw
    out = []
    for s in (seeds or []):
        if s.get("discovery_mode") == "spy_arbitrage" and (s.get("evidence") or {}):
            out.append(s)
    return out


def _fixture_from_topics_db() -> list[dict]:
    """Reconstruye seeds spy_arbitrage desde la evidencia persistida en topics_db.
    Usa search_keyword como proxy de seed_title (es la entidad pre-narrativa, el
    mejor anclaje de ESPECIFICIDAD disponible post-grounding) y
    evidence_from_discovery como evidence."""
    if not TOPICS_DB_FILE.exists():
        return []
    db = json.loads(TOPICS_DB_FILE.read_text(encoding="utf-8"))
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
            # solo para mostrar en la tabla del lab:
            "_video_title": t.get("video_title"),
        })
    return out


def load_seeds() -> tuple[list[dict], str]:
    real = _load_real_seeds()
    if real:
        return real, "selected_seeds.json (real)"
    return _fixture_from_topics_db(), "topics_db.json (fixture — selected_seeds vacío)"


# ───────────────────────────────────────────────────────────────────
#  JUEZ
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
- edad del viral: {en.get('en_age_months')} meses
- saturación ES: label={es_gap.get('label')}, competidor más pesado={_fmt_heaviest(es_gap)}

CRITERIOS (en este orden):
1. DEMANDA REAL vs RATIO INFLADO. Ratio alto (ej. 185x) sobre mediana chica (ej. 2.000) =
   golpe de suerte de un canal diminuto, NO demanda del tema. Vistas absolutas altas (1M+)
   sobre mediana grande = demanda sostenida real. Marcá cuál es.
2. ESPECIFICIDAD. Un título genérico ("sitios militares abandonados américa", "lugares
   prohibidos") compite en formato saturado aunque el label diga hueco. Un título con nombre
   propio / lugar / caso concreto ("Corpsewood Manor", "búnkeres de Albania") es defendible.
   Penalizá lo genérico.
3. HUECO ES. label VACÍO/HUECO = español libre (bueno). DISPUTADO = competencia real.

Respondé SOLO con un JSON (sin markdown):
{{"verdict": "oro|dudoso|descartar", "risk": "ninguno|ratio_inflado|generico|disputado", "reason": "1 frase"}}"""


def judge_once(seed: dict) -> dict:
    """Una evaluación del juez. Tolera respuesta malformada (no rompe el lab)."""
    prompt = _build_judge_prompt(seed)
    try:
        data = call_flash_json(prompt)
    except Exception as e:
        return {"verdict": "error", "risk": "error", "reason": str(e)[:80]}
    verdict = str(data.get("verdict", "error")).strip().lower()
    risk = str(data.get("risk", "ninguno")).strip().lower()
    reason = str(data.get("reason", "")).strip()
    return {"verdict": verdict, "risk": risk, "reason": reason}


def judge_seed(seed: dict, n: int = N_VOTES) -> dict:
    """Corre el juez n veces y agrega por mayoría."""
    votes = [judge_once(seed) for _ in range(n)]
    verdicts = [v["verdict"] for v in votes]
    risks = [v["risk"] for v in votes]

    verdict_counts = Counter(verdicts)
    maj_verdict, maj_count = verdict_counts.most_common(1)[0]

    # riesgo de mayoría entre los votos que coinciden con el veredicto ganador
    aligned_risks = [v["risk"] for v in votes if v["verdict"] == maj_verdict]
    maj_risk = Counter(aligned_risks).most_common(1)[0][0] if aligned_risks else "—"

    # razón representativa: la del primer voto que coincide con la mayoría
    maj_reason = next((v["reason"] for v in votes if v["verdict"] == maj_verdict), "")

    return {
        "verdict": maj_verdict,
        "cohort": f"{maj_count}/{n}",
        "risk": maj_risk,
        "reason": maj_reason,
        "all_verdicts": verdicts,
        "all_risks": risks,
    }


# ───────────────────────────────────────────────────────────────────
#  MAIN
# ───────────────────────────────────────────────────────────────────

def main() -> None:
    seeds, source = load_seeds()
    print(f"\n{'═' * 78}")
    print(f"  LAB JUEZ DE SEEDS (spy_arbitrage) — N={N_VOTES} votos/seed")
    print(f"  Fuente: {source}")
    print(f"  Seeds a juzgar: {len(seeds)}  ·  NO escribe a disco")
    print(f"{'═' * 78}")

    if not seeds:
        print("\n  ⚠ No hay seeds spy_arbitrage para juzgar (ni en selected_seeds ni en topics_db).")
        return

    rows = []
    for i, seed in enumerate(seeds, 1):
        title = seed.get("seed_title", "?")
        ev = seed.get("evidence") or {}
        en = ev.get("en_viral") or {}
        es_gap = ev.get("es_gap") or {}
        print(f"\n  [{i}/{len(seeds)}] Juzgando: {title}")
        print(f"        views={en.get('views')}  ratio={en.get('outlier_ratio')}  "
              f"median={en.get('channel_median')}  es_gap={es_gap.get('label')}")
        res = judge_seed(seed)
        print(f"        → votos: {res['all_verdicts']}  | riesgos: {res['all_risks']}")
        rows.append((title, en, es_gap, res))

    # ─── Tabla resumen ───
    print(f"\n{'═' * 78}")
    print(f"  RESUMEN")
    print(f"{'═' * 78}")
    print(f"  {'VEREDICTO':<11} {'COHORTE':<8} {'RIESGO':<14} {'es_gap':<10} TEMA")
    print(f"  {'-'*11} {'-'*8} {'-'*14} {'-'*10} {'-'*30}")
    for title, en, es_gap, res in rows:
        print(f"  {res['verdict']:<11} {res['cohort']:<8} {res['risk']:<14} "
              f"{str(es_gap.get('label')):<10} {title}")

    print()
    for title, en, es_gap, res in rows:
        print(f"  • {title}: {res['reason']}")
    print()


if __name__ == "__main__":
    main()
