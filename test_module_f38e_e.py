"""
test_module_f38e_e.py — F38e §E: `m01d_particion.titles()` con el pedido de la prueba 2 (letra por letra) y `lines`
con función, qué se ve, pregunta que abre, « · pico» (desde esc["pico"]["beat"]) y «termina (no lo cuentes)».
Sin red: `call` inyectado. Lee de lab/ (nunca de data/) o usa escaletas sintéticas.
"""
from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from script_engine import m01d_particion as md

ROOT = Path(__file__).resolve().parent
MD = ROOT / "lab/hyperframes/f38/PRUEBA2_prompt_titulos.md"
ESC_VAJONT = ROOT / "lab/hyperframes/f38/b2/fase1/f8s3-vajont/01a_escaleta.json"

SIETE = ["El agua", "La orden", "El viento", "La marea", "El techo", "El sol", "La lista"]


def _esc(pico_beat: int = 5) -> dict:
    """Escaleta sintética: 7 caps, 2 beats por cap salvo el 1 y el 7 (1 beat); pico en `pico_beat`."""
    beats, k = [], 1
    for cap in range(1, 8):
        for _ in range(1 if cap in (1, 7) else 2):
            beats.append({"n": k, "cap": cap, "funcion": "gancho" if cap == 1 else "cierre" if cap == 7 else "escalada",
                          "imagen_sensorial": f"imagen del beat {k}", "pregunta_abierta": f"¿pregunta del beat {k}?",
                          "cierre": f"cierre del beat {k}.", "dato_central": f"D{k}", "datos_apoyo": []})
            k += 1
    return {"beats": beats, "caps": [], "pico": {"beat": pico_beat}}


def _captura(esc: dict, resp: dict | None = None) -> tuple[str, list[str], str]:
    seen: dict = {}

    def call(prompt, **kw):
        seen["prompt"], seen["kw"] = prompt, kw
        return resp if resp is not None else {"titulos": list(SIETE)}
    ts, src = md.titles(esc, call=call)
    assert seen["kw"]["response_schema"] is md.TITLES_SCHEMA
    return seen["prompt"], ts, src


def _bloque_md() -> str:
    m = re.search(r"## Pedido nuevo, entero\n```\n(.*?)\n```", MD.read_text(encoding="utf-8"), re.S)
    assert m
    return m.group(1)


def test_literal_del_codigo_es_el_bloque_del_md_letra_por_letra():
    bloque = _bloque_md()
    assert md.PEDIDO_TITULOS == bloque
    assert hashlib.md5(bloque.encode("utf-8")).hexdigest() == "0c3fe5599f500ce523c77aac0e328597"
    assert sorted(set(re.findall(r"\{[^{}]*\}", bloque))) == ["{TITLE_MAX_WORDS}", "{lines}"]


def test_el_pedido_contiene_el_texto_del_md_con_el_tope_de_palabras():
    prompt, _, _ = _captura(_esc())
    cabeza = md.PEDIDO_TITULOS.split("{lines}")[0].replace("{TITLE_MAX_WORDS}", str(md.TITLE_MAX_WORDS))
    assert prompt.startswith(cabeza)
    assert f"de 2 a {md.TITLE_MAX_WORDS} palabras" in prompt
    assert "sin contar cómo termina" in prompt and "qué pregunta abren" in prompt
    assert "Basate en lo que se ve" not in prompt          # el pedido viejo se fue


def test_lines_tiene_funcion_se_ve_y_pregunta_por_beat():
    esc = _esc()
    prompt, _, _ = _captura(esc)
    for b in esc["beats"]:
        assert f"beat {b['n']} {b['funcion']}" in prompt
        assert f"se ve: {b['imagen_sensorial']} · pregunta que abre: {b['pregunta_abierta']}" in prompt
    assert prompt.count("CAP ") == 7


def test_pico_solo_en_el_beat_de_esc_pico_beat():
    esc = _esc(pico_beat=5)
    prompt, _, _ = _captura(esc)
    assert prompt.count(" · pico") == 1
    assert "  beat 5 escalada · pico: se ve:" in prompt
    esc2 = _esc(pico_beat=8)
    prompt2, _, _ = _captura(esc2)
    assert prompt2.count(" · pico") == 1 and "  beat 8 escalada · pico: se ve:" in prompt2
    sin_pico = _esc()
    sin_pico.pop("pico")
    prompt3, _, _ = _captura(sin_pico)
    assert " · pico" not in prompt3


def test_termina_no_lo_cuentes_con_el_cierre_del_ultimo_beat_de_cada_cap():
    esc = _esc()
    prompt, _, _ = _captura(esc)
    lines = prompt.splitlines()
    assert sum(1 for x in lines if x.startswith("  termina (no lo cuentes): ")) == 7
    for n in range(1, 8):
        ultimo = [b for b in esc["beats"] if b["cap"] == n][-1]
        assert f"  termina (no lo cuentes): {ultimo['cierre']}" in lines
        primero = [b for b in esc["beats"] if b["cap"] == n][0]
        if primero is not ultimo:
            assert f"  termina (no lo cuentes): {primero['cierre']}" not in lines
    # orden: el «termina» de cada cap va después de sus beats y antes del CAP siguiente
    for n in range(1, 7):
        i_cap, i_next = lines.index(f"CAP {n}:"), lines.index(f"CAP {n + 1}:")
        assert lines[i_next - 1].startswith("  termina (no lo cuentes): ")
        assert i_cap < i_next - 1


def test_pedido_de_vajont_desde_la_escaleta_congelada_en_lab():
    esc = json.loads(ESC_VAJONT.read_text(encoding="utf-8"))
    assert esc["pico"]["beat"] == 10 and not any("pico" in b for b in esc["beats"])    # abierto e7 de F38e-0
    prompt, _, _ = _captura(esc)
    assert prompt.count(" · pico") == 1 and "  beat 10 pico · pico: se ve:" in prompt
    assert prompt.count("  termina (no lo cuentes): ") == 7
    assert prompt.startswith(md.PEDIDO_TITULOS.split("{TITLE_MAX_WORDS}")[0])


def test_validacion_y_respaldo_intactos():
    esc = _esc()
    _, ts, src = _captura(esc)
    assert src == "flash" and ts == SIETE
    # un título con dígito → ese cap al respaldo (imagen sensorial del primer beat), src «mixto»
    con_digito = list(SIETE)
    con_digito[2] = "Los 517 muertos"
    _, ts2, src2 = _captura(esc, {"titulos": con_digito})
    assert src2 == "mixto" and ts2[2] == "Imagen del beat 4" and ts2[0] == "El agua"
    # un título con «?» → respaldo en ese cap
    con_pregunta = list(SIETE)
    con_pregunta[0] = "¿Qué cayó?"
    _, ts3, src3 = _captura(esc, {"titulos": con_pregunta})
    assert src3 == "mixto" and ts3[0] == "Imagen del beat 1"
    # 6 palabras → respaldo en ese cap
    largo = list(SIETE)
    largo[6] = "una dos tres cuatro cinco seis"
    _, ts4, src4 = _captura(esc, {"titulos": largo})
    assert src4 == "mixto" and ts4[6] == "Imagen del beat 12"
    # 6 títulos → todo al respaldo
    _, ts5, src5 = _captura(esc, {"titulos": SIETE[:6]})
    assert src5 == "respaldo" and len(ts5) == 7 and ts5 == [md._title_fallback([b for b in esc["beats"] if b["cap"] == n])
                                                             for n in range(1, 8)]
    # comillas y «» se limpian como antes
    _, ts6, src6 = _captura(esc, {"titulos": ['"El agua"', "«La orden»"] + SIETE[2:]})
    assert src6 == "flash" and ts6[:2] == ["El agua", "La orden"]
    # el call explota → respaldo
    boom = lambda prompt, **kw: (_ for _ in ()).throw(RuntimeError("sin red"))
    ts7, src7 = md.titles(esc, call=boom)
    assert src7 == "respaldo" and len(ts7) == 7
