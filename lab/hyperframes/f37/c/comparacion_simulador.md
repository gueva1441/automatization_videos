# Comparación en seco: F37 (Vajont) contra `lab/hyperframes/f36/REVISION_PAPEL.md`

Solo lectura. No se corrió el pipeline ni ningún modelo. Fuentes: `f37/c/01e_pantalla.md/.json/.raw.json`, `f37/c/GUION_PANTALLA.json/.md`, `f37/c/resumen_guion.txt`, `f37/HANDOFF_F37_papel_y_colocar.md` §C.3, y para «antes» `f36/c/01e_pantalla.md` y `f36/d/GUION_PANTALLA.json`. Código leído solo para entender un solape: `script_engine/pantalla_colocar.py`.

Convenciones: `t_mp4` es el segundo del mp4 final. F37 tiene `intro_s` 2.5 (sin tarjeta) y F36 3.0, así que el mismo instante del cap cae 0.5 s antes en F37. «Papel» = lo que eligió el autor (m01e-2, 2 intentos, USD 0.7649). «Pantalla» = lo que dejó Fase 2.

## Lo primero que hay que saber

1. De las 7 expectativas de §C.3: 5 cumplen (gancho en las primeras oraciones, T39 de vuelta, D47 y D105 juzgados por el autor, ninguna ficha > 6 s; el «ningún pico vacío» cumple en el papel pero no en pantalla), 1 cumple el efecto pero no el mecanismo (Q43 cayó porque el autor lo descartó viendo `fecha: desconocida`, no por la validación 1c, que nunca disparó) y 1 cumple a medias (los 8 cortes de F36: 1 colocado por mover, 2 colocados porque el papel los cambió de sitio, 3 sin colocar con lista de intentos, 2 que el papel ya no propone).
2. **Hay un pico sin ficha en pantalla: ch07 b12.** El autor reemplazó Q14 (la ironía de Leone, «muy bueno» en el contrato) por T85, y T85 no entró en Fase 2 porque el reloj `20 FEB 1968` ocupaba ese tramo. En F36 ese beat tenía Q14. Es una regresión respecto de F36 en ese beat.
3. El gancho quedó anclado en [1] (15.22 s en vez de 86.24 s) pero con el mismo dato de F36 (D131), que además **adelanta unos 70 s el giro de ch01 [14]-[15]** («vino por encima de él»). El filtro de spoiler no lo ve porque compara cifras.
4. El reintento **reescribió el papel entero** (no solo lo preguntado) y perdió cosas sin descarte registrado: D128 (1.910 muertos, estaba en el intento 1), Q14, el sello AVISO, el sello ALARMA, la tarjeta fecha-hora.
5. La tarjeta fecha-hora quedó en `null`: en pantalla hay un marcador «⚠ falta fecha-hora» de 3.0 s en el segundo 0 y el chequeo «tarjeta fecha-hora» pasó de ✓ a ✗.

---

## 1. Tabla línea por línea de «Cap por cap (DEBERÍA)»

Columnas: cap·beat · DEBERÍA (resumido) · F37 papel · F37 en pantalla (t_mp4, texto, dur) · ¿salió solo por las reglas generales? · por qué.

| # | cap · beat | DEBERÍA | F37 papel | F37 en pantalla | ¿Salió solo? | Por qué |
|---|---|---|---|---|---|---|
| 1 | ch01 b1 gancho | A: D118 «LA PRESA DEL VAJONT · 266 m» en [1]. B: D195 «LONGARONE · 1.269 de 1.328» en [2]. Nada en [15] (1:26) | D131 «SALTO DEL AGUA · Más de 260 metros» en [1] sobre «presa» | 15.22 s · «SALTO DEL AGUA · Más de 260 metros» · 2.5 s (el mínimo) | **En parte** (el ancla sí; el dato es gusto) | El ancla en [1] salió con el prompt m01e-2, pero **solo en el intento 2**: el intento 1, con el mismo prompt, dejó D131 en [15]. El reintento no pedía mover el gancho (sus 6 motivos son otros), así que no hay regla que lo garantice; fue el modelo. El dato no es ni A ni B: es el mismo D131 de F36. Dos problemas: (a) las fuentes no coinciden en la altura (D123 250, D215 200, D44 260), sigue sin resolverse; (b) en [1] la voz dice «la presa… sigue en pie» y recién en [15] «vino por encima de él», unos 70 s después (en F36 la ficha caía a 86.24 s, 85.7 s en el reloj de F37). La ficha dice «SALTO DEL AGUA» 70 s antes que la voz. El `aporta` del modelo afirma que «la voz dice que la ola pasó por encima», lo cual es falso en [1]. Compuerta de Omar. |
| 2 | ch01 sello | PÁNICO [4] | PÁNICO [4] | 26.64 s · PÁNICO · 2.5 s | Sí | Sin cambios respecto de F36 (27.14 s con el reloj de entonces). |
| 3 | ch02 b2 | D117 «SESIÓN DEL CONSEJO SUPERIOR · 13 de 34» se queda; F37: mover, no cortar | D117 [papel] «ACTA DEL CONSEJO SUPERIOR · Solo 13 de 34 representantes presentes» en [2] sobre «aprobó» | 123.3 s · «ACTA DEL CONSEJO SUPERIOR · Solo 13 de 34 representantes presentes» · 4.2 s · movido 21.24 → 19.20 s | **Sí** | Caso de manual de B.1: F36 lo cortó por el crítico («tapa el documento»); F37 probó otro instante de la misma oración («1 · inicio de la oración»), el crítico lo dejó pasar y entró. Cambia «SESIÓN» por «ACTA» y suma «Solo»; el `aporta` incluye «procedimiento irregular», que está en D117. |
| 4 | ch02 b2 sello | CALMA [6], cortado (rostros); F37: mover de posición | CALMA [6] (igual) | **Sin colocar.** 5 intentos | **No** (con su lista de intentos, como pedía el handoff) | Palabra de más peso 58.18 s (crítico: estorba en los dos lados; derecha por rostros y Vespa, izquierda por el mercado); inicio de la oración 56.14 s (cruza el corte de la escena 5 a 56.17 s); oración siguiente [7] 61.08 s (crítico: estorba en los dos lados). La escalera funcionó como estaba escrita; el que no deja es el crítico. |
| 5 | ch02 b3 PICO | D47 «DESMORONAMIENTO DEL TOC · 2 km de frente y 600 m» en [11] | D47 «FRENTE DEL DESMORONAMIENTO · 2 km de frente y 600 m de desarrollo vertical» en [11] sobre «desmoronamiento» | 190.7 s · «FRENTE DEL DESMORONAMIENTO · 2 km de frente y 600 m de desarrollo vertical» · 4.73 s · movido 84.70 → 86.60 s a [12] (inicio de la escena 9) | **Sí** | A.4: el código encontró el «2» en ch03 [17] («casi dos kilómetros de largo»), se lo preguntó al autor y este contestó «otro hecho» (queda escrito: «Los 2 km de la fisura de ch03 son otro hecho»). Fase 2 respetó el juicio. Después B.1 lo corrió a la oración siguiente porque la palabra ancla no tenía tiempo de lectura antes del corte. Cae una oración después de la que pedía el contrato; el contrato permitía mover. |
| 6 | ch02 b3 sello | AMENAZA [10] | AMENAZA [16] | 224.88 s · AMENAZA · 2.5 s | Sí (el papel lo corrió de [10] a [16]) | El contrato lo daba por bueno sin tocar. El autor lo pone en [16] ya en el intento 1, seguramente porque ahora hay ficha en [11]. En F36 caía a 176.34 s; ahora a 224.88 s. Neutro. |
| 7 | ch03 b4 PICO | T16 «LA VÍCTIMA DE PONTESEI · Arcangelo Tiziani» [3] se queda; duración ≤ 6 s | **T16 descartado** [otro]: «el nombre no entra en la oración de la ola… ponerlo antes adelantaría “Un trabajador murió”». En su lugar T15 «ROCA CAÍDA AL LAGO · 3 millones de metros cúbicos» en [1] | 252.14 s · «ROCA CAÍDA AL LAGO · 3 millones de metros cúbicos» · 3.07 s | **No en contenido; sí en duración** | La duración se arregló (la ficha más larga de F37 es 4.73 s; T16 había durado 12.74 s). Pero el contenido cambió: T15 es el dato que el modelo de F36 había descartado como «no suma frente al nombre de la víctima». El contrato dijo que el nombre humaniza. Gusto: Omar decide. T15 también pasó por pregunta de A.4 («3» vs «tres o cuatro minutos» de ch06 [6]) y el autor dijo «otro hecho». |
| 8 | ch03 b5 | D49 «ANCHO DE LA FISURA · Más de 1 metro» [17] | D49 «ANCHO DE LA FISURA · Más de 1 metro de ancho» [17] | 350.54 s · «ANCHO DE LA FISURA · Más de 1 metro de ancho» · 2.73 s · movido 113.10 → 105.84 s | Sí | Se movió a «1 · palabra de más peso» porque la palabra ancla no tenía 2.7 s antes del corte (le faltaban 0.1 s). Texto redundante («ANCHO … de ancho»); detalle de estilo. |
| 9 | ch03 b5 sello | INMINENTE [18], cortado (tapa la fisura); F37: mover de posición | **Ya no está en ch03.** INMINENTE pasó a ch05 b9 [26] | 672.707 s (ch05) · INMINENTE · 2.5 s | **No** (lo resolvió el papel, no la colocación) | El autor lo mudó de cap, al beat vacío ch05 b9 (la noche del párroco). Colocó sin moverse. ch03 b5 quedó sin sello; el crítico nunca volvió a juzgar la fisura. |
| 10 | ch04 b6 | T39 «ROCA QUE AMENAZA ERTO · 50 millones de m³» en [6] | T39 «DERRUMBE QUE ADVERTÍA MERLIN · 50 millones de metros cúbicos de roca» en [6] sobre «advertencia» | 423.52 s · «DERRUMBE QUE ADVERTÍA MERLIN · 50 millones de metros cúbicos de roca» · 4.33 s | **En parte** | Resultado: está. Mecanismo: A.2 (verificar «la voz ya lo dice») **no se ejercitó con T39**: el modelo ya lo había elegido en el intento 1. Tuvo pregunta de A.4 («50» vs «aumento del 50%» de ch05 [17]) y el autor contestó «otro hecho». El caso que sí ejercitó A.2 fue D68 (ver 2.2). |
| 11 | ch04 b7 PICO | D105 «ENEL · creado por ley en diciembre de 1962» en [16] | D105 «CREACIÓN DE ENEL POR LEY · diciembre de 1962» en [15] sobre «ENEL» | 486.267 s · «CREACIÓN DE ENEL POR LEY · diciembre de 1962» · 2.73 s · movido 104.80 → 106.27 s a [16] (inicio de la escena 10) | **Sí** | A.4: «1962» vs ch04 [14] («noviembre de mil novecientos sesenta y dos»); el autor dijo «otro hecho» y Fase 2 lo respetó. B.1 lo movió a la oración [16], justo la que el contrato pedía. |
| 12 | ch04 b7 sello | AVISO [14], cortado (cruza el corte); F37: mover antes del corte | **Sin AVISO.** En el intento 1 estaba en ch03 b4 [9]; el intento 2 lo sacó | No está | **No** (se perdió en el papel) | No figura en «sin colocar» ni en «Lo que cayó» ni hay motivo escrito: los sellos no tienen lista de descartes. El pico ch04 b7 queda sin sello (la ficha D105 sí está). Se pierde un sello que el contrato valoraba, sin que nadie lo diga. |
| 13 | ch05 b8 PICO | Q50 «CARTA DEL MUNICIPIO DE ERTO · “en continua aprensión y en continua alarma”» (~70 car.) en [7] | **Q50 descartado** [otro]: «solo cabe una ficha por beat y se eligió el dato con cifra». Ficha D161 «LADERA CON EL AGUA A 710 M · 2 cm por día» en [0] sobre «centímetro» | 512.047 s · «LADERA CON EL AGUA A 710 M · 2 cm por día» · 2.53 s · movido 10.26 → 3.08 s (inicio de la oración) | **No** (gusto) | El pico tiene ficha, pero no la que pedía el contrato. Q50 no entra al papel, así que no se probó nada de lo nuevo para citas (ver observaciones). D161 es un dato nuevo (el contrato no lo mencionaba): pasó por pregunta de A.4 (el «2» era «el dos de octubre» de ch05 [2]) y el autor contestó bien. Cae a 3.08 s del cap, en el primer segundo de voz del capítulo. |
| 14 | ch05 b8 sello | SILENCIO [10] «De la ola no hablaba nadie», cortado (corte); F37: mover antes del corte | SILENCIO [10] (igual) | **Sin colocar.** 4 intentos | **No** (con su lista) | Palabra de más peso 71.94 s: cruza el corte de la escena 7 (74.13 s). Inicio de la oración 71.66 s: cruza el mismo corte (aritmética mía: 71.66 + 2.5 = 74.16 s, es decir **pasa por 0.03 s**). Oración siguiente [11] 74.14 s: el crítico dice que estorba en los dos lados (cartel «STRADA CHIUSA»; los hombres mirando hacia arriba). No hay paso 2 porque el corte cae justo al borde de la oración. |
| 15 | ch05 b9 | Q43 «INGENIERO JEFE · “Son sacudidas menores…”» en [15]; Omar decide (la fuente no da fecha) | Q43 descartado [otro]: «la fecha de la cita es desconocida y no se puede anclar a esa noche». Sin ficha | b9 solo tiene el sello INMINENTE (672.707 s) | **Sí en el efecto; no por 1c** | Ver 2.4. El archivo que ve el autor ahora trae `fecha: "desconocida"` (A.1a) y el modelo lo usó. La validación 1c (cita sin fecha sin autor en la voz) no se ejercitó: «fichas fuera 0» en los dos intentos. b9 sigue sin ficha: el contrato dice que eso lo decide Omar. |
| 16 | ch06 b10 PICO | D01 «ROCA DESPRENDIDA · 270 millones de m³ de roca» [3] | D121 «ROCA QUE CAYÓ · 270 millones de metros cúbicos de roca» en [3] sobre «desploma» | 710.087 s · «ROCA QUE CAYÓ · 270 millones de metros cúbicos de roca» · 3.4 s · movido 26.42 → 25.42 s | Sí | Mismo hecho que D01 (el autor lo declara «repetido»: D01 → D121). La duración bajó de 5.44 s a 3.4 s. |
| 17 | ch06 b10 | **+ D195 «LONGARONE · 1.269 de 1.328 habitantes»** en [20] («Longarone ya no.») | D195 ni elegido ni descartado: no aparece en ninguno de los dos intentos | Nada en [20] | **No** (gusto) | Opción de gusto del contrato (el golpe del video). El modelo ni lo mencionó, ni con motivo. Compuerta de Omar. |
| 18 | ch06 b10 sello | COLAPSO [20], cortado (corte); con D195, pasa a [19] o se mueve | COLAPSO en [3] (en el intento 1 estaba en [5]; en F36 en [20]) | 713.907 s · COLAPSO · 2.5 s | **En parte** (colocado, pero lo resolvió el papel) | El autor lo llevó al desprendimiento («se desploma»), junto a la ficha D121 y al punch, 3.8 s después de la ficha. Pasó sin moverse; la escalera de B.1 no se ejercitó con este sello. El momento de «Longarone ya no.» ([20]) quedó sin sello ni ficha. |
| 19 | ch06 b11 | **D128 «MUERTOS, RECUENTO OFICIAL · 1.910 personas»** en [24]; D17 fuera | D128 **no está** (sí estaba en el intento 1, en [24]). D17 y D192 descartados «solo cabe una ficha por beat». Ficha D228 «PREPARATIVOS EN BELLUNO · 1000 camas para refugiados» en [25] | 816.706 s · «PREPARATIVOS EN BELLUNO · 1000 camas para refugiados» · 3.27 s · movido 136.24 → 132.04 s | **No** (gusto, con una falla) | D17 ya no está (bien, según el contrato), pero tampoco D128. Y D128 **desapareció en el reintento sin motivo ni descarte**: es la misma falla que el revisor marcó en F36 («D128 omitido sin motivo»). D228 es un dato nuevo y fuerte (las camas para sobrevivientes que no había). Compuerta de Omar: D128 vs D228. |
| 20 | ch06 b11 sello | RABIA [31], cortado (rostro); F37: mover de posición | RABIA pasó a ch07 b12 [1] (el grito «Presidente, queremos justicia») | **Sin colocar.** 6 intentos | **No** (con su lista) | Peso 10.90 s derecha e izquierda, inicio 7.92 s derecha e izquierda, oración siguiente [2] 18.28 s izquierda y derecha: el crítico dice «estorba» en los seis (rostros de pobladores gritando; titular del diario). ch06 b11 quedó sin sello y la nueva ubicación del autor tampoco entra. |
| 21 | ch07 b12 PICO | Q14 «RESPUESTA DE GIOVANNI LEONE · “Y justicia tendréis”» [1] se queda; **T85 fuera** (un texto por beat; el reloj 20 FEB 1968 ya marca la fecha) | **Q14 descartado** en el intento 1 («una ficha por beat, se eligió T85, que tiene cifra») y ausente del intento 2. T85 «REMISIÓN A JUICIO · contra 11 personas» en [11] sobre «resolución» | **Nada.** T85 «sin colocar». En pantalla solo el punch (877.067 s) y el reloj 20 FEB · 1968 (943.567 s, 9.03 s) | **No. Regresión respecto de F36** | F36 tenía Q14 en pantalla (877.567 s, 5.26 s). F37 invierte lo que pedía el contrato. T85 cayó en Fase 2 con 3 intentos, todos «se solapa con reloj»: palabra ancla 91.26 s, inicio de la oración 84.70 s, oración siguiente [12] 94.00 s. Dato raro: el reloj termina a 93.73 s en pantalla y el tercer intento empezaba a 94.00 s. Por el código (`pantalla_colocar.py`, líneas 328-359) el reloj se coloca **antes** que las fichas con su intervalo sin recortar (`hasta_el_corte` lo corta después), así que seguramente el filtro lo ve más largo de lo que se ve. No lo verifiqué corriendo nada. Es un hueco de la regla de colocación: el reloj le gana a una ficha de pico. |
| 22 | ch07 b13 | D245 «CONDENA A MONTEDISON · 55.645.758.500 liras» [18] | D245 «MONTEDISON A LONGARONE · 55.645.758.500 liras» [18] sobre «indemnización» | 986.967 s · «MONTEDISON A LONGARONE · 55.645.758.500 liras» · 2.8 s | Sí | La duración bajó de 7.38 s a 2.8 s. En el intento 1 el autor había puesto T92; en el 2 volvió a D245 (el contrato lo daba por bueno). |
| 23 | ch07 sello | MEMORIA [22] | MEMORIA [21] | 1007.787 s · MEMORIA · 2.5 s | Sí | Se corrió una oración. En el intento 1 estaba en ch06 b11 [23]. |
| 24 | (opcional) ch06 | D84 «dos bombas de Hiroshima» en [5]; solo si Omar lo quiere | No aparece | — | No (opcional, gusto) | No se forzó, como pedía el handoff. |

---

## 2. Las 7 expectativas de §C.3

| # | Expectativa | Veredicto | Evidencia |
|---|---|---|---|
| 2.1 | Gancho anclado en las primeras oraciones de ch01 | **Cumple** (con reparos) | D131 en [1] sobre «presa», 15.22 s en el mp4 (F36: [15], 86.24 s). Reparos: se logró solo en el intento 2, sin motivo de reintento que lo pidiera; y el dato adelanta el giro de [14]-[15] (fila 1). |
| 2.2 | T39 de vuelta en ch04 | **Cumple** | T39 en ch04 b6 [6], 423.52 s, 4.33 s. Lo puso el modelo ya en el intento 1; A.2 (verificar «la voz lo dice») no fue lo que lo trajo. A.2 sí actuó con D68: el autor dijo «la voz lo dice», el código buscó «1,5» en la voz, no lo halló y lo devolvió como candidato; el modelo lo volvió a descartar «voz_lo_dice». **El código se equivocó**: la voz de ch04 [14] dice «más de un centímetro y medio por día» (el 1,5 en palabras). El `.md` publica «falso: la voz no dice [1,5]» sobre un descarte que era correcto. Inocuo esta vez, pero la verificación no convierte «centímetro y medio». |
| 2.3 | Ningún pico vacío (o ⚠ explicado) | **Cumple en el papel; no cumple en pantalla** | Papel: los 7 picos (ch01 b1, ch02 b3, ch03 b4, ch04 b7, ch05 b8, ch06 b10, ch07 b12) tienen ficha; el log dice «picos vacíos 0» en los dos intentos. Pantalla: ch07 b12 queda sin ficha porque T85 no entró (fila 21): 6 de 7. La causa figura en «papel sin colocar» (3 intentos, todos solapados con el reloj), pero el `.md` no lo marca como pico vacío. |
| 2.4 | Q43 fuera por 1c | **Cumple el efecto, no el mecanismo** | Q43 está fuera, descartado por el autor con «la fecha de la cita es desconocida y no se puede anclar a esa noche» en ambos intentos. «fichas fuera 0»: la validación 1c nunca rechazó nada. Lo sacó A.1a (el archivo ahora trae `fecha: "desconocida"`, `rol` y `testimonio`) y el criterio del modelo, no el código. Sirve, pero esta corrida no prueba que 1c funcione; solo el test sintético lo hace. |
| 2.5 | D47 y D105 juzgados por el autor | **Cumple** | Preguntas: D47 `{'spoiler': ['2']}`, D105 `{'no_dicho': ['1962']}`, más T15 («3»), T39 («50») y D161 («2»). Las 5 respuestas: «la mantuvo… otro hecho». Las 5 son falsos positivos reales (km de la fisura, «tres o cuatro minutos», 50% de la posdata, «dos de octubre», noviembre vs diciembre de 1962). «Lo que cayó»: nada (F36: 3). Fase 2 respetó los juicios: los cinco están en pantalla (`juicio_autor` en el `.json`). El autor contestó «otro hecho» a las 5; acá acertó, pero no hay ningún caso donde haya dicho «sí es el mismo hecho», así que no sabemos si discrimina. |
| 2.6 | Los 8 cortes de F36 colocados o con su lista | **Cumple a medias** | Ver punto 3. Hay 4 «sin colocar» (CALMA, SILENCIO, RABIA y T85, esta última nueva), los cuatro con su lista de intentos. Pero de los 8 originales solo D117 se resolvió por la escalera. |
| 2.7 | Ninguna ficha > 6 s | **Cumple** | Duraciones en pantalla: 2.5, 4.2, 4.73, 3.07, 2.73, 4.33, 2.73, 2.53, 3.4, 3.27, 2.8 s. Máximo 4.73 s (D47). F36: 12.74 s (T16), 11.24 s (D131), 7.38 s (D245), 5.72 s, 5.44 s. |

---

## 3. Los 8 «papel sin colocar» de F36 en F37

El papel nuevo movió o borró varios de estos sellos antes de que Fase 2 los viera. Separo qué cambió el papel y qué cambió la colocación.

| F36 (por qué cayó) | Qué hizo el papel F37 | Qué hizo la colocación F37 | Estado final |
|---|---|---|---|
| **CALMA ch02** [6] (crítico: rostros) | Nada: sigue en [6] | Escalera completa, 5 intentos: peso 58.18 s en los dos lados (estorba), inicio 56.14 s (cruza el corte de 56.17 s), siguiente [7] 61.08 s en los dos lados (estorba) | **Sin colocar**, con lista |
| **AVISO ch04** [14] (cruza el corte) | **Lo borró** (en el intento 1 lo había mudado a ch03 [9]; en el 2 desapareció; sin motivo) | No lo vio | **No está** ni en pantalla ni en sin colocar. Pérdida silenciosa |
| **SILENCIO ch05** [10] (cruza el corte) | Nada: sigue en [10] | 4 intentos: peso 71.94 s e inicio 71.66 s cruzan el corte de 74.13 s (el inicio por 0.03 s); siguiente [11] 74.14 s en los dos lados (estorba) | **Sin colocar**, con lista |
| **COLAPSO ch06** [20] (cruza el corte) | Lo mudó a [3] (junto a la ficha D121) | Entró en el primer intento, sin mover | **Colocado** en 713.907 s, 2.5 s. Lo resolvió el papel, no la escalera |
| **INMINENTE ch03** [18] (crítico: tapa la fisura) | Lo mudó a ch05 b9 [26] | Entró en el primer intento | **Colocado** en 672.707 s (ch05), 2.5 s. Lo resolvió el papel; ch03 quedó sin sello |
| **RABIA ch06** [31] (crítico: rostro) | Lo mudó a ch07 b12 [1] | 6 intentos (peso, inicio y siguiente [2], dos lados cada uno): estorba en todos (rostros de pobladores, titular del diario) | **Sin colocar**, con lista. ch06 b11 quedó sin sello |
| **D117 ch02** [2] (crítico: tapa el documento) | Se mantiene (con «ACTA» y «Solo») | Intento 1 (palabra ancla) sin tiempo de lectura; intento 2, «1 · inicio de la oración» 19.20 s, crítico no estorba | **Colocado** en 123.3 s, 4.2 s. **Único que resolvió la escalera de B.1 como se pensó** |
| **Q50 ch05** [2] (lectura: 127 car. piden 8.5 s, hay 3.4 s) | **Lo descartó** («solo cabe una ficha por beat»); puso D161 | No lo vio | **No está.** La regla nueva de citas (B.3: no contar el autor dos veces; mover a la oración siguiente) **no se probó**: el papel F37 tiene 0 citas |

Resumen: 1 colocado por mover (D117) · 2 colocados porque el papel los cambió de sitio (COLAPSO, INMINENTE) · 3 sin colocar con lista (CALMA, SILENCIO, RABIA) · 2 que el papel ya no propone (AVISO, Q50). Más 1 corte nuevo: T85 (ficha, solape con reloj). Además, otras 6 fichas se movieron con la escalera y entraron (D47, D49, D105, D161, D121, D228) y en F36 habrían caído o corrido sin esa escalera: ahí el cambio de colocación sí rindió.

---

## 4. Para la compuerta de Omar (gusto o decisión de contenido)

Los cambios de papel se hacen con `--plan-edit` sobre `01e_pantalla.json`.

1. **Tarjeta fecha-hora.** El papel la trae en `null`. En pantalla hay un marcador «⚠ falta fecha-hora» de 3.0 s en el segundo 0 (el guion dice «agregar con --plan-edit; nunca se inventa») y el chequeo está en ✗. El intento 1 la traía como «9 OCT 1963 · 22:39» (igual que F36), y la voz dice «Son las diez y treinta y nueve» en ch06 [1] y repite las diez y treinta y nueve en ch07 [25]: 22:39 está respaldada por el guion. El motivo del modelo en el intento 2 (T72, 22:43, «adelanta ch06») habla de otra hora (22:43). Decidir: ponerla (22:39) o aceptar un arranque sin tarjeta (con ella F36 tenía intro 3.0 s; sin ella 2.5 s con el primer cuadro congelado).
2. **Gancho: qué dato.** D131 en [1] (hoy) / D118 «266 m, la más alta del mundo» (opción A del contrato) / D195 «1.269 de 1.328» (opción B). D131 adelanta «el agua saltó» unos 70 s antes de que la voz lo cuente, y sus fuentes se contradicen en la altura.
3. **D195 en el clímax** ([20] «Longarone ya no.»): hoy no hay nada ahí.
4. **ch06 b11:** D128 (1.910 muertos, que el modelo tenía en el intento 1 y perdió sin motivo) vs D228 (1000 camas, hoy) vs D17.
5. **ch07 b12:** Q14 (la ironía de Leone) vs T85 (11 imputados). El contrato dice Q14 y T85 fuera; F37 hace lo contrario y deja el pico vacío en pantalla. Volver a Q14 es una edición del papel.
6. **ch03 b4:** T16 (Arcangelo Tiziani, humaniza) vs T15 (3 millones de m³).
7. **ch05 b8:** Q50 (carta del municipio) vs D161 (2 cm por día a 710 m).
8. **ch05 b9 / Q43 «Omar decide»:** sigue vacío; si se quiere Q43 es una edición a mano (el autor lo rechazó por la fecha).
9. **T85, D84:** los «solo gusto» del handoff. T85 ya está arriba; D84 (dos bombas de Hiroshima, ch06 [5]) no se propuso.
10. **Sellos:** el papel pasó de 9 a 8 (AVISO y ALARMA se perdieron en el reintento) y hay 3 sin colocar (CALMA, SILENCIO, RABIA); SILENCIO falla por 0.03 s en un solo intento. Omar decide si los quiere (editar posición o texto) o los da por perdidos. COLAPSO en [3] y no en [20]; AMENAZA en [16]; INMINENTE en ch05: movimientos del autor, no forzados.
11. **Clave de costos.** El perfil no trae `costos.m01e_tope_usd`; se usó el respaldo 1.00. Si Omar quiere dejarla fija, la agrega él (handoff §Frenos).

---

## 5. Totales: F37 contra F36 contra «Con las DEBERÍA»

«Papel» = lo que eligió el autor. «Pantalla» = lo que quedó tras Fase 2.

| Concepto | F36 papel | F36 pantalla | F37 papel | F37 pantalla | «Con las DEBERÍA» |
|---|---|---|---|---|---|
| Fichas | 9 (7 normales + 2 citas) | 7 (6 fichas + 1 cita Q14) | 12 | **11** (10 fichas + 1 recorte D117) | 14 (ch01 1 · ch02 2 · ch03 2 · ch04 2 · ch05 2 · ch06 3 · ch07 2) |
| Fichas por cap (ch01..ch07) | 1/1/2/0/1/2/2 | 1/0/2/0/0/2/2 | 1/2/2/2/1/2/2 | 1/2/2/2/1/2/1 | 1/2/2/2/2/3/2 |
| Una cada | | 1056 s / 7 = 151 s | | **96 s** (1055.8 s / 11) | 75 s |
| Picos con ficha en pantalla | | 4 de 7 (ch01, ch03, ch06, ch07) | 7 de 7 | **6 de 7** (falta ch07 b12) | 7 de 7 |
| Fichas de más de 6 s | | 3 (12.74, 11.24, 7.38) | | **0** (máx. 4.73 s) | 0 |
| Fichas movidas por la escalera | | n/a | | 7 (D117, D47, D49, D105, D161, D121, D228) | |
| Sellos | 9 | 3 (PÁNICO, AMENAZA, MEMORIA) | 8 | **5** (PÁNICO, AMENAZA, INMINENTE, COLAPSO, MEMORIA) | 9 (los del papel, recolocados) |
| Sellos sin colocar | | 6 | | 3 (CALMA, SILENCIO, RABIA) | |
| Relojes | 4 en el papel | 4 | 4 en el papel | 4 (9 OCT ch01, 4 NOV ch04, 9 OCT ch05 que viene de la voz, 20 FEB ch07). El 29 NOV 1968 del papel no sale, igual que en F36 («informativo») | no especificado |
| Tarjeta fecha-hora | 1 («9 OCT 1963 · 22:39») | 1 | `null` (motivo T72) | **0** real + marcador «⚠ falta fecha-hora» (3.0 s); chequeo ✗ | no especificado |
| Punches | | 6 | | 6 (ch02 183.667, ch03 250.733, ch04 458.267, ch05 527.134, ch06 707.5, ch07 877.067); el de ch07 queda sin ficha ni cita en su pico | |
| «Papel sin colocar» | | 8 | | 4 (CALMA, SILENCIO, RABIA, T85) | |
| Lo que cayó por filtros | 3 (D47, D105, Q43) | | | 0 | |
| Descartados del modelo | 85 | | 26 | | |
| Intentos · costo · tokens de entrada | 1 · USD 0.3091 · 59 976 | | 2 · USD 0.7649 (0.4299 + 0.3350) · 65 940 + 66 978 | | |
| Chequeos que fallan | | a_pantalla 1/5, inicio de voz ch07, papel sin colocar | | a_pantalla 2/5 (faltan Q50, D128, D192), inicio de voz ch07 (igual que antes), tarjeta fecha-hora, papel sin colocar | |
| Duración total | | 1056.27 s | | 1055.77 s | |

Lectura: las fichas pasan de 7 a 11 en pantalla (contrato: 14), sobre todo por D47, D105, T39, D161 y D228, y porque D117 ahora entra. Faltan tres para llegar a 14: ch05 (Q50 o Q43), ch06 (D195) y ch07 (Q14). Los sellos suben de 3 a 5 (contrato: 9). La tarjeta y el pico de ch07 sin ficha son los dos retrocesos reales.

---

## 6. Observaciones sobre las reglas (no son gusto)

1. **El reloj le gana a la ficha del pico** (T85, fila 21). La escalera es la de B.1, pero el reloj se coloca primero y posiblemente con un intervalo más largo del que se ve. Es un tema de la regla de colocación, no de contenido.
2. **El reintento reescribe todo.** El segundo intento generó el papel completo otra vez (20 103 tokens de salida); perdió D128, Q14, AVISO, ALARMA y la tarjeta, y cambió T92 por D245, casi sin descartes escritos. El handoff dice que la respuesta del reintento es final para las preguntas, pero nada impide que se pierda lo demás. «Lo que cayó: nada» es cierto solo para los filtros.
3. **La verificación de A.2 no entiende cifras escritas con palabras** («centímetro y medio» no es «1,5»). Produjo una anotación falsa en el `.md` (D68).
4. **El anclaje del gancho depende del modelo**, no de una regla: el prompt m01e-2 solo no bastó en el intento 1.
5. **No se probó nada de lo nuevo para citas** (B.3, mover Q50 a la oración siguiente): el papel F37 no tiene ninguna.
6. **La validación 1c** (cita sin fecha) **no se ejercitó** en esta corrida.
7. **El filtro de spoiler compara cifras y no ve un hecho adelantado** (D131 en [1], «SALTO DEL AGUA»). El autor tampoco lo notó: su `aporta` afirma lo contrario.

Archivo: `C:\CLAUDE_PROJECTS\automatization_videos\lab\hyperframes\f37\c\comparacion_simulador.md`
