"""F29c §B — Vajont v4 completo con el rotulista por beat, sobre la copia `f8s3-vajont-f30` (ya cocida por F30).

    prefetch   el rotulista de los 7 caps en paralelo (7 llamadas, tope Claude US$ 1.5 del handoff, ledger nuevo: el de
               F29b queda como `rotulista_costos.f29b.json`; las crudas de F29b como `rotulista_chNN.f29b.raw.json`).
    render     el video entero en fila: `fase2b --keep-segments --reuse-visuals --gfx --gfx-sparse --rotulista` (los
               chNN_gfx.mp4, logs, segmentos y planes resueltos de antes se apartan en `_bak_antes_de_v4/`; el
               rotulista sale de caché). Firefox cerrado y RAM libre > 14 GB antes (se aborta si no). Salida
               `output/f8s3-vajont-f30/f8s3-vajont_final_gfx_v4.mp4`.
    tabla      la tabla por cap de B.3 y las medidas de B.4 → `tabla.md`, `medidas.json`.
Uso: python -I lab/hyperframes/f29c/b/f29c_vajont.py prefetch | render | tabla
"""
from __future__ import annotations

import json
import os
import re
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT), str(ROOT / "lab" / "hyperframes" / "f30"), str(ROOT / "lab" / "hyperframes" / "f26" / "b")]
LAB = Path(__file__).resolve().parent
DST = "f8s3-vajont-f30"
OUT = ROOT / "output" / DST
WD = OUT / "_fase2b_work"
TOPE_F29C = 1.5            # HANDOFF_F29c §B.1: Claude ≤ US$ 1.5 para los planes
TOPE_TANDA = 2.0           # la tanda F29c + F30b + F31: Claude ≤ US$ 2 en total
CAPS = [f"ch{k:02d}" for k in range(1, 8)]


def _f30():
    import f30_vajont as f
    f.DST, f.W_DST, f.LAB = DST, WD, LAB
    return f


def _plans():
    import fase2b
    from config import OUTPUT_DIR
    ad = OUTPUT_DIR / "audio" / DST
    return fase2b._build_plans(json.loads((ad / "sync_map.json").read_text(encoding="utf-8")),
                               json.loads((OUTPUT_DIR / DST / "assets" / "assets_manifest.json").read_text(encoding="utf-8")),
                               DST, ad, fase2b._load_script_lookup(DST))


def prefetch() -> dict:
    for cap in CAPS:                                           # las crudas de F29b (otro prompt) quedan aparte
        f = WD / f"rotulista_{cap}.raw.json"
        dst = WD / f"rotulista_{cap}.f29b.raw.json"
        if f.exists() and not dst.exists():
            raw = json.loads(f.read_text(encoding="utf-8"))
            if raw.get("prompt_version") != "f29c-1":
                f.rename(dst)
    led = WD / "rotulista_costos.json"
    if led.exists() and not (WD / "rotulista_costos.f29b.json").exists():
        led.rename(WD / "rotulista_costos.f29b.json")
    from script_engine import gfx_intensity
    from script_engine import gfx_rotulista as gro
    gfx_intensity.record_proposals = lambda *a, **k: []      # no toca gfx_profiles/
    plans = _plans()
    t0 = time.time()
    pre = gro.prefetch(plans, DST, WD, {p.chapter_id: 0.0 for p in plans}, tope=TOPE_F29C)
    res = {"rotulista_paralelo_s": round(time.time() - t0, 1), "prefetch": pre, "tope": TOPE_F29C,
           "claude_usd": gro.gastado(WD), "prompt_md5": gro.prompt_md5()}
    (LAB / "prefetch.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False), flush=True)
    return res


def render() -> dict:
    from script_engine import gfx_rotulista as gro
    f = _f30()
    ram = f._guardia()
    bak = WD / "_bak_antes_de_v4"
    bak.mkdir(exist_ok=True)
    for x in (list(WD.glob("ch*_gfx.mp4")) + list(WD.glob("gfx_ch*.log")) + list(WD.glob("ch*_segment*.mp4"))
              + list(WD.glob("seg_*_ch*.mp4")) + list(WD.glob("gfx_plan_ch*.resolved.json"))):
        x.replace(bak / x.name)
    queda = round(TOPE_F29C - gro.gastado(WD), 4)
    rc, pared, ram_min = f._fase2b([DST, "--keep-segments", "--reuse-visuals", "--gfx", "--gfx-sparse", "--gfx-quality",
                                    "looks", "--rotulista", "--rotulista-tope", str(queda)], LAB / "render_v4.out")
    final = OUT / f"{DST}_final_gfx.mp4"
    v4 = OUT / "f8s3-vajont_final_gfx_v4.mp4"
    if rc == 0 and final.exists():
        final.replace(v4)
        nm = OUT / f"{DST}_final_gfx_no_music.mp4"
        if nm.exists():
            nm.replace(OUT / "f8s3-vajont_final_gfx_v4_no_music.mp4")
    res = {"rc": rc, "pared_min": round(pared / 60, 1), "salida": str(v4) if v4.exists() else None,
           "bytes": v4.stat().st_size if v4.exists() else None, "ram_libre_antes_gb": round(ram, 1),
           "ram_libre_min_gb": round(ram_min, 2) if ram_min else None, "claude_usd": gro.gastado(WD)}
    (LAB / "render_v4.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False), flush=True)
    return res


def _gfx_s(cap: str) -> dict:
    log = (WD / f"gfx_{cap}.log").read_text(encoding="utf-8") if (WD / f"gfx_{cap}.log").exists() else ""
    blk = log.split("\n[")[-1]

    def g(pat: str):
        return (re.findall(pat, blk) or [None])[-1]
    return {"gfx_total_s": g(r"OK total ([\d.]+)s"), "hf_s": g(r"6 lint \+ render looks \(sparse\): ([\d.]+)s"),
            "bake_s": g(r"4b safe bake \(ffmpeg\): ([\d.]+)s"), "stitch_s": g(r"7 stitch \+ grade FFmpeg: ([\d.]+)s")}


def tabla() -> dict:
    from script_engine import gfx_rotulista as gro
    from script_engine.gfx_project import GfxScene  # noqa: F401
    reglas = ("cantidad", "lectura", "no_dicho", "spoiler", "coherencia", "zona")
    filas, med = [], {"munones": [], "cifras_sin_etiqueta": [], "textos_en_pico": [], "dos_en_escena": [],
                      "cruzan_corte": [], "contradicciones": [], "a_pantalla": {}}
    costos = json.loads((WD / "rotulista_costos.json").read_text(encoding="utf-8"))
    for cap in CAPS:
        rp = WD / f"gfx_plan_{cap}.resolved.json"
        if not rp.exists():
            continue
        plan = json.loads(rp.read_text(encoding="utf-8"))["plan"]
        raw = json.loads((WD / f"rotulista_{cap}.raw.json").read_text(encoding="utf-8"))
        rot = plan.get("rotulista") or {}
        ent = raw["entrada"]
        beats = ent["beats"]
        pk = (ent.get("pico") or {}).get("beat")
        fil = rot.get("filas") or []
        esc = rot.get("escena") or []
        propuestos = len((raw.get("final") or {}).get("bloques") or [])
        fuera = {r: sum(1 for x in fil + esc if x.get("regla") == r and x.get("accion") == "fuera") for r in reglas}
        fuera["contenido (anclaje/forma/candado)"] = sum(1 for x in fil if x.get("regla") in ("anclaje", "forma", "candado"))
        fuera["ya_mostrado"] = sum(1 for x in fil if x.get("regla") == "ya_mostrado")
        crit = [r for r in plan.get("critico_rotulista") or []]
        cortados = [r for r in crit if not r["pasa"]]
        en_pantalla = []
        for c in plan.get("callouts") or []:
            if c.get("rotulista"):
                en_pantalla.append(("ficha", c))
        for a in plan.get("archive_clippings") or []:
            if a.get("rotulista"):
                en_pantalla.append(("documento", a))
        for k, nombre in (("quote_card", "cita"), ("evidence_zoom", "lupa")):
            if plan.get(k) and plan[k].get("rotulista"):
                en_pantalla.append((nombre, plan[k]))
        por_beat = {b["n"]: 0 for b in beats}
        for _, b in en_pantalla:
            por_beat[b["beat"]] = por_beat.get(b["beat"], 0) + 1
        anim = {b["n"]: [] for b in beats}

        def beat_en(t: float) -> int:
            for b in beats:
                if b["t0"] - 0.3 <= t <= b["t1"]:
                    return b["n"]
            prev = [b for b in beats if b["t0"] <= t]
            return (prev[-1] if prev else beats[0])["n"]
        for e in plan.get("emphasis") or []:
            anim[beat_en(float(e["start"]))].append("sello")
        if plan.get("time_ticker"):
            anim[beat_en(float(plan["time_ticker"]["start"]))].append("reloj")
        if plan.get("evidence_zoom"):
            anim[beat_en(float(plan["evidence_zoom"]["start"]))].append("lupa")
        # medidas B.4
        scenes = _escenas(cap)
        ocup: dict[int, list[str]] = {}
        for nombre, b in en_pantalla:
            txt = b.get("text") or b.get("headline") or b.get("detail") or ""
            et = b.get("kicker")
            if nombre != "lupa" and nombre != "cita" and gro.munon(txt):
                med["munones"].append(f"{cap} {txt}")
            if b.get("tipo_rotulista") == "cifra" and not et:
                med["cifras_sin_etiqueta"].append(f"{cap} {txt}")
            if pk is not None and b["beat"] == pk:
                med["textos_en_pico"].append(f"{cap} {b.get('pool_id')}")
            st = float(b["start"])
            en = st + float(b.get("duration") or 0) if nombre != "lupa" else st
            sc = next((s for s in scenes if s[0] <= st < s[1]), None)
            if sc:
                ocup.setdefault(sc[0], []).append(f"{b.get('pool_id')}")
                if nombre != "lupa" and en > sc[1] + 1e-3:
                    med["cruzan_corte"].append(f"{cap} {b.get('pool_id')} {st:.2f}–{en:.2f} corte {sc[1]:.2f}")
            contra = gro.contradicciones(f"{et or ''} {txt}", ent.get("voz_video") or [])
            if contra:
                med["contradicciones"].append(f"{cap} {b.get('pool_id')}: {contra}")
        med["dos_en_escena"] += [f"{cap} escena@{k:.2f}: {v}" for k, v in ocup.items() if len(v) > 1]
        for x in ent["items"]:
            if x["a_pantalla"]:
                sale = any(b.get("pool_id") == x["id"] for _, b in en_pantalla)
                motivo = None
                if not sale:
                    motivo = next((f"{r.get('regla')}: {r.get('motivo')}" for r in reversed(fil + esc)
                                   if r.get("pool_id") == x["id"] and r.get("accion") == "fuera"), None)
                    c = next((r for r in cortados if r.get("pool_id") == x["id"]), None)
                    if c:
                        motivo = (f"crítico: (1) {c.get('motivo_1')} · (2) {c.get('motivo_2')} · (3) "
                                  f"{c.get('motivo_3')}")
                    motivo = motivo or (rot.get("motivo_faltan") or {}).get(x["id"]) or "el rotulista no lo propuso"
                med["a_pantalla"][x["id"]] = {"cap": cap, "sale": sale, "motivo": motivo}
        cc = [c for c in costos["llamadas"] if c["cap"] == cap]
        filas.append({"cap": cap, "beats": " · ".join(f"{b['n']} {b['funcion']}" + (" (pico)" if b["n"] == pk else "")
                                                       for b in beats),
                      "textos_por_beat": " · ".join(f"{n}:{v}" for n, v in por_beat.items()),
                      "anim_por_beat": " · ".join(f"{n}:{'+'.join(v) or '0'}" for n, v in anim.items()),
                      "propuestos": propuestos, **{f"fuera_{k}": v for k, v in fuera.items()},
                      "cortados_critico": len(cortados), "en_pantalla": len(en_pantalla),
                      "intentos": len(raw.get("intentos") or []),
                      "claude_usd": round(sum(c["usd"] for c in cc), 4), "llamadas": len(cc),
                      **_gfx_s(cap),
                      "bloques": [{"tipo": b.get("tipo_rotulista"), "kicker": b.get("kicker"),
                                   "texto": b.get("text") or b.get("headline") or b.get("detail"),
                                   "pool_id": b.get("pool_id"), "t0": b.get("start"), "dur": b.get("duration"),
                                   "beat": b.get("beat"), "oracion": b.get("sentence_idx"), "palabra": b.get("word_idx"),
                                   "movido": b.get("movido") or b.get("movido_escena"),
                                   "critico": b.get("critico")} for _, b in en_pantalla]})
    res = {"filas": filas, "medidas": med, "claude_usd_total": costos["usd"]}
    (LAB / "medidas.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: (v if k != "filas" else len(v)) for k, v in res.items()}, ensure_ascii=False, indent=1))
    return res


def _escenas(cap: str) -> list[tuple[float, float]]:
    """Las escenas del cap como las armó apply_gfx (log del gfx: «escenas: N (0.00R2, 7.12R3, …)»)."""
    log = (WD / f"gfx_{cap}.log").read_text(encoding="utf-8") if (WD / f"gfx_{cap}.log").exists() else ""
    m = re.findall(r"  escenas: \d+ \(([^)]*)\)", log.split("\n[")[-1])
    if not m:
        return []
    st = [float(re.match(r"[\d.]+", x.strip()).group(0)) for x in m[-1].split(",")]
    dur = re.findall(r"base_clip_dur=([\d.]+)|clip ([\d.]+) s", log)
    end = 1e9
    return [(a, st[k + 1] if k + 1 < len(st) else end) for k, a in enumerate(st)]


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    os.chdir(ROOT)
    {"prefetch": prefetch, "render": render, "tabla": tabla}[sys.argv[1]]()
