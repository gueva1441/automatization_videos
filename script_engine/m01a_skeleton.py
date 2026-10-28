"""
script_engine/m01a_skeleton.py — lo que queda del estructurador viejo (Módulo 01a).

F41 (DECISIONES 2026-10-27 20:59, una sola cadena): el estructurador (`generate_skeleton`, una llamada a Flash que
armaba el skeleton de 7 caps con bullets) se borró con la cadena vieja de fase1_5. Queda lo que usa la cadena única
(escaleta → guion v4 → partición):
  STEPS_DIR                       data/scripts/_steps (m01a_escaleta, m01d_particion, m01e_pantalla, m01a_columna, ficha_caso)
  CHAPTER_SCHEMA                  el contrato de 7 caps (rol, motor, duración) — m01a_escaleta, m01d_particion
  DEFAULT_INTENT_BY_CAP           narrative_intent por cap — m01a_escaleta, m01d_particion, tts_tags
  SCREEN_PER_CAP / SCREEN_MUST    ids del pool reservados para pantalla — m01a_escaleta
  canonize_figures, assign_screen_ids, finalize_pool_plan   cifras canónicas y reservados (m01a_escaleta)
"""

import re
from pathlib import Path

from config import DATA_DIR
from script_engine import evidence as ev


# ═══════════════════════════════════════════════════════════════
#  PATHS Y CONSTANTES
# ═══════════════════════════════════════════════════════════════

STEPS_DIR: Path = DATA_DIR / "scripts" / "_steps"

# Estructura fija del skeleton — NO se le pide a Flash que la decida. Duraciones desde config (HANDOFF_F7 §8.2:
# desarrollo 105 s, antes 75). Contrato de 7 caps intacto.
from script_engine.video_length import get as _len  # noqa: E402

CHAPTER_SCHEMA = [
    {"chapter_number": 1, "role": "hook",         "render_engine": "veo",  "duration_seconds": _len("hook_cap_seconds")},
    *[{"chapter_number": n, "role": "development", "render_engine": "flux", "duration_seconds": _len("dev_cap_seconds")}
      for n in range(2, 7)],
    {"chapter_number": 7, "role": "reveal_outro", "render_engine": "veo",  "duration_seconds": _len("outro_cap_seconds")},
]


# ═══════════════════════════════════════════════════════════════
#  NARRATIVE INTENT — defaults por cap (PR 2.A chat 24)
# ═══════════════════════════════════════════════════════════════

DEFAULT_INTENT_BY_CAP: dict[int, str] = {
    1: "hook",
    2: "setup",
    3: "rising_tension",
    4: "shock",
    5: "consequences",
    6: "resolution",
    7: "outro",
}


# ═══════════════════════════════════════════════════════════════
#  CIFRAS CANÓNICAS Y RESERVADOS PARA PANTALLA (F5d)
# ═══════════════════════════════════════════════════════════════

SCREEN_PER_CAP = 2                     # F5d: ids del pool reservados para pantalla, por cap (1–2)
SCREEN_MUST = (6, 7)                   # caps que tienen que tener al menos uno


def canonize_figures(sk: dict, pool: dict) -> list[str]:
    """F5d (in place): una sola cifra por conteo en todo el video. Las variantes de una cifra canónica (pool
    `cifras_canonicas`: «6,500 aprox.», «8,000 de medios», el rango) salen de los caps; la oficial entra en el
    primero que tenía una variante. El cap que trae la variante de MEDIOS es el de la contradicción: conserva la
    variante, suma la oficial y queda marcado (`contradiccion_cifras`) — ahí el narrador cuenta las dos."""
    notes: list[str] = []
    chs = sorted(sk.get("chapters") or [], key=lambda c: c["chapter_number"])
    its = ev.items(pool)
    for g in pool.get("cifras_canonicas") or []:
        # F23 §1.3: una variante con rango («entre 200 y 10.000») es un valor válido, no otra cifra del conteo
        var = {v["id"]: v for v in g["variantes"]
               if not ev.es_rango(ev.text_of(its.get(v["id"]) or {}) or str(v.get("valor") or ""))}
        contra = next((c for c in chs if any(var.get(i, {}).get("estatus") == "medios"
                                             for i in c.get("evidence_ids") or [])), None)
        placed = any(g["oficial"] in (c.get("evidence_ids") or []) for c in chs if c is not contra)
        for c in chs:
            ids = c.get("evidence_ids") or []
            if c is contra:
                if g["oficial"] not in ids:
                    ids.append(g["oficial"])
                c.setdefault("contradiccion_cifras", []).append(g["oficial"])
                notes.append(f"cap {c['chapter_number']}: contradicción {g['valor']} (oficial) vs "
                             f"{[var[i]['valor'] for i in ids if i in var]}")
                continue
            gone = [i for i in ids if i in var]
            if not gone:
                continue
            k = ids.index(gone[0])
            ids = [i for i in ids if i not in var]
            if not placed and g["oficial"] not in ids:
                ids.insert(k, g["oficial"])
                placed = True
            c["evidence_ids"] = ids
            notes.append(f"cap {c['chapter_number']}: cifra canónica {g['valor']} en vez de "
                         f"{[var[i]['valor'] for i in gone]}")
    return notes


def assign_screen_ids(sk: dict, pool: dict) -> list[str]:
    """F5d (in place): por cap, 1–2 ids del pool RESERVADOS PARA PANTALLA (`pantalla_ids`): datos que el narrador no
    dice y el director muestra con prioridad. Son datos duros que nadie narra, con fuente, cifra precisa, fecha
    completa o una cita corta, que tienen un recorte posible (cláusula completa + kicker) y no cuentan el mismo
    hecho que algo narrado. Van al cap con el que más se relacionan (palabras en común; +2 si la fecha cae en el
    rango del cap). Los caps 6 y 7 reciben al menos uno."""
    from script_engine.gfx_pool import _kicker, pool_clause_options
    its = ev.items(pool)
    chs = sorted(sk.get("chapters") or [], key=lambda c: c["chapter_number"])
    narrated = {i for c in chs for i in c.get("evidence_ids") or []}
    narrated |= {v["id"] for g in pool.get("cifras_canonicas") or [] for v in g["variantes"]}

    def _worthy(it: dict) -> bool:
        txt = ev.text_of(it)
        if it["_kind"] == "citas":
            return len(txt.split()) <= 12
        return bool(it.get("fuente") or (it.get("tipo") in ("cifra", "magnitud") and re.search(r"\d", txt))
                    or ev.item_date(it))
    cands = []
    for i, it in its.items():
        if i in narrated or it["_kind"] not in ("datos", "cronologia", "citas") or not ev.is_hard(it) or not _worthy(it):
            continue
        if any(ev.same_fact(it, its[j]) for j in narrated if j in its):
            continue
        # el mismo día y el mismo asunto que algo narrado (≥ 2 palabras en común): ya lo cuenta la voz en algún cap
        d = ev.item_date(it)
        if d and any(ev.item_date(its[j]) == d and len(ev._content(ev.text_of(it)) & ev._content(ev.text_of(its[j]))) >= 2
                     for j in narrated if j in its):
            continue
        txt = ev.text_of(it)
        if not any(_kicker(it, o) for o in pool_clause_options(txt)) and it["_kind"] != "citas":
            continue
        cands.append(i)

    def _score(i: str, c: dict) -> int:
        """Relación dato ↔ cap; −1 = no puede ir (su fecha es posterior a todo lo que narra el cap: S2 lo
        bloquearía en pantalla)."""
        own = [its[j] for j in c.get("evidence_ids") or [] if j in its]
        words = set().union(*(ev._content(ev.text_of(x)) for x in own)) if own else set()
        sc = len(ev._content(ev.text_of(its[i])) & words)
        # el rango del cap sale de sus eventos y fechas (no de la fecha suelta de una cifra)
        dates = sorted(d for d in (ev.item_date(x) for x in own
                                   if x["_kind"] == "cronologia" or x.get("tipo") == "fecha") if d)
        d = ev.item_date(its[i])
        if d and dates and d > dates[-1]:
            return -1
        if d and dates and dates[0] <= d:
            sc += 2
        return sc
    for c in chs:
        c["pantalla_ids"] = []
    # cada dato al cap con el que más se relaciona (empate: el cap más temprano, donde ocurre); primero los datos
    # más relacionados
    best = {i: max(chs, key=lambda c: (_score(i, c), -c["chapter_number"])) for i in cands}
    for i in sorted(cands, key=lambda i: (-_score(i, best[i]), i)):
        c = best[i]
        if _score(i, c) >= 2 and len(c["pantalla_ids"]) < SCREEN_PER_CAP:
            c["pantalla_ids"].append(i)
    for c in chs:                                      # los caps 6 y 7 tienen al menos uno
        if c["chapter_number"] in SCREEN_MUST and not c["pantalla_ids"]:
            used = {j for x in chs for j in x["pantalla_ids"]}
            # los caps del final: primero lo más reciente (es lo que cuentan), después lo más relacionado
            late = lambda i: (ev.item_date(its[i]) or "", _score(i, c), i)  # noqa: E731
            free = sorted((i for i in cands if i not in used and _score(i, c) >= 0), key=late, reverse=True)
            if free:
                c["pantalla_ids"].append(free[0])
            # F23 §1.2: sin libres, ese cap no tiene pantalla (antes se le «robaba» uno a un cap con 2)
    return [f"cap {c['chapter_number']}: pantalla {c['pantalla_ids']}" for c in chs if c["pantalla_ids"]]


def finalize_pool_plan(sk: dict, pool: dict | None) -> None:
    """F5d: cifras canónicas y datos reservados para pantalla sobre el skeleton (in place, anotado en `_pool_plan`)."""
    if not pool:
        return
    sk["_pool_plan"] = {"cifras_canonicas": canonize_figures(sk, pool), "pantalla": assign_screen_ids(sk, pool)}


