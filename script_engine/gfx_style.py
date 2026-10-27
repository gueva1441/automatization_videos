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
    identity_violations() chequeo duro del plan final (cantidades, alternancia, pico) → lista de violaciones
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from gfx_config import gfx_rules

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


ZOOM_PUNCH_SCALE = 1.4        # transition_config «zoom_punch»: 1.0→1.4 saliente / 1.4→1.0 entrante
ZOOM_PUNCH_MS = 400           # ídem, duration_ms


def transiciones_por_relato(scenes: list[Any], plan: dict[str, Any], beats: list[dict[str, Any]],
                            fps: int = 30) -> dict[int, dict[str, Any]]:
    """F30b §A: la transición de ENTRADA de cada escena por el relato (clave = idx de la escena entrante); el
    emotional_rank no decide nada. Por cada corte, la primera que aplica:
        1. el corte más cercano a pico.t dentro del beat pico (uno por cap)   → zoom_punch «pico»
        2. la escena entrante es de otro beat que la saliente                → dissolve  «cambio de beat»
        3. arranca el reloj (time_ticker) en la escena entrante               → dissolve  «salto de tiempo»
        4. la última escena del cap (la de la pregunta de cierre)             → dip       «cierre»
        5. todo lo demás                                                      → cut       «corte»
    Corre sobre el plan final (después del crítico). F36 §D: sin la regla de la lupa (la lupa se borró)."""
    r = gfx_rules
    out: dict[int, dict[str, Any]] = {}
    if len(scenes) < 2:
        return out
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
        if s.idx == punch:
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
