"""F38e §C.5 · la corrida del papel m01e-6 de Vajont fuera de data/ (lab, no pipeline).

Copia data/scripts/_steps/f8s3-vajont/ entera a c/vajont_steps/f8s3-vajont/ (solo lectura de data/) y corre ahí
m01e_pantalla.generar(topic, steps_dir=c/vajont_steps): el vocabulario de clima del perfil y `seg` derivado, como lo
hace generar. No llama a main() (escribe 01_v3_costos.json en data/ y start_video/end_video → data/cost_history.json).
El ledger: claude_helpers._track se desvía a un acumulador en memoria que suma claude_helpers.cost_of(model, usage) por
llamada (el gasto real se reporta de ahí); el tope de `llamar` sigue funcionando porque mide su propio `out["usd"]`
con la salida real. logging.FileHandler queda como NullHandler durante todo el proceso (error_handler abre un log en
logs/ al importarse; F38e-0 e11). Foto de data/ (mtime + md5) antes y después, pegada en el log.

    python lab/hyperframes/f38e/c/c_corrida.py --seco    # copia, entrada, peor caso: sin llamada
    python lab/hyperframes/f38e/c/c_corrida.py           # la corrida (se niega si ya hay c/01e_pantalla.raw.json)
    python lab/hyperframes/f38e/c/c_corrida.py --tabla   # rehace TABLA.md desde lo guardado (US$ 0)
"""
from __future__ import annotations

import sys
sys.dont_write_bytecode = True

import hashlib
import json
import logging
import re
import shutil
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
F38 = ROOT / "lab" / "hyperframes" / "f38"
TOPIC = "f8s3-vajont"
STEPS_DATA = ROOT / "data" / "scripts" / "_steps" / TOPIC
STEPS_LAB = HERE / "vajont_steps"
OUT_RAW = HERE / "01e_pantalla.raw.json"
OUT_PAPEL = HERE / "01e_pantalla.json"
OUT_MD = HERE / "01e_pantalla.md"
OUT_TABLA = HERE / "TABLA.md"
OUT_LOG = HERE / "c_corrida.log"
RAW_PRUEBA1 = F38 / "prueba1" / "prueba1.raw.json"
PAPEL_B4 = F38 / "b4" / "01e_pantalla.json"
MD5_SYSTEM = "7d2ccdd28055d6e621d1d251a0fe8bb7"
OUT_REAL_PRUEBA1 = 20_623                         # F38e-0 e4: la salida real de la prueba 1 (OUT_TOKENS_PEOR la subestima)
LOG: list[str] = []


def log(s: str = "") -> None:
    print(s, flush=True)
    LOG.append(s)


def foto(d: Path) -> dict[str, tuple[float, str]]:
    return {str(f.relative_to(ROOT)).replace("\\", "/"): (f.stat().st_mtime, hashlib.md5(f.read_bytes()).hexdigest())
            for f in sorted(d.rglob("*")) if f.is_file()}


ANTES = foto(ROOT / "data")
COST_HIST = ROOT / "data" / "cost_history.json"
LOGS_ANTES = {p.name for p in (ROOT / "logs").glob("*")} if (ROOT / "logs").exists() else set()

logging.FileHandler = lambda *a, **k: logging.NullHandler()   # type: ignore[assignment,misc]  todo el proceso
import claude_helpers as hx                                    # noqa: E402
from script_engine import evidence as ev                        # noqa: E402
from script_engine import m01e_pantalla as mp                   # noqa: E402
from script_engine.pantalla_colocar import caracteres           # noqa: E402
from script_engine.voz_utils import _palabra_en, _valor, nombres, numero_en, numeros   # noqa: E402

LEDGER: list[dict] = []


def _track_en_memoria(model: str, usage: dict, description: str) -> float:
    c = hx.cost_of(model, usage)
    LEDGER.append({"model": model, "usage": usage, "description": description, "usd": round(c, 5)})
    return c


hx._track = _track_en_memoria


# ═══════════ verificación por ficha (copia de prueba1_rotulos.verificar; el autor va aparte) ═══════════
MULT = (("mil millones", 1e9), ("millones", 1e6), ("millon", 1e6), ("mil", 1e3))


def _valores(texto: str) -> list[tuple[str, float]]:
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
    cita_ok = None
    if tipo == "cita":
        d = re.sub(r"^[«\"“]+|[»\"”]+$", "", txt.strip()).strip()
        cita_ok = bool(d) and ev.norm(d) in ev.norm(fuente)
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
    return {"respaldo_ok": r_ok, "respaldo_por": r_por, "cita_literal": cita_ok, "cifras": cifras, "nombres": noms}


# ═══════════ tabla ═══════════
def _fichas(beats: list | None) -> dict[tuple[str, int], dict]:
    out = {}
    for b in beats or []:
        if isinstance(b, dict) and isinstance(b.get("ficha"), dict):
            out[(str(b.get("cap")), int(b.get("beat")))] = b["ficha"]
    return out


def _celda_v6(fi: dict | None) -> str:
    if not fi:
        return "—"
    s = f"{fi.get('pool_id')}: {fi.get('etiqueta')} · {fi.get('texto')}"
    if fi.get("autor"):
        s += f" · {fi['autor']}"
    return s.replace("|", "/")


def _celda_p1(fi: dict | None, arch: dict) -> str:
    """Como prueba1._celda: el autor venía dentro del dato («— autor») o, si no, el del archivo."""
    if not fi:
        return "—"
    pid = fi.get("pool_id")
    s = f"{pid}: {fi.get('etiqueta')} · {fi.get('texto')}"
    if str(pid).startswith("Q") and not re.search(r"\s[—–-]\s", str(fi.get("texto") or "")):
        s += f" · {(arch.get(pid) or {}).get('autor') or ''} (archivo)"
    return s.replace("|", "/")


def _celda_nueva(fi: dict | None) -> str:
    if not fi:
        return "—"
    s = f"{fi.get('pool_id')}: {fi.get('etiqueta')} · {fi.get('texto')}"
    if fi.get("autor"):
        s += f" · autor del modelo: «{fi['autor']}»"
    return s.replace("|", "/")


def tabla(papel: dict, raw: dict, ent: dict) -> str:
    arch = {x["id"]: x for x in ent["archivo"]}
    caps = {c["cap"]: c for c in ent["caps"]}
    v6p = json.loads(PAPEL_B4.read_text(encoding="utf-8"))
    p1 = json.loads(RAW_PRUEBA1.read_text(encoding="utf-8"))
    v6 = _fichas(v6p["beats"])
    i1 = _fichas((p1.get("respuesta") or {}).get("beats"))
    final = raw.get("final") or {}
    nu = _fichas(final.get("beats"))                                  # lo que el autor dejó tras las vueltas
    quedan = {(b["cap"], b["beat"]): b["ficha"] for b in papel["beats"] if b.get("ficha")}
    cortes = [d for d in papel["descartados"] if d.get("quien") == "validación" and d.get("que") == "ficha"]
    claves = sorted(set(v6) | set(i1) | set(nu), key=lambda k: (k[0], k[1]))
    rt = papel.get("reintento") or {}
    L = ["# F38e §C — papel m01e-6 de Vajont con vueltas (contra v6 y la prueba 1)", "",
         f"SYSTEM md5 `{raw.get('system_md5')}` · prompt_md5 `{papel['prompt_md5']}` · {papel['modelo']} ({papel['effort']}) · "
         f"{papel['intentos']} llamada(s) = intento 1 + {len(rt.get('vueltas') or [])} vuelta(s) · cerró por "
         f"**{rt.get('cierre')}** · US$ {papel['usd']:.4f}.", "",
         "| cap·beat | v6 hoy (etiqueta · dato · autor) | prueba 1 | NUEVO m01e-6 con vueltas (etiqueta · dato · autor) | "
         "respaldo ✓/✗ | cifras | nombres | validar | car./caben | ¿se entiende solo? | autor mostrado | de dónde salió |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for k in claves:
        f = nu.get(k)
        if f:
            pid = str(f.get("pool_id") or "")
            x = arch.get(pid)
            estilo = mp.estilo_de(pid, str(f.get("etiqueta") or ""), ent["a_pantalla"].get(pid, ""))
            tipo = mp.TIPO_DE_ESTILO[estilo]
            vr = verificar(f, x, tipo)
            rs = ("✓" if vr["respaldo_ok"] else f"✗ ({vr['respaldo_por']})") + \
                 (f" · respaldo: «{f.get('respaldo')}»" if f.get("respaldo") else "")
            if vr["cita_literal"] is not None:
                rs += f" · cita literal {'✓' if vr['cita_literal'] else '✗'}"
            cf = "; ".join(f"{c['cifra']} {c['es']}" + (f" (resp. {c['respaldo_cifra']})" if c.get("respaldo_cifra")
                                                           and c["es"] != "literal" else "") for c in vr["cifras"]) or "—"
            nm = ", ".join(f"{n['nombre']} {'✓' if n['ok'] else '✗'}" for n in vr["nombres"]) or "—"
            q = quedan.get(k)
            if q and q.get("pool_id") == pid:
                vs = "queda" + (" (juzgado por el autor: " + json.dumps(q["juicio_autor"], ensure_ascii=False) + ")"
                                if q.get("juicio_autor") else "")
                cc = f"{q['caracteres']}/{q['caben']}"
                am, ao = (q.get("autor") or "—"), (q.get("autor_origen") or "—")
            else:
                d = next((d for d in cortes if d.get("pool_id") == pid and d.get("cap") == k[0] and d.get("beat") == k[1]),
                         None)
                vs = f"corta ({d['regla']}: {d['motivo']})" if d else "corta (?: sin descarte anotado)"
                c, si = caps.get(k[0]), mp._int(f.get("sentence_idx"))
                cab = c["oraciones"][si]["caben"] if c and si is not None and 0 <= si < len(c["oraciones"]) else "?"
                t = re.sub(r"^[«\"“]+|[»\"”]+$", "", str(f.get("texto") or "").strip()).strip() if tipo == "cita" \
                    else str(f.get("texto") or "")
                am, ao = (mp.autor_mostrado(str(f.get("autor") or ""), x) if tipo == "cita" and x else ("—", "—"))
                cc = f"{caracteres(tipo, str(f.get('etiqueta') or ''), t, am if tipo == 'cita' else '')}/{cab}"
            if tipo != "cita":
                am, ao = "—", "—"
        else:
            rs = cf = nm = vs = cc = am = ao = "—"
        row = [f"{k[0]}·{k[1]}", _celda_v6(v6.get(k)), _celda_p1(i1.get(k), arch), _celda_nueva(f),
               rs, cf, nm, vs, cc, "", am, ao]
        L.append("| " + " | ".join(str(c).replace("|", "/").replace("\n", " ") for c in row) + " |")
    # aparte
    s6 = sum(1 for b in v6p["beats"] if b.get("sello"))
    sn_resp = sum(1 for b in final.get("beats") or [] if isinstance(b, dict) and isinstance(b.get("sello"), dict))
    sn_q = sum(1 for b in papel["beats"] if b.get("sello"))
    fn_resp = len(nu)
    fn_q = len(quedan)
    rel_resp = [r for r in final.get("relojes") or [] if isinstance(r, dict)]
    rel_ok = sum(1 for r in papel["relojes"] if not r.get("error"))
    L += ["", "## Las 3 citas (Q50, Q51, Q14): ¿entran ahora?", ""]
    for pid in ("Q50", "Q51", "Q14"):
        k = next((k for k, f in nu.items() if f.get("pool_id") == pid), None)
        q = next((q for q in quedan.values() if q.get("pool_id") == pid), None)
        if q:
            L.append(f"- {pid}: **entra** en {k[0]} beat {k[1]} [{q['sentence_idx']}] «{q['etiqueta']} · {q['texto']}» — "
                     f"{q.get('autor')} (autor: {q.get('autor_origen')}) · {q['caracteres']}/{q['caben']} car.")
        elif k:
            f = nu[k]
            d = next((d for d in cortes if d.get("pool_id") == pid), None)
            L.append(f"- {pid}: la propuso en {k[0]} beat {k[1]} «{f.get('etiqueta')} · {f.get('texto')}» (autor del "
                     f"modelo «{f.get('autor')}») y **cayó**: {d['regla']}: {d['motivo']}" if d else
                     f"- {pid}: la propuso en {k[0]} beat {k[1]} y no quedó (sin descarte anotado)")
        else:
            dm = next((d for d in papel["descartados"] if d.get("pool_id") == pid and d.get("quien") == "modelo"), None)
            L.append(f"- {pid}: **no la propuso** en el papel final" + (f" (la descartó: [{dm.get('tipo')}] {dm.get('motivo')})"
                                                                     if dm else ""))
    L += ["", "## Vueltas y gasto", "",
          f"- llamadas: {papel['intentos']} (intento 1 + {len(rt.get('vueltas') or [])} vuelta(s)) · cerró por "
          f"**{rt.get('cierre')}** · tope US$ {papel['tope']['usd']} ({papel['tope']['de']})"
          + (f" · error/aviso: {papel['error']}" if papel.get("error") else "")]
    for i, it in enumerate(papel.get("por_intento") or []):
        L.append(f"- {'intento 1' if i == 0 else f'vuelta {i}'}: in {it['tokens_in']} · out {it['tokens_out']} · "
                 f"US$ {it['usd']:.4f} · {it['segundos']} s")
    L.append(f"- total US$ {papel['usd']:.4f} (suma de cost_of por llamada; ledger en memoria: "
             f"US$ {sum(e['usd'] for e in LEDGER) if LEDGER else raw.get('usd_ledger', 0):.4f}) · peor caso estimado antes de "
             f"llamar: US$ {raw.get('peor_usd_estimado', 0):.4f} (OUT_TOKENS_PEOR {mp.OUT_TOKENS_PEOR}) / "
             f"US$ {raw.get('peor_usd_estimado_20623', 0):.4f} (salida {OUT_REAL_PRUEBA1}, e4)")
    for vu in rt.get("vueltas") or []:
        L.append(f"- vuelta {vu['vuelta']}: beats {', '.join(f'{c} b{b}' for c, b in vu['beats'])} · {len(vu['motivos'])} "
                 f"motivo(s) · {len(vu['aplicados'])} aplicado(s) · {len(vu['ignorados'])} ignorado(s) · US$ {vu['usd']:.4f}"
                 + (" · SIN JSON" if vu.get("sin_json") else ""))
        for m in vu["motivos"]:
            L.append(f"  - {m}")
    if rt.get("cortados_al_cierre"):
        L.append("- cortado al cerrar sin preguntar: " + "; ".join(
            f"{d.get('pool_id')} ({d.get('cap')} b{d.get('beat')}) {d.get('regla')}: {d.get('motivo')}"
            for d in rt["cortados_al_cierre"]))
    else:
        L.append("- cortado al cerrar sin preguntar: nada")
    L += ["", "## Sellos y relojes (no se evalúan: solo que no se hayan roto)", "",
          "| | v6 hoy | NUEVO (respuesta final del autor) | NUEVO (quedan tras validar) |", "|---|---|---|---|",
          f"| sellos | {s6} | {sn_resp} | {sn_q} |",
          f"| relojes | {len(v6p['relojes'])} | {len(rel_resp)} | {rel_ok} (sin error) |",
          f"| fichas | {sum(1 for b in v6p['beats'] if b.get('ficha'))} | {fn_resp} | {fn_q} |", "",
          "Relojes v6: " + ", ".join(f"{r['cap']}[{r['sentence_idx']}] {r['fecha']}" for r in v6p["relojes"]),
          "Relojes NUEVO: " + ", ".join(f"{r.get('cap')}[{r.get('sentence_idx')}] {r.get('fecha')}" for r in rel_resp),
          "Sellos v6: " + ", ".join(f"{b['cap']}·{b['beat']} {b['sello']['palabra']}" for b in v6p["beats"] if b.get("sello")),
          "Sellos NUEVO (quedan): " + ", ".join(f"{b['cap']}·{b['beat']} {b['sello']['palabra']}" for b in papel["beats"]
                                                 if b.get("sello")),
          "", "## Picos y a_pantalla", "",
          "- picos: " + ", ".join(f"{b['cap']}·{b['beat']} {'CON ficha ' + b['ficha']['pool_id'] if b.get('ficha') else 'SIN ficha'}"
                                  for b in papel["beats"] if b.get("pico")),
          f"- picos vacíos: {papel.get('picos_vacios') or 'ninguno'}",
          "- `a_pantalla` de la escaleta: " + ", ".join(
              f"{x['id']} (beat {x['a_pantalla']['beat']}): "
              + ("presente" if any(q.get("pool_id") == x["id"] for q in quedan.values()) else "ausente")
              for x in ent["archivo"] if x.get("a_pantalla")),
          f"- a_pantalla_vacios: {papel.get('a_pantalla_vacios') or 'ninguno'}",
          "", "Notas de lectura: «car./caben» con `pantalla_colocar.caracteres` (en una cita, con el autor que se muestra "
          "+ 5); «cifras» y «nombres» como en la prueba 1 (`verificar` copiado de prueba1_rotulos.py: una cifra seguida "
          "de «mil/millones» se escala; «redondeo» = «más de» (menor) o «casi» (mayor) en el campo; `nombres` no ve el que "
          "abre el campo ni texto en mayúsculas); el autor va en su columna (modelo / archivo: motivo). «prueba 1» = la "
          "respuesta de prueba1.raw.json (sin campo autor: el que figura es el del dato o el del archivo). «NUEVO» = la "
          "respuesta final tras las vueltas (`final` del raw); «validar» = lo que hizo la validación final."]
    return "\n".join(L) + "\n"


def peor_caso(ent: dict) -> tuple[float, float, float, float]:
    user = mp.pedido(ent)
    body = {"model": mp.MODELO, "max_tokens": hx.MAX_TOKENS, "system": mp.PANTALLA_SYSTEM,
            "messages": [{"role": "user", "content": user}], "output_config": {"effort": mp.EFFORT}}
    pin, pout = hx.PRICES.get(hx._base(mp.MODELO), (0.0, 0.0))
    n = len(json.dumps(body, ensure_ascii=False))
    p16 = mp._peor_usd(n, mp.OUT_TOKENS_PEOR, pin, pout)
    p20 = mp._peor_usd(n, OUT_REAL_PRUEBA1, pin, pout)
    # una vuelta: el USER + la respuesta anterior (la de la prueba 1 como medida) + motivos (~40 líneas) + formato
    p1 = json.loads(RAW_PRUEBA1.read_text(encoding="utf-8"))
    ped_v = mp._reintento_parcial(user, p1["respuesta"], ["x" * 150] * 20, [("ch01", 1)])
    nv = len(json.dumps({**body, "messages": [{"role": "user", "content": ped_v}]}, ensure_ascii=False))
    v16 = mp._peor_usd(nv, mp.OUT_TOKENS_PEOR, pin, pout)
    v20 = mp._peor_usd(nv, OUT_REAL_PRUEBA1, pin, pout)
    log(f"USER {len(user)} car. · body {n} car. · tarifas {pin}/{pout} · tope {mp.tope_usd()}")
    log(f"peor caso intento 1: US$ {p16:.4f} (salida {mp.OUT_TOKENS_PEOR}) / US$ {p20:.4f} (salida {OUT_REAL_PRUEBA1}, e4)")
    log(f"peor caso una vuelta (USER + papel anterior como el de la prueba 1): US$ {v16:.4f} / US$ {v20:.4f}")
    log(f"con el tope 1,00 y la lógica de `llamar` (gastado + peor ≤ tope): entra el intento 1; la vuelta 1 entra si "
        f"gastó ≤ {1.0 - v16:.4f}; la vuelta 2 entra si gastó ≤ {1.0 - v16:.4f} tras dos llamadas (~{2 * 0.34:.2f} real → no)")
    return p16, p20, v16, v20


def main(argv: list[str]) -> int:
    seco, solo_tabla = "--seco" in argv, "--tabla" in argv
    log(f"# c_corrida · {time.strftime('%Y-%m-%d %H:%M:%S')} · {'SECO' if seco else 'TABLA' if solo_tabla else 'CORRIDA'}")
    s_md5 = hashlib.md5(mp.PANTALLA_SYSTEM.encode("utf-8")).hexdigest()
    log(f"m01e {mp.PROMPT_VERSION} · md5 SYSTEM {s_md5} ({'OK' if s_md5 == MD5_SYSTEM else 'NO COINCIDE'}) · "
        f"prompt_md5 {mp.prompt_md5()} · modelo {mp.MODELO} {mp.EFFORT}")
    if s_md5 != MD5_SYSTEM:
        log("PARADA: el SYSTEM no es el de la prueba 1")
        return 2
    dst = STEPS_LAB / TOPIC
    if not dst.exists():
        shutil.copytree(STEPS_DATA, dst)
        log(f"copiado data/scripts/_steps/{TOPIC}/ → {dst.relative_to(ROOT)} ({sum(1 for _ in dst.rglob('*') if _.is_file())} archivos)")
    else:
        log(f"{dst.relative_to(ROOT)} ya existe: no se vuelve a copiar")
    from script_engine.clima import vocabulario_clima
    carga = mp.cargar(TOPIC, STEPS_LAB)
    ent = mp.entrada(carga, vocabulario_clima())
    ent["_pool"] = carga["pool"]
    log(f"entrada: {len(ent['caps'])} caps · {len(ent['beats'])} beats · archivo {len(ent['archivo'])} ítems · clima "
        f"{ent['clima']} · seg {ent['seg_por_palabra']} · entrada_md5 {mp.entrada_md5(ent)}")
    p16, p20, v16, v20 = peor_caso(ent)
    if solo_tabla:
        raw = json.loads(OUT_RAW.read_text(encoding="utf-8"))
        papel = json.loads(OUT_PAPEL.read_text(encoding="utf-8"))
        OUT_TABLA.write_text(tabla(papel, raw, ent), encoding="utf-8")
        log(f"tabla → {OUT_TABLA}")
        return 0
    if seco:
        return 0
    if OUT_RAW.exists():
        log("PARADA: ya hay c/01e_pantalla.raw.json (una sola corrida): no se vuelve a llamar")
        return 4
    glog: list[str] = []
    t0 = time.time()
    try:
        papel = mp.generar(TOPIC, steps_dir=STEPS_LAB, log=glog)
    except (mp.SinJSON, mp.TopePantalla) as e:
        log("\n".join(glog))
        log(f"PARADA: {e}")
        return 5
    log("\n".join(glog))
    log(f"generar: {time.time() - t0:.1f} s")
    raw = json.loads((dst / f"{mp.ARCHIVO}.raw.json").read_text(encoding="utf-8"))
    raw["system_md5"] = s_md5
    raw["peor_usd_estimado"], raw["peor_usd_estimado_20623"] = round(p16, 5), round(p20, 5)
    raw["peor_usd_vuelta"], raw["peor_usd_vuelta_20623"] = round(v16, 5), round(v20, 5)
    raw["ledger_memoria"] = LEDGER
    raw["usd_ledger"] = round(sum(e["usd"] for e in LEDGER), 5)
    OUT_RAW.write_text(json.dumps(raw, ensure_ascii=False, indent=1), encoding="utf-8")
    shutil.copy2(dst / f"{mp.ARCHIVO}.json", OUT_PAPEL)
    shutil.copy2(dst / f"{mp.ARCHIVO}.md", OUT_MD)
    for i, it in enumerate(raw["intentos"]):
        u = it.get("usage") or {}
        log(f"{'intento 1' if i == 0 else f'vuelta {i}'}: in {u.get('input_tokens')} · out {u.get('output_tokens')} · "
            f"US$ {it['usd']:.4f} · {it['segundos']} s · stop {it.get('stop')} · {'JSON' if it.get('respuesta') is not None else 'SIN JSON'}")
    log(f"US$ total {raw['usd']:.4f} (llamar) · ledger en memoria US$ {raw['usd_ledger']:.4f} ({len(LEDGER)} entradas) · "
        f"cierre {raw['reintento'].get('cierre')} · vueltas {len(raw['reintento'].get('vueltas') or [])}")
    OUT_TABLA.write_text(tabla(papel, raw, ent), encoding="utf-8")
    log(f"tabla → {OUT_TABLA}")
    return 0


if __name__ == "__main__":
    rc = 1
    try:
        rc = main(sys.argv[1:])
    finally:
        DESPUES = foto(ROOT / "data")
        cambios = sorted(k for k in set(ANTES) | set(DESPUES) if ANTES.get(k) != DESPUES.get(k))
        logs_nuevos = sorted(({p.name for p in (ROOT / "logs").glob("*")} if (ROOT / "logs").exists() else set()) - LOGS_ANTES)
        log(f"data/: {len(ANTES)} archivos antes, {len(DESPUES)} después (mtime + md5) · cambiados/nuevos: "
            f"{cambios or 'ninguno'} · cost_history.json md5 {ANTES.get('data/cost_history.json', (0, '?'))[1]} → "
            f"{DESPUES.get('data/cost_history.json', (0, '?'))[1]} · logs/ nuevos: {logs_nuevos or 'ninguno'}")
        with OUT_LOG.open("a" if OUT_LOG.exists() else "w", encoding="utf-8") as fh:
            fh.write("\n".join(LOG) + "\n\n")
    sys.exit(rc)
