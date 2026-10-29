"""F54 adenda 2026-10-29 18:30 (1) — medida de retención por código, sin LLM: los ingredientes, viejo | nuevo, cap por cap.
Por guion (escaleta + narración + pool): segundos hasta la primera apuesta (primera oración que dice el dato del pico o
del `paga_beat` del loop principal, a PALABRAS_POR_SEG); loops abiertos / pagados y si el pago es la primera oración del
cap; re-gancho (sí/no, minuto: la oración de `recuerda_loop` dicha en su cap); años/cap y datos/min (guion_v3_reglas);
el cierre vuelve a la imagen del gancho (el `dato_central` del beat cierre dicho en el cap 7). Informa, no frena.
Uso: python lab/hyperframes/f54/medida_retencion.py [--viejo DIR] [--nuevo DIR] [--salida MD]
"""
from __future__ import annotations

import argparse
import json
import sys
from difflib import SequenceMatcher
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import fase1_5  # noqa: E402
from script_engine import evidence as ev  # noqa: E402
from script_engine import guion_v4 as g4  # noqa: E402
from script_engine import m01b_guionista as mg  # noqa: E402
from script_engine.guion_v3_reglas import anios_por_cap, datos_por_min, sentences_of  # noqa: E402
from script_engine.m05_narrative import used_items  # noqa: E402

TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
STEPS = ROOT / "data" / "scripts" / "_steps" / TID
PPS = g4.PALABRAS_POR_SEG


def _wc(t: str) -> int:
    return len(t.split())


def cargar(d: Path, pool: dict) -> dict:
    esc = json.loads((d / "01a_escaleta.json").read_text(encoding="utf-8"))
    nar = json.loads((d / "01b_narration.json").read_text(encoding="utf-8"))
    caps = [{"chapter_number": c["chapter_number"], "narration": c["narration"],
             "datos_usados": list(dict.fromkeys(c.get("ids_usados") or c.get("datos_usados") or []))}
            for c in nar["chapters"]]
    return {"esc": esc, "caps": caps}


_U = {"uno": 1, "un": 1, "una": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5, "seis": 6, "siete": 7, "ocho": 8,
      "nueve": 9, "diez": 10, "once": 11, "doce": 12, "trece": 13, "catorce": 14, "quince": 15, "dieciseis": 16,
      "diecisiete": 17, "dieciocho": 18, "diecinueve": 19, "veinte": 20, "treinta": 30, "cuarenta": 40, "cincuenta": 50,
      "sesenta": 60, "setenta": 70, "ochenta": 80, "noventa": 90}
_RX_ANIO = None


def _anios_a_digitos(s: str) -> str:
    """«mil novecientos noventa y uno» → «1991», «dos mil siete» → «2007»: `evidence.used_in` ancla los eventos por el
    año en cifras y la voz lo dice en letras (la misma ceguera que deja a T64 fuera de los ids del cap 5 en producción;
    acá se corrige solo para medir). Las palabras son las que `m01a_escaleta.NUM_PALABRA` ya reconoce, al revés."""
    import re
    global _RX_ANIO
    if _RX_ANIO is None:
        from script_engine.m01a_escaleta import NUM_PALABRA
        _RX_ANIO = re.compile(rf"\b(mil (?:ochocientos|novecientos)(?: (?:{NUM_PALABRA}))?|dos mil (?:{NUM_PALABRA}))\b")

    def _n(m: "re.Match") -> str:
        w = m.group(1).split()
        base = 2000 if w[0] == "dos" else 1800 if w[1] == "ochocientos" else 1900
        resto = w[2:] if w[0] == "dos" else w[2:]
        if w[0] == "dos":
            resto = w[2:]
        tot = 0
        for x in resto:
            if x == "y":
                continue
            if x.startswith("veinti") and x != "veinte":
                tot += 20 + _U.get(x[6:], 0)
            else:
                tot += _U.get(x, 0)
        return str(base + tot)
    return _RX_ANIO.sub(_n, ev.norm(s))


def _dice(texto: str, item: dict | None) -> bool:
    """Lo que decide producción (`evidence.used_in`), con los años en letras pasados a cifras; para un evento con fecha,
    además vale que el año y una palabra del hecho estén en el mismo cap aunque no en la misma oración («Madrid, 1991.
    Daniel muere…»): `used_in` los exige en la misma oración y por eso T64 no figura en los ids del cap 5 (anotado)."""
    if not item:
        return False
    t = _anios_a_digitos(texto)
    if ev.used_in(texto, item) or ev.used_in(t, item):
        return True
    dated = item.get("_kind") == "cronologia" or (item.get("_kind") == "datos" and item.get("tipo") == "fecha")
    if not dated:
        return False
    ancs = ev.anchors(item)
    words = ev._content(ev.text_of(item))
    return any(ev.literal_in(a, t) for a in ancs) and (not words or bool(words & ev._content(t)))


def _oracion_que_dice(texto: str, item: dict | None) -> int | None:
    """Índice de la oración donde el dato se dice: `used_in` decide sobre el cap entero (los eventos con fecha ponen
    el año y el hecho en oraciones vecinas: «Madrid, 1991. Daniel muere…»); la oración es la primera con un ancla del
    dato (año o cifra) o, sin anclas, la primera con una palabra de contenido del dato."""
    if not _dice(texto, item):
        return None
    ss = sentences_of(texto)
    ancs = ev.anchors(item)
    for k, s in enumerate(ss):
        if any(ev.literal_in(a, _anios_a_digitos(s)) for a in ancs):
            return k
    words = ev._content(ev.text_of(item))
    for k, s in enumerate(ss):
        if words & ev._content(s):
            return k
    return 0


def primera_apuesta(esc: dict, caps: list[dict], its: dict) -> dict:
    """Primera oración del video que dice el dato del pico o el dato central del paga_beat del loop principal."""
    beats = {b["n"]: b for b in esc["beats"]}
    ids = []
    pk = beats.get(int((esc.get("pico") or {}).get("beat") or 0))
    if pk:
        ids.append(("pico", pk["dato_central"]))
    loops = esc.get("loops") or []
    if loops:
        pb = beats.get(int(loops[0].get("paga_beat") or 0))
        if pb:
            ids.append(("loop principal", pb["dato_central"]))
    seg = 0.0
    for c in caps:
        ss = sentences_of(c["narration"])
        hits = [(k, que, i) for que, i in ids for k in [_oracion_que_dice(c["narration"], its.get(i))] if k is not None]
        if hits:
            k, que, i = min(hits)
            return {"segundos": round(seg + sum(_wc(s) for s in ss[:k]) / PPS, 1), "cap": c["chapter_number"],
                    "que": f"{que} ({i})", "oracion": ss[k]}
        seg += sum(_wc(s) for s in ss) / PPS
    return {"segundos": None, "cap": None, "que": "ninguno", "oracion": ""}


def loops_pagados(esc: dict, caps: list[dict], its: dict) -> list[dict]:
    beats = {b["n"]: b for b in esc["beats"]}
    by_cap = {c["chapter_number"]: c for c in caps}
    out = []
    pagos = [(f"loop {lp.get('id') or k}", lp.get("abre_beat"), lp.get("paga_beat"), lp.get("pregunta"))
             for k, lp in enumerate(esc.get("loops") or [], 1)]
    pagos += [(f"beat {b['n']} paga", b["paga"], b["n"], beats.get(b["paga"], {}).get("pregunta_abierta"))
              for b in esc["beats"] if b.get("paga")]
    for que, a, p, preg in pagos:
        ba, bp = beats.get(a), beats.get(p)
        if not bp:
            out.append({"que": que, "abre": a, "paga": p, "abierto": None, "pagado": None, "primera_oracion": None})
            continue
        ca, cp = by_cap.get(ba["cap"]) if ba else None, by_cap.get(bp["cap"])
        abierto = bool(ca) and bool(ba) and _dice(ca["narration"], its.get(ba["dato_central"]))
        k = _oracion_que_dice(cp["narration"], its.get(bp["dato_central"])) if cp else None
        pagado = k is not None
        primera = k == 0
        out.append({"que": que, "pregunta": preg, "abre": a, "paga": p, "dato": bp["dato_central"],
                    "abierto": abierto, "pagado": pagado, "primera_oracion": primera, "cap_pago": bp["cap"]})
    return out


def re_gancho(esc: dict, caps: list[dict]) -> dict:
    rl = esc.get("recuerda_loop") or {}
    if not rl or not rl.get("oracion"):
        return {"declarado": False, "dicho": False, "minuto": None}
    beats = {b["n"]: b for b in esc["beats"]}
    cap = beats.get(int(rl.get("beat") or 0), {}).get("cap")
    seg, mejor = 0.0, (0.0, None, None)
    for c in caps:
        for s in sentences_of(c["narration"]):
            if c["chapter_number"] == cap:
                r = SequenceMatcher(None, ev.norm(s), ev.norm(rl["oracion"])).ratio()
                if r > mejor[0]:
                    mejor = (r, round(seg / 60, 2), s)
            seg += _wc(s) / PPS
    return {"declarado": True, "beat": rl.get("beat"), "cap": cap, "oracion": rl["oracion"],
            "dicho": mejor[0] >= 0.6, "parecido": round(mejor[0], 2), "minuto": mejor[1], "oracion_dicha": mejor[2]}


def cierre_vuelve(esc: dict, caps: list[dict], its: dict) -> dict:
    b = next((b for b in esc["beats"] if b.get("funcion") == "cierre"), None)
    if not b:
        return {"dato": None, "dicho": None}
    c7 = next((c for c in caps if c["chapter_number"] == b["cap"]), None)
    dicho = bool(c7) and _dice(c7["narration"], its.get(b["dato_central"]))
    return {"beat": b["n"], "dato": b["dato_central"], "cap": b["cap"], "dicho": dicho,
            "gancho_dato": esc["beats"][0]["dato_central"]}


def medir(d: Path, pool: dict) -> dict:
    g = cargar(d, pool)
    esc, caps = g["esc"], g["caps"]
    its = ev.items(pool)
    # datos usados: si la narración no los trae, se calculan (used_items ∩ beats del cap, como en producción)
    for c in caps:
        if not c["datos_usados"]:
            own = {i for b in esc["beats"] if b["cap"] == c["chapter_number"]
                   for i in [b["dato_central"], *(b.get("datos_apoyo") or [])]}
            c["datos_usados"] = [i for i in used_items(c["narration"], pool, hard=False) if i in own]
    return {"dir": str(d), "prompt_escaleta": esc.get("prompt_version"),
            "palabras_por_cap": {c["chapter_number"]: _wc(c["narration"]) for c in caps},
            "anios_por_cap": anios_por_cap(caps), "datos_por_min": datos_por_min(caps, PPS),
            "primera_apuesta": primera_apuesta(esc, caps, its), "loops": loops_pagados(esc, caps, its),
            "re_gancho": re_gancho(esc, caps), "cierre": cierre_vuelve(esc, caps, its),
            "loops_declarados": len(esc.get("loops") or []), "beats_con_paga": [b["n"] for b in esc["beats"] if b.get("paga")]}


def tabla(v: dict, n: dict) -> str:
    L = ["| ingrediente | viejo | nuevo |", "|---|---|---|"]
    pa = lambda m: (f"{m['primera_apuesta']['segundos']} s (cap {m['primera_apuesta']['cap']}, {m['primera_apuesta']['que']})"
                    if m["primera_apuesta"]["segundos"] is not None else "nunca")
    L.append(f"| segundos hasta la primera apuesta | {pa(v)} | {pa(n)} |")
    lp = lambda m: (f"{m['loops_declarados']} declarado(s) · "
                    + "; ".join(f"{x['que']} ({x['dato']}): {'pagado' if x['pagado'] else 'NO pagado'}"
                                f"{', en la primera oración del cap' if x['primera_oracion'] else ''}"
                                for x in m["loops"]) if m["loops"] else f"{m['loops_declarados']} declarado(s)")
    L.append(f"| loops abiertos / pagados | {lp(v)} | {lp(n)} |")
    rg = lambda m: ("no declarado" if not m["re_gancho"]["declarado"] else
                    f"{'sí' if m['re_gancho']['dicho'] else 'declarado pero no dicho'} (cap {m['re_gancho']['cap']}, "
                    f"min {m['re_gancho']['minuto']}, parecido {m['re_gancho']['parecido']})")
    L.append(f"| re-gancho | {rg(v)} | {rg(n)} |")
    ci = lambda m: f"{'sí' if m['cierre']['dicho'] else 'NO'} ({m['cierre']['dato']} en el cap {m['cierre']['cap']})"
    L.append(f"| el cierre vuelve a la imagen del gancho | {ci(v)} | {ci(n)} |")
    L += ["", "| cap | palabras v | n | años v | n | datos/min v | n |", "|---|---|---|---|---|---|---|"]
    for k in range(1, 8):
        L.append(f"| {k} | {v['palabras_por_cap'].get(k, 0)} | {n['palabras_por_cap'].get(k, 0)} | "
                 f"{v['anios_por_cap'].get(k, 0)} | {n['anios_por_cap'].get(k, 0)} | "
                 f"{v['datos_por_min'].get(k, 0)} | {n['datos_por_min'].get(k, 0)} |")
    return "\n".join(L)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--viejo", default=str(ROOT / "lab/hyperframes/f54/antes"))
    ap.add_argument("--nuevo", default=str(STEPS))
    ap.add_argument("--salida", default=str(ROOT / "lab/hyperframes/f54/MEDIDA_RETENCION.md"))
    a = ap.parse_args()
    topic = dict(fase1_5._load_topic_by_id(TID))
    pool = topic["evidence_pool"]
    v, n = medir(Path(a.viejo), pool), medir(Path(a.nuevo), pool)
    md = ["# F54 — medida de retención por código (adenda 18:30, 1): viejo | nuevo", "",
          f"viejo = `{a.viejo}` (escaleta {v['prompt_escaleta']}) · nuevo = `{a.nuevo}` (escaleta {n['prompt_escaleta']}) · "
          f"{PPS} pal/s. Informa, no frena.", "", tabla(v, n), "", "## Detalle", "",
          "```json", json.dumps({"viejo": v, "nuevo": n}, ensure_ascii=False, indent=1), "```"]
    Path(a.salida).write_text("\n".join(md), encoding="utf-8", newline="\n")
    print("\n".join(md[:6]))


if __name__ == "__main__":
    main()
