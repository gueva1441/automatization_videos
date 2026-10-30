# -*- coding: utf-8 -*-
"""F60 Etapa A — m03 (casilleros, con el casillero `persona` nuevo) sobre la COPIA de lab lab/hyperframes/f60/base/.

- Entradas de solo lectura copiadas de producción a la copia (_steps/<tid>/): escaleta, narración v3, narración 01b,
  pool v3 (la ficha remapea ids), ficha, _perfil, canon. El topic se lee de data/topics_db.json (fase1_5._load_topic_by_id;
  NO se llama asegurar_canon, que escribe en topics_db). sync_map y timestamps: output/audio/<tid>/ de producción (lectura).
- m03_visual.STEPS_DIR → la copia: `_persist` escribe lab/hyperframes/f60/base/data/scripts/_steps/<tid>/03_visual.json.
  El 03_visual anterior de la copia se guarda antes en lab/hyperframes/f60/a/03_visual_antes.json.
- Salida: lab/hyperframes/f60/a/etapa_a.json (+ .log): tabla foto → persona vs la tabla de verdad (por índice y por ancla),
  grep de nombres del canon en todos los `prompt`, diff de 5 ítems, costo (cost_tracker). Cero fotos.

USO: PYTHONIOENCODING=utf-8 python lab/hyperframes/f60/etapa_a_m03.py
"""
from __future__ import annotations

import difflib
import json
import re
import shutil
import sys
import time
import unicodedata
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
F60 = Path(__file__).resolve().parent
BASE = F60 / "base"
A = F60 / "a"
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
STEPS_PROD = ROOT / "data/scripts/_steps" / TID
STEPS_COPIA = BASE / "data/scripts/_steps" / TID
# Corrida 1 (a/corrida1_narracion_29oct.*): entradas de producción tal cual → `01b_narration.json` de _steps es la narración
# NUEVA del 29-oct 20:55 (F54 B.5), distinta de la que usó el 03_visual del 29-oct 13:00 (y el audio y el guion vivo): 3/96
# anclas coinciden → la tabla de verdad no se puede aplicar. Corrida 2: las entradas del guion ANTERIOR, que son las del
# 03_visual anterior (96/96 anclas): lab/hyperframes/f54/antes/ (respaldo del 29-oct 18:34 hecho antes de F54 B.5) y el
# pool previo a F54 (lab/hyperframes/f44/B/_steps/<tid>/, 27-oct 23:37); ficha, _perfil y canon de producción (sin cambios).
F54_ANTES = ROOT / "lab/hyperframes/f54/antes"
F44_B = ROOT / "lab/hyperframes/f44/B/_steps" / TID
ENTRADAS = (("01a_escaleta.json", F54_ANTES), ("01a_skeleton.json", F54_ANTES), ("01b_narracion_v3.json", F54_ANTES),
            ("01b_narration.json", F54_ANTES), ("00_pool_v3.json", F44_B), ("ficha_caso.json", STEPS_PROD),
            ("_perfil.json", STEPS_PROD), ("05_visual_canon.json", STEPS_PROD))

# Tabla de verdad del analista (handoff): (k, kind, i) → esperado. kind: img / supp / image_prompt
VERDAD = [
    ((1, "img", 0), "Daniel Écija", "1961, traje"),
    ((1, "img", 1), "Daniel Écija", ""),
    ((1, "img", 3), "Daniel Écija (+ María Bernal)", "img[3] también María Bernal"),
    ((1, "img", 4), "Daniel Écija (+ quizá Ramón de Juan)", "dos parejas"),
    ((1, "img", 5), "NO Daniel", "la otra familia"),
    ((2, "img", 15), "Daniel Écija", ""),
    ((3, "img", 6), "Daniel Écija (dudoso: podría ser Ramón)", ""),
    ((3, "img", 8), "Daniel Écija", "aparte de los otros mineros"),
    ((3, "img", 13), "Daniel Écija", "de espaldas"),
    ((4, "img", 4), 'Daniel Écija o ""', "1966, de espaldas, ~30"),
    ((4, "img", 12), '""', "1991, 55 años"),
    ((4, "img", 13), '""', "1991, 55 años"),
    ((4, "img", 14), '""', "foto sepia en 2023"),
    ((0, "supp", 0), '""', "solo el pie"),
    ((0, "image_prompt", 0), "Daniel Écija", "cap con clip, Etapa C"),
    ((0, "supp", 3), "Daniel Écija", "cap con clip, Etapa C"),
]
LOG: list[str] = []


def log(s: str) -> None:
    print(s, flush=True)
    LOG.append(s)


def _norm(s: str) -> str:
    return unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()


def _item(ch: list, k: int, kind: str, i: int) -> dict | None:
    c = ch[k]
    if kind == "img":
        l = c.get("image_prompts") or []
        return l[i] if i < len(l) else None
    if kind == "supp":
        l = c.get("supplemental_image_prompts") or []
        return l[i] if i < len(l) else None
    return {"prompt": c.get("image_prompt"), "narration_anchor": c.get("narration_anchor"),
            **{kk: v for kk, v in (c.get("image_f8") or {}).items()}} if c.get("image_prompt") else None


def _todas(ch: list):
    """(ref, item) de TODAS las fotos: image_prompts, supps y la foto del clip (image_prompt + image_f8)."""
    for k, c in enumerate(ch):
        for i, it in enumerate(c.get("image_prompts") or []):
            yield f"chapters[{k}].img[{i}]", it
        for i, it in enumerate(c.get("supplemental_image_prompts") or []):
            yield f"chapters[{k}].supp[{i}]", it
        if c.get("image_prompt"):
            yield f"chapters[{k}].image_prompt", _item(ch, k, "image_prompt", 0)


def _parrafo(narr: dict, k: int, ancla: str) -> str:
    """El párrafo de la narración del cap k que contiene el ancla (o '')."""
    text = (narr["chapters"][k].get("narration") or "")
    for p in re.split(r"\n\s*\n", text):
        if ancla and _norm(ancla[:40]) in _norm(p):
            return p.strip()
    return ""


def main() -> int:
    A.mkdir(exist_ok=True)
    from script_engine import m03_visual as m3
    from fase1_5 import _load_topic_by_id
    from config import OUTPUT_DIR
    from cost_tracker import cost_tracker

    # 1. entradas de solo lectura a la copia; respaldo del 03_visual anterior
    for f, d in ENTRADAS:
        src = d / f
        assert src.exists(), src
        shutil.copy2(src, STEPS_COPIA / f)
    antes_p = STEPS_COPIA / "03_visual.json"
    antes = json.loads(antes_p.read_text(encoding="utf-8"))
    shutil.copy2(antes_p, A / "03_visual_antes.json")
    log("entradas copiadas a la copia: " + ", ".join(f"{f} ← {d.relative_to(ROOT)}" for f, d in ENTRADAS) + "; 03_visual anterior → a/03_visual_antes.json")

    m3.STEPS_DIR = STEPS_COPIA.parent          # _persist y las lecturas de _steps van a la copia
    topic = _load_topic_by_id(TID)
    assert topic.get("documented_people") and topic.get("people_groups"), "el topic no trae el canon"
    skeleton = json.loads((STEPS_COPIA / "01a_skeleton.json").read_text(encoding="utf-8"))
    narration = json.loads((STEPS_COPIA / "01b_narration.json").read_text(encoding="utf-8"))
    sync_map = json.loads((OUTPUT_DIR / "audio" / TID / "sync_map.json").read_text(encoding="utf-8"))
    nombres = [p["name"] for p in topic["documented_people"]]
    log(f"topic: {len(nombres)} personas documentadas, {len(topic['people_groups'])} grupos · STEPS_DIR → {m3.STEPS_DIR}")
    log("SI casilleros trae `- persona:`: " + str("- persona:" in m3.SYSTEM_INSTRUCTION_CASILLEROS)
        + " · required: " + str(m3._casilleros_schema(1)["items"]["required"][-3:]))

    # 2. m03 completo (7 caps) con el costo medido
    cost_tracker.start_video(TID)
    t0 = time.time()
    try:
        out = m3.assign_visual_prompts(topic, skeleton, narration, sync_map=sync_map)
    finally:
        r = cost_tracker.end_video()
        usd = round(getattr(r, "total_cost", 0.0) or 0.0, 4)
        seg = round(time.time() - t0, 1)
    log(f"m03: {seg} s · US$ {usd} (cost_tracker) · persistido en {STEPS_COPIA / '03_visual.json'}")
    despues = json.loads((STEPS_COPIA / "03_visual.json").read_text(encoding="utf-8"))
    ch, ch0 = despues["chapters"], antes["chapters"]

    # 3. tabla foto → persona (todas) + contra la tabla de verdad (por índice y por ancla del 03_visual anterior)
    tabla = []
    for ref, it in _todas(ch):
        tabla.append({"ref": ref, "persona": it.get("persona"), "people_group": it.get("people_group"),
                      "year": it.get("year") or it.get("anio"), "shot_scale": it.get("shot_scale"),
                      "ancla": it.get("narration_anchor")})
    sin_persona = [t["ref"] for t in tabla if "persona" not in (dict(t) if t["persona"] is not None else {}) and t["persona"] is None]
    log(f"fotos: {len(tabla)} · con `persona` no vacía: {sum(1 for t in tabla if t['persona'])} · sin clave persona: {sin_persona}")
    verdad = []
    for (k, kind, i), esperado, nota in VERDAD:
        viejo = _item(ch0, k, kind, i)
        nuevo = _item(ch, k, kind, i)
        ancla_v = (viejo or {}).get("narration_anchor")
        # misma ancla en el 03_visual nuevo (m03 vuelve a elegir anclas: el índice puede moverse)
        por_ancla = None
        if ancla_v:
            for ref, it in _todas(ch):
                if ref.startswith(f"chapters[{k}].") and _norm(it.get("narration_anchor") or "") == _norm(ancla_v):
                    por_ancla = {"ref": ref, "persona": it.get("persona"), "prompt": it.get("prompt")}
                    break
        verdad.append({"ref": f"chapters[{k}].{kind}[{i}]" if kind != "image_prompt" else f"chapters[{k}].image_prompt",
                       "esperado": esperado, "nota": nota,
                       "ancla_anterior": ancla_v, "persona_por_indice": (nuevo or {}).get("persona"),
                       "ancla_nueva_por_indice": (nuevo or {}).get("narration_anchor"),
                       "misma_ancla": por_ancla, "parrafo": _parrafo(narration, k, ancla_v or "")})
    # 4. grep de nombres del canon (completo y de pila, sin mayúsculas ni acentos) en TODOS los `prompt`
    hits = []
    for ref, it in _todas(ch):
        pn = _norm(it.get("prompt") or "")
        for n in nombres:
            for tok in {n, n.split()[0]}:
                if re.search(r"(?<![a-z])" + re.escape(_norm(tok)) + r"(?![a-z])", pn):
                    hits.append({"ref": ref, "nombre_canon": n, "token": tok, "prompt": it.get("prompt")})
    log(f"grep de nombres del canon en `prompt`: {len(hits)} coincidencias" + (" → PARÁ" if hits else ""))
    for h in hits:
        log(f"  {h['ref']}: «{h['token']}» ({h['nombre_canon']})")
    # 5. diff de 5 ítems contra el 03_visual anterior (mismo índice; se muestra también la ancla de cada lado)
    diffs = []
    for (k, kind, i) in [(1, "img", 0), (1, "img", 3), (3, "img", 8), (4, "img", 12), (0, "supp", 0)]:
        a, b = _item(ch0, k, kind, i) or {}, _item(ch, k, kind, i) or {}
        d = list(difflib.unified_diff((a.get("prompt") or "").split(". "), (b.get("prompt") or "").split(". "),
                                      "antes", "despues", lineterm="", n=0))
        diffs.append({"ref": f"chapters[{k}].{kind}[{i}]", "ancla_antes": a.get("narration_anchor"),
                      "ancla_despues": b.get("narration_anchor"), "persona_despues": b.get("persona"),
                      "claves_antes": list(a.keys()), "claves_despues": list(b.keys()),
                      "prompt_antes": a.get("prompt"), "prompt_despues": b.get("prompt"), "diff": d})
    res = {"tid": TID, "segundos_m03": seg, "usd_m03": usd, "nombres_canon": nombres, "tabla": tabla, "verdad": verdad,
           "grep_nombres": hits, "diffs": diffs, "caps": [(c["chapter_number"], len(c.get("image_prompts") or []),
                                                          len(c.get("supplemental_image_prompts") or [])) for c in ch],
           "caps_antes": [(c["chapter_number"], len(c.get("image_prompts") or []),
                           len(c.get("supplemental_image_prompts") or [])) for c in ch0], "log": LOG}
    (A / "etapa_a.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    (A / "etapa_a.log").write_text("\n".join(LOG), encoding="utf-8")
    return 1 if hits else 0


if __name__ == "__main__":
    sys.exit(main())
