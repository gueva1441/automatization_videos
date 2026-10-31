# -*- coding: utf-8 -*-
"""F60 Etapa A3.2 paso 2 — m03 de los 7 caps sobre la COPIA de lab con el canon NUEVO (a3/05_visual_canon_a3.json)
inyectado al topic y las ANCLAS FIJAS de a/03_visual_despues.json (corrida 2 de la Etapa A). Desde etapa_a2_m03.py:
- CAPS = range(1, 8), sin la envoltura de caps parciales (los 7 llaman a Opus; workers al máximo = CAP_MAX_WORKERS).
- Entradas de la corrida 2 (f54/antes + pool f44/B); ficha y _perfil de producción; el 05_visual_canon.json de producción
  NO se copia: `topic = {**topic, **{k: canon_a3[k] for k in fase1_5.CANON_KEYS}}` antes de assign_visual_prompts.
- Anclas fijas: `m3._plan_anchors` se envuelve en el runner para devolver las anclas de la referencia (flux: anchors
  con pos/end por búsqueda en la narración; veo: veo_anchor + supplementals). `_reconcile_anchor_timing` sigue como en
  producción: si mueve anclas, se empareja por ancla y se declara.
- Verificación en el log de que el bloque PERSONAS que recibe Opus es el nuevo (pass-through de _llamar_casilleros que
  guarda el primer prompt).
Salidas en a3/: 03_visual_a3.json, etapa_a3.json, etapa_a3.log. Cero fotos.
USO: PYTHONIOENCODING=utf-8 python lab/hyperframes/f60/etapa_a3_m03.py
"""
from __future__ import annotations

import json
import re
import shutil
import sys
import time
import unicodedata
from pathlib import Path
from threading import Lock

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
F60 = Path(__file__).resolve().parent
BASE = F60 / "base"
A3 = F60 / "a3"
REF = F60 / "a" / "03_visual_despues.json"          # corrida 2 de la Etapa A (anclas + persona de referencia)
REF_A2 = F60 / "a2" / "03_visual_a2.json"
REF_ANTES = F60 / "a" / "03_visual_antes.json"       # el 03_visual de la tabla de verdad
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
STEPS_PROD = ROOT / "data/scripts/_steps" / TID
STEPS_COPIA = BASE / "data/scripts/_steps" / TID
F54_ANTES = ROOT / "lab/hyperframes/f54/antes"
F44_B = ROOT / "lab/hyperframes/f44/B/_steps" / TID
ENTRADAS = (("01a_escaleta.json", F54_ANTES), ("01a_skeleton.json", F54_ANTES), ("01b_narracion_v3.json", F54_ANTES),
            ("01b_narration.json", F54_ANTES), ("00_pool_v3.json", F44_B), ("ficha_caso.json", STEPS_PROD),
            ("_perfil.json", STEPS_PROD))
CAPS = range(1, 8)
# escenas de Daniel (SALIDA_A tabla de verdad + A2), por fragmento de ancla
ESCENAS = [("baile", "Dieciséis de septiembre"), ("boda", "se casan"), ("barco", "van juntos"), ("mi marido", "mi marido"),
           ("dos parejas", "amigos íntimos de otra pareja"), ("pista", "los Écija bajaban"),
           ("mina (Daniel trabajaba)", "Daniel trabajaba en la mina"), ("mina (primer día)", "primer día de trabajo de su padre"),
           ("fórceps / bautizo", "Le pusieron Daniel"), ("se fueron", "Se fueron antes de que nadie"),
           ("Madrid 1966", "entran a su casa en Madrid"), ("1991 médico", "Daniel Écija va al médico"),
           ("muere 55", "Daniel muere a los cincuenta y cinco"), ("retrato pie", "todos miran a cámara menos el pie"),
           ("clip pie", "pie envuelto en una venda"), ("se llama Daniel", "El hombre se llama Daniel")]
LOG: list[str] = []
_LOCK = Lock()
_PROMPTS: list[str] = []


def log(s: str) -> None:
    with _LOCK:
        print(s, flush=True)
        LOG.append(s)


def _norm(s: str) -> str:
    return " ".join(unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower().split())


def _todas(v):
    for k, c in enumerate(v["chapters"]):
        if c.get("image_prompt"):
            yield f"chapters[{k}].image_prompt", {"prompt": c["image_prompt"], "narration_anchor": c.get("narration_anchor"),
                                                  **(c.get("image_f8") or {})}
        for i, it in enumerate(c.get("image_prompts") or []):
            yield f"chapters[{k}].img[{i}]", it
        for i, it in enumerate(c.get("supplemental_image_prompts") or []):
            yield f"chapters[{k}].supp[{i}]", it


def _parrafo(narr, k, ancla):
    for p in re.split(r"\n\s*\n", narr["chapters"][k].get("narration") or ""):
        if ancla and _norm(ancla[:40]) in _norm(p):
            return p.strip()
    return ""


def _pos(text: str, anchor: str) -> tuple[int, int]:
    i = text.find(anchor)
    if i < 0:
        i = _norm(text).find(_norm(anchor))
    return (max(i, 0), max(i, 0) + len(anchor))


def main() -> int:
    A3.mkdir(exist_ok=True)
    from script_engine import m03_visual as m3
    from fase1_5 import _load_topic_by_id, CANON_KEYS
    from config import OUTPUT_DIR
    from cost_tracker import cost_tracker

    for f, d in ENTRADAS:
        shutil.copy2(d / f, STEPS_COPIA / f)
    ref = json.loads(REF.read_text(encoding="utf-8"))
    ref_a2 = json.loads(REF_A2.read_text(encoding="utf-8"))
    ref_antes = json.loads(REF_ANTES.read_text(encoding="utf-8"))
    canon_a3 = json.loads((A3 / "05_visual_canon_a3.json").read_text(encoding="utf-8"))
    shutil.copy2(STEPS_COPIA / "03_visual.json", A3 / "03_visual_antes_a3.json")
    m3.STEPS_DIR = STEPS_COPIA.parent
    topic = _load_topic_by_id(TID)
    topic = {**topic, **{k: canon_a3[k] for k in CANON_KEYS}}
    skeleton = json.loads((STEPS_COPIA / "01a_skeleton.json").read_text(encoding="utf-8"))
    narration = json.loads((STEPS_COPIA / "01b_narration.json").read_text(encoding="utf-8"))
    sync_map = json.loads((OUTPUT_DIR / "audio" / TID / "sync_map.json").read_text(encoding="utf-8"))
    nombres = [p["name"] for p in canon_a3["documented_people"]]
    dan = next(p for p in canon_a3["documented_people"] if p["name"] == "Daniel Écija")
    log(f"canon A3 inyectado al topic ({list(CANON_KEYS)}); Daniel: appearance «{dan['appearance_canon']}» · condition {dan.get('condition_by_period')}")
    log("TEXTO_PERSONA: " + m3.TEXTO_PERSONA)
    bloque = m3._format_seedream_canon_block(topic)
    log("bloque PERSONAS (según _format_seedream_canon_block):\n" + "\n".join(l for l in bloque.splitlines() if "Daniel Écija" in l or l.startswith("    condition") or l.startswith("PERSONAS")))

    # ── anclas fijas: envoltura de _plan_anchors (devuelve las de la referencia; si n no coincide, la real) ──
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
    log(f"m03 7 caps: {seg} s · US$ {usd} (cost_tracker) · caps con _plan_anchors real (n distinto): {usado_real}")
    a3 = json.loads((STEPS_COPIA / "03_visual.json").read_text(encoding="utf-8"))
    shutil.copy2(STEPS_COPIA / "03_visual.json", A3 / "03_visual_a3.json")
    # bloque PERSONAS que recibió Opus (primer prompt de casilleros)
    p0 = next((p for p in _PROMPTS if "PERSONAS DOCUMENTADAS" in p), "")
    i = p0.find("PERSONAS DOCUMENTADAS")
    personas_en_prompt = p0[i:i + 2600] if i >= 0 else ""
    log(f"prompts de casilleros capturados: {len(_PROMPTS)} · el bloque PERSONAS del prompt trae «condition»: {'condition ' in personas_en_prompt} · Daniel con appearance nuevo: {dan['appearance_canon'] in personas_en_prompt}")

    # ── emparejamiento por ancla con la referencia (y A2) ──
    def by_anchor(v):
        return {_norm(it.get("narration_anchor")): (ref_, it) for ref_, it in _todas(v)}
    R, R2 = by_anchor(ref), by_anchor(ref_a2)
    pares, sin_par = [], []
    for ref_, it in _todas(a3):
        key = _norm(it.get("narration_anchor"))
        if key in R:
            pares.append({"ref_a3": ref_, "ref_A": R[key][0], "ancla": it.get("narration_anchor"), "persona_A": R[key][1].get("persona"),
                          "persona_A2": R2[key][1].get("persona") if key in R2 else "(sin par en A2)", "persona_A3": it.get("persona")})
        else:
            sin_par.append({"ref_a3": ref_, "ancla": it.get("narration_anchor"), "persona_A3": it.get("persona")})
    log(f"pares por ancla con la referencia: {len(pares)}/{sum(1 for _ in _todas(a3))} · sin par: {len(sin_par)} (anclas movidas por _reconcile_anchor_timing o conteo distinto)")

    # b) escenas de Daniel: A (ref) / A2 / A3 por fragmento
    def busca(v, frag):
        return [(ref_, it.get("persona")) for ref_, it in _todas(v) if _norm(frag) in _norm(it.get("narration_anchor"))]
    escenas = [{"escena": nom, "frag": frag, "A": busca(ref, frag), "A2": busca(ref_a2, frag), "A3": busca(a3, frag),
                "tabla_verdad": busca(ref_antes, frag)} for nom, frag in ESCENAS]
    for e in escenas:
        log(f"[b] {e['escena']}: A {[(r[0], r[1]) for r in e['A']]} · A2 {[(r[0], r[1]) for r in e['A2']]} · A3 {[(r[0], r[1]) for r in e['A3']]}")
    # c/d/e) todas las fotos con Daniel, con año, venda, ancla y párrafo; María; Daniel hijo; Víctor; edades
    def info(ref_, it):
        k = int(ref_.split("[")[1].split("]")[0])
        pr = it.get("prompt") or ""
        return {"ref": ref_, "persona": it.get("persona"), "year": it.get("year") or it.get("anio"), "ancla": it.get("narration_anchor"),
                "venda": bool(re.search(r"bandag|limp\b|limping|crutch", pr, re.I)), "prompt": pr,
                "parrafo": _parrafo(narration, k, it.get("narration_anchor") or "")}
    daniel = [info(r_, it) for r_, it in _todas(a3) if "Daniel Écija" in (it.get("persona") or [])]
    maria = [info(r_, it) for r_, it in _todas(a3) if "María Bernal" in (it.get("persona") or [])]
    hijo = [info(r_, it) for r_, it in _todas(a3) if "Daniel Écija hijo" in (it.get("persona") or [])]
    victor = [info(r_, it) for r_, it in _todas(a3) if "Víctor Calvo" in (it.get("persona") or [])]
    log(f"[c/d] fotos con Daniel en A3: {len(daniel)} · con venda/cojera: {sum(1 for d in daniel if d['venda'])} · años {[d['year'] for d in daniel]}")
    log(f"[e] María: {len(maria)} · Daniel hijo: {len(hijo)} · Víctor Calvo: {len(victor)} (años {[v['year'] for v in victor]})")
    # f) control de nombres (regla 19:35) en TODAS las fotos
    para, revisar = [], []
    for ref_, it in _todas(a3):
        pn = _norm(it.get("prompt") or "")
        for nom in nombres:
            toks = {nom, nom.split()[0]} if len(nom.split()) > 1 else {nom}
            for tok in toks:
                if re.search(r"(?<![a-z])" + re.escape(_norm(tok)) + r"(?![a-z])", pn):
                    (para if len(nom.split()) >= 2 else revisar).append({"ref": ref_, "nombre_canon": nom, "token": tok, "prompt": it.get("prompt")})
    log(f"[f] control de nombres: PARÁ {len(para)} · revisar {len(revisar)}")
    for h in para + revisar:
        log(f"    {'PARÁ' if h in para else 'revisar'} {h['ref']}: «{h['token']}» ({h['nombre_canon']})")
    # g) prompt de video del cap 1
    c1 = a3["chapters"][0]
    g = {"image_prompt": c1.get("image_prompt"), "video_prompt": c1.get("video_prompt"), "persona_image_f8": (c1.get("image_f8") or {}).get("persona"),
         "venda_en_image_prompt": bool(re.search(r"bandag|limp", c1.get("image_prompt") or "", re.I)),
         "venda_en_video_prompt": bool(re.search(r"bandag|limp", c1.get("video_prompt") or "", re.I))}
    log(f"[g] cap 1: venda en image_prompt {g['venda_en_image_prompt']} · en video_prompt {g['venda_en_video_prompt']} · persona {g['persona_image_f8']}")
    personas_todas = [{"ref": r_, "persona": it.get("persona"), "year": it.get("year") or it.get("anio"), "ancla": it.get("narration_anchor")}
                      for r_, it in _todas(a3) if it.get("persona")]
    res = {"tid": TID, "segundos": seg, "usd": usd, "usado_plan_real": usado_real, "personas_en_prompt": personas_en_prompt,
           "n_prompts": len(_PROMPTS), "pares": pares, "sin_par": sin_par, "escenas": escenas, "daniel": daniel, "maria": maria,
           "hijo": hijo, "victor": victor, "control_para": para, "control_revisar": revisar, "cap1": g, "personas_todas": personas_todas,
           "nombres_canon": nombres, "log": LOG}
    (A3 / "etapa_a3.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    (A3 / "etapa_a3.log").write_text("\n".join(LOG), encoding="utf-8")
    return 1 if para else 0


if __name__ == "__main__":
    sys.exit(main())
