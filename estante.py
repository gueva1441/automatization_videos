"""estante.py — F77 (V6): tanda de semillas y estante de temas.

Omar lanza varias semillas a la vez («D · Tanda de semillas» en el form) y elige después cuál producir.

Tanda (`correr_tanda`):
  1. Cada título pasa por el mismo camino que el modo C (semilla manual con receta `remeasure` already_es=True) y el
     gate ES de la Etapa A (`fase1.measure_pick_es`, que no pregunta nada). Todos los títulos a la vez.
  2. SATURADO → queda en el estante con ⚠ y SIN research (no se gasta). VACIO/HUECO/DISPUTADO siguen; un gate que no
     pudo medir también sigue, con ⚠ (como el gate de siempre: «no se pudo verificar, conservo el pick»).
  3. Los que siguen corren `fase1_5 --semilla <registro> --topic <tid> --batch --hasta-ficha`, un subproceso por tema,
     todos a la vez: research v3 → compuerta del pool → ficha, y paran. Compuerta roja = queda con ⚠, sin ficha.

El registro de cada semilla de la tanda es `data/estante/<tid>.json` (la semilla + el resultado del gate): es la
entrada que `fase1_5 --semilla` necesita y lo único que la tanda escribe fuera de lo que ya escribe el research.

Estante (`listar`): se DEDUCE DEL DISCO, sin estado nuevo. Un tema está en el estante si NO tiene
`_steps/<tid>/01a_escaleta.json` y además: tiene `ficha_caso.json` (listo para elegir), o su registro de la tanda dice
SATURADO, o el research quedó con la compuerta del pool roja / sin ficha (⚠). `run_pipeline.etapa_de` devuelve
`estante` para los que tienen ficha. Elegir uno = `run_pipeline --topic <tid>` sigue desde la escaleta.
"""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import uuid
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

from config import DATA_DIR

ESTANTE_DIR = DATA_DIR / "estante"
STEPS_DIR = DATA_DIR / "scripts" / "_steps"
ROOT = Path(__file__).resolve().parent

# orden del gate en el estante (handoff F77 C4): VACIO/HUECO → DISPUTADO → SATURADO; sin medir, después
_ORDEN_GATE = {"VACIO": 0, "HUECO": 0, "DISPUTADO": 1, "SATURADO": 2}


def partir_titulos(texto: str) -> list[str]:
    """Títulos separados por «;» o salto de línea; sin vacíos ni repetidos (se queda el primero)."""
    vistos, out = set(), []
    for t in re.split(r"[;\n\r]+", texto or ""):
        t = t.strip()
        if t and t.lower() not in vistos:
            vistos.add(t.lower())
            out.append(t)
    return out


def semilla_manual(titulo: str) -> dict:
    """La semilla del modo C (niche_discoverer._run_manual) sin preguntar el nicho (la tanda no pregunta)."""
    import niche_discoverer as nd
    return nd._build_seed(titulo, "manual", None,
                          {"user_input": True, "entered_at": datetime.now().isoformat(), "tanda": True},
                          remeasure={"es_query": titulo, "entity": titulo, "already_es": True})


def _resumen_gate(m: dict) -> dict:
    """Lo que el estante muestra del gate (sin la tabla entera de candidatos)."""
    return {k: m.get(k) for k in ("status", "label", "saturation", "heaviest", "quota_units", "source")} | {
        "medido_at": datetime.now().isoformat()}


def medir(titulos: list[str], *, medir_fn=None) -> list[dict]:
    """Semilla + gate de cada título, todos a la vez (workers = títulos). Devuelve [{tid, titulo, seed, gate}]."""
    if medir_fn is None:
        from fase1 import measure_pick_es as medir_fn
    seeds = [semilla_manual(t) for t in titulos]

    def uno(seed: dict) -> dict:
        try:
            g = _resumen_gate(medir_fn(seed, n=3))
        except Exception as e:                       # el gate no tumba la tanda: queda sin medir, con ⚠
            g = {"status": "error", "label": None, "error": f"{type(e).__name__}: {e}"[:300],
                 "medido_at": datetime.now().isoformat()}
        seed.setdefault("evidence", {})["es_gap"] = {"label": g.get("label"), "heaviest": g.get("heaviest")}
        return {"tid": str(uuid.uuid4()), "titulo": seed["seed_title"], "seed": seed, "gate": g}

    with ThreadPoolExecutor(max_workers=max(1, len(seeds))) as ex:
        return list(ex.map(uno, seeds))


def _registro_path(tid: str) -> Path:
    return ESTANTE_DIR / f"{tid}.json"


def guardar_registro(rec: dict) -> Path:
    ESTANTE_DIR.mkdir(parents=True, exist_ok=True)
    p = _registro_path(rec["tid"])
    tmp = p.with_name(p.name + ".tmp")          # atómico: `listar` puede estar leyendo mientras la tanda reescribe
    tmp.write_text(json.dumps(rec, ensure_ascii=False, indent=1), encoding="utf-8")
    os.replace(tmp, p)
    return p


def sigue(rec: dict) -> bool:
    """SATURADO no se investiga (no se gasta); todo lo demás sigue."""
    return (rec.get("gate") or {}).get("label") != "SATURADO"


def comando_hasta_ficha(rec: dict, python: str | None = None) -> list[str]:
    return [python or sys.executable, str(ROOT / "fase1_5.py"), "--semilla", str(_registro_path(rec["tid"])),
            "--topic", rec["tid"], "--batch", "--hasta-ficha"]


def correr_tanda(titulos: list[str], *, log=print, medir_fn=None, popen=subprocess.Popen,
                 python: str | None = None) -> list[dict]:
    """La tanda entera: gate de todos a la vez → un subproceso `--hasta-ficha` por tema que sigue, todos a la vez.
    Cada subproceso escribe su log en `data/estante/<tid>.log`. Devuelve los registros con `rc` (None = no corrió)."""
    recs = medir(titulos, medir_fn=medir_fn)
    for r in recs:
        g = r["gate"]
        h = g.get("heaviest") or {}
        log(f"  [tanda] «{r['titulo']}» → {g.get('label') or 'sin medir'}"
            + (f" · más pesado: «{h.get('title')}» {h.get('views')} views, {h.get('months')} meses" if h else "")
            + f" · {g.get('quota_units') or 0} u API · tid {r['tid']}")
        r["rc"] = None
        guardar_registro(r)
    procs = []
    for r in recs:
        if not sigue(r):
            log(f"  [tanda] ⚠ «{r['titulo']}» SATURADO: queda en el estante sin research")
            continue
        out = open(ESTANTE_DIR / f"{r['tid']}.log", "w", encoding="utf-8")
        cmd = comando_hasta_ficha(r, python)
        log(f"  [tanda] ▶ «{r['titulo']}»: research + ficha (log: data/estante/{r['tid']}.log)")
        procs.append((r, popen(cmd, cwd=str(ROOT), stdout=out, stderr=subprocess.STDOUT,
                               env={**_env(), "PYTHONIOENCODING": "utf-8"}), out))
    for r, p, out in procs:
        r["rc"] = p.wait()
        out.close()
        guardar_registro(r)
        log(f"  [tanda] {'✓' if r['rc'] == 0 else '⚠'} «{r['titulo']}» terminó (exit {r['rc']})")
    return recs


def _env() -> dict:
    import os
    e = dict(os.environ)
    e.pop("QA_FORM", None)                      # los subprocesos no hablan con el form (no hay preguntas)
    return e


# ═══════════════════════════════ estante: leído del disco ═══════════════════════════════
def _json(p: Path):
    try:
        return json.loads(p.read_text(encoding="utf-8"))
    except Exception:
        return None


def _usd(tid: str) -> float:
    c = _json(STEPS_DIR / tid / "01_v3_costos.json") or {}
    return round(sum(float(x.get("usd") or 0) for x in c.get("_corridas") or []), 4)


def _pool(tid: str) -> dict | None:
    pool = _json(STEPS_DIR / tid / "00_pool_v3.json")
    if not pool:
        return None
    from researcher_steps import pool_gate as pg
    try:
        ev = pg.evaluate(pool)
    except Exception:
        ev = {"metricas": pg.measure(pool), "color": None}
    return {**ev["metricas"], "compuerta": ev.get("color")}


def _compuerta_md(tid: str) -> str | None:
    f = STEPS_DIR / tid / "POOL_GATE.md"
    if not f.exists():
        return None
    t = f.read_text(encoding="utf-8")
    for c in ("ROJO", "AMARILLO", "VERDE"):
        if f"**🔴 {c}" in t or f"**🟡 {c}" in t or f"**🟢 {c}" in t:
            return c.lower()
    return None


def _ficha(tid: str) -> dict | None:
    f = _json(STEPS_DIR / tid / "ficha_caso.json")
    if not f:
        return None
    esc = f.get("escenas") or []
    return {"titulo": f.get("titulo"), "hechos": len(f.get("hechos") or []), "escenas": len(esc),
            "personas": len(f.get("personas") or []),
            "primeras": [str(e.get("que_pasa") or e.get("donde") or "").strip() for e in esc[:3]]}


def item(tid: str, rec: dict | None = None) -> dict | None:
    """Un tema del estante, o None si ya siguió a la escaleta (o no es del estante)."""
    d = STEPS_DIR / tid
    if (d / "01a_escaleta.json").exists():
        return None
    rec = rec if rec is not None else _json(_registro_path(tid))
    ficha = _ficha(tid)
    pool = _pool(tid)
    compuerta = (pool or {}).get("compuerta") or _compuerta_md(tid)
    gate = (rec or {}).get("gate") or {}
    titulo = (rec or {}).get("titulo") or (ficha or {}).get("titulo") or tid
    avisos = []
    if gate.get("label") == "SATURADO":
        avisos.append("SATURADO: sin research")
    elif rec is not None and not gate.get("label"):
        avisos.append("gate sin medir")
    if not ficha:
        if compuerta == "rojo":
            avisos.append("compuerta del pool ROJA: sin ficha")
        elif gate.get("label") != "SATURADO":
            if rec is None and not d.exists():
                return None
            rc = (rec or {}).get("rc")
            avisos.append("sin ficha" + (f" (exit {rc}; ver data/estante/{tid}.log)" if rc not in (None, 0) else
                                         " (corriendo o sin correr)" if rc is None else ""))
    if rec is None and not ficha:
        return None                             # un topic viejo sin ficha no es del estante
    return {"tid": tid, "titulo": titulo, "gate": gate, "pool": pool, "compuerta": compuerta, "ficha": ficha,
            "usd": _usd(tid) if d.exists() else 0.0, "avisos": avisos, "elegible": bool(ficha)}


def listar() -> list[dict]:
    """Todos los temas del estante, ordenados (C4)."""
    tids: dict[str, dict | None] = {}
    if ESTANTE_DIR.exists():
        for p in ESTANTE_DIR.glob("*.json"):
            rec = _json(p)
            if isinstance(rec, dict) and rec.get("tid"):
                tids[rec["tid"]] = rec
    if STEPS_DIR.exists():
        for d in STEPS_DIR.iterdir():
            if d.is_dir() and d.name not in tids and (d / "ficha_caso.json").exists():
                tids[d.name] = None
    items = [i for i in (item(t, r) for t, r in tids.items()) if i]
    return ordenar(items)


def ordenar(items: list[dict]) -> list[dict]:
    """VACIO/HUECO → DISPUTADO → SATURADO (sin medir después); dentro, más `elegibles_humano` primero; ⚠ al final."""
    def clave(i):
        lab = (i.get("gate") or {}).get("label")
        return (bool(i["avisos"]), _ORDEN_GATE.get(lab, 3), -((i.get("pool") or {}).get("elegibles_humano") or 0),
                i["titulo"].lower())
    return sorted(items, key=clave)


def _c(x) -> str:
    return str(x if x is not None else "—").replace("|", "/").replace("\n", " ")


def body(items: list[dict]) -> str:
    """La tabla del menú «E · Estante (N)», tal cual la ve Omar."""
    if not items:
        return "El estante está vacío."
    L = ["| # | título | gate | pool | ficha | US$ |", "|---|---|---|---|---|---|"]
    for n, i in enumerate(items, 1):
        g = i.get("gate") or {}
        h = g.get("heaviest") or {}
        gate = _c(g.get("label") or "sin medir")
        if h:
            vistas = f"{int(h.get('views') or 0):,}".replace(",", ".")
            gate += f" · «{_c(h.get('title'))[:60]}» {vistas} views, {h.get('months')} meses"
        p = i.get("pool")
        pool = (f"{p['datos']} datos · {p['citas_verificadas']} citas · {p['personas_con_nombre']} personas · "
                f"{p['eventos_con_fecha']} eventos · {p['elegibles_humano']} humanos · {_c(i.get('compuerta'))}"
                if p else ("compuerta " + _c(i["compuerta"]) if i.get("compuerta") else "—"))
        f = i.get("ficha")
        ficha = (f"«{_c(f['titulo'])}» · {f['hechos']} hechos · {f['escenas']} escenas · {f['personas']} personas · "
                 + " / ".join(_c(e)[:70] for e in f["primeras"]) if f else "—")
        aviso = (" ⚠ " + "; ".join(i["avisos"])) if i["avisos"] else ""
        L.append(f"| {n} | {_c(i['titulo'])}{aviso} | {gate} | {pool} | {ficha} | {i['usd']:.2f} |")
    return "\n".join(L)


def elegibles(items: list[dict]) -> list[dict]:
    return [i for i in items if i["elegible"]]
