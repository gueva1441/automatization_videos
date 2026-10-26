# HANDOFF F34 — Reglas de pantalla corregidas: textos cortos, gancho con contenido, reloj, agua, sellos de clima y plan congelado

Analista · 2026-10-26 · Para CC (vía `/tanda`). Base: `fc889c9` (F33 E). Dos partes A→B; **PARADA al final de B, sin render**. API: Claude ≤ US$ 1 (rotulista, 7 llamadas) · Gemini ≤ US$ 0.5. Banco: `f8s3-vajont-f30`.

**En cristiano:** el guion de pantalla de Vajont (F32) dejó 2 textos en 17 min, sellos que repiten la voz, el gancho vacío, el reloj tapado por sellos y cero animaciones de agua. Las causas son reglas del analista que se cancelan con el material. Esta tanda corrige esas reglas (todas simuladas antes contra el guion real; tabla en §1) y regenera el guion. Después el analista lo revisa y Omar dice «aprobado» o no.

## 0. Módulos que toca (stickers de `lab/MAPA_MODULOS.md`)
| módulo | qué hace hoy | qué hará |
|---|---|---|
| `gfx_rotulista` | escribe los textos de pantalla por beat | 3 cambios exactos de prompt (§A.1) + gancho con todo el pool + candado/spoiler/números corregidos |
| `gfx_realizador` / escena final de `gfx_rotulista` | reparte: una cosa por escena | reloj gana al sello; en caps de una sola escena, una cosa por oración |
| `gfx_director` → sellos (`sellos_por_tema`) | elige sello = palabra que dice la voz | elige palabra de **clima** de un vocabulario aprobado (§A.4) |
| `gfx_project` / `gfx_guion` | dibuja y escribe el guion | tarjeta fecha-hora sobre negro al inicio; nivel de agua desde la voz |
| `fase2b` + `music_intensity` | arma el video; mapa de música | música alineada con cada cap; render usa el plan congelado |
| `.claude/` | — | chascadas de modelo y de `/tanda` (§A.8) |

## 0b. Constantes y origen
| constante | valor | origen |
|---|---|---|
| textos por beat | 1; 2 si son dos `a_pantalla` en oraciones/escenas distintas; pico: solo `a_pantalla` | DECISIONES 14:22 |
| gancho | 0–1 texto (candidatos = todo el pool no dicho en el video), 1 reloj, 1 sello; **nunca vacío de todo** | DECISIONES 14:28 |
| prioridad | información > clima: reloj, agua y textos ganan al sello | DECISIONES 14:22 |
| vocabulario de sellos (perfil misterio) | PÁNICO, CALMA, AMENAZA, AVISO, ALARMA, INMINENTE, COLAPSO, SILENCIO, RABIA, MEMORIA | DECISIONES 14:22 (Omar). Vive en `gfx_profiles/misterio.json` → `sellos_clima`; si falta la clave, sin sellos |
| tarjeta fecha-hora inicial | dura `title_dur` (identidad F3); estilo = title card | DECISIONES 14:36 |
| lectura | 15 cps | estándar (ya en F29c) |
Ningún otro número nuevo.

## 1. Lo que la simulación del analista espera (sobre `GUION_PANTALLA.json` de F32)
| cap | textos | animaciones |
|---|---|---|
| ch01 | 1: `LA PRESA DEL VAJONT · 266 m de alto` (D118, el valor del pool) (ancla «la presa que todos creyeron caída sigue en pie», 0:10) | tarjeta «9 OCT 1963 · 22:39» en 0:00; sello PÁNICO (Coletti); reloj 9 OCT 1963 en «Longarone, Italia, nueve de octubre…» |
| ch02 | 1: D117 `ACTA DEL CONSEJO SUPERIOR · 13 de 34 representantes presentes` | sellos CALMA, AMENAZA |
| ch03 | 1: D49 `ANCHO DE LA FISURA · Más de 1 metro` | agua `OLA · 20 m` (Pontesei); sello AVISO |
| ch04 | 1: T39 `ALERTA DE MERLIN, 1961 · 50 millones de m³ de roca` (puede arrancar en la escena siguiente) | reloj 4 NOV 1960; agua `COTA AUTORIZADA · 715 m` |
| ch05 | 1: Q50 recorte `Carta del municipio de Erto y Casso a SADE · Las poblaciones viven en continua aprensión y alarma` | reloj 9 OCT 1963; sello INMINENTE |
| ch06 | 2: D128 `MUERTOS, RECUENTO OFICIAL · 1.910 personas` y D192 `CENTRO DE CONTROL, ESTRIBO IZQ. · 20 técnicos muertos` | sellos COLAPSO, SILENCIO |
| ch07 | 2: T85 `REMISIÓN A JUICIO, 1968 · 11 imputados` y D245 `TRIBUNAL DE BELLUNO, 1997 · 55.645.758.500 liras a Longarone` | reloj 20 FEB 1968; sello MEMORIA |
Total esperado: **9 textos · 4 relojes + tarjeta inicial · 2 aguas · 8 sellos · 6 punches**. B mide contra esto línea por línea. Las palabras exactas las escribe el modelo; lo que se compara es el dato, el ancla y que quepa.

## A. Reglas (un commit; la salida en texto de cada punto va en el reporte)
### A.1 Prompt del rotulista — tres reemplazos exactos (el resto del prompt no cambia; md5 nuevo en el reporte)
1. Reemplazar
`En cada beat puede ir como máximo UN texto; en el beat marcado como pico no va ninguno; en el gancho, a lo sumo uno.`
por
`En cada beat puede ir como máximo UN texto (dos si son dos datos marcados a_pantalla y van en oraciones distintas); en el beat marcado como pico solo van los datos a_pantalla; en el gancho va a lo sumo uno, y para el gancho podés usar cualquier dato de la lista que la narración no diga en todo el video, aunque no sea de su beat: el gancho tiene que prometer algo.`
2. Reemplazar
`Escritura: una línea de etiqueta y una o dos líneas de dato; oración completa o etiqueta + valor; nunca un fragmento sin sujeto o sin el valor.`
por
`Escritura: la etiqueta es una línea corta que dice qué es («ANCHO DE LA FISURA», «ACTA DEL CONSEJO SUPERIOR»); el dato es UNA línea corta con el valor o el hecho en pocas palabras («Más de 1 metro», «13 de 34 representantes presentes»). Nunca una oración larga: se tiene que leer en dos segundos. Nunca un fragmento sin sujeto o sin el valor. No pongas el nombre de la fuente ni el año de publicación en el dato.`
3. En `Para cada bloque devolvé: … pool_id y una línea aporta …` agregar después de `pool_id`: `, y si es cifra también unidad y valor`; y en el formato de salida del USER agregar a cada bloque `"unidad": str|null, "valor": number|null` (hoy el SYSTEM los pide y el formato no los nombra: por eso no salían).
**Para el gancho**, la entrada del rotulista trae todos los ítems del pool del video (no solo los del beat), marcando cuáles la voz dice en algún cap (esos se descartan en código igual).

### A.2 Filtros: tres falsos positivos medidos en F32
1. **Candado:** un número, año o nombre que la voz dice en la oración ancla (en dígitos o en letras) cuenta como presente aunque no esté en el texto fuente (D117 cayó por «1943»).
2. **No dicho:** antes de comparar, los números en letras de la voz se convierten a dígitos con el conversor existente (`num_es`) (D237 pasó como «nuevo» con «cuatrocientos»).
3. **Spoiler:** un nombre propio que la voz ya dijo antes en el cap o en un cap anterior no es spoiler (T85 cayó por «Vajont»).
Test por cada uno con el caso real.

### A.3 Reparto: prioridad y unidad
1. Reloj, agua y textos ganan al sello: si compiten en un beat o escena, el sello se mueve a otra oración del beat o no va (hoy el sello cortó «9 OCT» y «20 FEB»).
2. En un cap de **una sola escena** (ch01 de Vajont, Veo), «una cosa por escena» se aplica **por oración**: dos bloques nunca en la misma oración ni solapados en el tiempo.
3. El reloj se propone cuando la voz dice una fecha completa (día + mes + año, en letras o dígitos) en una oración, aunque el director no lo haya pedido; texto = la fecha en el formato del reloj existente.

### A.4 Sellos de clima
`sellos_por_tema` deja de usar la palabra de la oración. Para cada candidato a sello (los mismos momentos que hoy), una llamada a Gemini Flash (en lote por cap) con este prompt, literal:
```
Elegí UNA palabra de esta lista que nombre el clima de este momento del relato, no lo que se dice: {lista}.
No puede ser una palabra que aparezca en estas oraciones: «{voz_-1}» «{voz_ancla}» «{voz_+1}».
Momento: función del beat «{funcion}»; oración: «{voz_ancla}».
Respondé solo la palabra en mayúsculas, o NINGUNA si ninguna calza.
```
`{lista}` = `sellos_clima` del perfil. Código: si la palabra no está en la lista o aparece en las tres oraciones, el sello no va. Una palabra no se repite en el mismo cap. El crítico sigue mirando forma (que no tape), no contenido.

### A.5 Nivel de agua desde la voz (animación, no texto)
Cuando una oración dice una altura o nivel con número (`<n> metros`, o `cota`/`nivel`/`ola` con número en esa oración o la anterior), se propone un `water_level` con etiqueta corta derivada de la oración (`OLA`, `COTA AUTORIZADA`, `NIVEL DEL EMBALSE`) y el valor. Cuenta como la animación del beat. Es la única animación que puede repetir la cifra de la voz (es la imagen de esa frase, no un dato nuevo). Coherencia con el resto del video como hoy.

### A.6 Tarjeta fecha-hora inicial
Antes de la primera imagen del video (sobre negro, `title_dur`), una tarjeta con fecha y hora del suceso central. Se deriva de la escaleta/pool (beat `pico` + el ítem que da la hora; para Vajont: 9 OCT 1963 · 22:39). Si no se puede derivar con certeza, el guion la marca `⚠ falta fecha-hora` y se agrega con `--plan-edit`; nunca se inventa.

### A.7 Plan congelado y música alineada
1. **Plan congelado («lock»):** con `--gfx` y guion aprobado, el render dibuja exactamente los planes aprobados: el crítico no vuelve a decidir (reusa el veredicto guardado de cada bloque) y ningún paso del render cambia bloques, tiempos ni transiciones. Test: md5 de los planes antes y después de un `--only-cap` con `--gfx` idénticos.
2. **Música alineada:** la pieza de música de cada cap arranca con su title card (incluida la intro de 2.5 s y los cruces entre caps); el mapa de intensidad se corre igual. Medida en `mezcla_preview.wav`: inicio de la música de cada cap contra su title card, ±1 cuadro (hoy ch02 4.6 s antes, ch07 14.8 s antes).

### A.8 Chascadas
1. Commitear `DECISIONES.md` como está en disco (tiene líneas nuevas de Omar del 26).
2. `.claude/settings.json`: modelo por defecto del repo = `claude-opus-5-5`. Subagentes `revisor-handoff` y `simulador`: `model: sonnet` en su frontmatter.
3. `/tanda`: antes de la PARADA, cerrar toda tarea en segundo plano propia.
4. Actualizar `lab/MAPA_MODULOS.*` con lo que cambió.

## B. Guion nuevo de Vajont (un commit)
1. `fase2b f8s3-vajont-f30 --plan-only --rotulista` → `GUION_PANTALLA.md/.json` + `mezcla_preview.wav`. Copia en `lab/hyperframes/f34/`.
2. **Comparación con §1**, línea por línea, con el agente `simulador`: por cap, lo esperado / lo que salió / si no coincide, por qué (qué regla, qué dijo el modelo). Totales contra los esperados.
3. Chequeos del guion (los de F32) + inicio de música por cap.
**No renderizar.** No correr `--aprobar-guion`.

## Frenos
Prompts de guion/escaleta/ficha intactos; el del rotulista cambia solo por los tres reemplazos de A.1. Ningún número fuera de §0b. Sin merge, sin publicar, sin borrar. `.env`, `config.py`, `lab/_gpt_probe_analista/`, `gfx_profiles/*` fuera de git (excepto la clave `sellos_clima`, que se anota en el reporte para que Omar la commitee si quiere). Suite rápida y amplia verdes; md5 ch02 sin `--gfx` `38e5ba14…`. Reporte `lab/hyperframes/f34/F34_REPORT.md` con «lo que queda abierto» y el veredicto íntegro del revisor; `ESTADO_SESION.md`; **PARADA**.
