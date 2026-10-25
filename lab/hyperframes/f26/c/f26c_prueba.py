"""F26 §C — prueba sin gasto de los workers: R2 + R3 de Kyshtym sobre una COPIA de sus fuentes (los txt ya bajados y la
caché de R3 de F23/F24), con el registro de fuentes de F24; pared con 1 y con 8 workers.
- R2: `download_sources` con los candidatos de siempre (R1 guardado ∪ registro) y `previos` del registro: lo ya bajado
  no se pide; lo que falta se pide a la red de verdad (sin API, sin costo).
- R3: `extract_documents` sobre los 8 documentos del pool de F23 con la caché copiada y un `call` que FALLA si se lo
  llama (cero API): todo sale de la caché (la clave lleva el título de la semilla, «Desastre nuclear Kyshtym Mayak»).
- R3 con latencia simulada: sin caché y un `call` que devuelve lo guardado después de dormir LAT_S por trozo (para ver
  qué gana el paralelo cuando hay llamadas de verdad).
Uso: python -I lab/hyperframes/f26/c/f26c_prueba.py <carpeta de trabajo fuera del repo>
"""
from __future__ import annotations

import json
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT)]
KYS = ROOT / "data" / "scripts" / "_steps" / "f18-kyshtym-mayak"
LAT_S = 2.0


def _j(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    from researcher_steps import research_v3 as rv
    trabajo = Path(sys.argv[1])
    perfil = json.loads((KYS / "_perfil.json").read_text(encoding="utf-8"))
    rv.set_vocabulario(perfil)
    rv.set_idiomas(perfil.get("idiomas_research"))
    registro = rv.cargar_registro(KYS)
    r1 = json.loads((KYS / "fuentes_r1.json").read_text(encoding="utf-8"))
    candidatos = rv.unir_fuentes(r1["fuentes"], registro)
    tiempo = rv.tiempo_del_perfil(perfil)
    seed = {"seed_title": "Desastre nuclear Kyshtym Mayak",          # el de la semilla (seeds_archive): la clave de la caché
            "roles_testigo": perfil.get("roles_testigo") or [],
            "roles_antagonista": perfil.get("roles_antagonista") or []}
    res: dict = {"candidatos": len(candidatos), "r2": {}, "r3_cache": {}, "r3_latencia": {}, "lat_s": LAT_S}
    for w in (1, 8):
        d = trabajo / f"w{w}"
        if d.exists():
            shutil.rmtree(d)
        shutil.copytree(KYS / "fuentes", d / "fuentes")
        shutil.copytree(KYS / "_r3_cache", d / "_r3_cache")
        (d / "fuentes" / "manifest.json").unlink()        # el manifest de la corrida se rehace; lo bajado sigue
        log: list[str] = []
        t0 = time.time()
        man = rv.download_sources(candidatos, d / "fuentes", place_re=perfil["place_re"], log=log,
                                  previos=rv.previos_del_registro(registro), workers=w)
        res["r2"][w] = {"pared_s": round(time.time() - t0, 1),
                        "ok": sum(1 for x in man["documentos"] if x.get("ok")),
                        "pedidos": sum(len(x.get("intentos") or []) for x in man["documentos"]
                                       if x.get("estado") not in ("no_intentada",) and x.get("descargado")),
                        "estados": {e: sum(1 for x in man["documentos"] if x["estado"] == e)
                                    for e in sorted({x["estado"] for x in man["documentos"]})},
                        "log": log}
        # R3: los documentos del pool de F23 (los que tienen caché de R3 con sus ids); los demás OK del registro no
        # se leyeron nunca con este prompt y con la caché vacía la prueba gastaría
        docs = [x for x in _j(KYS / "fuentes" / "manifest.json")["documentos"] if x.get("ok")]
        texts = {x["id"]: rv.DocText(x["id"], (d / "fuentes" / x["txt"]).read_text(encoding="utf-8")) for x in docs}

        def prohibido(prompt, **kw):
            raise RuntimeError("R3 sin caché: esta prueba no gasta")
        log3: list[str] = []
        t0 = time.time()
        per = rv.extract_documents(seed, [dict(x) for x in docs], texts, event_year=tiempo["anio_inicio"],
                                   cache_dir=d / "_r3_cache", place_re=perfil["place_re"], log=log3, workers=w,
                                   call=prohibido)
        res["r3_cache"][w] = {"pared_s": round(time.time() - t0, 2), "docs": len(per),
                              "items": sum(len(v.get(k) or []) for v in per.values() for k in rv.KINDS),
                              "fallidos": [x for x in log3 if "fallida" in x]}
        guardado = {}
        for x in docs:
            c = d / "_r3_cache" / f"r3_{x['id']}.json"
            if c.exists():
                guardado[x["url"]] = list(json.loads(c.read_text(encoding="utf-8")).values())
        n = {"llamadas": 0}

        def lento(prompt, **kw):
            import re
            cab = prompt.splitlines()[1]
            m = re.search(r"\(parte (\d+) de \d+\)", cab)
            xs = guardado.get(cab.rsplit(" — ", 1)[1].strip()) or [{}]
            time.sleep(LAT_S)
            n["llamadas"] += 1
            return json.loads(json.dumps(xs[min(int(m.group(1)) - 1 if m else 0, len(xs) - 1)]))
        t0 = time.time()
        per2 = rv.extract_documents(seed, [dict(x) for x in docs], texts, event_year=tiempo["anio_inicio"],
                                    cache_dir=None, place_re=perfil["place_re"], log=[], workers=w, call=lento)
        res["r3_latencia"][w] = {"pared_s": round(time.time() - t0, 1), "llamadas_simuladas": n["llamadas"],
                                 "mismo_resultado_que_cache": json.dumps(per2, sort_keys=True, default=str)
                                 == json.dumps(per, sort_keys=True, default=str)}
        print(f"[w={w}] R2 {res['r2'][w]['pared_s']} s ({res['r2'][w]['estados']}) · R3 caché "
              f"{res['r3_cache'][w]['pared_s']} s ({res['r3_cache'][w]['items']} ítems) · R3 latencia "
              f"{res['r3_latencia'][w]['pared_s']} s ({n['llamadas']} trozos × {LAT_S} s)", flush=True)
    m1 = json.dumps([{k: v for k, v in x.items() if k != "descargado"} for x in
                     json.loads((trabajo / "w1" / "fuentes" / "manifest.json").read_text(encoding="utf-8"))["documentos"]],
                    sort_keys=True)
    m8 = json.dumps([{k: v for k, v in x.items() if k != "descargado"} for x in
                     json.loads((trabajo / "w8" / "fuentes" / "manifest.json").read_text(encoding="utf-8"))["documentos"]],
                    sort_keys=True)
    res["manifest_igual_1_vs_8"] = m1 == m8
    res["r3_igual_1_vs_8"] = res["r3_cache"][1]["items"] == res["r3_cache"][8]["items"]
    out = Path(__file__).resolve().parent / "prueba_workers.json"
    out.write_text(json.dumps(res, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"manifest igual 1 vs 8: {res['manifest_igual_1_vs_8']} · R3 igual: {res['r3_igual_1_vs_8']}")


if __name__ == "__main__":
    main()
