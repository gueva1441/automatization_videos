# -*- coding: utf-8 -*-
"""F50e-A — el canon de Wittenoom con 3 modelos (Flash, claude-sonnet-5-5, claude-opus-5-5), 3 corridas cada uno, el
MISMO pedido (`step_4e.canon_desde_ficha`: `pedido_canon` + `VISUAL_CANON_SCHEMA_FICHA`) y la medida 4a–4f por código.
Producción no se toca: nada va a topics_db ni a 05_visual_canon.json.

Transporte (no texto): `step_4e.call_flash_json` se reemplaza en este proceso por un ruteador por hilo.
- flash  → `gemini_helpers.call_flash_json` (el de hoy), con la descripción de la corrida;
- sonnet / opus → `claude_helpers.call_json(prompt, model=…, response_schema=<el mismo esquema>, effort="high")`.
  El esquema de Gemini se pasa como dict (`model_dump`) y sin la marca `nullable` (no es JSON Schema): mismos campos y
  tipos, ninguno obligatorio.
El ruteador guarda el md5 del pedido de cada intento y el error si la llamada falla (`extract_visual_canon` devuelve un
canon vacío sin avisar: acá un canon vacío o sin `periods` es FALLA y no se mide).

Tope US$ 1,00 (`lab/TOPE_TANDA.json`): tanda 1 = 7 a la vez (flash ×3, sonnet ×3, opus 1); las opus 2 y 3 corren
solo si lo gastado + 2 × (costo de opus 1) ≤ tope; si no, PARADA.
Uso: python -u lab/hyperframes/f50e/canon_modelos.py
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "lab" / "hyperframes" / "f50c"))
F50E = Path(__file__).resolve().parent
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
MODELOS = {"flash": None, "sonnet": "claude-sonnet-5-5", "opus": "claude-opus-5-5"}   # Omar 2026-10-28 23:04
EFFORT = "high"                       # Opus: guion_v4.ESFUERZO; Sonnet: el de F47b (k7)
_TL = threading.local()
_REG: dict[str, dict] = {}


def _md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def _sin_nullable(x):
    if isinstance(x, dict):
        return {k: _sin_nullable(v) for k, v in x.items() if k != "nullable"}
    if isinstance(x, list):
        return [_sin_nullable(v) for v in x]
    return x


def ruteador(prompt, system_instruction=None, response_schema=None, thinking_budget=None, description=None):
    import claude_helpers
    import gemini_helpers
    clave = _TL.clave
    r = _REG[clave]
    r["intentos"].append({"md5_pedido": _md5(prompt), "con_esquema": response_schema is not None})
    desc = f"f50e canon {clave} (intento {len(r['intentos'])})"
    try:
        if _TL.modelo == "flash":
            return gemini_helpers.call_flash_json(prompt, system_instruction=system_instruction,
                                                  response_schema=response_schema, description=desc)
        esquema = (_sin_nullable(response_schema.model_dump(mode="json", exclude_none=True))
                   if response_schema is not None else None)
        return claude_helpers.call_json(prompt, model=MODELOS[_TL.modelo], system_instruction=system_instruction,
                                        response_schema=esquema, effort=EFFORT, description=desc)
    except Exception as e:  # noqa: BLE001 — se guarda y se re-lanza (extract_visual_canon lo traga)
        r["errores"].append(f"{type(e).__name__}: {str(e)[:500]}")
        raise


def una(modelo: str, n: int, topic: dict, ficha: dict) -> None:
    from researcher_steps import step_4e_visual_canon as s4e
    clave = f"{modelo}_{n}"
    _TL.clave, _TL.modelo = clave, modelo
    _REG[clave] = {"intentos": [], "errores": []}
    t0 = time.time()
    canon = s4e.canon_desde_ficha(topic, ficha)
    _REG[clave]["segundos"] = round(time.time() - t0, 1)
    _REG[clave]["canon"] = canon
    (F50E / f"canon_{clave}.json").write_text(json.dumps(canon, ensure_ascii=False, indent=1), encoding="utf-8")


def fotos_con_anio() -> list[dict]:
    """[(cap, foto, año)] de las 96 fotos de 03_visual.json: año = anio_ancla o respaldo[0] (el cálculo de m03)."""
    import expedientes_f50c as ex
    from script_engine import m03_expediente as mexp
    topic, skel, narr_ch = ex.preparar()
    v = json.loads((ROOT / "data" / "scripts" / "_steps" / TID / "03_visual.json").read_text(encoding="utf-8"))
    out = []
    for cap in sorted(v["chapters"], key=lambda c: c["chapter_number"]):
        n = cap["chapter_number"]
        anchors, _ = ex._anclas(cap)
        sch = next(c for c in skel["chapters"] if c["chapter_number"] == n)
        narr = next(c for c in narr_ch if c["chapter_number"] == n)["narration"].strip()
        _, exps = ex.pedido_y_expedientes(mexp, topic, sch, narr, anchors, n)
        for e in exps:
            a = str(e.get("anio_ancla") or (e.get("respaldo") or ("",))[0] or "")
            out.append({"cap": n, "foto": e["foto"], "anio": int(a) if re.fullmatch(r"\d{4}", a) else None})
    return out


def medir(canon: dict, fotos: list[dict]) -> dict:
    from script_engine import m03_visual as m3
    periods = [p for p in (canon.get("era_visual_canon") or {}).get("periods") or [] if isinstance(p, dict)]
    tramos = [(p.get("years"), m3._tramo(p.get("years"))) for p in periods]
    ilegibles = [y for y, t in tramos if t is None]
    por_cap, sin = {}, []
    for f in fotos:
        c = por_cap.setdefault(f["cap"], {"con_anio": 0, "cubiertas": 0})
        if f["anio"] is None:
            continue
        c["con_anio"] += 1
        if any(t and t[0] <= f["anio"] <= t[1] for _, t in tramos):
            c["cubiertas"] += 1
        else:
            cerca = [p.get("years") for p in m3._periods_del_cap(periods, [str(f["anio"])])]
            sin.append({"cap": f["cap"], "foto": f["foto"], "anio": f["anio"], "le_daria": cerca})
    grupos = []
    for g in canon.get("people_groups") or []:
        ropa = [(t.get("years"), m3._tramo(t.get("years"))) for t in g.get("clothing_by_period") or []
                if isinstance(t, dict)]
        ilegibles += [y for y, t in ropa if t is None]
        anios = sorted({int(y) for y in re.findall(r"\b(1[89]\d\d|20\d\d)\b", str(g.get("where_when") or ""))})
        sin_ropa = [a for a in anios if not any(t and t[0] <= a <= t[1] for _, t in ropa)]
        grupos.append({"id": g.get("id"), "where_when": g.get("where_when"), "anios": anios,
                       "ropa": [y for y, _ in ropa], "anios_sin_ropa": sin_ropa})
    return {"periods": [y for y, _ in tramos], "por_cap": por_cap,
            "con_anio": sum(c["con_anio"] for c in por_cap.values()),
            "cubiertas": sum(c["cubiertas"] for c in por_cap.values()), "sin_period": sin, "grupos": grupos,
            "grupos_con_anios_sin_ropa": sum(bool(g["anios_sin_ropa"]) for g in grupos), "ilegibles": ilegibles}


def main() -> int:
    import fase1_5
    from cost_tracker import cost_tracker
    from researcher_steps import ficha_caso as fc
    from researcher_steps import step_4e_visual_canon as s4e
    from script_engine.topics_db import get_topic_by_id
    tope = float(json.loads((ROOT / "lab" / "TOPE_TANDA.json").read_text(encoding="utf-8"))["usd"])
    topic = get_topic_by_id(TID)
    ficha = fc.load(TID, fase1_5.STEPS_DIR)
    md5_pedido = _md5(s4e.pedido_canon(topic, ficha))
    db_antes = hashlib.md5((ROOT / "data" / "topics_db.json").read_bytes()).hexdigest()
    canon_antes = hashlib.md5((fase1_5.STEPS_DIR / TID / "05_visual_canon.json").read_bytes()).hexdigest()
    fotos = fotos_con_anio()
    s4e.call_flash_json = ruteador
    cost_tracker.start_video("f50e-canon-modelos")
    parada = None
    try:
        tanda1 = [("flash", 1), ("flash", 2), ("flash", 3), ("sonnet", 1), ("sonnet", 2), ("sonnet", 3), ("opus", 1)]
        with ThreadPoolExecutor(max_workers=len(tanda1)) as ex_:
            list(ex_.map(lambda mn: una(*mn, topic, ficha), tanda1))
        gastado = sum(e.total_cost for e in cost_tracker.current_video.entries)
        opus1 = sum(e.total_cost for e in cost_tracker.current_video.entries if "canon opus_1" in e.description)
        print(f"tanda 1: US$ {gastado:.4f} (opus 1: {opus1:.4f})", flush=True)
        if gastado + 2 * opus1 <= tope:
            with ThreadPoolExecutor(max_workers=2) as ex_:
                list(ex_.map(lambda mn: una(*mn, topic, ficha), [("opus", 2), ("opus", 3)]))
        else:
            parada = (f"tope: gastado {gastado:.4f} + 2 × opus 1 {opus1:.4f} = {gastado + 2 * opus1:.4f} > {tope}: "
                      "opus 2 y 3 no corren")
    finally:
        rep = cost_tracker.end_video()
    entradas = [e for e in rep.entries] if rep else []
    for clave, r in _REG.items():
        es = [e for e in entradas if f"canon {clave} " in e.description]
        r["usd"] = round(sum(e.total_cost for e in es), 4)
        r["tokens_in"] = sum(int(getattr(e, "tokens_in", 0) or 0) for e in es)
        r["tokens_out"] = sum(int(getattr(e, "tokens_out", 0) or 0) for e in es)
        r["tokens_thinking"] = sum(int(getattr(e, "tokens_thinking", 0) or 0) for e in es)
        c = r.get("canon") or {}
        periods = (c.get("era_visual_canon") or {}).get("periods")
        if not c.get("people_groups") and not periods:
            r["falla"] = "canon vacío" + (f" · {r['errores'][-1]}" if r["errores"] else "")
        elif not periods:
            r["falla"] = "canon sin periods" + (f" · {r['errores'][-1]}" if r["errores"] else "")
        else:
            r["medida"] = medir(c, fotos)
        r.pop("canon", None)
    db_despues = hashlib.md5((ROOT / "data" / "topics_db.json").read_bytes()).hexdigest()
    canon_despues = hashlib.md5((fase1_5.STEPS_DIR / TID / "05_visual_canon.json").read_bytes()).hexdigest()
    salida = {"md5_pedido": md5_pedido, "parada": parada, "total_usd": round(getattr(rep, "total_cost", 0) or 0, 4),
              "produccion_intacta": {"topics_db": db_antes == db_despues, "05_visual_canon": canon_antes == canon_despues},
              "fotos_con_anio": sum(f["anio"] is not None for f in fotos), "fotos": len(fotos), "corridas": _REG}
    (F50E / "CANON_MODELOS.json").write_text(json.dumps(salida, ensure_ascii=False, indent=1, default=str),
                                             encoding="utf-8")
    print(json.dumps({k: salida[k] for k in ("md5_pedido", "parada", "total_usd", "produccion_intacta")}), flush=True)
    for k, r in _REG.items():
        m = r.get("medida") or {}
        print(k, r.get("falla") or f"{m.get('cubiertas')}/{m.get('con_anio')} · {m.get('periods')} · "
              f"grupos {len(m.get('grupos') or [])}", r["usd"], r.get("segundos"),
              sorted({i["md5_pedido"][:8] for i in r["intentos"]}), flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
