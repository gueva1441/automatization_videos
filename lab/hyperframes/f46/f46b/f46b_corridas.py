"""F46b — el prompt de imagen «como cuchillo»: se arma solo, por código, con un expediente por foto (cap 2 de Wittenoom).

    canon C    el canon de B1 (step_4e con la ficha) regenerado con el BLOQUE EXTRA people_groups (texto 1 del handoff,
               al final del prompt de step_4e; el esquema de respuesta se amplía en este proceso para recibirlo).
    expediente por foto, por código: ancla y párrafo · beat (imagen_sensorial, emoción, intensidad) · AÑO (regla de la
               tabla del handoff, con de dónde salió) · DÓNDE · escenas de la ficha · citas del beat (texto entero) ·
               personas del beat (rol y lugar, sin nombre) · PEOPLE GROUPS del canon C.
    slots      UNA llamada a Pro (SI v3 de producción + el casillero `people_group`, texto 2; el expediente va con su
               encabezado, texto 3, después del bloque de beats de producción); anclas y beats de 03_visual (force_assign).
    C0         el CÓDIGO arma el prompt en el orden de la guía de Seedream 5 Lite: sujeto/acción → aspecto de la gente →
               mirada → objeto → lugar+año → estilo (style_head + STYLE_TAIL) → luz+paleta → plano/ángulo/lente →
               16:9 + «no text». Sin tejido de Flash, sin `mood`, sin el slot `style` (lleva «faceless»), sin cifras.
               Después las reglas F8 de producción (conteos, izquierda/derecha, escala, manos/cara/prohibidas/menores con
               su backstop de sacar la frase, nombres documentados, sensible, motivos).
    C1         C0 traducido al español por Flash (texto 4, solo traduce).      C2   C0 sin la oración de aspecto.
Producción no se edita: se importa. Freno antes de cada llamada paga; gasto en cost_history con el id `f46b-lab`.

    python lab/hyperframes/f46/f46b/f46b_corridas.py prompts   → canon_C.json, expedientes.md, C0/C1/C2.json, PROMPTS_C.md
    python lab/hyperframes/f46/f46b/f46b_corridas.py fotos     → C0/ C1/ C2/ (16 prompts × 2 fotos cada una) con su _graded
"""
from __future__ import annotations

import copy
import json
import re
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

LAB = Path(__file__).resolve().parent
ROOT = LAB.parents[3]
sys.path[:0] = [str(ROOT), str(LAB.parent)]
import f46_corridas as f46  # noqa: E402  (cargar, adaptador_facts: los mismos datos de F46)

TID, CAP = f46.TID, f46.CAP
LAB_ID = "f46b-lab"
TOPE_USD = 6.00                                       # Omar, al pegar el prompt de F46b
NUM_IMAGES = 2                                        # handoff F46b (medir la varianza)

# ── los 4 textos nuevos del handoff, tal cual ──
TEXTO_1_PEOPLE_GROUPS = """═══ BLOQUE EXTRA: people_groups ═══
Lista de los grupos de personas que el material documenta en este caso (hechos, cronología, escenas y citas de arriba). Por grupo, un objeto:
- id: corto, snake_case, en inglés (p. ej. "spanish_migrant_families")
- who: quiénes son y su origen documentado (EN, una frase)
- where_when: dónde y en qué años aparecen (EN, una frase)
- appearance: cómo se ven físicamente según su origen documentado y su época: tono de piel, color y tipo de pelo, rasgos, contextura típica de su trabajo (EN, una frase)
- clothing: ropa, peinado y accesorios de ESE grupo en ESOS años, ese clima y esa clase social (EN, una frase)
Sin nombres propios de personas. Solo grupos que el material documenta; si el material no dice el origen de un grupo, no lo inventes: dejá appearance vacío."""
TEXTO_2_PEOPLE_GROUP = ("- people_group: a LIST of ids from PEOPLE GROUPS whose members are visible in THIS image "
                        "(usually one); [] if no person is visible. Routing only — not rendered as text.")
TEXTO_3_ENCABEZADO = ("CASE FILE PER IMAGE — documented data. Use it to make each image specific to its place, year and "
                      "people; do not invent beyond it.")
TEXTO_4_TRADUCCION = ("Translate this image prompt into Spanish. Keep every number, year and proper place name exactly as "
                      "written. Return only the translated prompt.")

_LOCK = threading.Lock()
_PREVIO = 0.0


class Parada(RuntimeError):
    pass


_w, _j = f46._w, f46._j


# ─────────────────────────── gasto y freno ───────────────────────────
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


def freno(que: str, costo: float = 0.0) -> None:
    g = gastado()
    if g + costo > TOPE_USD:
        raise Parada(f"freno ({que}): gastado {g:.4f} + {costo:.4f} > tope {TOPE_USD:.2f}")


def _con_freno(fn, que: str):
    def envuelta(*a, **k):
        freno(f"{que} · {k.get('description') or ''}")
        return fn(*a, **k)
    return envuelta


# ─────────────────────────── canon C ───────────────────────────
def canon_c(d: dict) -> dict:
    from google.genai import types as gt
    from researcher_steps import step_4e_visual_canon as s4e
    crudo: dict = {}
    build_orig, flash_orig, schema_orig = s4e._build_prompt, s4e.call_flash_json, s4e._VISUAL_CANON_SCHEMA
    s4e._build_prompt = lambda *a, **k: build_orig(*a, **k).rstrip() + "\n\n" + TEXTO_1_PEOPLE_GROUPS
    s_str = gt.Schema(type=gt.Type.STRING, nullable=True)
    grupo = gt.Schema(type=gt.Type.OBJECT, properties={k: s_str for k in
                                                       ("id", "who", "where_when", "appearance", "clothing")})
    s4e._VISUAL_CANON_SCHEMA = gt.Schema(type=gt.Type.OBJECT, nullable=True, properties={
        **schema_orig.properties, "people_groups": gt.Schema(type=gt.Type.ARRAY, nullable=True, items=grupo)})

    def flash(*a, **k):
        freno("Flash canon C")
        r = flash_orig(*a, **k)
        if isinstance(r, dict):
            crudo.update(r)
        return r
    s4e.call_flash_json = flash
    try:
        topic = d["topic"]
        canon = s4e.extract_visual_canon(seed={"seed_title": topic.get("video_title")}, angle_blocks={},
                                         verified_facts=f46.adaptador_facts(d["ficha"]),
                                         canonical=topic.get("canonical_subject_description"))
    finally:
        s4e._build_prompt, s4e.call_flash_json, s4e._VISUAL_CANON_SCHEMA = build_orig, flash_orig, schema_orig
    canon["people_groups"] = [g for g in crudo.get("people_groups") or [] if isinstance(g, dict) and g.get("id")]
    return canon


# ─────────────────────────── expediente ───────────────────────────
def _anio_del_ancla(texto: str) -> str | None:
    """Primer año de 1800–2100 dicho en el texto: la primera cláusula que trae uno (`voz_utils.numeros` no devuelve
    las cifras en orden de aparición; por cláusula sí queda el orden)."""
    from script_engine import voz_utils as vu
    for cl in re.split(r"[.;:,¿?¡!]", texto or ""):
        ys = [y for y in vu.numeros(cl) if re.fullmatch(r"\d{4}", y) and 1800 <= int(y) <= 2100]
        if ys:
            return ys[0]
    return None


def _anclas_cap(v03_caps: dict, cap: int) -> list[str]:
    ch = v03_caps.get(cap) or {}
    if ch.get("image_prompts"):
        return [it["narration_anchor"] for it in ch["image_prompts"]]
    out = [ch["narration_anchor"]] if ch.get("narration_anchor") else []           # cap veo: el clip + los extras
    return out + [it["narration_anchor"] for it in ch.get("supplemental_image_prompts") or []]


def anios(d: dict) -> list[tuple[str, str]]:
    """(año, de dónde) por foto del cap, con la regla de la tabla del handoff."""
    v03_caps = {c["chapter_number"]: c for c in _j(f46.STEPS / TID / "03_visual.json")["chapters"]}

    def cadena(cap: int) -> list[str | None]:
        out, prev = [], None
        for a in _anclas_cap(v03_caps, cap):
            y = _anio_del_ancla(a) or prev
            out.append(y)
            prev = y
        return out
    ultimo_prev = None
    for c in range(1, CAP):
        for y in cadena(c):
            ultimo_prev = y or ultimo_prev
    by_n = {b["n"]: b for b in d["cap_beats"]}
    res: list[tuple[str, str]] = []
    for i, it in enumerate(d["v03"]):
        y = _anio_del_ancla(it["narration_anchor"])
        if y:
            res.append((y, "1) dicho en el ancla"))
        elif i > 0:
            res.append((res[-1][0], "2) el de la foto anterior del cap"))
        elif ultimo_prev:
            res.append((ultimo_prev, "3) el último del cap anterior"))
        elif re.match(r"\d{4}", (by_n.get(it.get("beat")) or {}).get("fecha") or ""):
            res.append((by_n[it["beat"]]["fecha"][:4], "4) la fecha del dato_central del beat"))
        else:
            res.append((d["year_topic"], "5) topic_year"))
    return res


def expedientes(d: dict, canon: dict, anios_: list[tuple[str, str]]) -> list[dict]:
    from script_engine import m03_imagenes_v3 as v3img
    pool = d["topic"].get("evidence_pool") or {}
    lugares = {l["id"]: l.get("nombre") for l in pool.get("lugares") or []}
    crono = {t["id"]: t for t in pool.get("cronologia") or []}
    citas = {q["id"]: q for q in pool.get("citas") or []}
    pers = {p["id"]: p for p in pool.get("personajes") or []}
    esc_beats = {b["n"]: b for b in d["esc"].get("beats") or []}
    by_n = {b["n"]: b for b in d["cap_beats"]}
    parrafos = _j(f46.STEPS / TID / "01b_narracion_v3.json").get("parrafos") or []
    out = []
    for i, (it, (anio, fuente)) in enumerate(zip(d["v03"], anios_), start=1):
        bn = it.get("beat")
        b = by_n.get(bn) or {}
        eb = esc_beats.get(bn) or {}
        ids = [x for x in [eb.get("dato_central"), *(eb.get("datos_apoyo") or [])] if x]
        ancla = it["narration_anchor"]
        clave = v3img._norm_ws(ancla)[:40]
        par = next((p["texto"] for p in parrafos if clave and clave in v3img._norm_ws(p.get("texto") or "")),
                   next((p["texto"] for p in parrafos if p.get("beat") == bn), ""))
        escenas = [e for e in d["ficha"].get("escenas") or [] if set(e.get("ids") or []) & set(ids)]
        donde: list[str] = []
        for x in [*((crono.get(i_) or {}).get("lugar") for i_ in ids), *(lugares.get(i_) for i_ in ids),
                  *(e.get("donde") for e in escenas)]:
            if x and x not in donde:
                donde.append(x)
        out.append({
            "foto": i, "ancla": ancla, "parrafo": par, "beat": bn, "imagen_sensorial": b.get("imagen_sensorial"),
            "emocion": b.get("emocion"), "intensidad": b.get("intensidad"), "anio": anio, "anio_fuente": fuente,
            "donde": donde,
            "escenas": [" · ".join(str(e.get(k) or "") for k in ("donde", "quien", "que_pasa", "sentidos")) for e in escenas],
            "citas": [citas[x].get("texto") for x in ids if x in citas],
            "personas": [f"{pers[x].get('rol') or ''}" + (f" ({pers[x]['lugar']})" if pers[x].get("lugar") else "")
                         for x in ids if x in pers]})
    return out


def bloque_expediente(exps: list[dict], canon: dict) -> str:
    L = ["", "═══════════════════════════════════════════════════", TEXTO_3_ENCABEZADO,
         "═══════════════════════════════════════════════════"]
    for e in exps:
        L += [f"  [{e['foto']}] YEAR: {e['anio']} · WHERE: {'; '.join(e['donde']) or '-'}",
              f"      PARAGRAPH: «{e['parrafo']}»",
              f"      SCENES: {' | '.join('«' + s + '»' for s in e['escenas']) or '-'}",
              f"      QUOTES: {' | '.join('«' + q + '»' for q in e['citas']) or '-'}",
              f"      PEOPLE (roles): {'; '.join(e['personas']) or '-'}"]
    L += ["PEOPLE GROUPS:"]
    for g in canon.get("people_groups") or []:
        L.append(f"  - {g.get('id')}: {g.get('who') or ''} · {g.get('where_when') or ''}")
    return "\n".join(L) + "\n"


# ─────────────────────────── slots (Pro) ───────────────────────────
def slots(d: dict, topic_c: dict, exps: list[dict], canon: dict) -> list[dict]:
    from script_engine import m03_imagenes_v3 as v3img
    from script_engine import m03_visual as m03
    anchors = [it["narration_anchor"] for it in d["v03"]]
    n = len(anchors)
    assign = [{"beat": it.get("beat"), "cerrada": bool(it.get("cerrada"))} for it in d["v03"]]
    lang = v3img.place_language(d["topic"])
    extra = v3img.beats_block(d["cap_beats"], assign, d["sch"].get("bullets"), lang) + bloque_expediente(exps, canon)
    prompt = m03._build_seedream_prompt_step2(topic_c, d["sch"], d["narr"], anchors, extra)
    si = m03.SYSTEM_INSTRUCTION_VISUAL_SEEDREAM_V3
    k = si.index("- foto_madre_ref:")
    fin = si.index("\n", k)
    si = si[:fin] + "\n" + TEXTO_2_PEOPLE_GROUP + si[fin:]
    schema = m03._seedream_slots_schema(n)
    schema["items"]["properties"]["people_group"] = {"type": "ARRAY", "items": {"type": "STRING"}}
    schema["items"]["required"].append("people_group")

    def validar(parsed):
        items = parsed.get("image_prompts") if isinstance(parsed, dict) else None
        if not isinstance(items, list) or len(items) != n:
            raise m03.VisualValidationError(f"se esperaban {n} slot-objects, llegaron "
                                            f"{len(items) if isinstance(items, list) else 'no-lista'}")
        for i, it in enumerate(items, start=1):
            if not isinstance(it, dict) or it.get("shot_scale") not in m03.VALID_SHOT_SCALES \
                    or not (it.get("subject") or "").strip():
                raise m03.VisualValidationError(f"item {i} inválido")
        return {"image_prompts": [{**items[i], "narration_anchor": anchors[i]} for i in range(n)]}
    out = m03._call_with_validation_retry(prompt, validar, CAP, system_instruction=si, response_schema=schema,
                                          use_pro=m03.SEEDREAM_SLOTS_USE_PRO, description="m03:slots f46b")
    (LAB / "prompt_slots_pro.txt").write_text(f"=== SYSTEM ===\n{si}\n\n=== USER ===\n{prompt}\n", encoding="utf-8")
    items = out["image_prompts"]
    for k_, it in enumerate(items):
        it["beat"], it["cerrada"] = assign[k_]["beat"], assign[k_]["cerrada"]
        gone = v3img.scrub_slots(it)                                   # F8 de producción sobre los slots
        why = v3img.fix_text_slot(it, lang)
        if why:
            gone.append(f"text_in_image: {why}")
        if gone:
            it["_f8_slots_scrub"] = gone
    return items


# ─────────────────────────── armado por código ───────────────────────────
def _oracion(x: str) -> str:
    x = re.sub(r"\s+", " ", str(x or "")).strip().rstrip(".,;")
    return (x[:1].upper() + x[1:] + ".") if x else ""


def armar(it: dict, anio: str, grupos: dict[str, dict], con_aspecto: bool) -> dict:
    from engine_profiles import select_profile
    from script_engine import m03_imagenes_v3 as v3img
    aspecto = []
    for gid in it.get("people_group") or []:
        g = grupos.get(gid)
        if not g:
            continue
        ap, ro = (g.get("appearance") or "").strip().rstrip("."), (g.get("clothing") or "").strip().rstrip(".")
        if ap:
            aspecto.append(f"The people are {ap}, wearing {ro}." if ro else f"The people are {ap}.")
        elif ro:
            aspecto.append(f"The people are wearing {ro}.")
    tii = it.get("text_in_image") or {}
    texto = ""
    if tii.get("present") and tii.get("text"):
        texto = _oracion(f'{tii.get("location") or "A sign"} reads "{tii["text"]}" in {tii.get("font") or "plain"} '
                         f'lettering, in clear crisp lettering')
    plano = ", ".join(str(x).strip().rstrip(".,; ") for x in
                      [f"{str(it.get('shot_scale') or '').replace('_', ' ')} shot", it.get("camera_angle"),
                       it.get("lens_technique")] if x and str(x).strip())
    partes = {
        "sujeto": " ".join(p for p in (_oracion(it.get("subject")), _oracion(it.get("action"))) if p),
        "aspecto": " ".join(aspecto) if con_aspecto else "",
        "mirada": _oracion(it.get("gaze_interaction")),
        "objeto": _oracion(it.get("props_detail")),
        "lugar_anio": _oracion(f"{str(it.get('setting') or '').strip().rstrip('.')}, {anio}"),
        "estilo": f"{v3img.style_head(anio)} {v3img.STYLE_TAIL}",
        "luz": " ".join(p for p in (_oracion(it.get("lighting")), _oracion(it.get("color_palette"))) if p),
        "tecnica": _oracion(plano),
        "texto": texto,
        "cierre": f"{select_profile('seedream').aspect_ratio_text}" + ("" if texto else f" {v3img.NO_TEXT}"),
    }
    return {"partes": partes, "prompt": " ".join(p for p in partes.values() if p)}


def f8(prompt: str, it: dict, escala: bool, documented) -> tuple[str, list[str]]:
    """Las reglas F8 de producción sobre la prosa armada (las de `_f8_finish_item` y el scrub de nombres del tejido);
    donde producción re-teje con Flash, acá va directo su backstop (sacar la frase): en C no hay tejido."""
    from script_engine import m03_imagenes_v3 as v3img
    from script_engine.name_matching import scrub_documented_names
    notas = []
    p, _ = scrub_documented_names(prompt, documented)
    p = v3img.fix_counts_lr(p)
    if escala:
        p = v3img.fix_scale(p)
    probs = v3img.problems(p, it.get("shot_scale"))
    if probs:
        notas = [f"{k}: {f}" for k, f in probs]
        p = v3img.scrub_sentence_problems(p, it.get("shot_scale"))
    if escala and re.search(v3img.HUMAN, p, re.I) and not v3img.SCALE_EN.search(p):
        p = p.rstrip() + " Hundreds of people fill the frame."
    return re.sub(r"\s+", " ", p).strip(), notas


def traducir(prompt: str) -> str:
    from google.genai import types as gt

    from config import api, gemini_client
    from cost_tracker import cost_tracker
    freno("Flash traducción C1")
    r = gemini_client.models.generate_content(model=api.gemini_model, contents=prompt,
                                              config=gt.GenerateContentConfig(system_instruction=TEXTO_4_TRADUCCION))
    cost_tracker.track_gemini_response(r, api.gemini_model, "f46b:traduccion C1")
    return re.sub(r"\s+", " ", (r.text or "")).strip()


# ─────────────────────────── parte 1 ───────────────────────────
def parte1() -> None:
    global _PREVIO
    from cost_tracker import cost_tracker
    from script_engine import m03_visual as m03
    d = f46.cargar()
    _PREVIO = gastado_previo()
    cost_tracker.start_video(LAB_ID)
    m03.call_flash_json = _con_freno(m03.call_flash_json, "Flash m03")
    m03.call_pro_json = _con_freno(m03.call_pro_json, "Pro m03")
    try:
        canon = canon_c(d)
        _w(LAB / "canon_C.json", {"facts_de_la_ficha": len(f46.adaptador_facts(d["ficha"])), **canon})
        print(f"  canon C: {len(canon['people_groups'])} people_groups · US$ {gastado():.4f}", flush=True)
        anios_ = anios(d)
        exps = expedientes(d, canon, anios_)
        escribir_expedientes(exps, canon)
        topic_c = {**d["topic"], **{k: canon[k] for k in f46.CANON_KEYS if k in canon}}
        items = slots(d, topic_c, exps, canon)
        print(f"  slots Pro: {len(items)} · US$ {gastado():.4f}", flush=True)
        grupos = {g["id"]: g for g in canon["people_groups"]}
        documented = topic_c.get("documented_people")
        by_n = {b["n"]: b for b in d["cap_beats"]}
        var = {"C0": [], "C2": []}
        for it, e in zip(items, exps):
            esc = bool((by_n.get(it.get("beat")) or {}).get("escala"))
            for v, con in (("C0", True), ("C2", False)):
                a = armar(it, e["anio"], grupos, con)
                p, notas = f8(a["prompt"], it, esc, documented)
                var[v].append({"foto": e["foto"], "beat": it.get("beat"), "anio": e["anio"],
                               "anio_fuente": e["anio_fuente"], "people_group": it.get("people_group") or [],
                               "partes": a["partes"], "prompt": p, "f8_problemas": notas,
                               "hard_fact_ids_fuera": it.get("hard_fact_ids") or [],
                               "slots": {k: v_ for k, v_ in it.items() if k not in ("narration_anchor",)}})
        c1: list[dict] = [None] * len(var["C0"])

        def tr(k: int, x: dict) -> None:
            c1[k] = {**{kk: vv for kk, vv in x.items() if kk not in ("prompt", "partes")}, "prompt": traducir(x["prompt"])}
        with ThreadPoolExecutor(max_workers=m03.FLUIDIFY_MAX_WORKERS) as ex:
            for f in as_completed([ex.submit(tr, k, x) for k, x in enumerate(var["C0"])]):
                f.result()
        var["C1"] = c1
        for v in ("C0", "C1", "C2"):
            _w(LAB / f"{v}.json", {"chapter_number": CAP, "image_prompts": var[v]})
        print(f"  C0/C1/C2 armados · US$ {gastado():.4f}", flush=True)
        escribir_prompts_c(d, exps, var)
    finally:
        cost_tracker.end_video()
    print(f"  parte 1: US$ {gastado_previo():.4f} en cost_history ({LAB_ID})", flush=True)


def escribir_expedientes(exps: list[dict], canon: dict) -> None:
    L = ["# F46b — Expedientes por foto (cap 2 de Wittenoom, por código)", "",
         "Lo que recibe Pro, por foto, después del bloque de beats de producción (con el encabezado del texto 3).", "",
         "## PEOPLE GROUPS (canon C)", ""]
    for g in canon.get("people_groups") or []:
        L += [f"- **{g.get('id')}** — who: {g.get('who')} · where_when: {g.get('where_when')} · appearance: "
              f"{g.get('appearance') or '(vacío)'} · clothing: {g.get('clothing')}"]
    for e in exps:
        L += ["", f"## Foto {e['foto']} · beat {e['beat']} · año {e['anio']} ({e['anio_fuente']})", "",
              f"- ancla: «{e['ancla']}»", f"- párrafo: «{e['parrafo']}»",
              f"- beat: SEEN «{e['imagen_sensorial']}» · emoción {e['emocion']} · intensidad {e['intensidad']}",
              f"- DÓNDE: {'; '.join(e['donde']) or '—'}",
              f"- escenas: {' | '.join(e['escenas']) or '—'}",
              f"- citas: {' | '.join('«' + q + '»' for q in e['citas']) or '—'}",
              f"- personas (rol, sin nombre): {'; '.join(e['personas']) or '—'}"]
    (LAB / "expedientes.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def escribir_prompts_c(d: dict, exps: list[dict], var: dict) -> None:
    def tiene_lugar(p: str, donde: list[str]) -> bool:
        toks = {w for x in donde for w in re.findall(r"[A-ZÁÉÍÓÚÑ][\wáéíóúñ'-]{3,}", x)}
        return any(re.search(rf"\b{re.escape(t)}\b", p) for t in toks)
    L = ["# F46b — Prompts C0 / C1 / C2 del cap 2 de Wittenoom (salida de la parte 1)", "",
         "C0 = armado por código (orden de la guía de Seedream 5 Lite) · C1 = C0 traducido al español por Flash · "
         "C2 = C0 sin la oración de aspecto. Sin `mood`, sin el slot `style`, sin cifras (`hard_fact_ids` fuera).", "",
         "## Chequeos por código", "",
         "| foto | año (de dónde) | grupos | palabras C0 / C1 / C2 | año C0 / C1 / C2 | lugar de DÓNDE C0 / C1 / C2 | aspecto C0 / C1 / C2 |",
         "|---|---|---|---|---|---|---|"]
    sn = lambda b: "sí" if b else "no"  # noqa: E731
    for e, a, b, c in zip(exps, var["C0"], var["C1"], var["C2"]):
        ps = [a["prompt"], b["prompt"], c["prompt"]]
        asp_c0 = bool(a["partes"]["aspecto"])
        L.append(f"| {e['foto']} | {e['anio']} ({e['anio_fuente']}) | {', '.join(a['people_group']) or '—'} | "
                 f"{' / '.join(str(len(p.split())) for p in ps)} | {' / '.join(sn(e['anio'] in p) for p in ps)} | "
                 f"{' / '.join(sn(tiene_lugar(p, e['donde'])) for p in ps)} | "
                 f"{sn(asp_c0)} / {sn(asp_c0)} (traducción) / {sn(bool(c['partes']['aspecto']))} |")
    L += ["", "## Los tres prompts enteros, por foto", ""]
    for e, a, b, c in zip(exps, var["C0"], var["C1"], var["C2"]):
        L += [f"### Foto {e['foto']} · beat {e['beat']} · año {e['anio']} ({e['anio_fuente']}) · grupos: "
              f"{', '.join(a['people_group']) or '—'}", "", f"Ancla: «{e['ancla']}»", ""]
        if a["f8_problemas"]:
            L += [f"Reglas F8 (frase sacada): {'; '.join(a['f8_problemas'])}", ""]
        if a["hard_fact_ids_fuera"]:
            L += [f"Cifras que quedaron fuera (hard_fact_ids): {', '.join(a['hard_fact_ids_fuera'])}", ""]
        for nom, x in (("C0", a), ("C1", b), ("C2", c)):
            L += [f"**{nom}** ({len(x['prompt'].split())} palabras):", "", "> " + x["prompt"], ""]
    (LAB / "PROMPTS_C.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("  PROMPTS_C.md listo", flush=True)


# ─────────────────────────── parte 2 ───────────────────────────
def generar_2(prompt: str, base: Path) -> dict:
    """Una llamada a Seedream 5 Lite con el payload de producción y num_images 2 → base_a.png y base_b.png."""
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
    rutas = []
    for suf, img in zip("ab", imgs):
        p = base.with_name(f"{base.name}_{suf}.png")
        p.parent.mkdir(parents=True, exist_ok=True)
        g = requests.get(img["url"], timeout=60)
        g.raise_for_status()
        p.write_bytes(g.content)
        rutas.append(p)
    cost_tracker.track_seedream(description=f"{base.name}: {prompt[:60]}...", images=len(imgs))
    return {"rutas": rutas, "nsfw": data.get("has_nsfw_concepts")}


def parte2() -> None:
    global _PREVIO
    import asset_manager as am
    from cost_tracker import cost_tracker
    from engine_profiles import select_profile
    from script_engine import image_grade
    costo = select_profile("seedream").render.cost_usd * NUM_IMAGES
    _PREVIO = gastado_previo()
    cost_tracker.start_video(LAB_ID)
    reservado = {"n": 0}
    trabajos = [(v, x["foto"], x["prompt"]) for v in ("C0", "C1", "C2") for x in _j(LAB / f"{v}.json")["image_prompts"]]

    def una(v: str, i: int, prompt: str) -> dict:
        base = LAB / v / f"ch02_img_{i:02d}"
        if base.with_name(base.name + "_a.png").exists():
            return {"var": v, "foto": i, "estado": "ya estaba"}
        with _LOCK:
            freno(f"{v} foto {i}", costo * (reservado["n"] + 1))
            reservado["n"] += 1
        try:
            res = generar_2(prompt, base)
            for p in res["rutas"]:
                image_grade.grade(p)
            return {"var": v, "foto": i, "estado": "ok", "fotos": len(res["rutas"]), "nsfw": res["nsfw"]}
        except am.ContentRejectedError as e:
            (LAB / v).mkdir(parents=True, exist_ok=True)
            (LAB / v / f"ch02_img_{i:02d}.rechazada.txt").write_text(str(e), encoding="utf-8")
            return {"var": v, "foto": i, "estado": f"rechazada: {str(e)[:200]}"}
        finally:
            with _LOCK:
                reservado["n"] -= 1
    resultado = []
    try:
        with ThreadPoolExecutor(max_workers=am.FLUX_MAX_WORKERS) as ex:
            for f in as_completed([ex.submit(una, *t) for t in trabajos]):
                try:
                    r = f.result()
                except Parada as e:
                    r = {"estado": f"PARADA: {e}"}
                except Exception as e:  # noqa: BLE001 — una foto que falla no tira las demás; se reporta
                    r = {"estado": f"error: {type(e).__name__}: {str(e)[:200]}"}
                resultado.append(r)
                print(f"  {r}", flush=True)
    finally:
        cost_tracker.end_video()
    _w(LAB / "fotos_resultado.json", sorted(resultado, key=lambda r: (r.get("var", ""), r.get("foto", 0))))
    print(f"  parte 2: {sum(1 for r in resultado if r.get('estado') == 'ok')} prompts ok · cost_history {LAB_ID} = "
          f"US$ {gastado_previo():.4f}", flush=True)


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
