"""
fase1_5.py — Orchestrator del motor de guion (m01a → m03 → assemble)

F41 (DECISIONES 2026-10-27 20:59): UNA sola cadena, la de F39 con guion v4, para todo topic (sin flags ni
`guion_version` que la elijan):
  m01a  compuerta del pool → ficha si falta → escaleta
  m01b  guion v4 → reparación → partición (caps y títulos) → papel (m01e) → juez m05
  PARADA del papel salvo `--aprobar-papel` vigente
  normalizer_gate → audio → m07 → m03 → foto madre → assemble (data/scripts/<topic_id>.json, el contrato que lee
  fase2a)
Un topic sin evidence_pool v3 (`_research_v3`, el research v3) para antes de gastar, con su motivo. La cadena vieja
(m01a_skeleton → m01b_narrator) y el guionista v3 (F10) se borraron.

Chat 119: el juez (m05 voting + m06 clasificador/menú [P]/[R]/[E]) fue
DESCONECTADO del chain. m05_judge.py y m06_classifier.py siguen VIVOS en el
repo; para re-enchufarlos → git revert del commit de desconexión (o tag juez-vivo).

Cada módulo persiste su output en data/scripts/_steps/<topic_id>/.

Uso:
  python fase1_5.py                              menú: elegir 1 topic validado y correr la cadena desde m01a
  python fase1_5.py --topic <id> --batch         corre la cadena de 1 topic (hasta la PARADA del papel)
  python fase1_5.py --topic <id> --from normalizer_gate --batch
                                                 con el papel aprobado: voz, música, m03, foto madre y assemble
  python fase1_5.py --topic <id> --only m03      corre SOLO m03 y corta (sin arrastrar la cadena)
  python fase1_5.py --topic <id> --only m01b     corre SOLO m01b y corta
  python fase1_5.py --semilla <s.json> --topic <id_nuevo> --batch
                                                 F39: de la semilla al papel (research → ficha → escaleta → guion →
                                                 caps → papel) y PARADA del papel
  python fase1_5.py --topic <id> --aprobar-papel "Omar <fecha>"
                                                 F39: aprueba el papel (md5); recién ahí sigue a la voz

Flags:
  --topic <id>      Procesar solo el topic con este UUID (default: todos los aprobados del CSV).
  --only <step>     Correr SOLO ese módulo (equivale a --from <step> + cortar después).
  --csv <path>      Path al CSV editado (default: data/fase1_review.csv).
  --no-gate         Modo batch del normalizer_gate (sin CLI interactivo).
  --batch           Desatiende los gates del medio (normalizer_gate + music_gate).

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
from cost_tracker import cost_tracker   # HANDOFF_133: resumen de costo Gemini al cerrar la corrida
from csv_exporter import parse_decisions_csv, OUTPUT_CSV, export_single_topic_csv

# Módulos del motor de guion
import audio_manager
from script_engine import m02_5_normalizer_gate
from script_engine.m03_visual import assign_visual_prompts
# Chat 119: el juez (m05_judge + m06_classifier) fue DESCONECTADO del chain — assemble
# directo tras m03. Los módulos siguen VIVOS en el repo; para re-enchufarlos: git revert
# de este commit (o partir del tag juez-vivo). Ver m06_assembler.assemble_final_script.
from script_engine.m06_assembler import assemble_final_script
from script_engine import m07_music_director

# paso0 EAGER (HANDOFF_132): foto madre debe existir en topics_db ANTES del assemble.
from foto_madre import generate_foto_madre_for_topic
from script_engine.topics_db import load_db, save_db


VALID_FROM_STEPS = ("m01a", "m01b", "normalizer_gate", "audio", "m07", "m03")
STEPS_DIR: Path = DATA_DIR / "scripts" / "_steps"
TOPICS_DB: Path = DATA_DIR / "topics_db.json"

# Orden completo de la cadena (incluye assemble, que VALID_FROM_STEPS no lista).
_PIPELINE_ORDER = ("m01a", "m01b", "normalizer_gate", "audio", "m07", "m03", "assemble")


def _derive_failed_step(from_step: str, steps_completed) -> str | None:
    """YAPA (HANDOFF_134): el paso REAL donde falló = el primer paso (en orden, DESDE
    from_step) que NO quedó en steps_completed. from_step es el paso DESDE donde ARRANCÓ
    la corrida, NO donde falló (rótulo mentiroso: 'FAIL en m01a' para un crash de m03).
    Devuelve None si no es determinable (todos los pasos previstos completaron) → el caller
    imprime un rótulo honesto en vez del mentiroso."""
    done = set(steps_completed or [])
    start = _PIPELINE_ORDER.index(from_step) if from_step in _PIPELINE_ORDER else 0
    return next((s for s in _PIPELINE_ORDER[start:] if s not in done), None)


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
            # F10: guion v3 → el texto con etiquetas de v4 (audio_manager lo manda a Eleven; alinea con `text`)
            **({"narration_tts": ch["narration_tts"]} if ch.get("narration_tts") else {}),
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
#  LA CADENA (F39/F41): compuerta → ficha → escaleta → guion v4 → partición → papel → juez
# ═══════════════════════════════════════════════════════════════

def pool_v3(topic: dict) -> bool:
    """F41: la única cadena necesita el evidence_pool del research v3 (la marca `_research_v3` que pone el research v3
    y que mira la compuerta del pool, `m01a_escaleta.pool_gate_profile`)."""
    return bool((topic.get("evidence_pool") or {}).get("_research_v3"))


def motivo_sin_pool(topic_id: str, topic: dict) -> str:
    """El motivo de la PARADA de un topic sin evidence_pool v3 (antes de gastar nada)."""
    falta = "sin evidence_pool" if not topic.get("evidence_pool") else "el evidence_pool no es del research v3"
    return (f"{topic_id}: {falta} (falta `_research_v3`): la cadena no corre sin el pool del research v3; "
            f"para un tema nuevo, `python fase1_5.py --semilla <archivo> --topic <id_nuevo> --batch`")


def cargar_perfil(topic_id: str) -> bool:
    """F21b: carga el perfil del seed (`_steps/<id>/_perfil.json`) en `research_v3.set_vocabulario` para la escaleta y el
    guion v4 (roles del caso para (b), conteos, tratamientos). Sin perfil, el vocabulario queda vacío. Devuelve si había."""
    from researcher_steps.research_v3 import set_vocabulario
    f = STEPS_DIR / topic_id / "_perfil.json"
    perfil = json.loads(f.read_text(encoding="utf-8")) if f.exists() else None
    set_vocabulario(perfil)
    return perfil is not None


def _topic_v3(topic_id: str) -> dict:
    """El topic con lo que la cadena necesita: el perfil del caso y las notas del analista para la escaleta
    (`_steps/<id>/escaleta_notas.md`, si existe; van como indicaciones, no como reglas)."""
    topic = dict(_load_topic_by_id(topic_id))
    cargar_perfil(topic_id)                                 # F21b: el vocabulario del caso, antes de cualquier bloqueante
    notes = STEPS_DIR / topic_id / "escaleta_notas.md"
    if notes.exists() and not topic.get("escaleta_notas"):
        topic["escaleta_notas"] = notes.read_text(encoding="utf-8").strip()
    return topic


def _step_cost(topic_id: str, label: str, fn):
    """Corre `fn` con el costo medido (cost_tracker) y lo acumula en _steps/<id>/01_v3_costos.json."""
    import time as _time
    from cost_tracker import cost_tracker
    f = STEPS_DIR / topic_id / "01_v3_costos.json"
    costs = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    cost_tracker.start_video(topic_id)
    t0 = _time.time()
    try:
        return fn()
    finally:
        r = cost_tracker.end_video()
        costs.setdefault("_corridas", []).append({"paso": label, "usd": round(getattr(r, "total_cost", 0.0) or 0.0, 4),
                                                  "segundos": round(_time.time() - t0, 1)})
        f.parent.mkdir(parents=True, exist_ok=True)
        f.write_text(json.dumps(costs, ensure_ascii=False, indent=1), encoding="utf-8")


def run_pantalla(topic_id: str, pool: dict | None, log: list[str]) -> dict | None:
    """F36 §C (DECISIONES 2026-10-26 19:54): m01e_pantalla, el guion de pantalla en papel, después de la partición y
    antes de la voz (una llamada a Sonnet por video, con su costo en 01_v3_costos.json como paso «pantalla»). Si no da
    JSON en dos intentos o el tope no alcanza, avisa y Fase 1 sigue: el papel se revisa a mano antes de la voz."""
    from script_engine import m01e_pantalla as mp
    try:
        return _step_cost(topic_id, "pantalla", lambda: mp.generar(topic_id, STEPS_DIR, pool=pool, log=log))
    except (mp.SinJSON, mp.TopePantalla) as e:
        print(f"  [m01e] PARADA del guion en papel: {e}")
        return None


class Parada(RuntimeError):
    """F39: la cadena para a propósito (topic ya existente, compuerta roja, escaleta sin ficha, papel sin aprobar): no
    es una falla del código; el mensaje dice por qué y qué hacer."""


# ═══════════════════════ F39 §A.1: la ficha, entre la compuerta y la escaleta ═══════════════════════

def _titulo_de_semilla(topic: dict) -> str | None:
    """El título de la ficha = el `seed_title` de la semilla (el que usaron F23/F24): el que el topic guardó al
    registrarse (A.3) o, para un topic viejo, el del archivo de semillas por `seed_id`. Nunca se inventa."""
    if topic.get("seed_title"):
        return str(topic["seed_title"])
    f = DATA_DIR / "seeds_archive.json"
    if topic.get("seed_id") and f.exists():
        data = json.loads(f.read_text(encoding="utf-8"))
        # F41: también `archived` (donde research_topics archiva la semilla que investigó: el camino del form)
        filas = ((data.get("seeds") or []) + (data.get("archived") or [])) if isinstance(data, dict) else data
        for s in filas or []:
            if isinstance(s, dict) and s.get("seed_id") == topic["seed_id"] and s.get("seed_title"):
                return str(s["seed_title"])
    return None


def asegurar_ficha(topic_id: str, topic: dict, log: list[str]) -> dict:
    """F39 §A.1: si no hay `ficha_caso.json` con `historia` (ficha v2), se genera con `ficha_caso.run` (modelo y prompt
    vigentes), con su costo como paso «ficha» en 01_v3_costos.json; si ya hay, se usa y no se regenera. Se llama después
    de la compuerta del pool (rojo = no se paga la ficha)."""
    from researcher_steps import ficha_caso as fc
    ficha = fc.load(topic_id, STEPS_DIR)
    if ficha and "historia" in ficha:
        log.append(f"  [ficha] ya hay ficha v2 ({ficha.get('prompt_version')}): se usa")
        return ficha
    titulo = _titulo_de_semilla(topic)
    if not titulo:
        raise Parada(f"{topic_id}: sin ficha v2 y sin seed_title (ni en el topic ni en seeds_archive): no se inventa")
    log.append(f"  [ficha] sin ficha v2 → ficha_caso.run ({fc.MODELO} {fc.ESFUERZO}, prompt {fc.PROMPT_VERSION}) · "
               f"título «{titulo}»")
    res = _step_cost(topic_id, "ficha", lambda: fc.run(topic_id, steps_dir=STEPS_DIR, title=titulo, tag=topic_id))
    log.append(f"  [ficha] {res.get('meta', {}).get('conteos')} · sacados {res.get('meta', {}).get('sacados')}")
    return fc.load(topic_id, STEPS_DIR)


# ═══════════════════════ F39 §A.4: la compuerta del papel (como --aprobar-guion de F33) ═══════════════════════

def _papel_path(topic_id: str) -> Path:
    return STEPS_DIR / topic_id / "01e_pantalla.json"


def md5_papel(papel: dict) -> str:
    """El md5 del contenido del papel sin el campo `aprobado` (JSON con claves ordenadas): un papel regenerado o editado
    cambia su md5 y queda sin aprobar."""
    import hashlib
    sin = {k: v for k, v in papel.items() if k != "aprobado"}
    return hashlib.md5(json.dumps(sin, ensure_ascii=False, sort_keys=True).encode("utf-8")).hexdigest()


def estado_papel(topic_id: str) -> tuple[bool, str]:
    """(aprobado y vigente, por qué). Sin papel no hay nada que aprobar: no pasa."""
    f = _papel_path(topic_id)
    if not f.exists():
        return False, f"no hay papel ({f}): m01e no dejó guion de pantalla, no hay nada que aprobar"
    papel = json.loads(f.read_text(encoding="utf-8"))
    ap = papel.get("aprobado")
    if not ap:
        return False, "el papel no está aprobado"
    if ap.get("md5") != md5_papel(papel):
        return False, (f"el papel cambió después de la aprobación de {ap.get('por')} ({ap.get('fecha')}): md5 "
                       f"{str(ap.get('md5'))[:8]}… → {md5_papel(papel)[:8]}…")
    return True, f"papel aprobado por {ap.get('por')} ({ap.get('fecha')}), md5 {str(ap.get('md5'))[:8]}…"


def aprobar_papel(topic_id: str, quien_fecha: str) -> dict:
    """`--aprobar-papel "QUIÉN FECHA"`: escribe `aprobado: {por, fecha, md5}` en 01e_pantalla.json; no corre nada más."""
    f = _papel_path(topic_id)
    if not f.exists():
        raise Parada(f"{topic_id}: no hay papel que aprobar ({f})")
    papel = json.loads(f.read_text(encoding="utf-8"))
    partes = quien_fecha.split()
    por, fecha = (" ".join(partes[:-1]), partes[-1]) if len(partes) > 1 else (quien_fecha, None)
    import time as _time
    papel["aprobado"] = {"por": por, "fecha": fecha or _time.strftime("%Y-%m-%d %H:%M"), "md5": md5_papel(papel)}
    f.write_text(json.dumps(papel, ensure_ascii=False, indent=1), encoding="utf-8")
    return papel["aprobado"]


def parada_del_papel(topic_id: str) -> str:
    """El mensaje de la PARADA del papel: por qué, dónde leerlo y el comando para aprobarlo."""
    _, motivo = estado_papel(topic_id)
    md = STEPS_DIR / topic_id / "01e_pantalla.md"
    return (f"PARADA del papel: {motivo}.\n"
            + (f"     Leer: {md}\n" if md.exists() else "")
            + f"     Aprobar: python fase1_5.py --topic {topic_id} --aprobar-papel \"Omar <fecha>\"")


# ═══════════════════════ F39 §A.3: arrancar desde una semilla ═══════════════════════

def leer_semilla(path: Path) -> dict:
    """La semilla de un archivo: el dict de la semilla (con `seed_id` y `seed_title`)."""
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(data, dict) and "seed" in data and isinstance(data["seed"], dict):
        data = data["seed"]
    if not isinstance(data, dict) or not data.get("seed_id") or not data.get("seed_title"):
        raise Parada(f"{path}: no es una semilla (falta seed_id o seed_title)")
    return data


def research_de_semilla(semilla: Path, topic_id: str) -> dict:
    """F39 §A.3: investiga UNA semilla en un topic dado (topic_researcher.investigar_semilla) y la registra en
    topics_db con ese id. No pisa nada: si `_steps/<id>/` ya existe o el id ya está en topics_db, PARADA. Antes,
    respaldo de topics_db como topics_db.pre_<id>.json. La compuerta roja del pool es PARADA con sus motivos."""
    import shutil
    seed = leer_semilla(semilla)
    if (STEPS_DIR / topic_id).exists():
        raise Parada(f"{topic_id}: ya existe {STEPS_DIR / topic_id} (no se pisa)")
    if TOPICS_DB.exists() and any(t.get("id") == topic_id for t in
                                  json.loads(TOPICS_DB.read_text(encoding="utf-8")).get("topics") or []):
        raise Parada(f"{topic_id}: ya está en topics_db (no se pisa)")
    if TOPICS_DB.exists():
        shutil.copy2(TOPICS_DB, TOPICS_DB.with_name(f"topics_db.pre_{topic_id}.json"))
    print(f"  [semilla] «{seed['seed_title']}» ({seed['seed_id']}) → topic {topic_id}")
    import topic_researcher as tr
    from researcher_steps.pool_gate import PoolGateRed
    try:
        topic = _step_cost(topic_id, "research", lambda: tr.investigar_semilla(seed, topic_id))
    except PoolGateRed as e:
        raise Parada(f"{topic_id}: compuerta del pool ROJA: {'; '.join(e.gate.get('motivos') or [])}") from e
    print(f"  [semilla] topic registrado: {topic.get('video_title')!r}")
    return topic


def run_escaleta_v3(topic_id: str, columna: bool = False, modelo: str | None = None) -> dict:
    """m01a v3: compuerta del pool (rojo → PoolGateRed, sin gastar) + escaleta (Pro, con reintentos).
    F17: con ficha v2, m01a era columna → escaleta. F22d (decisión del analista): la columna ya no alimenta a la
    escaleta (la escaleta va siempre sin columna); con `columna=True` (`--columna`) se genera además la columna como
    página de lectura (`_steps/<id>/COLUMNA_<id>.md` + `01a_columna.json`), después de la escaleta y sin pasarla."""
    from script_engine import m01a_escaleta as me
    from researcher_steps.pool_gate import PoolGateRed
    topic = _topic_v3(topic_id)
    log: list[str] = []
    if not (topic.get("escaleta_frozen") or me._frozen_is_escaleta(topic)):   # F39 §A.1: compuerta → ficha → escaleta
        try:
            me.pool_gate_profile(topic, topic.get("evidence_pool") or {}, log=log)   # rojo = no se paga la ficha
        except PoolGateRed as e:
            raise Parada(f"{topic_id}: compuerta del pool ROJA: {'; '.join(e.gate.get('motivos') or [])}") from e
        asegurar_ficha(topic_id, topic, log)
        print("\n".join(log))
        log.clear()
    try:
        esc = _step_cost(topic_id, "escaleta", lambda: me.generate_escaleta(topic, log=log, columna=None,
                                                                            modelo=modelo))
    except me.EscaletaSinFicha as e:                         # F39 §A.2: sin ficha v2 la escaleta no corre
        raise Parada(f"escaleta sin ficha: {e}") from e
    if columna:
        from researcher_steps.ficha_caso import load as load_ficha
        from script_engine import m01a_columna as mc
        ficha = load_ficha(topic_id, STEPS_DIR)
        if ficha and "historia" in ficha:
            col = _step_cost(topic_id, "columna", lambda: mc.generate_columna(topic, topic["evidence_pool"], ficha,
                                                                               log=log))
            (STEPS_DIR / topic_id / f"COLUMNA_{topic_id}.md").write_text(
                mc.to_markdown(col, topic.get("video_title") or topic_id), encoding="utf-8")
        else:
            log.append("  [columna] sin ficha v2: no se genera")
    print("\n".join(log[-8:]))
    return esc


def run_guion_v4(topic_id: str, modelo: str | None = None, editor: bool = False) -> dict:
    """F11: m01b v4: guionista v4 (UNA llamada) → reparación (una ronda: cap, oración, fechas, editor) → m01d_particion
    → juez m05. Escribe 01b_guionista_v4 (texto, bloqueantes antes/después, pasos), 01a_skeleton, 01b_narration,
    01b_narracion_v3 y 06_judge_narrative. Si quedan bloqueantes, se reportan (no hay segunda ronda).
    F11b: `modelo` (`--modelo`) = el de toda la cadena v4 (guionista + reparación); la partición y el juez, los de
    siempre.
    F27: `editor` (`--editor`) = la pasada del editor m01c en la reparación (fuera del camino por defecto)."""
    from script_engine import guion_v4 as g4
    from script_engine import m01d_particion as md
    from script_engine.m05_narrative import judge_narration
    topic = _topic_v3(topic_id)
    pool = topic["evidence_pool"]
    esc = _load_step_output(topic_id, "01a_escaleta.json")
    log: list[str] = []
    d = STEPS_DIR / topic_id
    call = g4.call_for(modelo or g4.DEFAULT_MODELO_GUION)  # F22d/F22e: sin --modelo, el del guion (Fable 5.1)
    from researcher_steps.ficha_caso import load as load_ficha
    ficha = load_ficha(topic_id, STEPS_DIR)                  # F14: si hay ficha, el texto de los ids sale de ella
    g = _step_cost(topic_id, "guionista_v4", lambda: g4.write(topic, esc, call=call, log=log, ficha=ficha))
    r = _step_cost(topic_id, "reparacion_v4", lambda: g4.reparar(topic, esc, g["parrafos"], call=call, log=log,
                                                                         ficha=ficha, editor=editor))
    out = {**g, "reparacion": r, "metricas": g4.metricas(topic, esc, r["parrafos"]), "nota_b": g4.nota_b()}
    (d / "01b_guionista_v4.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
    part = _step_cost(topic_id, "particion", lambda: md.particionar(topic, esc, r["parrafos"], pool, log=log,
                                                                     shorten=md.editor_shorten()))
    pantalla = run_pantalla(topic_id, pool, log)                 # F36 §C: después de la partición, antes de la voz
    judge = judge_narration(topic_id, pool=pool, narration=part["narration"], skeleton=part["skeleton"])
    print("\n".join(log[-12:]))
    if out["nota_b"]:
        print(f"  [v4] {out['nota_b']}")
    if r["parada"]:
        print(f"  [v4] quedan {len(r['bloqueantes_despues'])} bloqueante(s) después de la ronda única: PARADA")
    return {"guionista": g, "reparacion": r, "particion": part, "pantalla": pantalla, "juez": judge}


# ═══════════════════════════════════════════════════════════════
#  PIPELINE POR TOPIC
# ═══════════════════════════════════════════════════════════════

def process_topic(
    topic_id: str,
    from_step: str = "m01a",
    gate_interactive: bool = True,
    music_gate_interactive: bool = True,
    stop_after_step: str | None = None,
    modelo: str | None = None,
    columna: bool = False,
    modelo_escaleta: str | None = None,
    editor: bool = False,
) -> dict:
    """Corre LA cadena (F41: la única) para 1 topic, reanudando desde from_step: m01a (compuerta → ficha → escaleta)
    → m01b (guion v4 → partición → papel → juez) → PARADA del papel salvo aprobado → normalizer_gate → audio → m07 →
    m03 → foto madre → assemble. Un topic sin evidence_pool v3 → PARADA antes de gastar, desde cualquier paso.

    Chat 119: el juez (m05 + m06) fue DESCONECTADO — tras m03 se ensambla directo el
    JSON final con assemble_final_script. Los módulos del juez siguen vivos en el repo.

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
            validar 1 módulo aislado sin arrastrar la cadena.
        modelo: F11b `--modelo`, el de la cadena v4 (guionista + reparación); None = el del guion.
        columna, modelo_escaleta: F22d `--columna`, F25c `--modelo-escaleta` (la escaleta).
        editor: F27 `--editor`, la pasada del editor m01c en la reparación del guion v4.

    Returns:
      dict {topic_id, steps_completed: list[str], status: 'PASS'|'FAIL', error?: str}
    """
    print(f"\n{'═' * 60}")
    print(f"  📜 Procesando topic {topic_id} desde {from_step}")
    print(f"{'═' * 60}")

    result = {"topic_id": topic_id, "steps_completed": [], "status": "RUNNING"}

    try:
        # F41: una sola cadena; sin el pool del research v3 no corre nada (PARADA antes de gastar, desde cualquier paso)
        topic = _load_topic_by_id(topic_id)
        if not pool_v3(topic):
            raise Parada(motivo_sin_pool(topic_id, topic))
        skeleton = narration = None                          # se cargan abajo si hace falta

        # m01a — compuerta del pool → ficha si falta → escaleta
        if from_step == "m01a":
            print(f"  [01a] Compuerta del pool + ficha si falta + escaleta...")
            run_escaleta_v3(topic_id, columna=columna, modelo=modelo_escaleta)
            result["steps_completed"].append("m01a")
            if stop_after_step == "m01a":
                result["status"] = "PASS"
                print(f"\n  ✅ Topic {topic_id} OK (stop after m01a) — pasos: {result['steps_completed']}")
                return result

        # m01b — guion v4 → reparación (una ronda) → partición (caps y títulos) → papel (m01e) → juez
        if from_step in ("m01a", "m01b"):
            print(f"  [01b] Guion v4 → reparación (una ronda) → partición → papel → juez...")
            ed = {"editor": True} if editor else {}          # F27: sin --editor, la llamada de siempre
            out = run_guion_v4(topic_id, modelo=modelo, **ed) if modelo else run_guion_v4(topic_id, **ed)
            topic = _topic_v3(topic_id)
            skeleton, narration = out["particion"]["skeleton"], out["particion"]["narration"]
            result["steps_completed"].append("m01b")
            if stop_after_step == "m01b":
                result["status"] = "PASS"
                print(f"\n  ✅ Topic {topic_id} OK (stop after m01b) — pasos: {result['steps_completed']}")
                return result

        # F39 §A.4 (DECISIONES 2026-10-26 19:54): nada después de m01b (la voz se paga) sin el papel aprobado y vigente;
        # vale también al reanudar (--from normalizer_gate / audio / m07 / m03).
        ok, motivo = estado_papel(topic_id)
        if not ok:
            print(f"\n  ⏸  {parada_del_papel(topic_id)}")
            result.update(status="PARADA", parada="papel", motivo=motivo)
            return result
        print(f"  [papel] {motivo}")

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

        # paso0 EAGER (HANDOFF_132): la foto madre DEBE existir en topics_db ANTES de que
        # m06 hornee el foto_madre_registry en el contrato. Sin esto, topics nuevos ensamblan
        # registry {} y TODAS las anclas de m03 degradan a t2i (seam detectado en ec3d7c7f).
        # Idempotente: si el PNG existe, skip (reúso built-in de foto_madre.py).
        print(f"  [paso0] Foto madre (sujeto + props anclados)...")
        db = load_db()
        for t in db.get("topics", []):
            if t.get("id") == topic_id:
                generate_foto_madre_for_topic(t, topic_id)   # video_id == topic_id en LONG
                save_db(db)
                break

        # assemble — ensambla data/scripts/<id>.json (contrato sagrado que lee fase2a)
        # DIRECTO tras m03. Chat 119: el juez (m05 voting + m06 clasificador/menú) fue
        # DESCONECTADO del chain. assemble_final_script recibe SOLO topic_id (ya desacoplado
        # del juez) y escribe el JSON final. Gate = MISMO alcance que tenía m06.
        if from_step in ("m01a", "m01b", "normalizer_gate", "audio", "m07", "m03"):
            print(f"  [assemble] Ensamblando data/scripts/{topic_id}.json...")
            final_path = str(assemble_final_script(topic_id))
            result["steps_completed"].append("assemble")
            result["final_path"] = final_path

        result["status"] = "PASS"
        print(f"\n  ✅ Topic {topic_id} OK — pasos: {result['steps_completed']}")

    except Parada as e:                                      # F39: la cadena para a propósito, con el motivo
        result.update(status="PARADA", parada=_derive_failed_step(from_step, result.get("steps_completed")),
                      motivo=str(e))
        print(f"\n  ⏸  PARADA del topic {topic_id}: {e}")
    except Exception as e:
        result["status"] = "FAIL"
        result["error"] = f"{type(e).__name__}: {e}"
        # YAPA (HANDOFF_134): rótulo HONESTO del paso REAL donde falló, no from_step.
        failed_step = _derive_failed_step(from_step, result.get("steps_completed"))
        result["failed_step"] = failed_step
        _label = failed_step or f"(paso desconocido, arrancó en {from_step})"
        print(f"\n  ❌ Topic {topic_id} FAIL en {_label}: {result['error']}")

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
    gate_interactive: bool = True,
    music_gate_interactive: bool = True,
    csv_path: "Path | None" = None,
) -> int:
    """Chat 35 — Punto de entrada interactivo de UN tema.

    Flujo: menú → elegir 1 tema validado → reescribir el CSV con ese único tema
    (para fase2a) → correr LA cadena (F41: la única, sin flags) sobre ese tema.

    Lo usan: fase1_5.main() (cuando se corre SIN --topic) y fase1.py (encadenado
    al final del Latido A). Devuelve exit code (0 ok / cancelado / PARADA del papel,
    2 otra PARADA, 1 fail).
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
        gate_interactive=gate_interactive,
        music_gate_interactive=music_gate_interactive,
        stop_after_step=stop_after_step,
    )

    print(f"\n{'═' * 60}")
    if result["status"] == "PASS":
        print(f"  ✅ {chosen_id}")
        print(f"     pasos: {result.get('steps_completed')}")
        print(f"{'═' * 60}\n")
        _print_gemini_cost()
        return 0
    if result["status"] == "PARADA":                         # F41: la cadena única para en el papel (0) u otra (2)
        print(f"  ⏸  {chosen_id}  (PARADA en {result.get('parada')}: {result.get('motivo')})")
        print(f"{'═' * 60}\n")
        _print_gemini_cost()
        return 0 if result.get("parada") == "papel" else 2
    print(f"  ❌ {chosen_id}  ({result.get('error', '?')})")
    print(f"{'═' * 60}\n")
    _print_gemini_cost()
    return 1


def _print_gemini_cost() -> None:
    """HANDOFF_133: resumen de costo Gemini al cerrar la corrida (m03 corre 2.5-pro).
    Defensivo: nunca rompe el cierre por un fallo de telemetría."""
    try:
        cost_tracker.print_gemini_report()
    except Exception:
        pass


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════

def temas_cmds(temas: list[str], argv: list[str]) -> list[list[str]]:
    """F26 §C: un comando por tema: los mismos argumentos sin `--temas`/`--topic`, con `--topic <tema>` y `--batch`
    (los gates interactivos no se pueden contestar desde varios procesos a la vez)."""
    base, skip = [], False
    for a in argv:
        if skip:
            skip = False
            continue
        if a in ("--temas", "--topic"):
            skip = True
            continue
        if a.startswith(("--temas=", "--topic=")):
            continue
        base.append(a)
    if "--batch" not in base:
        base.append("--batch")
    return [[sys.executable, str(Path(__file__).resolve()), *base, "--topic", t] for t in temas]


def run_temas(temas: list[str], argv: list[str], popen=None) -> int:
    """F26 §C: `--temas a,b,c`: lanza un proceso por tema a la vez (log en _steps/<tema>/fase1_5_temas.log) y
    espera a todos. Devuelve 0 si todos terminaron bien."""
    import subprocess
    popen = popen or subprocess.Popen
    procs = []
    for t, cmd in zip(temas, temas_cmds(temas, argv)):
        (STEPS_DIR / t).mkdir(parents=True, exist_ok=True)
        fh = open(STEPS_DIR / t / "fase1_5_temas.log", "w", encoding="utf-8")
        procs.append((t, popen(cmd, stdout=fh, stderr=subprocess.STDOUT), fh))
        print(f"  [temas] {t}: pid {procs[-1][1].pid}")
    malos = 0
    for t, p, fh in procs:
        rc = p.wait()
        fh.close()
        malos += int(rc != 0)
        print(f"  [temas] {'✅' if rc == 0 else '❌'} {t} (exit {rc})")
    return 0 if malos == 0 else 1


def main():
    parser = argparse.ArgumentParser(description="fase1.5 — orchestrator m01a→m03→assemble")
    parser.add_argument("--topic", type=str, default=None,
                        help="Procesar solo este topic_id (default: todos los aprobados del CSV)")
    parser.add_argument("--only", dest="only_step", type=str, default=None,
                        choices=VALID_FROM_STEPS,
                        help="Correr SOLO este módulo (equivale a --from <step> + cortar "
                             "después). Útil para validar 1 módulo aislado sin arrastrar la cadena.")
    parser.add_argument("--from", dest="from_arg", type=str, default=None, choices=VALID_FROM_STEPS,
                        help="F10: reanudar desde este módulo y seguir la cadena hasta assemble")
    parser.add_argument("--csv", type=str, default=None,
                        help="Path al CSV editado (default: data/fase1_review.csv)")
    parser.add_argument("--no-gate", dest="no_gate", action="store_true",
                        help="Skipear el gate interactivo del normalizer "
                             "(modo batch nocturno; sospechosos solo se loguean)")
    parser.add_argument("--no-music-gate", dest="no_music_gate", action="store_true",
                        help="Skipear el gate interactivo de m07 music_director "
                             "(modo batch nocturno; todos los tracks generados "
                             "se aprueban automáticamente)")
    parser.add_argument("--modelo", choices=("gemini-pro", "gpt-6.1-sol", "gpt-6-astra", "gemini-4-argon",
                                             "claude-opus-5-5", "claude-fable-5-1"), default=None,
                        help="F11b: el modelo del guion v4 (guionista + reparación); por defecto el del guion; el juez "
                             "es el de siempre")
    parser.add_argument("--modelo-escaleta", dest="modelo_escaleta", choices=("claude-fable-5-1", "claude-opus-5-5",
                                                                           "gpt-6.1-sol"), default=None,
                        help="F25c: el modelo de la escaleta v2 (con ficha); por defecto claude-fable-5-1")
    parser.add_argument("--sin-columna", dest="sin_columna", action="store_true",
                        help="F17; F22d: es el camino por defecto (la escaleta va siempre sin columna); se acepta y no "
                             "cambia nada")
    parser.add_argument("--columna", action="store_true",
                        help="F22d: además de la escaleta (sin columna), genera la columna vertebral como página de "
                             "lectura COLUMNA_<id>.md; no se le pasa a la escaleta")
    parser.add_argument("--batch", action="store_true",
                        help="Modo batch desatendido: desactiva los gates del medio "
                             "(normalizer_gate + music_gate). Equivale a "
                             "--no-gate --no-music-gate.")
    parser.add_argument("--editor", action="store_true",
                        help="F27: la pasada del editor m01c en la reparación del guion v4 (fuera del camino desde "
                             "F27; solo para leer)")
    parser.add_argument("--temas", type=str, default=None,
                        help="F26 §C: varios topic_id separados por coma; cada uno corre en su propio proceso (el "
                             "perfil del caso es un global de proceso) con los mismos argumentos y --batch")
    parser.add_argument("--semilla", type=str, default=None, metavar="ARCHIVO.json",
                        help="F39 §A.3: con --topic <id> nuevo, investiga primero esa semilla en ese topic (research v3 + "
                             "4a–4e, registro en topics_db con respaldo topics_db.pre_<id>.json) y sigue la cadena: "
                             "compuerta → ficha si falta → escaleta → guion → caps y títulos → papel → PARADA del papel. "
                             "Si _steps/<id>/ o el id ya existen, PARADA (no pisa nada)")
    parser.add_argument("--aprobar-papel", dest="aprobar_papel", type=str, default=None, metavar='"QUIÉN FECHA"',
                        help="F39 §A.4: escribe `aprobado: {por, fecha, md5}` en _steps/<id>/01e_pantalla.json (la "
                             "compuerta antes de la voz: sin eso, nada corre después de m01b) y no corre nada más")
    args = parser.parse_args()
    if args.aprobar_papel is not None:                      # F39 §A.4: solo aprueba
        if not args.topic:
            parser.error("--aprobar-papel necesita --topic")
        try:
            ap = aprobar_papel(args.topic, args.aprobar_papel)
        except Parada as e:
            print(f"  ⏸  {e}")
            sys.exit(2)
        print(f"  ✓ papel de {args.topic} aprobado por {ap['por']} ({ap['fecha']}) · md5 {ap['md5']}")
        sys.exit(0)
    if args.semilla is not None and not args.topic:
        parser.error("--semilla necesita --topic <id> (un topic nuevo)")
    if args.semilla is not None and (args.from_arg or args.only_step):
        parser.error("--semilla arranca desde el research: no va con --from ni --only")
    if args.temas:
        sys.exit(run_temas([t.strip() for t in args.temas.split(",") if t.strip()], sys.argv[1:]))

    # --batch desatiende los gates del medio de una (normalizer + music).
    gate_interactive = not (args.no_gate or args.batch)
    music_gate_interactive = not (args.no_music_gate or args.batch)

    # --only <step> equivale a --from <step> + stop_after_step=<step>.
    # Bug fix latente: si --only no se pasa, args.from_step nunca se setea
    # y rompe en process_topic. Default = "m01a" (cadena completa desde el
    # principio).
    if args.only_step is not None:
        args.from_step = args.only_step
        stop_after_step = args.only_step
    else:
        args.from_step = args.from_arg or "m01a"
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
            gate_interactive=gate_interactive,
            music_gate_interactive=music_gate_interactive,
            csv_path=Path(args.csv) if args.csv else None,
        ))

    if args.semilla is not None:                            # F39 §A.3: research de la semilla en el topic dado
        try:
            research_de_semilla(Path(args.semilla), args.topic)
        except Exception as e:                              # F39 §B.3: una falla del research es PARADA con su error
            print(f"\n  ⏸  PARADA en research: {e if isinstance(e, Parada) else f'{type(e).__name__}: {e}'}")
            _print_gemini_cost()
            sys.exit(2)

    # Procesar cada topic
    results = []
    for tid in topic_ids:
        results.append(process_topic(
            topic_id=tid,
            from_step=args.from_step,
            gate_interactive=gate_interactive,
            music_gate_interactive=music_gate_interactive,
            stop_after_step=stop_after_step,
            modelo=args.modelo,
            columna=args.columna,
            modelo_escaleta=args.modelo_escaleta,
            editor=args.editor,
        ))
        
    # Resumen final
    print(f"\n{'═' * 60}")
    print(f"  📊 RESUMEN FASE 1.5")
    print(f"{'═' * 60}")
    n_pass = sum(1 for r in results if r["status"] == "PASS")
    n_fail = sum(1 for r in results if r["status"] == "FAIL")
    n_par = sum(1 for r in results if r["status"] == "PARADA")
    print(f"  Total: {len(results)}  |  PASS: {n_pass}  |  PARADA: {n_par}  |  FAIL: {n_fail}\n")

    for r in results:
        if r["status"] == "PASS":
            print(f"  ✅ {r['topic_id']}")
        elif r["status"] == "PARADA":                       # F39: para a propósito (papel sin aprobar, compuerta…)
            print(f"  ⏸  {r['topic_id']}  (PARADA en {r.get('parada')}: {r.get('motivo')})")
        else:
            print(f"  ❌ {r['topic_id']}  ({r.get('error', '?')})")

    print()
    _print_gemini_cost()
    # F39: la PARADA del papel es el final esperado de Fase 1 (0); otra PARADA, 2; una falla, 1
    otra_parada = any(r["status"] == "PARADA" and r.get("parada") != "papel" for r in results)
    sys.exit(1 if n_fail else 2 if otra_parada else 0)


if __name__ == "__main__":
    main()
