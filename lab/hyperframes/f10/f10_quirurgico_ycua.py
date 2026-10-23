"""F10: arreglos quirúrgicos del guion de Ycuá sobre la VERSIÓN 1 (Omar descartó la corrida de ajuste).

1. Guarda la del ajuste como *_ajuste y parte de *_v1 (7 caps completos).
2. Escaleta v1 + D192 (327 oficiales) de pantalla a la voz: dato central del beat 9 con contador; fuera de reservados.
3. regenerate_cap_v3 del cap 7 (cierre: contradicción pericia–testimonios, pregunta, última frase la cita de Liz Torres;
   largo ≥ mínimo) y del cap 5 («a las 11:25» en el pico; 327 una vez), solo con los datos permitidos.
4. El editor saca los juicios de la lista donde aparezcan; pasada determinista de fechas (la primera «1 de agosto de
   2004» queda; las siguientes → «ese domingo»).
5. Partición (títulos de la v1), revisión, juez y criterio de Omar: 7 caps con narración, cierre en la cita, 11:25,
   fecha ≤ 1 por cap, ningún cap bajo el mínimo, duras ≤ 15 → quirurgico_chequeos.json.
Uso: python -I lab/hyperframes/f10/f10_quirurgico_ycua.py
"""
from __future__ import annotations

import json
import re
import shutil
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
TOPIC = "f8s1-ycua-bolanos"
LAB = Path(__file__).resolve().parent
LIZ = "Soy la vida de muchas personas que cayeron sobre mi cuerpo"
JUICIOS = ["solo podían esperar un milagro", "esperar un milagro", "fue una masacre", "un peligro que nadie veía"]
NOTAS_7 = [
    "El cap 7 cierra el video. Orden: (a) la contradicción: la pericia dijo que solo tres puertas estaban cerradas (la "
    "azotea, el mirador y la administración); cientos de testimonios dicen que los guardias cerraron los portones; "
    "(b) UNA pregunta que queda abierta; (c) la ÚLTIMA FRASE DEL VIDEO es la cita de Liz Torres: «Soy la vida de muchas "
    "personas que cayeron sobre mi cuerpo» (con su nombre dentro de la oración, antes de la cita). Nada después de la "
    "cita.",
    "Sin resumen, sin activismo: nada de «su lucha», «que la memoria no se apague», «la voz de los que ya no pueden "
    "hablar», «un antes y un después».",
    "Usá los heridos y los huérfanos (244 y 204) una sola vez, como hecho, antes de la contradicción.",
    "La fecha del día no se repite: si hace falta, «ese domingo».",
]
NOTAS_5 = [
    "En el pico (el primer párrafo, beat 8) la explosión ocurre «a las 11:25»: decí esa hora tal cual, en voz.",
    "La cifra oficial de muertos, 327, se dice UNA sola vez, en la morgue (beat 9); en ese momento sube el contador en "
    "pantalla. No repitas la cifra.",
    "Fuera los juicios del narrador: «fue una masacre», «un infierno del que nadie podía escapar», «el silencio era "
    "aterrador». Contá el hecho o la cita.",
    "La fecha del día no se repite: si hace falta, «ese domingo».",
]


def wc(s: str) -> int:
    return len(re.findall(r"[\wáéíóúñü]+", s or "", re.I))


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")                # -I ignora PYTHONIOENCODING
    import fase1_5 as f15
    from cost_tracker import cost_tracker
    from script_engine import m01a_escaleta as me
    from script_engine import m01b_guionista as mg
    from script_engine import m01d_particion as md
    from script_engine.guion_v3_reglas import date_problems, replace_repeated_dates, sentences_of
    from script_engine.m01a_skeleton import STEPS_DIR
    from script_engine.m05_narrative import judge_narration
    d = STEPS_DIR / TOPIC
    ld = lambda f: json.loads((d / f).read_text(encoding="utf-8"))  # noqa: E731
    for f in ("01a_escaleta.json", "01a_skeleton.json", "01b_narration.json", "01b_narracion_v3.json",
              "01b_editor_v3.json", "01b_guionista_v3.json", "06_judge_narrative.json"):
        if (d / f).exists() and not (d / f.replace(".json", "_ajuste.json")).exists():
            shutil.copy2(d / f, d / f.replace(".json", "_ajuste.json"))
    topic = f15._topic_v3(TOPIC)
    pool = topic["evidence_pool"]
    log: list[str] = []
    t0 = time.time()
    cost_tracker.start_video(f"{TOPIC}-quirurgico")
    # 2. escaleta v1 + D192 a la voz
    esc = ld("01a_escaleta_v1.json")
    esc["a_pantalla"] = [x for x in esc.get("a_pantalla") or [] if x["id"] != "D192"]
    for c in esc.get("caps") or []:
        c["pantalla_ids"] = [i for i in c.get("pantalla_ids") or [] if i != "D192"]
    b9 = next(b for b in esc["beats"] if b["n"] == 9)
    b9["dato_central"], b9["datos_apoyo"], b9["contador"] = "D192", ["Q53"], True
    esc["instrucciones_guionista"] = [x for x in esc.get("instrucciones_guionista") or []
                                      if not x.startswith("D192 va a pantalla")]
    esc["_quirurgico_f10"] = ["D192: de a_pantalla a dato central del beat 9 con contador (Q53 de apoyo)"]
    _, hard_esc, _, _ = me.validate(esc, pool, final=True)
    if hard_esc:
        raise SystemExit(f"la escaleta v1 + D192 no valida: {hard_esc}")
    (d / "01a_escaleta.json").write_text(json.dumps(esc, ensure_ascii=False, indent=2), encoding="utf-8")
    # 3. caps 7 y 5
    ps = ld("01b_narracion_v3_v1.json")["parrafos"]
    mins = {c["chapter_number"]: round(mg.MIN_WORDS_FACTOR * (c.get("palabras_objetivo") or 0)) for c in esc["caps"]}
    ps = md.regenerate_cap_v3(topic, esc, ps, 7, pool, notas=NOTAS_7,
                              permitidos=["Q77", "D25", "D29", "D89", "D109", "D195", "D196"],
                              min_words=mins[7] + 8, log=log)
    ps = md.regenerate_cap_v3(topic, esc, ps, 5, pool, notas=NOTAS_5, permitidos=["T21", "D192", "Q53"],
                              min_words=mins[5] + 8, log=log)
    # 4. juicios y fechas
    ps = md.cut_phrases(ps, JUICIOS, log=log)
    ps, date_changes = replace_repeated_dates(ps, "1 de agosto", "2004")
    log += [f"  [fechas] {x}" for x in date_changes]
    # 5. partición (títulos de la v1), revisión, juez
    sk1 = ld("01a_skeleton_v1.json")
    tl = [c["title"] for c in sorted(sk1["chapters"], key=lambda c: c["chapter_number"])]
    part = md.particionar(topic, esc, ps, pool, call_titles=lambda p, **k: {"titulos": tl}, log=log)
    rv = mg.review(topic, esc, ps)
    judge = judge_narration(TOPIC, pool=pool, narration=part["narration"], skeleton=part["skeleton"])
    rep = cost_tracker.end_video()
    costo = {"usd": round(getattr(rep, "total_cost", 0.0) or 0.0, 4), "segundos": round(time.time() - t0, 1)}
    costs = ld("01_v3_costos.json")
    costs.setdefault("_corridas", []).append({"paso": "quirurgico", **costo})
    (d / "01_v3_costos.json").write_text(json.dumps(costs, ensure_ascii=False, indent=1), encoding="utf-8")
    (d / "01b_editor_v3.json").write_text(json.dumps({
        "parrafos": ps, "revision_despues": rv, "aceptados": None, "cambios": [], "quirurgico": log,
        "prompt_version": "f10-quirurgico"}, ensure_ascii=False, indent=2), encoding="utf-8")
    # criterio de Omar
    caps = part["narration"]["chapters"]
    last = sentences_of(caps[-1]["narration"])[-1] if caps[-1]["narration"] else ""
    full = " ".join(c["narration"] for c in caps)
    short = [n for n, c in ((c["chapter_number"], c) for c in caps) if wc(c["narration"]) < mins[n]]
    chk = {"siete_caps_con_narracion": all(c["narration"].strip() for c in caps),
           "cierre_en_cita_de_liz": LIZ.lower() in last.lower(), "ultima_frase": last,
           "hora_11_25_en_voz": bool(re.search(r"\b11[:.]25\b", full)),
           "fechas": date_problems(caps), "fecha_max_1_por_cap": not date_problems(caps),
           "minimos": mins, "palabras_por_cap": [wc(c["narration"]) for c in caps], "caps_bajo_minimo": short,
           "duras": len(rv["hard"]), "lista_duras": rv["hard"], "palabras": wc(full),
           "dice_327": len(re.findall(r"\b327\b", full)),
           "juicios_que_quedan": [j for j in JUICIOS if j in full.lower()], "log": log, "costo": costo,
           "juez_video": judge.get("video")}
    chk["seguir_a_produccion"] = (chk["siete_caps_con_narracion"] and chk["cierre_en_cita_de_liz"]
                                  and chk["hora_11_25_en_voz"] and chk["fecha_max_1_por_cap"] and not short
                                  and chk["duras"] <= 15)
    (LAB / "quirurgico_chequeos.json").write_text(json.dumps(chk, ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps({k: v for k, v in chk.items() if k not in ("log", "juez_video")}, ensure_ascii=False, indent=1))
    print("\n".join(log))


if __name__ == "__main__":
    main()
