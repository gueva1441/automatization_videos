"""
report_foto_madre_edits.py — sidecar de telemetría (HANDOFF_133 + pedido de Omar).

Deja un JSON con la LISTA de todas las imágenes que, por corrida, usaron la foto madre
(o sea, salieron por /edit anclado). Lee los `assets_manifest.json` de cada corrida y
marca las imágenes con `foto_madre_refs` no vacías — ESE es el signal fiable de "usó la
madre", grabado bien incluso en manifests viejos (pre-fix del endpoint).

Escribe:
  - por corrida:  output/<video_id>/assets/foto_madre_edits.json
  - índice combinado: output/foto_madre_edits.json

NO llama a fal, NO re-renderiza, NO toca el ruteo. Solo lee manifests y escribe JSON.
El campo `endpoint_recorded` sale del manifest tal cual; `stale_telemetry=true` marca las
imágenes ancladas cuyo manifest viejo todavía dice "text-to-image" (se corrige al re-render).

USO:
    python report_foto_madre_edits.py                 # todas las corridas
    python report_foto_madre_edits.py --topic <id>    # solo esa corrida
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

from config import OUTPUT_DIR

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")


def _edits_for_manifest(manifest_path: Path) -> dict:
    """Extrae del manifest la lista de imágenes que usaron la foto madre (/edit)."""
    m = json.loads(manifest_path.read_text(encoding="utf-8"))
    video_id = m.get("video_id", manifest_path.parent.parent.name)
    images: list[dict] = []
    total = 0
    for ch in m.get("chapters", []):
        cid = ch.get("id") or ch.get("chapter_id") or "?"
        for img in ch.get("images", []):
            total += 1
            refs = img.get("foto_madre_refs") or []
            if not refs:
                continue
            fm = img.get("flux_meta") or {}
            endpoint = fm.get("endpoint")
            endpoint_is_edit = bool(endpoint and "/edit" in endpoint)
            images.append({
                "chapter": cid,
                "index": img.get("index"),
                "file": Path(img.get("path", "")).name,
                "path": img.get("path"),
                "foto_madre_refs": refs,
                "endpoint_recorded": endpoint,
                "endpoint_is_edit": endpoint_is_edit,
                # ancla confirmada por refs pero el manifest viejo aún dice t2i → se corrige al re-render.
                "stale_telemetry": not endpoint_is_edit,
            })
    return {
        "video_id": video_id,
        "manifest": str(manifest_path).replace("\\", "/"),
        "total_images": total,
        "edit_images": len(images),
        "images": images,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Lista las imágenes /edit (foto madre) por corrida")
    parser.add_argument("--topic", type=str, default=None, help="Solo esta corrida (video_id)")
    args = parser.parse_args()

    stamp = datetime.now().isoformat(timespec="seconds")

    if args.topic:
        manifests = [OUTPUT_DIR / args.topic / "assets" / "assets_manifest.json"]
    else:
        manifests = sorted(OUTPUT_DIR.glob("*/assets/assets_manifest.json"))

    runs: list[dict] = []
    print(f"{'video_id':<38} {'imgs':>5} {'edit':>5} {'stale':>6}")
    print("─" * 58)
    for mp in manifests:
        if not mp.exists():
            print(f"[skip] no existe {mp}")
            continue
        run = _edits_for_manifest(mp)
        run["generated_at"] = stamp
        # sidecar por corrida (junto al manifest)
        per_run = mp.parent / "foto_madre_edits.json"
        per_run.write_text(json.dumps(run, indent=2, ensure_ascii=False), encoding="utf-8")
        n_stale = sum(1 for i in run["images"] if i["stale_telemetry"])
        print(f"{run['video_id']:<38} {run['total_images']:>5} {run['edit_images']:>5} {n_stale:>6}")
        runs.append({
            "video_id": run["video_id"],
            "total_images": run["total_images"],
            "edit_images": run["edit_images"],
            "stale_telemetry_images": n_stale,
            "per_run_json": str(per_run).replace("\\", "/"),
        })

    index = {"generated_at": stamp, "n_runs": len(runs),
             "total_edit_images": sum(r["edit_images"] for r in runs), "runs": runs}
    index_path = OUTPUT_DIR / "foto_madre_edits.json"
    index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
    print("─" * 58)
    print(f"índice → {index_path}")
    print(f"corridas: {len(runs)} · imágenes /edit totales: {index['total_edit_images']}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
