# F38e §D — Borrar la fecha-hora del segundo 0 (salida en texto)

Base: HEAD `8f7d9cd` (A, B, C y E ya commiteadas). DECISIONES 2026-10-27 11:21 («se quita definitivamente … fuera del código, con su plantilla, tests y chequeo; el video arranca con la primera imagen») y 2026-10-26 16:38 / 18:17 («borrar, no apagar»). Sin flags, sin ramas muertas, sin números nuevos, nada hardcode de Vajont. Nada en `data/` salvo el ledger del cost_tracker. Sin `--aprobar-guion`, sin render, sin fase3. Sin `git add` ni commit (los hace el principal).

## 1. grep antes / después

- Antes: `grep_antes.txt` (88 líneas: 25 en `fase2b.py`, 23 en `m01e_pantalla.py`, 22 en `voz_datos.py`, 6 en `gfx_guion.py`, 6 en `gfx_layer.py`, 4 en `pantalla_entrada.py`, 2 en `gfx_project.py` (docstring del recorte: «tarjeta» en el sentido de la tarjeta del recorte, no la del segundo 0; se reescribió «recorte» para que el grep quede en cero), 5 `.pyc` y 3 de `zod` en `gfx_runtime/node_modules` (ajeno); tests: `f34`, `f36`, `f36c_pantalla`, `f38a_m01e`, `f38a_voz`, `f38e_c2`).
- Después: `grep_despues.txt`. `grep -rn tarjeta script_engine/ fase2b.py` → **vacío** (fuera de `gfx_runtime/node_modules/zod`, «número de tarjeta de crédito», ajeno). Se borró también el `.pyc` huérfano `script_engine/__pycache__/gfx_rotulista.cpython-311.pyc` (el módulo no existe desde F37; era lo único binario que todavía matcheaba).
- `grep -rln tarjeta test_module_*.py` después: `f38a_m01e.py` y `f38a_voz.py` solo por el nombre del handoff viejo `HANDOFF_F38_reintento_tarjeta_juez` en la línea 2 del docstring (un nombre de archivo, no la función), y `test_module_f38e_d.py` (el test que busca la palabra).

## 2. Archivos tocados / creados / borrados

Código (todos CRLF, verificados con `file`):
- `script_engine/voz_datos.py` (−173 líneas): fuera `tarjeta_inicial`, `tarjeta_de_voz`, `horas_dichas`, `_numero_de`, `_hora_item` y las constantes del reloj de 12/24 h (`_HORAS_DIA`, `_MIN_HORA`, `_MIN_FRAC`, `_TARDE`, `_PARTE_DIA`, `_ANTES_HORA`) que solo ellas usaban (grep en todo el repo: ningún otro llamador, ni en tests); `from datetime import date` (solo lo usaba `tarjeta_de_voz`); docstring de cabecera y encabezado de sección. Queda `_entero` (lo usa `fechas_completas`).
- `script_engine/m01e_pantalla.py` (−52/+14): fuera `tarjeta()`, las claves `tarjeta`/`tarjeta_motivo` de `armar`, la línea «**Tarjeta:**» y el conteo «1 tarjeta / sin tarjeta» de `a_markdown`, el `tarjeta {bool}` del log de `generar`, la clave `_escaleta` de `entrada` (solo la leía `tarjeta()`; `_pool` queda, lo usa `validar`), la rama `{tarjeta: …}` de `editar` y las tres líneas de docstring/comentario. `editar` ahora **rechaza** una edición que no traiga `ficha` ni `sello`: `ValueError("edición sin ficha ni sello (claves [...]): solo se edita ficha o sello de un beat")` — genérico (no nombra la tarjeta: no queda rama muerta), antes del lookup del beat para que el motivo sea claro en vez de «no hay beat None en None».
- `script_engine/pantalla_entrada.py`: fuera `rot["tarjeta"]` (inicialización y lectura del papel) y dos docstrings.
- `script_engine/gfx_layer.py`: fuera el bloque `if plan.is_first:` que armaba `resolved["tarjeta_inicial"]` desde `rot["tarjeta"]` + `vd.tarjeta_inicial` (8 líneas) y el log; docstring (paso 3) y comentario.
- `script_engine/gfx_guion.py`: el cuadro de la intro queda fijo «primer cuadro congelado, sin voz»; fuera el evento «tarjeta fecha-hora» (7 líneas) y el chequeo 11 (5 líneas); los chequeos del papel pasan de «12–14» a «11–13» en el comentario.
- `script_engine/gfx_project.py`: solo docstring de `archive_head_px` («tarjeta» del recorte → «recorte»).
- `fase2b.py` (−85/+10): fuera `_intro_de`, `_ff_ruta` (solo lo usaba `_filtro_tarjeta`), `_filtro_tarjeta` (escribía `_tarjeta.txt`), `_pad_tarjeta`; el parámetro `tarjeta` y sus ramas en `_mix_music_into_video` (el `v_pad` vuelve a `tpad … start_mode=clone`, primer cuadro congelado, como antes de F36 B.9) y en `_mix_music_audio_only` (el `_pad.ts` siempre es el primer cuadro clonado); `_mezcla_preview` usa `INITIAL_SILENCE_SEC` directo; en `main` desaparece `intro_s` y se pasa `INITIAL_SILENCE_SEC` donde se usaba (música alineada ×2, mezcla ×2); la ayuda de `--plan-edit` sin «o {tarjeta: {texto}|null}»; 3 comentarios.

Tests editados (CRLF salvo `f38e_c2`, que ya era LF):
- `test_module_f34.py`: **borrado** `test_a6_tarjeta_vajont_y_falta_si_no_hay_certeza` (probaba `vd.tarjeta_inicial`); docstring.
- `test_module_f36.py`: **borrado** `test_b9_la_tarjeta_reemplaza_la_intro` (probaba `_intro_de`, `_pad_tarjeta` y `_tarjeta.txt`); en su lugar `test_b9_la_intro_de_la_musica_es_initial_silence` conserva la parte que no era de la tarjeta (el `adelay` del grafo de música = la intro, ahora `INITIAL_SILENCE_SEC` = 2.5 → `adelay=2500|2500`).
- `test_module_f36c_pantalla.py`: `_esquema` ya no exige la clave `tarjeta` ni la valida; `test_a_salida_valida_el_esquema` y `test_h_plan_edit_edita_el_papel` sin la tarjeta (en `test_h` se quita la edición `{tarjeta: …}` y su assert; el resto igual).
- `test_module_f38a_m01e.py`: **borrados** `test_a2_la_tarjeta_sale_de_voz_datos_y_no_del_autor` y `test_a2_vajont_tarjeta_real`; en `test_a1_formatos_literales` se quita el assert «TARJETA no está en el prompt» (lo cubre el grep-test nuevo, que mira la palabra en cualquier caja); docstring.
- `test_module_f38a_voz.py`: **borrados** `test_a2_horas_dichas_en_letras_y_digitos`, `test_a2_vajont_9_oct_1963_22_39_de_t66`, `test_a2_sin_fecha_en_el_gancho_falta`, `test_a2_voz_sin_hora_solo_fecha`, `test_a2_sin_pool_ni_vajont_la_hora_sale_del_item_que_coincide` (`horas_dichas` solo servía a la tarjeta: se va con ella); `import copy` y `voz_datos as vd` ya no se usan; docstring. Queda el fixture `vajont` (lo usa el test de D68 de §A.4).
- `test_module_f38e_c2.py`: el papel sintético sin `"tarjeta": None`.

Nuevo: `test_module_f38e_d.py` (4 tests: los 3 pedidos, el (3) partido en dos):
- (1) `test_d1_la_palabra_no_esta_en_el_codigo`: ningún `.py` de `script_engine/` ni `fase2b.py` contiene «tarjeta» (en minúsculas sobre el texto, así cubre TARJETA/Tarjeta);
- (2) `test_d2_gfx_guion_sin_evento_ni_chequeo_y_la_intro_es_el_primer_cuadro`: plan sintético de ch01 (el de `test_module_f32`) con la clave vieja `tarjeta_inicial` metida a propósito (como un plan resuelto de antes): sin evento, sin chequeo, costura = «intro 2.5 s (primer cuadro congelado, sin voz) → title card 3.0 s …», `intro_s` = `fase2b.INITIAL_SILENCE_SEC`, ningún evento antes del cap, la palabra no está en el .md;
- (3a) `test_d3_armar_y_markdown_sin_la_clave`: `armar`/`a_markdown` con respuesta sintética no traen la clave ni la palabra; «Totales: 0 fichas · 0 sellos · 0 relojes · 0 descartados»;
- (3b) `test_d3_editar_rechaza_lo_que_no_es_ficha_ni_sello`: `{tarjeta: {texto}}` y `{tarjeta: null}` → `ValueError` «sin ficha ni sello»; el papel no cambia. **Elegido: rechazar** (lo más honesto; ignorar en silencio escondería un `--plan-edit` viejo).

Otros: `lab/hyperframes/f38e/d/` (este archivo, `grep_antes.txt`, `grep_despues.txt`, `plan_only.log`, `_plan_only_inicio/fin.txt`, `_data_antes_full.txt`, `_data_despues_full.txt`, `antes/` = copia del guion de B.5, `despues/` = el guion nuevo, `diff_guion.py` copiado de `b/` con el docstring cambiado, `diff_guion.txt`). `lab/tools/mapa_modulos.py` NO se tocó; `data/` NO se tocó (el papel de Vajont sigue trayendo la clave `tarjeta` de F38d y Fase 2 simplemente no la lee).

## 3. `--plan-only` de Vajont sin la tarjeta

`PYTHONIOENCODING=utf-8 python fase2b.py f8s3-vajont-f30 --gfx --plan-only` desde la raíz, 13:28:18 → 13:31:20 (168 s según el log, exit 0, «Procesados OK: 1/1»). `plan_only.log`.

- **US$ 0,0000**: `costos {}` en el log; el ledger `data/cost_history.json` agrega una entrada `f8s3-vajont-f30` con `entries: []`, `total_cost: 0.0` (todo por caché: ni una llamada al crítico; en B.5 habían sido 4 llamadas, US$ 0,0004).
- **Foto de `data/`**: 1320 archivos antes y después; `diff _data_antes_full.txt _data_despues_full.txt` = solo `data/cost_history.json` (1003161 → 1003300 bytes, el ledger). Nada más.
- Guion nuevo copiado a `despues/GUION_PANTALLA.json` y `.md`.

Cabecera y cuadro de la intro (ch01 arranca con la primera imagen):

```
Generado 2026-10-27 13:31:20 por `fase2b --plan-only` (f36-c). Duración del mp4: 17:27.3 (1047.3 s; intro 2.5 s, title card 3.0 s).
## ch01 — Cama en la oscuridad (00:02.5–01:44.4)
- 00:02.5 · ch01 · beat 1 (gancho) · costura · «intro 2.5 s (primer cuadro congelado, sin voz) → title card 3.0 s desde 0.0 s → voz a 0.12 s del cap (+2.62 s del mp4)» · escena 0 (0.0 a 101.9 s)
- 00:02.5 · ch01 · beat 1 (gancho) · title card · «CAPÍTULO 1 | Cama en la oscuridad» · dura 3.0 s · …
```
(`intro_s` 2.5 = `INITIAL_SILENCE_SEC`; `mezcla.intro` 2.5; `costos {}`.)

Chequeos del guion (13; en B.5 eran 14):
```
✓ dos bloques al mismo tiempo · ✓ bloque que cruza un corte · ✓ texto sin lectura · ✓ pregunta de cierre sin lectura ·
✓ cifra que contradice la voz · ✗ a_pantalla · ✓ costuras con cuadro no negro · ✗ inicio de voz por cap ·
✓ gancho no vacío · ✓ inicio de música por cap · ✗ papel sin colocar · ✓ papel sin alinear · ✓ relojes del papel (informativo)
```
Los tres ✗ son los mismos tres de B.5 (`a_pantalla` 4/5, `inicio de voz` ch07 sin rampa, `papel sin colocar` CALMA); sin «tarjeta fecha-hora».

Diff por evento contra el guion de B.5 (`diff_guion.txt`, `antes/` = `b/despues/`):
```
## Top
- duracion_s: 1047.8 → 1047.3
- intro_s: 3.0 → 2.5
- mezcla: intro 3.0 → 2.5; duracion_s 1047.8 → 1047.3; musica: title_card_s/medido_s de los 7 caps −0.500 s, desvío 0.000 s en los 7 (ok True)
- costos: {'gemini_usd': 0.0004} → {}
## Caps (escalares)
- chNN offset: −0.5 s en los 7 (ch01 3.0 → 2.5 · ch02 104.933 → 104.433 · ch03 246.533 → 246.033 · ch04 381.833 → 381.333 ·
  ch05 510.8 → 510.3 · ch06 686.5 → 686.0 · ch07 860.7 → 860.2); seg_dur iguales
- chNN inicio_voz: esperado/medido/t_18db −0.5 s en los 7; ok igual que antes (ch07 sigue ✗ sin rampa)
## Eventos
- ch01 QUITADO: tarjeta fecha-hora «9 OCT 1963 · 22:39» @ -3.0 (queda=True)
- ch01 QUITADO: costura «intro 3.0 s (tarjeta «9 OCT 1963 · 22:39» sobre negro, sin voz) → …» @ 0.0
- ch01 NUEVO:   costura «intro 2.5 s (primer cuadro congelado, sin voz) → title card 3.0 s …» @ 0.0 filtro='pasó'
(ningún otro evento quitado, nuevo ni cambiado fuera de t_mp4)
## Chequeos
- inicio de voz por cap / inicio de música por cap / costuras con cuadro no negro: solo los tiempos del mp4 −0.5 s; ok iguales
- tarjeta fecha-hora: {ok: true, «✓ 00:00.0 «9 OCT 1963 · 22:39» …»} → null (desapareció)
(322 líneas distintas en el .md por el corrimiento de −0.5 s en todo t_mp4; 272 → 268 líneas)
```
En números: la intro pasa de 3,0 s (title_dur, la tarjeta) a 2,5 s (`INITIAL_SILENCE_SEC`), así que **todo el mp4 se corre −0,5 s** (offsets de los 7 caps, inicios de voz y de música, duración 1047,8 → 1047,3 s) y la música sigue clavada al title card de cada cap (desvío 0 cuadros en los 7). No cambia ninguna ficha, sello, reloj, cita ni pregunta.

## 4. Tests

- `test_module_f38e_d.py` + los 6 archivos tocados: 42 verdes.
- Lista pedida (`f38e_a b c c2 f36c_pantalla f34 f36 f32 f38a_m01e f38a_voz f37a_papel f38c_papel f38d_vueltas gfx_layer_fallback fase2b_reassemble` + `f38e_d`): **124 verdes, 0 rojos** (128,8 s).
- Rápida `f25c f24 f21`: **58 verdes**.
- `py_compile` + `pyflakes` de los 7 módulos tocados: sin nombres sin definir ni imports huérfanos nuevos (el único aviso, `total_cost` sin usar en `fase2b.py:3535`, es previo).
- Tests borrados por nombre: 9 (1 en f34, 1 en f36 —reemplazado por uno sin tarjeta—, 2 en f38a_m01e, 5 en f38a_voz). Tests nuevos: 4.

## 5. Stickers para `lab/MAPA_MODULOS.md` (en `lab/tools/mapa_modulos.py`; NO editado)

- **fase2b**: «El armador final: junta imagen, voz, subtítulos y música de cada capítulo en un segmento y los pega en el video. Con `--gfx` le pone encima la capa gráfica; con `--plan-only` solo escribe el guion de pantalla. Desde F34, con `--gfx` la música de cada cap arranca con su title card (pieza = segmento, después de la intro) y la mezcla de previsualización mide dónde arranca. La intro es siempre INITIAL_SILENCE_SEC con el primer cuadro congelado (F38e §D: la fecha-hora del segundo 0 se borró; el video arranca con la primera imagen); `--plan-edit` edita el guion en papel (ficha o sello de un beat; otra cosa se rechaza).» (entradas/salidas/origen iguales).
- **gfx_layer**: «El director de orquesta de la capa gráfica de un capítulo: llama a todos los demás en orden (plan base con el title card de la partición —F37: sin borrador del director—, textos del papel, reparto con crítico, sellos, relojes del papel, transiciones) y hace el render en HyperFrames. Desde F34, con el guion aprobado dibuja el plan aprobado tal cual (plan congelado) y no lo reescribe.» (solo se agrega «relojes del papel»; el sticker no nombraba la tarjeta; resto igual).
- **pantalla_entrada**: descripción igual; salida: «entrada del cap + bloques, sellos y relojes del papel» (antes «… relojes y tarjeta del papel»).
- **voz_datos**: «Lo que sale de la voz y la escaleta sin modelo: el pico del cap y el reloj cuando la voz dice una fecha completa (y su esquina libre). F38e §D: la fecha-hora del segundo 0 (la derivada de la escaleta y la de la voz, con su lector de horas) se borró.»; entradas «oraciones de la voz, escaleta, pool»; salida «pico, reloj»; origen «F36 (código de F34)», «vivo».
- **gfx_guion**: «Escribe el guion de pantalla: todo lo que se va a ver, en texto, con lo cortado y por quién, y los chequeos (lectura, nunca al mismo tiempo, costuras, inicio de voz, inicio de música, gancho no vacío; desde F36 C la columna `papel` y «papel sin colocar / sin alinear»; desde F38c «cifra que contradice la voz» no marca lo que el autor juzgó otro hecho). F38e §D: sin evento ni chequeo de fecha-hora del segundo 0; la costura de ch01 dice «primer cuadro congelado».» (resto igual).
- **m01e_pantalla**: solo cambia la frase «relojes (F38: la tarjeta sale de la voz, voz_datos)» → «relojes (F38e §D: sin fecha-hora del segundo 0)»; resto igual.

## 6. Lo que queda abierto (D entero)

- d1. El papel de Vajont en `data/scripts/_steps/f8s3-vajont/01e_pantalla.json` sigue trayendo `"tarjeta": {…}` (de F38d); Fase 2 no la lee. Se limpia sola la próxima vez que corra m01e (Kyshtym u otro); no se reescribió `data/` a propósito.
- d2. `b/despues/` (B.5) y cualquier `GUION_PANTALLA` anterior a hoy traen el evento y el chequeo; `gfx_plan_ch01.resolved.json` viejos en `_fase2b_work/` pueden traer `tarjeta_inicial`: nadie la lee (el test d2 lo prueba con la clave puesta a propósito). Con `--reuse-visuals` + md5 del plan (A.1) la capa de ch01 se rehace sola porque el plan resuelto cambia.
- d3. El `.md` de B.5 y el de F38d en `lab/hyperframes/f38/…` quedan como historia (no se tocan).
- d4. `git status` avisa «LF will be replaced by CRLF» para `test_module_f38e_c2.py`: ya era LF antes de D (como `f38e_c.py` y el nuevo `f38e_d.py`); no se cambió el final de línea de ningún archivo.
- d5. Render: no se hizo (freno). El mp4 real con la intro de 2,5 s y el primer cuadro congelado se ve recién en el próximo render; el guion ya lo describe.
