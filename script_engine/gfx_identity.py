"""
gfx_identity.py — Identidad del canal que sale del laboratorio (F3 §C; HANDOFF_F3 §1.1 paso 6 y §4).

"Guardar identidad" escribe tres cosas a partir del estado del lab:
    gfx_profiles/<perfil>.json             tokens + fuentes + inventario (enabled) + pesos del léxico + `identity`
                                           (marcas ✔/✖, variantes anotadas, sugerencias, lo que falta)
    gfx_profiles/<perfil>_golden_<cap>.json  el plan del cap tal como lo dejó Omar (ya con candado) = ejemplo dorado
    lab/identidad/IDENTIDAD_<perfil>.md    resumen humano para el analista (§4)

El perfil NUEVO se valida con gfx_config.load_profile ANTES de reemplazar el actual (un perfil inválido nunca
llega a disco con su nombre real) y el anterior queda en <perfil>.json.bak_f3_<fecha> (ignorado por git).

Estado del lab (dict):
    plan, tokens, anotado {elem: {attr: v}}, marks {elem: {v: "si"|"no", regla, por_que}},
    sugerencias {Sxx: "probando"|"si"|"no"}, lexicon {palabra: 0–3}, faltan (texto), touched [elem]
"""
from __future__ import annotations

import copy
import json
import os
import time
from pathlib import Path
from typing import Any

# token del lab → clave de `fonts` del perfil (rules_from_profile aplica fonts DESPUÉS de tokens)
FONT_TOKENS: dict[str, str] = {"callout_font": "callout", "figure_font": "callout_figure",
                               "title_font": "title", "clipping_font": "clipping"}
# pieza del catálogo → bloque del motor (inventario `blocks` del perfil)
ENGINE_BLOCK: dict[str, str] = {
    "title_card": "title_card", "data_callout": "data_callout", "archive_clipping": "archive_clipping",
    "count_up": "count_up", "punch_in": "punch_in", "chapter_question": "chapter_question",
    "keyword_emphasis": "keyword_emphasis", "icon_callout": "icon_callout", "icon_array": "icon_array",
    "source_tag": "source_tag",
}
# ✖ en piezas que no son bloques: token que las apaga
NEVER_TOKENS: dict[str, dict[str, Any]] = {
    "keyword_stamp": {"emphasis_stamp": False},
    "vignette": {"vignette_opacity": 0.0},
    "grain": {"grain_opacity": 0.0},
    "flash": {"flash_max_per_cap": 0},
}
CUE_TO_ELEM: dict[str, str] = {
    "shot_transition:dissolve": "crossfade", "shot_transition:dip": "dip_to_black", "shot_transition:flash": "flash",
    "shot_transition:cut_punch": "cut", "shot_transition:cut": "cut", "evidence_zoom": "punch_in",
}


def elem_of(block: str) -> str:
    return CUE_TO_ELEM.get(block) or block.split(":")[0]


def _fmt(t: float) -> str:
    return f"{int(t // 60):02d}:{t % 60:04.1f}"


def _label(attr: dict[str, Any], v: Any) -> str:
    for o in attr.get("opciones") or []:
        if json.dumps(o["v"], sort_keys=True) == json.dumps(v, sort_keys=True):
            return str(o["label"])
    return str(v)


def chosen_variant(el: dict[str, Any], state: dict[str, Any], rules: dict[str, Any]) -> list[str]:
    """'Atributo: valor' de cada atributo del elemento con el valor que quedó (lab > perfil > default)."""
    out = []
    for a in el.get("atributos") or []:
        kind, _, path = a["aplica"].partition(":")
        if kind == "token":
            v = state.get("tokens", {}).get(path, rules.get(path, a.get("default")))
        elif kind == "anotado":
            v = (state.get("anotado", {}).get(el["id"]) or {}).get(a["id"], a.get("default"))
        else:
            continue                                     # elem/all: van por pieza en el plan dorado
        if a["tipo"] == "texto":
            continue
        out.append(f"{a['nombre']}: {_label(a, v)}" + (" (anotado)" if kind == "anotado" else ""))
    return out


def count_in_plan(elem_id: str, cues: list[dict[str, Any]]) -> int:
    return sum(1 for c in cues if elem_of(c["block"]) == elem_id)


def open_questions(state: dict[str, Any], catalog: dict[str, Any], cues: list[dict[str, Any]]) -> list[str]:
    """§4.5: lo que el lab detecta solo."""
    marks = state.get("marks") or {}
    by_id = {e["id"]: e for e in catalog["elementos"]}
    qs: list[str] = []
    for eid in state.get("touched") or []:
        if eid in by_id and eid not in marks:
            qs.append(f"Probaste **{by_id[eid]['nombre']}** y no marcaste ✔ ni ✖.")
    for sid, st in sorted((state.get("sugerencias") or {}).items()):
        if st == "probando":
            qs.append(f"La sugerencia {sid} quedó en 'probando' (ni aceptada ni rechazada).")
    sfx = (state.get("anotado") or {}).get("keyword_emphasis", {}).get("sfx")
    moods = [c for c in cues if c["block"].startswith(("keyword_emphasis", "icon_callout"))]
    if moods and sfx in (None, "nada"):
        qs.append(f"Hay {len(moods)} mood(s) en el plan y el SFX de mood está en "
                  f"'{sfx or 'sin elegir'}': ¿van sin sonido?")
    for eid, m in marks.items():
        el = by_id.get(eid)
        if m.get("v") == "si" and el and el.get("estado") == "nuevo_D":
            qs.append(f"**{el['nombre']}** está ✔ pero todavía no se dibuja: es pieza nueva, se ve en el mp4 recién en §D.")
        elif m.get("v") == "si" and el and el.get("estado") == "futuro":
            qs.append(f"**{el['nombre']}** marcado 'lo quiero': no se construye en F3; queda para después del lab.")
    rec = state.get("recorrido") or []
    pend = [(f["foto"], o["nombre"]) for f in rec for o in f.get("objetos") or [] if o.get("estado") == "pendiente"]
    if pend:
        fotos = sorted({n for n, _ in pend})
        qs.append(f"Quedan {len(pend)} objeto(s) pendientes (sin ☑ ni ✖) en los tramos {', '.join(map(str, fotos))}.")
    sin_ver = [f["foto"] for f in rec if not f.get("vista")]
    if rec and sin_ver:
        qs.append(f"Tramos que no abriste: {', '.join(map(str, sin_ver))}.")
    for eid, m in marks.items():
        if m.get("v") == "no" and count_in_plan(eid, cues):
            el = by_id.get(eid, {"nombre": eid})
            qs.append(f"**{el['nombre']}** está ✖ pero sigue {count_in_plan(eid, cues)} vez/veces en el plan de ch02.")
    return qs


def summary_md(state: dict[str, Any], catalog: dict[str, Any], cues: list[dict[str, Any]],
               words: list[dict[str, Any]], rules: dict[str, Any], *, profile: str, cap: str, video_id: str,
               sugerencias: list[dict[str, Any]] | None = None) -> str:
    """IDENTIDAD_<perfil>.md (§4). Se regenera entero en cada cambio."""
    by_id = {e["id"]: e for e in catalog["elementos"]}
    marks = state.get("marks") or {}
    lines = [f"# IDENTIDAD — {profile}", "",
             f"Generado por el lab de identidad · {time.strftime('%Y-%m-%d %H:%M')} · {cap} de `{video_id}`.", ""]

    lines += ["## 1. Lo que se queda", "",
              "| Elemento | Variante elegida | Veces en " + cap + " | Dónde (regla) |", "|---|---|---|---|"]
    keep = [(eid, m) for eid, m in marks.items() if m.get("v") == "si" and eid in by_id]
    for eid, m in sorted(keep, key=lambda x: by_id[x[0]]["nombre"]):
        el = by_id[eid]
        var = "; ".join(chosen_variant(el, state, rules)) or "—"
        regla = (m.get("regla") or "").strip() or f"(hint) {el['hint']['cuando']}"
        lines.append(f"| {el['nombre']} (`{eid}`) | {var} | {count_in_plan(eid, cues)} | {regla} |")
    if not keep:
        lines.append("| — | — | — | — |")

    lines += ["", "## 2. Lo que nunca", ""]
    never = [(eid, m) for eid, m in marks.items() if m.get("v") == "no" and eid in by_id]
    lines += [f"- **{by_id[eid]['nombre']}** (`{eid}`)" + (f": {m['por_que'].strip()}" if (m.get("por_que") or "").strip() else "")
              for eid, m in sorted(never, key=lambda x: by_id[x[0]]["nombre"])] or ["- —"]
    rej = [s for s in (sugerencias or []) if (state.get("sugerencias") or {}).get(s["id"]) == "no"]
    if rej:
        lines += ["", "Sugerencias rechazadas:"] + [f"- {s['id']} · {s['titulo']}" for s in rej]

    lines += ["", "## 3. Lo que falta", ""]
    faltan = (state.get("faltan") or "").strip()
    quiero = [by_id[eid]["nombre"] for eid, m in marks.items() if m.get("v") == "si" and by_id.get(eid, {}).get("estado") == "futuro"]
    lines += ([f"> {ln}" for ln in faltan.splitlines()] if faltan else ["- (Omar no escribió nada en «quisiera que…»)"])
    if quiero:
        lines += [f"- Quiere (futuro): {', '.join(quiero)}"]

    lines += ["", f"## 4. Plan dorado de {cap}", "", "| t | Palabra | Elemento | Variante |", "|---|---|---|---|"]
    ws = sorted(words, key=lambda w: w["start"])
    for c in cues:
        if c["block"].startswith("shot_transition"):
            continue
        w = next((x for x in reversed(ws) if x["start"] <= c["t"] + 0.05), ws[0] if ws else {"word": ""})
        el = by_id.get(elem_of(c["block"]))
        lines.append(f"| {_fmt(c['t'])} | {w['word']} | {el['nombre'] if el else c['block']} | {c.get('text') or '—'} |")
    trans: dict[str, int] = {}
    for c in cues:
        if c["block"].startswith("shot_transition"):
            k = by_id.get(elem_of(c["block"]), {}).get("nombre", c["block"])
            trans[k] = trans.get(k, 0) + 1
    if trans:
        lines += ["", "Cambios de foto: " + ", ".join(f"{k} × {v}" for k, v in sorted(trans.items()))]
    lex = {k: v for k, v in (state.get("lexicon") or {}).items()}
    if lex:
        lines += ["", "Léxico ajustado: " + ", ".join(f"«{k}» → {'apagada' if v == 0 else f'peso {v}'}" for k, v in sorted(lex.items()))]
    tok = state.get("tokens") or {}
    if tok:
        lines += ["", "Tokens cambiados en el lab: " + ", ".join(f"`{k}` = {json.dumps(v, ensure_ascii=False)}" for k, v in sorted(tok.items()))]

    lines += ["", "## 5. Preguntas abiertas", ""]
    lines += [f"- {q}" for q in open_questions(state, catalog, cues)] or ["- Ninguna."]

    rec = state.get("recorrido") or []                 # §F: lo arma la pantalla tramo por tramo
    if rec:
        icon = {"si": "✔", "no": "✖", "pendiente": "…"}
        lines += ["", "## 6. Recorrido tramo por tramo", "",
                  "✔ se queda · … pendiente (sin marcar) · ✖ nunca", ""]
        for f in rec:
            vista = "" if f.get("vista") else " · (no la abriste)"
            lines.append(f"**Tramo {f['foto']}** ({f['desde']}–{f['hasta']}){vista}")
            for o in f.get("objetos") or []:
                forma = f" — {o['forma']}" if o.get("forma") else ""
                lines.append(f"- {icon.get(o['estado'], '…')} {o['nombre']} ({o['t']}){forma}")
            lines.append("")
    return "\n".join(lines).rstrip("\n") + "\n"


def apply_identity(prof: dict[str, Any], state: dict[str, Any], *, golden_name: str) -> dict[str, Any]:
    """Perfil nuevo = perfil actual + tokens/fuentes del lab + enabled por ✔/✖ + léxico + `identity`."""
    new = copy.deepcopy(prof)
    tokens = dict(state.get("tokens") or {})
    for k, v in tokens.items():
        if k in FONT_TOKENS:
            new.setdefault("fonts", {})[FONT_TOKENS[k]] = v
        else:
            new.setdefault("tokens", {})[k] = v
    marks = state.get("marks") or {}
    for eid, m in marks.items():
        blk = ENGINE_BLOCK.get(eid)
        if blk and m.get("v") in ("si", "no"):
            new.setdefault("blocks", {}).setdefault(blk, {})["enabled"] = m["v"] == "si"
        if m.get("v") == "no":
            for k, v in NEVER_TOKENS.get(eid, {}).items():
                new.setdefault("tokens", {})[k] = v
    for word, weight in (state.get("lexicon") or {}).items():
        for m in (new.get("moods") or {}).values():
            trig = m.get("triggers") or {}
            if word in trig:
                if int(weight) == 0:
                    trig.pop(word)
                    (m.get("icon_words") or {}).pop(word, None)
                else:
                    trig[word] = int(weight)
    new["identity"] = {
        "version": 1, "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"), "golden_plan": golden_name,
        "marks": marks, "anotado": state.get("anotado") or {}, "sugerencias": state.get("sugerencias") or {},
        "faltan": state.get("faltan") or "", "lab_tokens": tokens,
    }
    return new


def save_identity(state: dict[str, Any], *, profile: str, cap: str, video_id: str, locked_plan: dict[str, Any],
                  rejected: list[dict[str, Any]], summary: str, md_dir: Path) -> dict[str, str]:
    """Escribe perfil (validado) + plan dorado + resumen. Devuelve {qué: ruta}."""
    import gfx_config
    prof_path = gfx_config.profile_path(profile)
    prof = json.loads(prof_path.read_text(encoding="utf-8"))
    golden = gfx_config.GFX_PROFILES_DIR / f"{profile}_golden_{cap}.json"
    new = apply_identity(prof, state, golden_name=golden.name)
    # validar con el mismo loader del pipeline ANTES de reemplazar
    tmp_name = f"_lab_tmp_{profile}"
    tmp = gfx_config.profile_path(tmp_name)
    tmp.write_text(json.dumps(new, ensure_ascii=False, indent=1), encoding="utf-8")
    try:
        gfx_config.load_profile(tmp_name)
    except Exception:
        tmp.unlink(missing_ok=True)
        raise
    bak = prof_path.with_name(prof_path.name + f".bak_f3_{time.strftime('%Y%m%d_%H%M%S')}")
    n = 1
    while bak.exists():                                  # dos guardados en el mismo segundo: no pisar el respaldo
        bak = prof_path.with_name(prof_path.name + f".bak_f3_{time.strftime('%Y%m%d_%H%M%S')}_{n}")
        n += 1
    bak.write_text(prof_path.read_text(encoding="utf-8"), encoding="utf-8")
    os.replace(tmp, prof_path)
    golden.write_text(json.dumps({
        "profile": profile, "video_id": video_id, "cap": cap, "saved_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "plan": locked_plan, "rejected_by_lock": rejected, "tokens": state.get("tokens") or {},
        "anotado": state.get("anotado") or {}, "marks": state.get("marks") or {},
    }, ensure_ascii=False, indent=1), encoding="utf-8")
    md_dir.mkdir(parents=True, exist_ok=True)
    md = md_dir / f"IDENTIDAD_{profile}.md"
    md.write_text(summary, encoding="utf-8")
    return {"perfil": str(prof_path), "respaldo": str(bak), "golden": str(golden), "resumen": str(md)}
