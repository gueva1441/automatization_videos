# F64_REPORT — El papel a producción: Opus + entrada completa, sin tope, y el verificador decide los cortes

Handoff `lab/hyperframes/f64/HANDOFF_F64_papel_a_produccion.md` (md5 8e02950969854ba7bee830e102aec980) · rama `f11-guion-v4` · base `b9979f6` · 2026-10-31 · CC Opus medium. Commits: `0e849f4` (Etapa 0) · `f82f35b` (Etapa 1) · `4ec3102` (Etapa 2) · `7b48ebf` (Etapa 3) · `43eba23` (Etapa 4 + reporte).

## 0. Antes de tocar nada: los llamadores de `m01e_pantalla` (§2.5)

`grep -rn "m01e_pantalla\.\(validar\|llamar\|momentos\|TopePantalla\|tope_usd\|_peor_usd\|OUT_TOKENS_PEOR\|confirmados\|cortados_al_cierre\)\|from script_engine.m01e_pantalla import" --include=*.py .` (sin `.venv`), corrido sobre `b9979f6` antes de tocar nada:

| llamador | qué usa | qué se hizo |
|---|---|---|
| `fase2b.py:3738` | `from script_engine.m01e_pantalla import editar` (`--plan-edit`, a mano) | nada: `editar` no cambia |
| `script_engine/pantalla_entrada.py:83` y `:100` | `_texto_item`, `TIPO_DE_ESTILO`, `cargar_papel` (Fase 2 lee el papel) | `_texto_item` ahora también escribe un L «nombre — rol»; en `:142` dejó de copiar `juicio_autor` al bloque (Etapa 3) |
| `lab/hyperframes/f40/a/sim_gancho.py:4` | `m01e_pantalla.validar` (lab, historia) | no se adapta ni se importa |
| `lab/hyperframes/f63/etapa_a_papel.py:153` | solo en un docstring (`m01e_pantalla.llamar.autor`); importa `cargar/entrada/validar/...` con la firma vieja | historia: no se adapta (el handoff lo dice); la simulación de la Etapa 3 NO importa de ahí |
| `fase1_5.py:234-237` | `import m01e_pantalla as mp` → `mp.generar`, `mp.SinJSON`, `mp.TopePantalla` | el grep del handoff no lo ve (importa el módulo, no `from … import`); `TopePantalla` fuera en la Etapa 1 |
| `gfx_realizador`, `pantalla_colocar` | no importan `m01e_pantalla` (el grep no los encuentra); `pantalla_colocar` lee el papel por `pantalla_entrada` | `pantalla_colocar.py:196` dejó de copiar `juicio_autor` (Etapa 3) |
| tests | `test_module_f36c_pantalla, f37a_papel, f38a_m01e, f38a_voz, f38c_papel, f38d_vueltas, f38e_c, f38e_d, f38e_e, f40_gancho` (`from script_engine import m01e_pantalla as mp`) | adaptados o borrados por etapa (ver cada etapa) |

También leen `juicio`/`juicio_autor` (lo encontró `grep -rn juicio script_engine/`): `pantalla_filtros.py` (`contradicciones_de`, `contradicciones`, `_sin_juicio`, `no_dicho`, `spoiler`, `ancla_papel`), `gfx_guion.py:275/283/493` (eventos y chequeo 5), `pantalla_colocar.py:196`, `pantalla_entrada.py:142`. Todo eso se tocó en la Etapa 3 (§2.3: «si … leen `juicio`, se borra el parámetro y su lectura»).

## Etapa 0 — Opus medium y la entrada completa (`0e849f4`)

`script_engine/m01e_pantalla.py`: `PROMPT_VERSION = "m01e-7"`, `MODELO = "claude-opus-5-5"`, `EFFORT = "medium"`; `PANTALLA_SYSTEM` con la oración 2 del primer párrafo reemplazada byte a byte por `ORACION2_DESPUES` de F63 A.2; `_tipo` devuelve D/T/Q/P/L por `_kind` (fuera la condición `numeros(...)` que escondía D85, D34, D03, D129, D10, D20, D70); `_texto_item` escribe un L «nombre — rol» como una P; `contexto_fuente(it)` nuevo (cita_literal o la de la primera evidencia, espacios normalizados) y cada ítem lo lleva al final; los beats llevan `emocion, imagen_sensorial, pregunta_abierta, paga` después de `cierre`, tal cual (None donde falte); `cargar(…, log=None)` lee `ficha_caso.json` (ausente → `ficha_caso: None`, `disputas = {}` y una línea en el log); `entrada` arma `escaleta_video` (los 7 campos en orden, None donde falte) y `disputas` (`versiones`, `contradicciones`); `_para_modelo` los suma después de `clima`. Docstring del módulo. Nada específico de Wittenoom.

**Salida en texto:**

```
md5(PANTALLA_SYSTEM) = 85d094bed6090b14d1802ca97433d982   (esperado 85d094be…) OK
md5(pedido(ent))     = 018f9cc1b939e2afdcfad5eb5ebcc36f   (esperado 018f9cc1…) OK  — sin diff de claves
cabecera: {archivo: 362 (D155·T98·Q50·P35·L24), caps: 7, beats: 13, chars_user: 199691}
```
Sin llamadas al modelo. `01b_narracion_v3.json` md5 c7badfbe260f5eb24a47e780b40406b5 (el de producción de hoy).

**Tests:** `test_module_f64.py` Etapa 0 (5): modelo/effort/versión/SYSTEM; todo el pool entra con `contexto_fuente` al final; beats, `escaleta_video` y `disputas` en orden (y `flash_forward` no llega al autor); `ficha_caso.json` ausente no rompe y `cargar` lo anota; un L propuesto como ficha sale `normal` y `voz_no_lo_dice` lo tolera. Adaptados a m01e-7: `f37a::test_a3a`, `f38a::test_a1_formatos_literales` y `test_f38b_gancho_literal`, `f38c::test_prompt_no_cambia` (prompt_md5 f2bfdf2044a4c77a59fc62ebe93966c2), `f38d::test_5`, `f38e_c::test_c1` (el bloque del md con su oración 2 reemplazada, y nada más) y `test_c5` (la corrida histórica queda fijada a su md5 de m01e-6), `f40::test_prompt_no_cambia`. Suite del papel 82 verdes + 7 saltados.

## Etapa 1 — Se borra el tope + chascada `error_handler` (`f82f35b`)

`m01e_pantalla.py`: fuera `TOPE_USD_RESPALDO`, `OUT_TOKENS_PEOR`, `tope_usd()`, `TopePantalla`, `_peor_usd`, el argumento `tope` de `llamar`, `out["tope"]`, `salida_peor`, el cierre «tope» y el `raise`; `autor()` devuelve solo la respuesta; `armar` sin el campo `tope`; `a_markdown` sin la línea «tope US$»; `main()` atrapa solo `SinJSON`; docstrings reescritos. `fase1_5.run_pantalla`: `except mp.SinJSON`. `gfx_config.py`: «costos» fuera de `_PROFILE_KEYS` y de la validación (l.437-439); `grep -rn costos --include=*.py .` fuera de m05_judge solo da `01_v3_costos.json`, los `costos_fNN.json` de lab y variables locales, ningún lector de `costos.m01e_tope_usd`. El perfil activo (`gfx_profiles/misterio.json`) no trae `costos`; si un perfil fuera de git la trajera, el validador la reporta como clave desconocida y Omar la borra a mano. Chascada: `error_handler.py` l.68 `logging.FileHandler(log_file, encoding="utf-8", delay=True)`.

**Salida en texto:**

```
$ grep -rn "tope" script_engine/m01e_pantalla.py fase1_5.py
script_engine/m01e_pantalla.py:23:   … sin tope en dólares (F64 Etapa 1, DECISIONES 2026-10-31 13:07: el costo se informa, no frena) …
script_engine/m01e_pantalla.py:808:  """La llamada con caché y las vueltas de reintento, sin tope en dólares (F64 Etapa 1 …
script_engine/m01e_pantalla.py:845:  """Una llamada del autor: la respuesta JSON o None (sin tope: F64 Etapa 1)."""
fase1_5.py:232:                      … sin tope en dólares desde F64 Etapa 1 …
```
Solo docstrings reescritos que dicen «sin tope». Tests borrados: `test_module_f37a_papel::test_0_tope_usd_se_lee_del_perfil`, `test_module_f38d_vueltas::test_3_tope_cierra_antes_de_la_vuelta_que_no_entra` (+ sus helpers `_peor`/`_usd`); `tope=100.0` quitado de las llamadas en f37a, f38a, f38d, f38e_c, f40.

**Tests:** `test_module_f64.py` Etapa 1 (4): sin tope en el código ni en raw/.json/.md y el costo se informa; `gfx_config` sin «costos»; `fase1_5` solo atrapa `SinJSON`; importar `error_handler` y construir el handler en un proceso nuevo no crea archivo en `logs/`, y escribir sí lo crea. Suite del papel + f39 91 verdes + 7 saltados.

## Etapa 2 — El año del relato por máximo del cap (`4ec3102`)

`m01e_pantalla.py`: `momentos_detalle(ent)` nuevo → por oración `{anio, cap, idx, heredado}`: el MÁXIMO año dicho en el cap hasta la oración incluida, sin contar las oraciones de beats `flash_forward`; mientras el cap no dijo ninguno, el del cap anterior (heredado, que no entra al máximo); `momentos(ent)` = `{(cap, idx): anio}` sobre él. Los beats de `entrada` llevan `flash_forward` (dato de la escaleta) y `_para_modelo` lo quita, así el USER sigue en 018f9cc1…. El motivo de `fecha_relato` dice «el año más alto que la voz dijo en el cap hasta ahí». Lab: `lab/hyperframes/f64/etapa2_relato.py` (reimplementa el viejo tal cual para compararlo; no toca nada fuera de f64/).

**Salida en texto:**

Tabla y filas de diferencia en `ETAPA2_relato.md` (abajo, entero). Dos cosas que el handoff no sabía: (1) **D83 en ch02 [7] ya pasaba hoy** con la función real: la vecina [8] dice «1962» y `dice_anio(1958, vecinas)` la sitúa (el auditor supuso «corta»); (2) `anios_dichos` lee «dos mil» de ch06 [7] como 2000 → relato 2000 en [7]–[9], igual que hoy (no cambia). 43 de 142 oraciones cambian de relato: ch01 entero → None (su único año, 1963, es del beat flash-forward: el gancho queda libre), ch05 [13]–[23] y ch06 [0]–[6] 1962 → 1991 (D23 [18] y T57 [2] pasan), ch06 [10]–[15] 2006 → 2007, ch06 [17]–[20] y ch07 [0] 2016 → 2021, ch07 [9]–[15] 1957 → 2026.

**Tests:** `test_module_f64.py` Etapa 2 (2): máximo del cap con recuerdo de un año anterior, cap sin año que hereda, heredado fuera del máximo, beat flash-forward ignorado, `momentos_detalle` con dónde se dijo; `fecha_relato` usa el máximo y el gancho queda libre. Suite 82 + 7.

### Etapa 2 — ETAPA2_relato.md entero

#### F64 Etapa 2 — el año del relato: viejo (último año dicho) vs nuevo (máximo del cap) sobre Wittenoom

Topic `123bbb64-9fca-4395-8bf4-57d60e219ef1` · rango de años del material (1930, 2026) · beats flash-forward: [1] · calculado con `voz_utils.anios_dichos` y `m01e_pantalla.momentos` (el viejo, reimplementado en este script tal cual F37 §A.1b).

#### 1. La tabla del handoff, con la función real

| ficha | año | ancla | relato hoy (viejo) | relato nuevo |
|---|---|---|---|---|
| D23 | 1989 | ch05 [18] | 1962 → corta | 1991 → pasa |
| D23 | 1989 | ch05 [12] | 1991 → pasa | 1991 → pasa |
| T57 | 1985 | ch06 [2] | 1962 → corta | 1991 → pasa |
| D94 | 1989 | ch05 [8] | 1988 → corta | 1988 → marca (la decide el verificador, Etapa 3) |
| D83 | 1958 | ch02 [7] | 1950 → pasa | 1962 → pasa |

#### 2. Oraciones de Wittenoom donde el relato nuevo ≠ el viejo

| cap | idx | beat | viejo | nuevo | de dónde sale el nuevo | oración |
|---|---|---|---|---|---|---|
| ch01 | 6 | 1 | 1963 | None | — (ningún año dicho fuera del flash-forward) | Wittenoom, Australia Occidental, 1963. |
| ch01 | 7 | 1 | 1963 | None | — (ningún año dicho fuera del flash-forward) | Esa foto se tomó en un pueblo que hoy no figura en ningún mapa. |
| ch01 | 8 | 1 | 1963 | None | — (ningún año dicho fuera del flash-forward) | Arrancaron las señales de la carretera y borraron el nombre. |
| ch01 | 9 | 1 | 1963 | None | — (ningún año dicho fuera del flash-forward) | Lo que sobró de la mina, en cambio, sigue donde lo dejaron. |
| ch01 | 10 | 1 | 1963 | None | — (ningún año dicho fuera del flash-forward) | Pero antes de que lo borraran, alguien tuvo que llevar a ese hombre hasta allí. |
| ch01 | 11 | 1 | 1963 | None | — (ningún año dicho fuera del flash-forward) | Dos años antes de la foto, en Madrid, hubo un baile. |
| ch02 | 7 | 3 | 1950 | 1962 | dicho en ch02 [4] | No iban solos: cerca de ocho mil españoles cruzaron por un acuerdo entre los dos gobiernos, y CSR, la compañía |
| ch05 | 13 | 10 | 1962 | 1991 | dicho en ch05 [12] | La misma palabra que McNulty había escrito en 1962 sobre un trabajador del molino, el año en que Daniel bajó d |
| ch05 | 14 | 10 | 1962 | 1991 | dicho en ch05 [12] | Eso había en el polvo. |
| ch05 | 15 | 10 | 1962 | 1991 | dicho en ch05 [12] | Eso respiraba mientras esperaba que le cerrara el pie. |
| ch05 | 16 | 10 | 1962 | 1991 | dicho en ch05 [12] | Daniel tenía cincuenta y cinco años. |
| ch05 | 17 | 10 | 1962 | 1991 | dicho en ch05 [12] | María tenía las fotos. |
| ch05 | 18 | 10 | 1962 | 1991 | dicho en ch05 [12] | Nueve meses después del diagnóstico, Daniel Écija murió en Madrid, a miles de kilómetros de la pista roja, cas |
| ch05 | 19 | 10 | 1962 | 1991 | dicho en ch05 [12] | Lo alcanzó. |
| ch05 | 20 | 10 | 1962 | 1991 | dicho en ch05 [12] | «Ese lugar cambió nuestras vidas para siempre», dice el hijo, el niño del bautizo. |
| ch05 | 21 | 10 | 1962 | 1991 | dicho en ch05 [12] | Fueron nueve meses. |
| ch05 | 22 | 10 | 1962 | 1991 | dicho en ch05 [12] | El mismo tiempo que un embarazo. |
| ch05 | 23 | 10 | 1962 | 1991 | dicho en ch05 [12] | Daniel había estado en Wittenoom diez. |
| ch06 | 0 | 11 | 1962 | 1991 | heredado de ch05 [12] | A los que pasaron por Wittenoom, el nombre los sigue. |
| ch06 | 1 | 11 | 1962 | 1991 | heredado de ch05 [12] | Los que nacieron allí lo llevan escrito en el pasaporte. |
| ch06 | 2 | 11 | 1962 | 1991 | heredado de ch05 [12] | En un control de aeropuerto, el policía lee la página, baja la cabeza, vuelve a mirar. |
| ch06 | 3 | 11 | 1962 | 1991 | heredado de ch05 [12] | «Así que de Wittenoom, ¿eh? |
| ch06 | 4 | 11 | 1962 | 1991 | heredado de ch05 [12] | Un sitio terrorífico», dice el policía. |
| ch06 | 5 | 11 | 1962 | 1991 | heredado de ch05 [12] | Mercedes de Juan se quedó en Australia y vive con una cita que se repite. |
| ch06 | 6 | 11 | 1962 | 1991 | heredado de ch05 [12] | «Nos hacen un escáner y una prueba de función pulmonar», dice ella. |
| ch06 | 10 | 12 | 2006 | 2007 | dicho en ch06 [10] | Hacia junio de 2007, según otras referencias en 2006, Wittenoom fue abolido oficialmente. |
| ch06 | 11 | 12 | 2006 | 2007 | dicho en ch06 [10] | Le quitaron el nombre de los mapas y arrancaron las señales de la carretera. |
| ch06 | 12 | 12 | 2006 | 2007 | dicho en ch06 [10] | El gobierno de Australia Occidental lo llamó «el fin de un período oscuro en la historia de nuestro Estado». |
| ch06 | 13 | 12 | 2006 | 2007 | dicho en ch06 [10] | El DWER y el Department of Health declararon la zona «no apta para ninguna forma de ocupación humana o uso del |
| ch06 | 14 | 12 | 2006 | 2007 | dicho en ch06 [10] | Lo que no se puede abolir son los relaves: más de tres millones de toneladas que siguen donde las dejaron. |
| ch06 | 15 | 12 | 2006 | 2007 | dicho en ch06 [10] | El agua baja por los lechos de los arroyos y las pozas hasta el Fortescue arrastrando asbesto, y un informe ad |
| ch06 | 17 | 12 | 2016 | 2021 | dicho en ch06 [16] | En 2016 un documento estatal aconsejó no asegurar los relaves. |
| ch06 | 18 | 12 | 2016 | 2021 | dicho en ch06 [16] | No porque fuera técnicamente imposible. |
| ch06 | 19 | 12 | 2016 | 2021 | dicho en ch06 [16] | Porque salía caro. |
| ch06 | 20 | 12 | 2016 | 2021 | dicho en ch06 [16] | En esa tierra vivía un hombre que no podía irse. |
| ch07 | 0 | 13 | 2016 | 2021 | heredado de ch06 [16] | Maitland Parker era Banjima, y esa tierra era la suya. |
| ch07 | 9 | 13 | 1957 | 2026 | dicho en ch07 [5] | Quién sabía está escrito: dos inspectores en 1944, un médico al que llamaron alborotador en 1948, un tribunal  |
| ch07 | 10 | 13 | 1957 | 2026 | dicho en ch07 [5] | La mina siguió hasta que dejó de dar dinero. |
| ch07 | 11 | 13 | 1957 | 2026 | dicho en ch07 [5] | La palada, todavía nadie. |
| ch07 | 12 | 13 | 1957 | 2026 | dicho en ch07 [5] | Daniel Écija vivió diez meses en Wittenoom. |
| ch07 | 13 | 13 | 1957 | 2026 | dicho en ch07 [5] | Nadie en su familia sabe decir qué respiró allí. |
| ch07 | 14 | 13 | 1957 | 2026 | dicho en ch07 [5] | Wittenoom ya no está en el mapa. |
| ch07 | 15 | 13 | 1957 | 2026 | dicho en ch07 [5] | ¿Qué respiró en diez meses que tardó casi treinta años en matarlo? |

Total: 43 oraciones distintas de 142.

#### 3. «dos mil» en ch06 [7]

- oración: «Melita Markey sigue contando lo que el gobierno dejó de contar en dos mil; otras estimaciones, dice, hablan de más de cuatro mil, y la cifra sube.»
- `anios_dichos` lee: [2000]
- relato viejo en ch06 [7]–[9]: [2000, 2000, 2000] · nuevo: [2000, 2000, 2000]


## Etapa 3 — El verificador decide los cortes (`7b48ebf`)

**`script_engine/pantalla_verificador.py` (nuevo):** `MODELO = "claude-opus-5-5"`, `EFFORT = "medium"`, `REINTENTOS = 1`; `SYSTEM_V` y `FORMATO_V` literales del handoff (md5 del SYSTEM 104b9ea817690c5b45afbe74f87a2111); `pedido(marcas, caps)` puro (caps con idx/texto; fichas con pool_id, cap, beat, sentence_idx, oracion_ancla, etiqueta, texto, respaldo, dato_archivo —en una Q la frase que la ficha muestra y el testimonio entero en `cita_completa`—, regla, coincidencia {token, cap, idx, oracion}; descartes con pool_id, dato_archivo, motivo_del_autor, caps_que_lo_cuentan) + «Formato de salida: » + FORMATO_V; `pedido_md5`; `_leer(resp, marcas)` puro (un veredicto cuyo (pool_id, cap, beat) —o pool_id— no está en las marcas se ignora y se anota, lo mismo un veredicto que no es pasa/corta o dicho/no_dicho; una marca sin veredicto queda «pasa»/«no_dicho» con motivo «sin veredicto»); `verificar(marcas, caps, *, post, log)` como `llamar.autor` (system, messages, output_config.effort, hx.MAX_TOKENS → `hx._post`, `hx.cost_of`, `hx._track(…, "m01e_verificador")`), 1 reintento; sin JSON en dos intentos: todo «pasa» «sin veredicto», `error` y una línea en el log (no se corta a ciegas, no se frena). Sin marcas no llama.

**`m01e_pantalla.validar(resp, ent, *, juez=None)`:** `no_dicho`, `spoiler`, `contradice` y `fecha_relato` no cortan: cada coincidencia es una marca (en el gancho, la cifra que la voz dice en un cap siguiente no se repite como spoiler: una marca por (token, cap, idx), dedupe que pidió la revisión de los tests); `fecha_relato` marca solo donde hoy cortaría (testimonio y `dice_anio` exentos), con `coincidencia = {token: str(anio), relato, cap, idx, oracion}` de donde la voz dijo el máximo; los descartes «voz_lo_dice» que `voz_no_lo_dice` pone en duda son marcas de regla `voz_lo_dice` con `caps_que_lo_cuentan` (o «todo el video»). UNA llamada al `juez` (por defecto `pantalla_verificador.verificar`) después del loop de fichas y de calcular `vuelven`, antes de `picos_vacios`, `a_pantalla_vacios` y `motivos`. «corta» → `slot["ficha"] = None`, fuera de `usados_ids`, a `descartados` con `que: "ficha"`, `quien: "verificador"`, la regla original (`reglas` y `tokens` con todas las marcas de esa ficha) y el motivo del verificador (+ «(cap [idx])»); «pasa» → `juicio_verificador: {regla, motivo, tokens}`; descarte «dicho» → queda como el autor lo escribió (sin «falso»; se anota `verificador: dicho: …`), «no_dicho» → sigue en `vuelven` marcado «falso». Sin marcas no se llama. `claves` paralelas a `motivos`: ficha `(regla, pool_id, cap, beat, token)`, descarte `("voz_lo_dice", pool_id)`, pico `("pico", cap, beat)`, a_pantalla `("a_pantalla", cap, beat)`. `_validar_ficha` devuelve `(motivo, regla, ficha, marcas)` y recibe `momentos_detalle(ent)`. **Borrados:** `confirmados`, `final`, `juicio` (también en `pantalla_filtros`), `_confirmar`, `_acumular`, `juicio_autor`, `_respuestas`, `preguntas`/`pregunta` en la ficha, `_pregunta_txt`, `cortados_al_cierre`, `cierre_final`, `_clave_desc`. Siguen cortando en código: `candado`, `caben`, `anclaje`, `formato`, `respaldo`, `cita_sin_fecha`, `una_vez`, `sello`.

**`llamar(ent, out_dir, *, post=None, juez=None, log=None)`:** `juez` por defecto `functools.partial(pantalla_verificador.verificar, post=post, log=log)`; hay vuelta mientras haya motivos y el conjunto de claves no sea igual al de NINGUNA vuelta anterior (el ciclo A→B→A cierra); el texto con el motivo del verificador se le manda al autor igual; cierres «sin motivos» / «sin progreso» / «sin JSON» / «sin beat»; `cerrar(papel, val, por)` guarda el papel y SU validación (ya no hay una validación distinta al cerrar). Raw: `verificador: [{pedido_md5, marcas, veredictos {fichas, descartes, ignorados, sin_veredicto}, usage, usd, segundos, intentos, error}]`, `usd = usd_autor + usd_verificador`, `claves` por vuelta. Caché: en el hit, `validar` corre con un juez que busca en `prev["verificador"]` por `pedido_md5` y devuelve lo guardado (US$ 0); si un pedido no está, llama al verificador, anota «caché parcial» en el log y completa el raw. `armar`: `usd`, `usd_autor`, `usd_verificador`, `verificador` (por llamada: marcas, pasa, corta, dicho, no_dicho, usd, segundos, error), `marcas`; sin `tope`, `preguntas`, `cortados_al_cierre`. `a_markdown`: encabezado con autor + verificador, «verificador: pasa (reglas tokens) — motivo» por ficha, «Lo que cayó» con `quien in (validación, verificador)` y «(verificador; marcas …)», sección «Verificador» (cada llamada y cada marca), «claves:» por vuelta, «Cierre del reintento»; `_por_que_falta` también lee lo del verificador.

**`pantalla_filtros.py`:** `contradicciones_de`/`contradicciones` sin `juicio`; `_sin_juicio` borrado; `no_dicho`/`spoiler` sin él; `ancla_papel` sin `juicio_autor`. **`gfx_guion.py`** l.275/283 (eventos sin `juicio_autor`) y l.491-493 (chequeo 5 sin `juicio=`); **`pantalla_colocar.py`** l.196 y **`pantalla_entrada.py`** l.142 dejan de copiar `juicio_autor`. Nada específico de Wittenoom en el código.

**Tests:** `test_module_f64.py` Etapa 3: (a) `pedido` puro y estable (md5 fijo 848621c94d364db29d92a0e7002a737f sobre marcas de juguete; la Q lleva `dato_archivo` = frase de la ficha y `cita_completa`; sin `falta` ni `que`; constantes y md5 del SYSTEM); (b) `_leer` (desconocido se ignora y se anota, veredicto raro se ignora, faltante = pasa «sin veredicto»; `verificar` sin JSON dos veces → todo pasa «sin veredicto», body como llamar.autor, sin marcas no llama); (c) `validar` con juez falso (corta → descartados quien verificador, fuera del slot, motivo con «(cap [idx])», tokens, clave; pasa → `juicio_verificador`; descarte dicho no vuelve y queda sin «falso», no_dicho vuelve marcado; fecha_relato corta con su regla original; sin marcas el juez no se llama; .md con lo del verificador); (f) `llamar` (sin tope, «sin motivos» con una llamada del verificador; «sin progreso» por claves con motivo de texto distinto —el texto del verificador viaja al autor—; ciclo A→B→A cierra con 2 vueltas y 3 POST; una llamada del verificador por validación; el juez por defecto usa el `post` falso: sin API); (g) caché con `pedido_md5` guardado no llama al juez; caché parcial llama, anota y completa el raw. **Borrados con su lógica** (subagente): `f37a::test_a4_d47_llega_como_pregunta…`, `f38c::test_a2_confirmada_queda_juzgada…`, `f38c::test_a2_contradice_nueva_tras_el_reintento_corta`, `f40::test_2_sin_preguntar_al_cierre_corta_como_no_dicho`, `f40::test_4_fase2_no_dicho…respeta_el_juicio_del_autor`. **Reescritos como marcas:** `f38c::test_a2_d40_marca_contradice`, `f38d::test_1_d241_llega_como_marca_contradice_y_el_verificador_decide`, `f40::test_1_d03_llega_como_marca_no_dicho…`, `f40::test_2_mismo_hecho_el_verificador_la_corta_y_el_autor_la_saca`, `f40::test_4_no_dicho_en_el_gancho_deja_la_coincidencia_en_dichos`. **Adaptados:** `f37a::test_a1b` (marca fecha_relato «1970»/1963; con SEG ancho porque con 0,3459 s/palabra la ficha caía por `caben` y una ficha caída no deja marcas), `f38a::test_a1_lo_del_intento_1…` (las 5 marcas del intento 1 de F37; `beats_m` pasa de 6 a 2 porque las coincidencias ya no son motivo), `f38a::test_f38b_nada_llama_a_un_juez` (quedan los nombres del juez de anclaje de F38; «juez» existe ahora por F64), `f38c::test_a2_contradicciones…` (sin `juicio`), `f38d::test_2_sin_progreso_cierra` (con los datos reales de F38c cierra con 1 vuelta y 2 POST: las claves {caben Q50, pico, a_pantalla} se repiten aunque el texto del motivo cambie), `f38d::test_4`, `f38e_c::test_c3/test_c5`, `f40::test_3`. **Blindaje** en los 9 archivos viejos: fixture autouse que reemplaza `_juez_por_defecto` y `pantalla_verificador.verificar` por un juez «pasa todo» (sin él, `validar(resp, ent)` llama al verificador real). Suite del papel (f64, f36c, f37a, f38a_m01e, f38a_voz, f38c, f38d, f38e_c, f38e_d, f38e_e, f40, f37b, f39): **105 verdes + 6 saltados** (los saltados: sin Vajont en `data/`, previos). Rápida (hook) verde en cada commit. Stickers m01e_pantalla, pantalla_verificador (nuevo), pantalla_filtros, gfx_guion, pantalla_colocar, pantalla_entrada; MAPA 0 fallas.

### Etapa 3 — SIM_VERIFICADOR.md entero

#### F64 Etapa 3 — SIM_VERIFICADOR: los 8 papeles de F63 contra el `validar` nuevo + verificador real

Topic `123bbb64-9fca-4395-8bf4-57d60e219ef1` · entrada completa de producción (archivo 362 ítems) · verificador `claude-opus-5-5` medium · una llamada por papel, 8 a la vez · fuente: `lab/hyperframes/f63/a/*_[12].raw.json` (`respuesta`) · salidas crudas en `lab/hyperframes/f64/sim/`.

#### Totales por papel

| papel | marcas | fichas marcadas | pasa | corta | descartes marcados | dicho | no_dicho | tokens in/out | US$ | s (llamada) | intentos | error |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| O1_1 | 8 | 3 | 3 | 0 | 4 | 4 | 0 | 9948/1153 | 0.0629 | 10.4 | 1 | — |
| O1_2 | 5 | 3 | 2 | 1 | 2 | 2 | 0 | 9306/804 | 0.0533 | 7.1 | 1 | — |
| O2_1 | 9 | 3 | 3 | 0 | 6 | 6 | 0 | 9814/1164 | 0.0625 | 10.1 | 1 | — |
| O2_2 | 7 | 4 | 4 | 0 | 2 | 2 | 0 | 10039/1131 | 0.0628 | 11.0 | 1 | — |
| O3_1 | 10 | 4 | 3 | 1 | 6 | 6 | 0 | 10154/1366 | 0.0679 | 11.7 | 1 | — |
| O3_2 | 8 | 2 | 2 | 0 | 6 | 6 | 0 | 9582/1041 | 0.0592 | 8.5 | 1 | — |
| S_1 | 12 | 5 | 4 | 1 | 5 | 5 | 0 | 11117/1822 | 0.0809 | 15.1 | 1 | — |
| S_2 | 5 | 2 | 1 | 1 | 2 | 2 | 0 | 9246/857 | 0.0541 | 7.1 | 1 | — |
| **total** | 64 | | 22 | 4 | | 33 | 0 | | **0.5036** | 81.0 | | |

#### Cada marca, con su veredicto

##### O1_1

| que | id | cap/beat | regla | token (dónde lo dice la voz) | veredicto | motivo del verificador | oración |
|---|---|---|---|---|---|---|---|
| ficha | Q25 | ch02 b2 | spoiler | «2» (ch02 [7]) | **pasa** | La voz cuenta que ella iba cerca de él y confiaba en lo que venía, pero no cita la frase de que en España no tenían nada; el «2» de la coincidencia habla de otr | — |
| ficha | D94 | ch05 b9 | fecha_relato | «1989» (ch05 [8]) | **pasa** | La voz menciona el fallo de 1988, pero no el pago de 18,3 millones a 200 afectados en 1989; la ficha suma una consecuencia que la voz no dice. | — |
| ficha | D23 | ch05 b10 | contradice | «30» (ch05 [18]) | **pasa** | Los «casi treinta años» de Daniel no tienen relación con el corte de más de 500 muertos para 1989; la voz no dice esa cifra. | — |
| ficha | D23 | ch05 b10 | contradice | «2024» (ch07 [4]) | **pasa** | Los «casi treinta años» de Daniel no tienen relación con el corte de más de 500 muertos para 1989; la voz no dice esa cifra. | — |
| descarte | T13 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice que en 1946 ya había diagnósticos de asbestosis. | ch03 [14] |
| descarte | D21 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice que en 1961 la producción subió, tras narrar las advertencias previas. | ch03 [28] |
| descarte | T80 | — | voz_lo_dice | no dice Ministro, Desarrollo, Regional, Hon, Jon, Ford, MLC | **dicho** | La voz cuenta la abolición oficial hacia junio de 2007, aunque omite al ministro. | ch06 [10] |
| descarte | D95 | — | voz_lo_dice | no dice 1.500 | **dicho** | La voz dice la reclamación de mil quinientos millones de dólares australianos por la tierra Banjima. | ch07 [6] |

- fichas que quedan: 11/13 · cortadas por el verificador: [] · cortadas por el código: [('D26', 'caben'), ('Q19', 'caben')] · vuelven: [] · motivos para una vuelta: 9

##### O1_2

| que | id | cap/beat | regla | token (dónde lo dice la voz) | veredicto | motivo del verificador | oración |
|---|---|---|---|---|---|---|---|
| ficha | Q25 | ch02 b2 | spoiler | «2» (ch02 [7]) | **pasa** | La voz cuenta que ella confiaba en lo que venía y cita «me pegué a mi marido», pero nunca dice que en España no tuvieran nada. | — |
| ficha | T38 | ch02 b3 | spoiler | «1962» (ch02 [8]) | **corta** | La voz ya da la fecha en la vecina: boda el 20 de septiembre de 1962 y «cuatro días después estaban en un barco», es decir, el 24. | ch02 [5] |
| ficha | D94 | ch05 b9 | fecha_relato | «1989» (ch05 [8]) | **pasa** | La voz habla del fallo de 1988, pero nunca menciona el pago de 18,3 millones a 200 afectados en 1989. | — |
| descarte | D21 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice «En 1961 la producción subió», justo después de enumerar las advertencias. | ch03 [28] |
| descarte | D95 | — | voz_lo_dice | no dice 1.500 | **dicho** | La voz menciona la reclamación de 1.500 millones de dólares australianos por la tierra Banjima contra Australia Occidental. | ch07 [6] |

- fichas que quedan: 12/13 · cortadas por el verificador: ['T38'] · cortadas por el código: [] · vuelven: [] · motivos para una vuelta: 7

##### O2_1

| que | id | cap/beat | regla | token (dónde lo dice la voz) | veredicto | motivo del verificador | oración |
|---|---|---|---|---|---|---|---|
| ficha | D108 | ch01 b1 | no_dicho | «Australia» (ch01 [6]) | **pasa** | La voz nunca califica a Wittenoom como el peor desastre industrial de Australia; solo coincide la palabra 'Australia'. | — |
| ficha | D83 | ch02 b3 | no_dicho | «Australia» (ch02 [6]) | **pasa** | La voz menciona el acuerdo entre gobiernos, pero no su nombre (Operación Canguro) ni el año 1958; la ficha suma ambos datos. | — |
| ficha | D94 | ch05 b9 | fecha_relato | «1989» (ch05 [8]) | **pasa** | La voz cuenta el fallo de 1988, pero no el pago de 18,3 millones a 200 afectados en 1989; es un hecho nuevo. | — |
| descarte | D03 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice que el pueblo, la pista, los patios y la escuela estaban hechos con lo que sobraba de la mina. | ch03 [9] |
| descarte | D129 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice que con relaves se hicieron las carreteras, los patios y los espacios públicos. | ch03 [7] |
| descarte | T13 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice que en 1946 ya había diagnósticos de asbestosis. | ch03 [14] |
| descarte | D21 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice que en 1961 la producción subió, después de las advertencias que acaba de contar. | ch03 [28] |
| descarte | T27 | — | voz_lo_dice | no dice 3, 4 | **dicho** | La voz cuenta que, al instalarse los equipos, se recortó y restringió el suplemento salarial por polvo; omite la cifra. | ch03 [26] |
| descarte | D95 | — | voz_lo_dice | no dice 1.500 | **dicho** | La voz menciona la reclamación de mil quinientos millones de dólares australianos. | ch07 [6] |

- fichas que quedan: 13/13 · cortadas por el verificador: [] · cortadas por el código: [] · vuelven: [] · motivos para una vuelta: 5

##### O2_2

| que | id | cap/beat | regla | token (dónde lo dice la voz) | veredicto | motivo del verificador | oración |
|---|---|---|---|---|---|---|---|
| ficha | D108 | ch01 b1 | no_dicho | «Australia» (ch01 [6]) | **pasa** | La voz nunca califica a Wittenoom como el peor desastre industrial de Australia; solo coincide la palabra «Australia». | — |
| ficha | Q25 | ch02 b2 | spoiler | «2» (ch02 [7]) | **pasa** | La voz cita otra frase de María («Me pegué a mi marido…») y habla de su confianza, pero no dice que en España no tuvieran nada. | — |
| ficha | D94 | ch05 b9 | fecha_relato | «1989» (ch05 [8]) | **pasa** | La voz cuenta el fallo de 1988, pero no la indemnización de 1989 ni sus cifras; la ficha suma un hecho nuevo. | — |
| ficha | D23 | ch05 b10 | contradice | «30» (ch05 [18]) | **pasa** | El corte histórico de más de 500 muertos para 1989 no está en la voz; los «casi treinta años» de Daniel son otro hecho, y las cifras de ch06 (dos mil, más de cu | — |
| ficha | D23 | ch05 b10 | contradice | «2024» (ch07 [4]) | **pasa** | El corte histórico de más de 500 muertos para 1989 no está en la voz; los «casi treinta años» de Daniel son otro hecho, y las cifras de ch06 (dos mil, más de cu | — |
| descarte | D21 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice que en 1961 la producción subió, tras narrar las advertencias de 1944 a 1957. | ch03 [28] |
| descarte | D95 | — | voz_lo_dice | no dice 1.500 | **dicho** | La voz menciona la reclamación de mil quinientos millones de dólares australianos por la tierra Banjima contra Australia Occidental. | ch07 [6] |

- fichas que quedan: 12/13 · cortadas por el verificador: [] · cortadas por el código: [('T86', 'candado')] · vuelven: [] · motivos para una vuelta: 7

##### O3_1

| que | id | cap/beat | regla | token (dónde lo dice la voz) | veredicto | motivo del verificador | oración |
|---|---|---|---|---|---|---|---|
| ficha | D108 | ch01 b1 | no_dicho | «Australia» (ch01 [6]) | **pasa** | La voz nunca califica a Wittenoom como el peor desastre industrial de Australia; solo coincide la palabra «Australia». | — |
| ficha | Q25 | ch02 b2 | spoiler | «2» (ch02 [7]) | **pasa** | La voz cita otra frase de María («Me pegué a mi marido…»), pero no dice que en España no tuvieran nada. | — |
| ficha | T38 | ch02 b3 | spoiler | «1962» (ch02 [8]) | **corta** | La voz sitúa la boda el 20 de septiembre de 1962 y dice que cuatro días después estaban en el barco, es decir, el 24 de septiembre. | ch02 [5] |
| ficha | D94 | ch05 b9 | fecha_relato | «1989» (ch05 [8]) | **pasa** | La voz no menciona el pago de 18,3 millones de 1989 ni los 200 afectados; la ficha suma un hecho nuevo al fallo de 1988. | — |
| descarte | D03 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice que la pista y el pueblo entero estaban hechos con lo que sobraba de la mina. | ch03 [9] |
| descarte | D129 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice que con los relaves se hicieron las carreteras, los patios y los espacios públicos. | ch03 [7] |
| descarte | T13 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice que en 1946 ya había diagnósticos de asbestosis. | ch03 [14] |
| descarte | D21 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice «En 1961 la producción subió», tras enumerar las advertencias. | ch03 [28] |
| descarte | T27 | — | voz_lo_dice | no dice 3, 4 | **dicho** | La voz dice que, al instalarse los equipos contra el polvo, se recortó y restringió el suplemento salarial; omite la cifra en peniques. | ch03 [26] |
| descarte | D95 | — | voz_lo_dice | no dice 1.500 | **dicho** | La voz menciona la reclamación de mil quinientos millones de dólares australianos por la tierra Banjima. | ch07 [6] |

- fichas que quedan: 12/13 · cortadas por el verificador: ['T38'] · cortadas por el código: [] · vuelven: [] · motivos para una vuelta: 8

##### O3_2

| que | id | cap/beat | regla | token (dónde lo dice la voz) | veredicto | motivo del verificador | oración |
|---|---|---|---|---|---|---|---|
| ficha | Q25 | ch02 b2 | spoiler | «2» (ch02 [7]) | **pasa** | La voz nunca cita ni dice que en España no tuvieran nada; el «dos» coincide con los dos gobiernos del acuerdo migratorio, que es otro hecho. | — |
| ficha | D94 | ch05 b9 | fecha_relato | «1989» (ch05 [8]) | **pasa** | La voz cuenta el fallo de 1988, pero no menciona en ningún momento el pago de 18,3 millones a 200 afectados en 1989; la ficha suma un hecho nuevo. | — |
| descarte | D03 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice que la pista se hizo con relaves de la mina, y en idx9 que el pueblo entero también. | ch03 [6] |
| descarte | D129 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice que con relaves se hicieron las carreteras, los patios y los espacios públicos. | ch03 [7] |
| descarte | T13 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice que en 1946 ya había diagnósticos de asbestosis. | ch03 [14] |
| descarte | D21 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice que en 1961 la producción subió, después de narrar las advertencias previas. | ch03 [28] |
| descarte | T27 | — | voz_lo_dice | no dice 3, 4 | **dicho** | La voz cuenta que, tras instalar los equipos contra el polvo, se recortó y restringió el suplemento; solo omite los peniques. | ch03 [26] |
| descarte | D95 | — | voz_lo_dice | no dice 1.500 | **dicho** | La voz dice que la prensa habla de una reclamación de mil quinientos millones de dólares australianos por la tierra Banjima. | ch07 [6] |

- fichas que quedan: 11/13 · cortadas por el verificador: [] · cortadas por el código: [('D115', 'candado'), ('D102', 'candado')] · vuelven: [] · motivos para una vuelta: 8

##### S_1

| que | id | cap/beat | regla | token (dónde lo dice la voz) | veredicto | motivo del verificador | oración |
|---|---|---|---|---|---|---|---|
| ficha | D79 | ch01 b1 | no_dicho | «2000» (ch06 [7]) | **corta** | La voz da más adelante el recuento de muertos (el gobierno dejó de contar en dos mil, otras estimaciones más de cuatro mil); la ficha lo adelantaría con otra ve | ch06 [7] |
| ficha | D79 | ch01 b1 | spoiler | «2000» (ch06 [7]) | **corta** | La voz da más adelante el recuento de muertos (el gobierno dejó de contar en dos mil, otras estimaciones más de cuatro mil); la ficha lo adelantaría con otra ve | ch06 [7] |
| ficha | Q17 | ch04 b7 | spoiler | «2» (ch05 [4]) | **pasa** | La voz cuenta una explosión el primer día, pero nunca dice que las ambulancias fueran frecuentes; el «dos» y el «tres» coinciden hablando de otra cosa. | — |
| ficha | Q17 | ch04 b7 | spoiler | «3» (ch04 [14]) | **pasa** | La voz cuenta una explosión el primer día, pero nunca dice que las ambulancias fueran frecuentes; el «dos» y el «tres» coinciden hablando de otra cosa. | — |
| ficha | D94 | ch05 b9 | fecha_relato | «1989» (ch05 [8]) | **pasa** | La voz cuenta el fallo de 1988, pero no la indemnización de 1989 de 18,3 millones a 200 afectados. | — |
| ficha | D73 | ch06 b11 | no_dicho | «2.000» (ch06 [7]) | **pasa** | Los dos mil de la voz son el recuento oficial de muertos; los clientes de Peter Gordon no se mencionan. | — |
| ficha | D64 | ch06 b12 | spoiler | «2» (ch07 [9]) | **pasa** | La voz da tres millones de toneladas, pero no la comparación con el Melbourne Cricket Ground; la ficha la suma. | — |
| descarte | T13 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice que en 1946 ya había diagnósticos de asbestosis. | ch03 [14] |
| descarte | D21 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice «En 1961 la producción subió», después de las advertencias. | ch03 [28] |
| descarte | T27 | — | voz_lo_dice | no dice 3, 4 | **dicho** | La voz cuenta que, con los equipos contra el polvo, se recortó y restringió el suplemento salarial; solo omite los peniques. | ch03 [26] |
| descarte | T80 | — | voz_lo_dice | no dice Ministro, Desarrollo, Regional, Hon, Jon, Ford, MLC | **dicho** | La voz dice que hacia junio de 2007 Wittenoom fue abolido oficialmente; solo omite quién lo anunció. | ch06 [10] |
| descarte | D95 | — | voz_lo_dice | no dice 1.500 | **dicho** | La voz dice que la reclamación por la tierra Banjima es de mil quinientos millones de dólares australianos. | ch07 [6] |

- fichas que quedan: 10/13 · cortadas por el verificador: ['D79'] · cortadas por el código: [('D109', 'candado')] · vuelven: [] · motivos para una vuelta: 10

##### S_2

| que | id | cap/beat | regla | token (dónde lo dice la voz) | veredicto | motivo del verificador | oración |
|---|---|---|---|---|---|---|---|
| ficha | D79 | ch01 b1 | no_dicho | «2000» (ch06 [7]) | **corta** | La voz cuenta en ch06 el recuento de muertos (el gobierno dejó de contar en dos mil y otras estimaciones hablan de más de cuatro mil); la ficha lo adelantaría. | ch06 [7] |
| ficha | D79 | ch01 b1 | spoiler | «2000» (ch06 [7]) | **corta** | La voz cuenta en ch06 el recuento de muertos (el gobierno dejó de contar en dos mil y otras estimaciones hablan de más de cuatro mil); la ficha lo adelantaría. | ch06 [7] |
| ficha | D141 | ch05 b9 | spoiler | «2.5» (ch05 [4]) | **pasa** | La voz habla de razones económicas pero no da la cifra de pérdidas; el 2.5 coincide solo con los «dos años y medio» de los de Juan, que es otra cosa. | — |
| descarte | D21 | — | voz_lo_dice | no dice Wittenoom | **dicho** | La voz dice que en 1961 la producción subió. | ch03 [28] |
| descarte | D95 | — | voz_lo_dice | no dice 1.500 | **dicho** | La voz menciona la reclamación de mil quinientos millones de dólares australianos por la tierra Banjima. | ch07 [6] |

- fichas que quedan: 11/13 · cortadas por el verificador: ['D79'] · cortadas por el código: [('D115', 'candado')] · vuelven: [] · motivos para una vuelta: 9

#### Contra la tabla DEBERÍA de REVISION_CIEGA_F63.md §2 (para el analista)

Lo que el analista marcó bueno (DEBERÍA del beat) y el verificador **corta**:

- (ninguna)

Lo que el analista marcó flojo o malo y el verificador **pasa** (el verificador juzga el hecho, no la calidad: informativo):

- S_1: Q17 (ch04 b7, spoiler «2») → pasa: La voz cuenta una explosión el primer día, pero nunca dice que las ambulancias fueran frecuentes; el «dos» y el «tres» coinciden hablando de otra cosa.
- S_1: Q17 (ch04 b7, spoiler «3») → pasa: La voz cuenta una explosión el primer día, pero nunca dice que las ambulancias fueran frecuentes; el «dos» y el «tres» coinciden hablando de otra cosa.
- S_1: D73 (ch06 b11, no_dicho «2.000») → pasa: Los dos mil de la voz son el recuento oficial de muertos; los clientes de Peter Gordon no se mencionan.
- S_1: D64 (ch06 b12, spoiler «2») → pasa: La voz da tres millones de toneladas, pero no la comparación con el Melbourne Cricket Ground; la ficha la suma.

Fichas cortadas por el verificador que NO están en el DEBERÍA ni en lo marcado malo (ni bueno ni malo para el analista):

- (ninguna)

#### Contra los veredictos que el handoff espera (§Etapa 3, «Revisión del prompt por el analista»)

| id | que | regla | esperado | papeles donde hay marca | veredictos obtenidos |
|---|---|---|---|---|---|
| D79 | ficha | cualquiera | corta | S_1 (no_dicho «2000»); S_1 (spoiler «2000»); S_2 (no_dicho «2000»); S_2 (spoiler «2000») | corta, corta, corta, corta ✓ |
| D23 | ficha | cualquiera | pasa | O1_1 (contradice «30»); O1_1 (contradice «2024»); O2_2 (contradice «30»); O2_2 (contradice «2024») | pasa, pasa, pasa, pasa ✓ |
| D108 | ficha | cualquiera | pasa | O2_1 (no_dicho «Australia»); O2_2 (no_dicho «Australia»); O3_1 (no_dicho «Australia») | pasa, pasa, pasa ✓ |
| Q25 | ficha | cualquiera | pasa | O1_1 (spoiler «2»); O1_2 (spoiler «2»); O2_2 (spoiler «2»); O3_1 (spoiler «2»); O3_2 (spoiler «2») | pasa, pasa, pasa, pasa, pasa ✓ |
| D94 | ficha | fecha_relato | pasa | O1_1 (fecha_relato «1989»); O1_2 (fecha_relato «1989»); O2_1 (fecha_relato «1989»); O2_2 (fecha_relato «1989»); O3_1 (fecha_relato «1989»); O3_2 (fecha_relato «1989»); S_1 (fecha_relato «1989») | pasa, pasa, pasa, pasa, pasa, pasa, pasa ✓ |
| D141 | ficha | cualquiera | pasa | S_2 (spoiler «2.5») | pasa ✓ |
| D21 | descarte | cualquiera | dicho | O1_1; O1_2; O2_1; O2_2; O3_1; O3_2; S_1; S_2 | dicho, dicho, dicho, dicho, dicho, dicho, dicho, dicho ✓ |
| T80 | descarte | cualquiera | dicho | O1_1; S_1 | dicho, dicho ✓ |

Costo de la simulación: US$ 0.5036 (8 llamadas; estimado del handoff ≈ 0,5).


### Lectura de CC de la simulación

- 8/8 JSON al primer intento, 0 veredictos ignorados, 0 marcas sin veredicto. US$ 0,5036 (estimado ≈ 0,5), 7–15 s por llamada, ~10k tokens de entrada cada una (la narración entera + marcas).
- 64 marcas: 31 de fichas (26 fichas distintas marcadas) → 22 pasa · 4 corta; 33 descartes → 33 «dicho» · 0 «no_dicho».
- Los 8 veredictos que el handoff espera salieron: D79 **corta** en S_1 y S_2 (no_dicho y spoiler «2000» → ch06 [7]); D23 **pasa** las 4 veces que fue marcada `contradice` («30», «2024»); D108, Q25, D141 **pasa**; D94 **pasa** las 7 veces (`fecha_relato` «1989», relato 1988: «la ficha suma una consecuencia que la voz no dice»); D21 **dicho** en los 8 papeles; T80 **dicho** en los 2 donde fue duda.
- Las otras 2 «corta» son T38 (O1_1 y O2_1, spoiler «1962»): la voz da la boda el 20 de septiembre de 1962 y «cuatro días después» → el 24 está dicho. Es la ficha que el analista marcó «derivable, sirve como reloj, no como ficha»: el verificador coincide con él.
- Ninguna ficha del DEBERÍA del analista fue cortada. Lo que el analista marcó flojo y el verificador pasa (Q17, D73, D64 en S_1) es lo esperado: el verificador juzga el hecho, no la calidad.
- **Para mirar:** 33/33 descartes «dicho» y 0 «no_dicho» → `vuelven` quedó vacío en los 8 papeles. El código dudaba de todos (la voz no decía «Wittenoom», «CSR», una cifra); el verificador dice que el hecho principal sí está dicho en todos. En los dos casos que el handoff fijó (D21, T80) es lo correcto; los otros 31 no los revisó nadie a mano: si el verificador fuera indulgente con «dicho», el autor pierde candidatos que antes volvían. Lista entera en SIM_VERIFICADOR.md.
- Con el `validar` nuevo, los 8 papeles de F63 quedan con 10–13 fichas de 13 (O2_1: 13/13; lo que cae es por `caben`, `candado` o el verificador: D26/Q19 caben en O1_1, T86 candado en O2_2, D115/D102 candado en O3_2, D109 en S_1, D115 en S_2) y con 5–10 motivos para una vuelta, casi todos «beat sin su a_pantalla» (6 ids que la escaleta dejó para la pantalla) y picos sin ficha, no cortes; en F63 (solo intento 1, con los filtros viejos cortando) pasaban 6–10.

## Etapa 4 — Corrida real sobre Wittenoom (PARADA)

Antes de correr: `01e_pantalla.json/.md/.raw.json` del 29-oct 20:58 (Sonnet m01e-6, 4 intentos, 11 fichas, cierre «tope», US$ 0,70; el 6/10 de la revisión a ciegas) copiados a `lab/hyperframes/f64/antes/` (md5 f881bd32… / 417a93a0… / d6d84ba8…, iguales a los de `_steps`). Después `python -m script_engine.m01e_pantalla 123bbb64-9fca-4395-8bf4-57d60e219ef1` con el código de las etapas 0–3 (`7b48ebf`): la clave de caché cambió (m01e-7, Opus) → llamada nueva; escribió los tres archivos en `_steps` (15:35) y la corrida «pantalla» en `01_v3_costos.json` (US$ 1,3004, 211 s). **No** se aprobó el papel, no hubo voz, fotos ni `fase1_5`.

**Resultado:** 13 fichas de 13 (las seis `a_pantalla` de la escaleta —D01, D23, D34, D40, D51, D61— están todas en su beat), 8 sellos, 3 relojes, 62 descartados del autor; **cierre «sin motivos» después de 1 vuelta**; nada cortado por el código ni por el verificador en la validación final. Costo US$ 1,3004 = autor 1,1576 (intento 1 0,7135 + vuelta 1 0,4441) + verificador 0,1428 (2 llamadas). Fichas por beat: D108 · Q25 · D83 · D02 · D01 · D115 · Q19 · D102 · D51 · D23 · D34 · D40 · D61 (11 de 13 coinciden con el DEBERÍA del analista o con sus alternativas: D108 gancho, Q25, D83, D02, Q19, D102, D23; los seis `a_pantalla` los puso porque el motivo de la vuelta lo pidió).

**Intento 1** (in 88.647 · out 17.944 · US$ 0,7135 · JSON): 12 fichas; cayó D115 por `candado` («Australia» no está en el texto de D115: dice «australiano»; es el bug del candado literal que la revisión a ciegas anotó en §5) y 4 beats quedaron sin su `a_pantalla` (ch03 b5 D01, ch06 b11 D34, ch06 b12 D40, ch07 b13 D61: el autor los descartó como «cifra técnica» / «mejor leída que dicha»). Verificador (10 marcas, US$ 0,0685, 11,7 s): D108 `no_dicho` «Australia» → pasa; Q25 `spoiler` «2» → pasa; D23 `contradice` «30» y «2024» → pasa («el corte de más de 500 muertos para 1989 no aparece en la voz; los casi treinta años de Daniel hablan de otra cosa»); 6 descartes dudosos (D03, D129, T13, D21 «Wittenoom»; T27 «3/4»; D95 «1.500») → los 6 **dicho** → `vuelven` vacío. Motivos enviados: 5 (claves `(candado, D115, ch03, 6)`, `(a_pantalla, ch03, 5)`, `(a_pantalla, ch06, 11)`, `(a_pantalla, ch06, 12)`, `(a_pantalla, ch07, 13)`), beats que podía cambiar: ch03 b5 y b6, ch06 b11 y b12, ch07 b13.

**Vuelta 1** (in 95.768 · out 3.051 · US$ 0,4441 · JSON): 5 cambios aplicados, 0 ignorados: D115 reescrita (ahora pasa el candado), D01 en ch03 b5, D34 en ch06 b11, D40 en ch06 b12, D61 en ch07 b13. Verificador (11 marcas, US$ 0,0743, 13,7 s): las 4 del intento 1 otra vez pasa + D01 `spoiler` «3» (ch04 [14]) → pasa («los tres millones de toneladas de ch06 son relaves, otra cosa»); los mismos 6 descartes → dicho. Validación: 0 fichas fuera, 0 marcas cortadas, 0 picos vacíos, 0 `a_pantalla` vacíos → **motivos = [] → cierre «sin motivos»**. No hizo falta medir «sin progreso»: las claves de la vuelta 1 ({a_pantalla ×4, candado D115}) no se repitieron porque la validación siguiente no tuvo ninguna.

**El verificador en la corrida real:** 2 llamadas, 21 marcas, 7 veredictos de ficha (todos «pasa», coherentes con la simulación) y 12 de descarte (todos «dicho»). Otra vez 0 «no_dicho»: la observación 2 de «lo que queda abierto» vale también acá.

**Costo total de la tanda:** simulación 0,5036 + corrida real 1,3004 = **US$ 1,804** (estimado del handoff ≈ 2–3), más el gasto accidental de los tests declarado (≈ 0,6–0,9, estimado).


### Por intento / vuelta

| llamada | tokens in | tokens out | US$ | segundos | JSON |
|---|---|---|---|---|---|
| intento 1 | 88647 | 17944 | 0.7135 | 153.5 | sí |
| vuelta 1 | 95768 | 3051 | 0.4441 | 29.9 | sí |

Cierre: **sin motivos** después de 1 vuelta(s).

**Vuelta 1** · US$ 0.4441 · beats que podía cambiar: ch03 b5, ch03 b6, ch06 b11, ch06 b12, ch07 b13

- claves enviadas: (a_pantalla, ch03, 5); (a_pantalla, ch06, 11); (a_pantalla, ch06, 12); (a_pantalla, ch07, 13); (candado, D115, ch03, 6, None)
- motivos (texto que vio el autor):
  - D115 (ch03 beat 6) «1962, AÑO RÉCORD · El 95% del asbesto de Australia salió de Wittenoom»: candado: no están en el texto fuente de D115: ['Australia']
  - el beat 5 de ch03 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D01 («150.000 toneladas de asbesto comercial entre 1937 y 1966: cifra técnica de contexto.»)
  - el beat 11 de ch06 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D34 («Fuentes gubernamentales actuales: 'miles' de muertes sin total; se muestra junto a la estimación de Markey que sí dice la voz.»)
  - el beat 12 de ch06 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D40 («Superficie oficial de WAMA: 46.840 hectáreas; cifra administrativa con versiones en disputa, mejor leída que dicha.»)
  - el beat 13 de ch07 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D61 («Reconocimiento oficial de 2023 de que los estudios sobre la extensión quedaron desactualizados; va como documento fechado.»)
- aplicados: [{'cap': 'ch03', 'beat': 5, 'partes': ['ficha']}, {'cap': 'ch03', 'beat': 6, 'partes': ['ficha']}, {'cap': 'ch06', 'beat': 11, 'partes': ['ficha']}, {'cap': 'ch06', 'beat': 12, 'partes': ['ficha']}, {'cap': 'ch07', 'beat': 13, 'partes': ['ficha']}] · ignorados: 0

**Claves de la validación final** (las que, de haber otra vuelta, se compararían): ninguna → «sin motivos»

### Llamadas del verificador en la corrida real

| # | marcas | pasa | corta | dicho | no_dicho | tokens in/out | US$ | s | pedido_md5 | error |
|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 10 | 3 | 0 | 6 | 0 | 10139/1398 | 0.0685 | 11.7 | a728e755… | — |
| 2 | 11 | 4 | 0 | 6 | 0 | 10467/1621 | 0.0743 | 13.7 | 7242ccc0… | — |

### Log de la corrida

```
[15:31:57] INFO     | viral_pipeline | [cost_tracker] Tracking de costos iniciado para video: 123bbb64-9fca-4395-8bf4-57d60e219ef1
[15:35:28] INFO     | viral_pipeline | [cost_tracker] Video 123bbb64-9fca-4395-8bf4-57d60e219ef1 — Costo total: $1.3004
  m01e intento 1: in 88647 · out 17944 · US$ 0.7135 · JSON
  m01e verificador: 10 marca(s) → corta 0 · pasa 3 · dicho 6 · no_dicho 0 · US$ 0.0685
  m01e intento 1 validado: fichas fuera 1 · marcas 10 · cortadas por el verificador 0 · vuelven 0 · picos vacíos 0
  m01e intento 2: in 95768 · out 3051 · US$ 0.4441 · JSON
  m01e verificador: 11 marca(s) → corta 0 · pasa 4 · dicho 6 · no_dicho 0 · US$ 0.0743
  m01e vuelta 1 validada: fichas fuera 0 · marcas 11 · cortadas por el verificador 0 · vuelven 0 · picos vacíos 0
  m01e: 13 fichas · 8 sellos · 3 relojes → C:\CLAUDE_PROJECTS\automatization_videos\data\scripts\_steps\123bbb64-9fca-4395-8bf4-57d60e219ef1\01e_pantalla.md
exit 0
```

### `01e_pantalla.md` final, entero

#### Guion de pantalla en papel — 123bbb64-9fca-4395-8bf4-57d60e219ef1

`m01e_pantalla` m01e-7 (md5 del prompt `f2bfdf2044a4c77a59fc62ebe93966c2`) · claude-opus-5-5 medium · 2 intento(s) · US$ 1.3004 (autor 1.1576 + verificador 0.1428) · tokens de entrada 88647

Segundos por palabra 0.34 (mediana de 347 oraciones de 16 caps del narrador N9Z5MLTIaHFLflaLtbDi) · intento 1: in 88647 · out 17944 · US$ 0.7135 · intento 2: in 95768 · out 3051 · US$ 0.4441

Totales: 13 fichas · 8 sellos · 3 relojes · 62 descartados

#### ch01 — La herida que no cerraba

- beat 1 · gancho · PICO · ficha **D108** [normal] «LO QUE PASÓ AHÍ · El peor desastre industrial de la historia de Australia» en [7] sobre «pueblo» (70/71 car.) · respaldo: «considerada el peor desastre industrial en la historia de Australia» · año — / relato — · verificador: pasa (no_dicho {'no_dicho': ['Australia']}) — La voz nunca califica a Wittenoom como el peor desastre industrial de Australia; solo coincide la palabra «Australia» en el rótulo de lugar. · aporta: Pone en escala el pueblo borrado: la voz nunca dice que fue el peor desastre industrial del país. · sello **AMENAZA** en [1]
- relojes: —

#### ch02 — A la tierra roja

- beat 2 · planteo · ficha **Q25** [cita] «POR QUÉ SE FUERON · En España no teníamos nada, ninguno de los dos.» — María Bernal (autor: modelo) en [2] sobre «confiaba» (81/90 car.) · respaldo: «En España no teníamos nada, ninguno de los dos.» · año — / relato 1961 · verificador: pasa (spoiler {'spoiler': ['2']}) — La voz cita otra frase de María («Me pegué a mi marido…»); «En España no teníamos nada» no aparece en ninguna oración. · aporta: El motivo del viaje, que la voz no cuenta: no tenían nada en España. · sello —
- beat 3 · planteo · PICO · ficha **D83** [normal] «EL ACUERDO SE LLAMÓ · Operación Canguro, del franquismo, desde 1958» en [7] sobre «acuerdo» (64/90 car.) · respaldo: «Un acuerdo migratorio entre el franquismo y Australia iniciado en 1958, llamado Operación Canguro» · año 1958 / relato 1962 · aporta: Nombre, régimen y año del acuerdo que la voz menciona sin nombrar. · sello —
- relojes: 16 SEP 1961 en [0], 20 SEP 1962 en [4]

#### ch03 — Ignorar el veneno

- beat 4 · planteo · ficha **D02** [normal] «LO QUE TENÍAN ESOS RELAVES · Alrededor de un 5% de asbesto» en [6] sobre «relaves» (55/90 car.) · respaldo: «que contienen alrededor de un 5% de asbesto» · año — / relato 1962 · aporta: Cuánto asbesto quedaba en el material con que hicieron la pista y el pueblo. · sello —
- beat 5 · escalada · PICO · ficha **D01** [normal] «LO QUE SE SACÓ DE AHÍ · Unas 150.000 toneladas de asbesto de tres minas» en [12] sobre «mina» (68/90 car.) · respaldo: «aproximadamente 150.000 toneladas de asbesto de tres minas» · año 1937 / relato 1943 · verificador: pasa (spoiler {'spoiler': ['3']}) — La voz no da el tonelaje extraído ni el número de minas; los tres millones de toneladas de ch06 son relaves, otra cosa. · aporta: Cuánto asbesto se sacó de esas minas, cifra que la voz nunca da. · sello **AVISO** en [17]
- beat 6 · giro · ficha **D115** [normal] «1962, RÉCORD DE ASBESTO DEL PAÍS · El 95% salió de Wittenoom» en [31] sobre «año» (57/90 car.) · respaldo: «En 1962, el año de máxima producción australiana de asbesto, se extrajeron 18416 toneladas cortas, de las cuales el 95% era crocidolita de Wittenoom.» · año 1962 / relato 1962 · aporta: Daniel llega en el año de máxima producción, y casi todo salía de esa mina. · sello **INMINENTE** en [31]
- relojes: —

#### ch04 — El juego peligroso

- beat 7 · escalada · PICO · ficha **Q19** [cita] «EL PELIGRO · Nadie nos avisó de nada.» — Víctor Calvo (autor: modelo) en [9] sobre «miedo» (51/51 car.) · respaldo: «Nadie nos avisó de nada.» · año — / relato 1962 · aporta: El cierre del testimonio que la voz omite: a los chicos nadie les advirtió. · sello —
- beat 8 · giro · ficha **D102** [normal] «ESE BEBÉ, HOY · Conocido productor de televisión» en [13] sobre «Daniel» (45/51 car.) · respaldo: «Daniel Écija (hijo), nacido en Wittenoom, tiene 63 años y es un conocido productor de televisión en España.» · año — / relato 1963 · aporta: Quién es hoy el recién nacido, dato que la voz nunca da. · sello **CALMA** en [18]
- relojes: 7 JUL 1963 en [15]

#### ch05 — Wittenoom por dentro

- beat 9 · escalada · ficha **D51** [normal] «LO QUE SACÓ LA MINA · 131.000 toneladas; más de 100.000 exportadas» en [1] sobre «cierre» (63/71 car.) · respaldo: «La mina de Wittenoom produjo 131.000 toneladas de crocidolita, de las cuales más de 100.000 toneladas fueron exportadas.» · año 1966 / relato 1966 · aporta: Lo que la mina produjo y exportó hasta el cierre que la voz atribuye a costos. · sello **ALARMA** en [6]
- beat 10 · pico · PICO · ficha **D23** [papel] «NO ERA EL PRIMERO · Más de 500 muertos de Wittenoom hasta 1989» en [12] sobre «mesotelioma» (59/76 car.) · respaldo: «Para 1989, más de 500 antiguos trabajadores y residentes de Wittenoom habían muerto por infecciones relacionadas con el asbesto.» · año 1989 / relato 1991 · verificador: pasa (contradice {'contradice': ['30', '2024']}) — El corte histórico de más de 500 muertos para 1989 no lo dice la voz; los dos mil y cuatro mil de ch06 son totales de hoy, no lo contradicen. · aporta: Cuando diagnostican a Daniel ya había más de 500 muertos de ese pueblo. · sello **MEMORIA** en [11]
- relojes: —

#### ch06 — El polvo viaja

- beat 11 · respiro · ficha **D34** [normal] «LO QUE ADMITE EL GOBIERNO · Miles de muertos: mineros, vecinos y visitantes» en [7] sobre «gobierno» (72/90 car.) · respaldo: «han provocado miles de muertes entre mineros, residentes y visitantes» · año — / relato 2000 · aporta: El propio gobierno reconoce miles de muertos, visitantes incluidos. · sello **SILENCIO** en [9]
- beat 12 · revelacion · PICO · ficha **D40** [normal] «LO QUE MIDE LA ZONA PROHIBIDA · 46.840 hectáreas» en [13] sobre «zona» (45/90 car.) · respaldo: «cubre una superficie de 46.840 hectáreas» · año — / relato 2007 · aporta: El tamaño de la zona declarada no apta, que la voz no dice. · sello **RABIA** en [19]
- relojes: —

#### ch07 — La herida ancestral

- beat 13 · cierre · PICO · ficha **D61** [papel] «UN SUBCOMITÉ OFICIAL, EN 2023 · Los informes ya no sirven; la contaminación se extendió» en [7] sobre «sitio» (84/90 car.) · respaldo: «Un Subcomité de Wittenoom determinó en 2023 que todos los informes sobre el alcance de la contaminación ya no son aplicables y que la contaminación se ha extendido.» · año 2023 / relato 2026 · aporta: El propio Estado admitió que ya no sabe hasta dónde llega la contaminación. · sello —
- relojes: —

#### Lo que cayó

- (nada)

#### Verificador

- 2 llamada(s) · US$ 0.1428 · marcas de la última validación: 11
- llamada 1: 10 marca(s) → fichas pasa 3 · corta 0 · descartes dicho 6 · no_dicho 0 · US$ 0.0685 · 11.7 s · pedido a728e755…
- llamada 2: 11 marca(s) → fichas pasa 4 · corta 0 · descartes dicho 6 · no_dicho 0 · US$ 0.0743 · 13.7 s · pedido 7242ccc0…
  - D108 (ch01 beat 1, [7]) «LO QUE PASÓ AHÍ · El peor desastre industrial de la historia de Australia»: no_dicho «Australia» en ch01 [6] («Wittenoom, Australia Occidental, 1963.»)
  - Q25 (ch02 beat 2, [2]) «POR QUÉ SE FUERON · En España no teníamos nada, ninguno de los dos.»: spoiler «2» en ch02 [7] («No iban solos: cerca de ocho mil españoles cruzaron por un acuerdo entre los dos»)
  - D01 (ch03 beat 5, [12]) «LO QUE SE SACÓ DE AHÍ · Unas 150.000 toneladas de asbesto de tres minas»: spoiler «3» en ch04 [14] («Tres meses antes, en marzo, Milagros Barroso había dado a luz en el mismo pueblo»)
  - D23 (ch05 beat 10, [12]) «NO ERA EL PRIMERO · Más de 500 muertos de Wittenoom hasta 1989»: contradice «30» en ch05 [18] («Nueve meses después del diagnóstico, Daniel Écija murió en Madrid, a miles de ki»)
  - D23 (ch05 beat 10, [12]) «NO ERA EL PRIMERO · Más de 500 muertos de Wittenoom hasta 1989»: contradice «2024» en ch07 [4] («Maitland Parker murió de mesotelioma en 2024.»)
  - descarte D03 («Los desechos de asbesto se utilizaron en la construcción de la ciudad de Wittenoom, la pista de aterrizaje y otras instalaciones.»; el autor: «Que la pista y el pueblo se hicieron con relaves lo dice la voz.»; la voz de ch03 no dice ['Wittenoom'])
  - descarte D129 («En Wittenoom se usaban los relaves, residuos del procesamiento del asbesto, como superficie para carreteras y para cubrir patios y lugares públicos.»; el autor: «Los relaves en carreteras y patios los dice la voz.»; la voz de ch03 no dice ['Wittenoom'])
  - descarte T13 («Se diagnosticó un primer caso de asbestosis en Wittenoom. (fecha 1946)»; el autor: «La asbestosis de 1946 la dice la voz.»; la voz de ch03 no dice ['Wittenoom'])
  - descarte D21 («La producción minera en Wittenoom se incrementó en 1961 a pesar de la evidencia de los riesgos.»; el autor: «El aumento de producción en 1961 lo dice la voz.»; la voz de ch03 no dice ['Wittenoom'])
  - descarte T27 («El subsidio por polvo se redujo a 3 o 4 peniques y se restringió a ciertas áreas, tras la instalación de equipo para reducir el polvo. (fecha 1957)»; el autor: «El recorte del suplemento lo dice la voz.»; la voz de ch03 no dice ['3', '4'])
  - descarte D95 («El pueblo aborigen banjima reclama 1.500 millones de dólares australianos al Ejecutivo por la contaminación.»; el autor: «Los 1.500 millones los dice la voz.»; la voz de ch07 no dice ['1.500'])

#### Reintento: los motivos que se le mandaron al autor

- D115 (ch03 beat 6) «1962, AÑO RÉCORD · El 95% del asbesto de Australia salió de Wittenoom»: candado: no están en el texto fuente de D115: ['Australia']
- el beat 5 de ch03 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D01 («150.000 toneladas de asbesto comercial entre 1937 y 1966: cifra técnica de contexto.»)
- el beat 11 de ch06 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D34 («Fuentes gubernamentales actuales: 'miles' de muertes sin total; se muestra junto a la estimación de Markey que sí dice la voz.»)
- el beat 12 de ch06 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D40 («Superficie oficial de WAMA: 46.840 hectáreas; cifra administrativa con versiones en disputa, mejor leída que dicha.»)
- el beat 13 de ch07 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D61 («Reconocimiento oficial de 2023 de que los estudios sobre la extensión quedaron desactualizados; va como documento fechado.»)

##### Reintento parcial: 1 vuelta(s)

#### Vuelta 1 · US$ 0.4441

- beats que podía cambiar: ch03 beat 5, ch03 beat 6, ch06 beat 11, ch06 beat 12, ch07 beat 13
- motivos:
  - D115 (ch03 beat 6) «1962, AÑO RÉCORD · El 95% del asbesto de Australia salió de Wittenoom»: candado: no están en el texto fuente de D115: ['Australia']
  - el beat 5 de ch03 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D01 («150.000 toneladas de asbesto comercial entre 1937 y 1966: cifra técnica de contexto.»)
  - el beat 11 de ch06 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D34 («Fuentes gubernamentales actuales: 'miles' de muertes sin total; se muestra junto a la estimación de Markey que sí dice la voz.»)
  - el beat 12 de ch06 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D40 («Superficie oficial de WAMA: 46.840 hectáreas; cifra administrativa con versiones en disputa, mejor leída que dicha.»)
  - el beat 13 de ch07 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D61 («Reconocimiento oficial de 2023 de que los estudios sobre la extensión quedaron desactualizados; va como documento fechado.»)
- claves: (a_pantalla, ch03, 5); (a_pantalla, ch06, 11); (a_pantalla, ch06, 12); (a_pantalla, ch07, 13); (candado, D115, ch03, 6, None)
- aplicados: ch03 beat 5 (ficha), ch03 beat 6 (ficha), ch06 beat 11 (ficha), ch06 beat 12 (ficha), ch07 beat 13 (ficha)

#### Cierre del reintento

- cerró por: **sin motivos** (después de 1 vuelta)

#### Descartados por el modelo

- D85 [voz_lo_dice]: La herida que no cerraba la cuenta la voz en ch01 idx3.
- T34 [voz_lo_dice]: El baile y su fecha los dice la voz.
- T37 [voz_lo_dice]: La boda y su fecha las dice la voz.
- Q13 [voz_lo_dice]: La amistad con Milagros y Ramón está parafraseada en ch02 idx8.
- T38 [voz_lo_dice]: La partida cuatro días después de la boda la dice la voz.
- Q14 [voz_lo_dice]: La voz cita el testimonio de Calvo sobre el viaje.
- T36 [voz_lo_dice]: La llegada en agosto de 1962 la dice la voz.
- T24 [voz_lo_dice]: Los viajes de reclutamiento desde 1950 los dice la voz.
- Q27 [voz_lo_dice]: La voz cita casi todo; el resto no cabe en las oraciones afines.
- D82 [otro]: La distancia a Perth está en disputa entre fuentes.
- D03 [voz_lo_dice]: Que la pista y el pueblo se hicieron con relaves lo dice la voz. — verificador: dicho: La voz dice que la pista y el pueblo estaban hechos con lo que sobraba de la mina.
- Q44 [voz_lo_dice]: La voz cita al extrabajador.
- D129 [voz_lo_dice]: Los relaves en carreteras y patios los dice la voz. — verificador: dicho: La voz dice que con los relaves se hicieron las carreteras, los patios y los espacios públicos.
- D92 [voz_lo_dice]: La advertencia escrita de Saint en 1948 la dice la voz (ch03 idx19).
- Q45 [voz_lo_dice]: La voz lee la carta de Saint.
- Q46 [voz_lo_dice]: La voz cita a Saint; el resto no suma más que D44.
- Q53 [voz_lo_dice]: La voz cita al defensor del empleador.
- D19 [voz_lo_dice]: El informe de 1944 lo dice la voz.
- T13 [voz_lo_dice]: La asbestosis de 1946 la dice la voz. — verificador: dicho: La voz dice que en 1946 ya había diagnósticos de asbestosis.
- T06 [voz_lo_dice]: La compra de 1943 la dice la voz.
- D21 [voz_lo_dice]: El aumento de producción en 1961 lo dice la voz. — verificador: dicho: La voz dice que en 1961 la producción subió, tras narrar las advertencias.
- Q54 [voz_lo_dice]: La voz lee el acta de la Junta.
- T27 [voz_lo_dice]: El recorte del suplemento lo dice la voz. — verificador: dicho: La voz dice que con los equipos se recortó y restringió el suplemento salarial por polvo; omite la cifra en peniques.
- D20 [voz_lo_dice]: La voz resume ese documento.
- T35 [voz_lo_dice]: El primer caso de mesotelioma fuera de Sudáfrica lo dice la voz.
- Q49 [voz_lo_dice]: La voz cita a McNulty.
- D138 [otro]: Buen dato, pero en el beat 6 sumaba más D115 (récord de 1962 sobre la llegada de Daniel).
- Q16 [voz_lo_dice]: La voz cuenta la explosión del primer día.
- D104 [voz_lo_dice]: Las jornadas de 16 horas las dice la voz.
- T39 [voz_lo_dice]: El nacimiento de John Patrick lo dice la voz.
- T40 [voz_lo_dice]: El nacimiento de Daniel en junio lo dice la voz.
- T41 [voz_lo_dice]: El bautizo y la partida los dice la voz.
- D87 [voz_lo_dice]: Los diez meses en Wittenoom los dice la voz.
- T49 [voz_lo_dice]: El cierre por costos lo dice la voz.
- T47 [voz_lo_dice]: El regreso a Madrid en 1966 lo dice la voz.
- D88 [voz_lo_dice]: Los dos años y medio de los De Juan los dice la voz.
- T51 [voz_lo_dice]: El regreso de los De Juan en 1971 lo dice la voz.
- D27 [voz_lo_dice]: La reducción del pueblo desde 1978 la dice la voz.
- D93 [voz_lo_dice]: El fallo de 1988 lo dice la voz.
- T56 [voz_lo_dice]: La fundación de la sociedad en 1979 la dice la voz.
- T64 [voz_lo_dice]: El diagnóstico y la muerte los dice la voz.
- D89 [voz_lo_dice]: Los 55 años y los nueve meses los dice la voz.
- Q35 [otro]: La parte que la voz no dice no cabe en 71 caracteres sin perder sentido.
- Q24 [voz_lo_dice]: La voz cita al policía.
- Q21 [voz_lo_dice]: La voz cita a Mercedes.
- Q33 [voz_lo_dice]: La voz parafrasea a Markey.
- D34 [otro]: «Miles» sin total suma menos que el testimonio de la excursión escolar.
- D10 [voz_lo_dice]: El asbesto que baja al Fortescue lo dice la voz.
- T90 [voz_lo_dice]: Las fibras fuera de la zona en 2021 las dice la voz.
- D59 [voz_lo_dice]: No asegurar los relaves por costo lo dice la voz.
- Q07 [voz_lo_dice]: La voz cita al gobierno.
- Q03 [voz_lo_dice]: La voz cita la declaración.
- D40 [otro]: Superficie administrativa con cifras en disputa; en el pico va el dato central.
- D61 [otro]: Se superpone con las fibras fuera de zona que ya dice la voz.
- T98 [voz_lo_dice]: La demanda de Gordon Legal la dice la voz.
- Q10 [voz_lo_dice]: La voz cita a Parker.
- T92 [voz_lo_dice]: La visita de Orellana la dice la voz.
- T96 [voz_lo_dice]: La muerte de Parker la dice la voz.
- D95 [voz_lo_dice]: Los 1.500 millones los dice la voz. — verificador: dicho: La voz menciona la reclamación de mil quinientos millones de dólares australianos.
- D70 [voz_lo_dice]: Que no se gastó en remediar lo dice la voz.
- Q34 [voz_lo_dice]: La voz cita al gobierno.
- D01 [otro]: Cifra técnica de contexto; en el beat 5 sumaba más D44.


## Costo real por llamada

| qué | llamadas | US$ |
|---|---|---|
| simulación (verificador, 8 papeles de F63) | 8 | 0.5036 |
| corrida real: autor (intento 1 + vueltas) | 2 | 1.1576 |
| corrida real: verificador | 2 | 0.1428 |
| accidente declarado: la 1.ª corrida de la suite vieja antes del blindaje llamó al verificador real (tests que llaman `validar` sin `juez`; Opus medium, narración de Vajont/Kyshtym/video chico) | ≈ 12–14 (estimado: 98 s de suite, no quedó registro: `hx._track` sin video activo va a `session_overhead`, que no se persiste) | ≈ 0,6–0,9 (estimado) |
| **total de la tanda** | | **1.8040** + ≈ 0,6–0,9 (estimado) (estimado del handoff ≈ 2–3) |

## Lo que queda abierto

1. **Fase 2 vuelve a correr los filtros por tokens sin el juicio del papel.** §2.3 pedía borrar `juicio` de `pantalla_filtros` y así se hizo. Consecuencia: `pantalla_colocar → validar_papel → no_dicho/spoiler` y el chequeo 5 de `gfx_guion` (`contradicciones`) corren en Fase 2 sobre las fichas del papel SIN saber lo que el verificador decidió. Una ficha que el verificador salvó (D23 «500» frente a «30», D94 1989, D108 «Australia») puede caer en Fase 2 por la misma coincidencia de token que el papel ya juzgó. Hasta F63 `juicio_autor` protegía eso. Propuesta para el analista: que Fase 2 reciba `juicio_verificador.tokens` donde recibía `juicio_autor` (`pantalla_entrada.py:142`, `pantalla_colocar.py:196`, `gfx_guion.py:275/283/493`, y `_sin_juicio` de vuelta en `pantalla_filtros`), o que esos tres filtros dejen de correr en Fase 2 para fichas con `juicio_verificador`. No se tocó: no está en el handoff y no se corrió Fase 2 (PARADA).
2. **El verificador dijo «dicho» a los 33 descartes dudosos de la simulación** (0 «no_dicho»). D21 y T80 eran los esperados; los otros 31 no tienen revisión humana. Si es indulgencia del SYSTEM («aunque omita un detalle…»), el autor pierde candidatos que antes volvían. Para mirar en SIM_VERIFICADOR.md y en la corrida real.
3. **Sin tope, sin freno.** Las vueltas cierran por claves; una corrida con motivos nuevos en cada vuelta (el autor cambia de ficha cada vez) sigue pagando ≈ US$ 0,75 por vuelta + verificador. No hay tope por diseño (DECISIONES 13:07); el costo se informa. Si hace falta un límite de vueltas (no de dólares), es otra decisión.
4. **Gasto accidental declarado:** la primera corrida de los tests viejos (antes del blindaje) llamó al verificador real ≈ 12–14 veces, ≈ US$ 0,6–0,9 estimado; no quedó registro persistente. Los tests quedaron blindados (juez falso en `_juez_por_defecto` y en `pantalla_verificador.verificar`).
5. **Tests saltados por falta de Vajont en disco** (6): `data/scripts/_steps/f8s3-vajont` no está en esta máquina; los `@hay_vajont` de f37a/f38a_voz/f36c no se verificaron (ya se saltaban antes de F64).
6. **D83 ya pasaba** con la regla vieja (la vecina dice 1962): la fila del handoff estaba mal en «hoy»; con la nueva también pasa.
7. **`ficha_caso.json` ausente** no frena: `disputas = {}` y una línea en el log; los temas viejos sin ficha pierden esa parte de la entrada (declarado por el handoff).
8. **Lo que no se corrió:** aprobar el papel, voz, fotos, `fase1_5`, Fase 2. El papel de Wittenoom quedó pisado (el de hoy no estaba aprobado; respaldo en `lab/hyperframes/f64/antes/`). Sigue la PARÁ de F62: nada después del guion corre sin la aprobación de Omar.

## Veredicto de revisor-handoff (íntegro)

**VEREDICTO: CUMPLE CON OBSERVACIONES**

Todo lo que pude recalcular da. Quedan dos puntos que no pude comprobar (hook de commits y el conteo de la suite) y un riesgo de diseño que el reporte ya declara.

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | md5 SYSTEM del autor 85d094be… | OK | `md5(m.PANTALLA_SYSTEM)` = 85d094bed6090b14d1802ca97433d982, recalculado. |
| 2 | Solo cambia la oración 2 del primer párrafo | OK | Los demás párrafos son idénticos a PRUEBA1_prompt_rotulos.md. La oración 2 es la de HANDOFF_F63 l.59, con "Escribís…" intacto. |
| 3 | md5 USER Wittenoom 018f9cc1… | OK | `entrada_md5(entrada(cargar(...), vocabulario_clima()))` = 018f9cc1b939e2afdcfad5eb5ebcc36f. Esto fija también el orden de claves (a)-(e). |
| 4 | SYSTEM_V y FORMATO_V literales del handoff | OK | `SYSTEM_V in handoff` y `FORMATO_V in handoff`: ambos True, comparados sobre el texto con CRLF normalizado. |
| 5 | Etapa 0: MODELO/EFFORT/PROMPT_VERSION; L como "nombre — rol"; flash_forward | OK | claude-opus-5-5, medium, m01e-7. `flash_forward` está en `ent["beats"]` y `_para_modelo` lo quita (m01e_pantalla.py:285-293). |
| 6 | Etapa 1: sin tope | OK | El grep de TopePantalla, _peor_usd, confirmados, juicio_autor, cortados_al_cierre y _pregunta_txt en script_engine y fase1_5 solo deja la palabra "juicio" en docstrings. |
| 7 | `costos` fuera de gfx_config | OK | gfx_config.py:335 solo lo menciona en un comentario. |
| 8 | error_handler `delay=True` | OK | error_handler.py:71. |
| 9 | Etapa 2: regla de `momentos` | OK | m01e_pantalla.py:322-348. Máximo por cap, flash_forward fuera, heredado no entra al máximo. `heredado` solo se actualiza si el cap dijo un año. La tabla de ETAPA2_relato.md coincide con la lógica. |
| 10 | Etapa 3: una sola llamada al juez, en el orden pedido | OK | m01e_pantalla.py:544-546. Está después del loop y de `vuelven`, y antes de `picos_vacios` (l.579), `a_pantalla_vacios` (l.582) y `motivos` (l.592). |
| 11 | Lo que corta va con `quien:"verificador"`, sale del slot y de `usados_ids` | OK | l.559-568. |
| 12 | "Sin progreso" por claves contra todas las vueltas | OK | `vistas` guarda todas las vueltas previas (l.1005-1016). |
| 13 | Caché por `pedido_md5` y "caché parcial" | OK | l.912-930. |
| 14 | Simulación con el `validar` de producción, sin importar etapa_a_papel | OK | `sim_verificador.py` importa solo m01e_pantalla y pantalla_verificador, y llama `m.validar(resp, ent, juez=juez)`. |
| 15 | Los 8 veredictos esperados del handoff | OK | En SIM_VERIFICADOR.md: Q25, D94, D23 y D108 "pasa"; D21 y T80 "dicho"; D79 "corta" (l.114). No grepé D141 por separado. |
| 16 | Costo | OK | Suma de sim/*.json = 0,50359. El raw de producción da usd 1,30037 (autor 1,15756 + verificador 0,14281). Total 1,804 = lo informado. |
| 17 | Nada específico de Wittenoom en el código | OK | Solo aparece en un docstring de historia (l.171) y en el ejemplo literal de FORMATO_V. |
| 18 | Tests | OK | Corrí test_module_f64 más los f36c, f37a, f38a (m01e y voz), f38c, f38d, f38e_c, f38e_d y f40: 77 pasados, 6 saltados (sin Vajont en disco). No toqué nada. |
| 19 | Un commit por etapa | OK | 0e849f4, f82f35b, 4ec3102 y 7b48ebf, todos con prefijo `feat(m01e): F64`. |
| 20 | Hook de la suite rápida en cada commit | NO VERIFICABLE | No hay registro del hook en el repo. Habría que ver la salida del hook de cada commit. |
| 21 | Main no se tocó | OK | main sigue en 43f528a, ancestro de HEAD. |
| 22 | Papel no aprobado | OK | `01e_pantalla.json` no tiene clave `aprobado` y no hay marca de aprobación en `_steps`. |
| 23 | Reporte con "lo que queda abierto" y PARADA | PARCIAL | F64_REPORT.md tiene la sección (8 ítems), pero "Veredicto" sigue en "(pendiente)" (l.579). Es el espacio de este veredicto. |

Fuera de alcance: ninguno.
- El working tree tiene solo DECISIONES.md, diag_234_cap4.py y f28a.log modificados, los tres ya sucios en el snapshot inicial.
- Lo demás sin seguimiento (f64/antes, etapa4_run.log, F64_REPORT.md) es lo declarado.
- La corrida real pisó 01e_pantalla.{json,md,raw.json} de producción. data/ está en .gitignore y el original quedó respaldado en lab/hyperframes/f64/antes/.

Observaciones:
1. El reporte dice "suite del papel 105 verdes" y yo conté 77 con los 10 archivos del papel. Puede haber otros archivos en la suite rápida; no pude cotejarlo.
2. Interpretaciones de CC, todas aceptables:
   - El `flash_forward` quitado del USER por `_para_modelo` es necesario, porque el handoff pide a la vez agregarlo a los beats y mantener el md5 018f9cc1.
   - El dedupe de la marca spoiler en el gancho evita doble marca sobre la misma coincidencia, y el comportamiento de corte no cambia.
   - D83 ya pasaba: el handoff se equivocó en la columna "hoy", y CC lo declaró.
3. El gasto accidental (≈US$ 0,6–0,9, estimado, sin registro) viola "NO llamar API" en los tests. Está declarado y los tests quedaron blindados con un juez falso, pero el monto es una estimación que nadie puede auditar. Omar debería saberlo.
4. Borrar `juicio` deja a Fase 2 (`pantalla_colocar`, `gfx_guion` chequeo 5) corriendo los filtros por token sin el veredicto del verificador. Eso lo pedía §2.3 y CC lo declaró como abierto #1. Aceptable ahora, pero es una regresión posible: una ficha salvada en el papel puede caer en Fase 2 por el mismo token.
5. En la corrida real el verificador cortó 0 y dijo "dicho" a todos los descartes dudosos de la simulación (33 de 33). Con un 0/33, no se sabe si el SYSTEM es indulgente o si los filtros marcan de más. Está declarado como abierto #2.

Riesgos que el contrato no cubre:
- No hay límite de vueltas ni de dólares: si el autor cambia de ficha en cada vuelta, el costo crece (≈US$ 0,75 por vuelta más el verificador).
- El papel nuevo de Wittenoom pisó el del 29-oct (con respaldo), pero ninguna persona lo calificó: la PARADA depende de que nadie corra `--aprobar-papel` por inercia.
- La rama sigue con mucho archivo sin seguimiento ajeno a F64 (_lab_*, _probe_*), que no se tocó.

### Adenda de CC
- **Obs. 1 (105 vs 77):** los 105 incluyen, además de los 10 archivos del papel que corrió el revisor, `test_module_f38e_e.py`, `test_module_f37b_colocar.py` y `test_module_f39_fase1.py` (28 tests más), que también tocan m01e/fase1_5; con los mismos 10 archivos del revisor el conteo es 77 + 6 saltados, el mismo que el suyo.
- **Req. 20 (hook):** el hook `suite_rapida` bloquea el commit si la suite rápida (f25c, f24, f21) está en rojo; los 4 commits salieron, lo que es la única evidencia posible (el hook no deja registro en el repo). El commit de cierre pasa por el mismo hook.
- **Obs. 3:** compartida; el monto es estimado (≈ 12–14 llamadas de Opus medium con la narración de Vajont/Kyshtym, ≈ US$ 0,05–0,07 cada una); va en el reporte, en ESTADO y en el mensaje a Omar.
- **Obs. 4 y 5:** compartidas; son los abiertos 1 y 2 del reporte. Para el 5, la corrida real sumó 12 descartes más, también todos «dicho» (45/45 en total).
- **Req. 15 (D141):** está en la tabla «Contra los veredictos que el handoff espera» de SIM_VERIFICADOR.md: S_2 (spoiler «2.5») → pasa ✓.
