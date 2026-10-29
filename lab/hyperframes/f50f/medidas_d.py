# -*- coding: utf-8 -*-
"""F50f D — las 5 medidas del handoff sobre el papel nuevo (`f50f/PAPEL_FOTOS_WITTENOOM.json`, de `f50/papel.py
--salida lab/hyperframes/f50f`) contra el de F50b (`f50b/PAPEL_FOTOS_WITTENOOM.json`). Solo lee; sin API.
1. fotos de 1967+ cuyo prompt trae ropa, vehículos o tecnología de los 40–60. MEDIDA DE LAB (no regla): una lista de
   marcas de época (décadas 1940s–1960s y objetos o prendas típicos de esos años) buscada como palabra entera; sale
   con cada acierto y su frase para que lo revise el analista (puede haber falsos: un documento mecanografiado en 1985
   existe). «forties/fifties/sixties» quedan fuera: en los prompts son edades («in their sixties»), no épocas.
2. fotos con nombre propio de persona en la prosa: las formas de `ficha.personas` (nombre y variantes, sin paréntesis;
   `m03_expediente._formas`) y los `name` de `documented_people` del canon, como palabra entera.
3. las 8 fotos testigo de F50c, buscadas por el TEXTO de su ancla (D re-planea las anclas: la posición ya no es la
   misma frase): PEOPLE del expediente junto al sujeto del casillero; y todas las fotos nuevas cuya ancla nombra a una
   persona, con su sujeto.
4. las líneas «fotos sin period» del log de m03.
5. el gasto por paso (01_v3_costos y el último registro de cost_history del tema).
Escribe MEDIDAS_D.md. Uso: python lab/hyperframes/f50f/medidas_d.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "lab" / "hyperframes" / "f50c"))
F50F = Path(__file__).resolve().parent
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
EPOCA_40_60 = re.compile(
    r"\b(19[456]0s|mid-century|mid-20th-century|post-?war|valve radios?|"
    r"rotary(?:-dial)? (?:tele)?phones?|fedoras?|trilby|trilbies|braces|suspenders|Brylcreem|Bedford|FJ Holden|"
    r"Holden FJ|EH Holden|Land Rover Series|Ford Prefect|Austin|Morris Minor|DC-3|propeller (?:plane|aircraft)|"
    r"typewriters?|slouch hats?|khaki shorts|flannel shirts?)\b", re.I)


def _j(p: Path):
    raw = p.read_bytes()
    try:
        return json.loads(raw.decode("utf-8"))
    except UnicodeDecodeError:
        return json.loads(raw.decode("cp1252"))


def epoca(papel: dict) -> list[dict]:
    out = []
    for f in papel["fotos"]:
        if f.get("anio") and int(f["anio"]) >= 1967:
            frases = [x for x in re.split(r"(?<=[.!?])\s+", f.get("prompt") or "") if EPOCA_40_60.search(x)]
            if frases:
                out.append({"cap": f["cap"], "foto": f["foto"], "anio": f["anio"], "frases": frases,
                            "marcas": sorted({m.group(0) for x in frases for m in EPOCA_40_60.finditer(x)})})
    return out


def main() -> int:
    import expedientes_f50c as ex
    from script_engine import m03_expediente as mexp
    nuevo = _j(F50F / "PAPEL_FOTOS_WITTENOOM.json")
    viejo = _j(ROOT / "lab" / "hyperframes" / "f50b" / "PAPEL_FOTOS_WITTENOOM.json")
    steps = ROOT / "data" / "scripts" / "_steps" / TID
    v = _j(steps / "03_visual.json")
    L = ["# MEDIDAS_D — Wittenoom en texto con el canon de Opus (F50f D)", "",
         "Salida de `python lab/hyperframes/f50f/medidas_d.py` sobre `f50f/PAPEL_FOTOS_WITTENOOM.json` (nuevo) y "
         "`f50b/PAPEL_FOTOS_WITTENOOM.json` (antes).", ""]

    # diff de papel
    pv = {(f["cap"], f["foto"]): f for f in viejo["fotos"]}
    pn = {(f["cap"], f["foto"]): f for f in nuevo["fotos"]}
    iguales = sum(1 for k in pn if k in pv and pv[k]["prompt"] == pn[k]["prompt"])
    L += ["## Papel: F50b → F50f", "", "| cap | fotos F50b | fotos F50f |", "|---|---:|---:|"]
    for c in range(1, 8):
        L.append(f"| {c} | {sum(1 for k in pv if k[0] == c)} | {sum(1 for k in pn if k[0] == c)} |")
    L += [f"| total | {len(pv)} | {len(pn)} |", "",
          f"Prompts idénticos (misma foto): {iguales} de {len(pn)}. Anclas iguales: "
          f"{sum(1 for k in pn if k in pv and pv[k]['ancla'] == pn[k]['ancla'])} de {len(pn)}.", ""]

    # 1
    ev, en = epoca(viejo), epoca(nuevo)
    n67v = sum(1 for f in viejo["fotos"] if f.get("anio") and int(f["anio"]) >= 1967)
    n67n = sum(1 for f in nuevo["fotos"] if f.get("anio") and int(f["anio"]) >= 1967)
    L += ["## 1. Fotos de 1967+ con marcas de época de los 40–60", "",
          "Medida de lab (no del handoff): una lista de marcas de época armada por CC (décadas 1940s–1960s en cifras y "
          "objetos o prendas típicos de esos años), como palabra entera. «forties/fifties/sixties» quedan fuera: en los "
          "prompts son edades («in their sixties»), no épocas. Se pega cada frase para revisarla.", "",
          f"- F50b: {len(ev)} de {n67v} fotos de 1967+ · F50f: **{len(en)} de {n67n}**", "",
          "| papel | cap/foto | año | marcas | frase |", "|---|---|---|---|---|"]
    L += [f"| {pp} | {x['cap']}/{x['foto']} | {x['anio']} | {', '.join(x['marcas'])} | {' '.join(x['frases'])[:300]} |"
          for pp, lst in (("F50b", ev), ("F50f", en)) for x in lst]

    # 2
    ficha = _j(steps / "ficha_caso.json")
    topic_canon = _j(steps / "05_visual_canon.json")
    formas = sorted({f for p in ficha.get("personas") or [] for f in mexp._formas(p)}
                    | {str(p.get("name") or "").strip() for p in topic_canon.get("documented_people") or []
                       if str(p.get("name") or "").strip()}, key=len, reverse=True)
    con_nombre = []
    for f in nuevo["fotos"]:
        hits = sorted({x for x in formas if re.search(rf"\b{re.escape(x)}\b", f.get("prompt") or "")})
        if hits:
            con_nombre.append((f["cap"], f["foto"], hits))
    L += ["", "## 2. Fotos con nombre propio de persona en la prosa final", "",
          f"Formas buscadas: {len(formas)} (ficha.personas + documented_people del canon). "
          f"**Fotos con nombre: {len(con_nombre)}**", ""]
    L += [f"- {c}/{n}: {', '.join(h)}" for c, n, h in con_nombre] or ["- ninguna"]

    # 3
    topic, skel, narr_ch = ex.preparar()
    caps = {c["chapter_number"]: c for c in v["chapters"]}
    exps_cap, items_cap = {}, {}
    for cap, c in caps.items():
        anchors, _ = ex._anclas(c)
        sch = next(x for x in skel["chapters"] if x["chapter_number"] == cap)
        narr = next(x for x in narr_ch if x["chapter_number"] == cap)["narration"].strip()
        exps_cap[cap] = ex.pedido_y_expedientes(mexp, topic, sch, narr, anchors, cap)[1]
        # cap Veo: foto 1 = primer cuadro del clip, después los extras
        items_cap[cap] = ([c.get("image_f8") or {}] + list(c.get("supplemental_image_prompts") or [])
                          if c.get("image_prompts") is None else c["image_prompts"])

    def sujeto(cap, foto):
        it = items_cap[cap][foto - 1] or {}
        return (json.loads(it.get("raw_llm_prompt") or "{}") or {}).get("subject") or "?"
    anclas_f50c = {(f["cap"], f["foto"]): f["ancla"]
                   for f in _j(ROOT / "lab" / "hyperframes" / "f50c" / "EXPEDIENTES_F50c.json")["fotos"]}
    L += ["", "## 3. Las 8 fotos testigo de F50c (por el texto del ancla) y las fotos con persona en el ancla", "",
          "D re-planea las anclas: una foto testigo cuenta solo si su ancla de F50c sigue siendo ancla.", "",
          "| testigo F50c | ancla | foto F50f | PEOPLE | sujeto (casillero) |", "|---|---|---|---|---|"]
    for (cap, foto), (nombres, fuente) in ex.TESTIGOS.items():
        a = anclas_f50c[(cap, foto)]
        e = next((x for x in exps_cap[cap] if x["ancla"] == a), None)
        if e is None:
            L.append(f"| {cap}/{foto} ({', '.join(nombres)}) | «{a[:70]}» | ya no es ancla | — | — |")
            continue
        L.append(f"| {cap}/{foto} ({', '.join(nombres)}) | «{a[:70]}» | {cap}/{e['foto']} | "
                 f"{', '.join(e['personas']) or '—'} ({e['personas_fuente'] or '—'}) | {sujeto(cap, e['foto'])[:240]} |")
    con_persona = [(cap, e) for cap in sorted(exps_cap) for e in exps_cap[cap] if e["personas_fuente"] == "ancla"]
    L += ["", f"Fotos del papel nuevo cuya ancla nombra a una persona: {len(con_persona)}", "",
          "| foto | personas | sujeto (casillero) |", "|---|---|---|"]
    L += [f"| {cap}/{e['foto']} | {', '.join(e['personas'])} | {sujeto(cap, e['foto'])[:200]} |"
          for cap, e in con_persona]

    # 4
    log = (F50F / "d_m03.log").read_text(encoding="utf-8", errors="replace").splitlines()
    sinp = [x.strip() for x in log if "fotos sin period" in x or "canon sin periods" in x]
    L += ["", "## 4. Log de m03: fotos sin period", ""] + [f"- `{x}`" for x in sinp]
    tot = sum(int(m.group(1)) for x in sinp if (m := re.search(r": (\d+) de \d+ fotos sin period", x)))
    L += [f"", f"**Total de fotos sin period: {tot}**"]

    # 5
    co = nuevo.get("costos") or {}
    L += ["", "## 5. Gasto real por paso", "", f"Último registro de cost_history del tema ({co.get('registro')}): "
          f"US$ {co.get('total')}", "", "| servicio · descripción | llamadas | US$ |", "|---|---:|---:|"]
    L += [f"| {k} | {x['llamadas']} | {x['usd']} |" for k, x in (co.get("por_servicio") or {}).items()]
    L += ["", f"Pasos en `01_v3_costos.json` (los últimos): {co.get('pasos_01_v3_costos')}", ""]
    (F50F / "MEDIDAS_D.md").write_text("\n".join(L), encoding="utf-8")
    print(json.dumps({"fotos": len(pn), "epoca_F50b": len(ev), "epoca_F50f": len(en), "con_nombre": len(con_nombre),
                      "sin_period": tot, "usd": co.get("total")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
