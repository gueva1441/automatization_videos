"""
_lab_formula_validate_chat42.py — FASE B (chat 42→43). LAB de VALIDACIÓN de "la fórmula".
DETERMINISTA, sin Gemini, sin red. Lee transcripts_v2_chat42.json y computa V1–V4 (las
hipótesis que Claude chat sacó a mano). Solo imprime + escribe un reporte JSON.
NO saca conclusiones ni propone prompts — solo números.

SET MOLDE = joyas (new=True) formato=="documental_narrado" Y drift==False.
CONTROL   = rechazadas (new=False) del mismo formato.
(Charlas y drift se EXCLUYEN del molde pero se listan aparte para trazabilidad.)

Output: _lab_out/formula_report_chat42.json + tabla a consola.

USO:
    python -X utf8 _lab_formula_validate_chat42.py
    python -X utf8 _lab_formula_validate_chat42.py --smoke
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

IN_JSON = Path("_lab_out/transcripts_v2_chat42.json")
OUT_JSON = Path("_lab_out/formula_report_chat42.json")
HOOK_WORDS = 60

_SUPER = (r"\b(most|scariest|largest|never|deepest|biggest|strangest|worst|greatest|"
          r"deadliest|terrifying|unexplained|mysterious|disturbing|shocking|incredible|"
          r"unbelievable|forbidden)\b")
_MONTHS = (r"\b(january|february|march|april|may|june|july|august|september|october|"
           r"november|december)\b")
_TENSION = (r"\b(mystery|mysteries|secret|secrets|unexplained|reveal|reveals|revealed|"
            r"strange|terrifying|hidden|disappear|disappeared|disappearance|truth)\b")


# ─── features PURAS (GATE A) ───
def first_n_words(text: str, n: int = HOOK_WORDS) -> str:
    return " ".join(text.split()[:n])


def hook_features(text60: str) -> dict:
    s = text60.lower()
    numero = bool(re.search(r"\d", text60))
    escena = bool(re.search(r"\b(19\d{2}|20\d{2})\b", s)) or bool(re.search(_MONTHS, s))
    return {
        "numero": numero,
        "superlativo": bool(re.search(_SUPER, s)),
        "segunda_persona": bool(re.search(r"\b(you|your|you're|you've|yourself)\b", s)),
        "escena_fecha": escena,
        "concrecion_temprana": numero or escena,
    }


def is_hook_segment(seg_text: str) -> bool:
    return ("?" in seg_text) or bool(re.search(r"\d", seg_text)) or \
        bool(re.search(_TENSION, seg_text.lower()))


def _total_duration(segments: list[dict]) -> float:
    """Largo total robusto = max(start+duration) (los segments pueden no venir ordenados)."""
    if not segments:
        return 0.0
    return max(float(s.get("start", 0) or 0) + float(s.get("duration", 0) or 0)
               for s in segments)


def cadence_seconds(segments: list[dict]) -> float | None:
    """Segundos promedio entre segmentos-gancho consecutivos (starts ORDENADOS)."""
    starts = sorted(float(s.get("start", 0) or 0) for s in segments
                    if is_hook_segment(s.get("text", "")))
    if len(starts) < 2:
        return None
    gaps = [starts[i + 1] - starts[i] for i in range(len(starts) - 1)]
    return sum(gaps) / len(gaps) if gaps else None


def reveal_position_pct(segments: list[dict]) -> float | None:
    """% del video donde cae el segmento con más densidad de tensión (proxy del reveal).
    Robusto: total = max(start+duration); clamp a [0,100] (segments no siempre ordenados)."""
    total = _total_duration(segments)
    if total <= 0:
        return None
    best_start, best_c = None, -1
    for s in segments:
        c = len(re.findall(_TENSION, s.get("text", "").lower()))
        if c > best_c:
            best_c, best_start = c, float(s.get("start", 0) or 0)
    if best_start is None or best_c <= 0:
        return None
    return min(max(best_start / total * 100.0, 0.0), 100.0)


# ─── SMOKE (GATE A) ───
def run_smoke() -> int:
    print("  SMOKE features FASE B (sin red)")
    fails = []
    f1 = hook_features("July 19th 1969 the 3 deepest most mysterious abysses you have")
    for k, exp in [("numero", True), ("escena_fecha", True), ("superlativo", True),
                   ("segunda_persona", True), ("concrecion_temprana", True)]:
        ok = f1[k] == exp
        print(f"    hook[{k}]={f1[k]} esp {exp}  {'OK' if ok else 'FAIL'}")
        if not ok:
            fails.append(f"hook {k}")
    f2 = hook_features("a calm quiet plain sentence about nothing in particular here")
    ok2 = not any(f2.values())
    print(f"    hook(plano) todo False = {not any(f2.values())}  {'OK' if ok2 else 'FAIL'}")
    if not ok2:
        fails.append("hook plano")
    for name, txt, exp in [("?", "what lies beneath?", True), ("num", "in 1942 a ship", True),
                           ("tension", "a hidden secret", True), ("plano", "the cat sat", False)]:
        got = is_hook_segment(txt)
        ok = got == exp
        print(f"    is_hook({name})={got} esp {exp}  {'OK' if ok else 'FAIL'}")
        if not ok:
            fails.append(f"is_hook {name}")
    cad = cadence_seconds([{"start": 0, "text": "secret"}, {"start": 10, "text": "mystery"},
                           {"start": 30, "text": "reveal"}])
    print(f"    cadence([0,10,30]) = {cad} esp 15.0  {'OK' if cad == 15.0 else 'FAIL'}")
    if cad != 15.0:
        fails.append("cadence")
    print("  " + "─" * 50)
    if fails:
        print(f"  [SMOKE FAIL] {fails}")
        return 1
    print("  [SMOKE OK]")
    return 0


def _pct(items: list[dict], key: str) -> float:
    if not items:
        return 0.0
    return sum(1 for it in items if it["feat"][key]) / len(items) * 100.0


def _avg(vals: list) -> float | None:
    vals = [v for v in vals if v is not None]
    return sum(vals) / len(vals) if vals else None


def main() -> int:
    if "--smoke" in sys.argv:
        return run_smoke()
    if run_smoke() != 0:
        return 1
    if not IN_JSON.exists():
        print(f"\n❌ no existe {IN_JSON} — corré FASE A primero "
              f"(_lab_transcripts_v2_chat42.py)")
        return 1

    rows = json.loads(IN_JSON.read_text(encoding="utf-8"))
    # enriquecer cada fila ok con features
    enriched = []
    for r in rows:
        if r.get("status") != "ok":
            continue
        feat = hook_features(first_n_words(r.get("transcript", "")))
        enriched.append({
            "video_id": r["video_id"], "title": r["title"], "subnicho": r.get("subnicho"),
            "new": bool(r.get("new")), "formato": r.get("formato"),
            "drift": bool(r.get("drift")), "ratio": r.get("ratio"), "views": r.get("views"),
            "feat": feat,
            "cadence_s": cadence_seconds(r.get("segments", [])),
            "reveal_pct": reveal_position_pct(r.get("segments", [])),
        })

    joyas = [e for e in enriched if e["new"]]
    molde = [e for e in joyas if e["formato"] == "documental_narrado" and not e["drift"]]
    control = [e for e in enriched if not e["new"] and e["formato"] == "documental_narrado"]
    charlas = [e for e in joyas if e["formato"] == "charla_entrevista"]
    drift_joyas = [e for e in joyas if e["drift"]]

    print("\n" + "=" * 66)
    print("  V1 — FILTRO DE FORMATO")
    print("=" * 66)
    fc_all = Counter(e["formato"] for e in enriched)
    fc_joyas = Counter(e["formato"] for e in joyas)
    print(f"  formato (todos ok, n={len(enriched)}): {dict(fc_all)}")
    print(f"  formato (joyas, n={len(joyas)}):       {dict(fc_joyas)}")
    print(f"  SET MOLDE (joya+documental+sin drift): {len(molde)}")
    print(f"  CONTROL  (rechazada+documental):       {len(control)}")
    print(f"  charlas excluidas: {len(charlas)} | drift excluidas: {len(drift_joyas)}")
    print(f"  → SET MOLDE ({len(molde)}) {'≠' if len(molde) != len(joyas) else '=='} "
          f"todas las joyas ({len(joyas)})")

    print("\n" + "=" * 66)
    print("  V2 — ADN DEL HOOK (primeras 60 palabras, SET MOLDE)")
    print("=" * 66)
    feats = ["numero", "superlativo", "segunda_persona", "escena_fecha", "concrecion_temprana"]
    v2 = {f: round(_pct(molde, f), 1) for f in feats}
    for f in feats:
        print(f"    {f:<20} {v2[f]:>5.1f}%")
    print(f"  hipótesis 'concreción temprana en la mayoría': "
          f"{'SÍ' if v2['concrecion_temprana'] > 50 else 'NO'} ({v2['concrecion_temprana']}%)")

    print("\n" + "=" * 66)
    print("  V3 — DISCRIMINADOR MOLDE vs CONTROL")
    print("=" * 66)
    v3_molde = {f: round(_pct(molde, f), 1) for f in feats}
    v3_control = {f: round(_pct(control, f), 1) for f in feats}
    print(f"    {'feature':<20} {'MOLDE':>8} {'CONTROL':>8} {'Δ':>8}")
    for f in feats:
        print(f"    {f:<20} {v3_molde[f]:>7.1f}% {v3_control[f]:>7.1f}% "
              f"{v3_molde[f] - v3_control[f]:>+7.1f}")
    delta_num = round(v3_molde["numero"] - v3_control["numero"], 1)
    print(f"  delta 'número temprano' (a mano dio 62% vs 22% = +40): "
          f"molde {v3_molde['numero']}% vs control {v3_control['numero']}% = {delta_num:+.1f} "
          f"(n chico: molde={len(molde)}, control={len(control)} — señal, no ley)")

    print("\n" + "=" * 66)
    print("  V4 — CADENCIA DE GANCHOS (usa timestamps)")
    print("=" * 66)
    cad_molde = _avg([e["cadence_s"] for e in molde])
    cad_control = _avg([e["cadence_s"] for e in control])
    rev_molde = _avg([e["reveal_pct"] for e in molde])
    rev_control = _avg([e["reveal_pct"] for e in control])
    print(f"    cadencia media entre ganchos (seg):  MOLDE {cad_molde if cad_molde is None else round(cad_molde,1)}  "
          f"CONTROL {cad_control if cad_control is None else round(cad_control,1)}")
    print(f"    posición media del reveal (%):       MOLDE {rev_molde if rev_molde is None else round(rev_molde,1)}  "
          f"CONTROL {rev_control if rev_control is None else round(rev_control,1)}")
    if cad_molde is not None and cad_control is not None:
        print(f"  hipótesis 'molde sostiene ganchos más seguido': "
              f"{'SÍ' if cad_molde < cad_control else 'NO'} "
              f"(molde {round(cad_molde,1)}s {'<' if cad_molde < cad_control else '>='} "
              f"control {round(cad_control,1)}s)")

    # ─── listados para trazabilidad ───
    def _lst(group):
        return [{"video_id": e["video_id"], "title": e["title"], "ratio": e["ratio"],
                 "cadence_s": e["cadence_s"], "reveal_pct": e["reveal_pct"],
                 **{k: e["feat"][k] for k in feats}} for e in group]

    report = {
        "n_ok": len(enriched), "n_joyas": len(joyas),
        "set_molde": len(molde), "control": len(control),
        "charlas_excluidas": len(charlas), "drift_excluidas": len(drift_joyas),
        "formato_counts_all": dict(fc_all), "formato_counts_joyas": dict(fc_joyas),
        "V2_hook_adn_molde": v2,
        "V3_discriminador": {"molde": v3_molde, "control": v3_control, "delta_numero": delta_num},
        "V4_cadencia": {
            "molde_cadencia_s": cad_molde, "control_cadencia_s": cad_control,
            "molde_reveal_pct": rev_molde, "control_reveal_pct": rev_control,
        },
        "molde": _lst(molde), "control": _lst(control),
        "charlas": _lst(charlas), "drift": _lst(drift_joyas),
    }
    OUT_JSON.parent.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n  reporte guardado: {OUT_JSON}")
    print(f"  → Omar + Claude (chat) leen los números y deciden el molde de m01b. "
          f"(Este lab NO concluye.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
