"""
script_engine/m01f_critico.py — F67 B (DECISIONES 2026-10-31 18:43, «Fuego»): el crítico de retención de la narración. Corre en
Fase 1 después del juez m05 y del verificador, antes de la compuerta de narración: una llamada a Claude Opus 5.5 medium con la
misma entrada que el lab F67a (narración por oraciones, escaleta, archivo, disputas), más `metricas` (el bloque `retencion` del
juez) y `verificacion` (la tabla de 01b_verificacion.md). Solo propone (Fase 1 del lazo): Omar acepta o edita en QA Studio y nada
se corrige solo. Sin JSON tras el reintento no aborta: 01f_critico lleva `error` y la cadena sigue a la PARADA.

    SYSTEM, FORMATO   m01f_prompts/*.txt, bloques §4 y §5 de lab/hyperframes/f67/HANDOFF_F67a_critico_por_api.md byte a byte
                      (md5 del SYSTEM en lab/hyperframes/f67/a/md5.json; candado en tests/test_m01f_compuerta.py).
    entrada           caps sin `caben`, beats con `humano_en_escena` (m01e no lo copia: se repone de la escaleta por `n`, como
                      el lab v3), escaleta_video, archivo, disputas, metricas, verificacion.
    generar           llamada → validación en código → 01f_critico.json/.md en el directorio del topic.
    validar           ids, (cap, idx), palabras antes → después, cifras sin respaldo y marcas `[…]`, por DEBERÍA; se reporta,
                      no se trunca ni se corrige (DEBERÍA sin tope en código: voto del analista, pendiente de Omar, F67 §9.2).
Copiado del lab, que producción no importa: armar_user, leer_json, validar, critica_md, tabla_verificacion, faltantes.
"""
from __future__ import annotations

import hashlib
import json
import re
import time
from pathlib import Path
from typing import Any, Callable

from script_engine.m05_narrative import RE_CIFRA, cifra_norm

PROMPT_VERSION = "m01f-1"       # F67 B: el SYSTEM y el FORMATO de F67a tal cual
MODELO = "claude-opus-5-5"      # DECISIONES 2026-10-31 18:43 (F67a: 6,5/6,4, Δ 0,1, US$ 0,78)
EFFORT = "medium"               # DECISIONES 2026-10-31 18:43
INTENTOS = 2                    # F67a §6.2: 1 reintento idéntico si no hay JSON
ARCHIVO = "01f_critico"
_PROMPTS = Path(__file__).resolve().parent / "m01f_prompts"
SYSTEM = (_PROMPTS / "SYSTEM.txt").read_text(encoding="utf-8")
FORMATO = (_PROMPTS / "FORMATO.txt").read_text(encoding="utf-8")
SEPARADOR = "[…]"                 # F67d: salida real de m01f-1; separa las partes de un DEBERÍA no contiguo
ACCIONES = ("aceptar", "editar", "rechazar")
RE_MARCA = re.compile(r"\[[^\]]*\]")   # F67a abierto 3: `[idx1]`, `[…]`; la narración nunca lleva corchetes: va a TTS


def md5(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def _dir(steps_dir: Path | None) -> Path:
    from script_engine.m01a_skeleton import STEPS_DIR
    return Path(steps_dir or STEPS_DIR)


def palabras(texto: str) -> int:
    from script_engine.m05_narrative import words_of
    return len(words_of(texto))


def tabla_verificacion(md_txt: str) -> str:
    """La tabla de 01b_verificacion.md tal cual."""
    lineas = md_txt.replace("\r\n", "\n").split("\n")
    i = next(k for k, x in enumerate(lineas) if x.startswith("| cap |"))
    j = i
    while j < len(lineas) and lineas[j].startswith("|"):
        j += 1
    return "\n".join(lineas[i:j])


def faltantes(e: dict) -> list[str]:
    """Lo que el crítico tiene que encontrar en la entrada (F67a §2)."""
    f = []
    ev = e.get("escaleta_video") or {}
    if "promesa_gancho" not in ev:
        f.append("entrada.escaleta_video.promesa_gancho")
    if "pico" not in ev:
        f.append("entrada.escaleta_video.pico")
    if not e.get("beats") or not all("humano_en_escena" in b for b in e["beats"]):
        f.append("entrada.beats[*].humano_en_escena")
    if not e.get("archivo") or not all("id" in x for x in e["archivo"]):
        f.append("entrada.archivo[*].id")
    if not e.get("caps") or not all("idx" in s for c in e["caps"] for s in c["oraciones"]):
        f.append("entrada.caps[*].oraciones[*].idx")
    return f


def armar_user(e: dict, m: dict, verif: str, formato: str) -> str:
    caps = [{**c, "oraciones": [{k: v for k, v in s.items() if k != "caben"} for s in c["oraciones"]]} for c in e["caps"]]
    payload = {"caps": caps, "beats": e["beats"], "escaleta_video": e["escaleta_video"], "archivo": e["archivo"], "disputas": e["disputas"],
               "metricas": m, "verificacion": verif}
    return json.dumps(payload, ensure_ascii=False, indent=None) + "\n\nFormato de salida (devolvé solo este JSON):\n" + formato


def entrada(topic_id: str, steps_dir: Path | None = None, *, pool: dict | None = None, log: list[str] | None = None) -> dict[str, Any]:
    """{e, metricas, verificacion}: lo que `armar_user` recibe. La misma entrada del lab salvo `metricas`, que viene del juez
    (si 06_judge_narrative no tiene `retencion`, corre el juez primero)."""
    from script_engine import m01e_pantalla as mp
    from script_engine.clima import vocabulario_clima
    from script_engine.m05_narrative import judge_narration
    sd = _dir(steps_dir)
    d = sd / topic_id
    carga = mp.cargar(topic_id, sd, pool, log)
    e = mp._para_modelo(mp.entrada(carga, vocabulario_clima()))
    e.pop("clima", None)
    n_esc = {int(b["n"]): b for b in carga["escaleta"].get("beats") or []}
    for b in e["beats"]:
        if "humano_en_escena" in n_esc.get(b["n"], {}):
            b["humano_en_escena"] = n_esc[b["n"]]["humano_en_escena"]
    f = faltantes(e)
    if f:
        raise ValueError(f"al crítico le faltan en la entrada: {f}")
    j = d / "06_judge_narrative.json"
    rep = json.loads(j.read_text(encoding="utf-8")) if j.exists() else {}
    if not rep.get("retencion"):
        rep = judge_narration(topic_id, steps_dir=sd, pool=carga["pool"])
    if not rep.get("retencion"):
        raise ValueError(f"{topic_id}: el juez no dejó `retencion`: el crítico no tiene métricas")
    v = d / "01b_verificacion.md"
    verif = tabla_verificacion(v.read_text(encoding="utf-8")) if v.exists() else "sin verificación en disco"
    return {"e": e, "metricas": rep["retencion"], "verificacion": verif}


def leer_json(txt: str) -> dict | None:
    """F67a §6.2: quitar fences ```json si las hay, json.loads."""
    t = (txt or "").strip()
    f = re.fullmatch(r"```(?:json)?\s*(.*?)\s*```", t, re.S)
    try:
        r = json.loads(f.group(1) if f else t)
    except json.JSONDecodeError:
        return None
    return r if isinstance(r, dict) else None


def llamar(user: str, *, post: Callable[[dict], dict] | None = None, log: list[str] | None = None) -> dict[str, Any]:
    """{respuesta, usage, usd, segundos, intentos, error, crudo}. Sin JSON o error de API → 1 reintento idéntico."""
    import claude_helpers as hx
    log = log if log is not None else []
    body = {"model": MODELO, "max_tokens": hx.MAX_TOKENS, "system": SYSTEM, "messages": [{"role": "user", "content": user}],
            "output_config": {"effort": EFFORT}}
    out: dict[str, Any] = {"respuesta": None, "usage": None, "usd": 0.0, "segundos": 0.0, "intentos": 0, "error": None, "crudo": None}
    for k in range(INTENTOS):
        out["intentos"] = k + 1
        t0 = time.time()
        try:
            r = (post or hx._post)(body)
        except Exception as e:  # noqa: BLE001 — API, timeout: se anota y, si es el primero, se reintenta
            out["segundos"] = round(out["segundos"] + time.time() - t0, 1)
            out["error"] = f"{type(e).__name__}: {str(e)[:200]}"
            log.append(f"  [m01f] intento {k + 1}: {out['error']}")
            continue
        out["segundos"] = round(out["segundos"] + time.time() - t0, 1)
        u = r.get("usage") or {}
        out["usage"] = u
        out["usd"] = round(out["usd"] + hx.cost_of(MODELO, u), 5)
        if post is None:
            hx._track(r.get("model") or MODELO, u, "m01f_critico")
        txt = "".join(c.get("text") or "" for c in r.get("content") or [] if c.get("type") == "text")
        out["crudo"] = txt
        resp = leer_json(txt)
        log.append(f"  [m01f] intento {k + 1}: in {u.get('input_tokens')} · out {u.get('output_tokens')} · US$ {hx.cost_of(MODELO, u):.4f} · "
                   f"{'JSON' if resp is not None else 'SIN JSON'}")
        if resp is not None:
            out.update(respuesta=resp, error=None, crudo=None)
            break
        out["error"] = f"la respuesta no es JSON válido (stop_reason {r.get('stop_reason')})"
    return out


def numeros(t: Any) -> set[str]:
    return {cifra_norm(x) for x in RE_CIFRA.findall(str(t or ""))}


def limpiar(texto: Any) -> str:
    """El `deberia_texto` sin marcas entre corchetes y sin espacios dobles: lo que entra a la narración."""
    return re.sub(r"[ \t]{2,}", " ", RE_MARCA.sub(" ", str(texto or ""))).strip()


def validar(resp: dict | None, e: dict) -> dict[str, Any]:
    """F67a §6.3 + `fecha` en el conjunto permitido (abierto 4) + marcas (abierto 3: se cuentan y no pasan por las cifras ni las
    palabras). `k` = ordinal con base 1 en el orden de la respuesta, el mismo número del .md. Se reporta, no falla."""
    if resp is None:
        return {"deberia": [], "ids_invalidos": [], "oraciones_invalidas": []}
    arch = {x["id"]: x for x in e["archivo"]}
    ors = {(c["cap"], s["idx"]): s["texto"] for c in e["caps"] for s in c["oraciones"]}
    voz = set().union(*(numeros(t) for t in ors.values())) if ors else set()
    filas, ids_inv, ors_inv = [], [], []
    for k, d in enumerate([x for x in resp.get("deberia") or [] if isinstance(x, dict)], start=1):
        cap = str(d.get("cap"))
        idx = list(d.get("oraciones") or [])
        ids = [str(i) for i in d.get("ids") or []]
        malos_ids = [i for i in ids if i not in arch]
        malos_or = [f"{cap}:{i}" for i in idx if (cap, i) not in ors]
        ids_inv += malos_ids
        ors_inv += malos_or
        original = [ors[(cap, i)] for i in idx if (cap, i) in ors]
        ok = set(voz)
        for i in ids:
            if i in arch:
                ok |= numeros(arch[i].get("texto")) | numeros(arch[i].get("contexto_fuente")) | numeros(arch[i].get("fecha"))
        crudo = str(d.get("deberia_texto") or "")
        limpio = limpiar(crudo)
        filas.append({"k": k, "cap": cap, "idx": idx, "texto_original": original, "palabras_antes": sum(palabras(t) for t in original),
                      "palabras_despues": palabras(limpio), "cifras_sin_respaldo": sorted(x for x in numeros(limpio) if x not in ok),
                      "marcas": RE_MARCA.findall(crudo), "ids_invalidos": malos_ids})
    return {"deberia": filas, "ids_invalidos": ids_inv, "oraciones_invalidas": ors_inv}


def critica_md(resp: dict | None, val: dict, metricas: dict, cabecera: str) -> str:
    """01f_critico.md: la crítica y sus métricas, con cada DEBERÍA numerado (`k`) y lo que la validación midió."""
    L = ["# Crítica de la narración", "", cabecera, ""]
    if resp is None:
        return "\n".join(L + ["sin JSON válido", ""])
    g = resp.get("gancho") or {}
    p = resp.get("pico") or {}
    per = metricas.get("personaje")
    L += [f"**Nota total:** {resp.get('nota_total')}", "", "## Resumen", ""] + [f"- {x}" for x in resp.get("resumen") or []]
    L += ["", "Personaje según la escaleta: " + (f"{per['id']} {per['nombre']}" if per else f"ninguno ({metricas.get('personaje_motivo')})"), "",
          "## Métricas por cap (código)", "", "| cap | palabras | s | % | % acum. | años/min | racha sin personaje |", "|---|---|---|---|---|---|---|"]
    L += [f"| {c['cap']} | {c['palabras']} | {c['segundos']} | {c['pct']} | {c['pct_acumulado']} | {c['anios_por_min']} | {c['racha_max_sin_personaje']} |"
          for c in metricas.get("caps") or []]
    L += ["", "## Gancho", "", f"- Promesa cumplida: {g.get('promesa_cumplida')}", f"- {g.get('comentario')}", "", "## Capítulos", "",
          "| cap | nota | personaje en voz | oraciones seguidas sin personaje | fuerte | débil | re-enganche |", "|---|---|---|---|---|---|---|"]
    for c in resp.get("caps") or []:
        L.append(f"| {c.get('cap')} | {c.get('nota')} | {c.get('personaje_en_voz')} | {c.get('oraciones_seguidas_sin_personaje')} | {c.get('fuerte')} | {c.get('debil')} | {c.get('reengancho')} |")
    L += ["", "## Loops", "", "| pregunta | abre | paga | se recuerda |", "|---|---|---|---|"]
    for x in resp.get("loops") or []:
        L.append(f"| {x.get('pregunta')} | {x.get('abre')} | {x.get('paga')} | {x.get('se_recuerda')} |")
    L += ["", "## Pico", "", f"- {p.get('cap')} · acumulado {p.get('pct_acumulado')} % · {p.get('segundos_despues')} s después", f"- {p.get('comentario')}", "",
          "## Cierre", "", str(resp.get("cierre")), "", "## DEBERÍA", ""]
    filas = {f["k"]: f for f in val.get("deberia") or []}
    for k, d in enumerate([x for x in resp.get("deberia") or [] if isinstance(x, dict)], start=1):
        f = filas.get(k) or {}
        L += [f"### {k}. {d.get('cap')} · oraciones {d.get('oraciones')} · {f.get('palabras_antes')} → {f.get('palabras_despues')} palabras", "",
              f"- **Sale:** {d.get('que_sale')}", f"- **Por qué se van:** {d.get('por_que_se_van')}",
              f"- **Ids:** {', '.join(str(i) for i in d.get('ids') or [])}" + (f" · **inválidos:** {', '.join(f['ids_invalidos'])}" if f.get("ids_invalidos") else ""),
              f"- **Cifras sin respaldo:** {', '.join(f.get('cifras_sin_respaldo') or []) or '—'} · **Marcas:** {', '.join(f.get('marcas') or []) or '—'}", "",
              f"> {d.get('deberia_texto')}", ""]
    L += ["## Reglas generales candidatas", ""]
    L += [f"- {x.get('regla')} · *medible:* {x.get('medible_como')} · *por qué:* {x.get('por_que')}" for x in resp.get("reglas_generales_candidatas") or []]
    L += ["", "## Riesgos", ""] + [f"- {x}" for x in resp.get("riesgos") or []] + [""]
    return "\n".join(L)


def generar(topic_id: str, steps_dir: Path | None = None, *, pool: dict | None = None, post: Callable[[dict], dict] | None = None,
            log: list[str] | None = None) -> dict[str, Any]:
    """El paso entero: entrada → llamada → validación → 01f_critico.json/.md. Devuelve lo que escribe."""
    from script_engine.m01d_particion import md5_narracion
    log = log if log is not None else []
    d = _dir(steps_dir) / topic_id
    ent = entrada(topic_id, steps_dir, pool=pool, log=log)
    user = armar_user(ent["e"], ent["metricas"], ent["verificacion"], FORMATO)
    r = llamar(user, post=post, log=log)
    val = validar(r["respuesta"], ent["e"])
    out = {"prompt_version": PROMPT_VERSION, "modelo": MODELO, "effort": EFFORT, "system_md5": md5(SYSTEM), "user_md5": md5(user),
           "narracion_md5": md5_narracion(json.loads((d / "01b_narracion_v3.json").read_text(encoding="utf-8"))),
           "usd": r["usd"], "segundos": r["segundos"], "intentos": r["intentos"], "usage": r["usage"], "respuesta": r["respuesta"],
           "validacion": val, "n_deberia": len(val["deberia"])}
    if r["respuesta"] is None:
        out.update(error=r["error"], crudo=r["crudo"])
    u = r["usage"] or {}
    cab = (f"`{PROMPT_VERSION}` · {MODELO} {EFFORT} · US$ {r['usd']:.4f} · tokens in {u.get('input_tokens')} · out {u.get('output_tokens')} · "
           f"{r['segundos']} s · {r['intentos']} intento(s) · narración `{out['narracion_md5']}`")
    (d / f"{ARCHIVO}.json").write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    (d / f"{ARCHIVO}.md").write_text(critica_md(r["respuesta"], val, ent["metricas"], cab), encoding="utf-8")
    log.append(f"  [m01f] nota {(r['respuesta'] or {}).get('nota_total')} · {out['n_deberia']} DEBERÍA · US$ {r['usd']:.4f} → {d / (ARCHIVO + '.md')}")
    return out


def cargar_critica(topic_id: str, steps_dir: Path | None = None) -> dict[str, Any] | None:
    f = _dir(steps_dir) / topic_id / f"{ARCHIVO}.json"
    try:
        return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None
    except (OSError, ValueError):
        return None


# ═══════════════════════ F67 C.2: la edición de la compuerta. Nada corre solo: Omar decide, el código reconstruye ═══════════════════════

def _carga(topic_id: str, steps_dir: Path | None) -> dict[str, Any]:
    """Topic (el cargador de `verificar_narracion`), escaleta, párrafos, pool y títulos vigentes (m01e.cargar)."""
    from fase1_5 import _topic_v3
    from script_engine import m01e_pantalla as mp
    topic = _topic_v3(topic_id)
    c = mp.cargar(topic_id, _dir(steps_dir), topic.get("evidence_pool"))
    return {"topic": topic, "esc": c["escaleta"], "parrafos": c["parrafos"], "pool": c["pool"],
            "titulos": [c["titulos"][n] for n in sorted(c["titulos"])]}


def _aplicar(topic_id: str, c: dict[str, Any], steps_dir: Path | None) -> str:
    """Reconstruye el contrato y corre el juez (US$ 0: `metricas` sigue vigente). Devuelve el md5 nuevo."""
    from script_engine.m01d_particion import md5_narracion, reconstruir
    from script_engine.m05_narrative import judge_narration
    r = reconstruir(c["topic"], c["esc"], c["parrafos"], c["pool"], c["titulos"], steps_dir=_dir(steps_dir))
    judge_narration(topic_id, steps_dir=_dir(steps_dir), pool=c["pool"])
    return md5_narracion(r["narracion_v3"])


def _oraciones_cap(parrafos: list[dict[str, Any]], n: int) -> list[dict[str, Any]]:
    """Las oraciones actuales del cap, con su párrafo y su posición en el texto del párrafo (el corte de la voz junta las palabras
    con un espacio: la posición se busca, no se calcula)."""
    from script_engine.voz_utils import oraciones_de_texto
    out = []
    for i, p in enumerate(parrafos):
        if int(p["cap"]) != n:
            continue
        pos = 0
        for t in oraciones_de_texto(p["texto"]):
            m = re.compile(r"\s+".join(re.escape(w) for w in t.split())).search(p["texto"], pos)
            out.append({"parrafo": i, "beat": int(p.get("beat") or 0), "texto": t, "ini": m.start(), "fin": m.end()})
            pos = m.end()
    return out


def _ubicar(ors: list[dict[str, Any]], original: list[str]) -> int | None:
    """Dónde está el tramo: la secuencia aparece exactamente una vez, contigua. Nunca por `idx`, que se corre al aplicar otro DEBERÍA
    del mismo cap."""
    if not original:
        return None
    textos = [o["texto"] for o in ors]
    hits = [j for j in range(len(textos) - len(original) + 1) if textos[j:j + len(original)] == original]
    return hits[0] if len(hits) == 1 else None


# ═══════════════════════ F67d: el borrador. Aceptar, editar o rechazar no escribe; aprobar aplica todo junto, una vez ═══════════════════════

def _partes(crudo: Any) -> list[str]:
    """Las partes del `deberia_texto`: se corta por SEPARADOR en crudo, porque `limpiar` lo borra; después se limpia cada una."""
    return [t for t in (limpiar(x) for x in str(crudo or "").split(SEPARADOR)) if t]


def _tramos(fila: dict[str, Any]) -> list[list[str]] | None:
    """Los tramos contiguos de oraciones del DEBERÍA; None si algún `idx` no existía cuando se validó."""
    idx, original = fila.get("idx") or [], fila.get("texto_original") or []
    if not original or len(idx) != len(original):
        return None
    out: list[list[str]] = []
    for pos, t in enumerate(original):
        if pos and idx[pos] == idx[pos - 1] + 1:
            out[-1].append(t)
        else:
            out.append([t])
    return out


def _sin_espacios(t: str) -> str:
    return " ".join(t.split())


def _reemplazar(ps: list[dict[str, Any]], ors: list[dict[str, Any]], j: int, n: int, nuevo: str) -> list[int]:
    """El tramo de `n` oraciones desde `j` pasa a ser `nuevo`: primer párrafo = lo previo + el texto nuevo; último = lo posterior; los del
    medio quedan sin texto. Un párrafo sin texto se ELIMINA al final de `borrador`: `tts_tags.tag_cap` saltea los vacíos y sus
    `intensities`/`pico_par` (índices de párrafo) se correrían. Devuelve los párrafos tocados."""
    a, b = ors[j], ors[j + n - 1]
    espacios = lambda t: re.sub(r"[ \t]{2,}", " ", t).strip()  # noqa: E731
    pa, pb = a["parrafo"], b["parrafo"]
    if pa == pb:
        t = ps[pa]["texto"]
        ps[pa]["texto"] = espacios(t[:a["ini"]] + nuevo + t[b["fin"]:])
    else:
        ps[pa]["texto"] = espacios(ps[pa]["texto"][:a["ini"]] + nuevo)
        ps[pb]["texto"] = espacios(ps[pb]["texto"][b["fin"]:])
        for m in range(pa + 1, pb):
            ps[m]["texto"] = ""
    return list(range(pa, pb + 1))


def _aplicar_deberia(ps: list[dict[str, Any]], fila: dict[str, Any], crudo: Any, ids: list[str]) -> dict[str, Any]:
    """Aplica un DEBERÍA sobre `ps`, entero o nada. Cada parte va con su tramo; si no coinciden en número no se adivina. Ya aplicada =
    la parte está en el texto del cap y no está contenida en su tramo original (el original puede seguir ubicable)."""
    n = int(str(fila["cap"])[2:])
    tramos, partes = _tramos(fila), _partes(crudo)
    if tramos is None:
        return {"estado": "no_aplica", "motivo": "el crítico citó oraciones que no existían"}
    if len(partes) != len(tramos):
        return {"estado": "no_aplica", "motivo": f"{len(partes)} parte(s) en el texto y {len(tramos)} tramo(s) en la narración: editar a mano"}
    copia = [{**p} for p in ps]
    tocados: list[int] = []
    ya = 0
    for parte, tramo in zip(partes, tramos):
        cap = _sin_espacios(" ".join(p["texto"] for p in copia if int(p["cap"]) == n))
        if _sin_espacios(parte) in cap and _sin_espacios(parte) not in _sin_espacios(" ".join(tramo)):
            ya += 1
            continue
        ors = _oraciones_cap(copia, n)
        j = _ubicar(ors, tramo)
        if j is None:
            return {"estado": "no_aplica", "motivo": "el texto cambió: ya no está el tramo"}
        tocados += _reemplazar(copia, ors, j, len(tramo), parte)
    if ya == len(partes):
        return {"estado": "ya_aplicado"}
    if ids:
        p = copia[tocados[0]]
        p["ids_usados"] = list(dict.fromkeys(list(p.get("ids_usados") or []) + ids))
    ps[:] = copia
    return {"estado": "aplicado", "beats": sorted({int(ps[m].get("beat") or 0) for m in tocados}), "partes_ya_aplicadas": ya}


def _decisiones(decisiones: Any) -> dict[int, dict[str, Any]]:
    """k → {accion, texto?}. JSON manda las claves como texto."""
    out: dict[int, dict[str, Any]] = {}
    for k, d in (decisiones or {}).items():
        if not isinstance(d, dict) or d.get("accion") not in ACCIONES:
            raise ValueError(f"DEBERÍA {k}: la acción tiene que ser una de {ACCIONES}")
        if d.get("texto") is not None and (not isinstance(d["texto"], str) or not d["texto"].strip()):
            raise ValueError(f"DEBERÍA {k}: el texto no puede quedar vacío")
        out[int(k)] = d
    return out


def _ediciones(parrafos: list[dict[str, Any]], ediciones: Any) -> dict[int, str]:
    """i → texto, `i` indexado sobre los párrafos del disco. Las que dejan el texto igual no son ediciones."""
    out: dict[int, str] = {}
    for e in ediciones or []:
        i, texto = e.get("i"), e.get("texto")
        if not isinstance(i, int) or isinstance(i, bool) or not 0 <= i < len(parrafos):
            raise ValueError(f"no hay párrafo {i}")
        if not isinstance(texto, str) or not texto.strip():
            raise ValueError("el párrafo no puede quedar vacío")
        if texto.strip() != parrafos[i]["texto"]:
            out[i] = texto.strip()
    return out


def borrador(parrafos: list[dict[str, Any]], critica: dict[str, Any] | None, decisiones: Any = None, ediciones: Any = None) -> dict[str, Any]:
    """Pura: sin disco y sin juez. Siempre parte de los párrafos del disco: primero las ediciones libres, después cada DEBERÍA aceptado o
    editado una sola vez (`decisiones` es un mapa k → acción). Una edición que toca el tramo de un k lo deja «no aplica».
    {parrafos, indices (el `i` del disco de cada uno), por_k {k: {estado, motivo?, beats?, ...}}, pendientes, cambio}. Estados: pendiente
    (con `aplica`: lo que pasaría al aceptarlo), aplicado, ya_aplicado, no_aplica, rechazado, editado_a_mano."""
    dec = _decisiones(decisiones)
    ed = _ediciones(parrafos, ediciones)
    filas = {f["k"]: f for f in ((critica or {}).get("validacion") or {}).get("deberia") or []}
    deb = [x for x in ((critica or {}).get("respuesta") or {}).get("deberia") or [] if isinstance(x, dict)]
    if set(dec) - set(filas):
        raise ValueError(f"no hay DEBERÍA {sorted(set(dec) - set(filas))}")
    tocado_a_mano: set[int] = set()
    for k, f in filas.items():                       # sobre el disco, antes de las ediciones
        ors = _oraciones_cap(parrafos, int(str(f["cap"])[2:]))
        for tramo in _tramos(f) or []:
            j = _ubicar(ors, tramo)
            if j is not None and any(ors[m]["parrafo"] in ed for m in range(j, j + len(tramo))):
                tocado_a_mano.add(k)
    ps = [{**p, "_i": i, **({"texto": ed[i]} if i in ed else {})} for i, p in enumerate(parrafos)]
    por_k: dict[int, dict[str, Any]] = {}
    for k in sorted(filas):
        f, d = filas[k], dec.get(k)
        x = deb[k - 1]
        malos = set(f.get("ids_invalidos") or [])
        ids = [str(i) for i in x.get("ids") or [] if str(i) not in malos]
        crudo = (d or {}).get("texto") if (d or {}).get("texto") is not None else x.get("deberia_texto")
        a_mano = {"estado": "no_aplica", "motivo": "editado a mano"} if k in tocado_a_mano else None
        if d is None:
            prueba = a_mano or _aplicar_deberia([{**p} for p in ps], f, crudo, ids)
            por_k[k] = {"estado": "pendiente", "aplica": "aplica" if prueba["estado"] == "aplicado" else prueba["estado"],
                        **({"motivo": prueba["motivo"]} if "motivo" in prueba else {})}
        elif d["accion"] == "rechazar":
            por_k[k] = {"estado": "rechazado"}
        elif d["accion"] == "editar" and d.get("texto") is None:
            por_k[k] = {"estado": "editado_a_mano"}
        else:
            por_k[k] = a_mano or _aplicar_deberia(ps, f, crudo, ids)
    vivos_ps = [p for p in ps if p["texto"].strip()]
    vivos = {(int(p["cap"]), int(p.get("beat") or 0)) for p in vivos_ps}
    for k, r in por_k.items():
        n = int(str(filas[k]["cap"])[2:])
        if r.get("beats"):
            r["beats_sin_texto"] = [b for b in r["beats"] if (n, b) not in vivos]
        ors = _oraciones_cap(vivos_ps, n)
        actuales: list[int] = []
        for tramo in _tramos(filas[k]) or []:
            j = _ubicar(ors, tramo)
            if j is not None:
                actuales += list(range(j, j + len(tramo)))
        r["oraciones_actuales"] = actuales
    limpios = [{c: v for c, v in p.items() if c != "_i"} for p in vivos_ps]
    return {"parrafos": limpios, "indices": [p["_i"] for p in vivos_ps], "por_k": por_k,
            "pendientes": [k for k, r in por_k.items() if r["estado"] in ("pendiente", "no_aplica")], "cambio": limpios != parrafos}


def guardar_y_aprobar(topic_id: str, decisiones: Any, ediciones: Any, por: str, steps_dir: Path | None = None) -> dict[str, Any]:
    """«Aprobar narración»: `borrador` → 1 `_aplicar` (reconstrucción + juez) → `aprobar_narracion`. Con decisiones pendientes no escribe nada.
    Si el borrador deja el texto igual no reconstruye: el md5 no cambia y el papel sigue vigente."""
    import time

    import fase1_5 as f15
    por = str(por or "").strip()
    if not por:
        raise ValueError("falta quién aprueba")
    c = _carga(topic_id, steps_dir)
    b = borrador(c["parrafos"], cargar_critica(topic_id, steps_dir), decisiones, ediciones)
    if b["pendientes"]:
        raise ValueError(f"falta decidir DEBERÍA {b['pendientes']}: aceptar, editar o rechazar (los que no aplican: rechazar o editar)")
    if b["cambio"]:
        c["parrafos"] = b["parrafos"]
        _aplicar(topic_id, c, steps_dir)
    try:
        ap = f15.aprobar_narracion(topic_id, f"{por} {time.strftime('%Y-%m-%dT%H:%M')}", steps_dir)
    except f15.Parada as e:
        raise ValueError(str(e)) from e
    return {"aprobado": ap, "por_k": b["por_k"], "cambio": b["cambio"]}
