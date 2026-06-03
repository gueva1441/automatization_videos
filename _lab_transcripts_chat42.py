"""
_lab_transcripts_chat42.py — LAB AISLADO read-only (chat 42). NO baja el video, NO toca
el pipeline, $0. Extrae la NARRACIÓN CRUDA (transcript) de los videos que surfaceó el
lab Molde 1, para análisis de "fórmula" POSTERIOR (acá NO se analiza nada).

Insumo:  _lab_out/molde1_chat42_20260603_010310.json  (28 video_ids únicos + metadata)
Output:  _lab_out/transcripts_chat42.json

Herramienta: youtube-transcript-api 1.2.4 (API NUEVA: instancia .fetch()/.list(),
sondeada — NO el get_transcript estático viejo). Usa el proxy del proyecto
(_proxies_dict, rotación por video) porque esta máquina no tiene salida directa a YouTube.

USO:
    python -X utf8 _lab_transcripts_chat42.py
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from youtube_transcript_api import (  # noqa: E402
    YouTubeTranscriptApi,
    TranscriptsDisabled,
    NoTranscriptFound,
    VideoUnavailable,
)
from youtube_transcript_api.proxies import GenericProxyConfig  # noqa: E402

from script_engine.youtube_scanner import _proxies_dict  # noqa: E402

IN_JSON = Path("_lab_out/molde1_chat42_20260603_010310.json")
OUT_JSON = Path("_lab_out/transcripts_chat42.json")
LANGS = ["en", "en-US", "en-GB"]
SLEEP_SEC = 1.5


def _new_api() -> YouTubeTranscriptApi:
    """Instancia con IP fresca del proxy (rotación por video, anti rate-limit)."""
    pd = _proxies_dict()
    cfg = GenericProxyConfig(http_url=pd["http"], https_url=pd["https"])
    return YouTubeTranscriptApi(proxy_config=cfg)


def _flatten(fetched) -> str:
    """Une los segmentos en texto plano (saca timestamps)."""
    parts = [s.get("text", "").strip() for s in fetched.to_raw_data()]
    return " ".join(p for p in parts if p)


def _fetch_one(video_id: str) -> tuple[str, str]:
    """
    Devuelve (lang, texto_plano). Lanza si no hay ningún transcript.

    EN primero: fetchea TODOS los tracks EN (manual Y auto-generado) y se queda con el
    MÁS LARGO. Necesario porque "manual > auto-generado" falla cuando el manual es un
    STUB (ej. video 4+HOURS: manual EN = 91 chars, auto-generado EN = el real). Si no
    hay EN, cae a manual > auto-generado en cualquier idioma.
    """
    ytt = _new_api()
    tlist = ytt.list(video_id)
    try:
        transcripts = list(tlist)
    except TypeError:
        transcripts = (list(getattr(tlist, "_transcripts", {}).values())
                       if hasattr(tlist, "_transcripts") else [])
    if not transcripts:
        raise NoTranscriptFound(video_id, LANGS, tlist)  # type: ignore[call-arg]

    en = [t for t in transcripts if getattr(t, "language_code", "") in LANGS]
    if en:
        pool = en                       # comparar manual vs generado EN → el más largo
    else:
        manual = [t for t in transcripts if not getattr(t, "is_generated", True)]
        generated = [t for t in transcripts if getattr(t, "is_generated", False)]
        pool = (manual or generated)[:1]   # cualquier idioma: manual > generado

    best_text, best_lang, best_len = "", None, -1
    last_err: Exception | None = None
    for t in pool:
        try:
            txt = _flatten(t.fetch())
        except Exception as e:  # noqa: BLE001  (SSL/conn transitorio en un track → probar otro)
            last_err = e
            continue
        if len(txt) > best_len:
            best_text, best_lang, best_len = txt, getattr(t, "language_code", "?"), len(txt)
    if best_lang is None:
        raise last_err if last_err else NoTranscriptFound(video_id, LANGS, tlist)  # type: ignore[call-arg]
    return best_lang, best_text


def main() -> int:
    if not IN_JSON.exists():
        print(f"❌ no existe el insumo: {IN_JSON}")
        return 1
    rows = json.loads(IN_JSON.read_text(encoding="utf-8"))

    # dedupe por video_id (conservar la 1ª aparición con su metadata)
    by_vid: dict[str, dict] = {}
    for r in rows:
        vid = r.get("video_id")
        if vid and vid not in by_vid:
            by_vid[vid] = r
    items = list(by_vid.values())
    print(f"  {len(rows)} filas → {len(items)} video_ids únicos\n")

    out: list[dict] = []
    ok = 0
    sin: list[tuple[str, str, bool]] = []   # (title, motivo, new)
    for i, r in enumerate(items, 1):
        vid = r["video_id"]
        title = r.get("title", "")
        is_jewel = bool(r.get("new"))
        tag = "💎" if is_jewel else "·"
        print(f"  [{i:>2}/{len(items)}] {tag} {vid}  {title[:48]}", flush=True)

        status, lang, error, text = "sin_transcript", None, None, ""
        # Errores DEFINITIVOS (no reintentar): no hay transcript / video caído.
        definitive = (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable)
        try:
            lang, text = _fetch_one(vid)
            status = "ok"
        except definitive as e:
            error = type(e).__name__
        except Exception as e:  # noqa: BLE001  transitorio (SSL/conn/IpBlocked) → 1 retry IP fresca
            try:
                time.sleep(2.0)
                lang, text = _fetch_one(vid)
                status = "ok"
            except definitive as e2:
                error = type(e2).__name__
            except Exception as e2:  # noqa: BLE001
                error = f"{type(e2).__name__}: {e2}"[:160]

        if status == "ok":
            ok += 1
            print(f"        ✓ lang={lang}  {len(text):,} chars")
        else:
            sin.append((title, error or "?", is_jewel))
            print(f"        ⚠ sin_transcript: {error}")

        out.append({
            "video_id": vid,
            "title": title,
            "subnicho": r.get("subnicho"),
            "puerta": r.get("puerta"),
            "views": r.get("views"),
            "ratio": r.get("ratio"),
            "median": r.get("median"),
            "new": is_jewel,
            "old": r.get("old"),
            "lang": lang,
            "status": status,
            "error": error,
            "transcript": text,
        })
        time.sleep(SLEEP_SEC)

    OUT_JSON.parent.mkdir(exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")

    # ─── reporte ───
    jewels_ok = sum(1 for o in out if o["status"] == "ok" and o["new"])
    rej_ok = sum(1 for o in out if o["status"] == "ok" and not o["new"])
    print("\n" + "─" * 60)
    print(f"  OK: {ok}/{len(items)}  (joyas: {jewels_ok} · rechazadas: {rej_ok})")
    print(f"  sin_transcript: {len(sin)}")
    for title, motivo, jewel in sin:
        print(f"     {'💎' if jewel else '·'} {motivo:<22} {title[:50]}")
    total_chars = sum(len(o["transcript"]) for o in out)
    print(f"\n  total transcript: {total_chars:,} chars")
    print(f"  guardado: {OUT_JSON}")
    print(f"  → Omar lo pasa a Claude (chat) para el análisis de fórmula.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
