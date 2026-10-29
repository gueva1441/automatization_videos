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
