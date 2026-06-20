"""
test_module_03_prompt_por_anchor.py — BLOQUE 3 del handoff m03 two-step: PASO 2 (prompt por anchor).

Cubre los 4 candados de Omar:
  #1 el prompt de imagen NO se reescribe: _build_veo_prompt sigue byte-idéntico (hash) tras extraer
     los bloques visuales a constantes; el Paso 2 reusa esas MISMAS constantes + _build_rules_block.
  #2 el narration_anchor del output se copia VERBATIM del Paso 1, NUNCA del eco del LLM (aunque el
     LLM devuelva un anchor distinto, se ignora).
  #3 alineación a prueba de balas: count==n enforced; nada de pairing desalineado.
  #4 campos creativos (subject_ref, emotional_rank, prompt) presentes; validados con los validadores
     EXISTENTES (_validate_veo_cap/_validate_flux_cap) + _validate_no_text_leakage (regla 9).

Determinista, SIN red (mockea m03_visual.call_flash_json). Correr:
  python -X utf8 test_module_03_prompt_por_anchor.py
"""
from __future__ import annotations

import hashlib
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import script_engine.m03_visual as m

# Este test valida los candados ENGINE-AGNÓSTICOS del two-step (no-rewrite, anchors
# verbatim, count==n, text-leakage). shot_scale/light_mode son payload kling ortogonal,
# cubierto por los tests kling dedicados. Se pinea el engine a "flux" para ejercer los
# validadores originales (_validate_veo_cap/_validate_flux_cap) bajo los que se escribieron
# los fixtures; sin esto, el default kling exige shot_scale en los fakes y el test rompe.
# (El bake de producción está OK — la corrida real emite esos campos vía Gemini.)
m.api.image_engine = "flux"

_fails: list[str] = []


def check(cond, msg):
    print(("  ✓ " if cond else "  ✗ ") + msg)
    if not cond:
        _fails.append(msg)


NARR = (
    "Primera oración del capítulo sobre el evento. "
    "Segunda oración con más detalle del contexto histórico. "
    "Tercera oración que describe a las personas afectadas. "
    "Cuarta oración sobre las consecuencias más graves. "
    "Quinta oración que cierra el desarrollo del tema. "
    "Sexta y última oración que revela el misterio final."
)
S = [
    "Primera oración del capítulo sobre el evento.",
    "Segunda oración con más detalle del contexto histórico.",
    "Tercera oración que describe a las personas afectadas.",
    "Cuarta oración sobre las consecuencias más graves.",
    "Quinta oración que cierra el desarrollo del tema.",
]
VEO_ANCHOR = "revela el misterio final."
CAP = {"chapter_number": 7, "role": "reveal_outro", "title": "Revelación", "bullets": ["b1", "b2"]}
TOPIC = {"id": "t", "video_title": "T", "verified_facts": [], "research_summary": "ctx"}

IMG = ("An elderly figure in period-correct 1960s clothing stands alone inside a dim stone jail "
       "corridor, weathered walls around, soft natural light from a high window, documentary "
       "photography, slightly desaturated palette throughout the quiet scene.")
VID = ("Slow push in toward the figure, fine dust drifting through the cold air, faint light "
       "flickering along the stone corridor while the silhouette breathes slowly and stays still.")
def P(k):
    return (f"A period-correct 1960s documentary scene number {k}, weathered stone interior, plain "
            f"era clothing, soft natural overcast light, slightly desaturated palette, quiet still air.")
LEAK = ("A weathered prison wall with a sign where the name was once, period-correct 1960s stone "
        "corridor, dim natural light, documentary photography, slightly desaturated palette here.")


def mk(anchor):
    p = NARR.find(anchor)
    return {"anchor": anchor, "pos": p, "end": p + len(anchor)}


PLAN_VEO = {"veo_anchor": mk(VEO_ANCHOR), "supplementals": [mk(S[i]) for i in range(4)]}
PLAN_FLUX = {"anchors": [mk(S[i]) for i in range(5)]}


def _patch(ret):
    calls = {"n": 0}

    def fake(prompt, system_instruction=None, response_schema=None):
        calls["n"] += 1
        return ret
    orig = m.call_flash_json
    m.call_flash_json = fake
    return orig, calls


def test_candado1_hash_y_reuso():
    print("\n[B3] candado #1: _build_veo_prompt byte-idéntico + Paso 2 reusa reglas (no reescribe)")
    snap = Path("_lab_out/_snap_veo_before.txt")
    if snap.exists():
        # reconstruye el prompt veo original y compara hash con el snapshot pre-refactor
        import json
        from config import DATA_DIR, OUTPUT_DIR
        TID = "91bea3b0-eb43-4797-a32d-90a45fccf1c8"
        db = json.loads((DATA_DIR / "topics_db.json").read_text(encoding="utf-8"))
        topics = db.get("topics", db) if isinstance(db, dict) else db
        topic = next(t for t in topics if t.get("id") == TID or t.get("topic_id") == TID)
        steps = DATA_DIR / "scripts" / "_steps" / TID
        skel = json.loads((steps / "01a_skeleton.json").read_text(encoding="utf-8"))
        narr = json.loads((steps / "01b_narration.json").read_text(encoding="utf-8"))
        sm = json.loads((OUTPUT_DIR / "audio" / TID / "sync_map.json").read_text(encoding="utf-8"))
        sch = next(c for c in skel["chapters"] if c["chapter_number"] == 7)
        n7 = next(c for c in narr["chapters"] if c["chapter_number"] == 7)["narration"].strip()
        dur = float(next(c for c in sm["chapters"] if c["id"] == "ch07")["duration_sec"])
        nfx = m._calculate_flux_extras_count(dur)
        cps = len(n7) / dur
        vzc = max(1, min(int(m.VEO_CLIP_DURATION_SEC * cps), len(n7) - 1))
        veo = m._build_veo_prompt(topic, sch, n7, dur, nfx, "end", vzc)
        same = hashlib.sha256(veo.encode()).hexdigest() == hashlib.sha256(snap.read_text(encoding="utf-8").encode()).hexdigest()
        check(same, "_build_veo_prompt sigue byte-idéntico al snapshot pre-refactor")
    else:
        print("  (snapshot ausente — corré el lab GATE 0 primero; salteo el hash)")

    p2 = m._build_veo_prompt_step2(TOPIC, CAP, NARR, VEO_ANCHOR, S[:4], "end")
    check(m._build_rules_block()[:80] in p2, "el Paso 2 veo reusa _build_rules_block (reglas intactas)")
    check(VEO_ANCHOR in p2 and all(s in p2 for s in S[:4]), "el Paso 2 veo inyecta los anchors dados")
    check("NO los elijas" in p2 and "NO devuelvas el fragmento" in p2,
          "el Paso 2 NO pide elegir el anchor (entra como dato)")


def test_veo_ok_y_verbatim():
    print("\n[B3] veo Paso 2 ok → n prompts; anchors VERBATIM del Paso 1 (candado #2)")
    resp = {
        "image_prompt": IMG, "video_prompt": VID, "subject_ref": "main_subject",
        "supplemental_image_prompts": [
            {"prompt": P(i), "narration_anchor": "ECO BOGUS QUE DEBE IGNORARSE"} for i in range(4)
        ],
    }
    orig, calls = _patch(resp)
    try:
        out = m._render_prompts_veo(TOPIC, CAP, NARR, PLAN_VEO, "end", 7)
    finally:
        m.call_flash_json = orig
    check(calls["n"] == 1, "1 llamada (ok al primer intento)")
    check(len(out["supplemental_image_prompts"]) == 4, "4 supplementals (count==n)")
    got = [s["narration_anchor"] for s in out["supplemental_image_prompts"]]
    check(got == S[:4], "anchors del output = los del Paso 1 VERBATIM (ignora el eco del LLM)")
    check(out["narration_anchor"] == VEO_ANCHOR, "veo_anchor del output = el del Paso 1")
    check(out["image_prompt"] == IMG and out["subject_ref"] == "main_subject",
          "campos creativos del LLM presentes (image_prompt/subject_ref)")
    check(out.get("veo_position") == "end", "veo_position propagado")


def test_veo_count_mismatch():
    print("\n[B3] veo Paso 2: LLM devuelve n-1 prompts SIEMPRE → count enforced → falla (candado #3)")
    bad = {"image_prompt": IMG, "video_prompt": VID, "subject_ref": "main_subject",
           "supplemental_image_prompts": [{"prompt": P(i)} for i in range(3)]}  # 3 != 4
    orig, calls = _patch(bad)
    try:
        try:
            m._render_prompts_veo(TOPIC, CAP, NARR, PLAN_VEO, "end", 7)
            raised = False
        except m.VisualValidationError as e:
            raised = "EXACTAMENTE 4" in str(e)
    finally:
        m.call_flash_json = orig
    check(raised, "count!=n levanta VisualValidationError (no pairing desalineado)")
    check(calls["n"] == m.MAX_RETRY_ATTEMPTS, f"reintentó {m.MAX_RETRY_ATTEMPTS}× antes de fallar")


def test_veo_leakage():
    print("\n[B3] veo Paso 2: prompt con text-leakage → regla 9 lo rechaza (candado #4, validador existente)")
    resp = {"image_prompt": IMG, "video_prompt": VID, "subject_ref": "main_subject",
            "supplemental_image_prompts": [{"prompt": (LEAK if i == 1 else P(i))} for i in range(4)]}
    orig, _ = _patch(resp)
    try:
        try:
            m._render_prompts_veo(TOPIC, CAP, NARR, PLAN_VEO, "end", 7)
            raised = False
        except m.VisualValidationError as e:
            raised = "text-leakage" in str(e) or "regla 3" in str(e).lower()
    finally:
        m.call_flash_json = orig
    check(raised, "_validate_no_text_leakage activado en el Paso 2 (regla 9)")


def test_flux_ok_y_verbatim():
    print("\n[B3] flux Paso 2 ok → n prompts; anchors verbatim + campos creativos (candado #2/#4)")
    items = [{"prompt": P(i), "subject_ref": "main_subject",
              "emotional_rank": ["R1", "R2", "R3", "R2", "R3"][i],
              "narration_anchor": "ECO BOGUS"} for i in range(5)]
    resp = {"image_prompts": items}   # _safe_json_parse envolvería un array así
    orig, _ = _patch(resp)
    try:
        out = m._render_prompts_flux(TOPIC, {"chapter_number": 2, "role": "development", "title": "Dev"},
                                     NARR, PLAN_FLUX, 2)
    finally:
        m.call_flash_json = orig
    check(len(out["image_prompts"]) == 5, "5 prompts (count==n)")
    got = [it["narration_anchor"] for it in out["image_prompts"]]
    check(got == S[:5], "flux: anchors del output = Paso 1 VERBATIM")
    check(all(it["emotional_rank"] in ("R1", "R2", "R3") for it in out["image_prompts"]),
          "emotional_rank presente y válido (campo creativo conservado)")
    check(all(it["subject_ref"] for it in out["image_prompts"]), "subject_ref presente")


def test_flux_count_mismatch():
    print("\n[B3] flux Paso 2: count!=n → falla (candado #3)")
    bad = {"image_prompts": [{"prompt": P(i), "subject_ref": "main_subject", "emotional_rank": "R3"}
                             for i in range(4)]}  # 4 != 5
    orig, _ = _patch(bad)
    try:
        try:
            m._render_prompts_flux(TOPIC, {"chapter_number": 2, "role": "development", "title": "Dev"},
                                   NARR, PLAN_FLUX, 2)
            raised = False
        except m.VisualValidationError as e:
            raised = "EXACTAMENTE 5" in str(e)
    finally:
        m.call_flash_json = orig
    check(raised, "flux count!=n levanta VisualValidationError")


if __name__ == "__main__":
    test_candado1_hash_y_reuso()
    test_veo_ok_y_verbatim()
    test_veo_count_mismatch()
    test_veo_leakage()
    test_flux_ok_y_verbatim()
    test_flux_count_mismatch()

    print("\n" + ("=" * 60))
    if _fails:
        print(f"FALLOS: {len(_fails)}")
        for f in _fails:
            print(f"  - {f}")
        sys.exit(1)
    print("TODO OK")
