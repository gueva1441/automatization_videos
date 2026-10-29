# -*- coding: utf-8 -*-
"""F51f etapa 2 — Wittenoom re-armado SIN LLM con la frase del cartel nueva. Casilleros = el `raw_llm_prompt` + `anio`
que dejó m03 en F51d-A en el 03_visual.json de producción → `f50g/rearmar.rearmar_una` (armar → f8_backstop →
_sacar_frases_con_texto), `grupos` = `people_groups` del topic vivo. No usa `f50g/rearmar.py --escribir`: ese pisa
`REARMADO_F50g.md`, se niega si existe `f50g/antes/` y su chequeo «sin grupos = guardado» ya no vale con el cartel nuevo.

Chequeo (PARADA si falla, sin escribir nada): cada foto queda igual, o tiene cartel y el prompt nuevo = el guardado con
la frase vieja del cartel (`f51a/contrato._frase_cartel_f50h`) cambiada por la nueva (`frase_cartel`).

Uso:
  python lab/hyperframes/f51f/rearmar_f51f.py              # en seco: diff y chequeo, escribe REARMADO_F51f.md
  python lab/hyperframes/f51f/rearmar_f51f.py --escribir   # además, si pasa, escribe prompt/sensible/motivos de las
                                                          # fotos que cambian (la copia de antes va en f51f/antes/)
  python lab/hyperframes/f51f/rearmar_f51f.py --desde-antes   # en seco desde f51f/antes/ (rehace el reporte después
                                                             # de escribir; sobre el vivo ya rearmado daría PARADA)
"""
import difflib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "lab" / "hyperframes" / "f50g"))
sys.path.insert(0, str(ROOT / "lab" / "hyperframes" / "f51a"))
F51F = Path(__file__).resolve().parent
ANTES = F51F / "antes" / "03_visual.json"
SALIDA = F51F / "REARMADO_F51f.md"


def diff_palabras(a: str, b: str) -> str:
    return " ".join(d for d in difflib.ndiff(a.split(), b.split()) if d[0] in "+-")


def main() -> int:
    import rearmar as rg
    from contrato import _frase_cartel_f50h
    from script_engine import m03_imagenes_v3 as v3
    from script_engine.topics_db import get_topic_by_id
    desde_antes = "--desde-antes" in sys.argv                    # el reporte, después de escribir: antes/ → código
    if desde_antes and "--escribir" in sys.argv:
        print("--desde-antes es solo en seco")
        return 1
    raw = (ANTES if desde_antes else rg.VISUAL).read_bytes()
    v = json.loads(raw.decode("utf-8"))
    topic = get_topic_by_id(rg.TID)
    beats = v3.load_beats(topic, rg.STEPS)
    grupos = {g["id"]: g for g in topic.get("people_groups") or [] if isinstance(g, dict) and g.get("id")}

    filas, malas = [], []
    for cap in v["chapters"]:
        n = cap["chapter_number"]
        by_n = {b["n"]: b for b in beats.get(n) or []}
        for i, (it, rol) in enumerate(rg.fotos(cap), start=1):
            k = f"{n}/{i}"
            antes = it.get("prompt") or ""
            if not it.get("raw_llm_prompt"):
                malas.append((k, "sin raw_llm_prompt"))
                continue
            esc = bool((by_n.get(it.get("beat")) or {}).get("escala"))
            despues, _ = rg.rearmar_una(it, esc, grupos)
            tii = json.loads(it["raw_llm_prompt"]).get("text_in_image") or {}
            cartel = bool(tii.get("present"))
            vieja = nueva = None
            if cartel:
                vieja, nueva = _frase_cartel_f50h(tii), v3.frase_cartel(tii)
                ok = antes.count(vieja) == 1 and despues == antes.replace(vieja, nueva)
            else:
                ok = despues == antes
            if not ok:
                malas.append((k, diff_palabras(antes, despues)))
            filas.append({"k": k, "rol": rol, "it": it, "cap": cap, "antes": antes, "despues": despues,
                          "cartel": cartel, "vieja": vieja, "nueva": nueva})

    cambian = [f for f in filas if f["despues"] != f["antes"]]
    con_cartel = [f for f in filas if f["cartel"]]
    L = ["# REARMADO_F51f — Wittenoom re-armado sin LLM con la frase del cartel nueva", "",
         "Salida de `python lab/hyperframes/f51f/rearmar_f51f.py`: casilleros (`raw_llm_prompt`) + `anio` del "
         "03_visual.json de F51d-A → `f50g/rearmar.rearmar_una` con el código de F51f, `grupos` = `people_groups` del "
         "topic vivo. Cero llamadas a modelos, cero fal.", "",
         f"- Fotos: {len(filas)} · con cartel: {len(con_cartel)} · cambian: {len(cambian)}",
         f"- Cambian solo fotos con cartel y solo en la oración del cartel: "
         f"**{'sí' if not malas and all(f['cartel'] for f in cambian) else 'NO — PARADA'}**", ""]
    if malas:
        L += ["## PARADA: diferencias fuera de la oración del cartel", ""] + [f"- {k}: {d}" for k, d in malas] + [""]
    L += ["## Las fotos con cartel", "", "| foto | rol | antes | después |", "|---|---|---|---|"]
    L += [f"| {f['k']} | {f['rol']} | {f['vieja']} | {f['nueva']} |" for f in con_cartel]
    L += ["", "## Los prompts enteros (después)", ""]
    for f in con_cartel:
        L += [f"### {f['k']} ({f['rol']})", "", "```", f["despues"], "```", ""]
    SALIDA.write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"fotos {len(filas)} · con cartel {len(con_cartel)} · cambian {len(cambian)} "
          f"({', '.join(f['k'] for f in cambian)}) · fuera del cartel {len(malas)} {malas[:3]}")
    if malas or not all(f["cartel"] for f in cambian):
        print("PARADA: no se escribe")
        return 1

    if "--escribir" in sys.argv:
        if not ANTES.exists() or ANTES.read_bytes() != raw:
            print(f"falta {ANTES.relative_to(ROOT)} igual al vivo: no se escribe")
            return 1
        nl = "\r\n" if b"\r\n" in raw else "\n"                  # m03 lo escribe con write_text (CRLF en Windows)
        fin = nl if raw.endswith(b"\n") else ""

        def volcar(x) -> bytes:
            return (json.dumps(x, ensure_ascii=False, indent=2).replace("\n", nl) + fin).encode("utf-8")

        if volcar(v) != raw:
            print("el formato del 03_visual.json no es el de json.dumps(indent=2): no se escribe")
            return 1
        for f in cambian:
            p, it, sens, mot = f["despues"], f["it"], v3.is_body(f["despues"]), sorted(v3.motifs_of(f["despues"]))
            if f["rol"] == "veo0":
                f["cap"]["image_prompt"], f["cap"]["image_sensible"] = p, sens
                f["cap"]["image_f8"]["motivos"] = mot
            else:
                it["prompt"], it["sensible"], it["motivos"] = p, sens, mot
        rg.VISUAL.write_bytes(volcar(v))
        print(f"escrito {rg.VISUAL.relative_to(ROOT)} ({len(cambian)} fotos)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
