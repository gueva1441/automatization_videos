# HANDOFF F50i — prueba: aspecto del grupo sin el «estado» (polvo rojo), en lab

Analista → CC · 2026-10-29 · rama `f11-guion-v4` · **no toca producción** · tope US$ 0,50 · una etapa y PARADA.

## Por qué
En F50h, varias fotos de C salieron con manchas rojas que parecen sangre: 2/9 (barco), 4/11 (hospital), 4/12 (foto de bautizo) y 5/8 (aeropuerto 1985). Las 4 tienen un solo grupo, `spanish_migrant_families`, cuyo `appearance` del canon (`lab/hyperframes/f50f/canon_f50f.json`) termina en «; women and children tanned and dusted red in Wittenoom». Desde F50g-A el código pega esa oración en todas las fotos del grupo, también en las que no pasan en Wittenoom.

Hipótesis: el estado («dusted red») metido en el aspecto fijo causa las manchas. No está probada, porque en la 5/8 una de las tres versiones salió limpia con el mismo aspecto. Esta prueba cambia **una sola variable**.

## Orden re-derivado
- ¿Construye sobre código que se va a reemplazar? No: lee `f50h.py` (`armar_c`) y no lo cambia.
- ¿Alguna decisión de hoy cambia el orden? Sí, ya está incorporada: el arreglo del canon (aspecto fijo separado del estado) y el pase de C a producción esperan el resultado de esta prueba y van juntos en F51.

## Constantes
| valor | origen | quién |
|---|---|---|
| 4 fotos: 2/9, 4/11, 4/12, 5/8 | las de F50h con manchas rojas según los dos evaluadores ciegos del analista; todas de un solo grupo con aspecto | analista, OK de Omar 2026-10-29 03:10 |
| 2 fotos por prompt | igual que F50h (Seedream 5.0 Lite no acepta `seed`, `engine_profiles.py` l. 35) | Omar 2026-10-29 02:03 |
| US$ 0,035 por foto → 8 fotos = US$ 0,28; tope US$ 0,50 | `engine_profiles.py` l. 79 + margen | Omar 2026-10-29 03:10 |

## Variante C′ (la única que se genera)
C′ = `armar_c` de `lab/hyperframes/f50h/f50h.py`, con `ESTILO_C` y el mismo post-proceso (`post`), con **un solo cambio**: el `appearance` de `spanish_migrant_families` pasa de

`Spanish Mediterranean people with olive to light skin, dark brown or black hair, dark eyes, slim to medium builds; women and children tanned and dusted red in Wittenoom.`

a

`Spanish Mediterranean people with olive to light skin, dark brown or black hair, dark eyes, slim to medium builds.`

El cambio se hace sobre una **copia en memoria** de `grupos` dentro del script de lab. El canon, topics_db y `03_visual.json` no se tocan. Todo lo demás de C queda igual.

## Etapa única (US$ ≤ 0,28) → PARADA
1. Etapa 0: md5 de este handoff en el reporte, y al final de `DECISIONES.md`, tal cual:
   `- 2026-10-29 03:10 · **F50i:** prueba en lab de una variable: las 4 fotos de F50h con manchas rojas (2/9, 4/11, 4/12, 5/8) se regeneran con C y el aspecto de spanish_migrant_families sin «; women and children tanned and dusted red in Wittenoom» (2 fotos por prompt, tope US$ 0,50). Si las manchas desaparecen, F51 lleva C a producción y el canon separa el aspecto fijo del estado (polvo, enfermedad) · Omar · F50i`
2. `lab/hyperframes/f50i/f50i.py`: arma los 4 prompts C′, los pega enteros en `PROMPTS_F50i.md` junto al C de F50h, con un diff palabra por palabra que tiene que mostrar solo la cláusula quitada (si muestra otra cosa, PARADA), y genera 8 fotos con `generar_1` de F49 (`num_images` 2), en paralelo. Las guarda en `fotos/<cap>_<foto>/Cp_1.png`, `Cp_2.png`.
3. Hojas, una por foto (`hojas/hoja_<cap>_<foto>.jpg`): fila de arriba las 2 de C de F50h (salen de la llave de F50h: la letra que era C), fila de abajo las 2 de C′. Rótulos «C (F50h)» y «C′ (sin polvo)». Esta vez **no** va a ciegas: es una comparación de una variable.
4. Sin visión ni otro modelo.

## Reglas fijas
- No tocar producción (`script_engine/`, canon, topics_db, `03_visual.json`).
- Ningún número fuera de la tabla.
- Workers en paralelo.
- Commit (sin `llave.json` de F50h); ESTADO_SESION y `F50i_REPORT.md` con la salida, el costo real y el veredicto íntegro de `revisor-handoff`.
- Suite rápida y candado ch02 como siempre.
- PARADA al terminar. El analista mira las hojas.
