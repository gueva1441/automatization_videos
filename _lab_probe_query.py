"""
_lab_probe_query.py — LAB: ver EXACTAMENTE lo que trae el scrape de prod para un query EN.

NO toca producción. NO escribe en data/. Usa la MISMA función que el pipeline real
(search_viral_english de youtube_scanner) para que veas lo mismo que ve prod —
no una imitación del navegador.

Sirve para validar: ¿el viral EN que trajo cierto query tiene el nombre propio en el
título (ej. "Corpsewood"), o el título es genérico ("abandoned house in Georgia")?

USO:
    python _lab_probe_query.py "abandoned places mysterious history"
    python _lab_probe_query.py "forbidden abandoned military bases" --limit 30
    python _lab_probe_query.py "ghost towns unexplained disappearance" --grep georgia

    --limit N   : cuántos videos inspeccionar (default 30)
    --grep STR  : resaltar/filtrar títulos que contengan STR (case-insensitive)
    --out PATH  : ruta del JSON de salida (default: data/_probe_<slug>.json)

Salida:
    - Tabla en consola (título, views, video_id, canal, idioma detectado).
    - JSON con la lista completa cruda, para inspección/diff.
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# MISMO código que prod — no reimplementamos nada
from script_engine.youtube_scanner import (
    search_viral_english,
    detect_language,
)

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "data"


def _slug(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", s.lower()).strip("_")[:40]


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("query", help="query EN exacto a probar (entre comillas)")
    ap.add_argument("--limit", type=int, default=30, help="videos a inspeccionar")
    ap.add_argument("--grep", default=None, help="resaltar títulos que contengan este texto")
    ap.add_argument("--out", default=None, help="ruta del JSON de salida")
    args = ap.parse_args()

    print(f"\n{'═' * 78}")
    print(f"  LAB PROBE QUERY — código real de prod (search_viral_english)")
    print(f"  query: '{args.query}'  ·  limit: {args.limit}")
    print(f"{'═' * 78}\n")

    # Llamada IDÉNTICA a la que hace niche_discoverer en el flujo spy-arbitrage
    results = search_viral_english(args.query, min_views=0, limit=args.limit)

    if not results:
        print("  ⚠ El scrape no devolvió nada (posible fallo de red/proxy o query sin resultados).")
        return 1

    print(f"  → {len(results)} videos crudos del scrape\n")
    grep = (args.grep or "").lower()

    # Tabla
    print(f"  {'#':>3}  {'views':>11}  {'lang':<5}  {'video_id':<13}  título")
    print("  " + "─" * 96)
    for i, v in enumerate(results, 1):
        title = v.get("title", "")
        lang = detect_language(title)
        vid = v.get("video_id", "")
        mark = ""
        if grep and grep in title.lower():
            mark = "  ← MATCH"
        t = (title[:60] + "…") if len(title) > 61 else title
        print(f"  {i:>3}  {v.get('views', 0):>11,}  {lang:<5}  {vid:<13}  {t}{mark}")

    # Si hay grep, resumen aparte de los matches con título COMPLETO
    if grep:
        matches = [v for v in results if grep in v.get("title", "").lower()]
        print(f"\n  {'─' * 50}")
        print(f"  Coincidencias con '{args.grep}': {len(matches)}")
        for v in matches:
            print(f"    • TÍTULO COMPLETO: {v.get('title')}")
            print(f"      views={v.get('views', 0):,}  video_id={v.get('video_id')}  "
                  f"canal={v.get('channel_name', '?')}")

    # JSON crudo
    out_path = Path(args.out) if args.out else (DATA_DIR / f"_probe_{_slug(args.query)}.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "probed_at": datetime.now().isoformat(),
        "query": args.query,
        "limit": args.limit,
        "count": len(results),
        "results": results,   # lista cruda tal cual la devuelve prod
    }
    out_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n  💾 JSON crudo escrito en: {out_path}")
    print(f"     (abrilo para ver el título EXACTO de cada video)\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
