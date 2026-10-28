# -*- coding: utf-8 -*-
"""F49 — fotos de la candidata (S5 de F48: Opus 5.5 + entrada nueva) contra C2 (Pro), caps 2 y 7 de Wittenoom (lab).

Sin LLM: los prompts son los ya escritos (S5 de f48/PROMPTS_F48.json caps 2 y 7; C2 de f47/PROMPTS_F47.json cap 7),
re-pasados por F8 (`f46b.f8`, que usa `fix_counts_lr` de producción, arreglada en e76d8ed) desde su armado (`partes`).
El cap 2 de C2 son las fotos `_a` ya generadas en f46/f46b/C2/ (no se regeneran).

Uso (python del sistema, desde la raíz):
  python lab/hyperframes/f49/f49_corridas.py prompts   → PROMPTS_F49.json + CAMBIOS_F8.md (sin API)
  python lab/hyperframes/f49/f49_corridas.py fotos     → S5/ y C2/ chNN_img_MM.png + _graded (40 llamadas a Seedream)
  python lab/hyperframes/f49/f49_corridas.py hojas     → hoja_chNN_MM-MM.jpg (C2 | S5, una cada 4 fotos)
  python lab/hyperframes/f49/f49_corridas.py costos    → COSTOS_F49.md (cost_history, video_id f49-lab)
"""
from __future__ import annotations

import json
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

LAB = Path(__file__).resolve().parent
ROOT = LAB.parents[2]
HF = ROOT / "lab" / "hyperframes"
sys.path[:0] = [str(ROOT), str(HF / "f47")]
import f47_corridas as f47  # noqa: E402  (cargar; importa f46 y f46b)

f46b = f47.f46b
f46b.LAB_ID = "f49-lab"
f46b.TOPE_USD = 2.50                                  # handoff F49 §Constantes (Omar confirma al pegar)
NUM_IMAGES = 1                                        # handoff F49 §Constantes (1 foto por prompt)
F46B_C2 = HF / "f46" / "f46b" / "C2"
# (variante, cap, archivo de prompts, clave)
FUENTES = [("S5", 2, HF / "f48" / "PROMPTS_F48.json", "S5_ch02"),
           ("S5", 7, HF / "f48" / "PROMPTS_F48.json", "S5_ch07"),
           ("C2", 7, HF / "f47" / "PROMPTS_F47.json", "C2_ch07")]
_LOCK = threading.Lock()
_j, _w = f47._j, f47._w


def _fix_counts_lr_previa(prose: str) -> str:
    """`fix_counts_lr` tal como estaba en 50c3c42 (antes de F49), solo para comprobar que el re-pase reproduce los
    prompts guardados byte a byte."""
    from script_engine import m03_imagenes_v3 as v3
    def _cnt(m: re.Match) -> str:
        w = m.group(1).lower()
        return "a couple of " if w == "two" else "a few " if w in ("three", "four") else "several "
    p = v3.COUNT_RE.sub(_cnt, prose)
    p = v3.LR_RE.sub(lambda m: "to one side" if m.group(0).lower().startswith(("on", "to", "at", "from")) else "side", p)
    return re.sub(r"\s{2,}", " ", p)


# ─────────────────────────── prompts ───────────────────────────
def prompts() -> None:
    from script_engine import m03_imagenes_v3 as v3
    canon = {"S5": _j(HF / "f48" / "canon_S5.json"), "C2": _j(HF / "f46" / "f46b" / "canon_C.json")}
    fix_nueva = v3.fix_counts_lr
    out, cambios, anclas = {}, [], {}
    for var, cap, arch, clave in FUENTES:
        d = f47.cargar(cap)
        by_n = {b["n"]: b for b in d["cap_beats"]}
        documented = canon[var].get("documented_people")
        anclas[cap] = [x.get("narration_anchor") or "" for x in d["v03"]]
        res = []
        for x in _j(arch)[clave]:
            it = {**x["slots"], "_f8_slots_scrub": x.get("f8_slots_scrub") or []}
            armado = " ".join(p for p in x["partes"].values() if p)
            esc = bool((by_n.get(it.get("beat")) or {}).get("escala"))
            try:
                v3.fix_counts_lr = _fix_counts_lr_previa
                previo, _ = f46b.f8(armado, it, esc, documented)
            finally:
                v3.fix_counts_lr = fix_nueva
            assert previo == x["prompt"], f"{clave} foto {x['foto']}: el re-pase con la F8 previa no da el guardado"
            nuevo, notas = f46b.f8(armado, it, esc, documented)
            if nuevo != x["prompt"]:
                cambios.append({"var": var, "cap": cap, "foto": x["foto"], "antes": x["prompt"], "despues": nuevo})
            res.append({"foto": x["foto"], "anio": x["anio"], "prompt": nuevo, "prompt_f48_f47": x["prompt"],
                        "f8_problemas": notas})
        out[f"{var}_ch{cap:02d}"] = res
    c2_2 = _j(HF / "f46" / "f46b" / "C2.json")["image_prompts"]
    out["C2_ch02"] = [{"foto": x["foto"], "anio": x["anio"], "prompt": x["prompt"], "fotos": "f46/f46b/C2/_a"}
                      for x in c2_2]
    out["_anclas"] = {f"ch{c:02d}": a for c, a in anclas.items()}
    _w(LAB / "PROMPTS_F49.json", out)
    L = ["# F49 — prompts re-pasados por F8 con `fix_counts_lr` arreglada (e76d8ed)", "",
         f"Se re-pasaron {sum(len(out[k]) for k in ('S5_ch02', 'S5_ch07', 'C2_ch07'))} prompts (S5 caps 2 y 7, "
         f"C2 cap 7). Con la F8 previa el re-pase reproduce los {sum(len(out[k]) for k in ('S5_ch02', 'S5_ch07', 'C2_ch07'))} "
         f"guardados byte a byte (assert). Cambiaron **{len(cambios)}**:", ""]
    if cambios:
        L += ["| variante | cap | foto | antes (fragmento) | después (fragmento) |", "|---|---|---|---|---|"]
    for c in cambios:
        a, b = c["antes"], c["despues"]
        i = next((k for k in range(min(len(a), len(b))) if a[k] != b[k]), min(len(a), len(b)))
        lo = max(0, i - 40)
        L.append(f"| {c['var']} | {c['cap']} | {c['foto']} | …{a[lo:i + 60]}… | …{b[lo:i + 60]}… |")
    L += [""] + [f"**{c['var']} cap {c['cap']} foto {c['foto']}**\n\n- antes: {c['antes']}\n- después: {c['despues']}\n"
                 for c in cambios]
    (LAB / "CAMBIOS_F8.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L[:12 + len(cambios)]))


# ─────────────────────────── fotos ───────────────────────────
def generar_1(prompt: str, png: Path) -> dict:
    """Una llamada a Seedream 5 Lite con el payload de producción y num_images 1 → png (como f46b.generar_2)."""
    import requests

    import asset_manager as am
    from cost_tracker import cost_tracker
    from engine_profiles import select_profile
    prof = select_profile("seedream")
    payload = am._SYNC_PAYLOAD_BUILDERS["seedream"](prompt, None)
    payload["num_images"] = NUM_IMAGES
    try:
        r = requests.post(f"{prof.render.base_url}/{prof.render.model_id}", headers=am._fal_headers(), json=payload,
                          timeout=240)
        r.raise_for_status()
    except requests.HTTPError as e:
        body = e.response.text if e.response is not None else str(e)
        if am._is_content_rejection(body):
            raise am.ContentRejectedError(body[:300])
        raise
    data = r.json()
    imgs = data.get("images") or []
    if imgs:
        png.parent.mkdir(parents=True, exist_ok=True)
        g = requests.get(imgs[0]["url"], timeout=60)
        g.raise_for_status()
        png.write_bytes(g.content)
    cost_tracker.track_seedream(description=f"{png.parent.name}/{png.name}: {prompt[:60]}...", images=len(imgs))
    return {"n": len(imgs), "nsfw": data.get("has_nsfw_concepts")}


def fotos() -> None:
    import asset_manager as am
    from cost_tracker import cost_tracker
    from engine_profiles import select_profile
    from script_engine import image_grade
    costo = select_profile("seedream").render.cost_usd * NUM_IMAGES
    P = _j(LAB / "PROMPTS_F49.json")
    trabajos = [(v, c, x["foto"], x["prompt"]) for v, c, _, _ in FUENTES for x in P[f"{v}_ch{c:02d}"]]
    f46b._PREVIO = f46b.gastado_previo()
    cost_tracker.start_video(f46b.LAB_ID)
    reservado = {"n": 0}

    def una(v: str, c: int, i: int, prompt: str) -> dict:
        png = LAB / v / f"ch{c:02d}_img_{i:02d}.png"
        if png.exists():
            return {"var": v, "cap": c, "foto": i, "estado": "ya estaba"}
        with _LOCK:                                   # freno antes de cada llamada, con lo ya reservado en vuelo
            f46b.freno(f"{v} cap {c} foto {i}", costo * (reservado["n"] + 1))
            reservado["n"] += 1
        try:
            r = generar_1(prompt, png)
            if not png.exists():
                return {"var": v, "cap": c, "foto": i, "estado": "sin imagen", "nsfw": r["nsfw"]}
            image_grade.grade(png)
            return {"var": v, "cap": c, "foto": i, "estado": "ok", "nsfw": r["nsfw"]}
        except am.ContentRejectedError as e:
            (LAB / v).mkdir(parents=True, exist_ok=True)
            png.with_suffix(".rechazada.txt").write_text(str(e), encoding="utf-8")
            return {"var": v, "cap": c, "foto": i, "estado": f"rechazada: {str(e)[:200]}"}
        finally:
            with _LOCK:
                reservado["n"] -= 1
    resultado = []
    try:
        with ThreadPoolExecutor(max_workers=min(am.FLUX_MAX_WORKERS, len(trabajos))) as ex:   # las 40 en paralelo
            for f in as_completed([ex.submit(una, *t) for t in trabajos]):
                try:
                    r = f.result()
                except f46b.Parada as e:
                    r = {"estado": f"PARADA: {e}"}
                except Exception as e:  # noqa: BLE001 — una foto que falla no tira las demás; se reporta
                    r = {"estado": f"error: {type(e).__name__}: {str(e)[:200]}"}
                resultado.append(r)
                print(f"  {r}", flush=True)
    finally:
        cost_tracker.end_video()
    _w(LAB / "fotos_resultado.json", sorted(resultado, key=lambda r: (r.get("var", ""), r.get("cap", 0),
                                                                      r.get("foto", 0))))
    print(f"  fotos: {sum(1 for r in resultado if r.get('estado') == 'ok')}/{len(trabajos)} ok · cost_history "
          f"{f46b.LAB_ID} = US$ {f46b.gastado_previo():.4f}", flush=True)


# ─────────────────────────── hojas ───────────────────────────
def _fuente(tam: int):
    from PIL import ImageFont
    try:
        return ImageFont.truetype("C:/Windows/Fonts/arial.ttf", tam)
    except OSError:
        return ImageFont.load_default()


def _celda(var: str, cap: int, n: int) -> tuple[Path, Path]:
    if var == "C2" and cap == 2:
        return F46B_C2 / f"ch02_img_{n:02d}_a_graded.png", F46B_C2 / f"ch02_img_{n:02d}.rechazada.txt"
    return LAB / var / f"ch{cap:02d}_img_{n:02d}_graded.png", LAB / var / f"ch{cap:02d}_img_{n:02d}.rechazada.txt"


def hojas(ancho_total: int = 3840) -> None:
    from PIL import Image, ImageDraw
    P = _j(LAB / "PROMPTS_F49.json")
    cols = ("C2", "S5")
    m, rot_w, enc_h = 12, 300, 40
    cw = (ancho_total - rot_w - m * (len(cols) + 1)) // len(cols)
    chh = round(cw * 1440 / 2560)
    f_enc, f_rot, f_anio, f_cel = _fuente(26), _fuente(20), _fuente(22), _fuente(28)
    for cap in (2, 7):
        anio = {v: {x["foto"]: x["anio"] for x in P[f"{v}_ch{cap:02d}"]} for v in cols}
        anclas = P["_anclas"][f"ch{cap:02d}"]
        n_fotos = len(P[f"S5_ch{cap:02d}"])
        for desde in range(1, n_fotos + 1, 4):
            filas = list(range(desde, min(desde + 4, n_fotos + 1)))
            ancho = rot_w + m * (len(cols) + 1) + cw * len(cols)
            im = Image.new("RGB", (ancho, enc_h + len(filas) * (chh + m) + m), (24, 24, 24))
            dr = ImageDraw.Draw(im)
            for j, col in enumerate(cols):
                dr.text((rot_w + m * (j + 1) + cw * j + 4, 8), f"{col}" + (" (F46b _a)" if col == "C2" and cap == 2
                                                                            else ""), fill=(235, 235, 235), font=f_enc)
            for i, n in enumerate(filas):
                y = enc_h + i * (chh + m)
                dr.text((m, y + 2), f"Cap {cap} · foto {n:02d}", fill=(255, 210, 90), font=f_enc)
                dr.text((m, y + 36), f"C2: {anio['C2'].get(n, '?')}", fill=(130, 220, 255), font=f_anio)
                dr.text((m, y + 64), f"S5: {anio['S5'].get(n, '?')}", fill=(130, 255, 160), font=f_anio)
                pal = " ".join((anclas[n - 1] if n - 1 < len(anclas) else "").split()[:8])
                linea, ys = "", y + 100
                for w in pal.split():
                    if dr.textlength(linea + " " + w, font=f_rot) > rot_w - m:
                        dr.text((m, ys), linea.strip(), fill=(200, 200, 200), font=f_rot)
                        ys, linea = ys + 24, ""
                    linea += " " + w
                if linea.strip():
                    dr.text((m, ys), linea.strip(), fill=(200, 200, 200), font=f_rot)
                for j, col in enumerate(cols):
                    x = rot_w + m * (j + 1) + cw * j
                    p, rech = _celda(col, cap, n)
                    if p.exists():
                        with Image.open(p) as f:
                            im.paste(f.convert("RGB").resize((cw, chh), Image.LANCZOS), (x, y))
                    else:
                        txt = "rechazada" if rech.exists() else "falta"
                        dr.rectangle([x, y, x + cw - 1, y + chh - 1], fill=(110, 110, 110))
                        dr.text((x + (cw - dr.textlength(txt, font=f_cel)) / 2, y + chh / 2 - 14), txt,
                                fill=(240, 240, 240), font=f_cel)
            s = LAB / f"hoja_ch{cap:02d}_{filas[0]:02d}-{filas[-1]:02d}.jpg"
            im.save(s, "JPEG", quality=88)
            print(f"{s.relative_to(ROOT)}  {im.size[0]}x{im.size[1]}")


# ─────────────────────────── costos ───────────────────────────
def costos() -> None:
    from cost_tracker import cost_tracker
    raw = cost_tracker.HISTORY_FILE.read_bytes()
    try:
        h = json.loads(raw.decode("utf-8"))
    except UnicodeDecodeError:
        h = json.loads(raw.decode("cp1252"))
    reps = [r for r in h if isinstance(r, dict) and r.get("video_id") == f46b.LAB_ID]
    es = [e for r in reps for e in r.get("entries", [])]
    tot = sum(float(e.get("total_cost") or 0) for e in es)
    L = [f"# F49 — costos (cost_history, video_id {f46b.LAB_ID})", "",
         f"{len(reps)} registro(s), {len(es)} entradas, total **US$ {tot:.4f}** (tope {f46b.TOPE_USD:.2f}).", "",
         "| servicio | descripción | imágenes | costo US$ |", "|---|---|---:|---:|"]
    for e in es:
        d = str(e.get("description", "")).replace("|", "/")
        L.append(f"| {e.get('service', '?')} | {d[:70]} | {e.get('images', e.get('units', ''))} | "
                 f"{float(e.get('total_cost') or 0):.4f} |")
    (LAB / "COSTOS_F49.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[:4]))


if __name__ == "__main__":
    {"prompts": prompts, "fotos": fotos, "hojas": hojas, "costos": costos}[sys.argv[1]]()
