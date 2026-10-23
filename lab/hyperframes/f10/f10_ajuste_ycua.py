"""F10 §4.3 → ajuste: UNA corrida de ajuste del guion de Ycuá Bolaños con las notas del analista (OK de Omar).

1. Guarda la versión 1 (escaleta, narración, juez, entregas) como *_v1.
2. Retoca la escaleta (lo estructural de las notas) y la vuelve a validar:
   - D192 (327 muertos, oficial) sale de pantalla: pasa a ser el dato central del beat 9 (morgue), que ya lleva
     contador → se dice una vez en la voz y el contador sube en pantalla en ese momento; Q53 queda como apoyo;
   - caps cortos con material del pool: Blas Cristaldo hora por hora (T19, T20 en el cap 4; T25, T27 en el cap 5) y
     Tatiana Gabaglio adulta (Q03 en el cap 7);
   - el cierre del último beat: la contradicción pericia–testimonios, una pregunta y la cita de Liz Torres (Q77).
3. Las notas del analista van al guionista como `instrucciones_guionista` (el canal que ya lee m01b).
4. Corre `fase1_5 --v3 --only m01b` (guionista → editor → partición → juez) y chequea el criterio de Omar:
   cierre en la cita, «11:25» en la voz, ≤ 1 fecha literal por cap, duras ≤ 12. Escribe ajuste_chequeos.json.
Uso: python -I lab/hyperframes/f10/f10_ajuste_ycua.py [--solo-chequeo]
"""
from __future__ import annotations

import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
TOPIC = "f8s1-ycua-bolanos"
LAB = Path(__file__).resolve().parent
LIZ = "Soy la vida de muchas personas que cayeron sobre mi cuerpo"
NOTAS = [
    "NOTA DEL ANALISTA 1 — CIERRE (cap 7): la contradicción entre la pericia (solo tres puertas cerradas: azotea, "
    "mirador y administración) y los cientos de testimonios de portones cerrados por los guardias; después UNA "
    "pregunta; y la ÚLTIMA FRASE DEL VIDEO es la cita de Liz Torres «Soy la vida de muchas personas que cayeron sobre "
    "mi cuerpo» (Q77). Sin resumen, sin activismo, sin «su lucha», sin «que la memoria no se apague».",
    "NOTA DEL ANALISTA 2 — FECHAS: la fecha completa «1 de agosto de 2004» se dice UNA sola vez en todo el video (en "
    "el gancho, con el ancla de lugar). Después: «ese domingo», «esa mañana», «esa noche». Como máximo una fecha "
    "literal por cap. Un evento contado con «ese domingo» cuenta como dicho.",
    "NOTA DEL ANALISTA 3 — PICO (cap 5): la hora «11:25» suena en la voz, tal cual, en el momento de la explosión.",
    "NOTA DEL ANALISTA 4 — SIN JUICIOS NI RELLENO: nada de «fue una masacre», «un peligro que nadie veía», «solo "
    "podían esperar un milagro», «un infierno», «el silencio era aterrador». Cada frase cuenta un hecho, una cita o una "
    "pregunta.",
    "NOTA DEL ANALISTA 5 — LARGO: los caps 4, 5 y 7 llegan a su mínimo con material del pool: Blas Cristaldo hora por "
    "hora (T19: Teresa y sus hijas pasan a buscar a Estela a las 10:30; T25 y T27: la búsqueda y las 22:30, cuando "
    "retira el cuerpo de Estela del estacionamiento) y Tatiana Gabaglio como la adulta que hoy recuerda (Q03), nunca "
    "como niña.",
    "NOTA DEL ANALISTA 6 — 327: la cifra oficial (D192, «oficialmente 327 muertos, además de los desaparecidos») se "
    "dice UNA vez en la voz, en el beat 9 (la morgue); en ese momento sube el contador en pantalla.",
]


def wc(s: str) -> int:
    return len(re.findall(r"[\wáéíóúñü]+", s or "", re.I))


def ajustar_escaleta() -> dict:
    from script_engine import m01a_escaleta as me
    from script_engine.m01a_skeleton import STEPS_DIR
    d = STEPS_DIR / TOPIC
    esc = json.loads((d / "01a_escaleta.json").read_text(encoding="utf-8"))
    pool = json.loads((d / "01_facts_sources.json").read_text(encoding="utf-8"))["evidence_pool"]
    for f in ("01a_escaleta.json", "01a_skeleton.json", "01b_narration.json", "01b_narracion_v3.json",
              "01b_editor_v3.json", "01b_guionista_v3.json", "06_judge_narrative.json"):
        if (d / f).exists() and not (d / f.replace(".json", "_v1.json")).exists():
            shutil.copy2(d / f, d / f.replace(".json", "_v1.json"))
    for f in ("NARRACION_ycua.md", "ESCALETA_ycua.md", "06_judge_ycua.json", "costo_guion_ycua.json"):
        if (LAB / f).exists() and not (LAB / f.replace("_ycua", "_ycua_v1")).exists():
            shutil.copy2(LAB / f, LAB / f.replace("_ycua", "_ycua_v1"))
    b = {x["n"]: x for x in esc["beats"]}
    # 6. D192 de pantalla a la voz (beat 9, con contador)
    esc["a_pantalla"] = [x for x in esc.get("a_pantalla") or [] if x["id"] != "D192"]
    for c in esc.get("caps") or []:
        c["pantalla_ids"] = [i for i in c.get("pantalla_ids") or [] if i != "D192"]
    b[9]["dato_central"], b[9]["datos_apoyo"], b[9]["contador"] = "D192", ["Q53", "T25", "T27"], True
    # 5. material para los caps cortos
    b[6]["datos_apoyo"] = list(dict.fromkeys(b[6]["datos_apoyo"] + ["T19", "T20"]))[:3]
    b[12]["datos_apoyo"] = ["D196", "Q03"]
    # 1. cierre
    b[12]["cierre"] = ("Termina en la cita de Liz Torres (Q77) después de la contradicción pericia–testimonios y una "
                       "pregunta.")
    # 2–6. notas al guionista (sin la línea vieja que mandaba D192 a pantalla)
    ins = [x for x in esc.get("instrucciones_guionista") or [] if not x.startswith("D192 va a pantalla")]
    esc["instrucciones_guionista"] = ins + NOTAS
    esc["_ajuste_f10"] = {"notas": NOTAS, "cambios": ["D192: de a_pantalla a dato central del beat 9 con contador",
                                                      "beat 9 apoyo Q53, T25, T27", "beat 6 apoyo + T19, T20",
                                                      "beat 12 apoyo D196, Q03", "beat 12 cierre: cita de Liz"]}
    esc2, hard, rep, warn = me.validate(esc, pool, final=True)
    if hard:
        raise SystemExit(f"la escaleta ajustada no valida: {hard}")
    for k in ("instrucciones_guionista", "_ajuste_f10", "caps", "_pool_plan", "topic_id", "prompt_version",
              "_reparaciones", "_avisos", "_intentos", "_pantalla_por_fecha", "_costo"):
        if k in esc and k not in esc2:
            esc2[k] = esc[k]
    esc2["_reparaciones_ajuste"] = rep
    (d / "01a_escaleta.json").write_text(json.dumps(esc2, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"escaleta ajustada: reparaciones {rep} · avisos {len(warn)}", flush=True)
    return esc2


def chequeo() -> dict:
    from script_engine.guion_v3_reglas import date_problems, sentences_of
    from script_engine.m01a_skeleton import STEPS_DIR
    d = STEPS_DIR / TOPIC
    na = json.loads((d / "01b_narration.json").read_text(encoding="utf-8"))
    ed = json.loads((d / "01b_editor_v3.json").read_text(encoding="utf-8"))
    caps = na["chapters"]
    last = sentences_of(caps[-1]["narration"])[-1] if caps[-1]["narration"] else ""
    full = " ".join(c["narration"] for c in caps)
    hard = (ed.get("revision_despues") or {}).get("hard") or []
    chk = {"cierre_en_cita_de_liz": LIZ.lower() in last.lower(), "ultima_frase": last,
           "hora_11_25_en_voz": bool(re.search(r"\b11[:.]25\b", full)),
           "fechas": date_problems(caps), "fecha_max_1_por_cap": not date_problems(caps),
           "duras": len(hard), "duras_ok": len(hard) <= 12, "lista_duras": hard,
           "palabras": wc(full), "palabras_por_cap": [wc(c["narration"]) for c in caps],
           "dice_327": len(re.findall(r"\b327\b", full)),
           "juicios_viejos": [p for p in ("fue una masacre", "un peligro que nadie veía", "esperar un milagro")
                              if p in full.lower()]}
    chk["seguir_a_produccion"] = (chk["cierre_en_cita_de_liz"] and chk["hora_11_25_en_voz"]
                                  and chk["fecha_max_1_por_cap"] and chk["duras_ok"])
    (LAB / "ajuste_chequeos.json").write_text(json.dumps(chk, ensure_ascii=False, indent=1), encoding="utf-8")
    return chk


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")                # -I ignora PYTHONIOENCODING
    if "--solo-chequeo" not in sys.argv:
        ajustar_escaleta()
        import fase1_5 as f15
        res = f15.process_topic(TOPIC, from_step="m01b", stop_after_step="m01b", gate_interactive=False,
                                music_gate_interactive=False, v3=True)
        if res["status"] != "PASS":
            raise SystemExit(f"m01b falló: {res.get('error')}")
    print(json.dumps(chequeo(), ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
