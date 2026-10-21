"""F4e: tabla de bloques con el veredicto del crítico visual (ch02, ch05) desde los planes resueltos.
Uso: PYTHONIOENCODING=utf-8 python lab/hyperframes/f4e/tabla_critico.py > lab/hyperframes/f4e/TABLA_critico.md
"""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
W = ROOT / "output" / "ba6c3cac-a091-41c0-8dad-afd2f4364747" / "_fase2b_work"
OUT = Path(__file__).resolve().parent
LABEL = {"sello": "sello", "icono": "ícono", "recorte": "recorte", "dato": "dato", "contador": "contador",
         "nivel_agua": "nivel de agua", "zoom": "zoom"}


def _t(x: float) -> str:
    return f"{int(x // 60)}:{x % 60:04.1f}"


def main() -> None:
    print("# F4e — Bloques con veredicto del crítico visual (ch02, ch05)\n")
    print("Cada bloque del plan resuelto (después de las reglas duras) contra el cuadro real de la foto + la voz. "
          "Solo pasan los «suma». Antes = F4d (`_bak_f4e_pre`).\n")
    for cap in ("ch02", "ch05"):
        plan = json.loads((W / f"gfx_plan_{cap}.resolved.json").read_text(encoding="utf-8"))["plan"]
        rows = plan.get("critico") or []
        n = sum(r["pasa"] for r in rows)
        pk = plan.get("pico") or {}
        print(f"## {cap} — pasan {n} de {len(rows)}\n")
        print(f"Pico: «{pk.get('palabra') or pk.get('word')}» → {pk.get('block')}"
              + (" (el bloque del pico no pasó el crítico)" if pk.get("block_quitado_por_critico") else "") + "\n")
        print("| t | bloque | texto | voz en ese instante | veredicto | motivo |\n|---|---|---|---|---|---|")
        for r in rows:
            voz = (r.get("voz") or "").replace("|", "/")
            voz = voz if len(voz) <= 90 else voz[:87] + "…"
            print(f"| {_t(r['t'])} | {LABEL[r['bloque']]} | {r['texto']} | {voz} | **{r['veredicto']}** | {r['motivo']} |")
        print()
        sheet = W / f"hoja_contactos_{cap}.jpg"
        if sheet.exists():
            shutil.copy2(sheet, OUT / sheet.name)
            print(f"Hoja de contactos: `{sheet.name}`\n")


if __name__ == "__main__":
    main()
