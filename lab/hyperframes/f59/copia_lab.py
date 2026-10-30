"""
copia_lab.py — F59 Etapa 0 (punto 3): copia de lab de Wittenoom para QAState(tid, base_dir=.../f59/base).

Idempotente: rehace la copia entera. Sin LLM, sin fotos, sin red, US$ 0.
NO escribe en data/, output/ ni script_engine/ (se verifica con md5 del guion vivo antes/después).

Qué arma dentro de lab/hyperframes/f59/base/:
  data/scripts/<tid>.json                      ← m06_assembler.assemble_final_script con SCRIPTS_DIR
                                                  redirigido a la copia (STEPS_DIR y TOPICS_DB se LEEN de producción);
                                                  después: narration de cada cap = la del guion vivo data/scripts/<tid>.json
                                                  (no la de 01b_narration.json), y voz_clip en los caps veo (1 y 7).
  data/scripts/_steps/<tid>/03_visual.json     ← copia de producción + voz_clip en caps 1 y 7 (agregado de CC: la
                                                  Etapa A guarda ahí)
  data/scripts/_steps/<tid>/01a_skeleton.json  ← copia (QAState lee los roles de ahí)
  output/<tid>/assets/                         ← copytree de producción
  output/audio/<tid>/                          ← copytree solo si pesa < 100 MB

USO:  python lab/hyperframes/f59/copia_lab.py
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))

TID = "123bbb64-9fca-4395-8bf4-57d60e219ef1"
BASE = Path(__file__).resolve().parent / "base"
AUDIO_MAX_MB = 100

VIVO = ROOT / "data" / "scripts" / f"{TID}.json"
STEPS_PROD = ROOT / "data" / "scripts" / "_steps" / TID
ASSETS_PROD = ROOT / "output" / TID / "assets"
AUDIO_PROD = ROOT / "output" / "audio" / TID

SCRIPTS_COPIA = BASE / "data" / "scripts"
STEPS_COPIA = SCRIPTS_COPIA / "_steps" / TID
ASSETS_COPIA = BASE / "output" / TID / "assets"
AUDIO_COPIA = BASE / "output" / "audio" / TID


def md5(p: Path) -> str:
    h = hashlib.md5()
    with p.open("rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def md5_text(s: str) -> str:
    return hashlib.md5(s.encode("utf-8")).hexdigest()


def dir_size(p: Path) -> tuple[int, int]:
    """(archivos, bytes) recursivo."""
    n = b = 0
    for root, _dirs, files in os.walk(p):
        for f in files:
            n += 1
            b += (Path(root) / f).stat().st_size
    return n, b


def load(p: Path) -> dict:
    return json.loads(p.read_text(encoding="utf-8"))


def dump(p: Path, d: dict) -> None:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(d, ensure_ascii=False, indent=2), encoding="utf-8")


def ventana_chars(narr: str) -> int:
    """La ventana como en lab/hyperframes/f57/clip_b.py l.62-64 (y m03 _process_one_cap)."""
    from script_engine import m03_visual as m3
    from script_engine.guion_v4 import PALABRAS_POR_SEG
    dur = len(narr.split()) / PALABRAS_POR_SEG
    return max(1, min(int(m3.VEO_CLIP_DURATION_SEC * (len(narr) / dur)), len(narr) - 1))


def main() -> int:
    from script_engine import m03_visual as m3
    from script_engine import m06_assembler as m6

    print(f"ROOT  = {ROOT}\nBASE  = {BASE}\nTID   = {TID}\n")
    md5_vivo_antes = md5(VIVO)
    md5_steps_antes = {f: md5(STEPS_PROD / f) for f in ("03_visual.json", "01a_skeleton.json", "01b_narration.json")}

    # ── 0. rehacer la copia (idempotente) ──
    if BASE.exists():
        shutil.rmtree(BASE)
    BASE.mkdir(parents=True)

    # ── 1. ensamblar SIN LLM con SCRIPTS_DIR redirigido ──
    assert m6.SCRIPTS_DIR == ROOT / "data" / "scripts", m6.SCRIPTS_DIR
    assert m6.STEPS_DIR == ROOT / "data" / "scripts" / "_steps", m6.STEPS_DIR
    scripts_dir_orig = m6.SCRIPTS_DIR
    m6.SCRIPTS_DIR = SCRIPTS_COPIA
    try:
        out = m6.assemble_final_script(TID)
    finally:
        m6.SCRIPTS_DIR = scripts_dir_orig
    assert out.resolve() == (SCRIPTS_COPIA / f"{TID}.json").resolve(), out
    assert md5(VIVO) == md5_vivo_antes, "¡el guion vivo cambió tras assemble_final_script!"
    print(f"[1] ensamblado en la copia: {out.relative_to(ROOT)}  ({out.stat().st_size} bytes)")

    # ── 2a. narration = la del guion vivo; medir vs 01b ──
    copia = load(out)
    vivo = load(VIVO)
    n01b = {c["chapter_number"]: c.get("narration", "") for c in load(STEPS_PROD / "01b_narration.json")["chapters"]}
    nvivo = {c["chapter_number"]: c.get("narration", "") for c in vivo["chapters"]}
    print("\n[2a] narración: 01b_narration.json vs guion vivo data/scripts/<tid>.json")
    print("| cap | chars 01b | chars vivo | md5 01b | md5 vivo | iguales |")
    print("|---|---|---|---|---|---|")
    difieren = 0
    for cap in copia["chapters"]:
        n = cap["chapter_number"]
        a, b = n01b.get(n, ""), nvivo[n]
        ig = a == b
        difieren += (not ig)
        print(f"| {n} | {len(a)} | {len(b)} | {md5_text(a)[:8]} | {md5_text(b)[:8]} | {'sí' if ig else 'NO'} |")
        cap["narration"] = b
    print(f"→ caps que difieren: {difieren} de {len(copia['chapters'])}")

    # ── 2b. voz_clip en caps veo ──
    visual = load(STEPS_PROD / "03_visual.json")
    vis_by = {c["chapter_number"]: c for c in visual["chapters"]}
    print("\n[2b] voz_clip (caps con render_engine == veo)")
    print("| cap | veo_position | palabras | chars | ventana | palabras voz_clip | chars voz_clip |")
    print("|---|---|---|---|---|---|---|")
    voz_por_cap: dict[int, str] = {}
    for cap in copia["chapters"]:
        if cap.get("render_engine") != "veo":
            continue
        n = cap["chapter_number"]
        narr = cap["narration"]
        pos = vis_by[n].get("veo_position", "start")
        v = ventana_chars(narr)
        voz = m3.voz_del_clip(narr, pos, v)
        cap["voz_clip"] = voz
        voz_por_cap[n] = voz
        print(f"| {n} | {pos} | {len(narr.split())} | {len(narr)} | {v} | {len(voz.split())} | {len(voz)} |")
    for n, voz in voz_por_cap.items():
        print(f"\nvoz_clip cap {n}:\n«{voz}»")
    dump(out, copia)

    # ── 3. _steps de la copia: 03_visual (+voz_clip) y 01a_skeleton ──
    for n, voz in voz_por_cap.items():
        vis_by[n]["voz_clip"] = voz
    dump(STEPS_COPIA / "03_visual.json", visual)
    shutil.copyfile(STEPS_PROD / "01a_skeleton.json", STEPS_COPIA / "01a_skeleton.json")
    print(f"\n[3] _steps copiados a {STEPS_COPIA.relative_to(ROOT)}: 03_visual.json (+voz_clip caps {sorted(voz_por_cap)}), 01a_skeleton.json")

    # ── 4. assets y audio ──
    shutil.copytree(ASSETS_PROD, ASSETS_COPIA, dirs_exist_ok=True)
    na, ba = dir_size(ASSETS_COPIA)
    print(f"[4] assets: {na} archivos, {ba / 2**20:.1f} MB → {ASSETS_COPIA.relative_to(ROOT)}")
    if AUDIO_PROD.exists():
        nau, bau = dir_size(AUDIO_PROD)
        mb = bau / 2**20
        if mb < AUDIO_MAX_MB:
            shutil.copytree(AUDIO_PROD, AUDIO_COPIA, dirs_exist_ok=True)
            print(f"[4] audio: {nau} archivos, {mb:.1f} MB (< {AUDIO_MAX_MB} MB) → copiado a {AUDIO_COPIA.relative_to(ROOT)}")
        else:
            print(f"[4] audio: {nau} archivos, {mb:.1f} MB (≥ {AUDIO_MAX_MB} MB) → NO se copia")
    else:
        print("[4] audio: output/audio/<tid> no existe → nada que copiar")

    # ── 5. verificación con QAState ──
    import qa_studio_server as qs
    st = qs.QAState(TID, base_dir=BASE)
    assert st.script_path == (BASE / "data" / "scripts" / f"{TID}.json").resolve(), st.script_path
    print(f"\n[5] QAState(tid, base_dir=base): caps en _script = {len(st._script)}")
    for cid, info in st._script.items():
        print(f"    {cid}: render_engine={info['render_engine']} veo_position={info['veo_position']} "
              f"anchors={len(info['anchors'])} supp={len(info['supp_anchors'])} role={st._roles.get(cid, '')}")
    assert len(st._script) == 7, len(st._script)
    flux02 = st._flux_imgs("ch02")
    clip01 = st.resolve_clip("ch01")
    print(f"    _flux_imgs('ch02') = {len(flux02)} PNG (primero: {flux02[0].name if flux02 else None})")
    print(f"    resolve_clip('ch01') = {clip01.relative_to(ROOT) if clip01 else None}")
    print(f"    resolve_audio('ch01') = {st.resolve_audio('ch01')}")
    print(f"    words ch01 = {len(st._load_words('ch01'))}")
    assert flux02, "_flux_imgs('ch02') vacío"
    assert clip01 is not None and clip01.suffix == ".mp4", clip01

    # árbol
    print(f"\n[5] árbol de {BASE.relative_to(ROOT)}/ (dir · archivos directos · MB directos)")
    for root, dirs, files in os.walk(BASE):
        dirs.sort()
        rp = Path(root)
        b = sum((rp / f).stat().st_size for f in files)
        depth = len(rp.relative_to(BASE).parts)
        print(f"    {'  ' * depth}{rp.name if depth else 'base'}/  ({len(files)} archivos, {b / 2**20:.1f} MB)")
    ntot, btot = dir_size(BASE)
    print(f"    TOTAL: {ntot} archivos, {btot / 2**20:.1f} MB")

    # md5
    print("\n[5] md5")
    print(f"    guion COPIA {out.relative_to(ROOT)}: {md5(out)}")
    print(f"    guion VIVO  {VIVO.relative_to(ROOT)}: antes {md5_vivo_antes} · después {md5(VIVO)}")
    assert md5(VIVO) == md5_vivo_antes, "¡el guion vivo cambió!"
    for f, h in md5_steps_antes.items():
        assert md5(STEPS_PROD / f) == h, f"¡{f} de producción cambió!"
    print(f"    _steps de producción (03_visual, 01a_skeleton, 01b_narration): sin cambios")
    print("\nOK — producción intacta, copia de lab lista.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
