"""
script_engine/m03_imagenes_v3.py — F8 (HANDOFF_F8_imagenes_v3 §1 B–F): imágenes v3 sobre el camino seedream de m03.

Solo actúa cuando el guion es v3 (hay escaleta: `01a_escaleta.json` + `01b_narracion_v3.json` en los pasos del topic,
o `topic["escaleta"]`). Sin escaleta (guion v2), `load_beats` devuelve None y m03 sale byte-idéntico.

    B  ancla por beat     el plan de anclas no se toca; cada imagen hereda el BEAT del párrafo donde cae su ancla y el
                          sujeto visual sale de su `imagen_sensorial` (la narración aporta lugar, época y detalle). Cada
                          beat del cap recibe ≥ 1 imagen; el del pico, 2, una de ellas la más cerrada del cap.
    C  estilo             «Grainy 35mm documentary photograph, <año>, …» al PRINCIPIO del prompt y abreviado al final.
    D  composición        motivos (máx. 2 por video salvo que el beat los nombre), manos nunca sujeto ni primer plano,
                          sin macro facial ni clichés de cara, sin conteos exactos ni izquierda/derecha, ≤ 25 % de
                          humanos en plano medio, ≥ 1 establecimiento/exterior por cap.
    E  sensible           cuerpos ≤ 2 por video, nunca en el cap 1 ni candidatos a miniatura, siempre parcialmente
                          ocultos; palabras prohibidas; menores sin daño; flag `sensible` por imagen.
    F  re-encuadre        cuántos planos pide la duración por encima del tope de fotos → propuestas inertes
                          (`reencuadres_propuestos`): fase2a no arma clips (los arma fase2b, frenado).
Funciones puras (testeables sin LLM); m03_visual las llama.
"""
from __future__ import annotations

import json
import re
from collections import Counter
from pathlib import Path
from typing import Any

# ═══════════════════════════════════════════════════════════════
#  B — beats de la escaleta por cap
# ═══════════════════════════════════════════════════════════════

BEAT_KEYS = ("n", "cap", "funcion", "emocion", "intensidad", "dato_central", "imagen_sensorial")


def load_beats(topic: dict, steps_dir: Path | None = None) -> dict[int, list[dict]] | None:
    """{cap: [beat + "parrafos": [texto…]]} desde la escaleta del topic, o None si el guion no es v3."""
    esc = topic.get("escaleta")
    parrafos = topic.get("parrafos_v3")
    tid = topic.get("id") or topic.get("topic_id")
    if esc is None and steps_dir is not None and tid:
        f = steps_dir / tid / "01a_escaleta.json"
        if f.exists():
            esc = json.loads(f.read_text(encoding="utf-8"))
    if parrafos is None and steps_dir is not None and tid:
        f = steps_dir / tid / "01b_narracion_v3.json"
        if f.exists():
            parrafos = json.loads(f.read_text(encoding="utf-8")).get("parrafos")
    if not esc or not esc.get("beats"):
        return None
    pool = topic.get("evidence_pool") or {}
    from script_engine import evidence as ev
    its = ev.items(pool) if pool else {}
    out: dict[int, list[dict]] = {}
    pico = int((esc.get("pico") or {}).get("beat") or 0)
    for b in esc["beats"]:
        d = {k: b.get(k) for k in BEAT_KEYS}
        d["pico"] = int(b.get("n") or 0) == pico
        it = its.get(str(b.get("dato_central") or ""))
        d["dato_texto"] = ev.text_of(it) if it else ""
        d["fecha"] = (ev.item_date(it) or "") if it else ""
        d["parrafos"] = [p.get("texto") or "" for p in parrafos or [] if p.get("beat") == b.get("n")]
        d["escala"] = beat_scale(d)                                   # F8b §2.4
        out.setdefault(int(b["cap"]), []).append(d)
    return out


def topic_year(topic: dict, beats: dict[int, list[dict]] | None) -> str:
    """El año de la historia para el estilo: el más común en las fechas de los datos centrales; si no, el primer año
    del canon de época."""
    years = [b["fecha"][:4] for bs in (beats or {}).values() for b in bs if re.match(r"\d{4}", b.get("fecha") or "")]
    if years:
        return Counter(years).most_common(1)[0][0]
    era = topic.get("era_visual_canon") or {}
    m = re.search(r"(1[5-9]\d{2}|20\d{2})", f"{era.get('spans') or ''} {era.get('primary_decade') or ''}")
    return m.group(1) if m else ""


def _norm_ws(s: str) -> str:
    return re.sub(r"\s+", " ", (s or "").replace("…", "").replace("...", "")).strip().lower()


def assign_beats(narration: str, anchors: list[str], cap_beats: list[dict]) -> list[dict]:
    """Beat de cada imagen (el párrafo donde cae su ancla) + cobertura: cada beat ≥ 1 imagen; el pico 2, una de ellas
    `cerrada` (la más cerrada del cap). Reasigna solo el SUJETO visual (el ancla y su tiempo no se tocan): una imagen de
    un beat con varias pasa al beat vecino que quedó sin ninguna. Devuelve [{"beat": n, "cerrada": bool}] por imagen."""
    n = len(anchors)
    if not n or not cap_beats:
        return [{"beat": None, "cerrada": False} for _ in anchors]
    text = _norm_ws(narration)
    # tramo de cada beat en la narración del cap (por sus párrafos, en orden)
    spans: list[tuple[int, int, int]] = []
    pos = 0
    for b in cap_beats:
        st = None
        for p in b.get("parrafos") or []:
            k = text.find(_norm_ws(p)[:60], pos)
            if k >= 0:
                st = k if st is None else st
                pos = k + len(_norm_ws(p))
        spans.append((b["n"], st if st is not None else -1, pos))
    known = [s for s in spans if s[1] >= 0]
    out = []
    last = 0
    for a in anchors:
        k = text.find(_norm_ws(a)[:80], last)
        if k < 0:
            k = text.find(_norm_ws(a)[:30])
        if k >= 0:
            last = k
        beat = None
        if known and k >= 0:
            beat = max((s for s in known if s[1] <= k), key=lambda s: s[1], default=known[0])[0]
        out.append({"beat": beat, "cerrada": False})
    # sin posición (párrafos no encontrados): reparto proporcional en orden
    if any(o["beat"] is None for o in out):
        order = [b["n"] for b in cap_beats]
        for i, o in enumerate(out):
            if o["beat"] is None:
                o["beat"] = order[min(len(order) - 1, i * len(order) // n)]
    order = [b["n"] for b in cap_beats]

    def _count(bn: int) -> int:
        return sum(1 for o in out if o["beat"] == bn)

    def _take_for(bn: int) -> bool:
        """Pasa a `bn` una imagen del beat vecino más cargado (la más cercana a su tramo)."""
        k = order.index(bn)
        donors = sorted((d for d in order if d != bn and _count(d) > (2 if _is_pico(d) else 1)),
                        key=lambda d: (abs(order.index(d) - k), -_count(d)))
        if not donors:
            return False
        d = donors[0]
        idx = [i for i, o in enumerate(out) if o["beat"] == d]
        i = idx[0] if order.index(d) > k else idx[-1]          # la del borde que toca al beat
        out[i]["beat"] = bn
        return True

    def _is_pico(bn: int) -> bool:
        return any(b["n"] == bn and b.get("pico") for b in cap_beats)

    for bn in order:
        if _count(bn) == 0:
            _take_for(bn)
    for b in cap_beats:
        if b.get("pico"):
            if _count(b["n"]) < 2:
                _take_for(b["n"])
            idx = [i for i, o in enumerate(out) if o["beat"] == b["n"]]
            if idx:
                out[idx[-1] if len(idx) > 1 else idx[0]]["cerrada"] = True
    # la reasignación puede dejar el orden de beats salteado; se re-ordena (las anclas van en orden de narración)
    seq = sorted((o["beat"] for o in out), key=order.index)
    cer = [o["cerrada"] for o in out]
    return [{"beat": bn, "cerrada": c} for bn, c in zip(seq, cer)]


def beats_block(cap_beats: list[dict], assign: list[dict], bullets: list | None = None, lang: str | None = None) -> str:
    """Bloque del user-prompt de slots: qué se VE en cada imagen (la imagen sensorial del beat), en el idioma del guion;
    los slots se escriben en inglés."""
    by_n = {b["n"]: b for b in cap_beats}
    lines = []
    for i, a in enumerate(assign, start=1):
        b = by_n.get(a["beat"]) or {}
        extra = (" · PEAK beat — this is the TIGHTEST framing of the cap, at HUMAN scale (a person in posture or a "
                 "human trace; never an object or a weapon in detail, never a face macro, never hands)"
                 if a["cerrada"] else "")
        if b.get("escala"):
            extra += " · SCALE: hundreds of people, filling the frame (never a handful of figures)"
        if WEAPON_ES.search(b.get("imagen_sensorial") or ""):
            # F10 §0.2 (Omar): la imagen es SIEMPRE la reacción de las víctimas o del testigo; el tirador no aparece
            # nunca, ni lejos
            extra += (" · WEAPON BEAT: show ONLY the reaction of the victims or the witness (people crouching in the "
                      "water, faces turned up, a witness watching from a terrace); the shooter and the weapon NEVER "
                      "appear, not even far away or as a silhouette")
        lines.append(f"  [{i}] beat {a['beat']} · {b.get('funcion') or ''} · emotion {b.get('emocion') or ''} · "
                     f"intensity {b.get('intensidad') or ''}{extra}\n      SEEN: «{b.get('imagen_sensorial') or ''}»")
    ctx = ""
    if bullets:
        ctx = "\nCap bullets (context only):\n" + "\n".join(f"  - {x}" for x in bullets)
    if lang:
        ctx += (f"\nLanguage of the place of the event (for any text in the image, max 3 words, only if the beat "
                f"demands it): {LANG_NAMES.get(lang, lang)}.")
    return f"""
═══════════════════════════════════════════════════
VISUAL SUBJECT PER IMAGE — decided by the scriptwriter (MANDATORY)
═══════════════════════════════════════════════════
For each item, the SUBJECT, ACTION and PROPS come from what the beat says is SEEN (its sensory image, in Spanish:
translate it). The narration fragment only adds place, period and detail. Two images of the same beat show two
DIFFERENT parts or distances of that sensory image (never the same frame twice).
{chr(10).join(lines)}{ctx}
"""


# ═══════════════════════════════════════════════════════════════
#  C — estilo al principio y al final
# ═══════════════════════════════════════════════════════════════

def style_head(year: str) -> str:
    y = f", {year}" if year else ""
    return (f"Grainy 35mm documentary photograph{y}, dark-history realism, muted colors, visible film grain, "
            f"slightly underexposed.")


STYLE_TAIL = "35mm film grain, muted documentary colors."


def wrap_style(prose: str, year: str) -> str:
    """Estilo primero y repetido abreviado al final (con el estilo en cola, Seedream devuelve set de película)."""
    p = (prose or "").strip()
    head = style_head(year)
    if p.startswith(head[:30]):
        return p
    return f"{head} {p} {STYLE_TAIL}".strip()


# ═══════════════════════════════════════════════════════════════
#  D/E — reglas sobre el prompt (validador determinista) + instrucción al director
# ═══════════════════════════════════════════════════════════════

# motivo → patrón (inglés: los prompts van en inglés; español: la imagen sensorial del beat)
MOTIFS: dict[str, str] = {
    "pasillo": r"\b(corridor|hallway|tier walkway|cellblock walkway)s?\b|\bpasillos?\b",
    "podio/sheriff": r"\b(podium|lectern|sheriff)\b|\b(podio|sheriff|atril)\b",
    "manos en barrotes": r"\bhands?\b[^.]{0,40}\b(bars?|grille?s?)\b|\bmanos?\b[^.]{0,40}\bbarrotes\b",
    "generador": r"\bgenerators?\b|\bgeneradore?s?\b",
    "calendario": r"\bcalendars?\b|\bcalendarios?\b",
    "documento en escritorio": r"\b(documents?|papers?|files?|ledger|report)\b[^.]{0,40}\b(desk|table)\b"
                               r"|\b(documentos?|papeles|expediente)\b[^.]{0,40}\b(escritorio|mesa)\b",
    "puerta cerrada": r"\b(closed|locked|shut|sealed)\s+(steel\s+|iron\s+|metal\s+|cell\s+)*doors?\b"
                      r"|\bpuertas?\s+(cerradas?|trabadas?|con llave)\b",
}
MOTIF_MAX = 2

# manos y caras (D2, D3): frases prohibidas
HANDS_FACE = [
    r"close[- ]?(?:up|shot)\s+of\s+(?:\w+\s+){0,2}hands?", r"\bknuckles?\b", r"\bfingers?\s+(?:gripping|clutching|curled)",
    r"\bjaw\s+(?:clenched|tight|set)\b", r"\bclenched\s+jaw\b", r"\blips\s+pressed\b", r"\bpupils?\s+dilated\b",
    r"\bdilated\s+pupils?\b", r"\bwhites\s+of\s+(?:his|her|their|the)\s+eyes\b", r"\bwhites\s+visible\b",
    r"\btrembl\w*", r"\bextreme\s+close[- ]?up\s+of\s+(?:\w+\s+){0,2}(?:face|eyes)\b",
    # F8b §2.5: sinónimos que salieron en el humo
    r"\bhollow(?:ed)?(?:,?\s+\w+)?\s+eyes\b", r"\bcracked\s+lips\b", r"\bfacial\s+muscles\b",
    r"\btense[d]?\s+(?:facial\s+)?muscles\b", r"\beyes\s+squeezed\s+shut\b", r"\bgrimac\w*", r"\bveins?\b",
    r"\bmacro\b[^.]{0,30}\b(?:face|eyes?|skin)\b", r"\b(?:face|eyes)\s+fill(?:s|ing)?\s+the\s+frame\b",
    # manos en un plano cerrado (sujeto o primer plano), aunque no se nombre el plano de las manos
    r"\b(?:close|detail)(?:[- ]up)?\s+(?:shot|view|framing)\b[^.]*\bhands?\b",
    r"\b(?:cupped|bare|bloodied|outstretched)\s+hands\b",
]
# F8b §2.1: armas y disparos. Nunca fogonazo, nunca arma en primera persona ni encuadre desde el tirador: armas solo en
# reposo, a distancia, de espaldas; la cámara está con las víctimas o con el testigo
WEAPONS = [r"\bmuzzle[- ]?flash\w*", r"\bfiring\b", r"\bfires?\s+(?:a|the|his|her|their)?\s*(?:shot|round|rifle|gun)s?\b",
           r"\bdischarg\w+", r"\b(?:gun|rifle|weapon|pistol|shotgun)'?s?\s+barrel\b",
           r"\bbarrel\s+of\s+(?:a|the|his|her)\s+(?:gun|rifle|weapon|pistol)\b", r"\bfirst[- ]person\b", r"\bPOV\b",
           r"\bpoint[- ]of[- ]view\b", r"\baim(?:s|ed|ing)?\b[^.]{0,30}\b(?:at|toward|towards)\s+(?:the\s+)?"
           r"(?:camera|viewer|lens)\b", r"\bscope\b", r"\bcrosshairs?\b", r"\bgunshots?\b", r"\bbullets?\b",
           r"\b(?:over|from)\s+(?:the\s+)?(?:shoulder|position)\s+of\s+(?:the\s+)?(?:shooter|sniper|gunman)\b",
           # un arma apuntando (a quien sea) no está en reposo; tampoco un tirador tendido con el arma
           r"\baim(?:s|ed|ing)\b", r"\bprone\b[^.]{0,60}\b(?:rifle|gun|weapon)s?\b",
           r"\b(?:rifle|gun|weapon)s?\s+(?:raised|leveled|levelled|pointed|trained)\b"]

# la frase de manos que se saca de la frase-sujeto en el backstop («… held in his hands», «with cupped hands»)
HANDS_PHRASE = (r",?\s*(?:\w+\s+){0,2}(?:in|with|from|between|by)\s+(?:his|her|their|the|both|two)?\s*"
                r"(?:cupped\s+|bare\s+|trembling\s+)?hands?\b")
# sensible (E): palabras que no van nunca
FORBIDDEN = [r"\bblood\w*", r"\bbleed\w*", r"\bwounds?\b", r"\bwounded\b", r"\bgore\b", r"\bgory\b", r"\bmutilat\w*",
             r"\bdismember\w*", r"\brope\s+around\s+(?:his|her|the|a)?\s*neck\b", r"\bnoose\b", r"\bhanged\s+body\b"]
MINOR = r"\b(child|children|kid|kids|boy|girl|toddler|baby|infant|teen(?:ager)?s?|minor|juvenile)\b"
HARM = r"\b(beaten|hurt|injur\w*|dead|dying|drown\w*|burn\w*|shot|kill\w*|corpse|body|bodies|abuse\w*|struck)\b"
BODY = (r"\b(corpses?|cadavers?|dead\s+(?:body|bodies|man|men|woman|women|inmates?|prisoners?)|lifeless|"
        r"(?:floating|drowned|bloated)\s+bod(?:y|ies)|body\s+bags?|human\s+remains)\b")
# «body»/«bodies» solo cuenta como cuerpo con una palabra de muerte en la misma oración («the body of one of the men»
# no lo es)
BODY_WORD = r"\bbod(?:y|ies)\b"
DEATH = r"\b(dead|death|died|deceased|lifeless|drown\w*|decompos\w*|corpse\w*|remains|floating\s+face[- ]?down)\b"
HUMAN = r"\b(man|men|woman|women|person|people|inmates?|prisoners?|guards?|officers?|deputy|deputies|figures?|" \
        r"crowd|boy|girl|survivors?|workers?|firefighters?|families|mother|father|teen\w*)\b"
COUNT_WORDS = "two|three|four|five|six|seven|eight|nine|ten|eleven|twelve|a dozen"
COUNT_RE = re.compile(rf"\b(?:exactly\s+)?({COUNT_WORDS})\s+(?=(?:\w+\s+){{0,2}}{HUMAN[2:]})", re.I)
ART_COUNT_RE = re.compile(rf"\b(?:(the|a|an)\s+)?{COUNT_RE.pattern[2:]}", re.I)
LR_RE = re.compile(r"\b(?:on|to|at|from)\s+the\s+(?:far\s+)?(?:left|right)(?:\s+side)?(?:\s+of\s+the\s+frame)?\b"
                   r"|\b(?:left|right)[- ](?:hand|side|third|edge|foreground|background)\b"
                   r"|\b(?:in\s+the\s+)?(?:left|right)\s+(?:of\s+the\s+frame|corner)\b", re.I)


def motifs_of(text: str) -> set[str]:
    t = text or ""
    return {k for k, p in MOTIFS.items() if re.search(p, t, re.I)}


def problems(prose: str, shot_scale: str | None = None) -> list[tuple[str, str]]:
    """[(tipo, fragmento)] de lo que el prompt no puede llevar: manos/cara (D2–D3), palabras prohibidas (E), menor en
    daño (E), conteos exactos o izquierda/derecha (D4). En un plano close/detail las manos no aparecen (serían sujeto o
    primer plano)."""
    out = []
    if shot_scale in ("close", "detail"):
        m = re.search(r"\bhands?\b", prose, re.I)
        if m:
            out.append(("manos/cara", f"manos en plano {shot_scale}"))
    for p in HANDS_FACE:
        m = re.search(p, prose, re.I)
        if m:
            out.append(("manos/cara", m.group(0)))
    for p in FORBIDDEN:
        m = re.search(p, prose, re.I)
        if m:
            out.append(("prohibida", m.group(0)))
    for p in WEAPONS:
        m = re.search(p, prose, re.I)
        if m:
            out.append(("arma", m.group(0)))
    for s in re.split(r"(?<=[.!?])\s+", prose):
        if re.search(MINOR, s, re.I) and re.search(HARM, s, re.I):
            out.append(("menor en daño", s[:80]))
    for m in COUNT_RE.finditer(prose):
        out.append(("conteo", m.group(0).strip()))
    for m in LR_RE.finditer(prose):
        out.append(("izquierda/derecha", m.group(0)))
    return out


def fix_counts_lr(prose: str) -> str:
    """D4 determinista: «three inmates» → «a few inmates»; «on the left» → «to one side». Un artículo delante de la cifra
    se va con ella («The two men» → «A couple of men»). Las cifras del candado van en numerales, no en palabras: no se
    tocan."""
    def _cnt(m: re.Match) -> str:
        w = m.group(2).lower()
        out = "a couple of " if w == "two" else "a few " if w in ("three", "four") else "several "
        return out[0].upper() + out[1:] if (m.group(1) or "")[:1].isupper() else out
    # F49: el artículo de antes de la cifra se va con ella («The two men» → «A couple of men», no «The a couple of»)
    p = ART_COUNT_RE.sub(_cnt, prose)
    p = LR_RE.sub(lambda m: "to one side" if m.group(0).lower().startswith(("on", "to", "at", "from")) else "side", p)
    return re.sub(r"\s{2,}", " ", p)


def scrub_sentence_problems(prose: str, shot_scale: str | None = None) -> str:
    """Último recurso (backstop): saca la frase que lleva manos/cara, palabra prohibida o menor en daño (y, en un plano
    close/detail, la que nombra manos); si es la única, saca solo el fragmento."""
    bad = [re.compile(p, re.I) for p in HANDS_FACE + FORBIDDEN + WEAPONS
           + ([r"\bhands?\b"] if shot_scale in ("close", "detail") else [])]
    ss = re.split(r"(?<=[.!?])\s+", prose)
    keep = []
    for k, s in enumerate(ss):
        hit = any(r.search(s) for r in bad) or (re.search(MINOR, s, re.I) and re.search(HARM, s, re.I))
        if not hit:
            keep.append(s)
        elif k == 0:                                 # la primera frase es el sujeto: se saca el fragmento, no la frase
            for p in [HANDS_PHRASE] + [x for x in HANDS_FACE + WEAPONS if "[^.]*" not in x and "{0,30}" not in x] \
                    + FORBIDDEN:
                s = re.sub(p, "", s, flags=re.I)
            s = re.sub(r"\s*,(\s*,)+", ",", re.sub(r"\s{2,}", " ", s)).replace(" ,", ",").strip()
            keep.append(s)
    if not keep:
        out = prose
        for r in bad:
            out = r.sub("", out)
        return re.sub(r"\s{2,}", " ", out).strip()
    return " ".join(keep)


def scrub_slots(slots: dict) -> list[str]:
    """In place: saca de los slots de texto las frases con clichés de cara/manos o palabras prohibidas ANTES de tejer (si
    no, el fluidificador las copia). Devuelve lo que sacó."""
    gone = []
    bad = [re.compile(p, re.I) for p in HANDS_FACE + FORBIDDEN + WEAPONS]
    for k, v in list(slots.items()):
        if not isinstance(v, str) or not v.strip():
            continue
        parts = re.split(r"(?<=[,;.])\s+", v)
        kept = [x for x in parts if not any(r.search(x) for r in bad)]
        if len(kept) != len(parts):
            gone += [f"{k}: {x}" for x in parts if x not in kept]
            slots[k] = " ".join(kept).strip(" ,;") or ("" if k not in ("subject",) else v)
    return gone


WEAPON_ES = re.compile(r"\b(rifles?|fusil\w*|disparo\w*|dispar\w+|fogonazo\w*|francotirador\w*|armas?|balas?|"
                       r"tiros?|escopeta\w*|pistola\w*)\b", re.I)
SHOOTER_EN = re.compile(r"\b(snipers?|shooters?|gunm[ae]n|marksm[ae]n|rifles?|guns?|pistols?|shotguns?|weapons?)\b", re.I)


def weapon_subject(item: dict) -> bool:
    """§2.1: el tirador o el arma como sujeto de la imagen (la cámara tiene que estar con las víctimas o el testigo)."""
    return bool(SHOOTER_EN.search(f"{item.get('subject') or ''} {item.get('action') or ''}"))


TRACE = (r"\b(shoes?|boots?|sneakers?|belongings|clothes|clothing|jumpsuits?|blankets?|mattress(?:es)?|cots?|bags?|"
         r"letters?|photographs?|tray|cups?|toys?|footprints?|handprints?|bunks?|beds?)\b")


def human_scale(item: dict) -> bool:
    """§2.2: el pico es a escala humana: una persona (o un grupo) o un rastro humano; nunca un objeto ni un arma solos."""
    subj = f"{item.get('subject') or ''} {item.get('props_detail') or ''}"
    weapon = re.search(r"\b(rifle|gun|pistol|weapon|shotgun|barrel)\b", item.get("subject") or "", re.I)
    return not weapon and bool(re.search(HUMAN, subj, re.I) or re.search(TRACE, subj, re.I))


SCALE_ES = re.compile(r"\b(cientos|centenares|miles|millares|multitud|muchedumbre|masiv\w+|interminable|hacinad\w+|"
                      r"amontonad\w+|repleto|repleta)\b", re.I)
PEOPLE_ES = re.compile(r"\b(hombres|mujeres|presos|reclusos|internos|personas|gente|familias|j[oó]venes|chicos|"
                       r"evacuados|sobrevivientes|v[ií]ctimas|fila|filas)\b", re.I)


def beat_scale(beat: dict) -> bool:
    """§2.4: el beat pide escala de masa (cientos/miles de personas) si su imagen sensorial nombra gente en plural y la
    imagen o el dato central dicen cientos/miles, o el dato trae una cifra de 100 o más."""
    img = beat.get("imagen_sensorial") or ""
    dato = beat.get("dato_texto") or ""
    if not PEOPLE_ES.search(img):
        return False
    big = any(int(n.replace(",", "").replace(".", "")) >= 100 for n in re.findall(r"\d[\d.,]*\d|\d", dato)
              if n.replace(",", "").replace(".", "").isdigit())
    return bool(SCALE_ES.search(img) or SCALE_ES.search(dato) or big)


SCALE_EN = re.compile(r"\b(hundreds|thousands|crowd(?:ed|s)?|masses|mass of|packed|filling the frame|sea of)\b", re.I)


def fix_scale(prose: str) -> str:
    """§2.4: en un beat de masa, «a few/several inmates» → «hundreds of inmates» (nunca 5–7 figuras)."""
    return re.sub(rf"\b(?:a few|several|a couple of|a handful of|a small group of|a group of)\s+(?=(?:\w+\s+){{0,2}}"
                  rf"{HUMAN[2:]})", "hundreds of ", prose, flags=re.I)


LANG_NAMES = {"en": "English", "es": "Spanish", "it": "Italian", "fr": "French", "pt": "Portuguese", "de": "German"}
SPANISH_WORDS = re.compile(r"[ñáéíóú¿¡]|\b(de|del|la|los|las|el|sin|registro|desconocido|desaparecido|muertos?|"
                           r"c[aá]rcel|prisi[oó]n|lista|nombres?|estado|atendido|pr[oó]fugo)\b", re.I)
NO_TEXT = "No readable text, no signage, no labels."
TEXT_MAX_WORDS = 3


def place_language(topic: dict) -> str:
    """Código del idioma del lugar del evento: el más común entre los documentos del pool v3 (los locales); si no hay,
    `idioma_local` del topic; si no, inglés."""
    docs = ((topic.get("evidence_pool") or {}).get("_research_v3") or {}).get("documentos") or []
    langs = [d.get("idioma") for d in docs if d.get("idioma") in LANG_NAMES]
    if langs:
        return Counter(langs).most_common(1)[0][0]
    loc = (topic.get("idioma_local") or "").lower()
    for code, name in LANG_NAMES.items():
        if loc.startswith(code) or name.lower()[:5] in loc or {"es": "españ", "it": "italia", "en": "ingl"}.get(code, "#") in loc:
            return code
    return "en"


def fix_text_slot(item: dict, lang: str) -> str | None:
    """§2.3: texto en imagen solo si el beat lo exige; en el idioma del lugar (nunca español en documentos de otro país),
    ≤ 3 palabras. In place sobre `text_in_image`; marca `texto_en_imagen`. Devuelve el motivo si sacó o recortó."""
    tii = item.get("text_in_image") or {}
    why = None
    if tii.get("present"):
        txt = str(tii.get("text") or "").strip()
        if lang != "es" and SPANISH_WORDS.search(txt):
            tii["present"], why = False, f"texto en español en un lugar de habla {LANG_NAMES.get(lang, lang)}: «{txt}»"
        elif len(txt.split()) > TEXT_MAX_WORDS:
            tii["text"] = " ".join(txt.split()[:TEXT_MAX_WORDS])
            why = f"texto recortado a {TEXT_MAX_WORDS} palabras: «{txt}»"
    item["text_in_image"] = tii
    item["texto_en_imagen"] = bool(tii.get("present"))
    return why


def is_body(text: str) -> bool:
    if re.search(BODY, text or "", re.I):
        return True
    return any(re.search(BODY_WORD, s, re.I) and re.search(DEATH, s, re.I)
               for s in re.split(r"(?<=[.!?])\s+", text or ""))


def human_medium(item: dict) -> bool:
    """Humano en plano medio (D5): shot_scale medium/close con una persona como sujeto."""
    return (item.get("shot_scale") in ("medium", "close")) and bool(re.search(HUMAN, item.get("subject") or "", re.I))


def establishing(item: dict) -> bool:
    return item.get("subject_ref") == "establishing_shot" or item.get("shot_scale") == "extreme_wide" or \
        (item.get("shot_scale") == "wide" and bool(re.search(r"\b(exterior|outside|aerial|facade|from above|skyline|"
                                                              r"street|overpass|levee|landscape)\b",
                                                              f"{item.get('setting') or ''} {item.get('camera_angle') or ''}",
                                                              re.I)))


# instrucción para el director (reemplaza los ejemplos de cara de la doctrina R6 en el camino v3)
DOCTRINE_R6_V3 = """PHYSICAL TRANSLATION — THE ENGINE IS A PAINTER, NOT AN ACTOR (R6, v3):
- Internal states DO NOT render. Never write a bare abstract emotion ("fear", "terror", "dread", "panic", "despair").
- Emotion is carried by POSTURE, LIGHT and ACTION, never by a face macro: a body slumped against a wall, shoulders
  drawn up, a figure turned away toward a window, a group pressed together in a doorway, harsh light from one high
  window, a figure small in a large dark space.
- FORBIDDEN face/hand clichés (they render as stock acting): "jaw clenched", "lips pressed thin", "pupils dilated",
  "whites of his eyes", "knuckles white", "trembling", any face macro or extreme close-up of a face."""

COMPOSITION_RULES_V3 = """COMPOSITION RULES (v3 — HARD, the prompt is validated after you):
1. HANDS are never the subject and never in the foreground: only within a medium shot or out of focus. Never "close shot
   of hands", "knuckles", "fingers gripping".
2. FACES: no facial macro, no extreme close-up of a face. Emotion through posture, light and action.
3. NO exact counts of people and NO left/right as a requirement ("three men on the left"): use absolute references
   ("toward the window", "beside the podium", "a few men").
4. At most a QUARTER of the images show a person in medium shot; prefer places, objects, distance and silhouettes.
   Every cap has at least ONE establishing / exterior image (the place seen from outside or from above).
5. WEAPONS: never a muzzle flash, never a weapon in first person, never framed from the shooter. When a beat is
   about shooting, the SHOOTER NEVER APPEARS (not even far away or as a silhouette): the image is the REACTION of
   the victims or the witness (crouching in the water, faces turned up, watching from a terrace).
6. The PEAK image is at HUMAN scale: a person, a group or a human trace — never an object or a weapon in detail.
7. NO readable text by default (no signage, no labels). Only if the beat demands it: in the LANGUAGE OF THE PLACE of
   the event (given in the user prompt), at most 3 words. Never Spanish on documents of another country.
8. SCALE from the research: if the beat speaks of hundreds or thousands of people, write "hundreds of …, filling the
   frame" — never five or seven figures for an endless line.
9. Recurring motifs are rationed across the WHOLE video (corridor, podium/sheriff, hands on bars, generator, calendar,
   document on a desk, closed door): use one only when THIS beat's sensory image names it.
SENSITIVE CONTENT (YouTube, HARD):
10. Dead bodies: only if the beat demands it, ALWAYS partially hidden (by water, shadow or distance), never a face, never
   a close shot. Never in the hook.
11. NEVER write: blood, wound, gore, mutilated, dismembered, rope around a neck (a hanging only as a shadow or feet).
12. Minors: only if the research documents them, never in a situation of physical harm; prefer their objects (shoes, a
   tray) to their bodies."""


def video_audit(caps: list[list[dict]], beats_by_cap: dict[int, list[dict]] | None = None) -> dict[str, Any]:
    """Auditoría del video entero (D1, D5, E) sobre los ítems finales de cada cap (en orden de cap). Cada ítem: dict
    con slots + `prompt`. Devuelve {"motivos": {motivo: [(cap, i)]}, "exceso_motivos": [(cap, i, motivo)],
    "cuerpos": [(cap, i)], "exceso_cuerpos": [(cap, i)], "humano_medio": [(cap, i)], "exceso_humano_medio": [...],
    "caps_sin_establecimiento": [cap]}. Un motivo que la imagen sensorial del beat nombra no cuenta para el tope."""
    beats_by_cap = beats_by_cap or {}
    seen: dict[str, list[tuple[int, int]]] = {}
    exceso_m, cuerpos, hm, sin_est = [], [], [], []
    total = 0
    for cap, items in enumerate(caps, start=1):
        bs = {b["n"]: b for b in beats_by_cap.get(cap) or []}
        if items and not any(establishing(it) for it in items):
            sin_est.append(cap)
        for i, it in enumerate(items):
            total += 1
            text = it.get("prompt") or ""
            sens = (bs.get(it.get("beat")) or {}).get("imagen_sensorial") or ""
            demanded = motifs_of(sens)
            for m in motifs_of(text):
                seen.setdefault(m, []).append((cap, i))
                if m not in demanded and len([x for x in seen[m]]) > MOTIF_MAX:
                    exceso_m.append((cap, i, m))
            if is_body(text):
                cuerpos.append((cap, i))
            if human_medium(it):
                hm.append((cap, i))
    exceso_c = [c for c in cuerpos if c[0] == 1] + [c for c in cuerpos if c[0] != 1][2:]
    lim = int(0.25 * total)
    return {"total": total, "motivos": seen, "exceso_motivos": exceso_m, "cuerpos": cuerpos,
            "exceso_cuerpos": exceso_c, "humano_medio": hm, "exceso_humano_medio": hm[lim:] if len(hm) > lim else [],
            "caps_sin_establecimiento": sin_est}


# ═══════════════════════════════════════════════════════════════
#  F — re-encuadre (propuesta inerte)
# ═══════════════════════════════════════════════════════════════

def reencuadres(n_pedidas: int, n_fotos: int, rank_order: list[int]) -> list[dict]:
    """Cuando la duración pide más planos que el tope de fotos: un plano extra desde una foto ya hecha (otro recorte:
    zoom 1.3–1.6 sobre el tercio opuesto, otro movimiento). `rank_order` = índices de las fotos, las mejores primero."""
    k = max(0, n_pedidas - n_fotos)
    out = []
    for j, idx in enumerate(rank_order[:k]):
        out.append({"reencuadre_de": idx, "zoom": round(1.3 + 0.3 * (j % 2), 2), "tercio": "opuesto",
                    "movimiento": "pan" if j % 2 else "push_in"})
    return out
