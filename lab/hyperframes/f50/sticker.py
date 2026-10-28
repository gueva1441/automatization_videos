# -*- coding: utf-8 -*-
"""Reescribe campos del sticker de un archivo de producción en lab/mapa/stickers/<zona>.json (mismo formato que tiene:
indent=1, sin escapar, CRLF o LF, con o sin salto final) y pone el md5 actual del archivo.
Uso: python sticker.py <zona> <archivo> <json con campos>   (campo con valor null → se borra del sticker)"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
zona, archivo = sys.argv[1], sys.argv[2]
campos = json.loads(Path(sys.argv[3]).read_text(encoding="utf-8")) if len(sys.argv) > 3 else {}
p = ROOT / "lab" / "mapa" / "stickers" / f"{zona}.json"
raw = p.read_bytes()
d = json.loads(raw.decode("utf-8"))
nl = "\r\n" if b"\r\n" in raw else "\n"
fin = raw[len(raw.rstrip(b"\r\n")):]


def _dump(x) -> bytes:
    return json.dumps(x, ensure_ascii=False, indent=1).replace("\n", nl).encode("utf-8")


assert _dump(d) + fin == raw, "formato distinto"
e = dict(d.get(archivo) or {})
for k, v in campos.items():
    if v is None:
        e.pop(k, None)
    else:
        e[k] = v
e["md5"] = hashlib.md5((ROOT / archivo).read_bytes()).hexdigest()
d[archivo] = e
p.write_bytes(_dump(d) + fin)
print(f"{zona}: {archivo} → md5 {e['md5'][:8]}")
