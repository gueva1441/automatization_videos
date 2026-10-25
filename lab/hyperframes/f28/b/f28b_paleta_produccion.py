"""F28 §B.1 — las 12 pistas elegidas por el analista (`ELECCION_F28_12_pistas.md`) a producción (0 API).

Por pista:
  1. Recorte del fade medido en la parte A (`fade_in_s`/`fade_out_s` de PALETA_medidas.json) + 0.5 s de margen de cada
     lado → `audio_library/<intent>_f28_<a|b>.mp3` (libmp3lame 192k). Tiene que quedar entre 150 y 175 s.
  2. Loop: `loop_crossfade_s: 3` en el json (fase2b empalma el loop con acrossfade de 3 s).
  3. Nivel: el mismo objetivo que las curated. Nivel efectivo de una curated = su LUFS integrado + 20·log10(su
     music_volume) (lo que entra a la mezcla antes del ducking). Para cada pista nueva: music_volume =
     10^((efectivo de la curated de su intent − LUFS de la pista nueva)/20); el floor guarda la proporción
     floor/volume de esa curated. La verificación es la mezcla de Vajont (§B.3: con música ≤ 0.5 LU sobre la voz).
  4. json con origen, plan, medidas, nota y descripción de Gemini (también en `elevenlabs_metadata.description`, que es
     lo que lee el matcher), `paleta: "f28"`, `fits_intents` (consequences también cubre resolution).
Las `*_curated` se MUEVEN a `audio_library/_retiradas/` (no se borran).
Uso: PYTHONIOENCODING=utf-8 python -I lab/hyperframes/f28/b/f28b_paleta_produccion.py
"""
from __future__ import annotations

import json
import math
import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
LAB = Path(__file__).resolve().parent
F28 = LAB.parent
LIB = ROOT / "audio_library"
PAL = LIB / "_paleta_f28"
RET = LIB / "_retiradas"
MARGEN_S = 0.5
LOOP_XF_S = 3.0

# ELECCION_F28_12_pistas.md: (intent de producción, letra) → id de la paleta
ELECCION = {("hook", "a"): "hook_03", ("hook", "b"): "hook_05",
            ("setup", "a"): "setup_03", ("setup", "b"): "outro_03",
            ("rising_tension", "a"): "rising_tension_04", ("rising_tension", "b"): "rising_tension_05",
            ("shock", "a"): "shock_03", ("shock", "b"): "shock_04",
            ("consequences", "a"): "consequences_03", ("consequences", "b"): "consequences_04",
            ("outro", "a"): "outro_01", ("outro", "b"): "outro_02"}
FITS = {"consequences": ["consequences", "resolution"]}


def _j(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def lufs(p: Path) -> float:
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", str(p), "-af", "ebur128", "-f", "null", "-"],
                         capture_output=True, text=True, encoding="utf-8", errors="replace").stderr
    return float(re.findall(r"I:\s+(-?[\d.]+) LUFS", err[err.rfind("Summary:"):])[0])


def duracion(p: Path) -> float:
    return float(subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(p)], capture_output=True, text=True).stdout.strip())


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    med = _j(F28 / "PALETA_medidas.json")["pistas"]
    # nivel efectivo de las curated, por intent (antes de moverlas)
    ref: dict[str, dict] = {}
    for intent in ("hook", "setup", "rising_tension", "shock", "consequences", "outro"):
        cj = (LIB / f"{intent}_curated.json") if (LIB / f"{intent}_curated.json").exists() else RET / f"{intent}_curated.json"
        cm = cj.with_suffix(".mp3")
        c = _j(cj)
        i = lufs(cm)
        ref[intent] = {"track": cj.stem, "I": i, "vol": c["music_volume"], "floor": c["music_volume_floor"],
                       "efectivo": round(i + 20 * math.log10(c["music_volume"]), 2),
                       "efectivo_floor": round(i + 20 * math.log10(c["music_volume_floor"]), 2)}
    out = {"referencia_curated": ref, "pistas": {}}
    for (intent, letra), pid in ELECCION.items():
        m = med[pid]
        src = PAL / f"{pid}.mp3"
        tid = f"{intent}_f28_{letra}"
        dst = LIB / f"{tid}.mp3"
        dur0 = duracion(src)
        a = (m["fade_in_s"] or 0) + MARGEN_S
        b = (m["fade_out_s"] or 0) + MARGEN_S
        largo = dur0 - a - b
        subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", f"{a:.2f}", "-t", f"{largo:.2f}", "-i", str(src),
                        "-c:a", "libmp3lame", "-b:a", "192k", str(dst)], check=True)
        d = duracion(dst)
        i = lufs(dst)
        r = ref[intent]
        vol = round(10 ** ((r["efectivo"] - i) / 20), 3)
        flr = round(vol * r["floor"] / r["vol"], 3)
        pj = _j(PAL / f"{pid}.json")
        esc = (_j(F28 / "a" / "escucha" / f"{pid}.json").get("json") or {})
        meta = {"track_id": tid, "mp3_filename": dst.name, "intent_origin": intent,
                "fits_intents": FITS.get(intent, [intent]), "compatible_profiles": ["MISTERIO_ABISAL"],
                "paleta": "f28", "origen": f"_paleta_f28/{pid}", "loop_crossfade_s": LOOP_XF_S,
                "music_volume": vol, "music_volume_floor": flr,
                "calibracion": {"metodo": "F28: nivel efectivo igual al de la curated del intent "
                                          "(LUFS + 20·log10 volumen)", "curated": r["track"], "I_pista": i,
                                "objetivo_efectivo": r["efectivo"]},
                "recorte": {"inicio_s": round(a, 2), "fin_s": round(b, 2), "duracion_original_s": round(dur0, 2),
                            "duracion_s": round(d, 2)},
                "plan": pj.get("plan"), "song_metadata": pj.get("song_metadata"),
                "medidas": {k: v for k, v in m.items() if not k.startswith("_") and k != "parecido"},
                "nota_gemini": esc.get("nota_canal"), "escucha_gemini": esc,
                "elevenlabs_metadata": {"description": esc.get("descripcion", ""), "genres": [],
                                        "title": tid},
                "topic_source": "F28 paleta del canal", "times_used": 0, "last_used_at": None}
        (LIB / f"{tid}.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        ok = 150 <= d <= 175
        out["pistas"][tid] = {"origen": pid, "recorte_in": round(a, 2), "recorte_out": round(b, 2),
                              "duracion_s": round(d, 2), "en_rango_150_175": ok, "I_lufs": i,
                              "music_volume": vol, "music_volume_floor": flr}
        print(f"[{tid}] ← {pid}: −{a:.1f} s / −{b:.1f} s → {d:.1f} s{'' if ok else ' ⚠ FUERA DE 150–175'} · "
              f"I {i} LUFS → vol {vol} / floor {flr}")
    RET.mkdir(exist_ok=True)
    movidas = []
    for f in sorted(LIB.glob("*_curated.*")):
        shutil.move(str(f), str(RET / f.name))
        movidas.append(f.name)
    out["curated_movidas_a_retiradas"] = movidas
    (LAB / "paleta_produccion.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"curated movidas a {RET}: {movidas}")


if __name__ == "__main__":
    main()
