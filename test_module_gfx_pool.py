"""F5 §2: la pantalla sale del evidence_pool — candado, recortes con fuente/fecha (nunca de la narración), dedupe por
id entre caps, ícono por contenido, reloj desde la cronología y pregunta desde el cliffhanger."""
from __future__ import annotations

import json

from script_engine import gfx_pool as gp
from script_engine.gfx_icons import ICON_WHITELIST
from script_engine.gfx_project import GfxScene

POOL = {
    "datos": [{"id": "D01", "texto": "Human Rights Watch registró a 517 prisioneros como desaparecidos después de los eventos",
               "tipo": "cifra", "valor": "517", "fuente": "Human Rights Watch, 2005, \"New Orleans: Prisoners Abandoned\""},
              {"id": "D02", "texto": "Los generadores de respaldo de la prisión fallaron el 29 de agosto de 2005",
               "tipo": "fecha", "valor": "29 de agosto de 2005", "fecha": "2005-08-29"},
              {"id": "D03", "texto": "Aproximadamente 6,500 personas estaban encarceladas", "tipo": "cifra",
               "valor": "6,500"}],
    "cronologia": [{"id": "T01", "fecha": "2005-08-29", "evento": "Los generadores de la prisión fallan"},
                   {"id": "T02", "fecha": "2005-08-30", "evento": "Comienza la evacuación de Templeman 1 y 2"}],
    "citas": [], "lugares": [], "personajes": []}
SKEL = {"chapters": [{"chapter_number": 3, "evidence_ids": ["D01", "D02", "T01", "T02"], "cliffhanger": None},
                     {"chapter_number": 4, "evidence_ids": ["D03"], "cliffhanger": None}]}


def W(text: str, step: float = 0.4) -> list[dict]:
    return [{"word": w, "start": round(k * step, 3), "end": round(k * step + 0.3, 3)} for k, w in enumerate(text.split())]


VOICE = ("El 29 de agosto los generadores de la prisión fallaron y todo quedó a oscuras. Nadie sabía cuántos "
         "prisioneros quedaban adentro. El 30 de agosto comenzó la evacuación de Templeman. Todo era confusión.")


def _ctx(n=3):
    return {"chapter_number": n, "pool": POOL, "skeleton_all": SKEL}


def test_icono_por_contenido_y_fuente_corta():
    its = {it["id"]: it for it in POOL["datos"]}
    assert gp.content_icon(its["D01"], ICON_WHITELIST) == (None, None)                 # cifra de personas
    reg = {"texto": "No existen registros oficiales de lo que ocurrió", "tipo": "contradiccion"}
    assert gp.content_icon(reg, ICON_WHITELIST) == (None, None)                        # F5b S4: no está en el mapa
    cel = {"texto": "Las celdas del primer piso comienzan a inundarse", "tipo": "fecha"}
    assert gp.content_icon(cel, ICON_WHITELIST) == ("candado", None)                   # «celdas» → candado (literal)
    adj = {"texto": "Un calor sofocante y escalofriante en el pabellón", "tipo": "fecha"}
    assert gp.content_icon(adj, ICON_WHITELIST) == (None, None)                        # adjetivos: nunca
    assert gp.content_icon(its["D02"], ICON_WHITELIST) == ("rayo_tachado", None)      # G4: ya está en el set
    assert gp.content_icon(its["D03"], ICON_WHITELIST) == (None, None)                 # cifra de personas
    assert gp.short_source(POOL["datos"][0]["fuente"]) == "Human Rights Watch, 2005"
    src = gp.pool_sources(POOL)
    assert src["pool.D01"].startswith("Human Rights Watch registró") and "pool.D01.fuente" in src


def test_recortes_del_pool_con_fuente_y_dedupe(tmp_path):
    words = W(VOICE)
    scenes = [GfxScene(0, 0.0, 15.0), GfxScene(1, 15.0, 40.0)]
    plan = {"archive_clippings": [{"headline": "de verified_facts", "start": 1.0}], "callouts": [], "emphasis": []}
    picks = {}

    def fake(prompt, **kw):
        picks["p"] = prompt
        return {"elecciones": [{"id": "recorte0", "n": 1}]}
    log: list[str] = []
    rows = gp.plan_pool_documents(plan, ctx=_ctx(), words=words, scenes=scenes, time_offset=0.0, work_dir=tmp_path,
                                  cap="ch03", log=log, call=fake)
    arcs = plan["archive_clippings"]
    assert arcs and all(a.get("pool_id") for a in arcs) and "de verified_facts" not in [a["headline"] for a in arcs]
    d01 = next(a for a in arcs if a["pool_id"] == "D01")
    assert d01["kicker"] == "Human Rights Watch, 2005" and "517" in d01["headline"]       # suma: la voz no dice 517
    assert "icon" not in d01 and "La voz dice" in picks["p"]                               # personas: sin ícono
    assert any("pool: recortes" in ln for ln in log) and any(r.get("ahora") for r in rows)
    (tmp_path / "gfx_plan_ch03.resolved.json").write_text(json.dumps({"plan": plan}), encoding="utf-8")
    plan4 = {"archive_clippings": [], "callouts": [], "emphasis": []}
    gp.plan_pool_documents(plan4, ctx=_ctx(4), words=words, scenes=scenes, time_offset=0.0, work_dir=tmp_path,
                           cap="ch04", log=[], call=fake)
    assert "D01" not in {a["pool_id"] for a in plan4["archive_clippings"]}                 # dedupe por id
    assert gp.used_ids_before(tmp_path, 4) >= {"D01"}


def test_reloj_desde_la_cronologia():
    tk = gp.pool_ticker(_ctx(), W(VOICE), 40.0)
    assert tk and (tk["day"], tk["month"], tk["tail"]) == ("29", "AGO", "2005") and tk["pool_id"] == "T01"
    assert tk["duration"] > 2.0
    one = {"chapter_number": 3, "pool": POOL, "skeleton_all": {"chapters": [{"chapter_number": 3, "evidence_ids": ["T01"]}]}}
    assert gp.pool_ticker(one, W(VOICE), 40.0) is None                                     # no avanza de fecha


def test_pregunta_desde_el_cliffhanger(tmp_path, monkeypatch):
    import gfx_config
    from dataclasses import replace
    from script_engine import gfx_question as gq
    monkeypatch.setattr(gfx_config, "gfx_rules", replace(gfx_config.gfx_rules, question_rubric=True))
    chapters = [{"chapter_number": 3, "narration": "Los presos esperaban. Los generadores fallaron. Nadie vino."},
                {"chapter_number": 4, "narration": "Uno. Dos. Tres."}]
    seen = []

    def fake(p, **k):
        seen.append(p)
        return ({"preguntas": ["¿Quién apagó la luz?", "¿Qué pasó con los presos?", "¿Quién fue el culpable?"]}
                if "TRES" in p else {"n": 1})
    r = gq.question_for(tmp_path, "ch03", 3, chapters, call=fake, cliff="517 presos registrados como desaparecidos")
    assert "EL CAPÍTULO SIGUIENTE REVELA" in seen[0] and r["text"] == "¿Qué pasó con los presos?"
    assert r["v"] == gq.CLIFF_VERSION
