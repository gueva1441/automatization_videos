"""F38e · Parte E (handoff HANDOFF_F38e_lo_que_rompe_cualquier_video.md §E): títulos de cap con el código nuevo.

1. Verifica por código que `m01d_particion.PEDIDO_TITULOS` es, byte a byte, el bloque «Pedido nuevo, entero» de
   lab/hyperframes/f38/PRUEBA2_prompt_titulos.md (md5 de los dos).
2. Lee (solo lee) la escaleta y el skeleton CONGELADOS de lab/hyperframes/f38/b2/fase1/f8s3-vajont/ y comprueba por md5
   que son iguales a los de data/scripts/_steps/f8s3-vajont/ (que no se abren para escribir).
3. Imprime el pedido entero tal como sale para Vajont (capturado con un `call` falso: sin red).
4. `--seco` para acá. Sin `--seco`: UNA llamada real, `m01d_particion.titles(esc)` tal cual (sin `call` inyectado), con
   los desvíos de la prueba 2: `_dump_invalid_json` a esta carpeta (único camino de call_flash_json que escribe en
   data/), sin start_video/end_video (cost_tracker solo escribe data/cost_history.json en end_video), y foto
   mtime+md5 de data/ antes y después.
5. Escribe E_SALIDA.md, e_titulos.raw.json y e_titulos.log acá. Nada en data/.
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
SECO = "--seco" in sys.argv
FROZEN = ROOT / "lab/hyperframes/f38/b2/fase1/f8s3-vajont"
ESC = FROZEN / "01a_escaleta.json"
SKEL = FROZEN / "01a_skeleton.json"
ESC_DATA = ROOT / "data/scripts/_steps/f8s3-vajont/01a_escaleta.json"
SKEL_DATA = ROOT / "data/scripts/_steps/f8s3-vajont/01a_skeleton.json"
MD = ROOT / "lab/hyperframes/f38/PRUEBA2_prompt_titulos.md"
DATA = ROOT / "data"

LOG = open(HERE / "e_titulos.log", "a", encoding="utf-8")
LOG.write(f"\n===== corrida {time.strftime('%Y-%m-%d %H:%M:%S')} · {'--seco' if SECO else 'llamada real'} =====\n")


def log(*a):
    s = " ".join(str(x) for x in a)
    print(s)
    LOG.write(s + "\n")
    LOG.flush()


def md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def md5s(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def data_snapshot() -> dict[str, tuple[float, str]]:
    out = {}
    for dp, _dn, fns in os.walk(DATA):
        for fn in fns:
            p = os.path.join(dp, fn)
            try:
                out[p] = (os.path.getmtime(p), md5(Path(p)))
            except OSError:
                pass
    return out


# ── 1. el literal del código = el bloque del md ──
md_text = MD.read_text(encoding="utf-8")
m = re.search(r"## Pedido nuevo, entero\n```\n(.*?)\n```", md_text, re.S)
assert m, "no encontré el bloque «Pedido nuevo, entero»"
bloque = m.group(1)
placeholders = sorted(set(re.findall(r"\{[^{}]*\}", bloque)))
assert placeholders == ["{TITLE_MAX_WORDS}", "{lines}"], placeholders

from script_engine import m01d_particion  # noqa: E402

log("md5 PRUEBA2_prompt_titulos.md:", md5(MD))
log(f"md5 bloque «Pedido nuevo, entero» del md: {md5s(bloque)} · {len(bloque)} car.")
log(f"md5 m01d_particion.PEDIDO_TITULOS:        {md5s(m01d_particion.PEDIDO_TITULOS)} · "
    f"{len(m01d_particion.PEDIDO_TITULOS)} car.")
assert bloque == m01d_particion.PEDIDO_TITULOS, "el literal del .py NO es el bloque del md"
log("literal del .py == bloque del md: True")
log("TITLE_MAX_WORDS =", m01d_particion.TITLE_MAX_WORDS)

# ── 2. escaleta congelada (lab) == data (solo lectura, por md5) ──
for a, b in ((ESC, ESC_DATA), (SKEL, SKEL_DATA)):
    log(f"md5 {a.relative_to(ROOT)}: {md5(a)} · data: {md5(b)} · iguales: {md5(a) == md5(b)}")
    assert md5(a) == md5(b)
esc = json.loads(ESC.read_text(encoding="utf-8"))
skel = json.loads(SKEL.read_text(encoding="utf-8"))
log("esc['pico'] =", json.dumps({k: v for k, v in (esc.get("pico") or {}).items() if k != "por_que"}, ensure_ascii=False),
    "· beats con campo `pico`:", [b["n"] for b in esc["beats"] if "pico" in b] or "ninguno")

# ── 3. el pedido entero tal como sale para Vajont (call falso: sin red) ──
capturado: dict = {}


def _captura(prompt, **kw):
    capturado["prompt"] = prompt
    capturado["kw"] = kw
    raise RuntimeError("captura: sin red")


m01d_particion.titles(esc, call=_captura)
pedido = capturado["prompt"]
assert capturado["kw"].get("response_schema") is m01d_particion.TITLES_SCHEMA
pedido_prueba2 = json.loads((ROOT / "lab/hyperframes/f38/prueba2/prueba2.raw.json").read_text(encoding="utf-8"))["pedido"]
diff_vs_p2 = [(i, a, b) for i, (a, b) in enumerate(zip(pedido.splitlines(), pedido_prueba2.splitlines()), 1) if a != b]
log(f"md5 pedido Vajont (código nuevo): {md5s(pedido)} · {len(pedido)} car.")
log(f"md5 pedido prueba 2:              {md5s(pedido_prueba2)} · {len(pedido_prueba2)} car.")
log("líneas distintas contra el pedido de la prueba 2:", diff_vs_p2 or "ninguna")
log("── PEDIDO ──\n" + pedido + "\n── fin PEDIDO ──")

if SECO:
    log("--seco: termina acá, sin llamada.")
    LOG.close()
    sys.exit(0)


# ── validación de hoy, copiada de titles() para la tabla (no está expuesta como función) ──
def limpiar(t) -> str:
    return str(t).strip().strip('".«»')


def valida(t: str) -> str:
    if t and len(t.split()) <= m01d_particion.TITLE_MAX_WORDS and not re.search(r"\d|\?", t):
        return "✓"
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
    return "✗ (" + ", ".join(why) + ")"


# ── 4. la llamada real: titles(esc) tal cual ──
import gemini_helpers  # noqa: E402
from cost_tracker import cost_tracker  # noqa: E402

desvios_dump: list[str] = []


def _dump_lab(raw_text, text, e, motivo=None):
    p = HERE / f"json_invalid_{time.strftime('%Y%m%d_%H%M%S')}.txt"
    p.write_text(f"{e}\nmotivo: {motivo}\n\n{raw_text}\n\n{text}\n", encoding="utf-8")
    desvios_dump.append(str(p))
    return f" | Dump (lab): {p}"


gemini_helpers._dump_invalid_json = _dump_lab   # desvío: el dump no va a data/_debug/
assert cost_tracker.current_video is None       # sin start_video: el gasto va a session_overhead (en memoria)

snap_antes = data_snapshot()
log("modelo Flash:", gemini_helpers._cfg.gemini_model, "· archivos en data/:", len(snap_antes))
n0 = len(cost_tracker.session_overhead)
t0 = time.time()
titulos, src = m01d_particion.titles(esc)
dt = time.time() - t0
entradas = cost_tracker.session_overhead[n0:]
usd = round(sum(e.total_cost for e in entradas), 6)
tok = [{"descripcion": e.description, "in": e.tokens_in, "out": e.tokens_out, "thinking": e.tokens_thinking,
        "usd": e.total_cost, "usage_ok": e.usage_ok} for e in entradas]
log(f"titles(esc) → src={src} · {len(titulos)} títulos · {dt:.1f} s · generaciones={len(entradas)} · US$ {usd} · {tok}")
log("títulos:", json.dumps(titulos, ensure_ascii=False))

snap_despues = data_snapshot()
tocados = sorted(p for p, v in snap_despues.items() if p not in snap_antes or v != snap_antes[p])
faltan = sorted(p for p in snap_antes if p not in snap_despues)
log(f"foto data/ antes: {len(snap_antes)} archivos · después: {len(snap_despues)} · nuevos o tocados (mtime o md5): "
    f"{tocados or 'ninguno'} · borrados: {faltan or 'ninguno'}")
log("dumps desviados al lab:", desvios_dump or "ninguno")

# ── 5. tabla y archivos ──
hoy = {c["chapter_number"]: c["title"] for c in skel["chapters"]}
filas = [f"| ch0{n} | {hoy.get(n, '—')} | {titulos[n - 1]} | {valida(titulos[n - 1])} |  |" for n in range(1, 8)]
tabla = "\n".join(["| cap | hoy (de 01a_skeleton.json congelado) | nuevo | validación | ¿promete sin contar el final? |",
                   "|---|---|---|---|---|", *filas])
log("\n" + tabla)

md_out = f"""# F38e · E — títulos de cap con `m01d_particion.titles()` nuevo (Flash, una llamada)

Escaleta: `lab/hyperframes/f38/b2/fase1/f8s3-vajont/01a_escaleta.json` (congelada; md5 `{md5(ESC)}`, igual a la de
`data/scripts/_steps/f8s3-vajont/`, que no se abre para escribir). Modelo: `{gemini_helpers._cfg.gemini_model}` vía
`titles(esc)` tal cual queda en el código (sin `call` inyectado). `src` = `{src}`. US$ {usd} ({tok}).
Validación = la de `titles()` (≤ {m01d_particion.TITLE_MAX_WORDS} palabras, sin dígito, sin «?», tras `strip().strip('".«»')`).

- Literal del código: md5 bloque del md `{md5s(bloque)}` = md5 `PEDIDO_TITULOS` `{md5s(m01d_particion.PEDIDO_TITULOS)}` ({len(bloque)} car.).
- Pedido de Vajont: md5 `{md5s(pedido)}` ({len(pedido)} car.); el de la prueba 2 era `{md5s(pedido_prueba2)}`. Líneas distintas: {diff_vs_p2 or 'ninguna'}.
- data/: {len(snap_antes)} archivos antes, {len(snap_despues)} después; nuevos o tocados (mtime o md5): {tocados or 'ninguno'}; dumps desviados: {desvios_dump or 'ninguno'}.

{tabla}

## Pedido entero, tal como sale para Vajont (md5 `{md5s(pedido)}`)

```
{pedido}
```
"""
(HERE / "E_SALIDA.md").write_text(md_out, encoding="utf-8")
(HERE / "e_titulos.raw.json").write_text(json.dumps({
    "fuente_pedido": {"md": str(MD.relative_to(ROOT)), "md5_md": md5(MD), "bloque": "Pedido nuevo, entero",
                      "md5_bloque": md5s(bloque), "md5_PEDIDO_TITULOS": md5s(m01d_particion.PEDIDO_TITULOS)},
    "escaleta": {"ruta": str(ESC.relative_to(ROOT)), "md5": md5(ESC), "md5_data": md5(ESC_DATA)},
    "TITLE_MAX_WORDS": m01d_particion.TITLE_MAX_WORDS, "modelo": gemini_helpers._cfg.gemini_model,
    "pedido": pedido, "md5_pedido": md5s(pedido), "md5_pedido_prueba2": md5s(pedido_prueba2), "diff_vs_prueba2": diff_vs_p2,
    "titulos": titulos, "src": src, "segundos": round(dt, 1), "usd": usd, "tokens": tok,
    "data_escrituras": {"antes": len(snap_antes), "despues": len(snap_despues), "nuevos_o_tocados": tocados,
                        "borrados": faltan, "dumps_desviados": desvios_dump},
}, ensure_ascii=False, indent=2), encoding="utf-8")
log("escrito: E_SALIDA.md, e_titulos.raw.json")
LOG.close()
