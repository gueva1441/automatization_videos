"""
script_engine/rotulista_llm.py — F36 §A: el pedido al modelo del rotulista (movido de gfx_rotulista sin cambios): el
prompt literal (`ROTULISTA_SYSTEM`/`ROTULISTA_USER`, `PROMPT_VERSION`, los de F29c/F32 para la historia), la entrada
de un cap (`entrada`: oraciones, beats, ítems del cap y del gancho, lo ya mostrado, el pico), el texto del pedido
(`prompt_user`) y la llamada (`llamar`: caché por pedido, ledger de costos, tope con las llamadas en vuelo, reintento).
"""
from __future__ import annotations

import hashlib
import json
import re
import threading
import time
from pathlib import Path
from typing import Any, Callable

from script_engine import evidence as ev
from script_engine.rotulista_colocar import caracteres
from script_engine.rotulista_filtros import validar
from script_engine.voz_datos import pico_cap
from script_engine.voz_utils import beat_de_oracion, numero_en, oraciones, palabras

PROMPT_VERSION = "f34-1"
MODELO_DEFAULT = "claude-sonnet-5-5"
EFFORT_DEFAULT = "medium"
OUT_TOKENS_PEOR = 16_000       # peor caso de salida para el tope (razonamiento + JSON)
REGLAS_REINTENTO = ("anclaje", "forma", "candado", "no_dicho", "spoiler", "coherencia")


# ═══════════════════════ prompt (HANDOFF_F29c §A.5, literal) ═══════════════════════

ROTULISTA_SYSTEM = """Sos el rotulista de un documental de historia oscura en español. Recibís la narración de un capítulo, oración por oración, con tiempos y con la palabra numerada, y una lista de datos verificados (citas, cifras, hechos, documentos) con su texto fuente. Decidís qué va escrito en pantalla, en qué palabra de qué oración aparece, de qué tipo es y con qué palabras.

Un texto en pantalla vale solo si cumple las tres a la vez:
(a) dice algo que la narración NO dice en este capítulo;
(b) es sobre lo que la narración cuenta en esa oración exacta;
(c) no adelanta nada que la narración diga después.
Si para una oración no hay ningún dato que cumpla las tres, no va nada. La pantalla vacía es correcta. Nunca repitas ni parafrasees la oración ancla ni la anterior ni la siguiente.

Cada capítulo está dividido en beats. En cada beat puede ir como máximo UN texto (dos si son dos datos marcados a_pantalla y van en oraciones distintas); en el beat marcado como pico solo van los datos a_pantalla; en el gancho va a lo sumo uno, y para el gancho podés usar cualquier dato de la lista que la narración no diga en todo el video, aunque no sea de su beat: el gancho tiene que prometer algo. Proponé por beat los candidatos que cumplan (a)(b)(c) y ordenalos con `rank` (1 = el que más aporta); los datos marcados `a_pantalla` van siempre con rank 1 en su beat y con lo que pide su `por_que`. El código se queda con uno por beat.

Tipos y su compuerta (solo cuando la narración, en esa oración, habla de eso):
- cifra: la narración habla de esa magnitud. Lleva etiqueta obligatoria (qué es la cifra) y el valor. No uses una cifra que contradiga otra cifra que la narración diga en cualquier parte del video.
  devolvé `unidad` (metros, personas, m³, liras u otra) y `valor` numérico
- hecho: la narración cuenta ese hecho; aportás el quién, el cargo, la fecha, lo que dice el acta. Lleva etiqueta corta (la fuente o el documento, con año).
- documento: una carta, un acta, un informe que la narración menciona o cuyo momento está contando. Sale como recorte: kicker = nombre real del documento con año; titular = lo esencial en una línea, redactado (no es cita literal).
- cita: la narración nombra a esa persona o lee de ella; texto literal del dato, con el autor.
- persona: la narración nombra a alguien por primera vez en el capítulo; etiqueta = cargo, texto = nombre, tal como están en el dato.
- lupa: la narración nombra un detalle chico que está en la imagen (fisura, firma, fecha en un papel); nunca el sujeto de la foto. Texto = qué se señala.

Escritura: la etiqueta es una línea corta que dice qué es («ANCHO DE LA FISURA», «ACTA DEL CONSEJO SUPERIOR»); el dato es UNA línea corta con el valor o el hecho en pocas palabras («Más de 1 metro», «13 de 34 representantes presentes»). Nunca una oración larga: se tiene que leer en dos segundos. Nunca un fragmento sin sujeto o sin el valor. No pongas el nombre de la fuente ni el año de publicación en el dato. Para citas, copiá el dato literal. Para el resto, redactá, pero cada número, nombre propio, fecha y cantidad tiene que estar en el texto fuente de ese dato; si el dato no trae el valor, no va.

Para cada bloque devolvé: `sentence_idx`, `word_idx` (la palabra de esa oración que el dato responde: la narración dice «murió» y el bloque pone el nombre; dice «aprobó» y el bloque pone el acta), `beat`, `rank`, `tipo`, `etiqueta`, `texto`, `pool_id`, y si es cifra también unidad y valor y una línea `aporta` que diga qué dice que la narración no dice. Si no podés escribir `aporta` con algo concreto, el bloque no va.

Respondé SOLO con un objeto JSON, sin texto antes ni después."""

ROTULISTA_USER = """CAPÍTULO {cap} — {titulo}

NARRACIÓN (oración por oración; cada palabra con su índice):
{oraciones: "[idx] t0–t1 · beat N · texto con palabras numeradas: 0:En 1:marzo 2:de …"}

BEATS DEL CAPÍTULO (n, función, ventana en segundos, cierre); el pico es el beat {pico_beat}:
{beats}

DATOS DISPONIBLES (solo estos; cada uno con su texto fuente):
{items: "- id · tipo Q/D/T · a_pantalla: sí/no · por_que: … · fuente: … · texto fuente: «…»"}

YA MOSTRADO EN CAPÍTULOS ANTERIORES (no repetir):
{ya_mostrado}

Devolvé:
{"bloques": [{"sentence_idx": int, "word_idx": int, "beat": int, "rank": int, "tipo": "cifra|hecho|documento|cita|persona|lupa", "etiqueta": str, "texto": str, "pool_id": str, "unidad": str|null, "valor": number|null, "aporta": str}], "descartados": [{"pool_id": str, "motivo": str}]}"""

_HUECOS = ("{cap}", "{titulo}",
           '{oraciones: "[idx] t0–t1 · beat N · texto con palabras numeradas: 0:En 1:marzo 2:de …"}',
           "{pico_beat}", "{beats}",
           '{items: "- id · tipo Q/D/T · a_pantalla: sí/no · por_que: … · fuente: … · texto fuente: «…»"}',
           "{ya_mostrado}")

PROMPT_VERSION_F29B = "f29b-1"     # el de F29b queda para la historia (md5 50e6ae74…): F29b_REPORT
# F34 §A.1: los tres reemplazos exactos (viejo, nuevo); el resto del prompt no cambia. El de F32 (md5 c9231e24…) queda
# como ROTULISTA_SYSTEM_F32 / ROTULISTA_USER_F32 (F32_REPORT).
A1_SYSTEM = (
    ("En cada beat puede ir como máximo UN texto; en el beat marcado como pico no va ninguno; en el gancho, a lo sumo uno.",
     "En cada beat puede ir como máximo UN texto (dos si son dos datos marcados a_pantalla y van en oraciones distintas); "
     "en el beat marcado como pico solo van los datos a_pantalla; en el gancho va a lo sumo uno, y para el gancho podés "
     "usar cualquier dato de la lista que la narración no diga en todo el video, aunque no sea de su beat: el gancho "
     "tiene que prometer algo."),
    ("Escritura: una línea de etiqueta y una o dos líneas de dato; oración completa o etiqueta + valor; nunca un fragmento "
     "sin sujeto o sin el valor.",
     "Escritura: la etiqueta es una línea corta que dice qué es («ANCHO DE LA FISURA», «ACTA DEL CONSEJO SUPERIOR»); el "
     "dato es UNA línea corta con el valor o el hecho en pocas palabras («Más de 1 metro», «13 de 34 representantes "
     "presentes»). Nunca una oración larga: se tiene que leer en dos segundos. Nunca un fragmento sin sujeto o sin el "
     "valor. No pongas el nombre de la fuente ni el año de publicación en el dato."),
    ("`pool_id` y una línea `aporta`", "`pool_id`, y si es cifra también unidad y valor y una línea `aporta`"),
)
A1_USER = (('"pool_id": str, "aporta": str}', '"pool_id": str, "unidad": str|null, "valor": number|null, "aporta": str}'),)


def _deshacer(texto: str, reemplazos: tuple[tuple[str, str], ...]) -> str:
    for viejo, nuevo in reemplazos:
        texto = texto.replace(nuevo, viejo)
    return texto


ROTULISTA_SYSTEM_F32 = _deshacer(ROTULISTA_SYSTEM, A1_SYSTEM)
ROTULISTA_USER_F32 = _deshacer(ROTULISTA_USER, A1_USER)
LINEA_B7 = "  devolvé `unidad` (metros, personas, m³, liras u otra) y `valor` numérico"   # F32 §B.7: lo único nuevo
ROTULISTA_SYSTEM_F29C = ROTULISTA_SYSTEM_F32.replace("\n" + LINEA_B7, "")  # el de F29c (md5 7dafbb96…): F29c_REPORT


def prompt_md5() -> str:
    return hashlib.md5((ROTULISTA_SYSTEM + "\n\n" + ROTULISTA_USER).encode("utf-8")).hexdigest()


# ═══════════════════════ entrada ═══════════════════════

def _tipo_id(i: str) -> str:
    return (str(i)[:1] or "?").upper()


def items_cap(cap: int, escaleta: dict, beats: list[dict], pool: dict | None) -> list[dict[str, Any]]:
    """Los `a_pantalla` del cap + `dato_central`/`datos_apoyo` de sus beats (nada más), con su texto fuente completo."""
    from script_engine.gfx_realizador import beat_de_pantalla
    its = ev.items(pool) if pool else {}
    out: dict[str, dict[str, Any]] = {}
    for a in escaleta.get("a_pantalla") or []:
        if int(a.get("cap") or 0) != cap:
            continue
        i = str(a.get("id"))
        n, _ = beat_de_pantalla(a, beats)
        if i in its and i not in out:
            out[i] = {"id": i, "a_pantalla": True, "por_que": str(a.get("por_que") or ""), "beats": [n] if n else []}
    for b in beats:
        for i in [b["dato_central"]] + list(b["datos_apoyo"]):
            if not i or i not in its:
                continue
            x = out.setdefault(i, {"id": i, "a_pantalla": False, "por_que": "", "beats": []})
            if b["n"] not in x["beats"]:
                x["beats"].append(b["n"])
    res = []
    for i, x in out.items():
        it = its[i]
        res.append({**x, "tipo": _tipo_id(i), "kind": it["_kind"], "texto": re.sub(r"\s+", " ", ev.text_of(it)).strip(),
                    "fuente": str(it.get("fuente") or ""), "autor": str(it.get("autor") or "")})
    return res


def ya_mostrado(cap: int, escaleta: dict, pool: dict | None) -> list[dict[str, str]]:
    """Los `a_pantalla` de los caps anteriores (salen sí o sí: se saben antes de correr los caps en paralelo). Lo que
    de verdad salió en caps anteriores se vuelve a mirar al colocar (gfx_pool.used_ids_before)."""
    its = ev.items(pool) if pool else {}
    out = []
    for a in escaleta.get("a_pantalla") or []:
        i = str(a.get("id"))
        if int(a.get("cap") or 0) < cap and i in its:
            out.append({"id": i, "texto": re.sub(r"\s+", " ", ev.text_of(its[i])).strip()})
    return sorted(out, key=lambda x: x["id"])


def voz_del_video(ctx: dict[str, Any]) -> list[str]:
    """§A.4: la voz de los 7 caps, oración por oración (el texto de la narración: el mismo que los subtítulos remapeados
    del sync map)."""
    out = []
    for c in sorted(ctx.get("chapters") or [], key=lambda c: int(c.get("chapter_number") or 0)):
        out += [s for s in re.split(r"(?<=[.!?…])\s+", str(c.get("narration") or "").strip()) if s.strip()]
    return out


def voz_previa(ctx: dict[str, Any]) -> str:
    """F34 §A.2.3: la voz de los caps anteriores al del contexto (un nombre que ya dijo no es spoiler)."""
    n = int(ctx.get("chapter_number") or 0)
    return " ".join(str(c.get("narration") or "") for c in sorted(ctx.get("chapters") or [],
                    key=lambda c: int(c.get("chapter_number") or 0)) if int(c.get("chapter_number") or 0) < n)


def items_gancho(beats: list[dict], pool: dict | None, ya: set[str], voz_video: list[str]) -> list[dict[str, Any]]:
    """F34 §A.1: para el gancho, todos los ítems del pool del video (no solo los del beat), cada uno marcado con si la voz
    lo dice en algún cap; esos se descartan en `validar`. Lectura declarada de «lo dice»: sus anclas literales
    (evidence.used_in: la cifra, la fecha, el nombre) o una de sus cifras duras (sin años ni días, evidence._figures) por
    valor (numero_en: «doscientos sesenta y seis» = 266). La coincidencia del 60 % de palabras (ya_dicho, pensada para la
    voz de un beat) no se usa: contra la voz de todo el video marca casi todo (D118 «266 metros» quedaba como dicho)."""
    g = next((b for b in beats if b["funcion"] == "gancho"), None)
    if g is None or not pool:
        return []
    voz = " ".join(voz_video)
    out = []
    for i, it in ev.items(pool).items():
        if i in ya:
            continue
        out.append({"id": i, "a_pantalla": False, "por_que": "", "beats": [g["n"]], "tipo": _tipo_id(i),
                    "kind": it["_kind"], "texto": re.sub(r"\s+", " ", ev.text_of(it)).strip(),
                    "fuente": str(it.get("fuente") or ""), "autor": str(it.get("autor") or ""), "gancho": True,
                    "dice_voz": ev.used_in(voz, it) or any(numero_en(n, voz) for n in ev._figures(ev.text_of(it)))})
    return out


def entrada(cap: int, real: dict, escaleta: dict, pool: dict | None, words: list[dict], time_offset: float,
            titulo: str | None = None, voz_video: list[str] | None = None, pre_roll: float = 0.0,
            voz_antes: str = "") -> dict[str, Any]:
    """La entrada del rotulista de un cap. `pre_roll` (F30b §B.3): los segundos de title card sin voz que el cap tiene
    adelante; los tiempos quedan en el tiempo del plan (con el pre-roll) y el pedido los imprime sin él, así el prompt
    (y su caché) es el mismo con o sin pre-roll. F34: `voz_antes` = la voz de los caps anteriores (spoiler, §A.2.3); si el
    cap tiene gancho, los ítems traen además todo el pool del video (§A.1)."""
    sents = oraciones(words, time_offset)
    beats = real["beats"]
    for s in sents:
        s["beat"] = beat_de_oracion(s, beats)
    its = items_cap(cap, escaleta, beats, pool)
    reservados = {str(a.get("id")) for a in escaleta.get("a_pantalla") or []}    # los a_pantalla de otros caps: suyos
    its += items_gancho(beats, pool, {x["id"] for x in its} | reservados, list(voz_video or []))
    pk = pico_cap(cap, escaleta, beats, sents, pool)
    tit = titulo or " · ".join(dict.fromkeys(b["funcion"] for b in beats))
    return {"cap": cap, "titulo": tit, "oraciones": sents,
            "beats": [{k: b[k] for k in ("n", "funcion", "t0", "t1", "cierre", "dato_central", "datos_apoyo")}
                      for b in beats],
            "items": its, "ya_mostrado": ya_mostrado(cap, escaleta, pool), "pico": pk,
            "voz_video": list(voz_video or []), "pre_roll": round(float(pre_roll), 3), "voz_antes": voz_antes}


def prompt_user(ent: dict[str, Any]) -> str:
    def item_line(x: dict) -> str:
        fuente = x["fuente"] or "—"
        if x["kind"] == "citas" and x["autor"]:
            fuente += f" (autor: {x['autor']})"
        gancho = (f" · solo para el gancho · la narración lo dice en el video: {'sí' if x['dice_voz'] else 'no'}"
                  if x.get("gancho") else "")                   # F34 §A.1: el pool del video, marcado
        return (f"- {x['id']} · tipo {x['tipo']} · a_pantalla: {'sí' if x['a_pantalla'] else 'no'} · por_que: "
                f"{x['por_que'] or '—'}{gancho} · fuente: {fuente} · texto fuente: «{x['texto']}»")

    def or_line(s: dict) -> str:
        pal = s.get("palabras") or [{"k": j, "w": w} for j, w in enumerate(palabras(s["texto"]))]
        return (f"[{s['idx']}] {round(s['t0'] - pr, 3):.1f}–{round(s['t1'] - pr, 3):.1f} · beat {s.get('beat', '—')} · "
                + " ".join(f"{p['k']}:{p['w']}" for p in pal))
    pr = float(ent.get("pre_roll") or 0.0)
    pk = ent["pico"] or {"beat": "—"}
    vals = (str(ent["cap"]), ent["titulo"],
            "\n".join(or_line(s) for s in ent["oraciones"]),
            str(pk["beat"]),
            "\n".join(f"- {b['n']} · {b['funcion']} · {round(b['t0'] - pr, 3):.1f}–{round(b['t1'] - pr, 3):.1f} s · cierre: «{b['cierre'] or '—'}»"
                      for b in ent["beats"]),
            "\n".join(item_line(x) for x in ent["items"]) or "(ninguno)",
            "\n".join(f"- {x['id']} «{x['texto']}»" for x in ent["ya_mostrado"]) or "(nada)")
    out = ROTULISTA_USER
    for h, v in zip(_HUECOS, vals):
        out = out.replace(h, v)
    return out


# ═══════════════════════ llamada ═══════════════════════

_LOCK = threading.Lock()
_EN_VUELO: dict[str, float] = {}      # peor caso (US$) de las llamadas en curso, por carpeta de trabajo


def _ledger(work_dir: Path) -> Path:
    return Path(work_dir) / "rotulista_costos.json"


def gastado(work_dir: Path) -> float:
    f = _ledger(work_dir)
    try:
        return float(json.loads(f.read_text(encoding="utf-8")).get("usd", 0.0)) if f.exists() else 0.0
    except (OSError, ValueError):
        return 0.0


def primer_json(txt: str) -> dict | None:
    """§A.6.1: el primer objeto JSON válido del texto (lo que haya antes o después se ignora); None si no hay ninguno."""
    dec = json.JSONDecoder()
    for m in re.finditer(r"\{", txt or ""):
        try:
            obj, _ = dec.raw_decode(txt, m.start())
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            return obj
    return None


def _solo_el_json(r: dict) -> dict:
    """La respuesta de la API con el texto reemplazado por su primer objeto JSON válido (si hay uno): claude_helpers
    parsea eso y no vuelve a pedir por un texto de más antes o después."""
    txt = "".join(b.get("text") or "" for b in r.get("content") or [] if b.get("type") == "text")
    obj = primer_json(txt)
    if obj is None:
        return r
    return {**r, "content": [{"type": "text", "text": json.dumps(obj, ensure_ascii=False)}]}


def _post_con_registro(work_dir: Path, cap_id: str, modelo: str, tope: float, crudos: list[dict]) -> Callable[[dict], dict]:
    import claude_helpers as hx

    def post(body: dict) -> dict:
        pin, pout = hx.PRICES.get(hx._base(modelo), (0.0, 0.0))
        peor = len(json.dumps(body, ensure_ascii=False)) / 2.5 / 1e6 * pin + OUT_TOKENS_PEOR / 1e6 * pout
        clave = str(Path(work_dir).resolve())
        with _LOCK:                      # lo gastado + el peor caso de las llamadas que están en vuelo (prefetch en
            vuelo = _EN_VUELO.get(clave, 0.0)   # paralelo: las 7 ven el mismo gasto inicial si solo se mira el ledger)
            if gastado(work_dir) + vuelo + peor > tope:
                raise TopeRotulista(f"tope Claude del rotulista US$ {tope:.2f} (gastado {gastado(work_dir):.4f}, "
                                    f"en vuelo {vuelo:.4f}, esta llamada hasta {peor:.4f})")
            _EN_VUELO[clave] = vuelo + peor
        t0 = time.time()
        try:
            r = hx._post(body)
        finally:
            with _LOCK:
                _EN_VUELO[clave] = max(0.0, _EN_VUELO.get(clave, 0.0) - peor)
        u = r.get("usage") or {}
        usd = round(hx.cost_of(modelo, u), 5)
        crudos.append({"respuesta": r, "segundos": round(time.time() - t0, 1), "usd": usd})
        with _LOCK:
            f = _ledger(work_dir)
            c = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {"llamadas": [], "usd": 0.0}
            c["llamadas"].append({"cap": cap_id, "in": u.get("input_tokens"), "out": u.get("output_tokens"),
                                  "stop": r.get("stop_reason"), "usd": usd, "segundos": round(time.time() - t0, 1)})
            c["usd"] = round(sum(x["usd"] for x in c["llamadas"]), 5)
            f.write_text(json.dumps(c, ensure_ascii=False, indent=1), encoding="utf-8")
        return _solo_el_json(r)
    return post


class TopeRotulista(RuntimeError):
    """El tope de costo del rotulista no alcanza para otra llamada: el cap sale sin bloques de texto."""


def _reintento(user: str, errores: list[str]) -> str:
    return user + "\n\nTU RESPUESTA ANTERIOR TUVO ESTOS PROBLEMAS (corregilos y devolvé el JSON completo otra vez):\n" + \
        "\n".join(f"- {e}" for e in errores)


def pasados_de_largo(resp: Any, ent: dict[str, Any]) -> list[str]:
    """F36 §B.8: los bloques de la respuesta cuya etiqueta + dato pasan de lo que cabe en su oración (`caben` de la
    entrada; sin `caben`, nada), con el número, para el reintento."""
    its = {x["id"]: x for x in ent.get("items") or []}
    sents = ent.get("oraciones") or []
    out = []
    for b in (resp or {}).get("bloques") or [] if isinstance(resp, dict) else []:
        if not isinstance(b, dict):
            continue
        try:
            si = int(b.get("sentence_idx"))
        except (TypeError, ValueError):
            continue
        cab = sents[si].get("caben") if 0 <= si < len(sents) else None
        x = its.get(str(b.get("pool_id") or "")) or {}
        n = caracteres(str(b.get("tipo") or ""), b.get("etiqueta"), str(b.get("texto") or ""), x.get("autor") or "")
        if cab is not None and n > cab:
            out.append(f"{b.get('pool_id')} en la oración [{si}] «{b.get('texto')}»: etiqueta + dato tienen {n} "
                       f"caracteres y en esa oración caben {cab}")
    return out


def llamar(ent: dict[str, Any], words: list[dict], time_offset: float, work_dir: Path, cap_id: str, *,
           modelo: str | None = None, effort: str | None = None, tope: float = 2.0,
           call: Callable[..., dict] | None = None, log: list[str] | None = None) -> dict[str, Any]:
    """Rotulista de un cap (con caché por pedido). Devuelve {modelo, intentos, final, validacion, error?}. `call` (tests)
    reemplaza la llamada: recibe (prompt, system_instruction=, description=) y devuelve el dict parseado."""
    import claude_helpers as hx
    modelo, effort = modelo or MODELO_DEFAULT, effort or EFFORT_DEFAULT
    log = log if log is not None else []
    user = prompt_user(ent)
    clave = hashlib.sha1(f"{PROMPT_VERSION}|{modelo}|{effort}|{ROTULISTA_SYSTEM}|{user}".encode("utf-8")).hexdigest()[:20]
    raw_f = Path(work_dir) / f"rotulista_{cap_id}.raw.json"
    try:
        prev = json.loads(raw_f.read_text(encoding="utf-8")) if raw_f.exists() else None
    except (OSError, ValueError):
        prev = None
    if prev and prev.get("clave") == clave and prev.get("final") is not None:
        prev["validacion"] = validar(prev["final"], ent, words, time_offset)   # determinista: con el código de hoy
        v = prev.get("validacion") or {"bloques": []}
        log.append(f"  rotulista {cap_id}: caché ({len(prev.get('intentos') or [])} intento(s), {len(v['bloques'])} bloques)")
        return {**prev, "cache": True}
    out: dict[str, Any] = {"clave": clave, "modelo": modelo, "effort": effort, "prompt_version": PROMPT_VERSION,
                           "prompt_md5": prompt_md5(), "entrada": ent, "intentos": [], "final": None, "validacion": None}
    usados = {"forma": False, "a_pantalla": False}
    pedido = user
    for _ in range(3):
        crudos: list[dict] = []
        t0 = time.time()
        err = None
        try:
            if call is not None:
                resp = call(pedido, system_instruction=ROTULISTA_SYSTEM, description=f"gfx_rotulista {cap_id}")
            else:
                c = hx.make_call(modelo, effort, post=_post_con_registro(work_dir, cap_id, modelo, tope, crudos))
                resp = c(pedido, system_instruction=ROTULISTA_SYSTEM, response_schema=None,
                         description=f"gfx_rotulista {cap_id}")
        except TopeRotulista as e:
            out["error"] = str(e)
            log.append(f"  rotulista: {e} → cap sin bloques de texto")
            break
        except Exception as e:  # noqa: BLE001 — sin ningún JSON tras los reintentos de claude_helpers o la API caída
            resp, err = None, f"{type(e).__name__}: {str(e)[:200]}"
        val = validar(resp, ent, words, time_offset) if resp is not None else None
        out["intentos"].append({"pedido": pedido, "respuesta": resp, "crudas": crudos, "error": err, "validacion": val,
                                "segundos": round(time.time() - t0, 1)})
        if resp is None:
            if usados["forma"]:
                out["final"], out["validacion"] = None, None
                log.append(f"  rotulista: la respuesta no parsea dos veces ({err}) → cap sin bloques de texto")
                break
            usados["forma"] = True
            pedido = _reintento(user, [f"la respuesta no es JSON válido ({err})"])
            continue
        out["final"], out["validacion"] = resp, val
        errores = []
        de_contenido = [r for r in val["rechazos"] if r["regla"] in REGLAS_REINTENTO]
        if de_contenido and not usados["forma"]:
            usados["forma"] = True
            errores += [f"{r['pool_id']} en la oración [{r['sentence_idx']}] «{r['texto']}»: {r['motivo']}"
                        for r in de_contenido]
        no_propuestos = [i for i in val["faltan"]
                         if not any(r["pool_id"] == i and r["regla"] in ("cantidad", "lectura") for r in val["rechazos"])]
        largos = pasados_de_largo(resp, ent)             # F36 §B.8: el reintento le dice el número
        if largos and not usados["forma"]:
            usados["forma"] = True
            errores += largos
        if (no_propuestos or val["incompletos"]) and not usados["a_pantalla"]:
            usados["a_pantalla"] = True
            pq = {x["id"]: x["por_que"] for x in ent["items"]}
            errores += [f"falta el dato a_pantalla {i} (por_que: {pq.get(i)})" for i in no_propuestos]
            errores += [f"el dato a_pantalla {i} salió sin {f} (por_que: {pq.get(i)})"
                        for i, f in val["incompletos"].items()]
        if not errores:
            break
        pedido = _reintento(user, errores)
    v = out["validacion"]
    if v is not None:
        log.append(f"  rotulista {cap_id}: {len(out['intentos'])} intento(s) · {len(v['bloques'])} bloque(s) · "
                   f"{len(v['rechazos'])} fuera · a_pantalla que faltan {v['motivo_faltan']} · incompletos {v['incompletos']}")
    raw_f.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    return out
