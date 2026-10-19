"""shot.py — captura de una página HTML local con el chrome-headless-shell de HyperFrames (sin red)."""
from __future__ import annotations

import subprocess
from pathlib import Path

CHROME_GLOB = "chrome/chrome-headless-shell/*/chrome-headless-shell-win64/chrome-headless-shell.exe"


def chrome() -> Path:
    found = sorted((Path.home() / ".cache" / "hyperframes").glob(CHROME_GLOB))
    if not found:
        raise FileNotFoundError("chrome-headless-shell de HyperFrames no encontrado (correr `hyperframes doctor`)")
    return found[-1]


def screenshot(html: Path, png: Path, width: int, height: int) -> Path:
    """HTML → PNG del tamaño pedido (fondo transparente desactivado: lo pone la página)."""
    png.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([str(chrome()), "--headless", "--disable-gpu", "--hide-scrollbars", "--allow-file-access-from-files",
                    f"--window-size={width},{height}", f"--screenshot={png}", html.resolve().as_uri()],
                   check=True, capture_output=True, timeout=180)
    return png
