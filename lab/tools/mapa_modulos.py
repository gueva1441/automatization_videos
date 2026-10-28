"""
lab/tools/mapa_modulos.py — F42 §C (antes F33 §D, solo gfx): arma `lab/MAPA_PROYECTO.md` y `lab/MAPA_PROYECTO.json`.

Los hechos (quién importa o lanza a quién, la secuencia del form, el alcance por etapa, commits, md5) salen del código
con `mapa_hechos.py`; los stickers (qué hace para el video, recibe/entrega, modelo, etapa y estado verificados, funciones
muertas confirmadas) los escribe quien leyó cada archivo entero, en `lab/mapa/stickers/<zona>.json`, con el md5 del
archivo que leyó. Si el archivo cambia, el sticker queda viejo y `--check` lo dice.

    python lab/tools/mapa_modulos.py            → lab/MAPA_PROYECTO.md + .json
    python lab/tools/mapa_modulos.py --check    → exit 1 si un archivo de producción no tiene sticker o lo tiene viejo
    python lab/tools/mapa_modulos.py --zonas    → la zona de cada archivo de producción (JSON)
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import mapa_hechos as mh  # noqa: E402

MAPA = ROOT / "lab" / "mapa"
STICKERS = MAPA / "stickers"
SALIDA_MD = ROOT / "lab" / "MAPA_PROYECTO.md"
SALIDA_JSON = ROOT / "lab" / "MAPA_PROYECTO.json"

# Zonas del handoff F42 §B, por patrón sobre el nombre del archivo (sin extensión); lo que no cae en ninguna va a la 5.
ZONAS: list[tuple[str, list[str]]] = [
    ("research", ["niche_discoverer", "nicho_config", "topic_researcher", "topic_validator", "topics_db", "subtopic_*",
                  "youtube_scanner", "transcript_fetch", "m_judge_seeds", "evidence*", "learned_patterns", "fase1",
                  "researcher_steps/*", "purge_history", "migrate_*"]),
    ("guion", ["fase1_5", "m01a_*", "m01b_*", "m01c_*", "m01d_*", "m01e_*", "guion_v3_reglas", "guion_v4", "nombres",
               "num_es", "name_matching", "tts_tags", "video_length"]),
    ("fase2a", ["fase2a", "m02_5_*", "tts_normalizer", "audio_*", "music_*", "m07_*", "m03_*", "foto_madre",
                "image_grade", "vision_validator", "zoom_judge", "parallax_*", "depth_probe", "art_*", "engine_profiles",
                "flow_*", "anchor_timing", "m05_*", "m06_*", "voz_*", "subs_remap", "patch_sync_map_mixing",
                "promote_palette_*"]),
    ("fase2b_gfx", ["fase2b", "gfx_*", "gfx_profiles/*", "script_engine/gfx_templates/*", "pantalla_*", "clima",
                    "aprobacion", "freeze_check", "transition_*", "gfx_lab_server", "mixer_server"]),
    ("orquestador", ["*"]),
]
ESTADOS = ("vivo", "solo herramienta manual", "huérfano", "roto")


def zona(archivo: str) -> str:
    p = Path(archivo)
    tallo = p.name.split(".")[0]
    for z, pats in ZONAS:
        for pat in pats:
            if "/" in pat:
                if fnmatch.fnmatch(archivo, pat):
                    return z
            elif not archivo.startswith(".claude/") and fnmatch.fnmatch(tallo, pat):
                return z
    return ZONAS[-1][0]


def produccion() -> dict[str, str]:
    """{archivo de producción: md5} — rápido (sin git ni AST): lo usa --check y el hook."""
    pys = mh.py_produccion()
    return {mh.rel(p): mh.md5(p) for p in pys + mh.no_py_produccion(pys)}


def stickers(carpeta: Path = STICKERS) -> tuple[dict[str, dict], list[str]]:
    out: dict[str, dict] = {}
    dup: list[str] = []
    for f in sorted(x for x in carpeta.glob("*.json") if not x.name.startswith("_")):
        for k, v in json.loads(f.read_text(encoding="utf-8")).items():
            if k.startswith("_"):
                continue
            if k in out:
                dup.append(f"{k} ({f.name} y {out[k]['_zona_archivo']})")
            out[k] = {**v, "_zona_archivo": f.name}
    return out, dup


def check(carpeta: Path = STICKERS) -> list[str]:
    prod = produccion()
    st, dup = stickers(carpeta)
    fallas = [f"sticker repetido: {d}" for d in dup]
    for k, m in sorted(prod.items()):
        if k not in st:
            fallas.append(f"sin sticker: {k} (zona {zona(k)})")
        elif st[k].get("md5") != m:
            fallas.append(f"sticker viejo: {k} (md5 del sticker {str(st[k].get('md5'))[:8]}… ≠ archivo {m[:8]}…; "
                          f"releer el archivo y reescribir su sticker en {st[k]['_zona_archivo']})")
        elif st[k].get("estado") not in ESTADOS:
            fallas.append(f"estado inválido: {k} → {st[k].get('estado')!r}")
    fallas += [f"sticker sin archivo de producción: {k}" for k in sorted(set(st) - set(prod))]
    return fallas


# ─────────────────────────── armado ───────────────────────────
def _corto(k: str) -> str:
    return Path(k).name.removesuffix(".py")


def _git(e: dict | None) -> str:
    if not e:
        return "(fuera de git)"
    return f"{e['commit']} {e['fecha']}" + (f" ({e['tanda']})" if e.get("tanda") else "")


# El `modelo` del sticker es texto libre (lo que dice el código); para las cajas del flujograma se lleva a la familia que
# paga. No pagan: lo que solo fija nombres (config), lo local y lo apagado.
FAMILIAS: list[tuple[str, str]] = [
    (r"claude-fable", "Claude Fable"), (r"claude-sonnet", "Claude Sonnet"), (r"claude-opus", "Claude Opus"),
    (r"gpt-image", "GPT Image (fal)"), (r"gpt-6", "GPT-6"), (r"gemini-4-argon", "Gemini 4 Argon"),
    (r"gemini_model_research|gemini-2\.5-pro|call_pro_json|Gemini Pro", "Gemini Pro"),
    (r"gemini_model\b|gemini-2\.5-flash|call_flash_json|Gemini Flash|VISION_MODEL|Gemini \(config", "Gemini Flash"),
    (r"ElevenLabs Music|music_v1", "ElevenLabs Music"), (r"[Ff]orced[- ][Aa]lignment", "ElevenLabs alineador"),
    (r"ElevenLabs|eleven_v|elevenlabs_model", "ElevenLabs TTS"), (r"[Ss]eedream", "Seedream (fal)"),
    (r"[Kk]ling", "Kling (fal)"), (r"[Vv]eo|fal_video_model", "Veo (fal)"), (r"[Ff]lux", "Flux (fal)"),
]
NO_PAGA = re.compile(r"solo los fija|sin costo de API|apagado|local en|el que pase quien llama|lista MODELOS|"
                     r"si se pasa --modelo|por --modelo")


def familias(texto: str) -> list[str]:
    if NO_PAGA.search(texto):
        return []
    return [nombre for pat, nombre in FAMILIAS if re.search(pat, texto)]


def _modelos(s: dict) -> list[str]:
    out: list[str] = []
    for m in s.get("modelo") or []:
        if isinstance(m, dict) and m.get("modelo"):
            out += [f for f in familias(f"{m['modelo']} {m.get('para', '')}") if f not in out]
    return out


def _celda(x) -> str:
    if isinstance(x, list):
        x = "; ".join(str(i) for i in x)
    return str(x or "—").replace("|", "\\|").replace("\n", " ")


def flujograma(seq: dict, filas: dict[str, dict]) -> tuple[list[str], list[dict]]:
    """Mermaid de la cadena del form desde la secuencia de A: una caja por etapa (rombo si es compuerta), con su script,
    sus módulos propios (los que solo esa etapa usa, según el sticker) y el modelo que paga."""
    L = ["```mermaid", "flowchart TD"]
    cajas = []
    previo = None
    scripts = {c["script"] for e in seq["etapas"] for c in e["comandos"]}     # orquestan: su sticker lista lo de abajo
    for e in seq["etapas"]:
        if not e["comandos"] and not e["compuertas"]:
            continue
        nid = e["etapa"].upper()
        script = e["comandos"][0]["script"] if e["comandos"] else ""
        propios = sorted(_corto(k) for k, f in filas.items() if f["etapas_sticker"] == [e["etapa"]])
        es_compuerta = bool(e["compuertas"]) and all(any(a.startswith("--aprobar") for a in c["argv"])
                                                      for c in e["comandos"])
        modelos = [] if es_compuerta else sorted({m for k, f in filas.items()
                                                  if e["etapa"] in f["etapas_sticker"] and k not in scripts
                                                  for m in f["modelos"]})
        cajas.append({"etapa": e["etapa"], "orden": e["orden"], "encabezado": e["encabezado"], "funcion": e["funcion"],
                      "comandos": [" ".join(["python", *c["argv"]]) for c in e["comandos"]],
                      "compuertas": [c["menu"] for c in e["compuertas"]], "sin_form": e.get("sin_form", ""),
                      "propios": propios, "modelos": modelos, "es_compuerta": es_compuerta})
        lineas_mod = [", ".join(propios[i:i + 4]) for i in range(0, len(propios), 4)]
        txt = "<br/>".join([f"<b>{e['encabezado'] or e['etapa']}</b>", f"<i>{script}</i>"]
                           + ([f"módulos propios: {lineas_mod[0]}"] + lineas_mod[1:] if propios else [])
                           + ([f"modelo: {', '.join(modelos)}"] if modelos else []))
        txt = txt.replace('"', "'")
        for c in e["compuertas"]:
            if es_compuerta:
                continue
            gid = f"G_{c['menu']}"
            L.append(f'  {gid}{{"compuerta del form: {c["menu"]}"}}')
            if previo:
                L.append(f"  {previo} --> {gid}")
            previo = gid
        L.append(f'  {nid}{{"{txt}"}}' if es_compuerta else f'  {nid}["{txt}"]')
        if previo:
            L.append(f"  {previo} --> {nid}")
        previo = nid
    L.append("```")
    return L, cajas


def armar() -> tuple[dict, list[str]]:
    H = mh.hechos()
    st, dup = stickers()
    tc_path = MAPA / "tests_collect.json"
    tc = json.loads(tc_path.read_text(encoding="utf-8")) if tc_path.exists() else {"archivos": {}, "resumen": "(sin colecta)"}
    tl_path = MAPA / "tests_lab.json"
    tl = json.loads(tl_path.read_text(encoding="utf-8")) if tl_path.exists() else {}
    filas: dict[str, dict] = {}
    for k, h in H["modulos"].items():
        s = st.get(k, {})
        quien = sorted(set(h.get("lo_importan", {})) | set(h.get("lo_lanzan", {})) | set(h.get("lo_referencian", [])))
        filas[k] = {"archivo": k, "zona": zona(k), "sticker": s.get("sticker", "(sin sticker)"),
                    "recibe": s.get("recibe", ""), "entrega": s.get("entrega", ""), "modelo": s.get("modelo", []),
                    "modelos": _modelos(s), "etapas_a": h.get("etapas", []), "etapas_sticker": s.get("etapa", []),
                    "compartido": h.get("compartido", False), "lo_llaman": quien, "tests": len(h.get("tests", [])),
                    "nacio": _git(h.get("nacio")), "ultimo": _git(h.get("ultimo")), "estado_a": h.get("estado_a", ""),
                    "estado": s.get("estado", "(sin sticker)"), "estado_prueba": s.get("estado_prueba", ""),
                    "funciones_muertas": s.get("funciones_muertas", []), "imports_rotos": h.get("imports_rotos", []),
                    "sin_llamador_a": [f["nombre"] for f in h.get("funciones", []) if f.get("sin_llamador")],
                    "md5": h.get("md5"), "sticker_al_dia": s.get("md5") == h.get("md5")}
    L_flujo, cajas = flujograma(H["secuencia"], filas)
    conteo = {e: sum(1 for f in filas.values() if f["estado"] == e) for e in ESTADOS}
    conteo["(sin sticker)"] = sum(1 for f in filas.values() if f["estado"] == "(sin sticker)")
    tests = []
    for t, v in sorted(tc.get("archivos", {}).items()):
        imp = H["tests"].get(t, {})
        tests.append({"test": t, "importa": [_corto(x) for x in imp.get("importa", [])],
                      "colecta": v.get("colecta", 0), "error": v.get("error", ""),
                      "imports_rotos": [r["falta"] for r in imp.get("imports_rotos", [])],
                      "clase": (tl.get(t) or {}).get("clase", "")})
    data = {"generado_por": "lab/tools/mapa_modulos.py (F42 §C)", "secuencia": H["secuencia"], "cajas": cajas,
            "form": H["form"], "orquestador": H["orquestador"], "entradas": H["entradas"], "conteo": conteo,
            "modulos": filas, "tests": tests, "tests_resumen": tc.get("resumen", ""), "stickers_repetidos": dup}
    return data, L_flujo


def escribir(data: dict, L_flujo: list[str]) -> None:
    F = data["modulos"]
    L = ["# MAPA DEL PROYECTO — de la semilla al video", "",
         "Generado por `lab/tools/mapa_modulos.py` (F42). Los hechos (imports, `subprocess`, la secuencia del form, el "
         "alcance por etapa, commits, md5) salen del código con `lab/tools/mapa_hechos.py`; sticker, recibe/entrega, "
         "modelo, etapa y estado los escribió quien leyó cada archivo entero (`lab/mapa/stickers/<zona>.json`, con el md5 "
         "del archivo leído). `python lab/tools/mapa_modulos.py --check` falla si un archivo de producción no tiene "
         "sticker o lo tiene viejo. Datos para máquinas: `lab/MAPA_PROYECTO.json`.", "",
         "## La cadena como la corre el form", "",
         f"El form (`{', '.join(data['form'])}`) lanza `{data['orquestador']}`; `sequence()` corre las etapas de "
         "`ETAPAS` en orden desde la primera que falta (`etapa_de`). Cajas leídas de `run_pipeline.py` por AST; los "
         "rombos son compuertas del form (sin el form, la etapa para y reporta el comando).", ""]
    L += L_flujo
    L += ["", "### Las etapas", "", "| # | etapa | función | comando | compuerta | módulos propios | modelo |",
          "|---|---|---|---|---|---|---|"]
    for c in data["cajas"]:
        L.append(f"| {c['orden']} | {c['encabezado'] or c['etapa']} | `{c['funcion']}` | "
                 f"{'<br>'.join('`' + x + '`' for x in c['comandos']) or '—'} | {', '.join(c['compuertas']) or '—'} | "
                 f"{', '.join(c['propios']) or '—'} | {', '.join(c['modelos']) or '—'} |")
    L += ["", "### Conteo por estado", "", "| estado | archivos |", "|---|---|"]
    L += [f"| {k} | {v} |" for k, v in data["conteo"].items()]
    L += ["", "## Todos los módulos, por zona", ""]
    for z, _ in ZONAS:
        filas = sorted((f for f in F.values() if f["zona"] == z), key=lambda f: f["archivo"])
        L += [f"### Zona {z} ({len(filas)})", "",
              "| módulo | sticker | recibe | entrega | modelo | etapa(s) | quién lo llama | nació / último cambio | estado |",
              "|---|---|---|---|---|---|---|---|---|"]
        for f in filas:
            mod = "; ".join(f"{m.get('modelo')}: {m.get('para', '')}" for m in f["modelo"] if isinstance(m, dict)) \
                if f["modelo"] else "—"
            quien = ", ".join(_corto(q) for q in f["lo_llaman"][:12]) + (" …" if len(f["lo_llaman"]) > 12 else "")
            quien = (quien or "—") + (f" (+ {f['tests']} tests)" if f["tests"] else "")
            L.append(f"| `{f['archivo']}` | {_celda(f['sticker'])} | {_celda(f['recibe'])} | {_celda(f['entrega'])} | "
                     f"{_celda(mod)} | {_celda(f['etapas_sticker'])} | {quien} | {f['nacio']} / {f['ultimo']} | "
                     f"{f['estado']}{'' if f['sticker_al_dia'] else ' ⚠ sticker viejo'} |")
        L.append("")
    L +=["## Compartidos (los alcanzan dos o más scripts de etapa)", "", "| módulo | etapas (sticker) | etapas por import (A) |",
          "|---|---|---|"]
    L += [f"| `{f['archivo']}` | {_celda(f['etapas_sticker'])} | {_celda(f['etapas_a'])} |"
          for f in sorted(F.values(), key=lambda f: f["archivo"]) if f["compartido"]]
    for est, tit in (("solo herramienta manual", "Solo herramienta manual"), ("huérfano", "Huérfanos"), ("roto", "Rotos")):
        sel = sorted((f for f in F.values() if f["estado"] == est), key=lambda f: f["archivo"])
        L += ["", f"## {tit} ({len(sel)})", "", "| módulo | prueba | sticker |", "|---|---|---|"]
        L += [f"| `{f['archivo']}` | {_celda(f['estado_prueba'])} | {_celda(f['sticker'])} |" for f in sel]
    muertas = [(f["archivo"], m) for f in sorted(F.values(), key=lambda f: f["archivo"]) for m in f["funciones_muertas"]]
    L += ["", f"## Funciones muertas confirmadas leyendo ({len(muertas)})", "",
          "Candidatas de A = funciones sin ninguna referencia por nombre en producción (ni como string); el worker de la "
          "zona confirmó leyendo y descartó las que se llaman por string, `getattr`, decoradores o el framework.", "",
          "| módulo | función | línea | por qué |", "|---|---|---|---|"]
    for a, m in muertas:
        m = m if isinstance(m, dict) else {"nombre": m}
        L.append(f"| `{a}` | `{m.get('nombre')}` | {m.get('linea', '')} | {_celda(m.get('por_que', ''))} |")
    L += ["", f"## Tests (A.4) — `pytest --collect-only` (no se corren): {data['tests_resumen']}", "",
          "| test | módulos de producción que importa | colecta | error de import | clase (zona 6) |",
          "|---|---|---|---|---|"]
    for t in data["tests"]:
        L.append(f"| `{t['test']}` | {_celda(', '.join(t['importa']))} | {t['colecta']} | "
                 f"{_celda(t['error'] or '; '.join(t['imports_rotos']))} | {t['clase'] or '—'} |")
    SALIDA_MD.write_text("\n".join(L) + "\n", encoding="utf-8")
    SALIDA_JSON.write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")


def main() -> int:
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--zonas", action="store_true")
    ap.add_argument("--stickers", type=Path, default=STICKERS, help="carpeta de stickers (para probar --check)")
    a = ap.parse_args()
    if a.zonas:
        print(json.dumps({k: zona(k) for k in sorted(produccion())}, ensure_ascii=False, indent=1))
        return 0
    if a.check:
        fallas = check(a.stickers)
        for f in fallas:
            print(f"✗ {f}")
        n = len(produccion())
        print(f"mapa --check: {n} archivos de producción · {len(fallas)} fallas")
        return 1 if fallas else 0
    data, L_flujo = armar()
    escribir(data, L_flujo)
    print(f"{len(data['modulos'])} archivos · {len(data['cajas'])} cajas · conteo {data['conteo']} → "
          f"{SALIDA_MD.relative_to(ROOT).as_posix()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
