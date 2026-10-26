"""F30b — Vajont v5: transiciones por relato, costura a negro, pre-roll del title card y chascada, sobre
`f8s3-vajont-f30` (el v4 de F29c). API 0: el rotulista sale de caché (su pedido imprime los tiempos sin el pre-roll) y
el crítico reusa el veredicto de v4 por identidad del bloque (`gfx_critic.clave_identidad`).

    identidad  carga en las cachés del crítico la clave por identidad de cada veredicto de v4 (planes resueltos de v4).
    render     `fase2b --keep-segments --reuse-visuals --gfx --gfx-sparse --rotulista`, en fila; lo de v4 se aparta en
               `_bak_v4/` (gfx, logs, segmentos, planes). Firefox cerrado y RAM > 14 GB. Salida `…_final_gfx_v5.mp4`.
    medidas    las 6 fronteras (10 cuadros alrededor, ningún plano que no sea negro), md5 de las voces, duración,
               desplazamiento de 3 bloques a cuadro, transiciones v4 → v5 con razón, tiempos → `medidas.json`.
    hoja       `COSTURAS_v5.jpg`: por frontera, 12 cuadros de la unión (negro → title card → primera imagen con voz).
Uso: python -I lab/hyperframes/f30b/f30b_vajont.py identidad | render | medidas | hoja
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
sys.path[:0] = [str(ROOT), str(ROOT / "lab" / "hyperframes" / "f30"), str(ROOT / "lab" / "hyperframes" / "f26" / "b")]
LAB = Path(__file__).resolve().parent
DST = "f8s3-vajont-f30"
OUT = ROOT / "output" / DST
WD = OUT / "_fase2b_work"
BAK = WD / "_bak_v4"
V4, V5 = OUT / "f8s3-vajont_final_gfx_v4.mp4", OUT / "f8s3-vajont_final_gfx_v5.mp4"
CAPS = [f"ch{k:02d}" for k in range(1, 8)]
FPS = 30
INTRO_S = 2.5                 # fase2b.INITIAL_SILENCE_SEC: el primer cuadro clonado al arranque del mp4 final


def _f30():
    import f30_vajont as f
    f.DST, f.W_DST, f.LAB = DST, WD, LAB
    return f


def identidad() -> dict:
    from script_engine.gfx_critic import PROMPT_VERSION_ROT, clave_identidad
    n = 0
    src = BAK if BAK.exists() else WD
    for cap in CAPS:
        rp = src / f"gfx_plan_{cap}.resolved.json"
        if not rp.exists():
            continue
        plan = json.loads(rp.read_text(encoding="utf-8"))["plan"]
        cache = WD / f"gfx_critic_rot_{cap}.json"
        data = json.loads(cache.read_text(encoding="utf-8")) if cache.exists() else {}
        for r in plan.get("critico_rotulista") or []:
            v = {k: r.get(k) for k in ("habla_de_eso", "motivo_1", "dice_algo_nuevo", "motivo_2", "estorba", "motivo_3")}
            if all(isinstance(v[k], bool) for k in ("habla_de_eso", "dice_algo_nuevo", "estorba")):
                data[clave_identidad(cap, r.get("pool_id"), r.get("texto"), r.get("aporta"), PROMPT_VERSION_ROT)] = v
                n += 1
        cache.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"veredictos del rotulista por identidad: {n}", flush=True)
    return {"rotulista": n}


def render() -> dict:
    from script_engine import gfx_rotulista as gro
    f = _f30()
    ram = f._guardia()
    BAK.mkdir(exist_ok=True)
    for x in (list(WD.glob("ch*_gfx.mp4")) + list(WD.glob("gfx_ch*.log")) + list(WD.glob("ch*_segment*.mp4"))
              + list(WD.glob("seg_*_ch*.mp4")) + list(WD.glob("gfx_plan_ch*.resolved.json"))):
        x.replace(BAK / x.name)
    identidad()
    usd0 = gro.gastado(WD)
    rc, pared, ram_min = f._fase2b([DST, "--keep-segments", "--reuse-visuals", "--gfx", "--gfx-sparse", "--gfx-quality",
                                    "looks", "--rotulista", "--rotulista-tope", str(round(2.0 - usd0, 4))],
                                   LAB / "b" / "render_v5.out")
    final = OUT / f"{DST}_final_gfx.mp4"
    if rc == 0 and final.exists():
        final.replace(V5)
        nm = OUT / f"{DST}_final_gfx_no_music.mp4"
        if nm.exists():
            nm.replace(OUT / "f8s3-vajont_final_gfx_v5_no_music.mp4")
    res = {"rc": rc, "pared_min": round(pared / 60, 1), "salida": str(V5) if V5.exists() else None,
           "bytes": V5.stat().st_size if V5.exists() else None, "ram_libre_antes_gb": round(ram, 1),
           "ram_libre_min_gb": round(ram_min, 2) if ram_min else None, "claude_usd_nuevo": round(gro.gastado(WD) - usd0, 5)}
    (LAB / "b" / "render_v5.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(res, ensure_ascii=False), flush=True)
    return res


def _dur(p: Path) -> float:
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(p)],
                       capture_output=True, text=True)
    return float(r.stdout.strip())


def _frames(p: Path, t0: float, n: int, w: int = 64, h: int = 36) -> np.ndarray:
    r = subprocess.run(["ffmpeg", "-v", "error", "-ss", f"{max(0.0, t0):.4f}", "-i", str(p), "-frames:v", str(n), "-vf",
                        f"scale={w}:{h},format=gray", "-f", "rawvideo", "-"], capture_output=True, timeout=300)
    return np.frombuffer(r.stdout, np.uint8).reshape(-1, h, w).astype(np.float32)


def offsets_v5() -> dict[str, float]:
    """Inicio de cada cap en el mp4 v5: la intro + la suma de los segmentos (las uniones a negro no solapan)."""
    off, t = {}, INTRO_S
    for cap in CAPS:
        off[cap] = round(t, 3)
        t += _dur(WD / f"seg_{CAPS.index(cap) + 1:02d}_{cap}.mp4")
    return off


def _plan(d: Path, cap: str) -> dict:
    return json.loads((d / f"gfx_plan_{cap}.resolved.json").read_text(encoding="utf-8"))["plan"]


def _aparece(seg: Path, t: float, box: tuple[float, float, float, float]) -> float | None:
    """El primer cuadro (en el segmento) donde cambia la zona del bloque, buscando desde t − 0.5 s: el bloque entra."""
    fr = _frames(seg, t - 0.5, 45, 256, 144)
    x0, y0, x1, y1 = (int(box[0] * 256), int(box[1] * 144), int(box[2] * 256), int(box[3] * 144))
    z = fr[:, y0:y1, x0:x1]
    d = np.abs(z[1:] - z[0]).mean(axis=(1, 2))
    k = int(np.argmax(d > 2.0)) if (d > 2.0).any() else None
    return None if k is None else round(t - 0.5 + (k + 1) / FPS, 3)


def medidas() -> dict:
    res: dict = {}
    # md5 de las voces
    antes = dict(ln.split(" *")[::-1] for ln in (LAB / "b" / "md5_voz_antes_v5.txt").read_text().split("\n") if ln.strip())
    ahora = {}
    for p in sorted((ROOT / "output" / "audio" / DST).glob("ch0*.mp3")):
        ahora[str(p.relative_to(ROOT)).replace("\\", "/")] = hashlib.md5(p.read_bytes()).hexdigest()
    res["md5_voz"] = {k: {"antes": antes.get(k), "despues": v, "igual": antes.get(k) == v} for k, v in ahora.items()}
    # duraciones
    d4, d5 = _dur(V4), _dur(V5)
    seg4 = {c: _dur(BAK / f"seg_{i + 1:02d}_{c}.mp4") for i, c in enumerate(CAPS)}
    seg5 = {c: _dur(WD / f"seg_{i + 1:02d}_{c}.mp4") for i, c in enumerate(CAPS)}
    res["duracion"] = {"v4": round(d4, 3), "v5": round(d5, 3), "v4_mas_7_title_dur": round(d4 + 7 * 3.0, 3),
                       "diferencia_v5_menos_v4": round(d5 - d4, 3),
                       "segmentos_v4": {c: round(v, 3) for c, v in seg4.items()},
                       "segmentos_v5": {c: round(v, 3) for c, v in seg5.items()},
                       "segmentos_v5_menos_v4": {c: round(seg5[c] - seg4[c], 3) for c in CAPS}}
    # fronteras (B.2): 10 cuadros alrededor de cada una, en el mp4 final
    off = offsets_v5()
    fr = []
    for k in range(1, 7):
        c = off[CAPS[k]]
        f = _frames(V5, c - 5 / FPS, 10)
        mu, sd = f.mean(axis=(1, 2)), f.std(axis=(1, 2))
        planos = [{"cuadro": j - 5, "luma": round(float(mu[j]), 1), "desvio": round(float(sd[j]), 2)}
                  for j in range(len(f)) if sd[j] < 6.0 and mu[j] >= 30]
        fr.append({"frontera": f"{CAPS[k - 1]}→{CAPS[k]}", "t_mp4": c, "lumas": [round(float(x), 1) for x in mu],
                   "planos_no_negros": planos})
    res["fronteras"] = fr
    # pre-roll: el primer cuadro con voz de cada cap = 3 s después del inicio del segmento; plan gfx corrido 3 s
    desp = []
    for c in CAPS:
        p4, p5 = _plan(BAK, c), _plan(WD, c)
        for k in ("callouts", "archive_clippings"):
            for b5 in p5.get(k) or []:
                b4 = next((x for x in p4.get(k) or [] if x.get("pool_id") == b5.get("pool_id")
                           and (x.get("text") or x.get("headline")) == (b5.get("text") or b5.get("headline"))), None)
                if b4:
                    desp.append({"cap": c, "bloque": k, "pool_id": b5.get("pool_id"), "t_v4": b4["start"],
                                 "t_v5": b5["start"], "delta_plan": round(b5["start"] - b4["start"], 3)})
        for k in ("time_ticker", "chapter_question", "black_hold", "quote_card", "evidence_zoom"):
            if p4.get(k) and p5.get(k) and "start" in p4[k]:
                desp.append({"cap": c, "bloque": k, "t_v4": p4[k]["start"], "t_v5": p5[k]["start"],
                             "delta_plan": round(p5[k]["start"] - p4[k]["start"], 3),
                             "dur_v4": p4[k].get("duration"), "dur_v5": p5[k].get("duration")})
        for e4, e5 in zip(p4.get("emphasis") or [], p5.get("emphasis") or []):
            desp.append({"cap": c, "bloque": "sello", "t_v4": e4["start"], "t_v5": e5["start"],
                         "delta_plan": round(e5["start"] - e4["start"], 3)})
    res["desplazamiento_plan"] = desp
    # a cuadro en los segmentos: la ficha / el recorte entra 90 cuadros después
    medidos = []
    for d in desp:
        if d["bloque"] in ("callouts", "archive_clippings") and len(medidos) < 3:
            i = CAPS.index(d["cap"]) + 1
            box = (0.05, 0.22, 0.75, 0.48) if d["bloque"] == "callouts" else (0.05, 0.05, 0.95, 0.95)
            a4 = _aparece(BAK / f"seg_{i:02d}_{d['cap']}.mp4", float(d["t_v4"]), box)
            a5 = _aparece(WD / f"seg_{i:02d}_{d['cap']}.mp4", float(d["t_v5"]), box)
            medidos.append({**d, "aparece_seg_v4": a4, "aparece_seg_v5": a5,
                            "delta_cuadros": round((a5 - a4) * FPS) if a4 is not None and a5 is not None else None})
    res["desplazamiento_a_cuadro"] = medidos
    # transiciones v4 → v5
    trs = {}
    for c in CAPS:
        t4 = {int(k): v for k, v in (_plan(BAK, c).get("transitions") or {}).items()}
        t5 = {int(k): v for k, v in (_plan(WD, c).get("transitions") or {}).items()}
        trs[c] = [{"escena": k, "v4": f"{t4[k]['kind']} ({t4[k].get('why')})" if k in t4 else None,
                   "v5": f"{t5[k]['kind']} ({t5[k].get('why')})" if k in t5 else None} for k in sorted(set(t4) | set(t5))]
    res["transiciones"] = trs
    # tiempos
    for v, d in (("v4", BAK), ("v5", WD)):
        res[f"gfx_s_{v}"] = {}
        for c in CAPS:
            lg = (d / f"gfx_{c}.log").read_text(encoding="utf-8") if (d / f"gfx_{c}.log").exists() else ""
            m = re.findall(r"OK total ([\d.]+)s", lg)
            res[f"gfx_s_{v}"][c] = float(m[-1]) if m else None
    (LAB / "b" / "medidas.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in res.items() if k in ("duracion", "fronteras")}, ensure_ascii=False)[:3000])
    return res


def hoja() -> Path:
    from PIL import Image, ImageDraw, ImageFont
    off = offsets_v5()
    try:
        font = ImageFont.truetype("arial.ttf", 18)
    except OSError:
        font = ImageFont.load_default()
    w, h = 240, 135
    # 12 cuadros por frontera: 3 de la cola del cap saliente, 3 de la entrada desde negro, 3 del title card y 3
    # después del title card (la primera imagen con voz)
    rel = [-0.30, -0.15, -1 / FPS, 0.0, 4 / FPS, 9 / FPS, 1.0, 2.0, 2.9, 3.1, 3.5, 4.5]
    sheet = Image.new("RGB", (12 * (w + 4) + 160, 6 * (h + 30) + 10), (14, 14, 14))
    d = ImageDraw.Draw(sheet)
    tmp = LAB / "_costuras"
    tmp.mkdir(exist_ok=True)
    for k in range(1, 7):
        c = off[CAPS[k]]
        y = 10 + (k - 1) * (h + 30)
        d.text((8, y + h // 2 - 10), f"{CAPS[k - 1]}→{CAPS[k]}", fill=(240, 232, 210), font=font)
        for j, r in enumerate(rel):
            t = c + r
            f = tmp / f"f{k}_{j:02d}.jpg"
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{t:.4f}", "-i", str(V5), "-frames:v", "1", "-vf",
                            f"scale={w}:{h}", str(f)], check=True)
            x = 160 + j * (w + 4)
            sheet.paste(Image.open(f).convert("RGB"), (x, y))
            d.text((x + 4, y + h + 4), f"{r:+.2f} s", fill=(170, 170, 160), font=font)
    out = LAB / "COSTURAS_v5.jpg"
    sheet.save(out, quality=88)
    print(out, flush=True)
    return out


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    os.chdir(ROOT)
    {"identidad": identidad, "render": render, "medidas": medidas, "hoja": hoja}[sys.argv[1]]()
