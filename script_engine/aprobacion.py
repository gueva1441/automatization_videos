"""
script_engine/aprobacion.py — F33 §B: la compuerta del render. Sin guion de pantalla aprobado no hay `fase2b --gfx`.

Omar aprueba el guion (`fase2b <topic> --aprobar-guion "<quién> <fecha>"`, que CC corre solo cuando el prompt de Omar
dice literalmente «aprobado»): en `output/<topic>/GUION_PANTALLA.json` queda `aprobado: {por, fecha, md5_planes,
planes}`, con el md5 conjunto de los `gfx_plan_chNN.resolved.json` del topic en ese momento. Cualquier `--plan-edit` o
regeneración posterior la invalida: `--plan-only` reescribe el guion (sin `aprobado`) y, si los planes cambian, el md5
ya no coincide. El hook `.claude/hooks/guard_render.py` usa `estado()` antes de dejar pasar un `fase2b --gfx`.
Solo biblioteca estándar (lo carga el hook, que corre con `python -I`).
"""
from __future__ import annotations

import hashlib
import json
import time
from pathlib import Path

GUION = "GUION_PANTALLA.json"
PLANES = "gfx_plan_ch*.resolved.json"


def planes(topic_dir: Path) -> list[Path]:
    return sorted((Path(topic_dir) / "_fase2b_work").glob(PLANES))


def md5_planes(topic_dir: Path) -> str | None:
    """md5 conjunto de los planes resueltos del topic (nombre y bytes de cada uno, en orden); None si no hay planes."""
    fs = planes(topic_dir)
    if not fs:
        return None
    h = hashlib.md5()
    for f in fs:
        h.update(f.name.encode("utf-8") + b"\0" + f.read_bytes() + b"\0")
    return h.hexdigest()


def aprobar(topic_dir: Path, por: str, fecha: str | None = None) -> dict:
    """Escribe el bloque `aprobado` en el guion del topic. Falla si no hay guion, si no hay planes o si algún plan es más
    nuevo que el guion (el guion no describe los planes de hoy: hay que regenerarlo con --plan-only)."""
    topic_dir = Path(topic_dir)
    g = topic_dir / GUION
    if not g.exists():
        raise RuntimeError(f"no existe {g}: generar el guion con `fase2b {topic_dir.name} --plan-only --rotulista`")
    fs = planes(topic_dir)
    if not fs:
        raise RuntimeError(f"no hay planes resueltos en {topic_dir / '_fase2b_work'}")
    viejos = [f.name for f in fs if f.stat().st_mtime > g.stat().st_mtime]
    if viejos:
        raise RuntimeError(f"hay planes más nuevos que el guion ({', '.join(viejos)}): regenerar con --plan-only")
    data = json.loads(g.read_text(encoding="utf-8"))
    data["aprobado"] = {"por": por, "fecha": fecha or time.strftime("%Y-%m-%d %H:%M"), "md5_planes": md5_planes(topic_dir),
                        "planes": [f.name for f in fs]}
    g.write_text(json.dumps(data, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    return data["aprobado"]


def estado(topic_dir: Path) -> tuple[bool, str]:
    """(aprobado y vigente, motivo). Vigente = el guion tiene `aprobado` y los planes de hoy dan el mismo md5."""
    topic_dir = Path(topic_dir)
    g = topic_dir / GUION
    if not g.exists():
        return False, f"no existe {g.as_posix()} (generarlo con `fase2b {topic_dir.name} --plan-only --rotulista`)"
    try:
        ap = json.loads(g.read_text(encoding="utf-8")).get("aprobado")
    except (OSError, ValueError) as e:
        return False, f"{g.name} ilegible ({type(e).__name__})"
    if not ap:
        return False, (f"el guion de {topic_dir.name} no está aprobado (Omar lo aprueba; CC corre "
                       f"`fase2b {topic_dir.name} --aprobar-guion \"Omar <fecha>\"` solo si su prompt dice «aprobado»)")
    hoy = md5_planes(topic_dir)
    if hoy != ap.get("md5_planes"):
        return False, (f"los planes cambiaron después de la aprobación de {ap.get('por')} ({ap.get('fecha')}): md5 "
                       f"aprobado {str(ap.get('md5_planes'))[:8]}…, hoy {str(hoy)[:8]}… — regenerar el guion y volver a aprobar")
    return True, f"guion aprobado por {ap.get('por')} ({ap.get('fecha')}), planes {str(hoy)[:8]}…"
