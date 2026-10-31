"""
script_engine/m01e_pantalla.py — F36 §C: el guion de pantalla EN PAPEL (DECISIONES 2026-10-26 19:54: «el autor de la
pantalla va a Fase 1»). Corre en Fase 1 después del OK de Omar en la compuerta de narración y antes de la voz (F67:
fase1_5.run_papel_aprobado, con su costo en 01_v3_costos.json como los demás pasos) o suelto:
`python -m script_engine.m01e_pantalla <topic>`.

    entrada    (§C.1, una para todo el video) por cap el título (01a_skeleton) y sus oraciones numeradas, partidas con
               el mismo corte de la voz (voz_utils.oraciones_de_texto) desde los párrafos de 01b_narracion_v3, cada una
               con su beat y `caben` (palabras × segundos por palabra del narrador —F37: derivado de sus voces,
               voz_utils.seg_por_palabra— × 15 cps, sin pasar de callout_dur_max: una estimación; la medida real es
               de Fase 2);
               los beats de la escaleta (n, función, pico sí/no, dato central, apoyo, cierre y, F64 Etapa 0, emoción,
               imagen sensorial, pregunta abierta y paga); el archivo = TODO el pool (F64 Etapa 0, DECISIONES 2026-10-31
               14:16: D con o sin cifra, T, Q, P y L; antes solo D con número, T, Q, P), cada ítem con id, texto, fuente,
               fecha (F37 §A.1a; «desconocida» si no tiene), las citas autor, rol y testimonio, `beats_que_lo_cuentan`
               (los beats cuyo dato central o de apoyo es el ítem) y al final `contexto_fuente` (el fragmento original
               de la fuente); F38c §A.1: el que la escaleta dejó para la pantalla lleva además `a_pantalla` {beat,
               por_que} (campo propio, no entra en `beats_que_lo_cuentan`); el vocabulario `sellos_clima` del perfil;
               F64 Etapa 0: `escaleta_video` (promesa del gancho, loops, pico, humano, antagonista, cierre humano) y
               `disputas` (versiones y contradicciones de ficha_caso.json).
    llamada    UNA a Claude Opus 5.5 (medium; F64 Etapa 0, antes Sonnet 5.5) con el prompt literal de §C.2
               (PANTALLA_SYSTEM, m01e-7: el de la prueba 1 con la oración 2 de F63 A.2; F37: el gancho en las primeras
               oraciones, m01e-2; el USER = el JSON de entrada + «Formato de salida: …», con el `tipo` de cada descarte),
               sin tope en dólares (F64 Etapa 1, DECISIONES 2026-10-31 13:07: el costo se informa, no frena), caché por
               md5 de la entrada y la versión del prompt. F37 §A.5: un reintento si el JSON no parsea o si la validación deja algún motivo
               (ficha caída, pregunta al autor, descarte «la voz lo dice» falso, pico sin ficha), con todos juntos. Dos
               respuestas sin JSON → PARADA (la cruda queda en 01e_pantalla.raw.json).
               F38 §A.1: el reintento es PARCIAL: ve el papel completo del intento 1 como contexto, pero devuelve solo
               `cambios` de los beats con motivo; el código los fusiona por (cap, beat) y lo demás queda congelado.
               F38d §A.1 / F64 Etapa 3: el reintento parcial da VUELTAS mientras haya motivos y el conjunto de sus
               CLAVES (regla, pool_id, cap, beat, token) no sea igual al de ninguna vuelta anterior («sin progreso»,
               por clave y no por texto: el motivo del verificador es prosa). Cierres: «sin motivos», «sin progreso»,
               «sin JSON», «sin beat» (`reintento.vueltas`, `cierre`); ya no hay una validación distinta al cerrar.
    respaldo   F38e §C: prompt m01e-6 (el de la prueba 1, letra por letra: el dato con las palabras del autor; los hechos
               en un `respaldo` literal del ítem); el respaldo tiene que ser fragmento del texto del ítem (regla
               `respaldo`) y el candado mira cifras, nombres y años contra él; en una cita, el `autor` del modelo se
               muestra si sus nombres propios están en el archivo (`autor_mostrado`, `autor_origen`), si no el del archivo.
    validar    (§C.3, sin tiempos ni fotos, con los filtros de pantalla_filtros) por ficha: anclaje (cap, beat, ítem y
               oración que existen; la oración es del beat), formato (etiqueta en 1 línea y dato en 2, gfx_project.
               ficha_medida), F37 §A.1b fecha del relato (el año del ítem contra el año del relato: F64 Etapa 2, el
               máximo que la voz dijo en el cap hasta la oración, sin los beats flash-forward; heredado del cap anterior
               mientras el cap no dijo ninguno) y §A.1c
               cita sin fecha (su autor en la oración o una vecina), candado (números, nombres y años literales en el
               texto del ítem; en el gancho vale la voz de todo el video), no dicho (oración ancla ± 1; en el gancho,
               una cifra del dato que la voz dice en cualquier oración del video: F40 §A), spoiler (la narración
               posterior del cap y de los caps siguientes), contradice (F38c §A.2) y fecha del relato
               —F64 Etapa 3 (DECISIONES 2026-10-31 14:20): estas cuatro ya no cortan ni le preguntan al autor: cada
               coincidencia es una MARCA y todas las marcas de la validación van en UNA llamada al verificador
               (pantalla_verificador, Opus medium), que decide hecho por hecho; lo que salva pasa con
               `juicio_verificador`, lo que corta va a `descartados` con `quien: "verificador"`—, el mismo dato una sola
               vez en el video, `caben`. Los descartes «voz_lo_dice» que el código pone en duda (§A.2) también son
               marcas (regla `voz_lo_dice`): «dicho» → el descarte queda como el autor lo escribió; «no_dicho» →
               vuelve a ser candidato (`vuelven`). Los picos sin ficha se nombran (§A.3b). Por sello: palabra de la
               lista, no es palabra de la voz del cap, no repetida en el video, uno por beat. Lo que cae va a
               `descartados` con la regla y el motivo. `candado`, `caben`, `anclaje`, `formato`, `respaldo`,
               `cita_sin_fecha`, `una_vez` y `sello` siguen cortando en código: son candados de Omar, no juicios de hecho.
               El raw guarda cada pedido y respuesta del verificador (`verificador`); en el hit de caché, `validar` se
               corre con los veredictos guardados por `pedido_md5` (caché parcial si falta alguno).
    estilo     (§C.1) lo pone el código por tipo de dato: Q → cita (con autor), P → nombre, D/T cuya etiqueta (o el
               `por_que` de su `a_pantalla`) nombra una carta, un acta, un informe o un documento → papel, resto → normal.
Salida en el directorio del topic de Fase 1 (aclaración 1: el que leen gfx_realizador y el rotulista): 01e_pantalla.json
(lo consume Fase 2), 01e_pantalla.md (una línea por beat y lo que cayó, para Omar) y 01e_pantalla.raw.json.
"""
from __future__ import annotations

import functools
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

PROMPT_VERSION = "m01e-7"       # F64 Etapa 0: el SYSTEM de m01e-6 (lab/hyperframes/f38/PRUEBA1_prompt_rotulos.md, md5 7d2ccdd2…) con la oración 2 del primer párrafo reemplazada por la de F63 A.2 (entrada completa; md5 del SYSTEM 85d094bed6090b14d1802ca97433d982, medido en F63) · antes m01e-6 (F38e §C.1: `respaldo` y `autor` en el formato)
MODELO = "claude-opus-5-5"      # DECISIONES 2026-10-31 14:16 (F63 a ciegas: Opus medium con la entrada completa 8,8; Sonnet 6,3) · antes claude-sonnet-5-5
EFFORT = "medium"               # DECISIONES 2026-10-31 14:16 (high no suma)
SEG_POR_PALABRA_RESPALDO = 0.35  # medido: Vajont ch04 (F36); solo si no hay ninguna voz del narrador (F37 §0: se deriva, voz_utils.seg_por_palabra)
ARCHIVO = "01e_pantalla"
ESTILOS = ("normal", "papel", "cita", "nombre")
TIPOS_DESCARTE = ("voz_lo_dice", "spoiler", "repetido", "otro")      # F37 §A.2 (formato)


def velocidad(seg: dict[str, Any] | None = None) -> dict[str, Any]:
    """F37 §0: segundos por palabra del narrador (voz_utils.seg_por_palabra) o el respaldo, con su origen."""
    seg = seg if seg is not None else seg_por_palabra()
    if seg and seg.get("valor"):
        return {**seg, "origen": f"mediana de {seg['oraciones']} oraciones de {seg['caps']} caps del narrador {seg['voz']}"}
    return {"valor": SEG_POR_PALABRA_RESPALDO, "origen": "respaldo (no hay voces generadas del narrador)"}


# ═══════════════════════ prompt (F38e §C.1: PRUEBA1_prompt_rotulos.md, literal, con la oración 2 de F63 A.2 [F64 Etapa 0]; antes HANDOFF_F36_C_D §C.2) ═══════════════════════

PANTALLA_SYSTEM = """Sos el rotulista de un documental de historia oscura en español. Recibís la narración completa de un video (7 capítulos, oraciones numeradas), la escaleta (qué cuenta cada beat y cuál es el pico de cada capítulo; en `escaleta_video`, la promesa del gancho, las preguntas que el video deja abiertas y dónde las paga, y el pico del video), el archivo del caso (todo lo que encontró la investigación: datos, fechas, citas, personas y lugares, cada uno con su fuente y, en `contexto_fuente`, el fragmento original de la fuente), las versiones en disputa del caso (`disputas`) y una lista de palabras de clima. El `respaldo` se copia siempre del `texto` del dato, nunca de `contexto_fuente`. Escribís lo que va en pantalla para todo el video, de una vez.

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
# F65b §3 A: el botón «sugerir» del QA del papel. Textos del handoff tal cual. NO entran a prompt_md5() ni a PROMPT_VERSION:
# la `clave` de caché de `llamar` no cambia y la próxima corrida del autor no se paga de nuevo.
SUGERIR_N = 3                    # hasta 3 alternativas por clic: DECISIONES 2026-10-31 16:13
SUGERIR_USER = ("\n\nOmar revisó el papel y quiere OTRAS opciones para {cap} beat {beat}. Proponé hasta {n} fichas "
                "alternativas para ESE beat, con las mismas reglas que el papel completo: cada una ancla en una oración "
                "de ese beat, su `respaldo` se copia del `texto` del dato, y dice algo que la voz NO dice en ese momento. "
                "No repitas estos pool_id (ya están en pantalla en este video): {excluidos}. Ordenalas de la que más "
                "aporta a la que menos. Si no hay ninguna que valga la pena, devolvé la lista vacía.")
FORMATO_SUGERIR = ('{"alternativas": [{"pool_id": "D49", "sentence_idx": 17, "palabra": "fisura", '
                   '"etiqueta": "ANCHO DE LA FISURA", "texto": "Más de 1 metro", "respaldo": "…", "autor": "…" | null, '
                   '"aporta": "…"}]}')


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
    if k in ("personajes", "lugares"):          # F64 Etapa 0: un L se escribe como una P, «nombre — rol»
        return f"{it.get('nombre') or ''} — {it.get('rol') or ''}".strip(" —")
    return re.sub(r"\s+", " ", ev.text_of(it)).strip()


def _tipo(it: dict[str, Any]) -> str | None:
    """F64 Etapa 0 (DECISIONES 2026-10-31 14:16, la entrada completa de F63 A.1): TODO ítem del pool entra al archivo,
    por su `_kind`: D (con o sin cifra), T, Q, P y L. Antes (§C.1) solo D con número, T, Q y P: la condición
    `numeros(...)` escondía D85, D34, D03, D129, D10, D20 y D70 de Wittenoom."""
    return {"datos": "D", "cronologia": "T", "citas": "Q", "personajes": "P", "lugares": "L"}.get(it["_kind"])


def contexto_fuente(it: dict[str, Any]) -> str:
    """F64 Etapa 0 (F63 A.1): el fragmento original de la fuente que respalda el ítem: su `cita_literal` o, si no la
    tiene, la de su primera `evidencia`; espacios normalizados. Vacío si no hay."""
    cl = it.get("cita_literal")
    if not cl:
        evd = it.get("evidencia") or []
        cl = (evd[0] or {}).get("cita_literal") if evd else ""
    return re.sub(r"\s+", " ", str(cl or "")).strip()


def cargar(topic_id: str, steps_dir: Path, pool: dict | None = None, log: list[str] | None = None) -> dict[str, Any]:
    """Los archivos de Fase 1 del topic (aclaración 1: los que leen gfx_realizador y el rotulista): escaleta, párrafos
    por cap y beat (01b_narracion_v3), títulos de la partición (01a_skeleton), el pool (00_pool_v3, o el que se pasa)
    y, F64 Etapa 0, la ficha del caso (ficha_caso.json: sus `versiones` y `contradicciones` son las `disputas` de la
    entrada); si no existe, `ficha_caso` None (disputas = {}) y una línea en el log."""
    sd = Path(steps_dir) / topic_id

    def lee(nombre: str) -> dict:
        return json.loads((sd / nombre).read_text(encoding="utf-8"))
    sk = lee("01a_skeleton.json")
    ficha = lee("ficha_caso.json") if (sd / "ficha_caso.json").exists() else None
    if ficha is None and log is not None:
        log.append(f"  m01e: {sd / 'ficha_caso.json'} no existe → la entrada va sin `disputas`")
    return {"topic_id": topic_id, "dir": sd, "escaleta": lee("01a_escaleta.json"),
            "parrafos": lee("01b_narracion_v3.json").get("parrafos") or [],
            "titulos": {int(c["chapter_number"]): str(c.get("title") or "") for c in sk.get("chapters") or []},
            "pool": pool if pool is not None else lee("00_pool_v3.json"), "ficha_caso": ficha}


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
    # F64 Etapa 0 (F63 A.1): después de `cierre`, los cuatro campos de la escaleta que el autor también ve, tal cual
    beats = [{"n": int(b["n"]), "cap": cap_id(b["cap"]), "funcion": str(b.get("funcion") or ""),
              "pico": int(b["n"]) == picos.get(int(b["cap"])), "dato_central": str(b.get("dato_central") or ""),
              "apoyo": [str(x) for x in b.get("datos_apoyo") or []], "cierre": str(b.get("cierre") or "").strip(),
              "emocion": b.get("emocion"), "imagen_sensorial": b.get("imagen_sensorial"),
              "pregunta_abierta": b.get("pregunta_abierta"), "paga": b.get("paga"),
              "flash_forward": bool(b.get("flash_forward"))}      # F64 Etapa 2: lo lee `momentos`; el autor no lo ve
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
        x["contexto_fuente"] = contexto_fuente(it)         # F64 Etapa 0: al final del ítem (el md5 del USER depende del orden)
        archivo.append(x)
    # F64 Etapa 0 (F63 A.1): la escaleta del video (7 campos, None donde falte) y las disputas de la ficha del caso
    escaleta_video = {k: esc.get(k) for k in ("promesa_gancho", "loops", "recuerda_loop", "pico", "humano",
                                             "antagonista", "cierre_humano")}
    fc = carga.get("ficha_caso")
    disputas = {"versiones": fc.get("versiones"), "contradicciones": fc.get("contradicciones")} if fc else {}
    return {"topic_id": carga["topic_id"], "caps": caps, "beats": beats, "archivo": archivo,
            "clima": list(vocabulario), "escaleta_video": escaleta_video, "disputas": disputas,
            "a_pantalla": {str(a.get("id")): str(a.get("por_que") or "") for a in esc.get("a_pantalla") or []},
            "seg_por_palabra": vel, "anios": anios_de([x.get("fecha") for x in todos.values()])}


def _para_modelo(ent: dict[str, Any]) -> dict[str, Any]:
    """Lo que ve el autor: caps, beats (sin `flash_forward`, que es del código), archivo, clima y (F64 Etapa 0)
    `escaleta_video` y `disputas`, en ese orden (el md5 del USER depende del orden)."""
    return {"caps": [{"cap": c["cap"], "titulo": c["titulo"],
                      "oraciones": [{k: s[k] for k in ("idx", "beat", "texto", "caben")} for s in c["oraciones"]]}
                     for c in ent["caps"]],
            "beats": [{k: v for k, v in b.items() if k != "flash_forward"} for b in ent["beats"]],
            "archivo": ent["archivo"], "clima": ent["clima"],
            "escaleta_video": ent.get("escaleta_video") or {}, "disputas": ent.get("disputas") or {}}


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


def momentos_detalle(ent: dict[str, Any]) -> dict[tuple[str, int], dict[str, Any]]:
    """F64 Etapa 2 (HANDOFF_F64 §Etapa 2; reemplaza «el último año que dijo la voz» de F37 §A.1b): el año del relato en
    cada oración = el MÁXIMO año que la voz dijo en ese cap hasta la oración (incluida), sin contar las oraciones de
    los beats con `flash_forward: true` de la escaleta (el gancho que salta al final); mientras el cap no dijo ninguno,
    el valor del cap anterior, heredado, que NO entra al máximo (en cuanto el cap dice su primer año, el relato es el
    máximo de los años de ese cap solamente). Años en cifras o en letras (voz_utils.anios_dichos); las fechas relativas
    («tres días después») no se parsean. Por oración: {anio (None mientras nadie dijo ninguno), cap, idx (la oración
    donde la voz dijo ese año máximo; la del cap anterior si es heredado), heredado}."""
    ff = {b["n"] for b in ent["beats"] if b.get("flash_forward")}
    out: dict[tuple[str, int], dict[str, Any]] = {}
    heredado: dict[str, Any] = {"anio": None, "cap": None, "idx": None}
    for c in ent["caps"]:
        mejor: dict[str, Any] | None = None
        for s in c["oraciones"]:
            if s["beat"] not in ff:
                for y in anios_dichos(s["texto"], ent.get("anios")):
                    if mejor is None or y > mejor["anio"]:
                        mejor = {"anio": y, "cap": c["cap"], "idx": s["idx"]}
            out[(c["cap"], s["idx"])] = {**(mejor or heredado), "heredado": mejor is None}
        if mejor is not None:
            heredado = mejor
    return out


def momentos(ent: dict[str, Any]) -> dict[tuple[str, int], int | None]:
    """El año del relato por oración (F64 Etapa 2, `momentos_detalle`): {(cap, idx): año | None}."""
    return {k: v["anio"] for k, v in momentos_detalle(ent).items()}


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


def validar(resp: Any, ent: dict[str, Any], *, juez: Callable[[list[dict], list[dict]], dict] | None = None
            ) -> dict[str, Any]:
    """§C.3 sobre la respuesta: {beats (lo que queda, por cap y beat), relojes, descartados (del modelo, de la
    validación y del verificador, con regla y motivo), fichas_fuera, marcas, verificador, vuelven, picos_vacios,
    a_pantalla_vacios, motivos, motivos_beat, claves}. F38 §A.1: `motivos_beat` = por motivo, los (cap, beat) que el
    reintento parcial puede cambiar; F64 Etapa 3: `claves` = por motivo, la clave estable (regla, pool_id, cap, beat,
    token) con la que `llamar` mide el progreso.
    F37 §A.1b fecha del relato y §A.1c cita sin fecha; F38c §A.1 `a_pantalla_vacios` (F65a Etapa A: aviso en el JSON y
    el .md, ya no motivo de vuelta ni clave); F38e §C.3 `respaldo`; §C.4 `autor`.
    F64 Etapa 3 (DECISIONES 2026-10-31 14:20): `no_dicho`, `spoiler`, `contradice` y `fecha_relato` no cortan: cada
    coincidencia es una marca (pool_id, cap, beat, sentence_idx, oracion_ancla, etiqueta, texto, respaldo,
    dato_archivo, regla, coincidencia {token, cap, idx, oracion}); los descartes «voz_lo_dice» que `voz_no_lo_dice`
    pone en duda también (regla `voz_lo_dice`, con `caps_que_lo_cuentan`). Con marcas, UNA llamada al `juez`
    (`(marcas, ent["caps"]) → lo que devuelve pantalla_verificador.verificar`; por defecto `verificar`; los tests pasan
    uno falso), después del loop de fichas y de `vuelven`, antes de `picos_vacios`, `a_pantalla_vacios` y `motivos`.
    Ficha «corta» → sale del slot y de `usados_ids`, va a `descartados` con `que: "ficha"`, `quien: "verificador"`, su
    regla original y el motivo del verificador; «pasa» → queda con `juicio_verificador: {regla, motivo, tokens}`.
    Descarte «no_dicho» → sigue en `vuelven` (marcado «falso»); «dicho» → queda como el autor lo escribió. Sin marcas
    no se llama al juez. `motivos` = todo lo que va al reintento, en una lista."""
    from script_engine.gfx_project import ficha_medida
    from script_engine.pantalla_colocar import caracteres
    caps = {c["cap"]: c for c in ent["caps"]}
    orden_caps = [c["cap"] for c in ent["caps"]]
    beats = {b["n"]: b for b in ent["beats"]}
    arch = {x["id"]: x for x in ent["archivo"]}
    pool = ev.items(ent.get("_pool")) if ent.get("_pool") else {}
    lista = {ev.norm(w): w for w in ent["clima"]}
    voz_video = _voz_video(ent)
    mom = momentos_detalle(ent)
    resp = resp if isinstance(resp, dict) else {}
    filas = sorted([b for b in resp.get("beats") or [] if isinstance(b, dict)],
                   key=lambda b: (str(b.get("cap")), _int(b.get("beat")) or 0))
    quedan: dict[tuple[str, int], dict[str, Any]] = {}
    desc: list[dict[str, Any]] = [{"pool_id": d.get("pool_id"), "regla": "modelo", "tipo": d.get("tipo"),
                                   "motivo": d.get("motivo"), "quien": "modelo"}
                                  for d in resp.get("descartados") or [] if isinstance(d, dict)]
    usados_ids: set[str] = set()
    usadas_pal: set[str] = set()
    marcas: list[dict[str, Any]] = []
    fichas_fuera = 0
    for f in filas:
        cap, nb = str(f.get("cap") or ""), _int(f.get("beat"))
        b = beats.get(nb)
        k = (cap, nb if nb is not None else -1)
        slot = quedan.setdefault(k, {"cap": cap, "beat": nb, "funcion": (b or {}).get("funcion"),
                                     "pico": bool((b or {}).get("pico")), "ficha": None, "sello": None})
        fi = f.get("ficha") if isinstance(f.get("ficha"), dict) else None
        if fi:
            motivo, regla, ficha, mf = _validar_ficha(fi, cap, nb, b, slot, caps, orden_caps, arch, pool, voz_video,
                                                      usados_ids, ent, ficha_medida, caracteres, mom)
            if motivo:
                fichas_fuera += 1
                desc.append({"pool_id": fi.get("pool_id"), "cap": cap, "beat": nb, "que": "ficha",
                             "etiqueta": fi.get("etiqueta"), "texto": fi.get("texto"),
                             "sentence_idx": fi.get("sentence_idx"), "regla": regla, "motivo": motivo,
                             "quien": "validación"})
            else:
                slot["ficha"] = ficha
                usados_ids.add(ficha["pool_id"])
                marcas += mf
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
    # §A.1: un `a_pantalla` ya no lleva `beats_que_lo_cuentan` (salvo que sea dato de un beat) → todo el video.
    # F64 Etapa 3: la duda es una marca (`voz_lo_dice`) para el verificador; `vuelven` queda después de su veredicto
    vuelven = []
    dudas: dict[str, dict[str, Any]] = {}
    for d in desc:
        if d.get("quien") != "modelo" or d.get("tipo") != "voz_lo_dice" or d.get("pool_id") in usados_ids:
            continue
        it, x = pool.get(str(d.get("pool_id"))), arch.get(str(d.get("pool_id")))
        if it is None or x is None or str(d["pool_id"]) in dudas:
            continue
        caps_it = {beats[n]["cap"] for n in x["beats_que_lo_cuentan"] if n in beats}
        voz = " ".join(s["texto"] for cc in orden_caps if not caps_it or cc in caps_it for s in caps[cc]["oraciones"])
        falta = voz_no_lo_dice(it, voz, ent.get("anios"))
        if falta:
            pid = str(d["pool_id"])
            dudas[pid] = d
            vuelven.append({"pool_id": pid, "motivo": d.get("motivo"), "falta": falta,
                            "caps": sorted(caps_it) or ["todo el video"], "texto": x["texto"]})
            marcas.append({"que": "descarte", "regla": "voz_lo_dice", "pool_id": pid, "dato_archivo": x["texto"],
                           "motivo_del_autor": d.get("motivo"), "caps_que_lo_cuentan": sorted(caps_it) or ["todo el video"],
                           "falta": falta})
    # F64 Etapa 3: el verificador decide las marcas, en una llamada (sin marcas no se llama)
    ver: dict[str, Any] | None = None
    if marcas:
        ver = (juez or _juez_por_defecto())(marcas, ent["caps"])
        vf = {(str(v.get("pool_id")), str(v.get("cap")), _int(v.get("beat"))): v for v in ver.get("veredictos_fichas") or []}
        vd = {str(v.get("pool_id")): v for v in ver.get("veredictos_descartes") or []}
        for slot in out_beats:
            fi = slot["ficha"]
            caida = aplicar_veredicto(fi, slot["cap"], slot["beat"], marcas, vf) if fi else None
            if caida:
                slot["ficha"] = None
                usados_ids.discard(fi["pool_id"])
                fichas_fuera += 1
                desc.append(caida)
        dichos = {pid for pid, v in vd.items() if v.get("veredicto") == "dicho"}
        vuelven = [v for v in vuelven if v["pool_id"] not in dichos]
        for pid, d in dudas.items():
            if pid in dichos:                               # «dicho»: queda como el autor lo escribió, sin «falso»
                d["verificador"] = f"dicho: {(vd.get(pid) or {}).get('motivo') or ''}".strip()
    for v in vuelven:
        dudas[v["pool_id"]]["verificado"] = f"falso: la voz no dice {v['falta']}"
    picos_vacios = [{"cap": s["cap"], "beat": s["beat"]} for s in out_beats if s["pico"] and not s["ficha"]]
    # F38c §A.1: el beat que tiene `a_pantalla` y cuya ficha no es ninguno de ellos (vacía u otro id); si lleva uno, los
    # demás de ese beat no cuentan («como máximo una ficha por beat» del prompt). F65a: solo aviso, no motivo
    a_pantalla_vacios = []
    for s in out_beats:
        ids = [x for x in ent["archivo"] if (x.get("a_pantalla") or {}).get("beat") == s["beat"]
               and beats.get(s["beat"], {}).get("cap") == s["cap"]]
        if ids and (s["ficha"] or {}).get("pool_id") not in {x["id"] for x in ids}:
            a_pantalla_vacios.append({"cap": s["cap"], "beat": s["beat"],
                                      "ids": [{"id": x["id"], "por_que": x["a_pantalla"]["por_que"]} for x in ids]})
    # F38 §A.1: cada motivo con los beats que puede cambiar el reintento (`motivos_beat`, lista paralela a `motivos`):
    # la ficha caída → su beat (y, si la oración existe y es de otro beat, también ese: ahí puede ir); el pico vacío →
    # su beat; el descarte que vuelve → [] (no tiene beat: va en cualquier beat con motivo). F64 Etapa 3: `claves`.
    # F65a Etapa A: el beat sin su `a_pantalla` ya no es motivo.
    motivos, motivos_beat, claves = [], [], []
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
        toks = [t for ts in (d.get("tokens") or {}).values() for t in ts]
        claves.append((str(d["regla"]), str(d.get("pool_id")), str(d.get("cap")), d.get("beat"), toks[0] if toks else None))
    for v in vuelven:
        motivos.append(f"{v['pool_id']}: dijiste que la voz lo dice («{v['motivo']}»); la voz de {', '.join(v['caps'])} "
                       f"no dice {' ni '.join('«' + str(t) + '»' for t in v['falta'])} («{v['texto']}»): vuelve a ser "
                       f"candidato")
        motivos_beat.append([])
        claves.append(("voz_lo_dice", v["pool_id"]))
    for p in picos_vacios:
        motivos.append(f"el beat {p['beat']} de {p['cap']} es pico y quedó sin ficha")
        motivos_beat.append([(p["cap"], p["beat"])])
        claves.append(("pico", p["cap"], p["beat"]))
    # F65a Etapa A (DECISIONES 2026-10-31 15:49): un beat sin su `a_pantalla` ya NO es motivo de vuelta ni clave; queda
    # en `a_pantalla_vacios` (JSON, ⚠ en el .md). Reemplaza la parte «motivo de reintento» de F38c §A.1.
    return {"beats": out_beats, "relojes": relojes,
            "descartados": desc, "fichas_fuera": fichas_fuera, "marcas": marcas, "verificador": ver, "vuelven": vuelven,
            "picos_vacios": picos_vacios, "a_pantalla_vacios": a_pantalla_vacios, "motivos": motivos,
            "motivos_beat": motivos_beat, "claves": claves}


def aplicar_veredicto(fi: dict[str, Any], cap: str, beat: int | None, marcas: list[dict[str, Any]], vf: dict[tuple, dict]
                      ) -> dict[str, Any] | None:
    """El veredicto del verificador sobre UNA ficha validada (lo usan `validar` y `sugerir`, F65b §3 A.4). `vf` = veredictos
    por (pool_id, cap, beat). Sin marcas no hace nada; «pasa» (o sin veredicto) deja `juicio_verificador` en la ficha y
    devuelve None; «corta» devuelve el descarte (`quien: "verificador"`, con la regla original): sacarla es del que llama."""
    mf = [m for m in marcas if m.get("que") != "descarte" and (m["pool_id"], m["cap"], m["beat"]) == (fi["pool_id"], cap, beat)]
    if not mf:
        return None
    v = vf.get((fi["pool_id"], cap, beat)) or {"veredicto": "pasa", "motivo": "sin veredicto"}
    reglas = sorted({m["regla"] for m in mf})
    tokens = {r: [str(m["coincidencia"]["token"]) for m in mf if m["regla"] == r] for r in reglas}
    if v.get("veredicto") == "corta":
        o = v.get("oracion") or {}
        donde = f" ({o.get('cap')} [{o.get('idx')}])" if isinstance(o, dict) and o.get("cap") is not None else ""
        return {"pool_id": fi["pool_id"], "cap": cap, "beat": beat, "que": "ficha", "etiqueta": fi["etiqueta"],
                "texto": fi["texto"], "sentence_idx": fi["sentence_idx"], "regla": mf[0]["regla"], "reglas": reglas,
                "tokens": tokens, "motivo": f"{v.get('motivo') or ''}{donde}", "quien": "verificador"}
    fi["juicio_verificador"] = {"regla": reglas, "motivo": v.get("motivo"), "tokens": tokens}
    return None


def _juez_por_defecto() -> Callable[[list[dict], list[dict]], dict]:
    from script_engine.pantalla_verificador import verificar
    return verificar


def _int(v: Any) -> int | None:
    try:
        return int(v)
    except (TypeError, ValueError):
        return None


def _validar_ficha(fi: dict, cap: str, nb: int | None, b: dict | None, slot: dict, caps: dict, orden_caps: list[str],
                   arch: dict, pool: dict, voz_video: list[str], usados_ids: set[str], ent: dict,
                   ficha_medida: Callable, caracteres: Callable, mom: dict
                   ) -> tuple[str | None, str | None, dict | None, list[dict]]:
    """(motivo, regla, ficha validada, marcas) de una ficha del papel, en el orden de §C.3 (+ F37 §A.1b/c, F38c §A.2,
    F38e §C.3/C.4). F64 Etapa 3: `fecha_relato`, `no_dicho`, `spoiler` y `contradice` no cortan: dejan marcas para el
    verificador (una por coincidencia); `mom` es `momentos_detalle(ent)`."""
    from script_engine.pantalla_filtros import candado, contradicciones_de, no_dicho, spoiler
    pid = str(fi.get("pool_id") or "")
    c = caps.get(cap)
    si = _int(fi.get("sentence_idx"))
    et = re.sub(r"\s+", " ", str(fi.get("etiqueta") or "")).strip()
    txt = re.sub(r"\s+", " ", str(fi.get("texto") or "")).strip()
    x = arch.get(pid)
    # anclaje
    if c is None or b is None or b["cap"] != cap:
        return f"el beat {nb} no es de {cap}", "anclaje", None, []
    if x is None:
        return f"{pid!r} no está en el archivo", "anclaje", None, []
    if si is None or not 0 <= si < len(c["oraciones"]):
        return f"la oración [{fi.get('sentence_idx')}] no existe en {cap}", "anclaje", None, []
    s = c["oraciones"][si]
    if s["beat"] != nb:
        return f"la oración [{si}] es del beat {s['beat']}, no del {nb}", "anclaje", None, []
    if slot["ficha"]:
        return f"una ficha por beat: el beat {nb} ya tiene {slot['ficha']['pool_id']}", "anclaje", None, []
    estilo = estilo_de(pid, et, ent["a_pantalla"].get(pid, ""))
    tipo = TIPO_DE_ESTILO[estilo]
    autor_arch = str(x.get("autor") or "")
    autor, autor_origen = autor_arch, None
    if tipo == "cita":
        txt = re.sub(r"^[«\"“]+|[»\"”]+$", "", txt).strip()
    # formato
    if not txt or not et:
        return "etiqueta o dato vacío", "formato", None, []
    if tipo == "cita" and not autor_arch:
        return "la cita no tiene autor en el archivo", "formato", None, []
    m = ficha_medida(et, txt)
    if m["kicker"] > 1 or m["title"] > 2:
        return f"etiqueta en {m['kicker']} línea(s) y dato en {m['title']} (1 y 2)", "formato", None, []
    # F38e §C.3a: el respaldo (el fragmento del texto del ítem que el autor copió letra por letra) tiene que ser
    # subcadena de ese texto con la normalización del candado (ev.norm); si falta o no lo es, cae con regla `respaldo`
    resp = re.sub(r"\s+", " ", str(fi.get("respaldo") or "")).strip()
    if not resp:
        return f"la ficha no trae `respaldo` (el fragmento literal del texto de {pid})", "respaldo", None, []
    if ev.norm(resp) not in ev.norm(x["texto"]):
        return f"el respaldo «{resp}» no es un fragmento literal del texto de {pid}", "respaldo", None, []
    if tipo == "cita":                 # F38e §C.4: el autor que se muestra (el del modelo si sus nombres están en el archivo)
        autor, autor_origen = autor_mostrado(str(fi.get("autor") or ""), x)
    it = pool.get(pid)
    vecinas = " ".join(ss["texto"] for ss in c["oraciones"][max(0, si - 1):si + 2])
    # F64 Etapa 3: la marca que va al verificador (una por coincidencia); en una cita, `dato_archivo` es la frase que la
    # ficha muestra y el testimonio entero va en `cita_completa`
    base = {"que": "ficha", "pool_id": pid, "cap": cap, "beat": nb, "sentence_idx": si, "oracion_ancla": s["texto"],
            "etiqueta": et, "texto": txt, "respaldo": resp, "dato_archivo": txt if tipo == "cita" else x["texto"],
            **({"cita_completa": x["texto"]} if tipo == "cita" else {})}
    marcas: list[dict[str, Any]] = []
    # F37 §A.1b: fecha del relato (por año; un testimonio se cuenta después; la oración o su vecina lo sitúan después).
    # F64 Etapa 2: el relato es el máximo del cap (`momentos_detalle`); Etapa 3: donde hoy cortaría, marca
    det = mom.get((cap, si)) or {}
    anio, ahora = anio_de((it or {}).get("fecha")), det.get("anio")
    testimonio = bool((it or {}).get("testimonio"))
    if anio and ahora and anio > ahora and not testimonio and not dice_anio(anio, vecinas, ent.get("anios")):
        oc = caps[det["cap"]]["oraciones"][det["idx"]]["texto"] if det.get("cap") in caps and det.get("idx") is not None else None
        marcas.append({**base, "regla": "fecha_relato",
                       "coincidencia": {"token": str(anio), "relato": ahora, "cap": det.get("cap"), "idx": det.get("idx"),
                                        "oracion": oc}})
    # F37 §A.1c: una cita sin fecha (y que no es testimonio) vale solo si su autor está en la oración o en una vecina
    if x["id"][:1] == "Q" and not anio and not testimonio and not autor_en(autor_arch, x.get("rol") or "", vecinas):
        return (f"cita sin fecha: su autor («{autor_arch}», {x.get('rol') or 'sin rol'}) no aparece en la oración "
                f"[{si}] ni en sus vecinas", "cita_sin_fecha", None, [])
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
    ctx: dict[str, Any] = {"its": {pid: xi}, "x": xi, "pid": pid, "sents": c["oraciones"], "si": si, "s": s,
                           "voz_video": voz_video, "tipo": tipo, "txt": txt, "et": et}
    fil_ent = {"voz_antes": antes}
    mot = candado({}, fil_ent, {**ctx, "x": xi_c, "its": {pid: xi_c}})
    if mot:
        return mot, "candado", None, []

    def coincidencia(t: str, donde: tuple[str, int, str] | None) -> dict[str, Any]:
        return {"token": str(t), "cap": donde[0] if donde else None, "idx": donde[1] if donde else None,
                "oracion": donde[2] if donde else None}
    vec = [(cap, ss["idx"], ss["texto"]) for ss in c["oraciones"][max(0, si - 1):si + 2]]
    todo = [(cc, ss["idx"], ss["texto"]) for cc in orden_caps for ss in caps[cc]["oraciones"]]
    # no_dicho: la coincidencia en la oración ancla ± 1 (F40 §A: en el gancho, la cifra que la voz dice en otra oración)
    if no_dicho({}, fil_ent, ctx):
        for t in ctx["dichos"]:
            marcas.append({**base, "regla": "no_dicho", "coincidencia": coincidencia(t, _donde(t, vec) or _donde(t, todo))})
    despues = c["oraciones"][si + 1:] + [ss for cc in orden_caps[k + 1:] for ss in caps[cc]["oraciones"]]
    sp_ctx = {**ctx, "sents": c["oraciones"][:si + 1] + despues}               # (c): en ese cap o en los siguientes
    if spoiler({}, fil_ent, sp_ctx):
        tras = [(cap, ss["idx"], ss["texto"]) for ss in c["oraciones"][si + 1:]] + \
               [(cc, ss["idx"], ss["texto"]) for cc in orden_caps[k + 1:] for ss in caps[cc]["oraciones"]]
        # (en el gancho, la cifra que la voz dice en un cap siguiente ya salió como no_dicho —F40 §A—: una marca por
        # coincidencia, no dos por el mismo (token, cap, idx))
        ya = {(m["coincidencia"]["token"], m["coincidencia"]["cap"], m["coincidencia"]["idx"]) for m in marcas}
        for t in sp_ctx["spoil"]:
            co = coincidencia(t, _donde(t, tras))
            if (co["token"], co["cap"], co["idx"]) not in ya:
                marcas.append({**base, "regla": "spoiler", "coincidencia": co})
    # F38c §A.2: la cifra que contradice la voz (pantalla_filtros.contradicciones, la del chequeo 5 de Fase 2, con la
    # oración ancla ± 1 como vecindad); el token es la cifra de la voz
    cons = contradicciones_de(f"{et} {txt}", voz_video, cerca=[t for _, _, t in vec])
    for t in dict.fromkeys(q["token"] for q in cons):
        o = next(q["oracion"] for q in cons if q["token"] == t)
        donde = next(((cc, i, tt) for cc, i, tt in vec + todo if tt.strip() == o), None)
        marcas.append({**base, "regla": "contradice", "coincidencia": coincidencia(t, donde)})
    if pid in usados_ids:
        return f"{pid} ya va en otro beat del video", "una_vez", None, []
    n = caracteres(tipo, et, txt, autor)
    if n > s["caben"]:
        # F38d §A.2.2: el desglose que mide el código (en una cita, el autor + 5 de comillas y raya) y el mayor `caben`
        # de las oraciones del beat con su oración (empate: la primera): data de la entrada, no regla
        m, sm = max(((ss["caben"], -ss["idx"]) for ss in c["oraciones"] if ss["beat"] == nb), default=(s["caben"], -si))
        cuenta = (f"etiqueta {len(et)} + dato {len(txt)} + autor {len(autor)} (con comillas y raya)" if tipo == "cita"
                  else f"etiqueta {len(et)} + dato {len(txt)}")
        return (f"{cuenta} = {n} caracteres y en la oración [{si}] caben {s['caben']}; en este beat caben como máximo "
                f"{m} (oración [{-sm}])"), "caben", None, []
    pal = str(fi.get("palabra") or "").strip()
    en = any(ev.norm(pal) == ev.norm(re.sub(r"[^\w]", "", w)) for w in palabras(s["texto"])) if pal else False
    return None, None, {"pool_id": pid, "sentence_idx": si, "palabra": pal, "palabra_en_oracion": en,
                        "etiqueta": et, "texto": txt, "respaldo": resp, "estilo": estilo,
                        **({"autor": autor, "autor_origen": autor_origen} if tipo == "cita" else {}),
                        "aporta": str(fi.get("aporta") or ""), "oracion": s["texto"], "caracteres": n,
                        "caben": s["caben"], "anio": anio, "relato": ahora}, marcas


# ═══════════════════════ llamada (§C.2) ═══════════════════════

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
           juez: Callable[[list[dict], list[dict]], dict] | None = None, log: list[str] | None = None) -> dict[str, Any]:
    """La llamada con caché y las vueltas de reintento, sin tope en dólares (F64 Etapa 1, DECISIONES 2026-10-31 13:07:
    el costo se informa en el raw, el .json y el .md; nunca frena). Devuelve {clave, intentos, final, validacion, usd
    (autor + verificador), usd_autor, usd_verificador, tokens_in, motivos, motivos_beat, claves, verificador, reintento}.
    `post` (tests) reemplaza al POST de la API del autor: recibe el body y devuelve el mensaje {content, usage,
    stop_reason}; cada llamada al POST es un intento, en orden. `juez` (tests) reemplaza al verificador; por defecto
    `pantalla_verificador.verificar` con el mismo `post` y `log` (F64 Etapa 3).
    F37 §A.5: los motivos van juntos (fichas caídas por el código y por el verificador, descartes «la voz lo dice» que
      vuelven, picos sin ficha; F65a: ya no los `a_pantalla` vacíos, que quedan como aviso). F38 §A.1: el reintento es parcial (`fusionar`): solo los beats
      con motivo (`beats_con_motivo`). El JSON que no parsea sigue con el reintento de JSON completo de siempre (no es
      parcial) y esa respuesta es final (F38d §A.1.6). F38b: los motivos son solo los de la validación en papel.
    F38d §A.1 / F64 Etapa 3: VUELTAS. Hay otra vuelta mientras haya motivos y el conjunto de sus CLAVES
      (regla, pool_id, cap, beat, token; el descarte que vuelve ("voz_lo_dice", pool_id); pico ("pico", cap, beat);
      F65a: el beat sin su a_pantalla ya no es motivo ni clave) no sea igual al de NINGUNA vuelta anterior (no solo la inmediata: evita el
      ciclo A→B→A); el texto con el motivo del verificador se le manda al autor igual. Cierres (`reintento.cierre`):
      «sin motivos», «sin progreso», «sin JSON», «sin beat»; `cerrar` guarda el papel y SU validación: ya no hay una
      validación distinta al cerrar. `reintento.vueltas`: por vuelta {vuelta, beats, motivos, claves, aplicados,
      ignorados, usd}; `beats`, `aplicados` e `ignorados` de `reintento` son la unión de todas las vueltas.
    Caché (F64 Etapa 3): el raw guarda cada pedido y respuesta del verificador (`verificador`: [{pedido_md5, marcas,
      veredictos, usage, usd, segundos}]). En el hit de caché, `validar` se corre con un juez que busca en el raw por
      `pedido_md5` y devuelve los veredictos guardados; si uno no está (el código de `validar` cambió) se llama al
      verificador y se anota «caché parcial» (el raw se completa). Nunca se paga una llamada del verificador por un raw
      cuya clave coincide y cuyo `pedido_md5` está guardado."""
    import claude_helpers as hx
    from script_engine import pantalla_verificador as pv
    log = log if log is not None else []
    user = pedido(ent)
    clave = hashlib.md5(f"{PROMPT_VERSION}|{MODELO}|{EFFORT}|{PANTALLA_SYSTEM}|{user}".encode("utf-8")).hexdigest()
    raw_f = Path(out_dir) / f"{ARCHIVO}.raw.json"
    try:
        prev = json.loads(raw_f.read_text(encoding="utf-8")) if raw_f.exists() else None
    except (OSError, ValueError):
        prev = None
    registro: list[dict[str, Any]] = []                      # cada llamada al verificador de esta corrida
    juez_real = juez or functools.partial(pv.verificar, post=post, log=log)

    def juez_registrado(marcas: list[dict], caps: list[dict]) -> dict[str, Any]:
        v = juez_real(marcas, caps)
        vf, vd = v.get("veredictos_fichas") or [], v.get("veredictos_descartes") or []
        registro.append({"pedido_md5": v.get("pedido_md5"), "marcas": marcas,
                         "veredictos": {"fichas": vf, "descartes": vd, "ignorados": v.get("ignorados") or [],
                                        "sin_veredicto": v.get("sin_veredicto") or []},
                         "usage": v.get("usage"), "usd": v.get("usd") or 0.0, "segundos": v.get("segundos") or 0.0,
                         "intentos": v.get("intentos"), "error": v.get("error")})
        log.append(f"  m01e verificador: {len(marcas)} marca(s) → corta "
                   f"{sum(1 for x in vf if x.get('veredicto') == 'corta')} · pasa "
                   f"{sum(1 for x in vf if x.get('veredicto') == 'pasa')} · dicho "
                   f"{sum(1 for x in vd if x.get('veredicto') == 'dicho')} · no_dicho "
                   f"{sum(1 for x in vd if x.get('veredicto') == 'no_dicho')} · US$ {v.get('usd') or 0:.4f}"
                   + (f" · {v['error']}" if v.get("error") else ""))
        return v

    if prev and prev.get("clave") == clave and prev.get("final") is not None:
        guardados = {r.get("pedido_md5"): r for r in prev.get("verificador") or []}
        parcial: list[str] = []

        def juez_cache(marcas: list[dict], caps: list[dict]) -> dict[str, Any]:
            h = pv.pedido_md5(pv.pedido(marcas, caps))
            r = guardados.get(h)
            if r:
                vs = r.get("veredictos") or {}
                return {"veredictos_fichas": vs.get("fichas") or [], "veredictos_descartes": vs.get("descartes") or [],
                        "ignorados": vs.get("ignorados") or [], "sin_veredicto": vs.get("sin_veredicto") or [],
                        "usage": r.get("usage"), "usd": 0.0, "segundos": 0.0, "pedido_md5": h, "intentos": 0, "cache": True}
            parcial.append(h)
            return juez_registrado(marcas, caps)
        prev["validacion"] = validar(prev["final"], ent, juez=juez_cache)      # determinista: el código de hoy
        prev["usd_cache_parcial"] = round(sum(r.get("usd") or 0.0 for r in registro), 5)
        if parcial:
            prev["verificador"] = (prev.get("verificador") or []) + registro
            prev["usd_verificador"] = round((prev.get("usd_verificador") or 0.0) + prev["usd_cache_parcial"], 5)
            prev["usd"] = round((prev.get("usd_autor") or prev.get("usd") or 0.0) + prev["usd_verificador"], 5)
            raw_f.write_text(json.dumps(prev, ensure_ascii=False, indent=1), encoding="utf-8")
            log.append(f"  m01e: caché parcial: {len(parcial)} pedido(s) del verificador no estaban en el raw → verificador "
                       f"llamado (US$ {prev['usd_cache_parcial']:.4f})")
        log.append(f"  m01e: caché ({len(prev.get('intentos') or [])} intento(s) del autor, US$ 0)")
        return {**prev, "cache": True}
    out: dict[str, Any] = {"clave": clave, "modelo": MODELO, "effort": EFFORT, "prompt_version": PROMPT_VERSION,
                           "prompt_md5": prompt_md5(), "entrada_md5": entrada_md5(ent), "intentos": [], "final": None,
                           "validacion": None, "usd": 0.0, "usd_autor": 0.0, "usd_verificador": 0.0, "motivos": [],
                           "motivos_beat": [], "claves": [], "verificador": registro,
                           "reintento": {"tipo": None, "beats": [], "aplicados": [], "ignorados": [], "sin_beat": [],
                                         "vueltas": [], "cierre": None}}

    def juez_w(marcas: list[dict], caps: list[dict]) -> dict[str, Any]:
        v = juez_registrado(marcas, caps)
        out["usd_verificador"] = round(out["usd_verificador"] + (v.get("usd") or 0.0), 5)
        out["usd"] = round(out["usd_autor"] + out["usd_verificador"], 5)
        return v

    def autor(pedido_k: str, k: int) -> dict | None:
        """Una llamada del autor: la respuesta JSON o None (sin tope: F64 Etapa 1). F65b §2.4: con caché (SYSTEM + USER de
        entrada; lo que sigue de una vuelta va en un segundo bloque)."""
        resto = pedido_k[len(user):] if pedido_k.startswith(user) else None
        body = hx.body_cacheado(PANTALLA_SYSTEM, user if resto is not None else pedido_k, MODELO, EFFORT, resto=resto)
        t0 = time.time()
        r = (post or hx._post)(body)
        u = r.get("usage") or {}
        usd = round(hx.cost_of(MODELO, u), 5)
        if post is None:
            hx._track(r.get("model") or MODELO, u, "m01e_pantalla")    # al cost_tracker (el ledger del paso)
        out["usd_autor"] = round(out["usd_autor"] + usd, 5)
        out["usd"] = round(out["usd_autor"] + out["usd_verificador"], 5)
        out["tokens_in"] = out.get("tokens_in") or hx.tokens_entrada(u)
        txt = "".join(c.get("text") or "" for c in r.get("content") or [] if c.get("type") == "text")
        resp = primer_json(txt)
        out["intentos"].append({"pedido": pedido_k if k else "(el USER de entrada)", "texto": txt, "respuesta": resp,
                                "usage": u, "stop": r.get("stop_reason"), "usd": usd,
                                "segundos": round(time.time() - t0, 1)})
        log.append(f"  m01e intento {k + 1}: in {hx.tokens_entrada(u)} (caché: escrito {u.get('cache_creation_input_tokens') or 0}, "
                   f"leído {u.get('cache_read_input_tokens') or 0}) · out {u.get('output_tokens')} · "
                   f"US$ {usd:.4f} · {'JSON' if resp is not None else 'SIN JSON'}")
        return resp

    def escribir() -> None:
        raw_f.parent.mkdir(parents=True, exist_ok=True)
        raw_f.write_text(json.dumps({**out, "entrada": _para_modelo(ent)}, ensure_ascii=False, indent=1),
                         encoding="utf-8")

    def cerrar(papel: dict[str, Any], val: dict[str, Any], por: str | None) -> dict[str, Any]:
        """F64 Etapa 3: el papel y SU validación (la última), con el motivo del cierre; escribe el raw."""
        out["reintento"]["cierre"] = por
        out["final"], out["validacion"] = papel, val
        escribir()
        return out

    def resumen(val: dict[str, Any]) -> str:
        return (f"fichas fuera {val['fichas_fuera']} · marcas {len(val['marcas'])} · cortadas por el verificador "
                f"{sum(1 for d in val['descartados'] if d.get('quien') == 'verificador')} · vuelven {len(val['vuelven'])} · "
                f"picos vacíos {len(val['picos_vacios'])}")

    resp = autor(user, 0)
    if resp is None:                                  # JSON inválido: el reintento de JSON completo de siempre
        out["reintento"]["tipo"] = "json"
        stop = out["intentos"][-1].get("stop")
        resp = autor(_reintento(user, [f"la respuesta no es JSON válido (stop_reason {stop})"]), 1)
        if resp is None:
            escribir()
            raise SinJSON(f"dos respuestas sin JSON válido; la cruda en {raw_f}")
        return cerrar(resp, validar(resp, ent, juez=juez_w), None)   # final: sin vueltas (A.1.6), `cierre` None
    val = validar(resp, ent, juez=juez_w)
    log.append(f"  m01e intento 1 validado: {resumen(val)}")
    out["motivos"] = val["motivos"]
    out["motivos_beat"] = [list(map(tuple, bs)) for bs in val["motivos_beat"]]
    out["claves"] = [list(c) for c in val["claves"]]
    rt = out["reintento"]
    papel, vistas, k = resp, [], 0
    while True:
        motivos = val["motivos"]
        mb = [list(map(tuple, bs)) for bs in val["motivos_beat"]]
        claves = {tuple(c) for c in val["claves"]}
        if not motivos:
            return cerrar(papel, val, "sin motivos")
        if claves in vistas:                          # derivado: otra vuelta no tiene nada nuevo que decirle al autor
            log.append(f"  m01e: las claves de los motivos después de la vuelta {k} ya se le mandaron al autor "
                       f"(vuelta {vistas.index(claves)}) → cierra (sin progreso)")
            return cerrar(papel, val, "sin progreso")
        vistas.append(claves)
        beats_m = beats_con_motivo(mb)
        if not beats_m:                               # solo motivos sin beat: no hay dónde proponer nada
            rt["sin_beat"] = motivos
            log.append(f"  m01e: {len(motivos)} motivo(s) sin beat → sin {'otra vuelta' if k else 'reintento'} "
                       f"(anotados)")
            return cerrar(papel, val, "sin beat")
        k += 1
        rt["tipo"] = "parcial"
        r = autor(_reintento_parcial(user, papel, motivos, beats_m), k)
        if r is None:                                 # sin JSON: queda la vuelta anterior
            rt["vueltas"].append({"vuelta": k, "beats": beats_m, "motivos": motivos, "claves": sorted(map(list, claves)),
                                  "aplicados": [], "ignorados": [], "usd": out["intentos"][-1]["usd"], "sin_json": True})
            rt["beats"] = _union_beats(rt["beats"], beats_m)
            out["error"] = (f"la vuelta {k} no devolvió JSON: queda "
                            + ("el intento 1" if k == 1 else f"la vuelta {k - 1}"))
            return cerrar(papel, val, "sin JSON")
        fus, aplicados, ignorados = fusionar(papel, r, beats_m)
        rt["vueltas"].append({"vuelta": k, "beats": beats_m, "motivos": motivos, "claves": sorted(map(list, claves)),
                              "aplicados": aplicados, "ignorados": ignorados, "usd": out["intentos"][-1]["usd"]})
        rt["beats"] = _union_beats(rt["beats"], beats_m)
        rt["aplicados"] = rt["aplicados"] + aplicados
        rt["ignorados"] = rt["ignorados"] + ignorados
        if ignorados:
            log.append(f"  m01e vuelta {k}: {len(aplicados)} cambio(s) aplicados · {len(ignorados)} ignorado(s)")
        papel = fus
        val = validar(papel, ent, juez=juez_w)
        log.append(f"  m01e vuelta {k} validada: {resumen(val)}")


def _union_beats(a: list[tuple[str, int]], b: list[tuple[str, int]]) -> list[tuple[str, int]]:
    return sorted({(str(c), int(n)) for c, n in list(a) + list(b)}, key=lambda x: (x[0], x[1]))


# ═══════════════════════ salida ═══════════════════════

def armar(ent: dict[str, Any], res: dict[str, Any]) -> dict[str, Any]:
    v = res["validacion"]
    cache = bool(res.get("cache"))
    rt = res.get("reintento") or {}
    return {"topic_id": ent["topic_id"], "prompt_version": PROMPT_VERSION, "prompt_md5": prompt_md5(),
            "modelo": res["modelo"], "effort": res["effort"], "entrada_md5": res.get("entrada_md5"),
            "intentos": len(res.get("intentos") or []),
            # F64: el costo (autor + verificador) se informa; en un hit de caché solo lo que pagó la caché parcial
            "usd": (res.get("usd") or 0.0) if not cache else (res.get("usd_cache_parcial") or 0.0),
            "usd_autor": (res.get("usd_autor") or 0.0) if not cache else 0.0,
            "usd_verificador": (res.get("usd_verificador") or 0.0) if not cache else (res.get("usd_cache_parcial") or 0.0),
            "tokens_in": res.get("tokens_in"), "caps": [{"cap": c["cap"], "titulo": c["titulo"],
                                                         "oraciones": [s["texto"] for s in c["oraciones"]]}
                                                        for c in ent["caps"]],
            "beats": v["beats"], "relojes": v["relojes"],
            "descartados": v["descartados"],
            # F37: de dónde salen las medidas y qué pasó en el reintento (motivos enviados, por vuelta, por qué cerró)
            "seg_por_palabra": ent.get("seg_por_palabra"), "error": res.get("error"),
            "por_intento": [{"tokens_in": sum(int((i.get("usage") or {}).get(k) or 0) for k in
                                              ("input_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")),
                             "tokens_out": (i.get("usage") or {}).get("output_tokens"), "usd": i.get("usd"),
                             "segundos": i.get("segundos")} for i in res.get("intentos") or []],
            "reintento": {"motivos": res.get("motivos") or [],
                          **{k: rt.get(k) for k in ("tipo", "beats", "aplicados", "ignorados", "sin_beat", "vueltas",
                                                    "cierre")}},
            # F64 Etapa 3: el verificador, llamada por llamada (lo que juzgó y lo que costó) y las marcas de la validación
            "verificador": [{"pedido_md5": r.get("pedido_md5"), "marcas": len(r.get("marcas") or []),
                             "pasa": sum(1 for x in (r.get("veredictos") or {}).get("fichas") or [] if x.get("veredicto") == "pasa"),
                             "corta": sum(1 for x in (r.get("veredictos") or {}).get("fichas") or [] if x.get("veredicto") == "corta"),
                             "dicho": sum(1 for x in (r.get("veredictos") or {}).get("descartes") or [] if x.get("veredicto") == "dicho"),
                             "no_dicho": sum(1 for x in (r.get("veredictos") or {}).get("descartes") or [] if x.get("veredicto") == "no_dicho"),
                             "usd": r.get("usd"), "segundos": r.get("segundos"), "error": r.get("error")}
                            for r in res.get("verificador") or []],
            "marcas": v.get("marcas") or [],
            "picos_vacios": v.get("picos_vacios") or [],
            "a_pantalla_vacios": v.get("a_pantalla_vacios") or []}         # F38c §A.1: después del reintento


def _por_que_falta(p: dict[str, Any], pid: str) -> str:
    """F38c §A.1: por qué un `a_pantalla` no está en su beat: el descarte del autor, o lo que lo sacó en la validación
    (lo puso y cayó), o «el autor no lo puso»."""
    d = next((d for d in p.get("descartados") or [] if d.get("pool_id") == pid and d.get("quien") == "modelo"), None)
    if d:
        return f"el autor lo descartó{' [' + str(d['tipo']) + ']' if d.get('tipo') else ''}: {d.get('motivo')}"
    d = next((d for d in p.get("descartados") or [] if d.get("pool_id") == pid
              and d.get("quien") in ("validación", "verificador")), None)
    if d:
        return f"lo puso y cayó: {d['regla']}{' (verificador)' if d.get('quien') == 'verificador' else ''}: {d['motivo']}"
    return "el autor no lo puso"


def a_markdown(p: dict[str, Any]) -> str:
    """Una línea por beat (ficha · sello) y los relojes; después lo que cayó, con motivo. F37: el año de cada
    ficha y el momento del relato, los picos sin ficha (⚠), el reintento (motivos enviados, por vuelta, por qué cerró).
    F38c §A.1: el beat que después del reintento sigue sin ninguno de sus `a_pantalla` lleva ⚠, con el descarte del
    autor si lo hay (o lo que lo sacó en la validación) o «el autor no lo puso»: no se fuerza ni se corta nada.
    F64 Etapa 3: lo que el verificador salvó («verificador: pasa») y lo que cortó (en «Lo que cayó», con «(verificador)»),
    y la sección «Verificador» con cada llamada."""
    sp = p.get("seg_por_palabra") or {}
    pi = " · ".join(f"intento {k + 1}: in {i.get('tokens_in')} · out {i.get('tokens_out')} · US$ {i.get('usd') or 0:.4f}"
                    for k, i in enumerate(p.get("por_intento") or []))
    lines = [f"# Guion de pantalla en papel — {p['topic_id']}", "",
             f"`m01e_pantalla` {p['prompt_version']} (md5 del prompt `{p['prompt_md5']}`) · {p['modelo']} {p['effort']} · "
             f"{p['intentos']} intento(s) · US$ {p['usd']:.4f} (autor {p.get('usd_autor') or 0:.4f} + verificador "
             f"{p.get('usd_verificador') or 0:.4f}) · tokens de entrada {p.get('tokens_in')}", ""]
    if sp or pi:
        lines += [f"Segundos por palabra {sp.get('valor')} ({sp.get('origen')}){' · ' + pi if pi else ''}"
                  + (f" · **{p['error']}**" if p.get("error") else ""), ""]
    fichas = sum(1 for b in p["beats"] if b["ficha"])
    sellos = sum(1 for b in p["beats"] if b["sello"])
    lines += [f"Totales: {fichas} fichas · {sellos} sellos · {len(p['relojes'])} relojes · "
              f"{len(p['descartados'])} descartados", ""]
    for c in p["caps"]:
        lines += [f"## {c['cap']} — {c['titulo']}", ""]
        for b in [b for b in p["beats"] if b["cap"] == c["cap"]]:
            f, s = b["ficha"], b["sello"]
            jv = (f or {}).get("juicio_verificador") or {}
            fi = (f"ficha **{f['pool_id']}** [{f['estilo']}] «{f['etiqueta']} · {f['texto']}»"
                  + (f" — {f['autor']}" + (f" (autor: {f['autor_origen']})" if f.get("autor_origen") else "")
                     if f.get("autor") else "")
                  + f" en [{f['sentence_idx']}] sobre «{f['palabra']}»{'' if f['palabra_en_oracion'] else ' (no está en la oración)'}"
                  f" ({f['caracteres']}/{f['caben']} car.)"
                  + (f" · respaldo: «{f['respaldo']}»" if f.get("respaldo") else "")
                  + (f" · año {f.get('anio') or '—'} / relato {f.get('relato') or '—'}" if "anio" in f else "")
                  + (f" · verificador: pasa ({', '.join(jv.get('regla') or [])} {jv.get('tokens')}) — {jv.get('motivo')}"
                     if jv else "")
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
    val = [d for d in p["descartados"] if d.get("quien") in ("validación", "verificador")]
    lines += [f"- {d.get('cap')} beat {d.get('beat')} · {d['que']} {d.get('pool_id') or ''} «"
              f"{(str(d.get('etiqueta')) + ' · ') if d.get('etiqueta') else ''}{d.get('texto')}» en "
              f"[{d.get('sentence_idx')}] → **{d['regla']}**"
              + (f" (verificador; marcas {', '.join(d.get('reglas') or [])} {d.get('tokens')})" if d.get("quien") == "verificador" else "")
              + f": {d['motivo']}" for d in val] or ["- (nada)"]
    ver = p.get("verificador") or []
    if ver or p.get("marcas"):
        lines += ["", "## Verificador", "",
                  f"- {len(ver)} llamada(s) · US$ {sum(x.get('usd') or 0 for x in ver):.4f} · marcas de la última validación: "
                  f"{len(p.get('marcas') or [])}"]
        lines += [f"- llamada {k + 1}: {x.get('marcas')} marca(s) → fichas pasa {x.get('pasa')} · corta {x.get('corta')} · "
                  f"descartes dicho {x.get('dicho')} · no_dicho {x.get('no_dicho')} · US$ {x.get('usd') or 0:.4f} · "
                  f"{x.get('segundos') or 0} s · pedido {str(x.get('pedido_md5') or '')[:8]}…"
                  + (f" · **{x['error']}**" if x.get("error") else "") for k, x in enumerate(ver)]
        for m in p.get("marcas") or []:
            if m.get("que") == "descarte":
                lines.append(f"  - descarte {m['pool_id']} («{m.get('dato_archivo')}»; el autor: «{m.get('motivo_del_autor')}»; "
                             f"la voz de {', '.join(m.get('caps_que_lo_cuentan') or [])} no dice {m.get('falta')})")
            else:
                co = m.get("coincidencia") or {}
                lines.append(f"  - {m['pool_id']} ({m['cap']} beat {m['beat']}, [{m['sentence_idx']}]) «{m['etiqueta']} · "
                             f"{m['texto']}»: {m['regla']} «{co.get('token')}»"
                             + (f" en {co.get('cap')} [{co.get('idx')}] («{str(co.get('oracion') or '')[:80]}»)" if co.get("cap") else "")
                             + (f" (relato {co.get('relato')})" if "relato" in co else ""))
    rt = p.get("reintento") or {}
    if rt.get("motivos"):
        lines += ["", "## Reintento: los motivos que se le mandaron al autor", ""]
        lines += [f"- {m}" for m in rt["motivos"]]
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
            if vu.get("claves") is not None:          # F64 Etapa 3: las claves con que se mide el progreso
                lines += ["- claves: " + "; ".join("(" + ", ".join(str(x) for x in c) + ")" for c in vu["claves"])]
            lines += [f"- aplicados: {ap or '—'}"]
            lines += [f"- ignorado: {i.get('cap')} beat {i.get('beat')} — {i['motivo']}" for i in vu.get("ignorados") or []]
        if rt.get("sin_beat"):
            lines += ["", "### Motivos sin beat (no hubo reintento)", ""] + [f"- {m}" for m in rt["sin_beat"]]
    if rt.get("cierre"):                              # F38d §A.1.3 / F64: por qué cerró
        nv = len(rt.get("vueltas") or [])
        lines += ["", "## Cierre del reintento", "",
                  f"- cerró por: **{rt.get('cierre')}** (después de {nv} vuelta{'s' if nv != 1 else ''})"]
    lines += ["", "## Descartados por el modelo", ""]
    lines += [f"- {d.get('pool_id')}" + (f" [{d['tipo']}]" if d.get("tipo") else "") + f": {d.get('motivo')}"
              + (f" — **{d['verificado']}**" if d.get("verificado") else "")
              + (f" — verificador: {d['verificador']}" if d.get("verificador") else "")
              for d in p["descartados"] if d.get("quien") == "modelo"] or ["- (ninguno)"]
    if p.get("aviso_narracion"):                      # F66: al final, donde Omar ya lee: la cadena siguió con esto
        from script_engine.narracion_verificador import aviso_txt
        lines += ["", "## ⚠ Aviso de la verificación de la narración", "", aviso_txt(p["aviso_narracion"]), ""]
        lines += [f"- {q.get('cap')} [{q.get('oracion')}] «{q.get('texto')}»: {q.get('afirmacion')} · {', '.join(q.get('ids') or [])}"
                  f" · «{q.get('fragmento')}»" for q in p["aviso_narracion"]]
    return "\n".join(lines) + "\n"


def sugerir(topic_id: str, cap: str, beat: int, n: int = SUGERIR_N, *, steps_dir: Path | None = None,
            post: Callable[[dict], dict] | None = None, juez: Callable[[list[dict], list[dict]], dict] | None = None,
            log: list[str] | None = None) -> dict[str, Any]:
    """F65b §3 A (DECISIONES 2026-10-31 16:13): hasta `n` fichas alternativas para UN beat, del mismo autor (MODELO, EFFORT,
    PANTALLA_SYSTEM) con la misma entrada, ya pasadas por los candados de `validar` y por UNA llamada al verificador. No toca
    el papel; deja el pedido y la respuesta en 01e_sugerir.log.jsonl. Candado: la entrada del autor del raw tiene que ser la
    del papel (ValueError si no). Para validar hace falta lo que el raw no guarda (el pool, `a_pantalla`, `anios`,
    `flash_forward`): se rearma con `cargar`/`entrada` y tiene que dar el mismo md5, si no ValueError. Devuelve {cap, beat,
    alternativas (fichas validadas), descartadas [{ficha, motivo, regla, quien}], excluidos, usd, usd_autor, usd_verificador,
    segundos, tokens_in, usage, error}. `post`/`juez` (tests) reemplazan al POST y al verificador."""
    import copy
    import functools

    import claude_helpers as hx
    from script_engine import pantalla_verificador as pv
    from script_engine.m01a_skeleton import STEPS_DIR
    log = log if log is not None else []
    sd = Path(steps_dir or STEPS_DIR)
    d = sd / topic_id
    papel = cargar_papel(topic_id, sd)
    raw_f = d / f"{ARCHIVO}.raw.json"
    if papel is None or not raw_f.exists():
        raise ValueError(f"{topic_id}: no hay papel ni raw para sugerir")
    raw = json.loads(raw_f.read_text(encoding="utf-8"))
    nb = _int(beat)
    if not any(b["cap"] == cap and b["beat"] == nb for b in papel["beats"]):
        raise ValueError(f"no hay beat {beat} en {cap}")
    h = entrada_md5(raw["entrada"])
    if h != papel.get("entrada_md5"):
        raise ValueError(f"el raw no es de este papel: entrada {h} ≠ {papel.get('entrada_md5')}")
    carga = cargar(topic_id, sd)
    ent = entrada(carga, raw["entrada"]["clima"], papel.get("seg_por_palabra"))
    ent["_pool"] = carga["pool"]
    if entrada_md5(ent) != h:
        raise ValueError(f"la entrada de hoy no es la del papel ({entrada_md5(ent)} ≠ {h}): la narración o el pool cambiaron")
    excluidos = sorted({b["ficha"]["pool_id"] for b in papel["beats"] if b.get("ficha")})
    user = pedido(raw["entrada"])
    resto = ("\n\nTU RESPUESTA ANTERIOR (el papel completo, como contexto):\n" + json.dumps(raw["final"], ensure_ascii=False)
             + SUGERIR_USER.format(cap=cap, beat=nb, n=n, excluidos=", ".join(excluidos))
             + "\n\nFormato de salida: " + FORMATO_SUGERIR)
    t0 = time.time()
    usd_autor = 0.0
    usos: list[dict] = []
    crudos: list[str] = []
    resp, stop = None, None
    for k in range(2):                                # sin JSON → 1 reintento, como el autor
        r = (post or hx._post)(hx.body_cacheado(PANTALLA_SYSTEM, user, MODELO, EFFORT, resto=(
            resto if k == 0 else _reintento(resto, [f"la respuesta no es JSON válido (stop_reason {stop})"]))))
        u = r.get("usage") or {}
        usos.append(u)
        usd_autor = round(usd_autor + hx.cost_of(MODELO, u), 5)
        if post is None:
            hx._track(r.get("model") or MODELO, u, "m01e_sugerir")
        stop = r.get("stop_reason")
        txt = "".join(c.get("text") or "" for c in r.get("content") or [] if c.get("type") == "text")
        crudos.append(txt)
        resp = primer_json(txt)
        log.append(f"  sugerir {cap} beat {nb} intento {k + 1}: in {hx.tokens_entrada(u)} (caché: escrito "
                   f"{u.get('cache_creation_input_tokens') or 0}, leído {u.get('cache_read_input_tokens') or 0}) · out "
                   f"{u.get('output_tokens')} · US$ {hx.cost_of(MODELO, u):.4f} · {'JSON' if resp is not None else 'SIN JSON'}")
        if resp is not None:
            break
    propuestas = [a for a in (resp or {}).get("alternativas") or [] if isinstance(a, dict)][:n]
    descartadas: list[dict[str, Any]] = []
    candidatas: list[dict[str, Any]] = []
    marcas: list[dict[str, Any]] = []
    vistos: set[str] = set()
    for fi in propuestas:
        pid = str(fi.get("pool_id") or "")
        if pid in excluidos or pid in vistos:         # en código, antes de `validar`: ver §3 A.2 (una_vez no alcanza)
            descartadas.append({"ficha": fi, "motivo": "ya está en pantalla" if pid in excluidos else "repetida en la lista",
                                "regla": "una_vez", "quien": "código"})
            continue
        vistos.add(pid)
        resp_k = copy.deepcopy(raw["final"])
        filas = [f for f in resp_k.get("beats") or [] if isinstance(f, dict)]
        fila = next((f for f in filas if str(f.get("cap")) == cap and _int(f.get("beat")) == nb), None)
        if fila is None:
            fila = {"cap": cap, "beat": nb, "sello": None}
            filas.append(fila)
        fila["ficha"] = fi
        resp_k["beats"] = filas
        acum: list[dict[str, Any]] = []

        def juez_k(ms: list[dict], caps: list[dict], _acum: list = acum) -> dict:
            # `validar` re-marca el papel entero: lo de los otros beats ya está juzgado, no va al verificador
            _acum.extend(m for m in ms if m.get("que") != "descarte" and (m.get("cap"), m.get("beat")) == (cap, nb))
            return {}
        v = validar(resp_k, ent, juez=juez_k)
        caida = next((x for x in v["descartados"] if x.get("que") == "ficha" and x.get("cap") == cap and x.get("beat") == nb
                      and str(x.get("pool_id")) == pid), None)
        slot = next((s for s in v["beats"] if s["cap"] == cap and s["beat"] == nb), None)
        if caida or not slot or not slot.get("ficha"):
            descartadas.append({"ficha": fi, "motivo": f"{(caida or {}).get('regla', 'validación')}: {(caida or {}).get('motivo', 'sin ficha')}",
                                "regla": (caida or {}).get("regla"), "quien": "validación"})
            continue
        ficha = slot["ficha"]
        ficha.pop("juicio_verificador", None)         # el «sin veredicto» del juez que no llama: el real va abajo
        candidatas.append(ficha)
        marcas += acum
    usd_v, ver = 0.0, None
    if marcas:                                        # UNA llamada al verificador por clic
        ver = (juez or functools.partial(pv.verificar, post=post, log=log))(marcas, ent["caps"])
        usd_v = float(ver.get("usd") or 0.0)
    vf = {(str(x.get("pool_id")), str(x.get("cap")), _int(x.get("beat"))): x for x in (ver or {}).get("veredictos_fichas") or []}
    alternativas: list[dict[str, Any]] = []
    for ficha in candidatas:
        caida = aplicar_veredicto(ficha, cap, nb, marcas, vf)
        if caida:
            descartadas.append({"ficha": ficha, "motivo": f"verificador ({caida['regla']}): {caida['motivo']}",
                                "regla": caida["regla"], "quien": "verificador"})
        else:
            alternativas.append(ficha)
    out = {"cap": cap, "beat": nb, "alternativas": alternativas, "descartadas": descartadas, "excluidos": excluidos,
           "usd": round(usd_autor + usd_v, 5), "usd_autor": usd_autor, "usd_verificador": round(usd_v, 5),
           "segundos": round(time.time() - t0, 1), "tokens_in": hx.tokens_entrada(usos[-1]) if usos else 0, "usage": usos,
           "verificador": {k: (ver or {}).get(k) for k in ("usage", "usd", "segundos", "pedido_md5", "error")} if ver else None,
           **({"error": "sin JSON"} if resp is None else {})}
    with (d / "01e_sugerir.log.jsonl").open("a", encoding="utf-8") as fl:
        fl.write(json.dumps({"ts": time.strftime("%Y-%m-%dT%H:%M:%S"), "cap": cap, "beat": nb, "n": n, "user_md5": hashlib.md5(user.encode("utf-8")).hexdigest(),
                             "pedido": resto, "respuesta_cruda": crudos, "resultado": out}, ensure_ascii=False) + "\n")
    return out


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
    from script_engine.narracion_verificador import leer_quedan   # F66: lo que la narración sigue contradiciendo
    quedan = leer_quedan(carga["dir"])
    if quedan:
        papel["aviso_narracion"] = quedan
    from script_engine.m01d_particion import md5_narracion          # F67 C: de qué narración salió este papel
    papel["narracion_md5"] = md5_narracion(json.loads((carga["dir"] / "01b_narracion_v3.json").read_text(encoding="utf-8")))
    (carga["dir"] / f"{ARCHIVO}.json").write_text(json.dumps(papel, ensure_ascii=False, indent=1), encoding="utf-8")
    (carga["dir"] / f"{ARCHIVO}.md").write_text(a_markdown(papel), encoding="utf-8")
    if not res.get("cache"):                          # F65b: un papel nuevo no está revisado
        (carga["dir"] / f"{ARCHIVO}.revision.json").unlink(missing_ok=True)
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


def _revision_path(topic_id: str, steps_dir: Path | None = None) -> Path:
    return ruta(topic_id, steps_dir).with_name(f"{ARCHIVO}.revision.json")


def revisados(topic_id: str, steps_dir: Path | None = None) -> list[list]:
    """F65b §3 B: los [cap, beat] que Omar marcó revisados en el QA del papel ([] si ninguno)."""
    f = _revision_path(topic_id, steps_dir)
    try:
        return list(json.loads(f.read_text(encoding="utf-8")).get("revisados") or []) if f.exists() else []
    except (OSError, ValueError):
        return []


def marcar_revisado(topic_id: str, cap: str, beat: int, on: bool, steps_dir: Path | None = None) -> list[list]:
    """F65b §3 B: el ✓ del QA va en 01e_pantalla.revision.json, NO en el papel (`md5_papel` excluye solo `aprobado`: un ✓
    adentro lo dejaría «cambió después de la aprobación»). Informativo: no bloquea nada. Devuelve la lista."""
    r = [x for x in revisados(topic_id, steps_dir) if list(x) != [cap, int(beat)]]
    if on:
        r.append([cap, int(beat)])
    _revision_path(topic_id, steps_dir).write_text(json.dumps({"revisados": r}, ensure_ascii=False, indent=1), encoding="utf-8")
    return r


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
    except SinJSON as e:
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
