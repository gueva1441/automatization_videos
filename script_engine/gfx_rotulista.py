"""
script_engine/gfx_rotulista.py — F29b §A: el rotulista. El texto de pantalla lo escribe alguien, anclado a la oración.
F29c: por beat, anclado a la palabra, y la ficha es el title card.

Regla (Omar): un bloque vale si (a) dice algo que la voz no dice, (b) sobre lo que la voz cuenta en ese momento y (c) sin
adelantar. Con `gfx_rules.rotulista` y escaleta (realizador), por cap:
    entrada    oraciones de la voz con tiempos y cada palabra numerada (gfx_peak.sentences), el beat de cada oración,
               beats del cap (gfx_beats_chNN.json), ítems = los `a_pantalla` del cap + `dato_central`/`datos_apoyo` de
               sus beats (texto fuente completo, fuente, `por_que`), lo ya mostrado (los `a_pantalla` de caps
               anteriores: dejan correr los 7 caps en paralelo), el pico ÚNICO del cap (pico_cap) y la voz de todo el
               video (para la coherencia de cifras).
    llamada    UNA por cap con claude_helpers (Sonnet 5.5 por defecto, effort medium, JSON sin esquema), prompt literal
               (ROTULISTA_SYSTEM / ROTULISTA_USER, HANDOFF_F29c §A.5), cruda en `_fase2b_work/rotulista_chNN.raw.json`
               (caché por pedido). De la respuesta se toma el primer objeto JSON válido (§A.6.1). Un reintento si no
               parsea o si una regla de contenido saca algo; otro si faltan `a_pantalla`. Tope de US$ antes de cada
               llamada (con las llamadas en vuelo). Sin respuesta válida, el cap sale sin bloques (nunca se inventa).
    validar    (determinista) anclaje (oración y palabra que existen, en un beat del ítem; el `a_pantalla` del beat pico
               pasa al beat siguiente si su ítem es de ese beat), forma (tipo, etiqueta, valor, muñón, que quepa en la
               ficha), candado (cita = subcadena del texto fuente; resto = cada número, nombre propio y año en el texto
               fuente), tiempos (§A.2: t0 = la palabra `word_idx`; t1 = fin de la oración, o de la siguiente si no
               alcanza el mínimo de lectura caracteres ÷ 15; nunca después del corte de escena; si no alcanza, no va),
               no dicho (oración ancla ± 1) y spoiler (oraciones posteriores del cap) (§A.3), coherencia de cifras con
               la voz de todo el video (§A.4).
    finalizar  (§A.1) por beat queda 1 (`a_pantalla` primero, después `rank`); el beat pico, 0.
    colocar    cifra, hecho, persona → ficha (el title card sin #tc-dim: kicker = etiqueta, título = dato); documento →
               archive_clipping; cita → quote_card; lupa → evidence_zoom con la caja de visión del detalle.
    escena     (§0/§A.5, después del reloj y el sello) una cosa por escena: la ficha espera a la escena siguiente del
               beat si en la suya hay title card, reloj, sello u otro bloque; el reloj (animación) no va encima de un
               texto ni en el beat de otra animación.
Lecturas declaradas (F29b_REPORT y F29c_REPORT). Sin escaleta o con el flag apagado no corre nada de esto.

F36 §A: el rotulista está partido en cinco módulos (el código se movió, no se reescribió); este archivo queda como
fachada para que gfx_layer, fase2b, gfx_guion, los tests y el lab no cambien de import:
    rotulista_llm      prompt, entrada, pedido y llamada (caché, ledger, tope, reintento)
    rotulista_filtros  validar (los filtros de ORDEN, en orden), finalizar, contradicciones
    rotulista_colocar  tiempos, colocar, ediciones a mano, escena
    clima              sellos de clima (y peak_word, traído de gfx_peak)
    voz_datos          pico del cap, reloj y agua desde la voz, tarjeta fecha-hora
    voz_utils          números, nombres y oraciones de la voz (los usan los cinco)
F36 §C.4: el texto de pantalla ya no lo escribe un modelo en Fase 2: lo escribe m01e_pantalla en Fase 1 (el guion en
papel). preparar_cap lee `01e_pantalla.json`, alinea sus oraciones con las de la voz por texto (`alinear`) y ancla cada
ficha a su palabra (`palabra_idx`); prefetch (el rotulista de los 7 caps en paralelo) se fue con el modelo.
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any

# F36 §A: re-exports (todos los nombres que el módulo tenía antes de partirse; nadie cambia de import)
from script_engine.voz_utils import (_analiza, _ARTPREP, beat_de_oracion, _DIFERENCIA, _DIG, _fmt, _MAGNITUD, munon,
                                     nombre_inicial, nombres, _num_en, _num_tok, numero_en, numeros, _NUMW, oraciones,
                                     _palabra_en, palabras, palabras_de_contenido, _PARTICULAS, _raiz_en, _toks,
                                     _UNIDAD_1, _UNIDAD_2, _valor, _w2n, _W2N, _W2N_LOCK)
from script_engine.rotulista_filtros import (A_PANTALLA_POR_BEAT, ancla_papel, ORDEN_MODELO, validar_papel, LOCALES, anclaje, candado, cantidad, coherencia, CON_ETIQUETA,
                                             contradicciones, _DOC, FICHA, finalizar, forma, gancho_dicho, lectura,
                                             lo_que_pide, no_dicho, ORDEN, pide_documento, regla, spoiler, TIPOS,
                                             validar)
from script_engine.rotulista_colocar import (caben, hasta_el_corte, animacion_de_cifra, aplicar_ediciones, CAMPOS_EDITABLES, caracteres,
                                             colocar, _cubre, despues_del_corte, EDICIONES, ediciones_de, _escena_de,
                                             escena_final, guardar_ediciones, KIND_FICHA, LECTURA_CPS, lupa_de_detalles,
                                             mover_a_escena, tiempos, UNIDAD_CONTADOR, unidades)
from script_engine.rotulista_llm import (pasados_de_largo, A1_SYSTEM, A1_USER, _deshacer, EFFORT_DEFAULT, _EN_VUELO, entrada, gastado,
                                         _HUECOS, items_cap, items_gancho, _ledger, LINEA_B7, llamar, _LOCK,
                                         MODELO_DEFAULT,
                                         OUT_TOKENS_PEOR, _post_con_registro, primer_json, prompt_md5, prompt_user,
                                         PROMPT_VERSION, PROMPT_VERSION_F29B, REGLAS_REINTENTO, _reintento,
                                         ROTULISTA_SYSTEM, ROTULISTA_SYSTEM_F29C, ROTULISTA_SYSTEM_F32, ROTULISTA_USER,
                                         ROTULISTA_USER_F32, _solo_el_json, _tipo_id, TopeRotulista, voz_del_video,
                                         voz_previa, ya_mostrado)
from script_engine.clima import (usadas_antes, sellos_del_papel, elegir_clima, _gemini_clima, palabra_clima, peak_word, prompt_clima,
                                 SELLO_CLIMA_PROMPT, _sello_queda, sellos_por_tema, TEMA_DE_MOOD, vocabulario_clima)
from script_engine.voz_datos import (_agua_de, agua_de_voz, AGUA_ETIQUETAS, _entero, fechas_completas, _MES_RE,
                                     pico_cap, pico_plan, _raices, reloj_de_voz, tarjeta_inicial)


# ═══════════════════════ el guion en papel (F36 §C.4: Fase 2 consume m01e_pantalla) ═══════════════════════

def alinear(papel: list[str], voz: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Aclaración 2: cada oración del papel con la de la voz por texto normalizado (voz_utils.norm_oracion: sin tildes,
    puntuación, mayúsculas ni etiquetas de TTS), en orden. La que no es igual a ninguna se ancla a la más parecida
    (difflib) y queda marcada `exacta: False` (el guion la muestra como «papel sin alinear»)."""
    from difflib import SequenceMatcher
    from script_engine.voz_utils import norm_oracion
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
