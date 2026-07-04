"""
test_module_asset_manager_telemetria.py — HANDOFF_133 (offline, sin llamar a fal).

Verifica que la telemetría del /edit anclado NO miente:
  1. con foto_madre_data_uris → el `endpoint` del return Y la submit_url contienen "/edit",
     y la etiqueta de costo va con mode="edit".
  2. sin uris → el `endpoint` == model_id t2i del perfil, y el costo va con mode="t2i".

Monkeypatch de requests.post/get (captura la submit_url, devuelve respuesta mínima
válida) + del cost tracker de seedream (captura el mode). NO toca fal ni disco de red.

USO:
    python test_module_asset_manager_telemetria.py
"""
import sys
import tempfile
from pathlib import Path

import asset_manager as am
from config import api


class _FakeResp:
    def __init__(self, jd=None, content=b""):
        self._jd = jd or {}
        self.content = content

    def raise_for_status(self):
        pass

    def json(self):
        return self._jd


def main() -> int:
    fails: list[str] = []
    captured: dict = {}
    cost_modes: list[str] = []

    # ── Monkeypatch red ──
    def fake_post(url, headers=None, json=None, timeout=None):
        captured["submit_url"] = url
        return _FakeResp({"images": [{"url": "http://fake/x.png", "width": 10, "height": 10}],
                          "seed": 1})

    def fake_get(url, headers=None, timeout=None):
        return _FakeResp(content=b"\x89PNG\r\n\x1a\nfakebytes")

    am.requests.post = fake_post
    am.requests.get = fake_get

    # ── Monkeypatch cost tracker seedream (captura el mode; no persiste) ──
    def fake_track_seedream(description, images=1, mode="t2i"):
        cost_modes.append(mode)

    am._SYNC_COST_TRACKERS = dict(am._SYNC_COST_TRACKERS)
    am._SYNC_COST_TRACKERS["seedream"] = fake_track_seedream

    # Forzar el motor de perfil (el /edit vive SOLO en seedream).
    api.image_engine = "seedream"
    profile = am.select_profile("seedream")
    t2i_model = profile.render.model_id

    tmp = Path(tempfile.mkdtemp())

    # ── Caso 1: CON anclas → /edit ──
    meta_edit = am._generate_image_raw(
        "un prompt", tmp / "edit.png", use_ultra=False, seed=1,
        foto_madre_data_uris=["data:image/png;base64,AAAA"],
    )
    if "/edit" not in meta_edit["endpoint"]:
        fails.append(f"[1] endpoint del return no contiene '/edit': {meta_edit['endpoint']!r}")
    edit_submit = captured.get("submit_url", "")   # snapshot antes de que el caso 2 lo pise
    if "/edit" not in edit_submit:
        fails.append(f"[1] submit_url no contiene '/edit': {edit_submit!r}")
    if not cost_modes or cost_modes[-1] != "edit":
        fails.append(f"[1] costo no etiquetado 'edit': {cost_modes[-1:]!r}")

    # ── Caso 2: SIN anclas → t2i == model_id del perfil ──
    meta_t2i = am._generate_image_raw(
        "un prompt", tmp / "t2i.png", use_ultra=False, seed=1,
        foto_madre_data_uris=None,
    )
    if meta_t2i["endpoint"] != t2i_model:
        fails.append(f"[2] endpoint t2i != model_id perfil: {meta_t2i['endpoint']!r} vs {t2i_model!r}")
    if "text-to-image" not in captured.get("submit_url", ""):
        fails.append(f"[2] submit_url t2i no es text-to-image: {captured.get('submit_url')!r}")
    if not cost_modes or cost_modes[-1] != "t2i":
        fails.append(f"[2] costo no etiquetado 't2i': {cost_modes[-1:]!r}")

    print("─" * 60)
    print(f"[1] edit  endpoint  : {meta_edit['endpoint']}")
    print(f"[1] edit  submit_url: {edit_submit}")
    print(f"[2] t2i   endpoint  : {meta_t2i['endpoint']}")
    print(f"[2] t2i   submit_url: {captured.get('submit_url')}")
    print(f"    cost modes vistos: {cost_modes}")
    print("─" * 60)

    if fails:
        print(f"[FAIL] {len(fails)} assert(s):")
        for f in fails:
            print(f"   ✗ {f}")
        return 1
    print("[PASS] telemetría no miente: endpoint REAL + label de costo edit/t2i")
    return 0


if __name__ == "__main__":
    sys.exit(main())
