"""F47 — ¿Sirve C2 para cualquier historia? Medido solo en texto (caps 5, 6, 7 de Wittenoom) + D (Claude Fable llenando
los casilleros, caps 2, 5, 6, 7). Cero fotos, cero fal.

    C2   f46b tal cual: expediente por foto → UNA llamada a Pro (SI v3 + `people_group`, user-prompt con beats + expediente)
         → armado por código sin la oración de aspecto → F8 de producción con backstop.
    D    C2 con un solo cambio: los casilleros los llena `claude-fable-5-1` (effort high) por `claude_helpers.call_json`,
         con el MISMO system, el MISMO user-prompt, el MISMO esquema y la MISMA validación (`f46b_corridas.slots`).
Se reusa `f46b_corridas` importado (anios, expedientes, slots, armar, f8) y el canon `f46b/canon_C.json` sin regenerar.
Dentro de este proceso, `m03_visual.call_pro_json` se reemplaza por un ruteador por hilo (C2 → el Pro de producción;
D → Fable); si Fable devuelve un array en la raíz se envuelve en {"image_prompts": …}, lo mismo que hace
`gemini_helpers._try_json_parse` para Pro. El cap 7 (Veo) se arma sobre sus `supplemental_image_prompts`.
Freno antes de cada llamada; gasto en cost_history con el id `f47-lab`.

    python lab/hyperframes/f47/f47_corridas.py prompts      → expedientes_F47.md, slots_*_chNN.json, PROMPTS_F47.md, COSTOS.md
    python lab/hyperframes/f47/f47_corridas.py seco <dir>   → lo mismo en <dir>, sin API (prueba del armado)
"""
from __future__ import annotations

import copy
import hashlib
import json
import re
import sys
import tempfile
import threading
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

LAB = Path(__file__).resolve().parent
ROOT = LAB.parents[2]
F46 = ROOT / "lab" / "hyperframes" / "f46"
sys.path[:0] = [str(ROOT), str(F46), str(F46 / "f46b")]
import f46_corridas as f46  # noqa: E402
import f46b_corridas as f46b  # noqa: E402

TID = f46.TID
LAB_ID = "f47-lab"
TOPE_USD = 6.00                                       # Omar, al pegar el prompt de F47 (lab/TOPE_TANDA.json)
CAPS_C2 = (5, 6, 7)                                   # handoff F47 §Constantes (los de otra época, ENTRADA 28c)
CAPS_D = (2, 5, 6, 7)                                 # handoff F47 §Constantes (cap 2: C2 ya tiene fotos en F46b)
MODELO_D = "claude-fable-5-1"                         # handoff F47 §Constantes (Omar 02:55 pidió un Claude)
MODELOS = {"D": MODELO_D}                             # variante → modelo Claude (F47b agrega E y F)
CANON_C = F46 / "f46b" / "canon_C.json"

_TL = threading.local()
_PRO_ORIG = None
_SECO = False                                         # `seco`: sin API (casilleros falsos desde 03_visual), para probar el armado
_PREVIO = 0.0
_w, _j = f46._w, f46._j


class Parada(RuntimeError):
    pass


# ─────────────────────────── gasto y freno (los de f46b, con el id de F47) ───────────────────────────
def gastado_previo() -> float:
    from cost_tracker import cost_tracker
    f = cost_tracker.HISTORY_FILE
    if not f.exists():
        return 0.0
    try:
        h = json.loads(f.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        h = json.loads(f.read_text(encoding="cp1252"))
    return round(sum(float(r.get("total_cost") or 0) for r in h if isinstance(r, dict) and r.get("video_id") == LAB_ID), 4)


def gastado() -> float:
    from cost_tracker import cost_tracker
    cv = cost_tracker.current_video
    return round(_PREVIO + (cv.total_cost if cv else 0.0), 4)


def freno(que: str) -> None:
    g = gastado()
    if g > TOPE_USD:
        raise Parada(f"freno ({que}): gastado {g:.4f} > tope {TOPE_USD:.2f}")


# ─────────────────────────── datos (solo lectura) ───────────────────────────
def cargar(cap: int) -> dict:
    """`f46.cargar` con el cap como parámetro; en un cap Veo las fotos son sus `supplemental_image_prompts`."""
    import fase1_5
    from script_engine import m03_imagenes_v3 as v3img
    topic = copy.deepcopy(fase1_5._load_topic_by_id(TID))
    skel = fase1_5._load_skeleton(TID)
    narr = fase1_5._load_narration(TID)
    sch = next(c for c in skel["chapters"] if c["chapter_number"] == cap)
    nch = next(c for c in narr["chapters"] if c["chapter_number"] == cap)
    ch = next(c for c in _j(f46.STEPS / TID / "03_visual.json")["chapters"] if c["chapter_number"] == cap)
    v03 = ch.get("image_prompts") or ch.get("supplemental_image_prompts") or []
    beats = v3img.load_beats(topic, f46.STEPS)
    year_topic = v3img.topic_year(topic, beats)
    return {"cap": cap, "topic": topic, "sch": sch, "narr": (nch.get("narration") or "").strip(), "v03": v03,
            "beats": beats, "cap_beats": beats[cap], "year_topic": year_topic,
            "ficha": _j(f46.STEPS / TID / "ficha_caso.json"), "esc": _j(f46.STEPS / TID / "01a_escaleta.json"),
            "veo": None if ch.get("image_prompts") else {k: ch.get(k) for k in
                                                          ("narration_anchor", "veo_position", "image_prompt",
                                                           "video_prompt")}}


# ─────────────────────────── ruteador del modelo (por hilo) ───────────────────────────
def _md5(x) -> str:
    s = x if isinstance(x, str) else json.dumps(x, ensure_ascii=False, sort_keys=True)
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def ruteador(prompt, system_instruction=None, response_schema=None, thinking_budget=None, description=None):
    import claude_helpers
    from script_engine import guion_v4
    var, cap = _TL.var, _TL.cap
    _TL.intento += 1
    desc = f"f47 {var} ch{cap:02d} slots (intento {_TL.intento})"
    _TL.pedidos.append({"intento": _TL.intento, "md5_system": _md5(system_instruction or ""),
                        "md5_user": _md5(prompt), "md5_schema": _md5(response_schema)})
    if _TL.intento == 1:
        (LAB / "pedidos").mkdir(exist_ok=True)
        (LAB / "pedidos" / f"pedido_{var}_ch{cap:02d}.txt").write_text(
            f"=== SYSTEM ===\n{system_instruction}\n\n=== USER ===\n{prompt}\n", encoding="utf-8")
    freno(desc)
    t0 = time.time()
    if _SECO:
        raw = {"image_prompts": [{"subject": (it.get("subject") or it.get("prompt") or "x").split(".")[0],
                                  "shot_scale": it.get("shot_scale") or "wide", "people_group": [],
                                  **{k: it.get(k) for k in ("action", "setting", "lighting", "text_in_image")}}
                                 for it in _TL.v03]}
    elif var == "C2":
        raw = _PRO_ORIG(prompt, system_instruction=system_instruction, response_schema=response_schema,
                        description=desc)
    else:
        raw = claude_helpers.call_json(prompt, model=MODELOS[var], system_instruction=system_instruction,
                                       response_schema=response_schema, effort=guion_v4.ESFUERZO[MODELO_D],
                                       description=desc)
        if isinstance(raw, list):                     # igual que gemini_helpers._try_json_parse (array → wrapper)
            raw = {"image_prompts": raw}
    _TL.crudos.append({"intento": _TL.intento, "segundos": round(time.time() - t0, 1), "respuesta": raw})
    return raw


def una_variante(var: str, cap: int, d: dict, topic_c: dict, exps: list[dict], canon: dict) -> dict:
    _TL.var, _TL.cap, _TL.intento, _TL.pedidos, _TL.crudos, _TL.v03 = var, cap, 0, [], [], d["v03"]
    out = {"var": var, "cap": cap}
    try:
        out["items"] = f46b.slots(d, topic_c, exps, canon)
        out["estado"] = "ok"
    except Parada:
        raise
    except Exception as e:  # noqa: BLE001 — una negativa o un JSON roto se reporta tal cual; no tira las demás
        out["estado"] = f"{type(e).__name__}: {e}"
    out["pedidos"], out["crudos"] = _TL.pedidos, _TL.crudos
    _w(LAB / f"slots_{var}_ch{cap:02d}.json", out)
    print(f"  {var} ch{cap:02d}: {out['estado'][:200]} · intentos {_TL.intento} · US$ {gastado():.4f}", flush=True)
    return out


# ─────────────────────────── armado (C2 de f46b: sin aspecto) ───────────────────────────
def armar_c2(items: list[dict], exps: list[dict], d: dict, canon: dict, documented) -> list[dict]:
    grupos = {g["id"]: g for g in canon.get("people_groups") or []}
    by_n = {b["n"]: b for b in d["cap_beats"]}
    res = []
    for it, e in zip(items, exps):
        esc = bool((by_n.get(it.get("beat")) or {}).get("escala"))
        a = f46b.armar(it, e["anio"], grupos, False)
        p, notas = f46b.f8(a["prompt"], it, esc, documented)
        res.append({"foto": e["foto"], "beat": it.get("beat"), "anio": e["anio"], "anio_fuente": e["anio_fuente"],
                    "people_group": it.get("people_group") or [], "partes": a["partes"], "prompt": p,
                    "f8_problemas": notas, "f8_slots_scrub": it.get("_f8_slots_scrub") or [],
                    "hard_fact_ids_fuera": it.get("hard_fact_ids") or [],
                    "slots": {k: v for k, v in it.items() if k != "narration_anchor"}})
    return res


# ─────────────────────────── corrida ───────────────────────────
def prompts() -> None:
    global _PREVIO, _PRO_ORIG
    from cost_tracker import cost_tracker
    from script_engine import m03_visual as m03
    canon = {k: v for k, v in _j(CANON_C).items() if k != "facts_de_la_ficha"}
    datos: dict[int, dict] = {}
    for cap in sorted(set(CAPS_C2) | set(CAPS_D)):          # secuencial: f46b.anios lee f46b.CAP
        d = cargar(cap)
        f46b.CAP = cap
        anios_ = f46b.anios(d)
        exps = f46b.expedientes(d, canon, anios_)
        topic_c = {**d["topic"], **{k: canon[k] for k in f46.CANON_KEYS if k in canon}}
        datos[cap] = {"d": d, "exps": exps, "topic_c": topic_c}
    f46b.CAP = 0                                              # solo aparece en logs de reintento
    escribir_expedientes(datos, canon)
    f46b.LAB = Path(tempfile.mkdtemp(prefix="f47_"))         # f46b.slots escribe ahí su prompt_slots_pro.txt (no en f46b/)
    _PREVIO = gastado_previo()
    if not _SECO:
        cost_tracker.start_video(LAB_ID)
    _PRO_ORIG, m03.call_pro_json = m03.call_pro_json, ruteador
    trabajos = [("C2", c) for c in CAPS_C2] + [("D", c) for c in CAPS_D]
    res: dict[tuple[str, int], dict] = {}
    try:
        with ThreadPoolExecutor(max_workers=len(trabajos)) as ex:      # todas las llamadas en paralelo
            futs = {ex.submit(una_variante, v, c, datos[c]["d"], datos[c]["topic_c"], datos[c]["exps"], canon): (v, c)
                    for v, c in trabajos}
            for f in as_completed(futs):
                try:
                    res[futs[f]] = f.result()
                except Parada as e:
                    res[futs[f]] = {"var": futs[f][0], "cap": futs[f][1], "estado": f"PARADA: {e}"}
    finally:
        m03.call_pro_json = _PRO_ORIG
        if not _SECO:
            cost_tracker.end_video()
    variantes: dict[tuple[str, int], list[dict]] = {}
    for (v, c), r in res.items():
        if r.get("estado") == "ok":
            variantes[(v, c)] = armar_c2(r["items"], datos[c]["exps"], datos[c]["d"], canon,
                                         datos[c]["topic_c"].get("documented_people"))
    c2_f46b = _j(F46 / "f46b" / "C2.json")["image_prompts"]           # C2 del cap 2 = el de F46b (ya tiene fotos)
    variantes[("C2", 2)] = c2_f46b
    _w(LAB / "PROMPTS_F47.json", {f"{v}_ch{c:02d}": x for (v, c), x in variantes.items()})
    escribir_prompts(datos, canon, variantes, res)
    escribir_costos()
    print(f"  F47: US$ {gastado_previo():.4f} en cost_history ({LAB_ID})", flush=True)


# ─────────────────────────── salidas ───────────────────────────
def escribir_expedientes(datos: dict, canon: dict) -> None:
    L = ["# F47 — Expedientes por foto (Wittenoom, caps 2, 5, 6, 7; por código con `f46b_corridas.expedientes`)", "",
         "Lo que reciben Pro (C2) y Fable (D), por foto, después del bloque de beats de producción. El cap 7 (Veo) "
         "sobre sus `supplemental_image_prompts`.", "", "## PEOPLE GROUPS (canon C de F46b, sin regenerar)", ""]
    for g in canon.get("people_groups") or []:
        L.append(f"- **{g.get('id')}** — who: {g.get('who')} · where_when: {g.get('where_when')}")
    for cap, x in datos.items():
        L += ["", f"# Cap {cap}" + (" (Veo: fotos suplementarias)" if x["d"]["veo"] else ""), ""]
        for e in x["exps"]:
            L += [f"## Cap {cap} · foto {e['foto']} · beat {e['beat']} · año {e['anio']} ({e['anio_fuente']})", "",
                  f"- ancla: «{e['ancla']}»", f"- párrafo: «{e['parrafo']}»",
                  f"- beat: SEEN «{e['imagen_sensorial']}» · emoción {e['emocion']} · intensidad {e['intensidad']}",
                  f"- DÓNDE: {'; '.join(e['donde']) or '—'}",
                  f"- escenas: {' | '.join(e['escenas']) or '—'}",
                  f"- citas: {' | '.join('«' + q + '»' for q in e['citas']) or '—'}",
                  f"- personas (rol, sin nombre): {'; '.join(e['personas']) or '—'}", ""]
    (LAB / "expedientes_F47.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def _spans(canon: dict) -> tuple[int, int] | None:
    ys = [int(y) for y in re.findall(r"\d{4}", str((canon.get("era_visual_canon") or {}).get("spans") or ""))]
    return (min(ys), max(ys)) if ys else None


def _tiene_lugar(p: str, donde: list[str]) -> list[str]:
    """La misma regla de F46b (`escribir_prompts_c.tiene_lugar`): palabras con mayúscula de ≥4 letras del DÓNDE."""
    toks = {w for x in donde for w in re.findall(r"[A-ZÁÉÍÓÚÑ][\wáéíóúñ'-]{3,}", x)}
    return sorted(t for t in toks if re.search(rf"\b{re.escape(t)}\b", p))


def _nombres(topic: dict, canon: dict) -> list[str]:
    ns = [p.get("name") for p in canon.get("documented_people") or [] if isinstance(p, dict)]
    ns += [p.get("nombre") for p in (topic.get("evidence_pool") or {}).get("personajes") or []]
    return sorted({n for n in ns if n}, key=len, reverse=True)


def _sale(nombre: str, texto: str) -> bool:
    """Nombre entero, o su último token con mayúscula de ≥4 letras (el apellido), como palabra."""
    if re.search(rf"\b{re.escape(nombre)}\b", texto, re.I):
        return True
    caps = [t for t in nombre.split() if t[:1].isupper() and len(t) >= 4]
    return bool(caps) and len(nombre.split()) > 1 and bool(re.search(rf"\b{re.escape(caps[-1])}\b", texto))


def chequeos(x: dict, e: dict, canon: dict, topic: dict, lang: str) -> dict:
    from script_engine import m03_imagenes_v3 as v3img
    p = x["prompt"]
    sp = _spans(canon)
    nombres = _nombres(topic, canon)
    en_ancla = [n for n in nombres if _sale(n, e["ancla"])]
    tii = (x.get("slots") or {}).get("text_in_image") or {}
    return {
        "anio": f"{e['anio']} ({e['anio_fuente']})",
        "en_canon": "sí" if sp and sp[0] <= int(e["anio"]) <= sp[1] else "año fuera del canon",
        "lugar": _tiene_lugar(p, e["donde"]),
        "gente_sin_grupo": bool(re.search(v3img.HUMAN, p, re.I)) and not x.get("people_group"),
        "nombres_ancla": en_ancla, "nombres_prosa": [n for n in en_ancla if _sale(n, p)],
        "texto": (f"sí «{tii.get('text')}» ({lang})" if tii.get("present") and tii.get("text") else "no"),
        "f8": [*(x.get("f8_slots_scrub") or (x.get("slots") or {}).get("_f8_slots_scrub") or []),
               *x.get("f8_problemas", [])],
        "palabras": len(p.split()),
    }


def escribir_prompts(datos: dict, canon: dict, variantes: dict, res: dict) -> None:
    from script_engine import m03_imagenes_v3 as v3img
    sn = lambda b: "sí" if b else "no"  # noqa: E731
    ev = canon.get("era_visual_canon") or {}
    L = ["# F47 — Prompts C2 | D en texto (Wittenoom, caps 2, 5, 6, 7) — salida de la parte única", "",
         "C2 = f46b tal cual (Pro llena los casilleros; armado por código sin la oración de aspecto; F8 con backstop). "
         "D = lo mismo con `claude-fable-5-1` (effort high) llenando los casilleros. Cap 2: C2 es el de F46b "
         "(`f46b/C2.json`, ya tiene fotos); D se corrió acá. Cap 7 (Veo): sobre sus `supplemental_image_prompts`.", "",
         f"Canon (uno por video): `primary_decade` {ev.get('primary_decade')} · `spans` {ev.get('spans')}", "",
         f"`condition_evolution`: {ev.get('condition_evolution')}", "",
         f"`forbidden_anachronisms`: {ev.get('forbidden_anachronisms')}", "", "## Estado de cada llamada", "",
         "| variante | cap | estado | intentos | md5 system / user / esquema (1.er intento) |", "|---|---|---|---|---|"]
    for (v, c), r in sorted(res.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        p0 = (r.get("pedidos") or [{}])[0]
        L.append(f"| {v} | {c} | {r.get('estado', '')[:300]} | {len(r.get('pedidos') or [])} | "
                 f"{p0.get('md5_system', '—')[:8]} / {p0.get('md5_user', '—')[:8]} / {p0.get('md5_schema', '—')[:8]} |")
    for cap in sorted(datos):
        d, exps = datos[cap]["d"], datos[cap]["exps"]
        lang = v3img.place_language(d["topic"])
        c2, dd = variantes.get(("C2", cap)), variantes.get(("D", cap))
        L += ["", f"# Cap {cap}" + (" (Veo)" if d["veo"] else ""), ""]
        for k, e in enumerate(exps):
            a = c2[k] if c2 else None
            b = dd[k] if dd else None
            L += [f"## Cap {cap} · foto {e['foto']} · beat {e['beat']}", "", f"- ancla: «{e['ancla']}»",
                  f"- año: {e['anio']} ({e['anio_fuente']})", f"- DÓNDE: {'; '.join(e['donde']) or '—'}",
                  f"- grupos C2 | D: {', '.join(a['people_group']) if a else '(sin C2)'} | "
                  f"{', '.join(b['people_group']) if b else '(sin D)'}", ""]
            for nom, x in (("C2", a), ("D", b)):
                if x is None:
                    L += [f"**{nom}**: — (la llamada no devolvió casilleros; ver «Estado de cada llamada»)", ""]
                    continue
                L += [f"**{nom}** ({len(x['prompt'].split())} palabras):", "", "> " + x["prompt"], ""]
    # tabla de los 8 chequeos
    L += ["", "## Tabla de los 8 chequeos (por foto; C2 | D)", "",
          "1 año (fuente) · 2 año dentro de `spans` · 3 lugar del DÓNDE en la prosa · 4 gente sin grupo · "
          "5 nombres reales en el ancla → en la prosa · 6 `text_in_image` (idioma de `place_language`) · "
          "7 notas F8 · 8 palabras", "",
          "| cap · foto | 1 año (fuente) | 2 en canon | 3 lugar C2 \\| D | 4 gente sin grupo C2 \\| D | "
          "5 nombres ancla → prosa C2 \\| D | 6 texto C2 \\| D | 7 F8 C2 \\| D | 8 palabras C2 \\| D |",
          "|---|---|---|---|---|---|---|---|---|"]
    for cap in sorted(datos):
        d, exps = datos[cap]["d"], datos[cap]["exps"]
        lang = v3img.place_language(d["topic"])
        c2, dd = variantes.get(("C2", cap)), variantes.get(("D", cap))
        tot = {"C2": {"lugar": 0, "sin": 0, "nom": 0, "txt": 0, "f8": 0, "pal": 0, "n": 0},
               "D": {"lugar": 0, "sin": 0, "nom": 0, "txt": 0, "f8": 0, "pal": 0, "n": 0}}
        fuera = 0
        for k, e in enumerate(exps):
            ch = {}
            for nom, xs in (("C2", c2), ("D", dd)):
                if xs:
                    ch[nom] = q = chequeos(xs[k], e, canon, d["topic"], lang)
                    t = tot[nom]
                    t["n"] += 1
                    t["lugar"] += bool(q["lugar"])
                    t["sin"] += q["gente_sin_grupo"]
                    t["nom"] += bool(q["nombres_prosa"])
                    t["txt"] += q["texto"] != "no"
                    t["f8"] += bool(q["f8"])
                    t["pal"] += q["palabras"]
            q0 = ch.get("C2") or ch.get("D")
            if not q0:
                continue
            fuera += q0["en_canon"] != "sí"

            def col(f):
                return " \\| ".join(f(ch[n]) if n in ch else "—" for n in ("C2", "D"))
            L.append(
                f"| {cap} · {e['foto']} | {q0['anio']} | {q0['en_canon']} | "
                f"{col(lambda q: ', '.join(q['lugar']) or 'no')} | {col(lambda q: sn(q['gente_sin_grupo']))} | "
                f"{', '.join(q0['nombres_ancla']) or '—'} → {col(lambda q: ', '.join(q['nombres_prosa']) or 'no')} | "
                f"{col(lambda q: q['texto'].replace('|', '/'))} | "
                f"{col(lambda q: '; '.join(q['f8']).replace('|', '/') or '—')} | {col(lambda q: str(q['palabras']))} |")

        def tc(f):
            return " \\| ".join(f(tot[n]) if tot[n]["n"] else "—" for n in ("C2", "D"))
        L.append(f"| **cap {cap} total** ({len(exps)} fotos) | — | **{fuera} fuera** | "
                 f"**{tc(lambda t: str(t['lugar']))}** | **{tc(lambda t: str(t['sin']))}** | "
                 f"**{tc(lambda t: str(t['nom']))} con nombre en la prosa** | **{tc(lambda t: str(t['txt']))}** | "
                 f"**{tc(lambda t: str(t['f8']))}** | **{tc(lambda t: str(round(t['pal'] / t['n'])) + ' prom.')}** |")
    # por cap: grupos y el setting (para leer el estado de condition_evolution)
    L += ["", "## Por cap: `people_group` y el setting de cada foto (estado de `condition_evolution`: lo lee el analista)",
          ""]
    for cap in sorted(datos):
        c2, dd = variantes.get(("C2", cap)), variantes.get(("D", cap))
        L += [f"### Cap {cap}", "", "| foto | grupos C2 | grupos D | setting C2 | setting D |", "|---|---|---|---|---|"]
        for k, e in enumerate(datos[cap]["exps"]):
            def s(xs, key):
                if not xs:
                    return "—"
                v = xs[k]["people_group"] if key == "g" else (xs[k].get("slots") or {}).get("setting")
                return (", ".join(v) or "[]") if key == "g" else str(v or "—").replace("|", "/")
            L.append(f"| {e['foto']} | {s(c2, 'g')} | {s(dd, 'g')} | {s(c2, 's')} | {s(dd, 's')} |")
        L.append("")
    veo = datos.get(7, {}).get("d", {}).get("veo")
    if veo:
        L += ["## Cap 7 (Veo): el `video_prompt` del clip, entero y sin evaluar", "",
              f"Clips Veo en el cap: 1 (`veo_position` {veo.get('veo_position')}). Ancla del clip: "
              f"«{veo.get('narration_anchor')}»", "", "> " + str(veo.get("video_prompt")), ""]
    (LAB / "PROMPTS_F47.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("  PROMPTS_F47.md listo", flush=True)


def escribir_costos() -> None:
    from cost_tracker import cost_tracker
    try:
        h = json.loads(cost_tracker.HISTORY_FILE.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        h = json.loads(cost_tracker.HISTORY_FILE.read_text(encoding="cp1252"))
    regs = [r for r in h if isinstance(r, dict) and r.get("video_id") == LAB_ID]
    L = [f"# F47 — costos reales (`data/cost_history.json`, video_id {LAB_ID}; {len(regs)} reporte/s)", "",
         "| servicio | descripción | tokens in / out | costo US$ |", "|---|---|---|---:|"]
    sub: dict[str, float] = {}
    for r in regs:
        for e in r.get("entries", []):
            sub[e.get("service", "?")] = sub.get(e.get("service", "?"), 0.0) + float(e.get("total_cost") or 0)
            L.append(f"| {e.get('service')} | {e.get('description')} | {e.get('tokens_in', '—')} / "
                     f"{e.get('tokens_out', '—')} | {float(e.get('total_cost') or 0):.4f} |")
    L += [""] + [f"- **{k}**: US$ {v:.4f}" for k, v in sub.items()]
    L.append(f"- **Total**: US$ {sum(float(r.get('total_cost') or 0) for r in regs):.4f} (tope {TOPE_USD:.2f})")
    (LAB / "COSTOS.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def main() -> int:
    global _SECO, LAB
    sys.stdout.reconfigure(encoding="utf-8")
    que = sys.argv[1] if len(sys.argv) > 1 else ""
    if que == "seco":
        _SECO, LAB = True, Path(sys.argv[2])
        LAB.mkdir(parents=True, exist_ok=True)
    elif que != "prompts":
        print(__doc__)
        return 2
    try:
        prompts()
    except Parada as e:
        print(f"⛔ PARADA: {e}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
