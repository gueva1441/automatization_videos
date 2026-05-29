"""
test_edge_density.py — Mide complejidad visual con Canny edge density.
Sin IA, sin API. ~50ms por imagen.
"""
import json
from pathlib import Path
import cv2

ASSETS_DIR = Path(
    r"C:\CLAUDE_PROJECTS\automatization_videos\output"
    r"\7b52de57-eee6-4018-ac25-8357e9779d92\assets"
)
OUTPUT_JSON = Path(r"C:\CLAUDE_PROJECTS\automatization_videos\edge_density_scores.json")


def edge_density(img_path: Path) -> float:
    """Devuelve el % de pixels que son borde según Canny. 0-100."""
    img = cv2.imread(str(img_path), cv2.IMREAD_GRAYSCALE)
    if img is None:
        return -1.0
    edges = cv2.Canny(img, 100, 200)
    return float((edges > 0).mean() * 100)


def main():
    images = sorted(ASSETS_DIR.glob("*.png"))
    if not images:
        print(f"No hay .png en {ASSETS_DIR}")
        return

    results = [(p.name, edge_density(p)) for p in images]
    results.sort(key=lambda x: -x[1])  # descendente

    print("=" * 50)
    print(f"  Edge density (Canny) — {len(results)} imágenes")
    print("=" * 50)
    for name, score in results:
        print(f"  {score:5.2f}%   {name}")
    print("=" * 50)

    OUTPUT_JSON.write_text(
        json.dumps([{"image": n, "edge_density": s} for n, s in results], indent=2),
        encoding="utf-8",
    )
    print(f"  Guardado: {OUTPUT_JSON}")


if __name__ == "__main__":
    main()