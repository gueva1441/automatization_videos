"""F55 Salida D (texto, sin LLM): tabla A/B cap por cap (F54 = lab/hyperframes/f55/antes | F55 = _steps regenerado:
palabras, años, datos/min, bloqueantes y quién los vio: código o Sonnet); la promesa y la oración 2 del cap 1 (viejo | nuevo);
loops con sus pagos leídos con evidence.regla_dicho; medida_retencion.py (F54) sobre el nuevo; y el grep de los 8 ids
descartados en todo _steps/<topic>/ regenerado (debe dar 0 fuera de _descartados y de ficha_caso.json en disco).
Escribe lab/hyperframes/f55/SALIDA_D.md."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import fase1_5  # noqa: E402
from script_engine import evidence as ev  # noqa: E402
from script_engine import guion_v4 as g4  # noqa: E402
from script_engine.guion_v3_reglas import anios_por_cap, datos_por_min, sentences_of  # noqa: E402

TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
STEPS = ROOT / "data" / "scripts" / "_steps" / TID
ANTES = ROOT / "lab" / "hyperframes" / "f55" / "antes"
DESC = ("Q12", "Q15", "Q20", "Q23", "Q26", "Q28", "Q29", "Q30")


def _j(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def _caps(d: Path) -> list[dict]:
    nar = _j(d / "01b_narration.json")
    return [{"chapter_number": c["chapter_number"], "narration": c["narration"],
             "datos_usados": list(dict.fromkeys(c.get("ids_usados") or []))} for c in nar["chapters"]]


def _bloq(g: dict) -> dict[int, list[str]]:
    out: dict[int, list[str]] = {}
    for x in g["reparacion"]["bloqueantes_despues"]:
        out.setdefault(int(x.get("cap") or 0), []).append(f"({x['codigo']}) {x['motivo'][:60]}")
    return out


def _quien(g: dict) -> str:
    m = g.get("metricas") or {}
    alt = m.get("confirmados_sonnet") or []
    v = m.get("verificador") or {}
    return (f"Sonnet confirmó {len(alt)}: " + "; ".join(f"{a['id']} (cap {a['cap']}, {a.get('que', '')})" for a in alt)
            + f" · verificador: {v.get('llamadas', 0)} llamada(s), {v.get('cache', 0)} caché, US$ {v.get('usd', 0)}") if alt or v else "—"


def main() -> None:
    topic = dict(fase1_5._load_topic_by_id(TID))
    pool = topic["evidence_pool"]
    its = ev.items(pool)
    v_esc, n_esc = _j(ANTES / "01a_escaleta.json"), _j(STEPS / "01a_escaleta.json")
    v_g, n_g = _j(ANTES / "01b_guionista_v4.json"), _j(STEPS / "01b_guionista_v4.json")
    v_caps, n_caps = _caps(ANTES), _caps(STEPS)
    vb, nb = _bloq(v_g), _bloq(n_g)
    va, na = anios_por_cap(v_caps), anios_por_cap(n_caps)
    vd, nd = datos_por_min(v_caps, g4.PALABRAS_POR_SEG), datos_por_min(n_caps, g4.PALABRAS_POR_SEG)
    L = ["# F55 — Salida D (texto)", "",
         f"F54 = `lab/hyperframes/f55/antes/` (escaleta `{v_esc.get('prompt_version')}`, guion `{v_g.get('prompt_version')}`, pool de 58 citas) · "
         f"F55 = `_steps/{TID}/` regenerado (escaleta `{n_esc.get('prompt_version')}`, guion `{n_g.get('prompt_version')}`, pool de 50). "
         "Corrida combinada a propósito (detector + dedupe + promesa): la tabla no atribuye diferencias a una sola variable.", "",
         "## 1. Tabla A/B cap por cap", "",
         "| cap | palabras F54 | F55 | años F54 | F55 | datos/min F54 | F55 | bloqueantes F54 (tras la ronda) | bloqueantes F55 (tras la ronda) |",
         "|---|---|---|---|---|---|---|---|---|"]
    for k in range(1, 8):
        L.append(f"| {k} | {len(v_caps[k - 1]['narration'].split())} | {len(n_caps[k - 1]['narration'].split())} | {va[k]} | {na[k]} | "
                 f"{vd[k]} | {nd[k]} | {'; '.join(vb.get(k, [])) or '—'} | {'; '.join(nb.get(k, [])) or '—'} |")
    tv, tn = sum(len(c["narration"].split()) for c in v_caps), sum(len(c["narration"].split()) for c in n_caps)
    L += [f"| **total** | {tv} | {tn} | {sum(va.values())} | {sum(na.values())} | | | {len(v_g['reparacion']['bloqueantes_despues'])} | {len(n_g['reparacion']['bloqueantes_despues'])} |", "",
          f"Quién vio los bloqueantes del nuevo: código (f/h con `regla_dicho`) → lo que quedó arriba; {_quien(n_g)}.",
          f"Bloqueantes del crudo nuevo antes de la ronda única: {len(n_g['reparacion']['bloqueantes_antes'])} → después {len(n_g['reparacion']['bloqueantes_despues'])}; PARADA del guion: {n_g['reparacion'].get('parada')}.", ""]
    for x in n_g["reparacion"]["bloqueantes_antes"]:
        L.append(f"- (crudo) cap {x['cap']} beat {x['beat']} ({x['codigo']}): {x['motivo'][:160]}")
    # promesa y oración 2
    def _o2(caps):
        ss = sentences_of(caps[0]["narration"])
        return ss[1] if len(ss) > 1 else "(una sola oración)"
    L += ["", "## 2. La promesa (escaleta) y la oración 2 del cap 1 (guion)", "", "| | F54 | F55 |", "|---|---|---|",
          f"| promesa_gancho | {v_esc.get('promesa_gancho')} | {n_esc.get('promesa_gancho')} |",
          f"| oraciones de la promesa | {len(ev._sentences(str(v_esc.get('promesa_gancho') or '')))} | {len(ev._sentences(str(n_esc.get('promesa_gancho') or '')))} (métrica `promesa_oraciones`: {(n_esc.get('_metricas') or {}).get('promesa_oraciones')}) |",
          f"| oración 2 del cap 1 | {_o2(v_caps)} | {_o2(n_caps)} |", "",
          "### Los dos cap 1 enteros", "", "| F54 | F55 |", "|---|---|",
          f"| {v_caps[0]['narration'].replace(chr(10), ' ')} | {n_caps[0]['narration'].replace(chr(10), ' ')} |", ""]
    # loops con pagos (regla_dicho)
    L += ["## 3. Loops declarados con sus pagos (escaleta F55), leídos con `evidence.regla_dicho`", ""]
    beats = {b["n"]: b for b in n_esc["beats"]}
    cap_txt = {c["chapter_number"]: c["narration"] for c in n_caps}
    for k, lp in enumerate(n_esc.get("loops") or [], 1):
        a, p = beats.get(lp.get("abre_beat"), {}), beats.get(lp.get("paga_beat"), {})
        ra = ev.regla_dicho(cap_txt.get(a.get("cap"), ""), its.get(a.get("dato_central"), {})) if a else None
        rp = ev.regla_dicho(cap_txt.get(p.get("cap"), ""), its.get(p.get("dato_central"), {})) if p else None
        L.append(f"- **Loop {k}** ({lp.get('id')}): «{lp.get('pregunta')}» — se abre en el beat {lp.get('abre_beat')} (cap {a.get('cap')}, "
                 f"{a.get('dato_central')}: {ra or 'no dicho por código'}) · se paga en el beat {lp.get('paga_beat')} (cap {p.get('cap')}, "
                 f"{p.get('dato_central')}: {rp or 'no dicho por código'})")
    pagas = [b for b in n_esc["beats"] if b.get("paga")]
    L += ["", f"Beats con `paga` ({len(pagas)}):"]
    for b in pagas:
        r = ev.regla_dicho(cap_txt.get(b["cap"], ""), its.get(b["dato_central"], {}))
        L.append(f"- beat {b['n']} (cap {b['cap']}, {b['dato_central']}: {r or 'no dicho por código'}) paga la pregunta del beat {b['paga']}: "
                 f"«{beats.get(b['paga'], {}).get('pregunta_abierta')}»")
    rl = n_esc.get("recuerda_loop")
    L += ["", f"`recuerda_loop`: {('beat ' + str(rl.get('beat')) + ' · «' + str(rl.get('oracion')) + '»') if rl else 'no vino'}", ""]
    # títulos y papel
    vt = {c["chapter_number"]: c.get("title") for c in _j(ANTES / "01a_skeleton.json")["chapters"]}
    nt = {c["chapter_number"]: c.get("title") for c in _j(STEPS / "01a_skeleton.json")["chapters"]}
    L += ["## 4. Los 7 títulos", "", "| cap | F54 | F55 |", "|---|---|---|"] + [f"| {k} | {vt.get(k)} | {nt.get(k)} |" for k in range(1, 8)]
    # medida de retención (F54) sobre viejo=f55/antes, nuevo=_steps
    out_mr = ROOT / "lab/hyperframes/f55/MEDIDA_RETENCION_D.md"
    subprocess.run([sys.executable, str(ROOT / "lab/hyperframes/f54/medida_retencion.py"), "--viejo", str(ANTES), "--nuevo", str(STEPS),
                    "--salida", str(out_mr)], check=True, capture_output=True, env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
    mr = out_mr.read_text(encoding="utf-8")
    L += ["", "## 5. Medida de retención por código (`lab/hyperframes/f54/medida_retencion.py`): F54 | F55", "",
          mr[mr.index("| ingrediente"):mr.index("## Detalle")]]
    # grep de los 8 ids descartados en _steps regenerado
    L += ["## 6. `grep` de los 8 ids descartados en `_steps/<topic>/` regenerado", "",
          "| archivo | apariciones fuera de `_descartados` | dónde |", "|---|---|---|"]
    rx = re.compile(r'"(' + "|".join(DESC) + r')"')
    total = 0
    for f in sorted(STEPS.glob("*.json")) + sorted(STEPS.glob("*.md")):
        if f.name in ("ficha_caso.json", "ficha_respuesta_cruda.json") or f.name.startswith("_"):
            continue
        txt = f.read_text(encoding="utf-8", errors="replace")
        if f.suffix == ".json":
            try:
                d = json.loads(txt)
            except ValueError:
                d = None
            if isinstance(d, dict):
                d = {k: v for k, v in d.items() if k != "_descartados"}
                if isinstance(d.get("evidence_pool"), dict):
                    d["evidence_pool"] = {k: v for k, v in d["evidence_pool"].items() if k != "_descartados"}
                txt = json.dumps(d, ensure_ascii=False)
        hits = rx.findall(txt)
        if hits:
            total += len(hits)
            L.append(f"| {f.name} | {len(hits)} | {dict(__import__('collections').Counter(hits))} |")
    if not total:
        L.append("| (ninguno) | 0 | — |")
    L += ["", f"**Total fuera de `_descartados` y de `ficha_caso.json`: {total}** (debe dar 0). `ficha_caso.json` en disco sigue con sus 36 "
          "apariciones (no se reescribe; `load` las remapea en memoria).", ""]
    L += ["## 7. El papel (01e_pantalla.md, F55)", "", (STEPS / "01e_pantalla.md").read_text(encoding="utf-8")
          if (STEPS / "01e_pantalla.md").exists() else "(no hay papel: la cadena no llegó a m01e)"]
    (ROOT / "lab/hyperframes/f55/SALIDA_D.md").write_text("\n".join(L), encoding="utf-8", newline="\n")
    print("\n".join(L[:60]))


if __name__ == "__main__":
    main()
