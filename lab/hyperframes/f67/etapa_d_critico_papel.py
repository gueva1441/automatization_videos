# -*- coding: utf-8 -*-
"""
lab/hyperframes/f67/etapa_d_critico_papel.py — F67 Etapa D: el crítico de pantalla sobre el papel de Wittenoom en disco (m01e-7, sin aprobar).
Lab, no cableado, no frena. Solo lee de _steps; escribe en lab/hyperframes/f67/d/. Copia de etapa_a_critico.py: body → hx._post, costo
hx.cost_of, hx._track sin start_video (no escribe data/cost_history.json). SYSTEM_D y FORMATO_D se extraen de la copia del handoff.
Nombres reales del papel, usados tal cual (F67 §5 D lo pide): el «dato» de la ficha es `texto`; el «ancla» son `palabra`, `oracion` y
`sentence_idx`; `aporta` vive dentro de la ficha y acá va al nivel del beat, como dice el handoff; `autor` solo existe en las citas.
    python lab/hyperframes/f67/etapa_d_critico_papel.py
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import time
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[3]
AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(AQUI))

import steps_md5  # noqa: E402

TID, STEPS = steps_md5.TID, steps_md5.STEPS
HANDOFF = AQUI / "HANDOFF_F67_compuerta_narracion.md"
HANDOFF_MD5 = "dd4c977e99047c42c6d19a154e4286de"
MODELO, EFFORT = "claude-opus-5-5", "medium"       # F67 §2: 1 corrida, Opus medium
NUM = re.compile(r"\d+(?:[.,]\d+)*")


def md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def bloques() -> tuple[str, str]:
    raw = HANDOFF.read_bytes()
    if hashlib.md5(raw).hexdigest() != HANDOFF_MD5:
        raise SystemExit(f"PARÁ: md5 del handoff {hashlib.md5(raw).hexdigest()} ≠ {HANDOFF_MD5}")
    t = raw.decode("utf-8").replace("\r\n", "\n")

    def bloque(titulo: str) -> str:
        i = t.index("```\n", t.index(titulo)) + 4
        return t[i:t.index("\n```", i)]
    return bloque("SYSTEM_D (completo"), bloque("FORMATO_D (va al final")


def armar_user(papel: dict, formato: str, pool: dict) -> tuple[str, dict]:
    from script_engine import m01e_pantalla as mp
    from script_engine.clima import vocabulario_clima
    carga = mp.cargar(TID, STEPS.parent, pool)
    e = mp._para_modelo(mp.entrada(carga, vocabulario_clima()))
    caps = [{**c, "oraciones": [{k: v for k, v in s.items() if k != "caben"} for s in c["oraciones"]]} for c in e["caps"]]
    def ficha(f: dict | None) -> dict | None:
        return None if not f else {"etiqueta": f.get("etiqueta"), "texto": f.get("texto"), "autor": f.get("autor"), "respaldo": f.get("respaldo"),
                                   "palabra": f.get("palabra"), "oracion": f.get("oracion"), "sentence_idx": f.get("sentence_idx")}
    beats = [{"cap": b["cap"], "beat": b["beat"], "funcion": b.get("funcion"), "pico": b.get("pico"), "ficha": ficha(b.get("ficha")), "sello": b.get("sello"),
              "aporta": (b.get("ficha") or {}).get("aporta")} for b in papel["beats"]]
    payload = {"caps": caps, "escaleta_video": e["escaleta_video"],
               "papel": {"beats": beats, "relojes": papel.get("relojes") or [],
                         "descartados": [{k: d.get(k) for k in ("pool_id", "motivo", "quien")} for d in papel.get("descartados") or []]},
               "archivo": [{k: x.get(k) for k in ("id", "texto", "fuente", "fecha", "contexto_fuente")} for x in e["archivo"]]}
    return json.dumps(payload, ensure_ascii=False, indent=None) + "\n\nFormato de salida (devolvé solo este JSON):\n" + formato, payload


def leer_json(txt: str) -> dict | None:
    t = (txt or "").strip()
    f = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", t, re.S)
    try:
        r = json.loads(f.group(1) if f else t)
    except json.JSONDecodeError:
        return None
    return r if isinstance(r, dict) else None


def llamar(system: str, user: str, d: Path) -> dict:
    import claude_helpers as hx
    body = {"model": MODELO, "max_tokens": hx.MAX_TOKENS, "system": system, "messages": [{"role": "user", "content": user}], "output_config": {"effort": EFFORT}}
    out: dict[str, Any] = {"modelo": MODELO, "effort": EFFORT, "system_md5": md5(system), "user_md5": md5(user), "intentos": [], "respuesta": None, "usage": None, "usd": 0.0, "segundos": 0.0}
    for k in range(2):
        t0 = time.time()
        try:
            r = hx._post(body)
        except Exception as e:  # noqa: BLE001
            out["intentos"].append({"error": f"{type(e).__name__}: {e}"})
            out["segundos"] = round(out["segundos"] + time.time() - t0, 1)
            continue
        out["segundos"] = round(out["segundos"] + time.time() - t0, 1)
        u = r.get("usage") or {}
        usd = round(hx.cost_of(MODELO, u), 5)
        hx._track(r.get("model") or MODELO, u, "lab_f67d")
        txt = "".join(c.get("text") or "" for c in r.get("content") or [] if c.get("type") == "text")
        resp = leer_json(txt)
        out["intentos"].append({"texto": txt, "json": resp is not None, "usage": u, "stop": r.get("stop_reason"), "usd": usd})
        out["usd"] = round(out["usd"] + usd, 5)
        if resp is not None:
            out["respuesta"], out["usage"] = resp, u
            break
    (d / "D_1.raw.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8", newline="\n")
    return out


def numeros(t: Any) -> set[str]:
    return {re.sub(r"[.,]", "", x) for x in NUM.findall(str(t or ""))}


def validar(resp: dict, payload: dict, papel: dict) -> list[dict]:
    """§5 D: ids de `que_pondria`/`huecos` existen y no están ya en el papel; cada (cap, beat) existe; cifras de cada `texto` propuesto ⊂
    texto/contexto_fuente/fecha de su id. Se reporta, no falla."""
    arch = {x["id"]: x for x in payload["archivo"]}
    en_papel = {(b.get("ficha") or {}).get("pool_id") for b in papel["beats"]} - {None}
    pares = {(b["cap"], b["beat"]) for b in papel["beats"]}
    filas = []

    def fila(tipo: str, cap: Any, beat: Any, i: Any, texto: Any) -> dict:
        x = arch.get(i) or {}
        ok = numeros(x.get("texto")) | numeros(x.get("contexto_fuente")) | numeros(x.get("fecha"))
        return {"tipo": tipo, "cap": cap, "beat": beat, "id": i, "beat_existe": (cap, beat) in pares, "id_existe": i is None or i in arch,
                "ya_en_papel": i in en_papel, "cifras_sin_respaldo": sorted(c for c in numeros(texto) if c not in ok) if i else []}
    for b in resp.get("beats") or []:
        q = b.get("que_pondria")
        if q:
            filas.append(fila("que_pondria", b.get("cap"), b.get("beat"), q.get("id"), q.get("texto")))
        else:
            filas.append({"tipo": "beat", "cap": b.get("cap"), "beat": b.get("beat"), "id": None, "beat_existe": (b.get("cap"), b.get("beat")) in pares,
                          "id_existe": True, "ya_en_papel": False, "cifras_sin_respaldo": []})
    for h in resp.get("huecos") or []:
        filas.append(fila("hueco", h.get("cap"), h.get("beat"), h.get("id"), h.get("texto")))
    return filas


def d_md(r: dict) -> str:
    q = r["respuesta"]
    u = r["usage"] or {}
    L = ["# Crítica del papel (lab F67 D)", "", f"{r['modelo']} {r['effort']} · US$ {r['usd']:.4f} · tokens in {u.get('input_tokens')} · out {u.get('output_tokens')} · {r['segundos']} s · {len(r['intentos'])} intento(s)", ""]
    if q is None:
        return "\n".join(L + ["sin JSON válido", ""])
    L += [f"**Nota total:** {q.get('nota_total')}", "", "## Resumen", ""] + [f"- {x}" for x in q.get("resumen") or []]
    L += ["", "## Por beat", "", "| cap | beat | ficha suma | por qué | sello suma | por qué | momento | se lee | compite | qué pondría | sello pondría |", "|---|---|---|---|---|---|---|---|---|---|---|"]
    for b in q.get("beats") or []:
        p = b.get("que_pondria")
        qp = "—" if not p else f"{p.get('id')} · {p.get('etiqueta')} · {p.get('texto')} · {p.get('autor')} · {p.get('por_que')}"
        L.append(f"| {b.get('cap')} | {b.get('beat')} | {b.get('ficha_suma')} | {b.get('ficha_por_que')} | {b.get('sello_suma')} | {b.get('sello_por_que')} | {b.get('momento')} | {b.get('se_lee')} | {b.get('compite')} | {qp} | {b.get('sello_pondria')} |")
    L += ["", "## Huecos", ""] + [f"- {h.get('cap')} beat {h.get('beat')} · {h.get('id')} · {h.get('etiqueta')} · {h.get('texto')} · {h.get('autor')} · {h.get('por_que')}" for h in q.get("huecos") or []]
    L += ["", "## Relojes", "", str(q.get("relojes")), "", "## Gancho y pico", "", str(q.get("gancho_y_pico")), "", "## Riesgos", ""] + [f"- {x}" for x in q.get("riesgos") or []] + [""]
    return "\n".join(L)


def main() -> int:
    import fase1_5 as f15
    d = AQUI / "d"
    d.mkdir(exist_ok=True)
    system, formato = bloques()
    papel = json.loads((STEPS / "01e_pantalla.json").read_text(encoding="utf-8"))
    assert not papel.get("aprobado") and papel.get("prompt_version") == "m01e-7"
    user, payload = armar_user(papel, formato, f15._topic_v3(TID)["evidence_pool"])
    (d / "user.json").write_text(user, encoding="utf-8", newline="\n")
    print("md5 SYSTEM_D", md5(system), "· md5 USER", md5(user), "·", len(user), "car.")
    steps_md5.foto("D_antes")
    ch = ROOT / "data" / "cost_history.json"
    m0 = ch.stat().st_mtime_ns
    r = llamar(system, user, d)
    steps_md5.foto("D_despues")
    cambios = steps_md5.compara("D_antes", "D_despues")
    (d / "D_1.md").write_text(d_md(r), encoding="utf-8", newline="\n")
    filas = validar(r["respuesta"], payload, papel) if r["respuesta"] else []
    V = ["# F67 D — validación", "", "| tipo | cap | beat | id | (cap, beat) existe | id existe | ya en el papel | cifras sin respaldo |", "|---|---|---|---|---|---|---|---|"]
    V += [f"| {f['tipo']} | {f['cap']} | {f['beat']} | {f['id']} | {f['beat_existe']} | {f['id_existe']} | {f['ya_en_papel']} | {', '.join(f['cifras_sin_respaldo']) or '—'} |" for f in filas]
    V += ["", f"Nota {(r['respuesta'] or {}).get('nota_total')} · US$ {r['usd']:.4f} · {r['segundos']} s", ""]
    (d / "validacion.md").write_text("\n".join(V), encoding="utf-8", newline="\n")
    R = ["# F67d_REPORT — crítico del papel (lab, no cableado)", "",
         f"Handoff `{HANDOFF_MD5}` · SYSTEM_D `{md5(system)}` · USER `{md5(user)}` · {MODELO} {EFFORT} · 1 corrida · US$ {r['usd']:.4f}", "",
         f"Producción intacta: archivos de `_steps/<tid>/` que cambiaron: {cambios or 'ninguno'} · `data/cost_history.json` mtime igual: {ch.stat().st_mtime_ns == m0}", "",
         (d / "validacion.md").read_text(encoding="utf-8"), "", (d / "D_1.md").read_text(encoding="utf-8")]
    (d / "F67d_REPORT.md").write_text("\n".join(R), encoding="utf-8", newline="\n")
    print("\n".join(R))
    return 0 if r["respuesta"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
