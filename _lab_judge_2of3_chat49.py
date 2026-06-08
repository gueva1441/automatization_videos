"""
_lab_judge_2of3_chat49.py — LAB T4 (NO cablear hasta validar): juez con regla 2/3-genérico.

Consenso (handoff chat 49): mayoría **2/3** votos `descartar`+`generico` → el seed se marca
`descartar`. NO veto de 1/3 (reintroduce la fragilidad que N=3 paga por evitar). Mantener la
lógica actual (flip-flop→inestable, 3/3) para `inestable` y `ratio_inflado`.

Este archivo NO toca prod. Define `_aggregate_v2` (la regla nueva) y un harness que:
  1. carga los 26 seeds de data/selected_seeds.json (solo spy_arbitrage),
  2. RE-CORRE el juez N=3 por seed (Gemini) — necesario porque el risk POR VOTO no se
     persiste, solo el verdict; la regla nueva necesita el risk de cada voto,
  3. aplica al MISMO set de votos el _aggregate viejo y _aggregate_v2 nuevo (aísla el efecto
     de la regla de la estocasticidad del juez),
  4. imprime la tabla antes/después + cuenta genéricos cazados y JOYAS muertas de más,
  5. escribe _lab_out/judge_2of3_chat49.json.

La LÓGICA de _aggregate_v2 está cubierta offline por test_t4_aggregate.py (sin Gemini).
La TABLA contra los 26 (este harness) es el entregable que decide el cableado.

Correr (en la máquina de Omar, con GEMINI_API_KEY):  python -X utf8 _lab_judge_2of3_chat49.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SEEDS_FILE = Path("data/selected_seeds.json")
OUT_FILE = Path("_lab_out/judge_2of3_chat49.json")
N_VOTES = 3


# ───────────────────────────────────────────────────────────────────
#  REGLA NUEVA (copia de _aggregate con la regla 2/3-genérico ANTES del flip-flop)
# ───────────────────────────────────────────────────────────────────

def _aggregate_v2(votes: list[dict], n: int) -> dict:
    """Igual que m_judge_seeds._aggregate, salvo la regla nueva al frente:
    si ≥2 votos son verdict='descartar' Y risk='generico' → descartar (cohorte k/n).
    Esto caza el genérico que hoy el flip-flop oro↔descartar salva como 'dudoso'."""
    verdicts = [v["verdict"] for v in votes]
    verdict_set = set(verdicts)

    # ── NUEVO T4: mayoría 2/3 'descartar'+'generico' (NO veto de 1) ──
    descartar_generico = [v for v in votes
                          if v["verdict"] == "descartar" and v.get("risk") == "generico"]
    if len(descartar_generico) >= 2:
        return {
            "verdict": "descartar",
            "risk": "generico",
            "reason": descartar_generico[0].get("reason", ""),
            "cohort": f"{len(descartar_generico)}/{n}",
            "votes": verdicts,
        }

    # ── resto IDÉNTICO a _aggregate actual ──
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
        "verdict": maj_verdict, "risk": maj_risk, "reason": maj_reason,
        "cohort": f"{maj_count}/{n}", "votes": verdicts,
    }


# ───────────────────────────────────────────────────────────────────
#  HARNESS LIVE (re-corre el juez para tener el risk por voto)
# ───────────────────────────────────────────────────────────────────

def main() -> None:
    from script_engine.m_judge_seeds import _judge_once, _aggregate  # juez prod (sin tocar)

    raw = json.loads(SEEDS_FILE.read_text(encoding="utf-8"))
    seeds = raw.get("seeds", raw) if isinstance(raw, dict) else raw
    spy = [s for s in seeds if s.get("discovery_mode") == "spy_arbitrage"]
    print(f"LAB T4 — re-juez {len(spy)} seeds spy · N={N_VOTES} · regla 2/3-genérico\n")

    rows, gen_caught, joyas_killed = [], 0, 0
    for i, seed in enumerate(spy, 1):
        title = seed.get("seed_title", "?")
        old_persisted = (seed.get("judge") or {}).get("verdict", "?")
        votes = [_judge_once(seed) for _ in range(N_VOTES)]   # votos frescos CON risk
        old = _aggregate(votes, N_VOTES)
        new = _aggregate_v2(votes, N_VOTES)
        changed = old["verdict"] != new["verdict"]
        if new["verdict"] == "descartar" and old["verdict"] != "descartar":
            gen_caught += 1
        # "joya muerta": era oro (persistido o en esta corrida) y la regla nueva la descarta
        if new["verdict"] == "descartar" and ("oro" in (old_persisted, old["verdict"])):
            joyas_killed += 1
        rows.append({
            "seed_title": title, "persisted": old_persisted,
            "old_verdict": old["verdict"], "old_cohort": old["cohort"],
            "new_verdict": new["verdict"], "new_cohort": new["cohort"],
            "new_risk": new["risk"], "votes": [v["verdict"] for v in votes],
            "risks": [v.get("risk") for v in votes], "changed": changed,
        })
        flag = "  ←CAMBIA" if changed else ""
        print(f"  [{i:2}/{len(spy)}] {title[:34]:<34} old={old['verdict']:<9} "
              f"new={new['verdict']:<9} ({new['cohort']}){flag}")

    print(f"\n  RESUMEN: genéricos NUEVOS cazados = {gen_caught} · JOYAS muertas de más = {joyas_killed}")
    print("  CRITERIO DE ÉXITO: caza genéricos (orfanato, prisión-más-embrujada…) con "
          "joyas_killed == 0. Si mata oro → reportar, NO cablear.")
    OUT_FILE.parent.mkdir(exist_ok=True)
    OUT_FILE.write_text(json.dumps({"rows": rows, "gen_caught": gen_caught,
                                    "joyas_killed": joyas_killed}, ensure_ascii=False, indent=2),
                        encoding="utf-8")
    print(f"\n  Guardado: {OUT_FILE}  (NADA cableado a prod)")


if __name__ == "__main__":
    main()
