"""F79: reescribe el md5 del sticker de cada archivo de producción tocado (el texto del sticker no nombra intro, pre-roll
ni pausa tras cita, así que solo cambia el md5). Reemplaza el md5 viejo por el nuevo en el texto del json, sin volver a
serializarlo (cada zona tiene su propia sangría). Uso: python lab/hyperframes/f79/stickers_md5.py <archivo> [...]"""
import glob
import hashlib
import json
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[3]


def main(archivos: list[str]) -> int:
    hechos = set()
    for f in glob.glob(str(RAIZ / "lab" / "mapa" / "stickers" / "*.json")):
        texto = Path(f).read_text(encoding="utf-8")
        d = json.loads(texto)
        nuevo_texto = texto
        for a in archivos:
            if a in d and isinstance(d[a], dict):
                viejo, m = str(d[a].get("md5")), hashlib.md5((RAIZ / a).read_bytes()).hexdigest()
                if viejo != m:
                    assert nuevo_texto.count(viejo) == 1, (f, a)
                    nuevo_texto = nuevo_texto.replace(viejo, m)
                    print(f"{Path(f).name}: {a} {viejo[:8]} -> {m[:8]}")
                hechos.add(a)
        if nuevo_texto != texto:
            Path(f).write_text(nuevo_texto, encoding="utf-8", newline="")
    for a in archivos:
        if a not in hechos:
            print(f"sin sticker: {a}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
