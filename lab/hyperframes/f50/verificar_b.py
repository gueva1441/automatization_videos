# -*- coding: utf-8 -*-
"""F50 B §5 — verificación en seco (sin API) del prompt de foto de producción contra la candidata del lab.

1. Pedido: cap 2 de Wittenoom con el canon S5 de F48 (`f48/canon_S5.json`) sobre el topic de antes de F50
   (`f50/antes/topic_wittenoom.json`) y las anclas/beats de `f50/antes/03_visual.json`: sistema + usuario de producción
   = `f48/pedidos/pedido_S5_ch02.txt` byte a byte, y el md5 del esquema = el del pedido S5 (`f48/slots_S5_ch02.json`).
2. Armado: con los casilleros crudos de `f48/slots_S5_ch02.json` y `slots_S5_ch07.json` pasados por
   `_render_prompts_seedream` de producción (Opus reemplazado por la respuesta guardada; sin re-hechuras), los prompts =
   los S5 de `f49/PROMPTS_F49.json` salvo las fotos que tocan las chascadas de F50 (cartel y cifra en mayúscula).

Uso: python lab/hyperframes/f50/verificar_b.py → escribe B_VERIFICACION_datos.json; sale 1 si algo no coincide.
"""
from __future__ import annotations

import copy
import difflib
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
HF = ROOT / "lab" / "hyperframes"
F50 = HF / "f50"
sys.path.insert(0, str(ROOT))
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"


def _j(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def _md5(x) -> str:
    s = x if isinstance(x, str) else json.dumps(x, ensure_ascii=False, sort_keys=True)
    return hashlib.md5(s.encode("utf-8")).hexdigest()


class _Alto(Exception):
    pass


def preparar(cap: int):
    """topic (antes + GEO/ERA + canon S5 + _f8), cap_data, narración del cap, anclas y beats de antes."""
    import fase1_5
    from script_engine import m03_expediente as mexp
    from script_engine import m03_imagenes_v3 as v3img
    from script_engine import m03_visual as m03
    topic = _j(F50 / "antes" / "topic_wittenoom.json")
    canon = _j(HF / "f48" / "canon_S5.json")
    narr = fase1_5._load_narration(TID)
    skel = fase1_5._load_skeleton(TID)
    topic = {**topic, **m03._geo_era(TID, narr),
             **{k: canon[k] for k in ("era_visual_canon", "documented_people", "anachronism_blocklist",
                                      "documented_props") if k in canon},
             "people_groups": canon["people_groups"]}
    beats = v3img.load_beats(topic, m03.STEPS_DIR)
    narr_ch = narr["chapters"]
    topic["_f8"] = {"beats": beats, "year": v3img.topic_year(topic, beats), "lang": v3img.place_language(topic),
                    "fuentes": mexp.fuentes(TID, m03.STEPS_DIR),
                    "anio_prev": {n: mexp.anio_previo(narr_ch, n) for n in range(1, 8)}}
    ch = next(c for c in _j(F50 / "antes" / "03_visual.json")["chapters"] if c["chapter_number"] == cap)
    v03 = ch.get("image_prompts") or ch.get("supplemental_image_prompts") or []   # cap Veo: los extras (como el lab)
    topic["_f8"]["force_assign"] = [{"beat": it.get("beat"), "cerrada": bool(it.get("cerrada"))} for it in v03]
    sch = next(c for c in skel["chapters"] if c["chapter_number"] == cap)
    nch = next(c for c in narr_ch if c["chapter_number"] == cap)
    plan = {"anchors": [{"anchor": it["narration_anchor"]} for it in v03]}
    return topic, sch, (nch.get("narration") or "").strip(), plan


def pedido() -> tuple[bool, dict]:
    from script_engine import m03_visual as m03
    topic, sch, narr, plan = preparar(2)
    visto = {}

    def falsa(prompt, system_instruction=None, response_schema=None, description=None, **_):
        visto.update(system=system_instruction, user=prompt, schema=response_schema)
        raise _Alto()
    orig = m03._llamar_casilleros
    m03._llamar_casilleros = falsa
    try:
        m03._render_prompts_seedream(topic, sch, narr, plan, 2)
    except _Alto:
        pass
    finally:
        m03._llamar_casilleros = orig
    prod = f"=== SYSTEM ===\n{visto['system']}\n\n=== USER ===\n{visto['user']}\n"
    lab = (HF / "f48" / "pedidos" / "pedido_S5_ch02.txt").read_text(encoding="utf-8")
    lab_schema = _j(HF / "f48" / "slots_S5_ch02.json")["pedidos"][0]["md5_schema"]
    ok_txt, ok_sch = prod == lab, _md5(visto["schema"]) == lab_schema
    print(f"  pedido cap 2: sistema+usuario {'= byte a byte' if ok_txt else 'DISTINTO'} "
          f"(md5 lab {_md5(lab)} · producción {_md5(prod)}); esquema {'=' if ok_sch else 'DISTINTO'} "
          f"(md5 lab {lab_schema} · producción {_md5(visto['schema'])})")
    if not ok_txt:
        sys.stdout.writelines(list(difflib.unified_diff(lab.splitlines(True), prod.splitlines(True), "lab",
                                                         "producción"))[:200])
    return ok_txt and ok_sch, {"md5_lab": _md5(lab), "md5_prod": _md5(prod), "md5_schema_lab": lab_schema,
                               "md5_schema_prod": _md5(visto["schema"])}


def armado() -> tuple[bool, list[dict]]:
    from script_engine import m03_visual as m03
    p49 = _j(HF / "f49" / "PROMPTS_F49.json")
    filas, ok = [], True
    for cap in (2, 7):
        topic, sch, narr, plan = preparar(cap)
        topic["_f8"]["refill"] = True                          # sin re-hechuras de cap (llamarían a Opus)
        crudo = _j(HF / "f48" / f"slots_S5_ch{cap:02d}.json")["crudos"][-1]["respuesta"]
        orig = m03._llamar_casilleros
        m03._llamar_casilleros = lambda *a, **k: copy.deepcopy(crudo)
        try:
            out = m03._render_prompts_seedream(topic, sch, narr, plan, cap)
        finally:
            m03._llamar_casilleros = orig
        for it, ref in zip(out["image_prompts"], p49[f"S5_ch{cap:02d}"]):
            igual = it["prompt"] == ref["prompt"]
            anio_igual = str(it.get("anio")) == str(ref["anio"])
            tii = it.get("text_in_image") or {}
            cartel = bool(tii.get("present") and tii.get("text"))
            fila = {"cap": cap, "foto": ref["foto"], "igual": igual, "anio_prod": it.get("anio"),
                    "anio_lab": ref["anio"], "cartel": cartel, "antes": ref["prompt"], "despues": it["prompt"]}
            if not igual:
                a, b = ref["prompt"], it["prompt"]
                fila["por_chascada"] = cartel or _solo_mayuscula(a, b)
                ok = ok and fila["por_chascada"]
            ok = ok and anio_igual
            filas.append(fila)
    dif = [f for f in filas if not f["igual"]]
    print(f"  armado: {len(filas)} prompts · iguales {len(filas) - len(dif)} · distintos {len(dif)} "
          f"(por chascada {sum(1 for f in dif if f.get('por_chascada'))}) · años distintos "
          f"{sum(1 for f in filas if str(f['anio_prod']) != str(f['anio_lab']))}")
    return ok, filas


def _solo_mayuscula(a: str, b: str) -> bool:
    """Las dos prosas difieren solo en la mayúscula de «a couple of / a few / several» al inicio de una oración."""
    import re
    return a != b and re.sub(r"\b(A couple of|A few|Several)\b", lambda m: m.group(0).lower(), b) == a


def main() -> int:
    ok1, md5s = pedido()
    ok2, filas = armado()
    (F50 / "B_VERIFICACION_datos.json").write_text(json.dumps({"pedido": md5s, "armado": filas}, ensure_ascii=False,
                                                              indent=1), encoding="utf-8")
    print(f"  → {'PASA' if ok1 and ok2 else 'NO PASA (PARADA)'}")
    return 0 if ok1 and ok2 else 1


if __name__ == "__main__":
    sys.exit(main())
