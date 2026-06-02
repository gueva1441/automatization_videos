"""_smoke_chat38_ch01.py — smoke SEGURO del BLOQUE 5 (chat 38).

Reconstruye los inputs del cap1 desde sync_map.json, PRE-CHEQUEA que el hash de
text_for_tts coincide con el guardado (→ generate_chapter_assets REUSA el mp3, NO
regenera audio = no gasta TTS), borra solo ts+alignment, y corre el paso de audio
integrado (que ahora usa Forced Alignment). Valida el output real contra
_chars_to_syllables. Gasta ~centavos de Forced Alignment (1 llamada).
"""
import hashlib
import json
from pathlib import Path

import audio_manager as am
from config import OUTPUT_DIR
from fase2b import _chars_to_syllables

VID = "8286b193-ff82-4357-b32d-21ca30909c4d"
audio_dir = OUTPUT_DIR / "audio" / VID

sm = json.loads((audio_dir / "sync_map.json").read_text(encoding="utf-8"))
ch01 = next(c for c in sm["chapters"] if c["id"] == "ch01")
raw_text = ch01["text"]
voice_id = sm["voice_id"]
voice_settings = ch01.get("voice_settings_applied") or sm["voice_settings"]

# ── PRE-CHECK de seguridad: si el hash no coincide, ABORTAR antes de gastar ──
t4t = am._resolve_text_for_tts(
    chapter_id="ch01", raw_text=raw_text, video_id=VID, language="es"
)
h = hashlib.md5(t4t.encode("utf-8")).hexdigest()[:12]
stored = json.loads((audio_dir / "ch01.meta.json").read_text(encoding="utf-8"))["text_hash"]
print(f"[precheck] text_for_tts hash={h}  stored={stored}")
assert h == stored, "HASH MISMATCH → generate_chapter_assets regeneraría audio. ABORTO (no gasto TTS)."
print("[precheck] OK → el audio se REUSA, no se regenera. Procediendo.\n")

# ── Borrar solo timestamps + alignment del cap1 (NO el mp3) ──
(audio_dir / "ch01_timestamps.json").unlink(missing_ok=True)
(audio_dir / "ch01_alignment.json").unlink(missing_ok=True)
print("[setup] ch01_timestamps.json + ch01_alignment.json borrados\n")

# ── Paso de audio integrado (ahora vía Forced Alignment) ──
entry = am.generate_chapter_assets(
    chapter={"id": "ch01", "text": raw_text},
    video_id=VID,
    voice_id=voice_id,
    voice_settings=voice_settings,
    skip_if_exists=True,
)
print(f"\n[result] entry: dur={entry['duration_sec']}s words={entry['word_count']}\n")

# ── Verificaciones ──
align_path = audio_dir / "ch01_alignment.json"
ts_path = audio_dir / "ch01_timestamps.json"
print("alignment.json creado:", align_path.exists())
chars = json.loads(align_path.read_text(encoding="utf-8"))
print("characters count:", len(chars))
print("character[0] keys:", sorted(chars[0].keys()) if chars else "(vacío)")
print("character[0]:", chars[0] if chars else None)

words = json.loads(ts_path.read_text(encoding="utf-8"))
print("timestamps[0] keys:", sorted(words[0].keys()) if words else "(vacío)")
print("timestamps[0]:", words[0] if words else None)

# ── _chars_to_syllables sobre los characters REALES de la API ──
syl = _chars_to_syllables(chars)
print(f"\n_chars_to_syllables sobre characters reales → {len(syl)} sílabas")
print("primeras 8:", [s["text"] for s in syl[:8]])
mono = all(syl[k]["start"] >= syl[k - 1]["start"] for k in range(1, len(syl)))
print("monotonía start no-decreciente:", mono)
print("cobertura: 1a sílaba start ==", syl[0]["start"], "| 1er char start ==", chars[0]["start"])
