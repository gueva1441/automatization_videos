# F67 Etapa C — la compuerta de narración

## 1. La PARADA (`run_pipeline --topic <tid> --batch`)

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

## 2. GET /narracion, resumido (topic real)

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

## 3. Prueba sobre la copia (`lab/hyperframes/f67/c/<tid>/`)

### Reconstruir sin cambios

Los 3 archivos con los mismos bytes: {'01a_skeleton.json': True, '01b_narration.json': True, '01b_narracion_v3.json': True}

### Qué DEBERÍA aplican hoy

{1: True, 2: True, 3: False, 4: True, 5: True, 6: True, 7: True}

### Aprobar

`{'por': 'Prueba', 'fecha': '2026-10-31', 'md5': '778d3e1dcd4ca545453f7a29b6a92bb3'}` · estado: (True, 'narración aprobada por Prueba (2026-10-31), md5 778d3e1d…') · md5 sigue `True`

### Aceptar DEBERÍA 2 (ch03, 21 oraciones, cruza 5 párrafos)

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

### Editar el párrafo 5

Antes: (True, 'narración aprobada por Prueba (2026-10-31), md5 a2693169…')

Respuesta: `{'i': 5, 'beat': 4, 'md5': 'e87e9cdee16101b37f8645b69295c380'}`

md5 cambió: `a2693169…` → `e87e9cde…` · la aprobación cayó: (False, 'la narración no está aprobada')

### Métricas vigentes en la copia

`retencion.total_palabras` 1797 · pico ch05 71 %

Archivos del topic REAL que cambiaron durante la prueba: ninguno
