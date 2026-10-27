# F36 — Respuesta del analista a la PARADA antes de C (2026-10-26 18:05)

Leído: `F36_REPORT.md` entero (A, B, simulador, lectura de CC, pregunta), commits `74a309f`–`60d3e0e`, los 6 módulos nuevos (2.256 líneas, `ORDEN` de 9 filtros visible), `b/GUION_PANTALLA.json`.

## Veredicto de A y B
- **A cierra**: diff vacío contra F34, suites iguales, md5 igual. Bien hecho.
- **B cierra como tanda** (cada arreglo hace lo pedido y tiene test). El contrato pasó de 5/15 (F34) a 6/15 + 2 en parte, y lo que no cerró destapó el obstáculo siguiente, que es lo que se esperaba de arreglar por capas. Tres cosas que eran **mías** en el contrato: pedía AMENAZA dos veces (contradice B.3); pedía D49 como «lupa/ficha» sin ver que el rotulista lo propuso como lupa y la foto no tiene el detalle; y CALMA en ch02 lo juzgué sin la foto (tapa rostros: el crítico tiene razón).

## Correcciones al contrato (REVISION_GUION, tabla DEBERÍA) — vigentes para C y D
- Línea 2 (CALMA ch02 162.3): **se acepta cortada** (tapa rostros). CALMA puede salir en otro lugar del video si el modelo la elige.
- Línea 3: AMENAZA en ch02 vale en 155.4 («colgados») o en 211.1; las dos cumplen.
- Línea 4 y ch04: ch03 **AVISO**, ch04 **ALARMA** (no AMENAZA: no se repite en el video).
- Línea 6 (D49): sigue vigente, **como ficha**. Regla nueva **B.10** (va en C, es chica): *lupa cuya detalle la visión no encuentra en la escena → se degrada a ficha con la misma etiqueta y dato* (reemplaza el corte por «zona» para lupas; el corte por zona se queda para recortes/citas).
- Línea 9 (ch05 532): con Q50 vivo (C.2), «nunca sobre un texto» saca el sello; si Q50 no vive, RABIA puede quedarse. Se mide después de C.
- Línea 14 (MEMORIA 1013.65, «la escena 13 ya tiene ficha»): **decide Omar** (ver pregunta 1 abajo). Hasta que decida, se queda cortada.

## Respuestas a las dos preguntas de CC
1. **C.1 — autorizado**, con la frase literal del handoff. Mi prompt a CC decía «solo C.2 y C.3» por error mío: los cambios literales de prompt son C.1, C.2, C.3 y C.4 (este archivo da el de C.4).
2. **C.4 — autorizado, con este texto literal** para la lista de tipos de `ROTULISTA_SYSTEM` (agregar al final de la lista de tipos existente, sin tocar los demás):
   > `agua`: una altura o nivel en metros que la voz dice en esa oración (una cota, una ola, el nivel del embalse). Etiqueta: la palabra o las dos palabras de la oración que lo nombran, en mayúsculas («COTA AUTORIZADA», «OLA»); dato: el número con «m»; `unidad: "m"`, `valor`: el número. Como el reloj, el agua **sí** repite lo que la voz dice: es su dibujo.
   Y en `rotulista_filtros`: `no_dicho` y `candado` tratan `tipo: "agua"` como al reloj (la cifra viene de la voz, por diseño); el resto de filtros igual. `agua_de_voz` y `AGUA_ETIQUETAS` se borran con su test. Caso de prueba: ch03 OLA 20 m y ch04 COTA AUTORIZADA 715 m tienen que salir del modelo; si no salen, anotarlo y **no** resucitar `agua_de_voz`: PARADA y se mira la respuesta cruda.

## Dos cambios a C que salen de leer B (no son nuevos números)
- **C.3, los sellos: una sola llamada por video, no una por cap.** B.3 repartió COLAPSO a ch04 solo porque ch04 corre antes que ch06; con una llamada por cap Sonnet tendría el mismo defecto. Entonces: los textos siguen en prefetch paralelo como hoy; **después**, una llamada chica a Sonnet con los 7 caps (por beat: función, oración ancla, oración antes y después, y si el beat ya tiene texto) + el vocabulario del perfil, que devuelve `{cap, beat, sentence_idx, word_idx, palabra | null}` para todo el video, **sin repetir palabra y como máximo una por beat**, con la instrucción literal del handoff C.3 adaptada a «en todo el video». El reparto y el crítico (B.2) corren igual después. Caché por md5 de la entrada. Tope de esa llamada: dentro del US$ 1.50 de C.
- **C.2, los cortes de escena en la entrada:** como propone CC, tomarlos de `build_scenes` sin `snap_cuts`, iguales en prefetch y plan, para no romper la caché. Anotar en el guion si un `caben` difiere del corte final en más de 1 cuadro.

## Preguntas a Omar — RESPONDIDAS 17:58 (las dos: con el voto del analista; van en C, anotadas en DECISIONES 17:58)
1. **«Una por escena»** en escenas largas (ch07 escena 13 dura 40 s; MEMORIA cae 7 s después de que terminó la ficha): ¿se queda la regla tal cual (MEMORIA no sale) o pasa a «nunca al mismo tiempo» (dos bloques no se solapan ni se tocan; sin número nuevo)? **Omar: «nunca al mismo tiempo».** Implementación en C: el filtro «una por escena» de `rotulista_colocar` y del catálogo de sellos se reemplaza por «no se solapa ni se toca con otro bloque» (comparar intervalos start/t1); test con MEMORIA ch07 1013.65 (debe quedar) y con dos bloques solapados (debe cortar). Razón: la regla nació con escenas de ~10 s y Veo trae escenas de 40–100 s (misma lección que los caps de una escena).
2. **T85 («11 imputados», línea 13)**: cae por tu regla «pico: solo a_pantalla» (14:22). ¿Se queda la regla o pasa a «pico: solo a_pantalla, salvo que el beat pico no tenga ningún a_pantalla»? **Omar: la excepción.** Implementación en C: el filtro `cantidad` para el beat pico deja pasar un texto no marcado solo si el beat no tiene ningún `a_pantalla` en el pool; test con T85 ch07 (debe quedar, con el reloj 20 FEB 1968 antes y la ficha después, sin tocarse).
