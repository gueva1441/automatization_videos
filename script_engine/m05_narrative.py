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
"""
from __future__ import annotations

import re
from collections import Counter
from typing import Any

from script_engine import evidence as ev

DENSITY_MIN = 2.0
MAX_DATO_CAPS = 2
TRIGRAM_MAX = 0.05
# Umbral del handoff: ≤ 8 adjetivos/100 con v1 ≈ 14 (medición del analista). Esta heurística mide Orleans v1 en
# 6.2 → mismo recorte relativo (8/14): 6.2 × 8/14 ≈ 3.6. Con 8 literal, v1 ya «aprobaría» (DECISIONES_F5 J18).
ADJ_MAX = 3.6
FILLER_RUN_MAX = 2                     # oraciones seguidas que califican sin dato

FORBIDDEN_FILLER = ("imaginen", "una eternidad de", "cámara de tortura", "coloso de", "manto oscuro",
                    "infierno personal", "eco fantasmal", "sombra inalcanzable", "tragedia íntima")
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
               hard: bool = True) -> list[str]:
    """Ítems del pool que la narración usa. hard=True: solo datos duros (evidence.is_hard) — lo que mide densidad."""
    return [i for i, it in ev.items(pool).items()
            if it["_kind"] in kinds and (not hard or ev.is_hard(it)) and ev.used_in(text, it)]


def repeat_items(text: str, pool: dict[str, Any] | None) -> list[str]:
    """Ítems que cuentan para la regla de repetición (los mismos datos duros que la densidad)."""
    return used_items(text, pool)


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
    """(nombrado por nombre y apellido, con cargo cerca de la 1.ª mención)."""
    ws = [w for w in re.findall(r"[A-Za-zÁÉÍÓÚÑáéíóúñ]+", person["nombre"]) if len(w) > 1 and w[:1].isupper()
          and w.lower() not in {"jr", "sr"}]
    if not ws:
        return False, False
    first, last = ws[0], ws[-1]
    t = ev.norm(text)
    m = re.search(rf"\b{re.escape(ev.norm(first))}\b(?:\s+\w\.?)?\s+{re.escape(ev.norm(last))}\b", t)
    if not m:
        return False, False
    role_words = [w for w in re.findall(r"[a-záéíóúñ]{4,}", ev.norm(person.get("rol") or ""))
                  if w not in _STOP][:3]
    ctx = t[max(0, m.start() - 70):m.end() + 70]
    return True, (not role_words) or any(w in ctx for w in role_words)


# ═══════════════════════════════════════════════════════════════
#  Métricas por cap y por video
# ═══════════════════════════════════════════════════════════════

def cap_metrics(text: str, pool: dict[str, Any] | None) -> dict[str, Any]:
    n_w = max(1, len(words_of(text)))
    used = used_items(text, pool)
    adj = adjectives(text)
    return {"palabras": n_w, "datos_usados": used, "densidad": round(100 * len(used) / n_w, 2),
            "adjetivos": len(adj), "adj_100": round(100 * len(adj) / n_w, 2), "relleno_seguido": filler_run(text, pool),
            "relleno_prohibido": forbidden_filler(text)}


def video_metrics(narrations: list[str], pool: dict[str, Any] | None, skeleton: dict[str, Any] | None = None
                  ) -> dict[str, Any]:
    """Métricas de las 7 narraciones (en orden) + veredicto por umbral."""
    its = ev.items(pool)
    caps = [cap_metrics(t, pool) for t in narrations]
    tri = trigram_overlap(narrations)
    caps_of: dict[str, list[int]] = {}
    for k, t in enumerate(narrations, start=1):
        for i in repeat_items(t, pool):
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
         "cliffhangers": cliffs, "datos_distintos": len(used_all), "palabras": words}
    v["umbral"] = {"densidad": v["densidad"] >= DENSITY_MIN, "repeticion": not over and tri_video < TRIGRAM_MAX,
                   "adjetivacion": v["adj_100"] <= ADJ_MAX,
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
    texts = [c["narration"] for c in sorted(narration.get("chapters") or [], key=lambda c: c["chapter_number"])]
    rep = video_metrics(texts, pool, skeleton)
    rep["umbrales"] = {"densidad_min": DENSITY_MIN, "max_caps_por_dato": MAX_DATO_CAPS, "trigramas_max": TRIGRAM_MAX,
                       "adj_100_max": ADJ_MAX}
    rep["violaciones_narrador"] = narration.get("_f5_violations") or {}
    d.mkdir(parents=True, exist_ok=True)
    (d / out_name).write_text(json.dumps(rep, ensure_ascii=False, indent=1), encoding="utf-8")
    return rep


# ═══════════════════════════════════════════════════════════════
#  Validación de un cap (la usa m01b para reintentar)
# ═══════════════════════════════════════════════════════════════

def cap_problems(text: str, *, cap: int, pool: dict[str, Any], skeleton: dict[str, Any],
                 previous: list[str]) -> list[str]:
    """Problemas F5 de una narración contra su skeleton (lista vacía = cumple). Mensajes cortos para el feedback."""
    its = ev.items(pool)
    ch = next((c for c in skeleton.get("chapters") or [] if c.get("chapter_number") == cap), {})
    out: list[str] = []
    seen_before = {i for t in previous for i in used_items(t, pool)}
    assigned = [i for i in ch.get("evidence_ids") or [] if i in its]
    new_assigned = [i for i in assigned if i not in seen_before]
    used = [i for i in new_assigned if ev.used_in(text, its[i])]
    need = min(3, len(new_assigned))
    if len(used) < need:
        miss = [i for i in new_assigned if i not in used][:6]
        out.append(f"usaste {len(used)} de los datos asignados (mínimo {need}); faltan literales: "
                   + "; ".join(f"[{i}] «{' / '.join(ev.anchors(its[i])) or ev.text_of(its[i])[:50]}»" for i in miss))
    prev_caps = Counter(i for t in previous for i in set(repeat_items(t, pool)))
    rep = [i for i in repeat_items(text, pool) if prev_caps[i] >= MAX_DATO_CAPS]
    if rep:
        out.append("estos datos ya salieron en 2 caps, no los repitas: "
                   + "; ".join(f"«{' / '.join(ev.anchors(its[i]))}»" for i in rep))
    for p in skeleton.get("personajes") or []:
        if p.get("entra_en_cap") == cap:
            named, role = names_with_role(text, p)
            if not named or not role:
                out.append(f"nombrá a {p['nombre']} por nombre y apellido y con su cargo ({p.get('rol')}) la primera vez")
    crono = sorted((i for i in used if its[i]["_kind"] == "cronologia"), key=lambda i: its[i]["fecha"])
    if len(crono) >= 2:
        pos = [min(m.start() for a in ev.anchors(its[i]) for m in re.finditer(re.escape(ev.norm(a)), ev.norm(text)))
               for i in crono]
        if pos != sorted(pos):
            out.append("narrá los eventos en orden de fecha y decí las fechas: "
                       + " → ".join(f"{ev.spoken_date(its[i]['fecha'])}" for i in crono))
    for i in used_items(text, pool, kinds=("citas",)):
        q = its[i]
        m = re.search(re.escape(ev.norm(q["texto"])), ev.norm(text))
        k = ev.norm(text).find(ev.norm(q["texto"])[:12])
        quoted = k >= 0 and bool(re.search(r"[\"“«]", text[max(0, k - 40):k + 1]))     # la comilla abre antes
        near = m and ev.literal_in(ev._surname(q["autor"]), ev.norm(text)[max(0, m.start() - 150):m.end() + 150])
        if not quoted or not near:
            out.append(f"la cita «{q['texto'][:40]}…» va entre comillas y con su autor ({q['autor']}) al lado")
    cm = cap_metrics(text, pool)
    if new_assigned and cm["densidad"] < DENSITY_MIN:
        out.append(f"densidad {cm['densidad']} datos/100 palabras (mínimo {DENSITY_MIN}): más datos literales del pool, "
                   "menos descripción")
    if cm["adj_100"] > ADJ_MAX:
        out.append(f"{cm['adj_100']} adjetivos/100 palabras (máximo {ADJ_MAX}): sacá adjetivos — "
                   + ", ".join(dict.fromkeys(adjectives(text)))[:160])
    bad = forbidden_filler(text)
    if bad:
        out.append(f"relleno prohibido: {', '.join(bad)}")
    if filler_run(text, pool) > FILLER_RUN_MAX:
        out.append(f"más de {FILLER_RUN_MAX} oraciones seguidas que califican sin dato: cambiá adjetivos por hechos")
    cid = ch.get("cliffhanger")
    if cap <= 6 and cid and cid in its and not closing_hits_cliffhanger(text, its[cid]):
        out.append(f"el cierre tiene que anticipar el dato concreto del cap {cap + 1}: «{ev.text_of(its[cid])[:90]}» "
                   f"(nombralo o dejalo incompleto; nada de retórica genérica)")
    return out
