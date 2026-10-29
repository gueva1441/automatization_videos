# -*- coding: utf-8 -*-
"""F52 — lee de fal, ANTES de cualquier llamada que cueste, el schema (OpenAPI) y el precio de cada endpoint de la prueba.
Solo GET: no genera nada, no cobra. Escribe f52/schemas/<letra>.json (el OpenAPI crudo) y f52/SCHEMAS_F52.md (los campos
de entrada con tipo, default y enum, y el precio leído).

Uso: python lab/hyperframes/f52/schemas_f52.py
"""
import json
import sys
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
F52 = Path(__file__).resolve().parent
ENDPOINTS = {
    "K": "kling/v4/image-to-video",
    "S": "bytedance/seedance-2.5/image-to-video",
    "F": "blackforestlabs/flux-3-max/image-to-video",
    "G": "google/gemini-omni-flash/v1.1/image-to-video",
    "seedream": "fal-ai/bytedance/seedream/v5/lite/text-to-image",
}


def _key() -> str:
    from config import APIConfig
    return APIConfig().fal_api_key


def openapi(eid: str) -> dict:
    r = requests.get("https://fal.ai/api/openapi/queue/openapi.json", params={"endpoint_id": eid}, timeout=60)
    r.raise_for_status()
    return r.json()


def precio(eid: str) -> dict:
    r = requests.get("https://api.fal.ai/v1/models/pricing", params={"endpoint_id": eid},
                     headers={"Authorization": f"Key {_key()}"}, timeout=60)
    return {"http": r.status_code, "body": r.json() if r.headers.get("content-type", "").startswith("application/json")
            else r.text[:500]}


def campos_entrada(spec: dict) -> dict:
    sch = spec.get("components", {}).get("schemas", {})
    nombre = next((k for k in sch if k.endswith("Input")), None)
    if not nombre:
        return {}
    s = sch[nombre]
    req = set(s.get("required") or [])
    out = {}
    for k, v in (s.get("properties") or {}).items():
        enum = v.get("enum")
        if not enum and "anyOf" in v:
            enum = [e for a in v["anyOf"] for e in (a.get("enum") or [])] or None
        if not enum and "$ref" in str(v.get("allOf") or ""):
            ref = v["allOf"][0]["$ref"].split("/")[-1]
            enum = sch.get(ref, {}).get("enum")
        out[k] = {"tipo": v.get("type") or [a.get("type") for a in v.get("anyOf", [])] or "ref",
                  "default": v.get("default"), "enum": enum, "min": v.get("minimum"), "max": v.get("maximum"),
                  "requerido": k in req, "desc": (v.get("description") or "")[:160]}
    return {"schema": nombre, "campos": out}


def main() -> int:
    (F52 / "schemas").mkdir(exist_ok=True)
    L = ["# SCHEMAS_F52 — schemas y precios leídos de fal antes de llamar", "",
         "Salida de `python lab/hyperframes/f52/schemas_f52.py` (solo GET: OpenAPI de `fal.ai/api/openapi/queue/"
         "openapi.json?endpoint_id=…` y precio de `api.fal.ai/v1/models/pricing?endpoint_id=…`).", ""]
    res = {}
    for letra, eid in ENDPOINTS.items():
        try:
            spec = openapi(eid)
            (F52 / "schemas" / f"{letra}.json").write_text(json.dumps(spec, ensure_ascii=False, indent=1),
                                                          encoding="utf-8")
            ce = campos_entrada(spec)
        except Exception as e:                                   # noqa: BLE001 — se reporta tal cual
            ce = {"error": f"{type(e).__name__}: {e}"[:300]}
        pr = precio(eid)
        res[letra] = {"endpoint": eid, "entrada": ce, "precio": pr}
        L += [f"## {letra} — `{eid}`", ""]
        if "error" in ce:
            L += [f"- schema: **error** {ce['error']}", ""]
        else:
            L += [f"Schema de entrada `{ce.get('schema')}`:", "", "| campo | req | tipo | default | enum / rango | descripción |",
                  "|---|---|---|---|---|---|"]
            for k, v in ce.get("campos", {}).items():
                rango = v["enum"] or (f"{v['min']}–{v['max']}" if v["min"] is not None or v["max"] is not None else "")
                L += [f"| `{k}` | {'sí' if v['requerido'] else ''} | {v['tipo']} | {json.dumps(v['default'], ensure_ascii=False)} "
                      f"| {rango} | {v['desc'].replace('|', '/')} |"]
            L += [""]
        L += [f"Precio (HTTP {pr['http']}): `{json.dumps(pr['body'], ensure_ascii=False)[:600]}`", ""]
    (F52 / "SCHEMAS_F52.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (F52 / "schemas" / "_resumen.json").write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    for letra, r in res.items():
        print(letra, r["endpoint"], "· campos:", list((r["entrada"].get("campos") or {}).keys()) or r["entrada"],
              "· precio:", json.dumps(r["precio"], ensure_ascii=False)[:300])
    return 0


if __name__ == "__main__":
    sys.exit(main())
