# F38e · E — títulos de cap con `m01d_particion.titles()` nuevo (Flash, una llamada)

Escaleta: `lab/hyperframes/f38/b2/fase1/f8s3-vajont/01a_escaleta.json` (congelada; md5 `e0094c37e704d173a414dca977acc2a0`, igual a la de
`data/scripts/_steps/f8s3-vajont/`, que no se abre para escribir). Modelo: `gemini-2.5-flash` vía
`titles(esc)` tal cual queda en el código (sin `call` inyectado). `src` = `flash`. US$ 0.004071 ([{'descripcion': 'm01d_particion: títulos', 'in': 1354, 'out': 37, 'thinking': 1429, 'usd': 0.004071, 'usage_ok': True}]).
Validación = la de `titles()` (≤ 5 palabras, sin dígito, sin «?», tras `strip().strip('".«»')`).

- Literal del código: md5 bloque del md `0c3fe5599f500ce523c77aac0e328597` = md5 `PEDIDO_TITULOS` `0c3fe5599f500ce523c77aac0e328597` (494 car.).
- Pedido de Vajont: md5 `9b497da4ce33763d4912bc99eb63cccd` (5185 car.); el de la prueba 2 era `85e8b649fcac2ba25d9fbf987e282025`. Líneas distintas: [(22, '  beat 10 pico · pico: se ve: Una ventana que se abre a un rugido que crece y un resplandor; una pantalla de televisor que se apaga en un bar; cuatro minutos; una niña que aparece a cuatrocientos metros de donde estaba su cama. · pregunta que abre: ¿Cuánto duran cuatro minutos cuando nadie te dijo que corrieras?', '  beat 10 pico: se ve: Una ventana que se abre a un rugido que crece y un resplandor; una pantalla de televisor que se apaga en un bar; cuatro minutos; una niña que aparece a cuatrocientos metros de donde estaba su cama. · pregunta que abre: ¿Cuánto duran cuatro minutos cuando nadie te dijo que corrieras?')].
- data/: 1320 archivos antes, 1320 después; nuevos o tocados (mtime o md5): ninguno; dumps desviados: ninguno.

| cap | hoy (de 01a_skeleton.json congelado) | nuevo | validación | ¿promete sin contar el final? |
|---|---|---|---|---|
| ch01 | Cama en la oscuridad | La fuerza misteriosa | ✓ |  |
| ch02 | El muro que tapa | La montaña advierte | ✓ |  |
| ch03 | La costura abierta | El agua responde | ✓ |  |
| ch04 | La ola de juguete | Ignorar la evidencia | ✓ |  |
| ch05 | Piedras rodando | Las últimas horas | ✓ |  |
| ch06 | El gran rugido | Cuatro minutos fatales | ✓ |  |
| ch07 | Diarios y verdades | La verdad final | ✓ |  |

## Pedido entero, tal como sale para Vajont (md5 `9b497da4ce33763d4912bc99eb63cccd`)

```
Títulos de capítulo para un documental en español. Cada título se lee solo en pantalla, 3 segundos sin voz, justo antes de que empiece su capítulo: es la promesa de lo que ese capítulo le va a contar a quien mira, sin contar cómo termina. Uno por cap, en orden, de 2 a 5 palabras, concretos, sin cifras, sin fechas, sin nombres propios de personas y sin signos de pregunta. De cada cap tenés sus beats (qué función cumplen, qué se ve, qué pregunta abren) y cómo termina:
CAP 1:
  beat 1 gancho: se ve: Una cama que acelera en la oscuridad; una fuerza que dobla una espalda de niña; un portoncito que se abre solo con un ruido de aire antes de que se vaya la luz. · pregunta que abre: ¿Qué puede mover una cama con una niña adentro si la presa no cayó?
  termina (no lo cuentes): El dique no cedió esa noche. Lo que llegó a la cama de Micaela vino por encima de él.
CAP 2:
  beat 2 planteo: se ve: Un pueblo de fondo de valle con el Piave pasando por delante; arriba, en una garganta lateral, hombres colgados de andamios levantan una pared curva que tapa el cielo. · pregunta que abre: ¿Qué significa vivir debajo de una obra que se aprobó cuando vos ni habías nacido?
  beat 3 escalada: se ve: Un geólogo joven, hijo del hombre que diseñó la presa, caminando la ladera del Toc con un martillo en la mano, buscando la cicatriz de un deslizamiento viejo. · pregunta que abre: ¿Qué pasa cuando el que encuentra el peligro es el hijo del que hizo la obra?
  termina (no lo cuentes): En marzo del cincuenta y nueve, en otro embalse de la misma empresa, una montaña caminó primero.
CAP 3:
  beat 4 giro: se ve: Rocas entrando al agua de Pontesei y una pared de agua de veinte metros levantándose sobre el hombre cuyo trabajo era vigilar la montaña. · pregunta que abre: Si ya hubo un muerto por una ola en un embalse, ¿qué más hacía falta ver?
  beat 5 escalada: se ve: Una abertura de más de un metro de ancho corriendo casi dos kilómetros por la ladera, como una costura abierta; abajo, el agua sube día a día. · pregunta que abre: ¿Quién lee a una periodista de L'Unità cuando el diario local es de la empresa?
  termina (no lo cuentes): El cuatro de noviembre, durante las pruebas, el agua tuvo su primera respuesta.
CAP 4:
  beat 6 giro: se ve: Roca cayendo al lago nuevo y el agua levantándose; cuatro días después, una máquina de escribir; semanas después, una sala de tribunal y una periodista en el banquillo. · pregunta que abre: ¿Por qué el proceso es contra la que avisa y no contra la montaña que ya cayó una vez?
  beat 7 giro: se ve: Una maqueta del valle en un galpón de Padua, con grava donde debía ir roca, y una ola de laboratorio pasando por encima de una presa de juguete. · pregunta que abre: ¿Para qué se pide un modelo si la cota se decide antes del resultado?
  termina (no lo cuentes): La presa cambió de dueño con el agua todavía subiendo. La montaña no se enteró del contrato.
CAP 5:
  beat 8 escalada: se ve: Estruendos que bajan de la ladera de noche; grietas nuevas en la tierra de Erto; caminos cerrados con barreras; en Longarone, abajo, las ventanas encendidas como cualquier noche. · pregunta que abre: Si evacúan casas en Erto, ¿por qué nadie evacúa el pueblo que está delante de la presa?
  beat 9 giro: se ve: Una carta ya firmada a la que se agrega una posdata con dos signos de exclamación; un teléfono colgado; piedras chicas rodando hacia el lado de la presa. · pregunta que abre: ¿Qué hace un hombre después de escribir dos signos de exclamación en una carta?
  termina (no lo cuentes): A las diez y media de la noche, el párroco de Casso escuchó algo y abrió la ventana.
CAP 6:
  beat 10 pico · pico: se ve: Una ventana que se abre a un rugido que crece y un resplandor; una pantalla de televisor que se apaga en un bar; cuatro minutos; una niña que aparece a cuatrocientos metros de donde estaba su cama. · pregunta que abre: ¿Cuánto duran cuatro minutos cuando nadie te dijo que corrieras?
  beat 11 respiro: se ve: Fango y piedras donde había calles; un hombre parado en el medio sin saber hacia dónde mirar; el ruido de rotores bajando sobre una aldea. · pregunta que abre: ¿Cómo se cuenta a los muertos de un pueblo que ya no tiene esquinas?
  termina (no lo cuentes): Tres días después llegó el presidente del Consejo. La gente ya sabía qué pedirle.
CAP 7:
  beat 12 revelacion: se ve: Un presidente con abrigo oscuro entre escombros y un grito que le sale de la gente; en los kioscos, dos diarios con dos verdades distintas sobre la misma noche. · pregunta que abre: ¿Se puede llamar fatalidad a algo que tenía fisura, maqueta y carta?
  beat 13 cierre: se ve: Cajas de un archivo trasladado de un tribunal a otro; una mujer que de niña viajó cuatrocientos metros sobre una cama, sentada ahora frente a una mesa con un cartel de comité. · pregunta que abre: ¿Quién tomó —o dejó sin tomar— la decisión de avisar a Longarone aquella noche, y por qué la preocupación escrita a la mañana no se convirtió en una evacuación?
  termina (no lo cuentes): La sentencia dice inundación agravada por la previsión del evento. No dice quién, entre la posdata de la mañana y las diez y treinta y nueve de la noche, decidió que Micaela siguiera durmiendo.
```
