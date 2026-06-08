"""
transcript_fetch.py — Util de fetch de transcript de YouTube para el fix spy-subtemas.
Reusa el plumbing de proxy de prod (youtube_scanner._proxies_dict + sesión rotada por request)
para no throttlear (ver memoria/CHAT 42). youtube-transcript-api v1.x (instancia + http_client).

Distingue (T1, chat 49) DOS desenlaces que antes se confundían en "":
  - ""   → el video genuinamente NO tiene subtítulos (fallback válido: el caller cae al
           flujo de HOY, 1 seed genérico desde spanish_topic).
  - None → FALLO DE INFRA (import faltante / red / SSL / parse). Se loguea explícito y el
           caller debe SKIPpear el video — NO fabricar un seed ATÓMICO sobre un video que
           falló (ese bug ya nos pasó: módulo no instalado → "sin transcript" en TODA una
           corrida, en silencio).

API:
    fetch_transcript(video_id, languages=("en","es")) -> str | None
        # texto limpio · "" sin subtítulos legítimo · None fallo de infra
    clean_transcript(raw) -> str
"""
from __future__ import annotations

import logging
import re

import requests

from script_engine.youtube_scanner import _proxies_dict

# Mismo logger que el resto del pipeline (configurado en error_handler.py → logs/pipeline_*.log)
logger = logging.getLogger("viral_pipeline")

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


def fetch_transcript(video_id: str, languages: tuple[str, ...] = ("en", "es")) -> str | None:
    """Baja el transcript de un video_id reusando el proxy de prod.

    Returns:
        str   — transcript limpio (puede ser "" si vino vacío).
        ""    — el video genuinamente no tiene subtítulos (fallback válido).
        None  — FALLO DE INFRA (import faltante / red / SSL / parse). Logueado. El caller
                debe SKIPpear el video, no tratarlo como atómico.
    """
    if not video_id:
        logger.error("transcript_fetch: video_id vacío → None (no se puede fetchear)")
        return None

    try:
        from youtube_transcript_api import YouTubeTranscriptApi
    except Exception as e:
        # ESTE es el bug histórico: módulo no instalado → antes "" (se leía como "sin subs").
        logger.error("transcript_fetch: no se pudo importar youtube_transcript_api (%s) "
                     "— FALLO DE INFRA, no 'sin subtítulos'", e)
        return None

    # Excepciones que SÍ significan "sin subtítulos legítimo" (→ "", fallback válido).
    # Import defensivo: si la lib reubica estas clases, _NO_SUBS queda vacío y cualquier
    # fallo cae a None (conservador: mejor skip que fabricar un atómico falso).
    try:
        from youtube_transcript_api._errors import (
            TranscriptsDisabled, NoTranscriptFound, VideoUnavailable,
        )
        _NO_SUBS: tuple = (TranscriptsDisabled, NoTranscriptFound, VideoUnavailable)
    except Exception:
        _NO_SUBS = ()

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
    except _NO_SUBS:
        # sin subtítulos / video sin captions → fallback válido al flujo de hoy
        return ""
    except Exception as e:
        logger.error("transcript_fetch: FALLO DE INFRA al traer transcript de %s (%s) → None",
                     video_id, e)
        return None
