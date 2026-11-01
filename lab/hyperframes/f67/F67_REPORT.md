# F67_REPORT — compuerta de narración: métricas en m05 → crítico cableado → pestaña NARRACIÓN → lab del crítico del papel

Handoff `HANDOFF_F67_compuerta_narracion.md`, md5 `dd4c977e99047c42c6d19a154e4286de` (la copia del §5 D es ese mismo archivo) · rama `f11-guion-v4` · CC Opus 5.5 high · commits A `37c3261`, B `46102e5`, C `da63ddc`, arreglos de la revisión `c7c7f3a`, D (este).

**PARADA:** voz, fotos y papel de Wittenoom sin correr; el papel m01e-7 sigue en disco sin aprobar. Narración bytes `c7badfbe…` intacta; `md5_narracion` `778d3e1dcd4ca545453f7a29b6a92bb3`.

## Costos

| paso | US$ | esperado (§2) |
|---|---|---|
| verificador (7 caps, Etapa B) | 2.4575 | ≈ 2,4 |
| crítico m01f (Etapa B) | 0.7203 | ≈ 0,8 |
| lab crítico del papel (Etapa D) | 0.5976 | ≈ 0,8 |
| **total** | **3.7755** | |

A y C: US$ 0.

## md5 de `_steps/<tid>/` por etapa

Fotos en `lab/hyperframes/f67/md5/`.

- **A:** 06_judge_narrative.json: 33d88b4c → 75735829
- **B:** 01_v3_costos.json: 2d800876 → 77283ace; 01b_verificacion.json: 00a95fee → 688c28b1; 01b_verificacion.md: fa7e2a9d → 7c315644; 01f_critico.json: — → 5af2d447; 01f_critico.md: — → aea41c5e; 06_judge_narrative.json: 75735829 → 75735829
- **C:** ninguno cambió
- **D:** ninguno cambió

`01_v3_costos.json` cambia en B porque `_step_cost`, que el handoff pide, anota ahí. El §5 B no lo lista. `06_judge_narrative.json` se reescribe en B con los mismos bytes.

## Etapa A — métricas de retención


`seg_por_palabra` 0.34 · total 1941 palabras (`words_of`) ≈ 11.0 min · personaje según la escaleta: P16 María Bernal, términos ['maria bernal', 'bernal'] · cap más humano: ch01

| cap | título | oraciones | palabras | s | % | % acum. | años | años/min | vs más humano | con personaje | racha sin él | desde–hasta | lab F67a (pal/s/%/años) | `\S+` |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| ch01 | La herida que no cerraba | 12 | 161 | 55 | 8 | 8 | 1 | 1.09 | 1.0 | 0 | 12 | [0, 11] | 161/55/8/1 | 161 |
| ch02 | A la tierra roja | 18 | 220 | 75 | 11 | 20 | 3 | 2.4 | 2.2 | 1 | 16 | [2, 17] | 220/75/11/3 | 220 |
| ch03 | Ignorar el veneno | 32 | 523 | 178 | 27 | 47 | 7 | 2.36 | 2.17 | 0 | 32 | [0, 31] | 523/178/27/7 | 523 |
| ch04 | El juego peligroso | 19 | 232 | 79 | 12 | 59 | 1 | 0.76 | 0.7 | 0 | 19 | [0, 18] | 232/79/12/1 | 232 |
| ch05 | Wittenoom por dentro | 24 | 292 | 99 | 15 | 74 | 7 | 4.24 | 3.89 | 0 | 24 | [0, 23] | 292/99/15/7 | 292 |
| ch06 | El polvo viaja | 21 | 297 | 101 | 15 | 89 | 4 | 2.38 | 2.18 | 0 | 21 | [0, 20] | 297/101/15/4 | 297 |
| ch07 | La herida ancestral | 16 | 216 | 73 | 11 | 100 | 6 | 4.93 | 4.52 | 0 | 16 | [0, 15] | 216/73/11/6 | 216 |

**Diferencia con el lab:** `words_of` 1941 contra `\S+` 1941 (lab F67a: 1941). Se reporta, no se corrige (F67 §2).

#### Pico

```json
{
 "beat": 10,
 "cap": "ch05",
 "idx_ultima_oracion": 23,
 "pct_acumulado": 74,
 "segundos_despues": 174,
 "personaje_en_siguientes": false,
 "n_siguientes": 3,
 "oraciones_siguientes": [
  "A los que pasaron por Wittenoom, el nombre los sigue.",
  "Los que nacieron allí lo llevan escrito en el pasaporte.",
  "En un control de aeropuerto, el policía lee la página, baja la cabeza, vuelve a mirar."
 ]
}
```

#### Promesa

```json
{
 "texto": "Un minero español vivió diez meses en un pueblo construido con polvo de asbesto azul y tardó casi treinta años en morir de eso; el pueblo ya no existe en los mapas, pero tres millones de toneladas de relaves siguen donde las dejaron.",
 "cifras": [],
 "cifras_en_gancho": [],
 "faltan": [],
 "motivo": "sin cifras en dígitos"
}
```

#### Lo que el juez ya medía

Claves de `06_judge_narrative.json` antes: ['caps', 'umbrales', 'video', 'violaciones_narrador']. Las que cambiaron de valor: ninguna. Clave nueva: `retencion`.

#### Archivos del topic que cambiaron (md5)

- 06_judge_narrative.json: 33d88b4c → 75735829


`promesa` sale de la clave `promesa_gancho` de la escaleta, la misma que copia `script_engine/m01e_pantalla.py:287`. `words_of` y `\S+` dan lo mismo en esta narración: 1.941.

**Contra la simulación del §6:** la racha de ch03 no salió corta: da 32, porque P16 «María Bernal» no se nombra en ch03. No es la cifra de los críticos (31 sin Daniel). En 6 de 7 caps P16 no aparece nunca, por eso `cap_mas_humano` = ch01 solo porque es el cap con menos oraciones: ver abierto 1.

## Etapa B — crítico cableado


exit 0 · narración bytes `c7badfbe260f5eb24a47e780b40406b5` → `c7badfbe260f5eb24a47e780b40406b5` · `narracion_md5` 778d3e1dcd4ca545453f7a29b6a92bb3 · SYSTEM `fb3e5a9e734ff730a3b5184d88e7f38a` · USER `6c2591ad1f37cf9331a4ba88b93de1c3`

Entrada contra `a/user.json` del lab: {'caps': True, 'beats': True, 'escaleta_video': True, 'archivo': True, 'disputas': True, 'metricas': False, 'verificacion': True}

Claves de `metricas` del lab: ['caps', 'seg_por_palabra', 'total_min', 'total_palabras']; caps ['anios_distintos', 'cap', 'oraciones', 'palabras', 'pct', 'pct_acumulado', 'segundos', 'titulo']

Claves de `metricas` del juez: ['anios_por_min_vs_mas_humano', 'cap_mas_humano', 'caps', 'personaje', 'personaje_motivo', 'pico', 'pico_motivo', 'promesa', 'seg_por_palabra', 'total_min', 'total_palabras']; caps ['anios_distintos', 'anios_por_min', 'cap', 'oraciones', 'oraciones_con_personaje', 'palabras', 'pct', 'pct_acumulado', 'personaje_en_voz', 'racha_desde_hasta', 'racha_max_sin_personaje', 'segundos', 'titulo']

| nota | n DEBERÍA | ids inválidos | oraciones inválidas | cifras sin respaldo | marcas | US$ crítico | s | US$ verificador | «contradice» |
|---|---|---|---|---|---|---|---|---|---|
| 6.5 | 7 | — | — | — | — | 0.7203 | 166.7 | 2.4575 | 7 |

| k | cap | oraciones | palabras antes → después |
|---|---|---|---|
| 1 | ch01 | [1] | 31 → 49 |
| 2 | ch03 | [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31] | 363 → 216 |
| 3 | ch05 | [4, 7] | 35 → 72 |
| 4 | ch06 | [1, 2, 3, 4] | 37 → 49 |
| 5 | ch06 | [10, 11, 12, 13, 14, 15, 16, 17, 18, 19] | 156 → 112 |
| 6 | ch07 | [5, 6, 7, 8] | 79 → 45 |
| 7 | ch07 | [12, 13, 14, 15] | 35 → 56 |

Archivos del topic que cambiaron (md5):

- 01_v3_costos.json: 2d800876 → 77283ace
- 01b_verificacion.json: 00a95fee → 688c28b1
- 01b_verificacion.md: fa7e2a9d → 7c315644
- 01f_critico.json: — → 5af2d447
- 01f_critico.md: — → aea41c5e
- 06_judge_narrative.json: 75735829 → 75735829


**Verificador re-corrido:** 7 «contradice» (antes 7); iguales 7, nuevos 0, se fueron 0; «sin respaldo» 28 (antes 24). Pisó el `01b_verificacion` anterior, con su sección de ch03 [15]: el respaldo está en `b/antes/`.

**Diferencia con la entrada del lab (declarada, §0):** `caps`, `beats`, `escaleta_video`, `archivo` y `disputas` son iguales a `a/user.json`; `metricas` tiene más claves que las del lab y contiene todas las de `metricas_de`. El SYSTEM no se adaptó.

### `01f_critico.md`, entero

#### Crítica de la narración

`m01f-1` · claude-opus-5-5 medium · US$ 0.7203 · tokens in 90936 · out 17827 · 166.7 s · 1 intento(s) · narración `778d3e1dcd4ca545453f7a29b6a92bb3`

**Nota total:** 6.5

##### Resumen

- Retiene bien: el gancho del pie vendado, la travesía, los chicos que juegan con amianto y el pico de los nueve meses (ch04-ch05) sostienen al espectador.
- Se pierde en ch03 idx 11-30: tres minutos de informes, siglas y años con Daniel ausente durante 31 oraciones, entre el 20% y el 47% del video. Después del pico (74%), el ch06 corre 21 oraciones sin la familia y el ch07 cierra con la mayor densidad del video.
- Primero reescribiría el bloque documental de ch03 anclándolo al calendario de Daniel. Después nombraría al hijo en la escena del pasaporte, justo detrás del pico.

Personaje según la escaleta: P16 María Bernal

##### Métricas por cap (código)

| cap | palabras | s | % | % acum. | años/min | racha sin personaje |
|---|---|---|---|---|---|---|
| ch01 | 161 | 55 | 8 | 8 | 1.09 | 12 |
| ch02 | 220 | 75 | 11 | 20 | 2.4 | 16 |
| ch03 | 523 | 178 | 27 | 47 | 2.36 | 32 |
| ch04 | 232 | 79 | 12 | 59 | 0.76 | 19 |
| ch05 | 292 | 99 | 15 | 74 | 4.24 | 24 |
| ch06 | 297 | 101 | 15 | 89 | 2.38 | 21 |
| ch07 | 216 | 73 | 11 | 100 | 4.93 | 16 |

##### Gancho

- Promesa cumplida: True
- Están el minero de Madrid, los casi treinta años, el pueblo borrado y lo que sobró de la mina. Faltan los «diez meses», que es el contraste que hace funcionar la promesa, e idx 1 dice que el pie «va a cerrar», lo que contradice idx 3 y el archivo (D85).

##### Capítulos

| cap | nota | personaje en voz | oraciones seguidas sin personaje | fuerte | débil | re-enganche |
|---|---|---|---|---|---|---|
| ch01 | 8 | True | 4 | Imagen concreta (retrato, pie vendado), muerte anunciada a futuro y un pueblo borrado: tres preguntas en 55 s con 1,09 años/min. | Idx 1 («ese pie va a cerrar») choca con idx 3 («la herida no cerraba») y confunde la pregunta central. No dice cuánto tiempo estuvo. | «Dos años antes de la foto, en Madrid, hubo un baile»: salto temporal que promete el origen. Fuerte. |
| ch02 | 7 | True | 9 | La ternura del baile y la cita de María, y la travesía de Víctor contada con el cuerpo (calor, mareos). | Idx 7 junta en una oración el acuerdo, los ocho mil, CSR y 1950. Desde idx 9 la pareja desaparece y Víctor carga solo el capítulo. | «Del avión, a la tierra más roja…»: imagen que empuja a la llegada. Correcto. |
| ch03 | 4.5 | True | 31 | Idx 0-10: la pista, los patios y la escuela hechos de relaves, con la cita del extrabajador. La revelación del suelo es muy buena. | Es el valle del video: el 27% del total, siete años distintos, ABA, CSR, inspector, ingeniero adjunto, Junta de Referencia y suplemento salarial, sin Daniel ni María hasta la última oración. El chico de idx 4 queda sin nombre aunque el cap anterior terminó con Víctor. | «Un recién casado de Madrid se bajaba de un avión en esa misma pista»: excelente, devuelve al humano. Llega tarde. |
| ch04 | 8 | True | 8 | Densidad mínima (0,76 años/min): los niños que se meten el amianto en la boca, el parto y el bautizo. Es el capítulo más físico. | Idx 2-9 cede la escena a Ramón y Víctor. Funciona porque es sensorial. | «Creyeron que se llevaban de Wittenoom un hijo y nada más»: ironía dramática que obliga a seguir. Fuerte. |
| ch05 | 8 | True | 6 | El pico: «eso respiraba mientras esperaba que le cerrara el pie», «Lo alcanzó», nueve meses contra diez. Paga el gancho. | Idx 0-10 sube a 4,24 años/min justo antes del pico (1966, 1971, 1978, 1979, 1988). El dato de los De Juan y la Asbestos Diseases Society son carga muerta en ese tramo. | «Daniel había estado en Wittenoom diez»: cierra con fuerza pero no promete nada. Todo el empuje hacia ch06 depende de su primera oración. |
| ch06 | 5.5 | False | 21 | La escena del pasaporte y el remate «No porque fuera técnicamente imposible. Porque salía caro». | El pasaporte es del hijo (T57) pero la voz lo vuelve anónimo. Además: cifras de Markey enredadas, fecha con duda («hacia junio de 2007, según otras referencias en 2006»), sigla DWER y 2021 antes que 2016. | «En esa tierra vivía un hombre que no podía irse»: promete un personaje nuevo. Fuerte. |
| ch07 | 6 | True | 12 | Maitland Parker y su cita, su muerte en 2024 y la palada que nadie sacó como imagen de cierre del loop institucional. | Es el capítulo más denso del video (4,93 años/min): Gordon Legal, BNTAC, Tribunal Federal, mil quinientos millones y una recapitulación con tres años en los últimos 73 s. La pregunta final repite una que ch05 ya respondió. | Termina con una pregunta retórica sobre Daniel. Vuelve al humano pero no a la imagen del gancho (la foto, el pie). |

##### Loops

| pregunta | abre | paga | se recuerda |
|---|---|---|---|
| ¿Qué le hizo Wittenoom a Daniel, si lo alcanzó a miles de kilómetros y casi treinta años después? | ch01:1 | ch05:18 | True |
| ¿Quién lo llevó hasta allí? | ch01:10 | ch02:7 | True |
| ¿Qué nombre tenía en los informes lo que sobraba de la mina? ¿Quién sabía y quién va a limpiar? | ch03:10 | ch07:11 | True |
| ¿Se llevaron de Wittenoom solo un hijo? | ch04:18 | ch05:12 | True |
| ¿Quién es el hombre que no podía irse de esa tierra? | ch06:20 | ch07:2 | True |

##### Pico

- ch05 · acumulado 74 % · 174 s después
- El pico está bien colocado y paga el gancho, pero sus casi tres minutos de cola corren sin la familia: el pasaporte es anónimo y el resto es administración y siglas. Nombrar al hijo en la primera escena de ch06 sostendría la caída emocional.

##### Cierre

Vuelve a Daniel y a los diez meses, pero no a la foto del pie vendado. Termina en una pregunta que ch05:12-14 ya respondió, así que la promesa queda pagada a medias.

##### DEBERÍA

###### 1. ch01 · oraciones [1] · 31 → 49 palabras

- **Sale:** «Ese pie va a cerrar», que contradice idx 3 y el archivo.
- **Por qué se van:** El espectador oye que la herida cierra y dos oraciones después que no cerraba: la pregunta central del gancho se desarma en los primeros 15 s.
- **Ids:** D85, D87, D89
- **Cifras sin respaldo:** — · **Marcas:** —

> Va a pasar diez meses en este lugar. Esa herida no va a cerrar, pero no es el pie lo que lo va a matar: lo que respira mientras espera que cierre va a tardar casi treinta años, y lo va a alcanzar a miles de kilómetros de aquí.

###### 2. ch03 · oraciones [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31] · 363 → 216 palabras

- **Sale:** La toma de ABA en 1943, los diagnósticos de 1946, el suplemento salarial, la frase repetida de Saint, la cita larga de McNulty y la mitad de las siglas. Se conservan 1944, 1948, 1957, 1961 y 1962, que necesitan ch05:13 y ch07:9.
- **Por qué se van:** Son 20 oraciones de expediente con años, siglas e instituciones y ningún rostro conocido. Es el tramo de 20%-47% donde el espectador decide si el video es sobre Daniel o un informe.
- **Ids:** D19, Q45, T20, Q46, D92, Q53, Q54, T26, D20, D21, T34, D130, T35, T38
- **Cifras sin respaldo:** — · **Marcas:** —

> Los informes eran anteriores a la boda, al barco y al avión. En 1944, el inspector de minas y el ingeniero de minas adjunto del Estado ya informaban sobre el problema del polvo. En 1948, un médico joven llegó en avión, vio el molino y escribió a Perth: «En un año o dos, ABA producirá la cosecha más abundante y letal de casos de asbestosis de la literatura mundial». Se llamaba Eric Saint. La respuesta la contó él: «Me desestimaron y, de hecho, me tildaron de alborotador». La empresa tenía otra lectura: «El mero hecho de que haya nubes de polvo no significa que ese polvo sea peligroso». Faltaban catorce años para que Daniel Écija bajara de ese avión. En 1957, un tribunal laboral entró al molino y escribió lo que vio: «Las condiciones dentro del molino eran extremadamente polvorientas y… sus trabajadores estaban cubiertos de polvo». Faltaban cinco años. Los reguladores hicieron poco más que emitir advertencias y pedir equipos. En 1961, el año en que Daniel y María se conocieron en un baile de Madrid, la producción subió. En 1962, un médico, Jim McNulty, comunicó un caso de mesotelioma en un antiguo trabajador del molino. Ese mismo año, un recién casado de Madrid se bajaba de un avión en esa misma pista de polvo.

###### 3. ch05 · oraciones [4, 7] · 35 → 72 palabras

- **Sale:** La estadía y el regreso de los De Juan en 1971 y la fundación de la Asbestos Diseases Society en 1979.
- **Por qué se van:** Son dos años y un nombre en inglés más en el tramo de mayor densidad, justo antes del pico. El espectador quiere saber qué le pasa a Daniel, no a los vecinos.
- **Ids:** T47, D27, D93
- **Cifras sin respaldo:** — · **Marcas:** —

> Ese mismo año los Écija volvieron a Madrid. Con la mina cerrada, el suelo del pueblo seguía siendo el mismo. En 1978 el gobierno del Estado empezó a reducir Wittenoom y a alentar a la gente a irse, por el riesgo de fibras en el aire. Y en 1988 un juez determinó que la compañía había mostrado un desprecio continuo, consciente y contumaz por la seguridad y la salud de sus trabajadores.

###### 4. ch06 · oraciones [1, 2, 3, 4] · 37 → 49 palabras

- **Sale:** La versión anónima del pasaporte («los que nacieron allí», «el policía»). Se conserva idx 0 como re-gancho.
- **Por qué se van:** Justo después del pico, la voz suelta a la familia que acaba de hacer llorar al espectador. La escena es del hijo, el niño del bautizo, y nombrarlo mantiene el hilo humano.
- **Ids:** T57, Q24, D102
- **Cifras sin respaldo:** — · **Marcas:** —

> Daniel, el hijo, el niño del bautizo, volvió a Australia de adulto por primera vez en 1985. Lo llevaba escrito en el pasaporte. En el control del aeropuerto, el policía leyó la página, bajó la cabeza, volvió a mirar. «Así que de Wittenoom, ¿eh? Un sitio terrorífico», le dijo.

###### 5. ch06 · oraciones [10, 11, 12, 13, 14, 15, 16, 17, 18, 19] · 156 → 112 palabras

- **Sale:** La fecha con duda, la sigla DWER, la cita del «período oscuro» mal fechada y el desorden 2021/2016. Se conservan el borrado del mapa, los tres millones de toneladas, el Fortescue, «salía caro» y las fibras fuera de la zona.
- **Por qué se van:** La voz duda de su propia fecha, salta de 2021 a 2016 y mete organismos en inglés: el espectador pierde el hilo justo cuando el capítulo debería escalar.
- **Ids:** D31, T79, Q03, D02, D147, D10, T75, D59, T90
- **Cifras sin respaldo:** — · **Marcas:** —

> En junio de 2007, Wittenoom fue abolido oficialmente. Le quitaron el nombre de los mapas y arrancaron las señales de la carretera. La zona quedó declarada «no apta para ninguna forma de ocupación humana o uso del suelo». Lo que no se puede abolir son los relaves: más de tres millones de toneladas, sin cubrir. El agua los arrastra por los arroyos hasta el río Fortescue, y un informe advirtió que podía seguir así durante cientos de años si nadie intervenía. En 2016, un documento estatal aconsejó no asegurarlos. No porque fuera técnicamente imposible. Porque salía caro. Cinco años después, se encontraron fibras en arroyos fuera de la zona marcada como contaminada.

###### 6. ch07 · oraciones [5, 6, 7, 8] · 79 → 45 palabras

- **Sale:** Gordon Legal, BNTAC, la cifra de mil quinientos millones y la respuesta del gobierno. Se conserva la palada, que necesita idx 11.
- **Por qué se van:** Es el capítulo más denso del video (4,93 años/min) cayendo en el último minuto. Las siglas jurídicas enfrían el duelo de Parker.
- **Ids:** T98, D62, D70, D71
- **Cifras sin respaldo:** — · **Marcas:** —

> En 2026, el pueblo Banjima llevó al Estado de Australia Occidental ante el Tribunal Federal. Sus abogados sostienen que el Estado no ha gastado un dólar en remediar el sitio y que no se ha retirado una sola palada de asbesto de la tierra Banjima.

###### 7. ch07 · oraciones [12, 13, 14, 15] · 35 → 56 palabras

- **Sale:** La pregunta final que repite lo ya respondido en ch05.
- **Por qué se van:** El cierre no vuelve a la imagen del gancho. Pregunta algo que el espectador ya sabe (mesotelioma, el polvo) y el final se siente plano en vez de circular.
- **Ids:** D87, D85, Q25, D89, D31, D02
- **Cifras sin respaldo:** — · **Marcas:** —

> Daniel Écija vivió diez meses en Wittenoom. María todavía guarda la foto: un hombre joven, el pie vendado, una herida que no cerraba. Nadie en su familia sabe decir qué respiró allí, en diez meses, que tardó casi treinta años en matarlo. Wittenoom ya no está en el mapa. Lo que sobró de la mina, sí.

##### Reglas generales candidatas

- Ningún tramo pasa más de 10 oraciones seguidas sin el protagonista (por nombre o acción). · *medible:* racha_max_sin_personaje ≤ 10 por capítulo, con los terminos del personaje tomados del humano real de la escaleta. · *por qué:* Las rachas largas sin rostro (ch03: 31, ch06: 21) coinciden con los tramos expositivos donde el espectador abandona.
- Un capítulo de contexto documental no puede superar el doble de años por minuto del capítulo más humano si ocupa más del 15% del video. · *medible:* Marcar si anios_por_min_vs_mas_humano > 2,0 y pct > 15. · *por qué:* ch03 (2,17x, 27% del video) es el valle principal.
- Cada capítulo con 4 o más años distintos debe anclar al menos un año al calendario del protagonista. · *medible:* Si anios_distintos ≥ 4, exigir al menos una oración que contenga un año y un término del personaje. · *por qué:* Convierte la cronología institucional en cuenta regresiva hacia el humano en lugar de expediente.
- El protagonista o su familia aparecen en las primeras 3 oraciones después del pico. · *medible:* pico.personaje_en_siguientes == true. · *por qué:* Tras la descarga emocional el espectador se va si la voz cambia de sujeto. Aquí quedaban 174 s sin la familia.
- El último capítulo no puede ser más denso que el capítulo del pico. · *medible:* anios_por_min del último cap ≤ anios_por_min del cap del pico. · *por qué:* ch07 (4,93) supera a ch05 (4,24): el cierre se recarga de datos justo cuando debería volver a la imagen del gancho.

##### Riesgos

- Toco el gancho en ch01 idx 1: agrego «diez meses» y saco «va a cerrar» para alinear con D85. La promesa no cambia, solo se refuerza.
- Las métricas buscan a «María Bernal» porque la escaleta tiene el nombre equivocado en humano (el rol y la fuente son de Daniel Écija). Conté las rachas con Daniel; si el código sigue con esos términos, todos los capítulos van a aparecer sin personaje.
- El DEBERÍA de ch03 elimina la toma de ABA en 1943, los diagnósticos de 1946 (además sobredimensionados en plural), el recorte del suplemento salarial y la cita de McNulty «lo esperaban», apoyo del beat 6. Conserva 1944, 1948, 1957 y McNulty 1962, que son los que retoman ch05:13 y ch07:9.
- Al sacar ch05 idx 4, ch06 idx 5 debería presentar a Mercedes como «la hija de Ramón de Juan» para no quedar huérfana.
- El DEBERÍA de ch06 quita la cita «el fin de un período oscuro» (Q07), que es el ancla de la pregunta del beat 12. Si se quiere conservar, debe ir fechada en 2022 con el desalojo de los últimos vecinos (T91), no con la abolición.
- El DEBERÍA de ch07 quita la respuesta del gobierno (Q34) y la cifra reclamada (D95). Se pierde la versión del Estado: decidirlo con quien revisa equilibrio.
- Los re-ganchos ch01:11, ch03:31, ch04:18, ch06:9, ch06:0 y ch06:20 y el bloque del pico ch05:11-23 no se tocan. ch01 idx 9 y la promesa dicen que los relaves «siguen donde los dejaron», cuando el archivo dice que se dispersan (D04, D61): la reescritura de ch06 usa «sin cubrir» (D147) para no contradecir el arrastre por el agua.


## Etapa C — compuerta NARRACIÓN


#### 1. La PARADA (`run_pipeline --topic <tid> --batch`)

```
exit 0

  ⏵ 123bbb64-9fca-4395-8bf4-57d60e219ef1: arranca en «narracion» — la narración no está aprobada

────────────────────────────────────────────────────────────
  ▶ NARRACION (compuerta de narración) — 123bbb64-9fca-4395-8bf4-57d60e219ef1
────────────────────────────────────────────────────────────

════════════════════════════════════════════════════════════
  📊 RUN_PIPELINE — 123bbb64-9fca-4395-8bf4-57d60e219ef1
════════════════════════════════════════════════════════════
  Fases corridas: narracion
  ⛔ Frenó en: NARRACION
     Motivo: la narración no está aprobada (la compuerta no se aprueba sola: sin el form la aprueba Omar a mano)
  ➡  Próximos comandos:
       leer:    QA Studio → NARRACIÓN (o C:/CLAUDE_PROJECTS/automatization_videos/data/scripts/_steps/123bbb64-9fca-4395-8bf4-57d60e219ef1/01f_critico.md)
       aprobar: python fase1_5.py --topic 123bbb64-9fca-4395-8bf4-57d60e219ef1 --aprobar-narracion "Omar <fecha>"
       retomar: python run_pipeline.py --topic 123bbb64-9fca-4395-8bf4-57d60e219ef1
════════════════════════════════════════════════════════════

```

Archivos del topic que cambiaron: ninguno

#### 2. GET /narracion, resumido (topic real)

- estado: {'aprobado': False, 'motivo': 'la narración no está aprobada'}
- nota: 6.5 · crítico vigente: True · sin_critico: False
- 7 caps · 7 DEBERÍA · 6 con `aplica`
- verificación: 7 «contradice», vigente True
- pico: ch05 74 %, 174 s después

Chrome headless: 0 errores de página  · texto entero en `c/narracion_pestana.txt`, JSON en `c/narracion_get.json`, capturas `c/narracion_qa.png` y `c/narracion_qa_deberia.png`.
Archivos del topic que cambiaron al abrir la pestaña: ninguno

Comienzo de la pestaña:

```
Sin aprobar
la narración no está aprobada
claude-opus-5-5 m01f-1 · US$ 0.7203 · 7 DEBERÍA
Aprobar narración
nota6.5 / 10
Retiene bien: el gancho del pie vendado, la travesía, los chicos que juegan con amianto y el pico de los nueve meses (ch04-ch05) sostienen al espectador.
Se pierde en ch03 idx 11-30: tres minutos de informes, siglas y años con Daniel ausente durante 31 oraciones, entre el 20% y el 47% del video. Después del pico (74%), el ch06 corre 21 oraciones sin la familia y el ch07 cierra con la mayor densidad del video.
Primero reescribiría el bloque documental de ch03 anclándolo al calendario de Daniel. Después nombraría al hijo en la escena del pasaporte, justo detrás del pico.
Gancho: promesa cumplida sí · Están el minero de Madrid, los casi treinta años, el pueblo borrado y lo que sobró de la mina. Faltan los «diez meses», que es el contraste que hace funcionar la promesa, e idx 1 dice que el pie «va a cerrar», lo que contradice idx 3 y el archivo (D85).
Pico (código): ch05 · 74 % acumulado · 174 s después · personaje en las 3 siguientes: no
Personaje según la escaleta: P16 María Bernal
⚠ aviso del verificador: 7 «contradice»
loops (5)
cierre
riesgos (7)
reglas candidatas (5)
ch01La herida que no cerraba · 8
161 palabras · 55 s · 8 % · 1.09 años/min · racha sin personaje 12 · personaje en voz (crítico) sí
Fuerte: Imagen concreta (retrato, pie vendado), muerte anunciada a futuro y un pueblo borrado: tres preguntas en 55 s con 1,09 años/min.
Débil: Idx 1 («ese pie v
```

#### 3. Prueba sobre la copia (`lab/hyperframes/f67/c/<tid>/`)

##### Reconstruir sin cambios

Los 3 archivos con los mismos bytes: {'01a_skeleton.json': True, '01b_narration.json': True, '01b_narracion_v3.json': True}

##### Qué DEBERÍA aplican hoy

{1: True, 2: True, 3: False, 4: True, 5: True, 6: True, 7: True}

##### Aprobar

`{'por': 'Prueba', 'fecha': '2026-10-31', 'md5': '778d3e1dcd4ca545453f7a29b6a92bb3'}` · estado: (True, 'narración aprobada por Prueba (2026-10-31), md5 778d3e1d…') · md5 sigue `True`

##### Aceptar DEBERÍA 2 (ch03, 21 oraciones, cruza 5 párrafos)

Respuesta: `{'k': 2, 'cap': 'ch03', 'beats_cambiados': [5, 6], 'beats_sin_texto': [6], 'md5': 'a2693169d6e15f8bd7e6fd929f79231f'}`

md5 cambió: `778d3e1d…` → `a2693169…` · estado: (False, 'la narración no está aprobada')

**Párrafos antes:**

- [5] beat 4: El avión era pequeño, de hélices, y se movía muchísimo. Abajo, el desierto de Pilbara, en Australia Occidental. «Aterrizamos en una pista en medio de una tierra muy muy roja. Había polvo por todas partes. Nunca había visto tanto polvo», recuerda uno de los chicos que bajaron de ese avión. Los llevaron a las casas: chapa, madera y uralita.
- [6] beat 4: La pista donde aterrizaron estaba hecha con relaves de la mina, con lo que quedaba después de sacar la fibra. Con lo mismo se hicieron las carreteras, los patios y los espacios públicos del pueblo, y la empresa descargaba los relaves a pedido de los vecinos. «Las escuelas y el jardín de infantes, las iglesias, todos lo tenían bonito con relaves allí», dijo un antiguo trabajador de la mina. El pueblo entero, la pista, los patios, la escuela: todo estaba hecho con lo que sobraba de la mina. Y lo que sobraba de la mina ya tenía nombre en los informes.
- [7] beat 5: Los informes eran anteriores a la boda, al barco y al avión. En 1943, ABA, una filial de CSR, se quedó con los intereses de Hancock y Wright en la mina. En 1944, el inspector de minas y el ingeniero de minas Adjunto del Estado informaron sobre el problema del polvo. En 1946 ya había diagnósticos de asbestosis, y un inspector describió las condiciones de trabajo como terroríficas. El defensor del empleador tenía otra lectura: «El mero hecho de que haya nubes de polvo no significa que ese polvo sea peligroso».
- [8] beat 5: En 1948, un médico llegó en avión y puso por escrito lo que encontró. «En un año o dos, ABA producirá la cosecha más abundante y letal de casos de asbestosis de la literatura mundial», dice la carta de ese médico. Pedía, naturalmente, examinar algunos de esos tórax.
- [9] beat 5: Eric Saint, médico, fue quien advirtió por escrito ese año que los niveles de polvo eran extremadamente peligrosos. La respuesta la contó él: «Me desestimaron y, de hecho, me tildaron de alborotador», dijo Saint. Nueve años después, un tribunal laboral fue a ver el molino con sus propios ojos.
- [10] beat 6: La Junta de Referencia entró al molino en 1957 y escribió lo que vio. «Las condiciones dentro del molino eran extremadamente polvorientas y… sus trabajadores estaban cubiertos de polvo», dice el acta. Una nube espesa flotaba alrededor del edificio. Siete meses después se instalaron equipos para reducir el polvo, y con los equipos se recortó y se restringió el suplemento salarial que los hombres cobraban por ese polvo. Un documento oficial lo resume así: los reguladores hicieron poco más que emitir advertencias y pedir equipos.
- [11] beat 6: En 1961 la producción subió. En 1962, Jim McNulty comunicó un caso de mesotelioma en un antiguo trabajador del molino; una fuente lo presenta como el primero comunicado fuera de Sudáfrica. Según McNulty, los que habían advertido sobre el polvo y predicho las enfermedades no sorprendieron a nadie: «no se encendieron las alarmas entre los involucrados en la industria minera porque estaban acostumbrados; lo esperaban». El año en que McNulty escribió ese primer caso, un recién casado de Madrid se bajaba de un avión en esa misma pista de polvo.

**Párrafos después:**

- [5] beat 4: El avión era pequeño, de hélices, y se movía muchísimo. Abajo, el desierto de Pilbara, en Australia Occidental. «Aterrizamos en una pista en medio de una tierra muy muy roja. Había polvo por todas partes. Nunca había visto tanto polvo», recuerda uno de los chicos que bajaron de ese avión. Los llevaron a las casas: chapa, madera y uralita.
- [6] beat 4: La pista donde aterrizaron estaba hecha con relaves de la mina, con lo que quedaba después de sacar la fibra. Con lo mismo se hicieron las carreteras, los patios y los espacios públicos del pueblo, y la empresa descargaba los relaves a pedido de los vecinos. «Las escuelas y el jardín de infantes, las iglesias, todos lo tenían bonito con relaves allí», dijo un antiguo trabajador de la mina. El pueblo entero, la pista, los patios, la escuela: todo estaba hecho con lo que sobraba de la mina. Y lo que sobraba de la mina ya tenía nombre en los informes.
- [7] beat 5: Los informes eran anteriores a la boda, al barco y al avión. En 1944, el inspector de minas y el ingeniero de minas adjunto del Estado ya informaban sobre el problema del polvo. En 1948, un médico joven llegó en avión, vio el molino y escribió a Perth: «En un año o dos, ABA producirá la cosecha más abundante y letal de casos de asbestosis de la literatura mundial». Se llamaba Eric Saint. La respuesta la contó él: «Me desestimaron y, de hecho, me tildaron de alborotador». La empresa tenía otra lectura: «El mero hecho de que haya nubes de polvo no significa que ese polvo sea peligroso». Faltaban catorce años para que Daniel Écija bajara de ese avión. En 1957, un tribunal laboral entró al molino y escribió lo que vio: «Las condiciones dentro del molino eran extremadamente polvorientas y… sus trabajadores estaban cubiertos de polvo». Faltaban cinco años. Los reguladores hicieron poco más que emitir advertencias y pedir equipos. En 1961, el año en que Daniel y María se conocieron en un baile de Madrid, la producción subió. En 1962, un médico, Jim McNulty, comunicó un caso de mesotelioma en un antiguo trabajador del molino. Ese mismo año, un recién casado de Madrid se bajaba de un avión en esa misma pista de polvo.

Aceptar otra vez → `DEBERÍA 2 ya no aplica (el texto cambió)`

##### Editar el párrafo 5

Antes: (True, 'narración aprobada por Prueba (2026-10-31), md5 a2693169…')

Respuesta: `{'i': 5, 'beat': 4, 'md5': 'e87e9cdee16101b37f8645b69295c380'}`

md5 cambió: `a2693169…` → `e87e9cde…` · la aprobación cayó: (False, 'la narración no está aprobada')

##### Métricas vigentes en la copia

`retencion.total_palabras` 1797 · pico ch05 71 %

Archivos del topic REAL que cambiaron durante la prueba: ninguno


**Al retomar no se vuelve a correr `run_guion_v4`:** la condición es `fase1_5.py:730`; `run_pipeline._paso_voz` usa `--from normalizer_gate`. Test: `test_process_topic_para_en_narracion_antes_del_papel_y_al_reanudar`.

**`01b_narration_normalized.json`:** `reconstruir` lo borra, porque `audio_manager._resolve_text_for_tts` lo lee antes que la narración (`audio_manager.py:493`). El de Wittenoom sigue en disco, sin tocar: es la prueba sobre la copia la que lo borra. Omar: al aprobar, la voz va `--from normalizer_gate`, que es lo que corre `_paso_voz`.

## Etapa D — crítico del papel (lab)


Handoff `dd4c977e99047c42c6d19a154e4286de` · SYSTEM_D `da15cabeb304278db8d992c2b87c301c` · USER `7877de7c37c01492f1cee1ccefda7a0b` · claude-opus-5-5 medium · 1 corrida · US$ 0.5976

Producción intacta: archivos de `_steps/<tid>/` que cambiaron: ninguno · `data/cost_history.json` mtime igual: True

### F67 D — validación

| tipo | cap | beat | id | (cap, beat) existe | id existe | ya en el papel | cifras sin respaldo |
|---|---|---|---|---|---|---|---|
| beat | ch01 | 1 | None | True | True | False | — |
| beat | ch02 | 2 | None | True | True | False | — |
| beat | ch02 | 3 | None | True | True | False | — |
| beat | ch03 | 4 | None | True | True | False | — |
| beat | ch03 | 5 | None | True | True | False | — |
| beat | ch03 | 6 | None | True | True | False | — |
| beat | ch04 | 7 | None | True | True | False | — |
| beat | ch04 | 8 | None | True | True | False | — |
| beat | ch05 | 9 | None | True | True | False | — |
| que_pondria | ch05 | 10 | D35 | True | True | False | — |
| beat | ch06 | 11 | None | True | True | False | — |
| que_pondria | ch06 | 12 | D150 | True | True | False | — |
| beat | ch07 | 13 | None | True | True | False | — |
| hueco | ch03 | 6 | D138 | True | True | False | — |
| hueco | ch07 | 13 | D68 | True | True | False | — |

Nota 6.5 · US$ 0.5976 · 131.8 s


### Crítica del papel (lab F67 D)

claude-opus-5-5 medium · US$ 0.5976 · tokens in 81659 · out 13549 · 131.8 s · 1 intento(s)

**Nota total:** 6.5

#### Resumen

- Las fichas están bien elegidas: diez de doce dan un dato que la voz no dice (1930, Operación Canguro, 5%, el 95% de 1962, los 18,3 millones, los 70.000 millones) y casi todas caen en su palabra.
- Los siete sellos son etiquetas de emoción (INMINENTE, AMENAZA, CALMA, ALARMA, MEMORIA, RABIA, SILENCIO) que le dicen al espectador qué sentir sin darle nada; INMINENTE además contradice los treinta años de la voz.
- El pico pierde fuerza con una estadística de 500 muertos justo en el diagnóstico de Daniel, el beat 12 gasta su ficha en un nombre de ministro, y los relojes repiten fechas que la voz ya dice.

#### Por beat

| cap | beat | ficha suma | por qué | sello suma | por qué | momento | se lee | compite | qué pondría | sello pondría |
|---|---|---|---|---|---|---|---|---|---|---|
| ch01 | 1 | True | La voz dice que lo que sobró 'sigue' allí; la ficha agrega la escala: es el mayor sitio contaminado del hemisferio sur. | False | INMINENTE no da ningún dato y choca con 'casi treinta años'; el gancho necesita el otro término de la promesa, los diez meses, que ch01 no dice. | justo | True | False | — | 10 MESES |
| ch02 | 2 | True | La voz cuenta que ella confiaba en lo que venía; la ficha da el motivo de irse, que no tenían nada, y eso la voz no lo dice. | None | Sin sello. | justo | True | False | — | None |
| ch02 | 3 | True | La voz dice 'un acuerdo entre los dos gobiernos'; la ficha pone nombre, régimen y año en la misma palabra. | None | Sin sello. | justo | True | False | — | None |
| ch03 | 4 | True | La voz insiste en que todo se hizo con lo que sobraba; el 5% de asbesto convierte ese suelo en una cifra. | None | Sin sello. | justo | True | False | — | None |
| ch03 | 5 | True | Sobre 'los informes eran anteriores', 1930 lleva el saber más atrás que cualquier fecha que da la voz. | False | AVISO repite lo que la oración dice con 'advirtió por escrito' y no agrega nada; la oración dice 'ese año' sin decir cuál, y el sello puede darlo. | justo | True | True | — | 1948 |
| ch03 | 6 | True | Ata la llegada de Daniel al año récord y al 95% de Wittenoom; la voz no lo dice y le da peso al recuerdo del loop. | None | Sin sello. | justo | True | False | — | None |
| ch04 | 7 | True | Es la frase de Calvo que la voz corta: la voz dice 'no les daba miedo' y la ficha completa con 'nadie nos avisó'. | False | AMENAZA es un adjetivo de editor sobre 'se deshacía entre los dedos'; mejor nombrar el mineral que los chicos tocaban. | justo | True | False | — | CROCIDOLITA |
| ch04 | 8 | True | Quién es hoy el bebé no está en la voz y engancha al público español (P17 permite el más fuerte 'creador de Médico de familia y Los Serrano'). | False | CALMA explica la ironía de 'un hijo y nada más' y la apaga; esa línea funciona mejor sola: quitar el sello. | justo | True | False | — | None |
| ch05 | 9 | True | Después del fallo, la cifra y los 200 afectados son la consecuencia concreta, y la voz no la da. | False | ALARMA no agrega nada sobre 1978; la distancia desde el cierre sigue el patrón de 'veintidós años después' que la voz usa tres oraciones más abajo. | justo | True | False | — | 12 AÑOS DESPUÉS |
| ch05 | 10 | False | Es un dato nuevo, pero en el diagnóstico de Daniel una estadística de 500 muertos lleva la mirada a la masa en el momento más íntimo del video. | False | MEMORIA sobre 'María tenía las fotos' subraya lo obvio; quitar el sello y dejar la pausa. | justo | True | False | D35 · LO QUE HABÍA EN EL POLVO · El asbesto azul: el más mortal de todos · None · Anclada en 'polvo' (idx14), responde al loop L1, qué respiró, sin sacar a Daniel del centro. | None |
| ch06 | 11 | True | Gente que murió por una excursión escolar sube la apuesta sobre los hijos de funcionarios que cuenta la voz. | None | Sin sello. | justo | True | False | — | None |
| ch06 | 12 | False | El nombre de un ministro regional no le dice nada a este público y gasta la ficha del beat de revelación. | False | RABIA le ordena al espectador qué sentir; sobre 'Porque salía caro' lo que falta es cuánto, y una cifra se lee en tres palabras. | justo | True | False | D150 · ADÓNDE VA ESE RÍO · El Fortescue alimenta el agua de Karratha · None · Anclada en 'Fortescue' (idx15), muestra que el asbesto llega al agua de una ciudad, algo que la voz no dice. | 150 MILLONES |
| ch07 | 13 | True | Frente a 'no ha gastado dinero', los 70.000 millones cobrados dan el contraste, y más aún después de los 150 millones del beat 12. | False | SILENCIO pisa el cierre; la pregunta final tiene que llegar limpia: quitar el sello. | justo | True | False | — | None |

#### Huecos

- ch03 beat 6 · D138 · ANTES DE LA INSPECCIÓN · ABA limpiaba el molino antes de cada visita oficial · None · En idx22, cuando la Junta entra al molino: lo que vio ya era la versión limpia, y nada en pantalla cubre idx22-30.
- ch07 beat 13 · D68 · LOS BANJIMA · La mayor tasa per cápita de cáncer por asbesto del mundo · Gordon Legal · En idx4, la muerte de Parker deja de ser un caso aislado; la voz no lo dice y el tramo idx0-6 está vacío.

#### Relojes

Los tres repiten fechas que la voz dice textuales; sobran donde están, y faltan en los saltos que desorientan: la vuelta a 1943 en ch03 idx11 y el salto a 1991 en ch05 idx12.

#### Gancho y pico

El gancho tiene buena ficha, pero INMINENTE contradice la espera de treinta años; con 10 MESES queda la promesa entera. El pico se diluye con los 500 muertos y MEMORIA: va mejor con el asbesto azul sobre 'polvo' y sin sello.

#### Riesgos

- No tocar la ficha de 1930 en el beat 5: es la que sostiene el loop de quién sabía.
- No mover el 95% de 1962 del beat 6: ata a Daniel con el año récord en la oración del recuerdo.
- No cambiar 'Nadie nos avisó de nada' de Calvo ni los 70.000 millones del cierre; cada uno completa exactamente lo que la voz deja abierto.
- Si entra 150 MILLONES en el beat 12, no repetir la cifra de remediación en el beat 13, para que el contraste con las regalías quede limpio.


El resumen del modelo dice «siete sellos» y lista siete; el papel tiene 8 (también AVISO, que sí evalúa en el beat 5). Lo mide la lectura del analista, no el código.

## Tests

- `tests/test_m05_retencion.py` (A) y `tests/test_m01f_compuerta.py` (B, C), con el POST real explotando.
- Ajustados al flujo nuevo: `test_module_f66`, `test_run_pipeline`, `test_module_f39_fase1`, `test_module_f41_cadena`.
- Suite amplia (`c/suite_amplia.log`): **1507 verdes, 30 saltados, 3 xfail, 4 fallas previas** (`m03_merge_timing` ×2 y `gfx_lab` ×2, las de `lab/ESTADO_SESION.md`). `mapa --check`: 161 archivos, 0 fallas.

## Diff por archivo (A–C y arreglos)

```
fase1_5.py                             | 206 ++++++++++---
 qa_form.html                           |   4 +-
 qa_studio.html                         | 109 ++++++-
 qa_studio_server.py                    | 104 ++++++-
 run_pipeline.py                        |  96 +++++-
 script_engine/m01d_particion.py        |  31 ++
 script_engine/m01e_pantalla.py         |   7 +-
 script_engine/m01f_critico.py          | 375 +++++++++++++++++++++++
 script_engine/m01f_prompts/FORMATO.txt |  13 +
 script_engine/m01f_prompts/SYSTEM.txt  |  20 ++
 script_engine/m05_narrative.py         | 132 ++++++++-
 test_module_f39_fase1.py               |  14 +-
 test_module_f41_cadena.py              |   4 +-
 test_module_f66.py                     |  20 +-
 test_run_pipeline.py                   |  63 +++-
 tests/test_m01f_compuerta.py           | 525 +++++++++++++++++++++++++++++++++
 tests/test_m05_retencion.py            | 133 +++++++++
 17 files changed, 1767 insertions(+), 89 deletions(-)
```

## Nombres reales y desvíos del handoff

Existen tal cual: `nombres.nombra`, `nombres.terminos`, `_step_cost`, `aviso_txt`, `cargar_papel`, `descartados.pool_id`, `ficha.respaldo`, `revisor-handoff`, Chrome headless de F66b. No hubo que parar por ninguno.

1. **`tests/`** no existía: lo creé porque el handoff nombra esas rutas. El resto de la suite sigue en la raíz.
2. **`_FORM_PHASES`** no está en `run_pipeline.py`: está en `qa_studio_server.py:1605`. También toqué `qa_form.html`, que el §3 no lista, para que el form muestre `narracion_gate`, y `_preflight` del servidor, para abrir con la narración sola.
3. **`humano_en_escena`** tampoco está en `m01e.entrada`, no lo quita `_para_modelo`. Lo repongo de la escaleta por `n` dentro de m01f, la misma decisión del lab v3; m01e no se toca, así su USER y su caché no cambian.
4. **Campos del papel en D:** el «dato» es `texto`; el «ancla» son `palabra`, `oracion` y `sentence_idx`; `aporta` vive en la ficha y va al nivel del beat como pide el §5 D; `autor` solo existe en citas.
5. **`editar_parrafo` también corre el juez** (el §C.2 lo pide solo en `aceptar_deberia`): US$ 0, y si no, la pestaña mostraría métricas viejas. Decisión mía.
6. **Párrafos sin texto: se eliminan, no se conservan.** `tag_cap` saltea los vacíos y sus `pico_par`/`intensities` son índices de párrafo: se correrían (test `test_los_vacios_correrian_el_pico_de_tag_cap`). Es la rama que el §C.2 prevé; el POST responde `beats_sin_texto`.
7. **Validación:** `palabras_despues` y `cifras_sin_respaldo` se miden sobre el texto sin marcas, para no repetir el falso positivo del abierto 3 de F67a. `ids` inválidos no se suman al párrafo al aceptar.
8. **`metricas` del pool:** m01f recibe el `evidence_pool` del topic (`_topic_v3`), no `00_pool_v3.json`: difieren. Con ese pool la entrada es la del lab y `reconstruir` da bytes idénticos.

## Lo que queda abierto

1. **La métrica de personaje sigue a la persona equivocada en Wittenoom** (§4, declarado): escaleta `humano` = P16 María Bernal con el rol de Daniel. Rachas, `cap_mas_humano`, `personaje_en_siguientes` y el cociente años/min quedan distorsionados; el crítico lo señala solo en sus riesgos. Sin umbral no frena nada, pero estas cifras no sirven para fijar reglas hasta arreglar el `humano` de esta escaleta.
2. **DEBERÍA no contiguos no se pueden aceptar:** el k=3 (ch05 [4, 7]) sale `aplica: false` por la regla del §C.2, y la pestaña dice «ya no aplica» aunque el texto no cambió. Omar puede editarlo a mano. 1 de 7 en Wittenoom.
3. **Aceptar el DEBERÍA de bloque deja al beat 6 sin texto** (prueba sobre la copia). El §C.2 lo acepta y el POST lo avisa; la escaleta sigue listándolo, y ese párrafo mueve sus `ids` y su pico si lo tuviera. Conviene mirarlo antes de aprobar.
4. **Pendientes de Omar (§9):** escala de nota; DEBERÍA sin truncar a 8 (implementado el voto del analista, **pendiente de Omar**); botón «volver a criticar», no entra.
5. **Re-enganches en los DEBERÍA:** el crítico dice que no toca los re-ganchos, pero el DEBERÍA 2 reemplaza hasta ch03 [31] y lo reescribe. El código no lo compara con `recuerda_loop`; es lo que el rediseño de la corrección tendrá que proteger (DECISIONES 17:25).
6. **Línea de costo por video:** cada topic paga verificador + crítico antes de la compuerta (≈ US$ 3,2 medido aquí).
7. **Copia de prueba sin commitear:** `lab/hyperframes/f67/c/<tid>/` (3,5 MB) queda en disco; se regenera con `etapa_c_prueba.py`.
8. **`python` global sin `faster_whisper`:** `run_pipeline` frena antes de empezar con ese Python. La prueba corre con `viral-video-pipeline/.venv`; la primera pasada de C.4 había frenado ahí y la repetí.
9. **No aprobar el papel m01e-7 de Wittenoom antes que la narración.** Ese papel no trae `narracion_md5`, y el §2 manda respetar uno aprobado sin ese campo. Si se aprueba en la pestaña PAPEL y después se edita la narración, la cadena pasa a la voz con fichas ancladas a oraciones viejas. Sin aprobar, se re-corre solo. Decisión posible: que PAPEL no apruebe sin narración aprobada, o sacar esa excepción ahora que no hay ningún papel aprobado.
10. **`01b_narration_normalized.json` de Wittenoom es de otra narración** (28-oct): `narration_original` no coincide en los 7 caps, y `audio_manager` lo lee primero. La voz va `--from normalizer_gate`, que lo reescribe; `--from audio` directo hablaría el texto viejo, y el md5 de aprobación no lo cubre. También: «María» a secas sí aparece en ch04 y ch05, pero los términos del código son `maria bernal` y `bernal`. Y los «7 iguales» del verificador son por (cap, oración): el texto de la afirmación cambió en 6.
11. **La validación de D no mira las cifras de `sello_pondria`** («150 MILLONES», «12 AÑOS DESPUÉS»): el §5 D pide las de `texto`. Lab, no se cableó.

## Veredicto de revisor-handoff (íntegro)

VEREDICTO: CUMPLE CON OBSERVACIONES

Recalculé lo que se podía sin API. Las pruebas de aceptar/editar las corrí sobre una copia en el scratchpad (`C:\Users\Canada\AppData\Local\Temp\claude\C--CLAUDE-PROJECTS-automatization-videos\6d986205-ac5e-4060-9fec-b50ba6f9aea6\scratchpad\sd`). `_steps/<tid>` real hoy es idéntico a `md5/D_despues.json` (79 archivos, md5 y mtime).

| # | Requisito | Estado | Evidencia |
|---|---|---|---|
| 1 | A: claves y fórmulas de `retencion` | OK | Recalculé por separado palabras, s, %, % acum., años, años/min: coinciden con `06_judge` y con `A_retencion.md`. Pico beat 10 → último párrafo en ch05, idx 23, 74 %, 174 s. Promesa sale de `promesa_gancho` (`m01e_pantalla.py:287`), con prefijo `words_of` (`m05_narrative.py`, `_promesa`). `pytest tests`: 50 passed. |
| 2 | B: SYSTEM/FORMATO byte a byte | OK | md5 de `SYSTEM.txt` = `fb3e5a9e…` = `a/md5.json`; SYSTEM y FORMATO == bloques §4/§5 del handoff F67a (comparados por mí). |
| 3 | B: entrada, validar, `01f_critico.json`, cableado | OK | `m01f_critico.py`: campos del JSON, validación con `fecha` y marcas. `run_guion_v4` va juez → verificación → crítico sin `run_pantalla`; `verificar_narracion` igual y termina en `parada_de_narracion`. Costos 0,72028 + 2,45755 + 0,59762 = 3,7754 (reporta 3,7755 por redondeo). |
| 4 | B: el commit compila y no trae código de C | PARCIAL | `ast.parse` OK en los 8 archivos de `46102e5`. Pero trae `estado_narracion` (que el handoff asigna a C.1), y `parada_de_narracion` imprime `--aprobar-narracion`, flag que recién nace en C. El resto de C (aprobar, `run_papel_aprobado`, `reconstruir`, `editar_parrafo`, `aceptar_deberia`) no está. |
| 5 | C: candado y papel | OK, con hueco | `estado_narracion`, `aprobar_narracion`, `papel_falta`, `run_papel_aprobado` y el candado antes del papel (`fase1_5.py` ~740) están. El `--from` ≠ m01a/m01b salta el guion (`fase1_5.py:726`, línea citada correcta). Hueco: ver riesgo 1. |
| 6 | C: `reconstruir`, `editar_parrafo`, `aceptar_deberia`, `aplica` | OK | `reconstruir` sin cambios da bytes idénticos (3 archivos). Con el Wittenoom real, `aplica` = {1 T, 2 T, 3 F, 4 T, 5 T, 6 T, 7 T}. Para cada DEBERÍA aceptado, las oraciones del cap quedan igual a lo esperado, el resto de los caps no cambia, y el md5 devuelto es el del disco. Aceptar 1, 2, 4, 5, 6, 7 en secuencia anda. El 2 deja el beat 6 sin texto (párrafos 28 → 24). El 3 no aplica (no contiguo), como dice el reporte. |
| 7 | C: GET/POST, pestaña, `etapa_de`/`_paso_*`, §10 | OK, con obs. | Las rutas devuelven 400 ante entradas inválidas. GET `/narracion`: 7 caps, 7 DEBERÍA, 6 `aplica`. `etapa_de` con guion/narración/papel_nuevo/papel y los `_paso_*` en `run_pipeline.py`. `run_pantalla` ya no se llama en `run_guion_v4` ni en `verificar_narracion`; el md5 por bytes del verificador se fue; se borró «guion = no hay 01e_pantalla.md». Observaciones: riesgos 3 y 4. |
| 8 | D: extracción, payload, validación | OK | Handoff md5 `dd4c977e…`. SYSTEM_D `da15cabe…` recalculado por mí, FORMATO_D igual al final del USER. 1 llamada, 0,5976 US$. D_1.md pegado en el reporte (encabezados bajados 2 niveles). El papel tiene 13 fichas y 8 sellos (el modelo dice siete). D35/D150/D138/D68 no están en el papel. La validación no revisa las cifras de `sello_pondria` ('150 MILLONES', '12 AÑOS DESPUÉS'). |
| 9 | Producción intacta | OK | Solo cambian 6 archivos de `_steps`, todos reportados: `06_judge`, `01_v3_costos`, `01b_verificacion.*`, `01f_*`. `01b_narracion_v3` sigue en `c7badfbe…`. `01e_pantalla.*` sin tocar. |
| 10 | Afirmaciones del reporte | OK, con matices | «6 de 7 caps sin P16» es cierto por los términos del código: «María» a secas aparece en ch04 y ch05. Verificador «iguales 7»: son las mismas 7 (cap, oración); el texto de `afirmacion` coincide solo en 1 de 7. El log de la suite amplia dice 1505 / 30 / 3 / 4, igual que el reporte (leí el log, no re-corrí la suite). Los 8 desvíos que listé de «Nombres reales» son ciertos. |
| 11 | Commits y ESTADO | PARCIAL | `DECISIONES.md` con las 3 líneas (18:06, 18:43, 18:59) está en A. Un commit por etapa, D pendiente. `lab/ESTADO_SESION.md` no tiene la tanda F67: la cabecera dice «F67a hecha» y ningún commit lo tocó. El commit C incluyó `SALIDA_C.md` con `exit 1` («faltan librerías») y `c_salida.log`. La corrección (`exit 0`, `VENV` en `etapa_c_prueba.py`) está sin commitear y caerá en el commit D. |
| 12 | Scripts de candado | OK | `python -m pytest tests -q`: 50 passed. `mapa_modulos.py --check`: 161 archivos, 0 fallas. `test_run_pipeline.py`: 68 passed (corrido por nombre de archivo). |

Fuera de alcance:
- `lab/mapa/stickers/fase2a.json`: 685/685 líneas de churn en A y de nuevo en B, sin relación con el handoff. Probablemente salida de `mapa_modulos`.
- `lab/MAPA_PROYECTO.*` y `lab/mapa/stickers/{guion,orquestador}.json`: regenerados por el mapa.
- `diag_234_cap4.py` y `f28/a/f28a.log` figuran modificados, pero ya estaban así antes de F67. No deben entrar al commit D.

Riesgos que el contrato no cubre:
1. El candado de papel se puede saltear por la compuerta del papel. `process_topic` no llama a `papel_falta`, y un papel aprobado sin `narracion_md5` se respeta (§2). El papel actual de Wittenoom no trae ese campo, y la pestaña PAPEL deja aprobarlo antes de aprobar la narración. Si se aprueba y después se edita la narración, `--from normalizer_gate` y `run_pipeline` pasan a la voz con el papel anclado a oraciones viejas.
2. `01b_narration_normalized.json` de Wittenoom (28-oct) es de otra narración: `narration_original` ≠ la actual en los 7 caps, y `audio_manager.py:493` lo lee primero. El md5 de aprobación no lo cubre. Hoy lo salva que `normalizer_gate` siempre lo reescribe; `--from audio` directo hablaría el texto viejo. El reporte menciona el archivo pero no que está desfasado.
3. En la pestaña, el resaltado y la etiqueta «oraciones […]» usan el `idx` original del crítico, no el actual. Comprobado: tras aceptar el DEBERÍA 4, el 5 sigue `aplica` pero su tramo real empieza en idx 11 y se resalta desde 10. Aceptar anda bien (por texto); falla solo la UI.
4. Docs viejas en `fase1_5.py`: líneas 7, 17, 29, 33-36 y 178 siguen describiendo «verificación → papel → juez» y «--verificar-narracion … papel nuevo».
5. `etapa_de` devuelve `guion` si falta `01b_verificacion.json`, aunque haya papel, voz o assets: un topic viejo sin esa verificación volvería a pagar el guion. Es lo que pide §C.3.

## Adenda de CC

El veredicto es sobre el código de C (`da63ddc`) y la primera versión de este reporte. Después de recibirlo, sin nueva revisión, hice esto; el commit `fix(F67 C)` lo trae, con test y suite amplia re-corrida:

- **Riesgo 1, en parte:** `process_topic` ahora llama a `papel_falta` después del candado de narración. Un papel que salió de otra narración para aunque esté aprobado, también con `--from`. Es un agregado mío, no del §C.1: lo decidí por «nada río abajo de la narración corre sin su md5». **Sigue abierto** lo que el §2 manda respetar: un papel aprobado sin `narracion_md5` (abierto 9).
- **Riesgo 3:** GET `/narracion` trae `oraciones_actuales` por DEBERÍA y la pestaña resalta y rotula esos índices. Test: `test_get_narracion_oraciones_actuales_tras_aceptar_otro`.
- **Riesgo 4:** docstring y comentarios de `fase1_5.py` puestos al día con el flujo nuevo.
- **Fila 11:** `SALIDA_C.md` y `c_salida.log` con `exit 1` quedaron en el commit C; la versión correcta, `exit 0`, entra con este cierre. `ESTADO_SESION.md` actualizado en el commit D.
- **Fila 4:** `estado_narracion` entró en B porque la PARADA de B lo necesita. Los commits B se armaron por índice, porque el código de C ya estaba en disco mientras corría la Etapa B: ese commit no se corrió aparte, solo compila.
- **Fila 10 y riesgo 2:** van en los abiertos 1 y 10, con sus matices. El abierto de D sobre `sello_pondria`, en el 11.
- **Fuera de alcance, `fase2a.json`:** el churn no viene de `mapa_modulos`: lo causó mi script de stickers en A, con otra sangría, y lo revertí en B. El cambio neto son 2 líneas.
- **Riesgo 5:** queda como lo pide el §C.3; hoy Wittenoom es el único topic con papel.
