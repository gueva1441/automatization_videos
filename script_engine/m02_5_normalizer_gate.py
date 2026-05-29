"""
m02_5_normalizer_gate.py — Gate humano del normalizer (PR 2.0.X chat 24).

POST PR 2.0.X: detector regex reemplazado por LLM auditor.

Flujo:
  1. LLM auditor analiza la narración entera y emite spans (original + sugerencia)
     en 8 categorías (las 6 donde ElevenLabs falla en español neutro: acronym,
     acronym_with_number, gender, foreign_word, time_format, punctuation_artifact;
     más abbreviation y unit que pueden venir del custom_dict).
  2. CLI [V/E/R/S] por span — el usuario aprueba, edita, rechaza o skipea.
  3. Bifurcación de persistencia:
       - SIEMPRE → patch al texto del cap → 01b_narration_normalized.json
       - is_recurring=true → entry al custom_dict.json (futuros videos)
  4. 01b_narration.json queda INTOCABLE. La fuente del guion no se modifica.

audio_manager._resolve_text_for_tts() lee 01b_narration_normalized.json si
existe, fallback a normalize_for_tts() del tts_normalizer minimal.

ARCHITECTURE.md anti-patrón #3 cumplido: el LLM PROPONE, el usuario APRUEBA,
el sistema APLICA. El validador no reescribe por sí solo.
"""
from __future__ import annotations

import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

from gemini_helpers import call_flash_json
from error_handler import error_handler, PipelineStage

from tts_normalizer import (
    normalize_for_tts,
    _load_custom_dict as _reload_custom_dict_runtime,
    ACRONYMS_SPELLED,
    ACRONYMS_PRONOUNCEABLE,
)
from config import DATA_DIR

STEPS_DIR = DATA_DIR / "scripts" / "_steps"


# ═══════════════════════════════════════════════════════════════
#  CONSTANTES
# ═══════════════════════════════════════════════════════════════

CUSTOM_DICT_PATH: Path = DATA_DIR / "normalizer_custom_dict.json"

# Categorías internas del LLM (las del custom_dict.json siguen siendo
# spelled/pronounceable/abbreviation/unit — manejadas vía _CATEGORY_TO_DICT).
VALID_LLM_CATEGORIES = (
    "acronym", "acronym_with_number", "abbreviation", "unit",
    "gender", "foreign_word", "time_format", "punctuation_artifact",
    "year_format", "conjunction_y",  # ← agregadas #162
)

# Mapping de category interna → category del custom_dict.json
# (para spans con is_recurring=true que se persisten al dict)
_CATEGORY_TO_DICT = {
    "acronym": "spelled",                # default; LLM puede sugerir "pronounceable"
    "acronym_with_number": "spelled",    # se persiste solo la sigla, no el número
    "abbreviation": "abbreviation",
    "unit": "unit",
}

# Categorías que JAMÁS van al dict (son one-off por definición).
_CATEGORIES_NEVER_RECURRING = {
    "gender", "foreign_word", "time_format", "punctuation_artifact",
    "year_format",  # ← one-off por cap, igual que time_format
}
# Nota #162: conjunction_y NO está acá a propósito. "Y" → "I" puede ser regla
# global del canal (recurring=true → custom_dict) si el LLM lo decide así.
# Si en validación palpable Pripyat resulta que siempre debería ser one-off,
# moverla acá en chat 26.


# ═══════════════════════════════════════════════════════════════
#  PROMPT DEL LLM AUDITOR
# ═══════════════════════════════════════════════════════════════

def _build_system_instruction(
    known_acronyms_spelled: dict[str, str],
    known_acronyms_pronounceable: set[str],
) -> str:
    """Arma el system_instruction del LLM auditor incluyendo el dict actual
    como referencia (siglas ya resueltas que el LLM puede reusar)."""
    known_spelled_str = ", ".join(
        f'"{k}"→"{v}"' for k, v in sorted(known_acronyms_spelled.items())
    ) or "(ninguna todavía)"
    known_pron_str = ", ".join(sorted(known_acronyms_pronounceable)) or "(ninguna)"

    return f"""\
Sos un auditor de pronunciación TTS para ElevenLabs en español neutro,
canal documental.

═══════════════════════════════════════════════════════════════
CONTEXTO TÉCNICO IMPORTANTE
═══════════════════════════════════════════════════════════════
ElevenLabs aplica normalización automática (apply_text_normalization=on por
default). Maneja BIEN sin tu intervención:
  - Cardinales: 1980, 13500, 200000 → "mil novecientos ochenta", etc.
  - Decimales: 121.5, 3,14
  - Monedas: $2,500 → "dos mil quinientos dólares"
  - Fechas: 26 de abril de 1986
  - Horas HH:MM: 14:30 → "catorce treinta"
  - Ordinales: 1.º, 2.ª

NO marques estos casos. NO reescribas lo que ya funciona.

═══════════════════════════════════════════════════════════════
TU TRABAJO: detectar SOLO los 8 casos donde ElevenLabs FALLA
═══════════════════════════════════════════════════════════════

1. ACRONYM — siglas no comunes en español que ElevenLabs deletrearía mal.
   Ej: "RBMK", "EPIRB", "OMS", "TLC".
   → suggested = letras deletreadas en español fonético.

2. ACRONYM_WITH_NUMBER — sigla + guion + número.
   Ej: "RBMK-1000" → ElevenLabs lee "guion mil" raro.
   → suggested = sigla deletreada + número en palabras, SIN guion.
     "RBMK-1000" → "erre be eme ka mil"
     "F-16" → "efe dieciséis"

3. GENDER — concordancia de género en números escritos en palabras.
   ElevenLabs por default escribe los números en masculino:
   - "31 muertes" lo lee como "treinta y uno muertes" (mal — muertes es femenino)
     → suggested = "treinta y una muertes"
   - "200000 víctimas" → "doscientos mil víctimas" (mal)
     → suggested = "doscientas mil víctimas"
   - "21 personas" → "veintiún personas" o "veintiuna personas" (depende contexto)

   ⚠ ATENCIÓN INFLEXIBLE — REVISÁ ESTOS PATRONES SIN EXCEPCIÓN:

   a) NÚMEROS CON SEPARADOR DE MILES seguidos de sustantivo femenino —
      patrón frecuentemente perdido. Tratalos con la misma rigurosidad
      que los números chicos:
      "7,300 toneladas"  → "siete mil trescientas toneladas"
      "9,335 víctimas"   → "nueve mil trescientas treinta y cinco víctimas"
      "1,500 personas"   → "mil quinientas personas"
      "200,000 vidas"    → "doscientas mil vidas"
      "13,500 mujeres"   → "trece mil quinientas mujeres"

   b) NÚMEROS CHICOS: "31 muertes", "21 personas", etc.

   c) NÚMEROS GRANDES EN PALABRAS YA: "doscientos mil víctimas" (mal) →
      "doscientas mil víctimas".

   REGLA OPERATIVA: para CADA número que aparezca en el texto, preguntate:
   "¿el sustantivo que sigue es femenino?" Si sí Y el número en palabras
   sería masculino por default → SPAN OBLIGATORIO. NO te saltees números
   con coma o punto en el medio (1,500 / 7,300 / 200,000) — esos son los
   que más se pierden.

   El span "original" debe ser el FRAGMENTO completo que cubre número +
   sustantivo, ej: "7,300 toneladas" (no solo "7,300").

4. FOREIGN_WORD — palabras en latín/inglés/otro idioma que ElevenLabs ES no
   pronuncia natural.
   Ej: "gamma" (lo lee como "ga-ma"), "sphaerospermum" (latín),
   "Cladosporium" (latín), nombres científicos.
   → suggested = aproximación fonética en español o leer letra por letra.
     "gamma" → "gama"
     "sphaerospermum" → "esferospermum"

5. TIME_FORMAT — horas con SEGUNDOS (HH:MM:SS).
   Ej: "01:23:45" → ElevenLabs deja el segundo `:` literal.
   → suggested = forma hablada completa.
     "01:23:45" → "una y veintitrés con cuarenta y cinco segundos"

6. PUNCTUATION_ARTIFACT — comillas simples, '\\n' literales, signos raros,
   tags internos del pipeline tipo [F##] o [F\\d+].
   Ej: "'Refugio'" → ElevenLabs hace pausa rara.
   Ej: "[F02]" → lo lee literal "F cero dos" destruyendo el audio.
   → suggested = quitar comillas, cambiar a comillas dobles, o remover el tag.
   ⚠ EXCEPCIÓN: los "..." (puntos suspensivos) son PAUSAS INTENCIONALES del
     guionista — el TTS las lee como silencio. NUNCA las marques como
     artefacto. Dejalas intactas.

7. YEAR_FORMAT — años de 4 dígitos (1800-2099). Aunque la docu oficial dice
   que ElevenLabs maneja cardinales bien, empíricamente con voces cloned al
   español hay artefactos (se come la "s" final, lectura partida raro).
   → suggested = año en palabras explícito.
     "1986" → "mil novecientos ochenta y seis"
     "1991" → "mil novecientos noventa y uno"
     "2023" → "dos mil veintitrés"

8. CONJUNCTION_Y — la conjunción "Y" sola, mayúscula, palabra suelta.
   ElevenLabs en voces cloned inglesas al español la lee "e" en vez de "i"
   (el sonido natural de la conjunción "y").
   → suggested = reemplazar "Y" por "I" para forzar pronunciación correcta.
     " Y un hongo" → " I un hongo"
     "¿Y qué" → "¿I qué"

═══════════════════════════════════════════════════════════════
SIGLAS YA CONOCIDAS (custom_dict.json acumulado) — REUSÁ ESTAS
═══════════════════════════════════════════════════════════════
Spelled (deletreadas): {known_spelled_str}
Pronounceable (literales): {known_pron_str}

Si detectás una sigla que YA ESTÁ en spelled, NO la marques como span — el
sistema la aplica automáticamente vía custom_dict.

═══════════════════════════════════════════════════════════════
FLAG IS_RECURRING (crítico)
═══════════════════════════════════════════════════════════════
- true → la corrección va a aparecer en otros videos del canal.
  Ejemplo: "RBMK" como sigla. Se persiste al custom_dict.json.
  Categorías que pueden ser recurring: acronym, acronym_with_number,
  abbreviation, unit.

- false → es one-off del topic actual.
  Ejemplo: "treinta y una muertes" (gender), "01:23:45" (time_format),
  "sphaerospermum" (foreign_word del topic Pripyat),
  "mil novecientos ochenta y seis" (year_format del topic Pripyat).
  Categorías SIEMPRE false: gender, foreign_word, time_format,
  punctuation_artifact, year_format.
  Categoría conjunction_y: puede ser true (regla global del canal) o false
  según contexto. El LLM decide caso por caso.

═══════════════════════════════════════════════════════════════
SCHEMA DE OUTPUT (JSON estricto, sin markdown)
═══════════════════════════════════════════════════════════════
{{
  "spans": [
    {{
      "chapter_number": 1,
      "original": "RBMK-1000",
      "suggested": "erre be eme ka mil",
      "category": "acronym_with_number",
      "is_recurring": true,
      "reasoning": "sigla con número, el guion rompe pronunciación"
    }},
    {{
      "chapter_number": 1,
      "original": "treinta y uno muertes",
      "suggested": "treinta y una muertes",
      "category": "gender",
      "is_recurring": false,
      "reasoning": "muertes es femenino plural, debe ser una"
    }}
  ]
}}

REGLAS DEL OUTPUT:
- "original" debe ser substring EXACTO del texto del cap (necesario para
  search-and-replace determinístico).
- Si el mismo problema aparece en varios caps, emití UNA span por cap (con
  chapter_number distinto). El campo "original" puede ser idéntico.
- "reasoning" en español, una línea, máx 20 palabras.
- Si no hay nada que normalizar: {{"spans": []}}.

Solo JSON. Sin markdown. Sin texto fuera del JSON.
"""


# ═══════════════════════════════════════════════════════════════
#  AUDITOR LLM
# ═══════════════════════════════════════════════════════════════

def _audit_with_llm(narration: dict) -> list[dict]:
    """LLM auditor: emite spans de normalización para los 6 casos donde
    ElevenLabs falla en español neutro.

    Args:
        narration: output de m01b ({"chapters": [{"chapter_number", "narration"}], ...})

    Returns:
        list[span] con los campos del schema. Vacía si nada que normalizar
        o si LLM falló.
    """
    chapters_block = "\n".join(
        f"=== CAP {c['chapter_number']} ===\n{c.get('narration', '').strip()}"
        for c in narration.get("chapters", [])
    )

    user_prompt = f"""Auditá las siguientes narraciones documentales en español neutro
para ElevenLabs. Detectá SOLO los 6 casos definidos en tu system_instruction.
Devolvé el JSON con el schema indicado.

{chapters_block}
"""

    system_instruction = _build_system_instruction(
        known_acronyms_spelled=ACRONYMS_SPELLED,
        known_acronyms_pronounceable=ACRONYMS_PRONOUNCEABLE,
    )

    try:
        response = call_flash_json(
            prompt=user_prompt,
            system_instruction=system_instruction,
        )
        spans = response.get("spans", [])
        if not isinstance(spans, list):
            raise ValueError("spans no es lista")
    except Exception as e:
        error_handler.log_warning(
            PipelineStage.AUDIO,
            f"[normalizer_gate] LLM auditor falló ({type(e).__name__}: {e}) — "
            f"continuando sin normalización adicional",
        )
        return []

    # Validación: cada span debe tener todos los campos requeridos
    valid_spans = []
    for s in spans:
        try:
            if (
                isinstance(s.get("chapter_number"), int)
                and isinstance(s.get("original"), str) and s["original"]
                and isinstance(s.get("suggested"), str) and s["suggested"]
                and s.get("category") in VALID_LLM_CATEGORIES
                and isinstance(s.get("is_recurring"), bool)
            ):
                # Forzar is_recurring=False si la categoría es never-recurring
                if s["category"] in _CATEGORIES_NEVER_RECURRING:
                    s["is_recurring"] = False
                valid_spans.append(s)
        except (KeyError, TypeError):
            continue

    return valid_spans


# ═══════════════════════════════════════════════════════════════
#  CLI INTERACTIVO
# ═══════════════════════════════════════════════════════════════

def _interactive_review_spans(spans: list[dict]) -> dict:
    """CLI por span. Acciones: V (aprobar) / R (rechazar) / E (editar) / S (skip todo).

    Returns:
        {
          "approved": list[span],       # spans aprobados tal cual
          "rejected": list[span],       # spans rechazados (no se aplican)
          "edited":   list[span],       # spans con suggested editado por usuario
          "skipped":  bool,
        }
    """
    approved: list[dict] = []
    rejected: list[dict] = []
    edited: list[dict] = []
    skipped = False

    n = len(spans)
    print()
    print("─" * 70)
    print(f"  GATE NORMALIZER — {n} span(s) para revisar")
    print("─" * 70)

    for i, sp in enumerate(spans, 1):
        recur = "♻ recurring" if sp.get("is_recurring") else "1× one-off"
        print()
        print(f"  [{i}/{n}] Cap {sp['chapter_number']} — {sp['category']} ({recur})")
        print(f"    Original:    {sp['original']!r}")
        print(f"    Sugerido:    {sp['suggested']!r}")
        print(f"    Razón:       {sp['reasoning']}")
        print(f"    [V] Aprobar  [R] Rechazar  [E] Editar suggested  [S] Skip resto")

        while True:
            action = input("    > ").strip().upper()
            if action in ("V", "R", "E", "S"):
                break
            print("    Inválido. V/R/E/S.")

        if action == "V":
            approved.append(sp)
            print("    ✓ aprobado")
        elif action == "R":
            rejected.append(sp)
            print("    ✗ rechazado")
        elif action == "E":
            new_suggested = input(f"    Nuevo suggested: ").strip()
            if not new_suggested:
                new_suggested = sp["suggested"]
                print(f"    (vacío → manteniendo: {new_suggested!r})")
            edited_span = {
                **sp,
                "suggested": new_suggested,
                "reasoning": f"{sp['reasoning']} (editado manualmente)",
            }
            edited.append(edited_span)
            print(f"    ✏  editado → {new_suggested!r}")
        elif action == "S":
            skipped = True
            print(f"    ⏭  skip total — corte en {i}/{n}")
            break

    return {
        "approved": approved,
        "rejected": rejected,
        "edited": edited,
        "skipped": skipped,
    }


# ═══════════════════════════════════════════════════════════════
#  PERSISTENCIA — bifurcada (custom_dict + narration_normalized)
# ═══════════════════════════════════════════════════════════════

def _persist_to_custom_dict(
    spans_to_persist: list[dict],
    topic_id: str,
) -> int:
    """Persiste spans con is_recurring=true al custom_dict.json.

    Solo procesa spans cuya category esté en _CATEGORY_TO_DICT.
    Para acronym_with_number, persiste solo la parte alfa de "original"
    (ej: "RBMK-1000" → token "RBMK", pronunciation derivada de suggested).

    Returns:
        Cantidad de entries nuevas efectivamente agregadas al dict.
    """
    if CUSTOM_DICT_PATH.exists():
        try:
            data = json.loads(CUSTOM_DICT_PATH.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, OSError):
            data = {"version": 1, "entries": []}
    else:
        data = {"version": 1, "entries": []}

    existing_tokens = {e.get("token") for e in data.get("entries", [])}
    new_entries: list[dict] = []
    now = datetime.now().isoformat()

    for sp in spans_to_persist:
        if not sp.get("is_recurring"):
            continue
        cat = sp["category"]
        dict_cat = _CATEGORY_TO_DICT.get(cat)
        if dict_cat is None:
            continue

        # Para acronym_with_number, extraer solo la parte alfa como token
        # Ej: "RBMK-1000" → token "RBMK", pron "erre be eme ka"
        original = sp["original"]
        suggested = sp["suggested"]
        if cat == "acronym_with_number":
            m = re.match(r"^([A-Za-zÁÉÍÓÚÑáéíóúñ]+)", original)
            if not m:
                continue
            token = m.group(1)
            # Heurística: pronunciación = primeras N palabras del suggested
            # donde N = len(token). Ej: "RBMK" (4) → primeras 4 palabras de
            # "erre be eme ka mil" = "erre be eme ka". Conservadora.
            pron_words = suggested.split()
            pron_letters = pron_words[:len(token)]
            pron = " ".join(pron_letters) if pron_letters else suggested
        else:
            token = original
            pron = suggested

        if token in existing_tokens:
            continue

        new_entries.append({
            "token": token,
            "category": dict_cat,
            "pronunciation": pron,
            "added_at": now,
            "first_seen_in_topic": topic_id,
        })
        existing_tokens.add(token)

    if not new_entries:
        return 0

    data.setdefault("entries", []).extend(new_entries)
    CUSTOM_DICT_PATH.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    _reload_custom_dict_runtime()
    return len(new_entries)


def _apply_spans_to_narration(
    narration: dict,
    approved_spans: list[dict],
    edited_spans: list[dict],
) -> dict:
    """Aplica spans aprobados+editados al texto de cada cap (search-replace).

    El span "original" debe ser substring exacto del cap. Si no se encuentra,
    se loguea warning y se skipea ese span (defensa contra desincronía).

    Returns:
        Diccionario con la estructura del 01b_narration_normalized.json:
        {
          "topic_id": str,
          "generated_at": iso,
          "chapters": [
            {
              "chapter_number": int,
              "narration_original": str,
              "narration_normalized": str,
              "spans_applied": list[span_with_decision]
            }
          ]
        }
    """
    all_spans = list(approved_spans) + list(edited_spans)
    spans_by_cap: dict[int, list[dict]] = {}
    for sp in all_spans:
        spans_by_cap.setdefault(sp["chapter_number"], []).append(sp)

    out_chapters = []
    for ch in narration.get("chapters", []):
        cap_n = ch["chapter_number"]
        original_text = ch.get("narration", "")
        normalized_text = original_text
        applied_spans = []

        # Aplicar spans en orden de longitud descendente para evitar matches parciales
        cap_spans = sorted(
            spans_by_cap.get(cap_n, []),
            key=lambda s: len(s["original"]),
            reverse=True,
        )
        for sp in cap_spans:
            orig_frag = sp["original"]
            new_frag = sp["suggested"]
            if orig_frag in normalized_text:
                normalized_text = normalized_text.replace(orig_frag, new_frag, 1)
                applied_spans.append({**sp, "decision": "applied"})
            else:
                error_handler.log_warning(
                    PipelineStage.AUDIO,
                    f"[normalizer_gate] cap {cap_n}: span original "
                    f"{orig_frag!r} no encontrado en texto, skipeado",
                )
                applied_spans.append({**sp, "decision": "skipped_not_found"})

        out_chapters.append({
            "chapter_number": cap_n,
            "narration_original": original_text,
            "narration_normalized": normalized_text,
            "spans_applied": applied_spans,
        })

    return {
        "topic_id": narration.get("topic_id", ""),
        "generated_at": datetime.now().isoformat(),
        "chapters": out_chapters,
    }


def _persist_normalized_narration(topic_id: str, normalized_data: dict) -> Path:
    """Escribe data/scripts/_steps/<topic_id>/01b_narration_normalized.json"""
    step_dir = STEPS_DIR / topic_id
    step_dir.mkdir(parents=True, exist_ok=True)
    out_path = step_dir / "01b_narration_normalized.json"
    out_path.write_text(
        json.dumps(normalized_data, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return out_path


# ═══════════════════════════════════════════════════════════════
#  ENTRY POINT PÚBLICO
# ═══════════════════════════════════════════════════════════════

def gate_normalizer_for_topic(
    topic_id: str,
    narration: dict,
    interactive: bool = True,
) -> dict:
    """Corre el gate LLM auditor sobre la narración de m01b.

    Flujo:
      1. LLM auditor detecta spans (6 categorías where ElevenLabs falla)
      2. Si interactive: CLI [V/E/R/S] por span
      3. Aplica spans aprobados/editados al texto → 01b_narration_normalized.json
      4. Spans con is_recurring=true → custom_dict.json (para futuros videos)

    Args:
        topic_id: para trazabilidad y path del normalized.
        narration: output de m01b (con narration_original sin tocar).
        interactive: si False, salta CLI y solo loguea (modo batch).

    Returns:
        dict con spans_detected, approved/rejected/edited, added_to_dict,
        normalized_path (Path al 01b_narration_normalized.json escrito).
    """
    out: dict[str, Any] = {
        "topic_id": topic_id,
        "spans_detected": [],
        "approved": [],
        "rejected": [],
        "edited": [],
        "added_to_dict": 0,
        "normalized_path": None,
    }

    # 1. Auditor LLM
    print(f"  [normalizer_gate] LLM auditor analizando narración...")
    spans = _audit_with_llm(narration)
    out["spans_detected"] = spans

    if not spans:
        # Sin spans: igual generamos narration_normalized.json con texto idéntico
        # (para que audio_manager pueda leerlo siempre y no haya rama especial).
        normalized_data = _apply_spans_to_narration(narration, [], [])
        out["normalized_path"] = _persist_normalized_narration(topic_id, normalized_data)
        return out

    if not interactive:
        error_handler.log_warning(
            PipelineStage.AUDIO,
            f"[normalizer_gate] {len(spans)} span(s) detectado(s) — modo batch, "
            f"se aplican TODOS sin revisión humana",
        )
        normalized_data = _apply_spans_to_narration(narration, spans, [])
        out["approved"] = spans
        out["normalized_path"] = _persist_normalized_narration(topic_id, normalized_data)
        out["added_to_dict"] = _persist_to_custom_dict(spans, topic_id)
        return out

    # 2. CLI interactivo
    review = _interactive_review_spans(spans)
    out["approved"] = review["approved"]
    out["rejected"] = review["rejected"]
    out["edited"] = review["edited"]

    # 3. Aplicar al texto + persistir narration_normalized
    normalized_data = _apply_spans_to_narration(
        narration,
        approved_spans=review["approved"],
        edited_spans=review["edited"],
    )
    out["normalized_path"] = _persist_normalized_narration(topic_id, normalized_data)

    # 4. Persistir recurring al custom_dict
    out["added_to_dict"] = _persist_to_custom_dict(
        spans_to_persist=[*review["approved"], *review["edited"]],
        topic_id=topic_id,
    )

    return out
