"""
gfx_director.py — Director de gráficos por capítulo (Gemini Flash, 1 call por cap).

Patrón flow_director/flow_config (D8: director separado, comparte insumos, no prompt):
  1. System prompt con el inventario inmutable de gfx_config (el LLM SOLO elige de ahí).
  2. response_schema estricto (call_flash_json).
  3. Validación determinista post-LLM: índices en rango, máximos del inventario, regla de
     omisión por text_in_image, textos literales del fact elegido, sin solapes. Bloques
     inválidos se DESCARTAN (nunca lanza).
  4. Fallback estático si Gemini falla: solo title_card (no inventa datos).
  5. shot_transition y grade NO los decide el LLM (deterministas).

D7: el LLM nunca escribe texto libre. Para cada bloque con texto devuelve fact_idx y un
extracto que DEBE ser substring literal del fact (doc maestro §3 "text (literal)"); el
validador lo comprueba y gfx_literal_lock lo vuelve a comprobar contra todas las fuentes.

Cache por cap: work_dir/gfx_plan_chXX.json (respuesta cruda + versión de prompt).

F2 §1 (director v1):
  - Facts POR CAP: hard_fact_ids de las image_prompts del cap + facts que comparten ≥ 1 entidad
    (año, nombre, lugar) con la narración. Si quedan < 2 → facts de los caps vecinos, marcados
    foráneos (solo data_callout).
  - Guard de época: year del fact fuera de era_window del cap (años de la narración ± 1) → no elegible,
    salvo que la narración diga ese año literal.
  - Anti-spoiler: en ch01 no entran facts que solo aparecen en ch06–ch07.
  - Hueco > interrupt_max_sec: el VALIDADOR (no el LLM) inserta un data_callout con el siguiente fact
    elegible que la voz dice en ese tramo; si no hay, un punch_in en la palabra de más énfasis.
  - Box del zoom: lo decide visión (judge_zoom_box) sobre el frame real; null → sin zoom.
  - Titular del recorte nunca substring del cuerpo (ni al revés).
"""
from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

from config import DATA_DIR
from cost_tracker import cost_tracker
from error_handler import error_handler, PipelineStage
from gemini_helpers import call_flash_json

from gfx_config import (
    VALID_CALLOUT_KINDS,
    clamp_box,
    gfx_rules,
    max_per_cap,
    render_inventory_for_prompt,
)
from script_engine.gfx_literal_lock import normalize


# ═══════════════════════════════════════════════════════════════
#  Contexto del cap (insumos compartidos con m03/flow_director, sin LLM)
# ═══════════════════════════════════════════════════════════════

def load_chapter_context(video_id: str, chplan: Any) -> dict[str, Any]:
    """Lee script, verified_facts, skeleton y canonical del cap. Fuentes del candado literal."""
    script = json.loads((DATA_DIR / "scripts" / f"{video_id}.json").read_text(encoding="utf-8"))
    n = int(str(chplan.chapter_id).replace("ch", ""))
    chapter = next((c for c in script.get("chapters", []) if int(c.get("chapter_number", -1)) == n),
                   script["chapters"][n - 1])
    topic_id = script.get("topic_id") or video_id
    steps = DATA_DIR / "scripts" / "_steps" / topic_id
    skeleton_ch: dict[str, Any] = {}
    canonical: Any = {}
    try:
        sk = json.loads((steps / "01a_skeleton.json").read_text(encoding="utf-8"))
        skeleton_ch = next((c for c in sk.get("chapters", []) if c.get("chapter_number") == n), {})
    except (OSError, ValueError):
        pass
    try:
        canonical = json.loads((steps / "02_canonical.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        canonical = {"canonical_subject_description": script.get("canonical_subject_description", "")}

    # verified_facts sin `id`: el orden ES el id (F01 = índice 0). Deuda anotada en DOC_MAESTRO §6.
    facts = [f["fact"] if isinstance(f, dict) else str(f) for f in script.get("verified_facts", [])]
    sources: dict[str, str] = {f"verified_facts[{i}]": t for i, t in enumerate(facts)}
    sources[f"narration_ch{n:02d}"] = chplan.narration or chapter.get("narration", "")
    if skeleton_ch.get("title"):
        sources["skeleton.title"] = skeleton_ch["title"]
    for j, b in enumerate(skeleton_ch.get("bullets", []) or []):
        sources[f"skeleton.bullets[{j}]"] = b
    sources["canonical"] = json.dumps(canonical, ensure_ascii=False)
    narration = sources[f"narration_ch{n:02d}"]
    eligible, era = eligible_facts(facts, script.get("chapters", []), n, narration)
    return {
        "video_id": video_id, "chapter_number": n, "script_chapter": chapter,
        "facts": facts, "skeleton": skeleton_ch, "canonical": canonical, "sources": sources,
        "eligible": eligible, "era_window": era,
    }


# ═══════════════════════════════════════════════════════════════
#  F2 §1: facts por cap, época y anti-spoiler (determinista)
# ═══════════════════════════════════════════════════════════════

_YEAR_RE = re.compile(r"\b(1[5-9]\d\d|20\d\d)\b")
# Nombre propio: palabra capitalizada que NO abre oración (las que abren oración son ambiguas)
_NAME_RE = re.compile(r"(?<![.!?¿¡:]\s)(?<!^)(?<![.!?¿¡:])\b([A-ZÁÉÍÓÚÑ][a-záéíóúñ]{2,}|[A-Z]{2,})\b")


def fact_year(text: str) -> int | None:
    """Primer año 1500–2099 del texto (regex de 4 dígitos)."""
    m = _YEAR_RE.search(text)
    return int(m.group(1)) if m else None


def entities(text: str) -> set[str]:
    """Entidades comparables: años + nombres propios (palabras capitalizadas que no abren oración)."""
    return set(_YEAR_RE.findall(text)) | {w.lower() for w in _NAME_RE.findall(text)}


def _hard_ids(chapter: dict[str, Any]) -> set[int]:
    """Índices de facts citados por las image_prompts del cap ('F03' → 2)."""
    out: set[int] = set()
    for p in chapter.get("image_prompts", []) or []:
        for fid in (p.get("hard_fact_ids") or []) if isinstance(p, dict) else []:
            m = re.fullmatch(r"F(\d+)", str(fid).strip())
            if m:
                out.add(int(m.group(1)) - 1)
    return out


def eligible_facts(facts: list[str], chapters: list[dict[str, Any]], n: int, narration: str
                   ) -> tuple[dict[int, bool], list[int]]:
    """Facts elegibles del cap n → ({fact_idx: foráneo}, era_window [min, max] o []).

    Propios: hard_fact_ids del cap ∪ facts con ≥ 1 entidad compartida con la narración.
    Si quedan < 2: + hard_fact_ids de los caps n−1 y n+1 como foráneos (solo data_callout).
    Guard de época y anti-spoiler aplican a todos.
    """
    by_n = {int(c.get("chapter_number", i + 1)): c for i, c in enumerate(chapters)}
    ids_by_cap = {k: _hard_ids(c) for k, c in by_n.items()}
    narr_ents = entities(narration)
    own = {i for i in ids_by_cap.get(n, set()) if 0 <= i < len(facts)}
    own |= {i for i, f in enumerate(facts) if entities(f) & narr_ents}

    # era_window: años de la narración ± 1; sin años → años de los facts propios por hard_fact_ids
    years = [int(y) for y in _YEAR_RE.findall(narration)]
    if not years:
        years = [y for i in ids_by_cap.get(n, set()) if 0 <= i < len(facts) for y in [fact_year(facts[i])] if y]
    era = [min(years) - 1, max(years) + 1] if years else []

    def _ok(i: int) -> bool:
        y = fact_year(facts[i])
        if era and y is not None and not (era[0] <= y <= era[1]) and str(y) not in narration:
            return False                                   # guard de época
        if n == 1:                                         # anti-spoiler del hook
            caps = {k for k, ids in ids_by_cap.items() if i in ids}
            if caps and min(caps) >= 6:
                return False
        return True

    out = {i: False for i in sorted(own) if _ok(i)}
    if len(out) < 2:
        for k in (n - 1, n + 1):
            for i in sorted(ids_by_cap.get(k, set())):
                if 0 <= i < len(facts) and i not in out and _ok(i):
                    out[i] = True
    return out, era


# ═══════════════════════════════════════════════════════════════
#  Prompt + schema
# ═══════════════════════════════════════════════════════════════

_SYSTEM_PROMPT = f"""Sos director de gráficos de un documental largo de historia oscura (16:9, YouTube).
Para UN capítulo elegís qué bloques gráficos usar, dónde y con qué dato. Identidad > vistosidad:
pocos bloques, siempre los mismos, solo donde un dato real lo justifica.

INVENTARIO EXACTO — usá SOLO estos bloques:
{render_inventory_for_prompt()}

REGLAS DURAS:
- NUNCA escribas texto propio. Todo texto que devuelvas (text, headline, kicker, value, unit) tiene que
  ser un FRAGMENTO COPIADO LITERAL (mismas palabras, mismos números, misma ortografía) del fact cuyo
  fact_idx indicás. Si no hay fragmento literal adecuado, no uses el bloque.
- data_callout: máx {max_per_cap("data_callout")}. text = el dato corto (año, cifra con unidad, nombre o lugar), 1–6 palabras,
  copiado del fact. trigger_word_idx = índice de WORDS donde la voz empieza a decir ese dato (o la
  palabra más cercana). NO pongas un callout si el TEXTO EN IMAGEN de esa escena ya muestra el dato.
- count_up: máx {max_per_cap("count_up")}, solo si el fact trae una cifra escrita con dígitos (ej. "6,500"). value = esa cifra
  exacta, unit = la palabra que la sigue en el fact (o "").
- archive_clippings: lista de 0–{max_per_cap("archive_clipping")}, cada uno en una escena distinta de ≥ 4 s y SOLO con facts de texto
  suficiente (≥ 12 palabras). headline = fragmento literal corto del fact (≤ 8 palabras, NO el fact entero);
  kicker = fragmento literal de 1–3 palabras del mismo fact (lugar o fecha) o "".
- evidence_zoom: máx {max_per_cap("evidence_zoom")}, en una escena de ≥ 3.1 s (el zoom ocupa el FINAL de esa escena), sobre un detalle
  concreto descrito en el prompt de la imagen. box = [x, y, w, h] normalizado 0–1.
- punch_in_word_idx: máx {max_per_cap("punch_in")}, palabras de énfasis (idealmente las de los callouts).
- Pattern interrupt: intentá que haya un bloque visible cada {gfx_rules.interrupt_min_sec:.0f}–{gfx_rules.interrupt_max_sec:.0f} s, pero SOLO con datos reales.
- Un bloque con máx 0 está APAGADO para este canal: no lo uses.
- title_card.use = true siempre.
- Si un bloque no aplica: use=false (o lista vacía).
"""

_SCHEMA: dict[str, Any] = {
    "type": "OBJECT",
    "properties": {
        "title_card": {"type": "OBJECT", "properties": {"use": {"type": "BOOLEAN"}}, "required": ["use"]},
        "callouts": {"type": "ARRAY", "items": {
            "type": "OBJECT",
            "properties": {
                "fact_idx": {"type": "INTEGER"}, "text": {"type": "STRING"},
                "trigger_word_idx": {"type": "INTEGER"},
                "kind": {"type": "STRING", "enum": sorted(VALID_CALLOUT_KINDS)},
            },
            "required": ["fact_idx", "text", "trigger_word_idx", "kind"]}},
        "archive_clippings": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
            "fact_idx": {"type": "INTEGER"}, "scene_idx": {"type": "INTEGER"},
            "headline": {"type": "STRING"}, "kicker": {"type": "STRING"}},
            "required": ["fact_idx", "scene_idx", "headline", "kicker"]}},
        "evidence_zoom": {"type": "OBJECT", "properties": {
            "use": {"type": "BOOLEAN"}, "scene_idx": {"type": "INTEGER"},
            "box": {"type": "ARRAY", "items": {"type": "NUMBER"}}},
            "required": ["use", "scene_idx", "box"]},
        "count_up": {"type": "OBJECT", "properties": {
            "use": {"type": "BOOLEAN"}, "fact_idx": {"type": "INTEGER"}, "value": {"type": "STRING"},
            "unit": {"type": "STRING"}, "trigger_word_idx": {"type": "INTEGER"}},
            "required": ["use", "fact_idx", "value", "unit", "trigger_word_idx"]},
        "punch_in_word_idx": {"type": "ARRAY", "items": {"type": "INTEGER"}},
    },
    "required": ["title_card", "callouts", "archive_clippings", "evidence_zoom", "count_up", "punch_in_word_idx"],
}


def _build_user_prompt(ctx: dict[str, Any], words: list[dict], scenes: list[Any]) -> str:
    ch = ctx["script_chapter"]
    prompts = ch.get("image_prompts") or []
    lines = [f"CAPÍTULO {ctx['chapter_number']} — título: {ctx['skeleton'].get('title', '')}",
             f"Bullets: {' | '.join(ctx['skeleton'].get('bullets', []) or [])}",
             f"Duración: {scenes[-1].end:.1f} s", "",
             "VERIFIED_FACTS DE ESTE CAPÍTULO (fact_idx: texto). Usá SOLO estos índices; "
             "los marcados [FORÁNEO] solo sirven para data_callout:"]
    elig = ctx.get("eligible")
    for i, f in enumerate(ctx["facts"]):
        if elig is None or i in elig:
            lines.append(f"  {i}: {'[FORÁNEO] ' if elig and elig.get(i) else ''}{f}")
    lines += ["", "ESCENAS (scene_idx: inicio–fin, rank, texto en imagen, prompt de imagen):"]
    for s in scenes:
        p = prompts[s.idx] if s.idx < len(prompts) else {}
        desc = (p.get("prompt") or "")[:220] if isinstance(p, dict) else ""
        lines.append(f"  {s.idx}: {s.start:.1f}–{s.end:.1f}s {s.rank} | texto_en_imagen='{s.text_in_image}' | {desc}")
    lines += ["", "WORDS (idx:palabra@segundo):"]
    lines.append(" ".join(f"{i}:{w['word']}@{float(w['start']):.1f}" for i, w in enumerate(words)))
    lines += ["", "Devolvé el JSON del plan."]
    return "\n".join(lines)


# ═══════════════════════════════════════════════════════════════
#  Validación determinista (nunca lanza)
# ═══════════════════════════════════════════════════════════════

def archive_body(headline: str, fact: str) -> str:
    """Cuerpo del recorte. Por default NO hay cuerpo (kicker + titular). Solo si el titular tiene
    ≤ archive_body_head_max_words palabras va un cuerpo literal cortado en frase completa ("" si no hay corte limpio)."""
    if not gfx_rules.archive_body_default and len(headline.split()) > gfx_rules.archive_body_head_max_words:
        return ""
    return trim_body(fact) or ""


def trim_body(fact: str, max_words: int | None = None) -> str | None:
    """Cuerpo del recorte: prefijo LITERAL del fact con ≤ max_words palabras, cortado en frase completa.

    Primero oraciones enteras (. ! ? ;). Si la primera oración ya se pasa, corta en la última pausa
    (, :) que entre; el signo de la pausa se quita (no se agrega nada: el candado literal sigue pasando).
    None si no hay ningún corte limpio.
    """
    max_words = max_words or gfx_rules.archive_body_max_words
    text = re.sub(r"\s+", " ", fact).strip()
    if len(text.split()) <= max_words:
        return text
    best = None
    for m in re.finditer(r"[.!?;](?=\s|$)", text):
        cand = text[:m.end()]
        if len(cand.split()) <= max_words:
            best = cand
    if best:
        return best
    for m in re.finditer(r"[,:](?=\s)", text):
        cand = text[:m.start()]
        if len(cand.split()) <= max_words:
            best = cand
    return best


def _literal_in(fragment: str, fact: str) -> bool:
    return bool(normalize(fragment)) and normalize(fragment) in normalize(fact)


def _shown_in_image(text: str, image_text: str) -> bool:
    """Regla de omisión: el dato ya está en la imagen (texto o cifras de ≥ 2 dígitos)."""
    if not image_text:
        return False
    it = normalize(image_text)
    if normalize(text) in it:
        return True
    return any(d in it for d in re.findall(r"\d{2,}", text))


def validate_plan(raw: dict[str, Any], *, n_facts: int, n_words: int, scenes: list[Any],
                  facts: list[str], log: list[str] | None = None,
                  eligible: dict[int, bool] | None = None) -> dict[str, Any]:
    """Valida y repara el plan crudo del LLM. Descarta lo inválido; nunca lanza.

    eligible: {fact_idx: foráneo} del cap (F2 §1). None = todos elegibles (compat).
    Un fact no elegible se descarta; uno foráneo solo vale para data_callout.
    """
    log = log if log is not None else []
    if not isinstance(raw, dict):
        raw = {}
    n_scenes = len(scenes)

    def _idx(v: Any, n: int) -> int | None:
        try:
            i = int(v)
        except (TypeError, ValueError):
            return None
        return i if 0 <= i < n else None

    def _fact(v: Any, block: str) -> int | None:
        """Índice de fact válido Y elegible para ese bloque (si no, None + log)."""
        i = _idx(v, n_facts)
        if i is None or eligible is None:
            return i
        if i not in eligible:
            log.append(f"{block} descartado (fact {i} no es de este cap / fuera de época)")
            return None
        if eligible[i] and block != "data_callout":
            log.append(f"{block} descartado (fact {i} foráneo: solo data_callout)")
            return None
        return i

    plan: dict[str, Any] = {"title_card": {"use": True}, "callouts": [], "archive_clippings": [],
                            "evidence_zoom": None, "count_up": None, "punch_in_word_idx": []}

    for c in (raw.get("callouts") or [])[:20]:
        if not isinstance(c, dict):
            continue
        fi, wi = _fact(c.get("fact_idx"), "data_callout"), _idx(c.get("trigger_word_idx"), n_words)
        text, kind = str(c.get("text", "")).strip(), c.get("kind")
        if fi is None or wi is None or kind not in VALID_CALLOUT_KINDS:
            log.append(f"callout descartado (índice/kind): {c}")
            continue
        if not _literal_in(text, facts[fi]) or len(text.split()) > 8:
            log.append(f"callout descartado (no literal del fact {fi}): {text!r}")
            continue
        plan["callouts"].append({"fact_idx": fi, "text": text, "trigger_word_idx": wi, "kind": kind,
                                 "foreign": bool(eligible and eligible.get(fi))})
    if len(plan["callouts"]) > max_per_cap("data_callout"):
        log.append(f"callouts recortados {len(plan['callouts'])} → {max_per_cap('data_callout')}")
        plan["callouts"] = plan["callouts"][: max_per_cap("data_callout")]

    arcs = raw.get("archive_clippings")
    if not isinstance(arcs, list):           # compat cache F1: un solo objeto con "use"
        one = raw.get("archive_clipping") or {}
        arcs = [one] if isinstance(one, dict) and one.get("use") else []
    used_facts, used_scenes = set(), set()
    for a in arcs[:6]:
        if not isinstance(a, dict):
            continue
        fi, si = _fact(a.get("fact_idx"), "archive"), _idx(a.get("scene_idx"), n_scenes)
        head, kick = str(a.get("headline", "")).strip(), str(a.get("kicker", "")).strip()
        if fi is None or si is None:
            log.append(f"archive descartado (índice): {a}")
        elif scenes[si].duration < gfx_rules.archive_min_scene:
            log.append(f"archive descartado (escena {si} dura {scenes[si].duration:.1f}s)")
        elif not _literal_in(head, facts[fi]) or (kick and not _literal_in(kick, facts[fi])):
            log.append(f"archive descartado (headline/kicker no literal del fact {fi})")
        elif len(head.split()) > gfx_rules.archive_head_max_words:
            log.append(f"archive descartado (titular de {len(head.split())} palabras > {gfx_rules.archive_head_max_words}): {head!r}")
        elif fi in used_facts or si in used_scenes:
            log.append(f"archive descartado (fact {fi} o escena {si} repetidos)")
        elif len(plan["archive_clippings"]) >= gfx_rules.archive_max_per_cap:
            log.append(f"archive recortado (máx {gfx_rules.archive_max_per_cap} por cap)")
        else:
            used_facts.add(fi)
            used_scenes.add(si)
            plan["archive_clippings"].append({"fact_idx": fi, "scene_idx": si, "headline": head, "kicker": kick})

    z = raw.get("evidence_zoom") or {}
    if isinstance(z, dict) and z.get("use") and max_per_cap("evidence_zoom") > 0:
        si, box = _idx(z.get("scene_idx"), n_scenes), clamp_box(z.get("box") or [])
        if si is None or box is None:
            log.append(f"zoom descartado (índice/box): {z}")
        elif scenes[si].duration < gfx_rules.zoom_min_scene:
            log.append(f"zoom descartado (escena {si} dura {scenes[si].duration:.1f}s)")
        else:
            plan["evidence_zoom"] = {"scene_idx": si, "box": box}

    cu = raw.get("count_up") or {}
    if isinstance(cu, dict) and cu.get("use") and max_per_cap("count_up") > 0:
        fi, wi = _fact(cu.get("fact_idx"), "count_up"), _idx(cu.get("trigger_word_idx"), n_words)
        val, unit = str(cu.get("value", "")).strip(), str(cu.get("unit", "")).strip()
        if fi is None or wi is None or not re.fullmatch(r"[\d.,]+%?", val) or not _literal_in(val, facts[fi]):
            log.append(f"count_up descartado: {cu}")
        else:
            plan["count_up"] = {"fact_idx": fi, "value": val, "unit": unit if _literal_in(unit, facts[fi]) else "",
                                "trigger_word_idx": wi}

    pw = [i for i in (_idx(v, n_words) for v in (raw.get("punch_in_word_idx") or [])) if i is not None]
    plan["punch_in_word_idx"] = sorted(set(pw))[: max_per_cap("punch_in")]
    return plan


# ═══════════════════════════════════════════════════════════════
#  Resolución: índices → textos literales + tiempos (determinista)
# ═══════════════════════════════════════════════════════════════

def _era_decade(text: str, fallback: int = 2000) -> int:
    years = [int(y) for y in re.findall(r"\b(1[5-9]\d\d|20\d\d)\b", text)]
    return (years[0] // 10) * 10 if years else fallback


def callout_duration(text: str, trigger_idx: int, words: list[dict], time_offset: float = 0.0) -> float:
    """F1b: 0.4 s × palabras + 1.0 s, mínimo 2.5 s, y NUNCA termina antes del fin de la frase hablada
    (siguiente palabra con puntuación de cierre en `words`, desde el trigger)."""
    d = max(gfx_rules.callout_dur_min, gfx_rules.callout_sec_per_word * len(text.split()) + gfx_rules.callout_base_sec)
    if gfx_rules.callout_until_phrase_end and words:
        t0 = float(words[trigger_idx]["start"])
        for w in words[trigger_idx:]:
            if re.search(r"[.,;:?!…]$", str(w.get("word", "")).strip()):
                d = max(d, float(w["end"]) - t0)
                break
    return min(d, gfx_rules.callout_dur_max)


def resolve_plan(plan: dict[str, Any], *, ctx: dict[str, Any], words: list[dict], scenes: list[Any],
                 time_offset: float = 0.0, log: list[str] | None = None) -> dict[str, Any]:
    """Plan validado (índices) → plan RESUELTO para el templater. Aplica omisión por text_in_image,
    solapes y la advertencia de pattern interrupt (no inventa bloques)."""
    log = log if log is not None else []
    facts = ctx["facts"]
    dur = scenes[-1].end
    t_of = lambda wi: float(words[wi]["start"]) + time_offset  # noqa: E731

    from script_engine.gfx_project import scene_at
    out: dict[str, Any] = {"chapter_number": ctx["chapter_number"], "title_card": None, "callouts": [],
                           "count_up": None, "archive_clippings": [], "evidence_zoom": None, "punch_in": []}
    if (plan.get("title_card") or {}).get("use") and ctx["skeleton"].get("title") and max_per_cap("title_card") > 0:
        out["title_card"] = {"kicker": f"CAPÍTULO {ctx['chapter_number']}", "title": ctx["skeleton"]["title"]}

    busy: list[tuple[float, float]] = [(0.0, gfx_rules.title_dur)] if out["title_card"] else []

    def _free(a: float, b: float) -> bool:
        return all(b <= s or a >= e for s, e in busy)

    # F2 §0b: el count_up (rampa) tiene prioridad sobre un callout de la misma cifra
    cu = plan.get("count_up")
    if cu:
        t = t_of(cu["trigger_word_idx"])
        a, b = t, t + gfx_rules.count_dur + gfx_rules.count_hold_sec
        if b <= dur and _free(a, b):
            busy.append((a, b))
            out["count_up"] = {"value_text": cu["value"], "unit": cu["unit"], "start": round(t, 3)}
        else:
            log.append(f"count_up omitido (solape @ {t:.1f}s)")

    for c in sorted(plan.get("callouts", []), key=lambda c: c["trigger_word_idx"]):
        t = t_of(c["trigger_word_idx"])
        sc = scene_at(scenes, t)
        if _shown_in_image(c["text"], sc.text_in_image):
            log.append(f"callout omitido (ya en text_in_image escena {sc.idx}): {c['text']!r}")
            continue
        cdur = callout_duration(c["text"], c["trigger_word_idx"], words, time_offset)
        a, b = t, t + cdur
        if b > dur or not _free(a, b):
            log.append(f"callout omitido (solape/fuera de rango @ {t:.1f}s): {c['text']!r}")
            continue
        busy.append((a, b))
        # F2 §0b.7: lado opuesto al sujeto (quiet_side) y nunca dos seguidos en la misma esquina
        side = getattr(sc, "quiet_side", "left")
        if out["callouts"] and out["callouts"][-1]["side"] == side:
            side = "left" if side == "right" else "right"
        out["callouts"].append({"text": c["text"], "start": round(t, 3), "kind": c["kind"],
                                "duration": round(cdur, 3), "side": side})

    arcs = plan.get("archive_clippings")
    if arcs is None:                       # compat plan validado F1
        arcs = [plan["archive_clipping"]] if plan.get("archive_clipping") else []
    for ar in arcs:
        sc = scenes[ar["scene_idx"]]
        a = sc.start + 0.5
        b = min(a + gfx_rules.archive_dur, dur - 0.3)          # F2 §0b.6: 6 s en pantalla
        if b - a < gfx_rules.archive_min_sec:
            log.append(f"archive omitido (no entran {gfx_rules.archive_min_sec}s antes del fin del cap)")
        elif _free(a, b):
            busy.append((a, b))
            fact = facts[ar["fact_idx"]]
            head, body = headline_vs_body(ar["headline"], archive_body(ar["headline"], fact), ar["kicker"], fact, log)
            out["archive_clippings"].append({
                "kicker": ar["kicker"], "headline": head, "body": body, "scene_idx": ar["scene_idx"],
                "era_decade": _era_decade(fact), "start": round(a, 3), "duration": round(b - a, 3),
                "side": getattr(sc, "quiet_side", "right")})       # lado opuesto al sujeto
        else:
            log.append("archive omitido (solape con otro bloque)")

    ez = plan.get("evidence_zoom")
    if ez:
        sc = scenes[ez["scene_idx"]]
        # F2 §0b.5: el zoom ocupa el FINAL de su escena (acerca, sostiene ≥ 1 s y corta). Nunca vuelve.
        a = sc.end - gfx_rules.zoom_dur
        if a < sc.start + 0.2:
            log.append(f"zoom omitido (escena {ez['scene_idx']} demasiado corta para acercar + sostener)")
        elif _free(a, sc.end):
            busy.append((a, sc.end))
            out["evidence_zoom"] = {"scene_idx": ez["scene_idx"], "box": ez["box"], "start": round(a, 3)}
        else:
            log.append("zoom omitido (el final de su escena choca con otro bloque)")

    out["punch_in"] = [round(t_of(wi), 3) for wi in plan.get("punch_in_word_idx", [])]

    # F2 §1: hueco > interrupt_max_sec → el VALIDADOR rellena (callout con fact elegible dicho en el
    # tramo; si no hay, punch_in en la palabra de más énfasis). gap_warning queda como MÉTRICA.
    fill_gaps(out, busy, ctx=ctx, words=words, scenes=scenes, time_offset=time_offset, log=log)
    gaps = find_gaps(out, busy, dur)
    for g in gaps:
        log.append(f"gap_warning: {g[1] - g[0]:.1f}s sin bloque ({g[0]:.1f}–{g[1]:.1f}s)")
    out["gap_warnings"] = [[round(a, 1), round(b, 1)] for a, b in gaps]
    return out


# ═══════════════════════════════════════════════════════════════
#  F2 §1: titular ≠ cuerpo, huecos (determinista)
# ═══════════════════════════════════════════════════════════════

def headline_vs_body(head: str, body: str, kicker: str, fact: str, log: list[str]) -> tuple[str, str]:
    """Prohibido que el titular sea substring del cuerpo o viceversa. Si pasa: titular = kicker + año
    (solo si esa forma es LITERAL del fact, si no el candado lo mataría); si no, se quita el cuerpo."""
    if not body or not (normalize(head) in normalize(body) or normalize(body) in normalize(head)):
        return head, body
    y = fact_year(fact)
    cand = f"{kicker} {y}".strip() if kicker and y else ""
    if cand and _literal_in(cand, fact):
        log.append(f"archive: titular ⊂ cuerpo → titular = kicker + año {cand!r}")
        return cand, body
    log.append("archive: titular ⊂ cuerpo → sin cuerpo (kicker + año no es literal del fact)")
    return head, ""


def find_gaps(out: dict[str, Any], busy: list[tuple[float, float]], dur: float) -> list[tuple[float, float]]:
    """Tramos > interrupt_max_sec sin ningún bloque visible (inicios de bloques + punch_in)."""
    marks = sorted({0.0, dur, *[s for s, _ in busy], *out.get("punch_in", [])})
    return [(marks[i], marks[i + 1]) for i in range(len(marks) - 1)
            if marks[i + 1] - marks[i] > gfx_rules.interrupt_max_sec]


def _norm_tok(w: str) -> str:
    return re.sub(r"[^\wáéíóúñü.,%]", "", str(w).lower()).strip(".,")


def _fragments(fact: str) -> list[tuple[str, str]]:
    """Fragmentos literales cortos de un fact aptos para callout: (texto, kind)."""
    out: list[tuple[str, str]] = []
    for m in re.finditer(r"\b\d{1,2} de [a-záéíóú]+ de (?:1[5-9]|20)\d\d\b", fact):
        out.append((m.group(0), "year"))
    stop = {"y", "o", "de", "del", "el", "la", "los", "las", "en", "a", "al", "que", "por", "con", "un", "una"}
    for m in re.finditer(r"\b(\d+(?:[.,]\d+)*%?)(?: ([a-záéíóúñ]{3,}))?", fact):
        num, unit = m.group(1), m.group(2)
        if _YEAR_RE.fullmatch(num):
            out.append((num, "year"))
        elif unit and unit not in stop:
            out.append((f"{num} {unit}", "figure"))
        elif re.search(r"[.,]\d{3}|%", num):                 # cifra grande o porcentaje sin unidad
            out.append((num, "figure"))
    for m in re.finditer(r"(?<![.!?]\s)(?<!^)\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+(?:\s+(?:de\s+)?[A-ZÁÉÍÓÚÑ][\wáéíóúñ]*)*", fact):
        if len(m.group(0)) > 3:
            out.append((m.group(0), "place" if " de " in m.group(0) or m.group(0).split()[0] in ("Nueva", "Prisión") else "name"))
    seen, uniq = set(), []
    for t, k in out:
        if t not in seen and 1 <= len(t.split()) <= 6:
            seen.add(t)
            uniq.append((t, k))
    return uniq


def _find_spoken(fragment: str, words: list[dict], lo: int = 0) -> int | None:
    """Índice de la primera palabra (≥ lo) donde la voz dice el fragmento literal (tokens consecutivos)."""
    toks = [_norm_tok(t) for t in fragment.split()]
    ws = [_norm_tok(w.get("word", "")) for w in words]
    for i in range(lo, len(ws) - len(toks) + 1):
        if ws[i:i + len(toks)] == toks:
            return i
    return None


def fill_gaps(out: dict[str, Any], busy: list[tuple[float, float]], *, ctx: dict[str, Any], words: list[dict],
              scenes: list[Any], time_offset: float, log: list[str]) -> None:
    """Rellena huecos > interrupt_max_sec. Nunca escribe texto: solo fragmentos literales de facts elegibles."""
    from script_engine.gfx_project import scene_at
    if not words:
        return
    dur = scenes[-1].end
    facts, elig = ctx["facts"], ctx.get("eligible")
    used = {normalize(c["text"]) for c in out["callouts"]}
    for _ in range(12):                                    # tope de iteraciones (cada una tapa un hueco)
        gaps = find_gaps(out, busy, dur)
        if not gaps:
            return
        a, b = gaps[0]
        placed = False
        if len(out["callouts"]) < max_per_cap("data_callout"):
            best = None
            for fi in sorted(elig if elig is not None else range(len(facts))):
                for text, kind in _fragments(facts[fi]):
                    if normalize(text) in used:
                        continue
                    wi = _find_spoken(text, words)
                    while wi is not None:
                        t = float(words[wi]["start"]) + time_offset
                        cdur = callout_duration(text, wi, words, time_offset)
                        sc = scene_at(scenes, t)
                        if a + 1.0 < t < b - 1.0 and t + cdur <= dur and all(t + cdur <= s or t >= e for s, e in busy) \
                                and not _shown_in_image(text, sc.text_in_image):
                            if best is None or t < best[0]:
                                best = (t, text, kind, cdur, sc, fi)
                            break
                        wi = _find_spoken(text, words, wi + 1)
            if best:
                t, text, kind, cdur, sc, fi = best
                side = getattr(sc, "quiet_side", "left")
                prev = [c for c in out["callouts"] if c["start"] < t]
                if prev and prev[-1]["side"] == side:
                    side = "left" if side == "right" else "right"
                out["callouts"].append({"text": text, "start": round(t, 3), "kind": kind, "duration": round(cdur, 3),
                                        "side": side, "gap_fill": True})
                out["callouts"].sort(key=lambda c: c["start"])
                busy.append((t, t + cdur))
                used.add(normalize(text))
                log.append(f"gap_fill: callout {text!r} @ {t:.1f}s (fact {fi}) en hueco {a:.1f}–{b:.1f}s")
                placed = True
        if not placed:
            # punch_in en la palabra de más énfasis cerca del centro del hueco: cifra > nombre propio > palabra larga
            mid = (a + b) / 2
            best_w = None
            for i, w in enumerate(words):
                t = float(w["start"]) + time_offset
                if not (a + 3.0 < t < b - 3.0):
                    continue
                raw = str(w.get("word", "")).strip()
                score = (3 if re.search(r"\d", raw) else 2 if raw[:1].isupper() and i > 0 and
                         not re.search(r"[.!?]$", str(words[i - 1].get("word", ""))) else 1 if len(raw) >= 8 else 0)
                key = (score, -abs(t - mid))
                if best_w is None or key > best_w[0]:
                    best_w = (key, t, raw)
            if best_w is None:
                return
            out["punch_in"] = sorted([*out["punch_in"], round(best_w[1], 3)])
            log.append(f"gap_fill: punch_in en {best_w[2]!r} @ {best_w[1]:.1f}s (hueco {a:.1f}–{b:.1f}s sin fact dicho)")


# ═══════════════════════════════════════════════════════════════
#  F2 §1: box del zoom por visión (patrón zoom_judge: Flash vision, temp 0, schema, fail-safe)
# ═══════════════════════════════════════════════════════════════

_ZOOM_SYSTEM = """Mirás UN fotograma de un documental. Elegí el detalle visual más interesante y concreto para
acercar la cámara (un objeto, una marca, un texto, una textura reveladora), que NO sea un rostro humano.
Devolvé su caja normalizada [x, y, w, h] (0–1, origen arriba a la izquierda), de lado entre 0.06 y 0.25.
Si no hay ningún detalle que valga un acercamiento (imagen vacía, solo cielo, solo una cara), present=false."""

_ZOOM_SCHEMA: dict[str, Any] = {
    "type": "OBJECT",
    "properties": {"present": {"type": "BOOLEAN"}, "box": {"type": "ARRAY", "items": {"type": "NUMBER"}},
                   "detalle": {"type": "STRING"}},
    "required": ["present", "box", "detalle"],
}


def judge_zoom_box(image_path: Path) -> dict[str, Any]:
    """1 call Flash vision. {box: [x,y,w,h] | None, detalle}. Fail-safe: error → box None (sin zoom)."""
    try:
        from google.genai import types as genai_types
        from config import api, gemini_client
        resp = gemini_client.models.generate_content(
            model=api.gemini_model,
            contents=[genai_types.Part.from_bytes(data=image_path.read_bytes(), mime_type="image/jpeg"),
                      "Elegí el detalle para el acercamiento. Devolvé solo el JSON."],
            config=genai_types.GenerateContentConfig(system_instruction=_ZOOM_SYSTEM, temperature=0.0,
                                                     response_mime_type="application/json",
                                                     response_schema=_ZOOM_SCHEMA))
        cost_tracker.track_gemini_vision(description=f"gfx_zoom_box:{image_path.stem}", calls=1)
        data = json.loads(resp.text)
        box = clamp_box(data.get("box") or []) if data.get("present") else None
        return {"box": box, "detalle": str(data.get("detalle", ""))[:120]}
    except Exception as e:  # noqa: BLE001 — sin visión no hay zoom (conservador)
        error_handler.log_warning(PipelineStage.ASSEMBLY, f"[gfx_director] zoom box falló ({e}) → sin zoom")
        return {"box": None, "detalle": f"error: {e}"}


def apply_zoom_vision(plan: dict[str, Any], *, frame_for_scene: Any, cache: Path, log: list[str]) -> dict[str, Any]:
    """Reemplaza el box del LLM por el de visión (cacheado por escena). box None → sin zoom en el cap."""
    ez = plan.get("evidence_zoom")
    if not ez:
        return plan
    key = str(ez["scene_idx"])
    data: dict[str, Any] = {}
    if cache.exists():
        try:
            data = json.loads(cache.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            data = {}
    if key not in data:
        img = frame_for_scene(ez["scene_idx"])
        data[key] = judge_zoom_box(img) if img else {"box": None, "detalle": "sin frame"}
        cache.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    v = data[key]
    if v.get("box") is None:
        log.append(f"zoom omitido (visión: sin detalle en escena {key} — {v.get('detalle', '')})")
        return {**plan, "evidence_zoom": None}
    log.append(f"zoom box por visión escena {key}: {v['box']} ({v.get('detalle', '')})")
    return {**plan, "evidence_zoom": {**ez, "box": v["box"]}}


# ═══════════════════════════════════════════════════════════════
#  Entry point
# ═══════════════════════════════════════════════════════════════

DIRECTOR_VERSION = "v1"        # cambia el prompt → el cache crudo de una versión anterior se re-llama

def select_gfx_plan(chplan: Any, *, ctx: dict[str, Any], words: list[dict], scenes: list[Any],
                    work_dir: Path, log: list[str] | None = None) -> dict[str, Any]:
    """1 call Flash por cap → plan validado (índices).

    Cache en work_dir/gfx_plan_chXX.json = respuesta CRUDA del LLM (se re-valida en cada carga,
    así un cambio de reglas/clamps aplica sin re-llamar a Gemini). Guardar el plan ya validado
    rompía la ida y vuelta (sin `use`) → bloques perdidos al reusar (bug F1 ch06).
    """
    log = log if log is not None else []
    cache = work_dir / f"gfx_plan_{chplan.chapter_id}.json"
    kw = dict(n_facts=len(ctx["facts"]), n_words=len(words), scenes=scenes, facts=ctx["facts"], log=log,
              eligible=ctx.get("eligible"))
    raw: Any = None
    if cache.exists():
        try:
            cached = json.loads(cache.read_text(encoding="utf-8"))
            raw = cached.get("raw") if cached.get("director") == DIRECTOR_VERSION else None
        except (OSError, ValueError, AttributeError):
            raw = None
    if raw is None:
        try:
            raw = call_flash_json(_build_user_prompt(ctx, words, scenes), system_instruction=_SYSTEM_PROMPT,
                                  response_schema=_SCHEMA, description=f"gfx_director {chplan.chapter_id}")
        except Exception as e:  # noqa: BLE001 — Gemini caído → fallback estático (solo title_card)
            error_handler.log_warning(PipelineStage.ASSEMBLY, f"[gfx_director] {chplan.chapter_id} Gemini falló ({e}) → solo title_card")
            return validate_plan({"title_card": {"use": True}}, **kw)   # el fallback NO se cachea
        cache.write_text(json.dumps({"director": DIRECTOR_VERSION, "raw": raw}, ensure_ascii=False, indent=1),
                         encoding="utf-8")
    return validate_plan(raw, **kw)
