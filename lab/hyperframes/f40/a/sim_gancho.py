"""
lab/hyperframes/f40/a/sim_gancho.py — F40 §6.4: la tabla de §3 del handoff recalculada por código.

Corre la validación del papel (m01e_pantalla.validar) sobre cada ficha del gancho (cap 1, beat 1) dos veces:
  · «hoy»   con el código de HEAD 8669045 (git archive de script_engine/ a una carpeta temporal, primera en sys.path);
  · «F40»   con el código del árbol de trabajo (gancho_dicho y dice_voz borrados).
Con F40, si hay preguntas, simula la respuesta del autor «otro hecho» (la mantiene: confirmados = _confirmar(preguntas))
y valida al cierre (final=True): dice si queda.

Datos (solo lectura, congelados en esta carpeta):
  kyshtym/  copia de data/scripts/_steps/f39-kyshtym (pool, escaleta, skeleton, narración, 01e_pantalla.raw.json);
            las fichas del gancho son las que el autor propuso en ch01 beat 1 en cada intento del raw (D03, D50, D201).
  vajont/   copia de lab/hyperframes/f38/b2/fase1/f8s3-vajont + lab/hyperframes/f38/b4/01e_pantalla.raw.json; el papel
            v6 no trae D195 en el gancho: la ficha es la de HANDOFF_F35_v6 («LONGARONE · 1.269 de 1.328 habitantes
            murieron»), anclada en ch01 [2] («…una niña de Longarone…») con respaldo literal del texto de D195.
La voz es la de la entrada del raw (`entrada.caps`: la que vio m01e). Cero llamadas a modelos.

Uso: python lab/hyperframes/f40/a/sim_gancho.py   → escribe lab/hyperframes/f40/a/sim_gancho_salida.md
"""
from __future__ import annotations

import io
import json
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
ROOT = AQUI.parents[3]
HEAD = "8669045"
GANCHO = ("ch01", 1)
D195 = {"pool_id": "D195", "sentence_idx": 2, "palabra": "Longarone", "etiqueta": "LONGARONE",
        "texto": "1.269 de 1.328 habitantes murieron", "respaldo": "1.269 de 1.328 habitantes fallecidos",
        "autor": None, "aporta": "HANDOFF_F35_v6 (la ficha del gancho de Vajont v6)"}


def casos() -> list[dict]:
    out = []
    raw = json.loads((AQUI / "kyshtym" / "01e_pantalla.raw.json").read_text(encoding="utf-8"))
    for k, i in enumerate(raw["intentos"]):
        r = i.get("respuesta") or {}
        for b in (r.get("beats") or []) + (r.get("cambios") or []):
            fi = b.get("ficha") if isinstance(b, dict) else None
            if (b.get("cap"), b.get("beat")) == GANCHO and isinstance(fi, dict):
                out.append({"tema": "Kyshtym", "dir": "kyshtym", "intento": k + 1, "ficha": fi})
    out.append({"tema": "Vajont v6", "dir": "vajont", "intento": None, "ficha": D195})
    return out


def _ent(mp, d: str) -> dict:
    raw = json.loads((AQUI / d / "01e_pantalla.raw.json").read_text(encoding="utf-8"))
    carga = mp.cargar(d, AQUI)
    seg = {"valor": mp.SEG_POR_PALABRA_RESPALDO, "oraciones": 0, "caps": 0, "voz": "(sin uso: caps del raw)"}
    e = mp.entrada(carga, raw["entrada"]["clima"], seg)
    e["caps"] = raw["entrada"]["caps"]                 # la voz que vio m01e (con su `caben`)
    e["_pool"] = carga["pool"]
    return e


def correr(modo: str) -> list[dict]:
    """Dentro del subproceso: valida cada ficha del gancho con el script_engine que esté primero en sys.path."""
    from script_engine import evidence as ev
    from script_engine import m01e_pantalla as mp
    from script_engine.voz_utils import numero_en
    res = []
    ents: dict[str, dict] = {}
    for c in casos():
        ent = ents.setdefault(c["dir"], _ent(mp, c["dir"]))
        todo = [(cc["cap"], s["idx"], s["texto"]) for cc in ent["caps"] for s in cc["oraciones"]]
        voz = " ".join(t for _, _, t in todo)
        fi = c["ficha"]
        resp = {"beats": [{"cap": GANCHO[0], "beat": GANCHO[1], "ficha": fi}]}
        v = mp.validar(resp, ent)
        caida = next((d for d in v["descartados"] if d.get("que") == "ficha"), None)
        fila = {**{k: c[k] for k in ("tema", "intento")}, "pool_id": fi["pool_id"],
                "ficha": f"{fi.get('etiqueta')} · {fi.get('texto')}", "sentence_idx": fi.get("sentence_idx"),
                "caida": {k: caida[k] for k in ("regla", "motivo")} if caida else None,
                "preguntas": [mp._pregunta_txt(q) for q in v["preguntas"]],
                "tokens": [(q["regla"], q["token"], q.get("donde")) for q in v["preguntas"]]}
        if modo == "hoy":       # lo que miraba dice_voz en HEAD: las cifras del TEXTO DEL ÍTEM en toda la voz + used_in
            it = ev.items(ent["_pool"])[fi["pool_id"]]
            figs = [n for n in ev._figures(ev.text_of(it)) if numero_en(n, voz)]
            fila["dice_voz"] = {"used_in": bool(ev.used_in(voz, it)),
                                "cifras": [(n, mp._donde(n, todo)) for n in figs]}
        if modo != "hoy":       # lo que mira no_dicho en el gancho con F40: las cifras del DATO de la ficha en toda la voz
            from script_engine.voz_utils import numeros
            fila["cifras_ficha"] = [(n, mp._donde(n, todo)) for n in numeros(str(fi.get("texto") or ""))
                                    if mp._donde(n, todo)]
        if modo != "hoy" and v["preguntas"]:    # el autor contesta «otro hecho»: la mantiene en el reintento
            conf = mp._confirmar(v["preguntas"])
            v2 = mp.validar(resp, ent, conf, final=True)
            c2 = next((d for d in v2["descartados"] if d.get("que") == "ficha"), None)
            f2 = next((s["ficha"] for s in v2["beats"] if (s["cap"], s["beat"]) == GANCHO), None)
            fila["otro_hecho"] = {"queda": f2 is not None, "juicio_autor": (f2 or {}).get("juicio_autor"),
                                  "caida": {k: c2[k] for k in ("regla", "motivo")} if c2 else None}
        res.append(fila)
    return res


def _head_dir() -> Path:
    t = Path(tempfile.mkdtemp(prefix="f40a_head_"))
    tar = subprocess.run(["git", "-C", str(ROOT), "archive", HEAD, "script_engine"], capture_output=True, check=True)
    with tarfile.open(fileobj=io.BytesIO(tar.stdout)) as tf:
        tf.extractall(t)
    return t


def _sub(modo: str, primero: Path) -> list[dict]:
    code = (f"import sys,json; sys.path[:0]=[{str(primero)!r},{str(ROOT)!r},{str(AQUI)!r}]; import sim_gancho as s; "
            f"import script_engine; assert script_engine.__file__.startswith({str(primero)!r}), script_engine.__file__; "
            f"print('@@'+json.dumps(s.correr({modo!r}), ensure_ascii=False))")
    p = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, encoding="utf-8", cwd=str(ROOT),
                       env={**__import__("os").environ, "PYTHONIOENCODING": "utf-8"})
    if p.returncode:
        raise SystemExit(p.stderr)
    return json.loads(p.stdout.split("@@", 1)[1])


def _d(dn) -> str:
    return f"{dn[0]} [{dn[1]}] («{dn[2]}»)" if dn else "—"


def main() -> int:
    hoy = _sub("hoy", _head_dir())
    f40 = _sub("f40", ROOT)
    L = ["# F40 §6.4 — la tabla de §3 recalculada por código", "",
         f"`python lab/hyperframes/f40/a/sim_gancho.py` · hoy = código de HEAD {HEAD} · F40 = árbol de trabajo. "
         "Voz = `entrada.caps` del raw de cada papel (la que vio m01e). Una fila por ficha del gancho que el autor "
         "propuso (Kyshtym: ch01 beat 1, intento N del raw de F39).", "",
         "| tema | dato del gancho (intento, oración) | cifras que encuentra en la voz (con cap y oración) | hoy (HEAD) | con F40 |",
         "|---|---|---|---|---|"]
    det = []
    for h, f in zip(hoy, f40):
        assert (h["pool_id"], h["intento"]) == (f["pool_id"], f["intento"])
        dv = h["dice_voz"]
        hoy_c = (", ".join(f"«{n}» en {_d(dn)}" for n, dn in dv["cifras"]) or "ninguna") + \
                (" · used_in" if dv["used_in"] else "")
        f40_c = ", ".join(f"«{t}» en {_d(dn)}" for t, dn in f["cifras_ficha"]) or "ninguna"
        hoy_r = f"cae: {h['caida']['regla']} («{h['caida']['motivo']}»)" if h["caida"] else \
            ("pregunta" if h["preguntas"] else "pasa")
        if f["caida"]:
            f40_r = f"cae: {f['caida']['regla']} («{f['caida']['motivo']}»)"
        elif f["preguntas"]:
            oh = f.get("otro_hecho") or {}
            f40_r = (f"pregunta al autor ({len(f['preguntas'])}) → otro hecho → "
                     + ("**queda**" if oh.get("queda") else f"cae: {(oh.get('caida') or {}).get('regla')}"))
        else:
            f40_r = "pasa (sin cambio)" if not h["caida"] else "pasa"
        quien = f"{f['pool_id']} «{f['ficha']}» (int. {f['intento'] or '—'}, [{f['sentence_idx']}])"
        L.append(f"| {f['tema']} | {quien} | hoy (cifras del texto del ítem, `dice_voz`): {hoy_c}<br>F40 (cifras del "
                 f"dato de la ficha, `no_dicho`): {f40_c} "
                 f"| {hoy_r} | {f40_r} |")
        det.append(f"### {f['tema']} · {quien}")
        det.append(f"- hoy: {hoy_r}")
        for q in f["preguntas"]:
            det.append(f"- F40 pregunta: {q}")
        if f.get("otro_hecho"):
            det.append(f"- F40 con «otro hecho»: queda={f['otro_hecho']['queda']} · juicio_autor="
                       f"{json.dumps(f['otro_hecho']['juicio_autor'], ensure_ascii=False)}"
                       + (f" · cae {f['otro_hecho']['caida']}" if f['otro_hecho']['caida'] else ""))
        if f["caida"]:
            det.append(f"- F40: cae {f['caida']['regla']}: {f['caida']['motivo']}")
        det.append("")
    L += ["", "## Detalle por ficha", ""] + det
    out = AQUI / "sim_gancho_salida.md"
    out.write_text("\n".join(L) + "\n", encoding="utf-8")
    print("\n".join(L))
    return 0


if __name__ == "__main__":
    sys.exit(main())
