"""F40 §C.1–C.2 (sin modelo): voz de Kyshtym sin voseo («cenás» → «cenas», «acá» → «aquí») en los archivos de Fase 1
que llevan la narración, y los 7 títulos de cap de DECISIONES 18:30 en los que llevan los títulos; respaldo _pre_f40 de
cada uno. Los 01e_pantalla.* no se tocan acá: se regeneran en C.3 (respaldo 01e_pantalla_f39.*)."""
import hashlib
import json
import re
import shutil
from pathlib import Path

D = Path("data/scripts/_steps/f39-kyshtym")
VIEJOS = ["Un misterio ardiente", "Un proyecto oculto", "Temperatura descontrolada", "El golpe seco",
          "La verdad oculta", "Verdades contradictorias", "El largo silencio"]
NUEVOS = ["La luz que no era fuego", "La ciudad sin mapa", "El tanque catorce", "Un domingo de fútbol",
          "La aurora de Cheliábinsk", "Los pueblos enterrados", "Lo que calló el acta"]   # DECISIONES 18:30
ACA = re.compile(r"(?<![\wÁÉÍÓÚáéíóúñÑ])([aA])cá(?![\wáéíóúñ])")
VOZ = ["01b_narracion_v3.json", "01b_narration.json", "01b_guionista_v4.json"]
TIT = ["01a_skeleton.json"]


def md5(p: Path) -> str:
    return hashlib.md5(p.read_bytes()).hexdigest()


def main() -> None:
    print("C.1 voz sin voseo · C.2 títulos (DECISIONES 18:30) · f39-kyshtym")
    for nombre in VOZ + TIT:
        p = D / nombre
        t = p.read_text(encoding="utf-8")
        antes = md5(p)
        bak = D / (p.stem + "_pre_f40" + p.suffix)
        assert not bak.exists(), f"ya existe {bak}: no se pisa"
        shutil.copy2(p, bak)
        if nombre in VOZ:
            n1 = t.count("cenás")
            t = t.replace("cenás", "cenas")
            t, n2 = ACA.subn(lambda m: m.group(1) + "quí", t)
            det = f"cenás→cenas ×{n1} · acá→aquí ×{n2}"
        else:
            partes = []
            for v, n in zip(VIEJOS, NUEVOS):
                partes.append(f"«{v}»→«{n}» ×{t.count(v)}")
                t = t.replace(v, n)
            det = " · ".join(partes)
        json.loads(t)
        p.write_text(t, encoding="utf-8")
        print(f"- {nombre}: {det} · md5 {antes[:8]}… → {md5(p)[:8]}… · respaldo {bak.name}")
    print("grep final:")
    for nombre in VOZ + TIT:
        t = (D / nombre).read_text(encoding="utf-8")
        viejos = sum(t.count(v) for v in VIEJOS)
        print(f"  {nombre}: cenás {t.count('cenás')} · acá {len(ACA.findall(t))} · títulos viejos {viejos}")
    sk = json.loads((D / "01a_skeleton.json").read_text(encoding="utf-8"))
    print("títulos:", [c.get("title") for c in sk.get("chapters") or []])
    otros = [f.name for f in D.iterdir() if f.is_file() and f.suffix in (".json", ".md")
             and "_pre_f40" not in f.name and f.name not in VOZ + TIT
             and ("cenás" in f.read_text(encoding="utf-8", errors="ignore")
                  or ACA.search(f.read_text(encoding="utf-8", errors="ignore"))
                  or any(v in f.read_text(encoding="utf-8", errors="ignore") for v in VIEJOS))]
    print("otros archivos del topic que todavía los tienen (no llevan la narración ni los títulos, o se regeneran):",
          otros)


if __name__ == "__main__":
    main()
