"""
gfx_style.py — El director aplica la IDENTIDAD del canal (F4 §2, HANDOFF_F4 §1.1–§1.2).

La identidad que Omar armó en el lab (perfil `identity` + plan dorado) define las FORMAS; este módulo las aplica
de forma determinista en cada cap. El LLM nunca elige formas: solo dónde y qué (gfx_director). Todo lo de acá se
prende con el token `identity_rules` del perfil (misterio: true; el motor y otros canales: false = F3 tal cual).

    movement_for()       forma de movimiento de una foto: acercar por defecto, alejar en apertura/cierre del cap,
                         3D en paisajes, paneo en planos anchos con gente, quieta solo con texto en la imagen
    plan_movements()     aplica esas formas a las escenas (movimiento seguro sobre el PNG; 3D = clip DepthFlow)
    identity_transitions() transición de entrada por escena: fundido cruzado 20 f por default; corte en ritmo
                         rápido y cuando la foto siguiente es del mismo lugar; ≥ 1 corte cada 3; flash solo en
                         impacto (R1, tope del perfil); 1 fundido a negro por cap; corte después del zoom
    select_punches()     golpes de zoom: máx punch_max_identity (4), uno por frase, nunca a ±5 s del pico,
                         elegidos por peso de la palabra
    golden_fewshot()     el plan dorado resumido (t · palabra · elemento · variante) para el prompt del director
    identity_violations() chequeo duro del plan final (cantidades, alternancia, pico) → lista de violaciones
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from gfx_config import GFX_PROFILES_DIR, active_moods, gfx_rules

PEAK_CLEAR_SEC = 5.0

_PERSON = re.compile(r"\b(man|woman|boy|girl|child|person|face|hands?|individuals?|people|prisoners?|inmates?)\b", re.I)
_CROWD = re.compile(r"\b(crowd|crowded|mass of|street|row|line of)\b", re.I)
_PLACE = re.compile(r"\b(complex|tower|building|prison|cityscape|city|coast|landscape|sky|hurricane|cloud)\b", re.I)
_STOP = {"a", "an", "the", "of", "in", "on", "at", "with", "and", "or", "to", "from", "by", "for", "its", "their"}


def suggest_movement(prompt: dict[str, Any], *, already_out: bool) -> tuple[str, str]:
    """Hint del catálogo (F3 §2 A) aplicado al prompt de la foto → (forma, motivo en ≤ 5 palabras)."""
    tii = prompt.get("text_in_image")
    if isinstance(tii, dict) and tii.get("present"):
        return "quieta", "tiene texto: no moverlo"
    shot = str(prompt.get("shot_scale", "")).lower()
    subj = " ".join(str(prompt.get(k, "")) for k in ("subject", "setting", "prompt"))[:600]
    wide = "wide" in shot
    if _CROWD.search(subj) and wide:
        return "paneo", "foto ancha con gente"
    if _PERSON.search(str(prompt.get("subject", ""))) and not wide:
        return "acercar", "hay una persona"
    if "detail" in shot or "close" in shot:
        return "acercar", "es un detalle"
    if wide and _PLACE.search(subj):
        return ("3D", "paisaje con profundidad") if already_out else ("alejar", "revela el lugar")
    return "acercar", "base del documental"


def movement_for(prompt: dict[str, Any], idx: int, n: int) -> tuple[str, str]:
    """Identidad §1.1: acercar por defecto; alejar en apertura y cierre del cap; 3D en paisajes; paneo en planos
    anchos con gente; nunca quieta salvo documentos (texto en la imagen)."""
    tii = prompt.get("text_in_image")
    if isinstance(tii, dict) and tii.get("present"):
        return "quieta", "documento: tiene texto"
    forma, motivo = suggest_movement(prompt, already_out=True)        # alejar solo por posición (abajo)
    if forma == "3D":
        return forma, motivo
    if idx == 0 or (n > 2 and idx == n - 1):
        return "alejar", "apertura del cap" if idx == 0 else "cierre del cap"
    return forma, motivo


MOV_SAFE = {"acercar": "push", "alejar": "pull", "paneo": "pan", "quieta": "static", "3D": None}


def prompt_for_asset(asset: Path, prompts: list[dict[str, Any]], fallback_idx: int) -> dict[str, Any]:
    """ch02_img_03 → image_prompts[2] (mismo mapeo que fase2b._route_safe)."""
    m = re.search(r"_img_(\d+)$", Path(asset).stem)
    k = int(m.group(1)) - 1 if m else fallback_idx
    return prompts[k] if 0 <= k < len(prompts) and isinstance(prompts[k], dict) else {}


def plan_movements(scenes: list[Any], chplan: Any, prompts: list[dict[str, Any]], log: list[str] | None = None
                   ) -> list[dict[str, Any]]:
    """Forma por escena; las que no son 3D van con movimiento seguro sobre el PNG (el clip DepthFlow queda tapado).
    Una escena que el router ya marcó de riesgo (o caída a Ken Burns) conserva el movimiento del router: la
    identidad nunca vuelve a mostrar un clip 3D que se deforma. Solo motor flux (fotos); Veo/híbrido no se tocan."""
    out: list[dict[str, Any]] = []
    if getattr(chplan, "engine", "") != "flux" or not getattr(chplan, "asset_paths", None):
        return out
    n = len(scenes)
    for s in scenes:
        if s.idx >= len(chplan.asset_paths):
            continue
        asset = Path(chplan.asset_paths[s.idx])
        forma, motivo = movement_for(prompt_for_asset(asset, prompts, s.idx), s.idx, n)
        if s.safe and s.safe.get("risk") not in (None, "identity"):
            out.append({"scene": s.idx, "forma": "router", "motivo": f"riesgo {s.safe.get('risk')}: {s.safe.get('movement')}"})
            continue
        mv = MOV_SAFE[forma]
        if mv and asset.exists():
            s.safe = {"image": str(asset), "movement": mv, "risk": "identity"}
        out.append({"scene": s.idx, "forma": forma, "motivo": motivo})
    if log is not None:
        log.append("  identidad: movimiento " + ", ".join(f"{m['scene']}:{m['forma']}" for m in out))
    return out


def _setting_tokens(p: dict[str, Any]) -> set[str]:
    txt = " ".join(str(p.get(k, "")) for k in ("setting", "location"))
    return {w for w in re.findall(r"[a-z]+", txt.lower()) if len(w) > 2 and w not in _STOP}


def same_place(a: dict[str, Any], b: dict[str, Any]) -> bool:
    """La foto siguiente es del mismo lugar (setting casi igual) → corte obligatorio (evita «slideshow»)."""
    ta, tb = _setting_tokens(a), _setting_tokens(b)
    return bool(ta and tb) and len(ta & tb) / len(ta | tb) >= 0.6


def identity_transitions(scenes: list[Any], prompts_by_scene: list[dict[str, Any]] | None = None,
                         zoom_scene_idx: int | None = None) -> dict[int, dict[str, Any]]:
    """Transición de ENTRADA por escena con la identidad (clave = idx de la escena entrante)."""
    r = gfx_rules
    xf = int(r.crossfade_frames)
    prompts_by_scene = prompts_by_scene or []
    out: dict[int, dict[str, Any]] = {}
    flashes: list[float] = []
    dips = 0
    since_cut = 0                                    # transiciones seguidas sin corte
    for s in scenes[1:]:
        prev = scenes[s.idx - 1] if s.idx - 1 < len(scenes) else None
        pa = prompts_by_scene[s.idx - 1] if s.idx - 1 < len(prompts_by_scene) else {}
        pb = prompts_by_scene[s.idx] if s.idx < len(prompts_by_scene) else {}
        fast = min(s.duration, prev.duration if prev else 99) < r.fast_cut_sec
        if zoom_scene_idx is not None and s.idx == zoom_scene_idx + 1:
            tr = {"kind": "cut", "frames": 0, "why": "después del zoom"}
        elif s.rank == "R1" and len(flashes) < r.flash_max_per_cap and all(
                s.start - f >= r.flash_min_gap_sec for f in flashes):
            flashes.append(s.start)
            tr = {"kind": "flash", "frames": r.transition_frames.get("R1", 3), "why": "impacto"}
        elif s.rank == "R1":
            tr = {"kind": "cut_punch", "frames": 0, "why": "impacto sin flash disponible"}
        elif same_place(pa, pb):
            tr = {"kind": "cut", "frames": 0, "why": "mismo lugar"}
        elif fast:
            tr = {"kind": "cut", "frames": 0, "why": "ritmo rápido"}
        elif since_cut >= 2:
            tr = {"kind": "cut", "frames": 0, "why": "≥ 1 corte cada 3"}
        elif dips < r.dip_max_per_cap and s.rank == "R3" and s.start >= r.dip_min_t:
            dips += 1
            tr = {"kind": "dip", "frames": r.dip_frames, "why": "fundido a negro (1 por cap)"}
        else:
            tr = {"kind": "dissolve", "frames": xf, "why": "default"}
        since_cut = 0 if tr["kind"] in ("cut", "cut_punch", "flash") else since_cut + 1
        out[s.idx] = {**tr, "rank": s.rank}
    return out


ZOOM_PUNCH_SCALE = 1.4        # transition_config «zoom_punch»: 1.0→1.4 saliente / 1.4→1.0 entrante
ZOOM_PUNCH_MS = 400           # ídem, duration_ms


def transiciones_por_relato(scenes: list[Any], plan: dict[str, Any], beats: list[dict[str, Any]],
                            fps: int = 30) -> dict[int, dict[str, Any]]:
    """F30b §A: la transición de ENTRADA de cada escena por el relato (clave = idx de la escena entrante); el
    emotional_rank no decide nada. Por cada corte, la primera que aplica:
        1. la escena saliente tuvo lupa (evidence_zoom en ella)              → cut       «después de la lupa»
        2. el corte más cercano a pico.t dentro del beat pico (uno por cap)   → zoom_punch «pico»
        3. la escena entrante es de otro beat que la saliente                → dissolve  «cambio de beat»
        4. arranca el reloj (time_ticker) en la escena entrante               → dissolve  «salto de tiempo»
        5. la última escena del cap (la de la pregunta de cierre)             → dip       «cierre»
        6. todo lo demás                                                      → cut       «corte»
    Corre sobre el plan final (después del crítico): una lupa que el crítico sacó no deja su corte."""
    r = gfx_rules
    out: dict[int, dict[str, Any]] = {}
    if len(scenes) < 2:
        return out
    lupa = (plan.get("evidence_zoom") or {}).get("scene_idx")
    pk = plan.get("pico") or {}
    bpk = next((b for b in beats if b["n"] == pk.get("beat")), None)
    punch = None
    if bpk is not None and pk.get("t") is not None:
        en_pico = [s for s in scenes[1:] if bpk["t0"] - 0.3 <= s.start <= bpk["t1"]]
        if en_pico:
            punch = min(en_pico, key=lambda s: (abs(s.start - float(pk["t"])), s.idx)).idx

    def beat_de(t: float) -> int | None:
        for b in beats:
            if b["t0"] - 0.3 <= t <= b["t1"]:
                return b["n"]
        prev = [b for b in beats if b["t0"] <= t]
        return (prev[-1] if prev else beats[0])["n"] if beats else None
    tk = plan.get("time_ticker")
    tk_t = float(tk["start"]) if tk else None
    for s in scenes[1:]:
        prev = scenes[s.idx - 1]
        if lupa is not None and s.idx == lupa + 1:
            tr = {"kind": "cut", "frames": 0, "why": "después de la lupa"}
        elif s.idx == punch:
            tr = {"kind": "zoom_punch", "frames": round(ZOOM_PUNCH_MS / 1000 * fps), "why": "pico"}
        elif beats and beat_de(s.start) != beat_de(prev.start):
            tr = {"kind": "dissolve", "frames": int(r.crossfade_frames), "why": "cambio de beat"}
        elif tk_t is not None and s.start - 1e-6 <= tk_t < s.end:
            tr = {"kind": "dissolve", "frames": int(r.crossfade_frames), "why": "salto de tiempo"}
        elif s.idx == scenes[-1].idx:
            tr = {"kind": "dip", "frames": int(r.dip_frames), "why": "cierre"}
        else:
            tr = {"kind": "cut", "frames": 0, "why": "corte"}
        out[s.idx] = {**tr, "rank": s.rank}
    return out


def _word_weight(word: str, moods: dict[str, dict[str, Any]]) -> int:
    w = re.sub(r"[^\wáéíóúñü]", "", str(word).lower())
    return max((int((m.get("triggers") or {}).get(w, 0)) for m in moods.values()), default=0)


def _sentence_of(t: float, words: list[dict], time_offset: float) -> int:
    sid, best = 0, 0
    for w in words:
        if float(w["start"]) + time_offset <= t + 1e-6:
            best = sid
        if re.search(r"[.!?…]['\"»”)]*$", str(w.get("word", "")).strip()):
            sid += 1
    return best


def select_punches(plan: dict[str, Any], words: list[dict], *, time_offset: float = 0.0,
                   moods: dict[str, dict[str, Any]] | None = None, log: list[str] | None = None) -> list[float]:
    """Golpes de zoom de la identidad (§1.2.1): candidatos = los del plan (LLM + relleno) + palabras del léxico de
    peso ≥ 2 + disparadores de datos; puntaje = peso de la palabra (+2 dato, +1 propuesto por el director);
    máx punch_max_identity, uno por frase, nunca a ±5 s del pico. Devuelve los instantes elegidos (ordenados)."""
    moods = moods if moods is not None else active_moods()
    peak_t = (plan.get("pico") or {}).get("t")
    cands: dict[float, float] = {}

    def add(t: float, score: float) -> None:
        t = round(float(t), 3)
        cands[t] = max(cands.get(t, 0.0), score)

    def weight_at(t: float) -> int:
        w = min(words, key=lambda x: abs(float(x["start"]) + time_offset - t), default=None)
        return _word_weight(w["word"], moods) if w else 0

    for t in plan.get("punch_in", []) or []:
        add(t, weight_at(t) + 1)
    for w in words:
        wt = _word_weight(w["word"], moods)
        if wt >= 2:
            add(float(w["start"]) + time_offset, wt)
    for c in plan.get("callouts", []) or []:
        add(c["start"], weight_at(c["start"]) + 2)
    chosen: list[float] = []
    used_sent: set[int] = set()
    busy = [(e["start"], e["start"] + 1.0) for e in plan.get("emphasis") or []]  # el sello rojo ya golpea
    for t, sc in sorted(cands.items(), key=lambda kv: (-kv[1], kv[0])):
        if len(chosen) >= gfx_rules.punch_max_identity:
            break
        if peak_t is not None and abs(t - float(peak_t)) <= PEAK_CLEAR_SEC:
            continue
        if t < gfx_rules.title_dur:                      # el título ya abre el cap
            continue
        sid = _sentence_of(t, words, time_offset)
        if sid in used_sent:
            continue
        if any(a - 0.05 <= t < b for a, b in busy) and sc < 3:
            continue
        used_sent.add(sid)
        chosen.append(t)
    chosen.sort()
    if log is not None:
        log.append(f"  identidad: golpes de zoom {len(chosen)} (de {len(cands)} candidatos) @ {chosen}")
    return chosen


_ELEM = {"title_card": "título", "callouts": "dato", "archive_clippings": "recorte", "evidence_zoom": "zoom de detalle",
         "count_up": "contador", "emphasis": "mood + sello", "icon_array": "matriz de figuras", "water_level": "nivel de agua",
         "time_ticker": "reloj", "chapter_question": "pregunta de cierre", "icons": "ícono"}


def golden_fewshot(profile: dict[str, Any] | None = None, max_rows: int = 24) -> str:
    """Plan dorado del perfil resumido (t · elemento · qué) para el prompt del director. "" si no hay."""
    if profile is None:
        from gfx_config import ACTIVE_PROFILE as profile
    name = ((profile or {}).get("identity") or {}).get("golden_plan")
    if not name:
        return ""
    try:
        g = json.loads((GFX_PROFILES_DIR / name).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    p = g.get("plan") or {}
    rows: list[tuple[float, str, str]] = []
    if p.get("title_card"):
        rows.append((0.0, "título", f"{p['title_card'].get('kicker', '')} · {p['title_card'].get('title', '')}"))
    for c in p.get("callouts") or []:
        rows.append((c["start"], "dato", f"«{c['text']}» ({c.get('kind', '')})"))
    for a in p.get("archive_clippings") or []:
        rows.append((a["start"], "recorte", f"«{a['headline']}»" + (" con ícono" if a.get("icon") else "")))
    if p.get("evidence_zoom"):
        ez = p["evidence_zoom"]
        rows.append((ez.get("start", 0.0), "zoom de detalle", f"«{ez.get('word') or ez.get('anchor', '')}»"))
    for e in p.get("emphasis") or []:
        rows.append((e["start"], "mood + sello", f"«{e.get('word', '')}» ({e.get('layer', '')})"
                     + (f" + ícono {e['icon']}" if e.get("icon") else "")))
    for t in p.get("punch_in") or []:
        rows.append((float(t), "golpe de zoom", "suave"))
    if p.get("water_level"):
        rows.append((p["water_level"]["start"], "nivel de agua", f"{p['water_level'].get('value_text')} {p['water_level'].get('unit', '')}"))
    if p.get("chapter_question"):
        rows.append((p["chapter_question"]["start"], "pregunta de cierre", f"«{p['chapter_question'].get('text', '')}»"))
    rows.sort(key=lambda r: r[0])
    lines = [f"  {int(t // 60):02d}:{t % 60:04.1f} · {el} · {what}" for t, el, what in rows[:max_rows]]
    return ("ASÍ SE ARMA UN CAPÍTULO DE ESTE CANAL (plan dorado de "
            f"{g.get('cap', '?')}, aprobado por el dueño; copiá el RITMO y la densidad, no el contenido):\n" + "\n".join(lines))


def identity_violations(plan: dict[str, Any], transitions: dict[Any, dict[str, Any]] | None = None) -> list[str]:
    """Reglas duras de la identidad sobre el plan final (vacía = cumple)."""
    v: list[str] = []
    pk = (plan.get("pico") or {}).get("t")
    pun = plan.get("punch_in") or []
    if len(pun) > gfx_rules.punch_max_identity:
        v.append(f"golpes de zoom {len(pun)} > {gfx_rules.punch_max_identity}")
    if pk is not None and any(abs(t - pk) <= PEAK_CLEAR_SEC for t in pun):
        v.append("golpe de zoom a ±5 s del pico")
    if transitions:
        kinds = [transitions[k]["kind"] for k in sorted(transitions, key=lambda x: int(x))]
        run = 0
        for k in kinds:
            run = 0 if k in ("cut", "cut_punch", "flash") else run + 1
            if run >= 3:
                v.append("3 transiciones seguidas sin corte")
                break
        if kinds.count("flash") > gfx_rules.flash_max_per_cap:
            v.append(f"flash {kinds.count('flash')} > {gfx_rules.flash_max_per_cap}")
        if kinds.count("dip") > gfx_rules.dip_max_per_cap:
            v.append(f"fundido a negro {kinds.count('dip')} > {gfx_rules.dip_max_per_cap}")
    return v
