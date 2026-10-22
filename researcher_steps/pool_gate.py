"""
researcher_steps/pool_gate.py — F7d (HANDOFF_F7 §9.2): compuerta del pool, el semáforo entre research y guion.

Puntaje determinista sobre el evidence_pool de research v3, antes de escaleta, guion e imágenes:
    verde     datos ≥ 150 · citas verificadas ≥ 8 · humanos elegibles ≥ 2 · eventos con fecha ≥ 10 → 12 min, normal
    amarillo  todo ≥ la mitad de cada umbral → target_words 1,200 (≈ 10 min), escaleta de 7–8 beats, aviso en el reporte
              (el handoff dice 6–8 beats; el contrato de 7 caps con ≥ 1 beat cada uno pone el piso en 7)
    rojo      algo por debajo de la mitad → el topic vuelve al inbox con el motivo y no se gasta en guion ni imágenes
Umbrales en script_engine/video_length.py (DEFAULTS, `config.long_video` los pisa). Reporte POOL_GATE.md por topic.
"""
from __future__ import annotations

import re
from datetime import date
from pathlib import Path
from typing import Any

GREEN, YELLOW, RED = "verde", "amarillo", "rojo"

# métrica → (clave del umbral en video_length, motivo si falta)
CHECKS = {
    "datos": ("gate_datos", "pocas fuentes bajadas (pocos datos leídos de documentos)"),
    "citas_verificadas": ("gate_citas_verificadas", "sin testigos (pocas citas verificadas literal)"),
    "elegibles_humano": ("gate_elegibles", "sin humano que seguir (pocos testigos elegibles)"),
    "eventos_con_fecha": ("gate_eventos_fecha", "sin cronología (pocos eventos con fecha completa)"),
}


class PoolGateRed(RuntimeError):
    """El pool no alcanza para un video: el topic vuelve al inbox con `motivos`."""

    def __init__(self, gate: dict[str, Any]):
        self.gate = gate
        super().__init__("compuerta del pool en ROJO: " + "; ".join(gate["motivos"]))


def measure(pool: dict[str, Any]) -> dict[str, int]:
    return {
        "datos": len(pool.get("datos") or []),
        "citas_verificadas": sum(1 for q in pool.get("citas") or []
                                 if (q.get("verificacion") or {}).get("estado") == "verificada"),
        "elegibles_humano": sum(1 for p in pool.get("personajes") or [] if p.get("elegible_humano")),
        "eventos_con_fecha": sum(1 for c in pool.get("cronologia") or []
                                 if re.fullmatch(r"\d{4}-\d{2}-\d{2}", str(c.get("fecha") or ""))),
    }


def evaluate(pool: dict[str, Any]) -> dict[str, Any]:
    """{"color", "metricas", "umbrales", "faltan": [{metrica, valor, umbral, motivo}], "motivos", "target_words",
    "max_beats"}. Verde si todo llega al umbral; amarillo si todo llega a la mitad; rojo si no."""
    from script_engine.video_length import get
    m = measure(pool)
    half = get("gate_yellow_pct") / 100
    th = {k: get(key) for k, (key, _) in CHECKS.items()}
    below = [k for k in CHECKS if m[k] < th[k]]
    red = [k for k in CHECKS if m[k] < half * th[k]]
    color = RED if red else YELLOW if below else GREEN
    faltan = [{"metrica": k, "valor": m[k], "umbral": th[k], "motivo": CHECKS[k][1],
               "rojo": k in red} for k in below]
    return {"color": color, "metricas": m, "umbrales": th, "faltan": faltan,
            "motivos": [f["motivo"] for f in faltan if f["rojo"]] if red else [f["motivo"] for f in faltan],
            "target_words": get("gate_yellow_target_words") if color == YELLOW else get("target_words"),
            "max_beats": get("gate_yellow_max_beats") if color == YELLOW else None}


def report(gate: dict[str, Any], topic_id: str) -> str:
    icon = {GREEN: "🟢", YELLOW: "🟡", RED: "🔴"}[gate["color"]]
    L = [f"# POOL_GATE — `{topic_id}`", "", f"**{icon} {gate['color'].upper()}** · {date.today().isoformat()}", "",
         "| métrica | valor | umbral (verde) | mitad (amarillo) |", "|---|---|---|---|"]
    from script_engine.video_length import get
    half = get("gate_yellow_pct") / 100
    for k, v in gate["metricas"].items():
        t = gate["umbrales"][k]
        mark = "✔" if v >= t else ("~" if v >= half * t else "✖")
        L.append(f"| {k} | {v} {mark} | {t} | {half * t:g} |")
    L.append("")
    if gate["color"] == GREEN:
        L.append("Tubería normal: 12 min (≈ 1,500 palabras).")
    elif gate["color"] == YELLOW:
        L.append(f"**Aviso:** guion corto — `target_words` {gate['target_words']} (≈ 10 min) y escaleta de 7–"
                 f"{gate['max_beats']} beats. Falta: " + "; ".join(gate["motivos"]) + ".")
    else:
        L.append("**El topic vuelve al inbox** (no se gasta en guion ni imágenes). Motivo: " + "; ".join(gate["motivos"])
                 + ".")
    return "\n".join(L) + "\n"


def write_report(gate: dict[str, Any], topic_id: str, steps_dir: Path) -> Path:
    steps_dir.mkdir(parents=True, exist_ok=True)
    out = steps_dir / "POOL_GATE.md"
    out.write_text(report(gate, topic_id), encoding="utf-8")
    return out


def check(pool: dict[str, Any], topic_id: str, steps_dir: Path | None = None) -> dict[str, Any]:
    """Evalúa, escribe POOL_GATE.md (si hay `steps_dir`) y levanta PoolGateRed si es rojo. Devuelve el gate."""
    gate = evaluate(pool)
    if steps_dir is not None:
        write_report(gate, topic_id, steps_dir)
    if gate["color"] == RED:
        raise PoolGateRed(gate)
    return gate
