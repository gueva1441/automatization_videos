# -*- coding: utf-8 -*-
"""
lab/hyperframes/f65/sugerir_prueba.py — F65b Etapa A, salida en texto: `m01e_pantalla.sugerir` real, 2 veces, sobre el papel actual
del topic: (a) ch01 beat 1; (b) ch05 beat 9 si sigue con una ficha técnica; si no, el beat cuya ficha tenga juicio_verificador con
más marcas (el pedido de la tanda). Empate → el primero que no sea (a). PARÁ si la primera pasa de US$ 1 (alarma de bug). El papel
no se modifica. Escribe SUGERIR_PRUEBA.md y sugerir_prueba.json.
"""
from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import claude_helpers as hx  # noqa: E402
from script_engine import m01e_pantalla as m  # noqa: E402

TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
STEPS = ROOT / "data/scripts/_steps"
AQUI = Path(__file__).resolve().parent
TECNICAS = {"D01", "D51", "D40", "D61"}      # las fichas técnicas forzadas de F64 (DECISIONES 2026-10-31 15:49)


def corrida(cap: str, beat: int, papel: dict) -> tuple[dict, list[str]]:
    log: list[str] = []
    r = m.sugerir(TID, cap, beat, m.SUGERIR_N, log=log)
    b = next(x for x in papel["beats"] if x["cap"] == cap and x["beat"] == beat)
    actual = b["ficha"] or {}
    u = r["usage"][0] if r["usage"] else {}
    v = r.get("verificador") or {}
    L = [f"## {cap} beat {beat} ({b['funcion']}): hoy {actual.get('pool_id')} «{actual.get('etiqueta')} · {actual.get('texto')}»", "",
         "| | tokens in | escritos al caché | leídos del caché | tokens out | US$ | s |", "|---|---|---|---|---|---|---|",
         f"| autor | {u.get('input_tokens')} | {u.get('cache_creation_input_tokens') or 0} | {u.get('cache_read_input_tokens') or 0} | {u.get('output_tokens')} | {r['usd_autor']:.4f} | {r['segundos']} (total) |",
         f"| verificador | {(v.get('usage') or {}).get('input_tokens', '—')} | — | — | {(v.get('usage') or {}).get('output_tokens', '—')} | {r['usd_verificador']:.4f} | {v.get('segundos', '—')} |",
         f"| **total** | | | | | **{r['usd']:.4f}** | |", "", f"Excluidos: {', '.join(r['excluidos'])}", "", "### Alternativas que pasan", ""]
    for a in r["alternativas"]:
        jv = a.get("juicio_verificador")
        L += [f"- **{a['pool_id']}** [{a['estilo']}] «{a['etiqueta']} · {a['texto']}»" + (f" — {a['autor']}" if a.get("autor") else "")
              + f" · en [{a['sentence_idx']}] «{a['oracion']}» sobre «{a['palabra']}» · {a['caracteres']}/{a['caben']} car.",
              f"  - aporta: {a['aporta']}", f"  - respaldo: «{a['respaldo']}»",
              f"  - verificador: {'pasa (' + ', '.join(jv['regla']) + ' ' + str(jv['tokens']) + ') — ' + str(jv['motivo']) if jv else 'sin marcas, no se le preguntó'}"]
    if not r["alternativas"]:
        L.append("- (ninguna)")
    L += ["", "### Las que cayeron", ""]
    for d in r["descartadas"]:
        fi = d["ficha"]
        L.append(f"- {fi.get('pool_id')} «{fi.get('etiqueta')} · {fi.get('texto')}» → {d['quien']}: {d['motivo']}")
    if not r["descartadas"]:
        L.append("- (ninguna)")
    if r.get("error"):
        L += ["", f"**error: {r['error']}**"]
    return r, L + [""]


def main() -> None:
    f = STEPS / TID / "01e_pantalla.json"
    antes = hashlib.md5(f.read_bytes()).hexdigest()
    papel = json.loads(f.read_text(encoding="utf-8"))
    b9 = next(x for x in papel["beats"] if x["cap"] == "ch05" and x["beat"] == 9)
    if (b9["ficha"] or {}).get("pool_id") in TECNICAS:
        cap2, beat2, porque = "ch05", 9, "ch05 beat 9 sigue con una ficha técnica"
    else:
        cands = [(sum(len(v) for v in (x["ficha"]["juicio_verificador"].get("tokens") or {}).values()), x) for x in papel["beats"]
                 if x.get("ficha") and x["ficha"].get("juicio_verificador") and not (x["cap"] == "ch01" and x["beat"] == 1)]
        mx = max(n for n, _ in cands)
        x = next(y for n, y in cands if n == mx)
        cap2, beat2 = x["cap"], x["beat"]
        porque = (f"ch05 beat 9 ya no tiene ficha técnica ({(b9['ficha'] or {}).get('pool_id')}); el beat con juicio_verificador con más marcas "
                  f"({mx}; empate: el primero que no es el de la corrida a)")
    L = ["# F65b Etapa A — SUGERIR_PRUEBA: `sugerir` real sobre el papel nuevo", "",
         f"Papel `{papel['prompt_version']}` md5 `{antes}` · {m.MODELO} {m.EFFORT} · n = {m.SUGERIR_N} · caché `cache_control: ephemeral` en SYSTEM + USER de entrada (§2.4). Segunda corrida: {cap2} beat {beat2} ({porque}).", ""]
    r1, l1 = corrida("ch01", 1, papel)
    L += l1
    (AQUI / "sugerir_prueba.json").write_text(json.dumps({"a": r1}, ensure_ascii=False, indent=1), encoding="utf-8")
    if r1["usd"] > 1:
        (AQUI / "SUGERIR_PRUEBA.md").write_text("\n".join(L + [f"**PARÁ: la primera corrida costó US$ {r1['usd']:.4f} (> 1, alarma de bug).**"]), encoding="utf-8")
        raise SystemExit(f"PARÁ: la primera corrida costó US$ {r1['usd']:.4f}")
    r2, l2 = corrida(cap2, beat2, papel)
    L += l2
    (AQUI / "sugerir_prueba.json").write_text(json.dumps({"a": r1, "b": r2}, ensure_ascii=False, indent=1), encoding="utf-8")
    despues = hashlib.md5(f.read_bytes()).hexdigest()
    L += ["## Resultado", "", f"- Costo: a US$ {r1['usd']:.4f} (escribe el caché) · b US$ {r2['usd']:.4f} (lee el caché) · total US$ {r1['usd'] + r2['usd']:.4f}.",
          f"- Papel sin modificar: md5 antes `{antes}`, después `{despues}` ({'iguales' if antes == despues else 'DISTINTOS'}).",
          f"- `usage` a: {json.dumps(r1['usage'], ensure_ascii=False)}", f"- `usage` b: {json.dumps(r2['usage'], ensure_ascii=False)}",
          f"- tokens_entrada a/b: {[hx.tokens_entrada(u) for u in r1['usage']]} / {[hx.tokens_entrada(u) for u in r2['usage']]}", ""]
    (AQUI / "SUGERIR_PRUEBA.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
