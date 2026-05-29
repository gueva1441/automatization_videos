"""
_test_elevenlabs_music_probe.py — UNA llamada al endpoint Music detailed
para inspeccionar el schema REAL del response. Descartable después de chat 25.

Cost: ~$0.40 (30s de música a $0.80/min).
Endpoint: POST https://api.elevenlabs.io/v1/music/detailed
"""

import json
from email.parser import BytesParser
from email.policy import default
from pathlib import Path

import requests

from config import APIConfig

cfg = APIConfig()

print("[probe] POST https://api.elevenlabs.io/v1/music/detailed")
print("[probe] prompt: dark ambient drone | length 30s | force_instrumental=True")
print()

resp = requests.post(
    "https://api.elevenlabs.io/v1/music/detailed",
    headers={
        "xi-api-key": cfg.elevenlabs_api_key,
        "Accept": "multipart/mixed",
    },
    json={
        "prompt": (
            "Soft cinematic ambient drone, sustained sub-bass, slow swelling "
            "tension. 60 BPM. No drums, no melody hooks. Designed for "
            "documentary narration background."
        ),
        "music_length_ms": 30000,
        "model_id": "music_v1",
        "force_instrumental": True,
    },
    timeout=180,
)

print(f"[probe] HTTP {resp.status_code}")
print(f"[probe] Content-Type header: {resp.headers.get('Content-Type')}")
print(f"[probe] Total response size: {len(resp.content)} bytes")
print()

if resp.status_code != 200:
    print(f"[probe] ERROR body (first 1000 chars):")
    print(resp.text[:1000])
    raise SystemExit(1)

# Parsear multipart/mixed con email.parser (stdlib)
content_type = resp.headers.get("Content-Type", "")
raw = f"Content-Type: {content_type}\r\n\r\n".encode() + resp.content

parser = BytesParser(policy=default)
msg = parser.parsebytes(raw)

parts = list(msg.iter_parts())
print(f"[probe] Multipart parts encontradas: {len(parts)}")
print()

mp3_data = None
metadata_json = None

for i, part in enumerate(parts, 1):
    part_ct = part.get_content_type()
    print(f"=== PART {i} ===")
    print(f"  Content-Type: {part_ct}")
    cd = part.get("Content-Disposition", "(none)")
    print(f"  Content-Disposition: {cd}")

    payload = part.get_payload(decode=True)
    size = len(payload) if payload else 0
    print(f"  Payload size: {size} bytes")

    if "json" in part_ct.lower() and payload:
        try:
            metadata_json = json.loads(payload)
            print(f"  >>> JSON METADATA <<<")
            print(json.dumps(metadata_json, indent=2, ensure_ascii=False))
        except json.JSONDecodeError as e:
            print(f"  ERROR parsing JSON: {e}")
            print(f"  Raw payload (first 500 chars): {payload[:500]!r}")
    elif payload and (
        "audio" in part_ct.lower()
        or "mpeg" in part_ct.lower()
        or "octet" in part_ct.lower()
    ):
        mp3_data = payload
        out_path = Path("_probe_test_track.mp3")
        out_path.write_bytes(mp3_data)
        print(f"  >>> AUDIO BINARY ({size} bytes) — guardado en {out_path}")
    print()

print("=" * 60)
print("RESUMEN")
print("=" * 60)
print(f"MP3 generado: {'_probe_test_track.mp3' if mp3_data else 'NO'}")
print(f"JSON metadata recibido: {'SÍ' if metadata_json else 'NO'}")
if metadata_json:
    print(f"Top-level keys del metadata: {list(metadata_json.keys())}")
print()
print(f"[probe] Costo aproximado: $0.40 (30s @ $0.80/min)")
print(f"[probe] Cuando termine inspección: borrá _probe_test_track.mp3 y este script.")