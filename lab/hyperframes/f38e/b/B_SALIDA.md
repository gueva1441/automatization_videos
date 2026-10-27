# F38e — Parte B (Colocación B1–B4) — salida en texto (subagente B, 2026-10-27)

Handoff: `lab/hyperframes/f38e/HANDOFF_F38e_lo_que_rompe_cualquier_video.md` §B · contrato `lab/hyperframes/f38/REVISION_GUION_F38d.md` §2–§3.
Base: HEAD `2453cf8`, rama `f11-guion-v4`. Sin commit (commitea CC). Nada en `data/`; `fase2b` no se corrió (B.5 queda para después de A).

## Archivos tocados / creados
| archivo | qué |
|---|---|
| `script_engine/pantalla_colocar.py` (M, CRLF) | B1 `instantes` (l. 64–83), B2 `hasta_el_corte` (l. 133–146) + bloque del reloj en `repartir` (l. 364–403), B3 `en_orden` (l. 250–260) + `colocar_uno` (l. 323–356); docstrings |
| `script_engine/gfx_realizador.py` (M, CRLF) | B4 `pregunta_cierre_fuente` (l. 175–215), `pregunta_cierre` compatible (l. 218–221); docstring del módulo |
| `test_module_f38e_b.py` (nuevo, CRLF) | 11 tests: B1 ×3, B2 ×2, B3 ×3, B4 ×4 (incluida la tabla de Vajont desde `lab/hyperframes/f38/b2/fase1/`) |
| `test_module_f37b_colocar.py` (M) | 2 tests editados (ver «Tests») |
| `test_module_f29c_rotulista.py` (M, CRLF) | 1 test editado (ver «Tests») |
| `lab/hyperframes/f38e/b/sim_b4_cierre.py` (nuevo) | simulación B4 sobre los 7 caps, con la regla que corre (importa el módulo; no hay copia de la regla) |
| `lab/hyperframes/f38e/b/B4_simulacion.md` (nuevo) | la tabla de abajo |
| `lab/hyperframes/f38e/b/antes/GUION_PANTALLA.*` (ya estaban) | copia de hoy, md5 `0af5b1dc…` del .md |

No se tocó: `gfx_layer.py`, `fase2b.py`, `m01e_pantalla.py`, `m01d_particion.py`, `voz_utils.py`, `pantalla_filtros.py`, `gfx_guion.py`, ni los tests «no editar».

## B1 — todo inicio de escena dentro de la oración ancla (`pantalla_colocar.instantes`)
- Antes: el intento 2 probaba solo el primer inicio de escena **después** del instante original (`base`) y dentro de la oración.
- Ahora: todo inicio de escena con `s.t0 ≤ e.start ≤ s.t1`, antes o después de la palabra ancla, **en orden de tiempo** (elegido: es el orden de la escalera misma —el paso 1 ya prefiere el inicio de la oración antes que la escena siguiente— y es lo que simuló el analista para D47: 79,6 antes que un corte posterior). Sin repetidos (`add` dedupea por instante: una escena que arranca justo en el inicio de la oración ya es «1 · inicio de la oración»). Orden de la escalera intacto: 1 → 2 → 3. Nombre: `2 · inicio de la escena N`.
- Propaga solo: `pantalla_filtros.lectura` (fichas y citas), el reloj y `clima.sellos_del_papel` llaman a `instantes`.

## B2 — el reloj mueve su fin con el intento (`repartir`, bloque del reloj; `hasta_el_corte`)
- Antes: `end = start + duration` fijo con el instante original → todo intento más tarde «quedaría menos de TICKER_MIN». Peor: `hasta_el_corte` corre **antes** del reparto (F37 C) y ya había recortado el 9 OCT de ch05 a 1,88 s, así que hasta el instante original fallaba.
- Ahora: `hasta_el_corte` deja en el reloj la duración que trae (`duracion_plena`, `setdefault` la primera vez) y el margen del corte (`margen_corte` = 1 cuadro, el que ya usaba). `repartir` prueba cada intento con `fin = min(t + duracion_plena, fin de la escena de t − margen)`: ≥ `TICKER_MIN` (gfx_pool), sin cambio de fecha, sin solape. El elegido queda con esa duración; la fila «movido» dice `a0 → t (como), dura X s (corta en Y s)` y sus `intentos`; el recorte viejo (`rotulista.corte` del instante original) se quita porque ya no aplica; el segundo `hasta_el_corte` no encuentra nada que acortar. Constantes usadas: `TICKER_MIN` (gfx_pool), 1 cuadro (ya en `hasta_el_corte`); ningún número nuevo.
- Efecto colateral correcto: el reparto ve el tramo real del reloj aun sin `hasta_el_corte` antes (test `test_c_el_reparto_ve_el_reloj_recortado_al_corte` editado por eso).

## B3 — por qué Q51 pasó de [17] a [18] «sin motivo»
**Causa (archivo:línea, con datos de v6):** no es un bug de colocación: el crítico «¿estorba?» tiró los dos intentos de [17] con motivo (`output/f8s3-vajont-f30/_fase2b_work/gfx_ch05.log`, corrida del `--plan-only` de F38d):
- `115.5s ficha ««Que Dios nos ayude» — Alberico Biadene» → ESTORBA — El bloque tapa parte del texto manuscrito de la carta en la esquina superior izquierda.`
- `121.9s … → ESTORBA — El bloque cubre parte del texto manuscrito de la carta en la imagen.`
- `128.2s … → NO ESTORBA`.
Las fallas sí quedaron en la fila `rotulista.escena` del plan (`gfx_plan_ch05.resolved.json`: `"intentos": ["1 · palabra ancla (115.46 s): estorba — …", "1 · palabra de más peso (121.86 s): estorba — …"]`), pero el guion de pantalla no lee esa fila: lee `movido_escena` (`gfx_guion.py:286`), y `pantalla_colocar.py:317` (antes) escribía ahí solo el destino, `115.46 → 128.20 s (3 · oración siguiente [18], inicio de la escena 13)`, sin el `· antes: …`. Además `b["critico"]` (l. 313–315, antes) guarda solo el veredicto del intento ganador, por eso el guion dice «pasó (crítico ¿estorba?: no estorba)». Los `intentos_fallidos` de los filtros (`1 · inicio de la oración (113.24 s): sin tiempo de lectura…`, `3 · oración siguiente [18] (128.16 s): sin tiempo de lectura…`) tampoco se sumaban.
**Veredicto:** Q51 queda en [18] por el crítico (tapaba la carta manuscrita en la escena 12), no por un bug; con B3 el guion lo declara. Si Omar la quiere en [17] es gusto (`--plan-edit`), no código.
**Arreglo general:** `colocar_uno` junta las fallas de los filtros (`intentos_fallidos`) con las del reparto, las ordena por el instante «(t s)» que cada una trae (`en_orden`, sin repetidas) y las escribe en `movido_escena` (lo que lee el guion), en `b["intentos_fallidos"]` y en la fila «movido» (`intentos`, nunca vacío: si no hubiera ninguna, «sin falla registrada: el instante original (t s) no estaba entre los intentos»). La fila «fuera» también lleva las de los filtros. El reloj movido ya declaraba las suyas (y ahora dice la duración).

## B4 — pregunta de cierre desde la voz (`gfx_realizador.pregunta_cierre_fuente`)
Regla del handoff, exacta: (i) última oración de la voz del cap termina en «?» (tolerando comilla/paréntesis de cierre) → `voz-pregunta`; (ii) por cada oración del `cierre` del último beat, la oración de la voz de ese beat con más **palabras de contenido** en común (`evidence._content`: las mismas que `ya_dicho` llama «palabras de contenido» —≥ 5 letras, sin `_FUNC` ni meses—, raíz de 6; empate: la más tardía; sin coincidencia: ninguna), en orden de la voz y sin repetir → `voz-alineada`; (iii) el `cierre` literal → `escaleta`. Sin umbral: el máximo. La voz del cap = `real["beats"][i]["texto"]` (párrafos de `01b_narracion_v3`, lo que ya arma `ventanas`), partida con `voz_utils.oraciones_de_texto(texto)`. Sin lista nueva de stopwords. `pregunta_cierre(real)` sigue devolviendo solo el texto (compatibilidad con `gfx_layer.closing_question`).

Simulación (`sim_b4_cierre.py`, entradas congeladas `lab/hyperframes/f38/b2/fase1/f8s3-vajont/`):

| cap | antes (cierre de la escaleta) | ahora (texto) | fuente | car. | lectura s |
|---|---|---|---|---|---|
| ch01 | El dique no cedió esa noche. Lo que llegó a la cama de Micaela vino por encima de él. | Pero el dique no cedió esa noche. Lo que llegó a la cama de Micaela vino por encima de él. | voz-alineada | 90 | 6.0 |
| ch02 | En marzo del cincuenta y nueve, en otro embalse de la misma empresa, una montaña caminó primero. | En marzo de mil novecientos cincuenta y nueve, en otro embalse de la misma empresa, una montaña caminó primero. | voz-alineada | 111 | 7.4 |
| ch03 | El cuatro de noviembre, durante las pruebas, el agua tuvo su primera respuesta. | El cuatro de noviembre, durante las pruebas, el agua tuvo su primera respuesta. | voz-alineada | 79 | 5.3 |
| ch04 | La presa cambió de dueño con el agua todavía subiendo. La montaña no se enteró del contrato. | La presa cambió de dueño con el agua todavía subiendo. La montaña no se enteró del contrato. | voz-alineada | 92 | 6.1 |
| ch05 | A las diez y media de la noche, el párroco de Casso escuchó algo y abrió la ventana. | A las diez y media de la noche, el párroco de Casso escuchó algo y abrió la ventana. | voz-alineada | 84 | 5.6 |
| ch06 | Tres días después llegó el presidente del Consejo. La gente ya sabía qué pedirle. | Tres días después llegó el presidente del Consejo. La gente ya sabía qué pedirle. | voz-alineada | 81 | 5.4 |
| ch07 | La sentencia dice inundación agravada por la previsión del evento. No dice quién, entre la posdata de la mañana y las diez y treinta y nueve de la noche, decidió que Micaela siguiera durmiendo. | ¿Quién decidió que Micaela siguiera durmiendo? | voz-pregunta | 46 | 3.1 |

Contra lo esperado por el analista: **igual en los 7** (ch01 = «Pero el dique…» + «Lo que llegó…»; ch02, ch03, ch05 = su última oración; ch04 y ch06 = sus dos últimas; ch07 = la pregunta). Única diferencia: ch07 mide 46 caracteres (el analista contó 45); lectura 3,1 s.

**Cambio mínimo que necesita `gfx_layer.closing_question` (no lo toqué; lo hace CC después de A):**
```
l. 292:  from script_engine.gfx_realizador import pregunta_cierre_fuente
l. 294:  txt, fuente = pregunta_cierre_fuente(real) if real else (None, None)
l. 303:  "fuente": fuente,                      # «voz-pregunta» / «voz-alineada» / «escaleta» (F38e B4)
l. 308:  log.append(f"  pregunta de cierre ({fuente}, último beat {real['beats'][-1]['n']}): {txt!r}")
```
`gfx_guion.py:315–319` ya pasa `q.get("fuente")` al guion: con eso la fila «pregunta de cierre» dice de dónde salió sin tocar `gfx_guion`. Docstring de `closing_question` («la pregunta es el `cierre` del último beat, literal») queda vieja hasta ese cambio. La posición no cambia (sigue en su pausa al final del cap, F32).

## Tests
- `test_module_f38e_b.py`: **11/11** verdes.
- Tests editados (comportamiento que B1/B2 cambian a propósito):
  - `test_module_f37b_colocar.py::test_b1_q50_corta_se_mueve_a_la_oracion_siguiente_si_no_cabe`: con B1 la cita Q50 entra en el inicio de la escena 7 (19,5 s), dentro de su oración y antes del ancla (19,5 + 6,0 < 27,1), en vez de saltar a la oración siguiente; se asevera eso y que la oración siguiente queda como intento posterior.
  - `test_module_f37b_colocar.py::test_c_el_reparto_ve_el_reloj_recortado_al_corte`: con B2 el reparto recorta el reloj en su corte por sí mismo; aun sin `hasta_el_corte` antes la ficha de 88,5 no choca (antes chocaba con un tramo que ya no se veía); se asevera también `duracion_plena`.
  - `test_module_f29c_rotulista.py::test_reloj_no_va_encima_de_un_recorte_y_arranca_en_la_escena_siguiente_del_beat`: «termina donde terminaba (15,0)» era el comportamiento que B2 reemplaza; ahora termina en el corte de su nueva escena (18,0) con `duracion_plena` 12.
- Suite de mis módulos: `test_module_f38e_b.py test_module_f37b_colocar.py test_module_f29c_rotulista.py test_module_f29a.py test_module_f32.py` → **38/38**.
- «No editar»: `test_module_f34.py`, `test_module_f36.py` verdes; `test_module_f36c_pantalla.py` **3 rojos** (`test_a_salida_valida_el_esquema`, `test_b_candado_en_papel_rechaza_el_anio_que_no_esta_en_el_dato`, `test_d_un_dato_no_sale_dos_veces_en_el_video`), todos sobre `m01e_pantalla.validar`, que edita C en paralelo (`git diff --stat`: +79/−20 en `m01e_pantalla.py`). Verificado: cargando el `m01e_pantalla.py` de HEAD con mis módulos actuales, `f36c` da **9/9** → no son míos. Corrida completa del grupo: 57 verdes + esos 3.
- Suite rápida `test_module_f25c.py test_module_f24.py test_module_f21.py`: **58/58**.
- CRLF comprobado con `file`: `pantalla_colocar.py`, `gfx_realizador.py`, `test_module_f29c_rotulista.py`, `test_module_f38e_b.py` con CRLF; `test_module_f37b_colocar.py` era LF y sigue LF.

## Stickers nuevos para `lab/MAPA_MODULOS.md`
- `pantalla_colocar`: Pone cada texto del papel en su lugar (F37: antes rotulista_colocar): la ficha dura su lectura entre callout_dur_min y callout_dur_max sin pasar el corte, qué forma toma (ficha normal, nombre o cita con autor; papel = recorte) y el reparto: nunca al mismo tiempo (DECISIONES 17:58) y el crítico en cada intento, moviendo en vez de cortar (otro instante, todo inicio de escena dentro de la oración —F38e B1—, la oración siguiente, el otro lado); el reloj mueve su fin con el intento y se recorta en su nuevo corte (F38e B2); lo que no entra queda «sin colocar» y todo lo movido declara qué falló en cada intento anterior, también en los filtros (F38e B3). F38c: cada ficha lleva el juicio del autor hasta el guion de pantalla.
- `gfx_realizador`: Hace que la pantalla obedezca a la escaleta: ventanas de tiempo de cada beat, qué datos puede mostrar cada uno y la pregunta de cierre, que desde F38e B4 sale de la voz (la última oración del cap si es pregunta; si no, las oraciones de la voz del último beat que alinean con su `cierre`; si ninguna, el `cierre` literal) y dice de dónde salió. F37: el cierre del plan solo deja los sellos del papel y ningún punch_in (sin las ramas del camino sin papel, del contador ni de los íconos).

## Lo que queda abierto (B entero)
- b1. `gfx_layer.closing_question` todavía guarda `fuente: "escaleta (cierre del último beat)"` y llama a `pregunta_cierre` (texto solo): el texto nuevo ya sale (ch07 «¿Quién decidió…?»), pero la fuente del guion será la vieja hasta el cambio mínimo de arriba (después de A).
- b2. Fila #9 del contrato (ch01 «desfasada»): el handoff F38e dice «la posición no cambia» (la pregunta va en su pausa al final del cap); con B4 el texto de ch01 es lo que la voz dice en [14]+[15], pero sigue mostrándose después de [16], no anclada en [14]. Si el analista esperaba la ancla en [14], es un cambio de posición que el handoff excluye.
- b3. `TICKER_MIN` se mide contra el fin ya con el margen de 1 cuadro cuando `hasta_el_corte` corrió antes (como en gfx_layer); si alguien llama a `repartir` sin `hasta_el_corte` antes, el margen es 0 (el segundo `hasta_el_corte` lo recorta después y puede dejar TICKER_MIN − 1 cuadro en el caso límite exacto).
- b4. `b["critico"]` sigue guardando solo el veredicto del intento ganador y `plan["critico_rotulista"]` solo su fila: las fallas del crítico en intentos previos viajan como texto en `movido_escena`/`intentos`, no como filas del crítico (el guion las muestra en «movido»).
- b5. B.5 (`--plan-only` de Vajont con el papel congelado y la tabla contra las filas #2, #5, #6, #8, #9) no se corrió: espera a que A termine (CC avisa). Lo esperado con lo programado: #2 D47 a 79,6–84,3 (escena 8 dentro de [11]); #5 reloj 9 OCT en 89,43 con 12 s (hasta 101,43, antes del corte 109,6; sin solape con Q50 ni Q51); #6 Q51 sigue en [18] pero con sus 4 fallas declaradas (2 de lectura de los filtros + 2 del crítico); #8 ch07 «¿Quién decidió que Micaela siguiera durmiendo?» (46 car., 3,1 s); #9 ch01 texto «Pero el dique no cedió esa noche. Lo que llegó a la cama de Micaela vino por encima de él.» (misma posición). Todo lo demás debería quedar igual, salvo el crítico con caché nueva en los instantes nuevos (D47 a 79,6 y 9 OCT no pasan por el crítico: el reloj no lo tiene; D47 sí → una llamada a Gemini, centavos) y las filas «movido» que ahora traen «antes: …».
- b6. Los 3 rojos de `test_module_f36c_pantalla.py` son de C (m01e en edición); se vuelven a mirar cuando C termine.
