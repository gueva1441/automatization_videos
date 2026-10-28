"""F47b — ¿Qué modelo llena mejor los casilleros de foto? E = Opus 5.5 y F = Sonnet 5.5 (effort high, el mismo de D)
contra C2 (Pro) y D (Fable) de F47, en texto, caps 2, 5, 6, 7 de Wittenoom. Cero fotos, cero fal.

Reusa `f47_corridas` importado: `cargar`, `ruteador` (por hilo; mismo system, user-prompt, esquema, validación y el mismo
ajuste de transporte array → {"image_prompts": …} que D), `una_variante`, `armar_c2`, `chequeos` (los 8 de F47), freno.
Solo cambia el modelo (`f47.MODELOS`). C2 y D se leen de `PROMPTS_F47.json` (no se re-corren). Chequeos 9 y 10 nuevos
(handoff F47b): año del setting distinto del de la foto y negaciones en el setting.

    python lab/hyperframes/f47/f47b_corridas.py prompts     → slots_E/F_chNN.json, pedidos/, PROMPTS_F47b.md, COSTOS_F47b.md
    python lab/hyperframes/f47/f47b_corridas.py seco <dir>  → lo mismo en <dir>, sin API
"""
from __future__ import annotations

import json
import re
import sys
import tempfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

LAB = Path(__file__).resolve().parent
sys.path.insert(0, str(LAB))
import f47_corridas as f47  # noqa: E402

f46, f46b = f47.f46, f47.f46b
f47.LAB_ID = "f47b-lab"
f47.TOPE_USD = 4.00                                   # Omar, al pegar el prompt de F47b (lab/TOPE_TANDA.json)
CAPS = (2, 5, 6, 7)                                   # handoff F47b §Constantes (los mismos de D en F47)
f47.MODELOS.update({"E": "claude-opus-5-5", "F": "claude-sonnet-5-5"})   # handoff F47b §Constantes (Omar 03:19)
VARS = ("C2", "D", "E", "F")
_w, _j = f47._w, f47._j


# ─────────────────────────── chequeos 9 y 10 (handoff F47b) ───────────────────────────
def anios_setting(setting: str, anio: str) -> list[str]:
    """Años de 4 cifras y décadas («1980s») del setting crudo que no son el año de la foto."""
    out = []
    for m in re.finditer(r"\b(1[89]\d\d|20\d\d)(s)?\b", setting or ""):
        y, dec = m.group(1), m.group(2)
        if dec:
            if not (int(y) <= int(anio) <= int(y) + 9):
                out.append(m.group(0))
        elif y != anio:
            out.append(y)
    return out


def negaciones(setting: str) -> list[str]:
    """Frases «no + palabra» del setting crudo, enteras (el tramo entre comas que las trae)."""
    return [t.strip() for t in re.split(r"[,;.]", setting or "") if re.search(r"\bno\s+\w", t, re.I)]


# ─────────────────────────── corrida ───────────────────────────
def prompts(seco_dir: Path | None) -> None:
    from cost_tracker import cost_tracker
    from script_engine import m03_visual as m03
    if seco_dir:
        f47._SECO, f47.LAB = True, seco_dir
    out_dir = f47.LAB
    canon = {k: v for k, v in _j(f47.CANON_C).items() if k != "facts_de_la_ficha"}
    datos: dict[int, dict] = {}
    for cap in CAPS:                                         # secuencial: f46b.anios lee f46b.CAP
        d = f47.cargar(cap)
        f46b.CAP = cap
        exps = f46b.expedientes(d, canon, f46b.anios(d))
        datos[cap] = {"d": d, "exps": exps,
                      "topic_c": {**d["topic"], **{k: canon[k] for k in f46.CANON_KEYS if k in canon}}}
    f46b.CAP = 0
    f46b.LAB = Path(tempfile.mkdtemp(prefix="f47b_"))       # f46b.slots escribe ahí su prompt_slots_pro.txt
    f47._PREVIO = f47.gastado_previo()
    if not seco_dir:
        cost_tracker.start_video(f47.LAB_ID)
    f47._PRO_ORIG, m03.call_pro_json = m03.call_pro_json, f47.ruteador
    trabajos = [(v, c) for v in ("E", "F") for c in CAPS]
    res: dict[tuple[str, int], dict] = {}
    try:
        with ThreadPoolExecutor(max_workers=len(trabajos)) as ex:      # las 8 llamadas en paralelo
            futs = {ex.submit(f47.una_variante, v, c, datos[c]["d"], datos[c]["topic_c"], datos[c]["exps"], canon):
                    (v, c) for v, c in trabajos}
            for f in as_completed(futs):
                try:
                    res[futs[f]] = f.result()
                except f47.Parada as e:
                    res[futs[f]] = {"var": futs[f][0], "cap": futs[f][1], "estado": f"PARADA: {e}"}
    finally:
        m03.call_pro_json = f47._PRO_ORIG
        if not seco_dir:
            cost_tracker.end_video()
    var: dict[tuple[str, int], list[dict]] = {}
    for (v, c), r in res.items():
        if r.get("estado") == "ok":
            var[(v, c)] = f47.armar_c2(r["items"], datos[c]["exps"], datos[c]["d"], canon,
                                       datos[c]["topic_c"].get("documented_people"))
    f47j = _j(LAB / "PROMPTS_F47.json")
    for v in ("C2", "D"):
        for c in CAPS:
            var[(v, c)] = f47j[f"{v}_ch{c:02d}"]
    _w(out_dir / "PROMPTS_F47b.json", {f"{v}_ch{c:02d}": x for (v, c), x in var.items() if v in ("E", "F")})
    escribir(out_dir, datos, canon, var, res)
    print(f"  F47b: US$ {f47.gastado_previo():.4f} en cost_history ({f47.LAB_ID})", flush=True)


# ─────────────────────────── salidas ───────────────────────────
def _historia(vid: str) -> list[dict]:
    from cost_tracker import cost_tracker
    try:
        h = json.loads(cost_tracker.HISTORY_FILE.read_text(encoding="utf-8"))
    except UnicodeDecodeError:
        h = json.loads(cost_tracker.HISTORY_FILE.read_text(encoding="cp1252"))
    return [e for r in h if isinstance(r, dict) and r.get("video_id") == vid for e in r.get("entries", [])]


def _costos(out_dir: Path) -> dict[tuple[str, int], dict]:
    """Por variante y cap: estado, intentos, segundos (de los crudos), tokens y US$ (de cost_history)."""
    ent = _historia("f47-lab") + _historia("f47b-lab")
    out = {}
    for v in VARS:
        for c in CAPS:
            src = out_dir if v in ("E", "F") else LAB
            p = src / f"slots_{v}_ch{c:02d}.json"
            r = _j(p) if p.exists() else {}
            es = [e for e in ent if re.match(rf"f47 {v} ch{c:02d} slots", str(e.get("description") or ""))]
            out[(v, c)] = {"estado": (r.get("estado") or ("F46b (no se re-corrió)" if (v, c) == ("C2", 2) else "—")),
                           "intentos": len(r.get("pedidos") or []),
                           "seg": round(sum(x.get("segundos") or 0 for x in r.get("crudos") or []), 1),
                           "tin": sum(int(e.get("tokens_in") or 0) for e in es),
                           "tout": sum(int(e.get("tokens_out") or 0) for e in es),
                           "usd": sum(float(e.get("total_cost") or 0) for e in es)}
    return out


def escribir(out_dir: Path, datos: dict, canon: dict, var: dict, res: dict) -> None:
    from script_engine import m03_imagenes_v3 as v3img
    sn = lambda b: "sí" if b else "no"  # noqa: E731
    L = ["# F47b — Prompts E (Opus 5.5) y F (Sonnet 5.5) contra C2 (Pro) y D (Fable) — salida de la parte única", "",
         "Mismo pedido que D en F47; solo cambia el modelo (effort high en D, E y F). C2 y D se leen de "
         "`PROMPTS_F47.json` (sus prompts enteros están en `PROMPTS_F47.md`); el C2 del cap 2 es el de F46b.", "",
         "## Pedido igual al de D (md5 del archivo `pedidos/pedido_X_chNN.txt`, system + user del 1.er intento)", "",
         "| cap | D | E | F | E = D | F = D |", "|---|---|---|---|---|---|"]
    import hashlib

    def md5f(p: Path) -> str:
        return hashlib.md5(p.read_bytes()).hexdigest() if p.exists() else "—"
    for c in CAPS:
        m = {v: md5f((LAB if v == "D" else out_dir) / "pedidos" / f"pedido_{v}_ch{c:02d}.txt") for v in ("D", "E", "F")}
        L.append(f"| {c} | {m['D'][:8]} | {m['E'][:8]} | {m['F'][:8]} | {sn(m['E'] == m['D'])} | {sn(m['F'] == m['D'])} |")
    L += ["", "md5 de system / user / esquema por intento (los guarda el ruteador):", "",
          "| variante | cap | estado | intentos | md5 system / user / esquema (1.er intento) |", "|---|---|---|---|---|"]
    for (v, c), r in sorted(res.items(), key=lambda kv: (kv[0][1], kv[0][0])):
        p0 = (r.get("pedidos") or [{}])[0]
        L.append(f"| {v} | {c} | {r.get('estado', '')[:300]} | {len(r.get('pedidos') or [])} | "
                 f"{p0.get('md5_system', '—')[:8]} / {p0.get('md5_user', '—')[:8]} / {p0.get('md5_schema', '—')[:8]} |")
    # prompts por foto
    for cap in CAPS:
        d, exps = datos[cap]["d"], datos[cap]["exps"]
        L += ["", f"# Cap {cap}" + (" (Veo: fotos suplementarias)" if d["veo"] else ""), ""]
        for k, e in enumerate(exps):
            gs = " | ".join((", ".join(var[(v, cap)][k]["people_group"]) or "[]") if (v, cap) in var else "—"
                            for v in VARS)
            L += [f"## Cap {cap} · foto {e['foto']} · beat {e['beat']}", "", f"- ancla: «{e['ancla']}»",
                  f"- año: {e['anio']} ({e['anio_fuente']})", f"- grupos C2 | D | E | F: {gs}",
                  "- palabras C2 | D | E | F: " + " | ".join(str(len(var[(v, cap)][k]["prompt"].split()))
                                                            if (v, cap) in var else "—" for v in VARS), ""]
            for v in ("E", "F"):
                x = var.get((v, cap))
                L += ([f"**{v}** ({len(x[k]['prompt'].split())} palabras):", "", "> " + x[k]["prompt"], ""] if x else
                      [f"**{v}**: — (la llamada no devolvió casilleros; ver la tabla de estado)", ""])
    # tabla de los 10 chequeos
    L += ["", "## Tabla de los 10 chequeos (por foto; C2 \\| D \\| E \\| F)", "",
          "1 año (fuente) · 2 año dentro de `spans` · 3 lugar del DÓNDE en la prosa · 4 gente sin grupo · "
          "5 nombres reales en el ancla → en la prosa · 6 `text_in_image` · 7 notas F8 · 8 palabras · "
          "9 años/décadas del `setting` crudo distintos del de la foto · 10 negaciones «no + palabra» en el `setting` crudo",
          "", "| cap · foto | 1 año | 2 canon | 3 lugar | 4 sin grupo | 5 nombres ancla → prosa | 6 texto | 7 F8 | "
          "8 palabras | 9 año del setting ≠ | 10 negaciones |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    keys = ("lugar", "sin", "nom", "txt", "f8", "pal", "anio9", "neg", "n")
    gran = {v: dict.fromkeys(keys, 0) for v in VARS}
    for cap in CAPS:
        d, exps = datos[cap]["d"], datos[cap]["exps"]
        lang = v3img.place_language(d["topic"])
        tot = {v: dict.fromkeys(keys, 0) for v in VARS}
        fuera = 0
        for k, e in enumerate(exps):
            ch = {}
            for v in VARS:
                xs = var.get((v, cap))
                if not xs:
                    continue
                q = f47.chequeos(xs[k], e, canon, d["topic"], lang)
                st = str((xs[k].get("slots") or {}).get("setting") or "")
                q["anio9"], q["neg"] = anios_setting(st, e["anio"]), negaciones(st)
                ch[v] = q
                for t in (tot[v], gran[v]):
                    t["n"] += 1
                    t["lugar"] += bool(q["lugar"])
                    t["sin"] += q["gente_sin_grupo"]
                    t["nom"] += bool(q["nombres_prosa"])
                    t["txt"] += q["texto"] != "no"
                    t["f8"] += bool(q["f8"])
                    t["pal"] += q["palabras"]
                    t["anio9"] += bool(q["anio9"])
                    t["neg"] += bool(q["neg"])
            q0 = next(iter(ch.values()))
            fuera += q0["en_canon"] != "sí"

            def col(f):
                return " \\| ".join(f(ch[v]).replace("|", "/") if v in ch else "—" for v in VARS)
            L.append(
                f"| {cap} · {e['foto']} | {q0['anio']} | {q0['en_canon']} | {col(lambda q: ', '.join(q['lugar']) or 'no')} | "
                f"{col(lambda q: sn(q['gente_sin_grupo']))} | {', '.join(q0['nombres_ancla']) or '—'} → "
                f"{col(lambda q: ', '.join(q['nombres_prosa']) or 'no')} | {col(lambda q: q['texto'])} | "
                f"{col(lambda q: '; '.join(q['f8']) or '—')} | {col(lambda q: str(q['palabras']))} | "
                f"{col(lambda q: ', '.join(q['anio9']) or '—')} | {col(lambda q: '; '.join(q['neg']) or '—')} |")

        def tc(t, f):
            return " \\| ".join(f(t[v]) if t[v]["n"] else "—" for v in VARS)
        L.append(f"| **cap {cap} total** ({len(exps)} fotos) | — | **{fuera} fuera** | **{tc(tot, lambda t: str(t['lugar']))}** | "
                 f"**{tc(tot, lambda t: str(t['sin']))}** | **{tc(tot, lambda t: str(t['nom']))} con nombre** | "
                 f"**{tc(tot, lambda t: str(t['txt']))}** | **{tc(tot, lambda t: str(t['f8']))}** | "
                 f"**{tc(tot, lambda t: str(round(t['pal'] / t['n'])) + ' prom.')}** | "
                 f"**{tc(tot, lambda t: str(t['anio9']))}** | **{tc(tot, lambda t: str(t['neg']))}** |")
    L += ["", "## Totales por variante (los 4 caps, 60 fotos)", "",
          "| variante | fotos | 3 lugar en la prosa | 4 gente sin grupo | 5 con nombre en la prosa | 6 texto | 7 F8 | "
          "8 palabras prom. | 9 año del setting ≠ | 10 negaciones |", "|---|---|---|---|---|---|---|---|---|---|"]
    for v in VARS:
        t = gran[v]
        if t["n"]:
            L.append(f"| {v} | {t['n']} | {t['lugar']} | {t['sin']} | {t['nom']} | {t['txt']} | {t['f8']} | "
                     f"{round(t['pal'] / t['n'])} | {t['anio9']} | {t['neg']} |")
    # costos por cap y variante
    cs = _costos(out_dir)
    L += ["", "## Costos, tokens y tiempo por cap y variante (cost_history `f47-lab` para C2 y D, `f47b-lab` para E y F)", "",
          "| variante | cap | estado | intentos | segundos | tokens in / out | US$ |", "|---|---|---|---|---|---|---:|"]
    sub = defaultdict(float)
    for v in VARS:
        for c in CAPS:
            x = cs[(v, c)]
            sub[v] += x["usd"]
            L.append(f"| {v} | {c} | {x['estado'][:120]} | {x['intentos']} | {x['seg']} | {x['tin']} / {x['tout']} | "
                     f"{x['usd']:.4f} |")
    L += ["", "| variante | US$ (caps medidos) |", "|---|---:|"] + [f"| {v} | {sub[v]:.4f} |" for v in VARS]
    L += ["", "C2 del cap 2 es el de F46b (`f46b-lab`, US$ 0,1178 la llamada de slots); no entra en la suma de C2."]
    (out_dir / "PROMPTS_F47b.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    ent = _historia("f47b-lab")
    C = [f"# F47b — costos reales (`data/cost_history.json`, video_id f47b-lab)", "",
         "| servicio | descripción | tokens in / out | costo US$ |", "|---|---|---|---:|"]
    C += [f"| {e.get('service')} | {e.get('description')} | {e.get('tokens_in')} / {e.get('tokens_out')} | "
          f"{float(e.get('total_cost') or 0):.4f} |" for e in ent]
    C.append(f"\n**Total**: US$ {sum(float(e.get('total_cost') or 0) for e in ent):.4f} (tope {f47.TOPE_USD:.2f})")
    (out_dir / "COSTOS_F47b.md").write_text("\n".join(C) + "\n", encoding="utf-8")
    print("  PROMPTS_F47b.md listo", flush=True)


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    que = sys.argv[1] if len(sys.argv) > 1 else ""
    if que not in ("prompts", "seco"):
        print(__doc__)
        return 2
    seco = Path(sys.argv[2]) if que == "seco" else None
    if seco:
        seco.mkdir(parents=True, exist_ok=True)
    try:
        prompts(seco)
    except f47.Parada as e:
        print(f"⛔ PARADA: {e}")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
