# -*- coding: utf-8 -*-
"""F52 etapa 2 — los 8 prompts de video en texto: por modelo (K, S, F, G) y clip (cap 1, cap 7), UNA llamada a Opus 5.5
(effort high, como `m03:casilleros`) con el pedido del handoff tal cual: la ficha de guía del modelo
(`f52/guias/<letra>.md`) + el prompt de la foto (`image_prompt` del cap), la oración ancla de la voz
(`narration_anchor`) y el `video_prompt` vivo del 03_visual.json de F51f como movimiento ya aprobado. Las 8 llamadas
en paralelo. No toca producción: usa las piezas de `claude_helpers` (`_post`, `_track`) para una salida de texto (no
JSON). Costo por `cost_tracker` (video_id `f52_lab_prompts`). Salida: `f52/PROMPTS_F52.md` y `f52/prompts_f52.json`.

Uso: python lab/hyperframes/f52/prompts_video.py
"""
import hashlib
import json
import re
import sys
import time
import urllib.error
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
F52 = Path(__file__).resolve().parent
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
VISUAL = ROOT / "data" / "scripts" / "_steps" / TID / "03_visual.json"
MD5_VISUAL = "0d57b6bad197cae073c9c88596ed6130"
MODELO, ESFUERZO = "claude-opus-5-5", "high"           # = m03:casilleros (MODELO_CASILLEROS, guion_v4.ESFUERZO)
MODELOS = {"K": "Kling 4.0", "S": "Seedance 2.5", "F": "FLUX 3 Max", "G": "Gemini Omni Flash 1.1"}
INTENTOS_RED = 2                                       # solo errores de red/429/5xx (respuesta no cobrada)

# El pedido a Opus del handoff F52, completo, sin ajustar.
PEDIDO = """You write the motion prompt for an image-to-video model. The still image is the first frame. Follow the model guide below exactly; it decides structure, length and closing lines.
MODEL GUIDE:
{ficha}
STILL IMAGE PROMPT (what the first frame shows):
{prompt_foto}
NARRATION AT THIS MOMENT:
{ancla}
APPROVED MOTION (keep its intent, rewrite it for this model):
{video_prompt_vivo}
Clip length: 8 seconds, one continuous shot, no cuts, no dialogue, no music, no on-screen text.
Return only the prompt text."""


def llamar(texto: str, desc: str) -> tuple[str, dict]:
    import claude_helpers as ch
    body = {"model": MODELO, "max_tokens": ch.MAX_TOKENS, "messages": [{"role": "user", "content": texto}],
            "output_config": {"effort": ESFUERZO}}
    last = ""
    for intento in range(1, INTENTOS_RED + 1):
        try:
            r = ch._post(body)
        except urllib.error.HTTPError as e:
            last = f"HTTP {e.code}: {e.read().decode('utf-8', 'replace')[:300]}"
            if e.code in (408, 429, 529) or e.code >= 500:
                time.sleep(2 ** intento)
                continue
            raise
        except (urllib.error.URLError, TimeoutError) as e:
            last = type(e).__name__
            time.sleep(2 ** intento)
            continue
        uso = r.get("usage") or {}
        costo = ch._track(r.get("model") or MODELO, uso, desc)
        if r.get("stop_reason") == "refusal":
            raise RuntimeError(f"{desc}: Opus se negó ({r.get('stop_details')})")
        txt = "".join(b.get("text") or "" for b in r.get("content") or [] if b.get("type") == "text").strip()
        return txt, {"usage": uso, "usd": round(costo, 5), "stop_reason": r.get("stop_reason"), "intento": intento}
    raise RuntimeError(f"{desc}: falló la red {INTENTOS_RED} veces: {last}")


def main() -> int:
    raw = VISUAL.read_bytes()
    if hashlib.md5(raw).hexdigest() != MD5_VISUAL:
        print(f"03_visual.json no es el de F51f ({MD5_VISUAL[:8]}…): PARADA")
        return 1
    v = json.loads(raw.decode("utf-8"))
    caps = {c["chapter_number"]: c for c in v["chapters"] if c.get("image_prompts") is None}
    assert sorted(caps) == [1, 7], sorted(caps)
    fichas = {k: (F52 / "guias" / f"{k}.md").read_text(encoding="utf-8").strip() for k in MODELOS}
    trabajos = []
    for n, cap in sorted(caps.items()):
        for k in MODELOS:
            pedido = PEDIDO.format(ficha=fichas[k], prompt_foto=cap["image_prompt"], ancla=cap["narration_anchor"],
                                   video_prompt_vivo=cap["video_prompt"])
            trabajos.append((n, k, pedido))

    from cost_tracker import cost_tracker
    cost_tracker.start_video("f52_lab_prompts")
    res = {}
    try:
        with ThreadPoolExecutor(max_workers=len(trabajos)) as ex:
            futs = {(n, k): ex.submit(llamar, p, f"f52:prompt:{k}:cap{n:02d}") for n, k, p in trabajos}
            for (n, k), f in futs.items():
                try:
                    txt, meta = f.result()
                    res[(n, k)] = {"prompt": txt, **meta}
                except Exception as e:                       # noqa: BLE001 — se reporta tal cual
                    res[(n, k)] = {"error": f"{type(e).__name__}: {e}"[:400]}
    finally:
        rep = cost_tracker.end_video()
    total = round(rep.total_cost, 4) if rep else None

    pedidos = {(n, k): p for n, k, p in trabajos}
    L = ["# PROMPTS_F52 — los 8 prompts de video en texto (F52 etapa 2)", "",
         f"Salida de `python lab/hyperframes/f52/prompts_video.py`: 8 llamadas a `{MODELO}` (effort `{ESFUERZO}`) en "
         f"paralelo, una por modelo y clip, con el pedido del handoff tal cual. Entrada: el `03_visual.json` de F51f "
         f"(md5 `{MD5_VISUAL[:8]}…`). Costo total: **US$ {total}**. Palabras = `len(prompt.split())`.", "",
         "| clip | modelo | palabras | caracteres | US$ | stop_reason |", "|---|---|---|---|---|---|"]
    for (n, k) in sorted(res):
        r = res[(n, k)]
        if "error" in r:
            L += [f"| cap {n} | {k} {MODELOS[k]} | — | — | — | **error** |"]
        else:
            L += [f"| cap {n} | {k} {MODELOS[k]} | {len(r['prompt'].split())} | {len(r['prompt'])} | {r['usd']} "
                  f"| {r['stop_reason']} |"]
    for n, cap in sorted(caps.items()):
        L += ["", f"## Cap {n} (`veo_position` {cap.get('veo_position')})", "",
              f"- Foto: `lab/hyperframes/f52/fotos/cap{n:02d}.png`",
              f"- Ancla: «{cap['narration_anchor']}»", "", "**`video_prompt` vivo (referencia):**", "", "```",
              cap["video_prompt"], "```"]
        for k in MODELOS:
            r = res[(n, k)]
            L += ["", f"### cap {n} · {k} — {MODELOS[k]}", ""]
            if "error" in r:
                L += [f"**Error:** {r['error']}"]
                continue
            L += [f"{len(r['prompt'].split())} palabras · {len(r['prompt'])} caracteres", "", "```", r["prompt"], "```"]
    L += ["", "## Fichas usadas (`lab/hyperframes/f52/guias/`)", ""]
    L += [f"- {fichas[k]}" for k in MODELOS]
    L += ["", "## El pedido a Opus (plantilla)", "", "```", PEDIDO, "```", ""]
    (F52 / "PROMPTS_F52.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    (F52 / "prompts_f52.json").write_text(json.dumps(
        {"modelo": MODELO, "esfuerzo": ESFUERZO, "md5_visual": MD5_VISUAL, "usd_total": total,
         "prompts": {f"cap{n:02d}_{k}": {**res[(n, k)], "pedido": pedidos[(n, k)]} for (n, k) in sorted(res)}},
        ensure_ascii=False, indent=1), encoding="utf-8")
    errores = [f"cap{n}/{k}" for (n, k), r in res.items() if "error" in r]
    print(f"8 pedidos · errores {errores or 'ninguno'} · US$ {total}")
    for (n, k) in sorted(res):
        r = res[(n, k)]
        print(f"cap{n:02d} {k}: " + (r["error"] if "error" in r else f"{len(r['prompt'].split())} palabras"))
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
