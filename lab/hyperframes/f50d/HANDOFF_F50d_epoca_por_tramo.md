# HANDOFF F50d — Época por tramo en el canon y Wittenoom en texto con todo cableado (tope US$ 3,00)

Analista, 2026-10-28 22:45. Tema `123bbb64-9fca-4395-8bf4-57d60e219ef1` (Wittenoom). Rama `f11-guion-v4`.
**Qué es, en llano:** el canon visual (la guía de época de cada video) describe UNA sola época para todo el video. Wittenoom va de 1937 a 2026 y el canon dice «1960s»: a las fotos de 2021–2026 les llegan ropa, tecnología y vehículos de los 60. Esta tanda hace que el canon traiga la época **por tramo de años**, y después corre a Opus en texto sobre Wittenoom (sin fotos) para ver el papel nuevo con todo lo de F50c cableado.

## Orden (vuelto a derivar)
1. ¿Construye sobre algo que se decidió reemplazar? No: `canon_desde_ficha` (F50 A) y el expediente (F50c) son lo vigente.
2. ¿Una decisión de hoy cambia el orden? Sí, ya aplicada: Omar (22:30) eligió la opción A: F50d → F51 (fotos de Wittenoom con el research que ya tiene); los cajones nuevos del research se prueban en el próximo tema. F51 no corre sin el OK de Omar al papel de esta tanda.

## Medido (papel F50b, 96 fotos)
| Cap | Años de las fotos | Lo que les llega hoy del canon |
|---|---|---|
| 1–4 | 1943–1963 | época «1960s»: bien |
| 5 | 1966–2023 | 1960s para 10 de 16 fotos de 1971–2023 |
| 6 | 1979–2023 | 1960s para todas (16) |
| 7 | 2021–2026 | 1960s para todas (13): «passenger cars from the 1940s-1960s» |
**38 de 96 fotos (40 %) son de 1975 en adelante.** Además, 11 fotos usan un grupo de gente fuera de sus años (familias migrantes 1958–66 en fotos de 1985–2023), y desde F50c esa ropa de los 60 está a la vista de Opus.

## Constantes
| Valor | Origen | Quién |
|---|---|---|
| Tope de la tanda US$ 3,00 | derivado: corrida de m03 en F50 D = US$ 2,1205 + 4 llamadas de canon a Flash (~US$ 0,01 c/u) + margen por reintentos | analista; **Omar lo confirma al copiar el prompt** |
| 3 corridas del canon para medir la varianza | lo pidió la ENTRADA 28e (Flash no es determinista: 7 grupos en F50 contra 15 en F48) | analista |
Formato de años `AAAA-AAAA`: el mismo que ya usa `spans`.

## Módulos
| Archivo | Hoy | Después |
|---|---|---|
| `researcher_steps/step_4e_visual_canon.py` | `era_visual_canon` con una ropa/tecnología/vehículos/interiores; grupos con un `clothing` | + `era_visual_canon.periods` y grupos con `clothing_by_period` (A) |
| `script_engine/m03_visual.py` | el bloque ERA del canon imprime los 4 campos únicos | imprime los `periods` que se cruzan con los años de las fotos del cap (B) |
| `script_engine/m03_expediente.py` | `CLOTHING: <clothing>` por grupo | `CLOTHING: AAAA-AAAA: …; AAAA-AAAA: …` (B) |

## A. El canon por tramo (formato de salida + 2 líneas del texto del pedido)
1. **Esquema** (`VISUAL_CANON_SCHEMA_FICHA`):
   - `era_visual_canon.periods`: lista de objetos `{years, clothing, technology, vehicles_machinery, interiors}` (strings).
   - En `_GRUPO_SCHEMA`, `clothing` se **reemplaza** por `clothing_by_period`: lista de `{years, clothing}`.
   - Los campos únicos de `era_visual_canon` (`clothing`, `technology`, …) **se quedan**: los leen `m05_judge`, `m06_classifier` y `m03_imagenes_v3` (línea ~73). Se declara en el reporte.
2. **Texto del pedido**, cambios exactos (y nada más):
   - En `TEXTO_1_PEOPLE_GROUPS`, la línea `- where_when: dónde y en qué años aparecen (EN, una frase)` pasa a: `- where_when: dónde y en qué años aparecen, todos los años en que el material los muestra, también décadas después (EN, una frase)`.
   - En `TEXTO_1_PEOPLE_GROUPS`, la línea `- clothing: ropa, peinado y accesorios de ESE grupo en ESOS años, ese clima y esa clase social (EN, una frase)` **se reemplaza** por: `- clothing_by_period: una entrada por cada tramo de años en que el material muestra a ese grupo; years "AAAA-AAAA" y clothing: ropa, peinado y accesorios de ESE grupo en ESE tramo, ese clima y esa clase social (EN, una frase)`.
   - En el pedido del canon, después de la línea de `interiors` de los sub-campos de época, se agrega: `- periods: una entrada por cada tramo del material en que cambian la ropa, la tecnología, los vehículos o los interiores; years "AAAA-AAAA" y esos 4 campos para ese tramo (EN). Si el tema es de una sola época, una sola entrada.` Es campo nuevo, no reemplaza nada: se justifica con la tabla de arriba (40 % de las fotos fuera de la época única).
3. **Revisión del analista sobre Wittenoom** (no se puede simular sin el modelo; esto se espera): `periods` con al menos un tramo de 1937–1966 (pueblo minero), uno de 1966 a los 90 (pueblo que se vacía) y uno de los 2000 a 2026 (hoy); `spanish_migrant_families` con su ropa de 1958–66 y otra para las fotos de 1985–2023 (aeropuerto, médico, entrevistas). Si no sale así, se reporta, no se fuerza.

## B. El pedido de m03 usa los tramos
- Bloque ERA del canon (todo bloque que entre en el pedido de casilleros y en el del clip Veo; hoy líneas ~350 y ~945 de `m03_visual.py`): en lugar de `clothing/technology/vehicles_machinery/interiors` únicos, imprime cada `period` cuyo tramo se cruza con los años de las fotos del cap. Año de cada foto = el del expediente (`anio_ancla`, si no el `respaldo`). Si el canon no trae `periods` (un topic viejo), imprime los campos únicos como hoy.
- Expediente (`bloque`): `CLOTHING: 1958-1966: …; 1985-1995: …` con todos los tramos del grupo.
- **Lo viejo se borra:** la lectura de `clothing` único del grupo en `bloque` sale.
- **En seco primero:** los 7 pedidos con el canon nuevo, sin llamar a Opus → `lab/hyperframes/f50d/pedidos/`. Verificación: fuera del bloque ERA y de las líneas CLOTHING de PEOPLE GROUPS, nada cambia respecto de `lab/hyperframes/f50c/pedidos/` (diff). Si cambia otra cosa: PARADA.

## Marca del canon (sin esto, D no ve el canon nuevo)
`asegurar_canon` rehace el canon solo si cambia `canon_ficha_md5` (= md5 de `ficha_caso.json`). La ficha no cambia, así que el canon viejo se quedaría. Arreglo general: la marca pasa a ser md5(ficha + texto del pedido del canon + esquema), así cualquier cambio del pedido o del esquema rehace el canon en cualquier tema. Test: cambiar una letra del pedido → la marca cambia.

## C. Varianza del canon (antes de elegir)
3 llamadas a `canon_desde_ficha` sobre Wittenoom, en paralelo, **sin guardar en topics_db**. Tabla en `lab/hyperframes/f50d/CANON_VARIANZA.md`: por corrida, número de grupos, sus ids, los tramos de `periods` y los tramos de `clothing_by_period` de cada grupo. Se adopta la corrida 1 (la que corre `asegurar_canon` como en producción); las otras 2 son solo medida.

## D. Wittenoom en texto con Opus
`fase1_5 --only m03` como en F50 D (casilleros con Opus, armado, F8, movimiento de los 2 clips). **Cero fotos, cero clips.** Papel nuevo con `lab/hyperframes/f50/papel.py --salida lab/hyperframes/f50d/` y diff contra el papel de F50b.
En el reporte, medido sobre el papel nuevo:
1. fotos de 1975+ cuyo prompt trae ropa, vehículos o tecnología de los 40–60 (antes → después);
2. fotos con nombre propio de persona en la prosa final (debe ser 0);
3. fotos donde el sujeto coincide con la persona de PEOPLE (las 8 testigo de F50c);
4. gasto real por paso.

## Pasos, en este orden
A (código) y marca → C (3 corridas; la 1 queda en producción vía `asegurar_canon`) → B (código + pedidos en seco) → D. Cada parte termina con su salida en texto antes de la siguiente.

## Paso 0
`DECISIONES.md`, tal cual: «2026-10-28 22:30 · Opción A: F50d (época por tramo en el canon + Wittenoom en texto con Opus) y después F51 con el research que Wittenoom ya tiene; los cajones nuevos del research (aspecto de personas conocidas, lugares y objetos; cuándo es la escena; fenómenos y documentos; hora y clima) y las distancias desde lat/lon se prueban en el próximo tema · Omar · F50d». `TOPE_TANDA` = 3,00.

## Reglas fijas
- Subagentes en paralelo donde se pueda (A y el código de B; las 3 llamadas de C).
- Nada en `main`. Ninguna foto ni clip. Si el gasto llega al tope: PARADA.
- Sticker y `MAPA_PROYECTO` (`--check` 0); suite rápida y amplia; candado de ch02.
- `F50d_REPORT.md` con lo abierto entero y el veredicto íntegro de `revisor-handoff`; `ESTADO_SESION`; commit por parte.

## PARADA al terminar D.
