"""
lab/tools/mapa_modulos.py — F33 §D: arma `lab/MAPA_MODULOS.md` y `lab/MAPA_MODULOS.json`.

Los hechos (quién importa a quién, dónde, en qué commit nació cada archivo) salen del código con `mapa_hechos.py`; acá
van, escritos a mano después de leer cada módulo, el sticker (qué hace para el video, sin jerga), lo que recibe y
entrega, el estado en el camino de producción de hoy (topic con escaleta + `fase2b --gfx`, perfil
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

CAMINO = ("topic con escaleta + `fase2b <topic> --gfx` (perfil misterio); `--plan-only` recorre lo mismo "
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
                   "`gfx_rules`, `gfx_render`, moods, sfx del title card, claves huérfanas del perfil", "F1", "vivo"),
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
                  "(plan base con el title card de la partición —F37: sin borrador del director—, textos del papel, "
                  "reparto con crítico, sellos, transiciones) y hace el render en HyperFrames. Desde F34, "
                  "con el guion aprobado dibuja el plan aprobado tal cual (plan congelado) y no lo reescribe.",
                  "visual base del cap + palabras con tiempos + contexto", "`chNN_gfx.mp4`, plan resuelto, sfx, "
                  "escenas", "F1", "vivo"),
    "gfx_director": ("El contexto de un capítulo (sin modelo): script, skeleton, fuentes del candado literal, narración del "
                     "video, pool; y la palabra clave de la pregunta de cierre. F37: el borrador de Gemini (su prompt, su "
                     "esquema y su caché) se borró: el papel es el único camino y el title card sale de la partición.",
                     "script + skeleton + canonical + pool", "contexto del cap, palabra clave", "F1", "vivo"),
    "gfx_realizador": ("Hace que la pantalla obedezca a la escaleta: ventanas de tiempo de cada beat, qué datos puede "
                       "mostrar cada uno y la pregunta de cierre del último beat. F37: el cierre del plan solo deja los "
                       "sellos del papel y ningún punch_in (sin las ramas del camino sin papel, del contador ni de los "
                       "íconos).", "escaleta + narración por beat + pool", "`gfx_beats_chNN.json`, filas de lo quitado",
                       "F29", "vivo"),
    "pantalla_entrada": ("La entrada de Fase 2 para el texto de pantalla (F37: antes gfx_rotulista; no escribe nada): "
                         "`preparar_cap` lee el guion en papel de Fase 1 (`01e_pantalla.json`), alinea sus oraciones con "
                         "las de la voz por texto y ancla cada ficha a su palabra (con el juicio del autor, si lo hay).",
                         "papel del topic + oraciones de la voz + beats", "entrada del cap + bloques, sellos, relojes y "
                         "tarjeta del papel", "F29b", "vivo"),
    "pantalla_filtros": ("Los filtros que deciden si un texto del papel sale, en un orden que se lee en una línea "
                         "(`ORDEN`): anclar el papel a la voz, no dicho del gancho, candado de lo literal, no dicho, "
                         "spoiler (lo que el autor juzgó «otro hecho» no corta) y lectura: desde F37 la lectura prueba la "
                         "escalera de intentos (otro instante de la oración, la escena siguiente, la oración siguiente) y "
                         "corta solo si no entra en ninguno. F37: antes rotulista_filtros.", "bloques del papel + entrada "
                         "del cap", "bloques que pasan con sus intentos, cortados con su regla y motivo",
                         "F36 (código de F29b)", "vivo"),
    "pantalla_colocar": ("Pone cada texto del papel en su lugar (F37: antes rotulista_colocar): la ficha dura su "
                         "lectura entre callout_dur_min y callout_dur_max sin pasar el corte, qué forma toma (ficha normal, "
                         "nombre o cita con autor; papel = recorte) y el reparto: nunca al mismo tiempo (DECISIONES 17:58) y "
                         "el crítico en cada intento, moviendo en vez de cortar (otro instante, otra escena, la oración "
                         "siguiente, el otro lado); lo que no entra queda «sin colocar» con sus intentos.",
                         "bloques validados + escenas", "bloques en el plan, filas de lo movido o sin colocar",
                         "F36 (código de F29b)", "vivo"),
    "clima": ("Los sellos de clima: la palabra y la oración vienen del guion en papel; acá se prueba la misma "
              "escalera de intentos que las fichas (F37: palabra de más peso, inicio, escena siguiente, oración "
              "siguiente y el otro lado), sin cruzar el corte, nunca al mismo tiempo que otro bloque y con el crítico "
              "(«¿estorba?») en cada intento.", "sellos del papel + oraciones + léxico de moods",
              "sellos en el plan, filas de lo movido o sin colocar", "F36 (código de F32/F34)", "vivo"),
    "voz_datos": ("Lo que sale de la voz y la escaleta sin modelo: el pico del cap, el reloj cuando la voz dice una "
                  "fecha completa (y su esquina libre), y la tarjeta fecha-hora del papel: desde F38 sale de la voz "
                  "(la primera fecha completa del gancho y la hora que dice la voz en el beat pico, con la del ítem del "
                  "pool que coincide; nunca se inventa) y la derivada de la escaleta queda solo para comparar.",
                  "oraciones de la voz, escaleta, pool", "pico, reloj, tarjeta de la voz", "F36 (código de F34)",
                  "vivo"),
    "voz_utils": ("La utilería de la voz: lee cifras en dígitos y en letras, nombres propios, cifras con su unidad, y "
                  "parte la voz en oraciones con cada palabra numerada; desde F36 C parte igual el texto de Fase 1 "
                  "(`oraciones_de_texto`) y normaliza oraciones para alinear papel y voz; desde F37 dice qué años nombra "
                  "la voz (el momento del relato) y cuántos segundos por palabra habla el narrador (mediana de sus voces "
                  "ya generadas); desde F38 lee fracciones en letras («un centímetro y medio», «medio», «y cuarto», "
                  "«un tercio») y compara cifras a la precisión del archivo.", "texto / palabras con tiempos / voces del narrador",
                  "cifras, años, nombres, oraciones, segundos por palabra", "F36 (código de F29b)", "vivo"),
    "gfx_critic": ("El editor: Gemini mira la foto en el instante de un bloque del papel y dice si estorba (tapa un "
                   "rostro o lo que la imagen muestra). F37: corre en cada intento del reparto (instante y lado), y lo "
                   "que estorba se mueve al intento siguiente en vez de cortarse.", "bloque en un intento + cuadro del "
                   "video + voz", "veredicto por intento (caché por identidad)", "F4e", "vivo"),
    "gfx_project": ("El dibujante: convierte el plan en la página HTML que HyperFrames renderiza (title card, ficha, "
                    "recorte, cita, sello, reloj, pregunta). F36 D: sin lupa, contador, agua, dato suelto, íconos ni "
                    "fuente.", "plan resuelto + escenas", "proyecto HyperFrames (index.html, CSS)", "F1", "vivo"),
    "gfx_sparse": ("El ahorrador: HyperFrames solo donde hay algo que dibujar; el resto del cap lo cose ffmpeg, con "
                   "las transiciones, el grano y la viñeta (F36 D: sin la marca del canal).", "plan + escenas + base",
                   "`chNN_gfx.mp4` cosido", "F2", "vivo"),
    "gfx_safe_bake": ("Cuece con ffmpeg el movimiento suave de cada foto (acercar, alejar, paneo) para no pagarlo en "
                      "HyperFrames.", "escenas con movimiento seguro + sus PNG", "`base_cocido.mp4`", "F30", "vivo"),
    "gfx_style": ("La identidad del canal aplicada al plan: qué movimiento lleva cada foto y qué transición va en cada "
                  "corte según el relato (golpe de zoom en el pico, fundido, dip al cierre, corte).",
                  "escenas + plan + beats", "movimientos y transiciones", "F4", "vivo"),
    "gfx_peak": ("La utilería de la voz que usan clima y voz_utils: las frases de la narración con sus palabras y "
                 "tiempos y las palabras del léxico de moods (F36 D: el pico viejo, el agua, el zoom con latido y el reloj "
                 "de gfx_peak se borraron).", "palabras con tiempos + léxico de moods", "frases, palabras de mood",
                 "F3", "vivo"),
    "gfx_pool": ("La pantalla alimentada por el pool de evidencia: fuentes literales para el candado, lo ya mostrado "
                 "en caps anteriores, el reloj de fechas y los cortes de cláusula que usa Fase 1 (m01a_skeleton). F36 D: "
                 "se borraron recortes, citas, contadores y reservados del pool.", "pool de evidencia + palabras",
                 "fuentes, ids ya usados, reloj", "F5", "vivo"),
    "gfx_intensity": ("Gemini marca cuánto pesa cada frase y qué palabras cargan miedo, muerte o agua; ese léxico "
                      "alimenta los sellos.", "oraciones del cap + vecinas", "pico, cargas, léxico del cap", "F4b",
                      "vivo"),
    "gfx_vision": ("Gemini mira cada foto y dice qué detalles tiene y dónde (rostro, manos, objetos); con eso se "
                   "decide el movimiento seguro (F36 D: la lupa y su verificación se borraron).", "PNG / cuadro de la "
                   "escena", "detalles con caja, caja humana", "F4b", "vivo"),
    "gfx_literal_lock": ("El candado: un texto que no está literal en las fuentes (narración, partición, pool) no sale: "
                         "title card, reloj y lo que no viene del papel (el papel trae su propio candado). F37: sin las "
                         "ramas de los bloques borrados.", "plan + fuentes", "plan sin lo no literal + rechazados", "F1",
                         "vivo"),
    "gfx_review": ("La hoja de cues: un renglón por bloque visible con su segundo, para revisar el render.",
                   "eventos del plan", "`gfx_cues_chNN.md/.json`, página de revisión", "F1", "vivo"),
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
                      "vocabulario de clima → por beat ficha o nada, sello o nada; relojes (F38: la tarjeta sale de la "
                      "voz, voz_datos). Lo valida en papel "
                      "(candado, no dicho, spoiler, una vez, cabe, formato; F37: fecha del relato, cita sin fecha, "
                      "descartes «la voz lo dice» verificados, picos sin ficha; una coincidencia de número se le pregunta "
                      "al autor); F38: un juez (Gemini, el modelo chico de config) mira si cada ficha habla del mismo "
                      "asunto que su oración y si adelanta algo. Un reintento PARCIAL con todos los motivos cambia solo "
                      "los beats con motivo (lo demás queda congelado); lo que el juez sigue marcando sale del papel. "
                      "Lo deja para que Omar lo revise antes de la voz; Fase 2 lo consume.", "escaleta, narración por cap y beat, títulos, pool, `sellos_clima`",
                      "`01e_pantalla.json/.md` en el topic de Fase 1", "F36", "vivo (fase 1)"),
    "archive_clipping.html.tmpl": ("La forma del recorte de diario (papel, kicker, titular).", "un recorte del plan",
                                   "HTML", "F1", "vivo (la ficha de estilo papel)"),
    "chapter_question.html.tmpl": ("La forma de la pregunta de cierre sobre la foto oscurecida.", "la pregunta",
                                   "HTML", "F2", "vivo"),
    "index.html.tmpl": ("La página base de cada proyecto HyperFrames (escenas, overlays, timeline).", "escenas + "
                        "overlays", "index.html", "F1", "vivo"),
    "scene.html.tmpl": ("La forma de una escena (la foto o el clip con su movimiento).", "una escena", "HTML", "F1",
                        "vivo"),
    "title_card.html.tmpl": ("La forma del title card del capítulo; desde F29c también la de la ficha.", "kicker + "
                             "título", "HTML", "F1", "vivo"),
}

# funciones (o archivos) que el camino de producción ya no llama: (qué, por qué, commit desde el que no corre)
MUERTOS: list[tuple[str, str, str]] = [
    # F37 §B.4: el borrador del director (el último muerto de F36) se borró con su prompt; no queda ninguno
]


def fecha(h: str) -> str:
    if h == "—":
        return "nunca en fase2b"
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
          "resultado se descarta** (lo dice la columna «por qué»). F36 D borró lo de DECISIONES 18:17 y lo muerto del mapa "
          "(«borrar, no apagar»); lo que queda en esta tabla está explicado en F36_REPORT.md."]
    (ROOT / "lab" / "MAPA_MODULOS.md").write_text("\n".join(L) + "\n", encoding="utf-8")
    print(f"{len(filas)} módulos · {len(aristas)} aristas · {len(muertos)} muertos")


if __name__ == "__main__":
    main()
