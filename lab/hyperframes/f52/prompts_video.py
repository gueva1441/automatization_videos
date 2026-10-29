# -*- coding: utf-8 -*-
"""F52 etapa 2 / F52b — los 8 prompts de video en texto: por modelo (K, S, F, G) y clip (cap 1, cap 7), UNA llamada a
Opus 5.5 (effort high, como `m03:casilleros`). F52b: cada llamada lleva primero la foto real del cap (`fotos/capNN.png`,
base64, bloque `image`) y después el pedido del handoff F52b tal cual (= el de F52 + la línea FIRST FRAME), con la
ficha de guía del modelo en inglés (`f52/guias/<letra>.md`), el `image_prompt`, el `narration_anchor` y el
`video_prompt` vivo del 03_visual.json de F51f. Las 8 llamadas en paralelo. No toca producción: el `body` se arma acá
(contenido en lista: imagen + texto) y sale por `claude_helpers._post`; el costo por `claude_helpers._track` →
`cost_tracker` (video_id `f52b_lab_prompts`). Salida: `f52/prompts_f52.json` y `f52/PROMPTS_F52.md`, con cada prompt
nuevo al lado del de F52 (`prompts_f52_v1.json`) y la lectura de CC (`lectura_f52b.json`, si existe).

Uso:
  python lab/hyperframes/f52/prompts_video.py             # las 8 llamadas + PROMPTS_F52.md
  python lab/hyperframes/f52/prompts_video.py --solo-md   # rehace PROMPTS_F52.md desde prompts_f52.json, sin llamar
"""
import base64
import hashlib
import json
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
SALIDA_JSON, V1_JSON, LECTURA = F52 / "prompts_f52.json", F52 / "prompts_f52_v1.json", F52 / "lectura_f52b.json"

# El pedido a Opus del handoff F52b, completo, sin ajustar (F52 + la línea FIRST FRAME).
PEDIDO = """You write the motion prompt for an image-to-video model. The still image is the first frame. Follow the model guide below exactly; it decides structure, length and closing lines.
MODEL GUIDE:
{ficha}
FIRST FRAME: the attached image. Where it differs from the still image prompt (framing, pose, what is visible), describe the motion from the image as it is.
STILL IMAGE PROMPT (what the first frame was asked to show):
{prompt_foto}
NARRATION AT THIS MOMENT:
{ancla}
APPROVED MOTION (keep its intent, rewrite it for this model):
{video_prompt_vivo}
Clip length: 8 seconds, one continuous shot, no cuts, no dialogue, no music, no on-screen text.
Return only the prompt text."""


def foto_b64(n: int) -> tuple[str, str]:
    """(media_type real, base64). Seedream devuelve JPEG por defecto y producción lo guarda con extensión .png: el tipo
    sale de los primeros bytes, no de la extensión."""
    b = (F52 / "fotos" / f"cap{n:02d}.png").read_bytes()
    tipo = "image/jpeg" if b[:3] == b"\xff\xd8\xff" else "image/png" if b[:8] == b"\x89PNG\r\n\x1a\n" else None
    if tipo is None:
        raise SystemExit(f"cap{n:02d}.png no es ni JPEG ni PNG")
    return tipo, base64.b64encode(b).decode("ascii")


def llamar(texto: str, imagen: tuple[str, str], desc: str) -> tuple[str, dict]:
    import claude_helpers as ch
    contenido = [{"type": "image", "source": {"type": "base64", "media_type": imagen[0], "data": imagen[1]}},
                 {"type": "text", "text": texto}]
    body = {"model": MODELO, "max_tokens": ch.MAX_TOKENS, "messages": [{"role": "user", "content": contenido}],
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
            raise RuntimeError(f"{desc}: {last}") from None
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


def cargar_caps() -> dict:
    raw = VISUAL.read_bytes()
    if hashlib.md5(raw).hexdigest() != MD5_VISUAL:
        raise SystemExit(f"03_visual.json no es el de F51f ({MD5_VISUAL[:8]}…): PARADA")
    v = json.loads(raw.decode("utf-8"))
    caps = {c["chapter_number"]: c for c in v["chapters"] if c.get("image_prompts") is None}
    assert sorted(caps) == [1, 7], sorted(caps)
    return caps


def escribir_md(caps: dict, fichas: dict, nuevos: dict, total) -> None:
    v1 = json.loads(V1_JSON.read_text(encoding="utf-8"))["prompts"]
    lect = json.loads(LECTURA.read_text(encoding="utf-8")) if LECTURA.exists() else {}
    pal = lambda t: len((t or "").split())                                       # noqa: E731
    L = ["# PROMPTS_F52 — los 8 prompts de video en texto (F52b: fichas en inglés + Opus mira la foto)", "",
         f"Salida de `python lab/hyperframes/f52/prompts_video.py`: 8 llamadas a `{MODELO}` (effort `{ESFUERZO}`) en "
         f"paralelo, una por modelo y clip. Cada una lleva primero la foto real del cap (`fotos/capNN.png`, bloque "
         f"`image`) y después el pedido del handoff F52b tal cual. Entrada: el `03_visual.json` de F51f (md5 "
         f"`{MD5_VISUAL[:8]}…`). Costo de las 8: **US$ {total}**. Al lado de cada prompt nuevo va el de F52 etapa 2 "
         f"(v1, `prompts_f52_v1.json`: fichas en castellano, sin la foto). Palabras = `len(prompt.split())`.", "",
         "| clip | modelo | palabras v1 | palabras F52b | US$ F52b |", "|---|---|---|---|---|"]
    for n in sorted(caps):
        for k in MODELOS:
            r, a = nuevos.get(f"cap{n:02d}_{k}", {}), v1.get(f"cap{n:02d}_{k}", {})
            L += [f"| cap {n} | {k} {MODELOS[k]} | {pal(a.get('prompt'))} | "
                  f"{pal(r.get('prompt')) if 'prompt' in r else '**error**'} | {r.get('usd', '—')} |"]
    for n, cap in sorted(caps.items()):
        L += ["", f"## Cap {n} (`veo_position` {cap.get('veo_position')})", "",
              f"- Foto (la que ve Opus): `lab/hyperframes/f52/fotos/cap{n:02d}.png`",
              f"- Ancla: «{cap['narration_anchor']}»", "", "**`video_prompt` vivo (referencia):**", "", "```",
              cap["video_prompt"], "```"]
        for k in MODELOS:
            key = f"cap{n:02d}_{k}"
            r, a = nuevos.get(key, {}), v1.get(key, {})
            L += ["", f"### cap {n} · {k} — {MODELOS[k]}", ""]
            if key in lect:
                L += [f"**Lectura de CC:** {lect[key]}", ""]
            if "error" in r:
                L += [f"**F52b — error:** {r['error']}", ""]
            else:
                L += [f"**F52b** ({pal(r.get('prompt'))} palabras · {len(r.get('prompt') or '')} caracteres)", "",
                      "```", r.get("prompt") or "", "```", ""]
            L += [f"**v1, F52** ({pal(a.get('prompt'))} palabras)", "", "```", a.get("prompt") or "", "```"]
    L += ["", "## Fichas usadas (`lab/hyperframes/f52/guias/`, en inglés)", ""]
    L += [f"- {fichas[k]}" for k in MODELOS]
    L += ["", "## El pedido a Opus (plantilla F52b; la foto va antes, como bloque `image`)", "", "```", PEDIDO, "```",
          ""]
    (F52 / "PROMPTS_F52.md").write_text("\n".join(L) + "\n", encoding="utf-8")


def main() -> int:
    caps = cargar_caps()
    fichas = {k: (F52 / "guias" / f"{k}.md").read_text(encoding="utf-8").strip() for k in MODELOS}
    if "--solo-md" in sys.argv:
        d = json.loads(SALIDA_JSON.read_text(encoding="utf-8"))
        escribir_md(caps, fichas, d["prompts"], d.get("usd_total"))
        print("PROMPTS_F52.md rehecho desde prompts_f52.json")
        return 0

    fotos = {n: foto_b64(n) for n in caps}
    trabajos = []
    for n, cap in sorted(caps.items()):
        for k in MODELOS:
            pedido = PEDIDO.format(ficha=fichas[k], prompt_foto=cap["image_prompt"], ancla=cap["narration_anchor"],
                                   video_prompt_vivo=cap["video_prompt"])
            trabajos.append((n, k, pedido))

    from cost_tracker import cost_tracker
    cost_tracker.start_video("f52b_lab_prompts")
    res = {}
    try:
        with ThreadPoolExecutor(max_workers=len(trabajos)) as ex:
            futs = {(n, k): ex.submit(llamar, p, fotos[n], f"f52b:prompt:{k}:cap{n:02d}") for n, k, p in trabajos}
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
    nuevos = {f"cap{n:02d}_{k}": {**res[(n, k)], "pedido": pedidos[(n, k)], "foto": f"fotos/cap{n:02d}.png"}
              for (n, k) in sorted(res)}
    SALIDA_JSON.write_text(json.dumps({"tanda": "F52b", "modelo": MODELO, "esfuerzo": ESFUERZO,
                                       "md5_visual": MD5_VISUAL, "usd_total": total, "prompts": nuevos},
                                      ensure_ascii=False, indent=1), encoding="utf-8")
    escribir_md(caps, fichas, nuevos, total)
    errores = [f"cap{n}/{k}" for (n, k), r in res.items() if "error" in r]
    print(f"8 pedidos · errores {errores or 'ninguno'} · US$ {total}")
    for (n, k) in sorted(res):
        r = res[(n, k)]
        print(f"cap{n:02d} {k}: " + (r["error"] if "error" in r else f"{len(r['prompt'].split())} palabras"))
    return 1 if errores else 0


if __name__ == "__main__":
    sys.exit(main())
