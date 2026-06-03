"""
_lab_outlier_hunter_chat41.py — LAB aislado (chat 41). NO toca el pipeline.

Valida la VIABILIDAD del filtro OUTLIER para Mode A (Viral Hunter English): en vez de
"≥1M vistas", pasar = "ratio ≥3x vs la MEDIANA del canal, AND piso absoluto".

Resuelve 2 incógnitas antes de cablear nada en niche_discoverer:
  A. ¿En qué path del objeto crudo de get_search vive el channelId (UC...)?
  B. ¿get_channel devuelve videos con views parseables (mismo campo que get_search)?

Y EXPONE (no arregla) el bug del decimal de _parse_views_scrapetube ("1.2M"→12M).

Reusa de youtube_scanner: _proxies_dict, detect_language, _parse_views_scrapetube (el
buggy, solo para mostrarlo lado a lado). El parser CORREGIDO vive acá (solo para el lab).

DEV: $0 LLM, solo scraping. NO escribe a disco. Solo print.

USO:
    python _lab_outlier_hunter_chat41.py            # blocks 0/1/2 (scraping real)
    python _lab_outlier_hunter_chat41.py --smoke    # solo funciones puras, sin red
"""
from __future__ import annotations

import re
import statistics
import sys
import time

# Forzar UTF-8 en stdout/stderr (Windows usa cp1252 por defecto).
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

# ─────────────────────────────────────────────────────────────────
#  CONFIG (constantes del lab)
# ─────────────────────────────────────────────────────────────────
TEST_QUERY = "declassified ocean phenomena"   # query del nicho océano
SEARCH_LIMIT = 12      # resultados crudos de la búsqueda
N_CANDIDATES = 5       # sobre cuántos calcular ratio
BASELINE_N = 30        # videos del canal para la mediana
OUTLIER_MIN = 3.0      # ratio mínimo (3x real, 10x joya)
ABS_FLOOR = 80_000     # piso absoluto: corta micro-canales sin demanda real
SLEEP_SEC = 2.0        # anti-ban entre llamadas a scrapetube
MIN_BASELINE_VIDEOS = 5  # < esto → baseline no confiable

# Paths candidatos donde scrapetube esconde el channelId (browseId UC...).
_CHANNEL_ID_PATHS = ["longBylineText", "ownerText", "shortBylineText"]


# ─────────────────────────────────────────────────────────────────
#  FUNCIONES PURAS (las ejerce el smoke — NO reimplementar en el test)
# ─────────────────────────────────────────────────────────────────

def parse_views_fixed(views_text: str) -> int:
    """
    Parser CORREGIDO (solo del lab). Saca SOLO las comas (no el punto), captura
    [\\d.]+ como float, multiplica por k/m/b. Así "1.2M" → 1_200_000 (vs el buggy
    de youtube_scanner que hace .replace(".", "") → "12m" → 12_000_000).
    """
    if not views_text:
        return 0
    t = views_text.lower().replace(",", "")
    m = re.search(r"([\d.]+)\s*([kmb])?", t)
    if not m:
        return 0
    try:
        number = float(m.group(1))
    except ValueError:
        return 0
    mult = {"k": 1_000, "m": 1_000_000, "b": 1_000_000_000, "": 1}
    return int(number * mult.get(m.group(2) or "", 1))


def views_text_of(vid: dict) -> str:
    """Texto crudo de views de un objeto scrapetube (viewCountText / shortViewCountText)."""
    t = (vid.get("viewCountText") or {}).get("simpleText", "")
    if not t:
        t = (vid.get("shortViewCountText") or {}).get("simpleText", "")
    return t or ""


def parse_views_fixed_vid(vid: dict) -> int:
    return parse_views_fixed(views_text_of(vid))


def extract_channel_id(vid: dict) -> tuple[str | None, str | None]:
    """
    Prueba los 3 paths candidatos del channelId. Devuelve (channel_id, path_usado)
    o (None, None) si ninguno matchea un browseId UC...
    """
    for key in _CHANNEL_ID_PATHS:
        try:
            cid = (vid[key]["runs"][0]["navigationEndpoint"]
                   ["browseEndpoint"]["browseId"])
            if isinstance(cid, str) and cid.startswith("UC"):
                return cid, key
        except (KeyError, IndexError, TypeError):
            continue
    return None, None


def median_excluding(values: list[int], exclude_value: int | None = None) -> float | None:
    """Mediana de `values`, opcionalmente quitando UNA ocurrencia de exclude_value
    (no medir el video contra sí mismo). None si quedan < MIN_BASELINE_VIDEOS."""
    vals = [v for v in values if v > 0]
    if exclude_value is not None and exclude_value in vals:
        vals.remove(exclude_value)
    if len(vals) < MIN_BASELINE_VIDEOS:
        return None
    return statistics.median(vals)


def compute_ratio(views: int, baseline: float) -> float:
    return views / baseline if baseline and baseline > 0 else 0.0


def verdict_new(views: int, ratio: float,
                outlier_min: float = OUTLIER_MIN, abs_floor: int = ABS_FLOOR) -> bool:
    """Filtro NUEVO: outlier (ratio) AND piso absoluto."""
    return ratio >= outlier_min and views >= abs_floor


def verdict_old(views: int) -> bool:
    """Filtro VIEJO (para comparar): ≥1M vistas absolutas."""
    return views >= 1_000_000


# ─────────────────────────────────────────────────────────────────
#  SMOKE (sin red) — usa las MISMAS funciones de arriba
# ─────────────────────────────────────────────────────────────────

def run_smoke() -> int:
    print("  SMOKE (funciones puras, sin red)")
    fails: list[str] = []

    cases = [
        ("1.2M views", 1_200_000), ("250K vistas", 250_000),
        ("1,234,567 views", 1_234_567), ("999 views", 999),
        ("3.4B views", 3_400_000_000),
    ]
    for text, exp in cases:
        got = parse_views_fixed(text)
        ok = got == exp
        print(f"    parse_views_fixed({text!r}) = {got:,}  esperado {exp:,}  "
              f"{'OK' if ok else 'FAIL'}")
        if not ok:
            fails.append(f"parse {text!r} → {got} != {exp}")

    # mediana + ratio + veredicto con lista fija
    base = median_excluding([10, 20, 30, 40, 1000])
    print(f"    median([10,20,30,40,1000]) = {base}  esperado 30  "
          f"{'OK' if base == 30 else 'FAIL'}")
    if base != 30:
        fails.append(f"median = {base} != 30")
    ratio = compute_ratio(240, base)
    print(f"    ratio(240 vs 30) = {ratio}  esperado 8.0  {'OK' if ratio == 8.0 else 'FAIL'}")
    if ratio != 8.0:
        fails.append(f"ratio = {ratio} != 8.0")
    # 240 vistas, ratio 8 → outlier sí, pero ABS_FLOOR=80k lo corta (joya muy chica)
    v_small = verdict_new(240, ratio)
    print(f"    verdict_new(240, ratio=8) = {v_small} (esperado False: ABS_FLOOR corta)  "
          f"{'OK' if v_small is False else 'FAIL'}")
    if v_small is not False:
        fails.append("verdict_new(240,8) debería ser False por ABS_FLOOR")
    # 200k vistas, ratio 8 → outlier Y supera piso → True; viejo (≥1M) lo descartaba
    v_jewel = verdict_new(200_000, 8.0)
    v_jewel_old = verdict_old(200_000)
    print(f"    verdict_new(200k, ratio=8) = {v_jewel} | verdict_old(200k) = {v_jewel_old}  "
          f"(nuevo caza la joya que el viejo descarta)  "
          f"{'OK' if (v_jewel and not v_jewel_old) else 'FAIL'}")
    if not (v_jewel and not v_jewel_old):
        fails.append("joya 200k: nuevo debería True, viejo False")
    # exclude_value saca UNA ocurrencia (no medir contra sí mismo).
    # 6 elementos → tras excluir quedan 5 (≥ MIN_BASELINE_VIDEOS).
    base_ex = median_excluding([10, 20, 30, 40, 50, 1000], exclude_value=1000)
    print(f"    median([10..50,1000] exclude 1000) = {base_ex}  esperado 30  "
          f"{'OK' if base_ex == 30 else 'FAIL'}")
    if base_ex != 30:
        fails.append(f"median exclude = {base_ex} != 30")
    # < 5 videos → baseline no confiable → None
    base_few = median_excluding([10, 20, 30])
    print(f"    median([10,20,30]) = {base_few}  esperado None (<5)  "
          f"{'OK' if base_few is None else 'FAIL'}")
    if base_few is not None:
        fails.append(f"median <5 debería None, dio {base_few}")

    print("  " + "─" * 52)
    if fails:
        print(f"  [SMOKE FAIL] {len(fails)}:")
        for f in fails:
            print(f"    - {f}")
        return 1
    print("  [SMOKE OK] funciones puras del lab validadas.")
    return 0


# ─────────────────────────────────────────────────────────────────
#  BLOQUES CON RED
# ─────────────────────────────────────────────────────────────────

def run_live() -> int:
    import scrapetube
    from script_engine.youtube_scanner import (
        _proxies_dict, _parse_views_scrapetube, detect_language,
    )

    proxies = _proxies_dict()

    # ===== BLOQUE 0: sondear channelId =====
    print("\n" + "=" * 64)
    print("  BLOQUE 0 — sondear channelId en get_search")
    print("=" * 64)
    print(f"  query={TEST_QUERY!r} limit={SEARCH_LIMIT}")
    try:
        search_vids = list(scrapetube.get_search(
            TEST_QUERY, limit=SEARCH_LIMIT, proxies=proxies))
    except Exception as e:  # noqa: BLE001
        print(f"  ❌ get_search falló: {type(e).__name__}: {e}")
        return 1
    print(f"  get_search devolvió {len(search_vids)} videos")
    if not search_vids:
        print("  ❌ búsqueda vacía — FRENO")
        return 1

    first = search_vids[0]
    print(f"  keys top-level del 1er video: {sorted(first.keys())}")
    cid, path = extract_channel_id(first)
    if cid:
        print(f"  ✅ GATE 0 OK — channelId = {cid}  (path: {path})")
    else:
        print("  ❌ GATE 0 FALLÓ — ningún path candidato matcheó. Vuelco longBylineText:")
        import json
        print(json.dumps(first.get("longBylineText", "<ausente>"),
                         ensure_ascii=False, indent=2)[:1500])
        print("  FRENO (no seguir a ciegas).")
        return 1

    # ===== BLOQUE 1: sondear get_channel + parseo =====
    print("\n" + "=" * 64)
    print("  BLOQUE 1 — sondear get_channel + parseo de views")
    print("=" * 64)
    time.sleep(SLEEP_SEC)
    print(f"  get_channel(channel_id={cid}, limit={BASELINE_N})")
    chan_vids = _get_channel_videos(scrapetube, cid, BASELINE_N, proxies)
    if not chan_vids:
        print("  ❌ GATE 1 FALLÓ — get_channel no devolvió videos.")
        return 1
    print(f"  get_channel devolvió {len(chan_vids)} videos")
    cfirst = chan_vids[0]
    print(f"  keys top-level del 1er video del canal: {sorted(cfirst.keys())}")
    raw_views = views_text_of(cfirst)
    actual = _parse_views_scrapetube(cfirst)      # parser BUGGY de youtube_scanner
    fixed = parse_views_fixed_vid(cfirst)          # parser CORREGIDO del lab
    print(f"  views crudo: {raw_views!r}")
    print(f"  parser ACTUAL (youtube_scanner, buggy) = {actual:,}")
    print(f"  parser CORREGIDO (lab)                 = {fixed:,}")
    if actual != fixed:
        print(f"  ⚠ BUG DEL DECIMAL VISIBLE: difieren ({actual:,} vs {fixed:,})")
    else:
        print("  (este video no tiene decimal → ambos parsers coinciden)")
    if fixed > 0:
        print(f"  ✅ GATE 1 OK — get_channel parseable, views > 0 ({fixed:,})")
    else:
        print("  ❌ GATE 1 FALLÓ — parser corregido dio 0 sobre el video del canal.")
        return 1

    # ===== BLOQUE 2: mediana + ratio + tabla =====
    print("\n" + "=" * 64)
    print("  BLOQUE 2 — mediana + ratio + tabla comparativa")
    print("=" * 64)

    baseline_cache: dict[str, float | None] = {}
    rows: list[dict] = []
    candidates = [v for v in search_vids if _is_en(v, detect_language)][:N_CANDIDATES]
    print(f"  candidatos EN: {len(candidates)} (de {len(search_vids)} crudos)")

    for vid in candidates:
        title = _title_of(vid)
        views = parse_views_fixed_vid(vid)
        c_id, _ = extract_channel_id(vid)
        baseline = None
        if c_id is not None:
            if c_id not in baseline_cache:
                time.sleep(SLEEP_SEC)
                baseline_cache[c_id] = _channel_baseline(
                    scrapetube, c_id, BASELINE_N, proxies, exclude=views)
            baseline = baseline_cache[c_id]

        ratio = compute_ratio(views, baseline) if baseline else 0.0
        rows.append({
            "title": title, "views": views, "median": baseline, "ratio": ratio,
            "old": verdict_old(views),
            "new": (verdict_new(views, ratio) if baseline else False),
            "no_baseline": baseline is None,
        })

    _print_table(rows)
    print("\n  GATE 2 = de OJO (Omar): ¿el nuevo caza joyas chicas (ratio alto, <1M) que el "
          "viejo descartaba, y rechaza gigantes con ratio bajo que el viejo dejaba pasar?")
    return 0


def _is_en(vid: dict, detect_language) -> bool:
    return detect_language(_title_of(vid)) == "en"


def _title_of(vid: dict) -> str:
    try:
        return vid["title"]["runs"][0]["text"]
    except (KeyError, IndexError, TypeError):
        return "<sin título>"


def _get_channel_videos(scrapetube, channel_id: str, limit: int, proxies: dict) -> list:
    """get_channel con fallback si la versión de scrapetube no acepta proxies."""
    try:
        return list(scrapetube.get_channel(
            channel_id=channel_id, limit=limit, proxies=proxies))
    except TypeError as e:
        print(f"  ⚠ get_channel no aceptó proxies ({e}) → reintento SIN proxies")
        try:
            return list(scrapetube.get_channel(channel_id=channel_id, limit=limit))
        except Exception as e2:  # noqa: BLE001
            print(f"  ❌ get_channel falló sin proxies: {type(e2).__name__}: {e2}")
            return []
    except Exception as e:  # noqa: BLE001
        print(f"  ❌ get_channel falló: {type(e).__name__}: {e}")
        return []


def _channel_baseline(scrapetube, channel_id: str, limit: int, proxies: dict,
                      exclude: int) -> float | None:
    """Mediana de las views (parser corregido) de los uploads del canal,
    excluyendo UNA ocurrencia de `exclude` (el propio video). None si < 5 parseables."""
    vids = _get_channel_videos(scrapetube, channel_id, limit, proxies)
    views_list = [parse_views_fixed_vid(v) for v in vids]
    return median_excluding(views_list, exclude_value=exclude)


def _print_table(rows: list[dict]) -> None:
    print(f"\n  {'título':<44} {'views':>12} {'mediana':>12} {'ratio':>7} "
          f"{'viejo':>6} {'nuevo':>6}")
    print("  " + "─" * 92)
    for r in rows:
        title = (r["title"][:42] + "…") if len(r["title"]) > 43 else r["title"]
        med = f"{r['median']:,.0f}" if r["median"] is not None else "—(<5)"
        ratio = f"{r['ratio']:.1f}x" if r["ratio"] else "—"
        old = "✅" if r["old"] else "·"
        new = "✅" if r["new"] else ("?" if r["no_baseline"] else "·")
        print(f"  {title:<44} {r['views']:>12,} {med:>12} {ratio:>7} {old:>6} {new:>6}")


def run_search_only() -> int:
    """
    Variante SIN get_channel (que cuelga, ver hallazgo chat 41). Solo get_search:
    demuestra el BUG DEL DECIMAL sobre videos reales + tabla de candidatos con views
    y veredicto VIEJO. La columna ratio/nuevo queda N/A (necesita get_channel).
    """
    import scrapetube
    from script_engine.youtube_scanner import (
        _proxies_dict, _parse_views_scrapetube, detect_language,
    )
    print("\n" + "=" * 64)
    print("  SEARCH-ONLY — bug del decimal + candidatos (get_channel cuelga)")
    print("=" * 64)
    try:
        vids = list(scrapetube.get_search(
            TEST_QUERY, limit=SEARCH_LIMIT, proxies=_proxies_dict()))
    except Exception as e:  # noqa: BLE001
        print(f"  ❌ get_search falló: {type(e).__name__}: {e}")
        return 1
    print(f"  get_search devolvió {len(vids)} videos\n")

    print(f"  BUG DEL DECIMAL (parser actual vs corregido):")
    print(f"  {'raw views':<18} {'ACTUAL (buggy)':>16} {'CORREGIDO':>14}  bug?")
    print("  " + "─" * 58)
    diffs = 0
    for v in vids:
        raw = views_text_of(v)
        buggy = _parse_views_scrapetube(v)
        fixed = parse_views_fixed_vid(v)
        flag = ""
        if buggy != fixed:
            flag = "← INFLADO"
            diffs += 1
        print(f"  {raw[:18]:<18} {buggy:>16,} {fixed:>14,}  {flag}")
    print(f"\n  {diffs}/{len(vids)} videos con el bug visible (los que tienen decimal).")

    print(f"\n  CANDIDATOS EN (views corregidas + veredicto VIEJO ≥1M; ratio=N/A):")
    print(f"  {'título':<46} {'views':>12} {'channelId':>26} {'viejo':>6}")
    print("  " + "─" * 94)
    n = 0
    for v in vids:
        title = _title_of(v)
        if detect_language(title) != "en":
            continue
        n += 1
        if n > N_CANDIDATES:
            break
        views = parse_views_fixed_vid(v)
        cid, _ = extract_channel_id(v)
        t = (title[:44] + "…") if len(title) > 45 else title
        print(f"  {t:<46} {views:>12,} {(cid or '—'):>26} {'✅' if verdict_old(views) else '·':>6}")
    print("\n  (ratio/nuevo NO computable: get_channel cuelga vía proxy — ver reporte.)")
    return 0


def main() -> int:
    if "--smoke" in sys.argv:
        return run_smoke()
    if "--searchonly" in sys.argv:
        return run_search_only()
    # smoke siempre primero (barato, sin red), después la red.
    rc = run_smoke()
    if rc != 0:
        print("  smoke falló → no sigo a la red.")
        return rc
    return run_live()


if __name__ == "__main__":
    sys.exit(main())
