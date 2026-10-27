"""
script_engine/pantalla_filtros.py — F36 §A: todo lo que corta un texto de pantalla (movido de pantalla_entrada; F37 §B.5:
antes pantalla_filtros). F36 §C:
los textos vienen del guion en papel (m01e_pantalla); `validar_papel` corre por bloque los filtros de `ORDEN`, en ese
orden, y el primero que devuelve un motivo lo saca con su regla. F36 §D: se borraron el anclaje y la forma del modelo,
la coherencia (filtro) y la cantidad por beat. Además `contradicciones` (§A.4: la usa el chequeo del guion) y
`pide_documento` (el estilo «papel» del guion en papel).
"""
from __future__ import annotations

import re
from typing import Any

from script_engine import evidence as ev
from script_engine.pantalla_colocar import LECTURA_CPS, caben, caracteres, instantes, tiempos
from script_engine.voz_utils import (_PARTICULAS, _analiza, _fmt, _palabra_en, _raiz_en, beat_de_oracion,
                                     nombre_inicial, nombres, numero_en, numeros, oraciones, palabras_de_contenido)

FICHA = ("cifra", "hecho", "persona")              # §A.5: salen en la ficha (= title card)


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


def gancho_dicho(b: dict[str, Any], ent: dict[str, Any], ctx: dict[str, Any]) -> str | None:
    """F34 §A.1: del pool del video, pero la voz lo dice."""
    x = ctx["x"]
    if x.get("gancho") and x.get("dice_voz"):
        return f"{ctx['pid']} es del pool del video y la narración lo dice en algún cap (gancho)"
    return None


gancho_dicho.regla = "no_dicho"          # type: ignore[attr-defined]


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


def _sin_juicio(ctx: dict[str, Any], regla_: str, toks: list[str]) -> list[str]:
    """F37 §A.4: las coincidencias que el autor ya juzgó «otro hecho» en el reintento del papel (`juicio_autor` de la
    ficha) no vuelven a cortar, ni en papel ni en Fase 2."""
    ya = {str(t) for t in ((ctx.get("juicio") or {}).get(regla_) or [])}
    return [t for t in toks if str(t) not in ya]


def no_dicho(b: dict[str, Any], ent: dict[str, Any], ctx: dict[str, Any]) -> str | None:
    """§A.3 no dicho (oración ancla ± 1), sobre el dato. F34 §A.2.2: antes que la lectura (D237 «cuatrocientos» caía
    por lectura y no por repetir la voz); los números en letras de la voz se comparan por valor (numeros/numero_en, con
    el conversor de num_es). F37 §A.4: las coincidencias quedan en ctx["dichos"] (el papel se las pregunta al autor) y
    las que el autor juzgó otro hecho no cuentan."""
    sents, si, x, txt = ctx["sents"], ctx["si"], ctx["x"], ctx["txt"]
    vecinas = " ".join(ss["texto"] for ss in sents[max(0, si - 1):si + 2])
    nums = numeros(txt)
    exento = nombre_inicial(txt) if ctx["tipo"] == "persona" else set()     # el nombre de la persona (lo dice la voz)
    nms = [n for n in nombres(txt) if n not in exento]
    ctx.update(nums=nums, nms=nms)
    dichos = [n for n in nums if numero_en(n, vecinas)] + [n for n in nms if _palabra_en(n, vecinas)]
    if x.get("gancho"):                    # §A.1: el dato del gancho no lo dice la voz en todo el video
        dichos += [n for n in nums if n not in dichos and numero_en(n, " ".join(ctx["voz_video"]))]
    dichos = _sin_juicio(ctx, "no_dicho", dichos)
    ctx["dichos"] = dichos
    if dichos:
        return f"la voz lo dice en la oración ancla o en una vecina: {dichos}"
    return None


def spoiler(b: dict[str, Any], ent: dict[str, Any], ctx: dict[str, Any]) -> str | None:
    """§A.3 spoiler (oraciones posteriores del cap). §A.2.3: un nombre que la voz ya dijo antes en el cap o en un cap
    anterior no es spoiler. F37 §A.4: las coincidencias quedan en ctx["spoil"] y las que el autor juzgó otro hecho no
    cuentan."""
    sents, si = ctx["sents"], ctx["si"]
    despues = " ".join(ss["texto"] for ss in sents[si + 1:])
    antes = " ".join(ss["texto"] for ss in sents[:si + 1]) + " " + str(ent.get("voz_antes") or "")
    spoil = [n for n in ctx["nums"] if numero_en(n, despues)] + \
            [n for n in ctx["nms"] if _palabra_en(n, despues) and not _palabra_en(n, antes)]
    spoil = _sin_juicio(ctx, "spoiler", spoil)
    ctx["spoil"] = spoil
    if spoil:
        return f"la voz lo dice en una oración posterior del cap: {spoil}"
    return None


def lectura(b: dict[str, Any], ent: dict[str, Any], ctx: dict[str, Any]) -> str | None:
    """F37 §B.1/§B.2: dónde se puede leer el bloque. Prueba los instantes de pantalla_colocar.instantes, en orden (1 la
    palabra ancla, la de más peso —ent["peso"]—, el inicio de la oración; 2 el inicio de la escena siguiente dentro de
    la oración; 3 la oración siguiente del beat): en cada uno la duración de la ficha (lectura acotada entre
    callout_dur_min y callout_dur_max) sin pasar el corte; uno en otra oración vuelve a pasar candado, no dicho y
    spoiler con esa oración. Sale solo si no entra en ninguno («papel sin colocar», con cada intento y por qué falló);
    si no, deja `intentos` (los que entran, en orden: el reparto prueba esos con «nunca al mismo tiempo» y el crítico)
    y t0/t1 = el primero."""
    sents, si, escenas = ctx["sents"], ctx["si"], ctx["escenas"]
    chars = caracteres(ctx["tipo"], ctx["et"], ctx["txt"], ctx["x"]["autor"])
    ancla = ctx["s"]["palabras"][ctx["wi"]]["t0"]
    entran: list[dict[str, Any]] = []
    fallas: list[str] = []
    antes = 0                          # cuántos intentos fallaron antes del primero que entra
    for t, k, como in instantes(sents, si, escenas, ancla=ancla, peso=(ent.get("peso") or {}).get(si)):
        t1, sin_t = tiempos(t, chars, escenas)
        if sin_t:
            fallas.append(f"{como} ({t:.2f} s): {sin_t}")
            antes += 0 if entran else 1
            continue
        if k != si:                    # otra oración: los filtros de contenido con esa oración
            c2 = {**ctx, "si": k, "s": sents[k]}
            mot = next((f"{regla(f)}: {m}" for f in (candado, no_dicho, spoiler) for m in [f(b, ent, c2)] if m), None)
            if mot:
                fallas.append(f"{como} ({t:.2f} s): {mot}")
                antes += 0 if entran else 1
                continue
        entran.append({"t0": round(t, 3), "t1": t1, "si": k, "como": como})
    cab = sents[si].get("caben")
    ctx.update(chars=chars, max_chars=cab if cab is not None else caben(sents, si, escenas), intentos=entran,
               intentos_fallidos=fallas)
    if not entran:
        return "no entra en ningún intento: " + " · ".join(fallas)
    ctx.update(t0=entran[0]["t0"], t1=entran[0]["t1"], si_final=entran[0]["si"],
               movido_corte=(f"{ancla:.2f} → {entran[0]['t0']:.2f} s ({entran[0]['como']}): " + " · ".join(fallas[:antes]))
               if antes else None)
    return None


def ancla_papel(b: dict[str, Any], ent: dict[str, Any], ctx: dict[str, Any]) -> str | None:
    """F36 §C.4: el bloque viene del guion en papel (m01e_pantalla), ya anclado a la oración de la voz por texto
    (pantalla_entrada.del_papel) y a su palabra; acá solo se arma lo que leen los filtros que siguen (ítem, oración,
    palabra, tipo por estilo, texto, etiqueta). El anclaje y la forma del modelo quedan en papel (§C.3); sale solo si
    el ítem no está en el pool."""
    pid = str(b.get("pool_id") or "")
    x = ctx["its"].get(pid)
    if x is None:
        return f"pool_id {pid!r} no está en el pool del video"
    si, wi = int(b["sentence_idx"]), int(b["word_idx"])
    tipo = str(b.get("tipo") or "hecho")
    txt = re.sub(r"\s+", " ", str(b.get("texto") or "")).strip()
    if tipo == "cita":
        txt = re.sub(r"^[«\"“]+|[»\"”]+$", "", txt).strip()
    et = re.sub(r"\s+", " ", str(b.get("etiqueta") or "")).strip() or None
    b["texto"], b["etiqueta"] = txt, et
    ctx.update(pid=pid, x=x, si=si, s=ctx["sents"][si], wi=wi, tipo=tipo, txt=txt, et=et, forzado=None,
               juicio=b.get("juicio_autor") or {})                    # F37 §A.4: lo que el autor ya juzgó
    return None


ancla_papel.regla = "anclaje"            # type: ignore[attr-defined]

# F36 §C.4 (aclaración 3): Fase 2 re-chequea lo mecánico con los datos reales (candado, no dicho, spoiler, lectura
# hasta el corte); «nunca al mismo tiempo», el crítico de foto y «ya mostrado» corren después (colocar, escena_final).
# No se re-aplican: cantidad (uno por beat), «pico solo a_pantalla» ni el desempate (los decidió el papel), ni la
# forma y el anclaje del modelo (quedan en papel, §C.3), ni la coherencia (no está en la lista de la aclaración 3).
ORDEN = [ancla_papel, gancho_dicho, candado, no_dicho, spoiler, lectura]


def regla(f: Any) -> str:
    """La regla con que sale un bloque cortado por el filtro `f`."""
    return getattr(f, "regla", f.__name__)


def validar_papel(bloques: list[dict[str, Any]], ent: dict[str, Any], words: list[dict], time_offset: float = 0.0,
                  escenas: list[Any] | None = None) -> dict[str, Any]:
    """F36 §C.4: los bloques del guion en papel (pantalla_entrada.preparar_cap) por los filtros de `ORDEN`, en ese orden: el
    primero que devuelve un motivo saca el bloque con su regla. {bloques (con t0, t1, dur, beat, pantalla), rechazos,
    faltan, motivo_faltan (los `a_pantalla` del papel que no salieron)}. Sin `escenas` el fin no se corta en la escena."""
    its = {x["id"]: x for x in ent["items"]}
    sents = oraciones(words, time_offset)
    beats = ent["beats"]
    for s in sents:
        s["beat"] = beat_de_oracion(s, beats)
    funcion = {b["n"]: b["funcion"] for b in beats}
    voz_video = ent.get("voz_video") or [s["texto"] for s in sents]
    ok, rech = [], []
    for b in bloques:
        b = dict(b)
        ctx: dict[str, Any] = {"its": its, "sents": sents, "voz_video": voz_video, "escenas": escenas}
        for f in ORDEN:
            motivo = f(b, ent, ctx)
            if motivo:
                rech.append({"pool_id": b.get("pool_id"), "tipo": b.get("tipo"), "etiqueta": b.get("etiqueta"),
                             "texto": b.get("texto"), "sentence_idx": b.get("sentence_idx"), "regla": regla(f),
                             "motivo": motivo})
                break
        else:
            si, wi, s, t0, t1 = ctx["si_final"], ctx["wi"], ctx["s"], ctx["t0"], ctx["t1"]
            x, txt, et, chars = ctx["x"], ctx["txt"], ctx["et"], ctx["chars"]
            ok.append({**b, "sentence_idx": si, "word_idx": wi, "palabra": s["palabras"][wi]["w"], "t0": t0, "t1": t1,
                       "dur": round(t1 - t0, 3), "beat": s["beat"], "funcion": funcion.get(s["beat"], ""),
                       "intentos": ctx["intentos"], "intentos_fallidos": ctx["intentos_fallidos"],
                       "pantalla": txt, "etiqueta": et, "a_pantalla": x["a_pantalla"], "por_que": x["por_que"],
                       "caracteres": chars, "lectura_s": round(chars / LECTURA_CPS, 2), "movido": None,
                       "movido_corte": ctx["movido_corte"], "forzado": ctx["forzado"], "max_chars": ctx["max_chars"]})
    keep = sorted(ok, key=lambda b: b["t0"])
    salen = {b["pool_id"] for b in keep}
    faltan = [x["id"] for x in ent["items"] if x["a_pantalla"] and x["id"] not in salen]
    motivo_faltan = {}
    for i in faltan:
        r = [f"{r['regla']}: {r['motivo']}" for r in rech if r["pool_id"] == i]
        motivo_faltan[i] = r[-1] if r else "el rotulista no lo propuso"
    return {"bloques": keep, "rechazos": rech, "faltan": faltan, "motivo_faltan": motivo_faltan}


