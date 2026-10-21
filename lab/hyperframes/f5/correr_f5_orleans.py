"""F5 §3 — Guion v2 de Orleans sobre una COPIA del research (sin imágenes, sin render). v1 queda intacto.

Etapas (cada una idempotente; `--etapa todo` corre las 4 en orden):
    guion    4a·pool (reusa 00_pool_etiquetado.json; los verified_facts de v1 NO se tocan) → skeleton → narración
             → normalizer (batch, sin escribir el custom_dict global) → juez narrativo de v1 y de v2
    script   data/scripts/<V2>.json = guion de v1 (mismas imágenes/prompts) con la narración v2 + evidence_pool
    sim_v1   director + fragmentos + crítico en modo plan (sin HyperFrames) sobre v1, con el código de hoy
    sim_v2   lo mismo sobre v2, usando las fotos de v1 como proxy: palabras de v2 repartidas en la duración del
             audio de v1 y escenas en los MISMOS tiempos que v1 (anchors sintéticos de 4 palabras de v2)
    visual   (F5b S6 / §1.6) SOLO los prompts de imagen de v2 (texto, sin imágenes): m03 con el canon + UBICACIONES
             DOCUMENTADAS; duraciones de v1 y sin timestamps de v2 (no hay audio de v2)
    versionar copia lo de v2 a lab/hyperframes/f5/v2/ (la versión F5 queda en lab/hyperframes/f5/v2_f5/)
F5b: antes de regenerar, la corrida F5 se respalda (v2_f5/ y output/<V2>/_bak_f5b_pre/): el caché del director no
depende de la narración, así que la simulación de v2 arranca en un work dir limpio.
F5c: el skeleton queda CONGELADO en el de F5 (`f5c/01a_skeleton_F5_e7b661c.json`, token skeleton_frozen; los ids se
traducen al pool de F5b) y el narrador es Gemini Pro con el mejor de 3 por cap. La corrida F5b se respalda en
lab/…/v2_f5b y output/<V2>/_bak_f5c_pre. El costo del guion (Flash y Pro) sale del cost_tracker y va al log.
F5d: el skeleton congelado pasa además por `finalize_pool_plan` (cifras canónicas + datos reservados para
pantalla); la corrida F5c se respalda en lab/…/v2_f5c y output/<V2>/_bak_f5d_pre.
Uso: PYTHONIOENCODING=utf-8 python lab/hyperframes/f5/correr_f5_orleans.py --etapa todo
"""
from __future__ import annotations

import argparse
import re
import json
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

V1 = "ba6c3cac-a091-41c0-8dad-afd2f4364747"
V2 = "ba6c3cac-f5v2"
STEPS = ROOT / "data" / "scripts" / "_steps"
OUT = ROOT / "output"
LAB = Path(__file__).resolve().parent
W1 = OUT / V1 / "_fase2b_work"
SIM_V1 = OUT / V1 / "_fase2b_work_f5sim_v1"
SIM_V2 = OUT / V2 / "_fase2b_work"
HOOK = 1.8                                  # fase2b.HOOK_DURATION (pre-pad del ch01)


def _load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def _dump(p: Path, d) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


FROZEN = {"skeleton": str(LAB / "f5c" / "01a_skeleton_F5_e7b661c.json"),
          "pool": str(LAB / "f5c" / "01_facts_sources_F5_e7b661c.json")}


def topic_v2() -> dict:
    db = _load(ROOT / "data" / "topics_db.json")
    ts = db.get("topics", db) if isinstance(db, dict) else db
    t = dict(next(t for t in ts if (t.get("id") or t.get("topic_id")) == V1))
    t["id"] = V2
    f = STEPS / V2 / "01_facts_sources.json"
    if f.exists():
        t["evidence_pool"] = _load(f).get("evidence_pool")
    return t


# ═══════════════════════════════════════════════════════════════
def respaldo_f5c(log: list[str]) -> None:
    """F5d: una sola vez, la corrida F5c a un costado (lab/…/v2_f5c, output/<V2>/_bak_f5d_pre, …_bak_f5d de v1)."""
    dst = LAB / "v2_f5c"
    if not dst.exists() and (LAB / "v2").exists():
        shutil.copytree(LAB / "v2", dst)
        log.append(f"respaldo: {LAB / 'v2'} → {dst}")
    for work, bak in ((SIM_V2, OUT / V2 / "_bak_f5d_pre" / "_fase2b_work"),
                      (SIM_V1, OUT / V1 / "_fase2b_work_f5sim_v1_bak_f5d")):
        if work.exists() and not bak.exists():
            bak.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(work), str(bak))
            log.append(f"respaldo: {work} → {bak}")


def respaldo_f5b(log: list[str]) -> None:
    """F5c: una sola vez, la corrida F5b a un costado (lab/…/v2_f5b, output/<V2>/_bak_f5c_pre, …_bak_f5c de v1)."""
    dst = LAB / "v2_f5b"
    if not dst.exists() and (LAB / "v2").exists():
        shutil.copytree(LAB / "v2", dst)
        log.append(f"respaldo: {LAB / 'v2'} → {dst}")
    for work, bak in ((SIM_V2, OUT / V2 / "_bak_f5c_pre" / "_fase2b_work"),
                      (SIM_V1, OUT / V1 / "_fase2b_work_f5sim_v1_bak_f5c")):
        if work.exists() and not bak.exists():
            bak.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(work), str(bak))
            log.append(f"respaldo: {work} → {bak}")


def respaldo_f5(log: list[str]) -> None:
    """F5b: una sola vez, la corrida F5 a un costado (lab/…/v2_f5 y output/<V2>/_bak_f5b_pre, output/<V1>/…_bak_f5b)."""
    dst = LAB / "v2_f5"
    if not dst.exists() and (LAB / "v2").exists():
        shutil.copytree(LAB / "v2", dst)
        log.append(f"respaldo: {LAB / 'v2'} → {dst}")
    for work, bak in ((SIM_V2, OUT / V2 / "_bak_f5b_pre" / "_fase2b_work"),
                      (SIM_V1, OUT / V1 / "_fase2b_work_f5sim_v1_bak_f5b")):
        if work.exists() and not bak.exists():
            bak.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(work), str(bak))
            log.append(f"respaldo: {work} → {bak}")


def etapa_guion(log: list[str]) -> None:
    from researcher_steps.evidence_pool import extract_evidence_pool
    from script_engine.m01a_skeleton import generate_skeleton
    from script_engine.m01b_narrator import generate_narration
    from script_engine import m02_5_normalizer_gate as gate
    from script_engine.m05_narrative import judge_narration
    d2 = STEPS / V2
    d2.mkdir(parents=True, exist_ok=True)
    shutil.copy2(STEPS / V1 / "00_pool_etiquetado.json", d2 / "00_pool_etiquetado.json")
    raw_cache = d2 / "00b_pool_raw.json"
    if not raw_cache.exists() and (LAB / "pruebas" / "pool_raw.json").exists():
        shutil.copy2(LAB / "pruebas" / "pool_raw.json", raw_cache)        # misma respuesta de Flash (mismo prompt)
    t0 = time.time()
    plog: list[str] = []
    pool = extract_evidence_pool(_load(d2 / "00_pool_etiquetado.json")["angle_blocks"], log=plog, raw_cache=raw_cache)
    v1_facts = _load(STEPS / V1 / "01_facts_sources.json")
    _dump(d2 / "01_facts_sources.json", {**v1_facts, "evidence_pool": pool})   # verified_facts de v1 intactos
    log += plog + [f"guion: pool {time.time() - t0:.0f}s"]
    t = topic_v2()
    t["skeleton_frozen"] = FROZEN                   # F5c: el skeleton de F5, con los ids traducidos al pool actual
    t0 = time.time()
    sk = generate_skeleton(t)
    log.append(f"guion: skeleton {time.time() - t0:.0f}s · reparaciones {_load(d2 / '01a_skeleton.json').get('_evidence_repairs')}")
    from cost_tracker import cost_tracker
    n0 = len(cost_tracker.session_overhead)
    t0 = time.time()
    nar = generate_narration(t, sk)
    cost: dict[str, float] = {}
    for e in cost_tracker.session_overhead[n0:]:
        cost[e.service] = cost.get(e.service, 0.0) + e.total_cost
    _dump(STEPS / V2 / "01b_costo.json", {"por_servicio": {k: round(v, 4) for k, v in cost.items()},
                                          "total": round(sum(cost.values()), 4),
                                          "llamadas": len(cost_tracker.session_overhead) - n0})
    log.append(f"guion: narración {time.time() - t0:.0f}s · costo {cost} · violaciones {nar.get('_f5_violations')}")
    g = gate.gate_normalizer_for_topic(V2, nar, interactive=False, persist_dict=False)
    log.append(f"guion: normalizer {len(g['spans_detected'])} spans (aplicados en 01b_narration_normalized.json)")
    rep2 = judge_narration(V2, pool=pool, narration=nar, skeleton=_load(d2 / "01a_skeleton.json"))
    rep1 = judge_narration(V2, pool=pool, narration=_load(STEPS / V1 / "01b_narration.json"),
                           skeleton=_load(STEPS / V1 / "01a_skeleton.json"), out_name="06_judge_narrative_v1.json")
    # F5b: la v2 de F5 medida con el pool nuevo (por regex: no declaraba ids) para comparar F5 → F5b
    f5n, f5s = LAB / "v2_f5" / "01b_narration.json", LAB / "v2_f5" / "01a_skeleton.json"
    if f5n.exists():
        judge_narration(V2, pool=pool, narration=_load(f5n), skeleton=_load(f5s), out_name="06_judge_narrative_v2f5.json")
    # F5c: la v2 de F5b, con sus ids declarados (mismo pool que F5c)
    fbn, fbs = LAB / "v2_f5b" / "01b_narration.json", LAB / "v2_f5b" / "01a_skeleton.json"
    if fbn.exists():
        judge_narration(V2, pool=pool, narration=_load(fbn), skeleton=_load(fbs), out_name="06_judge_narrative_v2f5b.json")
    # F5d: la v2 de F5c medida contra el skeleton de F5d (mismas cifras canónicas y reservados)
    fcn = LAB / "v2_f5c" / "01b_narration.json"
    if fcn.exists():
        judge_narration(V2, pool=pool, narration=_load(fcn), skeleton=_load(d2 / "01a_skeleton.json"),
                        out_name="06_judge_narrative_v2f5c.json")
    log.append(f"guion: juez v1 {rep1['video']['umbral']} · v2 {rep2['video']['umbral']}")


def etapa_script(log: list[str]) -> None:
    s1 = _load(ROOT / "data" / "scripts" / f"{V1}.json")
    nar = {c["chapter_number"]: c["narration"] for c in _load(STEPS / V2 / "01b_narration.json")["chapters"]}
    s2 = json.loads(json.dumps(s1))
    s2["topic_id"] = V2
    for c in s2["chapters"]:
        c["narration"] = nar[int(c["chapter_number"])]
    s2["evidence_pool"] = _load(STEPS / V2 / "01_facts_sources.json")["evidence_pool"]
    s2["f5_nota"] = "guion v2 de simulación: imágenes/prompts de v1, narración v2 (F5 §3)"
    _dump(ROOT / "data" / "scripts" / f"{V2}.json", s2)
    # el director lee skeleton/canonical de _steps/<topic_id>: copiar canonical de v1 (no cambia)
    shutil.copy2(STEPS / V1 / "02_canonical.json", STEPS / V2 / "02_canonical.json")
    log.append(f"script: data/scripts/{V2}.json ({len(s2['chapters'])} caps)")


# ═══════════════════════════════════════════════════════════════
def _v1_plans():
    import fase2b
    audio_dir = OUT / "audio" / V1
    sm = _load(audio_dir / "sync_map.json")
    mf = _load(OUT / V1 / "assets" / "assets_manifest.json")
    return fase2b._build_plans(sm, mf, V1, audio_dir, fase2b._load_script_lookup(V1))


def _base_clip(cap: str) -> Path:
    for name in (f"{cap}_hybrid_visual.mp4", f"{cap}_flux_visual.mp4"):
        if (W1 / name).exists():
            return W1 / name
    raise FileNotFoundError(cap)


def _seed_sim_dir(work: Path, copy_director: bool) -> None:
    """Assets de visión (mismas fotos → mismo caché) y, para v1, los cachés del director de v1."""
    work.mkdir(parents=True, exist_ok=True)
    (work.parent / "assets").mkdir(parents=True, exist_ok=True)
    for f in ("photo_details.json", "zoom_verify.json"):
        src = OUT / V1 / "assets" / f
        if src.exists() and work.parent != OUT / V1 and not (work.parent / "assets" / f).exists():
            shutil.copy2(src, work.parent / "assets" / f)
    pats = ["gfx_zoom_box_ch*.json", "gfx_zoomframe_ch*.jpg"]
    if copy_director:
        pats += ["gfx_plan_ch0?.json", "gfx_intensity_ch*.json", "gfx_fragments_ch*.json", "gfx_question_ch*.json",
                 "gfx_critic_ch*.json"]
    for pat in pats:
        for f in W1.glob(pat):
            if not (work / f.name).exists():
                shutil.copy2(f, work / f.name)


def _synthetic_words(text: str, dur: float) -> list[dict]:
    ws = text.split()
    step = dur / max(1, len(ws))
    return [{"word": w, "start": round(k * step, 3), "end": round(k * step + step * 0.85, 3)} for k, w in enumerate(ws)]


def _anchors_at(words: list[dict], times: list[float]) -> list[str]:
    """Anchors de 4 palabras de v2 en los instantes de los cortes de v1. Índices estrictamente crecientes y con el
    trigrama inicial único desde el anchor anterior (compute_anchor_starts busca el primero después del cursor)."""
    from anchor_timing import _norm
    toks = [_norm(w["word"]) for w in words]
    out, prev = [], -1
    for t in times:
        k = max(min(range(len(words)), key=lambda j: abs(words[j]["start"] - t)), prev + 1)
        # el needle se normaliza como el TTS (cifras → palabras): un anchor no arranca en cifras ni repite trigrama
        while k < len(words) - 3 and (any(toks[j:j + 3] == toks[k:k + 3] for j in range(prev + 1, k))
                                      or not all(re.fullmatch(r"[A-Za-zÁÉÍÓÚÑÜáéíóúñü]+[,;:!?¿¡]?", w["word"])
                                                 for w in words[k:k + 3])):
            k += 1
        k = min(k, len(words) - 1)
        out.append(" ".join(w["word"] for w in words[k:k + 4]))
        prev = k
    return out


def etapa_sim(which: str, log: list[str]) -> None:
    from dataclasses import replace
    from script_engine.gfx_layer import apply_gfx, build_scenes, remapped_words, _ffprobe_duration
    from script_engine.gfx_director import load_chapter_context
    # la copia v2 NO es un 2.º video: sin esto record_proposals promovería palabras al perfil misterio
    from script_engine import gfx_intensity
    gfx_intensity.record_proposals = lambda *a, **k: []
    plans = _v1_plans()
    work = SIM_V1 if which == "v1" else SIM_V2
    _seed_sim_dir(work, copy_director=which == "v1")
    nar2 = {f"ch{c['chapter_number']:02d}": c["narration"] for c in _load(STEPS / V2 / "01b_narration.json")["chapters"]} \
        if which == "v2" else {}
    for p in plans:
        cap = p.chapter_id
        base = _base_clip(cap)
        off = HOOK if p.is_first else 0.0
        if which == "v1":
            vid, plan = V1, p
        else:
            vid = V2
            words = _synthetic_words(nar2[cap], p.audio_duration)
            tsf = work / f"_sim_{cap}_timestamps.json"
            _dump(tsf, words)
            # escenas de v1 → anchors sintéticos en las palabras de v2 en los mismos instantes
            ctx1 = load_chapter_context(V1, p)
            _, w1 = remapped_words(p)
            sc1 = build_scenes(p, ctx1["script_chapter"], w1, _ffprobe_duration(base), off)
            starts = [s.start - (off if k else 0.0) for k, s in enumerate(sc1)]
            kw = {"narration": nar2[cap], "timestamps_path": tsf}
            if p.engine == "flux" and len(sc1) > 1:
                kw["narration_anchors"] = _anchors_at(words, starts)
            elif p.engine == "veo" and p.supplemental_anchors:
                # build_scenes descarta supp[0]: va un anchor real al principio para que el cálculo resuelva
                inner = starts[2:] if p.veo_position == "start" else starts[1:-1]
                kw["supplemental_anchors"] = _anchors_at(words, [0.0] + inner)
            plan = replace(p, **kw)
        t0 = time.time()
        apply_gfx(base, plan, vid, work, width=2560, height=1440, fps=30, quality="looks", time_offset=off,
                  sparse=True, plan_only=True)
        res = work / f"gfx_plan_{cap}.resolved.json"
        log.append(f"sim_{which} {cap}: {time.time() - t0:.0f}s · resolved {'OK' if res.exists() else 'FALTA'}")
        cues = work / f"gfx_cues_{cap}.md"
        if cues.exists():
            dst = LAB / "cues" / f"gfx_cues_{which}_{cap}.md"
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(cues, dst)


def etapa_visual(log: list[str]) -> None:
    """F5b S6: SOLO los prompts de imagen de v2 (texto). m03 tal cual (FRENOS de §1.6): el único cambio es el bloque
    de UBICACIONES en el canon. sync_map de v1 (mismas duraciones → mismo número de imágenes) con video_id = v2: no hay
    timestamps de v2, así que la reconciliación temporal no corre (no hay audio de v2)."""
    from script_engine.m03_visual import assign_visual_prompts
    sm = _load(OUT / "audio" / V1 / "sync_map.json")
    sm = {**sm, "video_id": V2}
    t0 = time.time()
    out = assign_visual_prompts(topic_v2(), _load(STEPS / V2 / "01a_skeleton.json"),
                                _load(STEPS / V2 / "01b_narration.json"), sync_map=sm)
    n = sum(len(c.get("image_prompts") or []) + len(c.get("supplemental_image_prompts") or []) + (1 if c.get("image_prompt") else 0)
            for c in out["chapters"])
    log.append(f"visual: {n} prompts de imagen de v2 en {time.time() - t0:.0f}s → {STEPS / V2 / '03_visual.json'}")


def etapa_versionar(log: list[str]) -> None:
    """Copia versionada de v2 (fuera de git en data/ y output/) a lab/hyperframes/f5/v2/."""
    dst = LAB / "v2"
    dst.mkdir(exist_ok=True)
    for f in ("01_facts_sources.json", "01a_skeleton.json", "01b_narration.json", "01b_narration_normalized.json",
              "06_judge_narrative.json", "06_judge_narrative_v1.json", "06_judge_narrative_v2f5.json",
              "06_judge_narrative_v2f5b.json", "06_judge_narrative_v2f5c.json", "01b_costo.json", "03_visual.json"):
        if (STEPS / V2 / f).exists():
            shutil.copy2(STEPS / V2 / f, dst / f)
    for which, work in (("v1", SIM_V1), ("v2", SIM_V2)):
        for f in work.glob("gfx_plan_ch0?.resolved.json"):
            shutil.copy2(f, dst / f"sim_{which}_{f.name}")
    log.append(f"versionar: {dst}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--etapa", choices=["guion", "script", "visual", "sim_v1", "sim_v2", "versionar", "todo"],
                    default="todo")
    a = ap.parse_args()
    log: list[str] = [f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] F5b etapa {a.etapa}"]
    try:
        if a.etapa in ("todo", "guion"):
            respaldo_f5(log)
            respaldo_f5b(log)
            respaldo_f5c(log)
        for et in (["guion", "script", "visual", "sim_v1", "sim_v2", "versionar"] if a.etapa == "todo" else [a.etapa]):
            if et == "guion":
                etapa_guion(log)
            elif et == "script":
                etapa_script(log)
            elif et == "visual":
                etapa_visual(log)
            elif et == "versionar":
                etapa_versionar(log)
            else:
                etapa_sim(et.split("_")[1], log)
    finally:
        (LAB / "corrida").mkdir(exist_ok=True)
        with (LAB / "corrida" / "correr_f5_orleans.log").open("a", encoding="utf-8") as fh:
            fh.write("\n".join(log) + "\n")
        print("\n".join(log))


if __name__ == "__main__":
    main()
