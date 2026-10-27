"""
script_engine/clima.py — F36 §A: los sellos de clima (movido de gfx_rotulista; `peak_word` viene de gfx_peak). F36 §C:
la palabra y la oración vienen del guion en papel (`sellos_del_papel`); acá se pone el instante (la palabra de más peso
de la oración o su inicio), el crítico «¿estorba?» antes del reparto y «nunca al mismo tiempo». F36 §D: se borró el
camino de Gemini Flash (`sellos_por_tema`, `SELLO_CLIMA_PROMPT`).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any, Callable


# ═══════════════════════ sellos de clima (F32 §B.6 → F34 §A.4) ═══════════════════════

# el catálogo de Omar (25-10: muerte, agua, veneno…) = los moods del perfil; la tabla da el nombre del tema de cada uno
TEMA_DE_MOOD = {"muerte": "muerte", "agua": "agua", "veneno_enfermedad": "veneno", "fuego": "fuego",
                "oscuridad_encierro": "oscuridad", "radiacion_quimico": "radiación", "frio_abandono": "abandono",
                "silencio": "silencio", "caos_gritos": "caos"}


def vocabulario_clima() -> list[str]:
    """`sellos_clima` del perfil activo (DECISIONES 2026-10-26 14:22); sin la clave, lista vacía (= sin sellos)."""
    from gfx_config import ACTIVE_PROFILE
    return [str(w).strip().upper() for w in ACTIVE_PROFILE.get("sellos_clima") or [] if str(w).strip()]


def sellos_del_papel(plan: dict[str, Any], scenes: list[Any], ent: dict[str, Any], words: list[dict],
                     time_offset: float, moods: dict[str, dict], log: list[str], sellos: list[dict[str, Any]], *,
                     juez: Callable[[dict], dict] | None = None, usadas_video: set[str] | None = None
                     ) -> list[dict[str, Any]]:
    """F36 §C.4 (aclaración 5): los sellos vienen del guion en papel (m01e_pantalla): la palabra y la oración (ya
    alineada con la voz). El instante dentro de la oración lo pone este módulo como siempre: la palabra de más peso de
    un mood (peak_word) o, si no hay, el inicio de la oración. Después lo mecánico: la palabra es del vocabulario, no
    salió antes en el video, no cruza el corte de su escena; el crítico («¿estorba?», B.2) antes del reparto; y el
    reparto: nunca al mismo tiempo que otro bloque (title card, texto, reloj, otro sello: no se solapan ni se tocan,
    DECISIONES 17:58). «Uno por beat» ya lo decidió el papel. F36 §D: no hay otros sellos (ni del director ni de la
    palabra del pico) ni sfx propio del sello. Corre después de escena_final."""
    from gfx_config import gfx_rules
    from script_engine.gfx_peak import sentences
    from script_engine.gfx_project import scene_at
    from script_engine.rotulista_colocar import choca
    filas: list[dict[str, Any]] = []
    plan["emphasis"] = []
    if not scenes:
        return filas
    lista = vocabulario_clima()
    sents = sentences(words, time_offset)
    dur = round(float(gfx_rules.mood_dur), 3)
    iv: list[tuple[float, float, str]] = []
    if plan.get("title_card"):
        iv.append((0.0, float(gfx_rules.title_dur), "title card"))
    for campo, que in (("callouts", "ficha"), ("archive_clippings", "recorte")):
        for b in plan.get(campo) or []:
            iv.append((float(b["start"]), float(b["start"]) + float(b.get("duration") or 0.0), que))
    for campo, que in (("quote_card", "cita"), ("time_ticker", "reloj")):
        b = plan.get(campo)
        if b and "start" in b:
            iv.append((float(b["start"]), float(b["start"]) + float(b.get("duration") or 0.0), que))
    antes = set(usadas_video or ())
    criticos: list[dict[str, Any]] = []
    for sp in sorted(sellos, key=lambda x: (x.get("sentence_idx") is None, x.get("sentence_idx") or 0)):
        k, palabra = sp.get("sentence_idx"), str(sp.get("palabra") or "")
        if k is None or not 0 <= int(k) < len(sents):
            filas.append({"bloque": "emphasis", "texto": palabra, "t": None, "accion": "fuera", "regla": "tema",
                          "quien": "papel", "motivo": f"sello del papel «{palabra}»: sin oración de la voz", "papel": True})
            continue
        s = sents[int(k)]
        h = peak_word(s, words, moods)
        # aclaración 5: el instante = la palabra de más peso de la oración o el inicio de la oración; se prueba en ese
        # orden y queda el primero que no cruza el corte de su escena (lectura declarada, F36_REPORT)
        momentos = list(dict.fromkeys(([round(float(words[h["i"]]["start"]) + time_offset, 3)] if h else [])
                                      + [round(float(s["t0"]), 3)]))
        t = next((x for x in momentos if x + dur <= scene_at(scenes, x).end + 1e-6), momentos[0])
        sc = scene_at(scenes, t)
        quien, regla = "catálogo", "tema"
        motivo = (f"«{palabra}» no está en el vocabulario sellos_clima" if palabra not in lista else
                  f"«{palabra}» ya salió en el video" if palabra in antes else
                  f"cruza el corte de la escena {sc.idx} ({sc.end:.2f} s) en la palabra de más peso y en el inicio de "
                  f"la oración" if t + dur > sc.end + 1e-6 else None)
        if h and t != momentos[0]:
            h = None                                   # arranca con la oración: no hay palabra de la voz debajo
        m = (moods.get(str(h["category"])) or {}) if h else {}
        base = {"category": h["category"] if h else None, "layer": m.get("layer"), "icon_anim": m.get("icon_anim") or "stamp",
                "side": getattr(sc, "quiet_side", "right") or "right", "stamp": gfx_rules.emphasis_stamp,
                "weight": h["weight"] if h else 0,
                "word": palabra, "start": t, "duration": dur, "por_tema": True, "clima": True, "papel": True,
                "tema": TEMA_DE_MOOD.get(str(h["category"]), h["category"]) if h else None,
                "palabra_voz": re.sub(r"^[¿¡\"'«“(]+|[.,;:!?…\"'»”)]+$", "", str(words[h["i"]]["word"]).strip()) if h else None,
                "sentence_idx": int(k), **({"sin_alinear": sp["sin_alinear"]} if sp.get("sin_alinear") else {}),
                **({"editado": True} if sp.get("editado") else {})}
        if motivo is None and juez is not None:                   # §B.2: el crítico, antes del reparto
            row = juez(base)
            criticos.append(row)
            if not row["pasa"]:
                quien, regla = "crítico", "crítico"
                motivo = f"«{palabra}» estorba: {row['motivo']} (mira {row['mira']})"
        if motivo is None:
            hay = choca(iv, t, t + dur)
            motivo = f"se solapa con {', '.join(sorted(set(hay)))}" if hay else None
        if motivo:
            filas.append({"bloque": "emphasis", "texto": palabra, "t": t, "accion": "fuera", "regla": regla,
                          "quien": quien, "motivo": f"sello del papel «{palabra}»: {motivo}", "papel": True})
            continue
        plan["emphasis"].append(base)
        iv.append((t, t + dur, "sello"))
        antes.add(palabra)
    plan["critico_sellos"] = criticos
    plan["emphasis"].sort(key=lambda e: e["start"])
    plan["sellos_tema"] = filas
    log.append(f"  sellos del papel: {[(e['word'], round(e['start'], 1)) for e in plan['emphasis']]} · "
               f"fuera {[(f['texto'], f['motivo']) for f in filas]}")
    return filas


# ═══════════════════════ palabra del momento (gfx_peak.peak_word, F36 §A) ═══════════════════════

def peak_word(peak: dict[str, Any], words: list[dict], moods: dict[str, dict], *, block_category: str | None = None,
              freq: dict[str, int] | None = None) -> dict[str, Any] | None:
    """F4c R3: la palabra de mayor peso (≥ 2) de la frase pico. Empate: la de una categoría que el bloque grande no
    muestra ya (nivel de agua → no otra de agua), después la más rara del video, después la primera."""
    from script_engine.gfx_peak import lexicon_hits, prefer_icon_nouns
    f = freq or {}
    hits = [h for h in prefer_icon_nouns(lexicon_hits(words, moods, peak["idx"]), moods) if h["weight"] >= 2]
    if not hits:
        return None
    return max(hits, key=lambda h: (h["weight"], h["category"] != block_category, -f.get(h["word"], 0), -h["i"]))


def usadas_antes(work_dir: Path, cap_number: int) -> set[str]:
    """F36 §B.3: las palabras de los sellos de clima de los caps anteriores (sus planes resueltos en el work_dir: el
    plan corre en fila, ch01 → ch07)."""
    out: set[str] = set()
    for f in sorted(Path(work_dir).glob("gfx_plan_ch*.resolved.json")):
        m = re.fullmatch(r"gfx_plan_ch(\d+)\.resolved\.json", f.name)
        if not m or int(m.group(1)) >= cap_number:
            continue
        try:
            plan = json.loads(f.read_text(encoding="utf-8")).get("plan") or {}
        except (OSError, ValueError):
            continue
        out |= {str(e.get("word")) for e in plan.get("emphasis") or [] if e.get("clima") and e.get("word")}
    return out
