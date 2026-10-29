"""F54 Salida B (texto, sin LLM): tabla A/B cap por cap (viejo | nuevo: palabras, años, datos/min, bloqueantes) · los
dos cap 1 lado a lado · loops declarados con sus pagos · 7 títulos · el papel. Lee lab/hyperframes/f54/antes/ (viejo)
y data/scripts/_steps/<Wittenoom>/ (nuevo). Escribe lab/hyperframes/f54/SALIDA_B.md.
Los bloqueantes del guion nuevo salen de 01b_guionista_v4.json (antes/después de la ronda única); los del viejo, de la
corrida de la Parte A sobre su 01b_narration.json (salida_a.py, misma función)."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import fase1_5  # noqa: E402
from script_engine import guion_v4 as g4  # noqa: E402
from script_engine.guion_v3_reglas import anios_por_cap, datos_por_min  # noqa: E402

TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
STEPS = ROOT / "data" / "scripts" / "_steps" / TID
ANTES = ROOT / "lab" / "hyperframes" / "f54" / "antes"
sys.path.insert(0, str(ROOT / "lab" / "hyperframes" / "f54"))
from salida_a import parrafos_de_la_narracion  # noqa: E402


def _j(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def _caps(d: Path) -> list[dict]:
    nar = _j(d / "01b_narration.json")
    return [{"chapter_number": c["chapter_number"], "narration": c["narration"],
             "datos_usados": list(dict.fromkeys(c.get("ids_usados") or []))} for c in nar["chapters"]]


def _bloq_por_cap(bl: list[dict]) -> dict[int, list[str]]:
    out: dict[int, list[str]] = {}
    for x in bl:
        out.setdefault(int(x.get("cap") or 0), []).append(f"({x['codigo']}) {x['motivo'][:70]}")
    return out


def main() -> None:
    topic = dict(fase1_5._load_topic_by_id(TID))
    pool = topic["evidence_pool"]
    fase1_5.cargar_perfil(TID)
    ficha = _j(STEPS / "ficha_caso.json")
    v_esc, n_esc = _j(ANTES / "01a_escaleta.json"), _j(STEPS / "01a_escaleta.json")
    v_caps, n_caps = _caps(ANTES), _caps(STEPS)
    n_g = _j(STEPS / "01b_guionista_v4.json")
    # bloqueantes: viejo = misma corrida de la Parte A (01b_narration del viejo); nuevo = los de la reparación guardada
    import salida_a
    salida_a.STEPS = ANTES
    v_ps = parrafos_de_la_narracion()
    v_bl = g4.bloqueantes(topic, v_esc, v_ps, "abierto", ficha)
    n_bl0, n_bl1 = n_g["reparacion"]["bloqueantes_antes"], n_g["reparacion"]["bloqueantes_despues"]
    vb, nb = _bloq_por_cap(v_bl), _bloq_por_cap(n_bl1)
    va, na = anios_por_cap(v_caps), anios_por_cap(n_caps)
    vd, nd = datos_por_min(v_caps, g4.PALABRAS_POR_SEG), datos_por_min(n_caps, g4.PALABRAS_POR_SEG)
    L = ["# F54 — Salida B (texto)", "",
         f"viejo = `lab/hyperframes/f54/antes/` (escaleta `{v_esc.get('prompt_version')}`, guion `{_j(ANTES / '01b_guionista_v4.json').get('prompt_version')}`) · "
         f"nuevo = `data/scripts/_steps/{TID}/` (escaleta `{n_esc.get('prompt_version')}`, guion `{n_g.get('prompt_version')}`).", "",
         "## 1. Tabla A/B cap por cap", "",
         "| cap | palabras v | n | años v | n | datos/min v | n | bloqueantes viejo | bloqueantes nuevo (tras la ronda única) |",
         "|---|---|---|---|---|---|---|---|---|"]
    for k in range(1, 8):
        vw, nw = len(v_caps[k - 1]["narration"].split()), len(n_caps[k - 1]["narration"].split())
        L.append(f"| {k} | {vw} | {nw} | {va[k]} | {na[k]} | {vd[k]} | {nd[k]} | {'; '.join(vb.get(k, [])) or '—'} | "
                 f"{'; '.join(nb.get(k, [])) or '—'} |")
    tv, tn = sum(len(c["narration"].split()) for c in v_caps), sum(len(c["narration"].split()) for c in n_caps)
    L += [f"| **total** | {tv} | {tn} | {sum(va.values())} | {sum(na.values())} | | | {len(v_bl)} | {len(n_bl1)} |", "",
          f"Guion nuevo: bloqueantes antes de la ronda única {len(n_bl0)} → después {len(n_bl1)}"
          + (f" · PARADA del guion: {n_g['reparacion'].get('parada')}" if n_g.get("reparacion") else "") + ".", ""]
    if n_bl0:
        L += ["Bloqueantes del crudo nuevo (antes de reparar):", ""]
        L += [f"- cap {x['cap']} beat {x['beat']} ({x['codigo']}): {x['motivo']}" + (f" — «{x['frase'][:120]}»" if x.get('frase') else "")
              for x in n_bl0]
        L.append("")
    L += ["## 2. Los dos cap 1, lado a lado", "", "| viejo (f26-1 / f25-1) | nuevo (f54-1 / f54-2) |", "|---|---|",
          f"| {v_caps[0]['narration'].replace(chr(10), ' ')} | {n_caps[0]['narration'].replace(chr(10), ' ')} |", "",
          f"Promesa del gancho — viejo: «{v_esc.get('promesa_gancho')}» · nuevo: «{n_esc.get('promesa_gancho')}»", "",
          "## 3. Loops declarados con sus pagos (escaleta nueva)", ""]
    beats = {b["n"]: b for b in n_esc["beats"]}
    for k, lp in enumerate(n_esc.get("loops") or [], 1):
        a, p = beats.get(lp.get("abre_beat"), {}), beats.get(lp.get("paga_beat"), {})
        L.append(f"- **Loop {k}** ({lp.get('id')}): «{lp.get('pregunta')}» — se abre en el beat {lp.get('abre_beat')} "
                 f"(cap {a.get('cap')}, {a.get('dato_central')}) · se paga en el beat {lp.get('paga_beat')} (cap {p.get('cap')}, "
                 f"{p.get('dato_central')}: {p.get('pregunta_abierta')})")
    pagas = [b for b in n_esc["beats"] if b.get("paga")]
    L += ["", f"Beats con `paga` ({len(pagas)}):"] + [f"- beat {b['n']} (cap {b['cap']}, {b['dato_central']}) paga la pregunta del beat "
                                                    f"{b['paga']}: «{beats.get(b['paga'], {}).get('pregunta_abierta')}»" for b in pagas]
    rl = n_esc.get("recuerda_loop")
    L += ["", f"`recuerda_loop`: {('beat ' + str(rl.get('beat')) + ' · «' + str(rl.get('oracion')) + '»') if rl else 'no vino'}", ""]
    L += ["## 4. Los 7 títulos", "", "| cap | viejo | nuevo |", "|---|---|---|"]
    vt = {c["chapter_number"]: c.get("title") for c in _j(ANTES / "01a_skeleton.json")["chapters"]}
    nt = {c["chapter_number"]: c.get("title") for c in _j(STEPS / "01a_skeleton.json")["chapters"]}
    for k in range(1, 8):
        L.append(f"| {k} | {vt.get(k)} | {nt.get(k)} |")
    L += ["", "## 5. El papel (01e_pantalla.md, nuevo)", ""]
    papel = STEPS / "01e_pantalla.md"
    L.append(papel.read_text(encoding="utf-8") if papel.exists() else "(no hay papel: la cadena no llegó a m01e)")
    out = ROOT / "lab" / "hyperframes" / "f54" / "SALIDA_B.md"
    out.write_text("\n".join(L), encoding="utf-8", newline="\n")
    print("\n".join(L[:40]))


if __name__ == "__main__":
    main()
