"""LAB chat 44 — checkpoint hueco ES paralelizado (3 workers). Aislado, no toca producción."""
from concurrent.futures import ThreadPoolExecutor, as_completed
from niche_discoverer import (
    _run_spy_arbitrage, _gemini_translate_viral_titles, _build_seed, _save_seeds,
    extract_anchors, ROOT_NICHES,
    SPY_ES_MIN_VIEWS, SPY_ES_WINDOW_MONTHS, SPY_MAX_COMPETING_FOR_GAP,
)
from script_engine.youtube_scanner import count_competing_spanish

WORKERS = 3
all_viral = _run_spy_arbitrage(list(ROOT_NICHES.keys()), dry_run=True)   # scanner real (dur + outlier paralelo)
print(f"\n>>> candidatos del scanner: {len(all_viral)}")
translated = _gemini_translate_viral_titles(all_viral)
evidence_by_vid = {v.get("video_id"): v for v in all_viral}

def check_gap(item):
    if not item["spanish_topic"]:
        return None
    anchors = extract_anchors(item["spanish_topic"])
    comp = count_competing_spanish(item["spanish_topic"], min_views=SPY_ES_MIN_VIEWS,
                                   window_months=SPY_ES_WINDOW_MONTHS, anchors=anchors)
    return (item, anchors, comp)

results = []
with ThreadPoolExecutor(max_workers=WORKERS) as ex:
    for fut in as_completed([ex.submit(check_gap, it) for it in translated]):
        r = fut.result()
        if r:
            results.append(r)

seeds, errors_es = [], 0
for item, anchors, comp in results:
    if comp["competing_count"] < 0:
        errors_es += 1
        continue
    if comp["competing_count"] <= SPY_MAX_COMPETING_FOR_GAP:
        ev = evidence_by_vid.get(item["video_id"]) or {}
        seeds.append(_build_seed(
            title=item["spanish_topic"], mode="spy_arbitrage", root_niche=item["root_niche"],
            evidence={
                "en_viral": {"original_title": item["original_title"], "views": item["views"],
                    "video_id": item["video_id"], "query": item["source_query"],
                    "channel_median": ev.get("median"), "outlier_ratio": ev.get("ratio"),
                    "passed_reason": ev.get("passed_reason")},
                "es_gap": {"competing_count": comp["competing_count"], "window_months": SPY_ES_WINDOW_MONTHS,
                    "min_views_threshold": SPY_ES_MIN_VIEWS, "anchors_used": comp.get("anchors_used", []),
                    "top_titles": comp.get("top_titles", []), "source": comp.get("source", "unknown")},
            }))

_save_seeds(seeds)
print(f"\n>>> HUECOS ES (seeds): {len(seeds)}  ·  errores competencia ES: {errors_es}")
for s in seeds:
    ev = s["evidence"]["en_viral"]; gap = s["evidence"]["es_gap"]
    print(f"  [{s.get('root_niche')}] {s['seed_title']} | comp_ES={gap['competing_count']} "
          f"| EN: {ev['original_title'][:50]} ({ev['views']:,}v, ratio {ev.get('outlier_ratio')})")
