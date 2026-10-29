# F54 — gancho con apuesta, loops declarados y chequeos por código · REPORTE (Parte A)

Handoff: `lab/hyperframes/f54/HANDOFF_F54_gancho_con_apuesta.md` (md5 `1ac47c9bef43ad3f1c66fcd7acc593cc`, verificado al arrancar). Rama `f11-guion-v4`. Tope de la tanda US$ 6 (`lab/TOPE_TANDA.json` = 6,00 desde 2026-10-29T16:17:29). **Gasto de la Parte A: US$ 0** (sin LLM, sin red).

## Para Omar, en corto
- La escaleta ya no rechaza una promesa del gancho con años o cifras, y el prompt le dice que puede nombrar lo que está en juego. La imagen del gancho sigue sin año ni cifras.
- El guionista ya no copia la promesa tal cual: la dice con sus palabras, con lo que está en juego.
- Dos chequeos nuevos frenan el guion: el cap 7 no dice el dato del cierre, o una misma cita se dice en dos caps. Sobre el guion actual de Wittenoom, **frena por el cierre del cap 7 (D42)**, como esperaba el analista.
- Dos números nuevos en la tabla, que no frenan: años dichos por cap y datos por minuto.
- **Falta tu dato para la etapa 0:** la línea de las 16:05 en DECISIONES lleva «loops: N» y «re-gancho: <decisión>», y no me llegaron los valores (ni están en el handoff). No la escribí. Votos del analista: 2 loops; re-gancho al final del cap 3, como campo `recuerda_loop`.

## Commits
| commit | qué |
|---|---|
| `1c9cd7d` | etapa 0: DECISIONES 15:40 (texto literal del handoff). La de las 16:05 espera tus valores. ESTADO sin diferencias de CRLF: `git diff --ignore-cr-at-eol --stat` vacío, nada que normalizar |
| `2f91029` | Parte A: código, tests, prompts en `.md`, stickers, MAPA |
| `5bc5965` | `salida_a.py` + `SALIDA_A.md` |
| (este) | reporte, ESTADO, logs de la suite |

## Módulos: antes → después
| módulo | antes | después |
|---|---|---|
| `script_engine/m01a_escaleta.py` | `validate`: rechazo duro si la promesa del gancho lleva cifras o años; `metricas_escaleta.promesa_con_cifras`; `NUM_WORDS` sin dieciséis–diecinueve ni veintiuno–veintinueve; prompt `f26-1` | sin el rechazo y sin la métrica (la imagen del gancho con cifras sigue en hard); `NUM_WORDS` armado con unidades y decenas: `dieci(seis…nueve)`, `veinti(un…nueve)`, `«decena» y «unidad»` como un solo token, sin lista por tema (`NUM_PALABRA` exportado); `SYSTEM_V2` = `f54-1`, `SYSTEM_V2_F26_1` / `PROMPT_VERSION_V2_F26_1` quedan como constantes; `PROMPT_VERSION_COLUMNA` = `f54-1` |
| `script_engine/guion_v4.py` | sistema v5.4 (`f25-1`); bloqueantes a–e | `SYSTEM_V5_5` (`f54-1`) por defecto, v5.4 con `version="f25-1"`; bloqueantes nuevos **(f) cierre no dicho** y **(g) cita repetida**; `metricas` con `anios_por_cap` y `datos_por_min` |
| `script_engine/guion_v3_reglas.py` | — | `anios_por_cap(caps)`, `datos_por_min(caps, palabras_por_seg)` (solo tabla) |

Lectores que no se tocaron: `m01b_guionista.has_figure` (gancho) y `m01c_editor` (`NUM_WORDS.findall`) ahora ven también los compuestos; es el arreglo general que pide la tabla de constantes (con «treinta y dos» y «treinta y tres» antes los dos eran «treinta»).

Tests: `test_module_f54.py` nuevo (26); `test_module_f6b.py` −2 parámetros (promesa con cifras); `test_module_f16.py` sin la promesa con cifras (l. 129 y la métrica en l. 134); `test_module_f17.py`, `test_module_f22.py`, `test_module_f25c.py`, `test_module_f26.py`: la versión de hoy es `f54-1` y lo viejo se compara con su constante (`SYSTEM_V2_F26_1`, `system("f25-1")`), con el mismo md5 de antes.

## Decisiones de CC
1. **Letras de los bloqueantes.** En `guion_v4` ya existen (d) contaminación y (e) cita sin verificar con nombre (y `reparar` edita por oración justamente a, b, d, e). Por eso la (d) del handoff va como **`f`** y la (e) como **`g`**. Así no entran a la edición por oración: llegan tal cual a `bloqueantes_despues` y frenan. La (f) de la Parte B iría como `h`.
2. **(f) cierre no dicho:** mira los `ids_usados` (los calculados: lo que dice la voz ∩ los ids del beat) de los párrafos del cap del beat `funcion=cierre`, que es el 7. No cuenta lo que el modelo declara.
3. **(g) cita repetida:** mira lo que la voz dice, `used_items` sobre las citas del pool (con las traducciones de la ficha), no solo los ids del beat; si lo limitara a los ids del beat, una cita dicha fuera de su beat no se vería. Dos veces en el mismo cap no frena. Dos ids con el mismo texto (Q12/Q25) no se miran: es dedupe del pool, a la lista.
4. **Qué cuenta como año** (`anios_por_cap`): 4 cifras seguidas sin punto («1962»; «2.000» no), «mil ochocientos/novecientos [+ número]» y «dos mil + número». «Dos mil» solo no cuenta (en Wittenoom es «dos mil personas»). Cada mención cuenta. El «4» de `\d{4}` es la definición de un año escrito en cifras, no un umbral; lo dejo dicho por la regla de los números.
5. **«Las 6 frases de la ENTRADA 29h»:** la ENTRADA no las numera. Corrí la tabla sobre las 11 frases que cita en §3 (voz de hoy, `cierre_humano`, DEBERÍA). Si eran otras 6, se corre de nuevo sin costo.
6. **Párrafos de Wittenoom:** `01b_narration.json` no trae beats. Partí cada cap por línea en blanco y les di el beat del párrafo de `01b_guionista_v4.json` (`reparacion.parrafos`) en la misma posición. El script verifica que la cantidad coincida en los 7 caps (24 párrafos). El cap 7 de `01b_narration` es más corto que el de la reparación (207 contra 279 palabras): el párrafo del beat 14 perdió la vuelta a la foto, que es justo lo que (f) detecta.
7. **Versiones viejas como constantes:** el handoff lo pide en A.1 («como siempre»). La regla «lo viejo se borra» la apliqué a lo que se quitó: el rechazo, la métrica y los parámetros de test, sin flag.

## Salida A (texto)

### 1. Diff de los dos prompts (viejo → nuevo, solo las líneas que cambian)

#### Escaleta f26-1 → f54-1 (`<oficio>` §2)

```diff
- 2. El gancho es el peor momento, ya en curso. Tomá la escena más fuerte de la ficha y ponela en el beat 1, marcado como flash-forward. Sin contexto, sin año, sin cifras: lo que se ve. La promesa es una sola oración que deja una imagen sin cerrar o una pregunta que el espectador no puede responder todavía. No cuenta lo que va a pasar, no enumera lo que viene, no nombra juicios, comisiones ni consecuencias. Probala así: si la oración se puede leer como un resumen de lo que viene («nadie lo sabrá durante años», «terminará en un juicio»), no es una promesa; es un adelanto. Volvé a escribirla con lo que se ve o lo que no cierra.
+ 2. El gancho es el peor momento, ya en curso. Tomá la escena más fuerte de la ficha y ponela en el beat 1, marcado como flash-forward. Sin contexto, sin año, sin cifras: lo que se ve. La promesa es una sola oración que deja una imagen sin cerrar o una pregunta que el espectador no puede responder todavía. La promesa dice qué va a entender el espectador si se queda: puede nombrar lo que está en juego, con años o cifras si hacen falta; no es un índice de lo que viene.
```

#### Guion v5.4 (f25-1) → v5.5 (f54-1) (`<estructura>` 1)

```diff
- 1. Gancho (cap 1): la escena del peor momento, ya en curso. Primera frase: lo que se ve, sin año, sin cifra, sin institución. Segunda: la promesa, como viene en la escaleta, sin agregarle lo que va a pasar después. Antes de terminar el cap, una frase corta con lugar y año. El cap 1 termina volviendo atrás: «horas antes», «días antes».
+ 1. Gancho (cap 1): la escena del peor momento, ya en curso. Primera frase: lo que se ve, sin año, sin cifra, sin institución. Segunda: la promesa: lo que está en juego, con tus palabras, sin índice de lo que viene. Antes de terminar el cap, una frase corta con lugar y año. El cap 1 termina volviendo atrás: «horas antes», «días antes».
```

Para mirar: en la escaleta quedan dos oraciones seguidas que empiezan «La promesa…» (la vieja «es una sola oración que deja una imagen sin cerrar…» no estaba dentro del tramo a reemplazar). Así lo pide el handoff; si el analista quiere sacar la primera, es un cambio de una línea.

### 2. `has_figure` sobre las frases de la ENTRADA 29h (§3)

| # | de dónde | frase | antes | ahora | qué lo detecta ahora |
|---|---|---|---|---|---|
| 1 | voz de hoy | Un hombre joven posa para una foto con el pie envuelto en una venda blanca. | no | no | — |
| 2 | voz de hoy | Detrás, tierra roja y paredes de chapa. | no | no | — |
| 3 | voz de hoy | En el retrato de familia todos miran a cámara menos el pie. | no | no | — |
| 4 | voz de hoy | El hombre se llama Daniel Écija. | no | no | — |
| 5 | voz de hoy | Para entender ese pie hay que volver a un baile en Madrid. | no | no | — |
| 6 | cierre_humano | La herida del pie cerró. La otra nadie supo verla a tiempo. | no | no | — |
| 7 | DEBERÍA | Un hombre joven posa con el pie envuelto en una venda blanca. | no | no | — |
| 8 | DEBERÍA | Le cayó un trozo de amianto y la herida no cierra. | no | no | — |
| 9 | DEBERÍA | Wittenoom, Australia, mil novecientos sesenta y dos. | sí | sí | mil, novecientos, sesenta y dos |
| 10 | DEBERÍA | Esa herida va a cerrar. | no | no | — |
| 11 | DEBERÍA | Lo que respiró ese año, no: veintinueve años después, al otro lado del mundo, el polvo lo va a alcanzar. | no | **sí** | veintinueve |

La 11 es el bug de la tabla de constantes: «veintinueve» antes no se detectaba. Tests extra: dieciséis, diecinueve, veintiún, veintiuno, veintitrés, treinta y dos y noventa y nueve dan sí; «miles», «un hombre», «una venda», «decenas» dan no.

### 3. `bloqueantes` + `metricas` sobre el guion actual de Wittenoom

Fuente: `data/scripts/_steps/123bbb64-9fca-4395-8bf4-57d60e219ef1/01b_narration.json` (24 párrafos, beats según la decisión 6). Escaleta `01a_escaleta.json`, ficha `ficha_caso.json`, perfil `_perfil.json`. Llamada igual a la de producción: `bloqueantes(topic, esc, ps, "abierto", ficha)`.

**Bloqueantes: 2**

| código | cap | beat | motivo | frase |
|---|---|---|---|---|
| d | 3 | 4 | fuera del caso (descartado en el pool): Defensor del empleador no identificado | Un año después, en una sala de arbitraje, la empresa contestó a los que hablaban del polvo. «El mero hecho de que haya n… |
| **f** | 7 | 14 | cierre no dicho: el dato central D42 del beat 14 (cierre) no está en el cap 7 | — |

- **(f) frena en el cap 7 por D42**, como esperaba el handoff.
- **(g)** no salta: ninguna cita se dice en dos caps (Q12 en el cap 2 y Q25 en el cap 5 son ids distintos; eso es dedupe, a la lista).
- La **(d)** del cap 3 es un bloqueante viejo (contaminación), no es de esta tanda: ya estaba en el código y esta corrida lo muestra porque mide el texto final. No lo toqué. Queda abierto (ver abajo).

**Métricas nuevas por cap (solo tabla, sin freno)**

| cap | palabras | años dichos | datos usados | datos/min |
|---|---|---|---|---|
| 1 | 86 | 1 | 0 | 0.0 |
| 2 | 303 | 3 | 5 | 2.4 |
| 3 | 350 | **6** | 3 | 1.2 |
| 4 | 239 | 3 | 6 | 3.6 |
| 5 | 345 | **8** | 6 | 2.5 |
| 6 | 361 | **7** | 2 | 0.8 |
| 7 | 207 | 3 | 3 | 2.1 |

Total: 1891 palabras ≈ 13,1 min.

**Años contra lo esperado:** el handoff esperaba 7 en los caps 3, 5 y 6; salen **6, 8 y 7**. Los conté a mano oración por oración: cap 3 = 1944, 1946, 1943, 1948, 1957, 1961; cap 5 = 1966, 1971, 1985, 1978, 1986, 1992, 1993, 1991; cap 6 = 1989, 1988, 2007, 2006, 1992, 2016, 2023. El contador está bien; el «7» del handoff era aproximado. No ajusté nada para que dé 7.

## Suite
`bash lab/hyperframes/f41/verificar.sh f54a` (logs en `lab/hyperframes/f41/f54a/`):
- ch02 md5 `f792f3d483a1fa42daed5f7f0e054f46` (candado igual);
- rápida **55 passed**, 3 skipped;
- amplia **1077 passed** + las 4 fallas previas conocidas (`m03_merge_timing` ×2, `gfx_lab` ×2), 30 skipped. +24 contra F53b (1053): +26 de `test_module_f54.py`, −2 parámetros de f6b;
- `mapa_modulos.py --check`: 158 archivos, 0 fallas.

## Lo que queda abierto
1. **Etapa 0, línea de las 16:05:** falta que Omar diga «loops: N» y «re-gancho: <decisión>». Se escribe apenas lleguen, con el texto literal del handoff más esos dos campos.
2. **Dedupe de citas del pool** (Q12/Q25: dos ids con el mismo texto): a la lista; el umbral lo decide Omar.
3. **Tope de años por cap:** solo métrica (6/8/7 en los caps 3/5/6); el tope, si lo hay, lo decide Omar con este dato.
4. **(d) contaminación en el cap 3 de Wittenoom** («Defensor del empleador no identificado», descartado en el pool) sobre una cita de la empresa en el arbitraje: puede ser un falso positivo de `contamination`. No es de esta tanda; si frena en la corrida de la Parte B, se ve ahí.
5. **Las «6 frases»:** si el analista tenía otra lista, se corre de nuevo (US$ 0).
6. **Dos «La promesa…» seguidas** en `<oficio>` §2 de la escaleta f54-1 (ver salida 1).
7. F44 (P16 nombre/rol), miniatura real y fotos: fuera de esta tanda (handoff, «Lo que NO hace»).
8. **Parte B:** solo con el «sigue» de Omar (B.1/B.3 esquema, validador y bloqueante; B.2 el bloque `<ejemplos>` con PARADA B.0 para el analista; B.4 m09; B.5 corrida de Wittenoom en texto, ≈ US$ 5).

**PARADA A.**

## Veredicto de revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito (handoff / pedido) | estado | evidencia |
|---|---|---|---|
| 0 | md5 del handoff | OK | `md5sum` = 1ac47c9b…cc, coincide |
| 1 | Etapa 0: línea 15:40 en DECISIONES | OK | `DECISIONES.md` +1 línea (1c9cd7d), texto literal |
| 2 | Etapa 0: línea 16:05 (con loops N y re-gancho) | PARCIAL | No escrita. Es coherente con tu nota: Omar no pasó los valores. La etapa 0 queda abierta. |
| 3 | Etapa 0: ESTADO_SESION, normalizar CRLF solo si es eso | OK | El reporte dice que `git diff --ignore-cr-at-eol --stat` dio vacío en ese momento. No lo repetí. Hoy `lab/ESTADO_SESION.md` figura modificado (+13/−1), es la actualización del hito, aún sin commitear. |
| 4 | A.1 borrar el rechazo de promesa con cifras y la métrica `promesa_con_cifras` | OK | `m01a_escaleta.py`: el `hard.append` ya no está (queda solo el comentario) y la métrica fue borrada. La imagen del gancho sigue en hard. |
| 5 | A.1 `has_figure`/`NUM_WORDS` con compuestos, regex general | OK | `_UNIDAD`, `_DECENA` y `NUM_PALABRA` en `m01a_escaleta.py`. `has_figure("veintitrés años")` da True y `has_figure("un hombre")` da False (corrí ambos). |
| 6 | A.1 prompt `f54-1`: una sola oración sustituida; viejo como constante | OK | Comparé los dos textos por código: difiere 1 línea, solo la de §2. `SYSTEM_V2_F26_1` y `PROMPT_VERSION_V2_F26_1` quedan; la columna pasa a `f54-1`. |
| 7 | A.2 guion v5.5 `f54-1`: una sola línea cambia | OK | `g4.system("f25-1")` contra `g4.system()` difiere 1 línea, la de `<estructura>` 1. La línea de «Primera frase… sin año» se mantiene. |
| 8 | A.2 bloqueante cierre no dicho y bloqueante cita repetida | OK, con desvío de código | `guion_v4.py`: `cierre_no_dicho` y `cita_repetida`, con letras f y g. Se explica abajo. |
| 9 | A.3 métricas `anios_por_cap` y `datos_por_min` (solo tabla, 2,4 pal/s) | OK | `guion_v3_reglas.py` +18 líneas. `PALABRAS_POR_SEG = 2.4` está en `guion_v4.py:1056`. Ninguna frena. |
| 10 | A.4 tests: borrar f6b y f16, reescribir f25c y f26, tests nuevos | OK | `test_module_f54.py` (26 tests). f6b −2 parámetros, f16 sin la promesa con cifras. Corrí f54, f6b, f16, f17, f22, f25c, f26 y f11: 156 passed, 11 skipped. |
| 11 | Suite verde | OK | `suite_rapida.log`: 55 passed. `suite_amplia.log`: 1077 passed + 4 fallas previas conocidas (`m03_merge_timing` ×2, `gfx_lab` ×2). No las reproduje. |
| 12 | Salida A, diff de los dos prompts | OK | `F54_REPORT.md` y `SALIDA_A.md`; coincide con lo que verifiqué. |
| 13 | Salida A, tabla `has_figure` sobre las «6 frases» | PARCIAL | La ENTRADA 29h no numera 6 frases. CC corrió 11 y lo declaró. Cubre cualquier lista razonable. La frase 11 («veintinueve») es el caso que falla antes del arreglo. |
| 14 | Salida A, bloqueantes y métricas sobre `01b_narration.json`: frena por cierre no dicho en cap 7, años/cap 7 en caps 3, 5, 6 | PARCIAL | Frena por D42 en el cap 7, como esperaba el handoff. También frena una contaminación vieja en el cap 3, que no es de esta tanda. Años: salen 6, 8 y 7, no 7, 7 y 7. CC los contó a mano oración por oración (años de los caps 3, 5 y 6 enumerados en el reporte) y no ajustó nada. No lo recorrí; la discrepancia está declarada. |
| 15 | `F54_REPORT.md` con «lo que queda abierto» | OK, a cerrar | Existe, con 8 puntos. Falta pegar este veredicto y commitearlo (el propio reporte lo dice). |
| 16 | Tope US$ 6 y gasto de la Parte A | OK | Reporte: US$ 0, sin LLM ni red. `lab/TOPE_TANDA.json` figura modificado, consistente con el reporte. |

Decisiones de CC frente al handoff y a las reglas fijas:
- **f y g en vez de d y e:** no se aparta del handoff. En `guion_v4` ya existían (d) contaminación y (e) cita sin verificar, y `reparar` edita por oración justo esas letras. Con f y g los nuevos frenan sin pasar por la edición, que es lo que pide el handoff. Queda anotado que el bloqueante de la Parte B sería `h`.
- **Criterio de años:** es el punto más débil frente a la regla «ningún número ni lista de palabras nuevos».
  - `\d{4}`, `mil (ochocientos|novecientos)` y `dos mil` no están en la tabla de constantes. El handoff pide «años literales, dichos o en letras», así que algún criterio era inevitable.
  - Cuenta como año cualquier cifra de 4 dígitos sin punto, no solo años. Es una métrica sin freno y CC lo declaró, pero conviene que Omar lo vea.
- **Las «6 frases»:** no hay desvío; ver fila 13.
- **Párrafos por posición:** `01b_narration.json` no trae beats, así que CC asignó el beat de `01b_guionista_v4.json` por posición dentro del cap, con verificación de cantidad (24 párrafos). El cap 7 es más corto (207 contra 279 palabras), por lo que D42 ausente depende de esa reconstrucción. La conclusión es coherente con lo que esperaba el handoff, pero es una inferencia.
- **Versiones viejas como constantes:** las pide el handoff en A.1, así que no hay desvío. Lo que se quitó (rechazo, métrica, parámetros de test) se borró sin flag, como piden las reglas fijas. Un detalle de prolijidad: en el prompt de la escaleta quedan dos oraciones seguidas que empiezan con «La promesa…». Es literal del handoff y CC lo señaló.

Fuera de alcance: ninguno. Lo tocado coincide con la Parte A: los 3 módulos, los tests, `lab/hyperframes/f54/` (los `.md` de los prompts, `salida_a.py`, `SALIDA_A.md`), más `lab/mapa/stickers/guion.json` y `MAPA_PROYECTO.json/.md`, que son mantenimiento de rutina del mapa. No verifiqué que `diag_234_cap4.py` y `f28a.log` (modificados desde antes en el árbol, no son de la tanda) sigan sin tocarse.

Riesgos que el contrato no cubre:
- Los números que Omar debe decidir siguen abiertos: loops 1–2, re-gancho y el tope de años por cap. Sin la línea de las 16:05 la Parte B no tiene constantes aprobadas.
- Falsos positivos de los chequeos nuevos: el bloqueante de contaminación del cap 3 ya frena hoy y puede frenar la corrida de la Parte B. La cita repetida depende del dedupe del pool (Q12/Q25), que no está resuelto.


## Adenda de CC
- **Fila 14, párrafos por posición:** en el cap 7, D42 tampoco está en el párrafo del beat 14 de `01b_guionista_v4.json` (antes del recorte; `ids_usados` vacío). O sea, (f) frena aunque el beat se asigne de otra forma; no depende de la reconstrucción.
- **`diag_234_cap4.py` y `f28a.log`:** no los toqué ni entraron en ningún commit (`git show --stat` de `1c9cd7d`, `2f91029` y `5bc5965`).
- **Criterio de años:** si Omar o el analista prefieren otro (por ejemplo, sin `\d{4}`), se cambia en una línea de `guion_v3_reglas.anios_por_cap`; como solo es métrica, nada frena por él.
- **La Parte B espera dos cosas:** el «sigue» de Omar y la línea de las 16:05 con «loops: N» y «re-gancho», que son las constantes de B.1.


---

# Parte B — B.1/B.3 + chascada · PARADA B.0 (Omar: «sigue», 2026-10-29 16:50)

Pedido de Omar al dar el «sigue»: Fable medium; loops: 2 · re-gancho: sí, al cierre del cap 3 (campo `recuerda_loop`); chascada: §2 de la escaleta con una sola oración sobre la promesa; B.1 y B.3; después B.2 con PARADA B.0; B.4 y B.5 solo con el OK del analista. **Gasto hasta acá: US$ 0** (sin LLM).

## Commits
| commit | qué |
|---|---|
| `f72da82` | etapa 0, cierre: DECISIONES 16:05 con «loops: 2 · re-gancho: sí, al cierre del cap 3 (campo recuerda_loop)» |
| `66804dc` | B.1/B.3 + chascada: código, tests, los dos `.md`, stickers, MAPA |
| (este) | reporte (esta sección), `EJEMPLOS_v5_6_propuesta.md`, ESTADO, logs |

## Módulos: antes → después
| módulo | antes | después |
|---|---|---|
| `script_engine/m01a_escaleta.py` | esquema sin loops; §2 de `f54-1` con dos oraciones sobre la promesa | **esquema:** `loops: [{id, pregunta, abre_beat, paga_beat}]` (requerido), `recuerda_loop: {beat, oracion}` (opcional, con descripción: «el re-gancho: una oración al cierre del cap 3»), `beat.paga` (INTEGER, 0 = ninguna; descripción en el esquema). **validador:** `LOOPS_RANGO = (1, 2)` y `RECUERDA_LOOP_CAP = 3` (DECISIONES 16:05); cada loop se paga después de abrirse; el principal (el primero) en el cap 7 o en el pico; `paga` apunta a un beat anterior; `recuerda_loop`, si viene, en el último beat del cap 3 con su oración; sin loop → hard sin fabricar («si la ficha no da para un loop, decilo»). 3 bloqueantes nuevos en `BLOQUEANTES_V2` (rechazan → PARADA tras la regeneración). **métricas:** `loops`, `beats_con_paga`, `recuerda_loop`. **prompt `f54-1`:** §2 = una oración sobre la promesa + la línea literal de B.1 |
| `script_engine/guion_v4.py` | `<estructura>` 2 «termina con algo sin resolver que el siguiente paga»; el guionista no veía pagos | `<estructura>` 2 reemplazado (B.3, literal); `escaleta_section_v5` muestra por beat `paga: la pregunta del beat N («…»)` y `recuerda el loop: …`; el `<caso>` lleva `LOOP n: pregunta — se abre en el beat a, se paga en el beat p` (`loops_txt`; sin loops, nada); **bloqueante (h) pago no dicho:** el `dato_central` de un beat con `paga` (o del `paga_beat` de un loop) no está en los `ids_usados` de su cap → frena, sin edición por oración |
| `test_module_f6b.good()` | sin loops | un loop (abre 1, paga 8) y el beat 8 con `paga: 1`: la fixture que comparten f6b/f8/f16/f17/f19/f22/f24/f39/f54 |

Tests: `test_module_f54.py` 39 (26 de A + 13: esquema, pasa y normaliza, 9 rechazos duros que son bloqueantes, pico/segundo loop/recuerda_loop que pasan, métricas, `escaleta_section_v5`, bloqueante h frena/pasa). Los dos tests de los prompts se reescribieron: la escaleta sigue siendo un solo cambio contra f26-1 (toda §2 desde «La promesa es una sola oración…»); el guion v5.5 son dos líneas contra v5.4 (§1 y §2).

## Decisiones de CC (Parte B.1/B.3)
1. **La (f) del handoff es `h`** (f y g se usaron en la Parte A). Igual que f y g, no pasa por la edición por oración: frena.
2. **`recuerda_loop` opcional** en el esquema, como lo escribe el handoff («opcional»); Omar dijo «re-gancho: sí». Cuando el modelo lo trae, el validador exige el último beat del cap 3 (RECUERDA_LOOP_CAP, DECISIONES 16:05) y una oración. No lo hice obligatorio porque el prompt de B.1 no lo nombra y la regla fija prohíbe agregar texto al prompt; en vez de eso lleva `description` en el esquema (formato de salida). Si el modelo no lo trae en B.5, se ve en la tabla y lo decide Omar.
3. **`paga` = 0 significa ninguna.** El esquema de salida estructurada no acepta `null` cómodamente (el conversor baja `type` a minúsculas y exige `additionalProperties: false`); 0 u omitido → `None` al validar.
4. **El loop principal** es el primero de la lista: es el que tiene que pagarse en el cap 7 o en el pico. El segundo solo tiene que pagarse después de abrirse.
5. **(h) también mira el `paga_beat` de cada loop**, no solo los beats con `paga`: DECISIONES 16:05 dice «cierre y pagos chequeados por código», y un loop es un pago declarado.
6. **`<estructura>` §2 del guion:** el texto real era «cada uno avanza la historia y termina con algo sin resolver que el siguiente paga.»; reemplacé la segunda mitad y dejé «cada uno avanza la historia.» como oración propia. Reemplaza, no suma.
7. **Escaletas viejas** (sin `loops`): el guionista y los lectores siguen funcionando (`.get`, `loops_txt` vacío); solo `validate` las rechazaría si volvieran a pasar por él (`frozen_escaleta`). Ningún topic usa `escaleta_frozen` hoy; anotado.

## Salida B.1/B.3 (texto)

### Diff del prompt de la escaleta (f54-1 de la Parte A → f54-1 de hoy, solo la línea que cambia)
```diff
- 2. … Sin contexto, sin año, sin cifras: lo que se ve. La promesa es una sola oración que deja una imagen sin cerrar o una pregunta que el espectador no puede responder todavía. La promesa dice qué va a entender el espectador si se queda: puede nombrar lo que está en juego, con años o cifras si hacen falta; no es un índice de lo que viene.
+ 2. … Sin contexto, sin año, sin cifras: lo que se ve. La promesa dice qué va a entender el espectador si se queda: puede nombrar lo que está en juego, con años o cifras si hacen falta; no es un índice de lo que viene. Declará 1–2 loops: la pregunta que el video deja abierta, en qué beat se abre y en qué beat se paga. Cada beat dice qué pregunta anterior paga (o ninguna).
```

### Diff del prompt del guionista (v5.5 de la Parte A → v5.5 de hoy, solo la línea que cambia)
```diff
- 2. Caps 2 a 6: cada uno avanza la historia y termina con algo sin resolver que el siguiente paga. La última frase de cada cap no resume: deja una puerta abierta o nombra lo que viene.
+ 2. Caps 2 a 6: cada uno avanza la historia. La primera frase de cada cap paga lo que el beat marcado `paga` dejó abierto; la escaleta dice cuál. La última frase de cada cap no resume: deja una puerta abierta o nombra lo que viene.
```

### Lo que el guionista ve ahora en la escaleta (fixture de prueba)
```text
LOOP 1: ¿quién cerró el portón? — se abre en el beat 1, se paga en el beat 12
…
  BEAT 6 · escalada · miedo · intensidad 3
    imagen sensorial: el humo del beat 6
    dato central: [D6] El portón número 6 estaba cerrado
    el espectador se pregunta: ¿quién cerró?
    paga: la pregunta del beat 2 («¿quién cerró?»)
```

### Validador sobre la fixture, con mutaciones (de `test_module_f54`)
| mutación | mensaje duro | bloqueante |
|---|---|---|
| sin loops | `loops: 0 declarado(s); tienen que ser 1–2; si la ficha no da para un loop, decilo en vez de fabricarlo` | sí |
| 3 loops | `loops: 3 declarado(s); tienen que ser 1–2` | sí |
| se abre en 5, se paga en 3 | `loop 1: se abre en el beat 5 y se paga en el 3: tiene que pagarse después de abrirse` | sí |
| principal pagado en el beat 5 (cap 5) | `loop 1 (el principal) se paga en el beat 5 (cap 5): tiene que pagarse en el cap 7 o en el pico (beat 6)` | sí |
| principal pagado en el pico (beat 6) | — | pasa |
| beat 3 con `paga: 5` | `beat 3: paga 5 tiene que apuntar a un beat anterior` | sí |
| `recuerda_loop` en el beat 2 | `recuerda_loop: va en el último beat del cap 3 (beat 3) con su oración; vino beat 2, oración «x»` | sí |
| `recuerda_loop` en el beat 3 con oración | — | pasa |

### Bloqueante (h) sobre la fixture
`pago no dicho: el beat 6 paga la pregunta del beat 2 con D6, que no está en el cap 4` · `pago no dicho: el beat 10 paga el loop L1 con D10, que no está en el cap 6`.

## Suite
`bash lab/hyperframes/f41/verificar.sh f54b` (logs en `lab/hyperframes/f41/f54b/`): ch02 md5 `f792f3d483a1fa42daed5f7f0e054f46`; rápida **55 passed**; amplia **1094 passed** + las 4 fallas previas conocidas (`m03_merge_timing` ×2, `gfx_lab` ×2); `mapa_modulos.py --check`: 0 fallas.

## B.2 — bloque `<ejemplos>` entero (PARADA B.0: espera el OK del analista; no está en el código)
También en `lab/hyperframes/f54/EJEMPLOS_v5_6_propuesta.md`.

```text
<ejemplos>
Los ejemplos son de un caso que no es el tuyo (una estación de radio y faro en una isla, mil novecientos sesenta y ocho). Copiá la técnica, no el contenido: ninguno de estos nombres, lugares ni cifras está en tus datos.

Gancho (escena en curso, la apuesta, lugar y año, vuelta atrás):
«Una mujer transmite en clave morse a la luz de una vela. La sala huele a querosén quemado. Afuera, el faro sigue encendido. Once personas esperan un barco. Tres de ellas no van a ver la primavera. Puerto Cardal, invierno de mil novecientos sesenta y ocho. Pero tres semanas antes de la vela, llegó un telegrama. Y con él, una orden.»

Cierre de cap que deja una deuda, y la primera frase del cap siguiente que la paga:
el cap 2 termina: «El Alborada tenía que llegar el lunes. No llegó el lunes.»
el cap 3 empieza: «El lunes, el Alborada estaba amarrado en el puerto, con la bodega cargada y el capitán a bordo. Lo que faltaba era un papel.»

Re-gancho a mitad del video (una oración que recuerda la deuda sin pagarla, al cierre de un cap):
«Quedaban nueve días de telegramas sin firma. Para entonces, el niño ya tosía.»

Escena con los sentidos, sin inventar hechos (todo sale de «olor a querosén, ventanas tapadas con mantas, el ruido del generador que se apaga, el silencio después»):
«La noche del catorce, el generador tosió dos veces y se apagó. Por primera vez en tres semanas la estación quedó en silencio. Las ventanas estaban tapadas con mantas para guardar el calor. Olía a querosén. Alguien encendió una vela y la sala apareció, chica, llena de gente que no hablaba.»

Cita y silencio después:
«Teo Marín iba en el Alborada esa mañana. "El capitán leyó el papel y dio la vuelta", dijo Marín. No supo qué decía el papel. Vio la isla a lo lejos. Vio que se alejaba.»

El hecho concreto en vez del juicio (no dice «cruel», «abandono», «inhumano»):
«Elvira pidió el barco siete veces. Las siete respuestas dicen lo mismo: mantener servicio. Ninguna tiene firma.»

Pico (dos frases cortas antes, la más corta después; es la primera de las tres muertes que el gancho prometió):
«Bascuñán mira la silla. La levanta. La rompe contra el piso de la sala de radio y mete las patas en la estufa. Esa noche, mientras la madera arde, Elvira transmite con las baterías del faro. En el cuarto de al lado, el niño deja de toser. Nadie lo dice. Lo saben.»

Versiones en disputa, sin elegir:
«Según los telegramas que Elvira guardó, el Alborada zarpó y recibió orden de volver. El capitán declaró ante la comisión que nunca salió del puerto por el temporal. El barco, esa semana, no llegó.»

Cierre del video (vuelve a la imagen del gancho; la última frase es una cita, sin moraleja):
«La vela se apagó sola, al amanecer del día veintitrés, cuando el Alborada ya se veía desde la torre. Elvira Soto no habla de la comisión. Habla de su libro de telegramas: "Yo mandaba los telegramas. Nadie me dijo que los leyeran".»
</ejemplos>
```

## Qué cambió frente al bloque del v5.4/v5.5, ejemplo por ejemplo
| ejemplo | v5.5 | propuesta |
|---|---|---|
| Gancho | «Once personas esperan un barco que no va a llegar, porque alguien decidió que no llegara.» (sin apuesta: no dice qué se pierde) | «Once personas esperan un barco. Tres de ellas no van a ver la primavera.» (la frase del handoff; primera frase sin cifra, lugar y año, vuelta atrás, igual que antes) |
| Cierre de cap que abre | «Cuando el Alborada entró por fin a la bahía, el padre Quiroga contó… Faltaban dos. Las familias decían que tres.» (solo el cierre; adelantaba el conteo del final) | el cierre del cap 2 («No llegó el lunes.») **y** la primera frase del cap 3 que lo paga («…Lo que faltaba era un papel.») |
| Re-gancho | no había | una oración al cierre de un cap de la mitad que recuerda la deuda («…el niño ya tosía») sin pagarla |
| Pico | igual | igual, y el rótulo dice que paga lo que el gancho prometió (la primera de las tres muertes) |
| Cierre del video | la cita de Soto sola | la vela del gancho se apaga (vuelve a la imagen) y después la cita de Soto, igual que antes |
| Escena con los sentidos · Cita y silencio · Hecho concreto · Versiones en disputa | — | sin cambios |

## Para mirar (analista)
- El conteo: el gancho promete tres muertes; el pico es la primera (el niño); el viejo ejemplo de «faltaban dos, las familias decían que tres» se fue con el cierre de cap, y las versiones en disputa (comisión dos, familias tres) siguen en la escaleta de ejemplo de `m01a`. Si eso molesta, cambio «Tres» por lo que diga el analista: la frase es la del handoff.
- «Quedaban nueve días» es un número del caso ficticio (como los veintitrés días y los siete telegramas del bloque viejo), no una constante del pipeline.
- Se agregan dos nombres de técnica (deuda pagada en la primera frase, re-gancho) que ya existen en `<estructura>` §2 y en `recuerda_loop`: no hay regla nueva, hay ejemplo nuevo.

## Lo que queda abierto (Parte B)
1. **PARADA B.0:** el analista revisa el bloque `<ejemplos>`; con su OK entra en `guion_v4` como v5.6 (`f54-2`) y recién ahí B.4 (m09 lee el gancho entero) y B.5 (Wittenoom en texto, ≈ US$ 4 según los pasos de la corrida anterior: escaleta 1,86 + guion 1,23 + reparación 0,08 + partición 0,05 + papel 0,66; tope 6).
2. `recuerda_loop` opcional (decisión 2): si el modelo no lo trae, Omar decide si se vuelve obligatorio.
3. La (d) contaminación del cap 3 de Wittenoom puede frenar la corrida de B.5: no se arregla, se reporta (pedido de Omar).
4. Escaletas viejas sin loops no vuelven a pasar por `validate` (decisión 7).
5. Lo de la Parte A: dedupe Q12/Q25, tope de años por cap, las «6 frases».

**PARADA B.0.**

## Veredicto de revisor-handoff (Parte B.1/B.3, íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

Corrí `pytest -q test_module_f54.py test_module_f6b.py test_module_f16.py` y dio 91 passed. El md5 del handoff coincide (1ac47c9b…). No llamé a ningún modelo.

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Chascada: una sola oración sobre la promesa en §2, en código y `.md` | OK | `m01a_escaleta.py` (SYSTEM_V2 §2) y `PROMPT_ESCALETA_f54_1.md` quedan solo con «La promesa dice qué va a entender…». La vieja «La promesa es una sola oración…» se borró en ambos (`git show 66804dc`). El test byte-idéntico pasa. |
| 2 | Línea de loops literal del handoff, sin agregados | OK | «Declará 1–2 loops: la pregunta que el video deja abierta, en qué beat se abre y en qué beat se paga. Cada beat dice qué pregunta anterior paga (o ninguna).» Es idéntica a B.1. |
| 3 | DECISIONES 16:05 con el texto literal del handoff más los dos valores | OK | `f72da82`. La línea es literal y agrega «loops: 2 · re-gancho: sí, al cierre del cap 3 (campo recuerda_loop) · Omar». |
| 4 | Esquema B.1: `loops`, `recuerda_loop`, `paga` | OK, con desvío menor | `loops` es requerido y `recuerda_loop` es opcional. `paga` es INTEGER con 0 = ninguna; el handoff decía `null`. `validate` lo normaliza a None. |
| 5 | Validador: pago posterior a la apertura, principal en cap 7 o pico, `paga` hacia atrás, sin loop es hard | OK | `m01a_escaleta.py` (bloque F54 B.1 de `validate`). Sin loop da hard con «decilo en vez de fabricarlo». Coincide con la lección de `garantizar_pico`. |
| 6 | Constantes sin números nuevos | OK | `LOOPS_RANGO=(1,2)` y `RECUERDA_LOOP_CAP=3` citan DECISIONES 16:05. Los otros números salen del handoff. |
| 7 | B.3: `<estructura>` §2 reemplaza (no suma), con la frase literal | OK | `guion_v4.py` y `PROMPT_GUIONISTA_v5_5.md`: «La primera frase de cada cap paga lo que el beat marcado `paga` dejó abierto; la escaleta dice cuál.» Sigue «La última frase de cada cap… deja una puerta abierta», que ya estaba en v5.4. |
| 8 | Bloqueante de pago no dicho (la (f) del handoff) | OK | `pago_no_dicho` es la (h) porque (f) y (g) ya estaban tomadas por la Parte A. Está en `bloqueantes` y frena, sin pasar por `reparar`. Además de los beats con `paga`, mira el `paga_beat` de cada loop; es una extensión de CC, razonable y declarada. |
| 9 | Loops 1–2 + `recuerda_loop` | OK | Ver observación 4 sobre cómo sale el campo en el prompt. |
| 10 | B.2: bloque `<ejemplos>` escrito y pegado en el reporte | FALLA parcial | El bloque está en `lab/hyperframes/f54/EJEMPLOS_v5_6_propuesta.md` (5839 bytes) y no entró al código, como corresponde a la PARADA B.0. Pero `F54_REPORT.md` no se modificó y no tiene sección «Parte B». El pedido decía «pegalo en F54_REPORT.md». `git status` no lo lista y sus 172 líneas terminan en «Adenda de CC». |
| 11 | Nada de B.4/B.5 corrió | OK | `m09_packaging.py` no está en el diff. No existe `lab/hyperframes/f54/antes/`. Los logs de `f41/f54b` son solo suites y ch02, y no hay `01e_pantalla`. |

Observaciones concretas:
1. **Reporte sin Parte B.** `lab/ESTADO_SESION.md` línea 3 dice que el bloque está «propuesto en texto». El pedido de Omar era pegarlo en `F54_REPORT.md`, y eso no está. Solo vive en el archivo suelto. Tampoco están en ese reporte las decisiones de CC de Parte B, que era lo que había que revisar (letra h, recuerda_loop en el esquema, paga 0, loop principal = el primero, etc.). Esas decisiones las deduje del diff y del mensaje del commit.
2. **Ejemplos: lo que se queda.** Escena con sentidos, cita y silencio, hecho concreto y versiones en disputa son idénticos al bloque actual (`guion_v4.py` líneas 232–245). La frase del gancho es literal. También están el cierre de cap 2 con la primera frase del cap 3 que paga, el re-gancho, el pico y el cierre que vuelve a la vela.
3. **Ejemplos: rótulos y contenido nuevos.**
   - Los rótulos cambiaron: «(…la apuesta, lugar y año, vuelta atrás)», «Re-gancho a mitad… sin pagarla», «es la primera de las tres muertes que el gancho prometió». Esas aclaraciones son descripciones nuevas dentro del prompt. No son reglas de estilo, pero tampoco son literales del handoff.
   - Aparecen contenido y cifras nuevas: «Quedaban nueve días» y «tres muertes».
   - Las versiones en disputa (comisión dos, familias tres) no calzan del todo con la promesa de tres muertes. La propuesta lo avisa en «Para mirar».
   - «Tres de ellas no van a ver la primavera» le pone una cifra a la apuesta, pero la segunda frase del gancho sí puede llevar cifras (v5.5 §1), así que no contradice `<estructura>`.
4. **`recuerda_loop` sin texto en el prompt.** Está en el esquema con `description`, pero el SYSTEM de la escaleta no lo menciona. Respeta «cero reglas nuevas», pero depende de que el modelo lea la descripción del esquema. Como es opcional y Omar dijo «sí», puede no salir. En ese caso `validate` lo deja en None sin frenar.
5. **Desvío de `paga` 0 vs `null`.** Es menor y está declarado.

Fuera de alcance: ninguno. El commit 66804dc toca solo los 9 archivos esperados. Los sin commitear (`EJEMPLOS_v5_6_propuesta.md`, `ESTADO_SESION.md`, logs en `f41/f54b`) son los anunciados. `F54_REPORT.md` figura como sin cambios.

Riesgos que el contrato no cubre: (a) `loops` es requerido y la validación es dura. Una ficha sin loop frena la corrida B.5 en vez de degradar. (b) El bloqueante (h) puede dar falso positivo si el guionista paga con otro id, como ya pasó con (d) en el cap 3 de Wittenoom. (c) Si cambia el conteo del ejemplo (tres muertes), hay que revisar el ejemplo de escaleta en `m01a` que menciona la versión en disputa.

## Veredicto actualizado del revisor-handoff (tras releer F54_REPORT.md con la sección Parte B, íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES (actualizado tras releer F54_REPORT.md)

Corrí `pytest -q test_module_f54.py test_module_f6b.py test_module_f16.py` y dio 91 passed. El md5 del handoff coincide (1ac47c9b…). No llamé a ningún modelo.

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | Chascada: una sola oración sobre la promesa en §2, en código y `.md` | OK | `m01a_escaleta.py` (SYSTEM_V2 §2) y `PROMPT_ESCALETA_f54_1.md` quedan solo con «La promesa dice qué va a entender…». La vieja «La promesa es una sola oración…» se borró en ambos (`git show 66804dc`). El test byte-idéntico pasa. |
| 2 | Línea de loops literal del handoff | OK | «Declará 1–2 loops: la pregunta que el video deja abierta, en qué beat se abre y en qué beat se paga. Cada beat dice qué pregunta anterior paga (o ninguna).» Es idéntica a B.1. |
| 3 | DECISIONES 16:05 con el texto literal del handoff más los dos valores | OK | `f72da82`. La línea agrega «loops: 2 · re-gancho: sí, al cierre del cap 3 (campo recuerda_loop) · Omar». |
| 4 | Esquema B.1: `loops` (requerido), `recuerda_loop` (opcional), `paga` | OK, desvío menor | `m01a_escaleta.py`. `paga` es INTEGER con 0 = ninguna; el handoff decía null. El reporte lo declara (decisión 3) y `validate` lo normaliza a None. |
| 5 | Validador: pago posterior a la apertura, principal en cap 7 o pico, `paga` hacia atrás, sin loop es hard | OK | Bloque F54 B.1 de `validate`. Sin loop da hard con «decilo en vez de fabricarlo». |
| 6 | Constantes sin números nuevos | OK | `LOOPS_RANGO=(1,2)` y `RECUERDA_LOOP_CAP=3` citan DECISIONES 16:05. |
| 7 | B.3: `<estructura>` §2 reemplaza (no suma), con la frase literal | OK | `guion_v4.py` y `PROMPT_GUIONISTA_v5_5.md`. La frase es la literal del handoff y la segunda mitad vieja desaparece. |
| 8 | Bloqueante de pago no dicho | OK | `pago_no_dicho` es la (h), porque (f) y (g) ya estaban tomadas por la Parte A. Frena sin pasar por `reparar`. Además de los beats con `paga`, mira el `paga_beat` de cada loop; es una extensión de CC, declarada en el reporte (decisión 5). |
| 9 | B.2: bloque `<ejemplos>` entero pegado en F54_REPORT.md | OK | Ahora sí: `F54_REPORT.md` líneas 249–300 (sección B.2). Verifiqué con diff que el bloque `<ejemplos>` del reporte es idéntico al de `EJEMPLOS_v5_6_propuesta.md`. No está en el código (`guion_v4.py` conserva el Puerto Cardal viejo, líneas 226–252), como pide la PARADA B.0. |
| 10 | Decisiones de CC y salida en texto en el reporte | OK | Sección «Decisiones de CC (Parte B.1/B.3)», líneas 197+. Las 7 decisiones coinciden con el diff. Incluye diffs de ambos prompts, mutaciones del validador y el bloqueante (h). |
| 11 | Nada de B.4/B.5 corrió | OK | `m09_packaging.py` no está en el diff y no existe `lab/hyperframes/f54/antes/`. Los logs de `f41/f54b` son solo suites y ch02. El reporte dice que gastó US$ 0. |

Observaciones:
1. **Veredicto pendiente en el reporte.** La sección «Veredicto de revisor-handoff (Parte B.1/B.3, íntegro)» tiene el placeholder «(se pega abajo)». Este informe es lo que va ahí.
2. **Ejemplos: lo que se queda.** Escena con sentidos, cita y silencio, hecho concreto y versiones en disputa son idénticos al bloque actual (`guion_v4.py` líneas 232–245). La frase del gancho es literal. El cierre del cap 2 con la primera frase del cap 3 que paga, el re-gancho, el pico y el cierre que vuelve a la vela cumplen B.2.
3. **Ejemplos: rótulos y contenido nuevos.**
   - Los rótulos cambiaron, por ejemplo «Re-gancho a mitad… sin pagarla» y «es la primera de las tres muertes que el gancho prometió». Son descripciones nuevas dentro del prompt, no reglas de estilo, pero tampoco literales del handoff.
   - «Quedaban nueve días» y «tres muertes» son números nuevos del caso ficticio, y el reporte los declara.
   - Las versiones en disputa (comisión dos, familias tres) no calzan del todo con la promesa de tres muertes. El reporte lo avisa en «Para mirar».
   - «Tres de ellas no van a ver la primavera» pone una cifra en la apuesta. Es la frase del handoff y `<estructura>` §1 permite cifras en la segunda frase, así que no hay contradicción con `<estructura>` ni con `<voz>`.
4. **`recuerda_loop` sin texto en el prompt.** Está en el esquema con `description` pero el SYSTEM de la escaleta no lo nombra. Respeta «cero reglas nuevas», pero depende de que el modelo lea la descripción. Es opcional y, si no viene, `validate` lo deja en None sin frenar. El reporte lo deja abierto para que decida Omar.
5. **`paga` 0 en vez de null.** Es menor y está declarado.

Fuera de alcance: ninguno. El commit 66804dc toca solo los 9 archivos esperados. Sin commitear quedan `F54_REPORT.md`, `EJEMPLOS_v5_6_propuesta.md`, `ESTADO_SESION.md` y los logs de `f41/f54b`, como se anunció.

Riesgos que el contrato no cubre: (a) `loops` es requerido y la validación es dura. Una ficha sin loop frena B.5 en vez de degradar. (b) El bloqueante (h) puede dar falso positivo si el guionista paga con otro id, como ya pasó con (d) en el cap 3 de Wittenoom. (c) Si cambia el conteo del ejemplo (tres muertes), hay que revisar el ejemplo de escaleta en `m01a`, que menciona la versión en disputa.

## Adenda de CC (Parte B.1/B.3)
- **Fila 10 / observación 1:** el revisor leyó el reporte antes de que esta sección existiera (la escribí mientras corría; le avisé y cerró igual). La sección «Parte B» está arriba, con el bloque `<ejemplos>` entero y las decisiones de CC. Lo demás del veredicto no depende de eso.
- **Observación 3 (rótulos nuevos en `<ejemplos>`):** los rótulos describen la técnica del ejemplo, como los del bloque viejo («Gancho (escena en curso, sin contexto, promesa, vuelta atrás)»). Si el analista prefiere los rótulos viejos tal cual, se cambian al pegar el bloque: la PARADA B.0 es para eso.
- **Observación 4 (`recuerda_loop`):** si en B.5 el modelo no lo trae, se reporta y Omar decide si el prompt lo nombra (sería texto nuevo en el prompt, con su decisión).
- **Riesgo (a):** es lo que pide el handoff («Sin loop → hard, no fabricar; si la ficha no da para 1 loop, PARADA con el motivo»).


---

# Parte B — B.2/B.4/B.5 + adenda · PARADA B (OK del analista 2026-10-29 18:30)

Pedido: OK al bloque `<ejemplos>` tal cual (v5.6, `f54-2`); adenda del handoff (md5 `1732538fdd0b563c34a1325a2f1c01bf`, verificado) con la medida de retención por código y el panel ciego; B.4 y B.5; si la (d) del cap 3 frena, reportarla y seguir. **Gasto de la Parte B: US$ 3,34 de 6** (B.5 2,93: escaleta 1,08 + guionista 1,15 + reparación 0,05 + partición 0,13 + papel 0,51; panel ciego 0,41; `cost_history` desde las 16:17:29 = 3,34). Acumulado F54: US$ 3,34.

## Commits
| commit | qué |
|---|---|
| `8935ef2` | B.2 (`SYSTEM_V5_6`, `f54-2`) + B.4 (m09 lee el GANCHO entero) + tests + `.md` + stickers + MAPA |
| `5de02fc` | B.5: corrida de Wittenoom, `antes/`, `salida_b.py` → `SALIDA_B.md`, `medida_retencion.py` → `MEDIDA_RETENCION.md`, `panel_ciego.py`, log |
| (este) | panel ciego (`PANEL_CIEGO.md/.json`, log), reporte, ESTADO |

## Módulos: antes → después
| módulo | antes | después |
|---|---|---|
| `script_engine/guion_v4.py` | v5.5 (`f54-1`) vigente | **`SYSTEM_V5_6` (`f54-2`)** = v5.5 con el bloque `<ejemplos>` entero de `EJEMPLOS_v5_6_propuesta.md`; el bloque viejo ya no está en el prompt vigente; v5.5 queda como constante (`version="f54-1"`), como todas las versiones anteriores |
| `script_engine/m09_packaging.py` | el hero recibía la narración truncada a 1400 caracteres por cap; la metadata, título + facts + narración | `_bloque_gancho`: «GANCHO (la narración del cap 1 entera; la primera oración del título y el sujeto de la miniatura salen del GANCHO):» como **primer bloque** del usuario del hero (`_hero_user_prompt`) y de la metadata (`_meta_user_prompt`, función nueva y pura; `generate_metadata` la usa); `_narration_for_hero` ya no trunca el cap 1 (los demás caps, igual que antes) |
| `lab/hyperframes/f54/medida_retencion.py` (nuevo, lab) | — | adenda (1): ingredientes viejo \| nuevo por código, sin LLM |
| `lab/hyperframes/f54/panel_ciego.py` (nuevo, lab) | — | adenda (2): 3 modelos × 2 guiones × 7 caps, ciego, pregunta literal, notas y coincidencias |
| `lab/hyperframes/f54/salida_b.py` (nuevo, lab) | — | arma `SALIDA_B.md` |

Tests: `test_module_f54.py` 41 (+2: v5.6 literal y solo cambia `<ejemplos>`; m09 GANCHO primero y cap 1 sin truncar); `test_module_f22.py` (tupla de versiones). `test_m09_packaging.py` (script de lab, no está en la suite): el test del hero pasa; sus 4 cruces (títulos=4, overlays=4, descripción) ya estaban antes de este cambio (mismo conteo con el árbol limpio).

## Corrida B.5 (texto, `lab/hyperframes/f54/b5_run.log`)
`python fase1_5.py --topic 123bbb64-… --batch`: compuerta verde · ficha y canon ya existentes (sin costo) · **escaleta f54-1: 0 bloqueantes al primer intento** (25 reparaciones, 10 a métricas), con 2 loops, 4 beats con `paga` y `recuerda_loop` en el beat 5 (último del cap 3) · guionista f54-2: 19 párrafos, 1979 palabras · reparación: **4 bloqueantes → 4** (la edición del beat 5 se rechazó: «tocó otras frases del párrafo») → **PARADA del guion** reportada, y la cadena siguió (como pidió Omar) · partición: cap 3 y cap 7 acortados por el editor de largo · papel m01e: 2 intentos, 13 fichas · 9 sellos · 3 relojes → `01e_pantalla.md` · PARADA del papel (no aprobado). Cero fotos, cero voz.

### Los 4 bloqueantes del guion nuevo y qué son
| # | código | cap | qué dice | qué pasa de verdad |
|---|---|---|---|---|
| 1 | (d) | 3 | fuera del caso: «Defensor del empleador no identificado» (la cita del arbitraje) | el mismo de la Parte A, previo a esta tanda; Omar pidió no arreglarlo |
| 2 | (h) | 3 | el beat 5 paga la pregunta del beat 3 con D21 («la producción se incrementó en 1961»), que no está en el cap 3 | **falso positivo**: la voz dice «En mil novecientos sesenta y uno, la producción aumentó.» |
| 3 | (h) | 3 | el beat 5 paga el loop L2 con D21 | el mismo dato, el mismo falso positivo |
| 4 | (h) | 6 | el beat 11 paga la pregunta del beat 10 con D10 («el asbesto del vertedero de Colonial alimenta la cuenca del Fortescue») | **falso positivo**: la voz dice «Salía del vertedero de Colonial, arrastrado por el agua, … hasta el río Fortescue.» |

**Hallazgo (no se arregla en esta tanda; a la lista):** `evidence.used_in`, el detector de «lo que la voz dice» que alimenta `ids_usados` y por lo tanto (f), (h) y la medida, **nunca reconoce un dato sin cifra ni fecha** (`anchors` vacío → `any([])` → False): D21, D10, D85 y D42 son imposibles de detectar diga lo que diga la voz. Es la misma razón por la que (f) frenó en la Parte A sobre D42 («barricadas permanentes») y por la que T64 no figuraba en los ids del cap 5 (el año en letras y el hecho en oraciones distintas). Los chequeos nuevos están bien escritos sobre el detector que hay; el detector es el que ve poco. Arreglo general propuesto: para un dato sin ancla, `used_in` por palabras de contenido del hecho (como hace con los eventos con fecha), y los años en letras a cifras antes de buscar el ancla (lo que hace `medida_retencion._anios_a_digitos`). Es cambio de producción con sus tests: handoff aparte.

## Decisiones de CC (B.2/B.4/B.5)
1. **v5.5 queda como constante** (`f54-1`) aunque Omar dijo «el bloque viejo se borra»: el bloque viejo sale del prompt vigente; las versiones anteriores quedan como constantes, como pide el handoff A.1 («como siempre») y como con v5.4, f26-1, etc. Si Omar quiere borrar también la constante v5.5, es un commit de una línea.
2. **m09:** la instrucción literal del handoff va en el rótulo del bloque GANCHO del usuario (formato de salida), no en los sistemas `_HERO_SYSTEM` / `_META_SYSTEM` (cero reglas nuevas en prompts). `_meta_user_prompt` se separó de `generate_metadata` para poder probarla sin red.
3. **Medida (1), «primera apuesta»:** la primera oración del video que dice el dato del pico o el `dato_central` del `paga_beat` del loop principal, con el detector de producción; solo para medir, los años en letras pasan a cifras y, en un evento con fecha, el año y el hecho pueden estar en oraciones vecinas del mismo cap. Con el detector tal cual, las dos corridas daban «nunca».
4. **Medida (1), «el cierre vuelve a la imagen del gancho»:** sí/no = el `dato_central` del beat `cierre` dicho en el cap 7, como define la adenda. En el nuevo es Q24 (una cita: se detecta); en el viejo era D42 (sin ancla: no se detecta nunca).
5. **Panel (2):** una llamada por (modelo, guion, cap) = 42; orden de los dos guiones al azar por cap con semilla fija (reproducible); Claude en `medium`, Flash con esquema; costo medido con `cost_tracker` bajo el id «f54-panel». «Coincidencia» = los 3 marcan la misma oración (primeros 60 caracteres normalizados); «2 de 3» se muestra aparte.
6. **No corrí el revisor sobre la (d)** ni toqué `contamination`: pedido de Omar.

## Salida B (texto; entera en `lab/hyperframes/f54/SALIDA_B.md`)

## 1. Tabla A/B cap por cap

| cap | palabras v | n | años v | n | datos/min v | n | bloqueantes viejo | bloqueantes nuevo (tras la ronda única) |
|---|---|---|---|---|---|---|---|---|
| 1 | 86 | 168 | 1 | 2 | 0.0 | 0.9 | — | — |
| 2 | 302 | 263 | 3 | 3 | 2.4 | 3.3 | — | — |
| 3 | 350 | 368 | 6 | 11 | 1.2 | 2.0 | (d) fuera del caso (descartado en el pool): Defensor del empleador no iden | (d) fuera del caso (descartado en el pool): Defensor del empleador no iden; (h) pago no dicho: el beat 5 paga la pregunta del beat 3 con D21, que no e; (h) pago no dicho: el beat 5 paga el loop L2 con D21, que no está en el ca |
| 4 | 239 | 335 | 3 | 2 | 3.6 | 1.7 | — | — |
| 5 | 344 | 252 | 8 | 5 | 2.5 | 4.0 | — | — |
| 6 | 359 | 278 | 7 | 7 | 0.8 | 1.6 | — | (h) pago no dicho: el beat 11 paga la pregunta del beat 10 con D10, que no |
| 7 | 207 | 249 | 3 | 5 | 2.1 | 3.5 | (f) cierre no dicho: el dato central D42 del beat 14 (cierre) no está en e | — |
| **total** | 1887 | 1913 | 31 | 35 | | | 2 | 4 |

Guion nuevo: bloqueantes antes de la ronda única 4 → después 4 · PARADA del guion: True.

Bloqueantes del crudo nuevo (antes de reparar):

- cap 3 beat 5 (d): fuera del caso (descartado en el pool): Defensor del empleador no identificado — ««El mero hecho de que haya nubes de polvo no significa que ese polvo sea peligroso», dijo el defensor del empleador en m»
- cap 3 beat 5 (h): pago no dicho: el beat 5 paga la pregunta del beat 3 con D21, que no está en el cap 3
- cap 6 beat 11 (h): pago no dicho: el beat 11 paga la pregunta del beat 10 con D10, que no está en el cap 6
- cap 3 beat 5 (h): pago no dicho: el beat 5 paga el loop L2 con D21, que no está en el cap 3

### 2. Los dos cap 1, lado a lado

| viejo (f26-1 / f25-1) | nuevo (f54-1 / f54-2) |
|---|---|
| Un hombre joven posa para una foto con el pie envuelto en una venda blanca. Detrás, tierra roja y paredes de chapa. En el retrato de familia todos miran a cámara menos el pie: está vendado, y la herida que le hizo un trozo de amianto no cierra. El hombre se llama Daniel Écija y es minero. Vino de Madrid. Wittenoom, Australia Occidental, mil novecientos sesenta y dos. Para entender ese pie hay que volver a un baile en Madrid, un año antes de la foto. | Un hombre joven posa de pie para un retrato, con un pie envuelto en vendas. Vivió diez meses en el pueblo donde le tomaron esa foto y murió de esos diez meses casi treinta años después, en Madrid; había gente con cargo y con firma que sabía desde mil novecientos cuarenta y ocho lo que hacía ese polvo, y más de tres millones de toneladas siguen donde las dejaron. La foto es sepia, como las demás que hay sobre la mesa. Una mujer mayor las ordena, una por una. Cuenta que a su marido le cayó un trozo de amianto en el pie y que la herida no cerraba; por eso la venda. «Me pegué a mi marido, como una niña pequeña», dice la mujer que ordena las fotos. El hombre del pie vendado se llamaba Daniel Écija, minero emigrante español. Wittenoom, Australia Occidental, mil novecientos sesenta y dos. Para entender ese retrato hay que volver a Madrid, a un baile, un año antes de que lo tomaran. |

Promesa del gancho — viejo: «En el retrato de familia todos miran a cámara menos el pie: está vendado, y la herida que le hizo un trozo de amianto no cierra.» · nuevo: «Daniel Écija vivió diez meses en Wittenoom. Murió de eso casi treinta años después, en Madrid. Esta es la historia de quién sabía, desde mil novecientos cuarenta y ocho, lo que hacía ese polvo, y de por qué tres millones de toneladas siguen donde las dejaron.»

### 3. Loops declarados con sus pagos (escaleta nueva)

- **Loop 1** (L1): «¿Por qué un hombre que vivió diez meses en un pueblo del desierto muere de ese pueblo casi treinta años después y a medio mundo de distancia?» — se abre en el beat 1 (cap 1, D85) · se paga en el beat 9 (cap 5, D89: Si diez meses bastaron para él, ¿qué pasa con los que se quedaron años, y con los niños que se lo metían en la boca?)
- **Loop 2** (L2): «¿Qué sabía la empresa del polvo cuando fue a Europa a reclutar a estas familias?» — se abre en el beat 3 (cap 2, Q14) · se paga en el beat 5 (cap 3, D21: ¿Cómo se recluta gente en Europa para un lugar así, y qué se les cuenta?)

Beats con `paga` (4):
- beat 5 (cap 3, D21) paga la pregunta del beat 3: «¿De qué está hecho ese polvo que nadie había visto en esa cantidad?»
- beat 9 (cap 5, D89) paga la pregunta del beat 1: «¿Qué le pasó al hombre del pie vendado, y por qué una herida que no cierra importa en una historia sobre un pueblo borrado del mapa?»
- beat 11 (cap 6, D10) paga la pregunta del beat 10: «Si borrar el nombre es el fin del episodio, ¿qué pasa con el polvo que sigue ahí?»
- beat 12 (cap 7, T92) paga la pregunta del beat 11: «Si se sabe cómo encapsularlo y cuánto cuesta, ¿por qué no se ha hecho nunca?»

`recuerda_loop`: beat 5 · «A ese molino cubierto de polvo, a fines de mil novecientos sesenta y dos, iba a entrar un recién casado de Madrid que llevaba cuatro días de matrimonio cuando subió al barco.»

### 4. Los 7 títulos

| cap | viejo | nuevo |
|---|---|---|
| 1 | El pie que no cura | La herida que no cerró |
| 2 | El polvo de la tierra | Promesas y polvo |
| 3 | La verdad silenciada | Peligro silenciado |
| 4 | Jugar con veneno | El polvo lo cubría todo |
| 5 | El tiempo de matar | La factura del tiempo |
| 6 | Borrar el problema | Un pueblo, polvo eterno |
| 7 | Una herida abierta | El costo sin fin |

### 5. El papel (01e_pantalla.md, nuevo)

# Guion de pantalla en papel — 123bbb64-9fca-4395-8bf4-57d60e219ef1

`m01e_pantalla` m01e-6 (md5 del prompt `3b98aef1d8595124967ac7a85b75bab7`) · claude-sonnet-5-5 medium · 2 intento(s) · US$ 0.5103 · tokens de entrada 52702

Segundos por palabra 0.34 (mediana de 347 oraciones de 16 caps del narrador N9Z5MLTIaHFLflaLtbDi) · tope US$ 1.0 (respaldo (el perfil no trae costos.m01e_tope_usd)) · intento 1: in 52702 · out 25700 · US$ 0.3624 · intento 2: in 58538 · out 3082 · US$ 0.1479

Totales: 13 fichas · 9 sellos · 3 relojes · 23 descartados

### ch01 — La herida que no cerró

- beat 1 · gancho · PICO · ficha **D90** [normal] «MUERTOS POR WITTENOOM · Se calcula que superan los 4.000» en [1] sobre «polvo» (53/90 car.) · respaldo: «puede ser superior a 4.000» · año — / relato 1948 · aporta: La voz habla de un hombre y de las toneladas que quedan, pero nunca dice cuánta gente murió por el pueblo. · sello **MEMORIA** en [3]
- relojes: —

### ch02 — Promesas y polvo

- beat 2 · planteo · ficha **D83** [normal] «EL PLAN MIGRATORIO · Se llamó Operación Canguro, desde 1958» en [3] sobre «acuerdo» (56/90 car.) · respaldo: «iniciado en 1958, llamado Operación Canguro» · año 1958 / relato 1950 · juzgado por el autor: otro hecho {'spoiler': ['1958']} · aporta: La voz dice que cruzaron ocho mil españoles, pero no cómo se llamaba el acuerdo ni cuándo empezó. · sello **SILENCIO** en [8]
- beat 3 · planteo · PICO · ficha **D82** [normal] «AISLADO DEL MUNDO · A unos 1.400 kilómetros de Perth» en [15] sobre «desierto» (49/90 car.) · respaldo: «a unos 1.400 kilómetros de Perth» · año — / relato 1950 · aporta: Pone una distancia al aislamiento: la voz solo dice 'en medio del desierto'. · sello **AMENAZA** en [20]
- relojes: 16 SEP 1961 en [0], 20 SEP 1962 en [2]

### ch03 — Peligro silenciado

- beat 4 · escalada · PICO · ficha **Q45** [cita] «SU PRONÓSTICO · la cosecha más rica y letal de casos de asbestosis» — Eric Saint (autor: modelo) en [5] sobre «carta» (no está en la oración) (78/90 car.) · respaldo: «la cosecha más rica y letal de casos de asbestosis en la literatura mundial» · año 1948 / relato 1948 · aporta: Lo que Saint predijo en su advertencia. La voz solo cita cómo lo trataron después. · sello **ALARMA** en [3]
- beat 5 · giro · ficha **D78** [normal] «YA SE SABÍA · A mediados de la década de 1950 se descubrió que el asbesto da cáncer» en [14] sobre «mesotelioma» (80/90 car.) · respaldo: «A mediados de la década de 1950, los investigadores descubrieron los peligros cancerígenos del mineral de asbesto.» · año 1955 / relato 1962 · aporta: La voz cuenta el primer mesotelioma de 1962, pero no que el riesgo de cáncer se conocía desde los años 50. · sello **INMINENTE** en [16]
- relojes: —

### ch04 — El polvo lo cubría todo

- beat 6 · escalada · PICO · ficha **Q19** [cita] «LO QUE NO SABÍAN · Nadie nos avisó de nada» — Víctor Calvo (autor: modelo) en [5] sobre «deshilachaban» (56/90 car.) · respaldo: «Nadie nos avisó de nada.» · año — / relato 1962 · aporta: Cierra el testimonio de Calvo con la frase que la voz no dice: a los niños nadie les advirtió. · sello **CALMA** en [8]
- beat 7 · escalada · ficha **D88** [normal] «SE QUEDARON MÁS · La familia de Ramón vivió allí unos dos años y medio» en [14] sobre «Ramón» (67/90 car.) · respaldo: «vivió en Wittenoom unos dos años y medio» · año — / relato 1965 · juzgado por el autor: otro hecho {'no_dicho': ['Ramón']} · aporta: Cuánto se quedaron los amigos de los Écija, para contrastar con los diez meses que la voz cuenta después. · sello —
- relojes: 7 JUL 1963 en [18]

### ch05 — La factura del tiempo

- beat 8 · giro · ficha **D51** [normal] «LO QUE SACÓ LA MINA · 131.000 toneladas de amianto azul» en [1] sobre «anunció» (52/86 car.) · respaldo: «La mina de Wittenoom produjo 131.000 toneladas de crocidolita» · año 1966 / relato 1966 · aporta: Pone cifra a lo que produjo la mina que se cerraba; la voz solo dice el motivo y el número de personas. · sello —
- beat 9 · pico · PICO · ficha **D23** [papel] «ANTES QUE DANIEL · Para 1989, más de 500 antiguos trabajadores y residentes habían muerto» en [15] sobre «cuenta» (86/90 car.) · respaldo: «Para 1989, más de 500 antiguos trabajadores y residentes de Wittenoom habían muerto» · año 1989 / relato 1991 · aporta: Muestra que Daniel no fue el primero: cuando murió ya había más de 500 muertos documentados. La voz no lo dice. · sello **COLAPSO** en [19]
- relojes: —

### ch06 — Un pueblo, polvo eterno

- beat 10 · respiro · ficha **D26** [normal] «EL ÁREA CERRADA · El sitio contaminado más grande del hemisferio sur» en [6] sobre «área» (65/86 car.) · respaldo: «sitio contaminado más grande del hemisferio sur» · año — / relato 2006 · aporta: Pone tamaño a lo que las barricadas encierran: la voz solo dice que el área no es segura. · sello **AVISO** en [8]
- beat 11 · revelacion · PICO · ficha **D94** [normal] «LO QUE PAGÓ CSR · 18,3 millones de dólares a 200 afectados» en [13] sobre «propiedad» (55/90 car.) · respaldo: «la empresa CSR pagó 18,3 millones de dólares australianos en indemnizaciones a 200 afectados» · año 1989 / relato 2006 · aporta: La voz habla de quién quedó con los relaves, pero no de lo que pagó la empresa por los enfermos. · sello **RABIA** en [16]
- relojes: —

### ch07 — El costo sin fin

- beat 12 · consecuencia · PICO · ficha **T86** [normal] «LOS MÁS AFECTADOS · Banjima: la mayor incidencia de cáncer por asbesto per cápita del mundo» en [6] sobre «Banjima» (88/90 car.) · respaldo: «el pueblo Banjima sufre la mayor incidencia per cápita de cáncer por asbesto del mundo» · año 2016 / relato 2026 · aporta: Dice cuánto ha golpeado la enfermedad a los Banjima, algo que la voz no cuenta. · sello —
- beat 13 · cierre · ficha **D109** [normal] «CONTADOS EN 1986 · 94 mesoteliomas en 6912 extrabajadores» en [10] sobre «escáner» (54/71 car.) · respaldo: «Para finales de 1986, se habían registrado 94 casos de mesotelioma, 141 de cáncer de pulmón y 356 reclamos por asbestosis en una cohorte de 6912 antiguos trabajadores de Wittenoom» · año 1986 / relato 2026 · aporta: Pone cifra a los casos ya registrados entre los trabajadores, algo que la voz no dice al hablar de los controles médicos. · sello —
- relojes: —

### Lo que cayó

- (nada)

### Reintento: los motivos que se le mandaron al autor

- Q02 (ch06 beat 10) «LA ADVERTENCIA · desaconseja firmemente TODOS los viajes»: cita_sin_fecha: cita sin fecha: su autor («State Government», Gobierno estatal) no aparece en la oración [6] ni en sus vecinas
- D83 (ch02 beat 2, oración [3]) «EL PLAN MIGRATORIO · Se llamó Operación Canguro, desde 1958»: la voz dice «1958» en una oración posterior en ch03 [12] («En mil novecientos cincuenta y ocho, otro inspector resumió la mina en una palabra: una tragedia.»); ¿es el mismo hecho? si no, mantenelo
- D88 (ch04 beat 7, oración [14]) «SE QUEDARON MÁS · La familia de Ramón vivió allí unos dos años y medio»: la voz dice «Ramón» en la oración ancla o en una vecina en ch04 [14] («Tres meses antes, en marzo, Milagros Barroso había dado a luz en ese mismo pueblo a John Patrick; María recuerda que ella y Daniel se hicieron íntimos amigos de Milagros y de Ramón de Juan, que hacía jornadas de dieciséis horas.»); ¿es el mismo hecho? si no, mantenelo
- Q25: dijiste que la voz lo dice («La voz cita esa frase de María en la oración 5 del capítulo 1.»); la voz de ch01 no dice «2» («Me pegué a mi marido, como una niña pequeña. Pero estaba orgullosa. Me había enamorado de ese hombre y confiaba en el futuro… aunque estuviera tan lejos. En España no teníamos nada, ninguno de los dos.»): vuelve a ser candidato
- D28: dijiste que la voz lo dice («La voz cuenta las demoliciones y los cierres entre 1986 y 1992.»); la voz de ch06 no dice «Wittenoom» («Entre 1986 y 1992 se demolieron casas y edificios y se cerraron la escuela, el puesto de enfermería y la comisaría en Wittenoom.»): vuelve a ser candidato
- D95: dijiste que la voz lo dice («La voz dice los 1.500 millones del reclamo.»); la voz de ch07 no dice «1.500» («El pueblo aborigen banjima reclama 1.500 millones de dólares australianos al Ejecutivo por la contaminación.»): vuelve a ser candidato
- el beat 11 de ch06 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D23 («Recuento oficial de muertes hasta 1989 (más de 500): documento, no voz.»), D94 («Acuerdo de indemnización de CSR de 1989, 18,3 millones a 200 afectados: cifra de archivo.»)
- el beat 13 de ch07 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D109 («Cohorte de 6.912 trabajadores y 94 mesoteliomas hasta 1986: dato de estudio, va a pantalla sobre los controles médicos.»)

### Preguntas y respuesta del autor

- D83 {'spoiler': ['1958']}: la mantuvo en ch02 beat 2 [3]: otro hecho
- D88 {'no_dicho': ['Ramón']}: la mantuvo en ch04 beat 7 [14]: otro hecho

### Reintento parcial: 1 vuelta(s)

#### Vuelta 1 · US$ 0.1479

- beats que podía cambiar: ch02 beat 2, ch04 beat 7, ch06 beat 10, ch06 beat 11, ch07 beat 13
- motivos:
  - Q02 (ch06 beat 10) «LA ADVERTENCIA · desaconseja firmemente TODOS los viajes»: cita_sin_fecha: cita sin fecha: su autor («State Government», Gobierno estatal) no aparece en la oración [6] ni en sus vecinas
  - D83 (ch02 beat 2, oración [3]) «EL PLAN MIGRATORIO · Se llamó Operación Canguro, desde 1958»: la voz dice «1958» en una oración posterior en ch03 [12] («En mil novecientos cincuenta y ocho, otro inspector resumió la mina en una palabra: una tragedia.»); ¿es el mismo hecho? si no, mantenelo
  - D88 (ch04 beat 7, oración [14]) «SE QUEDARON MÁS · La familia de Ramón vivió allí unos dos años y medio»: la voz dice «Ramón» en la oración ancla o en una vecina en ch04 [14] («Tres meses antes, en marzo, Milagros Barroso había dado a luz en ese mismo pueblo a John Patrick; María recuerda que ella y Daniel se hicieron íntimos amigos de Milagros y de Ramón de Juan, que hacía jornadas de dieciséis horas.»); ¿es el mismo hecho? si no, mantenelo
  - Q25: dijiste que la voz lo dice («La voz cita esa frase de María en la oración 5 del capítulo 1.»); la voz de ch01 no dice «2» («Me pegué a mi marido, como una niña pequeña. Pero estaba orgullosa. Me había enamorado de ese hombre y confiaba en el futuro… aunque estuviera tan lejos. En España no teníamos nada, ninguno de los dos.»): vuelve a ser candidato
  - D28: dijiste que la voz lo dice («La voz cuenta las demoliciones y los cierres entre 1986 y 1992.»); la voz de ch06 no dice «Wittenoom» («Entre 1986 y 1992 se demolieron casas y edificios y se cerraron la escuela, el puesto de enfermería y la comisaría en Wittenoom.»): vuelve a ser candidato
  - D95: dijiste que la voz lo dice («La voz dice los 1.500 millones del reclamo.»); la voz de ch07 no dice «1.500» («El pueblo aborigen banjima reclama 1.500 millones de dólares australianos al Ejecutivo por la contaminación.»): vuelve a ser candidato
  - el beat 11 de ch06 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D23 («Recuento oficial de muertes hasta 1989 (más de 500): documento, no voz.»), D94 («Acuerdo de indemnización de CSR de 1989, 18,3 millones a 200 afectados: cifra de archivo.»)
  - el beat 13 de ch07 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D109 («Cohorte de 6.912 trabajadores y 94 mesoteliomas hasta 1986: dato de estudio, va a pantalla sobre los controles médicos.»)
- aplicados: ch06 beat 10 (ficha), ch06 beat 11 (ficha), ch07 beat 13 (ficha)

### Motivos sin beat (no hubo reintento)

- Q25: dijiste que la voz lo dice («La voz cita esa frase de María en la oración 5 del capítulo 1.»); la voz de ch01 no dice «2» («Me pegué a mi marido, como una niña pequeña. Pero estaba orgullosa. Me había enamorado de ese hombre y confiaba en el futuro… aunque estuviera tan lejos. En España no teníamos nada, ninguno de los dos.»): vuelve a ser candidato
- D28: dijiste que la voz lo dice («La voz cuenta las demoliciones y los cierres entre 1986 y 1992.»); la voz de ch06 no dice «Wittenoom» («Entre 1986 y 1992 se demolieron casas y edificios y se cerraron la escuela, el puesto de enfermería y la comisaría en Wittenoom.»): vuelve a ser candidato
- D95: dijiste que la voz lo dice («La voz dice los 1.500 millones del reclamo.»); la voz de ch07 no dice «1.500» («El pueblo aborigen banjima reclama 1.500 millones de dólares australianos al Ejecutivo por la contaminación.»): vuelve a ser candidato

### Cierre del reintento

- cerró por: **sin beat** (después de 1 vuelta)
- cortado al cerrar, sin preguntarle al autor: (nada)

### Descartados por el modelo

- D85 [otro]: Dato central del gancho que no figura en el archivo; se usó D90, que la voz no dice.
- Q25 [voz_lo_dice]: La voz cita esa frase de María en la oración 5 del capítulo 1. — **falso: la voz no dice ['2']**
- T34 [voz_lo_dice]: La voz cuenta el baile del 16 de septiembre de 1961.
- Q13 [spoiler]: Adelanta la amistad con Milagros y Ramón, que la voz cuenta en el capítulo 4.
- Q14 [voz_lo_dice]: La voz cita la travesía de Calvo casi completa.
- Q15 [voz_lo_dice]: La voz cuenta el avión, la tierra roja y el polvo.
- D92 [voz_lo_dice]: La voz dice que Saint advirtió por escrito en 1948.
- D21 [voz_lo_dice]: La voz dice que en 1961 la producción aumentó; la ficha solo repetiría eso.
- Q44 [voz_lo_dice]: La voz cita la frase de los relaves en la escuela.
- T41 [voz_lo_dice]: La voz cuenta el bautizo del 7 de julio de 1963 y la partida.
- T49 [voz_lo_dice]: La voz ya dice que la razón fue económica; se prefirió el dato de producción.
- D89 [voz_lo_dice]: La voz dice nueve meses, cincuenta y cinco años y la muerte en Madrid.
- Q23 [otro]: La voz cita su primera frase y no cabía una ficha de cita en la oración libre.
- D28 [voz_lo_dice]: La voz cuenta las demoliciones y los cierres entre 1986 y 1992. — **falso: la voz no dice ['Wittenoom']**
- Q07 [voz_lo_dice]: La voz cita 'el fin de un período oscuro'.
- D58 [otro]: Cifra de costo válida, pero en el beat 11 se prefirió D146.
- D10 [otro]: Dato central del beat 11 que no figura en el archivo.
- T92 [voz_lo_dice]: La voz cuenta la visita de Orellana en 2023.
- D95 [voz_lo_dice]: La voz dice los 1.500 millones del reclamo. — **falso: la voz no dice ['1.500']**
- Q24 [voz_lo_dice]: La voz cita la frase del policía.
- D109 [otro]: Se prefirió D110, que sugiere mejor la escala.
- D87 [voz_lo_dice]: La voz dice 'diez meses en total'.
- D56 [spoiler]: Introduce a los aborígenes que usan las gargantas antes de que la voz presente a los Banjima.


## Medida de retención (adenda 18:30, 1): viejo | nuevo, por código (`MEDIDA_RETENCION.md`)

| ingrediente | viejo | nuevo |
|---|---|---|
| segundos hasta la primera apuesta | 511.3 s (cap 5, pico (T64)) | 550.0 s (cap 5, loop principal (D89)) |
| loops abiertos / pagados | 0 declarado(s) | 2 declarado(s) · loop L1 (D89): pagado; loop L2 (D21): NO pagado; beat 5 paga (D21): NO pagado; beat 9 paga (D89): pagado; beat 11 paga (D10): NO pagado; beat 12 paga (T92): pagado |
| re-gancho | no declarado | sí (cap 3, min 5.33, parecido 1.0) |
| el cierre vuelve a la imagen del gancho | NO (D42 en el cap 7) | sí (Q24 en el cap 7) |

| cap | palabras v | n | años v | n | datos/min v | n |
|---|---|---|---|---|---|---|
| 1 | 86 | 168 | 1 | 2 | 0.0 | 0.9 |
| 2 | 302 | 263 | 3 | 3 | 2.4 | 3.3 |
| 3 | 350 | 368 | 6 | 11 | 1.2 | 2.0 |
| 4 | 239 | 335 | 3 | 2 | 3.6 | 1.7 |
| 5 | 344 | 252 | 8 | 5 | 2.5 | 4.0 |
| 6 | 359 | 278 | 7 | 7 | 0.8 | 1.6 |
| 7 | 207 | 249 | 3 | 5 | 2.1 | 3.5 |


Lectura de CC: la escaleta nueva declara 2 loops y 4 pagos; el código ve pagados L1 (D89, cap 5) y los pagos de los beats 9 (D89) y 12 (T92), y NO ve L2 ni los beats 5 y 11 por el hallazgo de arriba (D21 y D10 sin ancla; la voz sí los dice). Ningún pago cae en la **primera oración** del cap (las primeras oraciones de los caps 3, 5 y 7: «Se llamaba amianto azul…», «Funcionó tres años más.», «Se llamaba Maitland Parker…»): el guionista no siguió `<estructura>` §2 al pie de la letra. El re-gancho está declarado y dicho (cap 3, min 5,33, textual). La «primera apuesta» por código da 550 s en el nuevo (D89 en el cap 5), pero la segunda oración del cap 1 nuevo ya nombra lo que está en juego («murió de esos diez meses casi treinta años después, en Madrid») sin el año 1991 ni la palabra mesotelioma: el detector, anclado en el año, no la cuenta. Años por cap: el cap 3 nuevo dice **11** (viejo 6); datos/min suben en 5 de 7 caps.

## Panel ciego (adenda 18:30, 2; `PANEL_CIEGO.md`, US$ 0,41)
Pregunta literal por cap: «Estás escuchando este capítulo. ¿En qué oración dejarías de escuchar y por qué? Al final, una nota de 1 a 10 de cuánto te quedarías hasta el siguiente capítulo.» Modelos: Gemini Flash, Sonnet 5.5, Opus 5.5; los dos guiones sin marcar, orden al azar por cap.

#### Notas (1–10) por cap y modelo

| cap | gemini-flash v | gemini-flash n | claude-sonnet-5-5 v | claude-sonnet-5-5 n | claude-opus-5-5 v | claude-opus-5-5 n | media v | media n |
|---|---|---|---|---|---|---|---|---|
| 1 | 10 | 9 | 7 | 7 | 8 | 8 | 8.3 | 8.0 |
| 2 | 10 | 10 | 7 | 6 | 8 | 8 | 8.3 | 8.0 |
| 3 | 9 | 10 | 6 | 6 | 8 | 8 | 7.7 | 8.0 |
| 4 | 9 | 9 | 7 | 5 | 9 | 8 | 8.3 | 7.3 |
| 5 | 10 | 10 | 6 | 8 | 8 | 8 | 8.0 | 8.7 |
| 6 | 8 | 9 | 6 | 6 | 7 | 7 | 7.0 | 7.3 |
| 7 | 9 | 9 | 8 | 5 | 7 | 7 | 8.0 | 7.0 |
| **video** |  |  |  |  |  |  | **7.9** | **7.8** |


#### Coincidencias (los 3 modelos marcan la misma oración de abandono)

| cap | viejo | nuevo |
|---|---|---|
| 1 | 2 de 3 | no |
| 2 | no | no |
| 3 | no | no |
| 4 | no | no |
| 5 | 2 de 3 | no |
| 6 | 2 de 3 | no |
| 7 | no | no |

Orden en que cada modelo leyó los dos guiones por cap (ciego; semilla fija): cap 1: nuevo → viejo, cap 2: viejo → nuevo, cap 3: viejo → nuevo, cap 4: viejo → nuevo, cap 5: viejo → nuevo, cap 6: viejo → nuevo, cap 7: nuevo → viejo



### Oración de abandono del cap 1 (las 42 filas están en `PANEL_CIEGO.md`)
### viejo
| cap | modelo | oración de abandono | por qué |
|---|---|---|---|
| 1 | gemini-flash | Para entender ese pie hay que volver a un baile en Madrid, un año antes de la foto. | Esta oración funciona como un excelente gancho, creando una intriga sobre el pasado del personaje y cómo se conecta con su situación actual. Me deja con ganas d |
| 1 | claude-sonnet-5-5 | Para entender ese pie hay que volver a un baile en Madrid, un año antes de la foto. | Hasta ahí el arranque engancha: la imagen del pie vendado, la herida que no cierra y el contraste entre Madrid y Wittenoom crean intriga. Pero esa última frase  |
| 1 | claude-opus-5-5 | Ninguna. Si tuviera que señalar el punto de mayor riesgo, sería «Vino de Madrid.», la única frase que suena a ficha informativa y no a image | El capítulo es breve y está bien construido. Abre con una imagen concreta y extraña: la venda blanca, la tierra roja, la chapa. Luego introduce una torsión inge |
### nuevo
| cap | modelo | oración de abandono | por qué |
|---|---|---|---|
| 1 | gemini-flash | Wittenoom, Australia Occidental, mil novecientos sesenta y dos. | Porque en este punto ya se ha revelado la identidad del hombre, la causa de su herida y el contexto espacio-temporal de la foto, cerrando el marco inicial del r |
| 1 | claude-sonnet-5-5 | Para entender ese retrato hay que volver a Madrid, a un baile, un año antes de que lo tomaran. | Hasta ahí me tenía: la foto, el pie vendado y esa frase sobre el polvo que sabían peligroso y las tres millones de toneladas que siguen allí. Pero la última ora |
| 1 | claude-opus-5-5 | No dejaría de escuchar. El punto de mayor riesgo es la segunda oración: «Vivió diez meses en el pueblo donde le tomaron esa foto y murió de  | Escuchada en voz alta, esa oración pide demasiado de golpe: un pueblo sin nombre, una muerte diferida, unos responsables, un año y una cifra de toneladas, todo  |

Lectura de CC: **el panel no distingue los dos guiones** (media del video 7,9 viejo contra 7,8 nuevo; Flash puntúa 9–10 a casi todo, Sonnet 5–8, Opus 7–9). En el cap 1 los tres leen el viejo y el nuevo como «funciona»; Opus señala en el nuevo la segunda oración («pide demasiado de golpe: un pueblo sin nombre, una muerte diferida, unos responsables, un año y una cifra de toneladas») y Sonnet la vuelta atrás final en los dos. Las coincidencias de los 3 son 0 en los dos guiones; «2 de 3» aparece en los caps 1, 5 y 6 del viejo y en ninguno del nuevo. Informa, no frena.

## Lo que queda abierto (Parte B)
1. **El detector `evidence.used_in` no ve datos sin ancla: sin cifra, sin fecha, o con fecha sin guion como D21 `fecha='1961'`** (ni años en letras): (f) y (h) frenan por eso con la voz diciendo el dato; la promesa del gancho nuevo y la primera apuesta tampoco se miden bien. Handoff aparte, con tests.
2. **La promesa del gancho de la escaleta nueva** empieza «Esta es la historia de quién sabía…»: voz de tráiler, que `<voz>` del guionista prohíbe y el guionista no copió (dijo «había gente con cargo y con firma que sabía…»). La escaleta no tiene esa regla; el analista decide si es ejemplo (el `promesa_gancho` del `<ejemplo>` de la escaleta sigue diciendo «Esta es la historia de quién decidió que no llegara») o nada.
3. **Ningún pago en la primera oración del cap**: `<estructura>` §2 nuevo no se cumplió en la corrida; (h) no lo mide (mide que el dato esté en el cap). Si Omar lo quiere chequeado, es un bloqueante más o una métrica.
4. **El cap 3 nuevo dice 11 años**; el tope de años/cap sigue sin decidir (solo métrica).
5. La (d) contaminación del cap 3 (previa) sigue frenando el guion; `reparar` no la pudo editar (tocaba otras frases).
6. El guion nuevo quedó con **PARADA del guion** (4 bloqueantes, 3 falsos) y PARADA del papel: nada pasa a voz ni a fotos sin Omar.
7. De la Parte A: dedupe Q12/Q25, las «6 frases».

**PARADA B.** El analista califica 1–10 y Omar decide si la versión nueva pasa a fotos (F51d-B) o se vuelve a correr con los arreglos.

## Veredicto de revisor-handoff (Parte B.2/B.4/B.5, íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | v5.6 = v5.5 con solo `<ejemplos>` cambiado, idéntico al OK del analista | OK | `guion_v4.py` SYSTEM_V5_6, PROMPT_VERSION `f54-2`. `test_guion_v5_6_literal_y_solo_cambia_ejemplos` exige que el bloque esté en el sistema y que, al cambiarlo por el viejo, salga el v5.5 exacto. `pytest test_module_f54.py test_module_f22.py`: 87 passed, 8 skipped. |
| 2 | «El bloque viejo se borra» | PARCIAL | Sale del prompt vigente, pero sigue en `SYSTEM_V5_5` (`version="f54-1"`, `guion_v4.py` `system()`) y en las versiones anteriores. Omar dijo «lo viejo se borra, no se apaga por flag», y el selector por versión es en la práctica un flag. CC lo declara (decisión 1 del reporte, «un commit de una línea»), pero no obedece el texto literal. Decide Omar. |
| 3 | B.4: GANCHO primer bloque en hero y metadata, con la instrucción literal | OK | `m09_packaging.py`: `GANCHO_INSTRUCCION` es la frase literal del handoff. `_bloque_gancho` va primero en `_hero_user_prompt` y en `_meta_user_prompt`. Test `test_m09_gancho_primero…`. |
| 4 | B.4: cap 1 sin truncar, sin texto nuevo en los sistemas | OK | `_narration_for_hero` solo trunca `n != 1`. El diff no toca `_HERO_SYSTEM` ni `_META_SYSTEM`. |
| 5 | B.5: corrida hasta `01e_pantalla.md`, cero fotos y voz | OK | `b5_run.log`: escaleta f54-1, guion f54-2, papel «13 fichas · 9 sellos · 3 relojes». Termina en «PARADA del papel». |
| 6 | Viejos guardados en `f54/antes/` | OK | `antes/` tiene 11 archivos (escaleta, guion, narración, pantalla). El cap 1 viejo tiene 86 palabras y el nuevo 168. |
| 7 | La (d) se reporta y no se arregla | OK | Reporte, tabla de bloqueantes, fila 1. No se tocó `contamination`. |
| 8 | Tope US$ 6 | OK | Sumé `data/cost_history.json` desde 2026-10-29T16:17:29: US$ 3,336 (3,13 de la corrida B.5 y 0,41 del panel con redondeos). Coincide con el «3,34» del reporte. |
| 9 | Salida B completa (tabla A/B, los dos cap 1, loops con pagos, 7 títulos, papel) | OK | `SALIDA_B.md` y reporte, secciones 1 a 5. |
| 10 | Medida de retención (1) por código, viejo \| nuevo | OK | `medida_retencion.py` y `MEDIDA_RETENCION.md`: primera apuesta, loops, re-gancho (cap 3, min 5,33), años/cap, datos/min, cierre a la imagen. |
| 11 | Relajaciones del detector declaradas | PARCIAL | Están en el docstring (`medida_retencion.py:53-54, 80, 98`) y en la decisión 3 del reporte. Pero `MEDIDA_RETENCION.md`, el artefacto que se lee, no las menciona (grep sin resultados). Se aplican igual a viejo y nuevo, y solo en el script de medida. |
| 12 | Panel ciego (2) | OK | `panel_ciego.py`: la pregunta literal es idéntica a la adenda. Los 3 modelos hacen 42 llamadas, con orden al azar (semilla 54) y sin marcar. Salidas: notas, oraciones de abandono, tabla de coincidencias. Costo US$ 0,408, medido en `cost_history`. |
| 13 | Hallazgo `used_in` → 3 falsos positivos (h) | OK, confirmado | Lo corrí. Con el pool: D21 (`tipo=fecha`, `fecha='1961'`, sin guion) y D10 (`lugar`) dan `anchors()==[]`, entonces `used_in` es False aunque la voz lo diga. Cap 3: «En mil novecientos sesenta y uno, la producción aumentó.» Cap 6: «Salía del vertedero de Colonial… hasta el río Fortescue.» Matiz: el reporte dice «sin cifra ni fecha», pero D21 tiene un año; falla porque `fecha` no tiene «-» (`evidence.py:80-100`). |
| 14 | Informa, no frena | OK | El panel y la medida no bloquean nada. |

Observación adicional: la medida da «primera apuesta» 550 s en el nuevo, un valor sobre todo del detector. El reporte lo admite. Con L2 y los beats 5 y 11 marcados «NO pagado» por la misma ceguera, esa fila de la medida no sirve como evidencia tal cual.

Fuera de alcance: ninguno. Los commits tocan solo `script_engine/guion_v4.py` y `m09_packaging.py`, los dos tests, `lab/hyperframes/f54/*`, `f41/f54c` (logs), stickers, MAPA y ESTADO. Los archivos modificados sin commit (`diag_234_cap4.py`, `lab/TOPE_TANDA.json`, `f28a.log`) ya estaban así en el snapshot inicial.

Riesgos que el contrato no cubre:
- El guion nuevo queda con PARADA (4 bloqueantes, 3 de ellos falsos). Mientras `used_in` no se arregle, (f) y (h) volverán a frenar guiones buenos.
- Ningún pago cae en la primera oración del cap. Nada lo chequea, así que la regla de B.3 no se cumple en la práctica.
- El panel no distingue los guiones (7,9 contra 7,8) y no tiene coincidencias de los 3 modelos. Con n=1 caso, no hay evidencia de que v5.6 retenga más.

Nota: la sección «Veredicto de revisor-handoff (Parte B.2/B.4/B.5)» del reporte (`lab/hyperframes/f54/F54_REPORT.md`) dice «(se pega abajo)». Falta pegar este veredicto ahí.

## Adenda de CC (Parte B.2/B.4/B.5)
- **Fila 2 (v5.5 como constante):** es la práctica del proyecto desde F15 (cada versión del prompt queda con su `version=`, byte-idéntica, y el handoff A.1 la pide «como siempre»). El prompt vigente no tiene el bloque viejo. Si Omar quiere borrar `SYSTEM_V5_5` y su test, es un commit de una línea; lo decide él.
- **Fila 11:** las dos relajaciones del detector que usa la medida (años en letras → cifras; año y hecho en oraciones vecinas del mismo cap) quedan dichas acá, en la decisión 3 y en el docstring del script; se aplican igual a los dos guiones. `MEDIDA_RETENCION.md` lleva ahora una línea que las nombra (commit de este veredicto).
- **Fila 13, matiz:** correcto: D21 tiene `fecha='1961'` pero `anchors` solo toma fechas con guion; D10 y D42 no tienen nada. El hallazgo queda escrito así en «lo abierto»: datos sin ancla **o con fecha sin guion**.
- **Observación adicional:** de acuerdo; la fila «primera apuesta» y los «NO pagado» de L2/beats 5 y 11 miden al detector, no al guion. Está dicho en la lectura de CC y es el abierto 1.
