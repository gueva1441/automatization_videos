"""F59 A1 — construye `a1_fixture.json` (copia FIJA) desde el estado de hoy de Wittenoom (`123bbb64…`): por ítem de
`03_visual.json` (caps 2–6 `image_prompts`, caps 1 y 7 `supplemental_image_prompts` y la foto del clip `image_f8`) la
ENTRADA de `m03_visual.armar_item` (casilleros = `json.loads(raw_llm_prompt)` + beat/cerrada/subject_ref/foto_madre_ref/
narration_anchor/emotional_rank cuando están, `anio`, `anio_fuente`, `escala` del beat) y la SALIDA esperada (`prompt`,
`raw_llm_prompt`, `sensible`, `motivos`, `_f8_*` si están). Más `people_groups` del topic y `lang = place_language(topic)`.
Sin red, sin LLM. Correr desde la raíz: `python lab/hyperframes/f59/a1_fixture.py`."""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import fase1_5                                                  # noqa: E402
from script_engine import m03_imagenes_v3 as v3img              # noqa: E402
from script_engine import m03_visual as m3                      # noqa: E402

TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
OUT = Path(__file__).resolve().parent / "a1_fixture.json"
CONTEXTO = ("beat", "cerrada", "subject_ref", "foto_madre_ref", "narration_anchor", "emotional_rank")
ESPERADO = ("prompt", "raw_llm_prompt", "sensible", "motivos", "_f8_problemas", "_f8_texto_fuera", "_f8_slots_scrub")


def _entrada(it: dict, by_n: dict) -> dict:
    cas = json.loads(it["raw_llm_prompt"])
    for k in CONTEXTO:
        if k in it:
            cas[k] = it[k]
    return {"casilleros": cas, "anio": it.get("anio") or "", "anio_fuente": it.get("anio_fuente") or "",
            "escala": bool((by_n.get(it.get("beat")) or {}).get("escala"))}


def main() -> None:
    topic = fase1_5._load_topic_by_id(TID)
    beats = v3img.load_beats(topic, m3.STEPS_DIR)
    assert beats, "Wittenoom sin escaleta: no hay `escala` por beat"
    visual = json.loads((m3.STEPS_DIR / TID / "03_visual.json").read_text(encoding="utf-8"))
    items = []
    for ch in visual["chapters"]:
        cap = ch["chapter_number"]
        by_n = {b["n"]: b for b in beats.get(cap) or []}
        if "image_prompts" in ch:
            for i, it in enumerate(ch["image_prompts"], start=1):
                items.append({"id": f"ch{cap:02d}_img_{i:02d}", "cap": cap, "entrada": _entrada(it, by_n),
                              "esperado": {k: it[k] for k in ESPERADO if k in it}})
        else:
            f8 = ch["image_f8"]
            esperado = {"prompt": ch["image_prompt"], "raw_llm_prompt": f8["raw_llm_prompt"],
                        "sensible": ch["image_sensible"], "motivos": f8["motivos"],
                        **{k: f8[k] for k in ("_f8_problemas", "_f8_texto_fuera", "_f8_slots_scrub") if k in f8}}
            items.append({"id": f"ch{cap:02d}_f8", "cap": cap,
                          "entrada": _entrada({**f8, "narration_anchor": ch["narration_anchor"],
                                               "subject_ref": ch["subject_ref"]}, by_n),
                          "esperado": esperado})
            for i, it in enumerate(ch["supplemental_image_prompts"], start=1):
                items.append({"id": f"ch{cap:02d}_supp_{i:02d}", "cap": cap, "entrada": _entrada(it, by_n),
                              "esperado": {k: it[k] for k in ESPERADO if k in it}})
    fixture = {"topic_id": TID,
               "fuente": "data/scripts/_steps/<tid>/03_visual.json + data/topics_db.json + 01a_escaleta.json",
               "people_groups": topic.get("people_groups") or [], "lang": v3img.place_language(topic), "items": items}
    OUT.write_text(json.dumps(fixture, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"{OUT}: {len(items)} items", dict(Counter(i['cap'] for i in items)), "lang =", fixture["lang"])


if __name__ == "__main__":
    main()
