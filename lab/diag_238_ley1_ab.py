# lab/diag_238_ley1_ab.py — LAB (HANDOFF_137a §4). A/B de la LEY 1 "pintor-no-actor".
#
# Corre el path seedream de m03 SOLO para el CAP 3 de Orleans (ba6c3cac) con el prompt
# NUEVO (SYSTEM_INSTRUCTION_VISUAL_SEEDREAM ya trae PHYSICAL TRANSLATION R6 + BODY CARRIES
# THE SITUATION; slot mood física-solamente). Replica la rama flux de assign_visual_prompts
# ._process_one_cap para el cap 3 (mismos inputs, mismas helpers) SIN correr los otros 6 caps
# ni tocar producción. Dumpea los prompts nuevos, renderiza 4 beats con personas en el agua
# vía asset_manager t2i (seedream), y arma el result.txt A/B (viejo vs nuevo). El veredicto
# es del ojo de Omar — el lab NO concluye.
#
# ⚠ READ-ONLY sobre producción: lee topics_db + step files + sync_map + 03_visual.json vigente;
#   escribe SOLO en lab/. No toca data/scripts/<id>.json ni 03_visual.json ni los PNGs del topic.
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

import script_engine.m03_visual as m03
import asset_manager as am
from cost_tracker import cost_tracker

TOPIC = "ba6c3cac-a091-41c0-8dad-afd2f4364747"
CAP = 3
N_RENDERS = 4

OUT = Path(__file__).resolve().parent
RENDERS = OUT / "diag_238_renders"
PROMPTS_JSON = OUT / "diag_238_cap3_prompts_new.json"
RESULT_TXT = OUT / "diag_238_result.txt"

STEPS = ROOT / "data" / "scripts" / "_steps" / TOPIC
OLD_VISUAL = STEPS / "03_visual.json"
SYNC_MAP = ROOT / "output" / "audio" / TOPIC / "sync_map.json"
TOPICS_DB = ROOT / "data" / "topics_db.json"

# Tokens de "personas en el agua" para elegir los 4 beats (prompts en inglés).
WATER_TOKENS = ("floodwater", "flood water", "flood", "water", "submerged", "chest-deep",
                "chest deep", "waist-deep", "waist deep", "wading", "wade", "drown",
                "soaked", "wet ", "rising water", "inund")


def _load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8", errors="replace"))


def _load_topic() -> dict:
    db = _load(TOPICS_DB)
    topics = db.get("topics", []) if isinstance(db, dict) else db
    for t in topics:
        if t.get("id") == TOPIC or t.get("topic_id") == TOPIC:
            return t
    raise KeyError(f"{TOPIC} no está en topics_db.json")


def _norm(s: str) -> str:
    return " ".join((s or "").split()).strip().lower()


def _run_cap3_new(topic: dict, skeleton: dict, narration: dict, sync_map: dict) -> dict:
    """Replica la rama flux de m03.assign_visual_prompts._process_one_cap para el cap 3."""
    sch = next(c for c in skeleton["chapters"] if c.get("chapter_number") == CAP)
    nch = next(c for c in narration["chapters"] if c.get("chapter_number") == CAP)
    narration_text = (nch.get("narration") or "").strip()
    cap_id = f"ch{CAP:02d}"
    video_id = sync_map.get("video_id") or TOPIC

    entry = next((c for c in sync_map.get("chapters", []) if c.get("id") == cap_id), None)
    if entry is None:
        raise RuntimeError(f"sync_map sin entry para {cap_id}")
    cap_duration_sec = float(entry["duration_sec"])

    n_images = m03._calculate_image_count(
        cap_duration_sec=cap_duration_sec, chapter_number=CAP,
        total_chapters=m03.EXPECTED_CHAPTER_COUNT,
    )
    print(f"  [238] cap {CAP} flux → {n_images} imgs (audio {cap_duration_sec:.1f}s)")

    plan = m03._plan_anchors(narration_text, n_images, "flux", cap_number=CAP)
    words_ts = m03._load_cap_word_timestamps(video_id, cap_id)
    if words_ts:
        plan, _ = m03._reconcile_anchor_timing(plan, "flux", words_ts, m03.MIN_IMAGES_FLUX, CAP)

    cap_out = m03._render_prompts_seedream(topic, sch, narration_text, plan, CAP)
    cap_out = m03._stitch_zone2_into_cap_flux(cap_out)
    return cap_out


def _pick_water_beats(new_ips: list[dict]) -> list[int]:
    """Índices (0-based) de los 4 beats con PERSONAS en el agua (donde la LEY 1 se ve).
    Exige sujeto-persona (no arquitectura/objeto) + contexto de agua; prioriza los de mayor
    carga visible (cara/sumergido/apiñados/varios). Si hay <4 personas-en-agua, completa con
    personas sin agua y luego cualquiera. No mido 'carga emocional' con LLM → proxy por tokens
    de subject (honesto, anotado en result.txt)."""
    PERSON = ("inmate", "prisoner", "people", "man ", "woman", "teenager", "teenage", "child", "guard")
    STRONG = ("face", "submerged", "huddled", "three", "two ", "neck")   # más cara/cuerpo visible

    def _subj(ip): return _norm(ip.get("subject", ""))
    def _blob(ip): return _norm(" ".join(str(ip.get(k, "")) for k in
                               ("subject", "action", "setting", "props_detail", "prompt")))
    def _is_person(ip): return any(t in _subj(ip) for t in PERSON)
    def _has_water(ip): return any(t in _blob(ip) for t in WATER_TOKENS)

    scored = []
    for i, ip in enumerate(new_ips):
        if not _is_person(ip):
            continue
        s = (2 if _has_water(ip) else 0) + sum(1 for t in STRONG if t in _subj(ip))
        scored.append((s, i))
    scored.sort(key=lambda x: (-x[0], x[1]))          # score desc, luego orden narrativo
    picked = [i for _, i in scored[:N_RENDERS]]
    if len(picked) < N_RENDERS:                        # relleno: cualquier beat restante
        for i in range(len(new_ips)):
            if i not in picked:
                picked.append(i)
            if len(picked) == N_RENDERS:
                break
    return picked[:N_RENDERS]


def main() -> None:
    RENDERS.mkdir(parents=True, exist_ok=True)
    topic = _load_topic()
    skeleton = _load(STEPS / "01a_skeleton.json")
    narration = _load(STEPS / "01b_narration.json")
    sync_map = _load(SYNC_MAP)
    old_visual = _load(OLD_VISUAL)
    old_cap3 = next(c for c in old_visual["chapters"] if c.get("chapter_number") == CAP)
    old_by_anchor = {_norm(ip.get("narration_anchor", "")): ip for ip in old_cap3.get("image_prompts", [])}
    old_by_idx = old_cap3.get("image_prompts", [])

    print("=" * 100)
    print(f"DIAG #238 — LEY 1 pintor-no-actor — A/B cap {CAP} de {TOPIC[:8]} (Orleans)")
    print(f"  motor {am.api.image_engine} · prompt NUEVO (R6 físico + cuerpo-por-situación)")
    print("=" * 100)

    cost_tracker.start_video(f"diag238_{TOPIC[:8]}")
    try:
        # Reusar los prompts ya generados si existen (idempotente: no re-gasta Gemini en
        # re-corridas donde solo cambia el picker/render). Borrar el JSON para forzar regen.
        if PROMPTS_JSON.exists():
            cap_out = _load(PROMPTS_JSON)
            print(f"  [238] ♻ reusando prompts de {PROMPTS_JSON.name} (borralo para regenerar)")
        else:
            cap_out = _run_cap3_new(topic, skeleton, narration, sync_map)
            PROMPTS_JSON.write_text(json.dumps(cap_out, indent=2, ensure_ascii=False), encoding="utf-8")
        new_ips = cap_out.get("image_prompts", [])
        print(f"  [238] {len(new_ips)} prompts nuevos → {PROMPTS_JSON.name}")
        # renders frescos: limpiar PNGs viejos para no mezclar picks previos
        for old_png in RENDERS.glob("*.png"):
            old_png.unlink()

        picked = _pick_water_beats(new_ips)
        print(f"  [238] beats elegidos (0-based): {picked}  → renderizando {len(picked)} imgs…")

        renders: list[dict] = []
        for rank, idx in enumerate(picked, start=1):
            ip = new_ips[idx]
            anchor = ip.get("narration_anchor", "")
            new_prompt = ip.get("prompt", "")
            out_png = RENDERS / f"cap{CAP}_img{idx+1:02d}.png"
            print(f"    [{rank}/{len(picked)}] img #{idx+1} → {out_png.name}")
            try:
                am._generate_image_raw(new_prompt, out_png, use_ultra=False)
                render_path = str(out_png.relative_to(ROOT))
            except Exception as e:  # noqa: BLE001 — un render caído NO tumba el A/B
                render_path = f"ERROR: {type(e).__name__}: {e}"
                print(f"        ⚠ {render_path}")
            # old prompt: por anchor exacto, si no por índice
            om = old_by_anchor.get(_norm(anchor))
            match_by = "anchor"
            if om is None:
                om = old_by_idx[idx] if idx < len(old_by_idx) else None
                match_by = "índice (anchor nuevo no matchea)" if om else "sin viejo"
            renders.append({
                "img_idx": idx + 1, "anchor": anchor,
                "old_prompt": (om or {}).get("prompt", ""), "old_match_by": match_by,
                "new_prompt": new_prompt, "render_path": render_path,
            })
    finally:
        report = cost_tracker.end_video()

    # ── result.txt (sin conclusión — el ojo de Omar decide) ──
    lines: list[str] = []
    lines.append(f"DIAG #238 — LEY 1 pintor-no-actor — A/B cap {CAP} · topic {TOPIC}")
    lines.append(f"prompt NUEVO: R6 PHYSICAL TRANSLATION + BODY CARRIES THE SITUATION + slot mood física-solamente")
    lines.append(f"beats renderizados: {len(renders)} (elegidos por tokens de agua; relleno por orden si faltan)")
    lines.append("")
    for r in renders:
        lines.append("─" * 92)
        lines.append(f"IMG #{r['img_idx']}  ·  render: {r['render_path']}")
        lines.append(f"ANCHOR: {r['anchor']}")
        lines.append(f"OLD (match por {r['old_match_by']}):")
        lines.append(f"  {r['old_prompt']}")
        lines.append(f"NEW:")
        lines.append(f"  {r['new_prompt']}")
        lines.append("")
    RESULT_TXT.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"\n{'='*100}")
    print(f"  prompts nuevos: {PROMPTS_JSON}")
    print(f"  renders:        {RENDERS}  ({sum(1 for r in renders if not r['render_path'].startswith('ERROR'))}/{len(renders)} ok)")
    print(f"  result A/B:     {RESULT_TXT}")
    if report is not None and hasattr(report, "total_cost"):
        print(f"  costo del lab:  ${report.total_cost:.4f}")


if __name__ == "__main__":
    main()
