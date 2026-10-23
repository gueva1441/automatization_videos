"""F10 §4.1: corrida en seco de `fase1_5 --v3` con Orleans f7r3, de punta a punta hasta `assemble`.

Topic de copia `ba6c3cac-f10seco` (pasos copiados de `ba6c3cac-f7r3`; el topic se arma en memoria: no toca topics_db).
De verdad: fase1_5.process_topic (v3), m01d_particion (títulos con Flash; acortado con el editor si hace falta),
juez m05, m02_5 normalizer_gate en batch, m03_visual (todo lo determinista: plan de anclas por respaldo, beats, reglas
F8/F8b, pasada de video) y assemble_final_script. Simulado (cuesta plata o escribe fuera): la escaleta, el guionista y
el editor (sus salidas guardadas de F7c-3), el TTS (sync_map sintético a 2.25 palabras/s), m07, las llamadas LLM de m03
y la foto madre. Valida el contrato y escribe lab/hyperframes/f10/seco/ (SECO.md + copias de los archivos).
Uso: python -I lab/hyperframes/f10/f10_seco_orleans.py
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
SRC, TOPIC = "ba6c3cac-f7r3", "ba6c3cac-f10seco"
OUT = Path(__file__).resolve().parent / "seco"
SK_KEYS = ("chapter_number", "title", "role", "render_engine", "duration_seconds", "narrative_intent", "bullets",
           "evidence_ids", "cliffhanger", "pantalla_ids")
NA_KEYS = ("chapter_number", "narration", "datos_usados", "ids_usados", "narration_tts")


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")                # -I ignora PYTHONIOENCODING
    import fase1_5 as f15
    from config import DATA_DIR, OUTPUT_DIR
    from script_engine import m01a_escaleta as me
    from script_engine import m01b_guionista as mg
    from script_engine import m01c_editor as mc
    from script_engine import m03_visual as m3
    from script_engine import m06_assembler as m6
    from script_engine.tts_tags import strip_tags
    steps = DATA_DIR / "scripts" / "_steps"
    dst = steps / TOPIC
    if dst.exists():
        shutil.rmtree(dst)
    dst.mkdir(parents=True)
    for f in ("00_pool_v3.json", "01_facts_sources.json", "01a_escaleta.json", "01b_guionista_v3.json",
              "01b_editor_v3.json"):
        shutil.copy2(steps / SRC / f, dst / f)
    shutil.rmtree(OUTPUT_DIR / "audio" / TOPIC, ignore_errors=True)
    db = json.loads((DATA_DIR / "topics_db.json").read_text(encoding="utf-8"))
    topic = json.loads(json.dumps(next(t for t in db["topics"] if t["id"] == SRC)))
    topic.update({"id": TOPIC, "video_id": TOPIC,
                  "evidence_pool": json.loads((dst / "01_facts_sources.json").read_text(encoding="utf-8"))["evidence_pool"]})
    f15._load_topic_by_id = lambda tid: topic
    m6._load_topic = lambda tid: topic

    # ── simulados ──
    esc0 = json.loads((dst / "01a_escaleta.json").read_text(encoding="utf-8"))
    g0 = json.loads((dst / "01b_guionista_v3.json").read_text(encoding="utf-8"))
    e0 = json.loads((dst / "01b_editor_v3.json").read_text(encoding="utf-8"))
    calls = {"escaleta": 0, "guionista": 0, "editor": 0, "audio": None}

    def fake_esc(t, **kw):
        calls["escaleta"] += 1
        assert t.get("guion_version") == 3 and t.get("evidence_pool")
        (dst / "01a_escaleta.json").write_text(json.dumps(esc0, ensure_ascii=False, indent=2), encoding="utf-8")
        return esc0

    def fake_write(t, esc, **kw):
        calls["guionista"] += 1
        return g0

    def fake_edit(t, esc, parrafos, **kw):
        calls["editor"] += 1
        return e0
    me.generate_escaleta, mg.write, mc.edit = fake_esc, fake_write, fake_edit

    def fake_audio(script, language="es", skip_if_exists=True):
        calls["audio"] = script
        d = OUTPUT_DIR / "audio" / TOPIC
        d.mkdir(parents=True, exist_ok=True)
        chs, off = [], 0.0
        for c in script["chapters"]:
            dur = round(len(re.findall(r"\w+", c["text"])) / 2.25, 2)
            chs.append({"id": c["id"], "duration_sec": dur, "narrative_intent": c.get("narrative_intent", ""),
                        "start_offset_sec": off, "end_offset_sec": off + dur})
            off += dur
        p = d / "sync_map.json"
        p.write_text(json.dumps({"video_id": TOPIC, "chapters": chs, "total_duration_sec": off}), encoding="utf-8")
        return p
    f15.audio_manager.process_script = fake_audio
    f15.m07_music_director.generate_music_map = lambda **kw: {"tracks_by_chapter": {}}
    f15.generate_foto_madre_for_topic = lambda t, vid: None
    f15.load_db = lambda: {"topics": []}
    f15.save_db = lambda db: None

    def fake_retry(prompt, validator_fn, cap_number, system_instruction=None, checklist=None, **kw):
        if checklist is not None:                       # plan de anclas → respaldo determinista
            raise m3.VisualValidationError("seco: sin LLM")
        block = prompt.split("ANCHORS YA ELEGIDOS")[1].split("Emit EXACTLY")[0]
        n = len([ln for ln in block.splitlines() if ln.strip().startswith("[")])
        slots = [{"subject": "an empty flooded cell block" if i % 3 else "the prison complex seen from the street",
                  "action": "water standing still", "gaze_interaction": "toward the window",
                  "setting": "Orleans Parish Prison, 2005", "color_palette": "grey", "props_detail": "a mattress",
                  "shot_scale": "wide" if i % 3 else "extreme_wide", "camera_angle": "eye-level",
                  "lens_technique": "deep focus", "lighting": "overcast", "mood": "cold", "style": "documentary",
                  "text_in_image": {"present": False, "text": "", "font": "", "location": ""}, "hard_fact_ids": [],
                  "subject_ref": "interior_scene" if i % 3 else "establishing_shot", "foto_madre_ref": [],
                  "emotional_rank": "R3"} for i in range(n)]
        return validator_fn({"image_prompts": slots})
    m3._call_with_validation_retry = fake_retry
    m3._fluidify_item = lambda slots, locked, profile, label, max_attempts=3, extra_feedback="": (
        f"A {slots['shot_scale']} view of {slots['subject']}, {slots['action']}, {slots['setting']}. "
        "The image has a 16:9 aspect ratio.")
    m3._seedream_video_prompt = lambda image_prompt, label, max_attempts=3: "Slow push-in; water ripples; light constant."

    res = f15.process_topic(TOPIC, from_step="m01a", gate_interactive=False, music_gate_interactive=False, v3=True)
    print(json.dumps({k: v for k, v in res.items() if k != "error"}, ensure_ascii=False), res.get("error", ""))

    # ── chequeos del contrato ──
    sk = json.loads((dst / "01a_skeleton.json").read_text(encoding="utf-8"))
    na = json.loads((dst / "01b_narration.json").read_text(encoding="utf-8"))
    vi = json.loads((dst / "03_visual.json").read_text(encoding="utf-8"))
    final = json.loads((DATA_DIR / "scripts" / f"{TOPIC}.json").read_text(encoding="utf-8"))
    from fase2a import normalize_script
    norm = normalize_script(final)
    chk = {
        "pasos": res["steps_completed"], "status": res["status"],
        "llamadas_simuladas": {k: v for k, v in calls.items() if k != "audio"},
        "skeleton_7_caps_con_contrato": len(sk["chapters"]) == 7 and all(all(k in c for k in SK_KEYS)
                                                                         for c in sk["chapters"]),
        "titulos": [c["title"] for c in sk["chapters"]], "titulos_fuente": sk["_v3"]["particion"]["titulos"],
        "particion_notas": sk["_v3"]["particion"]["notas"],
        "narracion_7_caps_con_contrato": len(na["chapters"]) == 7 and all(all(k in c for k in NA_KEYS)
                                                                          for c in na["chapters"]),
        "narration_tts_limpia_igual_a_narration": all(strip_tags(c["narration_tts"]) == strip_tags(c["narration"])
                                                      for c in na["chapters"]),
        "audio_recibe_narration_tts": all(c.get("narration_tts") for c in calls["audio"]["chapters"]),
        "audio_text_sin_etiquetas": all("[" not in c["text"] for c in calls["audio"]["chapters"]),
        "palabras_por_cap": [len(re.findall(r"\w+", c["narration"])) for c in na["chapters"]],
        "juez": (dst / "06_judge_narrative.json").exists(),
        "normalizado": (dst / "01b_narration_normalized.json").exists(),
        "m03_v3_activo": "_f8_imagenes" in vi, "m03_auditoria": vi.get("_f8_imagenes", {}).get("despues"),
        "imagenes_por_cap": [len(c.get("image_prompts") or c.get("supplemental_image_prompts") or [])
                             for c in vi["chapters"]],
        "final_caps": len(final["chapters"]), "fase2a_normaliza": len(norm["chapters"]) == 7,
        "marca_sensible_en_final": any(isinstance(p, dict) and "sensible" in p for c in final["chapters"]
                                       for p in (c.get("image_prompts") or []) + (c.get("supplemental_image_prompts") or [])),
        "pantalla_ids": [c["pantalla_ids"] for c in sk["chapters"]],
    }
    OUT.mkdir(parents=True, exist_ok=True)
    for f in ("01a_skeleton.json", "01b_narration.json", "06_judge_narrative.json", "03_visual.json"):
        shutil.copy2(dst / f, OUT / f)
    shutil.copy2(DATA_DIR / "scripts" / f"{TOPIC}.json", OUT / f"{TOPIC}.json")
    (OUT / "seco_chequeos.json").write_text(json.dumps(chk, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(chk, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
