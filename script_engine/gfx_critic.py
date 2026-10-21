"""
gfx_critic.py — Crítico visual (F4e, paso 6b, pedido de Omar 2026-10-20). Último filtro ANTES del render.

Para cada bloque del plan resuelto (sello, ícono, recorte, dato, contador, nivel de agua, zoom):
    entrada   el cuadro REAL de la foto en ese instante (base.mp4, sin gráficos) + la frase que dice la voz + el
              bloque propuesto descrito en texto (qué es, qué dice, dónde va y cuánto ocupa)
    salida    UNA de tres: suma / repite / estorba, con motivo de una línea. Solo pasan los «suma».
    criterios el ícono no dibuja algo que la foto ya muestra; el texto no repite lo que dice la voz en ese instante;
              nada tapa un rostro ni una zona clara de la foto.
    few-shot  5 bloques del plan dorado de ch02 aprobados por Omar (gfx_profiles/<perfil>_critico_fewshot.json).
    caché     work_dir/gfx_critic_<cap>.json por (hash del cuadro, bloque, voz, versión del prompt).
    error     sin veredicto → el bloque QUEDA (el crítico solo saca con un veredicto; una caída de Gemini no vacía
              el cap) y se anota.
El crítico nunca agrega ni reescribe: solo quita. Las reglas duras (candado, un fact = un bloque, dedupe, máximos)
corren antes, igual que siempre.

G1 (token critic_snapshot): en vez de la foto sola + el bloque en texto, el crítico mira un SNAPSHOT de HyperFrames
del proyecto del cap con el bloque YA DIBUJADO, 1 s después de que entra (o a mitad, si dura menos de 2 s): ve el
tamaño real, el lugar y lo que tapa. Un solo `hyperframes snapshot --at t1,t2,…` por cap. Si el snapshot falla, cae
al cuadro de la foto (como F4e) y lo anota.

contact_sheet(): hoja_contactos_<cap>.jpg — un cuadro por bloque que pasó, tomado del render (capa gfx), etiquetado
con tiempo, bloque y veredicto.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Callable

PROMPT_VERSION = "f4e-1"
PROMPT_VERSION_SNAP = "g1-snap-2"     # F5e: dos cuadros (foto sola + bloque dibujado)
VERDICTS = ("suma", "repite", "estorba")
SYSTEM = ("Sos el editor final de un documental de misterio. Ves el cuadro REAL de la foto en un instante, la frase que "
          "dice la voz en ese momento y un bloque gráfico que se va a poner encima. Decidís si ese bloque SUMA, REPITE o "
          "ESTORBA. Respondés SOLO JSON.")
CRITERIA = (
    "SUMA: aporta algo que ni la foto ni la voz dan en ese instante (un dato, una fecha, una fuente, una palabra "
    "que golpea), y no tapa nada importante.",
    "REPITE: el ícono dibuja algo que la foto YA muestra (una gota sobre una foto de agua, una calavera sobre un "
    "cadáver visible), o el texto dice lo mismo que la voz en ese instante (tercer texto igual: voz + subtítulo + bloque).",
    "ESTORBA: tapa un rostro, unas manos o la zona clara/importante de la foto, o se pelea con lo que se ve.",
    "Un sello de UNA palabra que la voz dice no cuenta como repetir: es énfasis. Repite si es una frase entera de la voz.",
)
SCHEMA: dict[str, Any] = {"type": "OBJECT", "properties": {
    "veredicto": {"type": "STRING", "enum": list(VERDICTS)}, "motivo": {"type": "STRING"}},
    "required": ["veredicto", "motivo"]}
KIND_LABEL = {"sello": "sello", "icono": "ícono", "recorte": "recorte", "dato": "dato", "contador": "contador",
              "nivel_agua": "nivel de agua", "zoom": "zoom"}


def _side(b: dict[str, Any], default: str = "right") -> str:
    return "izquierda" if b.get("side", default) == "left" else "derecha"


def describe(kind: str, b: dict[str, Any]) -> str:
    """El bloque en una línea: qué es, qué dice, dónde va y cuánto ocupa (lo que el crítico no ve en el cuadro)."""
    if kind == "sello":
        return (f"SELLO rojo con la palabra «{str(b.get('word', '')).upper()}» (letras grandes, ~8 % del alto) a media "
                f"altura, a la {_side(b)}, + tinte de mood «{b.get('category')}» sobre toda la imagen 2.5 s")
    if kind == "icono":
        return (f"ÍCONO «{b.get('icon')}» (dibujo de ~25 % del alto) + la palabra «{str(b.get('word', '')).upper()}» al "
                f"lado, en la banda oscura a la {_side(b)}, + tinte de mood «{b.get('category')}»")
    if kind == "recorte":
        k = f" · kicker «{b['kicker']}»" if b.get("kicker") else ""
        return (f"RECORTE de diario (papel, ~30 % del ancho) con el titular «{b.get('headline')}»{k}, a la "
                f"{_side(b, 'left')}" + (f" con ícono «{b['icon']}»" if b.get("icon") else ""))
    if kind == "dato":
        return f"DATO en texto «{b.get('text')}» en la esquina superior {_side(b, 'left')}"
    if kind == "contador":
        return f"CONTADOR que sube hasta «{b.get('value_text')} {b.get('unit', '')}» en la esquina superior izquierda"
    if kind == "nivel_agua":
        return (f"NIVEL DE AGUA: línea que sube desde abajo hasta el {round(float(b.get('height', 0.5)) * 100)} % de la "
                f"altura con la cifra «{b.get('value_text')} {b.get('unit', '')}», tiñe de oscuro la parte de abajo")
    if kind == "zoom":
        return (f"ZOOM de evidencia: la cámara acerca hasta la zona {b.get('box')} (x, y, ancho, alto en 0–1) "
                f"«{b.get('detail') or b.get('anchor')}»")
    return f"{kind}: {json.dumps(b, ensure_ascii=False)[:120]}"


def blocks(plan: dict[str, Any]) -> list[dict[str, Any]]:
    """Bloques a juzgar: {key, kind, t, dur, desc, text}. key = (lista, índice) o (campo, None)."""
    out = []
    for i, e in enumerate(plan.get("emphasis") or []):
        kind = "icono" if e.get("icon_callout") else "sello"
        out.append({"key": ("emphasis", i), "kind": kind, "t": float(e["start"]), "dur": float(e.get("duration", 2.5)),
                    "desc": describe(kind, e), "text": e.get("word", "")})
    for i, a in enumerate(plan.get("archive_clippings") or []):
        out.append({"key": ("archive_clippings", i), "kind": "recorte", "t": float(a["start"]),
                    "dur": float(a.get("duration", 6.0)), "desc": describe("recorte", a), "text": a.get("headline", "")})
    for i, c in enumerate(plan.get("callouts") or []):
        out.append({"key": ("callouts", i), "kind": "dato", "t": float(c["start"]), "dur": float(c.get("duration", 2.5)),
                    "desc": describe("dato", c), "text": c.get("text", "")})
    for field, kind, dur in (("count_up", "contador", 3.7), ("water_level", "nivel_agua", 4.5), ("evidence_zoom", "zoom", 2.85)):
        b = plan.get(field)
        if b and "start" in b:
            out.append({"key": (field, None), "kind": kind, "t": float(b["start"]), "dur": float(b.get("duration", dur)),
                        "desc": describe(kind, b), "text": b.get("value_text") or b.get("anchor") or ""})
    return sorted(out, key=lambda x: x["t"])


def frame_at(video: Path, t: float, dst: Path, width: int = 1280) -> Path:
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(0.0, t):.3f}", "-i", str(video), "-frames:v", "1",
                    "-vf", f"scale={width}:-2", "-q:v", "3", str(dst)], check=True, capture_output=True)
    return dst


def voice_at(words: list[dict], t: float, time_offset: float = 0.0) -> str:
    """La frase que dice la voz en t (la oración que lo contiene; si cae en un silencio, lo que suena ±2 s)."""
    from script_engine.gfx_peak import sentences
    for s in sentences(words, time_offset):
        if s["t0"] - 0.3 <= t <= s["t1"] + 0.3:
            return s["text"]
    return " ".join(str(w["word"]) for w in words if t - 2.0 <= float(w["start"]) + time_offset <= t + 2.0)


def load_fewshot(path: Path | None = None) -> list[dict[str, Any]]:
    if path is None:
        from gfx_config import GFX_PROFILES_DIR, active_profile_name
        path = GFX_PROFILES_DIR / f"{active_profile_name()}_critico_fewshot.json"
    try:
        return json.loads(Path(path).read_text(encoding="utf-8")).get("ejemplos") or []
    except (OSError, ValueError):
        return []


def build_prompt(desc: str, voz: str, fewshot: list[dict[str, Any]], drawn: bool = False) -> str:
    lines = ["CRITERIOS:", *[f"- {c}" for c in CRITERIA], ""]
    if fewshot:
        lines.append("EJEMPLOS aprobados por el dueño del canal (sin imagen; el tono del canal):")
        lines += [f"- bloque: {e['bloque']} · voz: «{e['voz']}» → {e['veredicto']}" for e in fewshot]
        lines.append("")
    lines += [f"LA VOZ EN ESTE INSTANTE DICE: «{voz}»", f"BLOQUE PROPUESTO: {desc}", "",
              ("IMAGEN 1: la foto sola, sin gráficos. IMAGEN 2: el mismo instante con el bloque propuesto YA "
               "DIBUJADO (1 s después de que entra; puede haber otro bloque al lado). Juzgá el BLOQUE contra la FOTO: "
               "qué agrega, qué tapa, si se lee. El sello, el ícono o el texto que ves en la imagen 2 SON el bloque: "
               "nunca digas «repite» porque aparecen en la imagen 2. Repite solo si la FOTO (imagen 1) ya muestra lo "
               "mismo o si la voz dice la misma frase. Motivo en UNA línea corta." if drawn else
               "Mirá el cuadro (es la foto tal cual, sin el bloque) y decidí. Motivo en UNA línea corta."),
              '{"veredicto": "suma" | "repite" | "estorba", "motivo": "…"}']
    return "\n".join(lines)


def _gemini(img: Path, prompt: str, img2: Path | None = None) -> dict[str, Any]:
    from google.genai import types as genai_types
    from config import api, gemini_client
    from cost_tracker import cost_tracker
    parts = [genai_types.Part.from_bytes(data=img.read_bytes(), mime_type="image/jpeg")]
    if img2 is not None:                                  # F5e G1: foto sola + bloque dibujado
        parts.append(genai_types.Part.from_bytes(data=Path(img2).read_bytes(), mime_type="image/jpeg"))
    resp = gemini_client.models.generate_content(
        model=api.gemini_model,
        contents=[*parts, prompt],
        config=genai_types.GenerateContentConfig(system_instruction=SYSTEM, temperature=0.0,
                                                 response_mime_type="application/json", response_schema=SCHEMA))
    cost_tracker.track_gemini_vision(description=f"gfx_critic:{img.stem}", calls=1)
    return json.loads(resp.text)


def judge(img: Path, desc: str, voz: str, *, cache: Path, fewshot: list[dict[str, Any]],
          call: Callable[..., dict] | None = None, drawn: Path | None = None) -> dict[str, Any]:
    """{veredicto, motivo, cache: bool}. Caché por (cuadro(s), bloque, voz, versión). `drawn` = el cuadro con el
    bloque dibujado (F5e G1): el crítico recibe la foto sola (img) y ese cuadro."""
    ver = PROMPT_VERSION_SNAP if drawn else PROMPT_VERSION
    extra = Path(drawn).read_bytes() if drawn else b""
    key = hashlib.sha1(Path(img).read_bytes() + extra + f"|{desc}|{voz}|{ver}".encode("utf-8")).hexdigest()[:20]
    try:
        data = json.loads(cache.read_text(encoding="utf-8")) if cache.exists() else {}
    except (OSError, ValueError):
        data = {}
    if key in data:
        return {**data[key], "cache": True}
    try:
        args = (Path(img), build_prompt(desc, voz, fewshot, drawn=bool(drawn))) + ((Path(drawn),) if drawn else ())
        raw = (call or _gemini)(*args)
        v = str((raw or {}).get("veredicto", "")).strip().lower()
        res = {"veredicto": v if v in VERDICTS else "error",
               "motivo": re.sub(r"\s+", " ", str((raw or {}).get("motivo", ""))).strip()[:160]}
        if res["veredicto"] == "error":
            res["motivo"] = f"respuesta inválida: {json.dumps(raw, ensure_ascii=False)[:80]}"
    except Exception as e:  # noqa: BLE001 — sin veredicto el bloque queda; no se cachea (se reintenta la próxima)
        return {"veredicto": "error", "motivo": f"{type(e).__name__}: {str(e)[:100]}", "cache": False}
    if res["veredicto"] != "error":
        data[key] = res
        cache.parent.mkdir(parents=True, exist_ok=True)
        cache.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    return {**res, "cache": False}


def snapshots(project: Path, times: list[float], out_dir: Path, log: list[str] | None = None,
              timeout: int = 900) -> dict[float, Path]:
    """G1: un `hyperframes snapshot --at t1,t2,…` del proyecto del cap → {t: jpg}. {} si falla (se cae a la foto)."""
    from PIL import Image
    from script_engine.gfx_layer import _hf
    times = sorted(set(round(t, 2) for t in times))
    if not times:
        return {}
    project, out_dir = Path(project).resolve(), Path(out_dir).resolve()     # el CLI corre con cwd = project
    out_dir.mkdir(parents=True, exist_ok=True)
    try:
        r = _hf(["snapshot", str(project), "--at", ",".join(f"{t:.2f}" for t in times), "--no-end", "--keep",
                 "--describe", "false", "-o", str(out_dir)], timeout=timeout, cwd=project)
    except Exception as e:  # noqa: BLE001
        if log is not None:
            log.append(f"  crítico: snapshot falló ({type(e).__name__}) → cuadro de la foto")
        return {}
    got: dict[float, Path] = {}
    for t in times:
        name = f"at-{f'{t:.3f}'.rstrip('0').rstrip('.')}s.png"
        png = out_dir / name
        if png.exists():
            jpg = png.with_suffix(".jpg")
            Image.open(png).convert("RGB").resize((1280, 720)).save(jpg, quality=90)
            got[t] = jpg
    if log is not None and len(got) < len(times):
        log.append(f"  crítico: snapshot rc={r.returncode} · {len(got)}/{len(times)} cuadros "
                   f"{(r.stderr or r.stdout or '')[-160:]!r}")
    return got


def criticize(plan: dict[str, Any], *, base: Path, words: list[dict], time_offset: float, work_dir: Path, cap: str,
              log: list[str], call: Callable[[Path, str], dict] | None = None,
              fewshot: list[dict[str, Any]] | None = None, project: Path | None = None,
              snaps: dict[float, Path] | None = None) -> list[dict[str, Any]]:
    """Juzga cada bloque y saca del plan (in place) los que no «suman». Devuelve una fila por bloque.
    G1: con `project` (proyecto HyperFrames del cap ya escrito con este plan), el cuadro es el snapshot del bloque
    dibujado en t + 1 s; `snaps` permite pasarlos ya sacados (tests)."""
    fs = load_fewshot() if fewshot is None else fewshot
    cache = Path(work_dir) / f"gfx_critic_{cap}.json"
    rows, gone = [], []
    bl = blocks(plan)
    t_of = {id(b): round(b["t"] + (1.0 if b["dur"] >= 2.0 else b["dur"] / 2), 2) for b in bl}
    if snaps is None and project is not None:
        snaps = snapshots(project, list(t_of.values()), Path(work_dir) / f"gfx_critic_{cap}_snap", log)
    snaps = snaps or {}
    n_drawn = 0
    for b in bl:
        tf = t_of[id(b)]
        drawn = tf in snaps
        img = frame_at(base, tf, Path(work_dir) / f"gfx_critic_{cap}" / f"{b['kind']}_{tf:07.2f}.jpg") \
            if Path(base).exists() or not drawn else snaps[tf]
        n_drawn += drawn
        voz = voice_at(words, b["t"], time_offset)
        v = judge(img, b["desc"], voz, cache=cache, fewshot=fs, call=call, drawn=snaps[tf] if drawn else None)
        keep = v["veredicto"] in ("suma", "error")
        rows.append({"t": round(b["t"], 3), "t_frame": tf, "dur": b["dur"], "bloque": b["kind"], "texto": b["text"],
                     "veredicto": v["veredicto"], "motivo": v["motivo"], "pasa": keep, "voz": voz,
                     "mira": "bloque dibujado" if drawn else "foto sola"})
        log.append(f"  crítico: {b['t']:6.1f}s {KIND_LABEL[b['kind']]:<13} «{b['text']}» → {v['veredicto'].upper()}"
                   f" — {v['motivo']}" + (" (caché)" if v.get("cache") else ""))
        if not keep:
            gone.append(b["key"])
    for field, idx in sorted(gone, key=lambda k: (k[0], -(k[1] if k[1] is not None else 0))):
        if idx is None:
            plan[field] = None
        else:
            del plan[field][idx]
    pk = plan.get("pico") or {}
    blk_field = {"water_level": "water_level", "evidence_zoom": "evidence_zoom"}.get(pk.get("block"))
    if blk_field and plan.get(blk_field) is None:
        pk["block_quitado_por_critico"] = True
        log.append(f"  crítico: el bloque del pico ({pk['block']}) no pasó → el pico queda con su palabra")
    n_ok = sum(r["pasa"] for r in rows)
    if project is not None or snaps:
        log.append(f"  crítico: {n_drawn}/{len(rows)} juzgados sobre el bloque dibujado (snapshot)")
    log.append(f"  crítico: {n_ok}/{len(rows)} bloques pasan"
               + (f" · {sum(r['veredicto'] == 'error' for r in rows)} sin veredicto (quedan)" if any(
                   r["veredicto"] == "error" for r in rows) else ""))
    return rows


def _fmt_t(t: float) -> str:
    return f"{int(t // 60)}:{t % 60:04.1f}"


def contact_sheet(video: Path, rows: list[dict[str, Any]], dst: Path, *, cols: int = 3, width: int = 640,
                  log: list[str] | None = None) -> Path | None:
    """Hoja de contactos: un cuadro del render por bloque que pasó, etiquetado con tiempo, bloque y veredicto."""
    from PIL import Image, ImageDraw, ImageFont
    keep = [r for r in rows if r["pasa"]]
    if not keep:
        return None
    tmp = dst.parent / f"_{dst.stem}"
    thumbs = []
    for r in keep:
        im = Image.open(frame_at(video, r["t_frame"] + 0.4, tmp / f"{r['bloque']}_{r['t']:07.2f}.jpg", width)).convert("RGB")
        thumbs.append((im, r))
    h = thumbs[0][0].height
    band = 62
    try:
        font = ImageFont.truetype("arial.ttf", 19)
        small = ImageFont.truetype("arial.ttf", 15)
    except OSError:
        font = small = ImageFont.load_default()
    rows_n = (len(thumbs) + cols - 1) // cols
    sheet = Image.new("RGB", (cols * (width + 8) + 8, rows_n * (h + band + 8) + 8), (18, 18, 18))
    d = ImageDraw.Draw(sheet)
    for k, (im, r) in enumerate(thumbs):
        x, y = 8 + (k % cols) * (width + 8), 8 + (k // cols) * (h + band + 8)
        sheet.paste(im, (x, y))
        d.text((x + 6, y + h + 6), f"{_fmt_t(r['t'])} · {KIND_LABEL[r['bloque']]} · {r['veredicto'].upper()}",
               fill=(240, 232, 210), font=font)
        d.text((x + 6, y + h + 32), (r["motivo"] or "")[:86], fill=(170, 170, 160), font=small)
    sheet.save(dst, quality=88)
    for f in tmp.glob("*.jpg"):
        f.unlink()
    tmp.rmdir()
    if log is not None:
        log.append(f"  hoja de contactos: {dst.name} ({len(thumbs)} cuadros)")
    return dst
