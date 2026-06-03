"""
_lab_molde1_chat42.py — LAB Molde 1 (chat 42). AISLADO. NO toca el pipeline. CERO API
de pago (no Gemini/Flux/Veo). Solo scraping vía el proxy. Imprime a consola (+ opcional
un json en _lab_out/).

Molde 1: el territorio lo define Omar (PUERTAS fijas por subnicho), los TEMAS los traen
los datos, el filtro outlier separa la joya del ruido. Gemini queda FUERA.

  puerta fija → get_search → candidatos EN
    → por candidato: canal → get_channel (FORK #73) → mediana del canal
    → ratio = views_video / mediana_canal
    → PASA si ratio ≥ 3.0 AND views ≥ 80.000
    → ranking de joyas por ratio desc

Reusa TAL CUAL las funciones validadas del lab 41 (smoke verde): parser, mediana, ratio,
veredictos, extract_channel_id, _get_channel_videos, run_smoke. Los extractores del FORK
(estructura nueva lockup/metadataRows) son NUEVOS y viven acá (BLOQUE 3).

USO:
    python _lab_molde1_chat42.py --smoke   # BLOQUE 0 (puras, sin red)
    python _lab_molde1_chat42.py           # smoke → si OK → BLOQUES 1-5 (red real)
"""
from __future__ import annotations

import json
import sys
import time
from datetime import datetime
from pathlib import Path

# Forzar UTF-8 (Windows cp1252).
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ── Reusar del lab 41 (validado, smoke verde) — importar, no reescribir ──
from _lab_outlier_hunter_chat41 import (   # noqa: E402
    parse_views_fixed,
    parse_views_fixed_vid,
    median_excluding,
    compute_ratio,
    verdict_new,
    verdict_old,
    extract_channel_id,
    _get_channel_videos,
    _title_of,
    run_smoke,
    SEARCH_LIMIT,
    N_CANDIDATES,
    BASELINE_N,
    ABS_FLOOR,
    SLEEP_SEC,
)

# ── PUERTAS (config del lab — Omar las definió) ──
PUERTAS = {
    "espacio": [
        "nasa declassified space mysteries",
        "unexplained cosmic anomalies",
        "lost space missions secrets",
    ],
    "oceano": [
        "deep ocean mysteries unexplained",
        "terrifying ocean discoveries",
        "declassified ocean phenomena",
    ],
    "historias": [],   # SLOT VACÍO — el lab lo saltea sin error.
}

LAB_OUT = Path("_lab_out")


# ─────────────────────────────────────────────────────────────────
#  Extractores del FORK (estructura nueva get_channel) — NUEVOS (BLOQUE 3)
# ─────────────────────────────────────────────────────────────────

def _fork_metadata_rows(vid: dict) -> list:
    try:
        return (vid["metadata"]["lockupMetadataViewModel"]["metadata"]
                ["contentMetadataViewModel"]["metadataRows"])
    except (KeyError, TypeError):
        return []


def fork_views_text(vid: dict) -> str:
    """Recorre TODAS las metadataRows → metadataParts; identifica la parte de VIEWS y
    devuelve su número COMPACTO (text.content, ej '2.2K' o '191 views') para parsear.

    Robusto (sondeado chat 42): la estructura VARÍA por canal —
      - unos: text.content='191 views' (la palabra está en el content)
      - otros: text.content='2.2K' + accessibilityLabel='2.2 thousand views'
        (la palabra solo está en el label, el número compacto en content).
    Por eso identifico la parte por content O label que contenga 'view'/'vista', y
    devuelvo el content (compacto, que parse_views_fixed sabe leer: '2.2K'→2200)."""
    for row in _fork_metadata_rows(vid):
        for part in (row.get("metadataParts") or []):
            txt = (((part or {}).get("text") or {}).get("content")) or ""
            label = ((part or {}).get("accessibilityLabel")) or ""
            if any(w in s.lower() for s in (txt, label) for w in ("view", "vista")):
                return txt or label
    return ""


def fork_title(vid: dict) -> str:
    # En el fork night-0909, v["title"] es un STRING pelado (sondeado chat 42), no
    # {"content": ...}. Soportar ambas formas por robustez.
    t = vid.get("title")
    if isinstance(t, str):
        return t or "<sin título>"
    if isinstance(t, dict):
        return t.get("content") or "<sin título>"
    return "<sin título>"


def fork_views(vid: dict) -> int:
    return parse_views_fixed(fork_views_text(vid))


# ─────────────────────────────────────────────────────────────────
#  BLOQUE 1 — confirmar el FORK instalado (no el oficial)
# ─────────────────────────────────────────────────────────────────

def _scrapetube_install_info() -> tuple[str, str | None, bool]:
    import importlib.metadata as md
    d = md.distribution("scrapetube")
    ver = d.version
    try:
        du = d.read_text("direct_url.json")
    except Exception:  # noqa: BLE001
        du = None
    is_fork = bool(du) and ("night-0909" in du)
    return ver, du, is_fork


def _check_fork() -> bool:
    ver, du, is_fork = _scrapetube_install_info()
    print(f"  scrapetube versión: {ver}")
    print(f"  direct_url.json: {du if du else '<none> (instalado de PyPI = oficial)'}")
    if is_fork:
        print("  ✅ GATE 1 OK — fork night-0909 instalado.")
        return True
    print("  ❌ GATE 1 FRENO — está el scrapetube OFICIAL, no el fork.")
    print("     get_channel sigue muerto sin el fork. Instalá:")
    print("     pip install --force-reinstall git+https://github.com/night-0909/scrapetube")
    print("     ⚠ OJO: ese --force-reinstall reemplaza scrapetube GLOBAL → también se lo")
    print("     come el pipeline (youtube_scanner.get_search). Validar que search sigue OK.")
    return False


# ─────────────────────────────────────────────────────────────────
#  BLOQUES CON RED
# ─────────────────────────────────────────────────────────────────

def run_live() -> int:
    import scrapetube
    from script_engine.youtube_scanner import _proxies_dict, detect_language
    proxies = _proxies_dict()

    # ===== BLOQUE 1 =====
    print("\n" + "=" * 66)
    print("  BLOQUE 1 — ¿está el fork night-0909 (no el oficial 2.6.0)?")
    print("=" * 66)
    if not _check_fork():
        return 1

    # channelId conocido para sondear (de una puerta cualquiera)
    seed_query = next(q for qs in PUERTAS.values() for q in qs)
    print(f"\n  seed get_search: {seed_query!r}")
    seed_vids = list(scrapetube.get_search(seed_query, limit=SEARCH_LIMIT, proxies=proxies))
    # extract_channel_id (lab 41) devuelve TUPLA (channel_id, path) → tomar [0].
    seed_cid = None
    for v in seed_vids:
        c = extract_channel_id(v)[0]
        if c:
            seed_cid = c
            break
    if not seed_cid:
        print("  ❌ no se pudo sacar channelId del seed. FRENO.")
        return 1
    print(f"  channelId seed: {seed_cid}")

    # ===== BLOQUE 2 — sondear estructura cruda del fork =====
    print("\n" + "=" * 66)
    print("  BLOQUE 2 — sondear get_channel del fork (estructura cruda)")
    print("=" * 66)
    time.sleep(SLEEP_SEC)
    chan_vids = _get_channel_videos(scrapetube, seed_cid, 3, proxies)
    if not chan_vids:
        print("  ❌ get_channel (fork) no devolvió videos. FRENO.")
        return 1
    cv = chan_vids[0]
    print(f"  keys top-level del 1er video del canal: {sorted(cv.keys())}")
    rows = _fork_metadata_rows(cv)
    if not rows:
        print("  ❌ GATE 2 FRENO — path esperado (metadataRows) NO existe. Crudo:")
        print(json.dumps(cv, ensure_ascii=False, indent=2)[:2000])
        return 1
    print(f"  metadataRows ({len(rows)} filas):")
    print(json.dumps(rows, ensure_ascii=False, indent=2)[:2000])
    print(f"  título (fork): {fork_title(cv)!r}")
    print(f"  views_text (fork): {fork_views_text(cv)!r}")

    # ===== BLOQUE 3 — extractor + views > 0 =====
    print("\n" + "=" * 66)
    print("  BLOQUE 3 — extractor del fork: fork_views > 0 en la mayoría")
    print("=" * 66)
    vals = [fork_views(v) for v in chan_vids]
    pos = sum(1 for x in vals if x > 0)
    print(f"  fork_views sobre {len(chan_vids)} videos: {vals}  ({pos}/{len(chan_vids)} > 0)")
    if pos == 0:
        print("  ❌ GATE 3 FRENO — todos 0; extractor/path mal. No sigo a mediana basura.")
        return 1
    print("  ✅ GATE 3 OK")

    # ===== BLOQUE 4 — cadena Molde 1 multi-puerta =====
    print("\n" + "=" * 66)
    print("  BLOQUE 4 — cadena Molde 1 (todas las puertas)")
    print("=" * 66)
    baseline_cache: dict[str, float | None] = {}
    all_rows: list[dict] = []
    for subnicho, puertas in PUERTAS.items():
        if not puertas:
            print(f"  [{subnicho}] sin puertas → salteado")
            continue
        for puerta in puertas:
            print(f"\n  [{subnicho}] puerta: {puerta!r}")
            time.sleep(SLEEP_SEC)
            try:
                vids = list(scrapetube.get_search(puerta, limit=SEARCH_LIMIT, proxies=proxies))
            except Exception as e:  # noqa: BLE001
                print(f"     ⚠ get_search falló: {type(e).__name__}: {e}")
                continue
            cands = [v for v in vids if detect_language(_title_of(v)) == "en"][:N_CANDIDATES]
            print(f"     candidatos EN: {len(cands)}")
            for vid in cands:
                title = _title_of(vid)
                views = parse_views_fixed_vid(vid)
                cid = extract_channel_id(vid)[0]   # lab 41 devuelve (id, path)
                baseline = None
                if cid:
                    if cid not in baseline_cache:
                        time.sleep(SLEEP_SEC)
                        ups = _get_channel_videos(scrapetube, cid, BASELINE_N, proxies)
                        upviews = [fork_views(u) for u in ups]
                        baseline_cache[cid] = median_excluding(upviews, exclude_value=views)
                    baseline = baseline_cache[cid]
                ratio = compute_ratio(views, baseline) if baseline else 0.0
                all_rows.append({
                    "subnicho": subnicho, "puerta": puerta, "title": title,
                    "views": views, "median": baseline, "ratio": ratio,
                    "old": verdict_old(views),
                    "new": (verdict_new(views, ratio) if baseline else False),
                    "no_baseline": baseline is None,
                    "video_id": vid.get("videoId", ""),
                })

    # ===== BLOQUE 5 — ranking + tabla =====
    print("\n" + "=" * 66)
    print("  BLOQUE 5 — tabla + ranking de joyas")
    print("=" * 66)
    _print_table_molde(all_rows)
    jewels = sorted([r for r in all_rows if r["new"]], key=lambda r: r["ratio"], reverse=True)
    print(f"\n  💎 JOYAS (ratio ≥ 3.0 AND views ≥ 80k) — {len(jewels)}:")
    if not jewels:
        print("     (ninguna pasó el filtro — ver distribución arriba)")
    for r in jewels:
        t = (r["title"][:50] + "…") if len(r["title"]) > 51 else r["title"]
        print(f"     {r['ratio']:>6.1f}x  {r['views']:>10,}  [{r['subnicho']}] {t}")

    # opcional: dump json (análisis, NO pipeline)
    try:
        LAB_OUT.mkdir(exist_ok=True)
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        out = LAB_OUT / f"molde1_chat42_{ts}.json"
        out.write_text(json.dumps(all_rows, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\n  análisis guardado: {out}")
    except Exception as e:  # noqa: BLE001
        print(f"  (no se pudo guardar json: {type(e).__name__})")

    print("\n  GATE de OJO (Omar): ¿joyas DEL nicho o drift? ¿caza chicas <1M que el viejo "
          "tiraba? ¿rechaza gigantes en su nivel normal que el viejo dejaba pasar?")
    return 0


def _print_table_molde(rows: list[dict]) -> None:
    print(f"\n  {'subnicho':<9} {'título':<38} {'views':>11} {'mediana':>11} "
          f"{'ratio':>7} {'viejo':>6} {'nuevo':>6}")
    print("  " + "─" * 96)
    for r in rows:
        t = (r["title"][:36] + "…") if len(r["title"]) > 37 else r["title"]
        med = f"{r['median']:,.0f}" if r["median"] is not None else "—(<5)"
        ratio = f"{r['ratio']:.1f}x" if r["ratio"] else "—"
        old = "✅" if r["old"] else "·"
        new = "✅" if r["new"] else ("?" if r["no_baseline"] else "·")
        print(f"  {r['subnicho']:<9} {t:<38} {r['views']:>11,} {med:>11} "
              f"{ratio:>7} {old:>6} {new:>6}")


def main() -> int:
    if "--smoke" in sys.argv:
        return run_smoke()
    rc = run_smoke()
    if rc != 0:
        print("  smoke falló → no sigo a la red.")
        return rc
    return run_live()


if __name__ == "__main__":
    sys.exit(main())
