# HANDOFF F50b — Tres bugs del armado de la foto y el papel re-armado en seco (US$ 0)

Analista, 2026-10-28 21:40, después de revisar F50 (papel de Wittenoom). Tema `123bbb64-9fca-4395-8bf4-57d60e219ef1`. Rama `f11-guion-v4`.
**Qué es, en llano:** el papel de las 96 fotos salió bien en casi todo. Quedan tres fallas del código que arma la frase, y las tres valen para cualquier tema. Se arreglan y el papel se vuelve a armar **desde los casilleros que ya están guardados** en `03_visual.json`. No se llama a ningún modelo y no se hace ninguna foto.

## Orden (vuelto a derivar)
1. ¿Construye sobre algo que se decidió reemplazar? No. Toca el armado y la F8 que entraron a producción en F50.
2. ¿Una decisión de hoy cambia el orden? No. Las fotos (F51) esperan el OK de Omar sobre este papel.

## Los tres bugs (medidos sobre las 96 fotos del papel de F50)
| # | Qué pasa | Fotos | Arreglo general |
|---|---|---|---|
| 1 | La F8 «menor en daño» saca frases sanas porque `HARM` trae las palabras sueltas `shot` y `body`. Cae la oración de plano que arma el código («Wide shot, eye-level, child's height…») y la acción de la viuda («body curled forward… photograph of a bandaged infant») | cap 2 foto 13 y cap 4 foto 1 **quedan sin plano**; cap 5 foto 16 queda sin acción | En `HARM`, `shot` pasa a `shot\s+(?:dead\|down)\|gunshot\w*` y se quita `body\|bodies` (los cuerpos ya los cubre `BODY`). Medido: las 3 frases vuelven; de las 96 no se pierde ningún verdadero positivo (eran los únicos 3 «menor en daño») |
| 2 | Cláusulas negadas de los casilleros llegan a la prosa. Seedream dibuja lo que lee aunque esté negado (lección de QA Studio, receta A) | cap 4 foto 14 «never looking back» · cap 6 foto 1 «with no figure anywhere» · cap 7 foto 1 «nobody has dug and the shovel stands unused», «no machinery anywhere» · cap 7 foto 11 «no work», «no vehicles» | Antes de armar, el código saca de cada casillero de prosa la cláusula (entre comas, punto y coma o punto) que empieza con `no`, `nobody`, `nothing`, `never` o `none`, con un `with` delante opcional. Son palabras de la gramática inglesa, no de un tema. `without` no se toca, porque describe lo que sí hay («swings without seats»). Medido: 4 fotos y 6 cláusulas, ningún casillero queda vacío. Si quedara vacío, el casillero se omite. **No reemplaza ninguna regla.** Es nueva y se justifica así: ninguna otra pieza saca negaciones de la prosa, y `NO_TEXT` no pasa por este paso (lo agrega el código al final) |
| 3 | Mayúsculas del modelo en mitad de la oración: «Wide shot, Eye-level, Deep depth of field», «written Over the entrance in Metal block letters», «On the warning sign … in Bold block stencil» | 29 fotos en la oración de plano y 2 carteles | Al pegar un casillero en mitad de una oración (`camera_angle`, `lens_technique`, `font`, y la preposición inicial de `location`), la primera letra va en minúscula si la palabra es «Xxxx», es decir, mayúscula y después minúsculas. No se toca si la palabra va toda en mayúsculas o empieza con cifra. En `location` solo se baja la preposición de la lista cerrada de F50 §B.4 («Federal Court» queda igual) |

**Se quedan, a la lista (no se arreglan ahora):**
- «loosely wound» lo corta la F8 como «wound». Afecta a cap 1 foto 1: el vendaje sigue en la oración del sujeto.
- «blue asbestos veins» lo corta la F8 como manos/cara. Afecta a cap 3 foto 2: es solo la paleta.
- «in typewriter» / «in typewritten» en la letra de 2 carteles.
- Cap 5 foto 16: «a baby's bandaged foot» debería ser «a young man's bandaged foot». Es la foto de Daniel (cap 1). Es un error del modelo en 1 foto: se arregla en QA Studio cuando esté la foto.

## Constantes
Ninguna nueva. Las palabras de los arreglos 1–3 son gramática inglesa, declarada arriba.

## Módulos
- `script_engine/m03_imagenes_v3.py`:
  - `HARM` (arreglo 1);
  - `armar` (arreglos 2 y 3) con una función nueva `_sin_negadas(texto)`.

Nada más.

## Paso 0
`DECISIONES.md`, tal cual: «2026-10-28 21:23 · Foto madre de Wittenoom: se regenera con el canon nuevo de la ficha en la tanda de fotos (F51); la `subject.png` vieja pasa a `lab/hyperframes/f50/antes/` y no se adopta · Omar · F51». En esta tanda **no** se toca la foto madre.

## Pasos
1. Arreglos 1–3 con tests:
   - «Wide shot, eye-level, child's height…» no da problemas;
   - «the boy was shot dead» sí da «menor en daño»;
   - «with no figure anywhere» sale de un `setting`;
   - «swings without seats» se queda;
   - «shot, Eye-level» queda «shot, eye-level»;
   - «Over the entrance» queda «over the entrance»;
   - «Federal Court» no cambia.
2. **Re-armado en seco** de las 96 fotos de Wittenoom: los casilleros de `03_visual.json` (fotos de caps 2–6, extras y foto 0 de los caps 1 y 7) → `armar` → F8. Se escribe en `03_visual.json` solo el `prompt` (y `sensible`/`motivos` sobre el prompt nuevo). Antes, copia a `lab/hyperframes/f50b/antes/`.
   - Los `video_prompt` de los caps 1 y 7 **no se rehacen**: no traen negaciones y el primer cuadro cambia solo en la técnica o en la cláusula negada. Se declara en el reporte.
3. Salida en texto `lab/hyperframes/f50b/DIFF_PAPEL.md`: por cada foto que cambió, antes → después, y por qué arreglo (1, 2 o 3). Verificación automática: solo cambian las fotos de la tabla de arriba (2/13, 4/1, 5/16, 4/14, 6/1, 7/1, 7/11, las 29 de la técnica y los 2 carteles). Cualquier otra diferencia: PARADA con el diff.
4. Papel regenerado con `lab/hyperframes/f50/papel.py` en `lab/hyperframes/f50b/PAPEL_FOTOS_WITTENOOM.md/.json`.

## Reglas fijas
- Cero llamadas a modelos, cero fal. Nada en `main`.
- Sticker y `MAPA_PROYECTO` (`--check` 0); suite rápida y amplia (números antes y después); candado de ch02.
- `F50b_REPORT.md` con lo abierto entero y el veredicto íntegro de `revisor-handoff`; `ESTADO_SESION`; commit.

## PARADA al terminar el paso 4.
