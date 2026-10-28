"""
run_pipeline.py — Orquestador del pipeline completo (secuenciador por SUBPROCESS).

Encadena las fases del pipeline para UN topic, corriendo cada una como
`python faseX.py …` que HEREDA la terminal (el form de m09 en fase3 pregunta al humano
directo, sin que el orquestador tenga que manejar stdin).

El tid se threadea EXPLÍCITO a todas las fases (--topic / posicional): nunca se usa el
modo batch de una fase que podría agarrar OTROS topics. Después de cada fase el
orquestador decide si seguir mirando DOS señales: el exit code del subprocess Y el
artefacto en disco (`etapa_de`, de solo lectura).

NO usa el auto-chain fase1→fase1_5 (ahí el tid queda enterrado dentro de
run_one_topic_from_menu y no se puede secuenciar el resto).

USO:
    python run_pipeline.py --topic <id>           # retoma ese topic donde quedó
    python run_pipeline.py                         # menú de validados → elegís uno
    python run_pipeline.py --topic <id> --batch    # igual, y PACKAGING no levanta el form

Secuencia (F41, DECISIONES 2026-10-27 20:59) — una sola cadena:
    GUION (fase1_5 --batch: la cadena de F39 hasta el papel) → PAPEL (compuerta) →
    VOZ (fase1_5 --from normalizer_gate: voz, música, m03, foto madre, assemble) →
    ASSETS (fase2a) → VISOR (solo form) → FONDOS (fase2b sin gfx) →
    PANTALLA (fase2b --plan-only + compuerta del guion de pantalla) →
    RENDER (fase2b --reuse-visuals --keep-segments --gfx --gfx-sparse) → PACKAGING (fase3).

Retomar: cada corrida arranca en la primera etapa que falta según los artefactos en disco
(`etapa_de`); una etapa hecha no se vuelve a correr. Las dos compuertas (papel y guion de
pantalla) NUNCA se aprueban solas: con el form (QA_FORM) Omar elige A (aprobar) o P (parar);
sin el form la corrida para ahí e imprime los comandos para aprobar y retomar.

Modo --batch: PACKAGING NO levanta el form — solo reporta `python fase3.py <id>`.

Regla: cualquier exit≠0 o artefacto faltante → frenar, decir en qué fase y por qué,
NO seguir. Reporte final SIEMPRE (fases corridas, dónde frenó, próximo comando).
El orquestador no cierra ningún programa de Omar (DECISIONES 2026-10-27 00:30).
"""
from __future__ import annotations

import argparse
import datetime
import json
import subprocess
import sys
from pathlib import Path

from config import DATA_DIR, OUTPUT_DIR
from script_engine import aprobacion, topics_db

# Gate del VISOR fase2.5 (form asistido): marcador env-gated por QA_FORM. Sin QA_FORM
# (terminal pura) NO se emite ni se bloquea → fase2a corre directo a fase2b igual que hoy.
from qa_form_markers import QA_FORM, emit_choice_marker

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

PY = sys.executable


# ═══════════════════════════════════════════════════════════════
#  Artefactos en disco (de solo lectura; monkeypatcheables en tests)
# ═══════════════════════════════════════════════════════════════
def _papel_md_path(tid: str) -> Path:
    """data/scripts/_steps/<id>/01e_pantalla.md — el papel legible que deja fase1_5 (m01e) antes de su PARADA."""
    return DATA_DIR / "scripts" / "_steps" / tid / "01e_pantalla.md"


def _script_path(tid: str) -> Path:
    """data/scripts/<id>.json — lo escribe fase1_5 (`--from normalizer_gate`) vía assemble_final_script."""
    return DATA_DIR / "scripts" / f"{tid}.json"


def _manifest_path(tid: str) -> Path:
    """output/<id>/assets/assets_manifest.json — lo escribe fase2a (asset_manager)."""
    return OUTPUT_DIR / tid / "assets" / "assets_manifest.json"


def _fondos_path(tid: str) -> Path:
    """output/<id>/<id>_final.mp4 — el mp4 de preview que deja `fase2b <id>` sin gfx después de cocer los visuales
    base (`_fase2b_work/chNN_flux_visual.mp4` / `_hybrid_visual.mp4`, los que reusan --plan-only y --reuse-visuals)."""
    return OUTPUT_DIR / tid / f"{tid}_final.mp4"


def _visuales_base_faltan(tid: str) -> list[str]:
    """Los caps del manifest sin su visual base cocido en `output/<id>/_fase2b_work/`: flux → `chNN_flux_visual.mp4`;
    veo con suplementarias ok → `chNN_hybrid_visual.mp4`; veo solo → su clip (lo deja fase2a, no se cuece). Espejo de
    fase2b._visual_base_existente (fase2b no se importa: arrastra DepthFlow y Gemini). Sin manifest legible = todos."""
    try:
        caps = json.loads(_manifest_path(tid).read_text(encoding="utf-8")).get("chapters") or []
    except (OSError, ValueError):
        return ["(manifest ilegible)"]
    work = OUTPUT_DIR / tid / "_fase2b_work"
    faltan = []
    for c in caps:
        cid, engine = c.get("id"), str(c.get("engine", "")).lower()
        supp = [s for s in (c.get("supplemental_images") or []) if s.get("status") == "ok" and s.get("path")]
        if engine == "flux":
            base = work / f"{cid}_flux_visual.mp4"
        elif engine == "veo" and supp:
            base = work / f"{cid}_hybrid_visual.mp4"
        else:
            continue
        if not base.exists():
            faltan.append(cid)
    return faltan if caps else ["(manifest sin caps)"]


def _guion_pantalla_path(tid: str, ext: str = "json") -> Path:
    """output/<id>/GUION_PANTALLA.json (.md legible) — lo escribe `fase2b <id> --plan-only`."""
    return OUTPUT_DIR / tid / Path(aprobacion.GUION).with_suffix(f".{ext}").name


def _render_path(tid: str) -> Path:
    """output/<id>/<id>_final_gfx.mp4 — el video con gfx (fase2b con --gfx escribe acá, no pisa el _final.mp4)."""
    return OUTPUT_DIR / tid / f"{tid}_final_gfx.mp4"


def _estado_papel(tid: str) -> tuple[bool, str]:
    """(papel aprobado y vigente, motivo) — el de fase1_5 (import tardío: fase1_5 es pesado)."""
    from fase1_5 import estado_papel
    return estado_papel(tid)


def _estado_guion(tid: str) -> tuple[bool, str]:
    """(guion de pantalla aprobado y vigente, motivo) — el de script_engine.aprobacion (F33)."""
    return aprobacion.estado(OUTPUT_DIR / tid)


def _packaged(tid: str) -> bool:
    """fase3 marca `packaged` en topics_db al primer COMPONER."""
    return bool((topics_db.get_topic_by_id(tid) or {}).get("packaged"))


def _video_hecho(tid: str) -> bool:
    """topics_db dice que el topic ya tiene video (fase2b lo promueve a `video_generated`, con su video_id propio)."""
    return (topics_db.get_topic_by_id(tid) or {}).get("status") == "video_generated"


def _mtime(p: Path) -> float | None:
    return p.stat().st_mtime if p.exists() else None


# ═══════════════════════════════════════════════════════════════
#  Retomar: en qué etapa está un topic (SOLO LECTURA)
# ═══════════════════════════════════════════════════════════════
ETAPAS = ("guion", "papel", "voz", "assets", "fondos", "guion_pantalla", "aprobar_guion", "render",
          "packaging", "listo")
CADENA_VIEJA = "cadena_vieja"   # sin papel pero con artefactos de después: no se retoma (no se re-paga nada)


def etapa_de(tid: str) -> tuple[str, str]:
    """La primera etapa que le falta a `tid`, mirando solo artefactos en disco. No escribe nada.

    guion           no hay papel (`_steps/<id>/01e_pantalla.md`) ni nada de después
    papel           hay papel pero `fase1_5.estado_papel` no lo da aprobado (o cambió después de aprobado)
    voz             papel aprobado, falta `data/scripts/<id>.json`
    assets          falta `output/<id>/assets/assets_manifest.json`
    fondos          falta `output/<id>/<id>_final.mp4` (fase2b sin gfx) y a algún cap del manifest le falta su
                    visual base en `_fase2b_work/` (con los visuales cocidos, el preview no hace falta)
    guion_pantalla  falta `output/<id>/GUION_PANTALLA.json`
    aprobar_guion   hay guion de pantalla pero `aprobacion.estado` no lo da aprobado (o los planes cambiaron)
    render          falta `output/<id>/<id>_final_gfx.mp4` o es más viejo que GUION_PANTALLA.json
    packaging       falta `packaged` en topics_db (fase3)
    listo           todo hecho
    cadena_vieja    sin papel pero con guion/assets/video (o `video_generated` en topics_db): topic de la cadena
                    borrada; no se corre nada
    """
    papel_ok, motivo = _estado_papel(tid)
    if not papel_ok:
        if _papel_md_path(tid).exists():
            return "papel", motivo
        hechos = [p.name for p in (_script_path(tid), _manifest_path(tid), _fondos_path(tid), _render_path(tid))
                  if p.exists()]
        if _video_hecho(tid):
            hechos.append("status video_generated en topics_db")
        if hechos:
            return CADENA_VIEJA, (f"sin papel pero con {', '.join(hechos)}: topic de la cadena borrada "
                                  f"(DECISIONES 2026-10-27 20:59); no se retoma para no volver a pagar lo hecho")
        return "guion", motivo
    if not _script_path(tid).exists():
        return "voz", f"{motivo}; falta {_script_path(tid).as_posix()}"
    if not _manifest_path(tid).exists():
        return "assets", f"falta {_manifest_path(tid).as_posix()}"
    if not _fondos_path(tid).exists():
        faltan = _visuales_base_faltan(tid)
        if faltan:
            return "fondos", f"falta {_fondos_path(tid).name} y los visuales base de {', '.join(faltan)}"
    gj = _guion_pantalla_path(tid)
    if not gj.exists():
        return "guion_pantalla", f"falta {gj.as_posix()}"
    guion_ok, motivo = _estado_guion(tid)
    if not guion_ok:
        return "aprobar_guion", motivo
    rp_ = _render_path(tid)
    if not rp_.exists():
        return "render", f"{motivo}; falta {rp_.as_posix()}"
    if _mtime(rp_) < _mtime(gj):
        return "render", f"{rp_.name} es más viejo que {gj.name} (el guion se regeneró o se aprobó después)"
    if not _packaged(tid):
        return "packaging", f"{rp_.name} listo; falta empaquetar (fase3)"
    return "listo", "empaquetado"


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
            why: str | None, next_cmd: str | list[str] | None) -> None:
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
    if isinstance(next_cmd, str):
        print(f"  ➡  Próximo comando: {next_cmd}")
    elif next_cmd:
        print("  ➡  Próximos comandos:")
        for c in next_cmd:
            print(f"       {c}")
    print(f"{'═' * 60}\n")


# ═══════════════════════════════════════════════════════════════
#  Secuencia
# ═══════════════════════════════════════════════════════════════
# Las etapas son funciones `(tid, ran, batch) -> int | None`: None = la etapa corrió y la secuencia vuelve a mirar el
# disco (etapa_de); un int = la corrida termina acá con ese exit code (0 = PARADA normal en una compuerta o cadena
# completa; 1 = falla o artefacto faltante).

# Flags del render final (lab/ESTADO_SESION.md, «Video completo»; tabla de constantes de F41).
RENDER_FLAGS = ["--reuse-visuals", "--keep-segments", "--gfx", "--gfx-sparse"]
RAM_MIN_GB = 14.0   # DECISIONES: 2026-10-27 00:30 (antes de un render completo: < 14 GB libres → avisar y PARADA; umbral de F2)


def _ram_libre_gb() -> float | None:
    """La RAM física libre en GB (Windows: GlobalMemoryStatusEx); None si no se puede medir. Solo mide: no cierra nada."""
    try:
        import ctypes

        class _MEM(ctypes.Structure):
            _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                        ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                        ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                        ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
        m = _MEM()
        m.dwLength = ctypes.sizeof(_MEM)
        if not ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(m)):
            return None
        return m.ullAvailPhys / 1024 ** 3
    except Exception:  # noqa: BLE001 — sin medida no se inventa una
        return None


def _phase_header(name: str, tid: str) -> None:
    print(f"\n{'─' * 60}\n  ▶ {name} — {tid}\n{'─' * 60}")


def _hoy() -> str:
    """La fecha de una aprobación: la del reloj (el «FECHA» de --aprobar-papel / --aprobar-guion)."""
    return datetime.date.today().isoformat()


def _shell(cmd: list[str]) -> str:
    return subprocess.list2cmdline(["python", *cmd])


def _retomar_cmd(tid: str) -> str:
    return f"python run_pipeline.py --topic {tid}"


def _fallo(tid: str, ran: list[str], etapa: str, cmd: list[str], rc: int) -> int:
    why = f"{cmd[0]} exit {rc}"
    if cmd[0] == "fase1_5.py" and rc == 2:
        why += " (PARADA de fase1_5: el motivo está arriba en el log)"
    _report(tid, ran, stopped_at=etapa, why=why, next_cmd=[_shell(cmd), f"retomar: {_retomar_cmd(tid)}"])
    return 1


def _compuerta(menu: str, tid: str, doc: Path, *, prompt: str, ok_label: str, motivo: str) -> str:
    """Compuerta con el form: muestra `doc` ENTERO (el texto va en el `body` del marcador) y espera A/P por stdin.
    Devuelve "A" solo si Omar eligió A; cualquier otra línea o stdin cerrado = "P" (nunca se aprueba sola). Sin el
    documento en disco no hay nada que mostrar → "P" sin preguntar."""
    if not doc.exists():
        print(f"  ⛔ falta {doc.as_posix()}: la compuerta no tiene qué mostrar")
        return "P"
    emit_choice_marker(
        menu=menu,
        prompt=prompt,
        options=[{"key": "A", "label": ok_label}, {"key": "P", "label": "Parar acá (se retoma después)"}],
        default="P",
        body=doc.read_text(encoding="utf-8"),
        payload={"topic_id": tid, "doc": doc.as_posix(), "motivo": motivo},
    )
    try:
        resp = input()
    except EOFError:
        resp = ""
    return "A" if resp.strip().upper() == "A" else "P"


def _paso_guion(tid: str, ran: list[str], batch: bool) -> int | None:
    """GUION: la única cadena de fase1_5 (research v3 → ficha → escaleta → guion v4 → partición y títulos → papel);
    termina en la PARADA del papel con exit 0."""
    _phase_header("GUION (fase1_5)", tid)
    ran.append("guion")
    cmd = ["fase1_5.py", "--topic", tid, "--batch"]
    rc = _run(cmd)
    return _fallo(tid, ran, "GUION", cmd, rc) if rc != 0 else None


def _paso_papel(tid: str, ran: list[str], batch: bool) -> int | None:
    """PAPEL: la compuerta del papel (01e_pantalla.md). Con el form: A aprueba y sigue; P para. Sin el form: para."""
    _phase_header("PAPEL (compuerta del papel)", tid)
    ran.append("papel")
    md = _papel_md_path(tid)
    _, motivo = _estado_papel(tid)
    comandos = [f"leer:    {md.as_posix()}",
                f"aprobar: python fase1_5.py --topic {tid} --aprobar-papel \"Omar <fecha>\"",
                f"retomar: {_retomar_cmd(tid)}"]
    if not QA_FORM:
        _report(tid, ran, stopped_at="PAPEL", next_cmd=comandos,
                why=f"{motivo} (la compuerta no se aprueba sola: sin el form la aprueba Omar a mano)")
        return 0
    resp = _compuerta("papel_gate", tid, md, motivo=motivo,
                      prompt="Leé el papel entero. A lo aprueba y sigue a la voz y las imágenes (se paga); P para acá.",
                      ok_label="Aprobar el papel -> voz e imágenes")
    if resp != "A":
        _report(tid, ran, stopped_at="PAPEL", why=f"{motivo}; Omar paró en la compuerta del papel", next_cmd=comandos)
        return 0
    cmd = ["fase1_5.py", "--topic", tid, "--aprobar-papel", f"Omar {_hoy()}"]
    rc = _run(cmd)
    return _fallo(tid, ran, "PAPEL", cmd, rc) if rc != 0 else None


def _paso_voz(tid: str, ran: list[str], batch: bool) -> int | None:
    """VOZ: con el papel aprobado, fase1_5 desde normalizer_gate (voz, música, m03, foto madre, assemble)."""
    _phase_header("VOZ (fase1_5 --from normalizer_gate)", tid)
    ran.append("voz")
    cmd = ["fase1_5.py", "--topic", tid, "--from", "normalizer_gate", "--batch"]
    rc = _run(cmd)
    return _fallo(tid, ran, "VOZ", cmd, rc) if rc != 0 else None


def _paso_assets(tid: str, ran: list[str], batch: bool) -> int | None:
    _phase_header("ASSETS (fase2a)", tid)
    ran.append("assets")
    cmd = ["fase2a.py", "--topic", tid]
    rc = _run(cmd)
    return _fallo(tid, ran, "ASSETS", cmd, rc) if rc != 0 else None


def _paso_fondos(tid: str, ran: list[str], batch: bool) -> int | None:
    """FONDOS: fase2b sin gfx (cuece los visuales base y deja el mp4 de preview). Antes, con el form, el VISOR."""
    _phase_header("FONDOS (fase2b sin gfx)", tid)
    # ── VISOR — gate OBLIGADO (solo modo form) ─────────────────
    # Entre los assets (fase2a) y el horneado (fase2b): el form frena SIEMPRE acá para que
    # Omar revise/arregle foto/clip/audio en el visor (que lee data/scripts/<tid>.json, el
    # MISMO archivo que fase2b → preview == render). El server, al captar el marcador,
    # apunta su TOPIC_ID a este tid. input() bloquea sin timeout hasta que el form mande "C".
    # En terminal pura (sin QA_FORM) este bloque no corre → fase2b sigue de corrido.
    if QA_FORM:
        emit_choice_marker(
            menu="visor_gate",
            prompt="Revisá el video en el visor y arreglá lo que haga falta. Cuando estés listo, horneá.",
            options=[{"key": "C", "label": "Continuar -> hornear video"}],
            payload={"topic_id": tid},
        )
        input()  # bloquea hasta que el form escriba "C" (cualquier línea) por stdin
    ran.append("fondos")
    cmd = ["fase2b.py", tid]              # video_id posicional == topic_id en LONG
    rc = _run(cmd)
    return _fallo(tid, ran, "FONDOS", cmd, rc) if rc != 0 else None


def _paso_guion_pantalla(tid: str, ran: list[str], batch: bool) -> int | None:
    """El guion de pantalla (fase2b --plan-only, sobre los visuales base ya cocidos)."""
    _phase_header("PANTALLA (fase2b --plan-only)", tid)
    ran.append("guion de pantalla")
    cmd = ["fase2b.py", tid, "--plan-only"]
    rc = _run(cmd)
    return _fallo(tid, ran, "PANTALLA", cmd, rc) if rc != 0 else None


def _paso_aprobar_guion(tid: str, ran: list[str], batch: bool) -> int | None:
    """La compuerta del guion de pantalla (GUION_PANTALLA.md). P es el camino normal cuando el analista lo revisa y
    aplica --plan-edit; después se retoma. A: --aprobar-guion y sigue al render. Sin el form: para."""
    _phase_header("PANTALLA (compuerta del guion de pantalla)", tid)
    ran.append("compuerta del guion de pantalla")
    md = _guion_pantalla_path(tid, "md")
    _, motivo = _estado_guion(tid)
    comandos = [f"leer:    {md.as_posix()}",
                f"editar:  python fase2b.py {tid} --plan-edit ARCHIVO.json   (el analista; regenera el guion)",
                f"aprobar: python fase2b.py {tid} --aprobar-guion \"Omar <fecha>\"",
                f"retomar: {_retomar_cmd(tid)}"]
    if not QA_FORM:
        _report(tid, ran, stopped_at="GUION DE PANTALLA", next_cmd=comandos,
                why=f"{motivo} (la compuerta no se aprueba sola: sin el form la aprueba Omar a mano)")
        return 0
    resp = _compuerta("guion_gate", tid, md, motivo=motivo,
                      prompt="Leé el guion de pantalla entero. A lo aprueba y sigue al render con gfx; P para acá "
                             "(el analista lo revisa y edita con --plan-edit; después se retoma).",
                      ok_label="Aprobar el guion -> render con gfx")
    if resp != "A":
        _report(tid, ran, stopped_at="GUION DE PANTALLA", next_cmd=comandos,
                why=f"{motivo}; Omar paró en la compuerta del guion de pantalla")
        return 0
    cmd = ["fase2b.py", tid, "--aprobar-guion", f"Omar {_hoy()}"]
    rc = _run(cmd)
    return _fallo(tid, ran, "GUION DE PANTALLA", cmd, rc) if rc != 0 else None


def _paso_render(tid: str, ran: list[str], batch: bool) -> int | None:
    """RENDER con gfx. El orquestador no cierra ningún programa de Omar (DECISIONES 2026-10-27 00:30): si el render
    necesita RAM, lo dice el reporte y Omar decide."""
    _phase_header("RENDER (fase2b --gfx --gfx-sparse)", tid)
    ran.append("render")
    cmd = ["fase2b.py", tid, *RENDER_FLAGS]
    libre = _ram_libre_gb()                              # DECISIONES 00:30: medir antes de un render completo
    if libre is None:
        print(f"  ⚠ No pude medir la RAM libre (DECISIONES 00:30 pide ≥ {RAM_MIN_GB:g} GB); el render sigue.")
    elif libre < RAM_MIN_GB:
        _report(tid, ran, stopped_at="RENDER", next_cmd=[f"retomar: {_retomar_cmd(tid)}"],
                why=f"RAM libre {libre:.1f} GB < {RAM_MIN_GB:g} GB (DECISIONES 00:30): PARADA antes del render. "
                    f"El orquestador no cierra ningún programa; liberá RAM vos y retomá.")
        return 0
    else:
        print(f"  ℹ RAM libre {libre:.1f} GB ≥ {RAM_MIN_GB:g} GB (DECISIONES 00:30).")
    print("  ℹ Render completo con gfx: el orquestador no cierra ningún programa.")
    rc = _run(cmd)
    if rc != 0:
        _report(tid, ran, stopped_at="RENDER", next_cmd=[_shell(cmd), f"retomar: {_retomar_cmd(tid)}"],
                why=f"fase2b exit {rc} (si fue por falta de RAM: el orquestador no cierra nada; liberala vos y retomá)")
        return 1
    return None


def _paso_packaging(tid: str, ran: list[str], batch: bool) -> int:
    if batch:
        # Batch: NO levantar el form (gate humano). Se reporta y queda listo.
        ran.append("packaging (diferido)")
        _report(tid, ran, stopped_at=None, why=None, next_cmd=None)
        print(f"  📦 LISTO PARA PACKAGING → python fase3.py {tid}\n")
        return 0
    _phase_header("PACKAGING (fase3, form)", tid)
    ran.append("packaging")
    cmd = ["fase3.py", tid]
    rc = _run(cmd)
    if rc != 0:
        return _fallo(tid, ran, "PACKAGING", cmd, rc)
    _report(tid, ran, stopped_at=None, why=None, next_cmd=None)
    return 0


_PASOS = {"guion": _paso_guion, "papel": _paso_papel, "voz": _paso_voz, "assets": _paso_assets,
          "fondos": _paso_fondos, "guion_pantalla": _paso_guion_pantalla, "aprobar_guion": _paso_aprobar_guion,
          "render": _paso_render, "packaging": _paso_packaging}


def sequence(tid: str, *, batch: bool = False) -> int:
    """Corre la cadena para `tid` desde la primera etapa que falta (etapa_de). Devuelve el exit code: 0 = cadena
    completa o PARADA en una compuerta (papel / guion de pantalla); 1 = falla o artefacto faltante.

    Después de cada etapa vuelve a mirar el disco: si la etapa no avanzó, para (nunca corre dos veces lo mismo).
    `batch`: en PACKAGING no levanta el form, solo reporta el comando de fase3.
    """
    ran: list[str] = []
    etapa, motivo = etapa_de(tid)
    print(f"\n  ⏵ {tid}: arranca en «{etapa}» — {motivo}")
    while True:
        if etapa == CADENA_VIEJA:
            _report(tid, ran, stopped_at="RETOMAR", why=motivo, next_cmd=None)
            return 1
        if etapa == "listo":
            _report(tid, ran, stopped_at=None, why=None, next_cmd=None)
            print(f"  ✔ {tid} ya está empaquetado: no hay nada que correr.\n")
            return 0
        res = _PASOS[etapa](tid, ran, batch)
        if res is not None:
            return res
        nueva, motivo = etapa_de(tid)
        if nueva == CADENA_VIEJA or ETAPAS.index(nueva) <= ETAPAS.index(etapa):
            _report(tid, ran, stopped_at=etapa.upper(), next_cmd=_retomar_cmd(tid),
                    why=f"la etapa terminó sin dejar su artefacto (sigue en «{nueva}»: {motivo})")
            return 1
        etapa = nueva


# ═══════════════════════════════════════════════════════════════
#  Resolución de tid + CLI
# ═══════════════════════════════════════════════════════════════
# HANDOFF 66a — el path --research consume el SENTINEL que fase1 --no-chain declara (qué topic
# produjo ESTA corrida), en vez de escanear el DB por cualquier 'validated' (raíz del bug:
# agarraba un leftover viejo y horneaba el video equivocado; con 2+ leftover abría un input()
# no env-gated que colgaba el form). Contrato fase1 ↔ run_pipeline, gateado por --no-chain.
RESEARCH_SENTINEL = DATA_DIR / "_last_research.json"


def _read_research_sentinel() -> list[str]:
    """Lee SOLO lo que fase1 --no-chain declaró que produjo esta corrida. Ausente/ilegible = []."""
    try:
        d = json.loads(RESEARCH_SENTINEL.read_text(encoding="utf-8"))
        return [t for t in d.get("tids", []) if t]
    except Exception:
        return []


def _newest_validated(tids: list[str]) -> str:
    """Desempate determinístico por validated_at — SIN input() (no cuelga el form).
    topic_validator escribe el timestamp en competition_data.validated_at (no top-level)."""
    db = topics_db.load_db()
    by_id = {t.get("id"): t for t in db.get("topics", [])}

    def _ts(x: str) -> str:
        t = by_id.get(x, {}) or {}
        return (t.get("competition_data", {}) or {}).get("validated_at", "") or t.get("validated_at", "")

    return max(tids, key=_ts)


def main() -> int:
    ap = argparse.ArgumentParser(
        description="run_pipeline — secuenciador subprocess del pipeline (1 topic).")
    ap.add_argument("--topic", type=str, default=None,
                    help="Topic_id a correr (retoma donde quedó, según etapa_de). Sin esto, abre el menú de "
                         "validados.")
    ap.add_argument("--research", action="store_true",
                    help="Research-on-demand: corre fase1 --no-chain (pick de seed + "
                         "research + validate, interactivo) y después secuencia el resto.")
    ap.add_argument("--video-type", choices=["short", "long"], default=None,
                    help="(con --research) Reenvía el tipo a fase1 para saltar el prompt "
                         "S/L. Sin esto, fase1 pregunta igual que hoy. Lo usa el form.")
    ap.add_argument("--batch", action="store_true",
                    help="El PACKAGING no levanta el form (solo reporta el comando de fase3). "
                         "fase1_5 corre siempre con --batch. Las compuertas del papel y del guion "
                         "de pantalla NO se saltean. Convive con --research (el pick de seed "
                         "SIEMPRE es interactivo).")
    args = ap.parse_args()

    if args.research:
        # El pick de seed (gasto de grounding) SIEMPRE es interactivo: --batch solo
        # gobierna el skip del form de fase3, ya en sequence().
        # Header de fase con el MISMO formato que _phase_header (sin tid: RESEARCH todavía no
        # lo tiene): contiene "  ▶ " y "RESEARCH" → el reader del form marca la fase activa
        # igual que las demás (sin esto, RESEARCH —la fase más larga— quedaba gris).
        print(f"\n{'─' * 60}\n  ▶ RESEARCH (fase1)\n{'─' * 60}")
        rc = _run(["fase1.py", "--no-chain"]
                  + (["--video-type", args.video_type] if args.video_type else []))
        if rc != 0:
            print("  ⛔ fase1 falló o se canceló — no hay tema para seguir.")
            return rc
        tids = _read_research_sentinel()          # consume el sentinel; NO escanea el DB
        if not tids:
            print("  ℹ Esta corrida no produjo tema (soltaste el pick o cancelaste). Stop limpio.")
            return 0
        tid = tids[0] if len(tids) == 1 else _newest_validated(tids)
    elif args.topic:
        tid = args.topic
    else:
        from fase1_5 import _select_topic_interactive
        tid = _select_topic_interactive()
        if not tid:
            print("\n  Cancelado (sin tema elegido).")
            return 0

    return sequence(tid, batch=args.batch)


if __name__ == "__main__":
    raise SystemExit(main())
