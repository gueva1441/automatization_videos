"""
transcript_fetch.py — Util de fetch de transcript de YouTube para el fix spy-subtemas.
Reusa el plumbing de proxy de prod (youtube_scanner._proxies_dict + sesión rotada por request)
para no throttlear (ver memoria/CHAT 42). youtube-transcript-api v1.x (instancia + http_client).

Maneja el caso "sin transcript" devolviendo "" — el caller hace fallback al comportamiento de
HOY (1 seed genérico desde spanish_topic).

API:
    fetch_transcript(video_id, languages=("en","es")) -> str   # "" si no hay
    clean_transcript(raw) -> str
"""
from __future__ import annotations

import re

import requests

from script_engine.youtube_scanner import _proxies_dict

TRANSCRIPT_CAP = 500_000


def clean_transcript(raw: str) -> str:
    """Limpia [Music]/[Applause] y marcadores de speaker '>>'. Colapsa whitespace."""
    if not raw:
        return ""
    t = re.sub(r"\[(Music|Applause|Laughter|Audio|música)\]", " ", raw, flags=re.IGNORECASE)
    t = re.sub(r">>+", " ", t)
    return re.sub(r"\s+", " ", t).strip()[:TRANSCRIPT_CAP]


def _session_with_proxy() -> requests.Session:
    """requests.Session con el proxy scrapegw (sesión rotada por _proxies_dict)."""
    s = requests.Session()
    s.proxies.update(_proxies_dict())
    return s


def fetch_transcript(video_id: str, languages: tuple[str, ...] = ("en", "es")) -> str:
    """Baja el transcript de un video_id reusando el proxy de prod. Devuelve texto plano
    limpio, o "" si no hay transcript / falla (el caller hace fallback)."""
    if not video_id:
        return ""
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except Exception:
        return ""
    try:
        api = YouTubeTranscriptApi(http_client=_session_with_proxy())
        fetched = api.fetch(video_id, languages=list(languages))
        # v1.x: FetchedTranscript iterable de snippets con .text
        parts = []
        for snip in fetched:
            txt = getattr(snip, "text", None)
            if txt is None and isinstance(snip, dict):
                txt = snip.get("text", "")
            if txt:
                parts.append(txt)
        return clean_transcript(" ".join(parts))
    except Exception:
        return ""
