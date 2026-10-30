# -*- coding: utf-8 -*-
"""F58 Parte B — corrida real en Wittenoom: el comando del handoff tal cual
(`python -m script_engine.m09_packaging 123bbb64-9fca-4395-8bf4-57d60e219ef1 --candidates`, vía `main()` con ese argv)
envuelto en `cost_tracker.start_video/end_video` para desglosar el gasto. Después, solo lectura: arma SALIDA_B.md
(los 3 paquetes enteros con el texto de cada dato_id y los avisos; los 3 prompts enteros; nombres de
`documented_people` y de `ficha.personas` en los prompts, palabra entera; descripción y tags; gasto por servicio),
`hoja_paquetes.jpg` (las 3 compuestas lado a lado, ffmpeg hstack) y `parte_b.json`.
Uso: python lab/hyperframes/f58/parte_b.py
"""
import json
import re
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
F58 = Path(__file__).resolve().parent
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
COMANDO = ["python", "-m", "script_engine.m09_packaging", TID, "--candidates"]


def _formas_persona(persona: dict) -> list[str]:
    from script_engine.m03_expediente import _formas
    return _formas(persona)


def nombres_en(texto: str, formas: dict[str, str]) -> list[dict]:
    """Cada forma (palabra entera, sin distinguir mayúsculas) que aparece en el texto, con la frase donde está."""
    hits = []
    for forma, quien in formas.items():
        m = re.search(r"(?<![\w])" + re.escape(forma) + r"(?![\w])", texto, flags=re.IGNORECASE)
        if m:
            a, b = texto.rfind(".", 0, m.start()) + 1, texto.find(".", m.end())
            hits.append({"forma": forma, "persona": quien, "frase": texto[a:(b + 1 if b >= 0 else len(texto))].strip()})
    return hits


def main() -> int:
    from cost_tracker import cost_tracker
    from script_engine import m09_packaging as m09
    import fase1_5
    from researcher_steps import ficha_caso as fc

    t0 = time.time()
    res: dict = {"comando": " ".join(COMANDO), "error": None}
    cost_tracker.start_video("f58_parte_b")
    try:
        sys.argv = ["script_engine.m09_packaging", *COMANDO[3:]]   # como `python -m script_engine.m09_packaging <tid> --candidates`
        m09.main()
    except BaseException as e:          # noqa: BLE001 — PARADA/SystemExit se reportan tal cual
        res["error"] = f"{type(e).__name__}: {e}"[:1500]
    finally:
        rep = cost_tracker.end_video()
    res["segundos_reloj"] = round(time.time() - t0, 1)
    res["cost_tracker"] = [{"servicio": x.service, "descripcion": x.description, "usd": round(x.total_cost, 5)}
                           for x in (rep.entries if rep else [])]
    res["usd_total"] = round(rep.total_cost, 4) if rep else None

    # ── solo lectura desde acá ──
    meta = m09._leer_meta(TID)
    paquetes = [p for p in meta.get("paquetes", []) if isinstance(p, dict)]
    res["paquetes"] = paquetes
    res["descripcion"], res["tags"] = meta.get("descripcion"), meta.get("tags")

    topic = fase1_5._load_topic_by_id(TID)
    ficha = fc.load(TID, fase1_5.STEPS_DIR)
    formas: dict[str, str] = {}
    for per in ficha.get("personas") or []:
        for f in _formas_persona(per):
            formas.setdefault(f, f"ficha: {per.get('nombre')}")
    for dp in topic.get("documented_people") or []:
        if isinstance(dp, dict) and dp.get("name"):
            formas.setdefault(str(dp["name"]).strip(), f"documented_people: {dp['name']}")
    res["formas_buscadas"] = len(formas)
    for p in paquetes:
        p["nombres_en_prompt"] = nombres_en(p.get("prompt") or "", formas)

    cand = m09._candidates_dir(TID)
    fotos = [cand / p["miniatura"] for p in paquetes if p.get("miniatura") and (cand / p["miniatura"]).exists()]
    hoja = F58 / "hoja_paquetes.jpg"
    if fotos:
        ins = [a for f in fotos for a in ("-i", str(f))]
        fil = "".join(f"[{i}:v]scale=640:-2[v{i}];" for i in range(len(fotos))) + \
              "".join(f"[v{i}]" for i in range(len(fotos))) + f"hstack=inputs={len(fotos)}"
        if len(fotos) == 1:
            fil = "[0:v]scale=640:-2"
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", fil, "-frames:v", "1", str(hoja)],
                       check=True)
        res["hoja"] = str(hoja.relative_to(ROOT))
    (F58 / "parte_b.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")

    # ── SALIDA_B.md ──
    L = ["# F58 — Salida B (Wittenoom real)", "",
         f"Comando: `{res['comando']}` (vía `main()` con ese argv, dentro de `cost_tracker.start_video('f58_parte_b')`). "
         f"{res['segundos_reloj']} s de reloj. Topic `{TID}`.", ""]
    if res["error"]:
        L += [f"**Error:** {res['error']}", ""]
    L += ["## 1. Los 3 paquetes", ""]
    for p in paquetes:
        L += [f"### Paquete {p['n']:02d} — {p.get('estrategia')}", "",
              f"- **Título** ({len(p.get('titulo') or '')} caracteres): {p.get('titulo')}",
              f"- **Texto**: «{p.get('texto')}»",
              f"- **Ancla** (oración literal del gancho): «{p.get('ancla')}»",
              f"- **cap_que_paga**: {p.get('cap_que_paga')}",
              f"- **dato_ids**:"]
        for i, txt in (p.get("datos") or {}).items():
            L.append(f"  - `{i}`: {txt}")
        L += [f"- **Avisos**: {' · '.join(p.get('avisos') or []) or 'ninguno'}",
              f"- **Foto**: {p.get('foto') or 'SIN FOTO'}" + (f" · motivo: {p.get('motivo_sin_foto')}" if p.get("motivo_sin_foto") else "")
              + f" · año {p.get('anio')} ({p.get('anio_fuente')})",
              f"- **Compuesta**: {p.get('miniatura')} · base {p.get('base')}", ""]
        for k in ("_f8_problemas", "_f8_texto_fuera"):
            if p.get(k):
                L += [f"- `{k}`: {json.dumps(p[k], ensure_ascii=False)}", ""]
    L += ["## 2. Los 3 prompts de foto (enteros)", ""]
    for p in paquetes:
        L += [f"### Paquete {p['n']:02d}", "", "**prompt (el que fue a Seedream):**", "", f"    {p.get('prompt')}", "",
              "**raw_llm_prompt (casillero de Opus):**", "", f"    {p.get('raw_llm_prompt')}", ""]
    L += ["## 3. Nombres de `documented_people` / `ficha.personas` en los prompts (medida, no freno)", "",
          f"Formas buscadas: {res['formas_buscadas']} (nombre y variantes de las {len(ficha.get('personas') or [])} personas de la ficha, "
          f"sin paréntesis; `name` de los {len(topic.get('documented_people') or [])} `documented_people` del canon), palabra entera, sin distinguir mayúsculas.", ""]
    algun = False
    for p in paquetes:
        for h in p["nombres_en_prompt"]:
            algun = True
            L.append(f"- paquete {p['n']:02d}: «{h['forma']}» ({h['persona']}) — «{h['frase']}»")
    if not algun:
        L.append("Ningún prompt nombra a nadie.")
    L += ["", "## 4. Hoja", "", f"`{res.get('hoja', '(sin hoja: ninguna compuesta)')}` — las {len(fotos)} miniaturas compuestas lado a lado "
          f"(compuestas en `output/{TID}/publish/thumb_candidates/`; no van a git).", "",
          "## 5. Descripción y tags", "", f"**Descripción** ({len(res['descripcion'] or '')} caracteres):", "",
          *(("    " + ln) for ln in (res["descripcion"] or "").splitlines()), "",
          f"**Tags** ({len(res['tags'] or [])}): {', '.join(res['tags'] or [])}", "",
          "## 6. Gasto (cost_tracker, video `f58_parte_b`)", "", "| servicio | descripción | US$ |", "|---|---|---|"]
    L += [f"| {x['servicio']} | {x['descripcion']} | {x['usd']} |" for x in res["cost_tracker"]]
    por = {}
    for x in res["cost_tracker"]:
        d = x["descripcion"] or ""
        k = "m09:paquetes" if "m09:paquetes" in d else "casilleros" if "casilleros" in d else "canon" if "canon" in d.lower() \
            else "fotos" if x["servicio"].lower().startswith(("seedream", "fal", "flux")) else f"otro ({x['servicio']})"
        por[k] = round(por.get(k, 0) + x["usd"], 5)
    L += ["", "Por rubro: " + " · ".join(f"**{k}** US$ {v}" for k, v in por.items()),
          f"", f"**Total US$ {res['usd_total']}**.", "",
          "`asegurar_canon`: " + ("llamó a Flash (ver fila canon)" if "canon" in por else
                                  "no llamó a Flash (la marca `canon_ficha_md5` del topic coincidía con la ficha)."), "",
          "## 7. Archivos", "", f"- `output/{TID}/publish/metadata.json` (paquetes, descripción, tags) y `thumb_candidates/paquete_NN*.png` (no van a git)",
          "- `lab/hyperframes/f58/hoja_paquetes.jpg`, `parte_b.json` (todo), `parte_b.log` (stdout de la corrida)"]
    (F58 / "SALIDA_B.md").write_text("\n".join(L), encoding="utf-8", newline="\n")
    print("\n".join(L[-14:]))
    return 1 if res["error"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
