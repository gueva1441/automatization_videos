"""
test_module_03.py — Prueba aislada del módulo 03 (extractor visual).

Toma un topic + skeleton (01a) + narración (01b) y le pide al módulo 03
los image_prompts[] EN con narration_anchor por imagen.
Desde chat 19 (refactor catálogo), m03 emite art_profile="" como
placeholder backward-compat. El estilo viene del system_instruction.

Requiere que 01a y 01b hayan corrido antes (que existan
01a_skeleton.json + 01b_narration.json en _steps/{topic_id}/).

Uso:
  python test_module_03.py
"""

import json
import re
from collections import Counter
from pathlib import Path

from script_engine.m03_visual import (
    assign_visual_prompts,
    VisualValidationError,
    _calculate_image_count,
    MIN_IMAGES_FLUX,
    MAX_IMAGES_FLUX,
    SECONDS_PER_IMAGE_TARGET,
    VEO_CHAPTERS,
    FLUX_CHAPTERS,
)


TOPICS_DB = Path("data") / "topics_db.json"
STEPS_DIR = Path("data") / "scripts" / "_steps"


# ═══════════════════════════════════════════════════════════════
#  CARGA
# ═══════════════════════════════════════════════════════════════

def _load_topics_db() -> list[dict]:
    if not TOPICS_DB.exists():
        return []
    try:
        data = json.loads(TOPICS_DB.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and "topics" in data:
        return data["topics"]
    return []


def _load_skeleton(topic_id: str) -> dict | None:
    """Lee skeleton 01a y filtra _distribution_plan."""
    f = STEPS_DIR / topic_id / "01a_skeleton.json"
    if not f.exists():
        return None
    try:
        data = json.loads(f.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None
    return {
        "topic_id": data.get("topic_id"),
        "chapters": data.get("chapters", []),
    }


def _load_narration(topic_id: str) -> dict | None:
    f = STEPS_DIR / topic_id / "01b_narration.json"
    if not f.exists():
        return None
    try:
        return json.loads(f.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return None


def _pick_topic_with_inputs(topics: list[dict]):
    """Devuelve (topic, skeleton, narration) o None."""
    eligible = []
    for t in topics:
        tid = t.get("id")
        if not tid:
            continue
        skel = _load_skeleton(tid)
        narr = _load_narration(tid)
        if (
            skel and len(skel.get("chapters") or []) == 7
            and narr and len(narr.get("chapters") or []) == 7
        ):
            eligible.append((t, skel, narr))

    if not eligible:
        return None

    if len(eligible) == 1:
        return eligible[0]

    print("\n  Topics con 01a + 01b disponibles:")
    for i, (t, _, _) in enumerate(eligible, start=1):
        title = t.get("video_title") or "(sin título)"
        print(f"    [{i}] {title}")

    while True:
        choice = input(f"\n  Elegí topic [1-{len(eligible)}]: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(eligible):
            return eligible[int(choice) - 1]
        print("  Inválido, probá de nuevo.")


# ═══════════════════════════════════════════════════════════════
#  AUDITORÍAS NUEVAS POST-AJUSTE 4e (criterios de sello del HANDOFF)
# ═══════════════════════════════════════════════════════════════

def _collect_visible_prompts(out: dict) -> list[tuple[str, str]]:
    """Devuelve [(label, texto)] de todos los prompts EN visibles
    (image_prompt + video_prompt en veo, prompt en flux). NO incluye
    narration_anchor (es ES, fragmento de narración legítima)."""
    items: list[tuple[str, str]] = []
    for ch in out.get("chapters", []):
        cn = ch.get("chapter_number", "?")
        if "image_prompt" in ch:
            items.append((f"cap{cn}.image_prompt", ch.get("image_prompt", "")))
        if "video_prompt" in ch:
            items.append((f"cap{cn}.video_prompt", ch.get("video_prompt", "")))
        for i, item in enumerate(ch.get("image_prompts", []) or [], start=1):
            items.append((f"cap{cn}.img{i}.prompt", item.get("prompt", "")))
    return items


def _audit_proper_names(prompts: list[tuple[str, str]], topic: dict) -> list[tuple[str, str]]:
    """Detecta nombres propios de personas en los prompts visibles.

    Estrategia: extrae los `name` de `documented_people` del topic y busca
    cada nombre completo + tokens individuales (mínimo 4 chars, exclusión
    de tokens muy comunes). Esto es preciso porque sabemos exactamente
    qué nombres están en juego (no falso-positivea topónimos como
    "Norfolk" o "Atlantic").

    Returns:
        list[(label, nombre detectado)] con los hits encontrados.
    """
    documented = topic.get("documented_people") or []
    if not documented:
        return []  # No hay lista canónica → no podemos auditar nombres

    # Tokens a buscar: nombre completo + cada palabra de >=4 chars
    tokens: list[str] = []
    EXCLUDE = {
        "American", "British", "Australian", "Naval", "Navy", "Army",
        "Captain", "Commander", "Officer", "Doctor", "Chief", "Vice",
        "Admiral", "First", "Class", "Lieutenant", "President", "Court",
        "Inquiry", "Special", "Projects", "Division", "Sonar", "Technician",
        "Boat", "Force", "United", "States", "USS",
    }
    for p in documented:
        full_name = (p.get("name") or "").strip()
        if not full_name:
            continue
        tokens.append(full_name)  # nombre completo
        for word in full_name.split():
            w = word.strip(".,;:")
            if len(w) >= 4 and w not in EXCLUDE and w[0].isupper():
                tokens.append(w)

    # Dedup conservando orden
    seen = set()
    uniq_tokens = []
    for t in tokens:
        if t.lower() not in seen:
            seen.add(t.lower())
            uniq_tokens.append(t)

    # Buscar cada token en cada prompt como palabra completa
    hits: list[tuple[str, str]] = []
    for label, text in prompts:
        for token in uniq_tokens:
            pattern = r"\b" + re.escape(token) + r"\b"
            if re.search(pattern, text):
                hits.append((label, token))
    return hits


# Patrones de texto literal/numérico visible en imagen.
# Los matches son señaladores (no bloqueantes); algunos pueden ser falsos
# positivos legítimos en contextos negados ("no readable text", "blurred
# headline area"). El ojo humano decide.
_LITERAL_TEXT_PATTERNS = [
    (re.compile(r"\blabeled\b", re.IGNORECASE), "labeled"),
    (re.compile(r"\bstamp(ed|ing)?\b", re.IGNORECASE), "stamp"),
    (re.compile(r"\binscribed\b", re.IGNORECASE), "inscribed"),
    (re.compile(r"\bengraved\s+with\b", re.IGNORECASE), "engraved with"),
    (re.compile(r"\bwith\s+text\b", re.IGNORECASE), "with text"),
    (re.compile(r"\bsign\s+(that\s+says|saying|reading)\b", re.IGNORECASE), "sign that says/saying/reading"),
    (re.compile(r"\bheadline\s+reading\b", re.IGNORECASE), "headline reading"),
    (re.compile(r"\bnameplate\b", re.IGNORECASE), "nameplate"),
    (re.compile(r"\bsignage\b", re.IGNORECASE), "signage"),
    (re.compile(r"\bsignpost\b", re.IGNORECASE), "signpost"),
    (re.compile(r"\bdisplaying\s+\d", re.IGNORECASE), "displaying <number>"),
    (re.compile(r"\bdisplaying\s+coordinates\b", re.IGNORECASE), "displaying coordinates"),
    (re.compile(r"\bcoordinates\s+\d", re.IGNORECASE), "coordinates <number>"),
    (re.compile(r"\bGPS\b"), "GPS (acronym text)"),
    (re.compile(r"\breads\s+['\"\u2018\u201c]", re.IGNORECASE), "reads '...'"),
    (re.compile(r"\bnumber\s+plate\b", re.IGNORECASE), "number plate"),
]


def _audit_literal_text(prompts: list[tuple[str, str]]) -> list[tuple[str, str, str]]:
    """Detecta pedidos de texto/números/letras visibles en imagen (regla 4).

    Returns:
        list[(label, pattern_name, fragmento_matcheado)]
    """
    hits: list[tuple[str, str, str]] = []
    for label, text in prompts:
        for pattern, name in _LITERAL_TEXT_PATTERNS:
            m = pattern.search(text)
            if m:
                hits.append((label, name, m.group(0)))
    return hits


# Patrones de marcador temporal explícito (regla 11).
# Si NINGUNO matchea en un prompt → falta marcador → flag.
_TEMPORAL_PATTERNS = [
    re.compile(r"\b\d{4}s\b"),                              # "1960s"
    re.compile(r"\b\d{4}\b"),                               # "1968"
    re.compile(r"\b'\d{2}s\b"),                             # "'60s"
    re.compile(r"\bvintage\b", re.IGNORECASE),
    re.compile(r"\bperiod[-\s]correct\b", re.IGNORECASE),
    re.compile(r"\bperiod[-\s]accurate\b", re.IGNORECASE),
    re.compile(r"\bantique\b", re.IGNORECASE),
    re.compile(r"\bmid[-\s]century\b", re.IGNORECASE),
    re.compile(r"\bmidcentury\b", re.IGNORECASE),
    re.compile(r"\b(early|mid|late)\s+\d{2}(th|st|nd|rd)?\s+century\b", re.IGNORECASE),
    re.compile(r"\b\d{2}(th|st|nd|rd)\s+century\b", re.IGNORECASE),
    re.compile(r"\bCold\s+War([-\s]era)?\b", re.IGNORECASE),
    re.compile(r"\bpost[-\s]war\b", re.IGNORECASE),
    re.compile(r"\bworld\s+war\b", re.IGNORECASE),
    re.compile(r"\bvictorian\b", re.IGNORECASE),
    re.compile(r"\bedwardian\b", re.IGNORECASE),
    re.compile(r"\bantebellum\b", re.IGNORECASE),
    re.compile(r"\b(industrial|atomic|space|jazz|swing|disco)\s+age\b", re.IGNORECASE),
]


def _has_temporal_marker(text: str) -> bool:
    """True si al menos un patrón temporal aparece en el texto."""
    return any(p.search(text) for p in _TEMPORAL_PATTERNS)


def _audit_temporal_markers(prompts: list[tuple[str, str]]) -> list[str]:
    """Devuelve los labels de prompts SIN marcador temporal explícito."""
    return [label for label, text in prompts if not _has_temporal_marker(text)]


def _print_post_4e_audits(out: dict, topic: dict) -> int:
    """Corre las 3 auditorías nuevas y las imprime. Devuelve el total
    de issues encontrados (suma de hits de las 3)."""
    prompts = _collect_visible_prompts(out)
    total_prompts = len(prompts)

    print("\n" + "─" * 70)
    print(f"  AUDITORÍAS POST-AJUSTE 4e (criterios de sello del HANDOFF)")
    print(f"  Total prompts EN auditados: {total_prompts}")
    print("─" * 70)

    # ─── 1. Nombres propios ───
    name_hits = _audit_proper_names(prompts, topic)
    print(f"\n  [1/3] Nombres propios de personas en prompts (regla 5 endurecida)")
    documented = topic.get("documented_people") or []
    if not documented:
        print(f"        ⚪ Topic sin documented_people → auditoría no aplicable.")
    elif not name_hits:
        print(f"        ✅ CERO nombres propios detectados ({len(documented)} personas en canon).")
    else:
        print(f"        ✗ {len(name_hits)} hit(s) — Flash incluyó nombre(s) en prompts:")
        for label, name in name_hits[:15]:
            print(f"          - {label}: \"{name}\"")
        if len(name_hits) > 15:
            print(f"          ... y {len(name_hits) - 15} más")

    # ─── 2. Texto literal ───
    literal_hits = _audit_literal_text(prompts)
    print(f"\n  [2/3] Texto/números/letras visibles en imagen (regla 4 endurecida)")
    if not literal_hits:
        print(f"        ✅ CERO referencias a texto literal detectadas.")
    else:
        print(f"        ✗ {len(literal_hits)} hit(s) — revisar manualmente (algunos pueden ser falsos positivos en contextos negados):")
        for label, pname, frag in literal_hits[:15]:
            print(f"          - {label}: pattern '{pname}' → \"{frag}\"")
        if len(literal_hits) > 15:
            print(f"          ... y {len(literal_hits) - 15} más")

    # ─── 3. Marcador temporal ───
    no_marker = _audit_temporal_markers(prompts)
    print(f"\n  [3/3] Marcador temporal explícito en cada prompt (regla 11 nueva)")
    if total_prompts == 0:
        print(f"        ⚪ Sin prompts para auditar.")
    elif not no_marker:
        print(f"        ✅ TODOS los {total_prompts} prompts tienen marcador temporal.")
    else:
        pct = (len(no_marker) / total_prompts) * 100
        print(f"        ✗ {len(no_marker)} de {total_prompts} prompts ({pct:.1f}%) SIN marcador temporal:")
        for label in no_marker[:15]:
            print(f"          - {label}")
        if len(no_marker) > 15:
            print(f"          ... y {len(no_marker) - 15} más")

    print("─" * 70)
    return len(name_hits) + len(literal_hits) + len(no_marker)


# ═══════════════════════════════════════════════════════════════
#  IMPRESIÓN DEL OUTPUT
# ═══════════════════════════════════════════════════════════════

def _print_assignment(out: dict, skeleton: dict, narration: dict) -> None:
    skel_by_n = {ch["chapter_number"]: ch for ch in skeleton["chapters"]}
    narr_by_n = {ch["chapter_number"]: ch for ch in narration["chapters"]}

    print("\n" + "═" * 70)
    print("  ✅ PROMPTS VISUALES GENERADOS")
    print("═" * 70)
    print(f"\n  topic_id : {out.get('topic_id')}")

    ranks_used: list[str] = []
    total_imgs = 0

    for ch in out.get("chapters", []):
        cn = ch.get("chapter_number")
        sch = skel_by_n.get(cn, {})
        engine = sch.get("render_engine", "?")
        title = sch.get("title", "")

        print(f"\n  ── Cap {cn} ({engine}) ───────────────────────────────────")
        print(f"     title          : {title}")
        print(f"     profile (cap)  : (decidido por imagen — sin default)")

        if engine == "veo":
            ip = ch.get("image_prompt", "")
            vp = ch.get("video_prompt", "")
            sr = ch.get("subject_ref", "")
            anc = ch.get("narration_anchor", "")
            total_imgs += 1
            print(f"     image_prompt   : ({len(ip)} chars) {ip[:120]}...")
            print(f"     video_prompt   : ({len(vp)} chars) {vp[:120]}...")
            print(f"     subject_ref    : {sr}")
            print(f"     anchor         : \"{anc[:90]}{'...' if len(anc) > 90 else ''}\"")

        elif engine == "flux":
            imgs = ch.get("image_prompts", [])
            # Chat 30: _calculate_image_count requiere cap_duration_sec, no
            # narration. No tenemos el sync_map a mano acá — mostramos solo
            # cantidad real generada.
            print(f"     image_prompts  : {len(imgs)} generadas")

            for i, item in enumerate(imgs, start=1):
                rank = item.get("emotional_rank", "?")
                anc = item.get("narration_anchor", "")
                p = item.get("prompt", "")
                ranks_used.append(rank)
                print(f"       [{i:>2}] {rank}")
                print(f"            prompt ({len(p)} chars): {p[:100]}...")
                print(f"            anchor: \"{anc[:80]}{'...' if len(anc) > 80 else ''}\"")

            total_imgs += len(imgs)

    # ─── Auditorías ───
    print("\n" + "─" * 70)
    print(f"  Total imágenes (caps veo + flux) : {total_imgs}")

    # Distribución de emotional_rank
    if ranks_used:
        counter_r = Counter(ranks_used)
        total = len(ranks_used)
        print(f"\n  Distribución emotional_rank (total {total} imgs flux):")
        for rank in ("R1", "R2", "R3"):
            n = counter_r.get(rank, 0)
            pct = (n / total * 100) if total else 0
            print(f"    {rank} : {n:>3}  ({pct:>4.1f}%)")

    # Re-chequeo de anchors (sanity check externo)
    print("\n  Sanity check de anchors:")
    anchor_issues = 0
    for ch in out.get("chapters", []):
        cn = ch.get("chapter_number")
        narr_text = (narr_by_n.get(cn, {}).get("narration") or "")

        if cn in VEO_CHAPTERS:
            anc = ch.get("narration_anchor", "")
            if anc and narr_text.find(anc) < 0:
                print(f"    ✗ cap {cn} (veo): anchor NO encontrado en narración")
                anchor_issues += 1
        elif cn in FLUX_CHAPTERS:
            imgs = ch.get("image_prompts", [])
            last_pos = -1
            for i, item in enumerate(imgs, start=1):
                anc = item.get("narration_anchor", "")
                pos = narr_text.find(anc) if anc else -1
                if pos < 0:
                    print(f"    ✗ cap {cn} img {i}: anchor NO está en narración")
                    anchor_issues += 1
                elif pos <= last_pos:
                    print(f"    ✗ cap {cn} img {i}: anchor fuera de orden")
                    anchor_issues += 1
                last_pos = max(last_pos, pos)

    if anchor_issues == 0:
        print("    ✅ todos los anchors son substring exacto y están en orden")
    else:
        print(f"    ⚠  {anchor_issues} problemas detectados (no debería pasar — bug en validador)")

    # Rangos de chars de prompts.
    short_prompts = 0
    long_prompts = 0
    for ch in out.get("chapters", []):
        if "image_prompt" in ch:
            n = len(ch["image_prompt"])
            if n < 300: short_prompts += 1
            if n > 800: long_prompts += 1
        if "image_prompts" in ch:
            for item in ch["image_prompts"]:
                n = len(item.get("prompt", ""))
                if n < 300: short_prompts += 1
                if n > 800: long_prompts += 1

    if short_prompts == 0 and long_prompts == 0:
        print(f"  ✅ Todos los prompts en rango post-stitch 300-800 chars.")
    else:
        print(f"  ⚠  Prompts fuera de rango post-stitch: {short_prompts} cortos, {long_prompts} largos")

    print("─" * 70)


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════

# ═══════════════════════════════════════════════════════════════
#  CHECKS OFFLINE — DEPRECADOS
# ═══════════════════════════════════════════════════════════════
# Chat 30: eliminado _offline_prompt_checks (validaba literales del
# system_instruction viejo del chat 19; chat 30 reescribió completo
# el system_instruction y los checks quedaron desactualizados).
# Si en el futuro se quieren checks offline del SYSTEM_INSTRUCTION nuevo,
# armarlos como tests aislados separados (test_module_03_offline.py) que
# validen los elementos críticos del prompt structure (subject-first, no
# negatives, ethnicity default), NO literales de palabras.


# ═══════════════════════════════════════════════════════════════
#  MAIN — live test
# ═══════════════════════════════════════════════════════════════

def main():
    print("\n" + "═" * 70)
    print("  🧪 TEST MÓDULO 03 — extractor visual")
    print("═" * 70)
    print(f"\n  Fórmula imgs flux : clamp(round(audio_sec/{SECONDS_PER_IMAGE_TARGET}), {MIN_IMAGES_FLUX}, {MAX_IMAGES_FLUX})")

    # Offline checks: deprecados chat 30 (ver bloque eliminado arriba).
    # Conservamos --offline-only por compat con scripts que lo pasen;
    # ahora simplemente sale sin hacer nada.
    import sys
    if "--offline-only" in sys.argv:
        print("\n  (offline checks deprecados — chat 30. Saliendo sin live test.)")
        return

    topics = _load_topics_db()
    if not topics:
        print(f"\n  ❌ No hay topics en {TOPICS_DB}.")
        return

    triple = _pick_topic_with_inputs(topics)
    if not triple:
        print(
            f"\n  ❌ Ningún topic tiene 01a + 01b completos en "
            f"{STEPS_DIR}/{{topic_id}}/."
        )
        print("     Corré primero test_module_01a y _01b.")
        return

    topic, skeleton, narration = triple
    title = topic.get("video_title")
    print(f"\n  Topic seleccionado : {title}")
    print(f"  topic_id           : {topic.get('id')}")
    print(f"  Skeleton           : {len(skeleton['chapters'])} caps")
    print(f"  Narración          : {len(narration['chapters'])} caps")

    # Pre-cálculo: deshabilitado chat 30. _calculate_image_count cambió firma
    # en chat 27 PR 3 (ahora recibe cap_duration_sec: float, no narration: str).
    # Para calcular acá necesitaríamos cargar sync_map (output/audio/<id>/sync_map.json)
    # y derivar la duración por cap — overhead que no aporta al test (la lógica
    # real corre dentro de assign_visual_prompts con su propio sync_map autoritativo).
    # Mostramos info estática en su lugar.
    print(f"\n  Llamadas Gemini Flash : ~5 (1 por cap flux, secuencial). Caps veo (hook+outro) NO llaman LLM en m03.")
    print(f"  Estimado costo        : ~$0.01-0.02")
    print(f"  Estimado tiempo       : ~30-50s")

    confirm = input("\n  ¿Arrancar? [S/n]: ").strip().lower()
    if confirm in ("n", "no"):
        print("  Abortado.")
        return

    # Chat 29 #175: assign_visual_prompts requiere sync_map para caps veo
    # híbridos (necesario para calcular timings de los supps Flux).
    # Cargamos el sync_map del topic desde output/audio/<id>/sync_map.json
    sync_map_path = Path("output") / "audio" / topic.get("id") / "sync_map.json"
    if not sync_map_path.exists():
        print(f"\n  ❌ sync_map no encontrado: {sync_map_path}")
        print("     Corré primero audio_manager / test_module_02 para generarlo.")
        return
    sync_map = json.loads(sync_map_path.read_text(encoding="utf-8"))
    print(f"  sync_map cargado   : {sync_map_path} ({len(sync_map.get('chapters', []))} caps)")

    print("\n  Llamando al módulo 03...")
    print("  " + "─" * 60)
    try:
        out = assign_visual_prompts(topic, skeleton, narration, sync_map)
    except VisualValidationError as e:
        print(f"\n  ❌ Validación fallada: {e}")
        return
    except Exception as e:
        print(f"\n  ❌ Error inesperado: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return
    print("  " + "─" * 60)

    _print_assignment(out, skeleton, narration)

    issues = _print_post_4e_audits(out, topic)

    out_file = STEPS_DIR / topic["id"] / "03_visual.json"
    if out_file.exists():
        size_kb = out_file.stat().st_size / 1024
        print(f"\n  📁 Persistido: {out_file} ({size_kb:.1f} KB)")
    else:
        print(f"\n  ⚠  No se encontró {out_file}")

    print("\n" + "═" * 70)
    if issues == 0:
        print("  ✅ Prueba completada — TODOS los criterios de sello pasados")
        print(f"     (corré también con el OTRO topic antes de declarar m03 SELLADO)")
    else:
        print(f"  ⚠  Prueba completada — {issues} issue(s) detectado(s) en auditorías 4e")
        print(f"     Revisar arriba: nombres propios / texto literal / marcador temporal")
    print("═" * 70 + "\n")


if __name__ == "__main__":
    main()
