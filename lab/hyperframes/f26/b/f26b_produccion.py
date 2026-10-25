"""F26 §B — producción del primer video: Vajont, con el guion gvE2 de F25c (2,355 palabras) por el camino normal.

Etapas (cada una idempotente; log en lab/hyperframes/f26/b/produccion.log, costos en costos_f26b.json):
    preparar   respaldo de topics_db (data/topics_db.pre_f26.json) y de los pasos viejos de `_steps/f8s3-vajont/`
               (→ `_pre_f26/`); 4a–4e sobre el pool v3 de F24 (Gemini, como `topic_researcher._research_seed_deep`
               después de `run_seed`); topic `f8s3-vajont` agregado a topics_db con el título provisional del handoff
               y `guion_version` 4; la escaleta vE2 pasa a `01a_escaleta.json` y el guion a `01b_guionista_v4.json`.
    particion  `m01d_particion.particionar` (7 caps, intents desde la escaleta) SIN el recorte del editor
               (`shorten=None`): la partición no reescribe nada; lo que mueve, se anota.
    guion      `fase1_5.process_topic` desde normalizer_gate hasta m07 (TTS ElevenLabs v4 «MS Narrador» con tts_tags del
               intent de cada cap; música fija a los `*_curated` de audio_library: sin música nueva), y después desde
               m03 hasta assemble con `m03_visual.SECONDS_PER_IMAGE_TARGET` subido para que el total de imágenes
               (repartido por la duración REAL de cada cap) no pase de IMAGENES_PLAN (parámetro, no lógica).
    imagenes   `fase2a.py --topic f8s3-vajont` (Seedream 5.0 Lite + Veo ch01/ch07).
    render     Firefox cerrado y RAM libre > 14 GB; `fase2b.py f8s3-vajont --keep-segments --gfx --gfx-sparse
               --gfx-quality looks`; si el gfx se rompe, se apaga el gfx para este video (`fase2b.py` sin --gfx).
Uso: PYTHONIOENCODING=utf-8 python -I lab/hyperframes/f26/b/f26b_produccion.py --etapa <etapa>
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path[:0] = [str(ROOT)]
os.chdir(ROOT)
TID = "f8s3-vajont"
TITULO = "Vajont: la montaña que caminaba"
LAB = Path(__file__).resolve().parent
HF = LAB.parent.parent
DB = ROOT / "data" / "topics_db.json"
STEPS = ROOT / "data" / "scripts" / "_steps" / TID
ESC = HF / "f25c" / "vE2" / "escaleta.json"
GUION = HF / "f25c" / "gvE2" / "resultado.json"
IMAGENES_PLAN = 92                  # tope 100 del handoff, con margen para las re-hechuras del guardia de visión
TOPE_GEMINI = 5.00
COSTOS = LAB / "costos_f26b.json"
_YA: dict[str, float] = {}


class Parada(RuntimeError):
    pass


def _j(p: Path):
    return json.loads(p.read_text(encoding="utf-8")) if p.exists() else None


def _w(p: Path, obj) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2, default=str), encoding="utf-8")


def _costos() -> dict:
    return _j(COSTOS) or {"etapas": {}}


def _anotar_costos(etapa: str, extra: dict | None = None) -> dict:
    """Lo que anotó el cost_tracker de este proceso, por servicio."""
    from cost_tracker import cost_tracker
    por: dict[str, float] = {}
    for e in cost_tracker._all_entries():
        por[e.service] = por.get(e.service, 0.0) + e.total_cost
    tot = dict(por)
    por = {k: round(v - _YA.get(k, 0.0), 4) for k, v in por.items() if round(v - _YA.get(k, 0.0), 4)}
    _YA.update(tot)                                   # cada etapa anota solo lo suyo (el tracker acumula el proceso)
    c = _costos()
    c["etapas"][etapa] = {"por_servicio": por, "usd": round(sum(por.values()), 4), **(extra or {})}
    c["usd"] = round(sum(x.get("usd") or 0 for x in c["etapas"].values()), 4)
    c["gemini_usd"] = round(sum(v for x in c["etapas"].values() for k, v in (x.get("por_servicio") or {}).items()
                                if "gemini" in k.lower()), 4)
    _w(COSTOS, c)
    return c


def _freno_gemini(peor: float, que: str) -> None:
    g = _costos().get("gemini_usd") or 0.0
    if g + peor > TOPE_GEMINI:
        raise Parada(f"tope Gemini ({que}): gastado {g:.3f} + peor caso {peor:.2f} > {TOPE_GEMINI:.2f}")


def _seed() -> dict:
    s = _j(ROOT / "data" / "selected_seeds.json")["seeds"]
    return next(x for x in s if x.get("seed_id") == TID)


def preparar(log: list[str]) -> None:
    if not (ROOT / "data" / "topics_db.pre_f26.json").exists():
        shutil.copy2(DB, ROOT / "data" / "topics_db.pre_f26.json")
    db = _j(DB)
    if any(t.get("id") == TID for t in db["topics"]):
        log.append("preparar: el topic ya está en topics_db")
    else:
        _freno_gemini(0.60, "4a–4e")
        from researcher_steps import research_v3 as rv
        from researcher_steps.step_4a_facts import extract_facts_and_sources
        from researcher_steps.step_4b_canonical import extract_canonical
        from researcher_steps.step_4c_meta import extract_meta
        from researcher_steps.step_4d_summary import extract_research_summary
        from researcher_steps.step_4e_visual_canon import extract_visual_canon
        import fase1_5 as f15
        seed = _seed()
        pool = _j(STEPS / "00_pool_v3.json")
        f15.cargar_perfil(TID)
        blocks = rv.pool_to_blocks(pool)
        out: dict = {}
        cache = LAB / "_4a_4e.json"                      # para no volver a pagar si una etapa posterior falla
        out = _j(cache) or {}
        if "4a" not in out:
            out["4a"] = extract_facts_and_sources(blocks, with_pool=False)
            _w(cache, out)
        facts = out["4a"].get("verified_facts", [])
        if "4b" not in out:
            out["4b"] = extract_canonical(seed, blocks, facts)
            _w(cache, out)
        canonical = out["4b"].get("canonical_subject_description", "")
        if "4c" not in out:
            out["4c"] = extract_meta(seed, blocks, facts, canonical)
            _w(cache, out)
        if "4d" not in out:
            out["4d"] = extract_research_summary(seed, blocks, facts, canonical, out["4c"])
            _w(cache, out)
        if "4e" not in out:
            out["4e"] = extract_visual_canon(seed, blocks, facts, canonical)
            _w(cache, out)
        for k, name in (("4a", "01_facts_sources"), ("4b", "02_canonical"), ("4c", "03_meta"), ("4d", "04_summary"),
                        ("4e", "05_visual_canon")):
            _w(STEPS / f"{name}.json", out[k] if k != "4a" else {**out[k], "evidence_pool": pool})
        c4, e4 = out["4c"], out["4e"]
        t = {"id": TID, "video_id": TID, "seed_id": TID,
             **{k: seed.get(k) for k in ("discovery_mode", "root_niche", "tags")},
             "video_title": TITULO, "titulo_4c": c4.get("video_title"),
             "search_keyword": c4.get("search_keyword") or "Vajont", "hook": c4.get("hook", ""),
             "mystery": c4.get("mystery", ""), "reveal": c4.get("reveal", ""), "angle": c4.get("angle", ""),
             "virality_score": c4.get("virality_score", 5), "canonical_subject_description": canonical,
             "research_summary": out["4d"].get("research_summary", ""), "sources": out["4a"].get("sources", []),
             "verified_facts": facts, "evidence_pool": pool, "era_visual_canon": e4.get("era_visual_canon", {}),
             "documented_people": e4.get("documented_people", []),
             "anachronism_blocklist": e4.get("anachronism_blocklist", []),
             "documented_props": e4.get("documented_props", []),
             "central_subject": e4.get("central_subject", {"kind": "other", "foto_madre": ""}),
             "research_version": 3, "guion_version": 4, "status": "validated", "idioma": "español neutro",
             "f26_nota": "F26 §B: primer video; guion gvE2 (F25c), escaleta vE2; topic armado desde el pool de F24",
             "created_at": time.strftime("%Y-%m-%dT%H:%M:%S")}
        db = _j(DB)
        db["topics"].append(t)
        DB.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding="utf-8")
        log.append(f"preparar: topic {TID} agregado a topics_db («{TITULO}»; 4c proponía «{c4.get('video_title')}»)")
    pre = STEPS / "_pre_f26"
    if not pre.exists():
        pre.mkdir()
        for n in ("01a_escaleta.json", "01a_skeleton.json", "01b_narration.json", "01b_narracion_v3.json"):
            if (STEPS / n).exists():
                shutil.move(str(STEPS / n), str(pre / n))
        log.append(f"preparar: pasos viejos → {pre}")
    shutil.copy2(ESC, STEPS / "01a_escaleta.json")
    g = _j(GUION)
    _w(STEPS / "01b_guionista_v4.json", {"parrafos": g["parrafos"], "fuente": "lab/hyperframes/f25c/gvE2 (F25c)",
                                          "bloqueantes": g.get("bloqueantes"), "metricas": g.get("metricas")})
    _anotar_costos("preparar")


def _topic():
    import fase1_5 as f15
    t = f15._load_topic_by_id(TID)
    if not f15.cargar_perfil(TID):
        raise Parada("sin _perfil.json")
    t["guion_version"] = 4
    return t


def particion(log: list[str]) -> None:
    from script_engine import m01d_particion as md
    _freno_gemini(0.05, "títulos de la partición")
    topic = _topic()
    esc = _j(STEPS / "01a_escaleta.json")
    parrafos = _j(STEPS / "01b_guionista_v4.json")["parrafos"]
    lg: list[str] = []
    part = md.particionar(topic, esc, parrafos, topic["evidence_pool"], log=lg, shorten=None)
    caps = part["narration"]["chapters"] if isinstance(part["narration"], dict) else part["narration"]
    res = {"notas": part.get("notas"), "log": lg,
           "caps": [{"cap": c.get("chapter_number"), "intent": c.get("narrative_intent"),
                     "titulo": c.get("title") or c.get("chapter_title"),
                     "palabras": len((c.get("narration") or "").split())} for c in caps]}
    # ¿la partición movió párrafos de cap? (comparar con el cap de cada párrafo en el guion)
    orig = {}
    for p in parrafos:
        orig[p["cap"]] = orig.get(p["cap"], 0) + len(p["texto"].split())
    res["palabras_guion_por_cap"] = orig
    _w(LAB / "particion.json", res)
    log.append("particion: " + " · ".join(f"{c['cap']} {c['intent']} {c['palabras']}p" for c in res["caps"])
               + f" · notas {part.get('notas')}")
    _anotar_costos("particion")


def _music_curated(topic_id, sync_map, interactive=True):
    """F26: la música que ya usa el pipeline (audio_library/<intent>_curated), sin matcher ni generación."""
    from datetime import datetime
    from script_engine import m07_music_director as m7
    lib = {t["track_id"]: t for t in m7._load_library()}
    tracks = {}
    for ch in sync_map.get("chapters", []):
        tid = f"{ch.get('narrative_intent')}_curated"
        tracks[ch["id"]] = ({"track_id": tid, "mp3_path": f"audio_library/{lib[tid]['mp3_filename']}",
                             "match_source": "reused", "match_score": None,
                             "reasoning": "F26: track curado del intent (sin música nueva)"} if tid in lib else
                            {"track_id": None, "mp3_path": None, "match_source": "skipped", "match_score": None,
                             "reason": f"F26: no hay {tid} en audio_library"})
    mm = {"video_id": topic_id, "profile": sync_map.get("profile", ""), "generated_at": datetime.now().isoformat(),
          "total_chapters": len(tracks), "tracks_by_chapter": tracks}
    m7._persist_music_map(topic_id, mm)
    return mm


def _plan_imagenes(sync_map: dict) -> tuple[float, dict]:
    from script_engine import m03_visual as mv
    durs = {int(str(c["id"]).lstrip("ch")): float(c["duration_sec"]) for c in sync_map["chapters"]}
    spi = 7.0
    while True:
        mv.SECONDS_PER_IMAGE_TARGET = spi
        por = {n: (1 + mv._calculate_flux_extras_count(d)) if n in mv.VEO_CHAPTERS else
               mv._calculate_image_count(d, chapter_number=n, total_chapters=7) for n, d in sorted(durs.items())}
        if sum(por.values()) <= IMAGENES_PLAN:
            return spi, {"segundos_por_imagen": spi, "por_cap": por, "total": sum(por.values()), "duraciones": durs}
        spi += 0.25


def guion(log: list[str]) -> None:
    import fase1_5 as f15
    from script_engine import m03_visual as mv
    f15.m07_music_director.generate_music_map = _music_curated
    sm_path = ROOT / "output" / "audio" / TID / "sync_map.json"
    if not (ROOT / "output" / "audio" / TID / "music_map.json").exists():
        _freno_gemini(0.30, "normalizer_gate")
        r = f15.process_topic(TID, from_step="normalizer_gate", gate_interactive=False, music_gate_interactive=False,
                              stop_after_step="m07", v3=True, guion="v4")
        log.append(f"guion (normalizer→audio→m07): {r.get('status')} {r.get('steps_completed')} {r.get('error') or ''}")
        _anotar_costos("audio")
        if r.get("status") != "PASS":
            raise Parada(f"audio/m07: {r.get('error')}")
    sm = _j(sm_path)
    spi, plan = _plan_imagenes(sm)
    mv.SECONDS_PER_IMAGE_TARGET = spi
    _w(LAB / "plan_imagenes.json", plan)
    log.append(f"guion: plan de imágenes {plan['total']} ({plan['por_cap']}) a {spi} s por imagen; duraciones "
               f"{ {k: round(v) for k, v in plan['duraciones'].items()} } = {sum(plan['duraciones'].values()) / 60:.1f} min")
    _freno_gemini(1.50, "m03")
    # 2.º intento (el 1.º, por process_topic, falló con AttributeError sin traceback): m03 directo, como lo llama
    # process_topic, con el traceback guardado; después paso0 + assemble, igual que process_topic
    import traceback
    from script_engine.m06_assembler import assemble_final_script
    topic = f15._load_topic_by_id(TID)
    skeleton, narration = f15._load_skeleton(TID), f15._load_narration(TID)
    try:
        f15.assign_visual_prompts(topic, skeleton, narration, sync_map=sm)
    except Exception as e:  # noqa: BLE001
        (LAB / "m03_traceback.txt").write_text(traceback.format_exc(), encoding="utf-8")
        _anotar_costos("m03_intento2")
        raise Parada(f"m03 (2.º intento): {type(e).__name__}: {e} (traceback en m03_traceback.txt)")
    _anotar_costos("m03_intento2", {"plan_imagenes": plan})
    log.append("guion: m03 (2.º intento) OK")
    db = f15.load_db()
    for t in db.get("topics", []):
        if t.get("id") == TID:
            f15.generate_foto_madre_for_topic(t, TID)
            f15.save_db(db)
            break
    final = assemble_final_script(TID)
    log.append(f"guion: paso0 + assemble → {final}")
    _anotar_costos("paso0_assemble")


def _ram_free_gb() -> float:
    import ctypes

    class _MS(ctypes.Structure):
        _fields_ = [("dwLength", ctypes.c_ulong), ("dwMemoryLoad", ctypes.c_ulong),
                    ("ullTotalPhys", ctypes.c_ulonglong), ("ullAvailPhys", ctypes.c_ulonglong),
                    ("ullTotalPageFile", ctypes.c_ulonglong), ("ullAvailPageFile", ctypes.c_ulonglong),
                    ("ullTotalVirtual", ctypes.c_ulonglong), ("ullAvailVirtual", ctypes.c_ulonglong),
                    ("ullAvailExtendedVirtual", ctypes.c_ulonglong)]
    ms = _MS()
    ms.dwLength = ctypes.sizeof(_MS)
    ctypes.windll.kernel32.GlobalMemoryStatusEx(ctypes.byref(ms))
    return ms.ullAvailPhys / 1e9


def _firefox_open() -> bool:
    out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq firefox.exe"], capture_output=True, text=True).stdout
    return "firefox.exe" in out.lower()


def _run(cmd: list[str], log: list[str], name: str) -> int:
    t0 = time.time()
    with (LAB / f"{name}.out").open("w", encoding="utf-8") as fh:
        r = subprocess.run(cmd, cwd=ROOT, stdout=fh, stderr=subprocess.STDOUT, text=True,
                           env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    log.append(f"{name}: rc={r.returncode} en {(time.time() - t0) / 60:.1f} min ({' '.join(cmd[1:])})")
    return r.returncode


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--etapa", choices=["preparar", "particion", "guion", "imagenes", "render", "render_sin_gfx"],
                    required=True)
    a = ap.parse_args()
    log = [f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] F26 §B Vajont · etapa {a.etapa}"]
    rc = 0
    try:
        if a.etapa == "preparar":
            preparar(log)
        elif a.etapa == "particion":
            particion(log)
        elif a.etapa == "guion":
            guion(log)
        elif a.etapa == "imagenes":
            rc = _run([sys.executable, "fase2a.py", "--topic", TID], log, "fase2a")
        else:
            ram, ff = _ram_free_gb(), _firefox_open()
            log.append(f"render: RAM libre {ram:.1f} GB · Firefox {'ABIERTO' if ff else 'cerrado'}")
            if ff or ram <= 14:
                log.append("render: NO arranca (regla de Omar: Firefox cerrado y RAM > 14 GB)")
                rc = 3
            elif a.etapa == "render":
                rc = _run([sys.executable, "fase2b.py", TID, "--keep-segments", "--gfx", "--gfx-sparse",
                           "--gfx-quality", "looks"], log, "fase2b")
            else:
                rc = _run([sys.executable, "fase2b.py", TID, "--keep-segments"], log, "fase2b_sin_gfx")
    except Parada as e:
        log.append(f"PARADA: {e}")
        rc = 2
    finally:
        with (LAB / "produccion.log").open("a", encoding="utf-8") as fh:
            fh.write("\n".join(log) + "\n")
        print("\n".join(log), flush=True)
    sys.exit(rc)


if __name__ == "__main__":
    main()
