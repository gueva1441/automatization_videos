"""F48 — Que al prompt de foto le llegue lo que el research ya tiene: etapas acumuladas S1 → S5, medidas en texto con
Opus 5.5 (effort high, el de D/E) en los caps 2, 5, 6, 7 de Wittenoom. Cero fotos, cero fal.

    S0  = E de F47b (Opus, pedido de F47; se lee de PROMPTS_F47b.json, no se re-corre).
    S1  producción ya cambiada (commit f48-s1): GEO/ERA en el pedido (`m03._geo_era`) y sin «UBICACIONES DOCUMENTADAS».
    S2  + FACTS por foto en el expediente (`datos.texto` y `cronologia` «fecha · evento» de los ids del beat, enteros).
    S3  + PEOPLE por foto (rol · lugar · años, sin nombre): `personajes` de los ids del beat ∪ los que el ancla nombra
        con su `nombre` entero. Reemplaza «PEOPLE (roles)».
    S4  + casillero `year` (SI y esquema); año final = 1) dicho en el ancla, 2) `year` del modelo, 3)–5) respaldo de F46b
        (último del cap anterior, fecha del `dato_central`, `topic_year`); se borra «el de la foto anterior del cap»; la
        línea YEAR del expediente muestra solo el año del ancla o «-»; en la prosa el año va una vez.
    S5  + canon con `people_groups` regenerados por step_4e con la lista de `personajes` al final del texto 1 de F46b
        (el resto del canon es el de F46b: solo cambian los grupos).
Producción no se toca en S2–S5: f46b/f47 se importan y lo de cada etapa se parchea solo en este proceso, etapa por etapa
(las etapas van en secuencia; dentro de cada una, las 4 llamadas en paralelo). Freno antes de cada llamada; gasto en
cost_history con el id `f48-lab`.

    python lab/hyperframes/f48/f48_corridas.py prompts     → slots_S{n}_chNN.json, pedidos/, canon_S5.json, PROMPTS_F48.md
    python lab/hyperframes/f48/f48_corridas.py seco <dir>  → lo mismo en <dir>, sin API
"""
from __future__ import annotations

import copy
import difflib
import json
import re
import sys
import tempfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

LAB = Path(__file__).resolve().parent
F47 = LAB.parent / "f47"
sys.path.insert(0, str(F47))
import f47b_corridas as f47b  # noqa: E402  (al importarse fija LAB_ID/tope de F47b: se pisan abajo)
import f47_corridas as f47  # noqa: E402

f46, f46b = f47.f46, f47.f46b
f47.LAB = LAB
f47.LAB_ID = "f48-lab"
f47.TOPE_USD = 7.00                                   # Omar, al pegar el prompt de F48 (lab/TOPE_TANDA.json)
MODELO = "claude-opus-5-5"                            # handoff F48 §Constantes (F47b E; Omar 03:30–03:34)
ETAPAS = ("S1", "S2", "S3", "S4", "S5")
CAPS = (2, 5, 6, 7)                                   # handoff F48 §Constantes (los de F47/F47b)
f47.MODELOS.update({s: MODELO for s in ETAPAS})
_w, _j = f47._w, f47._j

# ── los textos nuevos del handoff F48, tal cual (no hay otros) ──
TEXTO_S4_YEAR = ("- year: the year (YYYY) in which THIS image's scene takes place, read from the narration fragment, its "
                 "paragraph and the case file (a year said earlier in the paragraph, «ten years before» a stated year, "
                 "«now» = the most recent year in the case file). Routing only — not rendered as text.")
TEXTO_S5 = ("Personajes del material (rol · lugar · años; sin nombres). Que ningún grupo que aparezca acá quede fuera de "
            "people_groups:")
_TEXTO_1_F46B = f46b.TEXTO_1_PEOPLE_GROUPS
_TEXTO_2_F46B = f46b.TEXTO_2_PEOPLE_GROUP
_SCHEMA_ORIG = None
_ANIO_O_DECADA = re.compile(r"\b(1[89]\d\d|20\d\d)s?\b")
# chequeo 12: palabras de origen del rol (pool en español) → cómo se diría en la prosa (inglés). Heurística declarada.
ORIGEN = {"español": r"Spanish|Spaniard|Spain", "española": r"Spanish|Spaniard|Spain",
          "españoles": r"Spanish|Spaniards|Spain", "banjima": r"Banjima", "aborigen": r"Aboriginal|Indigenous"}


def _sale_entero(nombre: str, texto: str) -> bool:
    """Chascada del handoff F48: el chequeo 5 busca solo el `nombre` entero (sin el apellido suelto)."""
    return bool(re.search(rf"\b{re.escape(nombre)}\b", texto or "", re.I))


f47._sale = _sale_entero


# ─────────────────────────── datos por foto (S2, S3, S4) ───────────────────────────
def extra_por_foto(d: dict, exps: list[dict]) -> None:
    """Agrega a cada expediente: ids del beat, FACTS (S2), PEOPLE (S3), año del ancla y respaldo 3–5 (S4)."""
    pool = d["topic"].get("evidence_pool") or {}
    datos = {x["id"]: x for x in pool.get("datos") or []}
    crono = {x["id"]: x for x in pool.get("cronologia") or []}
    pers = {x["id"]: x for x in pool.get("personajes") or []}
    esc_beats = {b["n"]: b for b in d["esc"].get("beats") or []}
    by_n = {b["n"]: b for b in d["cap_beats"]}
    v03_caps = {c["chapter_number"]: c for c in _j(f46.STEPS / f46.TID / "03_visual.json")["chapters"]}
    ultimo_prev = None                                       # regla 3: el último año dicho en los caps anteriores
    for c in range(1, d["cap"]):
        for a in f46b._anclas_cap(v03_caps, c):
            ultimo_prev = f46b._anio_del_ancla(a) or ultimo_prev
    for e in exps:
        eb = esc_beats.get(e["beat"]) or {}
        ids = [x for x in [eb.get("dato_central"), *(eb.get("datos_apoyo") or [])] if x]
        facts = []
        for i in ids:
            if i in datos and datos[i].get("texto"):
                facts.append(datos[i]["texto"])
            if i in crono and crono[i].get("evento"):
                facts.append(f"{crono[i].get('fecha') or '-'} · {crono[i]['evento']}")
        quien = [pers[i] for i in ids if i in pers]
        quien += [p for p in pers.values() if p not in quien and _sale_entero(p["nombre"], e["ancla"])]
        e["ids"], e["facts"] = ids, facts
        e["people3"] = [f"{(p.get('rol') or '').strip().rstrip('.')} · {p.get('lugar') or '-'} · "
                        f"{', '.join(p.get('fechas_presente') or []) or '-'}" for p in quien]
        e["people3_roles"] = [p.get("rol") or "" for p in quien]
        e["anio_ancla"] = f46b._anio_del_ancla(e["ancla"])
        b = by_n.get(e["beat"]) or {}
        if ultimo_prev:
            e["respaldo"] = (ultimo_prev, "3) el último del cap anterior")
        elif re.match(r"\d{4}", b.get("fecha") or ""):
            e["respaldo"] = (b["fecha"][:4], "4) la fecha del dato_central del beat")
        else:
            e["respaldo"] = (d["year_topic"], "5) topic_year")


def bloque(exps: list[dict], canon: dict, etapa: str) -> str:
    """`f46b.bloque_expediente` (S1 = idéntico) con lo que suma cada etapa."""
    n = ETAPAS.index(etapa) + 1
    L = ["", "═══════════════════════════════════════════════════", f46b.TEXTO_3_ENCABEZADO,
         "═══════════════════════════════════════════════════"]
    for e in exps:
        anio = (e.get("anio_ancla") or "-") if n >= 4 else e["anio"]
        L += [f"  [{e['foto']}] YEAR: {anio} · WHERE: {'; '.join(e['donde']) or '-'}",
              f"      PARAGRAPH: «{e['parrafo']}»",
              f"      SCENES: {' | '.join('«' + s + '»' for s in e['escenas']) or '-'}"]
        if n >= 2:
            L.append(f"      FACTS: {' | '.join('«' + q + '»' for q in e['facts']) or '-'}")
        L.append(f"      QUOTES: {' | '.join('«' + q + '»' for q in e['citas']) or '-'}")
        L.append(f"      PEOPLE (role · where · years): {'; '.join(e['people3']) or '-'}" if n >= 3 else
                 f"      PEOPLE (roles): {'; '.join(e['personas']) or '-'}")
    L += ["PEOPLE GROUPS:"]
    for g in canon.get("people_groups") or []:
        L.append(f"  - {g.get('id')}: {g.get('who') or ''} · {g.get('where_when') or ''}")
    return "\n".join(L) + "\n"


def _schema_con_year(n: int) -> dict:
    s = _SCHEMA_ORIG(n)
    s["items"]["properties"]["year"] = {"type": "STRING"}
    s["items"]["required"].append("year")
    return s


def preparar_etapa(etapa: str) -> None:
    """Parches de la etapa, solo en este proceso (las etapas corren en secuencia)."""
    from script_engine import m03_visual as m03
    n = ETAPAS.index(etapa) + 1
    f46b.bloque_expediente = lambda exps, canon: bloque(exps, canon, etapa)
    f46b.TEXTO_2_PEOPLE_GROUP = _TEXTO_2_F46B + ("\n" + TEXTO_S4_YEAR if n >= 4 else "")
    m03._seedream_slots_schema = _schema_con_year if n >= 4 else _SCHEMA_ORIG


# ─────────────────────────── año final y armado (S4+) ───────────────────────────
def anio_final(e: dict, it: dict, etapa: str) -> tuple[str, str]:
    if ETAPAS.index(etapa) + 1 < 4:
        return e["anio"], e["anio_fuente"]
    if e.get("anio_ancla"):
        return e["anio_ancla"], "1) dicho en el ancla"
    y = str(it.get("year") or "").strip()
    if re.fullmatch(r"\d{4}", y) and 1800 <= int(y) <= 2100:      # derivado: handoff F48 §Constantes (años 1800–2100)
        return y, "2) el casillero `year` del modelo"
    return e["respaldo"]


def armar_etapa(items: list[dict], exps: list[dict], d: dict, canon: dict, documented, etapa: str) -> list[dict]:
    if ETAPAS.index(etapa) + 1 < 4:
        return f47.armar_c2(items, exps, d, canon, documented)
    grupos = {g["id"]: g for g in canon.get("people_groups") or []}
    by_n = {b["n"]: b for b in d["cap_beats"]}
    res = []
    for it, e in zip(items, exps):
        anio, fuente = anio_final(e, it, etapa)
        a = f46b.armar(it, anio, grupos, False)
        setting = str(it.get("setting") or "")
        if _ANIO_O_DECADA.search(setting):                    # el setting ya trae año o década: no se agrega `, {año}`
            a["partes"]["lugar_anio"] = f46b._oracion(setting)
            a["prompt"] = " ".join(p for p in a["partes"].values() if p)
        p, notas = f46b.f8(a["prompt"], it, bool((by_n.get(it.get("beat")) or {}).get("escala")), documented)
        res.append({"foto": e["foto"], "beat": it.get("beat"), "anio": anio, "anio_fuente": fuente,
                    "people_group": it.get("people_group") or [], "partes": a["partes"], "prompt": p,
                    "f8_problemas": notas, "f8_slots_scrub": it.get("_f8_slots_scrub") or [],
                    "hard_fact_ids_fuera": it.get("hard_fact_ids") or [],
                    "slots": {k: v for k, v in it.items() if k != "narration_anchor"}})
    return res


# ─────────────────────────── canon S5 ───────────────────────────
def canon_s5(d: dict, canon_c: dict) -> tuple[dict, dict]:
    pers = (d["topic"].get("evidence_pool") or {}).get("personajes") or []
    lineas = [f"- {(p.get('rol') or '').strip().rstrip('.')} · {p.get('lugar') or '-'} · "
              f"{', '.join(p.get('fechas_presente') or []) or '-'}" for p in pers]
    f46b.TEXTO_1_PEOPLE_GROUPS = _TEXTO_1_F46B + "\n" + TEXTO_S5 + "\n" + "\n".join(lineas)
    f46b.freno = lambda que, costo=0.0: f47.freno(que)
    try:
        if f47._SECO:
            regen = {"people_groups": canon_c.get("people_groups"), "_seco": True}
        else:
            regen = f46b.canon_c(d)
    finally:
        f46b.TEXTO_1_PEOPLE_GROUPS = _TEXTO_1_F46B
    return {**canon_c, "people_groups": regen.get("people_groups") or []}, regen


# ─────────────────────────── corrida ───────────────────────────
def prompts(seco_dir: Path | None) -> None:
    global _SCHEMA_ORIG
    from cost_tracker import cost_tracker
    from script_engine import m03_visual as m03
    if seco_dir:
        f47._SECO, f47.LAB = True, seco_dir
    out = f47.LAB
    canon_c = {k: v for k, v in _j(f47.CANON_C).items() if k != "facts_de_la_ficha"}
    narr = _j(f46.STEPS / f46.TID / "01b_narration.json")
    geo_era = m03._geo_era(f46.TID, narr)                   # S1: la función de producción
    datos: dict[int, dict] = {}
    for cap in CAPS:                                         # secuencial: f46b.anios lee f46b.CAP
        d = f47.cargar(cap)
        f46b.CAP = cap
        exps = f46b.expedientes(d, canon_c, f46b.anios(d))
        extra_por_foto(d, exps)
        datos[cap] = {"d": d, "exps": exps, "topic": {**d["topic"], **geo_era}}
    f46b.CAP = 0
    # S1 = el bloque de F46b, byte a byte
    assert all(bloque(x["exps"], canon_c, "S1") == f46b.bloque_expediente(x["exps"], canon_c) for x in datos.values())
    f46b.LAB = Path(tempfile.mkdtemp(prefix="f48_"))        # f46b.slots escribe ahí su prompt_slots_pro.txt
    _SCHEMA_ORIG = m03._seedream_slots_schema
    bloque_orig = f46b.bloque_expediente
    f47._PREVIO = f47.gastado_previo()
    if not seco_dir:
        cost_tracker.start_video(f47.LAB_ID)
    f47._PRO_ORIG, m03.call_pro_json = m03.call_pro_json, f47.ruteador
    res: dict[tuple[str, int], dict] = {}
    canones = {s: canon_c for s in ETAPAS}
    regen = None
    try:
        for etapa in ETAPAS:
            if etapa == "S5":
                canones["S5"], regen = canon_s5(datos[CAPS[0]]["d"], canon_c)
                _w(out / "canon_S5.json", canones["S5"])
                _w(out / "canon_S5_regenerado.json", regen)
                print(f"  canon S5: {len(canones['S5']['people_groups'])} people_groups · US$ {f47.gastado():.4f}",
                      flush=True)
            preparar_etapa(etapa)
            cn = canones[etapa]
            with ThreadPoolExecutor(max_workers=len(CAPS)) as ex:          # las 4 llamadas de la etapa en paralelo
                futs = {ex.submit(f47.una_variante, etapa, c, datos[c]["d"],
                                  {**datos[c]["topic"], **{k: cn[k] for k in f46.CANON_KEYS if k in cn}},
                                  datos[c]["exps"], cn): (etapa, c) for c in CAPS}
                for f in as_completed(futs):
                    try:
                        res[futs[f]] = f.result()
                    except f47.Parada as e:
                        res[futs[f]] = {"var": etapa, "cap": futs[f][1], "estado": f"PARADA: {e}"}
            if any(str(r.get("estado", "")).startswith("PARADA") for r in res.values()):
                break
    finally:
        m03.call_pro_json = f47._PRO_ORIG
        m03._seedream_slots_schema = _SCHEMA_ORIG
        f46b.bloque_expediente = bloque_orig
        f46b.TEXTO_2_PEOPLE_GROUP = _TEXTO_2_F46B
        if not seco_dir:
            cost_tracker.end_video()
    var: dict[tuple[str, int], list[dict]] = {}
    for (s, c), r in res.items():
        if r.get("estado") == "ok":
            cn = canones[s]
            preparar_etapa(s)
            var[(s, c)] = armar_etapa(r["items"], datos[c]["exps"], datos[c]["d"], cn,
                                      (datos[c]["topic"] | {k: cn[k] for k in f46.CANON_KEYS if k in cn}).get(
                                          "documented_people"), s)
    preparar_etapa("S1")
    m03._seedream_slots_schema = _SCHEMA_ORIG
    f46b.bloque_expediente = bloque_orig
    e47b = _j(F47 / "PROMPTS_F47b.json")
    for c in CAPS:
        var[("S0", c)] = e47b[f"E_ch{c:02d}"]
    _w(out / "PROMPTS_F48.json", {f"{s}_ch{c:02d}": x for (s, c), x in var.items() if s != "S0"})
    escribir(out, datos, canones, var, res, geo_era)
    print(f"  F48: US$ {f47.gastado_previo():.4f} en cost_history ({f47.LAB_ID})", flush=True)


# ─────────────────────────── salidas ───────────────────────────
COLS = ("S0",) + ETAPAS


def _con_origen(t: dict) -> str:
    return f"{t['orig_si']}/{t['orig_n']} con origen"


def _origen(roles: list[str], prosa: str) -> str:
    pats = {w: pat for r in roles for w, pat in ORIGEN.items() if re.search(rf"\b{w}\b", r, re.I)}
    if not pats:
        return "rol sin origen"
    return ", ".join(f"{w}: {'sí' if re.search(p, prosa) else 'no'}" for w, p in pats.items())


def escribir(out: Path, datos: dict, canones: dict, var: dict, res: dict, geo_era: dict) -> None:
    from script_engine import m03_imagenes_v3 as v3img
    sn = lambda b: "sí" if b else "no"  # noqa: E731
    L = ["# F48 — Entrada del prompt de foto arreglada por etapas (S0 = E de F47b | S1 … S5), Opus 5.5 effort high", "",
         f"GEO/ERA de S1 en adelante (producción, `m03._geo_era`): {geo_era}", "",
         "## Estado de cada llamada", "", "| etapa | cap | estado | intentos | md5 system / user / esquema (1.er intento) |",
         "|---|---|---|---|---|"]
    for (s, c), r in sorted(res.items(), key=lambda kv: (kv[0][0], kv[0][1])):
        p0 = (r.get("pedidos") or [{}])[0]
        L.append(f"| {s} | {c} | {str(r.get('estado', ''))[:300]} | {len(r.get('pedidos') or [])} | "
                 f"{p0.get('md5_system', '—')[:8]} / {p0.get('md5_user', '—')[:8]} / {p0.get('md5_schema', '—')[:8]} |")
    # tabla de chequeos
    keys = ("lugar", "sin", "nom", "txt", "f8", "pal", "a9", "neg", "choca", "orig_si", "orig_n", "n")
    gran = {s: dict.fromkeys(keys, 0) for s in COLS}
    T = ["", "## Tabla de los chequeos por foto (S0 \\| S1 \\| S2 \\| S3 \\| S4 \\| S5)", "",
         "1 año (fuente) · 2 año en `spans` · 3 lugar del DÓNDE en la prosa · 4 gente sin grupo · 5 nombre entero del "
         "ancla en la prosa · 6 `text_in_image` · 7 F8 · 8 palabras · 9 años/décadas del setting ≠ año de la foto · "
         "10 negaciones en el setting · 11 año final (fuente) y si choca con el año/década del setting · 12 persona del "
         "pool (regla S3) y si la prosa dice su origen · 13 `people_group` (cap 7 fotos 7 y 8 abajo)", ""]
    for cap in CAPS:
        d, exps = datos[cap]["d"], datos[cap]["exps"]
        lang = v3img.place_language(d["topic"])
        tot = {s: dict.fromkeys(keys, 0) for s in COLS}
        T += [f"### Cap {cap}" + (" (Veo: suplementarias)" if d["veo"] else ""), "",
              "| foto | 1 año (fuente) S0–S3 | 2 canon | 3 lugar | 4 sin grupo | 5 nombre ancla → prosa | 6 texto | 7 F8 | "
              "8 palabras | 9 año setting ≠ | 10 negaciones | 11 año final (fuente) · choca | 12 persona del pool · origen | "
              "grupos |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
        for k, e in enumerate(exps):
            ch = {}
            for s in COLS:
                xs = var.get((s, cap))
                if not xs:
                    continue
                x = xs[k]
                ee = {**e, "anio": x.get("anio") or e["anio"], "anio_fuente": x.get("anio_fuente") or e["anio_fuente"]}
                q = f47.chequeos(x, ee, canones.get(s, canones["S1"]), d["topic"], lang)
                st = str((x.get("slots") or {}).get("setting") or "")
                q["a9"], q["neg"] = f47b.anios_setting(st, ee["anio"]), f47b.negaciones(st)
                q["final"] = f"{ee['anio']} ({ee['anio_fuente'].split(')')[0]})"
                q["choca"] = q["a9"]
                q["orig"] = _origen(e["people3_roles"], x["prompt"]) if e["people3_roles"] else "—"
                q["grupos"] = ", ".join(x.get("people_group") or []) or "[]"
                ch[s] = q
                for t in (tot[s], gran[s]):
                    t["n"] += 1
                    t["lugar"] += bool(q["lugar"])
                    t["sin"] += q["gente_sin_grupo"]
                    t["nom"] += bool(q["nombres_prosa"])
                    t["txt"] += q["texto"] != "no"
                    t["f8"] += bool(q["f8"])
                    t["pal"] += q["palabras"]
                    t["a9"] += bool(q["a9"])
                    t["neg"] += bool(q["neg"])
                    t["choca"] += bool(q["choca"])
                    if e["people3_roles"] and q["orig"] != "rol sin origen":
                        t["orig_n"] += 1
                        t["orig_si"] += "no" not in q["orig"].replace("rol sin origen", "")

            def col(f):
                return " \\| ".join(f(ch[s]).replace("|", "/") if s in ch else "—" for s in COLS)
            q0 = ch.get("S1") or next(iter(ch.values()))
            T.append(f"| {e['foto']} | {e['anio']} ({e['anio_fuente']}) | {q0['en_canon']} | "
                     f"{col(lambda q: ', '.join(q['lugar']) or 'no')} | {col(lambda q: sn(q['gente_sin_grupo']))} | "
                     f"{', '.join(q0['nombres_ancla']) or '—'} → {col(lambda q: ', '.join(q['nombres_prosa']) or 'no')} | "
                     f"{col(lambda q: q['texto'])} | {col(lambda q: '; '.join(q['f8']) or '—')} | "
                     f"{col(lambda q: str(q['palabras']))} | {col(lambda q: ', '.join(q['a9']) or '—')} | "
                     f"{col(lambda q: '; '.join(q['neg']) or '—')} | "
                     f"{col(lambda q: q['final'] + (' · choca ' + ', '.join(q['choca']) if q['choca'] else ''))} | "
                     f"{'; '.join(e['people3']) or '—'} · {col(lambda q: q['orig'])} | {col(lambda q: q['grupos'])} |")

        def tc(f):
            return " \\| ".join(f(tot[s]) if tot[s]["n"] else "—" for s in COLS)
        T.append(f"| **total cap {cap}** | — | — | **{tc(lambda t: str(t['lugar']))}** | **{tc(lambda t: str(t['sin']))}** | "
                 f"**{tc(lambda t: str(t['nom']))}** | **{tc(lambda t: str(t['txt']))}** | **{tc(lambda t: str(t['f8']))}** | "
                 f"**{tc(lambda t: str(round(t['pal'] / t['n'])))}** | **{tc(lambda t: str(t['a9']))}** | "
                 f"**{tc(lambda t: str(t['neg']))}** | **{tc(lambda t: str(t['choca']) + ' chocan')}** | "
                 f"**{tc(_con_origen)}** | — |")
        T.append("")
    T += ["### Totales por etapa (los 4 caps, 60 fotos)", "",
          "| etapa | fotos | 3 lugar | 4 sin grupo | 5 nombre en la prosa | 6 texto | 7 F8 | 8 palabras prom. | "
          "9 año setting ≠ | 10 negaciones | 11 choca | 12 origen dicho / fotos con persona de origen conocido |",
          "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for s in COLS:
        t = gran[s]
        if t["n"]:
            T.append(f"| {s} | {t['n']} | {t['lugar']} | {t['sin']} | {t['nom']} | {t['txt']} | {t['f8']} | "
                     f"{round(t['pal'] / t['n'])} | {t['a9']} | {t['neg']} | {t['choca']} | {t['orig_si']}/{t['orig_n']} |")
    L += T
    # chequeo 13
    L += ["", "## Chequeo 13: `people_group` de las fotos 7 y 8 del cap 7, y los `people_groups` del canon", "",
          "| etapa | cap 7 foto 7 | cap 7 foto 8 |", "|---|---|---|"]
    for s in COLS:
        xs = var.get((s, 7))
        if xs:
            L.append(f"| {s} | {', '.join(xs[6]['people_group']) or '[]'} | {', '.join(xs[7]['people_group']) or '[]'} |")
    for nom, cn in (("S0–S4 (canon C de F46b)", canones["S1"]), ("S5 (regenerado)", canones["S5"])):
        L += ["", f"**{nom}** — {len(cn.get('people_groups') or [])} grupos:", ""]
        L += [f"- `{g.get('id')}` — who: {g.get('who')} · where_when: {g.get('where_when')} · appearance: "
              f"{g.get('appearance') or '(vacío)'} · clothing: {g.get('clothing') or '(vacío)'}"
              for g in cn.get("people_groups") or []]
    # diffs del cap 6
    L += ["", "## Diff del pedido del cap 6, etapa contra la anterior (system + user del 1.er intento)", ""]
    prev = F47 / "pedidos" / "pedido_E_ch06.txt"
    for s in ETAPAS:
        cur = out / "pedidos" / f"pedido_{s}_ch06.txt"
        if not cur.exists():
            continue
        a, b = prev.read_text(encoding="utf-8").splitlines(), cur.read_text(encoding="utf-8").splitlines()
        dif = list(difflib.unified_diff(a, b, fromfile=prev.name, tofile=cur.name, lineterm="", n=0))
        L += [f"### {s} contra {'S0 (E de F47b)' if s == 'S1' else ETAPAS[ETAPAS.index(s) - 1]} "
              f"({sum(1 for x in dif if x.startswith('+') and not x.startswith('+++'))} líneas +, "
              f"{sum(1 for x in dif if x.startswith('-') and not x.startswith('---'))} líneas −)", "", "```diff",
              *dif, "```", ""]
        prev = cur
    # prompts de S5
    L += ["## Los prompts enteros de S5", ""]
    for cap in CAPS:
        xs = var.get(("S5", cap))
        L += [f"### Cap {cap}", ""]
        if not xs:
            L += ["— (la llamada no devolvió casilleros)", ""]
            continue
        for e, x in zip(datos[cap]["exps"], xs):
            L += [f"**Cap {cap} · foto {e['foto']}** · año {x['anio']} ({x['anio_fuente']}) · grupos "
                  f"{', '.join(x['people_group']) or '[]'} · {len(x['prompt'].split())} palabras", "",
                  f"Ancla: «{e['ancla']}»", "", "> " + x["prompt"], ""]
    # costos
    ent = f47b._historia("f48-lab")
    L += ["## Costos, tokens y tiempo por etapa y cap (`cost_history` f48-lab; S0 = E de f47b-lab)", "",
          "| etapa | cap | estado | intentos | segundos | tokens in / out | US$ |", "|---|---|---|---|---|---|---:|"]
    sub = defaultdict(float)
    e0 = f47b._historia("f47b-lab")
    for s in COLS:
        for c in CAPS:
            src = f47.LAB if s != "S0" else F47
            vv = "E" if s == "S0" else s
            pth = src / f"slots_{vv}_ch{c:02d}.json"
            r = _j(pth) if pth.exists() else {}
            es = [x for x in (e0 if s == "S0" else ent) if re.match(rf"f47 {vv} ch{c:02d} slots", str(x.get("description")))]
            usd = sum(float(x.get("total_cost") or 0) for x in es)
            sub[s] += usd
            L.append(f"| {s} | {c} | {str(r.get('estado') or '—')[:100]} | {len(r.get('pedidos') or [])} | "
                     f"{round(sum(x.get('segundos') or 0 for x in r.get('crudos') or []), 1)} | "
                     f"{sum(int(x.get('tokens_in') or 0) for x in es)} / {sum(int(x.get('tokens_out') or 0) for x in es)} | "
                     f"{usd:.4f} |")
    otros = [x for x in ent if not str(x.get("description") or "").startswith("f47 ")]
    L += ["", "| etapa | US$ (4 caps) |", "|---|---:|"] + [f"| {s} | {sub[s]:.4f} |" for s in COLS]
    L += ["", "Otras llamadas de F48 (canon S5): " + ("; ".join(f"{x.get('service')} · {x.get('description')} · US$ "
                                                             f"{float(x.get('total_cost') or 0):.4f}" for x in otros) or "—"),
          "", f"**Total F48 (`f48-lab`)**: US$ {sum(float(x.get('total_cost') or 0) for x in ent):.4f} "
              f"(tope {f47.TOPE_USD:.2f})"]
    (out / "PROMPTS_F48.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("  PROMPTS_F48.md listo", flush=True)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    que = sys.argv[1] if len(sys.argv) > 1 else ""
    if que not in ("prompts", "seco"):
        print(__doc__)
        return 2
    seco = Path(sys.argv[2]) if que == "seco" else None
    if seco:
        seco.mkdir(parents=True, exist_ok=True)
    try:
        prompts(seco)
    except f47.Parada as e:
        print(f"⛔ PARADA: {e}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
