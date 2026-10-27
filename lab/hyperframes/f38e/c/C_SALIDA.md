# F38e §C — Papel m01e-6 con `respaldo` y `autor` · salida en texto (CC, 2026-10-27)

Handoff `lab/hyperframes/f38e/HANDOFF_F38e_lo_que_rompe_cualquier_video.md` §C. Rama `f11-guion-v4`, sin commit (lo hace el principal).

## Archivos tocados / creados
- `script_engine/m01e_pantalla.py` (CRLF verificado con `file`: «with CRLF line terminators», 0 LF sueltos): PANTALLA_SYSTEM m01e-6 (escrito por `c1_prompt_del_md.py`), `PROMPT_VERSION`, `FORMATO_SALIDA`/`FORMATO_REINTENTO`, `_validar_ficha` (regla `respaldo`, candado contra el respaldo, autor mostrado), `_nombres_del_autor`, `autor_mostrado`, `a_markdown`, docstrings.
- Tests actualizados al formato nuevo: `test_module_f36c_pantalla.py`, `test_module_f37a_papel.py`, `test_module_f38a_m01e.py`, `test_module_f38c_papel.py`, `test_module_f38d_vueltas.py`. Test nuevo: `test_module_f38e_c.py`. Ninguno borrado.
- `lab/hyperframes/f38e/c/`: `c0_foto_data.py`, `c1_prompt_del_md.py`, `c_corrida.py`, `c_corrida.log`, `c_corrida.stdout`, `01e_pantalla.raw.json`, `01e_pantalla.json`, `01e_pantalla.md`, `TABLA.md`, `data_foto_antes.json`, `data_foto_despues.json`, `vajont_steps/f8s3-vajont/` (copia de `data/scripts/_steps/f8s3-vajont/`, 121 archivos, con el papel nuevo escrito ahí), este `C_SALIDA.md`.
- No se tocó `pantalla_filtros.py` (el candado del papel se alimenta desde `_validar_ficha`: se le pasa el ítem con `texto` = respaldo), ni `voz_datos.py`, ni nada de A/B/E.

## C.1 · Prompt m01e-6 (md5 comprobado)
`c1_prompt_del_md.py` extrae el bloque «Prompt nuevo (m01e-6-prueba), entero» de `PRUEBA1_prompt_rotulos.md` (md5 del md `240e3e7bf13656cb62f68b598393f41f`, OK) con el mismo corte que `prueba1_rotulos.system_del_md`, lo escribe en bytes dentro del string triple de `PANTALLA_SYSTEM` (cada `\n` → `\r\n`, el resto del archivo intacto) y verifica importando el módulo:
```
bloque del md: 3098 caracteres · md5 7d2ccdd28055d6e621d1d251a0fe8bb7 · OK
string viejo: 2539 bytes · nuevo: 3179 bytes · posición 7635
md5(m01e_pantalla.PANTALLA_SYSTEM) = 7d2ccdd28055d6e621d1d251a0fe8bb7 · OK
PANTALLA_SYSTEM == bloque del md: True
```
`PROMPT_VERSION = "m01e-6"` (comentario con el origen). `prompt_md5()` (SYSTEM + los dos formatos + REINTENTO_PARCIAL) = `3b98aef1d8595124967ac7a85b75bab7`.

## C.2 · Formato
`FORMATO_SALIDA` y `FORMATO_REINTENTO`: los de hoy con `"respaldo": "…", "autor": "…" | null, ` después de `"texto": "Más de 1 metro", ` (una vez en cada uno).

## C.3 / C.4 · Qué hace el código
- `respaldo` (después de anclaje y formato, antes de fecha del relato): `ev.norm(respaldo) in ev.norm(x["texto"])` (el texto del ítem que ve el modelo, `_texto_item`). Si falta o no es subcadena → cae con regla `respaldo`, entra a `motivos`/`motivos_beat` como cualquier ficha caída, la vuelta lo puede arreglar, y si no, queda caído con esa regla (nada «sin preguntar»: es un corte, no una pregunta).
- Candado: para todo lo que no es cita, `candado` recibe el ítem con `texto` = respaldo (cifras, nombres y años de etiqueta y dato contra el respaldo; la etiqueta además contra `fuente` del dato como hoy; la excepción de la oración ancla sigue adentro de `candado`). La cita sigue contra el texto entero (frase literal recortada).
- Autor (cita): `autor_mostrado(autor_modelo, x)` → el del modelo si cada nombre propio de `_nombres_del_autor` está (`_palabra_en`) en `autor`, `rol` o `texto` del ítem; si no, el del archivo sin cortar. `_nombres_del_autor` = `voz_utils.nombres` (no ve el que abre) **más el que abre cuando va seguido de otro nombre propio** («Pietro Leone» → Pietro, Leone; «Municipio de Erto y Casso» → Erto, Casso). Ver abierto c1. La ficha del papel guarda `autor` (el mostrado) y `autor_origen` («modelo» / «archivo: <motivo>»); `caracteres` y el motivo de `caben` usan el mostrado; `a_markdown` lo muestra («— Giovanni Leone (autor: modelo)») y también el respaldo.
- `cita_sin_fecha` (`autor_en`) sigue mirando el autor del archivo.

## Gasto
- Peor caso estimado antes de llamar (lógica de `llamar`, entrada real: USER 137 035 car., body 150 460 car., tarifas 2/10): **intento 1 US$ 0,2804** (OUT_TOKENS_PEOR 16 000) / **0,3266** (salida 20 623, e4); una vuelta (USER + papel anterior como el de la prueba 1) 0,2960 / 0,3422. Tope `m01e_pantalla.TOPE_USD_RESPALDO` 1,00 (`tope_usd()` → «respaldo (el perfil no trae costos.m01e_tope_usd)»).
- Real (una sola corrida, 4 llamadas, 194 s; `claude_helpers.cost_of` por llamada, ledger en memoria = `llamar`):

| llamada | in | out | US$ | s |
|---|---|---|---|---|
| intento 1 | 66 450 | 20 318 | 0,3361 | 139,8 |
| vuelta 1 | 71 417 | 2 433 | 0,1672 | 20,8 |
| vuelta 2 | 70 936 | 421 | 0,1461 | 8,3 |
| vuelta 3 | 71 053 | 1 814 | 0,1603 | 20,6 |
| **total** | | | **0,8096** | |

Cerró por **tope**: «gastado 0.8096 + esta llamada hasta 0.3308 → sin reintento» (la vuelta 4 no entró). Nada fue al `cost_tracker` (`hx._track` desviado a memoria; 4 entradas, US$ 0,8096).

## Foto de `data/` (mtime + md5, 1320 archivos)
- Dentro de la corrida (`c_corrida.py`, antes de importar nada → al salir): **cambiados/nuevos: ninguno** · `cost_history.json` md5 `1f5e5ded03a8637e780d6de237cb1550` → `1f5e5ded03a8637e780d6de237cb1550` (también en el `--seco`).
- Foto de toda mi parte (`c0_foto_data.py antes` 12:56 → `despues` 13:06): **1 cambiado: `data/cost_history.json`** (md5 `1f5e5ded…` → `237879aa…`, mtime 13:04:20, +139 bytes). Lo que se agregó es un `video_id "f8s3-vajont-f30"` con `created_at 2026-10-27T12:59:47`, `entries []`, `total_cost 0.0`: un `fase2b` de `f8s3-vajont-f30` (start_video/end_video) corrido en paralelo por la parte A o B. Mi corrida terminó 13:01:11 con ese md5 intacto, mi topic es `f8s3-vajont` y mis scripts no llaman `start_video`; los tests no escriben el historial bajo pytest (`_save_to_history`). No es de C.
- `logs/`: durante mi corrida aparecieron `pipeline_20261027_1257…`–`1300…` y siguieron apareciendo después de que terminé (13:01–13:06): los crea el import de `error_handler` en otros procesos (los de A/B/E). Mi proceso tiene `logging.FileHandler` → `NullHandler` durante todo el run y el `--seco` registró «logs/ nuevos: ninguno».

## Tests
- `python -m pytest -q test_module_f38e_c.py test_module_f36c_pantalla.py test_module_f37a_papel.py test_module_f38a_m01e.py test_module_f38c_papel.py test_module_f38d_vueltas.py test_constantes_con_origen.py` → **55 passed** (11 nuevos en `test_module_f38e_c.py`).
- Suite rápida `test_module_f25c.py test_module_f24.py test_module_f21.py` → **58 passed**.
- Qué cambié y por qué:
  - `f36c`, `f37a`, `f38a`, `f38c`, `f38d`: las respuestas congeladas (F37, F38b, F38c) y las fichas de mano no traen `respaldo` y ahora caerían con regla `respaldo`. Se completa con `_con_respaldo(resp, ent)` = el texto entero del ítem (fragmento literal trivial): el candado contra ese respaldo es el de antes, así que cada test sigue midiendo lo suyo. En `f38a` va en la fixture `raw37`; en `f38c` en `papel` (+ la ficha de mano de D128); en `f38d` en `r1`/`r2`.
  - `PROMPT_VERSION == "m01e-5"` → `"m01e-6"` (f37a, f38a ×2, f38d).
  - `f38c::test_prompt_no_cambia`: md5 `76f1de7a…` → `3b98aef1…` (comentario con la historia).
  - `f38d::test_5`: medía que m01e-5 difería de m01e-4 en una sola línea (la de «caben»). Con el SYSTEM reemplazado entero eso no se puede medir; ahora comprueba que m01e-6 conserva lo que F38d §A.2.1 pedía (la oración de «caben» con el autor y los 5 de comillas y raya, con las palabras de la prueba 1) y que el md5 ya no es el de m01e-4. **No se borró ningún test.**

## Sticker nuevo para `lab/MAPA_MODULOS.md` (fila `m01e_pantalla`)
| `m01e_pantalla` | Fase 1 (F36 C): el guion de pantalla EN PAPEL. Una llamada a Sonnet por video con la narración de los 7 caps (oraciones numeradas y cuánto cabe), la escaleta, el archivo del caso y el vocabulario de clima → por beat ficha o nada, sello o nada; relojes (F38: la tarjeta sale de la voz, voz_datos). Lo valida en papel (candado, no dicho, spoiler, una vez, cabe, formato; F37: fecha del relato, cita sin fecha, descartes «la voz lo dice» verificados, picos sin ficha; una coincidencia de número se le pregunta al autor); F38: un reintento PARCIAL con todos los motivos cambia solo los beats con motivo (lo demás queda congelado; F38b: sin juez de anclaje). F38c: lo que la escaleta dejó para la pantalla le llega aparte de «la voz lo cuenta», y un beat sin él es motivo del reintento; una cifra que contradice la voz se le pregunta al autor. F38d: el reintento da vueltas mientras haya motivos nuevos y entre en el tope del perfil, y «caben» se mide igual en el prompt, en el motivo y en el código. F38e: prompt m01e-6 (el de la prueba 1, letra por letra): el dato con las palabras del autor y los hechos en un `respaldo` literal del ítem (regla `respaldo`; el candado mira cifras, nombres y años contra él); en una cita el autor viene en español y se muestra si sus nombres están en el archivo (`autor_origen`). Lo deja para que Omar lo revise antes de la voz; Fase 2 lo consume. | escaleta, narración por cap y beat, títulos, pool, `sellos_clima` | `01e_pantalla.json/.md` en el topic de Fase 1 | fase1_5.py, fase2b.py, pantalla_entrada.py (+ 7 tests) | F36 (`9e9d844`) | vivo (fase 1) |

## Lo que queda abierto (C entero)
- c1. **«Pietro Leone» y la letra del handoff.** §C.4 dice «cada nombre propio que **no** abre la frase» con `voz_utils.nombres`; con eso solo, «Pietro Leone» pasa (Pietro abre, Leone está en el archivo) y el caso de test obligatorio («no pasa») no se cumple. Agregué una lectura: el que abre también cuenta cuando va seguido de otro nombre propio (nombre y apellido); seguido de una palabra común («Municipio de…», «Presidente del…») no cuenta. Es una regla de forma, sin número ni lista de palabras; la decide el analista. Consecuencia medida: «Giovanni Leone, presidente del Consejo» no pasa (Consejo ≠ Consiglio) → se muestra el del archivo; un autor de una sola palabra («Montedison») pasa sin verificar.
- c2. **El autor mostrado no llega a Fase 2.** `pantalla_colocar` dibuja la cita con `it["autor"]` del pool (línea ~200) y `pantalla_entrada._item` también lee el pool; el `autor` del papel solo se ve en el papel y en `caben`. Cablearlo es tocar archivos de B (`pantalla_colocar`) y `pantalla_entrada`: fuera de C hoy. Mientras tanto, Fase 2 mide y dibuja el autor del archivo (en Q50: «Administración del comune di Erto e Casso», 41 car.), que puede no caber donde el papel dijo que cabía con el del modelo (86/90 con «Municipio de Erto y Casso»).
- c3. **El cierre por tope con un motivo que no se va.** Después de la vuelta 3 no quedaba nada caído ni pregunta (fichas fuera 0 · preguntas 0 · picos 0), pero seguía el motivo `a_pantalla` de ch07 b13 (D245, que el autor descarta cada vuelta: «Montedison no se nombra en la voz… la cifra de liras se confunde con la de ENEL»). Los motivos de cada vuelta cambiaron (otros beats), así que «sin progreso» no disparó, y la vuelta 4 chocó con el tope (0,81 + 0,33 > 1,00). Es F38d tal cual (no toqué `llamar`); con el tope del perfil, las 3 vueltas consumieron US$ 0,47 además del intento 1. `cortados_al_cierre`: nada.
- c4. **El respaldo en una persona (P).** Con el respaldo como fuente del candado, en `tipo == "persona"` el cargo de la etiqueta (`palabras_de_contenido` por raíz) también se mira contra el respaldo (el handoff habla de cifras, nombres y años). Ninguna P entró en esta corrida; no se midió.
- c5. **Ninguna ficha cayó por `respaldo` ni por candado** en las 4 llamadas: el modelo copió los respaldos letra por letra. Las cifras salieron todas «literal» (ningún redondeo: e3 de F38e-0 sigue sin medir).
- c6. **Lo que cambió respecto de la prueba 1 además de las citas:** ch06·10 ahora D01 «LA ROCA QUE CAYÓ · 270 millones de metros cúbicos» (antes D86 70 m); ch07·13 D32 «ACUSADOS QUE FALTARON · Otros dos ya habían muerto» (antes D245); ch02·2 volvió a D117 (el `a_pantalla`); ch02·3 D47 recortada a «600 m de desarrollo vertical» (sacó el «2 km» que se le preguntó, aunque quedó «juzgado: otro hecho» porque mantuvo el ítem); ch04·6 T39 entró (en la prueba 1 no había ficha). La columna «¿se entiende solo?» queda vacía (Omar/analista).
- c7. **El `autor` del modelo en Q14 fue «Giovanni Leone»** (pasa: «modelo»); en Q51 «Alberico Biadene» (modelo); en Q50 «Municipio de Erto y Casso» (modelo). En la vuelta 1 el modelo propuso Q50 en la oración [7] y cayó por `cita_sin_fecha` (el autor del archivo no aparece ahí); en la vuelta 3 la recortó a [2] con 86/90.
- c8. **`data/cost_history.json` cambió durante la tanda** (13:04:20, entrada `f8s3-vajont-f30` vacía): no es de C (ver «Foto»). `logs/` sumó archivos de `error_handler` de otros procesos.
- c9. **`editar` (`--plan-edit`)** no pide `respaldo`: una ficha editada a mano no lo lleva (Fase 2 no lo verifica). No se tocó.
- c10. **La copia `vajont_steps/`** pesa 21 MB (incluye `fuentes/`, `_r3_cache`): el handoff pidió copiar la carpeta entera. Si no debe entrar al commit entera, el principal decide qué agregar (el papel nuevo está también en `c/01e_pantalla.*`).

## TABLA.md (pegada tal cual)

# F38e §C — papel m01e-6 de Vajont con vueltas (contra v6 y la prueba 1)

SYSTEM md5 `7d2ccdd28055d6e621d1d251a0fe8bb7` · prompt_md5 `3b98aef1d8595124967ac7a85b75bab7` · claude-sonnet-5-5 (medium) · 4 llamada(s) = intento 1 + 3 vuelta(s) · cerró por **tope** · US$ 0.8096.

| cap·beat | v6 hoy (etiqueta · dato · autor) | prueba 1 | NUEVO m01e-6 con vueltas (etiqueta · dato · autor) | respaldo ✓/✗ | cifras | nombres | validar | car./caben | ¿se entiende solo? | autor mostrado | de dónde salió |
|---|---|---|---|---|---|---|---|---|---|---|---|
| ch01·1 | D84: PRESIÓN DE LA OLA DE AIRE · dos bombas de Hiroshima | D195: LOS QUE VIVÍAN EN LONGARONE · Murieron 1.269 de 1.328 | D195: EL PUEBLO DE MICAELA · 1.269 de 1.328 habitantes murieron | ✓ · respaldo: «con 1.269 de 1.328 habitantes fallecidos» | 1.269 literal; 1.328 literal | — | queda | 54/90 |  | — | — |
| ch02·2 | D117: ACTA DEL CONSEJO SUPERIOR · solo 13 de 34 representantes presentes | D240: SESIÓN DE APROBACIÓN · Asistieron solo 13 de los 34 representantes | D117: SESIÓN QUE LA APROBÓ · Solo 13 de 34 representantes presentes | ✓ · respaldo: «con solo 13 de 34 representantes presentes» | 13 literal; 34 literal | — | queda | 58/90 |  | — | — |
| ch02·3 | D47: FRENTE DEL DESMORONAMIENTO · 2 km de frente y 600 m de desarrollo vertical | D47: TAMAÑO DEL DESMORONAMIENTO · 2 km de frente y 600 m de desarrollo vertical | D47: ALTURA DEL DESMORONAMIENTO · 600 m de desarrollo vertical | ✓ · respaldo: «600 m de desarrollo vertical» | 600 literal | — | queda (juzgado por el autor: {"spoiler": ["2"]}) | 54/83 |  | — | — |
| ch03·4 | T15: VOLUMEN DE LA ROCA · 3 millones de metros cúbicos | T16: EL TRABAJADOR MUERTO · Arcangelo Tiziani | T16: LA VÍCTIMA DE LA OLA · Arcangelo Tiziani | ✓ · respaldo: «mata a Arcangelo Tiziani» | — | Tiziani ✓ | queda | 37/83 |  | — | — |
| ch03·5 | D49: ANCHO DE LA FISURA · Más de 1 metro | D49: ANCHO DE LA FISURA · Más de 1 metro | D49: ANCHO DE LA FISURA · Más de 1 metro | ✓ · respaldo: «una fisura de más de 1 metro de ancho» | 1 literal | — | queda | 32/90 |  | — | — |
| ch04·6 | T39: ROCA QUE AMENAZABA ERTO · 50 millones de metros cúbicos | — | T39: LA ADVERTENCIA DE MERLIN · 50 millones de metros cúbicos de roca | ✓ · respaldo: «un derrumbamiento de 50 millones de metros cúbicos de roca que amenaza Erto» | 50 literal | — | queda (juzgado por el autor: {"spoiler": ["50"]}) | 61/90 |  | — | — |
| ch04·7 | T50: COTA ALCANZADA · 720 metros | D106: SOBRE LA COTA SEGURA · 15 metros de más | D106: SOBRE LA COTA SEGURA · 15 metros | ✓ · respaldo: «15 metros por encima de la cota de seguridad recomendada» | 15 literal | — | queda (juzgado por el autor: {"contradice": ["715"]}) | 29/36 |  | — | — |
| ch05·8 | Q50: DOCUMENTO OFICIAL · en continua aprensión · Administración del comune di Erto e Casso | Q50: LO QUE DECÍAN · «en continua aprensión y en continua alarma» — Municipio de Erto y Casso | Q50: MIEDO POR ESCRITO · «continua aprensión y en continua alarma» · autor del modelo: «Municipio de Erto y Casso» | ✓ · respaldo: «están viviendo en continua aprensión y en continua alarma» · cita literal ✓ | — | — | queda | 86/90 |  | Municipio de Erto y Casso | modelo |
| ch05·9 | Q51: ÚLTIMA LÍNEA DE LA POSDATA · Que Dios nos ayude · Alberico Biadene | Q51: LA ÚLTIMA LÍNEA · «Que Dios nos ayude» — Alberico Biadene | Q51: CIERRE DE LA POSDATA · Que Dios nos ayude. · autor del modelo: «Alberico Biadene» | ✓ · respaldo: «Que Dios nos ayude.» · cita literal ✓ | — | Dios ✓ | queda | 60/90 |  | Alberico Biadene | modelo |
| ch06·10 | D86: ALTURA DEL MURO DE AGUA · 70 metros | D86: EL MURO DE AGUA EN LONGARONE · 70 metros de altura | D01: LA ROCA QUE CAYÓ · 270 millones de metros cúbicos | ✓ · respaldo: «270 millones de metros cúbicos de roca» | 270 literal | — | queda | 46/90 |  | — | — |
| ch06·11 | D128: RECUENTO OFICIAL · 1.910 personas | D128: TOTAL DE MUERTOS · 1.910 personas | D128: VÍCTIMAS · 1.910 personas murieron | ✓ · respaldo: «En el desastre murieron 1.910 personas.» | 1.910 literal | — | queda | 31/57 |  | — | — |
| ch07·12 | Q14: RESPUESTA · Y justicia tendréis · Giovanni Leone | Q14: LA RESPUESTA · «Y justicia tendréis» — Giovanni Leone, presidente del Consejo | Q14: LA RESPUESTA · Y justicia tendréis · autor del modelo: «Giovanni Leone» | ✓ · respaldo: «Y justicia tendréis» · cita literal ✓ | — | — | queda | 50/90 |  | Giovanni Leone | modelo |
| ch07·13 | D245: CONDENA A MONTEDISON · 55.645.758.500 liras | D245: CONDENA A MONTEDISON, 1997 · 55.645.758.500 liras | D32: ACUSADOS QUE FALTARON · Otros dos ya habían muerto | ✓ · respaldo: «dos habían muerto» | 2 literal | — | queda | 47/90 |  | — | — |

## Las 3 citas (Q50, Q51, Q14): ¿entran ahora?

- Q50: **entra** en ch05 beat 8 [2] «MIEDO POR ESCRITO · continua aprensión y en continua alarma» — Municipio de Erto y Casso (autor: modelo) · 86/90 car.
- Q51: **entra** en ch05 beat 9 [17] «CIERRE DE LA POSDATA · Que Dios nos ayude.» — Alberico Biadene (autor: modelo) · 60/90 car.
- Q14: **entra** en ch07 beat 12 [1] «LA RESPUESTA · Y justicia tendréis» — Giovanni Leone (autor: modelo) · 50/90 car.

## Vueltas y gasto

- llamadas: 4 (intento 1 + 3 vuelta(s)) · cerró por **tope** · tope US$ 1.0 (respaldo (el perfil no trae costos.m01e_tope_usd)) · error/aviso: tope US$ 1.00 (respaldo (el perfil no trae costos.m01e_tope_usd)): gastado 0.8096 + esta llamada hasta 0.3308
- intento 1: in 66450 · out 20318 · US$ 0.3361 · 139.8 s
- vuelta 1: in 71417 · out 2433 · US$ 0.1672 · 20.8 s
- vuelta 2: in 70936 · out 421 · US$ 0.1461 · 8.3 s
- vuelta 3: in 71053 · out 1814 · US$ 0.1603 · 20.6 s
- total US$ 0.8096 (suma de cost_of por llamada; ledger en memoria: US$ 0.8096) · peor caso estimado antes de llamar: US$ 0.2804 (OUT_TOKENS_PEOR 16000) / US$ 0.3266 (salida 20623, e4)
- vuelta 1: beats ch02 b3, ch04 b6, ch04 b7, ch05 b8, ch07 b13 · 7 motivo(s) · 2 aplicado(s) · 0 ignorado(s) · US$ 0.1672
  - Q50 (ch05 beat 8) «POR ESCRITO · en continua aprensión y en continua alarma»: cita_sin_fecha: cita sin fecha: su autor («Administración del comune di Erto e Casso», autoridad local) no aparece en la oración [7] ni en sus vecinas
  - D47 (ch02 beat 3, oración [11]) «TAMAÑO DEL DESMORONAMIENTO · 2 km de frente y 600 m de desarrollo vertical»: la voz dice «2» en una oración posterior en ch03 [17] («Ese año hubo un pequeño desmoronamiento en el Toc, y después del desmoronamiento los habitantes vieron algo nuevo en la ladera: una fisura de casi dos kilómetros de largo, corriendo por la montaña como una costura abierta.»); ¿es el mismo hecho? si no, mantenelo
  - T39 (ch04 beat 6, oración [6]) «LA ADVERTENCIA DE MERLIN · 50 millones de metros cúbicos de roca»: la voz dice «50» en una oración posterior en ch05 [17] («Biadene volvió al papel y agregó una posdata: Rossi lo llamaba en ese momento, y «las mediciones de esta mañana resultan todavía mayores que las de ayer, ¡alcanzando un aumento del 50%!!».»); ¿es el mismo hecho? si no, mantenelo
  - D106 (ch04 beat 7, oración [13]) «SOBRE LA COTA SEGURA · 15 metros»: la voz dice «715» para lo mismo, en la oración ancla o en una vecina en ch04 [13] («La cota autorizada fue de setecientos quince.»); ¿es el mismo hecho? si no, mantenelo
  - el beat 8 de ch05 es pico y quedó sin ficha
  - el beat 8 de ch05 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: Q50 («Carta del municipio de Erto y Casso a SADE: documento que se lee en pantalla sobre la escena de los avisos de octubre.»)
  - el beat 13 de ch07 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D245 («Condena a Montedison de 1997: cifra de liras en fallo, ilegible en voz.»)
- vuelta 2: beats ch05 b8, ch07 b13 · 3 motivo(s) · 2 aplicado(s) · 0 ignorado(s) · US$ 0.1461
  - T54 (ch05 beat 8, oración [3]) «LA ORDEN DEL ALCALDE · El alcalde de Erto prohibió acercarse al embalse»: la voz dice «Erto» en la oración ancla o en una vecina en ch05 [2] («Desde el dos de octubre, los avisos se multiplicaron: sacudidas, estruendos que bajaban de la ladera de noche, grietas nuevas en la tierra de Erto, movimientos en la superficie.»); ¿es el mismo hecho? si no, mantenelo
  - el beat 8 de ch05 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: Q50 («Carta del municipio de Erto y Casso a SADE: documento que se lee en pantalla sobre la escena de los avisos de octubre.»)
  - el beat 13 de ch07 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D245 («Condena a Montedison de 1997: cifra de liras en fallo, ilegible en voz.»)
- vuelta 3: beats ch05 b8, ch07 b13 · 5 motivo(s) · 2 aplicado(s) · 0 ignorado(s) · US$ 0.1603
  - Q50 (ch05 beat 8) «CARTA DEL MUNICIPIO A SADE · «Viviendo en continua aprensión y en continua alarma»»: caben: etiqueta 26 + dato 51 + autor 30 (con comillas y raya) = 112 caracteres y en la oración [3] caben 77; en este beat caben como máximo 90 (oración [0])
  - D32 (ch07 beat 13) «LOS QUE NO LLEGARON AL JUICIO · Dos acusados habían muerto y uno se suicidó»: caben: etiqueta 29 + dato 43 = 72 caracteres y en la oración [16] caben 36; en este beat caben como máximo 90 (oración [15])
  - el beat 8 de ch05 es pico y quedó sin ficha
  - el beat 8 de ch05 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: Q50 («Carta del municipio de Erto y Casso a SADE: documento que se lee en pantalla sobre la escena de los avisos de octubre.»)
  - el beat 13 de ch07 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D245 («Condena a Montedison de 1997: cifra de liras en fallo, ilegible en voz.»)
- cortado al cerrar sin preguntar: nada

## Sellos y relojes (no se evalúan: solo que no se hayan roto)

| | v6 hoy | NUEVO (respuesta final del autor) | NUEVO (quedan tras validar) |
|---|---|---|---|
| sellos | 9 | 9 | 9 |
| relojes | 4 | 4 | 4 (sin error) |
| fichas | 13 | 13 | 13 |

Relojes v6: ch01[13] 9 OCT 1963, ch04[0] 4 NOV 1960, ch07[11] 20 FEB 1968, ch07[14] 29 NOV 1968
Relojes NUEVO: ch01[13] 9 OCT 1963, ch04[0] 4 NOV 1960, ch07[11] 20 FEB 1968, ch07[14] 29 NOV 1968
Sellos v6: ch01·1 INMINENTE, ch02·2 CALMA, ch02·3 AMENAZA, ch03·4 AVISO, ch03·5 SILENCIO, ch04·7 ALARMA, ch06·10 PÁNICO, ch07·12 RABIA, ch07·13 MEMORIA
Sellos NUEVO (quedan): ch01·1 PÁNICO, ch02·2 CALMA, ch02·3 AMENAZA, ch03·4 AVISO, ch03·5 INMINENTE, ch05·8 SILENCIO, ch06·10 COLAPSO, ch07·12 RABIA, ch07·13 MEMORIA

## Picos y a_pantalla

- picos: ch01·1 CON ficha D195, ch02·3 CON ficha D47, ch03·4 CON ficha T16, ch04·7 CON ficha D106, ch05·8 CON ficha Q50, ch06·10 CON ficha D01, ch07·12 CON ficha Q14
- picos vacíos: ninguno
- `a_pantalla` de la escaleta: D117 (beat 2): presente, D128 (beat 11): presente, D192 (beat 11): ausente, D245 (beat 13): ausente, Q50 (beat 8): presente
- a_pantalla_vacios: [{'cap': 'ch07', 'beat': 13, 'ids': [{'id': 'D245', 'por_que': 'Condena a Montedison de 1997: cifra de liras en fallo, ilegible en voz.'}]}]

Notas de lectura: «car./caben» con `pantalla_colocar.caracteres` (en una cita, con el autor que se muestra + 5); «cifras» y «nombres» como en la prueba 1 (`verificar` copiado de prueba1_rotulos.py: una cifra seguida de «mil/millones» se escala; «redondeo» = «más de» (menor) o «casi» (mayor) en el campo; `nombres` no ve el que abre el campo ni texto en mayúsculas); el autor va en su columna (modelo / archivo: motivo). «prueba 1» = la respuesta de prueba1.raw.json (sin campo autor: el que figura es el del dato o el del archivo). «NUEVO» = la respuesta final tras las vueltas (`final` del raw); «validar» = lo que hizo la validación final.
