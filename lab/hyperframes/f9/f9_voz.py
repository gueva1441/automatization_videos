"""F9 §3.6: prueba de cierre de la voz v4 (sin render de video) — caps 2 y 4 de Orleans F7c-3 con `narration_tts`.

Uso: python -I lab/hyperframes/f9/f9_voz.py [--slowly-dev] [--solo-mezcla]
    --slowly-dev   etiqueta [slowly] al abrir cada párrafo de desarrollo (si v4 habló a más de 2.4 palabras/s)
    --solo-mezcla  rehace las mezclas y VOZ_F9.md desde los audios ya generados (sin TTS)
Genera con audio_manager.process_script (el camino real: v4 + MS Narrador, etiquetas trasladadas al texto normalizado,
forced alignment con el texto limpio) y el mismo par con Bill en v4 (perfil pisado solo en este proceso). Mide
palabras/segundo y pausas (huecos entre palabras del alineado) por cap, mezcla cada par con la música del perfil por
intent (audio_library/<intent>_curated.mp3, volumen del track, ducking del perfil) y escribe
lab/hyperframes/f9/audio/cap2_cap4_v4_msnarrador.mp3, cap2_cap4_v4_bill.mp3 y lab/hyperframes/f9/VOZ_F9.md.
"""
from __future__ import annotations

import json
import statistics
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
LAB = Path(__file__).resolve().parent
OUT = LAB / "audio"
TOPIC = "ba6c3cac-f7r3"
CAPS = (2, 4)
BILL = "pqHfZKP75CvOlQylNhV4"
VIDS = {"msnarrador": f"{TOPIC}-f9voz", "bill": f"{TOPIC}-f9voz-bill"}


def build_chapters(slowly_dev: bool) -> list[dict]:
    from script_engine import m01c_editor as mc
    from script_engine.m01a_skeleton import DEFAULT_INTENT_BY_CAP, STEPS_DIR
    from script_engine.m01b_guionista import caps_text
    narr = json.loads((STEPS_DIR / TOPIC / "01b_narracion_v3.json").read_text(encoding="utf-8"))
    esc = json.loads((STEPS_DIR / TOPIC / "01a_escaleta.json").read_text(encoding="utf-8"))
    caps = mc.narration_tts(esc, narr["parrafos"], caps_text(esc, narr["parrafos"]), slowly_dev=slowly_dev)
    return [{"id": f"ch{c['chapter_number']:02d}", "text": c["narration"], "narration_tts": c["narration_tts"],
             "tts_tags": c["tts_tags"], "narrative_intent": DEFAULT_INTENT_BY_CAP[c["chapter_number"]]}
            for c in caps if c["chapter_number"] in CAPS]


def generate(slowly_dev: bool) -> dict:
    import audio_manager as am
    from cost_tracker import cost_tracker
    from config import OUTPUT_DIR
    chs = build_chapters(slowly_dev)
    res = {}
    for name, vid in VIDS.items():
        style0 = am.AUDIO_STYLE
        if name == "bill":
            am.AUDIO_STYLE = {**style0, "voice_id_v4": BILL}
        cost_tracker.start_video(vid)
        try:
            sm = json.loads(am.process_script({"video_id": vid, "chapters": [dict(c) for c in chs]})
                            .read_text(encoding="utf-8"))
        finally:
            am.AUDIO_STYLE = style0
            rep = cost_tracker.end_video()
        res[name] = {"sync_map": str(OUTPUT_DIR / "audio" / vid / "sync_map.json"),
                     "usd": round(getattr(rep, "total_cost", 0.0) or 0.0, 4),
                     "chars": sum(len(c.get("tts_text") or "") for c in sm["chapters"])}
    res["tags"] = {c["id"]: c["tts_tags"] for c in chs}
    res["slowly_dev"] = slowly_dev
    return res


def measure(vid: str) -> dict:
    from config import OUTPUT_DIR
    d = OUTPUT_DIR / "audio" / vid
    sm = json.loads((d / "sync_map.json").read_text(encoding="utf-8"))
    out = {}
    for ch in sm["chapters"]:
        words = json.loads((d / ch["timestamps_path"]).read_text(encoding="utf-8"))
        gaps = [round(b["start"] - a["end"], 3) for a, b in zip(words, words[1:])]
        long_ = [g for g in gaps if g >= 0.6]
        out[ch["id"]] = {"duracion_s": ch["duration_sec"], "palabras": len(words),
                         "wps": round(len(words) / ch["duration_sec"], 2),
                         "wps_hablado": round(len(words) / max(0.1, sum(w["end"] - w["start"] for w in words)), 2),
                         "pausas_ge_0_6": len(long_), "pausa_max_s": max(gaps) if gaps else 0,
                         "pausa_mediana_larga_s": statistics.median(long_) if long_ else 0,
                         "residuos_de_etiqueta": [w["word"] for w in words if "[" in w["word"] or "]" in w["word"]],
                         "voz": ch.get("voice_id"), "modelo": ch.get("tts_model"), "transfer": ch.get("tts_transfer")}
    return out


def mix(vid: str, dst: Path) -> None:
    """cap 2 + 1.5 s + cap 4, cada uno con la música de su intent (volumen del track, ducking del perfil)."""
    from audio_config import AUDIO_STYLE
    from config import OUTPUT_DIR
    d = OUTPUT_DIR / "audio" / vid
    sm = json.loads((d / "sync_map.json").read_text(encoding="utf-8"))
    mx = AUDIO_STYLE.get("mixing", {})
    parts = []
    for ch in sm["chapters"]:
        intent = ch.get("narrative_intent") or "setup"
        track = ROOT / "audio_library" / f"{intent}_curated.mp3"
        vol = json.loads(track.with_suffix(".json").read_text(encoding="utf-8")).get("music_volume") or mx.get(
            "music_volume", 0.2)
        part = OUT / f"_mix_{vid}_{ch['id']}.wav"
        fc = (f"[1:a]volume={vol},aloop=loop=-1:size=2e9[m];[0:a]asplit=2[v][sc];"
              f"[m][sc]sidechaincompress=threshold={mx.get('duck_threshold', 0.03)}:ratio={mx.get('duck_ratio', 5)}:"
              f"attack={mx.get('duck_attack_ms', 80)}:release={mx.get('duck_release_ms', 200)}[md];"
              f"[v][md]amix=inputs=2:duration=first:normalize=0[out]")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(d / ch["audio_path"]), "-i", str(track),
                        "-filter_complex", fc, "-map", "[out]", "-ar", "44100", "-ac", "2", str(part)], check=True)
        parts.append(part)
    sil = OUT / "_sil.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo", "-t", "1.5",
                    str(sil)], check=True)
    lst = OUT / f"_list_{vid}.txt"
    lst.write_text("\n".join(f"file '{p.as_posix()}'" for p in [parts[0], sil, parts[1]]), encoding="utf-8")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c:a",
                    "libmp3lame", "-b:a", "192k", str(dst)], check=True)
    for p in parts + [sil, lst]:
        p.unlink(missing_ok=True)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")                # -I ignora PYTHONIOENCODING
    a = sys.argv[1:]
    info_f = LAB / "voz_f9.json"
    info = json.loads(info_f.read_text(encoding="utf-8")) if info_f.exists() else {}
    if "--solo-mezcla" not in a:
        g = generate("--slowly-dev" in a)
        info.setdefault("corridas", []).append(g)
    info["medicion"] = {name: measure(vid) for name, vid in VIDS.items()}
    mix(VIDS["msnarrador"], OUT / "cap2_cap4_v4_msnarrador.mp3")
    mix(VIDS["bill"], OUT / "cap2_cap4_v4_bill.mp3")
    info_f.write_text(json.dumps(info, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(info["medicion"], ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
