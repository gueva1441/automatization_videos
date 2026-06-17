"""
m06_classifier.py — Clasificador de issues post-m05.

Para cada issue con cohort >= 2 emitido por m05, llama Flash 1 vez con
contexto filtrado al cap y clasifica el issue en uno de 3 buckets:

  - minor             (deja pasar opcional, no rompe video)
  - grave             (necesita fix de código + re-run desde módulo culpable)
  - false_positive    (candidato a agregar al catálogo histórico)

Persiste un JSON por issue en data/issues_log/<topic_id>/<bucket>_NN.json
y muestra menú interactivo:

  [P] pasar todo  → ensambla data/scripts/<topic_id>.json (contrato sagrado)
                    + agrega los false_positive aprobados a known_fps.json
  [R] rerun       → imprime comando para re-correr desde el módulo más temprano
                    de los issues GRAVE; NO ejecuta
  [E] exit        → solo deja JSONs en disco; usuario decide después

m06 NUNCA modifica prompts/narración (anti-patrón #3 de ARCHITECTURE.md).
"""

import json
from pathlib import Path

from config import DATA_DIR
from gemini_helpers import call_flash_json
from script_engine.m06_assembler import assemble_final_script


STEPS_DIR: Path = DATA_DIR / "scripts" / "_steps"
ISSUES_LOG_DIR: Path = DATA_DIR / "issues_log"
KNOWN_FPS_PATH: Path = ISSUES_LOG_DIR / "known_fps.json"


# Orden topológico para resolver "módulo más temprano"
MODULE_ORDER = ["m00", "m01a", "m01b", "m02", "m03"]


# ═══════════════════════════════════════════════════════════════
#  PROMPT FLASH — clasificador por issue
# ═══════════════════════════════════════════════════════════════

CLASSIFIER_PROMPT_TEMPLATE = """\
You are an issue triage classifier for a documentary video script engine.

You receive ONE issue detected by a previous validation module (m05) and you
classify it into exactly one of three buckets:

  - "auto_fixable"    : the issue can be fully resolved by REWRITING THE
                        PROMPT TEXT in 03_visual.json without changing any
                        code. Examples:
                          - quoted nouns ('liquidator', 'Object Shelter')
                            → replace with descriptive alternative
                          - literal dates ('April 26, 1986') → remove
                          - profile mismatch (e.g. URBAN nocturne in daytime
                            scene) → swap for compatible profile from catalog
                        If you select this bucket, you MUST also provide
                        `prompt_corregido` with the EXACT text that should
                        replace the current prompt.

                        CRITICAL — what counts as "the prompt":
                        The full prompt has TWO parts. PART A (start, ~80-260
                        chars): scene description. PART B (end): palette +
                        optics + grain + style descriptor stitched from the
                        stylistic categorization (deprecated). PART B IS
                        LEGITIMATE STRUCTURE, NOT BUG. When you write
                        `prompt_corregido`, you MUST preserve PART B verbatim.
                        Only edit PART A. If the issue requires changing
                        PART B (the profile itself), the fix is to swap to
                        a different stylistic category — but DO NOT remove
                        the descriptor block entirely or write your own from
                        scratch.

                        DO NOT use auto_fixable for category 'other'. That
                        category is a catch-all and the fix is rarely
                        purely textual — escalate to grave instead.
  - "minor"           : the issue is real but cosmetic. Video would still
                        play OK if shipped. NOT auto-fixable (requires
                        narrative or code change to fully resolve).
  - "grave"           : the issue would damage the video if shipped AND
                        cannot be resolved by simply rewriting the prompt
                        text. Requires code change (e.g. m03 prompt rules,
                        new stylistic category, m01b narration logic).
  - "false_positive"  : the issue was incorrectly flagged by m05.

You ALSO receive a catalog of previously-confirmed false positives. If the
issue at hand matches a pattern there, classify it as "false_positive" and
cite the matching pattern_id.

You DO NOT propose code fixes. m05 already proposed `how_to_fix`. Your job
is bucket + justification, nothing else.

--- ISSUE ---
{issue_json}

--- VISUAL PROMPT FOR THIS IMAGE ---
{prompt_actual}

--- NARRATION OF THIS CHAPTER (where the anchor lives) ---
{narration_cap}

--- BULLETS OF THIS CHAPTER ---
{bullets_cap}

--- TOPIC FACTS RELEVANT (era, persons, location) ---
{topic_facts}

--- KNOWN FALSE POSITIVES CATALOG ---
{known_fps_block}

--- OUTPUT (return STRICT JSON, no prose, no markdown) ---
{{
  "bucket":               "auto_fixable" | "minor" | "grave" | "false_positive",
  "prompt_corregido":     "ONLY if bucket=auto_fixable. Full rewritten prompt text (NOT a diff, the complete new prompt). Same language as original prompt (English)." | null,
  "diagnostico_m06":      "1-3 sentences in Spanish, your reasoning",
  "evidencia_narracion":  "5-15 words from the narration that show the truth",
  "facts_topic_relevantes": "era, persons, location relevant to this issue (Spanish)",
  "modulo_culpable":      "m00" | "m01a" | "m01b" | "m02" | "m03",
  "fix_sugerido":         "ONLY if bucket=grave. Spanish, 1 sentence." | null,
  "archivo_linea_sugerida": "ONLY if bucket=grave. e.g. 'm03_visual.py:_build_flux_prompt'" | null,
  "razon_fp":             "ONLY if bucket=false_positive. Spanish, 1-2 sentences." | null,
  "patron_para_log":      "ONLY if bucket=false_positive. regex or fingerprint string." | null,
  "matched_known_fp_id":  "ONLY if matches an existing pattern in catalog." | null,
  "por_que_leve":         "ONLY if bucket=minor. Spanish, 1 sentence." | null
}}
"""


# ═══════════════════════════════════════════════════════════════
#  HELPERS DE CARGA Y FILTRO DE CONTEXTO
# ═══════════════════════════════════════════════════════════════

def _load_step(topic_id: str, filename: str) -> dict:
    path = STEPS_DIR / topic_id / filename
    if not path.exists():
        raise FileNotFoundError(f"m06: falta {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def _load_topic_facts(topic_id: str) -> dict:
    """Devuelve solo era + personas + lugar del topic (no facts completos)."""
    from script_engine.m06_assembler import _load_topic
    topic = _load_topic(topic_id)
    return {
        "era":            topic.get("era_visual_canon") or topic.get("era") or "?",
        "documented_people": topic.get("documented_people", []),
        "canonical_subject_description": topic.get("canonical_subject_description", ""),
    }


def _load_known_fps() -> list[dict]:
    if not KNOWN_FPS_PATH.exists():
        return []
    return json.loads(KNOWN_FPS_PATH.read_text(encoding="utf-8")).get("entries", [])


def _save_known_fps(entries: list[dict]) -> None:
    ISSUES_LOG_DIR.mkdir(parents=True, exist_ok=True)
    KNOWN_FPS_PATH.write_text(
        json.dumps({"entries": entries}, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )


def _extract_prompt_for_issue(visual: dict, issue: dict) -> str:
    """Saca el prompt de la imagen específica que disparó el issue."""
    cap_num = issue.get("chapter_id")
    img_idx = issue.get("image_index", 1) - 1  # 1-based → 0-based
    cap = next((c for c in visual.get("chapters", []) if c["chapter_number"] == cap_num), {})
    if cap.get("render_engine") == "veo" or "image_prompt" in cap:
        return cap.get("image_prompt", "")
    items = cap.get("image_prompts", [])
    if 0 <= img_idx < len(items):
        return items[img_idx].get("prompt", "")
    return ""


def _extract_narration_cap(narration: dict, cap_num: int) -> str:
    cap = next((c for c in narration.get("chapters", []) if c["chapter_number"] == cap_num), {})
    return cap.get("narration", "")


def _extract_bullets_cap(skeleton: dict, cap_num: int) -> list:
    cap = next((c for c in skeleton.get("chapters", []) if c["chapter_number"] == cap_num), {})
    return cap.get("bullets", [])


def _earliest_module(modules: list[str]) -> str:
    """Devuelve el módulo más temprano según MODULE_ORDER."""
    for m in MODULE_ORDER:
        if m in modules:
            return m
    return MODULE_ORDER[0]


# ═══════════════════════════════════════════════════════════════
#  CLASIFICACIÓN POR ISSUE
# ═══════════════════════════════════════════════════════════════

def _classification_schema() -> dict:
    """HANDOFF 66b (R4) — response_schema para call_flash_json del clasificador.

    Derivado del contrato de salida que lee classify_one_issue desde
    `classification` (ver más abajo). Solo `bucket` es hard-required: el código
    bifurca lógica defensiva sobre él y aguas abajo (persist/menú/assembler) lo
    usa como clave. El resto se lee con .get() y es null-tolerante (campos por
    bucket: prompt_corregido/fix_sugerido/razon_fp/etc), por eso van opcionales.
    """
    return {
        "type": "OBJECT",
        "properties": {
            "bucket":                  {"type": "STRING"},
            "prompt_corregido":        {"type": "STRING"},
            "diagnostico_m06":         {"type": "STRING"},
            "evidencia_narracion":     {"type": "STRING"},
            "facts_topic_relevantes":  {"type": "STRING"},
            "modulo_culpable":         {"type": "STRING"},
            "fix_sugerido":            {"type": "STRING"},
            "archivo_linea_sugerida":  {"type": "STRING"},
            "razon_fp":                {"type": "STRING"},
            "patron_para_log":         {"type": "STRING"},
            "matched_known_fp_id":     {"type": "STRING"},
            "por_que_leve":            {"type": "STRING"},
        },
        "required": ["bucket"],
    }


def classify_one_issue(
    issue: dict,
    topic_id: str,
    visual: dict,
    narration: dict,
    skeleton: dict,
    topic_facts: dict,
    known_fps: list[dict],
) -> dict:
    """Llama Flash 1 vez para clasificar 1 issue."""
    cap_num = issue.get("chapter_id")
    prompt_actual = _extract_prompt_for_issue(visual, issue)
    narration_cap = _extract_narration_cap(narration, cap_num)
    bullets_cap = _extract_bullets_cap(skeleton, cap_num)

    known_fps_block = (
        json.dumps(known_fps, ensure_ascii=False, indent=2)
        if known_fps else "(empty — no entries yet)"
    )

    prompt = CLASSIFIER_PROMPT_TEMPLATE.format(
        issue_json=json.dumps(issue, ensure_ascii=False, indent=2),
        prompt_actual=prompt_actual or "(empty)",
        narration_cap=narration_cap or "(empty)",
        bullets_cap=json.dumps(bullets_cap, ensure_ascii=False),
        topic_facts=json.dumps(topic_facts, ensure_ascii=False, indent=2),
        known_fps_block=known_fps_block,
    )

    classification = call_flash_json(prompt, response_schema=_classification_schema())  # HANDOFF 66b (R4)

    # Construir payload final (lo que se persiste)
    payload = {
        "issue_id":                  issue.get("issue_id"),
        "chapter_id":                cap_num,
        "image_index":               issue.get("image_index"),
        "cohort":                    f"{issue.get('cohort')}/{issue.get('cohort_total')}",
        "category":                  issue.get("category"),
        "severity":                  issue.get("severity"),
        "anchor":                    issue.get("anchor_excerpt"),
        "prompt_actual":             prompt_actual,
        "bucket":                    classification.get("bucket"),
        "diagnostico_m06":           classification.get("diagnostico_m06"),
        "evidencia_narracion":       classification.get("evidencia_narracion"),
        "facts_topic_relevantes":    classification.get("facts_topic_relevantes"),
        "modulo_culpable":           classification.get("modulo_culpable"),
        # Extras por bucket:
        "fix_sugerido":              classification.get("fix_sugerido"),
        "archivo_linea_sugerida":    classification.get("archivo_linea_sugerida"),
        "razon_fp":                  classification.get("razon_fp"),
        "patron_para_log":           classification.get("patron_para_log"),
        "matched_known_fp_id":       classification.get("matched_known_fp_id"),
        "por_que_leve":              classification.get("por_que_leve"),
        # Trazabilidad:
        "m05_what_happened":         issue.get("what_happened"),
        "m05_how_to_fix":            issue.get("how_to_fix"),
        # FASE m06 v2: prompt_corregido para bucket auto_fixable
        "prompt_corregido":          classification.get("prompt_corregido"),
    }

    # Defensivo 1: si el LLM marcó auto_fixable pero olvidó prompt_corregido,
    # degradar a grave para no romper el flujo de aplicación.
    if payload.get("bucket") == "auto_fixable" and not payload.get("prompt_corregido"):
        print(f"  [06] ⚠ Issue {payload.get('issue_id')} marcado auto_fixable sin "
              f"prompt_corregido. Degradando a grave.")
        payload["bucket"] = "grave"

    # Defensivo 2: categoría 'other' es catch-all — el LLM no tiene contexto
    # suficiente para reescribir el prompt sin perder estructura legítima
    # (ej: stitching del profile descriptor). Bloquear auto_fixable para 'other'
    # y degradar a grave para revisión humana.
    if payload.get("bucket") == "auto_fixable" and payload.get("category") == "other":
        print(f"  [06] ⚠ Issue {payload.get('issue_id')} categoría 'other' no es "
              f"auto-fixable (catch-all sin garantías). Degradando a grave.")
        payload["bucket"] = "grave"
        # Limpiar prompt_corregido para evitar que apply_auto_fixes lo intente
        payload["prompt_corregido"] = None

    return payload


def _persist_issue_payload(topic_id: str, payload: dict, n: int) -> Path:
    """Escribe data/issues_log/<topic_id>/<bucket>_NN.json."""
    out_dir = ISSUES_LOG_DIR / topic_id
    out_dir.mkdir(parents=True, exist_ok=True)
    bucket = payload.get("bucket", "unknown")
    out_file = out_dir / f"{bucket}_{n:02d}.json"
    out_file.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    return out_file


# ═══════════════════════════════════════════════════════════════
#  AUTO-FIX Y HANDOFF CC
# ═══════════════════════════════════════════════════════════════

def apply_auto_fixes(topic_id: str, payloads: list[dict]) -> int:
    """Aplica los auto_fixes sobre 03_visual.json. Reescribe el prompt
    de cada imagen identificada por (chapter_id, image_index) con el
    prompt_corregido del payload. Hace backup antes.

    Returns:
      Cantidad de fixes aplicados con éxito.
    """
    fixable = [p for p in payloads if p.get("bucket") == "auto_fixable"]
    if not fixable:
        return 0

    visual_path = STEPS_DIR / topic_id / "03_visual.json"
    if not visual_path.exists():
        print(f"  [06] ⚠ No existe {visual_path}, no se puede auto-fix.")
        return 0

    # Backup
    backup_path = visual_path.with_suffix(".json.bak_pre_m06")
    backup_path.write_text(visual_path.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"  [06] Backup escrito en {backup_path.name}")

    visual = json.loads(visual_path.read_text(encoding="utf-8"))
    n_applied = 0
    n_failed = 0

    # Indexar caps para acceso rápido
    caps_by_num = {c["chapter_number"]: c for c in visual.get("chapters", [])}

    for fix in fixable:
        cap_num = fix.get("chapter_id")
        img_idx = fix.get("image_index", 1)
        new_prompt = fix.get("prompt_corregido")

        cap = caps_by_num.get(cap_num)
        if not cap or not new_prompt:
            n_failed += 1
            continue

        # Caps veo: 1 imagen, prompt está en cap["image_prompt"]
        # Caps flux: array image_prompts[], item con prompt
        if cap.get("render_engine") == "veo" or "image_prompt" in cap:
            # Solo se reescribe el image_prompt; el video_prompt queda igual
            cap["image_prompt"] = new_prompt
            n_applied += 1
            print(f"  [06] ✓ cap {cap_num} (veo): image_prompt reescrito")
        else:
            items = cap.get("image_prompts", [])
            idx0 = img_idx - 1
            if 0 <= idx0 < len(items):
                items[idx0]["prompt"] = new_prompt
                n_applied += 1
                print(f"  [06] ✓ cap {cap_num} img {img_idx}: prompt reescrito")
            else:
                n_failed += 1
                print(f"  [06] ⚠ cap {cap_num} img {img_idx}: índice fuera de rango")

    visual_path.write_text(
        json.dumps(visual, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"  [06] {n_applied}/{len(fixable)} auto-fixes aplicados a {visual_path.name}")
    if n_failed:
        print(f"  [06] ⚠ {n_failed} fallaron (revisar logs arriba).")
    return n_applied


def generate_cc_handoff(topic_id: str, payloads: list[dict]) -> Path | None:
    """Genera un handoff CC en markdown para los issues bucket=grave que
    requieren cambio de código. Persiste en data/issues_log/<topic>/.

    Returns:
      Path al archivo escrito, o None si no había issues grave.
    """
    grave = [p for p in payloads if p.get("bucket") == "grave"]
    if not grave:
        print(f"  [06] No hay issues grave que requieran handoff CC.")
        return None

    # Agrupar por archivo sugerido
    from collections import defaultdict
    by_file = defaultdict(list)
    for p in grave:
        archivo = p.get("archivo_linea_sugerida") or "(sin archivo sugerido)"
        by_file[archivo].append(p)

    from datetime import datetime
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    out_path = ISSUES_LOG_DIR / topic_id / f"HANDOFF_CC_{ts}.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    lines = [
        f"# HANDOFF CLAUDE CODE — auto-generado por m06",
        f"",
        f"**Topic:** {topic_id}",
        f"**Generado:** {datetime.now().isoformat()}",
        f"**Issues grave requiriendo código:** {len(grave)}",
        f"",
        f"## Reglas inviolables",
        f"",
        f"1. NO modificar m05, m06, fase1_5.",
        f"2. Validar cada fix con smoke test antes de declarar OK.",
        f"3. Si un cambio requiere decisión arquitectónica, parar y reportar.",
        f"",
        f"## Issues a resolver, agrupados por archivo",
        f"",
    ]

    for archivo, issues in by_file.items():
        lines.append(f"### Archivo: `{archivo}` ({len(issues)} issue(s))")
        lines.append("")
        for i, issue in enumerate(issues, 1):
            lines.append(f"**Issue {i} — cap {issue.get('chapter_id')}/img {issue.get('image_index')}** "
                         f"({issue.get('category')}, cohort {issue.get('cohort')})")
            lines.append(f"")
            lines.append(f"- **Anchor:** {issue.get('anchor', '?')}")
            lines.append(f"- **Diagnóstico m06:** {issue.get('diagnostico_m06', '?')}")
            lines.append(f"- **Fix sugerido:** {issue.get('fix_sugerido', '?')}")
            lines.append(f"- **Prompt actual:**")
            lines.append(f"  ```")
            lines.append(f"  {issue.get('prompt_actual', '?')}")
            lines.append(f"  ```")
            lines.append(f"")
        lines.append("---")
        lines.append("")

    lines.extend([
        f"## Smoke tests al finalizar",
        f"",
        f"```bash",
        f"python test_module_03.py        # si tocaste m03",
        f"python test_module_05.py        # si tocaste m05",
        f"python -c \"import fase1_5; print('OK')\"",
        f"```",
        f"",
        f"## Después de aplicar",
        f"",
        f"Re-correr el topic con:",
        f"```bash",
        f"python fase1_5.py --topic {topic_id} --from m03",
        f"```",
    ])

    out_path.write_text("\n".join(lines), encoding="utf-8")
    print(f"  [06] Handoff CC escrito en {out_path}")
    return out_path


# ═══════════════════════════════════════════════════════════════
#  COMANDO RERUN
# ═══════════════════════════════════════════════════════════════

def _build_rerun_command(topic_id: str, grave_payloads: list[dict]) -> str:
    """Construye el comando rerun desde el módulo más temprano."""
    modules_culpables = [p.get("modulo_culpable") for p in grave_payloads if p.get("modulo_culpable")]
    earliest = _earliest_module(modules_culpables)

    if earliest == "m00":
        return (
            f"# m00 vive en fase1 (research), no en fase1.5.\n"
            f"# Re-run de m00 requiere correr fase1 con el seed original."
        )
    return f"python fase1_5.py --topic {topic_id} --from {earliest}"


# ═══════════════════════════════════════════════════════════════
#  MENÚ INTERACTIVO Y RESOLUCIÓN
# ═══════════════════════════════════════════════════════════════

def _print_summary(topic_id: str, payloads: list[dict]) -> None:
    by_bucket = {"auto_fixable": [], "grave": [], "minor": [], "false_positive": []}
    for p in payloads:
        bucket = p.get("bucket", "unknown")
        if bucket in by_bucket:
            by_bucket[bucket].append(p)

    print(f"\n{'═' * 60}")
    print(f"  📊 m06 — clasificación de issues para {topic_id}")
    print(f"{'═' * 60}\n")

    for bucket, items in by_bucket.items():
        if not items:
            continue
        emoji = {"auto_fixable": "🟢", "grave": "🔴", "minor": "🟡", "false_positive": "⚪"}[bucket]
        print(f"  {emoji} {bucket.upper()} ({len(items)})")
        for p in items:
            cap = p.get("chapter_id")
            img = p.get("image_index")
            cat = p.get("category")
            cohort = p.get("cohort")
            diag = (p.get("diagnostico_m06") or "")[:80]
            json_path = ISSUES_LOG_DIR / topic_id / f"{bucket}_{items.index(p)+1:02d}.json"
            print(f"    Cap {cap}/{img}  [{cat}, cohort {cohort}]")
            print(f"      → {diag}")
            print(f"      📄 {json_path}")
        print()


def _interactive_menu(
    topic_id: str,
    payloads: list[dict],
) -> str:
    """Muestra menú [A]/[H]/[P]/[R]/[E] y devuelve la opción elegida."""
    auto_fixable = [p for p in payloads if p.get("bucket") == "auto_fixable"]
    grave = [p for p in payloads if p.get("bucket") == "grave"]

    if grave:
        rerun_cmd = _build_rerun_command(topic_id, grave)
        print(f"\n  Si elegís [R] sin tocar nada, el comando sería:\n    {rerun_cmd}\n")

    while True:
        print(f"  Opciones:")
        if auto_fixable:
            print(f"    [A] Aplicar {len(auto_fixable)} auto-fix(es) sobre 03_visual.json y volver al menú")
        if grave:
            print(f"    [H] Generar handoff CC para los {len(grave)} grave (que requieren código)")
        print(f"    [P] Pasar todo (ensambla JSON final, agrega FPs aprobados al catálogo)")
        print(f"    [R] Rerun (imprime comando, NO ejecuta)")
        print(f"    [E] Exit (deja JSONs en disco, decidís después)")
        choice = input(f"\n  👉 [A/H/P/R/E]: ").strip().upper()
        if choice == "A":
            if auto_fixable:
                return choice
            print(f"  ⚠ No hay auto-fixables. Probá P, R o E.\n")
        elif choice == "H":
            if grave:
                return choice
            print(f"  ⚠ No hay grave. Probá P, R o E.\n")
        elif choice in ("P", "R", "E"):
            return choice
        else:
            print(f"  ⚠ Opción inválida.\n")


def _approve_false_positives(payloads: list[dict]) -> int:
    """Agrega FPs aprobados al catálogo. Retorna cantidad agregada."""
    fps = [p for p in payloads if p.get("bucket") == "false_positive"]
    if not fps:
        return 0

    existing = _load_known_fps()
    existing_ids = {e.get("id") for e in existing}

    n_added = 0
    for fp in fps:
        new_id = f"FP-{len(existing) + n_added + 1:03d}"
        if new_id in existing_ids:
            continue
        entry = {
            "id":                  new_id,
            "category":            fp.get("category"),
            "pattern":             fp.get("patron_para_log"),
            "reason":              fp.get("razon_fp"),
            "source_topic_id":     fp.get("issue_id"),
            "confirmed_at":        __import__("datetime").datetime.utcnow().isoformat() + "Z",
        }
        existing.append(entry)
        n_added += 1

    if n_added > 0:
        _save_known_fps(existing)
    return n_added


# ═══════════════════════════════════════════════════════════════
#  API PÚBLICA
# ═══════════════════════════════════════════════════════════════

def classify_and_decide(
    topic_id: str,
    judge_result: dict,
    interactive: bool = True,
    auto_pass: bool = False,
) -> dict:
    """Clasifica issues 3/3+2/3 emitidos por m05 y muestra menú interactivo.

    Args:
      topic_id: UUID del topic.
      judge_result: output de judge_topic_with_voting (con all_issues+cohort).
      interactive: si True (default), muestra menú [P]/[R]/[E].
                   Si False, solo persiste JSONs y retorna (audit-only).
      auto_pass: solo aplica con interactive=False. Si True (batch desatendido),
                 en vez de cortar en NON_INTERACTIVE (que dejaría final_path=None y
                 rompería el batch sin script.json), ensambla el JSON final como si
                 el humano hubiera elegido [P]. Los issues YA quedan logueados por
                 _persist_issue_payload. interactive=False SIN auto_pass sigue siendo
                 audit-only (comportamiento histórico intacto).

    Returns:
      dict {decision: "P"|"R"|"E"|"NO_ISSUES"|"PASS_VERDICT"|"AUTO_PASS"|"NON_INTERACTIVE",
            payloads: list, final_path: str | None,
            rerun_command: str | None, fps_added: int}
    """
    print(f"\n  [06] Iniciando clasificación de issues para {topic_id}...")

    # 0. Si verdict m05 es PASS, no hay nada que clasificar
    if judge_result.get("global_verdict") == "PASS":
        print(f"  [06] m05 verdict=PASS. Ensamblando JSON final directo...")
        final_path = assemble_final_script(topic_id)
        print(f"  [06] ✅ Final escrito: {final_path}")
        return {
            "decision":      "PASS_VERDICT",
            "payloads":      [],
            "final_path":    str(final_path),
            "rerun_command": None,
            "fps_added":     0,
        }

    # 1. Filtrar issues con cohort >= 2
    all_issues = judge_result.get("all_issues", [])
    relevant = [i for i in all_issues if (i.get("cohort") or 0) >= 2]
    print(f"  [06] Issues relevantes (cohort >= 2): {len(relevant)} de {len(all_issues)} totales.")

    if not relevant:
        print(f"  [06] No hay issues que clasificar. Ensamblando JSON final...")
        final_path = assemble_final_script(topic_id)
        return {
            "decision":      "NO_ISSUES",
            "payloads":      [],
            "final_path":    str(final_path),
            "rerun_command": None,
            "fps_added":     0,
        }

    # 2. Cargar contexto compartido
    visual = _load_step(topic_id, "03_visual.json")
    narration = _load_step(topic_id, "01b_narration.json")
    skeleton = _load_step(topic_id, "01a_skeleton.json")
    topic_facts = _load_topic_facts(topic_id)
    known_fps = _load_known_fps()

    # 3. Clasificar uno por uno
    payloads = []
    for n, issue in enumerate(relevant, 1):
        print(f"  [06] Clasificando issue {n}/{len(relevant)} (cap {issue.get('chapter_id')}/{issue.get('image_index')})...")
        payload = classify_one_issue(
            issue, topic_id, visual, narration, skeleton, topic_facts, known_fps
        )
        _persist_issue_payload(topic_id, payload, n)
        payloads.append(payload)

    # 4. Mostrar resumen
    _print_summary(topic_id, payloads)

    # 5. Menú o salida no-interactiva
    if not interactive:
        if auto_pass:
            # Batch desatendido: ensamblar como [P] (los issues ya quedaron logueados).
            # Sin esto, NON_INTERACTIVE deja final_path=None y el batch rompe sin
            # data/scripts/<id>.json.
            final_path = str(assemble_final_script(topic_id))
            fps_added = _approve_false_positives(payloads)
            print(f"\n  ✅ [06 auto-pass] JSON final escrito: {final_path}")
            if fps_added:
                print(f"  ✅ {fps_added} false positive(s) agregados a known_fps.json")
            return {
                "decision":      "AUTO_PASS",
                "payloads":      payloads,
                "final_path":    final_path,
                "rerun_command": None,
                "fps_added":     fps_added,
            }
        return {
            "decision":      "NON_INTERACTIVE",
            "payloads":      payloads,
            "final_path":    None,
            "rerun_command": None,
            "fps_added":     0,
        }

    # 6. Loop interactivo: [A] y [H] vuelven al menú
    final_path = None
    rerun_command = None
    fps_added = 0
    handoff_path = None

    while True:
        choice = _interactive_menu(topic_id, payloads)

        if choice == "A":
            n = apply_auto_fixes(topic_id, payloads)
            # Reclasificar: los auto_fixable aplicados quedan resueltos
            # → los marcamos como tal para que el menú siguiente NO los muestre
            for p in payloads:
                if p.get("bucket") == "auto_fixable":
                    p["bucket"] = "applied"  # bucket virtual post-fix
            print(f"\n  ✅ {n} auto-fix(es) aplicados. Volviendo al menú...\n")
            continue

        if choice == "H":
            handoff_path = str(generate_cc_handoff(topic_id, payloads))
            print(f"\n  📝 Handoff generado. Aplicalo con CC y después corré --from m03.")
            print(f"     Volviendo al menú por si querés [P], [R] o [E]...\n")
            continue

        if choice == "P":
            final_path = str(assemble_final_script(topic_id))
            fps_added = _approve_false_positives(payloads)
            print(f"\n  ✅ JSON final escrito: {final_path}")
            if fps_added:
                print(f"  ✅ {fps_added} false positive(s) agregados a known_fps.json")
            break

        if choice == "R":
            grave_now = [p for p in payloads if p.get("bucket") == "grave"]
            rerun_command = _build_rerun_command(topic_id, grave_now)
            print(f"\n  🔁 Aplicá el fix manualmente y después corré:\n    {rerun_command}\n")
            break

        if choice == "E":
            print(f"\n  ⏸ Salida sin decidir. JSONs quedan en data/issues_log/{topic_id}/")
            break

    return {
        "decision":      choice,
        "payloads":      payloads,
        "final_path":    final_path,
        "rerun_command": rerun_command,
        "handoff_path":  handoff_path,
        "fps_added":     fps_added,
    }
