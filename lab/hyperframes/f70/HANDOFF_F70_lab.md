# HANDOFF F70 (lab) — fotos sin texto pedido y cola de época sin «taken in»

## Por qué (Omar, 2026-11-01 14:47)
La auditoría (`lab/hyperframes/f68/AUDITORIA_FOTOS.md`) encontró que Nano Banana obedece literal dos partes del prompt que se escribieron para Seedream:
1. Frases que piden texto escrito («The word(s) "X" is/are written on … in clear crisp … lettering»): la palabra sale, pero rellena hojas, periódicos y letreros con texto inventado y mal escrito (ch03_img_08, ch03_img_15, ch05_img_03, ch06_img_11, ch02_img_04).
2. La cola de estilo «A grainy 35mm documentary photograph taken in <año>»: en ch06_img_07 puso un sello de fecha «2023» de cámara.
Omar quiere ver, antes de tocar producción, si quitar eso arregla las fotos con error y si cambia las que estaban bien.

## Cambios a probar (los dos juntos, como un solo prompt nuevo)
A. Se QUITA la frase que pide texto escrito (no se reemplaza por otra regla). La frase final que ya existe («No readable text, no signage, no labels.») queda igual. El texto que la foto quería decir queda para la capa gfx (decisión aparte, fuera de este lab).
B. En la cola de estilo, «taken in <año>» pasa a «in the style of <año>». Nada más cambia en la cola.

## Constantes
| Valor | Origen | Quién |
|---|---|---|
| Motor nb2_lite, tolerancia 6, una foto por llamada, mismas madres | DECISIONES 2026-11-01 (F68) | Omar |
| Fotos con error de texto/fecha: ch03_img_08, ch03_img_15, ch05_img_03, ch06_img_11, ch02_img_04, ch07_supp_04, ch06_img_07 | auditoría F68 | analista (derivado) |
| Control sin texto: ch02_img_05, ch03_img_12, ch04_img_09, ch05_img_12, ch06_img_04, ch07_supp_02 | elegidas para cubrir épocas 1958–2023, con y sin madre | analista (derivado) |
| ≈ 13 × 0,042 US$ (se reporta después, no es tope) | F68 | derivado |

## Módulos
- Etapa 0 encuentra dónde se arman A (frase de texto, carteles F51f) y B (cola de estilo; perfil del motor o m03). En el lab NO se toca ese código: el script del lab aplica A y B sobre el texto ya armado de cada `.llamada.json` y lo manda igual que producción.
- Producción, `output/`, guion y QA: sin tocar.

## Salida
`lab/hyperframes/f70/`: por foto, texto viejo y nuevo (diff), png nuevo, y hoja de contacto por foto: vieja | nueva, rotulada. Tabla: ¿la frase A existía?, ¿la cola cambió?, ¿sale texto legible?, ¿sale sello de fecha?, ¿cambió algo más en las de control? (personas, época, luz, encuadre, cara de la madre).
