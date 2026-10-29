# -*- coding: utf-8 -*-
"""F51c etapa 3 — re-armado EN SECO de las 96 fotos de Wittenoom: antes (el rearmado de F51a: año guardado + borrado de
nombres viejo) contra después (código nuevo de 57f6aaf: sin borrado + año recalculado con `anio_final` sin el paso 1),
y los cortes Veo de los caps 1 y 7 (viejo en el carácter contra `_carve_veo_zones` nuevo).

- Antes: `armar(slots, it["anio"], grupos)` → `scrub_documented_names` VIEJO (código de `a4a784e`, cargado con
  `git show` y exec en memoria) → `f8_backstop` nuevo (el resto del backstop no cambió) → `_sacar_frases_con_texto`.
- Después: año = `anio_final(e, slots)` nuevo, con el expediente `e` reconstruido como `_render_prompts_seedream`
  (anclas y beat guardados en el 03_visual.json) → `armar` → `f8_backstop` nuevo → `_sacar_frases_con_texto`.
- `grupos` = `people_groups` del topic vivo (canon F51b) en los dos lados.
- Verificación: con el `anio_final` VIEJO (de `a4a784e`) el expediente reconstruido tiene que dar el `anio` guardado.

Sin modelos, sin fal. No escribe 03_visual.json, ni el canon, ni topics_db: solo REARMADO_F51c.md.

Uso:
  PYTHONIOENCODING=utf-8 python lab/hyperframes/f51c/rearmar_todo.py
"""
import ast
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "lab" / "hyperframes" / "f50g"))
F51C = Path(__file__).resolve().parent
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
SALIDA = F51C / "REARMADO_F51c.md"
VIEJO = "a4a784e"
ESPERADAS = [(6, 3), (7, 11), (3, 16)]


def git_show(ruta: str) -> str:
    return subprocess.run(["git", "show", f"{VIEJO}:{ruta}"], cwd=ROOT, capture_output=True, check=True,
                          encoding="utf-8").stdout


def cargar_viejo():
    """scrub_documented_names (el módulo name_matching entero) y anio_final, tal cual estaban en a4a784e."""
    ns_nm = {"__name__": "name_matching_a4a784e"}
    exec(compile(git_show("script_engine/name_matching.py"), "name_matching@a4a784e", "exec"), ns_nm)
    src = git_show("script_engine/m03_imagenes_v3.py")
    fn = next(n for n in ast.parse(src).body if isinstance(n, ast.FunctionDef) and n.name == "anio_final")
    ns_af = {"re": re}
    exec(compile(ast.Module(body=[fn], type_ignores=[]), "m03_imagenes_v3@a4a784e", "exec"), ns_af)
    return ns_nm["scrub_documented_names"], ns_af["anio_final"]


def cf(k) -> str:
    return f"{k[0]}/{k[1]}"


def corta(s: str) -> str:
    return "«" + s.replace("\n", " ") + "»"


def main() -> int:
    import rearmar as rg
    from script_engine import m03_imagenes_v3 as v3
    from script_engine import m03_expediente as mexp
    from script_engine import m03_visual as mv
    from script_engine.topics_db import get_topic_by_id
    scrub_viejo, anio_final_viejo = cargar_viejo()

    v = json.loads(rg.VISUAL.read_text(encoding="utf-8"))           # solo lectura
    narr = json.loads((rg.STEPS / TID / "01b_narration.json").read_text(encoding="utf-8"))
    narr_chapters = narr.get("chapters") or []
    sync = json.loads((ROOT / "output" / "audio" / TID / "sync_map.json").read_text(encoding="utf-8"))
    topic = get_topic_by_id(TID)
    beats = v3.load_beats(topic, rg.STEPS)
    year_topic = v3.topic_year(topic, beats)
    fu = mexp.fuentes(TID, rg.STEPS)
    grupos = {g["id"]: g for g in topic.get("people_groups") or [] if isinstance(g, dict) and g.get("id")}
    documented = topic.get("documented_people")

    filas, sin_armar = [], []
    for cap in v["chapters"]:
        n = cap["chapter_number"]
        cap_beats = beats.get(n) or []
        by_n = {b["n"]: b for b in cap_beats}
        fts = rg.fotos(cap)
        anclas = [(cap.get("narration_anchor") if rol == "veo0" else it.get("narration_anchor")) or "" for it, rol in fts]
        assign = [{"beat": it.get("beat"), "cerrada": bool(it.get("cerrada"))} for it, _ in fts]
        exps = mexp.expedientes(topic, fu, cap_beats, anclas, assign, mexp.anio_previo(narr_chapters, n), year_topic)
        for i, ((it, rol), e) in enumerate(zip(fts, exps), start=1):
            k = (n, i)
            if not it.get("raw_llm_prompt"):
                sin_armar.append({"k": k, "rol": rol})
                continue
            slots = json.loads(it["raw_llm_prompt"])
            escala = bool((by_n.get(it.get("beat")) or {}).get("escala"))
            tii = slots.get("text_in_image") or {}
            cartel = (tii.get("text") or "") if tii.get("present") else ""
            # antes (F51a): año guardado + borrado viejo
            a_antes = v3.armar(slots, it["anio"], grupos)
            p_scrub, _ = scrub_viejo(a_antes["prompt"], documented)
            borro = p_scrub != a_antes["prompt"]
            antes, _ = v3.f8_backstop(p_scrub, slots, escala)
            antes, _ = mv._sacar_frases_con_texto(antes, cartel)
            # verificación: anio_final viejo sobre el expediente reconstruido = anio guardado
            av, fv = anio_final_viejo(e, slots)
            # después: código nuevo
            anio_n, fuente_n = v3.anio_final(e, slots)
            a_desp = v3.armar(slots, anio_n, grupos)
            desp, _ = v3.f8_backstop(a_desp["prompt"], slots, escala)
            desp, _ = mv._sacar_frases_con_texto(desp, cartel)
            pg = [g for g in slots.get("people_group") or [] if isinstance(g, str)]
            filas.append({"k": k, "rol": rol, "antes": antes, "despues": desp, "borro": borro,
                          "anio_g": it.get("anio"), "fuente_g": it.get("anio_fuente"), "anio_v": av, "fuente_v": fv,
                          "anio_n": anio_n, "fuente_n": fuente_n, "year": slots.get("year"),
                          "anio_ancla": e.get("anio_ancla"), "pg": pg,
                          "pg_faltan": [g for g in pg if g not in grupos],
                          "asp_a": a_antes["partes"]["aspecto"], "asp_d": a_desp["partes"]["aspecto"],
                          "ancla": e["ancla"]})

    total = len(filas) + len(sin_armar)
    coinc = [f for f in filas if str(f["anio_v"]) == str(f["anio_g"])]
    coinc_f = [f for f in filas if str(f["anio_v"]) == str(f["anio_g"]) and f["fuente_v"] == f["fuente_g"]]
    no_coinc = [f for f in filas if str(f["anio_v"]) != str(f["anio_g"])]
    cambian = [f for f in filas if f["despues"] != f["antes"]]
    borradas = [f for f in filas if f["borro"]]
    anio_cambia = [f for f in filas if str(f["anio_n"]) != str(f["anio_g"])]
    por_k = {f["k"]: f for f in filas}

    def motivo(f) -> str:
        m = []
        if f["borro"]:
            m.append("a (el borrado de nombres cambiaba el prompt)")
        if str(f["anio_n"]) != str(f["anio_g"]):
            m.append(f"c (año {f['anio_g']} → {f['anio_n']})")
        return " + ".join(m) or "OTRO (ni a ni c) — revisar"

    falt = [f for f in filas if f["pg_faltan"]]
    ids_falt = sorted({g for f in falt for g in f["pg_faltan"]})
    sin_asp_a = sum(1 for f in filas if f["pg"] and not f["asp_a"])
    sin_asp_d = sum(1 for f in filas if f["pg"] and not f["asp_d"])
    asp_igual = sum(1 for f in filas if f["asp_a"] == f["asp_d"])

    L = ["# REARMADO_F51c — Wittenoom re-armado en seco: antes (F51a) contra después (código F51c)", "",
         "Salida de `PYTHONIOENCODING=utf-8 python lab/hyperframes/f51c/rearmar_todo.py`. Cero llamadas a modelos, "
         "cero fal; no se escribe `03_visual.json`, ni el canon, ni topics_db.", "",
         "- **Antes** = el rearmado de F51a: casilleros (`raw_llm_prompt`) + el `anio` guardado de cada foto → "
         "`armar` → `scrub_documented_names` **viejo** (código de `a4a784e`, cargado con `git show` y ejecutado en "
         "memoria) con `topic[\"documented_people\"]` → `f8_backstop` nuevo (el resto del backstop no cambió) → "
         "`_sacar_frases_con_texto`.",
         "- **Después** = el código de `57f6aaf`: año = `anio_final(e, slots)` nuevo (sin el paso 1 «dicho en el "
         "ancla») → `armar` → `f8_backstop` (sin borrado) → `_sacar_frases_con_texto`.",
         "- El expediente `e` se reconstruye como `m03_visual._render_prompts_seedream`: `mexp.expedientes(topic, "
         "mexp.fuentes(TID), cap_beats, anclas, assign, mexp.anio_previo(01b_narration.chapters, n), topic_year)`, "
         "con las anclas (`narration_anchor`; la de la foto Veo, la del capítulo) y el `beat` guardados en el "
         "03_visual.json. Nada se recalcula con LLM.",
         "- `grupos` = `people_groups` del topic **vivo** (canon F51b) en los dos lados, así la única diferencia entre "
         "antes y después son los arreglos a (borrado de nombres) y c (año). Por eso «antes» no es el texto literal "
         "de REARMADO_F51a.md (que usó el canon previo a F51b), sino el rearmado de F51a con el canon de hoy.", "",
         "## Verificación del año (expediente reconstruido + `anio_final` viejo)", "",
         f"- Fotos: {total} · pasan por `armar`: {len(filas)} · sin `raw_llm_prompt`: {len(sin_armar)}"
         + (" (" + ", ".join(cf(s["k"]) + " " + s["rol"] for s in sin_armar) + ")" if sin_armar else ""),
         f"- `anio_final` viejo sobre el expediente reconstruido = `anio` guardado: **{len(coinc)}/{len(filas)}**"
         + (" · no coinciden: " + ", ".join(f"{cf(f['k'])} (guardado {f['anio_g']}, reconstruido {f['anio_v']})"
                                           for f in no_coinc) if no_coinc else ""),
         f"- Además con la misma fuente (`anio_fuente`): {len(coinc_f)}/{len(filas)}", ""]
    dif_f = [f for f in filas if str(f["anio_v"]) == str(f["anio_g"]) and f["fuente_v"] != f["fuente_g"]]
    if dif_f:
        L += ["Mismo año, otra fuente:", ""] + [f"- {cf(f['k'])}: guardado «{f['fuente_g']}», reconstruido "
                                                 f"«{f['fuente_v']}»" for f in dif_f] + [""]

    L += ["## Qué cambia (después ≠ antes)", "",
          f"- Cambian: **{len(cambian)}/{len(filas)}**",
          f"- El borrado viejo cambiaba el prompt (arreglo a): {', '.join(cf(f['k']) for f in borradas) or 'ninguna'}",
          f"- El año cambia (arreglo c): " + (", ".join(f"{cf(f['k'])} ({f['anio_g']} → {f['anio_n']})"
                                                      for f in anio_cambia) or "ninguna"), "",
          "| foto | rol | motivo |", "|---|---|---|"]
    L += [f"| {cf(f['k'])} | {f['rol']} | {motivo(f)} |" for f in cambian]
    L += [""]
    for k in ESPERADAS:
        f = por_k.get(k)
        if f is None:
            L += [f"- {cf(k)}: no pasa por `armar`."]
        else:
            L += [f"- {cf(k)}: {'cambia' if f in cambian else 'NO cambia'}"
                  + (f" — {motivo(f)}" if f in cambian else "")
                  + f" · «Court» en antes: {'sí' if 'Court' in f['antes'] else 'no'}, en después: "
                    f"{'sí' if 'Court' in f['despues'] else 'no'}"]
    otras = [f for f in cambian if f["k"] not in ESPERADAS]
    L += [f"- Otros cambios fuera de 6/3, 7/11 y 3/16: "
          + (", ".join(f"{cf(f['k'])} ({motivo(f)})" for f in otras) or "ninguno"), ""]

    L += ["## Prompts enteros", ""]
    for k in ESPERADAS:
        f = por_k.get(k)
        if f is None:
            continue
        L += [f"### {cf(k)} ({f['rol']})", "",
              f"- Ancla: {corta(f['ancla'])}",
              f"- Casillero `year` de Opus: {f['year']!r} · año dicho en el ancla (`anio_ancla`): {f['anio_ancla']!r}",
              f"- Año antes: **{f['anio_g']}** — {f['fuente_g']} (guardado)",
              f"- Año después: **{f['anio_n']}** — {f['fuente_n']}", "",
              "**Antes**", "", "```", f["antes"], "```", "", "**Después**", "", "```", f["despues"], "```", ""]

    # ── cortes Veo ──
    L += ["## Cortes Veo (caps 1 y 7)", "",
          "Narración = `01b_narration.json` capítulo `narration`.strip(); `veo_zone_chars = max(1, min(int(8.0 × "
          "len / duration_sec), len − 1))` con `duration_sec` de `output/audio/<TID>/sync_map.json`. Corte viejo = en "
          "el carácter; corte nuevo = `m03_visual._carve_veo_zones`. **Solo son los cortes:** las anclas que eligió "
          "Opus dentro de cada zona no se recalculan sin LLM.", ""]
    print_veo = []
    for n, pos in ((1, "start"), (7, "end")):
        t = (next(c for c in narr_chapters if c["chapter_number"] == n).get("narration") or "").strip()
        dur = float(next(c for c in sync["chapters"] if c.get("id") == f"ch{n:02d}")["duration_sec"])
        vzc = max(1, min(int(mv.VEO_CLIP_DURATION_SEC * len(t) / dur), len(t) - 1))
        viejo = vzc if pos == "start" else len(t) - vzc
        vlo, vhi, slo, shi = mv._carve_veo_zones(t, pos, vzc)
        nuevo = vhi if pos == "start" else vlo
        delta = nuevo - viejo
        cps = len(t) / dur
        L += [f"### Cap {n} (posición {pos})", "",
              f"- len {len(t)} · duración {dur:.2f} s · {cps:.2f} car/s · `veo_zone_chars` {vzc}",
              f"- Corte viejo en el carácter {viejo} · nuevo en {nuevo} · Δ {delta:+d} caracteres ≈ {delta / cps:+.2f} s",
              f"- Zona Veo nueva [{vlo}, {vhi}) · fotos de apoyo [{slo}, {shi})", ""]
        if pos == "start":
            L += ["| | últimos 40 de la zona Veo | primeros 40 de las fotos de apoyo |", "|---|---|---|",
                  f"| viejo | {corta(t[max(0, viejo - 40):viejo])} | {corta(t[viejo:viejo + 40])} |",
                  f"| nuevo | {corta(t[max(0, vhi - 40):vhi])} | {corta(t[slo:slo + 40])} |", ""]
        else:
            L += ["| | últimos 40 de las fotos de apoyo | primeros 40 de la zona Veo |", "|---|---|---|",
                  f"| viejo | {corta(t[max(0, viejo - 40):viejo])} | {corta(t[viejo:viejo + 40])} |",
                  f"| nuevo | {corta(t[max(0, shi - 40):shi])} | {corta(t[vlo:vlo + 40])} |", ""]
        print_veo.append(f"cap {n} {pos}: viejo {viejo} → nuevo {nuevo} (Δ {delta:+d}) · "
                         f"zona Veo termina/empieza en {corta(t[max(0, vhi - 20):vhi]) if pos == 'start' else corta(t[vlo:vlo + 20])}")

    L += ["## Nota: ids de `people_group` fuera del canon vivo", "",
          f"- Fotos con algún id de `people_group` que no existe en el canon vivo: **{len(falt)}** (iguales en antes y "
          f"después: los dos lados usan el mismo `grupos`). Ids: {', '.join(ids_falt) or 'ninguno'}.",
          f"- Fotos con `people_group` y sin aspecto pegado: antes {sin_asp_a}, después {sin_asp_d}; texto del aspecto "
          f"igual antes/después en {asp_igual}/{len(filas)}.",
          "- Es lo esperado (F51b abierto 2): esos ids no pegan aspecto en este rearmado; se arregla en F51d al correr "
          "m03 de nuevo.", "",
          "## Por foto", "", "| foto | rol | año guardado | año después | fuente después | borrado viejo | cambia |",
          "|---|---|---|---|---|---|---|"]
    L += [f"| {cf(f['k'])} | {f['rol']} | {f['anio_g']} | {f['anio_n']} | {f['fuente_n']} | "
          f"{'sí' if f['borro'] else 'no'} | {'sí' if f in cambian else 'no'} |" for f in filas]
    SALIDA.write_text("\n".join(L) + "\n", encoding="utf-8")

    print(f"fotos {total} · por armar {len(filas)} · sin armar {len(sin_armar)} {[cf(s['k']) for s in sin_armar]}")
    print(f"año reconstruido (anio_final viejo) = guardado: {len(coinc)}/{len(filas)} · misma fuente "
          f"{len(coinc_f)}/{len(filas)}" + (f" · no coinciden {[cf(f['k']) for f in no_coinc]}" if no_coinc else ""))
    print(f"cambian {len(cambian)}/{len(filas)}: " + ", ".join(f"{cf(f['k'])} [{motivo(f)}]" for f in cambian))
    print(f"borrado viejo cambiaba: {[cf(f['k']) for f in borradas]} · año cambia: "
          f"{[(cf(f['k']), f['anio_g'], f['anio_n']) for f in anio_cambia]}")
    print(f"ids fuera del canon: {len(falt)} fotos · {ids_falt}")
    for s in print_veo:
        print(s)
    print(f"escrito {SALIDA.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
