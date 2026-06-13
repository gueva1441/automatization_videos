"""
run_pipeline.py — Orquestador del pipeline completo (secuenciador por SUBPROCESS).

Encadena las fases del pipeline para UN topic, corriendo cada una como
`python faseX.py …` que HEREDA la terminal → los gates interactivos (m06 [P]/[R]/[E],
normalizer_gate, music_gate, el form de m09) preguntan al humano directo, sin que el
orquestador tenga que manejar stdin.

El tid se threadea EXPLÍCITO a todas las fases (--topic / posicional): nunca se usa el
modo batch de una fase que podría agarrar OTROS topics. Después de cada fase el
orquestador decide si seguir mirando DOS señales: el exit code del subprocess Y el
artefacto en disco (data/scripts/<id>.json, assets_manifest.json, status en topics_db).

NO usa el auto-chain fase1→fase1_5 (ahí el tid queda enterrado dentro de
run_one_topic_from_menu y no se puede secuenciar el resto).

USO:
    python run_pipeline.py --topic <id>           # salta el menú, corre ese topic
    python run_pipeline.py                         # menú de validados → elegís uno
    python run_pipeline.py --topic <id> --batch    # desatendido (fase1_5 --batch, sin form)

Secuencia (asistida):
    GUION (fase1_5) → ASSETS (fase2a) → VIDEO (fase2b) → PACKAGING (fase3, form).

Modo --batch: fase1_5 corre con --batch (3 gates del medio desatendidos) y el
PACKAGING NO levanta el form — solo reporta `python fase3.py <id>` para que Omar
empaquete cuando quiera.

Regla: cualquier exit≠0 o artefacto faltante → frenar, decir en qué fase y por qué,
NO seguir. Reporte final SIEMPRE (fases corridas, dónde frenó, próximo comando).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from config import DATA_DIR, OUTPUT_DIR
from script_engine import topics_db

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PY = sys.executable
VIDEO_DONE_STATUS = "video_generated"


# ═══════════════════════════════════════════════════════════════
#  Artefactos en disco (monkeypatcheables en tests)
# ═══════════════════════════════════════════════════════════════
def _script_path(tid: str) -> Path:
    """data/scripts/<id>.json — lo escribe m06 (assemble_final_script) al final del guion."""
    return DATA_DIR / "scripts" / f"{tid}.json"


def _manifest_path(tid: str) -> Path:
    """output/<id>/assets/assets_manifest.json — lo escribe fase2a (asset_manager)."""
    return OUTPUT_DIR / tid / "assets" / "assets_manifest.json"


def _video_status(tid: str) -> str | None:
    """Status del topic en topics_db. fase2b lo promueve a 'video_generated'."""
    t = topics_db.get_topic_by_id(tid)
    return (t or {}).get("status")


def _mtime(p: Path) -> float | None:
    return p.stat().st_mtime if p.exists() else None


# ═══════════════════════════════════════════════════════════════
#  Corredor de fase (subprocess heredando la terminal)
# ═══════════════════════════════════════════════════════════════
def _run(cmd: list[str]) -> int:
    """Corre `python <cmd…>` heredando stdin/stdout/stderr (gates interactivos van al
    humano directo). Devuelve el returncode."""
    return subprocess.run([PY, *cmd]).returncode


# ═══════════════════════════════════════════════════════════════
#  Reporte
# ═══════════════════════════════════════════════════════════════
def _report(tid: str, ran: list[str], *, stopped_at: str | None,
            why: str | None, next_cmd: str | None) -> None:
    print(f"\n{'═' * 60}")
    print(f"  📊 RUN_PIPELINE — {tid}")
    print(f"{'═' * 60}")
    print(f"  Fases corridas: {', '.join(ran) if ran else '(ninguna)'}")
    if stopped_at:
        print(f"  ⛔ Frenó en: {stopped_at}")
        if why:
            print(f"     Motivo: {why}")
    else:
        print(f"  ✅ Cadena completa.")
    if next_cmd:
        print(f"  ➡  Próximo comando: {next_cmd}")
    print(f"{'═' * 60}\n")


# ═══════════════════════════════════════════════════════════════
#  Secuencia
# ═══════════════════════════════════════════════════════════════
def sequence(tid: str, *, batch: bool = False) -> int:
    """Corre la cadena para `tid`. Devuelve exit code (0 ok, 1 frenó en alguna fase).

    `batch` (Commit 2): pasa --batch a fase1_5 (gates del medio desatendidos) y, en
    PACKAGING, NO levanta el form — solo reporta el comando de fase3.
    """
    ran: list[str] = []

    def _phase_header(name: str) -> None:
        print(f"\n{'─' * 60}\n  ▶ {name} — {tid}\n{'─' * 60}")

    # ── 1) GUION — fase1_5 ──────────────────────────────────────
    _phase_header("GUION (fase1_5)")
    before = _mtime(_script_path(tid))
    ran.append("guion")
    fase1_5_cmd = ["fase1_5.py", "--topic", tid] + (["--batch"] if batch else [])
    rc = _run(fase1_5_cmd)
    if rc != 0:
        _report(tid, ran, stopped_at="GUION",
                why=f"fase1_5 exit {rc}",
                next_cmd=f"python {' '.join(fase1_5_cmd)}")
        return 1
    sp = _script_path(tid)
    if not sp.exists() or _mtime(sp) == before:
        _report(tid, ran, stopped_at="GUION",
                why=f"m06 quedó en [R]/[E]; cadena detenida en guion "
                    f"(sin {sp.as_posix()} fresco)",
                next_cmd=f"python {' '.join(fase1_5_cmd)} --from m06")
        return 1

    # ── 2) ASSETS — fase2a ──────────────────────────────────────
    _phase_header("ASSETS (fase2a)")
    ran.append("assets")
    rc = _run(["fase2a.py", "--topic", tid])
    if rc != 0:
        _report(tid, ran, stopped_at="ASSETS",
                why=f"fase2a exit {rc}",
                next_cmd=f"python fase2a.py --topic {tid}")
        return 1
    mf = _manifest_path(tid)
    if not mf.exists():
        _report(tid, ran, stopped_at="ASSETS",
                why=f"fase2a no dejó {mf.as_posix()}",
                next_cmd=f"python fase2a.py --topic {tid}")
        return 1

    # ── 3) VIDEO — fase2b (video_id posicional == topic_id en LONG) ──
    _phase_header("VIDEO (fase2b)")
    ran.append("video")
    rc = _run(["fase2b.py", tid])
    if rc != 0:
        _report(tid, ran, stopped_at="VIDEO",
                why=f"fase2b exit {rc}",
                next_cmd=f"python fase2b.py {tid}")
        return 1
    status = _video_status(tid)
    if status != VIDEO_DONE_STATUS:
        _report(tid, ran, stopped_at="VIDEO",
                why=f"topics_db status='{status}' (se esperaba '{VIDEO_DONE_STATUS}')",
                next_cmd=f"python fase2b.py {tid}")
        return 1

    # ── 4) PACKAGING — fase3 ────────────────────────────────────
    if batch:
        # Batch: NO levantar el form (gate humano). Se reporta y queda listo.
        ran.append("packaging (diferido)")
        _report(tid, ran, stopped_at=None, why=None,
                next_cmd=None)
        print(f"  📦 LISTO PARA PACKAGING → python fase3.py {tid}\n")
        return 0

    _phase_header("PACKAGING (fase3 — form)")
    ran.append("packaging")
    rc = _run(["fase3.py", tid])
    if rc != 0:
        _report(tid, ran, stopped_at="PACKAGING",
                why=f"fase3 exit {rc}",
                next_cmd=f"python fase3.py {tid}")
        return 1

    _report(tid, ran, stopped_at=None, why=None, next_cmd=None)
    return 0


# ═══════════════════════════════════════════════════════════════
#  Resolución de tid + CLI
# ═══════════════════════════════════════════════════════════════
def _resolve_tid(explicit: str | None) -> str | None:
    """--topic → directo. Sino, menú interactivo de validados (reusa fase1_5)."""
    if explicit:
        return explicit
    from fase1_5 import _select_topic_interactive
    return _select_topic_interactive()


def main() -> int:
    ap = argparse.ArgumentParser(
        description="run_pipeline — secuenciador subprocess del pipeline (1 topic).")
    ap.add_argument("--topic", type=str, default=None,
                    help="Topic_id a correr. Sin esto, abre el menú de validados.")
    ap.add_argument("--batch", action="store_true",
                    help="Desatendido: fase1_5 corre con --batch (gates del medio "
                         "desactivados) y el PACKAGING no levanta el form (solo reporta).")
    args = ap.parse_args()

    tid = _resolve_tid(args.topic)
    if not tid:
        print("\n  Cancelado (sin tema elegido).")
        return 0

    return sequence(tid, batch=args.batch)


if __name__ == "__main__":
    raise SystemExit(main())
