# -*- coding: utf-8 -*-
"""F50h — prueba L contra C del armado del prompt de foto (lab; no toca producción).

Etapa 1 (`--prompts`, US$ 0): los 60 prompts en texto de las 20 fotos del handoff.
- L  = el `prompt` guardado en el papel de F50g (`f50g/PAPEL_FOTOS_WITTENOOM.json`), verificado contra
       `f50g/rearmar.rearmar_una(..., grupos)` y contra el 03_visual.json vivo.
- C  = los mismos casilleros, sin mirada, objeto, paleta, `style_head` ni `STYLE_TAIL`, en el orden de la guía de fal:
       sujeto + acción → aspecto → lugar + año → cartel → luz → plano → una oración de estilo → cierre. Las partes que
       comparte con L salen de `m03_imagenes_v3.armar` (misma regla de lugar/año, plano, cartel y cierre, ya con
       `_sin_negadas`); la luz es `oracion(_sin_negadas(lighting))`, sin `color_palette`.
- C+ép = C con la oración de estilo «como una foto real de ese año».
Después, el mismo post-proceso que L: `f8_backstop` y `_sacar_frases_con_texto` (como `rearmar_una`).
Salida: PROMPTS_F50h.json y PROMPTS_F50h.md.

Etapa 2 (`--fotos`, Omar OK 2026-10-29 02:30): 20 fotos × 3 armados, 2 imágenes por llamada (60 llamadas a Seedream
5.0 Lite en paralelo, con el freno del tope), a ciegas: letra A/B/C al azar por foto; la llave (`llave.json`) va
aparte, fuera de git, y no se abre.
Etapa 3: `--hojas` (una hoja ciega 2 × 3 por foto), `--vision` (una llamada por png con el cliente y el modelo de
`gfx_critic`, prompt exacto del handoff) y `--tabla` (VISION_F50h.json/.md por letra, no por variante).
Uso: python lab/hyperframes/f50h/f50h.py --prompts | --fotos | --hojas | --vision | --tabla
"""
import json
import re
import statistics
import sys
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "lab" / "hyperframes" / "f50g"))
F50H = Path(__file__).resolve().parent
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"

# las 20 fotos del handoff F50h §Etapa 1 (cap, foto del papel de F50g)
FOTOS = [(1, 2), (1, 3), (1, 4), (2, 9), (2, 11), (2, 15), (3, 3), (3, 6), (3, 10), (4, 1), (4, 11), (4, 12), (5, 1),
         (5, 8), (5, 13), (5, 16), (6, 5), (6, 15), (7, 7), (7, 9)]
ENTEROS = [(1, 2), (3, 3), (7, 7)]                      # los 3 prompts que el .md pega enteros
ESTILO_C = ("A grainy 35mm documentary photograph taken in {anio}, with muted colors and slight underexposure, in a "
            "dark-history realist style.")          # handoff F50h, parte 7 de C
ESTILO_EP = ("A grainy documentary photograph taken in {anio}, with the film, color and tones a real photograph from "
             "{anio} would have, slightly underexposed, in a dark-history realist style.")   # handoff F50h, C+ép


def oraciones(p: str) -> int:
    return len([x for x in re.split(r"(?<=[.!?])\s+", (p or "").strip()) if x])


def palabras(p: str) -> int:
    return len((p or "").split())


def armar_c(slots: dict, anio: str, grupos: dict, estilo: str) -> str:
    """C (o C+ép con otro `estilo`): las partes de `armar` que comparte con L, en el orden de la guía de fal."""
    from script_engine import m03_imagenes_v3 as v3
    pa = v3.armar(slots, anio, grupos)["partes"]
    luz = v3.oracion(v3._sin_negadas(slots.get("lighting"))) if isinstance(slots.get("lighting"), str) else ""
    partes = [pa["sujeto"], pa["aspecto"], pa["lugar_anio"], pa["texto"], luz, pa["tecnica"],
              estilo.format(anio=anio), pa["cierre"]]
    return " ".join(p for p in partes if p)


def post(prompt: str, slots: dict, escala: bool, documented) -> str:
    """El mismo post-proceso que L (`f50g/rearmar.rearmar_una`)."""
    from script_engine import m03_imagenes_v3 as v3
    from script_engine.m03_visual import _sacar_frases_con_texto
    prose, _ = v3.f8_backstop(prompt, slots, escala, documented)
    tii = slots.get("text_in_image") or {}
    prose, _ = _sacar_frases_con_texto(prose, (tii.get("text") or "") if tii.get("present") else "")
    return prose


def prompts() -> int:
    import rearmar as rg
    from script_engine import m03_imagenes_v3 as v3
    from script_engine.topics_db import get_topic_by_id
    vivo = json.loads(rg.VISUAL.read_text(encoding="utf-8"))
    papel = {(f["cap"], f["foto"]): f for f in json.loads(
        (ROOT / "lab" / "hyperframes" / "f50g" / "PAPEL_FOTOS_WITTENOOM.json").read_text(encoding="utf-8"))["fotos"]}
    topic = get_topic_by_id(TID)
    beats = v3.load_beats(topic, rg.STEPS)
    grupos = {g["id"]: g for g in topic.get("people_groups") or [] if isinstance(g, dict) and g.get("id")}
    items = {(c["chapter_number"], i): it for c in vivo["chapters"] for i, (it, _) in enumerate(rg.fotos(c), 1)}
    out, verif = [], []
    for cap, foto in FOTOS:
        it = items[(cap, foto)]
        by_n = {b["n"]: b for b in beats.get(cap) or []}
        escala = bool((by_n.get(it.get("beat")) or {}).get("escala"))
        documented = topic.get("documented_people")
        slots = json.loads(it["raw_llm_prompt"])
        anio = it["anio"]
        L = papel[(cap, foto)]["prompt"]
        rearmado, _ = rg.rearmar_una(it, escala, documented, grupos)
        verif.append({"foto": f"{cap}/{foto}", "L_igual_rearmar": L == rearmado, "L_igual_vivo": L == it["prompt"]})
        C = post(armar_c(slots, anio, grupos, ESTILO_C), slots, escala, documented)
        CE = post(armar_c(slots, anio, grupos, ESTILO_EP), slots, escala, documented)
        out.append({"foto": f"{cap}/{foto}", "anio": anio, "people_group": slots.get("people_group") or [],
                    "shot_scale": slots.get("shot_scale"),
                    "cartel": (slots.get("text_in_image") or {}).get("text")
                    if (slots.get("text_in_image") or {}).get("present") else None,
                    "L": L, "C": C, "C+ép": CE,
                    "palabras": {"L": palabras(L), "C": palabras(C), "C+ép": palabras(CE)},
                    "oraciones": {"L": oraciones(L), "C": oraciones(C), "C+ép": oraciones(CE)}})
    ok = sum(v["L_igual_rearmar"] and v["L_igual_vivo"] for v in verif)
    med = {k: statistics.median(f["palabras"][k] for f in out) for k in ("L", "C", "C+ép")}
    mx = {k: max(f["palabras"][k] for f in out) for k in ("L", "C", "C+ép")}
    mn = {k: min(f["palabras"][k] for f in out) for k in ("L", "C", "C+ép")}
    ormed = {k: statistics.median(f["oraciones"][k] for f in out) for k in ("L", "C", "C+ép")}
    (F50H / "PROMPTS_F50h.json").write_text(json.dumps(
        {"fotos": out, "verificacion_L": verif, "L_igual_guardado": f"{ok}/{len(out)}",
         "palabras": {"mediana": med, "max": mx, "min": mn}, "oraciones_mediana": ormed},
        ensure_ascii=False, indent=1), encoding="utf-8")
    L_ = ["# PROMPTS_F50h — L, C y C+ép de las 20 fotos (F50h etapa 1, en texto, US$ 0)", "",
          "Salida de `python lab/hyperframes/f50h/f50h.py --prompts`. Casilleros: el `raw_llm_prompt` y el `anio` de "
          "cada foto del 03_visual.json vivo de Wittenoom; grupos: los `people_groups` del topic (igual que "
          "`f50g/rearmar.py`). Ninguna llamada a modelos ni a fal.", "",
          f"**Verificación L = guardado: {ok}/{len(out)}**. L (el `prompt` del papel de F50g) es igual a "
          f"`rearmar_una(..., grupos)` y al `prompt` del 03_visual.json vivo en {ok} de {len(out)} fotos.", "",
          "| | L | C | C+ép |", "|---|---:|---:|---:|",
          f"| palabras, mediana | {med['L']} | {med['C']} | {med['C+ép']} |",
          f"| palabras, mín · máx | {mn['L']} · {mx['L']} | {mn['C']} · {mx['C']} | {mn['C+ép']} · {mx['C+ép']} |",
          f"| oraciones, mediana | {ormed['L']} | {ormed['C']} | {ormed['C+ép']} |", "",
          "Referencia de la guía de fal (no es un corte; el handoff lo pide solo como dato al lado): 2–4 oraciones.", "",
          "## Por foto", "",
          "| foto | año | plano | grupos | cartel | palabras L · C · C+ép | oraciones L · C · C+ép | L = guardado |",
          "|---|---|---|---|---|---|---|---|"]
    for f, v in zip(out, verif):
        p, o = f["palabras"], f["oraciones"]
        L_.append(f"| {f['foto']} | {f['anio']} | {f['shot_scale']} | {', '.join(f['people_group']) or '—'} | "
                  f"{f['cartel'] or '—'} | {p['L']} · {p['C']} · {p['C+ép']} | {o['L']} · {o['C']} · {o['C+ép']} | "
                  f"{'sí' if v['L_igual_rearmar'] and v['L_igual_vivo'] else 'NO'} |")
    for cap, foto in ENTEROS:
        f = next(x for x in out if x["foto"] == f"{cap}/{foto}")
        L_ += ["", f"## {cap}/{foto} entera", ""]
        for k in ("L", "C", "C+ép"):
            L_ += [f"**{k}** ({f['palabras'][k]} palabras, {f['oraciones'][k]} oraciones)", "", "```", f[k], "```", ""]
    (F50H / "PROMPTS_F50h.md").write_text("\n".join(L_), encoding="utf-8")
    print(f"L = guardado {ok}/{len(out)} · palabras mediana {med} · máx {mx} · oraciones mediana {ormed}")
    return 0 if ok == len(out) else 1


# ═══════════════════════════ etapa 2: fotos (Seedream 5.0 Lite) ═══════════════════════════
LAB_ID = "f50h-lab"                                     # sesión de cost_tracker de esta prueba
TOPE_USD = 5.00                                         # handoff F50h §Constantes (Omar 2026-10-29 02:03)
NUM_IMAGES = 2                                          # handoff F50h §Constantes (no hay seed en 5.0 Lite)
VARIANTES = ("L", "C", "C+ép")
LETRAS = ("A", "B", "C")
FOTOS_DIR = F50H / "fotos"
LLAVE = F50H / "llave.json"                             # foto → {letra: variante}; fuera de git, no se abre
_LOCK = threading.Lock()


class Parada(RuntimeError):
    pass


def _gastado_previo() -> float:
    from cost_tracker import cost_tracker
    raw = cost_tracker.HISTORY_FILE.read_bytes() if cost_tracker.HISTORY_FILE.exists() else b"[]"
    try:
        h = json.loads(raw.decode("utf-8"))
    except UnicodeDecodeError:
        h = json.loads(raw.decode("cp1252"))
    return round(sum(float(r.get("total_cost") or 0) for r in h if isinstance(r, dict) and r.get("video_id") == LAB_ID),
                 4)


def _gastado(previo: float) -> float:
    from cost_tracker import cost_tracker
    cv = cost_tracker.current_video
    return round(previo + (cv.total_cost if cv else 0.0), 4)


def generar_2(prompt: str, base: Path) -> int:
    """`f49_corridas.generar_1` con `num_images` 2 (mismo payload de producción y endpoint); guarda las 2 imágenes como
    `<base>_1.png` y `<base>_2.png`. Devuelve cuántas llegaron."""
    import requests

    import asset_manager as am
    from cost_tracker import cost_tracker
    from engine_profiles import select_profile
    prof = select_profile("seedream")
    payload = am._SYNC_PAYLOAD_BUILDERS["seedream"](prompt, None)
    payload["num_images"] = NUM_IMAGES
    try:
        r = requests.post(f"{prof.render.base_url}/{prof.render.model_id}", headers=am._fal_headers(), json=payload,
                          timeout=240)
        r.raise_for_status()
    except requests.HTTPError as e:
        body = e.response.text if e.response is not None else str(e)
        if am._is_content_rejection(body):
            raise am.ContentRejectedError(body[:300])
        raise
    imgs = r.json().get("images") or []
    cost_tracker.track_seedream(description=f"{base.parent.name}/{base.name}", images=len(imgs))
    base.parent.mkdir(parents=True, exist_ok=True)
    for k, im in enumerate(imgs, start=1):
        g = requests.get(im["url"], timeout=60)
        g.raise_for_status()
        base.with_name(f"{base.name}_{k}.png").write_bytes(g.content)
    return len(imgs)


def fotos() -> int:
    """60 llamadas (20 fotos × 3 armados) en paralelo, a ciegas: letra al azar por foto; la llave va aparte."""
    import random

    import asset_manager as am
    from cost_tracker import cost_tracker
    from engine_profiles import select_profile
    P = {f["foto"]: f for f in json.loads((F50H / "PROMPTS_F50h.json").read_text(encoding="utf-8"))["fotos"]}
    if LLAVE.exists():
        llave = json.loads(LLAVE.read_text(encoding="utf-8"))
    else:
        rnd = random.SystemRandom()
        llave = {}
        for foto in P:
            v = list(VARIANTES)
            rnd.shuffle(v)
            llave[foto] = dict(zip(LETRAS, v))
        LLAVE.write_text(json.dumps(llave, ensure_ascii=False, indent=1), encoding="utf-8")
    costo = select_profile("seedream").render.cost_usd * NUM_IMAGES
    trabajos = [(foto, letra) for foto in P for letra in LETRAS]
    previo = _gastado_previo()
    cost_tracker.start_video(LAB_ID)
    reservado = {"n": 0}

    def una(foto: str, letra: str) -> dict:
        base = FOTOS_DIR / foto.replace("/", "_") / letra
        if all(base.with_name(f"{letra}_{k}.png").exists() for k in range(1, NUM_IMAGES + 1)):
            return {"foto": foto, "letra": letra, "estado": "ya estaba", "intentos": 0}
        prompt = P[foto][llave[foto][letra]]
        errores = []
        for intento in (1, 2):                          # handoff: un rechazo o un error se reintenta una vez
            with _LOCK:                                 # freno antes de cada llamada, con lo ya reservado en vuelo
                g = _gastado(previo)
                if g + costo * (reservado["n"] + 1) > TOPE_USD:
                    raise Parada(f"freno ({foto} {letra}): gastado {g:.4f} + en vuelo > tope {TOPE_USD:.2f}")
                reservado["n"] += 1
            try:
                n = generar_2(prompt, base)
                if n == NUM_IMAGES:
                    return {"foto": foto, "letra": letra, "estado": "ok", "intentos": intento}
                errores.append(f"llegaron {n} imágenes")
            except am.ContentRejectedError as e:
                errores.append(f"rechazada: {str(e)[:200]}")
            except Exception as e:  # noqa: BLE001 — se reintenta una vez y queda como hueco
                errores.append(f"{type(e).__name__}: {str(e)[:200]}")
            finally:
                with _LOCK:
                    reservado["n"] -= 1
        return {"foto": foto, "letra": letra, "estado": "hueco", "errores": errores, "intentos": 2}

    resultado = []
    try:
        with ThreadPoolExecutor(max_workers=min(am.FLUX_MAX_WORKERS, len(trabajos))) as ex:
            for f in as_completed([ex.submit(una, *t) for t in trabajos]):
                try:
                    r = f.result()
                except Parada as e:
                    r = {"estado": f"PARADA: {e}"}
                resultado.append(r)
                print(f"  {r}", flush=True)
    finally:
        cost_tracker.end_video()
    total = _gastado_previo()
    resultado.sort(key=lambda r: (r.get("foto", ""), r.get("letra", "")))
    (F50H / "fotos_resultado.json").write_text(json.dumps({"resultado": resultado, "usd_lab": total},
                                                          ensure_ascii=False, indent=1), encoding="utf-8")
    ok = sum(1 for r in resultado if r.get("estado") in ("ok", "ya estaba"))
    pngs = len(list(FOTOS_DIR.glob("*/*.png")))
    print(f"fotos: {ok}/{len(trabajos)} llamadas ok · {pngs} png · cost_history {LAB_ID} = US$ {total:.4f}")
    return 0


# ═══════════════════════════ etapa 3: hojas, visión y tabla ═══════════════════════════
def _fuente(tam: int):
    from PIL import ImageFont
    try:
        return ImageFont.truetype("C:/Windows/Fonts/arial.ttf", tam)
    except OSError:
        return ImageFont.load_default()


def _anclas() -> dict:
    papel = json.loads((ROOT / "lab" / "hyperframes" / "f50g" / "PAPEL_FOTOS_WITTENOOM.json").read_text(
        encoding="utf-8"))["fotos"]
    return {f"{f['cap']}/{f['foto']}": f["ancla"] for f in papel}


def hojas(cw: int = 1280) -> int:
    """Una hoja por foto: 2 filas × 3 columnas (A, B, C; arriba la foto 1, abajo la 2), rótulo A1…C2, arriba el ancla."""
    from PIL import Image, ImageDraw
    anclas = _anclas()
    (F50H / "hojas").mkdir(exist_ok=True)
    m, enc_h = 12, 110
    chh = round(cw * 1440 / 2560)
    f_enc, f_ancla, f_cel = _fuente(30), _fuente(24), _fuente(34)
    for cap, foto in FOTOS:
        key = f"{cap}/{foto}"
        im = Image.new("RGB", (m + 3 * (cw + m), enc_h + 2 * (chh + m) + m), (24, 24, 24))
        dr = ImageDraw.Draw(im)
        dr.text((m, 8), f"Cap {cap} · foto {foto}", fill=(255, 210, 90), font=f_enc)
        linea, ys = "", 48
        for w in (anclas.get(key) or "").split():
            if dr.textlength(linea + " " + w, font=f_ancla) > im.size[0] - 2 * m:
                dr.text((m, ys), linea.strip(), fill=(220, 220, 220), font=f_ancla)
                ys, linea = ys + 28, ""
            linea += " " + w
        if linea.strip():
            dr.text((m, ys), linea.strip(), fill=(220, 220, 220), font=f_ancla)
        for fila, n in enumerate((1, 2)):
            for col, letra in enumerate(LETRAS):
                x, y = m + col * (cw + m), enc_h + fila * (chh + m)
                p = FOTOS_DIR / f"{cap}_{foto}" / f"{letra}_{n}.png"
                if p.exists():
                    with Image.open(p) as f:
                        im.paste(f.convert("RGB").resize((cw, chh), Image.LANCZOS), (x, y))
                else:
                    dr.rectangle([x, y, x + cw - 1, y + chh - 1], fill=(110, 110, 110))
                    dr.text((x + cw / 2 - 40, y + chh / 2 - 17), "hueco", fill=(240, 240, 240), font=f_cel)
                dr.rectangle([x + 8, y + 8, x + 78, y + 52], fill=(0, 0, 0))
                dr.text((x + 16, y + 12), f"{letra}{n}", fill=(255, 255, 255), font=f_cel)
        s = F50H / "hojas" / f"hoja_{cap}_{foto}.jpg"
        im.save(s, "JPEG", quality=88)
        print(f"{s.relative_to(ROOT)}  {im.size[0]}x{im.size[1]}")
    return 0


VISION_PROMPT = """You are checking one photograph against a list of elements it should show.
For each element, answer "yes" if it is clearly shown, "no" if it is missing or contradicted, or "not_visible" if the framing makes it impossible to judge (for example, people seen only from behind for an appearance element).
Judge only what you can see in the image. Do not guess.
Elements:
{elementos}
Return only JSON, with no other text:
{{"elements":[{{"id":"<id>","answer":"yes|no|not_visible","reason":"<at most 12 words>"}}],"invented_text":true|false}}
"invented_text" is true if the image shows any letters or words other than the sign text listed above."""   # handoff


def elementos(slots: dict, anio: str, grupos: dict, blocklist: list) -> list[tuple[str, str]]:
    """Los elementos de una foto, por código desde sus casilleros (los mismos para las 3 variantes)."""
    e = [("subject", slots.get("subject")), ("action", slots.get("action"))]
    for g in slots.get("people_group") or []:
        if (grupos.get(g) or {}).get("appearance"):
            e.append((f"appearance_{g}", grupos[g]["appearance"]))
    e += [("place", slots.get("setting")),
          ("era", f"Everything visible fits the year {anio}; none of these appear: {'; '.join(blocklist)}"),
          ("lighting", slots.get("lighting")),
          ("shot", f"{slots.get('shot_scale')} shot, {slots.get('camera_angle')}")]
    tii = slots.get("text_in_image") or {}
    if tii.get("present") and tii.get("text"):
        e.append(("sign", f'A sign or label reads exactly "{tii["text"]}" and is legible'))
    else:
        e.append(("no_text", "No readable letters or words anywhere in the image"))
    return [(i, str(t or "").strip()) for i, t in e]


def _vision_una(png: Path, prompt: str) -> dict:
    from google.genai import types as genai_types

    from config import api, gemini_client
    from cost_tracker import cost_tracker
    resp = gemini_client.models.generate_content(
        model=api.gemini_model, contents=[genai_types.Part.from_bytes(data=png.read_bytes(), mime_type="image/png"),
                                          prompt],
        config=genai_types.GenerateContentConfig(temperature=0.0, response_mime_type="application/json"))
    cost_tracker.track_gemini_vision(description=f"f50h vision {png.parent.name}/{png.stem}", calls=1)
    u = getattr(resp, "usage_metadata", None)
    tokens = {"in": getattr(u, "prompt_token_count", 0) or 0, "out": getattr(u, "candidates_token_count", 0) or 0,
              "think": getattr(u, "thoughts_token_count", 0) or 0}
    return {"data": json.loads(resp.text), "tokens": tokens}


def vision() -> int:
    """Una llamada por png con el cliente y el modelo de gfx_critic; sin variante, prompt ni nombre de archivo."""
    import rearmar as rg
    from cost_tracker import cost_tracker
    from script_engine.topics_db import get_topic_by_id
    vivo = json.loads(rg.VISUAL.read_text(encoding="utf-8"))
    items = {f"{c['chapter_number']}/{i}": it for c in vivo["chapters"] for i, (it, _) in enumerate(rg.fotos(c), 1)}
    topic = get_topic_by_id(TID)
    grupos = {g["id"]: g for g in topic.get("people_groups") or [] if isinstance(g, dict) and g.get("id")}
    canon = json.loads((ROOT / "lab" / "hyperframes" / "f50f" / "canon_f50f.json").read_text(encoding="utf-8"))
    blocklist = [str(x) for x in canon.get("anachronism_blocklist") or []]
    trabajos = []
    for cap, foto in FOTOS:
        key = f"{cap}/{foto}"
        slots = json.loads(items[key]["raw_llm_prompt"])
        el = elementos(slots, items[key]["anio"], grupos, blocklist)
        prompt = VISION_PROMPT.format(elementos="\n".join(f"- {i}: {t}" for i, t in el))
        for letra in LETRAS:
            for n in (1, 2):
                p = FOTOS_DIR / f"{cap}_{foto}" / f"{letra}_{n}.png"
                if p.exists():
                    trabajos.append((key, letra, n, p, prompt, [i for i, _ in el]))
    previo = _gastado_previo()
    cost_tracker.start_video(LAB_ID)

    def una(key, letra, n, p, prompt, ids):
        errores = []
        for intento in (1, 2):                          # un JSON que no parsea se pide una vez más
            with _LOCK:
                if _gastado(previo) > TOPE_USD:
                    raise Parada(f"tope US$ {TOPE_USD:.2f} alcanzado antes de {key} {letra}{n}")
            try:
                r = _vision_una(p, prompt)
                d = r["data"]
                if not isinstance(d, dict) or not isinstance(d.get("elements"), list):
                    raise ValueError("JSON sin elements")
                return {"foto": key, "letra": letra, "n": n, "ids": ids, "respuesta": d, "tokens": r["tokens"],
                        "intentos": intento}
            except Exception as e:  # noqa: BLE001
                errores.append(f"{type(e).__name__}: {str(e)[:200]}")
        return {"foto": key, "letra": letra, "n": n, "ids": ids, "hueco": errores, "intentos": 2}

    out = []
    try:
        with ThreadPoolExecutor(max_workers=len(trabajos) or 1) as ex:
            for f in as_completed([ex.submit(una, *t) for t in trabajos]):
                try:
                    out.append(f.result())
                except Parada as e:
                    out.append({"PARADA": str(e)})
    finally:
        cost_tracker.end_video()
    out.sort(key=lambda r: (r.get("foto", ""), r.get("letra", ""), r.get("n", 0)))
    (F50H / "VISION_F50h_crudo.json").write_text(json.dumps({"respuestas": out, "usd_lab": _gastado_previo()},
                                                           ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"visión: {sum(1 for r in out if 'respuesta' in r)}/{len(trabajos)} ok · huecos "
          f"{sum(1 for r in out if 'hueco' in r)} · cost_history {LAB_ID} = US$ {_gastado_previo():.4f}")
    return 0


def tabla() -> int:
    """VISION_F50h.json/.md por letra (no por variante): puntaje = sí / (sí + no) por png, `not_visible` aparte."""
    import statistics as st
    d = json.loads((F50H / "VISION_F50h_crudo.json").read_text(encoding="utf-8"))
    pngs = {}
    for r in d["respuestas"]:
        if "foto" not in r:
            continue
        k = (r["foto"], r["letra"], r["n"])
        if "hueco" in r:
            pngs[k] = {"hueco": r["hueco"]}
            continue
        ans = {e.get("id"): str(e.get("answer") or "").lower() for e in r["respuesta"].get("elements") or []
               if isinstance(e, dict)}
        si = sum(1 for i in r["ids"] if ans.get(i) == "yes")
        no = sum(1 for i in r["ids"] if ans.get(i) == "no")
        nv = sum(1 for i in r["ids"] if ans.get(i) == "not_visible")
        falta = [i for i in r["ids"] if i not in ans]
        pngs[k] = {"si": si, "no": no, "not_visible": nv, "sin_respuesta": falta,
                   "puntaje": round(si / (si + no), 3) if si + no else None,
                   "invented_text": bool(r["respuesta"].get("invented_text")),
                   "respuestas": r["respuesta"].get("elements")}
    filas, tot = [], {l: {"puntajes": [], "nv": 0, "inv": 0, "huecos": 0} for l in LETRAS}
    for cap, foto in FOTOS:
        key = f"{cap}/{foto}"
        fila = {"foto": key}
        for l in LETRAS:
            ps = [pngs.get((key, l, n)) for n in (1, 2)]
            val = [p["puntaje"] for p in ps if p and p.get("puntaje") is not None]
            fila[l] = {"puntaje": round(st.mean(val), 3) if val else None,
                       "not_visible": sum(p.get("not_visible", 0) for p in ps if p),
                       "invented_text": sum(1 for p in ps if p and p.get("invented_text")),
                       "huecos": sum(1 for p in ps if not p or "hueco" in p)}
            tot[l]["puntajes"] += val
            tot[l]["nv"] += fila[l]["not_visible"]
            tot[l]["inv"] += fila[l]["invented_text"]
            tot[l]["huecos"] += fila[l]["huecos"]
        filas.append(fila)
    total = {l: {"puntaje_medio": round(st.mean(t["puntajes"]), 3) if t["puntajes"] else None,
                 "pngs_medidos": len(t["puntajes"]), "not_visible": t["nv"], "invented_text": t["inv"],
                 "huecos": t["huecos"]} for l, t in tot.items()}
    (F50H / "VISION_F50h.json").write_text(json.dumps(
        {"por_foto": filas, "total": total, "por_png": {f"{k[0]} {k[1]}{k[2]}": v for k, v in sorted(pngs.items())},
         "usd_lab": d.get("usd_lab")}, ensure_ascii=False, indent=1), encoding="utf-8")
    L = ["# VISION_F50h — puntaje por elemento con Gemini Flash, por letra (F50h etapa 3)", "",
         "Salida de `python lab/hyperframes/f50h/f50h.py --vision` y `--tabla`. Una llamada por png con el cliente y el "
         "modelo de `script_engine/gfx_critic.py` y el prompt exacto del handoff; el modelo no ve la variante, el "
         "prompt ni el nombre del archivo. Por letra (A/B/C), **no por variante**: la llave no se abrió.", "",
         "Puntaje por png = sí / (sí + no); `not_visible` aparte. Por foto y letra: la media de los 2 png.", "",
         "## Total por letra", "", "| letra | puntaje medio | png medidos | not_visible | invented_text | huecos |",
         "|---|---:|---:|---:|---:|---:|"]
    L += [f"| {l} | {t['puntaje_medio']} | {t['pngs_medidos']} | {t['not_visible']} | {t['invented_text']} | "
          f"{t['huecos']} |" for l, t in total.items()]
    L += ["", "## Por foto", "",
          "| foto | A puntaje · nv · inv | B puntaje · nv · inv | C puntaje · nv · inv |", "|---|---|---|---|"]
    for f in filas:
        L.append(f"| {f['foto']} | " + " | ".join(
            f"{f[l]['puntaje']} · {f[l]['not_visible']} · {f[l]['invented_text']}"
            + (f" · {f[l]['huecos']} hueco" if f[l]["huecos"] else "") for l in LETRAS) + " |")
    (F50H / "VISION_F50h.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"tabla: {json.dumps(total, ensure_ascii=False)}")
    return 0


def main() -> int:
    for flag, fn in (("--prompts", prompts), ("--fotos", fotos), ("--hojas", hojas), ("--vision", vision),
                     ("--tabla", tabla)):
        if flag in sys.argv:
            return fn()
    print("uso: f50h.py --prompts | --fotos | --hojas | --vision | --tabla")
    return 2


if __name__ == "__main__":
    sys.exit(main())
