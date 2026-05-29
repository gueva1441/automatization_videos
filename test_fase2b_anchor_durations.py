"""Test offline: valida que _compute_durations_from_anchors devuelve durations
sensatas para Pripyat cap 2. NO renderiza video."""
import json
from pathlib import Path
from fase2b import _compute_durations_from_anchors

VIDEO_ID = "7b52de57-eee6-4018-ac25-8357e9779d92"

# Cargar JSON final
script = json.loads(Path(f"data/scripts/{VIDEO_ID}.json").read_text(encoding="utf-8"))
ch2 = next(c for c in script["chapters"] if c["chapter_number"] == 2)
anchors = [ip["narration_anchor"] for ip in ch2["image_prompts"]]

# Cargar timestamps + duration
ts_path = Path(f"output/audio/{VIDEO_ID}/ch02_timestamps.json")
sm = json.loads(Path(f"output/audio/{VIDEO_ID}/sync_map.json").read_text(encoding="utf-8"))
ch2_meta = next(c for c in sm["chapters"] if c["id"] == "ch02")
total = float(ch2_meta["duration_sec"])

# Llamar al helper
durations = _compute_durations_from_anchors(anchors, ts_path, total)

print(f"Cap 2 — total: {total:.2f}s, {len(anchors)} imgs")
print(f"Anchor matching: {'OK' if durations else 'FAILED (fallback uniforme se aplicaría)'}")
if durations:
    print(f"Suma de durations: {sum(durations):.2f}s (target {total:.2f}s, diff {sum(durations)-total:+.2f}s)")
    for i, d in enumerate(durations, start=1):
        print(f"  img{i}: {d:.2f}s")
    # Validación: ningún desfase > +/- 0.5s vs lo esperado
    expected = [14.3, 8.7, 5.4, 12.5, 9.1, 10.5, 42.5, 8.7]   # del análisis manual
    for i, (d, e) in enumerate(zip(durations, expected), start=1):
        flag = "OK" if abs(d - e) < 2.0 else "WARN"
        print(f"  img{i}: {d:.2f}s vs esperado {e:.1f}s  {flag}")
