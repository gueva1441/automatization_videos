"""
test_subtema_fanout_dryrun.py — C5: dry-run END-TO-END del fan-out sobre UN contenedor
conocido (#17 "18 Terrifying Ocean Mysteries"), flag ON, SIN PERSISTIR seeds.

Ejercita el camino real: fetch_transcript → classify → extract_segment_subjects → measure
(ES-primero + LAXO + relevancia) → cap top-K → _build_seed. Imprime los seeds y el costo.
NO escribe selected_seeds.json ni nada de prod.

Correr:  python -X utf8 test_subtema_fanout_dryrun.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

from script_engine.transcript_fetch import fetch_transcript
from script_engine.subtopic_classifier import classify
from script_engine.subtopic_extractor import extract_segment_subjects, verify_names
from script_engine.subtopic_measurer import measure
from niche_discoverer import _build_seed, SUBTEMA_FANOUT_CAP_K

CORPUS = Path("_lab_out/transcripts_chat42.json")
TARGET_N = 17  # contenedor conocido (barcos), roster limpio


def main():
    videos = json.loads(CORPUS.read_text(encoding="utf-8"))
    v = videos[TARGET_N - 1]
    vid, en_title = v.get("video_id"), v.get("title")
    print(f"C5 DRY-RUN fan-out (flag ON simulado, NO persiste) — #{TARGET_N} {en_title}")
    print(f"  video_id={vid}\n")

    cost = {"transcript": 0, "gemini": 0, "es_scrape": 0, "en_scrape": 0}

    transcript = fetch_transcript(vid); cost["transcript"] += 1
    if not transcript:
        print("  sin transcript → en prod caería a 1 seed genérico (fallback). Fin dry-run.")
        return
    print(f"  transcript len={len(transcript):,}")

    cls = classify(en_title, transcript); cost["gemini"] += 1
    print(f"  clasificación: {cls['tipo']} :: {cls['razon'][:70]}")
    if cls["tipo"] != "CONTENEDOR":
        print("  no es CONTENEDOR → en prod = 1 seed genérico. Fin dry-run.")
        return

    subjects = extract_segment_subjects(en_title, transcript); cost["gemini"] += 1
    print(f"  sujetos-de-segmento: {len(subjects)}")

    measured = []
    for s in subjects:
        m = measure(s)
        cost["es_scrape"] += 1
        if m["verdict"] not in ("CORTADO_ES", "ES_ERROR"):
            cost["en_scrape"] += 1
        if m.get("passes"):
            measured.append((s, m))
    measured.sort(key=lambda sm: (sm[1].get("en") or {}).get("top_rel_views", 0), reverse=True)
    capped = measured[:SUBTEMA_FANOUT_CAP_K]
    dropped = len(measured) - len(capped)

    verif = verify_names([s for s, _ in capped]); cost["gemini"] += 1

    # construir seeds (sin persistir)
    seeds = []
    for s, m in capped:
        en, es, vf = m["en"], m["es"], verif.get(s, {})
        seeds.append(_build_seed(
            title=s, mode="spy_arbitrage", root_niche=v.get("subnicho"),
            evidence={
                "en_viral": {"original_title": en.get("top_rel_title"),
                             "views": en.get("top_rel_views"),
                             "video_id": en.get("top_rel_video_id"),
                             "query": s, "passed_reason": "laxo"},
                "es_gap": {"saturation": es.get("saturation"), "label": es.get("label")},
                "subtema_of_container": {"parent_video_id": vid, "parent_title": en_title},
                "asr_verify": {"canonical": vf.get("canonical"), "is_real": vf.get("is_real")},
            }))

    print(f"\n  {len(subjects)} sujetos → {len(measured)} pasan medidor → {len(capped)} seeds "
          f"(cap K={SUBTEMA_FANOUT_CAP_K}, {dropped} drop por cap)\n")
    print(f"  {'SEED (title)':<28} {'EN_views':>10} {'ES':<9} ASR  ← parent")
    for sd in seeds:
        ev = sd["evidence"]; en = ev["en_viral"]; es = ev["es_gap"]; asr = ev["asr_verify"]
        flag = "" if asr.get("is_real") is not False else "no-real?"
        can = f" →{asr['canonical']}" if asr.get("canonical") and asr["canonical"].strip().lower() != sd["seed_title"].strip().lower() else ""
        print(f"  {sd['seed_title'][:28]:<28} {en['views']:>10,} {str(es['label']):<9} {flag:<8}{can}")
        print(f"       parent: {ev['subtema_of_container']['parent_video_id']} "
              f"\"{(ev['subtema_of_container']['parent_title'] or '')[:46]}\"")

    print(f"\n  COSTO dry-run (1 contenedor): transcript={cost['transcript']} · "
          f"Gemini={cost['gemini']} (classify+extract+verify) · "
          f"ES_scrape={cost['es_scrape']} · EN_scrape={cost['en_scrape']} "
          f"(ES-primero ahorró {cost['es_scrape']-cost['en_scrape']} EN)")
    print(f"  Proyección 15 contenedores ≈ {15*cost['en_scrape']} EN + {15*cost['es_scrape']} ES scrapes")
    print("\n  NADA persistido. selected_seeds.json intacto.")


if __name__ == "__main__":
    main()
