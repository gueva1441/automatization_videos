"""
script_engine/rotulista_filtros.py — F36 §A: todo lo que corta un bloque del rotulista (movido de gfx_rotulista).
`validar` corre por bloque los filtros de `ORDEN`, en ese orden, y el primero que devuelve un motivo lo saca con su
regla; al final `cantidad` (= `finalizar`) deja uno por beat. Además `contradicciones` (§A.4), `pide_documento` y
`lo_que_pide`.
"""
from __future__ import annotations

import re
from typing import Any

from script_engine import evidence as ev
from script_engine.rotulista_colocar import LECTURA_CPS, caben, caracteres, despues_del_corte, tiempos
from script_engine.voz_utils import (_PARTICULAS, _analiza, _fmt, _palabra_en, _raiz_en, beat_de_oracion, munon,
                                     nombre_inicial, nombres, numero_en, numeros, oraciones, palabras_de_contenido)

TIPOS = ("cifra", "hecho", "documento", "cita", "persona", "lupa")
FICHA = ("cifra", "hecho", "persona")              # §A.5: salen en la ficha (= title card)
CON_ETIQUETA = ("cifra", "hecho", "documento", "persona")


# ═══════════════════════ coherencia de cifras (§A.4) ═══════════════════════

LOCALES = ("nivel", "altura")             # F36 §B.5: una cota o una altura se compara solo con su vecindad
PALABRAS_LOCALES = ("cota", "nivel", "altura")


def _palabras_mag(texto: str) -> set[str]:
    """F36 §B.5: qué cota, nivel o altura nombra el texto (la palabra, no la magnitud: «cota» no es «nivel del mar»)."""
    return {w for t in re.findall(r"[^\W\d_]+", ev.norm(texto or "")) for w in PALABRAS_LOCALES if t.startswith(w)}


def contradicciones(bloque: str, voz: list[str], cerca: list[str] | None = None) -> list[str]:
    """§A.4: cada cifra del bloque con unidad contra las cifras de la voz de todo el video. Lectura declarada de «misma
    unidad o misma magnitud nombrada en la oración»: la cifra de la voz se compara si (1) tiene la misma unidad y la
    oración nombra la misma magnitud que el bloque («setecientos metros sobre el nivel del mar» contra «Nivel del
    embalse: 720 m»); o (2) no tiene unidad pero viene después de la magnitud del bloque en su oración («la cota
    autorizada fue de setecientos quince»). La misma unidad sola no alcanza («ola de veinte metros» no es la cota; la
    oferta de ENEL en liras no es la condena a Montedison), y una diferencia («15 metros por encima de la cota») no se
    compara con la cota. F36 §B.5: con `cerca` (la oración ancla y sus vecinas), una cota o una altura (magnitud nivel
    o altura) solo contradice a OTRA de la misma palabra (cota con cota, nivel con nivel, altura con altura) en esas
    oraciones: los niveles anteriores del relato no cuentan («COTA AUTORIZADA 715 m» contra «el embalse estaba a 650 m»
    de 1960 o «no pasar de los setecientos metros sobre el nivel del mar», la vecina). Lectura declarada (F36_REPORT).
    Los muertos se siguen comparando con todo el video."""
    nb, mb = _analiza(bloque)
    mags_b = {m for m, _ in mb}
    out = []
    fuentes = [(s, None) for s in voz] if cerca is None else [(s, False) for s in voz] + [(s, True) for s in cerca]
    for v, u, _ in nb:
        if u is None or u == "diferencia":
            continue
        for s, local in fuentes:
            ns, ms = _analiza(s)
            mags_s = {m for m, _ in ms}
            for w, uw, p in ns:
                comunes = ((mags_b & mags_s) if uw == u else set()) | \
                          ({m for m, q in ms if m in mags_b and q < p} if uw is None else set())
                if local is not None and comunes and (comunes <= set(LOCALES)) != local:
                    continue                       # la cota contra la vecindad; lo demás contra todo el video
                if local and not (_palabras_mag(bloque) & _palabras_mag(s)):
                    continue
                if comunes and abs(w - v) > 1e-9:
                    out.append(f"{_fmt(v)} {u} vs {_fmt(w)}{' ' + uw if uw else ''} («{s.strip()[:70]}»)")
    return list(dict.fromkeys(out))


_DOC = re.compile(r"\b(carta|acta|informe|documento)s?\b")


def pide_documento(por_que: str) -> bool:
    """F32 §B.4: el `por_que` de un `a_pantalla` dice carta, acta, informe o documento → sale como recorte."""
    return bool(_DOC.search(ev.norm(por_que or "")))


# ═══════════════════════ validar: los filtros, en orden ═══════════════════════
# F36 §A: cada filtro de bloque recibe (bloque, ent, ctx) y devuelve el motivo si el bloque sale (None si pasa); sale
# con la regla del filtro (`regla`: el nombre de la función; `gancho_dicho` sale como no_dicho, que es lo que era). ctx
# es del bloque: lo que un filtro deja (ítem, oración, tipo, texto, tiempos) lo leen los que siguen; `forma` normaliza
# el bloque (tipo, texto, etiqueta). El orden es el de F34: el primero que corta se queda con el bloque.

def anclaje(b: dict[str, Any], ent: dict[str, Any], ctx: dict[str, Any]) -> str | None:
    """Oración y palabra que existen, en un beat del ítem."""
    pid = str(b.get("pool_id") or "")
    x = ctx["its"].get(pid)
    ctx["pid"], ctx["x"] = pid, x
    if x is None:
        return f"pool_id {pid!r} no está en los datos del cap"
    sents = ctx["sents"]
    try:
        si = int(b.get("sentence_idx"))
    except (TypeError, ValueError):
        si = -1
    if not 0 <= si < len(sents):
        return f"sentence_idx {b.get('sentence_idx')!r} no existe"
    s = sents[si]
    try:
        wi = int(b.get("word_idx"))
    except (TypeError, ValueError):
        wi = -1
    if not 0 <= wi < len(s["palabras"]):
        return f"word_idx {b.get('word_idx')!r} no existe en la oración [{si}]"
    if s["beat"] not in x["beats"]:
        return f"la oración [{si}] es del beat {s['beat']} y {pid} es del beat {x['beats']}"
    ctx.update(si=si, s=s, wi=wi)
    return None


def gancho_dicho(b: dict[str, Any], ent: dict[str, Any], ctx: dict[str, Any]) -> str | None:
    """F34 §A.1: del pool del video, pero la voz lo dice."""
    x = ctx["x"]
    if x.get("gancho") and x.get("dice_voz"):
        return f"{ctx['pid']} es del pool del video y la narración lo dice en algún cap (gancho)"
    return None


gancho_dicho.regla = "no_dicho"          # type: ignore[attr-defined]


def forma(b: dict[str, Any], ent: dict[str, Any], ctx: dict[str, Any]) -> str | None:
    """Tipo, etiqueta, valor, muñón, `aporta` y que quepa en la ficha; normaliza tipo, texto y etiqueta del bloque."""
    x, pid = ctx["x"], ctx["pid"]
    tipo = str(b.get("tipo") or "").strip().lower()
    if tipo not in TIPOS:
        return f"tipo {tipo!r} no válido"
    forzado = None
    if x["a_pantalla"] and tipo != "documento" and pide_documento(x["por_que"]):   # F32 §B.4
        forzado = f"{tipo} → documento (el por_que de {pid} pide un documento)"
        tipo = "documento"
    b["tipo"] = tipo
    txt = re.sub(r"\s+", " ", str(b.get("texto") or "")).strip()
    if tipo == "cita" or forzado:
        txt = re.sub(r"^[«\"“]+|[»\"”]+$", "", txt).strip()
    et = re.sub(r"\s+", " ", str(b.get("etiqueta") or "")).strip() or None
    if forzado and not et:             # el recorte lleva el nombre real de su fuente (literal: pasa el candado)
        from script_engine.gfx_pool import short_source
        et = short_source(x["fuente"]) or None
    b["texto"], b["etiqueta"] = txt, et
    ctx.update(tipo=tipo, txt=txt, et=et, forzado=forzado)
    if not txt:
        return "texto vacío"
    if tipo in CON_ETIQUETA and not et:
        return f"{tipo} sin etiqueta" + (" (y su fuente no da nombre)" if forzado else "")
    if tipo == "cifra" and not numeros(txt):
        return "cifra sin el valor"
    if tipo != "lupa" and munon(txt):
        return "fragmento cortado (empieza en minúscula o termina en preposición/artículo)"
    if not str(b.get("aporta") or "").strip():
        return "sin `aporta`"
    if tipo in FICHA:
        from script_engine.gfx_project import ficha_medida
        m = ficha_medida(et or "", txt)
        if m["kicker"] > 1 or m["title"] > 2:
            return f"no cabe en la ficha: etiqueta en {m['kicker']} línea(s), dato en {m['title']} (1 y 2)"
    return None


def candado(b: dict[str, Any], ent: dict[str, Any], ctx: dict[str, Any]) -> str | None:
    """F29b A.4.3: cita = subcadena del texto fuente; resto = cada número, nombre propio y año en el texto fuente."""
    x, pid, tipo, txt, et = ctx["x"], ctx["pid"], ctx["tipo"], ctx["txt"], ctx["et"]
    fuente = x["texto"]
    if tipo == "cita":
        if ev.norm(txt.strip("…").strip()) not in ev.norm(fuente):
            return "la cita no es literal del texto fuente"
        return None
    ancla = ctx["s"]["texto"]
    if x.get("gancho"):                # F36 §B.7: para el gancho (pool del video), lo que la voz dice en cualquier cap
        ancla = " ".join(ctx["voz_video"])

    def en_ancla(n: str) -> bool:      # F34 §A.2.1: lo que la voz dice en la oración ancla cuenta como presente
        return numero_en(n, ancla) if numeros(n) else _palabra_en(n, ancla)
    malos = [n for n in numeros(txt) if not numero_en(n, fuente)]
    malos += [n for n in nombres(txt) if not _palabra_en(n, fuente)]
    if tipo == "persona":              # el nombre (abre el texto: nombres() no lo mira) y el cargo (etiqueta)
        malos += [n for n in nombre_inicial(txt) if n.lower() not in _PARTICULAS and not _palabra_en(n, fuente)]
    elif et:                           # la etiqueta sale del texto o de la fuente del dato
        ff = fuente + " " + x["fuente"]
        malos += [n for n in numeros(et) + nombres(et) if not (numero_en(n, ff) or _palabra_en(n, ff))]
    malos = [n for n in malos if not en_ancla(n)]
    if tipo == "persona":              # el cargo (palabras, no nombres): solo del texto fuente
        malos += [w for w in palabras_de_contenido(et or "") if not _raiz_en(w, fuente)]
    if malos:
        return f"no están en el texto fuente de {pid}: {sorted(set(malos))}"
    return None


def no_dicho(b: dict[str, Any], ent: dict[str, Any], ctx: dict[str, Any]) -> str | None:
    """§A.3 no dicho (oración ancla ± 1), sobre el dato. F34 §A.2.2: antes que la lectura (D237 «cuatrocientos» caía
    por lectura y no por repetir la voz); los números en letras de la voz se comparan por valor (numeros/numero_en, con
    el conversor de num_es)."""
    sents, si, x, txt = ctx["sents"], ctx["si"], ctx["x"], ctx["txt"]
    vecinas = " ".join(ss["texto"] for ss in sents[max(0, si - 1):si + 2])
    nums = numeros(txt)
    exento = nombre_inicial(txt) if ctx["tipo"] == "persona" else set()     # el nombre de la persona (lo dice la voz)
    nms = [n for n in nombres(txt) if n not in exento]
    ctx.update(nums=nums, nms=nms)
    dichos = [n for n in nums if numero_en(n, vecinas)] + [n for n in nms if _palabra_en(n, vecinas)]
    if x.get("gancho"):                    # §A.1: el dato del gancho no lo dice la voz en todo el video
        dichos += [n for n in nums if n not in dichos and numero_en(n, " ".join(ctx["voz_video"]))]
    if dichos:
        return f"la voz lo dice en la oración ancla o en una vecina: {dichos}"
    return None


def spoiler(b: dict[str, Any], ent: dict[str, Any], ctx: dict[str, Any]) -> str | None:
    """§A.3 spoiler (oraciones posteriores del cap). §A.2.3: un nombre que la voz ya dijo antes en el cap o en un cap
    anterior no es spoiler."""
    sents, si = ctx["sents"], ctx["si"]
    despues = " ".join(ss["texto"] for ss in sents[si + 1:])
    antes = " ".join(ss["texto"] for ss in sents[:si + 1]) + " " + str(ent.get("voz_antes") or "")
    spoil = [n for n in ctx["nums"] if numero_en(n, despues)] + \
            [n for n in ctx["nms"] if _palabra_en(n, despues) and not _palabra_en(n, antes)]
    if spoil:
        return f"la voz lo dice en una oración posterior del cap: {spoil}"
    return None


def lectura(b: dict[str, Any], ent: dict[str, Any], ctx: dict[str, Any]) -> str | None:
    """§A.2 tiempos: t0 = la palabra `word_idx`; t1 = fin de la oración (o de la siguiente) sin pasar el corte; si no
    cabe antes del corte, arranca en la escena siguiente (F32 §B.3); si tampoco, no va."""
    sents, si, escenas = ctx["sents"], ctx["si"], ctx["escenas"]
    t0 = ctx["s"]["palabras"][ctx["wi"]]["t0"]
    chars = caracteres(ctx["tipo"], ctx["et"], ctx["txt"], ctx["x"]["autor"])
    t1, sin_t = tiempos(sents, si, t0, chars, escenas)
    movido_corte = None
    if sin_t and escenas:              # F32 §B.3: si no cabe antes del corte, arranca en la escena siguiente
        otro = despues_del_corte(sents, si, t0, chars, escenas)
        if otro is not None:
            t0, t1, movido_corte = otro
            sin_t = None
    cab = ctx["sents"][si].get("caben")
    ctx.update(t0=t0, t1=t1, chars=chars, movido_corte=movido_corte,
               max_chars=cab if cab is not None else caben(sents, si, escenas))      # F36 §B.8
    return sin_t


def coherencia(b: dict[str, Any], ent: dict[str, Any], ctx: dict[str, Any]) -> str | None:
    """§A.4 coherencia con la voz de todo el video."""
    si, sents = ctx["si"], ctx["sents"]
    contra = contradicciones(f"{ctx['et'] or ''} {ctx['txt']}", ctx["voz_video"],
                             cerca=[ss["texto"] for ss in sents[max(0, si - 1):si + 2]])     # F36 §B.5
    return ("contradice la voz: " + "; ".join(contra[:3])) if contra else None


A_PANTALLA_POR_BEAT = 2       # §0 (voto del analista, aplicado): 2 `a_pantalla` en un beat si van en escenas distintas


def finalizar(validos: list[dict[str, Any]], pico_beat: Any) -> tuple[list[dict], list[dict]]:
    """§A.1: por beat queda 1 (`a_pantalla` primero, después `rank`, F36 §B.6 después el dato con cifra o fecha —en
    dígitos o en letras, `numeros` del dato—, después la oración); el mismo dato una sola vez.
    F32 §B.5 (§0): un beat puede tener 2 si los dos son `a_pantalla` (las escenas distintas las pone escena_final: la
    segunda ficha espera a otra escena del beat o no va); en el beat pico solo `a_pantalla`, salvo que el pico sea el
    gancho (DECISIONES 14:28: «el gancho no es pico a efectos del texto», F36 §B.7). Devuelve (los que quedan,
    en orden de t0; los que salen por cantidad)."""
    keep, rech, vistos, por_beat = [], [], set(), {}
    for b in sorted(validos, key=lambda b: (not b["a_pantalla"], b["rank"], not numeros(b["pantalla"]),
                                            b["sentence_idx"])):        # F36 §B.6: con cifra o fecha antes
        ya = por_beat.get(b["beat"]) or []
        dos = b["a_pantalla"] and len(ya) < A_PANTALLA_POR_BEAT and all(k["a_pantalla"] for k in ya)
        motivo = ("el mismo dato dos veces" if b["pool_id"] in vistos else
                  f"beat pico ({b['beat']}): solo `a_pantalla`" if pico_beat is not None and b["beat"] == pico_beat
                  and not b["a_pantalla"] and b.get("funcion") != "gancho" else
                  f"un texto por beat: el beat {b['beat']} ya tiene {', '.join(k['pool_id'] for k in ya)}" if ya and not dos
                  else None)
        if motivo:
            rech.append({"pool_id": b["pool_id"], "tipo": b["tipo"], "etiqueta": b["etiqueta"], "texto": b["pantalla"],
                         "sentence_idx": b["sentence_idx"], "regla": "cantidad", "motivo": motivo})
            continue
        keep.append(b)
        vistos.add(b["pool_id"])
        por_beat.setdefault(b["beat"], []).append(b)
    return sorted(keep, key=lambda b: b["t0"]), rech


cantidad = finalizar                     # sobre el lote de los que pasaron, no por bloque
cantidad.regla = "cantidad"              # type: ignore[attr-defined]
cantidad.lote = True                     # type: ignore[attr-defined]

ORDEN = [anclaje, gancho_dicho, forma, candado, no_dicho, spoiler, lectura, coherencia, cantidad]


def regla(f: Any) -> str:
    """La regla con que sale un bloque cortado por el filtro `f`."""
    return getattr(f, "regla", f.__name__)


def validar(resp: Any, ent: dict[str, Any], words: list[dict], time_offset: float = 0.0,
            escenas: list[Any] | None = None) -> dict[str, Any]:
    """{bloques, rechazos, faltan, motivo_faltan, incompletos}: los bloques que pasan los filtros de `ORDEN` y la
    cantidad por beat (con t0, t1, dur, beat, pantalla), cada uno que sale con su regla y su motivo, y los `a_pantalla`
    que no salieron. Sin `escenas` (prefetch) el fin no se corta en la escena: eso lo hace `colocar`."""
    its = {x["id"]: x for x in ent["items"]}
    sents = oraciones(words, time_offset)
    beats = ent["beats"]
    for s in sents:
        s["beat"] = beat_de_oracion(s, beats)
    funcion = {b["n"]: b["funcion"] for b in beats}
    pk_beat = (ent.get("pico") or {}).get("beat")
    voz_video = ent.get("voz_video") or [s["texto"] for s in sents]
    ok, rech = [], []

    def fuera(b: dict, regla: str, motivo: str) -> None:
        rech.append({"pool_id": b.get("pool_id"), "tipo": b.get("tipo"), "etiqueta": b.get("etiqueta"),
                     "texto": b.get("texto"), "sentence_idx": b.get("sentence_idx"), "regla": regla, "motivo": motivo})
    por_bloque = [f for f in ORDEN if not getattr(f, "lote", False)]
    bl = (resp or {}).get("bloques") if isinstance(resp, dict) else None
    for b in bl if isinstance(bl, list) else []:
        if not isinstance(b, dict):
            continue
        b = dict(b)
        ctx: dict[str, Any] = {"its": its, "sents": sents, "voz_video": voz_video, "escenas": escenas}
        for f in por_bloque:
            motivo = f(b, ent, ctx)
            if motivo:
                fuera(b, regla(f), motivo)
                break
        else:
            try:
                rank = int(b.get("rank"))
            except (TypeError, ValueError):
                rank = len(bl) + 1                     # sin rank: después de todos los que lo traen
            si, wi, s, t0, t1 = ctx["si"], ctx["wi"], ctx["s"], ctx["t0"], ctx["t1"]
            x, txt, et, chars = ctx["x"], ctx["txt"], ctx["et"], ctx["chars"]
            ok.append({**b, "sentence_idx": si, "word_idx": wi, "palabra": s["palabras"][wi]["w"], "t0": t0, "t1": t1,
                       "dur": round(t1 - t0, 3), "beat": s["beat"], "funcion": funcion.get(s["beat"], ""), "rank": rank,
                       "pantalla": txt, "etiqueta": et, "a_pantalla": x["a_pantalla"], "por_que": x["por_que"],
                       "caracteres": chars, "lectura_s": round(chars / LECTURA_CPS, 2),
                       "movido": None,                 # F32 §B.5: un `a_pantalla` puede ir en el beat pico (ya no se mueve)
                       "movido_corte": ctx["movido_corte"], "forzado": ctx["forzado"], "max_chars": ctx["max_chars"]})
    keep, rech_c = cantidad(ok, pk_beat)
    rech += rech_c
    salen = {b["pool_id"]: b for b in keep}
    faltan = [x["id"] for x in ent["items"] if x["a_pantalla"] and x["id"] not in salen]
    motivo_faltan = {}
    for i in faltan:
        r = [f"{r['regla']}: {r['motivo']}" for r in rech if r["pool_id"] == i]
        motivo_faltan[i] = r[-1] if r else "el rotulista no lo propuso"
    incompletos = {}
    for x in ent["items"]:
        if x["a_pantalla"] and x["id"] in salen:
            b = salen[x["id"]]
            falta = lo_que_pide(x["por_que"], x["texto"], f"{b['etiqueta'] or ''} {b['pantalla']}")
            if falta:
                incompletos[x["id"]] = falta
    return {"bloques": keep, "rechazos": rech, "faltan": faltan, "motivo_faltan": motivo_faltan,
            "incompletos": incompletos}


def lo_que_pide(por_que: str, fuente: str, pantalla: str) -> str | None:
    """Lo que el `por_que` de un `a_pantalla` pide y el bloque no trae (None si cumple): si el `por_que` nombra cifras,
    esas cifras; si pide «la cifra» (o «cifra de …»), al menos una cifra del texto fuente. El resto (que Q50 salga
    «como carta del municipio») no se puede medir con reglas: lo cuenta la hoja."""
    sin_anios = re.sub(r"\b(1[5-9]\d\d|20\d\d)\b(?=\s*[:.,;)]|\s*$)", " ", por_que or "")   # «… de 1943:» es contexto
    pide = numeros(sin_anios)
    if pide:
        faltan = [n for n in pide if not numero_en(n, pantalla)]
        return f"las cifras del por_que {faltan}" if faltan else None
    if re.search(r"\bcifra", ev.norm(por_que)):
        tiene = [n for n in numeros(pantalla) if numero_en(n, fuente)]
        return None if tiene else "la cifra que pide el por_que"
    return None
