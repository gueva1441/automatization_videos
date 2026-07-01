"""
lab/probe_lock_imageref.py — PROBE EXPLORATORIO (HANDOFF_PROBE_lock_imageref).

Mide si el LOCK de un objeto se puede hacer por REFERENCIA-IMAGEN (Seedream 4.5 /edit
con image_urls) en vez de por TEXTO denso. NO es producción: script suelto, corrido a
mano, escribe SOLO a lab/outputs/probe_lock_imageref/. NO toca m03/fase2a/fase1_5.

Hipótesis:
  H1 · una foto-ancla del objeto → /edit en 3 escenas → ¿la gestalt (silueta/proporción)
       se mantiene?
  H2 · dos anclas (sub + reactor) como image_urls → /edit cutaway → ¿ambos reconocibles y
       el reactor ADENTRO del sub?

Único acople a producción permitido por el handoff: reusar la AUTH de fal (config.api).
No importa ningún módulo del pipeline.

Uso:
  python lab/probe_lock_imageref.py --paso0            # solo genera la foto-ancla del sub (t2i)
  python lab/probe_lock_imageref.py --smoke-edit       # paso0 + smoke-test de /edit (con el sub de ref)
  python lab/probe_lock_imageref.py --reactor <path|url>   # corrida COMPLETA (H1 3 edits + H2)
       (--reactor acepta URL http(s) o un path local — el local se manda como data-URI base64)
"""
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import sys
import time
from pathlib import Path

import requests

# Repo root al path (el script vive en lab/, config.py está en la raíz).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

# ── ÚNICO acople permitido: la auth de fal (no re-escribir key). No es módulo de pipeline. ──
from config import api, pipeline

if sys.stdout.encoding and sys.stdout.encoding.lower() != "utf-8":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ═══════════════════════════════════════════════════════════════
#  CONSTANTES fal (reusadas de la config de prod, NO tocadas)
# ═══════════════════════════════════════════════════════════════
BASE_URL = "https://fal.run"
T2I_MODEL = "fal-ai/bytedance/seedream/v4.5/text-to-image"
EDIT_MODEL = "fal-ai/bytedance/seedream/v4.5/edit"        # /edit (SYNC, image_urls de referencia)
IMAGE_SIZE = {"width": pipeline.image_width, "height": pipeline.image_height}   # 2560×1440 (16:9)

OUT_DIR = Path(__file__).parent / "outputs" / "probe_lock_imageref"
RESULTS_JSON = OUT_DIR / "results.json"


def _headers() -> dict[str, str]:
    return {"Authorization": f"Key {api.fal_api_key}", "Content-Type": "application/json"}


# ═══════════════════════════════════════════════════════════════
#  LLAMADAS
# ═══════════════════════════════════════════════════════════════
def _post(model: str, payload: dict, timeout: int = 240) -> dict:
    url = f"{BASE_URL}/{model}"
    resp = requests.post(url, headers=_headers(), json=payload, timeout=timeout)
    if resp.status_code == 404:
        raise RuntimeError(
            f"ENDPOINT NO DISPONIBLE (404): {url}. El modelo /edit no está accesible con la "
            f"key/cliente actual. PARANDO (regla §4 del probe — no improvisar otro proveedor)."
        )
    resp.raise_for_status()
    return resp.json()


def t2i(prompt: str) -> dict:
    """Text-to-image Seedream 4.5. Devuelve {url_out, seed}."""
    payload = {
        "prompt": prompt,
        "image_size": IMAGE_SIZE,
        "num_images": 1,
        "enable_safety_checker": True,
        "output_format": "png",
    }
    data = _post(T2I_MODEL, payload)
    return {"url_out": data["images"][0]["url"], "seed": data.get("seed")}


def edit(prompt: str, image_urls: list[str]) -> dict:
    """Seedream 4.5 /edit con image_urls de referencia. Devuelve {url_out, seed}."""
    payload = {
        "prompt": prompt,
        "image_urls": image_urls,
        "image_size": IMAGE_SIZE,
        "num_images": 1,
        "enable_safety_checker": True,
        "output_format": "png",
    }
    data = _post(EDIT_MODEL, payload)
    return {"url_out": data["images"][0]["url"], "seed": data.get("seed")}


# ═══════════════════════════════════════════════════════════════
#  HELPERS
# ═══════════════════════════════════════════════════════════════
def _to_ref(path_or_url: str) -> str:
    """URL http(s) → tal cual. Path local → data-URI base64 (fal acepta data-URIs)."""
    if path_or_url.startswith(("http://", "https://", "data:")):
        return path_or_url
    p = Path(path_or_url)
    if not p.exists():
        raise FileNotFoundError(f"--reactor: no existe el archivo {p}")
    mime = mimetypes.guess_type(str(p))[0] or "image/png"
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def _download(url: str, out_path: Path) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_bytes(requests.get(url, timeout=120).content)


def _record(results: list, *, id_: str, endpoint: str, prompt: str,
            image_urls_in: list[str], out: dict, filename: str, note: str = "") -> None:
    # image_urls_in: recortar data-URIs largos en el manifiesto (guardar solo un marcador legible).
    refs = [(u[:60] + "…[data-uri]") if u.startswith("data:") else u for u in image_urls_in]
    results.append({
        "id": id_, "endpoint": endpoint, "prompt": prompt,
        "image_urls_in": refs, "url_out": out["url_out"], "seed": out.get("seed"),
        "file": filename, "note": note,
    })
    print(f"  ✓ {id_} [{endpoint}] → {filename}  (seed={out.get('seed')})")
    print(f"      url_out: {out['url_out']}")


def _flush(results: list) -> None:
    RESULTS_JSON.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_JSON.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")


# ═══════════════════════════════════════════════════════════════
#  PROMPTS (verbatim del handoff)
# ═══════════════════════════════════════════════════════════════
P_SUB = ("An extreme wide shot of a Soviet Hotel-class ballistic missile submarine, 1960s, on the "
         "surface of the North Atlantic: long black steel hull with rounded bow, dark red lower hull "
         "below the waterline, an unusually tall and bulky conning tower elongated rearward housing "
         "three vertical ballistic missile silos, small rectangular bridge windows, no hull numbers. "
         "Cold overcast daylight, desaturated steel and teal sea, dark documentary, photorealistic, "
         "no text anywhere, 16:9.")

P_REACTOR = ("A wide shot of a large vertical cylindrical steel pressurized-water naval reactor vessel, "
             "tall — its height roughly twice its diameter — shallow domed top and rounded base, bare "
             "unmarked riveted steel plating, insulated pipework wrapped horizontally around the body, "
             "one manual valve wheel, one small analog pressure gauge with a plain unmarked white dial "
             "face, no digital screens. Radioactive, scorched, streaked with rust, resting on a heavy "
             "railway flatcar inside a cavernous Soviet shipyard, 1964, harsh overhead lights. "
             "Desaturated steel, dark documentary, photorealistic, no signage, no text anywhere, 16:9.")

P_H1_1 = ("This exact reactor vessel, now resting on the dark silted seabed of an arctic bay, partially "
          "covered in sediment, murky green water, deep underwater gloom. Keep the vessel's shape, "
          "proportions and riveted plating identical. Desaturated, photorealistic, 16:9.")
P_H1_2 = ("This exact reactor vessel, now sealed inside a heavy welded steel containment shell, being "
          "lowered by crane cables toward dark icy water from a barge. Keep the vessel's shape and "
          "proportions identical. Desaturated, photorealistic, 16:9.")
P_H1_3 = ("This exact reactor vessel decades later, heavily rusted and corroded, abandoned in a frozen "
          "scrapyard under grey sky. Keep the vessel's shape, proportions and riveted plating identical, "
          "only aged and rusted. Desaturated, photorealistic, 16:9.")

P_H2 = ("Cutaway cross-section of the submarine from the first reference image, hull opened to reveal "
        "its interior. Integrated inside the exposed reactor bay, the cylindrical reactor vessel from "
        "the second reference image, matching its shape and riveted plating. 1963 shipyard, harsh work "
        "lights. Desaturated steel, dark documentary, photorealistic, no text anywhere, 16:9.")

P_SMOKE = ("This exact submarine, now surfacing through drifting arctic ice fog under a pale low sun. "
           "Keep the hull shape, conning tower proportions and silhouette identical. Desaturated, "
           "photorealistic, 16:9.")


# ═══════════════════════════════════════════════════════════════
#  MAIN
# ═══════════════════════════════════════════════════════════════
def main() -> int:
    ap = argparse.ArgumentParser(description="Probe lock por referencia-imagen (Seedream 4.5 /edit).")
    ap.add_argument("--reactor", default=None,
                    help="OVERRIDE opcional de la ancla del reactor (URL http(s) o path local). "
                         "Por defecto el probe la GENERA por t2i (PASO 0-bis).")
    ap.add_argument("--paso0", action="store_true", help="Solo las anclas t2i (sub + reactor), sin /edit.")
    ap.add_argument("--smoke-edit", action="store_true",
                    help="Solo sub + smoke-test de /edit (sub como ref throwaway; NO corre H1/H2).")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    results: list = []

    # ── PASO 0 — foto-ancla del submarino (t2i) ──
    print("\n[PASO 0] t2i submarino (canon v2 verbatim)...")
    sub = t2i(P_SUB)
    _download(sub["url_out"], OUT_DIR / "PASO0.png")
    _record(results, id_="PASO0", endpoint="t2i", prompt=P_SUB,
            image_urls_in=[], out=sub, filename="PASO0.png",
            note="ancla del submarino; url_out = url_sub_ancla para H2")
    _flush(results)
    url_sub_ancla = sub["url_out"]

    # ── smoke-test de /edit (opcional, aislado) ──
    if args.smoke_edit and not args.reactor:
        print("\n[SMOKE] /edit availability con el sub como ref throwaway (NO es H1)...")
        sm = edit(P_SMOKE, [url_sub_ancla])
        _download(sm["url_out"], OUT_DIR / "SMOKE_edit_sub.png")
        _record(results, id_="SMOKE_edit_sub", endpoint="edit", prompt=P_SMOKE,
                image_urls_in=[url_sub_ancla], out=sm, filename="SMOKE_edit_sub.png",
                note="smoke-test de /edit sobre el SUB (no el reactor). Confirma endpoint + gestalt del sub.")
        _flush(results)
        print(f"\n✅ Smoke OK — results.json en {RESULTS_JSON}")
        return 0

    # ── PASO 0-bis — foto-ancla del REACTOR (t2i, o override --reactor) ──
    if args.reactor:
        print(f"\n[PASO 0-bis] override: usando ancla del reactor provista ({args.reactor[:70]})...")
        reactor_ref = _to_ref(args.reactor)
        reactor_ref_label = args.reactor
    else:
        print("\n[PASO 0-bis] t2i reactor (ficha, sin nombre VM-A)...")
        reactor = t2i(P_REACTOR)
        _download(reactor["url_out"], OUT_DIR / "PASO0bis.png")
        _record(results, id_="PASO0bis", endpoint="t2i", prompt=P_REACTOR,
                image_urls_in=[], out=reactor, filename="PASO0bis.png",
                note="ancla del reactor generada por el propio probe; url_out = url_reactor_ancla para H1/H2")
        _flush(results)
        reactor_ref = reactor["url_out"]
        reactor_ref_label = reactor["url_out"]

    if args.paso0:
        print(f"\n✅ Anclas OK (sin /edit) — results.json en {RESULTS_JSON}")
        return 0

    print(f"\n[H1] mismo reactor, 3 escenas (/edit, ref = {reactor_ref_label[:70]})...")
    for tag, prompt, fname in (
        ("H1_edit1", P_H1_1, "H1_edit1.png"),
        ("H1_edit2", P_H1_2, "H1_edit2.png"),
        ("H1_edit3", P_H1_3, "H1_edit3.png"),
    ):
        out = edit(prompt, [reactor_ref])
        _download(out["url_out"], OUT_DIR / fname)
        _record(results, id_=tag, endpoint="edit", prompt=prompt,
                image_urls_in=[reactor_ref_label], out=out, filename=fname,
                note="H1: ¿la gestalt del reactor sobrevive el cambio de escena?")
        _flush(results)

    print("\n[H2] dos objetos → una foto (/edit, [sub, reactor])...")
    h2 = edit(P_H2, [url_sub_ancla, reactor_ref])
    _download(h2["url_out"], OUT_DIR / "H2_multi.png")
    _record(results, id_="H2_multi", endpoint="edit", prompt=P_H2,
            image_urls_in=[url_sub_ancla, reactor_ref_label], out=h2, filename="H2_multi.png",
            note="H2: ¿ambos reconocibles y el reactor ADENTRO del sub?")
    _flush(results)

    print(f"\n✅ Probe COMPLETO — anclas (sub+reactor) + H1×3 + H2 + results.json en {RESULTS_JSON}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
