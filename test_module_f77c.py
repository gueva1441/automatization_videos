"""
test_module_f77c.py — F77 Etapa C (HANDOFF_F77 C1–C4): tanda de semillas y estante de temas. Todo con dobles: CERO
llamadas reales (ni gate ES, ni subprocesos, ni research/ficha) y CERO lecturas o escrituras en data/ real: el fixture
autouse `aislado` manda a tmp_path ESTANTE_DIR, STEPS_DIR, topics_db, el sentinel de research y el DATA_DIR de
run_pipeline/fase1_5, y verifica al final que todo siga apuntando adentro de tmp_path.

C1  partir_titulos, medir (todos a la vez, remeasure already_es, tid uuid, error del gate = label None), correr_tanda
    (SATURADO sin subproceso, `--hasta-ficha --semilla --topic`, todos lanzados antes de esperar, registros con rc,
    QA_FORM fuera del env del hijo).
C2  fase1_5.hasta_ficha (compuerta → ficha; rojo = Parada y no se paga; nada de escaleta) y el CLI.
C3  estante deducido del disco (listar/item) y run_pipeline.etapa_de → «estante», que corre como «guion».
C4  orden, body del menú E y el menú de niche_discoverer (E primero, default E), _run_estante y _run_tanda.
    topic_researcher: candado entre procesos de topics_db, guardado atómico, _pid_vivo.
"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import threading
import time
import uuid
from pathlib import Path

import pytest

import estante
import fase1
import fase1_5
import niche_discoverer as nd
import run_pipeline as rp
import topic_researcher as tr
from test_run_pipeline import FakePipeline, TID

PREFIJO = "@@QAFORM@@ "


def _marcadores(out: str) -> list[dict]:
    return [json.loads(l[len(PREFIJO):]) for l in out.splitlines() if l.startswith(PREFIJO)]


@pytest.fixture(autouse=True)
def aislado(tmp_path, monkeypatch):
    """Nada de data/ real: todos los caminos del estante, topics_db y sentinels van a tmp_path."""
    data = tmp_path / "data"
    rutas = {
        (estante, "ESTANTE_DIR"): data / "estante",
        (estante, "STEPS_DIR"): data / "scripts" / "_steps",
        (tr, "TOPICS_DB_FILE"): data / "topics_db.json",
        (fase1, "RESEARCH_SENTINEL"): data / "_last_research.json",
        (rp, "DATA_DIR"): data,
        (rp, "OUTPUT_DIR"): tmp_path / "output",
        (rp, "RESEARCH_SENTINEL"): data / "_last_research.json",
        (fase1_5, "STEPS_DIR"): data / "scripts" / "_steps",
        (fase1_5, "TOPICS_DB"): data / "topics_db.json",
    }
    for (mod, nombre), p in rutas.items():
        monkeypatch.setattr(mod, nombre, p)
    monkeypatch.delenv("QA_FORM", raising=False)
    data.mkdir()                                     # data/ siempre existe en la máquina de Omar
    yield data
    for (mod, nombre), _ in rutas.items():          # nadie volvió a apuntar a data/ real
        assert Path(getattr(mod, nombre)).resolve().is_relative_to(tmp_path.resolve()), (mod.__name__, nombre)


def _w(p: Path, obj) -> Path:
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(obj if isinstance(obj, str) else json.dumps(obj, ensure_ascii=False), encoding="utf-8")
    return p


def _gate(label, **kw) -> dict:
    return {"status": "ok" if label else "error", "label": label, **kw}


def _rec(tid: str, titulo: str, label, *, rc=None, heaviest=None) -> dict:
    return {"tid": tid, "titulo": titulo, "seed": {"seed_title": titulo}, "rc": rc,
            "gate": _gate(label, heaviest=heaviest, quota_units=101)}


def _ficha(titulo: str, n_escenas: int = 4) -> dict:
    return {"titulo": titulo, "hechos": [{"h": i} for i in range(7)], "personas": [{"n": "A"}, {"n": "B"}],
            "escenas": [{"que_pasa": f"escena {i} de {titulo}"} for i in range(1, n_escenas + 1)]}


# ═══════════════════════════════════════════════════════════════
#  C1 — partir_titulos
# ═══════════════════════════════════════════════════════════════

def test_partir_titulos_punto_y_coma_y_saltos():
    assert estante.partir_titulos("Palomares 1966; Goiânia 1987\nLos Alfaques 1978\r\nColza 1981") == [
        "Palomares 1966", "Goiânia 1987", "Los Alfaques 1978", "Colza 1981"]


def test_partir_titulos_sin_vacios_ni_repetidos():
    assert estante.partir_titulos(" ;; Palomares 1966 ;\n\n ; palomares 1966; Goiânia 1987 ;Palomares 1966") == [
        "Palomares 1966", "Goiânia 1987"]                       # se queda el primero (sin importar mayúsculas)


@pytest.mark.parametrize("vacio", ["", "   ", ";;\n ; \r\n", None])
def test_partir_titulos_vacio(vacio):
    assert estante.partir_titulos(vacio) == []


# ═══════════════════════════════════════════════════════════════
#  C1 — medir: todos a la vez
# ═══════════════════════════════════════════════════════════════

def test_medir_todos_a_la_vez_con_remeasure_y_tid_uuid():
    titulos = ["Palomares 1966", "Goiânia 1987", "Los Alfaques 1978", "Colza 1981"]
    barrera = threading.Barrier(len(titulos), timeout=10)      # en fila se rompe por timeout
    vistos = []

    def medir_fn(seed, n):
        vistos.append((seed["seed_title"], n, dict(seed["remeasure"])))
        barrera.wait()
        return {"status": "ok", "label": "VACIO", "saturation": 0.1, "quota_units": 101, "source": "api",
                "heaviest": {"title": "x", "views": 10, "months": 3}, "candidatos": ["no se guarda"]}

    recs = estante.medir(titulos, medir_fn=medir_fn)
    assert [r["titulo"] for r in recs] == titulos               # en orden, no por hilo
    assert all(n == 3 for _, n, _ in vistos)
    for r in recs:
        assert uuid.UUID(r["tid"]).version == 4
        rm = r["seed"]["remeasure"]
        assert rm == {"es_query": r["titulo"], "entity": r["titulo"], "already_es": True}
        assert r["seed"]["discovery_mode"] == "manual" and r["seed"]["evidence"]["tanda"] is True
        assert r["gate"]["label"] == "VACIO" and "candidatos" not in r["gate"] and r["gate"]["medido_at"]
        assert r["seed"]["evidence"]["es_gap"] == {"label": "VACIO", "heaviest": {"title": "x", "views": 10, "months": 3}}
    assert len({r["tid"] for r in recs}) == len(titulos)


def test_medir_error_del_gate_queda_sin_label():
    def medir_fn(seed, n):
        if "Goiânia" in seed["seed_title"]:
            raise RuntimeError("cuota agotada")
        return {"status": "ok", "label": "HUECO"}

    a, b = estante.medir(["Palomares 1966", "Goiânia 1987"], medir_fn=medir_fn)
    assert a["gate"]["label"] == "HUECO"
    assert b["gate"]["label"] is None and b["gate"]["status"] == "error"
    assert "RuntimeError: cuota agotada" in b["gate"]["error"]
    assert estante.sigue(b)                                     # sin medir también sigue (con ⚠)


# ═══════════════════════════════════════════════════════════════
#  C1/C2 — correr_tanda
# ═══════════════════════════════════════════════════════════════

class _Popen:
    """Popen falso: registra cmd/env y el orden lanzar/esperar."""

    def __init__(self, eventos: list, rc: dict):
        self.eventos, self.rc, self.lanzados = eventos, rc, []

    def __call__(self, cmd, **kw):
        tid = cmd[cmd.index("--topic") + 1]
        self.eventos.append(("popen", tid))
        self.lanzados.append({"cmd": cmd, **kw})
        fuera = self

        class P:
            def wait(self_inner):
                fuera.eventos.append(("wait", tid))
                return fuera.rc.get(tid, 0)
        return P()


@pytest.fixture
def tanda(monkeypatch):
    labels = {"Palomares 1966": "DISPUTADO", "Goiânia 1987": "SATURADO", "Los Alfaques 1978": "VACIO",
              "Colza 1981": None}

    def medir_fn(seed, n):
        lab = labels[seed["seed_title"]]
        if lab is None:
            raise TimeoutError("sin red")
        return {"status": "ok", "label": lab, "quota_units": 101,
                "heaviest": {"title": "competidor", "views": 1234, "months": 5}}

    monkeypatch.setenv("QA_FORM", "1")
    eventos: list = []
    popen = _Popen(eventos, rc={})
    log: list[str] = []
    return {"labels": labels, "medir_fn": medir_fn, "popen": popen, "eventos": eventos, "log": log}


def _correr(t, python="PYX"):
    return estante.correr_tanda(list(t["labels"]), log=t["log"].append, medir_fn=t["medir_fn"], popen=t["popen"],
                                python=python)


def test_tanda_saturado_sin_subproceso_y_los_demas_con_hasta_ficha(tanda):
    recs = _correr(tanda)
    por = {r["titulo"]: r for r in recs}
    lanzados = {l["cmd"][l["cmd"].index("--topic") + 1]: l for l in tanda["popen"].lanzados}
    assert por["Goiânia 1987"]["tid"] not in lanzados and por["Goiânia 1987"]["rc"] is None
    assert set(lanzados) == {por[t]["tid"] for t in ("Palomares 1966", "Los Alfaques 1978", "Colza 1981")}
    for tid, l in lanzados.items():
        cmd = l["cmd"]
        assert cmd == ["PYX", str(estante.ROOT / "fase1_5.py"), "--semilla", str(estante.ESTANTE_DIR / f"{tid}.json"),
                       "--topic", tid, "--batch", "--hasta-ficha"]
        assert l["cwd"] == str(estante.ROOT) and l["stderr"] == subprocess.STDOUT
        assert Path(l["stdout"].name) == estante.ESTANTE_DIR / f"{tid}.log" and l["stdout"].closed
    assert any("SATURADO: queda en el estante sin research" in x for x in tanda["log"])


def test_tanda_lanza_todos_antes_de_esperar(tanda):
    _correr(tanda)
    ev = tanda["eventos"]
    assert [e for e, _ in ev] == ["popen"] * 3 + ["wait"] * 3


def test_tanda_registros_con_rc(tanda):
    recs = _correr(tanda)
    por = {r["titulo"]: r for r in recs}
    for titulo, r in por.items():
        disco = json.loads((estante.ESTANTE_DIR / f"{r['tid']}.json").read_text(encoding="utf-8"))
        assert disco["tid"] == r["tid"] and disco["titulo"] == titulo and disco["seed"]["seed_title"] == titulo
        assert disco["rc"] == r["rc"]
        assert disco["gate"]["label"] == tanda["labels"][titulo]
    assert por["Goiânia 1987"]["rc"] is None
    assert por["Palomares 1966"]["rc"] == por["Los Alfaques 1978"]["rc"] == por["Colza 1981"]["rc"] == 0


def test_tanda_rc_distinto_de_cero_queda_en_el_registro(tanda, monkeypatch):
    rcs = {}

    class Pop(_Popen):
        def __call__(self, cmd, **kw):
            tid = cmd[cmd.index("--topic") + 1]
            rec = json.loads(Path(cmd[cmd.index("--semilla") + 1]).read_text(encoding="utf-8"))
            self.rc[tid] = 2 if rec["titulo"] == "Palomares 1966" else 0
            rcs[rec["titulo"]] = tid
            return super().__call__(cmd, **kw)
    tanda["popen"] = Pop(tanda["eventos"], {})
    _correr(tanda)
    disco = json.loads((estante.ESTANTE_DIR / f"{rcs['Palomares 1966']}.json").read_text(encoding="utf-8"))
    assert disco["rc"] == 2
    assert any("⚠ «Palomares 1966» terminó (exit 2)" in x for x in tanda["log"])


def test_tanda_semilla_del_registro_es_la_que_lee_fase1_5(tanda):
    """El archivo de --semilla existe antes del Popen y trae seed_id / seed_title / discovery_mode."""
    _correr(tanda)
    for l in tanda["popen"].lanzados:
        rec = json.loads(Path(l["cmd"][l["cmd"].index("--semilla") + 1]).read_text(encoding="utf-8"))
        assert {"seed_id", "seed_title", "discovery_mode"} <= set(rec["seed"])


def test_tanda_saca_qa_form_del_env_del_hijo(tanda):
    assert os.environ.get("QA_FORM") == "1"
    _correr(tanda)
    for l in tanda["popen"].lanzados:
        assert "QA_FORM" not in l["env"] and l["env"]["PYTHONIOENCODING"] == "utf-8"
    assert os.environ.get("QA_FORM") == "1"                   # el del padre no se toca


# ═══════════════════════════════════════════════════════════════
#  C3 — estante deducido del disco
# ═══════════════════════════════════════════════════════════════

def _steps(tid: str) -> Path:
    return estante.STEPS_DIR / tid


@pytest.fixture
def sin_pool(monkeypatch):
    pools: dict[str, dict] = {}
    monkeypatch.setattr(estante, "_pool", lambda tid: pools.get(tid))
    return pools


def test_item_ficha_sin_escaleta_es_elegible(sin_pool):
    estante.guardar_registro(_rec("t1", "Palomares 1966", "VACIO"))
    _w(_steps("t1") / "ficha_caso.json", _ficha("Palomares: los cobayas"))
    _w(_steps("t1") / "01_v3_costos.json", {"_corridas": [{"usd": 1.2}, {"usd": "0.7345"}, {}]})
    [i] = estante.listar()
    assert i["tid"] == "t1" and i["elegible"] and i["avisos"] == []
    assert i["titulo"] == "Palomares 1966"                     # el del registro manda
    assert i["ficha"] == {"titulo": "Palomares: los cobayas", "hechos": 7, "escenas": 4, "personas": 2,
                          "primeras": ["escena 1 de Palomares: los cobayas", "escena 2 de Palomares: los cobayas",
                                       "escena 3 de Palomares: los cobayas"]}
    assert i["usd"] == 1.9345
    assert estante.elegibles([i]) == [i]


def test_item_con_escaleta_queda_fuera(sin_pool):
    estante.guardar_registro(_rec("t1", "Palomares 1966", "VACIO"))
    _w(_steps("t1") / "ficha_caso.json", _ficha("x"))
    _w(_steps("t1") / "01a_escaleta.json", {})
    _w(_steps("t2") / "ficha_caso.json", _ficha("viejo"))      # topic viejo, también con escaleta
    _w(_steps("t2") / "01a_escaleta.json", {})
    assert estante.item("t1") is None
    assert estante.listar() == []


def test_item_saturado_sin_dir_tiene_aviso_y_no_es_elegible(sin_pool):
    estante.guardar_registro(_rec("t1", "Goiânia 1987", "SATURADO"))
    [i] = estante.listar()
    assert not i["elegible"] and i["ficha"] is None and i["usd"] == 0.0
    assert i["avisos"] == ["SATURADO: sin research"]


def test_item_compuerta_roja_sin_ficha_tiene_aviso(sin_pool):
    estante.guardar_registro(_rec("t1", "Los Alfaques 1978", "DISPUTADO", rc=2))
    _w(_steps("t1") / "POOL_GATE.md", "# POOL_GATE — `t1`\n\n**🔴 ROJO** · 2026-11-04\n")
    [i] = estante.listar()
    assert i["compuerta"] == "rojo" and not i["elegible"]
    assert i["avisos"] == ["compuerta del pool ROJA: sin ficha"]


def test_item_compuerta_del_pool_real_en_disco(aislado):
    """Sin parche de _pool: métricas y color salen de un 00_pool_v3.json mínimo (pool_gate.evaluate de verdad)."""
    estante.guardar_registro(_rec("t1", "Colza 1981", "HUECO"))
    pool = {"datos": [{}] * 3, "citas": [{"verificacion": {"estado": "verificada"}}],
            "personajes": [{"nombre": "Juan Pérez", "elegible_humano": True}], "cronologia": [{"fecha": "1981-05-01"}]}
    _w(_steps("t1") / "00_pool_v3.json", pool)
    [i] = estante.listar()
    assert i["pool"] == {"datos": 3, "citas_verificadas": 1, "elegibles_humano": 1, "eventos_con_fecha": 1,
                         "personas_con_nombre": 1, "compuerta": "rojo"}
    assert i["compuerta"] == "rojo" and "compuerta del pool ROJA: sin ficha" in i["avisos"]


def test_item_sin_ficha_con_rc_y_corriendo(sin_pool):
    estante.guardar_registro(_rec("t1", "A", "VACIO", rc=1))
    estante.guardar_registro(_rec("t2", "B", "VACIO", rc=None))
    _steps("t1").mkdir(parents=True)
    a, b = estante.item("t1"), estante.item("t2")
    assert a["avisos"] == ["sin ficha (exit 1; ver data/estante/t1.log)"] and not a["elegible"]
    assert b["avisos"] == ["sin ficha (corriendo o sin correr)"]


def test_item_gate_sin_medir_avisa_pero_con_ficha_es_elegible(sin_pool):
    estante.guardar_registro(_rec("t1", "A", None))
    _w(_steps("t1") / "ficha_caso.json", _ficha("A"))
    [i] = estante.listar()
    assert i["elegible"] and i["avisos"] == ["gate sin medir"]


def test_topic_viejo_con_ficha_y_sin_registro_entra(sin_pool):
    _w(_steps("viejo") / "ficha_caso.json", _ficha("Kyshtym 1957"))
    _w(_steps("viejo_sin_ficha") / "00_pool_v3.json", {})       # sin ficha ni registro: no es del estante
    (estante.STEPS_DIR / "suelto.txt").write_text("x", encoding="utf-8")
    [i] = estante.listar()
    assert i["tid"] == "viejo" and i["titulo"] == "Kyshtym 1957" and i["elegible"] and i["avisos"] == []
    assert i["gate"] == {}
    assert estante.item("viejo_sin_ficha") is None


def test_listar_sin_dirs_y_registro_roto(sin_pool):
    assert estante.listar() == []
    _w(estante.ESTANTE_DIR / "roto.json", "{no es json")
    _w(estante.ESTANTE_DIR / "lista.json", [1, 2])
    assert estante.listar() == []


# ═══════════════════════════════════════════════════════════════
#  C4 — orden
# ═══════════════════════════════════════════════════════════════

def test_listar_ordena_gate_luego_humanos_y_avisos_al_final(sin_pool):
    casos = [("sat", "Saturado", "SATURADO", None, False),
             ("dis", "Disputado", "DISPUTADO", 9, True),
             ("vac2", "Vacío dos", "VACIO", 2, True),
             ("hue5", "Hueco cinco", "HUECO", 5, True),
             ("roja", "Roja", "VACIO", 1, False),
             ("medir", "Sin medir", None, 50, True)]
    for tid, titulo, lab, hum, ficha in casos:
        estante.guardar_registro(_rec(tid, titulo, lab))
        if hum is not None:
            sin_pool[tid] = {"datos": 1, "citas_verificadas": 1, "personas_con_nombre": 1, "eventos_con_fecha": 1,
                             "elegibles_humano": hum, "compuerta": "verde"}
        if ficha:
            _w(_steps(tid) / "ficha_caso.json", _ficha(titulo))
    _w(_steps("roja") / "POOL_GATE.md", "**🔴 ROJO**")
    sin_pool["roja"]["compuerta"] = "rojo"
    _w(_steps("viejo") / "ficha_caso.json", _ficha("Viejo"))   # sin registro: sin label, sin aviso
    orden = [i["tid"] for i in estante.listar()]
    # sin ⚠: VACIO/HUECO (más humanos primero) → DISPUTADO → sin label; ⚠ al final, también por gate
    assert orden == ["hue5", "vac2", "dis", "viejo", "roja", "sat", "medir"]


def test_ordenar_desempata_por_titulo():
    it = [{"titulo": "beta", "gate": {"label": "VACIO"}, "pool": None, "avisos": []},
          {"titulo": "Alfa", "gate": {"label": "HUECO"}, "pool": None, "avisos": []}]
    assert [i["titulo"] for i in estante.ordenar(it)] == ["Alfa", "beta"]


# ═══════════════════════════════════════════════════════════════
#  C4 — body del menú E
# ═══════════════════════════════════════════════════════════════

def test_body_vacio():
    assert estante.body([]) == "El estante está vacío."


def test_body_tabla_miles_con_punto_y_aviso(sin_pool):
    estante.guardar_registro(_rec("t1", "Palomares 1966", "DISPUTADO",
                                  heaviest={"title": "Palomares | el accidente", "views": 1234567, "months": 14}))
    _w(_steps("t1") / "ficha_caso.json", _ficha("Palomares"))
    sin_pool["t1"] = {"datos": 40, "citas_verificadas": 6, "personas_con_nombre": 12, "eventos_con_fecha": 9,
                      "elegibles_humano": 3, "compuerta": "amarillo"}
    estante.guardar_registro(_rec("t2", "Goiânia 1987", "SATURADO",
                                  heaviest={"title": "Goiânia", "views": 987, "months": 2}))
    L = estante.body(estante.listar()).splitlines()
    assert L[0] == "| # | título | gate | pool | ficha | US$ |" and L[1] == "|---|---|---|---|---|---|"
    assert len(L) == 4
    uno, dos = L[2], L[3]
    assert uno.startswith("| 1 | Palomares 1966 | DISPUTADO · «Palomares / el accidente» 1.234.567 views, 14 meses |")
    assert ("| 40 datos · 6 citas · 12 personas · 9 eventos · 3 humanos · amarillo |") in uno
    assert "«Palomares» · 7 hechos · 4 escenas · 2 personas · escena 1 de Palomares / escena 2" in uno
    assert "escena 4" not in uno and uno.endswith("| 0.00 |")
    assert uno.count("|") == 7                                  # el «|» del título del competidor no rompe la tabla
    assert dos.startswith("| 2 | Goiânia 1987 ⚠ SATURADO: sin research | SATURADO · «Goiânia» 987 views, 2 meses |")
    assert "| — | — |" in dos


def test_body_sin_gate_ni_pool_con_compuerta_md(sin_pool):
    estante.guardar_registro(_rec("t1", "Colza 1981", None, rc=2))
    _w(_steps("t1") / "POOL_GATE.md", "**🔴 ROJO**")
    [fila] = estante.body(estante.listar()).splitlines()[2:]
    assert "| sin medir |" in fila and "| compuerta rojo |" in fila
    assert "⚠ gate sin medir; compuerta del pool ROJA: sin ficha" in fila


# ═══════════════════════════════════════════════════════════════
#  C3 — run_pipeline: etapa «estante» corre como «guion»
# ═══════════════════════════════════════════════════════════════

@pytest.fixture
def fake(tmp_path, monkeypatch):
    f = FakePipeline(tmp_path).install(monkeypatch.setattr)
    monkeypatch.setattr(rp, "QA_FORM", False)
    return f


def test_etapa_de_estante_para_ficha_sin_escaleta(fake):
    _w(rp._steps_path(TID, "ficha_caso.json"), _ficha("x"))
    assert rp.etapa_de(TID)[0] == rp.ESTANTE == "estante"
    _w(rp._steps_path(TID, "01a_escaleta.json"), {})
    assert rp.etapa_de(TID)[0] == "guion"                      # con escaleta ya no es del estante


def test_etapa_de_sin_ficha_es_guion(fake):
    assert rp.etapa_de(TID)[0] == "guion"


def test_orden_del_estante_es_el_del_guion():
    assert rp._orden(rp.ESTANTE) == rp._orden("guion") == 0
    assert rp._PASOS[rp.ESTANTE] is rp._paso_guion


def test_sequence_desde_el_estante_corre_el_guion(fake, capsys):
    _w(rp._steps_path(TID, "ficha_caso.json"), _ficha("x"))
    assert rp.sequence(TID) == 0
    assert fake.calls == [["fase1_5.py", "--topic", TID, "--batch"]]
    out = capsys.readouterr().out
    assert "arranca en «estante»" in out


# ═══════════════════════════════════════════════════════════════
#  C2 — fase1_5.hasta_ficha y el CLI
# ═══════════════════════════════════════════════════════════════

@pytest.fixture
def f15(monkeypatch):
    from script_engine import m01a_escaleta as me
    from researcher_steps.pool_gate import PoolGateRed
    calls: list = []
    est = {"rojo": False}
    topic = {"id": "tz", "evidence_pool": {"datos": []}}

    def gate(t, pool, log):
        calls.append("gate")
        if est["rojo"]:
            raise PoolGateRed({"motivos": ["pocos datos", "sin personas"]})
        log.append("  [compuerta] verde")

    def prohibido(nombre):
        def f(*a, **k):
            calls.append(nombre)
            raise AssertionError(f"{nombre} no se llama en --hasta-ficha")
        return f

    monkeypatch.setattr(fase1_5, "_topic_v3", lambda tid: topic)
    monkeypatch.setattr(fase1_5, "pool_v3", lambda t: True)
    monkeypatch.setattr(me, "pool_gate_profile", gate)
    monkeypatch.setattr(fase1_5, "asegurar_ficha",
                        lambda tid, t, log: calls.append("ficha") or {"titulo": "ficha de " + tid})
    monkeypatch.setattr(me, "generate_escaleta", prohibido("escaleta"))
    monkeypatch.setattr(fase1_5, "asegurar_canon", prohibido("canon"))
    monkeypatch.setattr(fase1_5, "run_escaleta_v3", prohibido("run_escaleta_v3"))
    return {"calls": calls, "est": est}


def test_hasta_ficha_compuerta_y_despues_ficha(f15):
    assert fase1_5.hasta_ficha("tz") == {"titulo": "ficha de tz"}
    assert f15["calls"] == ["gate", "ficha"]


def test_hasta_ficha_rojo_es_parada_y_no_paga_la_ficha(f15):
    f15["est"]["rojo"] = True
    with pytest.raises(fase1_5.Parada, match="compuerta del pool ROJA: pocos datos; sin personas"):
        fase1_5.hasta_ficha("tz")
    assert f15["calls"] == ["gate"]


def test_hasta_ficha_sin_pool_es_parada(f15, monkeypatch):
    monkeypatch.setattr(fase1_5, "pool_v3", lambda t: False)
    monkeypatch.setattr(fase1_5, "motivo_sin_pool", lambda tid, t: f"{tid}: sin pool v3")
    with pytest.raises(fase1_5.Parada, match="tz: sin pool v3"):
        fase1_5.hasta_ficha("tz")
    assert f15["calls"] == []


@pytest.mark.parametrize("argv", [["--hasta-ficha"], ["--hasta-ficha", "--batch"],
                                  ["--hasta-ficha", "--topic", "tz", "--from", "m01a"]])
def test_cli_hasta_ficha_sin_topic_es_error_del_parser(argv, monkeypatch, capsys, f15):
    monkeypatch.setattr(sys, "argv", ["fase1_5.py", *argv])
    with pytest.raises(SystemExit) as e:
        fase1_5.main()
    assert e.value.code == 2
    assert "--hasta-ficha necesita --topic" in capsys.readouterr().err
    assert f15["calls"] == []


def test_cli_hasta_ficha_parada_sale_2_y_ok_sale_0(monkeypatch, capsys, f15):
    monkeypatch.setattr(fase1_5, "_print_gemini_cost", lambda: None)
    monkeypatch.setattr(sys, "argv", ["fase1_5.py", "--topic", "tz", "--batch", "--hasta-ficha"])
    with pytest.raises(SystemExit) as e:
        fase1_5.main()
    assert e.value.code == 0 and "tz en el estante" in capsys.readouterr().out
    f15["est"]["rojo"] = True
    with pytest.raises(SystemExit) as e:
        fase1_5.main()
    assert e.value.code == 2 and "PARADA antes de la ficha" in capsys.readouterr().out


# ═══════════════════════════════════════════════════════════════
#  C4 — niche_discoverer: menú E/D, _run_estante, _run_tanda
# ═══════════════════════════════════════════════════════════════

class _Corte(Exception):
    pass


def _corta(prompt=""):
    raise _Corte


def _menu(monkeypatch, capsys, n: int) -> dict:
    monkeypatch.setattr(nd, "_QA_FORM", True)
    monkeypatch.setattr(nd, "_n_estante", lambda: n)
    monkeypatch.setattr("builtins.input", _corta)
    with pytest.raises(_Corte):
        nd.discover_niches()
    return next(m for m in _marcadores(capsys.readouterr().out) if m["menu"] == "discovery_mode")


def test_menu_con_estante_e_primero_y_default_e(monkeypatch, capsys):
    m = _menu(monkeypatch, capsys, 3)
    assert [o["key"] for o in m["options"]] == ["E", "A", "B", "C", "D", "S"]
    assert m["default"] == "E" and "Estante (3)" in m["options"][0]["label"]


def test_menu_sin_estante_sin_e(monkeypatch, capsys):
    m = _menu(monkeypatch, capsys, 0)
    assert [o["key"] for o in m["options"]] == ["A", "B", "C", "D", "S"] and m["default"] == "A"


def test_n_estante_lee_el_estante_aislado(sin_pool):
    assert nd._n_estante() == 0
    _w(_steps("t1") / "ficha_caso.json", _ficha("x"))
    assert nd._n_estante() == 1


def _respuestas(monkeypatch, *rs):
    it = iter(rs)
    monkeypatch.setattr("builtins.input", lambda prompt="": next(it))


def test_run_estante_elegir_1_escribe_el_sentinel(sin_pool, monkeypatch, capsys):
    monkeypatch.setattr(nd, "_QA_FORM", True)
    estante.guardar_registro(_rec("sat", "Goiânia 1987", "SATURADO"))     # ⚠ y no elegible: no tiene botón
    estante.guardar_registro(_rec("t1", "Palomares 1966", "VACIO"))
    _w(_steps("t1") / "ficha_caso.json", _ficha("Palomares"))
    _respuestas(monkeypatch, "1")
    assert nd._run_estante() == "t1"
    assert json.loads(fase1.RESEARCH_SENTINEL.read_text(encoding="utf-8"))["tids"] == ["t1"]
    [m] = [x for x in _marcadores(capsys.readouterr().out) if x["menu"] == "estante_pick"]
    assert [o["key"] for o in m["options"]] == ["1", "S"] and m["default"] == "S"
    assert m["body"].startswith("| # | título |") and "Goiânia 1987 ⚠" in m["body"]


@pytest.mark.parametrize("resp", ["S", "s", "", "7", "0"])
def test_run_estante_volver_no_escribe_nada(sin_pool, monkeypatch, resp):
    estante.guardar_registro(_rec("t1", "Palomares 1966", "VACIO"))
    _w(_steps("t1") / "ficha_caso.json", _ficha("Palomares"))
    _respuestas(monkeypatch, resp)
    assert nd._run_estante() is None
    assert not fase1.RESEARCH_SENTINEL.exists()


@pytest.mark.parametrize("resp", ["", "  ;  ;\n"])
def test_run_tanda_vacia_cancela(monkeypatch, capsys, resp):
    monkeypatch.setattr(nd, "_QA_FORM", True)
    monkeypatch.setattr(estante, "correr_tanda", lambda *a, **k: pytest.fail("no debe correr"))
    _respuestas(monkeypatch, resp)
    assert nd._run_tanda() is None
    out = capsys.readouterr().out
    assert "Tanda cancelada" in out
    [m] = _marcadores(out)
    assert m["menu"] == "tanda_titulos" and m["accept"] == "text"


def test_run_tanda_pasa_los_titulos_partidos(monkeypatch, sin_pool, capsys):
    vistos = []
    monkeypatch.setattr(estante, "correr_tanda", lambda t, **k: vistos.append(t) or [])
    _respuestas(monkeypatch, "Palomares 1966; Goiânia 1987;palomares 1966")
    nd._run_tanda()
    assert vistos == [["Palomares 1966", "Goiânia 1987"]]
    assert "El estante está vacío." in capsys.readouterr().out


def test_menu_e_elegido_devuelve_sin_seeds(monkeypatch):
    monkeypatch.setattr(nd, "_QA_FORM", False)
    monkeypatch.setattr(nd, "_n_estante", lambda: 1)
    monkeypatch.setattr(nd, "_run_estante", lambda: "t1")
    _respuestas(monkeypatch, "E")
    assert nd.discover_niches() == []


# ═══════════════════════════════════════════════════════════════
#  topic_researcher — candado y guardado atómico de topics_db
# ═══════════════════════════════════════════════════════════════

def test_lock_8_hilos_no_pierden_nada():
    tr._save_topics_db({"created_at": "x", "topics": []})
    errores = []

    def agregar(n):
        try:
            with tr._topics_db_lock():
                db = tr._load_topics_db()
                time.sleep(0.01)                                # ventana para la carrera si no hubiera candado
                db["topics"].append({"id": f"t{n}"})
                tr._save_topics_db(db)
        except Exception as e:                                  # pragma: no cover
            errores.append(e)

    hilos = [threading.Thread(target=agregar, args=(n,)) for n in range(8)]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join(timeout=60)
    assert not errores and not any(h.is_alive() for h in hilos)
    ids = sorted(t["id"] for t in tr._load_topics_db()["topics"])
    assert ids == sorted(f"t{n}" for n in range(8))
    assert not tr.TOPICS_DB_FILE.with_name(tr.TOPICS_DB_FILE.name + ".lock").exists()


def _pid_muerto() -> int:
    p = subprocess.Popen([sys.executable, "-c", "pass"])
    p.wait()
    return p.pid


def test_pid_vivo():
    assert tr._pid_vivo(os.getpid()) is True
    assert tr._pid_vivo(_pid_muerto()) is False


def test_lock_huerfano_de_pid_muerto_se_borra():
    lock = tr.TOPICS_DB_FILE.with_name(tr.TOPICS_DB_FILE.name + ".lock")
    lock.parent.mkdir(parents=True, exist_ok=True)
    lock.write_text(str(_pid_muerto()), encoding="utf-8")
    dentro = threading.Event()

    def tomar():
        with tr._topics_db_lock():
            assert lock.read_text() == str(os.getpid())
            dentro.set()
    h = threading.Thread(target=tomar, daemon=True)
    h.start()
    assert dentro.wait(timeout=10), "el candado huérfano no se borró"
    h.join(timeout=10)
    assert not lock.exists()


def test_lock_de_pid_vivo_espera():
    lock = tr.TOPICS_DB_FILE.with_name(tr.TOPICS_DB_FILE.name + ".lock")
    lock.parent.mkdir(parents=True, exist_ok=True)
    lock.write_text(str(os.getpid()), encoding="utf-8")         # vivo: hay que esperar a que lo suelte
    dentro = threading.Event()

    def tomar():
        with tr._topics_db_lock():
            dentro.set()
    h = threading.Thread(target=tomar, daemon=True)
    h.start()
    assert not dentro.wait(timeout=0.6)
    lock.unlink()
    assert dentro.wait(timeout=10)
    h.join(timeout=10)


def test_lock_se_suelta_aunque_falle_adentro():
    lock = tr.TOPICS_DB_FILE.with_name(tr.TOPICS_DB_FILE.name + ".lock")
    lock.parent.mkdir(parents=True, exist_ok=True)
    with pytest.raises(ValueError):
        with tr._topics_db_lock():
            raise ValueError("research roto")
    assert not lock.exists()


def test_save_topics_db_atomico_sin_tmp():
    db = {"created_at": "x", "topics": [{"id": "t1", "video_title": "Palomares — 1966"}]}
    tr._save_topics_db(db)
    tr._save_topics_db({**db, "topics": db["topics"] + [{"id": "t2"}]})
    carpeta = tr.TOPICS_DB_FILE.parent
    assert [p.name for p in carpeta.iterdir()] == ["topics_db.json"]
    assert [t["id"] for t in tr._load_topics_db()["topics"]] == ["t1", "t2"]
    assert "Palomares — 1966" in tr.TOPICS_DB_FILE.read_text(encoding="utf-8")
