"""
lab/tools/mapa_modulos.py — F33 §D: arma `lab/MAPA_MODULOS.md` y `lab/MAPA_MODULOS.json`.

Los hechos (quién importa a quién, dónde, en qué commit nació cada archivo) salen del código con `mapa_hechos.py`; acá
van, escritos a mano después de leer cada módulo, el sticker (qué hace para el video, sin jerga), lo que recibe y
entrega, el estado en el camino de producción de hoy (topic con escaleta + `fase2b --gfx --rotulista`, perfil
misterio) y las funciones que ese camino ya no llama. Volver a correrlo después de tocar un módulo:

    python lab/tools/mapa_modulos.py
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import mapa_hechos as mh  # noqa: E402

CAMINO = ("topic con escaleta + `fase2b <topic> --gfx --rotulista` (perfil misterio); `--plan-only` recorre lo mismo "
          "sin el render")

# módulo: (sticker, recibe, entrega, tanda, estado)
M: dict[str, tuple[str, str, str, str, str]] = {
    "fase2b": ("El armador final: junta imagen, voz, subtítulos y música de cada capítulo en un segmento y los pega en "
               "el video. Con `--gfx` le pone encima la capa gráfica; con `--plan-only` solo escribe el guion de pantalla. "
               "Desde F34, con `--gfx` la música de cada cap arranca con su title card (pieza = segmento, después de "
               "la intro) y la mezcla de previsualización mide dónde arranca. Desde F36, si el plan de ch01 trae la "
               "tarjeta fecha-hora, el mp4 arranca con 3 s de negro con la tarjeta en lugar de la intro congelada; "
               "`--plan-edit` edita el guion en papel.",
               "assets del topic (imágenes/clips), voz por cap + tiempos, sync map, música", "`*_final(_gfx).mp4`; o "
               "GUION_PANTALLA + mezcla", "previo a F1 (inicial)", "vivo"),
    "gfx_config": ("El tablero de perillas de la capa gráfica: duraciones, tamaños, colores y qué reglas están "
                   "prendidas; el perfil del canal (identidad F3) pisa los valores; el perfil trae también el vocabulario de "
                   "sellos de clima (`sellos_clima`).", "gfx_profiles/<perfil>.json",
                   "`gfx_rules`, `gfx_render`, moods, sfx por bloque", "F1", "vivo"),
    "transition_config": ("Las perillas del pegado entre capítulos (calidad del video, fps) y el inventario de "
                          "transiciones de los perfiles de arte.", "—", "`transition_render` y el inventario", "previo a F1",
                          "vivo (con --gfx solo calidad y fps; el inventario es del camino sin gfx)"),
    "transition_applier": ("Pega los capítulos uno detrás de otro. Con --gfx: corte a negro y el siguiente sube desde "
                           "negro; sin --gfx, las transiciones del perfil de arte (incluido el flash blanco).",
                           "segmentos por cap", "`_concat_video.ts` + `_concat_audio.wav` y el mp4 sin música",
                           "previo a F1", "vivo"),
    "aprobacion": ("La compuerta del render: guarda quién aprobó el guion de pantalla y la huella de los planes; si "
                   "algo cambió después, no hay render.", "GUION_PANTALLA.json + planes resueltos",
                   "`aprobado` en el guion; sí/no para el hook", "F33", "vivo"),
    "gfx_layer": ("El director de orquesta de la capa gráfica de un capítulo: llama a todos los demás en orden "
                  "(plan, textos, sellos, crítico, transiciones) y hace el render en HyperFrames. Desde F34, con el "
                  "guion aprobado dibuja el plan aprobado tal cual (plan congelado) y no lo reescribe.",
                  "visual base del cap + palabras con tiempos + contexto", "`chNN_gfx.mp4`, plan resuelto, sfx, "
                  "escenas", "F1", "vivo"),
    "gfx_director": ("El primer borrador de la pantalla: Gemini Flash propone bloques mirando la narración; acá también "
                     "se carga el contexto del cap y se arman los sfx de cada bloque.", "narración, hechos, escenas",
                     "plan crudo y resuelto, contexto, eventos de sfx", "F1",
                     "vivo (sus textos los reemplaza el rotulista; sus sellos, el catálogo)"),
    "gfx_realizador": ("Hace que la pantalla obedezca a la escaleta: ventanas de tiempo de cada beat, qué datos puede "
                       "mostrar cada uno, la pregunta de cierre del último beat y los topes (desde F36 no borra el "
                       "contador del rotulista).",
                       "escaleta + narración por beat + pool", "`gfx_beats_chNN.json`, candidatos, filas de lo quitado",
                       "F29", "vivo"),
    "gfx_rotulista": ("La fachada del rotulista: desde F36 C ya no llama a ningún modelo; `preparar_cap` lee el guion "
                      "en papel de Fase 1 (`01e_pantalla.json`), alinea sus oraciones con las de la voz por texto y ancla "
                      "cada ficha a su palabra; el resto lo re-exporta de sus módulos para que nadie cambie de import.",
                      "papel del topic + oraciones de la voz + beats", "entrada del cap + bloques, sellos, relojes y "
                      "tarjeta del papel", "F29b", "vivo"),
    "rotulista_llm": ("El pedido al modelo que escribía los textos de pantalla en Fase 2 (Claude Sonnet, uno por cap). "
                      "Desde F36 C el texto lo escribe m01e_pantalla en Fase 1 y nadie del camino lo llama (D lo borra).",
                      "oraciones de la voz, beats, pool, escaleta", "respuesta cruda y validada por cap, ledger de costos",
                      "F36 (código de F29b)", "muerto (F36 C: el texto viene del papel)"),
    "rotulista_filtros": ("Los filtros que deciden si un texto del papel sale, en un orden que se lee en una línea "
                          "(`ORDEN`, F36 C): anclar el papel a la voz, no dicho del gancho, candado de lo literal, no "
                          "dicho, spoiler y lectura hasta el corte. El orden viejo del modelo (`ORDEN_MODELO`) queda solo "
                          "para rotulista_llm.", "bloques del papel + entrada del cap", "bloques que pasan, cortados con "
                          "su regla y motivo", "F36 (código de F29b)", "vivo"),
    "rotulista_colocar": ("Pone cada texto que pasó en su lugar: cuánto dura (lectura, nunca después del corte), qué "
                          "forma toma (ficha normal, nombre o cita con autor; papel = recorte) y «nunca al mismo tiempo» "
                          "(DECISIONES 17:58: dos bloques no se solapan ni se tocan; si chocan, esperan al momento "
                          "siguiente de su beat).", "bloques validados + escenas", "bloques en el plan, filas de lo movido "
                          "o cortado", "F36 (código de F29b)", "vivo"),
    "clima": ("Los sellos de clima: desde F36 C la palabra y la oración vienen del guion en papel; acá se pone el "
              "instante (la palabra de más peso de la oración o su inicio), se mira que no cruce el corte, el crítico "
              "(«¿estorba?») antes del reparto y que nunca esté al mismo tiempo que otro bloque.",
              "sellos del papel + oraciones + léxico de moods", "sellos en el plan, filas de lo cortado",
              "F36 (código de F32/F34)", "vivo"),
    "voz_datos": ("Lo que sale de la voz y la escaleta sin modelo: el pico del cap, el reloj cuando la voz dice una "
                  "fecha completa y la tarjeta fecha-hora derivada (desde F36 C solo para comparar con la del papel).",
                  "oraciones de la voz, escaleta, pool", "pico, reloj, tarjeta derivada", "F36 (código de F34)", "vivo"),
    "voz_utils": ("La utilería de la voz: lee cifras en dígitos y en letras, nombres propios, cifras con su unidad, y "
                  "parte la voz en oraciones con cada palabra numerada; desde F36 C parte igual el texto de Fase 1 "
                  "(`oraciones_de_texto`) y normaliza oraciones para alinear papel y voz.", "texto / palabras con tiempos",
                  "cifras, nombres, oraciones", "F36 (código de F29b)", "vivo"),
    "gfx_critic": ("El editor: Gemini mira la foto y saca lo que repite la voz, no aporta o tapa algo. Desde F36 juzga "
                   "los candidatos ANTES del reparto (lo que saca no ocupa lugar); a las fichas del papel y a los sellos "
                   "solo les pregunta si estorban.", "plan + cuadros del video + voz", "plan sin lo que no pasa + "
                   "veredictos", "F4e", "vivo"),
    "gfx_project": ("El dibujante: convierte el plan en la página HTML que HyperFrames renderiza (title card, ficha, "
                    "recorte, cita, sello, reloj, agua, contador, zoom).", "plan resuelto + escenas", "proyecto "
                    "HyperFrames (index.html, CSS)", "F1", "vivo"),
    "gfx_sparse": ("El ahorrador: HyperFrames solo donde hay algo que dibujar; el resto del cap lo cose ffmpeg, con "
                   "las transiciones, el grano y la viñeta.", "plan + escenas + base", "`chNN_gfx.mp4` cosido", "F2",
                   "vivo"),
    "gfx_safe_bake": ("Cuece con ffmpeg el movimiento suave de cada foto (acercar, alejar, paneo) para no pagarlo en "
                      "HyperFrames.", "escenas con movimiento seguro + sus PNG", "`base_cocido.mp4`", "F30", "vivo"),
    "gfx_style": ("La identidad del canal aplicada al plan: qué movimiento lleva cada foto y qué transición va en cada "
                  "corte según el relato (corte, golpe de zoom en el pico, fundido, dip al cierre).",
                  "escenas + plan + beats", "movimientos y transiciones", "F4", "vivo"),
    "gfx_peak": ("El pico del capítulo: busca su frase y la palabra de más peso para el sello del pico; trae las "
                 "piezas de oraciones y palabras que usan los demás (desde F36 la palabra del momento vive en `clima`).", "palabras con tiempos + léxico de moods",
                 "frase y palabra del pico, sello", "F3", "vivo (el pico de la escaleta; `plan_peak` ya no corre)"),
    "gfx_pool": ("La pantalla alimentada por el pool de evidencia: fuentes literales para el candado, lo ya mostrado "
                 "en caps anteriores y el reloj de fechas.", "pool de evidencia + palabras", "fuentes, ids ya usados, "
                 "reloj", "F5", "vivo (recortes, citas y contadores del pool ya no corren)"),
    "gfx_intensity": ("Gemini marca cuánto pesa cada frase y qué palabras cargan miedo, muerte o agua; ese léxico "
                      "alimenta los sellos.", "oraciones del cap + vecinas", "pico, cargas, léxico del cap", "F4b",
                      "vivo"),
    "gfx_vision": ("Gemini mira cada foto y dice qué detalles tiene y dónde (rostro, manos, objetos); con eso se "
                   "decide el movimiento seguro y la caja de la lupa.", "PNG / cuadro de la escena", "detalles con "
                   "caja, sí/no del recorte", "F4b", "vivo"),
    "gfx_literal_lock": ("El candado: un texto que no está literal en las fuentes (narración, pool) no sale.",
                         "plan + fuentes", "plan sin lo no literal + rechazados", "F1", "vivo"),
    "gfx_question": ("Escribe una pregunta de cierre con Gemini cuando la escaleta no trae una.", "narración del cap y "
                     "del siguiente", "pregunta validada", "F3", "solo respaldo (con escaleta la pregunta es el cierre "
                     "del último beat)"),
    "gfx_review": ("La hoja de cues: un renglón por bloque visible con su segundo, para revisar el render.",
                   "eventos del plan", "`gfx_cues_chNN.md/.json`, página de revisión", "F1", "vivo"),
    "gfx_bug": ("La marca del canal (la llama en el farol): la esquina está apagada desde F4e; queda el cierre del "
                "último cap si no hay pregunta.", "SVG de la marca + plan", "PNG de la marca para el cosido", "F4b",
                "vivo (solo el cierre)"),
    "gfx_fragments": ("Elegía con Gemini el fragmento más impactante de un dato para recortes y rótulos; hoy solo "
                      "presta el ícono de categoría del sello.", "datos + léxico", "fragmentos; ícono de categoría",
                      "F4b", "solo sin escaleta (vive por `category_icon`)"),
    "gfx_identity": ("Guarda la identidad del canal que Omar arma en el laboratorio (F3) dentro del perfil.",
                     "estado del lab", "`identity` en gfx_profiles/<perfil>.json", "F3",
                     "muerto en el pipeline (lo usa solo el lab, gfx_lab_server)"),
    "gfx_guion": ("Escribe el guion de pantalla: todo lo que se va a ver, en texto, con lo cortado y por quién, y los "
                  "chequeos (lectura, nunca al mismo tiempo, costuras, inicio de voz, inicio de música, gancho no vacío, "
                  "tarjeta fecha-hora; desde F36 C la columna `papel` y «papel sin colocar / sin alinear»).",
                  "planes, escenas, beats, mezcla", "GUION_PANTALLA.md/.json", "F32", "vivo"),
    "music_intensity": ("Decide cuándo la música calla, acompaña o sube en cada cap según la escaleta; también da el "
                        "beat pico de cada cap.", "escaleta + narración por beat + tiempos de la voz",
                        "tramos de volumen por cap, beat pico", "F28", "vivo"),
    "m01a_escaleta": ("Fase 1: arma la escaleta (los beats del video con función, intensidad, datos y cierre) desde la "
                      "ficha del caso; es lo que el gfx lee para saber qué va dónde.", "ficha del caso + pool",
                      "`01a_escaleta.json`", "F6", "vivo (fase 1; el gfx lee su salida)"),
    "m01d_particion": ("Fase 1: parte el guion en los 7 capítulos con su texto para la voz; de ahí salen la "
                       "narración por cap y por beat que leen el realizador y el guion en papel.", "guion + escaleta",
                       "narración por cap y por beat", "F10", "vivo (fase 1)"),
    "m01e_pantalla": ("Fase 1 (F36 C): el guion de pantalla EN PAPEL. Una llamada a Sonnet por video con la narración "
                      "de los 7 caps (oraciones numeradas y cuánto cabe), la escaleta, el archivo del caso y el "
                      "vocabulario de clima → por beat ficha o nada, sello o nada; relojes; tarjeta. Lo valida en papel "
                      "(candado, no dicho, spoiler, una vez, cabe, formato) y lo deja para que Omar lo revise antes de la "
                      "voz; Fase 2 lo consume.", "escaleta, narración por cap y beat, títulos, pool, `sellos_clima`",
                      "`01e_pantalla.json/.md` en el topic de Fase 1", "F36", "vivo (fase 1)"),
    "archive_clipping.html.tmpl": ("La forma del recorte de diario (papel, kicker, titular).", "un recorte del plan",
                                   "HTML", "F1", "vivo (documentos del rotulista)"),
    "chapter_question.html.tmpl": ("La forma de la pregunta de cierre sobre la foto oscurecida.", "la pregunta",
                                   "HTML", "F2", "vivo"),
    "count_up.html.tmpl": ("La forma del contador que sube hasta la cifra.", "cifra + unidad + etiqueta", "HTML", "F1",
                           "vivo (F32 B.7; en Vajont no salió ninguno)"),
    "data_callout.html.tmpl": ("La forma vieja del dato en letras grandes sueltas.", "un rótulo del plan", "HTML", "F1",
                               "muerto en el camino con rotulista (todo texto es ficha); vive sin rotulista"),
    "evidence_zoom.html.tmpl": ("La forma de la lupa: recuadro, «DETALLE» y acercamiento.", "caja del detalle", "HTML",
                                "F1", "vivo (lupa del rotulista)"),
    "grade_css.html.tmpl": ("Un grade de color por CSS de la primera versión.", "—", "—", "F1",
                            "muerto (nadie la carga; el grade lo hace el CSS común y ffmpeg)"),
    "index.html.tmpl": ("La página base de cada proyecto HyperFrames (escenas, overlays, timeline).", "escenas + "
                        "overlays", "index.html", "F1", "vivo"),
    "scene.html.tmpl": ("La forma de una escena (la foto o el clip con su movimiento).", "una escena", "HTML", "F1",
                        "vivo"),
    "title_card.html.tmpl": ("La forma del title card del capítulo; desde F29c también la de la ficha.", "kicker + "
                             "título", "HTML", "F1", "vivo"),
}

# funciones (o archivos) que el camino de producción ya no llama: (qué, por qué, commit desde el que no corre)
MUERTOS = [
    ("gfx_peak.plan_peak (y water_level, zoom_latido, time_ticker, reserved_water_level, clear_around)",
     "con el rotulista el pico es el de la escaleta (`voz_datos.pico_plan`)", "5ae6177"),
    ("gfx_realizador.garantizar_pico", "`--rotulista` apaga `garantizar_pico`", "7e704de"),
    ("gfx_pool.plan_pool_documents, plan_pool_quote, pool_count_up, enforce_reserved",
     "con el rotulista los textos los escribe él (`rot_on` en apply_gfx)", "5ae6177"),
    ("gfx_fragments.choose_fragments", "con pool los recortes salían de gfx_pool (F5) y después del rotulista",
     "e18e656"),
    ("gfx_fragments.drop_repeated_callouts", "con el rotulista corre su regla de no dicho", "5ae6177"),
    ("gfx_vision.pick_zoom", "con el rotulista la lupa la propone él", "5ae6177"),
    ("gfx_director.fill_gaps", "`gap_fill` apagado", "2fcd603"),
    ("gfx_question.question_for", "con escaleta la pregunta es el `cierre` del último beat (queda de respaldo)",
     "2fcd603"),
    ("gfx_style.identity_transitions", "**se llama y se descarta**: con escaleta la pisa `transiciones_por_relato`",
     "7d0d0e5"),
    ("gfx_style.select_punches", "**se llama y se descarta**: el realizador saca todos los `punch_in` (los reemplaza el "
     "zoom_punch del pico)", "2fde994"),
    ("gfx_director.place_emphasis (sellos por léxico)", "**se llama y se descarta**: `sellos_por_tema` los reemplaza",
     "2fde994"),
    ("data_callout.html.tmpl", "con el rotulista todo texto sale como ficha", "cc3f079"),
    ("grade_css.html.tmpl", "nadie la carga", "a878836"),
    ("gfx_identity (todo el módulo)", "solo lo usa el lab de identidad (gfx_lab_server)", "—"),
    ("rotulista_llm (todo el módulo) y rotulista_filtros.ORDEN_MODELO (anclaje, forma, coherencia, cantidad)",
     "F36 C: el texto lo escribe el guion en papel (m01e_pantalla); Fase 2 no llama a ningún modelo de texto", "C"),
    ("clima.sellos_por_tema, elegir_clima, _gemini_clima, palabra_clima, prompt_clima (Gemini de clima)",
     "F36 C: los sellos vienen del papel (`sellos_del_papel`)", "C"),
    ("voz_datos.agua_de_voz y rotulista_colocar.animacion_de_cifra (agua y contador)",
     "F36 C / catálogo 18:17: no hay agua ni contador", "C"),
    ("rotulista_colocar.aplicar_ediciones, ediciones_de, guardar_ediciones, mover_a_escena (plan_edits.json)",
     "F36 C: `--plan-edit` edita el papel (m01e_pantalla.editar)", "C"),
]


def fecha(h: str) -> str:
    if h == "—":
        return "nunca en fase2b"
    if h == "C":
        return "F36 C (commit de esta parte)"
    r = subprocess.run(["git", "log", "-1", "--format=%ad %s", "--date=short", h], cwd=ROOT, capture_output=True,
                       text=True, encoding="utf-8", errors="replace")
    return f"{h} {r.stdout.strip()[:80]}"


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    hechos = json.loads(subprocess.run([sys.executable, str(Path(__file__).with_name("mapa_hechos.py"))], cwd=ROOT,
                                       capture_output=True, text=True, encoding="utf-8").stdout)
    faltan = sorted(set(hechos) - set(M))
    sobran = sorted(set(M) - set(hechos))
    assert not faltan and not sobran, f"módulos sin sticker {faltan} · stickers sin módulo {sobran}"
    filas, aristas = [], []
    for k, h in hechos.items():
        st, rec, ent, tanda, estado = M[k]
        quien = sorted(h["lo_importan"])
        filas.append({"modulo": k, "archivo": h["archivo"], "sticker": st, "recibe": rec, "entrega": ent,
                      "lo_llama": quien, "tests": len(h["tests"]), "lab": len(h["lab"]), "tanda": tanda,
                      "nacio": h["nacio"], "estado": estado, "doc": h["doc"]})
        for q, donde in h["lo_importan"].items():
            aristas.append({"de": Path(q).stem if not q.endswith(".tmpl") else q, "a": k, "donde": donde})
    muertos = [{"que": q, "por_que": p, "desde": fecha(c)} for q, p, c in MUERTOS]
    data = {"generado_por": "lab/tools/mapa_modulos.py (F33 §D)", "camino": CAMINO, "modulos": filas,
            "aristas": aristas, "muertos": muertos}
    (ROOT / "lab" / "MAPA_MODULOS.json").write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")
    L = ["# MAPA DE MÓDULOS — capa gráfica y lo que la alimenta", "",
         f"Generado por `lab/tools/mapa_modulos.py` (F33 §D) leyendo el código: quién llama a quién y cuándo nació cada "
         f"archivo salen del AST y de git; sticker, recibe/entrega y estado los escribió CC después de leer cada módulo. "
         f"Estado = en el camino de producción de hoy: {CAMINO}. Los datos con las aristas, para el flujograma, en "
         f"`lab/MAPA_MODULOS.json`.", "",
         "| módulo | sticker | recibe | entrega | quién lo llama | tanda en que nació | estado |",
         "|---|---|---|---|---|---|---|"]
    for f in filas:
        quien = ", ".join(Path(q).name for q in f["lo_llama"]) or "—"
        extra = f" (+ {f['tests']} tests)" if f["tests"] else ""
        L.append(f"| `{f['modulo']}` | {f['sticker']} | {f['recibe']} | {f['entrega']} | {quien}{extra} | "
                 f"{f['tanda']} (`{f['nacio'][:7]}`) | {f['estado']} |")
    L += ["", "## Lo que el camino de producción ya no llama (muertos)", "",
          "| qué | por qué | desde |", "|---|---|---|"]
    L += [f"| `{m['que']}` | {m['por_que']} | {m['desde']} |" for m in muertos]
    L += ["", "Muerto = en el camino con escaleta y rotulista no aporta nada al video: o nadie lo llama, o **se llama y su "
          "resultado se descarta** (`select_punches`, `identity_transitions`, `place_emphasis`: lo dice la columna «por "
          "qué»). El código sigue ahí (los topics sin escaleta o sin rotulista lo usan, o el lab). No se borra nada sin "
          "decisión de Omar."]
    (ROOT / "lab" / "MAPA_MODULOS.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{len(filas)} módulos · {len(aristas)} aristas · {len(muertos)} muertos")


if __name__ == "__main__":
    main()
