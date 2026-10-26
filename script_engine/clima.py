"""
script_engine/clima.py — F36 §A: los sellos de clima (movido de gfx_rotulista sin cambios; `peak_word` viene de
gfx_peak). Los momentos candidatos (la palabra de más peso de un mood en cada oración y la del pico), la palabra de
clima del vocabulario `sellos_clima` del perfil (hoy la elige Gemini Flash con `SELLO_CLIMA_PROMPT`) y el reparto
(`sellos_por_tema`: un sello por beat, nunca sobre un texto ni cruzando el corte).
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path
from typing import Any, Callable

from script_engine import evidence as ev
from script_engine.rotulista_colocar import _cubre, unidades
from script_engine.voz_utils import _raiz_en


def _sello_queda(e: dict, plan: dict) -> bool:
    """El sello que sobrevive al realizador (solo el de la palabra del pico)."""
    pw = str((plan.get("pico") or {}).get("word") or "").lower().strip(".,;:")
    return bool(e.get("peak_word")) or (bool(pw) and str(e.get("word", "")).lower().strip(".,;:") == pw)


# ═══════════════════════ sellos de clima (F32 §B.6 → F34 §A.4) ═══════════════════════

# el catálogo de Omar (25-10: muerte, agua, veneno…) = los moods del perfil; la tabla da el nombre del tema de cada uno
TEMA_DE_MOOD = {"muerte": "muerte", "agua": "agua", "veneno_enfermedad": "veneno", "fuego": "fuego",
                "oscuridad_encierro": "oscuridad", "radiacion_quimico": "radiación", "frio_abandono": "abandono",
                "silencio": "silencio", "caos_gritos": "caos"}

# F34 §A.4: el prompt literal (una llamada por candidato; el lote = las llamadas del cap, en paralelo)
SELLO_CLIMA_PROMPT = """Elegí UNA palabra de esta lista que nombre el clima de este momento del relato, no lo que se dice: {lista}.
No puede ser una palabra que aparezca en estas oraciones: «{voz_-1}» «{voz_ancla}» «{voz_+1}».
Momento: función del beat «{funcion}»; oración: «{voz_ancla}».
Respondé solo la palabra en mayúsculas, o NINGUNA si ninguna calza."""


def vocabulario_clima() -> list[str]:
    """`sellos_clima` del perfil activo (DECISIONES 2026-10-26 14:22); sin la clave, lista vacía (= sin sellos)."""
    from gfx_config import ACTIVE_PROFILE
    return [str(w).strip().upper() for w in ACTIVE_PROFILE.get("sellos_clima") or [] if str(w).strip()]


def prompt_clima(lista: list[str], prev: str, ancla: str, nxt: str, funcion: str) -> str:
    return (SELLO_CLIMA_PROMPT.replace("{lista}", ", ".join(lista)).replace("{voz_-1}", prev or "—")
            .replace("{voz_ancla}", ancla or "—").replace("{voz_+1}", nxt or "—").replace("{funcion}", funcion or "—"))


def _gemini_clima(prompt: str) -> str:
    from google.genai import types as genai_types
    from config import api, gemini_client
    from cost_tracker import cost_tracker
    resp = gemini_client.models.generate_content(model=api.gemini_model, contents=[prompt],
                                                 config=genai_types.GenerateContentConfig(temperature=0.0))
    cost_tracker.track_gemini_response(resp, api.gemini_model, "gfx_sello_clima")
    return str(resp.text or "")


def elegir_clima(prompts: list[str], cache: Path | None, call: Callable[[str], str] | None = None) -> list[str]:
    """Las respuestas crudas de Gemini Flash a cada prompt (caché por prompt en `cache`; las que faltan, en paralelo)."""
    from concurrent.futures import ThreadPoolExecutor
    hecho: dict[str, str] = {}
    if cache is not None and cache.exists():
        try:
            hecho = json.loads(cache.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            hecho = {}
    clave = {p: hashlib.sha1(p.encode("utf-8")).hexdigest()[:16] for p in prompts}
    faltan = [p for p in dict.fromkeys(prompts) if clave[p] not in hecho]
    fn = call or _gemini_clima

    def una(p: str) -> tuple[str, str]:
        try:
            return clave[p], fn(p)
        except Exception as e:  # noqa: BLE001 — sin respuesta, ese sello no va
            return clave[p], f"ERROR {type(e).__name__}"
    if faltan:
        with ThreadPoolExecutor(max_workers=len(faltan)) as ex:
            for k, r in ex.map(una, faltan):
                if not r.startswith("ERROR"):
                    hecho[k] = r
                else:
                    hecho.setdefault("_errores", []).append(r)  # type: ignore[union-attr]
        if cache is not None:
            cache.write_text(json.dumps(hecho, ensure_ascii=False, indent=1), encoding="utf-8")
    return [str(hecho.get(clave[p], "ERROR")) for p in prompts]


def palabra_clima(resp: str, lista: list[str], oraciones3: list[str]) -> tuple[str | None, str | None]:
    """(palabra de la lista, motivo si no va): la palabra tiene que estar en la lista y no aparecer en las tres oraciones
    (por su raíz de 5 letras: «AVISO» = «avisos»)."""
    r = re.sub(r"[^\wÁÉÍÓÚÑÜáéíóúñü]", "", str(resp or "").strip().split()[0] if str(resp or "").strip() else "")
    if not r or ev.norm(r) == "ninguna":
        return None, "el modelo respondió NINGUNA"
    por_norm = {ev.norm(w): w for w in lista}
    w = por_norm.get(ev.norm(r))
    if w is None:
        return None, f"«{r}» no está en el vocabulario sellos_clima"
    if any(_raiz_en(w, o) for o in oraciones3):
        return None, f"«{w}» aparece en la voz (oración ancla o vecina)"
    return w, None


def sellos_por_tema(plan: dict[str, Any], scenes: list[Any], ent: dict[str, Any], words: list[dict],
                    time_offset: float, moods: dict[str, dict], log: list[str], *, work_dir: Path | None = None,
                    cap: str = "", call: Callable[[str], str] | None = None,
                    juez: Callable[[dict], dict] | None = None, usadas_video: set[str] | None = None
                    ) -> list[dict[str, Any]]:
    """F32 §B.6 → F34 §A.4: los sellos. Los momentos candidatos son los de siempre (en cada oración, la palabra de mayor
    peso de un mood del catálogo, gfx_peak.peak_word, y la palabra del pico), pero el sello ya no dice esa palabra: dice
    una palabra de CLIMA del vocabulario `sellos_clima` del perfil, elegida por Gemini Flash con el prompt literal de
    §A.4; si no está en la lista, aparece en la oración ancla o sus vecinas o ya salió en el cap, no va. Sin
    `sellos_clima` en el perfil, no hay sellos. El filtro (información > clima, §A.3.1): un sello por beat (el reloj, el
    agua y la lupa ya no le cuentan: el sello va en otra oración del beat), nunca en una escena (u oración, en un cap de
    una sola escena) donde hay texto, title card, reloj, agua, lupa u otro sello, y nunca cruzando su corte. Los sellos
    del director (por léxico) salen. Corre después de escena_final.
    F36 §B.2: con `juez` (gfx_critic.estorba), el crítico juzga cada candidato que ya tiene palabra ANTES del reparto: el
    que estorba no ocupa beat ni escena; sus filas quedan en `plan["critico_sellos"]`. §B.3: `usadas_video` = las
    palabras de los sellos de los caps anteriores (`usadas_antes`); una palabra que ya salió en el video o en el cap se
    vuelve a pedir una vez con la lista sin las usadas; si tampoco, ese candidato no lleva sello."""
    from gfx_config import gfx_rules
    from script_engine.gfx_peak import sentences
    from script_engine.gfx_project import scene_at
    filas: list[dict[str, Any]] = []
    if not scenes:
        return filas
    beats = ent["beats"]
    us = unidades(scenes, ent)
    por_oracion = bool(us) and getattr(us[0], "oracion", False)
    del_pico = [e for e in plan.get("emphasis") or [] if _sello_queda(e, plan)][:1]
    director = [e for e in plan.get("emphasis") or [] if e not in del_pico]
    plan["emphasis"] = []
    lista = vocabulario_clima()

    def beat_en(t: float) -> dict | None:
        for b in beats:
            if b["t0"] - 0.3 <= t <= b["t1"]:
                return b
        prev = [b for b in beats if b["t0"] <= t]
        return prev[-1] if prev else None
    ocupa: dict[int, list[str]] = {}

    def marca(a: float, d: float, que: str) -> None:
        for u in (_cubre(us, a, a + d) if por_oracion else [scene_at(us, a)]):
            ocupa.setdefault(u.idx, []).append(que)
    if plan.get("title_card"):
        for s in us:
            if s.start < gfx_rules.title_dur:
                ocupa.setdefault(s.idx, []).append("title card")
    for campo, que in (("callouts", "ficha"), ("archive_clippings", "recorte")):
        for b in plan.get(campo) or []:
            marca(float(b["start"]), float(b.get("duration") or 0.0), que)
    for campo, que in (("quote_card", "cita"), ("count_up", "contador"), ("evidence_zoom", "lupa"),
                       ("water_level", "nivel de agua")):
        if plan.get(campo) and "start" in plan[campo]:
            marca(float(plan[campo]["start"]), float(plan[campo].get("duration") or 0.0), que)
    tk = plan.get("time_ticker")
    if tk:
        for s in us:
            if s.start < float(tk["start"]) + float(tk["duration"]) and s.end > float(tk["start"]):
                ocupa.setdefault(s.idx, []).append("reloj")
    sents = sentences(words, time_offset)
    cands: list[dict[str, Any]] = []
    for e in del_pico:                         # el momento del pico (su palabra, gfx_peak.add_peak_word)
        t = round(float(e["start"]), 3)
        k = next((i for i, s in enumerate(sents) if s["t0"] - 0.05 <= t <= s["t1"] + 0.05), None)
        b = beat_en(t)
        if k is not None and b is not None:
            cands.append({"t": t, "beat": b["n"], "funcion": b["funcion"], "k": k, "word": str(e.get("word", "")),
                          "category": e.get("category"), "weight": float("inf"), "pico": True, "em": e})
    for k, s in enumerate(sents):
        h = peak_word(s, words, moods)
        if h is None:
            continue
        t = round(float(words[h["i"]]["start"]) + time_offset, 3)
        b = beat_en(t)
        if b is None or any(abs(c["t"] - t) < 0.05 for c in cands):   # es el del pico: ya está
            continue
        cands.append({"t": t, "beat": b["n"], "funcion": b["funcion"], "k": k, "category": h["category"],
                      "weight": h["weight"], "pico": False,
                      "word": re.sub(r"^[¿¡\"'«“(]+|[.,;:!?…\"'»”)]+$", "", str(words[h["i"]]["word"]).strip())})
    vistos = {(c["word"].lower(), round(c["t"], 1)) for c in cands}
    for e in director:                     # los del director que no son candidatos del tema (los que sí, se ven abajo)
        if (str(e.get("word", "")).lower(), round(float(e.get("start", 0)), 1)) not in vistos:
            filas.append({"bloque": "emphasis", "texto": e.get("word"), "t": e.get("start"), "accion": "fuera",
                          "regla": "tema", "quien": "catálogo", "motivo": "sello del director por léxico: el sello va "
                          "por el clima de su momento"})
    tres = {c["t"]: [sents[j]["text"] if 0 <= j < len(sents) else "" for j in (c["k"] - 1, c["k"], c["k"] + 1)]
            for c in cands}
    prompts = [prompt_clima(lista, *tres[c["t"]], c["funcion"]) for c in cands] if lista else []
    resp = elegir_clima(prompts, (Path(work_dir) / f"sellos_clima_{cap}.json") if work_dir else None, call) \
        if prompts else []
    for c, r in zip(cands, resp):
        c["respuesta"] = r
    dur = round(float(gfx_rules.mood_dur), 3)
    anim: dict[int, str] = {}
    usadas: set[str] = set()
    antes = set(usadas_video or ())
    cache = (Path(work_dir) / f"sellos_clima_{cap}.json") if work_dir else None
    criticos: list[dict[str, Any]] = []
    for c in sorted(cands, key=lambda c: (c["beat"], not c["pico"], -c["weight"], c["t"])):
        sc = scene_at(scenes, c["t"])
        u = scene_at(us, c["t"])
        tema = TEMA_DE_MOOD.get(str(c["category"]), c["category"])
        # F36 §B.2/§B.3: primero lo que hace al sello (vocabulario, que no cruce el corte, la palabra, que no se repita
        # en el video, el crítico); recién después el reparto (uno por beat, nunca sobre otra cosa). Un sello que no
        # pasa no ocupa su beat ni su escena.
        motivo = ("sin vocabulario `sellos_clima` en el perfil" if not lista else
                  f"cruza el corte de la escena {sc.idx} ({sc.end:.2f} s)" if c["t"] + dur > sc.end + 1e-6 else None)
        palabra, quien, regla = None, "catálogo", "tema"
        if motivo is None:
            quien = "clima"
            palabra, motivo = palabra_clima(c.get("respuesta", ""), lista, tres[c["t"]])
        if palabra and palabra in antes | usadas:          # §B.3: se pide otra de la lista, una vez
            donde = "el video" if palabra in antes else "el cap"
            resto = [w for w in lista if w not in antes | usadas]
            r2 = elegir_clima([prompt_clima(resto, *tres[c["t"]], c["funcion"])], cache, call)[0] if resto else ""
            c["respuesta_2"] = r2
            p2, m2 = palabra_clima(r2, resto, tres[c["t"]]) if resto else (None, "no quedan palabras sin usar")
            palabra, motivo = (p2, None) if p2 else (None, f"«{palabra}» ya salió en {donde} y la segunda respuesta no "
                                                           f"da otra ({m2})")
        base: dict[str, Any] = {}
        if motivo is None:
            m = moods.get(str(c["category"])) or {}
            base = dict(c["em"]) if c["pico"] else {
                "category": c["category"], "layer": m.get("layer"), "icon": None,
                "icon_anim": m.get("icon_anim") or "stamp", "side": getattr(sc, "quiet_side", "right") or "right",
                "stamp": gfx_rules.emphasis_stamp, "weight": c["weight"], **({"sfx": m["sfx"]} if m.get("sfx") else {})}
            base.update({"word": palabra, "start": c["t"], "duration": dur, "por_tema": True, "clima": True,
                         "tema": tema, "palabra_voz": c["word"]})
            base.pop("icon", None)
            if juez is not None:                           # §B.2: el crítico, antes del reparto, solo «¿estorba?»
                row = juez({**base, "sentence_idx": c["k"]})
                criticos.append(row)
                if not row["pasa"]:
                    quien, regla = "crítico", "crítico"
                    motivo = f"«{palabra}» estorba: {row['motivo']} (mira {row['mira']})"
        if motivo is None:
            hay = sorted({q for x in (_cubre(us, c["t"], c["t"] + dur) if por_oracion else [u])
                          for q in ocupa.get(x.idx) or []})
            quien = "catálogo"
            motivo = (f"un sello por beat: el beat {c['beat']} ya tiene {anim[c['beat']]}" if c["beat"] in anim else
                      f"{'la oración' if por_oracion else 'la escena'} {u.idx} ya tiene {', '.join(hay)}" if hay
                      else None)
        if motivo:
            filas.append({"bloque": "emphasis", "texto": c["word"], "t": c["t"], "accion": "fuera", "regla": regla,
                          "quien": quien,
                          "motivo": f"sello {'del pico' if c['pico'] else 'de ' + str(tema)} «{c['word']}»: {motivo}",
                          **({"respuesta": c.get("respuesta")} if c.get("respuesta") else {}),
                          **({"respuesta_2": c["respuesta_2"]} if c.get("respuesta_2") is not None else {})})
            continue
        plan["emphasis"].append(base)
        anim[c["beat"]] = f"el sello «{palabra}»"
        usadas.add(palabra)
        marca(c["t"], dur, "sello")
    plan["critico_sellos"] = criticos
    plan["emphasis"].sort(key=lambda e: e["start"])
    plan["sellos_tema"] = filas
    log.append(f"  sellos de clima: {[(e['word'], e.get('palabra_voz')) for e in plan['emphasis']]} · "
               f"fuera {[(f['texto'], f['motivo']) for f in filas]}")
    return filas


# ═══════════════════════ palabra del momento (gfx_peak.peak_word, F36 §A) ═══════════════════════

def peak_word(peak: dict[str, Any], words: list[dict], moods: dict[str, dict], *, block_category: str | None = None,
              freq: dict[str, int] | None = None) -> dict[str, Any] | None:
    """F4c R3: la palabra de mayor peso (≥ 2) de la frase pico. Empate: la de una categoría que el bloque grande no
    muestra ya (nivel de agua → no otra de agua), después la más rara del video, después la primera."""
    from script_engine.gfx_peak import lexicon_hits, prefer_icon_nouns
    f = freq or {}
    hits = [h for h in prefer_icon_nouns(lexicon_hits(words, moods, peak["idx"]), moods) if h["weight"] >= 2]
    if not hits:
        return None
    return max(hits, key=lambda h: (h["weight"], h["category"] != block_category, -f.get(h["word"], 0), -h["i"]))


def usadas_antes(work_dir: Path, cap_number: int) -> set[str]:
    """F36 §B.3: las palabras de los sellos de clima de los caps anteriores (sus planes resueltos en el work_dir: el
    plan corre en fila, ch01 → ch07)."""
    out: set[str] = set()
    for f in sorted(Path(work_dir).glob("gfx_plan_ch*.resolved.json")):
        m = re.fullmatch(r"gfx_plan_ch(\d+)\.resolved\.json", f.name)
        if not m or int(m.group(1)) >= cap_number:
            continue
        try:
            plan = json.loads(f.read_text(encoding="utf-8")).get("plan") or {}
        except (OSError, ValueError):
            continue
        out |= {str(e.get("word")) for e in plan.get("emphasis") or [] if e.get("clima") and e.get("word")}
    return out
