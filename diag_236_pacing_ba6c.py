# diag_236_pacing_ba6c.py — LAB (derivado de diag_235_matcher_ba6c). HANDOFF_135g.
# Auditoría de PACING de la corrida REAL de ba6c3cac (cero API, cero regen, solo lee disco).
# Por cada imagen de cada cap cruza 3 fuentes:
#   (a) DURACIÓN REAL de la ventana — llama al MISMO fase2b._compute_durations_from_anchors
#       con el offset híbrido veo real (ffprobe del clip, como el 235) + el fallback uniforme
#       (total/n) si el matcher devuelve None. Marca source: anchors|uniforme.
#   (b) MODO 135d — loop_7s si dur>9.0 (LOOP_THRESHOLD_S = CYCLE_S 7 + 2), si no ciclo_unico;
#       columna ciclos = dur/7 (cuántas repeticiones ve el espectador).
#   (c) MOVIMIENTO — movement/intensity/steady del cap desde output/<tid>/flow_plan.json;
#       si la imagen tiene zoom_promotion, se marca con su categoría (movimiento efectivo zoom_in).
#   (d) RESUMEN al pie — bins de duración, conteo por modo/movement, top-5 largas, hook (ch01).
# SOLO LECTURA. No toca producción. El lab ES la evidencia.
import json
import datetime
from pathlib import Path

from anchor_timing import compute_anchor_starts                    # matcher REAL (para start_s)
from fase2b import _get_duration, _compute_durations_from_anchors  # ffprobe + cuenta REAL de ventanas

TOPIC = "ba6c3cac-a091-41c0-8dad-afd2f4364747"

# Constantes replicadas de script_engine/parallax_animator_v2.py (135d) — no se importa
# el módulo para no arrastrar DepthFlow; los valores son los validados al ojo.
CYCLE_S = 7.0                    # _DURATION_REFERENCE_S
LOOP_THRESHOLD_S = 9.0           # CYCLE_S + 2.0

SCRIPT = Path(f"data/scripts/{TOPIC}.json")
AUDIO = Path(f"output/audio/{TOPIC}")
ASSETS = Path(f"output/{TOPIC}/assets")
FLOW_PLAN = Path(f"output/{TOPIC}/flow_plan.json")
OUT_JSON = Path("lab/outputs/diag_236_pacing_ba6c.json")


def _load(p):
    return json.loads(p.read_text(encoding="utf-8", errors="replace"))


def _mode(dur):
    """Modo 135d + ciclos para una ventana de `dur` segundos."""
    m = "loop_7s" if dur > LOOP_THRESHOLD_S else "ciclo_unico"
    return m, round(dur / CYCLE_S, 1)


def _dur_bin(dur):
    if dur < 2.0:
        return "<2"
    if dur < 4.0:
        return "2-4"
    if dur < 6.0:
        return "4-6"
    if dur <= 9.0:
        return "6-9"
    return ">9"


BINS_ORDER = ["<2", "2-4", "4-6", "6-9", ">9"]


def main():
    script = _load(SCRIPT)
    sync = _load(AUDIO / "sync_map.json")
    dur_by_cap = {cm.get("id"): float(cm.get("duration_sec", 0.0)) for cm in sync.get("chapters", [])}

    manifest_p = ASSETS / "assets_manifest.json"
    manifest = _load(manifest_p) if manifest_p.exists() else {}
    veo_pos_by_cap = {mc.get("id"): mc.get("veo_position", "start") for mc in manifest.get("chapters", [])}

    # (c) flow_plan: movement/intensity/steady por cap + zoom_promotions por imagen
    flow = _load(FLOW_PLAN) if FLOW_PLAN.exists() else {}
    spec_by_cap = {}   # cid -> {"movement","intensity","steady"} o None
    for ch in flow.get("chapters", []):
        fs = ch.get("flow_spec")
        spec_by_cap[ch.get("chapter_id")] = (
            {"movement": fs.get("movement"),
             "intensity": fs.get("intensity_base"),
             "steady": fs.get("steady")}
            if fs else None
        )
    # promotions: cid -> {image_stem: categoria}
    promo_by_cap = {}
    for cid, promos in (flow.get("zoom_promotions") or {}).items():
        promo_by_cap[cid] = {pr["image"]: pr.get("categoria") for pr in promos}

    print("=" * 108)
    print(f"DIAG #236 — PACING corrida real — topic {TOPIC[:8]}  (duración × modo loop × movimiento)")
    print(f"  LOOP_THRESHOLD_S={LOOP_THRESHOLD_S} (dur>{LOOP_THRESHOLD_S}→loop_7s) · CYCLE_S={CYCLE_S} · ciclos=dur/{CYCLE_S:.0f}")
    print("=" * 108)

    out = {"topic": TOPIC, "loop_threshold_s": LOOP_THRESHOLD_S, "cycle_s": CYCLE_S, "caps": []}
    all_rows = []   # aplanado, para el resumen (d)

    for cap in script.get("chapters", []):
        n_num = cap.get("chapter_number")
        cid = f"ch{n_num:02d}"
        engine = (cap.get("render_engine") or cap.get("engine") or "flux").lower()
        is_veo = engine == "veo"
        kind = "supp" if is_veo else "img"   # sufijo del stem del PNG animado
        anchors = ([sp.get("narration_anchor", "") for sp in (cap.get("supplemental_image_prompts") or [])]
                   if is_veo else
                   [ip.get("narration_anchor", "") for ip in (cap.get("image_prompts") or [])])
        n = len(anchors)
        ts_path = AUDIO / f"{cid}_timestamps.json"
        cap_spec = spec_by_cap.get(cid)
        cap_promos = promo_by_cap.get(cid, {})

        cap_out = {"cap": n_num, "engine": engine, "images": n, "offset": 0.0,
                   "total": dur_by_cap.get(cid, 0.0), "veo_dur": None, "veo_position": None,
                   "source": None, "flow_spec": cap_spec, "rows": []}

        print(f"\n{'─'*108}\nCAP {n_num}  ·  engine={engine}  ·  {n} imgs  ·  audio_total={dur_by_cap.get(cid,0):.1f}s"
              + (f"  ·  flow=[{cap_spec['movement']} i={cap_spec['intensity']} s={cap_spec['steady']}]"
                 if cap_spec else "  ·  flow=None (veo o sin spec en flow_plan)"))

        if n == 0:
            print("  (sin imágenes animadas — clip puro)")
            out["caps"].append(cap_out); continue
        if not ts_path.exists():
            print(f"  !! sin {ts_path.name} — skip"); cap_out["error"] = "no timestamps"
            out["caps"].append(cap_out); continue

        # offset/total híbrido (reproduce fase2b, idéntico al 235)
        offset, total = 0.0, dur_by_cap.get(cid, 0.0)
        if is_veo:
            vpos = veo_pos_by_cap.get(cid, "start")
            clip = ASSETS / f"{cid}_veo" / f"{cid}_clip_01.mp4"
            veo_dur = _get_duration(clip) if clip.exists() else None
            cap_out["veo_dur"] = round(veo_dur, 3) if veo_dur else None
            cap_out["veo_position"] = vpos
            if veo_dur is not None:
                total = dur_by_cap.get(cid, 0.0) - veo_dur       # flux_segment_dur
                offset = veo_dur if vpos == "start" else 0.0
                print(f"  VEO: clip_dur={veo_dur:.2f}s pos={vpos} → offset={offset:.2f}s  flux_segment={total:.2f}s")
            else:
                print("  VEO: !! sin clip mp4 — offset=0")
        cap_out["offset"], cap_out["total"] = round(offset, 3), round(total, 3)

        # (a) DURACIÓN REAL — la MISMA cuenta que fase2b, con fallback uniforme si devuelve None
        durs = _compute_durations_from_anchors(anchors, ts_path, total, start_offset_sec=offset)
        if durs is not None:
            source = "anchors"
        else:
            durs = [total / n] * n if n else []          # fase2b: [total_duration/n]*n
            source = "uniforme"
        cap_out["source"] = source

        # start_s por imagen (solo informativo; puede ser None si el matcher no cerró)
        words = _load(ts_path)
        starts = compute_anchor_starts(anchors, words)   # None o lista de floats

        if source == "uniforme":
            print(f"  ⚠ matcher NO cerró → source=UNIFORME (cada img = {total:.1f}/{n} = {total/n:.2f}s)")
        else:
            print(f"  source=anchors (ventanas reales por narración)")

        print(f"  {'img':<14} {'start':>8} {'dur':>8} {'modo':<12} {'ciclos':>7} {'movement':<12} {'zoom?':<18}")
        for i in range(n):
            d = durs[i]
            mode, ciclos = _mode(d)
            stem = f"{cid}_{kind}_{i+1:02d}"
            zoom_cat = cap_promos.get(stem)              # categoría si fue promovida, si no None
            base_mov = cap_spec["movement"] if cap_spec else None
            eff_mov = "zoom_in" if zoom_cat else base_mov
            st = starts[i] if (starts is not None and i < len(starts)) else None
            row = {
                "img": stem, "img_idx": i + 1, "source": source,
                "start_s": round(st, 3) if st is not None else None,
                "duration_s": round(d, 3),
                "mode": mode, "ciclos": ciclos, "bin": _dur_bin(d),
                "cap_movement": base_mov, "effective_movement": eff_mov,
                "intensity": cap_spec["intensity"] if cap_spec else None,
                "steady": cap_spec["steady"] if cap_spec else None,
                "zoom_promotion": zoom_cat,
            }
            cap_out["rows"].append(row)
            all_rows.append({**row, "cap": n_num, "engine": engine})
            warn = " ⚠loop" if mode == "loop_7s" else ""
            zstr = f"ZOOM:{zoom_cat}" if zoom_cat else ""
            ststr = f"{st:8.2f}" if st is not None else "     n/a"
            print(f"  {stem:<14} {ststr} {d:8.2f} {mode:<12} {ciclos:>7} {str(base_mov):<12} {zstr:<18}{warn}")

        out["caps"].append(cap_out)

    # ═══════════════ (d) RESUMEN ═══════════════
    OUT_JSON.parent.mkdir(parents=True, exist_ok=True)
    OUT_JSON.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")

    n_imgs = len(all_rows)
    print(f"\n{'='*108}\nRESUMEN PACING — {n_imgs} imágenes animadas en {len(out['caps'])} caps")
    print("=" * 108)

    # distribución de duraciones (bins)
    bins = {b: 0 for b in BINS_ORDER}
    for r in all_rows:
        bins[r["bin"]] += 1
    print("\n  Distribución de duraciones (segundos por imagen):")
    for b in BINS_ORDER:
        c = bins[b]
        bar = "█" * c
        print(f"    {b:>4}s  {c:>3}  {bar}")

    # conteo por modo
    modes = {}
    for r in all_rows:
        modes[r["mode"]] = modes.get(r["mode"], 0) + 1
    print("\n  Conteo por modo 135d:")
    for m, c in sorted(modes.items(), key=lambda kv: -kv[1]):
        pct = 100.0 * c / n_imgs if n_imgs else 0
        print(f"    {m:<12} {c:>3}  ({pct:.0f}%)")

    # conteo por movement efectivo (lo que el espectador ve)
    movs = {}
    for r in all_rows:
        key = str(r["effective_movement"])
        movs[key] = movs.get(key, 0) + 1
    print("\n  Conteo por movement efectivo (zoom_in = promoción aplicada):")
    for m, c in sorted(movs.items(), key=lambda kv: -kv[1]):
        print(f"    {m:<12} {c:>3}")

    # top-5 imágenes más largas
    top = sorted(all_rows, key=lambda r: -r["duration_s"])[:5]
    print("\n  Top-5 imágenes más largas (ventana → modo · movement):")
    for r in top:
        print(f"    {r['img']:<14} {r['duration_s']:6.2f}s  {r['mode']:<12} {r['ciclos']}×  "
              f"{r['effective_movement']}")

    # HOOK: ch01 detalle completo (zona de retención crítica)
    hook = [r for r in all_rows if r["cap"] == 1]
    print(f"\n  HOOK ch01 — {len(hook)} imágenes (zona de retención crítica):")
    if not hook:
        print("    (ch01 sin imágenes animadas por anchor — clip veo puro / sin supplementals)")
    for r in hook:
        z = f" · ZOOM:{r['zoom_promotion']}" if r["zoom_promotion"] else ""
        print(f"    {r['img']:<14} start={r['start_s']}  dur={r['duration_s']:.2f}s  "
              f"{r['mode']} ({r['ciclos']}×)  mov={r['effective_movement']} src={r['source']}{z}")

    n_uni = sum(1 for c in out["caps"] if c.get("source") == "uniforme")
    n_loop = modes.get("loop_7s", 0)
    n_zoom = sum(1 for r in all_rows if r["zoom_promotion"])
    print(f"\n  TL;DR: {n_loop}/{n_imgs} imgs en loop_7s · {n_zoom} promovidas a zoom_in · "
          f"{n_uni} cap(s) con ventanas UNIFORMES (matcher no cerró)")
    print(f"\nescrito {OUT_JSON}")


if __name__ == "__main__":
    main()
