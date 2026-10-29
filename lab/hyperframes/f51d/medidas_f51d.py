# -*- coding: utf-8 -*-
"""F51d-A etapa 2 — las 9 medidas del handoff (`HANDOFF_F51d_A_m03_en_texto.md`) sobre un 03_visual.json de Wittenoom.
Solo lee: el 03_visual.json, el topic vivo (`topics_db.get_topic_by_id`), la narración (01b_narration.json), los
costos (01_v3_costos.json y data/cost_history.json). Sin modelos, sin fal. Escribe solo el .md de --salida.

Numeración de fotos «cap/i»: `f50g/rearmar.fotos(cap)`, i desde 1 (cap Veo: foto 1 = `image_f8` + `image_prompt`, la
del primer o último cuadro del clip; después los `supplemental_image_prompts`).

1. fotos con algún `people_group` (del ítem y del `raw_llm_prompt`) que no existe en `topic["people_groups"][].id`.
2. fotos cuyos grupos (los que existen en el canon, al menos uno) tienen todos `appearance` vacío: foto · grupo · subject.
3. fotos cuyo `prompt` final contiene como subcadena un `condition` de `people_groups[].condition_by_period[]`
   (exacta; aparte, la misma búsqueda sin mayúsculas y sin el punto final, para ver si hay casi-copias).
4. prompts enteros de 2/9, 4/11, 4/12 y 5/8.
5. 6/3, 7/11 y 3/16 por posición, y por texto del ancla (juez/veredicto/Tribunal Supremo, Tribunal Federal, «Al año
   siguiente, los Écija»): prompt entero, «Court», año y fuente del año.
6. caps 1 y 7: ancla Veo y las 2 anclas de apoyo vecinas a la zona Veo (start: las 2 primeras; end: las 2 últimas),
   con su posición en la narración del cap y el chequeo de mitad de palabra; más el `video_prompt` entero.
7. conteo de `anio_fuente`.
8. palabras por prompt: mediana y máximo.
9. gasto por paso: 01_v3_costos.json y las entradas de cost_history del topic desde --desde.

Uso:
  PYTHONIOENCODING=utf-8 python lab/hyperframes/f51d/medidas_f51d.py [--visual RUTA] [--salida MD] [--desde ISO]
"""
import argparse
import ast
import hashlib
import json
import re
import statistics
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "lab" / "hyperframes" / "f50g"))
F51D = Path(__file__).resolve().parent
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
STEPS = ROOT / "data" / "scripts" / "_steps" / TID
VISUAL = STEPS / "03_visual.json"
SALIDA = F51D / "MEDIDAS_F51d.md"
DESDE = "2026-10-29T12:37:02"
MANCHAS = [(2, 9), (4, 11), (4, 12), (5, 8)]
F51C = [(6, 3), (7, 11), (3, 16)]
# frases de la narración (01b_narration.json) de las 3 fotos de F51c; ver REARMADO_F51c.md
ANCLAS_F51C = [
    ("6/3 · juez / veredicto / Tribunal Supremo", re.compile(r"veredicto|\bjuez\b|Tribunal Supremo|Corte Suprema|"
                                                              r"Supreme Court", re.I)),
    ("7/11 · Tribunal Federal", re.compile(r"Tribunal Federal|tribunal federal|Federal Court", re.I)),
    ("3/16 · «Al año siguiente, los Écija»", re.compile(r"Al año siguiente,? los Écija", re.I)),
]


def _j(p: Path):
    raw = p.read_bytes()
    try:
        return json.loads(raw.decode("utf-8"))
    except UnicodeDecodeError:
        return json.loads(raw.decode("cp1252"))


def _lista(x) -> list[str]:
    if x is None or x == "":
        return []
    if isinstance(x, str):
        try:
            x = ast.literal_eval(x)
        except (ValueError, SyntaxError):
            return [x]
    if isinstance(x, str):
        return [x]
    return [str(g) for g in x if g]


def _slots(it: dict) -> dict:
    try:
        return json.loads(it.get("raw_llm_prompt") or "{}") or {}
    except json.JSONDecodeError:
        return {}


def grupos_de(it: dict) -> list[str]:
    """Unión ordenada de `people_group` del ítem y del casillero (`raw_llm_prompt`)."""
    out = []
    for g in _lista(it.get("people_group")) + _lista(_slots(it).get("people_group")):
        if g not in out:
            out.append(g)
    return out


def bloque(s: str) -> list[str]:
    return ["```", s or "(vacío)", "```"]


def palabras(p: str) -> int:
    return len((p or "").split())


def ubicar(ancla: str, narr: str) -> dict:
    """Posición del ancla en la narración del cap y si empieza / termina a mitad de palabra."""
    a = (ancla or "").strip()
    if not a:
        return {"pos": None, "nota": "ancla vacía"}
    i = narr.find(a)
    texto, modo = narr, "exacta"
    if i < 0:  # espacios normalizados
        texto = re.sub(r"\s+", " ", narr)
        a = re.sub(r"\s+", " ", a)
        i, modo = texto.find(a), "espacios normalizados"
    if i < 0:
        return {"pos": None, "nota": "no está en la narración del cap"}
    j = i + len(a)
    antes = texto[i - 1] if i > 0 else ""
    despues = texto[j] if j < len(texto) else ""
    mi = bool(antes) and antes.isalnum() and a[0].isalnum()
    mf = bool(despues) and despues.isalnum() and a[-1].isalnum()
    # aparte (informativo): ¿empieza / termina a mitad de oración? (borde de oración = [.!?…] más comillas/cierres)
    previo = texto[:i].rstrip().rstrip("»\"')”")
    oi = bool(previo) and previo[-1] not in ".!?…"
    of = a.rstrip("»\"')”")[-1:] not in tuple(".!?…")
    return {"pos": (i, j), "modo": modo, "antes": antes, "despues": despues, "mitad_inicio": mi, "mitad_fin": mf,
            "oracion_inicio": oi, "oracion_fin": of,
            "contexto": texto[max(0, i - 25):i] + "⟦" + a[:30] + "…" + a[-30:] + "⟧" + texto[j:j + 25]}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--visual", type=Path, default=VISUAL)
    ap.add_argument("--salida", type=Path, default=SALIDA)
    ap.add_argument("--desde", default=DESDE)
    args = ap.parse_args()
    import rearmar as rg
    from script_engine.topics_db import get_topic_by_id

    vis_path = args.visual.resolve()
    raw_vis = vis_path.read_bytes()
    md5 = hashlib.md5(raw_vis).hexdigest()
    v = _j(vis_path)                                                     # solo lectura
    topic = get_topic_by_id(TID)                                         # solo lectura
    grupos = {g["id"]: g for g in topic.get("people_groups") or [] if isinstance(g, dict) and g.get("id")}
    narr = {c["chapter_number"]: c.get("narration") or "" for c in _j(STEPS / "01b_narration.json")["chapters"]}

    fotos = []   # (cap, i, rol, it, prompt)
    caps = {}
    for cap in v["chapters"]:
        n = cap["chapter_number"]
        caps[n] = cap
        for i, (it, rol) in enumerate(rg.fotos(cap), start=1):
            fotos.append((n, i, rol, it, it.get("prompt") or ""))
    por_k = {(n, i): (rol, it, p) for n, i, rol, it, p in fotos}
    ancla = {(n, i): (it.get("narration_anchor") if rol != "veo0" else caps[n].get("narration_anchor")) or ""
             for n, i, rol, it, p in fotos}

    L = ["# MEDIDAS_F51d — Wittenoom en texto tras m03 (F51d-A etapa 2)", "",
         f"Salida de `python lab/hyperframes/f51d/medidas_f51d.py --visual {args.visual}`.", "",
         f"- Archivo medido: `{vis_path}`",
         f"- md5: `{md5}`",
         f"- topic_id del archivo: `{v.get('topic_id')}` · fotos: {len(fotos)} · "
         + " · ".join(f"cap {n}: {sum(1 for f in fotos if f[0] == n)}" for n in sorted(caps)),
         f"- Canon: `people_groups` del topic vivo ({len(grupos)} grupos): {', '.join(grupos)}",
         "- Numeración «cap/i»: `f50g/rearmar.fotos(cap)`, i desde 1 (en los caps Veo la foto 1 es la del clip).",
         "- Grupos de una foto: unión de `people_group` del ítem y del casillero (`raw_llm_prompt`).", ""]
    tot = {}

    # 1
    m1 = []
    for n, i, rol, it, p in fotos:
        falt = [g for g in grupos_de(it) if g not in grupos]
        if falt:
            m1.append((n, i, rol, falt))
    tot["1_grupo_inexistente"] = len(m1)
    L += ["## 1. Fotos con un `people_group` que no existe en el canon vivo", "",
          f"**Total: {len(m1)}** (tiene que dar 0 tras m03)", ""]
    if m1:
        L += ["| foto | rol | grupo(s) inexistente(s) |", "|---|---|---|"]
        L += [f"| {n}/{i} | {rol} | {', '.join(f)} |" for n, i, rol, f in m1]
        L += ["", "Ids inexistentes: " + ", ".join(f"{g} ({c})" for g, c in
                                                  Counter(g for *_, f in m1 for g in f).most_common())]
    else:
        L.append("- ninguna")

    # 2
    vacios = [g for g, x in grupos.items() if not str(x.get("appearance") or "").strip()]
    m2 = []
    for n, i, rol, it, p in fotos:
        exist = [g for g in grupos_de(it) if g in grupos]
        if exist and all(g in vacios for g in exist):
            m2.append((n, i, rol, exist, str(_slots(it).get("subject") or it.get("subject") or "?")))
    tot["2_grupos_sin_appearance"] = len(m2)
    L += ["", "## 2. Fotos cuyos grupos tienen todos `appearance` vacío", "",
          f"Grupos del canon con `appearance` vacío ({len(vacios)}): {', '.join(vacios) or '—'}", "",
          f"**Total: {len(m2)}**", ""]
    if m2:
        L += ["| foto | rol | grupo(s) | subject (casillero) |", "|---|---|---|---|"]
        L += [f"| {n}/{i} | {rol} | {', '.join(gs)} | {s.replace('|', '/')} |" for n, i, rol, gs, s in m2]
    else:
        L.append("- ninguna")

    # 3
    conds = [(g, c.get("years"), str(c.get("condition") or "").strip()) for g, x in grupos.items()
             for c in x.get("condition_by_period") or [] if isinstance(c, dict) and str(c.get("condition") or "").strip()]
    m3, m3b = [], []
    for n, i, rol, it, p in fotos:
        for g, yrs, c in conds:
            if c in p:
                m3.append((n, i, g, yrs, c))
            elif c.rstrip(".").lower() in p.lower():
                m3b.append((n, i, g, yrs, c))
    tot["3_condition_en_prompt"] = len({(a, b) for a, b, *_ in m3})
    L += ["", "## 3. Fotos cuyo prompt contiene un texto de `condition_by_period`", "",
          f"Textos de condición buscados: {len(conds)}. **Fotos con la subcadena exacta: {tot['3_condition_en_prompt']}** "
          f"(tiene que dar 0). Aparte, sin mayúsculas y sin el punto final: "
          f"{len({(a, b) for a, b, *_ in m3b})} fotos más.", ""]
    if m3 or m3b:
        L += ["| foto | búsqueda | grupo | years | condition |", "|---|---|---|---|---|"]
        L += [f"| {n}/{i} | exacta | {g} | {y} | {c} |" for n, i, g, y, c in m3]
        L += [f"| {n}/{i} | sin mayúsc./punto | {g} | {y} | {c} |" for n, i, g, y, c in m3b]
    else:
        L.append("- ninguna")

    # 4
    L += ["", "## 4. Prompts enteros de 2/9, 4/11, 4/12 y 5/8", ""]
    for k in MANCHAS:
        if k not in por_k:
            L += [f"### {k[0]}/{k[1]}", "", "- no existe en este archivo", ""]
            continue
        rol, it, p = por_k[k]
        L += [f"### {k[0]}/{k[1]} ({rol})", "", f"- Ancla: «{ancla[k]}»",
              f"- Año: {it.get('anio')} — {it.get('anio_fuente')} · palabras: {palabras(p)}", ""] + bloque(p) + [""]

    # 5
    def ficha5(k, titulo):
        rol, it, p = por_k[k]
        return [f"### {titulo}: {k[0]}/{k[1]} ({rol})", "", f"- Ancla: «{ancla[k]}»",
                f"- «Court» en el prompt: {'sí' if 'Court' in p else 'no'} · año: **{it.get('anio')}** — "
                f"{it.get('anio_fuente')} · casillero `year`: {_slots(it).get('year')!r}", ""] + bloque(p) + [""]
    L += ["## 5. 6/3, 7/11 y 3/16", "", "m03 re-planea las anclas: van por posición y, aparte, por el texto del ancla.",
          "", "### 5a. Por posición", ""]
    for k in F51C:
        L += ficha5(k, "posición") if k in por_k else [f"- {k[0]}/{k[1]}: no existe en este archivo", ""]
    L += ["### 5b. Por texto del ancla", ""]
    tot["5_por_ancla"] = {}
    for nombre, rx in ANCLAS_F51C:
        hits = [k for k in por_k if rx.search(ancla[k])]
        tot["5_por_ancla"][nombre.split(" ·")[0]] = [f"{a}/{b}" for a, b in hits]
        L += [f"#### {nombre} — {len(hits)} foto(s): {', '.join(f'{a}/{b}' for a, b in hits) or 'ninguna'}", ""]
        for k in hits:
            L += ficha5(k, "ancla")

    # 6
    L += ["## 6. Caps 1 y 7: ancla Veo, anclas vecinas y `video_prompt`", "",
          "Mitad de palabra = el carácter de la narración pegado al ancla es alfanumérico y el borde del ancla también. "
          "Se busca en `narration` del cap de 01b_narration.json.", ""]
    tot["6_mitad_de_palabra"] = 0
    for n in (1, 7):
        cap = caps.get(n)
        if not cap or cap.get("image_prompts") is not None:
            L += [f"### cap {n}: no es cap Veo en este archivo", ""]
            continue
        pos = cap.get("veo_position")
        supp = [k for k in sorted(por_k) if k[0] == n and por_k[k][0] == "supp"]
        vec = supp[:2] if pos == "start" else supp[-2:]
        L += [f"### cap {n} (veo_position: {pos})", "",
              "| foto | rol | ancla | posición | antes / después | mitad de palabra | mitad de oración (informativo) |",
              "|---|---|---|---|---|---|---|"]
        for k, nombre in [((n, 1), "Veo")] + [(x, "apoyo vecina") for x in vec]:
            u = ubicar(ancla[k], narr.get(n, ""))
            if u["pos"] is None:
                L.append(f"| {k[0]}/{k[1]} | {nombre} | «{ancla[k]}» | {u['nota']} | — | ? | ? |")
                continue
            mit = [x for x, b in (("inicio", u["mitad_inicio"]), ("fin", u["mitad_fin"])) if b]
            ora = [x for x, b in (("inicio", u["oracion_inicio"]), ("fin", u["oracion_fin"])) if b]
            tot["6_mitad_de_palabra"] += len(mit)
            tot["6_mitad_de_oracion"] = tot.get("6_mitad_de_oracion", 0) + len(ora)
            L.append(f"| {k[0]}/{k[1]} | {nombre} | «{ancla[k]}» | {u['pos'][0]}–{u['pos'][1]} ({u['modo']}) | "
                     f"{u['antes']!r} / {u['despues']!r} | {'**sí: ' + ', '.join(mit) + '**' if mit else 'no'} | "
                     f"{'sí: ' + ', '.join(ora) if ora else 'no'} |")
        L += ["", f"`video_prompt` del cap {n}, entero y tal cual:", ""] + bloque(cap.get("video_prompt") or "") + [""]

    # 7
    c7 = Counter(str(it.get("anio_fuente")) for _, _, _, it, _ in fotos)
    tot["7_anio_fuente"] = dict(c7.most_common())
    L += ["## 7. Fuentes del año (`anio_fuente`)", "", "| anio_fuente | fotos |", "|---|---:|"]
    L += [f"| {k} | {x} |" for k, x in c7.most_common()] + [f"| total | {sum(c7.values())} |", ""]

    # 8
    pw = [(palabras(p), f"{n}/{i}") for n, i, _, _, p in fotos]
    med, mx = statistics.median(w for w, _ in pw), max(pw)
    tot["8_palabras"] = {"mediana": med, "max": mx[0], "foto_max": mx[1]}
    L += ["## 8. Palabras por prompt", "", f"- Mediana: **{med}** · máximo: **{mx[0]}** ({mx[1]}) · mínimo: "
          f"{min(pw)[0]} ({min(pw)[1]}) · fotos: {len(pw)}", "",
          "| cap | fotos | mediana | máximo |", "|---|---:|---:|---:|"]
    for n in sorted(caps):
        ws = [palabras(p) for c, _, _, _, p in fotos if c == n]
        L.append(f"| {n} | {len(ws)} | {statistics.median(ws)} | {max(ws)} |")

    # 9
    L += ["", "## 9. Gasto por paso", "", "### 01_v3_costos.json (`_corridas`)", "",
          "| # | paso | US$ | segundos |", "|---:|---|---:|---:|"]
    corr = (_j(STEPS / "01_v3_costos.json") or {}).get("_corridas") or []
    L += [f"| {j} | {x.get('paso')} | {x.get('usd')} | {x.get('segundos')} |" for j, x in enumerate(corr, start=1)]
    hist = _j(ROOT / "data" / "cost_history.json")
    regs = [r for r in (hist if isinstance(hist, list) else []) if isinstance(r, dict) and r.get("video_id") == TID]
    entradas, por_reg = [], []
    for r in regs:
        es = [e for e in r.get("entries") or [] if str(e.get("timestamp") or "") >= args.desde]
        if es:
            por_reg.append((r.get("created_at"), len(es), sum(float(e.get("total_cost") or 0) for e in es)))
            entradas += es
    agg = defaultdict(lambda: [0, 0.0, 0, 0, 0])
    for e in entradas:
        a = agg[(e.get("stage"), e.get("service"), e.get("description"))]
        a[0] += 1
        a[1] += float(e.get("total_cost") or 0)
        a[2] += int(e.get("tokens_in") or 0)
        a[3] += int(e.get("tokens_out") or 0)
        a[4] += int(e.get("tokens_thinking") or 0)
    total9 = round(sum(a[1] for a in agg.values()), 6)
    tot["9_cost_history_desde"] = {"desde": args.desde, "entradas": len(entradas), "usd": total9}
    L += ["", f"### cost_history.json: entradas del topic con `timestamp` ≥ {args.desde}", "",
          f"**Total: US$ {total9}** en {len(entradas)} entradas de {len(por_reg)} registro(s).", ""]
    if por_reg:
        L += ["| registro (created_at) | entradas | US$ |", "|---|---:|---:|"]
        L += [f"| {c} | {k} | {round(u, 6)} |" for c, k, u in por_reg]
        L += ["", "| stage | proveedor / modelo | descripción | llamadas | US$ | tokens in | out | thinking |",
              "|---|---|---|---:|---:|---:|---:|---:|"]
        L += [f"| {s} | {sv} | {d} | {a[0]} | {round(a[1], 6)} | {a[2]} | {a[3]} | {a[4]} |"
              for (s, sv, d), a in sorted(agg.items(), key=lambda kv: -kv[1][1])]
    L.append("")

    args.salida.parent.mkdir(parents=True, exist_ok=True)
    args.salida.write_text("\n".join(L), encoding="utf-8")
    print(json.dumps({"salida": str(args.salida), "md5_visual": md5, "fotos": len(fotos), **tot},
                     ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
