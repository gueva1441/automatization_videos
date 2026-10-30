# -*- coding: utf-8 -*-
"""F59 Etapa B — prueba real en Wittenoom sobre la copia de lab (`lab/hyperframes/f59/base/`), dentro de
`cost_tracker.start_video('f59_parte_b')`. Llama `_fix_core` / `_clipfix_core` DIRECTO con
`QAState(tid, base_dir=BASE)` (no `_start_fix`: usa los globales). Las deps inyectables se usan solo para
MIRAR (wrappers que anotan y delegan en la función real de producción): qué devolvió Opus, el SSIM de la foto
final, el motor, los rechazos y los segundos del clip.

B1  Composición (una variable): los 3 paquetes de F58 con sus casilleros (`raw_llm_prompt` de publish/metadata.json),
    su `anio`, `sin_cartel=True`, `escala=False` y la oración nueva (`m09.COMPOSICION_MINIATURA`), sin LLM.
    Antes se comprueba que con la oración VIEJA el prompt sale byte-idéntico al de F58 (misma máquina, US$ 0).
B2  Foto: ch03_img_08 — foto «antes» desde los casilleros de 03_visual (mismo `prompt`, misma semilla por sujeto,
    grade de producción); después `_fix_core` con el pedido del analista.
B3  Clip: `_clipfix_core` sobre ch01 con el pedido del analista.

Salida: parte_b.json (todo), SALIDA_B.md (texto), b1/ b2/ b3/ (imágenes y mp4, no van a git), hoja_paquetes_f59.jpg,
hoja_paquetes_f58_vs_f59.jpg, b2/hoja_b2.jpg.
Uso: PYTHONIOENCODING=utf-8 python lab/hyperframes/f59/parte_b.py
"""
import difflib
import json
import re
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
F59 = Path(__file__).resolve().parent
BASE = F59 / "base"
TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
PEDIDO_B2 = "que mire hacia la cámara, con el ceño fruncido"
PEDIDO_B3 = "cámara quieta, solo sube el polvo, lento"
IMG_B2 = "ch03_img_08.png"
# La oración de F58 (m09_packaging antes de 10f08c0), solo para la comprobación de byte-identidad (sin gasto).
COMPOSICION_F58 = ("The person fills the right half of the frame, face and torso large; "
                   "the left half is dark, uncluttered negative space.")


def _run(cmd: list[str]) -> str:
    return subprocess.run(cmd, check=True, capture_output=True, text=True).stdout.strip()


def _md5(p: Path) -> str:
    import hashlib
    return hashlib.md5(p.read_bytes()).hexdigest()


def _dur(mp4: Path) -> float | None:
    try:
        return round(float(_run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0",
                                 str(mp4)])), 3)
    except Exception:  # noqa: BLE001
        return None


def _hstack(fotos: list[Path], out: Path, w: int = 640) -> None:
    ins = [a for f in fotos for a in ("-i", str(f))]
    fil = "".join(f"[{i}:v]scale={w}:-2[v{i}];" for i in range(len(fotos))) + \
          "".join(f"[v{i}]" for i in range(len(fotos))) + f"hstack=inputs={len(fotos)}"
    if len(fotos) == 1:
        fil = f"[0:v]scale={w}:-2"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", fil, "-frames:v", "1", str(out)],
                   check=True)


def _vstack(fotos: list[Path], out: Path, w: int = 1920) -> None:
    ins = [a for f in fotos for a in ("-i", str(f))]
    fil = "".join(f"[{i}:v]scale={w}:-2[v{i}];" for i in range(len(fotos))) + \
          "".join(f"[v{i}]" for i in range(len(fotos))) + f"vstack=inputs={len(fotos)}"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", *ins, "-filter_complex", fil, "-frames:v", "1", str(out)],
                   check=True)


def _tira(mp4: Path, out: Path, n: int = 5) -> None:
    """n cuadros repartidos en el clip, lado a lado (ver-render)."""
    d = _dur(mp4) or 8.0
    fil = f"fps={n / d:.6f},scale=384:-2,tile={n}x1"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(mp4), "-vf", fil, "-frames:v", "1", str(out)],
                   check=True)


def _frame(mp4: Path, t: float, out: Path) -> None:
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-ss", f"{t:.3f}", "-i", str(mp4), "-frames:v", "1",
                    str(out)], check=True)


def _diff_prompt(a: str, b: str) -> list[str]:
    sa = re.split(r"(?<=[.!?])\s+", a.strip())
    sb = re.split(r"(?<=[.!?])\s+", b.strip())
    return [ln for ln in difflib.unified_diff(sa, sb, "antes", "despues", lineterm="", n=0)
            if not ln.startswith(("---", "+++", "@@"))]


def _copy(src: Path, dst: Path) -> str | None:
    if not src.exists():
        return None
    dst.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(src, dst)
    return str(dst.relative_to(ROOT)).replace("\\", "/")


def main() -> int:
    from cost_tracker import cost_tracker
    import asset_manager as am
    import fase1_5
    import qa_studio_server as qs
    from script_engine import m03_imagenes_v3 as v3img
    from script_engine import m09_packaging as m09
    from script_engine.m03_visual import armar_item

    t0 = time.time()
    res: dict = {"tid": TID, "base": str(BASE.relative_to(ROOT)).replace("\\", "/"), "b1": {}, "b2": {}, "b3": {},
                 "errores": []}
    opus_calls: list[dict] = []

    def llamar_mirando(prompt, system_instruction=None, response_schema=None, description=None, **kw):
        """Wrapper de observación: delega en el Opus real de producción y anota prompt/salida."""
        from script_engine.m03_visual import _llamar_casilleros
        t = time.time()
        try:
            out = _llamar_casilleros(prompt, system_instruction=system_instruction, response_schema=response_schema,
                                     description=description, **kw)
        except Exception as e:  # noqa: BLE001
            opus_calls.append({"description": description, "prompt": prompt, "error": f"{type(e).__name__}: {e}"[:600],
                               "segundos": round(time.time() - t, 1)})
            raise
        opus_calls.append({"description": description, "prompt": prompt, "salida": out,
                           "segundos": round(time.time() - t, 1)})
        return out

    for d in ("b1", "b2", "b3"):
        (F59 / d).mkdir(exist_ok=True)

    cost_tracker.start_video("f59_parte_b")
    try:
        # ═══════════════════ B1 — composición ═══════════════════
        b1 = res["b1"]
        try:
            meta = json.loads((ROOT / "output" / TID / "publish" / "metadata.json").read_text(encoding="utf-8"))
            topic = fase1_5._load_topic_by_id(TID)          # sin asegurar_canon
            grupos = {g["id"]: g for g in topic.get("people_groups") or [] if isinstance(g, dict) and g.get("id")}
            lang = v3img.place_language(topic)
            b1["lang"] = lang
            b1["composicion_f58"] = COMPOSICION_F58
            b1["composicion_f59"] = m09.COMPOSICION_MINIATURA
            b1["paquetes"] = []
            compuestas: list[Path] = []
            for p in meta.get("paquetes", []):
                cas = json.loads(p["raw_llm_prompt"])
                anio, fuente = p.get("anio"), p.get("anio_fuente") or ""
                viejo = armar_item(json.loads(p["raw_llm_prompt"]), anio, grupos, False, lang,
                                   composicion=COMPOSICION_F58, sin_cartel=True, anio_fuente=fuente)
                nuevo = armar_item(json.loads(p["raw_llm_prompt"]), anio, grupos, False, lang,
                                   composicion=m09.COMPOSICION_MINIATURA, sin_cartel=True, anio_fuente=fuente)
                row = {"n": p["n"], "estrategia": p.get("estrategia"), "titulo": p.get("titulo"), "texto": p.get("texto"),
                       "anio": anio, "anio_fuente": fuente, "casilleros": cas,
                       "prompt_f58": p.get("prompt"), "prompt_viejo_rearmado": viejo["prompt"],
                       "byte_identico_con_oracion_vieja": viejo["prompt"] == p.get("prompt"),
                       "prompt_f59": nuevo["prompt"], "diff": _diff_prompt(p.get("prompt") or "", nuevo["prompt"]),
                       "_f8_problemas": nuevo.get("_f8_problemas"), "_f8_slots_scrub": nuevo.get("_f8_slots_scrub"),
                       "_f8_texto_fuera": nuevo.get("_f8_texto_fuera")}
                base_out = F59 / "b1" / f"paquete_{p['n']:02d}_base_f59.png"
                t = time.time()
                row["motivo_sin_foto"] = m09.foto_paquete(nuevo["prompt"], base_out)
                row["segundos_foto"] = round(time.time() - t, 1)
                row["base_f59"] = str(base_out.relative_to(ROOT)).replace("\\", "/") if base_out.exists() else None
                if base_out.exists():
                    comp = m09.compose_thumbnail(base_out, p.get("texto") or "", F59 / "b1" / f"paquete_{p['n']:02d}_f59.png")
                    row["compuesta_f59"] = str(comp.relative_to(ROOT)).replace("\\", "/")
                    compuestas.append(comp)
                row["compuesta_f58"] = f"output/{TID}/publish/thumb_candidates/{p.get('miniatura')}"
                b1["paquetes"].append(row)
            if compuestas:
                hoja = F59 / "hoja_paquetes_f59.jpg"
                _hstack(compuestas, hoja)
                b1["hoja_f59"] = str(hoja.relative_to(ROOT)).replace("\\", "/")
                hoja58 = ROOT / "lab" / "hyperframes" / "f58" / "hoja_paquetes.jpg"
                if hoja58.exists():
                    both = F59 / "hoja_paquetes_f58_vs_f59.jpg"
                    _vstack([hoja58, hoja], both)
                    b1["hoja_f58_vs_f59"] = str(both.relative_to(ROOT)).replace("\\", "/")
        except Exception as e:  # noqa: BLE001
            res["errores"].append(f"B1: {type(e).__name__}: {e}"[:1500])

        # ═══════════════════ B2 — foto ═══════════════════
        b2 = res["b2"]
        try:
            state = qs.QAState(TID, base_dir=BASE)
            cap = IMG_B2[:4]
            vpath = qs._visual_path(state, TID)
            visual = qs._read_json(vpath)
            entry = state.resolve_fix_entry(IMG_B2)
            b2["entry_antes"] = {k: v for k, v in (entry or {}).items() if k != "casilleros"}
            item03 = qs._item_of(qs._chapter_of(visual, cap), "img", int(IMG_B2[9:11]))
            b2["casilleros_antes"] = json.loads(item03["raw_llm_prompt"])
            b2["prompt_antes"] = item03["prompt"]
            b2["anio_antes"] = [item03.get("anio"), item03.get("anio_fuente")]
            b2["ancla"] = item03.get("narration_anchor")
            out_path = state.resolve_image(cap, IMG_B2) or (state.assets_dir / f"{cap}_flux" / IMG_B2)
            graded = out_path.with_name(f"{out_path.stem}_graded{out_path.suffix}")
            # la foto del 28-oct (guion vivo viejo) se guarda aparte, para la historia
            b2["foto_28oct"] = _copy(out_path, F59 / "b2" / "ch03_img_08_28oct.png")
            b2["foto_28oct_graded"] = _copy(graded, F59 / "b2" / "ch03_img_08_28oct_graded.png")
            seed = am._seed_for_subject(TID, item03.get("subject_ref"))
            b2["seed"] = seed
            b2["subject_ref"] = item03.get("subject_ref")
            t = time.time()
            am._generate_flux_image_at(b2["prompt_antes"], "", out_path, am._is_hook_chapter(cap), seed=seed,
                                       foto_madre_data_uris=None)
            qs._grade_como_produccion(out_path)
            b2["segundos_antes"] = round(time.time() - t, 1)
            b2["antes"] = _copy(out_path, F59 / "b2" / "antes.png")
            b2["antes_graded"] = _copy(graded, F59 / "b2" / "antes_graded.png")

            n_opus = len(opus_calls)
            t = time.time()
            ok, reason = qs._fix_core(state, TID, cap, IMG_B2, PEDIDO_B2, llamar_fn=llamar_mirando)
            b2["segundos_fix"] = round(time.time() - t, 1)
            b2["ok"], b2["reason"] = ok, reason
            b2["opus"] = opus_calls[n_opus:]
            visual2 = qs._read_json(vpath)
            item03b = qs._item_of(qs._chapter_of(visual2, cap), "img", int(IMG_B2[9:11]))
            script2 = qs._read_json(state.script_path)
            vivo_b = qs._item_of(qs._chapter_of(script2, cap), "img", int(IMG_B2[9:11]))
            b2["casilleros_despues"] = json.loads(item03b["raw_llm_prompt"])
            b2["prompt_despues"] = item03b["prompt"]
            b2["anio_despues"] = [item03b.get("anio"), item03b.get("anio_fuente")]
            b2["casilleros_cambiados"] = {k: {"antes": b2["casilleros_antes"].get(k), "despues": v}
                                          for k, v in b2["casilleros_despues"].items()
                                          if v != b2["casilleros_antes"].get(k)}
            b2["casilleros_quitados"] = [k for k in b2["casilleros_antes"] if k not in b2["casilleros_despues"]]
            b2["diff_prompt"] = _diff_prompt(b2["prompt_antes"], b2["prompt_despues"])
            b2["_f8_slots_scrub"] = item03b.get("_f8_slots_scrub")
            b2["_f8_problemas"] = item03b.get("_f8_problemas")
            b2["_f8_texto_fuera"] = item03b.get("_f8_texto_fuera")
            b2["vivo_igual_a_03"] = (vivo_b or {}).get("prompt") == item03b.get("prompt") and \
                                    (vivo_b or {}).get("raw_llm_prompt") == item03b.get("raw_llm_prompt")
            b2["despues"] = _copy(out_path, F59 / "b2" / "despues.png")
            b2["despues_graded"] = _copy(graded, F59 / "b2" / "despues_graded.png")
            bdir = state.assets_dir / "_qa_backups"
            b2["backups"] = sorted(p.name for p in bdir.glob("*")) if bdir.exists() else []
            if b2.get("antes_graded") and b2.get("despues_graded"):
                hoja = F59 / "b2" / "hoja_b2.jpg"
                _hstack([ROOT / b2["antes_graded"], ROOT / b2["despues_graded"]], hoja, w=960)
                b2["hoja"] = str(hoja.relative_to(ROOT)).replace("\\", "/")
        except Exception as e:  # noqa: BLE001
            res["errores"].append(f"B2: {type(e).__name__}: {e}"[:1500])

        # ═══════════════════ B3 — clip ═══════════════════
        b3 = res["b3"]
        try:
            state = qs.QAState(TID, base_dir=BASE)
            entry = state.resolve_clip_entry("ch01")
            b3["entry"] = {k: v for k, v in (entry or {}).items()}
            b3["movimiento_antes"] = entry["video_prompt"]
            out_clip = Path(entry["out_clip"])
            first = Path(entry["first_frame"])
            b3["clip_antes"] = _copy(out_clip, F59 / "b3" / "antes.mp4")
            b3["dur_antes"] = _dur(out_clip)
            b3["foto_inicial_md5_antes"] = _md5(first)
            cap_log: list[dict] = []
            final_res: dict = {}

            def foto_final_mirando(foto_inicial, image_prompt, voz_clip, out_path, *, use_ultra=False):
                t = time.time()
                r = am.foto_final_del_clip(foto_inicial, image_prompt, voz_clip, out_path, use_ultra=use_ultra)
                final_res.update({k: (str(v) if isinstance(v, Path) else v) for k, v in r.items()},
                                 segundos=round(time.time() - t, 1), use_ultra=use_ultra)
                return r

            def clip_mirando(foto, movimiento, output_path, *, image_prompt="", ancla="", foto_final=None, log=None):
                t = time.time()
                try:
                    return am._generate_clip(foto, movimiento, output_path, image_prompt=image_prompt, ancla=ancla,
                                             foto_final=foto_final, log=cap_log)
                finally:
                    for f in cap_log:
                        f.setdefault("segundos_reloj", round(time.time() - t, 1))
                    if log is not None:
                        log.extend(cap_log)

            n_opus = len(opus_calls)
            t = time.time()
            ok, reason = qs._clipfix_core(state, TID, "ch01", PEDIDO_B3, llamar_fn=llamar_mirando,
                                          foto_final_fn=foto_final_mirando, generate_clip_fn=clip_mirando)
            b3["segundos_total"] = round(time.time() - t, 1)
            b3["ok"], b3["reason"] = ok, reason
            b3["opus"] = opus_calls[n_opus:]
            b3["foto_final"] = final_res
            b3["clip_log"] = cap_log
            e2 = state.resolve_clip_entry("ch01") or {}
            b3["movimiento_despues"] = e2.get("video_prompt")
            v3 = qs._read_json(qs._visual_path(state, TID))
            b3["movimiento_03_visual"] = (qs._chapter_of(v3, "ch01") or {}).get("video_prompt")
            b3["foto_inicial_md5_despues"] = _md5(first)
            b3["clip_despues"] = _copy(out_clip, F59 / "b3" / "despues.mp4")
            b3["dur_despues"] = _dur(out_clip)
            if final_res.get("path"):
                b3["foto_final_copia"] = _copy(Path(final_res["path"]), F59 / "b3" / "ch01_img_01_final.png")
            b3["foto_inicial_copia"] = _copy(first, F59 / "b3" / "ch01_img_01.png")
            for tag, mp4 in (("antes", F59 / "b3" / "antes.mp4"), ("despues", F59 / "b3" / "despues.mp4")):
                if mp4.exists():
                    _tira(mp4, F59 / "b3" / f"tira_{tag}.jpg")
                    b3[f"tira_{tag}"] = f"lab/hyperframes/f59/b3/tira_{tag}.jpg"
            # SSIM primer/último cuadro del clip nuevo contra la foto inicial y la final (asset_manager._ssim)
            if (F59 / "b3" / "despues.mp4").exists():
                d = b3["dur_despues"] or 8.0
                f0, f1 = F59 / "b3" / "despues_f0.png", F59 / "b3" / "despues_f1.png"
                _frame(F59 / "b3" / "despues.mp4", 0.0, f0)
                _frame(F59 / "b3" / "despues.mp4", max(d - 0.05, 0), f1)
                b3["ssim_clip"] = {"primer_cuadro_vs_inicial": am._ssim(first, f0),
                                   "ultimo_cuadro_vs_final": am._ssim(Path(final_res["path"]), f1) if final_res.get("path") else None,
                                   "ultimo_cuadro_vs_inicial": am._ssim(first, f1)}
            bdir = state.assets_dir / "_qa_backups"
            b3["backups"] = sorted(p.name for p in bdir.glob("*")) if bdir.exists() else []
        except Exception as e:  # noqa: BLE001
            res["errores"].append(f"B3: {type(e).__name__}: {e}"[:1500])
    finally:
        rep = cost_tracker.end_video()

    res["segundos_reloj"] = round(time.time() - t0, 1)
    res["cost_tracker"] = [{"servicio": x.service, "descripcion": x.description, "usd": round(x.total_cost, 5),
                            "stage": getattr(x, "stage", None)} for x in (rep.entries if rep else [])]
    res["usd_total"] = round(rep.total_cost, 4) if rep else None
    res["opus_calls"] = opus_calls
    (F59 / "parte_b.json").write_text(json.dumps(res, ensure_ascii=False, indent=1, default=str), encoding="utf-8")
    print(json.dumps({"errores": res["errores"], "usd_total": res["usd_total"], "segundos": res["segundos_reloj"],
                      "b1": [(r["n"], r["byte_identico_con_oracion_vieja"], r["motivo_sin_foto"]) for r in res["b1"].get("paquetes", [])],
                      "b2": (res["b2"].get("ok"), res["b2"].get("reason")),
                      "b3": (res["b3"].get("ok"), res["b3"].get("reason"))}, ensure_ascii=False, indent=1))
    return 1 if res["errores"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
