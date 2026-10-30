# -*- coding: utf-8 -*-
"""F60 Etapa A2 — m03 (casilleros, `persona` sin «or if unsure») sobre la COPIA de lab, SOLO caps 2, 3 y 4.
Copia de etapa_a_m03.py con estos cambios:
- Entradas: las mismas de la corrida 2 de la Etapa A (guion anterior: f54/antes + pool f44/B + ficha/perfil/canon de producción).
- Solo caps 2-4 llaman a Opus: el ThreadPoolExecutor de m03 se envuelve en el runner (sin tocar producción) y para los
  otros caps devuelve el capítulo de la REFERENCIA (a/03_visual_despues.json, corrida 2) tal cual. El pase F8 de video
  (`_f8_fix_video`) corre como en producción sobre los 7 caps; lo que rehaga fuera de 2-4 se reporta.
- Salidas en a2/: 03_visual_a2.json, etapa_a2.json, etapa_a2.log. Referencia = a/03_visual_despues.json.
- Emparejamiento contra la corrida 2 POR ANCLA (normalizada); ancla sin par o cap con otro número de fotos → aparte.
- Control de nombres con la regla nueva (DECISIONES 19:35): nombre de 2+ palabras → PARÁ; 1 palabra → «revisar».
UNA sola corrida (Opus no es determinista). Cero fotos.

USO: PYTHONIOENCODING=utf-8 python lab/hyperframes/f60/etapa_a2_m03.py
"""
from __future__ import annotations

import copy
import json
import re
import shutil
import sys
import time
import unicodedata
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
F60 = Path(__file__).resolve().parent
BASE = F60 / "base"
A2 = F60 / "a2"
REF = F60 / "a" / "03_visual_despues.json"          # corrida 2 de la Etapa A
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
STEPS_PROD = ROOT / "data/scripts/_steps" / TID
STEPS_COPIA = BASE / "data/scripts/_steps" / TID
F54_ANTES = ROOT / "lab/hyperframes/f54/antes"
F44_B = ROOT / "lab/hyperframes/f44/B/_steps" / TID
ENTRADAS = (("01a_escaleta.json", F54_ANTES), ("01a_skeleton.json", F54_ANTES), ("01b_narracion_v3.json", F54_ANTES),
            ("01b_narration.json", F54_ANTES), ("00_pool_v3.json", F44_B), ("ficha_caso.json", STEPS_PROD),
            ("_perfil.json", STEPS_PROD), ("05_visual_canon.json", STEPS_PROD))
CAPS = (2, 3, 4)                                     # chapters[1], [2], [3] (base 0)
ESCENAS = [("baile", "Dieciséis de septiembre"), ("boda", "se casan"), ("barco", "van juntos"), ("mi marido", "mi marido"),
           ("dos parejas", "amigos íntimos de otra pareja"), ("pista", "los Écija bajaban"),
           ("mina (Daniel trabajaba)", "Daniel trabajaba en la mina"), ("mina (primer día)", "primer día de trabajo de su padre")]
LOG: list[str] = []


def log(s: str) -> None:
    print(s, flush=True)
    LOG.append(s)


def _norm(s: str) -> str:
    return " ".join(unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower().split())


def _parrafo(narr: dict, k: int, ancla: str) -> str:
    text = (narr["chapters"][k].get("narration") or "")
    for p in re.split(r"\n\s*\n", text):
        if ancla and _norm(ancla[:40]) in _norm(p):
            return p.strip()
    return ""


def main() -> int:
    A2.mkdir(exist_ok=True)
    from script_engine import m03_visual as m3
    from fase1_5 import _load_topic_by_id
    from config import OUTPUT_DIR
    from cost_tracker import cost_tracker

    for f, d in ENTRADAS:
        shutil.copy2(d / f, STEPS_COPIA / f)
    ref = json.loads(REF.read_text(encoding="utf-8"))
    shutil.copy2(STEPS_COPIA / "03_visual.json", A2 / "03_visual_antes_a2.json")
    log("entradas copiadas a la copia (las de la corrida 2 de la Etapa A); referencia = a/03_visual_despues.json")
    assert "or if unsure" not in m3.SYSTEM_INSTRUCTION_CASILLEROS and "- persona:" in m3.SYSTEM_INSTRUCTION_CASILLEROS
    log("TEXTO_PERSONA en el SI, sin «or if unsure»: " + m3.TEXTO_PERSONA)

    m3.STEPS_DIR = STEPS_COPIA.parent
    topic = _load_topic_by_id(TID)
    skeleton = json.loads((STEPS_COPIA / "01a_skeleton.json").read_text(encoding="utf-8"))
    narration = json.loads((STEPS_COPIA / "01b_narration.json").read_text(encoding="utf-8"))
    sync_map = json.loads((OUTPUT_DIR / "audio" / TID / "sync_map.json").read_text(encoding="utf-8"))
    canon = json.loads((STEPS_COPIA / "05_visual_canon.json").read_text(encoding="utf-8"))
    nombres = [p["name"] for p in canon["documented_people"]]

    # ── solo caps 2-4 llaman a Opus: envoltura del executor de m03 (lab, sin tocar producción) ──
    def _ref_cap(n: int) -> dict:
        c = copy.deepcopy(ref["chapters"][n - 1])
        if "image_prompt" in c:        # caps con clip: `_f8_items` (foto del clip + supps) para el pase F8 de video
            c["_f8_items"] = [{"prompt": c["image_prompt"], "narration_anchor": c.get("narration_anchor"),
                               **(c.get("image_f8") or {})}] + list(c.get("supplemental_image_prompts") or [])
        return c

    class _SoloCaps(ThreadPoolExecutor):
        def submit(self, fn, *args, **kw):
            n = args[0] if args else kw.get("cap_n")
            if n in CAPS:
                return super().submit(fn, *args, **kw)
            log(f"[a2] cap {n}: no se llama a Opus; capítulo de la referencia (corrida 2)")
            return super().submit(_ref_cap, n)

    m3.ThreadPoolExecutor = _SoloCaps
    cost_tracker.start_video(TID)
    t0 = time.time()
    try:
        m3.assign_visual_prompts(topic, skeleton, narration, sync_map=sync_map)
    finally:
        r = cost_tracker.end_video()
        usd = round(getattr(r, "total_cost", 0.0) or 0.0, 4)
        seg = round(time.time() - t0, 1)
    m3.ThreadPoolExecutor = ThreadPoolExecutor
    log(f"m03 (caps {CAPS} + pase F8 de video): {seg} s · US$ {usd} (cost_tracker)")
    a2 = json.loads((STEPS_COPIA / "03_visual.json").read_text(encoding="utf-8"))
    shutil.copy2(STEPS_COPIA / "03_visual.json", A2 / "03_visual_a2.json")

    # ── caps fuera de 2-4: ¿quedaron iguales a la referencia? (el pase F8 de video puede rehacer ítems) ──
    fuera = {}
    for n in range(1, 8):
        if n in CAPS:
            continue
        fuera[n] = json.dumps(a2["chapters"][n - 1], sort_keys=True, ensure_ascii=False) == json.dumps(ref["chapters"][n - 1], sort_keys=True, ensure_ascii=False)
    log(f"caps fuera de 2-4 idénticos a la referencia: {fuera}")

    # ── emparejamiento por ancla (caps 2-4) ──
    pares, sin_par, conteos = [], [], {}
    for n in CAPS:
        k = n - 1
        r_items = ref["chapters"][k].get("image_prompts") or []
        a_items = a2["chapters"][k].get("image_prompts") or []
        conteos[n] = {"referencia": len(r_items), "a2": len(a_items)}
        r_by = {}
        for i, it in enumerate(r_items):
            r_by.setdefault(_norm(it.get("narration_anchor")), []).append((i, it))
        for i, it in enumerate(a_items):
            cand = r_by.get(_norm(it.get("narration_anchor")))
            if cand:
                j, rit = cand.pop(0)
                pares.append({"cap": n, "k": k, "i_a2": i, "i_ref": j, "ancla": it.get("narration_anchor"),
                              "persona_ref": rit.get("persona"), "persona_a2": it.get("persona"), "year": it.get("year"),
                              "cambio": (rit.get("persona") or []) != (it.get("persona") or []),
                              "parrafo": _parrafo(narration, k, it.get("narration_anchor") or "")})
            else:
                sin_par.append({"cap": n, "i_a2": i, "ancla": it.get("narration_anchor"), "persona_a2": it.get("persona"),
                                "parrafo": _parrafo(narration, k, it.get("narration_anchor") or "")})
        for key, rest in r_by.items():
            for j, rit in rest:
                sin_par.append({"cap": n, "i_ref": j, "ancla": rit.get("narration_anchor"), "persona_ref": rit.get("persona"),
                                "solo_en_referencia": True})
    cambios_por_cap = {n: sum(1 for p in pares if p["cap"] == n and p["cambio"]) for n in CAPS}
    pares_por_cap = {n: sum(1 for p in pares if p["cap"] == n) for n in CAPS}
    log(f"pares por ancla: {pares_por_cap} · cambios de persona: {cambios_por_cap} · sin par: {len(sin_par)} · conteos: {conteos}")

    # a) escenas donde faltó Daniel en la corrida 2
    def _busca(doc, frag):
        out = []
        for n in CAPS:
            k = n - 1
            for i, it in enumerate(doc["chapters"][k].get("image_prompts") or []):
                if _norm(frag) in _norm(it.get("narration_anchor")):
                    out.append((f"chapters[{k}].img[{i}]", it.get("persona"), it.get("narration_anchor")))
        return out
    escenas = [{"escena": nombre, "frag": frag, "referencia": _busca(ref, frag), "a2": _busca(a2, frag)} for nombre, frag in ESCENAS]
    for e in escenas:
        log(f"[a] {e['escena']}: ref {[(r[0], r[1]) for r in e['referencia']]} → a2 {[(r[0], r[1]) for r in e['a2']]}")
    # b) fotos de caps 2-4 con Daniel en persona (A2), con ancla y párrafo; CC juzga si la ancla lo involucra
    daniel = []
    for n in CAPS:
        k = n - 1
        for i, it in enumerate(a2["chapters"][k].get("image_prompts") or []):
            if "Daniel Écija" in (it.get("persona") or []):
                daniel.append({"ref": f"chapters[{k}].img[{i}]", "persona": it.get("persona"), "ancla": it.get("narration_anchor"),
                               "parrafo": _parrafo(narration, k, it.get("narration_anchor") or ""), "year": it.get("year")})
    log(f"[b] fotos de caps 2-4 con Daniel en A2: {len(daniel)} (referencia: {sum(1 for p in pares if 'Daniel Écija' in (p['persona_ref'] or []))} entre los pares)")
    # ── control de nombres (regla nueva): 2+ palabras → PARÁ; 1 palabra → revisar ──
    para, revisar = [], []
    for n in CAPS:
        k = n - 1
        for i, it in enumerate(a2["chapters"][k].get("image_prompts") or []):
            pn = _norm(it.get("prompt") or "")
            for nom in nombres:
                toks = {nom, nom.split()[0]} if len(nom.split()) > 1 else {nom}
                for tok in toks:
                    if re.search(r"(?<![a-z])" + re.escape(_norm(tok)) + r"(?![a-z])", pn):
                        (para if len(nom.split()) >= 2 else revisar).append(
                            {"ref": f"chapters[{k}].img[{i}]", "nombre_canon": nom, "token": tok, "prompt": it.get("prompt")})
    log(f"control de nombres caps 2-4: PARÁ (2+ palabras) {len(para)} · revisar (1 palabra) {len(revisar)}")
    for h in para:
        log(f"  PARÁ {h['ref']}: «{h['token']}» ({h['nombre_canon']})")
    for h in revisar:
        log(f"  revisar {h['ref']}: «{h['token']}» ({h['nombre_canon']})")
    res = {"tid": TID, "caps": CAPS, "segundos": seg, "usd": usd, "texto_persona": m3.TEXTO_PERSONA, "fuera_identicos": fuera,
           "conteos": conteos, "pares": pares, "sin_par": sin_par, "cambios_por_cap": cambios_por_cap, "pares_por_cap": pares_por_cap,
           "escenas": escenas, "daniel_a2": daniel, "nombres_canon": nombres, "control_para": para, "control_revisar": revisar,
           "persona_a2_caps": [{"ref": f"chapters[{n-1}].img[{i}]", "persona": it.get("persona"), "ancla": it.get("narration_anchor")}
                               for n in CAPS for i, it in enumerate(a2["chapters"][n - 1].get("image_prompts") or []) if it.get("persona")],
           "log": LOG}
    (A2 / "etapa_a2.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    (A2 / "etapa_a2.log").write_text("\n".join(LOG), encoding="utf-8")
    return 1 if para else 0


if __name__ == "__main__":
    sys.exit(main())
