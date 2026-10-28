"""F46 — fotos de época: A/B del cap 2 de Wittenoom en el lab, sin tocar producción.

    A   las de hoy (output/<tid>/assets/ch02_flux/ch02_img_NN_graded.png; prompts = 03_visual.json, solo lectura).
    B1  ENTRADA nueva, estructura de hoy: canon desde la ficha (`extract_visual_canon` con hechos, cronología y escenas
        de la ficha como «facts») + el bloque de beats con WHEN / WHERE / CASE-FILE SCENES (datos que el beat ya trae
        por sus ids) → el mismo flujo de producción del cap (`m03_visual._render_prompts_seedream`: slots Pro → tejido
        Flash → reglas F8 → estilo al principio con el año de la foto + cola de hoy). Anclas y beats: los de 03_visual.
    B2  los MISMOS slots de B1 (sin volver a llamar a Pro), tejidos por el mismo `_fluidify_item` con otro orden de
        formula, sin `mood`, con el slot `style` = `style_head(<año de la foto>)` y sin anteponer el estilo.
Producción no se edita: las funciones se importan y, solo dentro de este proceso, se reemplazan `beats_block` (B1), el
año que recibe `_f8_finish_item` (B1, por foto) y `wrap_style` (B2: no antepone). Freno antes de cada llamada paga:
lo gastado en la tanda (cost_history `f46-lab` + lo de este proceso) + el costo de la llamada conocido (foto: el del
perfil) no pasa el tope. El gasto queda en `data/cost_history.json` con el id `f46-lab` (lo único en data/).

    python lab/hyperframes/f46/f46_corridas.py prompts   → canon_B.json, B1.json, B2.json, PROMPTS_AB.md
    python lab/hyperframes/f46/f46_corridas.py fotos     → B1/ y B2/ (16 + 16 fotos, en paralelo) con su _graded
"""
from __future__ import annotations

import copy
import dataclasses
import json
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
CAP = 2
STEPS = ROOT / "data" / "scripts" / "_steps"
A_IMG = ROOT / "output" / TID / "assets" / "ch02_flux"
LAB_ID = "f46-lab"
TOPE_USD = 3.00                                       # Omar, al pegar el prompt de F46
FORMULA_B2 = ("subject", "action", "gaze_interaction", "setting", "hard_facts", "props_detail", "style",
              "color_palette", "lighting", "shot_scale", "camera_angle", "lens_technique", "text_in_image",
              "aspect_ratio", "negations")        # handoff F46 §Parte 1.4 (sin `mood`)
CANON_KEYS = ("era_visual_canon", "documented_people", "anachronism_blocklist", "documented_props")

_LOCK = threading.Lock()


class Parada(RuntimeError):
    pass


def _j(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def _w(p: Path, obj) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=1, default=str), encoding="utf-8")


# ─────────────────────────── gasto y freno ───────────────────────────
def gastado_previo() -> float:
    """Lo de corridas anteriores de la tanda: los reportes `f46-lab` de cost_history."""
    from cost_tracker import cost_tracker
    f = cost_tracker.HISTORY_FILE
    if not f.exists():
        return 0.0
    try:
        h = json.loads(f.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        h = json.loads(f.read_text(encoding="cp1252"))
    return round(sum(float(r.get("total_cost") or 0) for r in h if isinstance(r, dict) and r.get("video_id") == LAB_ID), 4)


_PREVIO = 0.0


def gastado() -> float:
    from cost_tracker import cost_tracker
    cv = cost_tracker.current_video
    return round(_PREVIO + (cv.total_cost if cv else 0.0), 4)


def freno(que: str, costo: float = 0.0) -> None:
    g = gastado()
    if g + costo > TOPE_USD:
        raise Parada(f"freno ({que}): gastado {g:.4f} + {costo:.4f} > tope {TOPE_USD:.2f}")


def _con_freno(fn, que: str):
    def envuelta(*a, **k):
        freno(f"{que} · {k.get('description') or ''}")
        return fn(*a, **k)
    return envuelta


# ─────────────────────────── datos (solo lectura) ───────────────────────────
def cargar() -> dict:
    import fase1_5
    from script_engine import m03_imagenes_v3 as v3img
    topic = copy.deepcopy(fase1_5._load_topic_by_id(TID))
    skel = fase1_5._load_skeleton(TID)
    narr = fase1_5._load_narration(TID)
    sch = next(c for c in skel["chapters"] if c["chapter_number"] == CAP)
    nch = next(c for c in narr["chapters"] if c["chapter_number"] == CAP)
    v03 = next(c for c in _j(STEPS / TID / "03_visual.json")["chapters"] if c["chapter_number"] == CAP)["image_prompts"]
    beats = v3img.load_beats(topic, STEPS)
    year_topic = v3img.topic_year(topic, beats)
    cap_beats = beats[CAP]
    year_of_beat = {b["n"]: (b["fecha"][:4] if re.match(r"\d{4}", b.get("fecha") or "") else year_topic)
                    for b in cap_beats}
    return {"topic": topic, "sch": sch, "narr": (nch.get("narration") or "").strip(), "v03": v03, "beats": beats,
            "cap_beats": cap_beats, "year_topic": year_topic, "year_of_beat": year_of_beat,
            "ficha": _j(STEPS / TID / "ficha_caso.json"), "esc": _j(STEPS / TID / "01a_escaleta.json")}


def adaptador_facts(ficha: dict) -> list[dict]:
    """La ficha como «verified_facts» del canon (dato, no regla): hechos, cronología «fecha: evento» y escenas
    «donde — quien — que_pasa — sentidos»."""
    out = [{"fact": h.get("texto") or ""} for h in ficha.get("hechos") or []]
    out += [{"fact": f"{c.get('fecha') or ''}: {c.get('evento') or ''}"} for c in ficha.get("cronologia") or []]
    out += [{"fact": " — ".join(str(e.get(k) or "") for k in ("donde", "quien", "que_pasa", "sentidos"))}
            for e in ficha.get("escenas") or []]
    return [f for f in out if f["fact"].strip(" :—")]


def contexto_beat(d: dict) -> dict[int, dict]:
    """Por beat del cap: WHEN (fechas de sus ids en el pool), WHERE (lugar de sus ids de cronología + nombre de sus ids
    de lugares) y las escenas de la ficha cuyos ids se cruzan con los del beat."""
    from script_engine import evidence as ev
    pool = d["topic"].get("evidence_pool") or {}
    its = ev.items(pool)
    lugares = {l["id"]: l.get("nombre") for l in pool.get("lugares") or []}
    crono = {t["id"]: t for t in pool.get("cronologia") or []}
    esc_beats = {b["n"]: b for b in d["esc"].get("beats") or []}
    out = {}
    for b in d["cap_beats"]:
        eb = esc_beats.get(b["n"]) or {}
        ids = [x for x in [eb.get("dato_central"), *(eb.get("datos_apoyo") or [])] if x]
        when = sorted({str(its[i].get("fecha")) for i in ids if i in its and its[i].get("fecha")})   # la `fecha` del item, tal cual
        where: list[str] = []
        for i in ids:
            for v in ((crono.get(i) or {}).get("lugar"), lugares.get(i)):
                if v and v not in where:
                    where.append(v)
        escenas = [e for e in d["ficha"].get("escenas") or [] if set(e.get("ids") or []) & set(ids)]
        out[b["n"]] = {"ids": ids, "when": when, "where": where,
                       "escenas": [" · ".join(str(e.get(k) or "") for k in ("donde", "quien", "sentidos"))
                                   for e in escenas]}
    return out


def beats_block_b(ctx: dict[int, dict]):
    """El `beats_block` de producción, con 3 líneas más por imagen (datos del beat, ninguna regla)."""
    from script_engine import m03_imagenes_v3 as v3img
    original = v3img.beats_block

    def bloque(cap_beats, assign, bullets=None, lang=None):
        txt = original(cap_beats, assign, bullets, lang)
        for i, a in enumerate(assign, start=1):
            c = ctx.get(a["beat"]) or {"when": [], "where": [], "escenas": []}
            extra = (f"\n      WHEN: {', '.join(c['when']) or '-'}"
                     f"\n      WHERE: {', '.join(c['where']) or '-'}"
                     f"\n      CASE-FILE SCENES: {' | '.join('«' + s + '»' for s in c['escenas']) or '-'}")
            marca = f"  [{i}] beat {a['beat']} · "
            k = txt.find(marca)
            fin = txt.find("\n", txt.find("SEEN:", k))
            txt = txt[:fin] + extra + txt[fin:]
        return txt
    return bloque


# ─────────────────────────── parte 1 ───────────────────────────
def parte1() -> None:
    global _PREVIO
    from cost_tracker import cost_tracker
    from engine_profiles import select_profile
    from researcher_steps import step_4e_visual_canon as s4e
    from script_engine import m03_imagenes_v3 as v3img
    from script_engine import m03_visual as m03
    d = cargar()
    topic = d["topic"]
    _PREVIO = gastado_previo()
    cost_tracker.start_video(LAB_ID)
    m03.call_flash_json = _con_freno(m03.call_flash_json, "Flash m03")
    m03.call_pro_json = _con_freno(m03.call_pro_json, "Pro m03")
    s4e.call_flash_json = _con_freno(s4e.call_flash_json, "Flash canon")
    try:
        # 1. canon B desde la ficha
        facts = adaptador_facts(d["ficha"])
        canon_b = s4e.extract_visual_canon(seed={"seed_title": topic.get("video_title")}, angle_blocks={},
                                           verified_facts=facts, canonical=topic.get("canonical_subject_description"))
        _w(LAB / "canon_B.json", {"facts_de_la_ficha": len(facts), **canon_b})
        print(f"  canon B: {len(facts)} facts de la ficha → {sorted(canon_b)} · US$ {gastado():.4f}", flush=True)
        topic_b = {**topic, **{k: canon_b[k] for k in CANON_KEYS if k in canon_b}}
        # 2. contexto por beat + B1 por el flujo de producción del cap
        ctx = contexto_beat(d)
        _w(LAB / "contexto_beats.json", ctx)
        assign = [{"beat": it.get("beat"), "cerrada": bool(it.get("cerrada"))} for it in d["v03"]]
        topic_b["_f8"] = {"beats": d["beats"], "year": d["year_topic"], "lang": v3img.place_language(topic),
                          "force_assign": assign}
        plan = {"anchors": [{"anchor": it["narration_anchor"]} for it in d["v03"]]}
        fin_orig = m03._f8_finish_item
        v3img.beats_block = beats_block_b(ctx)

        def fin_con_anio(it, locked, profile, documented, cap_number, i, year, escala=False):
            return fin_orig(it, locked, profile, documented, cap_number, i,
                            d["year_of_beat"].get(it.get("beat"), year), escala)
        m03._f8_finish_item = fin_con_anio
        b1 = m03._render_prompts_seedream(topic_b, d["sch"], d["narr"], plan, CAP)
        _w(LAB / "B1.json", b1)
        print(f"  B1: {len(b1['image_prompts'])} prompts · US$ {gastado():.4f}", flush=True)
        m03._f8_finish_item = fin_orig
        # 3. B2: los slots de B1, otro orden, sin mood, el estilo como slot con el año de la foto, sin anteponer
        prof = dataclasses.replace(select_profile("seedream"), formula=FORMULA_B2)
        v3img.wrap_style = lambda prose, year: (prose or "").strip()
        facts_v = topic_b.get("verified_facts") or []
        documented = topic_b.get("documented_people")
        cap_beats = d["cap_beats"]
        b2_items: list[dict] = [None] * len(b1["image_prompts"])

        def una(i: int, src: dict) -> None:
            it = {k: copy.deepcopy(v) for k, v in src.items()
                  if k not in ("prompt", "raw_llm_prompt", "sensible", "motivos", "_f8_problemas")}
            anio = d["year_of_beat"].get(it.get("beat"), d["year_topic"])
            it["style"] = v3img.style_head(anio)
            it.pop("mood", None)
            locked = m03._enforce_measure_fit(m03._classify_locked_facts(
                m03._seedream_facts_verbatim(it.get("hard_fact_ids"), facts_v)), f"B2 img #{i}")
            it["prompt"] = m03._fluidify_with_leakage_guard(it, locked, prof, documented, CAP, i)
            b = next((x for x in cap_beats if x["n"] == it.get("beat")), {})
            fin_orig(it, locked, prof, documented, CAP, i, anio, bool(b.get("escala")))
            b2_items[i - 1] = it
        with ThreadPoolExecutor(max_workers=m03.FLUIDIFY_MAX_WORKERS) as ex:
            futs = [ex.submit(una, i, it) for i, it in enumerate(b1["image_prompts"], start=1)]
            for f in as_completed(futs):
                f.result()
        _w(LAB / "B2.json", {"chapter_number": CAP, "formula": FORMULA_B2, "image_prompts": b2_items})
        print(f"  B2: {len(b2_items)} prompts · US$ {gastado():.4f}", flush=True)
        escribir_prompts_ab(d, canon_b, ctx, b1["image_prompts"], b2_items)
    finally:
        cost_tracker.end_video()                      # el registro de costos (lo único en data/)
    print(f"  parte 1: US$ {gastado_previo():.4f} en cost_history ({LAB_ID})", flush=True)


# ─────────────────────────── PROMPTS_AB.md ───────────────────────────
_EPOCA = re.compile(r"\b(1[5-9]\d{2}|20\d{2})s?\b|\b(19|20)\d0s\b|\bera\b|\bperiod\b|\bdecade\b", re.I)


def _lugares(d: dict, ctx: dict) -> list[str]:
    pool = d["topic"].get("evidence_pool") or {}
    ns = {l.get("nombre") for l in pool.get("lugares") or []} | {t.get("lugar") for t in pool.get("cronologia") or []}
    ns |= {w for c in ctx.values() for w in c["where"]}
    return sorted({n for n in ns if n and len(n) > 2}, key=len, reverse=True)


def _pos_palabra(texto: str, pat: re.Pattern) -> str:
    m = pat.search(texto)
    if not m:
        return "—"
    return f"{len(texto[:m.start()].split()) + 1} («{m.group(0)}»)"


def escribir_prompts_ab(d: dict, canon_b: dict, ctx: dict, b1: list[dict], b2: list[dict]) -> None:
    lug = _lugares(d, ctx)
    pat_lugar = re.compile(r"\b(" + "|".join(re.escape(n) for n in lug) + r")\b", re.I) if lug else re.compile(r"$^")
    pat_anio = re.compile(r"\b(1[5-9]\d{2}|20\d{2})s?\b")
    L = ["# F46 — Prompts A / B1 / B2 del cap 2 de Wittenoom (salida de la parte 1)", "",
         "A = 03_visual.json (producción, lo que generó las fotos de hoy) · B1 = entrada nueva (canon desde la ficha + "
         "WHEN/WHERE/SCENES), estructura de hoy · B2 = los slots de B1 con la formula nueva, sin `mood`, estilo como "
         "slot con el año de la foto, sin anteponer. «Palabra n.º» cuenta desde 1 en el prompt entero.", ""]
    ov, nv = d["topic"].get("era_visual_canon") or {}, canon_b.get("era_visual_canon") or {}
    L += ["## Canon de época: viejo → nuevo", "", "| clave | viejo (topics_db, 10 verified_facts) | nuevo (ficha) |",
          "|---|---|---|"]
    for k in ("primary_decade", "spans", "clothing", "demographics"):
        L.append(f"| {k} | {str(ov.get(k) or '—').replace('|', '/')} | {str(nv.get(k) or '—').replace('|', '/')} |")
    L += ["", "## Tabla por foto", "",
          "| foto | beat | año | palabras A / B1 / B2 | año en palabra n.º A / B1 / B2 | primer lugar en palabra n.º A / B1 / B2 "
          "| sujeto+setting nombran época · lugar: A / B1 |", "|---|---|---|---|---|---|---|"]

    def nombra(it: dict) -> str:
        t = f"{it.get('subject') or ''} {it.get('setting') or ''}"
        return f"{'sí' if _EPOCA.search(t) else 'no'} · {'sí' if pat_lugar.search(t) else 'no'}"
    for i, (a, x1, x2) in enumerate(zip(d["v03"], b1, b2), start=1):
        anio = d["year_of_beat"].get(x1.get("beat"), d["year_topic"])
        ps = [a["prompt"], x1["prompt"], x2["prompt"]]
        L.append(f"| {i} | {x1.get('beat')} | {anio} | {' / '.join(str(len(p.split())) for p in ps)} | "
                 f"{' / '.join(_pos_palabra(p, pat_anio) for p in ps)} | "
                 f"{' / '.join(_pos_palabra(p, pat_lugar) for p in ps)} | {nombra(a)} / {nombra(x1)} |")
    L += ["", "## Contexto por beat (WHEN / WHERE / CASE-FILE SCENES)", ""]
    for n, c in ctx.items():
        L += [f"- beat {n} (ids {', '.join(c['ids'])}): WHEN {', '.join(c['when']) or '-'} · WHERE "
              f"{', '.join(c['where']) or '-'} · escenas: {' | '.join(c['escenas']) or '-'}"]
    L += ["", "## Los tres prompts enteros, por foto", ""]
    for i, (a, x1, x2) in enumerate(zip(d["v03"], b1, b2), start=1):
        L += [f"### Foto {i} · beat {x1.get('beat')}{' · cerrada' if x1.get('cerrada') else ''}", "",
              f"Ancla: «{a['narration_anchor']}»", "",
              f"**A** ({len(a['prompt'].split())} palabras):", "", "> " + a["prompt"], "",
              f"**B1** ({len(x1['prompt'].split())} palabras):", "", "> " + x1["prompt"], "",
              f"**B2** ({len(x2['prompt'].split())} palabras):", "", "> " + x2["prompt"], ""]
    (LAB / "PROMPTS_AB.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"  PROMPTS_AB.md: {len(b1)} fotos", flush=True)


# ─────────────────────────── parte 2 ───────────────────────────
def parte2() -> None:
    global _PREVIO
    import asset_manager as am
    from cost_tracker import cost_tracker
    from engine_profiles import select_profile
    from script_engine import image_grade
    costo_foto = select_profile("seedream").render.cost_usd
    _PREVIO = gastado_previo()
    cost_tracker.start_video(LAB_ID)
    reservado = {"n": 0}
    resultado: list[dict] = []
    trabajos = []
    for var in ("B1", "B2"):
        items = _j(LAB / f"{var}.json")["image_prompts"]
        for i, it in enumerate(items, start=1):
            trabajos.append((var, i, it["prompt"]))

    def una(var: str, i: int, prompt: str) -> dict:
        out = LAB / var / f"ch02_img_{i:02d}.png"
        if out.exists():
            image_grade.grade(out)
            return {"var": var, "foto": i, "estado": "ya estaba"}
        with _LOCK:
            freno(f"{var} foto {i}", costo_foto * (reservado["n"] + 1))
            reservado["n"] += 1
        try:
            meta = am._generate_image_raw(prompt, out, use_ultra=False)
            image_grade.grade(out)
            return {"var": var, "foto": i, "estado": "ok", "nsfw": meta.get("nsfw_flag"), "ms": meta.get("ms")}
        except am.ContentRejectedError as e:
            out.with_suffix(".rechazada.txt").write_text(str(e), encoding="utf-8")
            return {"var": var, "foto": i, "estado": f"rechazada: {str(e)[:200]}"}
        finally:
            with _LOCK:
                reservado["n"] -= 1
    try:
        with ThreadPoolExecutor(max_workers=am.FLUX_MAX_WORKERS) as ex:
            futs = [ex.submit(una, *t) for t in trabajos]
            for f in as_completed(futs):
                try:
                    r = f.result()
                except Parada as e:
                    r = {"estado": f"PARADA: {e}"}
                resultado.append(r)
                print(f"  {r}", flush=True)
    finally:
        cost_tracker.end_video()
    _w(LAB / "fotos_resultado.json", sorted(resultado, key=lambda r: (r.get("var", ""), r.get("foto", 0))))
    print(f"  parte 2: {sum(1 for r in resultado if r.get('estado') == 'ok')} fotos nuevas · cost_history {LAB_ID} "
          f"= US$ {gastado_previo():.4f}", flush=True)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    que = sys.argv[1] if len(sys.argv) > 1 else ""
    try:
        if que == "prompts":
            parte1()
        elif que == "fotos":
            parte2()
        else:
            print(__doc__)
            return 2
    except Parada as e:
        print(f"⛔ PARADA: {e}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
