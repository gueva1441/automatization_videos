# -*- coding: utf-8 -*-
"""F50 D §2 — Wittenoom en papel: lee el 03_visual.json que acaba de escribir m03 (camino nuevo) y arma
PAPEL_FOTOS_WITTENOOM.md y .json: por cap y por foto, n.º · ancla · beat · año y de dónde salió · people_group · plano ·
prompt entero · notas F8 · si fue rehecha y por qué; caps 1 y 7 además video_prompt, negative_prompt y duration.
Al final: fotos por cap (contra las de antes), años por fuente, re-hechuras, carteles y costos reales por modelo.
Uso: python lab/hyperframes/f50/papel.py   (solo lee; sin API)
"""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
F50 = Path(__file__).resolve().parent
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
STEPS = ROOT / "data" / "scripts" / "_steps" / TID


def _j(p: Path):
    raw = p.read_bytes()
    try:
        return json.loads(raw.decode("utf-8"))
    except UnicodeDecodeError:
        return json.loads(raw.decode("cp1252"))


def _plano(it: dict) -> str:
    return " · ".join(str(it[k]) for k in ("shot_scale", "camera_angle", "lens_technique") if it.get(k)) or "-"


def fotos_de(cap: dict) -> list[dict]:
    """Las fotos del cap en el orden del video; en un cap Veo, la foto 0 es el primer cuadro del clip."""
    if cap.get("image_prompts") is not None:
        return [{**it, "_rol": "foto"} for it in cap["image_prompts"]]
    f0 = {**(cap.get("image_f8") or {}), "prompt": cap.get("image_prompt"), "narration_anchor": cap.get("narration_anchor"),
          "_rol": "primer cuadro del clip Veo"}
    return [f0] + [{**it, "_rol": "foto"} for it in cap.get("supplemental_image_prompts") or []]


def costos() -> dict:
    hist = _j(ROOT / "data" / "cost_history.json")
    reps = [r for r in hist if isinstance(r, dict) and r.get("video_id") == TID]
    ult = reps[-1] if reps else {}
    por = defaultdict(lambda: [0, 0.0])
    for e in ult.get("entries", []):
        k = f"{e.get('service', '?')} · {str(e.get('description', '')).split(' (')[0]}"
        por[k][0] += 1
        por[k][1] += float(e.get("total_cost") or 0)
    pasos = (_j(STEPS / "01_v3_costos.json").get("_corridas") or [])[-3:]
    return {"registro": ult.get("created_at"), "total": round(float(ult.get("total_cost") or 0), 4),
            "por_servicio": {k: {"llamadas": n, "usd": round(c, 4)} for k, (n, c) in sorted(por.items())},
            "pasos_01_v3_costos": pasos}


def main() -> int:
    from asset_manager import VEO_NEGATIVE_PROMPT, _veo_duration
    v = _j(STEPS / "03_visual.json")
    antes = _j(F50 / "antes" / "03_visual.json")
    n_antes = {c["chapter_number"]: len(fotos_de(c)) for c in antes["chapters"]}
    caps, filas = [], []
    L = ["# Wittenoom en papel — las fotos con el prompt nuevo (F50 D)", "",
         "Salida de `python fase1_5.py --topic 123bbb64-9fca-4395-8bf4-57d60e219ef1 --only m03` con el camino de F50 "
         "(canon desde la ficha, casilleros con Opus 5.5, armado por código, F8). **Cero fotos.** Para revisar antes de "
         "la tanda de fotos y clips.", ""]
    for cap in sorted(v["chapters"], key=lambda c: c["chapter_number"]):
        n = cap["chapter_number"]
        fs = fotos_de(cap)
        L += [f"## Cap {n} — {len(fs)} fotos (antes {n_antes.get(n, '?')})", ""]
        if cap.get("video_prompt"):
            L += [f"**Clip Veo** ({cap.get('veo_position')}) — ancla: «{cap.get('narration_anchor')}»", "",
                  f"- video_prompt ({len(cap['video_prompt'])} caracteres): {cap['video_prompt']}",
                  f"- negative_prompt: {VEO_NEGATIVE_PROMPT}", f"- duration: {_veo_duration()}", ""]
        for i, it in enumerate(fs, start=1):
            tii = {}
            try:
                tii = (json.loads(it.get("raw_llm_prompt") or "{}") or {}).get("text_in_image") or {}
            except (TypeError, ValueError):
                pass
            notas = [*(it.get("_f8_slots_scrub") or []), *(it.get("_f8_problemas") or []),
                     *[f"texto legible: {s}" for s in it.get("_f8_texto_fuera") or []]]
            fila = {"cap": n, "foto": i, "rol": it["_rol"], "ancla": it.get("narration_anchor"), "beat": it.get("beat"),
                    "anio": it.get("anio"), "anio_fuente": it.get("anio_fuente"),
                    "people_group": it.get("people_group") or [], "plano": _plano(it), "prompt": it.get("prompt"),
                    "notas_f8": notas, "rehecha": it.get("_f8_rehecha"),
                    "cartel": tii.get("text") if tii.get("present") else None}
            filas.append(fila)
            L += [f"### Cap {n} · foto {i}" + (" (primer cuadro del clip Veo)" if it["_rol"] != "foto" else ""), "",
                  f"- Ancla: «{fila['ancla']}»", f"- Beat: {fila['beat']} · año **{fila['anio']}** ({fila['anio_fuente']})",
                  f"- people_group: {', '.join(fila['people_group']) or '—'} · plano: {fila['plano']}",
                  f"- Prompt ({len(fila['prompt'] or '')} caracteres): {fila['prompt']}",
                  f"- Notas F8: {'; '.join(notas) or '—'}",
                  f"- Rehecha: {fila['rehecha'] or 'no'}", ""]
        caps.append({"cap": n, "fotos": len(fs), "antes": n_antes.get(n), "video_prompt": cap.get("video_prompt"),
                     "veo_position": cap.get("veo_position")})
    total, total_antes = sum(c["fotos"] for c in caps), sum(n_antes.values())
    fuentes = Counter((f["anio_fuente"] or "?") for f in filas)
    rehechas_cap = [f for f in filas if f["rehecha"]]
    rv = (v.get("_f8_imagenes") or {}).get("rehechas") or []
    carteles = [f for f in filas if f["cartel"]]
    co = costos()
    L += ["## Resumen", "", "| cap | fotos | antes |", "|---|---:|---:|"]
    L += [f"| {c['cap']} | {c['fotos']} | {c['antes']} |" for c in caps]
    L += [f"| **total** | **{total}** | **{total_antes}** |", "",
          f"El número de fotos {'no cambia' if total == total_antes else f'cambia: {total_antes} → {total}'} "
          "(las anclas se re-planean en cada corrida).", "", "**Años por fuente**", ""]
    L += [f"- {k}: {n}" for k, n in sorted(fuentes.items())]
    L += ["", f"**Re-hechuras:** {len(rehechas_cap)} fotos quedaron rehechas (marca `_f8_rehecha`); "
          f"la pasada del video rehízo {len(rv)}.", ""]
    L += [f"- cap {f['cap']} foto {f['foto']}: {f['rehecha'][:160]}" for f in rehechas_cap]
    L += ["", f"**Carteles:** {len(carteles)}", ""]
    for f in carteles:
        frase = next((s for s in (f["prompt"] or "").split(". ") if f'"{f["cartel"]}"' in s), "")
        L.append(f"- cap {f['cap']} foto {f['foto']}: «{f['cartel']}» → {frase}")
    L += ["", f"**Costos reales** (cost_history, último registro de `{TID}`, {co['registro']}): total US$ {co['total']}",
          "", "| servicio · descripción | llamadas | US$ |", "|---|---:|---:|"]
    L += [f"| {k} | {x['llamadas']} | {x['usd']} |" for k, x in co["por_servicio"].items()]
    L += ["", f"Pasos en `01_v3_costos.json`: {co['pasos_01_v3_costos']}", ""]
    (F50 / "PAPEL_FOTOS_WITTENOOM.md").write_text("\n".join(L), encoding="utf-8")
    (F50 / "PAPEL_FOTOS_WITTENOOM.json").write_text(json.dumps(
        {"caps": caps, "fotos": filas, "fuentes_anio": fuentes, "rehechas_video": rv, "costos": co,
         "negative_prompt": VEO_NEGATIVE_PROMPT, "duration": _veo_duration()}, ensure_ascii=False, indent=1),
        encoding="utf-8")
    print(f"fotos {total} (antes {total_antes}) · fuentes {dict(fuentes)} · rehechas {len(rehechas_cap)} "
          f"(video {len(rv)}) · carteles {len(carteles)} · US$ {co['total']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
