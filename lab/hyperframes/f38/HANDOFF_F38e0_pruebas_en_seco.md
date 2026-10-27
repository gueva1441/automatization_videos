# HANDOFF F38e-0 — dos pruebas en seco: rótulos parafraseados y títulos de cap (analista, 2026-10-27)

**Qué es:** dos llamadas sueltas a modelos, en `lab/`, para comparar «hoy | nuevo» ANTES de programar nada. **No se toca el pipeline** (`script_engine/`, `tests/`, `gfx_profiles/`, `gemini_helpers.py`, `claude_helpers.py`): solo se importan. Sin render, sin fase3, sin merge. Al final, **PARADA**.

## 0. Orden re-derivado (skill handoff-analista §0)
- ¿Construye sobre código que se va a reemplazar? No: solo lee m01e (el autor del papel) y m01d (partición/títulos) y llama a los mismos modelos.
- ¿Alguna decisión de hoy cambia el orden? No: DECISIONES 11:44 manda estas pruebas antes de F38e (la tanda de bugs B1–B5, r1, R8).

## Constantes (ninguna nueva)
| valor | dónde se usa | origen |
|---|---|---|
| `claude-sonnet-5-5`, effort `medium` | prueba 1 | `m01e_pantalla.MODELO/EFFORT` (existente) |
| `caben` por oración (seg × 15 cps) | prueba 1 | ya viene en la entrada de `f38/b4/01e_pantalla.raw.json` (F36/F38d) |
| tope US$ 1,00 por prueba | prueba 1 | `m01e_pantalla.TOPE_USD_RESPALDO` (Omar, F37); una sola llamada, sin vueltas |
| «3 segundos» en los dos prompts | texto del prompt | `title_dur` 3 s (identidad F3); lectura de una ficha ≈ ese orden |
| `TITLE_MAX_WORDS` = 5 | prueba 2 | `m01d_particion.py:32` (existente) |
| Gemini Flash (`call_flash_json`) | prueba 2 | el mismo que `titles()` hoy |
El margen de redondeo **no** es constante: la prueba lo mide (DECISIONES 11:44).

## Módulos tocados
Ninguno del pipeline. Archivos nuevos:
- `lab/hyperframes/f38/prueba1/prueba1_rotulos.py` — una llamada a Sonnet con el prompt de prueba 1, verificación de `respaldo`, tabla.
- `lab/hyperframes/f38/prueba2/prueba2_titulos.py` — una llamada a Flash con el pedido de prueba 2, tabla.
- sus salidas (`*.raw.json`, `TABLA.md`, `.log`) en cada carpeta.

## Paralelo (DECISIONES 01:23)
Partes A y B son independientes: **un subagente cada una, a la vez**. El `revisor-handoff` al final, sobre las dos.

## Paso 0 (antes de A y B)
Commit «docs(f38e-0): …» con, tal cual (sin editar), y md5 en el mensaje:
- `DECISIONES.md` (md5 `184831d263cdf4777e73dc071a60c245`: líneas 11:21 y 11:44);
- `lab/hyperframes/f38/F38_REPORT.md` (quedó modificado sin commitear del render v6);
- `lab/hyperframes/f38/PRUEBA1_prompt_rotulos.md` (md5 `240e3e7bf13656cb62f68b598393f41f`);
- `lab/hyperframes/f38/PRUEBA2_prompt_titulos.md` (md5 `e644cb0e7adfdd607ecba33a07f67205`);
- este handoff.
Si un md5 no coincide: PARADA y avisar. Los M ajenos (`diag_234_cap4.py`, `gfx_profiles/*`, `f28a.log`) no entran.

## A — Prueba 1: rótulos parafraseados (Sonnet, ~US$ 0,3)
1. Entrada: `lab/hyperframes/f38/b4/01e_pantalla.raw.json` → `entrada` (la misma de v6, sin regenerar nada).
2. SYSTEM = el bloque «Prompt nuevo (m01e-6-prueba), entero» de `PRUEBA1_prompt_rotulos.md`, **copiado letra por letra** (leerlo del md, no reescribirlo). USER = `json.dumps(m01e._para_modelo(entrada))` + `"\n\nFormato de salida: "` + `m01e.FORMATO_SALIDA` con `"respaldo": "…", ` insertado después de `"texto": "Más de 1 metro", ` (una sola sustitución de cadena; imprimir el formato resultante en el log).
3. Una llamada con el mismo body que `m01e.llamar` → `autor()` (model, max_tokens, system, messages, `output_config.effort`) por `claude_helpers._post`. Sin vueltas, sin caché, sin escribir en `data/` ni en `output/`. Guardar `prueba1.raw.json` (respuesta cruda, usage, US$, md5 del SYSTEM).
4. Validación con el código de hoy: `m01e.validar(resp, entrada, {}, final=False)` (no corta coincidencias: las pregunta). Anotar por ficha: queda / corta (regla y motivo) / pregunta (regla y token).
   - Ojo, dato para el analista, no arreglo: `no_dicho` puede marcar una cifra que la voz dice cerca; con la (a) nueva («aclara») eso puede ser legítimo. Solo se reporta.
5. Verificación nueva (solo en el script de lab, ~20 líneas): por ficha,
   - `respaldo` es subcadena de `archivo[pool_id].texto` (con `ev.norm` como el candado; en citas, el dato mismo);
   - cada número de etiqueta+dato (`pantalla_filtros.numeros`) está en el respaldo (`numero_en`) → **literal**; si no, el número del respaldo más cercano por valor y la diferencia en % → **redondeo (±x %)** si va con «más de» y es menor, o con «casi» y es mayor; si no, **no está**;
   - cada nombre propio (`pantalla_filtros.nombres`) en el respaldo (`_palabra_en`) ✓/✗.
6. Tabla `prueba1/TABLA.md`, una fila por beat con ficha en cualquiera de las tres columnas:
   `cap·beat | v6 hoy (etiqueta · dato · autor) | intento 1 de m01e-5 (de raw.intentos[0], mismo formato) | NUEVO (etiqueta · dato · autor) | respaldo ✓/✗ | cifras | nombres | validar | car./caben | ¿se entiende solo? (vacía)`.
   La columna «intento 1» es el control justo (una sola llamada, como la nueva). La última columna la llenan el analista y Omar.
   Debajo: conteos de sellos y relojes de la respuesta nueva contra v6 (no se evalúan; solo que no se hayan roto), US$ y tokens.
7. Salida en texto al final de A: la tabla pegada en el reporte.

## B — Prueba 2: títulos de cap (Flash, centavos)
1. Entrada: `data/scripts/_steps/f8s3-vajont/01a_escaleta.json`.
2. `lines` por cap, exactamente con la forma del md: una línea `CAP n:`; por beat del cap `  beat <n> <funcion>[ · pico]: se ve: <imagen_sensorial> · pregunta que abre: <pregunta_abierta>`; al final `  termina (no lo cuentes): <cierre del último beat del cap>`. `pico` = el campo `pico` del beat.
3. Pedido = el bloque «Pedido nuevo, entero» de `PRUEBA2_prompt_titulos.md`, copiado letra por letra, con `{TITLE_MAX_WORDS}` = `m01d_particion.TITLE_MAX_WORDS` y `{lines}`. `call_flash_json(pedido, response_schema=m01d_particion.TITLES_SCHEMA, description="prueba2: títulos")`. **Tres llamadas** (mismo pedido) para ver cuánto varía Flash; guardar las tres en `prueba2.raw.json` con el pedido entero.
4. Validación de hoy por título (la de `titles()`: ≤ 5 palabras, sin dígito, sin «?») ✓/✗.
5. Tabla `prueba2/TABLA.md`: `cap | hoy (de 01a_skeleton.json) | nuevo 1 | nuevo 2 | nuevo 3 | validación | ¿promete sin contar el final? (vacía)`. Debajo, el pedido entero tal como se mandó (para que el analista vea la entrada real).
6. Salida en texto al final de B: la tabla pegada en el reporte.

## Reporte
`lab/hyperframes/f38/F38e0_REPORT.md`: tablas A y B, US$ total, md5 del paso 0, «lo que queda abierto» entero, veredicto íntegro de `revisor-handoff`. `lab/ESTADO_SESION.md`: una entrada corta. Un commit «lab(f38e-0): pruebas en seco…» con scripts, raws, tablas, reporte y ESTADO.

## Frenos
- Cualquier escritura fuera de `lab/hyperframes/f38/prueba1|prueba2/`, del reporte, de ESTADO y de los archivos del paso 0 → PARADA.
- Gasto > US$ 1,00 en total → PARADA.
- Respuesta sin JSON en A → un reintento de la misma llamada; si vuelve sin JSON, PARADA con el crudo guardado.

## PARADA
Al terminar A + B + revisor + commit. No se decide nada: comparan Omar y el analista.
