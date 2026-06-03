"""
_lab_getchannel_probe_chat41.py — DESTRABAR get_channel (chat 41). Standalone, $0, no
escribe a disco. NO toca el pipeline.

get_search anda por el proxy residencial pero get_channel cuelga (GATE 1 del lab outlier).
Premisa (Omar): el proxy sirve → el blocker es CÓMO se invoca get_channel. Dato clave:
_random_session_id() existe pero NUNCA se llama → search/lab usan IP sticky. La palanca 1
(sesión rotada) nunca se probó.

Prueba 3 palancas, MISMO proxy, cada intento en su PROPIO subprocess con timeout DURO de
30s (regla §1: nada sin timeout; thread no sirve — el ThreadPoolExecutor.shutdown se cuelga
esperando al hilo de scrapetube colgado). islice(gen, 10): no agotar el generador.

  Palanca 1 — sesión ROTADA (3 IPs frescas)         channel_id + proxies(session)
  Palanca 2 — channel_url .../videos                channel_url + proxies(sticky)
  Palanca 3 — sleep explícito + sort_by + rotada    channel_id + sleep=2 + sort_by

Corta en la primera palanca que devuelva videos.

USO:
    python _lab_getchannel_probe_chat41.py
    (interno) python _lab_getchannel_probe_chat41.py --child <lever> <CID>
    (interno) python _lab_getchannel_probe_chat41.py --cid
"""
from __future__ import annotations

import itertools
import subprocess
import sys

# Forzar UTF-8 (Windows cp1252).
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

TEST_QUERY = "declassified ocean phenomena"
SEARCH_LIMIT = 12
CHANNEL_LIMIT = 10
PER_ATTEMPT_TIMEOUT = 30   # §1: timeout duro por intento
N_SESSIONS = 3             # palanca 1: 3 IPs frescas

# Orden de palancas. (s1a/b/c = 3 sesiones frescas de la palanca 1.)
LEVERS = [
    ("P1 sesión rotada #1", "s1"),
    ("P1 sesión rotada #2", "s1"),
    ("P1 sesión rotada #3", "s1"),
    ("P2 channel_url /videos (sticky)", "url"),
    ("P3 sleep=2 + sort_by + rotada", "sleep"),
]


# ─────────────────────────────────────────────────────────────────
#  MODO CHILD — corre UN intento (lo mata el padre por timeout)
# ─────────────────────────────────────────────────────────────────

def _child_cid() -> int:
    """Saca un channelId real vía get_search (eso YA funciona)."""
    import scrapetube
    from script_engine.youtube_scanner import _proxies_dict
    vids = list(scrapetube.get_search(TEST_QUERY, limit=SEARCH_LIMIT, proxies=_proxies_dict()))
    for v in vids:
        try:
            cid = (v["longBylineText"]["runs"][0]["navigationEndpoint"]
                   ["browseEndpoint"]["browseId"])
            title = v["title"]["runs"][0]["text"]
        except (KeyError, IndexError, TypeError):
            continue
        if isinstance(cid, str) and cid.startswith("UC"):
            print(f"CID={cid}")
            print(f"TITLE={title}")
            return 0
    print("CID=NONE")
    return 1


def _child_lever(lever: str, cid: str) -> int:
    import scrapetube
    import statistics
    from script_engine.youtube_scanner import (
        _build_proxy_url, _proxies_dict, _random_session_id, _parse_views_scrapetube,
    )
    import _lab_outlier_hunter_chat41 as L

    if lever in ("s1", "sleep"):
        sess = _random_session_id()
        u = _build_proxy_url(sess)
        proxies = {"http": u, "https": u}
        print(f"SESSION={sess}")
    else:  # url → sticky (sin sesión)
        proxies = _proxies_dict()

    if lever == "s1":
        kwargs = dict(channel_id=cid, limit=CHANNEL_LIMIT, proxies=proxies)
    elif lever == "url":
        kwargs = dict(channel_url=f"https://www.youtube.com/channel/{cid}/videos",
                      limit=CHANNEL_LIMIT, proxies=proxies)
    elif lever == "sleep":
        kwargs = dict(channel_id=cid, limit=CHANNEL_LIMIT, sleep=2,
                      sort_by="newest", proxies=proxies)
    else:
        print("LEVER_DESCONOCIDO")
        return 2

    gen = scrapetube.get_channel(**kwargs)
    vids = list(itertools.islice(gen, CHANNEL_LIMIT))   # NO agotar el generador
    print(f"VIDEOS={len(vids)}")
    if not vids:
        return 0
    v = vids[0]
    vc = (v.get("viewCountText") or {}).get("simpleText", "")
    sc = (v.get("shortViewCountText") or {}).get("simpleText", "")
    print(f"VIEWCOUNT={vc!r}")
    print(f"SHORT={sc!r}")
    print(f"BUGGY={_parse_views_scrapetube(v)}")
    print(f"FIXED={L.parse_views_fixed_vid(v)}")
    allv = [L.parse_views_fixed_vid(x) for x in vids]
    print(f"ALLVIEWS={allv}")
    rest = [x for x in allv if x > 0]
    cand = allv[0]
    if cand in rest:
        rest.remove(cand)
    if rest:
        med = statistics.median(rest)
        print(f"MEDIAN={med}")
        if med:
            print(f"RATIO_EXAMPLE={cand / med:.2f}")
    return 0


# ─────────────────────────────────────────────────────────────────
#  MODO PADRE — orquesta con timeout duro por intento
# ─────────────────────────────────────────────────────────────────

def _spawn(args: list[str], timeout: int) -> tuple[str, str, int | None]:
    """Corre un child en subprocess; lo MATA a los `timeout`s. Devuelve (out, err, rc|None)."""
    try:
        r = subprocess.run(
            [sys.executable, __file__, *args], cwd=".",
            capture_output=True, text=True, encoding="utf-8", errors="replace",
            timeout=timeout)
        return r.stdout, r.stderr, r.returncode
    except subprocess.TimeoutExpired as e:
        return (e.stdout or ""), (e.stderr or ""), None  # rc None = HANG (matado)


def _parse_kv(out: str) -> dict:
    d = {}
    for line in out.splitlines():
        if "=" in line:
            k, _, val = line.partition("=")
            d[k.strip()] = val.strip()
    return d


def main() -> int:
    if "--cid" in sys.argv:
        return _child_cid()
    if "--child" in sys.argv:
        i = sys.argv.index("--child")
        return _child_lever(sys.argv[i + 1], sys.argv[i + 2])

    print("=" * 66)
    print("  PROBE get_channel — 3 palancas, timeout duro 30s/intento")
    print("=" * 66)

    # CID vía get_search (en subprocess con timeout también, por las dudas)
    out, err, rc = _spawn(["--cid"], timeout=40)
    kv = _parse_kv(out)
    cid = kv.get("CID")
    if not cid or cid == "NONE":
        print(f"  ❌ no se pudo sacar channelId vía get_search (rc={rc}). FRENO.")
        print(f"     stderr: {err[-300:]}")
        return 1
    print(f"  channelId de prueba: {cid}  (“{kv.get('TITLE', '?')[:50]}”)")
    print(f"  limit={CHANNEL_LIMIT}, islice(10), timeout={PER_ATTEMPT_TIMEOUT}s/intento\n")

    winner = None
    for label, lever in LEVERS:
        print(f"  → {label} ...", flush=True)
        out, err, rc = _spawn(["--child", lever, cid], timeout=PER_ATTEMPT_TIMEOUT + 3)
        kv = _parse_kv(out)
        if rc is None:
            print(f"     ⏱ HANG (matado a {PER_ATTEMPT_TIMEOUT}s)")
            continue
        if rc != 0 and "VIDEOS" not in kv:
            print(f"     ❌ error rc={rc}: {err.strip()[-200:] or out.strip()[-200:]}")
            continue
        n = int(kv.get("VIDEOS", "0") or "0")
        sess = kv.get("SESSION")
        if n > 0:
            print(f"     ✅ devolvió {n} videos" + (f"  (session={sess})" if sess else ""))
            winner = (label, lever, kv)
            break
        print(f"     ⚠ 0 videos (no colgó, pero canal vacío/bloqueado)"
              + (f"  (session={sess})" if sess else ""))

    print("\n" + "─" * 66)
    if not winner:
        print("  RESULTADO: las palancas probadas NO destrabaron get_channel.")
        print("  Raíz confirmada: endpoint de canal bloqueado/colgado para esta IP, no")
        print("  destrabable por invocación. Próximo paso (otro handoff): YouTube Data API")
        print("  (uploads playlist → videos.list → viewCount; int puro, sin bug del decimal).")
        return 1

    label, lever, kv = winner
    print(f"  ✅ DESTRABÓ: {label}")
    print(f"     config: lever={lever!r}" + (f", session_rotada=sí" if "SESSION" in kv else ", proxies=sticky"))
    print(f"     1er video: viewCount={kv.get('VIEWCOUNT')} short={kv.get('SHORT')}")
    abbreviated = bool(kv.get("SHORT")) and not kv.get("VIEWCOUNT", "").strip("'\"")
    print(f"     parser ACTUAL(buggy)={kv.get('BUGGY')}  CORREGIDO={kv.get('FIXED')}"
          + ("  ← BUG DEL DECIMAL MUERDE (formato abreviado)"
             if kv.get("BUGGY") != kv.get("FIXED") else "  (coinciden acá)"))
    print(f"     views(10)={kv.get('ALLVIEWS')}")
    if kv.get("MEDIAN"):
        print(f"     mediana(excl. candidato)={kv.get('MEDIAN')}  ratio_ejemplo={kv.get('RATIO_EXAMPLE')}x")
    print(f"\n  → Bloque 2 del lab ya puede correr con esta config. Cablear DESPUÉS.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
