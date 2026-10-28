"""F40b §1 (datos, sin código): quita las iniciales antes de un apellido en la narración de Kyshtym.
Regex del pedido: una o más «Letra mayúscula + punto + espacio» seguidas de una palabra con mayúscula.
Uso: `python lab/hyperframes/f40/f40b/iniciales.py listar` (solo lista cada coincidencia con su oración) y
`python lab/hyperframes/f40/f40b/iniciales.py aplicar` (respaldo _pre_f40b, reemplazo, grep y md5)."""
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

D = Path("data/scripts/_steps/f39-kyshtym")
ARCHIVOS = ["01b_narracion_v3.json", "01b_narration.json", "01b_guionista_v4.json"]
MAY = "A-ZÁÉÍÓÚÑÜ"
INI = re.compile(rf"(?<![\w.])((?:[{MAY}]\. )+)(?=[{MAY}][\wáéíóúñü]+)")
ACA = re.compile(r"(?<![\wÁÉÍÓÚáéíóúñÑ])[aA]cá(?![\wáéíóúñ])")


def md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def oracion(t: str, i: int) -> str:
    a = max(t.rfind(". ", 0, max(i - 3, 0)), t.rfind("\"", 0, i), t.rfind("\\n", 0, i))
    b_cands = [x for x in (t.find(". ", i + 40), t.find("\"", i)) if x != -1]
    b = min(b_cands) if b_cands else len(t)
    return t[a + 1:b + 1].strip(" \"")


def listar() -> None:
    for nombre in ARCHIVOS:
        t = (D / nombre).read_text(encoding="utf-8")
        ms = list(INI.finditer(t))
        print(f"== {nombre}: {len(ms)} coincidencia(s)")
        for m in ms:
            sig = re.match(r"\S+", t[m.end():]).group(0)
            print(f"  «{m.group(1)}{sig}» → «{sig}» · en: …{oracion(t, m.start())}…")


def aplicar() -> None:
    for nombre in ARCHIVOS:
        p = D / nombre
        bak = D / (p.stem + "_pre_f40b" + p.suffix)
        assert not bak.exists(), f"ya existe {bak}: no se pisa"
        antes = md5(p)
        shutil.copy2(p, bak)
        t = p.read_text(encoding="utf-8")
        t2, n = INI.subn("", t)
        json.loads(t2)
        p.write_text(t2, encoding="utf-8")
        print(f"- {nombre}: {n} reemplazo(s) · md5 {antes} → {md5(p)} · respaldo {bak.name}")
    print("grep final:")
    for nombre in ARCHIVOS:
        t = (D / nombre).read_text(encoding="utf-8")
        print(f"  {nombre}: iniciales {len(INI.findall(t))} · cenás {t.count('cenás')} · acá {len(ACA.findall(t))}")


if __name__ == "__main__":
    {"listar": listar, "aplicar": aplicar}[sys.argv[1]]()
