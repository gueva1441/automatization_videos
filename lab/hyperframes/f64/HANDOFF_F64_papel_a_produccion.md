# HANDOFF F64 — El papel a producción: Opus + entrada completa, sin tope, y el verificador decide los cortes

Rama `f11-guion-v4` (HEAD `b9979f6`). Modelo para CC: **Opus medium**. Subagentes en paralelo donde el trabajo lo permita (una etapa por subagente cuando tocan funciones distintas; las pruebas y la auditoría final siempre en paralelo). Sin sesión nueva.

## 0. Por qué esta tanda y no otra
- ¿Construye sobre código que ya decidimos reemplazar? No: `m01e_pantalla.py` sigue siendo el módulo del papel. Lo que se reemplaza (y se **borra**) es su mecanismo de «preguntas al autor» con `confirmados`/`final` (F37 §A.4, F38d §A.1): desde hoy las coincidencias las juzga el verificador, no el autor en una vuelta.
- ¿Alguna decisión de hoy cambia el orden? Sí: las tres de DECISIONES 2026-10-31 (13:07 tope, 14:16 modelo/entrada, 14:20 verificador) van juntas porque todas tocan `llamar`/`validar`; separarlas costaría tres pasadas por el mismo código. Después de esta tanda sigue el verificador **de la narración** (ENTRADA 31b §3.3), que es otro módulo y otra tanda.
- Qué midió F63 (`lab/hyperframes/f63/REVISION_CIEGA_F63.md`): a ciegas, Sonnet 6,3 · Opus medium hoy 7,8 · **Opus medium completa 8,8** · Opus high 8,3. En los 8 papeles los filtros cortaron 24 fichas y las 24 eran buenas.

## 1. Constantes (todo número con origen)
| valor | origen | quién |
|---|---|---|
| `MODELO = "claude-opus-5-5"`, `EFFORT = "medium"` | DECISIONES 2026-10-31 14:16 | Omar |
| SYSTEM del autor: oración 2 reemplazada por la de F63 A.2 (md5 del SYSTEM resultante `85d094bed6090b14d1802ca97433d982`) | `lab/hyperframes/f63/etapa_a_papel.py` l.54-63, medido en F63 | Omar (14:16: «entrada completa») |
| USER del autor sobre Wittenoom = md5 `018f9cc1b939e2afdcfad5eb5ebcc36f` | `tabla_a.json` → `cabecera.user_md5_completa` (F63) | derivado: chequeo que para |
| `PROMPT_VERSION = "m01e-7"` | siguiente al `m01e-6` | derivado |
| Tope en dólares del papel: **no existe** | DECISIONES 2026-10-31 13:07 | Omar |
| Verificador de fichas: `claude-opus-5-5`, `medium`, **una** llamada por validación con todas las fichas marcadas | DECISIONES 2026-10-31 14:20 | Omar |
| `MAX_TOKENS` del verificador = `hx.MAX_TOKENS` (el de todas las llamadas) | existente en `claude_helpers` | existente |
| Reintento del verificador sin JSON: 1 | igual que `dicho_verificador.REINTENTOS` (F55 A.2) | existente |
| Año del relato = máximo año dicho por la voz en el cap hasta la oración (incluida), sin contar oraciones de beats con `flash_forward: true`; mientras el cap no dijo ninguno, el valor del cap anterior (heredado, que **no** entra al máximo) | regla general de esta tanda (§Etapa 2), reemplaza «el último año que dijo la voz» de F37 §A.1b | analista → Omar la ve acá |
| Cabecera esperada de la entrada completa de Wittenoom: `archivo = 362` (D155 · T98 · Q50 · P35 · L24), `chars_user = 199691` | `tabla_a.json` → `cabecera` (F63) | derivado |
| Cierres de las vueltas: «sin motivos», «sin progreso», «sin JSON», «sin beat» | DECISIONES 13:07 (se va «tope») + F38d §A.1 | Omar |
| Costo esperado de la tanda ≈ US$ 2–3 (8 llamadas del verificador en la simulación ≈ 0,5; corrida real de Wittenoom ≈ 0,72 × (1 + vueltas) + verificador) | derivado de F63 (`tabla_a.json`) y del tamaño del pedido del verificador | informado, no frena |

Ningún otro número nuevo. Nada específico de Wittenoom entra al código.

## 2. Módulos que toca (qué hace hoy → qué hará)
1. `script_engine/m01e_pantalla.py` — el papel: entrada, llamada al autor, validación, vueltas, markdown. → Opus + entrada completa; sin tope; año del relato por máximo; las coincidencias van al verificador; se borran `confirmados`/`final`/`juicio`.
2. `script_engine/pantalla_verificador.py` — **nuevo**: arma el pedido con todas las fichas marcadas, llama una vez a Opus, lee los veredictos. Puro en `pedido()`, llamada en `verificar()`, igual que `dicho_verificador`.
3. `fase1_5.py` (`run_pantalla`, `_step_cost`), `gfx_config.py` (clave `costos` del perfil) — hoy atrapan `TopePantalla` / aceptan `costos.m01e_tope_usd` → se quita lo del tope. `script_engine/pantalla_filtros.py`: `grep -n juicio` — si `contradicciones_de`/`no_dicho`/`spoiler` leen `juicio` (F38c), se borra el parámetro y su lectura; si solo m01e lo pasa, se deja de pasar.
4. Pruebas: `test_module_f36c_pantalla.py`, `test_module_f37a_papel.py`, `test_module_f38a_m01e.py`, `test_module_f38a_voz.py`, `test_module_f38c_papel.py`, `test_module_f38d_vueltas.py`, `test_module_f38e_c.py` → se adaptan; las que prueban el tope, `_peor_usd`, `confirmados`, `cortados_al_cierre` o «¿es el mismo hecho?» se **borran** (lo viejo se borra con sus tests): `grep -ln "tope\|_peor_usd\|confirmados\|cortados_al_cierre\|es el mismo hecho" test_module_f3*.py` las encuentra.
5. Antes de tocar nada, CC corre `grep -rn "m01e_pantalla\.\(validar\|llamar\|momentos\|TopePantalla\|tope_usd\|_peor_usd\|OUT_TOKENS_PEOR\|confirmados\|cortados_al_cierre\)\|from script_engine.m01e_pantalla import" --include=*.py .` y lista en el reporte cada llamador (fase1_5, gfx_realizador, pantalla_colocar, tests, lab). Los runners de F63 (`lab/hyperframes/f63/*.py`) quedan como historia: no se adaptan ni se importan.

Más de 3–4 módulos: los de 3 y 4 son borrados y adaptaciones, no lógica nueva. La lógica nueva vive en 1 y 2.

## 3. Etapas (cada una termina con su salida en texto; un commit por etapa)

### Etapa 0 — Opus medium y la entrada completa (`m01e_pantalla.py`)
Portar a producción lo que `lab/hyperframes/f63/etapa_a_papel.py` hizo en lab:
- `_tipo` deja de filtrar: todo ítem del pool entra al archivo por `_kind` (D/T/Q/P/**L**), como `_tipo_todo` (l.101-103). Se borra la condición `numeros(ev.text_of(it))` (es la que escondía D85, D34, D03, D129, D10, D20, D70).
- Cada ítem lleva `contexto_fuente` (l.106-111); un L se escribe «nombre — rol» (l.126-127).
- Los beats de la entrada llevan además `emocion`, `imagen_sensorial`, `pregunta_abierta`, `paga` (l.131-134).
- `_para_modelo` suma `escaleta_video` (promesa_gancho, loops, recuerda_loop, pico, humano, antagonista, cierre_humano; l.135-136) y `disputas` (`versiones` + `contradicciones` de `ficha_caso.json`; l.137-138). `cargar` lee `ficha_caso.json` del directorio del topic; si no existe, `disputas = {}` y una línea en el log.
- `PANTALLA_SYSTEM`: la oración 2 del primer párrafo se reemplaza byte a byte por `ORACION2_DESPUES` (l.57-63). `MODELO`, `EFFORT`, `PROMPT_VERSION` según la tabla.
- `estilo_de` y `voz_no_lo_dice` ya toleran ids L (no empiezan con Q ni P); verificar con un test que un L propuesto como ficha sale `normal`.
- **Orden de claves del JSON (el md5 depende de esto; así lo armó el lab):** (a) en cada ítem del archivo, `contexto_fuente` va **al final**, después de `beats_que_lo_cuentan` / `autor` / `rol` / `testimonio` / `a_pantalla`; (b) en cada beat, `emocion, imagen_sensorial, pregunta_abierta, paga` van **después** de `cierre`, en ese orden; (c) en `_para_modelo`, `escaleta_video` y después `disputas` van **después** de `clima`; (d) `escaleta_video = {k: esc.get(k)}` con los 7 campos en el orden promesa_gancho, loops, recuerda_loop, pico, humano, antagonista, cierre_humano, con `None` donde falte; (e) el texto de un L es `f"{nombre} — {rol}".strip(" —")` (se pisa después de armar el ítem como los demás).

**Chequeos que paran:** `md5(PANTALLA_SYSTEM) == 85d094be…`; sobre `123bbb64-…` con los archivos de producción de hoy (`01b_narracion_v3.json` md5 `c7badfbe260f5eb24a47e780b40406b5`), `md5(pedido(ent)) == 018f9cc1b939e2afdcfad5eb5ebcc36f`. Si no da, PARÁ y mostrá el diff de claves entre el USER nuevo y el `body` de `lab/hyperframes/f63/a/O2_1.raw.json`.
**Salida en texto:** las dos líneas de md5 y la cabecera `{archivo: 362 (D155·T98·Q50·P35·L24), caps: 7, beats: 13, chars_user: 199691}`. Sin llamadas al modelo.

### Etapa 1 — Borrar el tope (`m01e_pantalla.py`, `fase1_5.py`, `gfx_config.py`)
Se borran: `TOPE_USD_RESPALDO`, `tope_usd()`, `TopePantalla`, el argumento `tope` de `llamar`, `out["tope"]`, `_peor_usd`, `OUT_TOKENS_PEOR`, `salida_peor`, el cierre `"tope"` y el `raise TopePantalla`; en `armar`/`a_markdown` el campo y la línea «tope US$»; en `fase1_5.py` l.237 y en `main()` el `except` queda solo con `SinJSON`; en `gfx_config.py` la clave `costos` sale de `_PROFILE_KEYS` y de la validación l.437-439 si no la usa nadie más (`grep -rn "costos" --include=*.py .` fuera de m05_judge, que es otra cosa). El perfil fuera de git: si trae `costos.m01e_tope_usd`, el validador del perfil lo reporta como clave desconocida; Omar la borra a mano (una línea en el reporte diciéndolo).
**Salida en texto:** `grep -rn "tope" script_engine/m01e_pantalla.py fase1_5.py` vacío (salvo docstrings históricos que se reescriben), y la lista de tests borrados (`test_0_tope_usd_se_lee_del_perfil` y los de `_peor_usd`/tope en `test_module_f38d_vueltas.py`).

### Etapa 2 — El año del relato (`momentos`, `m01e_pantalla.py` l.290-302)
Hoy: «el último año que la voz dijo» (literal, arrastra entre caps). Falla medida: ch05 [13] recuerda «1962» dentro de 1991 → el filtro cree que el relato va por 1962 y corta D23 en [18]; ch06 [2] arrastra ese 1962 y corta T57 (1985).
Nuevo: por cap, el **máximo** año dicho en el cap hasta la oración (incluida), **sin contar** las oraciones de beats con `flash_forward: true` en la escaleta (el gancho que salta al final); mientras el cap no dijo ninguno, el valor del cap anterior. **El valor heredado no entra al máximo:** en cuanto el cap dice su primer año, el relato es el máximo de los años de ese cap solamente (ch03 [11] = 1962 heredado de ch02 → [12] «En 1943» = 1943; si se hiciera `max(heredado, años del cap)` ch03 quedaría clavado en 1962 y el filtro moriría ahí). `entrada()` ya tiene el beat de cada oración; agregar `flash_forward` a los beats de `ent["beats"]` (dato de la escaleta, no regla nueva).
Simulado por el analista sobre Wittenoom (años en cifras; `anios_dichos` también lee letras, así que CC lo repite con la función real):

| ficha | año | ancla | relato hoy | relato nuevo |
|---|---|---|---|---|
| D23 | 1989 | ch05 [18] | 1962 → corta | 1991 → pasa |
| D23 | 1989 | ch05 [12] | 1991 → pasa | 1991 → pasa |
| T57 | 1985 | ch06 [2] | 1962 → corta | 1991 → pasa |
| D94 | 1989 | ch05 [8] | 1988 → corta | 1988 → marca (la decide el verificador, Etapa 3) |
| D83 | 1958 | ch02 [7] («…desde 1950») | 1950 → corta | 1962 → pasa (el auditor la agregó: hoy el «1950» final de la oración baja el relato) |

Ninguna ficha que hoy pasa en los 8 `.raw.json` de F63 pasa a cortarse con la regla nueva (el analista lo corrió sobre los 8). ch01 queda sin año de relato (su único año, 1963, es del beat flash-forward) → `None` → el filtro no actúa en el gancho, que es lo correcto: el gancho puede traer cualquier dato del archivo (regla del SYSTEM). CC verifica si `anios_dichos` lee «dos mil» de ch06 [7] como 2000 (relato 2000 en [7]–[9]: no es absurdo, pero cambia respecto a hoy) y lo anota.
**Salida en texto:** la misma tabla, calculada con `anios_dichos`, más una fila por cada oración de Wittenoom donde el relato nuevo ≠ el viejo.

### Etapa 3 — El verificador decide los cortes (`pantalla_verificador.py` nuevo + `validar`/`llamar`)
**Qué cambia en `validar`:** `no_dicho`, `spoiler`, `contradice` y (nuevo) `fecha_relato` dejan de cortar y dejan de preguntarle al autor: cada coincidencia es una **marca** (`marcas`: pool_id, cap, beat, sentence_idx, oracion_ancla, etiqueta, texto, respaldo, regla, `coincidencia: {token, cap, idx, oracion}`). `fecha_relato` marca solo donde hoy cortaría (mismas exenciones de l.617: testimonio, `dice_anio(anio, vecinas)`), con `coincidencia = {token: str(anio), relato: ahora, cap, idx: la oración donde la voz dijo el año máximo, oracion}`. Los descartes del autor «voz_lo_dice» que `voz_no_lo_dice` pone en duda (`vuelven`) también son marcas, de regla `voz_lo_dice`, con `caps_que_lo_cuentan` (o `["todo el video"]` si está vacío, como hoy l.498).
`validar(resp, ent, *, juez=None)`: `juez: Callable[[list[dict], list[dict]], dict]` recibe `(marcas, ent["caps"])` y devuelve lo que devuelve `pantalla_verificador.verificar` (`{veredictos_fichas, veredictos_descartes, …}`); por defecto `verificar`; las pruebas pasan uno falso. **Dónde entra:** una sola llamada, después del loop de fichas y de calcular `vuelven`, y **antes** de `picos_vacios`, `a_pantalla_vacios` y `motivos`. Ficha «corta» → sale del slot (`slot["ficha"] = None`) y de `usados_ids`, y va a `desc` con `que: "ficha"`, `quien: "verificador"`, su `regla` original y el `motivo` del verificador (así entra a `motivos` y a `fichas_fuera`); ficha «pasa» → queda, con `juicio_verificador: {regla, motivo}`; descarte «no_dicho» → sigue en `vuelven`; «dicho» → el descarte queda como el autor lo escribió, sin la marca «falso». Todo filtro `quien == "validación"` pasa a `quien in ("validación", "verificador")` (`a_markdown` «Lo que cayó» l.1068, `_por_que_falta` l.1019). Sin marcas, no se llama al verificador.
Se **borran**: `confirmados`, `final`, `juicio` (también en `pantalla_filtros`, §2.3), `_confirmar`, `_acumular`, `juicio_autor`, `_respuestas`, `preguntas`/`pregunta` en la ficha, `_pregunta_txt` («¿es el mismo hecho? si no, mantenelo»), `cortados_al_cierre` (en `armar` l.994-996, `a_markdown` l.1098-1107 y sus tests), y en `a_markdown` la línea `juicio_autor` (l.1055) y el bloque «Preguntas y respuesta del autor» (l.1076-1078). `cierre_final` se reemplaza por `cerrar(papel, val, por)` que pone `rt["cierre"] = por`, `out["final"] = papel`, `out["validacion"] = val` y escribe el raw: ya no hay una validación distinta al cerrar. `candado`, `caben`, `anclaje`, `formato`, `respaldo`, `cita_sin_fecha`, `una_vez`, `sello` siguen cortando en código: son candados de Omar (lock literal, una por beat, cabe en la oración), no juicios de hecho.
**Vueltas (`llamar(ent, out_dir, *, post=None, juez=None, log=None)`):** igual que F38d sin el tope: motivos = fichas cortadas (código + verificador) + `vuelven` + picos vacíos + `a_pantalla` vacíos; `juez` se pasa a cada `validar` (por defecto `functools.partial(pantalla_verificador.verificar, post=post, log=log)`). **«Sin progreso» por clave estable, no por texto** (el `motivo` del verificador es prosa y cambia entre llamadas aunque corte lo mismo): cada motivo lleva `clave = (regla, pool_id, cap, beat, token)` (el descarte que vuelve: `("voz_lo_dice", pool_id)`; pico vacío: `("pico", cap, beat)`; a_pantalla vacío: `("a_pantalla", cap, beat)`); hay vuelta mientras el conjunto de claves no sea igual al de **ninguna** vuelta anterior (no solo la inmediata: evita el ciclo A→B→A). El texto con el `motivo` del verificador se le manda al autor igual. Cierres: «sin motivos» / «sin progreso» / «sin JSON» / «sin beat». Si el verificador no devuelve JSON en dos intentos: las marcas de esa validación quedan «pasa» con `juicio_verificador: {motivo: "sin veredicto"}` y una línea en el log; no se corta a ciegas y no se frena el pipeline (la revisión del papel las ve).
**Caché:** el raw del papel guarda cada pedido y respuesta del verificador (`verificador: [{pedido_md5, marcas, veredictos, usage, usd, segundos}]`). En el hit de caché (`llamar` l.826-829 re-corre `validar`), `validar` se corre con un `juez` que busca en `prev["verificador"]` por `pedido_md5` y devuelve los veredictos guardados; si el `pedido_md5` no está (el código de `validar` cambió), se llama al verificador y se anota «caché parcial» en el log. Nunca se paga una llamada del verificador por un raw cuya clave coincide y cuyo `pedido_md5` está guardado.

**`pantalla_verificador.py`:**
```python
MODELO = "claude-opus-5-5"   # DECISIONES 2026-10-31 14:20
EFFORT = "medium"
REINTENTOS = 1               # como dicho_verificador (F55 A.2)
```
`pedido(marcas, caps) -> str` (puro): el USER es un JSON con `caps` (cap, oraciones [{idx, texto}]: la narración entera, la misma del autor), `fichas` [{pool_id, cap, beat, sentence_idx, oracion_ancla, etiqueta, texto, respaldo, dato_archivo, regla, coincidencia: {token, cap, idx, oracion}}] y `descartes` [{pool_id, dato_archivo, motivo_del_autor, caps_que_lo_cuentan}] + `"\n\nFormato de salida: " + FORMATO_V`. En una ficha de cita (Q), `dato_archivo` es la frase que la ficha muestra (su `texto`) y el testimonio entero va en `cita_completa`; en las demás, `dato_archivo` es el `texto` del ítem. `_leer(resp, marcas) -> dict` (puro) lee los veredictos: uno cuyo `(pool_id, cap, beat)` (o `pool_id` en descartes) no está en las marcas se ignora y se anota; una marca sin veredicto queda «pasa» (o «no_dicho») con motivo «sin veredicto».

SYSTEM, literal:
```
Sos el verificador de un documental de historia oscura en español. El rotulista propuso fichas (textos cortos en pantalla sobre una oración de la narración) y el código marcó en cada una una coincidencia con la voz: una palabra o un número que la voz también dice, una cifra distinta para algo parecido, o una fecha posterior al momento del relato. Las palabras y los números coinciden; vos decidís si coincide el hecho.

Recibís la narración completa del video (oraciones numeradas por capítulo), las fichas marcadas y, aparte, los datos que el rotulista descartó porque «la voz lo dice» y el código duda.

Para cada ficha, un veredicto:
- «pasa»: la voz no dice ese hecho en la oración ancla ni en las vecinas (la anterior y la siguiente), no lo cuenta más adelante en el video y no dice lo contrario. Que una palabra o un número coincidan hablando de otra cosa no cuenta. Que la ficha tenga fecha posterior al momento del relato no es motivo por sí solo. Una cifra con su propia fecha (un corte histórico: «para 1989, más de 500») no es la misma cifra que un total de hoy: ni lo contradice ni lo adelanta. Si la ficha suma algo que la voz no dice (una cifra, un nombre, una consecuencia), pasa aunque comparta parte del hecho.
- «corta»: la voz dice ese mismo hecho (con las mismas palabras o con otras) en la oración ancla o en una vecina; o lo cuenta más adelante en el video, en ese capítulo o en los siguientes, y la ficha lo adelantaría; o la voz da, para la misma cosa y el mismo momento, otra cifra u otra versión.
En una cita (Q), el hecho es la frase que la ficha muestra, no el testimonio entero: que la voz cite otra frase de la misma persona no cuenta.

Para cada descarte, un veredicto: «dicho» si alguna oración de los capítulos indicados dice el hecho principal del dato (con las mismas palabras o con otras; dicho como promesa, pregunta o adelanto también cuenta; aunque omita un detalle como quién lo anunció o la cifra exacta), o «no_dicho» si ninguna lo dice. Si `caps_que_lo_cuentan` dice «todo el video», cualquier oración cuenta.

Juzgá por el hecho, no por el estilo ni por si la ficha es buena. Devolvé solo JSON con el formato pedido, con un `motivo` de una línea por veredicto y, cuando cortás o decís «dicho», el cap y el idx de la oración de la voz que lo dice o lo contradice.
```
```
FORMATO_V = '{"fichas": [{"pool_id": "D23", "cap": "ch05", "beat": 10, "veredicto": "pasa" | "corta", "motivo": "…", "oracion": {"cap": "ch05", "idx": 12} | null}], "descartes": [{"pool_id": "D21", "veredicto": "dicho" | "no_dicho", "motivo": "…", "oracion": {"cap": "ch03", "idx": 28} | null}]}'
```
`verificar(marcas, caps, *, post=None, log=None) -> dict` llama como `llamar.autor` (body con `system`, `messages`, `output_config.effort`, `hx._post`, `hx.cost_of`, `hx._track(…, "m01e_verificador")`), lee con `primer_json`, y devuelve `{veredictos_fichas, veredictos_descartes, usage, usd, segundos, pedido_md5, intentos}`. Un veredicto cuyo `(pool_id, cap, beat)` no está en las marcas se ignora y se anota; una marca sin veredicto queda «pasa» con motivo «sin veredicto».

**Revisión del prompt por el analista, sobre casos reales de F63 (lo que espero que devuelva):**
- D79 «Más de 2000 muertos» en ch01 [7], marca `no_dicho` por «2000» en ch06 [7] («dejó de contar en dos mil… más de cuatro mil»: un conteo de muertos, el mismo hecho, con otra cifra y más adelante) → **corta**. Es el veredicto correcto; el filtro de tokens acertó por la razón equivocada.
- D23 «para 1989, más de 500 muertos» en ch05 [12] frente al mismo ch06 [7] → es un corte histórico con su fecha, no el total de hoy → **pasa** (la oración del SYSTEM sobre «cifra con su propia fecha» existe para esto: D79 y D23 se parecen y piden veredictos opuestos).
- D108 «peor desastre industrial de Australia» en ch01 [7], marca `no_dicho` por «Australia» ([6] «Australia Occidental») → la voz nunca dice que sea el peor desastre → **pasa**.
- Q25 «En España no teníamos nada» en ch02 [2], marca `spoiler` por «2» ([7] «los dos gobiernos») → **pasa**.
- D94 «CSR pagó 18,3 M a 200 afectados en 1989» en ch05 [8], marca `fecha_relato` (relato 1988) → la voz nunca cuenta el pago → **pasa**.
- D23 «más de 500 muertos para 1989» en ch05 [12], marca `contradice` (500 vs «30», «2024») → otra cosa → **pasa**.
- D141 «pérdidas 2,5 millones» en ch05 [2], marca `spoiler` por «2.5» (ch05 [4] «dos años y medio») → **pasa**.
- Descarte D21 «la voz dice que la producción subió en 1961», marca «la voz no dice Wittenoom» → ch03 [28] lo dice → **dicho**.
- Descarte T80 «la voz cuenta la abolición», marca «no dice Jon Ford» → el hecho principal (el pueblo fue abolido oficialmente) está en ch06 [10]; el nombre del ministro es un detalle → **dicho** (no vuelve). Coherente con la revisión a ciegas (T80 era la ficha floja de 6 de 8 papeles): si el autor quiere el nombre del ministro, lo propone como ficha y la juzga la regla (a) del SYSTEM del autor, no este descarte.
- Descarte con `caps_que_lo_cuentan = ["todo el video"]` (un `a_pantalla` que no es dato de ningún beat): cualquier oración cuenta.

**Simulación obligatoria antes de la corrida real (lab, `lab/hyperframes/f64/sim_verificador.py`):** tomar las 8 respuestas del autor de `lab/hyperframes/f63/a/*_[12].raw.json` (clave `respuesta`), validarlas con el `validar` nuevo (entrada completa de la Etapa 0 con `cargar`/`entrada`/`_para_modelo` de producción; verificador real; **nunca** importar de `etapa_a_papel`, que monkeypatchea `_tipo` y llama a `validar` con la firma vieja) y escribir `lab/hyperframes/f64/SIM_VERIFICADOR.md`: por papel, cada marca con regla, token, veredicto y motivo; totales (marcas, pasa, corta, dicho, no_dicho); costo y segundos por llamada. 8 llamadas en paralelo. Comparar con la tabla DEBERÍA de `REVISION_CIEGA_F63.md` §2: lo que yo marqué como bueno y el verificador corta, o al revés, va en una lista aparte para el analista. Costo ≈ US$ 0,5, se informa.
**Salida en texto:** `SIM_VERIFICADOR.md` entero.

### Etapa 4 — Corrida real sobre Wittenoom (PARADA al final)
Antes de correr: copiar `01e_pantalla.json/.md/.raw.json` de hoy a `lab/hyperframes/f64/antes/` (es la referencia 6/10 de la revisión a ciegas). Después `python -m script_engine.m01e_pantalla 123bbb64-9fca-4395-8bf4-57d60e219ef1` con el código de las etapas 0–3 (la clave de caché cambia por `PROMPT_VERSION`/`MODELO`: llamada nueva). Escribe `01e_pantalla.json/.md/.raw.json` en `_steps` (el papel de hoy no estaba aprobado; se pisa). **No** se aprueba (`--aprobar-papel` no se toca), no se genera voz ni fotos, no se corre `fase1_5`.
**Salida en texto:** `01e_pantalla.md` entero + por intento/vuelta: tokens, US$, segundos, claves de motivos enviadas y por qué no fue «sin progreso», cierre; llamadas del verificador con costo; costo total de la tanda.

### Chascada (sin costo, mismo commit de la Etapa 1)
`error_handler.py` l.68: el `FileHandler` se crea al importar y deja `logs/pipeline_<fecha>.log` vacíos en cada import (`pytest`, lab, revisión). Pasar a `logging.FileHandler(log_file, encoding="utf-8", delay=True)`: el archivo se crea en el primer `emit`. Mismo comportamiento cuando sí se escribe; cero archivos vacíos. Test: importar el módulo en un proceso nuevo no crea archivo en `logs/`.

## 4. Pruebas
- Suite rápida verde en cada commit (hook).
- Nuevas: `test_module_f64.py`: (a) `pedido()` del verificador puro y estable (md5 fijo sobre marcas de juguete; una Q lleva `dato_archivo` = frase de la ficha y `cita_completa`); (b) `_leer` de veredictos: desconocido se ignora, faltante = pasa «sin veredicto»; (c) `validar` con juez falso: una marca «corta» va a descartados con `quien: "verificador"` y sale de `usados_ids`, una «pasa» queda con `juicio_verificador`; un descarte «no_dicho» queda en `vuelven`, uno «dicho» no; sin marcas el juez no se llama; (d) `momentos` nuevo: cap con recuerdo de un año anterior, cap sin año que hereda, el heredado no entra al máximo, beat flash-forward ignorado; (e) la entrada completa trae L, `contexto_fuente`, `escaleta_video`, `disputas`, y un `ficha_caso.json` ausente no rompe; (f) `llamar` con `post` y `juez` falsos: sin tope, cierre «sin motivos» y «sin progreso» por claves (dos vueltas con el mismo conjunto de claves y motivos de texto distinto cierran; ciclo A→B→A cierra), verificador llamado una vez por validación con marcas; (g) hit de caché con `pedido_md5` guardado: el juez real no se llama.
- Borradas con su lógica: las de tope, `_peor_usd`, `confirmados`, `final`, «¿es el mismo hecho?».

## 5. Reporte (`lab/hyperframes/f64/F64_REPORT.md`)
Por etapa: diff resumido, salida en texto, tests. Tabla de costo real por llamada (autor, verificador, simulación). `SIM_VERIFICADOR.md`. `01e_pantalla.md` final. Sección «lo que queda abierto» (obligatoria, aunque sea «nada»). Veredicto íntegro del subagente `revisor-handoff` contra este archivo. `lab/ESTADO_SESION.md` actualizado. Commits `feat(m01e): F64 <etapa>` en `f11-guion-v4`; `main` no se toca.

## 6. Candados
Lock literal (`candado` sigue en código) · una ficha por beat · `caben` en código · el verificador nunca propone fichas, solo juzga · nada específico de Wittenoom en el código · sin topes en dólares · `main` intacta · PARADA al final de la Etapa 4 sin aprobar el papel.
