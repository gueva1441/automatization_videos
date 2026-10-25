"""
script_engine/m05_narrative.py — Juez NARRATIVO (F5 §1.5): métricas deterministas del guion por cap y por video.

El juez visual (m05_judge) audita imagen ↔ narración; este audita la narración contra el evidence_pool. Sin LLM:
lo usan m01b (validar cada cap y reintentar con feedback dirigido) y el reporte del video (judge_narration).

    densidad       datos literales del pool por 100 palabras            ≥ DENSITY_MIN   (Orleans v1 ≈ 0.7)
    repetición     ningún dato en > MAX_DATO_CAPS caps; 3-gramas repetidos entre caps < TRIGRAM_MAX
    adjetivación   adjetivos calificativos por 100 palabras             ≤ ADJ_MAX       (heurística, ver adjectives)
    antagonista    el antagonista del pool nombrado en el video
    cliffhanger    el cierre de cada cap 1–6 contiene el dato o la entidad del cliffhanger del skeleton
Un «dato usado» = algún anchor del ítem (evidence.anchors) suena literal en el texto. Para contar repetición solo
cuentan cifras, magnitudes, fechas, contradicciones, eventos y citas (un año suelto o un nombre no son «el dato»).

F5b:
    N2 por id    si el narrador DECLARA los ids que usó (01b chapters[].datos_usados), se cuenta solo lo declarado que
                 además suena literal («Interestatal 10» ya no cuenta como los niños de 10 años). Sin declaración
                 (guiones viejos, v1) se cuenta por regex como antes; el reporte dice cuál («conteo»).
    N3 una vez   cada dato declarado suena una sola vez en su cap (cifra/fecha o frase firma); después, paráfrasis.
    N4 piso      adjetivos/100 entre ADJ_MIN y ADJ_MAX (sin piso, el cap 4 de v2 se leía como acta).
    N5 nombres   un personaje que el pool descartó por no hacer nada no se nombra.
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Any

from script_engine import evidence as ev

DENSITY_MIN = 2.0
MAX_DATO_CAPS = 2
TRIGRAM_MAX = 0.05
# F5 J18 había fijado 3.6 (recorte relativo 8/14 sobre esta heurística). F5b N4 (analista, misma escala que esta
# heurística): piso 2/100 y techo 4/100.
ADJ_MIN = 2.0
ADJ_MAX = 4.0
FILLER_RUN_MAX = 2                     # oraciones seguidas que califican sin dato

FORBIDDEN_FILLER = ("imaginen", "una eternidad de", "cámara de tortura", "coloso de", "manto oscuro",
                    "infierno personal", "eco fantasmal", "sombra inalcanzable", "tragedia íntima",
                    # F5c (analista): el relleno que apareció en las v2 de F5b. F21: fuera «manto de», «el
                    # monstruo», «infierno flotante» y «ecos de» (de caso: «manto de nieve», «ecos de radio»)
                    "velo de misterio", "alfombra de la negación", "sentencia de abandono", "trampa brutal")
_REPEAT_TIPOS = {"cifra", "magnitud", "fecha", "contradiccion"}
_STOP = {"de", "del", "la", "las", "el", "los", "un", "una", "unos", "unas", "y", "o", "e", "en", "a", "al", "que",
         "por", "con", "para", "sin", "se", "su", "sus", "lo", "le", "les", "es", "fue", "era", "como", "más", "muy",
         "no", "ni", "pero", "si", "ya", "hasta", "desde", "entre", "sobre", "tras", "cuando", "donde", "este", "esta",
         "esos", "esas", "ese", "esa", "aquel", "aquella", "había", "habían", "eran", "fueron", "son", "está"}

# ── adjetivos calificativos: lista + sufijos (sin etiquetador gramatical; calibrada sobre Orleans v1)
_ADJ_LIST = set("""
oscuro oscura oscuros oscuras terrible terribles implacable implacables brutal brutales inmenso inmensa inmensos
inmensas desesperado desesperada desesperados desesperadas profundo profunda profundos profundas silencioso
silenciosa siniestro siniestra siniestros siniestras macabro macabra macabros macabras atroz atroces cruel crueles
helado helada gélido gélida espeso espesa pútrido pútrida putrefacto putrefacta denso densa densos densas frío fría
fríos frías húmedo húmeda húmedos húmedas sucio sucia sucios sucias olvidado olvidada olvidados olvidadas
abandonado abandonada abandonados abandonadas atrapado atrapada atrapados atrapadas indefenso indefensa
indefensos indefensas vulnerable vulnerables inocente inocentes eterno eterna eternos eternas vasto vasta vastos
vastas negro negra negros negras gris grises sombrío sombría sombríos sombrías trágico trágica trágicos trágicas
horrible horribles espantoso espantosa aterrador aterradora aterradores implacables feroz feroces devastador
devastadora devastadores devastadoras incontenible incontenibles inhumano inhumana inhumanos inhumanas cruda crudo
desgarrador desgarradora desgarradores desgarradoras escalofriante escalofriantes fantasmal fantasmales inquietante
inquietantes asfixiante asfixiantes nauseabundo nauseabunda angustiante angustiantes interminable interminables
infernal infernales mortal mortales letal letales voraz voraces furioso furiosa furiosos furiosas violento violenta
violentos violentas lúgubre lúgubres tétrico tétrica vibrante vibrantes colosal colosales gigantesco gigantesca
monstruoso monstruosa pesado pesada pesados pesadas cálido cálida opaco opaca turbio turbia turbios turbias
estancado estancada estancadas estancados inmóvil inmóviles débil débiles ciego ciega ciegos ciegas sordo sorda
mudo muda muda mudos cautivo cautiva cautivos cautivas impotente impotentes caótico caótica caóticos caóticas
""".split())
_ADJ_SUFFIX = re.compile(r"(osos?|osas?|bles?|ivos?|ivas?|izos?|izas?|escos?|escas?|antes?|entes?)$")
_NOT_ADJ = set("""
presidente presidentes gente agente agentes cliente clientes parte partes antes durante mientras siempre
detalle mente diente puente fuente fuentes frente corriente corrientes ambiente estudiante estudiantes paciente
pacientes residente residentes habitantes habitante teniente tenientes sargento comandante comandantes
viviente sobreviviente sobrevivientes superviviente supervivientes oriente occidente incidente incidentes
accidente accidentes continente expediente medicamentos instante instantes restaurante gobernante gobernantes
cantante elefante diamante semblante amante amantes cosas mesa casos oso osos ovillo torrente torrentes
mentes ente entes simiente serpiente serpientes pendiente pendientes vertiente diente dientes
""".split())


def words_of(text: str) -> list[str]:
    return re.findall(r"[A-Za-zÁÉÍÓÚÑÜáéíóúñü]+|\d[\d.,]*", str(text))


def adjectives(text: str) -> list[str]:
    """Adjetivos calificativos estimados (lista del género + sufijos -oso/-ble/-ivo/-ante/-ente…, sin sustantivos
    conocidos). No es un etiquetador: mide la TENDENCIA (v1 vs v2), no la gramática exacta."""
    out = []
    for w in words_of(text):
        t = w.lower()
        if t in _NOT_ADJ or t[:1].isdigit() or len(t) < 4 or t.endswith("mente"):
            continue
        if t in _ADJ_LIST or (_ADJ_SUFFIX.search(t) and w[:1].islower()):
            out.append(t)
    return out


def sentences(text: str) -> list[str]:
    return [s.strip() for s in re.split(r"(?<=[.!?…])\s+", str(text).strip()) if s.strip()]


def used_items(text: str, pool: dict[str, Any] | None, kinds: tuple[str, ...] = ("datos", "cronologia", "citas"),
               hard: bool = True, declared: list[str] | None = None) -> list[str]:
    """Ítems del pool que la narración usa. hard=True: solo datos duros (evidence.is_hard) — lo que mide densidad.
    F5b N2: con `declared` (ids que declaró el narrador) solo se miran esos; sin declaración, todo el pool (regex)."""
    its = ev.items(pool)
    cand = [i for i in dict.fromkeys(declared) if i in its] if declared is not None else list(its)
    return [i for i in cand if its[i]["_kind"] in kinds and (not hard or ev.is_hard(its[i]))
            and (_dated_said(text, its[i]) if declared is not None else ev.used_in(text, its[i]))]


def _dated_said(text: str, it: dict[str, Any]) -> bool:
    """Con declaración (N2), un evento o dato de fecha cuenta si su fecha suena: la identidad la da el id declarado,
    y el evento se puede contar con otras palabras en la oración siguiente (F5d: paráfrasis permitida en lo que no es
    cifra, nombre, fecha o cita). Sin fecha, como siempre (used_in)."""
    if it["_kind"] == "cronologia" or (it["_kind"] == "datos" and it.get("tipo") == "fecha"):
        if any(ev.literal_in(a, text) for a in ev.anchors(it)):
            return True
        return _date_paraphrased(text, it)
    return ev.used_in(text, it)


def _date_paraphrased(text: str, it: dict[str, Any]) -> bool:
    """F10 (Omar: una fecha literal por cap; «el candado acepta la paráfrasis»): un evento con fecha también cuenta si
    la oración lo dice con «ese domingo», «esa noche»… y comparte una palabra de contenido con el evento.
    F23 §1.1: solo si el caso es puntual (un caso prolongado dice cada fecha); sin perfil, como antes."""
    from researcher_steps.research_v3 import caso
    from script_engine.guion_v3_reglas import DATE_PARAPHRASE
    if caso().get("tipo_evento") == "prolongado":
        return False
    words = ev._content(ev.text_of(it))
    for s in ev._sentences(text):
        if DATE_PARAPHRASE.search(s) and (not words or words & ev._content(s)):
            return True
    return False


def repeat_items(text: str, pool: dict[str, Any] | None, declared: list[str] | None = None) -> list[str]:
    """Ítems que cuentan para la regla de repetición (los mismos datos duros que la densidad)."""
    return used_items(text, pool, declared=declared)


def text_and_ids(n: Any) -> tuple[str, list[str] | None]:
    """Una narración como str (sin declaración) o como cap de 01b {narration, datos_usados}."""
    if isinstance(n, dict):
        d = n.get("datos_usados")
        return str(n.get("narration") or ""), (list(d) if isinstance(d, list) else None)
    return str(n or ""), None


def silent_names(text: str, pool: dict[str, Any] | None) -> list[str]:
    """F5b N5: personajes que el pool descartó por no hacer nada y que la narración igual nombra."""
    out = []
    for d in (pool or {}).get("_descartados") or []:
        if d.get("kind") == "personajes":
            from script_engine import nombres
            sur = nombres.apellido(d["texto"])                         # F21: nombres.py
            if sur and nombres.menciona(text, sur):
                out.append(d["texto"])
    return out


def _trigrams(text: str) -> set[tuple[str, ...]]:
    ws = [w.lower() for w in words_of(text) if w.lower() not in _STOP]
    return {tuple(ws[k:k + 3]) for k in range(len(ws) - 2)}


def trigram_overlap(texts: list[str]) -> list[float]:
    """Por cap: fracción de sus 3-gramas (sin palabras funcionales) que aparecen en OTRO cap."""
    tg = [_trigrams(t) for t in texts]
    out = []
    for k, s in enumerate(tg):
        others = set().union(*(tg[j] for j in range(len(tg)) if j != k)) if len(tg) > 1 else set()
        out.append(round(len(s & others) / len(s), 4) if s else 0.0)
    return out


def filler_run(text: str, pool: dict[str, Any] | None) -> int:
    """Máximo de oraciones SEGUIDAS que califican sin dato (≥ 2 adjetivos y ni cifra, ni nombre, ni dato del pool)."""
    run = best = 0
    for s in sentences(text):
        has_data = bool(re.search(r"\d", s)) or bool(used_items(s, pool)) or bool(
            re.search(r"(?<![.!?¿¡]\s)(?<!^)\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]{2,}", s))
        if not has_data and len(adjectives(s)) >= 2:
            run += 1
            best = max(best, run)
        else:
            run = 0
    return best


def forbidden_filler(text: str) -> list[str]:
    t = text.lower()
    return [f for f in FORBIDDEN_FILLER if f in t]


def entity_terms(it: dict[str, Any]) -> list[str]:
    """Lo que prueba que un cierre anticipa el ítem: sus anchors + nombres propios + sustantivos largos del texto."""
    terms = [a for a in ev.anchors(it) if not re.fullmatch(r"\d{4}", a)]
    txt = ev.text_of(it)
    terms += [w for w in re.findall(r"\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]{3,}\b", txt)[1:]]
    terms += [w for w in words_of(txt) if len(w) >= 7 and w.lower() not in _STOP and w.lower() not in _NOT_ADJ
              and not w[:1].isdigit()]
    return list(dict.fromkeys(terms))


def closing_hits_cliffhanger(text: str, it: dict[str, Any] | None) -> list[str]:
    if not it:
        return []
    tail = " ".join(sentences(text)[-2:])
    return [t for t in entity_terms(it) if ev.literal_in(t, tail)]


def names_with_role(text: str, person: dict[str, Any]) -> tuple[bool, bool]:
    """(nombrado por nombre y apellido, con cargo cerca de la 1.ª mención). F21: nombre y apellido de `nombres.clave`
    (cualquier alfabeto, sin cargos ni partículas)."""
    from script_engine import nombres
    first, last = nombres.clave(person["nombre"])
    if not last:
        return False, False
    t = nombres.norm(text)
    w = r"(?<![^\W\d_])"
    pat = (rf"{w}{re.escape(first)}(?![^\W\d_])(?:\s+\w+\.?)?\s+" if first else w) + rf"{re.escape(last)}(?![^\W\d_])"
    m = re.search(pat, t)
    if not m or not first:
        return False, False
    role_words = [x for x in re.findall(r"[^\W\d_]{4,}", nombres.norm(person.get("rol") or ""))
                  if x not in _STOP][:3]
    ctx = t[max(0, m.start() - 70):m.end() + 70]
    return True, (not role_words) or any(w in ctx for w in role_words)


# ═══════════════════════════════════════════════════════════════
#  Métricas por cap y por video
# ═══════════════════════════════════════════════════════════════

def cap_metrics(text: str, pool: dict[str, Any] | None, declared: list[str] | None = None) -> dict[str, Any]:
    n_w = max(1, len(words_of(text)))
    used = used_items(text, pool, declared=declared)
    adj = adjectives(text)
    out = {"palabras": n_w, "datos_usados": used, "densidad": round(100 * len(used) / n_w, 2),
           "adjetivos": len(adj), "adj_100": round(100 * len(adj) / n_w, 2), "relleno_seguido": filler_run(text, pool),
           "relleno_prohibido": forbidden_filler(text), "conteo": "por_id" if declared is not None else "regex",
           "repetidos_en_cap": [list(x) for x in ev.repeats_in_cap(text, used_items(text, pool, hard=False,
                                                                                    declared=declared), pool)],
           "nombres_sin_accion": silent_names(text, pool)}
    # «por hecho»: anclas DISTINTAS que suenan (el «29 de agosto» de cinco eventos es un solo dato dicho)
    anc = {ev.norm(a) for i in used for a in ev.anchors(ev.items(pool)[i]) if ev.literal_in(a, text)}
    out["densidad_hechos"] = round(100 * len(anc) / n_w, 2)
    if declared is not None:                  # para comparar con la medición vieja (regex sobre todo el pool)
        rx = used_items(text, pool)
        out["densidad_regex"] = round(100 * len(rx) / n_w, 2)
        out["declarados_no_literales"] = [i for i in declared if i in ev.items(pool) and i not in
                                          used_items(text, pool, hard=False, declared=declared)
                                          and ev.items(pool)[i]["_kind"] in ("datos", "cronologia", "citas")]
    return out


def video_metrics(narrations: list[Any], pool: dict[str, Any] | None, skeleton: dict[str, Any] | None = None
                  ) -> dict[str, Any]:
    """Métricas de las 7 narraciones (en orden; str o caps de 01b con datos_usados) + veredicto por umbral."""
    its = ev.items(pool)
    pairs = [text_and_ids(n) for n in narrations]
    narrations = [t for t, _ in pairs]
    caps = [cap_metrics(t, pool, d) for t, d in pairs]
    tri = trigram_overlap(narrations)
    caps_of: dict[str, list[int]] = {}
    for k, (t, d) in enumerate(pairs, start=1):
        for i in repeat_items(t, pool, declared=d):
            caps_of.setdefault(i, []).append(k)
    over = {i: c for i, c in caps_of.items() if len(c) > MAX_DATO_CAPS}
    allt = " ".join(narrations)
    antag = ev.primary_antagonist(pool)
    antag_ok = ev.literal_in(ev._surname(antag["nombre"]), allt) if antag else None
    chs = (skeleton or {}).get("chapters") or []
    cliffs = []
    for k, t in enumerate(narrations, start=1):
        ch = next((c for c in chs if c.get("chapter_number") == k), {})
        cid = ch.get("cliffhanger")
        if k <= 6 and cid:
            hits = closing_hits_cliffhanger(t, its.get(cid))
            cliffs.append({"cap": k, "id": cid, "texto": ev.text_of(its.get(cid, {})), "ok": bool(hits), "en_cierre": hits})
        caps[k - 1]["trigramas_repetidos"] = tri[k - 1]
    words = sum(c["palabras"] for c in caps)
    used_all = {i for c in caps for i in c["datos_usados"]}
    tri_video = round(sum(c["trigramas_repetidos"] * c["palabras"] for c in caps) / max(1, words), 4)
    v = {"densidad": round(100 * sum(len(c["datos_usados"]) for c in caps) / max(1, words), 2),
         "adj_100": round(100 * sum(c["adjetivos"] for c in caps) / max(1, words), 2),
         "trigramas_repetidos": tri_video, "datos_en_mas_de_2_caps": over, "antagonista_nombrado": antag_ok,
         "antagonista": antag["nombre"] if antag else None,
         "cliffhangers": cliffs, "datos_distintos": len(used_all), "palabras": words,
         "conteo": "por_id" if all(c["conteo"] == "por_id" for c in caps) else "regex",
         "caps_con_repetidos_en_cap": [k for k, c in enumerate(caps, start=1) if c["repetidos_en_cap"]],
         "caps_fuera_de_adjetivos": [k for k, c in enumerate(caps, start=1)
                                     if not ADJ_MIN <= c["adj_100"] <= ADJ_MAX],
         "nombres_sin_accion": sorted({n for c in caps for n in c["nombres_sin_accion"]})}
    # F5d: cifras canónicas, fechas y datos reservados para pantalla, por cap del skeleton
    nc, dp, lk = [], 0, []
    for k, (t, d) in enumerate(pairs, start=1):
        ch = next((c for c in chs if c.get("chapter_number") == k), {})
        nc += [f"cap {k}: {x}" for x in non_canonical(t, pool, ch)]
        dp += len(date_problems(t, pool, list(ch.get("evidence_ids") or []) + list(d or [])))
        lk += [f"cap {k}: {x}" for x in screen_leaks(t, pool, ch)]
    v.update({"cifras_no_canonicas": nc, "problemas_de_fechas": dp, "pantalla_dichos": lk})
    v["densidad_hechos"] = round(sum(c["densidad_hechos"] * c["palabras"] / 100 for c in caps) * 100 / max(1, words), 2)
    if all("densidad_regex" in c for c in caps):
        v["densidad_regex"] = round(100 * sum(c["densidad_regex"] * c["palabras"] / 100 for c in caps)
                                    / max(1, words), 2)
    v["umbral"] = {"densidad": v["densidad"] >= DENSITY_MIN, "repeticion": not over and tri_video < TRIGRAM_MAX,
                   "adjetivacion": ADJ_MIN <= v["adj_100"] <= ADJ_MAX,
                   "repeticion_en_cap": not v["caps_con_repetidos_en_cap"],
                   "nombres": not v["nombres_sin_accion"],
                   "antagonista": antag_ok is not False,
                   "cliffhanger": all(c["ok"] for c in cliffs) if cliffs else None}
    return {"caps": caps, "video": v}


def judge_narration(topic_id: str, *, steps_dir: Any = None, pool: dict[str, Any] | None = None,
                    narration: dict[str, Any] | None = None, skeleton: dict[str, Any] | None = None,
                    out_name: str = "06_judge_narrative.json") -> dict[str, Any]:
    """Reporte del juez narrativo de un topic: métricas por cap y por video + umbrales → _steps/<id>/06_….json.
    Lee de disco lo que no se pase (01_facts_sources / 01a_skeleton / 01b_narration)."""
    import json
    from pathlib import Path
    if steps_dir is None:
        from config import DATA_DIR
        steps_dir = DATA_DIR / "scripts" / "_steps"
    d = Path(steps_dir) / topic_id

    def _load(name: str) -> dict[str, Any]:
        f = d / name
        return json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    pool = pool if pool is not None else _load("01_facts_sources.json").get("evidence_pool")
    narration = narration or _load("01b_narration.json")
    skeleton = skeleton or _load("01a_skeleton.json")
    caps_in = sorted(narration.get("chapters") or [], key=lambda c: c["chapter_number"])
    rep = video_metrics(caps_in, pool, skeleton)
    rep["umbrales"] = {"densidad_min": DENSITY_MIN, "max_caps_por_dato": MAX_DATO_CAPS, "trigramas_max": TRIGRAM_MAX,
                       "adj_100_min": ADJ_MIN, "adj_100_max": ADJ_MAX}
    rep["violaciones_narrador"] = narration.get("_f5_violations") or {}
    d.mkdir(parents=True, exist_ok=True)
    (d / out_name).write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    return rep


# ═══════════════════════════════════════════════════════════════
#  Validación de un cap (la usa m01b para reintentar)
# ═══════════════════════════════════════════════════════════════

def cap_problems(text: str, *, cap: int, pool: dict[str, Any], skeleton: dict[str, Any],
                 previous: list[Any], declared: list[str] | None = None,
                 facts: list[Any] | None = None) -> list[str]:
    """Problemas F5 de una narración contra su skeleton (lista vacía = cumple). Mensajes cortos para el feedback.
    `previous`: narraciones anteriores (str o caps de 01b con datos_usados). `declared`: ids que declara este cap
    (F5b N2: se cuenta lo declarado que suena literal; None = regex sobre todo el pool, como F5).
    Es la lista plana de cap_review (duras + blandas)."""
    r = cap_review(text, cap=cap, pool=pool, skeleton=skeleton, previous=previous, declared=declared, facts=facts)
    return r["hard"] + r["soft"]


# ═══════════════════════════════════════════════════════════════
#  F5c — reglas duras y blandas, «no inventar», «no contaminar», puntaje del mejor de 3
# ═══════════════════════════════════════════════════════════════

TRIGRAM_CAP_MAX = TRIGRAM_MAX           # 3-gramas del cap que ya sonaron en caps anteriores (regla blanda)
SCORE = {"dato": 3, "cliffhanger": 2, "repetido": -3, "relleno": -2, "adjetivos": -1}
_NUM_TOK = re.compile(r"\d[\d.,]*\d|\d")


def _num_key(tok: str) -> str:
    """«6,375» y «6.375» (miles con coma o con punto) → «6375»; «4.6» queda decimal."""
    t = tok.rstrip(".,")
    if re.fullmatch(r"\d{1,3}(?:[.,]\d{3})+", t):
        return re.sub(r"[.,]", "", t)
    return t.replace(",", "")


def _sources_text(pool: dict[str, Any] | None, facts: list[Any] | None) -> str:
    parts = [ev.text_of(it) + " " + str(it.get("valor") or "") + " " + str(it.get("fecha") or "")
             for it in ev.items(pool).values()]
    parts += [str(f.get("fact") if isinstance(f, dict) else f) for f in facts or []]
    return " ".join(parts)


def invented_numbers(text: str, pool: dict[str, Any] | None, facts: list[Any] | None = None,
                     recibido: str | None = None) -> list[str]:
    """F5c (dura): cifras en dígitos de la narración que no están en ninguna fuente (pool o verified_facts). Las
    fechas ISO del pool aportan su año y su día («2005-08-29» → 2005, 29). Las cifras dichas en palabras no se
    controlan acá (las cuenta el juez cuando son de un dato).
    F22b: `recibido` = las líneas de datos que el guionista recibió (texto, marcas VERSIÓN DE / PANTALLA, fuente): una
    cifra que está ahí no es inventada."""
    src = _sources_text(pool, facts) + ("\n" + recibido if recibido else "")
    ok = {_num_key(t) for t in _NUM_TOK.findall(src)}
    ok |= {str(int(x)) for d in re.findall(r"\d{4}-(\d{2})-(\d{2})", src) for x in d}
    out = []
    for m in _NUM_TOK.finditer(text):
        k = _num_key(m.group(0))
        if k in ok or (re.fullmatch(r"\d+", k) and str(int(k)) in ok):
            continue
        out.append(m.group(0))
    return list(dict.fromkeys(out))


def contamination(text: str, pool: dict[str, Any] | None, facts: list[Any] | None = None) -> list[str]:
    """F5c (dura): la narración trae algo que el pool DESCARTÓ (F5b N1/N5): una cifra o un nombre de lugar que solo
    estaba en lo descartado, ≥ 2 palabras propias de un dato descartado («médium», «psíquico»), o un personaje sin
    acción. Lo que también está en el pool que queda o en los verified_facts no cuenta."""
    kept = ev.norm(_sources_text(pool, facts))
    kept_nums = {_num_key(t) for t in _NUM_TOK.findall(kept)}
    t = ev.norm(text)
    out = list(silent_names(text, pool))
    for d in (pool or {}).get("_descartados") or []:
        if d.get("kind") == "personajes":
            continue
        dt = str(d.get("texto") or "")
        if d.get("kind") == "lugares":
            if ev.norm(dt) not in kept and re.search(rf"(?<!\w){re.escape(ev.norm(dt))}(?!\w)", t):
                out.append(dt)
            continue
        nums = [x for x in _NUM_TOK.findall(dt) if _num_key(x) not in kept_nums]
        if any(re.search(rf"(?<![\d.,]){re.escape(x)}(?![\d])", text) for x in nums):
            out.append(dt)
            continue
        own = {w for w in re.findall(r"[a-zñ]{6,}", ev.norm(dt)) if w not in kept}
        if len({w for w in own if re.search(rf"\b{w}", t)}) >= 2:
            out.append(dt)
    return list(dict.fromkeys(out))


def non_canonical(text: str, pool: dict[str, Any] | None, ch: dict[str, Any]) -> list[str]:
    """F5d (dura): cifras de un conteo que no son la oficial (pool `cifras_canonicas`), fuera del cap que cuenta la
    contradicción (`contradiccion_cifras` del skeleton)."""
    out = []
    for g in (pool or {}).get("cifras_canonicas") or []:
        if g["oficial"] in (ch.get("contradiccion_cifras") or []):
            continue
        for v in g["variantes"]:
            for val in re.findall(r"\d[\d,]*\d", v["valor"]):
                if val != g["valor"] and ev.literal_in(val, text):
                    out.append(f"{val} ({v['estatus']}; la oficial es {g['valor']})")
    return list(dict.fromkeys(out))


def screen_leaks(text: str, pool: dict[str, Any] | None, ch: dict[str, Any]) -> list[str]:
    """F5d (dura): la voz dice un dato RESERVADO PARA PANTALLA del cap (`pantalla_ids`): alguno de sus anchors que no
    comparte con los datos que el cap sí narra suena literal."""
    its = ev.items(pool)
    said = {ev.norm(a) for i in ch.get("evidence_ids") or [] if i in its for a in ev.anchors(its[i])}
    out = []
    for i in ch.get("pantalla_ids") or []:
        if i not in its:
            continue
        own = [a for a in ev.anchors(its[i]) if ev.norm(a) not in said]
        if any(ev.literal_in(a, text) for a in own) and (its[i]["_kind"] != "cronologia" or ev.used_in(text, its[i])):
            out.append(f"[{i}] «{ev.text_of(its[i])[:60]}»")
    return out


def _plain_content(s: str) -> set[str]:
    """Palabras de contenido sin los nombres propios (los nombres se comparten entre eventos del mismo personaje)."""
    names = {w.lower()[:6] for w in re.findall(r"\b[A-ZÁÉÍÓÚÑ][a-záéíóúñ]+", s)}
    return ev._content(s) - {ev.norm(n)[:6] for n in names}


DATE_MATCH_MIN = 0.5                    # fracción de las palabras del evento (sin nombres) en la oración
DATE_MATCH_WORDS = 2


def date_problems(text: str, pool: dict[str, Any] | None, ids: list[str], year: str | None = None) -> list[str]:
    """F5d (dura): (1) una oración que dice dos fechas distintas (fundidas); (2) una oración que cuenta un evento
    fechado del cap (≥ 50 % de sus palabras, sin nombres) sin su fecha y bajo OTRA fecha — la que dice o la que la
    voz venía narrando —; (3) un evento del cap contado sin que ninguna fecha suene antes."""
    its = ev.items(pool)
    evs = [its[i] for i in dict.fromkeys(ids) if i in its and (its[i]["_kind"] == "cronologia"
                                                              or its[i].get("tipo") == "fecha") and ev.item_date(its[i])]
    from researcher_steps.research_v3 import caso
    # F23 §1.1: sin año a mano, el inicio del caso del perfil (antes, «2000»)
    year = year or next((ev.item_date(e)[:4] for e in evs), None) or next(
        (str(c.get("fecha"))[:4] for c in (pool or {}).get("cronologia") or [] if c.get("fecha")),
        str(caso().get("anio_inicio") or "") or None)
    out, cur = [], None
    for s in sentences(text):
        # F23 §1.1: una fecha sin año toma el de la fecha anterior más cercana que lo dijo (la cronología cruza años)
        dichos = [m.group(3) for m in ev._DATE_TXT.finditer(s) if m.group(3)]
        if not dichos and cur:
            year = cur[:4]
        ds = list(dict.fromkeys(ev.spoken_dates(s, year)))
        if dichos:
            year = dichos[-1]
        if len(ds) >= 2:
            out.append(f"dos fechas en una oración ({', '.join(ev.spoken_date(d) or d for d in ds)}): «{s[:70]}…»")
        eff = ds[-1] if ds else cur
        cs = _plain_content(s)
        for e in evs:
            w = _plain_content(ev.text_of(e))
            hit = len(w & cs)
            if not w or hit < DATE_MATCH_WORDS or hit / len(w) < DATE_MATCH_MIN:
                continue
            d = ev.item_date(e)
            if d in ds or d == eff:
                continue
            if eff is None:
                out.append(f"contaste [{e['id']}] sin su fecha ({ev.spoken_date(d)}): «{s[:70]}…»")
            else:
                out.append(f"fundiste fechas: [{e['id']}] es del {ev.spoken_date(d)}, pero la oración queda en el "
                           f"{ev.spoken_date(eff)}: «{s[:70]}…»")
        cur = eff
    return list(dict.fromkeys(out))


_QUOTED = re.compile(r"[\"“«]([^\"”»]{3,})[\"”»]")


def false_quotes(text: str, pool: dict[str, Any] | None) -> list[str]:
    """F5d+ (dura): texto entre comillas que no es una cita del pool. Una frase del research («El sheriff de la cárcel
    declaró…») no es una cita: va sin comillas. Se permiten nombres o términos cortos entre comillas (≤ 3 palabras:
    «Templeman III»)."""
    cits = [ev.norm(q["texto"]) for q in (pool or {}).get("citas") or []]
    out = []
    for m in _QUOTED.finditer(text):
        q = m.group(1).strip()
        if len(q.split()) <= 3:
            continue
        nq = ev.norm(q).strip(" .,;:")
        if not any(nq in c or c in nq for c in cits):
            out.append(q[:60])
    return out


def trigram_vs_previous(text: str, previous: list[str]) -> float:
    """Fracción de los 3-gramas del cap (sin palabras funcionales) que ya sonaron en caps anteriores."""
    tg = _trigrams(text)
    prev = set().union(*(_trigrams(p) for p in previous)) if previous else set()
    return round(len(tg & prev) / len(tg), 4) if tg else 0.0


def cap_review(text: str, *, cap: int, pool: dict[str, Any], skeleton: dict[str, Any], previous: list[Any],
               declared: list[str] | None = None, facts: list[Any] | None = None) -> dict[str, Any]:
    """F5c: problemas de un cap separados por PRIORIDAD y el puntaje para elegir el mejor de 3.
    hard (rechazan): no inventar, datos asignados (una vez, literales, declarados), no repetir datos de 2 caps, no
          contaminar (lo descartado, nombres sin acción), relleno prohibido, cierre con el dato del cliffhanger.
    soft (aviso + un reintento, nunca rechazo): adjetivos 2–4/100, 3-gramas ya dichos < 5 %, densidad, cargo de las
          personas, orden de fechas, comillas de las citas, oraciones seguidas sin dato, datos sin declarar.
    score = datos declarados y literales ×3 + cliffhanger ×2 − 3 por repetido − 2 por relleno − 1 si los adjetivos
          salen del rango."""
    its = ev.items(pool)
    ch = next((c for c in skeleton.get("chapters") or [] if c.get("chapter_number") == cap), {})
    hard: list[str] = []
    soft: list[str] = []
    prev = [text_and_ids(n) for n in previous]
    seen_before = {i for t, d in prev for i in used_items(t, pool, declared=d)}
    assigned = [i for i in ch.get("evidence_ids") or [] if i in its]
    new_assigned = [i for i in assigned if i not in seen_before]
    lit = set(used_items(text, pool, hard=False, declared=declared))
    used = [i for i in new_assigned if i in lit] if declared is not None else \
        [i for i in new_assigned if ev.used_in(text, its[i])]
    need = min(3, len(new_assigned))
    if len(used) < need:
        miss = [i for i in new_assigned if i not in used][:6]
        hard.append(f"usaste {len(used)} de los datos asignados (mínimo {need}); faltan literales"
                    + (" o sin declarar en datos_usados" if declared is not None else "") + ": "
                    + "; ".join(f"[{i}] «{' / '.join(ev.anchors(its[i])) or ev.text_of(its[i])[:50]}»" for i in miss))
    if declared is not None:
        bad = [i for i in dict.fromkeys(declared) if i in its and i not in lit
               and its[i]["_kind"] in ("datos", "cronologia", "citas")]
        if bad:
            hard.append("declaraste en datos_usados ids que no están LITERALES en la narración (decí la cifra/fecha "
                        "tal cual o sacalos de la lista): " + ", ".join(bad))
        undecl = [i for i in used_items(text, pool) if i not in set(declared)]
        if undecl:
            soft.append("estos datos del pool suenan en tu narración pero no están en datos_usados (si los contaste, "
                        "declaralos; si es un choque de cifras —una ruta 10 no son los niños de 10 años—, no): "
                        + "; ".join(f"[{i}] «{' / '.join(ev.anchors(its[i]))}»" for i in undecl[:8]))
    reps = ev.repeats_in_cap(text, sorted(lit) if declared is not None else used_items(text, pool, hard=False), pool)
    if reps:
        hard.append("cada dato se dice UNA vez por cap; después parafraseá sin la cifra («ese lunes», «esa noche», "
                    "«el agua»): " + "; ".join(f"«{f}» ×{n}" for f, n in reps))
    prev_caps = Counter(i for t, d in prev for i in set(repeat_items(t, pool, declared=d)))
    rep = [i for i in repeat_items(text, pool, declared=declared) if prev_caps[i] >= MAX_DATO_CAPS]
    if rep:
        hard.append("estos datos ya salieron en 2 caps, no los repitas: "
                    + "; ".join(f"«{' / '.join(ev.anchors(its[i]))}»" for i in rep))
    inv = invented_numbers(text, pool, facts) if facts is not None else []
    if inv:
        hard.append("cifras que no están en el research (no inventes): " + ", ".join(inv))
    cont = contamination(text, pool, facts)
    if cont:
        hard.append("esto está fuera del caso o no hace nada en la historia; no lo nombres: "
                    + "; ".join(c[:60] for c in cont))
    bad = forbidden_filler(text)
    if bad:
        hard.append(f"relleno prohibido: {', '.join(bad)}")
    fq = false_quotes(text, pool)
    if fq:
        hard.append("comillas solo para las citas del pool (la frase del research va sin comillas): "
                    + "; ".join(f"«{x}…»" for x in fq))
    nc = non_canonical(text, pool, ch)
    if nc:
        hard.append("cifra canónica: este conteo se dice con la oficial en todo el video; sacá " + "; ".join(nc))
    lk = screen_leaks(text, pool, ch)
    if lk:
        hard.append("esto está reservado para la pantalla de este cap, no lo digas: " + "; ".join(lk))
    dp = date_problems(text, pool, list(ch.get("evidence_ids") or []) + list(declared or []))
    if dp:
        hard.append("fechas: " + " | ".join(dp[:4]))
    cid = ch.get("cliffhanger")
    cliff_ok = None
    if cap <= 6 and cid and cid in its:
        cliff_ok = bool(closing_hits_cliffhanger(text, its[cid]))
        if not cliff_ok:
            hard.append(f"el cierre tiene que anticipar el dato concreto del cap {cap + 1}: «{ev.text_of(its[cid])[:90]}» "
                        f"(nombralo o dejalo incompleto; nada de retórica genérica)")
    # ── blandas
    for p in skeleton.get("personajes") or []:
        if p.get("tipo") == "institucion":                  # F22 §1.2: una institución no tiene nombre y apellido
            continue
        if p.get("entra_en_cap") == cap:
            named, role = names_with_role(text, p)
            if not named or not role:
                soft.append(f"nombrá a {p['nombre']} por nombre y apellido y con su cargo ({p.get('rol')}) la primera vez")
    # F23 §1.1: con la cronología de mes/año como dato duro, un evento asignado puede no tener su anchor literal en el
    # texto; el orden se mide solo con los que lo tienen (antes, `min` de una lista vacía)
    at = {i: [m.start() for a in ev.anchors(its[i]) for m in re.finditer(re.escape(ev.norm(a)), ev.norm(text))]
          for i in used if its[i]["_kind"] == "cronologia"}
    crono = sorted((i for i, p in at.items() if p), key=lambda i: its[i]["fecha"])
    if len(crono) >= 2:
        pos = [min(at[i]) for i in crono]
        if pos != sorted(pos):
            soft.append("narrá los eventos en orden de fecha y decí las fechas: "
                        + " → ".join(f"{ev.spoken_date(its[i]['fecha'])}" for i in crono))
    for i in used_items(text, pool, kinds=("citas",)):
        q = its[i]
        m = re.search(re.escape(ev.norm(q["texto"])), ev.norm(text))
        k = ev.norm(text).find(ev.norm(q["texto"])[:12])
        quoted = k >= 0 and bool(re.search(r"[\"“«]", text[max(0, k - 40):k + 1]))     # la comilla abre antes
        near = m and ev.literal_in(ev._surname(q["autor"]), ev.norm(text)[max(0, m.start() - 150):m.end() + 150])
        if not quoted or not near:
            soft.append(f"la cita «{q['texto'][:40]}…» va entre comillas y con su autor ({q['autor']}) al lado")
    cm = cap_metrics(text, pool, declared)
    if new_assigned and cm["densidad"] < DENSITY_MIN:
        soft.append(f"densidad {cm['densidad']} datos/100 palabras (mínimo {DENSITY_MIN}): más datos literales del pool, "
                    "menos descripción")
    adj_out = not ADJ_MIN <= cm["adj_100"] <= ADJ_MAX
    if cm["adj_100"] > ADJ_MAX:
        soft.append(f"{cm['adj_100']} adjetivos/100 palabras (máximo {ADJ_MAX}): sacá adjetivos — "
                    + ", ".join(dict.fromkeys(adjectives(text)))[:160])
    elif cm["adj_100"] < ADJ_MIN:
        soft.append(f"{cm['adj_100']} adjetivos/100 palabras (mínimo {ADJ_MIN}): se lee como un acta; sumá 2 o 3 "
                    "calificativos concretos atados a los hechos (cómo era el lugar, la luz, el frío o el calor), sin relleno")
    if filler_run(text, pool) > FILLER_RUN_MAX:
        soft.append(f"más de {FILLER_RUN_MAX} oraciones seguidas que califican sin dato: cambiá adjetivos por hechos")
    tri = trigram_vs_previous(text, [t for t, _ in prev])
    if tri >= TRIGRAM_CAP_MAX:
        soft.append(f"{tri:.0%} de tus frases de 3 palabras ya se dijeron en caps anteriores (máximo "
                    f"{TRIGRAM_CAP_MAX:.0%}): no repitas fórmulas (el nombre completo con el cargo basta una vez; "
                    "después, el cargo o el apellido solo)")
    n_dat = len([i for i in lit if its[i]["_kind"] in ("datos", "cronologia", "citas")]) if declared is not None \
        else len(used_items(text, pool, hard=False))
    score = (SCORE["dato"] * n_dat + SCORE["cliffhanger"] * bool(cliff_ok) + SCORE["repetido"] * len(reps)
             + SCORE["relleno"] * len(bad) + SCORE["adjetivos"] * adj_out)
    return {"hard": hard, "soft": soft, "score": score,
            "parts": {"datos": n_dat, "cliffhanger": cliff_ok, "repetidos": len(reps), "relleno": len(bad),
                      "adj_100": cm["adj_100"], "adj_fuera": adj_out, "trigramas_previos": tri}}
