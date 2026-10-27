# F40 · parte A — el gancho: pregunta, no corte (subagente, 2026-10-27)

Handoff: `lab/hyperframes/f40/HANDOFF_F40_gancho_subs_kyshtym.md` §6 · DECISIONES 2026-10-27 18:30 (+ 22:26 «casi nada
hardcode», 16:38 «borrar, no apagar», F37 §A.4). HEAD de partida `8669045`. Sin commit, sin `git add`, sin mapa
regenerado, sin llamadas a modelos, `fase2b.py` sin tocar.

## Archivos tocados
- `script_engine/pantalla_filtros.py` — borrado `gancho_dicho` (+ `gancho_dicho.regla`) y su lugar en `ORDEN`
  (queda `[ancla_papel, candado, no_dicho, spoiler, lectura]`); `no_dicho`: el motivo dice «en otra oración del video
  (gancho)» cuando la coincidencia es la del gancho fuera de la oración ancla ± 1 (antes decía siempre «en la oración
  ancla o en una vecina», falso para el gancho); comentarios/docstring.
- `script_engine/m01e_pantalla.py` — borrado `dice_voz` en `_validar_ficha` (y su `xi["dice_voz"]`), el import y la
  llamada a `gancho_dicho`; `voz_txt` (solo lo leía `dice_voz`) sale de `validar` y de la firma de `_validar_ficha`; la
  pregunta `no_dicho` del gancho cuya cifra la voz dice fuera de la oración ancla ± 1 lleva `video: True` y
  `_pregunta_txt` la escribe con el formato del spoiler sin «en la oración ancla o en una vecina»: «la voz dice «6» en
  ch05 [12] («…»); ¿es el mismo hecho? si no, mantenelo» (el lugar sale del mismo `_donde` de siempre); docstring.
- `script_engine/pantalla_entrada.py` — borrado `dice_voz` de `_item`; `_item` pierde el parámetro `voz_video` (solo lo
  leía `dice_voz`) y el import `numero_en` (sin otro uso); docstring de `preparar_cap`.
- Tests ajustados: `test_module_f36c_pantalla.py`, `test_module_f37b_colocar.py`, `test_module_f38e_b.py`.
- Nuevo: `test_module_f40_gancho.py`.
- Lab: `lab/hyperframes/f40/a/sim_gancho.py`, `sim_gancho_salida.md`, este archivo, y las copias congeladas
  `kyshtym/` (de `data/scripts/_steps/f39-kyshtym`: `00_pool_v3`, `01a_escaleta`, `01a_skeleton`, `01b_narracion_v3`
  —la de las 18:44, ya sin voseo—, `01e_pantalla.raw.json`) y `vajont/` (de `lab/hyperframes/f38/b2/fase1/f8s3-vajont`
  + `lab/hyperframes/f38/b4/01e_pantalla.raw.json`).

## Símbolos
| símbolo | antes | ahora | llamadores vivos (grep -rn en código, tests y lab/tools) |
|---|---|---|---|
| `pantalla_filtros.gancho_dicho` | filtro de `ORDEN` + llamada directa en `m01e_pantalla._validar_ficha` | **borrado** | ninguno (solo esos dos) |
| `dice_voz` (m01e_pantalla) | calculado en `_validar_ficha` | **borrado** | solo lo leía `gancho_dicho` |
| `dice_voz` (pantalla_entrada._item) | clave del ítem de Fase 2 | **borrado** | solo lo leía `gancho_dicho`; los tests lo ponían en `False` en fixtures |
| `voz_txt` (m01e_pantalla.validar / `_validar_ficha`) | parámetro | **borrado** | solo lo leía `dice_voz` |
| `_item(..., voz_video)` (pantalla_entrada) | parámetro | **borrado** | solo lo leía `dice_voz`; `voz_video` sigue en `preparar_cap` (va a la entrada) |
| `no_dicho` | — | queda (con el gancho y el juicio del autor, como F37 §A.4) | m01e_pantalla, `ORDEN`, lectura |
| `_donde` | — | queda, mismo uso (primera oración que dice el token) | m01e_pantalla |
| `ev.used_in`, `ev._figures` | — | quedan | gfx_pool, gfx_realizador, m05_narrative, evidence |

## Prompts (md5 antes = después)
| constante | md5 HEAD 8669045 | md5 F40 §A |
|---|---|---|
| `PANTALLA_SYSTEM` | 7d2ccdd28055d6e621d1d251a0fe8bb7 | 7d2ccdd28055d6e621d1d251a0fe8bb7 |
| `FORMATO_SALIDA` | f63ad89ad721f319370fe2ebb8b539b5 | f63ad89ad721f319370fe2ebb8b539b5 |
| `FORMATO_REINTENTO` | 07cd8ad0fb3f3e31b46dcd2a6641fa23 | 07cd8ad0fb3f3e31b46dcd2a6641fa23 |
| `REINTENTO_PARCIAL` | 29deed051c1440eb4ea8c2b5e7b776e8 | 29deed051c1440eb4ea8c2b5e7b776e8 |
| `prompt_md5()` (los 4 juntos) | 3b98aef1d8595124967ac7a85b75bab7 | 3b98aef1d8595124967ac7a85b75bab7 |
`PROMPT_VERSION` m01e-6 sin cambio. Ningún número nuevo.

## Tests
Borrados por nombre: ninguno (no había ningún test de `gancho_dicho` ni de `dice_voz` como tal).
Ajustados:
- `test_module_f36c_pantalla.py::test_f_fase2_lee_el_papel_sin_llamar_a_ningun_modelo_de_texto` — el `ORDEN` esperado
  pasa de `[anclaje, no_dicho, candado, no_dicho, spoiler, lectura]` a `[anclaje, candado, no_dicho, spoiler,
  lectura]` (el primer `no_dicho` era `gancho_dicho`).
- `test_module_f36c_pantalla.py::test_g_cita_ficha_con_autor_y_sellos_del_papel_nunca_al_mismo_tiempo`,
  `test_module_f37b_colocar.py::test_b1_q50_corta_se_mueve_a_la_oracion_siguiente_si_no_cabe`, y el fixture de D47 en
  `test_module_f38e_b.py` — sale `"dice_voz": False` del ítem de la entrada (clave sin lector).
Nuevo `test_module_f40_gancho.py` (9): D03 «Nivel 6 de 7» (intento 1 real de F39) → pregunta con «6» en ch05 [12] y
«7» en ch04 [14], texto exacto; el autor no la cambia en la vuelta (POST falso) → queda con `juicio_autor.no_dicho`
{6, 7}; D91 «Más de 5000 personas» (la voz: «Más de cinco mil personas estaban en el sitio industrial…», ch04 [11], la
única vez, mismo hecho) → pregunta; el autor la saca (`ficha: null`) → sale; sin respuesta, al cierre corta como
no_dicho «en otra oración del video (gancho)»; Vajont v6 D195 → pasa sin pregunta; `gancho_dicho`/`dice_voz` no están;
Fase 2 (`no_dicho`) respeta el juicio del autor en el gancho; fuera del gancho, igual que antes; md5 de los prompts.

Resultados: `test_module_f40_gancho.py` + los 16 que mencionan `gancho_dicho`/`dice_voz`/`pantalla_filtros`/
`m01e_pantalla`/`pantalla_entrada` → **133 passed**; suite rápida (f25c, f24, f21) → **58 passed**. No se corrió la
amplia ni `fase2b`.

## Salida de §6.4
`python lab/hyperframes/f40/a/sim_gancho.py` · hoy = código de HEAD 8669045 · F40 = árbol de trabajo. Voz = `entrada.caps` del raw de cada papel (la que vio m01e). Una fila por ficha del gancho que el autor propuso (Kyshtym: ch01 beat 1, intento N del raw de F39).

| tema | dato del gancho (intento, oración) | cifras que encuentra en la voz (con cap y oración) | hoy (HEAD) | con F40 |
|---|---|---|---|---|
| Kyshtym | D03 «ESCALA DE ACCIDENTES NUCLEARES · Nivel 6 de 7» (int. 1, [5]) | hoy (cifras del texto del ítem, `dice_voz`): «7» en ch04 [14] («A las siete y veinte de la tarde, el viento ya había decidido hacia dónde.»), «6» en ch05 [12] («Seis de octubre de mil novecientos cincuenta y siete.») · used_in<br>F40 (cifras del dato de la ficha, `no_dicho`): «6» en ch05 [12] («Seis de octubre de mil novecientos cincuenta y siete.»), «7» en ch04 [14] («A las siete y veinte de la tarde, el viento ya había decidido hacia dónde.») | cae: no_dicho («D03 es del pool del video y la narración lo dice en algún cap (gancho)») | pregunta al autor (4) → otro hecho → **queda** |
| Kyshtym | D50 «LA FUGA, COMPARADA · Chernóbil liberó 19 veces más» (int. 2, [5]) | hoy (cifras del texto del ítem, `dice_voz`): «19» en ch01 [7] («Tenían dieciocho, diecinueve, veinte años.») · used_in<br>F40 (cifras del dato de la ficha, `no_dicho`): «19» en ch01 [7] («Tenían dieciocho, diecinueve, veinte años.») | cae: no_dicho («D50 es del pool del video y la narración lo dice en algún cap (gancho)») | pregunta al autor (2) → otro hecho → **queda** |
| Kyshtym | D03 «NIVEL OFICIAL DEL ACCIDENTE · 6 en una escala de 7» (int. 3, [8]) | hoy (cifras del texto del ítem, `dice_voz`): «7» en ch04 [14] («A las siete y veinte de la tarde, el viento ya había decidido hacia dónde.»), «6» en ch05 [12] («Seis de octubre de mil novecientos cincuenta y siete.») · used_in<br>F40 (cifras del dato de la ficha, `no_dicho`): «6» en ch05 [12] («Seis de octubre de mil novecientos cincuenta y siete.»), «7» en ch04 [14] («A las siete y veinte de la tarde, el viento ya había decidido hacia dónde.») | cae: no_dicho («D03 es del pool del video y la narración lo dice en algún cap (gancho)») | cae: caben («etiqueta 27 + dato 20 = 47 caracteres y en la oración [8] caben 31; en este beat caben como máximo 90 (oración [1])») |
| Kyshtym | D201 «OTRA MUERTE EN LA PLANTA · Valia Dronova, 38 años: pulmones de piedra» (int. 4, [4]) | hoy (cifras del texto del ítem, `dice_voz`): «20» en ch01 [7] («Tenían dieciocho, diecinueve, veinte años.»)<br>F40 (cifras del dato de la ficha, `no_dicho`): ninguna | cae: no_dicho («D201 es del pool del video y la narración lo dice en algún cap (gancho)») | pasa |
| Kyshtym | D03 «NIVEL 6 DE 7 · Escala internacional de accidentes» (int. 5, [1]) | hoy (cifras del texto del ítem, `dice_voz`): «7» en ch04 [14] («A las siete y veinte de la tarde, el viento ya había decidido hacia dónde.»), «6» en ch05 [12] («Seis de octubre de mil novecientos cincuenta y siete.») · used_in<br>F40 (cifras del dato de la ficha, `no_dicho`): ninguna | cae: no_dicho («D03 es del pool del video y la narración lo dice en algún cap (gancho)») | pasa |
| Vajont v6 | D195 «LONGARONE · 1.269 de 1.328 habitantes murieron» (int. —, [2]) | hoy (cifras del texto del ítem, `dice_voz`): ninguna<br>F40 (cifras del dato de la ficha, `no_dicho`): ninguna | pasa | pasa (sin cambio) |

## Detalle por ficha

### Kyshtym · D03 «ESCALA DE ACCIDENTES NUCLEARES · Nivel 6 de 7» (int. 1, [5])
- hoy: cae: no_dicho («D03 es del pool del video y la narración lo dice en algún cap (gancho)»)
- F40 pregunta: D03 (ch01 beat 1, oración [5]) «ESCALA DE ACCIDENTES NUCLEARES · Nivel 6 de 7»: la voz dice «6» en ch05 [12] («Seis de octubre de mil novecientos cincuenta y siete.»); ¿es el mismo hecho? si no, mantenelo
- F40 pregunta: D03 (ch01 beat 1, oración [5]) «ESCALA DE ACCIDENTES NUCLEARES · Nivel 6 de 7»: la voz dice «7» en ch04 [14] («A las siete y veinte de la tarde, el viento ya había decidido hacia dónde.»); ¿es el mismo hecho? si no, mantenelo
- F40 pregunta: D03 (ch01 beat 1, oración [5]) «ESCALA DE ACCIDENTES NUCLEARES · Nivel 6 de 7»: la voz dice «6» en una oración posterior en ch05 [12] («Seis de octubre de mil novecientos cincuenta y siete.»); ¿es el mismo hecho? si no, mantenelo
- F40 pregunta: D03 (ch01 beat 1, oración [5]) «ESCALA DE ACCIDENTES NUCLEARES · Nivel 6 de 7»: la voz dice «7» en una oración posterior en ch04 [14] («A las siete y veinte de la tarde, el viento ya había decidido hacia dónde.»); ¿es el mismo hecho? si no, mantenelo
- F40 con «otro hecho»: queda=True · juicio_autor={"no_dicho": ["6", "7"], "spoiler": ["6", "7"]}

### Kyshtym · D50 «LA FUGA, COMPARADA · Chernóbil liberó 19 veces más» (int. 2, [5])
- hoy: cae: no_dicho («D50 es del pool del video y la narración lo dice en algún cap (gancho)»)
- F40 pregunta: D50 (ch01 beat 1, oración [5]) «LA FUGA, COMPARADA · Chernóbil liberó 19 veces más»: la voz dice «19» en ch01 [7] («Tenían dieciocho, diecinueve, veinte años.»); ¿es el mismo hecho? si no, mantenelo
- F40 pregunta: D50 (ch01 beat 1, oración [5]) «LA FUGA, COMPARADA · Chernóbil liberó 19 veces más»: la voz dice «19» en una oración posterior en ch01 [7] («Tenían dieciocho, diecinueve, veinte años.»); ¿es el mismo hecho? si no, mantenelo
- F40 con «otro hecho»: queda=True · juicio_autor={"no_dicho": ["19"], "spoiler": ["19"]}

### Kyshtym · D03 «NIVEL OFICIAL DEL ACCIDENTE · 6 en una escala de 7» (int. 3, [8])
- hoy: cae: no_dicho («D03 es del pool del video y la narración lo dice en algún cap (gancho)»)
- F40: cae caben: etiqueta 27 + dato 20 = 47 caracteres y en la oración [8] caben 31; en este beat caben como máximo 90 (oración [1])

### Kyshtym · D201 «OTRA MUERTE EN LA PLANTA · Valia Dronova, 38 años: pulmones de piedra» (int. 4, [4])
- hoy: cae: no_dicho («D201 es del pool del video y la narración lo dice en algún cap (gancho)»)

### Kyshtym · D03 «NIVEL 6 DE 7 · Escala internacional de accidentes» (int. 5, [1])
- hoy: cae: no_dicho («D03 es del pool del video y la narración lo dice en algún cap (gancho)»)

### Vajont v6 · D195 «LONGARONE · 1.269 de 1.328 habitantes murieron» (int. —, [2])
- hoy: pasa


## Stickers (para que CC los aplique en lab/tools/mapa_modulos.py; solo la frase que cambia)
- `pantalla_filtros`: «anclar el papel a la voz, no dicho del gancho, candado de lo literal, no dicho, spoiler» →
  «anclar el papel a la voz, candado de lo literal, no dicho (en el gancho, con la voz de todo el video), spoiler»; y
  al final: «F40: sin el corte del gancho (`gancho_dicho`): su coincidencia con la voz es de no dicho y se le pregunta
  al autor.»
- `m01e_pantalla`: agregar «F40: el dato del gancho ya no cae en seco si una cifra suya está en la voz de cualquier
  cap: se le pregunta al autor con el cap, el número de oración y la oración.»
- `pantalla_entrada`: agregar «F40: el ítem ya no trae `dice_voz` (solo la marca de gancho).»

## Lo que queda abierto
1. **Preguntas dobles en el gancho.** Una cifra del gancho que la voz dice más adelante es a la vez `no_dicho` (todo el
   video) y `spoiler` (lo posterior del cap y de los caps siguientes): el autor recibe dos preguntas por cifra (D03: 4
   preguntas por «6» y «7»; D50: 2 por «19»). Mantenerla las contesta a las dos (`juicio_autor` con las dos reglas) y
   no cambia el resultado, pero duplica motivos en el reintento. No lo toqué (sería una regla nueva de deduplicación).
2. **`_donde` cita solo la primera oración** que dice la cifra. Si la voz dice la cifra varias veces, el autor ve solo
   la primera: con D11 «20 millones de curios» la pregunta cita ch01 [7] «Tenían dieciocho, diecinueve, veinte años.»
   y no ch04 [10] «Por ese agujero salieron unos veinte millones de curios.» (el mismo hecho). El autor podría
   «mantenerla» viendo la oración equivocada. Es el mismo helper y formato que el spoiler (pedido); listar todas sería
   otro formato. Decisión de Omar/analista.
3. **`no_dicho` mira solo el dato, no la etiqueta** (como desde F36, en todos los beats). D03 int. 5 «NIVEL 6 DE 7 ·
   Escala internacional de accidentes» pasa sin pregunta aunque la voz diga «seis» y «siete» en otros caps. Hoy el
   resultado es el correcto (otro hecho), pero un gancho con la cifra en la etiqueta que la voz sí dice no se pregunta.
4. **Se pierde `used_in` en el gancho.** `dice_voz` también cortaba si `ev.used_in(voz, ítem)` (anclas del ítem, no
   solo cifras) y miraba las cifras de TODO el texto del ítem; con F40 el gancho mira las cifras del dato de la ficha
   en todo el video y los nombres solo en la oración ancla ± 1. Es lo que pide §2 del handoff («la coincidencia sigue
   en no_dicho»).
5. **La tabla de §3 del handoff no coincide en dos filas**: D201 no es «pregunta → queda» sino «pasa» (el dato de la
   ficha es «Valia Dronova, 38 años: pulmones de piedra»; el «20» de «planta 20» está en el texto del ítem, no en la
   ficha, y la voz no dice 38); D03 int. 3 («6 en una escala de 7» en [8]) con F40 cae igual, pero por `caben` (47 > 31),
   no por el gancho. D03 int. 5 pasa sin pregunta (punto 3).
6. **Motivo de `no_dicho` en el gancho**: cambié el texto del motivo de corte (al cierre y en Fase 2) a «la voz lo dice
   en otra oración del video (gancho)» cuando la coincidencia está fuera de la oración ancla ± 1, porque «en la oración
   ancla o en una vecina» era falso. Es texto de motivo, no prompt; si CC prefiere no tocarlo, se revierte en
   `pantalla_filtros.no_dicho` (2 líneas) y en `test_2_sin_preguntar_al_cierre...`/`test_4_fase2...`.
7. La voz congelada de Kyshtym es la de `entrada.caps` del raw de F39 (con voseo: «cenás»); las cifras no cambian con
   C.1. La copia de `01b_narracion_v3.json` en `kyshtym/` es la de las 18:44 (ya sin voseo).

## Para la parte C (regenerar el papel de Kyshtym)
- La clave de caché de m01e incluye el USER, que lleva los títulos y la voz: con C.1/C.2 aplicados la clave cambia y
  hay llamada nueva (no sale de la caché). Respaldar antes `01e_pantalla.{json,md,raw.json}` como `01e_pantalla_f39.*`.
- Esperable en el intento 1 si el autor vuelve a poner D03 «Nivel 6 de 7» en ch01: 4 preguntas (6 y 7, no_dicho y
  spoiler), con «la voz dice «6» en ch05 [12] («Seis de octubre…»)» y ««7» en ch04 [14] («A las siete y veinte…»)». Si
  el autor la mantiene, queda con `juicio_autor {no_dicho: [6, 7], spoiler: [6, 7]}` y Fase 2 la respeta (no_dicho
  con juicio; `gancho_dicho` ya no está en `ORDEN`). Las preguntas y respuestas salen en el .md en «reintento».
- Las preguntas del gancho pesan en el tope (US$ 1,00): son motivos más en la vuelta 1, no llamadas extra.
- Fase 2 sobre un papel viejo (F39) no cambia nada: los cortes del gancho de F39 ya están en el papel como descartes.
