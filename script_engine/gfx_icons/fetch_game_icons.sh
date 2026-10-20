#!/usr/bin/env bash
# F4b §4: descarga UNA vez el set SVG de game-icons.net (CC BY 3.0) desde su repo oficial, fuera de git.
# Destino: script_engine/gfx_runtime/icons/game-icons/  (ignorado por .gitignore). Re-correr = actualizar.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
DST="$ROOT/script_engine/gfx_runtime/icons/game-icons"
if [ -d "$DST/.git" ]; then
  git -C "$DST" pull --ff-only
else
  git clone --depth 1 https://github.com/game-icons/icons "$DST"
fi
find "$DST" -name "*.svg" | wc -l
