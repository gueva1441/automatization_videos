"""F24 §A.4 y §D.1 — el registro de fuentes de Kyshtym con lo que está en disco (sin API) y una corrida en seco de
R1 unido: lo que trajo la R1 de F23 + el registro, en el orden del cupo de R2 (sin bajar nada).

    · `_steps/f18-kyshtym-mayak/fuentes.json` (la salida de R1 de F23) → `fuentes_r1.json`; `fuentes.json` = el registro.
    · `registro_kyshtym.json` (copia) y `registro_kyshtym.md` (tabla + la corrida en seco).
Uso: python -I lab/hyperframes/f24/f24_registro.py
"""
from __future__ import annotations

import json
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
D = ROOT / "data" / "scripts" / "_steps" / "f18-kyshtym-mayak"
OSETROV = "cyberleninka.ru/article/n/kyshtymskaya-radiatsionnaya-avariya-1957-goda"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    from researcher_steps import research_v3 as r3
    viejo = json.loads((D / "fuentes.json").read_text(encoding="utf-8"))
    if not viejo.get("registro"):                       # la salida de R1 de F23
        if not (D / r3.R1_SALIDA).exists():
            shutil.copy2(D / "fuentes.json", D / r3.R1_SALIDA)
        r1 = viejo
    else:
        r1 = json.loads((D / r3.R1_SALIDA).read_text(encoding="utf-8"))
    reg = r3.registro_desde_disco(D)
    (D / r3.REGISTRO_FUENTES).write_text(json.dumps(reg, ensure_ascii=False, indent=1), encoding="utf-8")
    (LAB / "registro_kyshtym.json").write_text(json.dumps(reg, ensure_ascii=False, indent=1), encoding="utf-8")
    F = reg["fuentes"]
    L = ["# Registro de fuentes de Kyshtym (F24 §A.4) y R1 unido en seco (§D.1)", "",
         f"**{len(F)} fuentes** en el registro · **{sum(1 for e in F if e['bajada_ok'])} bajadas** (txt en `fuentes/`) · "
         f"**{sum(1 for e in F if r3.aporte_total(e) > 0)} con aporte** al pool (datos + citas + personajes > 0). "
         "Armado sin API con las salidas de R1, los manifests y los pools de F18–F23 que están en disco "
         "(`veces_vista` = en cuántos de esos archivos figura).", "",
         "| # | url | idioma | bajada | chars | aporte (d/c/p) | de | veces |", "|---|---|---|---|---|---|---|---|"]
    for i, e in enumerate(sorted(F, key=lambda e: -r3.aporte_total(e)), start=1):
        a = e.get("aporte") or {}
        L.append(f"| {i} | {e['url'][:80]} | {r3.fuente_idioma(e.get('doc') or e)} | {'sí' if e['bajada_ok'] else 'no'} | "
                 f"{e.get('chars') or 0} | {a.get('datos', '—')}/{a.get('citas', '—')}/{a.get('personajes', '—')} | "
                 f"{e.get('aporte_de') or '—'} | {e.get('veces_vista')} |")
    # corrida en seco: R1 de F23 + registro → orden del cupo (10 OK por idioma); lo bajado cuenta como OK
    cands = r3.unir_fuentes(r1["fuentes"], reg)
    prev = r3.previos_del_registro(reg)
    n_ok: dict[str, int] = {}
    L += ["", "## R1 unido en seco", "",
          f"R1 de F23: {len(r1['fuentes'])} fuentes; candidatos con el registro: {len(cands)}. Orden del cupo de R2 "
          f"(aporte primero, después la prioridad de R1); `MAX_DESCARGAS_OK` = {r3.MAX_DESCARGAS_OK} por idioma. Lo que "
          "ya está bajado entra sin pedir nada; lo que no, figura como «se pediría».", "",
          "| id | url | idioma | aporte | estado en seco |", "|---|---|---|---|---|"]
    ose = None
    for f in sorted(cands, key=lambda f: (-(f.get("_aporte") or 0), f["prioridad"], f["id"])):
        lg = r3.fuente_idioma(f)
        if n_ok.get(lg, 0) >= r3.MAX_DESCARGAS_OK:
            st = f"fuera del cupo ({lg} lleno)"
        elif any(r3._site(f["url"]) == s or r3.domain(f["url"]).endswith(s) for s in r3.NO_TEXT_SITES):
            st = "sin texto (video)"
        elif f["url"] in prev:
            n_ok[lg] = n_ok.get(lg, 0) + 1
            st = f"**reusada** ({prev[f['url']].get('txt')}) · cupo {lg} {n_ok[lg]}/{r3.MAX_DESCARGAS_OK}"
        else:
            st = "se pediría (no está bajada)"
        if OSETROV in f["url"]:
            ose = (f["id"], st)
        L.append(f"| {f['id']} | {f['url'][:80]} | {lg} | {f.get('_aporte')} | {st} |")
    L += ["", f"**El artículo de Osetrov/Komarov/Serov** (`{OSETROV}…`): {ose[0]} → {ose[1]}." if ose else
          "**El artículo de Osetrov no está en el registro.**"]
    (LAB / "registro_kyshtym.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L[:4] + L[-1:]))


if __name__ == "__main__":
    main()
