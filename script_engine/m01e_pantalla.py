"""
script_engine/m01e_pantalla.py — F36 §C: el guion de pantalla EN PAPEL (DECISIONES 2026-10-26 19:54: «el autor de la
pantalla va a Fase 1»). Corre en Fase 1 después de m01d_particion y antes de la voz (fase1_5.run_guion_v3/v4, con su
costo en 01_v3_costos.json como los demás pasos) o suelto: `python -m script_engine.m01e_pantalla <topic>`.

    entrada    (§C.1, una para todo el video) por cap el título (01a_skeleton) y sus oraciones numeradas, partidas con
               el mismo corte de la voz (voz_utils.oraciones_de_texto) desde los párrafos de 01b_narracion_v3, cada una
               con su beat y `caben` (palabras × SEG_POR_PALABRA × 15 cps: una estimación; la medida real es de Fase 2);
               los beats de la escaleta (n, función, pico sí/no, dato central, apoyo, cierre); el archivo = el pool
               completo con cifra, fecha o cita (D con número, T, Q) y las personas (P), cada ítem con id, texto, fuente
               (y autor, las citas) y `beats_que_lo_cuentan`; el vocabulario `sellos_clima` del perfil.
    llamada    UNA a Sonnet 5.5 (medium) con el prompt literal de §C.2 (PANTALLA_SYSTEM; el USER = el JSON de entrada +
               «Formato de salida: …»), tope US$ TOPE_USD contando las dos llamadas, caché por md5 de la entrada y la
               versión del prompt. Un reintento si el JSON no parsea o si la validación saca ≥ REINTENTO_FICHAS fichas,
               con los motivos. Dos respuestas sin JSON → PARADA (la cruda queda en 01e_pantalla.raw.json).
    validar    (§C.3, sin tiempos ni fotos, con los filtros de rotulista_filtros) por ficha: anclaje (cap, beat, ítem y
               oración que existen; la oración es del beat), formato (etiqueta en 1 línea y dato en 2, gfx_project.
               ficha_medida), candado (números, nombres y años literales en el texto del ítem; en el gancho vale la voz
               de todo el video), no dicho (oración ancla ± 1; en el gancho, el dato que la voz dice en el video),
               spoiler (la narración posterior del cap y de los caps siguientes), el mismo dato una sola vez en el video,
               `caben`. Por sello: palabra de la lista, no es palabra de la voz del cap, no repetida en el video, uno por
               beat. Lo que cae va a `descartados` con la regla y el motivo.
    estilo     (§C.1) lo pone el código por tipo de dato: Q → cita (con autor), P → nombre, D/T cuya etiqueta (o el
               `por_que` de su `a_pantalla`) nombra una carta, un acta, un informe o un documento → papel, resto → normal.
Salida en el directorio del topic de Fase 1 (aclaración 1: el que leen gfx_realizador y el rotulista): 01e_pantalla.json
(lo consume Fase 2), 01e_pantalla.md (una línea por beat y lo que cayó, para Omar) y 01e_pantalla.raw.json.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Callable

if __name__ == "__main__" and __package__ in (None, ""):          # suelto: python script_engine/m01e_pantalla.py <topic>
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from script_engine import evidence as ev                           # noqa: E402
from script_engine.voz_utils import _raiz_en, numero_en, numeros, oraciones_de_texto, palabras   # noqa: E402

PROMPT_VERSION = "m01e-1"
MODELO = "claude-sonnet-5-5"
EFFORT = "medium"
TOPE_USD = 0.50                 # derivado: el tope del pedido de Omar para C (HANDOFF_F36_C_D §C.2)
SEG_POR_PALABRA = 0.35          # medido: Vajont ch04 (mediana de las 19 oraciones con tiempos de ElevenLabs = 0.348)
OUT_TOKENS_PEOR = 16_000        # derivado: el peor caso de salida del rotulista de gfx (razonamiento + JSON)
REINTENTO_FICHAS = 3            # derivado: HANDOFF_F36_C_D §C.2/§C.3 («si son ≥ 3 fichas, un reintento»)
ARCHIVO = "01e_pantalla"
ESTILOS = ("normal", "papel", "cita", "nombre")


# ═══════════════════════ prompt (HANDOFF_F36_C_D §C.2, literal) ═══════════════════════

PANTALLA_SYSTEM = """Sos el rotulista de un documental de historia oscura en español. Recibís la narración completa de un video (7 capítulos, oraciones numeradas), la escaleta (qué cuenta cada beat y cuál es el pico de cada capítulo), el archivo del caso (datos con cifra, fecha, cita o persona, con su fuente) y una lista de palabras de clima. Escribís lo que va en pantalla para todo el video, de una vez.

Reglas de todo texto en pantalla:
(a) dice lo que la voz NO dice en ese capítulo: un dato del archivo que la narración no menciona;
(b) va sobre la oración que habla de ese asunto: elegí la oración ancla y la palabra de la oración donde debe aparecer;
(c) no adelanta nada que la narración cuente después, en ese capítulo o en los siguientes.

Qué podés poner:
- FICHA: como máximo una por beat, y puede no haber. Etiqueta: una línea corta que diga qué es («ANCHO DE LA FISURA», «ACTA DEL CONSEJO SUPERIOR»), sin el año de publicación de la fuente. Dato: UNA línea corta con la cifra, la fecha o el hecho, tal como está en el archivo: cada número, nombre y año tiene que estar literal en el texto del dato que elegiste, no en otro lado. Etiqueta + dato no pueden pasar de los caracteres que caben en la oración ancla (`caben`); si no caben, elegí otra oración o un dato más corto. Para una cita (Q), el dato es la frase literal del archivo, recortada pero sin cambiar palabras, y lleva autor.
- SELLO DE CLIMA: como máximo uno por beat, y puede no haber. Una palabra de la lista que nombre lo que se siente en ese momento del relato. Nunca una palabra que la voz diga en ese capítulo, y nunca la misma palabra dos veces en el video. Elegí la oración donde cae.
- RELOJ: por capítulo, las fechas completas (día, mes y año) que la voz dice, con la oración donde las dice.
- TARJETA: solo si el video abre con un momento con fecha y hora en el archivo: «9 OCT 1963 · 22:39».

Prioridades: en el beat pico del capítulo, el dato marcado como central por la escaleta; en el gancho (capítulo 1), cualquier dato del archivo que la voz no diga en todo el video y que haga quedarse a quien mira: el gancho nunca queda sin ficha. Los datos marcados con tu beat son los que la escaleta cuenta ahí; los demás son el resto del archivo: usalos si suman más y no adelantan nada. Un mismo dato una sola vez en el video. Si dudás entre dos, el que tiene cifra o fecha.

Devolvé solo JSON con el formato pedido, con `aporta` (una línea: qué suma que la voz no dice) por ficha y `descartados` con motivo."""

# §C.1: el esquema de salida (por cap y beat; relojes por cap; tarjeta; descartados). Sin `estilo`: lo pone el código.
FORMATO_SALIDA = ('{"beats": [{"cap": "ch03", "beat": 5, "ficha": {"pool_id": "D49", "sentence_idx": 17, '
                  '"palabra": "fisura", "etiqueta": "ANCHO DE LA FISURA", "texto": "Más de 1 metro", "aporta": "…"} | '
                  'null, "sello": {"palabra": "AVISO", "sentence_idx": 3} | null}], "relojes": [{"cap": "ch03", '
                  '"sentence_idx": 4, "fecha": "9 OCT 1963"}], "tarjeta": {"texto": "9 OCT 1963 · 22:39"} | null, '
                  '"descartados": [{"pool_id": "…", "motivo": "…"}]}')


def prompt_md5() -> str:
    """md5 del prompt literal (SYSTEM + la línea del formato), para el reporte."""
    return hashlib.md5((PANTALLA_SYSTEM + "\n\n" + FORMATO_SALIDA).encode("utf-8")).hexdigest()


def pedido(ent: dict[str, Any]) -> str:
    """El USER: el JSON de entrada de §C.1 y, al final, la línea del formato."""
    return json.dumps(_para_modelo(ent), ensure_ascii=False) + "\n\nFormato de salida: " + FORMATO_SALIDA


# ═══════════════════════ entrada (§C.1) ═══════════════════════

def cap_id(n: int) -> str:
    return f"ch{int(n):02d}"


def _texto_item(it: dict[str, Any]) -> str:
    """El texto del ítem que ve el modelo y contra el que corre el candado (el mismo)."""
    k = it["_kind"]
    if k == "cronologia":
        cuando = str(it.get("fecha") or "") + (f", hora {it['hora']}" if it.get("hora") else "")
        return f"{ev.text_of(it)} (fecha {cuando})" if cuando else ev.text_of(it)
    if k == "personajes":
        return f"{it.get('nombre') or ''} — {it.get('rol') or ''}".strip(" —")
    return re.sub(r"\s+", " ", ev.text_of(it)).strip()


def _tipo(it: dict[str, Any]) -> str | None:
    """D con número, T, Q, P (§C.1); el resto del pool (lugares, D sin cifra) no entra al archivo."""
    k = it["_kind"]
    if k == "datos":
        return "D" if numeros(ev.text_of(it)) else None
    return {"cronologia": "T", "citas": "Q", "personajes": "P"}.get(k)


def cargar(topic_id: str, steps_dir: Path, pool: dict | None = None) -> dict[str, Any]:
    """Los archivos de Fase 1 del topic (aclaración 1: los que leen gfx_realizador y el rotulista): escaleta, párrafos
    por cap y beat (01b_narracion_v3), títulos de la partición (01a_skeleton) y el pool (00_pool_v3, o el que se pasa)."""
    sd = Path(steps_dir) / topic_id

    def lee(nombre: str) -> dict:
        return json.loads((sd / nombre).read_text(encoding="utf-8"))
    sk = lee("01a_skeleton.json")
    return {"topic_id": topic_id, "dir": sd, "escaleta": lee("01a_escaleta.json"),
            "parrafos": lee("01b_narracion_v3.json").get("parrafos") or [],
            "titulos": {int(c["chapter_number"]): str(c.get("title") or "") for c in sk.get("chapters") or []},
            "pool": pool if pool is not None else lee("00_pool_v3.json")}


def entrada(carga: dict[str, Any], vocabulario: list[str]) -> dict[str, Any]:
    """La entrada de §C.1 (con lo que el código necesita para validar; `_para_modelo` saca lo que el modelo no ve)."""
    from script_engine.gfx_realizador import beat_de_pantalla
    from script_engine.music_intensity import beat_pico_de_cap
    from script_engine.rotulista_colocar import LECTURA_CPS
    esc, pars = carga["escaleta"], carga["parrafos"]
    caps: list[dict[str, Any]] = []
    for n in sorted({int(p["cap"]) for p in pars}):
        ors = []
        for p in [p for p in pars if int(p["cap"]) == n]:
            for t in oraciones_de_texto(p["texto"]):
                ors.append({"idx": len(ors), "beat": int(p.get("beat") or 0), "texto": t,
                            "caben": int(len(palabras(t)) * SEG_POR_PALABRA * LECTURA_CPS)})
        caps.append({"cap": cap_id(n), "n": n, "titulo": carga["titulos"].get(n, ""), "oraciones": ors})
    beats_esc = sorted(esc.get("beats") or [], key=lambda b: int(b["n"]))
    picos = {}
    for n in {int(b["cap"]) for b in beats_esc}:
        bc = [b for b in beats_esc if int(b["cap"]) == n]
        picos[n] = beat_pico_de_cap(bc, (esc.get("pico") or {}).get("beat"))
    beats = [{"n": int(b["n"]), "cap": cap_id(b["cap"]), "funcion": str(b.get("funcion") or ""),
              "pico": int(b["n"]) == picos.get(int(b["cap"])), "dato_central": str(b.get("dato_central") or ""),
              "apoyo": [str(x) for x in b.get("datos_apoyo") or []], "cierre": str(b.get("cierre") or "").strip()}
             for b in beats_esc]
    cuentan: dict[str, list[int]] = {}
    for b in beats:
        for i in [b["dato_central"]] + b["apoyo"]:
            if i:
                cuentan.setdefault(i, []).append(b["n"])
    for a in esc.get("a_pantalla") or []:                 # el `a_pantalla` de la escaleta, en su beat
        bc = [{"n": int(b["n"]), "dato_central": str(b.get("dato_central") or ""),
               "datos_apoyo": [str(x) for x in b.get("datos_apoyo") or []],
               "texto": " ".join(p["texto"] for p in pars if int(p.get("beat") or 0) == int(b["n"])),
               "campos": " ".join(str(b.get(c) or "") for c in ("emocion", "imagen_sensorial", "pregunta_abierta", "cierre"))}
              for b in beats_esc if int(b["cap"]) == int(a.get("cap") or 0)]
        nb, _ = beat_de_pantalla(a, bc)
        if nb is not None and nb not in cuentan.setdefault(str(a.get("id")), []):
            cuentan[str(a["id"])].append(nb)
    archivo = []
    for i, it in ev.items(carga["pool"]).items():
        t = _tipo(it)
        if t is None:
            continue
        x = {"id": i, "texto": _texto_item(it), "fuente": str(it.get("fuente") or ""),
             "beats_que_lo_cuentan": sorted(cuentan.get(i) or [])}
        if t == "Q":
            x["autor"] = str(it.get("autor") or "")
        archivo.append(x)
    return {"topic_id": carga["topic_id"], "caps": caps, "beats": beats, "archivo": archivo,
            "clima": list(vocabulario), "a_pantalla": {str(a.get("id")): str(a.get("por_que") or "")
                                                       for a in esc.get("a_pantalla") or []}}


def _para_modelo(ent: dict[str, Any]) -> dict[str, Any]:
    return {"caps": [{"cap": c["cap"], "titulo": c["titulo"],
                      "oraciones": [{k: s[k] for k in ("idx", "beat", "texto", "caben")} for s in c["oraciones"]]}
                     for c in ent["caps"]],
            "beats": ent["beats"], "archivo": ent["archivo"], "clima": ent["clima"]}


def entrada_md5(ent: dict[str, Any]) -> str:
    return hashlib.md5(pedido(ent).encode("utf-8")).hexdigest()


# ═══════════════════════ validación en papel (§C.3) ═══════════════════════

def estilo_de(pool_id: str, etiqueta: str, por_que: str = "") -> str:
    """§C.1: el estilo sale del tipo de dato, sin modelo. Lectura declarada de «D/T que pide_documento»: la etiqueta de la
    ficha (lo que es: «ACTA DEL CONSEJO SUPERIOR») o el `por_que` de su `a_pantalla` nombran una carta, un acta, un
    informe o un documento (rotulista_filtros.pide_documento, F32 §B.4)."""
    from script_engine.rotulista_filtros import pide_documento
    t = str(pool_id)[:1].upper()
    if t == "Q":
        return "cita"
    if t == "P":
        return "nombre"
    return "papel" if pide_documento(f"{etiqueta} {por_que}") else "normal"


TIPO_DE_ESTILO = {"normal": "hecho", "papel": "documento", "cita": "cita", "nombre": "persona"}   # el de los filtros


def _voz_video(ent: dict[str, Any]) -> list[str]:
    return [s["texto"] for c in ent["caps"] for s in c["oraciones"]]


def validar(resp: Any, ent: dict[str, Any]) -> dict[str, Any]:
    """§C.3 sobre la respuesta: {beats (lo que queda, por cap y beat), relojes, tarjeta, descartados (del modelo y de la
    validación, con regla y motivo), fichas_fuera}."""
    from script_engine.gfx_project import ficha_medida
    from script_engine.rotulista_colocar import caracteres
    from script_engine.rotulista_filtros import candado, gancho_dicho, no_dicho, spoiler
    caps = {c["cap"]: c for c in ent["caps"]}
    orden_caps = [c["cap"] for c in ent["caps"]]
    beats = {b["n"]: b for b in ent["beats"]}
    arch = {x["id"]: x for x in ent["archivo"]}
    pool = ev.items(ent.get("_pool")) if ent.get("_pool") else {}
    lista = {ev.norm(w): w for w in ent["clima"]}
    voz_video = _voz_video(ent)
    voz_txt = " ".join(voz_video)
    resp = resp if isinstance(resp, dict) else {}
    filas = sorted([b for b in resp.get("beats") or [] if isinstance(b, dict)],
                   key=lambda b: (str(b.get("cap")), _int(b.get("beat")) or 0))
    quedan: dict[tuple[str, int], dict[str, Any]] = {}
    desc: list[dict[str, Any]] = [{"pool_id": d.get("pool_id"), "regla": "modelo", "motivo": d.get("motivo"),
                                   "quien": "modelo"} for d in resp.get("descartados") or [] if isinstance(d, dict)]
    usados_ids: set[str] = set()
    usadas_pal: set[str] = set()
    fichas_fuera = 0
    for f in filas:
        cap, nb = str(f.get("cap") or ""), _int(f.get("beat"))
        b = beats.get(nb)
        k = (cap, nb if nb is not None else -1)
        slot = quedan.setdefault(k, {"cap": cap, "beat": nb, "funcion": (b or {}).get("funcion"),
                                     "pico": bool((b or {}).get("pico")), "ficha": None, "sello": None})
        fi = f.get("ficha") if isinstance(f.get("ficha"), dict) else None
        if fi:
            motivo, regla, ficha = _validar_ficha(fi, cap, nb, b, slot, caps, orden_caps, arch, pool, voz_video, voz_txt,
                                                  usados_ids, ent, ficha_medida, caracteres, candado, gancho_dicho,
                                                  no_dicho, spoiler)
            if motivo:
                fichas_fuera += 1
                desc.append({"pool_id": fi.get("pool_id"), "cap": cap, "beat": nb, "que": "ficha",
                             "etiqueta": fi.get("etiqueta"), "texto": fi.get("texto"),
                             "sentence_idx": fi.get("sentence_idx"), "regla": regla, "motivo": motivo,
                             "quien": "validación"})
            else:
                slot["ficha"] = ficha
                usados_ids.add(ficha["pool_id"])
        se = f.get("sello") if isinstance(f.get("sello"), dict) else None
        if se:
            w = lista.get(ev.norm(str(se.get("palabra") or "").strip()))
            si = _int(se.get("sentence_idx"))
            c = caps.get(cap)
            voz_cap = " ".join(s["texto"] for s in c["oraciones"]) if c else ""
            motivo = ("el cap no existe" if c is None else
                      f"«{se.get('palabra')}» no está en el vocabulario de clima" if w is None else
                      f"la oración [{se.get('sentence_idx')}] no existe en {cap}" if si is None
                      or not 0 <= si < len(c["oraciones"]) else
                      f"«{w}» es palabra de la voz de {cap}" if _raiz_en(w, voz_cap) else
                      f"«{w}» ya salió en el video" if w in usadas_pal else
                      f"un sello por beat: el beat {nb} ya tiene «{slot['sello']['palabra']}»" if slot["sello"] else None)
            if motivo:
                desc.append({"cap": cap, "beat": nb, "que": "sello", "texto": se.get("palabra"),
                             "sentence_idx": se.get("sentence_idx"), "regla": "sello", "motivo": motivo,
                             "quien": "validación"})
            else:
                slot["sello"] = {"palabra": w, "sentence_idx": si, "oracion": c["oraciones"][si]["texto"]}
                usadas_pal.add(w)
    for n, b in beats.items():                              # todos los beats del video, aunque el modelo no los nombre
        quedan.setdefault((b["cap"], n), {"cap": b["cap"], "beat": n, "funcion": b["funcion"], "pico": b["pico"],
                                          "ficha": None, "sello": None})
    relojes = []
    for r in resp.get("relojes") or []:
        if not isinstance(r, dict):
            continue
        c, si = caps.get(str(r.get("cap") or "")), _int(r.get("sentence_idx"))
        ok = c is not None and si is not None and 0 <= si < len(c["oraciones"])
        relojes.append({"cap": r.get("cap"), "sentence_idx": si, "fecha": str(r.get("fecha") or ""),
                        "oracion": c["oraciones"][si]["texto"] if ok else None, **({} if ok else {"error": "la oración no existe"})})
    tj = resp.get("tarjeta") if isinstance(resp.get("tarjeta"), dict) and resp["tarjeta"].get("texto") else None
    out_beats = sorted(quedan.values(), key=lambda s: (orden_caps.index(s["cap"]) if s["cap"] in orden_caps else 99,
                                                       s["beat"] if s["beat"] is not None else -1))
    return {"beats": out_beats, "relojes": relojes, "tarjeta": {"texto": str(tj["texto"])} if tj else None,
            "descartados": desc, "fichas_fuera": fichas_fuera}


def _int(v: Any) -> int | None:
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _validar_ficha(fi: dict, cap: str, nb: int | None, b: dict | None, slot: dict, caps: dict, orden_caps: list[str],
                   arch: dict, pool: dict, voz_video: list[str], voz_txt: str, usados_ids: set[str], ent: dict,
                   ficha_medida: Callable, caracteres: Callable, candado: Callable, gancho_dicho: Callable,
                   no_dicho: Callable, spoiler: Callable) -> tuple[str | None, str | None, dict | None]:
    """(motivo, regla, ficha validada) de una ficha del papel, en el orden de §C.3."""
    pid = str(fi.get("pool_id") or "")
    c = caps.get(cap)
    si = _int(fi.get("sentence_idx"))
    et = re.sub(r"\s+", " ", str(fi.get("etiqueta") or "")).strip()
    txt = re.sub(r"\s+", " ", str(fi.get("texto") or "")).strip()
    x = arch.get(pid)
    # anclaje
    if c is None or b is None or b["cap"] != cap:
        return f"el beat {nb} no es de {cap}", "anclaje", None
    if x is None:
        return f"{pid!r} no está en el archivo", "anclaje", None
    if si is None or not 0 <= si < len(c["oraciones"]):
        return f"la oración [{fi.get('sentence_idx')}] no existe en {cap}", "anclaje", None
    s = c["oraciones"][si]
    if s["beat"] != nb:
        return f"la oración [{si}] es del beat {s['beat']}, no del {nb}", "anclaje", None
    if slot["ficha"]:
        return f"una ficha por beat: el beat {nb} ya tiene {slot['ficha']['pool_id']}", "anclaje", None
    estilo = estilo_de(pid, et, ent["a_pantalla"].get(pid, ""))
    tipo = TIPO_DE_ESTILO[estilo]
    autor = str(x.get("autor") or "")
    if tipo == "cita":
        txt = re.sub(r"^[«\"“]+|[»\"”]+$", "", txt).strip()
    # formato
    if not txt or not et:
        return "etiqueta o dato vacío", "formato", None
    if tipo == "cita" and not autor:
        return "la cita no tiene autor en el archivo", "formato", None
    m = ficha_medida(et, txt)
    if m["kicker"] > 1 or m["title"] > 2:
        return f"etiqueta en {m['kicker']} línea(s) y dato en {m['title']} (1 y 2)", "formato", None
    # candado, no dicho, spoiler (los de rotulista_filtros, con el ítem del archivo como texto fuente)
    gancho = (b.get("funcion") == "gancho")
    it = pool.get(pid)
    dice_voz = bool(it) and gancho and (ev.used_in(voz_txt, it) or any(numero_en(n, voz_txt)
                                                                       for n in ev._figures(ev.text_of(it))))
    xi = {"id": pid, "texto": x["texto"], "fuente": x["fuente"], "autor": autor, "a_pantalla": pid in ent["a_pantalla"],
          "por_que": ent["a_pantalla"].get(pid, ""), "gancho": gancho, "dice_voz": dice_voz}
    k = orden_caps.index(cap)
    antes = " ".join(ss["texto"] for cc in orden_caps[:k] for ss in caps[cc]["oraciones"])
    ctx: dict[str, Any] = {"its": {pid: xi}, "x": xi, "pid": pid, "sents": c["oraciones"], "si": si, "s": s,
                           "voz_video": voz_video, "tipo": tipo, "txt": txt, "et": et}
    fil_ent = {"voz_antes": antes}
    for f, regla in ((gancho_dicho, "no_dicho"), (candado, "candado"), (no_dicho, "no_dicho")):
        mot = f({}, fil_ent, ctx)
        if mot:
            return mot, regla, None
    despues = c["oraciones"] + [ss for cc in orden_caps[k + 1:] for ss in caps[cc]["oraciones"]]
    mot = spoiler({}, fil_ent, {**ctx, "sents": despues})            # (c): en ese cap o en los siguientes
    if mot:
        return mot.replace("del cap", "del cap o de un cap siguiente"), "spoiler", None
    if pid in usados_ids:
        return f"{pid} ya va en otro beat del video", "una_vez", None
    n = caracteres(tipo, et, txt, autor)
    if n > s["caben"]:
        return f"etiqueta + dato = {n} caracteres y en la oración [{si}] caben {s['caben']}", "caben", None
    pal = str(fi.get("palabra") or "").strip()
    en = any(ev.norm(pal) == ev.norm(re.sub(r"[^\w]", "", w)) for w in palabras(s["texto"])) if pal else False
    return None, None, {"pool_id": pid, "sentence_idx": si, "palabra": pal, "palabra_en_oracion": en,
                        "etiqueta": et, "texto": txt, "estilo": estilo, **({"autor": autor} if tipo == "cita" else {}),
                        "aporta": str(fi.get("aporta") or ""), "oracion": s["texto"], "caracteres": n,
                        "caben": s["caben"]}


# ═══════════════════════ llamada (§C.2) ═══════════════════════

class TopePantalla(RuntimeError):
    """El tope de US$ no alcanza para otra llamada."""


class SinJSON(RuntimeError):
    """Dos respuestas sin JSON válido: PARADA (HANDOFF_F36_C_D, Frenos)."""


def primer_json(txt: str) -> dict | None:
    """El primer objeto JSON válido del texto (lo de antes o después se ignora); None si no hay."""
    dec = json.JSONDecoder()
    for m in re.finditer(r"\{", txt or ""):
        try:
            obj, _ = dec.raw_decode(txt, m.start())
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            return obj
    return None


def _reintento(user: str, errores: list[str]) -> str:
    return user + "\n\nTU RESPUESTA ANTERIOR TUVO ESTOS PROBLEMAS (corregilos y devolvé el JSON completo otra vez):\n" + \
        "\n".join(f"- {e}" for e in errores)


def llamar(ent: dict[str, Any], out_dir: Path, *, post: Callable[[dict], dict] | None = None,
           tope: float = TOPE_USD, log: list[str] | None = None) -> dict[str, Any]:
    """La llamada con caché, tope y un reintento. Devuelve {clave, intentos, final, validacion, usd, tokens_in}.
    `post` (tests) reemplaza al POST de la API: recibe el body y devuelve el mensaje {content, usage, stop_reason}."""
    import claude_helpers as hx
    log = log if log is not None else []
    user = pedido(ent)
    clave = hashlib.md5(f"{PROMPT_VERSION}|{MODELO}|{EFFORT}|{PANTALLA_SYSTEM}|{user}".encode("utf-8")).hexdigest()
    raw_f = Path(out_dir) / f"{ARCHIVO}.raw.json"
    try:
        prev = json.loads(raw_f.read_text(encoding="utf-8")) if raw_f.exists() else None
    except (OSError, ValueError):
        prev = None
    if prev and prev.get("clave") == clave and prev.get("final") is not None:
        prev["validacion"] = validar(prev["final"], ent)             # determinista: con el código de hoy
        log.append(f"  m01e: caché ({len(prev.get('intentos') or [])} intento(s), US$ 0)")
        return {**prev, "cache": True}
    out: dict[str, Any] = {"clave": clave, "modelo": MODELO, "effort": EFFORT, "prompt_version": PROMPT_VERSION,
                           "prompt_md5": prompt_md5(), "entrada_md5": entrada_md5(ent), "intentos": [], "final": None,
                           "validacion": None, "usd": 0.0}
    pin, pout = hx.PRICES.get(hx._base(MODELO), (0.0, 0.0))
    pedido_k = user
    for k in range(2):
        body = {"model": MODELO, "max_tokens": hx.MAX_TOKENS, "system": PANTALLA_SYSTEM,
                "messages": [{"role": "user", "content": pedido_k}], "output_config": {"effort": EFFORT}}
        peor = len(json.dumps(body, ensure_ascii=False)) / 2.5 / 1e6 * pin + OUT_TOKENS_PEOR / 1e6 * pout
        if out["usd"] + peor > tope:
            msg = (f"tope US$ {tope:.2f}: gastado {out['usd']:.4f} + esta llamada hasta {peor:.4f}")
            out["error"] = msg
            log.append(f"  m01e: {msg} → sin {'reintento' if k else 'llamada'}")
            if k == 0:
                raise TopePantalla(msg)
            break
        t0 = time.time()
        r = (post or hx._post)(body)
        u = r.get("usage") or {}
        usd = round(hx.cost_of(MODELO, u), 5)
        if post is None:
            hx._track(r.get("model") or MODELO, u, "m01e_pantalla")    # al cost_tracker (el ledger del paso)
        out["usd"] = round(out["usd"] + usd, 5)
        out["tokens_in"] = out.get("tokens_in") or u.get("input_tokens")
        txt = "".join(c.get("text") or "" for c in r.get("content") or [] if c.get("type") == "text")
        resp = primer_json(txt)
        val = validar(resp, ent) if resp is not None else None
        out["intentos"].append({"pedido": pedido_k if k else "(el USER de entrada)", "texto": txt, "respuesta": resp,
                                "usage": u, "stop": r.get("stop_reason"), "usd": usd,
                                "segundos": round(time.time() - t0, 1)})
        log.append(f"  m01e intento {k + 1}: in {u.get('input_tokens')} · out {u.get('output_tokens')} · US$ {usd:.4f} · "
                   f"{'JSON' if resp is not None else 'SIN JSON'}"
                   + (f" · fichas fuera {val['fichas_fuera']}" if val else ""))
        if resp is None:
            if k == 0:
                pedido_k = _reintento(user, [f"la respuesta no es JSON válido (stop_reason {r.get('stop_reason')})"])
                continue
            break
        out["final"], out["validacion"] = resp, val
        if k == 0 and val["fichas_fuera"] >= REINTENTO_FICHAS:
            pedido_k = _reintento(user, [f"{d.get('pool_id')} ({d.get('cap')} beat {d.get('beat')}) «{d.get('etiqueta')} · "
                                         f"{d.get('texto')}»: {d['regla']}: {d['motivo']}"
                                         for d in val["descartados"] if d.get("que") == "ficha"])
            continue
        break
    raw_f.parent.mkdir(parents=True, exist_ok=True)
    raw_f.write_text(json.dumps({**out, "entrada": _para_modelo(ent)}, ensure_ascii=False, indent=1), encoding="utf-8")
    if out["final"] is None:
        raise SinJSON(f"dos respuestas sin JSON válido; la cruda en {raw_f}")
    return out


# ═══════════════════════ salida ═══════════════════════

def armar(ent: dict[str, Any], res: dict[str, Any]) -> dict[str, Any]:
    v = res["validacion"]
    return {"topic_id": ent["topic_id"], "prompt_version": PROMPT_VERSION, "prompt_md5": prompt_md5(),
            "modelo": res["modelo"], "effort": res["effort"], "entrada_md5": res.get("entrada_md5"),
            "intentos": len(res.get("intentos") or []), "usd": res.get("usd", 0.0) if not res.get("cache") else 0.0,
            "tokens_in": res.get("tokens_in"), "caps": [{"cap": c["cap"], "titulo": c["titulo"],
                                                         "oraciones": [s["texto"] for s in c["oraciones"]]}
                                                        for c in ent["caps"]],
            "beats": v["beats"], "relojes": v["relojes"], "tarjeta": v["tarjeta"], "descartados": v["descartados"]}


def a_markdown(p: dict[str, Any]) -> str:
    """Una línea por beat (ficha · sello), los relojes y la tarjeta; después lo que cayó, con motivo."""
    lines = [f"# Guion de pantalla en papel — {p['topic_id']}", "",
             f"`m01e_pantalla` {p['prompt_version']} (md5 del prompt `{p['prompt_md5']}`) · {p['modelo']} {p['effort']} · "
             f"{p['intentos']} intento(s) · US$ {p['usd']:.4f} · tokens de entrada {p.get('tokens_in')}", "",
             f"**Tarjeta:** {p['tarjeta']['texto'] if p.get('tarjeta') else '—'}", ""]
    fichas = sum(1 for b in p["beats"] if b["ficha"])
    sellos = sum(1 for b in p["beats"] if b["sello"])
    lines += [f"Totales: {fichas} fichas · {sellos} sellos · {len(p['relojes'])} relojes · "
              f"{'1 tarjeta' if p.get('tarjeta') else 'sin tarjeta'} · {len(p['descartados'])} descartados", ""]
    for c in p["caps"]:
        lines += [f"## {c['cap']} — {c['titulo']}", ""]
        for b in [b for b in p["beats"] if b["cap"] == c["cap"]]:
            f, s = b["ficha"], b["sello"]
            fi = (f"ficha **{f['pool_id']}** [{f['estilo']}] «{f['etiqueta']} · {f['texto']}»"
                  + (f" — {f['autor']}" if f.get("autor") else "")
                  + f" en [{f['sentence_idx']}] sobre «{f['palabra']}»{'' if f['palabra_en_oracion'] else ' (no está en la oración)'}"
                  f" ({f['caracteres']}/{f['caben']} car.) · aporta: {f['aporta']}") if f else "ficha —"
            se = f"sello **{s['palabra']}** en [{s['sentence_idx']}]" if s else "sello —"
            lines.append(f"- beat {b['beat']} · {b['funcion']}{' · PICO' if b['pico'] else ''} · {fi} · {se}")
        rel = [r for r in p["relojes"] if r.get("cap") == c["cap"]]
        rel_txt = ", ".join(f"{r['fecha']} en [{r['sentence_idx']}]" for r in rel) or "—"
        lines.append(f"- relojes: {rel_txt}")
        lines.append("")
    lines += ["## Lo que cayó", ""]
    val = [d for d in p["descartados"] if d.get("quien") == "validación"]
    lines += [f"- {d.get('cap')} beat {d.get('beat')} · {d['que']} {d.get('pool_id') or ''} «"
              f"{(str(d.get('etiqueta')) + ' · ') if d.get('etiqueta') else ''}{d.get('texto')}» en "
              f"[{d.get('sentence_idx')}] → **{d['regla']}**: {d['motivo']}" for d in val] or ["- (nada)"]
    lines += ["", "## Descartados por el modelo", ""]
    lines += [f"- {d.get('pool_id')}: {d.get('motivo')}" for d in p["descartados"] if d.get("quien") == "modelo"] \
        or ["- (ninguno)"]
    return "\n".join(lines) + "\n"


def generar(topic_id: str, steps_dir: Path | None = None, *, pool: dict | None = None,
            post: Callable[[dict], dict] | None = None, vocabulario: list[str] | None = None,
            log: list[str] | None = None) -> dict[str, Any]:
    """El paso entero: entrada → llamada → validación → 01e_pantalla.json/.md en el directorio del topic."""
    from script_engine.clima import vocabulario_clima
    from script_engine.m01a_skeleton import STEPS_DIR
    log = log if log is not None else []
    carga = cargar(topic_id, Path(steps_dir or STEPS_DIR), pool)
    ent = entrada(carga, vocabulario if vocabulario is not None else vocabulario_clima())
    ent["_pool"] = carga["pool"]
    res = llamar(ent, carga["dir"], post=post, log=log)
    papel = armar(ent, res)
    (carga["dir"] / f"{ARCHIVO}.json").write_text(json.dumps(papel, ensure_ascii=False, indent=1), encoding="utf-8")
    (carga["dir"] / f"{ARCHIVO}.md").write_text(a_markdown(papel), encoding="utf-8")
    log.append(f"  m01e: {sum(1 for b in papel['beats'] if b['ficha'])} fichas · "
               f"{sum(1 for b in papel['beats'] if b['sello'])} sellos · {len(papel['relojes'])} relojes · "
               f"tarjeta {bool(papel['tarjeta'])} → {carga['dir'] / (ARCHIVO + '.md')}")
    return papel


def ruta(topic_id: str, steps_dir: Path | None = None) -> Path:
    from script_engine.m01a_skeleton import STEPS_DIR
    return Path(steps_dir or STEPS_DIR) / topic_id / f"{ARCHIVO}.json"


def cargar_papel(topic_id: str, steps_dir: Path | None = None) -> dict[str, Any] | None:
    """El papel del topic (lo lee Fase 2); None si no hay."""
    f = ruta(topic_id, steps_dir)
    try:
        return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None
    except (OSError, ValueError):
        return None


def editar(topic_id: str, ediciones: list[dict[str, Any]], steps_dir: Path | None = None) -> Path:
    """`fase2b --plan-edit` (§C.4): las ediciones a mano van al papel, no al plan. Cada una: {cap, beat, ficha: {pool_id,
    sentence_idx, palabra, etiqueta, texto, aporta} | null} y/o {cap, beat, sello: {palabra, sentence_idx} | null}, o
    {tarjeta: {texto} | null}; reemplazan lo del beat (null lo borra) y quedan marcadas `editado`. El estilo lo vuelve a
    poner el código. La primera vez se guarda una copia (01e_pantalla.antes_de_edicion.json); el .md se reescribe.
    Fase 2 vuelve a pasar lo editado por sus filtros como a todo."""
    from script_engine.rotulista_colocar import LECTURA_CPS, caracteres
    f = ruta(topic_id, steps_dir)
    p = json.loads(f.read_text(encoding="utf-8"))
    bak = f.with_name(f"{ARCHIVO}.antes_de_edicion.json")
    if not bak.exists():
        bak.write_text(json.dumps(p, ensure_ascii=False, indent=1), encoding="utf-8")
    oraciones = {c["cap"]: c["oraciones"] for c in p.get("caps") or []}
    for e in ediciones:
        if "tarjeta" in e:
            p["tarjeta"] = ({"texto": str(e["tarjeta"]["texto"]), "editado": True} if e["tarjeta"] else None)
            continue
        b = next((x for x in p["beats"] if x["cap"] == e.get("cap") and x["beat"] == _int(e.get("beat"))), None)
        if b is None:
            raise ValueError(f"edición: no hay beat {e.get('beat')} en {e.get('cap')}")
        if "ficha" in e:
            fi = e["ficha"]
            if fi:
                si = int(fi["sentence_idx"])
                s = oraciones[e["cap"]][si]
                estilo = estilo_de(fi["pool_id"], fi.get("etiqueta") or "")
                tipo = TIPO_DE_ESTILO[estilo]
                fi = {"aporta": "(edición a mano)", **fi, "sentence_idx": si, "estilo": estilo, "oracion": s, "editado": True,
                      "palabra_en_oracion": ev.norm(str(fi.get("palabra") or "")) in ev.norm(s),
                      "caracteres": caracteres(tipo, fi.get("etiqueta"), str(fi.get("texto") or ""), fi.get("autor") or ""),
                      "caben": int(len(palabras(s)) * SEG_POR_PALABRA * LECTURA_CPS)}
            b["ficha"] = fi
        if "sello" in e:
            se = e["sello"]
            b["sello"] = ({"palabra": str(se["palabra"]).upper(), "sentence_idx": int(se["sentence_idx"]),
                           "oracion": oraciones[e["cap"]][int(se["sentence_idx"])], "editado": True} if se else None)
    p.setdefault("ediciones", []).extend(ediciones)
    f.write_text(json.dumps(p, ensure_ascii=False, indent=1), encoding="utf-8")
    f.with_suffix(".md").write_text(a_markdown(p), encoding="utf-8")
    return f


def main(argv: list[str] | None = None) -> int:
    """Suelto (para un topic que ya tiene Fase 1, como Vajont): con el costo en 01_v3_costos.json (paso «pantalla»)."""
    from cost_tracker import cost_tracker
    from script_engine.m01a_skeleton import STEPS_DIR
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print("uso: python -m script_engine.m01e_pantalla <topic_id>")
        return 1
    topic_id = args[0]
    f = STEPS_DIR / topic_id / "01_v3_costos.json"
    costs = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    log: list[str] = []
    cost_tracker.start_video(topic_id)
    t0 = time.time()
    rc = 0
    try:
        generar(topic_id, log=log)
    except (SinJSON, TopePantalla) as e:
        log.append(f"  m01e: PARADA — {e}")
        rc = 2
    finally:
        r = cost_tracker.end_video()
        costs.setdefault("_corridas", []).append({"paso": "pantalla", "usd": round(getattr(r, "total_cost", 0.0) or 0.0, 4),
                                                  "segundos": round(time.time() - t0, 1)})
        f.write_text(json.dumps(costs, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n".join(log))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
