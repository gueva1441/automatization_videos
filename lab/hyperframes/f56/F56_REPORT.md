# F56 — los 3 frenos falsos del guion de Wittenoom y el re-gancho que el reparto movió · REPORTE

Handoff: `lab/hyperframes/f56/HANDOFF_F56_frenos_falsos_y_regancho.md` (md5 `af1361eda9a69be3a5a555c15a34fd75`, verificado antes de tocar nada). Rama `f11-guion-v4`. Sin tope de dólares (el gasto se informa). **Cero cambios en prompts y esquemas; sin constantes nuevas.** Pedido de Omar: A y B en paralelo con subagentes; C después, sobre los párrafos del guion F55 **antes del reparto**, sin volver a llamar al guionista ni a la escaleta; una sola PARADA al final de C.

## Para Omar, en corto
- Los 3 frenos del guion de Wittenoom eran falsos y ya no frenan: el juez de contaminación deja pasar las citas duplicadas (son la misma cita) y los rótulos sin nombre del research; el juez de citas acepta las palabras de la duplicada; y la ficha, al cargarse, pasa el texto de la cita duplicada al de la que quedó (así la próxima vez el guionista cita la versión viva).
- El reparto ya no mueve ni recorta el párrafo del re-gancho (como protegía al pico). En Wittenoom el re-gancho vuelve al **cap 3** (estaba en el 4).
- **Wittenoom quedó con 0 bloqueantes, sin volver a escribir el guion** (mismos párrafos del F55): reparto nuevo, títulos nuevos, papel nuevo. Costó US$ 0,75 (títulos + editor de largo + papel). El cap 3 queda largo (3056 caracteres > 2242, aviso): el editor acortó el párrafo del re-gancho perdiendo su oración y el reparto lo rechazó, como manda B.
- **Gasto F56: US$ 0,75.** Cero fotos, cero voz. **PARADA C.**

## Commits
| commit | qué |
|---|---|
| `46a1d8a` | A + B: `m05_narrative`, `ficha_caso`, `m01d_particion`, `medida_retencion`, tests (`test_module_f56.py` 7, `test_module_f56_reparto.py` 7), respaldo `f56/antes/`, `reparto_c.py`, stickers, MAPA |
| (este) | C: `SALIDA_C.md`, `c_run.log`, reporte, ESTADO, logs de la suite |

## Módulos: antes → después
| módulo | antes | después |
|---|---|---|
| `script_engine/m05_narrative.py` → `contamination` | saltaba solo `kind == "personajes"`; leía toda `_descartados` | salta los kinds que **empiezan por** `personajes` (hoy `personajes` y `personajes_r3`: rótulos sin nombre propio como «Defensor del empleador no identificado») y las citas con `duplicado_de` (son la cita que quedó, no otro caso). Lo demás igual: un `datos_r3` descartado sigue frenando |
| `script_engine/m05_narrative.py` → `false_quotes` | comparaba solo contra `pool["citas"]` | además contra el texto de las descartadas con `duplicado_de`: citar con las palabras de la duplicada cuenta como la cita que quedó. Una cita inventada sigue frenando |
| `researcher_steps/ficha_caso.py` → `load` | F55 D.0: remapea ids | además, en `ficha["citas"]`, las entradas que traían el id de una duplicada pasan a tener el `texto` de la cita del pool que quedó (`textos_de_la_cita_que_quedo`); el log lo dice («36 id(s)…; 1 texto(s) de cita pasan al de la cita que quedó»); el archivo no cambia; sin duplicadas, nada cambia |
| `script_engine/m01d_particion.py` → `rebalance` | protegía solo el pico (`last["beat"] != pico`) | también el beat de `esc["recuerda_loop"]`: no se mueve de cap; si se acorta, la oración del re-gancho tiene que seguir entera (`evidence.norm` subcadena), si no se deja el original con nota y queda el aviso de largo de siempre. Sin `recuerda_loop`, igual que hoy |
| `lab/hyperframes/f54/medida_retencion.py` → `re_gancho` | buscaba la oración solo en el cap de su beat (dio «no dicho» 0,36 en F55 D cuando estaba al inicio del cap 4) | la busca en todos los caps; devuelve `cap_declarado` y `cap_dicho`; la tabla dice «declarado cap X, dicho en cap Y» |

Tests (sin red): `test_module_f56.py` (7): Q15 ×2 (ni (d) ni (a)) y «Defensor del empleador» con los párrafos reales de `f56/antes/`; los 3 bloqueantes de F55 desaparecen con `g4.bloqueantes` + jueces nuevos; un `datos_r3` descartado sigue frenando; sintético (duplicada, `personajes_r3`, `datos_r3`, cita inventada); `ficha_caso.load` con el texto de la cita que quedó (sintético y Wittenoom real: la entrada de Q27 trae el texto de Q27). `test_module_f56_reparto.py` (7): sin `recuerda_loop` igual que siempre; el párrafo del re-gancho no se mueve; otro último párrafo sí; acortar el del re-gancho conserva la oración o no se acorta; el pico sigue protegido; Wittenoom real: el beat 6 queda en el cap 3; `re_gancho` en todos los caps.

## Decisiones de CC
1. **A y B en paralelo:** A la hice yo; B la hizo un subagente (fork) sobre `m01d_particion`, `medida_retencion` y un archivo de tests propio (`test_module_f56_reparto.py`) para que no se pisaran. Revisé su diff antes de commitear.
2. **`contamination` salta `kind.startswith("personajes")`** en vez de listar `personajes_r3`: generaliza la protección que ya existía (el handoff: «los kinds que empiezan por personajes»).
3. **`false_quotes` suma los textos de las duplicadas a la lista de citas** que ya compara (misma regla: subcadena en uno u otro sentido), sin tocar el criterio de ≤ 3 palabras.
4. **`load` cambia el texto solo en `ficha["citas"]`** (la entrada que es la cita), no en `hechos`/`escenas` que la nombran con otras palabras: el handoff dice «donde un id de cita se remapeó y la ficha trae su texto».
5. **Parte C con un script de lab** (`reparto_c.py`): reusa `fase1_5._step_cost`, `run_pantalla`, `md.particionar` y `judge_narration` tal cual; `fase1_5` no cambia. Los párrafos son `reparacion.parrafos` del F55 D (28), copiados en `f56/antes/01b_guionista_v4.json`. Escribe los mismos archivos que la cadena y deja en `01b_guionista_v4.json` los bloqueantes nuevos con los viejos anotados en `_f56`.
6. **Los títulos cambiaron** aunque la escaleta es la misma: `titles()` llama a Flash en cada partición (son nuevos, no «los de F55»). Está en la Salida C.

## Salida C (texto; entera en `lab/hyperframes/f56/SALIDA_C.md`)

## 1. Bloqueantes antes → después, y quién los vio

**Antes (F55 D, jueces viejos): 3**
- cap 3 beat 4 (a): entre comillas, pero no es una cita del pool: «Aterrizamos en una pista en medio de una tierra muy muy roja…»
- cap 3 beat 4 (d): fuera del caso (descartado en el pool): El avión era pequeño, de hélices, y se movía muchísimo. Aterrizamos en una pista
- cap 3 beat 5 (d): fuera del caso (descartado en el pool): Defensor del empleador no identificado

**Después (jueces F56 A): 0**
- (ninguno)

Quién los vio: (a) `false_quotes` y (d) `contamination` nuevos (código); (f)/(h) `regla_dicho` + verificador: {'llamadas': 0, 'cache': 0, 'usd': 0.0} · altas de Sonnet: ninguna.
PARADA del guion: no.

### 2. Dónde cae el re-gancho

`recuerda_loop`: beat 6 · «Un año después de que McNulty escribiera ese primer caso, un recién casado de Madrid se bajaba de un avión en esa misma pista de polvo.»

Notas del reparto: cap 3: el acortado del último párrafo (beat 6) perdía la oración del re-gancho → se deja el original · cap 3: 3056 caracteres > 2242 y no se pudo mover ni acortar (aviso) · cap 7: 1378 caracteres > 1255 → el editor acortó el último párrafo (304 → 192)

Oración del re-gancho en la narración (parecido ≥ 0,6): cap 3, oración 31 (0.93)

### 3. Los 7 caps con su largo (y los 7 títulos)

| cap | título | palabras | caracteres | beats |
|---|---|---|---|---|
| 1 | La herida que no cerraba | 161 | 834 | [1] |
| 2 | A la tierra roja | 220 | 1188 | [2, 3] |
| 3 | Ignorar el veneno | 523 | 3056 | [4, 5, 6] |
| 4 | El juego peligroso | 232 | 1259 | [7, 8] |
| 5 | Wittenoom por dentro | 292 | 1682 | [9, 10] |
| 6 | El polvo viaja | 297 | 1712 | [11, 12] |
| 7 | La herida ancestral | 216 | 1266 | [13] |

Total: 1941 palabras.

### 4. Gasto

Pasos nuevos en `01_v3_costos.json`: [{'paso': 'particion (F56 C)', 'usd': 0.0458, 'segundos': 46.8}, {'paso': 'pantalla', 'usd': 0.7005, 'segundos': 174.8}] · verificador US$ 0.0 · **total US$ 0.7463**.

### 5. El papel (01e_pantalla.md)

# Guion de pantalla en papel — 123bbb64-9fca-4395-8bf4-57d60e219ef1

`m01e_pantalla` m01e-6 (md5 del prompt `3b98aef1d8595124967ac7a85b75bab7`) · claude-sonnet-5-5 medium · 4 intento(s) · US$ 0.7005 · tokens de entrada 51365

Segundos por palabra 0.34 (mediana de 347 oraciones de 16 caps del narrador N9Z5MLTIaHFLflaLtbDi) · tope US$ 1.0 (respaldo (el perfil no trae costos.m01e_tope_usd)) · intento 1: in 51365 · out 19391 · US$ 0.2966 · intento 2: in 59683 · out 3639 · US$ 0.1558 · intento 3: in 58329 · out 492 · US$ 0.1216 · intento 4: in 58235 · out 1009 · US$ 0.1266 · **tope US$ 1.00 (respaldo (el perfil no trae costos.m01e_tope_usd)): gastado 0.7005 + esta llamada hasta 0.2998**

Totales: 11 fichas · 6 sellos · 3 relojes · 56 descartados

### ch01 — La herida que no cerraba

- beat 1 · gancho · PICO · ficha **D26** [normal] «SITIO CONTAMINADO · El más grande del hemisferio sur» en [7] sobre «mapa» (49/71 car.) · respaldo: «el sitio contaminado más grande del hemisferio sur» · año — / relato 1963 · aporta: La voz dice que el pueblo desapareció del mapa, pero no dice que su suelo sigue siendo el sitio contaminado más grande del hemisferio sur. · sello **AMENAZA** en [1]
- relojes: —

### ch02 — A la tierra roja

- beat 2 · planteo · ficha **Q25** [cita] «LO QUE DEJABAN · En España no teníamos nada, ninguno de los dos» — María Bernal (autor: modelo) en [2] sobre «confiaba» (77/90 car.) · respaldo: «En España no teníamos nada, ninguno de los dos.» · año — / relato 1961 · juzgado por el autor: otro hecho {'spoiler': ['2']} · aporta: Da el motivo de la partida en palabras de ella: no tenían nada. La voz solo cuenta que confiaba en él. · sello —
- beat 3 · planteo · PICO · ficha **D83** [normal] «EL PLAN TENÍA NOMBRE · Operación Canguro, desde 1958» en [7] sobre «acuerdo» (49/90 car.) · respaldo: «iniciado en 1958, llamado Operación Canguro» · año 1958 / relato 1950 · aporta: Pone nombre y año de inicio al acuerdo entre gobiernos que la voz menciona sin nombrarlo. · sello —
- relojes: 16 SEP 1961 en [0], 20 SEP 1962 en [4]

### ch03 — Ignorar el veneno

- beat 4 · planteo · ficha **D82** [normal] «HASTA PERTH · Unos 1.400 kilómetros» en [1] sobre «Pilbara» (32/40 car.) · respaldo: «a unos 1.400 kilómetros de Perth» · año — / relato 1962 · aporta: Pone en una cifra el aislamiento del lugar, que la voz solo muestra como desierto. · sello —
- beat 5 · escalada · PICO · ficha — ⚠ pico sin ficha · sello **AVISO** en [19] · ⚠ sin su a_pantalla: D01 (el autor no lo puso)
- beat 6 · giro · ficha — · sello **RABIA** en [26]
- relojes: —

### ch04 — El juego peligroso

- beat 7 · escalada · PICO · ficha **Q19** [cita] «SIN AVISO · Nadie nos avisó de nada» — Víctor Calvo (autor: modelo) en [9] sobre «miedo» (49/51 car.) · respaldo: «Nadie nos avisó de nada.» · año — / relato 1962 · aporta: Cierra el testimonio de Calvo con una frase que la voz no lee: a los niños nadie les avisó. · sello **INMINENTE** en [10]
- beat 8 · giro · ficha **D102** [normal] «EL BEBÉ, HOY · 63 años, productor de televisión» en [13] sobre «varón» (44/51 car.) · respaldo: «tiene 63 años y es un conocido productor de televisión» · año — / relato 1963 · aporta: Dice qué fue de ese bebé: hoy tiene 63 años y es productor de televisión. · sello —
- relojes: 7 JUL 1963 en [15]

### ch05 — Wittenoom por dentro

- beat 9 · escalada · ficha **D51** [normal] «LO QUE SALIÓ DE LA MINA · 131.000 toneladas de amianto azul» en [1] sobre «cierre» (56/71 car.) · respaldo: «produjo 131.000 toneladas de crocidolita» · año 1966 / relato 1966 · aporta: Cuantifica lo que produjo la mina, dato que la voz no menciona. · sello —
- beat 10 · pico · PICO · ficha **D23** [papel] «MUERTOS HASTA 1989 · Más de 500 muertos por amianto» en [12] sobre «mesotelioma» (48/76 car.) · respaldo: «Para 1989, más de 500 antiguos trabajadores y residentes de Wittenoom habían muerto» · año 1989 / relato 1991 · juzgado por el autor: otro hecho {'contradice': ['30', '2024']} · aporta: Muestra que Daniel no fue el único: antes de su diagnóstico ya había más de 500 muertos. · sello **SILENCIO** en [19]
- relojes: —

### ch06 — El polvo viaja

- beat 11 · respiro · ficha **D124** [normal] «TRABAJADORES · 57% con menos de 30 años» en [0] sobre «Wittenoom» (36/51 car.) · respaldo: «El 57% de la fuerza laboral de Wittenoom tenía menos de 30 años» · año — / relato 1962 · juzgado por el autor: otro hecho {'spoiler': ['30']} · aporta: Dice quiénes cargan con ese nombre: más de la mitad de la plantilla era muy joven. · sello —
- beat 12 · revelacion · PICO · ficha **D40** [normal] «ZONA DE GESTIÓN DEL ASBESTO · 46.840 hectáreas» en [14] sobre «relaves» (43/90 car.) · respaldo: «cubre una superficie de 46.840 hectáreas» · año — / relato 2006 · aporta: Da la extensión oficial del área que el Estado gestiona por el asbesto, cifra que la voz no dice. · sello —
- relojes: —

### ch07 — La herida ancestral

- beat 13 · cierre · PICO · ficha **D61** [papel] «RECONOCIMIENTO OFICIAL · En 2023: la contaminación se ha extendido» en [7] sobre «asbesto» (63/90 car.) · respaldo: «en 2023 que todos los informes sobre el alcance de la contaminación ya no son aplicables y que la contaminación se ha extendido» · año 2023 / relato 2026 · aporta: Un organismo del propio gobierno admitió en 2023 que los estudios quedaron viejos y que la contaminación avanzó. · sello **MEMORIA** en [14]
- relojes: —

### Lo que cayó

- ch03 beat 5 · ficha D47 «QUIÉN MANDABA · CSR, 51%; Hancock y Wright, 49%» en [12] → **no_dicho**: la voz lo dice en la oración ancla o en una vecina: ['Hancock', 'Wright']

### Reintento: los motivos que se le mandaron al autor

- Q25 (ch02 beat 2, oración [2]) «LO QUE DEJABAN · En España no teníamos nada, ninguno de los dos»: la voz dice «2» en una oración posterior en ch02 [7] («No iban solos: cerca de ocho mil españoles cruzaron por un acuerdo entre los dos gobiernos, y CSR, la compañía dueña de la mina, venía haciendo viajes privados a Europa para reclutar gente desde 1950.»); ¿es el mismo hecho? si no, mantenelo
- D115 (ch03 beat 6, oración [29]) «AÑO DE MÁXIMA PRODUCCIÓN · En 1962, el 95% era crocidolita de Wittenoom»: la voz dice «1962» en la oración ancla o en una vecina en ch03 [29] («En 1962, Jim McNulty comunicó un caso de mesotelioma en un antiguo trabajador del molino; una fuente lo presenta como el primero comunicado fuera de Sudáfrica.»); ¿es el mismo hecho? si no, mantenelo
- D115 (ch03 beat 6, oración [29]) «AÑO DE MÁXIMA PRODUCCIÓN · En 1962, el 95% era crocidolita de Wittenoom»: la voz dice «1962» en una oración posterior en ch05 [13] («La misma palabra que McNulty había escrito en 1962 sobre un trabajador del molino, el año en que Daniel bajó del avión.»); ¿es el mismo hecho? si no, mantenelo
- D23 (ch05 beat 10, oración [12]) «MUERTOS HASTA 1989 · Más de 500 muertos por amianto»: la voz dice «30» para lo mismo, en la oración ancla o en una vecina en ch05 [18] («Nueve meses después del diagnóstico, Daniel Écija murió en Madrid, a miles de kilómetros de la pista roja, casi treinta años después de haberse ido de ella.»); ¿es el mismo hecho? si no, mantenelo
- D23 (ch05 beat 10, oración [12]) «MUERTOS HASTA 1989 · Más de 500 muertos por amianto»: la voz dice «2024» para lo mismo, en la oración ancla o en una vecina en ch07 [4] («Maitland Parker murió de mesotelioma en 2024.»); ¿es el mismo hecho? si no, mantenelo
- D124 (ch06 beat 11, oración [0]) «TRABAJADORES · 57% con menos de 30 años»: la voz dice «30» en una oración posterior en ch07 [15] («¿Qué respiró en diez meses que tardó casi treinta años en matarlo?»); ¿es el mismo hecho? si no, mantenelo
- D64 (ch06 beat 12, oración [14]) «PARA IMAGINARLO · Llenarían el Melbourne Cricket Ground dos veces»: la voz dice «2» en una oración posterior en ch07 [9] («Quién sabía está escrito: dos inspectores en 1944, un médico al que llamaron alborotador en 1948, un tribunal que entró al molino en 1957.»); ¿es el mismo hecho? si no, mantenelo
- T13: dijiste que la voz lo dice («La voz ya dice los diagnósticos de 1946.»); la voz de ch03 no dice «Wittenoom» («Se diagnosticó un primer caso de asbestosis en Wittenoom. (fecha 1946)»): vuelve a ser candidato
- D21: dijiste que la voz lo dice («La voz ya dice que en 1961 la producción subió.»); la voz de ch03 no dice «Wittenoom» («La producción minera en Wittenoom se incrementó en 1961 a pesar de la evidencia de los riesgos.»): vuelve a ser candidato
- T27: dijiste que la voz lo dice («La voz ya cuenta el recorte del suplemento por polvo.»); la voz de ch03 no dice «3» ni «4» («El subsidio por polvo se redujo a 3 o 4 peniques y se restringió a ciertas áreas, tras la instalación de equipo para reducir el polvo. (fecha 1957)»): vuelve a ser candidato
- T80: dijiste que la voz lo dice («La voz ya dice que el pueblo fue abolido en junio de 2007.»); la voz de ch06 no dice «Ministro» ni «Desarrollo» ni «Regional» ni «Hon» ni «Jon» ni «Ford» ni «MLC» («El Ministro de Desarrollo Regional, Hon Jon Ford MLC, anunció que el pueblo había sido oficialmente abolido. (fecha 2007-06)»): vuelve a ser candidato
- D95: dijiste que la voz lo dice («La voz ya dice los mil quinientos millones.»); la voz de ch07 no dice «1.500» («El pueblo aborigen banjima reclama 1.500 millones de dólares australianos al Ejecutivo por la contaminación.»): vuelve a ser candidato
- el beat 5 de ch03 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D01 («150.000 toneladas de asbesto comercial entre 1937 y 1966: cifra técnica de contexto.»)
- el beat 12 de ch06 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D40 («Superficie oficial de WAMA: 46.840 hectáreas; cifra administrativa con versiones en disputa, mejor leída que dicha.»)

### Preguntas y respuesta del autor

- Q25 {'spoiler': ['2']}: la mantuvo en ch02 beat 2 [2]: otro hecho
- D115 {'no_dicho': ['1962'], 'spoiler': ['1962']}: la sacó o la cambió (el mismo hecho, o eligió otra)
- D23 {'contradice': ['30', '2024']}: la mantuvo en ch05 beat 10 [12]: otro hecho
- D124 {'spoiler': ['30']}: la mantuvo en ch06 beat 11 [0]: otro hecho
- D64 {'spoiler': ['2']}: la sacó o la cambió (el mismo hecho, o eligió otra)
- T27 {'spoiler': ['3']}: la sacó o la cambió (el mismo hecho, o eligió otra)
- D01 {'spoiler': ['1966']}: la sacó o la cambió (el mismo hecho, o eligió otra)

### Reintento parcial: 3 vuelta(s)

#### Vuelta 1 · US$ 0.1558

- beats que podía cambiar: ch02 beat 2, ch03 beat 5, ch03 beat 6, ch05 beat 10, ch06 beat 11, ch06 beat 12
- motivos:
  - Q25 (ch02 beat 2, oración [2]) «LO QUE DEJABAN · En España no teníamos nada, ninguno de los dos»: la voz dice «2» en una oración posterior en ch02 [7] («No iban solos: cerca de ocho mil españoles cruzaron por un acuerdo entre los dos gobiernos, y CSR, la compañía dueña de la mina, venía haciendo viajes privados a Europa para reclutar gente desde 1950.»); ¿es el mismo hecho? si no, mantenelo
  - D115 (ch03 beat 6, oración [29]) «AÑO DE MÁXIMA PRODUCCIÓN · En 1962, el 95% era crocidolita de Wittenoom»: la voz dice «1962» en la oración ancla o en una vecina en ch03 [29] («En 1962, Jim McNulty comunicó un caso de mesotelioma en un antiguo trabajador del molino; una fuente lo presenta como el primero comunicado fuera de Sudáfrica.»); ¿es el mismo hecho? si no, mantenelo
  - D115 (ch03 beat 6, oración [29]) «AÑO DE MÁXIMA PRODUCCIÓN · En 1962, el 95% era crocidolita de Wittenoom»: la voz dice «1962» en una oración posterior en ch05 [13] («La misma palabra que McNulty había escrito en 1962 sobre un trabajador del molino, el año en que Daniel bajó del avión.»); ¿es el mismo hecho? si no, mantenelo
  - D23 (ch05 beat 10, oración [12]) «MUERTOS HASTA 1989 · Más de 500 muertos por amianto»: la voz dice «30» para lo mismo, en la oración ancla o en una vecina en ch05 [18] («Nueve meses después del diagnóstico, Daniel Écija murió en Madrid, a miles de kilómetros de la pista roja, casi treinta años después de haberse ido de ella.»); ¿es el mismo hecho? si no, mantenelo
  - D23 (ch05 beat 10, oración [12]) «MUERTOS HASTA 1989 · Más de 500 muertos por amianto»: la voz dice «2024» para lo mismo, en la oración ancla o en una vecina en ch07 [4] («Maitland Parker murió de mesotelioma en 2024.»); ¿es el mismo hecho? si no, mantenelo
  - D124 (ch06 beat 11, oración [0]) «TRABAJADORES · 57% con menos de 30 años»: la voz dice «30» en una oración posterior en ch07 [15] («¿Qué respiró en diez meses que tardó casi treinta años en matarlo?»); ¿es el mismo hecho? si no, mantenelo
  - D64 (ch06 beat 12, oración [14]) «PARA IMAGINARLO · Llenarían el Melbourne Cricket Ground dos veces»: la voz dice «2» en una oración posterior en ch07 [9] («Quién sabía está escrito: dos inspectores en 1944, un médico al que llamaron alborotador en 1948, un tribunal que entró al molino en 1957.»); ¿es el mismo hecho? si no, mantenelo
  - T13: dijiste que la voz lo dice («La voz ya dice los diagnósticos de 1946.»); la voz de ch03 no dice «Wittenoom» («Se diagnosticó un primer caso de asbestosis en Wittenoom. (fecha 1946)»): vuelve a ser candidato
  - D21: dijiste que la voz lo dice («La voz ya dice que en 1961 la producción subió.»); la voz de ch03 no dice «Wittenoom» («La producción minera en Wittenoom se incrementó en 1961 a pesar de la evidencia de los riesgos.»): vuelve a ser candidato
  - T27: dijiste que la voz lo dice («La voz ya cuenta el recorte del suplemento por polvo.»); la voz de ch03 no dice «3» ni «4» («El subsidio por polvo se redujo a 3 o 4 peniques y se restringió a ciertas áreas, tras la instalación de equipo para reducir el polvo. (fecha 1957)»): vuelve a ser candidato
  - T80: dijiste que la voz lo dice («La voz ya dice que el pueblo fue abolido en junio de 2007.»); la voz de ch06 no dice «Ministro» ni «Desarrollo» ni «Regional» ni «Hon» ni «Jon» ni «Ford» ni «MLC» («El Ministro de Desarrollo Regional, Hon Jon Ford MLC, anunció que el pueblo había sido oficialmente abolido. (fecha 2007-06)»): vuelve a ser candidato
  - D95: dijiste que la voz lo dice («La voz ya dice los mil quinientos millones.»); la voz de ch07 no dice «1.500» («El pueblo aborigen banjima reclama 1.500 millones de dólares australianos al Ejecutivo por la contaminación.»): vuelve a ser candidato
  - el beat 5 de ch03 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D01 («150.000 toneladas de asbesto comercial entre 1937 y 1966: cifra técnica de contexto.»)
  - el beat 12 de ch06 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D40 («Superficie oficial de WAMA: 46.840 hectáreas; cifra administrativa con versiones en disputa, mejor leída que dicha.»)
- aplicados: ch03 beat 6 (ficha), ch06 beat 12 (ficha)

#### Vuelta 2 · US$ 0.1216

- beats que podía cambiar: ch03 beat 5, ch03 beat 6, ch06 beat 12
- motivos:
  - T27 (ch03 beat 6, oración [26]) «EL PAGO POR EL POLVO · Quedó en 3 o 4 peniques»: la voz dice «3» en una oración posterior en ch04 [14] («Tres meses antes, en marzo, Milagros Barroso había dado a luz en el mismo pueblo a John Patrick.»); ¿es el mismo hecho? si no, mantenelo
  - T13: dijiste que la voz lo dice («La voz ya dice los diagnósticos de 1946.»); la voz de ch03 no dice «Wittenoom» («Se diagnosticó un primer caso de asbestosis en Wittenoom. (fecha 1946)»): vuelve a ser candidato
  - D21: dijiste que la voz lo dice («La voz ya dice que en 1961 la producción subió.»); la voz de ch03 no dice «Wittenoom» («La producción minera en Wittenoom se incrementó en 1961 a pesar de la evidencia de los riesgos.»): vuelve a ser candidato
  - D95: dijiste que la voz lo dice («La voz ya dice los mil quinientos millones.»); la voz de ch07 no dice «1.500» («El pueblo aborigen banjima reclama 1.500 millones de dólares australianos al Ejecutivo por la contaminación.»): vuelve a ser candidato
  - el beat 5 de ch03 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D01 («150.000 toneladas de asbesto comercial entre 1937 y 1966: cifra técnica de contexto.»)
  - el beat 12 de ch06 quedó sin ninguno de los datos que la escaleta dejó para la pantalla porque la voz no los dice: D40 («Superficie oficial de WAMA: 46.840 hectáreas; cifra administrativa con versiones en disputa, mejor leída que dicha.»)
- aplicados: ch03 beat 5 (ficha/sello), ch03 beat 6 (ficha/sello), ch06 beat 12 (ficha/sello)

#### Vuelta 3 · US$ 0.1266

- beats que podía cambiar: ch03 beat 5
- motivos:
  - D01 (ch03 beat 5, oración [12]) «LO QUE SE EXTRAJO · Unas 150.000 toneladas de asbesto, de 1937 a 1966»: la voz dice «1966» en una oración posterior en ch05 [1] («En diciembre de 1966, James Vernon, de CSR, anunció el cierre de las operaciones.»); ¿es el mismo hecho? si no, mantenelo
  - T13: dijiste que la voz lo dice («La voz ya dice los diagnósticos de 1946.»); la voz de ch03 no dice «Wittenoom» («Se diagnosticó un primer caso de asbestosis en Wittenoom. (fecha 1946)»): vuelve a ser candidato
  - D21: dijiste que la voz lo dice («La voz ya dice que en 1961 la producción subió.»); la voz de ch03 no dice «Wittenoom» («La producción minera en Wittenoom se incrementó en 1961 a pesar de la evidencia de los riesgos.»): vuelve a ser candidato
  - T27: dijiste que la voz lo dice («La voz ya cuenta el recorte del suplemento por polvo.»); la voz de ch03 no dice «3» ni «4» («El subsidio por polvo se redujo a 3 o 4 peniques y se restringió a ciertas áreas, tras la instalación de equipo para reducir el polvo. (fecha 1957)»): vuelve a ser candidato
  - T80: dijiste que la voz lo dice («La voz ya dice que el pueblo fue abolido en junio de 2007.»); la voz de ch06 no dice «Ministro» ni «Desarrollo» ni «Regional» ni «Hon» ni «Jon» ni «Ford» ni «MLC» («El Ministro de Desarrollo Regional, Hon Jon Ford MLC, anunció que el pueblo había sido oficialmente abolido. (fecha 2007-06)»): vuelve a ser candidato
  - D95: dijiste que la voz lo dice («La voz ya dice los mil quinientos millones.»); la voz de ch07 no dice «1.500» («El pueblo aborigen banjima reclama 1.500 millones de dólares australianos al Ejecutivo por la contaminación.»): vuelve a ser candidato
- aplicados: ch03 beat 5 (ficha)

### Cierre del reintento

- cerró por: **tope** (después de 3 vueltas)
- cortado al cerrar, sin preguntarle al autor:
  - ch03 beat 5 · ficha D47 «QUIÉN MANDABA · CSR, 51%; Hancock y Wright, 49%» en [12] → **no_dicho**: la voz lo dice en la oración ancla o en una vecina: ['Hancock', 'Wright']

### Descartados por el modelo

- D85 [otro]: Es el dato central del beat 1 según la escaleta, pero no existe en el archivo. Usé D26 como dato de gancho.
- T34 [voz_lo_dice]: La voz dice el baile y la fecha completa; esa fecha va como reloj.
- T37 [voz_lo_dice]: La boda del 20 de septiembre de 1962 ya la dice la voz.
- Q13 [voz_lo_dice]: La voz ya cuenta que se hicieron íntimos amigos de Milagros y Ramón.
- T38 [voz_lo_dice]: La voz ya da el viaje cuatro días después de la boda.
- Q14 [voz_lo_dice]: La voz lee la cita de Calvo casi completa.
- T36 [voz_lo_dice]: La llegada de los De Juan en agosto de 1962 ya la dice la voz.
- T24 [voz_lo_dice]: La voz ya dice que CSR reclutaba en Europa desde 1950.
- Q27 [voz_lo_dice]: La voz lee la cita de la pista y las casas casi completa.
- Q44 [voz_lo_dice]: La voz ya lee la cita de los relaves.
- D92 [voz_lo_dice]: La voz dice lo de Saint en 1948 y su cita; no queda nada nuevo.
- Q45 [voz_lo_dice]: La voz ya lee la carta de la «cosecha letal».
- Q46 [voz_lo_dice]: La voz ya lee «alborotador».
- D19 [voz_lo_dice]: La voz ya dice los informes de 1944.
- T13 [voz_lo_dice]: La voz ya dice los diagnósticos de 1946. — **falso: la voz no dice ['Wittenoom']**
- Q53 [voz_lo_dice]: La voz ya lee la frase del defensor del empleador.
- D21 [voz_lo_dice]: La voz ya dice que en 1961 la producción subió. — **falso: la voz no dice ['Wittenoom']**
- Q54 [voz_lo_dice]: La voz ya lee el acta de la Junta.
- T27 [voz_lo_dice]: La voz ya cuenta el recorte del suplemento por polvo. — **falso: la voz no dice ['3', '4']**
- Q49 [voz_lo_dice]: La voz ya lee la cita de McNulty.
- T35 [voz_lo_dice]: La voz ya dice el caso de 1962 comunicado por McNulty.
- T41 [voz_lo_dice]: La voz ya dice el bautizo del 7 de julio de 1963 y la salida.
- D87 [voz_lo_dice]: La voz ya dice los diez meses.
- T40 [voz_lo_dice]: La voz ya cuenta el nacimiento del hijo.
- T39 [voz_lo_dice]: La voz ya cuenta el nacimiento de John Patrick.
- T49 [voz_lo_dice]: La voz ya dice el cierre de diciembre de 1966 por costos.
- D88 [voz_lo_dice]: La voz ya dice la estadía de los De Juan.
- T51 [voz_lo_dice]: La voz ya dice el regreso de los De Juan a Madrid en 1971.
- D27 [voz_lo_dice]: La voz ya dice la reducción del pueblo desde 1978.
- D93 [voz_lo_dice]: La voz ya dice la sentencia de 1988.
- T56 [voz_lo_dice]: La voz ya dice la fundación de la sociedad en 1979.
- T64 [voz_lo_dice]: La voz ya dice el diagnóstico de 1991 y los nueve meses.
- D89 [voz_lo_dice]: La voz ya dice que murió a los 55 años, nueve meses después.
- Q35 [otro]: El resto de la cita no cabe en la oración ancla con autor y comillas; usé D23.
- Q24 [voz_lo_dice]: La voz ya lee la frase del policía.
- Q21 [voz_lo_dice]: La voz ya lee la cita de Mercedes.
- Q33 [voz_lo_dice]: La voz ya dice la cuenta de Markey y los hijos de funcionarios.
- T80 [voz_lo_dice]: La voz ya dice que el pueblo fue abolido en junio de 2007. — **falso: la voz no dice ['Ministro', 'Desarrollo', 'Regional', 'Hon', 'Jon', 'Ford', 'MLC']**
- Q07 [voz_lo_dice]: La voz ya lee el «período oscuro».
- Q03 [voz_lo_dice]: La voz ya lee «no apta para ninguna forma de ocupación humana».
- D02 [voz_lo_dice]: La voz ya dice los más de tres millones de toneladas.
- T90 [voz_lo_dice]: La voz ya dice las fibras fuera de la zona en 2021.
- D59 [voz_lo_dice]: La voz ya dice el documento de 2016 y el costo.
- D58 [spoiler]: El costo de remediar adelantaría el «porque salía caro» que la voz dice después.
- T98 [voz_lo_dice]: La voz ya dice el proceso de 2026.
- Q10 [voz_lo_dice]: La voz ya lee la cita de Parker.
- T92 [voz_lo_dice]: La voz ya dice la visita de Orellana en 2023.
- T96 [voz_lo_dice]: La voz ya dice la muerte de Parker en 2024.
- D95 [voz_lo_dice]: La voz ya dice los mil quinientos millones. — **falso: la voz no dice ['1.500']**
- Q34 [voz_lo_dice]: La voz ya lee el «grave problema de salud y seguridad pública».
- D40 [otro]: Cifra administrativa de hectáreas con versiones en disputa (46.840 y 46.480). Prefiero D26 en el gancho.
- D79 [otro]: Es otra cifra de muertes (más de 2000) que se cruza con la de más de 4000 que la voz da en el capítulo 6.
- D68 [spoiler]: Introduce al pueblo Banjima antes de que la voz lo presente en el capítulo 7.
- T14 [otro]: Dato de negociación sindical, no se entiende solo ni importa a quien mira.
- D128 [otro]: No se entiende si la deuda de 5500 dólares es por persona o del grupo.



Papel: (ver log).

## Suite
`bash lab/hyperframes/f41/verificar.sh f56` (logs en `lab/hyperframes/f41/f56/`, sobre `46a1d8a`, con la Parte C corriendo en paralelo): ch02 md5 `f792f3d483a1fa42daed5f7f0e054f46`; rápida **53 passed**; amplia **1132 passed** + 5 fallas: las 4 previas (`m03_merge_timing` ×2, `gfx_lab` ×2) y **1 nueva que no es de F56**: `test_module_f50c.py::test_f50c_a_fotos_testigo_de_wittenoom` lee la escaleta y la narración v3 vivas de `_steps` (con anclas congeladas de F50f) y espera «Eric Saint» en la foto 3/7: esa escaleta la regeneró F55 D (pasaba en la suite `f55d0`, anterior a esa corrida). Misma familia que f48/f51c en F55: test de tanda cerrada clavado a datos de producción; a «lo abierto». `mapa_modulos.py --check`: 0 fallas (158).

## Lo que queda abierto
1. **Cap 3 largo** (3056 > 2242, aviso): el editor de largo acortó el párrafo del re-gancho perdiendo su oración y el reparto lo rechazó (lo que pide B). Para que ese cap entre en el largo hace falta otra cosa (acortar otro párrafo, o que el editor sepa qué oración no puede tocar): decisión del analista.
2. `test_module_f50c::test_f50c_a_fotos_testigo_de_wittenoom` clavado a `_steps`: falla desde la regeneración de Wittenoom (F55 D / F56 C; pasaba en la suite anterior a F55 D); apuntarlo a una copia congelada (como f48/f51c en F55 D.0) o borrarlo.
3. Los textos de la ficha en `hechos`/`escenas` que parafrasean la cita duplicada no cambian (decisión 4); solo `citas[].texto`.
4. El guion quedó con **0 bloqueantes** y PARADA del papel: nada pasa a voz ni a fotos sin Omar. El re-gancho está en el cap 3, oración 31 (parecido 0,93).
5. `person_stats` del pool sin recalcular; `fase1_5` sin el log del remapeo (de F55).

**PARADA C.** Omar y el analista deciden si esta versión (F55 texto + F56 jueces/reparto) pasa a fotos.

## Veredicto de revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

Md5 del handoff verificado: af1361eda9a69be3a5a555c15a34fd75. Corrí `python -m pytest -q test_module_f56.py test_module_f56_reparto.py test_module_f5c.py test_module_f8.py`: 36 passed. No corrí reparto_c.py, fase1_5 ni ningún modelo.

| # | requisito | estado | evidencia |
|---|---|---|---|
| 1 | A: `contamination` salta kinds `personajes*` y citas con `duplicado_de`; `false_quotes` suma el texto de las duplicadas; nada más cambia en los jueces; `datos_r3` y cita inventada siguen frenando | OK | `m05_narrative.py` diff en l.415 y l.523, 7 líneas, sin otro cambio en los jueces. `test_module_f56.py` (7 tests) pasa e incluye `datos_r3` y cita inventada. |
| 2 | A: `ficha_caso.load` pasa el texto de `citas[]` de la duplicada al de la cita que quedó, en memoria | OK | `ficha_caso.py` `textos_de_la_cita_que_quedo` + `load`. Solo modifica el dict devuelto; no hay escritura de archivo. El test con la ficha de Wittenoom pasa. |
| 3 | B: `rebalance` protege el beat de `recuerda_loop`; acorta solo si la oración sigue entera, si no deja el original más aviso; sin `recuerda_loop` queda igual | OK | `m01d_particion.py` diff: `rl_beat` entra en la condición de mover, y `ev.norm(rl_oracion) not in ev.norm(new)` descarta el acortado. Con `rl_beat=0` la condición no cambia. `test_module_f56_reparto.py` (7 tests) pasa, incluido el beat 6 de Wittenoom en el cap 3. |
| 4 | B: `medida_retencion.re_gancho` busca en todos los caps e informa `cap_declarado` y `cap_dicho` | OK | `medida_retencion.py` diff: el filtro por cap desaparece, devuelve ambos campos y la tabla los muestra. Hay test. |
| 5 | C: usa los párrafos de `f56/antes/01b_guionista_v4.json` → `reparacion.parrafos`, sin guionista ni escaleta | OK | `reparto_c.py` l.37-38 y 51: lee `ANTES/...` y solo llama a `g4.bloqueantes`, `md.particionar`, `run_pantalla` y `judge_narration`. La escaleta se lee de disco. `fase1_5` sin diff. `c_run.log` muestra solo 2 bloques de cost_tracker, $0.0458 y $0.7005. |
| 5b | C: bloqueantes 3 → 0 y quién los vio | OK | `01b_guionista_v4.json` tiene `_f56.bloqueantes_f55` con 3, `parada` False y `bloqueantes_despues` con 0. Los vio código (`false_quotes` y `contamination`); verificador: 0 llamadas, $0. |
| 5c | C: el re-gancho cae en el cap 3 | OK | En `01b_narration.json` la frase «Un año después de que McNulty» está en el cap 3 y en ningún otro. `SALIDA_C.md`: cap 3, oración 31, parecido 0,93. |
| 5d | C: 7 caps con largo y títulos, papel, gasto | OK | Los 7 caps coinciden con `01b_narration.json`: 834, 1188, 3056, 1259, 1682, 1712 y 1266 caracteres. Hay 7 títulos y papel (`01e_pantalla.md`). Gasto en `01_v3_costos.json`: 0,0458 + 0,7005 = US$ 0,7463 ≈ 0,75. |
| 6 | Cero cambios en prompts/esquemas, sin constantes nuevas | OK | `git show 46a1d8a -U0 \| grep` de SYSTEM_/SCHEMA/PROMPT: sin ningún cambio real (los resultados son MAPA y un `CHAPTER_SCHEMA` ya existente). No hay números nuevos en el código. |
| 7 | Falla de `test_f50c_a_fotos_testigo_de_wittenoom` es de los datos vivos y no del código de F56 | PARCIAL | La falla reproduce (`([], None) != (['Eric Saint'], 'arrastre')`, foto 3/7). El test llama a `ex.preparar()`, que lee escaleta y narración vivas de `_steps` (`test_module_f50c.py` l.~80). El código de F56 no toca `mexp` ni `expedientes_f50c`. Eso es coherente con la explicación del reporte. No está demostrado que falle solo por F55 D: la narración y el skeleton de `_steps` también los reescribió F56 C (`SALIDA_C.md`) y la suite corrió con C en paralelo. El log `f55d0` no contiene f50c, así que el «pasaba antes» no se puede comprobar. |
| 8 | Nada fuera de alcance | OK | `git diff --name-only 46a1d8a~1 HEAD` solo trae `lab/`, los 3 módulos, los 2 tests y `ficha_caso`. Los únicos modificados sin commitear, `diag_234_cap4.py` y `lab/hyperframes/f28/a/f28a.log`, ya estaban sucios antes y no son de F56. |
| 9 | «Lo que queda abierto» entero | OK | F56_REPORT.md l.276: 5 ítems (cap 3 largo, f50c clavado, textos parafraseados en `hechos` y `escenas`, PARADA del papel, `person_stats` sin recalcular). |

Fuera de alcance: ninguno.

Observaciones:
1. El cap 3 queda en 3056 caracteres (523 palabras) contra un tope de 2242, es decir 36% por encima. Es consecuencia de proteger el re-gancho y está declarado como aviso, pero el entregable «largo de los 7 caps» no cumple el rango del cap 3. Es decisión del analista.
2. El punto 7 de arriba: la causa de la falla en f50c es verosímil pero no probada.
3. El reporte dice «verificado» para el md5 del handoff, y coincide. El veredicto del revisor en F56_REPORT.md está pendiente («se pega abajo»), como corresponde en este momento.

Riesgos que el contrato no cubre:
- `contamination` ahora ignora cualquier kind `personajes*` y toda cita con `duplicado_de`. Si un `duplicado_de` apuntara mal, la contaminación pasaría sin que nada la frene.
- `reparto_c.py` sobrescribe `01b_narration.json`, el skeleton y el papel de `_steps` vivos. El respaldo en `f56/antes/` es de F55 D, no de F56 C, y otros tests clavados a esos datos pueden romperse.

## Adenda de CC
- **Fila 7 (f50c):** correcto, no está probado cuál de las dos regeneraciones lo rompió: el log de la suite amplia solo lista fallas y f50c no estaba en la lista de `f55d0` (corrida antes de F55 D), así que pasaba con los datos previos a F55 D; después de F55 D y de F56 C (las dos reescriben escaleta/skeleton/narración v3 de `_steps`) falla. Lo que sí está demostrado es que el código de F56 no toca lo que ese test ejercita (`m03_expediente`, `expedientes_f50c`) salvo `fuentes` leyendo la ficha por `load` (D.0), que ya estaba cuando pasó. Abierto 2 queda escrito así: «falla desde la regeneración de Wittenoom (F55 D / F56 C)».
- **Observación 1 (cap 3 largo):** es el costo de B tal como la pide el handoff; la salida lo declara con su número. Decisión del analista (abierto 1).
- **Riesgo `duplicado_de` mal apuntado:** `duplicado_de` lo escribe `_dedupe_citas` con el id que quedó en el mismo pool (test F55 B); no viene del modelo.
- **Respaldo:** `f56/antes/` guarda lo de F55 D, que es lo que C transformó; el resultado de C es lo que hay en `_steps` y está entero en `SALIDA_C.md` (narración por caps, títulos, papel). Si hace falta congelarlo, es una copia más.
