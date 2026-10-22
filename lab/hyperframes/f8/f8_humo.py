"""F8 §1 G: corrida de humo — 12 imágenes de Orleans f7r3 con las reglas nuevas y Seedream 5.0 Lite (sin render).

Uso: python -I lab/hyperframes/f8/f8_humo.py [--solo-prompts] [--solo-html]
    --solo-prompts  arma los 12 prompts (m03 v3, Pro + Flash) y no genera imágenes
    --solo-html     rehace la hoja de contactos, HUMO.md y compara_imagenes_f8.html desde humo.json
Elige 12 imágenes sobre los 8 beats de la escaleta f7r3 (todos los beats, el pico con 2 y una de ellas la más cerrada,
el gancho con 2; las otras 2 a los beats más intensos). Las anclas son frases de la narración v3 repartidas dentro del
párrafo de cada beat (el plan de anclas de m03 necesita los timestamps del TTS, que f7r3 no tiene). Los prompts salen
de `m03_visual._render_prompts_seedream` con el camino v3 (beats, estilo, reglas) y la pasada de video `_f8_fix_video`.
Las fotos de v2 (misma posición relativa en el mismo cap) salen de output/ba6c3cac-f5v2.
Salidas: PNG completos en output/ba6c3cac-f7r3/humo_f8/ (fuera de git); JPG livianos, humo.json, HUMO.md,
hoja_contactos.jpg y ../compara_imagenes_f8.html en lab/hyperframes/f8/humo/.
"""
from __future__ import annotations

import html
import json
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
LAB = Path(__file__).resolve().parent
HUMO = LAB / "humo"
TOPIC = "ba6c3cac-f7r3"
V2 = "ba6c3cac-f5v2"
# imágenes por beat (12): gancho 2, pico 2, los más intensos (4: escalada 4 · 7: revelación 3) 2
PICKS = {1: 2, 2: 1, 3: 1, 4: 2, 5: 2, 6: 1, 7: 2, 8: 1}


def _sentences(t: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?…»])\s+", t or "") if len(s.split()) >= 4]


def _topic() -> dict:
    from config import DATA_DIR
    db = json.loads((DATA_DIR / "topics_db.json").read_text(encoding="utf-8"))
    ts = db["topics"] if isinstance(db, dict) and "topics" in db else db
    ts = ts if isinstance(ts, list) else list(ts.values())
    return next(t for t in ts if (t.get("id") or t.get("topic_id")) == TOPIC)


def build_prompts() -> list[dict]:
    from script_engine import m03_imagenes_v3 as v3
    from script_engine import m03_visual as m3
    from script_engine.m01a_skeleton import STEPS_DIR
    topic = _topic()
    beats = v3.load_beats(topic, STEPS_DIR)
    topic = {**topic, "_f8": {"beats": beats, "year": v3.topic_year(topic, beats)}}
    narr = json.loads((STEPS_DIR / TOPIC / "01b_narracion_v3.json").read_text(encoding="utf-8"))
    esc = json.loads((STEPS_DIR / TOPIC / "01a_escaleta.json").read_text(encoding="utf-8"))
    caps_txt = {c["chapter_number"]: c["narration"] for c in narr["caps"]}
    skel = {c["chapter_number"]: c for c in esc["caps"]}
    plans: dict[int, list[str]] = {}
    for cap, bs in sorted(beats.items()):
        for b in bs:
            ss = [s for p in b["parrafos"] for s in _sentences(p)]
            k = PICKS.get(b["n"], 1)
            pos = [round(j * (len(ss) - 1) / max(1, k - 1)) for j in range(k)] if k > 1 else [0]
            plans.setdefault(cap, []).extend(ss[i] for i in dict.fromkeys(pos))

    def _cap(cap: int) -> tuple[int, dict, dict]:
        bs = beats[cap]
        cap_data = {**skel[cap], "title": esc.get("promesa_gancho") if cap == 1 else "",
                    "bullets": [f"{b['imagen_sensorial']} · {b['dato_texto']}" for b in bs]}
        out = m3._render_prompts_seedream(topic, cap_data, caps_txt[cap], {"anchors": [{"anchor": a} for a in plans[cap]]},
                                          cap)
        return cap, cap_data, out
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=7) as ex:
        res = {cap: (cd, out) for cap, cd, out in ex.map(_cap, sorted(plans))}
    items_by_cap = {cap: out["image_prompts"] for cap, (_, out) in res.items()}
    fix = m3._f8_fix_video(topic, {c: cd for c, (cd, _) in res.items()},
                           {c: {"narration": caps_txt[c]} for c in res}, items_by_cap)
    rows = []
    for cap in sorted(items_by_cap):
        for it in items_by_cap[cap]:
            k = caps_txt[cap].find(it["narration_anchor"][:40])
            rows.append({"cap": cap, "beat": it.get("beat"), "cerrada": it.get("cerrada", False),
                         "anchor": it["narration_anchor"], "pos": round(max(0, k) / max(1, len(caps_txt[cap])), 3),
                         "prompt": it["prompt"], "shot_scale": it.get("shot_scale"), "subject_ref": it.get("subject_ref"),
                         "foto_madre_ref": it.get("foto_madre_ref") or [], "sensible": it.get("sensible"),
                         "motivos": it.get("motivos"), "problemas": it.get("_f8_problemas") or [],
                         "slots_scrub": it.get("_f8_slots_scrub") or [], "rehecha": it.get("_f8_rehecha")})
    for i, r in enumerate(rows, start=1):
        r["n"] = i
    return [{"_auditoria": fix, "_segundos_prompts": round(time.time() - t0, 1)}] + rows


def old_v2(rows: list[dict]) -> None:
    from config import DATA_DIR, OUTPUT_DIR
    s = json.loads((DATA_DIR / "scripts" / f"{V2}.json").read_text(encoding="utf-8"))
    for r in rows:
        ch = s["chapters"][r["cap"] - 1]
        if ch.get("image_prompts") and ch.get("render_engine") == "flux":
            lst = [(p.get("prompt") if isinstance(p, dict) else p, f"ch{r['cap']:02d}_flux/ch{r['cap']:02d}_img_{k:02d}.png")
                   for k, p in enumerate(ch["image_prompts"], start=1)]
        else:
            lst = [(p.get("prompt"), f"ch{r['cap']:02d}_flux/ch{r['cap']:02d}_supp_{k:02d}.png")
                   for k, p in enumerate(ch.get("supplemental_image_prompts") or [], start=1)]
        k = min(len(lst) - 1, int(r["pos"] * len(lst)))
        r["v2_prompt"], rel = lst[k]
        r["v2_png"] = str(OUTPUT_DIR / V2 / "assets" / rel)


def generate(rows: list[dict]) -> None:
    import asset_manager as am
    from config import OUTPUT_DIR
    from cost_tracker import cost_tracker
    s = json.loads((ROOT / "data" / "scripts" / f"{V2}.json").read_text(encoding="utf-8"))
    madre = {k: am._path_to_data_uri(v) for k, v in (s.get("foto_madre_registry") or {}).items() if Path(v).exists()}
    out_dir = OUTPUT_DIR / TOPIC / "humo_f8"
    cost_tracker.start_video(f"{TOPIC}-humo-f8")

    def _one(r: dict) -> None:
        uris = [madre[x] for x in r["foto_madre_ref"] if x in madre]
        p = out_dir / f"{r['n']:02d}_cap{r['cap']}_beat{r['beat']}.png"
        try:
            meta = am._generate_image_raw(r["prompt"], p, False, None, uris or None)
            r.update({"png": str(p), "endpoint": meta["endpoint"], "ms": meta.get("ms"), "estado": "ok",
                      "nsfw": meta.get("nsfw_flag"), "w": meta.get("width"), "h": meta.get("height")})
        except Exception as e:  # noqa: BLE001
            r.update({"estado": f"error: {type(e).__name__}: {str(e)[:200]}"})
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=12) as ex:
        list(ex.map(_one, rows))
    rep = cost_tracker.end_video()
    rows[0]["_pared_s"] = round(time.time() - t0, 1)
    rows[0]["_costo_imagenes_usd"] = round(getattr(rep, "total_cost", 0.0) or 0.0, 4)


def _jpg(src: str, dst: Path, w: int = 960) -> str:
    from PIL import Image
    im = Image.open(src).convert("RGB")
    im.thumbnail((w, w))
    dst.parent.mkdir(parents=True, exist_ok=True)
    im.save(dst, "JPEG", quality=84)
    return dst.name


def build_outputs(data: list[dict]) -> None:
    from PIL import Image, ImageDraw
    meta, rows = data[0], data[1:]
    for r in rows:
        if r.get("png") and Path(r["png"]).exists():
            r["jpg"] = _jpg(r["png"], HUMO / f"v3_{r['n']:02d}.jpg")
        if r.get("v2_png") and Path(r["v2_png"]).exists():
            r["v2_jpg"] = _jpg(r["v2_png"], HUMO / f"v2_{r['n']:02d}.jpg")
    # hoja de contactos (4 × 3, v3)
    W, H = 480, 270
    sheet = Image.new("RGB", (W * 4, (H + 22) * 3), (12, 12, 12))
    d = ImageDraw.Draw(sheet)
    for k, r in enumerate(rows[:12]):
        x, y = (k % 4) * W, (k // 4) * (H + 22)
        if r.get("jpg"):
            im = Image.open(HUMO / r["jpg"])
            im.thumbnail((W, H))
            sheet.paste(im, (x, y))
        d.text((x + 4, y + H + 4), f"{r['n']:02d} cap{r['cap']} beat{r['beat']}{' PICO' if r['cerrada'] else ''}"
                                   f"{' SENSIBLE' if r.get('sensible') else ''} {r.get('ms') or '-'} ms",
               fill=(230, 230, 230))
    sheet.save(HUMO / "hoja_contactos.jpg", "JPEG", quality=85)
    (HUMO / "humo.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    # tabla
    ok = [r for r in rows if r.get("estado") == "ok"]
    ms = sorted(r["ms"] for r in ok if r.get("ms"))
    lines = ["# Corrida de humo F8 — 12 imágenes de Orleans f7r3 (Seedream 5.0 Lite)", "",
             f"- Imágenes OK: {len(ok)}/{len(rows)} · costo medido (cost_tracker): US$ {meta.get('_costo_imagenes_usd')} · "
             f"pared {meta.get('_pared_s')} s con 12 en paralelo · prompts (Pro + Flash) {meta.get('_segundos_prompts')} s",
             f"- ms por imagen: mín {ms[0] if ms else '-'} · mediana {ms[len(ms) // 2] if ms else '-'} · máx "
             f"{ms[-1] if ms else '-'}",
             f"- Auditoría de video (antes → después de la pasada): `{json.dumps(meta['_auditoria']['antes'], ensure_ascii=False)}` → "
             f"`{json.dumps(meta['_auditoria']['despues'], ensure_ascii=False)}`; rehechas: {len(meta['_auditoria']['rehechas'])}",
             "", "| # | cap · beat | endpoint | ms | flags | prompt v2 (misma posición) | prompt v3 |", "|---|---|---|---|---|---|---|"]
    for r in rows:
        flags = ", ".join(x for x in [("pico/cerrada" if r["cerrada"] else ""), ("sensible" if r.get("sensible") else ""),
                                      ("motivos " + "/".join(r.get("motivos") or []) if r.get("motivos") else ""),
                                      (f"arreglos {len(r['problemas'])}" if r["problemas"] else ""),
                                      (f"slots limpiados {len(r['slots_scrub'])}" if r["slots_scrub"] else ""),
                                      ("rehecha" if r.get("rehecha") else ""), ("/edit" if "edit" in (r.get("endpoint") or "") else "")]
                          if x) or "—"
        lines.append(f"| {r['n']} | {r['cap']} · {r['beat']} | `{(r.get('endpoint') or r.get('estado') or '').split('/')[-2:]}` | "
                     f"{r.get('ms') or '-'} | {flags} | {(r.get('v2_prompt') or '')[:260]}… | {r['prompt'][:420]}… |")
    (HUMO / "HUMO.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    # página antes/después
    cards = []
    for r in rows:
        def img(name, label):
            return (f'<figure><img src="humo/{name}" loading="lazy"><figcaption>{label}</figcaption></figure>'
                    if name else f'<figure class="none"><figcaption>{label}: sin imagen</figcaption></figure>')
        cards.append(f"""<section class="card"><h2>#{r['n']:02d} · cap {r['cap']} · beat {r['beat']}
{'<span class="tag">pico · la más cerrada</span>' if r['cerrada'] else ''}{'<span class="tag warn">sensible</span>' if r.get('sensible') else ''}</h2>
<p class="anchor">«{html.escape(r['anchor'])}»</p>
<div class="pair">{img(r.get('v2_jpg'), 'v2 (F5, Seedream 4.5)')}{img(r.get('jpg'), f"v3 (F8, 5.0 Lite · {r.get('ms') or '-'} ms)")}</div>
<details><summary>prompts</summary><p><b>v2</b> {html.escape(r.get('v2_prompt') or '')}</p><p><b>v3</b> {html.escape(r['prompt'])}</p>
{'<p><b>arreglos</b> ' + html.escape('; '.join(r['problemas'] + r['slots_scrub'])) + '</p>' if r['problemas'] or r['slots_scrub'] else ''}</details></section>""")
    ep = meta.get("_edit_probe") or {}
    edit_card = (f"""<section class="card"><h2>Foto madre por /edit de v5 Lite ({html.escape(ep.get('estado') or '')},
{ep.get('ms') or '-'} ms)</h2><p class="anchor">{html.escape(ep.get('endpoint') or '')}</p><div class="pair">
<figure><img src="humo/edit_probe_madre.jpg"><figcaption>foto madre (referencia)</figcaption></figure>
<figure><img src="humo/edit_probe.jpg"><figcaption>v5 Lite /edit</figcaption></figure></div>
<details><summary>prompt</summary><p>{html.escape(ep.get('prompt') or '')}</p></details></section>"""
                 if ep.get("jpg") else "")
    page = f"""<!doctype html><html lang="es"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Imágenes F8 antes y después</title><style>
:root{{--bg:#111;--fg:#e8e8e8;--mute:#9a9a9a;--card:#1b1b1b;--acc:#c2302f}}
body{{margin:0;background:var(--bg);color:var(--fg);font:15px/1.45 system-ui,sans-serif}}
main{{max-width:1500px;margin:0 auto;padding:16px}} h1{{font-size:22px}} .card{{background:var(--card);border-radius:8px;padding:12px;margin:14px 0}}
.card h2{{font-size:16px;margin:0 0 6px}} .anchor{{color:var(--mute);margin:0 0 8px}} .pair{{display:grid;grid-template-columns:1fr 1fr;gap:10px}}
figure{{margin:0}} img{{width:100%;border-radius:4px;display:block}} figcaption{{color:var(--mute);font-size:13px;margin-top:4px}}
.tag{{background:var(--acc);color:#fff;font-size:12px;padding:1px 6px;border-radius:3px;margin-left:8px}} .tag.warn{{background:#8a6d00}}
details p{{font-size:13px;color:#cfcfcf}} @media (max-width:700px){{.pair{{grid-template-columns:1fr}}}}
</style></head><body><main><h1>Imágenes F8: Orleans v2 (izquierda) contra v3 con Seedream 5.0 Lite (derecha)</h1>
<p>12 imágenes de la escaleta f7r3; a la izquierda, la foto de v2 en la misma posición relativa del mismo cap. Detalle en
<code>humo/HUMO.md</code>.</p>{''.join(cards)}{edit_card}</main></body></html>"""
    (LAB / "compara_imagenes_f8.html").write_text(page, encoding="utf-8")


def rehacer(n: int, data: list[dict]) -> None:
    """Rehace la imagen `n` (prompt con el código actual, mismo ancla y beat) y la vuelve a generar."""
    from script_engine import m03_imagenes_v3 as v3
    from script_engine import m03_visual as m3
    from script_engine.m01a_skeleton import STEPS_DIR
    r = next(x for x in data[1:] if x["n"] == n)
    topic = _topic()
    beats = v3.load_beats(topic, STEPS_DIR)
    f8 = {"beats": beats, "year": v3.topic_year(topic, beats), "refill": True,
          "force_assign": [{"beat": r["beat"], "cerrada": r["cerrada"]}]}
    narr = json.loads((STEPS_DIR / TOPIC / "01b_narracion_v3.json").read_text(encoding="utf-8"))
    esc = json.loads((STEPS_DIR / TOPIC / "01a_escaleta.json").read_text(encoding="utf-8"))
    cap_txt = next(c["narration"] for c in narr["caps"] if c["chapter_number"] == r["cap"])
    cap_data = {**next(c for c in esc["caps"] if c["chapter_number"] == r["cap"]),
                "bullets": [f"{b['imagen_sensorial']} · {b['dato_texto']}" for b in beats[r["cap"]]]}
    it = m3._render_prompts_seedream({**topic, "_f8": f8}, cap_data, cap_txt, {"anchors": [{"anchor": r["anchor"]}]},
                                     r["cap"])["image_prompts"][0]
    r.update({"prompt_anterior": r["prompt"], "prompt": it["prompt"], "shot_scale": it.get("shot_scale"),
              "sensible": it.get("sensible"), "motivos": it.get("motivos"), "problemas": it.get("_f8_problemas") or [],
              "slots_scrub": it.get("_f8_slots_scrub") or [], "rehecha": "rehecha tras arreglar el respaldo (F8)"})
    old = data[0].get("_costo_imagenes_usd") or 0.0
    generate([r])
    data[0]["_costo_imagenes_usd"] = round(old + (r.pop("_costo_imagenes_usd", 0.0) or 0.0), 4)
    r.pop("_pared_s", None)


def probar_edit(data: list[dict]) -> None:
    """Una imagen por el /edit de v5 Lite con la foto madre de Orleans (el humo no eligió ninguna con ancla)."""
    import asset_manager as am
    from config import OUTPUT_DIR
    from cost_tracker import cost_tracker
    s = json.loads((ROOT / "data" / "scripts" / f"{V2}.json").read_text(encoding="utf-8"))
    madre = s["foto_madre_registry"]["__subject__"]
    from script_engine import m03_imagenes_v3 as v3
    prompt = v3.wrap_style("An extreme wide aerial view of the Orleans Parish Prison complex surrounded by dark "
                           "floodwater after the hurricane, overcast sky, the city flooded around it. The image has a "
                           "16:9 aspect ratio.", "2005")
    p = OUTPUT_DIR / TOPIC / "humo_f8" / "edit_probe.png"
    cost_tracker.start_video(f"{TOPIC}-humo-f8-edit")
    try:
        meta = am._generate_image_raw(prompt, p, False, None, [am._path_to_data_uri(madre)])
        res = {"estado": "ok", "endpoint": meta["endpoint"], "ms": meta.get("ms"), "png": str(p), "prompt": prompt,
               "foto_madre": madre}
        res["jpg"] = _jpg(str(p), HUMO / "edit_probe.jpg")
        _jpg(madre, HUMO / "edit_probe_madre.jpg")
    except Exception as e:  # noqa: BLE001
        res = {"estado": f"error: {type(e).__name__}: {str(e)[:300]}", "prompt": prompt}
    rep = cost_tracker.end_video()
    res["usd"] = round(getattr(rep, "total_cost", 0.0) or 0.0, 4)
    data[0]["_edit_probe"] = res
    print("edit:", res["estado"], res.get("endpoint"), res.get("ms"), flush=True)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")                # -I ignora PYTHONIOENCODING
    a = sys.argv[1:]
    HUMO.mkdir(parents=True, exist_ok=True)
    if "--rehacer" in a or "--probar-edit" in a:
        data = json.loads((HUMO / "humo.json").read_text(encoding="utf-8"))
        if "--rehacer" in a:
            rehacer(int(a[a.index("--rehacer") + 1]), data)
        if "--probar-edit" in a:
            probar_edit(data)
        build_outputs(data)
        return
    if "--solo-html" in a:
        data = json.loads((HUMO / "humo.json").read_text(encoding="utf-8"))
        build_outputs(data)
        return
    data = build_prompts()
    old_v2(data[1:])
    (HUMO / "humo.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"prompts: {len(data) - 1} · auditoría {json.dumps(data[0]['_auditoria']['despues'], ensure_ascii=False)}", flush=True)
    if "--solo-prompts" in a:
        return
    generate(data[1:])
    data[0].update({k: data[1].pop(k) for k in ("_pared_s", "_costo_imagenes_usd") if k in data[1]})
    build_outputs(data)
    print(f"imágenes: {sum(1 for r in data[1:] if r.get('estado') == 'ok')}/12 · US$ {data[0].get('_costo_imagenes_usd')}"
          f" · {data[0].get('_pared_s')} s", flush=True)


if __name__ == "__main__":
    main()
