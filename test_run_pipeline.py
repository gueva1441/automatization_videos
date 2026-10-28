"""
test_run_pipeline.py — Tests SIN red del orquestador (chat 57; F41: una sola cadena, compuertas y retomar).

Ningún subprocess real: `FakePipeline.run` reemplaza a `run_pipeline._run`, registra cada comando y deja en disco
(tmp_path) el mismo artefacto que deja la fase real, en las rutas de run_pipeline. DATA_DIR / OUTPUT_DIR /
RESEARCH_SENTINEL apuntan a tmp_path; el estado del papel, el del guion de pantalla, `packaged` y la fecha son
stubs. `input` es falso (lista de respuestas; agotada = stdin cerrado). QA_FORM se prende y apaga en los dos
módulos (run_pipeline y qa_form_markers).

    python -m pytest -q test_run_pipeline.py
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

import pytest

import qa_form_markers
import run_pipeline as rp

TID = "top_f41"
HOY = "2026-10-27"
MARKER = "@@QAFORM@@ "

# Lo que corre cada etapa, en orden (etiquetas de FakePipeline.etiqueta). PRODUCTOR[i] deja lo que hace pasar de
# ETAPAS[i] a ETAPAS[i + 1].
PRODUCTOR = ["guion", "aprobar-papel", "voz", "assets", "fondos", "plan-only", "aprobar-guion", "render", "fase3"]


class FakePipeline:
    """Fases falsas de la cadena de F41 (sin subprocess): cada comando deja lo que deja la fase real."""

    def __init__(self, tmp: Path, tid: str = TID, *, rc: dict | None = None, sin_artefacto: set | None = None):
        self.tmp = Path(tmp)
        self.tid = tid
        self.rc = rc or {}                     # {etiqueta: returncode}
        self.sin = sin_artefacto or set()      # etiquetas que salen con 0 pero no dejan su artefacto
        self.calls: list[list[str]] = []
        self.papel_ok = False
        self.guion_ok = False
        self.packaged = False
        self.video_hecho = False               # status video_generated en topics_db

    def install(self, setattr_):
        """`setattr_(obj, nombre, valor)`: monkeypatch.setattr en los tests; un setter con restore en el lab."""
        setattr_(rp, "DATA_DIR", self.tmp / "data")
        setattr_(rp, "OUTPUT_DIR", self.tmp / "output")
        setattr_(rp, "RESEARCH_SENTINEL", self.tmp / "data" / "_last_research.json")
        setattr_(rp, "_run", self.run)
        setattr_(rp, "_chequeo_dependencias", lambda: None)   # F42b: el chequeo de librerías tiene sus propios tests
        setattr_(rp, "_estado_papel",
                 lambda t: (True, "papel aprobado por Omar (stub)") if self.papel_ok
                 else (False, "el papel no está aprobado"))
        setattr_(rp, "_estado_guion",
                 lambda t: (True, "guion aprobado por Omar (stub)") if self.guion_ok
                 else (False, f"el guion de {t} no está aprobado"))
        setattr_(rp, "_packaged", lambda t: self.packaged)
        setattr_(rp, "_video_hecho", lambda t: self.video_hecho)
        setattr_(rp, "_hoy", lambda: HOY)
        return self

    @staticmethod
    def etiqueta(cmd: list[str]) -> str:
        s = cmd[0]
        if s == "fase1_5.py":
            if "--aprobar-papel" in cmd:
                return "aprobar-papel"
            return "voz" if "--from" in cmd else "guion"
        if s == "fase2b.py":
            if "--plan-only" in cmd:
                return "plan-only"
            if "--aprobar-guion" in cmd:
                return "aprobar-guion"
            return "render" if "--gfx" in cmd else "fondos"
        return {"fase1.py": "research", "fase2a.py": "assets", "fase3.py": "fase3"}.get(s, s)

    @staticmethod
    def _w(p: Path, txt: str = "{}") -> None:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(txt, encoding="utf-8")

    def producir(self, et: str) -> None:
        t = self.tid
        if et == "research":
            self._w(rp.RESEARCH_SENTINEL, json.dumps({"tids": [t]}))
        elif et == "guion":
            self._w(rp._papel_md_path(t), f"# Papel de {t}\n\nch01 · beat 1 · ficha: nada\nch01 · beat 2 · sello\n")
        elif et == "aprobar-papel":
            self.papel_ok = True
        elif et == "voz":
            self._w(rp._script_path(t))
        elif et == "assets":
            self._w(rp._manifest_path(t))
        elif et == "fondos":
            self._w(rp._fondos_path(t), "")
        elif et == "plan-only":
            self._w(rp._guion_pantalla_path(t))
            self._w(rp._guion_pantalla_path(t, "md"), f"# GUION DE PANTALLA — {t}\n\n| cap | beat | ficha |\n|---|---|---|\n")
            self.guion_ok = False
        elif et == "aprobar-guion":
            self.guion_ok = True
        elif et == "render":
            self._w(rp._render_path(t), "")
        elif et == "fase3":
            self.packaged = True

    def run(self, cmd: list[str]) -> int:
        cmd = list(cmd)
        self.calls.append(cmd)
        et = self.etiqueta(cmd)
        rc = self.rc.get(et, 0)
        if rc == 0 and et not in self.sin:
            self.producir(et)
        return rc

    def hasta(self, etapa: str) -> "FakePipeline":
        """Deja el disco como si el topic estuviera en `etapa` (sin registrar comandos)."""
        for et in PRODUCTOR[:rp.ETAPAS.index(etapa)]:
            self.producir(et)
        return self

    def etiquetas(self) -> list[str]:
        return [self.etiqueta(c) for c in self.calls]


def markers(out: str) -> list[dict]:
    return [json.loads(l[len(MARKER):]) for l in out.splitlines() if l.startswith(MARKER)]


@pytest.fixture
def fake(tmp_path, monkeypatch):
    return FakePipeline(tmp_path).install(monkeypatch.setattr)


@pytest.fixture
def form(monkeypatch):
    def _set(on: bool) -> None:
        monkeypatch.setattr(rp, "QA_FORM", on)
        monkeypatch.setattr(qa_form_markers, "QA_FORM", on)
    _set(False)
    return _set


@pytest.fixture
def respuestas(monkeypatch):
    """respuestas([...]): input() devuelve esas líneas en orden; agotadas → EOFError (stdin cerrado)."""
    pedidas: list[str] = []

    def _set(lineas):
        cola = list(lineas)

        def fake_input(prompt=""):
            if not cola:
                raise EOFError
            pedidas.append(cola[0])
            return cola.pop(0)
        monkeypatch.setattr("builtins.input", fake_input)
        return pedidas
    return _set


# ═══════════════════════ tests existentes, ajustados a la secuencia de F41 ═══════════════════════

def test_order_and_tid(fake, form, respuestas, capsys):
    """Cadena entera con el form y A en las dos compuertas: el orden nuevo y el tid en cada comando."""
    form(True)
    respuestas(["A", "C", "A"])            # papel · visor · guion de pantalla
    rc = rp.sequence(TID, batch=False)
    assert rc == 0
    assert fake.etiquetas() == PRODUCTOR
    assert all(TID in c for c in fake.calls)
    assert fake.calls[0] == ["fase1_5.py", "--topic", TID, "--batch"]
    assert [m["menu"] for m in markers(capsys.readouterr().out)] == ["papel_gate", "visor_gate", "guion_gate"]


def test_stop_on_nonzero(fake, form):
    """exit≠0 en fase2a → frena, no llama fase2b/fase3."""
    fake.rc = {"assets": 2}
    fake.hasta("voz")
    rc = rp.sequence(TID)
    assert rc == 1
    assert fake.etiquetas() == ["voz", "assets"]


def test_stop_missing_script(fake, form, capsys):
    """fase1_5 --from normalizer_gate sale 0 pero sin data/scripts/<id>.json → frena en VOZ."""
    fake.sin = {"voz"}
    fake.hasta("voz")
    rc = rp.sequence(TID)
    out = capsys.readouterr().out
    assert rc == 1
    assert fake.etiquetas() == ["voz"]
    assert "Frenó en: VOZ" in out and "sin dejar su artefacto" in out


def test_assisted_calls_fase3(fake, form):
    """Sin --batch, PACKAGING corre fase3 con el tid posicional."""
    fake.hasta("packaging")
    assert rp.sequence(TID, batch=False) == 0
    assert fake.calls == [["fase3.py", TID]]


def test_batch_skips_fase3(fake, form, capsys):
    """--batch → no llama fase3, reporta el comando."""
    fake.hasta("packaging")
    assert rp.sequence(TID, batch=True) == 0
    assert fake.calls == []
    assert f"python fase3.py {TID}" in capsys.readouterr().out


def test_research_runs_fase1_then_sequences(fake, form, monkeypatch, capsys):
    """--research → fase1.py --no-chain primero, después la secuencia con el tid del sentinel (para en el papel)."""
    monkeypatch.setattr(sys, "argv", ["run_pipeline.py", "--research", "--video-type", "long", "--batch"])
    rc = rp.main()
    assert fake.calls[0][:2] == ["fase1.py", "--no-chain"]
    assert fake.etiquetas() == ["research", "guion"]
    assert fake.calls[1] == ["fase1_5.py", "--topic", TID, "--batch"]
    assert rc == 0
    assert "Frenó en: PAPEL" in capsys.readouterr().out


def test_research_fase1_fails_no_sequence(fake, form, monkeypatch):
    """--research con fase1 exit≠0 → no secuencia y propaga el exit."""
    fake.rc = {"research": 1}
    monkeypatch.setattr(sys, "argv", ["run_pipeline.py", "--research"])
    assert rp.main() == 1
    assert fake.etiquetas() == ["research"]


# ═══════════════════════ B.1–B.2: GUION y la compuerta del papel ═══════════════════════

def test_papel_terminal_para_con_comando(fake, form, respuestas, capsys):
    """Sin QA_FORM: GUION corre, el papel no se aprueba solo; para e imprime aprobar + retomar, sin preguntar."""
    pedidas = respuestas([])
    rc = rp.sequence(TID)
    out = capsys.readouterr().out
    assert rc == 0
    assert fake.etiquetas() == ["guion"]
    assert not fake.papel_ok and pedidas == []
    assert markers(out) == []
    assert f'python fase1_5.py --topic {TID} --aprobar-papel "Omar <fecha>"' in out
    assert f"python run_pipeline.py --topic {TID}" in out


def test_papel_form_A_aprueba_y_sigue_from_normalizer_gate(fake, form, respuestas, capsys):
    """Con el form y A: muestra el papel ENTERO, --aprobar-papel "Omar <hoy>" y después --from normalizer_gate."""
    form(True)
    respuestas(["A"])
    fake.hasta("papel")
    fake.rc = {"assets": 1}                  # corta después de la voz
    rp.sequence(TID)
    out = capsys.readouterr().out
    assert fake.calls[:2] == [["fase1_5.py", "--topic", TID, "--aprobar-papel", f"Omar {HOY}"],
                              ["fase1_5.py", "--topic", TID, "--from", "normalizer_gate", "--batch"]]
    m = markers(out)[0]
    assert m["menu"] == "papel_gate" and [o["key"] for o in m["options"]] == ["A", "P"]
    assert m["body"] == rp._papel_md_path(TID).read_text(encoding="utf-8")
    assert m["payload"]["topic_id"] == TID


def test_papel_form_P_para_con_retomar(fake, form, respuestas, capsys):
    """Con el form y P: no aprueba nada, para (exit 0) con el comando de retomar."""
    form(True)
    respuestas(["P"])
    fake.hasta("papel")
    assert rp.sequence(TID) == 0
    out = capsys.readouterr().out
    assert fake.calls == [] and not fake.papel_ok
    assert f"retomar: python run_pipeline.py --topic {TID}" in out


@pytest.mark.parametrize("lineas", [[], [""], ["S"], ["aprobar"]])
def test_papel_nunca_se_aprueba_solo(fake, form, respuestas, lineas):
    """Con el form, cualquier cosa que no sea A (o stdin cerrado) es P."""
    form(True)
    respuestas(lineas)
    fake.hasta("papel")
    assert rp.sequence(TID) == 0
    assert fake.calls == [] and not fake.papel_ok


def test_guion_parada_de_fase1_5(fake, form, capsys):
    """fase1_5 --batch con exit 2 (otra PARADA) → frena en GUION con el comando."""
    fake.rc = {"guion": 2}
    assert rp.sequence(TID) == 1
    out = capsys.readouterr().out
    assert "PARADA de fase1_5" in out and f"python fase1_5.py --topic {TID} --batch" in out


# ═══════════════════════ B.3–B.5: VISOR, FONDOS y el guion de pantalla ═══════════════════════

def test_fondos_y_plan_only(fake, form, capsys):
    """Sin form: FONDOS = fase2b sin gfx; después --plan-only; la compuerta del guion para."""
    fake.hasta("fondos")
    assert rp.sequence(TID) == 0
    assert fake.calls == [["fase2b.py", TID], ["fase2b.py", TID, "--plan-only"]]
    assert "Frenó en: GUION DE PANTALLA" in capsys.readouterr().out


def test_visor_gate_antes_de_fondos(fake, form, respuestas, capsys):
    """Con el form, el VISOR (sin cambio) frena antes de cocer los fondos."""
    form(True)
    pedidas = respuestas(["C", "P"])
    fake.hasta("fondos")
    rp.sequence(TID)
    assert pedidas == ["C", "P"]
    assert [m["menu"] for m in markers(capsys.readouterr().out)] == ["visor_gate", "guion_gate"]
    assert fake.etiquetas() == ["fondos", "plan-only"]


def test_guion_form_A_aprueba_y_renderiza(fake, form, respuestas, capsys):
    """Con el form y A: muestra GUION_PANTALLA.md entero, --aprobar-guion, render con gfx y fase3."""
    form(True)
    respuestas(["A"])
    fake.hasta("aprobar_guion")
    assert rp.sequence(TID, batch=False) == 0
    assert fake.calls == [["fase2b.py", TID, "--aprobar-guion", f"Omar {HOY}"],
                          ["fase2b.py", TID, "--reuse-visuals", "--keep-segments", "--gfx", "--gfx-sparse"],
                          ["fase3.py", TID]]
    m = markers(capsys.readouterr().out)[0]
    assert m["menu"] == "guion_gate"
    assert m["body"] == rp._guion_pantalla_path(TID, "md").read_text(encoding="utf-8")


def test_guion_form_A_batch_reporta_fase3(fake, form, respuestas, capsys):
    form(True)
    respuestas(["A"])
    fake.hasta("aprobar_guion")
    assert rp.sequence(TID, batch=True) == 0
    assert fake.etiquetas() == ["aprobar-guion", "render"]
    assert f"LISTO PARA PACKAGING → python fase3.py {TID}" in capsys.readouterr().out


def test_guion_form_P_para(fake, form, respuestas, capsys):
    """Con el form y P (el camino normal: el analista revisa y edita): para con plan-edit, aprobar y retomar."""
    form(True)
    respuestas(["P"])
    fake.hasta("aprobar_guion")
    assert rp.sequence(TID) == 0
    out = capsys.readouterr().out
    assert fake.calls == [] and not fake.guion_ok
    assert f"python fase2b.py {TID} --plan-edit" in out
    assert f'python fase2b.py {TID} --aprobar-guion "Omar <fecha>"' in out
    assert f"retomar: python run_pipeline.py --topic {TID}" in out


def test_guion_terminal_para(fake, form, respuestas):
    """Sin QA_FORM la compuerta del guion para siempre, sin preguntar."""
    pedidas = respuestas(["A"])
    fake.hasta("aprobar_guion")
    assert rp.sequence(TID) == 0
    assert fake.calls == [] and pedidas == []


def test_render_falla_avisa_ram_y_no_cierra_nada(fake, form, capsys):
    """B.7: si el render falla, el reporte dice lo de la RAM; el orquestador no cierra programas."""
    fake.rc = {"render": 1}
    fake.hasta("render")
    assert rp.sequence(TID) == 1
    assert "RAM" in capsys.readouterr().out
    src = Path(rp.__file__).read_text(encoding="utf-8")
    for prohibido in ("taskkill", "kill(", "terminate(", "psutil"):
        assert prohibido not in src


def test_render_corre_sin_chequeo_de_ram(fake, form):
    """Omar sacó el chequeo de 14 GB de RAM antes del render (2026-10-27, después de F41): el render corre directo."""
    fake.hasta("render")
    rp.sequence(TID, batch=True)
    assert any("--gfx" in c for cmd in fake.calls for c in cmd)
    assert not hasattr(rp, "RAM_MIN_GB") and not hasattr(rp, "_ram_libre_gb")


# ═══════════════════════ B.6: etapa_de y retomar ═══════════════════════

@pytest.mark.parametrize("etapa", list(rp.ETAPAS))
def test_etapa_de_cada_etapa(fake, etapa):
    fake.hasta(etapa)
    assert rp.etapa_de(TID)[0] == etapa


def test_etapa_de_papel_cambiado_vuelve_a_la_compuerta(fake):
    """El papel aprobado que cambió después (estado_papel = False) vuelve a la compuerta, no al guion."""
    fake.hasta("assets")
    fake.papel_ok = False
    assert rp.etapa_de(TID)[0] == "papel"


def test_etapa_de_planes_cambiados_vuelve_a_la_compuerta(fake):
    fake.hasta("render")
    fake.guion_ok = False
    assert rp.etapa_de(TID)[0] == "aprobar_guion"


def test_etapa_de_fondos_por_visuales_base(fake):
    """Sin el mp4 de preview, los visuales base cocidos de todos los caps del manifest cuentan como FONDOS hechos
    (flux → _flux_visual; veo con suplementarias → _hybrid_visual; veo solo → su clip, no se cuece)."""
    fake.hasta("fondos")
    FakePipeline._w(rp._manifest_path(TID), json.dumps({"chapters": [
        {"id": "ch01", "engine": "flux"},
        {"id": "ch02", "engine": "veo", "supplemental_images": [{"status": "ok", "path": "x.png"}]},
        {"id": "ch03", "engine": "veo", "supplemental_images": [{"status": "failed", "path": "y.png"}]}]}))
    work = rp.OUTPUT_DIR / TID / "_fase2b_work"
    FakePipeline._w(work / "ch01_flux_visual.mp4", "")
    assert rp.etapa_de(TID)[0] == "fondos"            # falta el híbrido de ch02
    FakePipeline._w(work / "ch02_hybrid_visual.mp4", "")
    assert rp.etapa_de(TID)[0] == "guion_pantalla"


def test_etapa_de_render_mas_viejo_que_el_guion(fake):
    fake.hasta("packaging")
    g = rp._guion_pantalla_path(TID)
    r = rp._render_path(TID)
    os.utime(r, (g.stat().st_mtime - 60, g.stat().st_mtime - 60))
    assert rp.etapa_de(TID)[0] == "render"


@pytest.mark.parametrize("artefacto", ["_script_path", "_manifest_path", "_fondos_path", "_render_path"])
def test_etapa_de_cadena_vieja(fake, artefacto):
    """Sin papel pero con algo de después: topic de la cadena borrada; no es «guion» (no se re-paga)."""
    FakePipeline._w(getattr(rp, artefacto)(TID))
    assert rp.etapa_de(TID)[0] == rp.CADENA_VIEJA


def test_etapa_de_cadena_vieja_por_status(fake):
    """Sin papel ni artefactos con su id, pero `video_generated` en topics_db (video con otro video_id)."""
    fake.video_hecho = True
    assert rp.etapa_de(TID)[0] == rp.CADENA_VIEJA


def test_cadena_vieja_no_corre_nada(fake, form):
    FakePipeline._w(rp._script_path(TID))
    assert rp.sequence(TID) == 1
    assert fake.calls == []


def test_listo_no_corre_nada(fake, form):
    fake.hasta("listo")
    assert rp.sequence(TID) == 0
    assert fake.calls == []


def test_etapa_de_es_de_solo_lectura(fake):
    fake.hasta("render")

    def foto():
        return {p: (p.stat().st_mtime_ns, p.read_bytes()) for p in fake.tmp.rglob("*") if p.is_file()}
    antes = foto()
    for _ in range(2):
        rp.etapa_de(TID)
    assert foto() == antes and fake.calls == []


@pytest.mark.parametrize("etapa", [e for e in rp.ETAPAS if e != "listo"])
def test_retomar_nunca_recorre_una_etapa_hecha(fake, form, respuestas, monkeypatch, etapa):
    """run_pipeline --topic X --batch (lo que lanza «retomar») desde cada etapa: corre solo lo que falta."""
    form(True)
    respuestas(["A"] * 5)                  # A en las compuertas; el visor acepta cualquier línea
    fake.hasta(etapa)
    monkeypatch.setattr(sys, "argv", ["run_pipeline.py", "--topic", TID, "--batch"])
    assert rp.main() == 0
    i = rp.ETAPAS.index(etapa)
    assert fake.etiquetas() == [p for p in PRODUCTOR[i:] if p != "fase3"]
    if i >= rp.ETAPAS.index("voz"):
        assert ["fase1_5.py", "--topic", TID, "--batch"] not in fake.calls


def test_etapa_que_no_avanza_para(fake, form, capsys):
    """--plan-only sale 0 sin dejar GUION_PANTALLA.json → frena; no vuelve a correrlo."""
    fake.sin = {"plan-only"}
    fake.hasta("guion_pantalla")
    assert rp.sequence(TID) == 1
    assert fake.etiquetas() == ["plan-only"]
    assert "sin dejar su artefacto" in capsys.readouterr().out


# ═══════════════════════ B.1: el mensaje «m06» se borró ═══════════════════════

def test_sin_mensaje_m06(fake, form, capsys):
    fake.sin = {"voz"}
    fake.hasta("voz")
    rp.sequence(TID)
    out = capsys.readouterr().out.replace(fake.tmp.as_posix(), "<tmp>")   # el tmp_path lleva el nombre del test
    assert "m06" not in out and "[R]/[E]" not in out
    assert "m06" not in Path(rp.__file__).read_text(encoding="utf-8")


# ═══════════════════════ el form (qa_studio_server) con stubs ═══════════════════════

def _fase_del_server(linea: str):
    import qa_studio_server as qa
    if "  ▶ " not in linea:
        return None
    return next((ph for ph in qa._FORM_PHASES if ph in linea), None)


def test_headers_mapean_a_las_fases_del_form(fake, form, respuestas, capsys):
    """Cada header de run_pipeline cae en su fase del form (ningún nombre contiene a otro)."""
    form(True)
    respuestas(["A", "C", "A"])
    rp.sequence(TID, batch=False)
    fases = [_fase_del_server(l) for l in capsys.readouterr().out.splitlines() if "  ▶ " in l]
    assert fases == ["GUION", "PAPEL", "VOZ", "ASSETS", "FONDOS", "PANTALLA", "PANTALLA", "RENDER", "PACKAGING"]


def test_form_resume_lanza_run_pipeline_topic(monkeypatch, tmp_path):
    """/form_resume: _start_form con _form_resume_command (Popen stub: no se lanza nada)."""
    import qa_studio_server as qa
    lanzados = []

    class _P:
        stdout = iter(())
        returncode = 0
        stdin = None

        def wait(self):
            return 0

        def poll(self):
            return 0

    monkeypatch.setattr(qa.subprocess, "Popen", lambda cmd, **k: lanzados.append((cmd, k["env"]["QA_FORM"])) or _P())
    monkeypatch.setitem(qa._FORM, "running", False)
    assert qa._start_form(qa._form_resume_command(TID)) == {"started": True}
    assert lanzados[0][0][1:] == ["run_pipeline.py", "--topic", TID, "--batch"] and lanzados[0][1] == "1"


def test_form_topics_lee_topics_db(monkeypatch, tmp_path):
    import qa_studio_server as qa
    (tmp_path / "data").mkdir()
    (tmp_path / "data" / "topics_db.json").write_text(json.dumps({"topics": [
        {"id": "a", "video_title": "Título A", "status": "researched"}, {"id": "b", "seed_title": "B"}]}),
        encoding="utf-8")
    monkeypatch.setattr(qa, "BASE_DIR", tmp_path)
    assert qa._form_topics() == [{"id": "a", "title": "Título A", "status": "researched"},
                                 {"id": "b", "title": "B", "status": None}]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-q"]))
