# -*- coding: utf-8 -*-
"""F61 Etapa B — medición en texto: m03 de los 7 caps sobre la COPIA de lab (lab/hyperframes/f60/base) con el código
F61 (sin R7, sin «a QUARTER», sin el tope del 25 %). Copia de lab/hyperframes/f60/etapa_a3_m03.py con las MISMAS
entradas (f54/antes + pool f44/B, ficha y _perfil de producción, canon A3 inyectado por CANON_KEYS, anclas fijas de
f60/a/03_visual_despues.json, 7 caps en paralelo por assign_visual_prompts → _f8_fix_video) y salidas en f61/:
03_visual_f61.json, etapa_f61.json, etapa_f61.log. «Antes» = f60/a3/03_visual_a3.json. Cero fotos, clips o voz.
USO: PYTHONIOENCODING=utf-8 python lab/hyperframes/f61/etapa_f61_m03.py
"""
from __future__ import annotations

import json
import re
import shutil
import sys
import time
import unicodedata
from collections import Counter
from pathlib import Path
from threading import Lock

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
F60 = ROOT / "lab/hyperframes/f60"
F61 = Path(__file__).resolve().parent
BASE = F60 / "base"
A3 = F60 / "a3"
REF = F60 / "a" / "03_visual_despues.json"          # anclas fijas (corrida 2 de la Etapa A)
ANTES = A3 / "03_visual_a3.json"                     # el «antes» de la tabla B.2
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
STEPS_PROD = ROOT / "data/scripts/_steps" / TID
STEPS_COPIA = BASE / "data/scripts/_steps" / TID
F54_ANTES = ROOT / "lab/hyperframes/f54/antes"
F44_B = ROOT / "lab/hyperframes/f44/B/_steps" / TID
ENTRADAS = (("01a_escaleta.json", F54_ANTES), ("01a_skeleton.json", F54_ANTES), ("01b_narracion_v3.json", F54_ANTES),
            ("01b_narration.json", F54_ANTES), ("00_pool_v3.json", F44_B), ("ficha_caso.json", STEPS_PROD),
            ("_perfil.json", STEPS_PROD))
LOG: list[str] = []
_LOCK = Lock()
_PROMPTS: list[str] = []
_SI: list[str] = []


def log(s: str) -> None:
    with _LOCK:
        print(s, flush=True)
        LOG.append(s)


def _norm(s: str) -> str:
    return " ".join(unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower().split())


def _todas(v):
    """(ref, cap_number, item) de todas las fotos: image_f8 del cap con clip, image_prompts, supps."""
    for k, c in enumerate(v["chapters"]):
        n = c.get("chapter_number") or k + 1
        if c.get("image_prompt"):
            yield f"chapters[{k}].image_prompt", n, {"prompt": c["image_prompt"], "narration_anchor": c.get("narration_anchor"),
                                                     **(c.get("image_f8") or {})}
        for i, it in enumerate(c.get("image_prompts") or []):
            yield f"chapters[{k}].img[{i}]", n, it
        for i, it in enumerate(c.get("supplemental_image_prompts") or []):
            yield f"chapters[{k}].supp[{i}]", n, it


def _pos(text: str, anchor: str) -> tuple[int, int]:
    i = text.find(anchor)
    if i < 0:
        i = _norm(text).find(_norm(anchor))
    return (max(i, 0), max(i, 0) + len(anchor))


def _rehechas_cap(v) -> Counter:
    c = Counter()
    for _, _, it in _todas(v):
        r = it.get("_f8_rehecha")
        if r:
            c[str(r)[:60]] += 1
    return c


def main() -> int:
    F61.mkdir(exist_ok=True)
    from script_engine import m03_visual as m3
    from script_engine import m03_imagenes_v3 as v3img
    from fase1_5 import _load_topic_by_id, CANON_KEYS
    from config import OUTPUT_DIR
    from cost_tracker import cost_tracker

    assert "dominates" not in m3.SYSTEM_INSTRUCTION_CASILLEROS and "QUARTER" not in m3.SYSTEM_INSTRUCTION_CASILLEROS, "código sin F61"
    assert "following the VISUAL ARC OF THIS CAP block" in m3.SYSTEM_INSTRUCTION_CASILLEROS
    for f, d in ENTRADAS:
        shutil.copy2(d / f, STEPS_COPIA / f)
    ref = json.loads(REF.read_text(encoding="utf-8"))
    antes = json.loads(ANTES.read_text(encoding="utf-8"))
    canon_a3 = json.loads((A3 / "05_visual_canon_a3.json").read_text(encoding="utf-8"))
    if (STEPS_COPIA / "03_visual.json").exists():
        shutil.copy2(STEPS_COPIA / "03_visual.json", F61 / "03_visual_copia_antes_f61.json")
    m3.STEPS_DIR = STEPS_COPIA.parent
    topic = _load_topic_by_id(TID)
    topic = {**topic, **{k: canon_a3[k] for k in CANON_KEYS}}
    skeleton = json.loads((STEPS_COPIA / "01a_skeleton.json").read_text(encoding="utf-8"))
    narration = json.loads((STEPS_COPIA / "01b_narration.json").read_text(encoding="utf-8"))
    sync_map = json.loads((OUTPUT_DIR / "audio" / TID / "sync_map.json").read_text(encoding="utf-8"))
    intents = {c.get("chapter_number"): c.get("narrative_intent") for c in skeleton.get("chapters", [])}
    log(f"canon A3 inyectado ({list(CANON_KEYS)}) · intents {intents}")

    real_plan = m3._plan_anchors
    usado_real: list[int] = []

    def plan_fijo(narration_text, n, engine, veo_position=None, veo_zone_chars=None, cap_number=0):
        c = ref["chapters"][cap_number - 1]
        if engine == "veo":
            supps = [s["narration_anchor"] for s in c.get("supplemental_image_prompts") or []]
            if not c.get("narration_anchor") or len(supps) != n:
                usado_real.append(cap_number)
                return real_plan(narration_text, n, engine, veo_position=veo_position, veo_zone_chars=veo_zone_chars, cap_number=cap_number)
            va = c["narration_anchor"]
            return {"veo_anchor": {"anchor": va, "pos": _pos(narration_text, va)[0], "end": _pos(narration_text, va)[1]},
                    "supplementals": [{"anchor": a, "pos": _pos(narration_text, a)[0], "end": _pos(narration_text, a)[1]} for a in supps]}
        anchors = [it["narration_anchor"] for it in c.get("image_prompts") or []]
        if len(anchors) != n:
            usado_real.append(cap_number)
            return real_plan(narration_text, n, engine, veo_position=veo_position, veo_zone_chars=veo_zone_chars, cap_number=cap_number)
        return {"anchors": [{"anchor": a, "pos": _pos(narration_text, a)[0], "end": _pos(narration_text, a)[1]} for a in anchors]}

    real_llamar = m3._llamar_casilleros

    def llamar_mirando(prompt, system_instruction=None, response_schema=None, description=None, **kw):
        with _LOCK:
            _PROMPTS.append(prompt)
            if system_instruction and system_instruction not in _SI:
                _SI.append(system_instruction)
        return real_llamar(prompt, system_instruction=system_instruction, response_schema=response_schema, description=description, **kw)

    m3._plan_anchors = plan_fijo
    m3._llamar_casilleros = llamar_mirando
    cost_tracker.start_video(TID)
    t0 = time.time()
    try:
        m3.assign_visual_prompts(topic, skeleton, narration, sync_map=sync_map)
    finally:
        r = cost_tracker.end_video()
        usd = round(getattr(r, "total_cost", 0.0) or 0.0, 4)
        seg = round(time.time() - t0, 1)
        m3._plan_anchors = real_plan
        m3._llamar_casilleros = real_llamar
    log(f"m03 7 caps: {seg} s · US$ {usd} (cost_tracker) · caps con _plan_anchors real: {usado_real}")
    desp = json.loads((STEPS_COPIA / "03_visual.json").read_text(encoding="utf-8"))
    shutil.copy2(STEPS_COPIA / "03_visual.json", F61 / "03_visual_f61.json")
    si_ok = [("dominates" not in s and "QUARTER" not in s and "following the VISUAL ARC" in s) for s in _SI]
    arc_en_prompts = sum(1 for p in _PROMPTS if "VISUAL ARC OF THIS CAP" in p)
    log(f"prompts de casilleros: {len(_PROMPTS)} (con bloque VISUAL ARC: {arc_en_prompts}) · SI distintos: {len(_SI)} · SI sin R7/QUARTER y con VISUAL ARC: {si_ok}")

    # ── B.2 tablas antes / después ──
    def tabla(v):
        tot, per, ang, por_cap = Counter(), Counter(), Counter(), {}
        n = 0
        for _, cap, it in _todas(v):
            n += 1
            s = it.get("shot_scale")
            tot[s] += 1
            ang[str(it.get("camera_angle") or "").strip().lower()] += 1
            por_cap.setdefault(cap, Counter())[s] += 1
            if it.get("persona"):
                per[s] += 1
        f8 = v.get("_f8_imagenes") or {}
        return {"total": n, "shot_scale": dict(tot), "por_cap": {c: dict(x) for c, x in sorted(por_cap.items())},
                "persona_shot_scale": dict(per), "camera_angle_top6": ang.most_common(6),
                "caps_sin_establecimiento": (f8.get("despues") or {}).get("caps_sin_establecimiento"),
                "rehechas_video": f8.get("rehechas"), "rehechas_cap": dict(_rehechas_cap(v)),
                "f8_antes": f8.get("antes"), "f8_despues": f8.get("despues")}
    TA, TD = tabla(antes), tabla(desp)
    orden = ["extreme_wide", "wide", "medium", "close", "detail"]

    def fila(d):
        return " · ".join(f"{k} {d.get(k, 0)}" for k in orden)
    log(f"\nB.2 shot_scale TOTAL — antes ({TA['total']}): {fila(TA['shot_scale'])}")
    log(f"                      después ({TD['total']}): {fila(TD['shot_scale'])}")
    for c in sorted(set(TA["por_cap"]) | set(TD["por_cap"])):
        log(f"  cap {c} ({intents.get(c)}): antes {fila(TA['por_cap'].get(c, {}))} | después {fila(TD['por_cap'].get(c, {}))}")
    log(f"  con persona — antes: {fila(TA['persona_shot_scale'])} | después: {fila(TD['persona_shot_scale'])}")
    log(f"  camera_angle top 6 — antes: {TA['camera_angle_top6']} | después: {TD['camera_angle_top6']}")
    log(f"  caps_sin_establecimiento — antes: {TA['caps_sin_establecimiento']} | después: {TD['caps_sin_establecimiento']}")
    log(f"  re-hechuras del video — antes: {TA['rehechas_video']} | después: {TD['rehechas_video']}")
    log(f"  re-hechuras por cap (_f8_rehecha) — antes: {TA['rehechas_cap']} | después: {TD['rehechas_cap']}")
    log(f"  _f8 antes/después (después): {TD['f8_antes']} → {TD['f8_despues']}")
    # pares por ancla (la misma foto antes/después)
    A_by = {_norm(it.get("narration_anchor")): (r_, it) for r_, _, it in _todas(antes)}
    pares, cambios = [], Counter()
    for r_, cap, it in _todas(desp):
        k = _norm(it.get("narration_anchor"))
        if k in A_by:
            a = A_by[k][1]
            pares.append({"ref": r_, "cap": cap, "ancla": it.get("narration_anchor"), "antes": a.get("shot_scale"), "despues": it.get("shot_scale"),
                          "persona": it.get("persona"), "emotional_rank": it.get("emotional_rank")})
            cambios[f"{a.get('shot_scale')}→{it.get('shot_scale')}"] += 1
    log(f"  pares por ancla: {len(pares)}/{TD['total']} · cambios de shot_scale: {dict(cambios.most_common())}")

    # ── B.3 10 prompts completos ──
    todas = [(r_, cap, it) for r_, cap, it in _todas(desp)]
    rank = {"R1": 0, "R2": 1, "R3": 2}

    def pick(cond, n, key=None, usados=set()):
        c = [(r_, cap, it) for r_, cap, it in todas if cond(cap, it) and r_ not in usados]
        if key:
            c.sort(key=key)
        out = c[:n]
        usados.update(r for r, _, _ in out)
        return out
    usados: set = set()
    sel = []
    sel += [("close/detail de mayor emotional_rank", x) for x in pick(lambda cap, it: it.get("shot_scale") in ("close", "detail"), 3,
                                                                      key=lambda t: rank.get(t[2].get("emotional_rank"), 9), usados=usados)]
    sel += [("medium con persona", x) for x in pick(lambda cap, it: it.get("shot_scale") == "medium" and it.get("persona"), 3, usados=usados)]
    sel += [("cap 5 (shock)", x) for x in pick(lambda cap, it: cap == 5, 2, key=lambda t: rank.get(t[2].get("emotional_rank"), 9), usados=usados)]
    sel += [("cap 2 (setup)", x) for x in pick(lambda cap, it: cap == 2, 2, key=lambda t: rank.get(t[2].get("emotional_rank"), 9), usados=usados)]
    prompts10 = []
    for etiq, (r_, cap, it) in sel:
        prompts10.append({"grupo": etiq, "ref": r_, "cap": cap, "shot_scale": it.get("shot_scale"), "camera_angle": it.get("camera_angle"),
                          "emotional_rank": it.get("emotional_rank"), "persona": it.get("persona"), "anio": it.get("anio") or it.get("year"),
                          "ancla": it.get("narration_anchor"), "prompt": it.get("prompt")})
        log(f"\nB.3 [{etiq}] {r_} cap {cap} · {it.get('shot_scale')} · {it.get('camera_angle')} · {it.get('emotional_rank')} · persona {it.get('persona')}\n{it.get('prompt')}")
    res = {"tid": TID, "segundos": seg, "usd": usd, "usado_plan_real": usado_real, "n_prompts": len(_PROMPTS), "arc_en_prompts": arc_en_prompts,
           "si_ok": si_ok, "intents": intents, "antes": TA, "despues": TD, "pares": pares, "cambios": dict(cambios), "prompts10": prompts10, "log": LOG}
    (F61 / "etapa_f61.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    (F61 / "etapa_f61.log").write_text("\n".join(LOG), encoding="utf-8")
    return 0


if __name__ == "__main__":
    sys.exit(main())
