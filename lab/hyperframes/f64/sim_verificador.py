# -*- coding: utf-8 -*-
"""
lab/hyperframes/f64/sim_verificador.py — F64 Etapa 3, simulación obligatoria antes de la corrida real: las 8 respuestas
del autor de F63 (`lab/hyperframes/f63/a/*_[12].raw.json`, clave `respuesta`) validadas con el `validar` NUEVO de
producción (entrada completa de la Etapa 0 con `cargar`/`entrada`/`_para_modelo` de script_engine.m01e_pantalla; nunca
se importa de etapa_a_papel) y el verificador REAL (script_engine.pantalla_verificador.verificar, Opus medium): una
llamada por papel, las 8 a la vez. Escribe:
  - lab/hyperframes/f64/sim/<brazo>_<n>.json: marcas, veredictos, usage, usd, segundos, descartados y beats finales;
  - lab/hyperframes/f64/SIM_VERIFICADOR.md: por papel cada marca con regla, token, veredicto y motivo; totales (marcas,
    pasa, corta, dicho, no_dicho); costo y segundos por llamada; contra la tabla DEBERÍA de REVISION_CIEGA_F63.md §2
    (lo que el analista marcó bueno y el verificador corta, o al revés) y contra los veredictos que el handoff espera.
Solo lab: no toca data/ ni _steps (lee); el costo se registra con hx._track("m01e_verificador") sin start_video.
"""
from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from script_engine import m01e_pantalla as m  # noqa: E402
from script_engine import pantalla_verificador as pv  # noqa: E402
from script_engine.clima import vocabulario_clima  # noqa: E402

TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
STEPS = ROOT / "data" / "scripts" / "_steps"
AQUI = Path(__file__).resolve().parent
A63 = AQUI.parent / "f63" / "a"
SIM = AQUI / "sim"

# REVISION_CIEGA_F63.md §2: lo que el analista pondría por beat (ids «buenos»), y lo que marcó flojo o malo
DEBERIA = {1: {"D26", "D80", "D108"}, 2: {"Q25"}, 3: {"D83"}, 4: {"D02", "D82", "Q27"}, 5: {"D44", "D135"}, 6: {"D115"},
           7: {"Q19"}, 8: {"D102"}, 9: {"D141", "D94"}, 10: {"D23", "D35", "Q35"}, 11: {"Q22"}, 12: {"D58", "D150"},
           13: {"D69", "D68", "T86"}}
MALAS = {1: {"D79"}, 3: {"T38"}, 7: {"Q17"}, 10: {"D109"}, 11: {"D73", "T57"}, 12: {"T80", "D64"}}
# HANDOFF_F64 §Etapa 3 «Revisión del prompt por el analista»: lo que espera que devuelva el verificador
ESPERADOS = [("D79", "ficha", None, "corta"), ("D23", "ficha", None, "pasa"), ("D108", "ficha", None, "pasa"),
             ("Q25", "ficha", None, "pasa"), ("D94", "ficha", "fecha_relato", "pasa"), ("D141", "ficha", None, "pasa"),
             ("D21", "descarte", None, "dicho"), ("T80", "descarte", None, "dicho")]


def un_papel(nombre: str, resp: dict, ent: dict) -> dict:
    log: list[str] = []
    reg: list[dict] = []

    def juez(marcas, caps):
        v = pv.verificar(marcas, caps, log=log)
        reg.append(v)
        return v
    t0 = time.time()
    val = m.validar(resp, ent, juez=juez)
    v = reg[0] if reg else None
    vf = {(x["pool_id"], x["cap"], x["beat"]): x for x in (v or {}).get("veredictos_fichas") or []}
    vd = {x["pool_id"]: x for x in (v or {}).get("veredictos_descartes") or []}
    filas = []
    for mk in val["marcas"]:
        if mk.get("que") == "descarte":
            x = vd.get(mk["pool_id"]) or {}
            filas.append({"que": "descarte", "pool_id": mk["pool_id"], "regla": "voz_lo_dice", "token": ", ".join(mk.get("falta") or []),
                          "cap": None, "beat": None, "veredicto": x.get("veredicto"), "motivo": x.get("motivo"),
                          "oracion": x.get("oracion"), "dato": mk.get("dato_archivo")})
        else:
            x = vf.get((mk["pool_id"], mk["cap"], mk["beat"])) or {}
            co = mk.get("coincidencia") or {}
            filas.append({"que": "ficha", "pool_id": mk["pool_id"], "regla": mk["regla"], "token": str(co.get("token")),
                          "donde": f"{co.get('cap')} [{co.get('idx')}]" if co.get("cap") else "—", "cap": mk["cap"],
                          "beat": mk["beat"], "veredicto": x.get("veredicto"), "motivo": x.get("motivo"),
                          "oracion": x.get("oracion"), "dato": f"{mk['etiqueta']} · {mk['texto']}"})
    return {"papel": nombre, "marcas": val["marcas"], "filas": filas, "verificador": v, "log": log,
            "segundos_total": round(time.time() - t0, 1),
            "descartados": val["descartados"], "beats": val["beats"], "vuelven": val["vuelven"], "motivos": val["motivos"],
            "claves": [list(c) for c in val["claves"]]}


def main() -> None:
    SIM.mkdir(exist_ok=True)
    carga = m.cargar(TID, STEPS)
    ent = m.entrada(carga, vocabulario_clima())
    ent["_pool"] = carga["pool"]
    raws = sorted(p for p in A63.glob("*_[12].raw.json"))
    assert len(raws) == 8, [p.name for p in raws]
    papeles = {p.name.split(".raw")[0]: json.loads(p.read_text(encoding="utf-8"))["respuesta"] for p in raws}
    with ThreadPoolExecutor(max_workers=8) as ex:
        futs = {n: ex.submit(un_papel, n, r, ent) for n, r in papeles.items()}
        res = {n: f.result() for n, f in futs.items()}
    for n, r in res.items():
        (SIM / f"{n}.json").write_text(json.dumps(r, ensure_ascii=False, indent=1), encoding="utf-8")

    L = ["# F64 Etapa 3 — SIM_VERIFICADOR: los 8 papeles de F63 contra el `validar` nuevo + verificador real", "",
         f"Topic `{TID}` · entrada completa de producción (archivo {len(ent['archivo'])} ítems) · verificador "
         f"`{pv.MODELO}` {pv.EFFORT} · una llamada por papel, 8 a la vez · fuente: `lab/hyperframes/f63/a/*_[12].raw.json` "
         f"(`respuesta`) · salidas crudas en `lab/hyperframes/f64/sim/`.", ""]
    # ── totales
    L += ["## Totales por papel", "", "| papel | marcas | fichas marcadas | pasa | corta | descartes marcados | dicho | no_dicho | "
          "tokens in/out | US$ | s (llamada) | intentos | error |", "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    tot = {"marcas": 0, "pasa": 0, "corta": 0, "dicho": 0, "no_dicho": 0, "usd": 0.0, "s": 0.0}
    for n in sorted(res):
        r = res[n]
        v = r["verificador"] or {}
        f = [x for x in r["filas"] if x["que"] == "ficha"]
        d = [x for x in r["filas"] if x["que"] == "descarte"]
        pasa = sum(1 for x in v.get("veredictos_fichas") or [] if x["veredicto"] == "pasa")
        corta = sum(1 for x in v.get("veredictos_fichas") or [] if x["veredicto"] == "corta")
        dicho = sum(1 for x in v.get("veredictos_descartes") or [] if x["veredicto"] == "dicho")
        nod = sum(1 for x in v.get("veredictos_descartes") or [] if x["veredicto"] == "no_dicho")
        u = v.get("usage") or {}
        L.append(f"| {n} | {len(r['marcas'])} | {len({(x['pool_id'], x['cap'], x['beat']) for x in f})} | {pasa} | {corta} | "
                 f"{len(d)} | {dicho} | {nod} | {u.get('input_tokens')}/{u.get('output_tokens')} | {v.get('usd', 0):.4f} | "
                 f"{v.get('segundos')} | {v.get('intentos')} | {v.get('error') or '—'} |")
        for k, val_ in (("marcas", len(r["marcas"])), ("pasa", pasa), ("corta", corta), ("dicho", dicho), ("no_dicho", nod),
                        ("usd", v.get("usd") or 0.0), ("s", v.get("segundos") or 0.0)):
            tot[k] += val_
    L += [f"| **total** | {tot['marcas']} | | {tot['pasa']} | {tot['corta']} | | {tot['dicho']} | {tot['no_dicho']} | | "
          f"**{tot['usd']:.4f}** | {tot['s']:.1f} | | |", ""]
    # ── por papel, cada marca
    L += ["## Cada marca, con su veredicto", ""]
    for n in sorted(res):
        r = res[n]
        L += [f"### {n}", "", "| que | id | cap/beat | regla | token (dónde lo dice la voz) | veredicto | motivo del verificador | oración |",
              "|---|---|---|---|---|---|---|---|"]
        for x in r["filas"]:
            o = x.get("oracion") or {}
            o_txt = f"{o.get('cap')} [{o.get('idx')}]" if isinstance(o, dict) and o.get("cap") else "—"
            cb = f"{x['cap']} b{x['beat']}" if x["cap"] else "—"
            dd = (f"«{x['token']}» ({x.get('donde')})" if x["que"] == "ficha" else f"no dice {x['token']}")
            L.append(f"| {x['que']} | {x['pool_id']} | {cb} | {x['regla']} | {dd} | **{x['veredicto']}** | "
                     f"{str(x.get('motivo') or '').replace('|', '/')[:160]} | {o_txt} |")
        if not r["filas"]:
            L.append("| (sin marcas) | | | | | | | |")
        cortadas = [d for d in r["descartados"] if d.get("quien") == "verificador"]
        L += ["", f"- fichas que quedan: {sum(1 for b in r['beats'] if b['ficha'])}/13 · cortadas por el verificador: "
              f"{[d['pool_id'] for d in cortadas]} · cortadas por el código: "
              f"{[(d['pool_id'], d['regla']) for d in r['descartados'] if d.get('quien') == 'validación' and d.get('que') == 'ficha']} · "
              f"vuelven: {[v['pool_id'] for v in r['vuelven']]} · motivos para una vuelta: {len(r['motivos'])}", ""]
    # ── contra DEBERÍA y contra lo que espera el handoff
    L += ["## Contra la tabla DEBERÍA de REVISION_CIEGA_F63.md §2 (para el analista)", "",
          "Lo que el analista marcó bueno (DEBERÍA del beat) y el verificador **corta**:", ""]
    hubo = False
    for n in sorted(res):
        for x in res[n]["filas"]:
            if x["que"] == "ficha" and x["veredicto"] == "corta" and x["pool_id"] in DEBERIA.get(x["beat"], set()):
                hubo = True
                L.append(f"- {n}: {x['pool_id']} ({x['cap']} b{x['beat']}, {x['regla']} «{x['token']}») → corta: {x.get('motivo')}")
    if not hubo:
        L.append("- (ninguna)")
    L += ["", "Lo que el analista marcó flojo o malo y el verificador **pasa** (el verificador juzga el hecho, no la calidad: "
          "informativo):", ""]
    hubo = False
    for n in sorted(res):
        for x in res[n]["filas"]:
            if x["que"] == "ficha" and x["veredicto"] == "pasa" and x["pool_id"] in MALAS.get(x["beat"], set()):
                hubo = True
                L.append(f"- {n}: {x['pool_id']} ({x['cap']} b{x['beat']}, {x['regla']} «{x['token']}») → pasa: {x.get('motivo')}")
    if not hubo:
        L.append("- (ninguna)")
    L += ["", "Fichas cortadas por el verificador que NO están en el DEBERÍA ni en lo marcado malo (ni bueno ni malo para el analista):", ""]
    hubo = False
    for n in sorted(res):
        for x in res[n]["filas"]:
            if x["que"] == "ficha" and x["veredicto"] == "corta" and x["pool_id"] not in DEBERIA.get(x["beat"], set()) \
                    and x["pool_id"] not in MALAS.get(x["beat"], set()):
                hubo = True
                L.append(f"- {n}: {x['pool_id']} ({x['cap']} b{x['beat']}, {x['regla']} «{x['token']}») → corta: {x.get('motivo')}")
    if not hubo:
        L.append("- (ninguna)")
    L += ["", "## Contra los veredictos que el handoff espera (§Etapa 3, «Revisión del prompt por el analista»)", "",
          "| id | que | regla | esperado | papeles donde hay marca | veredictos obtenidos |", "|---|---|---|---|---|---|"]
    for pid, que, regla, esp in ESPERADOS:
        donde, obt = [], []
        for n in sorted(res):
            for x in res[n]["filas"]:
                if x["pool_id"] == pid and x["que"] == que and (regla is None or x["regla"] == regla):
                    donde.append(f"{n} ({x['regla']} «{x['token']}»)" if que == "ficha" else n)
                    obt.append(x["veredicto"])
        ok = "✓" if obt and all(o == esp for o in obt) else ("✗" if obt else "—")
        L.append(f"| {pid} | {que} | {regla or 'cualquiera'} | {esp} | {'; '.join(donde) or '— (sin marca)'} | "
                 f"{', '.join(o or '?' for o in obt) or '—'} {ok} |")
    L += ["", f"Costo de la simulación: US$ {tot['usd']:.4f} ({len(res)} llamadas; estimado del handoff ≈ 0,5).", ""]
    (AQUI / "SIM_VERIFICADOR.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
