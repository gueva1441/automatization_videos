# -*- coding: utf-8 -*-
"""
lab/hyperframes/f66/medir_c.py — F66 Etapa C, después de la corrida (solo lectura, CERO llamadas): qué cambió en la narración
(antes = lab/hyperframes/f66/antes/, después = _steps) y qué efectos tuvo cada corrección: párrafo antes → después, oraciones
sacadas, palabras por cap, si siguen la oración del re-gancho y las preguntas de la escaleta, los bloqueantes del guion con
`verificar` falso (solo los del código) antes y después, diferencias del skeleton, títulos. Escribe MEDIR_C.md.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import fase1_5 as f15  # noqa: E402
from script_engine import evidence as ev  # noqa: E402
from script_engine import guion_v4 as g4  # noqa: E402
from script_engine.voz_utils import oraciones_de_texto  # noqa: E402

TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
D = ROOT / "data/scripts/_steps" / TID
A = Path(__file__).resolve().parent / "antes"


def j(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> None:
    n0, n1 = j(A / "01b_narracion_v3.json"), j(D / "01b_narracion_v3.json")
    v = j(D / "01b_verificacion.json")
    esc = j(D / "01a_escaleta.json")
    L = ["# F66 Etapa C — qué le hizo la corrección a la narración (0 llamadas)", ""]
    L += ["| cap | palabras antes | palabras después | oraciones antes | oraciones después |", "|---|---|---|---|---|"]
    for c0, c1 in zip(n0["caps"], n1["caps"]):
        L.append(f"| {c0['chapter_number']} | {len(c0['narration'].split())} | {len(c1['narration'].split())} | "
                 f"{len(oraciones_de_texto(c0['narration']))} | {len(oraciones_de_texto(c1['narration']))} |")
    L += ["", "## Párrafo antes → después, por edición", ""]
    for e in v["ediciones"]:
        viejas, nuevas = oraciones_de_texto(e["antes"]), oraciones_de_texto(e["despues"])
        L += [f"### cap {e['cap']} beat {e['beat']} · {'aceptada' if e['aceptada'] else 'rechazada: ' + e['motivo_rechazo']}", ""]
        L += [f"- problema: «{p['frase']}» → {p['motivo'][:300]}" for p in e["problemas"]]
        L += [f"- SALE: «{s}»" for s in viejas if s not in nuevas]
        L += [f"- ENTRA: «{s}»" for s in nuevas if s not in viejas]
        L += [""]
    voz0, voz1 = ev.norm(" ".join(p["texto"] for p in n0["parrafos"])), ev.norm(" ".join(p["texto"] for p in n1["parrafos"]))
    rl = esc.get("recuerda_loop") or {}
    L += ["## Lo que la escaleta espera de la voz", ""]
    if isinstance(rl, dict) and rl.get("oracion"):
        o = ev.norm(str(rl["oracion"]))
        L.append(f"- `recuerda_loop` (beat {rl.get('beat')}): «{rl['oracion']}» → antes {'está' if o in voz0 else 'NO está'} · después "
                 f"{'está' if o in voz1 else '**NO está**'}")
    prom = esc.get("_promesa_oraciones")
    L.append(f"- `promesa_gancho`: «{esc.get('promesa_gancho')}»")
    for o in (prom if isinstance(prom, list) else []):
        t = ev.norm(str(o))
        L.append(f"- `_promesa_oraciones`: «{o}» → antes {'está' if t in voz0 else 'NO está'} · después {'está' if t in voz1 else '**NO está**'}")
    L.append(f"- `loops`: {json.dumps(esc.get('loops'), ensure_ascii=False)[:600]}")
    L.append("")
    # bloqueantes del código, con el verificador de Sonnet apagado (verificar falso = None): solo comparan antes/después
    topic = f15._topic_v3(TID)
    from researcher_steps.ficha_caso import load as load_ficha
    ficha = load_ficha(TID, f15.STEPS_DIR)

    def bl(ps: list[dict]) -> list[dict]:
        return g4.bloqueantes(topic, esc, g4.with_ids([dict(p) for p in ps], topic["evidence_pool"], esc), "abierto", ficha, verificar=lambda *a, **k: None)
    b0, b1 = bl(n0["parrafos"]), bl(n1["parrafos"])
    k = lambda x: (x.get("codigo"), x.get("beat"), str(x.get("motivo"))[:120])
    L += [f"## Bloqueantes del guion con el verificador de Sonnet apagado: antes {len(b0)} → después {len(b1)}", ""]
    nuevos = [x for x in b1 if k(x) not in {k(y) for y in b0}]
    L += [f"- NUEVO ({x.get('codigo')}) beat {x.get('beat')}: {str(x.get('motivo'))[:300]}" for x in nuevos] or ["- ningún bloqueante nuevo"]
    idos = [x for x in b0 if k(x) not in {k(y) for y in b1}]
    L += [f"- se fue ({x.get('codigo')}) beat {x.get('beat')}: {str(x.get('motivo'))[:200]}" for x in idos]
    s0, s1 = j(A / "01a_skeleton.json"), j(D / "01a_skeleton.json")
    L += ["", "## Skeleton", "", f"- títulos iguales: {[c['title'] for c in s0['chapters']] == [c['title'] for c in s1['chapters']]}",
          f"- particion antes: {s0['_v3'].get('particion')}", f"- particion después: {s1['_v3'].get('particion')}",
          f"- claves que cambian en chapters: {sorted({k2 for c0, c1 in zip(s0['chapters'], s1['chapters']) for k2 in c0 if c0[k2] != c1.get(k2)})}",
          f"- otras claves del skeleton que cambian: {[k2 for k2 in s0 if k2 != '_v3' and s0[k2] != s1.get(k2)]}", ""]
    (Path(__file__).resolve().parent / "MEDIR_C.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
