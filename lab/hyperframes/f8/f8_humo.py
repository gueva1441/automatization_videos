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
        if r.get("f8_png") and Path(r["f8_png"]).exists():          # F8b: la versión F8 de una imagen rehecha
            r["f8_jpg"] = _jpg(r["f8_png"], HUMO / f"v3_{r['n']:02d}_f8.jpg")
        if r.get("png") and Path(r["png"]).exists():
            r["jpg"] = _jpg(r["png"], HUMO / f"v3_{r['n']:02d}.jpg")
        if r.get("graded_png") and Path(r["graded_png"]).exists():
            r["f8b_jpg"] = _jpg(r["graded_png"], HUMO / f"f8b_{r['n']:02d}.jpg")
        if r.get("v2_png") and Path(r["v2_png"]).exists():
            r["v2_jpg"] = _jpg(r["v2_png"], HUMO / f"v2_{r['n']:02d}.jpg")
    # hojas de contactos (4 × 3): F8 (la v3 de la primera tanda) y F8b (reglas nuevas + grade)
    W, H = 480, 270
    for name, key in (("hoja_contactos.jpg", "f8"), ("hoja_contactos_f8b.jpg", "f8b")):
        if key == "f8b" and not any(r.get("f8b_jpg") for r in rows):
            continue
        sheet = Image.new("RGB", (W * 4, (H + 22) * 3), (12, 12, 12))
        d = ImageDraw.Draw(sheet)
        for k, r in enumerate(rows[:12]):
            x, y = (k % 4) * W, (k // 4) * (H + 22)
            j = (r.get("f8_jpg") or r.get("jpg")) if key == "f8" else r.get("f8b_jpg")
            if j:
                im = Image.open(HUMO / j)
                im.thumbnail((W, H))
                sheet.paste(im, (x, y))
            tag = (" REHECHA" if key == "f8b" and r.get("f8_png") else "")
            d.text((x + 4, y + H + 4), f"{r['n']:02d} cap{r['cap']} beat{r['beat']}{' PICO' if r['cerrada'] else ''}"
                                       f"{' SENSIBLE' if r.get('sensible') else ''}{tag}", fill=(230, 230, 230))
        sheet.save(HUMO / name, "JPEG", quality=85)
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
<div class="pair{' tri' if r.get('f8b_jpg') else ''}">{img(r.get('v2_jpg'), 'v2 (F5, Seedream 4.5)')}{img(r.get('f8_jpg') or r.get('jpg'), "v3 (F8, 5.0 Lite)")}{img(r.get('f8b_jpg'), ('F8b: rehecha con las reglas nuevas + grade' if r.get('f8_png') else 'F8b: misma imagen + grade')) if r.get('f8b_jpg') else ''}</div>
<details><summary>prompts</summary><p><b>v2</b> {html.escape(r.get('v2_prompt') or '')}</p><p><b>v3 F8</b> {html.escape(r.get('f8_prompt') or r['prompt'])}</p>{('<p><b>F8b</b> ' + html.escape(r['prompt']) + '</p>') if r.get('f8_png') else ''}
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
.pair.tri{{grid-template-columns:1fr 1fr 1fr}}
details p{{font-size:13px;color:#cfcfcf}} @media (max-width:700px){{.pair,.pair.tri{{grid-template-columns:1fr}}}}
</style></head><body><main><h1>Imágenes F8 / F8b: Orleans v2 · v3 F8 · F8b</h1>
<p>12 imágenes de la escaleta f7r3. Columnas: la foto de v2 en la misma posición relativa del mismo cap; la v3 de F8
(Seedream 5.0 Lite); F8b: #3, #7, #8, #9 y #10 rehechas con las reglas nuevas (armas, pico humano, texto, escala) y
las 12 con el grade de post. Detalle en <code>humo/HUMO.md</code>.</p>{''.join(cards)}{edit_card}</main></body></html>"""
    (LAB / "compara_imagenes_f8.html").write_text(page, encoding="utf-8")


def rehacer(n: int, data: list[dict], note: str | None = None, label: str = "rehecha tras arreglar el respaldo (F8)"
            ) -> None:
    """Rehace la imagen `n` (prompt con el código actual, mismo ancla y beat) y la vuelve a generar."""
    from script_engine import m03_imagenes_v3 as v3
    from script_engine import m03_visual as m3
    from script_engine.m01a_skeleton import STEPS_DIR
    r = next(x for x in data[1:] if x["n"] == n)
    topic = _topic()
    beats = v3.load_beats(topic, STEPS_DIR)
    f8 = {"beats": beats, "year": v3.topic_year(topic, beats), "refill": True, "lang": v3.place_language(topic),
          "force_assign": [{"beat": r["beat"], "cerrada": r["cerrada"]}], **({"note": note} if note else {})}
    narr = json.loads((STEPS_DIR / TOPIC / "01b_narracion_v3.json").read_text(encoding="utf-8"))
    esc = json.loads((STEPS_DIR / TOPIC / "01a_escaleta.json").read_text(encoding="utf-8"))
    cap_txt = next(c["narration"] for c in narr["caps"] if c["chapter_number"] == r["cap"])
    cap_data = {**next(c for c in esc["caps"] if c["chapter_number"] == r["cap"]),
                "bullets": [f"{b['imagen_sensorial']} · {b['dato_texto']}" for b in beats[r["cap"]]]}
    it = m3._render_prompts_seedream({**topic, "_f8": f8}, cap_data, cap_txt, {"anchors": [{"anchor": r["anchor"]}]},
                                     r["cap"])["image_prompts"][0]
    r.update({"prompt_anterior": r["prompt"], "prompt": it["prompt"], "shot_scale": it.get("shot_scale"),
              "sensible": it.get("sensible"), "motivos": it.get("motivos"), "problemas": it.get("_f8_problemas") or [],
              "slots_scrub": it.get("_f8_slots_scrub") or [], "rehecha": label,
              "texto_en_imagen": it.get("texto_en_imagen")})
    old = data[0].get("_costo_imagenes_usd") or 0.0
    generate([r])
    data[0]["_costo_imagenes_usd"] = round(old + (r.pop("_costo_imagenes_usd", 0.0) or 0.0), 4)
    r.pop("_pared_s", None)


def f8b(ns: list[int], data: list[dict]) -> None:
    """F8b §2.7: rehace `ns` con las reglas nuevas (la versión F8 queda en *_f8.png) y aplica el grade a las 12."""
    import shutil

    from script_engine import image_grade
    from script_engine import m03_visual as m3
    for r in data[1:]:
        if r["n"] in ns and not r.get("f8_png"):
            p = Path(r["png"])
            f8p = p.with_name(f"{p.stem}_f8{p.suffix}")
            shutil.copy2(p, f8p)
            r.update({"f8_png": str(f8p), "f8_prompt": r["prompt"], "f8_ms": r.get("ms")})
            rehacer(r["n"], data, note=m3.F8_NOTE_CERRADA if r["cerrada"] else None,
                    label="rehecha en F8b con las reglas nuevas")
            print(f"  F8b #{r['n']}: {r.get('estado')} {r.get('ms')} ms", flush=True)
    prm = image_grade.params()
    for r in data[1:]:
        if r.get("png") and Path(r["png"]).exists():
            r["graded_png"] = str(image_grade.grade(Path(r["png"]), prm, overwrite=True))
            a, b = image_grade.stats(Path(r["png"])), image_grade.stats(Path(r["graded_png"]))
            r["grade_stats"] = {"sat_antes": round(a["sat_media"], 3), "sat_despues": round(b["sat_media"], 3),
                                "negro_puro_antes": round(a["negro_puro_pct"], 2),
                                "negro_puro_despues": round(b["negro_puro_pct"], 2)}
    data[0]["_grade"] = prm


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
    if "--f8b" in a:
        data = json.loads((HUMO / "humo.json").read_text(encoding="utf-8"))
        f8b([int(x) for x in a[a.index("--f8b") + 1].split(",")], data)
        build_outputs(data)
        return
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
