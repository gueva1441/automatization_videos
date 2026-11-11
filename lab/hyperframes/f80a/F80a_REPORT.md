# F80a — reporte de SOLO LECTURA: qué amarra el pipeline al español, a los 13 minutos y al molde del guion

Rama `f11-guion-v4`, base `c0cce6a`. Handoff `lab/hyperframes/f80a/HANDOFF_F80a.md`, md5 `d46f4750301d83b13a8551db9de5d9c3` (verificado). Solo lectura: no se editó código, prompts, config, datos ni tests; ninguna API (US$ 0); ni render, ni TTS, ni corridas del pipeline. El inventario lo hicieron 7 subagentes en paralelo (A-1 Fase 1, A-2 voz / fotos / pantalla, A-3 tema / canal / QA, B, C, D y F) y uno más para E, con lo que dejaron los otros. Las búsquedas se hicieron con `timeout 60 git grep`, excluyendo `lab/`, `_archived/`, `output/`, `data/`, `test_*.py` y `tests/`. `config.py` no está en git (`.gitignore:2`): se leyó del disco y no se copió ninguna llave.

## Resumen
1. **Lo más amarrado al español es el pool.** R3 del research pide que `texto`/`evento` salgan en español y que cada cita traiga `texto_es` (`researcher_steps/research_v3.py:1401, 1408, 1531`). Todo lo que viene después (escaleta, guion, papel, fotos) lee ese pool.
2. **El riesgo más callado son los detectores de fechas y cifras.** Solo entienden español (`evidence.MESES`/`_DATE_TXT`, `num_es`, `voz_utils._NUMW`, `DATE_PARAPHRASE`, `NUM_WORDS`) y con una narración en inglés no fallan: devuelven «no dicho» sin avisar. Deciden `ids_usados`, los bloqueantes y lo que la voz «dice» en pantalla.
3. **Toda la voz y el texto en pantalla son español fijo.** El normalizador entero (`tts_normalizer.py`, `num_es.py`, el prompt de `m02_5_normalizer_gate.py`), los meses del reloj (`voz_datos.MESES`, `gfx_project.py:262`), «CAPÍTULO {n}» (`gfx_layer.py:465`) y `lang="es"` de la plantilla.
4. **El tema se elige con un arbitraje EN→ES**: demanda en virales en inglés, hueco en español. Está en `fase1._measure_es`, `_verify_pick_es_saturation`, `already_es`, `relevanceLanguage` y `topic_validator` `hl="es-ES"`. Un canal en inglés necesita un mercado objetivo por canal en el código, no solo traducir prompts.
5. **Lo más barato de soltar ya es perfil**: `voice_id_v4` / `language_code_v4` (`audio_profiles.py:17/19`), `sellos_clima` y moods (`gfx_profiles/misterio.json`), `GFX_PROFILE` por nicho y `fonts.subs`. Falta poner el valor en inglés.
6. **Duración: el largo ya sale de config** (`video_length.DEFAULTS`, 23 claves). Al doblarlo se rompen tres cosas. `m01d_particion.rebalance` recorta en silencio todo cap que pase su tope de caracteres (`fase1_5.py:712-713`). Las fotos se quedan en 16 por cap, unos 13 s cada una. El render gfx tiene 1500 s por cap (`gfx_config.py:47`) y hoy ya tarda 956–983 s; si se pasa, el cap sale sin gráficos.
7. **El 7 está fijo en código, no solo en prompts**: `CHAPTER_SCHEMA` / `DEFAULT_INTENT_BY_CAP`, dos bloqueantes de la escaleta (`m01a_escaleta.py:278, 438`), dos `ValueError` en m03 (`m03_visual.py:2153, 2157`) y `VEO_CHAPTERS=(1,7)`. DECISIONES 21:44 dice que los 7 caps no se tocan.
8. **El código no lee el texto de ninguna pieza M1–M7.** Lo que viaja río abajo es lo que el modelo devuelve por haberlas leído: `flash_forward`, la `funcion` / `intensidad` del cap 2 y del respiro, y de ahí `narrative_intent` (voz, música, arco visual, golpes de TTS). Las fijan `test_module_f55.py` y `test_module_f54.py`.
9. **Candados**: 16 archivos con test byte-idéntico o de md5 cubren 11 de las 52 llamadas a modelo de producción (E). Un prompt hermano en inglés no los toca. Meter el nombre del canal como dato dentro de un prompt sí les cambia el md5.
10. **Costo (F)**: Wittenoom US$ 46,91 registrados (10,85 de lab) y Colza 19,56. No hay registro de la voz, de las fotos y clips originales, de la música ni del juez m05. Lo que depende del largo: papel, verificador, m03, fotos y voz.

## A. Dónde está amarrado el español

**Cobertura (contrato #2).** Los 9 tipos del §2.A están: prompt 147 · ejemplo 21 · texto_pantalla 17 · voz 24 · karaoke 9 · logica_idioma 163 · api_idioma 21 · canal 23 · rutas 32, 457 filas (cuenta de la columna «tipo» en A-1 + A-2 + A-3). Los módulos del «mínimo a cubrir», con sus filas (cada nº cuenta todas las filas del módulo en A-1 + A-2 + A-3, también las repetidas de A-3.3 «canal» y A-3.4 «api_idioma»; «dónde» nombra cada subsección que suma):

| módulo (mínimo a cubrir del §2.A) | filas | dónde |
|---|---|---|
| `m01a_escaleta` (SYSTEM_V2, TAREA_V2, `validate`) | 28 (27 + 1 de `canal`, A-3.3: l.879, la misma línea de A-1.1) | A-1.1, A-3.3 |
| `guion_v4` (guionista, producción y reparación) | 31 (30 + 1 de `canal`, A-3.3: l.97) | A-1.3, A-3.3 |
| `m01b_guionista` | 2 | A-1.4 |
| `m01c_editor` | 5 | A-1.4 |
| `m01d_particion` (títulos) | 8 | A-1.5 |
| `m01e_pantalla` | 14 + 3 (rotulista, A-2.7) | A-1.6, A-2.7 |
| `m01f` (crítico + `m01f_prompts/`) | 7 (6 + 1 de `canal`, A-3.3: `m01f_prompts/SYSTEM.txt:1`) | A-1.7, A-3.3 |
| `m05_narrative` (juez y `retencion`) | 10 | A-1.8 |
| verificador de narración (`narracion_verificador`, + `dicho_verificador`) | 2 + 2 | A-1.9 |
| ficha (GPT, `ficha_caso`) | 14 (13 + 1 de `canal`, A-3.3: l.139) | A-1.10, A-3.3 |
| perfil y research v3 (R1–R3; + `evidence_pool`, `verify_quotes`) | 21 + 3 + 1 | A-1.11 |
| `tts_tags` | 5 | A-2.2 |
| `normalize_for_tts` (`tts_normalizer.py`) | 11 | A-2.3 |
| `audio_profiles` | 7 (6 + 1 de `api_idioma`, A-3.4: l.19, la misma línea de A-2.1) | A-2.1, A-3.4 |
| `voz_utils` | 11 | A-2.4 |
| m03 (`m03_visual` 14, `m03_imagenes_v3` 9, `m03_expediente` 1; prompts de foto y PERSONAS) | 24 | A-2.6 |
| `foto_madre` | 3 | A-2.6 |
| m09 (`m09_packaging` 9, `m09_review_server` 1) | 10 | A-3.2, A-3.6 |
| m09b | 0: **el módulo no existe** (solo `DECISIONES.md:238` y `fase3.py:6`; `git grep` en A-3) | A-3.2 |
| director de gfx (`gfx_director`) | 1 (solo `rutas`; «no tiene español», `git grep` en A-2.8) | A-2.7 |
| rotulista (hoy dentro de `m01e_pantalla`, F37 §B.4) | ver `m01e_pantalla` | A-1.6, A-2.7 |
| crítico de gfx (`gfx_critic`) | 5 | A-2.7 |
| `gfx_templates/` | 1 (`lang="es"`; el resto «no tiene español», `git grep` en A-2.8) | A-2.7 |
| `pantalla_colocar` | 2 | A-2.7 |
| `gfx_guion` | 1 (solo `rutas`; su español es el texto del documento para Omar, que no llega al modelo, a la voz ni a la pantalla; `git grep` en A-2.8) | A-2.7 |
| gate ES de `fase1` (`_measure_es`, `_verify_pick_es_saturation`, `already_es`) | 7 (+ 4 de `rutas` de fase1 en A-3.6) (+ `subtopic_measurer` 4, `subtopic_es_relevance` 3) | A-3.1, A-3.6 |
| `niche_discoverer` | 16 | A-3.1, A-3.6 |
| `estante` | 4 | A-3.1, A-3.6 |
| QA Studio (`qa_studio_server.py` + plantillas `qa_*.html`) | 9 | A-3.5 |

#### A-1 · Fase 1 (guion): dónde está amarrado el español

Barrido de solo lectura sobre la rama `f11-guion-v4`. No se llamó a ninguna API ni se corrió pytest. Cada `archivo:línea` se abrió y se comparó con lo que dice la fila. Los tests salen de `git grep` sobre `test_*.py` y `tests/` (no se ejecutaron).
Lo que pasa río abajo: la cadena de producción es `fase1_5`: perfil/R1–R3 (research_v3) → 4a–4d → ficha → escaleta v2 → guion v4 (guionista + reparación) → partición → juez m05 → verificador de narración → crítico m01f → papel m01e. El camino viejo y lo que solo se usa con un flag se marcan **(legado)** o **(flag)**.

Abreviaturas de «cómo se volvería dato»: **perfil** = un valor en un perfil por canal; **prompt_por_idioma** = hace falta un prompt hermano en inglés; **codigo** = hace falta lógica por idioma (se dice cuál).

#### A-1.1 Escaleta — `script_engine/m01a_escaleta.py`

| # | archivo:línea | qué es | tipo | tests que lo fijan | cómo se volvería dato |
|---|---|---|---|---|---|
| 1 | script_engine/m01a_escaleta.py:878 | `SYSTEM_V2` «<rol> Sos el guionista jefe…»: el prompt entero, en español | prompt | test_module_f55.py (byte-idéntico a lab/f55/PROMPT_ESCALETA_f55_1.md), test_module_f39_escaleta.py, test_module_f16.py, test_module_f17.py, test_module_f22.py | prompt_por_idioma |
| 2 | script_engine/m01a_escaleta.py:879 | «Sos el guionista jefe de Misterios Sepultados» | canal | test_module_f55.py (byte-idéntico) | perfil (nombre del canal; cambia el md5 fijado) |
| 3 | script_engine/m01a_escaleta.py:883 | «Siete capítulos, de 7 a 14 beats» dentro del prompt | prompt | test_module_f55.py | prompt_por_idioma (y C1) |
| 4 | script_engine/m01a_escaleta.py:895 | ejemplo de imagen «manos contra un vidrio ahumado» | ejemplo | test_module_f55.py | prompt_por_idioma |
| 5 | script_engine/m01a_escaleta.py:897 | regla 9: «Nunca una moraleja, nunca "hoy"» (la palabra española) | prompt | test_module_f55.py | prompt_por_idioma |
| 6 | script_engine/m01a_escaleta.py:903 | `<ejemplo>` del faro: Elvira Soto, «mil novecientos sesenta y ocho», beats 1–8 | ejemplo | test_module_f55.py | prompt_por_idioma |
| 7 | script_engine/m01a_escaleta.py:908 | promesa de ejemplo «Once personas esperaron veintitrés días…» (cifras con letras) | ejemplo | test_module_f55.py | prompt_por_idioma |
| 8 | script_engine/m01a_escaleta.py:936 | bloque `<errores>` con frases en español («la tensión en el aire») | prompt | test_module_f55.py | prompt_por_idioma |
| 9 | script_engine/m01a_escaleta.py:951 | `TAREA_V2` «Con la ficha de arriba, armá la escaleta…» | prompt | test_module_f22.py (md5), test_module_f16.py, test_module_f19.py | prompt_por_idioma |
| 10 | script_engine/m01a_escaleta.py:1226 | `TAREA_COLUMNA` «La columna de arriba ya decidió la historia…» (flag `--columna`) | prompt | test_module_f17.py, test_module_f22.py (md5) | prompt_por_idioma |
| 11 | script_engine/m01a_escaleta.py:1196 | `<rechazo>` «Tu escaleta anterior no pasó estos controles. Corregilos…» | prompt | test_module_f17.py (md5 `ESC_V2_MD5["fb"]`) | prompt_por_idioma |
| 12 | script_engine/m01a_escaleta.py:1202 | «Esta escaleta lleva entre {a} y {b} beats» | prompt | test_module_f19.py, test_module_f7d.py | prompt_por_idioma |
| 13 | script_engine/m01a_escaleta.py:1203 | `<caso>` con los rótulos TÍTULO / ÁNGULO / MISTERIO / REVELACIÓN | prompt | test_module_f17.py (md5) | prompt_por_idioma |
| 14 | script_engine/m01a_escaleta.py:1135 | `ficha_section_v2`: rótulos «historia:», «escenas:», «VERIFICADA / SIN VERIFICAR»… | prompt | test_module_f17.py (md5), test_module_f16.py | prompt_por_idioma (los rótulos) |
| 15 | script_engine/m01a_escaleta.py:1179 | «(traducción: «…»)» en la ficha que lee la escaleta | prompt | test_module_f19.py | prompt_por_idioma |
| 16 | script_engine/m01a_escaleta.py:133 | descripciones del SCHEMA en español (también en 139 y 147) | prompt | — | prompt_por_idioma |
| 17 | script_engine/m01a_escaleta.py:80 | `FUNCIONES`: enum en español («gancho», «planteo», «respiro»…) que devuelve el modelo | logica_idioma | test_module_f23.py (vía `intent_de_cap`) | codigo: se pueden dejar como ids internos, siempre que el prompt en inglés los nombre igual |
| 18 | script_engine/m01a_escaleta.py:81 | `ADMIN_TERMS` («indemnizacion», «expediente», «tribunal»…) de la pregunta de pantalla | logica_idioma | test_module_f6b.py | codigo (una lista por idioma) |
| 19 | script_engine/m01a_escaleta.py:84 | `Q_OPENERS` («quien», «por que», «cuant»…): con qué abre una pregunta válida | logica_idioma | test_module_f6b.py | codigo (una lista por idioma) |
| 20 | script_engine/m01a_escaleta.py:87 | `ABSTRACT`: sustantivos abstractos («desesperacion», «injusticia»…) que hacen que una imagen «es una idea» | logica_idioma | — | codigo (una lista por idioma) |
| 21 | script_engine/m01a_escaleta.py:99 | `NUM_PALABRA` / `NUM_WORDS`: cifras escritas en letras en español | logica_idioma | test_module_f54.py, test_module_f6b.py | codigo (números por idioma; también los usan m01c y guion_v3_reglas) |
| 22 | script_engine/m01a_escaleta.py:212 | la pregunta de pantalla tiene que empezar con «¿» | logica_idioma | test_module_f6b.py | codigo (la puntuación de pregunta por idioma) |
| 23 | script_engine/m01a_escaleta.py:228 | palabras vacías de la pregunta («quien», «cuantos», «nadie», «todavia»…) | logica_idioma | test_module_f6b.py | codigo |
| 24 | script_engine/m01a_escaleta.py:265 | mensajes de `validate` en español (265–577): vuelven al modelo en `<rechazo>` | prompt | test_module_f16.py, test_module_f54.py, test_module_f24.py (los leen por regex) | prompt_por_idioma (y la fila 25) |
| 25 | script_engine/m01a_escaleta.py:964 | `BLOQUEANTES_V2`: regex sobre los mensajes en español («^el beat 1 tiene que ser…») | logica_idioma | test_module_f16.py, test_module_f19.py, test_module_f22.py, test_module_f24.py, test_module_f54.py (vía `bloqueante_de`) | codigo (si se traducen los mensajes, los patrones cambian con ellos; mejor un código estable por bloqueante) |
| 26 | script_engine/m01a_escaleta.py:465 | palabras vacías de la imagen sensorial («sobre», «entre», «mientras»…) | logica_idioma | — | codigo |
| 27 | script_engine/m01a_escaleta.py:1284 | quita el artículo español `^(el\|la\|los\|las) ` al comparar antagonistas (solo con columna) | logica_idioma | — | codigo (sumar «the», como ya hace m01a_columna:263) |

#### A-1.2 Columna — `script_engine/m01a_columna.py` (flag `--columna`)

| # | archivo:línea | qué es | tipo | tests que lo fijan | cómo se volvería dato |
|---|---|---|---|---|---|
| 28 | script_engine/m01a_columna.py:39 | `SYSTEM` de la columna v1.1, entero en español | prompt | test_module_f22.py (igual al .md), test_module_f23.py (md5) | prompt_por_idioma |
| 29 | script_engine/m01a_columna.py:40 | «Sos el guionista jefe de Misterios Sepultados» | canal | test_module_f22.py | perfil |
| 30 | script_engine/m01a_columna.py:60 | `<ejemplo>` del faro (Elvira Soto, CAP 1–7 · QUÉ PASA / TERMINA) | ejemplo | test_module_f22.py | prompt_por_idioma |
| 31 | script_engine/m01a_columna.py:87 | `TAREA` «Con la ficha de arriba, escribí la columna vertebral…» | prompt | test_module_f22.py | prompt_por_idioma |
| 32 | script_engine/m01a_columna.py:93 | `SYSTEM_F17_1` (legado f17-1, también con el canal) | prompt | test_module_f17.py, test_module_f21.py (md5) | prompt_por_idioma, o borrarlo |
| 33 | script_engine/m01a_columna.py:178 | `<rechazo>` «Tu columna anterior no pasó estos controles» | prompt | test_module_f17.py | prompt_por_idioma |

#### A-1.3 Guionista y reparación — `script_engine/guion_v4.py`

| # | archivo:línea | qué es | tipo | tests que lo fijan | cómo se volvería dato |
|---|---|---|---|---|---|
| 34 | script_engine/guion_v4.py:183 | `SYSTEM_V5_6`: el SYSTEM del guionista en producción (f54-2), entero | prompt | test_module_f54.py (byte-idéntico a lab/f54/PROMPT_GUIONISTA_v5_6.md) | prompt_por_idioma |
| 35 | script_engine/guion_v4.py:184 | «Sos el guionista de Misterios Sepultados» | canal | test_module_f54.py | perfil |
| 36 | script_engine/guion_v4.py:184 | «…un canal de documentales… en español neutro» (pide español explícito) | prompt | test_module_f54.py | perfil (idioma y variedad) |
| 37 | script_engine/guion_v4.py:203 | «El video tiene siete capítulos» | prompt | test_module_f54.py | prompt_por_idioma (y C1) |
| 38 | script_engine/guion_v4.py:205 | estructura, punto 1: vuelta atrás «"horas antes", "días antes"» | ejemplo | test_module_f54.py | prompt_por_idioma |
| 39 | script_engine/guion_v4.py:209 | punto 5: «nunca "hoy"» | prompt | test_module_f54.py | prompt_por_idioma |
| 40 | script_engine/guion_v4.py:210 | SIN VERIFICAR por rol: «un mecánico contó», «una de las mujeres recuerda» | ejemplo | test_module_f54.py | prompt_por_idioma |
| 41 | script_engine/guion_v4.py:217 | cifras: «otras fuentes hablan de casi cuatrocientos» | ejemplo | test_module_f54.py | prompt_por_idioma |
| 42 | script_engine/guion_v4.py:219 | fechas: «"ese día", "esa noche", "el miércoles"» (va de la mano con DATE_PARAPHRASE) | ejemplo | test_module_f54.py | prompt_por_idioma y codigo (fila 157) |
| 43 | script_engine/guion_v4.py:226 | `<ejemplos>` del faro: el gancho de la vela, «mil novecientos sesenta y ocho»… | ejemplo | test_module_f54.py | prompt_por_idioma |
| 44 | script_engine/guion_v4.py:258 | `<errores>` con frases reales en español («Esta es la historia de…») | ejemplo | test_module_f54.py | prompt_por_idioma |
| 45 | script_engine/guion_v4.py:622 | `TAREA_V5` «Con la escaleta de arriba, escribí la narración completa…» | prompt | test_module_f15.py, test_module_f15b.py | prompt_por_idioma |
| 46 | script_engine/guion_v4.py:827 | `prompt_v5` `<caso>`: TEMA / HUMANO / PROMESA DEL GANCHO / PICO / CIERRE HUMANO | prompt | test_module_f15.py | prompt_por_idioma |
| 47 | script_engine/guion_v4.py:778 | `escaleta_section_v5`: «BEAT · imagen sensorial · dato central · el espectador se pregunta» | prompt | test_module_f15.py, test_module_f54.py | prompt_por_idioma (los rótulos) |
| 48 | script_engine/guion_v4.py:693 | `mark`: «PANTALLA (no va en la voz)», «SIN VERIFICAR (sin nombre)», «CIFRA OFICIAL» | prompt | test_module_f11.py («SIN VERIFICAR (sin nombre)») | prompt_por_idioma |
| 49 | script_engine/guion_v4.py:774 | marca «VERSIÓN DE: quién» | prompt | test_module_f15.py | prompt_por_idioma |
| 50 | script_engine/guion_v4.py:818 | `loops_txt`: «LOOP k: … — se abre en el beat…, se paga en el beat…» | prompt | — | prompt_por_idioma |
| 51 | script_engine/guion_v4.py:1228 | `PEDIDO_E` (reparación): «La cita va SIN el nombre… (un operario, un testigo…)» | prompt | test_module_f27.py | prompt_por_idioma |
| 52 | script_engine/guion_v4.py:1241 | `edit_sentences`: el prompt de reparación «En este párrafo de un documental hay frases…» | prompt | test_module_f27.py | prompt_por_idioma |
| 53 | script_engine/guion_v4.py:1161 | motivos de los bloqueantes («cifra que no está en el research…»): entran al prompt de 1237 y a las `notas` de regenerate_cap_v3 | prompt | — | prompt_por_idioma |
| 54 | script_engine/guion_v4.py:72 | `DIAS` («lunes»…«domingo») para «ese domingo» | logica_idioma | test_module_f11.py, test_module_f23.py | codigo |
| 55 | script_engine/guion_v4.py:1284 | `replace_repeated_dates`: regex «el/del … de AAAA» → «ese <día>»; reescribe la voz sin modelo | logica_idioma | test_module_f11.py, test_module_f23.py | codigo (patrón y paráfrasis por idioma) |
| 56 | script_engine/guion_v4.py:1127 | `PALABRAS_POR_SEG = 2.4` (medido con el narrador en español, Vajont F26) | logica_idioma | test_module_f27.py, test_module_f57.py | perfil |
| 57 | script_engine/guion_v4.py:96 | `SYSTEM_V5` (legado f15-1, con el canal y «en español neutro» en 97) | prompt | test_module_f15.py | borrarlo, o prompt_por_idioma |
| 58 | script_engine/guion_v4.py:275 | `SYSTEM_V5_4` (legado f25-1; canal y español en 276) | prompt | test_module_f25c.py | borrarlo, o prompt_por_idioma |
| 59 | script_engine/guion_v4.py:361 | `SYSTEM_V5_3` (legado f23-1; canal y español en 362) | prompt | test_module_f23.py | borrarlo, o prompt_por_idioma |
| 60 | script_engine/guion_v4.py:448 | `SYSTEM_V5_2` (legado f22-1; canal y español en 449) | prompt | test_module_f22.py, test_module_f22d.py | borrarlo, o prompt_por_idioma |
| 61 | script_engine/guion_v4.py:535 | `SYSTEM_V5_1` (legado f15b-1; canal y español en 536) | prompt | test_module_f15b.py | borrarlo, o prompt_por_idioma |
| 62 | script_engine/guion_v4.py:644 | `system_f11c` (legado f11c-1) con «en español neutro» en 648 | prompt | test_module_f11c.py | borrarlo, o prompt_por_idioma |
| 63 | script_engine/guion_v4.py:86 | `EJEMPLOS_VOZ` (Orleans, legado f11c) y `OFICIO` en 74 | ejemplo | test_module_f11c.py | borrarlo, o prompt_por_idioma |

#### A-1.4 Validadores de la narración — `m01b_guionista.py`, `m01b_narrator.py`, `m01c_editor.py`

| # | archivo:línea | qué es | tipo | tests que lo fijan | cómo se volvería dato |
|---|---|---|---|---|---|
| 64 | script_engine/m01b_guionista.py:37 | `institution_re` usa las palabras de organización de `nombres._ORG` (métrica del gancho) | logica_idioma | — | codigo (ver fila 168) |
| 65 | script_engine/m01b_guionista.py:166 | gancho: `has_figure` (cifras en letras en español) en las dos primeras frases | logica_idioma | — | codigo (depende de la fila 21) |
| 66 | script_engine/m01b_narrator.py:33 | `FORBIDDEN_OPENINGS` («hoy les voy a contar», «bienvenidos», «qué tal») | logica_idioma | test_module_f41_cadena.py (solo pide que exista `_validate_narration`) | codigo (una lista por idioma) |
| 67 | script_engine/m01b_narrator.py:42 | `FORBIDDEN_CLOSINGS` («suscríbete», «dale like», «hasta la próxima») | logica_idioma | — | codigo (una lista por idioma) |
| 68 | script_engine/m01b_narrator.py:55 | `GENERIC_CONNECTORS` («a continuación», «por otro lado», «veamos ahora») | logica_idioma | — | codigo (una lista por idioma) |
| 69 | script_engine/m01b_narrator.py:23 | `LEN_*` = char_band (palabras × 6 caracteres: la palabra media en español) | logica_idioma | — | perfil (caracteres por palabra) |
| 70 | script_engine/m01c_editor.py:20 | `SYSTEM` del editor «Sos el editor de guion de un canal…» (flag `--editor`) | prompt | — | prompt_por_idioma |
| 71 | script_engine/m01c_editor.py:50 | `build_prompt` «NARRACIÓN DEL GUIONISTA… EDITÁ (solo esto)… NUNCA» | prompt | test_module_f7.py, test_module_f8.py | prompt_por_idioma |
| 72 | script_engine/m01c_editor.py:83 | guardia léxica `_numbers`: usa `NUM_WORDS` (cifras con letras en español) | logica_idioma | test_module_f54.py, test_module_f11b.py | codigo |
| 73 | script_engine/m01c_editor.py:88 | `_names`: toda palabra con mayúscula que no abre la frase es un «nombre nuevo» (en inglés, los meses, los días y «I» van con mayúscula) | logica_idioma | test_module_f11b.py | codigo |
| 74 | script_engine/m01c_editor.py:95 | `_adjs` → `m05_narrative.adjectives` (lista española) | logica_idioma | test_module_f11b.py | codigo (ver filas 114–116) |

#### A-1.5 Partición y títulos — `script_engine/m01d_particion.py`

| # | archivo:línea | qué es | tipo | tests que lo fijan | cómo se volvería dato |
|---|---|---|---|---|---|
| 75 | script_engine/m01d_particion.py:138 | `PEDIDO_TITULOS` «Títulos de capítulo para un documental en español…» | prompt | test_module_f38e_e.py (letra por letra) | prompt_por_idioma |
| 76 | script_engine/m01d_particion.py:200 | `title` del cap (lo que devuelve Flash, en español) → el title card en pantalla | texto_pantalla | test_module_f38e_e.py | prompt_por_idioma (sale de la fila 75) |
| 77 | script_engine/m01d_particion.py:145 | título de respaldo «Capítulo» | texto_pantalla | test_module_f38e_e.py | perfil |
| 78 | script_engine/m01d_particion.py:121 | `editor_shorten` «Acortá este párrafo de un documental…» | prompt | — | prompt_por_idioma |
| 79 | script_engine/m01d_particion.py:349 | `regenerate_cap_v3` «Reescribí el CAP… de un documental en español» (reparación (c) de guion_v4) | prompt | test_module_f11.py, test_module_f11b.py | prompt_por_idioma |
| 80 | script_engine/m01d_particion.py:372 | juicios de ejemplo «fue una masacre», «un infierno», «una bofetada» | ejemplo | — | prompt_por_idioma |
| 81 | script_engine/m01d_particion.py:392 | «TU VERSIÓN ANTERIOR SE RECHAZÓ: … Corregí eso.» | prompt | — | prompt_por_idioma |
| 82 | script_engine/m01d_particion.py:428 | `cut_phrases` «Sacá de este párrafo SOLO estas expresiones» (sin llamadas en producción; solo lab/hyperframes/f10/f10_quirurgico_ycua.py:97: legado) | prompt | — | borrarlo, o prompt_por_idioma |

#### A-1.6 Papel de pantalla — `script_engine/m01e_pantalla.py` y `script_engine/pantalla_verificador.py`

| # | archivo:línea | qué es | tipo | tests que lo fijan | cómo se volvería dato |
|---|---|---|---|---|---|
| 83 | script_engine/m01e_pantalla.py:102 | `PANTALLA_SYSTEM` «Sos el rotulista de un documental… en español» | prompt | test_module_f38e_c.py (md5 85d094be…), test_module_f40_gancho.py, test_module_f37a_papel.py, test_module_f38a_m01e.py | prompt_por_idioma |
| 84 | script_engine/m01e_pantalla.py:111 | regla «el autor va en español, como lo entiende quien mira» | prompt | test_module_f38e_c.py (md5) | perfil (idioma de pantalla) / prompt_por_idioma |
| 85 | script_engine/m01e_pantalla.py:104 | «Reglas de todo texto en pantalla»: el modelo escribe en español la etiqueta y el dato de cada FICHA | texto_pantalla | test_module_f38e_c.py (md5) | prompt_por_idioma |
| 86 | script_engine/m01e_pantalla.py:112 | SELLO DE CLIMA: una palabra de la lista `clima` (la de `sellos_clima` del perfil gfx) | texto_pantalla | test_module_f36c_pantalla.py | perfil (ya sale de `gfx_config.ACTIVE_PROFILE`, vía clima.vocabulario_clima) |
| 87 | script_engine/m01e_pantalla.py:113 | RELOJ: las fechas completas que dice la voz | texto_pantalla | — | codigo (el formato de fecha en pantalla es de gfx) |
| 88 | script_engine/m01e_pantalla.py:123 | `FORMATO_SALIDA`: ejemplo «ANCHO DE LA FISURA», «Más de 1 metro», «AVISO», «9 OCT 1963» | ejemplo | test_module_f37a_papel.py, test_module_f38c_papel.py y test_module_f40_gancho.py (prompt_md5) | prompt_por_idioma |
| 89 | script_engine/m01e_pantalla.py:132 | `FORMATO_REINTENTO`, con el mismo ejemplo en español | ejemplo | test_module_f38c_papel.py, test_module_f40_gancho.py (prompt_md5) | prompt_por_idioma |
| 90 | script_engine/m01e_pantalla.py:136 | `REINTENTO_PARCIAL` «Devolvé solo JSON con `cambios`…» | prompt | test_module_f38c_papel.py (prompt_md5) | prompt_por_idioma |
| 91 | script_engine/m01e_pantalla.py:142 | `SUGERIR_USER` «Omar revisó el papel y quiere OTRAS opciones…» | prompt | test_module_f65b.py | prompt_por_idioma |
| 92 | script_engine/m01e_pantalla.py:147 | `FORMATO_SUGERIR`: ejemplo «ANCHO DE LA FISURA» | ejemplo | test_module_f65b.py | prompt_por_idioma |
| 93 | script_engine/m01e_pantalla.py:277 | fecha «desconocida» en el archivo que lee el modelo | prompt | — | prompt_por_idioma |
| 94 | script_engine/m01e_pantalla.py:79 | importa de voz_utils los analizadores en español (numeros, nombres, anio_de, oraciones_de_texto, _PARTICULAS) | logica_idioma | test_module_f38a_voz.py, test_module_f40_gancho.py | codigo (va con la fila de voz_utils de A-2) |
| 95 | script_engine/m01e_pantalla.py:86 | `SEG_POR_PALABRA_RESPALDO = 0.35` (narrador en español, Vajont ch04) | logica_idioma | test_module_f37a_papel.py, test_module_f40_gancho.py | perfil |
| 96 | script_engine/m01e_pantalla.py:318 | estilo «papel» según `pantalla_filtros.pide_documento` (palabras carta/acta/informe) | logica_idioma | — | codigo (va con la fila de pantalla_filtros, gfx) |
| 97 | script_engine/pantalla_verificador.py:31 | `SYSTEM_V` «Sos el verificador de un documental… en español» | prompt | test_module_f64.py (md5) | prompt_por_idioma |
| 98 | script_engine/pantalla_verificador.py:44 | `FORMATO_V` («pasa» / «corta», «dicho» / «no_dicho») | prompt | test_module_f64.py | prompt_por_idioma (los valores del enum pueden quedar como ids) |

#### A-1.7 Crítico — `script_engine/m01f_critico.py` y `script_engine/m01f_prompts/`

| # | archivo:línea | qué es | tipo | tests que lo fijan | cómo se volvería dato |
|---|---|---|---|---|---|
| 99 | script_engine/m01f_prompts/SYSTEM.txt:1 | SYSTEM del crítico de retención (m01f-2), entero | prompt | tests/test_m01f_compuerta.py (md5, y = lab/f75/a/SYSTEM_m01f-2.txt) | prompt_por_idioma |
| 100 | script_engine/m01f_prompts/SYSTEM.txt:1 | «crítico de retención del canal Misterios Sepultados» | canal | tests/test_m01f_compuerta.py | perfil |
| 101 | script_engine/m01f_prompts/SYSTEM.txt:1 | «documentales en español… de 10 a 12 minutos» | prompt | tests/test_m01f_compuerta.py | perfil (idioma y duración) |
| 102 | script_engine/m01f_prompts/SYSTEM.txt:14 | DEBERÍA «con la misma voz»: el texto vuelve a la narración (la aplica `_aplicar`) | prompt | tests/test_m01f_compuerta.py | prompt_por_idioma |
| 103 | script_engine/m01f_prompts/FORMATO.txt:11 | `deberia_texto` «…con la voz del canal» (placeholders en español en todo el FORMATO) | prompt | tests/test_m01f_compuerta.py (FORMATO = §5 de F67a) | prompt_por_idioma |
| 104 | script_engine/m01f_critico.py:39 | carga `SYSTEM.txt` y `FORMATO.txt` desde una carpeta fija `m01f_prompts/` | rutas | tests/test_m01f_compuerta.py | perfil (carpeta de prompts por idioma) |

#### A-1.8 Juez narrativo y retención — `script_engine/m05_narrative.py`

| # | archivo:línea | qué es | tipo | tests que lo fijan | cómo se volvería dato |
|---|---|---|---|---|---|
| 105 | script_engine/m05_narrative.py:46 | `FORBIDDEN_FILLER` («imaginen», «velo de misterio», «trampa brutal»…) | logica_idioma | test_module_f5c.py | codigo (una lista por idioma) |
| 106 | script_engine/m05_narrative.py:52 | `_STOP` palabras funcionales en español (3-gramas, roles) | logica_idioma | — | codigo |
| 107 | script_engine/m05_narrative.py:58 | `_ADJ_LIST`: adjetivos calificativos en español | logica_idioma | test_module_f5c.py | codigo |
| 108 | script_engine/m05_narrative.py:77 | `_ADJ_SUFFIX` sufijos españoles (-oso, -ble, -ivo, -ante, -ente) | logica_idioma | test_module_f5c.py | codigo |
| 109 | script_engine/m05_narrative.py:78 | `_NOT_ADJ`: sustantivos españoles en -ente/-ante que no son adjetivos | logica_idioma | — | codigo |
| 110 | script_engine/m05_narrative.py:131 | `_date_paraphrased`: con `DATE_PARAPHRASE` («ese domingo»), un evento cuenta como dicho → ids_usados | logica_idioma | test_module_f23.py | codigo (depende de la fila 157) |
| 111 | script_engine/m05_narrative.py:191 | `filler_run`: nombre propio = mayúscula a mitad de frase, con «¿¡» | logica_idioma | — | codigo |
| 112 | script_engine/m05_narrative.py:398 | `retencion` corta las oraciones con `voz_utils.oraciones_de_texto` | logica_idioma | tests/test_m05_retencion.py | codigo (va con la fila de voz_utils de A-2) |
| 113 | script_engine/m05_narrative.py:652 | `date_problems` lee fechas con `ev._DATE_TXT` («29 de agosto de 2005») | logica_idioma | test_module_f5d.py | codigo (depende de la fila 177) |
| 114 | script_engine/m05_narrative.py:486 | por defecto, `data/scripts/_steps` | rutas | — | perfil (raíz por canal) |

#### A-1.9 Verificadores de la narración — `script_engine/narracion_verificador.py` (F66) y `script_engine/dicho_verificador.py` (F55)

| # | archivo:línea | qué es | tipo | tests que lo fijan | cómo se volvería dato |
|---|---|---|---|---|---|
| 115 | script_engine/narracion_verificador.py:31 | `SYSTEM_B` «Sos el verificador de hechos de un documental de historia en español» | prompt | test_module_f66.py (md5 ce31cc51…, igual al lab) | prompt_por_idioma |
| 116 | script_engine/narracion_verificador.py:43 | `FORMATO_B` (estados respaldada / contradice / sin_respaldo) | prompt | test_module_f66.py | prompt_por_idioma (el enum puede quedar como id) |
| 117 | script_engine/dicho_verificador.py:22 | `PREGUNTA` «¿Alguna de estas oraciones dice este hecho…?» | prompt | test_module_f55.py | prompt_por_idioma |
| 118 | script_engine/dicho_verificador.py:36 | `pedido`: «HECHO: / ORACIONES: / Devolvé JSON» | prompt | test_module_f55.py | prompt_por_idioma |

#### A-1.10 Ficha del caso — `researcher_steps/ficha_caso.py` (GPT 6.1 Sol por defecto)

| # | archivo:línea | qué es | tipo | tests que lo fijan | cómo se volvería dato |
|---|---|---|---|---|---|
| 119 | researcher_steps/ficha_caso.py:139 | `SYSTEM_F23_1`: la ficha en producción, entera en español | prompt | test_module_f23.py (= lab PROMPT_FICHA_v2_2.md), test_module_f44.py | prompt_por_idioma |
| 120 | researcher_steps/ficha_caso.py:139 | «Sos el documentalista de Misterios Sepultados» | canal | test_module_f23.py | perfil |
| 121 | researcher_steps/ficha_caso.py:152 | ejemplos del faro (Elvira Soto, giro, escena, hecho nivel 1) | ejemplo | test_module_f23.py | prompt_por_idioma |
| 122 | researcher_steps/ficha_caso.py:167 | «Si «texto» no está en español, «traduccion» lleva la cita en español.» | prompt | test_module_f23.py | perfil (el idioma de salida de la ficha) |
| 123 | researcher_steps/ficha_caso.py:105 | SCHEMA `traduccion`: «la cita en español si «texto» no está en español» | prompt | — | perfil |
| 124 | researcher_steps/ficha_caso.py:345 | `<tarea>` «Con el pool de arriba, armá la ficha del caso…» | prompt | test_module_f44.py | prompt_por_idioma |
| 125 | researcher_steps/ficha_caso.py:329 | `caso_block`: TÍTULO / ÁNGULO / MISTERIO / REVELACIÓN | prompt | test_module_f44.py | prompt_por_idioma |
| 126 | researcher_steps/ficha_caso.py:292 | `item_line`: rótulos «tipo · valor · fecha», «CITA», «sin verificar», «(= arriba)» | prompt | — | prompt_por_idioma |
| 127 | researcher_steps/ficha_caso.py:184 | `SYSTEM_F22_1` (legado f22-1, con el canal) | prompt | test_module_f22.py | borrarlo, o prompt_por_idioma |
| 128 | researcher_steps/ficha_caso.py:228 | `SYSTEM_F15_1` (legado f15-1, con el canal) | prompt | — | borrarlo, o prompt_por_idioma |
| 129 | researcher_steps/ficha_caso.py:53 | `SENT_STOP` palabras vacías en español (chequeo de `sentidos`) | logica_idioma | — | codigo |
| 130 | researcher_steps/ficha_caso.py:383 | `_SCALE` «mil millones · millones · millón · mil» | logica_idioma | test_module_f12.py (l.122), test_module_f15b.py (l.103), vía `unsupported` → `numbers` → `_scaled` | codigo |
| 131 | researcher_steps/ficha_caso.py:384 | `_UNITS` / `_TENS` / `_HUND`: números con letras en español (`word_numbers`) | logica_idioma | test_module_f15b.py (l.104, «treinta y cinco presos», vía `unsupported` → `numbers`) | codigo (números por idioma) |

#### A-1.11 Perfil y research v3 (R1–R3) — `researcher_steps/research_v3.py` y lo que usa (`evidence_pool.py`, `verify_quotes.py`)

| # | archivo:línea | qué es | tipo | tests que lo fijan | cómo se volvería dato |
|---|---|---|---|---|---|
| 132 | researcher_steps/research_v3.py:123 | R1 `build_discovery_prompt` «Sos un documentalista…», en español | prompt | test_module_f23.py, test_module_f77b.py | prompt_por_idioma (opcional: lo que se busca no depende de esto) |
| 133 | researcher_steps/research_v3.py:114 | `idiomas_txt` sin perfil: «INGLÉS y en el idioma del lugar…» | prompt | test_module_f23.py | prompt_por_idioma |
| 134 | researcher_steps/research_v3.py:143 | `DISCOVERY_FOCOS`: los cuatro focos, en español | prompt | test_module_f77b.py | prompt_por_idioma |
| 135 | researcher_steps/research_v3.py:183 | `R1_FORCE_SEARCH` «IMPORTANTE: no respondas de memoria…» | prompt | — | prompt_por_idioma |
| 136 | researcher_steps/research_v3.py:211 | `build_alt_prompt` (Flash) «Buscá en Google, en…» | prompt | — | prompt_por_idioma |
| 137 | researcher_steps/research_v3.py:300 | `annotate_unmatched`: el prompt de fichas del grounding | prompt | — | prompt_por_idioma |
| 138 | researcher_steps/research_v3.py:340 | `build_pista_prompt` «Buscá con Google la página o el PDF…» | prompt | — | prompt_por_idioma |
| 139 | researcher_steps/research_v3.py:1130 | R2 `refine_fichas`: «Para cada documento, su ficha según su PROPIO encabezado…» | prompt | — | prompt_por_idioma |
| 140 | researcher_steps/research_v3.py:1354 | `R3_SYSTEM` «Sos un documentalista que extrae evidencia de UN documento…» | prompt | — | prompt_por_idioma |
| 141 | researcher_steps/research_v3.py:1391 | R3 `build_extraction_prompt`: el prompt de extracción, entero | prompt | test_module_f20.py, test_module_f22.py, test_module_f23.py | prompt_por_idioma |
| 142 | researcher_steps/research_v3.py:1401 | regla 3: «`texto` (datos) y `evento` (cronología) en español» → **el pool entero queda en español** | prompt | — (los tests de R3 miran otras líneas) | perfil (idioma del pool) |
| 143 | researcher_steps/research_v3.py:1408 | regla 6: «`texto_es` traducción natural y fiel (igual si ya está en español)» | prompt | — | perfil |
| 144 | researcher_steps/research_v3.py:1372 | `R3_SCHEMA`: el campo `texto_es` es obligatorio | logica_idioma | test_module_f7.py, test_module_f19.py (fixtures con `texto_es`) | codigo (un nombre de campo neutro, p. ej. `texto_canal`) |
| 145 | researcher_steps/research_v3.py:1531 | la cita del pool toma `texto_es` como `texto` | logica_idioma | test_module_f7.py | codigo |
| 146 | researcher_steps/research_v3.py:2620 | `idiomas_research`: «español siempre al final (es el idioma del pool)» | logica_idioma | test_module_f23.py | perfil |
| 147 | researcher_steps/research_v3.py:897 | `ACCEPT_LANGUAGE = "en,es;q=0.8"` por defecto en las descargas | api_idioma | test_module_f23.py (l.317) | perfil (ya se arma con `idiomas_research`) |
| 148 | researcher_steps/research_v3.py:2643 | `_TERMINO` / `VOCAB_SCHEMA`: la forma «es» de cada rol | logica_idioma | test_module_f20.py | codigo (la clave por idioma del canal) |
| 149 | researcher_steps/research_v3.py:2661 | `seed_vocabulario`: «IDIOMAS DEL RESEARCH: español, inglés» y «en español» | prompt | test_module_f20.py | prompt_por_idioma y perfil |
| 150 | researcher_steps/research_v3.py:2707 | `seed_profile`: el prompt del perfil del seed (Flash) | prompt | test_module_f23.py | prompt_por_idioma |
| 151 | researcher_steps/research_v3.py:1780 | `_COUNT_BASE` («personas», «víctimas») y la regex `[a-záéíóúñ]` de 1789 | logica_idioma | test_module_f20.py, test_module_f23.py | perfil (la base; los `sustantivos_conteo` ya salen del perfil) |
| 152 | researcher_steps/research_v3.py:2169 | `acting_filter` corre sobre los textos del pool en español («verbos en español») | logica_idioma | test_module_f5b.py | codigo (fila 153) |
| 153 | researcher_steps/evidence_pool.py:223 | `person_acts`: `_PASSIVE_AUX`, `_CLITIC`, `_NOT_VERB`, `_VERB_END` (226): un verbo español tras el nombre | logica_idioma | test_module_f5b.py | codigo (detector de acción por idioma) |
| 154 | researcher_steps/evidence_pool.py:289 | `_COMMON_HEADS` («Huracán», «Alcaide», «Recluso») de `fix_caps` | logica_idioma | — | codigo |
| 155 | researcher_steps/evidence_pool.py:502 | `anchor_place`: el lugar principal sale del rol «ciudad» (rol escrito en español por R3) | logica_idioma | test_module_f7.py, test_module_00_evidence_pool.py | codigo |
| 156 | researcher_steps/verify_quotes.py:35 | `build_prompt` «Está traducida al español; el original probablemente está en inglés» (`verify_testimonios`, sin llamadas en la cadena v3) | prompt | — | prompt_por_idioma, o borrarlo |

#### A-1.12 Reglas del guion, nombres, números y evidencia — `guion_v3_reglas.py`, `nombres.py`, `num_es.py`, `evidence.py`

| # | archivo:línea | qué es | tipo | tests que lo fijan | cómo se volvería dato |
|---|---|---|---|---|---|
| 157 | script_engine/guion_v3_reglas.py:204 | `DATE_PARAPHRASE` («ese domingo», «esa noche», «aquel invierno») | logica_idioma | test_module_f23.py | codigo (una lista por idioma) |
| 158 | script_engine/guion_v3_reglas.py:199 | `MESES` / `DATE_RE` «14 de marzo de 1957» (fechas literales por cap) | logica_idioma | test_module_f23.py | codigo |
| 159 | script_engine/guion_v3_reglas.py:47 | `_DATE` del gancho, con los meses en español | logica_idioma | test_module_f7.py | codigo |
| 160 | script_engine/guion_v3_reglas.py:222 | `anios_por_cap`: «mil novecientos…», «dos mil…» + `NUM_PALABRA` | logica_idioma | test_module_f54.py | codigo |
| 161 | script_engine/guion_v3_reglas.py:299 | `_role_before` / `_role_after`: artículos «el, la, los, las, un, una»; es el bloqueante (b) de guion_v4 | logica_idioma | test_module_f21.py (l.118, `role_problems`) | codigo (artículos por idioma) |
| 162 | script_engine/guion_v3_reglas.py:73 | `JUDGMENTS` («deliberad», «a propósito», «sabían que») | logica_idioma | test_module_f7.py (l.556–562, `judgment_problems`) | codigo |
| 163 | script_engine/guion_v3_reglas.py:121 | `_STOP` palabras funcionales en español (repetición entre caps) | logica_idioma | test_module_f7.py | codigo |
| 164 | script_engine/guion_v3_reglas.py:379 | `_ANON_VOICE` «según alguien», «una voz oficial» | logica_idioma | test_module_f7.py (l.623–625), test_module_f22.py (l.310–313), vía `antagonist_problems` | codigo |
| 165 | script_engine/guion_v3_reglas.py:452 | `_PHOTO_ANY` «foto / fotografía» | logica_idioma | test_module_f21.py (l.138–141, `photo_problems`) | codigo |
| 166 | script_engine/guion_v3_reglas.py:467 | `TRAILER`: voz de tráiler en español («esta es la historia de», «quédate») | logica_idioma | test_module_f7.py | codigo |
| 167 | script_engine/nombres.py:20 | `TRATAMIENTOS_BASE`: cargos en español y en inglés mezclados (es casi bilingüe) | logica_idioma | test_module_f20.py, test_module_f21.py | codigo (revisar lo que falta en inglés) |
| 168 | script_engine/nombres.py:100 | `_ORG`: palabras de organización (faltan en inglés «department», «office», «agency», «court», «commission», «government») | logica_idioma | test_module_f21.py | codigo (completar la lista en inglés) |
| 169 | script_engine/nombres.py:103 | `_GRUPO` «group / grupo / segun / según» | logica_idioma | test_module_f21.py | codigo |
| 170 | script_engine/num_es.py:13 | `_U` / `_D` / `_C`: números con letras en español (`words`) | logica_idioma | test_module_f5_narrative.py | codigo (un `num_en` hermano) |
| 171 | script_engine/num_es.py:68 | `variants`: cómo dice la voz una cifra («seis mil quinientas»); lo usan las anclas de evidence | logica_idioma | test_module_f5_narrative.py, test_module_f23.py | codigo |
| 172 | script_engine/num_es.py:60 | `parse_int`: «6.500» y «6,500» son los dos miles (en inglés, «6.5» es decimal) | logica_idioma | test_module_f38c_decimales.py | codigo |
| 173 | script_engine/num_es.py:79 | `hour_words` «seis y diez de la mañana» (lo usa tts_normalizer: A-2) | voz | test_module_f5_narrative.py | codigo |
| 174 | script_engine/evidence.py:21 | `MESES` en español | logica_idioma | test_module_f5_narrative.py, test_module_f7.py | codigo |
| 175 | script_engine/evidence.py:44 | `spoken_date` «29 de agosto» / «agosto de 2006» (ancla de fecha y paráfrasis) | logica_idioma | test_module_f5_narrative.py | codigo |
| 176 | script_engine/evidence.py:63 | `_DAY_MONTH` «\d de <mes>» | logica_idioma | — | codigo |
| 177 | script_engine/evidence.py:343 | `_DATE_TXT` (item_date, spoken_dates, _figures) | logica_idioma | test_module_f5_narrative.py | codigo |
| 178 | script_engine/evidence.py:74 | unidades en español después de una cifra («pies», «metros», «dólares», «años») | logica_idioma | — | codigo |
| 179 | script_engine/evidence.py:109 | `_num_forms` → `num_es.variants`: las cifras dichas con letras | logica_idioma | test_module_f5_narrative.py | codigo |
| 180 | script_engine/evidence.py:117 | `_NUMWORD`: palabras numéricas en español | logica_idioma | — | codigo |
| 181 | script_engine/evidence.py:152 | `_FUNC` palabras funcionales en español (`_content`: dicho A1/A2, same_fact) | logica_idioma | test_module_f55.py | codigo |
| 182 | script_engine/evidence.py:278 | `RANGO` «entre X y Y», «a / al / hasta» | logica_idioma | test_module_f23.py, test_module_f54.py | codigo |
| 183 | script_engine/evidence.py:305 | `_VAGUE_W` («algunos», «muchos», «durante»…) | logica_idioma | — | codigo |
| 184 | script_engine/evidence.py:420 | `fix_glued_caps`: pasa a minúscula un cargo a mitad de oración (en inglés «Sheriff Lee» lleva mayúscula) | logica_idioma | test_module_f21.py, test_module_f5b.py | codigo (apagarlo para el inglés) |

#### A-1.13 Otros módulos de Fase 1 con español amarrado

| # | archivo:línea | qué es | tipo | tests que lo fijan | cómo se volvería dato |
|---|---|---|---|---|---|
| 185 | researcher_steps/step_4c_meta.py:61 | 4c «Eres un editor de contenido viral en español neutro» | prompt | — | prompt_por_idioma |
| 186 | researcher_steps/step_4c_meta.py:98 | «video_title: ≤62 chars en español»: el título del video (entra al <caso> de la escaleta y la ficha) | canal | — | perfil (idioma y largo del título) |
| 187 | researcher_steps/step_4d_summary.py:59 | 4d «Eres un editor de documentales largos…» (y «1,800 palabras») | prompt | — | prompt_por_idioma |
| 188 | researcher_steps/step_4d_summary.py:111 | regla «4. En español neutro.» | prompt | — | perfil |
| 189 | researcher_steps/step_4a_facts.py:24 | 4a «Eres un investigador documental…» (verified_facts) | prompt | — | prompt_por_idioma |
| 190 | researcher_steps/step_4b_canonical.py:46 | 4b: prompt en español que ya pide la salida en inglés (65: «EN INGLÉS, no español») | prompt | — | ninguno para la salida; solo el texto del prompt |
| 191 | researcher_steps/step_4e_visual_canon.py:781 | `TEXTO_1_PEOPLE_GROUPS`: instrucción en español (442: la salida ya se pide en inglés) | prompt | test_module_f50a.py | ninguno para la salida; solo el texto |
| 192 | researcher_steps/step_4e_visual_canon.py:790 | `TEXTO_S5` «Personajes del material (rol · lugar · años…)» | prompt | test_module_f50a.py, test_module_f50d.py, test_module_f50f.py | prompt_por_idioma |
| 193 | topic_researcher.py:490 | stopwords en español del `search_keyword` de respaldo («el», «misterio», «historia») | logica_idioma | — | codigo |
| 194 | topic_researcher.py:669 | `_research_seed_simple` «investigador para contenido viral en español» (SHORT, legado) | prompt | — | borrarlo, o prompt_por_idioma |
| 195 | topic_researcher.py:182 | `_build_angle_query_prompt` (camino v2, RESEARCH_V3=0, legado) | prompt | — | borrarlo, o prompt_por_idioma |
| 196 | script_engine/m01a_skeleton.py:25 | `STEPS_DIR = DATA_DIR / "scripts" / "_steps"`: todos los pasos de Fase 1 de los dos canales en una sola carpeta | rutas | (todos los que usan `STEPS_DIR`) | perfil (raíz por canal) |
| 197 | fase1_5.py:876 | `audio_manager.process_script(…, language="es")` dentro de `process_topic` | api_idioma | — | perfil (va con A-2 audio) |
| 198 | topic_researcher.py:441 | `_sanitize_search_keyword` (def l.426): prefijos en español que borra del `search_keyword` («el misterio de», «desastre nuclear de», «caso de», «naufragio de», artículos `^(el\|la\|los\|las\|un\|una)`, l.441–454); lo llama `_research_seed_deep` (l.627, el camino de producción) y `_research_seed_simple` (l.730, legado) | logica_idioma | — | codigo (prefijos por idioma) |

### Lo que pesa más
1. **El pool es español desde R3** (filas 142–145, 146). Todo lo que viene después (ficha, escaleta, guion, anclas, verificadores) compara contra textos en español. Un canal en inglés necesita primero el idioma del pool en el perfil.
2. **Los detectores de evidencia** (`evidence.py`, `num_es.py`, `guion_v3_reglas.DATE_PARAPHRASE`, `m01a.NUM_WORDS`) deciden `ids_usados`, los bloqueantes (f)/(h) y lo que leen m03 y gfx. Reconocen fechas y cifras solo en español. En inglés no se caen: devuelven «no dicho» sin avisar.
3. **Prompts con candado byte-idéntico o md5**: SYSTEM_V2, SYSTEM_V5_6, PANTALLA_SYSTEM, SYSTEM_B, SYSTEM_V, m01f SYSTEM y ficha F23. Un prompt hermano en inglés no los toca. Meter el nombre del canal como dato del perfil sí cambia sus md5.

### Módulo → nº de filas

| módulo | filas |
|---|---|
| script_engine/m01a_escaleta.py | 27 |
| script_engine/m01a_columna.py | 6 |
| script_engine/guion_v4.py | 30 |
| script_engine/m01b_guionista.py | 2 |
| script_engine/m01b_narrator.py | 4 |
| script_engine/m01c_editor.py | 5 |
| script_engine/m01d_particion.py | 8 |
| script_engine/m01e_pantalla.py | 14 |
| script_engine/pantalla_verificador.py | 2 |
| script_engine/m01f_critico.py + m01f_prompts/ | 6 |
| script_engine/m05_narrative.py | 10 |
| script_engine/narracion_verificador.py | 2 |
| script_engine/dicho_verificador.py | 2 |
| researcher_steps/ficha_caso.py | 13 |
| researcher_steps/research_v3.py | 21 |
| researcher_steps/evidence_pool.py | 3 |
| researcher_steps/verify_quotes.py | 1 |
| script_engine/guion_v3_reglas.py | 10 |
| script_engine/nombres.py | 3 |
| script_engine/num_es.py | 4 |
| script_engine/evidence.py | 11 |
| researcher_steps/step_4a_facts.py | 1 |
| researcher_steps/step_4b_canonical.py | 1 |
| researcher_steps/step_4c_meta.py | 2 |
| researcher_steps/step_4d_summary.py | 2 |
| researcher_steps/step_4e_visual_canon.py | 2 |
| topic_researcher.py | 4 |
| script_engine/m01a_skeleton.py | 1 |
| fase1_5.py | 1 |
| researcher_steps/pool_gate.py | 0: no tiene español (ver abajo) |
| **total** | **198** |

`researcher_steps/pool_gate.py`, **no tiene español**: no tiene prompts y su única regex es una fecha ISO. Los textos en español que tiene son solo del reporte POOL_GATE.md para Omar. Usa `nombres` para contar personas, y eso ya está en las filas 167–169.
```
$ timeout 60 git grep -n -E "re\.(compile|search|findall|sub|match|fullmatch)|español|Misterios|MESES" -- researcher_steps/pool_gate.py
researcher_steps/pool_gate.py:50:    return bool(re.fullmatch(r"\d{4}-\d{2}(-\d{2})?", f) or (tipo_evento == "prolongado" and re.fullmatch(r"\d{4}", f)))
```

### Notas de alcance (no son filas)
- **Ya multilingües, no amarran** (revisados): `research_v3._STOP` / `detect_lang` (721, seis idiomas), `_TAIL_HEAD` (850), `_LANG_CODES` (892), `_OFFICIAL_BASE` (2360, es+en); `nombres.PARTICULAS` / `ARTICULOS` (16, 19, ya con «the»); `m01a_columna.institucion_de_la_ficha` (263, con «the»); `guion_v3_reglas.antagonista_terminos` (435, con «the»).
- **Solo métricas o reportes en español para Omar** (no entran a ningún modelo ni a la pantalla): `to_markdown` de la escaleta y la columna, los mensajes de `m01b_guionista.review`, `cap_review` de m05 (hoy solo métrica en `guion_v4.metricas`), `narracion_verificador.aviso_txt`, `m01e.a_markdown`, `m01f.critica_md`. Pasan a ser filas si alguna vez vuelven a entrar a un prompt.
- **Camino viejo fuera de producción en `evidence_pool.py`**: `_UNRELATED_RE` (172), `_OFICIAL` / `_MEDIOS` / `_COUNT_NOUN` / `_MESES_RE` (571–589), `SYSTEM` (61). Son de research v2. La cadena v3 solo importa de este archivo `fix_caps`, `_content_set`, `norm`, `acting_filter`, `anchor_place` y `geocode`.
- `m01a_escaleta.writer_instructions` (735) solo corre en el camino `escaleta_frozen`: la escaleta v2 llama `apply_pool_plan(…, instrucciones=False)` (1331).
- `script_engine/m05_judge.py` y `m05_PROMPT_v1.txt` son el juez visual de imagen ↔ narración (Fase 2). No se barrieron acá.

#### A-2 · Español amarrado en voz / karaoke / fotos / pantalla

Barrido de solo lectura sobre `c0cce6a` (rama `f11-guion-v4`), con `timeout 60 git grep` y sin `lab/`, `_archived/`, `output/`, `data/`, `tests/` ni `test_*.py`. Cada `archivo:línea` se abrió y se comprobó. La columna «tests» sale de `git grep -l` sobre los `test_*.py` y `tests/` con el literal o el nombre de la función.

Leyenda de «cómo se volvería dato»: **perfil** = un valor en un perfil por canal (audio_profiles / gfx_profiles / un perfil de idioma nuevo) · **prompt_por_idioma** = hace falta un prompt hermano en inglés · **codigo** = hace falta lógica por idioma (se dice cuál).

#### A-2.1 Voz: perfil ElevenLabs, idioma de la API, llamadores

| archivo:línea | qué es | tipo | tests que lo fijan | cómo se volvería dato |
|---|---|---|---|---|
| `audio_config.py:8` | `ACTIVE_AUDIO_PROFILE = "MISTERIO_ABISAL"`: un solo perfil de audio, fijo en el código | canal | test_module_38e_voice_ab.py | perfil (que el canal elija el perfil de audio en vez de un literal) |
| `audio_profiles.py:2` | docstring: «Librería de Presets de Audio para "Ruta de Valor"» | canal | — | perfil (nombre del canal) |
| `audio_profiles.py:14` | `"voice_id": "pqHfZKP75CvOlQylNhV4"`, Bill (v2) | voz | test_module_f9.py | perfil |
| `audio_profiles.py:17` | `"voice_id_v4": "N9Z5MLTIaHFLflaLtbDi"`, MS Narrador v1 (Voice Design de Omar, en español) | voz | test_module_f9.py | perfil (voz inglesa propia) |
| `audio_profiles.py:19` | `"language_code_v4": "es"`, va al payload de ElevenLabs | api_idioma | test_module_f9.py (afirma `language_code == "es"`) | perfil |
| `audio_profiles.py:23` | `"voice_lufs_v4": -24.0`, la v4 llevada al nivel de Bill (medido con MS Narrador) | voz | — | perfil (se mide de nuevo con la voz inglesa) |
| `audio_profiles.py:127` | `VOICE_SETTINGS_BY_INTENT_V4`: stability por intent, calibrada con MS Narrador | voz | test_module_f9.py | perfil (por voz) |
| `audio_manager.py:151` | `_transcribe_word_timestamps(..., language: str = "es")`, Whisper | api_idioma | — (test_module_38_timestamps_lab.py es un script de lab que repite el `language="es"` sin importar audio_manager, l.12 y l.139) | perfil (idioma del canal) |
| `audio_manager.py:498` | `_resolve_text_for_tts(..., language: str = "es")` → fallback `normalize_for_tts` | voz | test_module_f71.py | perfil |
| `audio_manager.py:545` | `_forced_align_elevenlabs(..., language="es")`: no se manda, la API detecta el idioma del texto | api_idioma | test_module_f9.py | ninguno hoy (solo firma); queda como está |
| `audio_manager.py:756` | `process_script(..., language: str = "es")`, idioma de Whisper | api_idioma | test_module_f9.py, test_module_f41_cadena.py | perfil |
| `audio_manager.py:783` | `voice_id = AUDIO_STYLE.get("voice_id") or api.elevenlabs_voice_id` | voz | test_module_f9.py | perfil |
| `audio_manager.py:810` | `"language_code": AUDIO_STYLE.get("language_code_v4") or "es"`, respaldo literal | api_idioma | test_module_f9.py | perfil (sin respaldo `"es"` fijo) |
| `config.py:104` | `elevenlabs_voice_id = "21m00Tcm4TlvDq8ikWAM"  # Rachel (default)`, respaldo global | voz | — | perfil |
| `config.py:105` | `elevenlabs_model = "eleven_multilingual_v2"` (multilingüe: no amarra) | voz | — | ya sirve (informativo) |
| `fase1_5.py:876` | `audio_manager.process_script(audio_script, language="es", ...)` | api_idioma | — | perfil (leer el idioma del canal) |
| `fase2a.py:330` | `audio_process(normalized, language="es")` | api_idioma | — | perfil |

#### A-2.2 Etiquetas TTS (`script_engine/tts_tags.py`)

| archivo:línea | qué es | tipo | tests que lo fijan | cómo se volvería dato |
|---|---|---|---|---|
| `script_engine/tts_tags.py:23` | `GOLPE_MAX_WORDS = 6`: la frase de golpe medida en palabras españolas | voz | test_module_f9.py, test_module_f10.py | perfil (por idioma, si hace falta) |
| `script_engine/tts_tags.py:26` | `SLOWLY_WPS = 2.4`, palabras por segundo de la v4 (MS Narrador) | voz | — (nada lo afirma) | perfil (por voz; se mide de nuevo) |
| `script_engine/tts_tags.py:27` | `_SENT` corta oraciones con cierre `»”"`: comillas angulares españolas | logica_idioma | test_module_f9.py | codigo (comillas del idioma: `“ ”` en inglés) |
| `script_engine/tts_tags.py:45` | `_words`: `[\wáéíóúñü]+` | logica_idioma | test_module_f9.py | codigo (inofensivo en inglés: `\w` ya cubre; se informa) |
| `script_engine/tts_tags.py:70` | golpe solo si `"«" not in s`: la cita se detecta por «» | logica_idioma | test_module_f9.py, test_module_f23.py | codigo (marca de cita por idioma) |

Las etiquetas (`[long pause]`, `[quietly]`, `[whispers]`, `[slowly]`, l.21–22) ya están en inglés: son de ElevenLabs v4 y no amarran.

#### A-2.3 Normalizador (números a letras, siglas, abreviaturas)

| archivo:línea | qué es | tipo | tests que lo fijan | cómo se volvería dato |
|---|---|---|---|---|
| `tts_normalizer.py:32` | `ACRONYMS_PRONOUNCEABLE`: «OVNI», «OTAN», «ONU», «SIDA»… | voz | — | perfil (diccionario por idioma) |
| `tts_normalizer.py:39` | `ACRONYMS_SPELLED`: `"FBI": "efe be i"`, `"EE.UU.": "Estados Unidos"` | voz | test_module_subs_remap.py (usa «efe be i») | perfil (diccionario por idioma) |
| `tts_normalizer.py:57` | `ABBREVIATIONS_ES`: `"Sr.": "señor"`, `"Dr.": "doctor"`… | voz | — | perfil |
| `tts_normalizer.py:69` | `UNITS_MAP`: `"km/h": "kilómetros por hora"` | voz | — | perfil |
| `tts_normalizer.py:94` | borde de sigla con `[A-Za-zÁÉÍÓÚÑáéíóúñ]` | logica_idioma | — | codigo (inofensivo en inglés; se informa) |
| `tts_normalizer.py:114` | `_RE_MONEY_MILL`: `(millones|mil millones|millón)` | voz | test_module_f5_narrative.py | codigo (normalizador en inglés) |
| `tts_normalizer.py:127` | decimal → «noventa y ocho coma siete» | voz | test_module_f5_narrative.py | codigo |
| `tts_normalizer.py:141` | `normalize_pool_forms`: «… de dólares», «… dólares», «… por ciento» (l.141–143) | voz | test_module_f5_narrative.py, test_module_f71.py | codigo (formas habladas en inglés) |
| `tts_normalizer.py:152` | `normalize_for_tts(text, language="es")` | voz | test_module_01b_pauses.py, test_module_f5_narrative.py, test_module_f71.py | perfil (idioma del canal) |
| `tts_normalizer.py:162` | `if language != "es":` → avisa «no soportado» y devuelve el texto tal cual | logica_idioma | test_module_f71.py | codigo (rama inglesa) |
| `tts_normalizer.py:181` | `CUSTOM_DICT_PATH = DATA_DIR / "normalizer_custom_dict.json"`: un diccionario para todos | rutas | test_qa_studio.py | perfil (un diccionario por idioma o canal) |
| `script_engine/num_es.py:13` | `_U/_D/_C`: «cero… veintinueve», «treinta»…, «doscientos»… (l.13–19) | voz | test_module_f5_narrative.py, test_module_f38c_decimales.py | codigo (conversor inglés, `num_en`) |
| `script_engine/num_es.py:41` | `words(n, fem)`: femenino «quinientas», «veintiuna» | voz | test_module_f5_narrative.py | codigo (el inglés no tiene género; otra función) |
| `script_engine/num_es.py:68` | `variants`: las formas en que la voz dice una cifra (dígitos y letras ES) | logica_idioma | test_module_f5_narrative.py | codigo |
| `script_engine/num_es.py:79` | `hour_words`: «seis y diez de la mañana», «las veintiuna» | voz | test_module_f5_narrative.py | codigo |
| `script_engine/m02_5_normalizer_gate.py:43` | `STEPS_DIR = DATA_DIR / "scripts" / "_steps"` (escribe `01b_narration_normalized.json`) | rutas | test_module_f39_fase1.py | perfil (carpeta por canal si los ids chocan) |
| `script_engine/m02_5_normalizer_gate.py:97` | SYSTEM: «Sos un auditor de pronunciación TTS para ElevenLabs en español neutro» | prompt | test_module_f5_narrative.py, test_chat33_hhmm.py | prompt_por_idioma |
| `script_engine/m02_5_normalizer_gate.py:126` | categoría GENDER: «"31 muertes" … "treinta y una muertes"» (l.126–153) | ejemplo | test_module_f5_narrative.py | prompt_por_idioma (en inglés la categoría sobra) |
| `script_engine/m02_5_normalizer_gate.py:159` | FOREIGN_WORD: «palabras en latín/inglés … que ElevenLabs ES no pronuncia» | prompt | — | prompt_por_idioma |
| `script_engine/m02_5_normalizer_gate.py:185` | YEAR_FORMAT: «"1986" → "mil novecientos ochenta y seis"» | ejemplo | test_module_f5_narrative.py | prompt_por_idioma |
| `script_engine/m02_5_normalizer_gate.py:194` | TIME_FORMAT_HM: «"22:00" → "las veintidós"» | ejemplo | test_chat33_hhmm.py | prompt_por_idioma |
| `script_engine/m02_5_normalizer_gate.py:293` | «"reasoning" en español, una línea, máx 20 palabras» | prompt | — | prompt_por_idioma (o queda en español para Omar) |
| `script_engine/m02_5_normalizer_gate.py:357` | user prompt: «Auditá las siguientes narraciones documentales en español neutro» | prompt | test_module_f5_narrative.py | prompt_por_idioma |
| `anchor_timing.py:56` | `normalize_for_tts(anchor, language="es")` para el trigrama de anclas | voz | test_module_135e_matcher.py, test_module_f71.py | perfil (idioma del canal) |
| `anchor_timing.py:84` | `normalize_pool_forms(texto)` (formas habladas ES) dentro del matcher | logica_idioma | test_module_f71.py | codigo (sigue a `normalize_pool_forms`) |

#### A-2.4 Utilería de la voz (`voz_utils`, `voz_datos`)

| archivo:línea | qué es | tipo | tests que lo fijan | cómo se volvería dato |
|---|---|---|---|---|
| `script_engine/voz_utils.py:20` | `_NUMW`: regex de números en letras ES («cero|uno|…|millon(?:es)?|y») | logica_idioma | test_module_f38a_voz.py, test_module_f29b_rotulista.py | codigo (detector de números en letras por idioma) |
| `script_engine/voz_utils.py:27` | `_w2n`: palabras → entero con `num_es.words` (masc. y fem.) | logica_idioma | test_module_f38c_decimales.py | codigo |
| `script_engine/voz_utils.py:73` | `nombres`: mayúsculas `[A-ZÁÉÍÓÚÑ]`, abre oración tras `¿¡«` (l.73–78) | logica_idioma | test_module_f38e_c.py | codigo (en inglés las mayúsculas de títulos y días también son nombres) |
| `script_engine/voz_utils.py:116` | `_ARTPREP`: «de, del, la, las, el, los, un, una…» | logica_idioma | — | perfil (lista de función por idioma) |
| `script_engine/voz_utils.py:129` | `_PARTICULAS` de nombres: «de, del, da, … van, von, la, le, y» | logica_idioma | — | perfil |
| `script_engine/voz_utils.py:154` | `_UNIDAD_1`: «metros», «personas», «víctimas», «liras»… | logica_idioma | test_module_f38a_voz.py | perfil (unidades por idioma) |
| `script_engine/voz_utils.py:158` | `_UNIDAD_2`: `("metros","cubicos")`, `("por","ciento")` | logica_idioma | — | perfil |
| `script_engine/voz_utils.py:160` | `_MAGNITUD` («nivel», «cota», «muert») y `_DIFERENCIA` («por encima», «más que») l.160–161 | logica_idioma | — | perfil |
| `script_engine/voz_utils.py:171` | fracciones: «medio», «media», «cuarto», «tercio», «un/una/uno» (l.171–174) | logica_idioma | test_module_f38a_voz.py | codigo |
| `script_engine/voz_utils.py:382` | `dice_anio`: «década del cincuenta = 1950: así se dicen los años en castellano» | logica_idioma | — | codigo |
| `script_engine/voz_utils.py:402` | `seg_por_palabra`: mediana por `voice_id` sobre `output/audio/*` | voz | test_module_f37a_papel.py, tests/test_m01f_compuerta.py, tests/test_m05_retencion.py | ya es por voz; una voz inglesa nueva arranca sin datos (usa el respaldo del que llama) |
| `script_engine/voz_datos.py:15` | `MESES = {"enero": "ENE", … "septiembre": "SEP", … "diciembre": "DIC"}` | texto_pantalla | test_module_f34.py (`"OCT"`), test_module_f37b_colocar.py (`"FEB"`) | perfil (abreviaturas de mes por idioma: JAN…DEC) |
| `script_engine/voz_datos.py:47` | `_MES_RE`: «(enero|febrero|…|setiembre|…|diciembre)» | logica_idioma | test_module_f34.py | perfil (meses por idioma) |
| `script_engine/voz_datos.py:65` | fecha = «<día> de <mes> de <año>» (`toks[i-1] != "de"`) | logica_idioma | test_module_f34.py | codigo (inglés: «October 9, 1963» / «9 October 1963») |
| `script_engine/voz_datos.py:98` | `"month": MESES["septiembre" if mes == "setiembre" else mes]`, el reloj desde la voz | texto_pantalla | test_module_f34.py, test_module_f36.py | perfil |

#### A-2.5 Subtítulos quemados (karaoke Shorts y documental long-form)

| archivo:línea | qué es | tipo | tests que lo fijan | cómo se volvería dato |
|---|---|---|---|---|
| `fase2b.py:120` | `letra_px = 60.0` («Anton 60 px»); fuente = `fonts.subs` del perfil | karaoke | test_module_f40_subs.py, test_constantes_con_origen.py | ya es perfil (Anton tiene el alfabeto inglés) |
| `fase2b.py:124` | `max_chars_renglon = 42`, `max_renglones = 2`, `min_dur`, `max_dur` (l.124–127): «estándar: Netflix Timed Text Style Guide» | karaoke | test_module_f40_subs.py | perfil (la guía Netflix es por idioma: se cita la del inglés) |
| `fase2b.py:248` | `_ASS_STYLE_VIRAL = ("Style: Viral,Anton,150,…")` (Shorts) | karaoke | test_module_f40_subs.py | ya sirve (fuente latina) |
| `fase2b.py:352` | karaoke Shorts: `sin_comillas` saca `«`, `»`, `…` (Anton dibuja » como >>) | karaoke | test_module_f30b.py | codigo (comillas del idioma) |
| `fase2b.py:398` | `_doc_limpio`: el subtítulo documental saca `«` `»` `…` (l.398–402) | karaoke | test_module_f40_subs.py (`"«" not in src`) | codigo (en inglés quedarían `“ ”` sin tratar) |
| `fase2b.py:549` | `_DIC_ES = pyphen.Pyphen(lang="es_ES")`, sílabas en español | karaoke | test_module_38d_forcealign_integration.py (test_module_38b_forced_align_cap1.py trae su propia copia de `_chars_to_syllables`, l.131, y no importa fase2b) | perfil (código pyphen), pero ver nota: rama sin llamador en producción |
| `fase2b.py:562` | `_chars_to_syllables`: corta palabras en `".,;:!?\"'()¿¡"` | karaoke | test_module_38d_forcealign_integration.py | codigo (misma nota) |
| `fase2b.py:1221` | `remap_words_to_original(original_text, norm_words)`: subtítulo = texto original, tiempos del normalizado | karaoke | test_module_subs_remap.py, test_module_f36c_pantalla.py | ya es neutro (diff de tokens) |
| `subs_remap.py:21` | `_PUNCT = ".,;:!?\"'()¿¡—–-«»…“”"` para comparar tokens | karaoke | test_module_subs_remap.py | ya sirve (trae `“ ”`); se informa |

Nota: `_build_ass_from_syllables` (fase2b.py:592) y `_chars_to_syllables` (l.552) no tienen llamador en producción. Solo los usan `_regen_alignments_chat38.py`, `_smoke_chat38_ch01.py` y dos tests. El long-form usa `_build_ass_documental` (l.1232) y los Shorts `_build_ass_from_words` (l.1243).

#### A-2.6 Fotos: m03 y foto madre

| archivo:línea | qué es | tipo | tests que lo fijan | cómo se volvería dato |
|---|---|---|---|---|
| `script_engine/m03_visual.py:189` | SI v2: text_in_image «IN SPANISH (the audience reads Spanish — … 'PRÓFUGO')» | prompt | test_module_f8b.py (l.162: afirma que el SI v3 ya no lo trae) | prompt_por_idioma (v2; v3 lo reemplaza, ver l.224) |
| `script_engine/m03_visual.py:212` | SI v2: «TEXT DISCIPLINE: … text_in_image slot, in Spanish.» | prompt | — | prompt_por_idioma (v2) |
| `script_engine/m03_visual.py:224` | SI v3: reemplaza «IN SPANISH» por «LANGUAGE OF THE PLACE» (l.224–227) | logica_idioma | test_module_f8b.py | ya no depende del canal (informativo) |
| `script_engine/m03_visual.py:476` | «PERSONAS DOCUMENTADAS (el nombre es solo para el casillero persona; … NUNCA el nombre)» | prompt | test_module_f60_a3.py, test_module_f78c.py, test_module_f78d.py | prompt_por_idioma (encabezado en español; lo lee Opus; `persona` lo cita textual) |
| `script_engine/m03_visual.py:493` | «PERSONAS DOCUMENTADAS: (vacío) — si la narración nombra a alguien, describilo por rol…» | prompt | test_module_f60_a3.py | prompt_por_idioma |
| `script_engine/m03_visual.py:499` | «OBJETOS DOCUMENTADOS (mantené la FORMA GENERAL constante…)» | prompt | test_module_f78d.py | prompt_por_idioma |
| `script_engine/m03_visual.py:512` | «ANACRONISMOS PROHIBIDOS: (vacío).» | prompt | — | prompt_por_idioma |
| `script_engine/m03_visual.py:522` | «USO (2 capas): la capa ÉPOCA es genérica; la capa LUGAR PUNTUAL…» (l.522–529) | prompt | — | prompt_por_idioma |
| `script_engine/m03_visual.py:591` | «Narration (Spanish, for context only — emit JSON in English):» | prompt | test_lab_v5.py, test_lab_v6.py, test_lab_v7_bhopal.py | perfil (nombre del idioma de la narración) |
| `script_engine/m03_visual.py:1094` | `_build_topic_block`: «Título», «DATOS DUROS», «DESCRIPCIÓN CANÓNICA…» (l.1094–1105) | prompt | test_module_f48.py | prompt_por_idioma |
| `script_engine/m03_visual.py:1949` | «NARRATOR OVER THIS CLIP (Spanish, context only): «{voz_clip}»» | prompt | test_module_f50b.py | perfil (nombre del idioma) |
| `script_engine/m03_visual.py:2086` | `"lang": v3img.place_language(topic)`, el idioma del texto en la foto es el del lugar | logica_idioma | test_module_f58_a3.py, test_module_f59_a1.py | ya es dato (informativo) |
| `script_engine/m03_visual.py:1803` | `_DEFAULT_RETRY_CHECKLIST` y `_ANCHOR_ONLY_RETRY_CHECKLIST` (l.1819): «REGLA 7 — narration_anchor = SUBSTRING EXACTO… Copiá literal.», en español, van al modelo en cada reintento (l.1379, 1396, 1860) | prompt | — | prompt_por_idioma |
| `script_engine/m03_visual.py:1878` | `feedback` de `_call_with_validation_retry`: «RETRY n/m — TU INTENTO PREVIO FALLÓ…» (l.1881), se suma al prompt (`prompt + feedback`) | prompt | test_qa_studio.py::test_fix_core_tres_validaciones_fallidas_no_genera (corre el `_call_with_validation_retry` real, l.441; l.707 afirma «RETRY 2/» en el segundo pedido; no fija el texto en español) | prompt_por_idioma |
| `script_engine/m03_imagenes_v3.py:187` | «its sensory image, in Spanish: translate it» | prompt | test_module_f8b.py | perfil (nombre del idioma del guion) |
| `script_engine/m03_imagenes_v3.py:207` | `MOTIFS`: regex inglés + español (`pasillos?`, `podio`, `barrotes`…) (l.207–216) | logica_idioma | — | codigo (la parte ES lee `imagen_sensorial`; en inglés, palabras inglesas) |
| `script_engine/m03_imagenes_v3.py:364` | `WEAPON_ES`: «rifles?|fusil|disparo|francotirador|armas?|balas?…» sobre `imagen_sensorial` | logica_idioma | test_module_f8b.py | codigo (detector en inglés para el guion inglés) |
| `script_engine/m03_imagenes_v3.py:385` | `SCALE_ES`: «cientos|centenares|miles|multitud…» | logica_idioma | test_module_f8b.py | codigo |
| `script_engine/m03_imagenes_v3.py:387` | `PEOPLE_ES`: «hombres|mujeres|presos|reclusos|personas|gente…» | logica_idioma | test_module_f8b.py | codigo |
| `script_engine/m03_imagenes_v3.py:413` | `SPANISH_WORDS`: «[ñáéíóú¿¡]|de|del|la|…|prófugo» | logica_idioma | test_module_f8b.py, test_module_f59_a1.py | ya sirve (detecta español fuera de lugar; en un canal inglés sigue valiendo) |
| `script_engine/m03_imagenes_v3.py:428` | `place_language`: `idioma_local` con «españ», «italia», «ingl» | logica_idioma | test_module_f8b.py, test_module_f58_a3.py | perfil (`idioma_local` lo escribe el research en español) |
| `script_engine/m03_imagenes_v3.py:440` | `fix_text_slot`: `if lang != "es" and SPANISH_WORDS.search(txt)` borra el texto | logica_idioma | test_module_f8b.py, test_module_f59_a1.py | codigo (la regla cuida que no haya español donde no va; en un canal inglés falta lo mismo para un lugar hispanohablante) |
| `script_engine/m03_imagenes_v3.py:486` | COMPOSITION_RULES 7: «Never Spanish on documents of another country.» | prompt | test_module_f61.py | prompt_por_idioma (o queda: sigue siendo cierto) |
| `script_engine/m03_expediente.py:39` | año de la foto vía `vu.numeros(cl)` (años dichos en letras ES) | logica_idioma | test_module_f50b.py, test_module_f50c.py | codigo (sigue a `voz_utils.numeros`) |
| `foto_madre.py:431` | `PROMPT_RASGOS = """Estas son personas reales de un documental…` (pide la salida en inglés) | prompt | test_module_f78a.py | prompt_por_idioma (opcional: la salida ya es inglesa) |
| `foto_madre.py:509` | `PROMPT_ESTADOS = """Cada fila es una persona real de un documental…` (gemelo de `PROMPT_RASGOS`; pide la salida en inglés; lo usa l.528) | prompt | test_module_f78a.py (l.477, `startswith(fm.PROMPT_ESTADOS)`) | prompt_por_idioma (opcional: la salida ya es inglesa) |
| `foto_madre.py:628` | `cache = OUTPUT_DIR / vid / "foto_madre" / RASGOS_JSON` | rutas | test_module_f78a.py, test_module_f78c.py | perfil (carpeta por canal si los ids chocan) |
| `script_engine/video_prompt.py:54` | `PEDIDO_CON_FINAL`: «NARRATION DURING THE CLIP (Spanish):» (gemelo de `m03_visual.py:1949`; lo usa asset_manager.py:948/979) | prompt | test_module_f57.py (l.142, igual letra por letra) | perfil (nombre del idioma) |
| `script_engine/video_prompt.py:67` | `PEDIDO_FINAL`: «NARRATION DURING THE SHOT (Spanish; …)» (instrucción de edit del último cuadro) | prompt | test_module_f57.py (l.142, l.151) | perfil (nombre del idioma) |
| `script_engine/flow_director.py:40` | `_SYSTEM_PROMPT` «Eres director de cinematografía…» (DepthFlow); el pedido le pasa la narración española («Narración:», l.85). Lo usan fase2b, flow_config y parallax_animator_v2 | prompt | — | prompt_por_idioma (la salida es un enum de movimiento) |
| `script_engine/zoom_judge.py:34` | `_SYSTEM` «Sos un clasificador visual. Mirás UNA imagen…» (lo usan fase2b, flow_config, depth_probe, gfx_layer y gfx_vision) | prompt | — | prompt_por_idioma (la salida es una categoría) |
| `script_engine/vision_validator.py:54` | `VISION_SYSTEM_PROMPT` «Eres un auditor visual…», con `reason` «en español» (l.73) (lo usa asset_manager) | prompt | — | prompt_por_idioma (la salida es un veredicto) |

#### A-2.7 Pantalla: gfx (director, rotulista, crítico, visión, plantillas, perfil)

| archivo:línea | qué es | tipo | tests que lo fijan | cómo se volvería dato |
|---|---|---|---|---|
| `script_engine/gfx_layer.py:465` | title card: `{"kicker": f"CAPÍTULO {n}", "title": titulo}` | texto_pantalla | test_module_f79.py, test_module_gfx_config.py, test_module_f34.py, test_module_gfx_lock.py | perfil (rótulo «CHAPTER») |
| `gfx_config.py:490` | `CHROME_TEMPLATES = ("CAPÍTULO {n}", "DETALLE")`: el cromo que el candado literal deja pasar (`chrome_strings`, l.495; lo lee `gfx_literal_lock.py:39`). Si el kicker de l.465 pasa a «CHAPTER {n}» y esta tupla no, el candado quita el title card | texto_pantalla | test_module_gfx_config.py (l.88), test_module_gfx_lock.py (l.29–31) | perfil (va junto con el kicker de gfx_layer.py:465) |
| `script_engine/gfx_project.py:262` | reloj: `head = f'{tk["day"]} {tk["month"]}'` → «29 AGO» (orden día-mes) | texto_pantalla | test_module_f5f.py | perfil (orden de la fecha por idioma: «AUG 29») |
| `script_engine/gfx_pool.py:458` | cambio de fecha del reloj: `MESES[ev.MESES[int(cm) - 1]]` (meses ES → ENE…DIC) | texto_pantalla | test_module_f5f.py, test_module_gfx_pool.py | perfil (meses por idioma) |
| `script_engine/gfx_pool.py:462` | primera fecha del reloj: `month = MESES[ev.MESES[int(m) - 1]]` | texto_pantalla | test_module_gfx_pool.py | perfil |
| `script_engine/gfx_pool.py:52` | `IMPERIAL`: «pies?|millas?|yardas?|pulgadas?|libras?|galones?» | logica_idioma | — | perfil (unidades por idioma) |
| `script_engine/gfx_pool.py:122` | `EDGE_STOP`: palabras vacías ES («de, del, la… fue, era, más», l.122–124) que deciden los bordes de cláusula y el kicker (`pool_clause_options` / `_kicker`, m01a_skeleton) | logica_idioma | test_module_f5b.py (vía `pool_clause_options`, l.127) | codigo (lista de función por idioma) |
| `script_engine/gfx_pool.py:126` | `_VERB_EDGE`: terminaciones verbales ES «ó|aron|ieron|ando|endo…» (corte de cláusula, lo usa m01a_skeleton) | logica_idioma | test_module_f5b.py | codigo (cortador de cláusulas en inglés) |
| `script_engine/gfx_pool.py:131` | `_MONTHS` y `_DATE_RE`: «\d{1,2} de <mes>( de \d{4})?» (l.131–133) | logica_idioma | test_module_f5b.py | codigo |
| `script_engine/gfx_pool.py:151` | `_PARTICIPLE`: «(ado|ada|ados|…|idas)$» | logica_idioma | test_module_f5b.py | codigo |
| `script_engine/gfx_pool.py:186` | `_AUX` («es, son, fue, …») y `_PAST` («ó|aron|ieron…») l.186–188 | logica_idioma | test_module_f5b.py | codigo |
| `script_engine/gfx_pool.py:479` | `_COUNT_NOUNS` («personas|reclusos|…|muertos») y `_APPROX` («más de|aproximadamente|…») l.479–480 (conteos de m01a_escaleta) | logica_idioma | test_module_gfx_pool.py | perfil (listas por idioma) |
| `script_engine/gfx_templates/index.html.tmpl:2` | `<html lang="es" data-resolution="landscape">` del render | texto_pantalla | — | perfil (cambia el corte y las mayúsculas del navegador) |
| `gfx_profiles/misterio.json:3` | `"description": "Perfil del canal … (Ruta de Valor)…"` | canal | — | perfil (perfil gfx propio del canal inglés) |
| `gfx_profiles/misterio.json:23` | `"callout_sec_per_word": 0.4`, segundos de lectura por palabra | logica_idioma | test_constantes_con_origen.py | perfil |
| `gfx_profiles/misterio.json:73` | `"sellos_clima": ["PÁNICO", "CALMA", "AMENAZA", "AVISO", … "MEMORIA"]` | texto_pantalla | test_module_f36c_pantalla.py, test_module_f37a_papel.py, test_module_f38a_m01e.py, test_module_f64.py | perfil (ya es perfil; hace falta la lista inglesa) |
| `gfx_profiles/misterio.json:75` | `moods.*.triggers` / `icon_words`: «veneno», «cadáver», «inundación», «humo»… (l.75–83) | logica_idioma | test_module_gfx_lab.py (l.250–256, `triggers` e `icon_words` del perfil activo; con datos), test_module_gfx_emphasis.py (l.20–24, 25 disparadores por categoría) | perfil (léxico inglés) |
| `gfx_profiles/misterio.json:107` | `"channel_bug": {"svg": "bug/channel_bug.svg", …}`, la mosca del canal | canal | — | perfil |
| `gfx_profiles/icons/icons_index.json:3` | índice game-icons → `"es": ["gafas", "lentes"]…` (una clave `es` por ícono) | logica_idioma | test_module_gfx_auto_icons.py | perfil (índice por idioma) |
| `gfx_config.py:38` | `DEFAULT_PROFILE: str = "misterio"` | canal | test_module_gfx_profiles.py | perfil (ya hay `GFX_PROFILE` y nicho → perfil) |
| `gfx_config.py:344` | `active_profile_name`: «GFX_PROFILE (env) > perfil cuyo `nichos` contiene el nicho activo > misterio» | canal | test_module_gfx_profiles.py | ya es perfil (informativo: es la costura para el segundo canal) |
| `script_engine/gfx_icons/auto_icons.py:28` | SYSTEM: «Traducís nombres de íconos (en inglés…) a palabras en español» | prompt | test_module_gfx_auto_icons.py | prompt_por_idioma (en inglés no hace falta traducir) |
| `script_engine/gfx_icons/auto_icons.py:41` | `lemmas`: plural y género ES («celdas → celda», «ahogadas → ahogado») | logica_idioma | test_module_gfx_auto_icons.py | codigo |
| `script_engine/gfx_critic.py:27` | `_side`: «izquierda» / «derecha» dentro del pedido | prompt | test_module_gfx_critic.py, test_module_f37b_colocar.py | prompt_por_idioma |
| `script_engine/gfx_critic.py:33` | `describe`: «SELLO rojo con la palabra «…»», «RECORTE de diario…», «FICHA…» (l.32–41) | prompt | test_module_gfx_critic.py, test_module_f30b.py, test_module_f36.py | prompt_por_idioma |
| `script_engine/gfx_critic.py:67` | `SYSTEM_ROT = ("Sos el editor final de un documental de historia oscura…")` | prompt | test_module_f30b.py, test_module_f36.py | prompt_por_idioma |
| `script_engine/gfx_critic.py:70` | `PREGUNTA_ROT_1..3`: «¿El bloque estorba: tapa un rostro…?» (l.70–72) | prompt | test_module_f30b.py, test_module_f36.py | prompt_por_idioma |
| `script_engine/gfx_critic.py:82` | `build_prompt_rot`: «LA NARRACIÓN…», «BLOQUE:», «IMAGEN 1: la foto sola…» (l.82–95) | prompt | test_module_f30b.py, test_module_f36.py | prompt_por_idioma |
| `script_engine/gfx_vision.py:41` | SYSTEM: «label = 1–3 palabras en español (… «candado»)» (l.39–43) | prompt | test_module_gfx_vision.py | prompt_por_idioma (el label no sale a pantalla: solo cuenta `tipo`) |
| `script_engine/gfx_vision.py:95` | user: «Devolvé solo el JSON.» | prompt | test_module_gfx_vision.py | prompt_por_idioma |
| `script_engine/gfx_intensity.py:34` | `SENSORY_PAIRS`: «putrefacta / catástrofe», «cadáveres / tragedia»… | ejemplo | — | prompt_por_idioma |
| `script_engine/gfx_intensity.py:36` | SYSTEM: «Sos editor de un documental de misterio. Leés la narración…» (corre con `intensity_director`, misterio.json:64) | prompt | test_module_gfx_intensity.py, test_module_f5e.py | prompt_por_idioma |
| `script_engine/gfx_intensity.py:64` | `build_prompt`: el mensaje de usuario «CATEGORÍAS DEL CANAL (usá SOLO estas claves)», «CAPÍTULO (frases numeradas):», «Devolvé:» (l.67–78; lo usa l.196) | prompt | test_module_gfx_intensity.py (l.54, «peso 1 NO es carga») | prompt_por_idioma |
| `script_engine/gfx_intensity.py:213` | `_VERB_FORM` («ó|aron|ando|arse…») y `_NOT_VERB_FORM` («cara», «agua»…) l.213–216 | logica_idioma | test_module_f5e.py | codigo |
| `script_engine/gfx_realizador.py:26` | `_NUM_PALABRA`: «uno, una, dos … millones» (l.26–29) | logica_idioma | — | perfil |
| `script_engine/gfx_realizador.py:89` | `_raices`: raíz de 5 letras sin `_NUM_PALABRA` ni `ev._FUNC` (stopwords ES) | logica_idioma | — | codigo (en inglés la raíz de 5 letras rinde distinto; lista de función inglesa) |
| `script_engine/gfx_peak.py:16` | `_clean`: saca `¿¡"«(` y `.,;:!?"»)` antes de buscar en el léxico | logica_idioma | test_module_f5f.py (l.29–30, vía `clima.peak_word` → `lexicon_hits` (clima.py:144) → `_clean` (gfx_peak.py:38): «flotando.» pasa por `_clean` y el test afirma «cadáveres»; no fija las comillas) | codigo (comillas del idioma) |
| `script_engine/gfx_peak.py:52` | `prefer_icon_nouns` usa `m05_narrative.adjectives` (detector de adjetivos ES) | logica_idioma | test_module_f5f.py | codigo (sigue a m05) |
| `script_engine/clima.py:19` | `TEMA_DE_MOOD`: «veneno», «radiación», «abandono»… (campo `tema` del sello) | logica_idioma | test_module_f36.py, test_module_f37b_colocar.py | perfil |
| `script_engine/clima.py:27` | `vocabulario_clima` lee `sellos_clima` del perfil activo (en misterio.json:73) | texto_pantalla | test_module_f36c_pantalla.py, test_module_f37b_colocar.py | ya es perfil (informativo) |
| `script_engine/clima.py:102` | `palabra_voz`: limpia `¿¡"'«“(` y `.,;:!?…"'»”)` | logica_idioma | test_module_f36.py | ya sirve (trae `“ ”`); se informa |
| `script_engine/pantalla_colocar.py:19` | `LECTURA_CPS = 15.0`: «estándar de subtitulado, el más lento» | logica_idioma | test_module_f37b_colocar.py | perfil (la guía de lectura es por idioma) |
| `script_engine/pantalla_colocar.py:208` | cita en pantalla: `f"«{b['pantalla']}» — {it['autor']}"` | texto_pantalla | test_module_f37b_colocar.py | perfil (comillas del idioma: `“…”`) |
| `script_engine/pantalla_filtros.py:24` | `LOCALES` / `PALABRAS_LOCALES`: «cota», «nivel», «altura» (l.24–25) | logica_idioma | — | perfil |
| `script_engine/pantalla_filtros.py:95` | `_DOC = re.compile(r"\b(carta|acta|informe|documento)s?\b")` → sale como recorte | logica_idioma | test_module_f7.py | perfil |
| `script_engine/pantalla_verificador.py:31` | `SYSTEM_V = """Sos el verificador de un documental de historia oscura en español…` | prompt | test_module_f36c_pantalla.py, test_module_f38e_c.py, test_module_f64.py, test_module_f65b.py | prompt_por_idioma |
| `script_engine/m01e_pantalla.py:102` | `PANTALLA_SYSTEM`: «Sos el rotulista de un documental de historia oscura en español… (7 capítulos…)» | prompt | test_module_f37a_papel.py, test_module_f38a_m01e.py, test_module_f64.py | prompt_por_idioma (puede estar repetida con A-1) |
| `script_engine/m01e_pantalla.py:112` | «SELLO DE CLIMA: … Una palabra de la lista…» (la lista sale de `sellos_clima`) | prompt | — | prompt_por_idioma (puede estar repetida con A-1) |
| `script_engine/m01e_pantalla.py:124` | FORMATO_SALIDA de ejemplo: «"ANCHO DE LA FISURA"», «"Más de 1 metro"», sello «"AVISO"», reloj «"9 OCT 1963"» (l.124–127) | ejemplo | test_module_f38a_m01e.py, test_module_f64.py | prompt_por_idioma (puede estar repetida con A-1) |
| `script_engine/gfx_director.py:25` | `DATA_DIR / "scripts" / f"{video_id}.json"` y `_steps/<topic_id>` (l.30) | rutas | test_module_f34.py, test_module_gfx_layer_fallback.py | perfil (carpeta por canal si los ids chocan) |
| `script_engine/gfx_guion.py:710` | escribe `output/<topic>/GUION_PANTALLA.md` / `.json` (en español para Omar) | rutas | test_run_pipeline.py | perfil (carpeta por canal); el idioma del documento puede quedar en español |

#### A-2.7b Música: prompts del director musical (`script_engine/m07_music_director.py`)

| archivo:línea | qué es | tipo | tests que lo fijan | cómo se volvería dato |
|---|---|---|---|---|
| `script_engine/m07_music_director.py:214` | `_MATCHER_SYSTEM_INSTRUCTION` «Sos un asistente especializado en seleccionar música…», en español; elige la pista por el «anchor» (la primera frase del cap, en español). El mensaje de usuario también («CAPÍTULO NUEVO:», «CANDIDATOS DE LA LIBRARY», l.256–260). Corre en `generate_music_map` (l.1106/1111, desde fase1_5.py:900) | prompt | — (test_module_f28b.py l.173 reemplaza `_match_intent_to_track`) | prompt_por_idioma |
| `script_engine/m07_music_director.py:1212` | `plan_composicion`: «THE CHANNEL SOUND (Spanish, the brief every track must fit):» | prompt | — (test_module_f28a.py l.46–53 arma el pedido pero no fija «Spanish») | perfil (nombre del idioma); sin llamador en producción (`git grep plan_composicion` fuera de lab y tests: solo la def) |

#### A-2.8 Módulo → nº de filas

| módulo | filas |
|---|---|
| audio_config.py | 1 |
| audio_profiles.py | 6 |
| audio_manager.py | 6 |
| config.py (voz) | 2 |
| fase1_5.py / fase2a.py (llamadores de la voz) | 2 |
| script_engine/tts_tags.py | 5 |
| tts_normalizer.py (`normalize_for_tts`, `normalize_pool_forms`) | 11 |
| script_engine/num_es.py | 4 |
| script_engine/m02_5_normalizer_gate.py (normalizador LLM) | 8 |
| anchor_timing.py | 2 |
| script_engine/voz_utils.py | 11 |
| script_engine/voz_datos.py | 4 |
| fase2b.py (subtítulos `_build_ass_*`) | 8 |
| subs_remap.py | 1 |
| script_engine/m03_visual.py | 14 |
| script_engine/m03_imagenes_v3.py | 9 |
| script_engine/m03_expediente.py | 1 |
| foto_madre.py | 3 |
| script_engine/video_prompt.py | 2 |
| script_engine/flow_director.py | 1 |
| script_engine/zoom_judge.py | 1 |
| script_engine/vision_validator.py | 1 |
| script_engine/gfx_layer.py | 1 |
| script_engine/gfx_project.py | 1 |
| script_engine/gfx_pool.py | 9 |
| script_engine/gfx_templates/ | 1 |
| gfx_profiles/ (misterio.json, icons_index.json) | 6 |
| gfx_config.py | 3 |
| script_engine/gfx_icons/auto_icons.py | 2 |
| script_engine/gfx_critic.py | 5 |
| script_engine/gfx_vision.py | 2 |
| script_engine/gfx_intensity.py | 4 |
| script_engine/gfx_realizador.py | 2 |
| script_engine/gfx_peak.py | 2 |
| script_engine/clima.py | 3 |
| script_engine/pantalla_colocar.py | 2 |
| script_engine/pantalla_filtros.py | 2 |
| script_engine/pantalla_verificador.py | 1 |
| script_engine/m01e_pantalla.py (rotulista; ver A-1) | 3 |
| script_engine/gfx_director.py | 1 (solo `rutas`) |
| script_engine/gfx_guion.py | 1 (solo `rutas`) |
| script_engine/m07_music_director.py (A-2.7b) | 2 |
| **total** | **156** |

`voz_utils` existe como `script_engine/voz_utils.py`. `normalize_for_tts` vive en `tts_normalizer.py:152`. El rotulista ya no es un módulo gfx: desde F37 §B.4 es `m01e_pantalla` (el «papel»). `gfx_director.py` quedó sin modelo ni texto (docstring l.5–9).

Módulos sin español que llegue al modelo, a la voz o a la pantalla, con el comando que lo muestra:

- **`script_engine/gfx_director.py`**: no tiene español en ningún literal; queda solo la fila de `rutas`.
  ```
  $ timeout 60 git grep -n -E '"[^"]*[áéíóúñ¿¡«»][^"]*"' -- script_engine/gfx_director.py
  (sin salida)
  ```
- **`script_engine/gfx_templates/`** (title_card, archive_clipping, scene, gfx_grade.json, gfx_common.css): no tienen español, salvo `lang="es"` de `index.html.tmpl:2` (fila arriba). Lo demás son comentarios CSS que no se dibujan.
  ```
  $ timeout 60 git grep -n -i -E 'lang=|[áéíóúñ¿¡«»]' -- script_engine/gfx_templates/
  script_engine/gfx_templates/gfx_common.css:8:      /* title_card (F2 §0b.2: escala ${tc_scale}); F29c: la ficha usa las mismas clases, sin #tc-dim */
  script_engine/gfx_templates/gfx_common.css:15:      /* F32 §B.8: la ficha del rotulista, un escalón más chica: …
  script_engine/gfx_templates/gfx_common.css:18:      /* data_callout (tercio superior, lado según el sujeto) */
  script_engine/gfx_templates/gfx_common.css:24:      /* animaciones firma (F2 §2): cascade = …
  script_engine/gfx_templates/gfx_common.css:34:      /* F3: ícono de la categoría como viñeta dentro del dato y del recorte */
  script_engine/gfx_templates/gfx_common.css:42:      /* archive_clipping (F2 §0b.6: escala ${ar_scale}, lado opuesto al sujeto; cuerpo ≥ 52 px) */
  script_engine/gfx_templates/gfx_common.css:58:      /* grade CSS (lab v1, ajuste v2): sobre escenas, bajo los gráficos. Intensidad en gfx_config */
  script_engine/gfx_templates/gfx_common.css:68:      /* Playfair SC: sin ligaduras (la "fi" minúscula rompía las versalitas: "fiGURABAN").
  script_engine/gfx_templates/index.html.tmpl:2:<html lang="es" data-resolution="landscape">
  ```
- **`script_engine/gfx_guion.py`**: tiene español (118 líneas con tilde, ñ o «»), pero es el texto del documento de revisión para Omar (GUION_PANTALLA.md/.json), que no llega al modelo, a la voz ni a la pantalla. No llama a ningún modelo y sus tres regex no tienen palabras españolas (l.180 corta etiquetas `[…]`, l.190 el fin de oración `[.!?…]$`, l.614 tokeniza con `[^\W_]+`). El chequeo 5 usa `pantalla_filtros.contradicciones` (l.440), que ya tiene sus filas en A-2.7. Su único amarre propio es la ruta (fila arriba).
  ```
  $ timeout 60 git grep -c -E '[áéíóúñ¿¡«»]' -- script_engine/gfx_guion.py
  script_engine/gfx_guion.py:118
  $ timeout 60 git grep -n -E "gemini|claude_helpers|openai|anthropic|elevenlabs|call_(pro|flash|opus)|requests\." -- script_engine/gfx_guion.py; echo "exit=$?"
  exit=1
  $ timeout 60 git grep -n -E "re\.(compile|search|findall|sub|match|fullmatch|split)\(" -- script_engine/gfx_guion.py
  script_engine/gfx_guion.py:180:    for tok in re.split(r"(\[[^\]]+\])", tts_text or ""):
  script_engine/gfx_guion.py:190:    fin = [g for g in gaps if re.search(r"[.!?…]$", str(raw[g[1]]["word"]).strip())]
  script_engine/gfx_guion.py:614:    return " ".join(re.findall(r"[^\W_]+", ev.norm(str(s or ""))))
  ```

#### A-2.9 Descartados (con motivo)

- `gfx_profiles/misterio_critico_fewshot.json` y `gfx_profiles/misterio_golden_ch02.json:223` (`"month": "AGO"`): ningún `.py` los lee. El crítico few-shot se borró en F36 §D (gfx_critic.py l.11). Comando: `timeout 60 git grep -n "critico_fewshot\|golden_ch02" -- '*.py' …` → sin lectores fuera de `misterio.json:108` (`identity.golden_plan`, metadato).
- `script_engine/gfx_review.py:53` (`<html lang="es">`): página interna de revisión, no se renderiza en el video.
- `script_engine/gfx_vision.py:35` (`TIPOS = ("rostro", "manos", …)`): claves internas del enum; no dependen del idioma del canal.
- `gfx_project.py:194` (cita con `&ldquo; &rdquo;` y `&mdash;`): ya son comillas inglesas, no amarran.
- Las fuentes Anton y Playfair Display SC (`misterio.json:5-11`, `gfx_common.css:1-7`) tienen el alfabeto latino completo y no hace falta cambiarlas para inglés.

#### A-2.10 Fuera de alcance (visto al pasar)

- `config.py:103` guarda una clave de API de ElevenLabs como literal en el archivo del disco. `config.py` NO está en git (`.gitignore:2`; `git ls-files config.py` vacío), así que no está versionada. No se copia acá. No es del contrato F80a.
- `script_engine/evidence.py:21` (`MESES = ("enero", …)`), `evidence.py:152` (`_FUNC`, stopwords ES) y `script_engine/guion_v3_reglas.py:199` (`MESES`) los usan módulos de esta parte (`gfx_pool`, `voz_utils`, `gfx_realizador`), pero son de la capa de texto (A-1). Se dejan para esa sección.
- `script_engine/m05_narrative.py` (`adjectives`, trigramas `TRIGRAM_MAX`): lo usa `gfx_peak`, pero es de A-1.

#### A-3 · Tema, canal, publicación, rutas y QA (dónde está amarrado el español)

Barrido con `timeout 60 git grep -n …` sobre la rama `f11-guion-v4`, sin `lab/`, `_archived/`, `output/`, `data/`, `tests/` ni `test_*.py`. Cada línea citada se abrió y dice lo que la fila afirma. Los tests solo aparecen en la columna «tests que lo fijan».

**Lo más importante de esta parte:** la elección de tema entera es un **arbitraje EN→ES**: busca virales en inglés (demanda) y mide el hueco en español (competencia). En un canal en inglés el mercado de la demanda y el de la competencia pasan a ser el mismo, así que no alcanza con traducir prompts: el gate, los umbrales y el juez de semillas necesitan un **mercado objetivo por canal** (`codigo` + `perfil`).

**config.py no está en git**: `.gitignore:2` lo ignora (`git ls-files config.py` no devuelve nada). La copia local define `OUTPUT_DIR = BASE_DIR / "output"` (config.py:30) y `DATA_DIR = BASE_DIR / "data"` (config.py:32), y no tiene ningún parámetro de idioma ni de región (sin `lang`, `hl`, `gl` ni `"es"`). Como no está en git, no se cita en las tablas como amarre versionado. Las rutas cuelgan todas de esas dos constantes.

#### A-3.1 Gate ES y descubrimiento de temas (fase1 · subtopic_measurer · subtopic_es_relevance · youtube_scanner · niche_discoverer · m_judge_seeds · topic_validator · estante)

| archivo:línea | qué es | tipo | tests que lo fijan | cómo se volvería dato |
|---|---|---|---|---|
| fase1.py:52 | `from script_engine.subtopic_measurer import _measure_es` · gate del pick atado a ES | logica_idioma | test_chat52_pick_gate.py (todos) | codigo: `_measure_<mercado>` según el mercado del perfil |
| fase1.py:326 | `print(f"      hueco ES: {label} · {ontopic_str}")` | logica_idioma | — | perfil: etiqueta del mercado objetivo |
| fase1.py:372 | `_ES_LABEL_RANK = {"VACIO"…"SATURADO"}` · ranking de saturación ES | logica_idioma | test_chat52_pick_gate.py::test_flip_disputado | codigo: mismo rango, nombre neutral por mercado |
| fase1.py:399 | `_measure_es(recipe["es_query"], …, already_es=recipe.get("already_es", False))` | logica_idioma | test_module_f77a.py, test_chat52_pick_gate.py::test_estable_sin_aviso | codigo: receta `{query, entity, already_in_market}` + mercado del perfil |
| fase1.py:420 | `def _verify_pick_es_saturation(chosen, n=3)` · re-mide ES y pregunta P/S/Q | logica_idioma | test_chat52_pick_gate.py::test_flip_sacar/test_flip_producir/test_sin_receta, test_module_f74.py, test_module_f42b.py | codigo: gate por mercado del canal |
| fase1.py:444 | `"re-mido ES {n}× (API oficial, solo > {SHORTS_MAX_S} s)"` | logica_idioma | — | perfil: nombre del mercado |
| fase1.py:801 | `chosen = _verify_pick_es_saturation(chosen, n=3)` · el gate se llama siempre | logica_idioma | — (test_module_f42b.py l.106 la reemplaza por la identidad) | codigo |
| script_engine/subtopic_measurer.py:70 | `def _measure_es(search_query, entity=None, already_es=False)` · saturación ES | logica_idioma | test_es_measure_offline.py, test_es_saturation_judge.py, test_chat52_already_es.py::test_unit_branching | codigo: `_measure_market(…, market)` |
| script_engine/subtopic_measurer.py:88 | `if already_es:` · no traduce si el tema ya viene en español | logica_idioma | test_chat52_already_es.py::test_unit_branching | codigo: «ya en el idioma del canal» |
| script_engine/subtopic_measurer.py:99 | `tr = translate_to_es(search_query)` · traduce EN→ES antes de buscar | logica_idioma | test_chat52_already_es.py, test_chat51_subject_angle.py | codigo: en canal EN no se traduce |
| script_engine/subtopic_measurer.py:107 | `cands = list_spanish_candidates(es_query)` · competencia solo en español | logica_idioma | test_module_f77a.py, test_es_measure_offline.py | codigo: `list_candidates(query, lang)` |
| script_engine/subtopic_es_relevance.py:29 | `_TRANSLATE_SYSTEM` (27): «grafía con la que el público hispanohablante la busca» | prompt | — (test_chat52_atomic_aliases.py lo mockea) | prompt_por_idioma (o se saltea en EN) |
| script_engine/subtopic_es_relevance.py:56 | `'ENTIDAD (en inglés): {name}'` · «Devolvé su grafía española de búsqueda» | prompt | — | prompt_por_idioma |
| script_engine/subtopic_es_relevance.py:86 | `_RELEVANCE_SYSTEM` (84): «…títulos de videos de YouTube en español» | prompt | — (test_es_saturation_judge.py lo corre en vivo con Gemini, l.24/46; no lo fija) | prompt_por_idioma |
| script_engine/youtube_scanner.py:128 | `def detect_language(title) -> Literal["es", "en", "other"]` (langdetect) | logica_idioma | — | codigo: sirve tal cual, el que llama pasa el idioma |
| script_engine/youtube_scanner.py:144 | `is_fresh`: `["hora", "día", "dia", "semana", "hour", "day", "week"]` | logica_idioma | — | codigo: lista bilingüe (ya trae inglés; revisar) |
| script_engine/youtube_scanner.py:202 | `_parse_date_scrapetube_months_ago`: `"día"…"semana"`, `"mes"` (204), `"año"` (206) | logica_idioma | test_t5_sentinel.py | codigo: ya bilingüe; fijarlo por test en inglés |
| script_engine/youtube_scanner.py:221 | `_STOPWORDS` «Stopwords ES + genéricos del nicho marino/misterio» (219) | logica_idioma | — | codigo: stopwords por idioma |
| script_engine/youtube_scanner.py:234 | stopwords de nicho en español: `"sonido", "ruido", "océano"…` | logica_idioma | — | perfil: stopwords del nicho por canal |
| script_engine/youtube_scanner.py:380 | `for lang_code in ("es", "en"):` · fallback API cuenta ES y EN | api_idioma | — | codigo: pares de mercado según perfil |
| script_engine/youtube_scanner.py:390 | `"relevanceLanguage": lang_code` (search.list) | api_idioma | — | codigo (el valor sale del par de arriba) |
| script_engine/youtube_scanner.py:737 | `_scrape_viral_english` (def l.712; la llama `search_viral_english`, l.848): `if detect_language(title) != "en": continue` · demanda solo EN | logica_idioma | — (test_chat50_seed_enrichment.py l.93 y test_chat51_subject_angle.py l.100/123 reemplazan `search_viral_english`) | perfil: idioma de la demanda |
| script_engine/youtube_scanner.py:798 | `"relevanceLanguage": "en"` · virales EN por la API | api_idioma | — | perfil: idioma de la demanda |
| script_engine/youtube_scanner.py:927 | `_scrape_spanish_competition`: `if detect_language(title) != "es"` | logica_idioma | — | codigo: idioma de la competencia por perfil |
| script_engine/youtube_scanner.py:990 | `"relevanceLanguage": "es"` · fallback competencia ES (Regla 3-50-24) | api_idioma | — | perfil: idioma de la competencia |
| script_engine/youtube_scanner.py:1162 | `score_spanish_saturation`: `if detect_language(title) != "es"` | logica_idioma | — (test_chat52_already_es.py la nombra solo en el docstring, l.5) | codigo |
| script_engine/youtube_scanner.py:1255 | `_api_spanish_candidates`: `"relevanceLanguage": "es"` (gate F77) | api_idioma | test_module_f77a.py::test_api_primero_sin_shorts_y_shape (afirma `== "es"`) | perfil: idioma de la competencia |
| script_engine/youtube_scanner.py:1283 | `_api_spanish_candidates`: filtra títulos `!= "es"` | logica_idioma | test_module_f77a.py::test_api_primero_sin_shorts_y_shape | codigo |
| script_engine/youtube_scanner.py:1327 | `_scrape_spanish_candidates`: filtra títulos `!= "es"` | logica_idioma | test_module_f77a.py | codigo |
| script_engine/youtube_scanner.py:492 | `ES_SAT_HUECO = 30_000` / `ES_SAT_DISPUTADO = 150_000` (493) · umbrales del mercado ES | logica_idioma | — (test_es_saturation_judge.py los usa en vivo, con Gemini y scrape, y no los fija) | perfil: umbrales por mercado (el mercado EN es otro tamaño) |
| script_engine/transcript_fetch.py:50 | `fetch_transcript(video_id, languages=("en", "es"))` | api_idioma | test_transcript_fetch.py | perfil (para EN alcanza; impacto bajo) |
| niche_discoverer.py:9 | docstring: «Busca virales en INGLÉS … cruza con ES via scrapetube» · el arbitraje | logica_idioma | — | codigo: modo de descubrimiento por canal |
| niche_discoverer.py:128 | `ROOT_NICHES["oceano"]["es_name"] = "Misterios del Océano"` (y 142, 156) | canal | test_module_f74.py::test_run_manual_con_qa_form_emite_text_y_choice_y_trae_remeasure (cuenta los nichos) | perfil: nichos raíz por canal |
| niche_discoverer.py:135 | `"tags": ["océano", "misterio", "profundidades", "abismos"]` (y 149, 163) | logica_idioma | — | perfil |
| niche_discoverer.py:136 | `"archaeology_focus": ("expediciones oceánicas fallidas, naufragios…"` (va al prompt Modo B) | prompt | — | perfil (texto por idioma) |
| niche_discoverer.py:174 | `SPY_ES_MIN_VIEWS = 50_000`; `SPY_ES_WINDOW_MONTHS` (173), `SPY_MAX_COMPETING_FOR_GAP` (175) | logica_idioma | — | perfil: umbrales por mercado |
| niche_discoverer.py:371 | `"Eres un experto en descubrimiento de contenido viral en YouTube inglés."` · queries dinámicas | prompt | — | prompt_por_idioma (pide queries EN: sirve; cambia el nombre ES del nicho) |
| niche_discoverer.py:559 | `"Eres un traductor de contenido viral inglés→español."` · `spanish_topic` | prompt | test_chat52_variant_label.py (lee `spanish_topic`) | prompt_por_idioma (en EN: extraer tema sin traducir) |
| niche_discoverer.py:750 | fan-out: `ex.submit(_measure_es, subj["search_query_en"], subj["nombre_en"])` | logica_idioma | test_t1_t3_fanout.py | codigo |
| niche_discoverer.py:817 | `remeasure={"es_query": …, "already_es": False}` (fan-out) | logica_idioma | test_t1_t3_fanout.py | codigo: receta neutral por mercado |
| niche_discoverer.py:1032 | `sat = _measure_es(item["spanish_topic"], already_es=True)` (atómico) | logica_idioma | — (test_chat52_already_es.py y test_chat52_atomic_aliases.py prueban la rama `already_es` de subtopic_measurer, no esta llamada) | codigo |
| niche_discoverer.py:1150 | prompt Modo B «Eres un investigador de misterios históricos para contenido viral.» | prompt | — | prompt_por_idioma |
| niche_discoverer.py:1175 | `- "title": máximo 8 palabras, en español, sin signos, buscable` | prompt | — | prompt_por_idioma |
| niche_discoverer.py:1370 | Modo C: «la semilla se escribe en el form del canal ES → already_es=True» | logica_idioma | test_module_f74.py (afirma `already_es is True`) | perfil: idioma de la semilla = idioma del canal |
| niche_discoverer.py:1586 | opción A del form «Spy-Arbitrage — virales EN, huecos ES»; B (1587) «sin competencia ES» | logica_idioma | — | perfil: nombre del mercado |
| script_engine/subtopic_classifier.py:22 | `SYSTEM_INSTRUCTION` «Sos un clasificador de ESTRUCTURA de un video documental…» (fan-out de fase 1; lo importa niche_discoverer) | prompt | — | prompt_por_idioma (la salida es una etiqueta) |
| script_engine/subtopic_extractor.py:32 | `SEGMENT_SYSTEM` «Sos un extractor de SUJETOS-DE-SEGMENTO…» (l.31–58) y `_VERIFY_SYSTEM` «Verificás nombres propios…» (l.106); lo importa niche_discoverer | prompt | — | prompt_por_idioma (la salida ya es inglesa: `nombre_en`, `search_query_en`) |
| script_engine/m_judge_seeds.py:63 | juez: «analista de contenido para un canal faceless de YouTube en español» · «8-10 min» (64) | prompt | test_chat50_seed_enrichment.py, test_t5_sentinel.py (arman el prompt) | prompt_por_idioma |
| script_engine/m_judge_seeds.py:88 | «3. HUECO ES. label VACÍO/HUECO = español libre (bueno).» | prompt | — | prompt_por_idioma |
| topic_validator.py:137 | `TrendReq(hl="es-ES", tz=360, …)` · Google Trends en español | api_idioma | — | perfil: `hl` por canal |
| topic_validator.py:361 | `VACIO / HUECO → ORO (demanda probada + español libre)` · veredicto spy | logica_idioma | — | codigo |
| topic_validator.py:528 | `_HUMAN_OPTIONS_PROMPT`: «guionista viral … contenido en español neutro» | prompt | — | prompt_por_idioma |
| topic_validator.py:994 | `comp = count_competing_spanish(search_query, …)` · Regla 3-50-24 en ES | logica_idioma | — | codigo |
| estante.py:6 | docstring: semilla manual `already_es=True` + «gate ES de la Etapa A» | logica_idioma | test_module_f77c.py | codigo |
| estante.py:59 | `remeasure={"es_query": titulo, "entity": titulo, "already_es": True}` | logica_idioma | test_module_f77c.py::test_medir_todos_a_la_vez_con_remeasure_y_tid_uuid | perfil: idioma de la semilla = idioma del canal |

#### A-3.2 Publicación: m09 (paquetes F58 y miniaturas), m09b, fase3

| archivo:línea | qué es | tipo | tests que lo fijan | cómo se volvería dato |
|---|---|---|---|---|
| script_engine/m09_packaging.py:83 | `PEDIDO_PAQUETES` «…documental de historia oscura en español neutro-latino…» | prompt | test_module_f58.py::test_a2_pedido_byte_identico_al_handoff (byte a byte contra el handoff) | prompt_por_idioma |
| script_engine/m09_packaging.py:95 | `descripcion: … y una línea de cierre del canal.` · firma la escribe Opus | canal | test_module_f58.py::test_a2_pedido_byte_identico_al_handoff | perfil: línea de cierre fija por canal |
| script_engine/m09_packaging.py:96 | `tags: la mayoría en español y de 3 a 5 en inglés` | prompt | test_module_f58.py::test_a2_pedido_byte_identico_al_handoff | prompt_por_idioma |
| script_engine/m09_packaging.py:132 | `ICON_CREDIT = "Íconos: game-icons.net (CC BY 3.0) · Lucide (MIT)"` · va a la descripción | canal | test_module_f58.py::test_a2_llamada_y_validacion_reintenta, test_m09_packaging.py | perfil (texto del crédito por idioma) |
| script_engine/m09_packaging.py:371 | `from script_engine.num_es import parse_int` · cifras del título contra el pool | logica_idioma | test_module_f58.py::test_a4_cifras | codigo: separador de miles por idioma |
| script_engine/m09_packaging.py:386 | `avisos_cifras` usa `voz_utils.numeros` (números en letras en español, `_NUMW` voz_utils.py:20) | logica_idioma | test_module_f58.py::test_a4_cifras (afirma «TRES MINAS», «2 MILLONES») | codigo: números en letras por idioma |
| script_engine/m09_packaging.py:877 | CHECKLIST: `- Idioma del video: **Español**` | canal | — (test_module_f58.py::test_a7_compose_paquete_cli solo mira el título) | perfil |
| script_engine/m09_packaging.py:881 | CHECKLIST: `Agregar el video a una **playlist** del canal` (sin id de playlist) | canal | — | perfil: playlist por canal |
| script_engine/m09_review_server.py:156 | `<html lang="es">` del form de miniaturas (interfaz de Omar) | texto_pantalla | — | perfil (solo si Omar lo quiere; no llega al video) |

- **m09b no existe en el código.** `git grep -n -i "m09b"` (con las exclusiones) da solo `DECISIONES.md:238` («La subida por API (m09b) queda aprobada para una tanda posterior») y `fase3.py:6` («El upload sigue MANUAL (Omar en Studio); m09b (API) es otro chat»). No hay `defaultLanguage`, `defaultAudioLanguage`, `categoryId` ni playlist que amarrar todavía. Cuando se escriba, esos campos tienen que salir del perfil.
- **Handle y playlist:** `git grep -n -i -E "youtube\.com/@|@misterios|playlistId"` no devuelve nada en el código. El canal no tiene handle ni id de playlist escritos en ningún lado; la firma la escribe Opus (fila :95) y el crédito de íconos (:132).
- **Miniatura (F58):** la fuente es Anton (`m09_packaging.py:51`, alfabeto latino) y el texto se pasa a mayúsculas con `.upper()`. Nada de eso depende del idioma. `"lang": v3img.place_language(topic)` (`m09_packaging.py:414`) es el idioma del **lugar** del caso (carteles dentro de la foto), no el del canal: va en Descartados.

#### A-3.3 Literal del canal y descripción del canal en prompts

| archivo:línea | qué es | tipo | tests que lo fijan | cómo se volvería dato |
|---|---|---|---|---|
| music_config.py:255 | `SONIDO_DEL_CANAL = ("Misterios Sepultados suena **grave, quieto y paciente**…` | canal | test_module_f28a.py::test_sonido_del_canal_literal | perfil. Nota: el código no lo lee (`git grep -n SONIDO_DEL_CANAL` da solo music_config.py:254) |
| researcher_steps/ficha_caso.py:139 | `SYSTEM_F23_1`: «Sos el documentalista de Misterios Sepultados…» (también 184, 228) | canal | — | perfil (nombre) + prompt_por_idioma |
| script_engine/guion_v4.py:97 | «Sos el guionista de Misterios Sepultados… en español neutro» (también 184, 276, 362, 449, 536, 648) | canal | test_module_f11c.py::test_sistema_rol_voz_oficio_ejemplos_en_orden (afirma el literal en `system_f11c`) | perfil (nombre) + prompt_por_idioma |
| script_engine/m01a_columna.py:40 | «Sos el guionista jefe de Misterios Sepultados…» (también 94) | canal | — | perfil + prompt_por_idioma |
| script_engine/m01a_escaleta.py:879 | «Sos el guionista jefe de Misterios Sepultados…» | canal | — | perfil + prompt_por_idioma |
| script_engine/m01f_prompts/SYSTEM.txt:1 | «crítico de retención del canal Misterios Sepultados: documentales en español… de 10 a 12 minutos» | canal | — | perfil + prompt_por_idioma |

(Total del literal: 15 apariciones en 6 archivos. Salida de `git grep -c -i "misterios sepultados"` con las exclusiones: `music_config.py:1`, `researcher_steps/ficha_caso.py:3`, `script_engine/guion_v4.py:7`, `script_engine/m01a_columna.py:2`, `script_engine/m01a_escaleta.py:1`, `script_engine/m01f_prompts/SYSTEM.txt:1`. Lo que esos prompts dicen además del nombre lo cubren A-1 y A-2; acá solo se cuenta el nombre.)

#### A-3.4 Parámetros de idioma a servicios externos (se cruzan con A-2, voz)

| archivo:línea | qué es | tipo | tests que lo fijan | cómo se volvería dato |
|---|---|---|---|---|
| audio_profiles.py:19 | `"language_code_v4": "es"` · ElevenLabs v4 | api_idioma | test_module_38e_voice_ab.py (lee AUDIO_STYLE) | perfil |
| audio_manager.py:810 | `"language_code": AUDIO_STYLE.get("language_code_v4") or "es"` · fallback fijo a "es" | api_idioma | test_module_f9.py::test_payload_v2_identico_y_v4_con_idioma (fija que el payload pasa el idioma que recibe, l.97–98; no el `or "es"` de la l.810) | perfil (el `or "es"` va afuera) |
| audio_manager.py:756 | `process_script(script, language="es", …)` · Whisper/alineado | api_idioma | — | perfil |
| fase2a.py:330 | `audio_process(normalized, language="es")` | api_idioma | — | perfil |
| fase1_5.py:876 | `audio_script, language="es", skip_if_exists=True` (process_script) | api_idioma | — | perfil |

YouTube (`relevanceLanguage`) está en A-3.1 y Google Trends (`hl="es-ES"`) en topic_validator.py:137. **Gemini, OpenAI y fal:** ninguna llamada pasa parámetro de idioma o región. El barrido `[\"'](language|lang|hl|gl|locale|region|languageCode|language_code)[\"']\s*:|\b(language|lang|hl|gl|locale|language_code)\s*=\s*[\"']` solo da las filas de arriba, los `<html lang="es">`, `fase2b.py:549` (`pyphen lang="es_ES"`: karaoke, es de A-2) y `anchor_timing.py:56` (normalizador, es de A-2). El idioma con esos servicios va por el texto de los prompts.

#### A-3.5 QA Studio (servidor y plantillas)

| archivo:línea | qué es | tipo | tests que lo fijan | cómo se volvería dato |
|---|---|---|---|---|
| qa_studio_server.py:1592 | `_NARRFIX_INSTRUCTION`: «auditor de pronunciación TTS (ElevenLabs, español neutro)» | prompt | — (test_qa_studio.py inyecta un `rewrite_fn` falso, `_narr_deps` l.981, que recibe el prompt armado en qa_studio_server.py:1712 sin mirarlo; nada lo fija) | prompt_por_idioma |
| qa_studio_server.py:1621 | `"REPORTE DEL USUARIO (mala pronunciación, español criollo)"` | prompt | — (test_qa_studio.py::test_narrfix_idempotent_dict usa el mismo `rewrite_fn` falso) | prompt_por_idioma |
| qa_studio_server.py:1639 | `state.base / "data" / "normalizer_custom_dict.json"` · diccionario de pronunciación único | rutas | test_qa_studio.py::test_narrfix_happy_boundary_dict_backup_invalidate | perfil: diccionario por canal (el que lee tts_normalizer.py:181 y m02_5_normalizer_gate.py:50) |
| qa_studio_server.py:141 | `self.base / "data" / "scripts" / f"{topic_id}.json"` · arma la ruta a mano, no usa DATA_DIR | rutas | test_qa_studio.py | codigo: usar la raíz del canal |
| qa_studio_server.py:923 | `return state.base / "data" / "scripts" / "_steps"` · ruta a mano | rutas | test_qa_studio.py | codigo |
| qa_studio_server.py:139 | `self.base / "output" / "audio" / topic_id` · ruta a mano | rutas | test_qa_studio.py | codigo |
| qa_studio_server.py:70 | `TOPIC_ID = "985a942f-…"  # default cableado` | rutas | — | perfil (o sin default) |
| qa_seed_pick.html:118 | leyenda «SATURADO · viral ES grande» | logica_idioma | — | perfil: nombre del mercado |
| qa_gallery.html:211 | «BADGE DE COMPETENCIA (por es_label)» · el form lee `es_label` | logica_idioma | — | codigo: campo `market_label` |

Interfaz de Omar, que no llega al video (no se cuenta como amarre del canal; se anota para que no se confunda): `<html lang="es">` en qa_studio.html:15, qa_form.html:10, qa_gallery.html:18, qa_choice.html:9, qa_judge.html:14, qa_multi.html:9, qa_seed_pick.html:8, qa_text.html:11 y mixer.html:8. Títulos de pestaña en español, como qa_studio.html:19 «Estudio QA — revisión por capítulo» y qa_form.html:14 «Producción asistida — QA Studio». Los textos del form en niche_discoverer.py:1335 («Tema (enter vacío = terminar)») y :1349 («Nicho raíz»). Los pedidos de edición `PEDIDO_EDITAR_CASILLEROS` (qa_studio_server.py:803) y `PEDIDO_EDITAR_MOVIMIENTO` (:818) son instrucciones de Omar en español que devuelven casilleros en inglés: sirven igual para los dos canales.

#### A-3.6 Rutas donde un segundo canal chocaría

Los directorios por tema (`data/scripts/_steps/<tid>/`, `output/<tid>/`, `output/<tid>/publish/`) usan el uuid del tema, así que no se pisan entre canales. Lo que choca son los **archivos globales** y la mezcla de temas de los dos canales en las mismas listas.

| archivo:línea | qué es | tipo | tests que lo fijan | cómo se volvería dato |
|---|---|---|---|---|
| script_engine/topics_db.py:20 | `DB_FILE = DATA_DIR / "topics_db.json"` · una sola base de temas | rutas | — (test_module_f77c.py l.50 y test_module_f39_research.py l.27 redirigen `topic_researcher.TOPICS_DB_FILE`, no esta constante) | perfil: `DATA_DIR` por canal |
| fase1.py:73 | `db_path = DATA_DIR / "topics_db.json"` (copia propia del camino; también fase1_5.py:86, script_engine/m06_assembler.py:19, csv_exporter.py:42, topic_researcher.py:71) | rutas | test_module_f39_fase1.py (fija la copia de fase1_5, `f15.TOPICS_DB`, l.37; no fase1.py:73) | perfil |
| topics_db.json:1 | hay un `topics_db.json` **versionado en la raíz del repo**, aparte del de `data/` | rutas | — | perfil (revisar si alguien lo lee) |
| cost_tracker.py:84 | `HISTORY_FILE = DATA_DIR / "cost_history.json"` · historial de costo único | rutas | test_module_f17.py::test_cost_tracker_no_escribe_el_historial_bajo_pytest | perfil (o campo `canal` en cada registro) |
| fase1.py:79 | `SEEDS_FILE = DATA_DIR / "selected_seeds.json"` (también niche_discoverer.py:121, m_judge_seeds.py:36, topic_researcher.py:69) | rutas | test_module_f42b.py, test_module_f39_research.py | perfil |
| fase1.py:117 | `arch = DATA_DIR / "seeds_archive.json"` | rutas | — | perfil |
| fase1.py:530 | `RESEARCH_SENTINEL = DATA_DIR / "_last_research.json"` (también run_pipeline.py:555) | rutas | test_run_pipeline.py, test_module_f77c.py | perfil |
| niche_discoverer.py:123 | `DROPPED_CAP_LOG = DATA_DIR / "_steps" / "dropped_by_cap.jsonl"` | rutas | — | perfil |
| niche_discoverer.py:204 | `DYNAMIC_QUERIES_CACHE = DATA_DIR / "dynamic_queries_cache.json"` | rutas | — | perfil |
| topic_validator.py:65 | `TRENDS_CACHE_FILE = DATA_DIR / "trends_cache.json"` (y la caché depende de `hl`) | rutas | — | perfil |
| estante.py:35 | `ESTANTE_DIR = DATA_DIR / "estante"` · un solo estante | rutas | test_module_f77c.py | perfil |
| estante.py:36 | `STEPS_DIR = DATA_DIR / "scripts" / "_steps"` · el estante se deduce de este disco | rutas | test_module_f77c.py::test_listar_sin_dirs_y_registro_roto | perfil |
| run_pipeline.py:50 | `from config import DATA_DIR, OUTPUT_DIR` · etapas deducidas del disco (68–147) | rutas | test_run_pipeline.py | perfil |
| run_pipeline.py:491 | `m09.archivar_paquetes_desfasados(tid)` · `publish/_desfasado_*` | rutas | test_module_f73.py | — (por tema, no choca) |
| script_engine/m09_packaging.py:153 | `return OUTPUT_DIR / tid / "publish"` | rutas | test_m09_packaging.py, test_module_f58.py, test_module_f73.py | perfil (sigue `OUTPUT_DIR`) |
| script_engine/m07_music_director.py:72 | `AUDIO_LIBRARY_DIR = BASE_DIR / "audio_library"` «Shared entre todos los videos del canal» | rutas | — | perfil (decidir si la biblioteca se comparte: los volúmenes están calibrados por pista) |
| script_engine/m02_5_normalizer_gate.py:50 | `CUSTOM_DICT_PATH = DATA_DIR / "normalizer_custom_dict.json"` (también tts_normalizer.py:181) | rutas | — (ningún test nombra `CUSTOM_DICT_PATH`; test_qa_studio.py usa la ruta propia de qa_studio_server, l.1639) | perfil: diccionario de pronunciación por idioma |
| CLAUDE.md:3 | «Leé `DECISIONES.md` antes de cualquier tanda» · un solo registro de decisiones | rutas | — | perfil / doc por canal (o sección por canal) |
| CLAUDE.md:11 | «leer `lab/ESTADO_SESION.md`» · un solo estado de sesión | rutas | — | doc por canal |

### Módulo → nº de filas (parte A-3)

| módulo | filas |
|---|---|
| fase1.py (gate ES + rutas) | 11 (7 en A-3.1, 4 en A-3.6) |
| script_engine/subtopic_measurer.py (`_measure_es`) | 4 |
| script_engine/subtopic_es_relevance.py | 3 |
| script_engine/subtopic_classifier.py | 1 |
| script_engine/subtopic_extractor.py | 1 |
| script_engine/youtube_scanner.py (API YouTube: `relevanceLanguage`) | 16 |
| script_engine/transcript_fetch.py | 1 |
| niche_discoverer.py | 16 (14 en A-3.1, 2 en A-3.6) |
| script_engine/m_judge_seeds.py | 2 |
| topic_validator.py | 5 (4 en A-3.1, 1 en A-3.6) |
| estante.py | 4 (2 en A-3.1, 2 en A-3.6) |
| run_pipeline.py | 2 (solo rutas) |
| script_engine/m09_packaging.py (m09a, paquetes F58, miniaturas) | 9 (8 en A-3.2, 1 en A-3.6) |
| script_engine/m09_review_server.py | 1 |
| m09b | 0: **no existe el módulo** (ver A-3.2) |
| fase3.py | 0: **no tiene español** (ver abajo) |
| qa_studio_server.py + plantillas qa_*.html | 9 |
| config.py | 0: **no está en git** (`.gitignore:2`); la copia local no tiene parámetros de idioma |
| literal «Misterios Sepultados» (music_config, ficha_caso, guion_v4, m01a_columna, m01a_escaleta, m01f SYSTEM.txt) | 6 filas (15 apariciones) |
| api_idioma de voz (audio_profiles, audio_manager, fase2a, fase1_5) | 5 |
| rutas globales (topics_db, cost_tracker, m07, normalizer, topics_db.json raíz) | 5 |
| docs (CLAUDE.md) | 2 |

Módulos con 0 filas:

```
$ timeout 60 git grep -n -i -E "español|spanish|\"es\"|lang|Misterios|playlist|idioma|DATA_DIR|OUTPUT_DIR" -- fase3.py; echo "exit=$?"
exit=1
```
(sin salida: fase3.py **no tiene español**. Llega a los datos del canal solo a través de `script_engine.topics_db` (fila topics_db.py:20) y de m09.)

```
$ timeout 60 git grep -n -i "m09b" -- . ':(exclude)lab' ':(exclude)_archived' ':(exclude)output' ':(exclude)data' ':(exclude)tests' ':(exclude)test_*.py' ':(exclude)**/test_*.py'
DECISIONES.md:238:- 2026-11-04 · La subida por API (m09b) queda aprobada para una tanda posterior · Omar · F74
fase3.py:6:El upload sigue MANUAL (Omar en Studio); m09b (API) es otro chat — fase3 nace con el enchufe.
```

```
$ git ls-files config.py ; git check-ignore -v config.py
.gitignore:2:config.py	config.py
```

### Descartados (vistos y no son amarre del canal)
- `script_engine/m09_packaging.py:414` `"lang": v3img.place_language(topic)`: es el idioma del lugar del caso, no el del canal.
- `script_engine/m09_packaging.py:253` `oraciones()`: corta en `. ! ? …`, sirve igual en inglés.
- `script_engine/m09_packaging.py:51` fuente Anton: alfabeto latino, sirve en inglés.
- `audio_manager.py:554`: la Forced Alignment de ElevenLabs no recibe `language` («la API de FA NO lo exige»).
- Los html `lang="es"` y los textos del form: son la interfaz de Omar (A-3.5).

### Fuera de mi parte (visto de paso; lo cubren A-1 y A-2)
- `script_engine/m01b_narrator.py:45` `"suscribite"` (lista de frases prohibidas en la narración).
- `fase2b.py:549` `pyphen.Pyphen(lang="es_ES")` (karaoke).
- `script_engine/gfx_templates/index.html.tmpl:2` y `script_engine/gfx_review.py:53` `<html lang="es">` (gfx).
- `anchor_timing.py:56` `normalize_for_tts(anchor, language="es")` (normalizador).
- `script_engine/youtube_scanner.py` no usa `hl` ni `gl` con scrapetube. El idioma del feed que devuelve scrapetube no se fija en el código: no lo verifiqué, porque hacerlo pide una corrida con red.

## B. Dónde está amarrada la duración

Base: rama `f11-guion-v4`, árbol de trabajo del 2026-11-10. Barrido con `git grep` sin `lab/`, `_archived/`, `output/`, `data/`, `test_*.py` ni `tests/`. Cada `archivo:línea` de abajo se abrió y se leyó.

**`config.py` no está en git** (`.gitignore:2`; `git ls-files --error-unmatch config.py` → «did not match»). Lo leí desde disco porque es la config viva. No copio ninguna llave. `audio_library/` tampoco está en git: los largos de pista salen de `ffprobe` sobre los mp3 del disco.

Cómo se resuelve un valor: `video_length.get(name)` (`script_engine/video_length.py:53-58`) devuelve `getattr(config.long_video, name, DEFAULTS[name])`. Por eso, en la columna «de dónde sale»:
- **config** quiere decir que `LongVideoConfig` trae el campo con el mismo valor que el default;
- **default** quiere decir que `config.long_video` no trae el campo y manda `DEFAULTS`.

### B.1 `video_length.DEFAULTS` (`script_engine/video_length.py:10-38`): **23 claves**, 23 filas

| archivo:línea | parámetro | valor de hoy | de dónde sale | qué lo consume (archivo:función) |
|---|---|---|---|---|
| script_engine/video_length.py:11 | `target_words` | 1500 | config (`config.py:205`, 1500) | `researcher_steps/pool_gate.py:91` `evaluate` → sale en el gate y en `m01a_escaleta.py:1330` (`esc["pool_gate"]`). Es informativo: nada recorta con este valor |
| script_engine/video_length.py:12 | `max_words` | 2200 | config (`config.py:206`, 2200) | `script_engine/m01b_guionista.py:227-228` `review` (duro «el video tiene N palabras: el tope es 2200»); `script_engine/guion_v4.py:1132-1134` `largo_txt` («más que el tope de 2200»). En v4 los dos son métrica (`guion_v4.metricas`, l.1427-1435: `mg.review` l.1427 → `duras_v3` l.1433; `largo_txt` l.1435) |
| script_engine/video_length.py:13 | `hook_words` | 110 | config (`config.py:207`) | `m01a_escaleta.py:70-75` `_cap_words` → `CAP_WORDS[1]`; `video_length.py:45-50` `char_band("hook")` → `m01b_narrator.py:23` `LEN_HOOK` → `m01d_particion.py:45-49` `len_range` |
| script_engine/video_length.py:14 | `dev_words` | 250 | config (`config.py:208`) | `m01a_escaleta.py:72` → `CAP_WORDS[2..6]`; `char_band("development")` → `m01b_narrator.py:24` `LEN_DEVELOPMENT` → `m01d_particion.len_range` |
| script_engine/video_length.py:15 | `outro_words` | 140 | config (`config.py:209`) | `m01a_escaleta.py:72` → `CAP_WORDS[7]`; `char_band("reveal_outro")` → `m01b_narrator.py:25` `LEN_OUTRO` → `m01d_particion.len_range` |
| script_engine/video_length.py:16 | `hook_cap_seconds` | 45 | config (`config.py:210`) | `m01a_skeleton.py:32` `CHAPTER_SCHEMA[0].duration_seconds`; `m03_visual.py:1036` `_calculate_image_count` (`veo_extras = 2 × _calculate_flux_extras_count(45)` = 10) |
| script_engine/video_length.py:17 | `dev_cap_seconds` | 105 | config (`config.py:211`) | `m01a_skeleton.py:33` `CHAPTER_SCHEMA[1..5].duration_seconds` (ver B.3: solo se copia) |
| script_engine/video_length.py:18 | `outro_cap_seconds` | 45 | config (`config.py:212`) | `m01a_skeleton.py:35` `CHAPTER_SCHEMA[6].duration_seconds` (solo se copia) |
| script_engine/video_length.py:19 | `max_images_per_video` | 90 | config (`config.py:213`) | `m03_visual.py:1037` `_calculate_image_count`: `cap_max = (90 − 10) // 5 = 16` fotos por cap de desarrollo |
| script_engine/video_length.py:22 | `min_beats` | 7 | default | `m01a_escaleta.py:65` `MIN_BEATS` → `_profile` (l.192) → `validate` l.263-265 (duro «N beats (tienen que ser 7–14)»); `generate_v2` l.1305-1306 (el rango va al usuario del prompt) |
| script_engine/video_length.py:23 | `max_beats` | 14 | default | `m01a_escaleta.py:65` `MAX_BEATS`, mismo camino; bloqueante «beats entre 7 y 14» (l.965) |
| script_engine/video_length.py:24 | `min_beats_dev_cap` | 2 | default | `m01a_escaleta.py:66` `MIN_BEATS_DEV_CAP` → `validate` l.283 (caps 2–6 con menos beats) |
| script_engine/video_length.py:26 | `gate_datos` | 150 | default | `researcher_steps/pool_gate.py:26,82` `evaluate` (umbral del amarillo) |
| script_engine/video_length.py:27 | `gate_citas_verificadas` | 8 | default | `pool_gate.py:27,82` `evaluate` |
| script_engine/video_length.py:28 | `gate_elegibles` | 2 | default | `pool_gate.py:28,82` `evaluate` |
| script_engine/video_length.py:29 | `gate_eventos_fecha` | 10 | default | `pool_gate.py:29,82` `evaluate` |
| script_engine/video_length.py:30 | `gate_yellow_pct` | 50 | default | **nadie** (`git grep -n "gate_yellow"` fuera de video_length.py solo encuentra el docstring `m01a_escaleta.py:772`) |
| script_engine/video_length.py:31 | `gate_yellow_target_words` | 1200 | default | **nadie** (mismo grep; F23: «informativo») |
| script_engine/video_length.py:32 | `gate_yellow_max_beats` | 8 | default | **nadie** (solo el docstring `m01a_escaleta.py:772`) |
| script_engine/video_length.py:33 | `gate_yellow_min_beats_dev_cap` | 1 | default | **nadie** |
| script_engine/video_length.py:35 | `gate_rojo_datos` | 40 | default | `pool_gate.py:33,83` `evaluate` (piso del rojo) |
| script_engine/video_length.py:36 | `gate_rojo_personas` | 2 | default | `pool_gate.py:34,83` `evaluate` |
| script_engine/video_length.py:37 | `gate_rojo_eventos` | 3 | default | `pool_gate.py:35,83` `evaluate` |

En el mismo módulo, sin ser claves de `DEFAULTS`:

| archivo:línea | parámetro | valor de hoy | de dónde sale | qué lo consume |
|---|---|---|---|---|
| script_engine/video_length.py:41 | `CHARS_POR_PALABRA` | 6 | literal | `char_band` (l.49) |
| script_engine/video_length.py:42 | `BANDA_CHARS` | (0.5, 1.3) | literal | `char_band` (l.50). Hook queda en (330, 858) caracteres, desarrollo en (750, 1950) y cierre en (420, 1092) |
| script_engine/video_length.py:5 | docstring «12 min ≈ 1,500 palabras a 2.05 palabras/s» | 2.05 wps | texto | nadie: es comentario (ver B.5) |

### B.2 `config.long_video` (`config.py:182-237`, `LongVideoConfig`, instancia en `config.py:323`). **19 campos** más 1 método

| archivo:línea | parámetro | valor de hoy | de dónde sale | qué lo consume |
|---|---|---|---|---|
| config.py:192 | `total_chapters` | 7 | config | **nadie** (`git grep "long_video\."` → solo `m03_visual.py:1033`, que es un comentario. El `total_chapters` de `m03_visual.py:996` es un parámetro con default literal 7) |
| config.py:193 | `veo_chapters` | (1, 7) | config | **nadie** (hay un gemelo literal: `m03_visual.py:896` `VEO_CHAPTERS`) |
| config.py:194 | `leonardo_chapters` | (2, 3, 4, 5, 6) | config | **nadie** (hay un gemelo literal: `m03_visual.py:897` `FLUX_CHAPTERS`) |
| config.py:198 | `target_duration_seconds` | 540 («~9 min») | config | **nadie** (`git grep target_duration` → solo config) |
| config.py:199 | `target_word_count` | 1350 | config | **nadie** |
| config.py:200 | `min_word_count` | 1260 | config | **nadie** |
| config.py:201 | `max_word_count` | 1500 | config | **nadie** |
| config.py:205 | `target_words` | 1500 | config | por `video_length.get` (B.1) |
| config.py:206 | `max_words` | 2200 | config | por `video_length.get` (B.1) |
| config.py:207 | `hook_words` | 110 | config | por `video_length.get` (B.1) |
| config.py:208 | `dev_words` | 250 | config | por `video_length.get` (B.1) |
| config.py:209 | `outro_words` | 140 | config | por `video_length.get` (B.1) |
| config.py:210 | `hook_cap_seconds` | 45 | config | por `video_length.get` (B.1) |
| config.py:211 | `dev_cap_seconds` | 105 | config | por `video_length.get` (B.1) |
| config.py:212 | `outro_cap_seconds` | 45 | config | por `video_length.get` (B.1) |
| config.py:213 | `max_images_per_video` | 90 | config | por `video_length.get` (B.1) |
| config.py:216 | `veo_clips_per_long_video` | 6 | config | `config.py:222-235` `estimated_cost_per_long_video` → `config.estimated_cost_for` (l.344-347) → `csv_exporter.py:121` |
| config.py:217 | `leonardo_images_per_long_video` | 50 | config | el mismo costo estimado (l.227) |
| config.py:220 | `use_chain_of_generation` | True | config | **nadie** |
| config.py:236 | literal `1500 * 6 * elevenlabs_per_char` dentro de `estimated_cost_per_long_video` | 1500 palabras × 6 | literal | costo estimado de `csv_exporter` (no sigue a `target_words`) |

En `LongVideoConfig` faltan `min_beats`, `max_beats`, `min_beats_dev_cap` y todas las `gate_*`. Para esas claves manda `DEFAULTS`.

### B.3 Estructura por cap: `CHAPTER_SCHEMA`, beats y palabras objetivo

| archivo:línea | parámetro | valor de hoy | de dónde sale | qué lo consume |
|---|---|---|---|---|
| script_engine/m01a_skeleton.py:31-35 | `CHAPTER_SCHEMA` | 7 caps. Cap 1 `hook` veo 45 s; caps 2–6 `development` flux 105 s cada uno; cap 7 `reveal_outro` veo 45 s. Suma 615 s | `video_length` (`*_cap_seconds`) | `m01a_escaleta.py:653` (copia `duration_seconds` a `esc["caps"]`); `m01d_particion.py:202` (lo copia al skeleton); `m01d_particion.py:68` (`roles` para `len_range`). **Nadie decide nada con `duration_seconds`**: `git grep "\[.duration_seconds.\]\|get(.duration_seconds"` solo encuentra `m01d_particion.py:202` |
| script_engine/m01a_escaleta.py:75 | `CAP_WORDS` | {1: 110, 2–6: 250, 7: 140} (suma 1500) | `video_length` | `_profile` l.192 → `validate` l.519-526 |
| script_engine/m01a_escaleta.py:76 | `WORDS_TOL` | 0.15 | literal | `validate` l.523: si los `palabras_objetivo` de los beats de un cap se van más de ±15 % de `CAP_WORDS[n]`, **se re-escalan** a ese objetivo (l.525) |
| script_engine/m01a_escaleta.py:146, 271, 656 | `palabras_objetivo` (por beat; por cap = suma de sus beats) | lo propone el modelo y lo repara `validate` | escaleta (LLM) + `CAP_WORDS` | `guion_v4.py:744` (`CAP n · ≈ N palabras`, solo con `largo="objetivo"`); `guion_v4.py:863` (total en la tarea, solo con `objetivo`); `guion_v4.py:1189-1200` bloqueante (c) ±`CAP_TOL` (se salta con `largo="abierto"`, l.1195); `guion_v4.py:1359` regeneración; `guion_v4.py:1432` métrica; `m01b_guionista.py:145-150` (mínimo 0.85 ×, máximo 1.15 ×, `MIN_WORDS_FACTOR` l.32); `m01b_guionista.py:183-185` por beat (±15 %, l.35); `m01c_editor.py:47` (va en el prompt del editor) |
| script_engine/guion_v4.py:57 | `LARGOS` | ("objetivo", "abierto"). Producción: `largo="abierto"` (defaults l.842, 941, 1140, 1304) | literal | En abierto, el guionista no recibe palabras por cap. El largo sale de los beats y del material |
| script_engine/guion_v4.py:58 | `CAP_TOL` | 0.25 | literal | bloqueante (c) de `guion_v4.bloqueantes` (solo con `objetivo`) |
| script_engine/m01a_escaleta.py:873 | `MAX_BEATS_POR_CAP` | 3 | literal | `bloqueantes` l.1004 → `validate` l.280-282 (bloqueante «entre 1 y 3 beats por cap», l.967) |
| script_engine/m01a_escaleta.py:883 | prompt `SYSTEM_V2`: «Siete capítulos, de 7 a 14 beats» | 7 caps, 7–14 beats | **literal en el prompt** (no sigue a `MIN_BEATS`/`MAX_BEATS`) | el modelo de la escaleta (Fable, `DEFAULT_MODELO_ESCALETA` l.869) |
| script_engine/m01a_escaleta.py:278-286, 530, 667 | `range(1, 8)` / `range(2, 7)` | 7 caps fijos | literal | `validate` (caps 1–7 en orden; desarrollo 2–6) |
| script_engine/m01a_escaleta.py:870-872 | `REGENERACIONES_V2`, `LOOPS_RANGO`, `RECUERDA_LOOP_CAP` | 1; (1, 2) loops por video; re-gancho al cierre del cap 3 | literal (DECISIONES 2026-10-29 16:05) | bloqueantes de la escaleta v2 (l.979-981) |
| script_engine/m01a_escaleta.py:169-170 | `MAX_APOYOS` / `MAX_APOYOS_FICHA` | 3 / 6 por beat | literal | `validate` / `bloqueantes` l.1002 |
| script_engine/m01d_particion.py:32, 45-49 | `LEN_TOL` + `len_range` | ±15 % sobre `char_band`. Hook (280, 986), desarrollo (637, 2242), cierre (357, 1255) caracteres | literal + `video_length` | `rebalance` l.77-109. Si un cap pasa el máximo, su último párrafo se muda al cap siguiente o **el editor lo acorta** (`editor_shorten`, Gemini Pro, l.113-125). Producción: `fase1_5.py:712-713` pasa `shorten=md.editor_shorten()` |
| script_engine/m01d_particion.py:33 | `TITLE_MAX_WORDS` | 5 | literal | títulos de cap (no depende del largo) |
| script_engine/m01b_narrator.py:130-135 | `_validate_narration` largo por rol | `char_band` | `video_length` | `m01b_guionista.review` l.141-143 **ignora** el error de tipo `length` (el largo se mide en palabras) |

### B.4 Fotos por cap: `_calculate_image_count` y lo que la rodea (`script_engine/m03_visual.py`)

| archivo:línea | parámetro | valor de hoy | de dónde sale | qué lo consume |
|---|---|---|---|---|
| script_engine/m03_visual.py:895 | `EXPECTED_CHAPTER_COUNT` | 7 | literal | `assign_visual_prompts` l.2269, 2290 (`total_chapters`) |
| script_engine/m03_visual.py:902 | `SECONDS_PER_IMAGE_TARGET` | 7.0 s | literal (comentario l.899-901: ciclo DepthFlow) | `_calculate_image_count` l.1015 (`base = round(dur / 7)`); `_calculate_flux_extras_count` l.1051 |
| script_engine/m03_visual.py:903 | `MIN_IMAGES_FLUX` | 6 | literal | `_calculate_image_count` l.1031, 1037-1038; `_reconcile_anchor_timing` (l.2281) |
| script_engine/m03_visual.py:904 | `MAX_IMAGES_FLUX` | 18 | literal | `_calculate_image_count` l.1031, 1038 |
| script_engine/m03_visual.py:993-1038 | `_calculate_image_count(cap_duration_sec, chapter_number, total_chapters=7, capped=True)` | `n = round(dur/7) + bonus`; tope `min(18, cap_max, n)` con `cap_max = max(6, (90 − 2·extras(45)) // 5) = 16` | `video_length` + literales | `assign_visual_prompts` l.2266-2270 (caps flux, con `duration_sec` real del `sync_map`); l.2290 con `capped=False` → `reencuadres_propuestos` (F8) |
| script_engine/m03_visual.py:929-931 | `BONUS_POSITION_*` | +1 primer tercio, +1 último tercio, 0 medio | literal | `_calculate_image_count` l.1018-1028 |
| script_engine/m03_visual.py:919 | `VEO_CLIP_DURATION_SEC` | 8.0 s | literal | `_calculate_flux_extras_count` l.1050; zona veo en caracteres l.2210-2211; prompt de movimiento l.1950 («CLIP LENGTH: 8 seconds»); `asset_manager.py:980-989` (la duración que se pide al motor); `video_prompt.py:28, 86-87`; `config.py:229, 255` (costo estimado) |
| script_engine/m03_visual.py:923-924 | `MIN_FLUX_EXTRAS` / `MAX_FLUX_EXTRAS` | 4 / 14 fotos de apoyo por cap veo (gancho y cierre) | literal | `_calculate_flux_extras_count` l.1041-1052 → `assign_visual_prompts` l.2202 |
| script_engine/m03_visual.py:913 | `MIN_ANCHOR_GAP_SEC` | 1.0 s | literal | fusión de anclas apretadas (no depende del largo) |
| script_engine/m03_visual.py:137 | `CAP_MAX_WORKERS` | 7 | literal | paralelismo por cap (uno por cap) |
| script_engine/m03_visual.py:940-942 | `PROMPT_MIN_CHARS` / `PROMPT_MAX_CHARS` / `KLING_PROMPT_MAX_CHARS` | 120 / 700 / 2500 | literal | prompt de cada foto (no depende del largo del cap) |
| script_engine/parallax_animator_v2.py:234-235, 255-256 | `_DURATION_REFERENCE_S` / `_INTENSITY_FLOOR_FACTOR` | 7.0 s / 0.45 | literal | `_build_options`: solo **baja** la intensidad si la foto dura menos de 7 s. Si dura más, nada la compensa |
| asset_manager.py:72 | `FOTOS_POR_LLAMADA` | 6 | literal (DECISIONES 2026-10-30 18:34) | lotes de Seedream `/edit` |
| asset_manager.py:67 / config.py:134 | `FLUX_MAX_WORKERS` ← `pipeline.fal_concurrency` | 20 | config | concurrencia contra fal |

### B.5 Relojes de velocidad (palabras/s, s/palabra, caracteres/s): **7 valores distintos**

| archivo:línea | parámetro | valor de hoy | de dónde sale | uso / quién lo consume |
|---|---|---|---|---|
| script_engine/video_length.py:5 (y `config.py:202`) | «2.05 palabras/s» | 2.05 wps | comentario (F5d, v2) | **nadie**. Es el origen de «12 min ≈ 1,500 palabras». `guion_v4.py:1127` dice que se reemplazó |
| script_engine/guion_v4.py:1127 | `PALABRAS_POR_SEG` | 2.4 wps (Vajont F26: 2,355 palabras → 980.8 s) | literal | `largo_txt` l.1133 («largo: N palabras ≈ M min», métrica); `datos_por_min` l.1446 (→ `guion_v3_reglas.py:226-232`) |
| script_engine/tts_tags.py:26 | `SLOWLY_WPS` | 2.4 wps | literal | **nadie en producción**: solo aparece en el docstring l.12. `tag_cap(slowly_dev=…)` (l.62) llega en `False` desde `m01d_particion.py:237` y `m01c_editor.py:125-129`. `slowly_dev=True` solo existe en `test_module_f9.py:43`. El `voz_v4.wps` que cita el docstring no existe (`git grep voz_v4` → solo esa línea) |
| script_engine/voz_utils.py:402-439 | `seg_por_palabra()` | **medido**: mediana s/palabra de todas las voces ya generadas del narrador (`output/audio/*/ch*.meta.json` + `_timestamps.json`) | dato (output/) | `m01e_pantalla.velocidad` l.92-97 → `m05_narrative.retencion` (l.504) → `m01f_critico` (`metricas["seg_por_palabra"]`, l.120, 284, 338: `entre_promesas`) y `m01e_pantalla.caben_en` l.222 |
| script_engine/m01e_pantalla.py:86 | `SEG_POR_PALABRA_RESPALDO` | 0.35 s/palabra (≈ 2.86 wps; Vajont ch04 F36) | literal | respaldo de `velocidad()` cuando no hay voces (l.97); `m01e_pantalla.py:1434` |
| gfx_profiles/misterio.json (token `callout_sec_per_word`) | `callout_sec_per_word` | 0.4 s/palabra (2.5 wps) | perfil gfx | **huérfano**: está en `HUERFANAS_TOKENS` (`gfx_config.py:365-367`) |
| script_engine/pantalla_colocar.py:19 (gemelo `gfx_guion.py:31`) | `LECTURA_CPS` | 15 caracteres/s | literal (estándar de subtitulado) | `pantalla_colocar.py:35, 126`; `pantalla_filtros.py:15, 293`; `m01e_pantalla.py:221-222`; `gfx_guion.py:221, 482` |
| script_engine/m03_visual.py:2210-2211 | `chars_per_sec` | medido por cap (`len(narración) / duration_sec`) | dato | zona veo en caracteres (`veo_zone_chars = 8 s × cps`) |

Valores distintos: 2.05, 2.4 (dos constantes), la mediana medida, 0.35 s/p (≈ 2.86), 0.4 s/p (2.5) y 15 cps. Ojo: las dos de 2.4 tienen el mismo número por motivos distintos. Una está viva (largo y datos/min) y la otra muerta (`[slowly]`).

### B.6 Gancho y cierre: clips de video

| archivo:línea | parámetro | valor de hoy | de dónde sale | qué lo consume |
|---|---|---|---|---|
| script_engine/m03_visual.py:919 | `VEO_CLIP_DURATION_SEC` | 8.0 s, 1 clip por cap veo (1 y 7) | literal | ver B.4. El resto del audio del cap se cubre con apoyos flux (`fase2b.py:1060-1061`: `flux_segment_dur = audio − clip`) |
| asset_manager.py:69 | `CLIP_POLL_TIMEOUT` | 600 s | literal (F53b) | espera de un clip en la cola de fal (`asset_manager.py:2151`, `veo_config.poll_timeout_seconds`). El clip es de 8 s fijos: no crece con el video |
| asset_manager.py:70, 71, 68 | `CLIP_MAX_ATTEMPTS_NON_REJECTION` / `FAL_SUBMIT_TIMEOUT_S` / `FLUX_POLL_TIMEOUT` | 3 / 60 s / 180 s | literal | llamadas a fal (por clip o por foto) |
| engine_profiles.py:170-171, 186-187 | `duracion_min/max` de los perfiles G y K | G 3–10 s; K 3–30 s | literal | rango de duración del schema del motor (no se usa para pedir más de 8 s) |
| fase2b.py:1160, 1198-1202, 1299 | loop del clip | `-stream_loop -1` si el audio > clip | literal | `_build_chapter_segment` (ruta veo sin híbrido) |
| fase2b.py:110 | `HOOK_DURATION` | 1.8 s (pre-pad y overlay del gancho en ch01) | literal | `_build_chapter_segment` l.1175 (`pre_pad` si `apply_hook`); `_costura_medida` l.2851 y `_solo_plan` l.3072 (`pre_pad` si `plan.is_first and hook`). Fijo: no crece con el video |

### B.7 Música

| archivo:línea | parámetro | valor de hoy | de dónde sale | qué lo consume |
|---|---|---|---|---|
| audio_library/*.mp3 (fuera de git) | largo de las 12 pistas F28 | 156.98–174.04 s (ffprobe). Cada `.json` trae `recorte.duracion_s` y `loop_crossfade_s: 3.0` | dato | `fase2b._build_music_piece_for_chapter` |
| fase2b.py:1596-1612 | loop con acrossfade | si el cap dura más que la pista: `n = ceil((cap − xf)/(pista − xf))` copias encadenadas con `acrossfade=d=3` | pista (`loop_crossfade_s`) | `_build_music_piece_for_chapter`. Sin `loop_crossfade_s`: `-stream_loop -1` (l.1613-1631) |
| fase2b.py:139 | `MUSIC_CROSSFADE_SEC` | 2.0 s entre caps | literal | `_build_continuous_music_track` l.1650, 1718, 1767; `_mezcla_preview` l.2944-2949 |
| script_engine/music_intensity.py:27-33 | `GANANCIA_DB`, `FADE_SILENCIO_S`, `SILENCIO_PREVIO_S`, `VUELTA_GOLPE_S`, `RAMPA_SUBE_S`, `MAX_SILENCIOS`, `SUBE_DESDE` | {fondo 0, sube +3, golpe +5 dB}; 1.5 s; 1.5 s; 4 s; 1 s; **2 silencios por cap**; intensidad ≥ 4 | literal (HANDOFF_F28 §B.2) | `tramos_de_cap` l.66-122 → `aplicar_a_wav` (fase2b l.1640) |
| fase2b.py:1633, 1745, 1783 | timeouts de la música | 120 s por pieza de cap; 60 s (un solo cap); 300 s para la cadena de acrossfade del video entero | literal | `_build_music_piece_for_chapter`, `_build_continuous_music_track` |
| music_config.py:44 | `MUSIC_LENGTH_MS` | 180 000 ms (comentario: «la paleta del canal son pistas de ~150–175 s (recortadas de 180 s); solo informa») | literal (F28 §B.1) | `m07_music_director._call_elevenlabs_music_api` l.563 (`music_length_ms` del pedido por prompt); respaldo de duración en `_generate_new_track_with_gate` l.954. Es el largo de una pista nueva |
| music_config.py:53 | `MUSIC_REQUEST_TIMEOUT_SEC` | 180 s | literal | `_call_elevenlabs_music_api` l.568; `generar_con_plan` l.1255 (`max(180, 400)` = 400 s) |
| script_engine/m07_music_director.py:1179, 1239 | `PLAN_SECCIONES` / duración por sección | 3–5 secciones; cada una 3000–120 000 ms | literal (F28 §A) | `fijar_plan` l.1221-1223 (cantidad de secciones) y l.1239-1242 (duraciones; error si no entran). Tope: 5 × 120 s = 600 s por pista compuesta |

### B.8 Topes de tiempo, tamaño y cantidad que un video del doble puede tocar

| archivo:línea | parámetro | valor de hoy | de dónde sale | qué lo consume / alcance |
|---|---|---|---|---|
| gfx_config.py:47 | `GfxRenderSettings.timeout_sec` | 1500 s **por cap** | literal. El comentario dice que caps de ~3 min ya tardaban 956–983 s | `gfx_layer.py:115-122` `_render` → `TimeoutExpired` → `GfxError` → vuelve a `base_clip` (sin gfx) |
| gfx_config.py:49-50 | `player_ready_timeout_ms` / `protocol_timeout_ms` | 240 000 / 600 000 | literal | flags del render de HyperFrames (`gfx_layer.py:117-118`) |
| script_engine/gfx_layer.py:101, 245 | `_reencode` / `extend_base` | 900 s | literal | re-encode del base_clip del cap |
| script_engine/gfx_safe_bake.py:74, 150 · gfx_sparse.py:228, 426, 430 | timeouts | 1800 / 1800 · 900 / 1800 / 1800 s | literal | modo `--gfx-sparse` (por cap) |
| fase2b.py:955 | `_build_flux_visual` | 180 s | literal | concat `-c copy` del cap |
| fase2b.py:1034 | `_concat_visual_clips` | 300 s | literal | **re-encode** libx264 del visual del cap (concat con scale/pad) |
| fase2b.py:1335 | `_build_chapter_segment` | 600 s | literal | **re-encode** del segmento del cap a 2560×1440 con subs (NVENC p5 cq 23, `fase2b.py:2557`, o libx264) |
| fase2b.py:2012, 2077, 2086, 2954 | mezcla de música del video entero | 900 s | literal | `_mix_music_into_video` (video `-c:v copy`), `_mix_music_audio_only`, `_mezcla_preview` (solo audio). Pasa por el video completo, pero sin re-encode de imagen |
| fase2b.py:2920, 2927, 2937 | mezcla preview por segmento / concat | 300 s | literal | `_mezcla_preview` |
| fase2b.py:2552-2553 | `CLIP_WORKERS` / `GFX_PARALELO` | 6 / 1 | literal (F28 §C.3 / §C.2; comentario: con 3 en paralelo, 4 de 7 caps cayeron a `base_clip`) | `_build_flux_visual` l.923 (clips por cap); `_assemble_one_video` l.3332 (con 1 el gfx va en fila: `_segmentos_en_paralelo` no corre). El tiempo de render gfx crece en línea con el largo del video |
| script_engine/depth_probe.py:33 | `MAX_ZOOMS_PER_CHAPTER` | 7 fotos promovidas a zoom por cap | literal (HANDOFF_140b) | `rank_promotions` l.110-111 → `fase2b._apply_zoom_gate` l.2353. Tope **por cap**, no por minuto |
| script_engine/transition_applier.py:335, 409, 426, 433 | split / concat del video entero | 600 / 900 / 900 / 900 s | literal | `_split_copy`, `concat_windowed` (copy y audio PCM del video entero) |
| fase2b.py:127 · fase2b.py:124 | `subs_doc.max_dur` · `max_chars_renglon` | 7.0 s · 42 | literal (Netflix) | subtítulos (por evento; no dependen del largo) |
| audio_manager.py:411 | timeout del TTS | 120 s por cap («audios largos pueden tardar») | literal | `_generate_chapter_audio`: **un request por cap con el texto entero del cap**. En el repo no hay un tope de caracteres por request de ElevenLabs (`git grep -i "max_chars\|5000\|chunk"` no encuentra nada de TTS) |
| audio_manager.py:567 | timeout de forced alignment | 180 s | literal | `_forced_align_elevenlabs` (audio del cap + texto entero) |
| claude_helpers.py:33-34 | `TIMEOUT_S` / `MAX_TOKENS` | 600 s por lectura del stream / 100 000 (razonamiento + salida) | literal | guion, escaleta, ficha y crítico con Claude |
| gpt_helpers.py:25-26 | `TIMEOUT_S` / `MAX_COMPLETION_TOKENS` | 600 s / 32 000 | literal | `guion_v4.py:936-937` (guionista GPT si se elige), `researcher_steps/ficha_caso.py:861` |
| script_engine/dicho_verificador.py:20 | `MAX_TOKENS` | 2 000 | literal | salida chica por llamada (no crece con el largo) |
| researcher_steps/research_v3.py:47 | `MAX_DESCARGAS_OK` | 10 documentos por idioma | literal (F20) | R2 del research: el material no crece con el largo pedido |
| researcher_steps/research_v3.py:49, 1344-1345, 1663 | `MAX_DOC_CHARS` / `CHUNK_CHARS` / `CHUNK_OVERLAP` / `RESERVA_OUT_R3` | 300 000 / 60 000 / 3 000 / 16 000 | literal | R3 (por documento; no depende del largo del video) |
| gfx_profiles/misterio.json:94-105 | `max_per_cap` por bloque gfx | title 1, data_callout 5, archive 2, zoom 1, count_up 1, punch_in 4, keyword 5, icon 3, icon_array 1 | perfil | `gfx_config.py:446-479` (inventario). Son topes **por cap**, no por minuto |
| gfx_profiles/misterio.json:15 (default `gfx_config.py:189`) | `interrupt_max_sec` | 18 s (default 35) | perfil | `script_engine/gfx_review.py:39` (aviso de hueco sin bloque) |
| gfx_profiles/misterio.json:14 | `interrupt_min_sec` | 12 s | perfil | **huérfano**: está en `HUERFANAS_TOKENS` (`gfx_config.py:367`); `git grep interrupt_min_sec` fuera de lab/tests → solo `gfx_config.py:367` y `misterio.json:14` |
| gfx_profiles/misterio.json:51-52 | `flash_max_per_cap` / `flash_min_gap_sec` | 2 / 20 s | perfil | flashes por cap |
| gfx_config.py:261-262 | `dip_max_per_cap` / `punch_max_identity` | 1 / 4 | literal | por cap |
| script_engine/tts_tags.py:22-24 | `GOLPE_MAX_WORDS` / `GOLPE_MAX_PER_CAP` / `GOLPE_MIN_INTENSITY` | 6 / 2 por cap / 4 | literal | `tag_cap` ([quietly]/[whispers]) |
| script_engine/m05_narrative.py:40-41 | `VENTANA_GANCHO_S` / `ORACIONES_TRAS_PICO` | 30 s / 3 | literal (analista / DECISIONES 2026-10-31 18:43) | `retencion` (métrica) |
| script_engine/m05_narrative.py:31-32 | `DENSITY_MIN` / `MAX_DATO_CAPS` | 2.0 datos literales del pool cada 100 palabras / un dato en ≤ 2 caps | literal | `cap_review` (la llama `m01b_guionista.review` l.153 → `duras_v3`/`blandas_v3`, métricas en v4): l.750-752 duro «estos datos ya salieron en 2 caps», l.811-812 blanda de densidad; `video_metrics` l.279, 317 y `judge_narration` l.497 (umbrales del reporte del juez). La densidad va **por 100 palabras**: un guion del doble pide el doble de datos literales, y el pool no crece con el largo (`MAX_DESCARGAS_OK`, arriba). `MAX_DATO_CAPS` es un tope en caps, no por minuto. Ningún test los nombra (`git grep` en `test_*.py` y `tests/`: nada) |
| researcher_steps/pool_gate.py:106, 108 | texto del reporte | «Tubería normal: 12 min (≈ 1,500 palabras)» / «12 min, escaleta de 7–14 beats» | **literal en texto** | `pool_gate.report` → POOL_GATE.md |
| researcher_steps/step_4d_summary.py:5, 61, 86, 110 | «~1,800 palabras de guion», resumen de 1500–3000 caracteres | literal en el prompt | literal | `step_4d_summary` (research viejo) |
| script_engine/youtube_scanner.py:483 | `EN_MAX_DURATION_SEC` | 50 × 60 s | literal | filtro de videos de la competencia (no toca nuestro video) |

### B.9 Qué se rompe o se queda corto si el guion dobla su largo sin tocar nada

1. **El texto se recorta solo.** El texto de más se corta sin que nadie lo decida ni lo apruebe. Hoy un cap de desarrollo pasa el máximo con 2242 caracteres (`m01d_particion.py:32, 45-49` sobre `video_length.py:14, 41-42, 45-50`); a 500 palabras × 6 son unos 3000. Para cada cap que se pasa, `rebalance` (`m01d_particion.py:77-109`) muda el último párrafo al cap siguiente; si no puede, el editor Gemini lo **acorta** a `max(200, largo − exceso − 40)` caracteres. En producción esto corre siempre (`fase1_5.py:712-713`).
2. **La escaleta no deja planear caps más largos.** Si el modelo pide más palabras por cap, `validate` las vuelve a escalar a 110 / 250 / 140 ±15 % (`m01a_escaleta.py:75-76, 519-526`). Ese objetivo achicado entra después al prompt del editor (`m01c_editor.py:47`) y a los mínimos y máximos de `m01b_guionista.py:145-150, 183-185`.
3. **Los beats no crecen.** Hay 7–14 beats en total (`video_length.py:22-23`; también literal en el prompt, `m01a_escaleta.py:883`), entre 1 y 3 por cap (`m01a_escaleta.py:873`) y 7 caps fijos (`m01a_escaleta.py:278-286`). Para doblar el largo, cada beat tiene que durar el doble.
4. **Las fotos se quedan cortas.** El tope es de 16 fotos por cap de desarrollo (`m03_visual.py:1036-1038`, con `video_length.py:16, 19`) y de 14 apoyos por cap veo (`m03_visual.py:924`). Un cap de ~210 s pediría 30 fotos y recibe 16, o sea unos 13 s por foto contra el objetivo de 7 s (`m03_visual.py:902`). `parallax_animator_v2.py:255` no compensa las fotos que duran más de 7 s.
5. **El render gfx puede vencer y salir sin gráficos.** El tope es de 1500 s por cap (`gfx_config.py:47`), y su propio comentario dice que caps de ~3 min ya tardaban 956–983 s. Si un cap lo pasa, el cap sale **sin gfx** (`gfx_layer.py:115-122`).
6. **Los re-encodes por cap pueden vencer.** Son `_build_chapter_segment`, con 600 s (`fase2b.py:1335`), y `_concat_visual_clips`, con 300 s (`fase2b.py:1034`); los dos re-encodan a 1440p un cap que ahora dura el doble. Es un riesgo, no está medido.
7. **El tope de 2200 palabras se marca como falla.** Unas 3000 palabras pasan `max_words` (`video_length.py:12`). Sale como duro en `m01b_guionista.py:227-228` y como «más que el tope» en `guion_v4.py:1134`. En v4 son métricas y no frenan, pero el reporte lo marca.
8. **La densidad por minuto cae a la mitad.** Todos los topes son por cap, no por minuto: bloques gfx (`gfx_profiles/misterio.json:94-105`), golpes de voz (`tts_tags.py:23`), silencios de música (`music_intensity.py:32`), flashes (`misterio.json:51`) y zooms (`depth_probe.py:33`, 7 por cap). Suben los avisos de hueco de más de 18 s (`misterio.json:15` → `script_engine/gfx_review.py:39`).
9. **La música se repite.** Las pistas duran 157–174 s, así que un cap más largo que su pista entra en loop con acrossfade de 3 s (`fase2b.py:1596-1612`). No rompe, pero la repetición se oye.
10. **El TTS va en un solo request por cap.** El timeout es de 120 s (`audio_manager.py:411`) y el repo no tiene tope de caracteres por request (unos 3000 caracteres por cap de desarrollo). Sin verificar contra el límite del endpoint.
11. **El material del research no crece.** Siguen siendo 10 descargas por idioma (`research_v3.py:47`) y los mismos umbrales del pool (`video_length.py:26-29, 35-37`): el doble de guion sale del mismo material.
12. **Textos que mienten sobre el largo.** «12 min ≈ 1,500 palabras» sigue escrito en `pool_gate.py:106, 108`, en `video_length.py:5` y en el costo estimado (`config.py:236`, `1500 * 6`). Los `duration_seconds` de `CHAPTER_SCHEMA` (`m01a_skeleton.py:31-35`) siguen diciendo 615 s, aunque nadie los usa para decidir nada.

## C. Dónde vive la estructura del guion

Base: rama `f11-guion-v4`, árbol de trabajo (HEAD `c0cce6a`). Solo lectura: no se editó nada del repo, no se corrió pytest ni el pipeline, 0 llamadas a API. Cada `archivo:línea` de abajo se abrió y se leyó.
Fuera del barrido: `lab/`, `_archived/`, `output/`, `data/`, `test_*.py`, `tests/` (los tests aparecen solo en «qué test la fija»). Los scripts sueltos de la raíz (`_lab_*`, `diag_*`, `_probe_*`, `_run_*`, `_regen_*`) no son producción: se nombran aparte cuando aparecen.

### C1. El número 7

#### C1.a `EXPECTED_CHAPTER_COUNT`: la salida literal del grep

El comando del pedido, pegado tal cual, **no corre**:

```
$ timeout 60 git grep -n "EXPECTED_CHAPTER_COUNT" -- . ':!lab' ':!_archived' ':!output' ':!data' ':!test_*.py' ':!tests'
fatal: Unimplemented pathspec magic '_' in ':!_archived'
(exit 128)
```

`git` lee `:!_` como «magia de pathspec» y no conoce `_`. El mismo filtro con la forma larga (`:(exclude)`) sí corre:

```
$ timeout 60 git grep -n "EXPECTED_CHAPTER_COUNT" -- . ':(exclude)lab' ':(exclude)_archived' ':(exclude)output' ':(exclude)data' ':(exclude)test_*.py' ':(exclude)tests'
script_engine/_archived/m02_profiles.py:59:EXPECTED_CHAPTER_COUNT = 7
script_engine/_archived/m02_profiles.py:172:    for n in range(1, EXPECTED_CHAPTER_COUNT + 1):
script_engine/_archived/m02_profiles.py:343:    if len(chapters) != EXPECTED_CHAPTER_COUNT:
script_engine/_archived/m02_profiles.py:345:            f"se esperaban {EXPECTED_CHAPTER_COUNT} caps, llegaron {len(chapters)}"
script_engine/_archived/m02_profiles.py:446:    if len(skel_chapters) != EXPECTED_CHAPTER_COUNT:
script_engine/_archived/m02_profiles.py:448:            f"skeleton tiene {len(skel_chapters)} caps (esperado {EXPECTED_CHAPTER_COUNT})"
script_engine/_archived/m02_profiles.py:450:    if len(narr_chapters) != EXPECTED_CHAPTER_COUNT:
script_engine/_archived/m02_profiles.py:452:            f"narration tiene {len(narr_chapters)} caps (esperado {EXPECTED_CHAPTER_COUNT})"
script_engine/_archived/m02_profiles.py:459:    if len(chapters_raw) != EXPECTED_CHAPTER_COUNT:
script_engine/_archived/m02_profiles.py:461:            f"Flash devolvió {len(chapters_raw)} caps (esperado {EXPECTED_CHAPTER_COUNT})"
script_engine/m01a_escaleta.py:9:sigue siendo 7 caps (`EXPECTED_CHAPTER_COUNT`): cada beat va a un cap.
script_engine/m03_visual.py:860:        return [items_by_cap.get(n) or [] for n in range(1, EXPECTED_CHAPTER_COUNT + 1)]
script_engine/m03_visual.py:895:EXPECTED_CHAPTER_COUNT = 7
script_engine/m03_visual.py:2089:                                           for n in range(1, EXPECTED_CHAPTER_COUNT + 1)}}}
script_engine/m03_visual.py:2153:    if len(skel_chapters) != EXPECTED_CHAPTER_COUNT:
script_engine/m03_visual.py:2155:            f"skeleton tiene {len(skel_chapters)} caps (esperado {EXPECTED_CHAPTER_COUNT})"
script_engine/m03_visual.py:2157:    if len(narr_chapters) != EXPECTED_CHAPTER_COUNT:
script_engine/m03_visual.py:2159:            f"narration tiene {len(narr_chapters)} caps (esperado {EXPECTED_CHAPTER_COUNT})"
script_engine/m03_visual.py:2269:                total_chapters=EXPECTED_CHAPTER_COUNT,
script_engine/m03_visual.py:2290:                pedidas = _calculate_image_count(cap_duration_sec, cap_n, EXPECTED_CHAPTER_COUNT, capped=False)
script_engine/m03_visual.py:2308:    _cap_ns = list(range(1, EXPECTED_CHAPTER_COUNT + 1))
script_engine/m09_packaging.py:405:    from script_engine.m03_visual import EXPECTED_CHAPTER_COUNT
script_engine/m09_packaging.py:417:                                                for n in range(1, EXPECTED_CHAPTER_COUNT + 1)}}}
```

Son **23 líneas**. `:(exclude)_archived` solo saca la carpeta de la raíz; `script_engine/_archived/` queda adentro (10 líneas). Igual van en la tabla, porque el contrato pide una fila por línea. Un 7 cambiado en producción no las toca: nadie importa ese módulo.

```
$ timeout 60 git grep -n -E "_archived\.m02|_archived import|from script_engine\._archived|m02_profiles" -- '*.py' ':(exclude)lab' ':(exclude)output' ':(exclude)data'
script_engine/__init__.py:6:  m02_profiles   → asignador de art_profile (pendiente)
script_engine/_archived/m02_profiles.py:2:script_engine/m02_profiles.py — Módulo 02: asignador de profiles.
test_module_02.py:18:from script_engine.m02_profiles import (
```
(`test_module_02.py` importa `script_engine.m02_profiles`, que ya no existe: es un test viejo y roto. No importa `_archived`.)

| # | archivo:línea | qué asume | qué pasaría con otro número |
|---|---|---|---|
| 1 | `script_engine/_archived/m02_profiles.py:59` | constante `= 7` del módulo 02 archivado | nada: nadie lo importa (grep de arriba) |
| 2 | `script_engine/_archived/m02_profiles.py:172` | recorre los caps 1..7 | nada (archivado) |
| 3 | `script_engine/_archived/m02_profiles.py:343` | rechaza si llegan ≠ 7 caps | nada (archivado) |
| 4 | `script_engine/_archived/m02_profiles.py:345` | mensaje del rechazo de la fila 3 | nada (archivado) |
| 5 | `script_engine/_archived/m02_profiles.py:446` | skeleton con 7 caps | nada (archivado) |
| 6 | `script_engine/_archived/m02_profiles.py:448` | mensaje de la fila 5 | nada (archivado) |
| 7 | `script_engine/_archived/m02_profiles.py:450` | narration con 7 caps | nada (archivado) |
| 8 | `script_engine/_archived/m02_profiles.py:452` | mensaje de la fila 7 | nada (archivado) |
| 9 | `script_engine/_archived/m02_profiles.py:459` | Flash devuelve 7 caps | nada (archivado) |
| 10 | `script_engine/_archived/m02_profiles.py:461` | mensaje de la fila 9 | nada (archivado) |
| 11 | `script_engine/m01a_escaleta.py:9` | docstring: «la salida sigue siendo 7 caps» | solo texto. El 7 real de la escaleta vive en `range(1, 8)` (C1.b) y en el prompt (C1.c) |
| 12 | `script_engine/m03_visual.py:860` | `_f8_fix_video` arma la lista de imágenes por cap para los caps 1..7 (auditoría de motivos y cuerpos) | si el guion trae más caps, los de más quedan fuera de la auditoría; si trae menos, quedan listas vacías (sin error) |
| 13 | `script_engine/m03_visual.py:895` | `EXPECTED_CHAPTER_COUNT = 7` (al lado, `VEO_CHAPTERS = (1, 7)` y `FLUX_CHAPTERS = (2..6)` en 896-897) | es la fuente que leen las filas 12-23. Cambiarla sola no alcanza: `VEO_CHAPTERS` y `FLUX_CHAPTERS` siguen fijos |
| 14 | `script_engine/m03_visual.py:2089` | `_con_f8`: `anio_prev` por cap, para los caps 1..7 | los caps de más quedan sin `anio_prev` |
| 15 | `script_engine/m03_visual.py:2153` | **rechaza** el skeleton si no trae 7 caps | con otro número, m03 se cae con `ValueError` antes de pedir una sola imagen |
| 16 | `script_engine/m03_visual.py:2155` | mensaje de la fila 15 | — |
| 17 | `script_engine/m03_visual.py:2157` | **rechaza** la narración si no trae 7 caps | lo mismo que la fila 15 |
| 18 | `script_engine/m03_visual.py:2159` | mensaje de la fila 17 | — |
| 19 | `script_engine/m03_visual.py:2269` | `_calculate_image_count(total_chapters=7)`: bonus por posición para los caps de desarrollo (2..total−1); en 1037, tope por cap = `max_images_per_video` ÷ (total − 2) | cambia el reparto de fotos por cap: más caps, menos fotos por cap con el mismo tope |
| 20 | `script_engine/m03_visual.py:2290` | lo mismo, sin tope (re-encuadres propuestos) | lo mismo que la fila 19 |
| 21 | `script_engine/m03_visual.py:2308` | corre en paralelo exactamente los caps 1..7 | junto con 15/17: hoy no se llega acá con otro número |
| 22 | `script_engine/m09_packaging.py:405` | importa la constante de m03 | sigue a la fila 13 |
| 23 | `script_engine/m09_packaging.py:417` | `topic_produccion`: `anio_prev` para los caps 1..7 (copia de la fila 14) | igual que la fila 14 |

#### C1.b `CHAPTER_SCHEMA`, roles, `render_engine`, `DEFAULT_INTENT_BY_CAP`

| archivo:línea | qué asume | qué pasaría con otro número |
|---|---|---|
| `script_engine/m01a_skeleton.py:31-36` | `CHAPTER_SCHEMA`: cap 1 `hook`/`veo`/`hook_cap_seconds`; caps 2..6 (`range(2, 7)`, l.34) `development`/`flux`/`dev_cap_seconds`; cap 7 `reveal_outro`/`veo`/`outro_cap_seconds` | es la tabla de verdad del 7. La duración sale de config; la cantidad está escrita en el código. Con otro número hay que cambiar el `range` y los dos extremos |
| `script_engine/m01a_skeleton.py:43-51` | `DEFAULT_INTENT_BY_CAP`: dict fijo 1..7 (hook, setup, rising_tension, shock, consequences, resolution, outro) | un cap 8 da `KeyError` en las lecturas con `[n]` (m01a_escaleta 610/612, m01d 203); tts_tags 152 usa `.get` y da `None` solo si el cap no tiene beats (con beats pasa por `intent_de_cap` → `KeyError`) |
| `script_engine/m01a_skeleton.py:59` | `SCREEN_MUST = (6, 7)`: los caps que tienen que llevar reservado de pantalla | con otro número, el «penúltimo y último» deja de ser 6 y 7 |
| `script_engine/m01a_escaleta.py:619` | `caps_view` recorre `CHAPTER_SCHEMA` → `esc["caps"]` (653-654 copia `role`, `render_engine`, `duration_seconds`, `narrative_intent`) | la escaleta tiene tantos caps como el schema |
| `script_engine/m01a_escaleta.py:604-607` | `intent_de_cap`: cap 1 siempre `hook`, **cap 7** siempre `outro` | un cap 8 sale del `funcion → intent`; ninguno sería `outro` |
| `script_engine/m01a_escaleta.py:610, 612` | `DEFAULT_INTENT_BY_CAP[n]` como respaldo | `KeyError` fuera de 1..7 |
| `script_engine/m01d_particion.py:67` | `roles = {n: role}` desde `CHAPTER_SCHEMA` → `len_range(roles[n])` (l.77, 104) | `KeyError` en `rebalance` si un párrafo cae en un cap fuera del schema |
| `script_engine/m01d_particion.py:195-203` | `build_contract` arma el skeleton con un cap por fila de `CHAPTER_SCHEMA`: role, render_engine, duration_seconds, narrative_intent (respaldo `DEFAULT_INTENT_BY_CAP[n]`) | el contrato de salida (01a_skeleton / 01b_narration) tiene exactamente las filas del schema |
| `script_engine/m01b_narrator.py:116` | `_len_range(role)`: banda de caracteres por `hook` / `reveal_outro` / el resto | por rol, no por número: sirve con N caps mientras existan los 3 roles |
| `script_engine/m01b_narrator.py:139` | `role == "hook"`: primera oración ≤ 12 palabras (`_validate_narration`, lo llama m01b_guionista.review 141 → métrica) | por rol |
| `script_engine/m01b_guionista.py:135` | rol del cap desde `esc["caps"]`, `development` por defecto | por rol |
| `script_engine/video_length.py:48` | `char_band(role)`: hook_words / outro_words / dev_words | por rol |
| `script_engine/m03_visual.py:572, 583` | `role` del cap; `narrative_intent == "hook"` (clip de apertura) | por rol |
| `script_engine/m03_visual.py:2177, 2199-2200, 2298-2301` | `render_engine` del skeleton: `veo` → híbrido; `veo_position = "end"` si `reveal_outro`, si no `"start"`; otro valor → `ValueError` | por cap. El veo de los extremos lo decide `CHAPTER_SCHEMA` |
| `script_engine/m03_visual.py:869, 896-897` | `VEO_CHAPTERS = (1, 7)`: no rehace la imagen 0 de los caps 1 y 7; `FLUX_CHAPTERS = (2..6)` | número fijo: con otro N, el último cap deja de ser 7 |
| `script_engine/m06_assembler.py:132` | `render_engine = "veo" if cap_num in (1, 7) else "flux"` (`assemble_final_script`, lo importa `fase1_5.py:76`) | número fijo, no lee el schema |
| `script_engine/m06_classifier.py:171, 366` | `render_engine == "veo"` | por cap |
| `script_engine/m05_judge.py:1335-1372, 1469` | perfil del juez por `render_engine` (`veo` / `flux`; otro → `ValueError`) | por cap |
| `fase2a.py:125, 132, 189, 195` | normaliza `render_engine` (por defecto `leonardo` / `veo`) y pide `video_prompts` solo en caps veo | por cap |
| `fase2b.py:1401, 1455` | lookup del script con `render_engine` | por cap |
| `asset_manager.py:1321, 2089-2111` | elige el motor por `render_engine`; `leonardo` → `flux`; desconocido → skip | por cap |
| `qa_studio_server.py:182, 287-290` | QA Studio: «cap VEO» = clip en disco o `render_engine == "veo"` | por cap |
| `art_profiles.py:302` | comentario: «aplica solo a caps 1 y 7 (veo)» | texto |
| `script_engine/tts_tags.py:139-152` | intent del cap: `intent_de_cap` → `esc.caps` → `DEFAULT_INTENT_BY_CAP.get(n)` | un cap 8 **con beats** da `KeyError`: l.151 llama a `intent_de_cap`, que evalúa `DEFAULT_INTENT_BY_CAP[n]` (`m01a_escaleta.py:612`); **sin beats**, l.152 `.get` da `None`. Hoy no se llega: los caps vienen de `m01b_guionista.caps_text`, que recorre `range(1, 8)` (`m01b_guionista.py:81`; `m01d_particion.py:237`) |

#### C1.c `range(1, 8)` y equivalentes (`range(2, 7)`, `range(2, 8)`, `== 7`, `(1, 7)`, `ch07`, `len(...) != 7`)

| archivo:línea | qué asume | qué pasaría con otro número |
|---|---|---|
| `script_engine/m01a_escaleta.py:72` | `_cap_words`: hook_words para el 1, dev_words para `range(2, 7)`, outro_words para el 7 | palabras objetivo solo para los caps 1..7 |
| `script_engine/m01a_escaleta.py:278-279` | **bloqueante** «caps 1–7 en orden con al menos un beat» (`set(caps) != set(range(1, 8))`) | toda escaleta con otro número de caps se rechaza |
| `script_engine/m01a_escaleta.py:280-282, 286` | beats por cap contados sobre `range(1, 8)` (bloqueante «entre 1 y 3») | caps de más no se cuentan |
| `script_engine/m01a_escaleta.py:283` | caps de desarrollo = `range(2, 7)` (≥ `min_beats_dev_cap`) | — |
| `script_engine/m01a_escaleta.py:438` | **bloqueante** loop 1 «se paga en el cap 7 o en el pico» (`cap_of[p] != 7`) | el «último cap» está escrito como 7 |
| `script_engine/m01a_escaleta.py:491` | `a_pantalla`: cap válido `1 <= c <= 7` | ids mandados a un cap 8 se descartan |
| `script_engine/m01a_escaleta.py:530, 540` | preguntas de pantalla por cap 1..7; `n in (1, 7)` sin el chequeo «nombra algo ya visto» | — |
| `script_engine/m01a_escaleta.py:549-553` | la pregunta del cap 7 es obligatoria (`startswith("pregunta de pantalla del cap 7")` → siempre dura) | el último cap deja de ser 7 |
| `script_engine/m01a_escaleta.py:667` | `_cap_spans` por cap 1..7 | — |
| `script_engine/m01a_escaleta.py:701` | reservado posterior a todo → `min(7, …)` | — |
| `script_engine/m01a_escaleta.py:883` (prompt `SYSTEM_V2`) | «Siete capítulos, de 7 a 14 beats.» | el modelo arma 7 |
| `script_engine/m01a_escaleta.py:952` (prompt `TAREA_V2`) | «repartí los beats en los siete caps.» | ídem |
| `script_engine/m01a_escaleta.py:966` | nombre del bloqueante «caps 1–7 en orden…» | texto |
| `script_engine/guion_v4.py:741, 789` | la escaleta del prompt (f11c y v5) se escribe para los caps 1..7 | caps de más no llegan al guionista |
| `script_engine/guion_v4.py:115, 203, 295, 381, 468, 555` (prompts guionista v5…v5.6) | «El video tiene siete capítulos.» (producción: 203, `SYSTEM_V5_6`) | el modelo escribe 7 |
| `script_engine/guion_v4.py:121, 209, …` | «Cierre (cap 7)» | ídem |
| `script_engine/guion_v4.py:174, 266, 354, 440, 527, 614` (`<errores>` de los prompts guionista v5…v5.6; producción: 266, `SYSTEM_V5_6`) | «Adelantar la cita del final: contar en el cap 6 con tus palabras lo que la cita del cap 7 va a decir.» (el 6 es el penúltimo y el 7 el último) | con otro número el modelo recibe números de cap equivocados |
| `script_engine/m01b_guionista.py:81` | `caps_text` arma los caps 1..7 | caps de más se pierden en el contrato |
| `script_engine/m01d_particion.py:53, 75, 103` | `_caps_of` y `rebalance` sobre 1..7 | `KeyError` en `out[int(p["cap"])]` si un párrafo trae cap 8 |
| `script_engine/m01d_particion.py:150-154, 187` | títulos: 7 líneas al LLM; respaldo para 1..7 | — |
| `script_engine/m01d_particion.py:170` | `len(ts) != 7` → títulos de respaldo | con otro número siempre caen al respaldo |
| `script_engine/m01d_particion.py:2, 17, 149, 182` | docstrings «contrato de 7 caps», «7 títulos» | texto |
| `script_engine/m09_packaging.py:134, 203` | `CAPS_PAQUETES = range(2, 8)`: la narración del pedido de paquetes son los caps 2..7 | un cap 8 no entra al pedido de título/miniatura |
| `script_engine/m01a_columna.py:30, 40, 94, 310` | `CAPS = 7`; prompt de la columna «cada uno de los siete capítulos» | camino `columna` (opcional): mismo 7 |
| `script_engine/m01a_columna.py:80-81, 132-133` (`<errores>` de la columna) | «Un cap 1 que explica lo que va a pasar…»; «Un cap 5 con un solo hecho. El pico es el cap más denso.» (el pico cae en el cap 5) | camino `columna` (opcional): con otro número el pico deja de ser el 5 |
| `script_engine/m01e_pantalla.py:102` (prompt `PANTALLA_SYSTEM`) | «la narración completa de un video (7 capítulos…)» | texto del prompt del rotulista |
| `script_engine/m01f_prompts/SYSTEM.txt:20` | «`caps` lleva un objeto por capítulo, en orden ch01..ch07» | texto del prompt del crítico (md5 fijado en `tests/test_m01f_compuerta.py`) |
| `script_engine/clima.py:153`, `script_engine/gfx_layer.py:554`, `script_engine/m03_visual.py:135, 2305`, `script_engine/flow_director.py:239`, `script_engine/m05_judge.py:1172`, `script_engine/pantalla_entrada.py:26`, `fase2b.py:2554`, `script_engine/__init__.py:4`, `script_engine/m01a_skeleton.py:5, 8, 28` | comentarios o docstrings («los 7 caps», «ch01 → ch07») | texto, sin efecto |
| `qa_studio.html:12` | comentario «cap 7 (veo_position=end) llega como modelo timeline desde el server» | texto |
| `transition_config.py:74`, `transition_profiles.py:14` | «ch07→ch08» (transición cuerpo→revelación) | perfil de transiciones viejo (8 caps); no coincide con el contrato actual |
| `promote_palette_to_library_chat36.py:180` | `len(library) == 7` (los 7 intents de música) | 7 intents, no 7 caps |
| `_regen_alignments_chat38.py:31` (script suelto) | `CAPS = ch01..ch07` | no es producción |

`DEFAULT_INTENT_BY_CAP` también lo usa `_lab_chat66b_m01a_schema.py:44` (script de lab en la raíz).

**Para C1:** el 7 está amarrado en cuatro lugares. (a) `CHAPTER_SCHEMA` + `DEFAULT_INTENT_BY_CAP` (m01a_skeleton). (b) Los `range(1, 8)` / `== 7` de la escaleta, la partición y m01b, más dos **bloqueantes** (`m01a_escaleta.py:278`, `:438`). (c) Los dos rechazos de m03 (`m03_visual.py:2153`, `:2157`) más `VEO_CHAPTERS` y `m06_assembler.py:132`. (d) Los prompts (escaleta 883/952, guionista 203/209/266, rotulista 102, crítico SYSTEM.txt:20). DECISIONES 2026-11-10 21:44 punto (1): «los 7 caps no se tocan». Este inventario no propone cambiarlos.

### C2. Las piezas del molde M1–M7

Lectura común. Las piezas M1–M6 son texto del prompt `SYSTEM_V2` (`m01a_escaleta.py:878-944`, versión `f55-1`), y M7 es texto de `SYSTEM_V5_6` (`guion_v4.py:183-272`, versión `f54-2`). El código **no lee** el texto de ninguna de ellas. Lo que va río abajo es lo que el modelo devuelve por haberlas leído: campos de la escaleta (`flash_forward`, `funcion`, `intensidad`, `cierre`, `imagen_sensorial`) o la forma de la narración. Por eso cada fila tiene dos columnas «quién lee»: quién lee **la regla** (casi siempre nadie) y quién lee **el campo que la regla moldea**.

Candados byte a byte de los dos prompts (los mismos para todas las piezas de cada prompt):
- `SYSTEM_V2`: `test_module_f55.py:338` (`me.SYSTEM_V2 == _sistema(lab/hyperframes/f55/PROMPT_ESCALETA_f55_1.md)` y `PROMPT_VERSION_V2 == "f55-1"`); `test_module_f55.py:341-347` (contra `f54_1.md`, mismo número de líneas y una sola línea distinta: la promesa del ejemplo). Más débiles: `test_module_f22.py:86` (empieza con `<rol>`, sin «## SISTEMA»), `test_module_f22.py:113` (sin palabras de Orleans/Ycuá), `test_module_f55.py:355` (un solo `<rol>`). Por identidad, no por contenido: `test_module_f16.py:158`, `test_module_f17.py:234, 256`, `test_module_f39_escaleta.py:102`.
- `SYSTEM_V5_6`: `test_module_f54.py:65` (`g4.system() == SYSTEM_V5_6 == lab/hyperframes/f54/PROMPT_GUIONISTA_v5_6.md`, `PROMPT_VERSION == "f54-2"`); `test_module_f54.py:66-68` (el bloque `<ejemplos>` de `EJEMPLOS_v5_6_propuesta.md` está adentro, con «Tres de ellas no van a ver la primavera.»); `test_module_f54.py:71` (cambiando el bloque `<ejemplos>` por el del v5.5 da el v5.5 exacto). Las versiones viejas del guionista (`SYSTEM_V5`…`SYSTEM_V5_4`, que traen la misma `<estructura>`) tienen candados propios: `V5_2` en `test_module_f22.py:81, 83-85` y `V5_1` en `:108`. Las de producción no se tocan si se quita M7.
- Candado md5 de prompt: **no hay** un md5 de `SYSTEM_V2` ni de `SYSTEM_V5_6` en `tests/` ni en `test_*.py`. El único es el hook `.claude/hooks/md5_prompt.py`, que **avisa** (no bloquea) el md5 nuevo y el viejo cuando se edita un archivo con `SYSTEM_V2` o `## SISTEMA`. Sí hay candados md5 de prompts vecinos que no son parte del molde: `TAREA_V2` (`test_module_f22.py:101`, `5808b41e…`), `TAREA_COLUMNA` (`:102`), el SYSTEM del crítico m01f (`tests/test_m01f_compuerta.py`).
- Hay un test que lee la frase de M1, pero en el `.md` del lab, no en el código: `test_module_f54.py:59` (`"Sin contexto, sin año, sin cifras: lo que se ve." in nuevo`, con `nuevo` = `PROMPT_ESCALETA_f54_1.md`). Si se borra la frase del código, ese test sigue pasando; el que falla es `test_module_f55.py:338/341-347`.

| id | Pieza y dónde está el texto | qué test la fija byte a byte | quién lee la regla | quién lee río abajo lo que produce (campo → módulo:línea) |
|---|---|---|---|---|
| **M1** | Regla 2 de `<oficio>`: `m01a_escaleta.py:890`, la frase «Tomá la escena más fuerte… marcado como flash-forward. Sin contexto, sin año, sin cifras: lo que se ve.» (la misma línea sigue con la promesa y los loops, que **no** son M1). El flash-forward también aparece en el `<ejemplo>` (911: «beat 1 · cap 1 · gancho · flash-forward») y en `<errores>` (938) | `test_module_f55.py:338` y `:341-347` (SYSTEM_V2 = .md f55_1). La frase sola: `test_module_f54.py:59`, pero contra el .md de lab | nadie lee el texto (abajo, grep 5). El código que acompaña la regla: `SCHEMA` 146 (`flash_forward: BOOLEAN`, no obligatorio, l.149-151) | **`beats[0].flash_forward`** → `m01a_escaleta.py:329-331` (solo el beat 1 puede serlo), `:332-342` (la curva se mide desde el beat 2; el FF no puede superar al pico); de esos, solo «pico es un beat / no es el último» son bloqueantes, el resto va a métricas (`bloqueantes` 1006; `curva_problemas` 1089) · `:581` (cronología: el FF no cuenta para «vuelve atrás», aviso) · `:668` (`_cap_spans`: el FF no cuenta para el rango de fechas del cap → `_screen_by_date` 678-701 manda los reservados de pantalla por fecha) · `:1088` (métrica `flash_forward_beat1`) · `:1423` (`to_markdown`) · **`m01e_pantalla.py:252`** (lo copia a la entrada del rotulista), `:303` (lo saca de lo que ve el modelo), **`:342`** (`momentos_detalle`: el año del relato no cuenta las oraciones de beats FF → regla `fecha_relato` de la validación, 713-721) · `m01f_critico.py:103` (`entrada`, l.94) recibe `mp._para_modelo(...)` sin `flash_forward` (`tests/test_m01f_compuerta.py:128`). El guionista **no** lo recibe: `guion_v4.escaleta_section_v5` 789-812 no imprime `flash_forward`. **«Sin año, sin cifras» en `beats[0].imagen_sensorial`** → `m01a_escaleta.py:416-417` (duro, no bloqueante → métricas), `:1094` (métrica `imagen_gancho_con_cifras`) |
| **M2** | Regla 3 entera: `m01a_escaleta.py:891` («Del gancho se vuelve atrás. El cap 2 es la vida antes… el único cap tranquilo…») | `test_module_f55.py:338`, `:341-347` | nadie lee el texto (abajo, grep 6: solo la línea 891 y su eco en `m01a_columna.py` l.52/105, que es otro prompt) | Moldea **los beats del cap 2: `funcion` «planteo», `intensidad` 1**. `funcion` → `m01a_escaleta.intent_de_cap` 601-612 + `INTENT_DE_FUNCION` 595 (`planteo → setup`) → `esc.caps[].narrative_intent` (654) → `m01d_particion.py:203` (skeleton) → `fase1_5.py:122-130` (guion de audio) → `audio_manager.py:800-803` (voice settings por intent, `audio_profiles.VOICE_SETTINGS_BY_INTENT[_V4]`) y sync_map → `m07_music_director.py:1075` (filtro duro de tracks por intent, 193-196) y `fase2b.py:2461` (el mixer) · `m03_visual.py:578` (`_visual_arc_block`, `VISUAL_INTENT_BY_INTENT` 537) · `tts_tags.py:151` → `:55` (**en un cap `setup` no hay golpes `[quietly]/[whispers]`**). `intensidad` 1 → `music_intensity.py:90-95` (sin «sube»), `tts_tags.py:145, 64` (sin golpe), `m03_imagenes_v3.py:175` (prompt de fotos «intensity 1»), `guion_v4.py:799` (lo ve el guionista). La curva: `m01a_escaleta.py:333` (sin FF en el beat 1, la baja del cap 2 es «intensidad baja antes del pico», que va a métricas) |
| **M3** | Regla 5, segunda mitad: `m01a_escaleta.py:893` («Antes del pico, un cap que aprieta; después del pico, un respiro: lo que queda cuando pasa lo peor, el recuento, el silencio.»). Eco en el ejemplo: 929 («beat 6 · cap 6 · respiro · intensidad 2») | `test_module_f55.py:338`, `:341-347`. El chequeo de código (no el texto): `test_module_f6b.py:74` (sin un beat de intensidad 1 después del pico → mensaje «respiro») | nadie lee el texto (abajo, grep 7). El código par: `m01a_escaleta.py:343-344` («falta un beat de intensidad 1 (respiro) después del pico»); **no** está en `BLOQUEANTES_V2` (964-982) → va a métricas (`curva_problemas` 1089) | Moldea **un beat después del pico con `funcion` «respiro» e `intensidad` 1**. `funcion` «respiro» → `INTENT_DE_FUNCION` 596 (`respiro → consequences`) → la misma cadena de `narrative_intent` que M2 (audio_manager, m07, m03 visual arc, tts_tags). `intensidad` 1 → `music_intensity.py:93-95` (no sube), `tts_tags.py:64`. `funcion` → `gfx_realizador.py:77, 141-146` (candidatos; solo `giro` tiene trato propio), `gfx_guion.py:239, 420` (guion de pantalla), `pantalla_filtros.py:273, 290`, `pantalla_entrada.py:121, 152` (título del tramo = funciones), `m01e_pantalla.py:247, 1162`, `m01d_particion.py:158` (títulos), `m01d_particion.py:345` (regeneración de cap), `m01c_editor.py:46` (solo con `--editor`). Ninguno pide que exista «respiro»: lo leen si está |
| **M4** | Regla 9, final: `m01a_escaleta.py:897` («…Nunca una moraleja, nunca «hoy».») | `test_module_f55.py:338`, `:341-347` | **nadie** (abajo, grep 1) | Moldea **`beats[-1].cierre`** (la última frase del video). Lectores del campo, que no dependen de que falte «hoy»: `m01a_escaleta.py:507-517` (el cierre nombra al humano o a un testigo), `:571-577` (sin eco textual de una cita), `guion_v4.py:812` (lo ve el guionista), `m01d_particion.py:160` (títulos: «termina (no lo cuentes)»), `gfx_realizador.py:81`, `m01e_pantalla.py:249`. Ningún detector busca «hoy» en el cierre ni en la narración (grep 1). `guion_v3_reglas.closing_soft` 521-538 mira cita/pregunta, no «hoy» |
| **M5** | `<ejemplo>` del faro: `m01a_escaleta.py:903-934` (humano Elvira Soto; `promesa_gancho` l.909; beat 1 sin nombre en la imagen l.911-915; cap 2 `planteo · intensidad 1` l.916; pico beat 5 l.923; `beat 6 · cap 6 · respiro · intensidad 2 …` l.929) | `test_module_f55.py:338`; `:341-347` (la única línea distinta contra f54_1 es la `promesa_gancho` del ejemplo, l.909) | **nadie** (abajo, grep 2: los nombres del ejemplo solo están dentro de prompts) | Es un ejemplo de forma: moldea todos los campos a la vez (forma del humano, del antagonista, de la promesa, del pico, de cada beat). Río abajo, lo mismo que M1/M2/M3: `funcion`, `intensidad`, `flash_forward`, `cierre`. El mismo caso inventado vive en otros tres prompts que **no** son M5 y quedarían con el faro: `guion_v4.py` (ejemplos del guionista, M7 y versiones viejas), `m01a_columna.py:63-75` (columna), `researcher_steps/ficha_caso.py:155-206` (ficha) |
| **M6** | `<errores>`, segundo punto: `m01a_escaleta.py:938` («…la curva empieza alta, baja en el cap 2 y vuelve a subir. Eso es un flash-forward, no un error.») | `test_module_f55.py:338`, `:341-347` | **nadie** lee el texto (abajo, grep 3) | Moldea **la curva de `intensidad`** (beat 1 alto con `flash_forward`, cap 2 bajo). La lee: `m01a_escaleta.py:332-342` (la curva se mide desde el beat 2 con FF; a métricas), `tts_tags.py:145` (golpes), `music_intensity.py:57-63, 90-109` (sube, golpe, silencio antes del pico del cap), `voz_datos.py:30-34` (pico del cap para rotulista y realizador), `m01e_pantalla.py:245` (pico por cap), `gfx_realizador.py:77`, `m03_imagenes_v3.py:32, 175` |
| **M7** | Guionista `<estructura>`, `SYSTEM_V5_6` (producción): punto 1 en `guion_v4.py:205` («Primera frase: lo que se ve, sin año, sin cifra, sin institución… El cap 1 termina volviendo atrás: «horas antes», «días antes».»); punto 5 en `guion_v4.py:209` («…Nunca un resumen, nunca una moraleja, nunca «hoy».»); ejemplo del gancho de la vela en `guion_v4.py:229-230` (y su eco: cierre que «vuelve a la imagen del gancho» 254-255; error «gancho abstracto» 270). Usado solo por `write` (`guion_v4.py:940-946`, `system(version)`); la reparación (`reparar` 1343-1402 → `m01d.regenerate_cap_v3` 318-372) no manda `system_instruction` y no lo ve | `test_module_f54.py:65` (byte a byte contra PROMPT_GUIONISTA_v5_6.md); `:66-68` (el bloque `<ejemplos>`, la vela incluida); `:71` | nadie lee el texto (abajo, grep 8). Hay chequeos par, todos **métricas**: `m01b_guionista.py:166-167` («gancho: la primera frase no lleva año, cifra ni institución»), `:168-169` (institución, blanda), `:170-171` (la promesa sin cifras) → `guion_v4.metricas` 1433 (`duras_v3`) → `fase1_5.py:710` (`out["metricas"]`, no frena); `guion_v3_reglas.hook_problems` 51-61 (fechas en el gancho salvo el ancla) y `hook_anchor_problems` 504-513 (ancla lugar + año) → `review_v3` 181-182 → mismas métricas. «Termina volviendo atrás»: **nadie** (abajo, grep 4). «Nunca hoy»: **nadie** (grep 1) | Moldea **el texto del cap 1** (primera frase, ancla, vuelta atrás) y **la última frase del video**. Lo leen: `m09_packaging.py:195-197` (`gancho()` = cap 1 entero, va al pedido de paquetes), `guion_v3_reglas.closing_soft` 521-538 y `guion_v4.closing_kind` (métrica «cita/pregunta/resumen»), `guion_v4.cierre_no_dicho` 1026-1042 (bloqueante (f): el dato central del beat `cierre` está dicho en el cap 7, no su forma), `m05_narrative.retencion` 378/472 (`_promesa`: cifras de la promesa en el gancho, métrica), y m01e/m01f/QA Studio leen la narración entera. Ninguno exige «sin año», «volver atrás» ni «sin hoy» para seguir |

Greps que muestran los «nadie» (comando y salida, árbol de trabajo):

1. Nadie busca «hoy» con una regex en el código. Los otros «hoy» del repo son comentarios («como hoy») o variables; el único texto que lo prohíbe está en los prompts.
```
$ timeout 60 git grep -n -E "re\.(compile|search|findall|match|sub)\(.*hoy|r[\"'][^\"']*hoy" -- '*.py' ':(exclude)lab' ':(exclude)output' ':(exclude)data' ':(exclude)tests' | grep -Ev '(^|/)_archived/|(^|/)test_'
(sin salida; exit=1)
```
(`m01b_narrator.py:34-35` trae «hoy les voy a contar» / «hoy te voy a contar» como frases de tráiler prohibidas: es otra regla, no el «nunca hoy» del cierre.)

2. Los nombres del ejemplo del faro solo están dentro de prompts (ningún módulo los lee como dato):
```
$ timeout 60 git grep -n -E "Elvira|Alborada|Bascu|Puerto Cardal|Faros y Balizas|Teo Mar" -- '*.py' ':(exclude)lab' ':(exclude)output' ':(exclude)data' ':(exclude)tests' | grep -Ev '(^|/)_archived/|(^|/)test_' | cut -d: -f1 | sort | uniq -c
      5 researcher_steps/ficha_caso.py
     33 script_engine/guion_v4.py
      9 script_engine/m01a_columna.py
      6 script_engine/m01a_escaleta.py
```
(Todas las líneas, abiertas: son texto de prompts (`SYSTEM_V2` 903-934, `SYSTEM_V5…V5_6`, `m01a_columna` SYSTEM, `ficha_caso` ejemplos) o comentarios de versión (`ficha_caso.py:44`, `m01a_columna.py:11`).)

3. Nadie lee el texto de `<errores>`: «la curva empieza alta» solo está en el prompt.
```
$ timeout 60 git grep -n "la curva empieza alta" -- . ':(exclude)lab' ':(exclude)output' ':(exclude)data' ':(exclude)tests'
script_engine/m01a_escaleta.py:938:- Poner el gancho tranquilo para que la curva «suba». El gancho es el peor momento; la curva empieza alta, baja en el cap 2 y vuelve a subir. Eso es un flash-forward, no un error.
```

4. Nadie chequea «termina volviendo atrás» («horas antes», «días antes»): solo aparece en prompts.
```
$ timeout 60 git grep -n -E "horas antes|días antes|dias antes|vuelve atr|volviendo atr" -- '*.py' ':(exclude)lab' ':(exclude)output' ':(exclude)data' ':(exclude)tests' | grep -Ev '(^|/)_archived/|(^|/)test_'
script_engine/guion_v4.py:117:1. Gancho (cap 1): … El cap 1 termina volviendo atrás: «horas antes», «días antes».
script_engine/guion_v4.py:142:«El agua sucia de un inodoro entra … Pero días antes de la sed, llegó la tormenta. Y con ella, una decisión.»
script_engine/guion_v4.py:205:1. Gancho (cap 1): … El cap 1 termina volviendo atrás: «horas antes», «días antes».
script_engine/guion_v4.py:297:1. Gancho (cap 1): … El cap 1 termina volviendo atrás: «horas antes», «días antes».
script_engine/guion_v4.py:383:1. Gancho (cap 1): … El cap 1 termina volviendo atrás: «horas antes», «días antes».
script_engine/guion_v4.py:470:1. Gancho (cap 1): … El cap 1 termina volviendo atrás: «horas antes», «días antes».
script_engine/guion_v4.py:557:1. Gancho (cap 1): … El cap 1 termina volviendo atrás: «horas antes», «días antes».
script_engine/guion_v4.py:582:«El agua sucia de un inodoro entra … Pero días antes de la sed, llegó la tormenta. Y con ella, una decisión.»
script_engine/m01a_columna.py:51:4. Cap 1: el peor momento, ya en curso. … Sin año, sin cifras, sin juicio. Termina volviendo atrás.
script_engine/m01a_columna.py:104:3. Cap 1: el peor momento, ya en curso. … Sin año, sin cifras, sin juicio. Termina volviendo atrás.
script_engine/m01a_escaleta.py:585:            warn.append(f"beat {b['n']}: vuelve atrás en el tiempo ({d} < {prev})")
script_engine/m01a_escaleta.py:891:3. Del gancho se vuelve atrás. El cap 2 es la vida antes: …
```
(Recorté con «…» el medio de las líneas de prompt. `m01a_escaleta.py:585` es el aviso de cronología, el contrario: avisa cuando un beat vuelve atrás. No pide volver.)

5. Nadie lee el texto de M1: la frase solo está en el prompt.
```
$ timeout 60 git grep -n -E "Sin contexto, sin año|marcado como flash-forward" -- '*.py' ':(exclude)lab' ':(exclude)output' ':(exclude)data' ':(exclude)tests' | grep -Ev '(^|/)_archived/|(^|/)test_'
script_engine/m01a_escaleta.py:890:2. El gancho es el peor momento, ya en curso. Tomá la escena más fuerte de la ficha y ponela en el beat 1, marcado como flash-forward. Sin contexto, sin año, sin cifras: lo que se ve. La promesa dice … Cada beat dice qué pregunta anterior paga (o ninguna).
```

6. Nadie lee el texto de M2: la línea 891 y su eco en el SYSTEM de la columna (otro prompt).
```
$ timeout 60 git grep -n -E "vida antes|cap tranquilo" -- '*.py' ':(exclude)lab' ':(exclude)output' ':(exclude)data' ':(exclude)tests' | grep -Ev '(^|/)_archived/|(^|/)test_'
script_engine/m01a_columna.py:52:5. Cap 2: la vida antes. Quién era esta gente y qué hacía ahí. Es el único cap tranquilo; termina con la primera señal del peligro.
script_engine/m01a_columna.py:105:4. Cap 2: la vida antes. Quién era esta gente y qué hacía ahí. Es el único cap tranquilo; termina con la primera señal del peligro.
script_engine/m01a_escaleta.py:891:3. Del gancho se vuelve atrás. El cap 2 es la vida antes: quién era esta gente, qué hacía ahí. Es el único cap tranquilo y por eso es el más importante para que duela lo que viene.
```

7. Nadie lee el texto de M3: la frase solo está en el prompt.
```
$ timeout 60 git grep -n -E "un cap que aprieta|lo que queda cuando pasa lo peor" -- '*.py' ':(exclude)lab' ':(exclude)output' ':(exclude)data' ':(exclude)tests' | grep -Ev '(^|/)_archived/|(^|/)test_'
script_engine/m01a_escaleta.py:893:5. El pico es uno solo, y es el que la ficha marcó salvo que tengas una razón mejor (decila). Antes del pico, un cap que aprieta; después del pico, un respiro: lo que queda cuando pasa lo peor, el recuento, el silencio.
```
(Los tres re-corridos en el árbol de trabajo, exit 0. En el grep 5 recorté con «…» el medio de la línea 890.)

8. Nadie lee el texto de M7 (puntos 1 y 5 de `<estructura>`): las dos frases solo están en las `<estructura>` de `SYSTEM_V5…V5_6`.
```
$ timeout 60 git grep -n -E "sin año, sin cifra, sin institución|Nunca un resumen, nunca una moraleja" -- '*.py' ':(exclude)lab' ':(exclude)output' ':(exclude)data' ':(exclude)tests' | grep -Ev '(^|/)_archived/|(^|/)test_' | cut -d: -f1,2
script_engine/guion_v4.py:117
script_engine/guion_v4.py:121
script_engine/guion_v4.py:205
script_engine/guion_v4.py:209
script_engine/guion_v4.py:297
script_engine/guion_v4.py:301
script_engine/guion_v4.py:383
script_engine/guion_v4.py:387
script_engine/guion_v4.py:470
script_engine/guion_v4.py:474
script_engine/guion_v4.py:557
script_engine/guion_v4.py:561
```
(Re-corrido en el árbol de trabajo, exit 0. Las 12 caen dentro de las seis `<estructura>` de la nota de abajo — `SYSTEM_V5` 114-124, `V5_4` 294-304, `V5_3` 380-390, `V5_2` 467-477, `V5_1` 554-564, `V5_6` 202-212: solo prompts.)

Nota para la tanda que quite M1–M7: la `<estructura>` del guionista vive en **seis** constantes (`SYSTEM_V5` 114-124, `V5_1` 554-564, `V5_2` 467-477, `V5_3` 380-390, `V5_4` 294-304, `V5_6` 202-212). Solo `V5_6` es producción (`system()` 632). De las otras, `V5_2` está fijada contra su .md y por md5 (`test_module_f22.py:81, 83-85`) y `V5_1` por md5 (`:108`); todas se llaman con `version=`. La regla 2 (l.890) mezcla M1 con la promesa y los loops: quitar M1 es cortar parte de una línea, no la línea entera. Y `m01a_columna.py:51/104` repite M1+M7 en el prompt de la columna (camino opcional, `TAREA_COLUMNA`): no está en la lista aprobada.

#### Piezas atadas al molde que NO están aprobadas para quitar: quién las lee

| pieza | dónde | quién la lee |
|---|---|---|
| `BLOQUEANTES_V2` | `m01a_escaleta.py:964-982` (16 entradas, nombre + regex; «loops: 1–2… el principal en el cap 7 o en el pico» 979, «recuerda_loop al cierre del cap 3» 981) | solo `m01a_escaleta.bloqueante_de` 985-987 → `bloqueantes` 998-1006 → `generate_escaleta_v2` 1293-1344 (rechaza y regenera una vez; si vuelve a fallar, PARADA). Fuera del módulo, nadie (grep `BLOQUEANTES_V2\|bloqueante_de\|LOOPS_RANGO` sin m01a_escaleta: 0 líneas de producción). Tests: `test_module_f16.py:103, 111, 200`, `test_module_f19.py:92`, `test_module_f22.py:249`, `test_module_f24.py:183`, `test_module_f54.py:189, 211, 218` |
| `RECUERDA_LOOP_CAP = 3` | `m01a_escaleta.py:872` | solo `validate` 456-459 (el `recuerda_loop.beat` tiene que ser el último beat del cap 3; bloqueante vía 981). El **campo** `recuerda_loop` lo leen `guion_v4.py:808-810` (se lo dice al guionista), `m01d_particion.py:69-73` (protege ese párrafo en `rebalance`), `m01e_pantalla.py:287` (`escaleta_video` → rotulista y crítico m01f), `m01a_escaleta.py:1108` (métrica). Test: `test_module_f54.py:189, 211` |
| `MIN_HUMAN_CAPS = 3` | `m01a_escaleta.py:78` | solo `validate` 368, 386, 392 («el humano en escena en ≥ 3 caps»: duro, no está en `BLOQUEANTES_V2` → métricas `humano_en_escena_problemas` 1093). Hay **otra** constante con el mismo nombre en `m01b_guionista.py:36`, leída en `:199-200` (humano por nombre en ≥ 3 caps de la narración → `duras_v3`, métrica) |
| campo `flash_forward` | `SCHEMA` `m01a_escaleta.py:146` | `m01a_escaleta.py:329-342, 581, 668, 1088, 1423`; `m01e_pantalla.py:252` (lo copia), `:303` (se lo saca al modelo), `:342` (año del relato); el crítico m01f lo recibe sin el campo (`tests/test_m01f_compuerta.py:128`). El guionista no lo ve. Tests: `test_module_f6b.py:174-179`, `test_module_f64.py:69, 110-119, 220-238, 299`, `test_module_f65b.py:47` |
| `funcion` de cada beat | `SCHEMA` 145 (enum `FUNCIONES` 80) | escaleta: `validate` 287-288 (beat 1 = «gancho», bloqueante), `intent_de_cap` 612 → `narrative_intent` (audio_manager 800, m07 1075, fase2b 2461, m03_visual 578, tts_tags 151); guion: `guion_v4.py:750, 792, 799` (prompt), `:1033` (bloqueante (f) sobre el beat `cierre`), `:1187`; `m01d_particion.py:158` (títulos), `:345` (regeneración); `m01c_editor.py:46` (`--editor`); `music_intensity.py:91` (**golpe +5 dB solo en el beat `funcion == "pico"`**); `m03_imagenes_v3.py:32, 175`; gfx: `gfx_realizador.py:77, 141-146, 155` (`giro` ordena los ids distinto), `gfx_layer.py:271` (log), `gfx_guion.py:239, 420, 547` (**chequeo 9: «el gancho nunca vacío de todo», por `funcion == "gancho"`**), `voz_datos.py:41`, `pantalla_entrada.py:121, 152`, `pantalla_filtros.py:273, 290`; `m01e_pantalla.py:247, 485, 522, 727` (**`gancho = funcion == "gancho"`: en el gancho, el candado mira la voz de todo el video**), `:1162`; QA Studio: `qa_studio_server.py:2220` (pestaña de pantalla: «beat N · función · ⚡ pico») → `qa_studio.html:1070` |
| `intensidad` de cada beat | `SCHEMA` 145 | `validate` 323, 327-344 (curva; a métricas); `intent_de_cap` 611 (desempate); `tts_tags.py:145` → `:64` (golpe si ≥ 4); `music_intensity.py:60, 90-95` (sube si ≥ 4; el pico del cap = el más intenso si `escaleta.pico` no cae ahí) → `fase2b.py:1525-1538, 2941, 3481` (envolvente de la música); `voz_datos.py:30-34` (pico del cap para rotulista y realizador); `m01e_pantalla.py:245` (`pico` por cap); `gfx_realizador.py:77` (se copia; no se vuelve a leer: grep `["intensidad"]` sin otro lector); `guion_v4.py:799`, `m01d_particion.py:345`, `m01c_editor.py:46` (prompts); `m03_imagenes_v3.py:32, 175` (prompt de fotos) |
| `pico` (el `escaleta.pico` y la marca `pico` por beat) | `SCHEMA` 140 | `validate` 317-346 (pico.beat bloqueante; pico.id reparación); `guion_v4.py:826, 831` (prompt), `:1265` (fecha del evento); `m01b_guionista.py:187-192` (dos frases cortas antes del pico, métrica); `m01d_particion.py:68` (protege el párrafo), `:152-157` (títulos), `:236` (skeleton `_v3.pico`); `tts_tags.py:141-146` (`[short pause] [slowly]` al abrir el pico; `[whispers]` en su golpe); `music_intensity.py:57-63, 105-109, 186` (silencio de 1,5 s antes del pico del cap); `voz_datos.py:27-41, 110-116` (pico del cap → plan gfx); `gfx_realizador.py:167`; `m01e_pantalla.py:245-248` (marca `pico` por beat), `:287` (`escaleta_video.pico`), `:577` (`picos_vacios`), `:1156`; `m01f_critico.py:76-77` (falta → error de entrada), `:296`; `m05_narrative.py:449-467` (`retencion.pico`: % acumulado, segundos después) → QA Studio `qa_studio.html:1209`; `m03_imagenes_v3.py:54-57, 139-150` (el pico lleva 2 fotos, una la más cerrada del cap); QA Studio pantalla `qa_studio_server.py:2220` |

**Para C2:** quitar el texto de M1–M7 no rompe ningún lector de código: ninguno de los siete lo lee. Lo que se rompe son los candados byte a byte (`test_module_f55.py:338/341-347` para M1–M6; `test_module_f54.py:65-71` para M7), y hay que reescribirlos contra el `.md` nuevo. El efecto río abajo es indirecto, por lo que el modelo deje de devolver. (a) Sin M1/M6, el beat 1 puede dejar de venir con `flash_forward: true` y alto. Eso cambia la curva medida (`m01a_escaleta` 332-342, a métricas), el año del relato de la pantalla (`m01e_pantalla` 342) y el reparto de reservados por fecha (668). (b) Sin M2, el cap 2 puede dejar de ser `planteo`/1 → su `narrative_intent` deja de ser `setup`, y cambian voz (audio_profiles), música (m07 por intent), arco visual (m03) y golpes de TTS (tts_tags 55). (c) Sin M3, puede no haber `respiro` → menos caps `consequences`. El mensaje «falta respiro» ya hoy no frena. M4, M5 y la «vuelta atrás» de M7 no tienen ningún lector (greps 1-4).

## D. Arreglos en espera

Base: rama `f11-guion-v4`, commit `c0cce6a`, árbol de trabajo del 2026-11-10. Solo lectura, US$ 0.

**Contexto.** La decisión es `DECISIONES.md` l.254 (2026-11-10 21:44): canal nuevo en inglés «Filed and Ignored», de 20 a 30 min, con el español por defecto y en rama aparte. Esa línea remite a `claude/RESUMEN_FILED_AND_IGNORED_2026-11-10.md`, pero **ese archivo no está**: la carpeta `claude/` no existe en el repo y `find /c/CLAUDE_PROJECTS -maxdepth 3 -iname "*FILED_AND_IGNORED*"` no devuelve nada. Esta sección se apoya solo en l.254 y en el §0 de `HANDOFF_F80a.md`.

**Cómo se lee cada grupo.**
- `también_inglés`: hay que resolverlo antes o durante el primer video en inglés. Puede ser porque lo trae la pasada de estructura de l.254, o porque el arreglo pega más fuerte en inglés o en un video de 20–30 min.
- `solo_español`: no frena el primer video en inglés y se queda en la cola del canal en español. A veces es español puro (voseo, gate ES). Otras es un tema de gusto, de Wittenoom o Colza, o algo que hoy no frena ningún video.
- `ya_no_aplica`: ya está resuelto, otra decisión lo reemplazó o era de un video que ya salió («los videos ya generados son pasado», l.252).

Cada fila es un arreglo distinto. Si dos fuentes nombran el mismo arreglo, comparten fila y la columna «fuente» lleva las dos. El conteo por fuente está al final.

### D.1 Tabla

| # | arreglo | fuente (archivo · sección/línea) | grupo | por qué va en ese grupo |
|---|---|---|---|---|
| 1 | El largo sube por config y los 7 caps no se tocan | `DECISIONES.md` l.254 (1) | también_inglés | El canal en inglés pide 20–30 min. Hoy `video_length`/`long_video` dan el largo del español (ver B). Sin esto no hay video en inglés. |
| 2 | Quitar el molde de la escaleta (reglas 2, 3 y 5 de `SYSTEM_V2`, el «nunca hoy» de la 9, el ejemplo del faro, el `<estructura>` del guionista) | `DECISIONES.md` l.254 (2); l.252 punto 3 | también_inglés | Aprobado «en una sola pasada» junto con la redirección. El molde (cap 2 tranquilo, respiro tras el pico) se pensó para 13 min. El impacto río abajo va en C2. |
| 3 | El paquete (título, promesa, detalle simple, quién avisó) entra como dato antes de la escaleta | `DECISIONES.md` l.254 (3); l.252 punto 2 | también_inglés | Es parte de la misma pasada de estructura que abre el canal nuevo. |
| 4 | Despedida de 5–15 s al cierre | `DECISIONES.md` l.254 (4), «pendiente de Omar» | también_inglés | Es una pieza de la estructura aprobada para la pasada del canal nuevo. Falta la decisión de Omar antes de programarla. |
| 5 | Rama aparte para el trabajo del inglés | `DECISIONES.md` l.254 («Español sigue por defecto; rama aparte») | también_inglés | Así el español no se rompe mientras entra el inglés. F80a no crea rama (§ encabezado del handoff); la crea la primera tanda que cambie código. |
| 6 | Formato de las cifras del pool arreglado en la raíz (research): punto o coma decimal según la fuente, horas «22.39» | `DECISIONES.md` l.114 («pendiente»); l.123 (lista F40, último punto) | también_inglés | Hoy las cifras se leen con la regla de miles del español (`num_es.parse_int`, l.113). Una fuente en inglés escribe «1,269» y «8.30». Con la regla de hoy, el pool en inglés se lee al revés. |
| 7 | Iniciales del guionista sin manejo en el normalizador ni en el cortador de oraciones | `DECISIONES.md` l.124 («A la lista de 18:30») | también_inglés | El cortador parte en «N.». De ahí salen las anclas y los subtítulos. Los nombres con iniciales son más comunes en inglés que en español. |
| 8 | El grounding de R1 sigue flojo: 3 de 4 y 2 de 4 focos quedaron «sin» | `lab/hyperframes/f77/F77_REPORT.md` §Abierto 3; `lab/ESTADO_SESION.md` l.10 | también_inglés | El research es el mismo para el inglés. Un video de 20–30 min usa más pool que uno de 13, y con focos vacíos el pool sale corto. |
| 9 | Si la foto madre rehace los rasgos en la misma corrida que m03, las fotos marcadas «rasgos» se quedan con los rasgos viejos | `lab/hyperframes/f78d/F78d_REPORT.md` §Abierto 4 y Veredicto/Riesgos 1 | también_inglés | El primer video en inglés es un topic nuevo que corre la cadena entera: foto madre y m03 en la misma corrida. Es justo el caso sin cubrir (Colza corrió por pasos). |
| 10 | Se cuela el nombre real en el texto de la foto | `F78d_REPORT.md` §Abierto 1 y Veredicto/Obs. 2; `DECISIONES.md` l.250 («se arregla si se repite»); `ESTADO_SESION.md` l.6 y l.7 (F78c, ch06_img_14) | también_inglés | La condición «si se repite» ya se cumplió (2 de 32). El prompt de foto ya está en inglés y es el mismo para los dos canales, así que el arreglo entra antes del próximo video, sea del canal que sea. |
| 11 | El primer render después de F79 no está probado de punta a punta: mezclas con `-c:v copy` y sin tpad/adelay, inicio de voz, costuras | `lab/hyperframes/f79/F79_REPORT.md` Veredicto/Obs. 5 y Adenda | también_inglés | Desde F79 no hubo render. El primer video que salga, que puede ser el inglés, es la prueba; hay que mirarlo con `ver-render`. |
| 12 | Música de ch03 y ch07 en ✗ con desvío cambiado; falso positivo de `_medir_inicio_musica` / máscara de energía sobre el silencio de una cita | `F79_REPORT.md` Cierre/Abiertos 1 y Veredicto/Obs. 4; `ESTADO_SESION.md` l.18 (F72b) y l.14 (F73 D) | solo_español | Es un chequeo de QA que marca mal; el video no cambia. Los valores son de Wittenoom. No frena. |
| 13 | Los `chXX_visual_preroll.mp4` viejos siguen en `_fase2b_work/` y entran al glob de `_segment_hash` | `F79_REPORT.md` Cierre/Abiertos 2 y Riesgos 1 | solo_español | Solo existen en Wittenoom. Un topic nuevo no los tiene. |
| 14 | AVISO (ch03) y CALMA (ch04) cambiaron por un veredicto nuevo del crítico, no por una regla | `F79_REPORT.md` Cierre/Abiertos 3 | solo_español | Es la varianza del crítico sobre sellos de vocabulario en español. El vocabulario en sí se cuenta en A. |
| 15 | Golpe del title card: ch02/ch03 +110 ms, ch04 descartado; lo decide Omar al oírlo | `F79_REPORT.md` Cierre/Abiertos 4 | solo_español | Es una cuestión de gusto sobre Wittenoom. El mismo código sirve para los dos canales. |
| 16 | La voz entra a 0,08–0,10 s, dentro de la subida desde negro | `F79_REPORT.md` Cierre/Abiertos 5 y Riesgos 3 | solo_español | Es una cuestión de gusto que Omar decide al oírlo. No frena. |
| 17 | `lab/mapa/hechos.json` y `notas_auditoria_*.md` todavía nombran `_pre_roll_de`, `INITIAL_SILENCE_SEC` y `title_pre_roll` | `F79_REPORT.md` Veredicto/Obs. 2 | solo_español | Es documentación de lab; `--check` da 0. |
| 18 | 3 tests heredados en rojo (f51c [1-start], m03_merge_timing ×2) | `F79_REPORT.md` Veredicto/Obs. 3; `F78d_REPORT.md` §Chascada | solo_español | No frenan. f51c depende del `sync_map` de Wittenoom y merge_timing de la regla de 4 letras para anclas de una palabra. |
| 19 | 4 archivos modificados sin commitear: `diag_234_cap4.py`, `f28a.log`, `pedido_paquetes_wittenoom.txt`, `f78d/a/lista_aspecto.md` | `F79_REPORT.md` Veredicto/Obs. 1 y Adenda; `F78d_REPORT.md` Veredicto/Obs. 1 y Adenda | solo_español | Es higiene del árbol. Ojo: la adenda de F78d dice que `lista_aspecto.md` se restauró, pero el `git status` de hoy lo sigue mostrando `M`. |
| 20 | Carmen adulta (ch07_supp_07/08/09): no se lee de 33, la escena le pisa la trenza y volvió con otra persona | `F78d_REPORT.md` §Abierto 2 y Obs. 3; `lab/hyperframes/f78a/F78a_REPORT.md` §Abierto; `lab/hyperframes/f78a/F78b_REPORT.md` §Abierto; `ESTADO_SESION.md` l.6, l.8 y l.9 | solo_español | Es de Colza. No frena. |
| 21 | El refill puede sumar personas que el casillero no nombra (ch04_img_12) | `F78d_REPORT.md` §Abierto 3 y Riesgos 2 | solo_español | No frena. Se mira si se repite. |
| 22 | ch04_img_12: chica de espaldas con la espalda descubierta (respaldo Seedream); mirarla | `F78d_REPORT.md` Veredicto/Obs. 4; `ESTADO_SESION.md` l.6 | solo_español | Es una foto de Colza. |
| 23 | «Tocada en QA» se detecta por la copia en `_qa_backups`; una edición sin copia no se ve | `F78d_REPORT.md` Veredicto/Riesgos 3 | solo_español | No frena. Es la regla de la adenda 1.1. |
| 24 | Omar revisa en QA Studio las fotos de Colza | `ESTADO_SESION.md` l.6 (F78d) | solo_español | Es de Colza. |
| 25 | Nano Banana modera a los menores con estado; el respaldo Seedream cambia el estilo | `F78a_REPORT.md` §Abierto; `F78b_REPORT.md` §Abierto | solo_español | No frena: el respaldo existe. |
| 26 | La madre nueva de Mercedes trae marco oscuro (foto dentro de foto) | `F78a_REPORT.md` §Abierto; `F78b_REPORT.md` §Abierto («se arregla si se repite»); `ESTADO_SESION.md` l.9 («Mercedes madre con marco») | solo_español | Es de Colza y está en la lista «si se repite». |
| 27 | Con variantes, la regla «sin madre si el estado cae fuera de la era» podría pasar a «variante» (decisión de Omar) | `F78a_REPORT.md` §Abierto, último punto | solo_español | No frena. Es una decisión abierta. |
| 28 | Lozano llora en la variante y la expresión queda fija en sus 3 fotos | `F78b_REPORT.md` §Abierto | solo_español | Es de Colza y es una cuestión de gusto. |
| 29 | El gate de Palomares depende del título (VACIO / DISPUTADO) | `F77_REPORT.md` §Abierto 2 | solo_español | Es el gate ES. |
| 30 | La velocidad con 4 research a la vez no está probada | `F77_REPORT.md` §Abierto 4 | solo_español | No frena. |
| 31 | Mensaje confuso al elegir del estante («No se generaron seeds») | `F77_REPORT.md` §Abierto 5 | solo_español | No frena: el camino sigue bien. |
| 32 | Los menús D y E del form no se probaron en vivo | `F77_REPORT.md` §Abierto 6 | solo_español | No frena. |
| 33 | `exit 2` vale tanto para «compuerta roja» como para «ficha fallida» | `F77_REPORT.md` §Abierto 7 | solo_español | No frena. |
| 34 | Los juicios del gate no se atribuyen a ningún topic | `F77_REPORT.md` §Abierto 8 | solo_español | Son costos del gate ES. |
| 35 | El pool fusiona homónimos padre/hijo | `F77_REPORT.md` §Abierto 9 (1.er subpunto) | solo_español | Pendiente de antes. No frena. |
| 36 | Las rachas no cuentan pronombres | `F77_REPORT.md` §Abierto 9 (3.er subpunto) | solo_español | Los pronombres son lógica del español. En inglés se cuenta en A. |
| 37 | Personajes con partícula | `F77_REPORT.md` §Abierto 9 (4.º subpunto) | solo_español | La partícula «de/del» es del español. En inglés se cuenta en A. |
| 38 | ch07 #6 cae 2,16 s antes (años con el mismo trigrama) | `lab/hyperframes/f71/F71_REPORT.md` Veredicto; `ESTADO_SESION.md` l.21 | solo_español | Es de Wittenoom. No frena. |
| 39 | Un error de clip que no es rechazo ya no va a Kling: el cap sale con foto | `F71_REPORT.md` Veredicto; `ESTADO_SESION.md` l.21 | solo_español | No frena: el cap sale igual. |
| 40 | `_reconcile_anchor_timing` sin `narr_norm` (F71 lo cita como `m03_visual.py:1408`; hoy la llamada a `compute_anchor_starts` está en `script_engine/m03_visual.py:1459`) | `F71_REPORT.md` l.36, l.78 y l.100 | solo_español | Solo pega si se rearma m03 con audio ya grabado. F71 lo da por no bloqueante. Si A vuelve dato el normalizador, este llamador entra en el mismo arreglo. |
| 41 | El modo C (inyección manual) no se probó en el form real | `ESTADO_SESION.md` l.13 (F74) | solo_español | Vuelve a medir el gate ES. |
| 42 | `IDENTIDAD_misterio.md` todavía lista la pregunta de cierre y `TAIL_SEC` 4,5 | `ESTADO_SESION.md` l.16 (F72d) | solo_español | Es doc del canal en español. |
| 43 | Lo que se sigue leyendo de la escaleta (`a_pantalla`, `pico`, `dato_central`) queda desfasado cuando se aprueba la narración | `ESTADO_SESION.md` l.18 (F72b) | solo_español | Wittenoom salió así, no frena. Se cruza con C2: quién lee la escaleta. |
| 44 | Escala de nota del crítico | `ESTADO_SESION.md` l.50 (F67 §9) | solo_español | Espera a Omar. No frena. |
| 45 | DEBERÍA sin truncar a 8 (implementado, pendiente) | `ESTADO_SESION.md` l.50 (F67 §9) | solo_español | Falta que Omar lo confirme. No frena. |
| 46 | Forma del reloj (F31b, «se ven pobres») | `DECISIONES.md` l.37 y l.79 | solo_español | Es una cuestión de forma. Omar no eligió variante y F31b nunca corrió: `ESTADO_SESION.md` l.1039 dice «Ninguna variante es default: Omar elige → F31b» y es la única mención de F31b en ESTADO. Los meses en español se cuentan en A. |
| 47 | Variante de forma de F31 (V1–V3, S1–S3, R1–R2) | `DECISIONES.md` l.103 («pendiente») | solo_español | Es una cuestión de forma. No frena. |
| 48 | Que el código lea este archivo (`gfx_config` carga constantes desde DECISIONES) | `DECISIONES.md` l.110 (§Pendientes de infraestructura) | solo_español | No está hecho: `git grep -n "DECISIONES.md" -- gfx_config.py script_engine/` da 0. No frena. |
| 49 | Bloqueantes falsos de citas (la traducción de la ficha ≠ la del pool; «…») | `DECISIONES.md` l.123 («A la lista, sin tanda») | solo_español | En la lista «si se repite». No frena. |
| 50 | Detector de voseo | `DECISIONES.md` l.123 | solo_español | Es español puro. |
| 51 | Títulos automáticos: pasarlos al autor del papel | `DECISIONES.md` l.123 | solo_español | En la lista «si se repite». El prompt de títulos en español se cuenta en A. |
| 52 | Ficha de relleno en picos | `DECISIONES.md` l.123 | solo_español | En la lista «si se repite». |
| 53 | Fotos posadas (4/96) y planos medios que el motor abre a wide en exteriores | `DECISIONES.md` l.202 («se arregla si se repite») | solo_español | No frena. |
| 54 | Rediseñar la corrección automática del verificador «antes del tema 2» (corregir con el dato, nunca sacar, proteger promesa y re-gancho) | `DECISIONES.md` l.213; `ESTADO_SESION.md` l.76 (F66b, «Pendiente») | solo_español | Hoy el verificador solo avisa, no edita. No frena ningún video. |
| 55 | Arreglo general del armado del prompt de foto (texto que se cuela en la imagen) «antes del tema 2» | `DECISIONES.md` l.228; `ESTADO_SESION.md` l.23–24 (F70b, LAB F70) | solo_español | No frena. Colza salió sin él. |
| 56 | Subida por API (m09b) | `DECISIONES.md` l.238 («para una tanda posterior») | solo_español | El primer video en inglés se puede subir a mano. No hay archivo m09b en git (`git ls-files \| grep -i m09` solo trae `m09_packaging` y `m09_review_server`). El canal por API se cuenta en A (`canal`). |
| 57 | El tema se elige al revés: vistas ES a favor y bloqueo sin demanda | `DECISIONES.md` l.252 punto 1 | solo_español | Mide demanda en español. Los temas del inglés salen del chat de estrategia (l.254). |
| 58 | «El primer cap del video no lleva title card»: falta que Omar lo confirme | `DECISIONES.md` l.253 («voto del analista, pendiente de que Omar lo confirme») | solo_español | Ya está en código (F79 A2) y vale igual para los dos canales. La confirmación no frena. |
| 59 | Ficha un escalón más chica: «pendiente de ver en render» | `DECISIONES.md` l.34 | ya_no_aplica | Hubo renders después (F72c, F72e: `ESTADO_SESION.md` l.15 y l.17). |
| 60 | En caps de una sola escena (Veo), la unidad es la oración | `DECISIONES.md` l.39 («pendiente de confirmar») | ya_no_aplica | Veo se borró (`DECISIONES.md` l.159, F53b). |
| 61 | Sonnet elige los sellos en la llamada del rotulista | `DECISIONES.md` l.47 («pendiente de tanda») | ya_no_aplica | Lo reemplaza l.88: el autor del papel (`m01e_pantalla`) elige con el vocabulario y `rotulista_llm` se borra. |
| 62 | Mapa de módulos con flujograma y stickers | `DECISIONES.md` l.107 | ya_no_aplica | Hecho en F42 (`lab/MAPA_PROYECTO.md`, `mapa_modulos.py --check`). |
| 63 | Hook que bloquea `fase2b --gfx` sin `GUION_PANTALLA.json` aprobado | `DECISIONES.md` l.108 | ya_no_aplica | Existe: `.claude/hooks/guard_render.py` (F33 §B.2). |
| 64 | `/tanda` con PARADA y subagente simulador | `DECISIONES.md` l.109 | ya_no_aplica | Existen: el comando `/tanda` (`.claude/commands/tanda.md`), el skill `simular-reglas` (`.claude/skills/simular-reglas`) y el agente `simulador` (`.claude/agents/simulador.md`). |
| 65 | Subtítulos en registro documental | `DECISIONES.md` l.117 («pendiente de tanda») | ya_no_aplica | Aplicado en F40 B: el candado md5 de ch02 es «desde F40 (subtítulos documentales)» (`ESTADO_SESION.md` l.58). |
| 66 | Títulos de cap: dar el pico y el `cierre` de cada cap | `DECISIONES.md` l.118 («pendiente de tanda») | ya_no_aplica | Hecho: `script_engine/m01d_particion.py:148-162` (F38e §E) pasa la marca de pico y «termina (no lo cuentes)». |
| 67 | Quitar la tarjeta fecha-hora del segundo 0 | `DECISIONES.md` l.119 («pendiente de tanda») | ya_no_aplica | Borrada en F38e: `git grep -c "tarjeta" -- script_engine/ gfx_config.py fase2b.py` da 0. |
| 68 | Prueba 1, rótulos parafraseados | `DECISIONES.md` l.120 («pendiente de prueba») | ya_no_aplica | Se midió en F38e-0 y entró como m01e-6 (l.121). Hoy rige m01e-7. |
| 69 | La foto inicial de un cap con clip no se rehace desde QA | `DECISIONES.md` l.182 a) («abierto») | ya_no_aplica | Lo resolvió F69 (`ESTADO_SESION.md` l.22: «la foto de arranque del clip se rehace de un botón»). |
| 70 | Madres de niños (edad) y madres del mismo tipo parecidas | `DECISIONES.md` l.200 («se arregla si se repite») | ya_no_aplica | F78a (rasgos propios por persona) y F78b (edad exacta). |
| 71 | Los otros 4 DEBERÍA del crítico de Wittenoom | `DECISIONES.md` l.221 («se arregla si se repite») | ya_no_aplica | Son de Wittenoom, que ya salió (l.252: «los videos ya generados son pasado»). |
| 72 | Mezcla a −14 LUFS + limitador antes del render del tema 2 | `DECISIONES.md` l.237 («va en otra tanda») | ya_no_aplica | Hecho en F76 (l.241) y aprobado por oído (l.242). |
| 73 | Aire muerto fuera (intro, title card mudo, pausa tras cita) | `DECISIONES.md` l.252 punto 4 | ya_no_aplica | Aplicado en F79 (l.253). |
| 74 | Primer paso: reporte de solo lectura | `DECISIONES.md` l.254 | ya_no_aplica | Es esta tanda (F80a) y se cierra con este reporte. |
| 75 | El guion de pantalla de Wittenoom quedó sin aprobar después de F79 | `ESTADO_SESION.md` l.5; `F79_REPORT.md` Riesgos 2 | ya_no_aplica | Wittenoom ya está publicado (`ESTADO_SESION.md` l.11: «Wittenoom publicado sigue a −24»). Un topic nuevo arranca con su propio guion. |
| 76 | ch07_clip_01 se regeneró con el mismo texto | `F78d_REPORT.md` §Abierto 5 y Obs. 5 | ya_no_aplica | Es informativo: lo pedía el handoff. |
| 77 | Etapa C de F78a sin correr | `F78a_REPORT.md` §Abierto 1; `F78b_REPORT.md` §Abierto 1; `ESTADO_SESION.md` l.9 | ya_no_aplica | Corrió en F78d C (`ESTADO_SESION.md` l.6). |
| 78 | Lozano@1981: la variante dibuja la escena del estado | `F78a_REPORT.md` §Abierto 2; `ESTADO_SESION.md` l.9 | ya_no_aplica | F78b rehízo las variantes con `estado_visible`, sin la condición cruda (l.8). |
| 79 | `lab/hyperframes/f60/etapa_bc_prueba.py:90` con la firma vieja de `_clave_lote` | `F78a_REPORT.md` §Abierto; `F78b_REPORT.md` §Abierto («no entra») | ya_no_aplica | Es un script de lab, fuera de producción, y está marcado «no entra». |
| 80 | La deformación de manos de Arcadio no pasa a la escena | `F78b_REPORT.md` §Abierto 2 | ya_no_aplica | `DECISIONES.md` l.250: las manos deformes «se quedan, sin close-up». |
| 81 | El refill cambió de persona en 2 de 5 (F78c) | `ESTADO_SESION.md` l.7 | ya_no_aplica | F78d lo maneja como `persona_distinta`: se queda la foto vieja, sin reintento. |
| 82 | La llave de OpenAI vencida bloquea la ficha (Palomares, Colza) | `F77_REPORT.md` §Abierto 1; `ESTADO_SESION.md` l.10 | ya_no_aplica | Las dos fichas existen: `data/scripts/_steps/1b2a2c5d…/ficha_caso.json` y `c4934b7d…/ficha_caso.json`. |
| 83 | La escaleta no comprueba que `humano.id` coincida con su `rol` | `F77_REPORT.md` §Abierto 9 (2.º subpunto) | ya_no_aplica | `DECISIONES.md` l.239 (F75 A1): `escaleta.humano` deja de ser la fuente del personaje. |
| 84 | Omar escucha los extractos de F76 antes de Palomares | `ESTADO_SESION.md` l.11 | ya_no_aplica | Aprobado por oído (`DECISIONES.md` l.242). |
| 85 | F75: Omar escucha; C2 sin cablear | `ESTADO_SESION.md` l.12 | ya_no_aplica | Lo reemplazó F76 (l.241). |
| 86 | F72e: Omar mira el video; packaging diferido | `ESTADO_SESION.md` l.15 | ya_no_aplica | Wittenoom publicado (l.11). |
| 87 | F72c: en ch07 falta 1 cuadro en la costura | `ESTADO_SESION.md` l.17 | ya_no_aplica | F72e: «ch07 ya no tiene el cuadro de menos» (l.15). |
| 88 | F72: Omar decide `ch01_supp_02` y `ch03_img_16` | `ESTADO_SESION.md` l.19 | ya_no_aplica | Son fotos de Wittenoom, que ya salió. |
| 89 | F71b: la mujer desaparecida y la foto impresa como dos fotos pegadas | `ESTADO_SESION.md` l.20 | ya_no_aplica | Es de Wittenoom, que ya salió. |
| 90 | F69: falso rechazo «nsfw» dentro del base64 (`_is_content_rejection`) | `ESTADO_SESION.md` l.22 | ya_no_aplica | F71: «falso "nsfw" cerrado» (l.21). |
| 91 | Hojas NB-TOL6 / NB-AHORCADO: censura suave y caras sin juzgar | `ESTADO_SESION.md` l.40 (LAB NB-TOL6) | ya_no_aplica | F68 eligió el motor (`DECISIONES.md` l.224). |
| 92 | F68b: `ch01_img_01` con 6 chicos y borde de diapositiva | `ESTADO_SESION.md` l.29 | ya_no_aplica | F69 la rehízo: «Daniel solo, sin niños ni borde» (l.22). |
| 93 | F68b: no usar `--reuse-visuals` en ch01/ch07 | `ESTADO_SESION.md` l.30 | ya_no_aplica | F72 volvió a cocer ch01 y ch07 con los clips nuevos (l.19). |
| 94 | `compute_anchor_starts` falla en 5 caps antes de los fondos | `ESTADO_SESION.md` l.31 y l.36 | ya_no_aplica | F71 y F72: 97/97 anclas por trigrama (l.19, l.21). |
| 95 | El QA en :8002 está viejo | `ESTADO_SESION.md` l.35 | ya_no_aplica | Era una sesión del 1-nov. |
| 96 | Corrida de Wittenoom parada por las fotos («no retomar sin resolverlas») | `ESTADO_SESION.md` l.43 | ya_no_aplica | F68 rehízo las fotos y F72/F72e terminaron el video. |
| 97 | Botón «volver a criticar» | `ESTADO_SESION.md` l.50 (F67 §9, «no entra») | ya_no_aplica | Decidido que no entra; además l.221 cierra el `--criticar` sobre Wittenoom. |
| 98 | `humano` de la escaleta de Wittenoom en P16 (las rachas no sirven) | `ESTADO_SESION.md` l.50 | ya_no_aplica | F75 A1: el personaje sale de la narración (`DECISIONES.md` l.239). |
| 99 | F67c: el empaquetado del 30-oct sigue reusable | `ESTADO_SESION.md` l.3 (cabecera) | ya_no_aplica | F73 B lo movió a `publish/_desfasado_20261104_073537` (l.14). |
| 100 | Malla del mood agua: falta que Omar la confirme a ojo | `ESTADO_SESION.md` l.1662 (§Pendiente, era F3) | ya_no_aplica | El nivel de agua se borró del código (`DECISIONES.md` l.85, catálogo 18:17). |
| 101 | Pregunta de ch02 más concreta (`gfx_question`) | `ESTADO_SESION.md` l.1663 | ya_no_aplica | `gfx_question` se borró (l.57) y la pregunta de cierre también (F72d, l.234). |
| 102 | Video completo con pausas de cierre sin renderizar | `ESTADO_SESION.md` l.1664 | ya_no_aplica | Las pausas de cierre se borraron (F72d) y hubo renders completos (F72c/F72e). |
| 103 | Golpe de zoom sobre video (punch-in, mood muerte) | `ESTADO_SESION.md` l.1665 | ya_no_aplica | Los `punch_in` se borraron; el único golpe es el `zoom_punch` del pico (`DECISIONES.md` l.38). |
| 104 | §D y §E del HANDOFF_F3 (plantillas, director con identidad) | `ESTADO_SESION.md` l.1667 | ya_no_aplica | Los reemplazó el catálogo de 9 componentes (l.74–86) y el autor de pantalla en Fase 1 (l.88). |

Totales por grupo: **también_inglés 11** (1–11) · **solo_español 47** (12–58) · **ya_no_aplica 46** (59–104) · **104 filas**.

### D.2 Conteo por fuente (abiertos en la fuente = filas que los cubren)

Cuando una fila cubre abiertos de más de una fuente, cuenta en cada fuente que la nombra.

| Fuente | Qué se contó | Abiertos | → filas |
|---|---|---|---|
| `lab/hyperframes/f79/F79_REPORT.md` Cierre/Abiertos | puntos 1–5 | 5 | 5 → 12, 13, 14, 15, 16 |
| `F79_REPORT.md` Veredicto del revisor | Observaciones 1–5 + 3 riesgos | 8 | 8 → 19, 17, 18, 12, 11 · 13, 75, 16 (4 comparten fila con Abiertos o ESTADO) |
| `lab/hyperframes/f78d/F78d_REPORT.md` §Abierto | puntos 1–5 | 5 | 5 → 10, 20, 21, 9, 76 |
| `F78d_REPORT.md` Veredicto del revisor | 5 observaciones + 3 riesgos | 8 | 8 → 19, 10, 20, 22, 76 · 9, 21, 23 |
| `lab/hyperframes/f78a/F78a_REPORT.md` §Abierto (citado en ESTADO l.9) | 7 viñetas | 7 | 7 → 77, 78, 20, 25, 26, 79, 27 |
| `lab/hyperframes/f78a/F78b_REPORT.md` §Abierto (citado en ESTADO l.8) | 7 viñetas | 7 | 7 → 77, 80, 28, 20, 26, 79, 25 |
| `lab/hyperframes/f77/F77_REPORT.md` §Abierto (citado en ESTADO l.10) | puntos 1–8 + 4 subpuntos del 9 | 12 | 12 → 82, 29, 8, 30, 31, 32, 33, 34, 35, 83, 36, 37 |
| `lab/hyperframes/f71/F71_REPORT.md` Veredicto (citado en ESTADO l.21) | los «3 puntos abiertos» | 3 | 3 → 38, 39, 40 |
| `lab/ESTADO_SESION.md` | entradas vigentes (lista abajo) | 47 | 47 |
| `DECISIONES.md`, por estado | «pendiente», «pendiente de tanda», «pendiente de confirmar», «pendiente de prueba», «pendiente de handoff», «pendiente de Omar», «pendiente de forma» | 26 | 26 |
| `DECISIONES.md`, otras marcas de espera | «se arregla si se repite», «A la lista», «abierto», «antes del tema 2», «otra tanda», «tanda posterior» | 15 | 15 |

**ESTADO_SESION, 47 abiertos.** Entre paréntesis, las filas.
- l.3: 1 (99).
- l.5: 1 (75).
- l.6: 4 (24, 10, 20, 22).
- l.7: 2 (81, 10).
- l.8: 1 (20).
- l.9: 4 (77, 78, 20, 26).
- l.10: 2 (82, 8).
- Una cada una (10 en total): l.11 (84), l.12 (85), l.13 (41), l.14 (12), l.15 (86), l.16 (42), l.17 (87), l.19 (88), l.20 (89), l.22 (90). La l.25 (LAB NB-AHORCADO) solo da resultados («producción sin tocar») y no deja nada en espera: no cuenta.
- l.18: 2 (12, 43).
- l.21: 2 (38, 39).
- l.23–24: 1 (55).
- l.29: 1 (92).
- l.30: 1 (93).
- l.31 + l.36: 2 (94, 94).
- l.35: 1 (95).
- l.40: 1 (91).
- l.43: 1 (96).
- l.50: 4 (44, 45, 97, 98).
- l.76: 1 (54).
- §Pendiente l.1662–1667: 5 (100–104). La viñeta tachada de l.1666 («~~Perfil guardado…~~ → resuelto en F4») no cuenta.
- Las 47 asignaciones caen en 42 filas distintas de D.1 (la 10 y la 12 aparecen dos veces, la 94 dos —l.31 y l.36— y la 20 tres —l.6, l.8, l.9—), y cada una está citada en la columna «fuente» de su fila: 47 citas de `ESTADO_SESION.md`.

**DECISIONES por estado, 26 abiertos.**
- l.34 (59) · l.37 + l.79 (46, 46) · l.39 (60) · l.47 (61) · l.103 (47).
- l.107–110, 4 viñetas de «Pendientes de infraestructura» (62, 63, 64, 48).
- l.114 (6) · l.117 (65) · l.118 (66) · l.119 (67) · l.120 (68).
- l.252, 4 puntos (57, 3, 2, 73).
- l.253, la confirmación pendiente (58).
- l.254, 6 partes: (1), (2), (3), (4), rama aparte y primer paso (1, 2, 3, 4, 5, 74).
- Suma: 1+2+1+1+1+4+1+1+1+1+1+4+1+6 = 26.

**DECISIONES, otras marcas, 15 abiertos.**
- l.123, 5 puntos de la lista F40 (49, 50, 51, 52, 6).
- l.124 (7) · l.182 a) (69) · l.200 (70) · l.202 (53) · l.213 (54) · l.221 (71) · l.228 (55) · l.237 (72) · l.238 (56).
- l.250, el nombre real colado (10). En l.250, las manos y Nano Banana 2 completo son decisiones cerradas, no abiertos.

### D.3 Cómo se decidió qué entradas de ESTADO_SESION siguen vigentes

1. Se buscaron las marcas `abierto|pendiente|se arregla si se repite|omar decide|omar escucha|para omar` en todo el archivo: 199 líneas de 1712. La mayoría son el historial de cada tanda.
2. **Vigente** quiere decir:
   - la cabecera: l.3, la línea «Última actualización»;
   - la lista de estado l.5–25, de F79 hacia atrás hasta LAB NB-AHORCADO, que es el resumen al día que mantiene CC;
   - los bloques que siguen a la cabecera, l.27–51: los «Para Omar» de F68b y F68, LAB NB-TOL6, la corrida parada de Wittenoom y la tanda F67 con su §9 «Esperan a Omar»;
   - la única sección titulada `## Pendiente` (l.1661).
3. Los bloques de F66b para atrás (l.64 en adelante) son historial de tandas ya cerradas o reemplazadas. No se tomaron fila por fila. La excepción es lo que una entrada vigente o DECISIONES arrastra de forma explícita: el «Pendiente: rediseñar la corrección» de F66b (l.76), que repite `DECISIONES.md` l.213 (fila 54).
4. Cada abierto de esa zona se contrastó con lo que vino después: un texto posterior de ESTADO, una línea de DECISIONES o una prueba en el árbol (`git grep`, `ls`). Si apareció la resolución, va a `ya_no_aplica` y la columna «por qué» cita esa resolución.
5. De los F*_REPORT se abrió la sección de abiertos en dos casos: F79 y F78d, que pide el handoff, y los que ESTADO cita como abiertos sin resolver, que son F78a, F78b, F77 y F71. Para F72b, F72d, F73 y F74, ESTADO trae el abierto en la misma línea y se tomó de ahí. F76 y F75 solo dicen «Omar escucha» y DECISIONES l.242 ya lo cierra.

## E. Tamaño del trabajo

Sin horas. Cada cifra sale de una tabla de A–D (se dice de cuál) o de un `git grep` (se pega el comando). Los conteos de A se hicieron leyendo las columnas «tipo», «tests que lo fijan» y «cómo se volvería dato» de las tres tablas (A-1: 198 filas, A-2: 156 filas, A-3: 103 filas; total 457 filas, 437 `archivo:línea` distintos, porque A-1 y A-3 repiten 20 lugares: los literales del canal y `fase1_5.py:876`).

**Cómo se reparte A en bloques.** Una fila va a un bloque según su columna «cómo se volvería dato»: `perfil` → bloque 1, `prompt_por_idioma` → bloque 2, `codigo` → bloque 3; con tipo `rutas` → bloque 5, diga lo que diga. Hay 17 filas con dos marcas (7 `perfil`+`prompt_por_idioma`, 6 `perfil`+`codigo`, 3 `codigo`+`rutas`, 1 `codigo`+`prompt_por_idioma`): cuentan en los dos bloques. Hay 12 filas que no piden nada («ya sirve», «ya es perfil», «informativo»): no entran en ningún bloque.

**Un ajuste a propósito.** De las 126 filas `perfil` de A, hay 28 que están **dentro de un prompt**: 16 de tipo `prompt` (el nombre del idioma en el texto, p. ej. `m03_visual.py:591` «Narration (Spanish…)», `guion_v4.py:184` «en español neutro», `video_prompt.py:54` «NARRATION DURING THE CLIP (Spanish)») y 12 de tipo `canal` (el literal «Misterios Sepultados» en `m01a_escaleta.py:879`, `guion_v4.py:97/184`, `m01a_columna.py:40`, `ficha_caso.py:139`, `m01f_prompts/SYSTEM.txt:1`, `step_4c_meta.py:98`, `m09_packaging.py:95`). Las paso al bloque 2. Si el inglés va en un prompt hermano, ese prompt trae su propio nombre de canal e idioma, y el prompt español no se toca: no cambia ningún md5 ni ningún candado byte a byte. Si en cambio se mete el nombre del canal como dato del perfil, cambian los md5 fijados (lo avisa A-1, «Lo que pesa más» 3). Con este ajuste, el bloque 1 queda con 98 filas y ningún candado byte a byte.

### E.1 Tabla por bloque

| bloque | archivos | prompts | filas (fuente) | tests que lo fijan (contrato) | de esos, byte a byte o md5 | riesgo | depende de |
|---|---|---|---|---|---|---|---|
| **(1) Perfil por canal** | 39 | 0 propios (los 28 que viven en prompts pasan al bloque 2) | 98 filas, 92 lugares distintos (A, `perfil` sin `rutas` y sin las 28 de arriba). Por tipo: `logica_idioma` 36 (listas: meses, unidades, partículas, stopwords, umbrales del mercado), `api_idioma` 19, `voz` 15, `texto_pantalla` 14, `canal` 11, `karaoke` 3 | 51 archivos de test | 0. Sí hay tests de contrato que afirman el valor español: `test_module_f9.py` (`language_code == "es"`, fila `audio_manager.py:810`), `test_module_f77a.py` (`relevanceLanguage == "es"`, fila `youtube_scanner.py:1255`), `test_module_f74.py` (`already_es is True`, fila `niche_discoverer.py:1370`), `test_module_f34.py` («OCT») y `test_module_f37b_colocar.py` («FEB») (fila `voz_datos.py:15`) | **Bajo** si el perfil español devuelve exactamente los valores de hoy: nada cambia de salida. Sube a **medio** en la parte de voz: `voice_lufs_v4`, `VOICE_SETTINGS_BY_INTENT_V4` y `SLOWLY_WPS` están calibrados con el narrador español (filas `audio_profiles.py:23, 127`, `tts_tags.py:26`) y para inglés hay que medirlos de nuevo, no copiarlos | nada. Es la base: el bloque 3 lee de acá el idioma y el bloque 4 la duración. Ya hay costuras parciales que conviene reusar: `gfx_config.active_profile_name` (A-2, fila `gfx_config.py:344`, «ya es perfil»), `audio_config.ACTIVE_AUDIO_PROFILE` (fila `audio_config.py:8`), `config.long_video` (B.2) |
| **(2) Prompts en inglés** | 40 | **52 llamadas de producción** con texto en español o que piden salida en español, más **16** de legado o de flag (lista abajo, E.2) | 180 filas, 170 lugares distintos (las 159 `prompt_por_idioma` de A más las 28 del ajuste). Por tipo: `prompt` 131 + 16, `ejemplo` 21, `canal` 5 + 12, `texto_pantalla` 2 | 69 archivos de test | **16 archivos** con candado sobre un prompt (columna «tests» de A con «byte-idéntico», «md5», «letra por letra» o «= lab»): `test_module_f55.py`, `f54.py`, `f22.py`, `f17.py`, `f23.py`, `f21.py`, `f38e_e.py`, `f38e_c.py`, `f37a_papel.py`, `f38c_papel.py`, `f40_gancho.py`, `f64.py`, `f66.py`, `f58.py`, `f57.py`, `tests/test_m01f_compuerta.py`. Cubren 11 de las 52 llamadas (E.2). Un prompt hermano **no los toca**: siguen comparando el texto español | **Medio.** No rompe el español (los prompts españoles no se editan). El riesgo está en el inglés: son 52 textos largos, varios con ejemplos que el modelo copia (21 filas `ejemplo`), y 10 de las 52 llamadas (las de A-3.1: `subtopic_es_relevance` ×2, `niche_discoverer` ×3, `subtopic_classifier`, `subtopic_extractor` ×2, `m_judge_seeds`, `topic_validator`) no se traducen: son del gate de temas, que mide el hueco **en español** y necesitan otro diseño por mercado (A-3, párrafo de apertura) | **6** (estructura): si se traduce antes de quitar M1–M7, `SYSTEM_V2` y `SYSTEM_V5_6` se traducen dos veces. **1** (el perfil elige qué prompt va). **3** para que los bloqueantes y validadores que revisan la salida inglesa funcionen |
| **(3) Lógica por idioma** | 38 | 0 | 145 filas, 142 lugares distintos (A, `codigo`). Por tipo: `logica_idioma` 126, `voz` 7, `karaoke` 4, `rutas` 3, `api_idioma` 2, otros 3. Los archivos con más filas: `evidence.py` 11, `m01a_escaleta.py` 10, `guion_v3_reglas.py` 10, `youtube_scanner.py` 10, `m05_narrative.py` 9, `num_es.py` 8 | 56 archivos de test | 0 byte a byte. Los 56 son tests de comportamiento en español: siguen valiendo para la rama española y hacen falta tests nuevos para la inglesa | **Alto.** Los detectores de cifras y fechas (`evidence.py`, `num_es.py`, `guion_v3_reglas.DATE_PARAPHRASE`, `m01a.NUM_WORDS`) deciden `ids_usados` y los bloqueantes (f)/(h), y en inglés **no fallan: devuelven «no dicho» sin avisar** (A-1, «Lo que pesa más» 2). Además, dos arreglos de D caen acá: el formato de cifras del pool, coma o punto (D fila 6), y las iniciales en el cortador de oraciones (D fila 7) | **1** (de dónde sale el idioma) y el idioma del pool en R3 (A-1, «Lo que pesa más» 1, filas `research_v3.py:1401, 1408, 2620`, que están en el bloque 1). El gate de temas (A-3.1) depende además de una decisión aparte: cómo se elige el tema en un canal inglés (DECISIONES l.252, punto 1, «en otra tanda») |
| **(4) Duración** | 18 nombrados en B.9 (abajo); para el mínimo, 1 | 2 con el largo escrito: `m01a_escaleta.py:883` («de 7 a 14 beats», en `SYSTEM_V2`) y `m01f_prompts/SYSTEM.txt:1` («de 10 a 12 minutos», A-1). Más 2 textos de reporte: `pool_gate.py:106, 108` y `step_4d_summary.py:61` (B.8) | B.1 (23 claves de `DEFAULTS`), B.2 (19 campos de `long_video`, 8 sin lector), B.3–B.8 | **29** archivos de test nombran algún parámetro de B (comando abajo, grep 1). Solo 3 importan `video_length` (`test_module_f25c.py`, `f7.py`, `f7d.py`) | 0. B no tiene columna de tests; el grep 2 de abajo no encuentra candados md5 sobre `video_length` | **Medio-alto.** Si el perfil español da los mismos valores, el español no cambia (los 23 `DEFAULTS` y `config.long_video` ya llegan por `video_length.get`, B.1). El riesgo está en el video largo, y nada de eso está medido: el texto de más se recorta solo (B.9 punto 1), las fotos topan en 16 por cap (B.9 punto 4), el render gfx sale sin gráficos pasados los 1500 s por cap (B.9 punto 5, y el propio comentario dice que caps de ~3 min ya tardan 956–983 s), los re-encode tienen tope de 600 s y 300 s (B.9 punto 6) y la voz va en un request por cap sin tope de caracteres verificado (B.9 punto 10). `config.py` no está en git (B, encabezado): un cambio ahí no deja diff | **1** (la duración es un valor del perfil). Los números del inglés no los fija este reporte: salen de DECISIONES (CLAUDE.md, regla 1) |
| **(5) Carpetas por canal** | 20 | 0 | 32 filas `rutas` (A-1: 3, A-2: 5, A-3: 24). De esas, **18** son archivos únicos para todos los temas, y esos sí chocan entre canales: `topics_db.py:20`, `fase1.py:73, 79, 117, 530`, `topics_db.json:1`, `cost_tracker.py:84`, `niche_discoverer.py:123, 204`, `topic_validator.py:65`, `estante.py:35, 36`, `tts_normalizer.py:181`, `m02_5_normalizer_gate.py:50`, `qa_studio_server.py:1639`, `m07_music_director.py:72`, `CLAUDE.md:3, 11`. Las otras 14 cuelgan del id del tema (un uuid, p. ej. `qa_studio_server.py:70`), así que no chocan entre canales | 15 archivos de test | 0 | **Medio.** Las rutas cuelgan de `DATA_DIR` / `OUTPUT_DIR` de `config.py`, que no está en git (A-3, encabezado). Además, `qa_studio_server.py:139, 141, 923` arma las rutas a mano (filas `codigo`). Hay tests que escriben en disco real (memoria del proyecto «Tests viejos escriben en disco real»): una ruta mal movida escribe en `data/` de verdad | **1** (el perfil dice cuál es la raíz). La biblioteca de música compartida (`m07_music_director.py:72`) y si DECISIONES / ESTADO_SESION se separan por canal son decisiones de Omar, no de código |
| **(6) Estructura: M1–M7 + paquete antes de la escaleta** | M1–M7: 2 (`m01a_escaleta.py`, `guion_v4.py`) + 2 `.md` nuevos de lab contra los que se fijan los tests. Paquete: al menos 5 (`m09_packaging.py`, `fase1_5.py`, `m01a_escaleta.py`, `guion_v4.py`, `m01f_prompts/`) | M1–M7: 2 (`SYSTEM_V2`, `SYSTEM_V5_6`; C2). Paquete: 4 tocados (`PEDIDO_PAQUETES` `m09_packaging.py:83`; `<caso>` de la escaleta `m01a_escaleta.py:1203`; `<caso>` del guionista `guion_v4.py:827`; el SYSTEM del crítico, porque D fila 3 lo pide «como dato para guionista y crítico», DECISIONES l.252 punto 2) | C2 (7 filas M1–M7 + 6 piezas atadas), D filas 2, 3 y 4 | M1–M7: `test_module_f55.py:338, 341-347` (M1–M6) y `test_module_f54.py:65-71` (M7) (C2). `test_module_f6b.py:74` mira el chequeo de código del «respiro», no el texto, y sigue pasando. Paquete: los 8 tests que nombran `m09_packaging` (grep 3) más `test_module_f17.py` (md5 del `<caso>`) y `test_module_f15.py` (fila `guion_v4.py:827`) | M1–M7: 2 (`f55`, `f54`), que **hay que re-anclar** contra el `.md` nuevo. Paquete: `test_module_f58.py::test_a2_pedido_byte_identico_al_handoff`, `test_module_f17.py` (md5) y `tests/test_m01f_compuerta.py` (md5) | M1–M7: **medio**. Ningún código lee el texto (C2, greps 1-4), pero el español **cambia a propósito**: el modelo puede dejar de dar `flash_forward`, un cap 2 `planteo`/1 y un `respiro`, y eso mueve voz, música, arco visual y golpes de TTS (C2, «Para C2» a-c). Paquete: **alto**. Hoy el paquete corre en `fase3`, después del video, y se arma con la narración: `gancho()` es el cap 1 y `CAPS_PAQUETES = range(2, 8)` son los caps 2 a 7 (C1.c, fila `m09_packaging.py:134, 203`). Antes de la escaleta no hay narración: hace falta otra entrada (ficha o pool), un paso nuevo con costo de API y mover el módulo de fase (grep 3) | nada técnico; es la decisión de Omar en DECISIONES l.254 (2) y (3). La despedida de 5–15 s (l.254 (4), D fila 4) está «pendiente de Omar» y no entra hasta que la decida. Va **antes** del bloque 2 |

Greps de esta sección (árbol de trabajo, `c0cce6a`):

1. Tests que nombran un parámetro de duración de B:
```
$ timeout 60 git grep -l -E "video_length|CAP_WORDS|char_band|len_range|_calculate_image_count|MAX_IMAGES_FLUX|max_images_per_video|MAX_BEATS_POR_CAP|min_beats|max_beats|LEN_TOL|WORDS_TOL|SECONDS_PER_IMAGE_TARGET|timeout_sec|GOLPE_MAX_PER_CAP|MAX_SILENCIOS|PALABRAS_POR_SEG|SEG_POR_PALABRA_RESPALDO|LECTURA_CPS|max_per_cap" -- 'test_*.py' 'tests/' | wc -l
29
$ timeout 60 git grep -n -E "import video_length|video_length\.(get|DEFAULTS)" -- 'test_*.py' 'tests/'
test_module_f25c.py:15:from script_engine import video_length as vl
test_module_f7.py:513:    from script_engine import video_length as vl
test_module_f7d.py:60:    from script_engine import video_length as vl
```

2. Cruce de los candados de A con un grep propio. El grep de md5 sale más ancho, porque también agarra md5 de archivos y de datos, no solo de prompts. Y dos candados de A no salen en ninguno de los dos greps: `f55` y `f54` comparan contra el `.md` de lab armando la ruta por partes (C2):
```
$ timeout 60 git grep -l -E "md5|hexdigest" -- 'test_*.py' 'tests/' | wc -l
46
$ timeout 60 git grep -l -E "lab/hyperframes/f[0-9a-z_]+/(PROMPT|SYSTEM|EJEMPLOS)|byte_identico|byte a byte|letra por letra" -- 'test_*.py' 'tests/'
test_module_f13.py test_module_f15.py test_module_f15b.py test_module_f16.py test_module_f17.py test_module_f22.py test_module_f38e_e.py test_module_f44.py test_module_f51a.py test_module_f53b_video_prompt.py test_module_f58.py test_module_f58_a3.py test_module_f59_a1.py test_module_fase2b_only_cap.py
```
Los 16 de la tabla salen de las filas de A. Este grep los confirma en parte (`f17`, `f22`, `f38e_e`, `f58`). Los demás (`f21`, `f23`, `f37a`, `f38c`, `f38e_c`, `f40`, `f64`, `f66`, `test_m01f_compuerta`) están en la lista de md5, salvo `f57`, que compara letra por letra contra una copia del texto escrita en el propio test y no sale en ninguno de los dos greps.

3. Dónde corre hoy el paquete:
```
$ timeout 60 git grep -n -E "m09_packaging|PEDIDO_PAQUETES|paquetes\(" -- '*.py' ':(exclude)lab' ':(exclude)_archived' ':(exclude)output' ':(exclude)data' ':(exclude)test_*.py' ':(exclude)tests' | grep -v "^script_engine/m09_packaging.py"
fase3.py:25:from script_engine import m09_packaging as m09
fase3.py:64:    return ["-m", "script_engine.m09_packaging", topic_id, "--video-path", video_path, *passthrough]
qa_studio_server.py:1872:#  Patrón ENSAMBLAR: subprocess, NO import (m09_packaging arrastra config/gemini/cost_tracker
qa_studio_server.py:1926:            [sys.executable, "-m", "script_engine.m09_packaging", TOPIC_ID,
run_pipeline.py:490:    from script_engine import m09_packaging as m09
script_engine/m09_review_server.py:12:Las funciones de m09_packaging se llaman vía el módulo (monkeypatcheables en tests).
script_engine/m09_review_server.py:24:from script_engine import m09_packaging as pkg
$ timeout 60 git grep -l -E "m09_packaging|PEDIDO_PAQUETES" -- 'test_*.py' 'tests/'
test_fase3.py test_m09_packaging.py test_m09_review_server.py test_module_135_thumbs.py test_module_137d_meta_hero.py test_module_f58.py test_module_f73.py test_module_gfx_auto_icons.py
```

Archivos de duración nombrados en B.9: `m01d_particion.py`, `m01a_escaleta.py`, `video_length.py`, `m01a_skeleton.py`, `m03_visual.py`, `parallax_animator_v2.py`, `gfx_config.py`, `gfx_layer.py`, `fase2b.py`, `m01b_guionista.py`, `guion_v4.py`, `gfx_profiles/misterio.json`, `tts_tags.py`, `music_intensity.py`, `audio_manager.py`, `research_v3.py`, `pool_gate.py`, `config.py` (18). Para que el largo «suba por config» (DECISIONES l.254 (1)) alcanza con `video_length.py`, que ya resuelve las 23 claves (B.1): de ahí siguen solos `CAP_WORDS` (B.3), `char_band` → `len_range` (B.3) y el tope de fotos por cap (B.4, `cap_max` sale de `max_images_per_video`). Lo que no sigue solo son los literales de B.4 a B.8 (`MAX_IMAGES_FLUX` 18, `MAX_FLUX_EXTRAS` 14, los timeouts, los topes por cap) y el «de 7 a 14 beats» escrito en el prompt.

### E.2 Las 52 llamadas de producción del bloque 2 (cuenta hecha sobre las filas de A)

Una «llamada» es un tipo de pedido a un modelo: su system más su texto de tarea, con los reintentos del mismo pedido. Las filas de A que son pedazos del mismo pedido se agrupan (p. ej. `m01a_escaleta.py:878, 951, 1135, 1179, 1196, 1202, 1203, 133, 265` forman una sola llamada: la escaleta). **Con candado** = algún test la fija byte a byte o por md5 (columna «tests» de A).

| fase | llamadas | con candado |
|---|---|---|
| Fase 1, guion (A-1) | escaleta · guionista · reparación (`PEDIDO_E`/`edit_sentences`) · títulos (`PEDIDO_TITULOS`) · `regenerate_cap_v3` · `editor_shorten` · rotulista (`PANTALLA_SYSTEM` + formatos) · sugerir de QA (`SUGERIR_USER`) · `pantalla_verificador` · crítico m01f · `narracion_verificador` · `dicho_verificador` = **12** | escaleta (`f55`, `f22`, `f17`), guionista (`f54`), títulos (`f38e_e`), rotulista (`f38e_c`, `f37a`, `f38c`, `f40`), `pantalla_verificador` (`f64`), crítico (`test_m01f_compuerta`), `narracion_verificador` (`f66`) = **7** |
| Fase 1, research (A-1) | ficha (`SYSTEM_F23_1`) · R1 discovery · R1 alt (Flash) · `annotate_unmatched` · `build_pista_prompt` · R2 `refine_fichas` · R3 extracción · `seed_vocabulario` · `seed_profile` · 4a · 4c · 4d · 4e (`TEXTO_S5`) = **13** | ficha (`f23`) = **1** |
| Voz, fotos, gfx (A-2) | normalizador LLM (`m02_5`) · prompts de foto m03 (SI v2, PERSONAS, bloque del tema, reintentos) · `m03_imagenes_v3` COMPOSITION_RULES · `foto_madre.PROMPT_RASGOS` · `foto_madre.PROMPT_ESTADOS` · `video_prompt.PEDIDO_CON_FINAL` · `video_prompt.PEDIDO_FINAL` · `flow_director` · `zoom_judge` · `vision_validator` · `auto_icons` · `gfx_critic` (ROT) · `gfx_vision` · `gfx_intensity` · director musical (`m07` `_MATCHER_SYSTEM_INSTRUCTION`) = **15** | `PEDIDO_CON_FINAL` y `PEDIDO_FINAL` (`f57`) = **2** |
| Tema y publicación (A-3) | `subtopic_es_relevance` ×2 · `niche_discoverer` ×3 (371, 559, 1150) · `subtopic_classifier` · `subtopic_extractor` ×2 (`SEGMENT_SYSTEM`, `_VERIFY_SYSTEM`) · `m_judge_seeds` · `topic_validator._HUMAN_OPTIONS_PROMPT` · `PEDIDO_PAQUETES` · `_NARRFIX_INSTRUCTION` de QA Studio = **12** | `PEDIDO_PAQUETES` (`f58`) = **1** |
| **total** | **52** | **11** |

Legado o flag (filas de A marcadas «legado», «flag» o «sin llamadas»): la columna, con `TAREA_COLUMNA` (flag `--columna`), y `SYSTEM_F17_1`; los guionistas `SYSTEM_V5`, `V5_1`…`V5_4` y `system_f11c` con `EJEMPLOS_VOZ` (6); `m01c_editor` (flag `--editor`); `cut_phrases`; ficha `SYSTEM_F22_1` y `SYSTEM_F15_1`; `verify_quotes`; `topic_researcher` ×2; `m07_music_director.plan_composicion` (sin llamador en producción). Son **16**: no hace falta su hermano inglés mientras el canal inglés no use esos caminos. Tienen candados propios (`f21`, `f22`, `f23`, `f15`, `f15b`, `f25c`, `f11c`), que no se tocan.

Nota: 4 de las 15 llamadas de A-2 ya están escritas en inglés y solo nombran el idioma: los prompts de foto de m03 (`m03_visual.py:189, 212`, «IN SPANISH»), `m03_imagenes_v3` (`:486`) y los dos pedidos de `video_prompt` (`:54, 67`, «(Spanish)»). Ahí alcanza con poner el nombre del idioma como dato, no hace falta un prompt hermano entero.

### E.3 Orden propuesto de tandas

No es una decisión: es una propuesta para el analista y Omar. La regla es la misma en todas, salvo T4 y T5: **la tanda termina con el español igual que hoy, comprobado, antes de sumar nada en inglés.** Todo en la rama aparte (DECISIONES l.254; D fila 5).

**T0 — Foto del español de hoy (US$ 0, sin código de producción).** Un script de lab guarda:
- (a) el md5 de cada una de las 52 llamadas, con el prompt ya armado sobre la entrada guardada de Wittenoom y de Colza (el system y el texto de tarea, no solo la constante). El hook `.claude/hooks/md5_prompt.py` ya avisa del md5 al editar `SYSTEM_V2` o `## SISTEMA` (C2), pero no cubre las 52.
- (b) la salida de las funciones deterministas del bloque 3 (`evidence`, `num_es`, `guion_v3_reglas`, `tts_normalizer.normalize_for_tts`, `tts_tags.tag_cap`, `voz_datos`, `nombres`) sobre la narración y el pool guardados de los dos temas.
- (c) el `--plan-only` de Wittenoom: 777,766 s, offsets y los 7 inicios de voz (`lab/ESTADO_SESION.md` l.5, F79).
- (d) el número de la suite: 1585 + 3 heredadas, mapa 0 (commit `c0cce6a`).

Ojo con (c): el `--plan-only` llama al crítico de gfx (F79: 22 llamadas, US$ 0,0035), y su veredicto cambió AVISO ch03 y CALMA ch04 sin que cambiara el código. Hay que comparar solo lo determinista (duración, offsets, inicios de voz, eventos que no pasan por el crítico) o correrlo con el veredicto en caché.

**T1 — Perfil por canal (bloque 1).** Un perfil `es` que devuelve los literales de hoy, y las 98 filas leen de él. No se toca ningún prompt. Se verifica con T0 (a), (b) y (c) idénticos, la suite igual (los 51 tests del bloque, con los de contrato `f9`, `f77a`, `f74`, `f34`, `f37b`, siguen verdes sin editarlos) y el mapa en 0.

**T2 — Carpetas por canal (bloque 5).** La raíz del canal `es` = `data/` y `output/` de hoy. Se separan los 18 archivos únicos de la tabla y se arreglan las 3 rutas armadas a mano de QA Studio. Se verifica así: las mismas rutas absolutas para Wittenoom y Colza (un listado de qué archivo lee y escribe cada etapa, antes y después); `run_pipeline` deduce las mismas etapas del disco (`test_run_pipeline.py`); T0 (c) igual; y ningún test escribe fuera de tmp (excluir los de la memoria del proyecto).

**T3 — Duración por perfil (bloque 4), solo la costura.** `video_length.get` lee del perfil; el perfil `es` = las 23 claves de B.1 con los valores de `config.long_video` de hoy. Se verifica así: una tabla con `video_length.get(k)` para las 23 claves, `char_band` de los 3 roles y `_calculate_image_count` de los 7 caps de Wittenoom, antes y después, idéntica; los 29 tests del grep 1 verdes sin editar; T0 (c) igual. Los valores del inglés y los topes de B.9 (timeouts, `MAX_IMAGES_FLUX`, topes por cap) no entran: necesitan números de DECISIONES y una medición de un cap largo.

**T4 — Estructura: quitar M1–M7 (bloque 6, primera mitad).** Es la única tanda que **cambia el español a propósito** (aprobado en DECISIONES l.254 (2)). Por eso va **antes** de los prompts ingleses: así se traduce una sola vez la versión sin molde. Se verifica así:
- en T0 (a) cambian solo los md5 de la escaleta y del guionista; las otras 50 llamadas quedan iguales;
- `test_module_f55.py:338/341-347` y `test_module_f54.py:65-71` se re-anclan contra los `.md` nuevos de lab (no se borran);
- T0 (b) y (c) quedan iguales, porque `--plan-only` no corre la escaleta;
- una corrida real en español de escaleta + guion sobre un tema (con costo de API), para que Omar y el analista la lean, mirando los efectos indirectos de C2: `flash_forward` del beat 1, `funcion`/`intensidad` del cap 2, si hay `respiro`.

**T5 — Paquete antes de la escaleta (bloque 6, segunda mitad).** También cambia el español a propósito (DECISIONES l.254 (3)). Riesgo alto: el paquete hoy se arma con la narración, en `fase3`. Se verifica así:
- en T0 (a) cambian solo las llamadas que reciben el paquete (escaleta, guionista, crítico, y `PEDIDO_PAQUETES` si se reusa);
- `test_module_f58.py`, `f17` y `test_m01f_compuerta` se re-anclan;
- el `fase3` de hoy sigue armando el paquete final igual para un tema ya producido (`test_fase3.py`, `test_m09_packaging.py`);
- una corrida real en español, como en T4.

La despedida (l.254 (4)) espera a Omar.

**T6 — Lógica por idioma (bloque 3).** Rama inglesa al lado de cada detector; la española no se edita. Entran D fila 6 (cifras con coma o punto) y D fila 7 (iniciales). Se verifica así: T0 (b) idéntico en español, T0 (c) igual y los 56 tests del bloque verdes sin editar. Para el inglés, tests nuevos con frases inglesas, con el foco en que un «no dicho» falso avise en vez de callarse (A-1, «Lo que pesa más» 2). El gate de temas (A-3.1) queda fuera hasta que Omar decida cómo se elige el tema del canal inglés (l.252 punto 1).

**T7 — Prompts en inglés (bloque 2).** Prompts hermanos para las 38 llamadas que se traducen (las 52 menos las 10 del gate de A-3.1 y menos las 4 que ya están en inglés), y el nombre del idioma como dato en esas 4. El perfil elige el hermano. Se verifica así: T0 (a) idéntico en las 52 (contra la foto que dejaron T4 y T5), los 16 candados verdes sin editar y T0 (b) y (c) iguales. El inglés lo revisan el analista y Omar, prompt por prompt.

**T8 — Primer video en inglés.** Lleva los valores ingleses de duración (de DECISIONES), la voz inglesa medida (T1, riesgo medio) y los arreglos de D que pegan en el primer tema nuevo: el grounding de R1 (fila 8), foto madre y m03 en la misma corrida (fila 9), el nombre real en la foto (fila 10) y el render pos-F79 sin probar (fila 11). Este último conviene probarlo antes con un render español, con `ver-render`, para no estrenar dos cosas a la vez.

**Lo que este orden no resuelve:** el T0 (a) no existe todavía; hay que escribirlo. Y `config.py` no está en git (A-3 y B, encabezados): todo cambio que viva ahí no deja diff para el revisor. Conviene que T1 y T3 lleven los valores al perfil versionado y no a `config.py`.

Cifras recontadas sobre A final (457 filas) después de la Etapa 2.

## F. Costo real por etapa

Topics: Wittenoom `123bbb64-9fca-4395-8bf4-57d60e219ef1` (W) · Colza `c4934b7d-3f54-448f-ba5f-539dc744f0d8` (C). Solo lectura, US$ 0, sin extrapolar a otro largo.

**Archivos de costo usados**
1. `data/cost_history.json`: lista de 800 registros, filtrada por `video_id`. Abierta con `errors="replace"` porque hay bytes que no son UTF-8 (sale `t�tulos`). W: 52 registros (índices 651–799), suma **US$ 46,9084**. C: 17 registros (776–796), suma **US$ 19,5628**. En la tabla, «ch#N» es el índice del registro en esa lista.
2. `data/scripts/_steps/123bbb64-…/01_v3_costos.json` (35 corridas) y `data/scripts/_steps/c4934b7d-…/01_v3_costos.json` (14 corridas más `tiempos_research`; el `01_v3_tiempos.json` de C trae la misma parte de tiempos).
3. `output/<tid>/assets/assets_manifest.json`: `usd` por foto y `clip_usd` por clip. Solo los tiene lo que generó la última pasada; lo que se saltó (`skipped_exists`) no trae costo. Para W además está `output/123bbb64-…/_archivo_seedream5lite/assets_manifest.json` (fotos originales del 31-oct, sin `usd`).
4. `output/audio/<tid>/ch0N.meta.json` (`tts_chars` por cap) y la tarifa `elevenlabs_per_char: 0.00003` de `config.py:159`.
5. Reportes de tanda, citados en cada fila con su línea.

**Lo que ningún archivo de costo registra** (ningún registro de `cost_history` con esas fechas, para ese u otro `video_id`):
- **Voz de los dos topics.** El mp3 de W es del 2026-10-31 23:06 y el de C del 2026-11-04 18:27. El primer registro posterior de W es ch#767 (23:09) y el de C es ch#792 (18:30). La voz corre antes de `start_video`, igual que la foto madre (memoria «Foto madre: costo fuera del bus»). Por eso abajo va un **cálculo** (caracteres × tarifa de config), no un registro.
- **Research de W.** `_perfil.json`, `fuentes_r1.json`, `_r1_cache.json` y `_r3_cache/` son del 2026-10-27 23:32–23:34. El primer registro de W es ch#651, la ficha, a las 23:39. Entre ch#647 y ch#651 no hay nada de research.
- **Fotos y clips originales de los dos topics.** W: Seedream 5.0 Lite, 2026-10-31 23:41, manifest archivado sin `usd`. C: primera `fase2a` del 2026-11-04, entre 18:34 y 19:46. No hay registro `fal` de C antes de ch#793.
- **Foto madre original.** W: 9 madres de persona del 2026-10-31 23:15 y `subject.png` del 2026-10-28, en `output/123bbb64-…/foto_madre/`. C: `.prompt` del 2026-11-04 18:34; lo que hay ahora se rehízo en F78a/F78b.

Marcas: **[orig]** = primera corrida de esa etapa en el topic · **[rehacer]** = se volvió a generar en una tanda · **[lab]** = corrida de lab sobre una copia, que no quedó en producción pero sí está en `cost_history` bajo el tid · **[est]** = tarifa estimada de config, no factura (fal no devuelve el costo por API).

| etapa | US$ Wittenoom | US$ Colza | de qué depende | de dónde sale |
|---|---|---|---|---|
| research (perfil, R1–R3, pool) | **sin dato**. Corrió el 2026-10-27 23:32–23:34 (mtimes de `_steps/123bbb64-…/_perfil.json`, `fuentes_r1.json`, `_r3_cache/`). No está en `cost_history` ni en `01_v3_costos.json` | **0,8575** [orig]: Flash 0,2579 + Pro 0,5995 | fijo por video: 4 focos R1 y 7 docs R3 en C, por `tiempos_research` | C: ch#776; `_steps/c4934b7d-…/01_v3_costos.json` paso «research»; `lab/hyperframes/f77/F77_REPORT.md:142` (colza 0,8575) |
| ficha (GPT) | **0,3533** [orig] | **0,3263** [orig] (+ un intento de 0,0 que falló antes de llamar) | fijo por video: 64,5 k tokens en W, 45,3 k en C | W: ch#651 y `01_v3_costos` «ficha». C: ch#782 y `01_v3_costos` «ficha» ×2 |
| canon visual | **0,3909** (última, 2026-10-31 23:09) [rehacer]. Antes: 0,0306 (ch#666, Flash) [orig] · 0,0989 (F50d, solo en `01_v3_costos`) · 0,3415 (ch#682) · 0,3919 (ch#695) [rehacer] · 0,3437 (ch#749, F60) [lab] | **0,322** [orig] | fijo por video (una llamada de Opus, unos 27–32 k tokens) | W: ch#767 y los citados; `01_v3_costos` «canon» ×5; `lab/hyperframes/f60/F60_REPORT.md:876` (0,3437, lab). C: ch#783 |
| escaleta | **1,6392** (2026-10-29 20:21, F55 D) [rehacer]. Antes: 1,8637 (ch#652) [orig] · 1,0835 (ch#718, F54 B.5) [rehacer]. Suma de las 3: 4,5864 | **1,5895** [orig], 2 intentos | fijo por video; los intentos dependen de la validación (2 intentos = el doble) | W: ch#728, ch#652, ch#718; `lab/hyperframes/f55/F55_REPORT.md:627`; `f54/F54_REPORT.md:391`. C: ch#784 |
| guionista v4 | **1,5522** (F55 D) [rehacer]. Antes: 1,2342 [orig] · 1,1541 (F54) [rehacer]. Suma: 3,9405 | **1,5318** [orig] | tokens del guion (hoy 7 caps); unos 35–42 k tokens | W: ch#729, ch#653, ch#719; `f55/F55_REPORT.md:627`. C: ch#785 |
| reparación (editar frase) | **0,0849** (F55) [rehacer]. Antes: 0,0765 [orig] · 0,0518 [rehacer] · 0,2048 (7 ediciones dentro de la verificación F66) [rehacer] | **0,0266** [orig] | nº de frases a reparar (W: 1 a 7 llamadas; C: 1) | W: ch#730, ch#654, ch#720, ch#759; `f66/F66_REPORT.md:58`. C: ch#786 |
| partición (títulos + acortar) | **0,0458** (F56 C) [rehacer]. Antes: 0,0479 [orig] · 0,129 · 0,0235 [rehacer] | **0,0625** [orig] | nº de caps a acortar (Pro) + 1 llamada de títulos (Flash) | W: ch#733; `lab/hyperframes/f56/F56_REPORT.md:75`; ch#655, ch#721, ch#731. C: ch#787 |
| verificador de narración (m01b) | **2,4576** (2026-10-31 19:31, F67 B, 7 llamadas) [rehacer]. Antes: 4,1663 (F66: 12 llamadas, primera pasada + re-verificación) [orig] | **1,4897** [orig], 7 llamadas | nº de caps (1 llamada por cap) + re-verificaciones; tokens de la narración + pool (W 494 k, C 261 k tokens de entrada) | W: ch#762; `lab/hyperframes/f67/F67_REPORT.md:11` (2,4575); ch#759; `f66/F66_REPORT.md:58`. C: ch#788 |
| crítico m01f | **0,7203** (F67 B) [orig] · 0,6775 (ch#764) · 0,69 (ch#765) [rehacer, sin tanda identificada en los reportes]. Suma: 2,0878. Lab crítico del papel F67 D 0,5976 [lab, no está en `cost_history`] | **0,5459** [orig] | fijo por video: 1 llamada con la narración entera (70–109 k tokens) | W: ch#763–765; `f67/F67_REPORT.md:12-13`. C: ch#789 |
| juez m05 (`06_judge_narrative.json`) | **sin dato**. Ningún registro con descripción m05 | **sin dato** | — | busqué en `cost_history` por descripción, en los dos tid |
| papel (m01e pantalla + verificador) | **0,8378** (2026-10-31 22:11, la última en disco) [rehacer]. Antes: 0,6585 [orig] · 0,5103 · 0,6279 · 0,7005 (F56) · 1,3004 (F64) · 1,2309 (F66) · 0,9797 (F66b) [rehacer]. Suma de las 8: 6,846. Simulación F64 0,5036 [lab, no está bajo el tid]; 2 «sugerir» F66 0,65 (`ESTADO_SESION.md:85`) | **0,7765** (2026-11-04 18:20) [rehacer] · 0,653 [orig] | tokens de la narración (88 k) + nº de vueltas del autor (unos 0,40–0,75 por vuelta) + verificador por marca | W: ch#766, ch#656, ch#722, ch#732, ch#735, ch#758, ch#760, ch#761; `f64/F64_REPORT.md:345`; `f66/F66_REPORT.md:174`; `f66/F66b_REPORT.md:3`. C: ch#791, ch#790 |
| m03 (casilleros + movimiento: prompts de foto, Opus + Flash) | **2,4325** (2026-10-31 23:12, la de producción vigente) [rehacer]. Antes: 2,1205 [orig] · 2,332 · 2,2653 [rehacer]. [lab] bajo el tid: 2,5815 + 2,2494 + 1,0826 + 2,2811 (F60) + 2,3101 (F61) = 10,5047 | **2,4202** [orig] | nº de fotos (7–10 llamadas «casilleros» por lote de caps + 3–4 «motion» por clip) | W: ch#768, ch#672, ch#683, ch#698; `01_v3_costos` «m03» ×4; lab: ch#744, 745, 747, 750, 755; `f60/F60_REPORT.md:358,446,683`; `f61/F61_REPORT.md:189`. C: ch#792 |
| aspecto (m03 rehace los casilleros con persona, paso nuevo de F78d) | no corrió en W | **3,2859** (38 casilleros 3,2652 + 2 motion 0,0207) [rehacer: primera vez en C, sobre fotos ya hechas] | nº de fotos con persona documentada (38 en C) | C: ch#795; `01_v3_costos` «aspecto»; `lab/hyperframes/f78d/F78d_REPORT.md:96-98` |
| voz (ElevenLabs `eleven_v4`) | **sin registro**. Cálculo: 10.634 caracteres × 0,00003 = **≈ 0,319** (no es registro) | **sin registro**. Cálculo: 10.827 caracteres × 0,00003 = **≈ 0,325** (no es registro) | caracteres de voz (`tts_chars`). W por cap: 976 · 1244 · 2351 · 1283 · 1715 · 1795 · 1270. C: 903 · 703 · 1929 · 1075 · 1948 · 2192 · 2077 | `output/audio/123bbb64-…/ch01..07.meta.json`; `output/audio/c4934b7d-…/ch01..07.meta.json`; tarifa en `config.py:159`; ningún registro `audio_generator` en `cost_history` para los dos tid |
| foto madre (madres de persona + variantes) | **sin dato** para las 9 madres de persona del 2026-10-31 23:15 (`output/123bbb64-…/foto_madre/`). F68 l.73: «las 10 actuales se reusaron». Lab F60: 8 madres × 0,035 = 0,28 [lab, `f60/F60_REPORT.md:1307`] | original **sin dato** (2026-11-04 18:34). **0,8869** F78a B [rehacer]: rasgos 0,0249 + 7 madres Seedream 4.5 0,28 + 11 NB2 edit 0,462 (5 variantes + 6 fotos de control) + 3 Seedream edit 0,12. **0,5263** F78b B [rehacer]: estados 0,0263 + 10 NB2 0,42 + 2 Seedream 0,08 | nº de personas documentadas (madres, 0,04 cada una) + nº de variantes por tramo de edad o estado (0,042 cada una) + 1–2 llamadas de Opus fijas | C: ch#793, ch#794; `lab/hyperframes/f78a/F78a_REPORT.md:4,106-112`; `f78a/F78b_REPORT.md:6,94`; `lab/hyperframes/f78a/b/costo_etapa_b.json` |
| fotos (cuadros + arranque y final de los clips) | **4,242** [est] [rehacer]: 101 fotos NB2 Lite × 0,042 (F68). Prueba de F68 0,166 + 2 instrucciones de Opus 0,067. Total F68 4,475. Las originales (Seedream 5.0 Lite, 31-oct): **sin dato**. Después: F71b 1 foto 0,0605 [rehacer]; F70 13 fotos ≈ 0,55 [lab], de las que 3 pasaron a producción en F70b (US$ 0). El manifest vigente suma 4,158 (99 ítems × 0,042) | original **sin dato**. **1,678** F78d C [rehacer]: 38 NB2 edit 1,596 + 1 NB2 t2i 0,042 + 1 Seedream 4.5 de respaldo 0,04. El manifest vigente suma 1,552 (37 ítems con `usd`, 2 de ellos respaldo Seedream a 0,04; el resto `skipped_exists`, sin costo). Lab F78c 0,9119 [lab, no está bajo el tid] | nº de fotos × 0,042 [est] (0,04 si cae al respaldo Seedream) | W: `lab/hyperframes/f68/F68_REPORT.md:48-51`; `f71/F71b_REPORT.md:58`; `f70/F70_REPORT.md:61`; `output/123bbb64-…/assets/assets_manifest.json`; tarifa en `config.py:157`. C: ch#796; `f78d/F78d_REPORT.md:114-122`; `output/c4934b7d-…/assets/assets_manifest.json`; `f78c/F78c_REPORT.md:4` |
| clips (2 por video: gancho ch01 y ch07) | originales **sin dato**. **2,5131** F68b [rehacer]: 2 Gemini × 1,20 [est] + 2 Opus 0,1131. **2,1512** F69 [rehacer, ch01]: Kling 4.0 1,8938 + Opus/NB2 0,2574. Manifest vigente: ch01 kling_4 1,8938 · ch07 gemini_omni_flash 1,20. Lab F57 (cap 1, `f57_clip_b`) 1,3409 [lab] | original **sin dato**. **2,40** F78d C [rehacer]: 2 Gemini × 1,20 + Opus 0,1843 (fotos finales y prompts) | nº de clips × 1,20 por clip Gemini de 8 s (tarifa medida en F52) o 1,89 si cae a Kling | W: `lab/hyperframes/f68b/F68b_REPORT.md:23`; `lab/hyperframes/f69/F69_REPORT.md:64-73`; manifest `clip_usd`; `f57/F57_REPORT.md:183`. C: ch#796; `f78d/F78d_REPORT.md:118-120` |
| miniaturas (m09 paquetes + foto) | **0,4468** F73 [rehacer]: Opus paquetes 0,198 + casilleros 0,1228 + 3 NB2 0,126. Antes: **0,3953** F58 B [orig, registrado bajo `video_id` `f58_parte_b`, no bajo el tid] | **sin dato**. `output/c4934b7d-…/` no tiene `publish/` | fijo por video: 3 paquetes = 1–2 Opus + 3 fotos | W: ch#775; `lab/hyperframes/f73/F73_REPORT.md:4,51-57`; `lab/hyperframes/f58/F58_REPORT.md:10,260-262`. C: `ls output/c4934b7d-…` (solo `assets`, `foto_madre`) |
| fondos (fase2b: flow_director + zoom_judge) | **0,0883** F72 (97 escenas) [rehacer]. Antes: 0,0783 (2026-10-28, 94 escenas, video anterior) [orig] | **sin dato**: no corrió (no hay `_fase2b_work` ni mp4 en `output/c4934b7d-…/`) | 1 llamada Flash por video (crece con el nº de escenas) + 0,0001 por juicio de zoom | W: ch#769, ch#657; `lab/hyperframes/f72/F72_REPORT.md:116` |
| gfx / crítico de pantalla (`--plan-only`) | **0,0356** F72 (129 Gemini Vision + 9 `gfx_intensity`) [orig]. **0,0035** F79 (35 llamadas) [rehacer]. F72b y F72d en US$ 0 (caché) | **sin dato**: no hay `GUION_PANTALLA.json` | nº de ventanas gfx que pasan por el crítico (0,0001 cada una) + 1 Flash por cap | W: ch#770, ch#798; `f72/F72_REPORT.md:117`; `lab/hyperframes/f79/F79_REPORT.md:212`; `output/123bbb64-…/GUION_PANTALLA.json` (`costos.gemini_usd`) |
| música (m07) | **sin dato**. Ningún registro de `cost_history` del tid la nombra; hay `output/audio/123bbb64-…/music_map.json` | **sin dato** | — | busqué en `cost_history` por stage y servicio en los dos tid |
| render (fase2b + mezcla) | **0** en F72c y F72e (tracker «Costo total: $0.0000»; es local) | **sin dato**: no hubo render | local, US$ 0 por API | `lab/hyperframes/f72/F72c_REPORT.md:74`; `f72/F72e_REPORT.md:54` |

**Totales de los archivos (sin cálculos)**
- **W:** `cost_history` suma 46,9084. Incluye 10,8484 de lab sobre copias (m03 y canon de F60/F61: ch#744, 745, 747, 749, 750, 755). No incluye: research, voz, foto madre, fotos y clips originales, fotos F68 (4,475 est), clips F68b y F69 (2,5131 + 2,1512) ni miniaturas F58 (0,3953, bajo otro id).
- **C:** `cost_history` suma 19,5628, todo bajo el tid. No incluye voz, foto madre original, fotos y clips originales.
- La mayor parte de lo de W es rehacer: escaleta ×3, guionista ×3, papel ×8, m03 ×4 + 5 de lab, verificador ×2, crítico ×3, fotos ×2, clips ×3. C tiene casi solo corridas originales hasta m03; desde ahí, lo que hay en disco es rehacer de F78a, F78b y F78d.


## Verificación (Etapa 2)

Dos verificadores en paralelo, con contexto limpio: no vieron cómo se hizo el inventario. Los archivos de cada verificador quedaron en el scratchpad de la sesión (no van a git); acá van sus cifras.

- **V1 (filas)**: 6 subagentes, uno por bloque (A-1, A-2, A-3 + la tabla de cobertura, B, C, D). Recibieron solo el reporte y abrieron cada `archivo:línea` de **todas** las filas, no una muestra.
- **V2 (cobertura)**: 2 subagentes, uno para A y otro para B + C1. Cada uno hizo primero su barrido propio sin ver el reporte y lo escribió en disco antes de abrirlo. Después listó lo que el reporte no traía.

### Ronda 1

**V1 — filas**

| Sección | Filas revisadas | Sostienen | No sostienen | De qué eran las fallas |
|---|---|---|---|---|
| A-1 | 197 | 187 | 10 | Columna «tests que lo fijan» o afirmaciones de «sin llamadas». Las 197 líneas citadas caen donde dicen. |
| A-2 | 143 | 137 | 6 | Columna de tests: el test nombrado no toca lo que dice la fila. |
| A-3 + tabla de cobertura | 130 (101 + 29) | 113 | 17 | 11 por la columna de tests, 2 funciones mal nombradas, 1 ruta (`m06_assembler.py` está en `script_engine/`). Cobertura: 4 filas con la columna «dónde» incompleta y 1 `git grep` que no estaba pegado (gfx_guion). |
| B | 135 | 129 | 6 | Encabezados de B.1 (23 claves, no 22) y B.2 (19 campos, no 18); 3 líneas corridas (`max_words` l.1435; `VEO_CLIP_DURATION_SEC` l.919, dos veces); `interrupt_*` está en `script_engine/gfx_review.py` y `interrupt_min_sec` es huérfano. |
| C | 90 | 88 | 2 | M1: el crítico recibe `_para_modelo` en `m01f_critico.py:103`, no en l.84. C1.b: un cap 8 con beats da `KeyError` (`m01a_escaleta.py:612`), no `intent None`. |
| D | 104 | 103 | 1 | Fila 91: `ESTADO_SESION.md` l.25 no dice ese abierto; lo dice solo l.40. |
| **Total** | **799** | **757** | **42** | |

Contratos que V1 midió en esta ronda:
- **#4**: 23 claves en `video_length.DEFAULTS` (contadas por AST) = 23 filas en B.1. Cumple; el número del encabezado estaba mal.
- **#5**: el grep re-corrido da las mismas 23 líneas, en el mismo orden, una fila por línea. Cumple.
- **#6**: las 7 filas están, pero las «nadie» de M1, M2 y M3 no traían su grep pegado. Se corrige.
- **#7**: cuadra en 10 de 11 fuentes; en ESTADO_SESION la fila 91 baja el conteo de 48 a 47.

**V2 — cobertura**

| Parte | Hallazgos propios | Ya estaban | Faltaban en el reporte |
|---|---|---|---|
| A (español) | 125 (de 130 anotados, 5 descartados por él mismo: estaban en inglés) | 106 | 19 |
| B + C1 (duración y el 7) | 93 | 76 | 17 |
| **Total** | **218** | **182** | **36** |

Qué se hizo con cada falla y cada faltante (corregida / quitada / agregada / descartada con motivo): ver la tabla «Correcciones de la ronda 1», abajo.

### Correcciones de la ronda 1

| Bloque | V1 corregidas | V1 quitadas | V2 agregadas | V2 descartadas (en «Descartados») |
|---|---|---|---|---|
| A (A-1, A-2, A-3, cobertura) | 33 | 0 | 12 | 7 |
| B y C | 8 (+2 observaciones de V1: `config.py:236`; eco de M2 en `m01a_columna.py:52/105`) | 0 | 9 | 8 |
| D | 3 (fila 91, más las observaciones de las filas 46 y 64) | 0 | — | 2 (DECISIONES l.217 y l.44) |
| **Total** | **44** | **0** | **21** | **15 + 2** |

Cuenta: de los 36 faltantes de V2, 21 se agregaron y 15 se descartaron (19 → 12 + 7 en A; 17 → 9 + 8 en B y C). Los dos descartes de D salieron de observaciones de V1, no de V2. El detalle, ítem por ítem, va en el anexo «Registro de correcciones».

### Ronda 2

**V1 — filas** (se re-revisaron las filas que la ronda 1 corrigió o agregó, la tabla de cobertura completa y los contratos #4–#7)

| Sección | Filas revisadas | Sostienen | No sostienen | Qué falló |
|---|---|---|---|---|
| A-1 | 11 | 11 | 0 | — |
| A-2 | 19 | 17 | 2 | Columna de tests: `gfx_peak.py:16` (sí la fija `test_module_f5f.py` l.29–30); `m03_visual.py:1878` (`test_qa_studio.py` l.707) |
| A-3 | 14 | 13 | 1 | `qa_studio_server.py:1592`: el prompt sí se arma (l.1712) |
| Tabla de cobertura | 29 | 24 | 5 | No contaba las filas de canal repetidas en A-3.3 (`m01a_escaleta`, `guion_v4`, `ficha_caso`, `m01f`) ni la de `audio_profiles` en A-3.4 |
| B | 16 | 16 | 0 | — |
| C | 15 | 14 | 1 | El «nadie» de M7 no tenía su `git grep` pegado |
| D | 14 | 13 | 1 | Las filas 20 y 26 no citaban ESTADO_SESION l.6 y l.9 (la cuenta de 47 sí cierra) |
| **Total** | **118** | **108** | **10** | baja de 42 a 10 |

Contratos medidos en esta ronda:
- **#4**: 23 claves (AST) = 23 filas, y el encabezado ya dice 23. Cumple.
- **#5**: el grep re-corrido da 23 líneas, iguales a C1.a y en el mismo orden. Cumple.
- **#6**: M1–M6 cumplen; falta el grep del «nadie» de M7.
- **#7**: cuadran 10 de 11 fuentes; en ESTADO_SESION faltan las dos citas de arriba.

**V2 — cobertura** (re-compara el barrido propio de la ronda 1 contra el reporte corregido y sus «Descartados»)

| Parte | Hallazgos propios | Ya estaban | Agregados en r1 | Descartados con motivo | Faltan |
|---|---|---|---|---|---|
| A | 125 | 106 | 12 | 7 | **0** |
| B + C1 | 93 | 74 | 9 | 7 | **3** (`MIN_HUMAN_CAPS` en `m01b_guionista.py:36`; `m05_narrative.py:31-32`; `INTENT_DE_FUNCION` / `audio_profiles.py:118-134` sin fila ni descarte) |
| **Total** | **218** | **180** | **21** | **14** | **3** (baja de 36 a 3) |

En B + C1, «ya estaban» pasa de 76 a 74 y «descartados» de 8 a 7. V2 reclasificó tres ítems: los dos que en la ronda 1 había dado por cubiertos (`MIN_HUMAN_CAPS` de `m01b_guionista`, solo en C2; `m05_narrative.py:31-32`) y un descarte cuyo motivo no se sostiene (la parte de C34 que no está en `music_config`). Los tres son los «faltan».

### Correcciones de la ronda 2

V1: 10 corregidas, 0 quitadas. V2: 1 agregada (`m05_narrative.py:31-32` en B.8) y 2 descartadas con motivo (`MIN_HUMAN_CAPS` de `m01b_guionista.py:36`, que ya está en la fila de C2; `INTENT_DE_FUNCION` / `VOICE_SETTINGS_BY_INTENT*`: son 7 intents, no 7 caps).

### Ronda 3

**V1 — filas** (las que tocó la ronda 2, la tabla de cobertura entera y el recuento de D.2)

| Qué | Revisadas | Sostienen | No sostienen |
|---|---|---|---|
| A-2 / A-3 (`gfx_peak.py:16`, `m03_visual.py:1878`, `qa_studio_server.py:1592`) | 3 | 3 | 0 |
| Tabla de cobertura (las 29 filas; recuento por script: 457 filas en A, y la suma por tipo también da 457) | 29 | 29 | 0 |
| B (fila nueva `m05_narrative.py:31-32`) | 1 | 1 | 0 |
| B y C (descartes de la ronda 2) | 3 | 3 | 0 |
| C (M7, grep 8, re-corrido) | 1 | 1 | 0 |
| D (filas 20 y 26; las 47 de ESTADO_SESION citadas, una por una) | 3 | 3 | 0 |
| **Total** | **40** | **40** | **0** |

**V2 — cobertura**

| Parte | Hallazgos propios | Ya estaban | Agregados | Descartados con motivo | Faltan |
|---|---|---|---|---|---|
| A | 125 | 106 | 12 | 7 | 0 (ronda 2; no cambió nada de A en la ronda 2 que afecte la cobertura) |
| B + C1 | 93 | 74 | 10 | 9 | **0** |

**Fin del lazo**: la ronda 3 salió sin fallas en V1 ni en V2.

### Contrato #1: filas que sostienen, por sección

| Sección | Filas al cierre | Ronda 1 (todas) | Ronda 2 (corregidas y agregadas) | Ronda 3 | Estado final |
|---|---|---|---|---|---|
| A-1 | 198 (197 + 1 agregada) | 197 revisadas · 187 sostienen · 10 corregidas | 11 revisadas · 11 sostienen | — | 198 de 198 sostienen |
| A-2 | 156 (143 + 13 agregadas) | 143 · 137 · 6 corregidas | 19 · 17 · 2 corregidas | 2 · 2 | 156 de 156 |
| A-3 | 103 (101 + 2 agregadas) | 101 · 89 · 12 corregidas | 14 · 13 · 1 corregida | 1 · 1 | 103 de 103 |
| Tabla de cobertura (A) | 29 | 29 · 24 · 5 corregidas | 29 · 24 · 5 corregidas | 29 · 29 | 29 de 29 |
| B | 142 (135 + 6 en r1 + 1 en r2) | 135 · 129 · 6 corregidas | 16 · 16 | 1 · 1 | 142 de 142 |
| C | 93 (90 + 3 agregadas) | 90 · 88 · 2 corregidas | 15 · 14 · 1 corregida | 1 · 1 | 93 de 93 |
| D | 104 | 104 · 103 · 1 corregida | 14 · 13 · 1 corregida | 3 · 3 | 104 de 104 |

Las filas que sostuvieron en la ronda 1 no se volvieron a abrir en las rondas siguientes: ninguna corrección las tocó. El total de A (198 + 156 + 103 = 457) coincide con el recuento por script de la ronda 3.

### Registro de correcciones (ítem por ítem)

V1 corregidas 33 · quitadas 0 · V2 agregadas 12 · descartadas 7

#### Corrección ronda 1 · parte A (A1.md, A2.md, A3.md, Cobertura de _cabeza.md)

Todo se verificó abriendo el repo (rama `f11-guion-v4`) con `sed -n` / `grep -n` / `timeout 60 git grep -n`, sin correr tests ni APIs. Resultado: 16 filas nuevas (A-1 +1, A-2 +13, A-3 +2). Las tablas pasan de 441 a 457 filas: prompt 147 · ejemplo 21 · texto_pantalla 17 · voz 24 · karaoke 9 · logica_idioma 163 · api_idioma 21 · canal 23 · rutas 32. El conteo se hizo con un script sobre la columna «tipo» (`_corr_count.py`).

##### V1 · A1 (V1_A1_r1.md)

- V1-A1-1 · corregida · fila 13 (m01a_escaleta:1203): tests = test_module_f17.py (md5). Se sacó f44: importa solo `ficha_caso` (l.14).
- V1-A1-2 · corregida · fila 25 (BLOQUEANTES_V2): se sacó test_module_f13.py, que importa solo `guion_v4` (l.13) y prueba `g4.bloqueantes`. Se agregó «(vía `bloqueante_de`)».
- V1-A1-3 · corregida · fila 82 (cut_phrases): «sin llamadas en producción; solo lab/hyperframes/f10/f10_quirurgico_ycua.py:97: legado».
- V1-A1-4 · corregida · fila 130 (_SCALE): tests = test_module_f12.py (l.122) y test_module_f15b.py (l.103), vía `unsupported` → `numbers` → `_scaled` (ficha_caso l.489, 463, 413).
- V1-A1-5 · corregida · fila 131 (word_numbers): tests = test_module_f15b.py (l.104, «treinta y cinco presos»).
- V1-A1-6 · corregida · fila 147 (ACCEPT_LANGUAGE): tests = test_module_f23.py (l.317). f24 no lo nombra.
- V1-A1-7 · corregida · fila 161 (_role_*): tests = test_module_f21.py (l.118, `role_problems`).
- V1-A1-8 · corregida · fila 162 (JUDGMENTS): tests = test_module_f7.py (l.556–562, `judgment_problems`).
- V1-A1-9 · corregida · fila 164 (_ANON_VOICE): tests = test_module_f7.py (l.623–625) y test_module_f22.py (l.310–313), vía `antagonist_problems`, que usa `_ANON_VOICE` en la l.397.
- V1-A1-10 · corregida · fila 165 (_PHOTO_ANY): tests = test_module_f21.py (l.138–141, `photo_problems`).

##### V1 · A2 (V1_A2_r1.md)

- V1-A2-1 · corregida · `audio_manager.py:151`: tests «— (test_module_38_timestamps_lab.py es un script de lab que repite el `language="es"` sin importar audio_manager, l.12 y l.139)».
- V1-A2-2 · corregida · `fase2b.py:549`: tests = test_module_38d_forcealign_integration.py. Se anota que 38b trae su propia copia de `_chars_to_syllables` (l.131) y no importa fase2b.
- V1-A2-3 · corregida · `m03_visual.py:189`: tests = test_module_f8b.py (l.162: afirma que v3 ya no lo trae). Se sacó test_lab_v5.py, que solo tiene «Read the narration in Spanish» (l.171).
- V1-A2-4 · corregida · `m03_visual.py:212`: tests «—».
- V1-A2-5 · corregida · `misterio.json:75`: se sacó test_constantes_con_origen.py (lee solo `tokens`, l.70–73). Queda test_module_gfx_lab.py (l.250–256: `gfx_lab_server.context` recorre `active_moods()` → `triggers` / `icon_words`, l.226–234 del server; afirma «candado») y se suma test_module_gfx_emphasis.py (l.20–24: ≥ 25 disparadores en 4 categorías del perfil activo).
- V1-A2-6 · corregida · `gfx_peak.py:16`: tests «— (ningún test llama `lexicon_hits`, que es su único usuario, l.38; gfx_lab_server usa su propia regex)». test_module_gfx_intensity.py importa `gfx_peak`, pero no llama `lexicon_hits` ni `_clean`. test_module_f5f.py usa `gp.pool_ticker` y `sentences`, que no pasan por `_clean`.

##### V1 · A3 y Cobertura (V1_A3_r1.md)

- V1-A3-1 · corregida · `youtube_scanner.py:737`: «`_scrape_viral_english` (def l.712; la llama `search_viral_english`, l.848)». Tests «—»: test_chat50 l.93 y test_chat51 l.100/123 mockean `search_viral_english`.
- V1-A3-2 · corregida · `youtube_scanner.py:1162`: tests «— (test_chat52_already_es.py la nombra solo en el docstring, l.5)».
- V1-A3-3 · corregida · `youtube_scanner.py:492`: tests «— (test_es_saturation_judge.py los usa en vivo y no los fija)».
- V1-A3-4 · corregida · `subtopic_es_relevance.py:86`: «— (test_es_saturation_judge.py lo corre en vivo con Gemini, l.24/46; no lo fija)».
- V1-A3-5 · corregida · `fase1.py:801`: tests «— (test_module_f42b.py l.106 la reemplaza por la identidad)».
- V1-A3-6 · corregida · `niche_discoverer.py:1032`: tests «—». Los dos tests importan solo `subtopic_measurer` (l.39–40 / l.22–23).
- V1-A3-7 · corregida · `qa_studio_server.py:1592`: tests «— (test_qa_studio.py inyecta un `rewrite_fn` falso, `_narr_deps` l.981)».
- V1-A3-8 · corregida · `qa_studio_server.py:1621`: tests «—», por el mismo `rewrite_fn` falso en `test_narrfix_idempotent_dict` (l.1023).
- V1-A3-9 · corregida · `m02_5_normalizer_gate.py:50`: tests «—». `git grep CUSTOM_DICT_PATH` sobre test_*.py y tests/ no da nada.
- V1-A3-10 · corregida · `topics_db.py:20`: tests «—», con el dato de lo que sí se redirige: `topic_researcher.TOPICS_DB_FILE` (f77c l.50, f39_research l.27).
- V1-A3-11 · corregida · `fase1.py:73`: la ruta pasa a `script_engine/m06_assembler.py:19` (en la raíz no existe `m06_assembler.py`). Tests: «test_module_f39_fase1.py (fija la copia de fase1_5, `f15.TOPICS_DB`, l.37; no fase1.py:73)».
- V1-A3-12 · corregida · A-3.4 `audio_manager.py:810`: tests «test_module_f9.py::test_payload_v2_identico_y_v4_con_idioma (fija que el payload pasa el idioma que recibe, l.97–98; no el `or "es"` de la l.810)».
- V1-A3-13 · corregida · Cobertura m09: dónde «A-3.2, A-3.6».
- V1-A3-14 · corregida · Cobertura gate ES de fase1: «7 (+ 4 de `rutas` de fase1 en A-3.6) (+ subtopic_measurer 4, subtopic_es_relevance 3)», dónde «A-3.1, A-3.6».
- V1-A3-15 · corregida · Cobertura niche_discoverer: dónde «A-3.1, A-3.6» (14 + 2, contados por script).
- V1-A3-16 · corregida · Cobertura estante: dónde «A-3.1, A-3.6» (2 + 2).
- V1-A3-17 · corregida · Cobertura gfx_guion: «1 (solo `rutas`; su español es el texto del documento para Omar, que no llega al modelo, a la voz ni a la pantalla; `git grep` en A-2.8)». En A-2.8 se pegaron los tres comandos con su salida: `git grep -c` del español (118), `git grep` de llamadas a modelo (exit=1) y `git grep` de las regex (3 líneas, ninguna con palabras españolas).

Cobertura, además: m03 pasa de 22 a 24 (`m03_visual` 12 → 14), `foto_madre` de 2 a 3, y la línea de tipos se actualiza a 457 filas. En el resumen de `_cabeza.md` no cambia ninguna cifra.

##### V2 (V2_A_r1.md)

- V2-1 · agregada · A-2.7 `gfx_config.py:490` `CHROME_TEMPLATES` («CAPÍTULO {n}», «DETALLE»; consumidor `gfx_literal_lock.py:39`) · texto_pantalla · tests test_module_gfx_config.py l.88, test_module_gfx_lock.py l.29–31.
- V2-2 · descartada · `gfx_literal_lock.py:39`: el español está en la tupla; lo cubre la fila V2-1 (Desc_A.md).
- V2-3 · agregada · A-2.6 `video_prompt.py:54` (`PEDIDO_CON_FINAL`) y `:67` (`PEDIDO_FINAL`), «(Spanish…)» · prompt · test_module_f57.py l.142/151 (2 filas).
- V2-4 · agregada · subsección nueva A-2.7b: `m07_music_director.py:214` (SYSTEM del matcher, en español; corre en `generate_music_map` l.1106/1111) y `:1212` (`plan_composicion` «THE CHANNEL SOUND (Spanish…)», sin llamador en producción) · prompt (2 filas).
- V2-5 · agregada · A-2.6 `flow_director.py:40` `_SYSTEM_PROMPT` (recibe la narración, l.85) · prompt · tests «—».
- V2-6 · agregada · A-2.6 `zoom_judge.py:34` `_SYSTEM` · prompt · tests «—».
- V2-7 · agregada · A-2.6 `vision_validator.py:54` `VISION_SYSTEM_PROMPT` (`reason` «en español», l.73) · prompt · tests «—».
- V2-8 · agregada · A-3.1 `subtopic_classifier.py:22` y `subtopic_extractor.py:32` (+ `_VERIFY_SYSTEM` l.106) · prompt · tests «—» (2 filas).
- V2-9 · agregada · A-2.6 `m03_visual.py:1803` (checklists de reintento, + l.1819) y `:1878` (feedback «TU INTENTO PREVIO FALLÓ», l.1881) · prompt · tests «—» (2 filas).
- V2-10 · descartada · `evidence_pool.py:61` SYSTEM: corre solo con `RESEARCH_V3=0` (topic_researcher l.550-574); ya está en la nota de alcance de A-1 (Desc_A.md).
- V2-11 · agregada · A-2.6 `foto_madre.py:509` `PROMPT_ESTADOS` · prompt · test_module_f78a.py l.477.
- V2-12 · agregada · A-2.7 `gfx_pool.py:122` `EDGE_STOP` · logica_idioma · test_module_f5b.py (vía `pool_clause_options`, l.127).
- V2-13 · agregada · A-1.13 fila 198 `topic_researcher.py:441` `_sanitize_search_keyword` (def l.426; lo llama `_research_seed_deep` l.627) · logica_idioma · tests «—».
- V2-14 · descartada · `topic_researcher.py:152/165/355`: legado (fila 195, camino v2) y `research_testimonios` sin llamador en producción (Desc_A.md).
- V2-15 · agregada · A-2.7 `gfx_intensity.py:64` `build_prompt` (mensaje de usuario, l.67–78) · prompt · test_module_gfx_intensity.py l.54.
- V2-16 · descartada · `m06_classifier.py:116`: desconectado (`fase1_5.py:15-17`); es un reporte para Omar (Desc_A.md).
- V2-17 · descartada · `m05_judge.py:999`: desconectado y es un reporte para Omar (Desc_A.md).
- V2-18 · descartada · `tools/build_gemini_validation_prompt.py:20`: herramienta suelta, nadie la importa (Desc_A.md).
- V2-19 · descartada · `gfx_icons/make_bug.py:111`: herramienta de una sola vez, nadie la importa (Desc_A.md).

##### Conteos que cambiaron

- A1.md: `topic_researcher.py` pasa de 3 a 4 y el total de 197 a 198.
- A2.md: `foto_madre` 2 → 3, `m03_visual` 12 → 14, `gfx_pool` 8 → 9, `gfx_config` 2 → 3, `gfx_intensity` 3 → 4. Entran `video_prompt` 2, `flow_director` 1, `zoom_judge` 1, `vision_validator` 1 y `m07_music_director` (A-2.7b) 2. El total pasa de 143 a 156.
- A3.md: entran `subtopic_classifier` 1 y `subtopic_extractor` 1, y la tabla de módulos suma 103.

##### Visto al pasar (fuera de V1/V2, no se tocó)

- A2.md A-2.10 dice que `config.py:103` está «versionada», pero `_cabeza.md` y A-3 dicen que config.py no está en git (`.gitignore:2`). Hay que elegir una de las dos.
- A2.md A-2.1 `audio_manager.py:810` todavía cita test_module_f9.py sin la salvedad que se le agregó a la misma línea en A-3.4. V1_A2 la dio por buena.

#### Corrección ronda 1 · secciones B y C

V1 corregidas 8 · quitadas 0 · V2 agregadas 9 · descartadas 8

##### V1 · B (V1_B_r1.md)

- V1-B-1 · corregida · encabezado B.1: «22 claves, 22 filas» → «23 claves, 23 filas» (AST de `DEFAULTS` re-corrido: 23)
- V1-B-2 · corregida · encabezado B.2: «18 campos» → «19 campos» (AST de `LongVideoConfig` re-corrido: 19 AnnAssign + 1 método); rango `config.py:182-235` → `182-237` (la clase termina en 237)
- V1-B-3 · corregida · B.1 `max_words`: `guion_v4.metricas` l.1427-1430 → l.1427-1435 (`mg.review` 1427 → `duras_v3` 1433; `largo_txt` 1435)
- V1-B-4 · corregida · B.4 `VEO_CLIP_DURATION_SEC`: `m03_visual.py:915` → `:919`
- V1-B-5 · corregida · B.6 `VEO_CLIP_DURATION_SEC`: `m03_visual.py:915` → `:919`
- V1-B-6 · corregida · B.8 `interrupt_*`: partida en dos filas: `interrupt_max_sec` 18 s (misterio.json:15, default gfx_config.py:189) → `script_engine/gfx_review.py:39`; `interrupt_min_sec` 12 s (misterio.json:14) huérfano (`gfx_config.py:367`, git grep solo da esas dos líneas). B.9 #8: ruta `script_engine/gfx_review.py:39`
- V1-B-obs · corregida (extra, observación) · `config.py:235` → `:236` en la fila del literal `1500 * 6` de B.2 y en B.9 #12

##### V1 · C (V1_C_r1.md)

- V1-C-1 · corregida · M1 río abajo: `m01f_critico.py:84` → `m01f_critico.py:103` (`entrada`, l.94: `e = mp._para_modelo(mp.entrada(...))`); test `:128` se mantiene
- V1-C-2 · corregida · C1.b `tts_tags.py:139-152`: con beats, l.151 → `intent_de_cap` → `DEFAULT_INTENT_BY_CAP[n]` (m01a_escaleta 612) → `KeyError`; sin beats, `.get` → `None`; hoy no se llega (`caps_text` range(1, 8), m01b_guionista.py:81; m01d_particion.py:237). Misma salvedad agregada a la fila `m01a_skeleton.py:43-51`
- V1-C-contrato6 · corregida · M1, M2, M3: agregados al bloque de greps los greps 5, 6 y 7 (comando y salida, re-corridos: 890; 52/105/891; 893), y cada fila los cita («abajo, grep 5/6/7»)
- V1-C-obs · corregida (extra, observación) · M2: eco en `m01a_columna.py` l.51/104 → l.52/105

##### V2 (V2_BC_r1.md)

- V2-1 · agregada · B.6 `fase2b.py:110` `HOOK_DURATION` 1.8 s → `_build_chapter_segment` 1175, `_costura_medida` 2851, `_solo_plan` 3072
- V2-2 · agregada · B.7 `music_config.py:44` `MUSIC_LENGTH_MS` 180 000 → `m07_music_director._call_elevenlabs_music_api` 563; respaldo `_generate_new_track_with_gate` 954
- V2-3 · agregada · B.7 `music_config.py:53` `MUSIC_REQUEST_TIMEOUT_SEC` 180 → m07 568; `generar_con_plan` 1255 (`max(180, 400)`)
- V2-4 · agregada · B.7 `m07_music_director.py:1179, 1239` `PLAN_SECCIONES` (3, 5) y 3000–120 000 ms → `fijar_plan` 1221-1223, 1239-1242
- V2-5 · descartada · `promote_palette_to_library_chat36.py:104` (script viejo de la raíz)
- V2-6 · agregada · B.8 `fase2b.py:2552-2553` `CLIP_WORKERS` 6 / `GFX_PARALELO` 1 → `_build_flux_visual` 923, `_assemble_one_video` 3332
- V2-7 · agregada · B.8 `depth_probe.py:33` `MAX_ZOOMS_PER_CHAPTER` 7 → `rank_promotions` 110-111 → `fase2b._apply_zoom_gate` 2353 (V2 citaba 2345); y en B.9 #8
- V2-8 · descartada · `guion_v3_reglas.py:201` `DATE_MAX_PER_CAP` (muerto: git grep solo da definición y docstring)
- V2-9 · descartada · `m09_packaging.py:73-74` (no depende del largo)
- V2-10 · descartada · `m09_packaging.py:429` (por posición)
- V2-11 · agregada · C1.c `guion_v4.py:174, 266, 354, 440, 527, 614` «cap 6 … cita del cap 7» (producción 266); y en «Para C1» (d) guionista 203/209/266
- V2-12 · agregada · C1.c `m01a_columna.py:80-81, 132-133` «Un cap 5 con un solo hecho. El pico…»
- V2-13 · descartada · `music_config.py:85-123, 205-206, 268-274` (por intent)
- V2-14 · descartada · `fase2b.py` is_first/ultimo/pos (por posición)
- V2-15 · descartada · `gfx_layer.py:458, 665`, `gfx_guion.py:258-265` (por posición)
- V2-16 · descartada · `m03_visual.py:544` (por intent)
- V2-17 · agregada · C1.c `qa_studio.html:12` comentario «cap 7 (veo_position=end)» (texto; mismo criterio que `art_profiles.py:302` en C1.b)

#### Correcciones, sección D, ronda 1

V1 corregidas 3 · quitadas 0 · V2 agregadas 0 · descartadas 2

- V1 fila 91 · corregida · fuente pasa de «l.25 y l.40» a «l.40 (LAB NB-TOL6)»; l.25 (LAB NB-AHORCADO) solo da resultados. D.2: l.25 sale de «Una cada una» (11 → 10, con nota), ESTADO_SESION 48 → 47 en la tabla y en el encabezado de la lista.
- V1 obs. fila 46 · corregida · el «por qué» cita textual l.1039 («Ninguna variante es default: Omar elige → F31b») y que es la única mención de F31b en ESTADO, en vez de afirmar «nunca corrió» como si lo dijera la línea.
- V1 obs. fila 64 · corregida · `tanda` es comando (`.claude/commands/tanda.md`), no skill; se ponen las tres rutas verificadas con ls.
- V1 obs. DECISIONES l.217 · descartada · ver Desc_D.md (fase futura sin marca declarada).
- V1 obs. DECISIONES l.44 · descartada · ver Desc_D.md (cerrado por l.253).
- V1 obs. ESTADO cuenta por criterio D.3 · sin cambio · V1 confirma que no falta fila; D.3 ya explica el criterio.
- V2 · no hay V2 para D.

V1 corregidas 10 · quitadas 0 · V2 agregadas 1 · descartadas 2

#### Corrector ronda 2 (A1, A2, A3, tabla de Cobertura de _cabeza, B, C, D)

Cada línea se abrió en el repo (`f11-guion-v4`, árbol de trabajo). Solo lectura: no se tocó nada del repo.

##### V1_A_r2 (8)

- V1-A-1 · A-2.7 `gfx_peak.py:16` · corregida · tests = `test_module_f5f.py` (l.29–30, vía `clima.peak_word` → `lexicon_hits` (clima.py:144) → `_clean` (gfx_peak.py:38); «flotando.» pasa por `_clean`, el test afirma «cadáveres»; no fija las comillas). Abiertos test_module_f5f.py:27-30, clima.py:140-146, gfx_peak.py:36-39.
- V1-A-2 · A-2.6 `m03_visual.py:1878` · corregida · tests = `test_qa_studio.py::test_fix_core_tres_validaciones_fallidas_no_genera` (l.689; corre el `_call_with_validation_retry` real, l.441; l.707 afirma «RETRY 2/» en el segundo pedido; no fija el texto en español). Abiertos m03_visual.py:1876-1883 y test_qa_studio.py:441, 689-707.
- V1-A-3 · A-3.5 `qa_studio_server.py:1592` · corregida · «el prompt no se arma» → «`rewrite_fn` falso (`_narr_deps` l.981) que recibe el prompt armado en qa_studio_server.py:1712 sin mirarlo; nada lo fija». El «—» queda.
- V1-A-4 · Cobertura `m01a_escaleta` · corregida · 27 → 28 (27 + 1 `canal` de A-3.3, l.879); dónde «A-1.1, A-3.3».
- V1-A-5 · Cobertura `guion_v4` · corregida · 30 → 31 (+ 1 `canal` A-3.3, l.97); dónde «A-1.3, A-3.3».
- V1-A-6 · Cobertura ficha (`ficha_caso`) · corregida · 13 → 14 (+ 1 `canal` A-3.3, l.139); dónde «A-1.10, A-3.3».
- V1-A-7 · Cobertura `m01f` · corregida · 6 → 7 (+ 1 `canal` A-3.3, `m01f_prompts/SYSTEM.txt:1`); dónde «A-1.7, A-3.3».
- V1-A-8 · Cobertura `audio_profiles` · corregida · 6 → 7 (+ 1 `api_idioma` A-3.4, l.19); dónde «A-2.1, A-3.4».

Recuento de toda la tabla con un script sobre la columna `archivo:línea` de A-1 + A-2 + A-3 (`_r2_count.py`, 457 filas): las otras 23 filas cuadran con su nº y su «dónde» (m09 9+1 en A-3.2/A-3.6; fase1 7+4 en A-3.1/A-3.6; niche_discoverer 14+2; estante 2+2; m01e_pantalla 14+3; QA Studio 7+1+1; etc.). Extra de la misma regla: la fila «rotulista» («ver `m01e_pantalla`») pasa de «A-1.6» a «A-1.6, A-2.7», porque el nº que cita suma las dos. Además, a la frase de arriba de la tabla se le agregó el criterio: cada nº cuenta todas las filas del módulo, también las repetidas de A-3.3 y A-3.4.

##### V1_BCD_r2 (2)

- V1-BCD-1 · C2 M7, «nadie lee el texto» · corregida · la fila ahora dice «nadie lee el texto (abajo, grep 8)», y se agregó el grep 8 al bloque de greps, re-corrido hoy (exit 0, las mismas 12 líneas de `guion_v4.py`: 117/121, 205/209, 297/301, 383/387, 470/474, 557/561), todas dentro de las seis `<estructura>` (`V5` 114-124, `V5_4` 294-304, `V5_3` 380-390, `V5_2` 467-477, `V5_1` 554-564, `V5_6` 202-212).
- V1-BCD-2 · D.1 filas 20 y 26 · corregida · fila 20: fuente «`ESTADO_SESION.md` l.6, l.8 y l.9» (l.6 trae «Carmen adulta sin texto nuevo»); fila 26: + «`ESTADO_SESION.md` l.9 («Mercedes madre con marco»)». Comprobado con un script: las 47 asignaciones de la lista de D.2 están citadas en la columna «fuente» de su fila (47 citas) y caen en 42 filas distintas; se agregó esa nota debajo de la lista de ESTADO_SESION en D.2.

##### V2_BC_r2 (3)

- V2-B13 · `m01a_escaleta.py:78` / `m01b_guionista.py:36` `MIN_HUMAN_CAPS` · descartada (Desc_BC.md, ronda 2) · cuenta caps, no depende del largo, y no es el 7; ya está en C2, tabla «Piezas atadas al molde…», fila `MIN_HUMAN_CAPS = 3`, que nombra también la constante de `m01b_guionista.py:36` (leída en :199-200). Lo que dijo V2 («el duplicado no aparece en ninguna sección») no se sostiene: lo nombra esa fila de C2.
- V2-B48 · `m05_narrative.py:31-32` `DENSITY_MIN` / `MAX_DATO_CAPS` · agregada · fila nueva en B.8 (debajo de `m05_narrative.py:40-41`): consumidores `cap_review` l.750-752 (duro) y 811-812 (blanda) vía `m01b_guionista.review` l.153; `video_metrics` l.279, 317; `judge_narration` l.497. La densidad va por 100 palabras: un guion del doble pide el doble de datos y el pool no crece. Sin tests. B.8 no tiene conteo en el encabezado: no cambia ningún total.
- V2-C34 · `m01a_escaleta.py:595-597` `INTENT_DE_FUNCION` y `audio_profiles.py:118-134` (`VOICE_SETTINGS_BY_INTENT` l.116-124, `_V4` l.127-135) · descartada (Desc_BC.md, ronda 2) · son intents, no caps; lo que depende del 7 (`intent_de_cap` 604-607, 610/612) ya está en C1.b.

##### Fuera de mis secciones (no se tocó)

- `_cabeza.md` l.11 (Resumen 6) dice «`video_length.DEFAULTS`, 22 claves»; B.1 y V1 (AST) dicen 23.
- D.1 fila 91: el nombre sigue diciendo «Hojas NB-TOL6 / NB-AHORCADO» (observación de V1, no cambia el veredicto; no se tocó).

## Descartados

Lo que el barrido independiente (V2) o las observaciones de V1 trajeron y no entra a A–D, con el motivo.

### Descartados de la parte A (ronda 1): faltantes de V2 que no entran como fila

Formato: `archivo:línea · qué es · motivo del descarte`. Cada uno se abrió en el repo (rama `f11-guion-v4`).

- `script_engine/gfx_literal_lock.py:39` (docstring en l.6) · el candado literal deja pasar el cromo con `if text in chrome_strings(chapter_number)` · el español está en la tupla de `gfx_config.py:490`, no en este archivo (solo nombra «CAPÍTULO N» / «DETALLE» en el docstring). Ya lo cubre la fila nueva `gfx_config.py:490` de A-2.7, que lo nombra como consumidor.
- `researcher_steps/evidence_pool.py:61` · `SYSTEM` «Sos un investigador documental. Copiás datos de un bloque…» · camino viejo. Solo lo usan `add_block` (l.717) y `extract_evidence_pool` (l.782). A `extract_evidence_pool` lo llama `step_4a_facts.py:131` únicamente con `with_pool=True`, y `topic_researcher.py:571-574` lo hace así solo si `v3_pool is None`, o sea con `RESEARCH_V3=0` (l.550-557). La nota de alcance de A-1 («Camino viejo fuera de producción en `evidence_pool.py`: … `SYSTEM` (61)») ya lo cubre.
- `topic_researcher.py:152` / `:165` / `:355` · `MAGNITUDE_SECTION`, `TESTIMONIOS_SECTION` y `_build_testimonios_prompt` (F6a, «Eres un investigador de documentales…») · legado. Las dos secciones las usa `_build_angle_query_prompt` (l.180-181), que es la fila 195 (camino v2: `_gather_angle_blocks`, l.557, solo con `RESEARCH_V3=0`). `_build_testimonios_prompt` se registra en `research_testimonios` (l.387-390), y `git grep -n research_testimonios` fuera de lab/_archived solo da su def: no se llama en producción.
- `script_engine/m06_classifier.py:116` (l.116-125) · el esquema pide `diagnostico_m06`, `fix_sugerido`, `razon_fp`, `por_que_leve` «in Spanish» y `facts_topic_relevantes (Spanish)` · desconectado de la cadena: `fase1_5.py:15-17` dice «el juez (m05 voting + m06 clasificador/menú) fue DESCONECTADO del chain». `git grep m06_classifier` fuera de lab y tests solo da esos comentarios y `_lab_chat66b_m06_schema.py`. Además, su salida es un reporte para Omar.
- `script_engine/m05_judge.py:999` (y los textos del menú) · «PIEZA 6 — REPORTE GERENCIAL (CASTELLANO NATURAL)» · desconectado igual que m06 (`fase1_5.py:15-17`, `:73`). Es un reporte para Omar. A-1 ya lo deja afuera a propósito (nota final de A-1). Su SYSTEM, `m05_PROMPT_v1.txt`, está en inglés.
- `tools/build_gemini_validation_prompt.py:20` (l.20-27) · `PROMPT` «Sos un analista… canal faceless de YouTube en español… 8-10 min» · herramienta suelta, fuera de la cadena (su docstring, l.2: «READ-ONLY, $0»; se corre a mano, l.10). `git grep` fuera de lab: ningún módulo la importa.
- `script_engine/gfx_icons/make_bug.py:111` · `_ZOOM_SYSTEM` «Mirás UN fotograma de un documental…» · herramienta que hizo una sola vez la mosca del canal. `git grep make_bug` fuera de lab/_archived: ningún módulo la importa.

### Descartes de V2 (secciones B y C) · ronda 1

- promote_palette_to_library_chat36.py:104 · `NOMINAL_DURATION_MS = 60000` («tracks de 60s. fase2b loopea a la duracion del cap») · script viejo de la raíz (chat36), no es producción; el largo real de la paleta ya está en B.7 (`music_config.py:44` y ffprobe de `audio_library/`)
- script_engine/guion_v3_reglas.py:201 · `DATE_MAX_PER_CAP = 1` · código muerto: `timeout 60 git grep -n DATE_MAX_PER_CAP` (con las exclusiones) → solo `guion_v3_reglas.py:201` (la definición) y `:238` (docstring de `date_problems`, que dice que pasó a métrica); ninguna línea lo lee
- script_engine/m09_packaging.py:73-74 · `MAX_TITLE_CHARS = 90`, `MAX_TAGS_CHARS = 450` · topes del paquete de YouTube; no dependen del largo del video
- script_engine/m09_packaging.py:429 · la miniatura sale del cap 1 (`chapter_number == 1`; PARADA si no está) · por posición (el gancho es el primero), no por el número 7: vale con N caps
- music_config.py:85-123, 205-206, 268-274 · prompts y lista de los 7 intents de música · son 7 intents, no 7 caps; mismo criterio que la fila `promote_palette_to_library_chat36.py:180` de C1.c
- fase2b.py:724, 1171, 1717, 2155-2158, 2452, 2851 · `is_first` / `ultimo` / `pos = "hook"/"outro"` · por posición (primero y último cap), no por el 7: ya generalizado
- script_engine/gfx_layer.py:458, 665 · script_engine/gfx_guion.py:258-265 · title card y subida desde negro por `primero=is_first` · por posición, no por el 7
- script_engine/m03_visual.py:544 · brief visual del intent `outro` (`VISUAL_INTENT_BY_INTENT`) · por intent, no por número de cap; la cadena de `narrative_intent` ya está en C2 (M2/M3, `VISUAL_INTENT_BY_INTENT` 537)

### ronda 2

- script_engine/m01a_escaleta.py:78 · script_engine/m01b_guionista.py:36 · `MIN_HUMAN_CAPS = 3` (escaleta: `validate` 368, 386, 392, humano en escena en ≥ 3 caps; guionista: `review` l.199-200, humano por nombre en ≥ 3 caps → `duras_v3`, métrica) · no depende del largo (cuenta caps, no minutos ni palabras: con 7 caps más largos vale igual) y no es el número 7 de C1; su peso contra el número de caps ya está en C2, tabla «Piezas atadas al molde…», fila `MIN_HUMAN_CAPS = 3`, que nombra las dos constantes (`m01a_escaleta.py:78` y la de `m01b_guionista.py:36`, leída en `:199-200`). Ningún test la nombra (`git grep MIN_HUMAN_CAPS` en `test_*.py` y `tests/`: nada)
- script_engine/m01a_escaleta.py:595-597 · `INTENT_DE_FUNCION`: función del beat → `narrative_intent` (9 funciones → 7 intents) · son intents, no caps: el dict no tiene ningún número de cap; lo que sí depende del 7 (`intent_de_cap` 604-607, cap 7 siempre `outro`; `DEFAULT_INTENT_BY_CAP[n]` 610/612) ya está en C1.b. Mismo criterio que el descarte de `music_config.py:85-123` de la ronda 1
- audio_profiles.py:118-134 · `VOICE_SETTINGS_BY_INTENT` (l.116-124; la cita de V2 «118-134» cae dentro de las dos) y `VOICE_SETTINGS_BY_INTENT_V4` (l.127-135): stability/style por intent · son 7 intents, no 7 caps (claves `hook`…`outro`, ningún número de cap); mismo criterio que `music_config.py:85-123`. La l.127 ya está en A-2.1 como fila de voz

### Descartes, sección D (ronda 1)

- DECISIONES.md:217 · Fase 2 del lazo escritor → crítico → corrector («tras 2–3 videos de confianza») · no lleva ninguna de las marcas que cuenta D.2 (el «PENDIENTES» del título es la cabecera, como ya registró V1) y es una fase futura con condición, no un arreglo en espera; agregarla cambiaría el criterio de conteo de DECISIONES.
- DECISIONES.md:44 · «falta decidir qué pasa con la intro de 2.5 s» · sin marca declarada y ya cerrado: DECISIONES l.253 (F79) borra la intro de 2,5 s y dice «l.44 la dejó por decidir».


## Fuera de alcance

Lo que apareció durante el barrido y no es parte del contrato del §4. No se arregló y no abre trabajo nuevo: se deja anotado para el analista.

1. **El grep del handoff no corre tal cual.** `git grep … ':!_archived'` falla con `fatal: Unimplemented pathspec magic '_'` (exit 128). Se usó `':(exclude)_archived'`, que sí funciona. Pero esa exclusión saca solo la carpeta `_archived/` de la raíz. `script_engine/_archived/` sigue entrando al barrido: 10 de las 23 líneas de `EXPECTED_CHAPTER_COUNT` son de `script_engine/_archived/m02_profiles.py`, que nadie importa (ver C1.a).
2. **`config.py` guarda una llave de API escrita en claro** en el archivo del disco (l.103). No está en git (`.gitignore:2`) y no se copió en ningún lado.
3. **`claude/RESUMEN_FILED_AND_IGNORED_2026-11-10.md` no existe**, y tampoco la carpeta `claude/`. La línea de DECISIONES del 2026-11-10 21:44 lo cita como el lugar de las decisiones de canal, idioma, largo y temas. Lo mismo pasa con los tres documentos `claude/*_2026-11-09.md` que cita la línea del 2026-11-09 22:13.
4. **`lab/hyperframes/f78d/a/lista_aspecto.md`** sigue modificado en el árbol de trabajo, aunque la adenda de F78d dice que se restauró. Está entre los archivos que no se commitean.
5. **`gfx_config` todavía no lee DECISIONES** (pendiente de infraestructura, DECISIONES l.110). Va en D como arreglo en espera; acá solo se anota que sigue igual.
6. **El idioma del feed de scrapetube** (`script_engine/youtube_scanner.py`) no se fija en el código. Verificar qué idioma devuelve pide una corrida con red, que esta tanda no hace.
7. **`script_engine/m05_judge.py` y `m05_PROMPT_v1.txt`** (el juez visual de Fase 2, imagen ↔ narración) están desconectados de la cadena (`fase1_5.py:15-17`). El prompt está en inglés. Ver «Descartados».
8. **Scratchpad compartido entre subagentes**: dos agentes del inventario usaron el mismo nombre de script de búsqueda y uno pisó al otro. El agente A-3 cambió a un script propio y avisó que el otro dejaba afuera los archivos que no son `.py`. V2 (cobertura) barrió también `.txt`, `.json`, `.html` y `.tmpl`. Por ejemplo, `script_engine/m01f_prompts/SYSTEM.txt` está en A-1.7 y en C1.

## Veredicto del revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

Contrato: HANDOFF_F80a.md, md5 d46f4750301d83b13a8551db9de5d9c3 (coincide). Entregable: lab/hyperframes/f80a/F80a_REPORT.md (2059 líneas, 297 KB, sin commitear).
Forma §6: los encabezados van en el orden pedido (Resumen, A, B, C, D, E, F, Verificación, Descartados, Fuera de alcance). Falta solo el veredicto del revisor, que se agrega después, como se esperaba.

| # | Requisito del §4 | Estado | Evidencia |
|---|---|---|---|
| 1 | Filas de A–D con archivo:línea que sostiene, tabla de V1 | OK | Reporte l.1727-1735 (R1), 1768-1777 (R2), 1803-1811 (R3), 1824-1832 (final por sección). El lazo cierra: 42 → 10 → 0 fallas. Muestreo mío de 10 líneas (B: m01a_escaleta:65, m03_visual:1037/896-897, gfx_config:47, fase1_5:712-713; C: m01a_escaleta:278/438, m06_assembler:132, tts_tags:153; D: m03_visual:1459) coincide con lo que dice la fila. |
| 2 | A cubre los 9 tipos y los módulos del mínimo; "no tiene español" con grep | OK | l.19-51 (tipos 147+21+17+24+9+163+21+23+32 = 457; tabla módulo → filas). gfx_director, gfx_templates y gfx_guion tienen su `git grep` (l.633-663). m09b con 0 filas tiene su explicación (el módulo no existe). Confirmé que `script_engine/` tiene solo m09_packaging y m09_review_server. |
| 3 | Tabla de V2 | OK | l.1745-1749, 1787-1791, 1815-1818: propios 218, ya estaban, agregados, descartados con motivo, faltan 0 al cierre. Sección "Descartados" en l.2009. |
| 4 | Todas las claves de video_length.DEFAULTS | OK | Conté 23 claves con AST sobre `script_engine/video_length.py`. B.1 trae 23 filas (l.902-928). Ver observación 1. |
| 5 | EXPECTED_CHAPTER_COUNT: grep = filas de C1 | OK | Corrí `timeout 60 git grep -n` con `':(exclude)…'` y dio 23 líneas. Las del reporte (l.1114-1136) son las mismas 23 y la tabla C1.a tiene 23 filas. El reporte documenta que la forma `':!_archived'` falla (l.1102-1107) y aclara que `script_engine/_archived/` queda adentro (10 líneas). |
| 6 | C2 trae M1–M7, 7 filas, cada "nadie" con su grep | OK | l.1257-1263 (7 filas con "quién lee la regla" y "quién lee río abajo"). Greps 1-8 pegados en l.1265-1345, incluido M7 (grep 8). Los candados citados existen: `test_module_f55.py:338` y `test_module_f54.py:65` dicen lo que el reporte afirma. |
| 7 | D: nº de abiertos por fuente = nº de filas | OK (con salvedad) | D.2 (l.1487-1540) cuadra: F79 = 5, F78d = 5, ESTADO = 47, DECISIONES = 26 + 15. Las 104 filas se reparten 11 / 47 / 46. Comprobé que F79 tiene 5 abiertos (F79_REPORT l.220-226). Qué entradas de ESTADO son vigentes es criterio del subagente; D.3 lo explica (l.1542-1552) y no lo puedo certificar. |
| 8 | F sale de archivos reales, con la ruta de cada uno | OK | l.1670-1675. Existen y no están vacíos: `data/cost_history.json` (1,6 MB), los dos `01_v3_costos.json`, los dos `assets_manifest.json` y los `output/audio/<tid>/ch01.meta.json`. Las celdas "sin dato" están marcadas como tales. |
| 9 | Commit de cierre | NO VERIFICABLE | El commit todavía no existe, como avisó Omar. Ver "Fuera de alcance" para el estado del árbol. |

Observaciones DENTRO del contrato (corregir antes de cerrar, son rápidas):
1. Resumen, punto 6 (l.11) dice "`video_length.DEFAULTS`, 22 claves". El archivo y B.1 dicen 23. El propio reporte lo anotó en l.2006 como "fuera de mis secciones, no se tocó". Rompe la coherencia del #4. Lo mismo en E l.1642: "las 22 claves de B.1".
2. E l.1556 todavía dice "A-1: 197 filas, A-2: 143, A-3: 101; total 441". Al cierre son 198 / 156 / 103 = 457 (A l.19 y l.1834). Cifras viejas en E.
3. Verificación: V1 y V2 de las rondas 2 y 3 re-revisaron solo lo corregido o agregado, no el reporte entero (l.1834 lo declara). Se puede defender con el criterio "se vuelve a correr el verificador que falló". Un lector estricto del #1 ("todas las filas") lo ve como parcial. Yo no pude re-abrir las ~800 filas.

Fuera de alcance (archivos tocados en el árbol):
- Modificados previos y esperados: DECISIONES.md, diag_234_cap4.py, lab/hyperframes/f28/a/f28a.log, lab/hyperframes/f58/pedido_paquetes_wittenoom.txt, lab/hyperframes/f78d/a/lista_aspecto.md.
- Nuevos de esta tanda: solo `lab/hyperframes/f80a/` (F80a_REPORT.md; el HANDOFF también está sin trackear).
- Archivos modificados desde las 21:00 de hoy, fuera de `.git/`, `output/` y `data/`: solo DECISIONES.md y los dos de f80a. Los untracked de `lab/hyperframes/f44/` son del 27-28 oct, no de esta tanda.
- `lab/ESTADO_SESION.md` sigue sin tocar (0 diff). La línea del §5.3 todavía falta.
- No encontré tests, código, config ni prompts modificados por esta tanda.
- Dentro del reporte, A-2.10 deja anotado que `config.py:103` tiene una llave de ElevenLabs en claro. `config.py` no está en git. El reporte no la copia. Correctamente fuera de alcance.

Riesgos que el contrato no cubre:
- El archivo `claude/RESUMEN_FILED_AND_IGNORED_2026-11-10.md`, que DECISIONES l.254 cita, no existe en el repo. D se apoya solo en esa línea (el reporte lo dice en l.1367).
- El reporte pesa 297 KB y tiene anexos de corrección (l.1836-2007) con registros internos de subagentes. Antes del commit conviene decidir si esos anexos quedan.

## Adenda de CC

- **Observación 1** (corregida): el resumen, punto 6, ahora dice «23 claves». En E, «22 claves» → 23 y «18 campos» → 19.
- **Observación 2** (corregida): E se recontó sobre el A final (198 / 156 / 103 = 457 filas). Al final de E quedó la nota «Cifras recontadas sobre A final».
- **Observación 3** (declarada, sin cambio): las rondas 2 y 3 re-revisaron solo lo que la ronda anterior corrigió o agregó. La ronda 1 de V1 abrió las 799 filas. Las que sostuvieron en esa ronda no las tocó ninguna corrección, así que no hay motivo para que dejen de sostener. Es el criterio del §3: «se vuelve a correr el verificador que falló».
- **Anexos de corrección**: quedan en el reporte. Son la evidencia de qué se hizo con cada «no sostiene» y con cada faltante (§3: «se corrige o se quita… o se pone en Descartados con el motivo»).
- **Archivos de la tanda**: este reporte y una línea en `lab/ESTADO_SESION.md`. El commit lleva además `HANDOFF_F80a.md` y `DECISIONES.md` (la línea del analista del 2026-11-10 21:44, tal cual), como pide el contrato #9.
- **Tareas en segundo plano**: los subagentes de la tanda terminaron todos (inventario, E, verificadores, correctores, revisor). No quedó ninguna shell propia corriendo. No se cerró ningún proceso de Omar.
