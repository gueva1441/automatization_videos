"""
fase1_5.py — Orchestrator del motor de guion (m01a → m05 → m06)

Toma topics aprobados desde el CSV editado de fase1 (latido A) y los corre
por la cadena m01a → m01b → m03 → m05 → m06.

m06 clasifica issues, muestra menú interactivo [P]/[R]/[E] al usuario:
  [P] Pasar todo → ensambla data/scripts/<topic_id>.json (contrato sagrado)
  [R] Rerun     → imprime comando para re-correr desde el módulo culpable
  [E] Exit      → deja JSONs por issue en data/issues_log/<topic_id>/

Cada módulo persiste su output en data/scripts/_steps/<topic_id>/.

Uso:
  python fase1_5.py                              corre todos los topics aprobados desde m01a
  python fase1_5.py --topic <id>                 corre solo 1 topic específico
  python fase1_5.py --topic <id> --from m03      reanuda 1 topic desde m03 (asume m01a/m01b ya corrieron)
  python fase1_5.py --from m05                   solo audita (m05) todos los topics aprobados
  python fase1_5.py --topic <id> --only m01b     corre SOLO m01b y corta (sin arrastrar la cadena)

Flags:
  --topic <id>      Procesar solo el topic con este UUID (default: todos los aprobados del CSV).
  --only <step>     Correr SOLO ese módulo (equivale a --from <step> + cortar después).
  --csv <path>      Path al CSV editado (default: data/fase1_review.csv).
  --voting-n <int>  Cantidad de corridas voting de m05 (default: 3).
  --no-gate         Modo batch del normalizer_gate (sin CLI interactivo).

Salida:
  Imprime resumen al final con PASS/FAIL por topic.
"""

import argparse
import json
import sys
from pathlib import Path

# Fix #155 — PowerShell en Windows usa cp1252 default y rompe con caracteres
# como "→" (\u2192), "═" y emojis en prints. Reconfigurar stdout/stderr a utf-8.
# El guard `sys.stdout.encoding and ...` evita AttributeError cuando encoding
# es None (stdout capturado en tests/CI).
if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")

from config import DATA_DIR, OUTPUT_DIR
from csv_exporter import parse_decisions_csv, OUTPUT_CSV, export_single_topic_csv

# Módulos del motor de guion
import audio_manager
from script_engine.m01a_skeleton import generate_skeleton
from script_engine.m01b_narrator import generate_narration
from script_engine import m02_5_normalizer_gate
from script_engine.m03_visual import assign_visual_prompts
from script_engine.m05_judge import judge_topic_with_voting
from script_engine.m06_classifier import classify_and_decide
from script_engine import m07_music_director


VALID_FROM_STEPS = ("m01a", "m01b", "normalizer_gate", "audio", "m07", "m03", "m05", "m06")
STEPS_DIR: Path = DATA_DIR / "scripts" / "_steps"
TOPICS_DB: Path = DATA_DIR / "topics_db.json"


def _build_audio_script(
    topic_id: str,
    narration: dict,
    skeleton: dict,
) -> dict:
    """Convierte output de m01b al schema que espera audio_manager.process_script.

    PR 2.A chat 24: ahora también lee narrative_intent del skeleton y lo
    propaga a cada cap del audio_script. audio_manager hace el override de
    voice_settings (stability+style) por intent.

    Si el skeleton no tiene narrative_intent (skeleton viejo pre-PR 2.A),
    cada cap viaja con narrative_intent="" y audio_manager cae al fallback
    (voice_settings del profile sin override).

    Las humanizer_phrases viajan como metadata top-level aunque ningún
    módulo activo del pipeline las consuma (deuda técnica heredada).
    """
    intent_by_cap: dict[int, str] = {
        ch["chapter_number"]: ch.get("narrative_intent", "")
        for ch in skeleton.get("chapters", [])
    }

    chapters_for_audio = [
        {
            "id": f"ch{ch['chapter_number']:02d}",  # mismo formato que fase2a._chapter_id
            "text": ch["narration"],
            "narrative_intent": intent_by_cap.get(ch["chapter_number"], ""),
        }
        for ch in narration["chapters"]
    ]
    return {
        "video_id": topic_id,
        "chapters": chapters_for_audio,
        "humanizer_phrases": narration.get("humanizer_phrases", []),
    }


# ═══════════════════════════════════════════════════════════════
#  HELPERS DE CARGA
# ═══════════════════════════════════════════════════════════════

def _load_topic_by_id(topic_id: str) -> dict:
    """Carga topic dict desde data/topics_db.json por id.

    Lee el JSON directo (sin depender de paquetes externos). Acepta tanto
    formato `{"topics": [...]}` como list raíz.
    """
    if not TOPICS_DB.exists():
        raise FileNotFoundError(f"topics_db.json no existe en {TOPICS_DB}")
    db = json.loads(TOPICS_DB.read_text(encoding="utf-8"))
    topics = db.get("topics", []) if isinstance(db, dict) else db
    for t in topics:
        if t.get("id") == topic_id or t.get("topic_id") == topic_id:
            return t
    raise KeyError(f"topic_id {topic_id!r} no existe en topics_db.json")


def _load_step_output(topic_id: str, filename: str) -> dict:
    """Carga un JSON intermedio desde _steps/<topic_id>/."""
    path = STEPS_DIR / topic_id / filename
    if not path.exists():
        raise FileNotFoundError(
            f"fase1.5: archivo {filename} no existe en {path}. "
            f"Asegurate de haber corrido el módulo correspondiente antes."
        )
    return json.loads(path.read_text(encoding="utf-8"))


def _load_skeleton(topic_id: str) -> dict:
    return _load_step_output(topic_id, "01a_skeleton.json")


def _load_narration(topic_id: str) -> dict:
    return _load_step_output(topic_id, "01b_narration.json")


# ═══════════════════════════════════════════════════════════════
#  PIPELINE POR TOPIC
# ═══════════════════════════════════════════════════════════════

def process_topic(
    topic_id: str,
    from_step: str = "m01a",
    voting_n: int = 3,
    gate_interactive: bool = True,
    music_gate_interactive: bool = True,
    stop_after_step: str | None = None,
) -> dict:
    """Corre la cadena m01a → m05 para 1 topic, reanudando desde from_step.

    Args:
        gate_interactive: PR 2.0 chat 24. Default True (CLI humano para
            aprobar pronunciaciones de tokens nuevos detectados por
            tts_normalizer). Si False (--no-gate), solo loguea sospechosos
            y continúa — modo batch nocturno.
        music_gate_interactive: PR 2.B chat 25. Default True (CLI humano para
            aprobar tracks de música generados por m07 antes de persistir
            a audio_library). Si False (--no-music-gate), todos los tracks
            generados se aprueban automáticamente — modo batch nocturno.
        stop_after_step: PR --only chat 24. Si != None, después de ejecutar
            ese step la cadena se corta (no avanza al siguiente). Útil para
            validar 1 módulo aislado sin gastar plata en m05/m06.

    Returns:
      dict {topic_id, steps_completed: list[str], status: 'PASS'|'FAIL', error?: str}
    """
    print(f"\n{'═' * 60}")
    print(f"  📜 Procesando topic {topic_id} desde {from_step}")
    print(f"{'═' * 60}")

    result = {"topic_id": topic_id, "steps_completed": [], "status": "RUNNING"}

    try:
        # m01a — skeleton
        if from_step in ("m01a",):
            topic = _load_topic_by_id(topic_id)
            print(f"  [01a] Generando skeleton...")
            skeleton = generate_skeleton(topic)
            result["steps_completed"].append("m01a")
            if stop_after_step == "m01a":
                result["status"] = "PASS"
                print(f"\n  ✅ Topic {topic_id} OK (stop after m01a) — pasos: {result['steps_completed']}")
                return result

        else:
            skeleton = None  # se carga abajo si hace falta

        # m01b — narración
        if from_step in ("m01a", "m01b"):
            if skeleton is None:
                topic = _load_topic_by_id(topic_id)
                skeleton = _load_skeleton(topic_id)
            else:
                topic = _load_topic_by_id(topic_id)
            print(f"  [01b] Generando narración...")
            narration = generate_narration(topic, skeleton)
            result["steps_completed"].append("m01b")
            if stop_after_step == "m01b":
                result["status"] = "PASS"
                print(f"\n  ✅ Topic {topic_id} OK (stop after m01b) — pasos: {result['steps_completed']}")
                return result
        else:
            narration = None

        # normalizer_gate — gate humano del tts_normalizer (PR 2.0 chat 24).
        # Detecta sospechosos en la narración (siglas/abreviaturas/unidades sin
        # cubrir), pide al LLM una propuesta y abre CLI para aprobar/editar.
        # Aprobados se persisten a data/normalizer_custom_dict.json y se aplican
        # al runtime para que el audio que viene después los use ya correctos.
        if from_step in ("m01a", "m01b", "normalizer_gate"):
            if narration is None:
                topic = _load_topic_by_id(topic_id)
                skeleton = _load_skeleton(topic_id)
                narration = _load_narration(topic_id)
            print(f"  [normalizer_gate] Detectando sospechosos...")
            gate_result = m02_5_normalizer_gate.gate_normalizer_for_topic(
                topic_id=topic_id,
                narration=narration,
                interactive=gate_interactive,
            )
            n_added = gate_result["added_to_dict"]
            if n_added > 0:
                print(f"  [normalizer_gate] {n_added} entries nuevas → custom_dict.json")
            elif gate_result["spans_detected"]:
                print(f"  [normalizer_gate] {len(gate_result['spans_detected'])} span(s) "
                    f"detectado(s), nada persistido (rechazados/skipped)")
            else:
                print(f"  [normalizer_gate] sin spans")
            result["steps_completed"].append("normalizer_gate")
            if stop_after_step == "normalizer_gate":
                result["status"] = "PASS"
                print(f"\n  ✅ Topic {topic_id} OK (stop after normalizer_gate) — pasos: {result['steps_completed']}")
                return result

        # audio — TTS antes de m03 (LONG only). PR 1 chat 24: el sync_map
        # debe estar listo para m03. PR 2.A chat 24: skeleton se pasa a
        # _build_audio_script para propagar narrative_intent por cap.
        if from_step in ("m01a", "m01b", "normalizer_gate", "audio"):
            if narration is None:
                topic = _load_topic_by_id(topic_id)
                skeleton = _load_skeleton(topic_id)
                narration = _load_narration(topic_id)
            elif skeleton is None:
                # narration ya estaba en memoria pero skeleton no (caso raro,
                # cubre defensivamente reanudaciones intermedias).
                skeleton = _load_skeleton(topic_id)
            print(f"  [audio] Generando audio TTS + sync_map...")
            audio_script = _build_audio_script(topic_id, narration, skeleton)
            sync_map_path = audio_manager.process_script(
                audio_script, language="es", skip_if_exists=True,
            )
            sync_map = json.loads(sync_map_path.read_text(encoding="utf-8"))
            result["steps_completed"].append("audio")
            if stop_after_step == "audio":
                result["status"] = "PASS"
                print(f"\n  ✅ Topic {topic_id} OK (stop after audio) — pasos: {result['steps_completed']}")
                return result
        else:
            sync_map = None  # se carga del disco en el bloque m07/m03 si hace falta

        # m07 — music_director (PR 2.B chat 25). Genera music_map.json a partir
        # del sync_map. Matchea library / genera nuevos con gate humano. Crítico
        # para Sound Bank curado del canal.
        if from_step in ("m01a", "m01b", "normalizer_gate", "audio", "m07"):
            if sync_map is None:
                sync_map_path = OUTPUT_DIR / "audio" / topic_id / "sync_map.json"
                if not sync_map_path.exists():
                    raise FileNotFoundError(
                        f"sync_map.json no existe en {sync_map_path}. "
                        f"Re-correr desde audio: --from audio"
                    )
                sync_map = json.loads(sync_map_path.read_text(encoding="utf-8"))
            print(f"  [07] Music director — match library / generar nuevos...")
            music_map = m07_music_director.generate_music_map(
                topic_id=topic_id,
                sync_map=sync_map,
                interactive=music_gate_interactive,
            )
            tracks = music_map.get("tracks_by_chapter", {})
            n_reused = sum(1 for t in tracks.values() if t.get("match_source") == "reused")
            n_generated = sum(1 for t in tracks.values() if t.get("match_source") == "generated")
            n_skipped = sum(1 for t in tracks.values() if t.get("match_source") == "skipped")
            print(f"  [07] music_map listo — reused: {n_reused}, "
                  f"generated: {n_generated}, skipped: {n_skipped}")
            result["steps_completed"].append("m07")
            if stop_after_step == "m07":
                result["status"] = "PASS"
                print(f"\n  ✅ Topic {topic_id} OK (stop after m07) — pasos: {result['steps_completed']}")
                return result

        # m03 — visual (recibe sync_map como input opcional)
        if from_step in ("m01a", "m01b", "normalizer_gate", "audio", "m07", "m03"):
            if narration is None:
                topic = _load_topic_by_id(topic_id)
                skeleton = _load_skeleton(topic_id)
                narration = _load_narration(topic_id)
            if sync_map is None:
                # Reanudación desde m03: cargar sync_map de disco.
                sync_map_path = OUTPUT_DIR / "audio" / topic_id / "sync_map.json"
                if not sync_map_path.exists():
                    raise FileNotFoundError(
                        f"sync_map.json no existe en {sync_map_path}. "
                        f"Re-correr desde audio: --from audio"
                    )
                sync_map = json.loads(sync_map_path.read_text(encoding="utf-8"))
            print(f"  [03] Generando visual prompts...")
            visual = assign_visual_prompts(topic, skeleton, narration, sync_map=sync_map)
            result["steps_completed"].append("m03")
            if stop_after_step == "m03":
                result["status"] = "PASS"
                print(f"\n  ✅ Topic {topic_id} OK (stop after m03) — pasos: {result['steps_completed']}")
                return result

        # m05 — juez (voting N)
        if from_step in ("m01a", "m01b", "normalizer_gate", "audio", "m07", "m03", "m05"):
            print(f"  [05] Auditando con voting N={voting_n}...")
            judge_result = judge_topic_with_voting(topic_id, n=voting_n)
            result["steps_completed"].append("m05")
            result["judge_verdict"] = judge_result.get("global_verdict", "?")
            if stop_after_step == "m05":
                result["status"] = "PASS"
                print(f"\n  ✅ Topic {topic_id} OK (stop after m05) — pasos: {result['steps_completed']}")
                return result
        elif from_step == "m06":
            # Reanudar solo m06: leer output de m05 desde disco
            from script_engine.m05_judge import _resolve_data_paths
            _, sd = _resolve_data_paths(None)
            judge_path = sd / topic_id / "05_judge.json"
            if not judge_path.exists():
                raise FileNotFoundError(
                    f"fase1.5: --from m06 requiere 05_judge.json existente en {judge_path}"
                )
            judge_result = json.loads(judge_path.read_text(encoding="utf-8"))
            result["judge_verdict"] = judge_result.get("global_verdict", "?")

        # m06 — clasificador + assembler (siempre, salvo --from no llegue acá)
        if from_step in ("m01a", "m01b", "normalizer_gate", "audio", "m07", "m03", "m05", "m06"):
            print(f"  [06] Clasificando issues + decisión interactiva...")
            m06_result = classify_and_decide(topic_id, judge_result, interactive=True)
            result["steps_completed"].append("m06")
            result["m06_decision"] = m06_result.get("decision")
            result["final_path"] = m06_result.get("final_path")
            if m06_result.get("rerun_command"):
                result["rerun_command"] = m06_result["rerun_command"]

        result["status"] = "PASS"
        print(f"\n  ✅ Topic {topic_id} OK — pasos: {result['steps_completed']}")

    except Exception as e:
        result["status"] = "FAIL"
        result["error"] = f"{type(e).__name__}: {e}"
        print(f"\n  ❌ Topic {topic_id} FAIL en {from_step}: {result['error']}")

    return result


# ═══════════════════════════════════════════════════════════════
#  MENÚ DE SELECCIÓN DE TEMA (chat 35)
# ═══════════════════════════════════════════════════════════════

def _select_topic_interactive() -> str | None:
    """Lista los topics con status='validated' de topics_db.json y deja elegir
    UNO. Devuelve el topic_id elegido, o None si no hay validados / se cancela.

    NO consume APIs — solo lee topics_db.json.
    """
    if not TOPICS_DB.exists():
        print(f"\n  ❌ No existe {TOPICS_DB}. Corré `python fase1.py` primero.")
        return None

    try:
        data = json.loads(TOPICS_DB.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        print(f"\n  ❌ {TOPICS_DB} ilegible (JSON inválido).")
        return None

    topics = [t for t in data.get("topics", []) if t.get("status") == "validated"]
    if not topics:
        print(f"\n  ⚠ No hay topics con status='validated' en topics_db.json.")
        print(f"     Corré `python fase1.py` para investigar y validar temas.")
        return None

    print(f"\n{'═' * 60}")
    print(f"  🎬 SELECCIÓN DE TEMA — {len(topics)} validado(s)")
    print(f"{'═' * 60}")
    for i, t in enumerate(topics, start=1):
        title = t.get("video_title") or "(sin título)"
        verdict = t.get("market_verdict") or "?"
        vtype = t.get("video_type") or "?"
        print(f"    [{i}] {title}")
        print(f"         veredicto: {verdict}  ·  tipo: {vtype}")
        judge = t.get("judge")
        if judge:
            print(f"         🤖 juez: {judge.get('verdict','?')} "
                  f"({judge.get('cohort','?')})  ·  riesgo: {judge.get('risk','?')}")

    while True:
        choice = input(f"\n  Elegí tema [1-{len(topics)}]  (Q para salir): ").strip()
        if choice.upper() == "Q":
            print(f"\n  Cancelado por el usuario.")
            return None
        if choice.isdigit() and 1 <= int(choice) <= len(topics):
            return topics[int(choice) - 1].get("id")
        print(f"  Inválido. Ingresá un número entre 1 y {len(topics)}, o Q.")


def run_one_topic_from_menu(
    from_step: str = "m01a",
    stop_after_step: str | None = None,
    voting_n: int = 3,
    gate_interactive: bool = True,
    music_gate_interactive: bool = True,
    csv_path: "Path | None" = None,
) -> int:
    """Chat 35 — Punto de entrada interactivo de UN tema.

    Flujo: menú → elegir 1 tema validado → reescribir el CSV con ese único tema
    (para fase2a) → correr la cadena m01a→m06 sobre ese tema.

    Lo usan: fase1_5.main() (cuando se corre SIN --topic) y fase1.py (encadenado
    al final del Latido A). Devuelve exit code (0 ok / cancelado, 1 fail).
    """
    chosen_id = _select_topic_interactive()
    if chosen_id is None:
        return 0

    export_single_topic_csv(chosen_id, csv_path)
    print(f"\n  ✏  CSV reescrito con el tema elegido → {chosen_id}")
    print(f"  Modo: 1 topic (menú) · from_step={from_step}")

    result = process_topic(
        topic_id=chosen_id,
        from_step=from_step,
        voting_n=voting_n,
        gate_interactive=gate_interactive,
        music_gate_interactive=music_gate_interactive,
        stop_after_step=stop_after_step,
    )

    print(f"\n{'═' * 60}")
    if result["status"] == "PASS":
        verdict = result.get("judge_verdict", "—")
        print(f"  ✅ {chosen_id}  (verdict m05: {verdict})")
        print(f"     pasos: {result.get('steps_completed')}")
        print(f"{'═' * 60}\n")
        return 0
    print(f"  ❌ {chosen_id}  ({result.get('error', '?')})")
    print(f"{'═' * 60}\n")
    return 1


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="fase1.5 — orchestrator m01a→m05→m06")
    parser.add_argument("--topic", type=str, default=None,
                        help="Procesar solo este topic_id (default: todos los aprobados del CSV)")
    parser.add_argument("--only", dest="only_step", type=str, default=None,
                        choices=VALID_FROM_STEPS,
                        help="Correr SOLO este módulo (equivale a --from <step> + cortar "
                             "después). Útil para validar 1 módulo aislado sin gastar plata "
                             "en m05/m06 ni arrastrar la cadena.")
    parser.add_argument("--csv", type=str, default=None,
                        help="Path al CSV editado (default: data/fase1_review.csv)")
    parser.add_argument("--voting-n", type=int, default=3,
                        help="Corridas voting de m05 (default: 3)")
    parser.add_argument("--no-gate", dest="no_gate", action="store_true",
                        help="Skipear el gate interactivo del normalizer "
                             "(modo batch nocturno; sospechosos solo se loguean)")
    parser.add_argument("--no-music-gate", dest="no_music_gate", action="store_true",
                        help="Skipear el gate interactivo de m07 music_director "
                             "(modo batch nocturno; todos los tracks generados "
                             "se aprueban automáticamente)")
    args = parser.parse_args()

    # --only <step> equivale a --from <step> + stop_after_step=<step>.
    # Bug fix latente: si --only no se pasa, args.from_step nunca se setea
    # y rompe en process_topic. Default = "m01a" (cadena completa desde el
    # principio).
    if args.only_step is not None:
        args.from_step = args.only_step
        stop_after_step = args.only_step
    else:
        args.from_step = "m01a"
        stop_after_step = None


    # Determinar lista de topics a procesar
    if args.topic:
        topic_ids = [args.topic]
        print(f"\n  Modo: 1 topic específico → {args.topic}")
    else:
        # Chat 35: sin --topic ya NO se procesa batch del CSV. Se muestra el
        # menú interactivo (lee topics_db.json), se elige UN tema, se reescribe
        # el CSV con ese único tema y se corre. Resume puntual: usar --topic.
        sys.exit(run_one_topic_from_menu(
            from_step=args.from_step,
            stop_after_step=stop_after_step,
            voting_n=args.voting_n,
            gate_interactive=not args.no_gate,
            music_gate_interactive=not args.no_music_gate,
            csv_path=Path(args.csv) if args.csv else None,
        ))

    # Procesar cada topic
    results = []
    for tid in topic_ids:
        results.append(process_topic(
            topic_id=tid,
            from_step=args.from_step,
            voting_n=args.voting_n,
            gate_interactive=not args.no_gate,
            music_gate_interactive=not args.no_music_gate,
            stop_after_step=stop_after_step,
        ))
        
    # Resumen final
    print(f"\n{'═' * 60}")
    print(f"  📊 RESUMEN FASE 1.5")
    print(f"{'═' * 60}")
    n_pass = sum(1 for r in results if r["status"] == "PASS")
    n_fail = sum(1 for r in results if r["status"] == "FAIL")
    print(f"  Total: {len(results)}  |  PASS: {n_pass}  |  FAIL: {n_fail}\n")

    for r in results:
        verdict = r.get("judge_verdict", "—")
        if r["status"] == "PASS":
            print(f"  ✅ {r['topic_id']}  (verdict m05: {verdict})")
        else:
            print(f"  ❌ {r['topic_id']}  ({r.get('error', '?')})")

    print()
    sys.exit(0 if n_fail == 0 else 1)


if __name__ == "__main__":
    main()
