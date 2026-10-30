"""
m09_packaging.py — m09a: PAQUETE de publicación (F58: 3 paquetes título + texto + foto).

Flujo en DOS pasos con gate humano en el medio:
  1) python -m script_engine.m09_packaging <topic_id> --candidates
       → Opus (MODELO_CASILLEROS) lee el GANCHO (cap 1 entero), la narración (caps 2–7) y el POOL y devuelve
         N_PAQUETES paquetes, cada uno una unidad: título + texto de miniatura + la oración del gancho que muestra
         la foto. La foto de cada paquete sale de la máquina de fotos de producción (casilleros Opus + armado +
         canon, `m03_visual._render_prompts_seedream` del cap 1 con las anclas) más `COMPOSICION_MINIATURA`,
         sin cartel. Las cifras del título y del texto se cotejan por código contra el pool (aviso, no freno).
       → publish/thumb_candidates/paquete_NN_base.png + paquete_NN.png (compuesta) y publish/metadata.json
         (`paquetes` acumula con índice global, `descripcion`, `tags`, `avisos`). PARA. Omar revisa (--review).
  2) python -m script_engine.m09_packaging <topic_id> --compose --paquete N [--base <archivo>] [--text "TEXTO"]
       → thumb_final.png + metadata.json(final) + CHECKLIST_PUBLICACION.md.

Entradas: `_steps/<tid>/01b_narration.json`, `_steps/<tid>/00_pool_v3.json`, `_steps/<tid>/01a_skeleton.json` y el
topic de topics_db con su canon (`fase1_5._load_topic_by_id` + `asegurar_canon`), como en producción. Si falta un
archivo: PARADA (`PaquetesParada`) con su nombre, sin volver a nada viejo.

Texto encima (A5): zona = mitad izquierda (THUMB_W // 2 − THUMB_MARGIN), abajo; las líneas se parten por ancho medido
(`textbbox` con el borde) y la letra baja de a 1 px desde 108 hasta el piso 75 (tope 2 líneas); si no cabe, se compone
en 75 y se avisa. Fuente bundleada (Anton OFL en script_engine/fonts/), NO depende de fuentes del sistema.

Salida: output/<topic_id>/publish/.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
import webbrowser
from functools import lru_cache
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

from config import OUTPUT_DIR
from script_engine.m01a_skeleton import STEPS_DIR

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ═══════════════════════════════════════════════════════════════
#  KNOBS (constantes — no hardcodear inline)
# ═══════════════════════════════════════════════════════════════
THUMB_W, THUMB_H = 1280, 720
THUMB_FONT_PATH = Path(__file__).parent / "fonts" / "Anton-Regular.ttf"
THUMB_TEXT_SCALE = 0.15          # alto de fuente por línea ≈ 15% del alto del thumb (108 px)
THUMB_STROKE_PX = 8              # borde negro (≥6px a 1280×720)
THUMB_POSITION = "bottom-left"   # mitad izquierda, abajo (esquina inf-DER libre = duración YT)
THUMB_MARGIN = 56

# Color del texto del overlay (stroke negro SIEMPRE). Default blanco.
THUMB_FILL_BLANCO = (255, 255, 255)
THUMB_FILL_AMARILLO = (255, 214, 0)
THUMB_FILL_ROJO = (231, 29, 29)
THUMB_FILLS = {"blanco": THUMB_FILL_BLANCO, "amarillo": THUMB_FILL_AMARILLO, "rojo": THUMB_FILL_ROJO}
THUMB_FILL_DEFAULT = "blanco"
THUMB_MAX_BYTES = 2 * 1024 * 1024
THUMB_MAX_LINES = 2
THUMB_SIZE_FACTOR_MIN, THUMB_SIZE_FACTOR_MAX = 0.7, 1.6   # clamp de `size_factor` (HANDOFF_137d §3.c)

# F58: zona del texto = mitad izquierda; piso de la letra = el clamp 0,7 del size_factor sobre los 108 px.
THUMB_TEXT_ZONE_W = THUMB_W // 2 - THUMB_MARGIN                              # 584
THUMB_FONT_PX = int(THUMB_H * THUMB_TEXT_SCALE)                              # 108
THUMB_FONT_PX_MIN = int(THUMB_H * THUMB_TEXT_SCALE * THUMB_SIZE_FACTOR_MIN)  # 75
AVISO_NO_CABE = "⚠ no cabe"

MAX_TITLE_CHARS = 90
MAX_TAGS_CHARS = 450
N_PAQUETES = 3          # F58 (Omar 23:23): 3 paquetes por tanda (reemplaza a la cantidad de frescas, = 3)

# F58 A3 (origen: la CAPA CTR del hero viejo + la mitad de la decisión 23:23). Excepción declarada a D4 (LR_RE no la
# toca: «fills the right half of the frame» / «the left half is dark» no matchean sus alternativas).
COMPOSICION_MINIATURA = ("The person fills the right half of the frame, face and torso large; "
                         "the left half is dark, uncluttered negative space.")

# F58 A2: el pedido de paquetes, íntegro como el handoff ({n} = N_PAQUETES).
PEDIDO_PAQUETES = """Armás el empaquetado de un video documental de historia oscura en español neutro-latino: el título de YouTube, el texto que va sobre la miniatura y la oración del gancho que muestra la foto de la miniatura. Todo sale del material de abajo: un dato que no está en el POOL no existe.

Devolvé {n} PAQUETES. Cada paquete es una unidad: título, texto de la miniatura y foto. Cada paquete usa una estrategia distinta, elegida de esta lista: (1) dato brutal o cifra, (2) misterio o pregunta, (3) acusación, (4) lugar y año, (5) contradicción o ironía histórica, (6) consecuencia humana.

Por paquete:
- estrategia: el número de la lista.
- titulo: hasta 70 caracteres, con el gancho al principio. Toda cifra, fecha o nombre sale tal cual de un ítem del POOL.
- dato_ids: los ids de los ítems del POOL de los que salen el título y el texto.
- texto: de 2 a 4 palabras en MAYÚSCULAS para encima de la miniatura. No describe la foto ni repite el título: abre una pregunta que solo el video responde.
- cap_que_paga: el número del cap cuya narración responde el texto.
- ancla: la oración del GANCHO que muestra la foto, copiada tal cual; una oración distinta en cada paquete.

descripcion: de 150 a 300 palabras. La primera oración es el gancho, sin mentir; después, contexto fiel al material y una línea de cierre del canal.
tags: la mayoría en español y de 3 a 5 en inglés; los nombres propios sirven en los dos idiomas; entre todos, hasta 450 caracteres.

GANCHO (la narración del cap 1 entera; la primera oración del título y el sujeto de la miniatura salen del GANCHO):
{gancho}

NARRACIÓN (caps 2 a 7):
{narracion}

POOL (única fuente de cifras, fechas y nombres):
{pool}"""

ESQUEMA_PAQUETES = {
    "type": "OBJECT",
    "properties": {
        "paquetes": {
            "type": "ARRAY",
            "items": {
                "type": "OBJECT",
                "properties": {
                    "estrategia": {"type": "INTEGER"},
                    "titulo": {"type": "STRING"},
                    "dato_ids": {"type": "ARRAY", "items": {"type": "STRING"}},
                    "texto": {"type": "STRING"},
                    "cap_que_paga": {"type": "INTEGER"},
                    "ancla": {"type": "STRING"},
                },
                "required": ["estrategia", "titulo", "dato_ids", "texto", "cap_que_paga", "ancla"],
            },
        },
        "descripcion": {"type": "STRING"},
        "tags": {"type": "ARRAY", "items": {"type": "STRING"}},
    },
    "required": ["paquetes", "descripcion", "tags"],
}

# F4b §4: crédito fijo de los íconos de la capa gráfica (game-icons.net CC BY 3.0 exige atribución)
ICON_CREDIT = "Íconos: game-icons.net (CC BY 3.0) · Lucide (MIT)"

CAPS_PAQUETES = range(2, 8)     # la NARRACIÓN del pedido: caps 2 a 7


class PaquetesParada(RuntimeError):
    """Falta un archivo de entrada, Opus no devolvió paquetes válidos en MAX_RETRY_ATTEMPTS o la API se negó: PARADA."""


class PaquetesInvalidos(ValueError):
    """Un intento de Opus no pasó la validación por código (se reintenta con el motivo)."""


# ═══════════════════════════════════════════════════════════════
#  Paths
# ═══════════════════════════════════════════════════════════════
def _assets_dir(tid: str) -> Path:
    return OUTPUT_DIR / tid / "assets"


def _publish_dir(tid: str) -> Path:
    return OUTPUT_DIR / tid / "publish"


def _candidates_dir(tid: str) -> Path:
    return _publish_dir(tid) / "thumb_candidates"


def _final_mp4(tid: str) -> Path:
    # ⚠ _final_v3_ZOOM.mp4, NO {id}_final.mp4 (ese es el stale del chat 54)
    return OUTPUT_DIR / tid / f"{tid}_final_v3_ZOOM.mp4"


def _steps_dir(tid: str) -> Path:
    return STEPS_DIR / tid


# ═══════════════════════════════════════════════════════════════
#  A1 — entradas (narración, pool, skeleton; PARADA si falta algo)
# ═══════════════════════════════════════════════════════════════
def _leer_json(tid: str, nombre: str) -> dict:
    p = _steps_dir(tid) / nombre
    if not p.exists():
        raise PaquetesParada(f"PARADA: falta {p}")
    return json.loads(p.read_text(encoding="utf-8"))


def cargar_narracion(tid: str) -> dict:
    return _leer_json(tid, "01b_narration.json")


def cargar_pool(tid: str) -> dict:
    return _leer_json(tid, "00_pool_v3.json")


def cargar_skeleton(tid: str) -> dict:
    return _leer_json(tid, "01a_skeleton.json")


def _cap(narracion: dict, n: int) -> str:
    c = next((c for c in narracion.get("chapters", []) if c.get("chapter_number") == n), None)
    return ((c or {}).get("narration") or "").strip()


def gancho(narracion: dict) -> str:
    """La narración del cap 1 entera (el GANCHO), sin truncar."""
    return _cap(narracion, 1)


def bloque_narracion(narracion: dict) -> str:
    """`[Cap N] <narración>` por cap 2–7, sin truncar."""
    return "\n\n".join(f"[Cap {n}] {_cap(narracion, n)}" for n in CAPS_PAQUETES if _cap(narracion, n))


def lineas_pool(pool: dict) -> list[str]:
    """Una línea por ítem, ids tal cual, en el orden D / T / citas / P / L; `cifras_canonicas` (si hay) en JSON
    compacto, una por línea, al final. Entran todos los ítems (incluidas las citas verificada_parcial)."""
    from script_engine.m03_expediente import linea_cita
    out: list[str] = []
    for d in pool.get("datos") or []:
        out.append(f"{d.get('id')}: {d.get('texto')}")
    for t in pool.get("cronologia") or []:
        out.append(f"{t.get('id')} · {t.get('fecha') or '-'} · {t.get('evento')}")
    for q in pool.get("citas") or []:
        out.append(f"{q.get('id')}: {linea_cita(q)}")
    for p in pool.get("personajes") or []:
        out.append(f"{p.get('id')}: {p.get('nombre')} — {p.get('rol')}")
    for l in pool.get("lugares") or []:
        out.append(f"{l.get('id')}: {l.get('nombre')} — {l.get('rol')}")
    for c in pool.get("cifras_canonicas") or []:
        out.append(json.dumps(c, ensure_ascii=False, separators=(",", ":")))
    return out


def bloque_pool(pool: dict) -> str:
    return "\n".join(lineas_pool(pool))


def textos_pool(pool: dict) -> dict[str, str]:
    """`id → texto` de los ítems del pool (para mostrar los `dato_ids` de cada paquete)."""
    out: dict[str, str] = {}
    for ln in lineas_pool(pool):
        m = re.match(r"([A-Z]\d+)(?::| ·) (.*)", ln)
        if m:
            out[m.group(1)] = m.group(2)
    return out


def armar_pedido(narracion: dict, pool: dict, n: int = N_PAQUETES) -> str:
    """El usuario de A2 entero (PEDIDO_PAQUETES con gancho, narración y pool)."""
    return PEDIDO_PAQUETES.format(n=n, gancho=gancho(narracion), narracion=bloque_narracion(narracion),
                                  pool=bloque_pool(pool))


# ═══════════════════════════════════════════════════════════════
#  A2 — pedido a Opus + validación por código con reintentos
# ═══════════════════════════════════════════════════════════════
def _norm_ws(s: str) -> str:
    return " ".join((s or "").split())


def oraciones(texto: str) -> list[str]:
    """Las oraciones del gancho (corte en . ! ? … seguido de espacio o fin de párrafo), con espacios normalizados."""
    out = []
    for parrafo in re.split(r"\n+", texto or ""):
        for s in re.split(r"(?<=[.!?…])\s+", parrafo):
            if _norm_ws(s):
                out.append(_norm_ws(s))
    return out


def validar_paquetes(data: Any, gancho_txt: str, n: int = N_PAQUETES) -> dict:
    """Lo que el esquema no exige: exactamente n paquetes, campos llenos, estrategias distintas, cada ancla una
    oración literal del gancho (espacios normalizados) y anclas distintas. Lanza PaquetesInvalidos con el motivo."""
    if not isinstance(data, dict):
        raise PaquetesInvalidos("la respuesta no es un objeto")
    paqs = data.get("paquetes")
    if not isinstance(paqs, list) or len(paqs) != n:
        got = len(paqs) if isinstance(paqs, list) else "no-lista"
        raise PaquetesInvalidos(f"se esperaban EXACTAMENTE {n} paquetes, llegaron {got}")
    if not _norm_ws(str(data.get("descripcion") or "")):
        raise PaquetesInvalidos("descripcion vacía")
    if not [t for t in (data.get("tags") or []) if _norm_ws(str(t))]:
        raise PaquetesInvalidos("tags vacíos")
    frases = set(oraciones(gancho_txt))
    estrategias, anclas = [], []
    for i, p in enumerate(paqs, start=1):
        if not isinstance(p, dict):
            raise PaquetesInvalidos(f"paquete {i}: no es objeto")
        for k in ("estrategia", "titulo", "dato_ids", "texto", "cap_que_paga", "ancla"):
            v = p.get(k)
            if v is None or (isinstance(v, str) and not v.strip()) or (isinstance(v, list) and not v):
                raise PaquetesInvalidos(f"paquete {i}: campo '{k}' vacío")
        if p["estrategia"] in estrategias:
            raise PaquetesInvalidos(f"paquete {i}: estrategia {p['estrategia']} repetida (tienen que ser distintas)")
        estrategias.append(p["estrategia"])
        ancla = _norm_ws(str(p["ancla"]))
        if ancla not in frases:
            raise PaquetesInvalidos(f"paquete {i}: el ancla no es una oración literal del GANCHO: «{ancla[:90]}»")
        if ancla in anclas:
            raise PaquetesInvalidos(f"paquete {i}: ancla repetida (una oración distinta en cada paquete)")
        anclas.append(ancla)
    return data


def with_icon_credit(desc: str) -> str:
    desc = str(desc).rstrip()
    return desc if ICON_CREDIT in desc else (f"{desc}\n\n{ICON_CREDIT}" if desc else ICON_CREDIT)


def _truncate_tags(tags: list[str], max_chars: int) -> list[str]:
    """Recorta la lista de tags para que la suma (con comas) ≤ max_chars (regla YouTube)."""
    out: list[str] = []
    total = 0
    for t in tags:
        add = len(t) + (1 if out else 0)  # coma separadora
        if total + add > max_chars:
            break
        out.append(t)
        total += add
    return out


def normalizar_paquetes(data: dict) -> dict:
    """Después de validar: titulo[:MAX_TITLE_CHARS], texto en MAYÚSCULAS, ancla con espacios normalizados,
    `_truncate_tags` y `with_icon_credit`."""
    paqs = []
    for p in data.get("paquetes") or []:
        paqs.append({
            "estrategia": int(p.get("estrategia")),
            "titulo": str(p.get("titulo") or "").strip()[:MAX_TITLE_CHARS],
            "dato_ids": [str(x).strip() for x in (p.get("dato_ids") or []) if str(x).strip()],
            "texto": str(p.get("texto") or "").strip().upper(),
            "cap_que_paga": int(p.get("cap_que_paga")),
            "ancla": _norm_ws(str(p.get("ancla") or "")),
        })
    desc = with_icon_credit(str(data.get("descripcion", "")).strip())
    tags = _truncate_tags([str(t).strip() for t in (data.get("tags") or []) if str(t).strip()], MAX_TAGS_CHARS)
    return {"paquetes": paqs, "descripcion": desc, "tags": tags}


def _llamar_paquetes(prompt: str) -> Any:
    """La llamada a Opus (MODELO_CASILLEROS, effort de guion_v4), sin system_instruction."""
    import claude_helpers
    from script_engine import guion_v4
    from script_engine.m03_visual import MODELO_CASILLEROS
    return claude_helpers.call_json(prompt, model=MODELO_CASILLEROS, system_instruction=None,
                                    response_schema=ESQUEMA_PAQUETES, effort=guion_v4.ESFUERZO[MODELO_CASILLEROS],
                                    description="m09:paquetes")


def pedir_paquetes(narracion: dict, pool: dict, n: int = N_PAQUETES) -> dict:
    """Pide los paquetes a Opus y valida por código; reintenta MAX_RETRY_ATTEMPTS veces con el motivo (al estilo de
    `_call_with_validation_retry`); si fallan todos o la API se niega → PaquetesParada. Devuelve lo normalizado."""
    import claude_helpers
    from script_engine.m03_visual import MAX_RETRY_ATTEMPTS
    prompt = armar_pedido(narracion, pool, n)
    gancho_txt = gancho(narracion)
    intento = prompt
    ultimo: Exception | None = None
    for attempt in range(1, MAX_RETRY_ATTEMPTS + 1):
        try:
            raw = _llamar_paquetes(intento)
        except claude_helpers.ClaudeError as e:
            raise PaquetesParada(f"PARADA: Opus no devolvió los paquetes: {e}") from e
        try:
            return normalizar_paquetes(validar_paquetes(raw, gancho_txt, n))
        except (PaquetesInvalidos, ValueError, TypeError) as e:
            ultimo = e
            print(f"  [09] paquetes: validación falló intento {attempt}/{MAX_RETRY_ATTEMPTS}: {str(e)[:120]}")
            intento = (prompt + f"\n\nRETRY {attempt + 1}/{MAX_RETRY_ATTEMPTS} — TU INTENTO PREVIO FALLÓ: {e}\n"
                       f"Devolvé de nuevo los {n} paquetes completos cumpliendo TODAS las reglas de arriba.\n")
    raise PaquetesParada(f"PARADA: los paquetes no pasaron la validación en {MAX_RETRY_ATTEMPTS} intentos: {ultimo}")


# ═══════════════════════════════════════════════════════════════
#  A4 — cifras por código (aviso, no freno)
# ═══════════════════════════════════════════════════════════════
def _clave_numero(x: str):
    from script_engine.num_es import parse_int
    v = parse_int(x)
    return v if v is not None else x


def numeros_pool(pool: dict) -> set:
    """Los números de los ítems del pool (sin el id: «D07» no aporta un 7), más los de `cifras_canonicas`."""
    from script_engine.voz_utils import numeros
    textos = list(textos_pool(pool).values()) + [json.dumps(c, ensure_ascii=False) for c in pool.get("cifras_canonicas") or []]
    return {_clave_numero(x) for t in textos for x in numeros(t)}


def avisos_cifras(paquete: dict, pool_nums: set) -> list[str]:
    """Cada número del título y del texto (`voz_utils.numeros` + `parse_int`) tiene que estar entre los del pool;
    si no: «⚠ cifra sin dato: <número>». `dato_ids` solo se muestra."""
    from script_engine.voz_utils import numeros
    out: list[str] = []
    for campo in ("titulo", "texto"):
        for x in numeros(paquete.get(campo) or ""):
            if _clave_numero(x) not in pool_nums:
                aviso = f"⚠ cifra sin dato: {x}"
                if aviso not in out:
                    out.append(aviso)
    return out


# ═══════════════════════════════════════════════════════════════
#  A3 (desde m09) — la foto del paquete por la máquina de producción
# ═══════════════════════════════════════════════════════════════
def topic_produccion(tid: str, narracion: dict) -> dict:
    """El topic como lo recibe m03 en producción: topics_db + `asegurar_canon` + `_f8` (m03_visual:2153-2158)."""
    import fase1_5
    from script_engine import m03_expediente as mexp
    from script_engine import m03_imagenes_v3 as v3img
    from script_engine.m03_visual import EXPECTED_CHAPTER_COUNT
    topic = fase1_5._load_topic_by_id(tid)
    log: list[str] = []
    topic = fase1_5.asegurar_canon(tid, topic, log)
    if log:
        print("\n".join(log))
    beats = v3img.load_beats(topic, STEPS_DIR)
    if beats:
        topic = {**topic, "_f8": {"beats": beats, "year": v3img.topic_year(topic, beats),
                                  "lang": v3img.place_language(topic),
                                  "fuentes": mexp.fuentes(tid, STEPS_DIR),
                                  "anio_prev": {n: mexp.anio_previo(narracion.get("chapters") or [], n)
                                                for n in range(1, EXPECTED_CHAPTER_COUNT + 1)}}}
    return topic


def prompts_paquetes(tid: str, narracion: dict, anclas: list[str], topic: dict | None = None) -> list[dict]:
    """Los prompts de las fotos: `_render_prompts_seedream` del cap 1 con las anclas en UNA llamada de casilleros,
    con el reparto a beats como `_f8_refill` (refill=True + force_assign), sin el bloque del clip de apertura, sin
    cartel y con COMPOSICION_MINIATURA. Un ítem por ancla, en orden (prompt, raw_llm_prompt, …)."""
    from script_engine import m03_imagenes_v3 as v3img
    from script_engine import m03_visual as m3
    topic = topic or topic_produccion(tid, narracion)
    sk = cargar_skeleton(tid)
    cap_data = next((c for c in sk.get("chapters", []) if c.get("chapter_number") == 1), None)
    if not cap_data:
        raise PaquetesParada(f"PARADA: {_steps_dir(tid) / '01a_skeleton.json'} no trae el cap 1")
    narr1 = gancho(narracion)
    f8 = topic.get("_f8") or {}
    cap_beats = (f8.get("beats") or {}).get(1) or []
    f8 = dict(f8, refill=True, force_assign=v3img.assign_beats(narr1, anclas, cap_beats))
    plan = {"anchors": [{"anchor": a} for a in anclas]}
    out = m3._render_prompts_seedream({**topic, "_f8": f8}, cap_data, narr1, plan, 1,
                                      composicion=COMPOSICION_MINIATURA, sin_cartel=True, clip_apertura=False)
    return list(out["image_prompts"])


def foto_paquete(prompt: str, out_path: Path) -> str | None:
    """Genera la foto con el motor de producción (`_generate_image_raw`, use_ultra=False). Devuelve None si salió o el
    motivo literal (ContentRejectedError u otro error): el paquete queda sin foto y los otros siguen."""
    import asset_manager as am
    out_path.parent.mkdir(parents=True, exist_ok=True)
    try:
        am._generate_image_raw(prompt, out_path, use_ultra=False)
        return None
    except Exception as e:  # noqa: BLE001 — el motivo literal va al paquete
        return f"{type(e).__name__}: {e}"


# ═══════════════════════════════════════════════════════════════
#  A5 — OVERLAY (Pillow): texto en la mitad izquierda, partido por ancho
# ═══════════════════════════════════════════════════════════════
def _fit_cover(im: Image.Image, w: int, h: int, focus: str = "center") -> Image.Image:
    """Escala (cover) + crop a (w,h). `focus` controla la franja VERTICAL del crop en
    fuentes verticales: 'center' (default), 'top' (preserva el tercio superior — caras
    altas), 'bottom'. Horizontal siempre centrado."""
    im = im.convert("RGB")
    scale = max(w / im.width, h / im.height)
    nw, nh = round(im.width * scale), round(im.height * scale)
    im = im.resize((nw, nh), Image.LANCZOS)
    left = (nw - w) // 2
    if focus == "top":
        top = 0
    elif focus == "bottom":
        top = nh - h
    else:
        top = (nh - h) // 2
    return im.crop((left, top, left + w, top + h))


@lru_cache(maxsize=None)
def _font(px: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(THUMB_FONT_PATH), px)


_MEDIDOR = ImageDraw.Draw(Image.new("RGB", (1, 1)))


def ancho_linea(linea: str, px: int) -> int:
    """Ancho de una línea con el borde (`textbbox(..., stroke_width=THUMB_STROKE_PX)`)."""
    b = _MEDIDOR.textbbox((0, 0), linea, font=_font(px), stroke_width=THUMB_STROKE_PX)
    return b[2] - b[0]


def _cortes(palabras: list[str]) -> list[list[str]]:
    """Las particiones candidatas: 1 línea y cada corte posible en 2 (tope THUMB_MAX_LINES), en orden de desempate
    (1 línea primero, después el corte más a la izquierda)."""
    out = [[" ".join(palabras)]]
    if THUMB_MAX_LINES >= 2:
        for i in range(1, len(palabras)):
            out.append([" ".join(palabras[:i]), " ".join(palabras[i:])])
    return out


def partir_texto(text: str, size_factor: float = 1.0) -> tuple[list[str], int, str]:
    """Líneas y tamaño del texto de la miniatura. Desde int(108 × size_factor) (sin bajar del piso) baja de a 1 px
    hasta el piso 75; en cada tamaño gana el corte de menor ancho máximo (desempate: 1 línea, después el corte más
    a la izquierda); el primer tamaño en que cabe en la zona (584 px) gana. Si no cabe en 75: se compone en 75 y
    aviso «⚠ no cabe». Devuelve (lineas, px, aviso)."""
    palabras = (text or "").upper().split()
    if not palabras:
        return [], THUMB_FONT_PX, ""
    sf = max(THUMB_SIZE_FACTOR_MIN, min(THUMB_SIZE_FACTOR_MAX, float(size_factor or 1.0)))
    inicio = max(THUMB_FONT_PX_MIN, int(THUMB_H * THUMB_TEXT_SCALE * sf))
    mejor: list[str] = []
    for px in range(inicio, THUMB_FONT_PX_MIN - 1, -1):
        mejor = min(_cortes(palabras), key=lambda ls: max(ancho_linea(l, px) for l in ls))   # min = primer empate
        if max(ancho_linea(l, px) for l in mejor) <= THUMB_TEXT_ZONE_W:
            return mejor, px, ""
    return mejor, THUMB_FONT_PX_MIN, AVISO_NO_CABE


def compose_thumbnail(base_path: Path, text: str, out_path: Path, focus: str = "center",
                      fill: str = THUMB_FILL_DEFAULT, size_factor: float = 1.0) -> Path:
    """Compone la miniatura final 1280×720 con el texto encima (Anton, color `fill` + stroke negro) en la mitad
    izquierda, abajo (esquina inf-DER libre). Las líneas y el tamaño salen de `partir_texto` (si no cabe, avisa).
    `fill` ∈ {blanco, amarillo, rojo}. `focus` controla el cover-crop de bases verticales. Devuelve el path realmente
    escrito (puede ser .jpg si el PNG superaba 2MB). Sin red — testeable."""
    base = _fit_cover(Image.open(base_path), THUMB_W, THUMB_H, focus)
    draw = ImageDraw.Draw(base)
    lines, font_px, aviso = partir_texto(text, size_factor)
    color = THUMB_FILLS.get(fill, THUMB_FILLS[THUMB_FILL_DEFAULT])
    if aviso:
        print(f"  {aviso}: «{text}» a {font_px} px")

    if lines:
        font = _font(font_px)
        line_h = font_px + 10
        total_h = line_h * len(lines)
        y = THUMB_H - THUMB_MARGIN - total_h   # abajo, mitad izquierda
        for ln in lines:
            draw.text((THUMB_MARGIN, y), ln, font=font, fill=color,
                      stroke_width=THUMB_STROKE_PX, stroke_fill=(0, 0, 0))
            y += line_h

    out_path.parent.mkdir(parents=True, exist_ok=True)
    base.save(out_path, "PNG", optimize=True)
    if out_path.stat().st_size <= THUMB_MAX_BYTES:
        return out_path
    # PNG > 2MB → fallback JPEG bajando calidad (YouTube acepta jpg <2MB)
    jpg = out_path.with_suffix(".jpg")
    for q in (92, 88, 84, 80, 75):
        base.save(jpg, "JPEG", quality=q)
        if jpg.stat().st_size <= THUMB_MAX_BYTES:
            break
    out_path.unlink(missing_ok=True)
    print(f"  ⚠ PNG superaba 2MB → usé {jpg.name} (q≤92)")
    return jpg


def _validate_text(text: str) -> str:
    n = len((text or "").split())
    if n == 0:
        raise ValueError("--text vacío. Pasá 2-4 palabras en MAYÚSCULAS.")
    if n > 5:
        print(f"  ⚠ --text tiene {n} palabras (>5): puede quedar ilegible en miniatura.")
    return text


def next_thumb_name(tid: str) -> str:
    """Próximo thumb_final_NN.png versionado (el form compone varias veces; Omar compara)."""
    pub = _publish_dir(tid)
    nums = [int(p.stem.rsplit("_", 1)[1]) for p in pub.glob("thumb_final_*.png")
            if p.stem.rsplit("_", 1)[1].isdigit()]
    return f"thumb_final_{(max(nums) + 1) if nums else 1:02d}.png"


# ═══════════════════════════════════════════════════════════════
#  A6 — bases: la foto del paquete o cualquier foto del video
# ═══════════════════════════════════════════════════════════════
def bases_del_video(tid: str) -> list[str]:
    """Las fotos del video como bases alternativas: las `*_graded.png` de `_assets_dir(tid)`, o la cruda si no tiene
    graded. Rutas relativas a assets/, con prefijo `assets/` (así las resuelve `_resolve_base`)."""
    adir = _assets_dir(tid)
    if not adir.exists():
        return []
    pngs = sorted(adir.rglob("*.png"))
    graded = {p.with_name(p.stem[:-len("_graded")] + ".png") for p in pngs if p.stem.endswith("_graded")}
    out = []
    for p in pngs:
        if not p.stem.endswith("_graded") and p in graded:
            continue                                   # tiene graded → va la graded
        out.append("assets/" + p.relative_to(adir).as_posix())
    return out


def _dentro(p: Path, raiz: Path) -> bool:
    try:
        p.resolve().relative_to(raiz.resolve())
        return True
    except ValueError:
        return False


def _resolve_base(tid: str, base: str) -> Path:
    """`assets/<rel>` → foto del video; si no, un archivo de thumb_candidates/ (o publish/). Solo rutas dentro de
    `_assets_dir(tid)`, `thumb_candidates/` y `publish/`."""
    base = str(base or "").replace("\\", "/")
    if base.startswith("assets/"):
        p = _assets_dir(tid) / base[len("assets/"):]
        if not _dentro(p, _assets_dir(tid)):
            raise FileNotFoundError(f"Base fuera de assets/: {base}")
        return p
    p = Path(base)
    if not p.is_absolute():
        p = _candidates_dir(tid) / base
        if not p.exists() and (_publish_dir(tid) / base).exists():
            p = _publish_dir(tid) / base
    if not (_dentro(p, _assets_dir(tid)) or _dentro(p, _publish_dir(tid))):
        raise FileNotFoundError(f"Base fuera de assets/ y publish/: {base}")
    return p


# ═══════════════════════════════════════════════════════════════
#  A7 — PASO 1: candidates (paquetes + fotos + compuestas + metadata.json)
# ═══════════════════════════════════════════════════════════════
def _leer_meta(tid: str) -> dict:
    mp = _publish_dir(tid) / "metadata.json"
    if not mp.exists():
        return {}
    try:
        meta = json.loads(mp.read_text(encoding="utf-8"))
        return meta if isinstance(meta, dict) else {}
    except (json.JSONDecodeError, OSError):
        return {}


def _escribir_meta(tid: str, meta: dict) -> None:
    pub = _publish_dir(tid)
    pub.mkdir(parents=True, exist_ok=True)
    meta["avisos"] = [f"paquete {p['n']:02d}: {a}" for p in meta.get("paquetes", []) for a in p.get("avisos", [])]
    (pub / "metadata.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")


def candidates_ready(tid: str) -> bool:
    """True si metadata.json existe y trae la clave `paquetes` (F58)."""
    return "paquetes" in _leer_meta(tid)


def _nombre_base(n: int) -> str:
    return f"paquete_{n:02d}_base.png"


def _nombre_compuesta(n: int) -> str:
    return f"paquete_{n:02d}.png"


def _componer_paquete(tid: str, p: dict) -> None:
    """Compone paquete_NN.png desde la base del paquete (su foto u otra elegida) con su texto; sin red. Deja en el
    paquete `miniatura` y el aviso «⚠ no cabe» si corresponde (los otros avisos se conservan)."""
    cand = _candidates_dir(tid)
    avisos = [a for a in p.get("avisos", []) if a != AVISO_NO_CABE]
    p["miniatura"] = None
    if p.get("base"):
        try:
            base_path = _resolve_base(tid, p["base"])
            if base_path.exists():
                _lines, _px, aviso = partir_texto(p.get("texto") or "")
                written = compose_thumbnail(base_path, p.get("texto") or "", cand / _nombre_compuesta(p["n"]))
                p["miniatura"] = written.name
                if aviso:
                    avisos.append(aviso)
        except (FileNotFoundError, OSError) as e:
            avisos.append(f"⚠ base no se pudo componer: {e}")
    p["avisos"] = avisos


def _foto_del_paquete(tid: str, p: dict, item: dict | None, motivo: str | None = None) -> None:
    """Genera la foto del paquete desde su ítem de casilleros (`prompt`, `raw_llm_prompt`) y la deja como base."""
    cand = _candidates_dir(tid)
    p["foto"], p["motivo_sin_foto"] = None, motivo
    if item is None:
        p["base"] = p.get("base")
        return
    p["prompt"] = item.get("prompt")
    p["raw_llm_prompt"] = item.get("raw_llm_prompt")
    p["anio"], p["anio_fuente"] = item.get("anio"), item.get("anio_fuente")
    for k in ("_f8_problemas", "_f8_texto_fuera"):
        if item.get(k):
            p[k] = item[k]
    err = foto_paquete(item["prompt"], cand / _nombre_base(p["n"]))
    if err:
        p["motivo_sin_foto"] = err
    else:
        p["foto"] = _nombre_base(p["n"])
        p["base"] = p["foto"]


def run_candidates(tid: str, video_path: str | None = None, review: bool = False) -> None:
    """Paso 1 (F58): N_PAQUETES paquetes de Opus (validados), cifras cotejadas, la foto de cada uno por la máquina de
    producción y la compuesta. `metadata.json.paquetes` acumula con índice global (no pisa números); descripción y
    tags son los de la última tanda."""
    narracion, pool = cargar_narracion(tid), cargar_pool(tid)
    cand = _candidates_dir(tid)
    cand.mkdir(parents=True, exist_ok=True)

    print(f"  [m09a] {N_PAQUETES} paquetes (Opus)...")
    nuevo = pedir_paquetes(narracion, pool, N_PAQUETES)

    meta = _leer_meta(tid)
    previos = [p for p in meta.get("paquetes", []) if isinstance(p, dict) and isinstance(p.get("n"), int)]
    start = (max(p["n"] for p in previos) + 1) if previos else 1
    pool_nums, textos = numeros_pool(pool), textos_pool(pool)
    paquetes = []
    for k, p in enumerate(nuevo["paquetes"]):
        p = {"n": start + k, **p}
        p["datos"] = {i: textos.get(i, "(id no está en el pool)") for i in p["dato_ids"]}
        p["avisos"] = avisos_cifras(p, pool_nums)
        p["foto"], p["base"], p["miniatura"], p["motivo_sin_foto"] = None, None, None, None
        paquetes.append(p)
    meta.update({"topic_id": tid, "stage": "candidates", "paquetes": previos + paquetes,
                 "descripcion": nuevo["descripcion"], "tags": nuevo["tags"]})
    _escribir_meta(tid, meta)        # los paquetes quedan en disco antes de las fotos

    print(f"  [m09a] fotos: casilleros + armado (cap 1, {len(paquetes)} anclas)...")
    items = prompts_paquetes(tid, narracion, [p["ancla"] for p in paquetes])
    for p, it in zip(paquetes, items):
        _foto_del_paquete(tid, p, it)
        _componer_paquete(tid, p)
        est = p["foto"] or f"sin foto ({p['motivo_sin_foto']})"
        print(f"     paquete {p['n']:02d} · {p['titulo'][:60]} · «{p['texto']}» · {est}"
              + (" · " + " · ".join(p["avisos"]) if p["avisos"] else ""))
    _escribir_meta(tid, meta)
    print(f"  ✅ candidates en {_publish_dir(tid)}")
    print(f"     Revisá con --review o componé: --compose --paquete N [--base <archivo>] [--text \"TEXTO\"]")
    if review:
        run_review(tid, video_path=video_path)


def _paquete(meta: dict, n: int) -> dict:
    p = next((p for p in meta.get("paquetes", []) if p.get("n") == n), None)
    if not p:
        raise ValueError(f"paquete {n} no existe (hay {[q.get('n') for q in meta.get('paquetes', [])]})")
    return p


def editar_paquete(tid: str, n: int, titulo: str | None = None, texto: str | None = None,
                   base: str | None = None) -> dict:
    """Edita título y/o texto y/o la base del paquete y recompone paquete_NN.png (sin red). Recoteja las cifras."""
    meta = _leer_meta(tid)
    p = _paquete(meta, n)
    if titulo is not None:
        t = titulo.strip()[:MAX_TITLE_CHARS]
        if not t:
            raise ValueError("título vacío")
        p["titulo"] = t
    if texto is not None:
        p["texto"] = _validate_text(texto).strip().upper()
    if base is not None:
        _resolve_base(tid, base)       # valida la ruta
        p["base"] = base
    pool_path = _steps_dir(tid) / "00_pool_v3.json"
    if pool_path.exists():
        p["avisos"] = avisos_cifras(p, numeros_pool(cargar_pool(tid))) + \
            [a for a in p.get("avisos", []) if a == AVISO_NO_CABE]
    _componer_paquete(tid, p)
    _escribir_meta(tid, meta)
    return p


def rehacer_foto(tid: str, n: int) -> dict:
    """«Rehacer foto»: A3 solo para el ancla de ese paquete (casilleros + armado + foto) y recompone."""
    meta = _leer_meta(tid)
    p = _paquete(meta, n)
    narracion = cargar_narracion(tid)
    items = prompts_paquetes(tid, narracion, [p["ancla"]])
    _foto_del_paquete(tid, p, items[0] if items else None, motivo=None if items else "sin ítem de casilleros")
    _componer_paquete(tid, p)
    _escribir_meta(tid, meta)
    return p


# ═══════════════════════════════════════════════════════════════
#  PASO 2 — compose
# ═══════════════════════════════════════════════════════════════
_CHECKLIST_TMPL = """# Checklist de publicación — {title}

## Archivo
- **Video:** `{mp4}`
- **Miniatura:** `{thumb}`

## Pegar en YouTube Studio
**Título:**
{title}

**Descripción:**
{desc}

**Tags:**
{tags}

## Ajustes en Studio
- Idioma del video: **Español**
- Categoría: **Educación** o **Entretenimiento** (Omar decide)
- Audiencia: **No, no es contenido para niños**
- Visibilidad inicial: pública o programada (a elección de Omar)
- Agregar el video a una **playlist** del canal

## Pre-vuelo
- ⚠ Verificar **cap3 sin texto fantasma** antes de subir (pendiente de backlog).
"""


def _open(path_or_url) -> None:
    """Abre un archivo o URL en el navegador (Windows os.startfile / webbrowser fallback)."""
    try:
        s = str(path_or_url)
        if os.name == "nt" and not s.startswith("http"):
            os.startfile(s)  # type: ignore[attr-defined]
        else:
            webbrowser.open(s)
    except Exception as e:
        print(f"  (no pude abrir el navegador: {e} — abrí a mano {path_or_url})")


def run_review(tid: str, video_path: str | None = None, on_compose=None,
               port: int | None = None, open_browser: bool = True,
               auto_generate_if_empty: bool = False) -> None:
    """--review levanta el FORM web local. video_path (de fase3/topics_db) va al CHECKLIST;
    on_compose(thumb_name) se llama tras cada COMPONER exitoso (fase3 lo usa para PACKAGED).
    port/open_browser (HANDOFF_135): el QA Studio lo spawnea con puerto fijo y sin abrir
    pestaña (lo embebe en iframe). Default = comportamiento de siempre (puerto libre + abre).
    auto_generate_if_empty (HANDOFF_136b): primera tanda automática si el topic no tiene
    paquetes (el QA Studio lo usa; ver serve())."""
    from script_engine.m09_review_server import serve
    serve(tid, video_path=video_path, on_compose=on_compose,
          port=port, open_browser=open_browser,
          auto_generate_if_empty=auto_generate_if_empty)


def compose_and_package(tid: str, base: str, text: str, title: str,
                        focus: str = "center", fill: str = THUMB_FILL_DEFAULT,
                        out_name: str = "thumb_final.png",
                        video_path: str | None = None, size_factor: float = 1.0) -> Path:
    """Compone la miniatura final + escribe metadata.json(final) + CHECKLIST. Reusable por el
    CLI (--compose, out_name fijo) y por el form (out_name versionado). `title` es el título
    ELEGIDO (string libre: el del paquete o uno escrito a mano). El CHECKLIST referencia
    `video_path` si viene (fase3 lo resuelve desde topics_db); si no, cae al nombre v3 histórico.
    Devuelve el thumb escrito. Lanza ValueError/FileNotFoundError (el caller decide cómo mostrarlo)."""
    pub = _publish_dir(tid)
    meta = _leer_meta(tid)
    title = (title or "").strip()[:MAX_TITLE_CHARS]
    if not title:
        raise ValueError("título vacío")
    base_path = _resolve_base(tid, base)
    if not base_path.exists():
        raise FileNotFoundError(f"Base no encontrada: {base_path}")
    text = _validate_text(text)

    written = compose_thumbnail(base_path, text, pub / out_name, focus, fill, size_factor)
    meta.update({"stage": "final", "titulo_elegido": title, "texto_elegido": text.strip().upper(),
                 "base_thumb": base, "thumb_final": written.name})
    pub.mkdir(parents=True, exist_ok=True)
    (pub / "metadata.json").write_text(json.dumps(meta, indent=2, ensure_ascii=False), encoding="utf-8")
    checklist = _CHECKLIST_TMPL.format(
        title=title, mp4=video_path or _final_mp4(tid), thumb=written,
        desc=meta.get("descripcion", ""), tags=", ".join(meta.get("tags", [])),
    )
    (pub / "CHECKLIST_PUBLICACION.md").write_text(checklist, encoding="utf-8")
    return written


def run_compose(tid: str, paquete_n: int, base: str | None = None, text: str | None = None,
                focus: str = "center", fill: str = THUMB_FILL_DEFAULT,
                video_path: str | None = None) -> None:
    """CLI: `--compose --paquete N` toma título, texto y base del paquete N (--base/--text los reemplazan)."""
    meta = _leer_meta(tid)
    try:
        p = _paquete(meta, paquete_n)
    except ValueError as e:
        raise SystemExit(f"--paquete {paquete_n} fuera de rango: {e}")
    base = base or p.get("base")
    if not base:
        raise SystemExit(f"el paquete {paquete_n} no tiene foto: pasá --base <archivo>")
    try:
        written = compose_and_package(tid, base, text or p.get("texto") or "", p.get("titulo") or "", focus, fill,
                                      "thumb_final.png", video_path)
    except (ValueError, FileNotFoundError) as e:
        raise SystemExit(str(e))
    print(f"  ✅ thumb_final: {written.name} ({written.stat().st_size//1024} KB)")
    print(f"  ✅ CHECKLIST_PUBLICACION.md + metadata.json (final) en {_publish_dir(tid)}")


# ═══════════════════════════════════════════════════════════════
#  CLI
# ═══════════════════════════════════════════════════════════════
def _resolve_mode(candidates: bool, compose: bool, review: bool) -> str:
    """Valida la combinación de flags y devuelve el modo: 'candidates' | 'compose' | 'review'.
    --review puede acompañar a --candidates (genera y abre el form); solo, abre el form sin
    generar. --compose es excluyente. Lanza ValueError en combinaciones inválidas."""
    if compose and (candidates or review):
        raise ValueError("--compose no se combina con --candidates ni --review")
    if candidates:
        return "candidates"   # review (si viene) se maneja dentro de run_candidates
    if compose:
        return "compose"
    if review:
        return "review"       # form solo, sin generar nada
    raise ValueError("elegí un modo: --candidates, --compose o --review")


def main() -> int:
    ap = argparse.ArgumentParser(description="m09a — paquete de publicación (3 paquetes título + texto + foto).")
    ap.add_argument("topic_id")
    ap.add_argument("--candidates", action="store_true",
                    help=f"Paso 1: {N_PAQUETES} paquetes (Opus) + foto de producción + compuesta por paquete.")
    ap.add_argument("--review", action="store_true",
                    help="Levanta el form web local. Solo (--review) abre el form sin generar; "
                         "junto a --candidates genera y abre el form.")
    ap.add_argument("--compose", action="store_true", help="Paso 2: miniatura final + checklist.")
    ap.add_argument("--paquete", type=int, default=None, help="(--compose) número del paquete elegido.")
    ap.add_argument("--base", help="(--compose) base distinta de la foto del paquete (thumb_candidates/ o assets/...).")
    ap.add_argument("--text", help="(--compose) texto distinto del del paquete (2-4 palabras, MAYÚSCULAS).")
    ap.add_argument("--focus", choices=["top", "center", "bottom"], default="center",
                    help="Franja del cover-crop para bases verticales (default center).")
    ap.add_argument("--fill", choices=list(THUMB_FILLS), default=THUMB_FILL_DEFAULT,
                    help="Color del texto del overlay (stroke negro siempre). Default blanco.")
    ap.add_argument("--video-path", default=None,
                    help="Ruta del MP4 para el CHECKLIST (fase3 la resuelve desde topics_db). "
                         "Si falta, cae al nombre v3 histórico.")
    ap.add_argument("--port", type=int, default=None,
                    help="(HANDOFF_135, modo review) puerto fijo del form; default = libre.")
    ap.add_argument("--no-browser", action="store_true",
                    help="(HANDOFF_135, modo review) NO abrir pestaña (el QA Studio lo embebe).")
    ap.add_argument("--auto-first", action="store_true",
                    help="(HANDOFF_136b, modo review) si el topic no tiene paquetes, generar "
                         "la primera tanda en background al abrir el form.")
    args = ap.parse_args()

    try:
        mode = _resolve_mode(args.candidates, args.compose, args.review)
    except ValueError as e:
        ap.error(str(e))
    if mode == "candidates":
        run_candidates(args.topic_id, video_path=args.video_path, review=args.review)
    elif mode == "compose":
        if args.paquete is None:
            ap.error("--compose requiere --paquete N")
        run_compose(args.topic_id, args.paquete, base=args.base, text=args.text, focus=args.focus,
                    fill=args.fill, video_path=args.video_path)
    else:  # review solo → form (con --auto-first genera la primera tanda si falta)
        run_review(args.topic_id, video_path=args.video_path,
                   port=args.port, open_browser=not args.no_browser,
                   auto_generate_if_empty=args.auto_first)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
