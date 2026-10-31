# -*- coding: utf-8 -*-
"""
lab/hyperframes/f65/fase2_juicio.py — F65a Etapa B, salida en texto (solo lectura, CERO llamadas al modelo): las 13 fichas
del papel actual de Wittenoom (`01e_pantalla.json` → beats[].ficha) por el camino de Fase 2 —`pantalla_filtros.validar_papel`
(anclaje, candado, no_dicho, spoiler, lectura) y las `contradicciones` del chequeo 5 de gfx_guion con la voz del cap— CON y
SIN `juicio_verificador`. No hay voz generada para este guion (PARADA), así que las palabras con tiempos se sintetizan de la
narración de Fase 1 (segundos por palabra de la entrada, sin escenas): `lectura` corre con esos tiempos, lo que mide esta
tabla es el efecto del juicio, no la colocación real. Escribe lab/hyperframes/f65/FASE2_JUICIO.md.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

from script_engine import m01e_pantalla as m  # noqa: E402
from script_engine import pantalla_entrada as pe  # noqa: E402
from script_engine.clima import vocabulario_clima  # noqa: E402
from script_engine.pantalla_filtros import contradicciones, validar_papel  # noqa: E402
from script_engine.voz_utils import oraciones, palabras  # noqa: E402

TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
STEPS = ROOT / "data" / "scripts" / "_steps"
AQUI = Path(__file__).resolve().parent


def palabras_con_tiempos(oraciones_txt: list[str], seg: float) -> list[dict]:
    """Palabras sintéticas: cada palabra dura `seg` (la velocidad del narrador de la entrada), 0,02 s de aire."""
    words, t = [], 0.0
    for o in oraciones_txt:
        for w in palabras(o):
            words.append({"word": w, "start": round(t, 3), "end": round(t + seg - 0.02, 3)})
            t += seg
        t += 0.3
    return words


def main() -> None:
    carga = m.cargar(TID, STEPS)
    ent = m.entrada(carga, vocabulario_clima())
    papel = json.loads((STEPS / TID / "01e_pantalla.json").read_text(encoding="utf-8"))
    assert papel["prompt_version"] == m.PROMPT_VERSION
    seg = float(ent["seg_por_palabra"]["valor"])
    voz_video = [s["texto"] for c in ent["caps"] for s in c["oraciones"]]
    filas = []
    for c in ent["caps"]:
        n = c["n"]
        textos = [s["texto"] for s in c["oraciones"]]
        words = palabras_con_tiempos(textos, seg)
        sents = oraciones(words, 0.0)
        assert [s["texto"] for s in sents] == textos, f"{c['cap']}: el corte de la voz sintética no es el de la entrada"
        # beats del cap con t0/t1 por las oraciones que los componen
        bs = []
        for b in [b for b in ent["beats"] if b["cap"] == c["cap"]]:
            ss = [s for s in sents if c["oraciones"][s["idx"]]["beat"] == b["n"]]
            bs.append({"n": b["n"], "funcion": b["funcion"], "t0": ss[0]["t0"] if ss else 0.0, "t1": ss[-1]["t1"] if ss else 0.0,
                       "cierre": b["cierre"], "dato_central": b["dato_central"], "datos_apoyo": b["apoyo"]})
        antes = " ".join(s["texto"] for cc in ent["caps"] if cc["n"] < n for s in cc["oraciones"])
        for pb in [b for b in papel["beats"] if b["cap"] == c["cap"] and b["ficha"]]:
            f = pb["ficha"]
            gancho = pb["funcion"] == "gancho"
            it = pe._item(f["pool_id"], carga["pool"], carga["escaleta"], pb["beat"], gancho)
            if f.get("autor"):
                it["autor"] = str(f["autor"])
            ent2 = {"oraciones": sents, "beats": bs, "items": [it], "voz_video": voz_video, "voz_antes": antes}
            s = sents[f["sentence_idx"]]
            wi, como = pe.palabra_idx(f.get("palabra") or "", s)
            base = {"pool_id": f["pool_id"], "sentence_idx": f["sentence_idx"], "word_idx": wi, "beat": pb["beat"], "rank": 1,
                    "tipo": m.TIPO_DE_ESTILO.get(f.get("estilo") or "normal", "hecho"), "estilo": f.get("estilo"),
                    "etiqueta": f.get("etiqueta"), "texto": f.get("texto"), "aporta": f.get("aporta"), "papel": True,
                    "palabra_papel": f.get("palabra"), "ancla_palabra": como}
            jv = f.get("juicio_verificador") or {}
            tokens = jv.get("tokens") or {}
            con_j = validar_papel([{**base, **({"juicio_verificador": jv} if jv else {})}], ent2, words, 0.0)
            sin_j = validar_papel([base], ent2, words, 0.0)
            vec = [x["texto"] for x in sents[max(0, f["sentence_idx"] - 1):f["sentence_idx"] + 2]]
            bloque = f"{f.get('etiqueta') or ''} {f.get('texto') or ''}"
            c5_sin = contradicciones(bloque, voz_video, cerca=vec)
            c5_con = contradicciones(bloque, voz_video, cerca=vec, juicio=tokens or None)

            def res(v: dict) -> str:
                if v["bloques"]:
                    return "pasa"
                r = v["rechazos"][0]
                return f"**{r['regla']}**: {str(r['motivo'])[:90].replace('|', '/')}"
            filas.append({"cap": c["cap"], "beat": pb["beat"], "id": f["pool_id"], "estilo": f["estilo"],
                          "juicio": f"{jv.get('regla')} {tokens}" if jv else "—", "sin": res(sin_j), "con": res(con_j),
                          "c5_sin": "; ".join(c5_sin) or "—", "c5_con": "; ".join(c5_con) or "—",
                          "cambia": (res(sin_j) != res(con_j)) or (c5_sin != c5_con)})
    L = ["# F65a Etapa B — FASE2_JUICIO: las 13 fichas del papel actual por el camino de Fase 2, con y sin `juicio_verificador`", "",
         f"Papel `{papel['prompt_version']}` ({papel['modelo']}), entrada de hoy; palabras con tiempos sintetizadas de la narración "
         f"({seg} s por palabra, sin escenas: `lectura` corre con esos tiempos, no con la voz real). Fase 2 no llama al verificador: "
         "solo lee `juicio_verificador.tokens` de la ficha.", "",
         "| cap | beat | ficha | estilo | juicio_verificador (regla, tokens) | validar_papel SIN juicio | validar_papel CON juicio | "
         "chequeo 5 SIN juicio | chequeo 5 CON juicio | cambia |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in filas:
        L.append(f"| {r['cap']} | {r['beat']} | {r['id']} | {r['estilo']} | {r['juicio']} | {r['sin']} | {r['con']} | "
                 f"{r['c5_sin'][:80]} | {r['c5_con'][:80]} | {'**sí**' if r['cambia'] else 'no'} |")
    con_j = [r for r in filas if r["juicio"] != "—"]
    L += ["", f"- Fichas con `juicio_verificador`: {len(con_j)} ({', '.join(r['id'] for r in con_j)}); de ellas, sin juicio "
          f"Fase 2 cortaría {sum(1 for r in con_j if r['sin'] != 'pasa')} y marcaría en el chequeo 5 "
          f"{sum(1 for r in con_j if r['c5_sin'] != '—')}; con juicio pasan {sum(1 for r in con_j if r['con'] == 'pasa')} y el "
          f"chequeo 5 marca {sum(1 for r in con_j if r['c5_con'] != '—')}.",
          f"- Fichas sin juicio: {len(filas) - len(con_j)}; ninguna cambia entre las dos columnas "
          f"({'OK' if not any(r['cambia'] for r in filas if r['juicio'] == '—') else 'ALGUNA CAMBIA: revisar'}).",
          f"- Lo que corta en ambas columnas es independiente del juicio (p. ej. `lectura` con tiempos sintéticos, o candado): "
          f"{[(r['id'], r['con'].split(':')[0]) for r in filas if r['con'] != 'pasa']}", ""]
    (AQUI / "FASE2_JUICIO.md").write_text("\n".join(L), encoding="utf-8")
    print("\n".join(L))


if __name__ == "__main__":
    main()
