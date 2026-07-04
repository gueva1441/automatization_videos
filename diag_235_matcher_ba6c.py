# diag_235_matcher_ba6c.py — LAB (derivado de diag_234_cap4). HANDOFF_135c.
# Barre TODO el topic ba6c3cac e instrumenta el matcher anchor→tiempo (anchor_timing):
# por cada anchor de cada cap: matched_by (3-tokens|fallback-1tok), word_idx, palabra,
# start_s y la duration que fase2b imputaría. Marca ⚠ fallback y ⚠ duration < 1.0s.
# Híbrido veo (ch01/ch07): mide el MP4 veo real (ffprobe) y reproduce la cuenta de fase2b
# (offset, s0 vs banda [offset-0.5, offset), 1a duration imputada). Cruce de versiones de
# audio (mtime + backup _qa_backups → AUDIO REGENERADO POST-m03). SOLO LECTURA, cero API.
import json
import re
from pathlib import Path

from anchor_timing import _norm, _first_n_tokens   # el matcher REAL comparte estos
from fase2b import _get_duration                    # ffprobe, MISMO criterio que fase2b

TOPIC = "ba6c3cac-a091-41c0-8dad-afd2f4364747"
MIN_GAP = 1.0   # MIN_ANCHOR_GAP_SEC de m03

SCRIPT = Path(f"data/scripts/{TOPIC}.json")
AUDIO = Path(f"output/audio/{TOPIC}")
ASSETS = Path(f"output/{TOPIC}/assets")
BACKUPS = ASSETS / "_qa_backups"
OUT_JSON = Path("lab/outputs/diag_235_matcher_ba6c.json")


def _load(p):
    return json.loads(p.read_text(encoding="utf-8", errors="replace"))


def _match_instrumented(anchors, words):
    """Réplica EXACTA de anchor_timing.compute_anchor_starts + instrumentación por anchor
    (matched_by, word_idx, palabra, start). Devuelve (rows, starts, monotonic_ok)."""
    word_norm = [_norm(w.get("word", "")) for w in words]
    rows = []
    starts = []
    cursor = 0
    for ai, anchor in enumerate(anchors):
        needle = _first_n_tokens(anchor, n=3)
        row = {"anchor_idx": ai, "anchor8": " ".join((anchor or "").split()[:8]),
               "needle": needle, "matched_by": None, "word_idx": None,
               "matched_word": None, "start_s": None}
        if not needle:
            row["matched_by"] = "NO-TOKENS"
            rows.append(row); starts.append(None); continue
        found, matched_by = -1, "3-tokens"
        for i in range(cursor, len(words) - len(needle) + 1):
            if word_norm[i:i + len(needle)] == needle:
                found = i; break
        if found < 0:
            for i in range(cursor, len(words)):
                if word_norm[i] == needle[0]:
                    found = i; matched_by = "fallback-1tok"; break
        if found < 0:
            row["matched_by"] = "NO-MATCH"
            rows.append(row); starts.append(None); continue
        st = float(words[found].get("start", 0.0))
        row.update(matched_by=matched_by, word_idx=found,
                   matched_word=words[found].get("word", ""), start_s=round(st, 3))
        rows.append(row); starts.append(st); cursor = found + 1
    mono_ok = all(starts[i] is not None and starts[i - 1] is not None and starts[i] > starts[i - 1]
                  for i in range(1, len(starts))) and all(s is not None for s in starts)
    return rows, starts, mono_ok


def _durations(starts, offset, total):
    """Reproduce fase2b._compute_durations_from_anchors: end_of_segment=offset+total;
    1a imagen (offset>0) cubre [offset, end). Devuelve durations (o None si algún start None)."""
    if any(s is None for s in starts):
        return None
    end_seg = offset + total
    durs = []
    for i in range(len(starts)):
        end = starts[i + 1] if i + 1 < len(starts) else end_seg
        d = (end - offset) if (i == 0 and offset > 0.0) else (end - starts[i])
        durs.append(d)
    return durs


def main():
    script = _load(SCRIPT)
    sync = _load(AUDIO / "sync_map.json")
    dur_by_cap = {cm.get("id"): float(cm.get("duration_sec", 0.0)) for cm in sync.get("chapters", [])}
    manifest_p = ASSETS / "assets_manifest.json"
    manifest = _load(manifest_p) if manifest_p.exists() else {}
    veo_pos_by_cap = {}
    for mc in manifest.get("chapters", []):
        veo_pos_by_cap[mc.get("id")] = mc.get("veo_position", "start")

    print("=" * 100)
    print(f"DIAG #235 — matcher anchor→tiempo — topic {TOPIC[:8]} (COMPLETO)")
    print(f"  ⚠ fallback-1tok = match laxo (sospechoso) · ⚠ dur<{MIN_GAP}s = ventana sub-segundo")
    print("=" * 100)

    out = {"topic": TOPIC, "min_gap": MIN_GAP, "caps": []}

    for cap in script.get("chapters", []):
        n = cap.get("chapter_number")
        cid = f"ch{n:02d}"
        engine = (cap.get("render_engine") or cap.get("engine") or "flux").lower()
        is_veo = engine == "veo"
        anchors = ([sp.get("narration_anchor", "") for sp in (cap.get("supplemental_image_prompts") or [])]
                   if is_veo else
                   [ip.get("narration_anchor", "") for ip in (cap.get("image_prompts") or [])])
        ts_path = AUDIO / f"{cid}_timestamps.json"
        cap_out = {"cap": n, "engine": engine, "anchors": len(anchors), "rows": [],
                   "offset": 0.0, "total": dur_by_cap.get(cid, 0.0), "veo_dur": None,
                   "veo_position": None, "s0_in_band": None, "uniform_fallback": None,
                   "audio_regen_post_m03": None, "timestamps_mtime": None}

        print(f"\n{'─'*100}\nCAP {n}  ·  engine={engine}  ·  {len(anchors)} anchors  ·  audio_total={dur_by_cap.get(cid,0):.1f}s")
        if not ts_path.exists():
            print(f"  !! sin {ts_path.name} — skip"); cap_out["error"] = "no timestamps"; out["caps"].append(cap_out); continue
        words = _load(ts_path)

        # (d) cruce de versiones de audio
        import datetime
        mt = datetime.datetime.fromtimestamp(ts_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M:%S")
        cap_out["timestamps_mtime"] = mt
        bak = list(BACKUPS.glob(f"{cid}_timestamps.json.*.bak")) if BACKUPS.exists() else []
        cap_out["audio_regen_post_m03"] = bool(bak)
        print(f"  timestamps mtime: {mt}" + (f"   ⚠ AUDIO REGENERADO POST-m03 ({len(bak)} backup(s))" if bak else ""))

        # offset/total según engine (reproduce fase2b)
        offset, total = 0.0, dur_by_cap.get(cid, 0.0)
        if is_veo:
            vpos = veo_pos_by_cap.get(cid, "start")
            clip = ASSETS / f"{cid}_veo" / f"{cid}_clip_01.mp4"
            veo_dur = _get_duration(clip) if clip.exists() else None
            cap_out["veo_dur"] = round(veo_dur, 3) if veo_dur else None
            cap_out["veo_position"] = vpos
            if veo_dur is not None:
                total = dur_by_cap.get(cid, 0.0) - veo_dur          # flux_segment_dur
                offset = veo_dur if vpos == "start" else 0.0
            print(f"  VEO: clip_dur={veo_dur:.2f}s pos={vpos} → offset={offset:.2f}s  flux_segment={total:.2f}s"
                  if veo_dur is not None else "  VEO: !! sin clip mp4")
        cap_out["offset"], cap_out["total"] = round(offset, 3), round(total, 3)

        rows, starts, mono_ok = _match_instrumented(anchors, words)
        durs = _durations(starts, offset, total)
        cap_out["uniform_fallback"] = not (mono_ok and durs is not None and all(d > 0.05 for d in durs))

        # (c) híbrido: s0 vs banda
        if is_veo and starts and starts[0] is not None and offset > 0:
            s0 = starts[0]; in_band = s0 >= offset - 0.5
            cap_out["s0_in_band"] = bool(in_band)
            print(f"  s0={s0:.2f}s vs offset={offset:.2f}s → {'OK (dentro de banda)' if in_band else '⚠ ANTES de la banda [offset-0.5, offset)'}")

        # tabla SIEMPRE
        print(f"  {'idx':>3} {'matched_by':<13} {'w#':>5} {'start':>8} {'dur':>8}  anchor(8w)")
        for r in rows:
            i = r["anchor_idx"]
            d = durs[i] if durs is not None else None
            warn = ""
            if r["matched_by"] == "fallback-1tok":
                warn += " ⚠fb"
            if d is not None and d < MIN_GAP:
                warn += " ⚠dur"
            r["duration_s"] = round(d, 3) if d is not None else None
            dstr = f"{d:8.2f}" if d is not None else "     n/a"
            stx = f"{r['start_s']:8.2f}" if r["start_s"] is not None else "     n/a"
            w = r["word_idx"] if r["word_idx"] is not None else "-"
            print(f"  {i:>3} {str(r['matched_by']):<13} {str(w):>5} {stx} {dstr}  {r['anchor8']}{warn}")
        if cap_out["uniform_fallback"]:
            print("  >>> El matcher NO produce durations válidas → fase2b CAE A UNIFORME.")
        cap_out["rows"] = rows
        out["caps"].append(cap_out)

    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    # resumen
    n_fb = sum(1 for c in out["caps"] for r in c["rows"] if r.get("matched_by") == "fallback-1tok")
    n_sub = sum(1 for c in out["caps"] for r in c["rows"] if (r.get("duration_s") or 9) < MIN_GAP)
    n_uni = sum(1 for c in out["caps"] if c.get("uniform_fallback"))
    print(f"\n{'='*100}\nRESUMEN: {n_fb} anchors por fallback-1tok · {n_sub} durations < {MIN_GAP}s · "
          f"{n_uni} cap(s) a uniforme")
    print(f"escrito {OUT_JSON}")


if __name__ == "__main__":
    main()
