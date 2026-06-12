"""
fase3.py — Empaquetado de publicación (runner fino). El eslabón que sigue a fase2b.

m09a deja de ser una isla: fase3 resuelve el video terminado (status DONE en topics_db),
abre el FORM de m09 como gate humano, y al primer COMPONER exitoso marca el topic PACKAGED.
El upload sigue MANUAL (Omar en Studio); m09b (API) es otro chat — fase3 nace con el enchufe.

USO:
    python fase3.py <topic_id>           # empaqueta ese video (lanza el form)
    python fase3.py                      # menú: topics DONE sin empaquetar
    python fase3.py <id> --headless --candidates [...]   # passthrough al CLI de m09 (sin form)
    python fase3.py <id> --headless --compose --base ... --text ... [...]

Regla clave: el MP4 sale de topics_db.video_path (fuente de verdad), NUNCA de la convención
{id}_final.mp4 (nombre volátil que fase2b pisa). El CHECKLIST se escribe con ESE path.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from script_engine import topics_db
from script_engine import m09_packaging as m09

DONE_STATUS = "video_generated"   # mismo contrato que fase2b


def _resolve_video(topic_id: str) -> tuple[dict, str]:
    """Devuelve (topic, video_path) o lanza ValueError con mensaje claro."""
    topic = topics_db.get_topic_by_id(topic_id)
    if topic is None:
        raise ValueError(f"'{topic_id}' no existe en topics_db.")
    if topic.get("status") != DONE_STATUS:
        raise ValueError(
            f"'{topic_id}' no tiene video terminado por fase2b "
            f"(status='{topic.get('status')}', se esperaba '{DONE_STATUS}')."
        )
    video_path = topic.get("video_path")
    if not video_path:
        raise ValueError(f"'{topic_id}' está DONE pero sin video_path registrado en topics_db.")
    if not Path(video_path).exists():
        raise ValueError(f"El video registrado no existe en disco: {video_path}")
    return topic, video_path


def _volatile_warning(video_path: str) -> str | None:
    """Avisa si el path registrado es el nombre volátil {id}_final.mp4 mientras existe un
    artefacto de nombre estable (..._final_*_ZOOM.mp4) en el mismo dir. NO lo arregla."""
    p = Path(video_path)
    if not p.name.endswith("_final.mp4"):
        return None
    stable = sorted(p.parent.glob("*_final_*ZOOM*.mp4"))
    if stable:
        return (f"⚠ video_path registrado es el nombre VOLÁTIL ({p.name}); existe un artefacto "
                f"estable ({stable[0].name}). fase2b pisa el primero en cada corrida. Si querés, "
                f"repuntá topics_db al estable (decisión de Omar — fase3 NO lo toca).")
    return None


def _build_m09_argv(topic_id: str, video_path: str, passthrough: list[str]) -> list[str]:
    """argv para invocar el CLI de m09 en headless (pure/testeable)."""
    return ["-m", "script_engine.m09_packaging", topic_id, "--video-path", video_path, *passthrough]


def _mark_packaged(topic_id: str) -> None:
    newly = not (topics_db.get_topic_by_id(topic_id) or {}).get("packaged")
    topics_db.mark_as_packaged(topic_id)
    if newly:
        print(f"  📦 topics_db: {topic_id} → PACKAGED")


def package(topic_id: str, video_path: str) -> None:
    """Modo normal: genera candidatas si faltan, abre el form; al COMPONER marca PACKAGED."""
    if not m09.candidates_ready(topic_id):
        print("  [fase3] sin candidatas previas → generando metadata + thumbnails (primera vez)…")
        m09.run_candidates(topic_id, video_path=video_path)
    m09.run_review(topic_id, video_path=video_path,
                   on_compose=lambda _name: _mark_packaged(topic_id))


def headless(topic_id: str, video_path: str, passthrough: list[str]) -> int:
    """Passthrough al CLI de m09 (sin form). Si hubo --compose exitoso → PACKAGED."""
    argv = _build_m09_argv(topic_id, video_path, passthrough)
    rc = subprocess.run([sys.executable, *argv]).returncode
    if rc == 0 and "--compose" in passthrough:
        _mark_packaged(topic_id)
    return rc


def _menu() -> str | None:
    """Lista topics DONE sin empaquetar y deja elegir (estilo simple de las otras fases)."""
    pend = topics_db.get_unpackaged_generated()
    if not pend:
        print("  ℹ  No hay topics DONE sin empaquetar. Generá un video con fase2b primero.")
        return None
    print("\n  Topics DONE sin empaquetar:")
    for i, t in enumerate(pend, 1):
        title = t.get("video_title") or t.get("title") or "(sin título)"
        print(f"    [{i}] {t.get('id')} — {title}")
    try:
        raw = input("\n  Elegí número (Enter para salir): ").strip()
    except EOFError:
        return None
    if not raw.isdigit() or not (1 <= int(raw) <= len(pend)):
        print("  (salida)")
        return None
    return pend[int(raw) - 1].get("id")


def main() -> int:
    ap = argparse.ArgumentParser(description="fase3 — empaquetado de publicación (post fase2b).")
    ap.add_argument("topic_id", nargs="?", default=None)
    ap.add_argument("--headless", action="store_true",
                    help="No abre el form: pasa el resto de flags al CLI de m09.")
    args, passthrough = ap.parse_known_args()

    topic_id = args.topic_id
    if not topic_id:
        if args.headless:
            ap.error("--headless requiere un topic_id explícito.")
        topic_id = _menu()
        if not topic_id:
            return 0

    try:
        _topic, video_path = _resolve_video(topic_id)
    except ValueError as e:
        print(f"  ❌ {e}")
        return 1

    warn = _volatile_warning(video_path)
    if warn:
        print(f"  {warn}")
    print(f"  🎬 fase3 — {topic_id}\n     MP4: {video_path}")

    if args.headless:
        return headless(topic_id, video_path, passthrough)
    package(topic_id, video_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
