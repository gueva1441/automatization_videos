"""F38e §C.1 · el PANTALLA_SYSTEM de m01e-6 sale del md por código, no reescrito.

Extrae el bloque «Prompt nuevo (m01e-6-prueba), entero» de lab/hyperframes/f38/PRUEBA1_prompt_rotulos.md (igual que
prueba1_rotulos.system_del_md: lo que hay entre la ``` que sigue al título y la ``` siguiente) y lo escribe dentro de
script_engine/m01e_pantalla.py reemplazando el contenido del string triple de PANTALLA_SYSTEM. El .py es CRLF: se edita
en bytes, cada \\n del bloque pasa a \\r\\n al escribirlo (Python lo lee de vuelta como \\n), y el resto del archivo no
se toca. Al final importa el módulo y verifica md5(PANTALLA_SYSTEM) == 7d2ccdd28055d6e621d1d251a0fe8bb7.

    python lab/hyperframes/f38e/c/c1_prompt_del_md.py          # escribe y verifica
    python lab/hyperframes/f38e/c/c1_prompt_del_md.py --seco   # solo muestra lo que haría
"""
from __future__ import annotations

import hashlib
import importlib
import sys
from pathlib import Path

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(ROOT))
PROMPT_MD = ROOT / "lab" / "hyperframes" / "f38" / "PRUEBA1_prompt_rotulos.md"
PY = ROOT / "script_engine" / "m01e_pantalla.py"
MD5_ESPERADO = "7d2ccdd28055d6e621d1d251a0fe8bb7"     # F38e §C.1: el que se midió en F38e-0
MD5_MD = "240e3e7bf13656cb62f68b598393f41f"           # PRUEBA1_prompt_rotulos.md (F38e-0 paso 0)
ABRE = b'PANTALLA_SYSTEM = """'
CIERRA = b'"""'


def system_del_md() -> str:
    """Copia de prueba1_rotulos.system_del_md (líneas 10–25 del md, 3098 caracteres)."""
    md = PROMPT_MD.read_text(encoding="utf-8")
    h = "## Prompt nuevo (m01e-6-prueba), entero\n"
    i = md.index(h) + len(h)
    a = md.index("```\n", i) + len("```\n")
    b = md.index("\n```", a)
    return md[a:b]


def main(argv: list[str]) -> int:
    seco = "--seco" in argv
    md_md5 = hashlib.md5(PROMPT_MD.read_bytes()).hexdigest()
    print(f"PRUEBA1_prompt_rotulos.md md5 {md_md5} ({'OK' if md_md5 == MD5_MD else 'DISTINTO del de F38e-0'})")
    system = system_del_md()
    s_md5 = hashlib.md5(system.encode("utf-8")).hexdigest()
    print(f"bloque del md: {len(system)} caracteres · md5 {s_md5} · {'OK' if s_md5 == MD5_ESPERADO else 'NO COINCIDE'}")
    if s_md5 != MD5_ESPERADO:
        print("PARADA: el bloque extraído no da el md5 medido")
        return 2
    if '"""' in system or "\\" in system:
        print("PARADA: el bloque trae comillas triples o barras: no entra tal cual en un string triple")
        return 2
    raw = PY.read_bytes()
    assert raw.count(b"\r\n") > 0 and b"\n" not in raw.replace(b"\r\n", b""), "m01e_pantalla.py no es CRLF puro"
    i = raw.index(ABRE) + len(ABRE)
    j = raw.index(CIERRA, i)
    viejo = raw[i:j]
    nuevo = system.encode("utf-8").replace(b"\n", b"\r\n")
    print(f"string viejo: {len(viejo)} bytes · nuevo: {len(nuevo)} bytes · posición {i}")
    if seco:
        return 0
    PY.write_bytes(raw[:i] + nuevo + raw[j:])
    raw2 = PY.read_bytes()
    assert b"\n" not in raw2.replace(b"\r\n", b""), "quedó un LF suelto"
    import script_engine.m01e_pantalla as m01e
    importlib.reload(m01e)
    got = hashlib.md5(m01e.PANTALLA_SYSTEM.encode("utf-8")).hexdigest()
    print(f"md5(m01e_pantalla.PANTALLA_SYSTEM) = {got} · {'OK' if got == MD5_ESPERADO else 'NO COINCIDE'}")
    print(f"PANTALLA_SYSTEM == bloque del md: {m01e.PANTALLA_SYSTEM == system}")
    return 0 if got == MD5_ESPERADO else 3


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
