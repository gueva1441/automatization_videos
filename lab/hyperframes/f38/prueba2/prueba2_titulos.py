"""F38e-0 · Prueba 2 (parte B del handoff HANDOFF_F38e0_pruebas_en_seco.md): títulos de cap en seco.

Lee (solo lee) la escaleta y el skeleton de f8s3-vajont, arma `lines` como dice B.2, toma el pedido del bloque
«Pedido nuevo, entero» de PRUEBA2_prompt_titulos.md (extraído por código), hace TRES llamadas a Flash con el mismo
pedido y escribe prueba2.raw.json y TABLA.md en esta carpeta. No toca el pipeline: solo importa.

Escrituras en data/: el único camino de call_flash_json que escribe en data/ es `_dump_invalid_json` (data/_debug/,
solo si el JSON sale roto tres veces); se redirige por monkeypatch a esta carpeta. cost_tracker solo escribe
data/cost_history.json en end_video() (acá no hay start_video/end_video): se mide md5/mtime antes y después igual.
"""
from __future__ import annotations

import hashlib
import json
import os
import re
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
HERE = Path(__file__).resolve().parent
ESC = ROOT / "data/scripts/_steps/f8s3-vajont/01a_escaleta.json"
SKEL = ROOT / "data/scripts/_steps/f8s3-vajont/01a_skeleton.json"
MD = ROOT / "lab/hyperframes/f38/PRUEBA2_prompt_titulos.md"
DATA = ROOT / "data"
N_CALLS = 3
FRENO_USD = 0.10

LOG = open(HERE / "prueba2.log", "w", encoding="utf-8")


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LOG.write(s + "\n")
    LOG.flush()


def md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def data_snapshot() -> dict[str, float]:
    out = {}
    for dp, _dn, fns in os.walk(DATA):
        for fn in fns:
            p = os.path.join(dp, fn)
            try:
                out[p] = os.path.getmtime(p)
            except OSError:
                pass
    return out


# ── pedido: bloque «Pedido nuevo, entero» del md, sin reescribir ──
md_text = MD.read_text(encoding="utf-8")
m = re.search(r"## Pedido nuevo, entero\n```\n(.*?)\n```", md_text, re.S)
assert m, "no encontré el bloque «Pedido nuevo, entero»"
plantilla = m.group(1)
placeholders = sorted(set(re.findall(r"\{[^{}]*\}", plantilla)))
log("md5 PRUEBA2_prompt_titulos.md:", md5(MD))
log("placeholders en la plantilla:", placeholders)
assert placeholders == ["{TITLE_MAX_WORDS}", "{lines}"], placeholders

from script_engine import m01d_particion  # noqa: E402

esc = json.loads(ESC.read_text(encoding="utf-8"))
skel = json.loads(SKEL.read_text(encoding="utf-8"))

# ── lines, exactamente como B.2 del handoff (= la forma del md) ──
by_cap = {n: [b for b in esc["beats"] if b["cap"] == n] for n in range(1, 8)}
sin_campo_pico = [b["n"] for b in esc["beats"] if "pico" not in b]
out_lines = []
for n in range(1, 8):
    out_lines.append(f"CAP {n}:")
    for b in by_cap[n]:
        marca = " · pico" if b.get("pico") else ""   # `pico` = el campo `pico` del beat (B.2)
        out_lines.append(f"  beat {b['n']} {b.get('funcion')}{marca}: se ve: {b.get('imagen_sensorial')} · "
                         f"pregunta que abre: {b.get('pregunta_abierta')}")
    out_lines.append(f"  termina (no lo cuentes): {by_cap[n][-1].get('cierre')}")
lines = "\n".join(out_lines)
log(f"beats sin campo `pico`: {len(sin_campo_pico)}/{len(esc['beats'])} · esc['pico'] =",
    json.dumps({k: v for k, v in (esc.get('pico') or {}).items() if k != 'por_que'}, ensure_ascii=False))

pedido = plantilla.replace("{TITLE_MAX_WORDS}", str(m01d_particion.TITLE_MAX_WORDS)).replace("{lines}", lines)
log("TITLE_MAX_WORDS =", m01d_particion.TITLE_MAX_WORDS)
log("md5 pedido:", hashlib.md5(pedido.encode("utf-8")).hexdigest(), f"· {len(pedido)} car.")
log("── PEDIDO ──\n" + pedido + "\n── fin PEDIDO ──")


# ── validación de hoy: copia exacta de la de m01d_particion.titles() (no está expuesta como función) ──
def limpiar(t) -> str:
    return str(t).strip().strip('".«»')


def valida(t: str) -> tuple[bool, str]:
    ok = bool(t and len(t.split()) <= m01d_particion.TITLE_MAX_WORDS and not re.search(r"\d|\?", t))
    if ok:
        return True, "✓"
    why = []
    if not t:
        why.append("vacío")
    else:
        if len(t.split()) > m01d_particion.TITLE_MAX_WORDS:
            why.append(f"{len(t.split())} palabras")
        if re.search(r"\d", t):
            why.append("dígito")
        if "?" in t:
            why.append("«?»")
    return False, "✗ (" + ", ".join(why) + ")"


# ── llamadas ──
import gemini_helpers  # noqa: E402
from cost_tracker import cost_tracker  # noqa: E402

desvios_dump = []


def _dump_lab(raw_text, text, e, motivo=None):
    p = HERE / f"json_invalid_{time.strftime('%Y%m%d_%H%M%S')}.txt"
    p.write_text(f"{e}\nmotivo: {motivo}\n\n{raw_text}\n\n{text}\n", encoding="utf-8")
    desvios_dump.append(str(p))
    return f" | Dump (lab): {p}"


gemini_helpers._dump_invalid_json = _dump_lab   # monkeypatch: el dump no va a data/_debug/

hist = DATA / "cost_history.json"
hist_antes = (md5(hist), os.path.getmtime(hist)) if hist.exists() else None
snap_antes = data_snapshot()
t0 = time.time()
log("modelo Flash:", gemini_helpers._cfg.gemini_model)

llamadas = []
for i in range(1, N_CALLS + 1):
    n0 = len(cost_tracker.session_overhead)
    try:
        raw = gemini_helpers.call_flash_json(pedido, response_schema=m01d_particion.TITLES_SCHEMA,
                                            description="prueba2: títulos")
        err = None
    except Exception as ex:  # noqa: BLE001
        raw, err = None, repr(ex)
    entradas = cost_tracker.session_overhead[n0:]
    usd = sum(e.total_cost for e in entradas)
    tok = [{"in": e.tokens_in, "out": e.tokens_out, "thinking": e.tokens_thinking, "usd": e.total_cost,
            "usage_ok": e.usage_ok} for e in entradas]
    llamadas.append({"llamada": i, "respuesta": raw, "error": err, "generaciones": len(entradas), "tokens": tok,
                     "usd": round(usd, 6)})
    log(f"llamada {i}: {json.dumps(raw, ensure_ascii=False)} · err={err} · gen={len(entradas)} · US$ {usd:.6f} · {tok}")
    total = sum(x["usd"] for x in llamadas)
    if total > FRENO_USD:
        log(f"FRENO: gasto {total:.4f} > {FRENO_USD}")
        break

usd_total = round(sum(x["usd"] for x in llamadas), 6)

# ── ¿alguien escribió en data/? ──
hist_despues = (md5(hist), os.path.getmtime(hist)) if hist.exists() else None
snap_despues = data_snapshot()
nuevos_o_tocados = sorted(p for p, mt in snap_despues.items() if p not in snap_antes or mt != snap_antes[p])
log("cost_history.json antes:", hist_antes, "después:", hist_despues, "· igual:", hist_antes == hist_despues)
log("archivos de data/ nuevos o tocados durante la corrida:", nuevos_o_tocados or "ninguno")
log("dumps desviados al lab:", desvios_dump or "ninguno")
log(f"US$ total: {usd_total}")

# ── tabla ──
hoy = {c["chapter_number"]: c["title"] for c in skel["chapters"]}
cols = []
for x in llamadas:
    ts = [limpiar(t) for t in ((x["respuesta"] or {}).get("titulos") or [])]
    cols.append(ts)
filas = []
for n in range(1, 8):
    nuevos, vals = [], []
    for j, ts in enumerate(cols, 1):
        t = ts[n - 1] if len(ts) >= n else ""
        nuevos.append(t or "—")
        vals.append(f"{j}{valida(t)[1]}")
    filas.append(f"| ch0{n} | {hoy.get(n, '—')} | " + " | ".join(nuevos) + " | " + " · ".join(vals) + " |  |")
cuantos = " · ".join(f"llamada {j}: {len(ts)} títulos" for j, ts in enumerate(cols, 1))
tabla = "\n".join([
    "| cap | hoy (de 01a_skeleton.json) | nuevo 1 | nuevo 2 | nuevo 3 | validación | ¿promete sin contar el final? |",
    "|---|---|---|---|---|---|---|",
    *filas,
])

md_out = f"""# F38e-0 · Prueba 2 — títulos de cap (Flash, en seco)

Escaleta: `data/scripts/_steps/f8s3-vajont/01a_escaleta.json` (solo lectura). Modelo: `{gemini_helpers._cfg.gemini_model}` vía
`call_flash_json(pedido, response_schema=m01d_particion.TITLES_SCHEMA, description="prueba2: títulos")`, {len(llamadas)} llamadas con el mismo pedido.
Validación = la de `m01d_particion.titles()` (≤ {m01d_particion.TITLE_MAX_WORDS} palabras, sin dígito, sin «?», tras `strip().strip('".«»')`), por llamada (1/2/3).
Cantidad de títulos por llamada (titles() exige 7): {cuantos}. US$ total: {usd_total}.

{tabla}

## Pedido entero, tal como se mandó (md5 `{hashlib.md5(pedido.encode('utf-8')).hexdigest()}`)

```
{pedido}
```
"""
(HERE / "TABLA.md").write_text(md_out, encoding="utf-8")

(HERE / "prueba2.raw.json").write_text(json.dumps({
    "fuente_pedido": {"md": str(MD.relative_to(ROOT)), "md5_md": md5(MD), "bloque": "Pedido nuevo, entero",
                      "plantilla": plantilla},
    "TITLE_MAX_WORDS": m01d_particion.TITLE_MAX_WORDS,
    "modelo": gemini_helpers._cfg.gemini_model,
    "beats_sin_campo_pico": sin_campo_pico,
    "esc_pico": esc.get("pico"),
    "pedido": pedido,
    "md5_pedido": hashlib.md5(pedido.encode("utf-8")).hexdigest(),
    "llamadas": llamadas,
    "usd_total": usd_total,
    "data_escrituras": {"cost_history_antes": hist_antes, "cost_history_despues": hist_despues,
                        "nuevos_o_tocados": nuevos_o_tocados, "dumps_desviados": desvios_dump},
}, ensure_ascii=False, indent=2), encoding="utf-8")
log("\n" + tabla)
LOG.close()
