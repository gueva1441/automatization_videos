"""
script_engine/gfx_rotulista.py — F29b §A: el rotulista; F36 §C: el texto de pantalla ya no lo escribe un modelo en
Fase 2: lo escribe m01e_pantalla en Fase 1 (el guion en papel, DECISIONES 19:54). Este archivo queda como fachada
(gfx_layer, fase2b, gfx_guion, los tests y el lab no cambian de import) y con `preparar_cap`: lee `01e_pantalla.json`,
alinea sus oraciones con las de la voz por texto (`alinear`, aclaración 2) y ancla cada ficha a su palabra
(`palabra_idx`). Regla (Omar): un texto vale si (a) dice algo que la voz no dice, (b) sobre lo que la voz cuenta en ese
momento y (c) sin adelantar; eso lo decide el papel y lo re-chequean los filtros de Fase 2.
    rotulista_filtros  validar_papel (los filtros de ORDEN, en orden), contradicciones
    rotulista_colocar  tiempos, colocar, reloj contra el corte, nunca al mismo tiempo
    clima              sellos del papel (y peak_word, traído de gfx_peak)
    voz_datos          pico del cap, reloj desde la voz, tarjeta fecha-hora derivada
    voz_utils          números, nombres y oraciones de la voz
F36 §D: se borraron rotulista_llm (el pedido al modelo) y el prefetch.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

# F36 §A: re-exports (nadie cambia de import); F36 §D: los de lo borrado se fueron con su código
from script_engine.voz_utils import (_analiza, _ARTPREP, beat_de_oracion, _DIFERENCIA, _DIG, _fmt, _MAGNITUD, munon,
                                     nombre_inicial, nombres, norm_oracion, _num_en, _num_tok, numero_en, numeros,
                                     _NUMW, oraciones, oraciones_de_texto, _palabra_en, palabras,
                                     palabras_de_contenido, _PARTICULAS, _raiz_en, _toks, _UNIDAD_1, _UNIDAD_2,
                                     _valor, _w2n, _W2N_LOCK)
from script_engine.rotulista_filtros import (ancla_papel, candado, contradicciones, _DOC, FICHA, gancho_dicho,
                                             lectura, LOCALES, no_dicho, ORDEN, PALABRAS_LOCALES, _palabras_mag,
                                             pide_documento, regla, spoiler, validar_papel)
from script_engine.rotulista_colocar import (caben, caracteres, choca, colocar, _cubre, despues_del_corte, _escena_de,
                                             escena_final, hasta_el_corte, KIND_FICHA, LECTURA_CPS, tiempos, unidades)
from script_engine.clima import (peak_word, _sello_queda, sellos_del_papel, TEMA_DE_MOOD, usadas_antes,
                                 vocabulario_clima)
from script_engine.voz_datos import (_entero, fechas_completas, _MES_RE, pico_cap, pico_plan, _raices, reloj_de_voz,
                                     tarjeta_inicial)


def voz_del_video(ctx: dict[str, Any]) -> list[str]:
    """§A.4: la voz de los 7 caps, oración por oración (el texto de la narración: el mismo que los subtítulos remapeados
    del sync map). Movida de rotulista_llm (F36 §D)."""
    out = []
    for c in sorted(ctx.get("chapters") or [], key=lambda c: int(c.get("chapter_number") or 0)):
        out += [s for s in re.split(r"(?<=[.!?…])\s+", str(c.get("narration") or "").strip()) if s.strip()]
    return out


def voz_previa(ctx: dict[str, Any]) -> str:
    """F34 §A.2.3: la voz de los caps anteriores al del contexto (un nombre que ya dijo no es spoiler). Movida de
    rotulista_llm (F36 §D)."""
    n = int(ctx.get("chapter_number") or 0)
    return " ".join(str(c.get("narration") or "") for c in sorted(ctx.get("chapters") or [],
                    key=lambda c: int(c.get("chapter_number") or 0)) if int(c.get("chapter_number") or 0) < n)


# ═══════════════════════ el guion en papel (F36 §C.4: Fase 2 consume m01e_pantalla) ═══════════════════════

def alinear(papel: list[str], voz: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Aclaración 2: cada oración del papel con la de la voz por texto normalizado (voz_utils.norm_oracion: sin tildes,
    puntuación, mayúsculas ni etiquetas de TTS), en orden. La que no es igual a ninguna se ancla a la más parecida
    (difflib) y queda marcada `exacta: False` (el guion la muestra como «papel sin alinear»)."""
    from difflib import SequenceMatcher
    vn = [norm_oracion(s["texto"]) for s in voz]
    out, j0 = [], 0
    for i, t in enumerate(papel):
        n = norm_oracion(t)
        j = next((k for k in range(j0, len(vn)) if vn[k] == n), None)
        if j is not None:
            out.append({"papel": i, "voz": j, "exacta": True, "parecido": 1.0, "texto": t})
            j0 = j + 1
            continue
        r = [(SequenceMatcher(None, n, v).ratio(), k) for k, v in enumerate(vn)]
        p, k = max(r) if r else (0.0, None)
        out.append({"papel": i, "voz": k, "exacta": False, "parecido": round(p, 3), "texto": t,
                    "voz_texto": voz[k]["texto"] if k is not None else None})
    return out


def palabra_idx(palabra: str, s: dict[str, Any]) -> tuple[int, str]:
    """§C.4: el `word_idx` de la palabra del papel en la oración de la voz (igual, o por su raíz de 5 letras); si no
    está, la primera palabra de contenido (≥ 4 letras, sin artículos ni preposiciones)."""
    from script_engine import evidence as ev
    ws = [ev.norm(re.sub(r"[^\w]", "", p["w"])) for p in s["palabras"]]
    w = ev.norm(re.sub(r"[^\w]", "", palabra or ""))
    if w and w in ws:
        return ws.index(w), "palabra del papel"
    if len(w) >= 5:
        k = next((k for k, x in enumerate(ws) if x[:5] == w[:5]), None)
        if k is not None:
            return k, "palabra del papel (raíz)"
    k = next((k for k, x in enumerate(ws) if len(x) >= 4 and x not in _ARTPREP), 0)
    return k, f"«{palabra}» no está en la oración: primera palabra de contenido"


def _item(pid: str, pool: dict | None, escaleta: dict, beat: int | None, gancho: bool, voz_video: list[str]
          ) -> dict[str, Any] | None:
    from script_engine import evidence as ev
    from script_engine.m01e_pantalla import _texto_item
    it = ev.items(pool).get(pid) if pool else None
    if it is None:
        return None
    ap = {str(a.get("id")): str(a.get("por_que") or "") for a in escaleta.get("a_pantalla") or []}
    voz = " ".join(voz_video)
    return {"id": pid, "a_pantalla": pid in ap, "por_que": ap.get(pid, ""), "beats": [beat] if beat else [],
            "tipo": pid[:1].upper(), "kind": it["_kind"], "texto": _texto_item(it), "fuente": str(it.get("fuente") or ""),
            "autor": str(it.get("autor") or ""), "gancho": gancho,
            "dice_voz": gancho and (ev.used_in(voz, it) or any(numero_en(n, voz) for n in ev._figures(ev.text_of(it))))}


def preparar_cap(cap: int, cap_id: str, real: dict, ctx: dict[str, Any], words: list[dict], time_offset: float,
                 pre_roll: float = 0.0, steps_dir: Path | None = None) -> tuple[dict[str, Any], dict[str, Any]]:
    """F36 §C.4 (sin modelo): (entrada, papel del cap) desde `01e_pantalla.json` del topic de Fase 1. La entrada trae
    las oraciones de la voz con tiempos, los beats con sus ventanas, los ítems del pool que el papel usa en este cap
    (en el gancho, con «la voz lo dice en el video»), el pico, la voz del video y la de los caps anteriores. El papel
    del cap: los bloques (fichas ancladas a la oración de la voz y a su palabra), los sellos, los relojes, la tarjeta y
    la alineación (oraciones del papel que no alinean, anotadas)."""
    from script_engine.m01e_pantalla import TIPO_DE_ESTILO, cargar_papel
    escaleta = ctx.get("escaleta") or {}
    sents = oraciones(words, time_offset)
    beats = real["beats"]
    for s in sents:
        s["beat"] = beat_de_oracion(s, beats)
    voz_video = voz_del_video(ctx)
    pk = pico_cap(cap, escaleta, beats, sents, ctx.get("pool"))
    papel = cargar_papel(str(ctx.get("topic_id") or ctx.get("video_id")), steps_dir)
    rot: dict[str, Any] = {"papel": True, "modelo": None, "final": {"bloques": []}, "sellos": [], "relojes": [],
                           "tarjeta": None, "alineacion": [], "sin_alinear": []}
    its: list[dict[str, Any]] = []
    if papel is None:
        rot["error"] = "sin guion en papel (01e_pantalla.json): el cap sale sin fichas ni sellos"
    else:
        rot["modelo"] = f"papel {papel.get('prompt_version')} ({papel.get('modelo')})"
        rot["tarjeta"] = papel.get("tarjeta")
        pc = next((c for c in papel.get("caps") or [] if c["cap"] == cap_id), None)
        al = alinear(pc["oraciones"], sents) if pc else []
        rot["alineacion"] = al
        rot["sin_alinear"] = [a for a in al if not a["exacta"]]
        voz_de = {a["papel"]: a for a in al}
        funcion = {b["n"]: b.get("funcion") for b in escaleta.get("beats") or []}
        for b in [b for b in papel.get("beats") or [] if b["cap"] == cap_id]:
            f, se = b.get("ficha"), b.get("sello")
            if f:
                a = voz_de.get(int(f["sentence_idx"]))
                x = _item(f["pool_id"], ctx.get("pool"), escaleta, b["beat"], funcion.get(b["beat"]) == "gancho",
                          voz_video)
                if a is None or a["voz"] is None or x is None:
                    rot.setdefault("sin_colocar", []).append({**f, "beat": b["beat"], "motivo":
                                                             "sin oración de la voz" if x else "no está en el pool"})
                    continue
                if x["id"] not in {y["id"] for y in its}:
                    its.append(x)
                s = sents[a["voz"]]
                wi, como = palabra_idx(f.get("palabra") or "", s)
                rot["final"]["bloques"].append({
                    "pool_id": f["pool_id"], "sentence_idx": a["voz"], "word_idx": wi, "beat": b["beat"], "rank": 1,
                    "tipo": TIPO_DE_ESTILO.get(f.get("estilo") or "normal", "hecho"), "estilo": f.get("estilo"),
                    "etiqueta": f.get("etiqueta"), "texto": f.get("texto"), "aporta": f.get("aporta"), "papel": True,
                    "palabra_papel": f.get("palabra"), "ancla_palabra": como,
                    **({"sin_alinear": a} if not a["exacta"] else {}), **({"editado": True} if f.get("editado") else {})})
            if se:
                a = voz_de.get(int(se["sentence_idx"]))
                rot["sellos"].append({"palabra": se["palabra"], "beat": b["beat"], "sentence_idx": a["voz"] if a else None,
                                      **({"sin_alinear": a} if a and not a["exacta"] else {}),
                                      **({"editado": True} if se.get("editado") else {})})
        for r in [r for r in papel.get("relojes") or [] if r.get("cap") == cap_id]:
            a = voz_de.get(int(r["sentence_idx"])) if r.get("sentence_idx") is not None else None
            rot["relojes"].append({**r, "sentence_idx_voz": a["voz"] if a else None})
    ent = {"cap": cap, "titulo": " · ".join(dict.fromkeys(b["funcion"] for b in beats)), "oraciones": sents,
           "beats": [{k: b[k] for k in ("n", "funcion", "t0", "t1", "cierre", "dato_central", "datos_apoyo")}
                     for b in beats],
           "items": its, "ya_mostrado": [], "pico": pk, "voz_video": voz_video, "pre_roll": round(float(pre_roll), 3),
           "voz_antes": voz_previa(ctx)}
    return ent, rot
