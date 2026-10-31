# -*- coding: utf-8 -*-
"""
F63 Parte B — verificador de narración (solo mide; HANDOFF_F63_papel_opus.md §Parte B).

Opus 5.5 medium, una llamada por cap, 7 caps × 2 corridas = 14 a la vez, sobre 01b_narracion_v3.json de producción
(md5 c7badfbe…; PARÁ si no coincide). USER = {"cap", "oraciones": [{idx, texto}], "archivo": [id, texto, fecha, fuente,
contexto_fuente] (los 362 ítems de A.1.1), "disputas": versiones + contradicciones de ficha_caso.json} +
"\\n\\nFormato de salida: " + FORMATO. SYSTEM literal del handoff (md5 ce31cc51…; PARÁ si no da).
Salida: b/verificador_<cap>_<n>.json, b/tabla_b.json, b/etapa_b.log. Comparte con etapa_a_papel la entrada y la llamada.
"""
from __future__ import annotations

import hashlib
import json
import sys
import time
import traceback
from collections import Counter
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from typing import Any

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))
from etapa_a_papel import OPUS, STEPS, TID, entrada_completa, entrada_hoy, llamar_modelo, md5   # noqa: E402

DIR_B = AQUI / "b"
NARRACION_MD5 = "c7badfbe260f5eb24a47e780b40406b5"
SYSTEM_B_MD5 = "ce31cc515a077d74da72479e9693296e"
EFFORT = "medium"
CORRIDAS = (1, 2)

SYSTEM_B = """Sos el verificador de hechos de un documental de historia en español. Recibís las oraciones numeradas de un capítulo y el archivo del caso: cada dato con su id, su texto, su fecha, su fuente y, en `contexto_fuente`, el fragmento original de la fuente; y las versiones en disputa del caso.

Para cada oración, separá las afirmaciones de hecho que quien escucha va a tomar como verdad: quién, qué, cuándo, cuánto, dónde, cómo era algo, quién dijo qué y en qué momento. No listes preguntas, transiciones ni frases que no afirman un hecho. No juzgues el estilo.

Para cada afirmación, un estado:
- respaldada: un dato del archivo la sostiene (poné su id);
- contradice: un dato del archivo, o su contexto_fuente, dice otra cosa (poné el id y el fragmento literal que lo muestra);
- sin_respaldo: nada del archivo la sostiene ni la contradice.
Una cita atribuida a una fecha o a un hecho distinto del que dice el archivo es «contradice». Si el archivo trae versiones en disputa y la oración da una sola como cierta, es «contradice» con las dos versiones en el fragmento.

Devolvé solo JSON."""

FORMATO_B = ('{"cap": "ch01", "afirmaciones": [{"oracion": 0, "afirmacion": "…", "estado": "respaldada" | "contradice" | '
             '"sin_respaldo", "ids": ["D85"], "fragmento": "…" | null}]}')

# B.1 contrato: (cap, idx del handoff, comienzo del texto, qué cuenta como encontrada)
CONTRATO = [
    ("ch01", 1, "Ese pie va a cerrar", "contradice D85 («no se cerraba»)"),
    ("ch01", 2, "La foto es en blanco y negro.", "contradice Q25 (contexto_fuente «sepia family photos») o sin_respaldo"),
    ("ch06", 10, "Hacia junio de 2007, según otras referencias en 2006", "respaldada con D31 o D30 en ids"),
    ("ch06", 12, "El gobierno de Australia Occidental lo llamó", "contradice Q07 (fecha 2022)"),
]


def archivo_b(ent_comp: dict) -> list[dict]:
    return [{k: x.get(k) for k in ("id", "texto", "fecha", "fuente", "contexto_fuente")} for x in ent_comp["archivo"]]


def user_b(cap: dict, archivo: list[dict], disputas: dict) -> str:
    u = {"cap": cap["cap"], "oraciones": [{"idx": s["idx"], "texto": s["texto"]} for s in cap["oraciones"]],
         "archivo": archivo, "disputas": disputas}
    return json.dumps(u, ensure_ascii=False) + "\n\nFormato de salida: " + FORMATO_B


def _afs(resp: dict | None) -> list[dict]:
    return [a for a in (resp or {}).get("afirmaciones") or [] if isinstance(a, dict)]


def resumen(cap: str, n: int, resp: dict | None, ll: dict) -> dict[str, Any]:
    afs = _afs(resp)
    est = Counter(str(a.get("estado")) for a in afs)
    u = ll.get("usage") or {}
    return {"cap": cap, "corrida": n, "json": resp is not None, "afirmaciones": len(afs),
            "respaldadas": est.get("respaldada", 0), "contradice": est.get("contradice", 0),
            "sin_respaldo": est.get("sin_respaldo", 0), "otros_estados": {k: v for k, v in est.items()
                                                                           if k not in ("respaldada", "contradice", "sin_respaldo")},
            "lista": [{"oracion": a.get("oracion"), "afirmacion": a.get("afirmacion"), "estado": a.get("estado"),
                       "ids": a.get("ids"), "fragmento": a.get("fragmento")}
                      for a in afs if a.get("estado") in ("contradice", "sin_respaldo")],
            "tokens_in": u.get("input_tokens"), "tokens_out": u.get("output_tokens"), "usd": ll["usd"],
            "segundos": ll["segundos"], "intentos": len(ll["intentos"])}


def contrato(caps: dict[str, dict], resps: dict[tuple[str, int], dict | None]) -> list[dict]:
    filas = []
    for cap, idx, comienzo, cuenta in CONTRATO:
        ors = caps[cap]["oraciones"]
        real = idx if 0 <= idx < len(ors) and ors[idx]["texto"].startswith(comienzo) else \
            next((s["idx"] for s in ors if s["texto"].startswith(comienzo)), None)
        fila = {"cap": cap, "idx_handoff": idx, "idx_real": real, "oracion": ors[real]["texto"] if real is not None else None,
                "cuenta_como_encontrada": cuenta, "corridas": {}}
        for n in CORRIDAS:
            afs = [a for a in _afs(resps.get((cap, n))) if a.get("oracion") == real]
            fila["corridas"][n] = [{"afirmacion": a.get("afirmacion"), "estado": a.get("estado"), "ids": a.get("ids"),
                                    "fragmento": a.get("fragmento")} for a in afs]
        filas.append(fila)
    return filas


def contradice_en_ambas(resps: dict[tuple[str, int], dict | None], caps: list[str]) -> list[dict]:
    out = []
    for cap in caps:
        a1 = [a for a in _afs(resps.get((cap, 1))) if a.get("estado") == "contradice"]
        a2 = [a for a in _afs(resps.get((cap, 2))) if a.get("estado") == "contradice"]
        k2 = {(a.get("oracion"), tuple(sorted(a.get("ids") or []))): a for a in a2}
        for a in a1:
            k = (a.get("oracion"), tuple(sorted(a.get("ids") or [])))
            if k in k2:
                out.append({"cap": cap, "oracion": a.get("oracion"), "ids": a.get("ids"),
                            "corrida_1": a.get("afirmacion"), "corrida_2": k2[k].get("afirmacion")})
            else:
                misma_or = [b for b in a2 if b.get("oracion") == a.get("oracion")]
                if misma_or:
                    out.append({"cap": cap, "oracion": a.get("oracion"), "ids": a.get("ids"), "ids_corrida_2": misma_or[0].get("ids"),
                                "corrida_1": a.get("afirmacion"), "corrida_2": misma_or[0].get("afirmacion"),
                                "nota": "misma oración, ids distintos"})
    return out


def tarea(cap: dict, n: int, archivo: list[dict], disputas: dict, log: list[str]) -> tuple[str, int, dict | None, dict]:
    etiqueta = f"lab_f63_B_{cap['cap']}_{n}"
    try:
        user = user_b(cap, archivo, disputas)
        ll = llamar_modelo(OPUS, EFFORT, SYSTEM_B, user, etiqueta, log)
        resp = ll["respuesta"]
        raw = {"cap": cap["cap"], "corrida": n, "modelo": OPUS, "effort": EFFORT, "system_md5": md5(SYSTEM_B),
               "user_md5": md5(user), "oraciones": [{"idx": s["idx"], "texto": s["texto"]} for s in cap["oraciones"]],
               "intentos": ll["intentos"], "respuesta": resp, "usage": ll["usage"], "usd": ll["usd"], "segundos": ll["segundos"]}
        (DIR_B / f"verificador_{cap['cap']}_{n}.json").write_text(json.dumps(raw, ensure_ascii=False, indent=1), encoding="utf-8")
        return cap["cap"], n, resp, resumen(cap["cap"], n, resp, ll)
    except Exception as e:  # noqa: BLE001
        log.append(f"{etiqueta}: EXCEPCIÓN {type(e).__name__}: {e}\n{traceback.format_exc()}")
        return cap["cap"], n, None, {"cap": cap["cap"], "corrida": n, "error": f"{type(e).__name__}: {e}"}


def main() -> int:
    DIR_B.mkdir(parents=True, exist_ok=True)
    t0 = time.time()
    h = hashlib.md5((STEPS / TID / "01b_narracion_v3.json").read_bytes()).hexdigest()
    if h != NARRACION_MD5:
        raise SystemExit(f"PARÁ: md5 de 01b_narracion_v3.json {h} ≠ {NARRACION_MD5}")
    if md5(SYSTEM_B) != SYSTEM_B_MD5:
        raise SystemExit(f"PARÁ: md5 del SYSTEM B {md5(SYSTEM_B)} ≠ {SYSTEM_B_MD5}")
    carga, ent_hoy = entrada_hoy()
    ent_comp, _, disputas = entrada_completa(carga)
    archivo = archivo_b(ent_comp)
    log: list[str] = []
    caps = {c["cap"]: c for c in ent_hoy["caps"]}
    trabajos = [(c, n) for c in ent_hoy["caps"] for n in CORRIDAS]
    with ThreadPoolExecutor(max_workers=len(trabajos)) as ex:
        futs = [ex.submit(tarea, c, n, archivo, disputas, log) for c, n in trabajos]
        res = [f.result() for f in futs]
    resps = {(cap, n): r for cap, n, r, _ in res}
    tabla = [x for _, _, _, x in res]
    total = {"narracion_md5": h, "system_b_md5": md5(SYSTEM_B), "archivo_items": len(archivo),
             "tabla": tabla, "contrato": contrato(caps, resps),
             "contradice_en_ambas": contradice_en_ambas(resps, [c["cap"] for c in ent_hoy["caps"]]),
             "usd_total": round(sum(x.get("usd") or 0 for x in tabla), 4), "segundos_total": round(time.time() - t0, 1),
             "log": log}
    (DIR_B / "tabla_b.json").write_text(json.dumps(total, ensure_ascii=False, indent=1), encoding="utf-8")
    (DIR_B / "etapa_b.log").write_text("\n".join(log) + "\n", encoding="utf-8")
    print(json.dumps({k: v for k, v in total.items() if k not in ("log", "tabla")}, ensure_ascii=False, indent=1)[:6000])
    print(json.dumps([{k: v for k, v in x.items() if k != "lista"} for x in tabla], ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
