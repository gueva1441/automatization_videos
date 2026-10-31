# -*- coding: utf-8 -*-
"""
lab/hyperframes/f67/etapa_a_critico.py — F67a (HANDOFF_F67a_critico_por_api.md): ¿el crítico de retención por API critica como el analista?
Solo lab, solo texto: lee de _steps, escribe en lab/hyperframes/f67/. Copia de la forma de f63/etapa_a_papel.py: body → hx._post, costo
hx.cost_of, hx._track sin start_video (no escribe data/cost_history.json; F63 lo midió).
SYSTEM y FORMATO_SALIDA se leen del handoff (byte a byte; PARÁ si el md5 del handoff no da).
    python lab/hyperframes/f67/etapa_a_critico.py          Etapa 1 y, si el assert de carga pasa, las 4 llamadas y las etapas 3-5
    python lab/hyperframes/f67/etapa_a_critico.py --etapa1 solo la Etapa 1, sin llamadas
    python lab/hyperframes/f67/etapa_a_critico.py --desde-raw  rehace las etapas 3-5 desde los raw guardados, sin llamadas
"""
from __future__ import annotations

import hashlib
import json
import random
import re
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any, Callable

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

AQUI = Path(__file__).resolve().parent
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
STEPS = ROOT / "data" / "scripts" / "_steps" / TID
HANDOFF = AQUI / "HANDOFF_F67a_critico_por_api.md"
HANDOFF_MD5 = "d68e9c1741baccc4a48de0785449d41a"
BRAZOS = {"O": "claude-opus-5-5", "F": "claude-fable-5-1"}
EFFORT = "medium"
CORRIDAS = ("O_1", "O_2", "F_1", "F_2")
SEMILLA = 67
# §6.1: referencia del analista: (palabras, segundos, pct, años). No va al USER.
REF = {"ch01": (161, 55, 8, 1), "ch02": (220, 75, 11, 3), "ch03": (523, 178, 27, 7), "ch04": (232, 79, 12, 1), "ch05": (292, 99, 15, 7),
       "ch06": (297, 101, 15, 4), "ch07": (216, 73, 11, 6)}
REF_TOTAL = (1941, 11.0)
TOL = 0.02
NUM = re.compile(r"\d+(?:[.,]\d+)*")


def md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def _bloques_handoff() -> tuple[str, str]:
    raw = HANDOFF.read_bytes()
    if hashlib.md5(raw).hexdigest() != HANDOFF_MD5:
        raise SystemExit(f"PARÁ: md5 del handoff {hashlib.md5(raw).hexdigest()} ≠ {HANDOFF_MD5}")
    t = raw.decode("utf-8").replace("\r\n", "\n")

    def bloque(titulo: str) -> str:
        i = t.index("```\n", t.index(titulo)) + 4
        return t[i:t.index("\n```", i)]
    return bloque("## 4. SYSTEM"), bloque("## 5. FORMATO_SALIDA")


def palabras(texto: str) -> int:
    return len(re.findall(r"\S+", texto))


def metricas_de(caps: list[dict], seg: float) -> dict[str, Any]:
    textos = [" ".join(s["texto"] for s in c["oraciones"]) for c in caps]
    n = [palabras(t) for t in textos]
    total, acum, out = sum(n), 0, []
    for c, t, k in zip(caps, textos, n):
        acum += k
        out.append({"cap": c["cap"], "titulo": c["titulo"], "oraciones": len(c["oraciones"]), "palabras": k, "segundos": round(k * seg),
                    "pct": round(100 * k / total), "pct_acumulado": round(100 * acum / total),
                    "anios_distintos": len(set(re.findall(r"\b(1[89]\d\d|20\d\d)\b", t)))})
    return {"seg_por_palabra": seg, "total_palabras": total, "total_min": round(total * seg / 60, 1), "caps": out}


def metricas_md(m: dict) -> str:
    L = ["# F67a Etapa 1 — métricas por capítulo", "", f"Total {m['total_palabras']} palabras ≈ {m['total_min']} min a {m['seg_por_palabra']} s/palabra · referencia del analista {REF_TOTAL[0]} ≈ {REF_TOTAL[1]} min", "",
         "| cap | título | oraciones | palabras | s | % | % acum. | años | ref. (pal/s/%/años) | difiere |", "|---|---|---|---|---|---|---|---|---|---|"]
    notas = []
    for c in m["caps"]:
        r = REF[c["cap"]]
        d = []
        if abs(c["palabras"] - r[0]) / r[0] > TOL:
            d.append("palabras > 2 %")
        if c["anios_distintos"] != r[3]:
            d.append("años")
        if (c["segundos"], c["pct"]) != (r[1], r[2]):
            d.append("s o %")
        notas += [f"{c['cap']}: {x}" for x in d]
        L.append(f"| {c['cap']} | {c['titulo']} | {c['oraciones']} | {c['palabras']} | {c['segundos']} | {c['pct']} | {c['pct_acumulado']} | {c['anios_distintos']} | {r[0]}/{r[1]}/{r[2]}/{r[3]} | {', '.join(d) or '—'} |")
    L += ["", "Diferencias con la referencia: " + ("; ".join(notas) if notas else "ninguna."), ""]
    return "\n".join(L)


def tabla_verificacion(md_txt: str) -> str:
    """La tabla de 01b_verificacion.md tal cual."""
    lineas = md_txt.replace("\r\n", "\n").split("\n")
    i = next(k for k, x in enumerate(lineas) if x.startswith("| cap |"))
    j = i
    while j < len(lineas) and lineas[j].startswith("|"):
        j += 1
    return "\n".join(lineas[i:j])


def reponer_humano(e: dict, escaleta: dict) -> None:
    """§2 v3: _para_modelo del papel lo quita de los beats; se repone de la misma escaleta, por `n`."""
    por_n = {b["n"]: b for b in escaleta["beats"]}
    assert len(e["beats"]) == 13 and all(b["n"] in por_n and "humano_en_escena" in por_n[b["n"]] for b in e["beats"])
    for b in e["beats"]:
        b["humano_en_escena"] = por_n[b["n"]]["humano_en_escena"]


def faltantes(e: dict) -> list[str]:
    """§2: lo que el script tiene que encontrar al cargar."""
    f = []
    ev = e.get("escaleta_video") or {}
    if "promesa_gancho" not in ev:
        f.append("entrada.escaleta_video.promesa_gancho")
    if "pico" not in ev:
        f.append("entrada.escaleta_video.pico")
    if not e.get("beats") or not all("humano_en_escena" in b for b in e["beats"]):
        f.append("entrada.beats[*].humano_en_escena")
    if not e.get("archivo") or not all("id" in x for x in e["archivo"]):
        f.append("entrada.archivo[*].id")
    if not e.get("caps") or not all("idx" in s for c in e["caps"] for s in c["oraciones"]):
        f.append("entrada.caps[*].oraciones[*].idx")
    return f


def armar_user(e: dict, m: dict, verif: str, formato: str) -> str:
    caps = [{**c, "oraciones": [{k: v for k, v in s.items() if k != "caben"} for s in c["oraciones"]]} for c in e["caps"]]
    payload = {"caps": caps, "beats": e["beats"], "escaleta_video": e["escaleta_video"], "archivo": e["archivo"], "disputas": e["disputas"],
               "metricas": m, "verificacion": verif}
    return json.dumps(payload, ensure_ascii=False, indent=None) + "\n\nFormato de salida (devolvé solo este JSON):\n" + formato


def leer_json(txt: str) -> dict | None:
    """§6.2: quitar fences ```json si las hay, json.loads."""
    t = (txt or "").strip()
    f = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", t, re.S)
    try:
        r = json.loads(f.group(1) if f else t)
    except json.JSONDecodeError:
        return None
    return r if isinstance(r, dict) else None


def llamar(corrida: str, system: str, user: str, post: Callable[[dict], dict] | None, salida: Path, log: list[str]) -> dict:
    import claude_helpers as hx
    modelo = BRAZOS[corrida[0]]
    body = {"model": modelo, "max_tokens": hx.MAX_TOKENS, "system": system, "messages": [{"role": "user", "content": user}],
            "output_config": {"effort": EFFORT}}
    out: dict[str, Any] = {"corrida": corrida, "modelo": modelo, "effort": EFFORT, "system_md5": md5(system), "user_md5": md5(user), "intentos": [],
                           "respuesta": None, "usage": None, "usd": 0.0, "segundos": 0.0}
    for k in range(2):                                # §6.2: 1 reintento idéntico
        t0 = time.time()
        try:
            r = (post or hx._post)(body)
        except Exception as e:  # noqa: BLE001 — como F63: se anota y, si es el primero, se reintenta
            seg = round(time.time() - t0, 1)
            out["intentos"].append({"error": f"{type(e).__name__}: {e}", "segundos": seg})
            out["segundos"] = round(out["segundos"] + seg, 1)
            log.append(f"{corrida} intento {k + 1}: ERROR {type(e).__name__}: {str(e)[:200]}")
            continue
        seg = round(time.time() - t0, 1)
        u = r.get("usage") or {}
        usd = round(hx.cost_of(modelo, u), 5)
        if post is None:
            hx._track(r.get("model") or modelo, u, f"lab_f67a_{corrida}")
        txt = "".join(c.get("text") or "" for c in r.get("content") or [] if c.get("type") == "text")
        resp = leer_json(txt)
        out["intentos"].append({"texto": txt, "json": resp is not None, "usage": u, "stop": r.get("stop_reason"), "usd": usd, "segundos": seg})
        out["usd"] = round(out["usd"] + usd, 5)
        out["segundos"] = round(out["segundos"] + seg, 1)
        log.append(f"{corrida} intento {k + 1}: in {u.get('input_tokens')} · out {u.get('output_tokens')} · US$ {usd:.4f} · {seg} s · {'JSON' if resp is not None else 'SIN JSON'} · stop {r.get('stop_reason')}")
        if resp is not None:
            out["respuesta"], out["usage"] = resp, u
            break
    (salida / f"{corrida}.raw.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out


def numeros(t: str) -> set[str]:
    return {re.sub(r"[.,]", "", x) for x in NUM.findall(str(t or ""))}


def validar(resp: dict | None, e: dict) -> dict[str, Any]:
    """§6.3: ids, (cap, idx), palabras antes → después y cifras sin respaldo, calculados por el código. Se reporta, no falla."""
    if resp is None:
        return {"json": False}
    arch = {x["id"]: x for x in e["archivo"]}
    ors = {(c["cap"], s["idx"]): s["texto"] for c in e["caps"] for s in c["oraciones"]}
    voz = set().union(*(numeros(t) for t in ors.values()))
    deb = [d for d in resp.get("deberia") or [] if isinstance(d, dict)]
    ids_inv, ors_inv, pal, cifras = [], [], [], []
    for k, d in enumerate(deb):
        ids = [str(i) for i in d.get("ids") or []]
        ids_inv += [i for i in ids if i not in arch]
        cap = str(d.get("cap"))
        pares = [(cap, i) for i in d.get("oraciones") or []]
        ors_inv += [f"{c}:{i}" for c, i in pares if (c, i) not in ors]
        antes = sum(palabras(ors[p]) for p in pares if p in ors)
        despues = palabras(str(d.get("deberia_texto") or ""))
        pal.append({"n": k + 1, "cap": cap, "antes": antes, "despues": despues})
        ok = set(voz)
        for i in ids:
            if i in arch:
                ok |= numeros(arch[i].get("texto")) | numeros(arch[i].get("contexto_fuente"))
        for p in pares:
            ok |= numeros(ors.get(p))
        cifras += [{"n": k + 1, "cifra": x} for x in sorted(numeros(d.get("deberia_texto"))) if x not in ok]
    return {"json": True, "nota_total": resp.get("nota_total"), "notas_cap": {str(c.get("cap")): c.get("nota") for c in resp.get("caps") or [] if isinstance(c, dict)},
            "n_deberia": len(deb), "ids_invalidos": ids_inv, "oraciones_invalidas": ors_inv, "palabras": pal, "cifras_sin_respaldo": cifras,
            "marcadas": sorted({(str(d.get("cap")), i) for d in deb for i in d.get("oraciones") or [] if isinstance(i, int)})}


def validacion_md(res: dict[str, dict], val: dict[str, dict]) -> str:
    L = ["# F67a — validación en código", "", "| brazo | nota_total | notas por cap | n deberia | ids inválidos | oraciones inválidas | palabras antes→después | cifras sin respaldo | US$ | s |", "|---|---|---|---|---|---|---|---|---|---|"]
    for k in CORRIDAS:
        v, r = val[k], res[k]
        if not v["json"]:
            L.append(f"| {k} | sin JSON | — | — | — | — | — | — | {r['usd']:.4f} | {r['segundos']} |")
            continue
        notas = " · ".join(f"{c}: {n}" for c, n in v["notas_cap"].items())
        pal = " · ".join(f"{p['cap']} {p['antes']}→{p['despues']}" for p in v["palabras"]) or "—"
        cif = ", ".join(f"#{c['n']} {c['cifra']}" for c in v["cifras_sin_respaldo"]) or "—"
        L.append(f"| {k} | {v['nota_total']} | {notas} | {v['n_deberia']} | {', '.join(v['ids_invalidos']) or '—'} | {', '.join(v['oraciones_invalidas']) or '—'} | {pal} | {cif} | {r['usd']:.4f} | {r['segundos']} |")
    return "\n".join(L) + "\n"


def varianza(val: dict[str, dict]) -> dict[str, Any]:
    out = {}
    for b in BRAZOS:
        a, c = val[f"{b}_1"], val[f"{b}_2"]
        if not (a["json"] and c["json"]):
            out[b] = {"nota": None, "jaccard": None, "interseccion": []}
            continue
        x, y = {tuple(p) for p in a["marcadas"]}, {tuple(p) for p in c["marcadas"]}
        dn = round(abs(float(a["nota_total"]) - float(c["nota_total"])), 1) if a["nota_total"] is not None and c["nota_total"] is not None else None
        out[b] = {"delta_nota": dn, "jaccard": round(len(x & y) / len(x | y), 3) if x | y else None, "interseccion": sorted(x & y), "n": [len(x), len(y)]}
    return out


def critica_md(resp: dict | None, titulo: str, cabecera: str = "") -> str:
    """Plantilla fija: mismo orden de secciones y campos para todas. Sin `cabecera`, no lleva ningún metadato (el ciego)."""
    L = [f"# {titulo}", ""]
    if cabecera:
        L += [cabecera, ""]
    if resp is None:
        return "\n".join(L + ["sin JSON válido", ""])
    g = resp.get("gancho") or {}
    p = resp.get("pico") or {}
    L += [f"**Nota total:** {resp.get('nota_total')}", "", "## Resumen", ""] + [f"- {x}" for x in resp.get("resumen") or []]
    L += ["", "## Gancho", "", f"- Promesa cumplida: {g.get('promesa_cumplida')}", f"- {g.get('comentario')}", "", "## Capítulos", "",
          "| cap | nota | personaje en voz | oraciones seguidas sin personaje | fuerte | débil | re-enganche |", "|---|---|---|---|---|---|---|"]
    for c in resp.get("caps") or []:
        L.append(f"| {c.get('cap')} | {c.get('nota')} | {c.get('personaje_en_voz')} | {c.get('oraciones_seguidas_sin_personaje')} | {c.get('fuerte')} | {c.get('debil')} | {c.get('reengancho')} |")
    L += ["", "## Loops", "", "| pregunta | abre | paga | se recuerda |", "|---|---|---|---|"]
    for x in resp.get("loops") or []:
        L.append(f"| {x.get('pregunta')} | {x.get('abre')} | {x.get('paga')} | {x.get('se_recuerda')} |")
    L += ["", "## Pico", "", f"- {p.get('cap')} · acumulado {p.get('pct_acumulado')} % · {p.get('segundos_despues')} s después", f"- {p.get('comentario')}", "", "## Cierre", "", str(resp.get("cierre")), "", "## DEBERÍA", ""]
    for k, d in enumerate(resp.get("deberia") or [], 1):
        L += [f"### {k}. {d.get('cap')} · oraciones {d.get('oraciones')}", "", f"- **Sale:** {d.get('que_sale')}", f"- **Por qué se van:** {d.get('por_que_se_van')}", f"- **Ids:** {', '.join(str(i) for i in d.get('ids') or [])}", "", f"> {d.get('deberia_texto')}", ""]
    L += ["## Reglas generales candidatas", ""]
    L += [f"- {x.get('regla')} · *medible:* {x.get('medible_como')} · *por qué:* {x.get('por_que')}" for x in resp.get("reglas_generales_candidatas") or []]
    L += ["", "## Riesgos", ""] + [f"- {x}" for x in resp.get("riesgos") or []] + [""]
    return "\n".join(L)


def snapshot() -> dict[str, int]:
    fs = {p.relative_to(ROOT).as_posix(): p.stat().st_mtime_ns for p in STEPS.rglob("*") if p.is_file()}
    h = ROOT / "data" / "cost_history.json"
    fs[h.relative_to(ROOT).as_posix()] = h.stat().st_mtime_ns
    return fs


def etapas_3_5(res: dict[str, dict], e: dict, a: Path) -> dict[str, Any]:
    val = {k: validar(res[k]["respuesta"], e) for k in CORRIDAS}
    for k in CORRIDAS:
        r = res[k]
        u = r["usage"] or {}
        cab = f"{r['modelo']} {r['effort']} · US$ {r['usd']:.4f} · tokens in {u.get('input_tokens')} · out {u.get('output_tokens')} · {r['segundos']} s · {len(r['intentos'])} intento(s)"
        (a / f"{k}.md").write_text(critica_md(r["respuesta"], f"Crítica {k}", cab), encoding="utf-8")
    (a / "validacion.md").write_text(validacion_md(res, val), encoding="utf-8")
    orden = list(CORRIDAS)
    random.Random(SEMILLA).shuffle(orden)
    (a / "ciego").mkdir(exist_ok=True)
    clave = {}
    for n, k in enumerate(orden, 1):
        nombre = f"critica_{n:02d}"
        clave[nombre] = k
        (a / "ciego" / f"{nombre}.md").write_text(critica_md(res[k]["respuesta"], nombre), encoding="utf-8")
    (a / "clave_ciego.json").write_text(json.dumps(clave, ensure_ascii=False, indent=1), encoding="utf-8")
    var = varianza(val)
    (a / "varianza.json").write_text(json.dumps(var, ensure_ascii=False, indent=1), encoding="utf-8")
    return {"val": val, "var": var}


def main() -> int:
    a = AQUI / "a"
    a.mkdir(exist_ok=True)
    system, formato = _bloques_handoff()
    raw = json.loads((STEPS / "01e_pantalla.raw.json").read_text(encoding="utf-8"))
    e = raw["entrada"]
    seg = json.loads((STEPS / "01e_pantalla.json").read_text(encoding="utf-8"))["seg_por_palabra"]["valor"]
    m = metricas_de(e["caps"], seg)
    (a / "metricas.md").write_text(metricas_md(m), encoding="utf-8")
    print(metricas_md(m))
    reponer_humano(e, json.loads((STEPS / "01a_escaleta.json").read_text(encoding="utf-8")))
    f = faltantes(e)
    if f:
        print(f"ABORTA (§2): faltan en la entrada: {f}. `beats` trae: {list(e['beats'][0])}")
        return 2
    verif = tabla_verificacion((STEPS / "01b_verificacion.md").read_text(encoding="utf-8"))
    user = armar_user(e, m, verif, formato)
    (a / "user.json").write_text(user, encoding="utf-8", newline="\n")  # sin \r\n de Windows: el md5 del archivo es el del USER enviado
    (a / "md5.json").write_text(json.dumps({"system": md5(system), "user": md5(user), "chars_user": len(user), "entrada_md5": raw.get("entrada_md5")}, indent=1), encoding="utf-8")
    print("md5 SYSTEM", md5(system), "· md5 USER", md5(user), "·", len(user), "car.")
    if "--etapa1" in sys.argv:
        return 0
    if "--desde-raw" in sys.argv:
        res = {k: json.loads((a / f"{k}.raw.json").read_text(encoding="utf-8")) for k in CORRIDAS}
        assert all(r["user_md5"] == md5(user) and r["system_md5"] == md5(system) for r in res.values())
        print("varianza", json.dumps(etapas_3_5(res, e, a)["var"], ensure_ascii=False))
        return 0
    (a / "mtimes_antes.json").write_text(json.dumps(snapshot(), indent=0), encoding="utf-8")
    log: list[str] = []
    t0 = time.time()
    with ThreadPoolExecutor(max_workers=len(CORRIDAS)) as ex:
        res = dict(zip(CORRIDAS, ex.map(lambda k: llamar(k, system, user, None, a, log), CORRIDAS)))
    (a / "llamadas.log").write_text("\n".join(log) + "\n", encoding="utf-8")
    r = etapas_3_5(res, e, a)
    desp = snapshot()
    (a / "mtimes_despues.json").write_text(json.dumps(desp, indent=0), encoding="utf-8")
    print("\n".join(log))
    print((a / "validacion.md").read_text(encoding="utf-8"))
    print("varianza", json.dumps(r["var"], ensure_ascii=False))
    print("US$ total", round(sum(x["usd"] for x in res.values()), 4), "· pared", round(time.time() - t0, 1), "s")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
