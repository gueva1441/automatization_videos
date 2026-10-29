# -*- coding: utf-8 -*-
"""F50e-A/B — CANON_MODELOS.md desde CANON_MODELOS.json (F50e-A, 7 corridas), CANON_MODELOS_B.json (F50e-B: opus_2 y
opus_3, si existe) y canon_<modelo>_<n>.json (solo lee; sin API). La medida 4a–4g se recalcula para las 9 desde sus
json con `canon_modelos.medir` (F50e-B agregó 4g: grupos con appearance vacío).
Uso: python lab/hyperframes/f50e/canon_modelos_md.py
"""
import json
import sys
from pathlib import Path

F50E = Path(__file__).resolve().parent
sys.path.insert(0, str(F50E))


def main() -> int:
    import canon_modelos as cm
    d = json.loads((F50E / "CANON_MODELOS.json").read_text(encoding="utf-8"))
    fb = F50E / "CANON_MODELOS_B.json"
    db = json.loads(fb.read_text(encoding="utf-8")) if fb.exists() else None
    C = {**d["corridas"], **((db or {}).get("corridas") or {})}
    fotos = cm.fotos_con_anio()
    for k, r in C.items():                              # 4a–4g recalculada desde el json de cada corrida
        if not r.get("falla"):
            r["medida"] = cm.medir(json.loads((F50E / f"canon_{k}.json").read_text(encoding="utf-8")), fotos)
    L = ["# CANON_MODELOS — el canon de Wittenoom con Flash, Sonnet 5.5 y Opus 5.5 (F50e-A y F50e-B, en texto)", "",
         "Salida de `python -u lab/hyperframes/f50e/canon_modelos.py` (las llamadas) y `canon_modelos_md.py` (esta "
         "tabla). Mismo pedido que `step_4e.canon_desde_ficha`; nada se guardó en producción.", "",
         f"- md5 del pedido: `{d['md5_pedido']}` en todos los intentos de las {len(C)} corridas: "
         f"{'sí' if all(i['md5_pedido'] == d['md5_pedido'] for r in C.values() for i in r['intentos']) else 'NO'}",
         f"- Producción intacta (md5 antes = después): topics_db {d['produccion_intacta']['topics_db']} · "
         f"05_visual_canon.json {d['produccion_intacta']['05_visual_canon']}",
         f"- Gasto F50e-A (cost_tracker `f50e-canon-modelos`): US$ {d['total_usd']} · tope US$ 1,00",
         f"- F50e-A, parada por tope: {d['parada']}" if d["parada"] else "- F50e-A sin parada por tope",
         *([f"- **F50e-B** (opus_2 y opus_3, directo sin esquema; cost_tracker `f50e-b-canon-opus`): US$ "
            f"{db['total_usd']} · tope US$ 1,00 · md5 del pedido `{db['md5_pedido']}` · producción intacta: "
            f"topics_db {db['produccion_intacta']['topics_db']} · 05_visual_canon.json "
            f"{db['produccion_intacta']['05_visual_canon']}"] if db else []),
         f"- Fotos: {d['fotos']}, con año (anio_ancla o respaldo[0]): {d['fotos_con_anio']}", "",
         "**Aviso — el esquema no llegó a los modelos Claude.** El primer intento de cada corrida de Sonnet y Opus "
         "(con `VISUAL_CANON_SCHEMA_FICHA` como structured output) volvió HTTP 400: «Schemas contains too many optional "
         "parameters (46)… (limit: 24)». `extract_visual_canon` cayó entonces a su respaldo de producción: el MISMO "
         "texto, sin esquema. Esas respuestas son las que se miden. Flash sí corrió con el esquema. El pedido es el "
         "mismo; el formato forzado, no.", "",
         "## Resumen por modelo", "",
         "| modelo | corridas medidas | fotos cubiertas mín · máx | grupos (por corrida) | grupos con años sin ropa "
         "(por corrida) | grupos sin appearance (por corrida) | years ilegibles | US$ promedio por corrida | fallas |",
         "|---|---|---|---|---|---|---|---:|---|"]
    for mod in ("flash", "sonnet", "opus"):
        rs = {k: r for k, r in C.items() if k.startswith(mod + "_")}
        med = [r["medida"] for r in rs.values() if r.get("medida")]
        cub = [m["cubiertas"] for m in med]
        fallas = [f"{k}: {r['falla']}" for k, r in rs.items() if r.get("falla")]
        no_corr = 3 - len(rs)
        L.append(f"| {mod} | {len(med)} de 3" + (f" ({no_corr} no corrieron: tope)" if no_corr else "") + " | "
                 + (f"{min(cub)} · {max(cub)} de {med[0]['con_anio']}" if med else "—") + " | "
                 + " / ".join(str(len(m["grupos"])) for m in med) + " | "
                 + " / ".join(str(m["grupos_con_anios_sin_ropa"]) for m in med) + " | "
                 + " / ".join(f"{len(m['sin_appearance'])}/{len(m['grupos'])}" for m in med) + " | "
                 + (", ".join(sorted({y for m in med for y in m["ilegibles"]})) or "ninguno") + " | "
                 + f"{sum(r['usd'] for r in rs.values()) / max(len(rs), 1):.4f} | " + ("; ".join(fallas) or "—") + " |")
    L += ["", "## Por corrida", "",
          "| corrida | periods (4a) | fotos cubiertas (4b) | por cap 1–7 (cubiertas/con año) | grupos (4d) | con años "
          "sin ropa | ilegibles (4e) | tokens in / out / thinking (4f) | US$ | s | intentos |",
          "|---|---|---:|---|---:|---:|---|---|---:|---:|---:|"]
    for k, r in C.items():
        m = r.get("medida")
        if not m:
            L.append(f"| {k} | **FALLA: {r['falla']}** | — | — | — | — | — | {r['tokens_in']} / {r['tokens_out']} / "
                     f"{r['tokens_thinking']} | {r['usd']} | {r.get('segundos')} | {len(r['intentos'])} |")
            continue
        pc = " · ".join(f"{m['por_cap'][c]['cubiertas']}/{m['por_cap'][c]['con_anio']}" for c in sorted(m["por_cap"],
                                                                                                        key=int))
        L.append(f"| {k} | {' · '.join(map(str, m['periods']))} | {m['cubiertas']}/{m['con_anio']} | {pc} | "
                 f"{len(m['grupos'])} | {m['grupos_con_anios_sin_ropa']} | {', '.join(m['ilegibles']) or '—'} | "
                 f"{r['tokens_in']} / {r['tokens_out']} / {r['tokens_thinking']} | {r['usd']} | {r.get('segundos')} | "
                 f"{len(r['intentos'])} |")
    L += ["", "## 4c — fotos sin ningún period que las cruce (y el que les daría la regla del «más cercano»)", ""]
    for k, r in C.items():
        m = r.get("medida")
        if not m:
            continue
        sin = m["sin_period"]
        if not sin:
            L.append(f"- {k}: ninguna")
            continue
        por = {}
        for s in sin:
            por.setdefault((s["cap"], tuple(s["le_daria"])), []).append(s["anio"])
        L.append(f"- {k}: {len(sin)} fotos — " + "; ".join(f"cap {c}: {sorted(set(a))} → {' · '.join(t)}"
                                                          for (c, t), a in sorted(por.items())))
    L += ["", "## 4d — grupos con años de su where_when sin ropa por tramo", ""]
    for k, r in C.items():
        m = r.get("medida")
        if not m:
            continue
        g = [x for x in m["grupos"] if x["anios_sin_ropa"]]
        L.append(f"- {k}: " + ("; ".join(f"`{x['id']}` años {x['anios_sin_ropa']} (ropa: {' · '.join(map(str, x['ropa'])) or '—'})"
                                          for x in g) or "ninguno"))
    L += ["", "## 4g — grupos con appearance vacío", ""]
    for k, r in C.items():
        m = r.get("medida")
        if m:
            L.append(f"- {k}: {len(m['sin_appearance'])}/{len(m['grupos'])} — "
                     + (", ".join(f"`{x}`" for x in m["sin_appearance"]) or "ninguno"))
    L += ["", "## Ejemplo — la corrida de peor cobertura de cada modelo", ""]
    for mod in ("flash", "sonnet", "opus"):
        rs = [(k, r) for k, r in C.items() if k.startswith(mod + "_") and r.get("medida")]
        if not rs:
            continue
        # peor = menos fotos cubiertas; empate → más grupos sin appearance (4g, F50e-B)
        k, r = min(rs, key=lambda kr: (kr[1]["medida"]["cubiertas"], -len(kr[1]["medida"]["sin_appearance"])))
        canon = json.loads((F50E / f"canon_{k}.json").read_text(encoding="utf-8"))
        per = (canon.get("era_visual_canon") or {}).get("periods") or []
        g = max(canon.get("people_groups") or [{}], key=lambda x: len(r["medida"]["grupos"] and
                                                                      [y for y in r["medida"]["grupos"]
                                                                       if y["id"] == x.get("id")][0]["anios"] or []))
        L += [f"### {k} ({r['medida']['cubiertas']}/{r['medida']['con_anio']})", "", "```json",
              json.dumps(per, ensure_ascii=False, indent=1), "```", "", "Grupo con más años:", "", "```json",
              json.dumps(g, ensure_ascii=False, indent=1), "```", ""]
    (F50E / "CANON_MODELOS.md").write_text("\n".join(L), encoding="utf-8")
    print("ok")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
