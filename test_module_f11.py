"""
test_module_f11.py — F11 (guion v4): bloqueantes con casos de las corridas guardadas, el camino v3 byte-idéntico con
un `call` falso y la reparación de una sola ronda (nunca vuelve a llamar al guionista entero).
"""
from __future__ import annotations

import hashlib
import json

import pytest

import fase1_5 as f15
from script_engine import guion_v4 as g4
from script_engine import m01d_particion as md

# ═══════════════════════════════════════════════════════════════
#  Fixture chica (escaleta de 12 beats, pool mínimo)
# ═══════════════════════════════════════════════════════════════

FRASE = ("Liz Torres caminaba entre las góndolas del patio de comidas con su esposo. El humo bajó del techo. "
         "Nadie entendía nada. La gente corrió hacia el portón de la avenida y lo encontró cerrado. ")
POOL = {
    "datos": [{"id": f"D{k}", "texto": f"El portón número {k} estaba cerrado", "tipo": "cifra", "valor": str(k)}
              for k in range(1, 14)]
    + [{"id": "D50", "texto": "Oficialmente hubo 327 muertos", "tipo": "cifra", "valor": "327"}],
    "cronologia": [{"id": "T1", "evento": "Empieza el incendio del supermercado", "fecha": "2004-08-01"},
                   {"id": "T2", "evento": "Los bomberos llegan al supermercado", "fecha": "2004-08-01"}],
    "citas": [{"id": "Q1", "texto": "Era como estar dentro de un horno, con las cenizas", "autor": "Liz Torres",
               "rol": "Sobreviviente", "verificacion": {"estado": "verificada_parcial"}},
              {"id": "Q2", "texto": "Cerraron las puertas para que nadie saliera sin pagar", "autor": "Nelson Astigarraga",
               "rol": "Sobreviviente", "verificacion": {"estado": "verificada_parcial"}},
              {"id": "Q3", "texto": "Soy la vida de muchas personas que cayeron sobre mi cuerpo", "autor": "Liz Torres",
               "rol": "Sobreviviente", "verificacion": {"estado": "verificada"}}],
    "lugares": [{"id": "L1", "nombre": "Asunción"}],
    "personajes": [{"id": "P1", "nombre": "Liz Torres", "rol": "Sobreviviente"},
                   {"id": "P2", "nombre": "Juan Pío Paiva", "rol": "dueño"},
                   {"id": "P3", "nombre": "Daniel Areco", "rol": "guardia de seguridad"}],
    "_descartados": [{"kind": "datos", "texto": "Un incendio en Rosario dejó 194 muertos en 2004"}],
}
FACTS = [{"fact": "El incendio fue el 1 de agosto de 2004 en Asunción."}]
TOPIC = {"id": "t-f11", "video_title": "Ycuá", "evidence_pool": POOL, "verified_facts": FACTS}


def _esc():
    beats, k = [], 1
    for cap, nb in ((1, 1), (2, 2), (3, 2), (4, 2), (5, 2), (6, 2), (7, 1)):
        for _ in range(nb):
            beats.append({"n": k, "cap": cap, "funcion": "gancho" if k == 1 else "escalada", "emocion": "miedo",
                          "intensidad": 3, "dato_central": f"D{k}", "datos_apoyo": ["Q1"] if k == 1 else [],
                          "imagen_sensorial": f"el humo del beat {k}", "pregunta_abierta": "¿quién cerró?",
                          "cierre": "", "palabras_objetivo": 55 if cap in (1, 7) else 62})
            k += 1
    caps = [{"chapter_number": n, "role": "hook" if n == 1 else "reveal_outro" if n == 7 else "development",
             "render_engine": "flux", "duration_seconds": 45 if n in (1, 7) else 105, "narrative_intent": "setup",
             "evidence_ids": [f"D{n}"], "cliffhanger": "", "pantalla_ids": ["D13"] if n == 6 else [],
             "palabras_objetivo": 55 if n in (1, 7) else 125} for n in range(1, 8)]
    return {"beats": beats, "caps": caps, "pico": {"beat": 8, "id": "D8"}, "humano": {"id": "P1", "nombre": "Liz Torres",
            "rol": "Sobreviviente", "colectivo": False}, "antagonista": {"id": "P2"}, "promesa_gancho": "quién cerró",
            "cierre_humano": "Liz", "a_pantalla": [], "_pool_plan": {}, "prompt_version": "x",
            "instrucciones_guionista": ["Q1 (de Liz Torres) está SIN VERIFICAR: se usa sin su nombre."]}


def _parrafos(esc, text=FRASE):
    return [{"beat": b["n"], "cap": b["cap"], "texto": f"{text}El portón {b['n']} quedó cerrado.", "ids_usados": []}
            for b in esc["beats"]]


# ═══════════════════════════════════════════════════════════════
#  v3 byte-idéntico (con call falso)
# ═══════════════════════════════════════════════════════════════

# sha256 de los 6 archivos que escribe run_guion_v3 con el call falso, medido en b8ff4ef (antes de F11)
# F22: cambian solo cinco mensajes de feedback al modelo (sin nombres de Orleans); con esos textos vueltos atrás el
# hash es el de F21 (76101fbe…): test_module_f22.test_dorado_v3_solo_cambian_los_mensajes_de_f22
# F23: cambian solo las notas de largo de m01d (las bandas de caracteres salen de video_length, §1.2); con esas notas
# vueltas atrás el hash es el de F22e (cf2181e4…): test_module_f23.test_dorado_v3_solo_cambian_las_bandas
V3_GOLDEN = "aaffb169c5832630b055a81e84921794969dde8a50a78b1e99a79463e4ec220c"
V3_GOLDEN_F22 = "cf2181e4a83d166cefd7afb530a4ef495dcefe067b4942ed10f88325dfb2b6bd"
BANDAS_F23 = [("< 280 (corto", "< 255 (corto"), ("< 637 (corto", "< 680 (corto"), ("< 357 (corto", "< 340 (corto")]
V3_GOLDEN_F21 = "76101fbe25c8dec5aaa1f42978d541f2150d778cc30368ef67588061fe79bb6a"


def _fake_pro(prompt, **kw):
    d = kw.get("description") or ""
    esc = _esc()
    if d.startswith("m01b_guionista"):
        return {"parrafos": [{"beat": p["beat"], "texto": p["texto"], "ids_usados": [f"D{p['beat']}"]}
                             for p in _parrafos(esc)]}
    if d == "m01c_editor":
        ps = _parrafos(esc)
        return {"parrafos": [{"beat": p["beat"], "texto": p["texto"].replace("Nadie entendía nada. ", ""),
                              "ids_usados": [f"D{p['beat']}"]} for p in ps],
                "cambios": [{"parrafo": 0, "antes": "a", "despues": "b", "motivo": "corta"}]}
    return {"texto": prompt[-200:]}


def _run_v3(tmp_path, monkeypatch, **kw):
    import gemini_helpers
    monkeypatch.setattr(gemini_helpers, "call_pro_json", _fake_pro)
    monkeypatch.setattr(gemini_helpers, "call_flash_json",
                        lambda p, **k: {"titulos": [f"Título {n}" for n in range(1, 8)]})
    monkeypatch.setattr(f15, "STEPS_DIR", tmp_path)
    monkeypatch.setattr(md, "STEPS_DIR", tmp_path)
    monkeypatch.setattr(f15, "_load_topic_by_id", lambda tid: dict(TOPIC))
    monkeypatch.setattr(f15, "_step_cost", lambda tid, label, fn: fn())
    (tmp_path / "t-f11").mkdir(parents=True, exist_ok=True)
    (tmp_path / "t-f11" / "01a_escaleta.json").write_text(json.dumps(_esc(), ensure_ascii=False), encoding="utf-8")
    import script_engine.m05_narrative as m05
    monkeypatch.setattr(m05, "judge_narration", lambda tid, **k: m05.video_metrics(
        sorted(k["narration"]["chapters"], key=lambda c: c["chapter_number"]), k["pool"], k["skeleton"]))
    out = f15.run_guion_v3("t-f11", **kw)
    h = hashlib.sha256()
    for name in ("01b_guionista_v3.json", "01b_editor_v3.json", "01a_skeleton.json", "01b_narration.json",
                 "01b_narracion_v3.json"):
        h.update((tmp_path / "t-f11" / name).read_bytes())
    h.update(json.dumps(out["juez"], ensure_ascii=False, sort_keys=True).encode("utf-8"))
    return h.hexdigest(), out


def test_v3_byte_identico(tmp_path, monkeypatch):
    digest, _ = _run_v3(tmp_path, monkeypatch)
    assert digest == V3_GOLDEN


def test_v3_sigue_por_su_camino_y_v4_por_el_suyo(monkeypatch):
    called = []
    monkeypatch.setattr(f15, "_load_topic_by_id", lambda tid: {"id": tid, "evidence_pool": {"datos": []}})
    monkeypatch.setattr(f15, "_topic_v3", lambda tid: {"id": tid})
    out = {"particion": {"skeleton": {}, "narration": {}}}
    monkeypatch.setattr(f15, "run_guion_v3", lambda tid: called.append("v3") or out)
    monkeypatch.setattr(f15, "run_guion_v4", lambda tid: called.append("v4") or out)
    f15.process_topic("t", from_step="m01b", stop_after_step="m01b", v3=True)
    f15.process_topic("t", from_step="m01b", stop_after_step="m01b", v3=True, guion="v4")
    assert called == ["v3", "v4"]
    assert f15.is_v4_guion({"guion_version": 4}) and not f15.is_v4_guion({"guion_version": 3})
    assert f15.is_v3_topic({"evidence_pool": {"datos": []}, "guion_version": 4})


# ═══════════════════════════════════════════════════════════════
#  Bloqueantes (§1.2)
# ═══════════════════════════════════════════════════════════════

def _esc_ok():
    esc = _esc()
    for c in esc["caps"]:
        c["palabras_objetivo"] = 50 if c["chapter_number"] in (1, 7) else 100
    return esc


def _codes(bl):
    return sorted(x["codigo"] for x in bl)


def test_texto_limpio_sin_bloqueantes():
    esc = _esc_ok()
    assert g4.bloqueantes(TOPIC, esc, _parrafos(esc)) == []


def test_bloqueantes_a_b_d_e():
    esc = _esc_ok()
    ps = _parrafos(esc)
    ps[1]["texto"] += " Murieron 412 personas."                                                  # a: cifra
    ps[2]["texto"] += " Una sobreviviente relató: «la gente corría y volvían todos porque el portón estaba cerrado»."  # a
    ps[3]["texto"] += " La sobreviviente Daniel Areco miró la puerta."                           # b: es guardia
    ps[4]["texto"] += " En Rosario el fuego dejó 194 muertos."                                   # d (y a)
    ps[5]["texto"] += " Nelson Astigarraga contó: «Cerraron las puertas para que nadie saliera sin pagar»."  # e
    ps[6]["texto"] += " Liz Torres lo contó: «Era como estar dentro de un horno, con las cenizas»."  # humano: no es e
    from researcher_steps import research_v3 as r3            # F21: (b) usa los roles del perfil del caso
    r3.set_vocabulario({"roles_testigo": ["sobreviviente", "cliente"], "roles_antagonista": ["guardia", "dueño"]})
    try:
        bl = g4.bloqueantes(TOPIC, esc, ps, largo="objetivo")   # F15: el default es abierto
    finally:
        r3.set_vocabulario(None)
    by = {(x["codigo"], x["beat"]) for x in bl}
    assert ("a", 2) in by and ("a", 3) in by and ("b", 4) in by and ("d", 5) in by and ("e", 6) in by
    assert not any(x["beat"] == 7 for x in bl)
    e = next(x for x in bl if x["codigo"] == "e")
    assert "Astigarraga" in e["frase"] and e["cap"] == 4
    assert "412" in next(x for x in bl if x["beat"] == 2)["frase"]


def test_estructura_como_el_ajuste_de_ycua():
    esc = _esc_ok()
    ps = [p for p in _parrafos(esc) if p["cap"] != 3]           # se salteó los beats 4 y 5 (cap 3 vacío)
    ms = [x["motivo"] for x in g4.bloqueantes(TOPIC, esc, ps, largo="objetivo")]
    assert ms == ["falta el beat 4 (escalada)", "falta el beat 5 (escalada)", "cap 3 vacío"]
    ps = _parrafos(esc)
    ps[1]["texto"] = "Corto."                                    # cap 2: 1 + 40 palabras < 75
    assert any("cap 2 corto" in x["motivo"] for x in g4.bloqueantes(TOPIC, esc, ps, largo="objetivo"))


STEPS = f15.STEPS_DIR


@pytest.mark.skipif(not (STEPS / "f8s1-ycua-bolanos" / "01b_editor_v3_ajuste.json").exists(),
                    reason="corridas guardadas fuera de git")
def test_corridas_guardadas():
    db = {t["id"]: t for t in json.loads(f15.TOPICS_DB.read_text(encoding="utf-8"))["topics"]
          if t.get("id") in ("ba6c3cac-f7r3", "f8s1-ycua-bolanos")}
    ld = lambda tid, f: json.loads((STEPS / tid / f).read_text(encoding="utf-8"))  # noqa: E731
    aj = g4.bloqueantes(db["f8s1-ycua-bolanos"], ld("f8s1-ycua-bolanos", "01a_escaleta_ajuste.json"),
                        ld("f8s1-ycua-bolanos", "01b_editor_v3_ajuste.json")["parrafos"])
    assert {"falta el beat 4 (escalada)", "falta el beat 5 (escalada)", "cap 3 vacío"} <= {x["motivo"] for x in aj}
    v1 = g4.bloqueantes(db["f8s1-ycua-bolanos"], ld("f8s1-ycua-bolanos", "01a_escaleta_v1.json"),
                        ld("f8s1-ycua-bolanos", "01b_editor_v3_v1.json")["parrafos"])
    assert len(v1) <= 3                                          # §0: «la v1 de Ycuá tendría 0–3»
    assert not any(x["codigo"] == "e" and "Liz Torres" in x["motivo"] for x in v1)


# ═══════════════════════════════════════════════════════════════
#  Prompt, fechas y reparación de una ronda
# ═══════════════════════════════════════════════════════════════

def test_prompt_v4_corto_y_con_marcas_como_dato():
    esc = _esc_ok()
    esc["beats"][1]["datos_apoyo"] = ["Q2", "D50"]
    pr = g4.prompt(TOPIC, esc, "objetivo", version="f11c-1")                 # F15: el v4 de F11c, pedido explícito
    assert "Q1 (de Liz Torres)" not in pr and "INSTRUCCIONES" not in pr and "sonar literal" not in pr
    assert "— Liz Torres · SIN VERIFICAR\n" in pr                       # el humano: sin «(sin nombre)»
    assert "— Nelson Astigarraga · SIN VERIFICAR (sin nombre)" in pr
    assert "[D13] El portón número 13 estaba cerrado · PANTALLA (no va en la voz)" in pr
    assert "ids_usados" not in pr and pr.count("\n") < 120
    assert all(x in g4.system_f11c() for x in g4.OFICIO) and len(g4.OFICIO) == 8   # F11c: el oficio va en el sistema


def test_fechas_repetidas_con_dia_de_la_semana():
    ps = [{"beat": 1, "cap": 1, "texto": "El 29 de agosto de 2005 llegó el agua."},
          {"beat": 2, "cap": 2, "texto": "Del lunes 29 de agosto quedó poco. El 29 de agosto de 2005 nadie salió."}]
    out, ch = g4.replace_repeated_dates(ps, "2005-08-29")
    assert out[0]["texto"] == ps[0]["texto"]
    assert out[1]["texto"] == "De ese lunes quedó poco. Ese lunes nadie salió."
    assert len(ch) == 2
    assert g4.replace_repeated_dates(ps, None)[0] == ps


def test_regenerar_cap_vacio_inserta_en_su_lugar():
    esc = _esc_ok()
    ps = [p for p in _parrafos(esc) if p["cap"] != 3]
    new = md.regenerate_cap_v3(TOPIC, esc, ps, 3, POOL, notas=["falta"], permitidos=["D4", "D5"], attempts=1,
                               call=lambda p, **k: {"parrafos": [{"beat": 4, "texto": "El portón 4 quedó cerrado."},
                                                                 {"beat": 5, "texto": "El portón 5 quedó cerrado."}]})
    assert [p["beat"] for p in new] == list(range(1, 13)) and [p["cap"] for p in new][3:5] == [3, 3]


def test_reparacion_una_sola_ronda_sin_volver_al_guionista():
    esc = _esc_ok()
    ps = [p for p in _parrafos(esc) if p["cap"] != 3]
    ps[0]["texto"] += " Murieron 412 personas."
    calls = []

    def fake(prompt, **kw):
        calls.append(kw.get("description"))
        if (kw.get("description") or "").startswith("m01d regenerate_cap"):
            return {"parrafos": [{"beat": 9, "texto": "x"}]}         # beat de otro cap → se rechaza
        if kw.get("description") == "guion_v4 editar frase":
            return {"texto": prompt.split("PÁRRAFO:\n")[1].replace(" Murieron 412 personas.", "")}
        if kw.get("description") == "guion_v4 editor":
            return {"parrafos": [], "cambios": []}
        raise AssertionError(kw.get("description"))
    r = g4.reparar(TOPIC, esc, ps, call=fake, editor=True)   # F27: el editor m01c, solo con editor=True
    assert "guion_v4 guionista" not in calls
    assert calls.count("m01d regenerate_cap 3") == 1                   # 1 intento, sin segunda ronda
    assert calls.count("guion_v4 editar frase") == 1 and calls[-1] == "guion_v4 editor"
    assert r["parada"] and {x["motivo"] for x in r["bloqueantes_despues"]} >= {"cap 3 vacío"}
    assert not any(x["codigo"] == "a" for x in r["bloqueantes_despues"])
    assert all(p["ids_usados"] == [f"D{p['beat']}"] or p["ids_usados"] for p in r["parrafos"])
