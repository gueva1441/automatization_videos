"""test_module_f39_research.py — F39 §A.3: `topic_researcher.investigar_semilla(seed, topic_id)`.

Una semilla en un topic dado: la misma cadena del modo long (run_seed de v3 + 4a–4d + _enrich_with_seed_metadata), con
`id == topic_id` y `seed_title`, sin filtro de semillas ya investigadas y sin tocar inbox ni archivo de semillas.
`research_topics` queda igual por fuera. Sin red, sin LLM, sin data/ (todo a tmp_path)."""
import json

import pytest

import topic_researcher as tr
from researcher_steps import research_v3 as r3
from researcher_steps.pool_gate import PoolGateRed

SEED = {"seed_id": "s-f39", "seed_title": "La explosión de Kyshtym", "discovery_mode": "manual",
        "root_niche": "misterio", "tags": ["t"]}


@pytest.fixture
def entorno(monkeypatch, tmp_path):
    """Rutas a tmp_path, Flash 4a–4d falsos, run_seed falso que anota (topic_id, steps_dir)."""
    inbox, archivo, db = tmp_path / "selected_seeds.json", tmp_path / "seeds_archive.json", tmp_path / "topics_db.json"
    steps = tmp_path / "_steps"
    inbox.write_text(json.dumps({"seeds": [SEED]}, ensure_ascii=False), encoding="utf-8")
    archivo.write_text(json.dumps({"archived": []}), encoding="utf-8")
    monkeypatch.setattr(tr, "SEEDS_FILE", inbox)
    monkeypatch.setattr(tr, "SEEDS_ARCHIVE_FILE", archivo)
    monkeypatch.setattr(tr, "TOPICS_DB_FILE", db)
    monkeypatch.setattr(tr, "STEPS_DIR", steps)
    monkeypatch.setattr(tr, "time", type("T", (), {"sleep": staticmethod(lambda s: None)}))
    monkeypatch.delenv("RESEARCH_V3", raising=False)
    llamadas: list = []
    monkeypatch.setattr(r3, "run_seed", lambda seed, tid, d, **k: (llamadas.append(("run_seed", tid, d))
                                                                   or ({"v3": True}, {"tecnico": "p"}, None)))
    monkeypatch.setattr(tr, "extract_facts_and_sources", lambda blocks, *a, **k: llamadas.append("4a") or
                        {"verified_facts": [{"fact": "f", "source_block": "tecnico"}], "sources": ["u"]})
    monkeypatch.setattr(tr, "extract_canonical", lambda *a, **k: llamadas.append("4b") or
                        {"canonical_subject_description": "c"})
    monkeypatch.setattr(tr, "extract_meta", lambda *a, **k: llamadas.append("4c") or
                        {"video_title": "Kyshtym", "search_keyword": "kyshtym"})
    monkeypatch.setattr(tr, "extract_research_summary", lambda *a, **k: llamadas.append("4d") or
                        {"research_summary": "r"})
    return {"inbox": inbox, "archivo": archivo, "db": db, "steps": steps, "llamadas": llamadas}


def _bytes(e):
    return e["inbox"].read_bytes(), e["archivo"].read_bytes()


def test_investigar_semilla_registra_con_el_id_dado_sin_tocar_inbox_ni_archivo(entorno):
    antes = _bytes(entorno)
    topic = tr.investigar_semilla(SEED, "f39-prueba")
    assert topic["id"] == "f39-prueba" and topic["seed_title"] == SEED["seed_title"]
    assert topic["seed_id"] == "s-f39" and topic["research_version"] == 3 and topic["evidence_pool"] == {"v3": True}
    assert entorno["llamadas"] == [("run_seed", "f39-prueba", entorno["steps"] / "f39-prueba"),
                                   "4a", "4b", "4c", "4d"]   # F50 A: sin 4e
    guardado = json.loads(entorno["db"].read_text(encoding="utf-8"))["topics"]
    assert guardado == [topic]
    assert not {"era_visual_canon", "documented_people", "central_subject"} & set(topic)   # F50 A: el research no arma canon
    assert {p.name for p in (entorno["steps"] / "f39-prueba").iterdir()} == {
        "00_pool_etiquetado.json", "01_facts_sources.json", "02_canonical.json", "03_meta.json", "04_summary.json"}
    assert _bytes(entorno) == antes                      # ni inbox ni seeds_archive


def test_investigar_semilla_no_filtra_semillas_ya_investigadas(entorno):
    entorno["db"].write_text(json.dumps({"topics": [{"id": "viejo", "seed_id": "s-f39", "video_title": "V"}]}),
                             encoding="utf-8")
    topic = tr.investigar_semilla(SEED, "f39-otra")
    ids = [t["id"] for t in json.loads(entorno["db"].read_text(encoding="utf-8"))["topics"]]
    assert ids == ["viejo", "f39-otra"] and topic["seed_id"] == "s-f39"


def test_id_ya_en_topics_db_es_valueerror_sin_llamar_run_seed(entorno):
    entorno["db"].write_text(json.dumps({"topics": [{"id": "f39-prueba", "seed_id": "otro"}]}), encoding="utf-8")
    antes = entorno["db"].read_bytes()
    with pytest.raises(ValueError, match="f39-prueba"):
        tr.investigar_semilla(SEED, "f39-prueba")
    assert entorno["llamadas"] == [] and entorno["db"].read_bytes() == antes
    assert not (entorno["steps"] / "f39-prueba").exists()
    with pytest.raises(ValueError):
        tr.investigar_semilla(SEED, "")
    sin_modo = {k: v for k, v in SEED.items() if k != "discovery_mode"}
    with pytest.raises(ValueError, match="discovery_mode"):         # _enrich lo pide: se avisa antes de gastar
        tr.investigar_semilla(sin_modo, "f39-nueva")
    assert entorno["llamadas"] == []


def test_pool_gate_red_se_propaga_y_no_registra(entorno, monkeypatch):
    gate = {"color": "rojo", "metricas": {"datos": 1}, "motivos": ["no hay con qué contar"]}

    def rojo(seed, tid, d, **k):
        entorno["llamadas"].append("run_seed")
        raise PoolGateRed(gate)
    monkeypatch.setattr(r3, "run_seed", rojo)
    antes = _bytes(entorno)
    with pytest.raises(PoolGateRed) as e:
        tr.investigar_semilla(SEED, "f39-rojo")
    assert e.value.gate["motivos"] == ["no hay con qué contar"]
    assert entorno["llamadas"] == ["run_seed"]           # 4a–4d no corren
    assert not entorno["db"].exists() and _bytes(entorno) == antes   # sin registro, inbox sin bandera


def test_research_topics_igual_que_antes(entorno):
    otra = {**SEED, "seed_id": "s-nueva", "seed_title": "Otra"}
    entorno["inbox"].write_text(json.dumps({"seeds": [SEED, otra]}, ensure_ascii=False), encoding="utf-8")
    entorno["db"].write_text(json.dumps({"topics": [{"id": "viejo", "seed_id": "s-f39", "video_title": "V"}]}),
                             encoding="utf-8")
    out = tr.research_topics(video_type="long")
    assert [t["seed_id"] for t in out] == ["s-nueva"]               # la ya investigada se saltea
    assert "seed_title" not in out[0]                                # salida del topic: igual que antes
    tid = out[0]["id"]
    assert tid != "s-nueva" and len(tid) == 36                       # uuid4, como hoy
    assert entorno["llamadas"][0] == ("run_seed", tid, entorno["steps"] / tid)
    inbox = json.loads(entorno["inbox"].read_text(encoding="utf-8"))["seeds"]
    assert [s["seed_id"] for s in inbox] == ["s-f39"]                # la investigada sale del inbox
    archivados = json.loads(entorno["archivo"].read_text(encoding="utf-8"))["archived"]
    assert [(a["seed_id"], a["topic_id"]) for a in archivados] == [("s-nueva", tid)]
    assert [t["id"] for t in json.loads(entorno["db"].read_text(encoding="utf-8"))["topics"]] == ["viejo", tid]
