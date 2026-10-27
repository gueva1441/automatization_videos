"""
script_engine/m01e_pantalla.py — F36 §C: el guion de pantalla EN PAPEL (DECISIONES 2026-10-26 19:54: «el autor de la
pantalla va a Fase 1»). Corre en Fase 1 después de m01d_particion y antes de la voz (fase1_5.run_guion_v3/v4, con su
costo en 01_v3_costos.json como los demás pasos) o suelto: `python -m script_engine.m01e_pantalla <topic>`.

    entrada    (§C.1, una para todo el video) por cap el título (01a_skeleton) y sus oraciones numeradas, partidas con
               el mismo corte de la voz (voz_utils.oraciones_de_texto) desde los párrafos de 01b_narracion_v3, cada una
               con su beat y `caben` (palabras × segundos por palabra del narrador —F37: derivado de sus voces,
               voz_utils.seg_por_palabra— × 15 cps, sin pasar de callout_dur_max: una estimación; la medida real es
               de Fase 2);
               los beats de la escaleta (n, función, pico sí/no, dato central, apoyo, cierre); el archivo = el pool
               completo con cifra, fecha o cita (D con número, T, Q) y las personas (P), cada ítem con id, texto, fuente,
               fecha (F37 §A.1a; «desconocida» si no tiene), las citas autor, rol y testimonio, y `beats_que_lo_cuentan`
               (los beats cuyo dato central o de apoyo es el ítem); F38c §A.1: el que la escaleta dejó para la pantalla
               lleva además `a_pantalla` {beat, por_que} (campo propio, no entra en `beats_que_lo_cuentan`);
               el vocabulario `sellos_clima` del perfil.
    llamada    UNA a Sonnet 5.5 (medium) con el prompt literal de §C.2 (PANTALLA_SYSTEM; F37: el gancho en las primeras
               oraciones, m01e-2; el USER = el JSON de entrada + «Formato de salida: …», con el `tipo` de cada descarte),
               tope del perfil (`costos.m01e_tope_usd`, tope_usd) contando las dos llamadas, caché por md5 de la entrada
               y la versión del prompt. F37 §A.5: un reintento si el JSON no parsea o si la validación deja algún motivo
               (ficha caída, pregunta al autor, descarte «la voz lo dice» falso, pico sin ficha), con todos juntos. Dos
               respuestas sin JSON → PARADA (la cruda queda en 01e_pantalla.raw.json).
               F38 §A.1: el reintento es PARCIAL: ve el papel completo del intento 1 como contexto, pero devuelve solo
               `cambios` de los beats con motivo; el código los fusiona por (cap, beat) y lo demás queda congelado.
               F38d §A.1: el reintento parcial da VUELTAS mientras haya motivos, no sean los mismos de la vuelta
               anterior y entre en el tope; lo nuevo que aparece en una vuelta se pregunta en la siguiente y solo al
               cerrar corta lo que siga sin preguntar (`reintento.vueltas`, `cierre`, `cortados_al_cierre`).
    respaldo   F38e §C: prompt m01e-6 (el de la prueba 1, letra por letra: el dato con las palabras del autor; los hechos
               en un `respaldo` literal del ítem); el respaldo tiene que ser fragmento del texto del ítem (regla
               `respaldo`) y el candado mira cifras, nombres y años contra él; en una cita, el `autor` del modelo se
               muestra si sus nombres propios están en el archivo (`autor_mostrado`, `autor_origen`), si no el del archivo.
    validar    (§C.3, sin tiempos ni fotos, con los filtros de pantalla_filtros) por ficha: anclaje (cap, beat, ítem y
               oración que existen; la oración es del beat), formato (etiqueta en 1 línea y dato en 2, gfx_project.
               ficha_medida), F37 §A.1b fecha del relato (el año del ítem contra el último año que dijo la voz) y §A.1c
               cita sin fecha (su autor en la oración o una vecina), candado (números, nombres y años literales en el
               texto del ítem; en el gancho vale la voz de todo el video), no dicho (oración ancla ± 1; en el gancho,
               una cifra del dato que la voz dice en cualquier oración del video: F40 §A, ya no corta en seco) y
               spoiler (la narración posterior del cap y de los caps siguientes)
               —F37 §A.4: su coincidencia se le pregunta al autor en el reintento, que decide—, el mismo dato una sola
               vez en el video, `caben`. Los descartes «voz_lo_dice» se verifican (§A.2) y los picos sin ficha se
               nombran (§A.3b). Por sello: palabra de la lista, no es palabra de la voz del cap, no repetida en el video, uno por
               beat. Lo que cae va a `descartados` con la regla y el motivo.
    estilo     (§C.1) lo pone el código por tipo de dato: Q → cita (con autor), P → nombre, D/T cuya etiqueta (o el
               `por_que` de su `a_pantalla`) nombra una carta, un acta, un informe o un documento → papel, resto → normal.
Salida en el directorio del topic de Fase 1 (aclaración 1: el que leen gfx_realizador y el rotulista): 01e_pantalla.json
(lo consume Fase 2), 01e_pantalla.md (una línea por beat y lo que cayó, para Omar) y 01e_pantalla.raw.json.
"""
from __future__ import annotations

import hashlib
import json
import re
import sys
import time
from pathlib import Path
from typing import Any, Callable

if __name__ == "__main__" and __package__ in (None, ""):          # suelto: python script_engine/m01e_pantalla.py <topic>
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from script_engine import evidence as ev                           # noqa: E402
from script_engine.voz_utils import (_analiza, _PARTICULAS, _palabra_en, _raiz_en, anio_de, anios_de,   # noqa: E402
                                     anios_dichos, dice_anio, misma_cifra, nombre_inicial, nombres, numero_en, numeros,
                                     oraciones_de_texto, palabras, palabras_de_contenido, seg_por_palabra)

PROMPT_VERSION = "m01e-6"       # F38e §C.1: el SYSTEM es el bloque «Prompt nuevo (m01e-6-prueba), entero» de lab/hyperframes/f38/PRUEBA1_prompt_rotulos.md, letra por letra (md5 7d2ccdd28055d6e621d1d251a0fe8bb7, medido en F38e-0; lo escribió lab/hyperframes/f38e/c/c1_prompt_del_md.py); §C.2: `respaldo` y `autor` en el formato · antes m01e-5 (F38d §A.2: «caben» con el autor de la cita)
MODELO = "claude-sonnet-5-5"
EFFORT = "medium"
TOPE_USD_RESPALDO = 1.00        # DECISIONES: pedido de Omar F37 («TOPE_USD sale al perfil con valor 1.00»); el valor vive en el perfil (costos.m01e_tope_usd)
SEG_POR_PALABRA_RESPALDO = 0.35  # medido: Vajont ch04 (F36); solo si no hay ninguna voz del narrador (F37 §0: se deriva, voz_utils.seg_por_palabra)
OUT_TOKENS_PEOR = 16_000        # derivado: el peor caso de salida del rotulista de gfx (razonamiento + JSON); en el reintento, la salida real del primero si fue más
ARCHIVO = "01e_pantalla"
ESTILOS = ("normal", "papel", "cita", "nombre")
TIPOS_DESCARTE = ("voz_lo_dice", "spoiler", "repetido", "otro")      # F37 §A.2 (formato)


def tope_usd() -> tuple[float, str]:
    """F37 §0: el tope de la llamada (con su reintento) es del perfil del canal, `costos.m01e_tope_usd` (gfx_profiles,
    fuera de git: la clave la agrega Omar); sin la clave, el respaldo del pedido de Omar. (valor, de dónde)."""
    from gfx_config import ACTIVE_PROFILE
    v = (ACTIVE_PROFILE.get("costos") or {}).get("m01e_tope_usd")
    if isinstance(v, (int, float)) and v > 0:
        return float(v), "perfil (costos.m01e_tope_usd)"
    return TOPE_USD_RESPALDO, "respaldo (el perfil no trae costos.m01e_tope_usd)"


def velocidad(seg: dict[str, Any] | None = None) -> dict[str, Any]:
    """F37 §0: segundos por palabra del narrador (voz_utils.seg_por_palabra) o el respaldo, con su origen."""
    seg = seg if seg is not None else seg_por_palabra()
    if seg and seg.get("valor"):
        return {**seg, "origen": f"mediana de {seg['oraciones']} oraciones de {seg['caps']} caps del narrador {seg['voz']}"}
    return {"valor": SEG_POR_PALABRA_RESPALDO, "origen": "respaldo (no hay voces generadas del narrador)"}


# ═══════════════════════ prompt (F38e §C.1: PRUEBA1_prompt_rotulos.md, literal; antes HANDOFF_F36_C_D §C.2) ═══════════════════════

PANTALLA_SYSTEM = """Sos el rotulista de un documental de historia oscura en español. Recibís la narración completa de un video (7 capítulos, oraciones numeradas), la escaleta (qué cuenta cada beat y cuál es el pico de cada capítulo), el archivo del caso (datos con cifra, fecha, cita o persona, con su fuente) y una lista de palabras de clima. Escribís lo que va en pantalla para todo el video, de una vez.

Reglas de todo texto en pantalla:
(a) suma o aclara lo que la voz cuenta en esa oración: un hecho del archivo que la voz no dice, o lo que la voz cuenta puesto en una cifra, una persona o una consecuencia; nunca repite la frase de la voz;
(b) va sobre la oración que habla de ese asunto: elegí la oración ancla y la palabra de la oración donde debe aparecer;
(c) no adelanta nada que la narración cuente después, en ese capítulo o en los siguientes;
(d) se entiende solo, en 3 segundos, sin escuchar la voz, y le importa a quien mira: si necesita la voz para entenderse o suena a informe técnico, no sirve.

Qué podés poner:
- FICHA: como máximo una por beat, y puede no haber. La escribís con tus palabras, para quien mira. Etiqueta: una línea corta que diga qué es o por qué importa, en palabras de todos los días, sin el año de publicación de la fuente. Dato: UNA línea corta con el hecho. Las palabras son libres; los hechos no: cada cifra, nombre propio y año de la etiqueta y del dato tiene que estar en el `respaldo`, que es un fragmento copiado letra por letra del texto del dato del archivo que elegiste. No conviertas unidades ni hagas cuentas; una cifra larga podés redondearla con «más de» (hacia abajo) o «casi» (hacia arriba). Una comparación, solo si está en el archivo. Etiqueta + dato —y en una cita, también el autor y 5 caracteres de comillas y raya— no pueden pasar de los caracteres que caben en la oración ancla (`caben`); si no caben, elegí otra oración o un dato más corto. Para una cita (Q), el dato es la frase literal del archivo, recortada pero sin cambiar palabras; el autor va en español, como lo entiende quien mira (nombre, o cargo o institución).
- SELLO DE CLIMA: como máximo uno por beat, y puede no haber. Una palabra de la lista que nombre lo que se siente en ese momento del relato. Nunca una palabra que la voz diga en ese capítulo, y nunca la misma palabra dos veces en el video. Elegí la oración donde cae.
- RELOJ: por capítulo, las fechas completas (día, mes y año) que la voz dice, con la oración donde las dice.

Prioridades: en el beat pico del capítulo, el dato marcado como central por la escaleta; en el gancho (capítulo 1), cualquier dato del archivo que la voz no diga en todo el video y que haga quedarse a quien mira: el gancho nunca queda sin ficha. Los datos marcados con tu beat son los que la escaleta cuenta ahí; los demás son el resto del archivo: usalos si suman más y no adelantan nada. Un mismo dato una sola vez en el video. Si dudás entre dos, el que se entiende solo y más le importa a quien mira.

Devolvé solo JSON con el formato pedido, con `aporta` (una línea: qué suma que la voz no dice) y `respaldo` por ficha, y `descartados` con motivo."""

# §C.1: el esquema de salida (por cap y beat; relojes por cap; descartados). Sin `estilo`: lo pone el código.
# F37 §A.2: cada descarte dice de qué tipo es (cambio de formato, no de estilo): el código verifica «voz_lo_dice».
# F38e §C.2: `respaldo` (el fragmento literal del texto del ítem, como en la prueba 1) después de `texto`, y `autor`
# (solo en una cita: en español, como lo entiende quien mira; null en las demás) después de `respaldo`.
FORMATO_SALIDA = ('{"beats": [{"cap": "ch03", "beat": 5, "ficha": {"pool_id": "D49", "sentence_idx": 17, '
                  '"palabra": "fisura", "etiqueta": "ANCHO DE LA FISURA", "texto": "Más de 1 metro", "respaldo": "…", '
                  '"autor": "…" | null, "aporta": "…"} | '
                  'null, "sello": {"palabra": "AVISO", "sentence_idx": 3} | null}], "relojes": [{"cap": "ch03", '
                  '"sentence_idx": 4, "fecha": "9 OCT 1963"}], '
                  '"descartados": [{"pool_id": "…", "tipo": "voz_lo_dice" | "spoiler" | "repetido" | "otro", '
                  '"motivo": "…"}]}')

# F38 §A.1: el formato del reintento parcial (solo los beats con motivo; la clave que no se cambia no va; null la borra).
FORMATO_REINTENTO = ('{"cambios": [{"cap": "ch03", "beat": 5, "ficha": {"pool_id": "D49", "sentence_idx": 17, '
                     '"palabra": "fisura", "etiqueta": "ANCHO DE LA FISURA", "texto": "Más de 1 metro", "respaldo": "…", '
                     '"autor": "…" | null, "aporta": "…"} '
                     '| null, "sello": {"palabra": "AVISO", "sentence_idx": 3} | null}]}')
REINTENTO_PARCIAL = ("Devolvé solo JSON con `cambios` para los beats de esta lista: {beats}. Cada cambio nombra su cap y "
                     "su beat; `ficha` o `sello` con valor la reemplazan, con null la borran, y si no la cambiás no la "
                     "pongas. Todo lo demás de tu respuesta anterior queda como está: un cambio en otro beat se ignora.")


def prompt_md5() -> str:
    """md5 del prompt literal (SYSTEM + la línea del formato), para el reporte. F38: + el formato del reintento."""
    return hashlib.md5((PANTALLA_SYSTEM + "\n\n" + FORMATO_SALIDA + "\n\n" + FORMATO_REINTENTO + "\n\n"
                        + REINTENTO_PARCIAL).encode("utf-8")).hexdigest()


def pedido(ent: dict[str, Any]) -> str:
    """El USER: el JSON de entrada de §C.1 y, al final, la línea del formato."""
    return json.dumps(_para_modelo(ent), ensure_ascii=False) + "\n\nFormato de salida: " + FORMATO_SALIDA


# ═══════════════════════ entrada (§C.1) ═══════════════════════

def cap_id(n: int) -> str:
    return f"ch{int(n):02d}"


def _texto_item(it: dict[str, Any]) -> str:
    """El texto del ítem que ve el modelo y contra el que corre el candado (el mismo)."""
    k = it["_kind"]
    if k == "cronologia":
        cuando = str(it.get("fecha") or "") + (f", hora {it['hora']}" if it.get("hora") else "")
        return f"{ev.text_of(it)} (fecha {cuando})" if cuando else ev.text_of(it)
    if k == "personajes":
        return f"{it.get('nombre') or ''} — {it.get('rol') or ''}".strip(" —")
    return re.sub(r"\s+", " ", ev.text_of(it)).strip()


def _tipo(it: dict[str, Any]) -> str | None:
    """D con número, T, Q, P (§C.1); el resto del pool (lugares, D sin cifra) no entra al archivo."""
    k = it["_kind"]
    if k == "datos":
        return "D" if numeros(ev.text_of(it)) else None
    return {"cronologia": "T", "citas": "Q", "personajes": "P"}.get(k)


def cargar(topic_id: str, steps_dir: Path, pool: dict | None = None) -> dict[str, Any]:
    """Los archivos de Fase 1 del topic (aclaración 1: los que leen gfx_realizador y el rotulista): escaleta, párrafos
    por cap y beat (01b_narracion_v3), títulos de la partición (01a_skeleton) y el pool (00_pool_v3, o el que se pasa)."""
    sd = Path(steps_dir) / topic_id

    def lee(nombre: str) -> dict:
        return json.loads((sd / nombre).read_text(encoding="utf-8"))
    sk = lee("01a_skeleton.json")
    return {"topic_id": topic_id, "dir": sd, "escaleta": lee("01a_escaleta.json"),
            "parrafos": lee("01b_narracion_v3.json").get("parrafos") or [],
            "titulos": {int(c["chapter_number"]): str(c.get("title") or "") for c in sk.get("chapters") or []},
            "pool": pool if pool is not None else lee("00_pool_v3.json")}


def caben_en(texto: str, seg: float) -> int:
    """Caracteres que caben en una ficha anclada a la oración: su duración estimada (palabras × segundos por palabra
    del narrador) × 15 cps, nunca más que lo que se lee en `callout_dur_max` (F37 §B.2: la ficha dura su lectura y no
    pasa de callout_dur_max, identidad F3 del perfil). Fase 1 no tiene escenas: la medida real es de Fase 2."""
    from gfx_config import gfx_rules
    from script_engine.pantalla_colocar import LECTURA_CPS
    return int(min(len(palabras(texto)) * seg, float(gfx_rules.callout_dur_max)) * LECTURA_CPS)


def entrada(carga: dict[str, Any], vocabulario: list[str], seg: dict[str, Any] | None = None) -> dict[str, Any]:
    """La entrada de §C.1 (con lo que el código necesita para validar; `_para_modelo` saca lo que el modelo no ve).
    F37: `seg` = la velocidad del narrador (voz_utils.seg_por_palabra; None → se deriva acá); cada ítem del archivo
    lleva su `fecha` (o «desconocida») y las citas su `rol` y si son `testimonio`, tal como están en el pool (§A.1a)."""
    from script_engine.gfx_realizador import beat_de_pantalla
    from script_engine.music_intensity import beat_pico_de_cap
    esc, pars = carga["escaleta"], carga["parrafos"]
    vel = velocidad(seg)
    caps: list[dict[str, Any]] = []
    for n in sorted({int(p["cap"]) for p in pars}):
        ors = []
        for p in [p for p in pars if int(p["cap"]) == n]:
            for t in oraciones_de_texto(p["texto"]):
                ors.append({"idx": len(ors), "beat": int(p.get("beat") or 0), "texto": t,
                            "caben": caben_en(t, vel["valor"])})
        caps.append({"cap": cap_id(n), "n": n, "titulo": carga["titulos"].get(n, ""), "oraciones": ors})
    beats_esc = sorted(esc.get("beats") or [], key=lambda b: int(b["n"]))
    picos = {}
    for n in {int(b["cap"]) for b in beats_esc}:
        bc = [b for b in beats_esc if int(b["cap"]) == n]
        picos[n] = beat_pico_de_cap(bc, (esc.get("pico") or {}).get("beat"))
    beats = [{"n": int(b["n"]), "cap": cap_id(b["cap"]), "funcion": str(b.get("funcion") or ""),
              "pico": int(b["n"]) == picos.get(int(b["cap"])), "dato_central": str(b.get("dato_central") or ""),
              "apoyo": [str(x) for x in b.get("datos_apoyo") or []], "cierre": str(b.get("cierre") or "").strip()}
             for b in beats_esc]
    cuentan: dict[str, list[int]] = {}
    for b in beats:
        for i in [b["dato_central"]] + b["apoyo"]:
            if i:
                cuentan.setdefault(i, []).append(b["n"])
    # F38c §A.1: el `a_pantalla` de la escaleta va en un campo propio del ítem ({beat, por_que}), no en `cuentan` (esa
    # marca es «la voz lo cuenta ahí»: dato_central/datos_apoyo); si además es dato de un beat, queda en los dos
    a_pant: dict[str, dict[str, Any]] = {}
    for a in esc.get("a_pantalla") or []:                 # el `a_pantalla` de la escaleta, en su beat
        bc = [{"n": int(b["n"]), "dato_central": str(b.get("dato_central") or ""),
               "datos_apoyo": [str(x) for x in b.get("datos_apoyo") or []],
               "texto": " ".join(p["texto"] for p in pars if int(p.get("beat") or 0) == int(b["n"])),
               "campos": " ".join(str(b.get(c) or "") for c in ("emocion", "imagen_sensorial", "pregunta_abierta", "cierre"))}
              for b in beats_esc if int(b["cap"]) == int(a.get("cap") or 0)]
        nb, _ = beat_de_pantalla(a, bc)
        a_pant.setdefault(str(a.get("id")), {"beat": nb, "por_que": str(a.get("por_que") or "")})
    archivo = []
    todos = ev.items(carga["pool"])
    for i, it in todos.items():
        t = _tipo(it)
        if t is None:
            continue
        x = {"id": i, "texto": _texto_item(it), "fuente": str(it.get("fuente") or ""),
             "fecha": str(it.get("fecha") or "") or "desconocida", "beats_que_lo_cuentan": sorted(cuentan.get(i) or [])}
        if t == "Q":
            x["autor"] = str(it.get("autor") or "")
            x["rol"] = str(it.get("rol") or "")
            x["testimonio"] = "sí" if it.get("testimonio") else "no"
        if i in a_pant:                                   # F38c §A.1: data del ítem, no regla (el prompt no cambia)
            x["a_pantalla"] = dict(a_pant[i])
        archivo.append(x)
    return {"topic_id": carga["topic_id"], "caps": caps, "beats": beats, "archivo": archivo,
            "clima": list(vocabulario), "a_pantalla": {str(a.get("id")): str(a.get("por_que") or "")
                                                       for a in esc.get("a_pantalla") or []},
            "seg_por_palabra": vel, "anios": anios_de([x.get("fecha") for x in todos.values()])}


def _para_modelo(ent: dict[str, Any]) -> dict[str, Any]:
    return {"caps": [{"cap": c["cap"], "titulo": c["titulo"],
                      "oraciones": [{k: s[k] for k in ("idx", "beat", "texto", "caben")} for s in c["oraciones"]]}
                     for c in ent["caps"]],
            "beats": ent["beats"], "archivo": ent["archivo"], "clima": ent["clima"]}


def entrada_md5(ent: dict[str, Any]) -> str:
    return hashlib.md5(pedido(ent).encode("utf-8")).hexdigest()


# ═══════════════════════ validación en papel (§C.3) ═══════════════════════

def estilo_de(pool_id: str, etiqueta: str, por_que: str = "") -> str:
    """§C.1: el estilo sale del tipo de dato, sin modelo. Lectura declarada de «D/T que pide_documento»: la etiqueta de la
    ficha (lo que es: «ACTA DEL CONSEJO SUPERIOR») o el `por_que` de su `a_pantalla` nombran una carta, un acta, un
    informe o un documento (pantalla_filtros.pide_documento, F32 §B.4)."""
    from script_engine.pantalla_filtros import pide_documento
    t = str(pool_id)[:1].upper()
    if t == "Q":
        return "cita"
    if t == "P":
        return "nombre"
    return "papel" if pide_documento(f"{etiqueta} {por_que}") else "normal"


TIPO_DE_ESTILO = {"normal": "hecho", "papel": "documento", "cita": "cita", "nombre": "persona"}   # el de los filtros


def _voz_video(ent: dict[str, Any]) -> list[str]:
    return [s["texto"] for c in ent["caps"] for s in c["oraciones"]]


def momentos(ent: dict[str, Any]) -> dict[tuple[str, int], int | None]:
    """F37 §A.1b: el momento del relato en cada oración = el último año que la voz dijo en el video hasta ella (incluida;
    arrastra de los caps anteriores; años en cifras o en letras, voz_utils.anios_dichos). Por año: las fechas relativas
    («tres días después») no se parsean. None mientras la voz no dijo ningún año."""
    out: dict[tuple[str, int], int | None] = {}
    ultimo = None
    for c in ent["caps"]:
        for s in c["oraciones"]:
            ys = anios_dichos(s["texto"], ent.get("anios"))
            if ys:
                ultimo = ys[-1]
            out[(c["cap"], s["idx"])] = ultimo
    return out


def autor_en(autor: str, rol: str, texto: str) -> bool:
    """F37 §A.1c: ¿el autor de una cita aparece en el texto? Por su nombre (los nombres propios del autor, sin lo que va
    entre paréntesis, que es una descripción: «Ingeniero jefe (sucesor de Semenza)» no es Semenza) o por su rol (todas
    sus palabras de contenido, por raíz)."""
    cabeza = re.sub(r"\([^)]*\)", " ", autor or "")
    nms = [n for n in list(nombre_inicial(cabeza)) + nombres(cabeza) if n.lower() not in _PARTICULAS]
    if any(_palabra_en(n, texto) for n in nms):
        return True
    pr = palabras_de_contenido(rol or "")
    return bool(pr) and all(_raiz_en(w, texto) for w in pr)


def _nombres_del_autor(autor: str) -> list[str]:
    """F38e §C.4: los nombres propios del `autor` que escribe el modelo: los que no abren la frase (voz_utils.nombres,
    que no ve el que abre: «Municipio de Erto y Casso» → Erto, Casso) y, si la frase abre con un nombre seguido de otro
    nombre propio (nombre y apellido: «Pietro Leone»), también el que abre; el que abre seguido de una palabra común
    («Municipio de…», «Presidente del…») dice qué es, no es un nombre."""
    toks = nombres(autor)
    ws = [re.sub(r"^[«\"“(]+|[.,;:!?»\"”)·]+$", "", w) for w in palabras(autor)]
    if len(ws) >= 2 and ws[0] and ws[1] and ws[0][0].isupper() and ws[1][0].isupper() and len(ws[0]) >= 2 \
            and ws[0].lower() not in _PARTICULAS and ws[0] not in toks:
        toks = [ws[0]] + toks
    return toks


def autor_mostrado(autor_modelo: str, x: dict[str, Any]) -> tuple[str, str]:
    """F38e §C.4: (el autor que se muestra en una cita, de dónde salió). El del modelo (en español, como lo entiende
    quien mira) si cada uno de sus nombres propios (`_nombres_del_autor`) está en el `autor`, el `rol` o el `texto` del
    ítem del archivo; si no (o si el modelo no dio ninguno), el del archivo, sin cortar. Origen: «modelo» o
    «archivo: <motivo>»."""
    arch = str(x.get("autor") or "")
    a = re.sub(r"\s+", " ", str(autor_modelo or "")).strip()
    if not a:
        return arch, "archivo: el autor no escribió `autor`"
    donde = " ".join(str(x.get(k) or "") for k in ("autor", "rol", "texto"))
    faltan = [n for n in _nombres_del_autor(a) if not _palabra_en(n, donde)]
    if faltan:
        return arch, f"archivo: en «{a}», {faltan} no está en el autor, el rol ni el texto del archivo"
    return a, "modelo"


def _cifras(texto: str, rango: tuple[int, int] | None) -> list[float]:
    """Los valores de las cifras de un texto (voz_utils._analiza: «50 millones» = 5e7, «setecientos mil» = 7e5), sin
    los años del material (el año es la fecha, §A.1b)."""
    return [v for v, _, _ in _analiza(texto)[0]
            if not (rango and float(v).is_integer() and rango[0] <= int(v) <= rango[1])]


def voz_no_lo_dice(it: dict[str, Any], voz: str, rango: tuple[int, int] | None) -> list[str] | None:
    """F37 §A.2: ¿es falso que «la voz lo dice»? Las cifras del ítem (o, si no tiene, sus nombres propios) contra la
    voz: si la voz no dice ninguna, devuelve lo que no dice; si dice alguna, o el ítem no tiene ni cifras ni nombres
    (no se puede verificar), None. Una cita sin cifras no se verifica por nombres: lo que la voz cita es la frase, y la
    frase traducida no se compara palabra por palabra."""
    txt = ev.text_of(it)
    cif = _cifras(txt, rango)
    if cif:
        dichas = set(_cifras(voz, None))
        if any(misma_cifra(str(int(v)) if float(v).is_integer() else repr(float(v)), d)   # F38 §A.4: a la precisión
               for v in cif for d in dichas):                                              # del archivo («1,5» = «uno y medio»)
            return None
        return [n for n in numeros(txt) if not (rango and n.isdigit() and rango[0] <= int(n) <= rango[1])] or \
            [str(v) for v in cif]
    if it.get("_kind") == "citas":
        return None
    nms = nombres(txt)
    if nms and not any(_palabra_en(n, voz) for n in nms):
        return nms
    return None


def _donde(tok: str, sents: list[tuple[str, int, str]]) -> tuple[str, int, str] | None:
    """La primera oración (cap, idx, texto) que dice el número o el nombre."""
    for cap, i, t in sents:
        if (numero_en(tok, t) if numeros(tok) else _palabra_en(tok, t)):
            return cap, i, t
    return None


def validar(resp: Any, ent: dict[str, Any], confirmados: dict[str, dict[str, list[str]]] | None = None,
            final: bool | None = None) -> dict[str, Any]:
    """§C.3 sobre la respuesta: {beats (lo que queda, por cap y beat), relojes, descartados (del modelo y de la
    validación, con regla y motivo), fichas_fuera, preguntas, vuelven, picos_vacios, motivos, motivos_beat}. F38
    §A.1: `motivos_beat` = por motivo, los (cap, beat) que el
    reintento parcial puede cambiar. F37:
    - §A.1b fecha del relato y §A.1c cita sin fecha (reglas `fecha_relato`, `cita_sin_fecha`);
    - §A.4 una coincidencia de número o nombre en `no_dicho`/`spoiler` no corta: es una pregunta al autor para el
      reintento (`preguntas`; la ficha queda marcada `pregunta`). Con `confirmados` (las preguntas que se hicieron, en la
      validación del reintento) lo que el autor mantuvo queda juzgado «otro hecho» (`juicio_autor`); una coincidencia
      nueva ahí ya no se pregunta: corta;
    - F38d §A.1: `final` dice si una coincidencia nueva corta (la validación al cerrar) o es una pregunta de la vuelta
      siguiente (False: las vueltas, con los `confirmados` acumulados). Sin `final`, como siempre: corta si hay
      `confirmados`;
    - §A.2 los descartes «voz_lo_dice» cuya voz no dice las cifras o los nombres del ítem (`vuelven`);
    - §A.3b los beats pico sin ficha (`picos_vacios`).
    F38c §A.1: los beats con `a_pantalla` cuya ficha no es ninguno de ellos (`a_pantalla_vacios`); §A.2: la cifra que
    contradice la voz (oración ancla ± 1) es una pregunta al autor más (regla `contradice`), como no_dicho y spoiler.
    F38e §C.3: el `respaldo` de la ficha tiene que ser fragmento literal del texto del ítem (regla `respaldo`, un
    motivo más del reintento) y el candado mira las cifras, los nombres y los años contra él; §C.4: en una cita se
    guarda el `autor` que se muestra y `autor_origen`.
    `motivos` = todo lo que va al reintento, en una lista."""
    final = (confirmados is not None) if final is None else bool(final)
    from script_engine.gfx_project import ficha_medida
    from script_engine.pantalla_colocar import caracteres
    caps = {c["cap"]: c for c in ent["caps"]}
    orden_caps = [c["cap"] for c in ent["caps"]]
    beats = {b["n"]: b for b in ent["beats"]}
    arch = {x["id"]: x for x in ent["archivo"]}
    pool = ev.items(ent.get("_pool")) if ent.get("_pool") else {}
    lista = {ev.norm(w): w for w in ent["clima"]}
    voz_video = _voz_video(ent)
    mom = momentos(ent)
    resp = resp if isinstance(resp, dict) else {}
    filas = sorted([b for b in resp.get("beats") or [] if isinstance(b, dict)],
                   key=lambda b: (str(b.get("cap")), _int(b.get("beat")) or 0))
    quedan: dict[tuple[str, int], dict[str, Any]] = {}
    desc: list[dict[str, Any]] = [{"pool_id": d.get("pool_id"), "regla": "modelo", "tipo": d.get("tipo"),
                                   "motivo": d.get("motivo"), "quien": "modelo"}
                                  for d in resp.get("descartados") or [] if isinstance(d, dict)]
    usados_ids: set[str] = set()
    usadas_pal: set[str] = set()
    preguntas: list[dict[str, Any]] = []
    fichas_fuera = 0
    for f in filas:
        cap, nb = str(f.get("cap") or ""), _int(f.get("beat"))
        b = beats.get(nb)
        k = (cap, nb if nb is not None else -1)
        slot = quedan.setdefault(k, {"cap": cap, "beat": nb, "funcion": (b or {}).get("funcion"),
                                     "pico": bool((b or {}).get("pico")), "ficha": None, "sello": None})
        fi = f.get("ficha") if isinstance(f.get("ficha"), dict) else None
        if fi:
            motivo, regla, ficha = _validar_ficha(fi, cap, nb, b, slot, caps, orden_caps, arch, pool, voz_video,
                                                  usados_ids, ent, ficha_medida, caracteres, mom, confirmados,
                                                  final)
            if motivo:
                fichas_fuera += 1
                desc.append({"pool_id": fi.get("pool_id"), "cap": cap, "beat": nb, "que": "ficha",
                             "etiqueta": fi.get("etiqueta"), "texto": fi.get("texto"),
                             "sentence_idx": fi.get("sentence_idx"), "regla": regla, "motivo": motivo,
                             "quien": "validación"})
            else:
                slot["ficha"] = ficha
                usados_ids.add(ficha["pool_id"])
                preguntas += [{**q, "pool_id": ficha["pool_id"], "cap": cap, "beat": nb, "sentence_idx":
                               ficha["sentence_idx"], "etiqueta": ficha["etiqueta"], "texto": ficha["texto"]}
                              for q in ficha.get("pregunta") or []]
        se = f.get("sello") if isinstance(f.get("sello"), dict) else None
        if se:
            w = lista.get(ev.norm(str(se.get("palabra") or "").strip()))
            si = _int(se.get("sentence_idx"))
            c = caps.get(cap)
            voz_cap = " ".join(s["texto"] for s in c["oraciones"]) if c else ""
            motivo = ("el cap no existe" if c is None else
                      f"«{se.get('palabra')}» no está en el vocabulario de clima" if w is None else
                      f"la oración [{se.get('sentence_idx')}] no existe en {cap}" if si is None
                      or not 0 <= si < len(c["oraciones"]) else
                      f"«{w}» es palabra de la voz de {cap}" if _raiz_en(w, voz_cap) else
                      f"«{w}» ya salió en el video" if w in usadas_pal else
                      f"un sello por beat: el beat {nb} ya tiene «{slot['sello']['palabra']}»" if slot["sello"] else None)
            if motivo:
                desc.append({"cap": cap, "beat": nb, "que": "sello", "texto": se.get("palabra"),
                             "sentence_idx": se.get("sentence_idx"), "regla": "sello", "motivo": motivo,
                             "quien": "validación"})
            else:
                slot["sello"] = {"palabra": w, "sentence_idx": si, "oracion": c["oraciones"][si]["texto"]}
                usadas_pal.add(w)
    for n, b in beats.items():                              # todos los beats del video, aunque el modelo no los nombre
        quedan.setdefault((b["cap"], n), {"cap": b["cap"], "beat": n, "funcion": b["funcion"], "pico": b["pico"],
                                          "ficha": None, "sello": None})
    relojes = []
    for r in resp.get("relojes") or []:
        if not isinstance(r, dict):
            continue
        c, si = caps.get(str(r.get("cap") or "")), _int(r.get("sentence_idx"))
        ok = c is not None and si is not None and 0 <= si < len(c["oraciones"])
        relojes.append({"cap": r.get("cap"), "sentence_idx": si, "fecha": str(r.get("fecha") or ""),
                        "oracion": c["oraciones"][si]["texto"] if ok else None, **({} if ok else {"error": "la oración no existe"})})
    out_beats = sorted(quedan.values(), key=lambda s: (orden_caps.index(s["cap"]) if s["cap"] in orden_caps else 99,
                                                       s["beat"] if s["beat"] is not None else -1))
    # §A.2: el descarte «la voz lo dice» se verifica (las cifras o los nombres del ítem en la voz de sus caps). F38c
    # §A.1: un `a_pantalla` ya no lleva `beats_que_lo_cuentan` (salvo que sea dato de un beat) → todo el video
    vuelven = []
    for d in desc:
        if d.get("quien") != "modelo" or d.get("tipo") != "voz_lo_dice" or d.get("pool_id") in usados_ids:
            continue
        it, x = pool.get(str(d.get("pool_id"))), arch.get(str(d.get("pool_id")))
        if it is None or x is None:
            continue
        caps_it = {beats[n]["cap"] for n in x["beats_que_lo_cuentan"] if n in beats}
        voz = " ".join(s["texto"] for cc in orden_caps if not caps_it or cc in caps_it for s in caps[cc]["oraciones"])
        falta = voz_no_lo_dice(it, voz, ent.get("anios"))
        if falta:
            d["verificado"] = f"falso: la voz no dice {falta}"
            vuelven.append({"pool_id": d["pool_id"], "motivo": d.get("motivo"), "falta": falta,
                            "caps": sorted(caps_it) or ["todo el video"], "texto": x["texto"]})
    picos_vacios = [{"cap": s["cap"], "beat": s["beat"]} for s in out_beats if s["pico"] and not s["ficha"]]
    # F38c §A.1: el beat que tiene `a_pantalla` y cuya ficha no es ninguno de ellos (vacía u otro id); si lleva uno, los
    # demás de ese beat no cuentan («como máximo una ficha por beat» del prompt)
    a_pantalla_vacios = []
    for s in out_beats:
        ids = [x for x in ent["archivo"] if (x.get("a_pantalla") or {}).get("beat") == s["beat"]
               and beats.get(s["beat"], {}).get("cap") == s["cap"]]
        if ids and (s["ficha"] or {}).get("pool_id") not in {x["id"] for x in ids}:
            a_pantalla_vacios.append({"cap": s["cap"], "beat": s["beat"],
                                      "ids": [{"id": x["id"], "por_que": x["a_pantalla"]["por_que"]} for x in ids]})
    # F38 §A.1: cada motivo con los beats que puede cambiar el reintento (`motivos_beat`, lista paralela a `motivos`):
    # la ficha caída → su beat (y, si la oración existe y es de otro beat, también ese: ahí puede ir); la pregunta y el
    # pico vacío → su beat; el descarte que vuelve → [] (no tiene beat: va en cualquier beat con motivo).
    motivos, motivos_beat = [], []
    for d in desc:
        if d.get("que") != "ficha":
            continue
        motivos.append(f"{d.get('pool_id')} ({d.get('cap')} beat {d.get('beat')}) «{d.get('etiqueta')} · "
                       f"{d.get('texto')}»: {d['regla']}: {d['motivo']}")
        bs = [(str(d.get("cap")), d.get("beat"))] if d.get("beat") is not None else []
        c, si = caps.get(str(d.get("cap"))), _int(d.get("sentence_idx"))
        if c is not None and si is not None and 0 <= si < len(c["oraciones"]):
            bs.append((c["cap"], c["oraciones"][si]["beat"]))
        motivos_beat.append(sorted(set(bs), key=lambda x: (x[0], x[1])))
    for q in preguntas:
        motivos.append(_pregunta_txt(q))
        motivos_beat.append([(q["cap"], q["beat"])])
    for v in vuelven:
        motivos.append(f"{v['pool_id']}: dijiste que la voz lo dice («{v['motivo']}»); la voz de {', '.join(v['caps'])} "
                       f"no dice {' ni '.join('«' + str(t) + '»' for t in v['falta'])} («{v['texto']}»): vuelve a ser "
                       f"candidato")
        motivos_beat.append([])
    for p in picos_vacios:
        motivos.append(f"el beat {p['beat']} de {p['cap']} es pico y quedó sin ficha")
        motivos_beat.append([(p["cap"], p["beat"])])
    for a in a_pantalla_vacios:                             # F38c §A.1
        motivos.append(f"el beat {a['beat']} de {a['cap']} quedó sin ninguno de los datos que la escaleta dejó para la "
                       f"pantalla porque la voz no los dice: "
                       + ", ".join(f"{x['id']} («{x['por_que']}»)" for x in a["ids"]))
        motivos_beat.append([(a["cap"], a["beat"])])
    return {"beats": out_beats, "relojes": relojes,
            "descartados": desc, "fichas_fuera": fichas_fuera, "preguntas": preguntas, "vuelven": vuelven,
            "picos_vacios": picos_vacios, "a_pantalla_vacios": a_pantalla_vacios, "motivos": motivos,
            "motivos_beat": motivos_beat}


def _pregunta_txt(q: dict[str, Any]) -> str:
    """F37 §A.4, con las palabras del handoff: «D47: la voz dice “dos kilómetros” en ch03 [17] (“…”); ¿es el mismo
    hecho? si no, mantenelo». F38c §A.2: la cifra que contradice la voz dice «para lo mismo». F40 §A: la cifra del
    gancho que la voz dice fuera de la oración ancla y sus vecinas (`video`) dice solo dónde («en ch05 [12] (…)»)."""
    donde = f"en {q['donde'][0]} [{q['donde'][1]}] («{q['donde'][2]}»)" if q.get("donde") else "en la voz"
    que = ("en una oración posterior " if q["regla"] == "spoiler" else
           "para lo mismo, en la oración ancla o en una vecina " if q["regla"] == "contradice" else
           "" if q.get("video") else "en la oración ancla o en una vecina ")
    return (f"{q['pool_id']} ({q['cap']} beat {q['beat']}, oración [{q['sentence_idx']}]) «{q['etiqueta']} · "
            f"{q['texto']}»: la voz dice «{q['token']}» {que}{donde}; ¿es el mismo hecho? si no, mantenelo")


def _int(v: Any) -> int | None:
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _validar_ficha(fi: dict, cap: str, nb: int | None, b: dict | None, slot: dict, caps: dict, orden_caps: list[str],
                   arch: dict, pool: dict, voz_video: list[str], usados_ids: set[str], ent: dict,
                   ficha_medida: Callable, caracteres: Callable, mom: dict, confirmados: dict | None,
                   final: bool = False) -> tuple[str | None, str | None, dict | None]:
    """(motivo, regla, ficha validada) de una ficha del papel, en el orden de §C.3 (+ F37 §A.1b/c y §A.4). F38d §A.1:
    con `final` la coincidencia que queda (no juzgada en `confirmados`) corta; sin él, es una pregunta."""
    from script_engine.pantalla_filtros import candado, contradicciones_de, frase_contradiccion, no_dicho, spoiler
    pid = str(fi.get("pool_id") or "")
    c = caps.get(cap)
    si = _int(fi.get("sentence_idx"))
    et = re.sub(r"\s+", " ", str(fi.get("etiqueta") or "")).strip()
    txt = re.sub(r"\s+", " ", str(fi.get("texto") or "")).strip()
    x = arch.get(pid)
    # anclaje
    if c is None or b is None or b["cap"] != cap:
        return f"el beat {nb} no es de {cap}", "anclaje", None
    if x is None:
        return f"{pid!r} no está en el archivo", "anclaje", None
    if si is None or not 0 <= si < len(c["oraciones"]):
        return f"la oración [{fi.get('sentence_idx')}] no existe en {cap}", "anclaje", None
    s = c["oraciones"][si]
    if s["beat"] != nb:
        return f"la oración [{si}] es del beat {s['beat']}, no del {nb}", "anclaje", None
    if slot["ficha"]:
        return f"una ficha por beat: el beat {nb} ya tiene {slot['ficha']['pool_id']}", "anclaje", None
    estilo = estilo_de(pid, et, ent["a_pantalla"].get(pid, ""))
    tipo = TIPO_DE_ESTILO[estilo]
    autor_arch = str(x.get("autor") or "")
    autor, autor_origen = autor_arch, None
    if tipo == "cita":
        txt = re.sub(r"^[«\"“]+|[»\"”]+$", "", txt).strip()
    # formato
    if not txt or not et:
        return "etiqueta o dato vacío", "formato", None
    if tipo == "cita" and not autor_arch:
        return "la cita no tiene autor en el archivo", "formato", None
    m = ficha_medida(et, txt)
    if m["kicker"] > 1 or m["title"] > 2:
        return f"etiqueta en {m['kicker']} línea(s) y dato en {m['title']} (1 y 2)", "formato", None
    # F38e §C.3a: el respaldo (el fragmento del texto del ítem que el autor copió letra por letra) tiene que ser
    # subcadena de ese texto con la normalización del candado (ev.norm); si falta o no lo es, cae con regla `respaldo`
    resp = re.sub(r"\s+", " ", str(fi.get("respaldo") or "")).strip()
    if not resp:
        return f"la ficha no trae `respaldo` (el fragmento literal del texto de {pid})", "respaldo", None
    if ev.norm(resp) not in ev.norm(x["texto"]):
        return f"el respaldo «{resp}» no es un fragmento literal del texto de {pid}", "respaldo", None
    if tipo == "cita":                 # F38e §C.4: el autor que se muestra (el del modelo si sus nombres están en el archivo)
        autor, autor_origen = autor_mostrado(str(fi.get("autor") or ""), x)
    it = pool.get(pid)
    vecinas = " ".join(ss["texto"] for ss in c["oraciones"][max(0, si - 1):si + 2])
    # F37 §A.1b: fecha del relato (por año; un testimonio se cuenta después; la oración o su vecina lo sitúan después)
    anio, ahora = anio_de((it or {}).get("fecha")), mom.get((cap, si))
    testimonio = bool((it or {}).get("testimonio"))
    if anio and ahora and anio > ahora and not testimonio and not dice_anio(anio, vecinas, ent.get("anios")):
        return (f"{pid} es de {anio} y en la oración [{si}] el relato va por {ahora} (el último año que dijo la voz); "
                f"ni la oración ni sus vecinas lo sitúan después", "fecha_relato", None)
    # F37 §A.1c: una cita sin fecha (y que no es testimonio) vale solo si su autor está en la oración o en una vecina
    if x["id"][:1] == "Q" and not anio and not testimonio and not autor_en(autor_arch, x.get("rol") or "", vecinas):
        return (f"cita sin fecha: su autor («{autor_arch}», {x.get('rol') or 'sin rol'}) no aparece en la oración "
                f"[{si}] ni en sus vecinas", "cita_sin_fecha", None)
    # candado, no dicho, spoiler (los de pantalla_filtros, con el ítem del archivo como texto fuente)
    gancho = (b.get("funcion") == "gancho")
    xi = {"id": pid, "texto": x["texto"], "fuente": x["fuente"], "autor": autor_arch,
          "a_pantalla": pid in ent["a_pantalla"], "por_que": ent["a_pantalla"].get(pid, ""), "gancho": gancho}
    # F38e §C.3b: con un respaldo válido, el candado mira cifras, nombres y años contra el respaldo, no contra todo el
    # texto del ítem (la excepción de la oración ancla sigue dentro de `candado`); §C.3c: la cita sigue contra el texto
    # entero (frase literal, recortada)
    xi_c = xi if tipo == "cita" else {**xi, "texto": resp}
    k = orden_caps.index(cap)
    antes = " ".join(ss["texto"] for cc in orden_caps[:k] for ss in caps[cc]["oraciones"])
    juicio = (confirmados or {}).get(pid) or {}
    ctx: dict[str, Any] = {"its": {pid: xi}, "x": xi, "pid": pid, "sents": c["oraciones"], "si": si, "s": s,
                           "voz_video": voz_video, "tipo": tipo, "txt": txt, "et": et, "juicio": juicio}
    fil_ent = {"voz_antes": antes}
    mot = candado({}, fil_ent, {**ctx, "x": xi_c, "its": {pid: xi_c}})
    if mot:
        return mot, "candado", None
    # F37 §A.4: no_dicho y spoiler encuentran la coincidencia; la juzga el autor (pregunta en el reintento). F40 §A: la
    # cifra del gancho que la voz dice en otra oración del video también (`video`: la pregunta dice solo dónde)
    preguntas: list[dict[str, Any]] = []
    vec = [(cap, ss["idx"], ss["texto"]) for ss in c["oraciones"][max(0, si - 1):si + 2]]
    todo = [(cc, ss["idx"], ss["texto"]) for cc in orden_caps for ss in caps[cc]["oraciones"]]
    mot = no_dicho({}, fil_ent, ctx)
    if mot:
        if final:
            return mot, "no_dicho", None
        for t in ctx["dichos"]:
            cerca = _donde(t, vec)
            preguntas.append({"regla": "no_dicho", "token": t, "donde": cerca or _donde(t, todo),
                              **({} if cerca else {"video": True})})
    despues = c["oraciones"][si + 1:] + [ss for cc in orden_caps[k + 1:] for ss in caps[cc]["oraciones"]]
    sp_ctx = {**ctx, "sents": c["oraciones"][:si + 1] + despues}               # (c): en ese cap o en los siguientes
    mot = spoiler({}, fil_ent, sp_ctx)
    if mot:
        if final:
            return mot.replace("del cap", "del cap o de un cap siguiente"), "spoiler", None
        tras = [(cap, ss["idx"], ss["texto"]) for ss in c["oraciones"][si + 1:]] + \
               [(cc, ss["idx"], ss["texto"]) for cc in orden_caps[k + 1:] for ss in caps[cc]["oraciones"]]
        preguntas += [{"regla": "spoiler", "token": t, "donde": _donde(t, tras)} for t in sp_ctx["spoil"]]
    # F38c §A.2: la cifra que contradice la voz (pantalla_filtros.contradicciones, la del chequeo 5 de Fase 2, con la
    # oración ancla ± 1 como vecindad) también es una pregunta al autor: «¿es el mismo hecho?»; el token es la cifra
    # de la voz y lo que el autor mantuvo (juicio «contradice») no vuelve a contar
    cons = contradicciones_de(f"{et} {txt}", voz_video, cerca=[t for _, _, t in vec], juicio=juicio)
    if cons:
        if final:
            return f"la cifra contradice la voz: {'; '.join(frase_contradiccion(q) for q in cons)}", "contradice", None
        for t in dict.fromkeys(q["token"] for q in cons):
            o = next(q["oracion"] for q in cons if q["token"] == t)
            donde = next(((cc, i, tt) for cc, i, tt in vec + todo if tt.strip() == o), None)
            preguntas.append({"regla": "contradice", "token": t, "donde": donde})
    if pid in usados_ids:
        return f"{pid} ya va en otro beat del video", "una_vez", None
    n = caracteres(tipo, et, txt, autor)
    if n > s["caben"]:
        # F38d §A.2.2: el desglose que mide el código (en una cita, el autor + 5 de comillas y raya) y el mayor `caben`
        # de las oraciones del beat con su oración (empate: la primera): data de la entrada, no regla
        m, sm = max(((ss["caben"], -ss["idx"]) for ss in c["oraciones"] if ss["beat"] == nb), default=(s["caben"], -si))
        cuenta = (f"etiqueta {len(et)} + dato {len(txt)} + autor {len(autor)} (con comillas y raya)" if tipo == "cita"
                  else f"etiqueta {len(et)} + dato {len(txt)}")
        return (f"{cuenta} = {n} caracteres y en la oración [{si}] caben {s['caben']}; en este beat caben como máximo "
                f"{m} (oración [{-sm}])"), "caben", None
    pal = str(fi.get("palabra") or "").strip()
    en = any(ev.norm(pal) == ev.norm(re.sub(r"[^\w]", "", w)) for w in palabras(s["texto"])) if pal else False
    usado = {r: [str(t) for t in v] for r, v in juicio.items() if v}
    return None, None, {"pool_id": pid, "sentence_idx": si, "palabra": pal, "palabra_en_oracion": en,
                        "etiqueta": et, "texto": txt, "respaldo": resp, "estilo": estilo,
                        **({"autor": autor, "autor_origen": autor_origen} if tipo == "cita" else {}),
                        "aporta": str(fi.get("aporta") or ""), "oracion": s["texto"], "caracteres": n,
                        "caben": s["caben"], "anio": anio, "relato": ahora,
                        **({"pregunta": preguntas} if preguntas else {}), **({"juicio_autor": usado} if usado else {})}


# ═══════════════════════ llamada (§C.2) ═══════════════════════

class TopePantalla(RuntimeError):
    """El tope de US$ no alcanza para otra llamada."""


class SinJSON(RuntimeError):
    """Dos respuestas sin JSON válido: PARADA (HANDOFF_F36_C_D, Frenos)."""


def primer_json(txt: str) -> dict | None:
    """El primer objeto JSON válido del texto (lo de antes o después se ignora); None si no hay."""
    dec = json.JSONDecoder()
    for m in re.finditer(r"\{", txt or ""):
        try:
            obj, _ = dec.raw_decode(txt, m.start())
        except json.JSONDecodeError:
            continue
        if isinstance(obj, dict):
            return obj
    return None


def _peor_usd(chars: int, salida_tokens: int, pin: float, pout: float) -> float:
    """La estimación del peor caso de una llamada (la de siempre de §C.2: los caracteres del pedido a tokens, y la
    salida peor), en US$ con las tarifas por millón."""
    return chars / 2.5 / 1e6 * pin + salida_tokens / 1e6 * pout


def _reintento(user: str, errores: list[str]) -> str:
    """El reintento de JSON completo (la respuesta no parseó): no es parcial."""
    return user + "\n\nTU RESPUESTA ANTERIOR TUVO ESTOS PROBLEMAS (corregilos y devolvé el JSON completo otra vez):\n" + \
        "\n".join(f"- {e}" for e in errores)


def _reintento_parcial(user: str, anterior: dict[str, Any], motivos: list[str],
                       beats_m: list[tuple[str, int]]) -> str:
    """F38 §A.1: el USER original + la respuesta anterior (el papel completo, como contexto) + los motivos + el formato
    del reintento (solo `cambios` de los beats con motivo)."""
    return (user + "\n\nTU RESPUESTA ANTERIOR (el papel completo, como contexto):\n"
            + json.dumps(anterior, ensure_ascii=False)
            + "\n\nTUVO ESTOS PROBLEMAS:\n" + "\n".join(f"- {m}" for m in motivos)
            + "\n\n" + REINTENTO_PARCIAL.format(beats=", ".join(f"{c} beat {b}" for c, b in beats_m))
            + "\n\nFormato de salida: " + FORMATO_REINTENTO)


def _confirmar(preguntas: list[dict[str, Any]]) -> dict[str, dict[str, list[str]]]:
    """Las preguntas del reintento por ítem y regla: lo que el autor mantenga en el reintento queda juzgado «otro hecho»."""
    out: dict[str, dict[str, list[str]]] = {}
    for q in preguntas:
        out.setdefault(str(q["pool_id"]), {}).setdefault(q["regla"], []).append(str(q["token"]))
    return out


def beats_con_motivo(motivos_beat: list[list[Any]]) -> list[tuple[str, int]]:
    """F38 §A.1: los (cap, beat) que el reintento parcial puede cambiar = la unión de los beats de cada motivo. Un motivo
    sin beat (el descarte que vuelve a ser candidato) no agrega ninguno: el autor lo puede proponer en cualquiera de
    estos; si no hay ninguno, no hay dónde y el reintento no se manda (se anota)."""
    out = {(str(c), int(b)) for bs in motivos_beat for c, b in bs if b is not None}
    return sorted(out, key=lambda x: (x[0], x[1]))


def fusionar(base: dict[str, Any], resp: Any, permitidos: list[tuple[str, int]]
             ) -> tuple[dict[str, Any], list[dict[str, Any]], list[dict[str, Any]]]:
    """F38 §A.1: los `cambios` del reintento sobre la respuesta del intento 1, por (cap, beat); lo demás queda congelado
    (relojes, descartados, los otros beats). Por cambio: `ficha`/`sello` con un objeto lo reemplazan, con null lo borran,
    y la clave ausente = esa parte sin cambio. Un cambio sobre un beat sin motivo (o que no es un objeto, o sin ficha ni
    sello) se ignora y se anota. Devuelve (respuesta fusionada, aplicados, ignorados)."""
    out = json.loads(json.dumps(base if isinstance(base, dict) else {}, ensure_ascii=False))
    filas = [b for b in out.get("beats") or [] if isinstance(b, dict)]
    out["beats"] = filas
    ok = {(str(c), int(b)) for c, b in permitidos}
    aplicados: list[dict[str, Any]] = []
    ignorados: list[dict[str, Any]] = []
    cambios = resp.get("cambios") if isinstance(resp, dict) else None
    if not isinstance(cambios, list):
        if resp:
            ignorados.append({"cambio": None, "motivo": "la respuesta no trae `cambios`: sin cambios"})
        cambios = []
    for ch in cambios:
        if not isinstance(ch, dict):
            ignorados.append({"cambio": ch, "motivo": "el cambio no es un objeto"})
            continue
        cap, nb = str(ch.get("cap") or ""), _int(ch.get("beat"))
        partes = [p for p in ("ficha", "sello") if p in ch and (ch[p] is None or isinstance(ch[p], dict))]
        if (cap, nb) not in ok:
            ignorados.append({"cap": cap, "beat": nb, "cambio": ch, "motivo": "el beat no tiene motivo"})
            continue
        if not partes:
            ignorados.append({"cap": cap, "beat": nb, "cambio": ch, "motivo": "sin ficha ni sello"})
            continue
        mismas = [f for f in filas if str(f.get("cap")) == cap and _int(f.get("beat")) == nb]
        if not mismas:
            mismas = [{"cap": cap, "beat": nb, "ficha": None, "sello": None}]
            filas.append(mismas[0])
        for p in partes:
            mismas[0][p] = ch[p]
            for otra in mismas[1:]:                       # una por beat: la fila repetida pierde esa parte
                otra[p] = None
        aplicados.append({"cap": cap, "beat": nb, "partes": partes})
    return out, aplicados, ignorados


def llamar(ent: dict[str, Any], out_dir: Path, *, post: Callable[[dict], dict] | None = None,
           tope: float | None = None, log: list[str] | None = None) -> dict[str, Any]:
    """La llamada con caché, tope y las vueltas de reintento. Devuelve {clave, intentos, final, validacion, usd,
    tokens_in, tope, motivos, motivos_beat, confirmados, reintento}. `post` (tests) reemplaza al POST de la API: recibe
    el body y devuelve el mensaje {content, usage, stop_reason}; cada llamada al POST es un intento, en orden.
    F37 §A.5: los motivos van juntos (fichas caídas, preguntas al autor, descartes «la voz lo dice» falsos, picos sin
      ficha), dentro del tope del perfil (`tope_usd`). F38 §A.1: el reintento es parcial (`fusionar`): solo los beats
      con motivo (`beats_con_motivo`). El JSON que no parsea sigue con el reintento de JSON completo de siempre (no es
      parcial) y esa respuesta es final (F38d §A.1.6). F38b: los motivos son solo los de la validación en papel.
    F38d §A.1: VUELTAS. Después de cada vuelta, el papel fusionado se valida con los `confirmados` acumulados
      (`_acumular`, nunca se pisan) y sin cortar: una coincidencia nueva (no_dicho, spoiler, contradice) es una pregunta
      de la vuelta siguiente. Hay otra vuelta mientras haya motivos, no sean iguales a los de la vuelta anterior y la
      vuelta entre en el tope. Al cerrar (`reintento.cierre`: «sin motivos», «sin progreso», «tope», «sin JSON», «sin
      beat») la validación final de siempre: lo que sigue sin preguntar corta (`reintento.cortados_al_cierre`). Las
      preguntas de una vuelta que no volvió (tope, sin JSON) no quedan confirmadas: el autor no las contestó.
      `reintento.vueltas`: por vuelta {vuelta, beats, motivos, aplicados, ignorados, usd}; `beats`, `aplicados` e
      `ignorados` de `reintento` son la unión de todas las vueltas (para los lectores de antes)."""
    import claude_helpers as hx
    log = log if log is not None else []
    tope_v, tope_de = (float(tope), "argumento") if tope is not None else tope_usd()
    user = pedido(ent)
    clave = hashlib.md5(f"{PROMPT_VERSION}|{MODELO}|{EFFORT}|{PANTALLA_SYSTEM}|{user}".encode("utf-8")).hexdigest()
    raw_f = Path(out_dir) / f"{ARCHIVO}.raw.json"
    try:
        prev = json.loads(raw_f.read_text(encoding="utf-8")) if raw_f.exists() else None
    except (OSError, ValueError):
        prev = None
    if prev and prev.get("clave") == clave and prev.get("final") is not None:
        prev["validacion"] = validar(prev["final"], ent, prev.get("confirmados") or {})   # determinista: el código de hoy
        log.append(f"  m01e: caché ({len(prev.get('intentos') or [])} intento(s), US$ 0)")
        return {**prev, "cache": True}
    out: dict[str, Any] = {"clave": clave, "modelo": MODELO, "effort": EFFORT, "prompt_version": PROMPT_VERSION,
                           "prompt_md5": prompt_md5(), "entrada_md5": entrada_md5(ent), "intentos": [], "final": None,
                           "validacion": None, "usd": 0.0, "tope": {"usd": tope_v, "de": tope_de}, "motivos": [],
                           "motivos_beat": [], "confirmados": {},
                           "reintento": {"tipo": None, "beats": [], "aplicados": [], "ignorados": [], "sin_beat": [],
                                         "vueltas": [], "cierre": None, "cortados_al_cierre": []}}
    pin, pout = hx.PRICES.get(hx._base(MODELO), (0.0, 0.0))
    salida_peor = [OUT_TOKENS_PEOR]

    def autor(pedido_k: str, k: int) -> tuple[bool, dict | None]:
        """Una llamada del autor: (hubo llamada, respuesta JSON o None). Sin lugar en el tope: (False, None)."""
        body = {"model": MODELO, "max_tokens": hx.MAX_TOKENS, "system": PANTALLA_SYSTEM,
                "messages": [{"role": "user", "content": pedido_k}], "output_config": {"effort": EFFORT}}
        peor = _peor_usd(len(json.dumps(body, ensure_ascii=False)), salida_peor[0], pin, pout)
        if out["usd"] + peor > tope_v:
            msg = (f"tope US$ {tope_v:.2f} ({tope_de}): gastado {out['usd']:.4f} + esta llamada hasta {peor:.4f}")
            out["error"] = msg
            log.append(f"  m01e: {msg} → sin {'reintento' if k else 'llamada'}")
            if k == 0:
                raise TopePantalla(msg)
            return False, None
        t0 = time.time()
        r = (post or hx._post)(body)
        u = r.get("usage") or {}
        usd = round(hx.cost_of(MODELO, u), 5)
        if post is None:
            hx._track(r.get("model") or MODELO, u, "m01e_pantalla")    # al cost_tracker (el ledger del paso)
        out["usd"] = round(out["usd"] + usd, 5)
        out["tokens_in"] = out.get("tokens_in") or u.get("input_tokens")
        salida_peor[0] = max(salida_peor[0], int(u.get("output_tokens") or 0))
        txt = "".join(c.get("text") or "" for c in r.get("content") or [] if c.get("type") == "text")
        resp = primer_json(txt)
        out["intentos"].append({"pedido": pedido_k if k else "(el USER de entrada)", "texto": txt, "respuesta": resp,
                                "usage": u, "stop": r.get("stop_reason"), "usd": usd,
                                "segundos": round(time.time() - t0, 1)})
        log.append(f"  m01e intento {k + 1}: in {u.get('input_tokens')} · out {u.get('output_tokens')} · "
                   f"US$ {usd:.4f} · {'JSON' if resp is not None else 'SIN JSON'}")
        return True, resp

    def cerrar(val: dict[str, Any]) -> dict[str, Any]:
        """La validación final (escribe el raw)."""
        out["validacion"] = val
        raw_f.parent.mkdir(parents=True, exist_ok=True)
        raw_f.write_text(json.dumps({**out, "entrada": _para_modelo(ent)}, ensure_ascii=False, indent=1),
                         encoding="utf-8")
        return out

    def cierre_final(papel: dict[str, Any], antes: dict[str, Any], por: str | None) -> dict[str, Any]:
        """F38d §A.1.3: la validación final de siempre (lo que sigue sin preguntar corta) y lo que cortó sin pregunta
        (lo que no estaba caído en la última validación de las vueltas)."""
        fin = validar(papel, ent, out["confirmados"], final=True)
        ya = {_clave_desc(d) for d in antes["descartados"] if d.get("quien") == "validación"}
        rt = out["reintento"]
        rt["cierre"] = por
        rt["cortados_al_cierre"] = [{k: d.get(k) for k in ("que", "pool_id", "cap", "beat", "etiqueta", "texto",
                                                         "sentence_idx", "regla", "motivo")}
                                    for d in fin["descartados"]
                                    if d.get("quien") == "validación" and _clave_desc(d) not in ya]
        if rt["cortados_al_cierre"]:
            log.append(f"  m01e: al cerrar ({por}) {len(rt['cortados_al_cierre'])} corte(s) sin pregunta")
        out["final"] = papel
        return cerrar(fin)

    _, resp = autor(user, 0)
    if resp is None:                                  # JSON inválido: el reintento de JSON completo de siempre
        out["reintento"]["tipo"] = "json"
        stop = out["intentos"][-1].get("stop")
        _, resp = autor(_reintento(user, [f"la respuesta no es JSON válido (stop_reason {stop})"]), 1)
        if resp is None:
            raw_f.parent.mkdir(parents=True, exist_ok=True)
            raw_f.write_text(json.dumps({**out, "entrada": _para_modelo(ent)}, ensure_ascii=False, indent=1),
                             encoding="utf-8")
            raise SinJSON(f"dos respuestas sin JSON válido; la cruda en {raw_f}")
        return cierre_final(resp, validar(resp, ent), None)   # final: sin vueltas (A.1.6), `cierre` None
    val = validar(resp, ent)
    out["final"], out["validacion"] = resp, val
    log.append(f"  m01e intento 1 validado: fichas fuera {val['fichas_fuera']} · preguntas {len(val['preguntas'])} · "
               f"vuelven {len(val['vuelven'])} · picos vacíos {len(val['picos_vacios'])}")
    out["motivos"] = val["motivos"]
    out["motivos_beat"] = [list(map(tuple, bs)) for bs in val["motivos_beat"]]
    rt = out["reintento"]
    papel, anteriores, k = resp, None, 0
    while True:
        motivos = val["motivos"]
        mb = [list(map(tuple, bs)) for bs in val["motivos_beat"]]
        if not motivos:
            return cierre_final(papel, val, "sin motivos")
        if motivos == anteriores:                     # derivado: otra vuelta no tiene nada nuevo que decirle al autor
            log.append(f"  m01e: los motivos después de la vuelta {k} son los que se le mandaron → cierra (sin progreso)")
            return cierre_final(papel, val, "sin progreso")
        beats_m = beats_con_motivo(mb)
        if not beats_m:                               # solo motivos sin beat: no hay dónde proponer nada
            rt["sin_beat"] = motivos
            log.append(f"  m01e: {len(motivos)} motivo(s) sin beat → sin {'otra vuelta' if k else 'reintento'} "
                       f"(anotados)")
            return cierre_final(papel, val, "sin beat")
        k += 1
        rt["tipo"] = "parcial"
        hubo, r = autor(_reintento_parcial(user, papel, motivos, beats_m), k)
        if r is None:                                 # sin lugar en el tope o sin JSON: queda la vuelta anterior
            if not hubo:
                return cierre_final(papel, val, "tope")
            rt["vueltas"].append({"vuelta": k, "beats": beats_m, "motivos": motivos, "aplicados": [], "ignorados": [],
                                  "usd": out["intentos"][-1]["usd"], "sin_json": True})
            rt["beats"] = _union_beats(rt["beats"], beats_m)
            out["error"] = (f"la vuelta {k} no devolvió JSON: queda "
                            + ("el intento 1" if k == 1 else f"la vuelta {k - 1}"))
            return cierre_final(papel, val, "sin JSON")
        out["confirmados"] = _acumular(out["confirmados"], _confirmar(val["preguntas"]))   # contestadas en esta vuelta
        fus, aplicados, ignorados = fusionar(papel, r, beats_m)
        rt["vueltas"].append({"vuelta": k, "beats": beats_m, "motivos": motivos, "aplicados": aplicados,
                              "ignorados": ignorados, "usd": out["intentos"][-1]["usd"]})
        rt["beats"] = _union_beats(rt["beats"], beats_m)
        rt["aplicados"] = rt["aplicados"] + aplicados
        rt["ignorados"] = rt["ignorados"] + ignorados
        if ignorados:
            log.append(f"  m01e vuelta {k}: {len(aplicados)} cambio(s) aplicados · {len(ignorados)} ignorado(s)")
        papel, anteriores = fus, motivos
        val = validar(papel, ent, out["confirmados"], final=False)
        log.append(f"  m01e vuelta {k} validada: fichas fuera {val['fichas_fuera']} · preguntas nuevas "
                   f"{len(val['preguntas'])} · picos vacíos {len(val['picos_vacios'])}")


def _clave_desc(d: dict[str, Any]) -> tuple:
    """Un descarte de la validación, por lo que cayó y dónde (para ver qué cortó el cierre que no estaba caído)."""
    return (d.get("que"), d.get("pool_id"), d.get("cap"), d.get("beat"),
            d.get("texto") if d.get("que") == "sello" else None)


def _union_beats(a: list[tuple[str, int]], b: list[tuple[str, int]]) -> list[tuple[str, int]]:
    return sorted({(str(c), int(n)) for c, n in list(a) + list(b)}, key=lambda x: (x[0], x[1]))


def _acumular(conf: dict[str, dict[str, list[str]]], nuevos: dict[str, dict[str, list[str]]]
              ) -> dict[str, dict[str, list[str]]]:
    """F38d §A.1.4: los `confirmados` de vuelta en vuelta: se suman (por ítem y regla, sin repetir), nunca se pisan."""
    out = {pid: {r: list(ts) for r, ts in reglas.items()} for pid, reglas in (conf or {}).items()}
    for pid, reglas in (nuevos or {}).items():
        for r, ts in reglas.items():
            lst = out.setdefault(pid, {}).setdefault(r, [])
            lst += [t for t in ts if t not in lst]
    return out


# ═══════════════════════ salida ═══════════════════════

def armar(ent: dict[str, Any], res: dict[str, Any]) -> dict[str, Any]:
    v = res["validacion"]
    return {"topic_id": ent["topic_id"], "prompt_version": PROMPT_VERSION, "prompt_md5": prompt_md5(),
            "modelo": res["modelo"], "effort": res["effort"], "entrada_md5": res.get("entrada_md5"),
            "intentos": len(res.get("intentos") or []), "usd": res.get("usd", 0.0) if not res.get("cache") else 0.0,
            "tokens_in": res.get("tokens_in"), "caps": [{"cap": c["cap"], "titulo": c["titulo"],
                                                         "oraciones": [s["texto"] for s in c["oraciones"]]}
                                                        for c in ent["caps"]],
            "beats": v["beats"], "relojes": v["relojes"],
            "descartados": v["descartados"],
            # F37: de dónde salen las medidas y qué pasó en el reintento (motivos enviados, preguntas y su respuesta)
            "seg_por_palabra": ent.get("seg_por_palabra"), "tope": res.get("tope"), "error": res.get("error"),
            "por_intento": [{"tokens_in": (i.get("usage") or {}).get("input_tokens"),
                             "tokens_out": (i.get("usage") or {}).get("output_tokens"), "usd": i.get("usd"),
                             "segundos": i.get("segundos")} for i in res.get("intentos") or []],
            "reintento": {"motivos": res.get("motivos") or [], "preguntas": _respuestas(res, v),
                          # F38 §A.1: parcial (los beats que podía cambiar, lo aplicado y lo ignorado)
                          # F38d §A.1.5: + por vuelta, por qué cerró y lo que el cierre cortó sin preguntar
                          **{k: (res.get("reintento") or {}).get(k) for k in ("tipo", "beats", "aplicados",
                                                                               "ignorados", "sin_beat", "vueltas",
                                                                               "cierre", "cortados_al_cierre")}},
            "picos_vacios": v.get("picos_vacios") or [],
            "a_pantalla_vacios": v.get("a_pantalla_vacios") or []}         # F38c §A.1: después del reintento


def _respuestas(res: dict[str, Any], v: dict[str, Any]) -> list[dict[str, Any]]:
    """F37 §A.4: cada pregunta del reintento con la respuesta del autor (la mantuvo = otro hecho; la sacó = el mismo)."""
    quedan = {b["ficha"]["pool_id"]: b for b in v["beats"] if b.get("ficha")}
    out = []
    for pid, reglas in (res.get("confirmados") or {}).items():
        b = quedan.get(pid)
        out.append({"pool_id": pid, "coincidencias": reglas,
                    "respuesta": (f"la mantuvo en {b['cap']} beat {b['beat']} [{b['ficha']['sentence_idx']}]: otro hecho"
                                  if b else "la sacó o la cambió (el mismo hecho, o eligió otra)")})
    return out


def _por_que_falta(p: dict[str, Any], pid: str) -> str:
    """F38c §A.1: por qué un `a_pantalla` no está en su beat: el descarte del autor, o lo que lo sacó en la validación
    (lo puso y cayó), o «el autor no lo puso»."""
    d = next((d for d in p.get("descartados") or [] if d.get("pool_id") == pid and d.get("quien") == "modelo"), None)
    if d:
        return f"el autor lo descartó{' [' + str(d['tipo']) + ']' if d.get('tipo') else ''}: {d.get('motivo')}"
    d = next((d for d in p.get("descartados") or [] if d.get("pool_id") == pid and d.get("quien") == "validación"),
             None)
    if d:
        return f"lo puso y cayó: {d['regla']}: {d['motivo']}"
    return "el autor no lo puso"


def a_markdown(p: dict[str, Any]) -> str:
    """Una línea por beat (ficha · sello) y los relojes; después lo que cayó, con motivo. F37: el año de cada
    ficha y el momento del relato, los picos sin ficha (⚠), el reintento (motivos enviados y respuestas del autor).
    F38c §A.1: el beat que después del reintento sigue sin ninguno de sus `a_pantalla` lleva ⚠, con el descarte del
    autor si lo hay (o lo que lo sacó en la validación) o «el autor no lo puso»: no se fuerza ni se corta nada."""
    sp, tp = p.get("seg_por_palabra") or {}, p.get("tope") or {}
    pi = " · ".join(f"intento {k + 1}: in {i.get('tokens_in')} · out {i.get('tokens_out')} · US$ {i.get('usd') or 0:.4f}"
                    for k, i in enumerate(p.get("por_intento") or []))
    lines = [f"# Guion de pantalla en papel — {p['topic_id']}", "",
             f"`m01e_pantalla` {p['prompt_version']} (md5 del prompt `{p['prompt_md5']}`) · {p['modelo']} {p['effort']} · "
             f"{p['intentos']} intento(s) · US$ {p['usd']:.4f} · tokens de entrada {p.get('tokens_in')}", ""]
    if sp or tp or pi:
        lines += [f"Segundos por palabra {sp.get('valor')} ({sp.get('origen')}) · tope US$ {tp.get('usd')} "
                  f"({tp.get('de')}){' · ' + pi if pi else ''}" + (f" · **{p['error']}**" if p.get("error") else ""), ""]
    fichas = sum(1 for b in p["beats"] if b["ficha"])
    sellos = sum(1 for b in p["beats"] if b["sello"])
    lines += [f"Totales: {fichas} fichas · {sellos} sellos · {len(p['relojes'])} relojes · "
              f"{len(p['descartados'])} descartados", ""]
    for c in p["caps"]:
        lines += [f"## {c['cap']} — {c['titulo']}", ""]
        for b in [b for b in p["beats"] if b["cap"] == c["cap"]]:
            f, s = b["ficha"], b["sello"]
            fi = (f"ficha **{f['pool_id']}** [{f['estilo']}] «{f['etiqueta']} · {f['texto']}»"
                  + (f" — {f['autor']}" + (f" (autor: {f['autor_origen']})" if f.get("autor_origen") else "")
                     if f.get("autor") else "")
                  + f" en [{f['sentence_idx']}] sobre «{f['palabra']}»{'' if f['palabra_en_oracion'] else ' (no está en la oración)'}"
                  f" ({f['caracteres']}/{f['caben']} car.)"
                  + (f" · respaldo: «{f['respaldo']}»" if f.get("respaldo") else "")
                  + (f" · año {f.get('anio') or '—'} / relato {f.get('relato') or '—'}" if "anio" in f else "")
                  + (f" · juzgado por el autor: otro hecho {f['juicio_autor']}" if f.get("juicio_autor") else "")
                  + f" · aporta: {f['aporta']}") if f else ("ficha — ⚠ pico sin ficha" if b["pico"] else "ficha —")
            se = f"sello **{s['palabra']}** en [{s['sentence_idx']}]" if s else "sello —"
            ap = next((a for a in p.get("a_pantalla_vacios") or [] if a["cap"] == b["cap"] and a["beat"] == b["beat"]),
                      None)
            ap_txt = (" · ⚠ sin su a_pantalla: " + "; ".join(f"{x['id']} ({_por_que_falta(p, x['id'])})"
                                                            for x in ap["ids"])) if ap else ""
            lines.append(f"- beat {b['beat']} · {b['funcion']}{' · PICO' if b['pico'] else ''} · {fi} · {se}{ap_txt}")
        rel = [r for r in p["relojes"] if r.get("cap") == c["cap"]]
        rel_txt = ", ".join(f"{r['fecha']} en [{r['sentence_idx']}]" for r in rel) or "—"
        lines.append(f"- relojes: {rel_txt}")
        lines.append("")
    lines += ["## Lo que cayó", ""]
    val = [d for d in p["descartados"] if d.get("quien") == "validación"]
    lines += [f"- {d.get('cap')} beat {d.get('beat')} · {d['que']} {d.get('pool_id') or ''} «"
              f"{(str(d.get('etiqueta')) + ' · ') if d.get('etiqueta') else ''}{d.get('texto')}» en "
              f"[{d.get('sentence_idx')}] → **{d['regla']}**: {d['motivo']}" for d in val] or ["- (nada)"]
    rt = p.get("reintento") or {}
    if rt.get("motivos"):
        lines += ["", "## Reintento: los motivos que se le mandaron al autor", ""]
        lines += [f"- {m}" for m in rt["motivos"]]
        lines += ["", "### Preguntas y respuesta del autor", ""]
        lines += [f"- {q['pool_id']} {q['coincidencias']}: {q['respuesta']}" for q in rt.get("preguntas") or []] \
            or ["- (ninguna)"]
        if rt.get("tipo") and not rt.get("vueltas"):  # F38 §A.1 (un papel de antes de F38d, sin vueltas)
            bm = ", ".join(f"{c} beat {b}" for c, b in rt.get("beats") or []) or "—"
            ap = ", ".join(f"{a['cap']} beat {a['beat']} ({'/'.join(a['partes'])})" for a in rt.get("aplicados") or [])
            lines += ["", f"### Reintento {rt['tipo']}", "", f"- beats que podía cambiar: {bm}",
                      f"- aplicados: {ap or '—'}"]
            lines += [f"- ignorado: {i.get('cap')} beat {i.get('beat')} — {i['motivo']}" for i in rt.get("ignorados") or []]
        elif rt.get("tipo"):
            lines += ["", f"### Reintento {rt['tipo']}: {len(rt['vueltas'])} vuelta(s)"]
        for vu in rt.get("vueltas") or []:            # F38d §A.1.5: por vuelta
            bm = ", ".join(f"{c} beat {b}" for c, b in vu.get("beats") or []) or "—"
            ap = ", ".join(f"{a['cap']} beat {a['beat']} ({'/'.join(a['partes'])})" for a in vu.get("aplicados") or [])
            lines += ["", f"#### Vuelta {vu['vuelta']} · US$ {vu.get('usd') or 0:.4f}"
                      + (" · **no devolvió JSON**" if vu.get("sin_json") else ""), "",
                      f"- beats que podía cambiar: {bm}", "- motivos:"]
            lines += [f"  - {m}" for m in vu.get("motivos") or []]
            lines += [f"- aplicados: {ap or '—'}"]
            lines += [f"- ignorado: {i.get('cap')} beat {i.get('beat')} — {i['motivo']}" for i in vu.get("ignorados") or []]
        if rt.get("sin_beat"):
            lines += ["", "### Motivos sin beat (no hubo reintento)", ""] + [f"- {m}" for m in rt["sin_beat"]]
    if rt.get("cierre") or rt.get("cortados_al_cierre"):   # F38d §A.1.3: por qué cerró y qué cortó sin pregunta
        nv = len(rt.get("vueltas") or [])
        lines += ["", "## Cierre del reintento", "",
                  f"- cerró por: **{rt.get('cierre') or '—'}** (después de {nv} vuelta{'s' if nv != 1 else ''})"]
        lines += ["- cortado al cerrar, sin preguntarle al autor:"] + \
            [f"  - {d.get('cap')} beat {d.get('beat')} · {d.get('que')} {d.get('pool_id') or ''} «"
             f"{(str(d.get('etiqueta')) + ' · ') if d.get('etiqueta') else ''}{d.get('texto')}» en "
             f"[{d.get('sentence_idx')}] → **{d.get('regla')}**: {d.get('motivo')}"
             for d in rt.get("cortados_al_cierre") or []] \
            if rt.get("cortados_al_cierre") else ["- cortado al cerrar, sin preguntarle al autor: (nada)"]
    lines += ["", "## Descartados por el modelo", ""]
    lines += [f"- {d.get('pool_id')}" + (f" [{d['tipo']}]" if d.get("tipo") else "") + f": {d.get('motivo')}"
              + (f" — **{d['verificado']}**" if d.get("verificado") else "")
              for d in p["descartados"] if d.get("quien") == "modelo"] or ["- (ninguno)"]
    return "\n".join(lines) + "\n"


def generar(topic_id: str, steps_dir: Path | None = None, *, pool: dict | None = None,
            post: Callable[[dict], dict] | None = None, vocabulario: list[str] | None = None,
            log: list[str] | None = None) -> dict[str, Any]:
    """El paso entero: entrada → llamada → validación → 01e_pantalla.json/.md en el directorio del topic."""
    from script_engine.clima import vocabulario_clima
    from script_engine.m01a_skeleton import STEPS_DIR
    log = log if log is not None else []
    carga = cargar(topic_id, Path(steps_dir or STEPS_DIR), pool)
    ent = entrada(carga, vocabulario if vocabulario is not None else vocabulario_clima())
    ent["_pool"] = carga["pool"]
    res = llamar(ent, carga["dir"], post=post, log=log)
    papel = armar(ent, res)
    (carga["dir"] / f"{ARCHIVO}.json").write_text(json.dumps(papel, ensure_ascii=False, indent=1), encoding="utf-8")
    (carga["dir"] / f"{ARCHIVO}.md").write_text(a_markdown(papel), encoding="utf-8")
    log.append(f"  m01e: {sum(1 for b in papel['beats'] if b['ficha'])} fichas · "
               f"{sum(1 for b in papel['beats'] if b['sello'])} sellos · {len(papel['relojes'])} relojes → "
               f"{carga['dir'] / (ARCHIVO + '.md')}")
    return papel


def ruta(topic_id: str, steps_dir: Path | None = None) -> Path:
    from script_engine.m01a_skeleton import STEPS_DIR
    return Path(steps_dir or STEPS_DIR) / topic_id / f"{ARCHIVO}.json"


def cargar_papel(topic_id: str, steps_dir: Path | None = None) -> dict[str, Any] | None:
    """El papel del topic (lo lee Fase 2); None si no hay."""
    f = ruta(topic_id, steps_dir)
    try:
        return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None
    except (OSError, ValueError):
        return None


def editar(topic_id: str, ediciones: list[dict[str, Any]], steps_dir: Path | None = None) -> Path:
    """`fase2b --plan-edit` (§C.4): las ediciones a mano van al papel, no al plan. Cada una: {cap, beat, ficha: {pool_id,
    sentence_idx, palabra, etiqueta, texto, aporta} | null} y/o {cap, beat, sello: {palabra, sentence_idx} | null};
    reemplazan lo del beat (null lo borra) y quedan marcadas `editado`. Una edición sin `ficha` ni `sello` se rechaza
    (ValueError). El estilo lo vuelve a poner el código. La primera vez se guarda una copia
    (01e_pantalla.antes_de_edicion.json); el .md se reescribe. Fase 2 vuelve a pasar lo editado por sus filtros como a
    todo."""
    from script_engine.pantalla_colocar import caracteres
    f = ruta(topic_id, steps_dir)
    p = json.loads(f.read_text(encoding="utf-8"))
    seg = float((p.get("seg_por_palabra") or {}).get("valor") or SEG_POR_PALABRA_RESPALDO)   # la del papel
    bak = f.with_name(f"{ARCHIVO}.antes_de_edicion.json")
    if not bak.exists():
        bak.write_text(json.dumps(p, ensure_ascii=False, indent=1), encoding="utf-8")
    oraciones = {c["cap"]: c["oraciones"] for c in p.get("caps") or []}
    for e in ediciones:
        if "ficha" not in e and "sello" not in e:
            raise ValueError(f"edición sin ficha ni sello (claves {sorted(e)}): solo se edita ficha o sello de un beat")
        b = next((x for x in p["beats"] if x["cap"] == e.get("cap") and x["beat"] == _int(e.get("beat"))), None)
        if b is None:
            raise ValueError(f"edición: no hay beat {e.get('beat')} en {e.get('cap')}")
        if "ficha" in e:
            fi = e["ficha"]
            if fi:
                si = int(fi["sentence_idx"])
                s = oraciones[e["cap"]][si]
                estilo = estilo_de(fi["pool_id"], fi.get("etiqueta") or "")
                tipo = TIPO_DE_ESTILO[estilo]
                fi = {"aporta": "(edición a mano)", **fi, "sentence_idx": si, "estilo": estilo, "oracion": s, "editado": True,
                      "palabra_en_oracion": ev.norm(str(fi.get("palabra") or "")) in ev.norm(s),
                      "caracteres": caracteres(tipo, fi.get("etiqueta"), str(fi.get("texto") or ""), fi.get("autor") or ""),
                      "caben": caben_en(s, seg)}
            b["ficha"] = fi
        if "sello" in e:
            se = e["sello"]
            b["sello"] = ({"palabra": str(se["palabra"]).upper(), "sentence_idx": int(se["sentence_idx"]),
                           "oracion": oraciones[e["cap"]][int(se["sentence_idx"])], "editado": True} if se else None)
    p.setdefault("ediciones", []).extend(ediciones)
    f.write_text(json.dumps(p, ensure_ascii=False, indent=1), encoding="utf-8")
    f.with_suffix(".md").write_text(a_markdown(p), encoding="utf-8")
    return f


def main(argv: list[str] | None = None) -> int:
    """Suelto (para un topic que ya tiene Fase 1, como Vajont): con el costo en 01_v3_costos.json (paso «pantalla»)."""
    from cost_tracker import cost_tracker
    from script_engine.m01a_skeleton import STEPS_DIR
    args = list(sys.argv[1:] if argv is None else argv)
    if not args:
        print("uso: python -m script_engine.m01e_pantalla <topic_id>")
        return 1
    topic_id = args[0]
    f = STEPS_DIR / topic_id / "01_v3_costos.json"
    costs = json.loads(f.read_text(encoding="utf-8")) if f.exists() else {}
    log: list[str] = []
    cost_tracker.start_video(topic_id)
    t0 = time.time()
    rc = 0
    try:
        generar(topic_id, log=log)
    except (SinJSON, TopePantalla) as e:
        log.append(f"  m01e: PARADA — {e}")
        rc = 2
    finally:
        r = cost_tracker.end_video()
        costs.setdefault("_corridas", []).append({"paso": "pantalla", "usd": round(getattr(r, "total_cost", 0.0) or 0.0, 4),
                                                  "segundos": round(time.time() - t0, 1)})
        f.write_text(json.dumps(costs, ensure_ascii=False, indent=1), encoding="utf-8")
    print("\n".join(log))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
