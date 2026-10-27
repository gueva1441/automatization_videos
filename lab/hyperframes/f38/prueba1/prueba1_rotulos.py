"""F38e-0 · A — Prueba 1: rótulos parafraseados (HANDOFF_F38e0_pruebas_en_seco.md §A). Lab, no pipeline.

UNA llamada a Sonnet (m01e.MODELO / EFFORT) con el SYSTEM de PRUEBA1_prompt_rotulos.md («Prompt nuevo (m01e-6-prueba),
entero», recortado del md por código) y el USER de m01e con `"respaldo": "…", ` en el formato. Validación con el código
de hoy (m01e.validar, final=False) + verificación nueva del respaldo (solo acá). Escribe SOLO en esta carpeta.

    python lab/hyperframes/f38/prueba1/prueba1_rotulos.py --seco   # todo menos la llamada (reconstrucción, peor caso)
    python lab/hyperframes/f38/prueba1/prueba1_rotulos.py          # la llamada (se niega si ya hay prueba1.raw.json)
    python lab/hyperframes/f38/prueba1/prueba1_rotulos.py --tabla  # rehace la tabla desde prueba1.raw.json (US$ 0)
"""
from __future__ import annotations

import sys
sys.dont_write_bytecode = True                       # nada de __pycache__ en el pipeline

import hashlib
import json
import logging
import re
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
F38 = ROOT / "lab" / "hyperframes" / "f38"
TOPE_PRUEBA = 0.60                                    # pedido del analista (el tope de la tanda es 1,00)
LOG: list[str] = []


def log(s: str = "") -> None:
    print(s, flush=True)
    LOG.append(s)


def foto(dirs: list[Path]) -> dict[str, tuple[float, int]]:
    out = {}
    for d in dirs:
        for f in d.rglob("*"):
            if f.is_file():
                st = f.stat()
                out[str(f.relative_to(ROOT))] = (st.st_mtime, st.st_size)
    return out


def md5f(p: Path) -> str | None:
    return hashlib.md5(p.read_bytes()).hexdigest() if p.exists() else None


# ── antes de importar nada del pipeline: la foto de data/ y logs/ ──
VIGILADOS = [ROOT / "data", ROOT / "logs"]
ANTES = foto(VIGILADOS)
COST_HIST = ROOT / "data" / "cost_history.json"
COST_HIST_MD5 = md5f(COST_HIST)

# error_handler (lo importa cost_tracker, que importa claude_helpers) abre al importarse un FileHandler en
# logs/pipeline_<fecha>.log: escritura fuera de prueba1/. Se neutraliza ACÁ (no en el helper): durante el import el
# FileHandler es un NullHandler. cost_tracker solo escribe data/cost_history.json en end_video (que no se llama), y
# `_track` no se llama (lo llama m01e.llamar, que no se usa).
_FH = logging.FileHandler
logging.FileHandler = lambda *a, **k: logging.NullHandler()   # type: ignore[assignment,misc]
try:
    import claude_helpers as hx                                   # noqa: E402
    from script_engine import evidence as ev                       # noqa: E402
    from script_engine import m01e_pantalla as m01e                # noqa: E402
    from script_engine.pantalla_colocar import caracteres          # noqa: E402
    from script_engine.voz_utils import _palabra_en, _valor, nombres, numero_en, numeros   # noqa: E402
finally:
    logging.FileHandler = _FH
assert hasattr(hx, "_post")


def _hx_track_prohibido(*a, **k):                                 # por si algo lo llamara: no al ledger
    raise RuntimeError("prueba1: _track no se llama (nada al cost_tracker)")


hx._track = _hx_track_prohibido

PROMPT_MD = F38 / "PRUEBA1_prompt_rotulos.md"
RAW_B4 = F38 / "b4" / "01e_pantalla.raw.json"
PAPEL_B4 = F38 / "b4" / "01e_pantalla.json"
FASE1 = F38 / "b2" / "fase1"
OUT_RAW = HERE / "prueba1.raw.json"
OUT_TABLA = HERE / "TABLA.md"
OUT_LOG = HERE / "prueba1.log"

ANCLA_FMT = '"texto": "Más de 1 metro", '
INSERTO = '"respaldo": "…", '


def system_del_md() -> str:
    """El bloque «Prompt nuevo (m01e-6-prueba), entero»: lo que hay entre la línea ``` que sigue al título y la ```
    siguiente, tal cual (sin la nueva línea de antes del cierre)."""
    md = PROMPT_MD.read_text(encoding="utf-8")
    h = "## Prompt nuevo (m01e-6-prueba), entero\n"
    i = md.index(h) + len(h)
    a = md.index("```\n", i) + len("```\n")
    b = md.index("\n```", a)
    return md[a:b]


def formato() -> str:
    f = m01e.FORMATO_SALIDA
    if f.count(ANCLA_FMT) != 1:
        raise SystemExit(f"PARADA: la cadena {ANCLA_FMT!r} aparece {f.count(ANCLA_FMT)} veces en FORMATO_SALIDA")
    return f.replace(ANCLA_FMT, ANCLA_FMT + INSERTO, 1)


def entrada_completa(raw_b4: dict) -> dict:
    """La entrada del código reconstruida (cargar + entrada, con el seg y el vocabulario de b4) y `_pool` como generar."""
    papel = json.loads(PAPEL_B4.read_text(encoding="utf-8"))
    seg = papel["seg_por_palabra"]
    carga = m01e.cargar("f8s3-vajont", FASE1)
    ent = m01e.entrada(carga, vocabulario=list(raw_b4["entrada"]["clima"]), seg=seg)
    ent["_pool"] = carga["pool"]
    return ent


# ═══════════ verificación nueva (A.5) ═══════════
MULT = (("mil millones", 1e9), ("millones", 1e6), ("millon", 1e6), ("mil", 1e3))


def _valores(texto: str) -> list[tuple[str, float]]:
    """(cifra, valor) de un texto; si la cifra en dígitos va seguida de «mil / millones / mil millones», el valor se
    multiplica (para comparar «55.000 millones» con «55.645.758.500»)."""
    out = []
    n = ev.norm(texto)
    for x in numeros(texto):
        v = _valor(x)
        try:
            v = float(v)
        except (TypeError, ValueError):
            continue
        m = re.search(rf"(?<![\d.,]){re.escape(ev.norm(x))}(?![\d])\s+(\w+(?:\s+\w+)?)", n)
        if m:
            sig = m.group(1)
            for w, k in MULT:
                if sig == w or sig.startswith(w + " "):
                    v *= k
                    break
        out.append((x, v))
    return out


def verificar(fi: dict, x: dict | None, tipo: str) -> dict:
    """Por ficha: respaldo ✓/✗ (subcadena con ev.norm del texto del ítem; en citas, el dato mismo), cifras y nombres."""
    et, txt = str(fi.get("etiqueta") or ""), str(fi.get("texto") or "")
    resp = fi.get("respaldo")
    fuente = (x or {}).get("texto") or ""
    if not isinstance(resp, str) or not resp.strip():
        r_ok, r_por = False, "sin respaldo"
    elif x is None:
        r_ok, r_por = False, "el pool_id no está en el archivo"
    else:
        r_ok = ev.norm(resp) in ev.norm(fuente)
        r_por = "" if r_ok else "no es subcadena del texto del ítem"
    cita_ok = cita_sin_autor = None
    if tipo == "cita":
        d = re.sub(r"^[«\"“]+|[»\"”]+$", "", txt.strip()).strip()
        cita_ok = bool(d) and ev.norm(d) in ev.norm(fuente)
        if not cita_ok and re.search(r"\s[—–-]\s", txt):          # el modelo metió «— autor» dentro del dato
            d2 = re.sub(r"^[«\"“]+|[»\"”]+$", "", re.split(r"\s[—–-]\s", txt.strip())[0].strip()).strip()
            cita_sin_autor = bool(d2) and ev.norm(d2) in ev.norm(fuente)
    base = resp if isinstance(resp, str) else ""
    cifras = []
    vals_r = _valores(base)
    for campo, t in (("etiqueta", et), ("dato", txt)):
        for num, v in _valores(t):
            if numero_en(num, base):
                cifras.append({"cifra": num, "campo": campo, "es": "literal"})
                continue
            if not vals_r:
                cifras.append({"cifra": num, "campo": campo, "es": "no está"})
                continue
            rn, rv = min(vals_r, key=lambda p: abs(p[1] - v))
            pct = (v - rv) / rv * 100 if rv else float("inf")
            nt = ev.norm(t)
            redondeo = ("mas de" in nt and v < rv) or ("casi" in nt and v > rv)
            cifras.append({"cifra": num, "campo": campo, "es": f"redondeo ({pct:+.1f} %)" if redondeo else "no está",
                           "respaldo_cifra": rn, "dif_pct": round(pct, 2)})
    noms = [{"nombre": n, "ok": _palabra_en(n, base)} for n in nombres(et) + nombres(txt)]
    return {"respaldo_ok": r_ok, "respaldo_por": r_por, "cita_literal": cita_ok, "cita_sin_autor": cita_sin_autor,
            "cifras": cifras, "nombres": noms}


# ═══════════ tabla ═══════════
def _fichas(beats: list | None, arch: dict) -> dict[tuple[str, int], dict]:
    out = {}
    for b in beats or []:
        if isinstance(b, dict) and isinstance(b.get("ficha"), dict):
            out[(str(b.get("cap")), int(b.get("beat")))] = b["ficha"]
    return out


def _celda(fi: dict | None, arch: dict, autor_modelo: bool = False) -> str:
    if not fi:
        return "—"
    pid = fi.get("pool_id")
    s = f"{pid}: {fi.get('etiqueta')} · {fi.get('texto')}"
    if str(pid).startswith("Q"):
        if autor_modelo and fi.get("autor"):
            s += f" · {fi['autor']} (modelo)"
        elif not re.search(r"\s[—–-]\s", str(fi.get("texto") or "")):   # el autor no viene ya dentro del dato
            a = fi.get("autor") or (arch.get(pid) or {}).get("autor") or ""
            s += f" · {a}" + ("" if fi.get("autor") else " (archivo)")
    return s.replace("|", "/")


def tabla(raw: dict, ent: dict) -> str:
    arch = {x["id"]: x for x in ent["archivo"]}
    papel = json.loads(PAPEL_B4.read_text(encoding="utf-8"))
    raw_b4 = json.loads(RAW_B4.read_text(encoding="utf-8"))
    v6 = _fichas(papel["beats"], arch)
    i1 = _fichas((raw_b4["intentos"][0].get("respuesta") or {}).get("beats"), arch)
    nu = _fichas((raw.get("respuesta") or {}).get("beats"), arch)
    por = raw["por_ficha"]
    claves = sorted(set(v6) | set(i1) | set(nu), key=lambda k: (k[0], k[1]))
    L = ["# Prueba 1 — rótulos parafraseados (F38e-0 §A)", "",
         f"SYSTEM md5 `{raw['system_md5']}` · modelo {raw['modelo']} ({raw['effort']}) · una llamada"
         f"{' + 1 reintento' if len(raw['llamadas']) > 1 else ''}.", "",
         "| cap·beat | v6 hoy (etiqueta · dato · autor) | intento 1 de m01e-5 | NUEVO (etiqueta · dato · autor) | "
         "respaldo ✓/✗ | cifras | nombres | validar | car./caben | ¿se entiende solo? |",
         "|---|---|---|---|---|---|---|---|---|---|"]
    for k in claves:
        f = nu.get(k)
        p = por.get(f"{k[0]}·{k[1]}") if f else None
        if p:
            vr = p["verif"]
            rs = ("✓" if vr["respaldo_ok"] else f"✗ ({vr['respaldo_por']})") + \
                 (f" · respaldo: «{f.get('respaldo')}»" if f.get("respaldo") else "")
            if vr["cita_literal"] is not None:
                rs += f" · cita literal {'✓' if vr['cita_literal'] else '✗'}"
                if vr.get("cita_sin_autor") is not None:
                    rs += f" (el dato trae «— autor»; sin él: {'✓' if vr['cita_sin_autor'] else '✗'})"
            cf = "; ".join(f"{c['cifra']} {c['es']}" + (f" (resp. {c['respaldo_cifra']})" if c.get("respaldo_cifra")
                                                           and c["es"] != "literal" else "") for c in vr["cifras"]) or "—"
            nm = ", ".join(f"{n['nombre']} {'✓' if n['ok'] else '✗'}" for n in vr["nombres"]) or "—"
            va = p["validar"]
            if va["es"] == "corta":
                vs = f"corta ({va['regla']}: {va['motivo']})"
            elif va["es"] == "pregunta":
                vs = "pregunta (" + "; ".join(f"{q['regla']}: «{q['token']}»" for q in va["preguntas"]) + ")"
            else:
                vs = "queda"
            cc = f"{p['caracteres']}/{p['caben']}"
        else:
            rs = cf = nm = vs = cc = "—"
        row = [f"{k[0]}·{k[1]}", _celda(v6.get(k), arch), _celda(i1.get(k), arch), _celda(f, arch, True),
               rs, cf, nm, vs, cc, ""]
        L.append("| " + " | ".join(str(c).replace("|", "/").replace("\n", " ") for c in row) + " |")
    s6 = sum(1 for b in papel["beats"] if b.get("sello"))
    rn = raw.get("respuesta") or {}
    val = raw["validacion_resumen"]
    sn = sum(1 for b in rn.get("beats") or [] if isinstance(b, dict) and isinstance(b.get("sello"), dict))
    L += ["", "## Sellos y relojes (no se evalúan: solo que no se hayan roto)", "",
          "| | v6 hoy | NUEVO (respuesta) | NUEVO (quedan tras validar) |", "|---|---|---|---|",
          f"| sellos | {s6} | {sn} | {val['sellos_quedan']} |",
          f"| relojes | {len(papel['relojes'])} | {len(rn.get('relojes') or [])} | {val['relojes_ok']} (sin error) |",
          f"| fichas | {sum(1 for b in papel['beats'] if b.get('ficha'))} | "
          f"{sum(1 for b in rn.get('beats') or [] if isinstance(b, dict) and isinstance(b.get('ficha'), dict))} | "
          f"{val['fichas_quedan']} |", "",
          "Relojes v6: " + ", ".join(f"{r['cap']}[{r['sentence_idx']}] {r['fecha']}" for r in papel["relojes"]),
          "Relojes NUEVO: " + ", ".join(f"{r.get('cap')}[{r.get('sentence_idx')}] {r.get('fecha')}"
                                         for r in rn.get("relojes") or [] if isinstance(r, dict)),
          "Sellos v6: " + ", ".join(f"{b['cap']}·{b['beat']} {b['sello']['palabra']}" for b in papel["beats"]
                                     if b.get("sello")),
          "Sellos NUEVO: " + ", ".join(f"{b.get('cap')}·{b.get('beat')} {b['sello'].get('palabra')}"
                                        for b in rn.get("beats") or [] if isinstance(b, dict)
                                        and isinstance(b.get("sello"), dict)),
          "", "## Gasto", "",
          *[f"- llamada {i + 1}: in {c['usage'].get('input_tokens')} · out {c['usage'].get('output_tokens')} · "
            f"US$ {c['usd']:.4f} · {c['segundos']} s · stop {c['stop']} · {'JSON' if c['json'] else 'SIN JSON'}"
            for i, c in enumerate(raw["llamadas"])],
          f"- total US$ {raw['usd']:.4f} (claude_helpers.cost_of) · peor caso estimado antes US$ {raw['peor_usd']:.4f}",
          "", "Notas de lectura: «car./caben» con `pantalla_colocar.caracteres` (en una cita, autor del archivo + 5); "
          "«cifras» con `voz_utils.numeros` sobre etiqueta y dato (una cifra seguida de «mil/millones» se escala para "
          "comparar); «redondeo» = no literal y con «más de» (menor) o «casi» (mayor) en el mismo campo; «nombres» con "
          "`voz_utils.nombres` (no ve nombres en texto todo en mayúsculas ni el que abre el campo). «autor (archivo)» = "
          "el formato no tiene campo autor: es el del archivo; «(modelo)» = el modelo agregó `autor` a la ficha; si el "
          "dato ya trae «— autor» (lo metió el modelo), no se repite. En esas citas «car.» cuenta el autor dos veces (el "
          "del dato y el del archivo, como lo mide `caracteres`) y «nombres» mira también el autor metido en el dato. "
          "Ninguna ficha nueva trajo un campo `autor` propio."]
    return "\n".join(L) + "\n"


def evaluar(resp: dict | None, ent: dict) -> tuple[dict, dict]:
    val = m01e.validar(resp, ent, {}, final=False)
    arch = {x["id"]: x for x in ent["archivo"]}
    caps = {c["cap"]: c for c in ent["caps"]}
    quedan = {(s["cap"], s["beat"]): s for s in val["beats"]}
    por: dict[str, dict] = {}
    for b in (resp or {}).get("beats") or []:
        if not isinstance(b, dict) or not isinstance(b.get("ficha"), dict):
            continue
        fi, cap, nb = b["ficha"], str(b.get("cap")), b.get("beat")
        pid = str(fi.get("pool_id") or "")
        estilo = m01e.estilo_de(pid, str(fi.get("etiqueta") or ""), ent["a_pantalla"].get(pid, ""))
        tipo = m01e.TIPO_DE_ESTILO[estilo]
        q = quedan.get((cap, nb)) or {}
        fq = q.get("ficha") if (q.get("ficha") or {}).get("pool_id") == pid else None
        corte = next((d for d in val["descartados"] if d.get("quien") == "validación" and d.get("que") == "ficha"
                      and d.get("pool_id") == pid and d.get("cap") == cap and d.get("beat") == nb), None)
        if fq:
            va = {"es": "pregunta" if fq.get("pregunta") else "queda",
                  "preguntas": [{"regla": x["regla"], "token": x["token"]} for x in fq.get("pregunta") or []]}
        elif corte:
            va = {"es": "corta", "regla": corte["regla"], "motivo": corte["motivo"]}
        else:
            va = {"es": "corta", "regla": "?", "motivo": "no quedó y no hay descarte (fila repetida)"}
        c, si = caps.get(cap), m01e._int(fi.get("sentence_idx"))
        cab = c["oraciones"][si]["caben"] if c and si is not None and 0 <= si < len(c["oraciones"]) else None
        t = re.sub(r"^[«\"“]+|[»\"”]+$", "", str(fi.get("texto") or "").strip()).strip() if tipo == "cita" \
            else str(fi.get("texto") or "")
        n = caracteres(tipo, str(fi.get("etiqueta") or ""), t, str((arch.get(pid) or {}).get("autor") or ""))
        por[f"{cap}·{nb}"] = {"pool_id": pid, "estilo": estilo, "validar": va, "verif": verificar(fi, arch.get(pid), tipo),
                              "caracteres": n, "caben": cab}
    resumen = {"fichas_quedan": sum(1 for s in val["beats"] if s["ficha"]),
               "sellos_quedan": sum(1 for s in val["beats"] if s["sello"]),
               "relojes_ok": sum(1 for r in val["relojes"] if not r.get("error")),
               "fichas_fuera": val["fichas_fuera"], "preguntas": len(val["preguntas"]),
               "picos_vacios": val["picos_vacios"], "a_pantalla_vacios": val["a_pantalla_vacios"],
               "vuelven": [v["pool_id"] for v in val["vuelven"]],
               "sellos_cortados": [d for d in val["descartados"] if d.get("que") == "sello"]}
    return por, {"validacion": val, "resumen": resumen}


def main(argv: list[str]) -> int:
    seco, solo_tabla = "--seco" in argv, "--tabla" in argv
    log(f"# prueba1_rotulos · {time.strftime('%Y-%m-%d %H:%M:%S')} · {'SECO' if seco else 'TABLA' if solo_tabla else 'LLAMADA'}")
    system = system_del_md()
    s_md5 = hashlib.md5(system.encode("utf-8")).hexdigest()
    log(f"PRUEBA1_prompt_rotulos.md md5 {md5f(PROMPT_MD)}")
    log(f"SYSTEM: {len(system)} caracteres · md5 {s_md5} · empieza «{system[:40]}» · termina «{system[-60:]}»")
    fmt = formato()
    log("FORMATO con respaldo (resultado de la sustitución):")
    log(fmt)
    raw_b4 = json.loads(RAW_B4.read_text(encoding="utf-8"))
    ent = entrada_completa(raw_b4)
    pm = m01e._para_modelo(ent)
    igual = pm == raw_b4["entrada"]
    igual_txt = json.dumps(pm, ensure_ascii=False) == json.dumps(raw_b4["entrada"], ensure_ascii=False)
    log(f"_para_modelo(entrada reconstruida) == raw b4 `entrada`: dict {igual} · json {igual_txt}")
    if not (igual and igual_txt):
        log("PARADA: la entrada reconstruida no es idéntica a la de b4")
        return 2
    user = json.dumps(pm, ensure_ascii=False) + "\n\nFormato de salida: " + fmt
    body = {"model": m01e.MODELO, "max_tokens": hx.MAX_TOKENS, "system": system,
            "messages": [{"role": "user", "content": user}], "output_config": {"effort": m01e.EFFORT}}
    pin, pout = hx.PRICES.get(hx._base(m01e.MODELO), (0.0, 0.0))
    peor = m01e._peor_usd(len(json.dumps(body, ensure_ascii=False)), m01e.OUT_TOKENS_PEOR, pin, pout)
    log(f"body: model {body['model']} · max_tokens {body['max_tokens']} · effort {m01e.EFFORT} · USER {len(user)} car. · "
        f"peor caso US$ {peor:.4f} (m01e._peor_usd, salida {m01e.OUT_TOKENS_PEOR}, tarifas {pin}/{pout}) · "
        f"tope de la prueba {TOPE_PRUEBA}")
    if solo_tabla:                                       # US$ 0: re-evalúa la respuesta guardada y rehace la tabla
        raw = json.loads(OUT_RAW.read_text(encoding="utf-8"))
        por, ev_ = evaluar(raw["respuesta"], ent)
        raw["por_ficha"], raw["validacion_resumen"], raw["validacion"] = por, ev_["resumen"], ev_["validacion"]
        OUT_RAW.write_text(json.dumps(raw, ensure_ascii=False, indent=1), encoding="utf-8")
        OUT_TABLA.write_text(tabla(raw, ent), encoding="utf-8")
        log(f"tabla → {OUT_TABLA}")
        return 0
    if peor > TOPE_PRUEBA:
        log(f"PARADA: peor caso US$ {peor:.4f} > {TOPE_PRUEBA}: sin llamada")
        return 3
    if seco:
        return 0
    if OUT_RAW.exists():
        log("PARADA: ya hay prueba1.raw.json (una sola llamada): no se vuelve a llamar")
        return 4
    llamadas, resp = [], None
    for k in range(2):                                   # una + un único reintento si no trae JSON
        t0 = time.time()
        r = hx._post(body)
        u = r.get("usage") or {}
        usd = round(hx.cost_of(m01e.MODELO, u), 5)
        txt = "".join(c.get("text") or "" for c in r.get("content") or [] if c.get("type") == "text")
        resp = m01e.primer_json(txt)
        llamadas.append({"texto": txt, "usage": u, "stop": r.get("stop_reason"), "model": r.get("model"), "usd": usd,
                         "segundos": round(time.time() - t0, 1), "json": resp is not None})
        log(f"llamada {k + 1}: in {u.get('input_tokens')} · out {u.get('output_tokens')} · US$ {usd:.4f} · "
            f"{llamadas[-1]['segundos']} s · stop {r.get('stop_reason')} · {'JSON' if resp is not None else 'SIN JSON'}")
        if resp is not None:
            break
    raw = {"handoff": "F38e-0 §A", "modelo": m01e.MODELO, "effort": m01e.EFFORT, "max_tokens": hx.MAX_TOKENS,
           "system_md5": s_md5, "system": system, "formato": fmt, "user_md5": hashlib.md5(user.encode("utf-8")).hexdigest(),
           "entrada_igual_b4": True, "entrada_md5_b4": raw_b4.get("entrada_md5"), "peor_usd": round(peor, 5),
           "llamadas": llamadas, "usd": round(sum(c["usd"] for c in llamadas), 5),
           "tokens": {"in": sum(c["usage"].get("input_tokens") or 0 for c in llamadas),
                      "out": sum(c["usage"].get("output_tokens") or 0 for c in llamadas)},
           "respuesta": resp}
    if resp is None:
        OUT_RAW.write_text(json.dumps(raw, ensure_ascii=False, indent=1), encoding="utf-8")
        log("PARADA: dos respuestas sin JSON (crudo guardado en prueba1.raw.json)")
        return 5
    por, ev_ = evaluar(resp, ent)
    raw["por_ficha"] = por
    raw["validacion_resumen"] = ev_["resumen"]
    raw["validacion"] = ev_["validacion"]
    OUT_RAW.write_text(json.dumps(raw, ensure_ascii=False, indent=1), encoding="utf-8")
    OUT_TABLA.write_text(tabla(raw, ent), encoding="utf-8")
    log(f"US$ {raw['usd']:.4f} · tokens in {raw['tokens']['in']} out {raw['tokens']['out']}")
    log(f"validar: {json.dumps({k: v for k, v in ev_['resumen'].items() if k != 'sellos_cortados'}, ensure_ascii=False)}")
    for d in ev_["resumen"]["sellos_cortados"]:
        log(f"  sello cortado: {d.get('cap')}·{d.get('beat')} {d.get('texto')}: {d.get('motivo')}")
    return 0


if __name__ == "__main__":
    rc = 1
    try:
        rc = main(sys.argv[1:])
    finally:
        DESPUES = foto(VIGILADOS)
        cambios = sorted(k for k in set(ANTES) | set(DESPUES) if ANTES.get(k) != DESPUES.get(k))
        log(f"data/ y logs/: {len(ANTES)} archivos antes, {len(DESPUES)} después · cambiados/nuevos: {cambios or 'ninguno'}"
            f" · data/cost_history.json md5 {COST_HIST_MD5} → {md5f(COST_HIST)}")
        modo = "a" if OUT_LOG.exists() else "w"
        with OUT_LOG.open(modo, encoding="utf-8") as fh:
            fh.write("\n".join(LOG) + "\n\n")
    sys.exit(rc)
