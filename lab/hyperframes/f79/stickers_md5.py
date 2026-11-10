"""F79: reescribe el md5 del sticker de cada archivo de producción tocado (el texto del sticker no nombra intro, pre-roll
ni pausa tras cita, así que solo cambia el md5). Uso: python lab/hyperframes/f79/stickers_md5.py <archivo> [...]"""
import glob
import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]


def main(archivos: list[str]) -> int:
    hechos = set()
    for f in glob.glob(str(RAIZ / "lab" / "mapa" / "stickers" / "*.json")):
        d = json.loads(Path(f).read_text(encoding="utf-8"))
        cambio = False
        for a in archivos:
            if a in d and isinstance(d[a], dict):
                m = hashlib.md5((RAIZ / a).read_bytes()).hexdigest()
                if d[a].get("md5") != m:
                    print(f"{Path(f).name}: {a} {str(d[a].get('md5'))[:8]}… → {m[:8]}…")
                    d[a]["md5"] = m
                    cambio = True
                hechos.add(a)
        if cambio:
            Path(f).write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    for a in archivos:
        if a not in hechos:
            print(f"sin sticker: {a}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
