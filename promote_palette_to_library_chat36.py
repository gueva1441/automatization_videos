"""
promote_palette_to_library_chat36.py — Promueve los 7 tracks curados de chat 36
a audio_library/ como library fija, y retira la library vieja del Nyos a backup.

MUTA audio_library/. NO toca music_config.py, NO toca m07 (codigo), NO llama
ElevenLabs. Copia los mp3 EXACTOS elegidos + escribe sus descriptores JSON con
el schema que m07 espera. 1 candidato por intent => reuso forzado, nunca regenera.

Pasos:
  1. Guard: si ya hay *_curated.* en library, aborta.
  2. Mueve TODO lo que haya en audio_library/ (la vieja Nyos) a
     audio_library_backup_nyos_chat36/. NO borra.
  3. Copia los 7 winners -> <intent>_curated.mp3 + escribe <intent>_curated.json.
  4. Self-check: _load_library() ve 7, _filter_candidates da 1 por intent.

USO:
    python promote_palette_to_library_chat36.py
"""
import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

from config import BASE_DIR
from audio_config import ACTIVE_AUDIO_PROFILE
from music_config import NEGATIVE_GLOBAL_STYLES
from script_engine.m07_music_director import _load_library, _filter_candidates

LIBRARY_DIR = BASE_DIR / "audio_library"
BACKUP_DIR = BASE_DIR / "audio_library_backup_nyos_chat36"
SOURCE_DIR = BASE_DIR / "_music_palette_test_chat36"

# intent -> archivo winner elegido por Omar
WINNERS: dict[str, str] = {
    "hook":           "hook_60s_a.mp3",
    "setup":          "setup_60s_b.mp3",
    "rising_tension": "rising_tension_60s_a.mp3",
    "shock":          "shock_60s_a.mp3",
    "consequences":   "consequences_60s_b.mp3",
    "resolution":     "resolution_60s_b.mp3",
    "outro":          "outro_60s_b.mp3",
}

# Prompts base que generaron cada winner (registro canonico de la musica del canal).
PROMPTS: dict[str, str] = {
    "hook": (
        "Dark cinematic underscore in D minor. A low sustained cello drone with "
        "bright glockenspiel notes ringing clearly high above in a tense, "
        "insistent pulse, creating a sense of imminence and pulling the listener "
        "in from the very first second. Present and gripping, not slow or "
        "contemplative. Designed for seamless background looping under "
        "documentary narration. 85 BPM, dark and urgent, consistent intensity "
        "throughout."
    ),
    "setup": (
        "Slow cinematic underscore in D minor. A patient low cello drone with "
        "sparse, distant glockenspiel notes ringing high above at long "
        "intervals, clearly audible against the dark bed. Dark mystery "
        "atmosphere with quiet ominous tension and a sense of space. Designed "
        "for seamless background looping under documentary narration. 65 BPM, "
        "brooding and spacious, consistent dark depth throughout."
    ),
    "rising_tension": (
        "Building cinematic underscore in G sharp minor. A low sustained cello "
        "drone beneath high tremolo strings in viola and violin that slowly "
        "rise and intensify, clearly audible up high, mounting unease that "
        "pushes forward and refuses to settle. Designed for seamless background "
        "looping under documentary narration. 78 BPM, dark and steadily "
        "tightening, consistent intensity throughout."
    ),
    "shock": (
        "Dramatic cinematic underscore in F sharp minor. A heavy low cello "
        "drone beneath a high dissonant string cluster in violins and violas, "
        "screeching and unsettling in the upper register, cutting clearly "
        "through. Dark ominous intensity. Designed for seamless background "
        "looping under documentary narration. 80 BPM, dark and consistent "
        "throughout."
    ),
    "consequences": (
        "Heavy cinematic underscore in D minor. A deep low cello drone with "
        "slow, spaced glockenspiel notes ringing high above, sparse and "
        "weighted, carrying a sense of crushing gravity and loss. Clearly "
        "audible high notes against the dark bed. Designed for seamless "
        "background looping under documentary narration. 60 BPM, brooding and "
        "heavy, consistent dark depth throughout."
    ),
    "resolution": (
        "Lingering cinematic underscore in D minor. A low sustained cello drone "
        "under high sustained string harmonics that hang unresolved, shimmering "
        "and clearly audible above, an open question that never fully releases. "
        "Designed for seamless background looping under documentary narration. "
        "62 BPM, brooding and suspended, consistent quiet tension throughout."
    ),
    "outro": (
        "Fading cinematic underscore in D minor. Sustained low cello receding "
        "into the distance, with a slow descending harp glissando shimmering "
        "high above. Dark mystery atmosphere with lingering unease that refuses "
        "to resolve. Designed for seamless background looping under documentary "
        "narration. 60 BPM, brooding and haunting, consistent dark throughout."
    ),
}

NOMINAL_DURATION_MS = 60000  # tracks de 60s. fase2b loopea a la duracion del cap.


def build_descriptor(intent: str, base_prompt: str) -> dict:
    negatives = ", ".join(NEGATIVE_GLOBAL_STYLES)
    prompt_used = f"{base_prompt.rstrip('.')}. STRICTLY AVOID: {negatives}."
    now = datetime.now().isoformat()
    track_id = f"{intent}_curated"
    return {
        "track_id": track_id,
        "mp3_filename": f"{track_id}.mp3",
        "intent_origin": intent,
        "fits_intents": [intent],
        "compatible_profiles": [ACTIVE_AUDIO_PROFILE],
        "topic_source": "curated_chat36",
        "topic_title": "Curated palette chat 36",
        "prompt_used": prompt_used,
        "duration_ms": NOMINAL_DURATION_MS,
        "cost_usd": None,
        "generated_at": now,
        "approved_at": now,
        "elevenlabs_metadata": {
            "title": None,
            "description": f"Curated {intent} track (chat 36): cello bed + high audible color.",
            "genres": ["dark ambient", "cinematic", "documentary underscore"],
            "composition_plan": {},
        },
        "times_used": 0,
        "last_used_at": None,
    }


def main() -> int:
    # Sanity: los 7 winners existen
    missing = [f for f in WINNERS.values() if not (SOURCE_DIR / f).exists()]
    if missing:
        print(f"[FAIL] faltan winners en {SOURCE_DIR}: {missing}")
        return 1

    LIBRARY_DIR.mkdir(parents=True, exist_ok=True)

    # Guard anti doble-corrida
    already = list(LIBRARY_DIR.glob("*_curated.*"))
    if already:
        print(f"[FAIL] ya hay {len(already)} archivos *_curated en library. "
              f"Ya se promovio. Si querés rehacer, limpiá audio_library/ a mano.")
        return 1

    # 1. Retirar library vieja a backup (MOVER, no borrar)
    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    moved = 0
    for p in sorted(LIBRARY_DIR.iterdir()):
        if not p.is_file():
            continue
        dest = BACKUP_DIR / p.name
        if dest.exists():
            p.unlink()  # backup ya lo tiene de una corrida previa
        else:
            shutil.move(str(p), str(dest))
        moved += 1
    print(f"[ok] library vieja retirada a {BACKUP_DIR.name}: {moved} archivos")

    # 2. Promover los 7 curados
    for intent, src_name in WINNERS.items():
        track_id = f"{intent}_curated"
        shutil.copy2(str(SOURCE_DIR / src_name), str(LIBRARY_DIR / f"{track_id}.mp3"))
        desc = build_descriptor(intent, PROMPTS[intent])
        (LIBRARY_DIR / f"{track_id}.json").write_text(
            json.dumps(desc, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        print(f"[ok] {intent}: {src_name} -> {track_id}.mp3 (+ .json)")

    # 3. Verificacion
    print("\n--- VERIFICACION ---")
    library = _load_library()
    print(f"_load_library() ve {len(library)} tracks (esperado 7)")
    all_ok = len(library) == 7
    for intent in WINNERS:
        cands = _filter_candidates(library, intent, ACTIVE_AUDIO_PROFILE)
        n = len(cands)
        flag = "OK" if n == 1 else "XX"
        print(f"  [{flag}] {intent}: {n} candidato(s) para profile={ACTIVE_AUDIO_PROFILE}")
        if n != 1:
            all_ok = False

    print(f"\n{'PASS' if all_ok else 'FAIL'} - 7 curados, 1 candidato por intent")
    if all_ok:
        print("Library lista. m07 va a reusar estos 7 idénticos al byte, sin regenerar.")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
