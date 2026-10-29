# -*- coding: utf-8 -*-
"""F50c §2–3 — pedidos EN SECO de los 7 caps de Wittenoom con el expediente nuevo (sin llamar a Opus: la llamada se
corta antes de salir) y la verificación automática del handoff.

Por cap se arma el pedido de casilleros dos veces, con las mismas anclas y el mismo topic:
- «antes»: `m03_expediente` del commit 1ecf045 (F50b), cargado aparte;
- «después»: `m03_expediente` de hoy.
El resto del pedido es el código de producción (`m03_visual._render_prompts_seedream`). Las anclas son las de
`03_visual.json` (las del papel de F50b); los beats salen de `assign_beats`, como en producción, y se comparan con los
guardados.

Salidas: pedidos/pedido_chNN.txt (después) y pedidos/antes/pedido_chNN.txt (antes), EXPEDIENTES_F50c.md/.json.
Uso: python lab/hyperframes/f50c/expedientes_f50c.py   → sale 1 si alguna verificación no da lo esperado.
"""
from __future__ import annotations

import difflib
import importlib.util
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
F50C = Path(__file__).resolve().parent
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
COMMIT_ANTES = "1ecf045"

# la verificación del handoff F50c §3 y la tabla de fotos testigo de §A (nombres de ficha.personas)
ESPERADO = {"con_people": 73, "ancla": 35, "arrastre": 38, "ambiguas": 0, "con_quotes": 84, "grupos": 7}
TESTIGOS = {(1, 3): (["Daniel Écija (padre)"], "ancla"), (1, 4): (["Daniel Écija (padre)"], "arrastre"),
            (2, 1): (["Daniel Écija (padre)", "María Bernal"], "ancla"), (2, 8): (["Víctor Calvo"], "ancla"),
            (3, 7): (["Eric Saint"], "arrastre"), (3, 16): (["Jim McNulty"], "ancla"),
            (5, 9): (["Daniel Écija (hijo)"], "ancla"), (5, 14): (["Daniel Écija (padre)"], "ancla")}


class _Alto(Exception):
    pass


def _modulo_antes():
    src = subprocess.run(["git", "show", f"{COMMIT_ANTES}:script_engine/m03_expediente.py"], cwd=ROOT,
                         capture_output=True, check=True).stdout
    tmp = F50C / "_m03_expediente_antes.py"
    tmp.write_bytes(src)
    spec = importlib.util.spec_from_file_location("m03_expediente_antes", tmp)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    tmp.unlink()
    return mod


def _anclas(cap: dict) -> tuple[list[str], list]:
    if cap.get("image_prompts") is not None:
        its = cap["image_prompts"]
        return [it["narration_anchor"] for it in its], [it.get("beat") for it in its]
    its = [{"narration_anchor": cap["narration_anchor"], "beat": (cap.get("image_f8") or {}).get("beat")},
           *(cap.get("supplemental_image_prompts") or [])]
    return [it["narration_anchor"] for it in its], [it.get("beat") for it in its]


def preparar():
    import fase1_5
    from script_engine import m03_expediente as mexp
    from script_engine import m03_imagenes_v3 as v3img
    from script_engine import m03_visual as m03
    from script_engine.topics_db import get_topic_by_id
    narr = fase1_5._load_narration(TID)
    skel = fase1_5._load_skeleton(TID)
    topic = get_topic_by_id(TID)
    topic = {**topic, **m03._geo_era(TID, narr)}
    beats = v3img.load_beats(topic, m03.STEPS_DIR)
    narr_ch = narr["chapters"]
    topic["_f8"] = {"beats": beats, "year": v3img.topic_year(topic, beats), "lang": v3img.place_language(topic),
                    "fuentes": mexp.fuentes(TID, m03.STEPS_DIR),
                    "anio_prev": {n: mexp.anio_previo(narr_ch, n) for n in range(1, 8)}}
    return topic, skel, narr_ch


def pedido_y_expedientes(mod, topic, sch, narr, anchors, cap):
    """El pedido de casilleros de producción con el módulo de expediente `mod`, y sus expedientes."""
    from script_engine import m03_visual as m03
    visto, exps = {}, {}
    orig_m, orig_ll = m03.mexp, m03._llamar_casilleros

    class Espia:
        def __getattr__(self, k):
            return getattr(mod, k)

        def expedientes(self, *a, **k):
            exps["x"] = mod.expedientes(*a, **k)
            return exps["x"]

    def falsa(prompt, system_instruction=None, response_schema=None, description=None, **_):
        visto.update(system=system_instruction, user=prompt)
        raise _Alto()
    m03.mexp, m03._llamar_casilleros = Espia(), falsa
    try:
        m03._render_prompts_seedream(topic, sch, narr, {"anchors": [{"anchor": a} for a in anchors]}, cap)
    except _Alto:
        pass
    finally:
        m03.mexp, m03._llamar_casilleros = orig_m, orig_ll
    return f"=== SYSTEM ===\n{visto['system']}\n\n=== USER ===\n{visto['user']}\n", exps["x"]


def _fuera_de_las_tres(txt: str) -> list[str]:
    """El pedido sin las líneas PEOPLE, QUOTES y las de PEOPLE GROUPS."""
    out, en_grupos = [], False
    for ln in txt.splitlines(True):
        if ln.startswith("      PEOPLE (role · where · years):") or ln.startswith("      QUOTES:"):
            continue
        if ln.rstrip("\r\n") == "PEOPLE GROUPS:":
            en_grupos = True
            out.append(ln)
            continue
        if en_grupos and re.match(r"  - \S+: ", ln):
            continue
        en_grupos = False
        out.append(ln)
    return out


def main() -> int:
    from script_engine import m03_expediente as mexp
    from script_engine import m03_imagenes_v3 as v3img
    antes_mod = _modulo_antes()
    topic, skel, narr_ch = preparar()
    v = json.loads((ROOT / "data" / "scripts" / "_steps" / TID / "03_visual.json").read_text(encoding="utf-8"))
    (F50C / "pedidos" / "antes").mkdir(parents=True, exist_ok=True)
    filas, fallas, diffs, beats_distintos = [], [], [], []
    for cap in sorted(v["chapters"], key=lambda c: c["chapter_number"]):
        n = cap["chapter_number"]
        anchors, beats_guardados = _anclas(cap)
        sch = next(c for c in skel["chapters"] if c["chapter_number"] == n)
        narr = next(c for c in narr_ch if c["chapter_number"] == n)["narration"].strip()
        cap_beats = topic["_f8"]["beats"].get(n) or []
        asign = [a["beat"] for a in v3img.assign_beats(narr, anchors, cap_beats)] if cap_beats else []
        if asign != beats_guardados:
            beats_distintos.append((n, asign, beats_guardados))
        p_antes, e_antes = pedido_y_expedientes(antes_mod, topic, sch, narr, anchors, n)
        p_desp, e_desp = pedido_y_expedientes(mexp, topic, sch, narr, anchors, n)
        (F50C / "pedidos" / "antes" / f"pedido_ch{n:02d}.txt").write_text(p_antes, encoding="utf-8")
        (F50C / "pedidos" / f"pedido_ch{n:02d}.txt").write_text(p_desp, encoding="utf-8")
        d = list(difflib.unified_diff(_fuera_de_las_tres(p_antes), _fuera_de_las_tres(p_desp),
                                      f"antes ch{n:02d}", f"después ch{n:02d}"))
        if d:
            diffs.append((n, d))
        for ea, ed in zip(e_antes, e_desp):
            filas.append({"cap": n, "foto": ed["foto"], "ancla": ed["ancla"], "personas": ed["personas"],
                          "fuente": ed["personas_fuente"], "dudas": ed["personas_dudas"],
                          "people_antes": ea["people3"], "people": ed["people3"],
                          "quotes_antes": ea["citas"], "quotes": ed["citas"]})
    grupos = [ln for ln in (F50C / "pedidos" / "pedido_ch02.txt").read_text(encoding="utf-8").splitlines()
              if re.match(r"  - \S+: .* · APPEARANCE: .+ · CLOTHING: .+", ln)]
    grupos_ok = [g for g in grupos if " · APPEARANCE: - ·" not in g and not g.endswith("CLOTHING: -")]

    cuenta = {"con_people": sum(bool(f["people"]) for f in filas),
              "ancla": sum(f["fuente"] == "ancla" for f in filas),
              "arrastre": sum(f["fuente"] == "arrastre" for f in filas),
              "ambiguas": sum(bool(f["dudas"]) for f in filas),
              "con_quotes": sum(bool(f["quotes"]) for f in filas),
              "grupos": len(grupos_ok)}
    quotes_sin_autor = [(f["cap"], f["foto"], q) for f in filas for q in f["quotes"] if " — " not in q]
    reparto = Counter(min(len(f["personas"]), 3) for f in filas if f["personas"])
    for k, e in ESPERADO.items():
        if cuenta[k] != e:
            fallas.append(f"{k}: {cuenta[k]} (esperado {e})")
    if quotes_sin_autor:
        fallas.append(f"citas sin autor: {quotes_sin_autor[:5]}")
    por = {(f["cap"], f["foto"]): f for f in filas}
    testigos = []
    for k, (nombres, fuente) in TESTIGOS.items():
        f = por[k]
        ok = f["personas"] == nombres and f["fuente"] == fuente
        testigos.append((k, f["ancla"], f["personas"], f["fuente"], ok))
        if not ok:
            fallas.append(f"testigo {k[0]}/{k[1]}: {f['personas']} ({f['fuente']}), esperado {nombres} ({fuente})")
    for n, d in diffs:
        fallas.append(f"ch{n:02d}: el pedido cambia fuera de PEOPLE/QUOTES/PEOPLE GROUPS ({len(d)} líneas de diff)")

    L = ["# EXPEDIENTES_F50c — personas, citas y grupos en el pedido de foto (Wittenoom, en seco)", "",
         "Salida de `python lab/hyperframes/f50c/expedientes_f50c.py`. Los pedidos de casilleros de los 7 caps salen del "
         "código de producción con la llamada a Opus cortada antes de salir. «antes» es el expediente de F50b "
         f"(`{COMMIT_ANTES}`) y «después» el de F50c. Las anclas son las del papel de F50b. Cero modelos, cero fal.", "",
         "## Verificación automática", "", "| | resultado | esperado |", "|---|---:|---:|"]
    L += [f"| {k} | {cuenta[k]} | {ESPERADO[k]} |" for k in ESPERADO]
    L += [f"| fotos con PEOPLE antes | {sum(bool(f['people_antes']) for f in filas)} | 17 |",
          f"| 1 / 2 / 3 personas | {reparto[1]} / {reparto[2]} / {reparto[3]} | 48 / 23 / 2 |",
          f"| citas sin autor | {len(quotes_sin_autor)} | 0 |",
          f"| caps con diff fuera de PEOPLE/QUOTES/PEOPLE GROUPS | {len(diffs)} | 0 |", "",
          "**Fotos testigo**", "", "| foto | ancla | personas | fuente | ok |", "|---|---|---|---|---|"]
    L += [f"| {k[0]}/{k[1]} | «{a[:70]}» | {', '.join(p) or '—'} | {fu or '—'} | {'sí' if ok else 'NO'} |"
          for k, a, p, fu, ok in testigos]
    L += ["", f"**Beats:** `assign_beats` de producción "
          f"{'da los mismos beats que los guardados en los 7 caps' if not beats_distintos else 'difiere de lo guardado en ' + str([b[0] for b in beats_distintos])}.",
          "", f"**Resultado: {'PASA' if not fallas else 'FALLA — PARADA'}**", ""]
    L += [f"- {x}" for x in fallas]
    for n, d in diffs:
        L += ["", f"### diff ch{n:02d} fuera de las tres líneas", "", "```diff", *[x.rstrip("\n") for x in d[:200]], "```"]
    L += ["", "## PEOPLE GROUPS (después, igual en los 7 caps)", ""] + [f"- `{g.strip()}`" for g in grupos]
    L += ["", "## Por foto: PEOPLE y QUOTES, antes → después", ""]
    for f in filas:
        L += [f"### Cap {f['cap']} · foto {f['foto']}" + (f" — {f['fuente']}" if f["fuente"] else ""), "",
              f"- Ancla: «{f['ancla']}»",
              f"- PEOPLE antes: {'; '.join(f['people_antes']) or '-'}",
              f"- PEOPLE después: {'; '.join(f['people']) or '-'}"
              + (f" ({', '.join(f['personas'])})" if f["personas"] else ""),
              f"- QUOTES antes: {' | '.join('«' + q + '»' for q in f['quotes_antes']) or '-'}",
              f"- QUOTES después: {' | '.join(f['quotes']) or '-'}", ""]
    (F50C / "EXPEDIENTES_F50c.md").write_text("\n".join(L), encoding="utf-8")
    (F50C / "EXPEDIENTES_F50c.json").write_text(json.dumps(
        {"cuenta": cuenta, "esperado": ESPERADO, "reparto": dict(reparto), "fallas": fallas,
         "beats_distintos": beats_distintos, "testigos": [[f"{k[0]}/{k[1]}", p, fu, ok] for k, a, p, fu, ok in testigos],
         "grupos": grupos, "fotos": filas}, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"{cuenta} · reparto {dict(reparto)} · testigos {sum(t[4] for t in testigos)}/8 · diffs {len(diffs)} · "
          f"beats distintos {len(beats_distintos)} · {'PASA' if not fallas else 'FALLA: ' + ' | '.join(fallas)}")
    return 0 if not fallas else 1


if __name__ == "__main__":
    sys.exit(main())
