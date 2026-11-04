# Crítica de la narración

`m01f-1` · claude-opus-5-5 medium · US$ 0.6900 · tokens in 90447 · out 16412 · 154.8 s · 1 intento(s) · narración `3fc4168d8fc270ba0af8122d8c3799d7`

**Nota total:** 7.0

## Resumen

- Retiene bien el gancho (pie vendado, «casi treinta años», «miles de kilómetros») y el pico de ch05, porque el hilo de Daniel con cuenta regresiva se sostiene hasta el diagnóstico.
- Hay dos valles. El primero, entre el 34 % y el 45 %: ch03:12-22 encadena informes, instituciones, una sigla sin explicar (ABA) y cinco años. El segundo, después del pico: ch06 suma nombres nuevos (Mercedes, Markey) y repite lo del mapa; ch07 suma otros dos (Parker, Orellana) y vuelve a enumerar años.
- Primero, compactar ch03:12-22 y agregar un re-gancho al final de ch05, que hoy cierra el loop principal y deja 169 s sin promesa. Aviso: `metricas.personaje` cuenta a María Bernal, pero el humano del video es Daniel Écija, así que las rachas del código no sirven y las recalculé con Daniel.

Personaje según la narración: P17 Daniel Écija (padre) · 16 oraciones

## Métricas por cap (código)

| cap | palabras | s | % | % acum. | años/min | racha sin personaje |
|---|---|---|---|---|---|---|
| ch01 | 181 | 62 | 10 | 10 | 0.97 | 7 |
| ch02 | 220 | 75 | 12 | 23 | 2.4 | 16 |
| ch03 | 384 | 131 | 22 | 44 | 2.29 | 10 |
| ch04 | 232 | 79 | 13 | 57 | 0.76 | 12 |
| ch05 | 267 | 91 | 15 | 72 | 3.3 | 8 |
| ch06 | 299 | 102 | 17 | 89 | 1.76 | 12 |
| ch07 | 197 | 67 | 11 | 100 | 5.37 | 10 |

## Gancho

- Promesa cumplida: True
- En unos 35 s (idx 0-6) ya están el minero, el pie, el amianto, los diez meses, los casi treinta años y la distancia. El mapa borrado y los tres millones de toneladas llegan cerca de los 50 s, y la pregunta «¿qué respiraba?» obliga a quedarse.

## Capítulos

| cap | nota | personaje en voz | oraciones seguidas sin personaje | fuerte | débil | re-enganche |
|---|---|---|---|---|---|---|
| ch01 | 8.5 | True | 5 | idx 2 anticipa la muerte y la distancia sin decir qué la causa; idx 11 («Y no se queda quieto») deja abierta la amenaza del presente. | idx 3 («La foto es en blanco y negro») es relleno y además choca con «sepia» en ch05:9. | «Alguien tuvo que llevar a ese hombre hasta allí… hubo un baile»: promete el origen y lo cumple de inmediato. |
| ch02 | 7.0 | True | 9 | Del baile al barco en cuatro días, con la cita de María (idx 3): ternura con un reloj corriendo. | idx 9-17 pasan a Víctor Calvo sin decir quién es ni qué relación tiene con los Écija, y Daniel y María desaparecen de su propio viaje. | «La tierra más roja que Víctor había visto» promete el lugar, pero lo ancla en un chico que el espectador no ubica. |
| ch03 | 6.0 | True | 10 | El suelo hecho de relaves (idx 6-9) y la cuenta regresiva «faltaban catorce / cinco años» que ata los informes a Daniel. | Es el capítulo más largo (134 s, 22 %) y en idx 12-22 acumula inspectores, médico, empresa, tribunal y reguladores; ABA aparece en una cita sin explicar. | «Un recién casado de Madrid se bajaba de un avión en esa misma pista»: lleva directo a ch04 con Daniel. |
| ch04 | 8.0 | True | 8 | Los chicos con el amianto en la boca (idx 6-8) y el parto y el bautizo: es el capítulo más humano y menos denso (0,76 años/min). | idx 1 cierra la explosión con un descargo documental que corta la tensión y desperdicia el motivo de quedarse (Q16). | «Creyeron que se llevaban de Wittenoom un hijo y nada más»: promesa fuerte, abre la pregunta de si salieron a tiempo. |
| ch05 | 8.5 | True | 4 | 1988 queda atado a Daniel («le quedaban tres años»), y el mesotelioma enlaza con McNulty y con el pie: la densidad de años (3,45/min) no pesa porque cada fecha cuenta hacia su muerte. | Ninguno serio. idx 1-2 (Vernon, costos) es el único tramo institucional y es corto. | «Daniel había estado en Wittenoom diez»: remate perfecto, pero cierra todo y no promete nada del capítulo siguiente. |
| ch06 | 6.0 | True | 11 | El policía del aeropuerto (idx 4-6), «Daniel Écija es uno de ellos» (idx 12) y «Porque salía caro» (idx 22). | idx 10-16 traen una directora con cargo largo y repiten casi literalmente lo del mapa y las señales de ch01:8-9. | «En esa tierra vivía un hombre que no podía irse»: bueno, promete un personaje nuevo. |
| ch07 | 7.0 | True | 10 | Parker («no puedo alejarme») y la vuelta final al retrato del pie vendado y al mapa. | Es el capítulo más denso del video (5,37 años/min): suma Orellana sin rol y vuelve a enumerar 1944/1948/1957 en el último minuto. | «Lo que sobró de la mina, sí»: cierre espejo de ch01:8-10. |

## Loops

| pregunta | abre | paga | se recuerda |
|---|---|---|---|
| ¿Qué le hizo Wittenoom a Daniel en diez meses si lo alcanzó a miles de kilómetros? | ch01:2 | ch05:16 | True |
| ¿Por qué no cierra una herida hecha por un mineral? ¿Qué hay en ese polvo? | ch01:5 | ch05:12 | True |
| ¿Quién lo llevó hasta allí? | ch01:12 | ch02:7 | True |
| Los relaves siguen ahí y no se quedan quietos: ¿adónde van? | ch01:11 | ch06:19 | True |
| Si estaba escrito desde 1944, ¿quién sabía y quién decidió seguir? | ch03:11 | ch05:6 | True |
| ¿Salieron a tiempo? | ch04:18 | ch05:10 | True |
| ¿Quién va a sacar la primera palada? | ch06:20 | None | True |

## Promesas nuevas (código)

⚠ calculado sobre la narración actual, no la que vio el crítico (actual `cd0fe3bfcc81bf45871f575c3c0077dc`, crítico `3fc4168d8fc270ba0af8122d8c3799d7`)

| desde | hasta | s |
|---|---|---|
| ch01:2 | ch01:5 | 21 |
| ch01:5 | ch01:11 | 24 |
| ch01:11 | ch01:12 | 2 |
| ch01:12 | ch03:11 | 139 |
| ch03:11 | ch04:18 | 150 |
| ch04:18 | ch06:20 | **182 (máx.)** |
| ch06:20 | fin | 81 |

Segundos estimados por palabra (0.34 s/palabra, sin pausas ni title cards); sin umbral.

## Pico

- ch05 · acumulado 72 % · 169 s después
- El pico paga el loop principal y ch05 termina en un cierre total. Las primeras oraciones de ch06 siguen con la familia (el hijo), lo que ayuda, pero después llegan nombres nuevos y un párrafo repetido justo cuando el espectador siente que la historia ya terminó.

## Cierre

Vuelve al gancho y lo paga: el retrato, el pie vendado, los diez meses, los casi treinta años y el mapa borrado, con los relaves todavía ahí. Le resta fuerza el recuento de años de idx 7, que llega justo antes.

## DEBERÍA

### 1. ch02 · oraciones [9, 16, 17] · 27 → 47 palabras

- **Sale:** La entrada de Víctor sin presentación y el final del capítulo que deja a Daniel y María fuera de su propio viaje.
- **Por qué se van:** Después de 75 s con la pareja, la voz pasa a un desconocido y el espectador pierde a quién seguir.
- **Ids:** P21, T36, Q14, T38
- **Cifras sin respaldo:** — · **Marcas:** […]

> Víctor Calvo, el hijo de Milagros, había hecho esa misma travesía unas semanas antes, con siete años. […] Del barco, a un avión pequeño. Del avión, a la tierra más roja que Víctor había visto en su vida. Semanas después, Daniel y María bajaron a esa misma tierra.

### 2. ch03 · oraciones [12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22] · 161 → 152 palabras

- **Sale:** La sigla ABA sin explicar, el renglón de los reguladores (idx 22) y la cita del tribunal recortada en dos oraciones; se conservan 1944, Saint, el tribunal de 1957 y la cuenta regresiva, que ch05 y ch07 necesitan.
- **Por qué se van:** En el tramo más largo del video se suceden cinco organismos y una sigla sin contexto, y Daniel solo aparece una vez entre medio.
- **Ids:** D19, Q45, D84, Q46, Q53, Q54
- **Cifras sin respaldo:** — · **Marcas:** —

> Los informes eran anteriores a la boda, al barco y al avión. En 1944, el inspector de minas y el ingeniero de minas adjunto del Estado ya informaban sobre el problema del polvo. En 1948, un médico joven llegó en avión, vio el molino y escribió a Perth: «En un año o dos, ABA producirá la cosecha más abundante y letal de casos de asbestosis de la literatura mundial». ABA era la empresa de CSR que explotaba la mina. El médico se llamaba Eric Saint. La respuesta la contó él: «Me desestimaron y, de hecho, me tildaron de alborotador». La empresa tenía otra lectura: «El mero hecho de que haya nubes de polvo no significa que ese polvo sea peligroso». Faltaban catorce años para que Daniel Écija bajara de ese avión. En 1957, un tribunal laboral entró al molino y escribió: «Las condiciones dentro del molino eran extremadamente polvorientas». Faltaban cinco años.

### 3. ch04 · oraciones [1] · 26 → 39 palabras

- **Sale:** El descargo «no hay otro documento que lo confirme» y la versión «alguien murió».
- **Por qué se van:** Corta la tensión de la llegada y desperdicia la razón por la que Daniel se quedó, que es la que hace doler «diez meses».
- **Ids:** Q16
- **Cifras sin respaldo:** — · **Marcas:** —

> El hijo cuenta que el primer día de trabajo de su padre hubo una explosión y murieron varias personas. Cree que su padre pensó entonces en irse cuanto antes, pero María estaba embarazada y no tenían dinero. Se quedaron.

### 4. ch05 · oraciones [21] · 6 → 16 palabras

- **Sale:** Nada: se conserva idx 21 tal cual y se agrega una oración después.
- **Por qué se van:** El pico paga el loop principal y cierra todo; con 169 s por delante, el espectador no tiene ninguna pregunta abierta.
- **Ids:** D90, Q33
- **Cifras sin respaldo:** — · **Marcas:** —

> Daniel había estado en Wittenoom diez. Y no fue el único que se llevó Wittenoom adentro.

### 5. ch06 · oraciones [10, 11, 13, 14, 15, 16] · 92 → 78 palabras

- **Sale:** La repetición de ch01:8-9 (mapa y señales) y la presentación de Markey en una oración aparte.
- **Por qué se van:** Después del pico, un cargo nuevo y un dato ya escuchado le dicen al espectador que la historia ya se contó.
- **Ids:** Q33, D90, T80, D31
- **Cifras sin respaldo:** — · **Marcas:** —

> Melita Markey, que dirige la Sociedad de Enfermedades del Asbesto de Australia, dice que el gobierno dejó de contar los muertos en dos mil, que ahora pueden ser más de cuatro mil, y que la cifra sigue subiendo. Daniel Écija es uno de ellos. Y entre los que enferman ahora hay hijos de policías y maestros que trabajaron en el pueblo. El pueblo, mientras tanto, dejó de existir en los papeles: en junio de 2007 fue abolido oficialmente.

### 6. ch07 · oraciones [1, 7] · 43 → 46 palabras

- **Sale:** El nombre de Orellana sin rol y la lista de tres años en el último minuto.
- **Por qué se van:** En el capítulo más denso del video, un nombre que no se explica y un repaso de fechas frenan la llegada al retrato.
- **Ids:** T92, D19, Q45, Q54
- **Cifras sin respaldo:** — · **Marcas:** [idx 1], […], [idx 7]

> [idx 1] En 2023, un relator de la ONU visitó Australia y lo entrevistó sobre la contaminación y el daño que no se iba. […] [idx 7] Quién sabía está escrito desde 1944: lo escribieron los funcionarios de minas, lo escribió Eric Saint, lo escribió el tribunal que entró al molino.

## Reglas generales candidatas

- El humano del video no puede faltar más de 10 oraciones seguidas en ningún capítulo. · *medible:* racha_max_sin_personaje ≤ 10 por capítulo, con metricas.personaje.terminos tomados de escaleta_video.humano (nombre y apellido del humano real, no del campo mal cargado). · *por qué:* Los valles de este video coinciden con rachas de 10 o más oraciones sin Daniel (ch03, ch06, ch07).
- El capítulo más largo antes del 50 % no puede ser también el más cargado de instituciones y años. · *medible:* En los capítulos con pct_acumulado ≤ 50, el de mayor pct no debe tener anios_por_min mayor que 2 veces el de cap_mas_humano. · *por qué:* ch03 dura 134 s y concentra los informes en el tramo donde más gente se va.
- El capítulo del pico debe terminar con una oración que abra algo pendiente si después queda más del 20 % del video. · *medible:* Si 100 − pico.pct_acumulado > 20, la última oración del capítulo del pico o la siguiente contiene un término de un loop con paga_beat posterior al pico. · *por qué:* ch05 cierra el loop principal con 169 s por delante y sin promesa.
- No introducir más de un nombre propio nuevo en el último 15 % del video. · *medible:* Contar nombres propios cuya primera aparición en caps cae en capítulos con pct_acumulado > 85: debe ser ≤ 1. · *por qué:* ch07 suma Parker y Orellana a un minuto del final.
- El capítulo de cierre no debe ser el más denso en años. · *medible:* anios_por_min del último capítulo ≤ promedio de anios_por_min de todos los capítulos. · *por qué:* ch07 tiene 5,37 años/min, el máximo del video, justo antes de volver al retrato.

## Riesgos

- metricas.personaje está cargado como María Bernal (P16), pero el rol y la fuente corresponden a Daniel Écija, así que las rachas y personaje_en_voz del código son inválidas: corregir los términos antes de usar las reglas.
- El DEBERÍA de ch02 modifica el re-gancho de beat 3 para hacerlo más fuerte (se agrega «Daniel y María bajaron a esa misma tierra»): verificar que las fechas de T36 y T38 sostengan «semanas».
- El DEBERÍA de ch05 agrega una oración después del remate del pico: no tocar idx 19-21, que funcionan como cierre emocional.
- En ch03 no hay que cortar 1944, Saint, el tribunal de 1957 ni McNulty 1962: ch05:11 y ch07:7 dependen de ellos. El corte de idx 22 pierde D20 (reguladores), que solo era apoyo de beat 6.
- En ch04:1 se quita el descargo documental: confirmarlo con quien revisa hechos, porque Q16 es solo testimonio del hijo.
- Credibilidad, no retención: ch01:3 dice «blanco y negro» y ch05:9 dice «sepia» para la misma foto, que es la imagen del gancho y del cierre; conviene unificar.
