"""
auto_icons.py — Íconos gratis automáticos (F4b §4): game-icons.net (CC BY 3.0) restilizados al look del canal.

  index   (una vez) nombres en inglés del set → palabras en español con Flash, por tandas
          → gfx_profiles/icons/icons_index.json  {slug: {"path": "autor/slug.svg", "es": [palabras]}}
  lookup  palabra de carga CONCRETA → clave "gi:<autor>/<slug>" (palabra exacta, después lema: plural/género)
  svg     clave "gi:…" → SVG restilizado: sin el cuadrado negro de fondo, relleno hueso, clase ic-fill (el filtro de
          tinta y el grano los pone scoped_svg igual que al set propio). Sin rojo: el set de game-icons no tiene un
          «detalle semántico» marcado y pintarlo a ojo sería inventar.
Prioridad (gfx_layer): los 12 propios → game-icons → sin ícono. Flux solo por pedido manual de Omar.

Uso: python script_engine/gfx_icons/auto_icons.py index     (requiere fetch_game_icons.sh antes)
"""
from __future__ import annotations

import json
import re
import sys
import unicodedata
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
GI_DIR: Path = ROOT / "script_engine" / "gfx_runtime" / "icons" / "game-icons"
INDEX: Path = ROOT / "gfx_profiles" / "icons" / "icons_index.json"
BONE = "#e8e0cc"
BATCH = 250
SYSTEM = ("Traducís nombres de íconos (en inglés, con guiones) a palabras en español. Para cada ícono das 1–4 "
          "SUSTANTIVOS en español que nombran LO QUE EL ÍCONO DIBUJA (singular; sin artículos), los más comunes primero. "
          "Si el nombre es abstracto o es un objeto de videojuego sin equivalente común, devolvé lista vacía. "
          "Respondés SOLO JSON.")
SCHEMA = {"type": "OBJECT", "properties": {"items": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
    "n": {"type": "STRING"}, "es": {"type": "ARRAY", "items": {"type": "STRING"}}}, "required": ["n", "es"]}}},
    "required": ["items"]}


def plain(s: str) -> str:
    return "".join(c for c in unicodedata.normalize("NFD", str(s).lower().strip()) if unicodedata.category(c) != "Mn")


def lemmas(word: str) -> list[str]:
    """Formas a buscar: la palabra, sin plural, en masculino. «celdas» → celdas, celda; «ahogadas» → ahogada, ahogado."""
    w = plain(re.sub(r"[^\wáéíóúñü]", "", word.lower()))
    out = [w]
    if w.endswith("es") and len(w) > 4:
        out.append(w[:-2])
    if w.endswith("s") and len(w) > 3:
        out.append(w[:-1])
    for x in list(out):
        if x.endswith("a"):
            out.append(x[:-1] + "o")
    return list(dict.fromkeys(out))


def all_svgs() -> dict[str, str]:
    """slug → ruta relativa (el primer autor si el nombre se repite; lorc primero: es el autor del grueso del set)."""
    out: dict[str, str] = {}
    files = sorted(GI_DIR.glob("*/*.svg"), key=lambda p: (p.parent.name != "lorc", p.parent.name, p.name))
    for p in files:
        out.setdefault(p.stem, f"{p.parent.name}/{p.name}")
    return out


def build_index(call=None) -> dict[str, dict]:
    if call is None:
        sys.path.insert(0, str(ROOT))
        from gemini_helpers import call_flash_json as call
    svgs = all_svgs()
    idx: dict[str, dict] = json.loads(INDEX.read_text(encoding="utf-8")) if INDEX.exists() else {}
    todo = [s for s in svgs if s not in idx]
    for i in range(0, len(todo), BATCH):
        chunk = todo[i:i + BATCH]
        raw = call("Íconos:\n" + "\n".join(chunk) + '\n\nDevolvé {"items": [{"n": nombre, "es": [...]}, ...]} con uno por ícono.',
                   system_instruction=SYSTEM, response_schema=SCHEMA, thinking_budget=0, description="icons_index")
        got = {str(x.get("n")): [str(w).strip().lower() for w in x.get("es") or [] if str(w).strip()][:4]
               for x in (raw or {}).get("items") or [] if isinstance(x, dict)}
        for s in chunk:
            idx[s] = {"path": svgs[s], "es": got.get(s, [])}
        INDEX.write_text(json.dumps(idx, ensure_ascii=False, indent=0, sort_keys=True), encoding="utf-8")
        print(f"{min(i + BATCH, len(todo))}/{len(todo)}", flush=True)
    return idx


@lru_cache(maxsize=1)
def _word_map() -> dict[str, list[str]]:
    """palabra (sin tildes) → slugs que la dibujan, en orden de relevancia (la palabra como 1ra traducción primero)."""
    if not INDEX.exists():
        return {}
    idx = json.loads(INDEX.read_text(encoding="utf-8"))
    rank: dict[str, list[tuple[int, int, str]]] = {}
    for slug, e in idx.items():
        for pos, w in enumerate(e.get("es") or []):
            for form in lemmas(w)[:1]:
                rank.setdefault(form, []).append((pos, len(slug), slug))
    return {w: [s for _, _, s in sorted(v)] for w, v in rank.items()}


def lookup(word: str) -> str | None:
    """Clave "gi:<autor>/<slug>" para la palabra, o None. Busca la palabra y sus lemas."""
    wm = _word_map()
    if not wm:
        return None
    idx = json.loads(INDEX.read_text(encoding="utf-8"))
    for form in lemmas(word):
        slugs = wm.get(form)
        if slugs:
            return "gi:" + idx[slugs[0]]["path"][:-4]
    return None


def game_icon_svg(key: str) -> str | None:
    """SVG restilizado de una clave gi: (None si no existe)."""
    rel = key[3:] + ".svg"
    p = (GI_DIR / rel).resolve()
    if not str(p).startswith(str(GI_DIR.resolve())) or not p.exists():
        return None
    svg = p.read_text(encoding="utf-8")
    view = re.search(r'viewBox="([^"]+)"', svg)
    paths = re.findall(r"<path[^>]*\sd=\"([^\"]+)\"[^>]*/?>", svg)
    paths = [d for d in paths if not re.fullmatch(r"M0 0h512v512H0z", d.strip())]   # sin el cuadrado de fondo
    if not paths:
        return None
    d = "".join(paths)
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{view.group(1) if view else "0 0 512 512"}" class="gfx-icon">'
            f'<path class="ic-fill" fill="{BONE}" fill-rule="nonzero" d="{d}"/></svg>')


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "index":
        build_index()
    else:
        print(__doc__)


# ── F4b §4: elección del ícono por Flash entre candidatos del índice (la regla mecánica elegía mal:
#    «agua» → molécula H2O, «cadáver» → pez muerto). El LLM elige un número; nunca dibuja ni escribe.
CHOICES: Path = ROOT / "gfx_profiles" / "icons" / "auto_choice.json"
CHOICE_SYSTEM = ("Elegís íconos para un documental de misterio (prisión inundada, huracán, presos). Para cada palabra te "
                 "doy íconos candidatos por su nombre en inglés. Elegí el número del que DIBUJA esa palabra tal como se usa "
                 "en la frase; 0 si ninguno la dibuja de verdad (mejor sin ícono que uno equivocado). Si elegiste 0 y "
                 "existe un objeto concreto en inglés que la dibuje, ponelo en «buscar» (una palabra). Respondés SOLO JSON.")
CHOICE_SCHEMA = {"type": "OBJECT", "properties": {"items": {"type": "ARRAY", "items": {"type": "OBJECT", "properties": {
    "palabra": {"type": "STRING"}, "n": {"type": "INTEGER"}, "buscar": {"type": "STRING"}},
    "required": ["palabra", "n"]}}}, "required": ["items"]}


def candidates(word: str, k: int = 10) -> list[str]:
    wm = _word_map()
    out: list[str] = []
    for form in lemmas(word):
        for s in wm.get(form, []):
            if s not in out:
                out.append(s)
    return out[:k]


def by_english(term: str) -> str | None:
    """Slug cuyo nombre ES exactamente el término (prison → prison). Sin coincidencias parciales: «shadow» traía una
    mano de sombra y «liquid» un jabón líquido (F4b: mejor sin ícono que uno equivocado)."""
    if not term:
        return None
    t = re.sub(r"[^a-z]", "", term.lower())
    idx = json.loads(INDEX.read_text(encoding="utf-8")) if INDEX.exists() else {}
    return t if t in idx else None


def choose_icons(items: list[tuple[str, str]], call=None) -> dict[str, str | None]:
    """{palabra: clave gi:… | None} para [(palabra, frase)]. Cache por palabra (independiente del video)."""
    cache = json.loads(CHOICES.read_text(encoding="utf-8")) if CHOICES.exists() else {}
    idx = json.loads(INDEX.read_text(encoding="utf-8")) if INDEX.exists() else {}
    todo = [(w, s) for w, s in items if w not in cache]
    if todo and idx:
        if call is None:
            sys.path.insert(0, str(ROOT))
            from gemini_helpers import call_flash_json as call
        lines = []
        cands = {w: candidates(w) for w, _ in todo}
        for w, s in todo:
            lines.append(f"[{w}] frase: «{s[:160]}»")
            lines += [f"  {n}. {c}" for n, c in enumerate(cands[w], start=1)] or ["  (sin candidatos)"]
        try:
            raw = call("\n".join(lines) + '\n\nDevolvé {"items": [{"palabra": ..., "n": número, "buscar": "..."}]}',
                       system_instruction=CHOICE_SYSTEM, response_schema=CHOICE_SCHEMA, thinking_budget=0,
                       description="auto_icons")
        except Exception:  # noqa: BLE001 — sin LLM no se agrega ningún ícono automático
            raw = {}
        got = {str(x.get("palabra")): x for x in (raw or {}).get("items") or [] if isinstance(x, dict)}
        for w, _ in todo:
            x = got.get(w) or {}
            n = x.get("n") if isinstance(x.get("n"), int) else 0
            slug = cands[w][n - 1] if 1 <= n <= len(cands[w]) else by_english(str(x.get("buscar") or ""))
            cache[w] = slug
        CHOICES.write_text(json.dumps(cache, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")
    return {w: ("gi:" + idx[cache[w]]["path"][:-4] if cache.get(w) in idx else None) for w, _ in items}
