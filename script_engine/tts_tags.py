"""
script_engine/tts_tags.py — F9 §3.3: etiquetas de ElevenLabs v4 desde el guion (regla determinista).

`narration` queda limpia (subtítulos, candado literal, m03, m05 y forced alignment la siguen leyendo); las etiquetas
van a un campo nuevo `narration_tts` por cap, que solo lee audio_manager para el TTS.

    [long pause]    después de cada cita (la oración con «…») y al cerrar el cap
    [short pause]   antes del pico y después de cada «…» (puntos suspensivos)
    [quietly] / [whispers]   solo en la FRASE DE GOLPE (la última de un párrafo, ≤ 6 palabras, en un beat de intensidad
                    ≥ 4 o en el pico), máx. 2 por cap, nunca en caps `setup`; [whispers] solo en el golpe del pico
    [slowly]        al abrir el gancho y el pico; y al abrir cada párrafo de desarrollo si v4 habla a más de
                    `SLOWLY_WPS` palabras por segundo (medido: ver `voz_v4.wps`)

`transfer_tags` lleva las etiquetas de `narration_tts` al texto NORMALIZADO que se graba (mismas oraciones, en el mismo
orden: el normalizador no parte ni une oraciones); si no coinciden, solo las de párrafo.
"""
from __future__ import annotations

import re

LONG, SHORT, QUIET, WHISPER, SLOW = "[long pause]", "[short pause]", "[quietly]", "[whispers]", "[slowly]"
TAG_RE = re.compile(r"\[(?:long pause|short pause|quietly|whispers|slowly|pause)\]\s*")
GOLPE_MAX_WORDS = 6
GOLPE_MAX_PER_CAP = 2
GOLPE_MIN_INTENSITY = 4
SLOWLY_WPS = 2.4
_SENT = re.compile(r"(?<=[.!?…])[»”\"]?\s+")


def strip_tags(text: str) -> str:
    return re.sub(r"[ \t]{2,}", " ", TAG_RE.sub("", text or "")).replace(" \n", "\n").strip()


def _sentences(par: str) -> list[str]:
    out, pos = [], 0
    for m in _SENT.finditer(par):
        out.append(par[pos:m.start() + len(m.group(0).rstrip())].strip())
        pos = m.end()
    if par[pos:].strip():
        out.append(par[pos:].strip())
    return [s for s in out if s]


def _words(s: str) -> int:
    return len(re.findall(r"[\wáéíóúñü]+", s, re.I))


def tag_cap(text: str, *, intent: str | None, intensities: list[int] | None = None, pico_par: int | None = None,
            slowly_dev: bool = False) -> tuple[str, dict]:
    """Etiqueta UN cap. `intensities[i]` = intensidad del beat del párrafo i; `pico_par` = índice del párrafo del pico
    (None si el pico no está en este cap). Devuelve (texto etiquetado, conteo de etiquetas)."""
    pars = [p.strip() for p in re.split(r"\n\s*\n", text.strip()) if p.strip()]
    intensities = intensities or [0] * len(pars)
    dev = intent not in ("hook", "outro")
    golpes_left = 0 if intent == "setup" else GOLPE_MAX_PER_CAP
    out_pars = []
    for i, par in enumerate(pars):
        ss = _sentences(par)
        pre = []
        if i == pico_par:
            pre += [SHORT, SLOW]
        elif (intent == "hook" and i == 0) or (dev and slowly_dev):
            pre.append(SLOW)
        hot = i == pico_par or (intensities[i] if i < len(intensities) else 0) >= GOLPE_MIN_INTENSITY
        new = []
        for k, s in enumerate(ss):
            t = s
            if "…" in t:
                t = re.sub(r"…(?!\s*\[)", f"… {SHORT}", t)
            if k == len(ss) - 1 and k > 0 and hot and golpes_left and _words(s) <= GOLPE_MAX_WORDS and "«" not in s:
                t = f"{WHISPER if i == pico_par else QUIET} {t}"
                golpes_left -= 1
            if "«" in s or "“" in s:
                t = f"{t} {LONG}"
            new.append(t)
        body = " ".join(new)
        out_pars.append((" ".join(pre) + " " + body).strip() if pre else body)
    tagged = "\n\n".join(out_pars)
    if not tagged.rstrip().endswith(LONG):
        tagged = tagged.rstrip() + f" {LONG}"
    tagged = re.sub(r"(\[long pause\])(\s*\[long pause\])+", r"\1", tagged)
    counts = {t: tagged.count(t) for t in (LONG, SHORT, QUIET, WHISPER, SLOW)}
    return tagged, counts


def transfer_tags(tagged: str, clean: str) -> tuple[str, str]:
    """Pasa las etiquetas de `tagged` (narration_tts) a `clean` (el texto normalizado que se graba). Devuelve
    (texto con etiquetas, modo): «oracion» si párrafos y oraciones coinciden; «parrafo» si solo coinciden los párrafos
    (etiquetas de apertura y la pausa final); «final» si ni eso (solo la pausa final)."""
    tp = [p.strip() for p in re.split(r"\n\s*\n", tagged.strip()) if p.strip()]
    cp = [p.strip() for p in re.split(r"\n\s*\n", clean.strip()) if p.strip()]
    if len(tp) != len(cp):
        return clean.rstrip() + f" {LONG}", "final"

    def _split(par: str) -> list[tuple[str, str, str]]:
        """[(etiquetas de adelante, oración limpia, etiquetas de atrás)]"""
        out: list[tuple[str, str, str]] = []
        for s in _sentences(strip_tags_keep(par)):
            m = re.match(r"^((?:\[[a-z ]+\]\s*)*)(.*?)((?:\s*\[[a-z ]+\])*)$", s, re.S)
            a, body, b = m.group(1).strip(), m.group(2).strip(), m.group(3).strip()
            if not body and out:                     # etiqueta suelta («… letal. [long pause]»): va con la anterior
                pa, pb, pc = out[-1]
                out[-1] = (pa, pb, (pc + " " + a + " " + b).strip())
                continue
            out.append((a, body, b))
        return out
    sent_mode = True
    outs = []
    for t, c in zip(tp, cp):
        ts, cs = _split(t), _sentences(c)
        if len(ts) != len(cs):
            sent_mode = False
            break
        outs.append(" ".join(" ".join(x for x in (a, s2, b) if x) for (a, _, b), s2 in zip(ts, cs)))
    if sent_mode:
        res = "\n\n".join(outs)
        mode = "oracion"
    else:
        outs = []
        for t, c in zip(tp, cp):
            lead = re.match(r"^((?:\[[a-z ]+\]\s*)*)", t).group(1).strip()
            outs.append((lead + " " + c).strip() if lead else c)
        res = "\n\n".join(outs)
        mode = "parrafo"
    # «…» del texto limpio: la pausa corta va también ahí (el normalizador puede haber cambiado los puntos)
    if not res.rstrip().endswith(LONG):
        res = res.rstrip() + f" {LONG}"
    return res, mode


def strip_tags_keep(par: str) -> str:
    """El párrafo con las etiquetas pegadas a su oración (para partir en oraciones sin que una etiqueta suelta quede
    como oración propia): «… muros. [long pause] [quietly] Eran disparos.» → igual, el corte va después de la pausa."""
    return re.sub(r"([.!?…][»”\"]?)\s+((?:\[(?:long pause|short pause)\]\s*)+)", r"\1 \2", par)


def caps_tts(esc: dict, parrafos: list[dict], caps: list[dict], *, slowly_dev: bool = False) -> list[dict]:
    """`narration_tts` para cada cap de `caps` (m01b_guionista.caps_text), con la intensidad de cada párrafo desde su
    beat y el pico desde la escaleta. In place; devuelve `caps`."""
    from script_engine.m01a_escaleta import intent_de_cap as _intent_de_cap
    from script_engine.m01a_skeleton import DEFAULT_INTENT_BY_CAP
    beats = {b["n"]: b for b in esc.get("beats") or []}
    pico = int((esc.get("pico") or {}).get("beat") or 0)
    for c in caps:
        n = c["chapter_number"]
        ps = [p for p in parrafos if p["cap"] == n]
        inten = [int((beats.get(p["beat"]) or {}).get("intensidad") or 0) for p in ps]
        pico_par = next((i for i, p in enumerate(ps) if p["beat"] == pico), None)
        # el pico se marca en el PRIMER párrafo de su beat
        # F23 §1.3: el intent real del cap = el que sale de la función de sus beats (`m01a_escaleta.intent_de_cap`, lo
        # mismo que va al skeleton); sin beats, el guardado en la escaleta o el fijo por número de cap
        ec = next((x for x in esc.get("caps") or [] if x.get("chapter_number") == n), {})
        intent = c.get("narrative_intent") or (_intent_de_cap(esc, n) if any(b.get("cap") == n for b in beats.values())
                                               else ec.get("narrative_intent") or DEFAULT_INTENT_BY_CAP.get(n))
        c["narration_tts"], c["tts_tags"] = tag_cap(c["narration"], intent=intent, intensities=inten,
                                                    pico_par=pico_par, slowly_dev=slowly_dev)
    return caps
