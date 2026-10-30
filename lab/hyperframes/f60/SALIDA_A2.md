# F60 — Salida A2 (quitar la duda del casillero `persona`) — PARADA A2

Pedido del analista (19:35): quitar «or if unsure» de `TEXTO_PERSONA`; probar m03 solo en caps 2-4 sobre la copia de lab con las entradas de la corrida 2 de la Etapa A; control de nombres con la regla nueva (2+ palabras → PARÁ; 1 palabra → revisar). Cero fotos. UNA sola corrida (Opus no es determinista). Runner `lab/hyperframes/f60/etapa_a2_m03.py` → `a2/etapa_a2.json`, `a2/etapa_a2.log`, `a2/03_visual_a2.json` (referencia: `a/03_visual_despues.json`, corrida 2; `a2/03_visual_antes_a2.json` = el 03_visual de la copia antes de correr, igual a la referencia).

**Resultado en una línea:** quitar «or if unsure» no trae a Daniel: en caps 2-4 Daniel pasa de 2 fotos (corrida 2) a **0** en A2, y María entra en el baile y en la pista. La causa está en otra cláusula: **«at the same age and condition the canon describes»** con el canon de Daniel «a young adult Spanish migrant miner in work clothes, **one foot visibly bandaged**» (era 1962-1963). En las 3 corridas de m03 (A corrida 1, A corrida 2, A2), las **10 de 10** fotos donde Opus puso a Daniel muestran el pie vendado o la cojera; en el baile (1961, traje), la boda, el barco y la pista no hay venda → Opus lo excluye por «condition». Control de nombres: 0 PARÁ, 1 «revisar» («Court» = sala del tribunal).

## A2.1 `TEXTO_PERSONA` (script_engine/m03_visual.py), constante entera antes / después

ANTES:

    - persona: a LIST with the exact name, as written in PERSONAS DOCUMENTADAS, of each documented person who is recognisably shown in THIS image (even from behind), at the same age and condition the canon describes — the main one first, at most TWO; [] if none, if only a body part is shown, if they appear inside a photograph or picture within the scene, or if unsure. Routing only — not rendered as text.

DESPUÉS:

    - persona: a LIST with the exact name, as written in PERSONAS DOCUMENTADAS, of each documented person who is recognisably shown in THIS image (even from behind), at the same age and condition the canon describes — the main one first, at most TWO; [] if none, if only a body part is shown, or if they appear inside a photograph or picture within the scene. Routing only — not rendered as text.

Único cambio en la constante: «…, if they appear inside a photograph or picture within the scene, or if unsure.» → «…, or if they appear inside a photograph or picture within the scene.» (verificado en código contra la cadena del pedido; `SYSTEM_INSTRUCTION_CASILLEROS` sin «or if unsure»). Nada más cambió en producción; CRLF intacto. `test_module_f50b` sigue verde (compara el concatenado, no el texto). Sticker de m03_visual con md5 nuevo; MAPA `--check` 0 fallas.

## A2.2 Prueba: m03 caps 2-4 (chapters[1..3]) sobre la copia · 209.3 s · US$ 1.0826 (cost_tracker)

Cómo se limitó a caps 2-4 sin tocar producción: el runner envuelve `ThreadPoolExecutor` de m03 y, para los caps 1, 5, 6 y 7, devuelve el capítulo de la referencia en vez de llamar a Opus; el pase F8 de video corrió como en producción sobre los 7 y **no cambió nada fuera de 2-4** (caps 1, 5, 6, 7 idénticos a la referencia: `{'1': True, '5': True, '6': True, '7': True}`). Número de fotos por cap igual que la referencia: {2: {'referencia': 16, 'a2': 16}, 3: {'referencia': 16, 'a2': 16}, 4: {'referencia': 14, 'a2': 14}}.

**Emparejamiento por ancla:** m03 vuelve a elegir anclas (Gemini, paso 1) y esta vez las cortó distinto: solo **8/16, 8/16 y 8/14** fotos tienen la misma ancla que la referencia; las demás (22 de A2 y 22 de la referencia) van aparte y no cuentan como cambio.

### a) Escenas donde faltó Daniel en la corrida 2 (buscadas por fragmento de ancla; `persona` corrida 2 → A2)

| escena | referencia (corrida 2) | A2 | lectura |
|---|---|---|---|
| baile («Dieciséis de septiembre») | `chapters[1].img[0]` → `[]` | `chapters[1].img[0]` → `['María Bernal']` | Daniel sigue faltando; ahora entra María (la pareja se conoce: los dos). |
| boda («se casan») | `chapters[1].img[1]` → `['María Bernal']` | `chapters[1].img[1]` → `['María Bernal']` | igual: María sola; «se casan» son los dos. |
| barco («van juntos») | `chapters[1].img[3]` → `['María Bernal']` | `chapters[1].img[2]` → `[]` | peor: la ancla se fusionó («Van a Australia… van juntos») y `persona` quedó vacía. |
| mi marido («mi marido») | `chapters[1].img[4]` → `['María Bernal']` | `chapters[1].img[3]` → `['María Bernal']` | igual: María sola. |
| dos parejas («amigos íntimos de otra pareja») | `chapters[1].img[5]` → `['Milagros Barroso', 'Ramón de Juan']` | `chapters[1].img[4]` → `['Milagros Barroso', 'Ramón de Juan']` | igual: Milagros y Ramón; faltan Daniel y María. |
| pista («los Écija bajaban») | `chapters[2].img[15]` → `[]` | `chapters[2].img[15]` → `['María Bernal']` | Daniel sigue faltando; ahora entra María («los Écija bajaban»). |
| mina (Daniel trabajaba) («Daniel trabajaba en la mina») | `chapters[3].img[8]` → `['Ramón de Juan']` | `chapters[3].img[8]` → `['Ramón de Juan']` | igual: Ramón solo. |
| mina (primer día) («primer día de trabajo de su padre») | `chapters[3].img[9]` → `[]` | `chapters[3].img[9]` → `[]` | igual: vacío. |

Daniel: **0 de 8 escenas** en A2 (0 de 8 en la corrida 2). Lo que cambió es María: entra en el baile y en la pista. Nota: en la corrida 2, las dos únicas fotos de caps 2-4 con Daniel eran `chapters[3].img[12]` («Le pusieron Daniel, como el padre… foto del bautizo», hombre «with one foot bandaged») y `chapters[3].img[13]` («Se fueron…», «a slim man with a limp»); en A2 esas anclas se cortaron distinto (sin par) y sus fotos quedaron en `[]` y `['María Bernal']`: Daniel también salió de ahí.

### b) Falsos positivos (fotos de caps 2-4 con Daniel en `persona` cuya ancla no lo involucra)

**Ninguno: A2 no tiene ninguna foto de caps 2-4 con Daniel en `persona`** (0). Todas las fotos con `persona` no vacía en caps 2-4 (A2):

| foto | `persona` | ancla |
|---|---|---|
| `chapters[1].img[0]` | `['María Bernal']` | Dieciséis de septiembre de mil novecientos sesenta y uno. En el salón de baile del Círculo de Bellas… |
| `chapters[1].img[1]` | `['María Bernal']` | Un año después se casan: el jueves veinte de septiembre de mil novecientos sesenta y dos. Cuatro día… |
| `chapters[1].img[3]` | `['María Bernal']` | «Iba pegadita a mi marido, como una niña», recuerda su mujer. |
| `chapters[1].img[4]` | `['Milagros Barroso', 'Ramón de Juan']` | Con el tiempo se hicieron amigos íntimos de otra pareja, Milagros Barroso y Ramón de Juan. |
| `chapters[1].img[6]` | `['Víctor Calvo']` | Un niño que hizo ese viaje todavía recuerda el calor. |
| `chapters[1].img[7]` | `['Víctor Calvo', 'Milagros Barroso']` | Víctor Calvo era un niño cuando subió a ese barco. |
| `chapters[1].img[10]` | `['Víctor Calvo', 'Milagros Barroso']` | Recuerda los mareos. Y la incertidumbre: no saber muy bien adónde iban ni cómo iban a vivir. |
| `chapters[1].img[13]` | `['Víctor Calvo', 'Milagros Barroso']` | Ese niño cuenta que nunca había visto tanto polvo. Los llevan a las casas: chapa, madera y uralita. |
| `chapters[2].img[3]` | `['Eric Saint']` | Mil novecientos cuarenta y ocho. Un médico llega en avión y escribe una carta a máquina: los niveles… |
| `chapters[2].img[5]` | `['Eric Saint']` | y que convendría examinar algunos de esos tórax. Se llama Eric Saint. |
| `chapters[2].img[6]` | `['Eric Saint']` | Lo que pasó con la carta lo contó él mismo: «Me desestimaron y, de hecho, me tildaron de alborotador… |
| `chapters[2].img[15]` | `['María Bernal']` | «porque estaban acostumbrados; lo esperaban», dijo McNulty. En mil novecientos sesenta y uno la prod… |
| `chapters[3].img[1]` | `['Víctor Calvo']` | Víctor Calvo lo cuenta: «Nosotros jugábamos con él y lo íbamos deshilachando. Nos lo metíamos en la … |
| `chapters[3].img[8]` | `['Ramón de Juan']` | Daniel trabajaba en la mina. Ramón de Juan, el amigo, hacía jornadas de dieciséis horas. |
| `chapters[3].img[10]` | `['Milagros Barroso', 'John Patrick']` | En marzo de mil novecientos sesenta y tres, Milagros Barroso dio a luz en Wittenoom a John Patrick. |
| `chapters[3].img[11]` | `['María Bernal']` | Tres meses después le tocó a María. Llegó al hospital de Wittenoom debilitada por una infección rena… |
| `chapters[3].img[13]` | `['María Bernal']` | Se fueron antes de que nadie les dijera nada. Nadie les había dicho nada. |

Las 17 son coherentes con su ancla (la persona nombrada o «ese niño» = Víctor Calvo, «su mujer» = María). Ninguna trae a Daniel.

### c) Fotos que cambiaron `persona` respecto de la corrida 2 (solo pares por ancla)

| cap | pares por ancla | cambios |
|---|---|---|
| 2 | 8 de 16 | 2 |
| 3 | 8 de 16 | 0 |
| 4 | 8 de 14 | 0 |

| cap | par | corrida 2 | A2 | ancla |
|---|---|---|---|---|
| cap 2 | `chapters[1].img[0]` → `img[0]` | `[]` | `['María Bernal']` | Dieciséis de septiembre de mil novecientos sesenta y uno. En el salón de baile del Círculo de Bellas Artes de … |
| cap 2 | `chapters[1].img[6]` → `img[5]` | `['Milagros Barroso', 'Víctor Calvo']` | `[]` | Esa familia madrileña había hecho el mismo viaje un mes antes. |

Anclas sin par (no cuentan como cambio; una corrida, Opus/Gemini no deterministas):

| cap | lado | `persona` | ancla |
|---|---|---|---|
| cap 2 | A2 `img[1]` | `['María Bernal']` | Un año después se casan: el jueves veinte de septiembre de mil novecientos sesenta y dos. Cuatro días más tarde ya están… |
| cap 2 | A2 `img[2]` | `[]` | Van a Australia con el acuerdo migratorio por el que pasaron cerca de ocho mil españoles. De Wittenoom no saben nada; sa… |
| cap 2 | A2 `img[6]` | `['Víctor Calvo']` | Un niño que hizo ese viaje todavía recuerda el calor. |
| cap 2 | A2 `img[7]` | `['Víctor Calvo', 'Milagros Barroso']` | Víctor Calvo era un niño cuando subió a ese barco. |
| cap 2 | A2 `img[12]` | `[]` | Aterriza en una pista en medio de una tierra muy roja, en el desierto de Pilbara, en Australia Occidental. Hay polvo por… |
| cap 2 | A2 `img[13]` | `['Víctor Calvo', 'Milagros Barroso']` | Ese niño cuenta que nunca había visto tanto polvo. Los llevan a las casas: chapa, madera y uralita. |
| cap 2 | A2 `img[14]` | `[]` | De esa tierra sacan crocidolita, el asbesto azul, un mineral que se paga bien porque aguanta el calor y no se gasta. |
| cap 2 | A2 `img[15]` | `[]` | Nadie les dijo qué era el polvo. La compañía lo sabía desde hacía dieciocho años. |
| cap 3 | A2 `img[5]` | `['Eric Saint']` | y que convendría examinar algunos de esos tórax. Se llama Eric Saint. |
| cap 3 | A2 `img[6]` | `['Eric Saint']` | Lo que pasó con la carta lo contó él mismo: «Me desestimaron y, de hecho, me tildaron de alborotador», dijo Saint. |
| cap 3 | A2 `img[9]` | `[]` | Nueve años después, otro organismo entró al molino y escribió lo que vio. Mil novecientos cincuenta y siete. |
| cap 3 | A2 `img[10]` | `[]` | La Junta de Referencia entra al molino y deja constancia: condiciones extremadamente polvorientas, trabajadores cubierto… |
| cap 3 | A2 `img[11]` | `[]` | «Una espesa nube de polvo estaba presente en las inmediaciones del molino», escribió la Junta. |
| cap 3 | A2 `img[13]` | `[]` | CSR venía de la industria azucarera y tenía muy poca experiencia en minas. Los reguladores del Estado hicieron poco más … |
| cap 3 | A2 `img[14]` | `[]` | Jim McNulty lo explicó así: cuando las Casandras advirtieron que el polvo era un problema y predijeron la enfermedad, en… |
| cap 3 | A2 `img[15]` | `['María Bernal']` | «porque estaban acostumbrados; lo esperaban», dijo McNulty. En mil novecientos sesenta y uno la producción subió. Al año… |
| cap 4 | A2 `img[1]` | `['Víctor Calvo']` | Víctor Calvo lo cuenta: «Nosotros jugábamos con él y lo íbamos deshilachando. Nos lo metíamos en la boca. |
| cap 4 | A2 `img[2]` | `[]` | Cuando lo tocábamos salía un polvillo que lo impregnaba todo». |
| cap 4 | A2 `img[3]` | `[]` | Estaban rodeados de amianto azul y no les daba miedo. Tampoco había dónde no estar rodeados. |
| cap 4 | A2 `img[11]` | `['María Bernal']` | Tres meses después le tocó a María. Llegó al hospital de Wittenoom debilitada por una infección renal. El bebé era muy g… |
| cap 4 | A2 `img[12]` | `[]` | Le pusieron Daniel, como el padre. Hay una foto del bautizo: siete de julio de mil novecientos sesenta y tres. Después d… |
| cap 4 | A2 `img[13]` | `['María Bernal']` | Se fueron antes de que nadie les dijera nada. Nadie les había dicho nada. |
| cap 2 | referencia `img[1]` | `['María Bernal']` | Un año después se casan: el jueves veinte de septiembre de mil novecientos sesenta y dos. |
| cap 2 | referencia `img[2]` | `[]` | Cuatro días más tarde ya están en el barco. Van a Australia con el acuerdo migratorio por el que pasaron cerca de ocho m… |
| cap 2 | referencia `img[3]` | `['María Bernal']` | De Wittenoom no saben nada; saben que hay trabajo y que van juntos. |
| cap 2 | referencia `img[7]` | `['Víctor Calvo']` | Un niño que hizo ese viaje todavía recuerda el calor. Víctor Calvo era un niño cuando subió a ese barco. |
| cap 2 | referencia `img[12]` | `[]` | Aterriza en una pista en medio de una tierra muy roja, en el desierto de Pilbara, en Australia Occidental. |
| cap 2 | referencia `img[13]` | `['Víctor Calvo']` | Hay polvo por todas partes. Ese niño cuenta que nunca había visto tanto polvo. |
| cap 2 | referencia `img[14]` | `[]` | Los llevan a las casas: chapa, madera y uralita. La familia de Juan-Barroso había llegado en agosto de mil novecientos s… |
| cap 2 | referencia `img[15]` | `[]` | De esa tierra sacan crocidolita, el asbesto azul, un mineral que se paga bien porque aguanta el calor y no se gasta. Nad… |
| cap 3 | referencia `img[5]` | `['Eric Saint']` | Se llama Eric Saint. Lo que pasó con la carta lo contó él mismo: «Me desestimaron y, de hecho, me tildaron de alborotado… |
| cap 3 | referencia `img[8]` | `[]` | Nueve años después, otro organismo entró al molino y escribió lo que vio. |
| cap 3 | referencia `img[9]` | `[]` | Mil novecientos cincuenta y siete. La Junta de Referencia entra al molino y deja constancia: condiciones extremadamente … |
| cap 3 | referencia `img[10]` | `[]` | trabajadores cubiertos de polvo de pies a cabeza. «Una espesa nube de polvo estaba presente en las inmediaciones del mol… |
| cap 3 | referencia `img[12]` | `[]` | CSR venía de la industria azucarera y tenía muy poca experiencia en minas. |
| cap 3 | referencia `img[13]` | `[]` | Los reguladores del Estado hicieron poco más que emitir advertencias y pedir equipos para el polvo. |
| cap 3 | referencia `img[14]` | `[]` | cuando las Casandras advirtieron que el polvo era un problema y predijeron la enfermedad, en la industria minera no se e… |
| cap 3 | referencia `img[15]` | `[]` | En mil novecientos sesenta y uno la producción subió. Al año siguiente, los Écija bajaban de aquel avión. |
| cap 4 | referencia `img[1]` | `['Víctor Calvo']` | Víctor Calvo lo cuenta: «Nosotros jugábamos con él y lo íbamos deshilachando. Nos lo metíamos en la boca. Cuando lo tocá… |
| cap 4 | referencia `img[2]` | `[]` | Estaban rodeados de amianto azul y no les daba miedo. |
| cap 4 | referencia `img[3]` | `[]` | Tampoco había dónde no estar rodeados. |
| cap 4 | referencia `img[11]` | `['María Bernal']` | Tres meses después le tocó a María. Llegó al hospital de Wittenoom debilitada por una infección renal. |
| cap 4 | referencia `img[12]` | `['María Bernal', 'Daniel Écija']` | El bebé era muy grande. Lo sacaron con fórceps. Le pusieron Daniel, como el padre. Hay una foto del bautizo: siete de ju… |
| cap 4 | referencia `img[13]` | `['María Bernal', 'Daniel Écija']` | Después de esa foto, las maletas. Diez meses en Wittenoom. Se fueron antes de que nadie les dijera nada. Nadie les había… |

## A2.3 Diagnóstico de CC (por qué Daniel no entra)

- En las 3 corridas (A corrida 1: 4 fotos con Daniel; A corrida 2: 4; A2: 2, las dos copiadas de la referencia en el cap 1), **las 10 de 10 fotos con Daniel en `persona` llevan en el prompt «one foot bandaged» o «with a limp»**: el retrato con el pie vendado, «esperaba que le cerrara» (1962), la foto del bautizo, la partida cojeando.
- El canon que ve Opus para Daniel es «a young adult Spanish migrant miner in work clothes, one foot visibly bandaged», era 1962-1963; y el casillero pide la persona «at the same age and condition the canon describes». El baile (1961, traje), la boda, el barco, la pista y la mina de la explosión no tienen venda (y 1961 cae fuera de la era) → Opus concluye que no es «la misma condición» y deja a Daniel afuera. María («newlywed migrant woman in a modest cotton dress, hopeful yet physically weakened») no tiene una marca física tan específica, por eso sí entra.
- Es decir: «or if unsure» no era la causa; la causa es la cláusula de condición + un `appearance_canon` que fija un estado transitorio (la venda) como identidad. Decisión del analista/Omar: (i) sacar «and condition» del casillero (dejar «at the same age»), o (ii) decir en el casillero que `appearance_canon` describe a la persona en el momento del caso y no excluye otras escenas, o (iii) que el canon de personas separe identidad de estado (ropa, vendas). No se cambió nada más en esta etapa.

## A2.4 Control de nombres (regla nueva) en los prompts de chapters[1..3]

Nombres de `documented_people[].name` del canon de la copia (22), sin mayúsculas ni acentos, con borde de palabra. **PARÁ (2+ palabras): 0.** «Revisar» (1 palabra): 1.

PARÁ: (ninguno)

Revisar:
- `chapters[2].img[7]` · token «Court» (nombre del canon: Court, 1 palabra → revisar) · prompt completo:

      A 1949 labour arbitration hearing: Australian union men of European descent in shirtsleeves on benches, board members in formal suits at a raised table. The hearing in session, union men leaning forward on benches as the company side rises to answer. Adult Australian men of European descent with fair to tanned skin. Adult Anglo-Australian men of European descent with fair to sun-weathered skin and short hair. Austere arbitration court room 1949, dark timber panelling, high windows, wooden benches and a raised bench. Hard late-afternoon light from high windows, long shafts across the benches. Wide shot, high angle from the back of the room, deep depth of field, 35mm lens. A grainy 35mm documentary photograph taken in 1949, with muted colors and slight underexposure, in a dark-history realist style. The image has a 16:9 aspect ratio. No readable text, no signage, no labels.


## A2.5 Suites (`lab/hyperframes/f41/f60a2/`)

ch02 md5 `f792f3d483a1fa42daed5f7f0e054f46` (candado) · rápida 53 verdes + 3 skipped · amplia **1295 verdes + 31 skipped + 3 xfail + 4 fallas = las 4 previas** (`m03_merge_timing` ×2, `gfx_lab` ×2). El flaky `test_candado_en_el_preview` no apareció esta vez.

## A2.6 Gasto

| qué | US$ |
|---|---|
| m03 caps 2-4 (Opus casilleros + Flash anclas) + pase F8 de video | 1.0826 |

## Lo que queda abierto (A2)

1. **Daniel sigue sin ruteo** en las escenas sin venda; la causa propuesta es «same age and condition» + canon con la venda (A2.3). Hace falta una decisión sobre el texto del casillero o sobre el canon antes de la Etapa B.
2. **Las anclas no son estables entre corridas** (8/16, 8/16, 8/14 pares): cualquier comparación A/B de m03 por foto es ruidosa; una prueba más limpia sería fijar las anclas (paso 1) y repetir solo los casilleros (paso 2).
3. Con una sola corrida, los 2 cambios del cap 2 (baile `[]` → María; «Esa familia madrileña» `[Milagros, Víctor]` → `[]`) pueden ser ruido de Opus tanto como efecto del texto.
4. «Court» como sustantivo queda en «revisar» (no frena). Los nombres de 1 palabra del canon («Court», «Major», «Wright», «Hancock», «Mercedes») seguirán apareciendo ahí.
5. El pase F8 de video corrió con 4 caps de referencia pegados; esta vez no tocó nada fuera de 2-4, pero el método depende de que el refill no elija un ítem de esos caps.
