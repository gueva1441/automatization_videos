"""
patch_sync_map_mixing.py — Patch quirúrgico atómico del bloque mixing
del sync_map.json de Pripyat. Lee config activo, reescribe solo mixing.
NO toca audio, timestamps, ni texto. Backup automático antes de tocar.

Descartable después de chat 28.
"""
import json
from pathlib import Path
from audio_profiles import AUDIO_PROFILES
from audio_config import ACTIVE_AUDIO_PROFILE

VIDEO_ID = "7b52de57-eee6-4018-ac25-8357e9779d92"

sync_map_path = Path("output") / "audio" / VIDEO_ID / "sync_map.json"
backup_path = sync_map_path.with_suffix(".json.bak_pre_chat28_mixing_patch")

# Backup
backup_path.write_bytes(sync_map_path.read_bytes())
print(f"Backup: {backup_path.name}")

# Leer
sm = json.loads(sync_map_path.read_text(encoding="utf-8"))
old_mixing = sm.get("mixing", {})

# Reemplazar mixing por el del config activo
new_mixing = AUDIO_PROFILES[ACTIVE_AUDIO_PROFILE]["mixing"]
sm["mixing"] = new_mixing

# Persistir
sync_map_path.write_text(
    json.dumps(sm, ensure_ascii=False, indent=2),
    encoding="utf-8",
)

print(f"ACTIVE_AUDIO_PROFILE: {ACTIVE_AUDIO_PROFILE}")
print(f"Antes ({len(old_mixing)} keys):")
print(json.dumps(old_mixing, indent=2))
print(f"Despues ({len(new_mixing)} keys):")
print(json.dumps(new_mixing, indent=2))
print("OK")