# PRUEBA 2 — títulos de cap (analista, 2026-10-27) · prompt para la llamada en seco

Base: `script_engine/m01d_particion.titles()` (líneas 123–146), Gemini Flash (`call_flash_json`, mismo esquema `TITLES_SCHEMA`). Mismo modelo, misma validación de código (≤ `TITLE_MAX_WORDS` = 5 palabras, sin dígitos, sin «?»). Cambia el texto del pedido y lo que ve de cada cap.

## Causa (DECISIONES 03:37)
Hoy el modelo ve solo `funcion` + `imagen_sensorial` y la orden es «basate en lo que se ve». No sabe qué promete el cap → salen objetos poéticos que no prometen nada: «El muro que tapa», «Piedras rodando», «Diarios y verdades».

## Entrada nueva por cap (más entrada, no reglas nuevas)
```
CAP n:
  beat <n> <funcion>[ · pico]: se ve: <imagen_sensorial> · pregunta que abre: <pregunta_abierta>
  …
  termina (no lo cuentes): <cierre del último beat del cap>
```
Todo sale de `01a_escaleta.json` (`beats[].funcion/pico/imagen_sensorial/pregunta_abierta/cierre`). Nada de un tema.

## Pedido nuevo, entero
```
Títulos de capítulo para un documental en español. Cada título se lee solo en pantalla, 3 segundos sin voz, justo antes de que empiece su capítulo: es la promesa de lo que ese capítulo le va a contar a quien mira, sin contar cómo termina. Uno por cap, en orden, de 2 a {TITLE_MAX_WORDS} palabras, concretos, sin cifras, sin fechas, sin nombres propios de personas y sin signos de pregunta. De cada cap tenés sus beats (qué función cumplen, qué se ve, qué pregunta abren) y cómo termina:
{lines}
```
| pieza | hoy | prueba |
|---|---|---|
| para qué sirve el título | — | promesa del cap, leída sola antes de que empiece |
| base | «lo que se ve» | qué se ve + qué pregunta abre + cómo termina (marcado: no lo cuentes) |
| «concretos (un objeto, un lugar, un momento)» | sí | «concretos» (sale la lista que empuja a objetos) |
| sin nombres propios de personas | sí | **se queda**: el título sale antes de que la voz presente a la persona; «Merlin» antes de ch03 no le dice nada a nadie. Lugares (Toc, Longarone) ya estaban permitidos |
Reemplaza, no suma.

## Simulación (lo que debería permitir, con la escaleta de Vajont)
| cap | hoy | qué podría salir | por qué |
|---|---|---|---|
| ch01 | Cama en la oscuridad 🟢 | La presa que no cayó | pregunta: «¿qué mueve una cama si la presa no cayó?» (la voz lo dice en [1]) |
| ch02 | El muro que tapa 🔴 | El hijo del que la diseñó | pregunta del beat 3; promete conflicto |
| ch03 | La costura abierta 🟢 | El primer aviso | Pontesei + fisura + la periodista |
| ch04 | La ola de juguete 🟢 | Juicio a la que avisó | pregunta del beat 6 |
| ch05 | Piedras rodando 🟡 | La carta de la mañana | cierre del beat 8 y el beat 9 |
| ch06 | El gran rugido 🟡 | Cuatro minutos | pregunta del pico («¿cuánto duran cuatro minutos…?»); en letras pasa el código, pero choca con «sin cifras» → ver si el modelo lo evita |
| ch07 | Diarios y verdades 🔴 | La palabra imprevisible | cierre del beat 12 |

## Riesgo que el código no ve
Spoiler del propio cap (que use el `cierre`). Se mira a ojo en la tabla; si pasa, el `cierre` sale de la entrada.
