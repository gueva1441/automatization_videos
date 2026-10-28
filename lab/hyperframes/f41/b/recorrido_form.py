"""F41 B.8 — recorrido EN SECO del form con stubs (sin subprocess reales, sin API, US$ 0).

Corre `run_pipeline.main()` en proceso con QA_FORM prendido, las fases falsas de test_run_pipeline.FakePipeline
(cada comando deja su artefacto en un directorio temporal, nunca en data/ ni output/) e `input` falso con las
respuestas del form. La salida de run_pipeline se lee como la lee qa_studio_server (_form_reader): header de fase →
fase del form; @@QAFORM@@ → marcador. fase1 es un stub: los marcadores propios de fase1 (reuse_seeds, seed_pick,
video_type…) salen de su subprocess y acá no aparecen.

    PYTHONIOENCODING=utf-8 python lab/hyperframes/f41/b/recorrido_form.py
"""
from __future__ import annotations

import builtins
import contextlib
import io
import json
import shutil
import sys
import tempfile
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(RAIZ))

import qa_form_markers  # noqa: E402
import qa_studio_server as qa  # noqa: E402
import run_pipeline as rp  # noqa: E402
from test_run_pipeline import TID, FakePipeline  # noqa: E402


class _Parches:
    def __init__(self):
        self._orig: list[tuple[object, str, object]] = []

    def __call__(self, obj, nombre, valor):
        self._orig.append((obj, nombre, getattr(obj, nombre)))
        setattr(obj, nombre, valor)

    def restaurar(self):
        for obj, nombre, valor in reversed(self._orig):
            setattr(obj, nombre, valor)


def correr(argv: list[str], respuestas: list[str], fake: FakePipeline, titulo: str) -> None:
    print(f"\n### {titulo}\n")
    print(f"argv: `{' '.join(argv)}` · respuestas del form por stdin: {respuestas or '(ninguna)'}\n")
    cola = list(respuestas)
    eventos: list[str] = []
    buf = io.StringIO()
    n0 = len(fake.calls)

    def fake_input(prompt=""):
        if not cola:
            raise EOFError
        r = cola.pop(0)
        eventos.append(f"    form → stdin: {r!r}")
        return r

    p = _Parches()
    p(builtins, "input", fake_input)
    p(sys, "argv", argv)
    p(rp, "QA_FORM", True)
    p(qa_form_markers, "QA_FORM", True)
    orig_run = fake.run

    def run_y_registra(cmd):
        eventos.append(f"    subprocess (stub): {rp._shell(cmd)}")
        return orig_run(cmd)
    p(rp, "_run", run_y_registra)

    class _Tee(io.TextIOBase):
        """Lo que imprime run_pipeline, línea por línea, como lo lee el server."""
        def __init__(self):
            self._pend = ""

        def write(self, s):
            buf.write(s)
            self._pend += s
            while "\n" in self._pend:
                linea, self._pend = self._pend.split("\n", 1)
                leer_linea(linea)
            return len(s)

    def leer_linea(linea: str) -> None:
        if linea.startswith(qa._FORM_MARKER):
            m = json.loads(linea[len(qa._FORM_MARKER):])
            body = m.get("body") or ""
            eventos.append(f"  MARCADOR {m['menu']} · botones {[o['key'] for o in m['options']]} · "
                           f"documento {len(body)} caracteres (1.ª línea: {body.splitlines()[0] if body else '—'!r})")
        elif "  ▶ " in linea:
            fase = next((ph for ph in qa._FORM_PHASES if ph in linea), None)
            eventos.append(f"  FASE {fase}   ← «{linea.strip()}»")
        elif "Frenó en" in linea or "Próximo" in linea or linea.strip().startswith(("leer:", "aprobar:", "retomar:",
                                                                                   "editar:", "python ")):
            eventos.append(f"    reporte: {linea.strip()}")
        elif "LISTO PARA PACKAGING" in linea or "Cadena completa" in linea:
            eventos.append(f"    reporte: {linea.strip()}")

    try:
        with contextlib.redirect_stdout(_Tee()):
            rc = rp.main()
    finally:
        p.restaurar()
    print("```")
    print("\n".join(eventos))
    print(f"  exit code de run_pipeline: {rc}")
    print("```")
    print(f"\nComandos corridos (stub) en esta corrida: {fake.etiquetas()[len(fake.etiquetas()) - (len(fake.calls) - n0):]}")


def main() -> int:
    raiz_tmp = Path(tempfile.mkdtemp(prefix="f41b_recorrido_"))
    try:
        # 1) research → fase3 con A en las dos compuertas (lo que lanza /form_launch: qa._form_command())
        f1 = FakePipeline(raiz_tmp / "uno")
        p = _Parches()
        f1.install(p)
        try:
            correr(qa._form_command()[1:], ["A", "C", "A"], f1,
                   "Recorrido 1 — research → fase3, A en el papel, C en el visor, A en el guion de pantalla")
        finally:
            p.restaurar()

        # 2) P en el papel y después «retomar» (lo que lanza /form_resume: qa._form_resume_command(tid))
        f2 = FakePipeline(raiz_tmp / "dos")
        p = _Parches()
        f2.install(p)
        try:
            correr(qa._form_command()[1:], ["P"], f2, "Recorrido 2a — research → P en la compuerta del papel")
            print(f"\netapa_de({TID}) después de la P: {rp.etapa_de(TID)}")
            correr(qa._form_resume_command(TID)[1:], ["A", "C", "A"], f2,
                   "Recorrido 2b — «Retomar» (/form_resume) → A en el papel, C en el visor, A en el guion")
            print(f"\netapa_de({TID}) al final: {rp.etapa_de(TID)}")
            print(f"\n¿Se corrió dos veces alguna fase? {len(f2.calls) != len(set(map(tuple, f2.calls)))}")
        finally:
            p.restaurar()
    finally:
        shutil.rmtree(raiz_tmp, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
