# -*- coding: utf-8 -*-
"""F50i — una variable: el aspecto de `spanish_migrant_families` sin el estado («; women and children tanned and dusted
red in Wittenoom»), sobre las 4 fotos de F50h con manchas rojas (lab; no toca producción).

C′ = `f50h.armar_c` con `ESTILO_C` y el mismo post-proceso (`f50h.post`), con UN cambio: el `appearance` de
`spanish_migrant_families` en una COPIA en memoria de `grupos` (canon, topics_db y 03_visual.json no se tocan).
Antes de gastar: el C rearmado tiene que ser igual al C de F50h (`PROMPTS_F50h.json`), y el diff palabra por palabra C →
C′ tiene que mostrar solo la cláusula quitada; si no, PARADA.
Fotos: `f50h.generar_2` (= `generar_1` de F49 con `num_images` 2), las 4 en paralelo → fotos/<cap>_<foto>/Cp_1.png, Cp_2.png.
Hojas (no a ciegas): arriba las 2 de C de F50h (la letra que la llave de F50h da a C), abajo las 2 de C′.
Uso: python lab/hyperframes/f50i/f50i.py
"""
import difflib
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "lab" / "hyperframes" / "f50g"))
sys.path.insert(0, str(ROOT / "lab" / "hyperframes" / "f50h"))
F50I = Path(__file__).resolve().parent
F50H = ROOT / "lab" / "hyperframes" / "f50h"
LAB_ID = "f50i-lab"
TOPE_USD = 0.50                                         # handoff F50i §Constantes (Omar 2026-10-29 03:10)
FOTOS = [(2, 9), (4, 11), (4, 12), (5, 8)]              # handoff F50i §Constantes
GRUPO = "spanish_migrant_families"
VIEJO = ("Spanish Mediterranean people with olive to light skin, dark brown or black hair, dark eyes, slim to medium "
         "builds; women and children tanned and dusted red in Wittenoom.")      # handoff F50i, el de hoy
NUEVO = ("Spanish Mediterranean people with olive to light skin, dark brown or black hair, dark eyes, slim to medium "
         "builds.")                                                             # handoff F50i, C′


def _gastado_previo() -> float:
    from cost_tracker import cost_tracker
    raw = cost_tracker.HISTORY_FILE.read_bytes() if cost_tracker.HISTORY_FILE.exists() else b"[]"
    try:
        h = json.loads(raw.decode("utf-8"))
    except UnicodeDecodeError:
        h = json.loads(raw.decode("cp1252"))
    return round(sum(float(r.get("total_cost") or 0) for r in h if isinstance(r, dict) and r.get("video_id") == LAB_ID),
                 4)


def prompts() -> list[dict]:
    import f50h
    import rearmar as rg
    from script_engine import m03_imagenes_v3 as v3
    from script_engine.topics_db import get_topic_by_id
    vivo = json.loads(rg.VISUAL.read_text(encoding="utf-8"))
    topic = get_topic_by_id(f50h.TID)
    beats = v3.load_beats(topic, rg.STEPS)
    grupos = {g["id"]: g for g in topic.get("people_groups") or [] if isinstance(g, dict) and g.get("id")}
    if grupos[GRUPO]["appearance"] != VIEJO:
        raise SystemExit(f"PARADA: el appearance de {GRUPO} en el canon no es el del handoff")
    grupos_p = {**grupos, GRUPO: {**grupos[GRUPO], "appearance": NUEVO}}      # copia en memoria: un solo cambio
    items = {(c["chapter_number"], i): it for c in vivo["chapters"] for i, (it, _) in enumerate(rg.fotos(c), 1)}
    c_f50h = {f["foto"]: f["C"] for f in json.loads((F50H / "PROMPTS_F50h.json").read_text(encoding="utf-8"))["fotos"]}
    out = []
    for cap, foto in FOTOS:
        it = items[(cap, foto)]
        by_n = {b["n"]: b for b in beats.get(cap) or []}
        escala = bool((by_n.get(it.get("beat")) or {}).get("escala"))
        slots = json.loads(it["raw_llm_prompt"])
        doc = topic.get("documented_people")
        c = f50h.post(f50h.armar_c(slots, it["anio"], grupos, f50h.ESTILO_C), slots, escala, doc)
        cp = f50h.post(f50h.armar_c(slots, it["anio"], grupos_p, f50h.ESTILO_C), slots, escala, doc)
        a, b = c.split(), cp.split()
        ops = [(op, " ".join(a[i1:i2]), " ".join(b[j1:j2]))
               for op, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b, autojunk=False).get_opcodes() if op != "equal"]
        out.append({"foto": f"{cap}/{foto}", "people_group": slots.get("people_group"), "C": c, "Cp": cp,
                    "C_igual_F50h": c == c_f50h[f"{cap}/{foto}"], "solo_la_clausula": cp == c.replace(VIEJO, NUEVO)
                    and VIEJO in c, "diff": ops, "palabras": {"C": len(a), "Cp": len(b)}})
    return out


def fotos(P: list[dict]) -> dict:
    import f50h
    from cost_tracker import cost_tracker
    from engine_profiles import select_profile
    f50h.NUM_IMAGES = 2                                  # handoff F50i §Constantes (2 fotos por prompt)
    costo = select_profile("seedream").render.cost_usd * f50h.NUM_IMAGES * len(P)
    previo = _gastado_previo()
    if previo + costo > TOPE_USD:
        raise SystemExit(f"PARADA: gastado {previo:.4f} + {costo:.4f} > tope {TOPE_USD:.2f}")
    cost_tracker.start_video(LAB_ID)

    def una(p):
        base = F50I / "fotos" / p["foto"].replace("/", "_") / "Cp"
        errores = []
        for intento in (1, 2):                          # un rechazo o un error se reintenta una vez (como F50h)
            try:
                n = f50h.generar_2(p["Cp"], base)
                if n == f50h.NUM_IMAGES:
                    return {"foto": p["foto"], "estado": "ok", "intentos": intento}
                errores.append(f"llegaron {n} imágenes")
            except Exception as e:  # noqa: BLE001
                errores.append(f"{type(e).__name__}: {str(e)[:200]}")
        return {"foto": p["foto"], "estado": "hueco", "errores": errores}
    try:
        with ThreadPoolExecutor(max_workers=len(P)) as ex:
            res = list(ex.map(una, P))
    finally:
        cost_tracker.end_video()
    return {"resultado": res, "usd_lab": _gastado_previo()}


def hojas() -> None:
    """Una hoja por foto: arriba las 2 de C de F50h, abajo las 2 de C′; con rótulos (no va a ciegas)."""
    from PIL import Image, ImageDraw

    import f50h
    llave = json.loads((F50H / "llave.json").read_text(encoding="utf-8"))   # solo para hallar la letra de C
    anclas = f50h._anclas()
    (F50I / "hojas").mkdir(exist_ok=True)
    cw, m, enc_h, rot_w = 1280, 12, 90, 300
    chh = round(cw * 1440 / 2560)
    f_enc, f_ancla, f_rot = f50h._fuente(30), f50h._fuente(24), f50h._fuente(30)
    for cap, foto in FOTOS:
        key = f"{cap}/{foto}"
        letra_c = next(l for l, v in llave[key].items() if v == "C")
        filas = [("C (F50h)", [F50H / "fotos" / f"{cap}_{foto}" / f"{letra_c}_{n}.png" for n in (1, 2)]),
                 ("C′ (sin polvo)", [F50I / "fotos" / f"{cap}_{foto}" / f"Cp_{n}.png" for n in (1, 2)])]
        im = Image.new("RGB", (rot_w + m + 2 * (cw + m), enc_h + 2 * (chh + m) + m), (24, 24, 24))
        dr = ImageDraw.Draw(im)
        dr.text((m, 8), f"Cap {cap} · foto {foto}", fill=(255, 210, 90), font=f_enc)
        dr.text((m, 48), " ".join((anclas.get(key) or "").split()[:30]), fill=(220, 220, 220), font=f_ancla)
        for i, (rot, pngs) in enumerate(filas):
            y = enc_h + i * (chh + m)
            dr.text((m, y + 8), rot, fill=(130, 220, 255), font=f_rot)
            for j, p in enumerate(pngs):
                x = rot_w + m + j * (cw + m)
                if p.exists():
                    with Image.open(p) as f:
                        im.paste(f.convert("RGB").resize((cw, chh), Image.LANCZOS), (x, y))
                else:
                    dr.rectangle([x, y, x + cw - 1, y + chh - 1], fill=(110, 110, 110))
                    dr.text((x + cw / 2 - 40, y + chh / 2 - 15), "hueco", fill=(240, 240, 240), font=f_rot)
        s = F50I / "hojas" / f"hoja_{cap}_{foto}.jpg"
        im.save(s, "JPEG", quality=88)
        print(f"{s.relative_to(ROOT)}  {im.size[0]}x{im.size[1]}")


def main() -> int:
    P = prompts()
    L = ["# PROMPTS_F50i — C (F50h) y C′ (aspecto sin «dusted red»), las 4 fotos", "",
         "Salida de `python lab/hyperframes/f50i/f50i.py`. C′ = `f50h.armar_c` + `f50h.post` con el `appearance` de "
         f"`{GRUPO}` cambiado en una copia en memoria (canon, topics_db y 03_visual.json intactos).", "",
         "| foto | grupos | C = C de F50h | C′ = C con solo la cláusula quitada | palabras C → C′ |",
         "|---|---|---|---|---|"]
    L += [f"| {p['foto']} | {', '.join(p['people_group'])} | {'sí' if p['C_igual_F50h'] else 'NO'} | "
          f"{'sí' if p['solo_la_clausula'] else 'NO'} | {p['palabras']['C']} → {p['palabras']['Cp']} |" for p in P]
    for p in P:
        L += ["", f"## {p['foto']}", "", "Diff palabra por palabra (C → C′):", ""]
        L += [f"- {op}: «{a}» → «{b}»" for op, a, b in p["diff"]]
        L += ["", "**C (F50h)**", "", "```", p["C"], "```", "", "**C′**", "", "```", p["Cp"], "```"]
    ok = all(p["C_igual_F50h"] and p["solo_la_clausula"] for p in P)
    (F50I / "PROMPTS_F50i.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (F50I / "PROMPTS_F50i.json").write_text(json.dumps(P, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"prompts: C = F50h {sum(p['C_igual_F50h'] for p in P)}/4 · solo la cláusula {sum(p['solo_la_clausula'] for p in P)}/4"
          f" · diffs {[p['diff'] for p in P]}")
    if not ok:
        print("PARADA: el diff C → C′ no es solo la cláusula (o C no es el de F50h)")
        return 1
    if "--sin-fotos" in sys.argv:
        return 0
    r = fotos(P)
    (F50I / "fotos_resultado.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"fotos: {r['resultado']} · cost_history {LAB_ID} = US$ {r['usd_lab']:.4f}")
    hojas()
    return 0


if __name__ == "__main__":
    sys.exit(main())
