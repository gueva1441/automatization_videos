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
    active_moods,
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
    sk: dict[str, Any] = {}
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
    # F2 §0d: fuentes del research (para source_tag; entran al candado como texto literal)
    src_list = [str(x) for x in script.get("sources", []) or []]
    for j, src in enumerate(src_list):
        sources[f"sources[{j}]"] = src
    # F2 §0d: próximo cap (para chapter_question; NO entra al candado literal del cap)
    next_ch = next((c for c in script.get("chapters", []) if int(c.get("chapter_number", -1)) == n + 1), None)
    next_sources: dict[str, str] = {}
    if next_ch is not None:
        next_sources[f"narration_ch{n + 1:02d}"] = str(next_ch.get("narration", ""))
        nsk = next((c for c in sk.get("chapters", []) if c.get("chapter_number") == n + 1), {})
        for j, b in enumerate(nsk.get("bullets", []) or []):
            next_sources[f"next.bullets[{j}]"] = b
    # F2b §2: narración completa del video (rareza de las palabras de énfasis)
    narration_all = " ".join(str(c.get("narration", "")) for c in script.get("chapters", []))
    # F5 §2: el evidence_pool entra al candado (un recorte que dice lo que la voz NO dice es el caso deseado)
    pool = script.get("evidence_pool") or None
    if pool:
        from script_engine.gfx_pool import pool_sources, short_source
        sources.update(pool_sources(pool))
        for k, it in enumerate(pool.get("datos") or []):
            if it.get("fuente"):
                sources[f"pool.fuente_corta.{k}"] = short_source(it["fuente"])
    return {
        "video_id": video_id, "chapter_number": n, "script_chapter": chapter, "narration_all": narration_all,
        "facts": facts, "skeleton": skeleton_ch, "canonical": canonical, "sources": sources,
        "eligible": eligible, "era_window": era,
        "fact_source": fact_sources(facts, src_list), "next_sources": next_sources,
        "chapters": script.get("chapters", []),           # F3: pregunta de cierre (cap actual + siguiente)
        "pool": pool, "skeleton_all": sk if pool else {},   # F5 §2 (None/{} sin pool: todo igual que antes)
    }


def fact_sources(facts: list[str], src_list: list[str]) -> dict[int, str]:
    """{fact_idx: 'Organización, año'} cuando el fact NOMBRA la organización de una fuente.
    La etiqueta es un prefijo literal de la fuente (pasa el candado). Sin match → sin etiqueta."""
    out: dict[int, str] = {}
    for i, f in enumerate(facts):
        for src in src_list:
            org = src.split(",")[0].strip()
            m = _YEAR_RE.search(src)
            if len(org) >= 4 and normalize(org) in normalize(f) and m:
                tag = src[: m.end()]
                if tag.count(",") == 1:                    # "Org, año" exacto (sin autores con comas)
                    out[i] = tag
                    break
    return out


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

# F2b §1.3: chapter_question apagado en el perfil → la regla ni aparece en el prompt (el código queda)
_QUESTION_RULE = ("- chapter_question: si hay PRÓXIMO CAPÍTULO, elegí UNA de sus bullets y reformulala como pregunta corta\n"
                  "  (≤ 9 palabras, entre ¿ ?) usando SOLO palabras que ya están en esas bullets. Si no se puede, use=false.\n"
                  if max_per_cap("chapter_question") > 0 else "- chapter_question: APAGADO para este canal (use=false).\n")

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
- archive_clippings: lista de 0–{max_per_cap("archive_clipping")}, cada uno en una escena distinta de ≥ 4 s. Elegís SOLO fact_idx y
  scene_idx: el titular y el kicker los arma el sistema con palabras del fact (no los escribas).
- evidence_zoom: máx {max_per_cap("evidence_zoom")}, en una escena de ≥ 3.1 s (el zoom ocupa el FINAL de esa escena), sobre un detalle
  concreto QUE LA VOZ NOMBRA en esa escena (ej. "la herida en la mano"). anchor_word_idx = índice de WORDS donde
  empieza esa frase; anchor_len = cuántas palabras (1–6). Si la voz no nombra ningún detalle visible, use=false.
- punch_in_word_idx: máx {max_per_cap("punch_in")}, palabras de énfasis (idealmente las de los callouts).
- Pattern interrupt: intentá que haya un bloque visible cada {gfx_rules.interrupt_min_sec:.0f}–{gfx_rules.interrupt_max_sec:.0f} s, pero SOLO con datos reales.
- Un bloque con máx 0 está APAGADO para este canal: no lo uses.
- title_card.use = true siempre.
{_QUESTION_RULE}- Si un bloque no aplica: use=false (o lista vacía).
"""


def system_prompt() -> str:
    """Prompt del director + (F4 §2.1) el plan dorado de la identidad como ejemplo de ritmo y densidad."""
    if not gfx_rules.identity_rules:
        return _SYSTEM_PROMPT
    from script_engine.gfx_style import golden_fewshot
    shot = golden_fewshot()
    return _SYSTEM_PROMPT + ("\n" + shot + "\nLas FORMAS (animaciones, tamaños, transiciones, movimiento de foto) las pone el "
                             "sistema: vos elegís solo DÓNDE y QUÉ dato.\n" if shot else "")



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
            "fact_idx": {"type": "INTEGER"}, "scene_idx": {"type": "INTEGER"}},
            "required": ["fact_idx", "scene_idx"]}},
        "evidence_zoom": {"type": "OBJECT", "properties": {
            "use": {"type": "BOOLEAN"}, "scene_idx": {"type": "INTEGER"},
            "anchor_word_idx": {"type": "INTEGER"}, "anchor_len": {"type": "INTEGER"}},
            "required": ["use", "scene_idx", "anchor_word_idx", "anchor_len"]},
        "count_up": {"type": "OBJECT", "properties": {
            "use": {"type": "BOOLEAN"}, "fact_idx": {"type": "INTEGER"}, "value": {"type": "STRING"},
            "unit": {"type": "STRING"}, "trigger_word_idx": {"type": "INTEGER"}},
            "required": ["use", "fact_idx", "value", "unit", "trigger_word_idx"]},
        "punch_in_word_idx": {"type": "ARRAY", "items": {"type": "INTEGER"}},
        "chapter_question": {"type": "OBJECT", "properties": {"use": {"type": "BOOLEAN"}, "text": {"type": "STRING"}},
                             "required": ["use", "text"]},
    },
    "required": ["title_card", "callouts", "archive_clippings", "evidence_zoom", "count_up", "punch_in_word_idx",
                 "chapter_question"],
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
    nb = [v for k, v in (ctx.get("next_sources") or {}).items() if k.startswith("next.bullets")]
    lines += ["", f"PRÓXIMO CAPÍTULO — bullets: {' | '.join(nb)}" if nb else "PRÓXIMO CAPÍTULO: no hay (último cap)"]
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


# ── F2b §1.1: titular determinista (pasa el candado por construcción) ──
_MONTHS = r"(?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|septiembre|setiembre|octubre|noviembre|diciembre)"
_HEAD_EDGE_STOP = {"de", "del", "la", "las", "el", "los", "un", "una", "unos", "unas", "y", "o", "e", "en", "a", "al",
                   "que", "por", "con", "para", "sin", "se", "su", "sus", "lo", "como", "según", "hasta", "durante",
                   # auxiliares sueltos al final ("informaron haber" → "informaron")
                   "haber", "había", "habían", "ser", "sido", "estar", "fue", "fueron", "era", "eran"}


def _is_figure(tok: str, nxt: str) -> bool:
    """Cifra = número de ≥ 2 dígitos (o con decimales/%) que NO es año ni día de una fecha ('29 de agosto')."""
    core = tok.strip("()'\".,;:")
    if not re.fullmatch(r"\d[\d.,]*%?", core) or _YEAR_RE.fullmatch(core):
        return False
    if not (len(re.sub(r"\D", "", core)) >= 2 or re.search(r"[.,]\d|%", core)):
        return False
    return not (nxt == "de" and len(core) <= 2)               # día de fecha: "29 de agosto"


def build_headline(fact: str, max_words: int | None = None) -> str:
    """Titular del recorte = fragmento LITERAL del fact (≤ max_words palabras).

    Cláusulas = cortes en , . ; : seguidos de espacio. Si alguna cláusula tiene cifra, se usa la primera con
    cifra y la ventana de palabras incluye la cifra y la palabra que la sigue (unidad); si no, la primera
    cláusula. Se quitan palabras funcionales y paréntesis desbalanceados de los bordes. "" si no queda nada.
    """
    max_words = max_words or gfx_rules.archive_head_max_words
    text = re.sub(r"\s+", " ", fact).strip()
    clauses = [c.strip() for c in re.split(r"[,.;:](?=\s|$)", text) if c.strip()]
    if not clauses:
        return ""
    target, fig_i = clauses[0], None
    for c in clauses:
        ws = c.split()
        idx = next((i for i, w in enumerate(ws) if _is_figure(w, ws[i + 1].lower() if i + 1 < len(ws) else "")), None)
        if idx is not None:
            target, fig_i = c, idx
            break
    ws = target.split()
    start = 0 if fig_i is None else max(0, min(fig_i + 2 - max_words, len(ws) - max_words))
    full = ws
    ws = ws[start:start + max_words]
    # una fecha ("29 de agosto de 2005") no se parte: si la ventana corta dentro de una, se corta antes
    end = start + len(ws)
    for m in re.finditer(rf"\b\d{{1,2}} de {_MONTHS}(?: de \d{{4}})?", target, re.IGNORECASE):
        d0 = len(target[:m.start()].split())
        d1 = d0 + len(m.group(0).split())
        if d0 < end < d1 and d0 > start:
            ws = full[start:d0]

    def _edge_bad(w: str) -> bool:
        return w.lower().strip("'\"") in _HEAD_EDGE_STOP or w.count("(") != w.count(")")
    # paréntesis desbalanceados en la ventana: cortar antes del "(" abierto
    opened = next((i for i, w in enumerate(ws) if "(" in w and not any(")" in v for v in ws[i:])), None)
    if opened is not None and opened > 0:
        ws = ws[:opened]
    while ws and _edge_bad(ws[-1]):
        ws.pop()
    head = " ".join(ws)
    return head if head and _literal_in(head, fact) else ""


def build_kicker(fact: str, source: str, headline: str) -> str:
    """Kicker = fuente del fact ('Organización, año') o, si no hay, el año del fact (si no está ya en el titular)."""
    if source:
        return source                                          # prefijo literal de sources[] (pasa el candado)
    y = fact_year(fact)
    return str(y) if y and str(y) not in headline else ""


def zoom_anchor(z: dict[str, Any], words: list[dict], scene: Any, time_offset: float = 0.0) -> str:
    """F2b §1.2: frase ancla del zoom = palabras LITERALES de la voz [anchor_word_idx, +anchor_len), 1–6 palabras,
    dichas dentro de la escena del zoom (± 1 s). "" si no hay ancla válida."""
    try:
        i, n = int(z.get("anchor_word_idx")), int(z.get("anchor_len") or 0)
    except (TypeError, ValueError):
        return ""
    if scene is None or not words or not (0 <= i < len(words)) or not (1 <= n <= 6) or i + n > len(words):
        return ""
    t = float(words[i]["start"]) + time_offset
    if not (scene.start - 1.0 <= t <= scene.end + 0.5):
        return ""
    phrase = " ".join(str(w.get("word", "")).strip() for w in words[i:i + n])
    return re.sub(r"[.,;:!?…]+$", "", phrase).strip()


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
                  eligible: dict[int, bool] | None = None, words: list[dict] | None = None,
                  time_offset: float = 0.0, fact_source: dict[int, str] | None = None) -> dict[str, Any]:
    """Valida y repara el plan crudo del LLM. Descarta lo inválido; nunca lanza.

    eligible: {fact_idx: foráneo} del cap (F2 §1). None = todos elegibles (compat).
    Un fact no elegible se descarta; uno foráneo solo vale para data_callout.
    F2b §1.1: el titular/kicker del recorte los arma el validador (lo que mande el LLM se ignora).
    F2b §1.2: el zoom necesita una frase ancla de la voz (words) dicha dentro de su escena; sin ancla → sin zoom.
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
        head = build_headline(facts[fi]) if fi is not None else ""
        kick = build_kicker(facts[fi], (fact_source or {}).get(fi, ""), head) if fi is not None else ""
        if fi is not None and not head:
            log.append(f"archive descartado (fact {fi} sin titular armable)")
        elif fi is None or si is None:
            log.append(f"archive descartado (índice): {a}")
        elif scenes[si].duration < gfx_rules.archive_min_scene:
            log.append(f"archive descartado (escena {si} dura {scenes[si].duration:.1f}s)")
        elif not _literal_in(head, facts[fi]) or (kick and not _literal_in(kick, facts[fi])
                                                    and kick != (fact_source or {}).get(fi)):   # F2b: kicker = fuente
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
        si = _idx(z.get("scene_idx"), n_scenes)
        anchor = zoom_anchor(z, words or [], scenes[si] if si is not None else None, time_offset)
        if si is None:
            log.append(f"zoom descartado (índice): {z}")
        elif scenes[si].duration < gfx_rules.zoom_min_scene:
            log.append(f"zoom descartado (escena {si} dura {scenes[si].duration:.1f}s)")
        elif not anchor:
            log.append(f"zoom descartado (sin frase ancla de la voz dentro de la escena {si}): {z}")
        else:
            # el box lo pone visión (apply_zoom_vision) buscando ESA frase; sin box de visión no hay zoom
            plan["evidence_zoom"] = {"scene_idx": si, "anchor": anchor, "box": None}

    cu = raw.get("count_up") or {}
    if isinstance(cu, dict) and cu.get("use") and max_per_cap("count_up") > 0:
        fi, wi = _fact(cu.get("fact_idx"), "count_up"), _idx(cu.get("trigger_word_idx"), n_words)
        val, unit = str(cu.get("value", "")).strip(), str(cu.get("unit", "")).strip()
        if fi is None or wi is None or not re.fullmatch(r"[\d.,]+%?", val) or not _literal_in(val, facts[fi]):
            log.append(f"count_up descartado: {cu}")
        elif re.fullmatch(r"(?i)pies?|millas?|yardas?|pulgadas?|libras?|galones?|°?f", unit):
            log.append(f"count_up descartado (en pantalla, unidades métricas — F5b S5): {cu}")
        elif not is_count_quantity(val, unit, facts[fi]):
            log.append(f"count_up descartado (solo cantidades: personas, dinero, metros; nunca edades ni fechas — "
                       f"F5d): {cu}")
        else:
            plan["count_up"] = {"fact_idx": fi, "value": val, "unit": unit if _literal_in(unit, facts[fi]) else "",
                                "trigger_word_idx": wi}

    pw = [i for i in (_idx(v, n_words) for v in (raw.get("punch_in_word_idx") or [])) if i is not None]
    plan["punch_in_word_idx"] = sorted(set(pw))[: max_per_cap("punch_in")]

    q = raw.get("chapter_question") or {}
    if isinstance(q, dict) and q.get("use") and max_per_cap("chapter_question") > 0:
        text = re.sub(r"\s+", " ", str(q.get("text", ""))).strip()
        if not text or len(text.split()) > gfx_rules.question_max_words:
            log.append(f"chapter_question descartada (vacía o > {gfx_rules.question_max_words} palabras): {text!r}")
        else:
            if not text.endswith("?"):
                text = text.rstrip(".") + "?"
            if not text.startswith("¿"):
                text = "¿" + text
            plan["chapter_question"] = {"text": text}
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

    # F2 §0d: chapter_question ocupa el CIERRE del cap (se reserva antes que el resto)
    out["chapter_question"] = None
    cq = plan.get("chapter_question")
    if cq:
        qa = dur - gfx_rules.question_dur - 0.15
        if qa > gfx_rules.title_dur + 1.0 and _free(qa, dur):
            busy.append((qa, dur))
            out["chapter_question"] = {"text": cq["text"], "start": round(qa, 3),
                                       "duration": round(gfx_rules.question_dur, 3),
                                       "keyword": question_keyword(cq["text"])}
        else:
            log.append("chapter_question omitida (cap demasiado corto)")

    # F2 §0b: el count_up (rampa) tiene prioridad sobre un callout de la misma cifra
    cu = plan.get("count_up")
    counted = ctx.get("video_counted") or set()
    second_cifra: tuple[int, float] | None = None        # (fact, t) de una cifra que ya se animó en otro cap
    if cu and figure_digits(cu["value"]) in counted:
        second_cifra = (cu["fact_idx"], t_of(cu["trigger_word_idx"]))
        log.append(f"count_up omitido (la cifra {cu['value']} ya se animó en un cap anterior → recorte o nada)")
        cu = None
    if cu:
        t = t_of(cu["trigger_word_idx"])
        a, b = t, t + gfx_rules.count_dur + gfx_rules.count_hold_sec
        if b <= dur and _free(a, b):
            busy.append((a, b))
            out["count_up"] = {"value_text": cu["value"], "unit": cu["unit"], "start": round(t, 3),
                               "fact_idx": cu["fact_idx"],
                               "source": (ctx.get("fact_source") or {}).get(cu["fact_idx"], "")}
        else:
            log.append(f"count_up omitido (solape @ {t:.1f}s)")

    # Pre-merge (Omar): (1) recorte de un fact con fuente + año tiene prioridad sobre los callouts; (2) UN FACT =
    # UN BLOQUE: si el recorte comparte fact o cifra con el contador, gana el contador y el recorte pasa al
    # siguiente fact elegible (si no hay, sin recorte); (3) si el cap queda sin recortes con facts elegibles, se
    # convierte el mejor callout. El "cambio de lado por el contador" se QUITÓ: un solape descarta el recorte.
    fsrc = ctx.get("fact_source") or {}
    cu_out = out.get("count_up")
    cu_fi = cu_out.get("fact_idx") if cu_out else None
    cu_digits = figure_digits(cu_out["value_text"]) if cu_out else ""
    elig = ctx.get("eligible")

    def _shares_counter(fi: int) -> bool:
        return cu_out is not None and (fi == cu_fi or cu_digits in headline_digits(build_headline(facts[fi])))

    def _next_fact(fi: int) -> int | None:
        """Siguiente fact elegible (propio del cap, en orden de índice desde fi) con titular, sin compartir
        fact/cifra con el contador y que no esté ya en otro recorte."""
        pool = sorted(i for i in (elig if elig is not None else range(len(facts))) if not (elig and elig.get(i)))
        used = {x["fact_idx"] for x in out["archive_clippings"]}
        for i in pool[pool.index(fi) + 1:] + pool[:pool.index(fi)] if fi in pool else pool:
            if i not in used and build_headline(facts[i]) and not _shares_counter(i):
                return i
        return None

    def _place_archive(fi: int, si: int, kicker: str, a: float | None = None, why: str = "") -> bool:
        if _shares_counter(fi):
            alt = _next_fact(fi)
            log.append(f"archive: fact {fi} comparte fact/cifra con el contador (un fact = un bloque) → "
                       + (f"siguiente fact elegible {alt}" if alt is not None else "sin recorte (no hay otro fact elegible)"))
            if alt is None:
                return False
            fi = alt
            kicker = build_kicker(facts[fi], fsrc.get(fi, ""), build_headline(facts[fi]))
        if any(x["fact_idx"] == fi for x in out["archive_clippings"]):
            log.append(f"archive omitido (fact {fi} ya tiene recorte en este cap)")
            return False
        sc = scenes[si]
        a = sc.start + 0.5 if a is None else a
        b = min(a + gfx_rules.archive_dur, dur - 0.3)          # F2 §0b.6: 6 s en pantalla
        if out.get("chapter_question"):                        # no pisa la pregunta de cierre
            b = min(b, out["chapter_question"]["start"] - 0.2)
        if b - a < gfx_rules.archive_min_sec:
            log.append(f"archive omitido (no entran {gfx_rules.archive_min_sec}s antes del fin del cap)")
            return False
        side = getattr(sc, "quiet_side", "right")              # lado opuesto al sujeto
        if not _free(a, b):
            log.append(f"archive omitido (solape con otro bloque){why}")
            return False
        busy.append((a, b))
        fact = facts[fi]
        head = build_headline(fact)
        head, body = headline_vs_body(head, archive_body(head, fact), kicker, fact, log)
        out["archive_clippings"].append({
            "kicker": kicker, "headline": head, "body": body, "scene_idx": si, "fact_idx": fi,
            "era_decade": _era_decade(fact), "start": round(a, 3), "duration": round(b - a, 3), "side": side})
        return True

    arcs = plan.get("archive_clippings")
    if arcs is None:                       # compat plan validado F1
        arcs = [plan["archive_clipping"]] if plan.get("archive_clipping") else []
    for ar in arcs:                        # (1) primero los de fuente + año
        if ar["fact_idx"] in fsrc:
            _place_archive(ar["fact_idx"], ar["scene_idx"], ar["kicker"], why=" [con fuente]")

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
                                "duration": round(cdur, 3), "side": side, "fact_idx": c["fact_idx"],
                                "source": fsrc.get(c["fact_idx"], "")})

    for ar in arcs:                        # después, el resto
        if ar["fact_idx"] not in fsrc:
            _place_archive(ar["fact_idx"], ar["scene_idx"], ar["kicker"])

    if second_cifra and len(out["archive_clippings"]) < gfx_rules.archive_max_per_cap:
        fi, t = second_cifra
        if _place_archive(fi, scene_at(scenes, t).idx, build_kicker(facts[fi], fsrc.get(fi, ""), build_headline(facts[fi])),
                          a=t, why=" [cifra ya animada: recorte o nada]"):
            log.append(f"archive: la cifra ya animada va como recorte (fact {fi})")

    ez = plan.get("evidence_zoom")
    if ez:
        sc = scenes[ez["scene_idx"]]
        # F2 §0b.5: el zoom ocupa el FINAL de su escena (acerca, sostiene ≥ 1 s y corta). Nunca vuelve.
        a = sc.end - gfx_rules.zoom_dur
        if a < sc.start + 0.2:
            log.append(f"zoom omitido (escena {ez['scene_idx']} demasiado corta para acercar + sostener)")
        elif _free(a, sc.end):
            busy.append((a, sc.end))
            out["evidence_zoom"] = {"scene_idx": ez["scene_idx"], "box": ez["box"], "start": round(a, 3),
                                  "anchor": ez.get("anchor", "")}
        else:
            log.append("zoom omitido (el final de su escena choca con otro bloque)")

    out["punch_in"] = [round(t_of(wi), 3) for wi in plan.get("punch_in_word_idx", [])]

    # F2b §3: icon_array (cifra afectados/total ≤ 500 de un fact, cuando la voz la dice)
    out["icon_array"] = None
    if max_per_cap("icon_array") > 0 and words:
        out["icon_array"] = place_icon_array(busy, ctx=ctx, words=words, scenes=scenes, time_offset=time_offset, log=log)

    # F2b §2: keyword_emphasis (regex sobre la narración, sin LLM): las palabras de carga más raras del cap
    out["emphasis"] = []
    if max_per_cap("keyword_emphasis") > 0 and active_moods() and words:
        n0 = min(gfx_rules.emphasis_base_per_cap, max_per_cap("keyword_emphasis"))
        place_emphasis(out, busy, words=words, scenes=scenes, ctx=ctx, time_offset=time_offset, limit=n0, log=log)

    # F2 §1: hueco > interrupt_max_sec → el VALIDADOR rellena (callout con fact elegible dicho en el
    # tramo; si no hay, punch_in en la palabra de más énfasis). gap_warning queda como MÉTRICA.
    fill_gaps(out, busy, ctx=ctx, words=words, scenes=scenes, time_offset=time_offset, log=log)
    if not out["archive_clippings"] and gfx_rules.archive_max_per_cap > 0:
        convert_callout_to_archive(out, busy, _place_archive, ctx=ctx, scenes=scenes, log=log, skip=_shares_counter)
    mark_icon_callouts(out, log)                             # F2b §3: hasta 3 énfasis llevan su ícono
    gaps = find_gaps(out, busy, dur)
    for g in gaps:
        log.append(f"gap_warning: {g[1] - g[0]:.1f}s sin bloque ({g[0]:.1f}–{g[1]:.1f}s)")
    out["gap_warnings"] = [[round(a, 1), round(b, 1)] for a, b in gaps]
    return out


# ═══════════════════════════════════════════════════════════════
#  F2 §1: titular ≠ cuerpo, huecos (determinista)
# ═══════════════════════════════════════════════════════════════

_STOP = {"de", "del", "la", "las", "el", "los", "un", "una", "unos", "unas", "y", "o", "en", "a", "al", "que", "qué",
         "por", "con", "para", "sin", "se", "su", "sus", "lo", "le", "les", "es", "fue", "era", "cómo", "como", "cuál",
         "cuáles", "cuánto", "cuántos", "cuántas", "quién", "quiénes", "dónde", "cuándo", "por qué", "más", "muy", "no"}


def content_words(text: str) -> list[str]:
    """Palabras de contenido (≥ 4 letras, no funcionales) normalizadas."""
    return [w for w in re.findall(r"[a-záéíóúñü0-9]+", normalize(text)) if len(w) >= 4 and w not in _STOP]


def question_ok(text: str, next_sources: dict[str, str]) -> bool:
    """Candado de chapter_question: TODA palabra de contenido existe en bullets/narración del próximo cap
    (acepta singular/plural simple). La pregunta es reformulación, no literal: este es su candado."""
    pool = set(re.findall(r"[a-záéíóúñü0-9]+", normalize(" ".join(next_sources.values()))))
    def _in(w: str) -> bool:
        return any(v in pool for v in (w, w + "s", w + "es", w[:-1] if w.endswith("s") else w,
                                       w[:-2] if w.endswith("es") else w))
    words = content_words(text)
    return bool(words) and all(_in(w) for w in words)


def question_keyword(text: str) -> str:
    """Palabra clave a acentuar: la palabra de contenido más larga."""
    words = re.findall(r"[\wáéíóúñü]+", text)
    cands = [w for w in words if len(w) >= 4 and normalize(w) not in _STOP]
    return max(cands, key=len) if cands else ""


def sfx_events(out: dict[str, Any], words: list[dict], time_offset: float, sfx_for: Any,
               log: list[str] | None = None) -> list[dict[str, Any]]:
    """SFX del cap: (t, archivo, gain) por bloque visible según el perfil. Nunca sobre el ataque de una palabra:
    se corre ≤ sfx_shift_max_ms al hueco entre palabras más cercano; si no hay hueco y cae sobre una palabra
    acentuada (cifra, nombre propio o ≥ 7 letras), el SFX se descarta (menos frecuencia)."""
    marks: list[tuple[float, str]] = []
    if out.get("title_card"):
        marks.append((0.05, "title_card"))
    marks += [(c["start"], "data_callout") for c in out.get("callouts", [])]
    if out.get("count_up"):
        marks.append((out["count_up"]["start"], "count_up"))
    marks += [(a["start"], "archive_clipping") for a in out.get("archive_clippings", [])]
    ez = out.get("evidence_zoom")
    if ez and "start" in ez:
        marks.append((ez["start"] + gfx_rules.zoom_rect_sec, "evidence_zoom"))
    if out.get("chapter_question"):
        marks.append((out["chapter_question"]["start"], "chapter_question"))
    marks += [(e["start"], "keyword_emphasis") for e in out.get("emphasis", []) or []]     # F2b §2: tic sordo
    if out.get("icon_array"):
        marks.append((out["icon_array"]["start"], "icon_array"))
    if ez and ez.get("latido_t") is not None:                  # F3: latido del zoom de evidencia (lub-dub)
        marks.append((float(ez["latido_t"]), "latido"))
    spans = [(float(w["start"]) + time_offset, float(w["end"]) + time_offset, str(w.get("word", ""))) for w in words]
    gaps = [(spans[i][1], spans[i + 1][0]) for i in range(len(spans) - 1) if spans[i + 1][0] > spans[i][1]]
    win = gfx_rules.sfx_shift_max_ms / 1000.0
    ev: list[dict[str, Any]] = []
    from gfx_config import SFX_DIR
    own = {round(float(e["start"]), 3): e["sfx"] for e in out.get("emphasis", []) or [] if e.get("sfx")}
    for t, block in sorted(marks):
        sf = (SFX_DIR / "latido.wav", -16.0) if block == "latido" else sfx_for(block)
        if block == "keyword_emphasis" and round(float(t), 3) in own:      # F4c R5: SFX propio de la categoría
            o = own[round(float(t), 3)]
            sf = (SFX_DIR / o["file"], float(o.get("gain_db", -20)))
        if sf is None:
            continue
        on = next((sp for sp in spans if sp[0] - 0.03 <= t < sp[1]), None)
        tt = t
        if on is not None:                                   # cae sobre una palabra → buscar hueco cercano
            # punto del hueco más cercano, sin tocar el ataque de la palabra siguiente (30 ms de margen)
            near = [x for x in (min(max(t, g0), max(g0, g1 - 0.03)) for g0, g1 in gaps) if abs(x - t) <= win]
            if near:
                tt = min(near, key=lambda x: abs(x - t))
            elif re.search(r"\d", on[2]) or len(on[2].strip(".,;:!?¿¡")) >= 7 or on[2][:1].isupper():
                if log is not None:                          # palabra acentuada sin hueco: sin SFX
                    log.append(f"sfx descartado: {block} @ {t:.2f}s cae sobre {on[2]!r} sin hueco ≤ {gfx_rules.sfx_shift_max_ms} ms")
                continue
        ev.append({"t": round(max(0.0, tt), 3), "file": str(sf[0]), "gain_db": sf[1], "block": block,
                   "shift_ms": round((tt - t) * 1000)})
    return ev


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


# ═══════════════════════════════════════════════════════════════
#  F2b §2: léxico de moods + énfasis de palabra (determinista, sin LLM)
# ═══════════════════════════════════════════════════════════════

def _tok(w: Any) -> str:
    return re.sub(r"[^\wáéíóúñü]", "", str(w).lower())


def word_freq(text: str) -> dict[str, int]:
    """Frecuencia de cada palabra en la narración completa (rareza = menor frecuencia)."""
    freq: dict[str, int] = {}
    for w in str(text).split():
        t = _tok(w)
        if t:
            freq[t] = freq.get(t, 0) + 1
    return freq


def emphasis_candidates(words: list[dict], moods: dict[str, dict[str, Any]]) -> list[tuple[int, int, str, int, str]]:
    """(índice, cantidad de palabras, categoría, peso 1–3, disparador) por cada palabra del léxico dicha por la voz.
    Match exacto de tokens (las flexiones están listadas en el léxico); frases ("sin luz") antes que palabras."""
    toks = [_tok(w.get("word", "")) for w in words]
    trig = sorted(((cat, tuple(_tok(x) for x in t.split()), int(wt), t) for cat, m in moods.items()
                   for t, wt in (m.get("triggers") or {}).items()), key=lambda ct: -len(ct[1]))
    out: list[tuple[int, int, str, int, str]] = []
    i = 0
    while i < len(toks):
        hit = next(((cat, tt, wt, t) for cat, tt, wt, t in trig if tt and tuple(toks[i:i + len(tt)]) == tt), None)
        if hit:
            out.append((i, len(hit[1]), hit[0], hit[2], hit[3]))
            i += len(hit[1])
        else:
            i += 1
    return out


def _sentence_ids(words: list[dict]) -> list[int]:
    """Id de frase por palabra (una frase termina en . ! ? …)."""
    sid, out = 0, []
    for w in words:
        out.append(sid)
        if re.search(r"[.!?…]['\"»”)]*$", str(w.get("word", "")).strip()):
            sid += 1
    return out


def place_emphasis(out: dict[str, Any], busy: list[tuple[float, float]], *, words: list[dict], scenes: list[Any],
                   ctx: dict[str, Any], time_offset: float, limit: int, window: tuple[float, float] | None = None,
                   log: list[str] | None = None) -> int:
    """Agrega hasta `limit` énfasis a out["emphasis"] (y a busy). Reglas: máx 1 por frase, ≥ emphasis_same_cat_gap_sec
    entre moods de la misma categoría, intervalo del mood libre, tope max_per_cap; prioridad = peso del léxico (3 → 1)
    y después la palabra más rara en la narración completa. El texto del sello es la palabra LITERAL de la voz. Devuelve cuántos agregó."""
    from script_engine.gfx_project import scene_at
    moods = ctx.get("moods") or active_moods()          # F4b §1: léxico del cap (fijo + cargas del director de intensidad)
    dur = scenes[-1].end
    freq = word_freq(ctx.get("narration_all") or " ".join(str(w.get("word", "")) for w in words))
    sids = _sentence_ids(words)
    cands = []
    for i, n, cat, wt, trig in emphasis_candidates(words, moods):
        if wt < 2:                                       # F4c R1/R4: peso 1 nunca dispara sello ni mood
            continue
        rarity = min(freq.get(_tok(w.get("word", "")), 1) for w in words[i:i + n])
        cands.append((-wt, rarity, float(words[i]["start"]) + time_offset, i, n, cat, trig))
    # F5f: en una frase, el sustantivo con ícono literal gana sobre el adjetivo de su misma categoría
    from script_engine.gfx_peak import prefer_icon_nouns
    by_sid: dict[int, list[dict[str, Any]]] = {}
    for c in cands:
        by_sid.setdefault(sids[c[3]], []).append({"word": c[6], "category": c[5], "weight": -c[0], "c": c})
    cands = [h["c"] for hs in by_sid.values() for h in prefer_icon_nouns(hs, moods)]
    used_sids = {e["sid"] for e in out["emphasis"]}
    added = 0
    for neg_wt, rarity, t, i, n, cat, trig in sorted(cands):
        if added >= limit or len(out["emphasis"]) >= max_per_cap("keyword_emphasis"):
            break
        if window and not (window[0] + 1.0 < t < window[1] - 1.0):
            continue
        a, b = t, t + gfx_rules.mood_dur
        if sids[i] in used_sids or b > dur or not all(b <= s or a >= e for s, e in busy):
            continue
        if any(e["category"] == cat and abs(e["start"] - t) < gfx_rules.emphasis_same_cat_gap_sec for e in out["emphasis"]):
            continue
        word = " ".join(str(w.get("word", "")).strip() for w in words[i:i + n])
        word = re.sub(r"^[¿¡\"'«“(]+|[.,;:!?…\"'»”)]+$", "", word)
        sc = scene_at(scenes, t)
        out["emphasis"].append({"word": word, "category": cat, "layer": moods[cat]["layer"],
                                # F4c R4: ícono por categoría + peso ≥ 2 (el de la palabra si lo hay; si no, el de la
                                # categoría). Antes: solo si la palabra era lo que el ícono dibuja
                                "icon": emphasis_icon(cat, trig, -neg_wt, moods),
                                "icon_anim": moods[cat].get("icon_anim") or "stamp",
                                "start": round(t, 3),
                                "duration": round(gfx_rules.mood_dur, 3), "side": getattr(sc, "quiet_side", "right"),
                                "stamp": gfx_rules.emphasis_stamp, "sid": sids[i], "rarity": rarity,
                                "weight": -neg_wt, **({"sfx": moods[cat]["sfx"]} if moods[cat].get("sfx") else {})})
        out["emphasis"].sort(key=lambda e: e["start"])
        busy.append((a, b))
        used_sids.add(sids[i])
        added += 1
        if log is not None:
            log.append(f"emphasis: {word!r} ({cat}, peso {-neg_wt}, frec {rarity}) @ {t:.1f}s" + (" [relleno de hueco]" if window else ""))
    return added


NEVER_ICON_ALONE = {"agua", "aguas"}             # F4c R4: «agua» sola nunca lleva gota (es la palabra de todo el relato)


_QTY_PEOPLE = r"(?:personas|reclusos|reclusas|presos|presas|prisioneros|prisioneras|internos|evacuados|muertos|" \
              r"víctimas|victimas|niños|ninos|hombres|mujeres|almas|turistas|testimonios|desaparecidos|fugitivos)"
_QTY_MONEY = r"(?:dólares|dolares|millones|mil millones|USD)"
_QTY_METRIC = r"(?:metros|metro|m|kilómetros|kilometros|km|centímetros|cm)"
_QTY_NOT = r"(?:años|año|de edad|meses|días|dias|horas|de (?:enero|febrero|marzo|abril|mayo|junio|julio|agosto|" \
           r"septiembre|octubre|noviembre|diciembre))"


def is_count_quantity(val: str, unit: str, fact: str) -> bool:
    """F5d: el contador sube solo con CANTIDADES (personas, dinero, metros). Nunca una edad («10 años»), un lapso ni
    una fecha («29 de agosto», un año). Mira la unidad que eligió el director y, en el fact, lo que sigue a la cifra."""
    if re.fullmatch(r"(19|20)\d\d", val.replace(",", "").replace(".", "")):
        return False
    u = (unit or "").lower().strip()
    if re.fullmatch(_QTY_NOT, u):
        return False
    if re.fullmatch(rf"{_QTY_PEOPLE}|{_QTY_MONEY}|{_QTY_METRIC}", u):
        return True
    for m in re.finditer(re.escape(val), fact):
        before, after = fact[max(0, m.start() - 2):m.start()], fact[m.end():m.end() + 40].lower()
        if re.match(rf"\s*(?:\w+\s+)?{_QTY_NOT}\b", after):
            return False
        if "$" in before or re.match(rf"\s*(?:\w+\s+)?(?:{_QTY_PEOPLE}|{_QTY_MONEY}|{_QTY_METRIC})\b", after):
            return True
    return False


def emphasis_icon(cat: str, trig: str, weight: int, moods: dict[str, dict[str, Any]]) -> str | None:
    """F4c R4: ícono solo con peso ≥ 2 y si la categoría tiene ícono; el de la palabra es preferencia, no condición."""
    if weight < 2 or _tok(trig) in NEVER_ICON_ALONE:
        return None
    from gfx_config import gfx_rules
    if gfx_rules.icon_literal_only:                 # F5b S4: un adjetivo nunca lleva ícono
        from script_engine.m05_narrative import adjectives
        if adjectives(trig):
            return None
    from script_engine.gfx_fragments import category_icon
    return category_icon(cat, _tok(trig), moods)


def emphasis_without_icon(plan: dict[str, Any]) -> list[str]:
    """Palabras de énfasis que salieron sin ícono (entran al vigilante mensual, F2b §3)."""
    return [e["word"] for e in plan.get("emphasis", []) or [] if not e.get("icon_callout")]


def figure_digits(value: str) -> str:
    """'6,500' → '6500' (cifra comparable entre contador, titulares y caps)."""
    return re.sub(r"\D", "", str(value))


def headline_digits(text: str) -> set[str]:
    """Cifras de un texto como dígitos ('Más de 500 prisioneros' → {'500'})."""
    return {figure_digits(m) for m in re.findall(r"\d[\d.,]*\d|\d", str(text))}


def counted_figures_before(work_dir: Path, chapter_number: int) -> set[str]:
    """Pre-merge (Omar): cifras que ya se animaron como contador en caps ANTERIORES (planes resueltos en disco).
    Una cifra se anima una sola vez por video; la segunda vez va como recorte o nada."""
    out: set[str] = set()
    for f in sorted(Path(work_dir).glob("gfx_plan_ch*.resolved.json")):
        m = re.search(r"ch(\d+)", f.name)
        if not m or int(m.group(1)) >= chapter_number:
            continue
        try:
            cu = json.loads(f.read_text(encoding="utf-8"))["plan"].get("count_up")
        except (OSError, ValueError, KeyError):
            continue
        if cu:
            out.add(figure_digits(cu["value_text"]))
    return out


def convert_callout_to_archive(out: dict[str, Any], busy: list[tuple[float, float]], place: Any, *,
                               ctx: dict[str, Any], scenes: list[Any], log: list[str], skip: Any = None) -> bool:
    """Pre-merge (Omar): cap sin recortes con facts elegibles → el MEJOR callout se convierte en recorte en su
    mismo instante. Mejor = fact con fuente, después titular más largo (≤ 8 palabras). Solo facts propios del cap
    (los foráneos valen solo para data_callout). El recorte reemplaza al callout (se libera su intervalo)."""
    from script_engine.gfx_project import scene_at
    facts, elig, fsrc = ctx["facts"], ctx.get("eligible"), ctx.get("fact_source") or {}
    cands = []
    for c in out["callouts"]:
        fi = c.get("fact_idx")
        if fi is None or (elig is not None and (fi not in elig or elig[fi])) or (skip and skip(fi)):
            continue
        head = build_headline(facts[fi])
        if head:
            cands.append((fi not in fsrc, -len(head.split()), c["start"], fi, c))
    for _, _, t, fi, c in sorted(cands, key=lambda x: x[:3]):
        iv = next((x for x in busy if abs(x[0] - c["start"]) < 1e-3), None)
        if iv is not None:
            busy.remove(iv)
        kicker = build_kicker(facts[fi], fsrc.get(fi, ""), build_headline(facts[fi]))
        if place(fi, scene_at(scenes, t).idx, kicker, a=t, why=" [conversión de callout]"):
            out["callouts"].remove(c)
            log.append(f"archive: callout {c['text']!r} convertido en recorte (fact {fi}, cap sin recortes)")
            return True
        if iv is not None:
            busy.append(iv)
    if cands:
        log.append("archive: cap sin recortes y ningún callout convertible entra sin solape")
    return False


def mark_icon_callouts(out: dict[str, Any], log: list[str] | None = None) -> None:
    """F2b §3: los primeros max_per_cap('icon_callout') énfasis (por tiempo) cuya categoría tiene un ícono
    APROBADO de la lista blanca llevan icon_callout=True. El resto queda con el sello de texto solo.
    Nunca un ícono equivocado: sin SVG aprobado (o respaldo habilitado) → sin ícono."""
    from script_engine.gfx_icons import icon_svg
    n = 0
    # F4c R3: la palabra del pico lleva su ícono primero (el tope por cap no se la come)
    for e in sorted(out.get("emphasis", []) or [], key=lambda e: (not e.get("peak_word"), e["start"])):
        has = bool(e.get("icon")) and icon_svg(e["icon"], fallback=gfx_rules.icon_fallback_lucide) is not None
        e["icon_callout"] = bool(has and n < max_per_cap("icon_callout"))
        n += e["icon_callout"]
        if log is not None and e.get("icon") and not e["icon_callout"]:
            log.append(f"icon_callout omitido: {e['word']!r} ({e['icon']}: " + ("sin SVG aprobado)" if not has else "tope por cap)"))


_ARRAY_RE = re.compile(r"\b(\d{1,3}) de (?:los |las |sus |esos |esas )?(\d{1,3})\b")


def array_candidates(facts: list[str], eligible: dict[int, bool] | None) -> list[tuple[int, int, int, str]]:
    """(fact_idx, afectados, total, fragmento literal) para facts con relación 'A de (los) B', A < B ≤ icon_array_max."""
    out = []
    for fi in sorted(eligible if eligible is not None else range(len(facts))):
        if eligible and eligible.get(fi):                    # foráneos solo valen para data_callout
            continue
        for m in _ARRAY_RE.finditer(facts[fi]):
            a, b = int(m.group(1)), int(m.group(2))
            if 0 < a < b <= gfx_rules.icon_array_max:
                out.append((fi, a, b, m.group(0)))
    return out


def place_icon_array(busy: list[tuple[float, float]], *, ctx: dict[str, Any], words: list[dict], scenes: list[Any],
                     time_offset: float, log: list[str]) -> dict[str, Any] | None:
    """F2b §3: icon_array cuando la voz dice la cifra de afectados (o el fragmento entero) y hay lugar libre."""
    from script_engine.gfx_icons import icon_svg
    from script_engine.gfx_project import scene_at
    if icon_svg("persona", fallback=gfx_rules.icon_fallback_lucide) is None:
        return None
    dur = scenes[-1].end
    for fi, a, b, frag in array_candidates(ctx["facts"], ctx.get("eligible")):
        wi = _find_spoken(frag, words)
        wi = wi if wi is not None else _find_spoken(str(a), words)
        if wi is None:
            continue
        t = float(words[wi]["start"]) + time_offset
        t1 = t + gfx_rules.icon_array_dur
        if t1 > dur or not all(t1 <= s or t >= e for s, e in busy):
            log.append(f"icon_array omitido (solape/fuera de rango @ {t:.1f}s): {frag!r}")
            continue
        busy.append((t, t1))
        log.append(f"icon_array: {frag!r} (fact {fi}) @ {t:.1f}s")
        return {"affected": a, "total": b, "label": frag, "start": round(t, 3), "duration": gfx_rules.icon_array_dur,
                "side": getattr(scene_at(scenes, t), "quiet_side", "right"), "fact_idx": fi}
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
        # F2b §1.4: orden del relleno = énfasis de palabra → callout de fact → punch_in
        if "emphasis" in out and len(out["emphasis"]) < max_per_cap("keyword_emphasis") and active_moods():
            placed = place_emphasis(out, busy, words=words, scenes=scenes, ctx=ctx, time_offset=time_offset,
                                    limit=1, window=(a, b), log=log) > 0
        if not placed and len(out["callouts"]) < max_per_cap("data_callout"):
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
                                        "side": side, "gap_fill": True, "fact_idx": fi,
                                        "source": (ctx.get("fact_source") or {}).get(fi, "")})
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

# F2b §1.2: visión busca EL detalle que nombra la voz (no "lo más interesante"). Sin eso → sin zoom.
_ZOOM_SYSTEM = """Mirás UN fotograma de un documental y una FRASE de la narración que nombra un detalle.
Buscá en el fotograma ESE detalle exacto (no otro). Si está visible con claridad, devolvé su caja normalizada
[x, y, w, h] (0–1, origen arriba a la izquierda), de lado entre 0.06 y 0.25, y tu confianza 0–1 de que la caja
muestra lo que dice la frase. Si el detalle no se ve, es ambiguo o solo hay un rostro entero, present=false."""

_ZOOM_SCHEMA: dict[str, Any] = {
    "type": "OBJECT",
    "properties": {"present": {"type": "BOOLEAN"}, "box": {"type": "ARRAY", "items": {"type": "NUMBER"}},
                   "confianza": {"type": "NUMBER"}, "detalle": {"type": "STRING"}},
    "required": ["present", "box", "confianza", "detalle"],
}


def judge_zoom_box(image_path: Path, anchor: str) -> dict[str, Any]:
    """1 call Flash vision. {box | None, confianza, detalle}. Fail-safe: error → box None (sin zoom)."""
    try:
        from google.genai import types as genai_types
        from config import api, gemini_client
        resp = gemini_client.models.generate_content(
            model=api.gemini_model,
            contents=[genai_types.Part.from_bytes(data=image_path.read_bytes(), mime_type="image/jpeg"),
                      f'FRASE: "{anchor}". Devolvé solo el JSON.'],
            config=genai_types.GenerateContentConfig(system_instruction=_ZOOM_SYSTEM, temperature=0.0,
                                                     response_mime_type="application/json",
                                                     response_schema=_ZOOM_SCHEMA))
        cost_tracker.track_gemini_vision(description=f"gfx_zoom_box:{image_path.stem}", calls=1)
        data = json.loads(resp.text)
        box = clamp_box(data.get("box") or []) if data.get("present") else None
        conf = max(0.0, min(1.0, float(data.get("confianza") or 0.0)))
        return {"box": box, "confianza": round(conf, 2), "detalle": str(data.get("detalle", ""))[:120]}
    except Exception as e:  # noqa: BLE001 — sin visión no hay zoom (conservador)
        error_handler.log_warning(PipelineStage.ASSEMBLY, f"[gfx_director] zoom box falló ({e}) → sin zoom")
        return {"box": None, "confianza": 0.0, "detalle": f"error: {e}"}


def apply_zoom_vision(plan: dict[str, Any], *, frame_for_scene: Any, cache: Path, log: list[str]) -> dict[str, Any]:
    """Box del zoom = visión buscando la frase ancla (cache por escena + ancla). Sin box o confianza
    < zoom_conf_min → sin zoom en el cap. El umbral se aplica al leer (cambiarlo no re-llama)."""
    ez = plan.get("evidence_zoom")
    if not ez:
        return plan
    anchor = str(ez.get("anchor") or "")
    if not anchor:
        log.append("zoom omitido (sin frase ancla)")
        return {**plan, "evidence_zoom": None}
    key = f"{ez['scene_idx']}|{anchor}"
    data: dict[str, Any] = {}
    if cache.exists():
        try:
            data = json.loads(cache.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            data = {}
    if key not in data:
        img = frame_for_scene(ez["scene_idx"])
        data[key] = judge_zoom_box(img, anchor) if img else {"box": None, "confianza": 0.0, "detalle": "sin frame"}
        cache.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    v = data[key]
    conf = float(v.get("confianza") or 0.0)
    if v.get("box") is None or conf < gfx_rules.zoom_conf_min:
        log.append(f"zoom omitido (visión: '{anchor}' no encontrado en escena {ez['scene_idx']} — "
                   f"conf {conf:.2f} < {gfx_rules.zoom_conf_min} o sin box; {v.get('detalle', '')})")
        return {**plan, "evidence_zoom": None}
    log.append(f"zoom box por visión escena {ez['scene_idx']} '{anchor}': {v['box']} conf {conf:.2f} ({v.get('detalle', '')})")
    return {**plan, "evidence_zoom": {**ez, "box": v["box"], "confidence": conf}}


# ═══════════════════════════════════════════════════════════════
#  Entry point
# ═══════════════════════════════════════════════════════════════

# cambia el prompt → el cache crudo de una versión anterior se re-llama
DIRECTOR_VERSION = "v1.6"      # v1.1 = + chapter_question (F2 §0d) · v1.5 = titular determinista + zoom con ancla (F2b §1)
#                               v1.6 = plan dorado de la identidad como few-shot (F4 §2.1)

def select_gfx_plan(chplan: Any, *, ctx: dict[str, Any], words: list[dict], scenes: list[Any],
                    work_dir: Path, log: list[str] | None = None, time_offset: float = 0.0) -> dict[str, Any]:
    """1 call Flash por cap → plan validado (índices).

    Cache en work_dir/gfx_plan_chXX.json = respuesta CRUDA del LLM (se re-valida en cada carga,
    así un cambio de reglas/clamps aplica sin re-llamar a Gemini). Guardar el plan ya validado
    rompía la ida y vuelta (sin `use`) → bloques perdidos al reusar (bug F1 ch06).
    """
    log = log if log is not None else []
    cache = work_dir / f"gfx_plan_{chplan.chapter_id}.json"
    kw = dict(n_facts=len(ctx["facts"]), n_words=len(words), scenes=scenes, facts=ctx["facts"], log=log,
              eligible=ctx.get("eligible"), words=words, time_offset=time_offset,
              fact_source=ctx.get("fact_source"))
    raw: Any = None
    if cache.exists():
        try:
            cached = json.loads(cache.read_text(encoding="utf-8"))
            raw = cached.get("raw") if cached.get("director") == DIRECTOR_VERSION else None
        except (OSError, ValueError, AttributeError):
            raw = None
    if raw is None:
        try:
            raw = call_flash_json(_build_user_prompt(ctx, words, scenes), system_instruction=system_prompt(),
                                  response_schema=_SCHEMA, description=f"gfx_director {chplan.chapter_id}")
        except Exception as e:  # noqa: BLE001 — Gemini caído → fallback estático (solo title_card)
            error_handler.log_warning(PipelineStage.ASSEMBLY, f"[gfx_director] {chplan.chapter_id} Gemini falló ({e}) → solo title_card")
            return validate_plan({"title_card": {"use": True}}, **kw)   # el fallback NO se cachea
        cache.write_text(json.dumps({"director": DIRECTOR_VERSION, "raw": raw}, ensure_ascii=False, indent=1),
                         encoding="utf-8")
    return validate_plan(raw, **kw)
