"""F54 Parte A — salida en texto, sin LLM y sin red: (1) diff de los dos prompts (viejo → nuevo, solo las líneas que
cambian); (2) `has_figure` antes (NUM_WORDS de HEAD~ antes de F54) y ahora sobre las frases citadas en la ENTRADA 29h;
(3) `bloqueantes` + `metricas` de guion_v4 sobre el guion ACTUAL de Wittenoom (`01b_narration.json`, los párrafos
partidos por línea en blanco y con el beat del párrafo de `01b_guionista_v4.json` en la misma posición del cap).
Escribe lab/hyperframes/f54/SALIDA_A.md."""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import fase1_5  # noqa: E402
from script_engine import evidence as ev  # noqa: E402
from script_engine import guion_v4 as g4  # noqa: E402
from script_engine import m01a_escaleta as me  # noqa: E402

TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
STEPS = ROOT / "data" / "scripts" / "_steps" / TID
BASE = "1c9cd7d"     # etapa 0: el código de antes de la Parte A


def _dif(a: str, b: str) -> list[tuple[str, str]]:
    x, y = a.split("\n"), b.split("\n")
    assert len(x) == len(y)
    return [(p, q) for p, q in zip(x, y) if p != q]


def _num_words_viejo() -> re.Pattern:
    src = subprocess.run(["git", "show", f"{BASE}:script_engine/m01a_escaleta.py"], cwd=ROOT, capture_output=True,
                         check=True).stdout.decode("utf-8").replace("\r\n", "\n")
    m = re.search(r"NUM_WORDS = re\.compile\((.*?)\)\n", src, re.S)
    return re.compile(eval("(" + m.group(1) + ")"))      # noqa: S307 — el literal del archivo de antes


FRASES = [   # ENTRADA_ANALISTA_2026-10-29h §3, en el orden en que aparecen
    ("voz de hoy", "Un hombre joven posa para una foto con el pie envuelto en una venda blanca."),
    ("voz de hoy", "Detrás, tierra roja y paredes de chapa."),
    ("voz de hoy", "En el retrato de familia todos miran a cámara menos el pie."),
    ("voz de hoy", "El hombre se llama Daniel Écija."),
    ("voz de hoy", "Para entender ese pie hay que volver a un baile en Madrid."),
    ("cierre_humano", "La herida del pie cerró. La otra nadie supo verla a tiempo."),
    ("DEBERÍA", "Un hombre joven posa con el pie envuelto en una venda blanca."),
    ("DEBERÍA", "Le cayó un trozo de amianto y la herida no cierra."),
    ("DEBERÍA", "Wittenoom, Australia, mil novecientos sesenta y dos."),
    ("DEBERÍA", "Esa herida va a cerrar."),
    ("DEBERÍA", "Lo que respiró ese año, no: veintinueve años después, al otro lado del mundo, el polvo lo va a "
                "alcanzar."),
]


def parrafos_de_la_narracion() -> list[dict]:
    nar = json.loads((STEPS / "01b_narration.json").read_text(encoding="utf-8"))
    gv4 = json.loads((STEPS / "01b_guionista_v4.json").read_text(encoding="utf-8"))["reparacion"]["parrafos"]
    out = []
    for c in nar["chapters"]:
        n = c["chapter_number"]
        textos = [t.strip() for t in c["narration"].split("\n\n") if t.strip()]
        beats = [p["beat"] for p in gv4 if p["cap"] == n]
        assert len(textos) == len(beats), (n, len(textos), len(beats))
        out += [{"beat": b, "cap": n, "texto": t} for b, t in zip(beats, textos)]
    return out


def main() -> None:
    L: list[str] = ["# F54 — Salida A (sin LLM, US$ 0)", ""]
    # (1) prompts
    L += ["## 1. Diff de los dos prompts (viejo → nuevo, solo las líneas que cambian)", ""]
    for nombre, viejo, nuevo in (("Escaleta f26-1 → f54-1 (`<oficio>` §2)", me.SYSTEM_V2_F26_1, me.SYSTEM_V2),
                                 ("Guion v5.4 (f25-1) → v5.5 (f54-1) (`<estructura>` 1)", g4.SYSTEM_V5_4, g4.SYSTEM_V5_5)):
        L += [f"### {nombre}", "", "```diff"]
        for a, b in _dif(viejo, nuevo):
            L += [f"- {a}", f"+ {b}"]
        L += ["```", ""]
    # (2) has_figure
    viejo = _num_words_viejo()
    L += ["## 2. `has_figure` sobre las frases de la ENTRADA 29h (§3)", "",
          "| # | de dónde | frase | antes | ahora | qué lo detecta ahora |", "|---|---|---|---|---|---|"]
    for k, (src, f) in enumerate(FRASES, 1):
        antes = bool(re.search(r"\d", f) or viejo.search(ev.norm(f)))
        ahora = me.has_figure(f)
        hits = me.NUM_WORDS.findall(ev.norm(f)) or re.findall(r"\d+", f)
        L.append(f"| {k} | {src} | {f} | {'sí' if antes else 'no'} | {'sí' if ahora else 'no'} | "
                 f"{', '.join(hits) or '—'} |")
    L.append("")
    # (3) Wittenoom
    topic = dict(fase1_5._load_topic_by_id(TID))
    fase1_5.cargar_perfil(TID)
    esc = json.loads((STEPS / "01a_escaleta.json").read_text(encoding="utf-8"))
    ficha = json.loads((STEPS / "ficha_caso.json").read_text(encoding="utf-8"))
    ps = parrafos_de_la_narracion()
    bl = g4.bloqueantes(topic, esc, ps, "abierto", ficha)
    m = g4.metricas(topic, esc, ps)
    L += ["## 3. `bloqueantes` + `metricas` sobre el guion actual de Wittenoom", "",
          f"Fuente: `data/scripts/_steps/{TID}/01b_narration.json` ({len(ps)} párrafos; beat de cada párrafo tomado de "
          "`01b_guionista_v4.json` → `reparacion.parrafos`, misma posición dentro del cap). Escaleta `01a_escaleta.json`, "
          "ficha `ficha_caso.json`, perfil `_perfil.json`.", "",
          f"### Bloqueantes: {len(bl)}", ""]
    if bl:
        L += ["| código | cap | beat | motivo | frase |", "|---|---|---|---|---|"]
        for x in bl:
            L.append(f"| {x['codigo']} | {x['cap']} | {x['beat']} | {x['motivo']} | {(x['frase'] or '—')[:120]} |")
    else:
        L.append("(ninguno)")
    L += ["", "### Métricas nuevas por cap (solo tabla, sin freno)", "",
          "| cap | palabras | años dichos | datos usados | datos/min |", "|---|---|---|---|---|"]
    caps = {c["chapter_number"]: c for c in __import__("script_engine.m01b_guionista", fromlist=["x"]).caps_text(
        esc, g4.with_ids(ps, topic["evidence_pool"], esc))}
    for n in range(1, 8):
        L.append(f"| {n} | {m['palabras_por_cap'][n][0]} | {m['anios_por_cap'][n]} | "
                 f"{len(caps[n]['datos_usados'])} | {m['datos_por_min'][n]} |")
    L += ["", f"Total: {m['palabras']} palabras · {m['largo']}.", ""]
    out = ROOT / "lab" / "hyperframes" / "f54" / "SALIDA_A.md"
    out.write_text("\n".join(L), encoding="utf-8", newline="\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
