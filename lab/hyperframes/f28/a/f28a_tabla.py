"""F28 §A: tabla de las 30 pistas (medidas + poda + Gemini) para el reporte → lab/hyperframes/f28/a/TABLA_PALETA.md."""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8")
LAB = Path(__file__).resolve().parent
F28 = LAB.parent
med = json.loads((F28 / "PALETA_medidas.json").read_text(encoding="utf-8"))
INTENTS = ("hook", "setup", "rising_tension", "shock", "consequences", "outro")
filas = ["| id | tonalidad (r) | pulso · lento | LRA | I LUFS | voz 1–4k | fade in/out s | hueco s | poda (reglas del handoff) | "
         "Gemini: nota · melodía · pulso · tráiler · compite | Gemini: mejor intent | lo que oye Gemini (corto) |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|"]
cand = {i: [] for i in INTENTS}
for i in INTENTS:
    for k in range(1, 6):
        tid = f"{i}_{k:02d}"
        m = med["pistas"][tid]
        e = (json.loads((LAB / "escucha" / f"{tid}.json").read_text(encoding="utf-8")).get("json") or {})
        si = lambda b: "sí" if b else "no"  # noqa: E731
        desc = (e.get("descripcion") or "").split(". ")[0][:110]
        filas.append(
            f"| {tid} | {m['tonalidad']} ({m['tonalidad_r']:.2f}) | {m['pulso']:.2f} · {m['pulso_lento']:.2f} | "
            f"{m['LRA_lu']:.1f} | {m['I_lufs']:.1f} | {m['banda_voz']:.3f} | {m['fade_in_s']}/{m['fade_out_s']} | "
            f"{m['huecos_s']} | {'; '.join(m['poda']) or '—'} | {e.get('nota_canal')} · {si(e.get('tiene_melodia'))} · "
            f"{si(e.get('tiene_pulso'))} · {si(e.get('suena_a_trailer'))} · {si(e.get('compite_con_voz'))} | "
            f"{e.get('mejor_intent')} | {desc} |")
        sin_fade = [x for x in m["poda"] if not x.startswith("fade")]
        if not sin_fade and (e.get("nota_canal") or 0) >= 9 and not e.get("tiene_melodia") and not m["huecos_s"]:
            cand[i].append(tid)
(LAB / "TABLA_PALETA.md").write_text("\n".join(filas) + "\n", encoding="utf-8")
json.dump(cand, sys.stdout, ensure_ascii=False)
print()
