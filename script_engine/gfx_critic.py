"""
gfx_critic.py — Crítico visual (F4e, pedido de Omar 2026-10-20; F29b: el del rotulista; F36 §D: queda solo ese, con
«¿estorba?»). Gemini mira la foto sola en el instante del bloque y responde si el bloque tapa un rostro o lo que la
imagen muestra; «repite» y «no aporta» ya los decidió el guion en papel.
    estorba              F37 §B.1: un bloque del papel (ficha, recorte o sello) en UN intento (instante y lado): el
                         reparto (pantalla_colocar.repartir, clima.sellos_del_papel) lo llama en cada intento hasta que
                         uno pasa; lo que no pasa no se corta, se mueve al intento siguiente
    caché                gfx_critic_rot_<cap>.json por identidad (instante, descripción con el lado, voz); sin
                         veredicto (Gemini caído) el bloque QUEDA y se anota
    contact_sheet        hoja_contactos_<cap>.jpg del render: un cuadro por bloque que pasó
El crítico nunca agrega ni reescribe. F36 §D: se borró el crítico viejo de F4e (suma/repite/estorba con few-shot y
snapshot de HyperFrames). F37 §B.1/§B.4: se borraron `criticize_rotulista` y `blocks` (el crítico de todos los bloques de
una vez, antes del reparto) y las formas de los bloques borrados (contador, nivel de agua, zoom, ícono, dato suelto).
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any, Callable

KIND_LABEL = {"sello": "sello", "recorte": "recorte", "ficha": "ficha"}


def _side(b: dict[str, Any], default: str = "right") -> str:
    return "izquierda" if b.get("side", default) == "left" else "derecha"


def describe(kind: str, b: dict[str, Any]) -> str:
    """El bloque en una línea: qué es, qué dice, dónde va y cuánto ocupa (lo que el crítico no ve en el cuadro)."""
    if kind == "sello":
        return (f"SELLO rojo con la palabra «{str(b.get('word', '')).upper()}» (letras grandes, ~8 % del alto) a media "
                f"altura, a la {_side(b)}, + tinte de mood «{b.get('category')}» sobre toda la imagen 2.5 s")
    if kind == "recorte":
        k = f" · kicker «{b['kicker']}»" if b.get("kicker") else ""
        return (f"RECORTE de diario (papel, ~30 % del ancho) con el titular «{b.get('headline')}»{k}, a la "
                f"{_side(b, 'left')}" + (f" con ícono «{b['icon']}»" if b.get("icon") else ""))
    if kind == "ficha":                                          # F29c §A.5: el componente del title card
        return (f"FICHA como el título del capítulo, arriba a la izquierda: etiqueta roja «{str(b.get('kicker', '')).upper()}» "
                f"y debajo, en letras grandes, «{str(b.get('text', '')).upper()}», con una raya roja; la imagen no se oscurece")
    return f"{kind}: {json.dumps(b, ensure_ascii=False)[:120]}"


def frame_at(video: Path, t: float, dst: Path, width: int = 1280) -> Path:
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{max(0.0, t):.3f}", "-i", str(video), "-frames:v", "1",
                    "-vf", f"scale={width}:-2", "-q:v", "3", str(dst)], check=True, capture_output=True)
    return dst


def clave_identidad(*partes: Any) -> str:
    """F30b §C: la clave del veredicto por lo que el bloque ES (texto, voz, versión), sin los bytes de los cuadros: el
    pre-roll del title card corre el cap 3 s y vuelve a codificar el base, así que la misma foto con el mismo bloque
    ya no da los mismos bytes. Un bloque igual con la misma voz reusa su veredicto (API 0, mismos bloques)."""
    return "id:" + hashlib.sha1("|".join(str(p) for p in partes).encode("utf-8")).hexdigest()[:20]


def frame_t(b: dict[str, Any]) -> float:
    """El instante que se mira de un bloque: 1 s después de que entra (a mitad si dura menos de 2 s)."""
    return round(b["t"] + (1.0 if b["dur"] >= 2.0 else b["dur"] / 2), 2)


# ═══════════════════════ F29b §A.6 / F29c §A.6.2: crítico del rotulista ═══════════════════════

PROMPT_VERSION_ROT = "f29c-1"
SYSTEM_ROT = ("Sos el editor final de un documental de historia oscura. Ves la foto sola, el mismo instante con un bloque "
              "de texto ya dibujado, lo que dice la narración en esa oración y en sus vecinas, lo que el rotulista dice "
              "que el bloque aporta y, si el dato fue pedido para pantalla, por qué. Respondés SOLO JSON.")
PREGUNTA_ROT_1 = "¿La narración de esas oraciones habla de lo que este bloque muestra?"
PREGUNTA_ROT_2 = "¿El bloque dice algo que la narración no dice en esas oraciones?"
PREGUNTA_ROT_3 = "¿El bloque estorba: tapa un rostro o un texto que está en la imagen?"
SCHEMA_ROT: dict[str, Any] = {"type": "OBJECT", "properties": {
    "habla_de_eso": {"type": "BOOLEAN"}, "motivo_1": {"type": "STRING"},
    "dice_algo_nuevo": {"type": "BOOLEAN"}, "motivo_2": {"type": "STRING"},
    "estorba": {"type": "BOOLEAN"}, "motivo_3": {"type": "STRING"}},
    "required": ["habla_de_eso", "motivo_1", "dice_algo_nuevo", "motivo_2", "estorba", "motivo_3"]}


def build_prompt_rot(desc: str, voz: str, aporta: str, por_que: str = "") -> str:
    return "\n".join([
        f"LA NARRACIÓN (la oración del bloque, la anterior y la siguiente): «{voz}»",
        f"BLOQUE: {desc}",
        f"EL ROTULISTA DICE QUE APORTA: «{aporta}»",
        *([f"ESTE DATO SE PIDIÓ PARA PANTALLA PORQUE: «{por_que}»"] if por_que else []),
        "",
        "IMAGEN 1: la foto sola. IMAGEN 2: el mismo instante con el bloque ya dibujado.",
        "La fuente o el kicker del bloque (el nombre del documento, el diario, el año de la fuente) NO cuentan como "
        "aporte: juzgá el texto principal.",
        f"(1) {PREGUNTA_ROT_1}",
        f"(2) {PREGUNTA_ROT_2}",
        f"(3) {PREGUNTA_ROT_3}",
        "Motivo de cada respuesta en UNA línea corta.",
        '{"habla_de_eso": true|false, "motivo_1": "…", "dice_algo_nuevo": true|false, "motivo_2": "…", '
        '"estorba": true|false, "motivo_3": "…"}'])


def _gemini_rot(img: Path, prompt: str, img2: Path | None = None) -> dict[str, Any]:
    from google.genai import types as genai_types
    from config import api, gemini_client
    from cost_tracker import cost_tracker
    parts = [genai_types.Part.from_bytes(data=img.read_bytes(), mime_type="image/jpeg")]
    if img2 is not None:
        parts.append(genai_types.Part.from_bytes(data=Path(img2).read_bytes(), mime_type="image/jpeg"))
    resp = gemini_client.models.generate_content(
        model=api.gemini_model, contents=[*parts, prompt],
        config=genai_types.GenerateContentConfig(system_instruction=SYSTEM_ROT, temperature=0.0,
                                                 response_mime_type="application/json", response_schema=SCHEMA_ROT))
    cost_tracker.track_gemini_vision(description=f"gfx_critic_rot:{img.stem}", calls=1)
    return json.loads(resp.text)


def voice_at(words: list[dict], t: float, time_offset: float = 0.0) -> str:
    """La frase que dice la voz en t (la oración que lo contiene; si cae en un silencio, lo que suena ±2 s)."""
    from script_engine.gfx_peak import sentences
    for s in sentences(words, time_offset):
        if s["t0"] - 0.3 <= t <= s["t1"] + 0.3:
            return s["text"]
    return " ".join(str(w["word"]) for w in words if t - 2.0 <= float(w["start"]) + time_offset <= t + 2.0)


def voice_vecinas(words: list[dict], sentence_idx: Any, t: float, time_offset: float = 0.0) -> str:
    """F29c §A.3: la unidad del «no dicho» = la oración ancla y sus dos vecinas (sin índice: la oración que suena en t)."""
    from script_engine.gfx_peak import sentences
    try:
        k = int(sentence_idx)
    except (TypeError, ValueError):
        return voice_at(words, t, time_offset)
    ss = sentences(words, time_offset)
    return " ".join(s["text"] for s in ss[max(0, k - 1):k + 2])


def estorba(kind: str, obj: dict[str, Any], *, base: Path, words: list[dict], time_offset: float, work_dir: Path,
            cap: str, log: list[str], call: Callable[..., dict] | None = None) -> dict[str, Any]:
    """F36 §B.2: a los bloques del papel el crítico solo les pregunta si estorban (tapan un rostro o lo que está en la
    imagen); «repite» y «no aporta» los decidió el papel. Sin prompt nuevo: es el pedido del crítico del rotulista
    (`build_prompt_rot`, con `aporta` vacío) y de sus tres respuestas solo cuenta la (3). F37 §B.1: corre sobre cada
    INTENTO del reparto (ficha, recorte o sello en un instante y un lado), sobre la foto sola. Devuelve la fila
    {t, t_frame, dur, bloque, texto, veredicto («estorba» / «no estorba» / «error»), motivo, pasa, voz, mira}. Sin
    veredicto, pasa (como siempre). Caché en gfx_critic_rot_<cap>.json por (cap, bloque, segundo, descripción, voz)."""
    cache = Path(work_dir) / f"gfx_critic_rot_{cap}.json"
    try:
        data = json.loads(cache.read_text(encoding="utf-8")) if cache.exists() else {}
    except (OSError, ValueError):
        data = {}
    t = float(obj["start"])
    dur = float(obj.get("duration") or 2.5)
    desc = describe(kind, obj)
    tf = frame_t({"t": t, "dur": dur})
    voz = voice_vecinas(words, obj.get("sentence_idx"), t, time_offset)
    prompt = build_prompt_rot(desc, voz, "", "")
    ident = clave_identidad("estorba", cap, kind, round(t, 2), desc, voz, PROMPT_VERSION_ROT)
    texto = obj.get("word") if kind == "sello" else (obj.get("text") or obj.get("headline") or "")
    if ident in data:
        v = {**data[ident], "cache": True}
    else:
        try:
            img = frame_at(base, tf, Path(work_dir) / f"gfx_critic_{cap}" / f"estorba_{kind}_{tf:07.2f}.jpg")
            raw = (call or _gemini_rot)(Path(img), prompt)
            v = {"estorba": raw.get("estorba"), "motivo_3": str(raw.get("motivo_3") or "")[:160]}
            if isinstance(v["estorba"], bool):
                data[ident] = v
                cache.parent.mkdir(parents=True, exist_ok=True)
                cache.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
            else:
                v = {"error": f"respuesta inválida: {json.dumps(raw, ensure_ascii=False)[:80]}"}
        except Exception as e:  # noqa: BLE001 — sin veredicto el bloque queda (como el crítico de siempre)
            v = {"error": f"{type(e).__name__}: {str(e)[:100]}"}
        v["cache"] = False
    pasa = v.get("error") is not None or v.get("estorba") is not True
    ver = "error" if v.get("error") else "estorba" if v.get("estorba") else "no estorba"
    row = {"t": round(t, 3), "t_frame": tf, "dur": dur, "bloque": kind, "texto": texto, "veredicto": ver,
           "motivo": v.get("error") or v.get("motivo_3") or "", "pasa": pasa, "voz": voz, "mira": "foto sola",
           "pregunta": "¿estorba?"}
    log.append(f"  crítico (¿estorba?): {t:6.1f}s {KIND_LABEL[kind]:<13} «{texto}» → {ver.upper()} — {row['motivo']}"
               + (" (caché)" if v.get("cache") else ""))
    return row


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
