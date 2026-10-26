"""
script_engine/gfx_rotulista.py — F29b §A: el rotulista. El texto de pantalla lo escribe alguien, anclado a la oración.
F29c: por beat, anclado a la palabra, y la ficha es el title card.

Regla (Omar): un bloque vale si (a) dice algo que la voz no dice, (b) sobre lo que la voz cuenta en ese momento y (c) sin
adelantar. Con `gfx_rules.rotulista` y escaleta (realizador), por cap:
    entrada    oraciones de la voz con tiempos y cada palabra numerada (gfx_peak.sentences), el beat de cada oración,
               beats del cap (gfx_beats_chNN.json), ítems = los `a_pantalla` del cap + `dato_central`/`datos_apoyo` de
               sus beats (texto fuente completo, fuente, `por_que`), lo ya mostrado (los `a_pantalla` de caps
               anteriores: dejan correr los 7 caps en paralelo), el pico ÚNICO del cap (pico_cap) y la voz de todo el
               video (para la coherencia de cifras).
    llamada    UNA por cap con claude_helpers (Sonnet 5.5 por defecto, effort medium, JSON sin esquema), prompt literal
               (ROTULISTA_SYSTEM / ROTULISTA_USER, HANDOFF_F29c §A.5), cruda en `_fase2b_work/rotulista_chNN.raw.json`
               (caché por pedido). De la respuesta se toma el primer objeto JSON válido (§A.6.1). Un reintento si no
               parsea o si una regla de contenido saca algo; otro si faltan `a_pantalla`. Tope de US$ antes de cada
               llamada (con las llamadas en vuelo). Sin respuesta válida, el cap sale sin bloques (nunca se inventa).
    validar    (determinista) anclaje (oración y palabra que existen, en un beat del ítem; el `a_pantalla` del beat pico
               pasa al beat siguiente si su ítem es de ese beat), forma (tipo, etiqueta, valor, muñón, que quepa en la
               ficha), candado (cita = subcadena del texto fuente; resto = cada número, nombre propio y año en el texto
               fuente), tiempos (§A.2: t0 = la palabra `word_idx`; t1 = fin de la oración, o de la siguiente si no
               alcanza el mínimo de lectura caracteres ÷ 15; nunca después del corte de escena; si no alcanza, no va),
               no dicho (oración ancla ± 1) y spoiler (oraciones posteriores del cap) (§A.3), coherencia de cifras con
               la voz de todo el video (§A.4).
    finalizar  (§A.1) por beat queda 1 (`a_pantalla` primero, después `rank`); el beat pico, 0.
    colocar    cifra, hecho, persona → ficha (el title card sin #tc-dim: kicker = etiqueta, título = dato); documento →
               archive_clipping; cita → quote_card; lupa → evidence_zoom con la caja de visión del detalle.
    escena     (§0/§A.5, después del reloj y el sello) una cosa por escena: la ficha espera a la escena siguiente del
               beat si en la suya hay title card, reloj, sello u otro bloque; el reloj (animación) no va encima de un
               texto ni en el beat de otra animación.
Lecturas declaradas (F29b_REPORT y F29c_REPORT). Sin escaleta o con el flag apagado no corre nada de esto.

F36 §A: el rotulista está partido en cinco módulos (el código se movió, no se reescribió); este archivo queda como
fachada para que gfx_layer, fase2b, gfx_guion, los tests y el lab no cambien de import:
    rotulista_llm      prompt, entrada, pedido y llamada (caché, ledger, tope, reintento)
    rotulista_filtros  validar (los filtros de ORDEN, en orden), finalizar, contradicciones
    rotulista_colocar  tiempos, colocar, ediciones a mano, escena
    clima              sellos de clima (y peak_word, traído de gfx_peak)
    voz_datos          pico del cap, reloj y agua desde la voz, tarjeta fecha-hora
    voz_utils          números, nombres y oraciones de la voz (los usan los cinco)
Aquí quedan solo preparar_cap y prefetch.
"""
from __future__ import annotations

import time
from pathlib import Path
from typing import Any

# F36 §A: re-exports (todos los nombres que el módulo tenía antes de partirse; nadie cambia de import)
from script_engine.voz_utils import (_analiza, _ARTPREP, beat_de_oracion, _DIFERENCIA, _DIG, _fmt, _MAGNITUD, munon,
                                     nombre_inicial, nombres, _num_en, _num_tok, numero_en, numeros, _NUMW, oraciones,
                                     _palabra_en, palabras, palabras_de_contenido, _PARTICULAS, _raiz_en, _toks,
                                     _UNIDAD_1, _UNIDAD_2, _valor, _w2n, _W2N, _W2N_LOCK)
from script_engine.rotulista_filtros import (A_PANTALLA_POR_BEAT, LOCALES, anclaje, candado, cantidad, coherencia, CON_ETIQUETA,
                                             contradicciones, _DOC, FICHA, finalizar, forma, gancho_dicho, lectura,
                                             lo_que_pide, no_dicho, ORDEN, pide_documento, regla, spoiler, TIPOS,
                                             validar)
from script_engine.rotulista_colocar import (caben, hasta_el_corte, animacion_de_cifra, aplicar_ediciones, CAMPOS_EDITABLES, caracteres,
                                             colocar, _cubre, despues_del_corte, EDICIONES, ediciones_de, _escena_de,
                                             escena_final, guardar_ediciones, KIND_FICHA, LECTURA_CPS, lupa_de_detalles,
                                             mover_a_escena, tiempos, UNIDAD_CONTADOR, unidades)
from script_engine.rotulista_llm import (pasados_de_largo, A1_SYSTEM, A1_USER, _deshacer, EFFORT_DEFAULT, _EN_VUELO, entrada, gastado,
                                         _HUECOS, items_cap, items_gancho, _ledger, LINEA_B7, llamar, _LOCK,
                                         MODELO_DEFAULT,
                                         OUT_TOKENS_PEOR, _post_con_registro, primer_json, prompt_md5, prompt_user,
                                         PROMPT_VERSION, PROMPT_VERSION_F29B, REGLAS_REINTENTO, _reintento,
                                         ROTULISTA_SYSTEM, ROTULISTA_SYSTEM_F29C, ROTULISTA_SYSTEM_F32, ROTULISTA_USER,
                                         ROTULISTA_USER_F32, _solo_el_json, _tipo_id, TopeRotulista, voz_del_video,
                                         voz_previa, ya_mostrado)
from script_engine.clima import (usadas_antes, elegir_clima, _gemini_clima, palabra_clima, peak_word, prompt_clima,
                                 SELLO_CLIMA_PROMPT, _sello_queda, sellos_por_tema, TEMA_DE_MOOD, vocabulario_clima)
from script_engine.voz_datos import (_agua_de, agua_de_voz, AGUA_ETIQUETAS, _entero, fechas_completas, _MES_RE,
                                     pico_cap, pico_plan, _raices, reloj_de_voz, tarjeta_inicial)


# ═══════════════════════ prefetch (los 7 caps en paralelo) ═══════════════════════

def preparar_cap(chplan: Any, video_id: str, work_dir: Path, time_offset: float = 0.0
                 ) -> tuple[dict, list[dict], dict] | None:
    """(entrada, palabras, ctx) de un cap, sin escenas ni visión (lo mismo que arma apply_gfx)."""
    from config import DATA_DIR
    from script_engine import gfx_realizador as gr
    from script_engine.gfx_director import load_chapter_context
    from script_engine.gfx_layer import remapped_words
    _, words = remapped_words(chplan)
    ctx = load_chapter_context(video_id, chplan)
    carga = gr.cargar(ctx.get("topic_id") or ctx["video_id"], DATA_DIR / "scripts" / "_steps")
    if carga is None or not ctx.get("pool"):
        return None
    real = gr.preparar(ctx["chapter_number"], carga, ctx.get("pool"), words, time_offset, work_dir, chplan.chapter_id)
    return entrada(ctx["chapter_number"], real, carga["escaleta"], ctx.get("pool"), words, time_offset,
                   voz_video=voz_del_video(ctx), voz_antes=voz_previa(ctx)), words, ctx


def prefetch(plans: list[Any], video_id: str, work_dir: Path, offsets: dict[str, float] | None = None, *,
             modelo: str | None = None, effort: str | None = None, tope: float = 2.0,
             max_workers: int = 7) -> dict[str, Any]:
    """Rotulista de todos los caps en paralelo (threads) → `rotulista_chNN.raw.json`. apply_gfx lo encuentra en caché.
    Nunca lanza: un cap que falla lo vuelve a intentar apply_gfx."""
    from concurrent.futures import ThreadPoolExecutor

    def one(chplan: Any) -> tuple[str, Any]:
        cap = chplan.chapter_id
        t0 = time.time()
        try:
            got = preparar_cap(chplan, video_id, work_dir, (offsets or {}).get(cap, 0.0))
            if got is None:
                return cap, "sin escaleta/pool"
            ent, words, _ = got
            r = llamar(ent, words, (offsets or {}).get(cap, 0.0), work_dir, cap, modelo=modelo, effort=effort, tope=tope)
            v = r.get("validacion") or {}
            return cap, {"segundos": round(time.time() - t0, 1), "cache": bool(r.get("cache")),
                         "bloques": len(v.get("bloques") or []), "intentos": len(r.get("intentos") or [])}
        except Exception as e:  # noqa: BLE001
            return cap, f"falló ({type(e).__name__}: {str(e)[:120]})"
    Path(work_dir).mkdir(parents=True, exist_ok=True)
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        return dict(ex.map(one, plans))
