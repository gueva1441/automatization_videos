# F37 — El papel elige más y mejor; Fase 2 mueve en vez de cortar · reporte

Handoff `lab/hyperframes/f37/HANDOFF_F37_papel_y_colocar.md` (analista, 2026-10-26 22:40). Base `2067c77`. Pedido de Omar:
tres partes A → B → C, un commit cada una, sin PARADA entre ellas salvo §Frenos; esfuerzo high. Contrato:
`lab/hyperframes/f36/REVISION_PAPEL.md`. **Ningún freno se dio** (el JSON del papel parseó en los dos intentos, el tope
alcanzó para el reintento —US$ 0.7649 de 1.00—, las 7 narraciones alinean, los renombres no rompieron la suite).

Commits en `f11-guion-v4`: `6631703` (paso 0) · `cab5ce9` (A) · `838a104` (B) · C (este reporte, el papel de Vajont, el
guion y el arreglo de la escalera que la corrida encontró). Sin render, sin `--aprobar-guion`, sin merge; los prompts
de escaleta, guionista y partición no se tocaron.

## Lecturas declaradas (paso 1)
`C:\Users\Canada\AppData\Roaming\Claude\side-session-notes\local_4a1d5345…\F36_C_D_cierre.md`, la nota de traspaso
`…\local_529ea96e…\F36_handover_a_C_D_nuevo.md`, `CLAUDE.md`, `DECISIONES.md` entero (22:26 y 22:32), `lab/ESTADO_SESION.md`
(cabecera, F36, F34), `lab/hyperframes/f36/REVISION_PAPEL.md`, el handoff F37 entero, `F36_REPORT.md` §C, §D y «Lo que
queda abierto», `.claude/commands/tanda.md`. Código leído antes de tocar: `m01e_pantalla`, `rotulista_filtros`,
`rotulista_colocar`, `clima`, `gfx_rotulista`, `gfx_critic`, `gfx_realizador`, `gfx_layer`, `gfx_director`,
`gfx_literal_lock`, `voz_utils`, `gfx_config` (perfil), `fase2b` (CLI y `--plan-only`), `audio_manager` (el narrador).

## Paso 0 (`6631703`)
`DECISIONES.md` tal cual (22:26 «casi nada hardcode», 22:32 «la causa se arregla en el sistema», orden 3b) +
`lab/hyperframes/f36/REVISION_PAPEL.md` + `lab/hyperframes/f37/HANDOFF_F37_papel_y_colocar.md`, tal cual, con rutas
explícitas. Lo ajeno quedó afuera (`diag_234_cap4.py`, `gfx_profiles/*`, `f28a.log`, los `??` viejos).

## Módulos que toca la tanda (paso 2; sticker de `lab/MAPA_MODULOS.md` → después)
| módulo | hoy (sticker de F36) | después de F37 |
|---|---|---|
| `m01e_pantalla` | Fase 1: el papel, una llamada a Sonnet, validación en papel | + fecha del relato, cita sin fecha, descartes «la voz lo dice» verificados, picos sin ficha, coincidencias = preguntas al autor; un reintento con todos los motivos; tope del perfil; `caben` con la velocidad del narrador y sin pasar `callout_dur_max` |
| `voz_utils` | cifras, nombres, oraciones de la voz | + años que dice la voz (`anios_de`, `anios_dichos`, `dice_anio`) y segundos por palabra del narrador (`narrador`, `seg_por_palabra`) |
| `rotulista_filtros` → **`pantalla_filtros`** | `ORDEN` de filtros del papel | lo que el autor juzgó «otro hecho» no corta; `lectura` prueba la escalera de intentos |
| `rotulista_colocar` → **`pantalla_colocar`** | tiempos, colocar, «nunca al mismo tiempo» (`escena_final`) | duración = lectura acotada; `instantes`/`pesos` (escalera); `repartir` reemplaza a `escena_final` (nunca al mismo tiempo + crítico por intento) |
| `clima` | sellos del papel con crítico antes del reparto | la misma escalera + el otro lado, crítico en cada intento |
| `gfx_critic` | `criticize_rotulista` (todos de una vez) + `estorba` | solo `estorba`, por intento (instante y lado); formas de bloques borrados fuera |
| `gfx_director` | borrador de Gemini + contexto del cap (el muerto del mapa) | solo el contexto del cap y la palabra clave de la pregunta |
| `gfx_layer` | director de orquesta, plan del borrador | `plan_base` (title card de la partición), papel = único camino, `_escena` con `repartir` |
| `gfx_rotulista` → **`pantalla_entrada`** | fachada + `preparar_cap` | sin fachada: `preparar_cap`, `alinear`, `palabra_idx`, voz del video |
| `gfx_realizador` | finalizar con ramas del camino sin papel | solo sellos del papel y sin punch_in |
| `gfx_literal_lock` | candado con ramas de bloques borrados | title card, reloj y lo que no viene del papel |
| `gfx_guion` | guion + chequeos | sin lupa/agua/contador; filas «colocar» con intentos; crítico «¿estorba?» |
| `gfx_style`, `gfx_project`, `gfx_pool` | — | sin `golden_fewshot`/`_ELEM`, `load_grade_preset`; docstring de `gfx_pool` al día |
| `gfx_config` / perfil | 101 constantes, `rotulista`, `enable_gfx`, … | `costos` en el perfil; sin `rotulista`, `enable_gfx`, `hyperframes_version`, `block_enabled`, `render_inventory_for_prompt` ni las 15 perillas que solo leía el borrador |
| `fase2b` | `--rotulista`, prefetch del director | sin los dos |
| `lab/MAPA_MODULOS.*` | 35 módulos, 1 muerto | **35 módulos, 115 aristas, 0 muertos** |
Fuera del mapa, en cascada: `gfx_lab_server` (los datos del lab sin la elegibilidad del borrador), `script_engine/gfx_icons/make_bug.py`
(recibe `judge_zoom_box`, su único usuario), `.claude/hooks/guard_mapa.py` (`pantalla_*`), skills `guion-de-pantalla` y
`simular-reglas` y el agente `simulador` (sin `--rotulista`).

## Constantes (paso 4): ninguna nueva
| constante | antes | después | origen |
|---|---|---|---|
| `SEG_POR_PALABRA` 0.35 | fijo | **derivado** cada corrida: `voz_utils.seg_por_palabra` = mediana, oración por oración, de todas las voces del narrador (`voice_id_v4` del perfil de audio, `audio_manager`) en `output/audio/*/chNN_timestamps.json`, cada audio una vez por `tts_hash`. Hoy: **0.3459** (200 oraciones, 9 caps). `SEG_POR_PALABRA_RESPALDO = 0.35` (`# medido: Vajont ch04`) solo si no hay voces; el papel anota cuál usó | medido |
| `TOPE_USD` 0.50 | fijo | `costos.m01e_tope_usd` del perfil (`gfx_config` acepta la clave `costos`); **la clave no está** (perfil fuera de git: la agrega Omar), así que corrió con el respaldo `TOPE_USD_RESPALDO = 1.00` (`# DECISIONES: pedido de Omar F37`) | decisión de Omar (pedido literal) |
| `REINTENTO_FICHAS` 3 | umbral del reintento | **borrado**: el reintento va si hay algún motivo (A.5) | — |
| `OUT_TOKENS_PEOR` 16 000 | peor salida | igual; en el reintento, la salida real del primero si fue más (derivado) | derivado |
| tolerancia de t1 | — | `5e-4` (`# derivado: t1 va redondeado al milisegundo`) en `pantalla_colocar.tiempos` | derivado |
Duración de ficha: `callout_dur_min` 2.5 y `callout_dur_max` 6.0 (identidad F3, perfil); lectura 15 cps (estándar). El
año en dos cifras (`anio % 100`, «la década del cincuenta») es cómo se dice un año, no un número de tema.

---

## Parte A — el autor ve lo que el pool sabe y se corrige solo (commit `cab5ce9`)

### Qué se hizo, por punto
- **A.1a** cada ítem del archivo lleva `fecha` (o `"desconocida"`); las citas, `rol` y `testimonio` («sí»/«no»), como en
  el pool.
- **A.1b «fecha del relato»** (`m01e_pantalla.momentos`, `voz_utils.anios_dichos`): el momento de cada oración = el
  último año que la voz dijo hasta ella (incluida, arrastra de caps anteriores, en cifras o en letras); un año es una
  cifra dentro del rango de años de las `fecha` del pool (1943–2023 en Vajont: derivado del material). Un ítem con año
  posterior se rechaza (`fecha_relato`) salvo testimonio o que la oración ancla o una vecina diga ese año o uno posterior.
  **Lecturas declaradas:** (i) el año dicho en dos cifras también lo sitúa («En la década del cincuenta» = 1950: sin
  esto D47 caía por 1b y nunca llegaba a la pregunta de A.4); (ii) las expresiones relativas («años después», «más
  tarde») **no** se implementaron: piden una lista de palabras (regla 22:26); en Vajont ninguna ficha depende de ellas.
- **A.1c «cita sin fecha»** (`autor_en`): vale solo si el autor aparece en la oración o una vecina, por su nombre (los
  nombres propios del autor sin lo que va entre paréntesis: «Ingeniero jefe (sucesor de Semenza)» no es Semenza) o por
  su rol (todas sus palabras de contenido, por raíz).
- **A.1d** (anotado, sin tocar Fase 1): el research debería traer fecha y contexto de las citas (41 de 57 sin fecha).
- **A.2** `descartados` con `tipo` (formato). `voz_lo_dice` se verifica (`voz_no_lo_dice`): las cifras del ítem
  (valores con «mil»/«millones», sin los años) contra la voz de los caps que lo cuentan (o todo el video); sin cifras, sus
  nombres; una cita sin cifras no se verifica (la voz cita la frase traducida). Si la voz no dice ninguna, el ítem vuelve
  en el reintento con el motivo.
- **A.3a** reemplazo literal en `PANTALLA_SYSTEM`; `PROMPT_VERSION = "m01e-2"`. md5 del SYSTEM `0354c764…` →
  **`e7b3e0a3cb9ec292077cf677d30c5c42`**; md5 del prompt (SYSTEM + formato) `aa1ebc33…` → **`ababbc8b97171aab501211225b7c9c69`**.
  Diff entero del prompt (`f37/a/diff_prompt.txt`):
```
-Prioridades: … en el gancho (capítulo 1), cualquier dato del archivo que la voz no diga en todo el video y que haga quedarse a quien mira: el gancho nunca queda sin ficha. …
+Prioridades: … en el gancho (capítulo 1), cualquier dato del archivo que la voz no diga en todo el video, que haga quedarse a quien mira y que pueda ir en las primeras oraciones del capítulo: el gancho nunca queda sin ficha. …
-                  '"descartados": [{"pool_id": "…", "motivo": "…"}]}')
+                  '"descartados": [{"pool_id": "…", "tipo": "voz_lo_dice" | "spoiler" | "repetido" | "otro", '
+                  '"motivo": "…"}]}')
```
- **A.3b** pico sin ficha → motivo del reintento («el beat 3 de ch02 es pico y quedó sin ficha»); si sigue vacío, ⚠ en el `.md`.
- **A.4** las coincidencias de `no_dicho`/`spoiler` ya no cortan en papel: van como pregunta, con las palabras del
  handoff («D47: la voz dice «2» en una oración posterior en ch03 [17] («…»); ¿es el mismo hecho? si no, mantenelo»). Lo
  que el autor mantiene en el reintento queda `juicio_autor` en la ficha y los filtros de Fase 2 no lo re-cortan
  (`_sin_juicio`); una coincidencia nueva en el reintento corta (no hay más preguntas). Sin reintento (tope), lo
  preguntado corta como en F36.
- **A.5** un reintento con todos los motivos juntos; tokens y costo por intento en el papel y en el `.md`.
- **Cascada declarada (B.2 sobre Fase 1):** `caben` = palabras × segundos por palabra × 15, **sin pasar de
  `callout_dur_max` × 15 = 90**: una ficha más larga no se puede leer en Fase 2 (Q50 tenía 152 «caben» en F36).

### Verificación de A
md5 de ch02 sin `--gfx` `38e5ba14e3d24fd20f9297c9e1dfee24` (RAM 15.8 GB, Firefox 0), rápida **58**, amplia **842 + las 5
previas** (`f37/a/`). Tests `test_module_f37a_papel.py` (9, uno por punto con el caso real de Vajont): Q43 cae por 1c;
un ítem posterior cae y un testimonio no; D47 situado por «cincuenta»; T39 vuelve (la voz no dice «50»); el reemplazo
literal y `tipo`; pico vacío dispara el reintento; D47 llega como pregunta y su juicio es final (y Fase 2 lo respeta);
`SEG_POR_PALABRA` se deriva (copias por `tts_hash` cuentan una vez; otro narrador no cuenta); `TOPE_USD` del perfil.

### Salida de A en seco sobre la respuesta de F36 (`f37/a/seco_validacion_sobre_f36.txt`, sin API)
Q50 cae por `caben` (127 > 90); Q43 cae por cita sin fecha; D47 («2», ch03 [17]) y D105 («1962», ch04 [14]) van como
pregunta; vuelven T21 («3»), T39 («50»), D68 («1,5»: falso, ver abierto) y T85 («11»); pico vacío ch05 b8.

### Simulador de las reglas de A (después del código: declarado; íntegro en `f37/a/simulacion_reglas_a.md`)
Coincide en todo con la corrida en seco. Por regla: **1b** 12 propuestas → 0 cortadas (D47 y D245 se salvan por la
salvedad); **1c** 2 candidatas → 1 cortada (Q43) → queda Q50; **A.2** 58 «voz lo dice» → 40 correctos, 14 no
verificables, **4 vuelven** (T21, T39, D68, T85); **A.4** 12 → 2 preguntadas (D47, D105), 0 cortadas. Frágiles: D47
depende del año en dos cifras; Q50 pasa 1c por el topónimo «Erto»; D68 vuelve porque el parser no lee «y medio».

---

## Parte B — Fase 2 mueve en vez de cortar (commit `838a104`)

### Simulación previa (paso 5, ANTES del código; íntegra en `f37/b/simulacion_previa.md`)
| regla | propuestos | cortados por la regla | quedan |
|---|---|---|---|
| R1 (B.2) duración = lectura 2.5–6.0 s sin pasar el corte | 9 | 1 (Q50: 127 car. = 8.47 s > 6.0) | 8 (las 7 de hoy + D117, cortada por el crítico, no por R1); 8 cambian de duración: T16 12.74 → 2.60, D131 11.24 → 2.73, D245 7.38 → 2.67; texto en pantalla 50.42 → 20.93 s |
| R2 (B.1) mover en vez de cortar, los 8 sin colocar de F36 | 8 | 2 sin salida (COLAPSO, Q50) | 2 mecánicamente (AVISO → escena 8, SILENCIO → oración 11), 4 dependen del crítico (CALMA, INMINENTE, RABIA, D117) |
Ejemplos: T16 ch03 «LA VÍCTIMA DE PONTESEI / Arcangelo Tiziani» 12.74 → 2.60 s; AVISO ch04 87.98 → 88.03 (inicio de la
escena 8, dentro de la oración); COLAPSO ch06 «Longarone ya no.»: cruza el corte, la escena 12 arranca después de la
oración y la siguiente es de otro beat → ninguno. Observaciones del simulador (sin código): los pasos 1–3 de los
cortados por el crítico caen sobre la misma foto (Gemini probablemente repite); el orden se dejó literal del handoff.

### Qué se hizo, por punto
- **B.1 escalera** (`pantalla_colocar.instantes`): 1) otro instante de la oración (el original —ancla de la ficha, palabra
  de más peso del sello—, la de más peso, el inicio, la ancla); 2) el inicio de la escena siguiente dentro de la oración;
  3) la oración siguiente del beat (y, desde C, el inicio de la escena que arranca dentro de ella); 4) solo contra el
  crítico, el otro lado (`lados`: sello y recorte izquierda/derecha; la ficha tiene una sola posición: sin paso 4). Fichas
  y recortes: `pantalla_filtros.lectura` deja los intentos que entran en su lectura (el de otra oración re-pasa candado,
  no dicho y spoiler); `pantalla_colocar.repartir` (reemplaza a `escena_final`) prueba, por prioridad, recortes → reloj →
  fichas: nunca al mismo tiempo + `gfx_critic.estorba` en cada intento. Sellos: `clima.sellos_del_papel` con la misma
  escalera, corte, nunca al mismo tiempo y crítico por intento y por lado. Reloj: la misma escalera (sin crítico), ≥
  `TICKER_MIN` en pantalla, sin pasar un cambio de fecha. Lo que no entra: «papel sin colocar» con cada intento y por
  qué falló. Caché del crítico por identidad: instante, descripción (con el lado) y voz.
- **B.2** `duracion`/`tiempos`: lectura acotada entre `callout_dur_min` y `callout_dur_max`, nunca después del corte.
- **B.3** la cita: los intentos se miden una vez con `caracteres` (el autor una sola vez); el reparto no re-cuenta.
- **B.4 papel = único camino:** se borró el borrador del director (Gemini, `_SYSTEM_PROMPT`, `_SCHEMA`, validador,
  `resolve_plan`, caché `gfx_plan_chNN.json`, `prefetch_plans`, zoom por visión, cifras «ya animadas», elegibilidad de
  facts, etiqueta de fuente; `judge_zoom_box` pasó a `make_bug`, su único usuario); `gfx_layer.plan_base`: el title card
  con el título de la partición; `--rotulista` ya no existe (y `GfxRules.rotulista` tampoco); restos del abierto 19 de
  F36 (`gfx_critic.describe`/`KIND_LABEL` —reducidos a sello, recorte y ficha, en uso—, el `pop` de `gfx_layer`, ramas de contador/íconos de
  `gfx_realizador.finalizar`, ramas de `gfx_literal_lock`, lupa/agua/contador de `gfx_guion.eventos_cap`,
  `gfx_style.golden_fewshot`, docstring de `gfx_pool`) y muertos del abierto 13 (`gfx_critic.voice_around`,
  `gfx_project.load_grade_preset`, `gfx_config.block_enabled`, `gfx_style._ELEM`, `GfxRenderSettings.enable_gfx`,
  `hyperframes_version`). En cascada: 15 perillas de `GfxRules` que solo leía el borrador (las 9 que trae el perfil de Omar
  quedan declaradas huérfanas en `HUERFANAS_TOKENS`: `interrupt_min_sec`, `callout_sec_per_word`, `callout_base_sec`,
  `zoom_conf_min`, `archive_dur`, `archive_head_max_words`, `archive_body_default`, `archive_body_head_max_words`,
  `archive_body_max_words`), y `render_inventory_for_prompt`. `title_pre_roll` se borró por error en el barrido y se
  repuso (lo lee `fase2b` con un alias).
- **B.5 renombres** `gfx_rotulista` → `pantalla_entrada` (sin fachada: cada módulo se importa por su nombre),
  `rotulista_filtros` → `pantalla_filtros`, `rotulista_colocar` → `pantalla_colocar` (`git mv`); imports, tests, mapa
  (`mapa_hechos`, stickers), hook `guard_mapa`, skills y agente. Runners de lab rotos borrados: los 3 del abierto 15
  (`f29b/a/f29b_crudas.py`, `f29b/b/f29b_vajont.py`, `f29c/b/f29c_vajont.py`) y 3 más que también estaban rotos desde F36
  (`f29b/b/f29b_tabla.py` —`lo_que_pide`—, `f30b/f30b_vajont.py` —`gastado`—, `f34/a/salida_a.py` —`PROMPT_VERSION`—).
- **B.6 tests** `test_module_f37b_colocar.py` (8 en B, 9 con el de C): AVISO → inicio de la escena 8; SILENCIO →
  oración siguiente; COLAPSO sin salida, con los intentos; el crítico re-juzga en el otro lado; la ficha que estorba
  prueba el intento siguiente; Q50 corta se corre a la oración siguiente; ninguna ficha > `callout_dur_max` ni <
  `callout_dur_min`; la cita cuenta el autor una vez. Tests de lo borrado fuera (`test_module_gfx_director.py` entero y
  10 funciones); adaptados los que miraban `escena_final`, `unidades`, `criticize_rotulista`, el candado de sellos y de
  la pregunta reformulada, y la calibración de perillas borradas.

### Verificación de B
`--plan-only` con el papel de F36 (`f37/b/plan_only_papel_f36.log`, guion `f37/b/GUION_PANTALLA_papel_f36.*`): corre
entero, 0 fallbacks; AVISO → 88.03 (escena 8), INMINENTE → otro lado, D117 → inicio de su oración, D17 → oración
siguiente; COLAPSO, SILENCIO, CALMA, RABIA y Q50 sin colocar, con su lista. md5 `38e5ba14…`, rápida **58**, amplia **804 +
las 5 previas** (`f37/b/`). **Firefox:** al primer intento del verificador había 13 procesos de Firefox y 14.2 GB (el
verificador frenó); se cerró con `CloseMainWindow` (regla de Omar), quedó 0 y 15.6 GB, y recién ahí corrió el md5.

---

## Parte C — corrida de Vajont y comparación (commit C)

### C.1 `m01e_pantalla` suelto (`python -m script_engine.m01e_pantalla f8s3-vajont`, `f37/c/m01e_vajont.log`)
Dos llamadas: **intento 1** 65 940 tokens de entrada · 29 803 de salida · **US$ 0.4299** · 201 s (fichas fuera 0 ·
preguntas 5 · vuelven 1 · picos vacíos 0) → **reintento** 66 978 · 20 103 · **US$ 0.3350** · 136 s (preguntas 0 ·
vuelve 1 —D68, falso—). **Total US$ 0.7649** (tope 1.00, respaldo). Tarjeta: **no** (el modelo la dejó en null: T72
daba 22:43 y la voz dice 22:39). Papel en `data/scripts/_steps/f8s3-vajont/01e_pantalla.*` (copia en `f37/c/`).

#### `01e_pantalla.md` entero
````markdown
# Guion de pantalla en papel — f8s3-vajont

`m01e_pantalla` m01e-2 (md5 del prompt `ababbc8b97171aab501211225b7c9c69`) · claude-sonnet-5-5 medium · 2 intento(s) · US$ 0.7649 · tokens de entrada 65940

Segundos por palabra 0.3459 (mediana de 200 oraciones de 9 caps del narrador N9Z5MLTIaHFLflaLtbDi) · tope US$ 1.0 (respaldo (el perfil no trae costos.m01e_tope_usd)) · intento 1: in 65940 · out 29803 · US$ 0.4299 · intento 2: in 66978 · out 20103 · US$ 0.3350

**Tarjeta:** —

Totales: 12 fichas · 8 sellos · 4 relojes · sin tarjeta · 26 descartados

## ch01 — Cama en la oscuridad

- beat 1 · gancho · PICO · ficha **D131** [normal] «SALTO DEL AGUA · Más de 260 metros» en [1] sobre «presa» (31/90 car.) · año — / relato — · aporta: La voz dice que la ola pasó por encima, pero no dice desde qué altura cayó el agua al valle. · sello **PÁNICO** en [4]
- relojes: 9 OCT 1963 en [13]

## ch02 — El muro que tapa

- beat 2 · planteo · ficha **D117** [papel] «ACTA DEL CONSEJO SUPERIOR · Solo 13 de 34 representantes presentes» en [2] sobre «aprobó» (63/90 car.) · año — / relato 1943 · aporta: La voz dice que el proyecto se aprobó en 1943, pero no que fue con un procedimiento irregular y menos de la mitad del Consejo presente. · sello **CALMA** en [6]
- beat 3 · escalada · PICO · ficha **D47** [normal] «FRENTE DEL DESMORONAMIENTO · 2 km de frente y 600 m de desarrollo vertical» en [11] sobre «desmoronamiento» (71/83 car.) · año 1950 / relato 1943 · juzgado por el autor: otro hecho {'spoiler': ['2']} · aporta: La voz dice que Müller detectó el desmoronamiento, pero no sus dimensiones. Los 2 km de la fisura de ch03 son otro hecho. · sello **AMENAZA** en [16]
- relojes: —

## ch03 — La costura abierta

- beat 4 · giro · PICO · ficha **T15** [normal] «ROCA CAÍDA AL LAGO · 3 millones de metros cúbicos» en [1] sobre «roca» (46/83 car.) · año 1959 / relato 1959 · juzgado por el autor: otro hecho {'spoiler': ['3']} · aporta: La voz habla de una masa de roca y de la ola de veinte metros, pero no del volumen que cayó al lago de Pontesei. · sello —
- beat 5 · escalada · ficha **D49** [normal] «ANCHO DE LA FISURA · Más de 1 metro de ancho» en [17] sobre «fisura» (41/90 car.) · año 1960 / relato 1960 · aporta: La voz da el largo de la fisura (casi dos kilómetros) pero no cuánto se abría. · sello —
- relojes: —

## ch04 — La ola de juguete

- beat 6 · giro · ficha **T39** [normal] «DERRUMBE QUE ADVERTÍA MERLIN · 50 millones de metros cúbicos de roca» en [6] sobre «advertencia» (65/90 car.) · año 1961 / relato 1961 · juzgado por el autor: otro hecho {'spoiler': ['50']} · aporta: La voz dice que Merlin volvió a advertir sobre Erto, pero no la magnitud del derrumbe que anunciaba. · sello —
- beat 7 · giro · PICO · ficha **D105** [normal] «CREACIÓN DE ENEL POR LEY · diciembre de 1962» en [15] sobre «ENEL» (41/90 car.) · año 1962 / relato 1963 · juzgado por el autor: otro hecho {'no_dicho': ['1962']} · aporta: La voz nombra a ENEL y la venta, pero no cuándo se creó el ente estatal que iba a comprar la presa. · sello —
- relojes: 4 NOV 1960 en [0]

## ch05 — Piedras rodando

- beat 8 · escalada · PICO · ficha **D161** [normal] «LADERA CON EL AGUA A 710 M · 2 cm por día» en [0] sobre «centímetro» (38/90 car.) · año — / relato 1963 · juzgado por el autor: otro hecho {'spoiler': ['2']} · aporta: La voz da 0,5 cm por día con el agua a 700 m, pero no que a 710 m el desprendimiento llegó a 2 cm por día. · sello **SILENCIO** en [10]
- beat 9 · giro · ficha — · sello **INMINENTE** en [26]
- relojes: —

## ch06 — El gran rugido

- beat 10 · pico · PICO · ficha **D121** [normal] «ROCA QUE CAYÓ · 270 millones de metros cúbicos de roca» en [3] sobre «desploma» (51/90 car.) · año 1963 / relato 1963 · aporta: La voz cuenta que la ladera entera se desploma, pero no el volumen de roca que entró al lago. · sello **COLAPSO** en [3]
- beat 11 · respiro · ficha **D228** [normal] «PREPARATIVOS EN BELLUNO · 1000 camas para refugiados» en [25] sobre «rescate» (49/62 car.) · año — / relato 1963 · aporta: La voz dice que nadie coordinó el rescate, pero no que se prepararon camas y donantes de sangre para sobrevivientes que no había. · sello —
- relojes: —

## ch07 — Diarios y verdades

- beat 12 · revelacion · PICO · ficha **T85** [normal] «REMISIÓN A JUICIO · contra 11 personas» en [11] sobre «resolución» (35/90 car.) · año 1968 / relato 1968 · aporta: La voz da la fecha de la resolución, pero no a cuántas personas alcanzaba. · sello **RABIA** en [1]
- beat 13 · cierre · ficha **D245** [normal] «MONTEDISON A LONGARONE · 55.645.758.500 liras» en [18] sobre «indemnización» (42/62 car.) · año 1997 / relato 1971 · aporta: La voz da la oferta de ENEL, pero no que en 1997 un tribunal condenó a Montedison a pagar esa suma al municipio de Longarone. · sello **MEMORIA** en [21]
- relojes: 20 FEB 1968 en [11], 29 NOV 1968 en [14]

## Lo que cayó

- (nada)

## Reintento: los motivos que se le mandaron al autor

- D47 (ch02 beat 3, oración [11]) «FRENTE DEL DESMORONAMIENTO · 2 km de frente y 600 m de desarrollo vertical»: la voz dice «2» en una oración posterior en ch03 [17] («Ese año hubo un pequeño desmoronamiento en el Toc, y después del desmoronamiento los habitantes vieron algo nuevo en la ladera: una fisura de casi dos kilómetros de largo, corriendo por la montaña como una costura abierta.»); ¿es el mismo hecho? si no, mantenelo
- T15 (ch03 beat 4, oración [1]) «ROCA CAÍDA AL LAGO · 3 millones de metros cúbicos»: la voz dice «3» en una oración posterior en ch06 [6] («Benito Castellano oye un ruido «como de un trueno de verano multiplicado cien veces, muy lóbrego, que duró tres o cuatro minutos».»); ¿es el mismo hecho? si no, mantenelo
- T39 (ch04 beat 6, oración [6]) «DERRUMBE QUE ADVERTÍA MERLIN · 50 millones de metros cúbicos de roca»: la voz dice «50» en una oración posterior en ch05 [17] («Biadene volvió al papel y agregó una posdata: Rossi lo llamaba en ese momento, y «las mediciones de esta mañana resultan todavía mayores que las de ayer, ¡alcanzando un aumento del 50%!!».»); ¿es el mismo hecho? si no, mantenelo
- D105 (ch04 beat 7, oración [15]) «CREACIÓN DE ENEL POR LEY · Diciembre de 1962»: la voz dice «1962» en la oración ancla o en una vecina en ch04 [14] («En noviembre de mil novecientos sesenta y dos, la ladera ya se desplazaba más de un centímetro y medio por día.»); ¿es el mismo hecho? si no, mantenelo
- D161 (ch05 beat 8, oración [0]) «LADERA CON EL AGUA A 710 M · 2 cm por día»: la voz dice «2» en una oración posterior en ch05 [2] («Desde el dos de octubre, los avisos se multiplicaron: sacudidas, estruendos que bajaban de la ladera de noche, grietas nuevas en la tierra de Erto, movimientos en la superficie.»); ¿es el mismo hecho? si no, mantenelo
- D68: dijiste que la voz lo dice («La voz dice más de un centímetro y medio por día en noviembre de 1962.»); la voz de ch04 no dice «1,5» («En noviembre de 1962, el desplazamiento de la ladera superó el umbral de 1,5 cm por día.»): vuelve a ser candidato

### Preguntas y respuesta del autor

- D47 {'spoiler': ['2']}: la mantuvo en ch02 beat 3 [11]: otro hecho
- T15 {'spoiler': ['3']}: la mantuvo en ch03 beat 4 [1]: otro hecho
- T39 {'spoiler': ['50']}: la mantuvo en ch04 beat 6 [6]: otro hecho
- D105 {'no_dicho': ['1962']}: la mantuvo en ch04 beat 7 [15]: otro hecho
- D161 {'spoiler': ['2']}: la mantuvo en ch05 beat 8 [0]: otro hecho

## Descartados por el modelo

- Q49 [voz_lo_dice]: Dato central del gancho, pero la voz lo cita casi entero en ch01 [6]-[9].
- D24 [otro]: Dato central del beat 2, pero no aparece en el archivo.
- Q53 [voz_lo_dice]: La voz dice «la montaña que camina» en ch02 [10].
- T16 [otro]: El nombre del muerto no entra en la oración de la ola, y la oración de la muerte (caben 15) es demasiado corta; ponerlo antes adelantaría «Un trabajador murió».
- T18 [voz_lo_dice]: La voz cuenta la denuncia de Merlin en L'Unità en 1959.
- T36 [voz_lo_dice]: La voz dice los 700.000 m³ y la fecha del 4 de noviembre.
- D243 [otro]: Cifra alternativa (800.000 m³) del mismo derrumbe del 4 de noviembre; el beat 6 usa T39.
- D102 [repetido]: Mismo hecho que T39.
- D106 [voz_lo_dice]: La voz dice la cota de 715 y la recomendación de 700.
- T50 [otro]: Los 720 m contradicen la cota de 715 que dice la voz y otras fuentes del archivo.
- D68 [voz_lo_dice]: La voz dice «más de un centímetro y medio por día» en noviembre de 1962 (ch04 [14]); es el mismo hecho dicho en palabras. — **falso: la voz no dice ['1,5']**
- D226 [voz_lo_dice]: La voz dice «desde el dos de octubre, los avisos se multiplicaron».
- Q50 [otro]: Solo cabe una ficha por beat y se eligió el dato con cifra.
- T61 [voz_lo_dice]: La voz cuenta la carta de Biadene a Pancini.
- Q43 [otro]: La fecha de la cita es desconocida y no se puede anclar a esa noche.
- T57 [voz_lo_dice]: La voz cuenta la caída del Toc al embalse.
- D01 [repetido]: Mismo hecho que D121 (270 millones de m³).
- T72 [spoiler]: Habría dado la hora 22:43 para la tarjeta, pero esa hora no coincide con la voz y adelanta ch06; la tarjeta queda en null.
- D86 [spoiler]: Altura del muro de agua en Longarone: adelantaría ch06.
- Q25 [voz_lo_dice]: La voz cita la frase en ch06 [23].
- D17 [otro]: Solo cabe una ficha por beat 11 y se eligió D228.
- D192 [otro]: Solo cabe una ficha por beat 11 y se eligió D228.
- Q13 [voz_lo_dice]: La voz dice «Presidente, queremos justicia».
- D240 [repetido]: Mismo hecho que D117.
- T102 [voz_lo_dice]: La voz dice que la Casación reconoció la culpabilidad de Biadene y Sensidoni.
- D32 [otro]: Solo cabe una ficha por beat 13 y se eligió D245, que tiene cifra.
````

#### Tabla real de A.1: cada ficha del papel con su año y el momento del relato (`f37/c/tabla_anio_relato.md`)
| cap · beat | ficha | oración | año del ítem | momento del relato | juicio del autor |
|---|---|---|---|---|---|
| ch01 b1 | D131 «SALTO DEL AGUA · Más de 260 metros» | [1] | — | — | — |
| ch02 b2 | D117 «ACTA DEL CONSEJO SUPERIOR · Solo 13 de 34 representantes presentes» | [2] | — | 1943 | — |
| ch02 b3 | D47 «FRENTE DEL DESMORONAMIENTO · 2 km de frente y 600 m de desarrollo vertical» | [11] | 1950 | 1943 | {'spoiler': ['2']} |
| ch03 b4 | T15 «ROCA CAÍDA AL LAGO · 3 millones de metros cúbicos» | [1] | 1959 | 1959 | {'spoiler': ['3']} |
| ch03 b5 | D49 «ANCHO DE LA FISURA · Más de 1 metro de ancho» | [17] | 1960 | 1960 | — |
| ch04 b6 | T39 «DERRUMBE QUE ADVERTÍA MERLIN · 50 millones de metros cúbicos de roca» | [6] | 1961 | 1961 | {'spoiler': ['50']} |
| ch04 b7 | D105 «CREACIÓN DE ENEL POR LEY · diciembre de 1962» | [15] | 1962 | 1963 | {'no_dicho': ['1962']} |
| ch05 b8 | D161 «LADERA CON EL AGUA A 710 M · 2 cm por día» | [0] | — | 1963 | {'spoiler': ['2']} |
| ch06 b10 | D121 «ROCA QUE CAYÓ · 270 millones de metros cúbicos de roca» | [3] | 1963 | 1963 | — |
| ch06 b11 | D228 «PREPARATIVOS EN BELLUNO · 1000 camas para refugiados» | [25] | — | 1963 | — |
| ch07 b12 | T85 «REMISIÓN A JUICIO · contra 11 personas» | [11] | 1968 | 1968 | — |
| ch07 b13 | D245 «MONTEDISON A LONGARONE · 55.645.758.500 liras» | [18] | 1997 | 1971 | — |

Costos: 0.7649 · por intento: [{'tokens_in': 65940, 'tokens_out': 29803, 'usd': 0.42991, 'segundos': 201.0}, {'tokens_in': 66978, 'tokens_out': 20103, 'usd': 0.33499, 'segundos': 136.3}] · tope: {'usd': 1.0, 'de': 'respaldo (el perfil no trae costos.m01e_tope_usd)'} · seg/palabra: {'valor': 0.3459, 'oraciones': 200, 'caps': 9, 'voz': 'N9Z5MLTIaHFLflaLtbDi', 'origen': 'mediana de 200 oraciones de 9 caps del narrador N9Z5MLTIaHFLflaLtbDi'}

### C.2 `fase2b f8s3-vajont-f30 --plan-only` (`f37/c/plan_only.log`, guion `f37/c/GUION_PANTALLA.*`)
RAM 16.1 GB, Firefox 0. 163 s (la final, la cuarta). **Claude US$ 0** (el papel sale de disco); Gemini (crítico por
intento) US$ 0.0019, 0.0002, 0 y 0.0001 en las cuatro corridas.
**Arreglo que la corrida encontró (commit C):** la primera `--plan-only` dejó D47 y D105 sin colocar: el intento 3 probaba
solo el inicio de la oración siguiente (0.1 s antes de un corte) y no el inicio de la escena que arranca dentro de ella,
que el `despues_del_corte` viejo (F32 §B.3) sí probaba: regresión mía de B. Se agregó a la escalera (sin números) con su
test (`test_b1_d47_…`). También: la anotación «movido» listaba fallas de intentos posteriores al elegido (T15 «7.44 →
7.44»); ahora solo las anteriores. El reloj sin recortar en el reparto lo encontró el simulador (ver C.3, adenda). Logs de las corridas previas:
`plan_only_1_antes_del_arreglo.log`, `plan_only_2.log`, `plan_only_3_antes_del_reloj.log` (guion
`GUION_PANTALLA_3_antes_del_reloj.json`).

#### Lo que queda en pantalla (t_mp4) y los chequeos (`f37/c/resumen_guion.txt`, entero)
```
| cap | t_mp4 | qué | id | texto | dur | filtro / movido |
|---|---|---|---|---|---|---|
| ch01 | 0.0 | tarjeta fecha-hora |  | ⚠ falta fecha-hora | 3.0 | ⚠ falta fecha-hora: el guion en papel no trae tarjeta (agregar con --plan-edit; nunca se inventa) |
| ch01 | 15.22 | ficha | D131 | SALTO DEL AGUA · Más de 260 metros | 2.5 | pasó (crítico ¿estorba?: no estorba) |
| ch01 | 26.64 | sello |  | PÁNICO | 2.5 | pasó (crítico: no estorba) |
| ch01 | 76.04 | reloj |  | 9 OCT · 1963 | 8.32 | pasó |
| ch02 | 123.3 | recorte | D117 | ACTA DEL CONSEJO SUPERIOR · Solo 13 de 34 representantes presentes | 4.2 | pasó (crítico ¿estorba?: no estorba) · movido: 21.24 → 19.20 s (1 · inicio de la oración): 1 · palabra ancla (21.24 s): sin tiempo de lectura: 63 caracteres piden 4.2 s y hay 3.4 s hasta el corte de escena (24.6 s) |
| ch02 | 183.667 | punch |  | zoom_punch 12 cuadros | None | pasó |
| ch02 | 190.7 | ficha | D47 | FRENTE DEL DESMORONAMIENTO · 2 km de frente y 600 m de desarrollo vertical | 4.73 | pasó (crítico ¿estorba?: no estorba) · movido: 84.70 → 86.60 s (3 · oración siguiente [12], inicio de la escena 9): 1 · palabra ancla (84.70 s): sin tiempo de lectura: 71 caracteres piden 4.7 s y hay 1.9 s hasta el corte de escena (86.6 s) · 1 · inicio de la oración (79.50 s): sin tiempo de lectura: 71 caracteres piden 4.7 s y hay 0.1 s hasta el corte de escena (79.6 s) · 3 · oración siguiente [12] (86.52 s): sin tiempo de lectura: 71 caracteres piden 4.7 s y hay 0.1 s hasta el corte de escena (86.6 s) |
| ch02 | 224.88 | sello |  | AMENAZA | 2.5 | pasó (crítico: no estorba) |
| ch03 | 250.733 | punch |  | zoom_punch 12 cuadros | None | pasó |
| ch03 | 252.14 | ficha | T15 | ROCA CAÍDA AL LAGO · 3 millones de metros cúbicos | 3.07 | pasó (crítico ¿estorba?: no estorba) |
| ch03 | 350.54 | ficha | D49 | ANCHO DE LA FISURA · Más de 1 metro de ancho | 2.73 | pasó (crítico ¿estorba?: no estorba) · movido: 113.10 → 105.84 s (1 · palabra de más peso): 1 · palabra ancla (113.10 s): sin tiempo de lectura: 41 caracteres piden 2.7 s y hay 2.6 s hasta el corte de escena (115.7 s) |
| ch04 | 383.06 | reloj |  | 4 NOV · 1960 | 7.54 | pasó |
| ch04 | 423.52 | ficha | T39 | DERRUMBE QUE ADVERTÍA MERLIN · 50 millones de metros cúbicos de roca | 4.33 | pasó (crítico ¿estorba?: no estorba) |
| ch04 | 458.267 | punch |  | zoom_punch 12 cuadros | None | pasó |
| ch04 | 486.267 | ficha | D105 | CREACIÓN DE ENEL POR LEY · diciembre de 1962 | 2.73 | pasó (crítico ¿estorba?: no estorba) · movido: 104.80 → 106.27 s (3 · oración siguiente [16], inicio de la escena 10): 1 · palabra ancla (104.80 s): sin tiempo de lectura: 41 caracteres piden 2.7 s y hay 1.5 s hasta el corte de escena (106.3 s) · 1 · inicio de la oración (95.32 s): sin tiempo de lectura: 41 caracteres piden 2.7 s y hay 0.1 s hasta el corte de escena (95.4 s) · 3 · oración siguiente [16] (106.16 s): sin tiempo de lectura: 41 caracteres piden 2.7 s y hay 0.1 s hasta el corte de escena (106.3 s) |
| ch05 | 512.047 | ficha | D161 | LADERA CON EL AGUA A 710 M · 2 cm por día | 2.53 | pasó (crítico ¿estorba?: no estorba) · movido: 10.26 → 3.08 s (1 · inicio de la oración): 1 · palabra ancla (10.26 s): sin tiempo de lectura: 38 caracteres piden 2.5 s y hay 2.0 s hasta el corte de escena (12.3 s) |
| ch05 | 527.134 | punch |  | zoom_punch 12 cuadros | None | pasó |
| ch05 | 672.707 | sello |  | INMINENTE | 2.5 | pasó (crítico: no estorba) |
| ch06 | 707.5 | punch |  | zoom_punch 12 cuadros | None | pasó |
| ch06 | 710.087 | ficha | D121 | ROCA QUE CAYÓ · 270 millones de metros cúbicos de roca | 3.4 | pasó (crítico ¿estorba?: no estorba) · movido: 26.42 → 25.42 s (1 · palabra de más peso): 1 · palabra ancla (26.42 s): sin tiempo de lectura: 51 caracteres piden 3.4 s y hay 2.7 s hasta el corte de escena (29.1 s) |
| ch06 | 713.907 | sello |  | COLAPSO | 2.5 | pasó (crítico: no estorba) |
| ch06 | 816.706 | ficha | D228 | PREPARATIVOS EN BELLUNO · 1000 camas para refugiados | 3.27 | pasó (crítico ¿estorba?: no estorba) · movido: 136.24 → 132.04 s (1 · inicio de la oración): 1 · palabra ancla (136.24 s): sin tiempo de lectura: 49 caracteres piden 3.3 s y hay 1.3 s hasta el corte de escena (137.6 s) |
| ch07 | 877.067 | punch |  | zoom_punch 12 cuadros | None | pasó |
| ch07 | 943.567 | reloj |  | 20 FEB · 1968 | 9.03 | pasó |
| ch07 | 952.867 | ficha | T85 | REMISIÓN A JUICIO · contra 11 personas | 2.5 | pasó (crítico ¿estorba?: no estorba) · movido: 91.26 → 94.00 s (3 · oración siguiente [12]) |
| ch07 | 986.967 | ficha | D245 | MONTEDISON A LONGARONE · 55.645.758.500 liras | 2.8 | pasó (crítico ¿estorba?: no estorba) |
| ch07 | 1007.787 | sello |  | MEMORIA | 2.5 | pasó (crítico: no estorba) |

Totales: {'tarjeta fecha-hora': 1, 'title card': 7, 'ficha': 11, 'sello': 5, 'reloj': 3, 'pregunta de cierre': 7, 'recorte': 1, 'punch': 6}
✓ dos bloques al mismo tiempo
✓ bloque que cruza un corte
✓ texto sin lectura
✓ pregunta de cierre sin lectura
✓ cifra que contradice la voz
✗ a_pantalla
   ✗ 2/5 en pantalla
   ✗ ch05 Q50: el rotulista no lo propuso
   ✗ ch06 D128: el rotulista no lo propuso
   ✗ ch06 D192: el rotulista no lo propuso
✓ costuras con cuadro no negro
✗ inicio de voz por cap
   ✓ ch01 · voz esperada 2.62 s · medida 2.62 s · llega a −18 dB en 2.65 s con rampa (100 ms previos: -26.0 dB)
   ✓ ch02 · voz esperada 107.18 s · medida 107.18 s · llega a −18 dB en 107.18 s con rampa (100 ms previos: -28.1 dB)
   ✓ ch03 · voz esperada 247.78 s · medida 247.78 s · llega a −18 dB en 247.78 s con rampa (100 ms previos: -28.4 dB)
   ✓ ch04 · voz esperada 383.06 s · medida 383.06 s · llega a −18 dB en 383.56 s con rampa (100 ms previos: -21.6 dB)
   ✓ ch05 · voz esperada 512.05 s · medida 512.05 s · llega a −18 dB en 512.07 s con rampa (100 ms previos: -24.5 dB)
   ✓ ch06 · voz esperada 687.81 s · medida 687.81 s · llega a −18 dB en 687.83 s con rampa (100 ms previos: -29.5 dB)
   ✗ ch07 · voz esperada 861.95 s · medida 861.95 s · llega a −18 dB en 861.94 s sin rampa (100 ms previos: -32.6 dB, bajo la voz presente -30.5 dB)
✓ gancho no vacío
✓ inicio de música por cap
✗ tarjeta fecha-hora
   ✗ 00:00.0 «⚠ falta fecha-hora» ·  · ⚠ falta fecha-hora: el guion en papel no trae tarjeta (agregar con --plan-edit; nunca se inventa)
✗ papel sin colocar
   ✗ ch02 sello CALMA: sello del papel «CALMA»: no entra en ningún intento: 1 · palabra de más peso (58.18 s) · lado right: estorba — El sello grande a media altura a la derecha tapa rostros de las personas sentadas en la cafetería y elementos clave de la escena, como la Vespa. · 1 · palabra de más peso (58.18 s) · lado left: estorba — El sello tapa parte de la actividad del mercado y rostros de personas a la izquierda de la imagen. · 1 · inicio de la oración (56.14 s): cruza el corte de la escena 5 (56.17 s) · 3 · oración siguiente [7] (61.08 s) · lado right: estorba — El sello 'CALMA' se superpone a personas sentadas en la terraza y parte de los edificios, obstruyendo la vista de la escena. · 3 · oración siguiente [7] (61.08 s) · lado left: estorba — El sello es grande y se ubica a media altura en el lado izquierdo, tapando detalles de los puestos del mercado y algunas personas.
   ✗ ch05 sello SILENCIO: sello del papel «SILENCIO»: no entra en ningún intento: 1 · palabra de más peso (71.94 s): cruza el corte de la escena 7 (74.13 s) · 1 · inicio de la oración (71.66 s): cruza el corte de la escena 7 (74.13 s) · 3 · oración siguiente [11] (74.14 s) · lado left: estorba — El bloque se superpone al cartel "STRADA CHIUSA" que ya está en la imagen. · 3 · oración siguiente [11] (74.14 s) · lado right: estorba — El bloque, al estar 'a media altura, a la derecha', taparía los rostros o cuerpos de los hombres que están mirando hacia arriba, elementos clave de la composici
   ✗ ch07 sello RABIA: sello del papel «RABIA»: no entra en ningún intento: 1 · palabra de más peso (10.90 s) · lado right: estorba — El sello "RABIA" a media altura a la derecha probablemente tapa rostros de los pobladores que gritan. · 1 · palabra de más peso (10.90 s) · lado left: estorba — El sello 'RABIA' se superpone a los rostros y cuerpos de los pobladores que gritan, elementos clave de la imagen. · 1 · inicio de la oración (7.92 s) · lado right: estorba — El sello a la derecha a media altura taparía los rostros de los pobladores gritando. · 1 · inicio de la oración (7.92 s) · lado left: estorba — El sello se ubica a media altura a la izquierda, donde hay rostros de los pobladores que serían tapados. · 3 · oración siguiente [2] (18.28 s) · lado left: estorba — El sello 'RABIA' tapa parte del titular 'TRAGEDIA NATURALE' del periódico, que es central para la narración de las 'dos verdades'. · 3 · oración siguiente [2] (18.28 s) · lado right: estorba — El sello se ubica a la derecha, a media altura, y podría tapar parte del titular "ERRORE UMANO" o el texto del periódico.
✓ papel sin alinear
✓ relojes del papel (informativo)
```

### C.3 Simulador contra `REVISION_PAPEL.md` (íntegro en `f37/c/comparacion_simulador.md`)
#### Comparación en seco: F37 (Vajont) contra `lab/hyperframes/f36/REVISION_PAPEL.md`

Solo lectura. No se corrió el pipeline ni ningún modelo. Fuentes: `f37/c/01e_pantalla.md/.json/.raw.json`, `f37/c/GUION_PANTALLA.json/.md`, `f37/c/resumen_guion.txt`, `f37/HANDOFF_F37_papel_y_colocar.md` §C.3, y para «antes» `f36/c/01e_pantalla.md` y `f36/d/GUION_PANTALLA.json`. Código leído solo para entender un solape: `script_engine/pantalla_colocar.py`.

Convenciones: `t_mp4` es el segundo del mp4 final. F37 tiene `intro_s` 2.5 (sin tarjeta) y F36 3.0, así que el mismo instante del cap cae 0.5 s antes en F37. «Papel» = lo que eligió el autor (m01e-2, 2 intentos, USD 0.7649). «Pantalla» = lo que dejó Fase 2.

#### Lo primero que hay que saber

1. De las 7 expectativas de §C.3: 5 cumplen (gancho en las primeras oraciones, T39 de vuelta, D47 y D105 juzgados por el autor, ninguna ficha > 6 s; el «ningún pico vacío» cumple en el papel pero no en pantalla), 1 cumple el efecto pero no el mecanismo (Q43 cayó porque el autor lo descartó viendo `fecha: desconocida`, no por la validación 1c, que nunca disparó) y 1 cumple a medias (los 8 cortes de F36: 1 colocado por mover, 2 colocados porque el papel los cambió de sitio, 3 sin colocar con lista de intentos, 2 que el papel ya no propone).
2. **Hay un pico sin ficha en pantalla: ch07 b12.** El autor reemplazó Q14 (la ironía de Leone, «muy bueno» en el contrato) por T85, y T85 no entró en Fase 2 porque el reloj `20 FEB 1968` ocupaba ese tramo. En F36 ese beat tenía Q14. Es una regresión respecto de F36 en ese beat.
3. El gancho quedó anclado en [1] (15.22 s en vez de 86.24 s) pero con el mismo dato de F36 (D131), que además **adelanta unos 70 s el giro de ch01 [14]-[15]** («vino por encima de él»). El filtro de spoiler no lo ve porque compara cifras.
4. El reintento **reescribió el papel entero** (no solo lo preguntado) y perdió cosas sin descarte registrado: D128 (1.910 muertos, estaba en el intento 1), Q14, el sello AVISO, el sello ALARMA, la tarjeta fecha-hora.
5. La tarjeta fecha-hora quedó en `null`: en pantalla hay un marcador «⚠ falta fecha-hora» de 3.0 s en el segundo 0 y el chequeo «tarjeta fecha-hora» pasó de ✓ a ✗.

---

#### 1. Tabla línea por línea de «Cap por cap (DEBERÍA)»

Columnas: cap·beat · DEBERÍA (resumido) · F37 papel · F37 en pantalla (t_mp4, texto, dur) · ¿salió solo por las reglas generales? · por qué.

| # | cap · beat | DEBERÍA | F37 papel | F37 en pantalla | ¿Salió solo? | Por qué |
|---|---|---|---|---|---|---|
| 1 | ch01 b1 gancho | A: D118 «LA PRESA DEL VAJONT · 266 m» en [1]. B: D195 «LONGARONE · 1.269 de 1.328» en [2]. Nada en [15] (1:26) | D131 «SALTO DEL AGUA · Más de 260 metros» en [1] sobre «presa» | 15.22 s · «SALTO DEL AGUA · Más de 260 metros» · 2.5 s (el mínimo) | **En parte** (el ancla sí; el dato es gusto) | El ancla en [1] salió con el prompt m01e-2, pero **solo en el intento 2**: el intento 1, con el mismo prompt, dejó D131 en [15]. El reintento no pedía mover el gancho (sus 6 motivos son otros), así que no hay regla que lo garantice; fue el modelo. El dato no es ni A ni B: es el mismo D131 de F36. Dos problemas: (a) las fuentes no coinciden en la altura (D123 250, D215 200, D44 260), sigue sin resolverse; (b) en [1] la voz dice «la presa… sigue en pie» y recién en [15] «vino por encima de él», unos 70 s después (en F36 la ficha caía a 86.24 s, 85.7 s en el reloj de F37). La ficha dice «SALTO DEL AGUA» 70 s antes que la voz. El `aporta` del modelo afirma que «la voz dice que la ola pasó por encima», lo cual es falso en [1]. Compuerta de Omar. |
| 2 | ch01 sello | PÁNICO [4] | PÁNICO [4] | 26.64 s · PÁNICO · 2.5 s | Sí | Sin cambios respecto de F36 (27.14 s con el reloj de entonces). |
| 3 | ch02 b2 | D117 «SESIÓN DEL CONSEJO SUPERIOR · 13 de 34» se queda; F37: mover, no cortar | D117 [papel] «ACTA DEL CONSEJO SUPERIOR · Solo 13 de 34 representantes presentes» en [2] sobre «aprobó» | 123.3 s · «ACTA DEL CONSEJO SUPERIOR · Solo 13 de 34 representantes presentes» · 4.2 s · movido 21.24 → 19.20 s | **Sí** | Caso de manual de B.1: F36 lo cortó por el crítico («tapa el documento»); F37 probó otro instante de la misma oración («1 · inicio de la oración»), el crítico lo dejó pasar y entró. Cambia «SESIÓN» por «ACTA» y suma «Solo»; el `aporta` incluye «procedimiento irregular», que está en D117. |
| 4 | ch02 b2 sello | CALMA [6], cortado (rostros); F37: mover de posición | CALMA [6] (igual) | **Sin colocar.** 5 intentos | **No** (con su lista de intentos, como pedía el handoff) | Palabra de más peso 58.18 s (crítico: estorba en los dos lados; derecha por rostros y Vespa, izquierda por el mercado); inicio de la oración 56.14 s (cruza el corte de la escena 5 a 56.17 s); oración siguiente [7] 61.08 s (crítico: estorba en los dos lados). La escalera funcionó como estaba escrita; el que no deja es el crítico. |
| 5 | ch02 b3 PICO | D47 «DESMORONAMIENTO DEL TOC · 2 km de frente y 600 m» en [11] | D47 «FRENTE DEL DESMORONAMIENTO · 2 km de frente y 600 m de desarrollo vertical» en [11] sobre «desmoronamiento» | 190.7 s · «FRENTE DEL DESMORONAMIENTO · 2 km de frente y 600 m de desarrollo vertical» · 4.73 s · movido 84.70 → 86.60 s a [12] (inicio de la escena 9) | **Sí** | A.4: el código encontró el «2» en ch03 [17] («casi dos kilómetros de largo»), se lo preguntó al autor y este contestó «otro hecho» (queda escrito: «Los 2 km de la fisura de ch03 son otro hecho»). Fase 2 respetó el juicio. Después B.1 lo corrió a la oración siguiente porque la palabra ancla no tenía tiempo de lectura antes del corte. Cae una oración después de la que pedía el contrato; el contrato permitía mover. |
| 6 | ch02 b3 sello | AMENAZA [10] | AMENAZA [16] | 224.88 s · AMENAZA · 2.5 s | Sí (el papel lo corrió de [10] a [16]) | El contrato lo daba por bueno sin tocar. El autor lo pone en [16] ya en el intento 1, seguramente porque ahora hay ficha en [11]. En F36 caía a 176.34 s; ahora a 224.88 s. Neutro. |
| 7 | ch03 b4 PICO | T16 «LA VÍCTIMA DE PONTESEI · Arcangelo Tiziani» [3] se queda; duración ≤ 6 s | **T16 descartado** [otro]: «el nombre no entra en la oración de la ola… ponerlo antes adelantaría “Un trabajador murió”». En su lugar T15 «ROCA CAÍDA AL LAGO · 3 millones de metros cúbicos» en [1] | 252.14 s · «ROCA CAÍDA AL LAGO · 3 millones de metros cúbicos» · 3.07 s | **No en contenido; sí en duración** | La duración se arregló (la ficha más larga de F37 es 4.73 s; T16 había durado 12.74 s). Pero el contenido cambió: T15 es el dato que el modelo de F36 había descartado como «no suma frente al nombre de la víctima». El contrato dijo que el nombre humaniza. Gusto: Omar decide. T15 también pasó por pregunta de A.4 («3» vs «tres o cuatro minutos» de ch06 [6]) y el autor dijo «otro hecho». |
| 8 | ch03 b5 | D49 «ANCHO DE LA FISURA · Más de 1 metro» [17] | D49 «ANCHO DE LA FISURA · Más de 1 metro de ancho» [17] | 350.54 s · «ANCHO DE LA FISURA · Más de 1 metro de ancho» · 2.73 s · movido 113.10 → 105.84 s | Sí | Se movió a «1 · palabra de más peso» porque la palabra ancla no tenía 2.7 s antes del corte (le faltaban 0.1 s). Texto redundante («ANCHO … de ancho»); detalle de estilo. |
| 9 | ch03 b5 sello | INMINENTE [18], cortado (tapa la fisura); F37: mover de posición | **Ya no está en ch03.** INMINENTE pasó a ch05 b9 [26] | 672.707 s (ch05) · INMINENTE · 2.5 s | **No** (lo resolvió el papel, no la colocación) | El autor lo mudó de cap, al beat vacío ch05 b9 (la noche del párroco). Colocó sin moverse. ch03 b5 quedó sin sello; el crítico nunca volvió a juzgar la fisura. |
| 10 | ch04 b6 | T39 «ROCA QUE AMENAZA ERTO · 50 millones de m³» en [6] | T39 «DERRUMBE QUE ADVERTÍA MERLIN · 50 millones de metros cúbicos de roca» en [6] sobre «advertencia» | 423.52 s · «DERRUMBE QUE ADVERTÍA MERLIN · 50 millones de metros cúbicos de roca» · 4.33 s | **En parte** | Resultado: está. Mecanismo: A.2 (verificar «la voz ya lo dice») **no se ejercitó con T39**: el modelo ya lo había elegido en el intento 1. Tuvo pregunta de A.4 («50» vs «aumento del 50%» de ch05 [17]) y el autor contestó «otro hecho». El caso que sí ejercitó A.2 fue D68 (ver 2.2). |
| 11 | ch04 b7 PICO | D105 «ENEL · creado por ley en diciembre de 1962» en [16] | D105 «CREACIÓN DE ENEL POR LEY · diciembre de 1962» en [15] sobre «ENEL» | 486.267 s · «CREACIÓN DE ENEL POR LEY · diciembre de 1962» · 2.73 s · movido 104.80 → 106.27 s a [16] (inicio de la escena 10) | **Sí** | A.4: «1962» vs ch04 [14] («noviembre de mil novecientos sesenta y dos»); el autor dijo «otro hecho» y Fase 2 lo respetó. B.1 lo movió a la oración [16], justo la que el contrato pedía. |
| 12 | ch04 b7 sello | AVISO [14], cortado (cruza el corte); F37: mover antes del corte | **Sin AVISO.** En el intento 1 estaba en ch03 b4 [9]; el intento 2 lo sacó | No está | **No** (se perdió en el papel) | No figura en «sin colocar» ni en «Lo que cayó» ni hay motivo escrito: los sellos no tienen lista de descartes. El pico ch04 b7 queda sin sello (la ficha D105 sí está). Se pierde un sello que el contrato valoraba, sin que nadie lo diga. |
| 13 | ch05 b8 PICO | Q50 «CARTA DEL MUNICIPIO DE ERTO · “en continua aprensión y en continua alarma”» (~70 car.) en [7] | **Q50 descartado** [otro]: «solo cabe una ficha por beat y se eligió el dato con cifra». Ficha D161 «LADERA CON EL AGUA A 710 M · 2 cm por día» en [0] sobre «centímetro» | 512.047 s · «LADERA CON EL AGUA A 710 M · 2 cm por día» · 2.53 s · movido 10.26 → 3.08 s (inicio de la oración) | **No** (gusto) | El pico tiene ficha, pero no la que pedía el contrato. Q50 no entra al papel, así que no se probó nada de lo nuevo para citas (ver observaciones). D161 es un dato nuevo (el contrato no lo mencionaba): pasó por pregunta de A.4 (el «2» era «el dos de octubre» de ch05 [2]) y el autor contestó bien. Cae a 3.08 s del cap, en el primer segundo de voz del capítulo. |
| 14 | ch05 b8 sello | SILENCIO [10] «De la ola no hablaba nadie», cortado (corte); F37: mover antes del corte | SILENCIO [10] (igual) | **Sin colocar.** 4 intentos | **No** (con su lista) | Palabra de más peso 71.94 s: cruza el corte de la escena 7 (74.13 s). Inicio de la oración 71.66 s: cruza el mismo corte (aritmética mía: 71.66 + 2.5 = 74.16 s, es decir **pasa por 0.03 s**). Oración siguiente [11] 74.14 s: el crítico dice que estorba en los dos lados (cartel «STRADA CHIUSA»; los hombres mirando hacia arriba). No hay paso 2 porque el corte cae justo al borde de la oración. |
| 15 | ch05 b9 | Q43 «INGENIERO JEFE · “Son sacudidas menores…”» en [15]; Omar decide (la fuente no da fecha) | Q43 descartado [otro]: «la fecha de la cita es desconocida y no se puede anclar a esa noche». Sin ficha | b9 solo tiene el sello INMINENTE (672.707 s) | **Sí en el efecto; no por 1c** | Ver 2.4. El archivo que ve el autor ahora trae `fecha: "desconocida"` (A.1a) y el modelo lo usó. La validación 1c (cita sin fecha sin autor en la voz) no se ejercitó: «fichas fuera 0» en los dos intentos. b9 sigue sin ficha: el contrato dice que eso lo decide Omar. |
| 16 | ch06 b10 PICO | D01 «ROCA DESPRENDIDA · 270 millones de m³ de roca» [3] | D121 «ROCA QUE CAYÓ · 270 millones de metros cúbicos de roca» en [3] sobre «desploma» | 710.087 s · «ROCA QUE CAYÓ · 270 millones de metros cúbicos de roca» · 3.4 s · movido 26.42 → 25.42 s | Sí | Mismo hecho que D01 (el autor lo declara «repetido»: D01 → D121). La duración bajó de 5.44 s a 3.4 s. |
| 17 | ch06 b10 | **+ D195 «LONGARONE · 1.269 de 1.328 habitantes»** en [20] («Longarone ya no.») | D195 ni elegido ni descartado: no aparece en ninguno de los dos intentos | Nada en [20] | **No** (gusto) | Opción de gusto del contrato (el golpe del video). El modelo ni lo mencionó, ni con motivo. Compuerta de Omar. |
| 18 | ch06 b10 sello | COLAPSO [20], cortado (corte); con D195, pasa a [19] o se mueve | COLAPSO en [3] (en el intento 1 estaba en [5]; en F36 en [20]) | 713.907 s · COLAPSO · 2.5 s | **En parte** (colocado, pero lo resolvió el papel) | El autor lo llevó al desprendimiento («se desploma»), junto a la ficha D121 y al punch, 3.8 s después de la ficha. Pasó sin moverse; la escalera de B.1 no se ejercitó con este sello. El momento de «Longarone ya no.» ([20]) quedó sin sello ni ficha. |
| 19 | ch06 b11 | **D128 «MUERTOS, RECUENTO OFICIAL · 1.910 personas»** en [24]; D17 fuera | D128 **no está** (sí estaba en el intento 1, en [24]). D17 y D192 descartados «solo cabe una ficha por beat». Ficha D228 «PREPARATIVOS EN BELLUNO · 1000 camas para refugiados» en [25] | 816.706 s · «PREPARATIVOS EN BELLUNO · 1000 camas para refugiados» · 3.27 s · movido 136.24 → 132.04 s | **No** (gusto, con una falla) | D17 ya no está (bien, según el contrato), pero tampoco D128. Y D128 **desapareció en el reintento sin motivo ni descarte**: es la misma falla que el revisor marcó en F36 («D128 omitido sin motivo»). D228 es un dato nuevo y fuerte (las camas para sobrevivientes que no había). Compuerta de Omar: D128 vs D228. |
| 20 | ch06 b11 sello | RABIA [31], cortado (rostro); F37: mover de posición | RABIA pasó a ch07 b12 [1] (el grito «Presidente, queremos justicia») | **Sin colocar.** 6 intentos | **No** (con su lista) | Peso 10.90 s derecha e izquierda, inicio 7.92 s derecha e izquierda, oración siguiente [2] 18.28 s izquierda y derecha: el crítico dice «estorba» en los seis (rostros de pobladores gritando; titular del diario). ch06 b11 quedó sin sello y la nueva ubicación del autor tampoco entra. |
| 21 | ch07 b12 PICO | Q14 «RESPUESTA DE GIOVANNI LEONE · “Y justicia tendréis”» [1] se queda; **T85 fuera** (un texto por beat; el reloj 20 FEB 1968 ya marca la fecha) | **Q14 descartado** en el intento 1 («una ficha por beat, se eligió T85, que tiene cifra») y ausente del intento 2. T85 «REMISIÓN A JUICIO · contra 11 personas» en [11] sobre «resolución» | **Nada.** T85 «sin colocar». En pantalla solo el punch (877.067 s) y el reloj 20 FEB · 1968 (943.567 s, 9.03 s) | **No. Regresión respecto de F36** | F36 tenía Q14 en pantalla (877.567 s, 5.26 s). F37 invierte lo que pedía el contrato. T85 cayó en Fase 2 con 3 intentos, todos «se solapa con reloj»: palabra ancla 91.26 s, inicio de la oración 84.70 s, oración siguiente [12] 94.00 s. Dato raro: el reloj termina a 93.73 s en pantalla y el tercer intento empezaba a 94.00 s. Por el código (`pantalla_colocar.py`, líneas 328-359) el reloj se coloca **antes** que las fichas con su intervalo sin recortar (`hasta_el_corte` lo corta después), así que seguramente el filtro lo ve más largo de lo que se ve. No lo verifiqué corriendo nada. Es un hueco de la regla de colocación: el reloj le gana a una ficha de pico. |
| 22 | ch07 b13 | D245 «CONDENA A MONTEDISON · 55.645.758.500 liras» [18] | D245 «MONTEDISON A LONGARONE · 55.645.758.500 liras» [18] sobre «indemnización» | 986.967 s · «MONTEDISON A LONGARONE · 55.645.758.500 liras» · 2.8 s | Sí | La duración bajó de 7.38 s a 2.8 s. En el intento 1 el autor había puesto T92; en el 2 volvió a D245 (el contrato lo daba por bueno). |
| 23 | ch07 sello | MEMORIA [22] | MEMORIA [21] | 1007.787 s · MEMORIA · 2.5 s | Sí | Se corrió una oración. En el intento 1 estaba en ch06 b11 [23]. |
| 24 | (opcional) ch06 | D84 «dos bombas de Hiroshima» en [5]; solo si Omar lo quiere | No aparece | — | No (opcional, gusto) | No se forzó, como pedía el handoff. |

---

#### 2. Las 7 expectativas de §C.3

| # | Expectativa | Veredicto | Evidencia |
|---|---|---|---|
| 2.1 | Gancho anclado en las primeras oraciones de ch01 | **Cumple** (con reparos) | D131 en [1] sobre «presa», 15.22 s en el mp4 (F36: [15], 86.24 s). Reparos: se logró solo en el intento 2, sin motivo de reintento que lo pidiera; y el dato adelanta el giro de [14]-[15] (fila 1). |
| 2.2 | T39 de vuelta en ch04 | **Cumple** | T39 en ch04 b6 [6], 423.52 s, 4.33 s. Lo puso el modelo ya en el intento 1; A.2 (verificar «la voz lo dice») no fue lo que lo trajo. A.2 sí actuó con D68: el autor dijo «la voz lo dice», el código buscó «1,5» en la voz, no lo halló y lo devolvió como candidato; el modelo lo volvió a descartar «voz_lo_dice». **El código se equivocó**: la voz de ch04 [14] dice «más de un centímetro y medio por día» (el 1,5 en palabras). El `.md` publica «falso: la voz no dice [1,5]» sobre un descarte que era correcto. Inocuo esta vez, pero la verificación no convierte «centímetro y medio». |
| 2.3 | Ningún pico vacío (o ⚠ explicado) | **Cumple en el papel; no cumple en pantalla** | Papel: los 7 picos (ch01 b1, ch02 b3, ch03 b4, ch04 b7, ch05 b8, ch06 b10, ch07 b12) tienen ficha; el log dice «picos vacíos 0» en los dos intentos. Pantalla: ch07 b12 queda sin ficha porque T85 no entró (fila 21): 6 de 7. La causa figura en «papel sin colocar» (3 intentos, todos solapados con el reloj), pero el `.md` no lo marca como pico vacío. |
| 2.4 | Q43 fuera por 1c | **Cumple el efecto, no el mecanismo** | Q43 está fuera, descartado por el autor con «la fecha de la cita es desconocida y no se puede anclar a esa noche» en ambos intentos. «fichas fuera 0»: la validación 1c nunca rechazó nada. Lo sacó A.1a (el archivo ahora trae `fecha: "desconocida"`, `rol` y `testimonio`) y el criterio del modelo, no el código. Sirve, pero esta corrida no prueba que 1c funcione; solo el test sintético lo hace. |
| 2.5 | D47 y D105 juzgados por el autor | **Cumple** | Preguntas: D47 `{'spoiler': ['2']}`, D105 `{'no_dicho': ['1962']}`, más T15 («3»), T39 («50») y D161 («2»). Las 5 respuestas: «la mantuvo… otro hecho». Las 5 son falsos positivos reales (km de la fisura, «tres o cuatro minutos», 50% de la posdata, «dos de octubre», noviembre vs diciembre de 1962). «Lo que cayó»: nada (F36: 3). Fase 2 respetó los juicios: los cinco están en pantalla (`juicio_autor` en el `.json`). El autor contestó «otro hecho» a las 5; acá acertó, pero no hay ningún caso donde haya dicho «sí es el mismo hecho», así que no sabemos si discrimina. |
| 2.6 | Los 8 cortes de F36 colocados o con su lista | **Cumple a medias** | Ver punto 3. Hay 4 «sin colocar» (CALMA, SILENCIO, RABIA y T85, esta última nueva), los cuatro con su lista de intentos. Pero de los 8 originales solo D117 se resolvió por la escalera. |
| 2.7 | Ninguna ficha > 6 s | **Cumple** | Duraciones en pantalla: 2.5, 4.2, 4.73, 3.07, 2.73, 4.33, 2.73, 2.53, 3.4, 3.27, 2.8 s. Máximo 4.73 s (D47). F36: 12.74 s (T16), 11.24 s (D131), 7.38 s (D245), 5.72 s, 5.44 s. |

---

#### 3. Los 8 «papel sin colocar» de F36 en F37

El papel nuevo movió o borró varios de estos sellos antes de que Fase 2 los viera. Separo qué cambió el papel y qué cambió la colocación.

| F36 (por qué cayó) | Qué hizo el papel F37 | Qué hizo la colocación F37 | Estado final |
|---|---|---|---|
| **CALMA ch02** [6] (crítico: rostros) | Nada: sigue en [6] | Escalera completa, 5 intentos: peso 58.18 s en los dos lados (estorba), inicio 56.14 s (cruza el corte de 56.17 s), siguiente [7] 61.08 s en los dos lados (estorba) | **Sin colocar**, con lista |
| **AVISO ch04** [14] (cruza el corte) | **Lo borró** (en el intento 1 lo había mudado a ch03 [9]; en el 2 desapareció; sin motivo) | No lo vio | **No está** ni en pantalla ni en sin colocar. Pérdida silenciosa |
| **SILENCIO ch05** [10] (cruza el corte) | Nada: sigue en [10] | 4 intentos: peso 71.94 s e inicio 71.66 s cruzan el corte de 74.13 s (el inicio por 0.03 s); siguiente [11] 74.14 s en los dos lados (estorba) | **Sin colocar**, con lista |
| **COLAPSO ch06** [20] (cruza el corte) | Lo mudó a [3] (junto a la ficha D121) | Entró en el primer intento, sin mover | **Colocado** en 713.907 s, 2.5 s. Lo resolvió el papel, no la escalera |
| **INMINENTE ch03** [18] (crítico: tapa la fisura) | Lo mudó a ch05 b9 [26] | Entró en el primer intento | **Colocado** en 672.707 s (ch05), 2.5 s. Lo resolvió el papel; ch03 quedó sin sello |
| **RABIA ch06** [31] (crítico: rostro) | Lo mudó a ch07 b12 [1] | 6 intentos (peso, inicio y siguiente [2], dos lados cada uno): estorba en todos (rostros de pobladores, titular del diario) | **Sin colocar**, con lista. ch06 b11 quedó sin sello |
| **D117 ch02** [2] (crítico: tapa el documento) | Se mantiene (con «ACTA» y «Solo») | Intento 1 (palabra ancla) sin tiempo de lectura; intento 2, «1 · inicio de la oración» 19.20 s, crítico no estorba | **Colocado** en 123.3 s, 4.2 s. **Único que resolvió la escalera de B.1 como se pensó** |
| **Q50 ch05** [2] (lectura: 127 car. piden 8.5 s, hay 3.4 s) | **Lo descartó** («solo cabe una ficha por beat»); puso D161 | No lo vio | **No está.** La regla nueva de citas (B.3: no contar el autor dos veces; mover a la oración siguiente) **no se probó**: el papel F37 tiene 0 citas |

Resumen: 1 colocado por mover (D117) · 2 colocados porque el papel los cambió de sitio (COLAPSO, INMINENTE) · 3 sin colocar con lista (CALMA, SILENCIO, RABIA) · 2 que el papel ya no propone (AVISO, Q50). Más 1 corte nuevo: T85 (ficha, solape con reloj). Además, otras 6 fichas se movieron con la escalera y entraron (D47, D49, D105, D161, D121, D228) y en F36 habrían caído o corrido sin esa escalera: ahí el cambio de colocación sí rindió.

---

#### 4. Para la compuerta de Omar (gusto o decisión de contenido)

Los cambios de papel se hacen con `--plan-edit` sobre `01e_pantalla.json`.

1. **Tarjeta fecha-hora.** El papel la trae en `null`. En pantalla hay un marcador «⚠ falta fecha-hora» de 3.0 s en el segundo 0 (el guion dice «agregar con --plan-edit; nunca se inventa») y el chequeo está en ✗. El intento 1 la traía como «9 OCT 1963 · 22:39» (igual que F36), y la voz dice «Son las diez y treinta y nueve» en ch06 [1] y repite las diez y treinta y nueve en ch07 [25]: 22:39 está respaldada por el guion. El motivo del modelo en el intento 2 (T72, 22:43, «adelanta ch06») habla de otra hora (22:43). Decidir: ponerla (22:39) o aceptar un arranque sin tarjeta (con ella F36 tenía intro 3.0 s; sin ella 2.5 s con el primer cuadro congelado).
2. **Gancho: qué dato.** D131 en [1] (hoy) / D118 «266 m, la más alta del mundo» (opción A del contrato) / D195 «1.269 de 1.328» (opción B). D131 adelanta «el agua saltó» unos 70 s antes de que la voz lo cuente, y sus fuentes se contradicen en la altura.
3. **D195 en el clímax** ([20] «Longarone ya no.»): hoy no hay nada ahí.
4. **ch06 b11:** D128 (1.910 muertos, que el modelo tenía en el intento 1 y perdió sin motivo) vs D228 (1000 camas, hoy) vs D17.
5. **ch07 b12:** Q14 (la ironía de Leone) vs T85 (11 imputados). El contrato dice Q14 y T85 fuera; F37 hace lo contrario y deja el pico vacío en pantalla. Volver a Q14 es una edición del papel.
6. **ch03 b4:** T16 (Arcangelo Tiziani, humaniza) vs T15 (3 millones de m³).
7. **ch05 b8:** Q50 (carta del municipio) vs D161 (2 cm por día a 710 m).
8. **ch05 b9 / Q43 «Omar decide»:** sigue vacío; si se quiere Q43 es una edición a mano (el autor lo rechazó por la fecha).
9. **T85, D84:** los «solo gusto» del handoff. T85 ya está arriba; D84 (dos bombas de Hiroshima, ch06 [5]) no se propuso.
10. **Sellos:** el papel pasó de 9 a 8 (AVISO y ALARMA se perdieron en el reintento) y hay 3 sin colocar (CALMA, SILENCIO, RABIA); SILENCIO falla por 0.03 s en un solo intento. Omar decide si los quiere (editar posición o texto) o los da por perdidos. COLAPSO en [3] y no en [20]; AMENAZA en [16]; INMINENTE en ch05: movimientos del autor, no forzados.
11. **Clave de costos.** El perfil no trae `costos.m01e_tope_usd`; se usó el respaldo 1.00. Si Omar quiere dejarla fija, la agrega él (handoff §Frenos).

---

#### 5. Totales: F37 contra F36 contra «Con las DEBERÍA»

«Papel» = lo que eligió el autor. «Pantalla» = lo que quedó tras Fase 2.

| Concepto | F36 papel | F36 pantalla | F37 papel | F37 pantalla | «Con las DEBERÍA» |
|---|---|---|---|---|---|
| Fichas | 9 (7 normales + 2 citas) | 7 (6 fichas + 1 cita Q14) | 12 | **11** (10 fichas + 1 recorte D117) | 14 (ch01 1 · ch02 2 · ch03 2 · ch04 2 · ch05 2 · ch06 3 · ch07 2) |
| Fichas por cap (ch01..ch07) | 1/1/2/0/1/2/2 | 1/0/2/0/0/2/2 | 1/2/2/2/1/2/2 | 1/2/2/2/1/2/1 | 1/2/2/2/2/3/2 |
| Una cada | | 1056 s / 7 = 151 s | | **96 s** (1055.8 s / 11) | 75 s |
| Picos con ficha en pantalla | | 4 de 7 (ch01, ch03, ch06, ch07) | 7 de 7 | **6 de 7** (falta ch07 b12) | 7 de 7 |
| Fichas de más de 6 s | | 3 (12.74, 11.24, 7.38) | | **0** (máx. 4.73 s) | 0 |
| Fichas movidas por la escalera | | n/a | | 7 (D117, D47, D49, D105, D161, D121, D228) | |
| Sellos | 9 | 3 (PÁNICO, AMENAZA, MEMORIA) | 8 | **5** (PÁNICO, AMENAZA, INMINENTE, COLAPSO, MEMORIA) | 9 (los del papel, recolocados) |
| Sellos sin colocar | | 6 | | 3 (CALMA, SILENCIO, RABIA) | |
| Relojes | 4 en el papel | 4 | 4 en el papel | 4 (9 OCT ch01, 4 NOV ch04, 9 OCT ch05 que viene de la voz, 20 FEB ch07). El 29 NOV 1968 del papel no sale, igual que en F36 («informativo») | no especificado |
| Tarjeta fecha-hora | 1 («9 OCT 1963 · 22:39») | 1 | `null` (motivo T72) | **0** real + marcador «⚠ falta fecha-hora» (3.0 s); chequeo ✗ | no especificado |
| Punches | | 6 | | 6 (ch02 183.667, ch03 250.733, ch04 458.267, ch05 527.134, ch06 707.5, ch07 877.067); el de ch07 queda sin ficha ni cita en su pico | |
| «Papel sin colocar» | | 8 | | 4 (CALMA, SILENCIO, RABIA, T85) | |
| Lo que cayó por filtros | 3 (D47, D105, Q43) | | | 0 | |
| Descartados del modelo | 85 | | 26 | | |
| Intentos · costo · tokens de entrada | 1 · USD 0.3091 · 59 976 | | 2 · USD 0.7649 (0.4299 + 0.3350) · 65 940 + 66 978 | | |
| Chequeos que fallan | | a_pantalla 1/5, inicio de voz ch07, papel sin colocar | | a_pantalla 2/5 (faltan Q50, D128, D192), inicio de voz ch07 (igual que antes), tarjeta fecha-hora, papel sin colocar | |
| Duración total | | 1056.27 s | | 1055.77 s | |

Lectura: las fichas pasan de 7 a 11 en pantalla (contrato: 14), sobre todo por D47, D105, T39, D161 y D228, y porque D117 ahora entra. Faltan tres para llegar a 14: ch05 (Q50 o Q43), ch06 (D195) y ch07 (Q14). Los sellos suben de 3 a 5 (contrato: 9). La tarjeta y el pico de ch07 sin ficha son los dos retrocesos reales.

---

#### 6. Observaciones sobre las reglas (no son gusto)

1. **El reloj le gana a la ficha del pico** (T85, fila 21). La escalera es la de B.1, pero el reloj se coloca primero y posiblemente con un intervalo más largo del que se ve. Es un tema de la regla de colocación, no de contenido.
2. **El reintento reescribe todo.** El segundo intento generó el papel completo otra vez (20 103 tokens de salida); perdió D128, Q14, AVISO, ALARMA y la tarjeta, y cambió T92 por D245, casi sin descartes escritos. El handoff dice que la respuesta del reintento es final para las preguntas, pero nada impide que se pierda lo demás. «Lo que cayó: nada» es cierto solo para los filtros.
3. **La verificación de A.2 no entiende cifras escritas con palabras** («centímetro y medio» no es «1,5»). Produjo una anotación falsa en el `.md` (D68).
4. **El anclaje del gancho depende del modelo**, no de una regla: el prompt m01e-2 solo no bastó en el intento 1.
5. **No se probó nada de lo nuevo para citas** (B.3, mover Q50 a la oración siguiente): el papel F37 no tiene ninguna.
6. **La validación 1c** (cita sin fecha) **no se ejercitó** en esta corrida.
7. **El filtro de spoiler compara cifras y no ve un hecho adelantado** (D131 en [1], «SALTO DEL AGUA»). El autor tampoco lo notó: su `aporta` afirma lo contrario.

Archivo: `C:\CLAUDE_PROJECTS\automatization_videos\lab\hyperframes\f37\c\comparacion_simulador.md`

#### Adenda de CC (después de la comparación; el texto del simulador de arriba queda tal cual)
La comparación se hizo sobre el guion de la tercera `--plan-only`. El simulador señaló (fila 21 y §6.1) que T85 chocaba con
el reloj de ch07 en los tres intentos y dejaba el pico sin ficha. Causa: `repartir` ocupaba el tramo del reloj antes de que
`hasta_el_corte` lo recortara al corte de su escena. Arreglo (regla, no contenido): el reloj se recorta antes del reparto y
otra vez después (`gfx_layer._escena`; test `test_c_el_reparto_ve_el_reloj_recortado_al_corte`). Cuarta `--plan-only`
(la final, `GUION_PANTALLA.*`; diff contra la tercera en `c/diff_reloj.txt`): **T85 entra** en 952.87 s (oración
siguiente [12], 2.5 s) → **12 de 12 fichas en pantalla y 7 de 7 picos con ficha**. Efecto: el reloj de voz de ch05
(9 OCT 1963, sin papel) quedaba 1.88 s tras el corte, menos que `TICKER_MIN` (2 s, F29c): antes salía igual porque el
reparto miraba el tramo sin recortar; ahora queda «sin colocar» (relojes 3, no 4). Cambia también una transición de ch05
(«salto de tiempo» → corte: sin ese reloj no hay salto de fecha en esa escena). Con esto, de las expectativas de §C.3:
2.3 («ningún pico vacío») pasa a **cumple en papel y en pantalla**; 2.6 suma T85 colocado; las demás igual.

### C.4 Totales, costos y tokens
| | F36 pantalla | F37 papel | **F37 pantalla (final)** | «Con las DEBERÍA» |
|---|---|---|---|---|
| fichas | 7 (6 + cita Q14) | 12 | **12** (11 fichas + recorte D117) | 14 |
| fichas por cap ch01..ch07 | 1/0/2/0/0/2/2 | 1/2/2/2/1/2/2 | 1/2/2/2/1/2/2 | 1/2/2/2/2/3/2 |
| una cada | 151 s | | **88 s** (1055.8 s / 12) | 75 s |
| picos con ficha | 4 de 7 | 7 de 7 | **7 de 7** | 7 de 7 |
| fichas > 6 s | 3 (12.74, 11.24, 7.38) | | **0** (máx. 4.73 s) | 0 |
| sellos | 3 | 8 | **5** (PÁNICO, AMENAZA, INMINENTE, COLAPSO, MEMORIA) | 9 |
| sellos sin colocar | 6 | | 3 (CALMA, SILENCIO, RABIA: con su lista) | |
| relojes | 4 | 4 | **3** (ch05 fuera por `TICKER_MIN`) | |
| tarjeta | 1 | 0 (null) | **0** + marcador «⚠ falta fecha-hora» | |
| punches | 6 | | 6 | |
| papel sin colocar | 8 | | 3 | |
| caído en la validación del papel | 3 | 0 | | |
| descartados del modelo | 85 | 26 | | |

Costo: Claude **US$ 0.7649** (intento 1: 65 940 in · 29 803 out · US$ 0.4299 · 201 s; reintento: 66 978 in · 20 103
out · US$ 0.3350 · 136 s; tope 1.00, respaldo). Gemini (crítico por intento, cuatro `--plan-only` de C): US$ 0.0019 +
0.0002 + 0 + 0.0001. Tiempos de `--plan-only`: 273 s, 176 s, 168 s, 163 s.

### Verificación de C
md5 de ch02 sin `--gfx` `38e5ba14e3d24fd20f9297c9e1dfee24` (RAM 16.0 GB, Firefox 0), rápida **58**, amplia **806 + las 5
previas** (`f37/c/`; con los dos arreglos de C y sus tests: `test_b1_d47_…` y `test_c_el_reparto_ve_el_reloj_…`). Mapa
regenerado: **35 módulos, 115 aristas, 0 muertos**. Tests de la tanda: A 9, B+C 10 (`test_module_f37b_colocar.py`).

## Costos de la tanda
Claude (Sonnet 5.5, `m01e_pantalla` de Vajont): **US$ 0.7649** (dos llamadas; `01_v3_costos.json`, paso «pantalla»).
Gemini (crítico por intento, cuatro `--plan-only`): ≈ US$ 0.002. ElevenLabs, imágenes, render: 0.

## Procesos (paso 12)
Cerrados por la tanda: ninguno queda vivo. Los `--plan-only`, los verificadores y las suites corrieron en primer plano o
en segundo plano y terminaron solos (cada uno notificó su fin); los subagentes `simulador` (cuatro) y `revisor-handoff`
terminaron. No se lanzó qa_studio ni HyperFrames (sin render). Firefox: lo cerré una vez con cierre normal
(`CloseMainWindow`) antes del md5 de B, por la regla de Omar (estaba abierto con 13 procesos); no se lo volvió a abrir.
Los procesos viejos de otras tandas que anotó F34 no se tocaron.

## Lo que queda abierto (entero)
1. **Tarjeta fecha-hora.** El papel nuevo no la trae: el reintento la dejó en null (el intento 1 traía «9 OCT 1963 ·
   22:39», como F36; el motivo del modelo —T72, 22:43— habla de otra hora; la voz dice «las diez y treinta y nueve»).
   En pantalla hay un marcador «⚠ falta fecha-hora» y el chequeo da ✗. Decide Omar (`--plan-edit`) o una regla del
   analista (p. ej., que la tarjeta no se pueda perder en el reintento).
2. **El reintento reescribe el papel entero** (el handoff pide «el JSON completo otra vez»): además de responder lo
   preguntado, perdió sin descarte escrito D128 (estaba en el intento 1), Q14, los sellos AVISO y ALARMA y la tarjeta, y
   cambió T92 por D245. Nada en el código conserva lo que el reintento no tenía que tocar. Decide el analista (p. ej.,
   que el reintento solo pueda cambiar los beats con motivo).
3. **Para la compuerta de Omar (gusto, no se forzó; lista del simulador §4):** qué dato en el gancho (D131 en [1] hoy;
   D118 opción A; D195 opción B; D131 además «adelanta» el salto del agua ~70 s y sus fuentes no coinciden en la
   altura); D195 en el clímax ([20] «Longarone ya no.»: hoy nada); ch06 b11 D128 vs D228 (hoy) vs D17; ch07 b12 Q14 vs
   T85 (hoy T85; el contrato pedía Q14); ch03 b4 T16 vs T15 (hoy); ch05 b8 Q50 vs D161 (hoy); ch05 b9 Q43 (hoy vacío);
   D84; los sellos (8 en el papel, 3 sin colocar). Todo por `--plan-edit` sobre `01e_pantalla.json`.
4. **Sellos sin colocar: CALMA, SILENCIO, RABIA**, con su lista de intentos: el crítico dice «estorba» en todos los
   instantes y lados que la escalera prueba (SILENCIO falla además por 0.03 s el corte en el inicio de su oración).
   Observación del simulador B (sin código): los pasos 1–3 caen a menudo sobre la misma foto; probar el otro lado antes
   ahorraría llamadas. El orden quedó literal del handoff.
5. **Expectativas de §C.3 que se cumplen por el modelo y no por la regla:** el gancho en [1] salió recién en el reintento
   (el intento 1, con el mismo prompt m01e-2, lo dejó en [15]; ningún motivo del reintento lo pedía); Q43 lo descartó el
   autor viendo `fecha: desconocida` (la validación 1c no se ejercitó en la corrida: solo el test); T39 lo eligió el
   modelo en el intento 1 (A.2 no lo trajo; A.2 actuó con D68). Las preguntas de A.4 (5) fueron todas falsos positivos y
   el autor dijo «otro hecho» en las 5: no sabemos si discrimina un «mismo hecho».
6. **D68 «vuelve» por error:** el parser de cifras no lee «un centímetro y medio» (ni «medio centímetro») como 1,5 / 0,5;
   la verificación de A.2 publica «falso: la voz no dice 1,5» sobre un descarte correcto (inocuo esta vez: el autor lo
   volvió a descartar). Arreglarlo es del parser de `voz_utils` (fracciones en letras).
7. **El filtro de spoiler compara cifras y nombres, no hechos:** D131 «SALTO DEL AGUA» en [1] adelanta lo que la voz
   cuenta en [14]–[15] y nada lo detecta.
8. **Lecturas declaradas de A:** el año en dos cifras sitúa un ítem (sin eso D47 caía por 1b); las expresiones relativas
   («años después») no se implementaron (lista de palabras, regla 22:26); 1c acepta el autor por cualquiera de sus nombres
   propios (Q50 pasó por «Erto»); el rango de años es el de las `fecha` del pool. El año en dos cifras es frágil: cualquier número igual a
   los dos últimos dígitos del año del ítem en la oración o una vecina alcanza (revisor, fila 2).
9. **`caben` sin pasar de `callout_dur_max` × 15** (cascada de B.2 en Fase 1, no estaba en A): cambia la entrada del
   papel. Declarado.
10. **Clave del perfil:** `costos.m01e_tope_usd` no está en `gfx_profiles/misterio.json` (fuera de git): la agrega Omar;
    mientras tanto corre el respaldo 1.00. El analista puede anotar el 1.00 en DECISIONES (hoy el origen es el pedido).
11. **Perillas huérfanas nuevas del perfil** (las borra Omar; el código las ignora): `tokens.interrupt_min_sec`,
    `callout_sec_per_word`, `callout_base_sec`, `zoom_conf_min`, `archive_dur`, `archive_head_max_words`,
    `archive_body_default`, `archive_body_head_max_words`, `archive_body_max_words`. Y la lista de F36 sigue.
12. **Código sin uso que no estaba en la lista de F37** (no se tocó): perillas ya muertas antes de la tanda
    (`zoom_rect_sec`, `zoom_approach_sec`, `zoom_hold_min_sec`, `zoom_box_min`, `zoom_box_max`, `sfx_gain_db`),
    funciones `gfx_guion._ocupa`, `gfx_pool.content_icon`, `gfx_pool.cap_candidates`, `voz_utils.munon`,
    `gfx_literal_lock.plan_strings` (solo tests); `quote_card` (abierto 7 de F36) sigue sin uso en el camino del papel;
    `OUT_TOKENS_PEOR` conserva un origen que nombra al rotulista borrado.
13. **El crítico por intento cambió de clave de caché:** las fichas se re-juzgaron (Gemini no es determinista: en la prueba
    de B con el papel de F36, D17 —que pasaba en F36— dio «estorba» en su instante y se movió).
14. **Regresiones de B encontradas y arregladas en C** (con test): el intento 3 no probaba la escena que arranca dentro de
    la oración siguiente (F32 §B.3 sí); el reparto veía el reloj sin recortar. Y la anotación «movido» listaba fallas
    posteriores. La comparación del simulador está hecha sobre el guion previo al arreglo del reloj (adenda arriba).
15. **El reloj de voz de ch05** (9 OCT 1963, 1.88 s) ya no sale (`TICKER_MIN`). Si Omar lo quiere, es la regla del reloj.
16. **Simulador de A después del código** (declarado; antes hubo una corrida en seco de CC).
17. **El lab de identidad** (`gfx_lab_server`) muestra todos los datos sin elegibilidad (era del borrador) y ya no tiene el
    candado de la pregunta reformulada (la pregunta es el `cierre` de la escaleta o la manual de Omar); sigue sin
    `/question`, `/summary`, `/save_identity` (F36).
18. **Docs históricas** (reportes y handoffs de F29b–F36, `DECISIONES.md`) nombran `gfx_rotulista`/`rotulista_*` y
    `--rotulista`: no se reescribieron. `guard_render` todavía lista `--rotulista-tope`/`-modelo` como flags con valor
    (inocuo).
19. **Fase 1 entera** no se corrió con `run_pantalla` enganchado (abierto 14 de F36, sigue).
20. Las 5 fallas previas siguen (01b_pauses ×3, m03_merge_timing ×2); «inicio de voz» ch07 sin rampa (F32) sigue.
21. **La comparación del simulador se hizo sobre la 3.ª `--plan-only`** (antes del arreglo del reloj); la 4.ª, la final,
    está cubierta por la adenda de §C.3 y `c/diff_reloj.txt`, no por una segunda corrida del simulador.
22. **Mapa:** la columna «nació» de `pantalla_entrada`/`pantalla_filtros`/`pantalla_colocar` apunta a `838a104` (el
    commit del renombre), no a F29b (el mapa toma el primer commit del archivo con su nombre).

## Veredicto del revisor (`revisor-handoff`, íntegro)
VEREDICTO: CUMPLE CON OBSERVACIONES

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | Paso 0: DECISIONES tal cual | OK | `6631703` toca solo DECISIONES, REVISION_PAPEL y el handoff; las 3 líneas (22:26, 22:32, 3b) están en el diff. |
| 2 | A.1a–d (fecha/rol/testimonio, fecha del relato, cita sin fecha, nota para Fase 1) | PARCIAL | Implementado y con tests. Pero A.1b no implementa «años después» / «más tarde», que el handoff listaba; está declarado y justificado por la regla 22:26. Además se agregó el año en dos cifras (`voz_utils.dice_anio`, `anio % 100`). Es frágil: cualquier número igual a los dos últimos dígitos del año alcanza. Lo marcó el simulador de A. |
| 3 | A.2 `tipo` + verificar `voz_lo_dice` | OK, con falla conocida | `m01e_pantalla` (`TIPOS_DESCARTE`, `voz_no_lo_dice`). En la corrida, D68 volvió por error («centímetro y medio» no se lee como 1,5). Está declarado en el abierto 6. |
| 4 | A.3a: reemplazo literal y único cambio de prompt | OK | Recalculé los md5 con `git show`: SYSTEM `0354c764…` → `e7b3e0a3…`, prompt `aa1ebc33…` → `ababbc8b…`. Coinciden con el reporte. El diff es solo esa frase más `tipo`. `PROMPT_VERSION = "m01e-2"`. |
| 5 | A.3b / A.4 / A.5 (pico vacío, preguntas al autor, un reintento, tokens y costo) | OK | Tests f37a (9). Corrida real: 2 llamadas, US$ 0.7649 contra tope 1.00, tokens por intento en el `.md`. |
| 6 | A.6 un test por punto | OK | `test_module_f37a_papel.py`, 9 tests, uno por cada caso del handoff. |
| 7 | Constantes sin origen | OK | `SEG_POR_PALABRA` derivado (0.3459, respaldo 0.35 con `# medido`). `TOPE_USD_RESPALDO = 1.00` con `# DECISIONES: pedido de Omar`. `LECTURA_CPS` y la tolerancia `5e-4` tienen origen anotado. Los demás números del diff son literales de código, no constantes. `test_constantes_con_origen` pasa. |
| 8 | `TOPE_USD` al perfil | PARCIAL | `gfx_config` acepta `costos` y el código lo lee. La clave NO está en `gfx_profiles/misterio.json`; el valor 1.00 vive solo como respaldo en el código. El handoff §Frenos lo permite («dejar la clave para que Omar la agregue»). Está declarado. |
| 9 | B.1–B.3 (escalera, duración 2.5–6 s, cita sin doble autor) | OK | `pantalla_colocar.instantes` / `repartir` / `duracion`; tests f37b (10). Fichas del guion final: máximo 4.73 s. |
| 10 | B.4 papel como único camino y restos borrados | PARCIAL | Se borraron el borrador, Gemini, el caché, `--rotulista` y los muertos. `gfx_critic.KIND_LABEL` sigue (reducido a 3 etiquetas, en uso), aunque el reporte lo lista como borrado. `script_engine/aprobacion.py:43,62` todavía manda a correr `--plan-only --rotulista`, un flag que ya no existe. Eso no figura en el abierto 18. |
| 11 | B.5 renombres, runners rotos | OK | `git mv` hecho. En código vivo no quedan nombres viejos, salvo menciones en docstrings y comentarios. 6 runners de lab borrados. |
| 12 | Mapa con 0 muertos | OK | `MAPA_MODULOS.json`: `muertos: []`, 35 módulos, 115 aristas. Observación menor: la columna «nació» de los 3 módulos renombrados ahora apunta a `838a104` en vez de F29b. |
| 13 | Prohibiciones (render, aprobar, merge, prompts de escaleta/guionista/partición) | OK | Ningún `m01a*`, `m01b*` ni `m01d*` tocado. Sin `--aprobar-guion` ni merge en el historial. Corrí suite rápida (58) y amplia (806 + 5 previas, las mismas 5 fallas previas conocidas); no hice render ni llamadas a modelos. |
| 14 | C.1 / C.2 (m01e suelto y `--plan-only`) | OK | El `.md` pegado en el reporte es idéntico a `lab/hyperframes/f37/c/01e_pantalla.md` y a la copia en `data/scripts/_steps/f8s3-vajont/`. Incluye el reintento con sus motivos. El resumen del guion está entero. Las fechas de los logs son posteriores al último cambio de código. |
| 15 | C.3 simulador línea por línea | PARCIAL | Está hecho y es honesto (no fuerza los puntos de gusto y los lista). Pero se corrió sobre la 3.ª `--plan-only`. Después CC arregló el reloj (T85 entra, el reloj de ch05 sale) y solo lo cubrió con una adenda; el simulador no se re-corrió sobre el guion final. |
| 16 | C.4 totales, costo, tokens, abierto entero (20), ESTADO, md5 | OK | Totales finales: 12 fichas, 7 de 7 picos, 5 sellos, 3 relojes. El md5 de ch02 en los logs es `38e5ba14…` (no lo re-corrí: es render). El ESTADO está actualizado. El reporte conserva el marcador `@@REVISOR@@` (1 ocurrencia). |

Observaciones sin número:
- Simulador de A: el paso 5 de `tanda.md` pide el simulador antes del código. En A corrió después. Está declarado.
- Cambio de comportamiento en C: el arreglo de C (`hasta_el_corte` antes del reparto) sacó el reloj de voz de ch05 por `TICKER_MIN` y cambió una transición. Está declarado en el abierto 15.

Fuera de alcance: ninguno. Todo lo que no es del handoff es cascada declarada de B.4 y B.5 (`.claude/hooks/guard_mapa.py`, skills, agente `simulador`, `gfx_lab_server`, `make_bug`, `lab/tools/mapa_*`). Lo ajeno que ya estaba modificado (`diag_234_cap4.py`, `gfx_profiles/*`, `f28a.log`) no lo tocó la tanda.

Riesgos que el contrato no cubre:
- El reintento reescribe el papel entero y perdió D128, Q14, AVISO, ALARMA y la tarjeta sin dejar motivo. El reporte lo declara (abiertos 1 y 2), pero ningún control lo evita.
- Dos expectativas de §C.3 salieron por el modelo y no por la regla: el gancho en [1] y Q43 fuera. Las reglas 1c y A.2 nunca se ejercitaron sobre un caso real de Vajont. Solo las prueban los tests sintéticos.
- La parte C sigue sin commitear. El commit C tiene que incluir este veredicto pegado en lugar de `@@REVISOR@@`.

### Qué hizo CC con las observaciones (después del veredicto)
1. **`aprobacion.py`** (fila 10): los dos mensajes que mandaban a correr `--plan-only --rotulista` ahora dicen `--plan-only`
   (texto de error; `test_module_f33`/`f34` verdes, 16). Entra en el commit C.
2. **`KIND_LABEL`** (fila 10): el reporte decía «borrado»; quedó **reducido** a sello, recorte y ficha (en uso). Corregido
   en §B.4 del reporte.
3. **Simulador sobre la 3.ª `--plan-only`** (fila 15): no se re-corrió; la adenda de §C.3 dice qué cambió en la 4.ª (T85
   entra, reloj de ch05 fuera, una transición) y el diff entero está en `c/diff_reloj.txt`. Queda en el abierto (21).
4. **Año en dos cifras frágil** (fila 2), **clave del perfil** (fila 8), **reintento que reescribe todo** y **reglas que no
   se ejercitaron en Vajont** (riesgos): ya estaban en el abierto (8, 10, 2, 5); se agrega la fragilidad del año en dos
   cifras al abierto 8.
5. **Columna «nació» del mapa** de los módulos renombrados (fila 12): el mapa toma la fecha del primer commit del archivo
   con su nombre nuevo; queda anotado (abierto 22).
