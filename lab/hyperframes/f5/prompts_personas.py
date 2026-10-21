"""F5b S6 (§1.6): los prompts de imagen de v2 (texto, sin imágenes) cuyas anclas muestran PERSONAS → PROMPTS_PERSONAS_v2.md

Para leerlos en la PARADA. Se marca el que reemplaza al del niño en la celda (v1, ch02 imagen 8: «An African American
woman and a young boy, about 10 years old… inside a dim, concrete prison cell»): el de v2 en el mismo lugar del cap y
los de v2 cuya ancla habla de los niños/menores.
Uso: PYTHONIOENCODING=utf-8 python lab/hyperframes/f5/prompts_personas.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
V1, V2 = "ba6c3cac-a091-41c0-8dad-afd2f4364747", "ba6c3cac-f5v2"
STEPS = ROOT / "data" / "scripts" / "_steps"
OUT = Path(__file__).resolve().parent / "PROMPTS_PERSONAS_v2.md"
PEOPLE = re.compile(r"\b(man|men|woman|women|boy|boys|girl|girls|child|children|kid|kids|inmates?|prisoners?|guards?|"
                    r"sheriff|deput(?:y|ies)|officers?|people|person|persons|figures?|crowd|detainees?|teen(?:ager)?s?|"
                    r"juveniles?|youths?|hands?|faces?|silhouettes?|tourists?|jurors?|lawyers?|survivors?)\b", re.I)
KIDS = re.compile(r"\b(niñ[oa]s?|menores|juvenil(?:es)?|diez años|10 años|pequeñ[oa]s)\b", re.I)
V1_BOY = ("ch02", 8)


def _load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def prompts(visual: dict) -> list[dict]:
    """[{cap, idx, kind, anchor, subject, prompt}] de todas las imágenes (Veo + suplementarias + flux)."""
    out = []
    for c in visual["chapters"]:
        cap = f"ch{c['chapter_number']:02d}"
        if c.get("image_prompt"):
            out.append({"cap": cap, "idx": 0, "kind": "veo", "anchor": c.get("narration_anchor") or "",
                        "subject": "", "prompt": c["image_prompt"]})
        for k, ip in enumerate(c.get("supplemental_image_prompts") or [], start=1):
            out.append({"cap": cap, "idx": k, "kind": "supp", "anchor": ip.get("narration_anchor") or "",
                        "subject": "", "prompt": ip.get("prompt") or ""})
        for k, ip in enumerate(c.get("image_prompts") or []):
            out.append({"cap": cap, "idx": k, "kind": "flux", "anchor": ip.get("narration_anchor") or "",
                        "subject": ip.get("subject") or "", "prompt": ip.get("prompt") or ""})
    return out


def _where(prompt: str) -> str:
    """¿El prompt ubica a los niños en el centro juvenil (canon §1.6) o en una celda de la prisión de adultos?"""
    if re.search(r"\b(CYC|YSC|juvenile|youth (?:facility|center)|youth detention)\b", prompt, re.I):
        return "centro juvenil (CYC/YSC): respeta el canon"
    if re.search(r"\b(cell|prison|jail|cellblock|cell block)\b", prompt, re.I):
        return "celda/prisión sin centro juvenil: NO respeta el canon"
    return "sin lugar de detención"


def main() -> None:
    v2 = prompts(_load(STEPS / V2 / "03_visual.json"))
    v1 = {(p["cap"], p["idx"]): p for p in prompts(_load(STEPS / V1 / "03_visual.json")) if p["kind"] == "flux"}
    people = [p for p in v2 if PEOPLE.search(p["subject"] or p["prompt"])]
    canon = ""
    try:
        from script_engine.m03_visual import _format_documented_locations
        topic_pool = _load(STEPS / V2 / "01_facts_sources.json").get("evidence_pool")
        canon = _format_documented_locations({"evidence_pool": topic_pool})
    except Exception as e:  # noqa: BLE001
        canon = f"(no se pudo regenerar el bloque: {type(e).__name__})"
    boy = v1.get(V1_BOY)
    L = ["# F5b S6 — Prompts de imagen de v2 con personas (texto, sin imágenes)", "",
         f"Fuente: `data/scripts/_steps/{V2}/03_visual.json` (copia en `lab/hyperframes/f5/v2/03_visual.json`). "
         f"{len(v2)} prompts en total; {len(people)} con personas (sujeto o prompt nombra gente: hombre, mujer, niño, "
         "recluso, guardia, multitud, manos, siluetas…).", "",
         "## Bloque que se agregó al canon (§1.6, lo único que cambia en `m03_visual`)", "", "```", canon or "(vacío)",
         "```", "", "## El que reemplaza al del niño en la celda", ""]
    if boy:
        L += [f"**v1 · {V1_BOY[0]} imagen {V1_BOY[1]}** — ancla «{boy['anchor']}»", "", f"> {boy['prompt']}", ""]
    same = next((p for p in v2 if (p["cap"], p["idx"]) == V1_BOY and p["kind"] == "flux"), None)
    kids = [p for p in v2 if KIDS.search(p["anchor"])]
    # EL reemplazo: el ancla que dice el dato («niños de hasta 10 años», D67); el resto son otros prompts con niños
    main_ = next((p for p in kids if re.search(r"10 años|diez años", p["anchor"], re.I)), kids[0] if kids else None)
    marked = {(main_["cap"], main_["kind"], main_["idx"])} if main_ else set()
    if main_:
        L += [f"**v2 · {main_['cap']} {main_['kind']} {main_['idx']} ← REEMPLAZA AL DEL NIÑO EN LA CELDA** — ancla "
              f"«{main_['anchor']}» · {_where(main_['prompt'])}", "", f"> {main_['prompt']}", ""]
    if same:
        L += [f"Mismo lugar del cap en v2 ({same['cap']} imagen {same['idx']}): ancla «{same['anchor']}» — "
              f"{'con personas' if PEOPLE.search(same['subject'] or same['prompt']) else 'sin personas'}.", ""]
    L += ["### Otros prompts de v2 con niños", "", "| cap | img | ancla | dónde lo ubica el prompt |", "|---|---|---|---|"]
    L += [f"| {p['cap']} | {p['kind']} {p['idx']} | {p['anchor'][:110]} | {_where(p['prompt'])} |"
          for p in kids if p is not main_] or ["| — | — | — | — |"]
    L += [""]
    L += ["## Todos los prompts con personas", "", "| cap | img | ancla (narración v2) | sujeto / inicio del prompt |",
          "|---|---|---|---|"]
    for p in people:
        mark = " **← reemplaza al del niño en la celda**" if (p["cap"], p["kind"], p["idx"]) in marked else ""
        subj = (p["subject"] or p["prompt"])[:160].replace("|", "/")
        L.append(f"| {p['cap']} | {p['kind']} {p['idx']}{mark} | {p['anchor'][:120].replace('|', '/')} | {subj} |")
    L += ["", "## Prompts completos (con personas)", ""]
    for p in people:
        L += [f"### {p['cap']} · {p['kind']} {p['idx']}", f"- ancla: «{p['anchor']}»", "", f"> {p['prompt']}", ""]
    OUT.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{OUT}: {len(people)} con personas de {len(v2)} · reemplazo del niño: "
          f"{sorted(marked)} · otros con niños: {[(p['cap'], p['kind'], p['idx'], _where(p['prompt'])[:20]) for p in kids]}")


if __name__ == "__main__":
    main()
