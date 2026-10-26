"""F34 §A: la salida en texto de cada punto, sobre los datos reales de Vajont (sin API). → salida_a.txt"""
from __future__ import annotations

import hashlib
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(ROOT))
from config import DATA_DIR  # noqa: E402
from script_engine import evidence as ev  # noqa: E402
from script_engine import gfx_rotulista as gro  # noqa: E402
from script_engine.gfx_realizador import ya_dicho  # noqa: E402

d = DATA_DIR / "scripts" / "_steps" / "f8s3-vajont"
esc = json.loads((d / "01a_escaleta.json").read_text(encoding="utf-8"))
pool = json.loads((d / "00_pool_v3.json").read_text(encoding="utf-8"))
caps = json.loads((d / "01b_narracion_v3.json").read_text(encoding="utf-8"))["caps"]
L: list[str] = []
p = L.append

p("# F34 §A — salida en texto (datos reales de Vajont, sin API)\n")
p("## A.1 prompt del rotulista")
p(f"- versión {gro.PROMPT_VERSION} · md5 nuevo (SYSTEM + USER) `{gro.prompt_md5()}`")
f32 = hashlib.md5((gro.ROTULISTA_SYSTEM_F32 + "\n\n" + gro.ROTULISTA_USER_F32).encode("utf-8")).hexdigest()
p(f"- deshechos los tres reemplazos da el de F32 byte a byte: `{f32}` (F32: c9231e24…)")
for k, (v, n) in enumerate(gro.A1_SYSTEM, 1):
    p(f"- reemplazo {k} (SYSTEM):\n  - antes: «{v}»\n  - ahora: «{n}»")
for v, n in gro.A1_USER:
    p(f"- reemplazo 3 (formato de salida del USER):\n  - antes: «{v}»\n  - ahora: «{n}»")
voz = []
for c in sorted(caps, key=lambda c: c["chapter_number"]):
    voz += [s for s in re.split(r"(?<=[.!?…])\s+", c["narration"].strip()) if s.strip()]
beats1 = [{"n": 1, "funcion": "gancho", "t0": 0, "t1": 1, "cierre": "", "dato_central": "", "datos_apoyo": []}]
g = gro.items_gancho(beats1, pool, set(), voz)
nd = [x for x in g if not x["dice_voz"]]
p(f"- gancho (ch01): el pedido trae {len(g)} ítems del pool del video; la voz dice {len(g) - len(nd)} → quedan "
  f"{len(nd)} candidatos («la narración lo dice en el video: no»)")
it = ev.items(pool)
gi = {x["id"]: x for x in g}
for i in ("D118", "D128", "D117", "D49"):
    p(f"  - {i} «{ev.text_of(it[i])}» → la voz lo dice: {'sí' if gi[i]['dice_voz'] else 'no'}")

p("\n## A.2 filtros (los casos reales; tests en test_module_f34.py)")
p("- candado: el número/año/nombre que dice la oración ancla cuenta (D117 «1943»: test_a2_1)")
p("- no dicho: corre antes que la lectura; «cuatrocientos» = 400 por valor (D237: test_a2_2; el conversor ya estaba, la "
  "falla era el orden)")
p("- spoiler: un nombre dicho antes en el cap o en un cap anterior no es spoiler (T85 «Vajont»: test_a2_3)")
p(f"  - «Vajont» en la voz de ch01–ch06: {'sí' if gro._palabra_en('Vajont', ' '.join(c['narration'] for c in caps if c['chapter_number'] < 7)) else 'no'}")

p("\n## A.3.3 fechas completas que dice la voz (reloj desde la voz si la cronología no da reloj)")
for c in sorted(caps, key=lambda c: c["chapter_number"]):
    for s in re.split(r"(?<=[.!?…])\s+", c["narration"].strip()):
        for f in gro.fechas_completas(s):
            p(f"- ch{c['chapter_number']:02d}: {f[0]} {f[1]} {f[2]} · «{s.strip()[:90]}»")

p("\n## A.4 sellos de clima: el prompt literal (con {lista} del perfil)")
p("```\n" + gro.prompt_clima(gro.vocabulario_clima(), "{voz_-1}", "{voz_ancla}", "{voz_+1}", "{funcion}") + "\n```")

p("\n## A.5 agua desde la voz: oraciones candidatas por cap (y la elegida, una por cap)")
for c in sorted(caps, key=lambda c: c["chapter_number"]):
    ss = [s for s in re.split(r"(?<=[.!?…])\s+", c["narration"].strip()) if s.strip()]
    hall = [(gro.AGUA_ETIQUETAS.index(g[0]), k, g) for k, s in enumerate(ss) if (g := gro._agua_de(s, ss[k - 1] if k else ""))]
    for _, k, g in hall:
        p(f"- ch{c['chapter_number']:02d} oración [{k}]: {g[0]} · {g[2]} m · «{ss[k][:90]}»")
    if hall:
        _, k, g = min(hall)
        p(f"  → ch{c['chapter_number']:02d} elige [{k}] {g[0]} · {g[2]} m (antes de la regla de una animación por beat)")

p("\n## A.6 tarjeta fecha-hora")
p(f"- {json.dumps(gro.tarjeta_inicial(esc, pool), ensure_ascii=False)}")

out = Path(__file__).with_name("salida_a.txt")
out.write_text("\n".join(L) + "\n", encoding="utf-8")
print(out)
