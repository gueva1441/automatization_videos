"""
researcher_steps/pool_gate.py — F7d (HANDOFF_F7 §9.2): compuerta del pool, el semáforo entre research y guion.

Puntaje determinista sobre el evidence_pool de research v3, antes de escaleta, guion e imágenes.
F23 §1.2 (los umbrales de Orleans pasan a medida):
    rojo      solo si no hay con qué contar: datos < 40 · personas con nombre < 2 · eventos con fecha < 3 → el topic
              vuelve al inbox con el motivo
    amarillo  alguna de las cuatro medidas de siempre (datos 150 · citas verificadas 8 · elegibles 2 · eventos con fecha
              10) por debajo de su umbral: se muestran todas con su valor. Ya NO acorta el video (12 min, 7–14 beats)
    verde     las cuatro por encima
F23 §1.1: un evento cuenta «con fecha» si la tiene de mes o de día (AAAA-MM o AAAA-MM-DD); de año solo (AAAA), si el
caso es `prolongado` (`pool["_tiempo"]`, o el perfil cargado en research_v3).
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
    "eventos_con_fecha": ("gate_eventos_fecha", "sin cronología (pocos eventos con fecha)"),
}
# F23 §1.2: métrica → (clave del piso rojo, motivo)
ROJO = {
    "datos": ("gate_rojo_datos", "no hay con qué contar: casi no hay datos leídos de documentos"),
    "personas_con_nombre": ("gate_rojo_personas", "no hay con qué contar: menos de dos personas con nombre"),
    "eventos_con_fecha": ("gate_rojo_eventos", "no hay con qué contar: casi no hay eventos con fecha"),
}


def _tipo_evento(pool: dict[str, Any]) -> str | None:
    t = (pool.get("_tiempo") or {}).get("tipo_evento")
    if t:
        return t
    from researcher_steps.research_v3 import caso
    return caso().get("tipo_evento")


def con_fecha(fecha: Any, tipo_evento: str | None) -> bool:
    """F23 §1.1: fecha de mes o de día; de año solo, si el caso es prolongado."""
    f = str(fecha or "")
    return bool(re.fullmatch(r"\d{4}-\d{2}(-\d{2})?", f) or (tipo_evento == "prolongado" and re.fullmatch(r"\d{4}", f)))


class PoolGateRed(RuntimeError):
    """El pool no alcanza para un video: el topic vuelve al inbox con `motivos`."""

    def __init__(self, gate: dict[str, Any]):
        self.gate = gate
        super().__init__("compuerta del pool en ROJO: " + "; ".join(gate["motivos"]))


def measure(pool: dict[str, Any]) -> dict[str, int]:
    from script_engine import nombres
    tipo = _tipo_evento(pool)
    return {
        "datos": len(pool.get("datos") or []),
        "citas_verificadas": sum(1 for q in pool.get("citas") or []
                                 if (q.get("verificacion") or {}).get("estado") == "verificada"),
        "elegibles_humano": sum(1 for p in pool.get("personajes") or [] if p.get("elegible_humano")),
        "eventos_con_fecha": sum(1 for c in pool.get("cronologia") or [] if con_fecha(c.get("fecha"), tipo)),
        "personas_con_nombre": sum(1 for p in pool.get("personajes") or []
                                   if nombres.es_persona(p.get("nombre") or "", mononimo_ok=True)),
    }


def evaluate(pool: dict[str, Any]) -> dict[str, Any]:
    """{"color", "metricas", "umbrales", "pisos_rojo", "faltan": [{metrica, valor, umbral, motivo}], "motivos",
    "target_words", "max_beats"}. F23 §1.2: rojo si falta con qué contar (pisos de `ROJO`); amarillo si alguna de las
    cuatro medidas está bajo su umbral; verde si no. `target_words` es siempre el de siempre y `max_beats` None (el
    amarillo ya no acorta)."""
    from script_engine.video_length import get
    m = measure(pool)
    th = {k: get(key) for k, (key, _) in CHECKS.items()}
    pisos = {k: get(key) for k, (key, _) in ROJO.items()}
    below = [k for k in CHECKS if m[k] < th[k]]
    red = [k for k in ROJO if m[k] < pisos[k]]
    color = RED if red else YELLOW if below else GREEN
    faltan = [{"metrica": k, "valor": m[k], "umbral": th[k], "motivo": CHECKS[k][1], "rojo": False} for k in below]
    faltan += [{"metrica": k, "valor": m[k], "umbral": pisos[k], "motivo": ROJO[k][1], "rojo": True} for k in red]
    return {"color": color, "metricas": m, "umbrales": th, "pisos_rojo": pisos, "faltan": faltan,
            "motivos": [f["motivo"] for f in faltan if f["rojo"]] if red else [f["motivo"] for f in faltan],
            "target_words": get("target_words"), "max_beats": None}


def report(gate: dict[str, Any], topic_id: str) -> str:
    icon = {GREEN: "🟢", YELLOW: "🟡", RED: "🔴"}[gate["color"]]
    L = [f"# POOL_GATE — `{topic_id}`", "", f"**{icon} {gate['color'].upper()}** · {date.today().isoformat()}", "",
         "| métrica | valor | umbral (verde) | piso (rojo) |", "|---|---|---|---|"]
    pisos = gate.get("pisos_rojo") or {}
    for k, v in gate["metricas"].items():
        t = gate["umbrales"].get(k)
        r = pisos.get(k)
        mark = "✖" if r is not None and v < r else ("✔" if t is None or v >= t else "~")
        L.append(f"| {k} | {v} {mark} | {t if t is not None else '—'} | {r if r is not None else '—'} |")
    L.append("")
    if gate["color"] == GREEN:
        L.append("Tubería normal: 12 min (≈ 1,500 palabras).")
    elif gate["color"] == YELLOW:
        L.append("**Aviso** (el video no se acorta: 12 min, escaleta de 7–14 beats). Bajo su umbral: "
                 + "; ".join(gate["motivos"]) + ".")
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
