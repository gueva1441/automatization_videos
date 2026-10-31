# HANDOFF F62 — objetos de época: el canon nombra vehículos y aparatos por modelo concreto

Modelo → CC: Opus medium. Subagentes en paralelo donde el trabajo lo permita (Etapa 0: uno por pregunta; Etapa B: los 7 caps a la vez; Etapas C y D: todas las fotos a la vez). Handoff auditado por subagente (13 correcciones aplicadas).

## Por qué (lo que jode al espectador)
Un avión, un camión o un aire acondicionado moderno en una foto de 1962 rompe la inmersión en un canal de historia (comentarios «eso es falso»). En la prueba F60 B+C (`lab/hyperframes/f60/bc/MIRADA_SUBAGENTE.md`) ~1 de cada 5 fotos con persona trajo un anacronismo; **2 de 2 aviones** salieron de otra época (turbohélice años 70 en `ch03_img_16` 1962; Cessna Caravan años 80 en `ch03_img_04` 1948).

## Causa (medida por el analista sobre `lab/hyperframes/f61/03_visual_f61.json`, 96 prompts de foto)
1. **No es el año:** 93 de 96 prompts ya lo traen dos veces («Wittenoom, 1962» y «taken in 1962»); los otros 3 (ch02_img_04/05/12) una vez («taken in 1962»).
2. **m03 copia el tipo genérico que le da el canon.** Canon A3 (`lab/hyperframes/f60/a3/05_visual_canon_a3.json`, el que alimentó la corrida F61), tramo 1950-1966, `vehicles_machinery`: «1950s-1960s tipper trucks spreading tailings, utility trucks, small propeller passenger aircraft on the dirt airstrip…». Prompts: `ch03_img_16` «a small propeller passenger aircraft», `ch02_img_12` «small propeller plane», `ch02_img_16` «A 1960s tipper truck», `ch03_img_09` «A utility truck». Seedream rellena el tipo genérico con su modelo por defecto (moderno).
3. **El canon es genérico porque su pedido se lo ordena:** `researcher_steps/step_4e_visual_canon.py` l. 222–226, regla 2: «CAPA ÉPOCA-GENÉRICA (clothing, technology, vehicles, interiors)… mantené genérico… Si dudás entre 2 versiones, el más genérico.»
4. **Con el nombre concreto se arregla:** F60 Etapa X (`lab/hyperframes/f60/x/SALIDA_X.md`) 3 de 3 (DC-3, reloj de época, ranura de latón).
5. **Exposición:** 15 de 96 prompts nombran un vehículo (7 avión, 7 camión, 1 coche), 5 un aparato (lámpara, foco, ventilador), 3 algo médico (rayos X, cama, tomógrafo).
6. **Fuera de alcance de la A (solo se prueba en la D):** relleno que el prompt nunca nombró (en F60 B+C, con los prompts A3: aire acondicionado split en `ch04_img_02`, camión y chancletas en `ch04_img_03`, zapatillas en `ch05_img_05`).

## Diseño (y qué reemplaza)
No hace falta casillero nuevo en m03: m03 ya copia `vehicles_machinery`/`technology` del canon («ERA FIELDS ON DEMAND», `m03_visual.py` l. 208). Se cambia **solo la fuente**: la regla 2 del pedido del canon pasa de «mantené genérico» a «modelo concreto de uso común donde ocurre la escena y en ese tramo». Es un **reemplazo** (la regla vieja se va); no se agrega ninguna regla a los prompts de guion, escaleta, ficha ni m03. Sin búsqueda web en el canon (voto del analista: lo que retiene es que el objeto se vea de la época, no que sea el modelo exacto; Opus conoce los modelos comunes de cada época).

## Constantes
| valor | origen | quién |
|---|---|---|
| ninguna constante nueva en producción | — | — |
| `MODELO_CANON` claude-opus-5-5 / `ESFUERZO_CANON` high | existente (`step_4e_visual_canon.py` l. 80–81; DECISIONES 2026-10-28 23:34) | sin cambio |
| US$ 0,035 por foto `/edit` | precio real de fal medido en F60 Etapa X | medido |
| Etapa D: 2 tiradas por variante | analista: Seedream v5 Lite `/edit` no acepta `seed` (SALIDA_X), con 1 tirada no se separa azar de efecto | analista (Omar puede cambiarlo) |

## Módulos tocados
- `researcher_steps/step_4e_visual_canon.py` (pedido del canon visual, una llamada a Opus por tema): hoy pide lo genérico en vehículos y aparatos → después pide el modelo concreto de época. Único módulo de producción.
- Consecuencia declarada: la regla 2 también deja de empujar a lo genérico en `clothing` e `interiors` (y personas); B.2 no lo mide (solo reemplaza vehicles/technology).
- Consecuencia declarada: la marca `canon_ficha_md5` (`marca_canon`, incluye el texto del pedido) cambia → la próxima corrida de cualquier tema rehace su canon. Wittenoom en producción no se toca en esta tanda (Omar decide cuándo producir).
- Lab nuevo: `lab/hyperframes/f62/` (runners y salidas).

## Reglas fijas
- Rama `f11-guion-v4`; `main` no se toca.
- No se tocan: `m03_visual.py`, `m03_imagenes_v3.py`, `foto_madre.py`, `anachronism_blocklist`, `forbidden_anachronisms`, `documented_props` (BLOQUE 4), las demás reglas del pedido del canon.
- Producción intacta en B, C y D: mtimes iguales de `data/topics_db.json`, `data/scripts/<tid>.json`, `data/scripts/_steps/<tid>`, `output/<tid>` (los paths de `etapa_f61b_fotos.PROD`; pegarlos). `data/cost_history.json` cambia por cost_tracker (esperado).
- Sin tope de dólares; el gasto se informa al final.

## Etapa 0 — registro e impacto (US$ 0)
0.1 Anotar en `DECISIONES.md` (CRLF, tal cual):
- `2026-10-30 23:16 · F61 se cierra: posadas (4/96 prompts con pose) y planos medios que el motor abre a wide en exteriores → lista «se arregla si se repite» · Omar`
- `2026-10-30 23:18 · lo siguiente: tanda de anacronismos · Omar`
- `2026-10-30 23:23 · F62: los vehículos, máquinas y aparatos de época se arreglan en la fuente: la regla 2 del pedido del canon (step_4e) deja de pedir lo genérico y pide el modelo concreto de uso común donde ocurre la escena y en ese tramo; sin casillero nuevo en m03; el relleno que el prompt no nombra (aire acondicionado, calzado) solo se prueba en lab · Omar · F62`
0.2 Confirmar con grep y pegar: lectores de `vehicles_machinery` y `technology` del canon (esperado: `m03_visual._lineas_epoca`, único que los imprime en el pedido de m03, y `m06_classifier._load_topic_facts`, que pasa la era entera sin filtrar; `m03_imagenes_v3`, `m05_judge` y `foto_madre` NO leen esos dos campos; `test_module_05.py` l. 1287–1288 y `test_module_f50d.py` los usan solo como fixture). Si alguno **filtra o compara** esos textos (no solo los muestra), PARÁ antes de la A.
0.3 Confirmar que ningún test fija el texto de la regla 2 (grep «Rolex», «más genérico», «ampliamente documentado» en `test_*.py`). Esperado: ninguno.

## Etapa A — código
A.1 `researcher_steps/step_4e_visual_canon.py` l. 222–226, reemplazar el bloque entero (byte a byte). Antes:
```
2. CAPA ÉPOCA-GENÉRICA (clothing, technology, vehicles, interiors) y CUALQUIER
   persona: mantené genérico y ampliamente documentado. NO inventes un detalle
   específico no verificable (ej: "the captain wore a Rolex"). Si dudás entre 2
   versiones, el más genérico. El detalle de un individuo nombrable vive en
   documented_people, NO acá.
```
Después:
```
2. CAPA ÉPOCA-GENÉRICA (clothing, technology, vehicles, interiors) y CUALQUIER
   persona: lo ampliamente documentado de la época. NO inventes un detalle de un
   individuo no verificable (ej: "the captain wore a Rolex"); el detalle de un
   individuo nombrable vive en documented_people, NO acá. En technology y
   vehicles_machinery (también los de cada period), cada vehículo, máquina o
   aparato va con el modelo o tipo concreto de uso común donde ocurre la escena
   (si el tramo tiene escenas en más de un país, uno por país) y en ESE tramo,
   con el rasgo visible que lo fecha (ej: "black Bakelite rotary-dial telephone",
   NO "a telephone"; "Bedford OB coach with a rounded bonnet", NO "a bus"): el
   tipo genérico solo, el motor de imágenes lo pinta moderno. Sin logotipos ni
   texto pintado.
```
A.1b Tres reemplazos chicos en el mismo pedido, para que no quede una orden opuesta (byte a byte; CC pega antes/después de cada uno):
- l. 166: «La capa ÉPOCA es genérica de la década;» → «La capa ÉPOCA es de la década;» (resto de la línea igual).
- l. 169: «Sub-campos de ÉPOCA (genéricos de la década, derivados de los facts/contexto):» → «Sub-campos de ÉPOCA (de la década, derivados de los facts/contexto; vehículos y aparatos con modelo concreto, ver regla 2):».
- l. 177: `  Ej: "analog gauges, vacuum tubes, rotary dials. NO LEDs, NO digital displays."` → `  Ej: "black Bakelite rotary-dial telephones, valve radios, analog gauges. NO LEDs, NO digital displays."`
Si el texto exacto de alguna de esas líneas no coincide, PARÁ y pegalo.
A.2 Test nuevo `test_module_f62.py`: `pedido_canon` (con un topic y ficha mínimos de fixture) contiene «modelo o tipo concreto de uso común» y «Sin logotipos ni texto pintado»; no contiene «mantené genérico» ni «el más genérico».
A.3 Suites como siempre (ch02 md5, rápida, amplia + las 4 previas). Salida en texto: el diff de A.1.

## Etapa B — medición en texto (canon + m03, cero fotos)
B.1 Canon nuevo en lab: runner `f62/etapa_f62_canon.py` con el patrón de `lab/hyperframes/f60/etapa_a3_canon.py` (`fc.load(TID, f60/base/data/scripts/_steps)` + `fase1_5._load_topic_by_id`, `canon_desde_ficha` con el pedido F62, **sin** `asegurar_canon`, que escribe topics_db). Chequear `m03_visual._tramo` sobre cada `periods[].years` como hace `asegurar_canon`; ilegible → PARÁ. Guardar en `f62/05_visual_canon_f62.json`.
B.2 **Una sola variable:** armar `f62/05_visual_canon_b2.json` = copia profunda del A3 (`f60/a3/05_visual_canon_a3.json`) con **solo** `era_visual_canon.vehicles_machinery`/`technology` y los de cada `period` reemplazados por los F62 con los mismos `years`. Si los `years` no coinciden uno a uno: PARÁ, pegá ambas listas y el analista decide (opción prevista: emparejar con el period F62 que contiene el punto medio del tramo A3).
B.3 Runner `f62/etapa_f62_m03.py` = copia de `lab/hyperframes/f61/etapa_f61_m03.py` (mismas entradas, mismas anclas fijas, 7 caps en paralelo, mismo paso por `assign_visual_prompts`) que lee `f62/05_visual_canon_b2.json` en lugar de `05_visual_canon_a3.json`, `cost_tracker.start_video("lab_f62b")` en lugar del TID, y salidas en `f62/`.
B.4 Salida en texto:
- tabla por period: `vehicles_machinery` y `technology` A3 → F62;
- un subagente lee los 96 prompts de antes (`f61/03_visual_f61.json`) y los de después y lista cada ítem cuyo prompt nombra un vehículo, máquina o aparato (lectura, no lista de palabras): id · año · frase antes → frase después · ¿concreto de época? sí/no;
- conteo: ítems con objeto · cuántos pasan de genérico a concreto · cuántos siguen genéricos (con la frase);
- cualquier otro cambio en los prompts que no venga del canon (debería ser ruido de corrida: decirlo).
B.5 Costo real.

## PARADA B
Nada de fotos. El analista lee la tabla con Omar. C y D corren solo con «sigue» de Omar.

## Etapa C — fotos de los objetos (solo con «sigue»)
C.1 Runner `f62/etapa_f62c_fotos.py` = patrón de `lab/hyperframes/f61/etapa_f61b_fotos.py`: todos los ítems que B.4 marcó con vehículo o aparato, prompt del después tal cual, madres por `_madres_para_item` con `personas_canon` y registry como en `etapa_f61b_fotos.py` (documented_people del canon B.2 = A3; registry `{nombre: madre}` vía `foto_madre._slug` sobre `lab/hyperframes/f60/bc/output/<tid>/foto_madre/*.png`, 8 madres; persona sin madre → sin madre, listada), una foto por llamada, todas a la vez, `cost_tracker.start_video("lab_f62c")`.
C.2 Hoja + mirada de un subagente ciego (solo ve la hoja y el año de cada foto): por foto, ¿hay algún objeto de otra época? cuál. Tabla contra F60 B+C para los ítems que estén en las dos.

## Etapa D — relleno no nombrado (solo con «sigue»; variable aparte)
D.1 Ítems `ch04_img_02` = `chapters[3].image_prompts[1]` y `ch04_img_03` = `chapters[3].image_prompts[2]` (1-based), con el prompt de **`f60/a3/03_visual_a3.json`** tal cual (el que dio el aire acondicionado y el camión en B+C; en F61 `ch04_img_03` es otro prompt, sin camión ni persona). Los dos son de 1963, con Víctor (y Mercedes en el 03): madres como C.1. Variante «sin» = prompt tal cual; variante «con» = prompt + esta oración inmediatamente antes de «The image has a 16:9 aspect ratio.» (aparece una vez en cada uno), con `{anio}` = el año del ítem como texto literal (sin `.format()`): `Everything visible — buildings and their fittings, vehicles, clothing and footwear — is as it was in {anio}; nothing made after {anio}.` 2 tiradas por variante (8 fotos), madres como C.1, `cost_tracker.start_video("lab_f62d")`.
D.2 Mismo subagente ciego (no sabe cuál es cuál): objetos de otra época por foto. Tabla sin/con.

## PARADA D
F62_REPORT con veredicto íntegro del revisor + adenda, ESTADO, costo. Nada en producción fuera de A.
