"""F56 Parte C — Wittenoom sin volver a escribir el guion: sobre los párrafos del guion F55 ANTES del reparto
(lab/hyperframes/f56/antes/01b_guionista_v4.json → reparacion.parrafos: lo que salió del guionista y la edición por
oración), corre lo mismo que hace fase1_5.run_guion_v4 después del guionista: bloqueantes con los jueces nuevos →
partición (reparto nuevo + títulos) → papel (m01e) → juez m05. El guionista y la escaleta NO se vuelven a llamar;
`fase1_5` no cambia (se reusan sus funciones). Escribe en _steps/<id>/ los mismos archivos que la cadena y actualiza
01b_guionista_v4.json (bloqueantes nuevos y métricas; los párrafos quedan iguales). Costo medido por paso en
01_v3_costos.json (partición: títulos con Flash + editor de largo; pantalla: Sonnet). Salida: SALIDA_C.md."""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

import fase1_5  # noqa: E402
from researcher_steps.ficha_caso import load as load_ficha  # noqa: E402
from script_engine import dicho_verificador as dv  # noqa: E402
from script_engine import evidence as ev  # noqa: E402
from script_engine import guion_v4 as g4  # noqa: E402
from script_engine import m01d_particion as md  # noqa: E402
from script_engine.guion_v3_reglas import sentences_of  # noqa: E402
from script_engine.m05_narrative import judge_narration  # noqa: E402

TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
STEPS = fase1_5.STEPS_DIR / TID
ANTES = ROOT / "lab" / "hyperframes" / "f56" / "antes"


def main() -> None:
    topic = fase1_5._topic_v3(TID)
    pool = topic["evidence_pool"]
    esc = json.loads((STEPS / "01a_escaleta.json").read_text(encoding="utf-8"))
    g_antes = json.loads((ANTES / "01b_guionista_v4.json").read_text(encoding="utf-8"))
    ps = [dict(p) for p in g_antes["reparacion"]["parrafos"]]           # los párrafos ANTES del reparto (F55 Parte D)
    ficha = load_ficha(TID, fase1_5.STEPS_DIR)
    log: list[str] = []
    dv.reset()
    bl_antes = g_antes["reparacion"]["bloqueantes_despues"]
    ps = g4.with_ids(ps, pool, esc)
    bl = g4.bloqueantes(topic, esc, ps, "abierto", ficha)              # jueces nuevos (F56 A) + verificador real si hace falta
    altas = list(g4.ULTIMAS_ALTAS)
    costos_antes = json.loads((STEPS / "01_v3_costos.json").read_text(encoding="utf-8"))["_corridas"]
    part = fase1_5._step_cost(TID, "particion (F56 C)", lambda: md.particionar(topic, esc, ps, pool, log=log, shorten=md.editor_shorten()))
    pantalla = fase1_5.run_pantalla(TID, pool, log)
    judge = judge_narration(TID, pool=pool, narration=part["narration"], skeleton=part["skeleton"])
    # 01b_guionista_v4.json: mismos párrafos, bloqueantes y métricas nuevos
    g_new = dict(g_antes)
    g_new["reparacion"] = {**g_antes["reparacion"], "parrafos": ps, "bloqueantes_despues": bl, "parada": bool(bl),
                           "_f56": {"nota": "F56 C: jueces nuevos sobre los mismos párrafos; sin volver a llamar al guionista",
                                    "bloqueantes_f55": bl_antes}}
    g_new["metricas"] = g4.metricas(topic, esc, ps)
    (STEPS / "01b_guionista_v4.json").write_text(json.dumps(g_new, ensure_ascii=False, indent=2), encoding="utf-8")
    costos = json.loads((STEPS / "01_v3_costos.json").read_text(encoding="utf-8"))["_corridas"][len(costos_antes):]
    gasto = round(sum(c["usd"] for c in costos), 4) + dv.estado()["usd"]
    # salida
    na = part["narration"]["chapters"]
    rl = esc.get("recuerda_loop") or {}
    donde = []
    for c in na:
        for k, s in enumerate(sentences_of(c["narration"])):
            from difflib import SequenceMatcher
            r = SequenceMatcher(None, ev.norm(s), ev.norm(rl.get("oracion") or "")).ratio()
            if r >= 0.6:
                donde.append((c["chapter_number"], k + 1, round(r, 2)))
    sk = part["skeleton"]
    L = ["# F56 — Salida C (texto)", "",
         f"Párrafos: los de `lab/hyperframes/f56/antes/01b_guionista_v4.json` → `reparacion.parrafos` ({len(ps)}; los del guionista f54-2 + "
         "la edición por oración de F55 D, ANTES del reparto). Guionista y escaleta sin volver a llamar.", "",
         "## 1. Bloqueantes antes → después, y quién los vio", "",
         f"**Antes (F55 D, jueces viejos): {len(bl_antes)}**"] + [f"- cap {x['cap']} beat {x['beat']} ({x['codigo']}): {x['motivo'][:150]}" for x in bl_antes] + \
        ["", f"**Después (jueces F56 A): {len(bl)}**"] + ([f"- cap {x['cap']} beat {x['beat']} ({x['codigo']}): {x['motivo'][:150]}" for x in bl] or ["- (ninguno)"]) + \
        ["", f"Quién los vio: (a) `false_quotes` y (d) `contamination` nuevos (código); (f)/(h) `regla_dicho` + verificador: {dv.estado()} · altas de Sonnet: {altas or 'ninguna'}.",
         f"PARADA del guion: {'sí' if bl else 'no'}.", "",
         "## 2. Dónde cae el re-gancho", "",
         f"`recuerda_loop`: beat {rl.get('beat')} · «{rl.get('oracion')}»", "",
         f"Notas del reparto: " + (" · ".join(part["notas"]) or "ninguna"), "",
         f"Oración del re-gancho en la narración (parecido ≥ 0,6): {', '.join(f'cap {c}, oración {k} ({r})' for c, k, r in donde) or 'no encontrada'}", "",
         "## 3. Los 7 caps con su largo (y los 7 títulos)", "", "| cap | título | palabras | caracteres | beats |", "|---|---|---|---|---|"]
    for c, s in zip(na, sk["chapters"]):
        beats = sorted({p["beat"] for p in ps if p["cap"] == c["chapter_number"]})
        L.append(f"| {c['chapter_number']} | {s.get('title')} | {len(c['narration'].split())} | {len(c['narration'])} | {beats} |")
    L += ["", f"Total: {sum(len(c['narration'].split()) for c in na)} palabras.", "",
          "## 4. Gasto", "", f"Pasos nuevos en `01_v3_costos.json`: {costos} · verificador US$ {dv.estado()['usd']} · **total US$ {gasto}**.", "",
          "## 5. El papel (01e_pantalla.md)", "",
          (STEPS / "01e_pantalla.md").read_text(encoding="utf-8") if pantalla is not None else "(m01e no dio papel)", "",
          "## Log", ""] + [f"    {x.strip()}" for x in log]
    (ROOT / "lab/hyperframes/f56/SALIDA_C.md").write_text("\n".join(L), encoding="utf-8", newline="\n")
    print("\n".join(L[:45]))
    print("juez:", str(judge)[:200])


if __name__ == "__main__":
    main()
